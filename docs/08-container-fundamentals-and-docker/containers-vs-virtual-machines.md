# Containers vs. virtual machines

Containers a virtual machines izolujú workloads od host systému a od seba navzájom, ale používajú odlišnú virtualization boundary. Virtual machine virtualizuje hardware a spúšťa vlastný guest kernel. Linux container je izolovaný proces alebo skupina procesov zdieľajúca kernel hosta, pričom používa namespaces, cgroups a ďalšie kernel security controls.

Kontajnery nenahrádzajú virtuálne stroje vo všetkých prípadoch. Často sa používajú **vo vnútri VM**, čím sa kombinuje infrastructure isolation hypervisora s application packaging a scheduling modelom kontajnerov.

## 1. Proces bez izolácie

Bežný Linux process zdieľa s ostatnými procesmi hosta:

- kernel,
- process namespace,
- network stack,
- mount tree,
- hostname,
- IPC resources,
- user a group identity model,
- CPU a memory resources podľa scheduler/cgroup konfigurácie.

Process má vlastný virtual address space, file descriptors a runtime state, ale bez ďalších controls vidí veľkú časť spoločného host prostredia.

## 2. Čo je container

Container je runtime jednotka, v ktorej jeden alebo viac procesov beží s izolovaným pohľadom na vybrané systémové resources.

Na Linuxe sa typicky kombinuje:

- namespaces pre izolovaný pohľad,
- cgroups pre accounting a resource control,
- capabilities pre rozdelenie root privileges,
- seccomp pre obmedzenie system calls,
- SELinux alebo AppArmor pre mandatory access control,
- izolovaný root filesystem,
- runtime configuration a lifecycle.

Container nie je samostatný mini-počítač. Z pohľadu kernelu ide stále o host processes.

## 3. Čo je virtual machine

Virtual machine používa virtualizovaný hardware poskytovaný hypervisorom:

```text
physical host
→ hypervisor
→ virtual hardware
→ guest operating system
→ applications
```

Každá VM typicky obsahuje:

- vlastný guest kernel,
- init/service manager,
- system libraries,
- userspace tools,
- vlastný filesystem a virtual devices,
- applications.

Guest OS môže mať inú kernel verziu a často aj inú OS family než host, pokiaľ to podporuje hypervisor a hardware architecture.

## 4. Architektúrne porovnanie

### Virtual machines

```text
Hardware
└── Host/Hypervisor
    ├── VM A
    │   ├── Guest kernel
    │   └── Applications
    └── VM B
        ├── Guest kernel
        └── Applications
```

### Containers

```text
Hardware
└── Host kernel
    ├── Container A processes
    ├── Container B processes
    └── Host processes
```

Container runtime vytvára izolovaný execution context, ale všetky Linux containers na rovnakom hoste používajú ten istý host kernel.

## 5. Isolation boundary

### VM boundary

Hypervisor oddeľuje guest memory, virtual CPU, devices a guest kernel. Útočník po kompromitácii aplikácie musí typicky prekonať guest OS a následne hypervisor boundary, aby ovplyvnil hosta alebo inú VM.

### Container boundary

Container zdieľa kernel s hostom. Kernel vulnerability, nebezpečná capability, privileged container alebo vystavený host socket môže izoláciu výrazne oslabiť.

To neznamená, že containers nie sú bezpečné. Znamená to, že ich isolation model a threat model sú odlišné.

## 6. Shared kernel

Výhody zdieľaného kernelu:

- menší per-workload overhead,
- rýchlejší startup,
- vyššia workload density,
- jednoduchšie distribuovateľné userspace artifacts.

Obmedzenia:

- Linux container potrebuje kompatibilný Linux kernel,
- container nemôže priniesť vlastný kernel feature set nezávisle od hosta,
- kernel attack surface je spoločný,
- host kernel configuration ovplyvňuje všetky containers.

Container image môže obsahovať userspace z inej Linux distribúcie, ale stále používa host kernel.

## 7. Windows a macOS hosty

Linux containers na Windows alebo macOS typicky bežia cez Linux VM alebo inú virtualization vrstvu poskytovanú platformou.

Praktický model:

```text
Windows/macOS
→ lightweight Linux VM
→ Linux container runtime
→ containers
```

Preto „container beží priamo na mojom Windows hoste“ nemusí znamenať, že Linux process používa Windows kernel.

## 8. Startup time

VM startup zahŕňa:

- virtual hardware initialization,
- guest kernel boot,
- init/system services,
- application startup.

