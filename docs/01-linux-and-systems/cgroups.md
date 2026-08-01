# Linux control groups — cgroups

Control groups organizujú processes do hierarchie pre resource accounting, limits, prioritization a pressure control. V cgroup v2 má každý process jedno miesto v unified hierarchy a controllers distribuujú CPU, memory, I/O a PIDs policy cez parent-child boundaries.

```text
service/container identity
→ cgroup placement
→ inherited a local controller configuration
→ effective quota/weight/limit
→ runtime consumption a pressure
→ throttle, reclaim, OOM alebo admission failure
```

Configured hodnota nie je automaticky effective capacity. CPU quota sa interpretuje spolu s periodou a konkurenciou, memory limit spolu s page cache, swap a reclaim a I/O control závisí od device mappingu. Host môže mať voľné resources, kým workload je lokálne throttled alebo dostane cgroup OOM. Diagnostika preto číta `/proc/<pid>/cgroup`, effective files v `cgroup.controllers` hierarchy, pressure stall information a workload outcome namiesto iba host-wide utilization.

## 1. Definícia

Control groups, skrátene cgroups, sú kernelový mechanizmus na hierarchické zoskupovanie procesov a riadenie ich spotreby zdrojov. Cgroup môže merať, relatívne prioritizovať, mäkko brzdiť alebo tvrdo obmedziť CPU, memory, I/O a počet taskov celého workloadu.

Namespaces odpovedajú na otázku **čo proces vidí**. Cgroups odpovedajú na otázku **koľko zdrojov môže skupina procesov spotrebovať a ako sa o ne delí s ostatnými skupinami**.

```text
namespace → izolovaný pohľad
cgroup    → accounting, priority, pressure a limit
```

Cgroup nie je iba kontajnerová vlastnosť. Systemd používa cgroups na správu services, user sessions, scopes a slices aj na hoste bez aplikačných kontajnerov.

## 2. Prečo je potrebná skupinová kontrola

Aplikácia často nie je jeden PID. Môže vytvárať workers, helper procesy, kompilátory alebo stovky threadov, takže limit iba na main PID by sa dal obísť alebo by nezachytil skutočný resource footprint.

Cgroup drží procesný strom workloadu v spoločnej policy boundary:

```text
example.service cgroup
  ├── main process
  ├── worker 1
  ├── worker 2
  └── helper subprocess
```

Získame tým:

- **Skupinový accounting** — CPU time, memory charge, I/O a počet taskov sa sledujú pre celý workload.
- **Relatívnu prioritu** — pri contention môže kritická služba dostať vyššiu váhu než batch job.
- **Hard limits** — runaway workload nemôže neobmedzene spotrebovať hostovú RAM alebo vytvárať procesy.
- **Hierarchické rozdelenie** — parent môže prideliť budget tímu, službe alebo Podu a child groups ho ďalej rozdelia.
- **Prevádzkovú identitu** — service manager vie zastaviť, merať a diagnostikovať všetky procesy unit bez PID file heuristiky.

## 3. Cgroup v1 a cgroup v2

Cgroup v1 umožňovala samostatnú hierarchy pre každý controller. CPU, memory a blkio preto mohli zoskupovať procesy odlišne, čo komplikovalo delegáciu a konzistentné riadenie workloadu.

Cgroup v2 používa jednu unified hierarchy. Proces má jednu cestu v strome a controllery nad ňou aplikujú koordinovanú policy.

Kontrola typu mountu:

```bash
stat -fc %T /sys/fs/cgroup
```

Typický cgroup v2 výsledok:

```text
cgroup2fs
```

Moderné distribúcie, systemd a kontajnerové platformy preferujú cgroup v2. Dostupnosť konkrétneho controlleru alebo field-u však stále závisí od kernelu, systemd, runtime a device topology.

## 4. Unified hierarchy

Cgroup v2 je strom. Každý adresár reprezentuje cgroup objekt a jeho súbory predstavujú controller knobs, accounting alebo events.

