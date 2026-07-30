# Transactions a ACID

Transaction je bounded state transition, ktorá má previesť autoritatívny data state z jedného validného stavu do druhého. `BEGIN` a `COMMIT` nie sú iba syntaktické obalenie SQL príkazov; určujú snapshot a visibility, conflict coordination, constraint evaluation, durable acknowledgement, retry a recovery semantics jednej business operation.

ACID opisuje dôležité vlastnosti lokálnej transaction boundary, nie automatickú correctness celého distributed workflowu. Databáza môže atomicky commitnúť settlement a outbox, no nevie sama garantovať, že external provider vykonal operation exactly once alebo že document projection už zobrazuje nový stav. End-to-end návrh musí vedieť, čo transaction chráni, ktoré facts sú mimo nej a ako sa rieši unknown commit outcome.

## 1. Dominantný operation-to-durable-outcome lifecycle

Transaction design začína business intentom a invariantmi. Application načíta alebo vytvorí relevantný state, databáza koordinuje concurrent changes, constraints rozhodnú prípustnosť a commit vytvorí durable generation. Až potom môže application pravdivo potvrdiť local outcome a pokračovať do derived alebo external effects.

```text
business operation a stable identity
→ exact transaction subject a invariant set
→ begin a snapshot/visibility contract
→ read/validate/lock authoritative state
→ write-set a constraint evaluation
→ conflict, abort/retry alebo commit decision
→ durable commit position
→ truthful acknowledgement
→ outbox/event/external descendant processing
→ reconciliation a second-operation validation
```

Každá šípka je samostatná boundary. Successful SQL statement pred `COMMIT` nie je durable business outcome. Stratená commit response nevytvára automaticky failure; môže znamenať committed-but-unknown operation, ktorú treba resolve-nuť podľa stable identity a authoritative read-backu.

## 2. Exact transaction subject

Tvrdenie `request je v transactione` je príliš nepresné. Exact subject zachováva business operation a idempotency key, database/cluster a primary generation, schema a application version, isolation/read consistency, read-set a write-set, constraints, explicit a implicit locks, timeout/deadlock policy, external descendants, acknowledgement boundary, retry rules a audit/commit identity.

```text
subject: TX-PAY-56-merchant-operation
operation: accept settlement intent
identity: merchant_id + merchant_operation_id
primary: postgres timeline 91 / writer epoch 12
isolation: READ COMMITTED + unique constraint/locking read
read-set: merchant, account policy, existing operation
write-set: settlement + settlement_attempt + outbox
acknowledgement: HTTP 202 až po durable COMMIT
retry: same business key, bounded attempts
external effect: provider command iba z committed outbox
```

Zmena isolation levelu, transaction boundary, constraint, primary timeline alebo retry implementation mení effective contract. Dve application generations môžu používať rovnaké tables, ale chrániť iné invariants.

## 3. Atomicity, consistency, isolation a durability

**Atomicity** znamená, že databáza publikuje celý local write-set alebo žiadny. Settlement row bez outbox commandu by porušila workflow invariant; jedna transaction ich môže commitnúť spolu.

**Consistency** v ACID neznamená všeobecnú distributed consistency. Znamená, že transaction rešpektuje databázou a application protokolom definované invariants: types, constraints, uniqueness, referential rules a explicitné business checks. Chýbajúci constraint alebo chybná application predicate môže commitnúť business-neplatný state a stále byť technicky úspešná transaction.

**Isolation** určuje, ktoré concurrent effects sú viditeľné a aké anomalies alebo serialization failures môže application pozorovať. Izolácia sa nesmie interpretovať iba názvom levelu; engine-specific semantics, statement snapshots, locking reads a application retry contract rozhodujú o výsledku.

**Durability** viaže acknowledged commit na persistent log/storage a prípadne replica acknowledgement policy. Local WAL flush môže splniť engine durability na primary, ale nemusí spĺňať business RPO pri strate failure domainu. Durability tiež nechráni pred neskorším validne commitnutým logical delete alebo corruption.

## 4. Transaction lifecycle a acknowledgement

Praktický lifecycle vedie cez connection a transaction context, snapshot, reads, locks, writes, validation, commit protocol, durable position a response.

```text
BEGIN
→ establish statement/transaction visibility
→ read a validate current state
→ acquire required locks alebo conflict metadata
→ execute writes
→ check constraints a conflicts
→ append/flush commit record
→ publish visibility
→ return outcome
```

