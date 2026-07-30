# Backups a point-in-time recovery

Backup nie je úspešne dokončený scheduled job ani objekt s príponou `.bak`. Je to obnoviteľný, versionovaný mechanizmus pre presne definovaný data a business subject. Point-in-time recovery nie je iba výber timestampu. Obnova musí skombinovať správny base state, neprerušený change-log, správnu timeline alebo event position, použiteľné keys a identity, kompatibilnú schema a application generation a následne preukázať, že obnovený systém vie bezpečne pokračovať v business operáciách.

```text
business recovery objective
→ exact protected subject a consistency group
→ base backup + change-log generation
→ durable capture, read-back, retention a key lineage
→ clean recovery candidate a target position
→ isolated restore a controlled replay
→ engine, schema, data a application validation
→ post-point reconstruction a reconciliation
→ writer fencing, promotion a traffic ramp
→ measured RPO/RTO a alternate restore
```

Záloha má hodnotu až vtedy, keď z nej možno opakovateľne vytvoriť správny authoritative state. Zelený upload, existujúci snapshot alebo fungujúca replica sú iba intermediate evidence.

## 1. Recovery subject a consistency boundary

Tvrdenie `databáza je zálohovaná` nehovorí, čo sa vlastne chráni. Recovery subject musí pomenovať engine a cluster identity, databases a schemas, authoritative business facts, transaction a acknowledgement boundary, base-backup generation, požadovaný WAL alebo binary-log interval, schema a application generation, encryption-key lineage, restore identity, recovery target, RPO/RTO a post-point operations, ktoré bude potrebné replaynuť alebo reconciliovať.

Pre Atlas Payments je protected subject širší než jedna tabuľka:

```text
capability: complete merchant settlement exactly once
PostgreSQL authority:
  settlement intent
  outbox command
  idempotency operation
  final reconciliation state
external evidence:
  MySQL policy generation
  provider idempotency ledger
ack boundary:
  HTTP 202 až po atomic settlement + outbox commit
```

Ak sa obnoví `settlements`, ale chýba outbox alebo idempotency state, databáza môže byť technicky spustiteľná a súčasne business-nekonzistentná. Consistency group preto nie je zoznam súborov; je to množina facts a ordering evidence, ktoré spolu rozhodujú o jednom business outcome-e.

## 2. Backup, snapshot, replication a archive

Tieto mechanizmy riešia odlišné problémy. Logical backup exportuje objekty a rows cez engine-aware logical representation. Physical alebo base backup zachytáva engine storage generation použiteľnú ako starting point pre physical recovery. Snapshot kopíruje storage state v danom bode, ale bez coordination nemusí byť application-consistent naprieč volumes alebo stores. Continuous WAL či binary-log archive zachováva zmeny po base backup-e. Replication poskytuje current alebo near-current copy pre availability, nie clean historical point. Dlhodobý archive chráni retained data alebo evidence, ale nemusí byť priamo použiteľný pre online restore.

Tieto rozdiely určujú failure coverage. Replica okamžite skopíruje chybný `DELETE`, zlú migration aj kompromitovaný write. Snapshot vytvorený po chybe je úspešný snapshot poškodeného state-u. Logical dump môže byť portable, ale nie je PostgreSQL base backupom pre WAL replay. Recovery stratégia preto musí explicitne skladať viac mechanizmov podľa chráneného subjectu.

## 3. Capture a change-log continuity

PostgreSQL PITR používa engine-consistent base backup a neprerušenú sériu WAL records. Base backup poskytne starting files; WAL replay ich posunie na požadovanú transaction boundary a promotion vytvorí novú timeline.

```text
base-backup start LSN
→ complete base-backup files
→ continuous WAL sequence
→ timeline history
→ restore_command/read-back
→ replay po recovery target
→ recovery completion
→ new timeline promotion
```

`archive_command` success musí znamenať, že segment je durably uložený a neskôr čitateľný. Lokálne potvrdenie upload requestu nestačí. Chýbajúci jediný required segment môže znemožniť recovery za daný bod. Rovnako treba zachovať timeline history a configuration alebo external files, ktoré WAL nereprezentuje.

MySQL point-in-time recovery typicky začína full backupom a zaznamenanou binary-log coordinate alebo GTID množinou. Po restore sa replayujú binary-log events až po exact stop position. Timestamp môže byť praktický orientačný údaj, ale event position alebo GTID je presnejšia authority, najmä keď viac events zdieľa rovnakú časovú granularitu.

```text
full backup + binlog coordinate
→ restore base state
→ verify source/server identity
→ replay complete binlog sequence
→ stop pred/na exact event
→ validate schema a business state
```

V oboch produktoch je rozhodujúca chain continuity, nie počet zelených uploadov. Kontrola musí overiť sequence, checksums, object readability, source identity, retention vzhľadom na najstarší supported base backup, key availability a retrieval latency.

