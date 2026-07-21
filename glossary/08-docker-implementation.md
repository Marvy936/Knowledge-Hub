# Docker implementation glossary entries

## Anonymous volume — Docker

Docker-managed volume bez user-defined mena, vytvorené pre konkrétny mount request a schopné prežiť zmazanie containeru; bez explicitného ownershipu a cleanup policy ľahko vzniká orphan state. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## API version negotiation — Docker

Mechanizmus, ktorým Docker client a Engine vyberú spoločnú podporovanú verziu Engine API; neznamená, že starší server podporuje všetky features novšieho CLI. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Base image — Dockerfile

Image reference použitá instruction `FROM` ako počiatočný filesystem a metadata graph build stage-u; je supply-chain a patch-lifecycle dependency. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Build bind mount — Dockerfile

Dočasný bind mount dostupný iba počas `RUN --mount=type=bind`, ktorý sprístupní build context, stage alebo named context bez automatického uloženia mount contentu do výslednej layer. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Build cache — Docker

Znovupoužiteľné výsledky build graph nodes alebo instructions identifikované cache keys a relevantnými inputs, určené na zrýchlenie build-u, nie ako jediný correctness source. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Build context — Docker

Explicitná množina files, directories a metadata dostupná builderu ako source pre `COPY`, `ADD` alebo build mounts; context root nemusí byť directory Dockerfile-u. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Build secret — Dockerfile

Citlivý build-time input sprístupnený cez BuildKit secret mount bez zámerného uloženia do image layer alebo build argumentu; command ho stále nesmie zapísať do outputu, cache alebo logs. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Build stage — Dockerfile

Samostatný build filesystem a graph scope vytvorený instruction `FROM`, ktorý môže slúžiť na kompiláciu, testovanie, export artifacts alebo zostavenie final image-u. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Cache invalidation — Docker build

Stav, keď zmena instruction, parent resultu alebo relevantného inputu zmení cache key a builder musí príslušný graph node znovu vykonať. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Cache mount — Dockerfile

Persistentnejší pomocný directory pripojený počas `RUN --mount=type=cache`, napríklad pre compiler alebo package-manager cache; môže byť odstránený a nesmie ovplyvňovať correctness build-u. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Clean-room build

Build vykonaný bez dôvery v existujúcu local alebo external cache, používaný na overenie reproducibility, úplnosti dependencies a absencie skrytých cache assumptions. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## containerd — Docker Engine

Container lifecycle a image/snapshot komponent používaný Docker Engine-om na koordináciu tasks, runtime shims, content a snapshots podľa konkrétnej konfigurácie platformy. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Context root — Docker build

Root path build contextu, voči ktorému sa vyhodnocujú local source paths v `COPY` a `ADD`, nezávisle od umiestnenia Dockerfile-u. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Development target — Dockerfile

Multi-stage build target obsahujúci development-only tools, debugger, hot reload alebo source-mount contract, ktorý nesmie byť neúmyselne publikovaný ako production runtime image. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Distroless image

Minimalizovaný runtime image bez bežného shellu alebo package managera, určený na spustenie konkrétnej aplikácie s menším mutable surface; vyžaduje external observability a premyslený debugging model. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Docker bind mount

Runtime mount konkrétneho host filesystem pathu do container mount namespace-u, ktorý prenáša host path, permissions, labels a lifecycle coupling. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Docker CLI

Client program `docker`, ktorý parsuje príkazy a komunikuje s Docker Engine API; container primitives typicky nevytvára priamo. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker context

Pomenovaný client-side connection profil určujúci Docker daemon endpoint, TLS/SSH metadata a ďalšie connection nastavenia; nesprávny context môže nasmerovať deštruktívny príkaz na iný host. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker daemon — `dockerd`

Dlhodobo bežiaci server Docker Engine-u spravujúci images, containers, networks, volumes, builds a komunikáciu s nižšími runtime components. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker Desktop

Desktop platforma zahŕňajúca Docker Engine, CLI, UI, build, credential, networking a virtualizačné komponenty; na Windows a macOS typicky používa Linux virtualizačnú vrstvu pre Linux containers. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker embedded DNS

DNS service poskytovaná Docker Engine-om pre name resolution containers a aliases v user-defined networks. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker Engine

Client-server container platforma pozostávajúca z daemon-u, API a súvisiacich components na správu Docker objects a container lifecycle. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker Engine API

Versionované HTTP API, cez ktoré clients a integrations riadia Docker daemon; prístup k nemu je privilegovaná platformová capability. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker host network

Network mode, v ktorom container process zdieľa host network namespace, binduje priamo host ports a nemá bežnú samostatnú container network isolation. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker internal network

Docker network deklarovaná tak, aby obmedzila bežný external routing/egress podľa driver capabilities, používaná na užšie backend communication boundaries. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker network

