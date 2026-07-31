# CloudOps hands-on labs

Hands-on lab nie je zoznam príkazov na skopírovanie. Je to controlled experiment, v ktorom čitateľ vytvorí presný subject, zavedie jednu známu failure cause, zachová evidence, rozlíši hypotézy, vykoná minimálnu authoritative opravu a preukáže pôvodný aj zakázaný outcome. Každý lab sa vykonáva v sandbox account-e alebo inom explicitne izolovanom prostredí. Production account, reálne customer data a reálne payment credentials sú okamžité stop conditions.

```text
lab manifest a cost/safety boundary
→ identity, account a Region preflight
→ reproducible baseline
→ exact fault injection
→ symptom a competing hypotheses
→ discriminating commands a observations
→ evidence-preserving containment
→ authoritative recovery
→ positive, forbidden a second-run validation
→ dependency-aware cleanup a residual-resource proof
```

Príkaz má v lab-e hodnotu iba vtedy, keď je vysvetlené, čo jeho output dokazuje a čo ešte nedokazuje.

## 1. Lab manifest a preflight

Každý lab začína versionovaným manifestom. Nasledujúci príklad používa fiktívny sandbox account a nízky cost limit:

```yaml
labId: AWS-LAB-001
objective: Diagnose an IAM/KMS denial from the actual workload identity
accountId: "111122223333"
region: eu-central-1
owner: marvy
maximumDurationMinutes: 60
budgetLimitUsd: 10
requiredTags:
  Lab: AWS-LAB-001
  Owner: marvy
  ExpiresAt: "2026-07-31T12:00:00Z"
stopConditions:
  - caller account does not equal 111122223333
  - configured region does not equal eu-central-1
  - a command references a production ARN
  - a resource lacks the Lab and Owner tags
cleanupRequired: true
```

Pred prvou mutation over identity a Region:

```bash
set -euo pipefail
export AWS_REGION=eu-central-1
export EXPECTED_ACCOUNT=111122223333

ACTUAL_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
ACTUAL_ARN=$(aws sts get-caller-identity --query Arn --output text)
CONFIGURED_REGION=$(aws configure get region || true)

printf 'account=%s\ncaller=%s\nregion=%s\n' \
  "$ACTUAL_ACCOUNT" "$ACTUAL_ARN" "$CONFIGURED_REGION"

test "$ACTUAL_ACCOUNT" = "$EXPECTED_ACCOUNT"
test "$CONFIGURED_REGION" = "$AWS_REGION"
```

`get-caller-identity` dokazuje identity použitú aktuálnym AWS CLI credential provider chainom. Neznamená, že application alebo iný shell používa rovnaké credentials. `test` commands premenia mismatch na hard failure.

Evidence ukladaj do samostatného adresára:

```bash
export LAB_ID=AWS-LAB-001
export EVIDENCE_DIR="$HOME/cloudops-labs/$LAB_ID/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$EVIDENCE_DIR"
aws sts get-caller-identity > "$EVIDENCE_DIR/caller.json"
aws configure list > "$EVIDENCE_DIR/aws-config.txt"
```

Session tokens, secret values a plaintext KMS data do evidence nepatria.

## 2. Lab 1 — IAM a KMS encryption-context boundary

Cieľom je odlíšiť actual caller, IAM allow, key policy, key state a encryption context. Lab používa iba dočasný testovací plaintext.

Vytvor sandbox key a zaznamenaj jeho immutable identity:

```bash
KEY_ID=$(aws kms create-key \
  --description 'CloudOps AWS-LAB-001 temporary key' \
  --tags TagKey=Lab,TagValue="$LAB_ID" TagKey=Owner,TagValue=marvy \
  --region "$AWS_REGION" \
  --query KeyMetadata.KeyId \
  --output text)

aws kms describe-key \
  --key-id "$KEY_ID" \
  --region "$AWS_REGION" \
  --query 'KeyMetadata.{Arn:Arn,State:KeyState,Usage:KeyUsage,Origin:Origin}' \
  --output yaml | tee "$EVIDENCE_DIR/key-baseline.yaml"
```

