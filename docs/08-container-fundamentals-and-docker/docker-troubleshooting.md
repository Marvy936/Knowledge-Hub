# Docker troubleshooting

Docker troubleshooting nie je postupné skúšanie príkazov, kým symptom zmizne. Je to riadené dokazovanie nad presným artifactom, runtime generation, Docker contextom, data identity a request flowom. Restart, recreate alebo prune môžu zmeniť state a odstrániť evidence; bez subject identity potom nevieš, čo sa opravilo ani či sa incident vráti.

Dominantný diagnostický lifecycle je:

```text
user alebo business symptom
→ impact, scope a časová os
→ exact release/runtime/data/flow subject
→ preservation volatile evidence
→ competing causal hypotheses
→ discriminating observation points a bezpečné testy
→ containment
→ recovery cez authoritative source/artifact/state
→ overenie pôvodného outcome-u aj forbidden outcomes
→ skorší control a incident closure
```

Tento model spája daemon, container process, image, Compose model, mounts, network, cgroups, registry aj BuildKit. Jednotlivé commands sú observation tools, nie diagnostická metóda.

## 1. Atlas incident

Atlas Payments nasadil release `3.10.0`. Päť minút po rollout-e:

- časť payment requests vracala `502`;
- niektoré retries vytvorili vysokú latency;
- `docker compose ps` ukazoval všetky services ako `Up` a `healthy`;
- restart API dočasne znížil chyby;
- problém sa objavoval iba na jednom z dvoch Docker hosts;
- host mal dostatok voľnej RAM aj diskovej kapacity podľa základného dashboardu.

Slabý postup by bol:

```text
restart containers
→ docker system prune
→ zvýšiť memory limit
→ použiť host network
```

Taký postup mení viac boundaries naraz a ničí evidence. Správny postup najprv stabilizuje identity a hypotézy.

## 2. Definuj pôvodný outcome

Pred technickou diagnózou musí byť jasné, čo malo fungovať.

Pre Atlas incident:

```text
external client
→ production host port/TLS proxy
→ payments API generation G310
→ production configuration epoch CE-310
→ database data ID PAYMENTS-PROD
→ one payment authorization exactly once
→ response do 800 ms
```

Forbidden outcomes:

- traffic na staging dependency;
- duplicate authorization;
- write zo starej container generation;
- použitie iného image digestu;
- broad admin-port exposure;
- strata payment ledgeru pri recreate.

Troubleshooting sa nekončí tým, že container beží. Končí potvrdením tohto end-to-end outcome-u.

## 3. Zafixuj incident subject

Minimálny incident subject zahŕňa:

```text
časové okno a request/correlation IDs
Docker context, Engine host a project identity
Compose source set a resolved-model digest
service a container IDs, create times a config hashes
image index/platform manifest digest
entrypoint, command, UID a healthcheck generation
process-loaded configuration a secret epochs
mount source, data ID, schema a writer epoch
network/endpoint/DNS/publication generation
cgroup identity, limits, counters a pressure events
registry/build provenance a poslednú deployment zmenu
external dependency identities a business audit
```

Bez týchto údajov môžu dva tímy hovoriť o „rovnakom containeri“, hoci sledujú rozdielne hosts, projects, image digests alebo generations.

## 4. Najprv scope a timeline

Scope pomáha zredukovať hypotézy:

| Scope | Pravdepodobnejšie boundaries |
|---|---|
| jedna request class | application path, data, dependency alebo config |
| jedna container generation | runtime config, mount, process alebo local pressure |
| jeden host | daemon, kernel, storage, network, node policy |
| jeden image digest na všetkých hosts | artifact, image config, dependency closure |
| iba jedna platform | platform manifest, binary, loader, node capability |
| iba po recreate | data attachment, config snapshot, endpoint generation |
| iba pri load-e | cgroup, conntrack, ports, backlog, downstream saturation |
| local funguje, remote nie | publication, firewall, route, TLS/client path |

Timeline musí spájať:

