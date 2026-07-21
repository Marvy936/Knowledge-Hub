# EC2 a Auto Scaling

Amazon EC2 poskytuje virtuálne compute instances v AWS. EC2 Auto Scaling nad nimi udržiava požadovanú kapacitu, nahrádza nezdravé instances a mení počet instances podľa demandu alebo harmonogramu. Samotná EC2 instance nie je automaticky high availability; odolnosť vzniká až kombináciou immutable launch contractu, viacerých Availability Zones, health checks, load balancingu, stateless alebo externalizovaného state-u a riadeného replacementu.

## 1. Mentálny model

```text
AMI + instance type + launch template + network/storage/IAM configuration
→ EC2 instance
→ Auto Scaling Group desired capacity
→ health evaluation
→ replace / scale out / scale in
```

Rozlišuj:

- **EC2 instance** — jeden konkrétny virtual machine lifecycle,
- **launch template** — versionovaný launch contract,
- **Auto Scaling Group (ASG)** — controller pre fleet capacity,
- **scaling policy** — pravidlo meniace desired capacity,
- **load balancer target group** — traffic a application-health vrstva.

ASG pripomína reconciliation controller: porovnáva desired capacity so skutočným stavom a vytvára alebo ukončuje instances. Nevykonáva však application deployment orchestration automaticky bezpečne; potrebuje versionovaný image/bootstrap, health model a rollout stratégiu.

## 2. EC2 instance lifecycle

Hlavné stavy:

```text
pending → running → stopping → stopped → pending/running
                     ↘ shutting-down → terminated
```

Dôležité rozdiely:

- **reboot** typicky zachová instance identity, private IP a attached storage,
- **stop/start** môže presunúť instance na iný host a zmeniť auto-assigned public IPv4,
- **terminate** ukončí instance a odstráni volumes označené `DeleteOnTermination`,
- **hibernate** uloží obsah RAM na encrypted root EBS volume pri podporovanej konfigurácii.

Instance store je host-local ephemeral storage. Dáta môžu prežiť reboot, ale nie stop, termination alebo host failure. Durable state preto nepatrí iba na instance store bez replication alebo backup modelu.

## 3. AMI

Amazon Machine Image definuje boot image a block-device mapping pre nové instances.

AMI môže obsahovať:

- operating system,
- runtime a agents,
- hardened baseline,
- application artifact,
- launch-time bootstrap prerequisites.

Modely:

- **golden AMI** — väčšina software je pripravená pred launchom,
- **thin AMI + user data** — instance sa konfiguruje pri štarte,
- **hybrid** — stabilný OS/runtime v image, environment configuration pri launchi.

Golden image skracuje startup a znižuje runtime dependency na repositories. Príliš hrubý image však zvyšuje build frequency a patching coordination. User-data bootstrap je flexibilný, ale môže zlyhať pre DNS, IAM, repository, secret alebo network problém.

Production image pipeline má obsahovať:

- patching a hardening,
- vulnerability scan,
- boot test,
- application smoke test,
- immutable AMI ID,
- promotion medzi environments,
- retirement a deregistration policy.

## 4. Instance types a families

Instance type určuje kombináciu:

- vCPU,
- memory,
- network bandwidth,
- EBS bandwidth,
- local storage,
- acceleratorov,
- CPU architecture.

Bežné families:

- general purpose,
- compute optimized,
- memory optimized,
- storage optimized,
- accelerated computing.

Výber podľa priemernej CPU utilization je nedostatočný. Sleduj aj memory, network PPS/bandwidth, EBS throughput/IOPS, queue depth, latency, NUMA/architecture compatibility a burst-credit model.

Graviton/ARM môže znížiť cost/performance, ale vyžaduje kompatibilné binaries, container images a agents.

## 5. Nitro System

Moderné EC2 instances typicky používajú AWS Nitro System, ktorý offloaduje virtualization, network, storage a management funkcie do dedikovaného hardware a minimalizovaného hypervisoru.

Operational dôsledky:

- enhanced networking,
- vysoký EBS výkon,
- Nitro Enclaves pri vybraných use cases,
- iný device naming model pri NVMe,
- kompatibilita instance features závisí od family a generation.

Nespoliehaj sa na console device name ako jediný guest-OS disk identifier. Over filesystem UUID, NVMe mapping a persistent mount configuration.

## 6. Network identity

EC2 instance používa primary ENI a môže mať ďalšie ENIs.

Identity vrstvy:

- instance ID,
- private IPv4/IPv6,
- public IPv4 alebo Elastic IP,
- DNS names,
- ENI ID a MAC,
- IAM role credentials,
- application identity.

Auto Scaling replacement vytvorí novú instance identity. Workload nesmie vyžadovať ručné povoľovanie každého instance ID alebo lokálne uloženú jedinú kópiu state-u.

Elastic IP je stabilná public IPv4 identity, ale môže vytvoriť single-instance coupling. Pre fleet traffic preferuj load balancer alebo DNS-based service endpoint.

## 7. Instance Metadata Service a IMDSv2

Instance Metadata Service poskytuje instance-local metadata a temporary credentials pre attached IAM role.

IMDSv2 používa session token získaný `PUT` requestom a znižuje riziko niektorých SSRF a open-proxy útokov.

Bezpečný baseline:

- vyžadovať IMDSv2,
- obmedziť metadata hop limit podľa architecture,
- nepoužívať metadata credentials mimo instance,
- monitorovať neobvyklé credential použitie,
- chrániť application proti SSRF.

IAM role credentials sú dočasné, ale stále citlivé. Kompromitovaný process ich môže použiť do expirácie a podľa role permissions.

## 8. User data a bootstrap

User data sa používa na launch-time inicializáciu, často cez cloud-init.

Príklady:

- registrácia monitoring agentu,
- načítanie configuration,
- mount storage,
- spustenie application service,
- signalizácia bootstrap completion.

Požiadavky:

- idempotencia,
- explicitné timeouts a retries,
- structured logs,
- bezpečné získanie secrets,
- failure signal pre ASG/CloudFormation,
- deterministická package a artifact verzia.

User data nie je vhodné miesto pre plaintext secrets. Je čitateľné cez instance/API permissions a môže sa objaviť v launch templates, IaC state alebo support evidence.

Diagnostika:

```bash
sudo cloud-init status --long
sudo journalctl -u cloud-init
sudo journalctl -u cloud-final
sudo tail -n 200 /var/log/cloud-init-output.log
```

Cesty sa môžu líšiť podľa image-u.

## 9. Launch templates

Launch template je versionovaný EC2 launch contract.

Môže definovať:

- AMI,
- instance type alebo attributes,
- key pair,
- Security Groups,
- IAM instance profile,
- user data,
- EBS volumes,
- metadata options,
- monitoring,
- placement a capacity settings,
- tags.

Používaj launch templates namiesto legacy launch configurations.

Dôležitá hranica:

- `$Latest` sa môže zmeniť bez explicitného deployment rozhodnutia,
- `$Default` je stabilnejší iba vtedy, ak zmenu default version riadi pipeline,
- pinned version dáva najpresnejšiu reprodukovateľnosť.

Zmena launch template neaktualizuje existujúce instances automaticky. Potrebný je instance refresh, replacement alebo iný rollout mechanizmus.

## 10. Auto Scaling Group

ASG definuje:

- minimum capacity,
- desired capacity,
- maximum capacity,
- launch template/version,
- subnets/Availability Zones,
- health-check sources,
- scaling policies,
- termination a maintenance behavior.

Príklad konceptu:

```text
min=2
desired=4
max=12
subnets = eu-central-1a + 1b + 1c
```

ASG sa snaží udržať desired capacity. Keď `InService` instance označí ako unhealthy, spustí replacement podľa aktuálneho launch contractu.

ASG neposkytuje automaticky:

- application state replication,
- database consistency,
- safe schema migration,
- session externalization,
- správny health endpoint,
- dostatočnú subnet/IP alebo service-quota kapacitu.

