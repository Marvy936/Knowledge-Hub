# Memory and CPU Fundamentals

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Kernel a user space](kernel-and-user-space.md), [Procesy, thready, PID a signals](processes-threads-pid-signals.md)
- Súvisiace témy: cgroups, scheduling, performance troubleshooting, containers, capacity planning

## 1. Definícia

CPU a memory sú základné vykonávacie zdroje procesu. CPU poskytuje čas na vykonávanie inštrukcií; memory poskytuje virtuálny adresný priestor mapovaný kernelom na fyzické stránky, page cache, swap alebo zdieľané mapovania.

Výkonový problém nemožno spoľahlivo diagnostikovať iba tvrdením „CPU je vysoké“ alebo „RAM je plná“. Treba rozlíšiť využitie, saturáciu, čakanie, tlak na zdroj a správanie konkrétnych procesov.

## 2. CPU execution model

Linux scheduler prideľuje runnable threadom čas na logických CPU.

Zjednodušený stav threadu:

```text
running
   ↑
runnable ── scheduler queue
   ↓
sleeping / waiting na I/O, lock alebo timer
```

Dôležité rozlíšenie:

- **utilization**: akú časť času CPU vykonávalo prácu,
- **saturation**: koľko runnable práce čaká na CPU,
- **latency**: ako dlho thread čaká, kým sa dostane na CPU.

CPU môže byť na 100 % bez závažného problému, ak systém plní požadovanú prácu a queue nerastie. Naopak, pri krátkych latency-sensitive úlohách môže byť problém aj pri nižšom priemernom využití.

## 3. CPU time categories

Nástroje typicky rozlišujú:

- `user` — vykonávanie kódu v user space,
- `system` — vykonávanie kernel kódu v mene procesov,
- `idle` — CPU nemá runnable prácu,
- `iowait` — CPU je idle a systém eviduje outstanding block I/O,
- `steal` — hypervisor použil čas, ktorý guest očakával,
- `irq` a `softirq` — spracovanie interruptov.

`iowait` nie je presný čas konkrétneho procesu čakajúceho na disk a vysoká hodnota automaticky neznamená chybný disk. Je to systémová indícia, ktorú treba korelovať s block I/O latency a queue depth.

## 4. Load average

`load average` predstavuje priemerný počet úloh, ktoré sú runnable alebo v neinterruptible sleep, typicky kvôli I/O.

```bash
uptime
cat /proc/loadavg
```

Hodnota sa interpretuje voči počtu logických CPU:

```text
load 4 na 4 CPU
≈ systém má približne plnú runnable kapacitu

load 20 na 4 CPU
≈ významná queue alebo veľa uninterruptible tasks
```

Load nie je percento CPU a môže rásť aj pri I/O alebo lock probléme.

## 5. Procesy a thready

Proces môže mať viac threadov a využívať viac CPU súčasne.

```bash
ps -eo pid,ppid,comm,stat,pcpu,pmem,nlwp --sort=-pcpu
ps -L -p PID -o pid,tid,psr,stat,pcpu,comm
pidstat -p PID 1
pidstat -t -p PID 1
```

`%CPU` nad 100 % pri procese môže znamenať, že viac threadov súčasne používa viac jadier.

## 6. Context switches a interrupts

Context switch nastáva, keď CPU prestane vykonávať jeden thread a začne iný. Má cenu: scheduler bookkeeping, cache disruption a možné TLB effects.

```bash
vmstat 1
pidstat -w 1
cat /proc/interrupts
```

Veľký počet context switches nie je automaticky problém. Dôležité je, či koreluje s latency, lock contention, príliš veľkým počtom threadov alebo krátkymi wakeups.

## 7. Virtual memory

Každý proces vidí vlastný virtuálny adresný priestor. Kernel mapuje virtuálne stránky na:

- anonymnú memory,
- file-backed mappings,
- shared libraries,
- page cache,
- swap,
- memory-mapped devices.

Proces preto nemusí mať všetku adresovanú memory fyzicky resident v RAM.

Relevantné pojmy:

- **VSS/VSZ** — veľkosť virtuálneho adresného priestoru,
- **RSS** — resident pages aktuálne v RAM,
- **PSS** — zdieľané stránky pomerne rozdelené medzi procesy,
- **anonymous memory** — heap, stack a ďalšie nefile-backed stránky,
- **page cache** — RAM použitá na cache filesystem dát.

## 8. Prečo „used memory“ nie je automaticky problém

Linux používa voľnú RAM ako cache. `free` preto rozlišuje `free`, `buff/cache` a odhad `available`.

```bash
free -h
cat /proc/meminfo
```

`MemAvailable` je praktickejší odhad, koľko memory možno prideliť bez výrazného swapovania. Nízka hodnota spolu s rastúcim reclaim, swap I/O a PSI signalizuje tlak.