- deploy a recreate events;
- health transitions;
- first failed request;
- OOM/throttle/network/storage events;
- configuration alebo secret rotation;
- registry pull/tag changes;
- operator actions.

```bash
docker events --since 1h
docker inspect <container>
docker logs --timestamps --since 1h <container>
journalctl -u docker.service --since "1 hour ago"
journalctl -k --since "1 hour ago"
```

Events majú krátku retention a nemusia tvoriť úplný audit. Pri kritických workloads ich streamuj centrálne.

## 5. Preserve evidence pred mutation

Pred restartom, delete, recreate alebo prune zachovaj podľa incidentu:

```bash
docker context show
docker version
docker info
docker ps -a --no-trunc
docker inspect <container>
docker logs --timestamps --tail=1000 <container>
docker events --since 1h
docker stats --no-stream
docker system df -v
docker compose config
docker compose ps -a
docker compose images
```

Host evidence môže zahŕňať:

```bash
df -h
df -i
cat /proc/pressure/cpu
cat /proc/pressure/memory
cat /proc/pressure/io
ss -s
ip route
ip link
```

A podľa oprávnení:

- daemon a containerd logs;
- cgroup counters a events;
- OOM records;
- firewall/NAT counters;
- conntrack state;
- packet captures;
- volume/backend metadata;
- registry manifest read-back;
- application metrics, traces a downstream audit.

Evidence môže obsahovať secrets, tokens, environment values alebo osobné dáta. Rediguj ju, obmedz access a nastav retention. Incident artifact nesmie vytvoriť ďalší security incident.

## 6. Nepredpokladaj správny Docker context

Docker CLI môže byť lokálny, ale aktívny context môže smerovať na remote Engine.

```bash
docker context ls
docker context show
docker info --format '{{.Name}}'
printf '%s\n' "$DOCKER_HOST"
```

Context identity musí zahŕňať:

- context name;
- endpoint/host identity;
- expected environment;
- TLS/SSH trust subject;
- Engine version;
- Compose project.

### Failure boundary

Operator inspectoval local host, zatiaľ čo deployment bežal na remote Engine. Local disk, networks a volumes boli zdravé, no incident existoval na inom node-e. Diagnostické commands boli správne, observation subject bol nesprávny.

## 7. Oddeľ management plane od workload plane

Docker Engine API môže zlyhávať, hoci existujúce container processes stále bežia. Opačne môže daemon odpovedať, hoci application je nefunkčná.

Rozlišuj:

```text
Docker client/API connectivity
daemon object state
containerd task a shim state
OCI runtime process state
application health/readiness
external business outcome
```

`Cannot connect to the Docker daemon` môže znamenať:

- daemon down;
- wrong context alebo `DOCKER_HOST`;
- socket permissions;
- remote SSH/TLS failure;
- Docker Desktop backend down;
- daemon startup/configuration failure.

World-writable Docker socket nie je bezpečná oprava. Docker API access je prakticky host-admin authority.

## 8. Container object nie je application outcome

```bash
docker inspect --format '{{json .State}}' <container>
docker top <container>
docker events --filter container=<container>
```

Oddeľ:

- object existuje;
- task/process beží;
- PID 1 je správny;
- process načítal správnu konfiguráciu;
- healthcheck je validný;
- inštancia je ready;
- request path a business operation fungujú.

`running + healthy` môže stále používať nesprávnu DB, stale secret epoch alebo shallow healthcheck.

`Exited (0)` môže byť správny one-shot job alebo service, ktorej command sa okamžite úspešne skončil. Exit code bez command purpose nestačí.

## 9. Exit, signal a restart evidence

Bežné signals/exit patterns:

- `0` — úspešný process outcome podľa application contractu;
- `126` — command sa nedá vykonať;
- `127` — command/interpreter sa nenašiel;
- `137` — process dostal `SIGKILL`, ale príčina môže byť cgroup OOM, host OOM, forced stop alebo operator;
- `143` — typicky `SIGTERM`;
- application-specific non-zero — potrebuje application context.

