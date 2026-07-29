# Connection pooling

Connection pool nie je iba performance cache pre TCP spojenia. Je to concurrency, admission a session-state contract medzi application demand-om a databázovou execution capacity. Nesprávne navrhnutý pool môže vytvoriť connection storm, skryť overload v queue, vyčerpať database memory, predĺžiť transactions, zablokovať administratívny recovery access alebo porušiť application semantics pri zmene session, transaction alebo statement pooling mode-u.

```text
logical database demand
→ exact client/pool/server subject
→ connection a session setup cost
→ database concurrency envelope
→ pool topology a mode
→ admission, queue a timeout contract
→ checkout/use/transaction/reset/release
→ failover a stale-connection handling
→ saturation a fairness evidence
→ application/business outcome
→ second-burst a recovery validation
```

## 1. Exact pooling subject

Tvrdenie `pool má 40 connections` je neúplné. Pooling subject musí uvádzať:

- application/service a release generation;
- replica/Pod/process count;
- client library a pool generation;
- database endpoint, role a workload class;
- per-instance minimum, maximum a burst connections;
- total theoretical a effective connection count;
- connection/pooler/database layers;
- session, transaction alebo statement pooling mode;
- transaction a session-state requirements;
- database `max_connections`, reserved slots a safe execution concurrency;
- checkout, connect, statement, transaction a idle timeouts;
- queue discipline a overload behavior;
- failover/reconnect behavior;
- observability a acceptance boundaries.

Príklad:

```text
service: settlement-api 8.1
replicas: 96 Pods
application pool: min 5, max 40 per Pod
possible clients: 3 840
pooler: PgBouncer transaction mode
server pools: 120 PostgreSQL connections
PostgreSQL max_connections: 600
reserved/emergency envelope: 15
safe application envelope: 540
transaction p95: 85 ms
checkout objective: p99 <= 150 ms
session features: forbidden in transaction mode
```

Configured maxima nie sú automaticky simultaneously active demand, ale musia vstúpiť do worst-case a failure-mode modelu.

## 2. Prečo connections stoja resources

Database connection môže zahŕňať:

```text
TCP/TLS connection
→ authentication
→ backend/session process alebo thread
→ per-session memory a metadata
→ session parameters
→ prepared statements/temp objects
→ transaction snapshots a locks
→ result buffers
→ cleanup/reset
```

PostgreSQL používa server backend pre každú priamu client connection a časť resources dimenzuje podľa `max_connections`. MySQL defaultne používa one-thread-per-connection model; server-side thread pool je odlišný od client-side connection poolu. Redis používa multiplexed non-blocking client handling, ale stále má file descriptors, buffers, output limits a per-client state.

Connection limit preto nie je iba socket limit. Príliš veľa simultaneously executing queries môže preťažiť CPU, memory, storage, lock manager a cache aj vtedy, keď server nové connections technicky prijme.

## 3. Pooling layers

Pool môže existovať na viacerých vrstvách:

1. **Application pool** — HikariCP, Npgsql, JDBC/.NET/Go client pool.
2. **Sidecar/local proxy** — per-Pod alebo per-host pooling.
3. **Shared external pooler** — napríklad PgBouncer.
4. **Managed database proxy** — provider-managed connection multiplexing.
5. **Database thread/execution pool** — server-side concurrency management.

Ak sa vrstvy násobia bez spoločného budgetu:

```text
Pods × app pool max × database/user pools × environments
```

môže theoretical demand výrazne prekročiť database capacity. Shared pooler nezruší application queues; iba pridá ďalšiu queue a resource boundary.

## 4. Session, transaction a statement pooling

### Session pooling

Server connection patrí clientovi počas celého client session-u.

Výhody:

- session-local state funguje prirodzene;
- temporary tables, session variables a advisory locks môžu zostať viazané na session;
- protocol behavior je najbližšie priamemu connection modelu.

Nevýhody:

- slabšie multiplexing;
- veľa idle clients môže držať veľa server connections;
- reconnect storm sa prenáša bližšie k databáze.

### Transaction pooling

Server connection sa vráti do poolu po skončení transaction.

```text
client A transaction 1 → server connection X
client B transaction 1 → server connection X
client A transaction 2 → server connection Y
```

Application nesmie predpokladať server-session affinity medzi transactions. Rizikové sú najmä:

- session-level `SET` mimo každej transaction;
- temporary tables;
- session advisory locks;
- `LISTEN/NOTIFY` session assumptions;
- connection-local prepared statements bez pooler supportu;
- cursors alebo state presahujúci transaction;
- session identity alebo tenant context;
- transaction boundaries skryté frameworkom.

Tenant context musí byť transaction-local a explicitný:

```sql
BEGIN;
SET LOCAL app.tenant_id = 'merchant-42';
-- všetky queries tejto business transaction
COMMIT;
```

Aj to vyžaduje, aby každá relevantná operation skutočne bežala v tej istej transaction.

### Statement pooling

Server connection sa uvoľní po každom statemente. Multi-statement transactions nie sú podporované. Je vhodný iba pre veľmi obmedzené stateless workloads.

Pooling mode je compatibility decision, nie transparentný performance switch.

## 5. Sizing connection poolu

Pool size sa nemá odvodiť iba od počtu application threads. Potrebuje:

- database safe execution concurrency;
- počet workload classes;
- replica/failover topology;
- query/service-time distribution;
- transaction duration;
- external waits držané počas transaction;
- burst a retry amplification;
- reserved recovery/admin slots;
- background jobs, migrations a observability clients;
- failover/reconnect behavior.

Jednoduchá kapacitná kontrola:

```text
safe DB application connections
÷ active application replicas
= rough per-replica upper envelope
```

Nie je to finálny tuning vzorec. Ak databáza bezpečne spracuje 200 concurrent active queries, 540 open server connections môže byť prijateľných iba vtedy, ak pool/admission obmedzí active execution a väčšina sessions neudržiava costly transactions alebo buffers.

Littleov zákon poskytuje useful sanity check:

```text
concurrency ≈ throughput × average service time
```

Pri `2 000 queries/s` a average database service time `20 ms` je priemerná execution concurrency približne `40`. Tail latency, bursts, lock waits a multi-query transactions však vyžadujú headroom a meranie, nie mechanické nastavenie poolu na 40.

## 6. Min, max a warmup

### Minimum/idle connections

Vysoké minimum na každom Pode môže po scale-out-e okamžite vytvoriť storm:

```text
100 Pods × minIdle 10 = 1 000 connections
```

Aj bez trafficu.

### Maximum connections

Maximum je admission boundary. Ak je príliš vysoké, overload sa presunie do database. Ak je príliš nízke bez bounded queue/timeouts, clients môžu čakať neobmedzene a spôsobiť request/thread exhaustion.

### Warmup

Pool warmup má byť:

- rate-limited;
- jittered;
- readiness-aware;
- dependency-capacity-aware;
- failover-aware;
- bounded podľa rollout cohortu.

Readiness, ktorá čaká na naplnenie celého poolu, môže počas database incidentu vytvoriť restart/reconnect loop.

## 7. Checkout a queue contract

Application request môže čakať:

```text
request admission
→ application worker/thread
→ pool queue
→ connection checkout
→ transaction/query
→ result
→ connection release
```

Treba merať oddelene:

- pool queue depth;
- checkout wait distribution;
- connect attempts/failures;
- active/idle connections;
- transaction duration;
- idle-in-transaction sessions;
- statement latency;
- database wait events;
- pool timeouts a cancellations;
- request deadline remaining po checkout-e.

Ak request strávi 4 sekundy v pool queue a query 30 ms, query dashboard môže byť zelený, ale user latency je zlá.

Pool timeout musí byť kratší než upstream request deadline a musí zanechať čas na controlled fallback alebo error. Retry po pool timeout-e bez admission control zosilňuje overload.

## 8. Pool reset a state hygiene

Pri reuse connection treba klasifikovať session state:

- open transaction alebo failed transaction state;
- session variables;
- role/search path;
- temporary objects;
- prepared statements;
- advisory locks;
- `LISTEN` registrations;
- timezone/locale;
- application name a tracing context.

Reset contract závisí od pooling mode-u. V transaction pooling mode sa nesmie spoliehať na session reset medzi každou client transaction ako na náhradu za stateless application design.

Forbidden outcome:

```text
client A nastaví privileged alebo tenant-specific state
→ connection sa vráti do poolu
→ client B zdedí effective state
```

Positive test musí dopĺňať cross-client negative test.

## 9. Transactions a pool release

Connection sa má uvoľniť až po jednoznačnom transaction outcome-e:

- committed;
- rolled back;
- connection discarded pre unknown/broken state.

Framework môže connection vrátiť do poolu po exception-e bez rollbacku. Ďalší borrower potom dostane connection v `transaction aborted` alebo s otvorenou transaction.

Kontroly:

- `try/finally` alebo framework-managed cleanup;
- rollback pri cancellation/timeoute;
- discard connection po protocol/network ambiguity;
- maximum transaction duration;
- idle-in-transaction timeout;
- leak detection;
- second-borrow validation.

## 10. Prepared statements a protocol features

Prepared statement môže byť:

- client-side emulation;
- unnamed protocol statement;
- named server-side statement via session;
- pooler-managed mapping.

