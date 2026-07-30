# EC2 a Auto Scaling

Amazon EC2 vytvára konkrétne virtual-machine instances. EC2 Auto Scaling riadi fleet desired capacity, placement, health replacement, scale-out, scale-in a instance refresh. Business capacity však nevzniká pri stave `running` ani zvýšením `desired capacity`. Potrebuje reprodukovateľný launch contract, úspešný bootstrap, správne network/storage/IAM identity, application health, target registration a bezpečný drain.

```text
business capacity a release intent
→ immutable AMI and launch-template version
→ ASG desired capacity and placement
→ EC2, ENI, EBS and instance profile realization
→ bootstrap and process generation
→ EC2, application and target health
→ InService serving cohort
→ scale, refresh or replacement
→ drain and termination
→ business outcome
```

Auto Scaling je reconciliation controller pre fleet count a health. Nie je automaticky deployment, database migration ani exactly-once processing systém.

## 1. Exact fleet subject

Atlas Payments používa Auto Scaling group `payments-api-prod`. Accepted release je `4.2.0`, launch template `LT-PAY` version `57` a AMI `AMI57`. Fleet používa subnets `SUB-PA`, `SUB-PB`, `SUB-PC`, Security Group `SG-PAY-APP`, instance profile `ROLE-PAY-EC2` a target group `TG-PAY-8080`. Sample business request je `P-884`.

Fleet identity zahŕňa account, Region, ASG min/desired/max, exact launch-template version, AMI ID a provenance, architecture, instance type alebo weighted capacity, subnet/AZ, ENI/SG, EBS/KMS, instance profile, IMDS options, user-data digest, configuration generation, instance ID, lifecycle state, target health a rollout/refresh ID.

Reference `$Latest` alebo mutable package repository rozbíja identity closure. Neskorší scale-out môže spustiť inú generation bez explicitného ASG configuration diffu.

## 2. AMI a launch template sú odlišné artefakty

AMI obsahuje machine-image state: operating system, packages, agents, runtime a prípadne application artifact. Launch template opisuje, ako sa image materializuje: instance type, network, Security Groups, IAM profile, block devices, metadata options, user data, tags a ďalšie launch inputs.

```text
AMI generation
+ launch-template version
+ external bootstrap dependencies
+ retrieved config and secret generations
→ effective running instance generation
```

Golden AMI znižuje launch-time dependencies. Thin AMI s rozsiahlym bootstrapom zvyšuje flexibility, ale pridáva DNS, repository, IAM, KMS, secret a retry failure boundaries. Production image build má byť reproducible a AMI ID má byť promoted ako immutable input.

## 3. Praktický launch template v Terraform-e

Nasledujúci template používa pinned AMI, IMDSv2, encrypted root volume a versionovaný bootstrap contract:

```hcl
resource "aws_launch_template" "payments" {
  name_prefix   = "payments-api-"
  image_id      = var.payments_ami_id
  instance_type = "m7g.large"

  iam_instance_profile {
    name = aws_iam_instance_profile.payments.name
  }

  vpc_security_group_ids = [aws_security_group.application.id]

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "disabled"
  }

  block_device_mappings {
    device_name = "/dev/xvda"

    ebs {
      volume_type           = "gp3"
      volume_size           = 20
      encrypted             = true
      kms_key_id            = aws_kms_key.ec2.arn
      delete_on_termination = true
    }
  }

  user_data = base64encode(templatefile("${path.module}/cloud-init.yaml", {
    release_id        = "PAY-4.2.0"
    config_generation = "CFG-PAY-57"
  }))

  tag_specifications {
    resource_type = "instance"
    tags = {
      Application = "payments-api"
      Release     = "PAY-4.2.0"
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}
```

`http_tokens = "required"` vyžaduje IMDSv2. Hop limit musí zodpovedať architecture; pri container network path-e môže hodnota 1 brániť intended accessu. Terraform apply vytvorí novú launch-template version, ale existujúce instances nezmení. Fleet transition potrebuje instance refresh alebo replacement.

## 4. Bootstrap ako idempotentný state transition

Cloud-init príklad nesťahuje mutable `latest` artifact. Spustí image-baked service a zapíše iba bezpečnú generation metadata:

```yaml
#cloud-config
write_files:
  - path: /etc/atlas/release.env
    permissions: "0644"
    content: |
      RELEASE_ID=${release_id}
      CONFIG_GENERATION=${config_generation}

runcmd:
  - [systemctl, daemon-reload]
  - [systemctl, enable, --now, atlas-payments.service]
  - [bash, -lc, "curl --fail --silent --show-error http://127.0.0.1:8080/readyz"]
  - [touch, /var/lib/atlas/bootstrap-complete]
```

Bootstrap success preukazuje local process a readiness path. Neoveruje target registration, database transaction ani external payment provider. Plaintext secrets nepatria do user data, pretože user data a instance metadata majú odlišný confidentiality lifecycle než secret store.

Bootstrap musí byť idempotentný. ASG replacement alebo manual rerun nesmie vytvoriť druhý business side effect. Logy zostávajú na instance a v central destination so stable instance/release identity.

## 5. Auto Scaling group a placement

```hcl
resource "aws_autoscaling_group" "payments" {
  name                = "payments-api-prod"
  min_size            = 6
  desired_capacity    = 6
  max_size            = 24
  health_check_type   = "ELB"
  health_check_grace_period = 180
  vpc_zone_identifier = [
    aws_subnet.application["a"].id,
    aws_subnet.application["b"].id,
    aws_subnet.application["c"].id,
  ]

  launch_template {
    id      = aws_launch_template.payments.id
    version = aws_launch_template.payments.latest_version
  }

  target_group_arns = [aws_lb_target_group.payments.arn]

  instance_refresh {
    strategy = "Rolling"

    preferences {
      min_healthy_percentage = 100
      max_healthy_percentage = 125
      instance_warmup        = 180
    }
  }

  tag {
    key                 = "Release"
    value               = "PAY-4.2.0"
    propagate_at_launch = true
  }
}
```

Príklad používa Terraform-resolved konkrétnu version. Pri promotion je ešte lepšie uložiť exact numeric launch-template version do release manifestu a nepripustiť nečakaný diff. `min_healthy_percentage=100` vyžaduje rollout headroom; subnet IP a account capacity musia umožniť surge.

Desired capacity je iba request controlleru. Serving capacity vznikne až po launch, ENI/EBS/IAM realization, bootstrap, health a target registration.

## 6. Live fleet read-back

ASG state:

```bash
aws autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names payments-api-prod \
  --region eu-central-1 \
  --query 'AutoScalingGroups[0].{Min:MinSize,Desired:DesiredCapacity,Max:MaxSize,LaunchTemplate:LaunchTemplate,Instances:Instances[].{Id:InstanceId,Az:AvailabilityZone,Lifecycle:LifecycleState,Health:HealthStatus,Version:LaunchTemplate.Version}}'
```

Tento command ukazuje ASG desired state a instance cohort. `InService` nepreukazuje application business behavior.

Exact EC2 realization:

```bash
aws ec2 describe-instances \
  --instance-ids i-0123456789abcdef0 \
  --region eu-central-1 \
  --query 'Reservations[0].Instances[0].{State:State.Name,Image:ImageId,Type:InstanceType,Az:Placement.AvailabilityZone,Subnet:SubnetId,PrivateIp:PrivateIpAddress,Profile:IamInstanceProfile.Arn,Metadata:MetadataOptions,BlockDevices:BlockDeviceMappings}'
```

Launch-template version:

```bash
aws ec2 describe-launch-template-versions \
  --launch-template-id lt-0pay42 \
  --versions 57 \
  --region eu-central-1
```

Tieto read-backs odlišujú intended fleet manifest od actual instance generation.

## 7. EC2 a application health majú viac vrstiev

EC2 system status sleduje provider-side host a infrastructure boundary. Instance status sleduje guest reachability a základný runtime. ASG môže používať EC2 alebo ELB health. Target group testuje configured protocol, port a path. Application business canary testuje reálnu transaction.

```text
EC2 system check
→ EC2 instance check
→ ASG health
→ process/local readiness
→ target-group health
→ external request
→ payment invariant
```

Príliš krátky health-check grace period vytvorí replacement loop, pretože instance je ukončená skôr, než bootstrap skončí. Príliš dlhý interval zasa oneskorí detekciu. Readiness endpoint nemá bezhlavo závisieť od každého shared downstreamu; inak jeden database incident označí celý fleet unhealthy a ASG ho začne recyklovať.

