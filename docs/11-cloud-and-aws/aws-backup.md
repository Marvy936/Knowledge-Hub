# AWS Backup

AWS Backup centralizuje policy-driven backup, copy, retention, restore testing a audit podporovaných AWS resources. Služba však nevytvára business recovery iba tým, že job skončí stavom `COMPLETED`.

Obnoviteľnosť vzniká až cez celý lifecycle:

```text
business recovery objective
→ exact protected data a dependency subject
→ consistency a clean-point boundary
→ effective backup policy a assignment
→ capture a recovery-point generation
→ isolated copy, key a retention lineage
→ clean recovery-candidate selection
→ restore generation v controlled environment
→ dependency a application realization
→ data reconciliation a business validation
→ promotion, fencing a cutover
→ evidence, cleanup a ďalší rehearsal
```

Backup job dokazuje, že service-specific capture vytvoril recovery point. Copy job dokazuje, že vznikla ďalšia recovery-point generation. Restore job dokazuje, že AWS vytvoril resource podľa restore metadata. Ani jeden z týchto stavov sám nepreukazuje, že vybraný point je čistý, distribuovaný state je konzistentný, aplikácia je kompatibilná alebo business outcome je správny.

## 1. Exact recovery subject

Atlas Payments používa recovery subject `REC-PAY-42`:

```text
workload = CAP-PAY-42
production account = 100000000042
recovery account = 200000000042
primary Region = eu-central-1
recovery Region = eu-west-1

business service = Atlas Payments
critical outcome = authorize, settle and ledger payment exactly once
business RTO = 2 hours
ledger RPO = 15 minutes
receipt-object RPO = 1 hour, reconstructable from ledger/provider evidence

protected data generation = DATA-PAY-215
RDS database subject = DB-PAY-42 / schema SCHEMA-215
S3 receipt manifest = RECEIPTS-MANIFEST-81
EFS reconciliation workspace = EFS-REC-19
application artifact = payments-api 7.18.0 digest sha256:pay718
IaC/network generation = INFRA-PAY-64
secret/key generation = SEC-PAY-42 / KMS-PAY-17

backup plan generation = BP-GOLD-8
assignment generation = ASSIGN-GOLD-12
selection = BackupTier=Gold AND Environment=prod
RDS protection = continuous/PITR + daily recovery point
S3/EFS protection = scheduled recovery points podľa service contractu
source vault = vault-pay-prod-8
isolated vault = vault-pay-recovery-5
vault-lock generation = LOCK-7
copy rule generation = COPY-EUC1-EUW1-9
restore-testing plan = RT-PAY-6

recovery manifest generation = RM-PAY-27
selected clean boundary = 2026-07-28T01:40:00Z
restore role = arn:aws:iam::200000000042:role/AtlasRecoveryOperator
recovery VPC generation = VPC-REC-11

forbidden outcomes =
  latest recovery point is selected without clean-point evidence
  source backup is accepted when required isolated copy failed
  restore is promoted because AWS resource status is Available
  database, object and filesystem generations are logically inconsistent
  recovery uses unavailable or soon-to-be-deleted KMS keys
  restored writers coexist with unfenced corrupted production writers
  test resources with production data remain exposed after rehearsal
```

Recovery evidence musí obsahovať source resource ARN, backup-plan/assignment generation, job ID, recovery-point ARN, capture and completion timestamps, copy lineage, vault/account/Region, KMS key ARN, retention/lock state, selected clean boundary, restore metadata, restored resource identity, application artifact/schema generation, validation results, reconciliation interval, cutover authority a cleanup result.

## 2. Protection, recovery point a recoverability sú rozdielne stavy

### Protected resource

Resource je policy-covered iba vtedy, keď effective plan a assignment naozaj vyberajú exact resource generation. Deklarovaný tag štandard nestačí; musí existovať evidence, že resource mal matching tags v čase selection a job ho spracoval.

### Recovery point

Recovery point reprezentuje service-specific captured state v určitom čase. Obsahuje lineage, vault, encryption, lifecycle a restore metadata, ale nemusí obsahovať external dependencies aplikácie.

### Isolated recovery point

Kópia v inom account-e, Regione alebo locked/air-gapped vault-e znižuje určitý blast radius. Isolation je vlastnosť konkrétnej completed copy generation, nie source backup intentu.

### Recoverable business generation

Recoverable generation je overená kombinácia:

```text
clean data points
+ compatible schema a application artifact
+ available keys a secrets
+ identity/network/DNS dependencies
+ restore capacity
+ tested runbook
+ reconciliation evidence
```

