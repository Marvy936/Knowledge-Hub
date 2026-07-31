# CloudOps troubleshooting drills

Troubleshooting drill trénuje rozhodovanie pod časom a neistotou. Každý drill začína business symptomom, nie názvom služby. Kandidát musí zachovať evidence, vytvoriť hypotézy, vybrať jednu diskriminačnú observation, vykonať bounded containment a uzavrieť recovery technickým aj business testom.

## 1. Drill protocol

```text
T+0  → state symptom and exact subject
T+2  → preserve volatile evidence
T+5  → write 3–5 competing hypotheses
T+8  → run cheapest discriminating observation
T+12 → contain blast radius
T+20 → apply authoritative recovery
T+30 → verify positive and forbidden outcome
T+35 → repeat or record residual risk
```

Blind restart before evidence is drill failure unless restart is required to stop active harm.

## 2. Drill A – ECS tasks remain PENDING

Symptom: desired count rises from 20 to 40, old tasks are healthy, new tasks remain `PENDING`.

First commands:

```bash
aws ecs describe-services \
  --cluster payments-prod \
  --services payments-api \
  --query 'services[0].{Desired:desiredCount,Running:runningCount,Pending:pendingCount,Events:events[0:10]}'

aws ec2 describe-subnets \
  --subnet-ids subnet-0paya subnet-0payb subnet-0payc \
  --query 'Subnets[].{Subnet:SubnetId,Free:AvailableIpAddressCount}'
```

If event says `RESOURCE:ENI`, do not edit container command or health check. Contain by stopping uncontrolled scale-out while retaining old cohort. Recover with address/capacity generation and canary tasks.

## 3. Drill B – ALB targets healthy, wrong release receives traffic

Symptom: both target groups healthy, intended 10 % canary receives zero requests.

```bash
aws elbv2 describe-rules --listener-arn "$LISTENER_ARN"
aws elbv2 describe-target-health --target-group-arn "$CANARY_TG"
```

Hypotheses include rule precedence, host/path mismatch, stickiness and missing cohort telemetry. A broad higher-priority rule can shadow canary. Recovery changes ordered rule with exact `Host`/path test; do not restart targets.

## 4. Drill C – RDS failover green, duplicate payment

Symptom: cluster promoted and new connections work, but provider shows two authorizations.

```bash
aws rds describe-events \
  --source-type db-cluster \
  --source-identifier db-pay-prod-17 \
  --duration 60
```

Then query idempotency ledger and provider IDs. Do not replay timeout operation before reconciliation. Root cause may be lost acknowledgement, not failed commit. Acceptance is one business outcome after second failover test.

## 5. Drill D – Lambda SQS backlog and duplicates

```bash
aws lambda get-event-source-mapping --uuid "$MAPPING_UUID"
aws lambda get-function-configuration --function-name payments-settle:live
aws sqs get-queue-attributes \
  --queue-url "$QUEUE_URL" \
  --attribute-names VisibilityTimeout RedrivePolicy ApproximateNumberOfMessages ApproximateNumberOfMessagesNotVisible
```

Compare function duration with visibility and provider idempotency. Contain by pausing mapping or lowering bounded concurrency, not purging queue. Replay only manifest-selected unresolved operations.

## 6. Drill E – KMS AccessDenied after policy rollout

```bash
aws sts get-caller-identity
aws kms describe-key --key-id "$KEY_ARN"
aws kms get-key-policy --key-id "$KEY_ARN" --policy-name default
```

Run positive/forbidden context test with non-production ciphertext. If affected Pod uses legacy environment key, adding wildcard to key policy is incorrect. Recovery removes stale credential source and verifies actual assumed-role session.

## 7. Drill F – Hybrid path fails in one AZ

From affected workload:

```bash
getent ahostsv4 ledger.internal
nc -vz -w 3 ledger.internal 5443
openssl s_client -connect ledger.internal:5443 -servername ledger.internal -brief </dev/null
```