Pri restart loop-e koreluj:

```bash
docker inspect <container>
docker logs --timestamps <container>
docker events --filter container=<container>
journalctl -k --since "30 min ago"
```

Hypotézy môžu zahŕňať:

- missing config/secret;
- invalid command alebo loader;
- migration race;
- permission/LSM denial;
- OOM alebo PID limit;
- dependency failure;
- health remediation loop;
- signal/PID 1 defect.

Dočasné zastavenie restart policy môže zachovať failure evidence, ale je to containment mutation a musí byť zaznamenaná.

## 10. Actual runtime configuration vs. desired model

`docker inspect` poskytuje create-time container configuration. `docker compose config` poskytuje resolved desired model. Application môže mať ešte tretí state: process-loaded configuration.

Porovnaj:

```text
versionovaný Compose/Dockerfile source
→ resolved Compose model
→ Engine container create config
→ mounts a environment delivered procesu
→ process-loaded effective state
```

Observation points:

```bash
docker compose config
docker inspect <container>
docker compose images
docker compose ps -a
```

Pri environment a secrets nevypisuj celý obsah do incident logu. Použi redacted manifest, config checksum, logical endpoint a epoch markers.

### Failure boundary

`.env` bol aktualizovaný, ale container nebol recreated. Desired source ukazoval novú value, Engine object a process stále používali starú. Restart processu v rovnakom containeri by starý create-time environment nezmenil.

## 11. Image a runtime dependency subject

Pri startup failure over:

- exact index/platform manifest digest;
- effective entrypoint a command;
- executable permissions;
- architecture;
- shebang/interpreter;
- dynamic loader a libraries;
- runtime user a working directory;
- certificates/NSS/timezone files;
- writable paths;
- healthcheck executable.

`exec format error` môže vzniknúť pre:

- wrong architecture;
- invalid shebang;
- CRLF script;
- missing interpreter;
- corrupted executable.

`no such file or directory`, hoci binary existuje, často znamená chýbajúci dynamic loader alebo shebang interpreter.

```bash
file ./binary
readelf -l ./binary
ldd ./binary
```

Minimal/distroless image nemusí mať shell. Použi `docker top`, inspect, debug toolbox alebo host namespace tooling podľa security policy; nepridávaj permanentný debug toolchain do production artifactu iba kvôli incidentu.

## 12. Mount a data identity

Mount troubleshooting nezačína otázkou „existuje volume?“, ale:

```text
Ktorý logical data subject je pripojený?
Kto má writer authority?
Je schema compatible?
Ktorý daemon/project resolve-ol source?
```

```bash
docker inspect --format '{{json .Mounts}}' <container>
docker volume inspect <volume>
```

Hypotézy:

- mount obscuring skryl image files;
- relative bind source sa resolve-ol na inom hoste/path-e;
- project rename vytvoril nový empty volume;
- wrong environment volume bol pripojený;
- UID/GID/user namespace/LSM denial;
- read-only alebo noexec policy;
- stale writer nebol fenced;
- dáta boli iba vo writable layeri;
- `down -v` alebo prune odstránil authoritative object.

Recovery musí overiť data ID, schema, writer epoch, business records a clean restore; nestačí, že directory nie je prázdny.

## 13. Resource pressure má viac boundaries

```bash
docker stats --no-stream
journalctl -k --since "30 min ago"
cat /proc/pressure/cpu
cat /proc/pressure/memory
cat /proc/pressure/io
df -h
df -i
```

Rozlišuj:

- cgroup memory limit vs. host OOM;
- CPU usage vs. throttling;
- memory working set vs. reclaim pressure;
- disk bytes vs. inode exhaustion;
- filesystem quota vs. host capacity;
- application I/O wait vs. backend latency;
- PID limit vs. host process capacity;
- open files, sockets a ephemeral ports;
- container logs vs. volume vs. image/cache usage.

### Failure boundary: „host má voľnú RAM“

Container mal 512 MiB cgroup limit a application heap target 480 MiB. Krátky native buffer spike vyvolal cgroup OOM, hoci host mal 16 GiB free.

