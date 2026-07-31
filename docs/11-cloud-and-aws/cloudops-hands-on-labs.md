# CloudOps hands-on labs

Hands-on lab nie je zoznam príkazov. Je to controlled experiment s precondition, exact subjectom, injected failure, evidence, authoritative recovery, positive test, forbidden test a cleanup. Každý lab sa vykonáva v sandbox alebo explicitne izolovanom account-e; destructive commands sa nepoužívajú v production.

## 1. Lab contract

```yaml
labId: AWS-LAB-001
objective: Diagnose an IAM/KMS denial from the actual workload identity
account: sandbox-payments
region: eu-central-1
budgetLimitUsd: 10
preconditions:
  - AWS CLI v2 configured
  - jq installed
  - sandbox role assumed
stopConditions:
  - unexpected production account
  - resource tag Owner is not current user
cleanupRequired: true
```

Preflight:

```bash
set -euo pipefail
aws sts get-caller-identity
aws configure get region
```

Account a Region sa porovnajú s lab manifestom pred prvou mutation.

## 2. Lab 1 – IAM a KMS context

### Build

Vytvor sandbox KMS key a IAM role s decrypt allow iba pre context `application=payments,purpose=lab`.

```bash
KEY_ID=$(aws kms create-key \
  --description 'CloudOps lab key' \
  --tags TagKey=Lab,TagValue=AWS-LAB-001 \
  --query KeyMetadata.KeyId --output text)

aws kms create-alias \
  --alias-name alias/cloudops-lab-001 \
  --target-key-id "$KEY_ID"
```

### Experiment

Encrypt:

```bash
printf 'lab-secret' > /tmp/lab-secret.txt
aws kms encrypt \
  --key-id "$KEY_ID" \
  --plaintext fileb:///tmp/lab-secret.txt \
  --encryption-context application=payments,purpose=lab \
  --query CiphertextBlob --output text | base64 -d > /tmp/lab-secret.bin
```

Positive decrypt uses exact context. Forbidden decrypt changes purpose and must fail. Record actual caller with `sts get-caller-identity`.

### Cleanup

Remove alias and schedule key deletion only after confirming no shared resource uses key.

## 3. Lab 2 – Route, SG and NACL boundary

### Build

Create two tiny EC2 or SSM-managed test nodes in separate private subnets. Allow TCP 8080 through SG, then inject a subnet NACL rule that blocks return ephemeral ports.

### Observe

```bash
aws ec2 describe-network-interfaces --network-interface-ids "$SOURCE_ENI"
aws ec2 describe-route-tables --filters Name=association.subnet-id,Values="$SOURCE_SUBNET"
aws ec2 describe-network-acls --filters Name=association.subnet-id,Values="$SOURCE_SUBNET"
```

From source:

```bash
nc -vz -w 3 "$DESTINATION_IP" 8080
ss -tnp dst "$DESTINATION_IP":8080
```

Use Flow Logs or Reachability Analyzer to identify the first blocking boundary. Do not fix by allowing all traffic.

### Acceptance

Allowed flow passes, unsolicited reverse connection remains denied and repeated run produces same result.

## 4. Lab 3 – EC2 Auto Scaling and ALB generations

### Build

Create launch template version 1 with correct listener and version 2 binding only localhost. Configure ASG to reference `$Latest` in sandbox, scale out and observe new targets failing.

```bash
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name cloudops-lab-asg \
  --desired-capacity 4

aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name cloudops-lab-asg

aws elbv2 describe-target-health --target-group-arn "$TG_ARN"
```

### Recover

Pin known-good numeric launch-template version, build corrected version 3 and use instance refresh with checkpoint.

### Acceptance

Every serving instance reports exact AMI/LT version, target health passes and fresh scale-out uses version 3.

## 5. Lab 4 – RDS failover and unknown outcome

Use a low-cost sandbox Multi-AZ-compatible deployment or simulate client failure against test database when actual Multi-AZ cost is not approved.

Create idempotency table:

```sql
create table payment_operation (
  idempotency_key text primary key,
  state text not null,
  updated_at timestamptz not null default now()
);
```

