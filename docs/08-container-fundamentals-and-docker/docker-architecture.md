# Docker architecture

Docker nie je jeden process ani jedno binary. Je to client-server platforma, ktorá spravuje images, containers, networks, volumes a build alebo runtime operácie cez API. Keď používateľ zadá `docker run`, CLI nevytvorí Linux namespaces priamo. Odošle request Docker Engine-u. Engine resolve-ne image, vytvorí Docker container object, pripraví storage a network, deleguje low-level task lifecycle cez containerd a OCI runtime a napokon sleduje hlavný process.

Tento rozklad je dôležitý pri troubleshooting-u. Chyba môže vzniknúť ešte v klientovi, pri výbere Docker contextu, v API spojení, v image pull flowe, pri create operácii, v containerd snapshotter-i, pri OCI runtime create alebo až po úspešnom exec aplikácie. Všetky sa môžu používateľovi javiť ako „Docker nejde“, ale každá vrstva má iné dôkazy a inú recovery.

Budeme sledovať príkaz:

```bash
docker run --detach \
  --name payments-api \
  --publish 127.0.0.1:18080:8080 \
  atlas/payments-api:1.0.0
```

## 1. Docker CLI je API klient

`docker` CLI spracuje arguments, načíta context a configuration a zavolá Docker Engine API. Samotný CLI nemusí bežať na rovnakom hoste ako daemon.

```text
shell
→ docker CLI
→ selected Docker context
→ transport: Unix socket, named pipe, SSH alebo TCP/TLS
→ Docker Engine API
```

Aktuálny context:

```bash
docker context show
docker context inspect
```

Toto je prvá kontrola pri incidente, keď príkaz vracia neočakávané containers alebo images. Používateľ môže byť pripojený k Docker Desktop VM, remote serveru alebo test daemonu namiesto production hosta.

```bash
docker info
```

Výstup kombinuje client a server informácie. Pri vzdialenom daemone server sekcia opisuje remote Engine, nie laptop, na ktorom sa vykonal CLI.

## 2. Transport a daemon authority

Na Linuxe CLI často komunikuje cez Unix socket:

```text
/var/run/docker.sock
```

Socket nie je obyčajný application endpoint. Engine môže vytvárať containers, mountovať host paths, meniť networks a spravovať volumes. Používateľ alebo process s broad accessom k socketu môže často získať host-level authority.

Preto:

```bash
ls -l /var/run/docker.sock
```

nie je iba diagnostika connectivity. Ukazuje aj security boundary. Členstvo v skupine `docker` sa typicky považuje za privilegovaný host access.

Remote TCP API musí používať authentication a TLS alebo bezpečný SSH context. Verejne dostupný neautentizovaný Docker API endpoint je kritické zlyhanie.

## 3. `dockerd` spravuje Docker objects

Docker daemon prijíma API requests a spravuje higher-level objects: images, containers, networks, volumes, plugins a ich metadata. Container object vznikne už pri `docker create`, ešte pred spustením procesu.

```bash
docker create \
  --name payments-api \
  --publish 127.0.0.1:18080:8080 \
  atlas/payments-api:1.0.0
```

Po úspešnom create:

```bash
docker inspect payments-api
```

ukáže image reference, effective command, environment, host config, mounts a network settings. `.State.Status` bude `created`. Žiadny application PID ešte nemusí existovať.

Táto separácia je praktická. Pred mutation process state-u možno overiť, či Engine vytvoril container s očakávaným userom, read-only root filesystemom, limitmi a mounts.

## 4. Image resolution a local image store

Ak image nie je lokálne dostupný alebo pull policy vyžaduje registry access, Engine resolve-ne reference a stiahne potrebné manifests, config a layers.

```text
repository:tag alebo repository@digest
→ registry authentication
→ index/manifest resolution
→ platform selection
→ blob download a digest verification
→ unpack do snapshotter/storage drivera
```

Pull možno vykonať samostatne:

```bash
docker pull registry.example.com/atlas/payments-api@sha256:<digest>
```

