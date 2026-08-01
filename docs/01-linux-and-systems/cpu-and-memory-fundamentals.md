# CPU a memory fundamentals

CPU a memory telemetry opisuje odlišné resources a časy. CPU utilization ukazuje, koľko scheduling time-u tasky spotrebovali; nehovorí sama o sebe, či workload čaká v run queue, je throttled cgroupou alebo blokuje na I/O. Load average zahŕňa runnable a vybrané uninterruptible tasks a nie je percento CPU.

Memory model spája virtual address spaces, page tables, anonymous pages, file-backed page cache, reclaim, swap a cgroup accounting. `free` memory blízka nule môže byť zdravá, ak je väčšina RAM reclaimable cache. Problém vzniká pri sustained pressure, vysokých major faults, reclaim/compaction cost, swap thrash alebo OOM decisione.

```text
user symptom
→ task/cgroup/host scope
→ utilization, saturation a pressure
→ scheduler alebo memory-state hypothesis
→ discriminating observation
→ bounded change
→ latency/throughput a forbidden-outcome validation
```

Výkonová diagnóza preto nevyvodzuje root cause z jednej vysokej hodnoty. Musí zistiť effective quota/limit, workload concurrency, run-queue alebo allocation path a následne preukázať, že náprava zlepšila user outcome bez presunutia bottlenecku.

## 1. Mentálny model

Kernel rieši dve prepojené úlohy: prideľuje CPU čas runnable taskom a mapuje virtuálnu pamäť procesov na fyzické pages alebo backing storage. Výkonový problém preto nemožno diagnostikovať iba jedným percentom; treba rozlíšiť execution, queueing, waiting, reclaim a hard limits.

```text
Workload
  ↓
runnable tasks → scheduler → CPU cores
  ↓                           ↓
locks / I/O wait          instructions

virtual addresses → page tables → RAM / page cache / swap
                                      ↓
                               reclaim / OOM
```

Aplikácia nevidí konkrétny fyzický core ani RAM adresu. Pracuje s abstrakciami, ktoré kernel môže presúvať, zdieľať, odkladať alebo obmedziť podľa policy a aktuálneho tlaku.

## 2. Task execution a scheduler

Linux scheduler plánuje schedulable tasks, čo sú v praxi najmä thready. Proces s viacerými threadmi môže používať viac CPU cores súčasne, zatiaľ čo jednovláknová aplikácia môže saturovať iba jeden logical CPU.

Task prechádza stavmi podľa toho, či vykonáva inštrukcie alebo čaká:

- **Running** — task práve vykonáva inštrukcie na jednom CPU.
- **Runnable** — task je pripravený, ale čaká v run queue na pridelenie CPU času.
- **Interruptible sleep** — task čaká na event, timer, socket alebo inú udalosť a možno ho prebudiť signalom.
- **Uninterruptible sleep** — task čaká v kernelovej operácii, ktorú nemožno bezpečne prerušiť, často pri I/O.
- **Stopped alebo zombie** — task nevykonáva bežnú prácu; stopped čaká na pokračovanie, zombie na reap parentom.

Veľký počet procesov preto automaticky neznamená vysokú CPU záťaž. Rozhodujúci je počet runnable taskov, ich CPU demand a čas strávený čakaním na iné resources.

## 3. Scheduling policy, priority a fairness

Scheduler rozdeľuje CPU podľa scheduling class, priority, affinity a fairness pravidiel. Bežné user-space workloady používajú fair scheduling, zatiaľ čo real-time triedy môžu dostať prednosť a pri nesprávnom použití vyhladovať ostatné procesy.

`nice` hodnota ovplyvňuje relatívnu váhu bežného procesu, nie garantovaný podiel CPU. Zmena priority nepomôže, ak workload čaká na storage, lock alebo sieť.

```bash
ps -eo pid,tid,cls,pri,ni,psr,stat,comm
chrt -p <PID>
renice 5 -p <PID>
```

Pri diagnostike treba najprv zistiť scheduling class a run-queue pressure. Náhodné zvýšenie priority môže iba presunúť latency na inú službu.

## 4. Context switches

Context switch uloží register state aktuálneho tasku a obnoví state iného. Pri prepnutí môže dôjsť aj k narušeniu CPU caches, TLB locality a NUMA locality.

Context switches sú normálnou súčasťou multitaskingu. Problémom sa stávajú vtedy, keď ich vysoký počet vzniká z lock contention, príliš veľkého počtu threadov, krátkych wakeups alebo nevhodného polling loopu.

```bash
vmstat 1
pidstat -w 1
perf stat -p <PID> sleep 10
```

