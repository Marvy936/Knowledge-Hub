# Namespaces, cgroups a capabilities

Container nie je jeden kernel objekt. Je to koordinovaná konfigurácia Linux procesov, namespaces, cgroups, credentials, capabilities, filesystem mounts a security policy. Každý mechanizmus rieši inú časť izolácie; žiadny z nich sám nevytvára úplnú bezpečnostnú hranicu.

## 1. Tri rozdielne otázky

Pri container isolation oddeľuj:

1. **Čo process vidí?** — namespaces.
2. **Koľko resources môže spotrebovať?** — cgroups a limits.
3. **Ktoré privilegované operácie smie vykonať?** — capabilities, seccomp, LSM a credentials.

Container s oddeleným PID namespace môže stále vyčerpať host memory, ak nemá memory cgroup limit. Process s resource limitom môže stále poškodiť host, ak dostane priveľké capabilities alebo citlivý host mount.

## 2. Namespace model

Linux namespace virtualizuje vybranú kategóriu kernel state-u pre skupinu procesov. Process vidí namespace-specific pohľad, hoci kernel zostáva spoločný.

Najdôležitejšie namespaces:

| Namespace | Izoluje pohľad na |
|---|---|
| PID | process IDs a process tree |
| mount | mount table a propagation |
| network | interfaces, routes, sockets, firewall state |
| IPC | System V IPC a POSIX message queues |
| UTS | hostname a domain name |
| user | user/group IDs a capability scope |
| cgroup | viditeľnosť cgroup hierarchy |
| time | vybrané clocks a offsets |

Namespaces neposkytujú automaticky policy. Napríklad samostatný network namespace neznamená, že traffic je povolený iba bezpečným smerom; routes, veth, firewall a host forwarding stále určujú reálny reachability model.

## 3. PID namespace a PID 1

Process v novom PID namespace môže vidieť seba ako PID 1. PID 1 má špeciálne lifecycle povinnosti:

- zbiera orphaned child processes,
- správne forwarduje signals,
- ukončuje sa predvídateľne,
- drží container lifecycle.

Aplikácia, ktorá nereaguje na `SIGTERM`, môže prekročiť graceful-shutdown timeout a byť ukončená cez `SIGKILL`. Shell wrapper bez `exec` môže signal zachytiť alebo neforwardovať.

Diagnostika:

```bash
ps -o pid,ppid,stat,comm
cat /proc/1/status
```

## 4. Mount namespace

Mount namespace poskytuje samostatný pohľad na mount table. Container runtime typicky pripraví:

- image root filesystem,
- bind mounts alebo volumes,
- pseudo-filesystems ako `/proc`,
- read-only alebo masked paths,
- mount propagation pravidlá.

Rizikové sú najmä:

- bind mount host root filesystemu,
- writable `/proc` alebo `/sys` exposure,
- mount propagation z containeru na host,
- runtime socket mount,
- device nodes a host paths bez allowlistu.

Read-only root filesystem znižuje mutation surface, ale aplikácia potrebuje explicitné writable paths pre temporary data, caches alebo sockets.

## 5. Network namespace

Network namespace má vlastné:

- network interfaces,
- IP adresy,
- routing table,
- neighbor table,
- sockets a ports,
- firewall state podľa implementácie.

Bežný bridge model používa veth pair:

```text
container eth0
  ↕ veth pair
host-side veth
  ↕
Linux bridge
  ↕
host routing/NAT
```

`localhost` v containeri označuje jeho vlastný network namespace, nie host ani susedný container.

## 6. User namespace

User namespace mapuje container user IDs na odlišné host user IDs. Process môže mať UID 0 vo svojom namespace, ale neprivilegovaný host UID mimo neho.

To znižuje dopad container escape alebo host-file accessu, ale vyžaduje správny mapping a filesystem ownership model. Rootless containers využívajú user namespaces, unprivileged networking a ďalšie obmedzenia, no nemusia podporovať všetky privileged operations.