`docker image ls` zobrazuje user-facing image inventory, ale pri multi-platform a content store modeloch nemusí jedna tabuľka vysvetliť celý graph. `docker image inspect` a registry read-back odpovedajú na presnejšie otázky.

Pull failure nastáva pred application startom. Preto pri `manifest unknown`, TLS alebo authorization chybe application logs nebudú užitočné.

## 5. Container create skladá image defaults a runtime overrides

Image config môže definovať:

```text
USER
ENV
WORKDIR
ENTRYPOINT
CMD
HEALTHCHECK
```

Create request pridá alebo prepíše runtime state:

```text
name
mounts
ports
network membership
resource limits
capabilities a security options
restart policy
runtime environment a command overrides
```

Výsledok možno chápať ako:

```text
image config
+ docker create/run options
+ daemon defaults a platform capabilities
→ effective container configuration
```

Preto sa pri audite nečíta iba Dockerfile. Read-backuje sa `docker inspect` konkrétneho container ID.

## 6. Storage preparation

Pred process startom runtime pripraví root filesystem. Image layers sa použijú ako read-only lower snapshots a container dostane writable layer. Engine pripojí named volumes, bind mounts a tmpfs podľa create configuration.

```text
image layers
→ unpacked snapshot
→ container writable layer
→ mount namespace
→ volumes, bind mounts a tmpfs
```

Chyba môže vzniknúť pri chýbajúcom host path-e, unsupported mount option, volume pluginu, disk exhaustion alebo permission policy. Application process sa nemusí vôbec spustiť.

Storage stav:

```bash
docker inspect payments-api | jq '.[0].Mounts'
docker system df -v
```

## 7. Network preparation

Engine pripojí container do jednej alebo viacerých networks. Pri bridge modeli vytvorí alebo použije network endpoint, veth pair, address assignment a port publishing rules.

```text
Docker network object
→ endpoint a IP assignment
→ network namespace interface
→ routes a DNS configuration
→ host publishing/NAT
```

`docker network inspect NETWORK` ukazuje Engine-level desired a observed endpoint inventory. Neoveruje, že process počúva ani že host firewall alebo remote path funguje.

Port collision môže zablokovať start alebo create podľa platformy:

```text
Bind for 127.0.0.1:18080 failed: port is already allocated
```

V takom prípade image a application nemusia mať žiadny problém. Host port je už vlastnený iným listenerom alebo Docker objectom.

## 8. containerd a task lifecycle

Docker Engine používa containerd pre nižší container lifecycle, image content a snapshot alebo task management podľa verzie a konfigurácie. containerd nie je náhrada Docker CLI user experience; poskytuje nižšie primitives.

Zjednodušený tok:

```text
dockerd container start request
→ containerd task create
→ snapshot/rootfs a runtime specification
→ runtime shim
→ OCI runtime create/start
```

Runtime shim pomáha udržať stdio a process lifecycle oddelený od dlhodobej dostupnosti centrálneho daemon processu. Presná implementácia sa vyvíja, preto pri low-level diagnostike treba poznať konkrétnu Engine a containerd verziu.

```bash
docker version
docker info
```

Host administrátor môže navyše kontrolovať systemd services a logs:

```bash
systemctl status docker
journalctl -u docker --since '30 minutes ago'
systemctl status containerd
journalctl -u containerd --since '30 minutes ago'
```

Na Docker Desktop sú tieto komponenty vo vnútornej VM a diagnostika sa líši.

## 9. OCI runtime vytvorí process

Low-level OCI runtime, často `runc`, dostane pripravený rootfs a runtime configuration. Vytvorí namespaces, cgroups a process credentials, aplikuje capabilities, seccomp a mounts a vykoná entrypoint.

```text
OCI bundle/config
→ runtime create
→ namespaces a cgroups
→ mounts a security policy
→ execve entrypoint
→ process PID 1
```

Chyby ako nesprávna architektúra, chýbajúci dynamic loader, neplatný executable permission alebo seccomp/LSM denial sa prejavia v tejto alebo bezprostredne nasledujúcej vrstve.

`exec format error` smeruje na binary alebo platform mismatch. `no such file or directory` môže znamenať chýbajúci executable, shebang interpreter alebo ELF loader. `permission denied` môže vzniknúť z mode bits, read-only mountu, capabilities alebo LSM.