## 11. Health checks

Health sources môžu zahŕňať:

- EC2 system/instance status,
- Elastic Load Balancing target health,
- EBS health,
- VPC Lattice,
- custom health checks.

EC2 health môže potvrdiť, že virtual machine beží, ale nie že application obsluhuje používateľov. ELB health pridáva application/network path.

Health-check grace period alebo default instance warmup musia pokryť reálny startup. Príliš krátke hodnoty vytvoria replacement loop; príliš dlhé oneskoria detekciu reálneho failure.

Pred replacementom zachovaj evidence, ak incident model vyžaduje forenznú analýzu. Automatické terminate môže odstrániť volatile logs a local state.

## 12. Scaling policies

### Target tracking

Udržiava metric približne na target hodnote, napríklad average CPU alebo request count per target.

### Step scaling

Mení capacity podľa veľkosti alarm breach.

### Simple scaling

Legacy jednoduchá zmena s cooldownom; typicky menej pružná než target tracking alebo step scaling.

### Scheduled scaling

Mení min/desired/max podľa známeho harmonogramu.

### Predictive scaling

Vytvára forecast z historického patternu a pripravuje capacity pred očakávaným loadom.

Správny signal má korelovať s bottleneckom a demand per unit. Pri queue workload-e je často lepší backlog per instance než CPU.

## 13. Instance warmup a cooldown

Nová instance nemusí byť okamžite plnohodnotná.

Warmup pokrýva:

- boot,
- bootstrap,
- cache fill,
- registration,
- health checks,
- JIT alebo application initialization.

Počas warmup-u scaling engine podľa policy semantics obmedzí vplyv neúplných metrics. Nesprávne warmup nastavenie môže spôsobiť over-scaling alebo oscillation.

Scale-in má byť pomalší a konzervatívnejší než scale-out, ak workload potrebuje connection draining, queue completion alebo state handoff.

## 14. Lifecycle hooks

Lifecycle hook zastaví instance v prechodnom stave, aby automation vykonala custom action.

Typické use cases:

- launch-time registration alebo configuration,
- security/monitoring validation,
- graceful drain pri termination,
- log alebo diagnostic collection,
- deregistration z externého systému.

Hook čaká na heartbeat alebo completion result. Bez správneho timeout a failure behavioru môže fleet uviaznuť v `Pending:Wait` alebo `Terminating:Wait`.

Hook side effect musí byť idempotentný. Event delivery a automation retry môžu operáciu zopakovať.

## 15. Instance refresh

Instance refresh postupne nahrádza ASG instances podľa novej launch template verzie alebo configuration.

Riadi:

- minimum healthy percentage,
- instance warmup,
- checkpoints,
- skip matching,
- rollback podľa podporovaného workflowu.

Pred refreshom over:

- AMI availability a permissions,
- subnet IP capacity,
- quotas,
- target-group health,
- bootstrap dependencies,
- storage/state externalization,
- rollback artifact.

Instance refresh nie je databázová ani application migration stratégia. Ak nový build nie je backward-compatible so shared state-om, fleet rollout môže zlyhať aj pri zdravom EC2 replacement mechanizme.

## 16. Mixed instances a purchase options

ASG môže používať viac instance types a kombinovať On-Demand a Spot capacity.

Výhody:

- lepšia capacity availability,
- nižší cost,
- menšia závislosť od jednej instance family.

Požiadavky:

- application musí tolerovať odlišný výkon,
- scaling metric má zohľadniť weighted capacity,
- architecture musí podporovať CPU architecture,
- Spot interruption musí byť bezpečná,
- capacity allocation strategy musí zodpovedať workloadu.

Spot je interruptible capacity. Nepoužívaj ho ako jedinú vrstvu pre stateful alebo nereplikovaný kritický workload.

Capacity Rebalancing môže proaktívne spustiť náhradu Spot instance pri elevated interruption risk, ale workload stále potrebuje drain a idempotentné spracovanie.