Failure pred durable commit je abort alebo rollback. Failure po durable commit, ale pred client response, je unknown-to-client. Application nemá opakovať operation s novou identity; musí retry-nuť s rovnakým idempotency keyom a nájsť committed outcome alebo bezpečne pokračovať v tej istej operation.

Acknowledgement contract musí byť pravdivý. Ak API vráti `202` pred settlement/outbox commitom, crash môže vytvoriť potvrdený intent bez durable state-u. Ak odpoveď čaká na local commit, ale business deklaruje zero-loss regional RPO, replication policy a failover contract musia tento sľub podporovať alebo musí existovať reconstructability.

## 5. MVCC, snapshots a visibility

Multi-Version Concurrency Control udržiava viac versions rows a umožňuje readers pracovať so snapshotom bez blokovania každého writera. PostgreSQL statement alebo transaction vidí data podľa isolation semantics a concurrent writer vytvára novú row version; old versions zostávajú potrebné, kým ich môže vidieť active snapshot.

MVCC nezruší locks, conflicts ani cleanup cost. Writers môžu konfliktovať na rovnakom row/unique keyu, DDL potrebuje table/metadata locks a long transaction drží old snapshot, čím predlžuje vacuum/version retention, storage/WAL a replica recovery pressure. PostgreSQL dokumentácia explicitne kombinuje MVCC s row/table locking facilities pre situácie, kde snapshot semantics nestačia. citeturn758521search15turn758521search35

Snapshot je pozorovanie konkrétnej database history, nie automaticky latest truth. Long report alebo backfill môže čítať konzistentný, ale starý state. Read-after-write alebo authoritative action môže vyžadovať primary/current transaction path, nie arbitrary replica alebo cache.

## 6. Isolation levels a anomalies

Isolation level je trade-off medzi concurrency, observed consistency a retry rate. `READ COMMITTED` typicky vytvára nový snapshot pre každý statement; dva reads v jednej transaction môžu vidieť iný committed state. `REPEATABLE READ` drží stabilnejší snapshot, ale engine-specific behavior stále môže vyžadovať conflict handling. `SERIALIZABLE` sa snaží, aby výsledok zodpovedal nejakému serial orderu, často za cenu serialization abortov, ktoré application musí retry-nuť celú transaction.

Relevantné anomalies sa viažu na invariant. Non-repeatable read môže zmeniť decision medzi dvoma statements. Phantom môže pridať row do predicate population. Write skew vzniká, keď dve transactions čítajú spoločný invariant a menia odlišné rows tak, že každý write je lokálne validný, no kombinácia invariant poruší. Lost update vzniká pri read-modify-write bez conflict detection.

Vyšší label neodstraňuje potrebu correct retry, timeout a business identity. Serialization failure po external side effecte je nebezpečná; external call preto nemá byť nekontrolovane vložený doprostred retryable DB transactionu.

## 7. Constraints ako concurrency authority

Constraint je executable invariant na authoritative write boundary. Unique constraint rieši race, ktorý application `SELECT then INSERT` nevie bezpečne uzavrieť:

```text
T1: SELECT operation absent
T2: SELECT operation absent
T1: INSERT
T2: INSERT
```

Bez uniqueness môžu oba inserts prejsť. S unique constraintom engine rozhodne conflict a application mapuje duplicate key na existing operation. Foreign key chráni referential edge, check constraint local domain rule a exclusion alebo engine-specific constraint môže chrániť širšie predicates.

Constraint musí mať correct key a scope. Unique `merchant_operation_id` bez merchant alebo tenant namespace môže false-conflictovať; naopak key bez business identity umožní duplicates. Constraint activation počas migration potrebuje historical data proof a compatibility s old/new writers.

Application-level validation zostáva potrebná pre authorization, workflow a cross-system facts. Constraint však chráni concurrency boundary aj pri inom writerovi, retry workerovi alebo ad-hoc SQL.

## 8. Locks, blocking a deadlocks

Locks serializujú conflicting operations a chránia state, ale nesprávny scope alebo duration vytvára queue a availability failure. Row locks, predicate/range locks, table locks a metadata locks majú odlišný conflict matrix. Query plan ovplyvňuje, koľko rows sa navštívi a zamkne; missing index môže zmeniť intended narrow update na veľký scan a lock footprint.

Deadlock vzniká cyklom wait-for dependencies. Engine typicky abortne jednu transaction; application musí celý bounded operation retry-nuť bezpečne. Lock timeout a statement timeout chránia latency, ale timeout nehovorí, či transaction commitla, bola zrušená alebo stále rollbackuje. Kill root blockera bez outcome modelu môže spustiť veľký rollback a zhoršiť pressure.

