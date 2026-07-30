# AWS Organizations a accounts

AWS account je základná ownership a blast-radius boundary pre resources, IAM principals, quotas, billing, KMS keys a service configuration. AWS Organizations nad accounts pridáva hierarchy, centrally managed policies, delegated administration a consolidated governance. Multi-account model však nie je bezpečný iba počtom účtov. Potrebuje opakovateľný account lifecycle od requestu cez baseline až po quarantine a closure.

```text
workload a risk profile
→ account request a owner
→ OU placement
→ account creation
→ identity, logging, network a security baseline
→ workload onboarding
→ effective organization + IAM + resource policy
→ operation a incident containment
→ move, quarantine alebo closure
```

Account `created` nie je account `ready`. Ready account musí preukázať, že jeho guardrails, identity, logging, network, backup a recovery paths sú effective.

## 1. Governance subject pre Atlas Payments

Atlas organization má ID `o-atlas42`. Management account je `100000000001`, security delegated administrator `100000000010`, log archive `100000000011`, network account `100000000012` a production workload account `100000000042`.

Payments account patrí do `Root/Workloads/Production/Payments`. Baseline generation je `AB-17`, SCP set `SCP-PROD-9`, RCP set `RCP-DATA-4` a Identity Center assignments `IC-31`. Povolené workload Regions sú `eu-central-1` a recovery `eu-west-1`. Zakázané je nasadiť workload do management accountu, vypnúť central audit, verejne sprístupniť ledger alebo používať neschválený Region.

Každý governance incident musí používať account ID a aktuálnu OU/policy generation. Display name `payments-prod` nie je stabilná authorization identity.

## 2. Organization hierarchy ako inheritance graph

Organization obsahuje jeden root, pod ním OUs a member accounts. OU môže obsahovať accounts aj child OUs. Policies attached na root alebo parent OUs sa dedia podľa konkrétneho policy type-u.

```text
management account
→ organization root
→ foundational OUs
→ workload lifecycle OUs
→ member account
→ local IAM a resource policies
```

AWS odporúča navrhovať OUs podľa funkcie a spoločného control profilu, nie kopírovať organizačný diagram firmy. Foundation typicky oddeľuje security a infrastructure a workload OUs odlišujú production a non-production controls. citeturn398658search0turn398658search1

Ukážkový Atlas strom:

```text
Root
├── Security
│   ├── LogArchive account
│   └── SecurityTooling account
├── Infrastructure
│   ├── Network account
│   └── SharedServices account
├── Workloads
│   ├── Production
│   │   └── Payments account
│   └── NonProduction
└── Lifecycle
    ├── Sandbox
    ├── Quarantine
    └── Suspended
```

`Quarantine` a `Suspended` nie sú iba názvy. Každá OU má explicitný capability envelope a exit criteria.

## 3. Praktický inventory organization state-u

Najprv preukáž caller a organization identity:

```bash
aws sts get-caller-identity --profile org-admin

aws organizations describe-organization \
  --profile org-admin \
  --query 'Organization.{Id:Id,MasterAccountId:MasterAccountId,FeatureSet:FeatureSet,AvailablePolicyTypes:AvailablePolicyTypes}'
```

Aktuálne API môže v niektorých výstupoch používať historický field name `MasterAccountId` pre management account. Dokumentácia a governance artefakty majú používať termín management account.

Nájdi root a top-level OUs:

```bash
ROOT_ID=$(aws organizations list-roots \
  --profile org-admin \
  --query 'Roots[0].Id' \
  --output text)

aws organizations list-organizational-units-for-parent \
  --profile org-admin \
  --parent-id "$ROOT_ID" \
  --query 'OrganizationalUnits[].{Name:Name,Id:Id}' \
  --output table
```

Tieto príkazy ukazujú current tree. Nehovoria, či account baseline alebo policy intent je správny.

Pre exact account zisti parent:

```bash
aws organizations list-parents \
  --profile org-admin \
  --child-id 100000000042
```

Account má v organizácii jedného parenta: root alebo OU. Ak incidentný runbook predpokladá `Recovery` OU, read-back musí túto placement skutočne preukázať.

## 4. Management account je trust root, nie workload account

Management account ovláda organization lifecycle a consolidated billing. AWS best practice je držať bežné resources a workloads v member accounts a management account používať iba na úlohy, ktoré ho skutočne vyžadujú. citeturn398658search9turn398658search37

Dôvod nie je estetický. SCPs neobmedzujú users a roles v management account-e a authorization policies nechránia jeho resources rovnakým spôsobom ako member-account resources. Workload v management account-e preto obchádza významnú guardrail vrstvu. citeturn398658search24turn398658search41

Management account potrebuje phishing-resistant MFA, root credential custody, minimum human accessu, alerting na policy changes a delegovanie service administration do member accounts. Deployment pipeline pre payment application tam nepatrí.

## 5. OU ako risk a lifecycle boundary

OU má reprezentovať stabilný control profil. Production account potrebuje prísnejší Region, logging, public-access a change contract než sandbox. Quarantine potrebuje obmedziť mutations a external access, no zachovať forensic telemetry a recovery.