- `cs` vo `vmstat` — ukazuje celkovú frekvenciu prepnutí, ale bez procesného kontextu.
- `pidstat -w` — rozlišuje voluntary a involuntary context switches konkrétnych procesov.
- `perf stat` — poskytuje hlbšie CPU counters, ktoré pomáhajú potvrdiť overhead alebo cache problém.

## 5. CPU time states

CPU utilization je rozdelenie času medzi viac stavov. Samotná hodnota „CPU 90 %“ nestačí, pretože user computation, kernel work, interrupts a steal time majú odlišné príčiny.

- `us` — čas vykonávania user-space kódu; vysoká hodnota môže byť legitímny compute workload alebo busy loop.
- `sy` — čas v kerneli; môže rásť pri syscalls, networking, storage alebo kernel contention.
- `wa` — čas, keď CPU nemal runnable prácu a systém mal outstanding I/O; nie je to priamy súčet času všetkých procesov čakajúcich na I/O.
- `st` — čas odobratý hypervisorom virtuálnemu stroju; vysoká hodnota ukazuje contention mimo guest OS.
- `hi` a `si` — hardware a software interrupt processing, často relevantné pri network alebo device load.

```bash
mpstat -P ALL 1
top
sar -u 1
```

Interpretácia musí sledovať jednotlivé cores. Celkový priemer môže skryť jeden saturovaný core, na ktorom je serializovaný kritický thread.

## 6. Load average

Load average približuje priemerný počet taskov, ktoré sú runnable alebo v uninterruptible sleep. Preto môže byť vysoký aj pri nízkom CPU utilization, ak veľa taskov čaká na storage alebo network filesystem.

```bash
uptime
cat /proc/loadavg
nproc
```

Load `4` nemá univerzálny význam. Na dvojjadrovom hoste môže znamenať dlhú run queue, zatiaľ čo na 64-core hoste môže byť zanedbateľný.

Pri vysokom loade treba rozlíšiť:

1. **CPU queueing** — veľa `R` taskov čaká na cores.
2. **I/O blocking** — veľa `D` taskov čaká v kernelových I/O operáciách.
3. **Krátky burst** — 1-minútový priemer rastie, ale 15-minútový trend zostáva nízky.
4. **Trvalý constraint** — všetky intervaly ostávajú vysoké a latency rastie.

## 7. CPU affinity a topology

CPU affinity obmedzuje, na ktorých logical CPUs môže task bežať. Môže zlepšiť cache locality alebo izolovať latency-sensitive workload, ale zároveň môže vytvoriť lokálnu saturáciu pri voľnej kapacite inde.

```bash
lscpu -e
taskset -cp <PID>
cat /proc/<PID>/status | grep Cpus_allowed_list
```

SMT threads, cores, sockets a NUMA nodes nie sú ekvivalentné jednotky. Dva logical CPUs na rovnakom fyzickom core zdieľajú execution resources a neposkytujú rovnakú kapacitu ako dva samostatné cores.

## 8. NUMA

NUMA systém rozdeľuje CPUs a memory do nodes. Prístup k lokálnej pamäti je typicky lacnejší než prístup k memory page na inom socket-e.

```bash
numactl --hardware
numastat -p <PID>
lscpu
```

Výkon môže klesnúť, ak thread beží na jednom node a jeho working set leží prevažne na inom. Náhodné pinovanie však môže zhoršiť scheduler flexibility a memory balance, preto sa NUMA policy mení až po meraní locality a latency.

## 9. Virtual address space

Každý proces vidí vlastný virtuálny adresný priestor. Page tables mapujú virtual pages na fyzické frames, file-backed pages, swap alebo zatiaľ neprítomné pages.

```text
virtual address
  ↓ page-table lookup
present page → RAM
not present  → page fault → allocate / read file / swap-in
invalid      → fault signal, napr. SIGSEGV
```

`malloc()` často rezervuje virtuálny rozsah bez okamžitého pridelenia fyzickej RAM. Fyzická page sa môže prideliť až pri prvom zápise cez demand paging.

Tento model umožňuje izoláciu, shared libraries, memory-mapped files a copy-on-write. Zároveň znamená, že virtual size a resident memory sú odlišné metriky.

## 10. Page fault

Page fault je kontrolovaný prechod do kernelu, keď potrebné mapovanie nie je pripravené. Nie každý page fault je chyba.

- **Minor fault** — dáta už sú v RAM alebo sa page vytvorí bez čítania zo storage, napríklad pri copy-on-write.
- **Major fault** — kernel musí načítať page zo storage alebo swapu, čo prináša výrazne vyššiu latency.
- **Protection fault** — proces pristúpil k page spôsobom, ktorý permissions nepovoľujú; môže skončiť `SIGSEGV`.

