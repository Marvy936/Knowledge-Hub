# AWS Backup

AWS Backup centralizuje policy-driven backup, copy, retention, restore testing a audit podporovaných AWS resources. Stav `COMPLETED` však nie je business recovery. Backup job preukazuje, že service-specific capture vytvoril recovery point. Copy job preukazuje vznik ďalšej recovery-point generation. Restore job preukazuje vytvorenie resource-u podľa restore metadata. Až application a business validation rozhodnú, či je point použiteľný.

```text
business recovery objective
→ exact protected data and dependency subject
→ consistency and clean-point boundary
→ effective backup policy and assignment
→ recovery-point generation
→ isolated copy and retention lineage
→ clean recovery-candidate selection
→ restore in controlled environment
→ dependency and application realization
→ reconciliation and business validation
→ promotion or cleanup
```

## 1. Exact recovery subject

Atlas Payments používa subject `REC-PAY-42`. Production account je `100000000042`, recovery account `200000000042`, primary Region `eu-central-1` a recovery Region `eu-west-1`. Business RTO je dve hodiny, ledger RPO pätnásť minút a receipt-object RPO jedna hodina, pretože receipts možno rekonštruovať z ledger/provider evidence.

Protected generation `DATA-PAY-215` zahŕňa RDS database `DB-PAY-42/SCHEMA-215`, S3 manifest `RECEIPTS-MANIFEST-81`, EFS workspace `EFS-REC-19`, application artifact `payments-api 7.18.0`, infrastructure generation `INFRA-PAY-64` a secret/key generations `SEC-PAY-42/KMS-PAY-17`.

Backup plan je `BP-GOLD-8`, assignment `ASSIGN-GOLD-12`, source vault `vault-pay-prod-8`, isolated vault `vault-pay-recovery-5`, Vault Lock `LOCK-7`, copy rule `COPY-EUC1-EUW1-9` a restore-testing plan `RT-PAY-6`. Recovery manifest `RM-PAY-27` vyberá clean boundary `2026-07-28T01:40:00Z`.

Forbidden outcomes sú výber latest pointu bez clean-point evidence, source backup akceptovaný napriek failed isolated copy, restore promoted iba podľa resource `Available`, inconsistent database/object/filesystem generations a recovery writer bez fencing starej authority.

## 2. Protected, backed up a recoverable nie sú synonymá

Resource je **policy-covered**, keď effective plan a assignment vyberajú jeho exact ARN/generation. Je **backed up**, keď existuje completed recovery point. Je **isolated**, keď required cross-account/Region copy prešla a má správny vault/key/retention contract. Je **recoverable**, až keď restore experiment preukáže dependencies, application compatibility, data invariants a business outcome.

```text
resource tag matches plan
≠ scheduled job exists
≠ recovery point completed
≠ isolated copy completed
≠ restore succeeds
≠ business capability is recovered
```

Najnovší recovery point môže obsahovať logical corruption. Najstarší čistý point môže porušiť RPO. Selection je incident decision viazaný na corruption timeline a reconciliation, nie automatické `max(timestamp)`.

## 3. Backup plan a assignment v Terraform-e

Terraform v tejto sekcii nereprezentuje samotnú obnoviteľnosť. Deklaruje iba plan, pravidlá a selection contract; až live assignment, úspešný recovery point, požadovaná kópia a vykonaný restore dokazujú, že konkrétny resource je skutočne chránený. Preto sa po aplikovaní konfigurácie vždy číta effective state a porovnáva s authoritative inventory.

```hcl
resource "aws_backup_vault" "payments" {
  name        = "vault-pay-prod-8"
  kms_key_arn = aws_kms_key.backup.arn

  tags = {
    Generation = "VAULT-PAY-8"
  }
}

resource "aws_backup_plan" "gold" {
  name = "BP-GOLD-8"

  rule {
    rule_name         = "daily-and-continuous"
    target_vault_name = aws_backup_vault.payments.name
    schedule          = "cron(0 1 * * ? *)"
    start_window      = 60
    completion_window = 360
    enable_continuous_backup = true

    lifecycle {
      cold_storage_after = 30
      delete_after       = 365
    }

    copy_action {
      destination_vault_arn = aws_backup_vault.recovery.arn

      lifecycle {
        delete_after = 2555
      }
    }
  }
}

resource "aws_backup_selection" "gold" {
  name         = "ASSIGN-GOLD-12"
  plan_id      = aws_backup_plan.gold.id
  iam_role_arn = aws_iam_role.backup.arn

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "BackupTier"
    value = "Gold"
  }

  selection_tag {
    type  = "STRINGEQUALS"
    key   = "Environment"
    value = "prod"
  }
}
```