Container startup typicky zahŕňa:

- prípravu namespaces/cgroups/filesystem,
- vytvorenie processu,
- spustenie application entrypointu.

Container môže štartovať výrazne rýchlejšie, ale application readiness môže stále trvať dlho kvôli:

- migrations,
- cache warmup,
- dependency checks,
- JIT compilation,
- veľkému image pullu,
- pomalému storage/networku.

Process started nie je to isté ako workload ready.

## 9. Resource overhead

VM potrebuje memory a storage pre guest OS a kernel. Containers zdieľajú host kernel a často používajú copy-on-write image layers.

Vyššia density však neznamená bezplatné resources. Containers stále spotrebujú:

- CPU,
- memory,
- page cache,
- filesystem I/O,
- network bandwidth,
- kernel objects,
- process IDs,
- open files.

Bez requests, limits a observability môže jeden container vyčerpať host resources.

## 10. Resource isolation

Cgroups môžu riadiť alebo účtovať:

- CPU,
- memory,
- I/O,
- process count,
- cpuset placement,
- ďalšie resource controllers podľa kernelu.

Limit nie je automaticky rezervácia. Napríklad CPU limit, CPU request/share a dedicated CPU assignment reprezentujú odlišné scheduling semantics.

VM má typicky explicitne pridelené virtual CPUs a memory, ale hypervisor môže používať overcommit, ballooning alebo shared storage/network resources.

## 11. Packaging model

### VM image

Obsahuje typicky celý bootovateľný guest systém:

- kernel alebo boot artifacts,
- OS userspace,
- system services,
- application.

### Container image

Obsahuje typicky application filesystem a runtime metadata:

- application binaries,
- libraries,
- runtime,
- configuration defaults,
- entrypoint/command,
- image layers.

Container image neobsahuje bežne kernel, ktorý sa použije pri runtime.

## 12. Image nie je container

Image je immutable alebo content-addressed template/artifact. Container je runtime instance image-u s vlastným writable layerom a runtime configuration.

```text
image
→ create runtime instance
→ container process + writable state
```

Z jedného image-u možno vytvoriť viac containers s odlišnými:

- environment variables,
- secrets,
- mounts,
- network identities,
- resource limits,
- commands.

## 13. Filesystem

Container často používa:

- read-only image layers,
- writable container layer,
- volumes,
- bind mounts,
- tmpfs.

Writable container layer je typicky viazaný na lifecycle containeru. Dôležité dáta potrebujú explicitný persistence model.

VM disk sa správa viac ako plný machine filesystem a často prežíva reboot VM, ale aj tam treba riešiť snapshot, backup, replication a replacement lifecycle.

## 14. Persistence

Container je vhodné považovať za replaceable runtime unit:

```text
stop/remove old container
→ create new container from image
```

Persistence patrí mimo ephemeral writable layer:

- managed database,
- object storage,
- persistent volume,
- external state service,
- explicit host/remote mount podľa architektúry.

„Container je ephemeral“ neznamená, že aplikácia nemôže byť stateful. Znamená to, že runtime instance nemá byť jediným vlastníkom nenahraditeľných dát.

## 15. Networking

VM typicky dostáva virtual network interface pripojený k virtual switchu, bridge, overlay alebo cloud networku.

Container môže používať:

- samostatný network namespace,
- virtual ethernet pair,
- bridge,
- host networking,
- overlay alebo CNI model,
- port publishing/NAT.

Container network identity môže byť krátkodobá. Service discovery a stable endpoint nemajú závisieť od jednej ephemeral container IP.

## 16. Process model

Container runtime často sleduje hlavný process ako PID 1 v container PID namespace.

Keď hlavný process skončí, container lifecycle typicky skončí.

Dôsledky:

- aplikácia má správne spracovať signals,
- PID 1 má špecifické signal/reaping správanie,
- background daemon bez foreground processu môže container okamžite ukončiť,
- jeden container nemusí znamenať striktne jeden process, ale potrebuje jasný lifecycle owner.

VM môže prevádzkovať mnoho nezávislých system services pod init systémom.

## 17. Configuration model

VM konfigurácia býva kombináciou:

- machine image,
- cloud-init,
- configuration managementu,
- package managera,
- runtime zmien.

Container configuration sa typicky skladá z:

- immutable image,
- environment-specific variables,
- secrets,
- mounted configuration,
- command/arguments,
- platform policy.

