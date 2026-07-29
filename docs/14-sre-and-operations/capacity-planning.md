# Capacity planning

Capacity planning je proces prekladu budúceho business demandu na overenú schopnosť systému splniť reliability objectives aj počas rastu, špičiek, rolloutov, maintenance a definovaných failure scenárov. Nie je to jednorazový nákup serverov ani extrapolácia priemerného CPU.

Správna otázka nie je:

> Koľko CPU máme?

Správna otázka je:

> Koľko validných business operations dokáže konkrétna service generation dokončiť v požadovanom čase, pri ktorých constraints a failure assumptions, bez prekročenia error budgetu?

## 1. Dominantný lifecycle

```text
business forecast a reliability objective
→ exact capacity-planning subject
→ logical demand model
→ end-to-end service a resource model
→ constrained-resource a bottleneck verdict
→ degraded/failure scenario
→ required headroom a acquisition lead time
→ load/soak/failover experiment
→ provision a rollout
→ effective-capacity read-back
→ forecast-versus-actual recalibration
→ second-peak acceptance
```

Capacity plan je prijateľný až vtedy, keď je viazaný na exact workload, topology, release a SLO generation a keď experiment preukáže original aj degraded business outcome.

## 2. Exact capacity-planning subject

Capacity číslo bez subjectu je nebezpečné. Subject musí obsahovať aspoň:

```text
business capability a operation
+ valid demand population
+ tenant/Region/cohort
+ release a configuration generation
+ topology a failure domain
+ measurement window a seasonality
+ latency/completion SLO
+ dependency a quota generations
+ scaling/provisioning lead time
+ rollback a degraded-mode assumptions
```

Príklad:

```text
subject: Atlas settlement completion
Region: prod-eu1
operation: one unique settlement intent
release: settlement-api 8.1.0
window: end-of-month campaign peak, 30 min
SLO: 99.9 % complete do 10 min
failure assumption: loss jednej AZ
provider constraint: 2 100 accepted operations/s
broker generation: PAY-BROKER-23
```

Číslo `3 000 requests/s` bez unique-intent population, completion boundary a provider limitu nie je capacity contract.

## 3. Demand model

Demand model má pracovať s logical business units, nie iba technickými attempts.

Pre settlement flow treba oddeliť:

- unique settlement intents;
- HTTP attempts a client retries;
- outbox publish attempts;
- broker deliveries a redeliveries;
- provider authorization attempts;
- reconciliation reads;
- support alebo replay traffic.

Demand amplification:

```text
internal attempts / unique business operations
```

Ak 1 000 logical settlements vytvorí pri provider slowdown-e 4 600 internal attempts, kapacitu nemožno plánovať iba podľa vstupného request rate-u.

Demand model má zahrnúť:

- baseline a trend;
- dennú, týždennú a mesačnú seasonality;
- kampane, billing cycles a known launches;
- organic growth a tenant concentration;
- retry a fan-out multipliers;
- backlog recovery load;
- failover a maintenance redistribution;
- forecast uncertainty;
- business cancellation alebo degraded-mode možnosti.

Forecast je distribúcia a assumption set, nie jedno presné číslo.

## 4. Service capacity model

End-to-end capacity je limitovaná najužším required boundary:

```text
admission
→ application concurrency
→ database connection/lock/write throughput
→ outbox publisher
→ broker partitions a replication
→ consumer concurrency
→ provider quota/rate limit
→ callback/reconciliation throughput
→ final-state publication
```

Pre sériový required flow približne platí:

```text
end-to-end sustainable throughput
≈ minimum sustainable throughput required boundaries
```

Ak API prijme `3 600/s`, ale provider a settlement workers bezpečne dokončia `1 850/s`, service nemá completion capacity `3 600/s`. Rozdiel sa materializuje ako queue age, timeouty, retries alebo data-loss risk.

## 5. Effective capacity

Configured capacity nie je effective capacity.