```text
host capacity je dostupná
→ cgroup boundary ju workloadu nepovoľuje
→ process dostane SIGKILL
→ restart dočasne obnoví service
```

Zvýšenie limitu môže byť containment, nie root-cause closure. Treba overiť memory profile, heap contract, concurrency a host capacity planning.

## 14. Disk, content stores a logs

Docker disk spotrebúvajú odlišné owners:

- image/content blobs;
- unpacked snapshots;
- writable layers;
- named volumes;
- BuildKit cache;
- temporary pull/build/export data;
- container logs;
- plugin data.

```bash
docker system df -v
docker buildx du
df -h
df -i
```

`docker system prune` nemusí riešiť growing application volume ani external logging path. Môže však odstrániť rollback images, stopped evidence, cache alebo volumes podľa options.

Pred cleanupom definuj:

- object owner;
- active/rollback reference inventory;
- persistent data classification;
- backup/restore evidence;
- active build/pull leases;
- expected reclaimed bytes/inodes;
- recovery postup.

## 15. Network diagnosis sleduje flow

Network symptom fixni na flow subject:

```text
source namespace/address/port
→ DNS answer a endpoint generation
→ route/interface
→ veth/bridge alebo host namespace
→ pre-NAT tuple
→ publication/forwarding/firewall verdict
→ post-NAT destination
→ listener a readiness
→ reverse path/conntrack
→ client-visible response
```

Začni od listenera, nie od firewallu:

```bash
docker exec <container> ss -lntup
docker port <container>
docker inspect <container>
docker network inspect <network>
ss -lntp
```

Potom over DNS, route, NAT/firewall, upstream policy a client path.

### Failure boundaries

- application počúva iba na container `127.0.0.1`;
- mapping zamieňa host a container port;
- port je publikovaný iba na host loopbacku;
- host `INPUT` je čistý, no traffic ide forwarding/NAT pathom;
- service names sú v rozdielnych Compose projects/networks;
- endpoint IP bola recyklovaná, application drží stale connection;
- conntrack alebo ephemeral ports sú vyčerpané;
- MTU/PMTUD spôsobuje iba large-payload failure;
- IPv4 a IPv6 exposure sa líšia.

Host network alebo privileged mode nie sú diagnostika. Odstraňujú boundaries a môžu symptom zakryť.

## 16. Registry a pull path

Image pull failure môže vzniknúť v:

```text
reference resolution
→ authentication/authorization
→ index/platform selection
→ manifest/config/layer reachability
→ TLS/proxy/DNS path
→ local content/snapshot import
→ runtime compatibility
```

Over immutable reference:

```bash
docker pull registry.example.com/atlas/payments@sha256:<digest>
docker image inspect <reference>
docker manifest inspect <reference>
```

Hypotézy:

- wrong repository/reference;
- tag presunutý na iný digest;
- missing platform manifest;
- incomplete replication alebo GC;
- auth scope;
- CA/proxy/DNS failure;
- stale mirror;
- local snapshot/content corruption;
- artifact je pullable, ale platform runtime je incompatible.

## 17. Build incident je samostatný subject

Pri BuildKit/Buildx failure rozlišuj:

```text
builder selection
→ context/frontend translation
→ source/base pull
→ graph node execution
→ cache import/reuse
→ platform scheduling/emulation
→ secret/SSH/entitlement
→ exporter/push
→ attestation/publication read-back
```

```bash
docker buildx ls
docker buildx inspect --bootstrap
docker buildx build --progress=plain .
docker buildx du
```

Build success bez exporteru neznamená publikovaný image. Cache hit nemusí byť fresh ani trusted. Clean build failure odhaľuje skrytý input dependency. Multi-platform success potrebuje per-platform runtime evidence.

## 18. Compose incident je project reconciliation incident

Fixni:

- exact Docker context;
- project name;
- Compose file/include/override/profile inventory;
- resolved-model digest;
- external/managed resource ownership;
- image digests;
- container generations;
- network/volume identities;
- one-shot operation IDs;
- orphan inventory.

