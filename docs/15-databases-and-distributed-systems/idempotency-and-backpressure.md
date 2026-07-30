# Idempotency a backpressure

Idempotency chráni jednu logical operation pred viacnásobným business effectom. Backpressure chráni processing graph pred tým, aby upstream vytváral viac in-flight a queued worku, než downstream dokáže bezpečne dokončiť. Ani jeden mechanizmus nestačí samostatne: idempotentný systém môže skolabovať pod miliónmi duplicate attempts a backpressured systém môže vykonať každý duplicate ako novú operation, ak nemá stable identity a equivalence contract.

```text
business operation a completion objective
→ exact tenant, operation, identity a semantic fingerprint
→ atomic claim + authoritative state transition
→ operation lifecycle, owner epoch a retention
→ durable event/provider identity chain
→ downstream credits a bounded queues
→ side effect a durable result
→ duplicate, overflow alebo unknown verdict
→ acknowledgement, retry a reconciliation
→ drain, recovery a retention closure
→ concurrent duplicate, rebalance a sustained-overload validation
```

Correctness sa hodnotí na logical operation a final effecte. Capacity sa hodnotí na celom source-to-sink flowe, nie iba na jednom brokeri alebo process queue.

## 1. Idempotency subject a business equivalence

Operation je idempotentná, keď opakované spracovanie rovnakého intentu nevytvorí ďalší odlišný intended business effect. Physical retry môže vykonať lookup, zapísať audit alebo vrátiť novší status; rozhodujúce je, že smeruje k tej istej authoritative operation.

Exact subject obsahuje tenant/account, operation type, client idempotency key alebo stable business ID, normalized semantic fingerprint, schema generation, authoritative operation record, lifecycle state, processing owner/epoch, downstream event a provider identities, response/status semantics a retention window.

HTTP method semantics sú iba vstup. RFC 9110 považuje `PUT` a `DELETE` za idempotentné podľa intended effectu, no zle navrhnutý `PUT /charge` môže stále vytvárať nový charge. Naopak `POST /settlements` môže byť business-idempotentný cez explicitný key a operation registry.

Key musí mať správny namespace:

```text
(tenant_id, operation_type, idempotency_key)
```

Rovnaký key pre retry tej istej operation zostáva stabilný. Server-generated nový ID pri každom attempt-e duplicate nerozpozná. Samotný UUID nie je contract; bez scope-u, atomic claimu, lifecycle-u a retention je iba string.

## 2. Semantic fingerprint a key-reuse conflict

Server musí odlíšiť retry rovnakého intentu od omylom znovu použitého keyu. Fingerprint sa počíta z canonical business významu: tenant, operation type/path, amount, currency, recipient/provider target a schema generation. Raw-body hash môže nepravdivo rozlíšiť rovnaký intent pre field order alebo naopak ignorovať význam headera, ktorý mení effect.

```text
same key + same fingerprint
→ load same operation/status/result

same key + different fingerprint
→ explicit conflict
→ no overwrite, no second effect
```

Fingerprint je immutable evidence uložená pri claime. Neskorší request nesmie prepísať payload prvého attemptu ani dostať starý success response pre iný intent. Schema generation zabraňuje tomu, aby rovnaký JSON získal po rollout-e odlišný business význam bez conflict verdictu.

Response nemusí byť byte-identický. Duplicate počas processingu môže dostať `202` a rovnaký status resource; po completion current truthful final response. Všetky responses však odkazujú na ten istý operation ID a final outcome.

## 3. Atomic claim, operation state a concurrency

Check-then-insert nie je idempotency:

```text
T1 SELECT key → absent
T2 SELECT key → absent
T1 create operation A
T2 create operation B
```

Claim a authoritative operation musia vzniknúť v jednej transaction alebo v preukázanom conditional protocol-e:

```text
BEGIN
→ INSERT idempotency_claim
   UNIQUE (tenant_id, operation_type, key)
→ verify semantic fingerprint
→ create settlement operation
→ create durable outbox event
COMMIT
```

