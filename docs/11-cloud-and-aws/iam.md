# IAM

AWS Identity and Access Management (IAM) rozhoduje, či konkrétny authenticated request môže vykonať konkrétnu action nad konkrétnym resource-om v konkrétnom request contexte. IAM preto nie je zoznam users a policies, ale viacvrstvový authorization graph s implicit deny, explicit grants, permissions envelopes, trust boundaries a explicit deny pravidlami.

Dominantný lifecycle:

```text
human/workload operation intent
→ credential source a principal/session identity
→ exact AWS API request
→ trust a authentication
→ identity/resource policy grants
→ permissions boundary/session/SCP/RCP envelopes
→ conditions, tags a dependent-service checks
→ allow/deny verdict
→ service-side effect
→ CloudTrail a business outcome
→ credential/policy rotation, revocation a revalidation
```

## 1. Exact request subject

Atlas Payments používa IAM incident subject `IAM-PAY-42`:

```text
caller account = 100000000042
caller session ARN = arn:aws:sts::100000000042:assumed-role/payments-settlement/POD-7F2
credential source = EKS workload identity / STS session STS-991
session expiry = 2026-07-28T12:00Z
action = kms:Decrypt
resource = arn:aws:kms:eu-central-1:100000000042:key/key-pay-42
request Region/endpoint = eu-central-1
identity policy generation = IP-18
trust policy generation = TP-12
permissions boundary = PB-WORKLOAD-6
session policy = SP-7
SCP/RCP generation = SCP-PROD-9 / RCP-DATA-4
KMS key policy generation = KP-22
encryption context = service=payments, purpose=settlement
business outcome = decrypt settlement credential and commit exactly once
forbidden outcomes = decrypt by another workload/tenant/Region or stale session
```

`AccessDenied` bez caller ARN, action, resource ARN, Region, timestamp a request ID nie je dostatočne definovaný incident.

## 2. Authentication, principal a session

Authentication určuje identitu requestu. Authorization určuje, či request môže prejsť.

Relevantní principals:

- root user;
- IAM user;
- IAM role session;
- federated alebo IAM Identity Center session;
- AWS service principal;
- workload používajúci STS credentials;
- cross-account principal.

Role sama neposiela request. Request posiela konkrétna assumed-role session s vlastným ARN, session name, tags, source identity, policies a expiry.

Pri každom incidente najprv over skutočného callera:

```bash
aws sts get-caller-identity
```

Profile name, Pod service account alebo pipeline job name nie sú dôkaz použitej AWS identity.

## 3. Credential lifecycle

```text
identity alebo workload binding
→ STS/token exchange
→ temporary credential issuance
→ SDK credential-provider selection
→ process-loaded credential
→ signed request
→ expiry/refresh
→ revocation alebo replacement
```

Projected alebo refreshed credential na disku nepreukazuje, že ho application process načítal. Rovnako zmena trust alebo permissions policy nemusí ukončiť už vydanú session; treba poznať session lifetime a revocation model.

Pre workforce access preferuj federation/IAM Identity Center a temporary sessions. Long-lived access keys potrebujú výnimočný owner, rotation, last-used monitoring a explicitný retirement plán.

## 4. Role má trust aj permissions contract

```text
source principal permission na sts:AssumeRole
+ target role trust policy
+ STS request conditions
→ role session
→ role permissions a applicable envelopes
```

Trust policy odpovedá, kto smie role assume-nuť. Permissions policies odpovedajú, čo smie vzniknutá session robiť. Jedna vrstva bez druhej nevytvorí použiteľný access.

Pri third-party cross-account role môže byť potrebný external ID. Pri workforce/workload federation sleduj audience, issuer, subject, session tags a source identity.

## 5. Policy grant a envelope vrstvy

### Identity-based policy

Policy pripojená k userovi, group alebo role poskytuje candidate grants pre actions/resources/conditions.

### Resource-based policy

Policy pri resource-e môže povoľovať same-account alebo cross-account principals. Príklady: S3 bucket policy, KMS key policy, queue/topic policy, Secrets Manager resource policy a role trust policy.

### Permissions boundary

