# Databases and Distributed Systems — communication, messaging, routing a cache lifecycles

## Communication subject

Exact logical operation, caller/callee generations, immediate a final outcomes, deadline, cancellation, acknowledgement, retry identity, result visibility a recovery scope analyzovanej communication hranice. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Synchronous communication

Interaction, pri ktorej caller čaká na response v jednom request lifetime-e a preto zdedí availability, latency, timeout a unknown-outcome semantics celého dependency pathu. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Asynchronous communication

Interaction, pri ktorej immediate acknowledgement oddeľuje prijatie intentu od neskoršieho final outcome-u; vyžaduje durable acceptance, status/result visibility, retry a reconciliation. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Immediate outcome

Výsledok pôvodnej interaction, napríklad rejected alebo durably accepted, ktorý nemusí znamenať final business completion. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Final outcome

Authoritative terminal alebo explicitne reconcileable business stav operation po dokončení deferred processingu a external effects. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Deadline budget

End-to-end časový budget rozdelený medzi routing, queueing, execution, downstream calls, response transport a safety reserve. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Deadline propagation

Prenos remaining alebo child deadline-u cez dependency chain tak, aby každá vrstva nezačínala nový nezávislý plný timeout. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Cancellation boundary

Bod oddeľujúci prácu, ktorú možno bezpečne zastaviť, od už commitnutých, external alebo iba compensatable/reconcileable effects. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Unknown synchronous outcome

Stav, keď caller po timeout-e alebo strate response nevie, či callee operation neprijala, commitla alebo dokončila external effect. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Durable acceptance

Acknowledgement vydaný až po uložení stable operation identity a required intentu do recovery-capable authoritative state-u. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Status resource

Stable autorizovaný resource sprístupňujúci current authoritative alebo explicitne derived state asynchronous operation. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Command

Správa žiadajúca konkrétneho ownera vykonať business transition; má recipienta, stable identity a očakávaný outcome. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Event

Immutable oznámenie business alebo system factu, ktorý už nastal; nemá predstierať budúce dokončenie. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Query

Požiadavka na current alebo odvodenú representation, ktorá typicky nemá meniť authoritative state. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Acknowledgement level

Explicitný stupeň evidence, napríklad socket receipt, durable intent, broker responsibility, local consumer commit, external effect alebo final reconciled outcome. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Sync-over-async

Pattern, v ktorom caller publikuje asynchronous command, ale blokuje na reply a preto zostáva synchronous z pohľadu deadline-u a availability. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Async-over-sync

Asynchronous top-level workflow, ktorého worker vykonáva synchronous dependency call a potrebuje vlastný deadline, cancellation, retry a unknown-outcome contract. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Communication acceptance verdict

Dôkaz, že immediate/final outcomes, deadlines, cancellation, acknowledgements, status visibility, retries a second-attempt/dependency-failure scenarios tvoria truthful communication contract. Pozri [Synchronous vs. asynchronous communication](../docs/15-databases-and-distributed-systems/synchronous-vs-asynchronous-communication.md).

## Messaging subject

Exact business message/event identity, producer, schema, broker route/partition, durability, consumer group, delivery, acknowledgement, retry, replay a external-effect scope. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Queue

Messaging abstraction distribuujúca work deliveries eligible consumers, typicky s odstránením alebo completion po acknowledgement-e. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Partitioned log

Retained ordered records rozdelené do partitions, ktoré nezávislé consumer groups čítajú a replayujú podľa positions. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Producer acknowledgement

Evidence o publication boundary medzi producerom a brokerom; nepreukazuje consumer processing ani final business effect. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Publisher confirm

RabbitMQ publisher-side acknowledgement, že broker prevzal zodpovednosť za publication podľa queue/stream durability contractu; je oddelený od consumer acknowledgement-u. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Consumer acknowledgement

Consumer-to-broker signal, že delivery možno považovať za spracovanú podľa application contractu; musí nasledovať po required durable outcome-e. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Broker responsibility boundary

Stav, po ktorom broker publication prijal a chráni podľa konkrétnej leader/replication/queue policy, bez tvrdenia o downstream business completion. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## At-most-once delivery

Delivery semantics, pri ktorej message nemusí byť retryovaná a môže sa stratiť, ale system sa zámerne vyhýba redelivery. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## At-least-once delivery

