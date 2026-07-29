# USE method

USE method je resource-oriented performance metodika. Pre každý relevantný bounded resource skúma **Utilization**, **Saturation** a **Errors**. Jej sila nie je v troch skratkách, ale v discipline: najprv vytvoriť úplný resource inventory, potom merať resource na jeho skutočnej enforcement boundary a až následne rozhodnúť, či je príčinou user-facing degradácie.

USE nenahrádza Golden Signals, RED, traces, logs ani profiles. Golden Signals a RED ukážu, ktorá služba a operácia degraduje. USE vysvetlí, ktorý resource nevie prácu obslúžiť a akým mechanizmom vzniká čakanie, throttling alebo failure.

## 1. Dominantný lifecycle

```text
user alebo business symptóm
→ exact service/operation a affected cohort
→ component a dependency path
→ complete resource inventory
→ exact resource subject a enforcement boundary
→ effective capacity/limit generation
→ utilization observation
→ saturation observation
→ resource error observation
→ competing resource hypotheses
→ discriminating evidence
→ containment alebo bounded capacity change
→ authoritative recovery
→ user/business a adjacent-cohort validation
→ resource inventory a observability closure
```

USE sa nezačína grafom CPU. Začína otázkou: **ktoré obmedzené resources musia úspešne obslúžiť affected operation?**

## 2. Exact resource-analysis subject

Resource finding má byť viazaný na presný subject. Pre Atlas Payments používame:

```text
resource-analysis subject: USE-PAY-44
business capability: CAP-PAY-42
observability subject: OBS-PAY-44
operation: final settlement
release: payments-api 7.20.0
account/Region: 100000000042 / eu-central-1
cohort: enterprise settlements v eu-central-1b
analysis window: 2026-07-29T08:10Z–08:35Z
resource: provider HTTP connection pool
resource owner: provider-adapter process
resource scope: jeden ECS task a provider host
configured generation: POOL-CFG-64
loaded/effective limit: 8 connections per task
caller concurrency: 32 settlement workers per task
```

Bez tohto subjectu možno zmiešať host CPU, container limit, task-local pool, service-wide provider quota a inú AZ. Všetky sú „capacity“, ale majú inú identity, ownera, limit a recovery.

## 3. Resource inventory pred metrics inventory

Resource je bounded capacity alebo service mechanism, ktorý vykonáva, prenáša, ukladá alebo povoľuje prácu. Inventory pre jednu request path môže obsahovať:

```text
client concurrency a retry budget
→ load balancer connections
→ task CPU quota a memory limit
→ worker/thread pool
→ provider connection pool
→ DNS/TLS socket resources
→ NAT/conntrack/port capacity
→ provider request quota
→ database connection pool
→ storage IOPS/throughput
```

Ak dashboard nemá metric pre provider connection pool, resource neprestáva existovať. Vzniká **known observability gap**, nie dôkaz, že pool nie je saturovaný.

Resource inventory má pre každú položku evidovať:

- logical owner a runtime owner;
- scope: process, container, Node, AZ, Region, account alebo provider;
- effective capacity a spôsob jej zmeny;
- utilization, saturation a error observations;
- resolution a aggregation boundary;
- failure behavior po vyčerpaní;
- relation k user outcome-u;
- recovery a validation path.

## 4. Enforcement boundary a effective capacity

Nominálna capacity nie je vždy capacity dostupná workloadu.

```text
nominálna kapacita
− reservations a unavailable members
− policy/quota limits
− topology a failover constraints
− per-process alebo per-tenant limits
− maintenance a unhealthy capacity
= effective capacity
```

Príklady:

- host má 32 vCPU, ale container má quota 4 vCPU;
- database povoľuje 2 000 sessions, ale application pool má maximum 80;
- subnet má voľné adresy, ale iba jedna AZ má vhodný placement;
- provider má account quota 1 000 requests/s, ale tenant-specific limit je 200;
- konfigurácia deklaruje 64 connections, ale loaded library používa default 8.

