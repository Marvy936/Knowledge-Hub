# AWS Systems Manager

AWS Systems Manager je operations control plane pre managed nodes a AWS resources. Spája registration, remote command delivery, interactive access, desired-state associations, patching, inventory, automation a parameter storage. Control-plane request však nie je business result. `Command status=Success` môže znamenať iba exit code nula na nesprávnom targete alebo bez application postcondition.

```text
operational intent
→ exact target and document generation
→ managed-node eligibility
→ caller and execution authorization
→ resolved target manifest
→ rate-controlled delivery
→ per-node or per-step result
→ reboot, drain or resource convergence
→ application and business validation
→ compliance and evidence closure
```

Najväčšie riziko Systems Managera je jeho schopnosť rýchlo vykonať privileged operation na veľkej fleet-e. Target authority a blast-radius controls sú preto rovnako dôležité ako samotný script.

## 1. Exact operation subject

Atlas Payments používa operation subject `OPS-PAY-42`. Target fleet je 36 production EC2 instances v troch AZs, z toho štyri approved canary nodes. SSM Agent generation je `AGENT-SSM-17`, host-management configuration `DHMC-PROD-9`, endpoint generation `VPCE-SSM-12` a inventory association `ASSOC-INV-18`.

Patch operation používa policy `PATCH-POL-PAY-14`, baseline `PATCH-BL-PAY-22`, selector `PatchRing=prod-canary`, approved target manifest `TARGET-PAY-4-NODES`, document `AWS-RunPatchBaseline` v pinned version a execution `PATCH-EXEC-91`. Max concurrency je 1 alebo 25 % canary setu, max errors 1 a reboot `RebootIfNeeded`.

Forbidden outcomes sú mutable tag expanding target set, 100 % fleet reboot, command success accepted without application health and arbitrary high-privilege role passed to Automation.

## 2. Managed-node eligibility

Machine je managed node až keď má running SSM Agent, valid identity, correct account/Region registration, DNS/time/TLS, route/NAT alebo VPC endpoint path a capability-specific dependencies.

```bash
aws ssm describe-instance-information \
  --filters Key=InstanceIds,Values=i-0123456789abcdef0 \
  --region eu-central-1 \
  --query 'InstanceInformationList[0].{Id:InstanceId,Ping:PingStatus,Agent:AgentVersion,Platform:PlatformName,PlatformVersion:PlatformVersion,LastPing:LastPingDateTime,Association:AssociationStatus}'
```

`PingStatus=Online` preukazuje recent agent communication. NePreukazuje disk headroom, package repository, document compatibility ani application health.

Na node:

```bash
sudo systemctl status amazon-ssm-agent --no-pager
sudo journalctl -u amazon-ssm-agent --since '-30 minutes'
```

## 3. Identity and endpoint path

EC2 managed-node identity môže používať instance profile alebo Default Host Management Configuration podľa chosen modelu. Private node komunikuje cez NAT alebo interface endpoints. Session channel môže fungovať, kým S3 output alebo patch repository path zlyháva.

Endpoint inventory:

```bash
aws ec2 describe-vpc-endpoints \
  --region eu-central-1 \
  --filters Name=vpc-id,Values=vpc-0pay42 \
  --query 'VpcEndpoints[?contains(ServiceName, `ssm`)].{Id:VpcEndpointId,Service:ServiceName,State:State,Subnets:SubnetIds,PrivateDns:PrivateDnsEnabled}'
```

Exact required endpoints depend on Region, agent generation and capabilities. One endpoint named `ssm` is not proof of complete Systems Manager networking.

## 4. SSM document as versioned execution contract

Custom command document:

```yaml
schemaVersion: "2.2"
description: Validate the Atlas Payments application without mutation
parameters:
  HealthUrl:
    type: String
    default: http://127.0.0.1:8080/readyz
    allowedPattern: '^http://127\.0\.0\.1:[0-9]+/[a-zA-Z0-9/_-]+$'
mainSteps:
  - action: aws:runShellScript
    name: ValidateApplication
    precondition:
      StringEquals:
        - platformType
        - Linux
    inputs:
      timeoutSeconds: '30'
      runCommand:
        - set -euo pipefail
        - cat /etc/atlas/release.env
        - systemctl is-active atlas-payments
        - curl --fail --silent --show-error '{{ HealthUrl }}'
```

Document name, exact version, content hash, parameters, target manifest, execution role and timeout belong to operation identity. Default version can change; production invocation pins numeric version.

## 5. Run Command delivery and result