Boundary je maximum permissions, ktoré môže identity policy udeliť IAM userovi alebo role. Sama access neudeľuje.

### Session policy

Session policy zúži konkrétnu STS session.

### SCP a RCP

SCP obmedzuje maximum pre principals v member accounts. RCP obmedzuje maximum accessu k podporovaným resources v member accounts. Ani jedna policy nie je grant.

### Explicit deny

Applicable explicit deny prevažuje nad allow. Poradie statements v JSON dokumente prioritu neurčuje.

## 6. Request evaluation model

Zjednodušený model:

```text
authenticated principal/session
→ exact action/resource/request context
→ identity a resource policy candidate grants
→ trust/cross-account requirements
→ permissions boundary a session policy
→ SCP/RCP
→ service-specific policy, napríklad KMS key policy
→ applicable explicit denies
→ allow alebo deny
```

Detaily sa líšia podľa principal type, same-account/cross-account modelu a resource policy semantics. Diagnostika preto nesmie používať univerzálne „policies sa sčítajú“.

## 7. Conditions a ABAC

Conditions môžu používať:

- principal/account/organization identity;
- source IP, VPC alebo VPC endpoint;
- requested Region;
- MFA;
- principal, resource alebo request tags;
- TLS;
- KMS encryption context;
- token issuer/audience/subject;
- source account/ARN.

Missing-key semantics, `IfExists`, negated operators a multivalue operators môžu zmeniť verdict. Každá security condition potrebuje positive aj forbidden test.

ABAC prepája governed principal tags a resource tags. Ak principal smie meniť privileged tag, môže meniť aj svoje effective permissions. Tag mutation je preto súčasť authorization graphu.

## 8. Indirect capabilities

Úzka-looking permission môže vytvoriť širšiu authority:

- `iam:PassRole` + create/update service resource;
- create Pod/Task/Function s privilegovanou execution role;
- edit role trust alebo permissions boundary;
- attach policy alebo create policy version;
- update Lambda code alebo CI pipeline;
- read Secrets a následne používať external credential;
- KMS decrypt nad broad encryption contextom.

Least privilege sa preto hodnotí podľa reachable capability, nie iba podľa jedného policy statementu.

## 9. Connected walkthrough — `AccessDenied` po úspešnom policy teste

### Symptom

Payments Pod po rotácii KMS policy dostáva `AccessDenied` pri `kms:Decrypt`. IAM simulator pre expected role ukazuje allow a iné Pody v rovnakom namespace fungujú.

### Competing hypotheses

1. Aplikácia používa inú role/session než sa testuje.
2. Process drží starú STS session.
3. Identity policy chýba alebo má chybný ARN.
4. Permissions boundary alebo session policy action blokuje.
5. SCP/RCP denyuje Region alebo resource.
6. KMS key policy nepovoľuje session/account path.
7. Encryption context condition sa nezhoduje.
8. Workload identity trust subject/audience sa zmenil.
9. Request smeruje na iný key alebo Region.
10. Explicit deny vzniká cez tag alebo VPC endpoint condition.

### Discriminating observations

| Observation | Čo rozlišuje |
|---|---|
| actual `GetCallerIdentity` z affected processu | expected role od reálnej session |
| credential issue/expiry a process start time | current policy od stale loaded session |
| CloudTrail event request ID, key ARN a encryption context | broad `AccessDenied` od exact KMS requestu |
| identity policy/boundary/session/SCP/RCP versions | grant failure od envelope deny |
| KMS key policy a grant inventory | IAM allow od KMS-specific authorization |
| working versus failing Pod cohort | global policy od process/session generation |
| STS assume-role/web-identity event | decrypt failure od credential issuance/trust failure |

### Finding

Affected Pod bol vytvorený pred workload-identity migráciou a SDK credential chain uprednostnila staré environment access keys pred web-identity credentials. `GetCallerIdentity` ukázalo legacy IAM usera. Simulator testoval novú role, teda iný principal. KMS key policy správne odmietla legacy usera.

### Containment

