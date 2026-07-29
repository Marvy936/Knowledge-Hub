# Backups a point-in-time recovery

Backup nie je súbor s príponou `.bak` ani zelený scheduled job. Je to versionovaný recovery mechanismus pre presne definovaný data a business subject. Point-in-time recovery nie je iba voľba timestampu; je to obnovenie správneho base state-u, kontinuálneho change logu, správnej timeline, keys, schema a dependencies do bodu, ktorý je technicky konzistentný a zároveň použiteľný pre business recovery.

```text
business recovery objective
→ exact protected subject a consistency group
→ backup/log generation a clean-point semantics
→ capture, transfer, isolation, encryption a retention
→ catalog a continuity evidence
→ recovery target a timeline
→ isolated restore a log replay
→ schema/dependency/application validation
→ post-point merge, replay alebo reconciliation
→ promotion, fencing a business acceptance
→ second-restore a alternate-target closure
```

## 1. Exact database recovery subject

Tvrdenie `databáza je zálohovaná` je neúplné. Recovery subject musí obsahovať najmenej:

- engine, major version a exact cluster/server identity;
- databases, schemas, tablespaces a external large-object dependencies;
- authoritative business facts a consistency group;
- transaction/commit a client acknowledgement boundary;
- base-backup generation;
- WAL, binary-log alebo iný change-log interval;
- timeline, LSN, GTID, binlog file/position alebo ekvivalentný ordering subject;
- schema a migration generation;
- encryption keys, credentials a restore identity;
- recovery target a stop semantics;
- RPO, RTO a work-recovery boundary;
- post-point operations, ktoré treba replaynuť alebo reconciliovať;
- allowed aj forbidden restore outcomes.

Príklad:

```text
capability: complete merchant settlement exactly once
primary store: PostgreSQL cluster pay-prod-eu1
protected group:
  settlements
  settlement_events
  outbox_commands
  idempotency_operations
ack boundary: HTTP 202 after atomic settlement + outbox commit
base backup: BB-PAY-2026-07-29T00:00Z
WAL range: base backup start LSN → target LSN
schema: payments-v42
recovery target: immediately before first incorrect tenant-policy write
business RPO: no lost acknowledged intent
business RTO: safe degraded admission within 15 min; completion within 45 min
```

Ak sa obnoví iba `settlements`, ale nie outbox, idempotency alebo provider-correlation state, databáza môže byť crash-consistent a business-inconsistent.

## 2. Backup, snapshot, replication a archive nie sú synonymá

| Mechanizmus | Primárny účel | Typická hranica | Čo sám negarantuje |
|---|---|---|---|
| logical dump | portable logical export | selected databases/objects | physical layout, WAL continuity, rýchly full restore |
| physical/base backup | engine-level starting state | celý cluster/server generation | recovery po base-backup čase bez change logu |
| snapshot | point copy storage state-u | volume/filesystem/storage set | application alebo cross-volume consistency |
| continuous log archive | changes po base backup-e | WAL/binlog/change stream | použiteľný base backup a complete sequence |
| replication | current redundant copy | replication topology | clean historical point pri logical corruption |
| archive | long-term retained data/evidence | retention subject | online recovery path alebo current application compatibility |

Replication môže okamžite skopírovať chybný `DELETE`, nesprávny tenant update alebo kompromitovaný write. Snapshot po tejto zmene je úspešný snapshot poškodeného state-u. Backup strategy preto potrebuje history, clean-point selection a nezávislú restore cestu.

## 3. Logical a physical backup

### Logical backup

Logical export zapisuje databázové objekty a rows cez engine-aware logical representation. Je vhodný pre:

- selected object recovery;
- migration medzi kompatibilnými generations;
- audit alebo portable export;
- menšie datasets;
- obnovu, pri ktorej je prijateľný dlhší reload a index rebuild.

Musí sa overiť:

- transaction snapshot alebo consistency semantics exportu;
- zahrnutie roles, grants, extensions, sequences, routines a large objects;
- schema ordering a dependency graph;
- encoding, collation a version compatibility;
- restore throughput a resource cost;
- referential a business validation po importe.

### Physical backup

Physical/base backup zachytáva engine storage generation. Je vhodný pre veľké databázy a WAL/binlog-based recovery. Musí byť koordinovaný s engine-om; obyčajná kópia aktívnych data files bez snapshot alebo backup protocolu môže obsahovať nekonzistentné pages.

Physical backup je naviazaný na:

- engine a major-version compatibility;
- tablespace paths a storage layout;
- checkpoint/backup start a stop positions;
- WAL alebo redo dependencies;
- encryption a file ownership;
- recovery configuration.

