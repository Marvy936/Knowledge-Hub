# Rate limiting

Rate limiting nie je iba počítadlo requestov pred API. Je to admission-control contract, ktorý musí chrániť downstream capacity, fairness, business invarianty a recovery paths pri presne pomenovanom limite a scope-e.

Limiter môže korektne vracať `429 Too Many Requests` a napriek tomu nezabrániť overloadu, ak počíta nesprávny subject, existuje iba per Pod, ignoruje operation cost alebo povoľuje viac trafficu než downstream dokáže dokončiť.

## 1. Dominantný model

```text
business capacity, fairness alebo abuse objective
→ exact admission subject, key a operation class
→ downstream execution envelope
→ limit scope, algorithm a state generation
→ request cost a current usage
→ admit, delay, degrade alebo reject
→ response a retry contract
→ distributed convergence a fairness verification
→ downstream business outcome
→ second-burst a recovery validation
```

Rate-limit verdict musí byť odvodený z effective global demandu a downstream outcome-u, nie iba z local countera.

## 2. Čo presne limitujeme

Rate-limiting subject obsahuje minimálne:

- business capability a API operation;
- caller, tenant, merchant, user alebo workload identity;
- endpoint, provider, Region a priority class;
- logical operation a physical attempt identity;
- request cost alebo concurrency weight;
- limit generation, window a burst allowance;
- authoritative counter scope;
- downstream capacity a protected invariant;
- rejection, delay, degradation a retry semantics.

Tvrdenie `limit je 1 000 req/s` je neúplné. Nie je zrejmé:

- pre koho;
- pre ktorý endpoint;
- či ide o logical operations alebo HTTP attempts;
- či je limit local, zonálny alebo global;
- či status query stojí rovnako ako side-effecting create;
- aký burst je povolený;
- čo sa stane po prekročení;
- či downstream vôbec zvládne 1 000 admitted operations za sekundu.

## 3. Rate, quota, concurrency a capacity

### Rate limit

Obmedzuje počet alebo cost operácií za časové obdobie.

```text
600 units / 60 s
```

### Quota

Obmedzuje celkové použitie v dlhšom intervale alebo lifecycle-e.

```text
2 000 000 provider operations / day
```

### Concurrency limit

Obmedzuje počet súčasne rozpracovaných operácií.

```text
max 320 in-flight provider attempts
```

Concurrency limit reaguje na duration. Rovnaký request rate pri desaťnásobnej latency môže potrebovať približne desaťnásobný počet in-flight slots.

### Capacity envelope

Je skutočný bezpečný výkon celého completion pathu:

```text
API admission
→ transaction/outbox commit
→ broker
→ consumer
→ provider
→ final-state persistence
→ reconciliation
```

Admission nemá byť vyššia než najnižšia bezpečná a recoverable capacity required pathu, pokiaľ existuje explicitný bounded buffer a backlog objective.

## 4. Limiting key a fairness

Bežné keys:

- authenticated tenant alebo API client;
- user/account;
- merchant;
- source network identity;
- endpoint alebo operation class;
- provider a Region;
- organization/project;
- device alebo session.

IP adresa je často slabá business identity:

- veľa users môže zdieľať NAT;
- jeden client môže meniť IP;
- proxy môže skryť pôvod;
- spoofovateľný forwarding header môže obísť limiter;
- IPv6 môže vytvoriť veľký address space.

Fair limiter typicky používa hierarchiu:

```text
global service budget
→ provider/Region budget
→ tenant budget
→ operation-class budget
→ caller burst budget
```

Jedna úroveň nestačí. Tenant môže dodržať svoj limit a súčet tenants stále preťaží provider. Global limit zase môže dovoliť jednému tenantovi vyčerpať všetku kapacitu.

## 5. Weighted cost

Request count nie je vždy vhodná jednotka.

```text
GET operation status       = 1 unit
create settlement          = 8 units
bulk settlement of 100     = 400 units
reconciliation export      = 1 000 units
```

