# EC2 a Auto Scaling

Amazon EC2 vytvára konkrétne virtual-machine instances. EC2 Auto Scaling riadi fleet desired capacity, health replacement, scale-out/scale-in a instance refresh. Business capacity však nevzniká pri stave `running` ani pri samotnom zvýšení `desired capacity`. Potrebuje reprodukovateľný launch contract, úspešný bootstrap, správne network/storage/IAM identity, application health, target registration, traffic acceptance a bezpečný replacement alebo drain.

## Dominantný lifecycle

```text
business capacity, availability a release intent
→ immutable fleet/launch subject
→ ASG desired capacity a placement policy
→ EC2 launch, ENI, EBS a role realization
→ user-data/bootstrap a process generation
→ EC2/application/target health
→ warmup a InService serving cohort
→ scaling, refresh alebo replacement
→ drain, state handoff a termination
→ business outcome
→ recovery, rollback/roll-forward a retirement
```

ASG je reconciliation controller pre fleet count a health. Nie je automaticky deployment, database migration ani exactly-once processing systém.

## Connected Atlas Payments subject

Atlas Payments používa:

```text
ASG: payments-api-prod
source release: 4.2.0
expected launch template: LT-PAY version 57
expected AMI: AMI57
subnets: SUB-PA, SUB-PB, SUB-PC
Security Group: SG-PAY-APP
instance profile: ROLE-PAY-EC2
load balancer target group: TG-PAY-8080
business request: P-884
```

Exact fleet subject musí obsahovať:

```text
account, Region a ASG identity
ASG min/desired/max a scaling-process state
launch template ID a exact version
AMI ID/digest/provenance a architecture
instance type/weighted-capacity/purchase option
subnet/AZ, ENI, SG a route generation
instance profile/IMDS configuration
EBS/KMS/block-device generation
user-data digest a bootstrap operation ID
instance ID, lifecycle state a health-source verdicts
target-group registration/health reason
application/configuration generation
instance-refresh ID, preferences a checkpoint
request/transaction ID a business outcome
```

`$Latest`, mutable bootstrap dependencies alebo ručné instance changes rozbíjajú túto identity closure.

## 1. Launch template je versionovaný fleet contract

Launch template môže definovať:

- AMI a CPU architecture;
- instance type alebo attributes;
- subnets/ENI a Security Groups;
- IAM instance profile a metadata options;
- user data;
- EBS volumes, encryption a KMS dependencies;
- monitoring, tags a placement;
- capacity a purchase-related settings.

Dôležité rozlíšenie:

```text
launch template object
≠ launch template version
≠ AMI generation
≠ running instance generation
```

ASG referencing `$Latest` môže pri budúcom scale-out-e použiť novú neotestovanú version bez explicitného ASG configuration diffu. Production rollout má používať pinned version alebo iný rovnako auditovateľný promotion contract.

Zmena launch template version neaktualizuje existujúce instances. Potrebuje instance refresh, replacement alebo iný rollout.

## 2. AMI a bootstrap tvoria jeden effective machine image

AMI môže obsahovať OS, agents, runtime, application a hardened baseline. User data/cloud-init pridáva launch-time konfiguráciu.

Effective instance generation preto vzniká z:

```text
AMI content
+ launch template
+ user data
+ reachable repositories/artifacts
+ retrieved configuration/secrets
+ runtime service startup
```

Golden AMI znižuje startup dependencies. Thin bootstrap zvyšuje flexibilitu, ale pridáva DNS, route, IAM, repository, KMS a secret failure boundaries.

Bootstrap contract potrebuje:

- idempotentné kroky;
- pinned artifacts/packages;
- bounded retries a timeouty;
- structured logs;
- žiadne plaintext secrets v user data;
- explicitný completion/failure verdict;
- application process/configuration generation evidence.

## 3. EC2 lifecycle a data boundaries

EC2 instance môže prechádzať stavmi `pending`, `running`, `stopping`, `stopped`, `shutting-down` a `terminated`.

Operational boundaries:

- reboot zachováva instance identity a typicky attached storage;
- stop/start môže zmeniť underlying host a auto-assigned public IPv4;
- terminate ukončí instance a môže odstrániť `DeleteOnTermination` volumes;
- instance store je host-local ephemeral state;
- EBS je zonálny block storage a jeho lifecycle sa musí hodnotiť samostatne.

ASG replacement vytvorí nový instance ID, ENI/IP identity a process generation. Workload preto nemá držať jedinú authoritative session, queue claim, secret alebo business state iba lokálne bez replication/handoff modelu.

## 4. IAM role a IMDS sú runtime identity chain

