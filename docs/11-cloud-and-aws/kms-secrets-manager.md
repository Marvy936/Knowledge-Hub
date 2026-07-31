# KMS a Secrets Manager

AWS Key Management Service riadi cryptographic key resources, key material a authorization pre cryptographic operations. AWS Secrets Manager riadi versionované secret values, staging labels, retrieval, replication a rotation credentials v target systéme. Veta „secret je zašifrovaný“ preto nestačí: treba vedieť, ktorý key a material generation chránia hodnotu, ktorý principal môže vykonať operáciu, ktorá secret version je current, čo target systém akceptuje a čo konkrétny process skutočne načítal.

```text
protected-value alebo credential intent
→ exact KMS key, secret, target a consumer
→ authorization a key state
→ cryptographic alebo secret retrieval operation
→ target credential mutation
→ secret version a staging-label transition
→ consumer refresh a loaded state
→ old generation revocation
→ business validation a audit
```

KMS decrypt success nepreukazuje, že application načítala správnu secret version. Label `AWSCURRENT` nepreukazuje, že target credentials fungujú ani že warm processes a connection pools opustili predchádzajúcu generation.

## 1. Exact protected-value subject

Atlas Payments používa KMS key `key-pay-17`, logical generation `KMS-PAY-17`, material generation `MAT-9`, alias `alias/prod/payments-secrets`, key policy `KPOL-31` a grant set `GRANTSET-12`. Key ARN je authoritative cryptographic identity; alias je mutable lookup pointer a nesmie nahradiť ARN v incident evidence alebo migration inventory.

Secret `prod/payments/provider` má `AWSCURRENT=v42`, `AWSPREVIOUS=v41` a rotation candidate `v43/AWSPENDING`. Rotation model používa alternating users `atlas-pay-a` a `atlas-pay-b`. Target credential generation je `CRED-42` a consumers sú ECS API, Lambda settlement worker a reconciliation process.

Forbidden outcomes zahŕňajú key administrator automaticky schopného decryptovať payload, alias remap interpretovaný ako re-encryption, current label ukazujúci na neplatný target credential, old credential revoked pred consumer refresh a key deletion, ktorá zničí retained recovery points.

## 2. Logical key, key material, secret version a loaded state

KMS key resource má stabilný ARN, policy, state, usage, aliases, grants a históriu key materialu. Material generation sa môže zmeniť, zatiaľ čo key ARN ostáva rovnaký. Secret version je immutable value identifikovaná version ID; staging label je mutable pointer medzi versions. Consumer-loaded state je hodnota držaná processom, cache alebo connection poolom.

```text
ktorý key ARN autorizoval operáciu?
ktorý material generation chránil ciphertext?
ktorá secret version nesie AWSCURRENT?
ktorý credential akceptuje target?
ktorú version drží tento process a socket?
```

Tieto otázky majú rozdielne authoritative systems. KMS odpovie na key a cryptographic operation, Secrets Manager na version a labels, target audit na accepted credentials a process telemetry na loaded version. Ich zamieňanie vytvára rotation incidenty, v ktorých je control plane green, ale workload autentifikácia zlyháva.

## 3. Envelope encryption

KMS zvyčajne nechráni veľký payload priamym `Encrypt` callom. Vytvorí data key, vráti jeho plaintext pre lokálnu symetrickú operáciu a encrypted copy na uloženie vedľa ciphertextu. Plaintext data key musí mať krátky lifetime a encrypted data key musí zostať viazaný na rovnaký encryption context ako payload.

```text
GenerateDataKey
→ plaintext data key + encrypted data key
→ local payload encryption
→ erase plaintext key
→ store ciphertext + encrypted data key + context

Decrypt encrypted data key
→ local payload decryption
```

Nasledujúci príklad ukazuje mechanizmus, nie production-ready key-management framework. Dvanásťbajtový nonce vzniká cez cryptographically secure random source; `AESGCM.generate_key` slúži na AES keys a nie na 96-bitové nonces.