Najnovší recovery point môže byť poškodený. Najstarší čistý point môže porušiť RPO. Výber je preto incident decision viazaný na timeline corruption a business reconciliation, nie automatické `max(timestamp)`.

## 3. Backup nie je HA ani replication

High availability udržiava service počas host, AZ alebo component failures. Replication vytvára ďalšiu current-ish copy state-u. Backup zachováva historické recovery generations.

```text
HA:
current state → redundant execution/failover

replication:
current change → replica apply

backup:
versionovaný capture → retention → later restore
```

Replication môže rýchlo preniesť deletion, ransomware encryption, bad migration aj logical corruption. Multi-AZ databáza môže byť vysoko dostupná a zároveň dokonale replikovať chybný `DELETE`.

Backup zase nezabezpečuje low-downtime failover. Restore môže trvať dlhšie, vytvárať nový resource a vyžadovať DNS, identity, capacity a application validation.

## 4. Effective protection vzniká z policy a inventory

Backup plan definuje schedule, start/completion windows, target vault, lifecycle, retention, copy actions a continuous backup podľa resource supportu. Assignment definuje, ktoré resources plan reálne chráni.

Effective selection chain:

```text
organization/account policy
→ inherited a local plan generation
→ resource-type opt-in/support
→ assignment expression
→ resource identity a tags v selection čase
→ service role a KMS authorization
→ scheduled job creation
→ recovery-point result
```

### Tag-based selection failure boundary

Tagy škálujú governance, ale sú mutable input. Resource môže byť vytvorený bez `BackupTier=Gold`, tag môže automation odstrániť alebo attacker zmeniť ešte pred ďalším schedule-om.

Coverage evidence preto porovnáva:

- authoritative critical-resource inventory;
- expected tier a RPO/RTO class;
- effective assignment;
- last successful source recovery point;
- required isolated copy;
- restore-test freshness;
- explicit exception s ownerom a expiry.

`BackupTier=Gold` na resource-e nie je recovery point. Recovery point v source vault-e nie je completed cross-account copy. Completed copy nie je tested restore.

## 5. Schedule a job windows sú capacity contract

Schedule určuje, kedy je backup eligible. Start window určuje, ako dlho sa job môže začať; completion window obmedzuje execution po štarte.

Príliš úzke windows môžu pri throttlingu, veľkom resource-e alebo service incidente vytvoriť `EXPIRED` job. Zväčšenie okna môže odstrániť symptom, ale treba overiť, či completion stále spĺňa RPO a copy deadline.

Job status sa interpretuje spolu s:

- resource ARN a generation;
- scheduled a actual start;
- completion time;
- service status message;
- recovery-point ARN;
- bytes/items processed podľa typu;
- vault a KMS key;
- plan/rule generation.

## 6. Snapshot, continuous backup a application consistency

### Snapshot-style recovery point

Capture vytvára point-in-time resource generation. Je vhodný na periodickú retention, pre-change checkpoint, cross-account/Region copy a locked history.

### Continuous backup a PITR

Pri podporovaných services zachováva full backup a change history, z ktorých možno vybrať restore time v retention window. `LatestRestorableTime` je service capture boundary, nie automaticky posledná business-consistent transaction naprieč všetkými stores.

### Crash consistency a application consistency

Infrastructure capture môže byť crash-consistent. Stateful aplikácia môže vyžadovať:

```text
write quiesce alebo transaction boundary
→ buffer flush a filesystem/database checkpoint
→ coordinated multi-volume/store marker
→ capture timestamps a log positions
→ application resume
→ manifest publication
```

Pri RDS service-native backup engine zabezpečuje vlastný database recovery contract. Pri EC2/EBS alebo distributed file/application modeli môže byť potrebný Systems Manager pre/post script, Volume Shadow Copy, filesystem freeze alebo application checkpoint podľa supportu.

Nezávislé recovery points z rôznych časov môžu byť technicky validné a logicky nekompatibilné.

## 7. Recovery manifest spája service-specific points

Atlas recovery manifest `RM-PAY-27` obsahuje:

```text
clean boundary timestamp
RDS PITR timestamp a transaction/log marker
S3 object keys, version IDs a checksums
EFS recovery-point ARN a application checkpoint
application artifact digest a schema compatibility
secret versions a KMS keys
IaC/network/DNS generation
provider reconciliation cursor
expected allowed a forbidden business outcomes
```

Manifest nespolieha iba na resource names. Viaže exact versions a restore parameters, aby recovery tím nevytvoril náhodnú kombináciu „najnovších“ bodov.

## 8. Vault, encryption a access boundary

Backup vault je container recovery points s access policy, KMS modelom, lifecycle, lock, notifications a audit scope. Vault policy a IAM spolu určujú, kto môže backup/copy/restore/delete operations vykonať.