`Enabled` dokazuje, že key je v stave, ktorý umožňuje podporované cryptographic operations. Nedokazuje, že current caller má `Encrypt` alebo `Decrypt`.

Positive round trip:

```bash
printf 'cloudops-lab-secret' > /tmp/cloudops-lab-secret.txt

aws kms encrypt \
  --key-id "$KEY_ID" \
  --plaintext fileb:///tmp/cloudops-lab-secret.txt \
  --encryption-context application=payments,purpose=lab \
  --region "$AWS_REGION" \
  --query CiphertextBlob \
  --output text | base64 -d > /tmp/cloudops-lab-secret.bin

aws kms decrypt \
  --ciphertext-blob fileb:///tmp/cloudops-lab-secret.bin \
  --encryption-context application=payments,purpose=lab \
  --key-id "$KEY_ID" \
  --region "$AWS_REGION" \
  --query Plaintext \
  --output text | base64 -d > /tmp/cloudops-lab-decrypted.txt

cmp /tmp/cloudops-lab-secret.txt /tmp/cloudops-lab-decrypted.txt
```

Successful `cmp` dokazuje, že caller, key policy, key state a exact context dovolili round trip. Neznamená, že nesprávny context je odmietnutý.

Forbidden experiment zmení `purpose`:

```bash
set +e
aws kms decrypt \
  --ciphertext-blob fileb:///tmp/cloudops-lab-secret.bin \
  --encryption-context application=payments,purpose=reporting \
  --key-id "$KEY_ID" \
  --region "$AWS_REGION" \
  > "$EVIDENCE_DIR/forbidden-decrypt.stdout" \
  2> "$EVIDENCE_DIR/forbidden-decrypt.stderr"
FORBIDDEN_RC=$?
set -e

test "$FORBIDDEN_RC" -ne 0
```

Forbidden decrypt musí zlyhať. Ak uspeje, nepridávaj ďalší allow. Najprv over, či policy viaže decrypt na encryption context a či test používa správny key ARN. Cleanup vykonaj až po dependency read-backu; samotný tag `Lab` nie je dostatočný dôkaz, že key nič iné nechráni.

## 3. Lab 2 — Route, Security Group a Network ACL

Použi dve malé SSM-managed test nodes v oddelených sandbox subnets. Destination počúva na TCP/8080. Security Groups flow povoľujú; injected fault zavedie scoped NACL deny pre return ephemeral ports.

Najprv fixuj identities a live policy:

```bash
aws ec2 describe-network-interfaces \
  --network-interface-ids "$SOURCE_ENI" "$DESTINATION_ENI" \
  --region "$AWS_REGION" \
  --query 'NetworkInterfaces[].{
    Eni:NetworkInterfaceId,
    Ip:PrivateIpAddress,
    Subnet:SubnetId,
    Groups:Groups[].GroupId
  }' \
  --output table

aws ec2 describe-route-tables \
  --filters Name=association.subnet-id,Values="$SOURCE_SUBNET" \
  --region "$AWS_REGION" \
  --output json > "$EVIDENCE_DIR/source-routes.json"

aws ec2 describe-network-acls \
  --filters Name=association.subnet-id,Values="$SOURCE_SUBNET" \
  --region "$AWS_REGION" \
  --output json > "$EVIDENCE_DIR/source-nacl.json"
```

Route-table query môže vrátiť prázdny result, keď subnet dedí main table. Prázdny output nie je dôkaz absencie routingu.

Pred aj po fault injection spusti zo source node-u:

```bash
nc -vz -w 3 "$DESTINATION_IP" 8080
curl --connect-timeout 3 -fsS "http://$DESTINATION_IP:8080/health"
```

Baseline musí uspieť. Po injected NACL deny očakávaj timeout pri zachovanom listeneri. Flow Logs alebo Reachability Analyzer pomôžu lokalizovať configuration boundary, ale application response musia stále overiť runtime commands.

