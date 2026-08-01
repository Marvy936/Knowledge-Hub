# Databázová kompatibilita počas deploymentu

Databázová zmena počas deploymentu je distribuovaný protocol medzi všetkými readers, writers, migration workers, reporting jobs a downstream consumers. Úspešné vykonanie DDL alebo backfill jobu nie je cieľom samo osebe. Cieľom je zachovať read/write correctness, business semantics, operational limits a recovery compatibility počas celého obdobia, keď starý a nový contract koexistujú.

Application rollout a database transition majú rozdielne lifecycles. Pods možno vrátiť za minúty, ale destructive schema change, prepísané rows alebo emitted events môžu byť nevratné. Safe model preto používa expand–migrate–contract, tolerant readers, version-aware writers a explicitný consumer inventory. Contract cleanup prichádza až po dôkaze, že old generation už nič nepoužíva.

## 1. Dominantný compatibility protocol

```text
consumer a query/write-path inventory
→ versionovaný compatibility contract
→ additive expand schema
→ deploy tolerant readers
→ activate compatible/dual writers
→ bounded version-safe backfill
→ shadow/read-path comparison
→ switch authoritative reads/writes
→ prove old consumers and backlog absent
→ contract destructive cleanup
→ recovery and second-operation validation
```

Každý step má rollback boundary. Expand je zvyčajne ľahšie reversible než data rewrite. Contract cleanup môže odstrániť return path pre old binary. Progressive delivery musí poznať current data step, nie iba application release.

## 2. Exact database transition subject

```yaml
databaseTransitionSubject:
  id: DB-PAY-42
  databaseCluster: payments-prod-pg
  databaseGeneration: pg-prod-1844
  schemaBefore: settlement-schema-v41
  schemaExpanded: settlement-schema-v42-expand
  schemaAfter: settlement-schema-v42-contract
  migrationBundleDigest: sha256:mig1000
  applicationContracts:
    oldRelease: payments-9.9.3
    newRelease: payments-10.0.0-rc.4
  consumers:
    - payments-api-9.9
    - payments-api-10.0
    - settlement-worker-9.9
    - settlement-worker-10.0
    - reporting-etl-v18
    - support-console-v6
  backfill:
    generation: backfill-pay-42-7
    keyRange: settlement_id
    batchSize: 500
    maximumRowsPerSecond: 2000
  recoveryReference: db-recovery-pay-42
```

Migration filename ani schema version samostatne nestačia. Subject potrebuje exact database, bundle, old/new applications, all consumers a backfill generation.

## 3. Consumer inventory

Consumers zahŕňajú viac než production services. Ad-hoc reporting, BI, support tools, CDC connectors, backups, data exports a old event replayers môžu používať field alebo index. Search source repositories nestačí; runtime query telemetry, database permissions a ownership catalog dopĺňajú inventory.

```sql
SELECT usename, application_name, queryid, calls,
       LEFT(query, 200) AS sample
FROM pg_stat_statements
WHERE query ILIKE '%legacy_provider_route%'
ORDER BY calls DESC;
```

Query preukazuje statements zachytené extension v retention/current statistics window-e. Nepreukazuje dormant monthly job, prepared statement normalization gaps ani consumer, ktorý sa nepripojil počas window-u. Contract cleanup potrebuje time-based observation a owner attestations.

## 4. Expand schema

Expand pridáva nové structures bez odstránenia old contractu. Príklad:

```sql
ALTER TABLE settlements
  ADD COLUMN provider_route_v2 text;

CREATE INDEX CONCURRENTLY IF NOT EXISTS
  settlements_provider_route_v2_idx
  ON settlements (provider_route_v2)
  WHERE provider_route_v2 IS NOT NULL;
```

`ALTER TABLE ... ADD COLUMN` bez default rewrite je často low-impact, ale exact engine/version a lock semantics sa musia overiť. `CREATE INDEX CONCURRENTLY` znižuje blocking writes v PostgreSQL, no používa viac work, trvá dlhšie a po failure môže zanechať invalid index.

Read-back:

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'settlements'
  AND column_name = 'provider_route_v2';

SELECT indexrelid::regclass AS index_name, indisvalid, indisready
FROM pg_index
WHERE indexrelid = 'settlements_provider_route_v2_idx'::regclass;
```

Output preukazuje catalog state. Nepreukazuje application compatibility, query plan usage ani business values.

## 5. Tolerant readers

New reader má zvládnuť old aj new row state počas migration:

```text
if provider_route_v2 exists
→ use and validate v2
else
→ derive/read legacy field
```

Fallback semantics musia byť explicitné. `COALESCE(new, old)` môže skryť invalid partial value alebo významový rozdiel. Reader telemetry sleduje which path bol použitý a mismatches medzi old/new derivation.

Old reader zostáva functional, kým old column/semantics existujú. New writer nesmie okamžite prestať old field udržiavať, ak old consumers ešte existujú.

## 6. Dual write a atomicity

Ak old a new fields musia zostať synchronized, application write ich aktualizuje v jednej database transaction. Dve samostatné async writes môžu vytvoriť split state.

```sql
BEGIN;
UPDATE settlements
SET provider_route = :legacy_route,
    provider_route_v2 = :route_v2,
    row_generation = row_generation + 1
