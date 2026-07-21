# USE method

USE method je resource-oriented performance metodika vytvorená Brendanom Greggom. Pre každý relevantný resource systematicky preveruje **Utilization**, **Saturation** a **Errors**. Cieľom je rýchlo a úplne prejsť resource model bez náhodného klikania cez dostupné grafy.

USE je primárne metodika na hľadanie resource bottlenecks a failures. Nenahrádza workload characterization, RED, distributed tracing, application profiling ani business-level monitoring.

## 1. Mentálny model

Pre každý resource sa opýtaj:

```text
ako veľmi je resource používaný?          → Utilization
koľko práce čaká alebo sa nevie obslúžiť? → Saturation
aké failures resource hlási?              → Errors
```

Resource inventory je dôležitejší než zoznam existujúcich metrics.

## 2. Resource

Resource je obmedzená kapacita, ktorá vykonáva alebo podporuje prácu.

Príklady:

- CPU execution capacity,
- memory capacity,
- disk alebo block-device I/O,
- network interface a link,
- filesystem space a inodes,
- process/thread pool,
- connection pool,
- file descriptors,
- queue workers,
- database connections,
- API quota,
- Kubernetes Node allocatable capacity,
- cloud subnet IP addresses,
- GPU compute a memory,
- NAT connection/port capacity.

USE začína resource mapou. Ak resource nie je v checkliste, môže sa úplne prehliadnuť.

## 3. Utilization

Utilization vyjadruje, ako veľká časť dostupnej kapacity je používaná v sledovanom intervale.

Príklady:

- percento času CPU vykonáva prácu,
- disk busy time,
- network throughput voči link capacity,
- memory used voči usable capacity,
- active connections voči pool limitu,
- GPU compute utilization,
- used subnet IPs voči available IPs.

### Time-based a capacity-based utilization

Utilization môže znamenať:

- percento času resource pracoval,
- percento obsadenej kapacity,
- throughput voči maximálnemu výkonu,
- concurrency voči limitu.

Definícia musí byť explicitná. `CPU utilization 80 %` a `memory utilization 80 %` nemajú rovnakú interpretáciu.

### Average utilization

Priemerná utilization môže maskovať:

- hot core,
- hot disk,
- jednu preťaženú AZ,
- jeden shard,
- jeden network queue,
- krátke spikes,
- uneven load distribution.

Sleduj distribution podľa jednotlivých resources a vhodný časový interval.

### Vysoká utilization nie je automaticky chyba

Resource môže byť efektívne využitý bez user impactu.

Príklady:

- CPU-bound batch job môže správne používať takmer 100 % CPU,
- cache môže zámerne používať väčšinu memory,
- network link môže byť vysokou mierou využitý bez packet loss alebo queueing.

Utilization interpretuj spolu so saturation, errors a workload demand-om.

## 4. Saturation

Saturation vyjadruje prácu, ktorú resource nemôže okamžite obslúžiť.

Prejavuje sa ako:

- queue length,
- wait time,
- run queue,
- blocked tasks,
- thread-pool queue,
- connection waiters,
- throttling,
- swap pressure,
- packet drops,
- I/O wait,
- request rejection,
- scheduling delay.

Saturation je často skorší a presnejší signal user-impactu než vysoká average utilization.

### Queue length oproti wait time

Queue length ukazuje množstvo čakajúcej práce.

Wait time ukazuje dopad na jednotlivú operáciu.

Krátka queue pri extrémne pomalom resource-e môže byť kritická. Dlhšia queue pri veľmi rýchlom processingu nemusí mať rovnaký dopad.

### Hidden queues

Queues môžu existovať vo viacerých vrstvách:

```text
client retry/backoff
→ load balancer queue
→ application accept queue
→ thread pool
→ connection pool
→ database lock wait
→ disk scheduler
→ device queue
```

Sledovanie iba jednej queue môže viesť k nesprávnemu root cause-u.

## 5. Errors

Errors zahŕňajú explicitné resource failures.

Príklady:

- ECC alebo hardware errors,
- disk I/O errors,
- filesystem errors,
- packet errors/drops,
- failed allocation,
- out-of-memory kill,
- connection pool timeout,
- file descriptor exhaustion,
- quota exceeded,
- throttling/rejection,
- GPU errors,
- device reset.

Error counter môže byť cumulativny. Pri diagnostike sleduj rate/increase a timestamp correlation.

Errors sa nemajú ignorovať len preto, že utilization a saturation sú nízke. Hardware alebo configuration failure môže znižovať dostupnú kapacitu alebo spôsobovať silent degradation.

## 6. USE checklist

Základný postup:

1. vytvor resource inventory,
2. pre každý resource nájdi utilization signal,
3. nájdi saturation signal,
4. nájdi error signal,
5. identifikuj chýbajúce observability gaps,
6. koreluj findings s workloadom a user impactom,
7. iteruj na sub-resources.

Príklad:

| Resource | Utilization | Saturation | Errors |
|---|---|---|---|
| CPU | busy time per core | run queue, throttling | machine check, throttling events |
| Memory | working set/capacity | reclaim, swap, allocation stall | OOM, allocation failure |
| Disk | busy time, throughput | queue depth, await | I/O errors, timeouts |
| Network | throughput/link | queue, drops, retransmits | interface/protocol errors |
| Thread pool | active/max | queued tasks, wait | rejected tasks |
| DB pool | active/max | waiters, acquire latency | acquire timeout |

## 7. CPU

### Utilization

- per-core busy time,
- user/system/steal/irq categories,
- container CPU usage,
- quota consumption.

### Saturation

- run queue,
- scheduler wait,
- CPU throttling,
- runnable threads,
- load average interpretovaná spolu s CPU countom a task state-om.

### Errors

- hardware machine-check events,
- thermal throttling,
- CPU quota rejections alebo throttled periods podľa platformy.

### Caveats

Celkový CPU môže byť 40 %, ale jeden serialized worker alebo core môže byť na 100 %. Virtualized environment môže mať steal alebo host contention.

## 8. Memory

Memory utilization nie je jednoduché `used / total`.

Rozlišuj:

- application resident set,
- page cache,
- reclaimable memory,
- working set,
- cgroup/container limit,
- kernel memory,
- swap,
- committed virtual memory.

### Saturation

- reclaim pressure,
- major page faults,
- swap in/out,
- allocation stalls,
- compaction,
- memory PSI,
- container near-limit behavior.

### Errors

- OOM kill,
- allocation failure,
- cgroup limit breach,
- ECC error.

Free memory blízka nule môže byť normálna kvôli cache. Kritické je, či systém dokáže memory uvoľniť bez významného waitu a failures.

## 9. Storage a block I/O

### Utilization

- device busy time,
- IOPS,
- throughput,
- provisioned performance consumption.

### Saturation

- queue depth,
- await/service time,
- throttling,
- burst balance depletion,
- filesystem wait,
- storage network congestion.

### Errors

- read/write failures,
- timeouts,
- resets,
- filesystem corruption,
- capacity alebo inode exhaustion.

100 % device utilization nemusí znamenať rovnaký throughput pre sequential a random workload. Latency a queueing sú kritické.

## 10. Network

### Utilization

- bytes/bits per second voči link alebo service capacity,
- packets per second,
- connection count,
- flow/table capacity.

### Saturation

- interface queue,
- packet drops,
- retransmissions,
- buffer pressure,
- conntrack/NAT port pressure,
- connection establishment latency.

### Errors

- CRC/interface errors,
- dropped packets,
- failed connections,
- reset rate,
- DNS resolution failures,
- route/MTU errors.

Low bandwidth utilization nevylučuje packet-per-second, connection alebo NAT port saturation.

## 11. Filesystem

Resources:

- bytes capacity,
- inodes,
- file descriptors,
- mount availability,
- metadata operations.

Sleduj:

- used space,
- inode usage,
- allocation growth,
- blocked writes,
- read-only remount,
- I/O errors,
- open-file exhaustion.

Filesystem môže zlyhať pre nedostatok inodes aj pri dostatku voľných bytes.

## 12. Pools a software resources

USE sa dá aplikovať aj na bounded software resources.

### Thread pool

- utilization: active workers / max workers,
- saturation: queue a task wait,
- errors: rejection, timeout, worker crash.

### Database connection pool

- utilization: active connections / max,
- saturation: waiters a acquire latency,
- errors: acquire timeout, broken connection.

### Queue worker pool

- utilization: busy workers,
- saturation: backlog a oldest item age,
- errors: failed/dead-letter items.

### API quota

- utilization: requests alebo capacity units voči quota,
- saturation: throttling/backoff queue,
- errors: quota exceeded alebo rate-limit response.

## 13. Kubernetes a containers

Relevantné resources:

- Node CPU a memory,
- Pod/container CPU quota a memory limit,
- ephemeral storage,
- PID limits,
- Node allocatable,
- image filesystem,
- CNI IP capacity,
- volume IOPS/throughput,
- API server inflight requests,
- scheduler/controller queues.

Príklady:

- CPU utilization nízka, ale container je throttled pre nízky limit,
- Node memory vyzerá zdravo, ale konkrétny Pod dosahuje cgroup limit,
- cluster má CPU, ale Pods sú Pending pre topology alebo IP exhaustion,
- storage throughput je pod limitom, ale latency rastie pre burst-credit depletion.

Resource boundary musí zodpovedať enforcement boundary.

## 14. Cloud resources

Cloud abstrahuje hardware, ale resource limits nezmiznú.

Príklady:

- EBS IOPS/throughput a queue,
- RDS connections/storage/IO,
- Lambda concurrency,
- NAT ports/connections,
- subnet IP addresses,
- load balancer capacity,
- service quotas,
- API throttling,
- KMS request quotas,
- streaming shards/partitions.