Diagnostika potrebuje wait graph: waiting transaction, requested lock, blocker, blocker age, statement, application owner, write-set a rollback implication. Počet active connections bez dependency graphu neidentifikuje causal session.

## 9. Transaction boundary a external side effects

Database transaction nemôže atomicky rollback-nuť už vykonaný email, broker publish alebo provider settlement, pokiaľ všetky strany nezdieľajú explicitný distributed transaction protocol. Na internete a cloud dependencies je bežnejší local atomic commit plus durable intent/outbox a idempotent external processing.

```text
DB transaction:
  settlement + outbox
→ commit
→ publisher odošle command
→ provider použije operation idempotency key
→ callback/ledger reconciliation
```

Volanie providera pred DB commitom vytvára external effect bez local authority pri rollbacku. Volanie po commite bez durable outboxu vytvára committed intent bez retry lineage pri process crashi. Outbox nevyrieši provider semantics sám; consumer potrebuje idempotency, attempt lineage a sent-unknown reconciliation.

Compensation je nová business operation, nie technický rollback minulosti. Refund, reversal alebo corrective event musí mať vlastnú identity, authorization a audit.

## 10. Retry, idempotency a unknown outcome

Retry policy sa viaže na failure stage. Serialization/deadlock abort pred commitom možno retry-nuť celú transaction s rovnakým business intentom. Network timeout pri commit response môže znamenať committed outcome; najprv sa hľadá podľa stable keyu. Timeout pri external call potrebuje provider idempotency/ledger.

Idempotency record musí byť v authority boundary alebo atomicky prepojený s operation. Cache-only key s krátkou TTL nemusí chrániť finančný retry po failover-e. Response reuse, status, payload hash a ownership/expiry semantics majú byť explicitné.

```text
same merchant + operation key
→ existing committed operation
→ return same accepted/final identity
nie nová settlement operation
```

Blind retry s novým request ID presúva unknown outcome do duplicate business effectu.

## 11. Long transactions a operational coupling

Long transaction drží locks, snapshot, connections, memory a old versions dlhšie. Zvyšuje block queue, deadlock surface, vacuum/undo pressure, WAL retention, replication lag a rollback duration. Batch, migration alebo report môže byť syntakticky správny, no operationalne porušiť OLTP SLO.

Bounded transaction design používa stable cursor, small commits, idempotent conditional update, max rows/time/WAL/lag, pause/resume a exact last committed progress. `25 000 rows per batch` nie je bounded, ak access path opakovane scan-ne stovky miliónov rows a každá transaction trvá jedenásť minút.

Transaction size sa hodnotí podľa actual work, lock duration, WAL/undo a downstream apply costu, nie iba počtu SQL statements.

## 12. Transaction component incidentu `DB-PAY-56`

Migration pridávala `merchant_operation_id` do `settlement_attempt` s približne `780 miliónmi` rows. Backfill vyberal `IS NULL ORDER BY created_at` bez supporting partial indexu, takže každá batch transaction opakovane scanovala veľkú časť table, trvala 4–11 minút a držala row locks aj old snapshots.

OLTP lock waits vzrástli na desiatky sekúnd, connection pool sa naplnil waiters a timeout retries zvýšili write load. WAL generation vzrástla `6.4×`, standby replay lag dosiahol `94 s` a autovacuum nemohlo efektívne retire-nuť old versions.

Súčasne application-only idempotency flow ešte nemal validný unique constraint. Mixed-version retries mohli vytvoriť relational/document divergence. Pri failover-e `37` client-acknowledged intents chýbalo na promoted history, pretože local async commit policy a promotion contract nezodpovedali business durability claimu.

Transaction root causes boli unbounded scan-heavy transaction, incomplete database-enforced operation identity, timeout/retry bez complete unknown-outcome modelu a acknowledgement policy oddelená od failover RPO.

## 13. Evidence-preserving containment a recovery

Tím pozastavil nové batches, znížil retry amplification a chránené OLTP admission, zachoval transaction/lock graph, plans, WAL/replication positions, committed backfill cursor a invalid/partial constraint state. Nezabíjal náhodné sessions ani nereštartoval database bez outcome classification.