Encryption lineage môže zahŕňať:

```text
source resource key
→ source recovery point/vault encryption
→ copy operation
→ destination vault key
→ restore role a target resource key
```

Service-specific rules sa líšia. Recovery manifest preto uchováva exact key ARN, account, Region, key state a policy generation pre source, copy aj restore target.

Backup s KMS key `PendingDeletion` alebo key policy bez recovery principalu nie je bezpečný recovery asset, hoci jeho retention je správna.

## 9. Cross-account a cross-Region copy

Cross-account copy oddeľuje recovery points od workload-account credentials a administrators. Cross-Region copy znižuje regional blast radius. Obe transition majú vlastné jobs a môžu zlyhať po úspešnom source backupe.

Required copy acceptance:

```text
source point completed
→ copy rule selected exact point
→ destination vault/key authorization
→ copy job completed
→ destination recovery-point ARN exists
→ intended retention/lock applied
→ restore operator can access podľa break-glass modelu
```

Ak strategy vyžaduje isolated copy, source `COMPLETED` nesmie uzavrieť compliance verdict.

Destination data bez recovery VPC, quotas, artifacts, identity, DNS a target-service capacity nie je regional DR.

## 10. Vault Lock a logically air-gapped vault

Vault Lock presadzuje retention a deletion constraints podľa governance alebo compliance configuration. Compliance mode po grace period vytvára silnú immutable boundary; nesprávna retention sa potom nedá jednoducho opraviť administrátorským overrideom.

Pred lockom over:

- min/max retention;
- legal hold a deletion requirements;
- test vault a sample restores;
- KMS key lifetime;
- account closure a cost implications;
- break-glass a restore ownership.

Logically air-gapped vault pridáva logical isolation a compliance-mode protection. Pri podporovaných workflows môže byť zdieľaný s recovery accountom cez controlled restore access. Multi-party approval môže vyžadovať, aby skupina dôveryhodných approvers schválila vytvorenie restore-access pathu.

```text
suspected compromise
→ requester opens bounded restore-access request
→ independent approvers validate incident a scope
→ temporary restore-access vault/path
→ recovery account restore
→ validation a evidence
→ access revocation
```

Presný resource support, primary-backup capability, sharing a Multi-party approval workflow treba overiť podľa aktuálnej AWS Backup dokumentácie. „Air-gapped“ neznamená bez identity, KMS, network alebo operational dependencies.

## 11. Restore authority a clean-room recovery

Restore role môže vytvárať databases, volumes, filesystems alebo compute s production data. Je to high-impact data-access capability.

Bezpečný restore používa:

- explicitný incident/rehearsal ID;
- approved recovery manifest;
- isolated recovery account/VPC;
- bounded restore role session;
- no default production routes;
- controlled analyst/application access;
- data masking podľa use case-u;
- cleanup a evidence retention.

Pri ransomware alebo credential compromise sa najprv obnovuje control nad identity, keys a loggingom. Restore priamo do stále kompromitovaného production accountu môže okamžite poškodiť čisté dáta.

## 12. Restore job nie je cutover

Restore job vytvorí service-specific target podľa metadata. Ďalší chain je samostatný:

```text
restore target exists
→ decrypt a storage initialization
→ network a identity attachment
→ schema/filesystem integrity
→ application compatibility
→ dependency realization
→ business queries a invariants
→ reconciliation
→ capacity/performance
→ promotion decision
→ old-writer fencing a traffic cutover
```

`Available` database alebo `completed` EBS restore nepreukazuje production latency. DNS cutover bez fencing môže vytvoriť dvoch writers. Application start bez provider reconciliation môže znovu odoslať external side effects.

## 13. Restore testing musí testovať recovery contract

AWS Backup restore testing môže periodicky vybrať recovery point a vytvoriť test target. Optional validation workflow a owner musia overiť viac než resource creation.

Atlas testuje:

1. exact recovery-point a manifest identity;
2. decrypt a mount/connect;
3. database/filesystem/object integrity;
4. schema a artifact compatibility;
5. business invariants a sample payment journey;
6. forbidden network/identity paths;
7. measured RTO stages;
8. cleanup a residual-resource scan.

Validation script, ktorý iba pingne endpoint, môže prehliadnuť prázdnu ledger tabuľku, stale schema, chýbajúci object manifest alebo broad public access.

## 14. Worked failure: najnovší isolated point je úspešný, ale nie čistý

### Incident timeline