Nie všetky limits sú publikované ako jednoduché percento. Potrebný môže byť derived utilization alebo saturation signal.

## 15. USE a pressure metrics

Linux Pressure Stall Information a podobné metrics merajú čas, keď tasks čakajú na CPU, memory alebo I/O resources.

Pressure môže lepšie vyjadriť saturation než samotná utilization.

Príklad:

- memory used je vysoká,
- ale bez reclaim stall nie je user impact,
- po raste memory pressure a allocation stalls rastie latency.

Pressure metrics interpretuj spolu s workload a cgroup scope-om.

## 16. USE a time windows

Krátke spikes sa môžu stratiť v dlhom average.

Použi:

- high-resolution interval počas incidentu,
- max alebo quantiles per resource,
- per-core/per-device breakdown,
- workload/deployment correlation,
- sustained a burst thresholds.

Scrape interval musí byť dostatočne krátky vzhľadom na failure duration.

## 17. USE a capacity planning

USE pomáha identifikovať headroom, ale capacity planning potrebuje aj:

- workload growth,
- traffic shape,
- seasonality,
- failover capacity,
- deployment surge,
- maintenance,
- quotas,
- scaling delay,
- cost.

Nízka saturation dnes neznamená dostatok capacity pri strate jednej AZ alebo počas peak-u.

## 18. USE a RED

RED začína user-facing službou.

USE začína resources.

Odporúčaný incident postup:

```text
RED: ktorá služba a operation degraduje?
→ trace: ktorá component alebo dependency?
→ USE: ktorý resource je využitý, saturovaný alebo chybný?
→ logs/profile: prečo?
```

Použitie USE bez RED môže optimalizovať resource, ktorý nemá user impact. Použitie RED bez USE môže ukázať symptom bez bottleneck mechanizmu.

## 19. Resource inventory template

```text
Resource:
Scope/enforcement boundary:
Capacity/limit:
Utilization metric:
Saturation metric:
Error metric:
Resolution:
Expected baseline:
Critical threshold alebo SLO relation:
Owner:
Runbook:
Known observability gap:
```

Inventory udržiavaj spolu s architecture a capacity changes.

## 20. Troubleshooting príklady

### Latency rastie pri CPU 45 %

Over:

- per-core utilization,
- throttling,
- run queue,
- serialized worker,
- lock contention,
- downstream wait.

### Memory 95 %, ale služba je zdravá

Over working set, reclaim, swap, pressure a OOM events. Môže ísť o efektívnu cache.

### Disk throughput je nízky, latency vysoká

Over queue depth, IOPS limit, random I/O, burst credits, device errors a downstream storage service.

### Connection pool má 100 % utilization

Over waiters a acquire latency. Ak nie sú, pool môže byť správne dimenzovaný; ak rastú, ide o saturation.

### Network bandwidth je nízky, requests zlyhávajú

Over packet loss, PPS, NAT/conntrack, DNS, TLS handshake a connection limits.

## 21. Anti-patterny

### Začať dostupnými grafmi

Vedie k metric bias a prehliadnutiu resource-u bez dashboardu.

### Utilization ako jediný signal

Saturation a errors môžu rásť skôr alebo pri nízkom average.

### Agregovať všetky resources

Hot shard, core, AZ alebo device sa stratí.

### CPU load average interpretovaný izolovane

Bez CPU countu, task states a run-queue kontextu môže zavádzať.

### Memory free ako hlavný signal

Ignoruje cache, working set, reclaim a pressure.

### Cloud service považovaná za neobmedzenú

Quotas, concurrency, IOPS, connection a capacity limits stále existujú.

## 22. Kontrolné otázky

1. Čo znamenajú Utilization, Saturation a Errors?
2. Prečo USE začína resource inventory?
3. Ako sa líši utilization CPU a memory?
4. Prečo saturation často lepšie vysvetľuje latency?
5. Čo sú hidden queues?
6. Ako aplikuješ USE na connection pool?
7. Ako container limits menia resource boundary?
8. Prečo nízky bandwidth nevylučuje network saturation?
9. Ako USE súvisí s RED?
10. Ako by vyzeral USE checklist pre tvoju službu?

## Glossary impact

Relevantné pojmy: USE method, resource inventory, utilization, saturation, error counter, hidden queue, run queue, pressure stall, memory reclaim, working set, connection-pool saturation, resource boundary, enforcement boundary a capacity headroom.

## Primárne zdroje

- [Brendan Gregg — The USE Method](https://www.brendangregg.com/usemethod.html)
- [Brendan Gregg — USE Method Rosetta Stone](https://www.brendangregg.com/USEmethod/use-rosetta.html)
- [Brendan Gregg — Performance Analysis Methodology](https://www.brendangregg.com/methodology.html)
- [Grafana dashboard best practices — USE method](https://grafana.com/docs/grafana/latest/visualizations/dashboards/build-dashboards/best-practices/)
