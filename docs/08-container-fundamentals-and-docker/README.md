# Container Fundamentals and Docker

Táto sekcia vysvetľuje containers od Linux process isolation a OCI standards až po Docker images, networking, storage, security, Compose, BuildKit a troubleshooting. Cieľom nie je memorovať Docker CLI príkazy, ale rozumieť kernel, image, runtime, distribution a lifecycle modelu.

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

Nasledujúci blok prejde na Docker implementation vrstvu: Docker architecture, Dockerfile, build context a layer cache, multi-stage builds, volumes/bind mounts, Docker networks/port publishing, environment variables/health checks, Compose, BuildKit/Buildx a troubleshooting.

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
- rozhodnúť, kedy shared-kernel boundary nestačí a workload potrebuje VM, microVM alebo sandboxed runtime.

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