## 9. Page faults

Page fault nastane, keď požadovaná virtuálna stránka nie je okamžite mapovaná spôsobom potrebným pre operáciu.

- **minor fault** — stránku možno sprístupniť bez diskového I/O,
- **major fault** — typicky vyžaduje načítanie zo storage.

```bash
pidstat -r 1
ps -o pid,min_flt,maj_flt,rss,vsz,comm -p PID
```

Page faults sú normálnou súčasťou demand paging. Problémom je vysoká miera major faults alebo reclaim pod záťažou.

## 10. Swap

Swap poskytuje backing store pre niektoré anonymné stránky a môže uvoľniť RAM pre aktívnejšie dáta alebo page cache.

```bash
swapon --show
vmstat 1
cat /proc/swaps
```

Vo `vmstat` sleduj:

- `si` — swap in,
- `so` — swap out.

Samotná existencia použitého swapu nie je dôkaz aktuálneho problému. Kritické je aktívne swapovanie, latency a thrashing.

## 11. Memory reclaim a thrashing

Pri memory pressure sa kernel snaží získať stránky:

1. odstraňuje clean page cache,
2. zapisuje dirty pages,
3. presúva eligible anonymous pages do swapu,
4. aktivuje direct reclaim v alokujúcich procesoch,
5. pri zlyhaní môže spustiť OOM killer.

Thrashing nastáva, keď systém trávi veľkú časť času presúvaním stránok namiesto užitočnej práce.

## 12. OOM killer

Ak kernel nevie uspokojiť memory allocation, môže vybrať proces na ukončenie.

```bash
dmesg -T | grep -i -E 'out of memory|killed process|oom'
journalctl -k -g 'Out of memory|Killed process|oom'
```

Výber ovplyvňuje spotreba memory, `oom_score`, `oom_score_adj`, cgroup hranice a ďalšie faktory.

```bash
cat /proc/PID/oom_score
cat /proc/PID/oom_score_adj
```

V kontajneroch môže nastať cgroup OOM bez globálneho vyčerpania host memory.

## 13. Pressure Stall Information

PSI meria, akú časť času úlohy čakali kvôli nedostupnosti CPU, memory alebo I/O zdroja.

```bash
cat /proc/pressure/cpu
cat /proc/pressure/memory
cat /proc/pressure/io
```

Polia `some` a `full` odlišujú či bol blokovaný aspoň jeden task alebo všetky relevantné tasks. PSI je vhodný na detekciu saturácie a pre alerting, pretože meria dopad čakania, nie iba využitie.

## 14. Základný diagnostický postup

```bash
uptime
vmstat 1
free -h
ps -eo pid,comm,stat,pcpu,pmem,rss --sort=-pcpu | head
ps -eo pid,comm,stat,pcpu,pmem,rss --sort=-rss | head
pidstat 1
cat /proc/pressure/cpu
cat /proc/pressure/memory
```

Postup:

1. potvrď používateľský symptóm a časové okno,
2. zisti load, runnable queue a blocked tasks,
3. rozlíš user/system/iowait/steal,
4. identifikuj procesy a thready,
5. skontroluj memory availability, reclaim a swap activity,
6. over PSI a OOM udalosti,
7. koreluj s application latency, throughput a deploymentmi.

## 15. Časté omyly

### „100 % CPU znamená, že treba viac CPU“

Nie vždy. Príčinou môže byť busy loop, zlá query, lock contention, príliš veľa retry pokusov alebo legitímne dávkové spracovanie.

### „Free memory musí byť vysoká“

Nie. Linux zámerne používa memory na cache. Dôležitejšie sú `MemAvailable`, reclaim, swap activity a latency.

### „Load average je CPU utilization“

Nie. Zahŕňa runnable aj určité blocked tasks.

### „Použitý swap znamená aktuálne thrashing“

Nie. Stránky môžu zostať v swap bez aktuálneho I/O. Sleduj `si`, `so`, page faults a latency.

### „RSS sa dá jednoducho sčítať“

Zdieľané stránky by sa tým započítali viackrát. Pri presnejšej atribúcii použi PSS.

## 16. Kontrolné otázky

1. Aký je rozdiel medzi CPU utilization a saturation?
2. Prečo load average môže rásť aj pri nízkom CPU utilization?
3. Aký je rozdiel medzi VSS, RSS a PSS?
4. Prečo vysoké `buff/cache` nie je automaticky memory leak?
5. Ako sa líši minor a major page fault?
6. Čo ukazuje PSI oproti obyčajnému percentu využitia?
7. Ako rozlíšiš globálny OOM od cgroup OOM?
8. Prečo samotný reštart procesu nie je diagnostikou memory problému?