Recovery odstráni iba injected rule. Acceptance vyžaduje, že povolený source flow znovu funguje a unsolicited reverse connection ostáva odmietnutý. Broad `allow all` je forbidden remediation.

## 4. Lab 3 — EC2 Auto Scaling a ALB generation mismatch

Launch template version 1 binduje application na `0.0.0.0:8080`. Version 2 obsahuje chybný bind `127.0.0.1:8080`. Sandbox ASG dočasne referencuje `$Latest`. Po vytvorení version 2 zvýš desired capacity:

```bash
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name cloudops-lab-asg \
  --desired-capacity 4 \
  --honor-cooldown \
  --region "$AWS_REGION"

aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name cloudops-lab-asg \
  --region "$AWS_REGION" \
  --query 'Activities[0:10].{
    Start:StartTime,
    Status:StatusCode,
    Description:Description
  }' \
  --output table

aws elbv2 describe-target-health \
  --target-group-arn "$TG_ARN" \
  --region "$AWS_REGION" \
  --query 'TargetHealthDescriptions[].{
    Target:Target.Id,
    State:TargetHealth.State,
    Reason:TargetHealth.Reason
  }' \
  --output table
```

Očakávaná observation: EC2 launch uspeje, ale new targets sú unhealthy. To oslabuje quota a subnet-capacity hypotézu a presúva investigation do startup/listener/SG/health pathu.

Na affected instance cez SSM porovnaj listener a local/private-IP requests:

```bash
aws ssm send-command \
  --instance-ids "$AFFECTED_INSTANCE" \
  --document-name AWS-RunShellScript \
  --parameters 'commands=["ss -ltnp","curl -fsS http://127.0.0.1:8080/health"]' \
  --region "$AWS_REGION"
```

Localhost success pri ALB failure smeruje na bind alebo network/listener boundary. Recovery pinne known-good numeric launch-template version a vytvorí corrected version 3. Acceptance potvrdí LT/AMI generation, target health, fresh request a ďalší scale-out, ktorý znova použije version 3.

## 5. Lab 4 — RDS unknown commit outcome

Použi sandbox PostgreSQL. Reálny Multi-AZ failover je voliteľný; response loss možno simulovať proxy-m, ktorý preruší connection po odoslaní commit-u.

```sql
create table payment_operation (
  idempotency_key text primary key,
  provider_request_id text unique,
  state text not null,
  updated_at timestamptz not null default now()
);

create table payment_outbox (
  id bigserial primary key,
  idempotency_key text not null unique,
  payload jsonb not null,
  published_at timestamptz
);
```

Client vykoná transaction a fault injection preruší response po možnom durable commit-e. Pred retryom query-ni authoritative state:

```sql
select idempotency_key, provider_request_id, state, updated_at
from payment_operation
where idempotency_key = 'lab-payment-884';

select id, idempotency_key, published_at
from payment_outbox
where idempotency_key = 'lab-payment-884';
```

Ak row existuje, blind replay je forbidden. Application má vrátiť alebo reconciliovať current outcome. Pri actual cluster lab-e možno failover request vykonať cez `aws rds failover-db-cluster`, no accepted API request nepreukazuje application reconnect ani exactly-once outcome.

Acceptance vyžaduje jeden operation row, jeden outbox row, jeden provider idempotency outcome a second run bez ďalšieho side effectu.

## 6. Lab 5 — CloudWatch dimension drift a remediation safety

Vytvor metric `CloudOps/Lab / SuccessfulOperations` s dimensions `Environment=lab, Service=payments-api`. Alarm používa missing data ako breaching, ale action je najprv notification-only.

```bash
aws cloudwatch put-metric-data \
  --namespace CloudOps/Lab \
  --metric-data 'MetricName=SuccessfulOperations,Value=1,Unit=Count,Dimensions=[{Name=Environment,Value=lab},{Name=Service,Value=payments-api}]' \
  --region "$AWS_REGION"

aws cloudwatch list-metrics \
  --namespace CloudOps/Lab \
  --metric-name SuccessfulOperations \
  --region "$AWS_REGION" \
  --output json
```