WHERE settlement_id = :id
  AND row_generation = :expected_generation;
COMMIT;
```

Affected-row count `1` preukazuje optimistic condition success pre local row. Nepreukazuje downstream event publication ani provider effect. Transactional outbox alebo equivalent protocol zachová event relation.

Dual write má reconciliation query a sunset plan. Permanent duplicated fields zvyšujú divergence risk.

## 7. Version-safe backfill

Backfill číta old rows a zapisuje new representation. Medzitým live writer môže row zmeniť. Naivný backfill prepíše novší value stale snapshotom. Safe model používa generation/CAS alebo predicate, ktorý chráni current state.

```sql
UPDATE settlements
SET provider_route_v2 = :derived_route,
    migrated_by = 'backfill-pay-42-7'
WHERE settlement_id = :id
  AND provider_route_v2 IS NULL
  AND row_generation = :observed_generation;
```

Affected rows `0` nie je automaticky failure; môže znamenať live update alebo previous migration. Worker znovu načíta row a klasifikuje outcome.

Backfill checkpoint obsahuje key range, read snapshot semantics, last key, applied/skipped/conflict counts a code/artifact generation. Offset podľa page number je nestabilný pri concurrent inserts/deletes; stable key range je bezpečnejší.

## 8. Operational limits

Backfill môže vyčerpať I/O, WAL, locks, replicas, autovacuum alebo connection pool. Rate limit sa viaže na database saturation, replication lag a foreground SLO.

```sql
SELECT application_name, state, sync_state,
       pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS byte_lag
FROM pg_stat_replication;
```

Query preukazuje observed replication state/lag pre connected replicas. Nepreukazuje query latency, storage queue alebo cloud replica outside view. Backfill controller kombinuje viac signals a pause semantics.

Pause musí byť safe: transaction dokončí/rollbackne, checkpoint sa durable uloží a resume nepoužije stale in-memory batch.

## 9. Shadow comparison a read switch

New read path môže bežať shadow:

```sql
SELECT COUNT(*) AS mismatches
FROM settlements
WHERE provider_route_v2 IS NOT NULL
  AND normalize_legacy_route(provider_route) <> provider_route_v2;
```

Zero mismatches preukazuje equality podľa function a rows v query scope. Nepreukazuje completeness backfillu, correct business semantics alebo hidden consumers. Sampled request-level comparison a business canaries dopĺňajú evidence.

Authoritative read switch je versionovaný feature/config transition. Loaded generation a actual query path sa observe-nú; control-plane flag alone nestačí.

## 10. Contract cleanup eligibility

Destructive cleanup — drop old column, constraint tightening alebo old event removal — je posledný step. Eligibility vyžaduje:

```text
all writers use new contract
+ all readers tolerate/use new contract
+ old application cohorts removed
+ old backlog/replay drained
+ reporting/support consumers migrated
+ backups/restore/recovery plan understood
+ observation window without old usage
+ rollback no longer claims old binary compatibility
```

Drop sa nemá vykonať v rovnakom release, ktorý introduces new field, pokiaľ neexistuje exclusive downtime contract a complete inventory.

## 11. Migration transaction a unknown outcome

DDL semantics sú engine-specific. Niektoré operations sú transactional, iné majú implicit commits alebo external phases. Migration tool success preukazuje journal state podľa toolu, nie business compatibility.

Po timeout-e:

```sql
SELECT version, description, success, installed_on, checksum
FROM schema_history
WHERE version = '42';
```

Journal output sa porovná s actual catalog. Journal row môže existovať pred/po partial operation podľa tool behavior. Blind rerun bez engine-aware read-back môže zlyhať alebo poškodiť state.

## Doplnenie výkladu: expand/contract a mixed-version window

Počas rolling alebo progressive deploymentu stará a nová application version často používajú rovnakú databázu. Schema zmena preto musí byť kompatibilná počas **mixed-version window**.

Expand/contract pattern:

```text
expand:
pridať nový nullable column/table/index bez odstránenia starého contractu

migrate:
nová verzia dual-write/dual-read alebo backfilluje dáta

switch:
consumers prejdú na nový contract po overení completeness

