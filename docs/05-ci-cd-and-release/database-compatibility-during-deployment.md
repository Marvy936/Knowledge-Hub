# Databázová kompatibilita počas deploymentu

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Databázová kompatibilita počas deploymentu je schopnosť viacerých aplikačných, workerových, analytických a integračných verzií bezpečne čítať a zapisovať shared database state počas celého release a recovery lifecycle.

Cieľom nie je iba úspešne spustiť migration script. Cieľom je zachovať:

- dostupnosť,
- read a write correctness,
- business semantics,
- operational limity,
- rollback alebo roll-forward možnosti,
- data integrity pre všetkých consumers.

## 2. Mental model: databázová zmena je distribuovaný protocol

Počas rollout-u môžu súčasne existovať:

- old a new application instances,
- workers a schedulers,
- old/new clients,
- reporting a ETL,
- CDC connectors,
- ďalšie services s direct query,
- replicas, backups a restore tooling.

Schema a data change preto nie je lokálna DDL operácia. Je to protocol medzi readers, writers, migration workerom a contract-removal rozhodnutím.

## 3. Compatibility dimensions

### Structural/schema compatibility

Existujú očakávané tables, columns, indexes, constraints a types?

### Read compatibility

Dokážu všetky aktívne verzie interpretovať aktuálny state vrátane nových hodnôt?

### Write compatibility

Vytvára každý writer state, ktorý ostatní readers bezpečne spracujú?

### Semantic compatibility

Má rovnaká hodnota alebo column rovnaký business význam?

### Operational compatibility

Nevytvára zmena neprijateľný lock, lag, I/O, storage alebo connection pressure?

### Recovery compatibility

Môže sa current state bezpečne používať po artifact/config rollbacku?

## 4. Consumer inventory a ownership

Pred návrhom zmeny identifikuj:

- ORM/application access,
- workers a cron,
- direct SQL consumers,
- BI/reporting,
- CDC/ETL,
- data exports,
- backup/restore,
- replicas a downstream warehouses,
- ad hoc operational tooling.

Každá schema boundary potrebuje ownera. Contract krok bez consumer inventory je neauditovaný breaking change.

## 5. Migration identity a immutable history

Každá migration má:

- unique monotonic alebo otherwise ordered ID,
- immutable content/checksum,
- ownera a purpose,
- compatibility phase,
- engine/version assumptions,
- expected lock/runtime/resource profile,
- retry/recovery semantics,
- applied-state record.

Publikovanú a aplikovanú migration neupravuj spätne. Vytvor novú corrective migration.

## 6. Expand-migrate-contract lifecycle

```text
expand
→ deploy tolerant readers/writers
→ migrate/backfill
→ switch behavior
→ validate
→ end rollback window
→ contract
```

Jednotlivé fázy môžu byť samostatné releases. Contract sa neriadi dátumom, ale evidence, že starý contract už nikto nepotrebuje.

## 7. Expand fáza

Typické additive operácie:

- nová nullable column,
- nová table,
- nový index,
- compatibility view,
- nový event/schema representation,
- nový read/write target,
- unenforced alebo not-yet-validated constraint.

Aditívna zmena môže byť stále prevádzkovo drahá. Engine môže rewrite-nuť table, držať metadata lock alebo zvýšiť replica lag.

## 8. Tolerant application release

Pred aktiváciou nového state nasadzuj code, ktorý:

- toleruje neprítomnosť alebo prítomnosť nového tvaru podľa phase,
- pozná unknown values,
- dokáže fallback read,
- používa idempotentné writes,
- publikuje phase telemetry,
- zachováva old contract pre aktívne consumers.

Reader capability má často predchádzať writer activation.

## 9. Contract fáza

Destruktívne zmeny:

- drop table/column,
- rename bez bridge,
- type narrowing,
- `NOT NULL` enforcement,
- odstránenie enum/state hodnoty,
- semantic repurpose,
- drop indexu potrebného old consumerom.

Contract má vlastný release record, prechecks, recovery plan a evidence o nulovom použití starého contractu.

## 10. Rename bez big bang

```text
add new_column
→ deploy dual-compatible code
→ dual write alebo database-derived sync
→ backfill
→ read new with fallback old
→ validate equivalence
→ stop old writes
→ read new only
→ wait rollback/deprecation window
→ remove old_column
```

Compatibility view alebo trigger môže pomôcť, ale pridáva ordering, performance a cleanup riziko.

## 11. Dual write

Dual write má tri kľúčové otázky:

- ktorý store/field je authoritative,
- čo sa stane pri partial failure,
- ako sa drift deteguje a opraví.

Potrebuje:

- idempotency,
- explicitnú transaction boundary alebo outbox,
- retry model,
- reconciliation,
- mismatch metrics,
- repair queue,
- ukončenie dual-write fázy.

„Zapíšeme na dve miesta“ bez reconciliation nie je migration strategy.

## 12. Alternatives k application dual write

Podľa systému:

- database trigger,
- CDC replication,
- transactional outbox,
- migration worker odvodený zo source of truth,
- event replay,
- materialized view.

Každá možnosť má rozdielnu consistency, latency, ownership a failure semantics.

## 13. Read switching

Fázy:

- read old,
- shadow read new a compare,
- read new with fallback old,
- percentage/ring read new,
- read new only,
- remove fallback.

Zaznamenávaj fallback rate a mismatch kategórie. Ak fallback zostane aktívny trvalo, migration sa nedokončila.

## 14. Shadow reads

Shadow read spustí nový query path, ale používateľovi vráti old result. Kontroluj:

- extra database load,
- privacy v diff logs,
- nondeterminism a timing,
- snapshot consistency,
- normalization,
- sampling.

Rozdiel môže vzniknúť tým, že old a new query čítali state v inom okamihu.

## 15. Backfill contract

Backfill potrebuje:

- bounded batch size,
- deterministic key ordering,
- checkpointing,
- idempotent restart,
- rate limits,
- pause/resume,
- poison-record handling,
- progress a remaining estimate,
- replication-lag a load guardrails,
- verification queries,
- ownera a cleanup.

Jedna veľká transakcia zvyšuje lock, WAL/binlog, storage a rollback riziko.

## 16. Backfill concurrency s live writes

Definuj, ako sa rieši race:

```text
backfill reads old row
→ live writer updates row
→ backfill writes stale derived value
```

Možnosti:

- compare-and-swap/version column,
- backfill iba null/unmigrated rows,
- live dual write s monotonic version,
- repeat reconciliation pass,
- database-side atomic expression.

## 17. Backfill completion

`100 % rows processed` nemusí znamenať correctness. Over:

- expected population,
- null/missing counts,
- checksums alebo aggregates,
- business invariants,
- mismatch samples,
- late writes,
- reconciliation after completion,
- replicas a CDC.

## 18. Online schema change

Engine môže používať:

- metadata-only alteration,
- in-place operation,
- table copy,
- concurrent index build,
- shadow table a triggers,
- partition exchange.

Vždy over konkrétny engine/version, table size, lock mode, cancellation, replication behavior, disk peak a cleanup po failure.

Marketingový názov `online` neznamená nulový lock alebo nulový dopad.

## 19. Locks a transactions

Pred migration skontroluj:

- required lock mode,
- lock acquisition timeout,
- statement timeout,
- long transactions,
- metadata locks,
- connection pool behavior,
- deadlock/retry,
- replica apply.

Krátka DDL môže hodiny čakať na lock a po získaní zablokovať traffic.

## 20. Resource budget

Stanov guardrails pre:

- database CPU,
- I/O a storage throughput,
- WAL/binlog growth,
- replication lag,
- disk free space,
- buffer/cache pressure,
- connection usage,
- query latency,
- backup interference.

Migration job musí vedieť throttle alebo pause.

## 21. Constraints lifecycle

Bezpečný model:

```text
application začne produkovať compliant data
→ repair/backfill existing data
→ add constraint in non-blocking/not-valid mode, ak engine umožňuje
→ validate existing rows
→ enforce
→ remove application fallback
```

Okamžitý blocking validation môže spôsobiť outage.

## 22. NOT NULL

1. readers tolerujú null aj value,
2. writers vždy zapisujú value,
3. backfill existing nulls,
4. monitor null count,
5. validate/enforce constraint,
6. odstráň fallback.

Enforcement pred writer rolloutom rozbije old instances.

## 23. Defaults

Rozlišuj:

- application default,
- database default,
- materialized existing-row value,
- semantic default.

Engine môže default aplikovať metadata-only alebo table rewrite spôsobom. Old writers nemusia nové pole posielať, preto DB a application default musia byť kompatibilné.

## 24. Enum a stavové hodnoty

Nový writer môže zapísať value, ktorú old reader nepozná. Použi:

- tolerant unknown handling,
- reader-first rollout,
- feature flag na nové writes,
- versioned event/schema,
- compatibility adapter,
- rollback window pred aktiváciou values.

Silent mapovanie unknown na nesprávny default môže byť horšie než explicitný failure.

## 25. Data type change

Preferuj parallel representation:

```text
old column + new column
→ validated conversion
→ dual write/backfill
→ switch readers
→ stop old writers
→ contract old representation
```

In-place type conversion môže byť lossy, blocking alebo nevratná.

## 26. Index lifecycle

