# KMS a Secrets Manager

AWS Key Management Service riadi cryptographic key resources, key material a authorization pre cryptographic operations. AWS Secrets Manager riadi versionované secret values, staging labels, retrieval, replication a rotation credentials v target systéme. Veta „secret je zašifrovaný“ preto nestačí.

```text
protected-value or credential intent
→ exact KMS key, secret, target and consumer
→ authorization and key state
→ cryptographic or secret retrieval operation
→ target credential mutation
→ secret version and staging-label transition
→ consumer refresh and loaded state
→ old generation revocation
→ business validation and audit
```

KMS decrypt success nepreukazuje, že application načítala správnu secret version. `AWSCURRENT` nepreukazuje, že target service credentials fungujú ani že warm processes opustili old generation.

## 1. Exact protected-value subject

Atlas Payments používa KMS key `key-pay-17`, logical generation `KMS-PAY-17`, material generation `MAT-9`, alias `alias/prod/payments-secrets`, key policy `KPOL-31` a grant set `GRANTSET-12`.

Secret `prod/payments/provider` má `AWSCURRENT=v42`, `AWSPREVIOUS=v41` a rotation candidate `v43/AWSPENDING`. Rotation model používa alternating users `atlas-pay-a` a `atlas-pay-b`. Target credential generation je `CRED-42` a consumers sú ECS API, Lambda settlement worker a reconciliation process.

Forbidden outcomes sú key administrator automatically able to decrypt, alias remap treated as re-encryption, current label pointing to invalid target credential, old credential revoked before consumer refresh and key deletion destroying retained recovery points.

## 2. Logical key, key material, secret version and loaded state

KMS key resource has stable ARN, policy, state, usage, aliases, grants and key-material history. Key material generation can rotate while key ARN remains unchanged. Secret version is immutable value identified by version ID; staging label is mutable pointer. Consumer-loaded state is value held by process, cache or connection pool.

```text
which key ARN authorized operation?
which material generation protected ciphertext?
which secret version has AWSCURRENT?
which credential is accepted by target?
which version is loaded by this process and socket?
```

These are separate questions.

## 3. Envelope encryption

KMS usually protects data keys rather than large payload directly.

```text
GenerateDataKey
→ plaintext data key + encrypted data key
→ local payload encryption
→ erase plaintext key
→ store ciphertext + encrypted data key + context

Decrypt encrypted data key
→ local payload decryption
```

Python example:

```python
from __future__ import annotations

import base64
import json

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
    nonce = AESGCM.generate_key(bit_length=96)[:12]
    cipher = AESGCM(bytes(plaintext_key))
    ciphertext = cipher.encrypt(nonce, b"example-secret", json.dumps(context, sort_keys=True).encode())
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

Example is educational; production code should use AWS Encryption SDK or reviewed cryptographic library and stronger memory/process handling. Encryption context is non-secret and may appear in audit surfaces.

## 4. Key policy and identity policy

Terraform key and alias:

```hcl
resource "aws_kms_key" "payments" {
  description         = "Atlas Payments secret protection"
  enable_key_rotation = true
  rotation_period_in_days = 180
  deletion_window_in_days = 30
  policy = data.aws_iam_policy_document.payments_kms.json

  tags = {
    Generation = "KMS-PAY-17"
  }
}

resource "aws_kms_alias" "payments" {
  name          = "alias/prod/payments-secrets"
  target_key_id = aws_kms_key.payments.key_id
}
```

Key policy must allow account/IAM delegation or direct principals according to design. Identity policy alone cannot bypass missing key-policy path. Permissions boundary, session policy, SCP/RCP, grant constraints, key state and VPC endpoint policy can further restrict request.

Live read-back:

```bash
aws kms describe-key \
  --key-id arn:aws:kms:eu-central-1:100000000042:key/key-pay-17 \
  --region eu-central-1

aws kms get-key-policy \
  --key-id arn:aws:kms:eu-central-1:100000000042:key/key-pay-17 \
  --policy-name default \
  --region eu-central-1

aws kms list-grants \
  --key-id arn:aws:kms:eu-central-1:100000000042:key/key-pay-17 \
  --region eu-central-1
```

Alias is mutable pointer and must not replace key ARN in audit evidence.

## 5. Encryption context as authorization binding

Positive test with non-production ciphertext:

```bash
aws kms decrypt \
  --ciphertext-blob fileb://provider-token.bin \
  --key-id arn:aws:kms:eu-central-1:100000000042:key/key-pay-17 \
  --encryption-context application=payments,environment=prod,purpose=provider-token \
  --region eu-central-1 \
  --query Plaintext \
  --output text >/dev/null
```

Forbidden context:

```bash
aws kms decrypt \
  --ciphertext-blob fileb://provider-token.bin \
  --key-id arn:aws:kms:eu-central-1:100000000042:key/key-pay-17 \
  --encryption-context application=payments,environment=prod,purpose=reporting \
  --region eu-central-1
```

Second request must fail. Ciphertext copy to another tenant or purpose is unusable without exact context.

## 6. KMS rotation is not data re-encryption

Automatic or on-demand material rotation keeps key ID/ARN and old material required for decrypt. Existing ciphertext and encrypted data keys are not rewritten. Alias remap to new logical key also does not re-encrypt data.

Logical-key migration:

```text
create new key and policy
→ authorize consumers/services
→ copy or re-encrypt according to service contract
→ read-back and decrypt validation
→ inventory closure
→ disable old key observation window
→ deletion decision only after recovery proof
```

Key disable or deletion is recovery decision. Before it, inventory S3/EBS/RDS/backups/secrets, cross-account consumers and dormant archives.

## 7. Secrets Manager resource and versions

Terraform secret:

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

Bootstrap secret version should come from controlled pipeline, not plaintext Terraform state. Example CLI for a test secret:

```bash
aws secretsmanager put-secret-value \
  --secret-id prod/payments/provider \
  --client-request-token 11111111-2222-3333-4444-555555555543 \
  --secret-string file://provider-v43.json \
  --version-stages AWSPENDING \
  --region eu-central-1
