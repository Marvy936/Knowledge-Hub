# Scalability, elasticity a fault tolerance

Scalability, elasticity a fault tolerance opisujú odlišné vlastnosti systému. Často sa zamieňajú, pretože všetky súvisia s kapacitou a odolnosťou, ale riešia iné otázky:

```text
Scalability    → dokáže systém zvládnuť väčší workload?
Elasticity     → dokáže kapacitu automaticky prispôsobiť zmene workloadu?
Fault tolerance → dokáže pokračovať bez významného prerušenia pri zlyhaní komponentu?
```

## 1. Scalability

Scalability je schopnosť systému zvýšiť alebo znížiť spracovateľskú kapacitu bez neprimeraného zhoršenia výkonu, spoľahlivosti alebo nákladov.

Rozlišuj:

- compute scale,
- storage scale,
- network scale,
- database scale,
- control-plane scale,
- organizational a operational scale.

Systém môže škálovať compute vrstvu a stále zlyhať na databáze, locku, queue partition alebo quota.

## 2. Vertical scaling

Vertical scaling mení kapacitu jedného resource-u:

```text
väčšia VM
viac CPU/memory
väčší database instance class
vyšší storage performance tier
```

Výhody:

- jednoduchší application model,
- menej distributed-system complexity,
- vhodné pre legacy alebo single-node workload.

Limity:

- maximálna dostupná veľkosť,
- restart alebo migration,
- väčší blast radius,
- skokové ceny,
- single-resource failure domain.

Vertical scaling môže byť správny, ale nie nekonečný.

## 3. Horizontal scaling

Horizontal scaling pridáva alebo odoberá instances, workers, partitions alebo replicas.

Vyžaduje:

- distribúciu trafficu alebo práce,
- stateless alebo externalized state,
- idempotenciu,
- partitioning alebo sharding podľa potreby,
- coordination a consistency model,
- health checking,
- graceful scale-in.

Horizontal compute scale nepomôže, ak všetky replicas čakajú na jednu serializovanú dependency.

## 4. Diagonal scaling

Diagonal scaling kombinuje vertical a horizontal prístup:

- instances sa zväčšia do efektívneho bodu,
- následne sa pridávajú ďalšie instances,
- pri poklese sa zmenšuje count alebo size.

Môže optimalizovať cost, ale komplikuje capacity model a autoscaling.

## 5. Elasticity

Elasticity je schopnosť dynamicky pridávať a odoberať kapacitu podľa demandu.

Potrebuje:

- merateľný signal,
- scaling policy,
- provisioning čas,
- warm-up/readiness,
- scale-in protection,
- capacity a quota,
- cost guardrails,
- cooldown alebo stabilization.

Elasticita nie je okamžitá. Každý resource má provisioning latency a capacity limit.

## 6. Reactive a predictive scaling

### Reactive

Reaguje na aktuálny signal:

- CPU,
- request count,
- queue depth,
- latency,
- custom business metric.

Riziko: scaling nastane až po začiatku špičky.

### Predictive

Používa historické patterns alebo forecast na prípravu kapacity pred špičkou.

Riziko: zmena správania alebo jednorazová udalosť môže model zmiasť.

Kritické workloady často kombinujú baseline, scheduled/predictive a reactive scaling.

## 7. Scale-out signal

Dobrý signal musí korelovať s potrebnou kapacitou.

CPU nie je univerzálny:

- I/O-bound service môže mať nízke CPU a vysokú latency,
- queue worker sa lepšie škáluje podľa backlog age alebo depth,
- web tier podľa request rate alebo concurrency,
- stream consumer podľa lag,
- database podľa connections, IOPS, locks alebo replicas.

Scale policy musí odrážať bottleneck.

## 8. Scale-in

Scale-in je rizikovejší než scale-out, pretože odoberá aktívnu kapacitu.

Potrebné je:

- connection draining,
- graceful shutdown,
- work handoff,
- idempotent retry,
- scale-in protection pre kritický job,
- minimum healthy capacity,
- stabilization window,
- state cleanup.

Nesprávny scale-in môže spôsobiť dropped requests, duplicate processing alebo data loss.