```bash
pidstat -r 1
ps -o pid,min_flt,maj_flt,comm -p <PID>
perf stat -e page-faults,major-faults -p <PID> sleep 10
```

Rast major faults spolu s latency môže signalizovať working set väčší než dostupná RAM alebo cold-cache workload.

## 11. VIRT, RSS a PSS

Memory metrics merajú odlišné pohľady:

- **VIRT/VSZ** — celý virtual address space vrátane rezervovaných ranges a mapped files; veľká hodnota nemusí spotrebúvať RAM.
- **RSS** — resident pages procesu v RAM, pričom shared pages sa započítajú každému procesu celé.
- **PSS** — shared pages rozdelí pomerne medzi procesy, preto je vhodnejší na odhad reálneho podielu procesu.
- **USS** — pages unikátne danému procesu; približuje RAM, ktorá by sa uvoľnila po jeho ukončení.

```bash
ps -o pid,comm,vsz,rss,%mem -p <PID>
cat /proc/<PID>/smaps_rollup
pmap -x <PID>
```

Jedna hodnota RSS nestačí na diagnózu leak-u. Treba sledovať časovú sériu, workload a rozdelenie anonymous/file-backed memory.

## 12. Anonymous a file-backed memory

Anonymous memory zahŕňa heap, stack a ďalšie pages bez trvalého file backing. Pri pressure sa môže presunúť do swapu alebo zostať resident, kým kernel nenájde inú cestu reclaimu.

File-backed memory zahŕňa executable mappings, shared libraries a page cache. Čisté file-backed pages možno zahodiť a neskôr znovu načítať, preto sú často lacnejšie na reclaim než anonymous pages.

Dirty file-backed pages treba pred reclaimom zapísať. Ak storage nestíha writeback, memory pressure sa môže premeniť na I/O stalls.

## 13. Page cache

Kernel používa voľnú RAM ako page cache, aby opakované reads nemuseli ísť na storage. Nízke `free` preto môže byť zdravé, ak je veľká časť pamäte reclaimable a `MemAvailable` ostáva dostatočné.

```bash
free -h
cat /proc/meminfo
```

- `MemFree` — úplne nepoužité pages; samo osebe má malú diagnostickú hodnotu.
- `Cached` a `Buffers` — pamäť používaná na cache a metadata.
- `MemAvailable` — odhad pamäte dostupnej pre nové workloady bez výrazného swapovania.
- `Dirty` a `Writeback` — pages čakajúce na zápis alebo práve zapisované na storage.

Page cache nie je „zbytočne obsadená RAM“. Je to adaptívna vrstva výkonu, ktorú kernel pri potrebe reclaimuje.

## 14. Reclaim

Pri memory pressure kernel hľadá pages, ktoré možno uvoľniť. Reclaim môže zahodiť clean cache, zapísať dirty pages, swapovať anonymous memory alebo compactovať fyzickú pamäť.

```text
allocation request
  ↓
free pages nestačia
  ↓
reclaim clean pages
  ↓
writeback dirty pages / swap anonymous pages
  ↓
compaction
  ↓
ak stále nemožné → OOM handling
```

Reclaim nie je bezplatný. Direct reclaim môže zablokovať aplikačný thread a memory pressure sa potom prejaví ako latency aj bez OOM killu.

## 15. Swap

Swap umožňuje odsunúť menej aktívne anonymous pages mimo RAM. Mierne použitie swapu môže byť normálna policy; problémom je aktívny swap churn, keď working set neustále putuje medzi RAM a storage.

```bash
swapon --show
vmstat 1
sar -W 1
```

- `si` — množstvo dát čítaných zo swapu späť do RAM; trvalý rast môže priamo zvyšovať latency.
- `so` — množstvo dát zapisovaných do swapu; jednorazový rast nemusí byť incident.
- Thrashing — vysoké `si/so`, I/O pressure a nízky useful throughput znamenajú, že systém väčšinu času presúva pages.

`swappiness` ovplyvňuje relatívnu ochotu swapovať, ale nie je jednoduchým percentom alebo hard thresholdom. Zmena bez merania môže zhoršiť page-cache alebo application behavior.

## 16. Memory overcommit

Linux môže povoliť rezerváciu väčšieho virtual memory priestoru, než je okamžite dostupná RAM a swap. Predpokladá, že všetky procesy nepoužijú maximum naraz.

```bash
sysctl vm.overcommit_memory
sysctl vm.overcommit_ratio
```

