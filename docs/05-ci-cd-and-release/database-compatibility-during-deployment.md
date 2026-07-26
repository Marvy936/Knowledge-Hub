# Databázová kompatibilita počas deploymentu

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Databázová zmena počas deploymentu je distribuovaný protocol medzi všetkými readers, writers, migration workers a downstream consumers. Úspešné vykonanie DDL alebo backfill jobu nie je cieľom samo osebe. Cieľom je zachovať read/write correctness, business semantics, prevádzkové limity a recovery compatibility počas celého obdobia, keď starý a nový contract koexistujú.

```text
consumer inventory a compatibility contract
→ expand schema
→ deploy tolerant readers
→ activate compatible writers
→ bounded migration/backfill
→ shadow a reconciled reads
→ controlled read switch
→ stop old writes
→ prove old contract unused
→ close rollback window
→ contract old representation
```

Contract krok nie je cleanup podľa kalendára. Je to nevratnejší transition povolený konkrétnou evidence.

## 1. Nosný model: schema evolution ako viac-release protocol

Počas rollout-u môžu súčasne existovať:

```text
old a new API instances
old a new workers
mobile alebo partner clients
BI a direct SQL reports
CDC a ETL connectors
replicas a search indexes
backup a restore tooling
migration/backfill worker
```

Každý participant má read a write očakávania. Databáza je shared communication medium.

Preto treba oddeliť compatibility dimensions:

- **Structural:** existujú tables, columns, types, indexes a constraints, ktoré consumer očakáva?
- **Read:** dokáže consumer interpretovať všetky aktuálne hodnoty a representations?
- **Write:** vytvára writer state čitateľný ostatnými aktívnymi versions?
- **Semantic:** znamená hodnota pre všetkých rovnaký business stav?
- **Operational:** nevytvára migration neakceptovateľné locks, lag, I/O alebo storage pressure?
- **Recovery:** môže previous artifact alebo consumer pracovať s current state-om?

Additive schema môže byť structural-compatible a zároveň operational-nebezpečná. Rovnaký typ stĺpca môže byť structural-compatible, ale semantic-breaking.

## 2. Nosný scenár: Atlas Orders risk-decision migration

Atlas presúva risk state z legacy columns:

```text
orders.risk_status
orders.risk_reason
```

do normalizovaného modelu:

```text
risk_decisions(
  order_id,
  decision,
  reason_code,
  source_version,
  decision_version,
  updated_at
)
```

Aktívni consumers:

```text
Orders API v2 a v3
Risk workers v2 a v3
settlement scheduler
support dashboard
fraud BI report
audit export
CDC connector do warehouse
partner reconciliation job
```

Cieľový lifecycle:

```text
S0 old columns authoritative
→ S1 new table expanded, old readers/writers unchanged
→ S2 tolerant readers deployed
→ S3 dual-write, old read authoritative
→ S4 bounded backfill + reconciliation
→ S5 shadow-read new
→ S6 read-new with fallback-old
→ S7 read-new only, old writes stopped
→ S8 rollback window closed
→ S9 old columns contracted
```

Každá fáza má explicitnú migration identity, allowed application versions a recovery path.

## 3. Consumer inventory definuje contract boundary

Pred návrhom Atlas priradí každému consumerovi:

```text
owner
read fields a semantics
write capability
runtime/version inventory
release cadence
telemetry alebo query fingerprint
migration deadline
recovery dependency
```

Application repository nie je úplný consumer inventory. Fraud BI môže čítať column priamo. CDC connector môže exportovať schema. Support script môže byť spúšťaný iba počas incidentu a preto sa neobjaví v bežnej telemetry.

Unknown consumer je explicitný risk, nie dôkaz jeho neexistencie. Contract approval potrebuje kombináciu registry, query telemetry, repository search, owner acknowledgement a deprecation windowu.

## 4. Migration identity a phase sú immutable evidence

Každá migration má:

```text
migration ID a checksum
engine/version assumptions
from/to phase
owner a release relation
expected lock/runtime/resource profile
idempotency a retry semantics
checkpoint format
preconditions a postconditions
recovery/repair path
```

Aplikovanú migration neupravuj spätne. Corrective change dostane nový ID a vlastný state transition.

Atlas applications pri startup-e nevykonávajú DDL race. Overujú, či current schema phase patrí do podporovaného compatibility range-u. Jeden fenced migration job vlastní transition medzi phases.

## 5. Expand vytvára priestor pre koexistenciu

V `S1` Atlas vytvorí `risk_decisions` table bez zmeny authoritative read/write behavioru.

Pred apply overí:

- konkrétny PostgreSQL engine a version;
- lock mode a acquisition timeout;
- long-running transactions;
- disk, WAL a replica-lag budget;
- cancellation a partial-outcome semantics;
- backup/restore readiness.

Additive DDL nie je automaticky lacná. Index build alebo default môže rewrite-nuť veľkú table alebo čakať na metadata lock. Migration sa spustí s bounded timeoutom a guardrails, nie neobmedzene v deployment windowe.

## 6. Tolerant readers musia predchádzať novým values a writers

V `S2` sa deployne transition code, ktorý:

```text
číta old representation
+ rozumie prítomnosti new table
+ toleruje unknown decision values
+ publikuje migration-phase telemetry
+ vie fallbacknúť bez zmeny business významu
```

Reader-first poradie chráni mixed-version obdobie. Ak new writer zapíše `PENDING_REVIEW_V2` skôr, než old consumer pozná unknown handling, old worker alebo report môže zlyhať.

Tolerancia neznamená silent mapovanie neznámej hodnoty na `APPROVED`. Bezpečný reader môže explicitne odmietnuť mutation, zachovať raw value alebo route-nuť order do manual review.

## 7. Dual write potrebuje source of truth a failure semantics

V `S3` new workers zapisujú old columns aj new table. Contract definuje:

```text
authoritative source = old columns
transaction boundary = jeden DB transaction
idempotency key = order_id + decision_version
partial failure = transaction rollback
mismatch detection = reconciliation query
repair owner = migration worker
```

Ak stores alebo systems nemožno zahrnúť do jednej transaction boundary, treba outbox, retry a explicitné partial-state reconciliation.

„Zapíšeme na dve miesta“ bez authoritative source a drift repair nie je migration strategy. Je to mechanizmus na tiché vytváranie divergence.

## 8. Bounded backfill musí koexistovať s live writes

V `S4` backfill dopĺňa historical decisions.

```text
select next key range
→ read authoritative old state + row version
→ derive new representation
→ conditional insert/update
→ commit bounded batch
→ checkpoint last key
→ verify batch invariant
→ observe DB/replica budgets
→ continue alebo pause
```

Backfill má:

- deterministic key ordering;
- bounded batch size;
- durable checkpoint;
- idempotent restart;
- poison-record quarantine;
- DB CPU, I/O, WAL, lag a latency guardrails;
- rate limit a pause/resume;
- progress aj remaining population estimate;
- final reconciliation pass.

`100 % processed` znamená, že job navštívil keys. Neznamená, že výsledok zostal correct po concurrent live writes.

## 9. Live-write race musí mať explicitnú ochranu

Rizikový interleaving:

```text
backfill načíta old risk_status = PENDING, version 7
→ live worker zapíše APPROVED, version 8 a dual-write new row
→ backfill zapíše stale PENDING do new row
```

Atlas používa conditional write:

```text
update new representation
only if source decision_version <= observed version 7
```

Prípadne backfill vypĺňa iba missing rows a nikdy neprepíše novší live-write version. Reconciliation potom porovnáva business value aj monotonic version.

Bez CAS/version contractu môže backfill po celý čas vyzerať úspešne a napriek tomu poškodzovať najaktívnejšie rows.

## 10. Shadow read oddeľuje nový query path od authoritative response

V `S5` API stále vracia old result, ale vykoná new read a vytvorí paired comparison:

```text
same order ID
old read snapshot
new read snapshot
normalization revision
value diff category
fallback reason
application + migration phase
```

Comparison musí odlíšiť:

- skutočný migration mismatch;
- rozdielny snapshot alebo timing;
- expected semantic transform;
- missing backfill;
- stale replica;
- normalization bug;
- comparison-query failure.

Shadow read pridáva load a môže meniť cache/buffer behavior. Používa sampling a resource budget rovnako ako shadow deployment.

## 11. Read switch je samostatný progressive transition

Atlas neprepne všetkých naraz:

```text
internal tenants read-new
→ ring 1 read-new with fallback-old
→ observe mismatch a fallback rate
→ ring 2
→ read-new only pre všetkých
```

`read-new with fallback-old` je dočasná recovery pomôcka. Ak fallback rate zostane nenulová bez expiry, migration je neuzavretá a incidenty sa maskujú.

Promotion vyžaduje:

```text
backfill population complete
+ dual-write mismatch pod hard limitom
+ fallback dôvody klasifikované
+ old/new business invariants equivalent
+ replicas/CDC/analytics healthy
+ current application versions compatible
```

## 12. Compatibility matrix riadi rollout aj recovery

Atlas používa matrix:

```text
                    S0 old   S1–S6 expanded   S9 contracted
API v2 read/write      áno         áno              nie
API v3 transition      áno         áno          podľa build-u
Worker v2              áno         áno              nie
Worker v3              nie/bridge  áno              áno
BI legacy report       áno         áno              nie
CDC v2 schema          áno         áno              nie
```

Matrix nie je statická dokumentácia. Actual version inventory sa pri každom transitione porovná s allowed combinations.

Artifact rollback je eligible iba ak target row matrix zostáva compatible s current schema, values a events. Contract `S9` vedome odstraňuje niektoré rollback targets.

## 13. Contract proof je dôkaz zániku old dependency

Pred `S9` Atlas vyžaduje:

```text
zero old API/worker versions
zero legacy query fingerprints počas defined windowu
BI, CDC, audit a partner owners migrated
old write rate = 0
old read/fallback rate = 0 alebo approved exception
backfill + reconciliation complete
new representation business invariants healthy
rollback window formálne ukončené
forward-repair a restore path pripravené
```

Kalendárny dátum alebo „už to beží mesiac“ nedokazuje, že old contract nikto nepoužíva.

Contract transition má vlastný release record, approval a observation. Drop column je production change, nie housekeeping.

## 14. Worked failure: backfill prepísal novší live state

Pôvodný Atlas backfill nepoužíval source version.

```text
backfill prečíta PENDING
→ live worker rozhodne APPROVED a zapíše obe representations
→ backfill neskôr upsertne PENDING do new table
→ old authoritative path zostáva APPROVED
→ shadow mismatch rastie iba pri aktívnych orders
```

### Príčina

Job bol idempotentný voči opakovaniu rovnakého batchu, ale nebol concurrency-safe. „Last writer wins“ dovolil historical migration jobu poraziť novší business write.

### Dôsledok

Read switch by zmenil business outcome pre časť orders. Re-run backfillu bez opravy by race zopakoval.

### Recovery

Atlas pause-nul backfill aj read promotion, ponechal old source authoritative, pridal monotonic `decision_version` guard a spustil reconciliation/repair iba pre mismatched rows.

### Trvalá náprava

```text
source-version capture
→ conditional write
→ live-write-wins invariant
→ concurrent-write fixture
→ mismatch metric podľa source/new version
→ final reconciliation po backfill completion
```

## 15. Worked failure: contract odstránil column používanú skrytým reportom

Application telemetry ukazovala nulové old reads. Tím preto dropol `orders.risk_reason`.

```text
API a workers healthy
→ nightly fraud BI report spustí direct SQL
→ query zlyhá na missing column
→ compliance export sa nevytvorí
→ incident sa objaví až nasledujúce ráno
```

### Príčina

