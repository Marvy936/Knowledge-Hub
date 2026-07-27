# Container Fundamentals and Docker glossary entries

## Active deployment digest inventory

Evidencia exact image index a selected platform manifest digestov, ktoré sú aktuálne nasadené alebo potrebné pre podporovaný rollback; používa sa pri rescanningu, retention a garbage collection rozhodnutiach. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Application-consistent backup

Backup vytvorený po koordinácii s aplikáciou alebo databázou tak, aby zachytené dáta tvorili logicky konzistentný recovery point, nie iba náhodný filesystem okamih. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Artifact lineage — multi-stage build

Rekonštruovateľná väzba od source a immutable stage inputs cez konkrétny build/test node a artifact digest až po bytes prenesené do final stage-u a publikovaný image digest. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Artifact-to-process supply chain — OCI

End-to-end transition od source/build subjectu cez OCI image graph, registry publication, platform selection, trust verification, pull/unpack a runtime bundle až po low-level runtime process a deployment evidence. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Bind mount — container

Sprístupnenie existujúceho host filesystem pathu do container mount namespace-u, ktoré vytvára silnú väzbu na host path, permissions, labels a lifecycle. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Build context subject

Immutable alebo rekonštruovateľná identita build contextu zahŕňajúca source type, root/ref/commit, effective ignore rules, expected file inventory, named contexts, submodules a relevantné file metadata. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Build graph node subject

Identita jednej build operation zahŕňajúca frontend semantics, instruction, parent result, source/context inputs, mounts, args, platform a execution options, z ktorých builder odvodzuje result a cache decision. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Cache decision subject — BuildKit

Rekonštruovateľné rozhodnutie spájajúce build node subject, cache key, cache source a trust domain, hit/miss outcome, reused result identity, platform, timestamp a export destination. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Cache freshness gap

Stav, keď je cached result technicky validný podľa key, ale nepozoroval mutable external input alebo zámerný security/update event a preto už nespĺňa požadovanú freshness policy. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Cache poisoning path

Trust-boundary failure, pri ktorom nedôveryhodný writer ovplyvní shared build cache a privilegovaný alebo release build následne reuseuje podvrhnutý result. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Capability drop — container

Runtime policy odstraňujúca Linux capabilities z process credential sets, ideálne s defaultom drop-all a explicitným pridaním iba nevyhnutných oprávnení. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Cgroup identity — container

Rekonštruovateľná identita resource-control boundary zahŕňajúca cgroup path alebo ID, parent hierarchy, controller policy, process membership, limits, counters a pressure/event evidence. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Cgroup OOM — container

Ukončenie procesu v dôsledku prekročenia alebo nezvládnutia memory pressure v jeho cgroup boundary, ktoré nemusí znamenať vyčerpanie celej host memory. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Cgroup v2

Unified Linux control-group hierarchy organizujúca procesy a aplikujúca resource accounting, limits a distribution cez controllers ako CPU, memory, I/O a PIDs. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Clean image rebuild

Nový build z trusted source a kontrolovaných inputs po odstránení kompromitovaného source, secret alebo cache pathu; musí vytvoriť nový digest a nové evidence namiesto live opravy containeru. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Clean restore verdict

Subject-bound výsledok restore testu potvrdzujúci integrity a decryption backupu, správnu data identity, ownership/labels, application recovery, business invariant a namerané RPO/RTO na čistom targete. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Clean-room build evidence

Dôkaz nového build-u bez reuse relevantnej cache spolu s porovnaním immutable inputs, builder/toolchain identity, final digestu, SBOM a runtime verdictu; používa sa na odhalenie skrytých alebo mutable inputs. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Complete artifact graph — OCI

Očakávaná a overená množina image indexes, platform manifests, configs, layer blobs a subject-bound signatures, provenance, SBOM alebo ďalších referrers potrebných pre konkrétny release. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Conntrack — container networking

Kernel connection-tracking state používaný firewallom a NAT-om; jeho vyčerpanie alebo nevhodné timeouts môžu spôsobovať dropped nové spojenia medzi containers a externými sieťami. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container

Izolovaný runtime process alebo skupina procesov používajúca host kernel a oddelený pohľad na resources cez namespaces, cgroups a ďalšie security controls. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Container bridge network

Network model, v ktorom host-side konce veth pairs pripájajú container network namespaces k Linux bridge-u a následne k host routing, firewall alebo NAT vrstve. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container escape