Terraform preukazuje desired plan/selection. Nepreukazuje, že critical resource mal tags v selection čase, job vznikol, copy prešla alebo resource type podporuje continuous backup v danom contracte.

## 4. Effective coverage inventory

Najprv porovnaj authoritative resource inventory s planom a poslednými jobs:

```bash
aws backup list-protected-resources \
  --region eu-central-1 \
  --query 'Results[].{Arn:ResourceArn,Type:ResourceType,LastBackup:LastBackupTime}'

aws backup list-backup-jobs \
  --by-backup-vault-name vault-pay-prod-8 \
  --by-created-after 2026-07-29T00:00:00Z \
  --region eu-central-1 \
  --query 'BackupJobs[].{Job:BackupJobId,Resource:ResourceArn,State:State,Created:CreationDate,Completed:CompletionDate,RecoveryPoint:RecoveryPointArn,Message:StatusMessage}'
```

`list-protected-resources` je service inventory, nie complete proof proti business CMDB. Coverage report má obsahovať expected ARN, tier, RPO/RTO, last source point, required copy, restore-test freshness a exception owner/expiry.

Mutable tag je selection input. Ak attacker alebo automation odstráni `BackupTier=Gold` pred schedule-om, ďalší job resource nevyberie. High-value resources preto potrebujú config/policy guardrail a coverage alarm, nie iba naming convention.

## 5. Job windows a RPO

Schedule určuje eligibility. Start window určuje, ako dlho sa job môže začať; completion window obmedzuje execution po štarte. Pri throttlingu alebo large resource-e môže úzky interval skončiť `EXPIRED`.

Job status sa interpretuje s scheduled/actual startom, completion time, bytes/items processed, recovery-point ARN, vault, key a plan generation. Rozšírenie completion window môže odstrániť failure, ale treba znovu vypočítať effective RPO a copy deadline.

## 6. Crash consistency a application consistency

Infrastructure snapshot môže byť crash-consistent: podobný náhlej strate napájania. Application-consistent recovery point potrebuje engine/application checkpoint.

```text
quiesce or transaction boundary
→ flush filesystem/database buffers
→ record LSN/checkpoint and external offsets
→ capture resources
→ resume writes
→ publish recovery manifest
```

Service-native RDS backup má engine recovery contract. EC2/EBS alebo multi-volume application môže potrebovať Systems Manager pre/post scripts, filesystem freeze alebo database checkpoint. Samostatne validné points z rozdielnych časov môžu byť logicky nekompatibilné.

## 7. Recovery manifest

Recovery manifest spája service-specific recovery points do jednej business generation. Bez neho môže tím obnoviť technicky platnú databázu, objekty a filesystem z navzájom odlišných časov, takže application síce naštartuje, ale ledger, queue a external provider už nereprezentujú jeden konzistentný stav.

`RM-PAY-27` viaže service-specific points:

```yaml
manifest: RM-PAY-27
cleanBoundary: "2026-07-28T01:40:00Z"
database:
  recoveryPointArn: arn:aws:backup:eu-west-1:200000000042:recovery-point:db-pay-0140
  pitrTimestamp: "2026-07-28T01:40:00Z"
  schemaGeneration: SCHEMA-215
objects:
  manifestVersion: RECEIPTS-MANIFEST-81
  requiredVersions:
    - key: receipts/2026/07/28/P-884.json
      versionId: VER-P884-7
      sha256: "..."
filesystem:
  recoveryPointArn: arn:aws:backup:eu-west-1:200000000042:recovery-point:efs-rec-0140
  checkpoint: EFS-REC-19
application:
  imageDigest: sha256:pay718
  infrastructureGeneration: INFRA-PAY-64
identity:
  secretGeneration: SEC-PAY-42
  kmsKeyArn: arn:aws:kms:eu-west-1:200000000042:key/key-recovery-17
external:
  providerReconciliationCursor: PSP-0140
```

