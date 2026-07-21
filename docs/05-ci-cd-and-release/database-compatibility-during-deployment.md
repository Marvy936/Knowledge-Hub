# Databázová kompatibilita počas deploymentu

Databázová zmena musí umožniť bezpečnú koexistenciu starej a novej application verzie počas rolling, canary, ring, blue-green aj rollback scenárov. Cieľom nie je iba úspešne vykonať migration, ale zachovať čitateľnosť, zapisovateľnosť a význam dát počas celého release lifecycle.

## 1. Prečo je problém zložitejší než migration script

Počas deploymentu môžu súčasne existovať:

- staré application instances,
- nové application instances,
- background workers,
- scheduled jobs,
- starí a noví clients,
- CDC consumers,
- reporting jobs,
- ďalšie services nad rovnakou schema.

Jednorazová schema zmena môže každú z týchto vrstiev ovplyvniť inak.

## 2. Compatibility dimensions

Rozlišuj:

### Schema compatibility

Existujú tables, columns, indexes, constraints a types, ktoré komponent očakáva?

### Read compatibility

Dokáže stará aj nová verzia interpretovať aktuálne dáta?

### Write compatibility

Vytvára každá verzia dáta, ktoré druhá verzia bezpečne prečíta?

### Semantic compatibility

Majú rovnaké hodnoty rovnaký business význam?

### Operational compatibility

Nevytvorí migration neprijateľné locky, replication lag, I/O alebo storage pressure?

## 3. Expand-contract pattern

Bezpečný model:

```text
1. expand schema
2. deploy compatible writers/readers
3. migrate/backfill data
4. switch reads/writes
5. observe and validate
6. contract obsolete schema
```

Destruktívny contract krok sa vykoná až po skončení rollback window a po potvrdení, že žiadny aktívny consumer starý tvar nepotrebuje.

## 4. Expand fáza

Typické bezpečnejšie operácie:

- pridať nullable column,
- pridať table,
- pridať index online/concurrently,
- pridať nový enum model bez okamžitého použitia starými readers,
- zaviesť compatibility view,
- pridať nový event/schema version,
- pripraviť dual-write destination.

Aj aditívna zmena môže byť prevádzkovo drahá. Vždy over engine-specific behavior.

## 5. Contract fáza

Destruktívne operácie:

- drop column/table,
- rename bez compatibility bridge,
- zúženie type alebo length,
- pridanie `NOT NULL` bez pripravených dát,
- odstránenie enum hodnoty,
- zmena semantics existujúceho poľa,
- odstránenie indexu používaného starou verziou.

Contract musí mať vlastný release, evidence a recovery plán.

## 6. Rename bez big-bang zmeny

Namiesto priameho rename:

```text
add new_column
→ write old + new
→ backfill new_column
→ read new with fallback old
→ stop old writes
→ validate
→ remove old_column later
```

Alternatívou môže byť compatibility view, trigger alebo application adapter, ale každý pridáva vlastné riziká.

## 7. Dual write

Dual write pomáha prechodu medzi schema alebo stores, ale prináša:

- partial failure,
- ordering rozdiely,
- duplicate writes,
- retry ambiguity,
- transaction boundary problémy,
- drift medzi reprezentáciami.

Potrebné sú:

- idempotency,
- explicitný authoritative source,
- reconciliation,
- metrics rozdielov,
- failure queue alebo repair workflow,
- plán ukončenia dual write.

Dual write bez reconciliation iba skrýva nekonzistenciu.

## 8. Read switching

Možnosti:

- read-old,
- read-new with fallback,
- shadow read a diff,
- percentage read rollout,
- tenant/ring-based read switch,
- read-new only.

Shadow read môže porovnávať výsledky bez user-facing zmeny, ale musí kontrolovať extra load a privacy.

## 9. Backfill

Backfill je data migration cez existujúce rows alebo events. Navrhni:

- bounded batches,
- checkpointing,
- idempotentný restart,
- rate limiting,
- pause/resume,
- progress metrics,
- retry a poison-record handling,
- replication-lag guardrail,
- validation queries,
- cleanup.

Jedna obrovská transakcia zvyšuje lock, WAL/binlog, rollback a outage riziko.

## 10. Online schema changes

Engine môže podporovať:

- concurrent index creation,
- online DDL,
- in-place alter,
- copy-based migration,
- shadow table + trigger replication,
- metadata-only change.

Názov operácie nepostačuje. Over konkrétnu verziu databázy, table size, lock level, replication a failure behavior.