Meniť production container interaktívne cez shell vytvára neauditovaný drift. Oprava má vzniknúť v image alebo deployment configuration a potom sa má vytvoriť nová instance.

## 18. Immutable replacement

Containers podporujú replacement-oriented workflow:

```text
source change
→ build new image
→ test/scan/sign
→ deploy new container instances
→ remove old instances
```

To znižuje in-place configuration drift, ale iba ak:

- image tag/digest je kontrolovaný,
- runtime config je versionovaná,
- persistent state je oddelený,
- old instance nie je ručne upravená,
- rollout a rollback sú definované.

## 19. Security model

Container security zahŕňa viac vrstiev:

- trusted image provenance,
- minimal image content,
- non-root user,
- dropped capabilities,
- read-only root filesystem,
- seccomp,
- SELinux/AppArmor,
- user namespaces,
- resource limits,
- network policy,
- secret handling,
- host hardening,
- runtime patching.

Privileged container alebo mount host root filesystemu môže prakticky zrušiť významnú časť isolation boundary.

VM security zahŕňa:

- hypervisor patching,
- guest OS hardening,
- virtual device exposure,
- image provenance,
- network segmentation,
- guest identity a patch lifecycle.

## 20. Escape a blast radius

### Container escape

Útočník prekročí container isolation a získa access k hostu alebo iným workloads. Riziko zvyšujú:

- privileged mode,
- host PID/network namespace,
- writable host mounts,
- Docker/container runtime socket,
- broad capabilities,
- kernel vulnerabilities.

### VM escape

Útočník prekročí guest/hypervisor boundary. Je typicky odlišnou a silnejšou isolation vrstvou, ale nie absolútnou garanciou.

Citlivé multi-tenant workloads môžu používať kombináciu VM isolation a containers.

## 21. Portability

Container image štandardizuje application userspace artifact, ale portability má podmienky:

- CPU architecture,
- OS/kernel family,
- required kernel features,
- filesystem a security policy,
- runtime configuration,
- external services,
- storage a networking capabilities.

„Runs anywhere“ neznamená bezpodmienečne rovnaký runtime behavior na každej platforme.

Multi-platform images môžu publikovať variants pre viac architectures, ale každý variant je samostatný manifest/image content.

## 22. Observability

Pri VM typicky sleduješ:

- guest OS metrics,
- systemd/services,
- kernel logs,
- hypervisor metrics,
- virtual disk/network.

Pri containers sleduješ:

- container lifecycle,
- process exit code,
- stdout/stderr logs,
- cgroup resource metrics,
- image/digest identity,
- runtime events,
- host kernel pressure,
- orchestrator state.

Container restart môže odstrániť lokálny writable state a starý process context. Logs a traces preto potrebujú external collection.

## 23. Patching

### VM patching

Možnosti:

- in-place package patch,
- reboot,
- image replacement,
- configuration management.

### Container patching

Bežný model:

```text
update base/application dependencies
→ rebuild image
→ scan/test
→ redeploy
```

Patch host kernelu stále vyžaduje host/VM lifecycle, pretože containers ho zdieľajú.

## 24. Backup a recovery

Container image nie je backup application data.

Zálohuj:

- persistent volumes,
- databases,
- object storage,
- runtime configuration/secrets podľa policy,
- image provenance a release metadata.

VM snapshot môže pomôcť pri recovery, ale crash-consistent snapshot celej VM nemusí byť application-consistent backup databázy.

## 25. Typické použitie containers

Containers sú vhodné pre:

- stateless services,
- APIs,
- workers,
- batch jobs,
- CI jobs,
- reproducible development environments,
- microservices,
- stateful services s explicitným persistence modelom,
- platform add-ons a agents podľa orchestration modelu.

## 26. Typické použitie VMs

VMs sú vhodné pre:

- workloads vyžadujúce vlastný kernel alebo OS,
- silnejšiu tenant isolation,
- legacy applications očakávajúce full machine,
- appliance-like software,
- mixed service hosty,
- platform nodes pre container orchestration,
- špecifické kernel modules alebo drivers.

## 27. Containers vo VMs

Najbežnejší cloud model:

```text
physical infrastructure
→ cloud hypervisor
→ VM worker node
→ container runtime
→ application containers
```

Výhody:

- VM ako infrastructure/security boundary,
- container ako application packaging a scheduling unit,
- nezávislý node replacement,
- lepšia multi-workload density vo VM.

Prevádzka však musí sledovať obe vrstvy: guest/host OS aj container platformu.

