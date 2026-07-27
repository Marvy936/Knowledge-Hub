# Namespaces, cgroups a capabilities

Linux container nevzniká jedným kernel prepínačom. Runtime vytvorí process subject a skladá jeho isolation z viacerých nezávislých mechanizmov:

```text
workload policy a host trust boundary
→ process credentials a user mapping
→ namespace views
→ root filesystem a mounts
→ cgroup placement a resource policy
→ capability sets a no_new_privs
→ seccomp, SELinux/AppArmor a device policy
→ PID 1 start
→ resource/security observations
→ termination a cleanup
```

Každá vrstva odpovedá na inú otázku:

- namespaces: **čo process vidí a v akom kernel context-e?**
- cgroups: **aké resources spotrebúva a aké hranice má?**
- credentials/capabilities: **aké privilegované operácie smie žiadať?**
- seccomp: **ktoré syscalls smie vôbec volať?**
- SELinux/AppArmor a filesystem policy: **smie konkrétnu operáciu vykonať nad konkrétnym objektom?**

Žiadny mechanizmus samostatne netvorí plnú container boundary. Defense in depth vzniká iba z ich konzistentnej kompozície.

## 1. Atlas runtime-isolation subject

Atlas Payments container `AP-313-07` má policy:

```text
host/VM: node-17 / Linux 6.12
runtime instance: AP-313-07
process user in container: UID 10001
host UID mapping: 2010001 podľa user namespace policy
PID namespace: PNS-71
mount namespace/rootfs: MNS-71 / image MAMD313
network namespace: NNS-71
cgroup path: /atlas/payments/AP-313-07
CPU: weight 200, quota 200000/100000
memory.high: 1536 MiB
memory.max: 2048 MiB
pids.max: 512
capabilities: drop ALL, add NET_BIND_SERVICE
no_new_privs: true
seccomp profile: atlas-web-v4
SELinux/AppArmor profile: atlas-payments-prod-v3
writable mounts: /tmp tmpfs, /var/cache/atlas bounded volume
host mounts/devices: none
```

Úspešný isolation outcome:

```text
process vidí iba intended namespace resources
+ nemá neplánované host access paths
+ resource pressure je ohraničený a pozorovateľný
+ potrebné privilegované operácie prejdú
+ zakázané operácie zlyhajú na očakávanej policy vrstve
+ PID 1 ukončí workload korektne
+ teardown odstráni runtime state bez host side effects
```

## 2. Process subject pred namespace-om

Kernel rozhoduje nad processom, nie abstraktným „containerom“. Relevantná identita zahŕňa:

```text
host PID a namespace PID
real/effective/saved UID/GID
user namespace mapping
capability sets
no_new_privs
seccomp mode/filter
LSM label/profile
cgroup membership
mount a network namespace IDs
open file descriptors a inherited handles
```

Dva processes v rovnakom container image môžu mať odlišnú effective authority, ak sa líši runtime policy alebo inherited state.

## 3. Namespace lifecycle

Namespace virtualizuje vybraný kernel view. Runtime typicky:

```text
create/join namespace
→ place initial process
→ configure namespace-specific resources
→ exec workload
→ destroy namespace po zániku posledného membera
```

Dôležité namespaces:

| Namespace | Izolovaný view |
|---|---|
| PID | process IDs a process tree |
| mount | mount table a propagation |
| network | interfaces, routes, sockets a network stack |
| IPC | System V IPC a POSIX queues |
| UTS | hostname/domain name |
| user | UID/GID mappings a capability scope |
| cgroup | viditeľnosť cgroup hierarchy |
| time | podporované clock offsets |

Namespace nie je policy verdict. Samostatný network namespace môže mať route do production database. Mount namespace môže obsahovať writable host root. Isolation view musí byť spojený s explicitným connection a object policy modelom.

## 4. PID namespace a PID 1

Initial process nového PID namespace-u vidí seba ako PID 1. Host ho vidí pod iným PID.

```text
host PID 48291
↔ namespace PID 1
```

PID 1 má špecifické lifecycle povinnosti:

- prijímať a forwardovať signals;
- reaping orphaned children;
- držať foreground lifecycle;
- vracať pravdivý exit code;
- neukončiť sa pred children bez riadenej policy.

Shell wrapper bez `exec` môže zostať PID 1:

```sh
#!/bin/sh
/opt/atlas/bin/server
```

