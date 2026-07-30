# Backup a restore

Backup je oddelená, spravovaná a obnoviteľná reprezentácia presne definovaného subjectu. Restore je proces, ktorý z vybraného recovery candidate-u materializuje system alebo data state. Recovery je širší end-to-end outcome: obnovuje business capability vrátane dependencies, identities, configuration, trafficu, post-point divergence a reconciliation. Úspešný snapshot alebo zelený backup job preto recoverability nedokazuje.

Recoverability vzniká až vtedy, keď organizácia vie nájsť správny clean point, získať artifact aj key, vytvoriť vhodný target, obnoviť compatible dependencies, overiť technical a business invariants a bezpečne vykonať merge, replay alebo cutover bez divergentných writers.

## 1. Dominantný protected-subject-to-recovery lifecycle

Backup design sa odvodzuje od business recovery objective-u a failure modelu. Capture je iba skorý krok; rozhodujúce sú isolation, clean-candidate selection, restore execution a business validation.

```text
business recovery objective a failure model
→ exact protected subject a consistency group
→ acknowledgement a clean-point semantics
→ effective backup policy a assignment
→ capture a immutable recovery generation
→ isolation, encryption, retention a catalog
→ integrity, readability a coverage verification
→ recovery candidate selection
→ isolated restore a dependency reconstruction
→ technical, data, application a business validation
→ fencing, merge/replay/cutover a reconciliation
→ second restore a alternate-scenario validation
```

Každá generation musí byť reprodukovateľne prepojená so source subjectom, timestampom alebo sequence boundary, schema/application compatibility, key dependency a tested statusom.

## 2. Exact protected subject a consistency group

`Databáza je zálohovaná` je neúplné tvrdenie. Protected subject obsahuje capability, exact datasets, schema/application generation, account/Region/tenant, acknowledgement boundary, retention/legal constraints, key a identity dependencies, ownera, RPO/RTO a recovery consumers.

```text
capability: merchant settlement reconciliation
primary: PostgreSQL payments-prod-eu
related: outbox, broker offsets, object evidence, provider references
schema: settlement-ledger v17
application: payments-api 7.25.0
consistency group: CG-PAY-04
ack: committed payment + outbox intent
RPO: 5 min
RTO: 45 min
owner: Payments Resilience
```

Consistency group je versionovaný zoznam subjects, ktoré treba obnoviť alebo reconciliovať spolu. Každý member má authority, capture method, timestamp/sequence, retention, restore method, reconciliation rule a ownera. External provider ledger nemusí byť organizáciou backupovateľný, ale musí zostať v recovery contracte. Samostatne validné component restores môžu vytvoriť business-neplatnú kombináciu.

## 3. Backup, replication, snapshot, archive a export

Tieto artifacts riešia odlišné problems a systém ich používa na iných boundaries. Backup je spravovaný recovery contract: policy určuje, ktorý subject sa zachytí, ako dlho sa uchová a ako sa nájde a obnoví. Replication je availability mechanismus, ktorý udržiava ďalší current copy, ale zvyčajne zdieľa mutation stream a preto rýchlo prenesie logical corruption. Snapshot, archive a export zase menia point-in-time, retention alebo portability semantics.

Rozlíšenie rozhoduje o tom, ktorý failure model je pokrytý. Live replica pomôže pri instance loss-e, no nemusí poskytnúť clean historical point; archive zachová históriu, no nemusí splniť krátky RTO. Restore materializuje artifact, zatiaľ čo recovery až overí business capability.

- **backup —** recovery-oriented copy s policy, retention, catalogom a restore pathom;
- **replication —** ďalší live alebo near-live copy subject zvyšujúci availability, ktorý však kopíruje aj logical deletion alebo compromise;
- **snapshot —** point-in-time storage/data representation s definovanou consistency semantics;
- **archive —** dlhodobé uchovanie a retrieval contract, nie nevyhnutne rýchly full restore;
- **export —** logical portable representation, ktorá nemusí zachovať engine permissions, sequences alebo transaction boundaries;
- **restore —** materializácia candidate-u do targetu;
- **recovery —** obnovenie používateľsky bezpečnej capability.

Replication nie je backup a restore nie je rollback. Application rollback nemení automaticky data state; historical restore môže odstrániť validné neskoršie operations.

## 4. Failure model, consistency a clean point

Backup policy musí pokryť physical loss, accidental deletion, application bug, silent logical corruption, ransomware alebo admin compromise, schema migration failure, Region/account loss, key loss, provider divergence a long discovery window. Jedna replica v rovnakom trust domain-e nechráni pred compromised writerom a krátka retention nepokrýva corruption zistenú po týždni.

Consistency má viac vrstiev. Crash-consistent point zodpovedá náhlemu zastaveniu a môže vyžadovať log recovery. Application-consistent point koordinuje engine/application invariants. Transaction-consistent point zachová committed boundary jedného datastore-u. Business-consistent recovery zahŕňa relevantné stores a external effects.