## 28. MicroVM a sandboxed runtime

Medzi klasickou VM a shared-kernel container izoláciou existujú hybridné modely:

- microVMs,
- sandboxed container runtimes,
- user-space kernels,
- lightweight virtualized pods.

Cieľom je kombinovať rýchlejší startup a container workflow so silnejšou isolation boundary. Trade-offom je overhead, kompatibilita a prevádzková komplexita.

## 29. Density vs. isolation

Rozhodnutie nie je iba technické:

```text
vyššia density
↔ silnejšia isolation
↔ jednoduchšia prevádzka
↔ náklady
```

Jeden veľký shared host môže byť lacnejší, ale zväčšuje blast radius kernel incidentu alebo resource exhaustion.

Viac menších VM boundaries znižuje blast radius, ale zvyšuje infrastructure overhead.

## 30. Rozhodovací rámec

Pýtaj sa:

1. Potrebuje workload vlastný kernel alebo inú OS family?
2. Aká silná musí byť tenant isolation?
3. Aký je akceptovateľný blast radius shared kernelu?
4. Aký startup a scaling čas potrebujeme?
5. Aký je persistence model?
6. Kto patchuje host kernel a guest OS?
7. Je application pripravená na replacement?
8. Aké kernel capabilities alebo devices potrebuje?
9. Ako budeme zbierať logs a metrics po zániku instance?
10. Má workload bežať v containeri vo vnútri VM?

## 31. Anti-patterny

### Container ako malá VM

Inštalovanie SSH, systemd a množstva nesúvisiacich services môže skryť nejasný process lifecycle a image ownership.

### Všetky dáta vo writable layeri

Odstránenie containeru odstráni jedinú kópiu state-u.

### Privileged mode ako univerzálna oprava

Funkčnosť sa dosiahne zrušením veľkej časti isolation boundary.

### `latest` bez digest/release identity

Nie je zrejmé, aký content runtime spustil.

### Ručné patchovanie bežiaceho containeru

Zmena nie je v image a po replacement-e zmizne.

### Predpoklad, že VM automaticky znamená bezpečnosť

Guest OS, images, identities a hypervisor stále potrebujú hardening a patching.

### Predpoklad, že container nemôže byť stateful

Stateful workload je možný, ale potrebuje explicitný storage, identity, backup a scheduling model.

## 32. Troubleshooting

### Container vidí inú kernel verziu než image distribúcia

Je to očakávané: kernel poskytuje host, image poskytuje userspace.

### Application funguje vo VM, ale v containeri nie

Over filesystem paths, PID 1/signals, capabilities, read-only filesystem, port binding, DNS, environment variables a external state.

### Container bol odstránený a dáta zmizli

Dáta boli vo writable layeri bez volume alebo external persistence.

### Container je killed pri load-e

Over cgroup memory limit, host pressure, OOM events, CPU throttling a process count limits.

### Linux image sa nespustí priamo na inom OS

Image potrebuje kompatibilný kernel/runtime alebo virtualization vrstvu.

### VM aj container ukazujú vysoké CPU

Rozlišuj application process usage, cgroup throttling, guest scheduling a hypervisor steal/overcommit.

## 33. Kontrolné otázky

1. Aký je hlavný isolation rozdiel medzi containerom a VM?
2. Prečo container image typicky neobsahuje kernel?
3. Ako namespaces a cgroups prispievajú k container modelu?
4. Prečo Linux containers na macOS/Windows často potrebujú VM?
5. Aký je rozdiel medzi image a containerom?
6. Prečo writable layer nie je vhodný ako jediný persistent storage?
7. Ako sa líši patchovanie containeru a VM?
8. Prečo privileged container zväčšuje blast radius?
9. Kedy je vhodné spúšťať containers vo VMs?
10. Aké limity má tvrdenie o container portability?

## Glossary impact

Relevantné pojmy: container, virtual machine, hypervisor, guest OS, shared kernel, isolation boundary, container image, container runtime, writable layer, workload density, container escape, VM escape, microVM, sandboxed runtime a ephemeral runtime instance.

## Oficiálna dokumentácia

- [What is Docker](https://docs.docker.com/get-started/docker-overview/)
- [What is a container](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/)
- [Open Container Initiative](https://opencontainers.org/about/overview/)
- [OCI Runtime Specification](https://specs.opencontainers.org/runtime-spec/)
- [Linux namespaces](https://docs.kernel.org/admin-guide/namespaces/index.html)
- [Linux cgroup v2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
