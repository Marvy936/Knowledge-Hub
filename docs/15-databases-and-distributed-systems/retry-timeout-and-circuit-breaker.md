# Retry, timeout a circuit breaker

Retry, timeout a circuit breaker nie sú nezávislé utility decorators. Tvoria jeden control system nad latency, capacity, failure classification a unknown outcomes.

Zle zložené policies môžu z malého dependency incidentu vytvoriť retry storm, vyčerpať pools a queues, predĺžiť latency a znásobiť non-idempotent side effects. Správny návrh preto začína logical operation, deadline budgetom a jedným explicitným retry ownerom.

## 1. Dominantný model

```text
logical operation a business deadline
→ exact dependency/attempt subject
→ end-to-end timeout budget
→ failure a outcome classification
→ retry eligibility a stable identity
→ bounded attempts + backoff/jitter/budget
→ circuit state a admission decision
→ dependency recovery probe
→ final business outcome a reconciliation
→ second-failure validation
```

Každý physical attempt musí byť mapovateľný na jeden logical operation a jeho authoritative outcome.

## 2. Timeout nie je failure proof

Timeout znamená:

> Caller prestal čakať v definovanom čase.

Neznamená automaticky:

- request nedorazil;
- server nezačal pracovať;
- transaction rollbackla;
- external effect nenastal;
- response neexistuje;
- retry je bezpečný.

```text
provider effect completed
→ response lost alebo oneskorená
→ caller timeout
→ outcome = unknown, nie failed
```

Pre side-effecting operation sa timeout musí mapovať na lookup/reconciliation path.

## 3. Deadline vs. timeout

### Timeout

Maximálna duration konkrétneho waitu alebo attemptu.

### Deadline

Absolútny alebo odvodený end-to-end čas, po ktorom caller už result nepotrebuje alebo ho nemôže bezpečne použiť.

```text
business deadline 2 000 ms
→ gateway processing 100 ms
→ queueing 250 ms
→ service budget 1 650 ms
→ provider attempt + cleanup musia zostať v tomto budgete
```

Každá downstream vrstva musí dostať remaining budget, nie nový plný timeout.

## 4. Deadline propagation

Bez propagation vzniká:

```text
client timeout 1 s
→ gateway timeout 2 s
→ service timeout 3 s
→ provider timeout 30 s
```

Caller už dávno odišiel, ale downstream work pokračuje a spotrebúva:

- threads;
- connections;
- queue slots;
- provider quota;
- retry budget;
- memory;
- locks.

Downstream musí vedieť remaining deadline a cancellation state. Application je stále zodpovedná za zastavenie spawned worku tam, kde je to bezpečné.

## 5. Timeout layers

Bežný request môže mať:

- DNS/connect timeout;
- TLS handshake timeout;
- connection-pool checkout timeout;
- request/response timeout;
- database statement timeout;
- transaction timeout;
- queue visibility/lease timeout;
- provider attempt timeout;
- user/business deadline.

Najväčší configured timeout nie je automaticky effective deadline. Queueing a retries spotrebúvajú spoločný budget.

## 6. Failure classification

Retry policy potrebuje explicitnú classification.

### Typicky retryable

- transient connection reset pred potvrdeným sendom;
- rate limit s `Retry-After` a available budgetom;
- temporary leader election;
- explicit retriable serialization failure celej transaction;
- bounded overload response;
- stale discovery endpoint po safe reconnecte.

### Typicky non-retryable

- validation error;
- authentication/authorization denial;
- invariant conflict;
- unsupported schema/version;
- malformed request;
- permanent business rejection;
- exhausted deadline;
- open circuit.

### Unknown outcome

- timeout po možnom send-e;
- connection loss po request body;
- lost commit acknowledgement;
- provider call bez response;
- worker crash medzi side effectom a result persistence.

Unknown outcome potrebuje lookup/idempotency/reconciliation, nie blind retry.

## 7. Stable operation a attempt identity

```text
operation_id: logical business intent
attempt_id:   jeden physical execution attempt
```

Retry musí zachovať:

- operation/idempotency key;
- payload identity alebo hash;
- tenant/resource scope;
- provider idempotency key;
- current writer/leader epoch;
- attempt lineage;
- original deadline.

Nový random idempotency key pri každom retryi mení retry na novú business operation.

## 8. Retry owner

Retry môže implementovať:

- client SDK;
- gateway/proxy;
- service;
- database driver;
- message consumer;
- service mesh;
- provider SDK.

Ak každá vrstva retryuje nezávisle, attempts sa násobia.

```text
SDK:             1 + 2 retries = 3
Gateway:         1 + 1 retry   = 2
Provider client: 1 + 2 retries = 3

maximum physical attempts = 3 × 2 × 3 = 18
```

Pre jeden dependency boundary má byť jeden primary retry owner; ostatné vrstvy musia rešpektovať outcome, budget a idempotency contract.

## 9. Retry limit a retry budget

### Per-request limit

Obmedzuje attempts jedného logical requestu.

### Aggregate retry budget

Obmedzuje retry volume celej service/dependency/cohort populácie.

Per-request `maxAttempts=3` nestačí, ak tisíce concurrent requests retryujú súčasne.

Príklad:

```text
normal first attempts: 10 000/min
retry budget:          max 1 000/min
budget exhausted
→ fail fast/defer/reconcile
```

Retry budget chráni dependency aj caller capacity.

## 10. Backoff a jitter

Immediate retry môže uspieť pri jednej lost packet udalosti, ale coordinated retries vytvárajú synchronized load spikes.

```text
attempt 1
→ exponential backoff
→ random jitter
→ remaining-deadline check
→ attempt 2
```

Jitter rozkladá clients v čase. Backoff bez jitteru môže všetky instances prebudiť v rovnakých intervaloch.

Server-provided `Retry-After` alebo explicitný overload hint má prednosť pred agresívnym local schedule-om, ak business deadline dovolí čakať.

## 11. Hedging

Hedged request spustí ďalší concurrent attempt po krátkom delayi, aby znížil tail latency.

Je bezpečný iba pre:

- idempotent reads;
- deduplicated requests;
- resources s capacity budgetom;
- explicitne zrušiteľný losing attempt;
- no-side-effect alebo fenced operations.

Hedging non-idempotent provider callu je intentional duplication, nie retry optimization.

## 12. Circuit breaker

Circuit breaker chráni caller a dependency pred opakovanými calls, ktoré pravdepodobne zlyhajú.

Typický state machine:

```text
Closed
→ failures/slow outcomes prekročia threshold
→ Open
→ cooldown/recovery interval
→ Half-Open
→ bounded probes
→ Closed alebo Open
```

### Closed

Requests prechádzajú a breaker vyhodnocuje rolling failure/latency sample.

### Open

Requests sú odmietnuté bez dependency callu alebo smerujú na explicitný degraded path.

### Half-Open

Malý počet probes overuje recovery. Nesmie vypustiť celý backlog naraz.

## 13. Breaker scope

Breaker key musí zodpovedať failure domainu:

- dependency service;
- Region;
- provider;
- tenant;
- shard;
- operation type;
- endpoint generation.

Jeden global breaker môže blokovať healthy shards. Breaker per Pod môže byť naopak príliš fragmentovaný a každý Pod vyšle vlastné probes/retries.

Prakticky treba často shared alebo coordinated retry/admission budget, hoci breaker state môže zostať local.

## 14. Breaker signal

Breaker nemá sledovať iba HTTP `5xx`.

Relevantné signals:

- timeout/deadline exceeded;
- connection failure;
- high latency;
- rate limiting;
- saturation;
- malformed/contract failures oddelene;
- provider business rejection oddelene;
- queue age;
- unknown-outcome rate;
- successful final business completion.

Transport `200` s business failure nie je success. Timeout s neskorším successful provider effectom nie je jednoduchý dependency failure sample.

## 15. Circuit breaker vs. retry

- Retry očakáva, že transient failure sa môže v krátkom čase zlepšiť.
- Circuit breaker bráni ďalším attempts, keď failure pravdepodobne pretrváva.

```text
request
→ breaker admission
→ bounded retry policy
→ dependency
```

Retry musí prestať, keď breaker otvorí. Breaker bez retry budgetu nemusí zastaviť storm pred dosiahnutím threshold-u na mnohých instances.

## 16. Circuit breaker vs. rate limit a bulkhead

### Rate limit

Obmedzuje admission podľa množstva/času a chráni quota alebo fairness.

### Bulkhead

Izoluje capacity pools medzi workloads/dependencies.

### Circuit breaker

Reaguje na observed failure/recovery state dependency.

Tieto controls sa dopĺňajú. Circuit breaker nevytvára connection reserve, ak všetky threads už čakajú v dlhom timeout-e.

