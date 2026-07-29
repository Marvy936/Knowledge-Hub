# Databases and Distributed Systems — rate, idempotency a backpressure lifecycles

## Admission control — distributed systems

Rozhodovací boundary, ktorá podľa exact caller/tenant/operation identity, current demandu, policy a downstream capacity povolí, oneskorí, degraduje alebo odmietne novú prácu. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Backpressure subject

Exact source, sink, operation/event identity, queue a in-flight inventory, demand/credit signal, overflow policy, deadlines, priority a recovery scope analyzovaného flowu. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Bounded drain

Riadené spracovanie existujúceho backlogu pod hard concurrency, fairness, deadline a downstream-capacity limitmi až po business reconciliation bez nového overloadu. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Bounded queue — distributed flow

Queue s explicitným hard capacity, item costom, age/deadline limitom, overflow policy, priority/fairness a drain/recovery contractom. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Burst allowance

Krátkodobý počet quota units alebo operations, ktoré limiter môže prijať nad sustained rate a ktoré musí vedieť absorbovať downstream capacity a bounded buffers. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Capacity envelope — admission

Zmeraný bezpečný rate, concurrency, burst, queue a recovery rozsah required end-to-end completion pathu, podľa ktorého sa odvodzuje admission. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Concurrency limit — admission

Hard alebo dynamic limit počtu súčasne rozpracovaných operations alebo attempts pre exact dependency, tenant, provider, Region či operation class. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Consumer pause state

Current per-partition rozhodnutie, že consumer dočasne nemá získavať nové records pre processing; po rebalance sa musí znovu odvodiť z aktuálnych credits a assignment generation. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Demand propagation

Prenos downstream dostupných credits, queue/in-flight stavu alebo completion capacity smerom upstream, aby source nevytváral nebounded work. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Distributed counter consistency

Pomenovaný consistency a partition contract pre rate/quota counter naprieč processes, shards alebo Regions vrátane povoleného overshootu a acknowledgement semantics. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Downstream credit

Explicitná jednotka aktuálnej capacity, ktorá oprávňuje upstream poslať alebo rozpracovať ďalší item, request či provider attempt. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Duplicate join

Behavior, pri ktorom concurrent duplicate request nezaloží novú logical operation, ale dostane rovnaký status resource, bounded wait alebo prior result existujúcej operation. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Fairness verdict — rate limiting

Dôkaz, že global/provider/tenant/operation-class budgets, weights a reserves poskytujú bounded share a neumožňujú jednej cohort-e vyhladovať ostatné required operations. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Feedback hysteresis

Oddelené high/low thresholds, hold times alebo gradual credit changes, ktoré zabraňujú opakovanému pause–resume a overload oscillation. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Flow-control window

Protocol alebo runtime boundary určujúca množstvo bytes, messages alebo operations, ktoré môže sender poslať bez ďalšieho receiver demand/acknowledgement-u. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Global limiter

Logical rate/quota admission policy koordinovaná naprieč všetkými relevantnými instances alebo shards pre jeden exact scope. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Hidden buffer

Queue alebo pending-work boundary mimo hlavného application queue dashboardu, napríklad SDK, proxy, protocol window, executor, pool waiter, producer buffer alebo consumer fetch buffer. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Idempotency key scope

Namespace, typicky tenant + operation type + key, v ktorom key jednoznačne identifikuje jeden business intent a nesmie kolidovať s iným intentom. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Idempotency retention

Minimálny čas a state-dependent lifecycle, počas ktorého musí zostať duplicate verdict dostupný cez client retry, backlog, replay, restore a external reconciliation window. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Idempotency state machine

Authoritative lifecycle `CLAIMED → ACCEPTED_DURABLE → PROCESSING → COMPLETED/FAILED_FINAL/RECONCILIATION_REQUIRED` s owner generation, fingerprintom a recovery rule. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Idempotency subject

