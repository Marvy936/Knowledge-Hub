# Rate limiting

Rate limiting nie je iba počítadlo requestov pred API. Je to admission-control contract, ktorý mapuje business demand a fairness na skutočnú completion capacity downstream pathu. Limiter môže korektne vracať `429 Too Many Requests` a napriek tomu preťažiť provider, ak počíta nesprávny subject, existuje iba per Pod, ignoruje operation cost alebo blokuje recovery traffic rovnakou vyčerpanou kvótou ako nové creates.

```text
business capacity, fairness alebo abuse objective
→ exact admission subject a operation class
→ downstream rate, concurrency a recovery envelope
→ hierarchical policy, algorithm a state generation
→ logical operation cost a current usage
→ admit, delay, degrade, reserve alebo reject
→ truthful response a retry contract
→ completion, backlog a fairness feedback
→ distributed convergence a recovery
→ autoscale, burst a second-overload validation
```

Admission verdict musí byť odvodený z effective fleet demandu a final business completion, nie iba z local countera.

## 1. Admission subject a chránený envelope

Exact subject pomenúva capability, caller/tenant/merchant, endpoint a operation class, provider a Region, logical operation a physical attempt, weighted cost, policy generation, global alebo local scope, burst, downstream rate/concurrency, backlog objective, reserve a rejection/retry semantics.

Tvrdenie `limit je 1 000 req/s` je preto neúplné. Status lookup, settlement create a bulk replay nemajú rovnaký cost ani failure consequence. Limit per Pod sa pri autoscale násobí. Limit podľa raw HTTP attempts môže penalizovať bezpečný status lookup a zároveň neobmedziť drahý logical create, ktorý sa cez retries objaví viackrát.

Rate, quota, concurrency a capacity riešia rozdielne dimensions. Rate obmedzuje units za čas, quota dlhodobé allocation, concurrency súčasné in-flight operations a capacity envelope celý completion path:

```text
API admission
→ settlement + outbox commit
→ broker a consumer
→ provider attempt
→ final-state persistence
→ reconciliation
```

Ak provider bezpečne dokončí `6 500` attempts/s a unesie `1 200` in-flight, admission `9 000` creates/s nie je bezpečná len preto, že PostgreSQL ich vie commitnúť. Bounded buffer môže krátko absorbovať rozdiel, ale potrebuje hard capacity, maximum backlog age a recovery target.

## 2. Hierarchia, fairness a operation cost

Jeden global limit chráni celkovú kapacitu, ale dovolí jednému tenantovi vyčerpať celý budget. Jeden per-tenant limit chráni fairness, no súčet tenants môže stále preťažiť provider. Effective policy preto býva hierarchická:

```text
global settlement envelope
→ provider + Region envelope
→ tenant weighted share
→ operation class
→ client burst allowance
```

Každý request spotrebuje quota units podľa expected cost. Status query môže stáť `1`, create `8`, bulk settlement `400` a reconciliation export `1 000` units. Cost vychádza z fan-outu, records, provider calls, I/O, lock duration, payloadu a risku. Front-door limiter potrebuje lacnú identity a konzervatívny cost ešte pred drahým parsingom alebo database lookupom; presnejší limiter môže existovať na ďalšej boundary.

Priority a rezervovaná kapacita musia byť authenticated a hard-bounded. Cancellation, status a unknown-outcome lookup potrebujú reserve aj pri create overload-e. Interactive creates môžu mať vyššiu prioritu než bulk replay, ale priority queue nesmie obísť global/provider cap ani permanentne vyhladovať batch. Fairness sa preto overuje na admitted aj completed worke per tenant/class.

IP adresa je slabá business identity: NAT zdieľa viac users, proxy môže skryť origin a neoverený forwarding header možno spoofnúť. Security/abuse limiter môže IP používať ako defense-in-depth, no business quota sa viaže na authenticated subject.

## 3. Algorithms a burst semantics

Fixed window je lacný, ale umožní boundary burst: `999` requests na konci jednej minúty a `1 000` na začiatku ďalšej vytvorí približne `1 999` requests za sekundu. Sliding log je presnejší, no drží per-request timestamps; sliding counter je lacnejšia aproximácia. Approximation musí byť súčasťou risk contractu.

Token bucket kombinuje sustained rate a burst:

```text
refill rate = r units/s
bucket capacity = B
request cost = c
admit, ak tokens >= c
```

