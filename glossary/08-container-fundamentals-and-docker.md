# Container Fundamentals and Docker glossary entries

## Application-consistent backup

Backup vytvorený po koordinácii s aplikáciou alebo databázou tak, aby zachytené dáta tvorili logicky konzistentný recovery point, nie iba náhodný filesystem okamih. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Bind mount — container

Sprístupnenie existujúceho host filesystem pathu do container mount namespace-u, ktoré vytvára silnú väzbu na host path, permissions, labels a lifecycle. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Capability drop — container

Runtime policy odstraňujúca Linux capabilities z process credential sets, ideálne s defaultom drop-all a explicitným pridaním iba nevyhnutných oprávnení. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Cgroup OOM — container

Ukončenie procesu v dôsledku prekročenia alebo nezvládnutia memory pressure v jeho cgroup boundary, ktoré nemusí znamenať vyčerpanie celej host memory. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Cgroup v2

Unified Linux control-group hierarchy organizujúca procesy a aplikujúca resource accounting, limits a distribution cez controllers ako CPU, memory, I/O a PIDs. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Conntrack — container networking

Kernel connection-tracking state používaný firewallom a NAT-om; jeho vyčerpanie alebo nevhodné timeouts môžu spôsobovať dropped nové spojenia medzi containers a externými sieťami. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container

Izolovaný runtime process alebo skupina procesov používajúca host kernel a oddelený pohľad na resources cez namespaces, cgroups a ďalšie security controls. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Container bridge network

Network model, v ktorom host-side konce veth pairs pripájajú container network namespaces k Linux bridge-u a následne k host routing, firewall alebo NAT vrstve. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container escape

Prelomenie container isolation boundary, pri ktorom process získa access k hostu alebo iným workloads. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Container image