Fault injection zmení publisher dimension na `Service=payments`. Starý alarm začne vidieť missing datapoints. Čítaj configuration a históriu:

```bash
aws cloudwatch describe-alarms \
  --alarm-names cloudops-lab-success \
  --region "$AWS_REGION" \
  --output json > "$EVIDENCE_DIR/alarm.json"

aws cloudwatch describe-alarm-history \
  --alarm-name cloudops-lab-success \
  --history-item-type StateUpdate \
  --region "$AWS_REGION" \
  --output json > "$EVIDENCE_DIR/alarm-history.json"
```

Business counter ostáva healthy. Recovery obnoví versionovaný metric contract alebo kompatibilne presunie publisher a alarm. Samostatný telemetry-freshness alarm odlíši missing publisher od nulového business outcome-u. Forbidden test zopakuje dimension drift a preukáže, že destructive automation sa nespustí.

## 7. Lab 6 — SQS/Lambda duplicate delivery

Queue visibility nastav na 30 sekúnd, function timeout na 60 sekúnd a handler nech spracúva 40 sekúnd. Message môže byť visible skôr než prvý attempt skončí.

```bash
aws sqs get-queue-attributes \
  --queue-url "$QUEUE_URL" \
  --attribute-names VisibilityTimeout ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible RedrivePolicy \
  --region "$AWS_REGION" \
  --output json

aws lambda get-event-source-mapping \
  --uuid "$MAPPING_UUID" \
  --region "$AWS_REGION" \
  --query '{
    State:State,
    Function:FunctionArn,
    BatchSize:BatchSize,
    MaximumConcurrency:ScalingConfig.MaximumConcurrency,
    LastResult:LastProcessingResult
  }' \
  --output yaml
```

Duplicate receive je očakávaný failure. Recovery predĺži visibility podľa worst-case processing a pridá atomic idempotency claim pred external side effectom. Partial batch response znižuje zbytočný replay valid records, ale nenahrádza idempotency.

Acceptance odošle rovnaký business event dvakrát a očakáva jeden completion marker. Queue purge je forbidden, pretože by zničil unresolved work aj evidence.

## 8. Lab 7 — AWS Backup clean-room restore

Použi malý EBS volume alebo test database. Najprv vytvor backup a required copy, potom obnov resource do isolated subnet/accountu bez production egressu.

```bash
aws backup list-backup-jobs \
  --by-backup-vault-name cloudops-lab-source \
  --region eu-central-1 \
  --output table

aws backup list-copy-jobs \
  --by-destination-vault-arn "$RECOVERY_VAULT_ARN" \
  --region eu-west-1 \
  --output table

aws backup list-restore-jobs \
  --region eu-west-1 \
  --output table
```

Source backup `COMPLETED` nepreukazuje destination copy. Copy completion nepreukazuje KMS permission alebo restore metadata. Restore completion nepreukazuje mount, schema integrity ani application compatibility.

Po restore mountni alebo query-ni exact resource, porovnaj checksum/schema generation a vykonaj read/write canary s lab identity. Forbidden test overí, že restored environment nemá production routes alebo credentials. RPO sa vypočíta z posledného validného business checkpointu, nie z job completion timestampu.

## 9. Lab 8 — CloudFront cache-key isolation

Použi non-sensitive origin, ktorý vracia `X-Tenant-ID` v body. Faulty cache policy header forwarduje originu, ale nezahrnie ho do cache key a používa positive TTL.

```bash
curl -sS -D "$EVIDENCE_DIR/tenant-a.headers" \
  -H 'X-Tenant-ID: tenant-a' \
  "$DISTRIBUTION_URL/object" \
  -o "$EVIDENCE_DIR/tenant-a.body"

curl -sS -D "$EVIDENCE_DIR/tenant-b.headers" \
  -H 'X-Tenant-ID: tenant-b' \
  "$DISTRIBUTION_URL/object" \
  -o "$EVIDENCE_DIR/tenant-b.body"

diff -u "$EVIDENCE_DIR/tenant-a.body" "$EVIDENCE_DIR/tenant-b.body" || true
```

