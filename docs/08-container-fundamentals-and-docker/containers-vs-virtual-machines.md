# Containers vs. virtual machines

Container a virtual machine sú dve odlišné odpovede na otázku, **kde má byť runtime isolation boundary**. Virtual machine dostane virtualizovaný hardware a vlastný guest kernel. Linux container zostáva skupinou host procesov, ktoré zdieľajú host kernel, ale dostanú izolované views, resource controls a security policy.

Rozhodnutie preto nemá začínať zoznamom výhod a nevýhod. Má sledovať celý workload lifecycle:

```text
workload intent a threat model
→ vybraná isolation boundary
→ immutable machine/image subject
→ runtime instance creation
→ resource, network, storage a identity attachment
→ process start a readiness
→ observation a policy enforcement
→ patch, replacement alebo in-place recovery
→ persistent-state a incident closure
```

Container ani VM nie sú samy osebe application architecture. Obe sú execution boundaries, ktoré musia byť zosúladené s identity, persistence, networking, security a recovery modelom workloadu.

## 1. Atlas workload subject

Atlas Payments release `3.13.0` beží v cloud modeli:

```text
physical cloud host
→ hypervisor
→ worker VM node-17
→ Linux guest kernel 6.12
→ container runtime
→ Atlas Payments container AP-313-07
```

Rekonštruovateľný runtime subject obsahuje:

```text
service: Atlas Payments
release: 3.13.0
image index digest: IDX313
platform manifest: linux/amd64 MAMD313
worker VM identity: i-node-17
VM image: node-os-2026.07.2
host/guest kernel: 6.12.x
container runtime configuration: RC882
container instance: AP-313-07
runtime config generation: C44
secret epoch: SE02
persistent data owner: managed PostgreSQL cluster DB17
network endpoint: payments.prod.example
resource policy: 2 CPU / 2 GiB / pids 512
isolation class: internal trusted service
```

Úspešný outcome nie je iba „container je running“ alebo „VM je powered on“. Úspech znamená:

```text
správny artifact beží na kompatibilnej platforme
+ zvolená isolation boundary zodpovedá threat modelu
+ process je ready a reachable
+ limits neporušujú workload SLO
+ business data prežijú replacement runtime instance
+ patch a recovery zachovajú identity a audit
```

## 2. Process, container a VM

### Bežný host process

Process má vlastný virtual address space, file descriptors a execution state, ale bez ďalších controls zdieľa host kernel, mount tree, network stack, process view a resource pool.

### Linux container

Container runtime vytvorí process alebo process group a zostaví jeho execution context:

```text
image root filesystem
+ namespaces
+ cgroup placement
+ credentials/capabilities
+ seccomp a LSM policy
+ mounts, devices a networking
+ entrypoint
→ isolated host process tree
```

Z pohľadu kernelu sú to stále host processes. Container image typicky neprináša kernel, bootloader ani vlastný virtual hardware.

### Virtual machine

Hypervisor poskytne virtual hardware:

```text
physical CPU/memory/devices
→ hypervisor isolation
→ virtual CPU, memory, disk a NIC
→ guest kernel boot
→ guest userspace a services
→ application process
```

Guest môže používať inú kernel verziu alebo OS family než host, ak to podporuje hypervisor a architecture.

## 3. Isolation boundary ako hlavný rozdiel

### Container boundary

Container zdieľa kernel s ostatnými containers a host procesmi. Izolácia závisí od koordinácie:

- namespaces;
- cgroups;
- user a process credentials;
- capability sets;
- seccomp;
- SELinux alebo AppArmor;
- mount/device policy;
- runtime a host hardening.

Kernel vulnerability, privileged mode, runtime socket alebo writable host mount môže boundary výrazne oslabiť.

### VM boundary

VM pridáva guest-kernel a hypervisor boundary. Kompromitovaná aplikácia najprv zasiahne guest OS; pre priamy zásah hosta alebo inej VM musí útočník prekonať ďalšiu virtualization boundary.

VM však nie je automaticky bezpečná. Guest image, hypervisor, virtual devices, management plane, identities a network stále potrebujú hardening.

### Dôsledok

```text
shared-kernel container
→ menší overhead a rýchlejší lifecycle
→ väčší spoločný kernel blast radius

VM s guest kernelom
→ silnejšia a samostatnejšia boundary
→ vyšší per-instance overhead a širší OS lifecycle
```

## 4. Containers vo VMs

Cloud platforms často kombinujú obe vrstvy:

```text
hypervisor/VM
→ izoluje node alebo tenant failure domain

container
→ balí a spúšťa application workload
```

Atlas používa VM node ako infrastructure a kernel boundary a container ako replaceable application unit. To však znamená dva patch a observation lifecycles:

- cloud host/hypervisor;
- worker VM guest OS/kernel;
- container runtime;
- application image a config;
- application process.