Affected merchant operations sa porovnali podľa business keyu cez acknowledged responses, old/new relational timelines, outbox a provider ledger. Chýbajúce alebo unknown operations sa klasifikovali pred replayom. Backfill dostal supporting partial index, stable keyset cursor, menšie transactions a conditional updates. Historical duplicates sa opravili exact manifestom a až potom sa aktivoval validný unique constraint.

## 14. Transaction acceptance contract

Positive path musí atomicky commitnúť settlement, idempotency identity a outbox, po durable commit-e vrátiť truthful acknowledgement a publikovať derived command. Conflict path musí unique/serialization/lock conflict preložiť na existing operation alebo bounded retry. Unknown commit path musí read-backom resolve-nuť outcome.

Forbidden paths musia zlyhať: settlement bez outboxu, duplicate business key, external provider call pred local commit bez compensation contractu, retry s novou identity, long transaction nad lock/WAL/lag limits, stale replica použitá na authoritative decision a ACK pred durable boundary.

```text
positive:
intent → atomic commit → durable ack → descendant processing

conflict:
concurrent same key → one commit + existing outcome

unknown:
lost response → read-back by stable identity

forbidden:
partial local state
duplicate external effect
blind retry
unbounded transaction
```

Verdict patrí exact schema, constraint, isolation, retry, primary/replication a application generation. Second concurrent attempt a failover-window test overujú contract mimo happy pathu.

## 15. Troubleshooting transaction failure-u

Pri duplicate, stale alebo blocked operation začni business keyom a expected invariantom. Potom sleduj current primary/timeline, transaction IDs a states, snapshot/isolation, read/write set, locks/wait graph, constraints, commit/WAL position, response timing, retry identity a external descendants.

```text
business anomaly alebo latency
→ operation key a invariant
→ primary/timeline/schema generation
→ transaction state/snapshot
→ read/write set a constraints
→ locks/deadlock/root blocker
→ commit position a ACK
→ retry/idempotency
→ outbox/provider outcome
→ reconciliation a second attempt
```

Application log `timeout` bez commit/transaction evidence nie je outcome verdict.

## 16. Anti-patterny

Transaction anti-patterny zamieňajú syntaktickú transaction alebo izolovaný engine guarantee za end-to-end correctness.

- **BEGIN/COMMIT znamená ACID business workflow —** external effects a projections ostávajú mimo local boundary.
- **SELECT potom INSERT stačí —** concurrent writers potrebujú authoritative uniqueness alebo locking protocol.
- **Serializable znamená bez starostí —** application musí správne retry-nuť aborted transaction a nezdvojiť external effects.
- **Timeout znamená rollback —** commit response sa mohla stratiť; outcome je unknown.
- **MVCC znamená bez locks —** writers, constraints a DDL stále conflictujú a long snapshots vytvárajú pressure.
- **Veľká transaction je iba pomalšia —** drží locks/versions, generuje WAL a predlžuje rollback/failover.
- **Retry s novým ID je bezpečný —** môže vytvoriť novú business operation.
- **Database consistency znamená distributed consistency —** cache, broker, provider a projections potrebujú vlastný protocol.

## 17. Kontrolné otázky

1. Čo tvorí exact transaction subject?
2. Ako sa ACID consistency líši od distributed consistency?
3. Kedy vzniká unknown commit outcome?
4. Ako MVCC snapshot a locks spolupracujú?
5. Aké anomalies menia business invariant?
6. Prečo unique constraint rieši race lepšie než application check?
7. Ako lock graph pomáha pri blocking-u?
8. Prečo external call nepatrí nekontrolovane do retryable transactionu?
9. Ako outbox a provider idempotency spolupracujú?
10. Prečo long backfill transactions poškodili `DB-PAY-56`?
11. Ako acknowledgement a replication policy súvisia?
12. Ktoré positive, conflict, unknown a forbidden paths patria do acceptance?

## Glossary impact

Relevantné pojmy: transaction subject, transaction lifecycle, ACID boundary, snapshot visibility, MVCC version, isolation anomaly, write skew, authoritative constraint, lock/wait graph, unknown commit outcome, durable acknowledgement, transaction idempotency, external descendant, long-transaction pressure a transaction acceptance contract.

## Primárne zdroje

- [PostgreSQL Documentation — Concurrency Control](https://www.postgresql.org/docs/current/mvcc.html)
- [PostgreSQL Documentation — Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [PostgreSQL Documentation — Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html)
- [MySQL 8.4 Reference Manual — InnoDB Transaction Model](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-model.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Relational vs. non-relational databases](relational-vs-non-relational-databases.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Indexy, locks a migrations →](indexes-locks-and-migrations.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
