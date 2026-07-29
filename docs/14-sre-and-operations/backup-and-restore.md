# Backup a restore

Backup je oddelená, spravovaná a obnoviteľná reprezentácia presne definovaného subjectu. Restore je proces, ktorý z vybraného recovery candidate-u vytvorí použiteľný system/data state. **Existencia backup jobu ani úspešný snapshot nepreukazujú recoverability.**

Recoverability vzniká až vtedy, keď organizácia vie zvoliť správny clean point, získať dáta aj kľúče, obnoviť dependencies, overiť integritu a business semantics a bezpečne vykonať cutover alebo merge.

```text
business recovery objective
→ exact protected subject a consistency group
→ clean-point a acknowledgement semantics
→ effective backup policy a assignment
→ capture a immutable recovery generation
→ isolation, encryption, retention a catalog
→ integrity/readability verification
→ recovery-candidate selection
→ isolated restore a dependency reconstruction
→ technical, data a business validation
→ fencing, merge/replay/cutover a reconciliation
→ second-restore a recurrence closure
```

## 1. Exact protected subject

Tvrdenie `databáza je zálohovaná` je neúplné. Backup subject musí obsahovať:

- business capability;
- exact data stores a datasets;
- schema a application generation;
- account, Region, cluster alebo tenant scope;
- consistency-group members;
- acknowledgement boundary;
- encryption key a identity dependencies;
- retention a legal constraints;
- ownera;
- RPO/RTO objectives;
- recovery consumers.

Príklad:

```text
capability: merchant settlement reconciliation
primary store: PostgreSQL payments-prod-eu
related state: outbox, broker offsets, object evidence, provider references
schema: settlement-ledger v17
application: payments-api 7.25.0
consistency group: CG-PAY-04
ack boundary: committed payment + outbox intent
RPO: 5 min
RTO: 45 min
owner: Payments Resilience
```

Bez consistency groupu môže byť každý component samostatne obnoviteľný, ale ich kombinácia business-neplatná.

## 2. Backup, replication, snapshot, archive a export

### Backup

Recovery-oriented copy s policy, retention, catalogom a restore procesom.

### Replication

Kopíruje state do ďalšieho replica subjectu. Zlepšuje availability, ale často rýchlo replikuje deletion, corruption alebo ransomware.

### Snapshot

Point-in-time representation storage/data state-u. Môže byť crash-consistent, application-consistent alebo iba storage-consistent.

### Archive

Dlhodobé uchovanie historických dát podľa retention a retrieval contractu. Nemusí byť vhodné na rýchly full restore.

### Export

Logical representation, napríklad SQL dump alebo object manifest. Môže byť portable, ale nemusí zachovať všetky engine-specific semantics, permissions, sequence values alebo transaction boundaries.

### Restore

Materializuje recovery candidate do target environmentu.

### Recovery

Obnovuje požadovanú business capability vrátane dependencies, identities, trafficu, reconciliation a user outcome-u.

Tieto pojmy nie sú synonymá.

## 3. Failure model pred backup designom

Backup policy musí vychádzať z failure modes:

- accidental deletion;
- application bug a logical corruption;
- storage/media failure;
- Region alebo datacenter loss;
- ransomware a credential compromise;
- malicious administrator;
- schema migration failure;
- dependency alebo account loss;
- encryption-key loss;
- provider data divergence;
- compliance retention request;
- silent corruption zistená až po dlhšom čase.

Jedna replika v rovnakom trust domain-e nechráni pred compromised administratorom. Krátka retention nechráni pred corruption zistenou po týždni.

## 4. Consistency levels

### Crash-consistent

State zodpovedá náhlemu zastaveniu systému. Engine recovery môže replaynúť logs, ale application-level invariants nemusia byť potvrdené.

### Application-consistent

Aplikácia alebo datastore koordinuje flush/quiesce/checkpoint tak, aby interné invariants boli obnoviteľné.

### Transaction-consistent

Recovery point zachováva committed transaction boundary konkrétneho datastore-u.

### Business-consistent

Súvisiace stores a external effects možno interpretovať ako jeden validný business state.

Pre settlement:

```text
PostgreSQL commit
+ outbox intent
+ broker publication state
+ provider attempt/acknowledgement
+ customer-visible projection
```

Samostatný DB snapshot nemusí povedať, či provider už settlement vykonal.

## 5. Consistency group

Consistency group je versionovaný zoznam subjects, ktoré treba obnoviť alebo reconciliovať spoločne:

```text
CG-PAY-04
├── payments PostgreSQL
├── outbox rows
├── broker topic/offset generation
├── provider idempotency references
├── settlement evidence objects
├── schema/config generation
└── identity/key dependencies
```

Každý member potrebuje:

- authority;
- capture method;
- timestamp/sequence boundary;
- retention;
- restore method;
- reconciliation rule;
- ownera.