Green container health nepreukazuje zdravý node kernel. Green VM state nepreukazuje application readiness.

## 5. Packaging identity

### VM image

Machine image typicky obsahuje bootovateľný systém:

- kernel alebo boot artifacts;
- guest userspace;
- init a system services;
- drivers a agents;
- application alebo container runtime podľa modelu.

### Container image

Container image obsahuje application userspace artifact a runtime defaults:

- executable a libraries;
- filesystem layers;
- user;
- environment defaults;
- entrypoint a command;
- labels a platform metadata.

Image je template. Runtime container je:

```text
exact image manifest
+ runtime config
+ mounts/secrets/network/limits
+ process state
+ writable layer
```

Preto dve containers z rovnakého image digestu môžu mať odlišný effective runtime state.

## 6. Kernel compatibility a portability

Container image štandardizuje userspace artifact, nie celý machine environment.

Runtime compatibility závisí od:

- OS/kernel family;
- CPU architecture a variant;
- required syscalls a kernel features;
- filesystem a mount semantics;
- security profiles;
- devices;
- networking a storage capabilities;
- runtime configuration.

Linux image na Windows alebo macOS typicky beží cez Linux VM alebo inú compatible virtualization vrstvu:

```text
Windows/macOS
→ Linux VM alebo sandbox
→ Linux kernel
→ container runtime
→ Linux container
```

„Runs anywhere“ znamená iba prenositeľnosť v rámci podporovaného platform contractu.

## 7. Runtime creation a startup

VM startup:

```text
virtual hardware
→ guest firmware/boot
→ guest kernel
→ init a system services
→ application
```

Container startup:

```text
resolve/unpack image
→ prepare snapshot/rootfs
→ create namespaces a cgroups
→ attach mounts/network/security policy
→ exec entrypoint
```

Container môže začať rýchlejšie, ale process start nie je readiness. Atlas po starte ešte:

- načíta secret epoch;
- otvorí database pool;
- vykoná compatibility check;
- zahreje cache;
- začne počúvať;
- prejde readiness transaction.

Runtime state preto rozlišuj:

```text
created
started
alive
ready
serving
healthy under load
terminating
deleted
```

## 8. Resource model

Container zdieľa host resources a cgroups riadia accounting a limits. VM má virtual CPUs a memory, ale host/hypervisor môže používať overcommit a shared I/O.

Atlas container policy:

```text
CPU weight: relative scheduling priority
CPU quota: maximum time budget
memory.max: 2 GiB
pids.max: 512
I/O/network: shared node resources
```

Limit nie je rezervácia. Workload s memory limitom stále môže trpieť CPU alebo I/O contention. VM s 4 vCPU stále môže trpieť hypervisor steal alebo noisy-neighbor storage latency.

Observation musí korelovať vrstvy:

```text
application latency
↔ container cgroup throttling/OOM
↔ guest kernel pressure
↔ VM scheduling/steal
↔ physical host/storage/network
```

## 9. Process lifecycle a PID 1

Container runtime sleduje hlavný process. Ak PID 1 skončí, container lifecycle sa typicky ukončí.

PID 1 potrebuje:

- prijímať a forwardovať termination signals;
- zbierať child processes;
- ukončiť sa predvídateľným exit code-om;
- neoddeľovať daemon od lifecycle ownera.

VM má init systém spravujúci viac nezávislých services. Container nemusí mať iba jeden process, ale potrebuje jeden jasný lifecycle contract.

## 10. Network identity

VM typicky dostane stabilnejšiu virtual NIC identity. Container môže dostať krátkodobú network namespace a ephemeral IP.

Stable service identity preto nemá byť jedna container IP:

```text
container instances
→ service discovery/load balancer
→ stable service endpoint
```

Atlas DNS a load balancer smerujú na verified ready instances. Replacement container môže mať inú IP, ale musí zachovať service release a endpoint contract.

## 11. Persistence boundary

Container writable layer je viazaná na runtime instance. Je vhodná pre:

- temporary files;
- caches;
- ephemeral runtime state;
- replaceable generated data.

Nenahraditeľné dáta patria mimo nej:

- managed database;
- persistent volume;
- object storage;
- external state service;
- explicitný backup/recovery systém.

Stateful application môže bežať v containeri. „Ephemeral container“ znamená, že runtime instance nie je jediný vlastník business dát.

VM disk môže prežiť guest reboot, ale tiež potrebuje explicitný lifecycle. Machine snapshot nie je automaticky application-consistent database backup.

## 12. Configuration a immutable replacement

Container model preferuje:

```text
source/config change
→ build exact image
→ test/scan/sign
→ deploy new runtime instances
→ verify
→ remove old instances
```

Interactive patch v running containeri vytvorí snowflake state:

- zmena nie je v image digest-e;
- replacement ju odstráni;
- image scanner ju nevidí;
- recovery je neauditovateľný.

VM môže používať image replacement alebo in-place patching. Obe stratégie potrebujú explicitnú ownership a rollback policy.

## 13. Patching dvoch vrstiev

Container rebuild opraví userspace packages v image. Neopraví host/guest kernel, ktorý container zdieľa.

Atlas patch lifecycle:

```text
application/base-image vulnerability
→ rebuild MAMD313 successor
→ redeploy containers

kernel/runtime vulnerability
→ patch alebo replace worker VM image
→ drain workloads
→ create new node
→ reschedule exact application images
```

Ak sa patchne iba application image, kernel risk môže zostať. Ak sa patchne iba node, vulnerable image môže byť znova spustený.

## 14. Security a blast radius

Container risk rastie pri:

- privileged mode;
- broad capabilities;
- host PID/network namespace;
- runtime socket mount;
- writable host root mount;
- raw device access;
- unconfined seccomp/LSM;
- shared sensitive workloads na jednom kernel boundary.

VM risk zahŕňa:

- guest compromise;
- virtual-device alebo hypervisor vulnerability;
- management-plane compromise;
- shared storage/network;
- stale guest OS;
- broad cloud identity.

Citlivý multi-tenant workload môže potrebovať dedicated VM, microVM alebo sandboxed runtime aj vtedy, keď application packaging zostáva container-based.

## 15. Worked failure: privileged container zrušil očakávanú boundary

Atlas support tool potreboval čítať host logs. Tím použil:

```text
privileged container
+ host root filesystem mounted writable
+ container runtime socket mounted
```

Predpoklad bol „stále je to container, takže host je izolovaný“.

Mechanizmus:

```text
workload dostane široké kernel capabilities a devices
→ vidí host filesystem
→ runtime socket umožní vytvárať ďalšie privileged workloads
→ container compromise sa mení na node compromise
→ všetky workloads na node zdieľajú blast radius
```

Správny návrh používa narrow read-only log path, dedicated identity, minimum capabilities, oddelený support workflow alebo dedicated node podľa rizika.

## 16. Worked failure: business dáta boli vo writable layeri

Atlas export worker zapisoval pending reconciliation records do `/var/lib/atlas/pending`. Path nebola volume.

```text
container AP-313-07 spracuje 8 000 records
→ node drain odstráni container
→ writable layer sa odstráni
→ nový container nemá pending ledger
→ export a database stav sa rozídu
```

Container replacement fungoval presne podľa lifecycle-u. Chyba bola v persistence contracte.

Recovery vyžaduje reconstruct/reconcile records zo zdrojového systému. Skorší control je explicitný data inventory, persistent owner a replacement test.

## 17. Worked failure: running sa zamieňalo s ready

Container process sa spustil za dve sekundy, ale database migration compatibility check trval 40 sekúnd. Load balancer pridal instance ihneď po process start-e.

```text
process exists
→ platform označí instance available
→ traffic príde pred dependency readiness
→ requests zlyhávajú
```

Readiness musí testovať používateľsky významný precondition, nie iba PID existenciu.

## 18. Worked failure: VM image a container image mali rozdielnych owners bez contractu

Worker VM image obsahovala runtime version R7. Application image vyžadovala runtime/kernel feature R8, ale scheduler kontroloval iba CPU architecture.

```text
image manifest je linux/amd64
→ node je tiež amd64
→ deployment prejde platform selection
→ required kernel/runtime feature chýba
→ process zlyhá pri štarte
```

Platform contract potrebuje viac než OS/architecture: podporovaný kernel, runtime features a security policy.

## 19. Causal troubleshooting walkthrough: application funguje vo VM, ale nie v containeri

Atlas binary funguje ako systemd service v testovacej VM. Rovnaký binary v containeri skončí po štarte s `permission denied` a health endpoint nevznikne.

### 1. Zafixuj runtime subject

Zaznamenaj:

- image index a platform manifest digest;
- container config, user, entrypoint a arguments;
- host/guest kernel a runtime version;
- namespace, cgroup, capability, seccomp a LSM profile;
- mounts, ownership a read-only flags;
- effective environment/secrets;
- network a port binding;
- process exit code, audit events a runtime logs.

### 2. Súťažiace hypotézy

1. Binary alebo interpreter nemá execute permission.
2. Dynamic library alebo loader chýba v image.
3. Process beží pod iným UID/GID a nevie čítať config.
4. Root filesystem je read-only a aplikácia zapisuje do implicitného pathu.
5. Capability potrebná na bind alebo syscall bola odstránená.
6. Seccomp blokuje syscall.
7. SELinux/AppArmor blokuje file alebo socket operation.
8. Architecture alebo libc nie je compatible.
9. Entrypoint shell neforwarduje argumenty alebo signal.
10. Service počúva iba na `127.0.0.1` v container namespace.
11. Resource limit ukončí process pred readiness.
12. Mounted config/secret má inú hodnotu než VM file.

