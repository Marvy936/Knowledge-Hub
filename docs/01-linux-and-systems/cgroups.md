# Linux Control Groups — cgroups

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Procesy, thready, PID a signals](processes-threads-pid-signals.md), [CPU and Memory Fundamentals](cpu-and-memory-fundamentals.md), [Linux Namespaces](namespaces.md)
- Súvisiace témy: systemd, containers, Kubernetes resources, capacity management, OOM

## 1. Definícia

Control groups, skrátene cgroups, sú kernel mechanizmus na hierarchické zoskupovanie procesov a riadenie, meranie alebo obmedzovanie ich resource usage.

Cgroups neposkytujú izolovaný pohľad ako namespaces. Určujú, koľko zdrojov môže skupina procesov použiť a ako sa o ne delí s ostatnými skupinami.

## 2. Problém, ktorý rieši

Bez cgroups by host vedel riadiť priority alebo limity najmä na úrovni jednotlivých procesov. Moderná služba však môže vytvoriť celý strom child procesov.

Cgroup umožňuje riadiť workload ako celok:

- CPU bandwidth a weight,
- memory usage a pressure,
- I/O bandwidth a priority,
- počet procesov,
- device access v starších modeloch alebo cez doplnkové politiky,
- accounting a observability.

## 3. Mentálny model

```text
cgroup hierarchy
└── system.slice
    ├── sshd.service
    │   ├── sshd parent
    │   └── session processes
    └── example.service
        ├── application
        └── worker processes
```

Limity sa aplikujú na skupinu, nie iba na jeden PID. Child proces zostáva v cgroup, pokiaľ ho manager explicitne nepresunie.

## 4. cgroup v1 a cgroup v2

### cgroup v1

Každý controller mohol mať samostatnú hierarchiu. CPU, memory a blkio preto nemuseli zoskupovať procesy rovnakým spôsobom.

### cgroup v2

Používa jednu unified hierarchy a konzistentnejší model delegácie a resource control.

Kontrola:

```bash
stat -fc %T /sys/fs/cgroup
mount | grep cgroup
```

Pre cgroup v2 typicky uvidíš:

```text
cgroup2fs
```

Moderné distribúcie a orchestration platformy preferujú cgroup v2. Konkrétna podpora fields závisí od kernelu, systemd a runtime verzie.

## 5. Hierarchia a členstvo procesu

Cgroup filesystem je typicky pripojený na:

```text
/sys/fs/cgroup
```

Členstvo procesu:

```bash
cat /proc/<PID>/cgroup
```

Pri cgroup v2 môže výstup vyzerať:

```text
0::/system.slice/example.service
```

Systemd vytvára a spravuje cgroups pre units. Preto je pri systemd službe vhodnejšie používať unit properties než ručne presúvať PIDs cez filesystem.

```bash
systemctl status example.service
systemctl show example.service -p ControlGroup
```

## 6. Controllers

Dostupné controllery:

```bash
cat /sys/fs/cgroup/cgroup.controllers
```

Controllery aktivované pre child cgroups:

```bash
cat /sys/fs/cgroup/cgroup.subtree_control
```

Typické cgroup v2 controllery:

- `cpu`,
- `cpuset`,
- `memory`,
- `io`,
- `pids`,
- `hugetlb`,
- `rdma`,
- `misc` podľa kernelu.

Parent musí controller delegovať do subtree. Nestačí, že controller existuje v kerneli.

## 7. CPU controller

### CPU weight

Relatívna váha pri contention:

```text
cpu.weight
```

Vyššia hodnota znamená väčší podiel CPU, keď o CPU súťažia viaceré runnable cgroups. Weight nie je pevná rezervácia ani hard limit.

Systemd:

```ini
[Service]
CPUWeight=200
```

### CPU quota

Harder bandwidth limit:

```text
cpu.max
```

Príklad:

```text
50000 100000
```

znamená najviac 50 ms CPU času v každom 100 ms období, teda približne 0,5 CPU.

Systemd:

```ini
[Service]
CPUQuota=50%
```

Quota môže vytvoriť throttling a latency aj vtedy, keď host má inak voľné CPUs, pretože workload vyčerpal pridelený budget v danom period.

Pozorovanie:

```bash
cat /sys/fs/cgroup/<path>/cpu.stat
```

Sleduj najmä usage a throttling counters.

## 8. cpuset controller

Cpuset obmedzuje, na ktorých CPUs a NUMA memory nodes môže workload bežať.

```text
cpuset.cpus
cpuset.mems
```

