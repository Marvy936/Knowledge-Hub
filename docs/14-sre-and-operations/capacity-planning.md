# Capacity planning

Capacity planning je nepretržitý proces, ktorým sa budúci business demand prekladá na overenú schopnosť služby splniť reliability objectives počas bežnej prevádzky, špičky, rollout-u, maintenance aj definovaného failure scenára. Nie je to jednorazový nákup infraštruktúry ani extrapolácia priemerného CPU. Kapacita je vlastnosť konkrétnej business operation, release, topology, dependency contractu a časového horizontu.

Správna otázka preto neznie „koľko CPU máme?“, ale „koľko validných business operations dokáže táto service generation dokončiť v požadovanom čase, pri akých constraints a failure assumptions, bez prekročenia error budgetu?“. Atlas Payments používa settlement journey, v ktorej front door prijme unique intent, databáza uchová payment a outbox, broker prenesie command, worker vykoná provider operation a reconciler potvrdí final outcome.

## 1. Dominantný demand-to-capacity lifecycle

Capacity plan vzniká z business intentu a reliability objective, nie z resource grafu. Najprv sa určí presný demand subject, potom sa modelujú všetky required boundaries, bottleneck, failure capacity a lead time. Experiment následne overí, či model zodpovedá skutočnému runtime správaniu.

```text
business forecast a reliability objective
→ exact capacity subject a logical demand unit
→ demand distribution, seasonality a amplification
→ end-to-end required boundaries
→ effective capacity a constrained resource
→ failure-domain loss, headroom a lead time
→ load, soak, failover a backlog experiment
→ overload a degraded-service contract
→ provision a production read-back
→ forecast-versus-actual recalibration
→ second-peak a second-failure validation
```

Každý krok mení inú časť rozhodnutia. Forecast opisuje očakávaný demand, capacity model opisuje limity systému, allocation a provisioning vytvárajú resources a overload contract určuje správanie po prekročení bezpečnej hranice. Zelený provisioning result ešte nepreukazuje effective business capacity.

## 2. Exact capacity subject

Číslo bez subjectu nemožno bezpečne porovnať ani použiť ako launch gate. Exact subject zachováva business capability, logical operation, tenant alebo Region cohort, release a configuration generation, topology, measurement window, SLO, dependency quotas, failure assumption, scaling lead time a degraded-mode contract.

```text
subject: CAP-PAY-53-B
capability: settlement completion
operation: one unique acknowledged settlement intent
Region: prod-eu1
release: settlement-api 8.1.0
window: end-of-month peak, 30 minút
SLO: 99.9 % complete exactly once do 10 minút
topology: three AZ, N-1 required
provider contract: 2 100 accepted operations/s
broker generation: PAY-BROKER-23
recovery requirement: live traffic + bounded backlog drain
```

`3 000 requests/s` bez unique-operation population, completion boundary a provider limitu nie je capacity contract. Pri zmene release-u, partitioning keyu, DB poolu, provider tieru alebo retry policy vzniká nová generation, pretože rovnaký hardware môže mať inú effective capacity.

## 3. Logical demand a amplification

Demand sa musí merať v jednotke, ktorú rozpoznáva business outcome. Jedna unique settlement operation môže vytvoriť viac HTTP attempts, outbox publish attempts, broker redeliveries, provider calls a reconciliation reads. Technický attempt count preto nie je totožný s customer demandom.

```text
unique business operations
× client retry multiplier
× internal fan-out
× broker redelivery multiplier
× provider retry multiplier
+ backlog recovery traffic
= effective internal demand
```

Demand amplification je pomer internal attempts k unique business operations. Ak `1 000` logical settlements počas provider slowdown-u vytvorí `4 600` internal attempts, plan založený iba na vstupnom request rate-e podhodnotí DB, broker aj provider load. Model musí zachytiť baseline, trend, daily/monthly seasonality, kampane, tenant concentration, retry a fan-out, maintenance redistribution, failover, backlog recovery a forecast uncertainty.

