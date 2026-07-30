# Connection pooling

Connection pool nie je iba performance cache pre TCP spojenia. Je to concurrency, admission a session-state contract medzi application demand-om a databázovou execution capacity. Pool rozhoduje, koľko requests môže čakať, koľko transactions môže súčasne vstúpiť do databázy, aký server-session state sa smie zachovať, čo sa stane pri failover-e a či overload zostane bounded alebo sa premení na connection a retry storm.

```text
business request demand
→ exact fleet/pool/database subject
→ safe database execution envelope
→ application a shared pool topology
→ session/transaction/statement compatibility
→ bounded admission, queue a deadlines
→ checkout, transaction, reset a release
→ failover, invalidation a reconnect control
→ business latency a correctness evidence
→ second-client, burst a failover validation
```

`Pool max = 40` bez počtu replicas, server budgetu a pooling mode-u nie je konfigurácia s vysvetlenou semantics. Je to iba lokálne číslo, ktoré sa vo fleet-e môže násobiť stovkami.

## 1. Pooling subject a fleet-wide budget

Exact pooling subject musí pomenovať service a release, počet Podov alebo processes, client library a pool generation, database endpoint a workload class, per-instance min/max, teoretický a efektívny fleet total, všetky ďalšie pooler/proxy vrstvy, pooling mode, session-state požiadavky, database `max_connections`, reserved envelope, safe execution concurrency, checkout/connect/statement/transaction deadlines, queue discipline a failover behavior.

Atlas Payments pred incidentom používal:

```text
settlement-api replicas: 96
Hikari maxPoolSize: 40
Hikari minimumIdle: 20
possible application connections: 3 840
PostgreSQL max_connections: 600
reserved/admin envelope: 15
measured safe application envelope: 540
```

Configured maximum nie je rovnaký ako simultaneously active demand, ale musí vstúpiť do worst-case modelu. Rovnako `max_connections = 600` neznamená, že databáza bezpečne vykoná 585 drahých queries naraz. Open connection, active execution, idle transaction, lock holder a queued borrower sú odlišné states.

Fleet-wide budget sa začína database bottleneckom a požadovaným headroomom, nie počtom application threads. Littleov zákon poskytuje sanity check `concurrency ≈ throughput × service time`, ale tail latency, locks, bursts, multi-query transactions a failure capacity musia byť zmerané experimentom.

## 2. Čo pool chráni a čo môže poškodiť

Database connection nesie TCP/TLS a authentication cost, backend process alebo thread, per-session memory, parameters, prepared statements, temporary objects, snapshots, locks, buffers a cleanup state. PostgreSQL vytvára backend pre každú direct client connection; MySQL má vlastný connection/thread model; Redis síce spracúva client traffic odlišne, ale stále má file descriptors, buffers a per-client limits.

Pool má znovupoužiť drahé spojenie a obmedziť admission. Ak je príliš veľký, overload presunie do databázy, kde sa prejaví ako memory pressure, context switching, I/O, cache churn, lock waits alebo rollback cost. Ak je príliš malý bez bounded queue, overload sa presunie do application threads a request deadlines. Shared pooler pridáva multiplexing, ale aj ďalšiu queue a ďalší failure/control plane.

Typická cesta requestu je:

```text
request admission
→ application worker
→ application-pool queue
→ shared-pooler queue
→ server connection
→ transaction/query waits
→ commit alebo rollback
→ connection reset/release
→ response
```

Query môže trvať 30 ms a user request 8 sekúnd, pretože väčšinu času čakal pred checkoutom. Observability musí oddeliť queue wait, connect time, transaction time, server wait events a response serialization.

## 3. Session, transaction a statement pooling

Pooling mode je compatibility decision, nie transparentný tuning switch.

Pri **session pooling-u** patrí server connection client session-u až do disconnectu. Temporary tables, session variables, advisory locks, named prepared statements a `LISTEN/NOTIFY` assumptions môžu fungovať prirodzenejšie. Cena je slabšie multiplexing a veľké množstvo idle server connections.

Pri **transaction pooling-u** dostane client server connection iba na dobu jednej transaction. Ďalšia transaction môže bežať na inom backende:

```text
client A transaction 1 → server X
client B transaction 1 → server X
client A transaction 2 → server Y
```

Application sa nesmie spoliehať na session state medzi transactions. Tenant identity, role, search path alebo timezone musia byť explicitné a transaction-local. Temporary table, session advisory lock, cursor a connection-local state presahujúci transaction sú incompatible, pokiaľ ich pooler a driver výslovne nepodporujú iným mechanizmom.

```sql
BEGIN;
SET LOCAL app.tenant_id = 'merchant-42';
-- všetky queries tej istej business transaction
COMMIT;
```

