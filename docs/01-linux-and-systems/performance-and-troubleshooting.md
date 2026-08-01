# Linux performance a troubleshooting

Performance troubleshooting je evidence-driven proces premeny používateľského symptómu na testovateľnú príčinu. Začína presným outcome-om, časovým oknom a affected cohortou, nie príkazom `top`. Každý nástroj pozoruje iba jednu vrstvu a jeho hodnota musí byť interpretovaná voči workloadu, limits a dependencies.

```text
user-visible symptom
→ exact scope, timeline a baseline
→ request/process/resource/data path
→ competing hypotheses
→ discriminating observation
→ evidence-preserving containment
→ authoritative repair
→ original, forbidden a adjacent-scenario validation
```

Vysoké CPU môže byť expected productive work, runaway loop, spinlock alebo consequence retry stormu. Nízke CPU môže sprevádzať lock contention, storage latency, network timeout alebo cgroup throttling. Memory growth môže byť cache, leak alebo backlog. Preto sa najprv oddeľuje utilization od saturation, host od cgroup scope-u a correlation od causality.

Náprava nie je uzavretá poklesom jednej metriky. Musí zlepšiť latency, throughput alebo completion outcome, zachovať correctness a overiť druhú load alebo failure situáciu. Inak sa bottleneck iba presunie alebo sa symptóm potlačí bez odstránenia mechanizmu.

## 1. Definícia

Linux performance troubleshooting je systematický proces, ktorý prepája používateľský symptóm s konkrétnym mechanizmom v aplikácii, kerneli, resource hierarchy alebo externej dependency. Cieľom nie je nájsť najvyššie číslo v `top`, ale vytvoriť dôkazmi podložený kauzálny reťazec.

```text
workload alebo zmena
  ↓
queue, contention, error alebo resource pressure
  ↓
kernel/application behavior
  ↓
latency, throughput, availability alebo correctness dopad
```

Performance problém môže existovať aj pri nízkom priemernom utilization. Krátke quota throttling, lock convoy alebo storage tail-latency bursts môžu poškodiť p99 response time bez dramatického hostového priemeru.

## 2. Performance verzus funkčná chyba

Nie každý pomalý request je resource bottleneck. Rovnaký symptóm môže vytvoriť chybný retry loop, DNS timeout, nesprávna route, lock, security denial, chýbajúci file descriptor alebo downstream rate limit.

Pred tuningom treba rozlíšiť:

- **Funkčnú chybu** — operácia zlyháva, vracia nesprávny výsledok alebo čaká na podmienku, ktorá nenastane.
- **Capacity problém** — legitímna práca presahuje dostupnú CPU, memory, I/O alebo network kapacitu.
- **Contention problém** — zdroj existuje, ale workloady alebo thready sa navzájom blokujú.
- **Policy problém** — cgroup quota, rate limit, timeout alebo security policy vytvára zamýšľanú hranicu.
- **Dependency problém** — lokálny proces čaká na remote službu alebo shared storage.

Tuning nesprávnej kategórie môže zhoršiť incident. Zvýšenie thread countu pri downstream saturation napríklad zväčší queue a tail latency.

## 3. Začni používateľským dopadom

Pred prvým diagnostickým príkazom definuj pozorovaný problém. Neurčité tvrdenie „server je pomalý“ neposkytuje testovateľnú hypotézu.

Potrebné otázky:

- **Ktorá operácia je pomalá alebo zlyháva?** — login, API endpoint, build, disk write alebo SSH session majú odlišný path.
- **Aký je očakávaný baseline?** — porovnaj s predchádzajúcim obdobím, SLO alebo známym zdravým hostom.
- **Kedy problém začal?** — presný čas umožní koreláciu s deployom, config zmenou a resource trendom.
- **Aký je scope?** — jeden user, request class, Pod, host, availability zone alebo celý fleet.
- **Je problém trvalý alebo burstový?** — snapshot nástroje môžu minúť krátky incident.
- **Ktorý používateľský signál degradoval?** — latency percentile, error rate, throughput, queue age alebo business completion.

Root cause musí vysvetliť práve tento dopad. Vysoká metrika bez časovej a scope korelácie je iba podozrenie.

## 4. Incident timeline

Performance analýza potrebuje časovú os. Zbieraj udalosti v spoločnej timezone a rozlišuj wall-clock timestamp od monotonic duration.

