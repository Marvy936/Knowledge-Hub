# Container Fundamentals and Docker glossary entries

## Active deployment digest inventory

Evidencia exact image index a selected platform manifest digestov, ktoré sú nasadené alebo potrebné pre podporovaný rollback, rescanning, retention a garbage collection. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Address-family publication contract

Explicitný contract určujúci IPv4/IPv6 host bind addresses, container listen addresses, DNS A/AAAA odpovede, firewall rules a client selection pre published service. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Application-consistent backup

Backup vytvorený po koordinácii s aplikáciou alebo databázou tak, aby zachytené dáta tvorili logicky konzistentný recovery point. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Artifact lineage — multi-stage build

Väzba od source a immutable stage inputs cez konkrétny build/test node a artifact digest až po bytes prenesené do final stage-u a publikovaný image digest. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Artifact-to-process supply chain — OCI

End-to-end transition od source/build subjectu cez OCI image graph, registry, platform selection, trust verification, pull/unpack a runtime bundle až po process a deployment evidence. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Bind mount — container

Sprístupnenie existujúceho daemon-host filesystem pathu do container mount namespace-u so silnou väzbou na host path, permissions, labels a lifecycle. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md) a [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Bind-source resolution boundary

Rozhranie medzi client pathom, Docker daemon alebo Desktop VM pathom a container destination, na ktorom sa bind source môže vyhodnotiť na inom hoste alebo directory, než operator očakáva. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Build context subject

Identita build contextu zahŕňajúca source type, root/ref/commit, effective ignore rules, expected file inventory, named contexts, submodules a relevantné metadata. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Build graph node subject

Identita jednej build operation zahŕňajúca frontend semantics, instruction, parent result, sources, mounts, args, platform a execution options. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Cache decision subject — BuildKit

Rozhodnutie spájajúce build node, cache key, cache source/trust domain, hit alebo miss, reused result, platform, timestamp a export destination. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Cache freshness gap

Stav, keď je cached result technicky validný podľa key, ale nepozoroval mutable external input alebo zámerný security/update event. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Cache poisoning path

Trust-boundary failure, pri ktorom nedôveryhodný writer ovplyvní shared build cache a release build reuseuje podvrhnutý result. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Capability drop — container

Runtime policy odstraňujúca Linux capabilities z process credential sets, ideálne drop-all s explicitným pridaním iba potrebných oprávnení. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Cgroup identity — container

Identita resource-control boundary zahŕňajúca cgroup path/ID, hierarchy, controller policy, process membership, limits, counters a pressure/events. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Cgroup OOM — container

Ukončenie procesu pre memory pressure alebo limit v jeho cgroup boundary, ktoré nemusí znamenať vyčerpanie celej host memory. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Cgroup v2

Unified Linux control-group hierarchy aplikujúca resource accounting, limits a distribution cez CPU, memory, I/O a PIDs controllers. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Clean image rebuild

Nový build z trusted source a kontrolovaných inputs po odstránení kompromitovaného source, secret alebo cache pathu; vytvára nový digest a nové evidence. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Clean restore verdict

Výsledok restore testu potvrdzujúci integrity/decryption backupu, správnu data identity, ownership, application recovery, business invariant a RPO/RTO. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Clean-room build evidence

Dôkaz build-u bez reuse relevantnej cache spolu s porovnaním inputs, builder/toolchain identity, final digestu, SBOM a runtime verdictu. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Complete artifact graph — OCI

Očakávaná množina image indexes, platform manifests, configs, layers a subject-bound signatures, provenance, SBOM alebo ďalších referrers potrebných pre release. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Compose acceptance subject

Spoločná identita resolved Compose modelu, projektu, container/image generations, resource inventory, one-shot verdictov, health a end-to-end business verification potrebná na prijatie deploymentu. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose container generation

Konkrétna container instance vytvorená z resolved service definition, identifikovaná Engine ID, config hashom, image digestom, project generation a health/runtime stavom. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose destructive scope

Množina project-owned containers, networks, volumes a orphan resources, ktoré môže zasiahnuť `down`, `down -v`, `--remove-orphans` alebo iný cleanup command. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose project generation

Versionovaný stav jedného Compose projektu viazaný na project name, Docker daemon/context, resolved model digest a vytvorené resource generations. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose resource ownership plan

Inventory určujúci pre každý network, volume, bind, image, config alebo secret, či ho vlastní Compose, external systém alebo daemon host a kto riadi preflight, retention a cleanup. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose source subject

Identita base a override files, includes/extends, active profiles, interpolation environment, project directory, Compose version a CLI options použitých na zostavenie modelu. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Compose volume identity

Effective physical volume object odvodený z Compose projectu a logical volume key alebo explicitného external name, spolu s environment, data ID a lifecycle ownerom. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Conntrack — container networking

Kernel connection-tracking state používaný firewallom a NAT-om; jeho vyčerpanie môže blokovať nové connections pri stále funkčných existujúcich flows. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container

Izolovaný runtime process alebo skupina procesov používajúca host kernel a oddelené views/resources cez namespaces, cgroups a security controls. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Container bridge network

Model, v ktorom veth pairs pripájajú container network namespaces k Linux bridge-u a host routing, firewall alebo NAT vrstve. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container escape

Prelomenie container isolation boundary, pri ktorom process získa access k hostu alebo iným workloads. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Container flow subject

Identita flowu zahŕňajúca source namespace/interface/address/port, destination, route, dataplane, pre/post-NAT tuple, policy generation, DNS answer a timestamp. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container image

Content-addressed filesystem a runtime-metadata artifact používaný na vytvorenie container instance; typicky neobsahuje runtime kernel. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Container MTU

Maximum Transmission Unit platná na container packet path-e; nesúlad s bridge, tunnel alebo uplinkom môže spôsobiť partial connectivity. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container network namespace

Linux namespace poskytujúci procesu vlastné interfaces, IPs, routes, sockets, loopback a network-state view. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container port

Port, na ktorom process počúva vo svojom network namespace; nemusí byť dostupný z hosta alebo externej siete. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container replacement lifecycle

Model, v ktorom sa release realizuje novou exact image/runtime instance a odstránením starej pri oddelenom persistent state a service identity. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Container runtime

Software vrstva pripravujúca filesystem, namespaces, cgroups, process a lifecycle podľa runtime configuration alebo OCI štandardu. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Container security baseline

Minimálna kombinácia trusted digestu, non-root usera, capability dropu, seccomp/LSM, read-only rootfs, limits, segmentation a short-lived identity. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Container security subject

Identita artifact a runtime security state-u zahŕňajúca digest, node/runtime, process authority, seccomp/LSM, mounts/devices, network, identity, secrets, resources a exceptions. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Container task subject

Identita low-level tasku zahŕňajúca containerd namespace/task ID, runtime/shim, PID, bundle/config, start/exit generation a väzbu na Docker object. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Container volume

Runtime-managed storage object s lifecycle oddeleným od containeru, ktorý však automaticky neposkytuje backup, replication ani multi-host durability. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Controlled dependency refresh

Reviewovaný prechod na nový base, repository snapshot, lock alebo external input, ktorý zámerne mení build freshness a vytvára nové artifact evidence. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Copy-on-write — container filesystem

Model, pri ktorom read-only image content zostáva zdieľaný a prvá zmena vytvorí kópiu alebo záznam vo writable upper layeri. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Copy-up

Operácia prenesenia file-u z read-only lower layeru do writable upper layeru pri prvom zápise. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Crash-consistent snapshot

Snapshot zodpovedajúci náhlemu výpadku bez garancie, že application buffers alebo transactions boli konzistentne uzavreté. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Data-ID preflight

Kontrola pred mutation potvrdzujúca environment, persistent data identity, generation/lineage, schema compatibility a writer authority. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Dependency-coupled health failure

Failure, pri ktorom healthcheck stotožní vzdialenú dependency outage s local liveness a vyvolá zbytočné restarty alebo restart storm. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Descriptor — OCI

Štruktúra identifikujúca OCI content cez media type, digest, size a prípadné platform metadata. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Destructive volume cleanup subject

Presná identita daemonu, projektu, volume objectu, logical data ID, ownera, backup/restore verdictu a retention approval potrebná pred odstránením volume-u. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Diff ID — OCI image

Digest uncompressed filesystem changesetu uložený v OCI image configuration rootfs chain. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Distribution digest — OCI

Digest registry blobu alebo manifestu v distribuovanej reprezentácii, používaný na integrity a immutable references. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Docker API operation subject

Identita Engine API mutation zahŕňajúca context/endpoint, caller, requested object/image, name/labels, runtime policy, correlation ID a purpose. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker context identity

Resolved Docker client target zahŕňajúci context name, Engine endpoint, SSH/TLS metadata a expected daemon/environment identity. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker DNS generation

Versionovaný endpoint a alias inventory v konkrétnej Docker network/project boundary, ktorý mapuje stable service names na aktuálne container addresses a readiness state. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker endpoint subject

Identita pripojenia containeru k Docker networku zahŕňajúca network/endpoint IDs, addresses, aliases, veth/interface, routes, DNS a attach generation. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker forwarding path

Host-side packet transition od published bind addressu cez proxy alebo DNAT, forwarding policy, bridge/veth a reverse conntrack translation ku container socketu. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker mount subject

Identita mountu zahŕňajúca daemon/context, source type a physical/logical identity, project, destination, access flags, UID/GID mapping, LSM, propagation, data generation a ownera. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Docker network subject

Identita Docker network objectu zahŕňajúca daemon/project, network ID/name, driver/options, subnet/gateway, flags, endpoint inventory, DNS, MTU a policy generation. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Docker object-task reconciliation

Porovnanie Docker object metadata, containerd task/shim, runtime processu, endpoints, mounts a application outcome-u po timeoute alebo partial operation. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Dockerfile frontend identity

Versionovaná implementácia Dockerfile syntax a build semantics vybraná parser directive-om alebo builder defaultom. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Dockerfile program subject

Identita build programu zahŕňajúca Dockerfile/frontend, immutable inputs, stage graph, args/secrets references, platform, builder a selected target. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## East-west traffic

Traffic medzi internými workloads alebo services v rámci platformy. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Effective firewall verdict — container

Výsledok policy rozhodovania nad konkrétnym direction/interface a pre/post-NAT tuple po zohľadnení Docker, host, cloud a remote rules. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Effective image metadata

Runtime defaults vo final image confige, najmä entrypoint, command, environment, user, workdir, labels, healthcheck, exposed ports a stop signal. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Effective mount access verdict

Kernel výsledok nad visible pathom po zohľadnení process UID/GID, user mapping, inode mode/ACL, mount read-only flags a SELinux/AppArmor policy. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Effective runtime policy subject

Kernel-enforced state vzniknutý z image defaults, deployment overrides, daemon/orchestrator defaults a node policy vrátane credentials, capabilities, seccomp, LSM, mounts, devices, network a cgroups. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Endpoint replacement proof

Dôkaz, že po replacement-e alebo drain-e Docker DNS a caller connection state prestali používať stale endpoint a traffic smeruje iba na aktuálnu ready generation. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Ephemeral runtime instance

Nahraditeľná runtime inštancia, ktorej process a writable-layer state nie je jediným persistentným zdrojom dát. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Expected context inventory

Vopred validovaná množina paths a named contexts, ktoré musia alebo nesmú byť dostupné builderu. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Expected stage evidence inventory

Množina build, test, analysis, target a per-platform verdictov požadovaných pre release; missing evidence nie je pass. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## External cache trust domain

Boundary určujúca identities oprávnené čítať/zapisovať build cache a release classes, pre ktoré je reuse prípustný. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## External resource preflight

Kontrola external Compose networku, volume-u, configu alebo secretu pred deploymentom vrátane existence, environmentu, ownera, permissions, compatibility a cleanup zodpovednosti. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Filesystem transition — Dockerfile

Build-time zmena stage filesystemu cez `COPY`, `ADD` alebo `RUN`, ktorá vstupuje do layer graphu a môže preniesť content, ownership, permissions alebo secret residue. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Garbage collection — registry

Odstraňovanie manifestov alebo blobs, ktoré nie sú reachable z retained references, koordinované s pushes, deletes, referrers a retention policy. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## GC reachability snapshot — registry

Konzistentný pohľad na retained tags, manifests, blobs, referrers, uploads, leases, deployments a rollback subjects pre GC rozhodnutie. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Guest operating system

Operačný systém bežiaci vo VM nad virtualizovaným hardware a vlastným guest kernelom. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Health generation

Versionovaný stav healthcheck definition, container generation a jej časovej health history, ktorý sa musí viazať na konkrétny runtime subject. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Health remediation budget

Limitovaný restart alebo recovery contract určujúci confidence, backoff, drain, stateful risk, post-action verification a escalation threshold pri unhealthy stave. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Healthcheck subject

Identita probe zahŕňajúca container/image generation, command, runtime user/env/PATH, target namespace/endpoint, timing, redaction a health history. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Host network mode

Runtime mode zdieľajúci host network namespace a tým host ports, interfaces a traffic exposure. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Host port — container

Port a bind address v host namespace, ktorý forwarding alebo proxy mapuje na container port. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Host-publication subject

Exact mapping address family, host bind address/port/protocol, endpoint generation, container address/port, forwarding implementation a firewall/upstream policy. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Hypervisor

Virtualization vrstva poskytujúca virtual hardware a isolation pre virtual machines. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Image configuration — OCI

OCI JSON artifact obsahujúci platform, runtime defaults, user, entrypoint/command, environment, rootfs diff IDs a history metadata. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Image content subject

Identita image graphu zahŕňajúca manifest, config a ordered layer descriptors/digests, oddelená od snapshotu a runtime state-u. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Image index — OCI

Manifest list odkazujúci na viac platform-specific manifests. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Image layer

Immutable filesystem changeset v ordered image graph-e. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Image manifest — OCI

OCI artifact odkazujúci na jednu image configuration a ordered layer blobs. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Image-config contract test

Assertion nad final image configom a runtime overrides overujúca entrypoint, command, user, environment, healthcheck, signal, ports a writable paths pre exact digest. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Image-config transition — Dockerfile

Instruction meniaca runtime metadata image-u, napríklad `ENV`, `USER`, `ENTRYPOINT`, `CMD`, `HEALTHCHECK` alebo `STOPSIGNAL`. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Immutable build input inventory

Úplná identita source/contextu, Dockerfile/frontendu, base/external image digestov, dependencies, args, secret references, platformy, buildera, cache a targetu. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Internal direct path

Container-to-container flow cez spoločnú Docker network a service DNS priamo na container port bez host publication boundary. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Isolation boundary

Technická a bezpečnostná hranica oddeľujúca workload od hosta alebo iných workloads. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Layer-aware secret incident

Incident, pri ktorom secret môže byť v layeri, image metadata, context/cache, platform variante, writable layeri alebo mounted storage a vyžaduje clean rebuild aj revocation. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Low-level container runtime

Runtime vytvárajúci a spúšťajúci process podľa OCI runtime bundle a spravujúci namespaces, mounts a credentials. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Media type — OCI

Identifikátor semantic formátu OCI descriptorom odkazovaného contentu. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Merged filesystem lookup

Path resolution cez writable upper layer a ordered lower layers so zohľadnením whiteouts a opaque directories. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## MicroVM

Minimalizovaná VM s rýchlejším startupom a menším overheadom pri zachovaní virtualized-kernel boundary. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Mount obscuring

Runtime jav, pri ktorom mount na destination path skryje image content v merged view bez odstránenia bytes z image layers. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Mount source identity

Logical a physical identita volume-u, external backendu, bind host pathu, tmpfs alebo socket/device source-u spolu s daemonom, hostom, projektom a lifecycle ownerom. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Multi-platform image

OCI index a graph poskytujúci manifests pre viac OS/architecture/variant kombinácií. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Named context subject

Identita explicitne pomenovaného build contextu, napríklad directory, Git commit alebo image digest. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Namespace view

Process-specific pohľad na shared kernel state, napríklad PID tree, mounts alebo network stack; sám nie je resource limit ani access verdict. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## North-south traffic

Traffic medzi interným workloadom a externým klientom alebo službou mimo platformy. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## OCI — Open Container Initiative

Organizácia definujúca standards pre image format, runtime lifecycle a registry distribution. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## OCI artifact

Content uložený OCI modelom, ktorý nemusí byť runnable image, napríklad SBOM, signature, provenance alebo chart. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## OCI referrer

Artifact alebo discovery vzťah viažuci signature, SBOM alebo provenance na subject digest. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md) a [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## OCI release subject

Immutable release identity spájajúca source/build, image index, platform manifests, configs/layers, registry, trust artifacts a runtime contract. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## OCI runtime bundle

Directory obsahujúca `rootfs` a `config.json` s process, mounts, namespaces, capabilities a resources. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## One-shot operation subject

Identita Compose migration alebo init jobu zahŕňajúca operation ID, image/config/data subject, project, concurrency lock, result a rerun/unknown-outcome semantics. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Persistence classification — container

Rozdelenie writable paths na ephemeral, persistent business, re-injectable config/secret a incident evidence state. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Persistent data preflight

Kontrola logical data ID, environmentu, generation/schema, writer epoch, source volume/backend identity a backup compatibility pred prvou runtime mutation. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Persistent data subject — container

Identita durable state-u zahŕňajúca logical data ID, generation, backend/filesystem, topology/access mode, writer authority, encryption a backup contract. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## PID limit — container

Cgroup limit počtu procesov/threadov chrániaci host pred fork bomb alebo nekontrolovaným rastom. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Platform compatibility contract — container

Požiadavky na kernel/runtime features, CPU, libc, devices, filesystem, seccomp/LSM, storage a network potrebné na spustenie workloadu. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Platform manifest — OCI

Konkrétny manifest vybraný z indexu pre OS/architecture/variant, odkazujúci na config a layers. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Port-publication subject — container

Mapping host bind addressu, portu a protocolu cez forwarding/NAT/proxy na container address/port s policy. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Port publishing

Host-side forwarding alebo proxy konfigurácia sprístupňujúca container port cez host address a port. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Privileged container

Container s výrazne rozšírenými capabilities, devices a oslabenými security profiles. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Privileged-policy collapse

Runtime configuration, pri ktorej privileged mode alebo broad authority zruší významnú časť očakávanej container boundary. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Process-loaded configuration

Non-secret effective state, ktorý application reálne načítala po startup/reload-e, odlíšený od source files, resolved modelu a container create configuration. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Process readiness boundary

Prechod medzi spusteným processom a schopnosťou bezpečne prijímať traffic alebo vykonávať workload. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Project collision incident

Failure, pri ktorom dve pipelines alebo environments používajú rovnaký Compose project a vzájomne recreatujú, testujú alebo mažú spoločné resources. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Project-network split

Failure, pri ktorom services s rovnakými logical names bežia v rozdielnych Compose project networks a preto nezdieľajú DNS ani connectivity boundary. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Publication exposure generation

Versionovaný stav host publications, endpoint mappings, firewall/upstream policies a intended client scope použitý na audit dostupnosti aj neplánovanej exposure. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Pull-through cache — registry

Registry cache, ktorý pri prvom pull-e načíta content z upstream a následne ho poskytuje lokálne podľa freshness policy. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Read-only root filesystem — container

Policy zakazujúca zápis do image-derived rootfs a povoľujúca iba explicitné writable paths. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Redacted effective configuration manifest

Evidence názvov fields, source provenance, epochs a hashes bez plaintext secrets, ktorá vysvetľuje container create a process-loaded configuration. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Registry mirror

Alternatívny registry endpoint replikujúci alebo cacheujúci content pre availability, latency alebo air-gap účely. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Registry publication subject

Identita publication zahŕňajúca producer, registry/repository, index/platform manifests, reachable blobs, evidence, tags, policy a read-back generation. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Replication generation — registry

Versionovaný stav synchronizácie replica/mirror určujúci prijaté manifests, blobs, tags, deletes a referrers. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Replacement persistence proof

Dôkaz, že replacement container pripojil rovnaký expected persistent data subject a pokračuje bez neplánovanej initialization alebo data loss. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Resolved Compose model subject

Canonical effective application model po interpolation, merge, profiles, include a extends, viazaný na source inventory, Compose version a model digest. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Resolved-model policy

Policy vyhodnocujúca effective Compose model vrátane images, ports, mounts, networks, devices, privileged settings, secrets a external resources namiesto jednotlivých fragments. Pozri [Docker Compose](docs/08-container-fundamentals-and-docker/docker-compose.md).

## Rollback digest inventory

Množina immutable registry subjects, ktoré musia zostať pullable a policy-valid počas rollback/support windowu. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Rootless container

Container/runtime model bez host-root daemon identity, typicky cez user namespaces a unprivileged helpers. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Runtime bundle subject — OCI

Identita generated `rootfs` a `config.json` zahŕňajúca selected manifest, overrides, mounts, namespaces, capabilities, resources a hooks. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Runtime configuration subject

Identita image defaults, Compose sources, interpolation/env files, CLI overrides, mounted configs/secrets, schema, container generation a process-loaded config epoch. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Runtime dependency closure

Úplná množina executable, interpreter/linker, libraries, certificates, DNS/NSS, timezone/locale, users, writable paths a helpers potrebných vo final stage-i. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Runtime isolation subject

Identita process policy vrátane host/runtime, namespaces, cgroup, UID/GID mappings, capabilities, `no_new_privs`, seccomp, LSM, mounts, devices a entrypoint. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Runtime process contract — image

Vzťah effective entrypoint/command, PID 1, signals, runtime usera, workdir, health/readiness a required filesystem/dependencies. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Runtime socket authority

Host-admin-like authority získaná accessom k container-engine socketu. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Runtime socket exposure

Sprístupnenie Engine API socketu workloadu, ktoré často umožňuje ovládať host cez privileged containers alebo mounts. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Sandboxed container runtime

Runtime pridávajúci ďalšiu isolation vrstvu medzi workload a host kernel, napríklad user-space kernel alebo lightweight VM. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Seccomp profile — container

System-call filter policy znižujúca host-kernel attack surface dostupný workloadu. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Security exception subject — container

Časovo obmedzená výnimka viazaná na exact workload/runtime, environment, bypassovaný control, risk, ownera, compensating controls a expiration. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Selected build target

Explicitne zvolený final, test, development, debug alebo artifact stage, ktorý je súčasťou release subjectu a publication policy. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Service alias ownership

Contract určujúci, ktorá service vlastní konkrétny alias v danej Docker network a aké replica/load-distribution semantics caller očakáva. Pozri [Docker networks a port publishing](docs/08-container-fundamentals-and-docker/docker-networks-port-publishing.md).

## Service endpoint generation — container networking

Versionovaný service-discovery inventory viažuci stable workload identities, addresses, readiness, eligibility a draining/removal state. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Shared kernel

Model, v ktorom host a container processes používajú rovnaký kernel pri odlišných namespace views a limits. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Single-writer storage

Storage contract povoľujúci v danom čase iba jedného active writer-a a vyžadujúci scheduling/fencing. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Snapshot lease — container runtime

Referencia chrániaca unpacked content a snapshots používané pullom, buildom alebo containerom pred GC. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Snapshot subject — container filesystem

Runtime-specific unpacked representation verified image layers, z ktorej vzniká rootfs a per-container writable layer. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Socket capability mount

Mount Unix socketu alebo podobného host control endpointu, ktorého authority sa určuje server API oprávneniami, nie iba filesystem read/write flagom. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Split-writer incident

Failure, pri ktorom viac processov alebo nodes verí, že má write authority nad rovnakou persistent data identity. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Stage DAG subject

Identita multi-stage graphu zahŕňajúca stage names, base/inputs, dependency edges, targets, platforms, cache outcomes a transfers. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Stage-output secret incident

Incident, pri ktorom secret prejde cez generated artifact, `COPY --from`, cache alebo export z build stage-u do final image-u. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Storage attachment subject

Identita backend volume/objectu, node/device pathu, filesystem UUID, host/container mounts, options, topology a active writer lease-u. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Storage fencing

Mechanizmus zabezpečujúci, že stale writer už nemôže zapisovať pred aktiváciou nového writer-a. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Subject-bound referrer — OCI

Signature, provenance, SBOM alebo iný artifact explicitne viazaný na image index alebo platform manifest digest. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Subject-bound runtime verification

Health, configuration, client-path alebo business evidence viazaná na exact image, container/project generation a configuration/data epochs. Pozri [Environment variables a health checks](docs/08-container-fundamentals-and-docker/environment-variables-health-checks.md).

## Subject-bound security evidence inventory

Množina signature, provenance, SBOM, scan, runtime-policy, identity, network/storage a exception evidence validná pre exact artifact/workload. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Subject-bound test stage

Test verdict viazaný na exact source, inputs, platform, build artifact a final image subject. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Target publication policy

Policy overujúca, že production reference publikuje povolený target s expected base, user, content, metadata, platforms a lineage. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## tmpfs mount — container

Memory-backed temporary filesystem s runtime lifecycle a explicitným size, memory a permissions contractom. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Unknown Docker operation outcome

Stav, keď klient nevie, či Engine mutation neprebehla, zanechala partial objects alebo úspešne spustila process; pred retry vyžaduje reconciliation. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Veth pair

Dvojica prepojených virtual Ethernet interfaces spájajúca container namespace s host bridge/routing vrstvou. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Virtual machine — VM

Izolovaný machine environment s virtual hardware, vlastným guest kernelom a userspace-om. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## VM escape

Prelomenie guest/hypervisor boundary, pri ktorom code z VM ovplyvní hypervisor, host alebo inú VM. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Volume initialization subject

Identita empty/new volume initialization alebo schema migration zahŕňajúca data ID, generation, writer lock, migration ledger a postcondition verdict. Pozri [Volumes a bind mounts](docs/08-container-fundamentals-and-docker/volumes-bind-mounts.md).

## Whiteout — image layer

Marker v changesete, ktorý v merged view skryje path zo staršej layer bez odstránenia pôvodných bytes. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Workload density

Počet workloads, ktoré možno bezpečne a výkonovo prevádzkovať na spoločnej infraštruktúre pri danom isolation/resource modeli. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Workload identity subject — container

Short-lived authorization identity viazaná na workload/environment s audience, scopes, token epoch/expiration, issuance a auditom. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Workload isolation subject

Identita workloadu a VM/container boundary zahŕňajúca release/image, kernel, runtime config, resources, network, persistent ownera a isolation class. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Writer epoch — container storage

Monotónna alebo fencing-aware generation authoritative writer-a použitá na odmietnutie stale processu/node-u. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Writable layer — container

Dočasná zapisovateľná filesystem vrstva konkrétnej container instance nad read-only image layers. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).