Client sends transaction and intentionally drops connection near commit. Before retry, query by idempotency key. If actual failover is used:

```bash
aws rds failover-db-cluster \
  --db-cluster-identifier cloudops-lab-db
```

Acceptance is one logical operation after reconnect, not merely new writer status.

## 6. Lab 5 – CloudWatch metric drift and remediation safety

Publish `Service=payments-api` metric, create alarm, then change publisher to `Service=payments`. Observe old series missing and alarm transition.

```bash
aws cloudwatch list-metrics \
  --namespace CloudOps/Lab \
  --metric-name SuccessfulOperations

aws cloudwatch describe-alarm-history \
  --alarm-name cloudops-lab-success
```

Automation action must initially be notification-only. Add telemetry-freshness alarm and prove dimension drift does not trigger destructive restart.

## 7. Lab 6 – SQS/Lambda duplicate delivery

Create queue with visibility 30 seconds and function timeout 60 seconds. Handler sleeps 40 seconds and writes business key. Observe duplicate receive, then fix visibility and add conditional idempotency claim.

```bash
aws sqs get-queue-attributes \
  --queue-url "$QUEUE_URL" \
  --attribute-names VisibilityTimeout ApproximateNumberOfMessagesNotVisible

aws lambda get-event-source-mapping --uuid "$MAPPING_UUID"
```

Acceptance sends same message twice and produces one completion marker.

## 8. Lab 7 – AWS Backup clean-room restore

Protect a small EBS volume or test database, copy point to recovery vault and run restore in isolated VPC/account when available.

```bash
aws backup list-backup-jobs --region eu-central-1
aws backup list-copy-jobs --region eu-west-1
aws backup list-restore-jobs --region eu-west-1
```

Mount/query restored resource, verify checksum/schema and run forbidden network/credential tests. Delete restored resources after evidence capture.

## 9. Lab 8 – CloudFront cache-key isolation

Use non-sensitive sandbox origin returning `X-Tenant-ID`. Configure incorrect cache policy that ignores tenant header, reproduce shared response, then set TTL zero or include safe identity dimension.

```bash
curl -D - -H 'X-Tenant-ID: tenant-a' "$DISTRIBUTION_URL/object"
curl -D - -H 'X-Tenant-ID: tenant-b' "$DISTRIBUTION_URL/object"
```

Never use real credentials or tenant data. Acceptance proves independent representations and private origin access.

## 10. Evidence pack

Each lab stores:

```text
manifest and cost limit
→ commands and UTC timestamps
→ resource IDs/generations
→ injected fault
→ observations
→ remediation diff
→ positive and forbidden results
→ cleanup evidence
```

Screenshot alone is insufficient. Commands must be reproducible and secrets redacted.

## 11. Cost and safety guardrails

Use sandbox account, budget alarm, short TTL resources, owner/lab tags and cleanup script. Before stopping lab, list residual resources in each used Region. Expensive Multi-AZ/CloudFront/NAT labs need explicit cost estimate and reduced duration.

## Kontrolné otázky

1. Prečo lab potrebuje forbidden test?
2. Čo stop condition chráni?
3. Ako sa odlíši configuration evidence od runtime evidence?
4. Prečo SG/NACL lab nesmie skončiť allow-all rule?
5. Čo je acceptance v RDS failover lab-e?
6. Ako metric-drift lab overí bezpečnú automation?
7. Prečo duplicate Lambda event treba poslať zámerne?
8. Čo clean-room restore preukazuje navyše oproti backup jobu?
9. Ako sa preukáže cleanup?
10. Kedy sa lab považuje za opakovateľný?

## Oficiálna dokumentácia

- [AWS Workshops](https://workshops.aws/)
- [AWS CLI Command Reference](https://docs.aws.amazon.com/cli/latest/reference/)
- [AWS Well-Architected Labs](https://www.wellarchitectedlabs.com/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CloudOps domain review a timed reasoning](cloudops-domain-review-timed-reasoning.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CloudOps troubleshooting drills →](cloudops-troubleshooting-drills.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
