# Retry, timeout a circuit breaker

Retry, timeout a circuit breaker tvoria jeden control system nad logical operation, latency, capacity a unknown outcomes. Ak sú nakonfigurované nezávisle v SDK, gatewayi, service a provider clientovi, malý dependency incident sa môže zmeniť na retry storm, pool exhaustion a duplicate physical effects.

```text
logical operation a business deadline
→ exact dependency/attempt subject
→ remaining deadline budget
→ failure alebo unknown-outcome classification
→ stable operation a attempt identity
→ one retry owner + bounded aggregate budget
→ backoff/jitter alebo explicit refusal
→ circuit admission a recovery probes
→ durable final/reconciliation state
→ slow dependency, lost response a second-failure validation
```

Timeout znamená iba to, že caller prestal čakať. Neznamená, že request nedorazil, transaction rollbackla alebo external effect nenastal.

## 1. Resilience subject, deadline a timeout

Exact subject musí pomenovať logical operation, physical attempts, caller/dependency generation, business deadline, queue/connect/request/transaction timeouts, retry owner, idempotency identity, failure classification, circuit scope, fallback a final outcome authority.

Deadline je end-to-end čas, po ktorom result už nie je užitočný alebo bezpečný. Timeout je maximum konkrétneho waitu/attemptu. Každá downstream vrstva musí dostať remaining budget:

```text
business deadline 2 000 ms
- routing/auth/queueing 350 ms
= service child budget 1 650 ms
→ provider attempt + cleanup musia zostať v 1 650 ms
```

Ak client timeoutuje za `900 ms`, gateway za `900 ms`, service za `1 500 ms` a provider attempt za `700 ms` bez propagation, downstream work pokračuje po odchode caller-a. Spotrebúva threads, connections, queue slots, quota a retry budget a môže dokončiť side effect, o ktorom caller nevie.

Timeout layers zahŕňajú DNS/connect/TLS, pool checkout, request response, statement, transaction, queue lease a provider attempt. Ich súčet a queueing musia zapadnúť do jedného business deadline-u; najväčší config value nie je effective contract.

## 2. Outcome classification a stable identity

Retry policy musí rozlíšiť:

- definitely not executed alebo explicitne transient retryable;
- permanent validation/auth/business rejection;
- dependency overload s `Retry-After` alebo deferred contractom;
- exhausted deadline/open circuit;
- unknown outcome po možnom commite alebo send-e.

```text
provider effect succeeds
→ response lost
→ caller timeout
→ outcome = sent-unknown
→ lookup/reconciliation, nie blind retry
```

`operation_id` identifikuje logical business intent. `attempt_id` identifikuje physical execution. Každý retry musí zachovať operation/idempotency key, tenant/payload identity, provider idempotency key, current writer epoch, original deadline a attempt lineage. Idempotency key odvodený z attemptu mení retry na novú operation.

Unknown database commit, provider timeout alebo worker crash medzi effectom a result persistence potrebuje status lookup a reconciliation capacity. Retry eligibility vzniká až po outcome classification.

## 3. Retry owner, limits a backoff

Retry môže existovať v SDK, gatewayi, service, driveri, message consumerovi, mesh-i a provider SDK. Ak SDK vykoná tri attempts, gateway dva a provider client tri, maximum je `3 × 2 × 3 = 18`, nie osem.

Pre jednu dependency boundary má existovať jeden primary retry owner. Ostatné vrstvy môžu reconnectnúť pred potvrdeným sendom alebo queryovať status, ale nesmú vytvárať independent effect attempts.

Per-operation limit chráni jeden request. Aggregate retry budget chráni celú dependency a fleet:

```text
first attempts: 10 000/min
allowed retries: 1 000/min
budget exhausted
→ fail fast, defer alebo reconcile
```

Exponential backoff bez jitteru môže prebudiť celý fleet v rovnakom intervale. Každý retry kontroluje remaining deadline, circuit state a server hint. `Retry-After` sa rešpektuje iba ak business deadline dovolí čakať. Immediate retries sú výnimka pre presne klasifikovaný pre-send transient failure.

Hedging spustí concurrent attempt pre tail latency. Je vhodný iba pre idempotent reads alebo deduplicated/fenced operations s capacity budgetom a cancellable loserom. Hedging payment provider callu je intentional duplication.

## 4. Circuit breaker ako admission state machine

Circuit breaker chráni caller a dependency pred attempts, ktoré pravdepodobne zlyhajú:

```text
Closed
→ failure/slow/unknown threshold
→ Open
→ cooldown
→ Half-Open bounded probes
→ Closed alebo znovu Open
```

Closed neznamená dependency healthy; iba povoľuje calls a zbiera samples. Open odmieta alebo použije truthful degraded path. Half-Open smie pustiť malý representative cohort, nie celý backlog.

Breaker key musí zodpovedať failure domainu: provider + Region + operation class, prípadne endpoint generation alebo shard. Global breaker môže blokovať healthy cohort; per-Pod breaker v 72 Podoch môže každý posielať vlastné retries a probes. Local enforcement preto často potrebuje coordinated metrics a shared retry/admission budget.