## 10. Start, attach a detached mode

`docker start` spustí process v už vytvorenom container objecte:

```bash
docker start payments-api
```

Detached mode znamená, že CLI nečaká pripojený k foreground stdio. Neznamená, že application beží na pozadí pomocou vlastného daemonization modelu. Hlavný process musí zostať foreground PID 1 z pohľadu container lifecycle-u.

Process stav:

```bash
docker ps -a --filter name=payments-api
docker inspect payments-api --format '{{json .State}}' | jq .
docker top payments-api -eo pid,ppid,user,args
```

Engine môže úspešne prijať start a process môže o milisekundu neskôr exitnúť. Preto API success nie je application readiness.

## 11. Logs a stdio

Docker zachytáva stdout a stderr hlavného procesu podľa logging drivera. Aplikácia má logovať do stdout/stderr namiesto zapisovania jediných logs do container writable layer.

```bash
docker logs --timestamps payments-api
```

Logging driver môže ukladať lokálne files, používať journald alebo odosielať do external systému. `docker logs` nemusí fungovať rovnako pri každom driveri.

Log success nepreukazuje, že log bol doručený do central observability. Local daemon môže log prijať, ale forwarding pipeline môže zlyhať.

## 12. Healthcheck ako Engine-managed state

Ak image alebo runtime config definuje healthcheck, Engine pravidelne spúšťa command a udržiava health state oddelene od process state.

```bash
docker inspect payments-api \
  --format '{{json .State.Health}}' | jq .
```

Process môže byť `running` a health `starting` alebo `unhealthy`. Healthcheck command beží v container namespaces a filesystem view. Môže overovať local endpoint, ale nepreukazuje host-published port alebo external dependency path, pokiaľ to explicitne netestuje.

Health history je bounded a nemá byť jediným incident archívom. Relevantné failures treba dostať do central telemetry.

## 13. Stop a signal lifecycle

`docker stop` pošle configured stop signal, štandardne `SIGTERM`, a čaká grace period. Ak process neskončí, runtime použije `SIGKILL`.

```bash
docker stop --time 15 payments-api
```

Aplikácia ako PID 1 musí signal spracovať. Shell-form entrypoint môže signal zachytiť alebo neforwardovať.

Po stop-e:

```bash
docker inspect payments-api \
  --format 'status={{.State.Status}} exit={{.State.ExitCode}} finished={{.State.FinishedAt}}'
```

Exit code `0` dokazuje process-level ukončenie. Neoveruje dokončenie business transakcií alebo flush persistentného state-u.

## 14. Restart nie je recreate

`docker restart` zastaví a znovu spustí rovnaký container object. Používa rovnaký image ID, mounts, environment a host config.

```bash
docker restart payments-api
```

Ak bol image tag medzitým prepísaný alebo environment file zmenený, restart tieto zmeny automaticky neaplikuje. Potrebný je nový container create alebo Compose reconciliation.

```text
restart
→ rovnaká container generation a config

recreate
→ nový container object z nového effective modelu
```

Toto rozlíšenie je častou príčinou „nasadil som nový image, ale aplikácia je stále stará“.

## 15. Delete a cleanup

`docker rm` odstráni container object a writable layer. Named volumes sa štandardne neodstránia, pokiaľ to príkaz explicitne nepožiada alebo nejde o anonymous volume s vhodnou voľbou.

```bash
docker rm payments-api
```

Pred odstránením incident containeru zachovaj:

```bash
docker inspect payments-api > incident-inspect.json
docker logs --timestamps payments-api > incident.log 2>&1
docker diff payments-api > incident-filesystem-diff.txt
```

Recreate môže odstrániť pôvodný namespace, PID, writable layer a network endpoint a tým zničiť root-cause evidence.

## 16. Docker Desktop

Docker Desktop na Windows a macOS poskytuje Docker API a UX, ale Linux containers typicky bežia vo vnútornej Linux VM. Host filesystem mounts, networking a resource limity preto prechádzajú ďalšou virtualizačnou vrstvou.

