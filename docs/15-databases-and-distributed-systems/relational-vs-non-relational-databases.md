# Relational vs. non-relational databases

Voľba databázy nie je rozhodnutie medzi „tabuľkami“ a „JSON-om“. Je to návrh authority, invariants, transaction boundaries, access paths, distribution, lifecycle a recovery pre konkrétny business state. Relational, document, key-value, wide-column, graph a time-series systémy organizujú dáta a koordinujú concurrent changes odlišne; každý model niektoré operácie zjednodušuje a iné presúva do application, event pipeline alebo operational reconciliation.

Správna otázka preto neznie „SQL alebo NoSQL?“, ale „ktorý systém má byť autoritatívny pre tento business fact, ktoré zmeny musia byť atomické, aké queries a failure scenáre sú dominantné a ako sa preukáže, že odvodené copies zostali správne?“. Atlas Payments používa relational ledger pre settlement invariants a document projection pre merchant reads. Incident `DB-PAY-56` ukazuje, čo sa stane, keď projection začne nepozorovane fungovať ako druhý autoritatívny writer.

## 1. Dominantný invariant-to-data-system lifecycle

Data-system design začína business invariants a operation boundaries. Až potom sa vyberá model, schema, partitioning, indexes, transaction a replication contract. Runtime musí zachovať authority a derived-state lineage aj pri retry, partial failure, migration a failover.

```text
business capability a invariants
→ exact data-system subject a authority map
→ aggregate/transaction a consistency boundaries
→ relational/document/key-value/graph/time-series model
→ schema, keys, constraints a access paths
→ placement, partitioning a replication
→ write/read protocol a derived projections
→ effective runtime state a business verification
→ migration, reconciliation a recovery
→ second-operation a forbidden-path validation
```

Databázový produkt je iba jedna implementačná boundary. End-to-end correctness závisí aj od application retry semantics, event publication, cache/projection freshness, schema compatibility, provider effects a recovery tooling.

## 2. Exact data-system subject a field authority

Tvrdenie „settlements sú v PostgreSQL a MongoDB“ nie je návrh. Exact subject zachováva business entity a operations, authoritative system, schema/model generation, primary a derived fields, keys a identity semantics, transaction/aggregate boundary, read/write paths, consistency a staleness contract, partition/shard key, indexes, retention, encryption, replication/backup, migration lineage a owners.

```text
subject: DATA-PAY-56-v2
entity: settlement intent a execution state
authority: PostgreSQL settlement + outbox transaction
identity: merchant_id + merchant_operation_id
invariants:
  one accepted intent per merchant operation
  amount/currency immutable after acceptance
  provider effect at most once
projection: document merchant_settlement_view
projection source: ordered outbox events
projection staleness: p99 <= 5 s
forbidden: direct document write mení authoritative state
```

Field authority musí byť explicitná. Relational ledger môže vlastniť amount, status transition a provider correlation; document projection môže vlastniť UI-only rendering metadata. Last-write-wins medzi oboma stores nevytvára reconciliation, iba skrýva konflikt.

## 3. Relational model: invariants, joins a transactions

Relational databáza organizuje state do relations s explicitnými columns, types, keys a constraints. Primary/unique keys chránia identity; foreign keys referential integrity; check constraints local business pravidlá. Transactions umožňujú meniť viac rows/tables ako jednu atomic unit a query language podporuje joins a set-based operations.

Relational model je silný, keď business facts majú stabilné identity, viac vzťahov, cross-row alebo cross-table invariants, ad-hoc queries, audit/reconciliation potreby a schema evolution, ktorú treba koordinovať s viacerými application generations.

```text
merchant intent
→ insert settlement
+ insert outbox command
+ uniqueness constraint
+ referential a amount checks
→ one atomic commit
```

Tento model nevyrieši distribúciu automaticky. Large joins, global constraints, hot keys, cross-region latency a long transactions môžu byť drahé. Normalization znižuje redundantný authoritative state, ale príliš fragmentovaný model môže zvyšovať join, lock a operational complexity.

## 4. Document model: aggregate locality a flexible shape

Document database ukladá related data do documentov, často s nested objects a arrays. Silná je vtedy, keď aplikácia číta alebo mení celý aggregate spolu, shape sa vyvíja medzi cohorts a denormalizácia znižuje cross-collection joins alebo transactions.

```json
{
  "merchantId": "m-71",
  "settlementId": "s-902",
  "status": "pending",
  "amount": {"currency": "EUR", "minor": 12500},
  "timeline": []
}
```