## 17. Warm pools

Warm pool drží predinicializované instances mimo aktívnej `InService` capacity, aby skrátil scale-out latency.

Trade-offy:

- nižší startup čas,
- dodatočný cost,
- stale software/configuration,
- lifecycle complexity,
- security patching a credential freshness.

Warm pool nenahrádza immutable image pipeline. Pred aktiváciou musí byť instance stále validovaná voči aktuálnemu release contractu.

## 18. Placement groups a tenancy

Placement options ovplyvňujú latency, throughput a failure correlation.

- **cluster placement group** — nízka network latency/vysoký throughput, väčšia failure correlation,
- **spread placement group** — oddelenie malého počtu critical instances,
- **partition placement group** — partitions pre distributed systems,
- **Dedicated Hosts/Instances** — tenancy alebo licensing/compliance use cases.

Placement constraint môže znížiť available capacity. Pred deploymentom testuj capacity a fallback strategy.

## 19. Storage a state

EC2 fleet má preferovať externalizovaný state:

- S3 pre objects,
- EBS pre zonálny block state,
- EFS pre shared NFS filesystem,
- RDS/DynamoDB/ElastiCache podľa data modelu,
- queues/streams pre asynchronous work.

Lokálny disk, in-memory sessions alebo ručne upravená instance bránia bezpečnému replacementu.

## 20. Maintenance a recovery

Mechanizmy môžu zahŕňať:

- stop/start,
- reboot,
- instance recovery,
- ASG replacement,
- Systems Manager patching,
- AMI rollout,
- EC2 maintenance events.

Vo fleet modeli preferuj replacement pred ručnou opravou jednotlivého servera, ak state a bootstrap contract umožňujú reprodukciu.

## 21. Observability

Zbieraj:

- EC2 status checks,
- CPU, network a disk/EBS metrics,
- memory/filesystem/process metrics cez agent,
- ASG desired/in-service/pending/terminating capacity,
- scaling activities,
- lifecycle-hook events,
- target health reason codes,
- bootstrap logs,
- CloudTrail configuration changes,
- Spot interruption/rebalance events.

`CPUUtilization` sama nevysvetľuje memory pressure, EBS saturation, packet drops ani application latency.

## 22. Cost model

Hlavné cost drivers:

- instance runtime a purchase model,
- operating system/licensing,
- EBS volumes/snapshots/IOPS/throughput,
- data transfer,
- public IPv4,
- detailed monitoring,
- load balancer/NAT dependencies,
- idle warm-pool capacity.

Scale-in bez workload safety môže znížiť účet a zároveň poškodiť službu. Cost optimization musí zachovať availability, recovery a performance requirements.

## 23. Troubleshooting ASG launch failure

Postup:

```text
scaling activity reason
→ launch template version
→ AMI existence/permissions/architecture
→ instance type capacity a quota
→ subnet free IPs
→ Security Groups a IAM instance profile
→ KMS/EBS permissions
→ user data/bootstrap
→ health registration
```

Bežné príčiny:

- invalid alebo nedostupná AMI,
- unsupported instance type/AMI architecture,
- insufficient capacity v AZ,
- EC2 quota,
- subnet bez voľných IP,
- chýbajúci `iam:PassRole`,
- KMS key policy blokuje encrypted volume,
- launch template odkazuje na zmazaný resource,
- bootstrap nedokončí health check.

## 24. Troubleshooting replacement loop

Symptóm:

```text
instance launchne
→ krátko InService alebo nikdy healthy
→ ASG ju terminate-ne
→ opakuje sa
```

Over:

- ELB target health reason,
- health path/port/protocol,
- application bind address,
- Security Groups/NACL,
- startup duration vs grace/warmup,
- missing config/secrets,
- disk full alebo permission issue,
- lifecycle hook timeout,
- load balancer AZ/subnet alignment.

Neopravuj loop iba predĺžením grace periodu bez identifikácie root cause.

## 25. Troubleshooting scaling, ktoré nereaguje