```

Secret values do not belong in command history. Production uses secure file descriptor/pipeline and redaction.

Version inventory without values:

```bash
aws secretsmanager list-secret-version-ids \
  --secret-id prod/payments/provider \
  --include-deprecated \
  --region eu-central-1
```

## 8. Rotation coordinates store, target and consumers

```text
create candidate secret version
→ set AWSPENDING
→ create or update target credential
→ authenticate candidate and verify privilege
→ move AWSCURRENT
→ consumers refresh values and connections
→ observe mixed cohort
→ revoke old target credential
→ forbidden old-credential test
```

Lambda rotation steps are commonly `createSecret`, `setSecret`, `testSecret`, `finishSecret`; each must be idempotent because retries can occur.

Single-user rotation replaces one credential and can break stale consumers immediately. Alternating users prepare inactive identity and provide overlap window, but require privilege equivalence and explicit old-user retirement.

## 9. Rotation configuration

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

Rotation schedule is not acceptance. Workflow must verify target and consumer-loaded state.

Read-back:

```bash
aws secretsmanager describe-secret \
  --secret-id prod/payments/provider \
  --region eu-central-1 \
  --query '{Arn:ARN,KmsKeyId:KmsKeyId,RotationEnabled:RotationEnabled,Rules:RotationRules,VersionIdsToStages:VersionIdsToStages,Replicas:ReplicationStatus}'
```

## 10. Runtime retrieval and cache

Application should not call Secrets Manager for every request and should not cache forever. Cache contract defines max TTL, jitter, refresh on authentication failure, single-flight refresh, behavior during service outage, loaded version telemetry and connection-pool eviction.

Python retrieval skeleton:

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

Telemetry may log version ID, cache age and process/task identity, never secret value. Authentication failure should invalidate cache and connection pool in bounded manner.

## 11. Cross-account and multi-Region

Cross-account secret retrieval needs caller identity allow, secret resource policy, customer-managed KMS key policy and no explicit deny. AWS managed `aws/secretsmanager` key is not general cross-account key contract.

Secret replication creates regional secret replica, not target database user, application failover or immediate consumer refresh. Each Region has its KMS and endpoint dependencies.

```bash
aws secretsmanager replicate-secret-to-regions \
  --secret-id prod/payments/provider \
  --add-replica-regions Region=eu-west-1,KmsKeyId=arn:aws:kms:eu-west-1:200000000042:key/key-recovery-17 \
  --region eu-central-1
```

DR manifest binds replica version to regional target credential and application generation.

## 12. Worked incident: rotation split-brain

Rotation `ROT-14` prepared `v43` for `atlas-pay-b`. Candidate authenticated and workflow moved `AWSCURRENT` from v42 to v43. Team waited fixed ten minutes and disabled old `atlas-pay-a`.

New ECS tasks worked. Older tasks and some warm Lambda environments still held v42; some processes loaded v43 but connection pools retained old sessions. Secrets Manager showed rotation succeeded.

On-call moved `AWSCURRENT` back to v42, making incident worse because target already rejected `atlas-pay-a`. Store pointer and target truth diverged.

Evidence from `GetSecretValue` CloudTrail, process version telemetry and target audit showed consumer-refresh failure, not KMS or candidate-value failure.

Containment stopped rotation retries and label changes, kept `atlas-pay-b` authoritative, set current to v43 and isolated consumers unable to prove loaded version. Recovery recycled stale cohorts in waves, evicted pools, reconciled payment attempts and revoked old credential only after zero v42 consumers remained.

Acceptance required all approved consumers on v43, target accepting new and rejecting old identity, no duplicate settlement and successful next canary rotation using consumer-loaded-state gate.

## 13. Key retirement

```text
block new encrypt uses
→ inventory ciphertext and service resources
→ migrate or prove decrypt under replacement
→ validate backups and dormant restore
→ disable key
→ observe errors and rollback window
→ schedule deletion only after approval
```

Absence of recent CloudTrail decrypt does not prove quarterly restore or archive dependency does not exist.

## 14. Troubleshooting order

KMS AccessDenied: actual caller/session → key ARN/Region/state → key policy → IAM/boundary/SCP → grants → context → endpoint policy. Secret timeout: DNS/route/NAT/endpoint/SG → SDK timeout. Old credential: secret stages → loaded version → pool/session lifetime → target accepted principals.

## Kontrolné otázky

1. What is the difference between key resource and material generation?
2. Why does key rotation not re-encrypt existing data?
3. How does encryption context bind ciphertext?
4. Why is alias not audit identity?
5. Which three systems must secret rotation coordinate?
6. What does AWSCURRENT prove and not prove?
7. Why can fixed rotation delay be unsafe?
8. What telemetry proves consumer-loaded version?
9. How does regional replica differ from regional target credential?
10. Which forbidden test closes rotation recovery?

## Oficiálna dokumentácia

- [AWS KMS Developer Guide](https://docs.aws.amazon.com/kms/latest/developerguide/overview.html)
- [KMS key policies](https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html)
- [KMS grants](https://docs.aws.amazon.com/kms/latest/developerguide/grants.html)
- [Rotate KMS keys](https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
- [Rotate secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)
- [Secrets Manager caching](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_cache-python.html)
- [Replicate secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/replicate-secrets.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: AWS Systems Manager](systems-manager.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: AWS Backup →](aws-backup.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