Idle client môže minúť celý bucket naraz. `B` preto nesmie vychádzať iba z user-experience želania; queues, pools a provider musia burst absorbovať. Leaky-bucket alebo paced admission vyrovnáva output, ale pridáva queue latency. Ak arrival dlhodobo prevyšuje drain rate, bounded queue sa musí naplniť a ďalšiu prácu odmietnuť alebo degradovať. Unbounded queue nie je limiter, iba odložený incident.

Algorithm nie je celý contract. Dôležité sú tiež clock/refill generation, key scope, atomicity countera, behavior počas partition-u, policy rollout, fail-open/fail-closed a to, či denied attempt spotreboval quota.

## 4. Local, global a distributed state

Local limiter chráni process, ale per-Pod `L` pri `N` Podoch povoľuje približne `N × L`. Autoscaling a rolling update tým menia policy. Local bucket je vhodný ako defense-in-depth alebo leased shard pod global admission, nie ako neoznačená global quota.

Centralized limiter poskytuje spoločný verdict za cenu latency, hotspotu a novej dependency. Sharded/leased model rozdeľuje global budget medzi instances; unused leases, membership change a reconnect môžu vytvoriť underutilization alebo overshoot. Lease generation, reclaim a maximum aggregate error musia byť explicitné.

Nie každý counter potrebuje linearizability. Soft fairness môže tolerovať bounded overshoot. Paid quota, scarce provider concurrency alebo compliance export môže vyžadovať authoritative reservation/commit semantics a konzervatívny partition behavior. Atomic command na jednom Redis node ešte nedokazuje, ktoré acknowledged increments prežili failover a či dva Regions neprekročili spoločný hard limit.

Distributed acceptance test musí meniť Pod count, zabiť counter ownera, oddeliť Region, obnoviť stale lease a preukázať effective global maximum. Configured values bez fleet read-backu nie sú evidence.

## 5. Admission outcome, HTTP a retries

Limiter nemusí iba povoliť alebo odmietnuť. Môže bounded delayovať, použiť cheaper/stale-safe representation, shednúť optional work alebo rezervovať capacity pre recovery. Každý outcome musí zachovať business truth: financial create nemožno silentne dropnúť; rebuildable telemetry možno sampleovať.

RFC 6585 definuje `429 Too Many Requests`. Response má vysvetliť retry contract a môže niesť `Retry-After`:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 12
Content-Type: application/problem+json