Cost môže vychádzať z:

- očakávaného CPU alebo I/O;
- počtu records;
- provider calls;
- payload size;
- fan-out;
- lock duration;
- monetary alebo abuse risku.

Cost odhadnutý až po drahom parse alebo database lookup-e nechráni pred front-door exhaustion. Lacná admission identity a hrubý cost musia byť dostupné včas; presnejší cost možno aplikovať na ďalšej boundary.

## 6. Fixed window

Počíta requests v pevnom časovom okne.

```text
12:00:00–12:00:59 → 1 000 requests
12:01:00–12:01:59 → nový counter
```

Výhody:

- jednoduchý;
- lacný;
- ľahko distribuovateľný.

Nevýhoda je boundary burst:

```text
999 requests o 12:00:59
+ 1 000 requests o 12:01:00
→ 1 999 requests približne za jednu sekundu
```

Ak downstream nezvládne tento burst, fixed-window limit je formálne dodržaný a operationally nesprávny.

## 7. Sliding window

### Sliding log

Uchováva timestamps jednotlivých requests a presne počíta interval končiaci teraz. Je presný, ale state a cleanup cost rastú s trafficom.

### Sliding-window counter

Kombinuje current a previous bucket podľa prekryvu. Je lacnejší a približný.

Approximation musí byť súčasťou contractu. Pri hard financial alebo security limite môže byť potrebný konzervatívny verdict; pri abuse protection môže byť malá odchýlka prijateľná.

## 8. Token bucket

Token bucket modeluje sustained rate a burst:

```text
tokens pribúdajú rýchlosťou r
bucket capacity = B
request cost = c
admit ak tokens >= c
```

Príklad:

```text
refill: 100 units/s
capacity: 500 units
```

Dlhodobý priemer je približne 100 units/s, ale idle client môže krátko použiť burst 500 units.

Dôležité je rozlíšiť:

- configured capacity bucketu;
- current token state;
- clock a refill generation;
- distributed replicas countera;
- downstream burst tolerance.

Burst capacity nesmie byť iba násobok podľa želanej user experience. Musí byť absorbovateľná queues, pools a providerom.

## 9. Leaky bucket a paced admission

Leaky-bucket model vyrovnáva output na približne konštantnú rýchlosť. Request môže byť:

- zaradený do bounded queue;
- oneskorene admitted;
- odmietnutý po naplnení queue alebo deadline-u.

Pacing znižuje burst, ale pridáva queue latency. Queue bez hard boundu iba presunie overload do memory a predĺži čas do failure-u.

```text
arrival rate > drain rate počas dlhého času
→ queue rastie
→ deadline expiruje
→ stale work a retries
→ overload amplification
```

## 10. Local a distributed limiter

### Local limiter

Každý process alebo Pod drží vlastný counter.

Ak je limit `L` per instance a existuje `N` instances:

```text
effective aggregate limit ≈ N × L
```

Autoscaling preto mení effective policy. Rolling deployment môže dočasne zvýšiť počet instances a tým limit.

Local limiter je vhodný ako:

- posledná ochrana processu;
- approximate shard budget;
- defense-in-depth pod global admission.

Nie je automaticky global tenant quota.

### Centralized limiter

Jeden logical counter alebo strongly coordinated service poskytuje spoločný verdict. Prináša:

- presnejšiu globálnu policy;
- dodatočnú latency a dependency;
- hotspot risk;
- partition a fail-open/fail-closed rozhodnutie.

### Sharded alebo leased limiter

Global budget sa rozdelí medzi instances:

```text
global 10 000 units/s
→ Pod A lease 120
→ Pod B lease 140
→ ...
```

Unused leases, membership changes a reconnects môžu vytvoriť underutilization alebo overshoot. Lease generation a reclaim musia byť explicitné.

## 11. Consistency limit countera