```text
01:40  posledný preukázaný clean business checkpoint
01:42  kompromitovaná session začne mazať ledger rows a meniť outbox state
01:55  EFS scheduled recovery point
02:00  RDS daily point; continuous history pokračuje
02:05  S3 receipt recovery point
02:23  cross-account/cross-Region copies complete
02:35  anomaly a business reconciliation odhalia corruption
```

Backup dashboard ukazuje všetky jobs `COMPLETED`. On-call vyberie najnovšie isolated points: RDS 02:00, EFS 01:55 a S3 02:05. Restore jobs v recovery account-e uspejú.

### Symptom po application start-e

- niektoré receipt objects existujú bez matching ledger rows;
- outbox obsahuje records pre payments, ktoré provider už settled;
- reconciliation worker sa pokúša external settlement zopakovať;
- infrastructure healthchecks sú green;
- restore-test validation pôvodne kontrolovala iba connect a HTTP 200.

### Competing hypotheses

1. restore je incomplete alebo KMS decrypt poškodil dáta;
2. application artifact nie je kompatibilný so schema;
3. S3 alebo EFS copy zaostala;
4. recovery points pochádzajú z nekompatibilných časov;
5. všetky vybrané points už obsahujú attacker corruption;
6. provider state je novší než local restored ledger.

### Discriminating evidence

- checksums a service integrity sú validné, takže nejde o transport corruption;
- RDS audit a CloudTrail timeline dokazujú malicious changes od 01:42;
- selected RDS point 02:00 preto nie je clean;
- S3 object versions zachytávajú receipts vytvorené po deleted ledger rows;
- provider transaction export dokazuje settled operations, ktoré restored outbox považuje za pending;
- application artifact a schema sú kompatibilné, ale distributed business invariant je porušený.

Root cause nie je AWS Backup job failure. Recovery tím použil „latest successful“ ako selection oracle a nemal recovery manifest viazaný na clean business checkpoint.

### Containment

1. fence-ni corrupted production writers a revoke compromised sessions;
2. zastav settlement consumers a external side effects;
3. zachovaj CloudTrail, DB audit, object versions a provider evidence;
4. nepromuj aktuálny restore target;
5. označ recovery points po 01:42 ako technicky validné, ale business-dirty;
6. vytvor approved manifest pre clean boundary 01:40.

### Authoritative recovery

```text
RDS PITR do 01:40
→ S3 exact version manifest najneskôr 01:40
→ compatible EFS/application checkpoint
→ artifact 7.18.0 + schema validation
→ provider export pre reconciliation window 01:40–02:35
→ insert/mark already-settled operations bez nového settlementu
→ rebuild receipts/outbox podľa authoritative ledger/provider state
→ invariant a duplicate checks
→ load/performance test
→ controlled cutover s old-writer fencing
```

### Acceptance verdict

Recovery je uzavreté až keď:

- selected points sú preukázateľne clean a manifest-consistent;
- every restored payment má validný ledger/provider/receipt relationship;
- žiadny already-settled payment sa znovu neodošle;
- approved application journey funguje v RTO;
- forbidden production/public/old-writer paths zlyhávajú;
- KMS, secret, IAM a network dependencies sú recovery-owned;
- cleanup odstráni test targets bez odstránenia evidence;
- restore-testing validation je rozšírená o business invariants.

## 15. RPO a RTO sú measured outcomes

### Realized RPO

RPO sa meria od poslednej validnej clean recoverable generation, nie od najnovšieho job timestampu.

```text
incident/corruption boundary
- selected clean point
+ capture/copy gaps
+ unreconciled external side effects
= realized data-loss exposure
```

### Realized RTO

RTO zahŕňa:

```text
detection a decision
+ access/approval
+ point discovery
+ restore jobs
+ storage initialization
+ dependencies/IaC
+ application validation
+ reconciliation
+ cutover
+ business acceptance
```

AWS restore duration je iba jedna zložka.

## 16. Monitoring, compliance a audit

Monitoruj oddelene:

- source backup jobs;
- required copy jobs;
- recovery-point age;
- effective assignment coverage;
- Vault Lock a policy changes;
- KMS state/policy changes;
- restore-testing schedule, restore a validation status;
- recovery target cleanup;
- organization policy exceptions.

AWS Backup Audit Manager môže hodnotiť configuration a job controls. Report je evidence o coverage a policy, nie náhrada business restore validation.

CloudTrail musí umožniť vysvetliť, kto zmenil plan, assignment, vault policy, lock, copy rule, restore role alebo recovery point lifecycle.

## 17. Troubleshooting chain

### Resource nemá recovery point

```text
exact account/Region/resource ARN
→ service/resource support a opt-in
→ effective plan/assignment
→ tags v selection čase
→ schedule/window
→ role/SCP/KMS
→ job event/status
```