Unique conflict načíta existing claim; nevytvorí nový operation ID. Claim oddelený do Redis alebo samostatnej service pred/po PostgreSQL commite vytvára dual-write gaps, ak jeden systém potvrdí a druhý zlyhá.

Binary `seen/not-seen` nestačí. Practical state machine rozlišuje `CLAIMED`, `ACCEPTED_DURABLE`, `PROCESSING`, `COMPLETED`, `FAILED_FINAL` a `RECONCILIATION_REQUIRED`. Každý state nesie owner epoch, timestamps, fingerprint, operation ID a last durable evidence. Crash v `CLAIMED` môže povoliť fenced takeover processingu, nie vznik druhej logical operation.

Concurrent duplicate počas processingu sa pripojí k existing statusu alebo bounded waitu. Nesmie spustiť ďalší provider attempt len preto, že final response ešte neexistuje.

## 4. Identity chain a external effects

Stable identity musí prejsť celým distributed flowom:

```text
client key
→ authoritative operation_id
→ outbox event_id
→ broker message identity
→ consumer processing claim
→ provider idempotency key
→ final-result event
```

IDs nemusia byť rovnaké, ale mapping je durable a queryable. Provider key odvodený z `attempt_id` je chybný, pretože retry sa providerovi javí ako nová operation. Stabilný provider key vychádza z tenant + merchant business operation + effect type.

Idempotent consumer vykoná event claim a local transition v jednej transaction. Pri external provider call-e local transaction nedokáže atomicky zahrnúť effect. Worker preto ukladá durable attempt state, používa stable provider key, pri lost response-e vykoná provider lookup a až potom zapíše final alebo reconciliation-required result.

`Exactly once` sa vždy scoping-uje. Kafka môže poskytnúť supported exactly-once read-process-write v Kafka boundary; unique database claim môže garantovať one local transition per event ID; provider idempotency môže garantovať one effect per business key. End-to-end business outcome stále potrebuje identity, local atomicity a reconciliation.

## 5. Retention, expiry a recovery

Idempotency retention nie je cache TTL. Musí pokryť maximum client retry horizon, backlog age, provider unknown-outcome reconciliation, broker replay/restore a support/dispute window. Non-terminal alebo reconciliation-required record nesmie expirovať do `ABSENT`.

```text
retention floor
= retry horizon
+ maximum accepted backlog/replay horizon
+ external reconciliation window
+ recovery/support margin
```

Terminal records možno compactovať alebo archivovať, ale minimum evidence pre duplicate verdict — key scope, fingerprint, operation ID a final digest — musí zostať. Clock-based cleanup podľa `first_seen` bez lifecycle checku môže po dlhom outage-i zmeniť starú accepted operation na nový create.

Recovery inventarizuje orphan claims, owner epochs, operation/outbox state, provider attempts a result events. Takeover je fenced a unknown outcomes sa lookupujú. Broad delete/replay bez equivalence graphu môže vytvoriť ďalšie effects.

## 6. Backpressure a completion credits

Backpressure je feedback, ktorým downstream vyjadruje, koľko ďalšej práce dokáže prijať. Reactive Streams modeluje demand tak, že Publisher nesmie emitovať viac elements, než Subscriber requested. V service platforme môže byť credit semaphore, consumer permit, HTTP/2/gRPC flow window alebo downstream capacity signal.

```text
provider completions uvoľnia credits
→ consumer môže pollnúť/admitnúť ďalšie work
→ bounded executor drží max in-flight
→ durable result uvoľní ownership
```

Rate limiting a backpressure nie sú totožné. Limiter aplikuje policy podľa caller/class a času. Backpressure reaguje na current sink capacity a duration. Circuit breaker zastavuje attempts pri failure state-e. Queue absorbuje iba bounded rozdiel medzi arrival a completion.

