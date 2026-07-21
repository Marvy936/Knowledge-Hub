# Docker runtime, Compose, BuildKit and troubleshooting glossary entries

## Build attestation

Machine-readable statement viazaný na build output digest, napríklad provenance alebo SBOM, používaný na overenie source, build procesu a supply-chain policy. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Build driver — Buildx

Konfigurácia určujúca, kde a ako beží BuildKit backend, napríklad `docker`, `docker-container`, Kubernetes alebo remote driver. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Build exporter — BuildKit

Komponent určujúci výsledný output build-u, napríklad registry image, local Docker image store, OCI artifact, tar alebo local filesystem. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Build frontend — BuildKit

Parser a translator, ktorý premieňa Dockerfile alebo iný build language na interný BuildKit graph. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Builder instance — Buildx

Logical Buildx objekt združujúci jeden alebo viac BuildKit nodes, driver, endpoints, podporované platforms a configuration. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Builder node — Buildx

Jedna execution jednotka v builder instance, ktorá poskytuje BuildKit worker capabilities a konkrétne podporované target platforms. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Builder trust domain

Izolovaná bezpečnostná oblasť pre build workloads, cache a credentials; untrusted pull-request buildy nemajú zdieľať release signing alebo production registry oprávnenia. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## BuildKit

Moderný container build backend vykonávajúci dependency graph, content-aware cache, build mounts, exporters, multi-platform outputs a attestations. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Buildx

Docker CLI plugin na správu BuildKit builders a pokročilých build workflows vrátane multi-platform builds, external cache a output exporters. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Compose include

Mechanizmus importu ďalšieho Compose application modelu; celý transitive source a jeho privileged mounts, images, networks a commands musia byť auditované. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose interpolation