Forecast preto nie je jedno presné číslo. Je to distribution a assumption set s low/expected/high scenármi, confidence a triggerom na recalibration. Point estimate bez uncertainty sa ľahko zmení na falošnú garanciu.

## 4. End-to-end capacity a constrained resource

Required business flow je obmedzený najužšou boundary, nie komponentom s najvyšším CPU. Pre Atlas settlement completion treba sledovať admission, application concurrency, DB connections/locks/write throughput, outbox publisher, broker partitions, consumer concurrency, provider quota a callback/reconciliation throughput.

```text
sustainable end-to-end completion capacity
≈ minimum sustainable capacity všetkých required boundaries
```

Ak API prijme `3 600/s`, ale DB/provider path bezpečne dokončí iba `1 850/s`, completion capacity nie je `3 600/s`. Rozdiel sa materializuje ako queue age, timeout, retry amplification, retention pressure alebo data-integrity risk. Pridanie workerov môže dokonca znížiť throughput, ak zvýši lock alebo connection contention na spoločnej boundary.

Bottleneck verdict má vychádzať z experimentu a observation points. CPU, queue arrival/service rate, DB acquire latency, lock waits, provider 429, partition skew a final completion rate spoločne odlíšia application shortage od downstream constraintu.

## 5. Configured, installed a effective capacity

Configured replicas alebo quota hovoria, čo bolo požadované. Installed capacity opisuje, čo fyzicky existuje. Effective capacity odpočítava unavailable members, reservations, topology constraints, safe utilization margin, rollout/failover requirement, quotas a shared bottlenecks.

```text
installed capacity
− unavailable alebo draining members
− system overhead a reservations
− topology/placement constraints
− safe latency margin
− rollout a failover reserve
− dependency a quota limits
= effective capacity pre exact subject
```

Príkladom je 300 worker replicas obmedzených DB poolom na 1 200 concurrent sessions, 48 broker partitions so 44 % loadu na štyroch hot partitions alebo cluster s voľným CPU, ale bez subnet IPs pre nové Pody. Každá boundary potrebuje ownera, observation point a explicitnú current generation.

## 6. Headroom, failure capacity a acquisition lead time

Headroom nie je univerzálnych 30 %. Je to rezerva odvodená z forecast erroru, burst shape-u, detection a scaling latency, failure-domain lossu, rollout surge-u, backlog recovery, dependency uncertainty a požadovaného SLO.

Rozlišujú sa steady-state, burst, failover, recovery, rollout a quota headroom. Jedna hodnota ich nesmie zastupovať všetky. Služba môže mať dostatočnú steady-state rezervu a súčasne nemať kapacitu po strate AZ alebo na drain backlogu popri live trafficu.

Capacity musí byť dostupná pred demand eventom. Provider quota, DB partitioning, subnet expansion, storage throughput alebo regional cloud allocation môžu mať lead time dlhší než autoscaling response. Launch gate preto pracuje spätne od eventu:

```text
required activation date
← production validation a warm-up
← provisioning a rollout
← quota/network/storage preparation
← approval alebo contract change
← forecast confidence deadline
```

Autoscaler nevyrieši bottleneck, ktorý nie je škálovateľný alebo sa škáluje pomalšie než rast impactu.

## 7. Queueing, saturation a overload contract

Utilization blízko 100 % typicky spôsobuje nelineárny rast queueing latency. Maximum benchmark throughput preto nie je bezpečný operating point. Relevantné sú arrival rate, service rate, concurrency, service-time distribution, queue age, retry behavior, utilization voči effective capacity a drain rate po skončení peaku.

Stabilná queue vyžaduje, aby service rate v relevantnom intervale prevyšoval arrival rate. Krátky burst môže byť prijateľný, iba ak queue age zostane v SLO a existuje preukázaný drain plan. Unbounded queue iba odkladá failure a môže prekročiť retention, recovery alebo customer deadline.