```text
Windows/macOS host
→ Docker Desktop backend
→ Linux VM
→ dockerd/containerd/runtime
→ Linux container
```

Path performance, file permissions, localhost routing a available memory sa môžu líšiť od native Linux Engine-u. Tvrdenie „funguje to v Dockeri na notebooku“ preto nepreukazuje identické host kernel a filesystem semantics v produkcii.

## 17. Rootful a rootless Engine

Rootful Engine má broad host authority potrebnú na namespaces, mounts, networks a devices. Rootless mode spúšťa daemon a containers bez host root privileges pomocou user namespaces a userspace alebo obmedzených networking mechanizmov.

Rootless znižuje dopad daemon alebo runtime compromise, ale nie je plne transparentný. Low ports, cgroups, overlay networking, devices a storage drivers môžu mať odlišné možnosti podľa host konfigurácie.

Pri troubleshooting-u vždy zaznamenaj, či client komunikuje s rootful alebo rootless daemonom a aký context používa.

## 18. Incident: príkaz odstránil nesprávne production containers

Operator chcel vyčistiť lokálny test daemon. Jeho active Docker context však smeroval cez SSH na production node. Príkaz:

```bash
docker container prune -f
```

odstránil zastavené production incident containers, ktoré obsahovali filesystem a log evidence.

CLI fungoval správne a daemon vykonal autorizovanú požiadavku. Chyba bola v context identity a destructive-operation gate.

Oprava zaviedla výrazné context names, shell prompt s active contextom, production read-only access pre bežných operatorov a wrapper, ktorý pred prune vyžaduje explicitný daemon hostname a resource manifest.

## 19. Incident: restart nezaviedol nový image

Pipeline pushla `payments-api:1.0.1`. Operator na hoste vykonal:

```bash
docker pull atlas/payments-api:1.0.1
docker restart payments-api
```

Container po restarte stále používal starý image ID, pretože restart nemení container create configuration. `docker inspect payments-api --format '{{.Image}}'` ukázal starý digest.

Recovery vytvorila nový container z nového digestu a pripojila rovnaký volume. Automation prešla na Compose `up` alebo orchestrator rollout, ktorý porovná desired image a vytvorí novú generation.

## 20. Systematický Docker troubleshooting

Pri všeobecnom symptóme „Docker command zlyhal“ postupuj v poradí:

```text
CLI syntax a local config
→ active context a transport
→ Engine API availability a version
→ daemon authorization
→ image resolution a local store
→ container create configuration
→ storage a network preparation
→ containerd/runtime create
→ process start a exit
→ health a application path
```

Základný evidence set:

```bash
docker context show
docker version
docker info
docker image inspect IMAGE
docker inspect CONTAINER
docker logs --timestamps CONTAINER
docker events --since 30m
```

Na hoste doplň daemon a kernel logs. Najprv zisti, či zlyhal request, object mutation, process create alebo application outcome. Až potom rozhoduj o retry, restart, recreate, daemon remediation alebo host replacement.

## Čo si z kapitoly odniesť

Docker CLI je klient Docker Engine API. `dockerd` spravuje higher-level Docker objects a používa containerd a OCI runtime pre nižší process lifecycle. Image pull, container create, start, health, stop, restart a delete sú odlišné transitions.

Container object môže existovať bez procesu. API success nie je readiness. Restart používa rovnakú config generation, zatiaľ čo recreate vytvára nový object. Docker context určuje, ktorý daemon príkaz mení, a access k daemonu je privilegovaná boundary. Pri troubleshooting-u sleduj request cez jednotlivé vrstvy namiesto všeobecného „Docker nefunguje“.

## Primárne zdroje

- [Docker Engine overview](https://docs.docker.com/engine/)
- [Docker architecture overview](https://docs.docker.com/get-started/docker-overview/)
- [Docker contexts](https://docs.docker.com/engine/manage-resources/contexts/)
- [Docker Engine API](https://docs.docker.com/reference/api/engine/)
- [Rootless mode](https://docs.docker.com/engine/security/rootless/)
- [containerd](https://containerd.io/)
- [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Container security](container-security.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Dockerfile →](dockerfile.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