Aj tento pattern funguje iba vtedy, keď framework skutočne drží všetky relevantné statements v jednej transaction. **Statement pooling** uvoľňuje server connection po každom statemente a nepodporuje bežné multi-statement transactions; je vhodný len pre úzko stateless workloady.

## 4. Admission, queue a deadline contract

Pool maximum je admission boundary. Checkout timeout má byť kratší než upstream deadline a musí ponechať čas na controlled error alebo fallback. Request, ktorý už minul väčšinu deadline-u v queue, nemá po checkout-e spustiť drahú transaction a následne vyvolať timeout retry.

Mechanizmus musí definovať:

```text
request deadline
→ bounded pool wait
→ minimum remaining execution budget
→ transaction timeout
→ cancellation/rollback
→ response alebo explicit overload
```

Queue potrebuje capacity, fairness a overload semantics. Interactive settlement traffic, recovery jobs a batch workloady nemajú súťažiť v jednej neobmedzenej FIFO queue. Saturácia má load-shedovať skôr, než vyčerpá database, thread pool a memory. Retry po pool timeout-e bez shared retry budgetu zvyšuje presne ten demand, ktorý pool odmietol.

Minimum idle je tiež fleet decision. `96 × minimumIdle 20` môže po rollout-e alebo failover-e vytvoriť `1 920` connection attempts aj bez business trafficu. Warmup preto potrebuje rate limit, jitter, rollout cohort a dependency-capacity gate. Readiness nesmie otvárať celý pool naraz ani restartovať Pod pri každom prechodnom database probléme.

## 5. Transaction outcome a state hygiene

Connection sa smie vrátiť do poolu až po jednoznačnom stave: transaction commitla, rollbackla alebo sa connection discarduje ako broken/unknown. Exception, cancellation či network reset môžu nechať backend v open alebo failed transaction state. Ďalší borrower potom zdedí locks, snapshot, role alebo `transaction aborted` state.

Session hygiene musí pokryť role a search path, tenant variables, timezone, prepared statements, temp objects, advisory locks, `LISTEN`, application/tracing metadata a open transactions. Reset command nie je náhradou za správny stateless contract. Pri transaction pooling-u server session prirodzene strieda clients, preto je zakázané ukladať authorization alebo tenant authority iba do initialization hooku.

Forbidden outcome je jednoduchý:

```text
client A nastaví privileged alebo tenant state
→ connection sa vráti do poolu
→ client B zdedí effective state
```

Positive test jedného clienta preto nestačí. Potrebný je second-client negative test s iným tenantom a inou privilege úrovňou. Prepared statements sa musia overiť s exact driver a pooler version, schema generation a protocol mode-om; rovnaký statement name na inom server connection nemusí mať rovnaký state.

## 6. Failover, reconnect a administrative reserve

Failover preruší sockets, transactions a session state. Clients zistia failure v rôznych časoch, invalidujú connections a pokúsia sa pripojiť k novému endpointu. Bez jitteru, exponential backoffu, fleet token budgetu a admission controlu môže nový primary dostať tisíce TLS/authentication attempts skôr než užitočný traffic.

```text
old primary failure
→ socket/transaction ambiguity
→ connection invalidation
→ endpoint/writer-generation validation
→ jittered reconnect budget
→ bounded pool warmup
→ transaction retry alebo reconciliation
→ business recovery
```

Pool musí odlíšiť pre-execution connect failure, definitely aborted transaction, unknown commit outcome, stale read endpoint, old writer endpoint a authentication/configuration failure. Unknown commit sa nesmie retryovať ako nová business operation bez stable idempotency identity a database/provider read-backu.

Database potrebuje reserved administrative envelope pre incident inspection, fencing, blocker termination, backup/restore a schema correction. Application role nesmie túto rezervu spotrebovať. Reserve je reálna iba vtedy, keď fungujú credentials, network route a runbook počas saturation scenára.

## 7. Connected incident `DB-PAY-57`

Scale-out Atlas Payments vytvoril cez `minimumIdle` až `1 920` connection attempts. O `11:38 UTC` network flap spustil synchronized reconnect. Observed state bol:

```text
server connections: 587
active queries: 164
idle connections: 271
idle in transaction: 83
pool wait p99: 8.7 s
request deadline: 10 s
connect attempts: 12 400/min
```

Emergency change zapla PgBouncer `transaction` mode s `max_client_conn 5 000` a `default_pool_size 120`. Application compatibility nebola overená. Settlement flow nastavoval `app.tenant_id` pri physical connection initialization a vytváral temporary table, ktorú používal neskorší business transaction. Po multiplexing-u ďalšia transaction často dostala iný server backend.

