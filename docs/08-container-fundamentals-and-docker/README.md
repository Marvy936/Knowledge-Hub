# Container Fundamentals and Docker

Táto sekcia vysvetľuje container ako host-kernelom izolovaný process model a Docker ako konkrétny client–daemon, build, image-distribution, networking a storage toolchain nad Linux a OCI princípmi. Image nie je container, tag nie je immutable release identity, container filesystem nie je persistent data store a `docker run` success nie je application acceptance. Dôveryhodný container lifecycle vzniká až vtedy, keď exact image/index/platform subject, runtime configuration, host/daemon context, namespaces, cgroups, mounts, network path a process identity vedú k overenému technical aj business outcome-u.

Sekcia sa znovu spracúva podľa rovnakého prose-first a practical-example štandardu ako Keycloak a sekcie 5–7. Každá kapitola musí mať dominantný mechanistický lifecycle, konkrétny incidentný chain, reálne Docker/OCI/Linux CLI, Dockerfile, Compose YAML alebo daemon configuration, vysvetlené proof boundaries, competing hypotheses, evidence-preserving containment, authoritative rebuild/recreate recovery a validáciu pôvodnej, zakázanej aj druhej operácie.

## Section-wide container lifecycle

```text
business workload a isolation requirement
→ exact source, image/index/platform a configuration subject
→ trusted builder, Dockerfile frontend, build graph a inputs
→ immutable manifests, layers, config, attestations a registry publication
→ daemon/context, image resolution a platform selection
→ snapshot/root filesystem, namespaces, cgroups, capabilities a LSM policy
→ mounts, network namespace, DNS, routes a published-port rules
→ PID 1, signals, environment, health a application lifecycle
→ logs/events/inspect/kernel evidence
→ rebuild, replace, data restore alebo host/runtime remediation
→ forbidden-path a second-container validation
```

Počas celej sekcie zostávajú explicitne oddelené najmä tieto vrstvy:

- container nie je VM a shared kernel nie je hardware security boundary;
- image manifest/index/config/layers nie sú running process;
- mutable tag nie je digest a index digest nie je platform-specific manifest digest;
- image layer nie je container writable layer ani volume;
- `EXPOSE` nie je port publication;
- container port nie je host port a publish bez host IP môže otvoriť všetky host interfaces;
- process running nie je application ready ani dependency healthy;
- healthcheck result nie je všeobecná readiness/liveness politika;
- Compose source YAML nie je resolved Compose model;
- build cache nie je artifact authority a secret mount nie je image layer;
- Docker context/CLI success nepreukazuje správny daemon host;
- restart, delete alebo prune pred evidence capture môže zničiť root-cause dôkaz;
- ručne opravený running container nie je versionovaný recovery outcome.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Linux and Systems](../01-linux-and-systems/README.md),
- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [CI/CD and Release Engineering](../05-ci-cd-and-release/README.md),
- [GitLab](../06-gitlab/README.md),
- [Infrastructure as Code and Configuration Management](../07-infrastructure-as-code-and-configuration-management/README.md).

## Authoritative poradie — aktívne kapitoly

1. [Containers vs. virtual machines](containers-vs-virtual-machines.md)
2. [Namespaces, cgroups a capabilities](namespaces-cgroups-capabilities.md)
3. [OCI image a runtime standards](oci-image-runtime-standards.md)
4. [Images, layers a copy-on-write](images-layers-copy-on-write.md)
5. [Registries](registries.md)
6. [Container networking](container-networking.md)
7. [Container storage](container-storage.md)
8. [Container security](container-security.md)
9. [Docker architecture](docker-architecture.md)
10. [Dockerfile](dockerfile.md)
11. [Build context a layer cache](build-context-layer-cache.md)
12. [Multi-stage builds](multi-stage-builds.md)
13. [Volumes a bind mounts](volumes-bind-mounts.md)
14. [Docker networks a port publishing](docker-networks-port-publishing.md)
15. [Environment variables a health checks](environment-variables-health-checks.md)
16. [Docker Compose](docker-compose.md)
17. [BuildKit a Buildx](buildkit-buildx.md)
18. [Docker troubleshooting](docker-troubleshooting.md)

Po tejto sekcii nasleduje Kubernetes. Container/OCI subject, runtime process, image pull, network, storage, health a security models vytvoria základ pre Pod sandbox, CRI, probes, Services, volumes, security context a node-level troubleshooting.

## Connected learning scenarios

### `CTR-PAY-80` — správny image tag spustí nesprávny platformový a kernel outcome

Prvý blok spája containers vs. VMs, namespaces/cgroups/capabilities, OCI standards a images/layers/copy-on-write. Atlas Payments publikuje multi-platform tag `payments:10.4`, ale arm64 manifest obsahuje starší binary a privileged runtime configuration pridá broad capabilities. PID 1 používa shell wrapper bez signal forwarding, memory limit je nesprávne interpretovaný a secret odstránený v neskoršej image layer zostáva v predchádzajúcom blob-e.