EC2 instance profile poskytuje role credentials cez Instance Metadata Service.

Identity chain:

```text
launch template instance profile
→ attached role
→ IMDSv2 session/token
→ temporary credential generation
→ exact AWS API request
→ IAM authorization a CloudTrail outcome
```

Baseline:

- vyžadovať IMDSv2;
- nastaviť hop limit podľa architecture;
- používať least-privilege role;
- neukladať long-lived access keys do AMI alebo user data;
- monitorovať použitie credentials mimo expected instance/workload contextu.

EC2 `running` nepreukazuje, že role bola attached, credentials načítané alebo downstream API request autorizovaný.

## 5. ASG desired capacity a placement

ASG definuje minimum, desired, maximum, launch contract, subnets/AZs, health sources, scaling policies a termination/maintenance behavior.

Capacity chain:

```text
scaling policy alebo operator nastaví desired
→ ASG vyberie placement/capacity option
→ EC2 launch request
→ subnet IP, quota, instance capacity, IAM/KMS validation
→ instance pending/running
→ bootstrap
→ health a registration
→ InService
→ reálna serving capacity
```

Ak `desired` rastie, ale `InService` nie, failure je v launch, capacity, bootstrap alebo health boundary, nie nevyhnutne v scaling signal-e.

## 6. Health má viac vrstiev

Rozlišuj:

```text
EC2 system status
EC2 instance status
ASG health verdict
optional ELB/EBS/VPC Lattice/custom health
application process health
target-group readiness
business request success
```

EC2 health môže potvrdiť funkčnú VM, nie listener, správnu configuration alebo payment behavior.

Health-check grace period a default instance warmup musia pokryť realistický startup. Príliš krátke hodnoty vytvoria replacement loop. Príliš dlhé oneskoria detekciu.

Deep health check závislý od shared downstream môže fleet-wide failure zmeniť na fleet-wide replacement storm.

## 7. Scaling policy je feedback loop

Scaling signal musí reprezentovať demand alebo bottleneck na jednu serving unit.

Možnosti zahŕňajú target tracking, step, scheduled a predictive scaling. Dôležitejší než názov policy je causal model:

```text
metric provenance a window
→ recommendation
→ desired capacity
→ launch latency/warmup
→ InService/serving capacity
→ downstream pressure
→ business SLI
→ scale-in alebo stabilization
```

CPU nie je univerzálny signal. Workload môže byť limitovaný memory, EBS, network PPS, queue backlog, partner rate limitom alebo database connections.

Scale-out môže incident zhoršiť, ak každá instance pridá veľký connection pool, retries alebo downstream concurrency.

## 8. Instance warmup, draining a lifecycle hooks

Nová instance potrebuje boot, bootstrap, cache fill, target registration a application warmup. Počas scale-in-u môže potrebovať:

- load-balancer deregistration delay;
- request/connection drain;
- queue claim completion;
- session/state handoff;
- evidence export;
- external registry deregistration.

ASG lifecycle hook vloží instance do wait state-u pre custom action. Hook delivery a automation retry nie sú exactly-once; operation potrebuje idempotency key, heartbeat/timeout a durable result.

Hook timeout behavior musí byť explicitný. Fleet nemá zostať nekonečne v `Pending:Wait` alebo `Terminating:Wait`.

## 9. Instance refresh je fleet transition

Instance refresh mení fleet generation podľa launch contractu. Aktuálny AWS model podporuje rolling replacement a pri podporovanom scenári aj replace-root-volume stratégiu.

Refresh subject zahŕňa:

```text
source cohort a launch generation
target launch template/AMI generation
minimum/maximum healthy policy
warmup
checkpoints a pause durations
skip-matching semantics
rollback eligibility
health a business acceptance
```

Refresh success nepreukazuje database/schema compatibility ani správny shared state. Checkpoint má hodnotu iba vtedy, ak vyhodnocuje target health, application SLI a forbidden outcomes.

## 10. Mixed instances, Spot a weighted capacity

ASG môže používať viac instance types, architectures a On-Demand/Spot mix.

Potrebné invariants:

- binaries, AMI a agents podporujú architecture;
- weighted capacity zodpovedá reálnemu výkonu;
- application toleruje performance heterogenitu;
- Spot interruption má drain/retry/handoff model;
- capacity allocation strategy znižuje dependence na jednu pool/AZ;
- critical state nemá jedinú kópiu na interruptible instance.

Capacity Rebalancing môže spustiť replacement skôr, ale nezaručuje dokončenie in-flight business operationu.

## 11. Warm pools a stale generation

Warm pool skracuje scale-out latency, ale instance môže niesť stale:

- OS/package generation;
- application artifact;
- configuration alebo certificate;
- security patches;
- cached credential/session state.

Pred prechodom do service musí instance preukázať, že stále patrí do accepted launch a configuration generation. Warm pool nenahrádza immutable image promotion.

## 12. Worked incident — `$Latest` vytvorí replacement loop

### Symptóm

Po traffic spike-u:

```text
ASG desired capacity rastie 6 → 12
starých 6 instances ostáva healthy
nové instances sa launchnú
EC2 status checks sú green
ELB target health zlyhá
ASG ich terminate-ne a znovu vytvára
serving capacity ostáva 6
```

### Exact subject

```text
ASG: payments-api-prod
ASG launch template reference: LT-PAY:$Latest
previous healthy instances: LT-PAY:57 / AMI57
new instances: LT-PAY:58 / AMI58
source subnets: SUB-PA/B/C
SG: SG-PAY-APP
TG: TG-PAY-8080
health request: private-IP:8080/health
business request: P-884
```

### Competing hypotheses

1. EC2 quota alebo AZ capacity blokuje launch.
2. Subnets nemajú voľné IPs.
3. AMI architecture nesedí s instance type-mi.
4. KMS policy blokuje encrypted root volume.
5. IAM instance profile alebo `PassRole` je chybný.
6. User data/bootstrap zlyháva.
7. SG/NACL alebo target port blokuje health check.
8. Health grace period je príliš krátky.
9. Application binduje iba `127.0.0.1`.
10. Target group používa chybný path/protocol.

### Discriminating observations

- scaling activities ukazujú úspešný EC2 launch, takže quota/capacity nie sú primárny failure;
- ENI, EBS a role sú attached;
- EC2 status checks prejdú;
- target health reason ukazuje connection failure na private IP:8080;
- Security Group, NACL a target-group config sú rovnaké pre staré aj nové instances;
- na affected instance `curl 127.0.0.1:8080/health` funguje, ale `curl <private-ip>:8080/health` nie;
- AMI58 service config binduje application na `127.0.0.1`, AMI57 na `0.0.0.0`;
- ASG používa `$Latest`, preto scale-out automaticky prešiel na LT58.

Causal chain:

```text
image pipeline vytvorí LT58/AMI58
→ ASG reference `$Latest` sa effective zmení
→ traffic spike spustí scale-out
→ nové instances používajú LT58
→ process beží iba na loopback
→ EC2 health green, target health fails
→ ASG replacement loop
→ desired capacity nerovná sa serving capacity
```

### Containment

- pinni ASG späť na exact LT57 bez terminácie healthy old cohorty;
- zastav alebo pause-ni active instance refresh;
- obmedz retry/replacement churn, ak ohrozuje quotas alebo downstream;
- zachovaj jednu affected LT58 instance, cloud-init/systemd logs, target reason a image provenance;
- nezvyšuj iba grace period a neotváraj broad SG bez evidence.

### Authoritative recovery

1. Oprav AMI/service bind configuration v source image pipeline.
2. Vytvor novú immutable AMI59 a LT59.
3. Spusť standalone/canary instance s exact production subnet, SG, role a target registration.
4. Over private-IP listener, target health, configuration generation a payment request.
5. Pinni ASG na LT59.
6. Spusť instance refresh s checkpointmi a business SLI gate-om.
7. Retire-ni LT58 až po zachovaní incident evidence.

### Closure verdict

Recovery je prijatá až keď:

- ASG references exact approved LT59;
- desired, InService a serving capacity sa zhodujú podľa budgetu;
- každá AZ obsahuje healthy target cohortu;
- žiadna LT58 instance neprijíma traffic;
- payment request `P-884` a peak test prejdú bez duplicate outcome-u;
- forbidden management/inbound flows ostávajú blokované;
- nový scale-out a druhý refresh/reconcile nevytvoria regression;
- pipeline test odmietne loopback-only listener pre fleet workload.

## 13. Ďalšie failure boundaries

### Instance ostane `Pending:Wait`

Lifecycle-hook consumer, permission alebo callback zlyhal. EC2 resource existuje, ale nepatrí do serving capacity. Over hook operation ID, heartbeat, timeout a event delivery.

### Launch zlyhá pred vytvorením instance

AMI chýba, architecture je unsupported, AZ capacity/quota nestačí, subnet nemá IP, role/KMS/EBS permission je chybná alebo template odkazuje na odstránený resource. Scaling activity reason je prvý discriminating observation.

### Instance je InService, ale application používa stale config

Health endpoint je plytký alebo config fetch/reload zlyhal. Over process-loaded generation, nie iba launch template a file presence.