Prelomenie container isolation boundary, pri ktorom process získa access k hostu alebo iným workloads. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Container flow subject

Rekonštruovateľná identita jedného network flowu zahŕňajúca source namespace/interface/address/port, destination name/address/port, route, veth/bridge/dataplane, pre- a post-NAT tuple, policy generation, DNS answer a timestamp. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container image

Versionovaný a typicky content-addressed filesystem a runtime-metadata artifact používaný na vytvorenie container instance; bežne neobsahuje kernel použitý pri runtime. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md) a [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Container MTU

Maximum Transmission Unit platná na container interface a jeho packet path-e; nesúlad s bridge, tunnel alebo host uplinkom môže spôsobovať partial connectivity a dropped veľké packets. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container network namespace

Linux network namespace poskytujúci container procesu vlastné interfaces, IP adresy, routes, sockets, loopback a network state view. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container port

Port, na ktorom process počúva vo svojom network namespace; nemusí byť dostupný z hosta alebo externej siete bez routing alebo port-publishing konfigurácie. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Container replacement lifecycle

Model, v ktorom sa application zmena realizuje buildom a nasadením novej exact image/runtime instance a odstránením starej, pričom persistent state a service identity sú oddelené od writable layeru. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Container runtime

Software vrstva pripravujúca container filesystem, namespaces, cgroups, process a lifecycle podľa runtime configuration alebo štandardu. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Container security baseline

Minimálna kombinácia controls, napríklad trusted digest, non-root user, capability drop, seccomp, LSM policy, read-only root filesystem, resource limits, network segmentation a short-lived identity. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Container security subject

Presná identita artifact a runtime security state-u zahŕňajúca source/build evidence, selected platform digest, node/runtime, process identity a authority, seccomp/LSM, mounts/devices, network exposure, workload identity, secrets, resources a policy exceptions. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Container task subject

Identita low-level running alebo exited tasku zahŕňajúca containerd namespace/task ID, runtime/shim, process PID, bundle/config, start/exit generation a väzbu na Docker container object. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Container volume

Runtime-managed storage object s lifecycle oddeleným od konkrétnej container instance, ktorý môže poskytovať persistence, ale nie automaticky backup, replication alebo multi-host durability. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Controlled dependency refresh

Reviewovaný prechod na nový base, package-repository snapshot, lock alebo external input subject, ktorý zámerne mení build freshness a následne vytvára nový artifact, SBOM, scan a runtime evidence. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Copy-on-write — container filesystem

Filesystem model, pri ktorom read-only image layer content zostáva zdieľaný a prvá zmena vytvorí novšiu kópiu alebo záznam vo writable upper layeri. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Copy-up

Operácia, pri ktorej sa file z read-only lower layeru pri prvom zápise prenesie do writable upper layeru a ďalšie zmeny sa vykonávajú nad touto kópiou. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Crash-consistent snapshot

Storage snapshot zodpovedajúci stavu po náhlom výpadku napájania bez garancie, že application buffers, transactions alebo koordinované multi-volume dáta boli konzistentne uzavreté. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Data-ID preflight

Kontrola pred spustením alebo recovery stateful workloadu, ktorá potvrdzuje logical environment, persistent data identity, generation/lineage, schema/application compatibility a writer authority pred prvou mutation. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Descriptor — OCI

Štruktúra identifikujúca OCI content pomocou media type, digestu a size, prípadne ďalších annotations alebo platform metadata. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Diff ID — OCI image

Digest uncompressed filesystem layer changesetu uložený v OCI image configuration rootfs chain, odlišný od digestu compressed blobu prenášaného cez registry. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Distribution digest — OCI

Content digest registry blobu alebo manifestu v jeho distribuovanej reprezentácii, používaný na integrity verification a immutable references. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Docker API operation subject

Presná identita Engine API operácie zahŕňajúca Docker context a endpoint, caller identity, requested image/object, container name a labels, network/mount/port/resource policy, correlation ID a operation purpose. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker context identity

Resolved Docker client target zahŕňajúci context name, Engine endpoint, SSH/TLS metadata a očakávaný daemon/environment identity; musí sa overiť pred privilegovanou alebo deštruktívnou operáciou. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Docker object-task reconciliation

Porovnanie Docker container object metadata, containerd task/shim state, runtime processu, network endpointov, mounts a application outcome-u po timeoute, daemon failure alebo partial operation. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

## Dockerfile frontend identity

Versionovaná implementácia Dockerfile syntax a build semantics vybraná parser directive-om alebo builder defaultom, ktorá je súčasťou reprodukovateľného build subjectu. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Dockerfile program subject

Rekonštruovateľná identita build programu zahŕňajúca Dockerfile a frontend, immutable input inventory, stage graph, build args/secrets references, target platform, builder a selected final target. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## East-west traffic

Network traffic medzi internými workloads alebo services v rámci platformy, ktorého nekontrolovaný default-allow model zvyšuje lateral-movement risk. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Effective firewall verdict — container

Výsledok packet-policy rozhodovania nad konkrétnym direction, interface a pre- alebo post-NAT tuple po zohľadnení container, engine-managed, host, cloud a remote policy vrstiev. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Effective image metadata

Runtime defaults v image configuration po vyhodnotení stage graphu, najmä entrypoint, command, environment, user, working directory, labels, healthcheck, exposed ports a stop signal, ešte pred runtime overrides. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Effective runtime policy subject

Generated a kernel-enforced runtime state vzniknutý z image defaults, deployment overrides, daemon/orchestrator defaults a node policy, zahŕňajúci process identity, capabilities, seccomp, LSM, mounts, devices, network a cgroups. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Ephemeral runtime instance

Nahraditeľná runtime inštancia, ktorej lokálny procesový a writable-layer stav nie je považovaný za jediný persistentný zdroj dát. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Expected context inventory

Vopred validovaná množina files, paths, metadata a named contexts, ktoré musia alebo nesmú byť dostupné builderu pre konkrétny build subject. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Expected stage evidence inventory

Vopred definovaná množina build, test, analysis, target a per-platform verdictov požadovaných pre release; missing stage alebo evidence nie je ekvivalent pass-u. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## External cache trust domain

Boundary určujúca, ktoré identities môžu čítať alebo zapisovať konkrétny external build cache subject a pre ktoré branches, repositories, platforms a release classes je jeho reuse prípustný. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Filesystem transition — Dockerfile

Build-time zmena stage filesystemu vytvorená napríklad `COPY`, `ADD` alebo `RUN`, ktorá vstupuje do layer/result graphu a môže preniesť content, ownership, permissions alebo secret residue. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Garbage collection — registry

Proces odstraňovania manifestov alebo blobs, ktoré už nie sú reachable z retained references, vykonávaný s koordináciou voči pushes, deletes, referrers a retention policy. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## GC reachability snapshot — registry

Konzistentný pohľad na retained tags, manifests, blobs, referrers, active uploads, leases, deployments a rollback subjects používaný na bezpečné určenie obsahu oprávneného na garbage collection. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

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

## Image content subject

Rekonštruovateľná identita image graphu zahŕňajúca manifest, config a ordered layer descriptors/digests, oddelená od unpacked snapshotu a runtime writable state-u. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Image index — OCI

Manifest list odkazujúci na viac OCI manifests, typicky pre rozdielne OS, architecture a variant platformy. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Image layer

Immutable filesystem changeset v ordered image graph-e, ktorý sa skladá s ostatnými layers do výsledného root filesystemu. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Image manifest — OCI

OCI artifact odkazujúci descriptorom na jednu image configuration a ordered list filesystem layer blobs. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Image-config contract test

Assertion nad final image configom a effective runtime override-mi, ktorá overuje expected entrypoint, command, user, environment, healthcheck, stop signal, port metadata a writable-path assumptions pre exact image digest. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Image-config transition — Dockerfile

Build instruction, ktorá mení runtime metadata image-u bez toho, aby sama vytvorila budúci process, napríklad `ENV`, `USER`, `ENTRYPOINT`, `CMD`, `HEALTHCHECK` alebo `STOPSIGNAL`. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Immutable build input inventory

Úplná identita source/contextu, Dockerfile/frontendu, base a external image digestov, dependency lockov/snapshots, args, secret references, platformy, buildera, cache subjects a targetu potrebná na vysvetlenie final artifactu. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Isolation boundary

Technická a bezpečnostná hranica oddeľujúca workload od hosta alebo iných workloads, napríklad shared-kernel container boundary alebo hypervisor/VM boundary. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Layer-aware secret incident

Incident, pri ktorom sa secret môže nachádzať v historickom layeri, image config/history, build context/cache, platform variante, runtime writable layeri alebo mounted storage a recovery vyžaduje presný subject, clean rebuild aj revocation credentialu. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Low-level container runtime

Runtime implementácia, ktorá vytvorí a spustí izolovaný process podľa OCI runtime bundle a spravuje jeho low-level lifecycle, namespaces, mounts a credentials. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Media type — OCI

Identifikátor semantic formátu descriptorom odkazovaného contentu, napríklad image manifest, image index, configuration alebo layer blob. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Merged filesystem lookup

Path-resolution model, ktorý pri read-e hľadá najvyššiu visible verziu pathu vo writable upper layeri a následne v ordered lower layers, pričom rešpektuje whiteouts a opaque-directory semantics. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## MicroVM

Minimalizovaná virtual machine navrhnutá na rýchlejší startup a menší overhead pri zachovaní samostatnej virtualized-kernel boundary. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Multi-platform image

OCI image index a súvisiaci graph poskytujúci platform-specific manifests pod jednou higher-level reference, napríklad pre `linux/amd64` a `linux/arm64`. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Named context subject

Immutable identita explicitne pomenovaného Docker build contextu, napríklad local directory, Git commit alebo image digest, používaného stage-like reference-om bez rozšírenia primary contextu. Pozri [Build context a layer cache](docs/08-container-fundamentals-and-docker/build-context-layer-cache.md).

## Namespace view

Process-specific pohľad na vybranú kategóriu shared kernel state-u, napríklad PID tree, mount table alebo network stack; sám o sebe nepredstavuje resource limit ani access-control verdict. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## North-south traffic

Traffic medzi interným workloadom a externým klientom, internetom alebo službou mimo platformovej boundary. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## OCI — Open Container Initiative

Otvorená governance organizácia definujúca industry standards pre container image format, runtime bundle/lifecycle a registry distribution. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## OCI artifact

Content uložený pomocou OCI image/distribution modelu, ktorý nemusí byť runnable image, napríklad SBOM, signature, provenance, Helm chart alebo policy bundle. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## OCI referrer

Artifact alebo discovery vzťah odkazujúci na subject digest, používaný napríklad na pripojenie signature, SBOM alebo provenance k image-u. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md) a [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## OCI release subject

Immutable release identity spájajúca source/build subject, image index digest, expected platform manifests, configs/layers, registry/repository, trust artifacts a podporovaný runtime/platform contract. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## OCI runtime bundle

Directory forma pre low-level runtime obsahujúca `rootfs` a `config.json` s process, mount, namespace, capability a resource configuration. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Persistence classification — container

Rozdelenie writable paths na ephemeral state, persistent business state, znovu injektovateľnú configuration/secret state a incident evidence, z ktorého vyplýva storage, backup, cleanup a replacement contract. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Persistent data subject — container

Rekonštruovateľná identita durable application state-u zahŕňajúca logical data ID, generation/lineage, backend object, filesystem alebo object identity, topology/access mode, writer authority, encryption a backup/restore contract. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## PID limit — container

Cgroup process-count limit chrániaci host pred fork bomb alebo nekontrolovaným rastom procesov a threadov v workload-e. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Platform compatibility contract — container

Súbor požiadaviek nad rámec OS a CPU architecture, napríklad kernel/runtime features, CPU variant, libc, devices, filesystem, seccomp/LSM a storage/network capabilities potrebné na úspešné spustenie workloadu. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md) a [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Platform manifest — OCI

Konkrétny image manifest vybraný z image indexu pre jednu OS/architecture/variant kombináciu, ktorý odkazuje na config a ordered layer blobs reálne použité pri pull/unpack. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Port-publication subject — container

Effective mapping host bind addressu, host portu a protocolu cez forwarding/NAT/proxy na konkrétny container address a port spolu s firewall/exposure policy. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Port publishing

Host-side forwarding alebo proxy konfigurácia, ktorá sprístupní container port cez zvolený host bind address a port. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Privileged container

Container spustený s výrazne rozšírenými capabilities, device accessom a oslabenými security profiles, čím sa zásadne zmenšuje jeho isolation od hosta. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Privileged-policy collapse

Runtime konfigurácia, pri ktorej privileged mode alebo kombinácia broad capabilities, devices, host mounts a oslabených seccomp/LSM controls zruší významnú časť pôvodne očakávanej container boundary. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Process readiness boundary

Prechod medzi existenciou/spustením container processu a jeho schopnosťou bezpečne prijímať traffic alebo vykonávať workload, potvrdený dependency, configuration a business-level oracle. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Pull-through cache — registry

Lokálny registry cache model, ktorý pri prvom pull-e načíta content z upstream registry a ďalším clients ho poskytuje lokálne podľa cache a freshness policy. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Read-only root filesystem — container

Runtime policy zakazujúca zápis do image-derived root filesystemu a povoľujúca iba explicitne pripojené writable paths. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Registry mirror

Alternatívny registry endpoint replikujúci alebo cacheujúci content pre dostupnosť, latency, rate-limit alebo air-gap účely. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Registry publication subject

Immutable identita publication operácie zahŕňajúca producer identity, registry/repository, index a platform manifests, complete reachable blobs, related evidence, tags, policy verdict a read-back generation. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Replication generation — registry

Versionovaný stav replica/mirror synchronizácie určujúci, ktoré manifests, blobs, tags, deletes a referrers destination preukázateľne prijala z konkrétneho source generation. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Rollback digest inventory

Množina immutable registry subjects, ktoré musia zostať pullable a policy-valid počas deklarovaného rollback alebo support windowu aj vtedy, keď už nemajú aktívny tag. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md).