```text
PostgreSQL payment/outbox commit
+ broker publish/delivery state
+ provider attempt/acknowledgement
+ customer-visible projection
→ business-consistent settlement state
```

Latest point nie je automaticky clean point. Candidate môže byť najnovší dostupný, no už corrupted; starší clean point môže vyžadovať väčšiu post-point reconstruction. Selection používa incident timeline, audit/WAL, compromise interval, schema compatibility a business checkpoints.

## 5. Capture lifecycle a effective coverage

Backup lifecycle vedie od policy intentu cez discovery a assignment po artifact, copy, retention a verification:

```text
policy intent
→ resource discovery/selection
→ effective assignment
→ scheduled alebo event capture
→ backup generation
→ encryption a catalog publication
→ cross-domain copy
→ retention/immutability
→ verification a expiry
```

Configured policy nie je effective coverage. Read-back musí potvrdiť, že resource bol objavený, selector ho zahrnul, expected artifact vznikol, cross-account/Region copy dokončila, retention/lock sú effective, catalog artifact nájde a restore identity ho vie čítať/dešifrovať.

Full, incremental, differential, WAL/log, continuous a synthetic-full strategies menia capture cost, restore chain, granularity a dependency count. Dlhý incremental chain môže skrátiť backup window, ale predĺžiť recovery a zvýšiť počet points failure-u.

## 6. Isolation, encryption a retention

Backup musí prežiť compromise production trust domainu. Potrebuje oddelený account alebo admin boundary, immutable/offline copy podľa risku, deletion protection, dual control, independent audit, network segmentation, separate restore identity a key separation. Recovery environment nemá automaticky dediť production trust.

`Immutable` nechráni pred capture-om už corrupted alebo encrypted dát. Encryption zase vytvára key recoverability dependency: current key state, policy/grant, restore identity, Region/account access, provider compatibility a audited break-glass path. `Encrypted=true` bez decryption canary je configuration evidence, nie recovery evidence.

Retention musí pokryť operational points, corruption/ransomware discovery window, compliance/legal hold, cost, retrieval tier, schema compatibility a key lifetime. Príliš krátka retention odstráni posledný clean point; príliš dlhá zvyšuje privacy, compatibility a cost burden.

## 7. Artifact integrity a recovery catalog

Backup job `Completed` môže dokazovať iba upload. Artifact verification zahŕňa size/count, checksums, object completeness, log-chain continuity, catalog readability, schema parse, decryption, mount/open, referential/application invariants, malware/corruption scan a consistency-group coverage.

Checksum dokazuje, že captured bytes sa nezmenili; nedokazuje, že source capture bol clean alebo business-valid.

Recovery catalog spája protected subject s generations, timestamps/sequences, clean/unknown/compromised classification, location/retention, key dependency, tooling compatibility, last-tested status a expected duration. Musí byť dostupný aj pri výpadku primary accountu, identity, DNS a documentation platformy.

## 8. Restore target a execution lifecycle

Logical corruption sa typicky neobnovuje priamo cez current production. Bezpečný flow používa isolated forensic alebo recovery target:

```text
incident/recovery intent
→ exact subject a target
→ candidate/clean-point selection
→ access, key, network a capacity eligibility
→ isolated restore
→ engine/log recovery a schema compatibility
→ dependency/config/identity reconstruction
→ integrity/application/business validation
→ affected a post-point manifest
→ fencing a merge/replay/cutover
→ reconciliation, observation a cleanup
```

Možnosti recovery závisia od authority a side effects. Full rewind vracia celý subject a vyžaduje fencing a divergence work. Side-by-side restore extrahuje affected records. Replay používa ordered/idempotent logs. Compensation vytvorí novú business operation opravujúcu external effect. Rebuild from authority znovu vytvorí projection/cache/index.

## 9. Fencing a validation stack

Počas recovery nesmú old a new writers nekontrolovane meniť rovnaký business subject. Fencing môže použiť write freeze, epoch token, lease, route cutover, read-only mode, scheduler/consumer disable, role revocation alebo provider pause.

Validation ide vo vrstvách. Infrastructure overí resource, storage, network a keys. Engine overí log recovery a schema. Data overí counts, constraints a relationships. Application overí compatible reads/writes. Business overí critical journeys a invarianty. Forbidden verification odmietne wrong tenant, corrupted candidate, duplicate replay, stale identity alebo aktívneho old writera.

`Database accepts connections` je iba skorá vrstva, nie recovery verdict.

## 10. Connected incident `SRE-PAY-54`

Atlas používal PostgreSQL base snapshot každých šesť hodín, continuous WAL, cross-account copy, 35-dňovú retention, versioned evidence objects, provider ledger API plus 15-min export a catalog `BKP-PAY-22`. Všetky jobs boli zelené.

Compactor o `02:14:07 UTC` broad-archived active rows. Replication a snapshots po tomto bode zachytili intact bytes s invalidnou business semantics. Last DB-clean point bol `02:13:58`; posledný pre-built coordinated DB/provider checkpoint `02:03:00`. Full rewind by zahodil validné neskoršie operations, preto tím zvolil side-by-side restore a reconciliation.