```python
from __future__ import annotations

import base64
import json
import os

import boto3
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

kms = boto3.client("kms", region_name="eu-central-1")

context = {
    "application": "payments",
    "environment": "prod",
    "purpose": "provider-token",
}

response = kms.generate_data_key(
    KeyId="arn:aws:kms:eu-central-1:100000000042:key/key-pay-17",
    KeySpec="AES_256",
    EncryptionContext=context,
)

plaintext_key = bytearray(response["Plaintext"])
encrypted_key = response["CiphertextBlob"]

try:
    nonce = os.urandom(12)
    cipher = AESGCM(bytes(plaintext_key))
    associated_data = json.dumps(context, sort_keys=True).encode()
    ciphertext = cipher.encrypt(nonce, b"example-secret", associated_data)
finally:
    for i in range(len(plaintext_key)):
        plaintext_key[i] = 0

record = {
    "encryptedDataKey": base64.b64encode(encrypted_key).decode(),
    "nonce": base64.b64encode(nonce).decode(),
    "ciphertext": base64.b64encode(ciphertext).decode(),
    "context": context,
}
```

Production code má používať AWS Encryption SDK alebo iný reviewed cryptographic framework, pretože memory zeroing v managed runtime nie je úplná garancia a record format potrebuje authentication, versioning a error handling. Encryption context nie je secret a môže sa objaviť v CloudTrail; nesmie preto obsahovať password, token alebo osobné údaje.

## 4. Key policy, IAM a effective authorization

KMS authorization sa nedá odvodiť iba z jednej identity policy. Key policy musí priamo povoliť principal alebo vytvoriť account-level delegation path do IAM. Permissions boundary, session policy, SCP alebo RCP, grants, encryption-context conditions, key state a VPC endpoint policy môžu request ďalej obmedziť.

```hcl
resource "aws_kms_key" "payments" {
  description             = "Atlas Payments secret protection"
  enable_key_rotation     = true
  rotation_period_in_days = 180
  deletion_window_in_days = 30
  policy                  = data.aws_iam_policy_document.payments_kms.json

  tags = {
    Generation = "KMS-PAY-17"
  }
}

resource "aws_kms_alias" "payments" {
  name          = "alias/prod/payments-secrets"
  target_key_id = aws_kms_key.payments.key_id
}
```

Terraform plan a apply vytvoria desired key resource a alias mapping. Effective read-back musí používať key ARN a actual caller context:

```bash
aws sts get-caller-identity

aws kms describe-key \
  --key-id arn:aws:kms:eu-central-1:100000000042:key/key-pay-17 \
  --region eu-central-1 \
  --query 'KeyMetadata.{Arn:Arn,State:KeyState,Usage:KeyUsage,Origin:Origin,MultiRegion:MultiRegion}' \
  --output yaml

aws kms get-key-policy \
  --key-id arn:aws:kms:eu-central-1:100000000042:key/key-pay-17 \
  --policy-name default \
  --region eu-central-1 \
  --query Policy \
  --output text | jq .

aws kms list-grants \
  --key-id arn:aws:kms:eu-central-1:100000000042:key/key-pay-17 \
  --region eu-central-1
```

`DescribeKey` preukazuje identity a state, nie permission na decrypt. Policy a grants ukazujú configured authorization paths, ale effective verdict stále závisí od caller session a request context. Alias read-back je užitočný pre lookup, nie ako dôkaz, ktorý logical key historicky chránil ciphertext.

## 5. Encryption context ako authorization binding

Encryption context sa cryptographically viaže k ciphertextu a zároveň môže byť použitý v KMS policy conditions. Positive test preto musí použiť exact context a forbidden test zmeniť tenant, environment alebo purpose bez zmeny ciphertextu.

```bash
aws kms decrypt \
  --ciphertext-blob fileb://provider-token.bin \
  --key-id arn:aws:kms:eu-central-1:100000000042:key/key-pay-17 \
  --encryption-context application=payments,environment=prod,purpose=provider-token \
  --region eu-central-1 \
  --query Plaintext \
  --output text >/dev/null
```

Forbidden context používa rovnaký ciphertext, ale iný purpose:

```bash
aws kms decrypt \
  --ciphertext-blob fileb://provider-token.bin \
  --key-id arn:aws:kms:eu-central-1:100000000042:key/key-pay-17 \
  --encryption-context application=payments,environment=prod,purpose=reporting \
  --region eu-central-1
```