Meranie na nesprávnej boundary vytvára false reassurance. Host CPU 35 % nevylučuje container throttling. Service-wide pool utilization 50 % nevylučuje jeden task na 100 %.

## 5. Utilization

Utilization vyjadruje, aká časť effective capacity bola používaná v definovanom intervale.

Môže byť:

- časová: percento času CPU alebo device vykonával prácu;
- kapacitná: active connections / effective pool limit;
- throughputová: bytes/s alebo IOPS voči podporovanej hranici;
- populačná: used IPs, file descriptors alebo memory voči limitu.

Definícia musí byť explicitná. `80 % CPU`, `80 % memory` a `80 % connection pool` nemajú rovnakú semantiku.

Vysoká utilization sama osebe nie je incident. Batch job môže legitímne používať 100 % CPU. Connection pool môže byť plne využitý bez waiters. Rozhodujúce je, či vzniká čakanie, rejection, throttling alebo user impact.

### Aggregation risk

Priemer môže skryť:

- jeden hot core alebo serialized worker;
- jeden task s nesprávnym configom;
- jeden shard alebo AZ;
- burst kratší než query window;
- nerovnomerné traffic distribution;
- failover cohort s nižšou capacity.

Preto sa utilization analyzuje po exact resource instance alebo bounded cohort-e pred service-wide agregáciou.

## 6. Saturation

Saturation je extra práca, ktorú resource nevie okamžite obslúžiť. Prejavuje sa ako:

- queue length alebo oldest-item age;
- wait time alebo acquire latency;
- runnable, blocked alebo throttled tasks;
- connection waiters;
- allocation/reclaim stall;
- packet drops alebo retransmissions;
- request rejection alebo quota throttling;
- scheduler delay;
- backlog rastúci rýchlejšie než drain rate.

Saturation je často priamejší mechanizmus latency než utilization. Resource môže mať nízky dlhodobý priemer a napriek tomu vytvárať krátke kritické queues.

### Queue length a wait time

Queue length ukazuje množstvo čakajúcej práce. Wait time ukazuje dopad na operáciu. Obe potrebujú rate a service-time context:

```text
vyšší arrival rate alebo dlhší service time
→ resource zostane obsadený dlhšie
→ vzniknú waiters
→ rastie queue wait
→ rastie end-to-end latency
→ timeouty a retries môžu ďalej zvýšiť demand
```

### Hidden queues

Jedna request path môže obsahovať viac čakacích vrstiev:

```text
client backoff
→ load-balancer accept queue
→ application worker queue
→ provider connection-pool wait
→ DNS/TLS connection setup
→ provider-side queue
→ database lock wait
→ storage queue
```

Nízka queue na jednej vrstve nevylučuje saturation na inej.

## 7. Errors

Resource errors sú explicitné dôkazy, že resource alebo jeho capacity contract zlyhal. Patria sem:

- OOM kill alebo allocation failure;
- connection acquire timeout;
- rejected task alebo request;
- quota exceeded a throttling;
- device I/O error, timeout alebo reset;
- packet drop a failed connection;
- file descriptor alebo inode exhaustion;
- unhealthy pool member;
- hardware/ECC error;
- capacity allocation failure.

Error counter býva cumulative. Pri incidente sa používa rate alebo increase a korelácia s exact resource generation. Errors sa neignorujú pri nízkej utilization: redundantný member môže zlyhať a znížiť effective capacity bez okamžitého outage-u.

## 8. Typické resource classes

### CPU

- utilization: per-core busy time a container CPU use;
- saturation: run queue, scheduler wait, throttled time;
- errors: machine-check alebo quota/throttling events.

Celkové CPU 40 % nevylučuje jeden serialized core na 100 % ani container quota exhaustion.

### Memory

- utilization: working set voči cgroup alebo system capacity;
- saturation: reclaim, swap, major faults, allocation stalls, pressure;
- errors: OOM kill alebo failed allocation.

Nízke `free` memory môže byť zdravá cache. Dôležité je, či reclaim vytvára wait a či workload zostáva pod effective limitom.

### Storage a filesystem

