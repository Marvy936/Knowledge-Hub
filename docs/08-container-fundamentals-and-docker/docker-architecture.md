# Docker architecture

Docker nie je jeden process ani synonymum pre container. Je to control a runtime stack, v ktorom klient odošle požiadavku privilegovanému Engine API, daemon vytvorí alebo zmení Docker objects, containerd spravuje task a snapshot lifecycle a OCI runtime vytvorí konkrétny Linux process.

Najdôležitejší mentálny model tejto kapitoly je:

```text
operator intent a Docker context
→ immutable API operation subject
→ daemon authorization a object-state transition
→ image, snapshot, network a storage príprava
→ containerd task a runtime shim
→ OCI runtime create/start
→ process, readiness a events
→ object/task/runtime reconciliation
→ stop, remove, recovery alebo cleanup
```

Tento chain vysvetľuje, prečo úspech CLI príkazu nie je automaticky úspech aplikácie, prečo timeout neznamená, že operácia neprebehla, a prečo `docker ps` nie je úplný diagnostický obraz.

## 1. Jeden Atlas workload cez celý Docker stack

Atlas Payments nasadzuje image:

```text
registry.atlas.example/payments/api@sha256:9f3...
```

Release workflow chce vytvoriť container:

```text
name: atlas-payments-api-r42
host port: 8443
container port: 8080
volume: atlas-payments-config-r42
network: atlas-payments-prod
```

Operation subject obsahuje minimálne:

- Docker context a daemon endpoint,
- workload identity a authorization identity,
- requested image digest,
- container name a labels,
- runtime command a environment contract,
- mount, network a port-publication contract,
- resource a security policy,
- request/run correlation ID.

Tento subject musí zostať rozpoznateľný aj vtedy, keď klient stratí response. Bez neho nevieš bezpečne rozlíšiť „request sa nikdy nedostal k daemonu“ od „container už beží a iba sa stratilo potvrdenie“.

## 2. Docker CLI a context: prvá identity boundary

Docker CLI:

1. parsuje command,
2. načíta environment a Docker context,
3. vyberie Engine endpoint,
4. zostaví API request,
5. odošle ho,
6. zobrazí response alebo stream events/logov.

CLI nevytvára Linux namespaces ani cgroups. Rozhodujúce je, ku ktorému daemonu hovorí.

```bash
docker context show
docker context inspect
docker version
docker info
```

### Failure boundary: správny command, nesprávny daemon

Operator chce odstrániť lokálny test container:

```bash
docker rm -f atlas-payments-api-r42
```

Aktívny context však smeruje na production host. Syntax aj autorizácia sú správne, preto Docker vykoná presne nesprávnu operáciu na nesprávnom subjecte.

Príčina nie je v `docker rm`. Príčina je neoverená target identity.

Kontrolný model pred deštruktívnou operáciou:

```text
command intent
→ expected environment
→ resolved context/endpoint
→ daemon identity
→ object identity
→ mutation
```

## 3. Engine API a daemon: authoritative object manager

Docker Engine API je versionované HTTP API dostupné napríklad cez Unix socket, named pipe, SSH context alebo chránený TCP endpoint.

Linux default:

```text
/var/run/docker.sock
```

`dockerd` je authoritative manager Docker object metadata a orchestration requestov. Spravuje alebo koordinuje:

- images a registry pull/push,
- containers a ich desired lifecycle,
- networks a endpoints,
- volumes a mounts,
- port publication,
- logs a events podľa drivera,
- build requests,
- komunikáciu s containerd.

Access k daemonu je host-admin-like authority. Klient s možnosťou vytvoriť privileged container alebo host bind mount často dokáže ovládnuť host.

### Security consequence

Mount Docker socketu do application containeru nie je obyčajné „sprístupnenie API“. Je to prenesenie širokej daemon authority cez novú trust boundary.

## 4. `docker run` ako koordinovaná state transition

`docker run` je z pohľadu používateľa jeden command, ale z pohľadu systému ide o viac prechodov:

```text
resolve image
→ create container metadata
→ prepare snapshot/rootfs
→ validate a attach mounts
→ allocate network endpoint
→ install port publication
→ create containerd task
→ create runtime bundle
→ OCI runtime create
→ OCI runtime start
→ observe PID 1
→ report events/status
```

