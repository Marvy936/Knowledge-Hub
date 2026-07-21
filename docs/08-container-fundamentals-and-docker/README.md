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

Nasledujúci blok doplní namespaces/cgroups/capabilities v container kontexte, OCI image a runtime standards, image layers, registries, networking, storage a security. Potom sekcia prejde na Docker architecture, Dockerfile, BuildKit/Buildx, Compose a troubleshooting.

## Cieľ zvládnutia

Po dokončení aktuálneho bloku má byť možné:

- vysvetliť container ako izolovaný process alebo skupinu procesov, nie ako malú VM,
- porovnať shared-kernel container model s hardware virtualization a guest kernel modelom VM,
- rozlíšiť isolation, density, startup, portability, patching a recovery trade-offy,
- vysvetliť úlohu namespaces, cgroups, capabilities, seccomp a mandatory access controlu,
- rozlíšiť container image od runtime container instance,
- vysvetliť ephemeral writable layer a potrebu explicitného persistence modelu,
- navrhnúť základný process, networking, storage a configuration lifecycle containeru,
- vysvetliť, prečo Linux containers na Windows/macOS často používajú Linux VM,
- identifikovať riziká privileged containers, host mounts a runtime socketu,
- rozhodnúť, kedy použiť VM, container alebo containers vo VM.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Containers vs. virtual machines | Learning | L2 |
