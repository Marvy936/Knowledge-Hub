# Idempotency a backpressure

Idempotency chráni logical operation pred opakovaným vykonaním. Backpressure chráni spracovateľský graph pred tým, aby upstream vytváral viac práce, než downstream dokáže bezpečne dokončiť.

Ani jeden mechanizmus sám nestačí. Idempotentný systém môže skolabovať pod nekonečným počtom duplicate attempts. Backpressured systém môže zase spracovať každý duplicate presne raz ako novú logical operation, ak nemá stable identity a equivalence contract.

## 1. Dominantný model

```text
business operation a completion-capacity objective
→ exact idempotency/backpressure subject
→ stable operation identity a payload fingerprint
→ atomic claim a operation state machine
→ bounded demand, queue a in-flight credits
→ side effect a durable result
→ duplicate, replay alebo overflow verdict
→ acknowledgement, retry a reconciliation
→ retention, drain a recovery
→ second-delivery a sustained-overload validation
```

Correctness sa hodnotí na logical operation a business effecte. Capacity sa hodnotí na celom source-to-sink flowe, nie iba na jednom queue alebo process memory grafe.

## 2. Idempotentná operation

Operation je idempotentná, ak opakované vykonanie rovnakého intentu nevytvorí ďalší odlišný intended effect.

```text
apply(op) raz
≈
apply(op) viackrát
```

To neznamená, že každý physical attempt:

- vykoná nulovú prácu;
- vráti byte-identical response;
- nevytvorí nové logs/metrics/audit records;
- nemôže zlyhať;
- nemá concurrency races.

Rozhodujúci je authoritative business outcome.

## 3. HTTP method idempotency vs. business idempotency

RFC 9110 označuje method ako idempotentnú, ak intended effect viacerých identických requests je rovnaký ako effect jedného requestu. `PUT` a `DELETE` sú štandardne idempotentné methods; `POST` nie je automaticky idempotentný.

Method semantics však nestačia:

```text
PUT /balance/merchant-7
{"balance": 100}
```

môže byť idempotentný replacement, zatiaľ čo:

```text
PUT /accounts/merchant-7/charge
{"amount": 100}
```

môže byť business-neidempotentný, ak server interpretuje každý request ako nový charge napriek method name.

Naopak `POST /settlements` môže byť business-idempotentný cez explicitný key a operation registry.

## 4. Exact idempotency subject

Idempotency subject zahŕňa:

- tenant/merchant/account identity;
- API operation alebo command type;
- client-provided idempotency key alebo business operation ID;
- normalized payload fingerprint;
- relevant headers, currency, amount a target identity;
- operation schema/version;
- authoritative operation record;
- current lifecycle state a owner generation;
- downstream event/provider identity;
- retention a expiry contract;
- response replay a conflict semantics.

Samotný UUID nie je idempotency contract.

## 5. Key scope

Key musí byť unique v správnom namespace.

Príklad:

```text
(tenant_id, operation_type, idempotency_key)
```

Príliš úzky scope:

```text
idempotency_key iba global
```

môže vytvoriť cross-tenant collision.

Príliš široký alebo meniaci sa scope:

```text
(operation_id generated serverom pri každom retryi)
```

nevie rozpoznať opakovaný client intent.

Key má zostať rovnaký pre retries tej istej logical operation a nesmie sa použiť pre iný intent.

## 6. Payload fingerprint

Server musí rozhodnúť, či rovnaký key reprezentuje rovnaký intent.

Fingerprint môže zahŕňať:

```text
HTTP method
+ canonical path/operation type
+ tenant
+ normalized semantic payload
+ currency/amount/recipient
+ schema generation
```

Rovnaký key a rovnaký fingerprint:

- vráti existujúci operation status/result;
- nepridá nový business effect.

Rovnaký key a odlišný fingerprint:

- musí byť explicitný conflict;
- nesmie ticho vrátiť starý response ani prepísať operation.

Raw-body hash môže byť príliš citlivý na field order alebo nepodstatné metadata. Fingerprint sa má odvodiť zo semantic intentu po bezpečnej canonicalization.

## 7. Atomic claim

Anti-pattern:

```text
SELECT key
→ none
→ create operation
→ INSERT key mapping
```

Dva concurrent requests môžu oba prečítať `none`.

