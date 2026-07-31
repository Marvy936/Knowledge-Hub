# CloudOps domain review a timed reasoning

Táto kapitola premieňa SOA-C03 blueprint na opakovateľný reasoning tréning. Cieľom nie je odpovedať na čo najviac izolovaných otázok, ale merať, kde sa reasoning rozpadá: subject identification, service semantics, evidence selection, blast-radius control alebo verification.

## 1. Review unit

Každý tréningový scenár má jednotnú štruktúru:

```yaml
scenarioId: SOA-D1-OBS-017
domain: MonitoringLoggingRemediation
timeLimitSeconds: 120
symptom: Payment-success alarm entered ALARM after deployment
constraints:
  - business ledger remains healthy
  - old metric series stopped publishing
recentChange: release 7.18.0 changed EMF dimensions
question: Which action best restores correct monitoring without causing an outage?
evidenceExpected:
  - compare exact metric dimensions
  - inspect alarm history and publisher logs
forbiddenActions:
  - restart entire fleet
  - treat missing as proven payment failure
```

Po odpovedi sa nezapisuje iba správne/nesprávne. Zaznamená sa error class.

## 2. Error taxonomy

```text
S1 subject error        → wrong account, Region, resource or generation
S2 semantics error      → wrong service behavior assumption
S3 evidence error       → observation cannot distinguish hypotheses
S4 scope error          → action has unnecessary blast radius
S5 recovery error       → mutation without authority/idempotency
S6 verification error   → technical state accepted without business proof
```

Kandidát, ktorý má 75 % score, ale opakovane robí S6, potrebuje business validation drills, nie ďalšie flashcards.

## 3. Timed session design

Jedna 45-minútová session obsahuje:

```text
5 min  → preflight and objective
25 min → 12 mixed-domain scenarios
10 min → replay wrong/slow questions without options
5 min  → update error ledger and next drill
```

Čas na jednu otázku je približne 120 sekúnd. Prvých 20 sekúnd patrí subjectu, ďalších 40 boundary a evidence, zvyšok answer comparison and final verification.

## 4. Evidence-first scratchpad

Pre každú otázku používaj šesť riadkov:

```text
Subject:
Known healthy:
First divergent boundary:
Best observation:
Safest action:
Acceptance evidence:
```

Príklad:

```text
Subject: RDS cluster DB-PAY-42, eu-central-1, in-flight P-884
Known healthy: cluster promoted and new connection works
First divergent boundary: commit acknowledgement versus business outcome
Best observation: DB idempotency ledger + provider request IDs
Safest action: reconcile before retry
Acceptance evidence: one provider authorization and one ledger state
```

## 5. Domain 1 review

Monitoring/Logging/Remediation otázky sa riešia cez signal identity, freshness, aggregation, alarm state, delivery and automation postcondition.

Praktický verification set:

```bash
aws cloudwatch list-metrics \
  --namespace Atlas/Payments \
  --metric-name SuccessfulAuthorizations \
  --region eu-central-1

aws cloudwatch describe-alarm-history \
  --alarm-name ALARM-PAY-SUCCESS-18 \
  --region eu-central-1

aws logs start-query \
  --log-group-name /atlas/prod/payments-api \
  --start-time 1785227300 \
  --end-time 1785229200 \
  --query-string 'fields @timestamp, release, outcome | filter release="7.18.0"'
```

Question trap: missing datapoint is not automatically zero or service failure.

## 6. Domain 2 review

Reliability/Business Continuity uses failure scope, current authority, RTO/RPO, replication lag, backup isolation and restore validation.

Question trap: selecting Multi-AZ for logical deletion or selecting backup restore for low-latency read scaling.

Timed scenario:

```text
Source RDS is healthy but table was accidentally deleted.
Multi-AZ standby contains the same deletion.
Latest clean PITR point is 12 minutes old.
RPO is 15 minutes.
```

Correct reasoning chooses isolated PITR restore and reconciliation, not failover. Verification checks schema/data/business state before cutover.

## 7. Domain 3 review

Deployment/Provisioning/Automation focuses on immutable versions, controller convergence, drift, rollback eligibility and automation scope.

```bash
aws cloudformation describe-stack-events --stack-name payments-prod
aws autoscaling describe-instance-refreshes --auto-scaling-group-name payments-api-prod
aws ecs describe-services --cluster payments-prod --services payments-api
```

Question trap: CloudFormation `UPDATE_COMPLETE` accepted as application success.

## 8. Domain 4 review

Security/Compliance uses actual caller, policy layers, encryption context, evidence retention and forbidden access tests.

```bash
aws sts get-caller-identity
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::100000000042:role/payments-runtime \
  --action-names kms:Decrypt \
  --resource-arns "$KEY_ARN"
```

Question trap: adding broad IAM allow when KMS key policy or SCP is the actual boundary.

## 9. Domain 5 review

Networking/Content Delivery uses DNS → route → policy → transport → listener/cache → application ordering.

```bash
dig pay.example.com A
aws ec2 describe-route-tables --filters Name=association.subnet-id,Values=subnet-0payc
aws ec2 describe-network-acls --filters Name=association.subnet-id,Values=subnet-0payc
aws elbv2 describe-target-health --target-group-arn "$TG_ARN"
```

Question trap: target health used to explain wrong listener-rule precedence or cross-tenant cache collision.

## 10. Scoring model

Score combines correctness, time and error class:

```text
2 points → correct answer under time with correct reasoning
1 point  → correct answer but slow or weak evidence
0 points → incorrect answer
```

Add a severity penalty for recurring S1/S4/S6 because these errors create operational damage.

Session record:

```csv
scenario,domain,seconds,points,error_class,note
SOA-D1-017,D1,88,2,,metric generation identified
SOA-D2-021,D2,131,0,S6,accepted restore job without validation
SOA-D5-009,D5,104,1,S3,checked SG before route association
```

## 11. Replay without answer options

For every wrong question, hide choices and ask:

```text
Which observation would you run first?
What result would discriminate two leading hypotheses?
What action is safe before root cause is complete?
What evidence closes recovery?
```

This prevents memorizing answer wording.

## 12. Readiness gate

A domain is ready when three consecutive sessions achieve at least 80 %, median answer time under 105 seconds, no repeated high-risk S1/S4/S6 pattern and at least one corresponding hands-on lab passes twice.

## Kontrolné otázky

1. Prečo raw percent score nestačí?
2. Ktoré error classes majú najvyšší operational risk?
3. Ako scratchpad oddeľuje observation od action?
4. Prečo wrong question treba replay-nuť bez options?
5. Čo tvorí domain readiness gate?
6. Ako sa timed scenario prepája s hands-on labom?
7. Kedy je correct but slow answer stále slabina?
8. Prečo sa CloudFormation status nesmie zameniť za business result?
9. Aký trap rozlišuje failover od PITR?
10. Ako error ledger určí ďalší tréning?

## Oficiálna dokumentácia

- [SOA-C03 Exam Guide](https://docs.aws.amazon.com/aws-certification/latest/examguides/cloudops-associate-03.html)
- [AWS Skill Builder](https://skillbuilder.aws/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: AWS Certified CloudOps Engineer – Associate (SOA-C03)](cloudops-engineer-associate-soa-c03.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CloudOps hands-on labs →](cloudops-hands-on-labs.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