`root in container` a `root on host` nie sú vždy totožné, ale bez user namespace môžu mať rovnaký numeric UID a výrazne širší blast radius.

## 7. Cgroups

Control groups organizujú procesy hierarchicky a aplikujú resource accounting a control. Cgroup v2 používa unified hierarchy.

Relevantné controllers a rozhrania zahŕňajú:

- CPU weight a quota,
- memory limits a events,
- process count cez `pids`,
- I/O limits,
- cpuset placement,
- pressure stall information.

Cgroup nie je iba hard limit. Poskytuje aj accounting a evidence potrebnú na diagnostiku resource pressure.

## 8. CPU limits

Rozlišuj:

- **CPU request/share/weight** — relatívna priorita pri contention,
- **CPU quota** — hard time budget v period,
- **cpuset** — povolené CPU cores alebo NUMA nodes.

CPU quota môže spôsobiť throttling aj keď host celkovo nevyzerá plne vyťažený. Latency-sensitive workload môže trpieť pri krátkych burstoch a nevhodnom quota/period nastavení.

Dôležité evidence:

```bash
cat /sys/fs/cgroup/cpu.stat
cat /proc/pressure/cpu
```

## 9. Memory limits

Memory controller sleduje a obmedzuje napríklad anonymous memory, page cache a podľa konfigurácie swap.

Pri memory pressure môže nastať:

- reclaim,
- throttling,
- cgroup OOM,
- host-level OOM,
- process termination.

`memory.max` nie je performance target. Workload môže výrazne degradovať ešte pred OOM. Sleduj working set, reclaim, PSI a OOM events, nie iba poslednú spotrebu.

## 10. PID limit

`pids.max` chráni host pred fork bomb alebo nekontrolovaným process/thread rastom. Príliš nízky limit môže zlyhať pri:

- thread pools,
- process-based workers,
- shell helpers,
- package/runtime subprocessoch.

Failure sa môže prejaviť ako `Resource temporarily unavailable`, nie ako zjavná container policy chyba.

## 11. Capabilities

Linux capabilities rozdeľujú tradičné root oprávnenia na menšie jednotky, napríklad:

- `CAP_NET_BIND_SERVICE`,
- `CAP_NET_ADMIN`,
- `CAP_SYS_ADMIN`,
- `CAP_CHOWN`,
- `CAP_SETUID`,
- `CAP_SYS_PTRACE`.

Container by mal začínať s minimálnym capability setom. `CAP_SYS_ADMIN` je mimoriadne široká capability a často predstavuje takmer privileged boundary.

Príklad princípu:

```text
drop all capabilities
→ pridaj iba konkrétnu capability dokázateľne potrebnú workloadom
```

## 12. Capability sets

Kernel pracuje s viacerými sets:

- permitted,
- effective,
- inheritable,
- bounding,
- ambient.

Security review nemá kontrolovať iba „process beží ako non-root“. Non-root process môže mať capability a root process môže mať capability set výrazne obmedzený.

Diagnostika:

```bash
grep '^Cap' /proc/self/status
capsh --print
```

## 13. `no_new_privs`

Flag `no_new_privs` zabraňuje procesu a jeho descendants získať nové privileges cez `execve`, napríklad setuid binary alebo file capabilities.

Je dôležitou vrstvou pri spúšťaní nedôveryhodného alebo extensible kódu. Nenahrádza však odstránenie existujúcich capabilities alebo filesystem permissions.

## 14. Seccomp

Seccomp filtruje system calls podľa policy. Default profile môže blokovať zriedkavé alebo rizikové syscalls a zmenšiť kernel attack surface.

Riziká:

- `unconfined` vypne významnú ochranu,
- príliš úzky profil spôsobí runtime failures,
- profil musí zohľadniť architecture a application behavior,
- povolenie syscallu stále podlieha ďalším permission checks.

Pri chybe hľadaj `EPERM`, audit logs a seccomp events, nie iba application stack trace.

## 15. Mandatory Access Control