Správny claim potrebuje atomic primitive:

- unique constraint + `INSERT ... ON CONFLICT`;
- compare-and-swap;
- serializable transaction;
- conditional write;
- linearizable key reservation.

Pre settlement command core:

```text
BEGIN
→ claim (tenant, operation_type, key, fingerprint)
→ create settlement operation
→ create outbox event
→ persist initial idempotency state
COMMIT
```

Claim a authoritative operation nesmú byť independently acknowledged.

## 8. Idempotency state machine

Binary `seen/not seen` nestačí.

Praktický lifecycle:

```text
ABSENT
→ CLAIMED
→ ACCEPTED_DURABLE
→ PROCESSING
→ COMPLETED
   alebo FAILED_FINAL
   alebo RECONCILIATION_REQUIRED
```

Každý state potrebuje:

- owner/generation;
- created a updated timestamps;
- request fingerprint;
- authoritative operation ID;
- last durable evidence;
- response/status representation;
- takeover/recovery rule.

`CLAIMED` po process crash-i nesmie zostať permanentne blokujúci ani byť automaticky považovaný za safe-to-repeat. Lease expiry môže povoliť takeover processingu, nie vytvorenie novej logical operation.

## 9. Concurrent duplicate behavior

Druhý request môže prísť, keď prvý je stále processing.

Možné contracts:

- vrátiť `202` a rovnaký status resource;
- bounded wait na current result;
- vrátiť `409/425` podľa API contractu;
- pripojiť sa ako observer k existujúcej operation.

Nesmie bez dôkazu:

- vytvoriť druhý operation ID;
- spustiť nový provider attempt;
- prepísať fingerprint;
- označiť operation failed iba preto, že prvý response ešte neexistuje.

## 10. Idempotency retention

TTL nie je iba cache tuning.

Retention musí pokryť minimálne:

```text
max client retry horizon
+ max queue/backlog age
+ provider unknown-outcome reconciliation
+ replay/recovery window
+ business dispute alebo support requirement
```

Ak key expiruje skôr než operation dosiahne terminal/reconciled state, retry sa môže stať novou logical operation.

Terminal records možno archivovať alebo compactovať, ale authority potrebná na duplicate verdict musí zostať dostupná počas contract window-u.

## 11. Response replay

Idempotency registry môže uchovávať:

- exact operation ID;
- current status URL;
- selected response fields;
- final result digest;
- HTTP status generation;
- completion timestamp.

Nie každý duplicate musí dostať byte-identical response. Môže dostať current truthful status, ale response musí odkazovať na rovnakú logical operation a rovnaký business outcome.

Sensitive response body sa nemá slepo ukladať bez data-classification, encryption a retention pravidiel.

## 12. Stable identity cez distributed flow

Jedna logical operation potrebuje identity chain:

```text
client idempotency key
→ authoritative operation_id
→ outbox event_id
→ broker message identity
→ consumer processing record
→ provider idempotency key
→ final-result event
```

Nie všetky IDs musia byť rovnaké, ale mapping musí byť durable a queryable.

Provider idempotency key odvodený z `attempt_id` je chybný:

```text
attempt 1 → provider-key-A
attempt 2 → provider-key-B
```

Provider vidí dve nezávislé operations.

Stabilnejšie:

```text
provider key = tenant + business operation identity + effect type
```

## 13. Idempotent consumer

At-least-once delivery znamená, že consumer musí očakávať duplicate messages.

Pattern:

```text
BEGIN
→ INSERT processed_message(consumer, event_id) UNIQUE
→ apply local state transition
→ write result/outbox
COMMIT
```

Ak unique claim už existuje, consumer načíta authoritative prior outcome.

Processed-message table sama nestačí pri external side effecte. Ak provider call nastane mimo local transaction, treba:

- stable provider idempotency key;
- durable attempt state;
- unknown-outcome lookup;
- reconciliation pred retryom.

## 14. Exactly-once scope

End-to-end `exactly once` nie je magická broker property.

Treba presne pomenovať scope:

- exactly-once record processing v jednej Kafka transaction;
- one committed database transition per event ID;
- one provider financial effect per business key;
- one user-visible notification;
- one final reconciled business outcome.