### Source backup uspel, isolated copy chýba

Over copy rule generation, source-point eligibility, destination vault policy, KMS keys, Organizations trust, destination Region/account a copy-job status.

### Restore zlyhá

Over recovery-point type, restore metadata, restore role, service-linked role, KMS keys, quotas, network/subnet parameters a target-name conflicts.

### Restore je green, application zlyhá

Over artifact/schema generation, storage initialization, secret/KMS, network, external dependencies, distributed consistency, business invariants a selected clean boundary.

## 18. Cost a retention

Cost drivers zahŕňajú warm/cold backup storage, retained versions, cross-Region copy/transfer, restore, test resources, duplicate native protection a logically air-gapped capabilities.

Retention decision musí vyvažovať detection latency, legal requirement, clean-history depth, restore cadence a cost. Krátka retention môže odstrániť posledný čistý point. Neprimerane dlhá immutable retention môže vytvoriť vysoký cost a data-governance problém, ktorý sa po compliance locku nedá ľahko opraviť.

## 19. SOA-C03 mapovanie

- **Domain 1** — backup/copy/restore monitoring, events, reports a failure diagnosis.
- **Domain 2** — RPO/RTO, isolation, Vault Lock, restore testing a DR.
- **Domain 3** — plans, assignments, Organizations policies a automated recovery workflows.
- **Domain 4** — KMS, vault policies, ransomware resilience, restore-role security a audit.
- **Domain 5** — recovery account/Region network, DNS a dependency cutover.

## 20. Anti-patterny

### `COMPLETED` ako recoverability verdict

Dokazuje service job, nie clean business restore.

### Latest recovery point ako automatická voľba

Latest môže obsahovať logical corruption alebo attacker changes.

### Independent points bez manifestu

Technicky validné stores môžu tvoriť nekompatibilný distributed state.

### Source backup bez required isolated-copy evidence

Workload ostáva v rovnakom credential/administrative blast radius-e.

### Vault Lock bez rehearsal

Immutable chybná retention vytvorí dlhodobý cost alebo legal problém.

### Restore priamo do kompromitovaného production accountu

Čisté dáta sa môžu okamžite znovu poškodiť.

### Restore testing iba cez resource status

Neoveruje schema, invariants, dependencies, RTO ani forbidden paths.

## 21. Kontrolné otázky

1. Aký je rozdiel medzi protected resource, recovery point a recoverable business generation?
2. Prečo replication nie je backup?
3. Ako vzniká effective tag-based backup coverage?
4. Čo musí obsahovať recovery manifest?
5. Prečo latest successful point nemusí byť clean?
6. Čo dokazujú cross-account a cross-Region copies?
7. Čo Vault Lock a logically air-gapped vault neriešia?
8. Ako sa restore job líši od recovery cutoveru?
9. Ako zmeriaš realized RPO a RTO?
10. Aký acceptance verdict potrebuje ransomware recovery?

## Glossary impact

Relevantné pojmy: recovery subject, protected-resource generation, effective backup coverage, recovery-point generation, isolated-copy acceptance, clean recovery candidate, business-dirty recovery point, recovery manifest, distributed recovery consistency, restore generation, restore authority, recovery fencing, realized RPO, realized RTO, restore-validation contract, logically air-gapped restore access, multi-party recovery approval a recovery acceptance verdict.

## Oficiálna dokumentácia

- [AWS Backup Developer Guide](https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html)
- [Backup plans](https://docs.aws.amazon.com/aws-backup/latest/devguide/about-backup-plans.html)
- [Continuous backups and point-in-time recovery](https://docs.aws.amazon.com/aws-backup/latest/devguide/point-in-time-recovery.html)
- [AWS Backup Vault Lock](https://docs.aws.amazon.com/aws-backup/latest/devguide/vault-lock.html)
- [Logically air-gapped vault](https://docs.aws.amazon.com/aws-backup/latest/devguide/logicallyairgappedvault.html)
- [Multi-party approval](https://docs.aws.amazon.com/aws-backup/latest/devguide/multipartyapproval.html)
- [Restore testing](https://docs.aws.amazon.com/aws-backup/latest/devguide/restore-testing.html)
- [Restore testing validation](https://docs.aws.amazon.com/aws-backup/latest/devguide/restore-testing-validation.html)
- [AWS Backup Audit Manager](https://docs.aws.amazon.com/aws-backup/latest/devguide/aws-backup-audit-manager.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: KMS a Secrets Manager](kms-secrets-manager.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Well-Architected Framework →](well-architected-framework.md)
<!-- KNOWLEDGE-NAVIGATION:END -->