Delivery semantics, pri ktorej message môže byť redelivered, kým broker nedostane acknowledgement; duplicate delivery je normálna failure podmienka. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Scoped exactly-once

Exactly-once claim obmedzený na explicitný transaction/log/state boundary; automaticky sa nevzťahuje na arbitrary external effects. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Consumer group

Logical subscription, v ktorej broker prideľuje partitions alebo deliveries aktívnym consumers a riadi ich ownership/rebalance. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Consumer generation

Version alebo epoch aktuálneho assignmentu, používaná na odmietnutie stale consumer ownershipu a commitov. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Partition key

Hodnota určujúca partition/routing a tým ordering scope, load distribution a hot-partition risk. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Offset commit

Zápis consumer position-u označujúci records, ku ktorým sa group po recovery štandardne nevráti; timing musí zodpovedať durable processing boundary. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Redelivery

Opätovné doručenie rovnakej logical message po chýbajúcom acknowledgement-e, consumer failure-e alebo replay-i. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Prefetch

Limit alebo batch delivery model určujúci počet messages doručených consumerovi bez potvrdenia; ovplyvňuje throughput, memory a redelivery scope. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## In-flight message limit

Bound na deliveries súčasne spracúvané consumerom pred acknowledgement-om, odvodený z latency, memory, downstream capacity a recovery tolerance. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Retry topic

Samostatný stream pre delayed alebo classified retries; musí zachovať business identity, ordering context, age a bounded attempt policy. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Parking queue

Inventory messages dočasne vyradených z automatic processingu pre investigation alebo controlled replay, s ownerom a reason metadata. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Dead-letter queue

Destination unresolved alebo permanently rejected deliveries; nie je final business outcome a potrebuje ownera, age, evidence a replay/retirement contract. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Replay generation

Versionovaný manifest, code/schema generation, source positions a safety policy použité pri opätovnom spracovaní historical messages. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Integration event

Stabilný external contract oznamujúci relevantný business fact bez leakovania interného persistence schema detailu. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Messaging acceptance verdict

Dôkaz, že publication, routing, durability, ordering, consumer acknowledgement, duplicates, external outcomes, retry/DLQ, replay a second-delivery tests tvoria správny event flow. Pozri [Message queues a event-driven architecture](../docs/15-databases-and-distributed-systems/message-queues-and-event-driven-architecture.md).

## Route/discovery subject

Exact API operation, gateway route generation, service identity, discovery inventory, endpoint generations, readiness, connection state a response/business contract. Pozri [Service discovery a API gateway](../docs/15-databases-and-distributed-systems/service-discovery-and-api-gateway.md).

## Logical service identity

Stabilný názov capability contractu, ktorý sa mapuje na meniaci sa endpoint inventory; nemá zlučovať incompatible API semantics. Pozri [Service discovery a API gateway](../docs/15-databases-and-distributed-systems/service-discovery-and-api-gateway.md).

## Endpoint identity

Konkrétna runtime address, port, release/contract generation, readiness, locality a capacity jedného backendu. Pozri [Service discovery a API gateway](../docs/15-databases-and-distributed-systems/service-discovery-and-api-gateway.md).

## Client-side discovery

Model, pri ktorom client načíta endpoint inventory a sám vykonáva selection, refresh a load balancing. Pozri [Service discovery a API gateway](../docs/15-databases-and-distributed-systems/service-discovery-and-api-gateway.md).

## Server-side discovery

Model, pri ktorom client používa stable proxy/virtual service a infrastructure layer vyberá aktuálny endpoint. Pozri [Service discovery a API gateway](../docs/15-databases-and-distributed-systems/service-discovery-and-api-gateway.md).

## Discovery generation

Versionovaný snapshot service-to-endpoint mapovania načítaný registry clientom, proxy alebo dataplane-om. Pozri [Service discovery a API gateway](../docs/15-databases-and-distributed-systems/service-discovery-and-api-gateway.md).

## Contract-generation eligibility

Podmienka, že endpoint podporuje exact API, acknowledgement, schema a operational contract požadovaný route-om. Pozri [Service discovery a API gateway](../docs/15-databases-and-distributed-systems/service-discovery-and-api-gateway.md).

## Route precedence

Pravidlá určujúce, ktorý z viacerých matching gateway routes vyhrá podľa specificity, priority a implementation contractu. Pozri [Service discovery a API gateway](../docs/15-databases-and-distributed-systems/service-discovery-and-api-gateway.md).

## Resolved route graph