## 9. Stateless a stateful scaling

### Stateless tier

Každá replika spracuje ľubovoľný request bez lokálneho authoritative state-u.

### Stateful tier

Potrebuje:

- data partitioning,
- replication,
- leader/follower model,
- consistency,
- rebalancing,
- storage throughput,
- failover.

Stateful scaling je často dominantná komplexita celého systému.

## 10. Queue-based load leveling

Queue oddelí producer a consumer rate:

```text
producer → queue → workers
```

Výhody:

- absorbuje burst,
- umožňuje retry,
- worker count sa škáluje podľa backlogu,
- chráni downstream.

Potrebuje:

- visibility timeout,
- dead-letter handling,
- idempotent consumer,
- poison-message strategy,
- backlog age SLO.

Queue nezvyšuje nekonečne kapacitu; iba odkladá prácu.

## 11. Backpressure

Keď downstream nestíha, upstream musí:

- spomaliť,
- odmietnuť request,
- bufferovať s limitom,
- degradovať funkcionalitu,
- prioritizovať traffic.

Bez backpressure sa overload presunie do memory, queues, connection pools alebo databases a spôsobí kaskádové zlyhanie.

## 12. Load balancing

Load balancer distribuuje traffic medzi healthy targets.

Over:

- algorithm,
- health check,
- zonal distribution,
- connection reuse,
- sticky sessions,
- TLS termination,
- capacity a quotas,
- fail-open/fail-closed behavior.

Load balancing nevyrieši shared bottleneck za targets.

## 13. Fault tolerance

Fault-tolerant systém pokračuje vo funkcii pri zlyhaní komponentu s minimálnym alebo žiadnym prerušením.

Mechanizmy:

- redundancy,
- replication,
- quorum,
- automatic failover,
- retry s idempotenciou,
- timeout a circuit breaker,
- isolation,
- graceful degradation,
- self-healing.

Fault tolerance má cenu v kapacite, complexity, consistency a testingu.

## 14. Redundancy

Redundantný komponent pomáha iba vtedy, keď nemá rovnaký failure mode.

Slabé príklady:

- dve instances na jednom hoste/AZ,
- dva links cez rovnaký router,
- replicas s rovnakou chybnou konfiguráciou,
- primary a backup v jednom account-e s rovnakým admin accessom,
- viac copies poškodených rovnakou logical corruption.

Hľadaj nezávislosť failure domains.

## 15. Active-active a active-passive

### Active-active

Viac components súčasne spracúva traffic.

Výhody:

- využitá redundantná kapacita,
- rýchlejší failover,
- lepšie scale.

Riziká:

- consistency,
- conflict resolution,
- shared dependencies,
- split brain.

### Active-passive

Standby čaká na failover.

Výhody:

- jednoduchší write ownership,
- menšia conflict complexity.

Riziká:

- standby drift,
- failover latency,
- neoverená capacity,
- nevyužitý cost.

## 16. Retry

Retry je vhodný iba pre transient failure.

Použi:

- timeout,
- exponential backoff,
- jitter,
- maximum attempts,
- idempotency token,
- retry budget.

Neobmedzené retry zosilňuje incident a môže vytvoriť retry storm.

## 17. Circuit breaker

Circuit breaker dočasne zastaví calls na zlyhávajúcu dependency.

Stavy:

- closed — requests prechádzajú,
- open — requests sa rýchlo odmietajú,
- half-open — limitované test requests.

Chráni threads, connections a downstream, ale potrebuje fallback alebo explicitný error model.

## 18. Bulkhead isolation

Bulkhead oddeľuje resource pools:

- thread pools,
- queues,
- tenants,
- cells,
- accounts,
- Regions,
- rate limits.

Failure jednej skupiny potom nevyčerpá všetky resources.

## 19. Graceful degradation

Pri failure môže systém zachovať kritickú funkciu a vypnúť menej dôležitú:

- read-only mode,
- cached data,
- delayed processing,
- bez recommendations,
- nižšia kvalita media,
- obmedzené admin operácie.

Degradation musí byť zámerná, pozorovateľná a bezpečná.