Približne zodpovedá:

```text
docker create
+
docker start
```

Každý prechod má vlastnú failure boundary. Container object môže existovať v stave `created`, aj keď process nikdy nezačal. Network endpoint alebo mount môže byť pripravený skôr než task. Process môže bežať, aj keď klient nedostal response.

## 5. Image, content a snapshot vrstva

Daemon alebo containerd image store rieši:

- reference resolution,
- registry pull,
- manifest a layer verification,
- content storage,
- unpacked snapshots,
- leases a garbage collection.

Image digest identifikuje distribution content. Runtime snapshot je lokálna unpacked reprezentácia. Container writable layer je ďalšia instance-specific vrstva.

Preto tieto identity nesmieš zamieňať:

```text
registry digest
≠ local content record
≠ unpacked snapshot
≠ container writable snapshot
```

### Failure boundary: disk full počas prípravy snapshotu

Manifest a časť layers môžu byť stiahnuté, ale unpack alebo writable snapshot zlyhá na kapacite či inodoch. Výsledkom môže byť:

- lokálny image record,
- partial alebo nepoužitý content,
- container object v `created` alebo error stave,
- žiadny runtime process.

Blind `docker system prune` nie je diagnostika. Najprv treba určiť, ktoré references, leases, snapshots, containers a build caches držia content.

## 6. Network a storage object lifecycle

Docker network a volume nie sú properties jedného processu. Sú to samostatné objects s vlastnou identitou a lifecycle-om.

Pri create/start flow daemon typicky:

- resolveuje network object,
- vytvorí endpoint a IP/DNS identity,
- pripraví forwarding a port publication,
- resolveuje volume alebo bind source,
- validuje mount target a options,
- odovzdá mounts do runtime configuration.

Zmazanie containeru preto automaticky nemusí zmazať:

- image,
- named volume,
- custom network,
- external logs,
- registry content.

Cleanup musí vychádzať z ownership modelu, nie z predpokladu, že všetko je súčasť containeru.

## 7. containerd, task a runtime shim

Docker Engine deleguje low-level container lifecycle na containerd.

Dôležité identity:

- **container metadata** — desired a configured runtime object,
- **task** — bežiaci alebo ukončený process lifecycle v containerd,
- **runtime shim** — process udržiavajúci runtime/task communication a exit state,
- **OCI runtime invocation** — create/start/delete operácia nad runtime bundle,
- **application PID 1** — reálny workload process.

`dockerd`, containerd, shim a application process majú rozdielne failure modes.

### Failure boundary: management plane zlyhá, workload beží

Ak `dockerd` prestane odpovedať, už spustený task nemusí okamžite skončiť. Application môže ďalej obsluhovať traffic, zatiaľ čo:

- `docker ps` nefunguje,
- nové create/stop operácie zlyhávajú,
- operator nevie získať Engine-level state,
- containerd a shim stále držia process.

Recovery nesmie automaticky killnúť workload iba preto, že control API je nedostupné.

## 8. OCI runtime: z configuration na process

Low-level OCI runtime dostane bundle s rootfs a `config.json` a vykoná približne:

1. vytvorí alebo pripojí namespaces,
2. nastaví UID/GID a credentials,
3. pripojí rootfs a mounts,
4. aplikuje cgroups,
5. aplikuje capabilities, `no_new_privs`, seccomp a LSM context,
6. pripraví environment, working directory a process args,
7. vytvorí container process,
8. spustí PID 1.

Failure `OCI runtime create failed` preto môže byť spôsobený napríklad:

- neexistujúcim executable alebo interpreterom,
- chybným mountom,
- UID/GID alebo permission contractom,
- seccomp/LSM denial,
- unsupported cgroup alebo namespace feature,
- architecture/runtime incompatibility,
- invalid runtime configuration.

Jedna generická error veta je iba surface symptom. Diagnostika musí pokračovať k runtime bundle, daemon/containerd logom a host kernel evidence.

## 9. Running nie je ready ani correct

Docker state `running` znamená najmä, že task a PID 1 existujú. Neznamená, že:

- application počúva na správnom porte,
- dependencies sú dostupné,
- mounted data majú správnu identitu,
- healthcheck je kvalitný,
- workload prijíma production traffic,
- business transaction funguje.

