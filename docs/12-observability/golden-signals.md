# Golden Signals

Google SRE používa štyri Golden Signals pre user-facing systémy: **Latency**, **Traffic**, **Errors** a **Saturation**. Ich hodnota nevzniká tým, že dashboard obsahuje štyri panely. Vzniká až vtedy, keď všetky štyri signals opisujú rovnaký exact user alebo caller outcome, správnu measurement boundary a relevantnú capacity risk.

Golden Signals spájajú dve perspektívy:

```text
čo práve zažíva caller?
+
ako blízko je systém k mechanizmu, ktorý tento outcome poškodí?
```

## 1. Dominantný lifecycle

```text
business capability a caller outcome
→ exact workflow/operation/cohort subject
→ valid demand population
→ latency boundary a distribution
→ traffic demand unit
→ error numerator a success semantics
→ saturation resource a effective capacity
→ bounded breakdowns a change context
→ SLI/error-budget alebo operational verdict
→ alert/investigation
→ dependency a USE localization
→ containment/recovery
→ original, forbidden a capacity validation
```

Golden Signals sú konzistentné iba vtedy, keď sa neporovnáva server-handler latency s end-to-end business errors, interné retry attempts s user demandom a host CPU s task-local pool saturation.

## 2. Exact Golden-Signal subject

Pre Atlas Payments používame:

```text
Golden-Signal subject: GS-PAY-44
business capability: CAP-PAY-42
observability subject: OBS-PAY-44
workflow: enterprise final settlement
release: payments-api 7.20.0
account/Region: 100000000042 / eu-central-1
cohort: enterprise merchants v eu-central-1b
window: 2026-07-29T08:10Z–08:35Z
valid operation: settlement s accepted idempotency key a valid provider route
success: exactly one provider outcome reconciled a ledger marked settled
latency boundary: accepted business command → final reconciled outcome
traffic unit: logical settlement, nie provider attempt
critical saturation resource: per-task provider connection pool
```

Bez subjectu môže mať každý panel inú population. Taký dashboard vytvára štyri čísla, nie service-health contract.

## 3. Latency

Latency je čas od definovaného začiatku po definovaný outcome.

Možné boundaries:

- client-observed request;
- edge alebo load-balancer request;
- server handler;
- queue wait;
- dependency call;
- end-to-end async workflow;
- final business completion.

Tieto hodnoty nie sú zameniteľné.

```text
HTTP handler skončí po prijatí commandu
→ 202 môže prísť za 80 ms
→ message čaká v queue a provider poole
→ final settlement skončí o 5 sekúnd neskôr
```

Server latency je pravdivá pre acceptance boundary, ale nepreukazuje final outcome latency.

### Distribution a successful/failed separation

Average maskuje tail a multimodálne populations. Sledujú sa:

- histogram alebo distribution;
- p50 pre typický priebeh;
- p95/p99 alebo threshold compliance pre tail;
- successful latency;
- failed, timeout a cancelled latency;
- degraded/fallback latency.

Fast failure môže znížiť combined average. Preto sa úspešné a neúspešné operácie nemajú miešať do jedného health verdictu.

### Coordinated omission

Measurement, ktorá zaznamená iba dokončené operácie, môže vynechať interval, keď systém novú prácu neprijímal alebo ju držal mimo meranej boundary. Arrival time, queue wait, rejection a timeout musia zostať súčasťou relevantného outcome contractu.

## 4. Traffic

Traffic je demand kladený na systém v high-level workload-specific jednotke.

Príklady:

- logical requests;
- transactions;
- messages;
- queries;
- bytes;
- jobs alebo items;
- concurrent sessions;
- inference tokens.

Traffic má reprezentovať caller alebo business demand. Interné calls môžu byť useful decomposition, ale nesmú bez označenia nahradiť demand unit.

### Logical demand a amplification

```text
10 000 logical settlements
→ retries a fan-out
→ 11 800 provider attempts
```

Traffic panel založený na provider attempts ukáže `+18 %`, hoci user demand sa nezmenil. Rozdiel je retry amplification, nie growth.

Sleduj oddelene:

- external logical operations;
- internal attempts;
- attempts per logical operation;
- fan-out factor;
- redelivery alebo replay;
- success after retry a exhausted retries.

### Traffic absence

Nulový traffic nie je nulový error rate. Môže znamenať DNS, routing, target registration, client release alebo telemetry failure. Expected demand, upstream telemetry a black-box probes rozhodujú, či ide o incident alebo sezónnosť.

## 5. Errors

Error je validná operácia, ktorá nesplnila caller alebo business contract.

Môže ísť o:

- explicitnú failure response;
- timeout alebo cancellation;
- invalid alebo incomplete result;
- dropped message;
- retry exhaustion;
- policy/quota rejection;
- stale alebo degraded response;
- partial workflow;
- unknown external side-effect outcome;
- `2xx` alebo `202`, po ktorom final business outcome nevznikne.

Error ratio:

```text
failed valid operations
───────────────────────
all valid operations
```

Numerator a denominator musia mať rovnakú operation, cohort, time a retry semantics.

### Silent errors

Silent failure nemusí emitovať `5xx`. Príklady:

- `200` s nesprávnym obsahom;
- accepted async command bez completion;
- stale tenant data;
- backup bez usable restore;
- duplicate provider authorization pri nejasnom acknowledgement;
- job, ktorý technicky skončil, ale nepublikoval výstup.

Preto Golden Signals často potrebujú semantic alebo end-to-end outcome counter, nie iba transport status.

## 6. Saturation

Saturation vyjadruje, koľko práce čaká alebo ako blízko je kritický resource k effective capacity cliffu.

Relevantné signals:

- queue length, lag alebo oldest age;
- connection-pool waiters a acquire latency;
- worker/thread queue;
- CPU run queue alebo throttling;
- memory pressure a allocation stalls;
- disk/network queues a drops;
- in-flight requests voči limitu;
- concurrency, quota alebo partition headroom;
- available IP, descriptor alebo token capacity.

Saturation je leading indicator. Latency a errors môžu byť zatiaľ v objective, ale rast queue ukazuje, že ďalší demand alebo failure jednej AZ spôsobí capacity cliff.

### Saturation nie je utilization

CPU 90 % bez queueing a SLO impactu môže byť zdravé. CPU 37 % môže sprevádzať kritickú connection-pool saturation.

```text
current use / nominálny limit
```

nie je dostatočný denominator, ak loaded runtime limit, failover capacity alebo tenant quota je nižšia. Saturation musí používať effective capacity a wait/rejection evidence.

## 7. Measurement layers

Golden Signals možno merať na viacerých vrstvách:

```text
client
→ DNS/TLS/edge
→ load balancer
→ application acceptance
→ queue/workflow
→ dependency
→ final business outcome
```

Rozdiel medzi vrstvami je evidence:

- client latency vysoká, handler latency nízka → edge, queue alebo network wait;
- acceptance success vysoký, final completion nízky → async/downstream failure;
- dependency attempts rastú, logical traffic stabilný → retry amplification;
- resource saturation rastie len v jednej AZ → cohort alebo placement boundary.

Jedna vrstva nemá byť implicitne prezentovaná ako end-to-end truth.

## 8. Golden Signals pre rôzne workloads

### HTTP alebo gRPC API

- Latency: valid request duration distribution;
- Traffic: logical calls/s;
- Errors: caller-visible failure ratio;
- Saturation: in-flight requests, worker/pool waits, throttling.

### Queue consumer

- Latency: message age + processing + final completion;
- Traffic: logical messages produced/settled;
- Errors: failed, expired alebo dead-letter outcomes;
- Saturation: backlog, oldest age, busy workers a downstream pools.

### Batch pipeline

- Latency: job duration a output freshness;
- Traffic: jobs/items per schedule window;
- Errors: failed alebo partial output;
- Saturation: backlog, parallel slots a missed completion window.

### Database

- Latency: transaction/query distribution;
- Traffic: logical transactions/s;
- Errors: abort, timeout, conflict alebo wrong-result semantics;
- Saturation: connections, locks, CPU/I/O queues a replica lag.

## 9. Golden Signals, RED, USE a SLO

```text
Golden Signals
→ user outcome + capacity risk
RED
→ operation-level Rate, Errors a Duration
traces/dependency RED
→ component path
USE
→ resource utilization, saturation a errors
logs/profile/config evidence
→ mechanism
```

Golden Signals poskytujú SLI candidates, ale dashboard nie je automaticky SLO.

SLO contract musí určiť:

- valid population;
- success a degraded semantics;
- latency threshold a measurement point;
- time window;
- retry/partial/unknown outcomes;
- exclusions a ownera.

Saturation je typicky leading operational signal, nie priamo user-outcome SLI. Chráni error budget pred capacity cliffom.

## 10. Worked failure: štyri green panely, chybný service verdict

### Pôvodný dashboard

Po release `7.20.0` ukazuje dashboard:

```text
Latency: HTTP handler p95 = 82 ms
Traffic: provider attempts +31 %
Errors: HTTP 5xx = 0.3 %
Saturation: task CPU = 37 %
```

Tím usúdi, že služba je zdravá a traffic rastie.

### Business evidence

```text
enterprise final-settlement p95 = 5.2 s
final settlement failures/unknown outcomes = 7.4 %
logical settlement traffic = stabilný
provider attempts per operation = 1.31
provider pool active = 8/8
pool acquire p95 = 2.7 s
pool waiters = 180–420 per task
```

Každý pôvodný panel meral inú alebo neúplnú boundary:

- latency končila pri HTTP acceptance, nie final outcome;
- traffic meral attempts, nie logical demand;
- errors počítali transport `5xx`, nie business completion;
- saturation používala CPU, hoci critical resource bol connection pool.

### Competing hypotheses

1. reálny user traffic vzrástol;
2. provider je pomalší pre všetky cohorts;
3. HTTP handler alebo task CPU je bottleneck;
4. final workflow čaká v queue;
5. provider connection pool má nižší effective limit;
6. telemetry alebo query používa nesprávnu release/AZ population.

### Causal explanation

Loaded runtime použil default pool limit `8` namiesto deklarovaných `64`. Worker concurrency zostala `32`.