### 3. Diskriminačné observation points

- exact image filesystem a dynamic linker inspection;
- `stat`, UID/GID a mount flags;
- `/proc/<pid>/status` capability sets;
- seccomp/LSM audit denials;
- runtime spec/config;
- process syscall/exit evidence podľa policy;
- socket bind address v container network namespace;
- cgroup memory/CPU/PID events;
- redacted effective config digest;
- porovnanie VM a container execution identities.

### 4. Containment

Nezapínaj privileged mode ani globálne nevypínaj SELinux/AppArmor. Zastav rollout a zachovaj failed container metadata, image digest a host audit logs.

### 5. Recovery

- missing library/interpreter → oprav image build a rebuildni exact artifact;
- UID/permissions → nastav explicitný user a file ownership;
- writable-path assumption → pridaj bounded writable mount alebo oprav application path;
- capability gap → pridaj iba potrebnú capability;
- seccomp/LSM denial → uprav narrow policy podľa konkrétnej operation;
- bind address → počúvaj na intended interface a zachovaj network policy;
- resource failure → oprav limit alebo application usage podľa evidence;
- config mismatch → zosúlaď versionovaný runtime contract.

### 6. Over pôvodný outcome

Nový image/runtime subject musí prejsť process start, readiness, business transaction, graceful termination, replacement a second-instance test bez privileged bypassu.

### 7. Posuň control skôr

Pridaj containerized integration test s production-like user, read-only rootfs, seccomp/LSM, resource limits, mounted config a readiness oracle.

## 20. Rozhodovací rámec

Vyber boundary podľa otázok:

1. Potrebuje workload vlastný kernel alebo inú OS family?
2. Aký tenant a kernel blast radius je prijateľný?
3. Aké capabilities, devices a host mounts potrebuje?
4. Je application pripravená na process-oriented replacement?
5. Kde je authoritative persistent state?
6. Aký startup a readiness čas potrebuje?
7. Kto patchuje application userspace, runtime, guest kernel a hypervisor?
8. Aký node/workload identity a attestation model je potrebný?
9. Ako sa budú zbierať logs po zániku instance?
10. Potrebuje workload container vo VM, dedicated VM, microVM alebo sandbox?

## 21. Referenčné pravidlá

- Container je izolovaný host process model, nie mini-VM.
- VM virtualizuje hardware a prináša guest kernel boundary.
- Containers vo VMs kombinujú dve boundaries a dva patch lifecycles.
- Image identity a runtime effective state sú odlišné subjects.
- OS/architecture compatibility nie je celý platform contract.
- Process started nie je workload ready.
- Resource limit nie je automaticky rezervácia ani SLO.
- Stable service endpoint nemá závisieť od jednej ephemeral container IP.
- Writable layer nie je jediný persistent-state owner.
- Runtime patch v containeri vytvára snowflake state.
- Container rebuild neopraví host kernel.
- Privileged mode, runtime socket a host mounts zásadne menia trust boundary.
- Recovery začína identitou failure vrstvy, nie automatickým zvýšením privileges.

## 22. Kontrolné otázky

1. Kde leží hlavná isolation boundary containeru a VM?
2. Prečo container image typicky neobsahuje kernel?
3. Aké dva lifecycles vzniknú pri containers vo VMs?
4. Ako sa líši image subject a runtime container subject?
5. Prečo `running` nie je to isté ako `ready`?
6. Prečo memory alebo CPU limit nie je garantovaná rezervácia?
7. Kde majú byť dáta, ktoré musia prežiť replacement?
8. Prečo privileged container môže znamenať node compromise?
9. Ako sa líši patchovanie image a worker kernelu?
10. Aké observation points odlíšia filesystem, privilege, platform a resource failure?

## Glossary impact

Relevantné pojmy: workload isolation subject, container boundary, VM boundary, shared-kernel blast radius, guest-kernel boundary, runtime container subject, platform compatibility contract, process readiness boundary, container replacement lifecycle, writable-layer persistence failure, layered patch lifecycle, privileged-boundary collapse, microVM a sandboxed runtime.

## Oficiálna dokumentácia

- [What is Docker](https://docs.docker.com/get-started/docker-overview/)
- [What is a container](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)
- [Open Container Initiative](https://opencontainers.org/about/overview/)
- [OCI Runtime Specification](https://specs.opencontainers.org/runtime-spec/)
- [Linux namespaces](https://docs.kernel.org/admin-guide/namespaces/index.html)
- [Linux cgroup v2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Terraform vs. Ansible](../07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Namespaces, cgroups a capabilities →](namespaces-cgroups-capabilities.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
