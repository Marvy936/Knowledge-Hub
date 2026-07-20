# CPU and Memory Fundamentals

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Kernel a user space](kernel-and-user-space.md), [Procesy, thready, PID a signals](processes-threads-pid-signals.md)
- Súvisiace témy: scheduling, virtual memory, page cache, swap, cgroups, performance troubleshooting

## 1. Definícia

CPU a memory management sú dve základné úlohy kernelu:

- rozhodnúť, ktorý runnable thread dostane CPU čas,
- mapovať virtuálnu pamäť procesov na fyzické pages a storage-backed data.

Aplikácia nepracuje priamo s fyzickým CPU core ani s konkrétnou RAM adresou. Vidí abstrakcie poskytované kernelom.

## 2. CPU execution model

Proces môže mať jeden alebo viac threadov. Scheduler plánuje primárne schedulable tasks, typicky thready.

Stavy zjednodušene:

```text
running    práve vykonáva inštrukcie
runnable   čaká na CPU
sleeping   čaká na event, timer alebo I/O
stopped    pozastavený signalom/debuggerom
zombie     ukončený, čaká na reap parentom
```

Veľa procesov nemusí znamenať vysoké CPU usage. Väčšina môže spať.

## 3. Scheduler a context switch

Scheduler prideľuje CPU time podľa scheduling class, priority, fairness a affinity.

Context switch uloží stav aktuálnej task a obnoví stav inej. Má cenu:

- scheduler overhead,
- cache disruption,
- TLB effects,
- migration medzi cores.

Veľký počet context switches môže byť prirodzený pri I/O-heavy workload, ale môže tiež ukazovať lock contention alebo príliš veľa threadov.

Pozorovanie:

```bash
vmstat 1
pidstat -w 1
```

## 4. CPU usage nie je load average

CPU usage odpovedá, koľko času CPU trávilo v jednotlivých stavoch.

```bash
top
mpstat -P ALL 1
```

Časté CPU states:

- `us` user space,
- `sy` kernel/system,
- `id` idle,
- `wa` iowait,
- `st` steal time vo virtualizácii,
- `hi`/`si` hardware/software interrupts.

Load average je priemer počtu tasks, ktoré sú runnable alebo v určitom uninterruptible sleep, typicky pri čakaní na I/O.

```bash
uptime
cat /proc/loadavg
```

Load `4.0` môže byť nízky na 64-core hoste a kritický na 2-core hoste. Treba ho interpretovať voči počtu CPUs a charakteru čakania.

## 5. CPU affinity a NUMA

Affinity obmedzuje, na ktorých CPUs môže task bežať.

```bash
taskset -cp <PID>
```

NUMA systémy majú memory nodes s rozdielnou access latency. Thread bežiaci na jednom socket-e môže pristupovať k remote memory node.

```bash
lscpu
numactl --hardware
```

NUMA optimalizácia je workload-specific. Náhodné pinovanie bez merania môže zhoršiť scheduling flexibility.

## 6. Virtual memory

Každý proces má vlastný virtual address space.

```text
Virtual address procesu
  ↓ page tables
Physical memory page
  alebo
file-backed page / swap / not present
```

Výhody:

- izolácia procesov,
- zdieľanie knižníc,
- memory mapping files,
- demand paging,
- jednoduchší programovací model.

`malloc()` nemusí okamžite prideliť fyzickú RAM. Proces môže rezervovať virtual address range a fyzické pages sa pridelia až pri prvom prístupe.

## 7. RSS, VSZ a PSS

Časté metriky:

- VSZ/VIRT: veľkosť virtuálneho address space,
- RSS/RES: resident pages v RAM,
- PSS: zdieľané pages rozdelené pomerne medzi procesy.

```bash
ps -o pid,comm,vsz,rss,%mem -p <PID>
cat /proc/<PID>/status
cat /proc/<PID>/smaps_rollup
```

Veľké VIRT samo osebe neznamená vysokú spotrebu RAM. Memory-mapped files alebo rezervovaný address space môžu byť veľmi veľké.

## 8. Page cache

Kernel používa voľnú RAM ako cache filesystem data.

```text
Application read
  ↓
page cache hit → RAM
page cache miss → storage → cache → application
```

Preto nízka hodnota `free` nie je automaticky problém. Dôležitejšia je dostupná pamäť, ktorú možno použiť bez významného swapu alebo reclaim pressure.

```bash
free -h
cat /proc/meminfo
```

`available` odhaduje, koľko memory môže systém poskytnúť bez swapovania podstatnej časti pracovnej množiny.

## 9. Anonymous a file-backed memory

- anonymous memory: heap, stack a pages bez file backing,
- file-backed memory: executable, shared libraries, mmap files a page cache.

File-backed clean pages možno pri pressure zahodiť a neskôr znovu načítať. Dirty pages treba najprv zapísať. Anonymous pages možno presunúť do swapu, ak je aktívny.

