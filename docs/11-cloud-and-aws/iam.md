# IAM

AWS Identity and Access Management rozhoduje, či konkrétny authenticated request môže vykonať konkrétnu action nad konkrétnym resource-om v konkrétnom request contexte. IAM preto nie je zoznam users a policies. Je to authorization graph, v ktorom sa stretávajú principal/session identity, identity-based grants, resource policies, trust, permissions boundaries, session policies, Organizations guardrails, service-specific policies a explicit denies.

```text
operation intent
→ credential source
→ authenticated principal alebo role session
→ exact API action, resource a context
→ candidate allows
→ permissions envelopes a explicit denies
→ service-specific authorization
→ side effect
→ CloudTrail a business outcome
→ expiry, rotation alebo revocation
```

Najdôležitejší diagnostický princíp je jednoduchý: policy, ktorú si myslíš, že workload používa, nie je dôkaz actual caller identity.

## 1. Exact request subject

Atlas incident `IAM-PAY-42` sa týka requestu `kms:Decrypt`. Očakávaný caller je STS session:

```text
arn:aws:sts::100000000042:assumed-role/payments-settlement/POD-7F2
```

Credential mal vzniknúť cez EKS workload identity a session generation `STS-991`, expirovať 28. júla 2026 o 12:00 UTC a volať KMS key `key-pay-42` v `eu-central-1`. Authorization generation zahŕňa identity policy `IP-18`, trust `TP-12`, permissions boundary `PB-WORKLOAD-6`, session policy `SP-7`, SCP/RCP `SCP-PROD-9/RCP-DATA-4` a KMS key policy `KP-22`. Encryption context je `service=payments, purpose=settlement`.

Business outcome je dešifrovať settlement credential a commitnúť operáciu presne raz. Iný workload, tenant, Region alebo stale session musí zostať forbidden.

`AccessDenied` bez caller ARN, action, resource ARN, Regionu, timestampu a request ID nie je dostatočne definovaný incident.

## 2. Authentication a authorization sú dve odlišné otázky

Authentication odpovedá: kto request posiela? Authorization odpovedá: smie táto identity vykonať túto operation?

Role sama neposiela API request. Request posiela konkrétna role session s vlastným session ARN, session name, tags, source identity, policies a expiry. Rovnaká IAM role môže mať súčasne viac sessions s rozdielnymi session policies alebo tags.

Prvý command pri incidente:

```bash
aws sts get-caller-identity
```

Očakávaný výstup:

```json
{
  "UserId": "AROAXXXXXXXXXXXXX:POD-7F2",
  "Account": "100000000042",
  "Arn": "arn:aws:sts::100000000042:assumed-role/payments-settlement/POD-7F2"
}
```

Tento command preukazuje identity použitú AWS CLI credential provider chainom v danom process context-e. Neznamená, že application process používa rovnaký SDK chain. Test sa preto vykonáva priamo v affected containeri alebo runtime-e.

Pri EKS Pode:

```bash
kubectl -n payments exec deploy/settlement-consumer -- \
  aws sts get-caller-identity
```

Profile name, Kubernetes ServiceAccount name ani environment label nie sú náhradou za tento read-back.

## 3. Credential provider chain je runtime dependency

Temporary credentials typicky vzniknú cez federation alebo STS exchange a následne ich SDK vyberie z credential provider chainu.

```text
workload identity binding
→ token alebo certificate
→ STS exchange
→ temporary access key, secret a session token
→ SDK provider selection
→ process-loaded credentials
→ signed request
→ refresh alebo expiry
```

Static environment variables môžu v mnohých SDKs prebiť workload identity provider. Projected web-identity token na filesysteme nepreukazuje, že ho process zvolil. Pri migrácii identity je preto potrebné odstrániť staré environment credentials a sledovať actual caller cohort.

Bezpečná telemetry neobsahuje secret. Môže obsahovať account, assumed-role ARN, session name, source identity, issue/expiry a credential provider type.

## 4. Role má trust contract a permissions contract

Trust policy určuje, kto smie role assume-nuť. Identity permissions role určujú, čo smie vzniknutá session robiť. Obe vrstvy musia fungovať.

