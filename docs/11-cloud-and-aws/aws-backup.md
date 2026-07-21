# AWS Backup

AWS Backup je centralizovaná služba na definovanie, vykonávanie, monitorovanie a auditovanie backup a restore lifecycle-u podporovaných AWS resources. Neodstraňuje potrebu určiť RPO, RTO, application consistency, recovery dependencies ani vlastníka obnovy. Úspešný backup job je iba dôkaz, že vznikol recovery point; nie je dôkazom, že službu možno v požadovanom čase korektne obnoviť.

## 1. Mentálny model

```text
resource inventory a classification
→ backup policy a assignment
→ backup alebo continuous recovery point
→ vault, encryption a retention
→ copy/isolation
→ monitoring a compliance
→ restore test
→ application validation
→ recovery runbook
```

AWS Backup je control plane nad viacerými service-specific backup mechanizmami. Presné create, copy, encryption, retention a restore semantics sa preto môžu líšiť podľa resource type-u.

## 2. Backup nie je high availability

High availability minimalizuje prerušenie pri očakávateľných failures. Backup umožňuje obnoviť state po udalostiach ako:

- accidental deletion,
- logical corruption,
- ransomware alebo malicious change,
- chybný deployment alebo migration,
- account/Region incident,
- dlhodobo neodhalená chyba,
- strata primary aj replica state-u.

Replication môže rýchlo preniesť aj corruption alebo deletion. Backup potrebuje samostatný retention, immutability, access a recovery model.

## 3. Recovery point

Recovery point reprezentuje backup konkrétneho resource-u v určitom čase.

Dôležité metadata:

- source resource a account/Region,
- creation a completion time,
- backup type,
- lifecycle a expiration,
- vault,
- encryption key,
- copy lineage,
- status,
- tags a recovery metadata.

Recovery point nemusí obsahovať všetky externé dependencies aplikácie. Obnova databázy bez secrets, DNS, IAM, networking, schema compatibility a application artifacts nemusí obnoviť business službu.

## 4. Backup vault

Backup vault je logický container pre recovery points.

Vault boundary zahŕňa:

- access policy,
- KMS encryption,
- retention a Vault Lock,
- notifications,
- cross-account copy destination,
- reporting a audit scope.

Jeden default vault pre všetky workloady typicky neposkytuje dostatočné oddelenie production, non-production, compliance a recovery isolation požiadaviek.

## 5. Backup plan

Backup plan je policy expression určujúci, kedy a ako sa resources zálohujú.

Rule môže definovať:

- schedule,
- start window,
- completion window,
- target vault,
- lifecycle,
- cold-storage transition pri podporovaných typoch,
- retention,
- copy actions,
- continuous backup pri podporovaných resources,
- recovery-point tags.

Start window určuje, ako dlho sa job môže začať. Completion window určuje, ako dlho môže bežať po spustení. Príliš úzke okná môžu vytvárať `EXPIRED` alebo timeout failures pri throttlingu, veľkom resource-e alebo service incidente.

## 6. Resource assignment

Resources možno priradiť:

- explicitne podľa ARN/resource identity,
- tag-based selection,
- organization backup policy,
- service alebo resource-type selection podľa podporovaných capabilities.

Tag-based selection škáluje, ale iba ak tagging contract obsahuje:

- ownera,
- data classification,
- environment,
- backup tier,
- RPO/RTO class,
- retention class,
- recovery Region/account.

Chýbajúci alebo chybný tag sa môže zmeniť na neviditeľný protection gap.

## 7. Backup policy tiers

Príklad:

| Tier | Workload | Frekvencia | Retention | Isolation | Restore test |
|---|---|---|---|---|---|
| Gold | kritický state | hourly/PITR + daily | dlhá | cross-account + locked vault | mesačne |
| Silver | dôležitý workload | daily | stredná | cross-account | štvrťročne |
| Bronze | obnoviteľný workload | weekly | krátka | lokálny vault | polročne |

Konkrétne hodnoty musia vychádzať z BIA a service capability, nie z univerzálneho template-u.

## 8. Snapshot a continuous backup

### Snapshot backup

Zachytí resource v konkrétnom čase. Je vhodný pre:

- periodické retention body,
- dlhodobé uchovanie,
- cross-account alebo cross-Region copy podľa podpory,
- immutable vault model,
- recovery pred významnou zmenou.

### Continuous backup a PITR

Pri podporovaných services udržiava full backup a zmenový log, z ktorého možno obnoviť konkrétny čas v retention window.

Výhody:

- jemnejší RPO,
- návrat pred corruption/deletion event,
- menšia strata dát než pri periodickom snapshote.

Obmedzenia:

- service-specific maximum retention,
- iba jeden continuous recovery point na resource,
- nie všetky copy alebo immutability semantics sú rovnaké ako pri snapshots,
- restore time a latest restorable time sa líšia podľa služby.

Pre kritický state je často vhodná kombinácia continuous backup a periodických snapshotov.

## 9. On-demand backup

On-demand backup sa spustí mimo schedule-u.

Použitie:

- pre-change recovery point,
- emergency preservation,
- testovanie backup pathu,
- migration checkpoint.

Nie je náhradou policy-driven ochrany. Ručný proces sa môže vynechať a nepreukazuje dlhodobú compliance.

## 10. Lifecycle a retention

Lifecycle určuje:

- kedy recovery point prejde do cold storage pri podporovanom resource type,
- kedy sa odstráni,
- ako dlho zostáva dostupný pre restore.

Retention musí pokrývať:

- detekčný čas incidentu,
- právne/compliance požiadavky,
- seasonal alebo month-end recovery,
- restore rehearsal,
- copy lag a failed copy retries.

Príliš krátka retention môže odstrániť posledný čistý point ešte pred odhalením corruption. Príliš dlhá retention bez classification zvyšuje cost a data-governance riziko.

## 11. Cross-Region copy

Cross-Region copy chráni pred širším regional failure a podporuje regionálny DR.

Over:

- resource-type support,
- destination vault a KMS policy,
- destination retention,
- copy completion time,
- data residency,
- recovery capacity a dependencies v destination Region,
- restore permissions.

Cross-Region copy bez pripraveného networku, identity, DNS, application artifacts a capacity nie je úplný DR.

## 12. Cross-account copy

Cross-account copy oddeľuje recovery points od workload accountu.

Výhody:

- menší blast radius credential compromise,
- oddelené backup administration,
- central governance,
- jednoduchší incident containment.

Potrebuje:

- AWS Organizations a trusted access podľa modelu,
- source/destination vault policies,
- KMS permissions,
- explicitného restore operatora,
- testovaný recovery access pri izolovanom incidente.

Ak attacker ovláda production account, nemal by vedieť jednoducho zmazať alebo skrátiť retention všetkých recovery points.

## 13. Vault Lock

AWS Backup Vault Lock chráni recovery points pred predčasným zmazaním alebo zmenou lifecycle-u podľa konfigurácie.

Modely zahŕňajú governance a compliance behavior podľa zvoleného režimu.

Compliance mode po skončení grace period vytvára veľmi silnú immutability boundary. Pred aktiváciou over:

- minimálnu a maximálnu retention,
- právne požiadavky,
- test vault,
- IAM a break-glass proces,
- account closure implications,
- cost pri nesprávne dlhej retention.

Vault Lock nie je náhrada access isolation, KMS governance ani restore testovania.

## 14. Logically air-gapped vault

Logically air-gapped vault poskytuje dodatočnú logical isolation a používa Vault Lock compliance mode. Podporuje vybrané cross-account sharing a restore modely.

Použitie:

- ransomware resilience,
- recovery oddelené od production organization blast radiusu,
- immutable critical backups,
- controlled external recovery account.

Over service/resource support, KMS model, RAM sharing, temporary restore-access workflow a Multi-party approval capabilities podľa aktuálnej dokumentácie.

„Air-gapped“ neznamená, že nie je potrebné chrániť identity, recovery workflow, keys a validation environment.

## 15. Encryption

Recovery point môže závisieť od:

- source resource encryption,
- backup vault KMS key,
- destination vault KMS key,
- service-specific snapshot-copy behavior,
- cross-account key policy.

Pri KMS incidentoch over:

- key state,
- key policy,
- grants,
- source a destination account principals,
- service-linked role,
- encryption context,
- pending deletion alebo disabled key.

Backup s nedostupným KMS key nemusí byť obnoviteľný.

## 16. IAM a service roles

AWS Backup potrebuje role na:

- vytvorenie backupu,
- copy,
- restore,
- resource discovery,
- tagging,
- service-specific operations.

Least privilege musí stále pokryť dependent actions. `AccessDenied` môže vzniknúť v AWS Backup, source service, destination service, KMS alebo organization policy vrstve.

Restore role je citlivá, pretože môže vytvoriť nové compute, database alebo storage resources s prístupom k produkčným dátam.

## 17. Backup jobs

Sleduj:

- `CREATED`, `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `ABORTED` alebo `EXPIRED` status podľa job type-u,
- status message,
- resource ARN,
- start/completion time,
- bytes/resources processed,
- recovery point ARN,
- IAM role,
- vault,
- lifecycle.

Bežné failures:

- resource nie je v podporovanom stave,
- missing permission,
- KMS denial,
- start window expired,
- service quota alebo throttling,
- unsupported configuration,
- conflict s native backup/PITR configuration,
- copy destination policy.

## 18. Copy jobs

Copy job má vlastný lifecycle a môže zlyhať aj po úspešnom source backupe.

Monitoruj:

- source a destination vault,
- source/destination Region/account,
- encryption,
- copy completion time,
- destination recovery point,
- expiration,
- retry a failure message.

Backup compliance nesmie označiť workload za chránený iba podľa source recovery pointu, ak recovery strategy vyžaduje dokončenú isolated copy.

## 19. Restore job

Restore vytvára nový alebo obnovený resource podľa service-specific metadata.

Restore workflow:

```text
vyber správny clean recovery point
→ vytvor izolovaný recovery target
→ aplikuj network/IAM/encryption metadata
→ obnov dependencies
→ vykonaj application validation
→ rozhodni o promotion/cutover
→ zachovaj evidence
```

Neobnovuj nekontrolovane priamo cez production resource, ak restore vytvára nový target a potrebuje validation.

## 20. Restore testing

Restore testing automatizuje pravidelné vytvorenie testovacieho restore targetu z vybraných recovery points.

Test má overiť viac než API status:

- resource vznikol,
- je decryptable a accessible,
- filesystem/database integrity,
- application schema,
- sample business queries,
- expected object/file count,
- RTO a recovery duration,
- isolation a cleanup.

Voliteľná validation musí byť automatizovaná alebo mať explicitného ownera. Po testovaní sa test resources odstránia podľa restore-testing lifecycle-u; cleanup treba monitorovať aj z cost pohľadu.

## 21. Application consistency

Crash-consistent backup nemusí byť application-consistent.

Pre stateful workload môže byť potrebné:

- flush buffers,
- filesystem freeze,
- database-native transaction consistency,
- pre/post scripts,
- coordinated multi-volume snapshot,
- quiesce application writes,
- zachovať schema a application version.

Pri distributed application treba definovať consistency boundary medzi viacerými stores. Nezávislé snapshots z rôznych časov môžu vytvoriť logicky nekompatibilný stav.

## 22. AWS Backup Audit Manager

Audit Manager pre AWS Backup pomáha hodnotiť controls ako:

- resources zahrnuté v backup plan-e,
- minimálna frekvencia a retention,
- encryption,
- Vault Lock,
- cross-account/cross-Region copies,
- posledný recovery point,
- restore time objectives,
- restore testing,
- logically air-gapped vault coverage.

Compliance report je evidence o konfigurácii a jobs. Nie je dôkazom úplnej application recovery bez validation.

## 23. Organizations a backup policies

AWS Organizations backup policies umožňujú centrally definovať backup plans pre účty a OUs.

Potrebné je rozlíšiť:

- policy inheritance a merge semantics,
- opt-in resources,
- tag selection,
- local account permissions,
- destination vaults,
- delegated administratora,
- exception lifecycle.

Central policy bez resource ownership a tagging quality môže vytvoriť false sense of coverage.

## 24. Monitoring a events

Použi:

- AWS Backup job events,
- EventBridge,
- CloudWatch metrics/alarms podľa dostupnosti,
- CloudTrail API audit,
- Audit Manager reports,
- notifications,
- central dashboard.

Alertuj na:

- failed/expired backup,
- failed copy,
- missed recovery point age objective,
- restore test failure,
- Vault Lock/policy change,
- KMS key state change,
- abnormal deletion attempt,
- recovery target cleanup failure.

## 25. RPO a RTO measurement

### RPO evidence

- timestamp posledného validného clean recovery pointu,
- continuous-backup latest restorable time,
- copy lag,
- replication/capture delay,
- application transaction reconciliation.

### RTO evidence

- recovery-point discovery,
- approval a access,
- restore job duration,
- storage initialization,
- dependency recreation,
- data validation,
- DNS/traffic cutover,
- business acceptance.

AWS Backup job duration je iba časť reálneho RTO.

## 26. Ransomware recovery model

Silnejší model kombinuje:

- least-privilege workload account,
- central backup administration,
- cross-account isolation,
- immutable retention,
- separate KMS governance,
- logically air-gapped vault podľa požiadaviek,
- anomaly/detection controls,
- tested clean-room recovery,
- credential reset a forensic preservation.

Restore do kompromitovaného prostredia bez containmentu môže okamžite znovu poškodiť obnovené dáta.

## 27. Cost model

Cost drivers môžu zahŕňať:

- backup storage,
- warm/cold tier,
- restore,
- cross-Region/cross-account transfer a copy,
- service-specific snapshot cost,
- restore-test resources,
- retention a duplicate protection,
- logically air-gapped vault capabilities.

Optimalizácia nesmie odstrániť jediný clean recovery point alebo porušiť RPO/RTO/compliance contract.

## 28. SOA-C03 mapovanie

- **Domain 1** — backup/copy/restore job monitoring, Audit Manager, EventBridge remediation a performance evidence,
- **Domain 2** — RPO/RTO, cross-account/Region copies, Vault Lock, restore testing a DR,
- **Domain 3** — backup plans, Organizations policies, tag assignment a automated restore workflows,
- **Domain 4** — KMS, vault policies, immutability, ransomware defense a compliance,
- **Domain 5** — recovery Region/account connectivity, private endpoints a application cutover dependencies.

Praktické drilly:

- resource chýba v tag-based selection,
- backup job `EXPIRED`,
- cross-account copy KMS denial,
- Vault Lock retention konflikt,
- restore role nemá dependent permission,
- restored database nie je application-compatible,
- posledný isolated recovery point je príliš starý,
- restore test prejde infra statusom, ale zlyhá business validation.

## 29. Troubleshooting postup

```text
správny account/Region/resource?
→ backup-plan assignment a effective policy?
→ resource/service support a state?
→ IAM/SCP/KMS/vault policy?
→ job status a message?
→ source recovery point?
→ copy destination a retention?
→ restore metadata a target dependencies?
→ application validation?
```

Zachovaj job ID, recovery-point ARN, resource ARN, vault, KMS key, timestamps, policy version a CloudTrail events.

## 30. Anti-patterny

### Backup job `COMPLETED` ako jediný success criterion

Neoveruje restore ani application correctness.

### Backup v rovnakom account-e bez isolation

Credential compromise môže zasiahnuť production aj recovery points.

### Replication považovaná za backup

Prenáša aj chyby a deletions.

### Vault Lock bez rehearsal

Nesprávna retention môže vytvoriť dlhodobý cost alebo compliance problém.

### Cross-Region copy bez recovery capacity

Dáta existujú, ale workload sa nedá spustiť.

### Restore test bez validation

Overí vytvorenie resource-u, nie business obnoviteľnosť.

### Backup všetkého rovnakým tierom

Ignoruje business criticality, RPO/RTO a cost.

## 31. Kontrolné otázky

1. Aký je rozdiel medzi backup, replication a high availability?
2. Čo definuje backup plan a resource assignment?
3. Kedy použiť snapshot a kedy continuous backup?
4. Prečo cross-account copy znižuje blast radius?
5. Čo Vault Lock robí a čo nerobí?
6. Čo je logically air-gapped vault?
7. Prečo je restore testing dôležitejší než iba backup success?
8. Ako zmeriaš reálne RPO a RTO?
9. Ktoré vrstvy preveríš pri failed copy alebo restore?
10. Prečo application consistency nie je automatická?

## Glossary impact

Relevantné pojmy: AWS Backup, backup plan, backup rule, resource assignment, recovery point, backup vault, continuous backup, point-in-time recovery, backup lifecycle, cross-Region copy, cross-account copy, AWS Backup Vault Lock, logically air-gapped vault, restore job, restore testing, AWS Backup Audit Manager, backup policy, application-consistent backup, clean-room recovery a recovery-point age.

## Oficiálna dokumentácia

- [AWS Backup Developer Guide](https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html)
- [Backup plans](https://docs.aws.amazon.com/aws-backup/latest/devguide/about-backup-plans.html)
- [Continuous backups and point-in-time recovery](https://docs.aws.amazon.com/aws-backup/latest/devguide/point-in-time-recovery.html)
- [AWS Backup Vault Lock](https://docs.aws.amazon.com/aws-backup/latest/devguide/vault-lock.html)
- [Logically air-gapped vault](https://docs.aws.amazon.com/aws-backup/latest/devguide/logicallyairgappedvault.html)
- [Restore testing](https://docs.aws.amazon.com/aws-backup/latest/devguide/restore-testing.html)
- [AWS Backup Audit Manager](https://docs.aws.amazon.com/aws-backup/latest/devguide/aws-backup-audit-manager.html)