contract:
odstrániť starý column/path až keď ho žiadna supported verzia nepoužíva
```

`ALTER TABLE` success nepreukazuje, že operation bola online alebo že replicas/backfill sú complete. DDL môže držať lock, prepísať table alebo zvýšiť replication lag. Plan zahŕňa engine/version a dataset size.

Backfill je production workload. Potrebuje batches, checkpoint, rate limit, idempotenciu a verification query. Stale backfill nesmie prepísať novší live write; používa conditional update alebo version comparison.

Dual-write môže vytvoriť partial outcome, ak jeden write uspeje a druhý zlyhá. Transaction alebo reconciliation contract musí určiť authority.

Schema version v migration table preukazuje, že migration runner zaznamenal krok. Nepreukazuje data completeness ani to, že všetky processes načítali nový model.

Contract removal je samostatný release po telemetry dôkaze, že starý field/path sa nepoužíva. Rollback eligibility sa posudzuje pred každou fázou.

## 12. Connected incident `REL-PAY-71`

Atlas expandol `provider_route_v2` a spustil backfill. Worker načítal 500-row batch bez row generations. Počas spracovania live new writer aktualizoval 83 rows. Backfill neskôr prepísal `provider_route_v2` hodnotou odvodenou zo stale legacy snapshotu.

Feature flag zapol new read path pre enterprise accounts pred dokončením comparison. Latency alert spustil application rollback, no backfill a flag zostali active. Old application emitovala event v17, new consumer očakával v18 semantics a old consumers nepoznali new enum.

```text
expand
→ unsafe stale backfill
→ early read switch
→ multi-axis rollback iba application
→ data/event contract divergence
```

83 rows malo wrong route; 31 provider operations sa duplikovalo po retries a 119 ostalo unknown.

Root cause bol chýbajúci version-safe data protocol a cleanup/recovery contract.

## 13. Redesign a acceptance verdict

Redesign používa CAS backfill, atomic dual write/outbox, bounded load controller, shadow comparison a explicitné rollout generations. Flag activation čaká na completeness/mismatch gates. Recovery freeze-ne backfill a reconciliuje affected rows/provider effects pred application transition.

Databázová kompatibilita je prijatá iba vtedy, keď:

```text
all consumers and contracts sú inventoried
+ expand je additive a engine-aware
+ old/new readers and writers coexist safely
+ dual write je atomic alebo reconciled
+ backfill je version-safe, bounded and resumable
+ comparison covers completeness and correctness
+ read/write switch loaded state je observed
+ destructive cleanup má no-old-consumer proof
+ rollback claims zodpovedajú current schema/events
+ forbidden stale overwrite a second live-update test prejdú
```

## 14. Troubleshooting flow

```text
database/migration subject
→ consumer inventory
→ catalog/journal state
→ old/new reader/writer versions
→ dual-write divergence
→ backfill checkpoints/conflicts/load
→ read/feature effective generation
→ event/backlog compatibility
→ business rows and external effects
```

Competing hypotheses môžu byť catalog partial state, old consumer, stale backfill, dual-write split, replica lag, wrong flag generation, cleanup too early alebo incompatible rollback. Successful DDL nie je final verdict.

## 15. Anti-patterny

### Add a drop v jednom rolling release

Mixed-version consumers stratia compatibility boundary.

### `COALESCE` ako automaticky správny fallback

Môže skryť invalid partial value alebo semantic mismatch.

### Backfill bez optimistic generation

Stale batch môže prepísať novší live state.

### Zero mismatch ako complete migration proof

Rows bez new value alebo excluded consumers môžu zostať neoverené.

### Application rollback ako database rollback

Schema, rows, events a external effects zostávajú current.

## 16. Kontrolné otázky

1. Prečo databázová zmena je distributed protocol?
2. Čo tvorí exact transition subject?
3. Ako sa inventarizujú hidden consumers?
4. Čo preukazuje catalog read-back?
5. Ako tolerant reader pracuje s partial migration?
6. Prečo dual write má byť atomic?
7. Ako CAS chráni backfill pred stale overwrite?
8. Ktoré operational signals riadia backfill?
9. Čo musí preukázať shadow comparison?
10. Kedy je contract cleanup eligible?
11. Čo sa pokazilo v `REL-PAY-71`?
12. Ako sa testuje second live update počas backfillu?

## Glossary impact

Relevantné pojmy: database compatibility protocol, consumer inventory, expand–migrate–contract, tolerant reader, dual write, row generation, version-safe backfill, backfill checkpoint, foreground workload protection, shadow read comparison, authoritative read switch, contract cleanup eligibility, migration unknown outcome a stale backfill overwrite.

## Primárne zdroje

- [PostgreSQL documentation — ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)
- [PostgreSQL documentation — CREATE INDEX](https://www.postgresql.org/docs/current/sql-createindex.html)
- [PostgreSQL documentation — Monitoring Statistics](https://www.postgresql.org/docs/current/monitoring-stats.html)
- [Martin Fowler — Evolutionary Database Design](https://martinfowler.com/articles/evodb.html)
- [AWS Builders’ Library — Ensuring rollback safety during deployments](https://aws.amazon.com/builders-library/ensuring-rollback-safety-during-deployments/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Rollback a roll-forward](rollback-and-roll-forward.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Praktický CI/CD projekt od source change po overený production release →](ci-cd-practical-walkthrough.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