Trust policy pre EKS OIDC-style workload binding môže vyzerať takto:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::100000000042:oidc-provider/oidc.eks.eu-central-1.amazonaws.com/id/EXAMPLE"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "oidc.eks.eu-central-1.amazonaws.com/id/EXAMPLE:aud": "sts.amazonaws.com",
          "oidc.eks.eu-central-1.amazonaws.com/id/EXAMPLE:sub": "system:serviceaccount:payments:settlement-consumer"
        }
      }
    }
  ]
}
```

Policy povoľuje iba konkrétny issuer, audience a ServiceAccount subject. Ak namespace alebo ServiceAccount zmeníš, STS exchange zlyhá ešte pred KMS authorization.

Permissions policy role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DecryptSettlementCredential",
      "Effect": "Allow",
      "Action": "kms:Decrypt",
      "Resource": "arn:aws:kms:eu-central-1:100000000042:key/key-pay-42",
      "Condition": {
        "StringEquals": {
          "kms:EncryptionContext:service": "payments",
          "kms:EncryptionContext:purpose": "settlement"
        }
      }
    }
  ]
}
```

Identity policy je candidate allow. KMS key policy, boundary, SCP, session policy a key state stále môžu request odmietnuť.

## 5. Permissions boundary neudeľuje access

Permissions boundary určuje maximum, ktoré môžu identity policies udeliť userovi alebo role. Sama permission nevytvorí. Effective permission je pri bežnom role modeli prienik identity grants a boundary, ďalej obmedzený ďalšími applicable policies.

Boundary pre workload role môže povoliť iba application services a explicitne odmietnuť IAM mutation:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "WorkloadServiceEnvelope",
      "Effect": "Allow",
      "Action": [
        "kms:Decrypt",
        "secretsmanager:GetSecretValue",
        "sqs:ReceiveMessage",
        "sqs:DeleteMessage",
        "sqs:ChangeMessageVisibility"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DenyIdentityMutation",
      "Effect": "Deny",
      "Action": [
        "iam:*",
        "organizations:*"
      ],
      "Resource": "*"
    }
  ]
}
```

Broad `Resource: "*"` v envelope nie je finálny least-privilege grant; konkrétna identity policy musí stále scope-nuť resources. Explicit deny v boundary navyše prevažuje nad candidate allow.

## 6. Session policy zúži jednu STS session

Pri `AssumeRole` možno pridať inline alebo managed session policy. Session získava prienik role permissions a session policy, nie ich union.

Cross-account operator predpokladajme potrebuje iba read-only incident access:

```bash
aws sts assume-role \
  --role-arn arn:aws:iam::100000000042:role/PaymentsIncidentReader \
  --role-session-name INC-884 \
  --duration-seconds 3600 \
  --policy file://incident-session-policy.json
```

`incident-session-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:GetMetricData",
        "logs:StartQuery",
        "logs:GetQueryResults",
        "rds:DescribeDBInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

Role môže mať širšie permissions, ale táto session ich nezíska, ak session policy action neobsahuje. Session policy neumožní action, ktorú role sama nemá.

## 7. Identity a resource policies sa nevyhodnocujú ako jednoduchý súčet

Identity policy je pripojená k userovi, group alebo role. Resource policy je pripojená k resource-u, napríklad S3 bucketu, KMS keyu, Secrets Manager secretu, SQS queue alebo IAM role trustu.

Pri same-account requeste AWS často vyhodnocuje candidate allows z oboch zdrojov, no presná interaction závisí od principal type-u a od toho, či resource policy grantuje IAM role ARN, role-session ARN, user ARN alebo account principal. Permissions boundary a session policy môžu mať pri týchto variantoch rozdielny effect. Diagnostika preto nemá používať univerzálnu vetu „policies sa sčítajú“.

Cross-account access typicky potrebuje povolenie na oboch stranách: source principal musí mať identity allow a target trust/resource policy musí external principal prijať. Organizational guardrails a service-specific key policies môžu access ďalej obmedziť.

## 8. Organizations guardrails sú maximum, nie grant

SCP obmedzuje principals v member accounts a RCP obmedzuje access k podporovaným resources. Ani jedna policy neudeľuje `kms:Decrypt`. Identity/resource allow stále musí existovať.

Zjednodušený request model:

```text
authenticated principal/session
→ identity a resource candidate allows
→ permissions boundary a session envelope
→ SCP principal guardrail
→ RCP resource guardrail
→ KMS key policy/grants and key state
→ explicit deny search
→ allow or deny
```

AWS policy evaluation začína implicit deny, hľadá applicable explicit deny a až potom hodnotí allow podľa policy types a request contextu.

## 9. Conditions sú executable security assumptions

Condition môže používať requested Region, principal tags, resource tags, source VPC endpoint, MFA, TLS, source ARN/account alebo KMS encryption context.

Missing-key semantics sú dôležité. `StringNotEquals`, `IfExists`, multivalue operators a negated conditions môžu pri chýbajúcom context key vytvoriť iný result než intuitívne očakávaš.

Každá security condition potrebuje dve skúšky:

```text
positive request with expected context → Allow
forbidden request with missing or wrong context → Deny
```

Pre KMS:

```bash
aws kms decrypt \
  --ciphertext-blob fileb://settlement-credential.bin \
  --encryption-context service=payments,purpose=settlement \
  --key-id arn:aws:kms:eu-central-1:100000000042:key/key-pay-42 \
  --region eu-central-1 \
  --output text \
  --query Plaintext >/dev/null
```

Forbidden test:

```bash
aws kms decrypt \
  --ciphertext-blob fileb://settlement-credential.bin \
  --encryption-context service=payments,purpose=reporting \
  --key-id arn:aws:kms:eu-central-1:100000000042:key/key-pay-42 \
  --region eu-central-1
```

Druhý command musí zlyhať. Ciphertext a plaintext sa nesmú zapisovať do logov. Test je vhodný iba v izolovanom controlled prostredí s non-production credential blobom.

## 10. ABAC a tag mutation

Attribute-based access control prepája principal tags a resource tags. Napríklad role session s `Project=payments` môže pristupovať iba k resources s rovnakým tagom.

```json
{
  "Effect": "Allow",
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::atlas-evidence/*",
  "Condition": {
    "StringEquals": {
      "aws:ResourceTag/Project": "${aws:PrincipalTag/Project}"
    }
  }
}
```

ABAC je bezpečný iba ak principal nemôže svojvoľne meniť privileged principal alebo resource tag. Permission na tag mutation je preto indirect authorization capability a patrí do reachable-access review.

## 11. `iam:PassRole` je schopnosť odovzdať authority službe

`iam:PassRole` neznamená, že caller sám môže vykonať actions role. Umožní mu nakonfigurovať AWS service tak, aby role použila.

Bezpečná policy obmedzí role path a destination service:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PassOnlyPaymentsRuntimeRolesToLambda",
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "arn:aws:iam::100000000042:role/payments-runtime/*",
      "Condition": {
        "StringEquals": {
          "iam:PassedToService": "lambda.amazonaws.com"
        }
      }
    }
  ]
}
```

Ak caller zároveň môže vytvoriť Lambda function s arbitrary code a pass-nuť high-privilege role, jeho reachable capability zahŕňa permissions tejto role. Least privilege review preto nesmie hodnotiť permissions izolovane.

## 12. Policy simulation a Access Analyzer

IAM simulator je useful pre candidate policy evaluation:

```bash
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::100000000042:role/payments-settlement \
  --action-names kms:Decrypt \
  --resource-arns arn:aws:kms:eu-central-1:100000000042:key/key-pay-42 \
  --context-entries \
    ContextKeyName=kms:EncryptionContext:service,ContextKeyValues=payments,ContextKeyType=string \
    ContextKeyName=kms:EncryptionContext:purpose,ContextKeyValues=settlement,ContextKeyType=string
```

Simulation result `allowed` nie je live request verdict. Simulator nemusí reprodukovať actual credential source, every resource policy, service state alebo all external context. Vždy ho spoj s `get-caller-identity`, live request a CloudTrail.

IAM Access Analyzer môže hľadať external access alebo unused permissions podľa analyzer type-u a coverage. Finding je evidence na review, nie automatický proof exploitability ani business impact.

## 13. CloudTrail a encoded authorization message

CloudTrail event pomáha viazať caller session, event name, resource, Region, request parameters a error. Nie každý sensitive field je uložený a data-event coverage musí byť zapnuté podľa service.

Pri niektorých AWS authorization errors môže response obsahovať encoded authorization failure message. Principal s `sts:DecodeAuthorizationMessage` ho môže dekódovať:

```bash
aws sts decode-authorization-message \
  --encoded-message "$ENCODED_MESSAGE" \
  --query DecodedMessage \
  --output text | jq .