Consumer inventory bol odvodený iba z application code a krátkeho query windowu. Nightly report nemal owner acknowledgement ani deprecation check.

### Dôsledok

Application rollback column neobnovil. Atlas musel roll-forwardnúť compatibility view/column, opraviť export a znovu spustiť reporting pipeline.

### Trvalá náprava

- query telemetry window pokrývajúce celý business cycle;
- registry direct SQL consumers;
- owner acknowledgements;
- compatibility view pred dropom;
- delayed contract validation pre BI, CDC a audit ecosystem;
- contract proof ako strojovo kontrolovaný manifest.

## 16. Worked failure: additive index build poškodil primary traffic

Nový query path potreboval index. Tím považoval `CREATE INDEX CONCURRENTLY` za bezvýpadkový.

```text
index build začne na veľkej table
→ I/O a WAL rastú
→ replica lag prekročí read-routing threshold
→ reads sa presunú na primary
→ primary CPU a query latency rastú
→ client retries zvýšia load
```

DDL nevytvorila dlhý blocking lock, ale operational compatibility zlyhala cez resource coupling.

Recovery bola pause/cancel index buildu podľa engine-safe postupu, stabilizácia replicas a nový rate/resource window. Trvalý control meria disk peak, WAL, replica lag a primary latency počas rehearsal-u na reprezentatívnom objeme.

## 17. Kauzálny diagnostický walkthrough

Symptom: pri 40 % backfill completion rastie old/new mismatch pre aktívne orders, zatiaľ čo historical rows sú correct.

### Krok 1 — stabilizuj migration subject a phase

```text
migration MR17 checksum X17
phase S4 dual-write + backfill
old columns authoritative
backfill checkpoint order_id 48M
API/worker inventory v2 + v3
read switch ešte nezačal
```

### Krok 2 — formuluj konkurenčné hypotézy

```text
H1: backfill derivation logic je všeobecne nesprávna
H2: live-write race prepisuje new row stale hodnotou
H3: dual-write partial failures vytvárajú missing new rows
H4: shadow comparison číta old/new z rozdielnych snapshots
H5: CDC alebo replica lag skresľuje iba pozorovanie
```

### Krok 3 — vyber observation points

- mismatch podľa row activity a update timestamps rozlišuje H1 od H2;
- transaction/outbox audit a missing-row count testujú H3;
- primary snapshot comparison testuje H4/H5;
- source a new `decision_version` poradie testuje H2;
- deterministic re-derivation na immutable sample testuje H1.

Atlas zistí:

```text
historical immutable rows sú equivalent
mismatches majú new updated_at po live write, ale stale source version
missing-row rate je nízka a nekoreluje
primary-snapshot comparison mismatch zachováva
replica lag nie je príčinou
```

H2 je potvrdená.

### Krok 4 — contain-ni správnu fázu

Atlas pause-ne backfill a blokuje read promotion. Dual-write live path zostáva aktívny, pretože vytvára správny current state. Global application rollback by neodstránil stale rows a zbytočne by zmenil ďalšie vrstvy.

### Krok 5 — oprav mechanizmus

Backfill dostane conditional write podľa `decision_version`; reconciliation identifikuje rows, kde new version zaostáva za authoritative old version, a repair ich v bounded batches opraví.

### Krok 6 — over pôvodný outcome

```text
mismatch rate klesne na definovanú hranicu
žiadny new row nemá staršiu decision_version
active-order concurrent fixture prejde
replica/CDC health ostáva stabilná
business decision aggregates sú equivalent
```

### Krok 7 — vráť learning

Failure sa zmení na concurrency contract v migration template, CAS test, version telemetry a promotion precondition pred každým read switchom.

## 18. Recovery options rešpektujú data semantics

Pri migration failure môže Atlas použiť:

- pause phase a ponechať old source authoritative;
- corrective forward migration;
- selective row repair;
- event replay zo source of truth;
- compatibility view alebo adapter;
- compensation pre external effects;
- restore do nového targetu a selective recovery;
- point-in-time restore iba po RPO/RTO a collateral-write analýze.