Výsledkom boli missing temp-table errors, absent alebo stale tenant context a retries s novým session state-om. `214` operations potrebovalo tenant-policy verification, `31` provider attempts použilo nesprávnu routing-policy generation a `19` operations zostalo `sent-unknown` po timeout-e.

Trigger bol network flap počas scale-out-u. Connection-capacity root cause bol per-Pod tuning bez fleet-wide budgetu. Pooling-compatibility root cause bolo zapnutie transaction pooling-u pre session-stateful application contract. Vysoké minimum, synchronized reconnect, takmer vyčerpaný request deadline, retries a idle transactions incident zosilnili a zároveň skomplikovali administratívny recovery access.

## 8. Redesign a acceptance paths

Redesign znížil application max pool na `6` per Pod, minimum na `0–1` s jittered warmupom a oddelil workload-class pools. Normal envelope používa `360` server connections a controlled burst `120`; checkout timeout je `250 ms`, online settlement transaction timeout `2 s` a idle-in-transaction state je zakázaný. Reconnect používa exponential backoff, jitter a fleet token budget.

Tenant identity je explicitný parameter a `SET LOCAL` je defense-in-depth v každej transaction. Temporary batch table bola nahradená durable batch manifestom, session advisory locks fencing tokenom a broken/unknown connections sa discardujú. Rollout pooler alebo driver zmeny používa bounded cohort a compatibility tests.

**Positive path** preukáže, že request dostane správny tenant a role state, transakcia prebehne v deadline-e a connection sa bezpečne použije ďalším clientom bez leakage.

**Recovery path** simuluje pool saturation, pooler restart a database failover. Admission bounded odmieta časť trafficu, admin reserve zostane použiteľná, reconnect demand neprekročí budget a unknown operations sa reconciliujú.

**Failure path** pri prekročení queue, checkout alebo transaction threshold-u skončí explicitným overloadom a rollbackom, nie neobmedzeným waitom alebo retry stormom.

**Forbidden path** odmietne session-state leakage, temporary-table dependency v transaction mode-e, application multiplication nad database envelope, reuse broken connection, blind unknown-commit retry a readiness, ktorá otvorí celý pool naraz.

Acceptance vyžaduje second-client, second-burst, failover a pooler-restart test. Samotný pokles server connection countu nie je úspech, ak user latency alebo tenant correctness zlyháva.

## 9. Troubleshooting a anti-patterny

Diagnostika ide od exact app/pooler/database generation cez replica count, configured/effective min/max, pool queues, checkout waits, server active/idle states, transaction age, locks, session compatibility, timeouts, retries, failover endpoint a admin reserve až po user outcome. `Database CPU je nízke` nevylučuje pool starvation; `query p95 je 30 ms` nevylučuje osemsekundový queue wait.

Najčastejšie anti-patterny sú pool max odvodený z thread countu, slepé zvýšenie `max_connections`, pooler považovaný za transparentný proxy, vysoké `minimumIdle` na každom Pode, timeout nasledovaný automatickým retryom, reuse každej connection bez outcome classification a readiness závislá od plného pool warmup-u.

## 10. Kontrolné otázky

1. Čo tvorí exact fleet/pool/database subject?
2. Prečo server connection count nie je rovnaký ako safe execution concurrency?
3. Ako sa session, transaction a statement pooling líšia?
4. Prečo session tenant context zlyhal pri transaction pooling-u?
5. Ako pool queue a request deadline vytvárajú jeden contract?
6. Prečo vysoký `minimumIdle` vytvára scale-out alebo failover storm?
7. Kedy sa connection môže vrátiť do poolu a kedy sa musí discardnúť?
8. Ako second-client test odhalí state leakage?
9. Ako jittered reconnect a reserved envelope chránia recovery?
10. Ktoré positive, recovery, failure a forbidden paths musia prejsť?

## Glossary impact

Relevantné pojmy: connection-pooling subject, application connection pool, server connection envelope, session pooling, transaction pooling, statement pooling, pool queue, checkout wait, pool multiplication, minimum-idle storm, session-state compatibility, connection reset contract, broken-connection discard, administrative connection reserve, reconnect storm, pooler generation a pooling acceptance verdict.

## Primárne zdroje

- [PostgreSQL 18 Documentation — Connections and Authentication](https://www.postgresql.org/docs/current/runtime-config-connection.html)
- [PgBouncer Configuration — Pool modes and limits](https://www.pgbouncer.org/config)
- [MySQL 8.4 Reference Manual — Connection Management](https://dev.mysql.com/doc/refman/8.4/en/connection-management.html)
- [Redis Documentation — Client handling](https://redis.io/docs/latest/develop/reference/clients/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Backups a point-in-time recovery](backups-and-point-in-time-recovery.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: PostgreSQL, MySQL a Redis →](postgresql-mysql-and-redis.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