Exact tenant, operation type, key, semantic fingerprint, authoritative operation record, state/owner generation, downstream identity, retention a response/reconciliation scope. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Idempotency/backpressure acceptance verdict

Dôkaz, že atomic stable operation identity a bounded demand/queue/in-flight flow zabránia duplicate effectu, silent lossu, unbounded memory, starvation a false completion pri retries, rebalances a sustained overload-e. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Idempotent consumer

Consumer, ktorý duplicate event identity atomicky mapuje na existujúci local transition/result a pri external effecte používa stable destination key a reconciliation. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Leaky bucket

Admission model, ktorý odvádza work približne konštantnou rýchlosťou cez bounded queue a pri pretečení alebo expirovanom deadline-e musí použiť explicitný overflow outcome. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Leased admission budget

Časovo alebo generation-bounded časť global quota pridelená konkrétnej instance/shardu, ktorej reclaim a overshoot semantics musia byť explicitné. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Limiting key

Authenticated identity a dimensions, napríklad tenant, user, provider, Region a operation class, podľa ktorých limiter zdieľa alebo oddeľuje usage counter. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Local limiter

Per-process alebo per-Pod admission counter, ktorého aggregate effective limit sa typicky násobí počtom aktívnych instances a preto nie je automaticky global quota. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Operation identity chain

Durable mapping client idempotency keyu cez authoritative operation, outbox/event, consumer processing a provider effect až po final result. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Overflow policy

Explicitný outcome pri nedostupnej downstream capacity, napríklad reject, bounded delay, durable spill, coalesce, sample, drop rebuildable data alebo degrade, viazaný na business data class. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Priority reserve — admission

Oddelená capacity alebo quota zachovaná pre status, cancellation, reconciliation, control-plane alebo inú authenticated critical operation class. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Queue age

Čas od authoritative acceptance/enqueue po current processing alebo completion boundary; odhaľuje stale work a latency debt, ktoré samotná queue depth neukazuje. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Quota — admission

Limit celkových units alebo operations počas dlhšieho window/lifecycle-u, odlišný od krátkodobého rate a current concurrency. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Rate-limiting acceptance verdict

Dôkaz, že exact keys/costs, local-vs-global scope, downstream envelopes, fairness, distributed counters, response/retry contract a burst/autoscale tests vytvárajú bounded admission bez starvationu alebo overshootu. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Rate-limiting subject

Exact business operation, caller/tenant/provider/Region identity, limiting key, units/cost, algorithm, counter generation, window/burst, downstream envelope a admit/delay/reject semantics. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Response replay — idempotency

Vrátenie prior alebo current truthful status/result representation pre duplicate request bez vytvorenia novej logical operation. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Retry-after contract

Serverom publikovaná minimálna alebo odporúčaná doba pred ďalším attemptom spolu so scope-om a retryability semantics; nie je garanciou budúceho prijatia. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Semantic payload fingerprint

Canonical digest business-relevant method/path/payload a critical dimensions použitý na odlíšenie duplicate rovnakého intentu od reuse rovnakého keyu pre iný intent. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).

## Sliding-window counter

Approximate rate algorithm kombinujúci current a previous bucket podľa časového prekryvu, lacnejší než per-request sliding log. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Token bucket

Rate algorithm s refill rate, current tokens, request costom a bucket capacity, ktorý povoľuje bounded burst nad sustained rate. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Weighted request cost

Quota units odvodené z relatívneho CPU, I/O, fan-out, payloadu, lock duration, provider calls alebo risku namiesto uniformného one-request-one-token modelu. Pozri [Rate limiting](../docs/15-databases-and-distributed-systems/rate-limiting.md).

## Exactly-once scope

Presne pomenovaná boundary, na ktorej systém tvrdí one-time processing/effect, napríklad broker transaction, database transition alebo provider business effect; tvrdenie sa nesmie automaticky rozšíriť na celý distributed flow. Pozri [Idempotency a backpressure](../docs/15-databases-and-distributed-systems/idempotency-and-backpressure.md).