`Down` script dokazuje syntaktickú cestu späť, nie semantic alebo operational reversibility. Drop new table môže stratiť legitímne data. Reverse type conversion môže byť lossy. Backward DDL môže prekročiť incident RTO.

## 19. Celý data ecosystem musí byť súčasťou validation

Atlas neuzatvára phase iba podľa application smoke. Overuje:

```text
application synthetics
workers a schedulers
backfill/reconciliation invariants
query plans a latency
locks a resource budgets
replicas a failover readiness
CDC schema a offsets
ETL/warehouse outputs
BI a audit reports
backup/restore drill
partner reconciliation
```

Zelené API môže koexistovať s rozbitým CDC connectorom alebo audit exportom. Data compatibility je širšia než ORM compatibility.

## 20. Diagnostický runbook

1. Urči migration ID, checksum, phase a authoritative representation.
2. Zostav inventory aktívnych readers, writers a downstream consumers.
3. Over locks, transactions, resource pressure, replicas a CDC.
4. Pri backfill-e potvrď checkpoint, batch identity a source-version race protection.
5. Pri dual-write drift-e urč partial failure a source of truth.
6. Pri read mismatch-e odlíš data divergence, snapshot timing, replica lag a comparison bug.
7. Posúď artifact rollback cez actual compatibility matrix.
8. Contain-ni konkrétnu phase; necontractuj ani nepromotionuj pri neúplnej evidence.
9. Vyber forward repair, selective reconciliation, compensation alebo restore podľa semantics.
10. Over application, data, downstream a business outcomes pred ďalším transitionom.

## 21. Referenčné pravidlá

- Databázová zmena je distribuovaný protocol, nie lokálny DDL script.
- Consumer inventory zahŕňa application aj direct SQL, CDC, BI, replicas a restore tooling.
- Expand vytvára compatibility priestor; contract ho odstraňuje.
- Tolerant readers predchádzajú new writers a values.
- Dual write potrebuje authoritative source, idempotency a reconciliation.
- Backfill musí byť bounded, resumable a concurrency-safe.
- Processed row count nie je correctness proof.
- Shadow/read switch potrebuje paired evidence a fallback expiry.
- Compatibility matrix riadi rollout aj rollback eligibility.
- Contract povoľuje evidence o nulovom použití, nie dátum.
- `Down` migration nie je automaticky semantic ani operational rollback.
- Application health nepokrýva celý data ecosystem.

## 22. Časté omyly

### „Additive DDL je vždy bezpečná“

Môže vytvoriť locks, table rewrite, WAL alebo replica-lag incident.

### „Dual write stačí na synchronizáciu“

Bez source of truth a reconciliation vzniká silent drift.

### „Backfill je idempotentný, teda bezpečný“

Môže byť opakovateľný a zároveň prepisovať novšie live writes.

### „100 % processed znamená migration complete“

Treba dokázať expected population, versions, business invariants a downstream state.

### „Nulové application reads povoľujú drop“

Skrytý report, CDC alebo incident script môže stále používať old contract.

### „Rollbackneme databázu down scriptom“

Môže to stratiť data, zablokovať traffic alebo prekročiť RTO.

## 23. Zhrnutie

Atlas database-evolution lifecycle je:

```text
complete consumer inventory
→ immutable migration a compatibility matrix
→ engine-aware expand
→ tolerant readers
→ compatible dual writers
→ version-safe bounded backfill
→ shadow/read evidence
→ progressive read switch
→ stop old writes
→ contract proof a rollback-window closure
→ destructive cleanup
```

Databázová kompatibilita počas deploymentu je schopnosť udržať správny business význam naprieč viacerými versions a phases, nie iba schopnosť spustiť schema. Dôveryhodný protocol robí každý transition pozorovateľný, recoverable a podmienený evidence z celého data ecosystemu.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Rollback a roll-forward](rollback-and-roll-forward.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Projects, groups a permissions →](../06-gitlab/projects-groups-permissions.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