```text
workload/isolation intent
→ OCI index tag a digest
→ platform manifest/config/layers
→ unpack a runtime bundle
→ namespace/cgroup/capability setup
→ writable snapshot a PID 1
→ signal/resource/security outcome
→ host-kernel a business verification
```

Blok musí odlíšiť VM a shared-kernel threat boundary, image/index/platform identity, namespace view od cgroup control, UID od capability/LSM authority, PID 1 semantics, layer whiteout od blob deletion a writable layer od persistent storage.

### `CTR-PAY-81` — registry, network, storage a security vytvoria distribuovaný runtime incident

Druhý blok spája registries, container networking, container storage a container security. Produkčný host pullne mutable tag z lokálneho mirroru, ktorý má index bez aktuálneho arm64 manifestu. Container dostane bridge network a published management port na všetkých host interfaces; MTU mismatch vytvára partial TLS failures. Databáza zapisuje do container writable layer a privileged diagnostic sidecar má Docker socket aj host filesystem mount.

```text
repository/tag/digest publication
→ registry auth, manifest/blob resolution a replication
→ daemon platform pull
→ network namespace, veth/bridge/routes/NAT/DNS
→ mount a data identity
→ capabilities/seccomp/LSM/device/socket policy
→ runtime and host outcome
→ replacement, restore, revocation a second pull/run
```

Blok uzatvára immutable registry subject, index/platform completeness, exact network observation point, persistent-data lifecycle, backup/restore, least privilege a rozhodnutie, kedy shared-kernel boundary nestačí.

### `CTR-PAY-82` — Docker build vytvorí iný artifact než ten, ktorý prešiel testami

Tretí blok spája Docker architecture, Dockerfile, build context/layer cache a multi-stage builds. CLI používa nesprávny Docker context a buildne na remote privileged daemonovi. Dockerfile používa shell-form `ENTRYPOINT`, package repository bez pinning-u a `ARG` pre secret. Build context obsahuje `.git`, lokálny credential a generated binary; shared cache obnoví stale dependency output. Test stage prejde, final stage však kopíruje artifact z iného builder stage-u a release image nemá runtime library pre arm64.

```text
CLI/context a daemon identity
→ Dockerfile frontend a build context
→ BuildKit/legacy build graph a cache keys
→ build/test/package stages
→ final runtime filesystem/config
→ image/index publication
→ run, signal a dynamic-linker outcome
→ clean rebuild a artifact provenance
```

Blok musí preukázať exact daemon/builder, context inventory, cache correctness versus performance, secret mount versus layer/ARG, `ENTRYPOINT`/`CMD` semantics, test-to-final artifact identity a multi-platform runtime compatibility.

### `CTR-PAY-83` — Compose model je validný, ale mount, port, environment a health semantics sú nesprávne

Štvrtý blok spája volumes/bind mounts, Docker networks/port publishing, environment variables/health checks a Docker Compose. Development bind mount zakryje image directory aj v production profile, UID/GID mismatch znemožní zápis do volume a `0.0.0.0:8080:8080` sprístupní admin endpoint. Compose interpolation vyberie staging database URL a secret z `.env`; `depends_on: service_healthy` rieši iba startup gate, nie neskorší dependency failure. `docker compose up` vytvorí nový project name a tým paralelné networks/volumes.

```text
Compose source, includes/profiles a environment inputs
→ resolved project/service model
→ image, command, environment, mounts a networks
→ create/recreate reconciliation
→ embedded DNS a published-port rules
→ health/startup dependency transition
→ data/runtime/business verification
→ down/remove/backup alebo corrected recreate
```

Blok oddeľuje named volume, bind a tmpfs lifecycle, mount obscuring, host/container UID, `EXPOSE` versus publish, bind address, configuration precedence, process/health/readiness semantics a Compose project identity.

### `CTR-PAY-84` — shared builder a unstructured troubleshooting zničia supply-chain aj incident evidence

Záverečný blok spája BuildKit/Buildx a Docker troubleshooting. Untrusted pull request používa shared privileged builder, exportuje poisoned external cache a získa prístup k SSH/secret mountu. Release pipeline vytvorí multi-platform index, ale testuje iba amd64 a `--load` lokálne sprístupní iba jednu platformu. Produkčný container crashuje; operátor najprv restartne daemon, zmaže container a spustí `docker system prune`, čím odstráni writable-layer, events, inspect subject a build cache potrebné na diagnosis.