Target health read-back:

```bash
aws elbv2 describe-target-health \
  --target-group-arn "$TARGET_GROUP_ARN" \
  --region eu-central-1 \
  --query 'TargetHealthDescriptions[].{Instance:Target.Id,Port:Target.Port,Az:Target.AvailabilityZone,State:TargetHealth.State,Reason:TargetHealth.Reason,Description:TargetHealth.Description}'
```

## 8. Guest a process diagnostics cez Systems Manager

```bash
COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-0123456789abcdef0 \
  --document-name AWS-RunShellScript \
  --parameters 'commands=["cat /etc/atlas/release.env","systemctl status atlas-payments --no-pager","ss -ltnp | grep :8080","curl -fsS http://127.0.0.1:8080/readyz","curl -fsS http://$(hostname -I | awk '\''{print $1}'\''):8080/readyz"]' \
  --query Command.CommandId \
  --output text)

aws ssm get-command-invocation \
  --command-id "$COMMAND_ID" \
  --instance-id i-0123456789abcdef0
```

Localhost success a private-IP failure ukazujú bind/listener boundary. SSM command `Success` znamená exit code nula pre script; nepreukazuje load balancer ani payment transaction.

## 9. Scaling policy a downstream budget

Autoscaling signal musí reprezentovať demand na serving unit. CPU môže byť vhodný pre compute-bound workload, ale payment API môže byť limitovaná database connections alebo provider quota. `ALBRequestCountPerTarget` je často bližšie k request loadu, no retries môžu metric nafúknuť.

```bash
aws autoscaling put-scaling-policy \
  --auto-scaling-group-name payments-api-prod \
  --policy-name payments-requests-per-target \
  --policy-type TargetTrackingScaling \
  --estimated-instance-warmup 180 \
  --target-tracking-configuration file://target-tracking.json \
  --region eu-central-1
```

`target-tracking.json`:

```json
{
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ALBRequestCountPerTarget",
    "ResourceLabel": "app/atlas-payments/1234567890abcdef/targetgroup/payments/abcdef1234567890"
  },
  "TargetValue": 100.0,
  "DisableScaleIn": false
}
```

ASG maximum musí rešpektovať database connection a NAT/provider budgets. Scale-out, ktorý zvyšuje `InService` count a znižuje business success, je neúspešný.

## 10. Scale-in, drain a lifecycle hooks

Scale-in môže ukončiť instance s in-flight HTTP requestom, queue lease alebo background operation. Load balancer deregistration delay rieši nové traffic selection, no application stále potrebuje termination handling.

```bash
aws autoscaling put-lifecycle-hook \
  --lifecycle-hook-name payments-terminating-drain \
  --auto-scaling-group-name payments-api-prod \
  --lifecycle-transition autoscaling:EC2_INSTANCE_TERMINATING \
  --heartbeat-timeout 300 \
  --default-result CONTINUE \
  --region eu-central-1
```

Hook vloží instance do `Terminating:Wait`. Drain automation označí workload za ineligible, ukončí new work, počká na in-flight requests, odovzdá queue claims a až potom zavolá:

```bash
aws autoscaling complete-lifecycle-action \
  --lifecycle-hook-name payments-terminating-drain \
  --auto-scaling-group-name payments-api-prod \
  --lifecycle-action-result CONTINUE \
  --instance-id i-0123456789abcdef0 \
  --region eu-central-1
```

Automation musí byť idempotentná. Duplicate hook delivery alebo retry nesmie dvakrát kompenzovať business operation.

## 11. Instance refresh ako cohort transition

Instance refresh nahrádza fleet podľa target launch contractu. Current source/target generation, health percentages, warmup, checkpoints a rollback eligibility sú súčasť release manifestu.

```bash
aws autoscaling start-instance-refresh \
  --auto-scaling-group-name payments-api-prod \
  --preferences '{
    "MinHealthyPercentage": 100,
    "MaxHealthyPercentage": 125,
    "InstanceWarmup": 180,
    "CheckpointPercentages": [25,50,100],
    "CheckpointDelay": 300,
    "SkipMatching": true,
    "AutoRollback": true
  }' \
  --region eu-central-1
```

Checkpoint má zmysel iba vtedy, ak pipeline vyhodnotí target health, application SLI, release identity a forbidden outcomes. Refresh success nevracia database migration ani external payment side effects.