Manifest zabraňuje náhodnej kombinácii „najnovších“ points bez spoločného logical momentu.

## 8. Vault, KMS a isolation

Backup vault je policy, encryption, retention a access boundary. Cross-account copy oddeľuje recovery point od workload-account credentials. Cross-Region copy znižuje regional blast radius. Obe transitions majú samostatný job.

```bash
aws backup list-copy-jobs \
  --by-destination-vault-arn arn:aws:backup:eu-west-1:200000000042:backup-vault:vault-pay-recovery-5 \
  --by-created-after 2026-07-28T00:00:00Z \
  --region eu-west-1 \
  --query 'CopyJobs[].{Job:CopyJobId,State:State,Source:SourceRecoveryPointArn,Destination:DestinationRecoveryPointArn,Message:StatusMessage}'
```

Source `COMPLETED` nesmie uzavrieť control, ak strategy vyžaduje isolated copy. Destination point s KMS key `PendingDeletion` tiež nie je bezpečný recovery asset.

Vault Lock presadzuje retention/deletion constraints. Compliance mode po grace period vytvára silnú immutable boundary; chybná retention sa potom nedá jednoducho skrátiť. Pred lockom sa testuje retention, legal requirements, KMS lifetime, restores a cost.

## 9. Logically air-gapped vault a approval

Logically air-gapped vault poskytuje compliance-mode protected recovery boundary a controlled restore sharing. Multi-party approval môže vyžadovať nezávislých approvers pred otvorením restore accessu.

```text
incident or rehearsal request
→ bounded restore-access request
→ independent approval
→ temporary restore access in recovery account
→ restore and validation
→ access revocation
```

„Air-gapped“ neznamená bez IAM, KMS alebo operational dependencies. Recovery identity musí existovať a byť testovaná mimo compromised production pathu.

## 10. Restore testing plan

Restore testing automatizuje periodický výber recovery pointov a restore jobs podľa planu. Selection môže používať resource type, tags a protected-resource scope. Test stále potrebuje validation script/function, ktorá rozhodne, či restored resource je použiteľný.

Ukážková CLI konfigurácia sa overuje aktuálnym AWS Backup API modelom:

```bash
aws backup list-restore-testing-plans --region eu-central-1
aws backup get-restore-testing-plan \
  --restore-testing-plan-name RT-PAY-6 \
  --region eu-central-1
aws backup list-restore-testing-selections \
  --restore-testing-plan-name RT-PAY-6 \
  --region eu-central-1
```

Plan existence nepreukazuje posledný successful restore ani business assertion.

## 11. Clean-room restore walkthrough

Restore role session vznikne v recovery account-e:

```bash
aws sts get-caller-identity --profile atlas-recovery
```

Vyber exact point:

```bash
aws backup list-recovery-points-by-backup-vault \
  --backup-vault-name vault-pay-recovery-5 \
  --by-resource-arn arn:aws:rds:eu-central-1:100000000042:cluster:db-pay-prod-17 \
  --region eu-west-1 \
  --query 'RecoveryPoints[].{Arn:RecoveryPointArn,Created:CreationDate,Status:Status,Kms:EncryptionKeyArn}'
```

Získaj restore metadata:

```bash
aws backup get-recovery-point-restore-metadata \
  --backup-vault-name vault-pay-recovery-5 \
  --recovery-point-arn "$RECOVERY_POINT_ARN" \
  --region eu-west-1 > restore-metadata.json
```

Spusti restore:

```bash
RESTORE_JOB_ID=$(aws backup start-restore-job \
  --recovery-point-arn "$RECOVERY_POINT_ARN" \
  --iam-role-arn arn:aws:iam::200000000042:role/AtlasRecoveryOperator \
  --metadata file://restore-metadata.json \
  --resource-type Aurora \
  --idempotency-token REC-PAY-42-20260730 \
  --region eu-west-1 \
  --query RestoreJobId --output text)
```

Exact `resource-type` a metadata sa prispôsobujú protected service. Stable idempotency token zabraňuje accidental duplicate restore requests.

Sleduj job:

```bash
aws backup describe-restore-job \
  --restore-job-id "$RESTORE_JOB_ID" \
  --region eu-west-1
```

`COMPLETED` znamená, že resource bol vytvorený. Nasleduje network, identity, schema, data and performance validation.

## 12. Application validation

```bash
psql "$RECOVERY_DATABASE_URL" -v ON_ERROR_STOP=1 <<'SQL'
select current_database(), current_user;
select version from schema_generation where component = 'payments';
select max(checkpoint_id) from ledger_checkpoint;
select count(*) from settlement where payment_id = 'P-884';
SQL
```

Potom deployni exact approved image do isolated VPC s production side effects disabled. Synthetic journey overí read, idempotent write, outbox a reconciliation. Forbidden test potvrdí, že old credential, public path a production provider endpoint nie sú dostupné.

RTO končí až po validated service, nie po restore resource creation. RPO sa meria porovnaním restored business checkpointu s incident boundary.

## 13. Worked incident: source backup green, isolated recovery incomplete

Atlas mal daily RDS recovery point v source vault-e a dashboard ukazoval `COMPLETED`. Po account compromise recovery tím zistil, že cross-account copy posledných šiestich hodín zlyhávala na destination KMS policy. Source points existovali v compromised account-e, isolated vault mal starší clean point mimo fifteen-minute RPO.

Hypotézy zahŕňali source backup failure, copy selection, destination vault policy, KMS deny, lifecycle expiration and Region mismatch. Copy-job history a CloudTrail ukázali `AccessDenied` pri destination encryption; source jobs boli validné.

Containment zachovalo source points a zablokovalo destructive credentials. Recovery vybrala last clean isolated point, reconciliovala missing interval z provider/outbox evidence a transparentne vyhlásila RPA violation. KMS/vault policy sa opravila a canary copy/restore prešla.

Closure vyžadovala completed source and destination generations, usable key, clean-room restore, payment validation and alerting that treats required copy failure as protection failure.

## 14. Cleanup after rehearsal

Cleanup po recovery rehearsal je súčasť acceptance, nie administratívny dodatok. Obnovené dáta, temporary credentials, network paths a testovacie writers môžu po úspešnom cvičení vytvoriť nový security alebo cost incident, preto sa ich odstránenie a revokácia dokazujú samostatným inventory read-backom.

Recovery test môže vytvoriť databases, volumes, filesystems, ENIs, secrets and logs containing production data. Cleanup is governed transition:

```text
validation complete
→ evidence retained
→ application and access disabled
→ restored resources deleted
→ temporary shares and sessions revoked
→ residual ENIs/snapshots checked
→ cost and data-exposure closure
```

## Kontrolné otázky

1. Aký rozdiel je medzi policy-covered resource-om a recoverable business generation?
2. Prečo source backup success nepreukazuje isolated copy?
3. Ako application checkpoint mení recovery point?
4. Prečo latest point nemusí byť správny point?
5. Čo musí obsahovať recovery manifest?
6. Čo Vault Lock chráni a aké riziko prináša chybná retention?
7. Čo preukazuje restore job `COMPLETED`?
8. Ako sa meria Recovery Point Actual?
9. Ktorý forbidden test patrí do clean-room restore-u?
10. Ako sa uzavrie cleanup po restore rehearsal?

## Oficiálna dokumentácia

- [AWS Backup Developer Guide](https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html)
- [Backup plans](https://docs.aws.amazon.com/aws-backup/latest/devguide/about-backup-plans.html)
- [Cross-account backup](https://docs.aws.amazon.com/aws-backup/latest/devguide/create-cross-account-backup.html)
- [Vault Lock](https://docs.aws.amazon.com/aws-backup/latest/devguide/vault-lock.html)
- [Logically air-gapped vaults](https://docs.aws.amazon.com/aws-backup/latest/devguide/logicallyairgappedvault.html)
- [Restore testing](https://docs.aws.amazon.com/aws-backup/latest/devguide/restore-testing.html)
- [Restoring a backup](https://docs.aws.amazon.com/aws-backup/latest/devguide/restoring-a-backup.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: KMS a Secrets Manager](kms-secrets-manager.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Well-Architected Framework →](well-architected-framework.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