Nahrádzanie `${VARIABLE}` výrazov pri zostavovaní resolved Compose modelu; nie je totožné s environmentom odovzdaným procesu v containeri. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md) a [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose merge

Pravidlá kombinovania viacerých Compose files, pri ktorých mappings, sequences a špeciálne fields ako `command`, `entrypoint` alebo `healthcheck.test` môžu mať odlišné merge semantics. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose profile

Pomenovaná podmienka aktivujúca optional services, napríklad development alebo debug tooling, bez zmeny core application modelu. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose project

Logical application scope, ktorým Docker Compose zoskupuje services, containers, networks, volumes a labels pod spoločnú project identity. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose service

Deklaratívna definícia workloadu v Compose modeli, z ktorej môže vzniknúť jedna alebo viac runtime container inštancií. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose Specification

Otvorený application-model specification pre multi-container services, networks, volumes, configs, secrets a súvisiace lifecycle metadata. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose trust model

Bezpečnostný model, podľa ktorého je Compose file privilegovaná executable configuration schopná spúšťať containers, mountovať host paths, pripájať devices a publikovať ports. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Configuration recreate — container

Nahradenie container instance po zmene runtime environment alebo inej immutable container configuration, pretože už spustený process bežne neprevezme nové hodnoty automaticky. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Container environment

Sada environment variables dostupná runtime procesu po zlúčení image defaults a runtime overrides. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Container exit code

Numerický status ukončenia PID 1 procesu; musí sa interpretovať spolu so signalom, OOM stavom, daemon/kernel logs a application contractom. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Container drift

Nezdokumentovaná runtime zmena vo writable layeri alebo container configuration, ktorá nie je súčasťou versionovaného image-u alebo deployment modelu a zanikne alebo sa zmení pri recreate. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Controlled reproduction — Docker

Diagnostický postup používajúci pinned image digest, rovnakú platformu a explicitnú runtime configuration, pričom sa mení iba jedna premenná a zachováva evidence. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Cross-compilation — container build

Vytváranie binary pre target platform odlišnú od build host platformy pomocou toolchainu a automatic platform arguments ako `TARGETOS` a `TARGETARCH`. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Daemon log — Docker

Log Docker daemon-u a súvisiacich runtime components používaný na diagnostiku startupu, API, storage, networking a container lifecycle failures. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker diagnostic baseline

Minimálna sada evidence zahŕňajúca versions, context, `docker info`, container state, inspect, logs, events, resource usage a disk stav pred deštruktívnym zásahom. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker event

Časovo zoradená runtime udalosť Docker daemon-u, napríklad create, start, die, health status, network connect alebo image pull, použitá na incident koreláciu. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Docker healthcheck

Periodický command definovaný image-om alebo runtime modelom, ktorého exit status určuje health state bežiaceho containeru. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Docker health history

Obmedzený záznam posledných healthcheck executions, exit statuses a outputu dostupný cez container inspection. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Docker health status

Runtime stav `starting`, `healthy` alebo `unhealthy` odvodený z healthchecku a oddelený od process state `running` alebo `exited`. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Docker disk usage

Storage spotrebovaný images, writable layers, volumes, build cache, logs a runtime content stores, analyzovaný napríklad cez `docker system df`. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Emulation — multi-platform build

Spustenie target-architecture build binaries cez emulačnú vrstvu, napríklad QEMU, na hoste s odlišnou architecture; nenahrádza úplný native runtime test. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Environment precedence — Docker

Pravidlá určujúce výslednú environment hodnotu pri kombinácii CLI overrides, Compose `environment`, `env_file`, image `ENV` a application defaults. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Evidence preservation — Docker incident

Zachovanie inspect dát, logs, events, versions, image digestov, resource a host evidence pred restartom, delete alebo prune operáciou. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## External resource — Compose

Network, volume, config alebo secret deklarovaný ako vlastnený mimo aktuálneho Compose projektu; Compose ho používa, ale nemá automaticky riadiť jeho celý lifecycle. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Health start period

Warm-up interval healthchecku, počas ktorého startup failures nemusia prispievať k označeniu containeru za unhealthy podľa health configuration. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Inode exhaustion

Stav, keď filesystem nemôže vytvárať ďalšie files napriek voľnej byte capacity, čo môže narušiť image pull, logs, snapshots alebo container writes. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Kubernetes builder driver — Buildx

Buildx driver prevádzkujúci BuildKit workers v Kubernetes, s cluster schedulingom, resource controls a možnosťou native multi-architecture nodes. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Liveness

Schopnosť procesu pokračovať v užitočnej práci bez potreby restartu; nie je automaticky totožná s readiness alebo external availability. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## LLB — BuildKit

Low-Level Build graph representation používaná BuildKitom na opis operations, dependencies, mounts, cache keys a execution flow prekladom z frontendu. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Multi-platform build

Jeden build workflow produkujúci platform-specific manifests a typicky spoločný image index pre viac OS/architecture kombinácií. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Native builder

Builder node vykonávajúci build priamo na rovnakej architecture ako target bez user-mode emulation. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## OOMKilled — Docker

Container state signal indikujúci, že process bol ukončený v súvislosti s out-of-memory mechanizmom; root cause treba potvrdiť cgroup a kernel evidence. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## One-shot service — Compose

Service určená na jednorazové úspešné dokončenie úlohy, napríklad migration, ktorú môže dependency vyžadovať cez `service_completed_successfully`. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Orphan container — Compose

Container patriaci Compose projektu, ktorého service už nie je prítomná v aktuálnom resolved modeli. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Platform mismatch — container image

Nesúlad medzi target OS/architecture a vybraným image manifestom alebo executable, ktorý môže viesť k pull failure alebo `exec format error`. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Project name — Compose

Stabilná identity Compose projektu ovplyvňujúca názvy a scope containers, networks, volumes a lifecycle commandov. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Readiness

Stav, v ktorom má workload prijímať traffic alebo prácu; process môže byť live, ale ešte nemusí byť ready. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Remote builder — Buildx

BuildKit daemon spravovaný mimo lokálneho Docker Engine-u, ku ktorému sa Buildx pripája cez explicitný remote endpoint a trust model. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## Required configuration

Runtime configuration field, bez ktorého application nemôže bezpečne začať a má zlyhať s redigovanou validačnou chybou. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Resolved Compose model

Výsledná configuration po interpolation, merge, profiles, includes a overrides, ktorú možno kontrolovať cez `docker compose config`. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Resolved runtime configuration — Docker

Skutočná configuration vytvoreného containeru vrátane image, commandu, environmentu, mounts, networks, limits a security options dostupná cez inspection. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Restart loop — container

Opakovaný crash a automatický restart containeru podľa restart policy alebo external controllera, ktorý potrebuje koreláciu exit code, logs, events a dependencies. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Runtime configuration — container

Configuration dodaná pri vytvorení containeru, napríklad environment, command, mounts, ports, resources a security options, oddelená od immutable image artifactu. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Runtime dependency failure

Zlyhanie knižnice, dynamic linkeru, interpreteru, certificate store alebo iného runtime componentu, ktoré môže vyzerať ako chýbajúci executable napriek existencii file-u. Pozri [Docker troubleshooting](docs/08-container-fundamentals-and-docker/docker-troubleshooting.md).

## Startup health

Schopnosť workloadu dokončiť inicializáciu v očakávanom čase; je odlišná od dlhodobej liveness a readiness. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## `--load` — Buildx

Build exporter skratka importujúca vhodný build output do local Docker image store-u, typicky pre single-platform local workflow. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).

## `--push` — Buildx

Build exporter skratka publikujúca image alebo multi-platform index priamo do registry. Pozri [BuildKit a Buildx](docs/08-container-fundamentals-and-docker/buildkit-buildx.md).