- vytvor index pred aktiváciou nového query pathu,
- build monitoruj pre I/O, storage a lag,
- over query plans,
- zachovaj old index pre rollback/old versions,
- odstráň až po usage evidence.

Index usage môžu mať aj reporting alebo maintenance consumers.

## 27. Partitioning a large-table changes

Pri veľkých tables rieš:

- partition key compatibility,
- online repartitioning,
- hot partitions,
- foreign keys,
- archive/retention jobs,
- replica and backup behavior,
- cutover consistency.

Takáto zmena často potrebuje samostatný program, nie jeden application release.

## 28. Multi-service database ownership

Shared database zvyšuje coupling. Zaveď:

- schema/table ownera,
- explicitné APIs alebo views,
- consumer registry,
- query telemetry,
- migration review,
- deprecation notices,
- contract tests podľa možnosti,
- zákaz neznámych direct queries.

Bez ownershipu sa contract fáza nedá bezpečne dokázať.

## 29. CDC, replicas a analytics

Over dopad na:

- CDC schema registry/connectors,
- replica apply a lag,
- ETL a warehouse,
- materialized views,
- audit exports,
- backups a restores,
- search indexes,
- downstream data contracts.

Zelený application smoke nepokrýva celý data ecosystem.

## 30. Migration orchestration

Migration nemá bežať nekontrolovane pri startup-e každej instance. Preferuj jednoznačného ownera/job s:

- distributed lock,
- migration ordering,
- permissions,
- timeout,
- evidence,
- resume/recovery behavior.

Application startup môže overiť compatible schema range, nie pretekať o DDL ownership.

## 31. Compatibility matrix

Príklad:

| Application | Old schema | Expanded schema | Contracted schema |
|---|---:|---:|---:|
| Old version | áno | áno | nie |
| Transition version | áno | áno | podľa návrhu |
| New version | podľa návrhu | áno | áno |

Doplň readers, writers, workers a clients. Matrix je vstup pre rollout aj rollback eligibility.

## 32. Feature flags a migration phase

Flags môžu riadiť:

- new writes,
- read source,
- shadow read,
- dual write,
- backfill,
- fallback,
- cleanup.

Flag state musí mať prerequisites na schema/migration phase. Zapnutie new writes pred expand readiness je control-plane incident.

## 33. Rollback window

Počas window zachovaj:

- expanded schema,
- old read/write compatibility,
- old artifacts,
- event/cache compatibility,
- migration repair path.

Contract krok explicitne ukončuje niektoré rollback možnosti a musí to zaznamenať release record.

## 34. Forward-only verzus reversible

- **Reversible syntax —** existuje down operácia.
- **Semantically reversible —** neboli stratené dáta ani význam.
- **Operationally reversible —** operácia sa dá vykonať v RTO bez neprijateľného locku.

Down script, ktorý dropne novú column, môže byť syntakticky validný a recovery-nebezpečný.

## 35. Backup, restore a PITR

Pred rizikovou zmenou over:

- backup integrity,
- restore test,
- point-in-time window,
- encryption keys,
- RPO/RTO,
- storage/capacity,
- restore target,
- routing cutover,
- reconciliation s external systems.

Restore celej databázy môže stratiť legitímne writes po recovery point-e; nie je to bezplatné undo.

## 36. Validation layers

- migration unit/integration test,
- schema diff,
- compatibility matrix test,
- lock/runtime rehearsal,
- representative volume,
- backfill invariants,
- shadow reads,
- dual-write reconciliation,
- application synthetics,
- CDC/replica health,
- business/data invariants,
- restore drill.

## 37. Contract evidence

Pred odstránením starého contractu vyžaduj:

- zero old application/worker versions,
- zero old write/read telemetry,
- completed backfill a reconciliation,
- fallback usage nulové alebo vysvetlené,
- consumers/dependencies migrated,
- rollback window formálne ukončené,
- restore/roll-forward plan,
- approval ownera schema.

## 38. Observability

Sleduj:

- migration ID/phase,
- rows processed/remaining,
- batch latency a error,
- lock waits,
- query latency,
- DB CPU/I/O/storage,
- WAL/binlog a replication lag,
- fallback read rate,
- dual-write mismatch,
- unknown values,
- CDC/ETL failures,
- application version correlation.

## 39. Failure taxonomy

- lock acquisition/blocking failure,
- partial migration,
- resource saturation,
- backfill stale overwrite,
- dual-write divergence,
- read mismatch,
- old consumer incompatibility,
- CDC/replica failure,
- premature contract,
- rollback-ineligible state,
- restore/reconciliation failure.

## 40. Diagnostický postup