```bash
docker compose config
docker compose config --environment
docker compose ps -a
docker compose images
docker compose top
docker compose logs --timestamps --tail=500
```

`depends_on` rieši create/start ordering podľa zvoleného condition, nie permanentnú dependency dostupnosť. `up` je bounded reconciliation command, nie continuous controller. `down -v` a `--remove-orphans` potrebujú destructive-scope review.

## 19. Competing hypotheses pre Atlas incident

Po zafixovaní subjectu vznikli tieto hypotézy:

1. host B beží na inom image platform manifest digeste;
2. host B má stale container s predchádzajúcou configuration epoch;
3. API process je healthy, ale proxy smeruje na stale endpoint;
4. connection pool používa recyklovanú DB IP;
5. cgroup CPU throttling spôsobuje timeouty;
6. conntrack table alebo ephemeral ports sú pod pressure;
7. volume obsahuje nesprávny retry-ledger data subject;
8. healthcheck overuje iba local PID/endpoint;
9. Docker daemon je pomalý, ale workload plane je zdravý;
10. external DB/cache dependency má incident nezávislý od Dockeru;
11. restart dočasne pomáha, pretože resetuje connection pool, nie preto, že opravuje artifact;
12. klienti retryujú non-idempotent payment operation.

Hypotézy sú užitočné iba vtedy, keď každá má diskriminačný observation point.

## 20. Discriminating observations

| Hypotéza | Dôkaz, ktorý ju odlíši |
|---|---|
| wrong image digest | Engine inspect, registry manifest, deployed digest inventory |
| stale config | source/resolved/create/process-loaded generation comparison |
| stale endpoint | DNS answer, network endpoint ID, proxy upstream generation |
| CPU throttle | cgroup `cpu.stat`, pressure a request latency correlation |
| conntrack/ports | conntrack counters, socket summary, new vs. existing flow behavior |
| wrong data | mount source, data ID, schema, writer epoch, DB audit |
| shallow health | exact health command/history vs. external request oracle |
| daemon-only issue | API latency/logs vs. existing process and direct workload checks |
| external dependency | downstream SLI/audit from non-container clients |
| retry amplification | request IDs, client retry policy, duplicate authorization audit |

Nesprávna diagnóza často vznikne, keď tím sleduje iba supportujúci dôkaz a nehľadá observation point, ktorý konkurenčnú hypotézu vyvráti.

## 21. Atlas finding

Na hoste B bol správny image digest aj configuration epoch. Application listener a healthcheck fungovali. Packet capture a conntrack counters ukázali, že nové outbound DB connections zlyhávali pri vysokej concurrency, zatiaľ čo existujúce connections fungovali.

Cgroup CPU ani memory pressure neboli príčinou. Host mal vyčerpaný ephemeral port/NAT tuple pri agresívnych retries po krátkom DB incidente.

```text
DB latency spike
→ application otvorí mnoho nových retries bez dostatočného backoffu
→ host ephemeral/NAT capacity sa vyčerpá
→ nové spojenia zlyhávajú
→ healthcheck používa existujúce local path a zostáva green
→ clients retryujú a incident zosilňujú
→ restart vyčistí connection pool a dočasne zníži pressure
```

Docker bol observation a resource boundary, ale primárny causal loop vznikol v application retry a connection lifecycle-e.

## 22. Containment

Containment má znížiť dopad bez straty evidence:

- vyraď host B alebo affected containers z trafficu;
- obmedz client/application retry rate a concurrency;
- zastav non-idempotent side effects pri neistej deduplikácii;
- zachovaj conntrack/socket/cgroup/process evidence;
- nevykonávaj broad prune ani host-network bypass;
- neotváraj firewall broadly;
- chráň payment ledger a downstream audit;
- podľa potreby zvýš capacity iba ako dočasný, zaznamenaný control.

## 23. Recovery

Recovery opravila authoritative sources:

1. bounded exponential backoff a jitter;
2. connection pool limits;
3. idempotency key pre authorization;
4. circuit breaker/degradation pri DB pressure;
5. host ephemeral/conntrack capacity upravenú podľa meraného load modelu;
6. nový immutable image digest;
7. staged replacement containers;
8. synthetic aj real business-path verification.

Ručná zmena v bežiacom containeri alebo hoste nesmie zostať jediným zdrojom pravdy.

## 24. Over pôvodný outcome

Po recovery bolo overené:

- exact release, configuration, data a endpoint generation;
- normalizované new-connection success rate;
- žiadne conntrack/ephemeral exhaustion;
- payment authorization exactly once;
- latency pod 800 ms;
- graceful behavior pri opakovanom DB latency experimente;
- forbidden staging access absent;
- starý image digest odstránený z active deployment inventory;
- replacement container nemení data ani configuration subject.

„Error rate klesol“ by nebolo dostatočné closure.

## 25. Posuň control skôr

Incident viedol k týmto controls:

- deployment manifest s image/config/data/endpoint generations;
- host network-capacity SLO a conntrack alerts;
- retry budget a idempotency contract tests;
- external readiness/business synthetic;
- cgroup, socket a network evidence v incident bundle;
- controlled failure test DB latency;
- explicitné rollback a containment playbooky;
- zákaz destructive commands bez inventory/approval;
- centralizované Docker events a daemon/kernel correlation.

## 26. Controlled reproduction

Reproduction musí zachovať relevantný subject:

```text
pin image/platform digest
→ export redacted resolved runtime config
→ použiť rovnaký kernel/runtime/platform class
→ vytvoriť izolovaný data subject alebo snapshot clone
→ reprodukovať rovnaký flow/load/dependency condition
→ meniť jednu hypotézu naraz
→ zaznamenať before/after evidence
```

„Po rebuild-e to funguje“ nie je root cause, pokiaľ nevieš, ktorý input, cache, artifact alebo runtime state sa zmenil.

## 27. Remediation hierarchy

Preferované poradie:

```text
contain impact
→ opraviť versionovaný source/config/policy
→ vytvoriť nový immutable artifact alebo state generation
→ overiť artifact a recovery eligibility
→ nahradiť runtime instance
→ overiť pôvodný business outcome
→ uzavrieť adjacent risk a prevention
```

Ručná live oprava môže byť núdzový containment alebo diagnostický experiment. Musí byť zaznamenaná, reprodukovaná v authoritative source a následne odstránená replacementom.

## 28. Observation matrix

| Boundary | Hlavná identita | Typické observations |
|---|---|---|
| Client/context | context, endpoint, caller | `docker context`, client/server version |
| Engine | daemon host/config/generation | daemon logs, API latency, events |
| Container object/task | object ID, task, PID | inspect, top, exit/restart timeline |
| Artifact | index/platform digest | registry read-back, image config/history |
| Runtime config | resolved/create/loaded generation | Compose config, inspect, redacted app config |
| Process | PID 1, command, signals | logs, top, stop test, traces |
| Cgroup/host | cgroup ID a node | counters, PSI, OOM, limits |
| Storage | data ID, mount/writer epoch | mount/volume/backend inspect, audit |
| Network | flow/endpoint/publication generation | sockets, DNS, routes, counters, capture |
| Build | build/builder/cache/output subject | Buildx inspect, plain progress, registry/evidence |
| Business | request/operation ID | SLI, downstream audit, exact-once invariant |

Matrix pomáha vybrať observation points. Nie je náhradou hypotéz.

## 29. Deštruktívne anti-patterny

### Restart ako prvý krok

Môže vyčistiť pool, cache, pressure alebo transient state a odstrániť príčinné evidence.

### `docker system prune -a --volumes`

Môže odstrániť rollback artifacts, stopped incident evidence, cache a persistent data.

### `chmod 777`, privileged alebo host network

Obchádzajú identity/security/network boundary a maskujú root cause.

### `docker exec` a permanentná live mutation

