# Linux Performance and Troubleshooting

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: všetky predchádzajúce kapitoly sekcie Linux and Systems
- Súvisiace témy: observability, SRE, incident response, capacity planning, eBPF, profiling

## 1. Definícia

Linux performance troubleshooting je systematický proces identifikácie vrstvy, resource alebo mechanizmu, ktorý spôsobuje degradáciu správania systému.

Cieľom nie je nájsť „vysoké číslo“, ale vysvetliť kauzálny reťazec medzi workloadom, resource pressure, kernel správaním a používateľským dopadom.

## 2. Problém, ktorý rieši

Symptómy ako „server je pomalý“, „CPU je vysoké“ alebo „disk nestíha“ sú príliš všeobecné.

Rovnaký používateľský symptóm môže vzniknúť z rozdielnych príčin:

- CPU saturation,
- lock contention,
- memory pressure a reclaim,
- storage latency,
- network packet loss alebo retransmissions,
- DNS alebo TLS delay,
- cgroup throttling,
- dependency timeout,
- application queueing,
- chybná konfigurácia po deploymente.

Troubleshooting musí rozlišovať vrstvu, rozsah a časový priebeh.

## 3. Základný model: utilization, saturation, errors

USE method pre každý resource:

- **Utilization** — akú časť kapacity resource používa,
- **Saturation** — koľko práce čaká, pretože resource nestačí,
- **Errors** — zlyhania alebo degradované operácie.

Príklad CPU:

```text
utilization: CPU time
saturation: runnable queue, throttling, PSI
errors: machine check, thermal throttling, scheduler anomalies
```

Príklad storage:

```text
utilization: device busy time
saturation: queue depth, await, I/O PSI
errors: filesystem/device errors, timeouts, resets
```

Vysoká utilization bez saturation nemusí byť problém. Nízka priemerná utilization s krátkymi saturation burstami môže spôsobovať vysokú tail latency.

## 4. Začni používateľským dopadom

Pred spustením príkazov definuj:

- čo je pomalé alebo nefunkčné,
- odkedy,
- koho a ktoré requests to ovplyvňuje,
- či je problém trvalý alebo prerušovaný,
- čo sa zmenilo,
- aký je očakávaný baseline,
- ktoré SLI alebo business metriky degradovali.

Bez toho môže diagnostika optimalizovať resource, ktorý nie je bottleneck.

## 5. Golden workflow

```text
1. Potvrď symptóm
2. Urči rozsah a čas
3. Skontroluj nedávne zmeny
4. Pozri top-level resource pressure
5. Zúž problém na host, cgroup, process, thread alebo request
6. Vytvor hypotézu
7. Získaj dôkaz, ktorý ju môže potvrdiť alebo vyvrátiť
8. Urob najmenšiu bezpečnú nápravu
9. Over používateľský výsledok
10. Zachyť prevenciu a monitoring gap
```

Troubleshooting nie je sekvencia náhodných príkazov. Každý krok má testovať konkrétnu hypotézu.

## 6. Rýchly host-level prehľad

Užitočný prvý snapshot:

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

Pri storage:

```bash
iostat -xz 1
findmnt
df -h
df -i
```

Tento prehľad má určiť ďalšiu vetvu diagnostiky. Nie je sám o sebe root cause analýzou.

## 7. CPU troubleshooting

### Otázky

- Je vysoké user CPU alebo system CPU?
- Je problém na všetkých cores alebo jednom core?
- Je workload runnable alebo čaká?
- Existuje CPU quota throttling?
- Sú vysoké context switches alebo interrupts?
- Ide o užitočnú prácu, busy loop, lock contention alebo retry storm?

Príkazy:

```bash
mpstat -P ALL 1
pidstat -u -t 1
top -H -p <PID>
ps -eo pid,tid,psr,stat,comm,%cpu --sort=-%cpu
cat /proc/<PID>/cgroup
```

Cgroup throttling:

```bash
cat /sys/fs/cgroup/<path>/cpu.max
cat /sys/fs/cgroup/<path>/cpu.stat
cat /sys/fs/cgroup/<path>/cpu.pressure
```

### Sampling profiler

```bash
sudo perf top
sudo perf record -F 99 -g -p <PID> -- sleep 30
sudo perf report
```

Profil ukáže, kde CPU čas skutočne trávi proces alebo kernel. Interpretácia vyžaduje symbols a znalosť aplikácie.

### Jeden core na 100 %

Možné príčiny:

- single-threaded execution,
- global lock,
- CPU affinity,
- hot shard alebo queue,
- interrupt concentration,
- runtime garbage collection thread.

Host-wide CPU môže vyzerať nízko, ale latency jednej kritickej služby môže byť vysoká.

## 8. Load average

Load average zahŕňa runnable tasks a niektoré tasks v uninterruptible sleep.

```bash
uptime
cat /proc/loadavg
```

Interpretácia:

- porovnaj s počtom logical CPUs,
- over runnable queue cez `vmstat` alebo scheduler metrics,
- skontroluj tasks v `D` state,
- rozlíš CPU queue od I/O wait.

```bash
ps -eo state,pid,tid,wchan:32,comm | awk '$1 ~ /^D/'
```