Druhý request musí zlyhať. Úspech prvého callu dokazuje cryptographic a authorization path pre test principal, nie to, že production application používa rovnakú role session alebo context. Runtime test sa preto vykoná aj z workload identity a CloudTrail sa skontroluje bez logovania plaintextu.

## 6. KMS key-material rotation nie je re-encryption

Automatic alebo on-demand rotation mení current key material v rámci rovnakého logical KMS key resource-u. Key ID, ARN, policy a application reference ostávajú rovnaké. AWS KMS pri decrypt operácii vyberie material, ktorý pôvodne ciphertext chránil; existujúce ciphertexts ani data keys sa neprepisujú.

Alias remap na nový logical key je odlišná operácia. Mení, kam alias ukazuje, ale staré ciphertexts zostávajú viazané na pôvodný key ARN. Manual logical-key migration preto potrebuje inventory a service-specific copy alebo re-encryption lifecycle:

```text
create replacement key a policy
→ authorize exact consumers a AWS services
→ copy alebo re-encrypt podľa resource contractu
→ read-back new key identity
→ decrypt/restore validation
→ inventory closure
→ disable old key počas observation window
→ schedule deletion až po recovery approval
```

Key disable alebo deletion je recovery decision. Pred ním sa inventarizujú S3 objects, EBS snapshots, RDS resources, backups, secrets, cross-account consumers a dormant archives. Absencia recent `Decrypt` eventov nepreukazuje, že quarterly restore alebo legal archive starý key nepotrebuje.

## 7. Secrets Manager resource, versions a staging labels

Secret resource drží metadata, KMS key reference, policies, rotation configuration, replicas a version map. Každá secret value má immutable version ID. Labels `AWSCURRENT`, `AWSPREVIOUS` a `AWSPENDING` sú mutable staging pointers; presun labelu nemení target credential ani process cache.

```hcl
resource "aws_secretsmanager_secret" "provider" {
  name       = "prod/payments/provider"
  kms_key_id = aws_kms_key.payments.arn

  recovery_window_in_days = 30

  tags = {
    Generation = "SEC-PROVIDER-22"
  }
}
```

Bootstrap value má prísť z controlled secret pipeline, nie z plaintext Terraform variables alebo state-u. Nasledujúci CLI príklad je vhodný pre testovací secret a používa idempotency token:

```bash
aws secretsmanager put-secret-value \
  --secret-id prod/payments/provider \
  --client-request-token 11111111-2222-3333-4444-555555555543 \
  --secret-string file://provider-v43.json \
  --version-stages AWSPENDING \
  --region eu-central-1
```

Secret value nemá byť command-line argumentom ani súčasťou shell history. Version inventory sa číta bez hodnoty:

```bash
aws secretsmanager list-secret-version-ids \
  --secret-id prod/payments/provider \
  --include-deprecated \
  --region eu-central-1 \
  --output table
```

Tento output preukazuje version-to-label mapu. Nehovorí, či candidate funguje v target systéme alebo ktorú version držia bežiace consumers.

## 8. Rotation koordinuje store, target a consumers

Rotation je distribuovaná business operácia medzi troma authorities. Secrets Manager riadi version a labels, target systém riadi platnosť credentials a consumers držia loaded values a sessions. Úspech jednej vrstvy nesmie byť interpretovaný ako úspech celého lifecycle-u.

```text
create candidate secret version
→ attach AWSPENDING
→ create alebo update target credential
→ authenticate candidate a verify privilege
→ move AWSCURRENT
→ consumers refresh values a connections
→ observe mixed cohort
→ revoke old target credential
→ forbidden old-credential test
```

Lambda rotation steps sú typicky `createSecret`, `setSecret`, `testSecret` a `finishSecret`. Každý step musí byť idempotentný, pretože retry môže znova doručiť rovnaký token a stage. Single-user rotation mení jedno credential a môže okamžite zlomiť stale consumers. Alternating-users model pripraví neaktívnu identity a poskytne overlap window, ale vyžaduje privilege equivalence, loaded-version telemetry a explicitné retirement pravidlo.

## 9. Rotation schedule, execution a read-back

Rotation schedule určuje, kedy môže workflow začať a aké má duration window. Nie je to acceptance oracle. Successful invocation môže skončiť s validným labelom, ale nefunkčným target credentialom alebo stale consumers.