`SIGTERM` dostane shell, ale application ho nemusí dostať. Lepšie:

```sh
#!/bin/sh
exec /opt/atlas/bin/server
```

alebo minimal init, ak workload vytvára children a nevie ich reaping riešiť sám.

Observation:

```bash
ps -eo pid,ppid,stat,comm
cat /proc/1/status
```

## 5. Mount namespace a root filesystem

Runtime pripraví merged image rootfs a namespace-specific mounts:

```text
read-only image snapshot
+ writable layer podľa policy
+ /proc, /dev, /sys masks
+ volumes/bind mounts/tmpfs
+ mount propagation flags
→ process root filesystem view
```

Risk nie je iba „je rootfs writable“. Kritické sú paths, ktoré obchádzajú image boundary:

- host `/` alebo `/etc` bind mount;
- container runtime socket;
- writable `/proc` alebo `/sys` subtree;
- device nodes;
- shared propagation, ktorá prenesie mount na host;
- service-account alebo cloud credential paths;
- unbounded temporary filesystem.

Read-only rootfs znižuje mutation surface, ale workload potrebuje explicitné writable contracts:

```text
/tmp → tmpfs, size 128 MiB
/var/cache/atlas → ephemeral bounded volume
uploads → object storage
business data → managed database
```

## 6. Network namespace

Network namespace má vlastné interfaces, addresses, routes, neighbor state, sockets a port space.

Bridge model:

```text
container eth0
↔ veth pair
↔ host-side veth
↔ bridge
↔ host routing/firewall/NAT
↔ external network
```

`127.0.0.1` v containeri označuje container network namespace. Service bindnutá iba na loopback nemusí byť dostupná cez veth interface.

Network namespace neurčuje povolený traffic sám. Reachability vzniká kombináciou:

- interfaces a routes;
- host forwarding/NAT;
- firewall/network policy;
- DNS/service discovery;
- application bind address;
- return path.

## 7. User namespace a credential mapping

User namespace môže mapovať container UID 0 alebo UID 10001 na odlišný host UID range.

```text
container UID 0
→ host UID 2000000
```

Process môže mať capabilities vo svojom user namespace, ale nie automaticky globálne host capabilities.

Výhody:

- znižuje dopad container root-u;
- podporuje rootless runtime;
- oddeľuje numeric IDs od host ownershipu.

Failure boundaries:

- bind-mounted host file nemá mapped ownership;
- filesystem nepodporuje očakávané idmapped semantics;
- device alebo network operácia vyžaduje authority v parent namespace;
- rootless runtime nemôže vykonať privileged mount/network setup;
- subordinate UID/GID ranges kolidujú alebo chýbajú.

`root in container` preto nie je automaticky host root, ale mapping a namespace scope musia byť overené.

## 8. Cgroup placement ako runtime identity

Cgroup membership určuje resource accounting a controls. V cgroup v2 ide o unified hierarchy.

```text
runtime creates /atlas/payments/AP-313-07
→ writes resource policy
→ places process tree into cgroup
→ child processes inherit membership
→ kernel updates usage/events/pressure
```

Cgroup subject zahŕňa path alebo cgroup ID, parent policy, controller availability, limits, counters a process membership.

Ak process unikne do inej cgroup alebo helper beží mimo policy, metrics a limits môžu byť falošne neúplné.

## 9. CPU weight, quota a cpuset

### CPU weight

Relatívna priorita pri contention. Neznamená pevný počet CPU.

### CPU quota

Hard time budget v period:

```text
quota 200000 µs / period 100000 µs
→ maximálne približne 2 CPU time v každej period
```

Burst workload môže byť throttled, aj keď iné host CPUs sú idle, pretože cgroup vyčerpala svoj period budget.

### cpuset

Obmedzuje povolené CPUs/NUMA nodes. Môže zlepšiť isolation alebo locality, ale príliš úzky set vytvorí contention.

Observation:

```bash
cat /sys/fs/cgroup/cpu.stat
cat /proc/pressure/cpu
```

Sleduj `nr_throttled`, throttled time, runnable pressure a application latency spolu.

## 10. Memory lifecycle

Memory controller riadi anonymous memory, page cache a podľa konfigurácie swap a related accounting.

```text
allocation/page cache rastie
→ memory.high môže spustiť reclaim/throttling
→ memory.max zabráni ďalšiemu rastu
→ kernel vyberie process pre cgroup OOM
→ process/container skončí
```