```text
/sys/fs/cgroup
  ├── system.slice
  │    ├── ssh.service
  │    └── example.service
  ├── user.slice
  └── machine.slice
```

Parent policy ovplyvňuje descendants. Child nemôže získať viac resource authority, než mu umožní parent hierarchy.

To má dva dôsledky:

- limit na parent cgroup agreguje všetky child workloads,
- child limit sa vyhodnocuje súčasne s limitmi všetkých ancestors.

Proces preto môže mať vlastný `memory.max=2G`, ale stále naraziť na parent limit, ktorý zdieľa s ďalšími siblings.

## 5. Členstvo procesu

Cgroup membership procesu je viditeľný cez:

```bash
cat /proc/<pid>/cgroup
```

Cgroup v2 príklad:

```text
0::/system.slice/example.service
```

Proces sa môže presunúť zápisom PID do `cgroup.procs`, ak má caller potrebné oprávnenia a hierarchy pravidlá to dovoľujú. V systemd-managed strome sa však PIDs nemajú presúvať ručne bez vedomia managera, pretože by sa porušilo ownership a lifecycle unit.

Child proces typicky zdedí cgroup membership parenta. Preto subprocess vytvorený službou zostáva v jej resource boundary, pokiaľ ho oprávnený manager explicitne nepresunie.

## 6. Processes verzus threads

`cgroup.procs` pracuje s process-level membership, zatiaľ čo `cgroup.threads` podporuje thread-granular model v threaded subtree. Väčšina service a container use cases používa domain cgroups, kde sa workload riadi ako process group.

Threaded cgroups sú pokročilý mechanizmus a nie všetky controllery sa správajú rovnako v threaded subtree. Náhodné rozdeľovanie threadov jednej aplikácie medzi resource groups môže narušiť jej scheduler, memory locality a accounting predpoklady.

Pre DevOps prevádzku je bezpečný základ:

```text
jedna service / container / Pod boundary
  → jedna jasne vlastnená domain cgroup subtree
```

## 7. Controllers a subtree activation

Kernel môže podporovať viac controllerov, ale parent ich musí sprístupniť descendants cez `cgroup.subtree_control`.

```bash
cat /sys/fs/cgroup/cgroup.controllers
cat /sys/fs/cgroup/cgroup.subtree_control
```

Typické controllery:

- **`cpu`** — relatívna váha, quota a CPU accounting.
- **`cpuset`** — povolené CPU cores a NUMA memory nodes.
- **`memory`** — memory accounting, protection, reclaim boundaries a hard limit.
- **`io`** — block I/O accounting, weight a limity podľa zariadenia.
- **`pids`** — maximálny počet procesov a threadov.
- **`hugetlb`** — accounting a limit explicitných huge pages.
- **`rdma` alebo `misc`** — špecializované zdroje podľa kernelu a platformy.

To, že controller existuje v `cgroup.controllers`, neznamená, že je aktívny pre konkrétnu child cgroup. Treba overiť celý ancestor path a delegáciu.

## 8. No-internal-process rule

Pri domain controlleroch cgroup v2 platí princíp, že cgroup, ktorá distribuuje controllery do child subtree, nemá zároveň držať bežné workload procesy. Interný node slúži ako organizačný a policy parent; reálne processes patria do descendants.

```text
team.slice       policy parent, bez workload procesov
  ├── api.service
  └── worker.service
```

Toto pravidlo zjednodušuje hierarchické resource distribution. Bez neho by parentove vlastné processes súťažili s descendants nejasným spôsobom.

Systemd tento model spravuje cez slices a service cgroups. Ručné vytváranie stromu bez pochopenia pravidla často vedie k chybe pri aktivácii controlleru.

## 9. CPU accounting

CPU controller sleduje CPU čas spotrebovaný cgroup. `cpu.stat` obsahuje celkové usage a pri quota režime aj throttling counters.

```bash
cat /sys/fs/cgroup/<path>/cpu.stat
```