```text
10:00 deploy v2
10:04 request rate rovnaký
10:05 p99 latency rastie
10:06 CPU quota throttling začína
10:08 retry volume rastie
10:12 downstream timeouts
```

Timeline pomáha rozlíšiť primárnu príčinu od následkov. Retry storm môže byť viditeľnejší než pôvodný quota alebo dependency problém, ale vznikol neskôr.

Dôležité je zachytiť aj neprítomnosť zmeny. Ak workload a deploy zostali rovnaké, ale storage latency vzrástla, hypotéza sa presúva na infraštruktúru alebo susedný workload.

## 5. Baseline a porovnávací kontext

Jedna hodnota nemá význam bez kontextu. CPU `80 %`, disk latency `10 ms` alebo 500 otvorených file descriptors môže byť normálny alebo kritický stav podľa workloadu.

Použiteľný baseline môže byť:

- ten istý host pred incidentom,
- zdravý sibling host s rovnakou verziou,
- rovnaký request class pri nižšom loade,
- load-test profil,
- kapacitný alebo SLO limit.

Porovnanie musí kontrolovať confounders: verzia aplikácie, input size, cache warmth, traffic mix, node type, cgroup limits a downstream stav.

## 6. USE model

USE method skúma každý resource podľa troch dimenzií:

- **Utilization** — koľko kapacity je aktívne používané.
- **Saturation** — koľko práce čaká, pretože resource alebo policy nestačí.
- **Errors** — explicitné zlyhania, timeouts, resets alebo integrity problémy.

Príklad CPU:

```text
utilization → user/system CPU time
saturation  → runnable queue, cgroup throttling, CPU PSI
errors      → hardware faults, thermal events, scheduler anomalies
```

Príklad storage:

```text
utilization → throughput a device busy time
saturation  → queue, await, I/O PSI
errors      → timeouts, resets, filesystem/device errors
```

Vysoká utilization bez queue a používateľského dopadu môže byť zdravé využitie. Saturation a errors sú často lepšie signály než samotné percento.

## 7. RED a workload signály

Pre request-oriented službu je vhodné doplniť RED model:

- **Rate** — počet requests alebo jobs za čas.
- **Errors** — podiel alebo počet zlyhaní podľa failure class.
- **Duration** — distribúcia latency, nie iba priemer.

RED opisuje používateľský alebo aplikačný outcome, USE fyzické a kernelové resources. Spojenie oboch modelov umožní zistiť, či resource pressure vysvetľuje request degradáciu.

```text
p99 latency rastie
  + CPU throttle rastie v rovnakom čase a cgroup scope
  + stack samples ukazujú runnable work
  → quota hypothesis je silná
```

## 8. Golden troubleshooting workflow

```text
1. Potvrď symptóm
2. Urči scope a čas
3. Zachovaj evidence
4. Skontroluj nedávne zmeny
5. Získaj top-level pressure snapshot
6. Zúž host → cgroup → process → thread → request
7. Vytvor testovateľnú hypotézu
8. Získaj dôkaz, ktorý ju môže potvrdiť aj vyvrátiť
9. Aplikuj najmenšiu bezpečnú mitigation
10. Over používateľský outcome a vedľajšie účinky
11. Odstráň root cause a monitoring gap
```

Každý príkaz musí odpovedať na otázku. Zbieranie veľkého množstva metrík bez hypotézy vytvára náhodné korelácie a spomaľuje incident response.

## 9. Zachovanie evidence

Restart, scale-out alebo node replacement môže rýchlo obnoviť službu, ale zároveň zničiť process stacks, `/proc` state, open descriptors a lokálny journal kontext.

Pred deštruktívnou mitigation, ak to dopad dovolí, zachovaj:

- čas a host/container identity,
- process tree a cgroup path,
- CPU/memory/I/O/network snapshot,
- relevantný journal interval,
- stack alebo profiler sample,
- open files a sockets,
- config a artifact version.

Evidence collection nesmie predĺžiť kritický outage bez limitu. Incident commander musí vyvážiť recovery a diagnostickú hodnotu.

## 10. Observation point

Každý nástroj pozoruje konkrétnu vrstvu a namespace. Hostový `ss` neukáže všetky kontajnerové sockets, `df` opisuje filesystem allocation a `du` iba viditeľné path entries.