## Rootless container

Container a runtime model fungujúci bez host-root daemon identity, typicky cez user namespaces a unprivileged networking/storage helpers. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Runtime bundle subject — OCI

Rekonštruovateľná identita generated `rootfs` a `config.json` zahŕňajúca selected platform manifest, runtime overrides, mounts, namespaces, capabilities, resource policy, hooks a bundle/config digest. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Runtime dependency closure

Úplná množina executable, interpreter/dynamic linker, shared libraries, certificates, DNS/NSS, timezone/locale, user metadata, writable paths a helperov potrebných na spustenie final-stage processu. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Runtime isolation subject

Presná identita container process a policy kompozície zahŕňajúca host/runtime, namespace IDs, cgroup, UID/GID mappings, capability sets, `no_new_privs`, seccomp, LSM, mounts, devices a entrypoint. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md).

## Runtime process contract — image

Vzťah medzi effective entrypoint, command/arguments, PID 1, signal a exit behaviorom, runtime userom, working directory, health/readiness oracle a required filesystem/dependency paths. Pozri [Dockerfile](docs/08-container-fundamentals-and-docker/dockerfile.md).

## Runtime socket authority

Host-admin-like authority získaná accessom ku container-engine socketu, ktorá často umožňuje vytvárať workloads s ľubovoľnými mounts, devices, capabilities alebo host namespace accessom. Pozri [Namespaces, cgroups a capabilities](docs/08-container-fundamentals-and-docker/namespaces-cgroups-capabilities.md) a [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Runtime socket exposure

Sprístupnenie container-engine API socketu workloadu, ktoré často umožňuje vytvárať privileged containers, mounts alebo inak ovládať host a predstavuje host-admin trust boundary. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Sandboxed container runtime

Runtime model pridávajúci medzi container workload a host kernel ďalšiu isolation vrstvu, napríklad user-space kernel alebo lightweight virtual machine. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Seccomp profile — container

System-call filter policy aplikovaná na container processes s cieľom znížiť dostupný host-kernel attack surface. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Security exception subject — container

Časovo obmedzená výnimka viazaná na exact workload/runtime subject, environment, bypassovaný control, risk, ownera, compensating controls, expiration a removal/revalidation trigger. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Selected build target

Explicitne zvolený final, test, development, debug alebo artifact stage, ktorého identita musí byť súčasťou release subjectu a publication policy. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Service endpoint generation — container networking

Versionovaný stav service discovery inventory viažuci stable workload identities, addresses, readiness, eligibility a draining/removal state tak, aby stale alebo recyklovaná IP nebola považovaná za správny endpoint. Pozri [Container networking](docs/08-container-fundamentals-and-docker/container-networking.md).

## Shared kernel

Model, v ktorom viac host a container processes používa ten istý kernel, hoci môže mať odlišné namespace views a resource limits. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Single-writer storage

Storage contract povoľujúci v danom čase iba jedného aktívneho writer-a, ktorý potrebuje scheduling, attachment alebo fencing controls na zabránenie concurrent corruption. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Snapshot lease — container runtime

Referencia alebo pin chrániaci unpacked content a snapshots používané aktívnym pullom, buildom alebo containerom pred garbage collection počas ich lifecycle-u. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Snapshot subject — container filesystem

Runtime-specific unpacked representation verified image layers, z ktorej sa vytvorí root filesystem a nad ktorú sa pridá per-container writable layer. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).

