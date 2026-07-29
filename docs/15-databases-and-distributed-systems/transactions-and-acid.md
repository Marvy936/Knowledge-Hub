# Transactions a ACID

Transaction je bounded state transition, ktorá musí databázu previesť z jedného validného stavu do druhého. `BEGIN` a `COMMIT` nie sú iba syntaktické obalenie príkazov; definujú visibility, concurrency, durability, retry a acknowledgement contract business operácie.

```text
business operation a invarianty
→ exact transaction subject
→ read set, write set a preconditions
→ isolation/concurrency mechanism
→ statement execution
→ constraint a conflict verdict
→ commit protocol a durable boundary
→ acknowledgement alebo unknown outcome
→ retry/reconciliation
→ second-operation validation
```

ACID vlastnosti opisujú požadované správanie transaction systému. Samy však nehovoria, či aplikácia zvolila správnu transaction boundary, isolation level, idempotency contract alebo multi-system workflow.

## 1. Exact transaction subject

Transaction subject má uvádzať:

- business operation a actor;
- transaction ID alebo correlation identity;
- database, schema a topology generation;
- read set, write set a dependent records;
- preconditions a invarianty;
- isolation level;
- locking alebo optimistic-concurrency mechanismus;
- commit a acknowledgement boundary;
- timeout, retry a cancellation semantics;
- external side effects;
- expected allowed a forbidden outcomes.

Príklad:

```text
operation: create settlement intent
key: merchant_id + merchant_operation_id
read set: existing operation identity
write set:
  settlement_intent
  outbox_event
invarianty:
  operation identity is unique
  settlement and outbox appear together
isolation: READ COMMITTED + unique constraint
commit boundary: PostgreSQL COMMIT succeeds
aack boundary: HTTP 202 after commit
retry: same idempotency key returns existing outcome
```

## 2. Atomicity

Atomicity znamená, že transaction write set sa stane viditeľný ako jeden committed outcome alebo sa celý abortne.

```text
valid state A
→ execute multiple changes
→ COMMIT
→ valid state B
```

Ak transaction abortne:

```text
valid state A
→ partial internal work
→ ROLLBACK/abort
→ externally visible state remains A
```

Atomicity platí v hranici konkrétneho transaction managera. Dva autocommit writes do rovnakej databázy nie sú jedna transaction. Writes do dvoch nezávislých databases nie sú atomic bez distributed coordination alebo iného workflow contractu.

## 3. Consistency

ACID consistency neznamená, že databáza automaticky pozná všetky business pravidlá. Znamená, že transaction pri dodržaní deklarovaných constraints a aplikačnej logiky prechádza medzi validnými stavmi.

Consistency môže byť chránená cez:

- primary a unique keys;
- foreign keys;
- `CHECK` constraints;
- exclusion constraints;
- triggers;
- generated values;
- transaction logic;
- state-machine preconditions;
- conditional updates;
- serialization checks.

Invariant, ktorý existuje iba v dokumentácii, databáza nevynúti. Invariant v aplikácii môže byť porušený iným writerom, migration scriptom alebo concurrent requestom.

## 4. Isolation

Isolation určuje, aké effects concurrent transactions môžu navzájom pozorovať a ktoré interleavings sú povolené.

### Bežné anomálie

#### Dirty read

Transaction číta uncommitted write inej transaction, ktorá môže abortnúť.

#### Non-repeatable read

Rovnaká row prečítaná dvakrát v jednej transaction vráti inú committed hodnotu.

#### Phantom

Opakovaná predicate query vráti inú množinu rows pre concurrent inserts/deletes.

#### Lost update

Dve transactions prečítajú rovnaký stav a neskorší write prepíše zmenu prvej.

#### Write skew

Transactions menia odlišné rows na základe spoločnej precondition a spolu porušia invariant, hoci nevznikne direct row conflict.

Isolation level treba vyberať podľa konkrétnych invariantov, nie podľa názvu `najsilnejší` alebo `default`.

## 5. PostgreSQL isolation model

PostgreSQL používa MVCC a podporuje Read Committed, Repeatable Read a Serializable behavior. Pri vyššej isolation môže správnou reakciou byť serialization failure a retry celej transaction.