Pred interpretáciou sa pýtaj:

```text
Ktorý object alebo namespace tento príkaz pozoruje?
Je to host, Pod, container, service cgroup alebo process?
Je metrika agregovaná cez descendants?
Je údaj instantaneous, cumulative alebo rate?
```

Nesprávny observation point môže produkovať úplne správne číslo pre nesprávny scope.

## 11. Rýchly host-level snapshot

Prvý snapshot má rozhodnúť, ktorou vetvou pokračovať. Nemá byť finálnym root-cause dôkazom.

```bash
uptime
free -h
vmstat 1
mpstat -P ALL 1
pidstat 1
ss -s
ip -s link
journalctl -p warning..alert -b
```

Storage:

```bash
iostat -xz 1
findmnt
df -h
df -i
```

Snapshot čítaj ako kombináciu:

- CPU idle verzus runnable queue,
- memory available verzus reclaim/swap,
- I/O await a queue verzus device errors,
- network drops/retransmissions verzus socket states,
- kernel warnings verzus application time window.

## 12. CPU: utilization a states

CPU čas sa delí na user, system, idle, iowait, steal a interrupt categories. Vysoký user CPU naznačuje aplikačný compute, zatiaľ čo vysoký system CPU môže znamenať syscalls, networking, memory management alebo kernel overhead.

```bash
mpstat -P ALL 1
pidstat -u -t 1
top -H -p <pid>
```

CPU state nie je root cause. Vysoké system CPU treba ďalej rozložiť profilovaním alebo subsystem metrics.

Steal time vo virtualizácii znamená, že vCPU čakal na hypervisor scheduling. Lokálna aplikácia ho nevyrieši optimalizáciou kódu.

## 13. CPU saturation a run queue

Runnable task čaká na CPU, hoci je pripravený vykonávať inštrukcie. Run queue rastie, keď runnable demand presiahne dostupné scheduling slots alebo policy budget.

```bash
vmstat 1
cat /proc/loadavg
cat /proc/pressure/cpu
```

`vmstat` pole `r` treba porovnať s počtom logical CPUs a cpusetom workloadu. Host môže mať 64 cores, ale service cgroup môže mať povolené iba dva.

CPU PSI meria stall time, nie iba queue length. Je vhodný na koreláciu s latency, najmä pri krátkych burstoch.

## 14. Load average

Load average zahŕňa runnable tasks a niektoré tasks v uninterruptible sleep. Nie je to percento CPU.

```bash
uptime
ps -eo state,pid,tid,wchan:32,comm | awk '$1 ~ /^D/'
```

Vysoký load môže vzniknúť:

- CPU runnable queue,
- storage alebo NFS waits v stave `D`,
- kernel lock alebo device wait,
- kombináciou viacerých zdrojov.

Rozlíšenie vyžaduje CPU idle, `vmstat r/b`, process states, `wchan` a I/O evidence.

## 15. Jeden core na 100 percent

Hostový priemer môže byť nízky, ale kritický single-thread alebo serialized section saturuje jeden core.

Možné mechanizmy:

- single-threaded event loop,
- global lock alebo mutex convoy,
- CPU affinity/cpuset,
- hot shard alebo partition,
- interrupt concentration,
- runtime GC alebo compiler thread.

```bash
mpstat -P ALL 1
ps -eo pid,tid,psr,stat,comm,%cpu --sort=-%cpu
cat /proc/<pid>/status | grep Cpus_allowed_list
```

Scale-up počtu cores nepomôže, ak aplikácia nevie prácu paralelizovať alebo je pinovaná.

## 16. CPU cgroup throttling

Workload môže mať latency pri voľnom host CPU, ak vyčerpal `cpu.max` quota.

```bash
cat /proc/<pid>/cgroup
cat /sys/fs/cgroup/<path>/cpu.max
cat /sys/fs/cgroup/<path>/cpu.stat
cat /sys/fs/cgroup/<path>/cpu.pressure
```

Dôkazom je rast `nr_throttled` a `throttled_usec` v rovnakom časovom okne ako request latency. Samotná existencia quota nestačí.

Mitigation môže byť dočasné zvýšenie quota, ale root cause môže byť nový CPU-heavy code path, väčší batch alebo retry storm.