{
  "type": "urn:atlas:problem:rate-limit",
  "limit_scope": "merchant-provider-create",
  "retryable": true
}
```

`Retry-After` nie je garancia prijatia po 12 sekundách. Client musí používať deadline, exponential backoff, jitter a concurrency cap. Aktívny IETF HTTPAPI draft z mája 2026 navrhuje `RateLimit-Policy` a `RateLimit` fields; zatiaľ ide o Internet-Draft, preto sa wire contract versionuje a nevydáva za finálny RFC.

Desaťtisíc clients s rovnakým one-second retry intervalom vytvorí ďalší burst. Server preto potrebuje aggregate retry budget a client guidance; idempotency musí zachovať logical operation identity. Limiter má počítať, či retry len číta existujúci outcome alebo vytvára nový expensive attempt.

## 6. Feedback z completion pathu

Static quota nevie zachytiť zvýšenú provider latency, growing backlog alebo unknown-outcome spike. Admission controller preto sleduje admitted logical rate, current in-flight, oldest backlog age, completion rate, provider latency, database/pool waits, unknown cohort a fairness.

```text
provider credits klesnú
→ provider/Region budget sa zníži
→ bulk admission sa throttle-ne
→ status/reconciliation reserve zostane
→ backlog age sa stabilizuje
→ gradual recovery podľa completions
```

Rate limiting a backpressure sa dopĺňajú. Limiter aplikuje policy na caller/class; backpressure prenáša current downstream capacity upstream. Feedback potrebuje hysteresis a gradual ramp, aby po poklese queue depthu nevypustil celý backlog a nevytvoril second overload.

Security limiter nenahrádza authentication, authorization, validation, WAF/DDoS protection ani cost anomaly detection. Pri extrémnom attack trafficu môže byť lacnejší upstream drop než generovanie detailnej `429` odpovede pre každý packet.

## 7. Connected incident `DB-PAY-60`

Release `payments 8.4` otvoril bulk replay po 47-minútovom provider outage-i. Gateway mala `80` Podov; každý držal token bucket `450 requests/s` a burst `900`. Effective fleet policy preto povoľovala `36 000 requests/s` a immediate burst `72 000`.

Safe envelopes boli: PostgreSQL settlement+outbox `9 000` logical operations/s, provider P2 `6 500` new attempts/s a result persistence `7 200` results/s. Partner dosiahol `21 600 requests/s` plus normal traffic `3 200/s`. Limiter počítal raw HTTP attempts, nemal tenant/provider hierarchy, status stál rovnako ako create a autoscale násobil policy.

Počas 14 minút gateway prijala `6.9 milióna` requests; jeden partner spotreboval `71 %` create capacity, backlog age dosiahol `54 minút` a HTTP-attempt amplification `2.4×`. Local buckets vracali `429` bez `Retry-After`; SDK retryovala po fixných `100 ms`. Provider a DB pooly sa saturovali, hoci väčšina local bucketov nebola trvalo empty.

Evidence `450 × 80 = 36 000/s` a per-Pod bucket states vylúčili global-counter lag. Provider saturation začínala približne pri `6 500/s`. Root cause bol process-local request counter bez fleet, tenant, operation-cost a downstream-capacity contractu. Provider slowdown bol trigger; autoscale, fixed retries, shared priority a missing recovery reserve boli amplifiers.

## 8. Redesign a acceptance paths

Target používa global settlement envelope, provider+Region budget, tenant weighted share, operation cost a per-client burst. Pre P2 je safe new-attempt rate `5 800/s`, hard in-flight `1 200`, recovery reserve `15 %` a samostatný status/reconciliation budget. Duplicate request so známym idempotency keyom najprv načíta existing operation a neplatí cost nového create-u.

**Positive path** udrží admitted a completed rate v safe envelope, poskytne fair tenant share a truthful retry fields.

**Overload path** spomalí alebo odmietne bulk work podľa backlog age, zachová status/cancellation/reconciliation a neprekročí provider concurrency.

**Recovery path** postupne zvyšuje credits podľa final completions a prejde second burst bez oscillation.

**Forbidden path** odmietne per-Pod policy vydávanú za global, jeden tenant vyčerpávajúci celý budget, status starvation, no-jitter retry storm, stale lease overshoot a false admission nad downstream capacity.

Acceptance zahŕňa autoscale, rolling update, counter failure/partition, one-tenant flood, mixed costs, cache/idempotency hits a druhý overload počas recovery.

## 9. Troubleshooting a anti-patterny

Diagnostika ide od exact admission subjectu cez caller/tenant/provider identity, configured vs. effective fleet limit, algorithm a state generation, logical cost, downstream rate/concurrency/backlog, retry contract, fairness/reserves a final completion. `429 count` bez rejected operation classu a downstream outcome-u nie je dostatočný signal.

Najčastejšie anti-patterny sú neoznačené `500 req/s`, per-Pod limiter ako global quota, IP ako user, jeden token pre všetky operations, `429` bez retry guidance, unbounded queue ako limiter, high priority obchádzajúca hard cap a statická policy ignorujúca downstream credits.

## 10. Kontrolné otázky

1. Čo tvorí exact admission subject a chránený capacity envelope?
2. Ako sa rate, quota a concurrency limit líšia?
3. Prečo per-Pod limit nie je global limit?
4. Ako hierarchical budgets poskytujú capacity aj fairness?
5. Ako fixed window, token bucket a paced admission menia burst?
6. Kedy je approximate distributed counter prijateľný?
7. Čo musí niesť truthful `429` a retry contract?
8. Prečo status a reconciliation potrebujú reserve?
9. Prečo limiter v `DB-PAY-60` nechránil provider P2?
10. Ktoré positive, overload, recovery a forbidden paths musia prejsť?

## Glossary impact

Relevantné pojmy: rate-limiting subject, admission control, quota, concurrency limit, capacity envelope, hierarchical budget, limiting key, weighted request cost, fixed window, sliding window, token bucket, paced admission, local limiter, global limiter, leased budget, distributed-counter consistency, burst allowance, priority reserve, retry-after contract, completion feedback, fairness verdict a rate-limiting acceptance verdict.

## Primárne zdroje

- [RFC 6585 — Additional HTTP Status Codes](https://www.rfc-editor.org/rfc/rfc6585.html)
- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [IETF HTTPAPI — RateLimit header fields for HTTP, draft-11](https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/)
- [gRPC — Status Codes](https://grpc.io/docs/guides/status-codes/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Retry, timeout a circuit breaker](retry-timeout-and-circuit-breaker.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Idempotency a backpressure →](idempotency-and-backpressure.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