```text
installed capacity
− unavailable members
− reservations a system overhead
− topology constraints
− safe utilization margin
− rollout/failover requirements
− dependency a quota limits
= effective capacity pre subject
```

Príklady rozdielov:

- 300 worker replicas existuje, ale DB pool povoľuje iba 1 200 concurrent sessions;
- broker má 48 partitions, no tenant key skew koncentruje 44 % loadu na štyri partitions;
- provider deklaruje 2 500/s, ale current contract alebo fraud tier povoľuje 2 100/s;
- cluster má voľné CPU, ale subnet nemá IPs pre scale-out;
- autoscaler pridá Pody za 30 sekúnd, no Node provisioning trvá 12 minút;
- jedna AZ nesie 45 % active capacity, takže jej strata prekročí remaining headroom.

Capacity plan musí pomenovať observation point pre každú z týchto hraníc.

## 6. Headroom

Headroom je kapacita nad očakávaným demandom určená na neistotu, burst, failure a control latency.

Nie je univerzálne percento. Musí byť odvodená z:

```text
forecast error
+ traffic burst shape
+ detection a scaling latency
+ failure-domain loss
+ rollout surge
+ queue recovery requirement
+ dependency uncertainty
+ reliability objective
```

Relevantné druhy:

- **steady-state headroom** — bežná prevádzková rezerva;
- **burst headroom** — krátka špička pred autoscalingom;
- **failover headroom** — remaining capacity po strate definovaného failure domainu;
- **recovery headroom** — schopnosť spracovať live traffic aj backlog;
- **rollout headroom** — surge a mixed-generation overhead;
- **quota headroom** — rezerva vo provider alebo platform limits.

Headroom bez failure assumption je iba dekoratívne percento.

## 7. Capacity, latency a queueing

Utilization blízko 100 % typicky spôsobuje nelineárny rast queueing latency. Systém preto nemožno plánovať na teoretický maximálny throughput ako na sustainable operating point.

Sleduj:

- arrival rate;
- service rate;
- concurrency;
- queue depth a age;
- service-time distribúciu;
- timeout a retry behavior;
- utilization voči effective capacity;
- drain rate po skončení špičky.

Stabilná queue vyžaduje v relevantnom intervale service rate vyšší než arrival rate. Krátky burst môže byť prijateľný iba ak queue age zostane v SLO a existuje preukázaný drain plan.

## 8. Scaling time a acquisition lead time

Capacity musí byť dostupná pred demand eventom.

Lifecycle môže obsahovať:

```text
forecast detection
→ budget/approval
→ cloud quota alebo hardware acquisition
→ subnet/storage/network preparation
→ deployment
→ warmup a cache fill
→ load test
→ production activation
```

Autoscaling nerieši:

- provider quota, ktorú nemožno dynamicky navýšiť;
- DB schema alebo index bottleneck;
- partition count s rizikovou online migráciou;
- regional capacity shortage;
- cold data alebo cache warmup;
- people a operational support capacity.

Lead time je súčasť capacity subjectu, nie administratívna poznámka.

## 9. Load, soak a failover experiments

Capacity model sa musí kalibrovať experimentom.

### Load test

Overuje throughput, latency a error behavior pri definovanom demand profile.

### Stress test

Hľadá saturation point, failure mode a safe overload behavior.

### Soak test

Odhaľuje leaks, compaction, queue drift, storage growth a pomalú degradáciu.

### Failover capacity test

Overuje remaining capacity po strate AZ, node poolu, broker partition cohortu alebo dependency endpointu.

### Backlog recovery test

Kombinuje live demand s kontrolovaným backlogom a meria drain bez poškodenia SLO alebo downstreamu.

Test bez production-like topology, keys, retry behavior a provider constraints nepotvrdzuje production capacity.

## 10. Overload control

Keď demand prekročí safe completion capacity, správnou reakciou nemusí byť nekonečné prijímanie práce.

Mechanizmy:

- admission control;
- per-tenant alebo per-operation rate limit;
- priority queue;
- load shedding;
- bounded queue;
- retry-after a explicitný retryable outcome;
- degraded mode;
- expensive-feature disable;
- concurrency limiter;
- circuit breaker voči downstream dependency;
- backpressure propagovaná k callerovi.

Overload policy má chrániť critical business invariant, nie iba process uptime.

## 11. Worked incident `SRE-PAY-53`

Atlas Payments pripravoval end-of-month merchant campaign. Capacity spreadsheet predpokladal peak `1 500 unique settlements/s` a 30 % rezervu. Plán však používal:

- priemerný HTTP request rate;
- API CPU ako dominantný capacity signal;
- všetky tri AZ ako súčasne dostupné;
- provider latency `180 ms`;
- retry multiplier `1.2×`;
- nulový backlog pri začiatku kampane.

Skutočný stav o `10:02 UTC`:

```text
unique demand:              2 800 settlements/s
HTTP attempts:              3 600/s
provider p95 latency:       1.9 s
internal attempt multiplier: 4.6×
safe completion capacity:   1 850 settlements/s
one-AZ-safe capacity:       1 420 settlements/s
outbox queue age:            0 → 17 min
DB pool utilization:         96 %
```

Trigger bol campaign spike kombinovaný s provider slowdown-om.

Primary root cause bol **capacity plan viazaný na front-door CPU a priemerný request rate namiesto end-to-end completion capacity, retry amplificationu a one-AZ failure modelu**.

Causal amplifiers:

- API nemala admission control podľa downstream completion capacity;
- autoscaler sledoval CPU, nie queue age, DB sessions a provider quota;
- provider retries nemali shared retry budget;
- capacity review neobsahoval second-peak ani failover test;
- acquisition lead time na provider quota nebol súčasťou launch gate-u.

## 12. Causal evidence

- API CPU zostávalo pod 55 %, takže CPU dashboard bol zelený;
- DB connection acquire p99 vzrástlo z `12 ms` na `1.4 s`;
- queue arrival rate prevyšoval drain rate o približne `950/s`;
- provider 429 a timeouty spustili ďalšie retries;
- worker scale-out zvýšil DB contention, ale nie final completion throughput;
- po obmedzení admission na `1 700/s` a zrušení duplicate retries začala queue age klesať;
- one-AZ simulation z predchádzajúceho kvartálu neexistovala;
- campaign forecast obsahoval iba point estimate bez uncertainty bandu.

Viac workerov nebolo authoritative fixom. Bottleneck sa nachádzal v spoločnom DB/provider completion path-e.

## 13. Evidence-preserving containment

```text
zastaviť discretionary changes
→ zachovať demand, queue, DB, provider a retry evidence
→ vyhlásiť incident
→ obmedziť admission a noncritical cohorts
→ zastaviť retry amplification
→ chrániť DB a broker pred collapse
→ koordinovať provider quota/latency stav
→ udržať reconciliation a audit paths
```

Containment nesmie broad-delete queue ani meniť idempotency keys.

## 14. Authoritative recovery

1. zaviesť admission limit `1 700 unique intents/s` s `Retry-After`;
2. vypnúť nebounded client/provider retries a použiť shared retry budget;
3. rozdeliť critical settlement traffic od reporting/reconciliation batch práce;
4. obnoviť DB pool pod safe saturation threshold;
5. drainovať backlog bounded concurrency podľa provider acceptance;
6. reconciliovať payment, outbox, broker a provider ledger;
7. navýšiť provider quota až po potvrdení contractu;
8. vytvoriť nový model `CAP-PAY-53-B` s failure a uncertainty assumptions;
9. vykonať load, backlog-recovery a one-AZ test;
10. overiť druhý campaign peak bez manual override-u.

## 15. Capacity acceptance verdict

Plan je prijatý, keď:

- exact business operation a SLO sú definované;
- demand používa logical units a explicitný amplification model;
- všetky required boundaries majú effective capacity a ownera;
- bottleneck je experimentálne potvrdený;
- forecast obsahuje seasonality, launches a uncertainty;
- headroom je odvodená z konkrétnych failure a scaling assumptions;
- acquisition/provisioning lead time spĺňa launch termín;
- overload behavior je bounded a user-visible;
- load, soak, failover a backlog-recovery testy prešli;
- production read-back zodpovedá modelu;
- second peak a one-failure-domain outcome spĺňajú SLO;
- forecast-versus-actual variance aktualizuje ďalšiu generation.

## 16. Troubleshooting flow

```text
user latency alebo completion impact
→ exact operation/cohort/release/window
→ logical demand a amplification
→ queue arrival/service/drain rates
→ end-to-end required boundaries
→ effective capacity a saturation
→ dependency quotas/latency
→ scaling a provisioning lag
→ overload controls
→ current bottleneck hypothesis
→ bounded intervention
→ business completion a second-peak verification
```

CPU pod 60 % nevyvracia capacity incident. Môže znamenať čakanie na DB, lock, provider, partition alebo quota.

## 17. Earlier controls

- demand taxonomy a unique-operation IDs;
- forecast s uncertainty bands;
- per-boundary capacity owner;
- failover a recovery headroom;
- provider quota calendar;
- queue-age a drain-rate SLIs;
- retry budget;
- admission control a load shedding;
- production-shaped load tests;
- acquisition lead-time gate;
- forecast-versus-actual review;
- second-peak a one-AZ rehearsal.

## 18. Anti-patterny

### Priemerné CPU je capacity plan

Skryje queue, lock, network, storage, quota a dependency boundaries.

### Autoscaling vyrieši každý peak

Scaling môže byť pomalšie než failure a môže zosilniť spoločný bottleneck.

### Maximum benchmark throughput je safe capacity

Neobsahuje latency tail, failure reserve, recovery ani sustainable operating point.

### Headroom je vždy 30 %

Rezerva bez odvodenia z konkrétneho failure modelu nemá technický význam.

### Queue znamená, že nič nestratíme

Unbounded queue môže prekročiť completion SLO, retention alebo recovery capacity.

### Viac retries zvyšuje reliability

Pri overload-e retries zvyšujú demand a môžu znížiť completion rate.

## 19. Kontrolné otázky

1. Čo tvorí exact capacity-planning subject?
2. Prečo logical demand nie je HTTP request count?
3. Ako sa configured a effective capacity líšia?
4. Ako určiť constrained resource?
5. Čo musí obsahovať demand amplification model?
6. Ako sa steady-state, failover a recovery headroom líšia?
7. Prečo vysoká utilization nelineárne zvyšuje latency?
8. Kedy autoscaling nestačí?
9. Ako acquisition lead time ovplyvňuje launch gate?
10. Čo musí overiť backlog-recovery test?
11. Prečo viac workerov zhoršilo `SRE-PAY-53`?
12. Čo musí obsahovať capacity acceptance verdict?

## Glossary impact

Relevantné pojmy: capacity-planning subject, logical demand unit, demand amplification, service capacity model, constrained resource, effective capacity, steady-state headroom, failover headroom, recovery headroom, acquisition lead time, queue drain rate, overload contract, capacity acceptance verdict a second-peak validation.

## Primárne zdroje

- [Google SRE — Software Engineering in SRE](https://sre.google/sre-book/software-engineering-in-sre/)
- [Google SRE — Handling Overload](https://sre.google/sre-book/handling-overload/)
- [Google SRE Workbook — Managing Load](https://sre.google/workbook/managing-load/)
- [Google SRE — Operational Overload](https://sre.google/sre-book/operational-overload/)
- [Google SRE — Service Best Practices](https://sre.google/sre-book/service-best-practices/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Toil](toil.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Incident management →](incident-management.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