## 17. CPU profiling

Sampling profiler ukazuje, kde CPU čas trávi proces alebo kernel.

```bash
sudo perf top
sudo perf record -F 99 -g -p <pid> -- sleep 30
sudo perf report
```

Profil potrebuje symbols a správny scope. Profil hosta môže byť zahltený inými workloadmi; profil iba main threadu môže minúť workers.

Sampling odpovedá na otázku „kde sa vykonáva CPU práca“. Neodpovedá dobre na off-CPU waits, ktoré potrebujú blocking, scheduler alebo tracing analýzu.

## 18. On-CPU verzus off-CPU

On-CPU analýza skúma aktívne vykonávanie. Off-CPU analýza skúma, prečo thread spal alebo čakal.

```text
on-CPU  → compute, syscall execution, spin
off-CPU → I/O, lock, futex, timer, network, scheduler wait
```

Proces s nízkym CPU môže byť hlavným bottleneckom, ak väčšinu času čaká na lock alebo downstream response. `wchan`, stack traces, `strace -T` a eBPF off-CPU profiling pomáhajú odhaliť wait reason.

## 19. Context switches a interrupts

Vysoký počet context switches môže byť prirodzený pri I/O-heavy workload, ale aj dôsledok príliš veľkého thread poolu, lock contention alebo krátkych wakeups.

```bash
vmstat 1
pidstat -w -t 1
mpstat -I ALL 1
```

Hodnota musí byť korelovaná s throughputom a latency. Milión context switches pri vysokom úspešnom throughput môže byť prijateľný; rovnaká hodnota pri nulovom progresse naznačuje thrash.

## 20. Memory inventory

Memory analýza musí rozlišovať anonymous memory, file-backed pages, page cache, slab/kernel memory, swap a cgroup charge.

```bash
free -h
cat /proc/meminfo
cat /proc/<pid>/smaps_rollup
ps aux --sort=-%mem | head
```

Nízke `free` nie je automaticky problém, pretože Linux používa RAM ako page cache. Dôležitejšie sú `MemAvailable`, reclaim rate, swap-in/out, PSI a používateľský dopad.

## 21. Memory leak verzus pracovná množina

Rast RSS môže byť:

- skutočný leak nedostupných objektov,
- zámerná aplikačná cache,
- allocator arena retention,
- väčší workload working set,
- memory-mapped file alebo shared library behavior.

Jednorazový snapshot leak nepotvrdí. Potrebná je časová séria normalizovaná podľa trafficu a lifecycle udalostí.

Silnejší dôkaz leak-u:

```text
RSS alebo heap rastie po každom cykle
  + workload sa vracia na baseline
  + memory sa nereclaimuje
  + heap profile ukazuje retained objects
```

## 22. Memory pressure a reclaim

Kernel pri pressure reclaimuje clean cache, zapisuje dirty pages, swapuje anonymous memory alebo vykonáva compaction.

```bash
vmstat 1
cat /proc/pressure/memory
cat /sys/fs/cgroup/<path>/memory.pressure
cat /sys/fs/cgroup/<path>/memory.events
```

Memory pressure môže zvýšiť latency ešte pred OOM. Reclaim CPU, direct reclaim a writeback blokujú aplikačné thready.

`memory.events high` s rastúcim PSI môže vysvetliť degradáciu aj bez `oom_kill`.

## 23. Swap a thrashing

Swap usage samo osebe nie je incident. Staré anonymous pages môžu zostať v swap-e bez aktívneho výkonového dopadu.

Kritický je aktívny swap churn:

```bash
vmstat 1
sar -W 1
```

Trvalo vysoké `si` a `so`, vysoký memory PSI a nízky aplikačný progres naznačujú thrashing. Zvýšenie swapu môže oddialiť OOM, ale nevyrieši working set presahujúci dostupnú memory.

## 24. OOM analýza

OOM killer je recovery mechanizmus po zlyhaní allocation a reclaim, nie root cause.

```bash
journalctl -k -b | grep -i -E 'oom|out of memory|killed process'
cat /sys/fs/cgroup/<path>/memory.events
```

Treba rozlíšiť:

- host-wide OOM,
- cgroup-local OOM,
- systemd OOM policy,
- Kubernetes/container OOM event,
- kubelet eviction bez kernel OOM.

