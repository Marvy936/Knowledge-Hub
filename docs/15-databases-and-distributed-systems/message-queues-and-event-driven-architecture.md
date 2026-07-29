# Message queues a event-driven architecture

Message queue nie je iba `miesto, kam pošleme JSON`. Je to distributed state machine pre publication, routing, durability, ordering, delivery, acknowledgement, retry, retention a recovery. Event-driven architecture navyše definuje, **ktoré business facts vznikajú, kto ich vlastní, ako sa menia schemas, ako consumers obnovia state a ako sa rozlíši duplicate delivery od duplicate business effectu**.

```text
business intent alebo committed fact
→ exact message/event subject
→ durable production a routing
→ broker partition/queue/log state
→ consumer assignment a delivery
→ processing + side effect
→ acknowledgement/offset commit
→ retry, dead-letter alebo replay
→ final business outcome a reconciliation
→ second-delivery/consumer-failure validation
```

## 1. Exact messaging subject

Tvrdenie `message je v Kafka` alebo `queue je durable` nestačí. Subject má uvádzať:

- business operation alebo fact;
- producer a producer generation;
- event/command type a schema version;
- stable message a business identity;
- topic, queue, exchange, partition alebo stream;
- routing/partition key;
- producer acknowledgement level;
- retention a replication policy;
- consumer group/subscription identity;
- delivery, processing a acknowledgement semantics;
- ordering scope;
- retry a dead-letter policy;
- external side-effect contract;
- replay a reconciliation authority.

Príklad:

```text
event: SettlementRequested v3
business key: operation_id
producer: settlement outbox publisher 8.2
broker: Kafka topic settlement.commands.v3
partition key: operation_id
producer contract: idempotent producer + acks=all
consumer group: provider-execution-v3
consumer completion: provider outcome + durable result event + offset commit
retention: 14 days
```

## 2. Queue, log a stream

### Queue

Typický queue model distribuuje message jednému eligible consumerovi. Po úspešnom acknowledgement-e sa delivery môže odstrániť alebo označiť ako dokončená.

Vhodný je pre:

- work distribution;
- bounded command processing;
- task ownership;
- competing consumers.

### Partitioned log

Log uchováva ordered records v partitions. Consumers si udržiavajú positions a records možno replayovať počas retention.

Vhodný je pre:

- event streams;
- viac nezávislých consumer groups;
- rebuild projections;
- audit a replay;
- ordered processing per key/partition.

Queue ani log automaticky nevytvára presne jeden business effect. Delivery a application semantics sú samostatné.

## 3. Producer lifecycle

```text
application intent
→ serialization/schema validation
→ routing/partition decision
→ client buffer/batch
→ broker request
→ leader append
→ replication/durability condition
→ producer acknowledgement alebo timeout
→ retry/unknown publication outcome
```

Producer musí rozlíšiť:

- message nebola odoslaná;
- broker ju odmietol;
- leader ju prijal, ale response sa stratila;
- message bola accepted, no nebola routable do required queue;
- message je durable podľa konkrétnej replication policy;
- transaction bola committed alebo aborted.

RabbitMQ publisher confirms pokrývajú publisher-to-broker responsibility; consumer acknowledgements sú samostatná hranica. Kafka producer acknowledgement a idempotence riešia broker publication attempts, nie arbitrary external consumer side effects.

## 4. Dual write a transactional outbox

Klasický failure:

```text
commit business row
→ publish message
```

Medzi týmito krokmi môže process spadnúť. Opačné poradie môže publishnúť event o transaction, ktorá rollbackla.

Transactional outbox:

```text
one database transaction
→ business state + outbox record
→ commit
→ independent publisher
→ broker publication
→ mark/record publication state
```

Outbox nerieši všetko. Potrebuje:

- stable event identity;
- publisher concurrency/fencing;
- broker retry semantics;
- cleanup/retention boundary;
- reconciliation medzi outbox a brokerom;
- schema a routing generation;
- truthful publication status.

## 5. Delivery semantics

### At-most-once

Message môže byť stratená, ale nebude úmyselne redelivered. Typicky acknowledgement/position postupuje pred processingom alebo retry nie je povolený.

### At-least-once

Message sa retryuje, kým nie je acknowledged. Duplicate delivery je očakávaná.

### Exactly-once