Transaction v brokeri nemôže sama atomicky zahrnúť arbitrary external provider bez spoločného transaction protocolu. Correctness preto vzniká kombináciou stable identity, atomic local transitions, idempotent destinations a reconciliation.

## 15. Čo je backpressure

Backpressure je feedback, ktorým downstream vyjadruje, koľko ďalšej práce dokáže prijať.

```text
source production
→ demand/credit signal from sink
→ bounded emission
```

Cieľom nie je nulová queue. Cieľom je bounded memory, bounded in-flight work, truthful latency a kontrolovateľný overload outcome.

Reactive Streams napríklad vyžaduje, aby Publisher neposlal viac elements, než Subscriber požiadal. Kafka consumer umožňuje assigned partitions `pause()` a neskôr `resume()`, ale pause state sa po rebalance automaticky nezachováva.

## 16. Backpressure vs. rate limiting

### Rate limiting

Policy rozhoduje, koľko práce môže určitý caller alebo class vytvoriť za čas.

### Backpressure

Runtime downstream capacity rozhoduje, koľko práce môže upstream aktuálne posunúť.

### Circuit breaker

Dočasne zastavuje calls do dependency, ktorej failure/latency prekročila threshold.

### Queue

Absorbuje bounded rozdiel medzi arrival a service rate.

Mechanizmy spolupracujú:

```text
downstream credits klesnú
→ backpressure signal
→ admission rate sa zníži
→ optional work sa shedne
→ breaker môže otvoriť pre failed dependency
```

## 17. Little's Law a in-flight work

Približný vzťah:

```text
in-flight work ≈ throughput × average duration
```

Ak provider throughput zostane `5 000/s`, ale duration vzrastie zo `100 ms` na `2 s`:

```text
500 in-flight
→ 10 000 in-flight
```

Bez concurrency capu môže latency increase vyčerpať:

- threads/tasks;
- connections;
- memory;
- ephemeral ports;
- provider quota;
- retry budget.

Rate môže zostať rovnaká a systém napriek tomu skolabuje na concurrency.

## 18. Bounded queues

Každá queue potrebuje:

- exact owner a purpose;
- item identity a cost;
- hard capacity;
- age/deadline limit;
- admission a overflow policy;
- priority/fairness;
- persistence/durability semantics;
- drain rate a recovery target;
- observability.

Queue depth bez age je neúplná. Tisíc 5-ms jobs a tisíc 30-minútových financial operations nemajú rovnaký impact.

Unbounded queue:

```text
arrival > completion
→ hidden latency
→ deadline expiry
→ retries
→ stale work
→ memory exhaustion
```

## 19. Push a pull flow

### Pull/credit model

Consumer žiada presný počet items alebo drží permit/semaphore.

```text
available provider slots = 120
→ request/poll max 120 relevant records
```

### Push model

Producer posiela bez explicitného downstream demandu. Receiver musí:

- reject;
- drop podľa contractu;
- buffer bounded amount;
- spill do durable queue;
- signal slowdown iným channelom.

Zdroj, ktorý nemožno spomaliť, stále potrebuje overflow policy. `Buffer everything` nie je backpressure.

## 20. Kafka consumer backpressure

Consumer môže:

- obmedziť `max.poll.records`;
- držať bounded worker permits;
- pause assigned partitions pri nulových credits;
- pokračovať v `poll()` podľa group/liveness contractu;
- resume iba partitions s dostupnou downstream capacity;
- commitovať offset až po required durable outcome-e.

Dôležitý caveat:

> Kafka pause/resume state sa po rebalance nezachováva.

Assignment callback preto musí znovu odvodiť pause state z current credits a recovery policy. Inak rebalance nečakane obnoví plnú consumption rate.

## 21. Hidden buffers

Backpressure audit musí zahŕňať:

- client SDK queue;
- load balancer pending requests;
- HTTP/2 alebo gRPC stream flow-control windows;
- server accept/request queue;
- executor/task queue;
- database connection pool waiters;
- producer buffer;
- broker partitions;
- consumer fetch buffer;
- retry topic;
- provider client pool;
- result persistence queue.

Bounded queue na jednej vrstve nepomôže, ak pred ňou alebo za ňou existuje unbounded buffer.

## 22. Overflow policies

Keď capacity nie je dostupná, systém musí zvoliť explicitný outcome:

- reject new create;
- delay s bounded deadline;
- drop rebuildable telemetry;
- sample optional events;
- coalesce redundant refreshes;
- use latest-only state pre superseding updates;
- spill durable work;
- degrade na read-only/status mode;
- cancel stale work;
- route do delayed retry queue.

Pre financial command nemožno silent drop použiť. Pre rapidly superseded metrics môže byť latest-only alebo sampling správne.

## 23. Priority, fairness a starvation

Backpressure iba podľa global queue môže nechať bulk tenant zablokovať interactive users.

Hierarchický scheduler:

```text
global downstream credits
→ provider/Region credits
→ tenant weighted fair queue
→ operation priority
→ per-operation deadline
```

Status, cancellation a reconciliation potrebujú reserve. Batch replay sa môže spomaliť bez toho, aby znemožnil zistiť outcome už accepted operations.

Starvation test musí overiť, že low-priority work stále dostane bounded progress po odznení overloadu.

## 24. Feedback oscillation

Príliš agresívny feedback môže oscilovať:

```text
queue high
→ pause all
→ queue drains
→ resume all
→ burst
→ queue high
```

Potrebné sú:

- high/low watermarks;
- hysteresis;
- gradual credit increase;
- bounded probes;
- smoothed completion rate;
- minimum hold time;
- jitter medzi consumers.

Recovery throughput sa má zvyšovať postupne a podľa final completion, nie iba podľa nižšej queue depth.

## 25. Connected incident `DB-PAY-60`

Rate-limiting defect dovolil bulk replayu prejsť do durable settlement/outbox pathu rýchlejšie než provider dokázal dokončovať operations.

Idempotency implementation používala samostatný shared service:

```text
SELECT idempotency key
→ ak absent, generate new operation_id
→ commit settlement + outbox
→ autocommit INSERT key → operation mapping
```

Registry key bol iba:

```text
merchant_id + idempotency_key
```

Nemal payload fingerprint ani operation/schema generation. Cleanup mazal records `20 minút` po `first_seen`, aj keď operation bola stále `PROCESSING` alebo backlogovaná. Provider idempotency key sa odvodzoval z internal `operation_id`, takže duplicate logical operation dostala nový provider key.

Počas 14-minútového admission burstu a následného drainu:

- partner poslal `12 480` duplicate submissions s rovnakými business operation IDs;
- `1 906` retries prišlo po 20-minútovej registry expiry;
- `143` concurrent duplicate pairs prešlo cez check-before-insert race;
- `83` duplicate authoritative operations vzniklo s odlišnými operation IDs;
- `31` duplicate provider effects bolo potvrdených;
- `29` bolo automaticky reversed;
- `2` vyžadovali manuálnu merchant remediation.

### Backpressure topology

Provider fleet mal `48` worker Podov:

```text
max async in-flight per Pod: 2 000
fleet theoretical in-flight: 96 000
provider safe in-flight:     1 200
Kafka max.poll.records:       500
```

Worker po `poll()` vložil records do prakticky unbounded async executor queue. Partitions sa pause-li až pri heap utilization nad `85 %`, nie podľa provider credits alebo queue age. Po rebalance sa pause state neobnovil.

Dôsledky:

- Kafka backlog dosiahol `2.7 milióna` commands;
- oldest-command age dosiahol `54 minút`;
- across-fleet executor queues obsahovali približne `348 000` tasks;
- `17` worker Podov skončilo OOM killom;
- provider connection pool wait p99 dosiahol `11.2 s`;
- retry records sa vracali bez dostatočného delayu;
- API pokračovalo v durable acceptance, pretože admission nečítala downstream credits ani backlog age.

### Konkurenčné hypotézy

1. Kafka stratila records.
2. Provider idempotency nefungovala.
3. Idempotency TTL cleanup bol bezpečný, lebo request window je 20 minút.
4. Duplicate operations vznikli iba client bugom.
5. Consumer pause chránil fleet, ale metrics boli oneskorené.
6. Backlog bol veľký, no workers mali stále dostatočnú completion capacity.

### Diskriminačné dôkazy

Operation equivalence graph ukázal rovnaký merchant business ID a semantic payload mapovaný na viac internal operation IDs. Registry audit ukázal cleanup pred terminal outcome-om. Concurrent traces zachytili dva successful `SELECT absent` pred samostatnými settlement commits.