```text
builder instance/nodes/driver a trust class
→ LLB/build graph, inputs, secrets a caches
→ per-platform outputs a attestations
→ load/push/export semantics
→ pull/run symptom
→ client/context/daemon/runtime/process/storage/network/kernel evidence
→ competing hypotheses a containment
→ versionovaný rebuild/recreate a second-container validation
```

Sekcia sa uzatvára tým, že release builder, cache, platform manifests, SBOM/provenance a runtime evidence majú explicitnú identity a recovery sa vykonáva rebuildom alebo controlled recreate, nie neauditovanou mutáciou živého containera.

## Cieľ zvládnutia

Po dokončení sekcie má byť možné navrhnúť a diagnostikovať container lifecycle, ktorý:

- rozlišuje shared-kernel container isolation od VM guest-kernel a hardware-virtualization boundary;
- vysvetľuje namespace views, cgroup controls, capabilities, seccomp a SELinux/AppArmor enforcement;
- identifikuje OCI index, platform manifest, config, layers, runtime bundle a running process;
- používa digesty a platform-specific subjects namiesto dôvery v mutable tag;
- chápe copy-on-write, copy-up, whiteouts, writable snapshot a persistent storage boundary;
- zachová signatures, SBOM, provenance a manifest completeness pri registry promotion/mirroringu;
- diagnostikuje veth, bridge, routes, DNS, NAT, firewall, MTU, conntrack a return path;
- navrhuje explicitný data/volume identity, access, backup, restore a fencing lifecycle;
- používa non-root/rootless, capability drop, seccomp, LSM, read-only rootfs, limits a network segmentation;
- chráni Docker socket, daemon API, host mounts, devices a workload credentials;
- vysvetľuje Docker client/context/daemon/containerd/shim/OCI-runtime lifecycle bez zlievania responsibility;
- píše Dockerfile s pinned base subjectom, deterministic package/build inputs, exec-form process modelom a bez secret leakage;
- kontroluje build context, `.dockerignore`, named/Git contexts, cache keys a clean-room build;
- používa multi-stage graph tak, aby final image obsahoval presne testovaný runtime artifact;
- rozlišuje named/anonymous volume, bind mount a tmpfs vrátane ownershipu, obscuring a backupu;
- vysvetľuje user-defined bridge DNS, aliases, host-network tradeoff a `HOST_IP:HOST_PORT:CONTAINER_PORT`;
- riadi environment precedence, required/default/empty semantics a secret exposure;
- interpretuje Docker health ako scoped application signal, nie univerzálny readiness contract;
- overuje resolved Compose model, project identity, profiles, includes, networks, volumes a create/recreate behavior;
- používa BuildKit/Buildx builder classes, multi-platform strategy, cache, secret/SSH mounts, SBOM a provenance;
- zachováva evidence cez `docker context`, `info`, `inspect`, `events`, `logs`, process, mounts, network a kernel observation points;
- opravuje root cause versionovaným rebuild/recreate/restore workflowom a overuje forbidden aj second-container path.

## Revalidation completion gate

Sekcia bude označená `Ready for user review` iba po splnení všetkých podmienok:

1. všetkých 18 authoritative kapitol používa connected Keycloak-style prose a dominantný lifecycle;
2. každá kapitola definuje exact image/index/platform, daemon/context, container/process, network, mount, builder alebo recovery subject;
3. kapitoly obsahujú reálne Linux/Docker/OCI CLI, Dockerfile, Compose YAML, JSON inspection alebo daemon configuration tam, kde to téma umožňuje;
4. každý významný output vysvetľuje, čo preukazuje a čo nepreukazuje;
5. source, build graph, image, registry, pulled platform, container config, effective runtime a business states sa nezlievajú;
6. komplexné failures používajú competing hypotheses, discriminating evidence a evidence-preserving containment;
7. recovery používa authoritative rebuild, republish, recreate, restore alebo host/runtime remediation a overuje forbidden aj second-container path;
8. strict learning-depth audit pre všetkých 18 kapitol je `0/0/0` a practical gate nemá failures;
9. README, navigation, glossary a centrálny review ledger sú synchronizované;
10. čistý PR head bez dočasných workflowov alebo skriptov prejde štandardným documentation workflowom.

## Aktuálny stav revalidácie

| Blok | Kapitoly | Stav |
|---|---:|---|
| `CTR-PAY-80` — isolation, OCI subject a image filesystem | 0/4 | In progress |
| `CTR-PAY-81` — registry, network, storage a security | 0/4 | Not started |
| `CTR-PAY-82` — Docker runtime a image build graph | 0/4 | Not started |
| `CTR-PAY-83` — mounts, Docker networking, configuration a Compose | 0/4 | Not started |
| `CTR-PAY-84` — BuildKit/Buildx a troubleshooting | 0/2 | Not started |

Celkový authoritative stav: **0/18 · In progress**.