Nie každý limiter potrebuje linearizable counter. Potrebný model závisí od rizika.

### Approximate limit

Mierny overshoot je prijateľný; preferuje dostupnosť a nízku latency.

Použitie:

- soft API fairness;
- telemetry sampling;
- non-critical background refresh.

### Hard limit

Prekročenie môže porušiť provider quota, financial risk alebo security boundary.

Použitie:

- paid quota;
- scarce license;
- compliance export;
- critical provider concurrency.

Hard limit potrebuje autoritatívny counter, reservation/commit semantics alebo konzervatívny partition behavior. `Redis INCR` v jednom node môže byť atomic command, ale celý distributed failover/persistence contract musí stále preukázať, ktoré increments prežili a ktoré clients dostali acknowledgement.

## 12. Admission outcome

Limiter nemusí iba povoliť alebo odmietnuť.

Možné outcomes:

- **admit** — operation môže pokračovať;
- **delay** — bounded queue/pacing, ak deadline dovolí;
- **degrade** — lacnejší alebo stale-safe response;
- **shed** — zahodiť optional work;
- **reject** — caller dostane truthful retry contract;
- **reserve** — kapacita sa drží pre high-priority alebo recovery operation.

Status lookup, cancellation a reconciliation nemajú byť blokované rovnakou vyčerpanou create quota, inak preťažený systém znemožní klientom bezpečne zistiť outcomes.

## 13. HTTP contract

RFC 6585 definuje `429 Too Many Requests` pre situáciu, keď user poslal príliš veľa requests v danom čase. Response môže obsahovať `Retry-After`.

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 12
Content-Type: application/problem+json