Použitie je citlivé na topology. Nesprávne pinovanie môže:

- znížiť scheduler flexibility,
- preťažiť jeden core,
- spôsobiť remote NUMA access,
- skomplikovať failover pri offline CPU.

Cpuset je placement mechanizmus; CPU quota je bandwidth mechanizmus.

## 9. Memory controller

Dôležité cgroup v2 fields:

- `memory.current` — aktuálne chargeované použitie,
- `memory.max` — hard limit,
- `memory.high` — throttling/reclaim boundary,
- `memory.low` — best-effort protection,
- `memory.min` — silnejšia protection,
- `memory.swap.current`,
- `memory.swap.max`,
- `memory.events`,
- `memory.stat`.

### `memory.max`

Keď workload prekročí limit a reclaim nestačí, môže nastať cgroup-local OOM. Host pritom môže mať voľnú RAM.

### `memory.high`

Procesy nad hranicou čelia reclaim pressure a throttlingu. Je vhodný na kontrolovanejšiu degradáciu pred hard OOM.

### Memory accounting

Cgroup memory môže zahŕňať:

- anonymous memory,
- page cache,
- kernel memory kategórie,
- socket buffers,
- ďalšie charges podľa kernelu.

Preto RSS jedného procesu nemusí zodpovedať `memory.current` celej cgroup.

Diagnostika:

```bash
cat /sys/fs/cgroup/<path>/memory.current
cat /sys/fs/cgroup/<path>/memory.max
cat /sys/fs/cgroup/<path>/memory.events
cat /sys/fs/cgroup/<path>/memory.stat
```

`memory.events` pomáha rozlíšiť `high`, `max`, `oom` a `oom_kill` udalosti.

## 10. OOM v cgroup

Cgroup-local OOM nie je rovnaký ako host-wide OOM.

```text
Host capacity: 32 GiB
Container limit: 512 MiB
Container usage: 512 MiB
→ cgroup OOM môže nastať, aj keď host má voľnú RAM
```

Kernel alebo userspace manager môže ukončiť proces v postihnutej cgroup. Správanie ovplyvňujú cgroup settings a runtime.

Systemd podporuje napríklad:

```ini
[Service]
MemoryMax=512M
OOMPolicy=stop
```

Pri diagnostike kontroluj súčasne:

```bash
systemctl status example.service
systemctl show example.service -p MemoryCurrent -p MemoryMax
journalctl -k -b | grep -i oom
cat /sys/fs/cgroup/<path>/memory.events
```

## 11. PIDs controller

`pids.max` obmedzuje počet procesov alebo threadov v cgroup.

```text
pids.current
pids.max
pids.events
```

Limit chráni host pred fork bombou alebo nekontrolovaným thread creation.

Symptóm prekročenia môže byť:

```text
fork: Resource temporarily unavailable
```

Host môže mať dostatok memory aj PID space, ale workload narazil na cgroup-local limit.

Systemd:

```ini
[Service]
TasksMax=512
```

## 12. I/O controller

I/O controller riadi block I/O podľa device major/minor identifikátorov.

Typické fields:

- `io.stat`,
- `io.max`,
- `io.weight`,
- `io.pressure`.

Príklad konceptu:

```text
8:0 rbps=10485760 wbps=5242880
```

Limit sa viaže na konkrétny block device. Pri device mapper, LVM, RAID alebo cloud storage treba rozumieť skutočnej device topology.

I/O limit na nesprávnej vrstve nemusí riadiť fyzické zariadenie podľa očakávania.

## 13. Pressure Stall Information v cgroup

Cgroup v2 môže poskytovať PSI:

```text
cpu.pressure
memory.pressure
io.pressure
```

Ukazuje čas, počas ktorého tasks v cgroup čakali pre resource pressure.

To je dôležité, pretože:

```text
utilization
≠ saturation
≠ user-visible latency
```

Workload môže mať relatívne nízke priemerné použitie, ale krátke obdobia silného stalling-u.

## 14. Delegácia

Delegácia znamená, že parent manager bezpečne odovzdá správu subtree inému managerovi, napríklad container runtime alebo user session manageru.

Správna delegácia musí riešiť:

- ownership cgroup directories,
- ktoré controllers možno aktivovať,
- zákaz presúvania procesov mimo povoleného subtree,
- pravidlo no internal processes pre niektoré controller scenáre,
- koordináciu s systemd.

Ručné vytváranie cgroups pod systemd-managed hierarchy bez delegácie môže byť prepísané alebo porušovať manager invariants.

Systemd unit môže používať:

```ini
[Service]
Delegate=yes
```

To sa používa pre workload managers, nie ako všeobecné nastavenie každej služby.

## 15. Systemd resource controls

Príklady:

```ini
[Service]
CPUWeight=200
CPUQuota=150%
MemoryHigh=1G
MemoryMax=1500M
TasksMax=512
IOWeight=100
```

Runtime zmena:

```bash
sudo systemctl set-property example.service MemoryMax=1G
```

Pozorovanie:

```bash
systemctl show example.service \
  -p ControlGroup \
  -p CPUUsageNSec \
  -p MemoryCurrent \
  -p MemoryMax \
  -p TasksCurrent \
  -p TasksMax
```

Systemd abstrakcia je preferovaná pre systemd units, pretože zachováva desired state a ownership hierarchy.

## 16. Containers a Kubernetes

Container runtime vytvorí cgroups pre containers alebo Pods a mapuje runtime configuration na kernel controls.

Kubernetes requests a limits nie sú pri všetkých resources identické mechanizmy:

- CPU request ovplyvňuje scheduling a typicky relative shares,
- CPU limit sa typicky mapuje na quota,
- memory request ovplyvňuje scheduling a QoS,
- memory limit sa mapuje na hard cgroup boundary,
- cgroup hierarchy a QoS layout závisia od runtime a kubelet configuration.

Pre presnú diagnostiku treba sledovať celý reťazec:

```text
Kubernetes manifest
→ scheduler/kubelet policy
→ container runtime
→ OCI config
→ cgroup filesystem
→ kernel counters
```

## 17. Cgroups vs. nice a ulimit

### `nice`

Mení CPU scheduling priority procesu, nie hierarchický workload budget.

### `ulimit` / rlimits

Nastavuje per-process limity, napríklad open files alebo core size. Child proces ich môže dediť.

### cgroups

Riadia skupinu procesov a poskytujú hierarchical accounting.

Mechanizmy sa dopĺňajú; nie sú vzájomné synonymá.

## 18. Troubleshooting scenáre

### Aplikácia je pomalá, host CPU nie je plné

Kontrola:

```bash
cat /proc/<PID>/cgroup
cat /sys/fs/cgroup/<path>/cpu.max
cat /sys/fs/cgroup/<path>/cpu.stat
cat /sys/fs/cgroup/<path>/cpu.pressure
```

Možná príčina: CPU quota throttling.

### Proces bol zabitý, host má voľnú RAM

```bash
cat /sys/fs/cgroup/<path>/memory.max
cat /sys/fs/cgroup/<path>/memory.current
cat /sys/fs/cgroup/<path>/memory.events
journalctl -k -b | grep -i oom
```

Možná príčina: cgroup-local OOM.

### Aplikácia nevie vytvoriť nový thread

```bash
cat /sys/fs/cgroup/<path>/pids.current
cat /sys/fs/cgroup/<path>/pids.max
cat /sys/fs/cgroup/<path>/pids.events
```

Možná príčina: `pids.max` alebo systemd `TasksMax`.

## 19. Časté omyly

### „CPU limit rezervuje CPU“

Nie. Quota obmedzuje maximum; rezervácia a scheduling priority sú odlišné koncepty.

### „Memory limit sleduje iba RSS hlavného procesu“

Nie. Cgroup účtuje celý workload a viaceré memory kategórie.

### „Host má voľnú RAM, takže OOM nemohol nastať“

Cgroup-local hard limit môže spôsobiť OOM nezávisle od host-wide voľnej memory.

### „Namespaces a cgroups sú to isté“

Namespaces izolujú pohľad. Cgroups riadia a účtujú resources.

### „Môžem ľubovoľne meniť `/sys/fs/cgroup` pod systemd“

Systemd je owner hierarchy. Použi unit properties alebo korektnú delegáciu.

## 20. Kontrolné otázky

1. Aký je rozdiel medzi namespace a cgroup?
2. Prečo cgroup v2 používa unified hierarchy?
3. Aký je rozdiel medzi CPU weight a CPU quota?
4. Čo odlišuje `memory.high` od `memory.max`?
5. Prečo môže vzniknúť cgroup-local OOM pri voľnej host memory?
6. Ako `pids.max` chráni host?
7. Čo meria PSI v cgroup?
8. Prečo je delegácia dôležitá pri container runtime?
9. Ako sa Kubernetes resource settings dostanú až ku kernel cgroup fields?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Linux Namespaces](namespaces.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Linux Capabilities →](linux-capabilities.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