Overload contract určuje, čo sa stane po prekročení safe completion capacity. Môže použiť admission control, per-tenant priority, bounded queue, `Retry-After`, load shedding, concurrency limit, degraded mode alebo circuit breaker. Cieľom nie je udržať process uptime za každú cenu, ale chrániť critical business invariant a pravdivo komunikovať odmietnutý alebo oneskorený outcome.

## 8. Experimentálny dôkaz

Capacity model sa kalibruje kombináciou experimentov. Load test overuje definovaný demand profile, stress test hľadá saturation a overload behavior, soak test odhaľuje leaks a pomalý drift, failover test odoberie failure domain a backlog-recovery test kombinuje live traffic s nahromadenou prácou.

Experiment musí zodpovedať production topology, keys, data distribution, retries, provider quotas a release generation. Test s rovnomernými keys môže prehliadnuť partition skew; test bez provider throttlingu neoverí retry amplification; failover bez live backlogu neoverí recovery headroom.

Výsledkom nemá byť iba maximum requests/s. Potrebný je operating envelope:

```text
safe logical throughput
+ latency/completion distribution
+ saturation boundary
+ overload behavior
+ failure-domain capacity
+ backlog drain capability
+ confidence a assumptions
```

## 9. Connected incident `SRE-PAY-53`

Atlas pripravoval end-of-month campaign. Spreadsheet predpokladal peak `1 500 unique settlements/s` a 30 % rezervu, ale používal priemerný HTTP rate, API CPU, všetky tri AZ dostupné, provider latency `180 ms`, retry multiplier `1.2×` a nulový počiatočný backlog.

Skutočný stav o `10:02 UTC` bol:

```text
unique demand:                2 800 settlements/s
HTTP attempts:                3 600/s
provider p95 latency:         1.9 s
internal attempt multiplier:  4.6×
safe completion capacity:     1 850 settlements/s
one-AZ-safe capacity:         1 420 settlements/s
outbox queue age:              0 → 17 min
DB pool utilization:          96 %
```

Triggerom bol campaign spike spolu s provider slowdown-om. Root cause bol capacity plan viazaný na front-door CPU a priemerný request rate namiesto end-to-end completion capacity, retry amplificationu a one-AZ failure modelu. API nemala admission control podľa downstream capacity, autoscaler sledoval CPU, provider retries nemali shared budget a provider quota lead time nebol launch gate.

CPU zostávalo pod 55 %, no DB acquire p99 vzrástlo z `12 ms` na `1.4 s`, arrival rate prevyšoval drain rate približne o `950/s` a worker scale-out zvýšil contention bez rastu final completion. Po admission limite `1 700 unique intents/s` a odstránení duplicate retries začala queue age klesať. Tento dôkaz vyvrátil hypotézu, že riešením je viac application replicas.

## 10. Containment, recovery a recalibration

Containment najprv zastavilo discretionary changes, zachovalo demand/queue/DB/provider/retry evidence, obmedzilo admission a noncritical cohorts, zastavilo retry amplification a chránilo DB, broker a reconciliation paths. Queue sa nesmela broad-delete-nuť ani replayovať bez idempotency a provider evidence.

Recovery zaviedla limit `1 700/s` s `Retry-After`, shared retry budget, separáciu critical trafficu od batch práce, bounded backlog drain podľa provider acceptance a reconciliation payment–outbox–broker–provider. Provider quota sa menila až po potvrdení contractu.

Nová generation `CAP-PAY-53-B` obsahuje uncertainty, one-AZ model, acquisition lead time a experimentálny dôkaz. Recovery sa uzavrela až po load, backlog-recovery a one-AZ teste a po druhom campaign peaku bez manuálneho override-u. Forecast-versus-actual delta následne upravila ďalší model namiesto spätnej úpravy pôvodných assumptions.

## 11. Capacity acceptance contract

Positive acceptance musí preukázať, že expected demand aj high scenario sa dokončia v SLO pri current release a topology. Failover path musí preukázať N-1 capacity a backlog-recovery path súbežné spracovanie live trafficu a queue. Production read-back musí potvrdiť, že provisioned resources, quotas a placement zodpovedajú plánu.