Termín je vždy scoped. Kafka transactions môžu poskytnúť atomic read-process-write semantics v podporovanom Kafka flowe. Nevytvárajú automaticky exactly-once efekt v external providerovi, databáze bez koordinácie alebo e-mailovom systéme.

Pre business exactly-once outcome treba často:

```text
at-least-once delivery
+ stable operation identity
+ idempotent state transition/external API
+ durable dedupe evidence
+ unknown-outcome lookup
+ reconciliation
```

## 6. Consumer lifecycle

```text
assignment/subscription
→ delivery/fetch
→ deserialize a validate
→ business precondition read
→ local transaction
→ external side effect
→ durable result evidence
→ acknowledgement/offset commit
```

Nebezpečné poradie:

```text
delivery
→ auto-commit offset
→ provider call
→ process crash
```

Broker už message považuje za spracovanú, ale business effect nemusí existovať.

Opačný problém:

```text
delivery
→ provider call succeeds
→ process crash before offset commit
→ redelivery
```

Retry môže vytvoriť duplicate physical attempt. Stable provider idempotency key a provider lookup sú preto povinné.

## 7. Acknowledgement nie je business completion

Broker acknowledgement môže dokazovať:

- publication accepted;
- queue/partition leader prevzal record;
- required replicas potvrdili zápis;
- consumer dostal delivery;
- consumer tvrdí, že processing dokončil.

Ani posledný bod nemusí dokazovať final external outcome, ak consumer acknowledgement prebehne pred durable result evidence.

Correct consumer completion contract pre provider execution:

```text
message delivery
→ load authoritative operation
→ provider attempt so stable idempotency keyom
→ provider result/lookup
→ PostgreSQL final or sent-unknown state + result outbox
→ commit
→ acknowledge/commit offset
```

## 8. Ordering

Ordering musí mať scope:

- within one queue;
- within one partition;
- per aggregate/business key;
- per producer session;
- globally.

Global ordering znižuje concurrency a availability. Väčšina business workflows potrebuje ordering per aggregate alebo operation.

Partition key musí zodpovedať ordering a load distribution:

```text
merchant_id
→ preserves merchant ordering
→ môže vytvoriť hot partition pre veľkého merchanta

operation_id
→ distributes operations
→ nezachová ordering medzi operations jedného merchant accountu
```

Retry topic s iným partition keyom môže porušiť pôvodný ordering. Dead-letter queue tiež nie je automaticky ordered continuation pôvodného streamu.

## 9. Consumer groups, rebalancing a ownership

Consumer group prideľuje partitions alebo deliveries aktívnym consumers. Pri scale change, failure alebo membership change môže nastať rebalance.

Riziká:

- in-flight work pokračuje po strate assignmentu;
- nový consumer spracuje rovnaký record;
- stale consumer commitne offset;
- long processing prekročí heartbeat/session contract;
- partition-local state sa nestihne obnoviť;
- external operation nemá fencing token.

Consumer generation alebo ownership epoch má byť súčasťou state transitionov, keď stale worker môže poškodiť authoritative outcome.

## 10. Backpressure, prefetch a in-flight limit

Consumer throughput nie je iba počet replicas.

```text
arrival rate
→ broker backlog
→ assigned consumers
→ prefetch/fetch batch
→ in-flight processing
→ downstream capacity
→ acknowledgement rate
```

Unbounded prefetch môže presunúť backlog z brokeru do consumer memory a predĺžiť redelivery po crashi. Príliš malý prefetch môže nevyužiť throughput. Limit sa odvodzuje z:

- processing latency;
- consumer concurrency;
- memory;
- acknowledgement timeout;
- downstream capacity;
- acceptable redelivery scope.

Queue depth bez age a arrival/completion rate môže zavádzať.

## 11. Retry

Retry policy musí klasifikovať failures:

- transient retryable;
- permanent business rejection;
- malformed/schema-invalid;
- authorization/configuration failure;
- unknown external outcome;
- dependency overload;
- stale generation.

Retry má obsahovať:

- attempt count;
- first-seen time;
- next eligible time;
- stable business/message identity;
- original partition/order context;
- last error classification;
- maximum age;
- dead-letter/parking decision.

Immediate retry bez backoffu môže vytvoriť hot loop. Retry topic môže narušiť ordering. DLQ nie je opravený outcome; je to inventory unresolved messages vyžadujúci ownera, evidence, replay contract a retirement.