## 11. Locky a blocking

Pred migration over:

- required lock mode,
- lock acquisition timeout,
- statement timeout,
- long-running transactions,
- metadata locks,
- replication effect,
- connection pool behavior,
- retry storm po blokovaní.

Rýchla DDL operácia môže dlho čakať na lock a následne zablokovať kritický traffic.

## 12. Constraints

Bezpečný postup pre nový constraint môže byť:

```text
add nullable/unenforced condition
→ backfill and repair
→ validate existing data
→ enable enforcement for new writes
→ enforce globally
```

Konkrétna syntax závisí od engine. Základný princíp je oddeliť opravu dát od okamžitého blocking validation.

## 13. Default values

Pridanie column s defaultom môže byť:

- metadata-only,
- okamžitý table rewrite,
- lazy materialization,
- behavior závislý od engine/version.

Application default a database default musia mať konzistentný význam. Staré writers nemusia nové pole posielať.

## 14. Nullability

Prechod na `NOT NULL`:

1. application začne zapisovať hodnotu,
2. backfill existujúce rows,
3. monitoring potvrdí nulový počet chýbajúcich hodnôt,
4. constraint sa validuje/enforcuje,
5. starý fallback sa odstráni.

Opačné poradie môže rozbiť staré instances počas rollout-u.

## 15. Enum a stavové hodnoty

Nová application verzia môže zapísať hodnotu, ktorú stará verzia nepozná.

Ochrany:

- tolerant reader s `unknown` handlingom,
- oddelenie deploymentu readera pred writerom,
- capability negotiation,
- feature flag pre nové writes,
- versioned event/schema,
- rollback window bez nových hodnôt.

Ignorovanie unknown value môže byť rovnako nebezpečné ako crash.

## 16. Index lifecycle

Nový query path potrebuje index pripravený pred aktiváciou trafficu. Odstránenie starého indexu až po potvrdení, že:

- staré versions nie sú aktívne,
- rollback ho nepotrebuje,
- reporting/maintenance queries ho nepoužívajú,
- query plans sú stabilné.

Index build môže spotrebovať CPU, I/O, storage a replication bandwidth.

## 17. Data type changes

Pri type change preferuj nový column alebo representation:

```text
old_type column
+ new_type column
→ dual write/backfill
→ validate conversion
→ switch readers
→ remove old later
```

In-place conversion môže byť nevratná, blokujúca alebo lossy.

## 18. Multi-service ownership

Shared database zvyšuje coupling. Potrebné sú:

- schema owner,
- consumer inventory,
- compatibility contract,
- migration review,
- usage telemetry,
- deprecation window,
- zákaz nezdokumentovaných direct queries.

Bez znalosti consumers nemožno bezpečne vykonať contract fázu.

## 19. CDC, analytics a replicas

Schema changes môžu ovplyvniť:

- change-data-capture connector,
- replica lag,
- ETL jobs,
- data warehouse schemas,
- materialized views,
- backup/restore tooling,
- audit exports.

Production application health nie je jediná validačná hranica.

## 20. Migration identity a ordering

Každá migration potrebuje:

- unique ID,
- deterministic ordering,
- checksum alebo immutable content,
- applied-state table,
- environment evidence,
- idempotentný alebo explicitne non-repeatable model,
- concurrency protection.

Dve pipeline nesmú súčasne aplikovať konfliktujúce migrations bez coordination locku.

## 21. Forward-only vs. reversible migrations

### Reversible migration

Má definovaný down path, ale jeho existencia nedokazuje bezpečnosť ani zachovanie dát.

### Forward-only migration

Počíta s opravnou migration alebo restore namiesto automatického down.

Voľba závisí od engine, data-loss rizika a operational modelu. „Down“ skript, ktorý dropne novú column s dátami, nie je bezpečný rollback.

## 22. Migration a application ordering

Príklad expand-contract releaseov:

```text
Release A: add schema, old behavior remains
Release B: deploy compatible code, start dual write
Release C: backfill and validate
Release D: switch reads, stop old writes
Release E: remove compatibility path
Release F: contract old schema
```

Jedna aplikácia môže zvládnuť viac krokov, ale logical phases musia zostať pozorovateľné a reverzibilné podľa plánu.

## 23. Feature flags

Flags môžu riadiť:

- nové writes,
- read source,
- dual write,
- backfill activation,
- shadow comparison,
- cleanup.