Root cause môže byť leak, nízky limit, startup burst, neobmedzená concurrency, cache policy alebo parent cgroup limit.

## 25. Storage capacity

`df` a `du` merajú odlišné veci.

```bash
df -h
df -i
du -xhd1 /var | sort -h
sudo lsof +L1
```

Kontroluj:

- data blocks,
- inodes,
- user/project quota,
- reserved blocks,
- deleted-open files,
- prekrytý mount content,
- underlying LV alebo cloud volume capacity.

`ENOSPC` neznamená iba nulové voľné gigabajty.

## 26. Storage latency a queueing

```bash
iostat -xz 1
pidstat -d 1
cat /proc/pressure/io
```

Interpretuj:

- request latency,
- queue depth,
- throughput,
- read/write mix,
- device utilization,
- retries a errors.

Moderný NVMe alebo distributed storage môže obsluhovať viac paralelných requests, takže `%util=100` nemá univerzálny význam. Poznaj device model a service time distribution.

## 27. Storage stack a observation layer

Aplikačný path môže prechádzať cez filesystem, device mapper, encryption, LVM, RAID, virtual disk a remote backend.

```text
application path
  ↓ filesystem
page cache/writeback
  ↓ logical volume
DM/RAID/encryption
  ↓ virtual/block device
cloud or physical storage
```

Bottleneck a metrika nemusia byť na rovnakej vrstve. `iostat` na logical device môže agregovať alebo skryť backend behavior.

```bash
findmnt -T /path
lsblk -o NAME,MAJ:MIN,TYPE,PKNAME,MOUNTPOINTS
```

## 28. Filesystem a device errors

Kernel journal je autoritatívny zdroj pre resets, timeouts, filesystem remount read-only a I/O errors.

```bash
journalctl -k -b | grep -i -E \
  'I/O error|reset|timeout|filesystem|ext4|xfs|btrfs|nvme|scsi'
```

Aplikácia s najvyšším I/O nemusí byť root cause, ak storage device opakovane resetuje. Repair alebo reboot bez zachovania evidence môže skryť hardware alebo platform fault.

## 29. Network troubleshooting path

Network problém diagnostikuj po vrstvách:

```text
name resolution
  ↓
address family a route
  ↓
neighbor/link
  ↓
local firewall/conntrack
  ↓
packet departure a return path
  ↓
TCP/UDP state
  ↓
TLS
  ↓
application protocol
```

```bash
getent hosts example.com
ip route get <ip>
ip neigh
ss -lntup
ss -tan
ip -s link
nstat
tcpdump -ni any host <ip>
```

Ping testuje ICMP echo, nie port, TLS ani aplikáciu.

## 30. Packet loss a retransmissions

TCP retransmission môže vzniknúť packet lossom, reorderingom, congestion alebo timeoutom vyššej vrstvy. Interface drop counters ukazujú iba lokálny observation point.

```bash
ip -s link
nstat | grep -E 'Retrans|Listen|Drop'
ss -ti dst <ip>
```

Dôkaz potrebuje časovú koreláciu s request latency a packet capture na správnom namespace/interface. Capture iba na klientovi nemusí vysvetliť remote alebo return-path loss.

## 31. Socket queues a backlog

Listening socket môže existovať, ale backlog alebo application accept loop môže byť saturovaný.

```bash
ss -lnt
ss -s
nstat | grep -E 'ListenOverflows|ListenDrops'
```

Rast accept queue spolu s `ListenOverflows` naznačuje, že application alebo CPU policy nestíha prijímať nové connections. Zvýšenie backlogu iba zväčší buffer, ak aplikácia nemá dostatočný service rate.

## 32. DNS latency

DNS problém môže vyzerať ako pomalá sieť alebo aplikácia.

```bash
time getent hosts example.com
resolvectl query example.com
dig example.com
```

`getent` testuje NSS path podobný bežnej aplikácii. `dig` môže obísť `/etc/hosts`, NSS modules alebo aplikáčný cache.

Kontroluj resolver timeout/retry policy, search domains, IPv6/IPv4 behavior a network namespace reachability k resolveru.

## 33. TLS a application layer

Úspešný TCP handshake nepotvrdzuje funkčný TLS ani aplikáciu.

```bash
openssl s_client -connect host:443 -servername host
curl -v --connect-timeout 5 --max-time 20 https://host/
```