## 17. Graceful degradation

Open circuit môže vrátiť:

- explicitný `503`/deferred response;
- stale cache s jasným freshness markerom;
- queue acceptance, ak je durable a business contract to povoľuje;
- reduced capability;
- manual/reconciliation-required state.

Fallback nesmie klamať o success alebo použiť stale authority na side effect.

## 18. Recovery a half-open probes

Recovery contract zahŕňa:

- cooldown;
- probe count a concurrency;
- representative operation;
- dependency capacity warmup;
- success threshold;
- backlog release rate;
- re-open condition;
- observability.

Health endpoint môže byť green, ale real operation môže stále zlyhávať pre auth, quota, data alebo business path.

## 19. Connected incident `DB-PAY-59`

Počas regional partition-u a provider `P1` degradácie malo Atlas Payments tri retry vrstvy:

```text
merchant SDK:    max 2 retries
API gateway:     max 1 retry on timeout/connect failure
provider client: max 2 retries
```

Teoretické maximum bolo `18` physical attempts na jeden logical operation.

Configured deadlines:

```text
merchant request deadline: 900 ms
gateway upstream timeout:  900 ms
settlement service timeout: 1 500 ms
provider client timeout:   700 ms per attempt
```

Deadline sa nepropagoval. Každá vrstva začala vlastný timeout budget.

Circuit breaker:

- bol local v každom zo `72` provider-worker Podov;
- otvoril sa po `20` HTTP `5xx` v 30 sekundách;
- timeouts sa nepočítali ako failures;
- každý Pod mal vlastný half-open probe;
- breaker key nerozlišoval provider route generation ani Region.

Provider `P1` však prevažne timeoutoval, nie vracal `5xx`. Breakers zostali `Closed`.

## 20. Retry-storm dôsledky

Za 9 minút:

- `24 600` logical settlement operations;
- `68 240` physical provider attempts;
- attempt amplification `2.77×`;
- `1 384` operations v `sent-unknown` cohort-e;
- `27` duplicate physical provider attempts z overlapping retries/leader epochs;
- provider connection pool checkout p99 `1.9 s`;
- worker active concurrency vzrástla `4.6×`;
- Region A quorum/control operations zaznamenali vyššiu latency pre shared network/CPU pressure;
- zero duplicate financial effects vďaka provider idempotency.

Retry storm bol amplifier. Trigger bol provider degradation a partition. Root cause resilience layeru bola nesúvislá composition timeoutov, retries a breaker scopes bez shared logical-operation/deadline budgetu.

## 21. Unknown-outcome failure

Pri provider timeout-e systém vykonal:

```text
attempt timeout
→ gateway retry na inom workerovi
→ provider client nový attempt_id
→ rovnaký operation_id, ale nie vždy rovnaký provider idempotency key
```

Niektoré cohorts použili stable provider key, iné legacy key odvodený z `attempt_id`. To vytvorilo 27 duplicate physical attempts.

Provider ledger nakoniec potvrdil jeden financial effect pre každú operation, ale reconciliation trvalo 38 minút.

## 22. Evidence-preserving containment

```text
stop gateway a SDK retries pre settlement create
→ force one retry owner
→ preserve operation/attempt/deadline/breaker state
→ open provider P1 circuit centrally
→ stop stale-route Region B calls
→ reserve provider lookup/reconciliation capacity
→ classify never-sent/sent-unknown/completed
→ query provider by stable idempotency key
→ replay iba exact never-sent manifest
```

## 23. Authoritative redesign

### Deadline contract

```text
business acceptance deadline: 900 ms
provider execution: asynchronous after durable acceptance
provider attempt deadline: 2 s independent worker budget
final operation deadline/SLO: explicit status workflow
```

Public request už nečaká na provider effect.

### Retry ownership

```text
merchant SDK
→ no blind retry after accepted/unknown create
→ status lookup using stable operation_id

gateway
→ no non-idempotent retry

provider worker
→ single bounded retry owner
→ stable provider idempotency key
→ aggregate retry budget
```

### Backoff/budget

- max 2 provider attempts pred reconciliation state;
- exponential backoff s full jitter;
- shared provider+Region retry budget;
- honor `Retry-After`;
- no retry po deadline, validation alebo open circuit;
- queue backlog age ako admission signal.

### Circuit breaker