Account move je high-impact change:

```text
current parent a policy attachments
→ proposed parent a inherited policies
→ effective authorization/configuration diff
→ positive a forbidden test
→ move
→ baseline reconciliation
→ workload a recovery validation
```

Move operation:

```bash
aws organizations move-account \
  --profile org-admin \
  --account-id 100000000042 \
  --source-parent-id ou-old1234 \
  --destination-parent-id ou-prod5678
```

Command accepted nepreukazuje, že workload stále funguje. Policy inheritance sa zmenila a account baseline sa musí retestovať. Produkčný move sa nevykonáva bez explicitného diffu a rollback pathu.

## 6. Service Control Policy ako principal permissions guardrail

SCP definuje maximálne dostupné permissions pre IAM principals v member accounts. Neudeľuje access. Local identity policy musí stále obsahovať allow a všetky applicable denies/envelopes musia request prepustiť. citeturn398658search28turn398658search29

Nasledujúci SCP odmieta používanie Regions mimo `eu-central-1` a `eu-west-1`, pričom global alebo recovery-required actions musia byť vedome vyňaté podľa presného service contractu:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnapprovedRegions",
      "Effect": "Deny",
      "NotAction": [
        "iam:*",
        "organizations:*",
        "route53:*",
        "support:*"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": [
            "eu-central-1",
            "eu-west-1"
          ]
        }
      }
    }
  ]
}
```

`NotAction` list je citlivý security design. Nesmie sa slepo kopírovať; service endpoints a global-service semantics sa musia overiť. SCP sa najprv testuje na canary OU.

Vytvorenie policy cez CLI:

```bash
aws organizations create-policy \
  --profile org-admin \
  --name AtlasApprovedRegionsV1 \
  --description 'Deny workload actions outside approved primary and recovery Regions' \
  --type SERVICE_CONTROL_POLICY \
  --content file://approved-regions-scp.json
```

Po vytvorení nie je policy effective, kým sa neattachne na target. Attachment na root nie je prvý rollout krok.

## 7. Resource Control Policy ako resource-side guardrail

RCP obmedzuje, aké actions môžu identities vykonávať nad podporovanými resources v member accounts. Rovnako ako SCP access neudeľuje. Jeho effective result sa kombinuje s identity alebo resource policy permissions. citeturn398658search13turn398658search32turn398658search39

Príklad RCP, ktorý odmietne nešifrovaný S3 transport:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyInsecureTransportToS3Resources",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": "*",
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

RCP support je service-specific. Pred rolloutom sa overuje, ktoré resources a principals policy skutočne obmedzuje. AWS odporúča testovať impact a sledovať CloudTrail AccessDenied evidence pred broad root attachmentom. citeturn398658search13turn398658search33

## 8. Declarative policies nie sú authorization policies

Declarative policies centrálne konfigurujú podporované service features naprieč organizáciou. Nepoužívajú rovnaký allow/deny model ako SCP alebo RCP. Môžu napríklad presadzovať podporované VPC security settings alebo obmedziť public sharing určitých resources podľa policy type-u. citeturn398658search5turn398658search21turn398658search31

Pri diagnostike treba najprv identifikovať policy type. `AccessDenied` smeruje k authorization graphu; resource vytvorený s centrally enforced configuration môže byť výsledkom declarative policy inheritance.

## 9. Diagnostika policy inheritance

Pre account alebo OU zobraz direct attachments:

```bash
aws organizations list-policies-for-target \
  --profile org-admin \
  --target-id 100000000042 \
  --filter SERVICE_CONTROL_POLICY \
  --query 'Policies[].{Name:Name,Id:Id,AwsManaged:AwsManaged}' \
  --output table
```

Tento príkaz ukáže policies priamo attached na target. Effective SCP set však zahŕňa aj root a parent OUs. Preto treba traversovať parent chain a pre každý target zopakovať listing. Incident script má uložiť celý path a policy versions.

Obsah policy:

```bash
aws organizations describe-policy \
  --profile org-admin \
  --policy-id p-abc123 \
  --query 'Policy.{Summary:PolicySummary,Content:Content}'
```

Content je JSON string a treba ho parse-nuť. Presence policy v listingu nepreukazuje, ktorá statement matchla exact denied request. Na to treba action, resource, Region, condition context a CloudTrail authorization evidence.

## 10. Account vending ako executable baseline

Account request musí obsahovať ownera, cost center, data classification, lifecycle a required Regions. Po vytvorení sa account umiestni do OU a baseline automation nakonfiguruje identity, audit, network, backup, budgets a security service enrollment.

Terraform ukážka pre OU a policy attachment:

```hcl
resource "aws_organizations_organizational_unit" "payments_prod" {
  name      = "Payments"
  parent_id = aws_organizations_organizational_unit.production.id

  tags = {
    Environment = "production"
    Owner       = "payments-platform"
  }
}

resource "aws_organizations_policy" "approved_regions" {
  name        = "AtlasApprovedRegionsV1"
  description = "Restrict workload operations to approved Regions"
  type        = "SERVICE_CONTROL_POLICY"
  content     = file("${path.module}/approved-regions-scp.json")
}