```hcl
resource "aws_secretsmanager_secret_rotation" "provider" {
  secret_id           = aws_secretsmanager_secret.provider.id
  rotation_lambda_arn = aws_lambda_function.rotate_provider.arn

  rotation_rules {
    automatically_after_days = 30
    duration                 = "2h"
  }
}
```

Read-back oddelí rotation configuration, labels a regional replicas:

```bash
aws secretsmanager describe-secret \
  --secret-id prod/payments/provider \
  --region eu-central-1 \
  --query '{Arn:ARN,KmsKeyId:KmsKeyId,RotationEnabled:RotationEnabled,Rules:RotationRules,VersionIdsToStages:VersionIdsToStages,Replicas:ReplicationStatus}' \
  --output yaml
```

`RotationEnabled=true` dokazuje iba configuration. `AWSCURRENT=v43` dokazuje pointer transition. Target login s v43, process telemetry a forbidden login s v42 dokazujú operational completion. Ďalšia canary rotation alebo retry rovnakého rotation tokenu musí zostať idempotentný.

## 10. Runtime retrieval, cache a connection lifetime

Application nemá volať Secrets Manager pri každom requeste, ale nesmie cache držať bez hranice. Cache contract definuje TTL, jitter, single-flight refresh, refresh pri authentication failure, behavior počas Secrets Manager outage, loaded-version telemetry a connection-pool eviction.

```python
from __future__ import annotations

import json
import time
from threading import Lock

import boto3

client = boto3.client("secretsmanager", region_name="eu-central-1")
_lock = Lock()
_cache: dict[str, object] = {"expires": 0.0, "version": None, "value": None}


def provider_credentials() -> tuple[dict[str, str], str]:
    now = time.monotonic()
    if now < float(_cache["expires"]):
        return _cache["value"], str(_cache["version"])

    with _lock:
        now = time.monotonic()
        if now >= float(_cache["expires"]):
            response = client.get_secret_value(
                SecretId="prod/payments/provider",
                VersionStage="AWSCURRENT",
            )
            _cache.update(
                expires=now + 300,
                version=response["VersionId"],
                value=json.loads(response["SecretString"]),
            )

    return _cache["value"], str(_cache["version"])
```

Ukážka demonštruje bounded cache a version telemetry, nie kompletný production client. V praxi sa má použiť AWS-supported caching component alebo reviewed wrapper s metrics, error handling a secure memory modelom. Telemetry môže logovať version ID, cache age a task/Pod identity, nikdy secret value.

Refresh secretu ešte nemusí ukončiť staré database alebo provider sessions. Authentication failure má invalidovať cache aj relevantný connection pool v bounded režime, aby tisíce requestov nevytvorili refresh stampede.

## 11. Cross-account a multi-Region hranice

Cross-account retrieval potrebuje caller identity allow, secret resource policy, customer-managed KMS key policy a absenciu explicit deny v Organizations alebo endpoint policy. AWS managed `aws/secretsmanager` key nie je všeobecný cross-account cryptographic contract pre customer-designed sharing.

Secret replication vytvorí regional secret replica a version propagation path. Nevytvorí regional database user, provider credential, application failover ani okamžitý consumer refresh. Každý Region má vlastný endpoint, KMS dependency, target credential a runtime generation.

```bash
aws secretsmanager replicate-secret-to-regions \
  --secret-id prod/payments/provider \
  --add-replica-regions Region=eu-west-1,KmsKeyId=arn:aws:kms:eu-west-1:200000000042:key/key-recovery-17 \
  --region eu-central-1
```

DR manifest musí preto viazať replica version na regional target credential a application release. Recovery test načíta replica secret, autentifikuje sa k regional targetu a vykoná business operation; green replication status sám nestačí.

## 12. Worked incident: rotation split-brain

Rotation `ROT-14` pripravila v43 pre `atlas-pay-b`. Candidate authentication prešla a workflow presunul `AWSCURRENT` z v42 na v43. Tím potom čakal fixných desať minút a deaktivoval starý `atlas-pay-a`.