Potrebný evidence chain:

```text
Docker object running
→ process identity a command
→ socket/listener
→ dependency readiness
→ health result
→ external request
→ business/runtime outcome
```

## 10. Events a observation points

Žiadna jednotlivá command output vrstva nestačí.

### Client a target identity

```bash
docker context show
docker version
docker info
```

### Docker object state

```bash
docker ps -a
docker inspect atlas-payments-api-r42
docker events --since 10m
```

### Runtime outcome

```bash
docker logs atlas-payments-api-r42
docker stats atlas-payments-api-r42
docker exec atlas-payments-api-r42 <diagnostic-command>
```

### Host a lower layers

- daemon service logs,
- containerd a runtime logs,
- process tree a sockets,
- kernel OOM a LSM audit,
- cgroup events a pressure,
- filesystem bytes/inodes,
- network rules a conntrack,
- mount a device state.

Observation point treba vybrať podľa hypotézy. `docker logs` nevysvetlí prečo OCI runtime nevedel pripojiť mount. Host `df` sám nevysvetlí, ktorý reference graph drží Docker content.

## 11. Causal walkthrough: timeout, retry a obsadený port

### Symptóm

Pipeline spustí:

```bash
docker run -d \
  --name atlas-payments-api-r42 \
  -p 8443:8080 \
  registry.atlas.example/payments/api@sha256:9f3...
```

CLI po network timeoute skončí chybou. Automatický retry potom hlási, že container name alebo port už existuje.

### Competing hypotheses

1. prvý API request sa nikdy nedostal k daemonu;
2. daemon vytvoril iba container metadata;
3. network endpoint a port boli alokované, task však nezačal;
4. task a process bežia, stratila sa iba response;
5. retry smeruje na iný Docker context;
6. rovnaký port používa nesúvisiaci workload;
7. starý partial object z predchádzajúceho release-u nebol odstránený.

### Discriminating observation points

Najprv zachovaj operation subject:

```text
context
endpoint
container name
image digest
release label
requested port
pipeline run ID
```

Potom over:

```bash
docker context show
docker ps -a --filter name=atlas-payments-api-r42
docker inspect atlas-payments-api-r42
docker events --since <operation-start>
```

Ďalej podľa state-u:

- daemon log: prijatý create/start request,
- image digest: presný pulled subject,
- network inspect: endpoint a port mapping,
- host `ss`: listener na 8443,
- application logs a health: skutočný runtime outcome,
- containerd/task evidence: process existuje aj pri Engine probléme.

### Finding

Daemon vytvoril object, endpoint aj task; application už beží. Response sa stratila po úspešnom start-e. Retry nebol bezpečný, pretože pipeline interpretovala transport timeout ako „operácia neprebehla“.

### Containment a recovery

1. zastav ďalšie retries;
2. potvrď exact image digest a runtime configuration;
3. adoptuj existujúci container ako výsledok operácie, ak zodpovedá subjectu;
4. over readiness a external request;
5. zapíš výsledný container ID a deployment evidence;
6. odstráň iba objects, ktoré patria k neúspešnému subjectu.

Ak object existuje iba v partial stave, odstráň ho až po inventári network, mount a task side effects a následne vytvor nový operation subject.

### Skoršie controls

- deterministic container name alebo label viazaný na release/run,
- explicitný context a endpoint v pipeline,
- post-timeout reconciliation pred retry,
- request/deployment correlation ID,
- create a start ako pozorovateľné state transitions,
- runtime postcondition namiesto dôvery v CLI exit code.

## 12. Daemon restart a live restore

Daemon configuration change alebo upgrade môže vyžadovať restart. Dopad na existujúce tasks závisí od platformy a konfigurácie, napríklad live-restore behavioru.

Pred zmenou zaznamenaj:

- daemon a containerd versions,
- active containers a criticality,
- restart a rollback config,
- expected task survival behavior,
- post-restart object/task reconciliation,
- logging a network/storage continuity.

Po restarte nestačí, že daemon service je `active`. Over:

```text
Engine API dostupné
→ containers znovu inventarizované
→ tasks/processes správne korelované
→ network a storage stále funkčné
→ application outcome zachovaný
```

## 13. Docker Desktop ako ďalšia boundary