External provider ledger nemusí byť backupovateľný organizáciou, ale musí byť súčasťou recovery contractu.

## 6. Clean point

Latest point nie je automaticky správny point. Recovery candidate môže byť:

- pred destructive mutation;
- po validnom schema migration checkpoint-e;
- pred credential compromise;
- posledný malware-free point;
- posledný business-consistent checkpoint;
- point vybraný podľa legal hold alebo audit need.

```text
latest available
≠ latest clean
≠ latest business-consistent
≠ najrýchlejšie obnoviteľný
```

Clean-point selection používa incident timeline, data/audit evidence a compromise interval.

## 7. Backup typy a chain

### Full backup

Samostatná široká copy subjectu. Jednoduchší restore, vyššia capture/storage cena.

### Incremental backup

Obsahuje zmeny od posledného backup pointu. Restore závisí od chainu.

### Differential backup

Obsahuje zmeny od posledného full backupu.

### Transaction/WAL/log backup

Umožňuje jemnejší point-in-time recovery a replay committed changes.

### Continuous data protection

Capture-ne zmeny priebežne, ale stále potrebuje clean-point, isolation a restore validation.

### Synthetic full

Storage systém vytvorí full view kombináciou predchádzajúcich backupov bez full readu source-u.

Dlhý incremental chain môže skrátiť backup window, ale predĺžiť restore a zvýšiť počet dependencies.

## 8. Backup lifecycle a effective assignment

```text
policy intent
→ resource discovery/selection
→ effective assignment
→ scheduled/event capture
→ backup generation
→ encryption a catalog publication
→ copy/replication do recovery domainu
→ retention/immutability
→ verification a expiry
```

Configured policy nie je effective coverage. Over:

- resource bol objavený;
- správny scope/tag selector ho zahrnul;
- job vytvoril expected artifact;
- artifact má správnu generation a timestamp;
- cross-account/cross-Region copy dokončila;
- retention a lock sú effective;
- catalog vie artifact nájsť;
- restore identity ho vie čítať a dešifrovať.

## 9. Isolation a trust boundary

Backup má prežiť compromise production trust domainu. Controls:

- oddelený account alebo administrative domain;
- offline alebo logically isolated copy;
- immutable/WORM retention podľa potreby;
- deletion protection;
- dual control pre destructive actions;
- separate short-lived restore identity;
- independent audit trail;
- network segmentation;
- key separation a protected recovery access;
- recovery environment bez automatic production trust inheritance.

`Immutable` nechráni pred zachytením už corrupted alebo encrypted dát. Je to jeden control, nie celý clean-recovery contract.

## 10. Encryption a key recoverability

Encrypted backup je nepoužiteľný bez:

- existujúceho key materialu;
- current key state-u;
- správnej key policy/grantu;
- restore identity;
- region/account accessibility;
- algorithm/provider compatibility;
- auditovaného break-glass pathu.

Key backup a data backup nesmú vytvoriť jeden ľahko kompromitovateľný trust bundle. Zároveň strata kľúča nesmie nenápadne zmeniť durable backup na unreadable archive.

Testuj decryption cez canary restore, nie iba control-plane popis `encrypted=true`.

## 11. Retention a deletion

Retention design pokrýva:

- krátke operational recovery points;
- dlhšie logical-corruption discovery window;
- compliance/legal retention;
- ransomware dwell time;
- cost a retrieval tier;
- schema/application compatibility;
- secure expiry/deletion;
- litigation hold;
- key lifetime.

Príliš krátka retention môže odstrániť posledný clean point. Príliš dlhá retention zvyšuje cost, privacy exposure a compatibility burden.

## 12. Backup integrity

Backup job `Completed` môže znamenať iba úspešný upload. Potrebné checks:

- expected size/count;
- checksums a object completeness;
- log-chain continuity;
- catalog readability;
- schema/header parse;
- decryption;
- restore mount/open;
- referential/application invariants;
- malware/corruption scan podľa contextu;
- expected consistency-group coverage.

Checksum potvrdí, že bytes sa nezmenili od capture. Nepotvrdí, že capture bol clean alebo business-valid.

## 13. Recovery catalog

Catalog spája:

```text
protected subject
→ backup generations
→ timestamps/sequence numbers
→ clean/unknown/compromised classification
→ location a retention
→ encryption/key dependency
→ restore tooling/version
→ tested status
→ expected restore duration
```

Bez catalogu existujú backups, ale responder počas incidentu nevie, ktorý zvoliť.

Catalog musí byť dostupný aj pri výpadku primary identity, DNS, documentation alebo production accountu.

## 14. Restore target

Pred restore definuj target:

- isolated forensic environment;
- clean recovery environment;
- temporary validation cluster;
- alternate Region/account;
- original production resource;
- side-by-side data extraction target.