Dôležité hodnoty typicky zahŕňajú:

- **`usage_usec`** — agregovaný CPU čas workloadu.
- **`user_usec` a `system_usec`** — rozdelenie medzi user a kernel execution.
- **`nr_periods`** — počet quota periods, počas ktorých bol workload aktívny.
- **`nr_throttled`** — počet periods, v ktorých bol throttled.
- **`throttled_usec`** — čas, počas ktorého nemohol bežať pre vyčerpanú quota.

CPU usage a throttling treba interpretovať spolu. Workload môže používať menej CPU v priemere, ale pravidelne vyčerpať krátky quota budget a vytvárať tail latency.

## 10. CPU weight

`cpu.weight` určuje relatívny podiel CPU počas contention. Nie je to pevná rezervácia ani hard limit.

```text
service A weight 100
service B weight 200
```

Keď sú obe cgroups runnable a súťažia o rovnaké CPU, service B má približne vyššiu scheduling weight. Keď service A nemá prácu, B môže použiť voľnú CPU kapacitu aj nad svoj relatívny podiel.

Systemd:

```ini
[Service]
CPUWeight=200
```

Weight je vhodný na work-conserving prioritu. Zachováva využitie voľného CPU a prejaví sa až pri skutočnom contention.

## 11. CPU quota

`cpu.max` nastavuje maximálny CPU budget v každom period.

```text
50000 100000
```

Tento príklad povoľuje 50 ms CPU času za 100 ms period, teda približne `0.5 CPU`. Hodnota:

```text
max 100000
```

znamená bez hard quota pri danom period.

Systemd:

```ini
[Service]
CPUQuota=50%
```

Quota môže throttliť workload aj na hoste s idle cores. Dôvodom je, že cgroup vyčerpala svoj period budget, nie že host nemá fyzickú kapacitu.

Pre latency-sensitive službu môže nízka quota vytvoriť pravidelný sawtooth pattern:

```text
burst execution → budget exhausted → throttle → next period → burst
```

Preto sa quota nastavuje podľa burst modelu a meraného throttlingu, nie iba podľa priemerného CPU usage.

## 12. Weight verzus quota

Weight a quota riešia rozdielne problémy.

- **Weight** — rozhoduje, ako sa delí nedostatkový CPU čas medzi runnable groups.
- **Quota** — nastavuje hornú hranicu CPU bandwidth aj vtedy, keď je voľná kapacita.

Pre väčšinu zdieľaných služieb je weight menej deštruktívny, pretože zachováva work-conserving scheduling. Quota je vhodná, keď workload nesmie prekročiť konkrétny budget alebo musí byť chránený susedný systém.

Oba mechanizmy možno kombinovať. Potom treba diagnostikovať, či latency vzniká hostovým contention, nízkou weight alebo vlastnou quota.

## 13. Cpuset controller

Cpuset určuje, na ktorých logical CPUs a NUMA nodes môže workload bežať a alokovať memory.

```text
cpuset.cpus
cpuset.cpus.effective
cpuset.mems
cpuset.mems.effective
```

`effective` hodnoty ukazujú skutočný intersection s parent policy a online topology. Child nemôže používať CPU alebo memory node, ktorý parent nepovolil.

Cpuset je placement policy, nie CPU bandwidth limit. Workload pinovaný na dva cores môže tie cores použiť naplno, pokiaľ ho neobmedzí quota alebo scheduler contention.

Nesprávny cpuset môže:

- preťažiť jeden core,
- znížiť scheduler flexibility,
- zvýšiť remote NUMA access,
- vytvoriť nerovnomerné IRQ a workload placement,
- zlyhať po CPU hotplug alebo topology zmene.

Pinning má vychádzať z workload profilingu a NUMA modelu.

## 14. Memory accounting

Memory controller účtuje viac než RSS jedného procesu. Cgroup memory môže zahŕňať anonymous pages, page cache, kernel allocations, socket buffers a ďalšie kategórie podľa kernelovej implementácie.