Progress:

```bash
aws autoscaling describe-instance-refreshes \
  --auto-scaling-group-name payments-api-prod \
  --region eu-central-1 \
  --query 'InstanceRefreshes[0].{Id:InstanceRefreshId,Status:Status,Percentage:PercentageComplete,Remaining:InstancesToUpdate,Reason:StatusReason}'
```

## 12. Mixed instances, Spot a warm pools

Multiple instance types znižujú dependence na jednu capacity pool. Binaries a AMI musia podporovať architecture a weighted capacity musí približne reprezentovať reálnu throughput unit. Spot interruption potrebuje drain a idempotency; Capacity Rebalancing nevie garantovať dokončenie transaction.

Warm pool skracuje scale-out, ale môže niesť stale packages, configuration, certificate alebo cached credential. Pred prechodom do `InService` musí instance preukázať approved AMI, config generation a credential freshness.

## 13. Worked incident: `$Latest` vytvorí replacement loop

Po traffic spike-u rástla ASG desired capacity zo 6 na 12. Starých šesť instances zostalo healthy. Nové instances sa spustili, EC2 status checks boli green, no target health zlyhával a ASG ich opakovane nahrádzala. Serving capacity ostala šesť.

Exact subject ukázal, že ASG odkazovala na `LT-PAY:$Latest`. Staré instances používali version `57/AMI57`, nové version `58/AMI58`. ENI, EBS, role, SG a route boli správne. `curl 127.0.0.1:8080/health` fungoval, ale request na private IP nie. AMI58 bindovala application iba na `127.0.0.1`; AMI57 na `0.0.0.0`.

Image pipeline vytvorila LT58, a preto každý nový scale-out bez explicitného ASG rollout-u automaticky použil chybnú version.

Containment nastavilo ASG na pinned version 57 a zachovalo failed instance/bootstrap evidence. Healthy instances sa nerecyklovali. Recovery vytvorila AMI59, ktorá bindovala na expected interface, a launch template 59. Canary instance prešla local, private-IP, target-group a payment testom. Až potom instance refresh menil fleet po cohorts.

Closure vyžadovala, aby všetky serving instances používali pinned version 59, future scale-out vytvoril rovnakú generation, private listener fungoval a payment `P-884` skončil presne raz. Policy-as-code zakázala `$Latest` a `$Default` v production ASG manifests.

## 14. Troubleshooting order

Ak desired count rastie a instances nevzniknú, čítaj scaling activities a rozliš quota, capacity pool, subnet IP, KMS, IAM a launch-template validity. Ak instance je `running`, ale nie `InService`, pokračuj bootstrapom a ASG health. Ak je `InService`, ale target unhealthy, analyzuj SG/NACL, listener, health path a startup. Ak target healthy a business zlyháva, pokračuj application, database a external dependencies.

```bash
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name payments-api-prod \
  --region eu-central-1 \
  --max-items 20 \
  --query 'Activities[].{Time:StartTime,Status:StatusCode,Cause:Cause,Description:Description}'
```

## Kontrolné otázky

1. Aký rozdiel je medzi AMI, launch template a running instance generation?
2. Prečo `$Latest` rozbíja reproducible fleet identity?
3. Čo preukazuje EC2 `running` a čo nepreukazuje?
4. Ako odlíšiš desired, InService, target-healthy a serving capacity?
5. Ktorý bootstrap krok musí byť idempotentný?
6. Ako IMDSv2 a instance profile tvoria runtime identity chain?
7. Prečo autoscaling maximum závisí od database connection budgetu?
8. Čo musí vykonať lifecycle hook pred termination?
9. Prečo instance refresh success nie je business rollback?
10. Aký test preukáže, že future scale-out používa accepted launch generation?

## Oficiálna dokumentácia

- [Amazon EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html)
- [Launch templates](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-templates.html)
- [EC2 Auto Scaling](https://docs.aws.amazon.com/autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html)
- [Health checks for Auto Scaling instances](https://docs.aws.amazon.com/autoscaling/ec2/userguide/health-checks-overview.html)
- [Instance refresh](https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-instance-refresh.html)
- [Lifecycle hooks](https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html)
- [Instance Metadata Service](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Security Groups a Network ACLs](security-groups-network-acls.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Elastic Load Balancing →](elastic-load-balancing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