Littleov vzťah `in-flight ≈ throughput × duration` vysvetľuje, prečo rovnakých `5 000/s` pri latency raste z `100 ms` na `2 s` potrebuje približne `500 → 10 000` in-flight. Bez hard concurrency capu sa vyčerpajú threads, connections, memory, ports a provider quota, aj keď request rate ostane rovnaká.

## 7. Bounded queues, push/pull a hidden buffers

Každá queue potrebuje ownera, item identity/cost, hard capacity, maximum age/deadline, durability, overflow policy, fairness a drain target. Queue depth bez age je neúplná; tisíc 5-ms jobs a tisíc 30-minútových financial commands majú odlišný outcome risk.

Pull/credit model pollne iba toľko records, koľko permits downstream dovolí. Push source, ktorý nemožno spomaliť, musí explicitne rejectnúť, dropnúť rebuildable data, coalesce-nuť superseding state alebo spillnúť bounded durable work. `Buffer everything` nie je backpressure.

Kafka consumer môže limitovať `max.poll.records`, držať worker permits a pause-nuť assigned partitions pri nulových credits. Pause state sa po rebalance automaticky nezachováva; assignment callback ho musí z current credits znovu odvodiť. Offset sa commitne až po required durable outcome-e.

Backpressure audit zahŕňa SDK queue, gateway pending requests, server executor, database-pool waiters, producer buffer, broker partitions, consumer fetch buffer, retry topic, provider pool a result queue. Jeden bounded executor nepomôže, ak pred ním leží unbounded buffer.

Overflow policy zodpovedá data classu. Financial command sa truthful rejectne alebo durably deferne; optional telemetry sa môže sampleovať; superseding refresh coalescovať. Status, cancellation a reconciliation majú reserved credits. Weighted fair queue bráni bulk tenantovi vyhladovať interactive a recovery work.

## 8. Connected incident `DB-PAY-60`

Po provider outage-i prešiel partner bulk replay cez fleet admission `21 600 requests/s` a vytvoril backlog s oldest age `54 minút`. Idempotency service používala `SELECT absent → create settlement/outbox → autocommit key mapping`. Key nemal fingerprint ani operation/schema generation a cleanup mazal records po `20 minútach` od `first_seen`, aj keď operation stále `PROCESSING`.

Partner poslal `12 480` duplicate submissions; `1 906` retries prišlo po expiry a `143` concurrent pairs prešlo check-before-insert race-om. Vzniklo `83` duplicate authoritative operations s odlišnými IDs a provider keymi. Provider potvrdil `31` duplicate effects; `29` bolo automaticky reversed a `2` vyžadovali manual merchant remediation.

Backpressure topology bola rovnako nebezpečná. `48` worker Podov malo po `2 000` async in-flight, teda theoretical `96 000` proti provider safe in-flight `1 200`. Kafka pollovala po `500`; records išli do prakticky unbounded executor queue. Pause nastal až pri heap `85 %` a po rebalance sa neobnovil.

Backlog dosiahol `2.7 milióna` commands, executor queues približne `348 000` tasks, `17` Podov OOM a provider-pool wait p99 `11.2 s`. API naďalej durable-acceptovala creates, pretože nečítala provider credits ani backlog age.

Evidence ukázala dva samostatné root causes. Idempotency claim nebol atomic, nemal semantic fingerprint a expiroval pred operation/reconciliation closure. Backpressure neprepájala API admission, consumer poll a executor submission s downstream completion credits; buffers a theoretical concurrency boli rádovo väčšie než provider envelope.

## 9. Redesign a acceptance paths

Command core drží idempotency claim, settlement a outbox v jednej PostgreSQL transaction. Same key/same fingerprint vráti tú istú operation; different fingerprint conflict; non-terminal claim nemôže expirovať. Provider key používa merchant business operation ID, nie internal attempt.