- utilization: IOPS, throughput, busy time, used bytes/inodes;
- saturation: queue depth, await, throttling, burst-credit depletion;
- errors: failed I/O, timeout, read-only remount, full bytes alebo inodes.

### Network

- utilization: bandwidth, packets/s, active flows;
- saturation: interface queues, retransmissions, conntrack/NAT port pressure, connection latency;
- errors: drops, resets, DNS/TLS failures alebo route/MTU errors.

Nízka bandwidth utilization nevylučuje packet-rate alebo port exhaustion.

### Software pools a quotas

- utilization: active workers/connections/tokens voči limitu;
- saturation: waiters, queue age, acquire latency, throttling;
- errors: rejection, timeout, exhausted retry alebo quota response.

Software resource je rovnako reálny bottleneck ako fyzický device.

## 9. USE v incident workflowe

```text
Golden Signals alebo RED
→ ktorá user operation a cohort degraduje?
trace a dependency RED
→ na ktorej component boundary vzniká čas alebo failure?
USE
→ ktorý exact resource je utilized, saturated alebo erroring?
logs/profile/config evidence
→ prečo je effective capacity nižšia alebo service time vyšší?
```

USE bez user-facing scope-u môže optimalizovať resource bez relevantného dopadu. User-facing monitoring bez USE môže ukázať symptom bez bottleneck mechanizmu.

## 10. Worked failure: nízke CPU, ale saturovaný provider pool

### Symptóm

Po release `7.20.0` vzrastie enterprise final-settlement p95 z `740 ms` na `5.2 s`. HTTP acceptance zostáva rýchla, task CPU je priemerne `37 %` a memory `52 %`. Prvá hypotéza tímu je, že provider je všeobecne pomalý alebo že treba zvýšiť počet ECS tasks.

### Competing hypotheses

1. provider latency vzrástla pre všetky cohorts;
2. task CPU alebo memory je saturovaná;
3. NAT alebo network path stráca connections;
4. provider-side quota throttluje account;
5. per-task provider connection pool je saturovaný;
6. telemetry query agreguje nesprávny release alebo AZ;
7. queue pred workerom rastie ešte pred poolom.

### Resource inventory a observations

```text
enterprise logical traffic: stabilný
provider attempt rate: +31 % pre retries
provider span service time po získaní connection: p95 410 ms
pool configured value: 64
pool loaded/effective limit: 8 per task
active connections: 8/8
pool waiters: 180–420 per task
connection acquire p95: 2.7 s
worker concurrency: 32 per task
CPU throttling: 0
NAT allocation errors: 0
provider 429/quota errors: 0
```

Runtime library po rename config keyu nepoužila deklarovanú hodnotu `64`; načítala default `8`. Vyššia worker concurrency preto neznamenala vyššiu useful throughput. Viac workers čakalo na rovnakých osem connections.

Mechanizmus je:

```text
32 workers na task
→ iba 8 effective provider connections
→ connections zostávajú obsadené počas downstream callu
→ 24+ workers čaká
→ acquire latency dominuje logical duration
→ caller timeout spúšťa retries
→ attempts zvyšujú queue a provider demand
→ p95 a error-budget burn rastú pri nízkom CPU
```

### Containment

- zastaviť ďalší rollout a concurrency increase;
- obmedziť immediate retries a worker concurrency;
- zachovať per-task pool metrics, loaded config, traces a deployment evidence;
- neškálovať fleet naslepo, pretože ďalšie tasks by mohli znásobiť provider demand;
- chrániť healthy standard-merchant cohort.

### Authoritative recovery

1. opraviť config key a explicitne publikovať loaded effective pool limit;
2. nastaviť pool/concurrency podľa provider capacity contractu;
3. zaviesť bounded exponential backoff a retry budget;
4. canary-nuť jeden task a overiť pool utilization, waiters a logical duration;
5. rozšíriť rollout po AZ cohorts;
6. reconciliovať unknown settlement outcomes pred opakovaním business side effectu.

### Acceptance verdict

Recovery je prijatá iba keď:

- enterprise final-settlement success a latency SLI sa obnovia;
- pool waiters a acquire latency zostanú pod guardrailom;
- effective loaded limit je `64`, nie iba desired config;
- attempt amplification sa vráti k baseline;
- nevzniknú duplicate provider authorizations;
- standard cohort a susedná AZ neregresujú;
- druhý controlled rollout nezopakuje saturation.

## 11. Capacity planning a failover

USE finding je časovo viazaný. Capacity planning musí zohľadniť:

- growth a seasonality;
- traffic burst shape;
- loss jednej AZ alebo pool membera;
- deployment surge;
- scaling delay;
- provider a account quotas;
- maintenance a recovery capacity;
- cost.

Headroom sa počíta voči effective capacity po failure, nie iba voči nominálnemu steady-state súčtu.

## 12. Resource inventory template

```text
Resource-analysis subject:
Service/operation/cohort:
Resource a owner:
Scope/enforcement boundary:
Configured capacity generation:
Loaded/effective capacity:
Utilization observation:
Saturation observation:
Error observation:
Resolution/aggregation:
User-impact relation:
Competing hypotheses:
Discriminating evidence:
Containment:
Recovery:
Original outcome validation:
Forbidden outcome validation:
Known observability gap:
```

Inventory sa aktualizuje pri architecture, library, capacity, quota alebo topology zmene.

## 13. Troubleshooting chýbajúceho USE dôkazu

```text
resource je v inventory?
→ správna enforcement boundary?
→ effective limit je exportovaný alebo odvoditeľný?
→ utilization metric má správny denominator?
→ saturation queue/wait metric existuje?
→ resource errors majú counter a timestamp?
→ resolution zachytí burst?
→ aggregation neskrýva hot resource?
→ scrape/export/retention/query path je kompletný?
```

Absencia saturation metric nie je nulová saturation. Je to evidence gap, ktorý treba explicitne zaznamenať.

## 14. Anti-patterny

### Začať dostupnými grafmi

Dashboard inventory nahradí resource inventory a resource bez metric zostane neviditeľný.

### Utilization ako health verdict

Vysoká utilization môže byť zdravá a nízky priemer môže skrývať queues, throttling alebo hot shard.

### Nominálna capacity ako denominator

Ignoruje cgroup, pool, quota, failover, topology a loaded-state constraints.

### Service-wide average

Stratí per-task, per-core, per-shard alebo per-AZ saturation.

### Zvýšenie capacity bez demand kontroly

Môže amplifikovať retries alebo downstream overload namiesto odstránenia mechanizmu.

### Cloud alebo managed service ako neobmedzený resource

Quotas, concurrency, connections, partitions, IPs a rate limits zostávajú resource boundaries.

## 15. Kontrolné otázky

1. Prečo USE začína resource inventory, nie dashboardom?
2. Čo tvorí exact resource-analysis subject?
3. Aký je rozdiel medzi nominal a effective capacity?
4. Prečo utilization bez saturation nestačí?
5. Ako queue length a wait time vysvetľujú rozdielny dopad?
6. Čo sú hidden queues?
7. Ako enforcement boundary mení interpretáciu CPU alebo memory?
8. Prečo nízky bandwidth nevylučuje network saturation?
9. Ako USE nadväzuje na Golden Signals, RED a traces?
10. Ako overíš, že capacity recovery neamplifikovala downstream demand?

## Glossary impact

Relevantné pojmy: resource-analysis subject, resource inventory, effective resource capacity, enforcement boundary, utilization observation, saturation observation, resource error observation, hidden-queue inventory, capacity headroom, loaded resource limit a USE acceptance verdict.

## Primárne zdroje

- [Brendan Gregg — The USE Method](https://www.brendangregg.com/usemethod.html)
- [Brendan Gregg — USE Method Rosetta Stone](https://www.brendangregg.com/USEmethod/use-rosetta.html)
- [Brendan Gregg — Performance Analysis Methodology](https://www.brendangregg.com/methodology.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: RED method](red-method.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Golden Signals →](golden-signals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