Single-document atomicity môže byť veľmi užitočná, no aggregate boundary musí vychádzať z write invariants, nie iba z convenient read response-u. Unbounded arrays, document growth, duplicate embedded data a multi-document updates môžu vytvoriť contention a reconciliation debt. Modern document systems podporujú multi-document transactions, ale ich existencia nenahrádza dobrý aggregate design a môže zvýšiť latency, coordination a sharding cost.

Flexible schema znamená, že storage nemusí odmietnuť každý variant; neznamená schema-free system. Application, validation rules, indexes, serializers, readers a historical documents stále tvoria versionovaný schema contract.

## 5. Key-value, wide-column, graph a time-series models

Key-value store mapuje exact key na opaque alebo partially structured value. Poskytuje nízku latency pre known-key access, sessions, idempotency records, rate limits alebo caches. Nehodí sa ako primary authority, ak business potrebuje bohaté predicates, joins alebo cross-key invariants bez application coordination.

Wide-column model organizuje rows podľa partition keyu a clustering/order semantics. Je vhodný pre veľmi veľký distributed write/read workload s queries známymi vopred. Model sa navrhuje podľa access paths; query mimo partition keyu môže vyžadovať scan, secondary index alebo novú denormalizovanú table.

Graph database robí edges a traversals first-class. Je vhodná pre identity relations, fraud paths, dependency alebo authorization graphs. Graph traversal však nemusí byť najlepší system of record pre high-throughput ledger mutations.

Time-series system optimalizuje timestamped append-heavy observations, retention, compression a time-window aggregation. Metrics alebo sensor events sú prirodzené subjects; mutable financial entity s uniqueness a multi-row invariantmi zvyčajne potrebuje inú primary authority.

Tieto categories nie sú absolútne. Produkty pridávajú transactions, secondary indexes, JSON, graph alebo time-series extensions. Rozhoduje effective contract konkrétneho engine-u a deploymentu, nie marketingový label.

## 6. Aggregate a transaction boundary

Aggregate je scope, ktorý musí udržať invariants počas jednej business operation. Ak settlement a outbox command musia vzniknúť spolu, patria do jednej atomic authority boundary alebo potrebujú explicitný distributed protocol s recovery.

Príliš malý aggregate presunie consistency do eventov a compensation. Príliš veľký aggregate vytvorí contention, hot partition a veľké transactions. Správna hranica sa odvodzuje z invariants, concurrency, operation identity a failure behavior.

```text
operation intent
→ identify invariant set
→ choose atomic boundary
→ serialize conflicting changes
→ commit/abort
→ publish derived changes
→ reconcile downstream projections
```

Cross-store dual write bez atomic coordination je nebezpečný:

```text
commit PostgreSQL
→ write document projection
→ process crash medzi krokmi
```

Výsledkom je partial success. Transactional outbox alebo change-data capture zachová commit lineage a projection sa stane rebuildable derived stateom.

## 7. Schema, constraints a application compatibility

Schema contract zahŕňa types, required/optional fields, defaults, keys, constraints, indexes, version a reader/writer compatibility. Relational DDL býva explicitne enforcement-nuté engine-om. Document schema môže byť application- alebo server-validovaná a historical records môžu mať viac shapes.

Constraint má byť čo najbližšie k authoritative write boundary. Application-only uniqueness cez `SELECT then INSERT` zlyhá pri concurrency; unique constraint rozhodne konflikt autoritatívne. Naopak database constraint nevie sám vysvetliť všetky business workflows a application musí bezpečne spracovať conflict, retry a unknown outcome.

Schema evolution je protocol medzi old/new readers, writers, backfillom, indexes/constraints a replicas. Additive expand, tolerant readers, bounded backfill, read/write switch, validation a contract fáza sú bezpečnejšie než destructive one-shot change.

## 8. Keys, partitioning a locality

Primary/business key určuje identity. Partition alebo shard key určuje placement a routing. Môžu byť rovnaké, ale riešia inú otázku. Dobrý distribution key má dostatočnú cardinality, rovnomerný load, stable semantics, query locality a minimálnu potrebu cross-partition transactions.

Hot merchant, timestamp-only append alebo low-cardinality status môžu vytvoriť skew. Random key rozloží writes, ale zhorší range alebo tenant locality. Composite key môže kombinovať tenant a bucket, no mení query, rebalancing a uniqueness semantics.

Sharding je architektúrna zmena, nie iba capacity toggle. Zavádza routing metadata, rebalance/migration, distributed transactions/queries, cross-shard uniqueness, hotspots a partial failures. Ak dataset a workload bezpečne zvláda jeden cluster, skoré sharding často pridáva complexity bez užitočného outcome-u.