Run Command má oddelenú delivery a execution boundary. Accepted command môže zostať pending alebo delivery-timeoutovať; exit code nula zase dokazuje iba výsledok pluginu na konkrétnom node, nie správny target manifest, application health alebo business outcome.

```bash
COMMAND_ID=$(aws ssm send-command \
  --document-name Atlas-ValidatePayments \
  --document-version 7 \
  --instance-ids i-0canary1 i-0canary2 \
  --parameters 'HealthUrl=["http://127.0.0.1:8080/readyz"]' \
  --max-concurrency 1 \
  --max-errors 1 \
  --cloud-watch-output-config 'CloudWatchOutputEnabled=true,CloudWatchLogGroupName=/atlas/ssm/commands' \
  --region eu-central-1 \
  --query Command.CommandId --output text)
```

Per-node result:

```bash
aws ssm list-command-invocations \
  --command-id "$COMMAND_ID" \
  --details \
  --region eu-central-1
```

`Pending` or `Delayed` means script may not have started. `DeliveryTimedOut` is delivery failure. `ExecutionTimedOut` is plugin execution timeout. `Success` reflects plugin exit result, not load balancer or payment transaction.

## 6. Target manifest before mutation

Tag selector is dynamic query, not immutable approval artifact. Before high-impact operation resolve it:

```bash
aws ssm describe-instance-information \
  --filters Key=tag:PatchRing,Values=prod-canary \
  --region eu-central-1 \
  --query 'InstanceInformationList[].InstanceId' \
  --output text | tr '\t' '\n' | sort > target-manifest.txt

sha256sum target-manifest.txt
wc -l target-manifest.txt
```

Approval binds exact hash and expected count/AZ ownership. Runtime gate fails if selector resolves to different set. Principal allowed to mutate target tags and call `SendCommand` has indirect privilege escalation path.

## 7. Rate controls

`max-concurrency=100%` removes safety cohort. Percentages must be translated to real node count. `max-errors` counts command failure, not application SLO, unless runbook converts business check failure into execution failure.

Canary policy:

```text
4 approved nodes
→ max concurrency 1
→ one node drains, patches and reboots
→ agent reconnect and application test
→ next node only after acceptance
→ stop on first failed canary
```

## 8. Session Manager

Session Manager provides shell or port forwarding without inbound SSH/RDP. It still requires caller IAM, approved session document, node eligibility, local OS user, logging/KMS and duration limits.

```bash
aws ssm start-session \
  --target i-0123456789abcdef0 \
  --document-name AWS-StartInteractiveCommand \
  --parameters 'command=["sudo -iu atlas-ops"]' \
  --region eu-central-1
```

CloudTrail records session API lifecycle, not automatically every shell command. Session content logging depends on session type and configuration. Port-forward sessions can bypass intended network boundaries and need explicit governance.

## 9. State Manager and idempotency

Association periodically reconciles document against targets. Document must inspect current state and perform no-op when compliant.

```bash
aws ssm create-association \
  --name Atlas-ConfigureCloudWatchAgent \
  --document-version 4 \
  --targets Key=tag:Application,Values=payments-api \
  --schedule-expression 'rate(30 minutes)' \
  --compliance-severity HIGH \
  --region eu-central-1
```

Command `append line`, `create user without existence check` or `restart every run` creates recurring side effects. State Manager is not substitute for immutable image pipeline when replacement is authoritative host model.

## 10. Inventory freshness

Systems Manager Inventory je periodická observation s vlastným collection timestampom. Záznam môže byť syntakticky správny a zároveň stale alebo neúplný, preto sa package, OS alebo application verdict vždy viaže na agent, association, upload time a porovnanie s current node state-om.

```bash
aws ssm list-inventory-entries \
  --instance-id i-0123456789abcdef0 \
  --type-name AWS:Application \
  --region eu-central-1
```

Inventory observation has collection timestamp and association generation. Package presence does not prove loaded or used. Stale inventory must not close vulnerability remediation.

## 11. Patch Manager lifecycle

```text
OS and repository state
→ baseline/policy resolution
→ scan and compliance snapshot
→ canary install
→ reboot decision
→ application validation
→ controlled waves
→ fresh rescan
```

Scan:

```bash
aws ssm send-command \
  --document-name AWS-RunPatchBaseline \
  --document-version 1 \
  --instance-ids i-0canary1 \
  --parameters 'Operation=["Scan"]' \
  --region eu-central-1
```

Install:

```bash
aws ssm send-command \
  --document-name AWS-RunPatchBaseline \
  --document-version 1 \
  --instance-ids i-0canary1 \
  --parameters 'Operation=["Install"],RebootOption=["RebootIfNeeded"]' \
  --region eu-central-1
```

