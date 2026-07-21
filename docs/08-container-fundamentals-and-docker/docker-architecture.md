# Docker architecture

Docker je konkrétna container platforma postavená nad Linux kernel primitives, OCI artifacts a runtime components. Pri diagnostike je dôležité rozlišovať klienta, API, daemon, image store, container lifecycle manager a low-level runtime. Príkaz `docker run` nie je jedna lokálna operácia; je to požiadavka od klienta cez API na privilegovaný backend, ktorý pripraví filesystem, networking, cgroups, namespaces a proces.

## 1. Client-server model

Docker Engine pozostáva najmä z:

- Docker CLI klienta `docker`,
- Docker Engine API,
- dlhodobo bežiaceho daemon procesu `dockerd`,
- image a snapshot storage vrstvy,
- network a volume drivers,
- containerd a OCI runtime vrstvy.

CLI a daemon môžu bežať na rovnakom hoste alebo na odlišných systémoch. Klient preto nie je bezpečnostná hranica; rozhodujúce je, ku ktorému daemon endpointu je pripojený a aké oprávnenia nad ním má.

```text
Docker CLI
   ↓ Engine API
 dockerd
   ├─ images a registry komunikácia
   ├─ networks a volumes
   ├─ build orchestration
   └─ containerd
        └─ runtime shim
             └─ OCI runtime
                  └─ container process
```

## 2. Docker CLI

CLI:

- parsuje príkazové argumenty,
- načíta Docker context a environment,
- vyberie daemon endpoint,
- odošle API request,
- zobrazí response a streamované logs/events.

CLI typicky nevytvára namespaces ani nespúšťa workload process priamo.

Dôležité diagnostické príkazy:

```bash
docker version
docker info
docker context ls
docker context show
docker system info
```

`docker version` odlišuje client a server verziu. Funkčný lokálny CLI ešte neznamená dostupný alebo kompatibilný daemon.

## 3. Docker contexts

Docker context viaže klienta na konkrétny endpoint a connection metadata.

```bash
docker context ls
docker context use production
```

Riziko:

- operator očakáva lokálny daemon,
- context však ukazuje na remote production host,
- bežný `docker rm`, `prune` alebo `compose down` zasiahne produkciu.

Pred deštruktívnou operáciou over:

```bash
docker context show
docker info --format '{{.Name}}'
```

## 4. Docker daemon

`dockerd` spravuje Docker objects:

- images,
- containers,
- networks,
- volumes,
- build requests,
- registry pull/push,
- events a logs podľa drivera.

Daemon je vysokoprivilegovaná trust boundary. Prístup k Docker socketu je často prakticky ekvivalentný možnosti získať host root oprávnenia, pretože klient môže vytvoriť privileged container alebo mountnúť host filesystem.

## 5. Engine API

Docker Engine API je versionované HTTP API. Môže byť dostupné cez:

- Unix socket,
- Windows named pipe,
- TCP endpoint,
- SSH-backed Docker context.

Linux default býva:

```text
/var/run/docker.sock
```

Bezpečnostné pravidlá:

- socket nemountuj do bežných application containers,
- TCP API nevystavuj bez silnej autentifikácie a TLS,
- používaj least privilege proxy iba pri presne definovanom read-only use case,
- audituj identities a commands,
- oddel build daemon od production runtime tam, kde to znižuje blast radius.

## 6. containerd

Docker Engine používa containerd na správu container lifecycle a image/snapshot operácií podľa konfigurácie platformy.

containerd typicky koordinuje:

- image content a snapshots,
- create/start/stop/delete lifecycle,
- runtime výber,
- shims pre dlhodobejšiu správu container procesu,
- task state a exit status.

`dockerd` a containerd majú odlišné responsibilities. Zlyhanie Docker CLI alebo daemon UI vrstvy nemusí automaticky znamenať, že už spustený container process okamžite skončí.

## 7. OCI runtime a `runc`

Low-level OCI runtime dostane runtime bundle a vytvorí container process podľa OCI Runtime Specification.