Over:

- metric namespace/dimensions,
- alarm state a missing-data behavior,
- policy association,
- min/max hranice,
- suspended ASG processes,
- cooldown/warmup,
- service quotas,
- scaling activity history,
- manual desired-capacity override,
- predictive/scheduled action conflict.

Ak desired capacity rastie, ale `InService` nie, problém je launch/capacity/health, nie scaling signal.

## 26. Bezpečná remediation hierarchy

1. Zachovaj scaling activity, target health a bootstrap evidence.
2. Oprav launch contract alebo dependency.
3. Over jednu canary instance alebo malý refresh checkpoint.
4. Sleduj application SLI a fleet health.
5. Pokračuj v rollout-e.
6. Odstráň chybnú template version až po zachovaní incident evidence.

Ručné SSH úpravy jednej instance nevyriešia fleet desired state.

## 27. SOA-C03 mapovanie

Táto kapitola podporuje najmä:

- **Domain 1** — EC2/ASG metrics, alarms, performance a remediation,
- **Domain 2** — Multi-AZ capacity, health replacement a business continuity,
- **Domain 3** — launch templates, AMIs, Auto Scaling a automated provisioning,
- **Domain 4** — instance roles, IMDSv2, patching a encryption,
- **Domain 5** — subnet placement, Security Groups a load-balancer connectivity.

Praktické drilly:

- ASG launch failure pre subnet IP exhaustion,
- unhealthy targets pre chybný port,
- user-data bootstrap failure,
- KMS-denied encrypted root volume,
- scaling policy s chybnou metric dimension,
- Spot interruption s nefunkčným drainom.

## 28. Anti-patterny

### Pet server v Auto Scaling Group

Ručné zmeny sa stratia pri replacement-e a fleet sa nedá reprodukovať.

### `$Latest` bez release kontroly

Nové instances môžu používať neotestovanú launch template verziu.

### EC2 health ako jediný application health signal

Running VM môže vracať chyby alebo nemať application listener.

### CPU ako univerzálny scaling signal

Workload môže byť limitovaný memory, I/O, queue alebo external dependency.

### Jedna subnet/AZ

ASG názov nezaručuje Multi-AZ odolnosť bez viacerých vhodných subnets a capacity.

### Long-lived access keys v user data

Secrets sa šíria do launch metadata a audit surfaces.

### Scale-in bez drainu

Preruší requests, jobs alebo stateful sessions.

## 29. Kontrolné otázky

1. Aký je rozdiel medzi EC2 instance, launch template a Auto Scaling Group?
2. Ktoré dáta sa stratia pri stop alebo terminate?
3. Prečo zmena launch template neaktualizuje existujúce instances?
4. Ako sa líši EC2 health od ELB application health?
5. Kedy použiť target tracking a kedy queue-based custom metric?
6. Na čo slúži lifecycle hook?
7. Ako navrhneš bezpečný instance refresh?
8. Prečo Spot vyžaduje interruption-tolerant workload?
9. Ktoré evidence preveríš pri ASG launch failure?
10. Prečo ručná oprava jednej instance nie je fleet remediation?

## Glossary impact

Relevantné pojmy: Amazon EC2, EC2 instance, AMI, launch template, instance profile, IMDSv2, instance store, Auto Scaling Group, desired capacity, scaling policy, target tracking, instance warmup, lifecycle hook, instance refresh, mixed instances policy, Spot Instance, Capacity Rebalancing, warm pool, placement group a scaling activity.

## Oficiálna dokumentácia

- [Amazon EC2 User Guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html)
- [Amazon EC2 Auto Scaling User Guide](https://docs.aws.amazon.com/autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html)
- [Health checks for Auto Scaling instances](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-health-checks.html)
- [Auto Scaling lifecycle hooks](https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html)
- [Instance refresh](https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-instance-refresh.html)
- [IAM roles for Amazon EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Security Groups a Network ACLs](security-groups-network-acls.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Elastic Load Balancing →](elastic-load-balancing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