Signals zahŕňajú timeouty, connect failures, latency, saturation, rate limit, unknown-outcome rate a final business completion. HTTP `5xx` samotné nestačí; timeouting dependency môže vyčerpať capacity bez jediného response-u.

Circuit breaker nenahrádza bulkhead ani rate limit. Bulkhead izoluje pools, rate limit obmedzuje admission a breaker reaguje na observed dependency state. Long timeout môže spotrebovať všetky connections skôr, než breaker nazbiera threshold.

## 5. Fallback, recovery a capacity isolation

Open circuit môže vrátiť explicitný unavailable/deferred result, durable queue acceptance, reduced capability, bounded stale representation alebo reconciliation-required state. Fallback nesmie vracať cached success ani stale authority pre side effect.

Recovery contract určuje cooldown, probe count, representative operation, success threshold, warmup a backlog release rate. Health endpoint nie je dostatočný probe pre auth, quota, data a real business path.

Provider attempts, status lookup, reconciliation a control-plane traffic potrebujú oddelené bulkheads/reserves. Retry storm nesmie vyčerpať capacity potrebnú na zistenie unknown outcomes alebo consensus route change.

Queue backlog age a pool waits sú admission signals. Circuit close po dependency recovery nesmie naraz vypustiť celý accumulated backlog a znovu ju preťažiť.

## 6. Connected incident `DB-PAY-59`

Počas regional partition-u a degradácie `P1` používalo Atlas Payments tri retry vrstvy: merchant SDK max 2 retries, gateway max 1 a provider client max 2. Teoretické maximum bolo `18` attempts na logical operation. Deadline sa nepropagoval; každá vrstva začala vlastný budget.

Breaker bol local v každom zo `72` provider-worker Podov. Otváral sa po `20` HTTP `5xx` za 30 sekúnd, no provider prevažne timeoutoval. Timeouts sa nepočítali ako failures, breaker key nerozlišoval provider route/Region a každý Pod mal vlastný half-open probe. Breakers preto zostali Closed.

Za deväť minút prišlo `24 600` logical operations a vzniklo `68 240` physical provider attempts, teda amplification `2.77×`. `1 384` operations skončilo `sent-unknown`, pool checkout p99 dosiahol `1.9 s` a active worker concurrency vzrástla `4.6×`. `27` duplicate physical attempts vzniklo aj preto, že niektoré legacy cohorts odvodzovali provider key z `attempt_id`. Provider idempotency zachovala jeden financial effect, no reconciliation trvala 38 minút.

Root cause resilience layeru bola nesúvislá composition timeoutov, retries a breaker scopes bez shared operation/deadline budgetu. Provider degradation a partition boli trigger; retry storm bol silný amplifier.

## 7. Redesign a acceptance paths

Public `900 ms` request vykonáva iba durable acceptance; provider execution je asynchronous s vlastným bounded worker budgetom. SDK po accepted/unknown create neretryuje, ale queryuje status. Gateway neretryuje non-idempotent POST. Provider worker je jediný retry owner, používa stable provider key, max dva attempts pred reconciliation a shared provider+Region retry budget.

Breaker key je provider + Region + operation class. Signals zahŕňajú timeout, connect, `5xx`, saturation a unknown rate. Half-Open používa malý canary cohort; fallback je durable defer alebo reconciliation-required, nie false success.

**Positive path** dokončí first attempt v budgete alebo bounded retry po explicitne transient failure-i.

**Unknown path** stratí provider response; operation vstúpi do sent-unknown, reserved lookup zistí outcome a nevytvorí nový key/effect.

**Recovery path** otvorí circuit, chráni capacity, vykoná representative half-open probes a rampuje backlog bez second overloadu.

**Forbidden path** odmietne deadline reset, viac retry ownerov, attempt-based idempotency, retry po open circuit/deadline, breaker ignorujúci timeouty a cached false success fallback.

Acceptance zahŕňa slow dependency, lost response, rate limit hint, open/half-open transition, fleet restart, second failure počas recovery a exhausted reconciliation reserve.

## 8. Troubleshooting a anti-patterny

Diagnostika ide od logical operation a attempt tree cez business deadline, per-layer timeouts, failure classification, retry owners/limits/budget, idempotency identity, breaker key/state/signals, queues/pools/bulkheads a external outcome až po reconciliation.

Najčastejšie anti-patterny sú timeout automaticky znamenajúci retry, tri retries v každej vrstve, backoff bez jitter/deadline/budgetu, breaker iba na `5xx`, per-Pod breaker považovaný za fleet control, plošné zvýšenie timeoutu, cached success pri open circuit a idempotency key podľa attemptu.

## 9. Kontrolné otázky

1. Ako sa timeout líši od failure-u a deadline-u?
2. Prečo sa propaguje remaining budget?
3. Čo je unknown outcome?
4. Ako sa operation ID líši od attempt ID?
5. Prečo retries vo vrstvách násobia attempts?
6. Čo chráni aggregate retry budget?
7. Prečo backoff potrebuje jitter?
8. Ako breaker scope zodpovedá failure domainu?
9. Prečo breakers v `DB-PAY-59` zostali Closed?
10. Ktoré positive, unknown, recovery a forbidden paths musia prejsť?

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

[← Predchádzajúca: Leader election a consensus](leader-election-and-consensus.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Rate limiting →](rate-limiting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