## 20. Capacity headroom

Fault tolerance potrebuje rezervu.

Príklad dvoch AZ:

```text
normal: každá AZ 50 % loadu
failure jednej AZ: druhá musí zvládnuť 100 %
```

Ak obe AZ bežia na 80–90 %, zonal failure spôsobí overload. Autoscaling nemusí reagovať dostatočne rýchlo alebo nemusí mať capacity.

## 21. Quotas

Cloud resource quotas môžu blokovať scale-out:

- instance count,
- vCPU,
- IP addresses,
- load balancer targets,
- API rate,
- database connections,
- storage throughput.

Quota monitoring je súčasť capacity managementu. Zvýšenie quota nezaručuje physical capacity.

## 22. Cost a elasticity

Elasticity môže znižovať idle cost, ale môže aj zvýšiť spend:

- nesprávna metric,
- runaway queue,
- attack traffic,
- scaling loop,
- expensive instance selection,
- cross-AZ/data transfer,
- minimum capacity príliš vysoká.

Použi budgets, anomaly detection, max capacity a business-aware guardrails.

## 23. Scalability testing

Testuj:

- steady-state load,
- sudden burst,
- gradual ramp,
- sustained peak,
- downstream slowdown,
- scale-out latency,
- scale-in behavior,
- single-AZ failure pri peak-u,
- quota/capacity exhaustion.

Meraj:

- latency percentiles,
- throughput,
- errors,
- saturation,
- queue age,
- scaling events,
- cost per transaction.

## 24. Fault injection

Bezpečný resilience test:

1. definuj steady state,
2. vyber jednu fault hypothesis,
3. obmedz blast radius,
4. nastav abort conditions,
5. zachovaj observability,
6. vykonaj fault,
7. over recovery,
8. odstráň root weakness.

Chaos bez hypotézy je iba nekontrolovaný incident.

## 25. Anti-patterny

### Auto Scaling = fault tolerance

Ak všetky instances závisia od jednej databázy alebo AZ, nejde o fault tolerance.

### Viac replicas = lineárny scale

Shared locks, partitions a downstream limity môžu throughput zastaviť.

### Retry bez limitu

Zosilňuje failure.

### Scale-to-zero pre latency-critical službu bez cold-start budgetu

Prvý request môže porušiť SLO.

### Maximálna utilization ako cost optimalizácia

Odstraňuje headroom pre failure a burst.

## 26. Troubleshooting

### Auto Scaling nepridáva capacity

Over metric, policy, cooldown, max capacity, quota, launch failure, subnet IP a instance capacity.

### Capacity rastie, latency nie

Hľadaj downstream bottleneck, lock, connection pool, serialization alebo load-balancer imbalance.

### Scale-in spôsobuje errors

Over draining, shutdown grace, in-flight work a session affinity.

### Jedna AZ zlyhá a druhá sa preťaží

Over baseline headroom, failover speed, cross-zone routing a quota.

### Retry storm

Over client retry policies, timeout hierarchy, jitter a dependency recovery.

## 27. Kontrolné otázky

1. Aký je rozdiel medzi scalability a elasticity?
2. Kedy je vhodné vertical a horizontal scaling?
3. Prečo CPU nemusí byť správny scaling signal?
4. Prečo je scale-in rizikovejší než scale-out?
5. Čo odlišuje redundancy od fault tolerance?
6. Aký je rozdiel medzi active-active a active-passive?
7. Prečo retry potrebuje idempotenciu, backoff a jitter?
8. Ako bulkhead znižuje blast radius?
9. Prečo Multi-AZ potrebuje capacity headroom?
10. Ako quota obmedzuje elasticitu?

## Glossary impact

Relevantné pojmy: scalability, vertical scaling, horizontal scaling, diagonal scaling, elasticity, reactive scaling, predictive scaling, scale-in, backpressure, load leveling, fault tolerance, redundancy, active-active, active-passive, retry budget, circuit breaker, bulkhead, graceful degradation a capacity headroom.

## Oficiálna dokumentácia

- [Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
- [AWS fault isolation boundaries](https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/welcome.html)