```text
key: provider + Region + operation class
signals: timeout + connect + 5xx + saturation + unknown rate
state: coordinated metrics, bounded local enforcement
half-open: small canary cohort
fallback: durable defer/reconciliation-required, nie false success
```

### Capacity isolation

- provider attempts majú vlastný bulkhead;
- status lookup má reserved capacity;
- reconciliation má dedicated rate limit;
- control/consensus traffic nie je v rovnakom resource pool-e ako retry storm.

## 24. Retry/timeout/circuit-breaker acceptance verdict

Resilience design je prijatý, keď:

- exact logical operation, attempts a dependency subject sú explicitné;
- end-to-end deadline a per-stage remaining budgets sú definované;
- timeout sa neinterpretuje automaticky ako failure;
- failure/retry/unknown classifications sú explicitné;
- stable operation a provider idempotency identity prežijú retries;
- jeden primary retry owner existuje pre dependency boundary;
- per-request limit aj aggregate retry budget sú enforced;
- backoff, jitter a server hints sú podporované;
- circuit breaker scope zodpovedá failure domainu;
- timeout, latency, saturation a business outcome sú súčasť breaker signalov;
- Open/Half-Open behavior má bounded admission a truthful fallback;
- queues, pools a control-plane traffic majú bulkhead/reserve;
- unknown outcomes majú lookup a reconciliation;
- slow dependency, lost response, open circuit, recovery probe a second-failure tests prejdú;
- forbidden retry storm, deadline reset, duplicate side effect a false-success outcomes sú odmietnuté.

## 25. Troubleshooting flow

```text
timeout, retry storm alebo cascading failure
→ exact logical operation a attempt tree
→ caller business deadline
→ per-layer timeout/deadline propagation
→ failure classification
→ retry owners/limits/backoff/jitter
→ aggregate retry budget
→ operation/idempotency identity
→ breaker key/state/signals
→ queues/pools/bulkheads
→ dependency and external outcome
→ reconciliation a second-failure test
```

## 26. Anti-patterny

### Timeout znamená retry

Outcome môže byť unknown a effect už mohol nastať.

### Každá vrstva má tri retries

Attempts sa násobia, nie sčítavajú.

### Exponential backoff stačí

Bez jitteru, deadline a aggregate budgetu môže storm pokračovať.

### Circuit breaker počíta iba `5xx`

Slow/timeouting dependency môže zničiť capacity bez `5xx` responses.

### Breaker per Pod je úplná izolácia

Desiatky Podov môžu každý posielať vlastné attempts a probes.

### Zvýšime timeout

Môže zvýšiť held resources a znížiť throughput.

### Open circuit vráti cached success

Fallback musí zachovať business truth a freshness/authority contract.

### Idempotency key podľa attemptu

Každý retry sa stane novou operation.

## 27. Kontrolné otázky

1. Ako sa timeout líši od failure-u?
2. Ako sa deadline líši od per-attempt timeout-u?
3. Prečo treba propagovať remaining budget?
4. Čo je unknown outcome?
5. Ako sa operation_id líši od attempt_id?
6. Prečo viac retry vrstiev násobí attempts?
7. Čo je aggregate retry budget?
8. Prečo jitter patrí k backoffu?
9. Aké stavy má circuit breaker?
10. Prečo breakers v `DB-PAY-59` neotvorili?
11. Ako má vyzerať half-open recovery?
12. Čo overuje retry/timeout/circuit-breaker acceptance verdict?

## Glossary impact

Relevantné pojmy: resilience subject, end-to-end deadline, remaining deadline budget, attempt timeout, unknown timeout outcome, retry eligibility, retry owner, retry multiplication, retry budget, exponential backoff, jitter, hedged request, circuit breaker, Closed/Open/Half-Open state, breaker scope, breaker signal, recovery probe, graceful degradation, dependency bulkhead a retry/timeout/circuit-breaker acceptance verdict.

## Primárne zdroje

- [gRPC — Deadlines](https://grpc.io/docs/guides/deadlines/)
- [gRPC — Retry](https://grpc.io/docs/guides/retry/)
- [Azure Architecture Center — Circuit Breaker pattern](https://learn.microsoft.com/azure/architecture/patterns/circuit-breaker)
- [Azure Architecture Center — Transient fault handling](https://learn.microsoft.com/azure/architecture/best-practices/transient-faults)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Leader election a consensus](leader-election-and-consensus.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