## 9. Access paths a workload contract

Data model sa hodnotí podľa konkrétnych reads a writes: key lookup, range, join, graph traversal, append, aggregation, stream, batch alebo full-text. Každý path má population, selectivity, latency, consistency, frequency a peak concurrency.

Index alebo denormalization zrýchľuje read za cenu write, storage, maintenance a migration costu. Document embedding znižuje joins, ale duplikuje state. Materialized projection znižuje query latency, ale potrebuje source generation, lag a rebuild contract.

```text
business query
→ exact subject a freshness requirement
→ routing/partition
→ index alebo scan/traversal
→ visibility/consistency
→ result a authority interpretation
```

Fast query nad stale projection nie je správny outcome, ak rozhoduje o authorization, available balance alebo operation finality.

## 10. Consistency a read semantics

Consistency nie je jedna property všetkých database reads. Potrebné sú explicitné guarantees: read-your-writes, monotonic reads, causal ordering, bounded staleness, snapshot view alebo linearizable authoritative decision.

Projection môže mať eventual consistency a UI môže zobrazovať `processing`, pokiaľ je staleness bounded a business action sa stále overí vo authoritative store. Rovnaká stale projection nesmie autorizovať duplicate settlement alebo tvrdiť final failure/success bez ledger proofu.

Relational engine s ACID transaction nevytvára automaticky global consistency cez cache, document view, broker a provider. End-to-end model musí zachovať operation identity, event ordering, idempotency a reconciliation.

## 11. Polyglot persistence a authority graph

Polyglot persistence je legitímna, keď rôzne stores riešia odlišné workloady a authority zostáva jednoznačná. Atlas môže používať PostgreSQL pre ledger, document store pre merchant read model, Redis pre cache/idempotency window, object storage pre immutable evidence a search engine pre support discovery.

```text
PostgreSQL authoritative commit
→ outbox/change stream
→ document/search/cache projections
→ lag a generation evidence
→ rebuild/reconcile from authority
```

Každý derived store má source, transform generation, checkpoint, freshness, failure/duplicate handling, rebuild a delete/retention semantics. Direct write do projectionu, bidirectional sync bez conflict authority alebo last-write-wins medzi stores vytvára multi-master business state, aj keď to architecture diagram nepomenúva.

## 12. Worked incident `DB-PAY-56`

Atlas malo authoritative `settlement` a `settlement_attempt` tables v PostgreSQL. Merchant UI čítalo document projection `merchant_settlement_view`. Projection sa mala meniť iba z ordered outbox events.

Release 8.0 pridával `merchant_operation_id` pre stable idempotency a uniqueness. Počas mixed-version rollout-u nový API writer zapisoval relational transaction, legacy retry worker pri missing projection documente vytvoril document priamo a repair job mal fallback `document newer wins`. Tým vznikli tri authority paths.

Súbežne migration nad približne `780 miliónmi` rows nemala supporting partial index. Batch scans predĺžili transactions, WAL vzrástol `6.4×`, standby replay lag dosiahol `94 s` a application timeout retries `3.1×`. AZ network failure spustila failover; asynchronous standby chýbala časť acknowledged relational writes a old primary pokračovala vo writes ďalších `93 s`.

Document projection skryla authoritative gap: niektoré UI records existovali bez settlement/outbox transaction, iné ostali stale a repair job zapisoval status späť podľa document timestampu. `286` merchant operations vyžadovalo reconciliation a `37` intents bolo potvrdených clientovi, ale chýbalo na promoted relational history.

Triggerom bola kombinácia migration loadu a AZ network failure. Data-model root cause bol nejasný authority graph: document projection mohla byť written ako fallback a repair používal last-write-wins namiesto ledger/event lineage. HA root cause a migration causes sú rozpracované v ďalších kapitolách.

## 13. Evidence-preserving containment a recovery

Tím zastavil direct document writers a last-write-wins repair, fenced old/new relational writers podľa explicitnej epoch authority, pozastavil migration a blind retries a zachoval WAL timelines, outbox/broker checkpoints, document versions, transform generations a provider ledger evidence.

Operations sa klasifikovali podľa business keyu na authoritative relational commit present, old-primary-only, document-only, never-sent, sent-unknown, completed a duplicate-attempt. Jedna relational timeline bola zvolená ako authority; exact safe manifests doplnili chýbajúce intents alebo correlation records, provider ledger rozhodol external outcomes a projections sa rebuildli z authoritative streamu.