```

Decoded result môže ukázať matched statements a missing permissions. Táto permission je citlivá, pretože sprístupňuje authorization detail; má byť obmedzená na incident role.

## 14. Worked incident: simulator testoval inú identity než affected Pod

Po KMS policy rotation začal subset settlement Podov dostávať `AccessDenied`. Simulator pre role `payments-settlement` ukazoval allow a nové Pody fungovali.

Hypotézy zahŕňali stale session, identity policy, boundary, SCP/RCP, KMS key policy, encryption context, trust subject, wrong key/Region a VPC endpoint policy. Rozdelenie cohorty podľa Pod start time ukázalo, že zlyhávali iba staršie Pody.

`aws sts get-caller-identity` vykonaný v affected containeri vrátil legacy IAM usera, nie assumed role session. Starý Deployment template obsahoval environment access keys a SDK credential chain ich uprednostnil pred web identity. Simulator testoval novú role, teda iný principal. KMS key policy správne legacy usera odmietla.

Containment nepridalo wildcard do key policy. Legacy access key sa deaktivoval, affected cohort sa izoloval a settlement queue dostala bounded processing, aby nevznikol retry storm. CloudTrail sa skontroloval pre ďalšie použitia legacy keyu.

Recovery odstránila static credentials zo source Secretu aj Pod template-u, vytvorila novú workload generation a overila actual caller ARN. Allowed decrypt prešiel iba s expected encryption contextom. Iná role, purpose a Region ostali denied. Pending settlements sa reconciliovali podľa idempotency keyu.

Closure vyžadovala, aby každý accepted Pod používal expected STS session, legacy key bol odmietnutý a payment settlement skončil presne raz. Policy nebola rozšírená na maskovanie root cause.

## 15. Revocation nie je iba edit policy

Policy update môže zablokovať nové requesty, no temporary session alebo application connection môže žiť do expiry alebo ďalšieho authorization pointu. Static access key je revoke-nutý až po disable/delete a forbidden request teste. Secret credential môže zostať validný v external targete aj po odstránení Secrets Manager version labelu.

Revocation closure:

```text
old credential or trust path identified
→ new issuance blocked
→ existing sessions and caches inventoried
→ target credential disabled or expired
→ fresh forbidden request fails
→ remaining business operations reconciled
→ evidence retained
```

## 16. Authorization review ako code a experiment

Policy-as-code pipeline má parse a lint gate, simulation fixtures a live canary. Fixtures zahŕňajú exact allow, wrong resource, wrong Region, missing tag, wrong encryption context a forbidden principal.

Nie je cieľom vytvoriť policy s najmenším počtom znakov. Cieľom je presne obmedziť reachable capabilities a zachovať operability pri rotation, incident response a recovery.

## Kontrolné otázky

1. Ktorý exact principal alebo session poslal request?
2. Odkiaľ SDK načítal credentials?
3. Aký rozdiel je medzi trust a permissions policy role?
4. Prečo permissions boundary access neudeľuje?
5. Ako session policy mení jednu assumed-role session?
6. Prečo identity a resource policies nemožno vždy jednoducho sčítať?
7. Ktorý request context podmieňuje KMS decrypt?
8. Ako tag mutation mení ABAC authority?
9. Akú indirect capability vytvára `iam:PassRole`?
10. Čo musí preukázať revocation closure?

## Oficiálna dokumentácia

- [How IAM works](https://docs.aws.amazon.com/IAM/latest/UserGuide/intro-structure.html)
- [Policy evaluation logic](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html)
- [Identity-based and resource-based policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html)
- [Permissions boundaries](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html)
- [Session policies](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html)
- [IAM JSON policy reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html)
- [AWS STS CLI reference](https://docs.aws.amazon.com/cli/latest/reference/sts/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: AWS Organizations a accounts](aws-organizations-accounts.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: VPC, subnets a route tables →](vpc-subnets-route-tables.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