Recovery path zlyhala na currentness: restore identity po account migration nemala decrypt grant, recovery subnet nemala route k catalogu, runbook očakával schema v15 namiesto v17, provider export mal 15-min granularity a duration estimate neobsahoval validation/merge. Backup data existovali; recovery mechanismus nebol current.

Authoritative flow zachoval corrupted DB, fenced compactor/writers, obnovil `02:13:58` do isolated environmentu, validoval schema/invariant, odviedol exact `7 842`-row manifest, klasifikoval post-point operations, použil provider idempotency ledger, merge-ol clean correlation metadata, replayol iba never-sent intents a reconcilioval sent-unknown/completed cohorts. Business recovery skončila o `06:03 UTC`, teda `3 h 49 min` po mutation, namiesto deklarovaných 45 minút.

## 11. Restore drills a acceptance contract

Drill musí testovať respondera, catalog discovery, key/decryption, clean-point selection, target capacity/network, tooling/schema, dependencies, validation, fencing, cutover/merge, elapsed time, cleanup a second restore. Jedna malá table bez external dependencies production recoverability nedokazuje.

Positive path obnoví known clean candidate a business canary. Corruption path musí odmietnuť latest bad candidate. Key/account-loss path musí použiť alternate restore identity. Partial-record path musí zachovať current valid operations. Second-responder alebo alternate-target test overí prenositeľnosť knowledge.

```text
positive:
clean candidate → isolated restore → business success

logical corruption:
latest bad point denied → older clean point + merge

recovery:
post-point manifest → replay/reconcile → no loss/duplicate

forbidden:
restore over live writer
wrong tenant/key/candidate
engine green without business validation
RTO measured only restore API
```

Acceptance verdict patrí exact subject, consistency group, candidate, application/schema, key/access a drill generation. Residual gaps majú ownera a termín.

## 12. Troubleshooting restore failure-u

Symptom `restore job failed` môže patriť catalog, artifact, retention, key/access, target capacity, network, tooling, schema alebo log-chain boundary. Symptom `restore succeeded, app je zlá` patrí compatibility, dependency alebo business consistency vrstve.

```text
objective a protected subject
→ candidate a clean classification
→ catalog/artifact/retention
→ key/access eligibility
→ target capacity/network/storage
→ engine/tool/schema
→ dependency/config/identity
→ data/application/business validation
→ fencing/merge/reconciliation
→ measured RPO/RTO
```

Pred opakovaním restore sa musí rozlíšiť failure pred side effectom, partial materialization a unknown target state.

## 13. Anti-patterny

Backup anti-patterny zamieňajú existence alebo control-plane success za business recoverability.

- **Backup job je zelený —** potvrdzuje capture attempt, nie clean, readable a business-valid restore.
- **Replication je backup —** logical corruption alebo compromised credentials sa rýchlo kopírujú.
- **Latest snapshot je správny —** môže byť najnovšia corrupted generation.
- **Restore priamo do production —** ničí evidence a validné post-point operations a zvyšuje blast radius.
- **Kľúč existuje —** restore identity ho nemusí vedieť použiť v affected account/Regione.
- **Testovali sme jednu table —** nepreukazuje scale, dependencies, consistency group ani business outcome.
- **RTO je restore API duration —** ignoruje provisioning, validation, application, reconciliation a cutover.
- **Immutable všetko vyrieši —** immutable corrupted backup zostáva corrupted.

## 14. Kontrolné otázky

1. Čo tvorí exact backup subject a consistency group?
2. Ako sa backup, replication, snapshot, archive a export líšia?
3. Ako sa transaction a business consistency líšia?
4. Prečo latest point nemusí byť clean candidate?
5. Čo znamená effective backup assignment?
6. Ako key recoverability ovplyvňuje restore?
7. Čo musí obsahovať recovery catalog?
8. Kedy použiť rewind, merge, replay, compensation alebo rebuild?
9. Prečo je fencing nevyhnutný?
10. Aké validation vrstvy nasledujú engine restore?
11. Prečo zelené backups v `SRE-PAY-54` nevytvorili rýchlu recovery?
12. Ktoré positive, corruption, recovery a forbidden paths patria do acceptance?

## Glossary impact

Relevantné pojmy: protected backup subject, consistency group, business-consistent recovery, clean point, recovery candidate, effective backup assignment, recovery catalog, key recoverability, isolated restore, fencing, post-point divergence, side-by-side merge, validation stack a backup/restore acceptance contract.

## Primárne zdroje

- [NIST SP 800-34 Rev. 1](https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final)
- [NIST SP 800-209 — Security Guidelines for Storage Infrastructure](https://csrc.nist.gov/pubs/sp/800/209/final)
- [CISA StopRansomware Guide](https://www.cisa.gov/stopransomware/ransomware-guide)
- [Google SRE — Data Integrity](https://sre.google/sre-book/data-integrity/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Blameless postmortems](blameless-postmortems.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: RPO a RTO →](rpo-and-rto.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