Provider ledger ukázal odlišné provider idempotency keys odvodené z odlišných internal operation IDs, preto provider nemohol duplicate effects spojiť.

Consumer evidence ukázala:

```text
assigned partitions
→ poll 500 records
→ executor queue bez hard permitu
→ provider pool wait
→ heap 85 %
→ pause
→ rebalance
→ pause state lost
→ poll resumes
```

Backlog age a in-flight rástli, hoci broker publication a offset storage boli healthy.

### Primary idempotency root cause

> Idempotency claim nebol atomic s authoritative operation, nemal semantic fingerprint a expiroval skôr než operation/reconciliation lifecycle.

### Primary backpressure root cause

> Upstream admission, consumer polling a executor submission neboli riadené downstream completion credits; buffers a theoretical in-flight concurrency boli rádovo väčšie než safe provider envelope.

## 26. Evidence-preserving containment

```text
stop partner bulk admission
→ preserve registry cleanup, operation, outbox, consumer a provider evidence
→ reserve status/cancellation/reconciliation paths
→ set provider P2 hard in-flight cap
→ pause partitions podľa current credits
→ classify duplicate-equivalence groups
→ provider lookup pred ďalším attemptom
→ reverse confirmed duplicate effects
→ drain oldest safe operations first
```

Operations boli klasifikované:

- one operation, one effect;
- duplicate submission mapped na same operation;
- duplicate operation, provider-never-sent;
- duplicate operation, one provider effect;
- duplicate operation, multiple provider effects;
- sent-unknown;
- final-failed;
- reconciliation-required.

Broad replay bez tejto klasifikácie by vytvoril ďalšie effects.

## 27. Authoritative idempotency redesign

Idempotency registry je súčasťou settlement command-core PostgreSQL transaction:

```text
BEGIN
→ INSERT idempotency_claim
   UNIQUE (tenant_id, operation_type, key)
→ compare semantic fingerprint
→ create alebo load authoritative operation
→ insert settlement/outbox iba pri novom claim-e
COMMIT
```

Behavior:

```text
same key + same fingerprint + terminal
→ return same operation/result

same key + same fingerprint + processing
→ return 202 + same status resource

same key + different fingerprint
→ reject conflict

unknown prior outcome
→ lookup/reconcile, nevytvárať nový operation
```

Provider key:

```text
provider_idempotency_key
= tenant + merchant_business_operation_id + effect_type
```

Registry record sa nemaže podľa jednoduchého `first_seen TTL`. Retention pokrýva client retry, max backlog, restore/replay a provider reconciliation window. Non-terminal alebo reconciliation-required record nemôže expirovať do absent state-u.

## 28. Authoritative backpressure redesign

Provider P2 capacity contract:

```text
hard provider in-flight: 1 200
worker Pods:              48
base permits per Pod:     25
poll batch:               max 50, ďalej bounded dostupnými permits
executor queue:           hard bound 100 per Pod
```

Control loop:

```text
provider completions uvoľnia credits
→ consumer poll/pause podľa credits
→ bounded executor admission
→ offset commit po durable outcome
→ backlog age feeds API admission
→ gradual recovery with hysteresis
```

Backlog policy:

```text
age < 5 min
→ normal weighted admission

5–15 min
→ throttle bulk, preserve interactive/status

> 15 min
→ reject new bulk creates with Retry-After
→ preserve cancellation/status/reconciliation

unknown-outcome spike
→ stop new provider attempts for affected key
→ lookup/reconcile first
```

Assignment callback po rebalance znovu aplikuje pause state podľa provider/tenant credits. Retry topics majú explicitný delay a rovnakú stable operation identity; retry nesmie obísť original quota alebo priority class.

## 29. Idempotency/backpressure acceptance verdict

Návrh je prijatý, keď:

- exact logical operation, tenant, key scope a semantic fingerprint sú explicitné;
- key claim a authoritative operation vznikajú atomic alebo cez preukázaný conditional protocol;
- same-key/same-payload, same-key/different-payload a concurrent duplicate outcomes sú definované;
- operation state machine rozlišuje accepted, processing, completed, failed-final a reconciliation-required;
- retention pokrýva retry, backlog, replay a provider reconciliation lifecycle;
- stable identity prechádza cez outbox, broker, consumer a provider effect;
- exactly-once tvrdenie má presný scope;
- všetky queues, buffers, pools a in-flight boundaries majú hard bounds;
- downstream demand/credits riadia upstream poll, executor a admission;
- backlog age, deadlines, fairness a priority reserves sú explicitné;
- rebalance/reconnect obnoví pause a credit state bezpečne;
- overflow policy zodpovedá business data classu;
- sustained overload, duplicate concurrency, lost response, stale key, rebalance a drain tests prejdú;
- forbidden duplicate financial effect, silent loss, unbounded memory, starvation a false-completed outcomes sú odmietnuté.

## 30. Troubleshooting flow

```text
duplicate effect, growing backlog alebo OOM
→ exact logical operation a semantic fingerprint
→ idempotency key scope/state/retention
→ atomic claim a concurrent history
→ operation/event/provider identity chain
→ authoritative effect/result evidence
→ source arrival vs sink completion rate
→ queue/buffer/in-flight inventory
→ credits, pause/resume a rebalance state
→ overflow/retry/priority behavior
→ reconciliation a bounded drain
→ duplicate/overload second test
```

## 31. Anti-patterny

### Idempotency key = UUID

Bez scope-u, fingerprintu, atomic claimu, lifecycle-u a retention nie je UUID correctness mechanism.

### `SELECT` potom `INSERT`

Bez uniqueness/serialization môže concurrent duplicate vytvoriť dve operations.

### Key môže expirovať po 15 minútach

Nie ak backlog alebo provider reconciliation trvá dlhšie.

### Provider key podľa attempt ID

Každý retry sa providerovi javí ako nový effect.

### Kafka exactly once vyrieši provider call

Broker transaction nezahŕňa arbitrary external side effect bez spoločného protocolu.

### Queue absorbuje burst

Iba ak je bounded, má deadline a drain capacity. Inak absorbuje failure do budúcnosti.

### Pause pri 90 % heap

Je to neskorý memory symptom, nie downstream demand contract.

### `max.poll.records` je concurrency limit

Records môžu byť presunuté do iného unbounded executora.

### Rate limiting je backpressure

Rate policy nemusí poznať current downstream state. Backpressure musí prenášať effective capacity feedback.

### Po poklese queue depth je recovery hotová

External unknown outcomes, duplicate effects a stale operations môžu zostať.

## 32. Kontrolné otázky

1. Ako sa HTTP method idempotency líši od business idempotency?
2. Čo tvorí exact idempotency subject?
3. Prečo key potrebuje semantic fingerprint?
4. Ako sa atomic claim implementuje?
5. Aké states potrebuje idempotency record?
6. Ako sa správa concurrent duplicate počas processingu?
7. Z čoho sa odvodzuje retention window?
8. Prečo provider key nesmie vychádzať z attempt ID?
9. Ako exactly-once scope súvisí s external effectom?
10. Čo je backpressure a ako sa líši od rate limitu?
11. Prečo queue depth bez age nestačí?
12. Ako Kafka rebalance ovplyvní pause state?
13. Ktoré hidden buffers treba inventarizovať?
14. Prečo `DB-PAY-60` vytvoril duplicate effects aj OOM?
15. Čo musí overiť idempotency/backpressure acceptance verdict?

## Glossary impact

Relevantné pojmy: idempotency subject, business idempotency, idempotency key scope, semantic payload fingerprint, atomic idempotency claim, idempotency state machine, duplicate join, idempotency retention, response replay, operation identity chain, idempotent consumer, exactly-once scope, backpressure subject, downstream credit, bounded queue, queue age, hidden buffer, overflow policy, flow-control window, consumer pause state, demand propagation, feedback hysteresis, bounded drain a idempotency/backpressure acceptance verdict.

## Primárne zdroje

- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [IETF HTTPAPI — The Idempotency-Key HTTP Header Field, draft-07](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/)
- [Reactive Streams Specification for the JVM](https://github.com/reactive-streams/reactive-streams-jvm)
- [Apache Kafka 4.1 — KafkaConsumer](https://kafka.apache.org/41/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html)
- [gRPC — Flow Control](https://grpc.io/docs/guides/flow-control/)