Logical corruption sa zvyčajne neobnovuje priamo cez current production. Bezpečnejší flow:

```text
candidate
→ isolated restore
→ validation a affected manifest
→ bounded merge/replay alebo controlled cutover
```

## 15. Restore lifecycle

```text
incident a recovery intent
→ exact target/subject
→ candidate a clean-point selection
→ access, key, network a capacity eligibility
→ restore operation
→ engine recovery a schema compatibility
→ dependency/config/identity reconstruction
→ integrity a application validation
→ business reconciliation
→ fencing a cutover/merge
→ observation a cleanup
```

Každý krok má ownera, timeout, abort criterion a evidence.

## 16. Restore nie je rollback

Rollback aplikačného release-u nemení automaticky data state. Restore historického datastore-u môže odstrániť validné post-point operations.

Možnosti:

### Full rewind

Celý subject sa vráti na starší point. Vyžaduje fencing a spracovanie divergence.

### Side-by-side restore a merge

Z historical pointu sa extrahujú iba affected records a bezpečne sa zlúčia s current state-om.

### Replay

Events/logs sa aplikujú od recovery pointu s idempotency a ordering contractom.

### Compensation

Vytvorí sa nová business operation opravujúca external effect.

### Rebuild from authority

Projection/cache/index sa znovu vytvorí z authoritative source-u.

Výber závisí od data authority a external side effects.

## 17. Fencing

Počas recovery nesmú starý a nový writer nekontrolovane mutovať rovnaký business subject.

Fencing môže používať:

- write freeze;
- generation token alebo epoch;
- lease/fencing token;
- route cutover;
- read-only mode;
- disabled scheduler/consumer;
- database role revocation;
- queue partition ownership;
- provider operation pause.

Bez fencing môže restore vytvoriť druhú divergentnú históriu.

## 18. Validation layers

### Infrastructure

Resource existuje, storage je attached, network a keys fungujú.

### Engine

Datastore sa otvorí, recovery logs sú aplikované, schema je readable.

### Data

Counts, checksums, constraints, relationships a expected records sú validné.

### Application

Supported application generation vie dáta čítať a zapisovať.

### Business

Critical journeys a invariants sú správne, napríklad žiadny lost/duplicate settlement.

### Forbidden outcome

Wrong tenant, stale identity, duplicate replay, corrupted point alebo active old writer sú odmietnuté.

`Database accepting connections` je iba skorá validation vrstva.

## 19. Restore drills

Drill musí testovať celý path:

- responder a access;
- catalog discovery;
- key/decryption;
- candidate selection;
- provisioning capacity;
- restore tooling;
- dependency reconstruction;
- validation queries;
- business canary;
- cutover/fencing;
- elapsed time;
- cleanup;
- second restore.

Varianty:

- scheduled isolated restore;
- unannounced responder exercise;
- alternate-account/Region restore;
- ransomware/credential-loss scenario;
- logical-corruption point selection;
- large-scale full restore;
- partial record recovery;
- new-team-member drill.

Drill, ktorý obnoví jednu malú test table bez dependencies, nepreukazuje production recoverability.

## 20. Worked incident `SRE-PAY-54`

### Backup state

Atlas Payments používal:

```text
PostgreSQL base snapshot: každých 6 h
continuous WAL: enabled
cross-account copy: enabled
retention: 35 dní
object evidence: versioned object storage
provider ledger: external API + 15-min reconciliation export
backup catalog: BKP-PAY generation 22
```

Control plane ukazoval všetky backup jobs ako successful.

### Logical corruption

Compactor o `02:14:07 UTC` broad-archived active rows. Replication a snapshots po tomto čase zachytili validné bytes s invalidnou business semantikou.

Latest snapshot preto nebol clean candidate.

### Candidate selection

WAL a audit určili:

```text
last DB-clean point: 02:13:58 UTC
last coordinated DB/provider checkpoint: 02:03:00 UTC
current corrupted state: preserved pre comparison
```

Full production rewind na `02:03` by zahodil validné neskoršie operations. Tím preto zvolil side-by-side restore PostgreSQL na `02:13:58`, extrakciu affected manifestu a provider-ledger reconciliation.

### Restore failures

1. restore workload identity nemala po account migration current decrypt grant;
2. recovery subnet nemala route k artifact catalogu;
3. restore runbook odkazoval na schema v15, current backup bola v17;
4. provider reconciliation export mal 15-min granularity;
5. estimated restore duration neobsahovala data validation ani merge.

Backup data existovali a boli intact. Recovery path nebola current.

### Authoritative recovery