{
  "type": "urn:atlas:problem:rate-limit",
  "status": 429,
  "limit_scope": "merchant-provider-create",
  "retryable": true
}
```

`Retry-After` môže byť počet sekúnd alebo HTTP date. Client ho nemá interpretovať ako garanciu budúceho prijatia; je to minimum alebo guidance podľa server contractu.

Aktívny IETF Internet-Draft `RateLimit header fields for HTTP` z mája 2026 navrhuje `RateLimit-Policy` a `RateLimit` fields. Je to work in progress, nie finálny RFC. Implementácia musí preto versionovať svoj wire contract a nesmie predstierať štandard, ktorý ešte nebol publikovaný.

## 14. Retry interaction

Rate-limited response bez client guidance môže vytvoriť synchronizovaný retry storm.

```text
10 000 clients dostane 429
→ všetky retry po 1 s
→ ďalší burst 10 000
```

Potrebné controls:

- `Retry-After` alebo explicitný next-attempt hint;
- exponential backoff;
- jitter;
- aggregate retry budget;
- stable logical-operation identity;
- server-side dedupe/idempotency;
- client-side concurrency cap.

Limiter musí rozhodnúť, či rejected attempt spotreboval quota. Nejasná policy môže viesť k client/server disagreementu.

## 15. Priority a rezervovaná kapacita

Priority classes môžu byť legitímne:

```text
P0: cancellation a unknown-outcome lookup
P1: interactive settlement create
P2: scheduled merchant batch
P3: rebuildable projection/backfill
```

Riziká:

- starvation nižšej priority;
- každý caller sa označí ako high priority;
- priority inversion cez shared pool;
- recovery traffic nemá reserve;
- high-priority queue obíde fairness.

Priority musí byť odvodená z authenticated business role a enforced na každej relevantnej queue/pool boundary.

## 16. Security a abuse

Rate limiting môže zmierniť abuse, ale nenahrádza:

- authentication;
- authorization;
- input validation;
- WAF/DDoS protection;
- cost controls;
- anomaly detection.

Limiter identity nesmie dôverovať neoverenému `X-Forwarded-For`. Rate-limit responses a headers nemajú odhaľovať citlivú global capacity alebo usage iného tenanta.

Pri extrémnom attack trafficu môže byť odpovedanie na každý request drahšie než connection drop alebo upstream filtering. RFC 6585 výslovne nevyžaduje, aby server vždy generoval `429`.

## 17. Connected incident `DB-PAY-60`

Release `payments 8.4` otvoril partnerom bulk replay po 47-minútovom provider outage-i. Gateway fleet mal `80` Podov a každý Pod vlastný token bucket:

```text
sustained limit per Pod: 450 requests/s
burst per Pod:           900 requests
fleet sustained limit:   36 000 requests/s
fleet immediate burst:   72 000 requests
```

Safe downstream envelopes boli:

```text
PostgreSQL settlement+outbox: 9 000 logical operations/s
provider P2 new attempts:     6 500 attempts/s
final-result persistence:     7 200 results/s
```

Limiter počítal raw HTTP attempts, nemal tenant/provider hierarchy a nerozlišoval create od status lookupu. Po autoscale na 80 Podov sa configured `450 req/s` interpretovalo ako service limit, hoci bolo per Pod.

Partner replay dosiahol `21 600 requests/s`; normal traffic bol približne `3 200 requests/s`. Počas 14 minút:

- gateway prijala `6.9 milióna` requests;
- `71 %` admitted create capacity spotreboval jeden partner;
- provider backlog age vzrástol na `54 minút`;
- status a reconciliation requests súťažili s new creates;
- local buckets vracali `429` bez `Retry-After`;
- partner SDK opakoval request po fixných `100 ms`;
- HTTP-attempt amplification dosiahla `2.4×`;
- provider pool a settlement DB pool sa saturovali napriek tomu, že väčšina Pod-local limiterov nebola trvalo vyčerpaná.

### Konkurenčné hypotézy

1. Provider P2 má nižšiu kapacitu než deklaruje.
2. Kafka broker nevie ingestovať admission rate.
3. Database commit path je bottleneck.
4. Limiter je global, ale counter replication laguje.
5. Limiter je local a jeho effective fleet limit sa násobí počtom Podov.
6. Jeden tenant vyčerpal shared budget bez fairness boundary.

### Diskriminačné dôkazy

```text
configured per-Pod rate × ready Pod count
→ 450 × 80 = 36 000 requests/s
```

Gateway metrics ukázali samostatné bucket states pre každý Pod. Neexistoval global counter ani provider budget. Provider P2 saturation začínala približne pri `6 500 attempts/s`, teda hlboko pod fleet admission limitom.

Per-tenant breakdown ukázal `71 %` admitted creates z jedného partnera. Status endpoint mal rovnaký token cost ako create a nemal reserve. `429` responses neniesli retry timing, pričom SDK mala hard-coded 100-ms retry.

### Primary rate-limiting root cause

> Admission policy bola process-local request counter bez fleet, tenant, operation-cost a downstream-provider capacity contractu.

Provider slowdown bol trigger. Autoscaling, no-jitter retries, shared priority a chýbajúci status/recovery reserve boli causal amplifiers.

## 18. Containment a authoritative redesign

Containment:

```text
stop bulk replay
→ preserve per-tenant/Pod admission evidence
→ publish bounded Retry-After
→ reserve status/reconciliation capacity
→ cap provider P2 in-flight attempts
→ reduce create admission pod safe completion rate
```

Target hierarchy:

```text
global settlement envelope
→ provider + Region envelope
→ tenant weighted share
→ operation class
→ per-client burst
```

Pre provider P2:

```text
safe new-attempt rate: 5 800/s
hard in-flight cap:     1 200
recovery reserve:       15 %
status/reconciliation:  independent reserved budget
```

Limiter používa logical operation cost. Duplicate HTTP attempt so známym idempotency keyom najprv číta existujúci operation outcome a nemá byť účtovaný ako nový expensive create.

Admission controller sleduje:

- admitted logical rate;
- current in-flight;
- backlog age, nie iba depth;
- provider latency a unknown outcomes;
- database pool wait;
- tenant fairness;
- rejected/delayed/degraded outcomes;
- retry-after compliance;
- completion rate a final business success.

## 19. Rate-limiting acceptance verdict

Rate limiting je prijatý, keď:

- exact business operation, caller, tenant, provider, Region a generation sú explicitné;
- limit units a request costs zodpovedajú workloadu;
- configured local a effective fleet/global limits sú rozlíšené;
- downstream safe rate, concurrency a burst envelope sú zmerané;
- global, provider, tenant a operation-class budgets vytvárajú fairness;
- priority a recovery reserves sú authenticated a enforced;
- distributed counter consistency a partition behavior sú explicitné;
- `429`, `Retry-After` a retry semantics sú truthful;
- limiter nesmie blokovať safe status, cancellation a reconciliation paths;
- admission reaguje aj na backlog age, in-flight a completion capacity;
- autoscale, rolling update, counter failure, burst a one-tenant flood tests prejdú;
- forbidden starvation, global overshoot, retry storm a false-admission outcomes sú odmietnuté.

## 20. Troubleshooting flow

```text
429 storm, unfairness alebo downstream overload
→ exact admission subject a business operation
→ caller/tenant/provider/Region identity
→ configured limit vs effective fleet/global limit
→ algorithm, window, token/counter generation
→ request cost a logical/physical attempt mapping
→ downstream rate/concurrency/backlog envelope
→ rejection/delay/retry contract
→ fairness a priority reserves
→ completion/business outcome
→ second-burst/autoscale validation
```

## 21. Anti-patterny

### Limit je 500 req/s

Bez scope-u, keyu, costu a distributed topology je číslo neoveriteľné.

### Per-Pod limiter škáluje s aplikáciou

Škáluje aj effective admission, čo môže zničiť shared dependency.

### IP je user

NAT môže trestať mnoho users alebo umožniť jednému clientovi limit obísť.

### Všetky requesty stoja jeden token

Bulk alebo side-effecting request môže byť rádovo drahší než status query.

### `429` vyrieši overload

Client bez backoffu, jitteru a retry budgetu môže vytvoriť väčší load.

### Queue je rate limiter

Unbounded queue iba odloží failure a zvyšuje stale work.

### High priority obíde limit

Bez hard reserve a authority môže high-priority traffic vyčerpať celý systém.

### Rate limiting je backpressure

Limiter riadi admission podľa policy; backpressure prenáša downstream demand/capacity späť upstream. Môžu spolupracovať, ale nie sú totožné.

## 22. Kontrolné otázky

1. Čo tvorí exact rate-limiting subject?
2. Ako sa rate limit líši od quota a concurrency limitu?
3. Prečo per-Pod limit nie je global limit?
4. Aký burst vytvára fixed-window boundary?
5. Ako token bucket modeluje sustained rate a burst?
6. Kedy je approximate distributed counter prijateľný?
7. Prečo IP nemusí byť správny fairness key?
8. Ako weighted request cost mení policy?
9. Čo má obsahovať truthful `429` response?
10. Prečo limiter v `DB-PAY-60` nechránil provider P2?
11. Prečo status a reconciliation potrebujú reserve?
12. Čo overuje rate-limiting acceptance verdict?

## Glossary impact

Relevantné pojmy: rate-limiting subject, admission control, quota, concurrency limit, capacity envelope, limiting key, weighted request cost, fixed window, sliding log, sliding-window counter, token bucket, leaky bucket, local limiter, global limiter, leased budget, distributed counter consistency, burst allowance, priority reserve, retry-after contract, fairness verdict a rate-limiting acceptance verdict.

## Primárne zdroje

- [RFC 6585 — Additional HTTP Status Codes](https://www.rfc-editor.org/rfc/rfc6585.html)
- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [IETF HTTPAPI — RateLimit header fields for HTTP, draft-11](https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/)
- [gRPC — Status Codes](https://grpc.io/docs/guides/status-codes/)