`COMPLIANT` is relative to baseline and scan snapshot. It is not general security or application-health verdict.

Immutable fleet often prefers patched AMI build → canary → ASG instance refresh. In-place patch remains relevant for long-lived hosts or emergency response.

## 12. Automation runbook

Automation is explicit state machine. Example YAML:

```yaml
schemaVersion: '0.3'
description: Patch one Atlas canary and validate application health
assumeRole: '{{ AutomationAssumeRole }}'
parameters:
  InstanceId:
    type: String
    allowedPattern: '^i-[a-f0-9]+$'
  AutomationAssumeRole:
    type: String
mainSteps:
  - name: Patch
    action: aws:runCommand
    inputs:
      DocumentName: AWS-RunPatchBaseline
      InstanceIds: ['{{ InstanceId }}']
      Parameters:
        Operation: [Install]
        RebootOption: [RebootIfNeeded]
  - name: WaitForAgent
    action: aws:waitForAwsResourceProperty
    timeoutSeconds: 600
    inputs:
      Service: ssm
      Api: DescribeInstanceInformation
      Filters:
        - Key: InstanceIds
          Values: ['{{ InstanceId }}']
      PropertySelector: '$.InstanceInformationList[0].PingStatus'
      DesiredValues: [Online]
  - name: Validate
    action: aws:runCommand
    inputs:
      DocumentName: Atlas-ValidatePayments
      DocumentVersion: '7'
      InstanceIds: ['{{ InstanceId }}']
```

Runbook still needs ALB eligibility and business smoke outside local validation, or additional explicit steps. `iam:PassRole` to `AutomationAssumeRole` must be scoped to exact runbook and role path.

## 13. Parameter Store

Parameter Store stores versioned String/StringList/SecureString configuration.

```bash
aws ssm put-parameter \
  --name /atlas/prod/payments/config-generation \
  --type String \
  --value CFG-PAY-52 \
  --overwrite \
  --region eu-central-1

aws ssm get-parameter \
  --name /atlas/prod/payments/config-generation \
  --region eu-central-1
```

SecureString requires SSM permission and KMS decrypt. Parameter Store does not automatically provide Secrets Manager rotation workflow.

## 14. Worked incident: mutable tag patches all 36 nodes

Change `CHG-2026-884` approved four canary nodes selected by `PatchRing=prod-canary`. Two minutes before execution, provisioning automation assigned this tag to all 36 production instances. Runbook did not materialize approved target IDs and `maxConcurrency` had been changed to 100 %.

Patch plugin returned success on 34 nodes and rebooted them. Systems Manager showed mostly green executions, while all three ALB cohorts went unhealthy. Two nodes had package conflict; others caused secret-refresh and DB connection storm.

Root cause was target-authority failure, unsafe rate control and missing application postcondition.

Containment stopped remaining executions, blocked tag mutation and preserved SSM, ALB and node logs. Recovery replaced affected stateless nodes from last-known-good AMI in AZ waves and introduced runbook version 12 with one-node concurrency, one-error stop, drain, reboot wait, ALB health and payment smoke.

Acceptance required exact four-node manifest, fresh patch compliance, known AMI/application generation across fleet and forbidden proof that `SendCommand` principal cannot mutate target tags or pass arbitrary role.

## 15. Troubleshooting order

Offline node: power/OS → agent logs → identity → time/DNS/TLS → route/endpoints → registration. Command pending: target resolution → agent channel → quota/delivery. Command failed: exact plugin, user, working directory, parameters, exit code and stderr. Automation success but wrong outcome: controller/resource state → runtime → application postcondition.

## Kontrolné otázky

1. What makes a machine an eligible managed node?
2. Why is tag selector not immutable approval?
3. What does Run Command `Success` prove?
4. How do max concurrency and max errors limit blast radius?
5. Why must State Manager documents be idempotent?
6. What does patch compliance depend on?
7. When is immutable replacement safer than package rollback?
8. What does Session Manager audit and what may it not log?
9. How does Automation assume role create a PassRole boundary?
10. Which business postcondition closes patch operation?

## Oficiálna dokumentácia

- [AWS Systems Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html)
- [Managed nodes](https://docs.aws.amazon.com/systems-manager/latest/userguide/managed-instances.html)
- [Run Command](https://docs.aws.amazon.com/systems-manager/latest/userguide/run-command.html)
- [Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)
- [State Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-state.html)
- [Patch Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/patch-manager.html)
- [Systems Manager Automation](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-automation.html)
- [Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CloudWatch a CloudTrail](cloudwatch-cloudtrail.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: KMS a Secrets Manager →](kms-secrets-manager.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