```text
logical demand stabilný
→ pool capacity klesne na 8 connections/task
→ acquire wait rastie
→ end-to-end latency prekročí caller timeout
→ retries pridajú attempts
→ attempt traffic vyzerá ako growth
→ fast acceptance a nízky CPU zostávajú green
→ final errors a error-budget burn rastú
```

### Containment a recovery

- zastaviť rollout a immediate retry amplification;
- obmedziť worker concurrency;
- zachovať logical/attempt, queue, pool, trace a loaded-config evidence;
- opraviť effective pool configuration;
- canary-nuť jeden task a jednu AZ;
- rozšíriť po potvrdení end-to-end outcome a saturation guardrailov;
- reconciliovať unknown provider outcomes.

### Golden-Signal acceptance verdict

```text
Latency
→ final successful settlement p95/p99 a threshold compliance obnovené
Traffic
→ logical demand oddelený od attempts; amplification v baseline
Errors
→ final outcome failure ratio pod SLO; unknown/duplicate outcomes absent
Saturation
→ pool waiters/acquire latency pod guardrailom aj pri failover headroome
```

Forbidden outcomes:

- žiadne duplicate authorization;
- žiadne skrytie traffic dropu ako zlepšenie;
- žiadna regresia standard cohortu alebo susednej AZ;
- žiadna telemetry no-data interpretovaná ako zero error.

## 11. Alerting a dashboard hierarchy

Service overview má viesť:

```text
SLO/error-budget a black-box outcome
→ Latency, Traffic, Errors, Saturation
→ operation/cohort/version breakdown
→ dependency RED a trace
→ USE resource evidence
→ logs/profile/config
```

Page má byť viazaná na user impact alebo rýchly SLO risk. Saturation warning môže predchádzať page, ak má jasnú action a threshold odvodený od effective capacity.

Relevantné alert patterns:

- fast a slow error-budget burn;
- final-completion latency burn;
- sustained zero completions pri očakávanom demand-e;
- queue age alebo pool wait prekračujúci business deadline;
- saturation, ktorá odstránila failover headroom.

## 12. Black-box a telemetry validation

White-box signals môžu byť nesprávne, chýbať alebo merať inú boundary. Doplň:

- regional synthetic transaction;
- DNS/TLS/HTTP validation;
- async completion canary;
- known logical operation s očakávaným provider a ledger outcome;
- telemetry canary, ktorá overí, že Golden Signals vznikli a sú queryovateľné.

Black-box signal overí external contract. White-box signals vysvetlia mechanismus. Potrebné sú obe.

## 13. Implementačný template

```text
Golden-Signal subject:
Capability/workflow/caller:
Valid operation population:
Cohorts a versions:

Latency:
- start/end boundary:
- successful/failed/degraded separation:
- distribution a SLO threshold:

Traffic:
- logical demand unit:
- attempts/fan-out decomposition:
- expected demand model:

Errors:
- success contract:
- numerator/denominator:
- partial/unknown/silent outcomes:

Saturation:
- critical resource/queue:
- loaded/effective capacity:
- leading threshold a failover headroom:

Black-box evidence:
SLI/SLO:
Alerts a owner:
Investigation links:
Recovery validation:
Forbidden outcomes:
```

## 14. Anti-patterny

### Štyri panely bez spoločného subjectu

Každý signal používa inú boundary alebo population a dashboard nemá konzistentný význam.

### Handler latency ako end-to-end latency

Skryje queue, async workflow a dependency wait.

### Attempts ako business traffic

Retry storm sa javí ako legitímny growth.

### Errors iba z transport statusu

Silent, partial, stale a unknown business outcomes zostanú neviditeľné.

### CPU ako univerzálna saturation

Ignoruje pools, queues, quotas, locks, IPs a downstream limits.

### Traffic drop ako zlepšenie

Latency, errors aj saturation môžu klesnúť preto, že valid demand sa k službe nedostal.

## 15. Kontrolné otázky

1. Čo tvorí exact Golden-Signal subject?
2. Prečo musia všetky štyri signals používať kompatibilnú population?
3. Ako sa líši handler a end-to-end workflow latency?
4. Prečo successful a failed latency oddeľujeme?
5. Ako retries menia Traffic bez zmeny user demandu?
6. Čo je silent error?
7. Prečo Saturation nie je synonymum utilization?
8. Ako effective capacity mení saturation denominator?
9. Ako Golden Signals nadväzujú na RED, traces a USE?
10. Ako black-box a telemetry canary chránia pred false-green verdictom?

## Glossary impact

Relevantné pojmy: Golden-Signal subject, latency-boundary contract, logical demand unit, demand amplification, business error population, silent outcome failure, saturation-resource contract, effective-capacity denominator, capacity-risk verdict, black-box outcome canary a Golden-Signal acceptance verdict.

## Primárne zdroje

- [Google SRE — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Google SRE — Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/)
- [Google SRE — Practical Alerting from Time-Series Data](https://sre.google/sre-book/practical-alerting/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: USE method](use-method.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Prometheus →](prometheus.md)
<!-- KNOWLEDGE-NAVIGATION:END -->