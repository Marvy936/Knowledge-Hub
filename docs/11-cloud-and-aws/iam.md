# IAM

AWS Identity and Access Management (IAM) riadi, kto alebo čo môže poslať konkrétny AWS API request na konkrétny resource a za akých podmienok. IAM nie je iba zoznam používateľov a permissions. Je to policy-evaluation systém založený na principal identity, request contexte, explicitných grants, permissions envelopes a explicit deny pravidlách.

## 1. Authentication a authorization

- **Authentication** určuje identitu principalu.
- **Authorization** vyhodnocuje, či autentifikovaný request môže vykonať požadovanú action nad resource-om.

Typický request obsahuje:

```text
principal
+ action
+ resource
+ request context
+ applicable policies
→ allow alebo deny
```

## 2. IAM principals

AWS request môže vykonať napríklad:

- AWS account root user,
- IAM user,
- IAM role session,
- federovaný user/session,
- AWS service principal,
- workload používajúci temporary credentials,
- principal z iného AWS accountu.

Principal identity nie je to isté ako permission. Role môže existovať bez možnosti vykonať relevantnú action a resource policy môže povoľovať iba presne určený principal.

## 3. Root user

Root user má zvláštnu account-level identitu a nesmie byť bežným operations účtom.

Minimálny model:

- phishing-resistant MFA,
- žiadne root access keys,
- bezpečná custody credentials,
- alerting na root login a API použitie,
- dokumentovaný break-glass proces,
- pravidelný test recovery kontaktov.

Niektoré account-level operácie vyžadujú root usera; to nie je dôvod používať ho denne.

## 4. IAM users

IAM user je dlhodobejšia identity v jednom account-e. Pre workforce access sa preferuje federation a temporary role sessions.

IAM users zostávajú relevantné najmä pre legacy alebo výnimočné machine integrations, keď nie je dostupný vhodnejší role-based model. V takom prípade potrebujú:

- explicitného ownera,
- minimálne permissions,
- rotation a disable proces,
- credential-last-used monitoring,
- zákaz zdieľania credentials.

## 5. IAM roles

IAM role nemá vlastné permanentné credentials. Principal ju prevezme cez AWS Security Token Service (STS) a dostane temporary session credentials.

Role má dve odlišné policy vrstvy:

1. **Trust policy** — kto alebo čo môže role assume-nuť.
2. **Permissions policies** — čo smie vzniknutá role session robiť.

Trust bez permissions nevytvorí useful access. Permissions bez trustu nemožno použiť.

## 6. STS a temporary credentials

STS vydáva dočasné credentials:

```text
access key ID
+ secret access key
+ session token
+ expiration
```

Výhody:

- obmedzená lifetime,
- session-level audit identity,
- federation a cross-account access,
- jednoduchšia rotation než pri static keys,
- možnosť session policies, tags a MFA conditions.

Dočasné credentials sa stále môžu zneužiť počas ich platnosti. Potrebujú least privilege, krátku session duration a detekciu anomálií.

## 7. Identity-based policies