V transaction pooling mode named statements potrebujú explicitnú pooler/client compatibility. Rovnaký statement name na inom server connection nemusí existovať alebo môže mapovať na inú schema/search path generation.

Validation musí používať exact:

- driver version;
- pooler version/config;
- protocol mode;
- statement naming/cache behavior;
- schema rollout state;
- failover behavior.

## 11. Failover a reconnect storm

Failover mení endpoint, backend identity, open transactions a prepared/session state.

```text
primary failure
→ existing sockets break alebo half-open
→ clients detect failure v rôznych časoch
→ pools invalidate connections
→ reconnect attempts
→ DNS/proxy/pool convergence
→ authentication/TLS/setup load
→ new primary capacity
→ transaction retry/reconciliation
```

Bez jitter, exponential backoff, retry budget a admission control môžu tisíce clients súčasne zaútočiť na nový primary. Healthcheck/reconnect loops môžu spotrebovať reserved capacity skôr než business traffic.

Pool musí odlíšiť:

- safe pre-execution connection failure;
- transaction aborted;
- unknown commit outcome;
- stale read endpoint;
- old writer endpoint;
- authentication/configuration failure.

Unknown commit sa nesmie automaticky retryovať ako nový business operation bez idempotency/reconciliation.

## 12. Reserved a administrative access

Database potrebuje emergency envelope pre:

- incident inspection;
- terminating root blockers;
- fencing;
- backup/recovery;
- schema correction;
- observability/control plane.

PostgreSQL poskytuje reserved/superuser connection slots. MySQL povoľuje extra administrative connection pre privileged account a môže používať dedicated administrative interface. Tieto mechanizmy nepomôžu, ak credentials, route alebo runbook nie sú testované.

Application role nesmie spotrebovať recovery reserve.

## 13. Connected incident `DB-PAY-57`

Pred incidentom:

```text
settlement-api replicas: 96
Hikari maxPoolSize: 40
Hikari minimumIdle: 20
possible application connections: 3 840
PostgreSQL max_connections: 600
reserved + superuser reserve: 15
measured safe app envelope: 540
```

Scale-out vytvoril už len cez `minimumIdle` až `1 920` connection attempts. PostgreSQL prijal časť sessions, zvyšok čakal alebo zlyhal. O `11:38 UTC` network flap spustil synchronized reconnect storm.

Observed state:

```text
server connections: 587
active queries: 164
idle connections: 271
idle in transaction: 83
pool wait p99: 8.7 s
request deadline: 10 s
connect attempts: 12 400/min
```

Emergency change zaviedla PgBouncer transaction pooling:

```text
max_client_conn: 5 000
default_pool_size: 120
pool_mode: transaction
```

Application compatibility nebola overená. Settlement flow používal:

```text
on physical connection initialization:
  SET app.tenant_id = '<merchant tenant>'
  CREATE TEMP TABLE pending_settlement_batch (...)

later business transaction:
  read tenant context
  join temp batch
  insert settlement/outbox
```

Pri transaction pooling-e ďalšia transaction nemusela dostať rovnaký server connection. Výsledkom boli:

- missing temporary table errors;
- absent alebo stale tenant context;
- retries s novým connection/session state-om;
- `214` operations vyžadujúcich tenant-policy verification;
- `31` provider attempts použitých s nesprávnou routing-policy generation;
- `19` operations v `sent-unknown` stave po network timeout-e;
- ďalšia retry a pool pressure amplification.

### Causal boundaries

- **Trigger:** network flap počas scale-out-u.
- **Connection-capacity root cause:** per-Pod pool konfigurácia nebola odvodená z fleet-wide database envelope-u.
- **Pooling-compatibility root cause:** transaction pooling bolo aktivované pre session-stateful application contract.
- **Amplifiers:** vysoké `minimumIdle`, synchronized reconnect, 10-sekundové request deadline, retries bez shared budgetu a idle-in-transaction sessions.
- **Recovery delay:** exhausted application capacity sťažila incident queries a fencing.

## 14. Evidence-preserving containment

```text
freeze autoscaling a pool config changes
→ preserve pooler stats, DB sessions/waits a app thread dumps
→ reserve incident/admin path
→ stop retries a new batch submissions
→ lower readiness/reconnect amplification
→ classify open/unknown transactions
→ identify session-state-dependent queries
→ fence affected tenant-policy cohort
```

Nie je bezpečné iba zvýšiť `max_connections`. To môže zvýšiť memory, context switching a database contention bez zvýšenia useful throughputu.

## 15. Authoritative redesign

Nový contract:

```text
PostgreSQL safe app server connections: 360 normal + 120 controlled burst
PgBouncer transaction pools: workload-class specific
app max pool: 6 per Pod
app min idle: 0–1 s jittered warmupom
checkout timeout: 250 ms
transaction timeout: 2 s pre online settlement path
idle-in-transaction: forbidden/terminated
reconnect: exponential backoff + jitter + fleet token budget
```

Application zmeny:

- tenant identity je explicitný parameter a transaction-local `SET LOCAL` defense-in-depth;
- temporary-table batch workflow bol nahradený durable batch manifestom;
- session advisory locks boli nahradené invariantom/fencing tokenom;
- pooler mode a driver prepared-statement behavior majú compatibility tests;
- failed/unknown connections sa discardujú;
- idempotency a provider reconciliation riešia unknown outcomes;
- rollout používa bounded cohort a database-capacity gate.

## 16. Pooling acceptance verdict

Connection pooling je prijatý, keď:

- exact fleet/pool/database subject je explicitný;
- total theoretical aj effective connection demand je zmeraný;
- database safe execution a connection envelope sú experimentálne overené;
- session/transaction/statement mode zodpovedá application semantics;
- session-state features sú zakázané alebo správne scoped/resetované;
- queue, checkout a request deadlines sú kompatibilné;
- pool saturation load-sheduje skôr než zničí database;
- admin/recovery reserve je dostupný a testovaný;
- transaction cleanup a broken-connection discard fungujú;
- prepared statements, temp objects a identity context majú compatibility evidence;
- failover používa jittered reconnect, retry budget a endpoint/writer validation;
- unknown outcomes sa reconciliujú;
- second-client, second-burst, failover a pooler-restart tests prejdú;
- forbidden state leakage a unlimited connection multiplication sú odmietnuté.

## 17. Troubleshooting pooling incidentu

```text
latency alebo connection failures
→ exact app/pooler/DB generation
→ request rate a fleet replica count
→ configured/effective min/max pools
→ pool queues a checkout waits
→ server connections a active execution
→ idle-in-transaction/locks/waits
→ session-state a transaction compatibility
→ timeouts/cancellation/retry path
→ failover/DNS/reconnect state
→ admin reserve
→ user/business outcome
→ bounded configuration alebo code remediation
```

## 18. Anti-patterny

### Pool max podľa thread countu

Ignoruje fleet multiplication a database capacity.

### Zvýš `max_connections`

Môže iba presunúť bottleneck do memory, CPU, locks alebo storage.

### Pooler je transparentný proxy

Pooling mode môže meniť session a transaction semantics.

### Vysoký `minimumIdle` znižuje latency

Pri scale-out-e a failover-e môže vytvoriť storm.

### Query je 30 ms, databáza je rýchla

Request mohol čakať sekundy v pool queue.

### Timeout a retry

Bez admission a shared retry budgetu zvyšuje overload.

### Connection sa vždy vráti do poolu

Broken alebo unknown protocol/transaction state sa má discardnúť.

### Readiness otvorí celý pool

Incident dependent readiness môže vytvoriť restart loop.

## 19. Kontrolné otázky

1. Čo tvorí exact connection-pooling subject?
2. Aké resources spotrebúva database connection?
3. Ako sa application pool, pooler a server thread pool líšia?
4. Ako session, transaction a statement pooling menia semantics?
5. Prečo session tenant context nefungoval v `DB-PAY-57`?
6. Ako odvodiť fleet-wide connection envelope?
7. Čo odhalí checkout-wait metric?
8. Prečo vysoký `minimumIdle` vytvára storm?
9. Ako sa prepared statements správajú cez transaction pooler?
10. Čo má connection pool urobiť po unknown commit outcome-e?
11. Ako chrániť administrative recovery access?
12. Čo musí overiť pooling acceptance verdict?

## Glossary impact

Relevantné pojmy: connection-pooling subject, application connection pool, server connection envelope, session pooling, transaction pooling, statement pooling, pool queue, checkout wait, pool multiplication, minimum-idle storm, session-state compatibility, connection reset contract, broken-connection discard, administrative connection reserve, reconnect storm, pooler generation a pooling acceptance verdict.

## Primárne zdroje

- [PostgreSQL Documentation — Connections and Authentication](https://www.postgresql.org/docs/current/runtime-config-connection.html)
- [PgBouncer Configuration — Pool modes and limits](https://www.pgbouncer.org/config)
- [MySQL 8.4 Reference Manual — Connection Management](https://dev.mysql.com/doc/refman/8.4/en/connection-management.html)
- [MySQL 8.4 FAQ — Thread Pool vs. client-side connection pool](https://dev.mysql.com/doc/refman/8.4/en/faqs-thread-pool.html)
- [Redis Documentation — Client handling](https://redis.io/docs/latest/develop/reference/clients/)