- nezvyšovať permissions novej role ani nepridávať wildcard do key policy;
- zablokovať ďalšie použitie legacy key a zachovať CloudTrail evidence;
- izolovať affected Pod cohort;
- chrániť settlement queue pred nekontrolovanými retries;
- overiť, či legacy credential nebol použitý inde.

### Recovery

1. Odstrániť static environment credentials zo source Secretu a Pod template-u.
2. Revoke/deactivate legacy access key.
3. Vytvoriť novú Pod generation s explicitným workload-identity contractom.
4. Overiť caller ARN, session tags/source identity a expiry.
5. Vykonať allowed decrypt s presným encryption contextom.
6. Vykonať forbidden decrypt z cudzej role, tenant contextu a nepovoleného Regionu.
7. Reconciliovať pending settlement operations presne raz.

### Verification

- každý accepted Pod používa expected assumed-role session;
- legacy access key je disabled a neprijíma requests;
- correct encryption context funguje;
- wrong tenant/purpose/Region/principal je denied;
- CloudTrail obsahuje source identity a request correlation;
- payment settlement prejde exactly once;
- žiadna wildcard permission nebola pridaná.

## 10. `iam:PassRole` a service execution

`iam:PassRole` umožní principalu odovzdať role AWS službe. Bezpečný contract obmedzuje:

```text
caller
+ exact role ARN/path/tags
+ destination service
+ resource/workload scope
+ kto môže meniť passed role
```

Troubleshooting musí odlíšiť caller permission na `PassRole`, trust role voči service principalu a následné runtime permissions service session.

## 11. Cross-account access

Cross-account operation typicky potrebuje:

```text
source principal permission
→ target trust alebo resource policy
→ STS session alebo direct resource request
→ SCP/RCP a permissions envelopes
→ target service/KMS policy
→ business operation
```

Allow v source account-e nestačí, ak target boundary request neprijíma. Naopak broad target resource policy môže vytvoriť external access aj pri úzkych source policies.

## 12. Audit a revocation closure

Pre významný incident zachovaj:

- caller/session ARN a account ID;
- credential source, issue time a expiry;
- action, resource ARN, Region a endpoint;
- request ID a UTC timestamp;
- CloudTrail event;
- identity/resource/trust/KMS policies;
- boundary/session/SCP/RCP versions;
- tags, VPC/source context a encryption context;
- application operation ID a business result.

Revocation je uzavretá až keď forbidden credential alebo path preukázateľne zlyhá. Edit policy dokumentu nie je sám o sebe revocation verdict.

## 13. Earlier controls

- federation a temporary credentials;
- explicitný credential-provider contract;
- short sessions a refresh telemetry;
- role trust tests;
- positive aj forbidden authorization tests;
- policy-as-code validation;
- permissions-boundary a pass-role governance;
- Access Analyzer a unused-access review;
- CloudTrail correlation/source identity;
- credential inventory a automatic disable;
- periodic reachable-capability review.

## 14. Kontrolné otázky

1. Ktorý exact principal/session poslal request?
2. Odkiaľ process načítal credentials?
3. Aká je exact action, resource ARN, Region a request context?
4. Ktorá policy je grant a ktorá iba envelope?
5. Existuje applicable explicit deny?
6. Je potrebná resource alebo KMS key policy?
7. Je request same-account alebo cross-account?
8. Vytvára `PassRole`, tag mutation alebo workload creation indirect escalation?
9. Ako sa preukáže revocation starej session/credentialu?
10. Aký allowed a forbidden business outcome uzatvára zmenu?

## Glossary impact

Relevantné pojmy: AWS request authorization subject, credential-source identity, process-loaded AWS credential, assumed-role session subject, effective permission graph, permissions envelope, KMS authorization boundary, indirect IAM capability, authorization closure, credential revocation verdict, positive authorization test a forbidden authorization test.

## Oficiálna dokumentácia

- [IAM policy evaluation logic](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html)
- [Cross-account policy evaluation](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic-cross-account.html)
- [Request context](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic_policy-eval-reqcontext.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: AWS Organizations a accounts](aws-organizations-accounts.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: VPC, subnets a route tables →](vpc-subnets-route-tables.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