Overcommit zvyšuje utilization, ale prináša riziko neskorého zlyhania pri reálnom dotyku pages. Aplikácia môže úspešne alokovať address space a zlyhať až neskôr, keď kernel nedokáže prideliť fyzickú memory.

Pre workloady s prísnou predvídateľnosťou treba overiť allocation behavior, cgroup limits a peak concurrency namiesto spoliehania sa iba na priemernú spotrebu.

## 17. Cgroup CPU limits

Cgroup môže obmedziť CPU aj vtedy, keď host má voľné cores. CPU quota povoľuje iba určitý čas v každom period intervale; po jeho vyčerpaní sú tasks throttled.

```bash
cat /sys/fs/cgroup/<group>/cpu.max
cat /sys/fs/cgroup/<group>/cpu.stat
systemctl show <unit> -p CPUQuotaPerSecUSec -p ControlGroup
```

Vysoký `nr_throttled` alebo `throttled_usec` spolu s latency ukazuje cgroup-local constraint. Host-wide CPU utilization preto nemusí vysvetliť výkon kontajnera alebo systemd služby.

CPU weight neurčuje hard cap. Rozdeľuje relatívny podiel pri contention, takže jeho efekt je viditeľný až keď viac groups súťaží o CPU.

## 18. Cgroup memory limits

Memory cgroup účtuje pamäť workloadu a môže vyvolať local reclaim alebo cgroup OOM skôr, než sa vyčerpá RAM hosta.

```bash
cat /sys/fs/cgroup/<group>/memory.current
cat /sys/fs/cgroup/<group>/memory.max
cat /sys/fs/cgroup/<group>/memory.events
cat /sys/fs/cgroup/<group>/memory.stat
```

- `memory.current` — aktuálne účtovaná memory v cgroup.
- `memory.max` — hard limit; po jeho dosiahnutí môže nasledovať intenzívny reclaim alebo OOM.
- `memory.events` — počíta udalosti ako `high`, `max`, `oom` a `oom_kill`.
- `memory.high` — soft throttling boundary, ktorá vytvára reclaim pressure pred hard limitom.

Kontajner preto môže byť OOM-killed pri voľnej RAM hosta. Autoritatívna hranica je cgroup policy, nie globálne `free -h`.

## 19. OOM handling

OOM nastáva, keď allocation nemožno uspokojiť ani po reclaim mechanizmoch. Kernel alebo cgroup OOM logic vyberie victim process, aby obnovila schopnosť systému pokračovať.

```bash
journalctl -k -b | grep -i -E 'out of memory|oom|killed process'
cat /proc/<PID>/oom_score
cat /proc/<PID>/oom_score_adj
```

Výber ovplyvňuje memory usage, badness score, `oom_score_adj` a scope OOM udalosti. Cgroup OOM môže obmedziť dopad na jednu službu, zatiaľ čo host-wide OOM ohrozuje celý systém.

OOM kill je recovery action, nie root cause. Root cause môže byť leak, workload burst, príliš nízky limit, neobmedzená concurrency, veľká cache alebo nesprávne capacity assumptions.

## 20. Memory leak, cache a allocator behavior

Memory leak znamená, že aplikácia drží objekty bez ďalšej potreby a retained memory dlhodobo rastie. Rast RSS však môže mať aj legitímne príčiny.

- Application cache — zámerne drží dáta pre výkon a mala by mať limit alebo eviction policy.
- Allocator arenas — runtime môže uvoľniť objekty interne, ale nevrátiť všetky pages kernelu.
- Page cache — patrí kernelu, nie heapu aplikácie.
- Workload growth — väčšia concurrency alebo dataset prirodzene zväčší working set.

Diagnostika musí korelovať RSS/PSS, heap profiling, request volume, cache metrics a čas. Jeden snapshot nedokáže odlíšiť leak od warm-upu.

## 21. Pressure Stall Information

PSI meria čas, počas ktorého aspoň niektoré alebo všetky tasks čakali pre nedostatok CPU, memory alebo I/O capacity. Na rozdiel od utilization ukazuje priamo stall dopad.

```bash
cat /proc/pressure/cpu
cat /proc/pressure/memory
cat /proc/pressure/io
```

- `some` — aspoň jeden task bol stallovaný; pomáha zachytiť čiastočnú degradáciu.
- `full` — všetky non-idle tasks boli súčasne stallované; signalizuje výrazný constraint.
- `avg10`, `avg60`, `avg300` — kĺzavé priemery percenta času, nie jednoduché percento utilization.

Vysoké memory PSI môže odhaliť reclaim stalls skôr než OOM. Vysoké CPU PSI pri relatívne nízkom host utilization môže ukázať cgroup throttling alebo affinity constraint.