Then inspect source ENI, route association, advertised/received prefixes and return firewall path. Green Direct Connect interface does not prove exact source-prefix round trip.

## 8. Drill G – CloudFront cross-tenant response

```bash
curl -D - -H 'X-Tenant-ID: tenant-a' "$URL"
curl -D - -H 'X-Tenant-ID: tenant-b' "$URL"
aws cloudfront get-distribution-config --id "$DISTRIBUTION_ID"
aws cloudfront get-cache-policy --id "$CACHE_POLICY_ID"
```

`X-Cache: Hit` plus absent origin request indicates shared cache. Contain with caching-disabled policy and targeted invalidation. Never open origin public.

## 9. Drill H – Backup green, recovery point unusable

```bash
aws backup list-backup-jobs --by-backup-vault-name vault-pay-prod-8
aws backup list-copy-jobs --by-destination-vault-arn "$RECOVERY_VAULT_ARN"
aws kms describe-key --key-id "$RECOVERY_KEY_ARN" --region eu-west-1
```

Source backup may be complete while isolated copy failed. Recovery chooses clean point and records actual RPO; control closes only after clean-room restore and business validation.

## 10. Drill I – CloudWatch alarm loop

```bash
aws cloudwatch describe-alarms --alarm-names ALARM-PAY-SUCCESS-18
aws cloudwatch list-metrics --namespace Atlas/Payments
aws cloudwatch describe-alarm-history --alarm-name ALARM-PAY-SUCCESS-18
```

Compare complete dimensions and publisher schema. Disable destructive action before fixing metric contract. Add telemetry-freshness precondition and execution dedup.

## 11. Drill J – NAT egress timeouts

```bash
aws ec2 describe-nat-gateways --nat-gateway-ids "$NAT_ID"
aws cloudwatch get-metric-data \
  --metric-data-queries file://nat-metrics.json \
  --start-time 2026-07-30T18:00:00Z \
  --end-time 2026-07-30T19:00:00Z
```

Correlate `ErrorPortAllocation`, destination tuple concentration, pooling and retries. Adding more application instances can worsen incident.

## 12. Drill scorecard

```yaml
drillId: CLOUDOPS-DRILL-D
subjectIdentifiedSeconds: 70
evidencePreserved: true
hypotheses:
  - visibility timeout shorter than processing
  - function throttling
  - poison record
firstObservation: event-source mapping plus queue attributes
containmentBlastRadius: bounded
recovery: passed
positiveTest: one settlement
forbiddenTest: duplicate event produced no second side effect
secondRun: passed
```

A drill passes only when second run is clean. First recovery can succeed because of accidental residual state.

## 13. Drill rotation

Rotate one drill from each domain weekly and combine two failure modes monthly. Example combined drill: CloudWatch dimension drift during ECS rollout, or RDS failover while Secrets rotation has mixed consumers. Combined drills train competing evidence and avoid service silos.

## Kontrolné otázky

1. Kedy je restart acceptable containment?
2. Prečo first divergent boundary matters?
3. Ako `RESOURCE:ENI` changes investigation order?
4. What evidence distinguishes lost acknowledgement from rollback?
5. Why should SQS not be purged during duplicate incident?
6. What does exact caller reveal in KMS drill?
7. Why does green Direct Connect not close hybrid path?
8. How is CloudFront cache leak contained safely?
9. Why must backup drill inspect copy and KMS?
10. What does second clean run prove?

## Oficiálna dokumentácia

- [AWS re:Post Knowledge Center](https://repost.aws/knowledge-center/)
- [AWS CLI Command Reference](https://docs.aws.amazon.com/cli/latest/reference/)
- [AWS Systems Manager Automation](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-automation.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CloudOps hands-on labs](cloudops-hands-on-labs.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Monitoring vs. observability →](../12-observability/monitoring-vs-observability.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