Ak tenant-b dostane tenant-a representation a headers ukazujú cache hit, issue je cache identity, nie nový origin authorization request. Containment nastaví caching-disabled policy pre authenticated path a vykoná targeted invalidation. Public origin alebo removal authorization je forbidden remediation.

Acceptance používa dve identities s rovnakým pathom a overí independent origin authorization alebo bezpečne odlišný cache key.

## 10. Evidence pack a cleanup gate

Každý lab uloží:

```text
manifest a UTC start time
caller/account/Region evidence
resource IDs a immutable generations
baseline commands a outputs
fault-injection diff
symptom timeline
hypotheses a discriminating observations
containment action
recovery diff
positive a forbidden test outputs
second-run result
cleanup inventory
```

Screenshot je doplnok, nie jediný authoritative artefakt. Command musí obsahovať exact Region a resource identity a output musí byť interpretovaný v texte.

Po odstránení lab resources vyhľadaj residual inventory podľa tags:

```bash
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Lab,Values="$LAB_ID" \
  --region eu-central-1 \
  --output json > "$EVIDENCE_DIR/residual-eu-central-1.json"

aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Lab,Values="$LAB_ID" \
  --region eu-west-1 \
  --output json > "$EVIDENCE_DIR/residual-eu-west-1.json"
```

Tagging API nepokrýva každý resource type. Doplň service-specific inventory pre použité služby. Lab končí až keď residual resources sú nulové alebo majú explicitný owner, dôvod a expiry.

## 11. Opakovateľnosť a score

Lab sa považuje za zvládnutý až po druhom čistom behu z baseline. Prvý úspech môže závisieť od stale cache alebo retained resource-u.

```yaml
result:
  labId: AWS-LAB-006
  run: 2
  subjectIdentifiedSeconds: 54
  firstObservation: queue-attributes-and-event-source-mapping
  rootCause: visibility-timeout-shorter-than-processing
  containment: event-source-mapping-paused
  recovery: visibility-and-idempotency-fixed
  positiveTest: one-completion-marker
  forbiddenTest: duplicate-event-created-no-second-side-effect
  cleanup: passed
```

## Kontrolné otázky

1. Prečo sa account a Region overujú hard `test` commandom pred mutation?
2. Čo KMS positive decrypt dokazuje a prečo potrebuje forbidden context test?
3. Ako route, SG a NACL lab lokalizuje first blocking boundary bez allow-all opravy?
4. Prečo EC2 `running` a ASG scale-out nepreukazujú serving capacity?
5. Ako RDS lab rozlišuje rollback od unknown commit outcome-u?
6. Prečo CloudWatch metric drift nesmie okamžite recyklovať fleet?
7. Ako queue visibility mení duplicate-delivery mechanizmus?
8. Prečo AWS Backup lab kontroluje source, copy, KMS, restore a business state oddelene?
9. Ako CloudFront lab preukáže cache-key isolation?
10. Čím sa dokazuje, že lab nezanechal chargeable alebo privileged resources?

## Oficiálna dokumentácia

- [AWS CLI v2 Command Reference](https://docs.aws.amazon.com/cli/latest/reference/)
- [AWS Workshops](https://workshops.aws/)
- [AWS Well-Architected Labs](https://www.wellarchitectedlabs.com/)
- [AWS KMS encryption context](https://docs.aws.amazon.com/kms/latest/developerguide/encrypt_context.html)
- [Amazon ECS service event messages](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-event-messages-list.html)
- [Invoking Lambda functions from Amazon SQS](https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html)
- [AWS Backup restore testing](https://docs.aws.amazon.com/aws-backup/latest/devguide/restore-testing.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CloudOps domain review a timed reasoning](cloudops-domain-review-timed-reasoning.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CloudOps troubleshooting drills →](cloudops-troubleshooting-drills.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