SELinux alebo AppArmor aplikujú policy nad file, process, capability a ďalšími operáciami aj vtedy, keď Unix mode bits povoľujú access.

Container security potrebuje koordinovať:

- runtime-generated labels/profiles,
- host policy,
- volume labels,
- custom profiles,
- audit evidence.

Vypnutie SELinux/AppArmor kvôli jednému permission erroru odstráni system-wide ochranu namiesto opravy konkrétneho contractu.

## 16. Privileged container

Privileged mode typicky:

- udeľuje široké capabilities,
- sprístupňuje devices,
- oslabuje seccomp/LSM confinement,
- rozširuje host filesystem a kernel attack surface.

Privileged container nie je „container, ktorý môže bindovať port 80“. Je to zásadná zmena trust boundary. Použitie musí mať explicitný dôvod, obmedzené nodes, identity, auditing a alternatívy vyhodnotené vopred.

## 17. Device access

Device node poskytuje prístup k host kernel subsystemu. GPU, block device, KVM, FUSE alebo raw network device potrebujú samostatné security posúdenie.

Device access kombinuj s:

- allowlistom konkrétnych devices,
- cgroup/device policy podľa runtime,
- capabilities,
- ownershipom,
- SELinux/AppArmor policy,
- dedicated nodes podľa rizika.

## 18. Resource limits nie sú rezervácie

Hard limit neznamená, že resource je garantovaný. Workload potrebuje rozlíšiť:

- scheduling/reservation model,
- maximum limit,
- host overcommit,
- noisy-neighbor contention,
- kernel memory a disk pressure,
- external quotas.

Container môže mať memory limit 2 GiB, ale stále zápasiť o CPU, I/O alebo network bandwidth.

## 19. Isolation matrix

| Mechanizmus | Primárny účel | Nerobí automaticky |
|---|---|---|
| namespace | oddelený pohľad na kernel state | resource limit |
| cgroup | accounting a resource control | privilege isolation |
| capability | jemnejší privilege model | syscall filtering |
| seccomp | syscall allow/deny policy | filesystem ownership |
| SELinux/AppArmor | mandatory access policy | CPU/memory limit |
| user namespace | UID/GID a capability scope | kompletnú VM boundary |

Defense in depth vzniká ich kombináciou.

## 20. Troubleshooting

### Process je `OOMKilled`

Over cgroup memory events, working set, cache/reclaim, host pressure a application limits. Nezvyšuj limit bez určenia leak/burst modelu.

### Container nevie bindovať low port

Over effective UID, `CAP_NET_BIND_SERVICE`, sysctl behavior a runtime policy. Neudeľuj `CAP_NET_ADMIN` alebo privileged mode bez potreby.

### Operácia vracia `Operation not permitted`

Over capabilities, seccomp, user namespace mapping, SELinux/AppArmor denial a mount flags.

### Container nevidí host process

Je v samostatnom PID namespace. Host môže proces vidieť pod host PID, container používa namespace PID.

### CPU latency rastie bez 100 % host CPU

Over cgroup throttling, quota period, cpuset, PSI a workload burst profile.

## 21. Kontrolné otázky

1. Aký problém rieši namespace a aký cgroup?
2. Prečo PID 1 potrebuje správne signal a child-process správanie?
3. Čo znamená root v user namespace?
4. Aký je rozdiel medzi CPU weight a quota?
5. Prečo memory limit nie je performance SLO?
6. Čo chráni `pids.max`?
7. Prečo je `CAP_SYS_ADMIN` riziková?
8. Čo poskytuje `no_new_privs`?
9. Ako sa líšia seccomp a SELinux/AppArmor?
10. Prečo privileged mode mení trust boundary?

## Glossary impact

Relevantné pojmy: Linux namespace, PID namespace, mount namespace, network namespace, user namespace, cgroup v2, CPU throttling, memory cgroup, cgroup OOM, PID limit, Linux capability, capability set, `no_new_privs`, seccomp, privileged container a device access.

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