Dôležité fields:

```text
memory.current
memory.peak
memory.stat
memory.events
memory.swap.current
```

`memory.current` je agregovaný charge celej cgroup subtree. Nemusí sa rovnať súčtu RSS z `ps`, pretože accounting boundary a memory kategórie sú odlišné.

`memory.stat` pomáha rozložiť usage na anonymous, file-backed, slab, workingset a reclaim aktivity. Jedno číslo bez breakdownu nestačí na rozlíšenie leak-u od page cache alebo kernel pressure.

## 15. Memory protection: `memory.min` a `memory.low`

Memory protection neurčuje maximum. Chráni časť memory cgroup pred reclaimom počas pressure.

- **`memory.min`** — silná ochrana; kernel sa snaží nechránenú memory reclaimovať skôr a chránený rozsah považuje za nedotknuteľný, pokiaľ je to možné.
- **`memory.low`** — best-effort ochrana; workload má preferenciu pri reclaim rozhodovaní, ale pri silnom tlaku môže byť memory stále reclaimovaná.

Protection je hierarchická. Child ochrana je efektívna iba v rámci budgetu, ktorý mu poskytuje parent.

Nadmerné protections môžu zhoršiť host-wide OOM riziko. Ak všetky workloads požadujú chránenú memory nad fyzickú kapacitu, kernel nemá dostatočne reclaimable priestor.

## 16. `memory.high`

`memory.high` je pressure boundary, nie okamžitý kill limit. Keď cgroup prekročí túto hodnotu, jej processes čelia intenzívnejšiemu reclaimu a throttlingu.

```ini
[Service]
MemoryHigh=1G
```

Cieľom je vytvoriť kontrolovanú degradáciu pred hard OOM. Workload môže pokračovať, ale allocation a reclaim latency ho spomalia a `memory.events` zaznamená `high` udalosti.

`memory.high` je vhodný na signalizáciu a ochranu hosta, ak aplikácia dokáže reagovať na memory pressure. Bez monitoringu môže vyzerať iba ako náhodná latency.

## 17. `memory.max`

`memory.max` je hard boundary pre chargeovanú memory cgroup. Keď allocation prekročí limit a reclaim nestačí, vznikne cgroup-local OOM.

```ini
[Service]
MemoryMax=1500M
```

Host môže mať voľnú RAM, ale workload stále zlyhá, pretože jeho vlastná hierarchy policy nepovoľuje ďalší charge.

Hard limit chráni host a sibling workloads, ale mení failure mode aplikácie. Namiesto host-wide memory pressure môže jeden proces dostať OOM kill alebo celá service skončiť podľa manager policy.

Limit musí počítať s:

- application heap,
- page cache charge,
- thread stacks,
- socket buffers,
- runtime overhead,
- burst počas reloadu alebo compaction,
- child procesmi.

## 18. Swap control

Cgroup v2 môže samostatne riadiť swap usage:

```text
memory.swap.current
memory.swap.max
memory.swap.events
```

`memory.swap.max=0` zakáže workloadu chargeovať swap. To môže znížiť nepredvídateľnú swap latency, ale zároveň zvyšuje pravdepodobnosť skoršieho OOM pri anonymous memory pressure.

Swap policy musí zodpovedať workloadu. Latency-sensitive služba, batch job a hostový agent nemusia mať rovnaký kompromis medzi reclaim flexibility a response time.

Host-wide swap availability a cgroup-local swap limit sú dve rozdielne vrstvy. Diagnostika musí skontrolovať obe.

## 19. Memory events a local OOM

`memory.events` sumarizuje významné pressure a failure udalosti:

```bash
cat /sys/fs/cgroup/<path>/memory.events
```

Typické counters:

- **`low`** — reclaim zasahoval protected region.
- **`high`** — cgroup prekročila `memory.high` a bola throttled/reclaimed.
- **`max`** — allocation narazila na `memory.max` boundary.
- **`oom`** — kernel vstúpil do OOM handlingu pre cgroup.
- **`oom_kill`** — OOM handling ukončil task.