Rozlišuj:

- connect latency,
- TLS handshake latency,
- certificate validation,
- request queueing,
- server processing,
- response transfer.

Application tracing alebo server timing je potrebný, ak network path funguje, ale request stále čaká.

## 34. Process states

```bash
ps -eo pid,ppid,tid,stat,wchan:32,comm
pstree -ap <pid>
```

Stav `R` znamená running alebo runnable; `S` interruptible sleep; `D` uninterruptible kernel wait; `Z` zombie.

Stav bez wait reason nestačí. `wchan`, kernel stack a syscall tracing pomáhajú vysvetliť, na čom thread čaká.

## 35. `strace`

```bash
sudo strace -ff -tt -T -p <pid>
```

`strace` ukazuje syscalls, arguments, výsledky, signals a trvanie. Je vhodný na:

- opakované failed file opens,
- connect timeouts,
- blocking reads/writes/futex waits,
- permission denials,
- child-process lifecycle.

Riziká:

- runtime overhead a timing perturbation,
- veľký output,
- secrets v arguments alebo buffers,
- ptrace/LSM obmedzenia,
- nesprávny target thread alebo namespace.

Používaj časovo obmedzený a syscall-filtered trace, ak je produkčný workload citlivý.

## 36. Stack traces a `wchan`

```bash
cat /proc/<pid>/stack
cat /proc/<pid>/wchan
```

Kernel stack je užitočný pri `D` state alebo syscall wait. User-space stack potrebuje debugger, runtime-specific tooling alebo profiler.

Jeden stack je snapshot. Pri intermittent probléme zbieraj viac samples a hľadaj opakujúci sa wait point.

## 37. File descriptors

Symptómy descriptor exhaustion:

```text
Too many open files
accept/open failures
neúspešné logovanie
```

```bash
cat /proc/<pid>/limits
ls /proc/<pid>/fd | wc -l
sudo lsof -p <pid>
sysctl fs.file-nr
```

Rozlišuj:

- process soft/hard rlimit,
- systemd `LimitNOFILE`,
- host-wide file table,
- aplikáčný descriptor leak,
- legitímny rast connections.

Zvýšenie limitu bez opravy leak-u iba posunie incident a zväčší možný blast radius.

## 38. PID a thread limits

Process creation môže zlyhať pre `RLIMIT_NPROC`, cgroup `pids.max`, host PID exhaustion alebo memory allocation failure.

```bash
cat /proc/<pid>/limits
cat /sys/fs/cgroup/<path>/pids.current
cat /sys/fs/cgroup/<path>/pids.max
cat /sys/fs/cgroup/<path>/pids.events
```

Thread leak sa počíta do cgroup task limitu. Jednoduchý počet procesov môže preto výrazne podhodnotiť skutočný počet taskov.

## 39. Locks a futex contention

Aplikácia môže mať voľný CPU a memory, ale thready čakajú na mutex alebo futex.

Signály:

- vysoký off-CPU čas,
- veľa threadov v rovnakom futex wait,
- nízky throughput napriek dostupným resources,
- jeden lock-holder thread na CPU alebo blocked v I/O.

```bash
strace -f -e trace=futex -p <pid>
perf lock record -- <command>
perf lock report
```

Runtime-specific profiler býva presnejší než raw futex count. Cieľom je nájsť serialized critical section a jej owner.

## 40. Cgroup a container scope

Host-wide metrics môžu vyzerať zdravo, kým workload naráža na local quota alebo limit.

```bash
cat /proc/<pid>/cgroup
systemctl show <unit> -p ControlGroup -p MemoryCurrent -p MemoryMax
cat /sys/fs/cgroup/<path>/cpu.stat
cat /sys/fs/cgroup/<path>/memory.events
cat /sys/fs/cgroup/<path>/pids.events
```

Kontroluj aj ancestors. Pod alebo slice parent môže byť limitovaný, hoci child fields vyzerajú neobmedzene.

Container runtime event `OOMKilled` alebo throttling metric musí byť korelovaný s raw kernel/cgroup evidence.

## 41. Namespaces

Diagnostický príkaz musí bežať v namespace, ktorý vlastní skúmaný stav.

```bash
lsns -p <pid>
sudo nsenter -t <pid> -n ss -lntup
sudo nsenter -t <pid> -n ip route
sudo nsenter -t <pid> -m findmnt
```

