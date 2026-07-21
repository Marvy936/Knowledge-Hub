# Container Fundamentals and Docker

Táto sekcia vysvetľuje containers od Linux process isolation a OCI standards až po Docker Engine, images, networking, storage, security, Dockerfile, Compose, BuildKit a troubleshooting. Cieľom nie je memorovať Docker CLI príkazy, ale rozumieť kernel, image, runtime, build, distribution a lifecycle modelu.

Containers nadväzujú na Linux namespaces, cgroups, capabilities, networking, filesystems, artifact versioning, registries, CI/CD a Infrastructure as Code. Docker je konkrétna platforma a toolchain nad širšími container a OCI princípmi.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Linux and Systems](../01-linux-and-systems/README.md),
- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [CI/CD and Release Engineering](../05-ci-cd-and-release/README.md),
- [GitLab](../06-gitlab/README.md),
- [Infrastructure as Code and Configuration Management](../07-infrastructure-as-code-and-configuration-management/README.md).

## Odporúčané poradie

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

Posledný blok sekcie doplní environment variables a health checks, Docker Compose, BuildKit a Buildx a systematické Docker troubleshooting.

## Cieľ zvládnutia

Po dokončení aktuálneho bloku má byť možné:

- vysvetliť container ako izolovaný process alebo skupinu procesov, nie ako malú VM,
- porovnať shared-kernel container model s hardware virtualization a guest-kernel modelom VM,
- rozlíšiť isolation, density, startup, portability, patching a recovery trade-offy,
- vysvetliť namespaces ako virtualizované views, cgroups ako resource-control hierarchy a capabilities ako jemnejší privilege model,
- rozlíšiť PID, mount, network, user a cgroup namespace a ich security limity,
- diagnostikovať PID 1, signal forwarding, CPU throttling, cgroup OOM, PID exhaustion a capability/seccomp/LSM denials,
- vysvetliť OCI Image, Runtime a Distribution Specification ako samostatné interoperability contracts,
- rozlíšiť descriptor, manifest, image config, image index, layers, runtime bundle a low-level runtime,
- pracovať s tagom ako mutable pointerom a digestom ako immutable content identity,
- vysvetliť multi-platform image a rozdiel medzi index digestom a platform-specific manifest digestom,
- vysvetliť layered filesystem, copy-on-write, copy-up, whiteouts a per-container writable layer,
- navrhnúť image build ordering, cache a persistence model bez runtime mutation a secret leakage v layers,
- rozlíšiť registry, repository, manifest, blob, tag a digest reference,
- navrhnúť registry authentication, scoped authorization, immutability, retention, replication, garbage collection a air-gapped promotion,
- zachovať signatures, SBOM a provenance artifacts pri promotion alebo mirroringu,
- vysvetliť network namespace, veth pair, bridge, routes, NAT, port publishing a DNS/service-discovery model,
- diagnostikovať bind address, firewall/NAT, MTU, conntrack, IPv4/IPv6 a return-path failures,
- rozlíšiť writable layer, volume, bind mount, tmpfs, local/block/network/object storage a ich lifecycle,
- navrhnúť stateful container workload s explicitnou data identity, access mode, initialization, backup, restore a fencing policy,
- vysvetliť rozdiel medzi crash-consistent snapshotom a application-consistent backupom,
- navrhnúť defense-in-depth container security baseline od source/build/registry až po runtime a host,
- používať non-root/rootless model, capability drop, seccomp, SELinux/AppArmor, read-only root filesystem, resource limits a network segmentation,
- chrániť runtime socket, devices, secrets a workload identities a vykonať bezpečný rebuild/replace patch lifecycle,
- rozhodnúť, kedy shared-kernel boundary nestačí a workload potrebuje VM, microVM alebo sandboxed runtime,
- vysvetliť Docker client-server architecture, Docker contexts, Engine API, `dockerd`, containerd, runtime shim a OCI runtime responsibilities,
- popísať `docker run` lifecycle od image resolution cez snapshot, network a mounts až po PID 1,
- chrániť Docker socket, remote API a daemon host ako privilegovanú platformovú boundary,
- rozlíšiť Docker Engine, Docker Desktop, rootful a rootless execution model,
- navrhnúť Dockerfile s kontrolovaným base image-om, non-root runtime, správnym `ENTRYPOINT`/`CMD`, signals a metadata,
- rozlíšiť build-time `RUN`/`ARG`/secret mounts od runtime `CMD`/`ENTRYPOINT`/`ENV`,
- používať `COPY`, ownership, permissions, package installation a image labels bez secret leakage a nejasnej reproducibility,
- vysvetliť build context, context root, `.dockerignore`, named contexts a Git context trust boundary,
- navrhnúť instruction ordering, layer cache, cache mounts a external cache bez correctness dependency alebo cache poisoning,
- diagnostikovať cache invalidation a vytvoriť clean-room build/reproducibility kontrolu,
- používať multi-stage builds na oddelenie build, test, artifact, development a final runtime stages,
- preukázať, že release image pochádza z testovaného graphu a obsahuje iba narrow runtime artifacts,
- diagnostikovať dynamic linker, architecture, `scratch`/distroless a multi-platform build problémy,
- rozlíšiť Docker named/anonymous volume, bind mount a tmpfs podľa ownershipu, portability a persistence modelu,
- riešiť mount obscuring, UID/GID, user namespaces, SELinux/AppArmor labels, bind propagation a Docker Desktop file sharing,
- navrhnúť volume backup, migration, access-mode, fencing a cleanup lifecycle,
- rozlíšiť Docker network driver, user-defined bridge, embedded DNS, network alias a host network mode,
- vysvetliť `HOST_PORT:CONTAINER_PORT`, bind address a rozdiel medzi `EXPOSE` a publishingom,
- diagnostikovať Docker bridge, firewall/NAT, port collision, MTU, conntrack, DNS a IPv4/IPv6 connectivity.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Containers vs. virtual machines | Learning | L2 |
| Namespaces, cgroups a capabilities | Learning | L2 |
| OCI image a runtime standards | Learning | L2 |
| Images, layers a copy-on-write | Learning | L2 |
| Registries | Learning | L2 |
| Container networking | Learning | L2 |
| Container storage | Learning | L2 |
| Container security | Learning | L2 |
| Docker architecture | Learning | L2 |
| Dockerfile | Learning | L2 |
| Build context a layer cache | Learning | L2 |
| Multi-stage builds | Learning | L2 |
| Volumes a bind mounts | Learning | L2 |
| Docker networks a port publishing | Learning | L2 |