## 22. Diagnostika vysokého loadu pri nízkom CPU

Takýto symptóm typicky znamená, že tasks nie sú prevažne v user computation. Treba overiť uninterruptible sleep a downstream I/O.

```bash
vmstat 1
ps -eo state,pid,tid,wchan:32,comm | awk '$1 ~ /^D/'
iostat -xz 1
journalctl -k -b
```

1. **Rozlíš `R` a `D` tasks** — `R` ukazuje CPU queue, `D` kernel I/O wait.
2. **Identifikuj wait channel** — `wchan` približne ukáže, v ktorej kernelovej funkcii task čaká.
3. **Skontroluj storage alebo NFS latency** — vysoké await, queue depth alebo timeouts potvrdia I/O constraint.
4. **Skontroluj kernel logs** — device resets, filesystem errors alebo network stalls môžu byť skutočnou príčinou.
5. **Koreluj so zmenou workloadu** — nový batch job alebo backup môže vytvoriť dočasný tlak bez aplikačnej chyby.

## 23. Diagnostika jedného saturovaného core

Jeden core na 100 % pri voľných ostatných cores ukazuje serializovaný execution path alebo affinity restriction.

```bash
mpstat -P ALL 1
ps -eLo pid,tid,psr,pcpu,stat,comm --sort=-pcpu | head
 taskset -cp <PID>
```

Možné príčiny zahŕňajú single-threaded event loop, hot lock, jednu queue, interrupt affinity alebo explicitné CPU pinning. Riešením nie je automaticky pridať cores; workload musí vedieť paralelizovať kritickú cestu.

## 24. Diagnostika memory incidentu

Postup musí odlíšiť host pressure, cgroup pressure a aplikačný rast:

1. **Potvrď scope** — zisti, či problém ovplyvňuje celý host alebo jednu service cgroup.
2. **Skontroluj available memory a swap activity** — `MemAvailable`, `si/so` a PSI ukážu reálny tlak.
3. **Identifikuj consumers** — RSS/PSS, `memory.current` a process breakdown ukážu, kde je working set.
4. **Rozlíš anonymous a file-backed memory** — leak a page cache vyžadujú odlišnú nápravu.
5. **Skontroluj cgroup events** — `oom_kill`, `high` a `max` potvrdia local limits.
6. **Skontroluj OOM evidence** — kernel log ukáže victim a scope udalosti.
7. **Koreluj s workloadom a deploymentom** — bez časovej väzby nemožno určiť, či ide o leak, burst alebo nový limit.
8. **Over nápravu** — po zmene limitu alebo kódu sleduj latency, PSI, reclaim a stabilitu, nie iba absenciu ďalšieho OOM.

## 25. Anti-patterny

### Load average interpretovaný ako CPU percento

Tím škáluje CPU, hoci load tvoria `D` tasks čakajúce na NFS. Nové cores neznížia storage latency a môžu iba zvýšiť počet súbežných I/O requestov.

### Cache vyčistená pri každom incidente

`drop_caches` krátkodobo zvýši `free`, ale odstráni užitočnú page cache a môže spôsobiť cold-read storm. Najprv treba potvrdiť, že cache je príčinou a nie zdravým využitím RAM.

### Zvýšenie memory limitu bez modelu

Limit sa zvýši po OOM, ale leak alebo neobmedzená concurrency zostáva. Incident sa iba posunie a blast radius pri ďalšom zlyhaní rastie.

### Priemer skryje lokálnu saturáciu

Host CPU vyzerá na 25 %, ale jeden core je saturovaný kritickým threadom. Diagnostika musí pozerať per-CPU a per-thread údaje, nie iba globálny priemer.

## 26. Kontrolné otázky

1. Aký je rozdiel medzi running a runnable taskom?
2. Prečo load average nie je CPU percentage?
3. Ako sa líšia user, system, iowait a steal time?
4. Prečo môže vysoký context-switch rate znamenať lock contention?
5. Aký je rozdiel medzi minor a major page faultom?
6. Ako sa líšia VIRT, RSS, PSS a USS?
7. Prečo nízke `MemFree` nemusí znamenať memory incident?
8. Ako file-backed a anonymous memory ovplyvňujú reclaim?
9. Kedy je swap normálny a kedy ide o thrashing?
10. Prečo host-wide voľná RAM nevylučuje cgroup OOM?
11. Ako PSI dopĺňa utilization metriky?
12. Ako by si rozlíšil leak, cache warm-up a rast workloadu?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Storage, mounty a filesystems](storage-mounts-and-filesystems.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Linux networking →](linux-networking.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