1. Urči migration ID, phase a applied state.
2. Zisti aktívne application/worker/consumer versions.
3. Over locks, transactions a resource pressure.
4. Pri backfill-e skontroluj checkpoint, rate a live-write race.
5. Pri errors old version hľadaj nové values alebo premature contract.
6. Pri dual-write drift urči authoritative source a zastav read switch.
7. Skontroluj replicas, CDC a analytics.
8. Posúď artifact rollback podľa compatibility matrix.
9. Pri data incident-e zvoľ forward repair, compensation alebo restore.
10. Contract nepovoľ, kým evidence nie je úplná.

## 41. Metriky capability

- migration success/failure rate,
- lock wait a blocking incidents,
- backfill duration a throttle time,
- replication-lag guardrail activations,
- dual-write mismatch rate,
- fallback-read age,
- contract lead time,
- rollback-ineligible migrations,
- unknown consumer discoveries,
- restore test freshness,
- data-integrity incidents.

## 42. Typické anti-patterny

### Rename/drop v jednom release

Chýba mixed-version bridge.

### Migration pri startup-e každej instance

Vzniká race a nejasné ownership.

### Dual write bez reconciliation

Silent drift zostáva.

### Backfill bez rate limitu a checkpointu

Môže vytvoriť database incident a nemá bezpečný resume.

### `Down` script = garantovaný rollback

Môže stratiť data alebo prekročiť RTO.

### Contract podľa dátumu

Kalendár nedokazuje, že consumers zmizli.

### Application health = data ecosystem health

CDC, replicas a analytics môžu byť zlomené.

### Additive DDL sa považuje za lacnú

Engine môže rewrite-nuť alebo locknúť veľkú table.

## 43. Rozhodovací rámec

1. Ktoré readers/writers/consumers budú súčasne aktívne?
2. Aké structural, read, write, semantic a operational contracts potrebujú?
3. Aká je expand a contract boundary?
4. Kto je authoritative source počas dual write?
5. Ako sa riešia partial failures a reconciliation?
6. Ako backfill koexistuje s live writes?
7. Aké lock/resource limity má DDL?
8. Aká compatibility matrix povoľuje rollback?
9. Aké evidence ukončujú fallback a rollback window?
10. Ako sú zahrnuté CDC, replicas a analytics?
11. Aký forward-repair/restore plán existuje?
12. Kto schváli contract fázu?

## 44. Kontrolný checklist

- consumer inventory a owner sú známe,
- migration content je immutable,
- phases sú explicitné a pozorovateľné,
- tolerant readers predchádzajú new writers,
- dual write má source of truth a reconciliation,
- backfill je bounded, resumable a race-safe,
- engine-specific DDL behavior bol testovaný,
- locks/resource guardrails existujú,
- compatibility matrix zahŕňa rollback,
- flags majú schema prerequisites,
- CDC/replica/analytics validation je zahrnutá,
- backup restore je overený,
- contract evidence je úplná,
- cleanup odstráni fallback a migration debt.

## 45. Kontrolné otázky

1. Prečo je databázová zmena distribuovaný protocol?
2. Aké compatibility dimensions treba odlišovať?
3. Ako funguje expand-migrate-contract lifecycle?
4. Prečo reader rollout často predchádza writer rollout?
5. Aké failure modes má dual write?
6. Ako backfill bezpečne koexistuje s live writes?
7. Prečo `online DDL` nemusí znamenať nulový dopad?
8. Ako nové enum values rušia rollback eligibility?
9. Čo musí obsahovať compatibility matrix?
10. Aké evidence povoľujú contract fázu?
11. Prečo down migration nemusí byť semantically ani operationally reversible?
12. Ako sa validuje celý data ecosystem, nie iba aplikácia?

## Summary

Databázová kompatibilita počas deploymentu je viac-release protocol medzi readers, writers, migration workers a všetkými downstream consumers. Bezpečný model používa expand-migrate-contract, tolerant readers pred novými writers, bounded a resumable backfill, reconciliation, engine-specific lock/resource testy a explicitnú compatibility matrix. Rollback window existuje iba dovtedy, kým old versions rozumejú aktuálnemu state. Contract fázu povoľuje evidence o nulovom použití starého contractu, dokončenej migrácii a pripravenom forward-repair alebo restore pláne.

## Glossary impact

Relevantné pojmy: database deployment compatibility, expand-migrate-contract, structural compatibility, read compatibility, write compatibility, semantic compatibility, recovery compatibility, consumer inventory, dual write, reconciliation, shadow read, bounded backfill, compatibility matrix, contract evidence, forward-only migration a rollback window.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Rollback a roll-forward](rollback-and-roll-forward.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Projects, groups a permissions →](../06-gitlab/projects-groups-permissions.md)
<!-- KNOWLEDGE-NAVIGATION:END -->