`memory.max` nie je performance target. Workload môže byť veľmi pomalý pri reclaim-e ešte pred OOM.

Observation:

```bash
cat /sys/fs/cgroup/memory.current
cat /sys/fs/cgroup/memory.events
cat /sys/fs/cgroup/memory.stat
cat /proc/pressure/memory
```

Rozlišuj:

- application leak;
- legitimate burst;
- page-cache pressure;
- host-level pressure;
- cgroup-local OOM;
- kernel alebo external memory mimo očakávaného accountingu.

## 11. PID a process limit

`pids.max` ohraničuje processes a threads podľa kernel task modelu.

```text
worker/thread growth
→ cgroup reaches pids.max
→ clone/fork fails
→ application vidí EAGAIN / Resource temporarily unavailable
```

Failure nemusí vyzerať ako security policy. Sleduj `pids.current`, `pids.max`, `pids.events` a application thread model.

## 12. I/O a pressure

Cgroup I/O controls môžu riadiť weight alebo bandwidth/IOPS podľa device a kernel podpory. Workload môže mať dostatok CPU aj memory, ale trpieť:

- block I/O throttling;
- shared filesystem latency;
- writeback congestion;
- storage queue contention;
- page-cache reclaim.

PSI ukazuje čas, keď tasks čakajú pre CPU, memory alebo I/O pressure. Je to observation, nie automatický root-cause verdict.

## 13. Capabilities ako rozdelené privileges

Capabilities rozdeľujú časť tradičnej root authority, napríklad:

- `CAP_NET_BIND_SERVICE` pre low ports;
- `CAP_CHOWN`;
- `CAP_SETUID`;
- `CAP_NET_ADMIN`;
- `CAP_SYS_PTRACE`;
- veľmi širokú `CAP_SYS_ADMIN`.

Minimum model:

```text
drop ALL
→ pridaj iba capability viazanú na konkrétnu potrebnú operation
→ verify, že process ju má iba v required phase
```

Non-root process môže mať capability. Root process môže mať veľmi úzky set. UID samotné nie je plný privilege model.

## 14. Capability sets a exec transition

Kernel pracuje so sets:

- permitted;
- effective;
- inheritable;
- bounding;
- ambient.

Execution môže transformovať authority podľa current sets, file capabilities, user namespace, securebits a `no_new_privs`.

Observation:

```bash
grep '^Cap' /proc/<pid>/status
capsh --print
```

Bounding set je horná hranica, z ktorej process nemôže capability získať späť. Ambient capabilities môžu prežiť `execve` za definovaných podmienok.

## 15. `no_new_privs`

`no_new_privs` zabezpečuje, že process a jeho descendants nezískajú nové privileges cez `execve`, napríklad setuid binary alebo file capabilities.

```text
no_new_privs=true
→ exec privileged file
→ execution nesmie zvýšiť authority
```

Neodstraňuje už existujúce capabilities, filesystem permissions ani inherited file descriptors. Je to jedna vrstva, nie kompletné confinement.

## 16. Seccomp syscall boundary

Seccomp filter rozhoduje, či process smie vykonať konkrétny syscall a za akých argumentových podmienok podľa profilu.

```text
process invokes syscall
→ seccomp filter verdict
→ allow, errno, trap, kill alebo notification action
→ ďalšie kernel permission checks
```

Povolený syscall stále môže zlyhať na capability, LSM, namespace alebo filesystem policy.

`EPERM` preto nie je automaticky seccomp. Potrebuješ audit/runtime evidence.

Profile musí zohľadniť:

- CPU architecture a syscall numbering;
- application/runtime version;
- language runtime behavior;
- optional features;
- debugging/observability operations;
- default action a audit policy.

## 17. SELinux/AppArmor object policy

LSM policy hodnotí process label/profile, target object a operation.

```text
process label
+ file/socket/device label alebo path policy
+ requested operation
→ allow/deny + audit evidence
```

Unix mode môže povoľovať write a SELinux ho stále odmietne. Naopak vypnutie LSM môže skryť nesprávny volume label alebo profile transition.

Container policy potrebuje koordinovať runtime-generated labels, host policy, volume labeling, custom profile a audit retention.

## 18. Devices a runtime socket

Device node nie je obyčajný file. Otvára access k host kernel subsystemu.

Samostatne posudzuj:

- GPU;
- block device;
- KVM;
- FUSE;
- raw network interface;
- USB/serial devices;
- container runtime socket.

