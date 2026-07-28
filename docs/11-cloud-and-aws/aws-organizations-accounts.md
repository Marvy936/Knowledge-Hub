# AWS Organizations a accounts

AWS account je základná AWS-native boundary pre resource ownership, identity, quotas, billing a veľkú časť incident blast radiusu. AWS Organizations pridáva nad účty governance hierarchy, authorization boundaries, declarative configuration a delegated service administration. Bez opakovateľného account lifecycle-u však multi-account model iba rozmnoží nekonzistentné prostredia.

Dominantný lifecycle:

```text
business workload/risk profile
→ account request a owner
→ OU a policy placement decision
→ account creation/enrollment
→ identity, logging, network a security baseline
→ workload onboarding a delegated administration
→ effective organization/IAM/resource policy
→ operation, evidence a incident containment
→ move/quarantine/suspension
→ data/resource cleanup a account closure
```

## 1. Exact governance subject

Atlas Payments používa governance subject `ORG-PAY-42`:

```text
organization ID = o-atlas42
management account = 100000000001
security delegated admin = 100000000010
log archive account = 100000000011
network account = 100000000012
production workload account = 100000000042
OU path = Root/Workloads/Production/Payments
account baseline generation = AB-17
SCP set = SCP-PROD-9
RCP set = RCP-DATA-4
identity-center assignment generation = IC-31
required Regions = eu-central-1 + eu-west-1 recovery
business owner = Payments Platform
forbidden outcomes = workload in management account, disabled audit, public ledger access, unapproved Region use
```

Troubleshooting musí viazať verdict na account ID a aktuálnu OU/policy generation. Account name alebo organizačný tím nestačí.

## 2. Account boundary a organization hierarchy

Member account vlastní resources, IAM principals, KMS keys, quotas a service configuration. Organization určuje, kde account patrí a aké centrálne controls sa naň uplatnia.

```text
management account
→ organization root
→ parent/child OUs
→ member account
→ IAM/resource policies a resources
```

Account nie je absolútna izolácia. Shared network, central deployment role, delegated administrator, resource policies a cross-account trust môžu blast radius rozšíriť. Tieto hrany musia byť explicitné v governance graph-e.

## 3. Management account

Management account je najvyšší trust root pre Organizations a consolidated billing. Bežné workloads ani business data doň nepatria.

Controls:

- phishing-resistant MFA a root credential custody;
- žiadne bežné deployment pipelines;
- minimum human accessu;
- delegovanie service administration do member accounts;
- alerting na root a organization policy changes;
- testovaný break-glass a contact recovery.

SCP neobmedzuje principals v management account-e a RCP neobmedzuje resources, ktoré management account vlastní. Workload v ňom preto obchádza dôležitú organization guardrail vrstvu.

## 4. OU ako policy a lifecycle boundary

OU reprezentuje stabilný risk alebo lifecycle profil, nie momentálny org chart. Production, sandbox, security foundation, shared infrastructure, quarantine a suspended accounts majú rozdielne controls a recovery requirements.

Príliš plochá hierarchy vedie k account-specific exceptions. Príliš hlboká hierarchy komplikuje effective policy a incident diagnosis.

Account move je governance change:

```text
current OU/policies
→ proposed OU/policies
→ effective-policy diff
→ positive/negative validation
→ move
→ baseline reconciliation
→ workload a recovery verification
```

## 5. Organization policy vrstvy

### Service Control Policy

SCP určuje maximum permissions pre principals v member accounts. Access neudeľuje.

```text
identity/resource allow
∩ applicable SCP boundary
∩ permissions/session boundaries
− explicit denies
= možný effective principal access
```

### Resource Control Policy

RCP určuje organization-level maximum accessu k podporovaným resources v member accounts. Dopĺňa resource policies najmä pri cross-account/external access paths. Access tiež neudeľuje.

### Declarative policies

Declarative policies centrálne nastavujú podporovanú service configuration a používajú vlastnú inheritance/merge logiku. Nesmú sa diagnostikovať ako SCP allow/deny model.

### Effective organization state

Verdict závisí od:

- root policy attachments;
- všetkých parent/child OU attachments;
- account-level attachments;
- policy type a inheritance semantics;
- management/member account boundary;
- service/resource supportu;
- local IAM/resource/KMS policy.

## 6. Account vending a baseline

Account creation nie je hotová pri pridelení account ID. Ready account potrebuje:

```text
owner/cost center/data classification
→ OU placement
→ root/contact/security setup
→ IAM Identity Center assignments
→ CloudTrail/Config/security-service enrollment
→ log archive delivery
→ network/DNS/endpoints
→ KMS/backup baseline
→ quotas/tags/budgets
→ positive a forbidden control tests
→ workload onboarding
```

Baseline musí byť versionovaný. `Account created` a `baseline reconciled` sú rozdielne stavy.

## 7. Delegated administration

Delegated administrator umožňuje member accountu spravovať konkrétnu service integration pre organization. Neznamená všeobecnú organization administráciu.

Pre každú delegáciu eviduj:

- service a supported scope;
- delegated account ID;
- role/trust generation;
- data a resources, ktoré môže meniť;
- organization policies, ktoré naň stále pôsobia;
- audit a emergency revocation path.

## 8. Connected walkthrough — recovery zablokuje organization guardrail

### Symptom

Po regional incidente má Payments obnoviť workload v `eu-west-1`. Deployment role dostáva `AccessDenied` pri vytváraní recovery KMS keyu a subnetov, hoci lokálna IAM policy povoľuje potrebné actions.