### Read Committed

Každý statement typicky pracuje s novým snapshotom committed dát. Je vhodný pre mnoho OLTP operácií, ak constraints, row locks alebo conditional writes chránia relevantné invarianty.

### Repeatable Read

Transaction pracuje so stabilnejším snapshotom. Stále potrebuje conflict a retry model a nemá byť zamieňaná s automatickou ochranou každého business invariant-u.

### Serializable

Cieľom je outcome ekvivalentný nejakej serial execution. Databáza môže transaction abortnúť, ak nevie bezpečne potvrdiť serial order. Application musí retryovať celú transaction, nie iba posledný statement.

## 6. MVCC

Multi-Version Concurrency Control uchováva viac versions rows, aby readers a writers nemuseli vždy vzájomne blokovať.

```text
transaction snapshot
→ visible row versions
→ concurrent new versions
→ commit/abort metadata
→ future snapshots see committed versions
→ vacuum/garbage collection retires obsolete versions
```

MVCC znižuje časť read/write contentionu, ale neodstraňuje:

- write/write conflicts;
- row a table locks;
- unique constraint races;
- long-running transaction impact;
- vacuum/version-retention pressure;
- serialization failures;
- DDL lock conflicts.

Long transaction môže držať starý snapshot, zväčšovať dead tuples a predlžovať recovery alebo replication pressure.

## 7. Pessimistic a optimistic concurrency

### Pessimistic locking

```text
read target FOR UPDATE
→ acquire lock
→ verify state
→ mutate
→ commit
→ release lock
```

Je vhodné, keď conflict je pravdepodobný alebo operation potrebuje exclusive ownership. Nevýhody sú wait, deadlock a reduced concurrency.

### Optimistic concurrency

```text
read value + version
→ compute change
→ UPDATE ... WHERE id = ? AND version = ?
→ affected-row verdict
→ commit alebo retry
```

Je vhodná pri nižšom conflict rate a krátkych operations. Musí kontrolovať affected-row count a rozlíšiť conflict od success.

## 8. Locks, waits a deadlocks

Locks chránia data a metadata objects. Transaction môže držať locks do commit/rollback-u. Lock wait nie je automaticky deadlock.

Deadlock vznikne, keď transactions vytvoria cycle:

```text
T1 holds A, waits for B
T2 holds B, waits for A
```

Databáza jednu transaction abortne. Prevencia zahŕňa:

- stabilné poradie acquisition;
- kratšie transactions;
- menší lock footprint;
- vhodné indexes;
- oddelenie user/network wait od transaction;
- bounded timeout a full retry.

Retry bez backoff, idempotency a scope-u môže vytvoriť ďalší contention storm.

## 9. Durability a commit

Durability určuje, čo sa stane s committed transaction po process, host, storage alebo topology failure-i.

Commit contract môže zahŕňať:

```text
write log/WAL generation
→ local durable flush
→ replica transfer/flush/apply podľa policy
→ commit success
→ client acknowledgement
```

Presná boundary závisí od database engine a configuration. `COMMIT succeeded` na primary nemusí znamenať, že write už existuje na asynchronous standby. Naopak, timeout alebo lost response neznamená, že transaction necommitla.

## 10. Unknown commit outcome

Najkritickejší retry scenár:

```text
client sends COMMIT alebo final write
→ database commits
→ connection/response sa stratí
→ client nevie, či outcome committed
```

Blind retry môže vytvoriť duplicate business side effect. Bezpečný contract používa:

- stable idempotency/business key;
- unique constraint;
- queryable operation status;
- transaction/reconciliation identity;
- retry of whole transaction;
- provider alebo external idempotency;
- explicit unknown outcome classification.

## 11. Transactions a external side effects

Database transaction nemôže rollback-nuť email, HTTP request alebo provider payment, ktorý už external system prijal.

Nebezpečný model:

```text
BEGIN
→ update database
→ call provider
→ COMMIT
```

Ak provider succeeds a database commit zlyhá, external effect existuje bez local state-u. Ak database commit succeeds a provider response sa stratí, outcome je unknown.

Bežné patterns:

- transactional outbox;
- inbox/deduplication;
- saga a compensating action;
- idempotent external operation;
- reconciliation against external authority.

Tieto patterns nenahrádzajú local transaction. Spájajú local atomic transition s asynchronous external workflowom.

## 12. Autocommit

Autocommit znamená, že každý statement tvorí vlastnú transaction, pokiaľ application explicitne nezačne širšiu transaction.

```text
INSERT settlement       -- transaction 1
INSERT outbox_event      -- transaction 2
```

Medzi statements môže process crashnúť, connection zlyhať alebo concurrent reader pozorovať partial state. Framework alebo ORM môže autocommit zapnúť, aj keď developer logicky vníma method call ako jednu operáciu.

Overuj runtime behavior:

- transaction begin/commit logs;
- connection/ORM configuration;
- statement grouping;
- exception a rollback handling;
- connection-pool reset;
- nested transaction/savepoint semantics.

## 13. Savepoints

Savepoint umožňuje rollback časti transaction:

```text
BEGIN
→ write A
→ SAVEPOINT s1
→ write B
→ failure
→ ROLLBACK TO s1
→ write C
→ COMMIT
```

Neznamená samostatný durable commit. Outer transaction stále rozhoduje o final visibility a durability.

## 14. Transaction length

Transaction má byť dostatočne široká na ochranu invariant-u a dostatočne krátka na obmedzenie contentionu.

Do open transaction nepatrí bez dôvodu:

- čakanie na user input;
- dlhý HTTP call;
- large batch bez checkpointov;
- pomalý file transfer;
- indefinite queue wait;
- unbounded retry loop.

Long transaction môže držať locks, snapshots, connections a WAL retention. Rozdelenie batchu však musí zachovať resumability a correctness.

## 15. Worked incident `DB-PAY-56`

Release `payments 8.0` používal nový create flow:

```text
statement 1: INSERT settlement_intent
             ON CONFLICT DO NOTHING
             -- autocommit

statement 2: UPSERT document projection

statement 3: INSERT outbox_event
             -- autocommit

return HTTP 202
```

Developer predpokladal, že application method je transaction. ORM configuration však používala autocommit a document write bežal cez iný client.

Počas AZ network failure-u:

1. `settlement_intent` commitol na PostgreSQL primary;
2. response k statementu sa stratila;
3. application retry našiel existing intent;
4. document upsert prešiel;
5. outbox insert neprebehol pre connection reset;
6. retry path vrátil `202`, pretože intent už existoval;
7. provider operation nikdy nevznikla.

Súčasne niektoré balance-reservation transitions používali:

```text
SELECT available_amount
→ application computes new value
→ UPDATE account_balance
```

bez row locku alebo version predicate. Concurrent requests preto mohli vytvoriť lost update.

### Root causes

- settlement a outbox neboli v jednej transaction;
- idempotency success bol odvodený iba z existencie settlement row;
- transaction boundary bola predpokladaná z application methodu, nie overená runtime evidence;
- read-modify-write flow nemal concurrency contract;
- acknowledgement neoveroval complete durable intent.

## 16. Competing hypotheses a evidence

Pri chýbajúcom outbox evente treba rozlíšiť:

1. settlement transaction abortla;
2. settlement commitla, outbox statement sa nikdy nezačal;
3. outbox commitol a neskôr bol deleted;
4. read smeruje na stale replica;
5. transaction commit outcome je unknown;
6. projection write skryl local failure;
7. unique conflict vrátil existing, ale incomplete operation.

Evidence:

```text
business/idempotency key
→ application attempt a connection ID
→ transaction begin/commit/rollback evidence
→ WAL/LSN a row creation metadata
→ outbox unique key a audit
→ replica replay position
→ document version
→ broker/provider evidence
```

## 17. Evidence-preserving containment

```text
zastaviť incomplete write path
→ zachovať DB/ORM/connection/WAL evidence
→ neblind-retryovať provider operations
→ fence dual writers
→ inventory incomplete operation cohorts
→ prepnúť create flow na atomic relational transaction
→ obmedziť admission podľa reconciliation capacity
```

## 18. Authoritative remediation

Atomic create:

```sql
BEGIN;

INSERT INTO settlement_intent (
    merchant_id,
    merchant_operation_id,
    state
)
VALUES ($1, $2, 'accepted')
ON CONFLICT (merchant_id, merchant_operation_id)
DO NOTHING;

INSERT INTO outbox_event (
    merchant_id,
    merchant_operation_id,
    event_type
)
SELECT $1, $2, 'SettlementAccepted'
WHERE NOT EXISTS (
    SELECT 1
    FROM outbox_event
    WHERE merchant_id = $1
      AND merchant_operation_id = $2
);

COMMIT;
```

Production implementation má navyše kontrolovať affected rows, existing complete state a exact operation identity. Po commit-e sa projection vytvára z durable outbox/CDC streamu.

Balance transition používa row lock alebo conditional version update. Serialization/deadlock failures retryujú celú transaction s bounded backoffom.

## 19. Transaction acceptance verdict

Transaction design je prijatý, keď:

- exact business operation a invarianty sú explicitné;
- read/write set a authority sú známe;
- transaction boundary zodpovedá invariant-u;
- autocommit a ORM runtime behavior sú overené;
- isolation level pokrýva relevantné anomalies;
- locks alebo optimistic predicates majú bounded conflict model;
- constraints sú authoritative, nie iba application checks;
- commit/acknowledgement a replication semantics sú explicitné;
- unknown outcome má idempotency a reconciliation path;
- external side effects používajú outbox/saga alebo ekvivalentný contract;
- deadlock/serialization retryuje celú operation;
- allowed, forbidden, concurrent a second-operation testy prejdú.

## 20. Troubleshooting flow

```text
partial, duplicate alebo lost state
→ exact business operation a invariant
→ runtime transaction/autocommit boundary
→ read/write set a constraints
→ isolation snapshot a locks
→ commit/rollback/unknown outcome
→ replica visibility
→ external side-effect evidence
→ retry/idempotency behavior
→ bounded reconciliation
→ second concurrent operation validation
```

## 21. Anti-patterny

### Method s anotáciou je určite transaction

Proxy, connection, nested-call alebo exception semantics môžu runtime boundary zmeniť.

### ACID znamená, že application je correct

Nesprávna transaction boundary môže byť dokonale ACID a stále porušiť business invariant.

### Vyšší isolation level opraví všetko

Stále potrebuje constraints, retry, short transactions a external-effect contract.

### Timeout znamená rollback

Commit mohol prejsť a response sa stratiť.

### Retry posledného statementu

Serialization/deadlock retry musí znovu vyhodnotiť celú operation z nového state-u.

### Drž lock počas provider callu

Zvyšuje contention a stále nerieši atomicitu external side effectu.

## 22. Kontrolné otázky

1. Čo tvorí exact transaction subject?
2. Ako sa ACID atomicity líši od business workflow atomicity?
3. Ktoré constraints chránia consistency?
4. Aké anomalies isolation rieši?
5. Ako MVCC funguje a čo nerieši?
6. Kedy použiť pessimistic a optimistic concurrency?
7. Ako vzniká deadlock?
8. Čo je unknown commit outcome?
9. Prečo database transaction nevie rollback-nuť provider call?
10. Ako autocommit porušil `DB-PAY-56`?
11. Prečo musí serialization failure retryovať celú transaction?
12. Čo overuje transaction acceptance verdict?

## Glossary impact

Relevantné pojmy: transaction subject, atomicity, consistency, isolation, durability, MVCC, transaction snapshot, lost update, write skew, pessimistic locking, optimistic concurrency, serialization failure, unknown commit outcome, transaction acknowledgement boundary, autocommit, savepoint, transactional outbox a transaction acceptance verdict.

## Primárne zdroje

- [PostgreSQL Documentation — Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [PostgreSQL Documentation — Explicit Locking](https://www.postgresql.org/docs/current/explicit-locking.html)
- [PostgreSQL Documentation — Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html)
- [MongoDB Manual — Transactions](https://www.mongodb.com/docs/manual/core/transactions/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Relational vs. non-relational databases](relational-vs-non-relational-databases.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Indexy, locks a migrations →](indexes-locks-and-migrations.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