## 12. Events a schema evolution

Event je dlhodobý contract. Schema evolution musí riešiť:

- producer a consumer version inventory;
- backward/forward/full compatibility;
- required a optional fields;
- semantic change bez field change;
- default values;
- enum expansion;
- identity a timestamp semantics;
- retention a replay starých generations;
- deprecation a consumer retirement.

Nesprávne je zmeniť význam `completed=true` z `provider accepted` na `merchant ledger finalized` bez novej semantic generation.

## 13. Event-driven architecture

Event-driven architecture oddeľuje producers a consumers časovo a organizačne. To však neodstraňuje coupling; presúva ho do:

- event schemas;
- semantic meanings;
- ordering assumptions;
- partition keys;
- delivery/retention guarantees;
- consumer lag;
- replay behavior;
- authority ownership.

Choreography je vhodná, keď consumers nezávisle reagujú na facts. Orchestration/process manager je vhodný, keď workflow potrebuje explicitný state, deadlines, compensations a ownera.

## 14. Event sourcing, CDC a integration events

### Event sourcing

Authoritative state sa odvodzuje z ordered domain events. Vyžaduje aggregate rules, event versioning, snapshots a deterministic rebuild.

### Change Data Capture

CDC publikuje database changes. Row mutation nie je automaticky business event. Consumers potrebujú semantic mapping a transaction ordering.

### Integration event

Stabilný external contract oznamujúci relevantný business fact bez leakovania interného schema detailu.

Tieto modely sa nemajú zamieňať.

## 15. Worked incident `DB-PAY-58`

Async v8.2 path používal transactional outbox a Kafka topic `settlement.commands.v3`. Publication bola nakonfigurovaná s idempotentným producerom a `acks=all`.

Worker configuration však obsahovala:

```text
enable.auto.commit=true
auto.commit.interval.ms=1000
max.poll.records=500
provider concurrency=120 per Pod
```

Consumer flow bol:

```text
fetch batch
→ records become eligible for auto offset commit
→ load policy cache
→ provider calls
→ write results
```

O `12:08 UTC` provider latency stúpla na p95 `2.4 s`. O `12:13 UTC` tri worker Pody dostali OOM kill po nahromadení in-flight payloadov a response buffers.

Potvrdené evidence:

- `611` records malo committed consumer offsets pred durable provider resultom;
- `84` operations nemalo provider attempt ani final state po worker restart-e;
- `527` operations provider spracoval alebo ich bolo možné dohľadať;
- `43` duplicate provider attempts pochádzalo prevažne z legacy synchronous retries;
- retry worker používal `merchant_id` namiesto `operation_id` ako partition key;
- `19` operation histories malo retry/result records v inom poradí než original command;
- DLQ dashboard obsahoval iba count, nie age, schema generation ani ownera.

### Messaging root cause

Primary messaging root cause bol **consumer completion contract, ktorý posunul offset pred durable business outcome**. Broker publication bola správne durable; failure nastal na delivery-to-effect boundary.

Causal amplifiers:

- vysoký `max.poll.records` a unbounded provider concurrency;
- auto commit nezávislý od per-record resultu;
- retry topic s odlišným partition keyom;
- absence sent-unknown state;
- monitoring broker lag namiesto accepted-to-final completion;
- cache invalidation consumer zdieľal rovnaký unsafe offset pattern.

## 16. Evidence-preserving containment

```text
stop affected consumer group
→ preserve group offsets, assignments a broker records
→ snapshot outbox publication state
→ preserve provider request/idempotency evidence
→ classify offset-committed records without durable result
→ disable automatic retry topic
→ replay iba exact never-sent manifest
→ reconcile sent-unknown cez provider ledger
```

Nebol vykonaný broad `seek to earlier offset`, pretože by znovu prehral aj confirmed provider effects bez dostatočnej dedupe klasifikácie.

## 17. Authoritative redesign

Consumer flow:

```text
poll bounded records
→ validate schema/generation
→ load operation by stable ID
→ skip already-final operation
→ call provider with stable idempotency key
→ lookup on unknown outcome
→ commit final/sent-unknown state + result outbox
→ only then commit offset/acknowledge
```

Operational contract:

```text
max poll records: 50
per-Pod provider concurrency: 12
partition key: operation_id
manual offset commit: after durable result transaction
retry: classified, delayed and bounded
DLQ/parking: owner + age + reason + replay generation
```

Outbox-to-broker reconciliation porovnáva exact event IDs. Consumer reconciliation porovnáva broker positions, operation state a provider evidence.

## 18. Messaging acceptance verdict

Messaging design je prijatý, keď:

- exact command/event subject a authority sú explicitné;
- producer publication má stable identity a truthful acknowledgement semantics;
- dual write je odstránený alebo koordinovaný outbox/transaction mechanizmom;
- routing a partition key zodpovedajú ordering a load modelu;
- replication/retention zodpovedajú recovery window-u;
- consumer acknowledgement nastáva po durable required outcome-e;
- duplicate delivery je safe cez idempotency/reconciliation;
- external unknown outcome má lookup a bounded retry;
- consumer generation/ownership zabraňuje stale processingu;
- prefetch/in-flight limits chránia downstream;
- retry, parking a DLQ majú ownera, age a replay contract;
- schema compatibility zahŕňa retained/replayed records;
- backlog age a final completion sú observable;
- second delivery, worker crash, rebalance, broker failover a replay tests prejdú;
- forbidden lost-accepted-message, duplicate business effect a false acknowledgement outcomes zlyhajú.

## 19. Troubleshooting flow

```text
accepted message chýba, duplikuje sa alebo je out of order
→ exact event/message/business identity
→ producer/outbox evidence
→ broker route/partition/replication position
→ producer ack/unknown publication
→ consumer group assignment/generation
→ delivery/prefetch/in-flight state
→ local transaction/external effect
→ acknowledgement/offset timing
→ retry/DLQ/replay path
→ final business reconciliation
```

## 20. Anti-patterny

### Broker ack = spracované

Dokazuje producer-to-broker boundary, nie consumer business outcome.

### Exactly-once je checkbox

Je scoped na konkrétny system boundary a side effects.

### Auto commit zjednoduší consumer

Môže vytvoriť at-most-once business processing.

### Ack až úplne na konci vyrieši duplicates

Crash po external effecte a pred ackom stále vytvorí redelivery.

### DLQ znamená vybavené

Je to unresolved inventory, nie final outcome.

### Viac consumers vždy zvýši throughput

Downstream capacity, partitions, locks a provider limits môžu zostať bottleneckom.

### Queue depth je backlog health

Bez age, arrival/completion rate a in-flight state je neúplná.

### Events odstránia coupling

Coupling sa presunie do semantics, schemas, ordering a recovery.

## 21. Kontrolné otázky

1. Čo tvorí exact messaging subject?
2. Ako sa queue a partitioned log líšia?
3. Čo producer acknowledgement dokazuje?
4. Ako transactional outbox rieši dual write a čo nerieši?
5. Ako at-most-once, at-least-once a exactly-once závisia od scope-u?
6. Kedy má consumer commitnúť offset alebo ack?
7. Prečo external side effect potrebuje idempotency a lookup?
8. Aký ordering poskytuje partition key?
9. Ako rebalance vytvára stale consumer risk?
10. Prečo auto commit stratil 84 operations v `DB-PAY-58`?
11. Čo musí obsahovať DLQ/replay contract?
12. Čo musí overiť messaging acceptance verdict?

## Glossary impact

Relevantné pojmy: messaging subject, queue, partitioned log, producer acknowledgement, publisher confirm, consumer acknowledgement, broker responsibility boundary, transactional outbox, at-most-once delivery, at-least-once delivery, scoped exactly-once, consumer group, consumer generation, partition key, offset commit, redelivery, prefetch, in-flight limit, retry topic, parking queue, dead-letter queue, replay generation, integration event a messaging acceptance verdict.

## Primárne zdroje

- [Apache Kafka — Design](https://kafka.apache.org/documentation/#design)
- [Apache Kafka — Producer configuration](https://kafka.apache.org/documentation/#producerconfigs)
- [RabbitMQ — Consumer acknowledgements and publisher confirms](https://www.rabbitmq.com/docs/confirms)
- [RabbitMQ — Reliability guide](https://www.rabbitmq.com/docs/reliability)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Synchronous vs. asynchronous communication](synchronous-vs-asynchronous-communication.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Service discovery a API gateway →](service-discovery-and-api-gateway.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