Provider P2 má hard in-flight `1 200`; `48` Podov dostane base `25` permits, poll batch je max `50` a executor hard bound `100` per Pod. Completion uvoľňuje credits, consumer pause/resume ich rešpektuje a backlog age riadi API admission. Pri age `5–15 min` sa throttle-ne bulk; nad `15 min` sa nové bulk creates odmietnu, ale status/cancellation/reconciliation pokračujú. Recovery používa hysteresis a gradual credit increase.

**Positive path** vytvorí jeden atomic claim, jeden operation/outbox a jeden provider effect; duplicate dostane ten istý status/result.

**Concurrent/recovery path** crashne ownera, redeliveruje event alebo stratí provider response. Fenced takeover a lookup zachovajú jednu logical operation a unknown cohort sa reconciliuje.

**Overload path** obmedzí poll/executor/admission podľa credits, bounded queue age a fairness reserves; memory a provider in-flight zostanú v envelope.

**Forbidden path** odmietne check-then-insert, key reuse s iným fingerprintom, non-terminal expiry, attempt-based provider key, unbounded executor, pause iba podľa heapu, lost pause po rebalance a silent financial drop.

Acceptance zahŕňa concurrent duplicate, retry po dlhšom backlogu než pôvodný TTL, crash pred/po external effecte, rebalance, cache/registry loss, sustained overload, bounded drain a second overload počas recovery.

## 10. Troubleshooting a anti-patterny

Pri duplicate effecte, backlogu alebo OOM sa najprv vytvorí equivalence graph: tenant/business ID/fingerprint → internal operations → outbox/events → provider keys/effects. Potom sa analyzuje claim transaction, lifecycle/retention, owner epochs a unknown evidence. Capacity diagnostika porovná arrival a final completion, inventarizuje všetky buffers/in-flight boundaries, credits, pause/rebalance a overflow/fairness.

Najčastejšie anti-patterny sú `idempotency key = UUID`, `SELECT then INSERT`, fixed TTL kratší než backlog, provider key podľa attemptu, broker exactly-once vydávané za provider exactly-once, queue ako neobmedzený shock absorber, `max.poll.records` vydávané za concurrency cap a pokles queue depthu vydávaný za business recovery.

## 11. Kontrolné otázky

1. Ako sa HTTP method idempotency líši od business idempotency?
2. Čo tvorí exact key scope a semantic fingerprint?
3. Prečo claim a authoritative operation musia vzniknúť atomic?
4. Aké states a owner evidence potrebuje operation lifecycle?
5. Ako stable identity pokračuje cez outbox, broker a provider?
6. Z čoho sa odvodzuje retention window?
7. Ako exactly-once tvrdenie závisí od scope-u?
8. Ako sa backpressure líši od rate limitu a circuit breakeru?
9. Prečo queue depth bez age a hidden-buffer inventory nestačia?
10. Prečo `DB-PAY-60` vytvoril duplicate effects aj OOM?
11. Ktoré positive, concurrent/recovery, overload a forbidden paths musia prejsť?

## Glossary impact

Relevantné pojmy: idempotency subject, business idempotency, key scope, semantic fingerprint, atomic claim, idempotency state machine, duplicate join, idempotency retention, operation identity chain, idempotent consumer, exactly-once scope, backpressure subject, downstream credit, bounded queue, queue age, hidden buffer, overflow policy, consumer pause state, demand propagation, recovery hysteresis, bounded drain a idempotency/backpressure acceptance verdict.

## Primárne zdroje

- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [IETF HTTPAPI — The Idempotency-Key HTTP Header Field](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/)
- [AWS Builders' Library — Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)
- [Reactive Streams Specification for the JVM](https://github.com/reactive-streams/reactive-streams-jvm)
- [Apache Kafka — KafkaConsumer](https://kafka.apache.org/documentation/)
- [gRPC — Flow Control](https://grpc.io/docs/guides/flow-control/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Rate limiting](rate-limiting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Git ako source of truth →](../16-gitops-and-platform-engineering/git-as-source-of-truth.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