Hostový socket alebo mount inventory nemusí opisovať kontajner. Nesprávny namespace je častá príčina protichodných pozorovaní.

## 42. Security denials ako performance symptóm

SELinux/AppArmor denial, chýbajúca capability alebo seccomp blok môže spôsobiť retry loop, timeout alebo fallback na pomalší path.

```bash
journalctl -k -b | grep -i -E 'avc|apparmor|seccomp|denied'
grep '^Cap' /proc/<pid>/status
```

Permission problém nemusí byť iba funkčný fail-fast. Aplikácia môže opakovane skúšať operáciu a vytvárať CPU/log storm.

## 43. Little's Law a queueing

Little's Law:

```text
L = λ × W
```

- `L` — priemerný počet položiek v systéme,
- `λ` — arrival alebo throughput rate,
- `W` — priemerný čas v systéme.

Ak arrival rate zostáva rovnaký a latency rastie, rastie aj concurrency alebo queue length. Vyššia concurrency potom zvyšuje memory, sockets a lock contention.

Tento vzťah vysvetľuje, prečo pomalý downstream môže sekundárne vyčerpať lokálne connections a memory.

## 44. Tail latency

Priemer môže zostať stabilný, hoci malé percento requests prekračuje timeout. Používateľský dopad často riadi p95, p99 alebo maximum queue age.

Tail latency vytvárajú:

- queueing bursts,
- GC alebo compaction,
- cgroup quota periods,
- storage outliers,
- retransmissions,
- lock convoys,
- cold cache alebo DNS/TLS retries.

Analýza musí používať distribúciu a request class. Agregácia rýchlych a pomalých endpointov môže skryť problém.

## 45. Coordinated omission

Load generator, ktorý po pomalom requeste prestane posielať ďalšie requests, môže podhodnotiť skutočnú latency počas saturation. Nezaznamená čakanie požiadaviek, ktoré by v reálnej prevádzke prichádzali.

Performance test musí modelovať arrival pattern a queueing. Inak môže systém vyzerať stabilne práve preto, že test znížil load pri degradácii.

## 46. Hypotéza a falzifikácia

Dobrá hypotéza je konkrétna a vyvrátiteľná:

```text
P99 latency rastie, pretože payments.service vyčerpáva CPU quota.
```

Predikcie:

- throttle counters rastú v rovnakom intervale,
- latency postihuje iba túto cgroup,
- stack samples ukazujú runnable CPU work,
- dočasné zvýšenie quota zníži latency bez zmeny trafficu.

Ak sa predikcie nepotvrdia, hypotézu treba odmietnuť. Nie ju zachraňovať výberom ďalšej nesúvisiacej metriky.

## 47. Bezpečný experiment

Experiment mení jednu relevantnú premennú a má definovaný rollback.

Príklady:

- zvýš CPU quota iba jednej canary instance,
- zníž concurrency pre jednu worker group,
- presmeruj malú časť trafficu na predchádzajúci artifact,
- vypni konkrétny feature flag,
- zmeň resolver iba v testovacom namespace.

Experiment musí merať používateľský outcome aj možné vedľajšie účinky. Zvýšenie quota môže zlepšiť jednu službu a zhoršiť sibling workloads.

## 48. Mitigation verzus root-cause fix

Mitigation obnovuje službu; root-cause fix odstraňuje mechanizmus incidentu.

```text
restart procesu      → mitigation
oprava descriptor leak-u → root-cause fix
```

```text
zvýšenie memory limitu → mitigation alebo capacity change
bounded queue/backpressure → systémová oprava
```

Mitigation nie je zlyhanie. Pri incidente je správna, ak je bezpečná a obnoví SLO, ale musí byť explicitne zaznamenaná ako dočasná alebo trvalá.

## 49. Overenie nápravy

Náprava je úspešná až keď sa obnoví používateľský výsledok a nezhorší sa iná kritická vlastnosť.

Over:

- latency/error/throughput SLI,
- resource pressure a queue,
- absence nových errors,
- stabilitu počas dostatočného obdobia,
- správanie pri očakávanom peak load,
- sibling workloads,
- persistenciu konfigurácie po restart/redeploy.