## 10. Swap a reclaim

Pri memory pressure kernel reclaimuje pages.

Možnosti:

- drop clean file cache,
- writeback dirty pages,
- swap anonymous pages,
- compact memory,
- nakoniec OOM handling.

Pozorovanie:

```bash
vmstat 1
sar -W 1
swapon --show
```

V `vmstat`:

- `si` pages read from swap,
- `so` pages written to swap.

Aktívny swap nie je automaticky incident. Trvalé vysoké swap-in/out spolu s latency môže znamenať thrashing.

## 11. OOM killer

Keď kernel nedokáže uspokojiť memory allocation a recovery mechanizmy nestačia, môže vybrať proces na ukončenie.

Diagnostika:

```bash
journalctl -k -b | grep -i -E 'out of memory|oom|killed process'
dmesg -T | grep -i oom
```

Výber ovplyvňuje memory usage, `oom_score`, `oom_score_adj` a context, napríklad cgroup limit.

```bash
cat /proc/<PID>/oom_score
cat /proc/<PID>/oom_score_adj
```

OOM kill je posledný mechanizmus obnovy, nie root cause. Root cause môže byť memory leak, príliš nízky limit, burst, absent capacity planning alebo neobmedzená concurrency.

## 12. Memory leak vs. cache growth

Memory leak znamená, že aplikácia drží objekty, ktoré už nepotrebuje, a usage dlhodobo rastie.

Nie každý rast RSS je leak:

- runtime môže držať allocator arenas,
- application cache môže byť zámerná,
- page cache je kernel cache,
- workload môže mať väčšiu pracovnú množinu.

Diagnostika vyžaduje časovú sériu a workload kontext, nie jeden snapshot.

## 13. Pressure Stall Information

PSI meria čas, počas ktorého tasks čakali pre nedostatok CPU, memory alebo I/O capacity.

```bash
cat /proc/pressure/cpu
cat /proc/pressure/memory
cat /proc/pressure/io
```

PSI môže ukázať degradáciu skôr než úplné vyčerpanie resource. Je užitočné rozlíšiť vysokú utilization od reálneho stall dopadu.

## 14. Základné diagnostické nástroje

```bash
uptime
lscpu
free -h
vmstat 1
mpstat -P ALL 1
pidstat 1
top
ps aux --sort=-%cpu
ps aux --sort=-%mem
```

Interpretácia musí ísť vrstvovo:

1. Je systém CPU-bound, memory-bound alebo I/O-bound?
2. Je problém globálny alebo v jednom procese/cgroup?
3. Ide o utilization, queueing alebo stalling?
4. Zmenila sa workload intensity alebo konfigurácia?
5. Je problém trvalý alebo burst?

## 15. Troubleshooting scenáre

### Vysoký load, nízke CPU usage

Možné príčiny:

- tasks v uninterruptible I/O wait,
- storage latency,
- NFS hang,
- kernel lock alebo device problém.

Kontrola:

```bash
vmstat 1
ps -eo state,pid,comm,wchan:32 | grep '^D'
iostat -xz 1
journalctl -k -b
```

### Jeden core na 100 %, ostatné idle

Možné príčiny:

- single-threaded workload,
- CPU affinity,
- lock serialization,
- jedna hot queue.

### Pamäť „plná“, ale systém stabilný

Over page cache a `MemAvailable`. Vysoká cache pri nízkom swap activity môže byť zdravý stav.

### OOM v kontajneri, host má voľnú RAM

Proces mohol naraziť na cgroup memory limit. Host-wide free memory nie je autoritatívna pre cgroup-local OOM.

## 16. Časté omyly

### „Load average je percento CPU“

Nie. Je to priemerná queue/runnable a uninterruptible task pressure metrika.

### „Free RAM je dobrá RAM“

Nevyužitá RAM môže byť použitá ako page cache a zlepšiť výkon.

### „Vysoké VIRT znamená memory leak“

Nie. VIRT zahŕňa rezervovaný a mapped address space.

### „Swap je vždy zlý“

Nie. Zlé je nekontrolované thrashing a latency; mierny swap môže byť súčasťou memory policy.

### „OOM killer je príčina incidentu“

Je to mechanizmus reakcie na memory exhaustion.

## 17. Kontrolné otázky

1. Aký je rozdiel medzi runnable a running task?
2. Prečo load average nie je CPU percentage?
3. Aký je rozdiel medzi VIRT, RSS a PSS?
4. Prečo môže mať Linux málo free memory a byť zdravý?
5. Aký je rozdiel medzi anonymous a file-backed memory?
6. Čo znamená vysoké `si` a `so` vo `vmstat`?
7. Prečo host free memory nevylučuje cgroup OOM?
8. Ako PSI dopĺňa utilization metriky?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Storage, mounty a filesystems](storage-mounts-and-filesystems.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Linux networking →](linux-networking.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