## Split-writer incident

Failure stav, v ktorom viac processov alebo nodes súčasne verí, že má authoritative write authority nad rovnakou persistent data identity, často po partitione alebo failover-e bez fencing-u. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Stage DAG subject

Rekonštruovateľná identita multi-stage graphu zahŕňajúca stage names, base/input subjects, dependency edges, selected targets, platform branches, cache outcomes a cross-stage artifact transfers. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Stage-output secret incident

Incident, pri ktorom secret vložený alebo odvodený v build stage-i prejde cez generated artifact, broad alebo narrow `COPY --from`, cache či export do final image-u; recovery zahŕňa revocation aj clean graph rebuild. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Storage attachment subject

Rekonštruovateľná identita backend volume/objectu, node/device pathu, filesystem UUID, host a container mountov, options, topology a active writer lease-u. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Storage fencing

Mechanizmus zabezpečujúci, že starý alebo izolovaný writer už nemôže zapisovať na shared storage pred aktiváciou nového writer-a. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Subject-bound referrer — OCI

Signature, provenance, SBOM alebo iný related artifact, ktorého dôkazný význam je explicitne viazaný na konkrétny image index alebo platform manifest digest. Pozri [OCI image a runtime standards](docs/08-container-fundamentals-and-docker/oci-image-runtime-standards.md).