Vytvára neversionovaný drift, ktorý zmizne pri replacement-e.

### Diagnostika iba z application logs

Ignoruje daemon, kernel, cgroups, storage, network a deployment subject.

### Mutable tag pri reprodukcii

Rovnaký názov môže označovať iný artifact.

### Dump celého environmentu

Môže zverejniť secrets a rozšíriť incident.

### Cleanup pred restore/ownership kontrolou

Existencia snapshotu alebo volume-u nepreukazuje clean restore.

## 30. Praktický incident checklist

```text
[ ] Pôvodný user/business outcome a forbidden outcomes
[ ] Impact, scope a presná timeline
[ ] Docker context, Engine host a Compose project
[ ] Image index/platform digest a container generation
[ ] Resolved/create/process-loaded configuration generation
[ ] Data ID, schema, mount a writer epoch
[ ] Endpoint/DNS/publication/flow generation
[ ] Process, exit, health a signal evidence
[ ] Cgroup limits, counters, PSI a kernel events
[ ] Disk bytes, inodes, logs, volumes a build cache owners
[ ] Registry/build provenance a posledná zmena
[ ] Aspoň dve konkurenčné hypotézy
[ ] Diskriminačný observation point pre každú hypotézu
[ ] Evidence uložená pred restart/delete/prune
[ ] Containment nepoškodzuje dáta ani evidence
[ ] Recovery je v authoritative source/artifact/state
[ ] Pôvodný outcome aj forbidden outcomes overené
[ ] Skorší control, owner a follow-up closure
```

## 31. Prechod ku Kubernetes

Docker troubleshooting učí identifikovať artifact, process, cgroup, mount, flow, health a runtime generation na jednom Engine hoste. Kubernetes pridáva ďalšie reconciliation a identity vrstvy:

```text
API desired state
→ controllers a scheduler
→ node/kubelet/CRI
→ Pod sandbox a containers
→ Services/endpoints/network policy
→ volumes a storage controllers
→ probes a rollout state
```

Základná metóda zostáva rovnaká: zafixovať subject, rozlíšiť desired a effective state, sledovať observation points a overiť pôvodný workload outcome. Mení sa počet control planes a reconciliation owners.

## 32. Kontrolné otázky

1. Prečo symptom alebo container name nestačí ako incident subject?
2. Ktoré evidence sú volatile a treba ich zachovať pred restartom?
3. Ako sa líši Engine object, runtime process, health a business outcome?
4. Prečo exit code `137` nepreukazuje konkrétnu OOM príčinu?
5. Ako odlíšiš desired, container create a process-loaded configuration?
6. Prečo host free memory nevylučuje cgroup OOM?
7. Aký flow model použiješ pri nefunkčnom published porte?
8. Prečo clean build failure znamená neúplný input contract?
9. Čo robí observation point diskriminačným?
10. Ako overíš, že recovery odstránila príčinu, nie iba symptom?

## Glossary impact

Relevantné pojmy: Docker incident subject, original outcome contract, forbidden outcome, volatile evidence inventory, management-plane/workload-plane split, container generation, hypothesis evidence matrix, discriminating observation point, Docker containment subject, authoritative remediation, subject-preserving reproduction, incident closure verdict a Docker-to-Kubernetes diagnostic bridge.

## Oficiálna dokumentácia

- [Troubleshoot the Docker daemon](https://docs.docker.com/engine/daemon/troubleshoot/)
- [Read daemon logs](https://docs.docker.com/engine/daemon/logs/)
- [Docker logging](https://docs.docker.com/engine/logging/)
- [`docker system df`](https://docs.docker.com/reference/cli/docker/system/df/)
- [`docker events`](https://docs.docker.com/reference/cli/docker/system/events/)
- [Docker Desktop troubleshooting](https://docs.docker.com/desktop/troubleshoot-and-support/troubleshoot/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Praktický Docker projekt od Dockerfile-u po overený Compose runtime](docker-practical-walkthrough.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Kubernetes architecture →](../09-kubernetes/kubernetes-architecture.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