Versionovaný a typicky content-addressed filesystem a runtime-metadata artifact používaný na vytvorenie container instance; bežne neobsahuje kernel použitý pri runtime. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md) a [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Container MTU

Maximum Transmission Unit platná na container interface a jeho packet path-e; nesúlad s bridge, tunnel alebo host uplinkom môže spôsobovať partial connectivity a dropped veľké packets. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container network namespace

Linux network namespace poskytujúci container procesu vlastné interfaces, IP adresy, routes, sockets, loopback a network state view. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container port

Port, na ktorom process počúva vo svojom network namespace; nemusí byť dostupný z hosta alebo externej siete bez routing alebo port-publishing konfigurácie. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container runtime

Software vrstva pripravujúca container filesystem, namespaces, cgroups, process a lifecycle podľa runtime configuration alebo štandardu. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Container security baseline

Minimálna kombinácia controls, napríklad trusted digest, non-root user, capability drop, seccomp, LSM policy, read-only root filesystem, resource limits, network segmentation a short-lived identity. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Container volume

Runtime-managed storage object s lifecycle oddeleným od konkrétnej container instance, ktorý môže poskytovať persistence, ale nie automaticky backup, replication alebo multi-host durability. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Copy-on-write — container filesystem

Filesystem model, pri ktorom read-only image layer content zostáva zdieľaný a prvá zmena vytvorí novšiu kópiu alebo záznam vo writable upper layeri. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Copy-up

Operácia, pri ktorej sa file z read-only lower layeru pri prvom zápise prenesie do writable upper layeru a ďalšie zmeny sa vykonávajú nad touto kópiou. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Crash-consistent snapshot

Storage snapshot zodpovedajúci stavu po náhlom výpadku napájania bez garancie, že application buffers, transactions alebo koordinované multi-volume dáta boli konzistentne uzavreté. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Descriptor — OCI

Štruktúra identifikujúca OCI content pomocou media type, digestu a size, prípadne ďalších annotations alebo platform metadata. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Diff ID — OCI image

Digest uncompressed filesystem layer changesetu uložený v OCI image configuration rootfs chain, odlišný od digestu compressed blobu prenášaného cez registry. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Distribution digest — OCI

Content digest registry blobu alebo manifestu v jeho distribuovanej reprezentácii, používaný na integrity verification a immutable references. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## East-west traffic

Network traffic medzi internými workloads alebo services v rámci platformy, ktorého nekontrolovaný default-allow model zvyšuje lateral-movement risk. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Ephemeral runtime instance

Nahraditeľná runtime inštancia, ktorej lokálny procesový a writable-layer stav nie je považovaný za jediný persistentný zdroj dát. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Garbage collection — registry

Proces odstraňovania manifestov alebo blobs, ktoré už nie sú reachable z retained references, vykonávaný s koordináciou voči pushes, deletes, referrers a retention policy. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Guest operating system

Operačný systém bežiaci vo virtual machine nad virtualizovaným hardware a vlastným guest kernelom. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Host network mode

Container runtime mode zdieľajúci host network namespace, čím odstraňuje bežnú container network izoláciu a vytvára priame host port, interface a traffic exposure. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Host port — container

Port a bind address v host network namespace, ktorý forwarding alebo proxy mechanizmus mapuje na container port. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Hypervisor

Virtualization vrstva poskytujúca virtual hardware a izoláciu pre virtual machines. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Image configuration — OCI

OCI JSON artifact obsahujúci platform, runtime defaults, environment, entrypoint/command, user, rootfs diff IDs a build history metadata image-u. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Image index — OCI

Manifest list odkazujúci na viac OCI manifests, typicky pre rozdielne OS, architecture a variant platformy. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Image layer

Immutable filesystem changeset v ordered image graph-e, ktorý sa skladá s ostatnými layers do výsledného root filesystemu. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Image manifest — OCI

OCI artifact odkazujúci descriptorom na jednu image configuration a ordered list filesystem layer blobs. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Isolation boundary

Technická a bezpečnostná hranica oddeľujúca workload od hosta alebo iných workloads, napríklad shared-kernel container boundary alebo hypervisor/VM boundary. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Low-level container runtime

Runtime implementácia, ktorá vytvorí a spustí izolovaný process podľa OCI runtime bundle a spravuje jeho low-level lifecycle, namespaces, mounts a credentials. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Media type — OCI

Identifikátor semantic formátu descriptorom odkazovaného contentu, napríklad image manifest, image index, configuration alebo layer blob. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## MicroVM

Minimalizovaná virtual machine navrhnutá na rýchlejší startup a menší overhead pri zachovaní samostatnej virtualized-kernel boundary. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Multi-platform image

OCI image index a súvisiaci graph poskytujúci platform-specific manifests pod jednou higher-level reference, napríklad pre `linux/amd64` a `linux/arm64`. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## North-south traffic

Traffic medzi interným workloadom a externým klientom, internetom alebo službou mimo platformovej boundary. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## OCI — Open Container Initiative

Otvorená governance organizácia definujúca industry standards pre container image format, runtime bundle/lifecycle a registry distribution. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## OCI artifact

Content uložený pomocou OCI image/distribution modelu, ktorý nemusí byť runnable image, napríklad SBOM, signature, provenance, Helm chart alebo policy bundle. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## OCI referrer

Artifact alebo discovery vzťah odkazujúci na subject digest, používaný napríklad na pripojenie signature, SBOM alebo provenance k image-u. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md) a [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## OCI runtime bundle

Directory forma pre low-level runtime obsahujúca `rootfs` a `config.json` s process, mount, namespace, capability a resource configuration. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## PID limit — container

Cgroup process-count limit chrániaci host pred fork bomb alebo nekontrolovaným rastom procesov a threadov v workload-e. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Port publishing

Host-side forwarding alebo proxy konfigurácia, ktorá sprístupní container port cez zvolený host bind address a port. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Privileged container

Container spustený s výrazne rozšírenými capabilities, device accessom a oslabenými security profiles, čím sa zásadne zmenšuje jeho isolation od hosta. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Pull-through cache — registry

Lokálny registry cache model, ktorý pri prvom pull-e načíta content z upstream registry a ďalším clients ho poskytuje lokálne podľa cache a freshness policy. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Read-only root filesystem — container

Runtime policy zakazujúca zápis do image-derived root filesystemu a povoľujúca iba explicitne pripojené writable paths. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Registry mirror

Alternatívny registry endpoint replikujúci alebo cacheujúci content pre dostupnosť, latency, rate-limit alebo air-gap účely. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Rootless container

Container a runtime model fungujúci bez host-root daemon identity, typicky cez user namespaces a unprivileged networking/storage helpers. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Runtime socket exposure

Sprístupnenie container-engine API socketu workloadu, ktoré často umožňuje vytvárať privileged containers, mounts alebo inak ovládať host a predstavuje host-admin trust boundary. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Sandboxed container runtime

Runtime model pridávajúci medzi container workload a host kernel ďalšiu isolation vrstvu, napríklad user-space kernel alebo lightweight virtual machine. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Seccomp profile — container

System-call filter policy aplikovaná na container processes s cieľom znížiť dostupný host-kernel attack surface. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Shared kernel

Model, v ktorom viac host a container processes používa ten istý kernel, hoci môže mať odlišné namespace views a resource limits. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Single-writer storage

Storage contract povoľujúci v danom čase iba jedného aktívneho writer-a, ktorý potrebuje scheduling, attachment alebo fencing controls na zabránenie concurrent corruption. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Storage fencing

Mechanizmus zabezpečujúci, že starý alebo izolovaný writer už nemôže zapisovať na shared storage pred aktiváciou nového writer-a. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## tmpfs mount — container

Memory-backed temporary filesystem pripojený do containeru s lifecycle viazaným na runtime a potrebným explicitným size, memory a permissions limitom. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Veth pair

Dvojica prepojených virtual Ethernet interfaces, ktorá typicky spája container network namespace s host bridge alebo routing vrstvou. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Virtual machine — VM

Izolovaný machine environment s virtualizovaným hardware, vlastným guest kernelom a guest userspace, ktorý poskytuje hypervisor. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## VM escape

Prelomenie guest/hypervisor isolation boundary, pri ktorom code z virtual machine ovplyvní hypervisor, host alebo inú VM. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Whiteout — image layer

Marker vo filesystem changesete, ktorý v merged image view skryje path existujúci v staršom immutable layeri bez odstránenia jeho pôvodných bytes. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Workload density

Počet alebo množstvo workloads, ktoré možno bezpečne a výkonovo prevádzkovať na spoločnej infraštruktúre pri danom resource a isolation modeli. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Writable layer — container

Dočasná zapisovateľná filesystem vrstva konkrétnej container instance umiestnená nad read-only image layers, ktorej lifecycle je typicky viazaný na container. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).