## Subject-bound security evidence inventory

Očakávaná množina signature, provenance, SBOM, scan, runtime-policy, identity, network/storage a exception evidence, ktorá musí byť validná pre exact artifact a workload subject; missing alebo invalid evidence nie je pass. Pozri [Registries](docs/08-container-fundamentals-and-docker/registries.md) a [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Subject-bound test stage

Test stage verdict viazaný na exact source, immutable inputs, platform, build artifact digest a final image subject, nie iba na názov stage-u alebo úspech nesúvisiaceho pipeline jobu. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## Target publication policy

Policy overujúca, že production reference publikuje povolený named target s expected final base, user, content, metadata, platform evidence a artifact lineage, nie development alebo debug stage. Pozri [Multi-stage builds](docs/08-container-fundamentals-and-docker/multi-stage-builds.md).

## tmpfs mount — container

Memory-backed temporary filesystem pripojený do containeru s lifecycle viazaným na runtime a potrebným explicitným size, memory a permissions limitom. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Unknown Docker operation outcome

Failure stav, keď klient po timeoute alebo connection loss nevie, či Engine API mutation neprebehla, skončila partial object side effects alebo úspešne vytvorila task/process; pred retry vyžaduje object-task-runtime reconciliation. Pozri [Docker architecture](docs/08-container-fundamentals-and-docker/docker-architecture.md).

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

## Workload identity subject — container

Rekonštruovateľná short-lived authorization identity viazaná na workload a environment, s audience, scopes, token epoch/expiration, issuance a use auditom. Pozri [Container security](docs/08-container-fundamentals-and-docker/container-security.md).

## Workload isolation subject

Rekonštruovateľná identita workloadu a jeho zvolenej VM/container boundary zahŕňajúca release/image, host/guest kernel, runtime config, resource policy, network endpoint, persistent-state owner a isolation class. Pozri [Containers vs. virtual machines](docs/08-container-fundamentals-and-docker/containers-vs-virtual-machines.md).

## Writer epoch — container storage

Monotónna alebo fencing-aware generácia authoritative writera používaná na odmietnutie stale processu alebo node-u po failover-e a na koreláciu records s konkrétnou write authority. Pozri [Container storage](docs/08-container-fundamentals-and-docker/container-storage.md).

## Writable layer — container

Dočasná zapisovateľná filesystem vrstva konkrétnej container instance umiestnená nad read-only image layers, ktorej lifecycle je typicky viazaný na container. Pozri [Images, layers a copy-on-write](docs/08-container-fundamentals-and-docker/images-layers-copy-on-write.md).