New ECS tasks fungovali, ale older tasks a warm Lambda environments držali v42. Časť processov načítala v43, no ich connection pools stále používali sessions vytvorené so starým credentialom. Secrets Manager ukazoval successful rotation, pretože jeho store a labels boli konzistentné.

On-call presunul `AWSCURRENT` späť na v42, čím incident zhoršil: target už `atlas-pay-a` odmietal. Store pointer a target authority sa rozišli. CloudTrail `GetSecretValue`, process version telemetry a target authentication audit ukázali consumer-refresh failure, nie KMS alebo candidate-value failure.

Containment zastavil rotation retries a ďalšie label changes, ponechal `atlas-pay-b` ako target authority a izoloval consumers, ktoré nevedeli preukázať loaded version. Recovery vrátila `AWSCURRENT` na v43, recyklovala stale cohorts vo vlnách, evictovala connection pools a reconciliovala payment attempts. Old credential sa revoked až po nulovom počte v42 consumers.

Acceptance vyžadovala všetky approved consumers na v43, target accepting new a rejecting old identity, nulový duplicate settlement a successful next canary rotation s loaded-state gate. Second operation zopakovala refresh a pool eviction bez ďalšieho side effectu.

## 13. Key retirement ako recovery-sensitive operácia

Key retirement začína zastavením nových encrypt uses, nie okamžitým disable alebo deletion. Inventory musí pokryť active resources, snapshots, backup copies, cross-account integrations a dormant archives. Každý subject potrebuje replacement key alebo preukázanú decrypt/restore cestu.

```text
block new encrypt uses
→ inventory ciphertext a service resources
→ migrate alebo prove decrypt under replacement
→ validate backups a dormant restore
→ disable key
→ observe errors počas rollback window
→ schedule deletion až po approval
```

Disable je reverzibilný observation gate; scheduled deletion má časové okno, ale po dokončení je cryptographic loss nezvratný. Absencia recent CloudTrail decryptov nie je closure, pretože quarterly restore alebo legal archive sa v bežnom observation window nemusí objaviť. Forbidden test musí preukázať, že žiadny approved recovery point nezávisí od retiring key.

## 14. Troubleshooting podľa prvej rozhodujúcej boundary

Pri KMS `AccessDenied` sa najprv fixuje actual caller a session, key ARN, Region a key state. Potom sa analyzuje key policy, IAM a boundary/SCP/RCP layers, grants, encryption context a endpoint policy. Broad allow bez tejto postupnosti môže nechať pôvodný deny nedotknutý a zároveň zväčšiť privilege surface.

Pri Secrets Manager timeoute sa oddeľuje DNS, route, NAT alebo VPC endpoint, security policy a SDK timeout od authorization alebo value problému. Pri old credential incidente sa porovná version-to-label map, process-loaded version, cache age, pool/session lifetime a target accepted principals. Recovery sa uzatvára až positive retrieval/authentication testom, forbidden old-generation testom a fresh-process second operation.

## Kontrolné otázky

1. Aký je rozdiel medzi key resource a material generation?
2. Prečo key rotation nere-encryptuje existujúce dáta?
3. Ako encryption context viaže ciphertext k účelu alebo tenantovi?
4. Prečo alias nie je dostatočná audit identity?
5. Ktoré tri authorities musí secret rotation koordinovať?
6. Čo `AWSCURRENT` dokazuje a čo nedokazuje?
7. Prečo je fixed delay pred revocation nebezpečný?
8. Ktorá telemetry preukazuje consumer-loaded version?
9. Ako sa regional secret replica líši od regional target credentialu?
10. Ktorý forbidden test uzatvára rotation recovery?

## Oficiálna dokumentácia

- [AWS KMS Developer Guide](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html)
- [KMS key policies](https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html)
- [KMS grants](https://docs.aws.amazon.com/kms/latest/developerguide/grants.html)
- [Rotate KMS keys](https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html)
- [List KMS key rotations](https://docs.aws.amazon.com/kms/latest/developerguide/list-rotations.html)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
- [Rotate secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)
- [Alternating users rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/tutorials_rotation-alternating.html)
- [Secrets Manager caching](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_cache-python.html)
- [Replicate secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/replicate-secrets.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Systems Manager](systems-manager.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: AWS Backup →](aws-backup.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