Pokles CPU po reštarte nie je dôkaz opravy, ak sa leak alebo queue znovu vytvorí o hodinu.

## 50. Antipatterny

### Náhodné spúšťanie príkazov

Veľa outputu bez otázky nevytvára kauzálny model. Každý nástroj má testovať hypotézu alebo zúžiť scope.

### Najvyšší proces je vinník

Proces s najvyšším CPU môže vykonávať užitočnú prácu alebo reagovať na downstream problém. Root cause môže byť queue source, retry policy alebo iný resource.

### Reštart ako diagnóza

Restart mení state a môže odstrániť evidence. Je to mitigation, nie vysvetlenie.

### Zvýšenie všetkých limitov

Odstráni ochranné boundaries a môže presunúť incident na celý host. Limit sa mení iba po potvrdení workload requirementu a parent capacity.

### Priemer bez distribúcie

Priemer maskuje tail latency, bursty a odlišné request classes.

### Korelácia ako kauzalita

Dve metriky môžu rásť spolu pre spoločnú príčinu. Experiment alebo mechanistický dôkaz musí vysvetliť smer vzťahu.

## 51. Praktický host checklist

### Scope a timeline

- Definuj presný používateľský symptóm a request/job class.
- Urči začiatok, duration, affected scope a nedávne zmeny.
- Zachovaj artifact, config, host, namespace a cgroup identity.

### CPU

- Porovnaj utilization, run queue, PSI a cgroup throttling.
- Skontroluj per-core a per-thread rozloženie.
- Použi on-CPU alebo off-CPU profiler podľa hypotézy.

### Memory

- Rozlíš anonymous, file cache, slab, swap a cgroup charge.
- Sleduj reclaim, PSI, `memory.events` a OOM evidence.
- Použi časovú sériu a heap/runtime profiler pre leak hypotézu.

### Storage

- Over správny mount a device topology.
- Rozlíš blocks, inodes, quota a deleted-open files.
- Sleduj latency, queue, PSI a kernel errors.

### Network

- Postupuj DNS → route → link/neighbor → firewall → packet → transport → TLS → application.
- Over namespace a source address.
- Koreluj drops/retransmissions a socket queues s request dopadom.

### Process

- Skontroluj state, thread count, wait channel a child tree.
- Over file descriptors, rlimits, signals a syscalls.
- Over capability/LSM denials a service manager policy.

## 52. Kontrolné otázky

1. Prečo vysoká utilization nemusí znamenať bottleneck?
2. Aký je rozdiel medzi utilization, saturation a pressure?
3. Prečo treba začať používateľským symptómom a časovou osou?
4. Ako observation point a namespace menia interpretáciu príkazu?
5. Prečo load average nie je CPU percentage?
6. Ako potvrdíš CPU quota throttling ako príčinu latency?
7. Aký je rozdiel medzi on-CPU a off-CPU profilingom?
8. Ako rozlíšiš memory leak od cache alebo väčšieho working setu?
9. Prečo OOM killer nie je root cause?
10. Prečo sa `df` a `du` môžu líšiť?
11. Ako rozlíšiš TCP, TLS a application latency?
12. Kedy je `strace` vhodný a aké má riziká?
13. Ako Little's Law vysvetľuje rast concurrency pri vyššej latency?
14. Prečo priemer nestačí na tail-latency incident?
15. Aké vlastnosti má falzifikovateľná troubleshooting hypotéza?
16. Aký je rozdiel medzi mitigation a root-cause fixom?
17. Ako overíš, že náprava obnovila používateľský outcome a nie iba jednu metriku?

## 53. Zhrnutie

Linux performance troubleshooting je metodika, nie katalóg príkazov. Začína presným používateľským dopadom, scope a timeline, pokračuje vrstvovým resource a process observation a končí testovateľnou hypotézou, bezpečným experimentom a overenou nápravou.

USE, RED, PSI, cgroup events, profiling, syscall tracing a packet capture poskytujú rozdielne pohľady. Správny nástroj musí byť použitý na správnom hoste, namespace, cgroup a časovom intervale; až potom možno vytvoriť kauzálny reťazec medzi workloadom, kernelovým mechanizmom a používateľským výsledkom.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: SELinux a AppArmor](selinux-and-apparmor.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: OSI a TCP/IP model →](../02-networking-and-web/osi-and-tcp-ip-model.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