```text
preserve current corrupted database
→ disable/fence compactor a archive writers
→ restore 02:13:58 do isolated environmentu
→ validate schema v17 a clean invariant
→ derive exact 7 842-row affected manifest
→ classify post-point operations
→ query provider idempotency ledger
→ merge clean correlation metadata
→ replay only never-sent intents
→ reconcile sent-unknown/completed cohorts
→ validate merchant-visible state
→ second restore drill
```

Business recovery skončila o `06:03 UTC`, teda `3 h 49 min` po first bad mutation. Deklarovaný `45 min` RTO bol prekročený.

## 21. Backup/restore acceptance verdict

Recoverability je prijatá, keď:

- exact protected subject a consistency group sú inventoried;
- failure model pokrýva physical, logical, malicious a dependency loss;
- effective backup assignment je potvrdený read-backom;
- expected recovery generations existujú a sú catalogued;
- isolation, immutability, retention a deletion controls sú effective;
- restore identity a decryption path sú testované;
- clean-point selection je reprodukovateľná;
- isolated restore prejde v podporovanej generation;
- infrastructure, engine, data, application a business validation prejdú;
- fencing zabráni divergentným writers;
- post-point operations majú replay/merge/compensation/reconciliation contract;
- measured RPO/RTO sú porovnané s objectives;
- wrong/corrupted candidate je odmietnutý;
- second restore vykoná iný responder alebo alternate target;
- residual gaps majú ownera a termín.

## 22. Troubleshooting restore failure-u

```text
restore objective a exact subject
→ candidate/clean-point identity
→ catalog visibility
→ artifact completeness a retention
→ key/access eligibility
→ target capacity/network/storage
→ engine/tool/schema compatibility
→ log chain a recovery state
→ dependency/config/identity reconstruction
→ data/application/business validation
→ fencing/cutover/reconciliation
→ measured RPO/RTO a recurrence control
```

Symptom `restore job failed` môže patriť access, artifact, key, capacity, engine alebo data boundary. Symptom `restore succeeded, app je zlá` patrí vyššej compatibility alebo business consistency vrstve.

## 23. Earlier controls

- business impact analysis;
- protected-subject inventory;
- consistency-group manifest;
- backup coverage read-back;
- isolated recovery account;
- immutable/offline copy;
- restore-key canary;
- catalog mimo primary failure domainu;
- clean-point classification;
- retention podľa corruption discovery windowu;
- application/schema compatibility matrix;
- scheduled full a partial restore drills;
- provider/external-ledger reconciliation path;
- RPO/RTO measurement od business boundaries;
- recovery action items a second-responder test.

## 24. Anti-patterny

### Backup job je zelený

Potvrdzuje capture attempt, nie clean, readable a business-valid restore.

### Replication je backup

Logical corruption alebo compromised credential sa replikuje.

### Latest snapshot

Môže byť najnovšia corrupted generation.

### Restore priamo do production

Zvyšuje blast radius a môže zničiť current evidence alebo validné post-point operations.

### Kľúč existuje

Restore identity ho nemusí vedieť použiť v affected account/Regione.

### Testovali sme jednu table

Nepreukazuje dependency, consistency group, scale ani business recovery.

### RTO = čas restore API

Ignoruje provisioning, data validation, application startup, reconciliation a cutover.

### Immutable všetko vyrieši

Immutable corrupted backup zostáva corrupted.

## 25. Kontrolné otázky

1. Čo tvorí exact backup subject a consistency group?
2. Ako sa backup, replication, snapshot, archive a export líšia?
3. Aký je rozdiel medzi crash-, application-, transaction- a business-consistent state-om?
4. Prečo latest point nemusí byť clean point?
5. Ako encryption key dependency ovplyvňuje recoverability?
6. Čo musí obsahovať recovery catalog?
7. Kedy zvoliť full rewind, side-by-side merge, replay alebo compensation?
8. Prečo je fencing potrebný?
9. Ktoré validation layers nasledujú po engine restore?
10. Prečo successful backup jobs nezabránili dlhému recovery v `SRE-PAY-54`?
11. Čo musí obsahovať realistický restore drill?
12. Čo overuje backup/restore acceptance verdict?

## Glossary impact

Relevantné pojmy: protected backup subject, consistency group, acknowledgement boundary, crash-consistent backup, application-consistent backup, business-consistent recovery, clean point, recovery candidate, effective backup assignment, recovery catalog, key recoverability, isolated restore, recovery fencing, post-point divergence, side-by-side restore, restore validation stack a backup/restore acceptance verdict.

## Primárne zdroje

- [NIST SP 800-34 Rev. 1 — Contingency Planning Guide for Federal Information Systems](https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final)
- [CISA — StopRansomware Guide](https://www.cisa.gov/stopransomware/ransomware-guide)
- [Google SRE — Data Integrity: What You Read Is What You Wrote](https://sre.google/sre-book/data-integrity/)
- [Google SRE — Emergency Response](https://sre.google/sre-book/emergency-response/)