Forbidden paths musia byť explicitne odmietnuté. Systém nesmie prijímať unbounded work nad downstream capacity, retries nesmú zvyšovať total demand bez budgetu, scale-out nesmie prekročiť DB/provider guardrail, hot tenant nesmie zostať skrytý v aggregate a jedna AZ strata nesmie zmeniť pravdivé odmietnutie na silent queue growth.

```text
positive:
expected/high demand → bounded latency → SLO completion

failure:
loss jednej AZ → remaining capacity + controlled degradation

recovery:
live traffic + backlog → stable drain bez secondary overloadu

forbidden:
front-door green while completion collapses
unbounded retry amplification
queue growth bez customer-visible contractu
point forecast bez uncertainty
capacity claim bez experimentu
```

Verdict patrí exact demand, release, topology, dependency quota a experiment generation. Druhý peak a adjacent tenant cohort overujú, že model nebol fitnutý iba na pôvodný incident.

## 12. Troubleshooting capacity failure-u

Pri user latency alebo completion impacte začni logical operation a affected cohortom. Porovnaj unique demand s internal amplificationom, queue arrival/service/drain rates a effective capacity jednotlivých boundaries. Potom zohľadni dependency quota, scaling lag a aktuálne overload controls.

```text
user/business impact
→ exact operation/cohort/release/window
→ unique demand a amplification
→ queue arrival, service a drain
→ required boundaries a saturation
→ current constrained resource
→ failure/headroom assumptions
→ bounded intervention
→ business completion read-back
→ second-peak validation
```

CPU pod 60 % capacity incident nevylučuje. Môže iba dokazovať, že bottleneck leží v DB, locku, providerovi, partitioning-u, storage alebo quota.

## 13. Anti-patterny

Tieto anti-patterny zamieňajú jednoduchý resource signal za end-to-end completion contract. Každý z nich odstráni failure, queue alebo dependency boundary z modelu a vytvorí príliš optimistický launch verdict.

- **Priemerné CPU je capacity plan —** skryje queue, lock, storage, partition, quota a provider constraints. CPU je observation jedného resource-u, nie business capacity.
- **Autoscaling vyrieši každý peak —** scaling môže prísť neskoro alebo zosilniť shared bottleneck. Potrebuje lead-time a downstream guardrails.
- **Maximum benchmark throughput je safe capacity —** maximum neobsahuje latency tail, failure reserve, sustainable operating point ani recovery headroom.
- **Headroom je vždy 30 % —** rezerva bez konkrétneho burst, failure a scaling modelu nemá technickú semantics.
- **Queue znamená, že nič nestratíme —** unbounded queue môže porušiť completion SLO, retention a recovery capacity aj bez okamžitého dropu.
- **Viac retries zvyšuje reliability —** počas overload-u retries zvyšujú demand a môžu znížiť počet dokončených unique operations.

## 14. Kontrolné otázky

1. Čo tvorí exact capacity subject?
2. Prečo logical demand nie je HTTP request count?
3. Ako demand amplification mení resource model?
4. Ako sa configured, installed a effective capacity líšia?
5. Ako sa určí constrained resource?
6. Prečo headroom potrebuje failure a scaling assumptions?
7. Ako acquisition lead time ovplyvňuje launch gate?
8. Prečo maximum throughput nie je sustainable capacity?
9. Čo musí overiť backlog-recovery test?
10. Prečo viac workerov zhoršilo `SRE-PAY-53`?
11. Aké positive, failure, recovery a forbidden paths patria do acceptance?
12. Prečo je potrebný second-peak test?

## Glossary impact

Relevantné pojmy: capacity subject, logical demand unit, demand amplification, constrained resource, effective capacity, steady-state/burst/failover/recovery headroom, acquisition lead time, operating envelope, overload contract, capacity acceptance contract a second-peak validation.

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