Cgroup-local OOM treba korelovať s kernel journalom a service state. Aplikácia môže skončiť signalom bez jasnej vlastnej log message, pretože kill vykonal kernel.

## 20. OOM group semantics

`memory.oom.group` môže požiadať kernel, aby pri cgroup OOM zaobchádzal s workloadom ako s jednotkou. Namiesto náhodného ukončenia jedného worker procesu môže byť vhodnejšie zastaviť celú službu a nechať supervisor vykonať čistý restart.

Tento model je užitočný, keď čiastočne živá aplikácia po strate jedného kritického procesu nie je bezpečná. Naopak, workload navrhnutý na nezávislé workers môže preferovať granular recovery.

Systemd pridáva vlastnú `OOMPolicy=` pre unit lifecycle. Kernel OOM decision a manager response treba interpretovať ako dve vrstvy jedného failure path.

## 21. PIDs controller

`pids.max` obmedzuje počet taskov, teda procesov a threadov, v cgroup subtree.

```text
pids.current
pids.max
pids.events
```

Limit chráni pred fork bombou, neobmedzeným thread poolom a vyčerpaním host PID alebo scheduler capacity.

Pri prekročení môže `fork()`, `clone()` alebo thread creation zlyhať s `EAGAIN`:

```text
Resource temporarily unavailable
```

Host môže mať dostatok RAM a globálneho PID priestoru. Autoritatívny dôkaz je cgroup-local `pids.current`, `pids.max` a `pids.events`.

Systemd:

```ini
[Service]
TasksMax=512
```

Limit musí počítať s threadmi, nie iba s procesmi zobrazenými v jednoduchom `ps` pohľade.

## 22. I/O accounting

I/O controller pracuje nad block-device topology a sleduje reads, writes, bytes a operation counts.

```bash
cat /sys/fs/cgroup/<path>/io.stat
```

Záznam je viazaný na device major:minor identitu. Pri LVM, device mapper, RAID, loop devices alebo cloud storage môže byť viditeľná vrstva odlišná od fyzického bottlenecku.

I/O accounting jednej cgroup preto treba korelovať s hostovým device pohľadom:

```bash
lsblk -o NAME,MAJ:MIN,TYPE,PKNAME,MOUNTPOINTS
findmnt -T /path
```

Bez topology mapy môže limit alebo metrika ukazovať správne číslo pre nesprávnu vrstvu.

## 23. I/O weight a hard limits

`io.weight` určuje relatívnu prioritu pri contention na podporovanom scheduler/device path. Podobne ako CPU weight nie je pevná rezervácia a prejaví sa pri súťažení.

`io.max` môže nastaviť hard limit podľa zariadenia:

```text
8:0 rbps=10485760 wbps=5242880 riops=max wiops=max
```

Hard limit chráni storage latency susedných workloadov, ale môže spomaliť flush, checkpoint alebo log write natoľko, že aplikácia narazí na timeouty vyššej vrstvy.

Pri network filesysteme alebo remote block storage nemusí lokálny cgroup I/O controller zachytiť celý bottleneck. Časť latency môže vzniknúť v network stacku, remote service alebo cloud throttling policy.

## 24. Pressure Stall Information

Cgroup v2 poskytuje PSI pre CPU, memory a I/O:

```text
cpu.pressure
memory.pressure
io.pressure
```

PSI meria čas, počas ktorého tasks nemohli robiť užitočnú prácu pre nedostatok zdroja. Dopĺňa utilization o informáciu o reálnom stall dopade.

```text
utilization → koľko sa zdroj používa
queue       → koľko práce čaká
pressure    → ako dlho workload stojí pre nedostatok
```

Workload môže mať nízky priemerný CPU usage, ale vysoké `cpu.pressure`, ak je často throttled krátkou quota. Podobne memory pressure môže rásť skôr, než sa objaví OOM kill.