Vysoký load s nízkym CPU usage často smeruje k I/O alebo kernel waiting, nie automaticky k potrebe ďalších CPUs.

## 9. Memory troubleshooting

### Základné zdroje

```bash
free -h
cat /proc/meminfo
vmstat 1
ps aux --sort=-%mem | head
cat /proc/<PID>/smaps_rollup
```

Rozlišuj:

- anonymous memory,
- file-backed pages,
- page cache,
- slab/kernel memory,
- swap,
- cgroup charge,
- reclaim pressure.

### Memory pressure

```bash
cat /proc/pressure/memory
cat /sys/fs/cgroup/<path>/memory.pressure
cat /sys/fs/cgroup/<path>/memory.events
```

Jednorazový snapshot nestačí na rozlíšenie memory leak, workload growth a cache warming.

### OOM

```bash
journalctl -k -b | grep -i -E 'oom|out of memory|killed process'
cat /sys/fs/cgroup/<path>/memory.events
```

Root cause nie je „OOM killer“. Ten je posledný recovery mechanizmus. Hľadaj:

- leak,
- nízky limit,
- burst,
- concurrency,
- page cache pressure,
- absent backpressure,
- nesprávny capacity model.

## 10. Storage a filesystem troubleshooting

### Capacity

```bash
df -h
df -i
du -xhd1 /var | sort -h
```

Rozlišuj:

- voľné bloky,
- voľné inodes,
- deleted-open files,
- filesystem reserved space,
- quota,
- underlying volume capacity.

Deleted-open files:

```bash
sudo lsof +L1
```

### Latency a saturation

```bash
iostat -xz 1
pidstat -d 1
cat /proc/pressure/io
```

Dôležité metriky závisia od storage stacku, ale sleduj:

- request latency,
- queue depth,
- throughput,
- utilization,
- read/write mix,
- retries a device errors.

Vysoké `%util` na modernom paralelnom storage nie je vždy rovnaký signál ako na jednom rotačnom disku. Potrebuješ poznať device model a queueing.

### Kernel logs

```bash
journalctl -k -b | grep -i -E 'I/O error|reset|timeout|filesystem|ext4|xfs|nvme|scsi'
```

Device reset alebo filesystem error môže byť dôležitejší než aplikácia s najvyšším I/O.

## 11. Network troubleshooting

Vrstva po vrstve:

```text
name resolution
→ route a source address
→ local interface/link
→ firewall/policy
→ packet path
→ TCP/UDP state
→ TLS
→ application protocol
```

Príkazy:

```bash
getent hosts example.com
ip route get <IP>
ip neigh
ss -lntup
ss -tan
ip -s link
nstat
tcpdump -ni any host <IP>
```

Sleduj:

- drops a errors na interface,
- retransmissions,
- SYN backlog,
- connection states,
- MTU symptoms,
- DNS latency,
- asymmetric return path,
- namespace context.

Ping nie je test application availability.

## 12. Process a thread troubleshooting

```bash
ps -eo pid,ppid,tid,stat,wchan:32,comm
pstree -ap <PID>
cat /proc/<PID>/status
ls -l /proc/<PID>/fd
```

### `strace`

```bash
sudo strace -ff -tt -T -p <PID>
```

Ukazuje system calls, ich arguments, výsledky a trvanie.

Použitie:

- zistiť, na čom proces čaká,
- odhaliť opakované failed opens alebo connects,
- vidieť blocking syscalls,
- rozlíšiť application compute od kernel wait.

Riziká:

- overhead,
- veľký objem dát,
- citlivé arguments,
- zmena timing-u,
- ptrace security obmedzenia.

### `/proc/<PID>/stack` a `wchan`

Môžu ukázať kernel wait point threadu. Sú užitočné pri tasks v `D` state alebo pri low-level blocking analýze.

## 13. File descriptors a limits

Symptómy:

```text
Too many open files
connection accept failures
log file open errors
```

Kontrola:

```bash
cat /proc/<PID>/limits
ls /proc/<PID>/fd | wc -l
sudo lsof -p <PID>
sysctl fs.file-nr
```

Rozlišuj:

- per-process soft/hard rlimit,
- systemd `LimitNOFILE`,
- host-wide file table,
- application leak,
- legitimate connection growth.

Zvýšenie limitu bez opravy descriptor leak iba odďaľuje incident.

## 14. cgroup a container context

Host-wide metriky nemusia vysvetliť lokálny workload incident.

Kontroluj:

```bash
cat /proc/<PID>/cgroup
systemctl show <unit> -p ControlGroup -p MemoryCurrent -p MemoryMax
cat /sys/fs/cgroup/<path>/cpu.stat
cat /sys/fs/cgroup/<path>/memory.events
cat /sys/fs/cgroup/<path>/pids.events
```

Pri containers a Kubernetes porovnaj:

```text
orchestrator desired resources
→ runtime settings
→ cgroup fields
→ process behavior
```

## 15. Logs, metrics, traces a profiles

Každý signál odpovedá na inú otázku:

- logs: čo program explicitne oznámil,
- metrics: ako sa hodnota mení v čase,
- traces: kde request strávil čas naprieč komponentmi,
- profiles: kde proces trávi CPU alebo memory,
- events/audit: čo kernel alebo security vrstva rozhodla.

Jeden signál nie je automaticky autoritatívny pre celý incident.

## 16. Baseline a časová korelácia

Výkonové číslo bez baseline je slabý dôkaz.

Porovnávaj:

- rovnaký host pred incidentom,
- rovnakú službu na zdravom hoste,
- rovnakú hodinu predchádzajúceho dňa,
- pred a po deploymente,
- normalizované hodnoty na request alebo workload unit.

Časová os by mala spájať:

```text
deployment/config change
→ resource behavior
→ application latency/errors
→ recovery action
```

Korelácia nie je automaticky kauzalita, ale pomáha vytvárať testovateľné hypotézy.

## 17. Little's Law a queueing intuition

Zjednodušený vzťah:

```text
concurrency = throughput × time in system
```

Ak throughput zostáva rovnaký a latency rastie, rastie aj počet rozpracovaných requests.

To môže zvýšiť:

- memory usage,
- open connections,
- queue depth,
- lock contention,
- timeout cascades.

Výkonový incident preto môže byť pozitívna spätná väzba, nie izolovaný pomalý komponent.

## 18. Coordinated omission a percentily

Pri latency sleduj percentily, nie iba priemer.

```text
p50 = typický request
p95/p99 = tail behavior
```

Priemer môže skryť malú, ale dôležitú skupinu veľmi pomalých requests.

Load test musí generovať požadovanú arrival rate aj počas spomalenia. Inak môže vynechať requests, ktoré by reálni používatelia poslali, a podhodnotiť latency — coordinated omission.

## 19. eBPF a moderné observability nástroje

eBPF umožňuje bezpečne spúšťať overený bytecode na definovaných kernel hooks.

Použitie:

- syscall latency,
- scheduler delay,
- TCP retransmissions,
- block I/O latency,
- off-CPU profiling,
- network tracing.

Nástroje môžu zahŕňať BCC, bpftrace alebo distribučné eBPF observability platformy.

Príklady konceptu:

```bash
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_openat { @[comm] = count(); }'
```

Používaj ich cielene. eBPF nie je náhrada základného layer-by-layer modelu a môže mať version, privilege a overhead obmedzenia.

## 20. Zmeny počas incidentu

Pred zmenou zaznamenaj:

- hypotézu,
- očakávaný efekt,
- rollback,
- riziko,
- spôsob overenia.

Preferuj reverzibilné kroky:

- zníženie trafficu,
- rollback poslednej zmeny,
- scale-out pri potvrdenej saturation,
- vypnutie problémovej feature flagom,
- izoláciu chybného workloadu.

Náhodný restart môže obnoviť službu, ale zničiť diagnostické dôkazy a maskovať root cause.

## 21. Anti-patterny

### Metric roulette

Prezeranie veľkého počtu dashboardov bez hypotézy.

### Restart-first troubleshooting

Restart pred zachytením stavu. Môže odstrániť symptóm aj dôkaz.

### Single-metric diagnosis

„CPU je 90 %, takže treba viac CPU.“ Bez saturation, throughput a latency kontextu je záver slabý.

### Tuning before measurement

Zmena sysctl, JVM flags alebo database settings bez baseline a experimentu.

### Blame the network

Sieť sa označí za príčinu bez packet, route, loss alebo latency dôkazu.

### Permanent debug logging

Dočasné detailné logovanie zostane zapnuté a vytvorí I/O, storage alebo privacy problém.

## 22. Praktický diagnostický checklist

### Scope

- jeden request, používateľ, process, host, AZ alebo celý systém?
- začiatok a trvanie?
- čo sa zmenilo?

### CPU

- utilization per core,
- runnable queue,
- quota throttling,
- hot threads,
- profiles.

### Memory

- working set,
- reclaim a swap,
- PSI,
- cgroup events,
- OOM evidence.

### Storage

- capacity a inodes,
- latency a queue,
- device/filesystem errors,
- deleted-open files.

### Network

- DNS,
- route,
- drops/retransmissions,
- sockets,
- packet capture,
- TLS/application layer.

### Process

- state a wchan,
- file descriptors,
- syscalls,
- limits,
- namespaces a cgroups.

## 23. Kontrolné otázky

1. Aký je rozdiel medzi utilization a saturation?
2. Prečo vysoký load average nemusí znamenať vysoké CPU usage?
3. Ako rozlíšiš host-wide a cgroup-local resource problém?
4. Prečo je OOM killer mechanizmus, nie root cause?
5. Kedy je `strace` vhodný a aké má riziká?
6. Prečo priemer latency nestačí?
7. Ako Little's Law pomáha chápať rast concurrency?
8. Prečo restart môže poškodiť troubleshooting?
9. Kedy použiť profiler a kedy packet capture?
10. Ako overíš, že náprava skutočne obnovila používateľský výsledok?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: SELinux a AppArmor](selinux-and-apparmor.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: OSI a TCP/IP model →](../02-networking-and-web/osi-and-tcp-ip-model.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