Na Windows a macOS Docker Desktop typicky vkladá medzi host UI/CLI a Linux Engine ďalšiu VM alebo virtualizačnú vrstvu.

To mení observation points:

```text
host CLI/context
→ Desktop service a VM
→ Linux dockerd/containerd
→ container process
```

Bind mounts, `localhost`, networking, credentials a filesystem performance môžu prechádzať Desktop-specific translation vrstvou. Diagnostika preto musí určiť, či problém vzniká:

- na hoste,
- v Desktop VM/service,
- v Engine,
- v container runtime,
- v aplikácii.

## 14. Rootful, rootless a authority model

Rootful daemon poskytuje širokú kompatibilitu, ale jeho kompromitácia alebo socket exposure má veľký blast radius.

Rootless Docker znižuje host-root authority použitím user namespaces a unprivileged helpers, ale nemení tieto fakty:

- application môže byť zraniteľná,
- host kernel zostáva shared dependency,
- user-level credentials a data môžu byť citlivé,
- networking/storage behavior môže byť odlišný,
- rootless nie je automaticky tenant-grade sandbox.

Security rozhodnutie sa robí podľa threat modelu a effective authority, nie iba podľa labelu `rootless`.

## 15. Referenčný object a lifecycle katalóg

| Object alebo vrstva | Authoritative identity | Typický lifecycle | Hlavné failure dôkazy |
|---|---|---|---|
| Docker context | context name + endpoint + TLS/SSH metadata | select/update/remove | `docker context inspect`, connection logs |
| Image | repository digest + local content | pull/tag/remove/GC | manifest/content/snapshot evidence |
| Container object | container ID + name + labels | create/start/stop/remove | Engine events, inspect, daemon log |
| Task/process | containerd namespace/task ID + PID | create/start/exit/delete | task/shim/runtime/host process evidence |
| Network endpoint | network ID + endpoint/container ID | allocate/connect/disconnect | network inspect, veth/firewall/conntrack |
| Volume/mount | volume/data identity + mount target | create/attach/mount/detach/remove | mount, filesystem, driver/backend evidence |
| Build cache | builder/cache record subject | import/use/export/GC | build progress, cache refs, builder storage |

Katalóg pomáha pomenovať objekty, ale diagnóza musí stále sledovať konkrétny operation lifecycle.

## 16. Praktické controls

- explicitne pinuj Docker context pre automation;
- chráň socket a remote API ako host-admin boundary;
- používaj exact image digest a release labels;
- oddeľ trusted production runtime od untrusted builds;
- koreluj Engine events, container ID, task a application outcome;
- pri timeoute najprv reconcile state, až potom retry;
- nemaž ručne obsah z Docker data rootu;
- používaj `prune` iba s ownership a retention inventárom;
- validuj daemon config a restart behavior pred production zmenou;
- odlišuj `running`, healthy, ready a business-correct stav.

## 17. Kontrolné otázky

1. Prečo Docker CLI nie je vrstva, ktorá priamo vytvára container process?
2. Čo musí obsahovať Docker API operation subject?
3. Prečo môže CLI timeout nasledovať po úspešnom vytvorení containeru?
4. Aký je rozdiel medzi Docker container objectom a containerd taskom?
5. Čo vykonáva OCI runtime?
6. Prečo `running` neznamená ready?
7. Ktoré objects môžu prežiť odstránenie containeru?
8. Prečo je Docker socket host-admin-like authority?
9. Ako sa mení diagnostika pri Docker Desktop?
10. Prečo sa pred retry musí vykonať state reconciliation?

## Glossary impact

Relevantné pojmy: Docker API operation subject, Docker context identity, Docker object state transition, container task subject, runtime shim, object-task reconciliation, unknown Docker operation outcome, daemon authority boundary, Docker Desktop boundary a live-restore verification.

## Oficiálna dokumentácia

- [Docker Engine](https://docs.docker.com/engine/)
- [Docker overview and architecture](https://docs.docker.com/get-started/docker-overview/)
- [Docker Engine API](https://docs.docker.com/reference/api/engine/)
- [Alternative container runtimes](https://docs.docker.com/engine/daemon/alternative-runtimes/)
- [Docker daemon configuration](https://docs.docker.com/engine/daemon/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Container security](container-security.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Dockerfile →](dockerfile.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