PSI je vhodné alertovať podľa trendu a workload SLO, nie univerzálnym percentom bez kontextu.

## 25. Delegácia

Delegácia znamená, že parent manager odovzdá správu cgroup subtree inému managerovi, napríklad container runtime, user manageru alebo nested orchestratoru.

Bezpečná delegácia musí určiť:

- vlastníctvo a write oprávnenia cgroup filesystem nodes,
- ktoré controllery môže delegate aktivovať,
- hranicu, za ktorú nesmie presúvať processes,
- parent resource budget,
- kompatibilitu s no-internal-process rule,
- kto vykoná cleanup subtree po zlyhaní managera.

Systemd:

```ini
[Service]
Delegate=yes
```

`Delegate=yes` nie je hardening voľba pre bežnú aplikáciu. Zámerne poskytuje workload manageru väčšiu kontrolu nad descendant cgroups a má sa používať iba tam, kde je to súčasťou architecture.

## 26. Systemd slices a units

Systemd mapuje units do cgroup hierarchy. Services, scopes a user sessions sú zoskupené pod slices, ktoré môžu niesť parent policy.

```text
-.slice
  ├── system.slice
  │    ├── example.service
  │    └── ssh.service
  └── user.slice
```

Slice umožňuje nastaviť spoločný budget pre skupinu units:

```ini
[Slice]
CPUWeight=200
MemoryHigh=8G
MemoryMax=10G
```

Service potom môže mať vlastné child limity. Efektívny výsledok je intersection service policy a všetkých ancestor limits.

Pre systemd workload je preferované používať unit properties namiesto priameho zápisu do `/sys/fs/cgroup`. Service manager tak zachová desired state, ownership a lifecycle.

## 27. Systemd resource properties

Príklad service policy:

```ini
[Service]
CPUWeight=200
CPUQuota=150%
MemoryLow=512M
MemoryHigh=1G
MemoryMax=1500M
MemorySwapMax=256M
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
  -p CPUQuotaPerSecUSec \
  -p MemoryCurrent \
  -p MemoryPeak \
  -p MemoryHigh \
  -p MemoryMax \
  -p TasksCurrent \
  -p TasksMax
```

`systemctl show` poskytuje manager view. Pri hlbokej diagnostike treba prečítať aj raw cgroup files a kernel events.

## 28. Containers

Container runtime vytvorí cgroup boundary pre container alebo Pod a umiestni do nej namespace PID 1 aj descendants. Runtime config mapuje na kernel controls, ale názvy a hierarchy závisia od systemd drivera, runtime a orchestration platformy.

Kontajner bez memory limitu stále beží v cgroup, ale môže dediť iba parent policy. „Unlimited“ na úrovni kontajnera neznamená nekonečnú hostovú kapacitu; ancestor slice alebo Pod cgroup môže mať limit.

Pri diagnostike treba zistiť:

- container PID na hoste,
- jeho `/proc/<pid>/cgroup` path,
- parent Pod alebo service cgroup,
- runtime a systemd properties,
- raw controller events.

## 29. Kubernetes requests a limits

Kubernetes resource fields sa mapujú na viacero scheduler a runtime mechanizmov. Nie všetky requests a limits sú priamo rovnaký typ cgroup knobu.

### CPU request

CPU request ovplyvňuje scheduling a typicky relatívnu CPU váhu. Neznamená dedicated CPU ani hard minimum throughput, pokiaľ sa nepoužije špecifický CPU Manager a exclusive cpuset model.

### CPU limit

CPU limit sa typicky mapuje na CFS quota. Workload môže byť throttled aj pri voľnom host CPU, ak vyčerpá period budget.

### Memory request

Memory request je primárne scheduler capacity signal. Runtime a QoS policy môžu používať memory protection mechanizmy, ale presný mapping závisí od platformy a verzie.

### Memory limit

Memory limit sa mapuje na hard cgroup boundary. Prekročenie môže viesť ku container-local OOM kill, hoci node má voľnú memory.

Preto treba odlišovať:

```text
scheduler placement
relative priority/protection
hard runtime limit
observed workload usage
```

## 30. Kubernetes QoS a hierarchy

Kubernetes vytvára cgroup hierarchy podľa Podov, kontajnerov a QoS classes. Exact layout závisí od cgroup drivera a runtime.

QoS class ovplyvňuje eviction a resource policy, ale nie je náhradou za presné requests/limits a workload profiling. Dva Pods v rovnakej class môžu mať veľmi odlišný pressure profil.

Pri OOM incidente treba rozlíšiť:

- process-level OOM v container cgroup,
- Pod alebo parent cgroup limit,
- node-wide OOM,
- kubelet eviction pre memory pressure,
- application-controlled termination.

Tieto udalosti majú odlišné evidence a recovery semantics.

## 31. Cgroup freeze a kill

Cgroup v2 poskytuje lifecycle operations pre celú skupinu. `cgroup.freeze` môže pozastaviť descendant tasks a `cgroup.kill` môže ukončiť celý subtree.

Tieto operácie sú silnejšie než iterovanie cez snapshot PID listu, pretože nový child process nemôže ľahko uniknúť medzi enumerate a signal krokom.

Freeze nie je checkpoint. Procesný memory a kernel state zostáva v RAM a external dependencies môžu timeoutovať, zatiaľ čo workload stojí.

Service manager alebo runtime má tieto mechanizmy používať koordinovane. Ručný zásah môže narušiť supervisor state a readiness.

## 32. Cgroup lifecycle

Cgroup adresár možno odstrániť až keď neobsahuje processes ani child cgroups. Zostávajúci orphan subtree po páde managera môže indikovať neúplný cleanup alebo stále živé workloady.

Cgroup object nie je persistent configuration. Po reboote hierarchy znovu vytvorí service manager alebo runtime podľa svojej desired state.

Preto raw zmena v `/sys/fs/cgroup` nemusí prežiť restart unit, daemon reload ani reboot. Trvalá policy patrí do systemd unit, orchestration manifestu alebo runtime konfigurácie.

## 33. Troubleshooting: služba má vysokú latency pri nízkom host CPU

Host ukazuje voľné cores, ale jedna service má pravidelné latency spikes.

1. **Nájdi cgroup path** — `systemctl show -p ControlGroup` alebo `/proc/<pid>/cgroup`.
2. **Skontroluj `cpu.max`** — potvrď quota a period.
3. **Prečítaj `cpu.stat`** — sleduj `nr_throttled` a `throttled_usec` trend.
4. **Skontroluj `cpu.pressure`** — zisti reálny stall dopad.
5. **Porovnaj parent limits** — service môže byť obmedzená ancestor slice policy.
6. **Skontroluj cpuset** — workload môže byť pinovaný na preťažený core.
7. **Koreluj s request rate** — burst môže vyčerpať quota aj pri nízkom dlhodobom priemere.

Zvýšenie quota bez pochopenia burst modelu môže iba presunúť contention na inú službu.

## 34. Troubleshooting: OOM v kontajneri, host má voľnú RAM

1. **Potvrď cgroup path kontajnera** — host PID a `/proc/<pid>/cgroup` sú autoritatívnejšie než názov kontajnera.
2. **Prečítaj `memory.current`, `memory.high` a `memory.max`** — rozlíš pressure boundary od hard limitu.
3. **Prečítaj `memory.events`** — `high`, `max`, `oom` a `oom_kill` odhalia failure path.
4. **Rozlož `memory.stat`** — anonymous memory, file cache a kernel charges majú odlišné root causes.
5. **Skontroluj parent hierarchy** — Pod alebo node slice môže mať nižší agregovaný limit.
6. **Skontroluj kernel journal a runtime events** — potvrď, ktorý task bol zabitý.
7. **Porovnaj workload burst s limitom** — startup, reload alebo compaction môže krátko potrebovať viac než steady state.
8. **Over swap policy** — cgroup mohla mať `memory.swap.max=0`, hoci host má swap.