### Competing hypotheses

1. Pipeline používa nesprávny account alebo role.
2. Trust policy alebo STS session je chybná.
3. Permissions boundary blokuje action.
4. SCP denyuje recovery Region.
5. RCP blokuje key/resource policy.
6. Account bol presunutý do nesprávnej OU.
7. Policy propagation ešte nie je dokončená.
8. Service používa dependent action alebo global endpoint.
9. Recovery account baseline nie je dokončený.

### Discriminating observations

| Observation | Čo rozlišuje |
|---|---|
| `sts:GetCallerIdentity`, account a session ARN | wrong caller od policy evaluation |
| current OU path a move history | lokálny IAM problém od governance placementu |
| effective SCP/RCP attachments na každej úrovni | konkrétnu organization boundary |
| denied action/resource/Region/request context | broad symptom od exact requestu |
| CloudTrail event a authorization message | trust/session od explicit deny |
| baseline generation a Config/security enrollment | policy deny od incomplete account vendingu |
| positive control v `eu-central-1` a recovery action v `eu-west-1` | service-wide deny od Region conditionu |

### Finding

Recovery account bol deň pred incidentom presunutý z `Recovery` OU do `Suspended` OU počas cost cleanupu. Zdedený SCP povoľoval iba read-only a cleanup actions. Lokálny `AdministratorAccess` preto nemohol obnoviť deployment. Recovery path zároveň nebola súčasťou OU-move regression testu.

### Containment

- zachovať CloudTrail, OU move a policy-version evidence;
- neodstraňovať root SCP ani nepoužiť management-account credentials na workload deployment;
- obmedziť zmenu na exact recovery account;
- zmraziť ďalšie account moves/policy rollouty;
- potvrdiť, že log archive a security accounts zostávajú chránené.

### Recovery

1. Vrátiť account do schválenej Recovery OU cez auditovanú governance operáciu.
2. Overiť expected SCP/RCP/declarative policy generation.
3. Znovu reconciliovať identity, logging, network, KMS, backup a quota baseline.
4. Vykonať positive recovery deployment test.
5. Vykonať forbidden tests pre public access, nepovolené Regions a audit disable.
6. Pokračovať v DR až po account acceptance verdicte.

### Verification

- recovery resources možno vytvoriť iba v schválených Regions;
- deployment role nemá organization-management capabilities;
- CloudTrail a security telemetry nemožno vypnúť;
- ledger resource policy odmieta external principal mimo organization contractu;
- management account neobsahuje workload resources;
- DR business transaction prejde;
- forbidden public/cross-account access zlyhá.

## 9. Policy rollout

Organization policy má veľký blast radius. Bezpečný rollout:

```text
policy intent a owner
→ exact affected accounts/actions
→ static validation/simulation
→ canary account alebo OU
→ positive aj forbidden tests
→ staged OU rollout
→ CloudTrail/operational observation
→ recovery-path validation
→ wider attachment
```

Root attachment nie je prvý test krok. Každá zmena potrebuje rollback path, ale rollback nesmie odstrániť evidence alebo znovu otvoriť forbidden access.

## 10. Quarantine a incident response

Quarantine OU môže obmedziť nové writes, federation alebo network paths. Musí však zachovať:

- security telemetry;
- forensic access;
- backup/retention;
- KMS decrypt podľa incident plánu;
- emergency containment operations;
- owner a exit criteria.

Slepý deny-all môže zničiť schopnosť vyšetrovať alebo obnovovať.

## 11. Account closure lifecycle

```text
closure request a owner approval
→ workload/data/dependency inventory
→ retention/export/backup
→ cross-account trust a DNS/network removal
→ credential/KMS cleanup
→ billing/commitment review
→ suspended/quarantine period
→ recovery test alebo legal hold check
→ account closure
→ post-closure evidence retention
```

Zmazanie resources nie je account closure a account closure nie je okamžitá data-deletion garancia.

## 12. Earlier controls

- account vending pipeline a baseline conformance;
- OU/policy version inventory;
- canary OU;
- positive a forbidden control suite;
- recovery account permanent ownership;
- management-account workload prohibition;
- delegated-admin inventory;
- organization-wide CloudTrail/log archive;
- move/closure approvals a evidence;
- periodic cross-account trust graph review.

## 13. Kontrolné otázky

1. Ktorý account ID a OU path sú predmetom zmeny?
2. Aký risk/lifecycle profil OU reprezentuje?
3. Čo povoľuje local IAM a čo obmedzuje SCP/RCP?
4. Je management account mimo workload plane-u?
5. Je account baseline skutočne reconciled?
6. Ktoré delegated administrators majú organization scope?
7. Ako sa policy change testuje na canary OU?
8. Zachová quarantine forensic a recovery capabilities?
9. Je recovery Region zahrnutý v guardrail testoch?
10. Aký positive a forbidden outcome uzatvára account lifecycle krok?

## Glossary impact

Relevantné pojmy: governed account lifecycle subject, account baseline generation, OU placement generation, effective organization policy, governance graph, account acceptance verdict, canary OU, recovery account eligibility, quarantine capability envelope, delegated-administration subject a account closure evidence.

## Oficiálna dokumentácia

- [AWS Organizations authorization policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_authorization_policies.html)
- [Service control policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html)
- [Resource control policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_rcps.html)
- [Management account best practices](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_best-practices_mgmt-acct.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: High availability a disaster recovery](high-availability-disaster-recovery.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: IAM →](iam.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