## 4. PostgreSQL PITR mechanismus

PostgreSQL PITR kombinuje base backup s kontinuálnym WAL archívom:

```text
base backup start LSN
→ base backup files
→ complete WAL sequence od backup startu
→ restore_command alebo archive retrieval
→ redo replay
→ recovery target time/name/XID/LSN podľa contractu
→ promotion na novej timeline
```

WAL zaznamenáva zmeny potrebné na crash recovery. Base backup poskytne starting files; archivované WAL segments posunú state dopredu. Recovery môže skončiť pred konkrétnou chybnou zmenou.

Kritické boundaries:

- `archive_command` success musí znamenať durable a čitateľnú archiváciu, nie iba prijatie upload requestu;
- žiadny required WAL segment nesmie chýbať;
- base backup musí začínať pred prvým dostupným required WAL segmentom;
- timeline history files patria do recovery chainu;
- recovery target musí mať jednoznačnú clock/LSN authority;
- restore sa má vykonať izolovane, aby nevytvoril druhého writera;
- promotion vytvorí novú timeline; stará history sa nesmie potichu prepísať;
- schema, extensions a application binaries musia byť kompatibilné s target pointom.

`pg_dump` je logical backup. Nie je base backupom pre WAL replay.

## 5. MySQL point-in-time recovery

MySQL PITR typicky používa full backup a binary logs:

```text
full backup a recorded binlog coordinate
→ restore full backup
→ identify required binary-log sequence
→ replay events po backup coordinate
→ stop pred/na exact event position alebo target time
→ validate server, schema a business state
```

Binary log slúži aj replication a recovery use case-om. Recovery contract musí poznať:

- source/server UUID a binlog generation;
- binlog file a position alebo GTID set;
- row/statement/mixed logging implications;
- encrypted-log key path;
- retention a continuity;
- excluded alebo filtered events;
- target event boundary;
- downstream replicas a clients, ktoré treba fence-nuť.

Timestamp je slabší target než exact event position, keď viac events zdieľa rovnakú časovú granularitu alebo clocks nie sú authoritative.

## 6. Clean point a recovery target

`Najnovší backup` nemusí byť najlepší recovery candidate. Kandidát sa klasifikuje podľa:

```text
candidate generation
→ pred alebo po triggeri?
→ complete log continuity?
→ correct timeline/source identity?
→ schema/application compatibility?
→ logical corruption present?
→ encryption a access usable?
→ dependencies recoverable?
→ post-point divergence spracovateľná?
→ business invarianty validné?
```

Recovery target môže byť:

- timestamp;
- named restore point;
- PostgreSQL LSN alebo transaction boundary;
- MySQL binlog event position alebo GTID set;
- application event ID;
- business operation boundary.

Najsilnejší target kombinuje engine position s business evidence. Tvrdenie `obnoviť na 11:46` je slabé, ak nevie určiť, či chybný commit o `11:46:12.418` patrí pred alebo po targete.

## 7. Continuity a retention

PITR je chain. Jediný chýbajúci required segment môže zablokovať replay za daný bod.

```text
base backup
→ WAL/binlog segment 1
→ segment 2
→ ...
→ segment N
→ target
```

Kontroly musia overovať:

- sequence continuity, nie iba počet uploadov;
- object existence aj readability;
- checksum a expected size;
- source cluster/server identity;
- retention vzhľadom na najstarší supported base backup;
- timeline/GTID metadata;
- encryption-key retention;
- catalog consistency;
- restore retrieval latency;
- forbidden deletion alebo lifecycle transitions.

`Backup job succeeded` môže znamenať iba to, že lokálny process odovzdal object storage request. Recovery acceptance vyžaduje independent read-back a restore.

## 8. Cross-store consistency group

Distributed application môže používať PostgreSQL, MySQL, Redis, object storage a external provider. Rovnaký timestamp na každom systéme nevytvára automaticky jeden business-consistent point.

Treba definovať:

- ktorý store je authority pre ktorý fact;
- durable ordering alebo event ID medzi stores;
- whether derived store možno rebuildnúť;
- provider/external ledger availability;
- schema/config generation;
- cache a ephemeral state semantics;
- post-point reconciliation.

Príklad:

```text
PostgreSQL settlement/outbox LSN
↔ durable event ID
↔ MySQL merchant-policy generation
↔ provider idempotency ledger
↔ Redis cache/dedupe generation
```

Ak Redis obsahuje iba rebuildable cache, nemusí vstupovať do data-loss RPO. Ak sa však používa ako jediný idempotency authority, jeho persistence a failover semantics sa stávajú súčasťou business recovery subjectu.