## 4. Clean point a recoverable candidate

Najnovší backup nemusí byť najlepší kandidát. Recovery candidate sa posudzuje podľa toho, či vznikol pred alebo po triggeri, či má complete log sequence, správnu source/timeline identity, kompatibilnú schema a binaries, použiteľné keys a či už obsahuje logical corruption.

```text
candidate generation
→ trigger pred alebo po candidate?
→ complete log continuity?
→ correct source/timeline?
→ schema a application compatible?
→ corruption absent?
→ keys a identity usable?
→ dependencies recoverable?
→ post-point divergence spracovateľná?
```

Najsilnejší recovery target kombinuje engine position s business eventom. `Obnoviť na 11:46` je nejednoznačné, ak chybný commit prišiel o `11:46:12.418` a viac clocks alebo stores nemá spoločnú transaction authority. Praktický target môže byť PostgreSQL LSN, named restore point, MySQL event position/GTID a zároveň posledný potvrdený business operation ID pred incidentom.

## 5. Cross-store recovery a derived state

Distributed platforma môže používať PostgreSQL, MySQL, Redis, object storage, broker a external provider. Rovnaký timestamp na všetkých systémoch nevytvára cross-store atomic point. Recovery model musí vedieť, kto vlastní každý fact, ktorý state je derived a rebuildable a aké durable identity prepájajú stores.

```text
PostgreSQL settlement/outbox LSN
↔ durable operation/event ID
↔ MySQL policy generation
↔ provider idempotency identity
↔ Redis cache/dedupe generation
```

Redis cache možno po restore zahodiť a rebuildnúť. Ak však application používa Redis key ako jediný proof, či provider call už prebehol, Redis persistence a failover semantics sa stávajú súčasťou correctness boundary. To je zvyčajne authority inversion: rebuildable state rozhoduje o irreversible business effecte.

Post-point operations sa preto nesmú slepo zahodiť ani replaynuť. Každá operation patrí do cohortu `never-committed`, `committed-never-sent`, `sent-unknown`, `provider-completed` alebo `duplicate-attempt`. Recovery manifest vzniká koreláciou database logs, outboxu, API evidence, broker checkpointov a provider ledgeru.

## 6. Restore generation, isolation a validation

Restore je nový subject s vlastným generation ID, source manifestom, target environmentom, engine/schema/application versions, recovered position a validation evidence. Má prebiehať izolovane, aby nevytvoril druhého writera alebo neodoslal reálne provider operations ešte pred acceptance verdictom.

Validácia ide od infraštruktúry po business outcome. Najprv sa overí storage, network, permissions, encryption keys a restore identity. Potom engine startup, recovery completion, checksums a catalogs. Nasleduje schema generation, constraints a extensions; data integrity a business invarianty; application transaction, idempotency a read/write paths; napokon exact accepted, completed a unknown cohorts. Až potom možno rozhodnúť o promotion.

Restore test, ktorý používa trvalý super-admin účet alebo manuálne obchádza current network a KMS controls, neoveruje production recovery path. Identity, key rotation, break-glass access, object immutability a deletion protection patria do rovnakého mechanizmu ako samotné backup files.

## 7. Connected incident `DB-PAY-57`

Release `payments 8.1` používal PostgreSQL ledger, MySQL merchant-policy store, Redis idempotency/dedupe layer a provider ledger. Po end-of-month scale-out-e bežalo `96` settlement Podov s PostgreSQL poolom `40`, teda teoretických `3 840` client sessions proti približne `585` dostupným application slots.

O `11:38 UTC` network flap vytvoril reconnect storm. Emergency PgBouncer transaction pooling odstránil server-session affinity, hoci application nastavovala tenant context iba pri physical connection initialization a používala temporary tables. Od `11:46:12 UTC` preto časť operations používala missing alebo stale policy context. Incident bol potvrdený až o `17:58 UTC`; logical corruption už bola v primary, replicas aj novších snapshots.

Tím požadoval PostgreSQL PITR na `11:46:11 UTC`. Dashboard ukazoval successful base backup a zelené WAL uploads, independent continuity kontrola však zistila:

```text
last continuous WAL: 11:40:59 UTC
missing interval:     11:41:00–11:56:59 UTC
next available WAL:   11:57:00 UTC
```

Object lifecycle policy odstránila segments z dočasného archive prefixu po tom, čo uploader lokálne označil upload za complete. Requested target preto nebol dosiahnuteľný. MySQL mal vlastný binlog coordinate, Redis AOF `everysec` a provider samostatnú external history; versionovaný cross-store checkpoint neexistoval.