Runtime socket často poskytuje právo vytvoriť ďalší container s širšou policy, čo môže byť ekvivalent host-admin capability.

## 19. Privileged mode ako policy collapse

Privileged mode môže:

- pridať široké capabilities;
- sprístupniť devices;
- oslabiť seccomp;
- zmeniť LSM confinement;
- rozšíriť mount a kernel access.

Nie je to riešenie pre „potrebujem bindovať port 80“. Mení trust boundary celého workloadu.

Legitímne použitie potrebuje:

- explicitný host-level capability dôvod;
- dedicated nodes alebo sandbox;
- narrow devices/mounts, ak je to možné;
- short lifecycle;
- workload identity a audit;
- incident a cleanup model.

## 20. Worked failure: host root mount zrušil mount isolation

Support container mal samostatný PID a network namespace, no dostal writable bind mount `/host` na host `/` a `CAP_SYS_ADMIN`.

```text
namespace skryje default host mount tree
→ explicitný bind mount host root znova sprístupní
→ broad capability umožní ďalšie mount/kernel operácie
→ compromised process modifikuje host configuration
```

Namespace fungoval správne. Runtime policy vytvorila explicitný bypass.

## 21. Worked failure: host má voľnú memory, container je OOMKilled

Atlas container používal `memory.max=2GiB`. Host mal 20 GiB voľných, ale application burst prekročil limit.

```text
host capacity exists
→ cgroup local limit je authoritative boundary
→ allocation/reclaim fails v cgroup
→ cgroup OOM vyberie Atlas process
→ container skončí
```

Root cause sa nehľadá iba v host `free`. Treba cgroup path, `memory.events`, working set a application allocation timeline.

## 22. Worked failure: latency rastie pri idle host CPU

Container mal quota 100 ms CPU per 100 ms period, teda približne 1 CPU. Request burst spustil štyri worker threads a quota sa vyčerpala v prvej časti period.

```text
threads consume budget
→ cgroup throttled do ďalšej period
→ host má iné idle cores
→ request latency rastie
```

CPU percentage na hoste môže byť nízke. Diskriminačný dôkaz je `cpu.stat`, throttling events a latency correlation.

## 23. Worked failure: graceful shutdown nefunguje

Entrypoint shell bol PID 1 a nespúšťal application cez `exec`.

```text
runtime pošle SIGTERM PID 1
→ shell signal neforwarduje
→ application pokračuje
→ grace period vyprší
→ SIGKILL
→ pending transaction sa nereconcile-ne
```

Oprava je správny PID 1 contract a termination test, nie iba dlhší timeout.

## 24. Worked failure: rootless bind mount je permission denied

Container UID 10001 bol mapovaný na host UID 2010001. Host directory vlastnil UID 10001 bez idmapped mountu.

```text
numeric ID v containeri ≠ effective host filesystem ID
→ namespace mapping sa aplikuje
→ host VFS permission check vidí UID 2010001
→ access denied
```

`chmod 777` by skryl ownership model. Oprava je zosúladený UID mapping, idmapped mount alebo správny volume ownership lifecycle.

## 25. Causal troubleshooting walkthrough: operácia vracia `Operation not permitted`

Atlas potrebuje bindnúť port 443 a načítať mounted TLS key. Process končí s `EPERM`.

### 1. Zafixuj process a policy subject

Zaznamenaj:

- host PID a namespace PID;
- UID/GID a user namespace mappings;
- capability sets a bounding set;
- `no_new_privs`;
- seccomp profile/version;
- SELinux/AppArmor label/profile;
- mount source, destination, flags a labels;
- syscall/operation a target object;
- cgroup membership a resource events;
- runtime config digest.

### 2. Súťažiace hypotézy

1. Chýba `CAP_NET_BIND_SERVICE`.
2. Capability bola v permitted, ale nie effective sete.
3. Bounding set alebo `no_new_privs` zabránil exec transitionu.
4. Seccomp blokuje socket alebo related syscall.
5. SELinux/AppArmor odmieta bind alebo key read.
6. TLS key permissions/UID mapping sú nesprávne.
7. Mount je read-only, `noexec` alebo má wrong label.
8. Port už používa iný process v rovnakom network namespace.
9. Application binduje inú address alebo port než očakávané.
10. Error text pochádza z inej operation, napríklad temp file write.

### 3. Diskriminačné observation points