Identity policy je pripojená k userovi, group alebo role a typicky obsahuje:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::example-bucket/reports/*"
    }
  ]
}
```

Kľúčové prvky:

- `Effect`,
- `Action` alebo `NotAction`,
- `Resource` alebo `NotResource`,
- `Condition`,
- pri resource policies aj `Principal`.

## 8. Resource-based policies

Resource policy je uložená pri resource-e, napríklad:

- S3 bucket policy,
- KMS key policy,
- SNS/SQS policy,
- Secrets Manager resource policy,
- IAM role trust policy.

Resource policy je kritická pre cross-account access. Samotná identity policy v source account-e zvyčajne nestačí; target resource/account musí cross-account principal tiež dôveryhodne povoliť.

## 9. Policy evaluation

Základný model:

```text
implicit deny
→ hľadaj applicable explicit deny
→ hľadaj required explicit allow
→ vyhodnoť permissions envelopes a request conditions
→ allow alebo deny
```

Pravidlá:

- všetko je implicitne denied, kým neexistuje applicable allow,
- explicit deny prevažuje nad allow,
- identity a resource policies môžu v určitých same-account scenároch tvoriť union grants,
- permissions boundary, session policy, SCP alebo RCP môžu zúžiť effective permissions,
- cross-account request musí prejsť policy evaluation v source aj target boundary podľa konkrétneho modelu.

Poradie textu policy statements neurčuje prioritu.

## 10. Permissions boundaries

Permissions boundary je maximum, ktoré identity-based policies môžu userovi alebo role udeliť.

```text
identity policy allow
∩ permissions boundary allow
= effective identity permissions
```

Boundary sama access neudeľuje. Je vhodná pre delegated IAM administration, ale zle navrhnutý resource-policy alebo pass-role model môže stále vytvoriť privilege escalation.

## 11. Session policies

Session policy zúži permissions konkrétnej role alebo federated session. Nemôže rozšíriť permissions nad role identity policy a ostatné applicable guardrails.

Použitie:

- per-session scope,
- brokered access,
- temporary task-specific permissions,
- tenant alebo project context.

## 12. SCP a RCP

V AWS Organizations:

- **Service Control Policy (SCP)** obmedzuje maximálne permissions principals v member accounts.
- **Resource Control Policy (RCP)** obmedzuje maximálne permissions nad podporovanými resources.

Tieto policies nie sú grants. Request stále potrebuje allow z IAM/resource policy vrstvy.

## 13. Conditions a request context

Conditions môžu používať napríklad:

- principal ARN alebo organization ID,
- source VPC/VPC endpoint,
- source IP,
- MFA presence,
- requested Region,
- resource tags a principal tags,
- encryption context,
- transport security,
- token audience alebo source account.

Pri `IfExists`, negated operators a multivalue set operators treba analyzovať missing-key semantics. Chybná condition môže ticho otvoriť alebo zablokovať širší scope.

## 14. Attribute-based access control

ABAC používa attributes, typicky tags, na dynamické permissions:

```text
principal tag Project=A
resource tag Project=A
→ povoliť project-scoped action
```

ABAC znižuje počet statických policies, ale vyžaduje:

- governance tag keys/values,
- kontrolu tag mutation permissions,
- onboarding a cleanup lifecycle,
- audit resources bez tags,
- ochranu privileged tags.

## 15. Cross-account role model

Preferovaný model:

```text
human/workload identity v account A
→ sts:AssumeRole
→ target role v account B
→ temporary session
→ resource access
```

Over:

- source permission na `sts:AssumeRole`,
- target trust policy,
- external ID pri vhodných third-party prípadoch,
- session tags/source identity,
- permissions boundary a SCP,
- target resource policy/KMS key policy.

## 16. Service roles a service-linked roles

AWS service môže potrebovať role na vykonávanie actions v customer account-e.

- **Service role** spravuje zákazník alebo deployment workflow.
- **Service-linked role** je previazaná s konkrétnou AWS službou a má service-defined trust/lifecycle model.

Pred deletion over dependencies; odstránenie role môže rozbiť service reconciliation.

## 17. `iam:PassRole`

`iam:PassRole` umožní principalu odovzdať role AWS službe. Je to častá privilege-escalation cesta.

Bezpečný contract obmedzuje:

- presné role ARNs,
- povolenú destination service cez condition,
- kto môže meniť trust a permissions danej role,
- tags/path a deployment ownership.

## 18. Access keys a credential chain

AWS SDK/CLI môže hľadať credentials v rôznych zdrojoch:

- environment variables,
- shared config/credentials files,
- IAM Identity Center,
- web identity,
- ECS task role,
- EC2 instance profile,
- explicitný credential provider.

Pri incidente najprv zisti skutočne použitú identitu:

```bash
aws sts get-caller-identity
```

Nehádaj podľa lokálneho profile name.

## 19. Federation a IAM Identity Center

Workforce access má typicky používať central identity provider a federované role sessions.

IAM Identity Center môže poskytovať:

- users/groups alebo external IdP federation,
- permission sets,
- account assignments,
- temporary CLI/console sessions,
- central lifecycle a audit.

Federation nevylučuje AWS-side least privilege. Permission set sa stále mapuje na IAM role/policies v target accounts.

## 20. Least privilege workflow

Praktický postup:

1. identifikuj presné API actions a resources,
2. začni úzkym scope-om,
3. používaj conditions,
4. testuj pozitívne aj negatívne paths,
5. sleduj CloudTrail a AccessDenied context,
6. odstráň unused permissions,
7. reviduj pri zmene workloadu.

AWS managed policy je vhodná na bootstrap alebo štandardný job function, ale nemusí byť vhodná ako finálny production least-privilege contract.

## 21. IAM Access Analyzer

Access Analyzer pomáha napríklad:

- identifikovať external access z resource policies,
- validovať policy syntax a security findings,
- generovať candidate policies z CloudTrail activity,
- analyzovať unused access podľa dostupných capabilities.

Finding nie je automaticky incident. Potrebuje business ownership a intended-access kontext.

## 22. Audit evidence

Zachovaj:

- caller ARN a account ID,
- assumed-role session name/source identity,
- request ID a UTC timestamp,
- CloudTrail event,
- identity/resource policy versions,
- SCP/RCP/boundary/session policy,
- relevantné tags a request context,
- credential source a expiration.

## 23. Troubleshooting `AccessDenied`

Postup:

```text
správny account/Region/endpoint?
→ skutočný caller identity?
→ presná action/resource ARN?
→ explicit deny?
→ identity/resource allow?
→ boundary/session/SCP/RCP?
→ KMS alebo dependent-service permission?
→ trust/pass-role/cross-account boundary?
→ condition keys a tags?
```

Bežné príčiny:

- assumed iná role než očakávaná,
- action používa subresource alebo dependent action,
- resource ARN má chybný format,
- KMS key policy nepovoľuje použitie key,
- SCP explicitne denyuje Region/service,
- permissions boundary zúžila role,
- trust policy nepovoľuje principal/session tags,
- eventual propagation po policy zmene,
- service vykonáva action cez inú role.

## 24. Anti-patterny

### Long-lived access keys pre ľudí

Zvyšujú credential leakage a rotation risk.

### Wildcard `Action: "*"`, `Resource: "*"`

Rozširuje blast radius a komplikuje audit.

### `AdministratorAccess` ako troubleshooting oprava

Maskuje root cause a vytvára trvalú privilege escalation.

### SCP považovaný za permission grant

SCP iba zúži maximum.

### Kontrola iba identity policy

Access môže blokovať resource policy, key policy, boundary, session policy alebo organization guardrail.

### Role trust s príliš širokým principalom

Môže umožniť neplánované cross-account prevzatie role.

## 25. Kontrolné otázky

1. Aký je rozdiel medzi authentication a authorization?
2. Ako sa líši trust policy od permissions policy role?
3. Prečo explicit deny prevažuje nad allow?
4. Čo permissions boundary robí a čo nerobí?
5. Ako funguje cross-account AssumeRole?
6. Prečo je `iam:PassRole` citlivá permission?
7. Kedy použiť ABAC a aké má riziká?
8. Ako zistíš skutočnú CLI identitu?
9. Ktoré vrstvy preveríš pri `AccessDenied`?
10. Prečo federation sama nezaručuje least privilege?

## Glossary impact

Relevantné pojmy: IAM principal, IAM user, IAM role, role trust policy, identity-based policy, resource-based policy, explicit deny, implicit deny, permissions boundary, session policy, STS session, temporary credentials, AssumeRole, cross-account role, ABAC, IAM Identity Center, service-linked role, `iam:PassRole` a IAM Access Analyzer.

## Oficiálna dokumentácia

- [How IAM works](https://docs.aws.amazon.com/IAM/latest/UserGuide/intro-structure.html)
- [Policy evaluation logic](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html)
- [IAM JSON policy reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html)
- [IAM best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: AWS Organizations a accounts](aws-organizations-accounts.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: VPC, subnets a route tables →](vpc-subnets-route-tables.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