## 35. Troubleshooting: `fork()` zlyháva pri voľnej memory

1. **Skontroluj `pids.current` a `pids.max`** — limit zahŕňa thready.
2. **Prečítaj `pids.events`** — counter potvrdí zasiahnutie boundary.
3. **Skontroluj systemd `TasksMax`** — unit alebo parent slice môže mať vlastný limit.
4. **Spočítaj thready aplikácie** — thread leak môže vyzerať ako process limit problém.
5. **Až potom kontroluj host PID space a `ulimit -u`** — ide o ďalšie nezávislé vrstvy.

`EAGAIN` z process creation neznamená automaticky nedostatok RAM.

## 36. Časté omyly

### „Cgroup izoluje procesy ako namespace“

Nie. Cgroup riadi resource accounting a policy, ale process visibility a menné priestory riešia namespaces.

### „CPU request garantuje konkrétny výkon“

Nie automaticky. Request je scheduling a priority signal; výkon závisí od node contention, weight, cpuset, quota a workload charakteru.

### „CPU quota sa použije iba pri contention“

Nie. Hard quota môže throttliť workload aj na inak idle hoste.

### „RSS procesu sa musí rovnať `memory.current`“

Nie. Cgroup účtuje celý subtree a viac memory kategórií než RSS jedného procesu.

### „Host free memory vylučuje OOM“

Nie. Cgroup-local `memory.max` alebo ancestor limit môže vyvolať OOM pri voľnej hostovej RAM.

### „`memory.high` a `memory.max` sú rovnaký limit“

`memory.high` vytvára reclaim a throttling pressure. `memory.max` je hard boundary, po ktorej môže nastať OOM.

### „Priamy zápis do cgroup filesystemu je trvalá konfigurácia“

Nie. Systemd alebo runtime môže hodnotu prepísať a po reboote hierarchy vzniká nanovo z desired state.

### „I/O limit na logical volume presne riadi fyzický disk“

Nie vždy. Device mapper, RAID, remote storage a scheduler topology môžu meniť miesto, kde sa limit aplikuje a kde vzniká bottleneck.

## 37. Kontrolné otázky

1. Aký je rozdiel medzi namespace a cgroup?
2. Prečo je cgroup hierarchy vhodnejšia než limit iba na main PID?
3. Čo znamená unified hierarchy v cgroup v2?
4. Prečo parent musí aktivovať controller v `cgroup.subtree_control`?
5. Aký je rozdiel medzi CPU weight a CPU quota?
6. Prečo môže quota throttliť workload na idle hoste?
7. Čo je rozdiel medzi cpuset placementom a CPU bandwidth limitom?
8. Prečo sa `memory.current` nemusí rovnať súčtu RSS?
9. Aký je rozdiel medzi `memory.low`, `memory.high` a `memory.max`?
10. Ako vznikne cgroup-local OOM pri voľnej hostovej RAM?
11. Prečo `TasksMax` zahŕňa aj thready?
12. Ako PSI dopĺňa utilization a accounting?
13. Čo znamená bezpečná cgroup delegation?
14. Ako sa Kubernetes CPU limit typicky prejaví v cgroup v2?
15. Prečo treba pri diagnostike kontrolovať aj ancestor cgroups?

## 38. Zhrnutie

Cgroups poskytujú hierarchický accounting a resource policy pre skupiny procesov. Cgroup v2 zjednocuje CPU, memory, I/O, PIDs a ďalšie controllery v jednom strome, kde parent policy obmedzuje a deleguje authority descendants.

Spoľahlivá prevádzka vyžaduje rozlišovať relatívne weights, hard quotas, memory protection, pressure boundaries a hard limits. Diagnostika musí sledovať raw controller events, PSI, systemd alebo runtime desired state a všetky ancestor limits; samotný hostový utilization snapshot nevysvetľuje cgroup-local throttling ani OOM.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Namespaces](namespaces.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Linux capabilities →](linux-capabilities.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