## 9. Encryption, identity a isolation

Backup, ktorý nemožno dešifrovať, nie je recoverable. Recovery chain zahŕňa:

- backup encryption key;
- key version a wrapping lineage;
- restore principal a network path;
- separated production/backup administration;
- immutable alebo deletion-protected copies;
- audit log;
- break-glass access;
- tested key recovery;
- retention po key rotation.

Restore test nesmie používať širšie permanentné privilege než reálny incident responder. Inak overuje lab exception, nie production recovery path.

## 10. Restore je samostatná generácia

Restore vytvára nový subject:

```text
restore generation ID
→ source backup/log manifest
→ target environment
→ engine/schema/application versions
→ recovered position/timeline
→ validation evidence
→ promotion/fencing decision
```

Validácia má vrstvy:

1. **Infrastructure:** storage, permissions, network, keys.
2. **Engine:** startup, recovery completion, checksums, system catalogs.
3. **Schema:** expected migrations, constraints, extensions.
4. **Data:** counts, referential integrity, sampled/complete invariants.
5. **Application:** reads, writes, transaction a idempotency flows.
6. **Business:** exact accepted/completed/unknown cohorts.
7. **Forbidden:** corruption, duplicates, cross-tenant state, stale writer.
8. **Recovery operations:** replay, merge, compensation a backlog drain.

## 11. Connected incident `DB-PAY-57`

Release `payments 8.1` rozdelil payment platformu na:

```text
settlement-api
→ PostgreSQL ledger-service
→ MySQL merchant-policy-service
→ Redis idempotency/dedupe layer
→ provider
→ projection-service
```

Po end-of-month autoscale bežalo `96` settlement Podov. Každý mal PostgreSQL pool `40`, teda teoretických `3 840` client sessions proti server envelope-u približne `585` application connections.

O `11:38 UTC` krátky network flap vytvoril reconnect storm. Pri pool exhaustion bol núdzovo zapnutý PgBouncer transaction pooling. Aplikácia však nastavovala tenant context raz pri session initialization a používala temporary table pre batch processing. Transaction pooling zrušil server-session affinity.

Od `11:46:12 UTC` začali niektoré operations používať missing alebo stale tenant-policy context. Incident bol potvrdený až o `17:58 UTC`, keď už bol incorrect state v primary, replicas aj neskorších snapshots.

Tím chcel PostgreSQL obnoviť na `11:46:11 UTC`. Backup catalog ukazoval:

```text
base backup: 00:00 UTC — success
WAL archive uploads: green
requested target: 11:46:11 UTC
```

Independent continuity check však našiel:

```text
last continuous WAL: 11:40:59 UTC
missing interval: 11:41:00–11:56:59 UTC
next available WAL: 11:57:00 UTC
```

Object lifecycle policy odstránila objects z dočasného archive prefixu, hoci uploader už lokálne označil segments ako archived. Presný target nebol dosiahnuteľný z daného base backupu.

Súčasne:

- MySQL merchant-policy store mal vlastný binlog coordinate;
- Redis používal AOF `everysec`, ale nebol navrhnutý ako permanentný settlement authority;
- provider ledger obsahoval external attempts;
- neexistoval versionovaný cross-store consistency checkpoint.

### Causal boundaries

- **Trigger:** reconnect storm a núdzová pooling zmena.
- **Backup/PITR root cause:** recovery control overoval job/upload activity, nie durable WAL continuity, clean target reachability a restore.
- **Recovery amplifier:** logical corruption bola replikovaná do replicas a nových snapshots.
- **Cross-store amplifier:** neexistoval authoritative checkpoint medzi PostgreSQL eventom, MySQL policy generation a provider ledgerom.
- **Detection delay:** front-door success a backup dashboards zostali zelené.

## 12. Evidence-preserving containment

Bezpečné prvé kroky:

```text
freeze schema/config/pool changes
→ fence affected write cohort
→ preserve PostgreSQL data/WAL/timelines
→ preserve MySQL binlogs a coordinates
→ snapshot Redis persistence/config/runtime state
→ export provider idempotency evidence
→ seal backup catalog a object lifecycle evidence
→ identify first bad business event + engine positions
→ classify recovery candidates
```

Nie je bezpečné okamžite prepísať production z najnovšieho snapshotu alebo zmazať affected rows bez immutable manifestu.

## 13. Authoritative recovery

Tím použil:

1. isolated PostgreSQL restore po posledný kontinuálny point `11:40:59 UTC`;
2. application/business invariant validation;
3. exact manifest operations medzi `11:41:00` a containmentom;
4. outbox, API, MySQL binlog a provider-ledger correlation;
5. classification `never-committed`, `committed-never-sent`, `sent-unknown`, `provider-completed`;
6. bounded reconstruction iba pre evidence-backed operations;
7. rebuild derived projections a Redis dedupe keys z authoritative outcomes;
8. new timeline promotion s writer fencing;
9. canary a staged traffic ramp;
10. second restore z iného base backupu a alternate targetu.

Technical recovery point bol starší než desired target, ale permanentná strata acknowledged operations bola znížená na nulu pomocou external a durable event reconciliation. To nemení fakt, že pôvodný PITR objective neprešiel.

## 14. Backup/PITR acceptance verdict

Recovery mechanismus je prijatý, keď:

- exact protected subject a consistency group sú explicitné;
- logical/physical/base backup semantics sú vhodné;
- capture je transaction/engine-consistent;
- WAL/binlog/change-log sequence je complete, čitateľná a správne identifikovaná;
- retention chráni celý supported recovery window;
- keys, identities, network a tools sú current;
- clean candidate a recovery target sú jednoznačné;
- restore beží izolovane a vytvorí evidovanú timeline/generation;
- engine, schema, data, application a business validations prejdú;
- post-point divergence má replay/merge/compensation/reconciliation contract;
- old writers a wrong timelines sú fence-nuté;
- actual recovered point, permanent loss a recovery time sú zmerané;
- alternate target a second responder prejdú;
- forbidden missing-segment, stale-key a corrupted-candidate scenarios zlyhajú bezpečne.

## 15. Troubleshooting recovery failure-u

```text
restore alebo PITR zlyháva
→ exact recovery subject/generation
→ base backup identity a compatibility
→ catalog/readability/checksums
→ WAL/binlog continuity a source identity
→ timeline/GTID/event target
→ keys, roles, paths a permissions
→ engine recovery logs
→ schema/application generation
→ data/business invariants
→ post-point divergence
→ promotion/fencing
→ objective-vs-actual verdict
```

## 16. Anti-patterny

### Backup job je zelený

Neoveruje durable archive, continuity, readability ani restore.

### Replica je backup

Logical corruption a malicious writes sa replikujú.

### Najnovší snapshot je najlepší

Môže obsahovať incident state.

### PITR = vybrať timestamp

Chýba engine position, timeline, clean boundary a business event mapovanie.

### pg_dump + WAL

Logical dump nie je PostgreSQL base backup pre physical WAL replay.

### Obnovíme všetky stores na rovnaký čas

Clocks a independent logs nevytvárajú cross-store transaction.

### Restore skončil pri engine start-e

Application, business, reconciliation a forbidden outcomes ešte nemusia prejsť.

### Kľúč obnovíme počas incidentu

Untested key path môže dominovať RTO.

## 17. Kontrolné otázky

1. Čo tvorí exact database recovery subject?
2. Ako sa backup, snapshot, replication a archive líšia?
3. Kedy použiť logical a physical backup?
4. Ako PostgreSQL base backup a WAL vytvárajú PITR?
5. Ako MySQL full backup a binary logs vytvárajú PITR?
6. Prečo je continuity dôležitejšia než počet uploaded segments?
7. Ako sa clean point líši od latest pointu?
8. Čo je recovery timeline?
9. Prečo rovnaký timestamp nevytvára cross-store consistency?
10. Prečo `DB-PAY-57` nemohlo dosiahnuť requested target?
11. Ako možno rekonštruovať post-point business operations?
12. Čo musí overiť backup/PITR acceptance verdict?

## Glossary impact

Relevantné pojmy: database recovery subject, protected consistency group, logical backup, physical backup, base backup, continuous log archive, WAL continuity, binary-log continuity, recovery target, recovery timeline, clean recovery point, archive read-back, restore generation, cross-store recovery checkpoint, post-point divergence, work recovery a backup/PITR acceptance verdict.

## Primárne zdroje

- [PostgreSQL Documentation — Backup and Restore](https://www.postgresql.org/docs/current/backup.html)
- [PostgreSQL Documentation — Continuous Archiving and Point-in-Time Recovery](https://www.postgresql.org/docs/current/continuous-archiving.html)
- [MySQL 8.4 Reference Manual — Backup and Recovery](https://dev.mysql.com/doc/refman/8.4/en/backup-and-recovery.html)
- [MySQL 8.4 Reference Manual — Point-in-Time Recovery](https://dev.mysql.com/doc/refman/8.4/en/point-in-time-recovery.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Replication a high availability](replication-and-high-availability.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Connection pooling →](connection-pooling.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