- exact failing syscall/operation podľa runtime-safe tracing alebo application evidence;
- `/proc/<pid>/status` capabilities a `NoNewPrivs`;
- seccomp mode a audit events;
- SELinux AVC/AppArmor denial;
- `stat`, mountinfo a user namespace maps;
- socket inventory v target network namespace;
- runtime-generated OCI config;
- application log s operation contextom.

### 4. Containment

Nezapínaj privileged mode, `seccomp=unconfined` ani globálne nevypínaj LSM. Zastav rollout a zachovaj policy/audit evidence.

### 5. Recovery

- capability gap → pridaj iba `NET_BIND_SERVICE` alebo používaj high port + proxy;
- exec transition gap → oprav entrypoint/file capability model bez rozšírenia bounding setu;
- seccomp denial → povoľ konkrétny required syscall po threat review;
- LSM denial → oprav profile alebo object label;
- user/mount permission → zosúlaď mapping, owner a mount flags;
- port collision → oprav namespace/process lifecycle;
- wrong operation → oprav application writable-path/config contract.

### 6. Over pôvodný outcome

Potvrď bind na intended interface, TLS key access, readiness request, forbidden syscall denial, non-root identity, exact capability set a graceful termination.

### 7. Posuň control skôr

Pridaj production-like runtime-policy integration test, generated OCI config inspection, LSM/seccomp audit fixture a capability allowlist policy.

## 26. Isolation matrix

| Vrstva | Primárny mechanizmus | Nezaručuje |
|---|---|---|
| view isolation | namespace | resource alebo privilege limit |
| resource control | cgroup | filesystem alebo syscall authorization |
| privilege decomposition | capabilities | object-specific policy |
| privilege non-escalation | `no_new_privs` | odstránenie existujúcej authority |
| syscall surface | seccomp | že povolená operation má permission |
| object policy | SELinux/AppArmor | CPU, memory alebo PID isolation |
| UID scope | user namespace | plnú VM boundary |
| storage view | mount namespace | bezpečnosť explicitných host mounts |

## 27. Referenčné pravidlá

- Container je process subject s kompozitnou policy, nie jeden kernel objekt.
- Namespace mení view, nie automaticky authorization alebo limit.
- Explicitný host mount môže obísť očakávanú mount isolation.
- PID 1 je lifecycle contract, nie iba prvý process.
- Cgroup path a process membership sú súčasť runtime identity.
- CPU quota môže throttliť workload pri idle host CPUs.
- Host free memory neobchádza `memory.max`.
- UID v user namespace sa musí mapovať na host filesystem identity.
- Non-root neznamená bez capabilities; root neznamená automaticky všetky capabilities.
- `no_new_privs` zabraňuje novému privilege gain-u, neodstraňuje existujúce privileges.
- Seccomp, capabilities a LSM sú odlišné verdict layers.
- Device alebo runtime-socket access zásadne mení host trust boundary.
- Privileged mode je policy collapse, nie diagnostický nástroj.

## 28. Kontrolné otázky

1. Aký lifecycle vytvára container runtime z process a policy layers?
2. Prečo namespace nie je access-control policy?
3. Aké povinnosti má PID 1?
4. Ako mount namespace môže byť obídený explicitným bind mountom?
5. Ako sa líši CPU weight, quota a cpuset?
6. Prečo host free memory nevylučuje cgroup OOM?
7. Ako user namespace mení filesystem permission identity?
8. Čo znamenajú permitted, effective a bounding capability sets?
9. Ako sa líši seccomp denial od LSM alebo capability denial?
10. Aké observation points treba pred použitím privileged bypassu?

## Glossary impact

Relevantné pojmy: runtime isolation subject, process authority subject, namespace lifecycle, namespace view, PID 1 contract, mount exposure path, user-namespace mapping, cgroup identity, CPU quota throttling, cgroup-local OOM, capability execution transition, capability bounding set, `no_new_privs`, seccomp verdict, LSM object policy, privileged-policy collapse a runtime-socket authority.

## Oficiálna dokumentácia

- [Linux namespaces](https://docs.kernel.org/admin-guide/namespaces/index.html)
- [Control Group v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)
- [Linux capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Seccomp](https://docs.kernel.org/userspace-api/seccomp_filter.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Containers vs. virtual machines](containers-vs-virtual-machines.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: OCI image a runtime standards →](oci-image-runtime-standards.md)
<!-- KNOWLEDGE-NAVIGATION:END -->