resource "aws_organizations_policy_attachment" "payments_regions" {
  policy_id = aws_organizations_policy.approved_regions.id
  target_id = aws_organizations_organizational_unit.payments_prod.id
}
```

Terraform state a plan sú governance-sensitive. Apply môže ovplyvniť mnoho accounts. Pipeline musí používať canary target, policy tests a approval viazaný na exact policy digest.

Account acceptance potom vykoná positive aj forbidden tests. Positive test vytvorí bounded recovery resource v `eu-west-1`. Forbidden test skúsi unapproved Region, vypnutie CloudTrail alebo public ledger policy a očakáva deny.

## 11. Delegated administration

Delegated administrator umožňuje member accountu spravovať konkrétnu AWS service integration pre organization. Nie je to všeobecná administrácia Organizations. Security tooling account môže byť delegated admin pre Security Hub alebo GuardDuty podľa service supportu, zatiaľ čo management account si ponechá organization trust-root operations.

Inventory delegácií:

```bash
aws organizations list-delegated-administrators \
  --profile org-admin \
  --query 'DelegatedAdministrators[].{AccountId:Id,Name:Name,Status:Status}'

aws organizations list-delegated-services-for-account \
  --profile org-admin \
  --account-id 100000000010
```

Prvý príkaz ukáže delegated accounts, druhý service principals pre konkrétny account. Delegation stále potrebuje least privilege, audit a emergency revoke path.

## 12. Worked incident: recovery account bol presunutý do Suspended OU

Po regional incidente mala Atlas obnoviť workload v `eu-west-1`. Recovery deployment role dostávala `AccessDenied` pri vytváraní subnetov a KMS keyu, hoci local IAM policy obsahovala administrator allow.

Hypotézy zahŕňali wrong caller, trust policy, permissions boundary, Region SCP, RCP, wrong OU, propagation a incomplete baseline. `sts:GetCallerIdentity` potvrdil správny account a session. `list-parents` ukázal, že recovery account bol deň pred incidentom presunutý z `Recovery` do `Suspended` OU počas cost cleanupu. Zdedený SCP povoľoval iba read-only a cleanup actions.

Local `AdministratorAccess` nemohol prekročiť SCP maximum. SCP nezlyhal; governance vykonala presne nakonfigurovaný contract. Root cause bol nesprávny account lifecycle move a chýbajúci DR regression test.

Containment zachovalo CloudTrail, move a policy-version evidence a zmrazilo ďalšie organization policy zmeny. Tím neodstránil root SCP a nepoužil management-account credentials na workload deployment.

Recovery vrátila exact account do schválenej Recovery OU, overila inherited SCP/RCP/declarative policies a znovu reconciliovala identity, logging, network, KMS, backup a quotas. DR pokračoval až po positive recovery deployment teste a forbidden testoch pre public access, audit disable a unapproved Regions.

## 13. Quarantine bez zničenia vyšetrovania

Quarantine OU môže odmietnuť workload writes alebo federation a obmedziť network paths. Musí však zachovať CloudTrail/log delivery, forensic role, backup retention, KMS decrypt podľa incident planu a containment operations.

Slepý deny-all môže odstrihnúť security tooling, zablokovať snapshot alebo zničiť recovery. Quarantine policy sa preto testuje vopred a má explicitnú capability envelope.

## 14. Account closure

Closure začína inventory, nie `close-account` API. Treba identifikovať resources, data retention, cross-account trusts, DNS, certificates, KMS keys, commitments a legal holds. Account sa najprv presunie do lifecycle OU, zastavia sa nové workloads a vykoná sa export/backup a recovery validation.

```text
closure request and owner approval
→ resource/data/trust inventory
→ retention and export
→ credentials/network/DNS cleanup
→ suspended observation period
→ legal and recovery checks
→ account closure
→ evidence retention
```

Zmazanie resources nie je account closure a closure nie je okamžitý dôkaz fyzického data deletion.

## Kontrolné otázky

1. Prečo je account základná blast-radius boundary?
2. Prečo OUs nemajú kopírovať reporting hierarchy?
3. Čo SCP preukazuje a prečo access neudeľuje?
4. Aký rozdiel je medzi SCP, RCP a declarative policy?
5. Prečo direct policy attachments nie sú celý effective set?
6. Ktoré tests patria k account baseline acceptance?
7. Prečo workloads nemajú bežať v management account-e?
8. Ako account move ovplyvní DR readiness?
9. Čo musí quarantine policy zachovať?
10. Kedy je account closure skutočne pripravená?

## Oficiálna dokumentácia

- [What is AWS Organizations?](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html)
- [Best practices for OUs](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_ous_best_practices.html)
- [Management account best practices](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_best-practices_mgmt-acct.html)
- [Service control policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html)
- [Resource control policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_rcps.html)
- [Declarative policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_declarative_policies.html)
- [AWS Organizations CLI reference](https://docs.aws.amazon.com/cli/latest/reference/organizations/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: High availability a disaster recovery](high-availability-disaster-recovery.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: IAM →](iam.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