Redesign odstránil direct projection writes, zaviedol stable `merchant_id + merchant_operation_id` uniqueness, writer epoch v records/events, projection source/checkpoint metadata, stale-state UI semantics, authoritative action checks a continuous reconciliation canary.

## 14. Data-model acceptance contract

Positive path musí preukázať, že business operation vstúpi do jednej authoritative atomic boundary, derived events/projections vzniknú z commit lineage a intended reads spĺňajú query/freshness contract. Retry path musí použiť stable identity a vrátiť pôvodný outcome. Migration/failover path musí zachovať authority aj pri mixed generations.

Forbidden paths musia zlyhať: direct projection write, document-only authoritative settlement, duplicate business key, stale projection použitá na final/action decision, bidirectional last-write-wins, cross-partition operation bez explicitného protocolu a schema variant, ktorý readers ticho interpretujú inak.

```text
positive:
intent → authoritative commit → event → projection → read

retry:
same business key → same operation/outcome

rebuild:
projection lost → replay from authority → equivalent view

forbidden:
projection becomes writer
conflict resolved by timestamp alone
stale derived state authorizes mutation
```

Verdict patrí exact model, schema, partition, transform a application generation. Second store alebo second failure test overuje, že authority nie je iba dokumentačný claim.

## 15. Troubleshooting polyglot inconsistency

Pri rozdielnom state-e medzi stores začni business operation identity a authority mapou. Potom porovnaj authoritative commit/timeline, outbox/change stream, transform generation, checkpoint/lag, projection document a application routing/cache behavior. External provider ledger rozhoduje side effects, ktoré local stores nevedia samy potvrdiť.

```text
user-visible inconsistency
→ business key a expected invariant
→ authoritative store/timeline
→ commit/outbox/event identity
→ projection checkpoint a transform
→ document/cache/search state
→ mixed writer alebo stale reader
→ external effect/reconciliation
→ rebuild alebo exact repair
→ forbidden second-write validation
```

Náhodný manual edit derived documentu môže symptom skryť a zničiť causal evidence.

## 16. Anti-patterny

Data-model anti-patterny zamieňajú product feature alebo read convenience za authority a correctness contract.

- **SQL versus NoSQL podľa trendu —** ignoruje invariants, access paths, distribution a recovery.
- **Flexible schema znamená bez schema —** readers, validators, indexes a historical shapes stále tvoria contract.
- **Transactions vyriešia zlý aggregate —** distributed transaction môže byť drahá a nevhodná náhrada locality.
- **Denormalizuj všetko —** duplicate state bez ownera a reconciliation vytvára divergence.
- **Projection môže opraviť source —** derived view nemá authority na reverse write bez explicitného business protocolu.
- **Last-write-wins vyrieši konflikt —** clock/order nerozhoduje business validity ani external side effect.
- **Sharding je automatické scale-out —** zavádza placement, cross-shard a rebalance failure modes.
- **Fast read je správny read —** stale projection môže byť neprijateľná pre action alebo finality.

## 17. Kontrolné otázky

1. Čo tvorí exact data-system subject a field-authority map?
2. Kedy relational model poskytuje najsilnejšiu hodnotu?
3. Ako document aggregate boundary súvisí s atomicitou?
4. Na aké workloads sú vhodné key-value, wide-column, graph a time-series systems?
5. Prečo moderné transactions nenahrádzajú schema/aggregate design?
6. Ako sa business key a shard key líšia?
7. Čo je risk skorého shardingu?
8. Ako access paths ovplyvňujú model a indexes?
9. Kedy je eventual consistency prijateľná?
10. Ako polyglot persistence zachováva jednoznačnú authority?
11. Prečo document projection skryla a zosilnila `DB-PAY-56`?
12. Ktoré positive, retry, rebuild a forbidden paths patria do acceptance?

## Glossary impact

Relevantné pojmy: data-system subject, field authority, relational model, document aggregate, key-value/wide-column/graph/time-series model, aggregate boundary, schema generation, business key, partition/shard key, access-path contract, derived projection, projection checkpoint, authority graph, polyglot persistence, rebuildable state a data-model acceptance contract.

## Primárne zdroje

- [PostgreSQL Documentation](https://www.postgresql.org/docs/current/)
- [MySQL 8.4 Reference Manual — InnoDB](https://dev.mysql.com/doc/refman/8.4/en/innodb-storage-engine.html)
- [MongoDB Manual — Data Modeling](https://www.mongodb.com/docs/manual/data-modeling/)
- [MongoDB Manual — Transactions](https://www.mongodb.com/docs/manual/core/transactions/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Operational readiness](../14-sre-and-operations/operational-readiness.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Transactions a ACID →](transactions-and-acid.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