Trigger bol reconnect storm a pooling zmena. Backup/PITR root cause bol acceptance založený na job activity namiesto durable continuity a tested restore-u. Replication a novšie snapshots logical corruption iba rozšírili. Cross-store recovery predĺžila absencia spoločnej operation a policy-generation identity.

## 8. Recovery, acceptance a forbidden outcomes

Containment najprv zmrazilo schema, pool a retry zmeny; fence-nulo affected write cohort; zachovalo PostgreSQL data/WAL/timelines, MySQL binlogs, Redis persistence/config a provider evidence; uzavrelo backup catalog a určilo prvý chybný business event spolu s engine positions.

Recovery použila isolated PostgreSQL restore po posledný kontinuálny bod `11:40:59 UTC`. Tím vytvoril exact manifest post-point operations a cez outbox, API, MySQL binlog a provider ledger rekonštruoval iba evidence-backed cohorts. Derived projections a Redis dedupe keys boli rebuildnuté, nová timeline bola promoted až po writer fencing-u a traffic sa vracal cez canary a staged ramp. Následný second restore z iného base backupu a alternate targetu overil, že výsledok nebol závislý od jedného artifactu.

**Positive path** obnoví správny base backup, replayne complete log sequence na clean business boundary, prejde engine až business validáciou a bezpečne vytvorí nový authoritative writer.

**Recovery path** pracuje so starším clean pointom, explicitne zmeria objective gap a rekonštruuje post-point operations iba z durable a external evidence. Permanent loss, reconstructed work a actual RPO/RTO sa reportujú oddelene.

**Failure path** zastaví restore pri missing segment-e, nečitateľnom objecte, stale keyi, wrong source identity alebo incompatible schema. Nesmie improvizovať silent gap ani označiť nearest available point za requested target.

**Forbidden path** odmietne restore poškodeného latest snapshotu, promotion bez fencing-u, cache absence ako proof business absence, slepé replayovanie unknown provider operations a používanie production data v neizolovanom teste.

Mechanizmus je prijatý až vtedy, keď alternate target, druhý responder a second restore prejdú rovnakým contractom. V `DB-PAY-57` bola permanentná strata acknowledged operations po reconciliation nulová, ale pôvodný PITR objective napriek tomu zlyhal, pretože requested point nebol technicky dosiahnuteľný.

## 9. Troubleshooting a anti-patterny

Diagnostika recovery failure-u postupuje od exact recovery generation cez base-backup identity, catalog/readability, log continuity a timeline/GTID target ku keys, engine logs, schema/application compatibility, business invariants, post-point divergence a promotion/fencing. `Restore sa spustil` alebo `database accepting connections` nie je finálny verdict.

Najčastejšie anti-patterny sú zelený backup job bez read-backu, replica považovaná za backup, latest snapshot automaticky považovaný za clean, PITR definované iba timestampom, rovnaký wall-clock čas vydávaný za cross-store consistency a restore uzavretý po engine startup-e. Každý z nich zamieňa artifact alebo intermediate observation za recoverable business state.

## 10. Kontrolné otázky

1. Čo tvorí exact database recovery subject a consistency group?
2. Ako sa logical backup, physical/base backup, snapshot, replication a archive líšia?
3. Prečo PostgreSQL PITR potrebuje base backup aj complete WAL sequence?
4. Prečo je pri MySQL event position alebo GTID presnejší než samotný timestamp?
5. Ako sa clean recovery point líši od latest available pointu?
6. Prečo rovnaký timestamp nevytvára cross-store transaction?
7. Čo tvorí restore generation a prečo musí byť izolovaná?
8. Ako sa klasifikujú post-point operations a unknown provider outcomes?
9. Prečo requested target v `DB-PAY-57` nebol dosiahnuteľný?
10. Ktoré positive, recovery, failure a forbidden paths musia prejsť?

## Glossary impact

Relevantné pojmy: database recovery subject, protected consistency group, logical backup, physical backup, base backup, continuous log archive, WAL continuity, binary-log continuity, recovery target, recovery timeline, clean recovery point, archive read-back, restore generation, cross-store recovery checkpoint, post-point divergence, work recovery a backup/PITR acceptance verdict.

## Primárne zdroje

- [PostgreSQL 18 Documentation — Backup and Restore](https://www.postgresql.org/docs/current/backup.html)
- [PostgreSQL 18 Documentation — Continuous Archiving and Point-in-Time Recovery](https://www.postgresql.org/docs/current/continuous-archiving.html)
- [MySQL 8.4 Reference Manual — Backup and Recovery](https://dev.mysql.com/doc/refman/8.4/en/backup-and-recovery.html)
- [MySQL 8.4 Reference Manual — Point-in-Time Recovery](https://dev.mysql.com/doc/refman/8.4/en/point-in-time-recovery.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Replication a high availability](replication-and-high-availability.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Connection pooling →](connection-pooling.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
