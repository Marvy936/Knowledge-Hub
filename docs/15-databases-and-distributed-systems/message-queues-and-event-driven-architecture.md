# Message queues a event-driven architecture

Message queue ani partitioned log nie sú iba miesto, kam application odošle JSON. Broker udržiava distributed state pre publication, routing, replication, ordering, delivery, acknowledgement, retry, retention a replay. Event-driven architecture k tomu pridáva business authority: ktorý fact už nastal, kto ho smie publikovať, ako sa mení jeho schema a ako consumers vytvoria durable outcome bez straty alebo duplicitného business effectu.

```text
business intent alebo committed fact
→ exact message/event a schema generation
→ transactional production a stable identity
→ broker route, partition a durability boundary
→ consumer-group ownership a delivery
→ bounded processing a external side effect
→ durable result transaction
→ acknowledgement alebo offset commit
→ retry, parking, replay a reconciliation
→ worker-crash, rebalance a second-delivery validation
```

Broker acknowledgement, consumer acknowledgement a final business completion sú tri odlišné boundaries. Spojiť ich do jednej metriky `message processed` vytvára false success.

## 1. Messaging subject a authority

Exact subject musí pomenovať business operation alebo fact, producer a generation, command/event type a schema version, stable message a business identity, destination, routing alebo partition key, producer acknowledgement level, replication a retention, consumer group, delivery a processing semantics, ordering scope, retry/DLQ contract a external side-effect authority.

Príklad Atlas Payments:

```text
event: SettlementRequested v3
business identity: operation_id
producer: outbox publisher 8.2
broker: settlement.commands.v3
partition key: operation_id
publication: idempotent producer + acks=all
consumer group: provider-execution-v3
completion:
  durable provider result/sent-unknown state + result outbox
  až potom offset commit
retention: 14 days
```

Command žiada ownera o transition; event oznamuje committed fact. CDC row change nemusí byť stabilný integration event a event sourcing používa event history ako authority, nie iba ako transport log. Tieto modely sa nesmú zamieňať.

## 2. Producer, dual write a publication outcome

Producer lifecycle ide od serialization a schema validation cez routing, client batching a broker append až po acknowledgement alebo timeout. Timeout môže znamenať, že broker record neprijal, alebo že ho durably prijal a response sa stratila. Publication outcome preto môže byť successful, rejected alebo unknown.

Klasický dual write:

```text
commit business row
→ publish message
```

môže po database commite zlyhať pred publication. Opačné poradie môže publikovať fact o transaction, ktorá rollbackla. Transactional outbox presunie business transition a outbox record do jednej local transaction:

```text
business state + outbox record
→ one database commit
→ independent fenced publisher
→ broker publication
→ event-ID reconciliation
```

Outbox stále potrebuje stable event ID, schema a route generation, publisher concurrency/fencing, retry semantics, cleanup a porovnanie outboxu s brokerom. `Published=true` bez broker evidence môže byť rovnako nepravdivé ako direct dual write.

Producer `acks=all` alebo RabbitMQ publisher confirm dokazuje iba broker responsibility boundary podľa current replication policy. Nedokazuje consumer processing ani provider effect.

## 3. Queue/log, partitioning a ordering

Queue typicky pridelí work jednému eligible consumerovi a po acknowledgement-e ho odstráni alebo dokončí. Partitioned log uchová ordered records a consumer groups spravujú vlastné positions; records možno počas retention replayovať.

Ordering musí mať scope. Kafka zachováva order v jednej topic-partition, nie globálne cez všetky partitions. Partition key preto rozhoduje o correctness aj load distribution.

```text
operation_id
→ všetky records jednej operation v jednej partition
→ vysoká distribúcia medzi operations

merchant_id
→ ordering naprieč merchant operations
→ riziko hot partition pri veľkom merchantovi
```

Retry topic s odlišným keyom môže zmeniť order. DLQ nie je ordered pokračovanie pôvodného streamu. Global order znižuje concurrency a availability a má sa používať iba vtedy, keď ho invariant skutočne vyžaduje.

## 4. Consumer completion a delivery semantics

Consumer lifecycle zahŕňa assignment, fetch, validation, business state read, local transaction, external effect, durable result a až potom acknowledgement.

Nebezpečný at-most-once business path:

```text
delivery
→ offset auto-commit
→ provider call
→ process crash
```

Broker už record neposkytne, ale provider effect ani durable final state nemusia existovať. Opačný path:

```text
delivery
→ provider succeeds
→ crash pred result commitom/ackom
→ redelivery
```

vytvorí duplicate physical attempt. Stable operation a provider idempotency key, outcome lookup a reconciliation sú preto potrebné aj pri at-least-once delivery.

`Exactly-once` je vždy scoped. Kafka transactions vedia koordinovať podporovaný read-process-write flow v Kafka boundary. Nezabezpečia automaticky exactly-one provider payment, e-mail alebo write do nezávislej databázy. Business exactly-once outcome typicky vzniká kombináciou at-least-once delivery, stable identity, idempotent transition, durable dedupe, unknown-outcome lookup a reconciliation.

Correct provider consumer flow je:

```text
poll bounded records
→ validate schema/generation
→ load operation by stable ID
→ skip already-final operation
→ provider call with stable idempotency key
→ provider lookup pri unknown response
→ commit final/sent-unknown state + result outbox
→ až potom commit offset
```

## 5. Consumer ownership, backpressure a retry

Consumer group mení assignment pri scale-out-e, failure alebo rebalance. Old worker môže pokračovať v in-flight práci po strate partition a nový worker môže dostať rovnaký record. Ak stale worker môže meniť authoritative state, operation potrebuje consumer generation, lease alebo fencing token.