Effective gateway configuration po vyhodnotení listeners, matches, precedence, policies, backend references a loaded generations. Pozri [Service discovery a API gateway](../docs/15-databases-and-distributed-systems/service-discovery-and-api-gateway.md).

## Capability readiness

Eligibility endpointu prijímať nový traffic pre exact operation a contract, nie iba process liveness alebo generic HTTP health. Pozri [Service discovery a API gateway](../docs/15-databases-and-distributed-systems/service-discovery-and-api-gateway.md).

## Endpoint draining

Transition, ktorá zastaví new work, propaguje discovery change, dokončí alebo odmietne bounded in-flight requests a uzavrie old connections pred termination. Pozri [Service discovery a API gateway](../docs/15-databases-and-distributed-systems/service-discovery-and-api-gateway.md).

## Connection convergence

Čas a dôkaz, že DNS caches, proxies, pools a long-lived connections prestali používať old endpoint/route generation. Pozri [Service discovery a API gateway](../docs/15-databases-and-distributed-systems/service-discovery-and-api-gateway.md).

## Selected-backend evidence

Per-request telemetry identifikujúca exact gateway route, service, endpoint a release/contract generation, ktoré request spracovali. Pozri [Service discovery a API gateway](../docs/15-databases-and-distributed-systems/service-discovery-and-api-gateway.md).

## Route/discovery acceptance verdict

Dôkaz, že effective route graph, compatible service identity, endpoint eligibility, discovery convergence, retries, draining a second-request/failover tests tvoria správny backend selection outcome. Pozri [Service discovery a API gateway](../docs/15-databases-and-distributed-systems/service-discovery-and-api-gateway.md).

## Cache subject

Exact cached value, authoritative owner/generation, cache layer, key/variants, freshness, invalidation, failure, fallback a business tolerance. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Cache authority boundary

Explicitné rozhodnutie, či cache je odvodená optimization, coordination state alebo durability/authority boundary a ktoré outcomes smie určovať. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Cache key

Identity cached representation-u obsahujúca všetky dimensions, ktoré menia result a isolation scope. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Variant dimension

Request, tenant, authorization, locale, API, policy alebo cohort attribute, ktorého zmena vytvára odlišnú cached representation. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Freshness — cache

Business verdict, či cached value možno použiť pre konkrétnu operation bez authoritative validation. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Staleness — cache

Rozdiel medzi cached generation a required/current authoritative generation, vyhodnotený podľa use-case tolerance. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Cache validator

Metadata ako generation, ETag alebo version umožňujúca overiť equivalence cached representation-u s authority. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Cache-aside

Pattern, pri ktorom application najprv číta cache a pri miss-e číta authority a následne cache naplní. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Write-behind cache

Pattern, pri ktorom cache acknowledge-ne mutation pred neskorším authoritative persistence write-om a tým sa stáva ordering/durability/recovery boundary. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Invalidation race

Concurrency failure, pri ktorom fill, authority commit a delete/update event skončia v poradí vytvárajúcom stale cache state. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Versioned cache key

Cache identity obsahujúca immutable authority generation, často oddelenú od mutable current-pointer keyu. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Cache stampede

Súbežný authority load po expiry/miss populárneho keyu, keď veľa callers vykoná rovnaký fill. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Single-flight cache fill

Koordinácia, pri ktorej jeden request načíta missing value a ostatní čakajú alebo použijú bounded stale result. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Hot key

Cache key s neúmerne vysokým request rate-om, ktorý môže vyčerpať jeden shard, thread alebo network path. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Negative caching

Uloženie absent/rejected resultu na obmedzený čas; musí odlíšiť authoritative absence od transient failure-u a key mismatchu. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Cache authority inversion

Failure model, pri ktorom evictable alebo incomplete cache hit/miss začne rozhodovať o authoritative business existence alebo side effecte. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Multi-level cache

Reťazec viacerých cache layers, napríklad browser, CDN, gateway, process memory a Redis, s nezávislými keys, validators a invalidation. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Bounded stale use

Explicitne povolené použitie starej generation počas definovaného času a scenára, s forbidden values/operations a authority fallbackom. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).

## Cache acceptance verdict

Dôkaz, že key identity, generations, freshness, invalidation, eviction, failure fallback a mutation/failover/second-read tests chránia správny business outcome. Pozri [Caching](../docs/15-databases-and-distributed-systems/caching.md).