### Scale-out preťaží databázu

Každá instance otvorí rovnaký connection pool. Fleet capacity rastie, downstream envelope sa prekročí a latency/retries rastú. Scaling policy potrebuje downstream-aware guardrails.

### Scale-in ukončí in-flight jobs

Termination policy a lifecycle hook nemajú drain/claim handoff. Business operation musí byť idempotentná a recoverable nezávisle od instance termination.

### Spot replacement vytvorí duplicate processing

Interruption po external side-effect commit-e, ale pred durable acknowledgementom spôsobí retry na novej instance. Potrebný je work-item/operation ledger, nie iba lifecycle hook.

### Warm-pool instance obsahuje starý certificate

Instance prejde rýchlo do service, ale credential generation je revoked alebo incompatible. Activation gate musí overiť loaded epoch.

## 14. Troubleshooting sequence

```text
business symptom a affected cohort
→ ASG desired/InService/serving counts
→ scaling activity a process state
→ exact launch template version a AMI
→ EC2 launch, subnet IP, quota a capacity
→ ENI/SG/NACL/route
→ EBS/KMS a instance profile/IMDS
→ user-data/cloud-init/systemd/process
→ health-source reason a target registration
→ configuration/data/downstream state
→ fresh business request a forbidden outcome
```

Ručná SSH oprava jednej instance nie je fleet remediation. Ďalší replacement znovu použije chybný authoritative launch contract.

## 15. Recovery hierarchy

```text
preserve instance/scaling/bootstrap evidence
→ pin alebo opraviť authoritative launch contract
→ canary exact target generation
→ bounded refresh/scale transition
→ application a business acceptance
→ retire bad generation
→ earlier pipeline/control fix
```

Force termination všetkých instances alebo broad manual mutation zvyšujú blast radius a ničia evidence.

## 16. Earlier controls

- pinned launch template version;
- immutable AMI provenance a architecture matrix;
- boot/bootstrap/private-IP listener test;
- IMDSv2 a least-privilege instance profile;
- subnet IP, EC2 quota a AZ capacity headroom;
- target health reason alarms a serving-capacity SLI;
- realistic grace/warmup budget;
- instance-refresh canary/checkpoints;
- scale-out downstream connection budget;
- termination drain a idempotent work processing;
- Spot interruption drills;
- warm-pool generation validation;
- automatic retirement a rollback artifact retention.

## Referenčné rozlíšenia

| Otázka | Autoritatívna evidence |
|---|---|
| Čo ASG chce? | min/desired/max, scaling policies a activities |
| Čo nové instances používajú? | exact launch template version + AMI |
| Prečo launch nevznikol? | scaling activity, EC2/KMS/IAM/quota/subnet errors |
| Prečo VM beží, ale neslúži? | bootstrap, listener, target health a process-loaded config |
| Je scale-out business capacity? | serving cohort, SLI a downstream envelope |
| Je refresh bezpečný? | checkpoint/canary, compatibility a rollback eligibility |
| Je instance možné terminate-nuť? | drain, state/claim handoff a evidence retention |

## Kontrolné otázky

1. Prečo `desired capacity` nie je rovná serving capacity?
2. Aký je rozdiel medzi launch template objectom a exact version?
3. Prečo `$Latest` vytvára neviditeľný fleet drift?
4. Čo EC2 health nepreukazuje o application?
5. Ktoré boundaries môže user-data/bootstrap zlyhanie zasiahnuť?
6. Ako warmup ovplyvňuje scaling feedback loop?
7. Prečo instance refresh nie je database migration strategy?
8. Ako lifecycle hook súvisí s idempotenciou?
9. Kedy môže scale-out incident zhoršiť?
10. Ako overíš fleet recovery po oprave LT59?

## Glossary impact

Relevantné pojmy: EC2 fleet-realization subject, immutable launch subject, launch-template version closure, effective machine generation, serving-capacity realization, ASG reconciliation subject, health-source chain, replacement-loop subject, instance-refresh transition, lifecycle-hook operation subject, scale-out downstream envelope a fleet recovery closure.

## Oficiálna dokumentácia

- [Amazon EC2 concepts](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html)
- [Amazon EC2 Auto Scaling](https://docs.aws.amazon.com/autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html)
- [Auto Scaling health checks](https://docs.aws.amazon.com/autoscaling/ec2/userguide/health-checks-overview.html)
- [Lifecycle hooks](https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html)
- [Instance refresh](https://docs.aws.amazon.com/autoscaling/ec2/userguide/instance-refresh-overview.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Security Groups a Network ACLs](security-groups-network-acls.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Elastic Load Balancing →](elastic-load-balancing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