Flag state musí byť koordinovaný s migration state. Zapnutie flagu pred schema readiness spôsobí incident.

## 24. Rollback compatibility

Pred rolloutom definuj compatibility matrix:

| Application | Schema old | Schema expanded | Schema contracted |
|---|---:|---:|---:|
| Old version | áno | áno | nie |
| New version | podľa návrhu | áno | áno |

Artifact rollback je povolený iba do schema state, ktorému stará verzia rozumie.

## 25. Validation

Použi viac vrstiev:

- migration syntax/test database,
- schema diff,
- lock a duration rehearsal,
- representative data volume,
- constraint validation,
- row counts a checksums,
- shadow reads,
- business invariants,
- replication/CDC health,
- application metrics.

Rovnaký row count neznamená zachovanie business semantics.

## 26. Observability

Sleduj:

- migration phase a version,
- rows processed/remain,
- batch duration,
- error/retry rate,
- lock waits,
- query latency,
- replication lag,
- database CPU/I/O/storage,
- dual-write mismatch,
- fallback-read rate,
- unknown enum/value count.

Každý rollout marker má byť korelovateľný s application version.

## 27. Backup a restore

Pred rizikovou zmenou over:

- posledný úspešný backup,
- restore test,
- point-in-time recovery window,
- expected RPO/RTO,
- encryption keys,
- storage capacity,
- restore target a cutover postup.

Existencia backupu bez overeného restore nie je recovery capability.

## 28. Troubleshooting

### Migration čaká na lock

Identifikuj blocking transaction, nastav timeout, migration bezpečne zruš a preplánuj. Nezabíjaj transakcie bez znalosti business dopadu.

### Po rollout-e rastú chyby starých instances

Noví writers zapísali nekompatibilné hodnoty alebo schema bola contracted príliš skoro. Zastav nové writes a aktivuj compatibility/repair plan.

### Backfill zvyšuje replication lag

Zníž batch/rate, pause, rozlož workload a sleduj replica recovery. Promotion zastav.

### Dual-write dáta sa rozchádzajú

Urči authoritative source, zastav switch reads, spusti reconciliation a oprav retry/transaction model.

### Rollback artifactu zlyhal

Schema alebo data semantics už nie sú kompatibilné. Použi roll-forward, compatibility adapter alebo restore.

## 29. Anti-patterny

### Rename/drop v rovnakom release ako nový kód

Neexistuje bezpečná mixed-version fáza.

### Migration beží pri startup-e každej instance

Vznikajú race conditions, nejasný ownership a nekontrolovaný blast radius.

### `down` script = garantovaný rollback

Môže stratiť dáta alebo byť nekompatibilný s aktuálnymi writes.

### Dual write bez reconciliation

Silent drift zostáva neodhalený.

### Backfill bez rate limitu

Môže spôsobiť produkčný database incident.

### Contract podľa dátumu, nie podľa evidence

Kalendár nepotvrdzuje, že starí consumers zmizli.

## 30. Rozhodovací rámec

1. Ktoré versions a consumers budú súčasne aktívne?
2. Akú schema/read/write/semantic compatibility potrebujú?
3. Aká je expand fáza a čo je destructive contract?
4. Ako sa riadia dual writes, reads a reconciliation?
5. Ako prebehne backfill a jeho pause/resume?
6. Aké locky a resource náklady migration vytvorí?
7. Aká je compatibility matrix pre rollback?
8. Kedy presne končí rollback window?
9. Aké evidence povoľujú contract fázu?
10. Aký restore alebo roll-forward plán existuje?

## 31. Kontrolné otázky

1. Čo je expand-contract pattern?
2. Aký je rozdiel medzi schema a semantic compatibility?
3. Prečo je direct rename rizikový pri rolling update?
4. Aké riziká prináša dual write?
5. Ako navrhnúť bezpečný backfill?
6. Prečo aditívna DDL nemusí byť prevádzkovo lacná?
7. Ako nové enum hodnoty komplikujú rollback?
8. Čo má obsahovať application-schema compatibility matrix?
9. Prečo reversible migration nemusí byť bezpečná?
10. Aké evidence povoľujú odstránenie starej schema?

## Glossary impact

Relevantné pojmy: expand-contract, schema compatibility, read compatibility, write compatibility, semantic compatibility, dual write, reconciliation, shadow read, backfill, online schema change, contract phase, compatibility matrix, forward-only migration, migration lock a fallback read.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Rollback a roll-forward](rollback-and-roll-forward.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