Pomenovaný runtime connectivity object s konkrétnym driverom, IPAM a isolation/discovery semantics pre pripojené containers. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker network alias

Dodatočné logical DNS meno container endpointu platné v konkrétnej Docker network boundary. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker none network

Runtime network mode poskytujúci containeru minimálny network namespace bez bežnej external connectivity, typicky iba s loopback interfaceom. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker object

Daemon-managed objekt ako image, container, network alebo volume s vlastnou identity a lifecycle semantics. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker port publishing

Runtime forwarding alebo routing konfigurácia mapujúca host address a port na port v container network namespace; je odlišná od Dockerfile `EXPOSE`. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker socket

Local Unix socket alebo obdobný endpoint poskytujúci prístup k Docker Engine API; write access je často prakticky host-administration capability. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker volume

Docker-managed storage object s lifecycle oddeleným od konkrétnej container instance; persistence neznamená automatický backup, replication ani multi-host durability. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Dockerfile

Versionovaný build program obsahujúci instructions, z ktorých builder vytvorí image filesystem layers a runtime metadata. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Dockerfile frontend

Parser a build frontend implementujúci Dockerfile syntax a prekladajúci instructions do BuildKit build graphu, často vybraný cez `# syntax=` directive. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## External build cache

Build cache exportovaná mimo lokálneho buildera, napríklad do registry alebo CI backendu, s vlastnou access, trust, namespace a retention policy. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Final stage — Dockerfile

Stage, ktorého filesystem a image config tvoria publikovaný runtime image; má obsahovať iba potrebné runtime artifacts a dependencies. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Host bind address — Docker

Host IP adresa, na ktorej Docker publikuje port, napríklad `127.0.0.1` pre local-only alebo `0.0.0.0` pre všetky IPv4 interfaces. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Image runtime metadata — Dockerfile

Image configuration fields ako default command, entrypoint, environment, user, working directory, exposed ports, labels a stop signal použité pri vytváraní runtime containeru. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Mount obscuring — container

Runtime efekt, pri ktorom volume alebo bind mount pripojený na path prekryje files existujúce na rovnakom path-e v image filesysteme. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Multi-stage build

Dockerfile build s viacerými `FROM` stages, ktorý oddeľuje compilation, test, artifact a runtime filesystemy a umožňuje kopírovať do final image-u iba explicitné artifacts. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Named context — Docker build

Dodatočný explicitne pomenovaný build context dostupný Dockerfile-u podobne ako stage, používaný na užšie oddelenie source alebo external image inputs. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Named volume — Docker

Docker volume s explicitným user-defined menom a samostatným lifecycle, vhodné na auditovateľnejší persistence a cleanup workflow. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Narrow artifact copy — Dockerfile

Princíp kopírovania iba presne potrebných build outputs z build stage do final stage namiesto širokého prenosu celého stage filesystemu. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Network driver — Docker

Implementácia Docker network connectivity modelu, napríklad bridge, host, none, overlay, macvlan alebo ipvlan. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## OCI runtime — Docker

Low-level runtime implementujúci OCI Runtime Specification a vytvárajúci container process, namespaces, mounts a security/resource controls z runtime bundle-u. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Orphan volume — Docker

Volume, ktoré už nemá aktívneho workload ownera alebo referenciu, ale stále obsahuje dáta a spotrebúva storage; pred odstránením potrebuje ownership a retention overenie. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Rootless Docker

Docker daemon a containers spustené bez host root identity s user-namespace a userspace mechanizmami, znižujúce niektoré host privilege riziká za cenu feature a networking obmedzení. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Runtime shim — containerd

Per-container alebo per-runtime lifecycle proces oddeľujúci container process od containerd daemon lifecycle a poskytujúci task I/O a exit-state coordination. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Scratch image

Minimalistický Dockerfile stage `FROM scratch` bez base filesystemu, vhodný iba pre artifact s kompletne vyriešenými runtime dependencies. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Test stage — Dockerfile

Multi-stage build target určený na vykonanie testov; ak nie je v dependency graph-e final targetu, pipeline ho musí explicitne buildnúť ako quality evidence. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## tmpfs mount — Docker

Memory-backed runtime filesystem mount s ephemeral lifecycle, vhodný pre dočasné dáta alebo secrets podľa memory, swap a forensic threat modelu. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## User-defined bridge — Docker

Explicitne vytvorená single-host bridge network poskytujúca vlastnú lifecycle identity, embedded DNS, aliases a isolation boundary pre pripojené containers. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Volume driver — Docker

Plugin alebo built-in implementation určujúca storage backend a mount semantics Docker volume-u; application consistency, backup a access modes zostávajú samostatným contractom. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## `.dockerignore`

Pattern file filtrujúci content zahrnutý do Docker build contextu; znižuje transfer, cache invalidation a accidental exposure, ale nie je secret manager ani náhrada za odstránenie secrets z repository history. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).