Typická úloha runtime:

1. nastaví namespaces,
2. pripojí root filesystem a mounts,
3. aplikuje cgroups a resource constraints,
4. nastaví capabilities, seccomp a ďalšie security controls,
5. pripraví user, environment a working directory,
6. spustí entry process.

`runc` je bežný OCI runtime, ale Docker môže byť nakonfigurovaný aj s alternatívnymi runtimes.

## 8. Container lifecycle

Zjednodušený `docker run` flow:

1. CLI odošle create request.
2. Daemon overí image reference a prípadne vykoná pull.
3. Pripraví container metadata a writable snapshot.
4. Vytvorí network endpoint a mounty.
5. containerd vytvorí runtime task.
6. OCI runtime spustí PID 1 procesu.
7. Daemon streamuje status, logs a events podľa požiadavky klienta.

`docker run` je prakticky kombinácia `docker create` a `docker start`.

## 9. Images, containers, networks a volumes

### Image

Immutable alebo content-addressed build artifact obsahujúci layers a runtime config.

### Container

Runtime inštancia image s vlastnou writable layer, process lifecycle a runtime configuration.

### Network

Runtime connectivity object spravovaný network driverom.

### Volume

Persistentnejší storage object s lifecycle oddeleným od konkrétneho containeru.

Tieto objects majú odlišné identity. Zmazanie containeru nemusí zmazať image, volume ani network.

## 10. Docker Desktop

Docker Desktop na Windows a macOS typicky prevádzkuje Linux Docker Engine vo virtualizačnej vrstve alebo Linux VM. Preto:

- daemon nemusí bežať priamo v host OS kernel priestore,
- bind mounts prechádzajú file-sharing vrstvou,
- `localhost`, networking a filesystem performance môžu mať platform-specific behavior,
- Linux container vidí Linux kernel virtuálneho prostredia, nie Windows alebo macOS kernel.

Docker Desktop nie je synonymom pre Docker Engine. Zahŕňa ďalšie UI, VM, networking, update a credential komponenty.

## 11. Rootful a rootless mode

### Rootful daemon

Tradičný daemon má vysoké host privileges. Poskytuje širokú kompatibilitu, ale kompromitácia daemonu alebo socketu má veľký blast radius.

### Rootless mode

Daemon a containers bežia bez host root identity s využitím user namespaces a userspace/networking mechanizmov podľa platformy.

Rootless znižuje dopad niektorých útokov, ale:

- nie je úplnou sandbox boundary,
- má feature a networking obmedzenia,
- host kernel vulnerabilities zostávajú relevantné,
- workload môže mať stále citlivé user-level dáta a credentials.

## 12. Daemon configuration

Daemon sa konfiguruje cez command-line flags alebo `daemon.json`.

Typické oblasti:

- listen endpoints,
- storage a logging drivers,
- registry mirrors a insecure registries,
- default address pools,
- runtimes,
- live restore,
- authorization plugins,
- cgroup a resource defaults,
- containerd image store features.

Configuration change môže vyžadovať daemon restart. Pred zmenou over:

1. schema a podporu aktuálnej verzie,
2. syntax JSON,
3. restart dopad,
4. rollback config,
5. stav spustených containers.

## 13. Events a observability

Docker poskytuje runtime events:

```bash
docker events
```

Užitočné sú aj:

```bash
docker ps -a
docker inspect <container>
docker logs <container>
docker stats
docker system df
docker info
```

Host-level diagnostika zahŕňa:

- daemon service logs,
- containerd logs,
- kernel OOM a audit events,
- filesystem capacity/inodes,
- network rules a conntrack,
- cgroup pressure a throttling.

Docker CLI output je iba jedna vrstva dôkazov.

## 14. Version compatibility

Client a daemon môžu mať odlišné verzie. API negotiation môže umožniť kompatibilnú komunikáciu, ale novšie CLI features nemusia byť podporované starším serverom.

Pri probléme zaznamenaj:

```bash
docker version
docker info
```

A odlišuj:

- CLI version,
- Engine API version,
- daemon version,
- containerd version,
- OCI runtime version,
- Docker Desktop version.

## 15. Failure boundaries

### CLI zlyhá

Request nemusel byť odoslaný alebo response sa nemusela zobraziť. Over server state.

### Daemon zlyhá

Nové management operácie nefungujú. Dopad na existujúce containers závisí od runtime a daemon configuration.

### containerd/runtime zlyhá

Môže byť narušený task lifecycle, exit reporting alebo vytváranie nových processes.

### Registry je nedostupná

Existujúci lokálny image môže stále fungovať, ale pull alebo update zlyhá.

### Storage je plný

Pull, build, logovanie, snapshot creation alebo container writes môžu zlyhať rôznymi spôsobmi.

## 16. Security model

Chráň najmä:

- Docker socket a remote API,
- daemon host,
- registry credentials,
- build secrets,
- runtime identities,
- host mounts a devices,
- logging a audit data,
- plugin a runtime supply chain.

Daemon access nie je bežné application permission. Patrí do privilegovaného platformového workflowu.

## 17. Anti-patterny

### Mount Docker socketu do CI alebo application containeru bez obmedzenia

Compromise containeru môže znamenať compromise hosta.

### Predpoklad, že CLI command vykonal operáciu lokálne

Aktívny context môže smerovať na iný daemon.

### Používanie TCP API bez TLS

Ktokoľvek s network accessom môže ovládať daemon.

### Ručné mazanie obsahu z Docker data rootu

Obíde metadata a môže poškodiť content/snapshot state.

### Miešanie production runtime a nedôveryhodných builds na jednom daemon hoste

Build context a build steps rozširujú attack surface.

### Diagnostika iba cez `docker ps`

Nevidí kernel, storage, daemon ani network príčinu.

## 18. Troubleshooting

### `Cannot connect to the Docker daemon`

Over:

- aktívny context,
- endpoint path,
- daemon service,
- socket permissions,
- SSH/TLS connection,
- Docker Desktop VM stav.

### Client je novší než server

Skontroluj API compatibility a nepoužívaj serverom nepodporovanú feature.

### Container je running, ale application nefunguje

`running` znamená, že PID 1 žije. Over health, logs, listen address, dependencies a application readiness.

### Daemon nevie vytvoriť container

Over image/platform compatibility, mounts, network allocation, cgroup support, seccomp/LSM denial, disk/inode capacity a runtime logs.

### Docker disk usage nesedí

Porovnaj images, containers, local volumes, build cache a containerd content/snapshots. Nepoužívaj `prune` bez pochopenia retention dopadu.

## 19. Kontrolné otázky

1. Aký je rozdiel medzi Docker CLI a daemon-om?
2. Prečo je Docker socket privilegovaná trust boundary?
3. Akú úlohu má containerd?
4. Akú úlohu má OCI runtime?
5. Čo sa približne deje pri `docker run`?
6. Ako sa líši image, container, network a volume lifecycle?
7. Prečo môže Docker context spôsobiť nebezpečný operator error?
8. Ako sa Docker Desktop líši od samotného Docker Engine?
9. Čo rootless mode rieši a čo nerieši?
10. Ktoré vrstvy treba skontrolovať pri zlyhaní container create operácie?

## Glossary impact

Relevantné pojmy: Docker Engine, Docker CLI, Docker daemon, Engine API, Docker context, Docker socket, containerd, runtime shim, OCI runtime, `runc`, Docker object, daemon data root, rootless Docker a API version negotiation.

## Oficiálna dokumentácia

- [Docker Engine](https://docs.docker.com/engine/)
- [Docker overview and architecture](https://docs.docker.com/get-started/docker-overview/)
- [Alternative container runtimes](https://docs.docker.com/engine/daemon/alternative-runtimes/)
- [Docker daemon configuration](https://docs.docker.com/engine/daemon/)