Prefetch a `max.poll.records` presúvajú backlog z brokeru do consumer memory. Unbounded in-flight work zvyšuje OOM risk a redelivery scope. Limit sa odvodzuje z processing latency, downstream capacity, acknowledgement deadline, memory a acceptable crash recovery cohort.

```text
arrival rate
→ broker backlog age
→ assigned partitions
→ bounded fetched records
→ bounded provider concurrency
→ durable completions
→ acknowledgement rate
```

Retry policy klasifikuje transient failure, permanent rejection, malformed schema, authorization/config error, downstream overload, stale generation a unknown external outcome. Retry potrebuje attempt count, first-seen time, next eligible time, stable identity, original order context, maximum age a ownera.

DLQ alebo parking queue nie je final outcome. Je to inventory unresolved records s reason, age, schema generation, business impact, replay plan a retirement criteria. Broad seek na starší offset bez manifestu môže zopakovať už dokončené external effects.

## 6. Schema, events a replay

Retained event je dlhodobý contract. Compatibility musí pokryť current producers, current consumers aj replay starých records. Required/optional fields, enum expansion, default values, identity, timestamps a semantic meaning patria do versioning modelu.

Zmeniť význam `completed=true` z `provider accepted` na `ledger finalized` bez novej semantic generation je breaking change, aj keď Avro alebo JSON schema zostane technicky compatible.

Choreography je vhodná, keď nezávislí consumers reagujú na facts a každý vlastní svoj outcome. Process manager alebo orchestration je vhodná, keď workflow potrebuje explicitný state, deadlines, compensation a jedného ownera. Events neodstraňujú coupling; presúvajú ho do schema, semantics, partitioning, retention a recovery.

Replay je nová operation generation. Musí mať bounded manifest, target consumer generation, idempotency evidence, side-effect policy a progress/reconciliation state. Replay nie je `reset offsets and hope`.

## 7. Connected incident `DB-PAY-58`

Async v8.2 používal transactional outbox a Kafka topic `settlement.commands.v3`. Producer bol idempotentný a používal `acks=all`. Consumer však mal:

```text
enable.auto.commit=true
auto.commit.interval.ms=1000
max.poll.records=500
provider concurrency=120 per Pod
```

O `12:08 UTC` provider latency vzrástla na p95 `2.4 s`. Fetch batches vytvorili veľké in-flight cohorts a o `12:13 UTC` tri Pody dostali OOM kill. `611` records malo committed offsets pred durable provider resultom. Po restart-e `84` operations nemalo provider attempt ani final state; `527` provider spracoval alebo ich bolo možné dohľadať.

Retry worker navyše používal `merchant_id` namiesto `operation_id` ako partition key. Pri `19` operations sa retry/result records objavili v inom poradí než original command. DLQ dashboard ukazoval iba count, nie age, schema generation ani ownera.

Root cause bol consumer completion contract, ktorý posunul offset pred durable business outcome. Publication bola správne durable; strata vznikla na delivery-to-effect boundary. Vysoký batch, provider concurrency, auto commit, odlišný retry key, absent sent-unknown state a monitoring broker lagu namiesto accepted-to-final completion incident zosilnili.

## 8. Redesign a acceptance paths

Consumer teraz polluje najviac `50` records a provider concurrency je `12` per Pod. Partition key je `operation_id`; offset sa commitne manuálne až po durable result transaction. Retry je classified, delayed a bounded. Parking inventory obsahuje ownera, age, reason, exact record a replay generation.

**Positive path** publikuje outbox event, broker ho durably prijme, consumer vytvorí provider/result state a offset postúpi až po commite.

**Recovery path** zabije worker po provider response-e alebo počas rebalance-u. Redelivery nájde final alebo sent-unknown state, vykoná provider lookup a nevytvorí druhý business effect.

**Failure path** pri schema error, permanent rejection alebo downstream overloade record neackne ako úspešne dokončený; prejde do explicitného retry/parking state-u s ownerom.

**Forbidden path** odmietne auto commit pred resultom, producer ack ako business completion, retry s iným ordering keyom, stale consumer write, unbounded prefetch a broad replay bez manifestu.

Acceptance zahŕňa second delivery, crash pred/po external effecte, rebalance, broker failover, old-schema replay a DLQ re-drive.

## 9. Troubleshooting a anti-patterny

Diagnostika začína business a message identity, potom outbox/producer evidence, broker route/partition/replication position, consumer assignment/generation, fetched a in-flight cohort, local/external outcome, offset timing, retry/DLQ a final reconciliation.

Najčastejšie anti-patterny sú broker acknowledgement považovaný za spracovanie, exactly-once ako checkbox, auto commit pre jednoduchší consumer, DLQ považovaná za vyriešenie, throughput riešený iba počtom consumers, queue depth bez age a events vydávané za odstránenie coupling-u.

## 10. Kontrolné otázky

1. Čo tvorí exact messaging subject?
2. Ako sa queue a partitioned log líšia?
3. Čo producer acknowledgement dokazuje a čo nedokazuje?
4. Ako transactional outbox rieši dual write?
5. Prečo exactly-once potrebuje explicitný scope?
6. Kedy má consumer commitnúť offset?
7. Ako stable provider identity chráni redelivery?
8. Ako partition key ovplyvňuje order a load?
9. Prečo auto commit stratil `84` operations v `DB-PAY-58`?
10. Ktoré positive, recovery, failure a forbidden paths musia prejsť?

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
