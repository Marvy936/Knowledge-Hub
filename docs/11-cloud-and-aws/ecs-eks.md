# Amazon ECS a Amazon EKS

Amazon ECS a Amazon EKS realizujú desired container workload na compute, network, storage a identity resources. ECS používa AWS-native task/service control plane. EKS poskytuje managed Kubernetes control plane a zachováva Kubernetes API, controllers a ecosystem. Rozdiel nie je „jednoduché verzus pokročilé“. Mení sa authoritative desired state, scheduler evidence, capacity ownership, identity chain, upgrade surface a recovery procedure.

Spoločný orchestration lifecycle:

```text
business release intent
→ immutable image a workload specification
→ orchestrator desired-state generation
→ scheduler placement verdict
→ compute/network/storage capacity realization
→ workload identity a configuration injection
→ container process startup
→ readiness a service/target eligibility
→ traffic a business outcome
→ autoscaling/replacement/update/drain
→ acceptance, rollback alebo retirement
```

Orchestrator môže správne udržiavať desired count a application napriek tomu zlyhávať. `RUNNING`, `Ready` alebo `Available` sú iba medzistavy. Closure potrebuje klientsky a business dôkaz.

## 1. Exact container orchestration subject

Atlas Payments používa subject `CTR-PAY-42` pre release 7.17.0:

```text
account = 100000000042
Region = eu-central-1
image = 100000000042.dkr.ecr.eu-central-1.amazonaws.com/payments-api
image digest = sha256:pay-api-7-17-0
architecture = linux/amd64
configuration generation = CFG-PAY-52
secret generation = SEC-PAY-39
database/proxy generation = PROXY-10
load-balancer generation = ALB-PAY-18
business journey = authorize payment P-901

ECS realization =
  cluster = payments-prod
  service = payments-api
  task definition = payments-api:118
  deployment generation = ECS-DEP-73
  capacity provider = payments-managed-instances-v4
  network mode = awsvpc
  task role = ROLE-ECS-PAY-21
  task execution role = ROLE-ECS-EXEC-14
  desired count = 40

EKS realization =
  cluster = payments-eks-prod
  Kubernetes version generation = EKS-VER-16
  namespace = payments
  Deployment = payments-api
  ReplicaSet generation = RS-PAY-219
  Service/Ingress generation = SVC-PAY-31
  access-entry generation = EKS-ACCESS-12
  service account = payments-api
  Pod Identity association = PODID-PAY-9
  compute generation = NODEPOOL-PAY-17
  VPC CNI generation = CNI-31
  desired replicas = 40

required outcome =
  40 eligible instances across at least three AZs
  release 7.17.0 serves payment authorization within SLO
  task/Pod receives only workload permissions
  scale-out and replacement preserve capacity and connection drain

forbidden outcomes =
  mutable tag starts a different binary under the same release identity
  scheduler declares placement success but workload is not target-eligible
  node/host role leaks to application workload
  scale-out exhausts subnet IPs and removes healthy headroom
  EKS control-plane update is treated as full cluster/application upgrade
  rollback deletes or corrupts durable payment state
```

Incident evidence musí identifikovať image digest, task definition alebo Kubernetes object generation, scheduler verdict, selected capacity, ENI/Pod IP, node/task/Pod identity, startup/readiness, target health, deployment cohort, drain state a business request result.

## 2. ECS a EKS majú odlišný authoritative control plane

### ECS

```text
task definition revision
→ task alebo service desired state
→ ECS scheduler
→ capacity provider
→ task placement
→ ENI/volume/logging/identity
→ service deployment a target registration
```

Task definition je immutable runtime template. Service je controller, ktorý udržiava desired count a deployment. ECS service events a stopped reasons sú authoritative evidence pre placement a lifecycle pred štartom application logu.

### EKS

```text
Kubernetes manifests/API objects
→ admission
→ controllers
→ scheduler
→ Pod binding
→ kubelet/container runtime
→ CNI/CSI
→ Service/Ingress/controller
→ workload readiness a rollout
```

EKS spravuje Kubernetes control plane. Zákazník stále vlastní workload manifests, namespaces, RBAC/access model, policies, add-on compatibility, compute model podľa voľby, observability, upgrade readiness a application recovery.

Kubernetes API portability neznamená automatickú portability siete, IAM, storage, load balancerov alebo operations modelu.

## 3. Workload specification je release contract

### ECS task definition

Revision definuje najmä:

- image digest a containers;
- CPU, memory, ports a runtime platform;
- command/entrypoint;
- task a execution role;
- environment, secrets a logging;
- network mode;
- health checks;
- ephemeral alebo persistent storage.

Nová revision nemení existujúce tasks. Service deployment musí vytvoriť novú task cohortu a vyradiť starú.

### EKS workload objects

Deployment, StatefulSet, Job alebo iný controller vytvára Pod templates a následné runtime objects. Exact release subject zahŕňa manifest generation, image digest, ConfigMap/Secret generation, ServiceAccount, requests/limits, probes, volumes, topology a policy.

Zmena ConfigMap bez zmeny Pod template nemusí automaticky nahradiť všetky Pods. Mutable external configuration môže preto vytvoriť mixed population bez viditeľnej rollout revision.

## 4. Scheduler rozhoduje iba v rámci viditeľného contractu

Scheduler nevie, že „payments-api potrebuje bezpečne autorizovať platby“, pokiaľ to nie je vyjadrené cez resources, constraints, topology, probes a policies.

ECS placement vyhodnocuje resource fit, attributes, ENI/port requirements, AZ, constraints, strategies a capacity-provider availability.

Kubernetes scheduler vyhodnocuje requests, taints/tolerations, affinity, topology, volumes a ďalšie scheduling constraints. CNI alebo image pull však môže zlyhať až po bindingu Podu na Node.

Preto:

```text
scheduled/placed
≠ process started
≠ ready
≠ target healthy
≠ business accepted
```

## 5. Capacity má viac rozmerov než CPU

Container workload potrebuje súčasne:

```text
compute
+ memory
+ architecture/accelerator
+ ENI alebo Pod IP
+ ports
+ storage topology
+ AZ placement
+ quota
+ startup headroom
```

Host môže mať voľný CPU, ale task alebo Pod sa nezmestí pre memory, ENI density, IP exhaustion, incompatible architecture, taint, PVC topology alebo quota.

Capacity planning musí obsahovať replacement a rollout headroom. Fleet dimenzovaný presne na steady-state desired count nemá pri update priestor na start-before-stop.

## 6. ECS capacity providers

Capacity provider spája ECS scheduler s compute modelom. Strategy používa `base` a `weight` na rozdelenie tasks.

Relevantné modely:

- AWS Fargate a Fargate Spot;
- Amazon ECS Managed Instances;
- EC2 Auto Scaling Group capacity provider.

Aktuálne ECS Managed Instances poskytujú EC2-based capacity, pri ktorej AWS spravuje významnú časť instance provisioning, scaling, software/OS patching a maintenance lifecycle. Zákazník stále vlastní task sizing, workload compatibility, capacity-provider requirements, service deployment, identity, network, application health a business validation.

Capacity provider nie je application autoscaler. Service desired count a underlying host capacity sú samostatné control loops, ktoré sa musia stretnúť.

## 7. Fargate, Managed Instances a vlastné EC2 menia ownership

| Model | AWS preberá | Zákazník naďalej vlastní |
|---|---|---|
| Fargate | host provisioning a host OS lifecycle | task sizing, image, roles, network, storage, deployment, health, cost |
| ECS Managed Instances | veľkú časť EC2 instance selection, scaling, patching a maintenance | workload requirements, capacity-provider contract, tasks/services a application outcome |
| ASG capacity provider | ECS/ASG integration podľa konfigurácie | AMI, agent, OS patching, ASG, drain, headroom a host security |

„Managed“ neznamená, že každá task definition sa dá umiestniť. ENI density, architecture, accelerator, volume a Region/AZ support zostávajú reálne constraints.

## 8. ECS service deployment je cohort exchange

Rolling deployment používa desired count, minimum healthy percent a maximum percent na súbežnú old/new population.

```text
old cohort healthy
→ new tasks admitted a placed
→ process startup
→ container/LB health
→ new cohort eligible
→ old tasks deregister a drain
→ old tasks stop
```

Deployment circuit breaker alebo alarm-based failure detection môže rollout zastaviť alebo rollbacknúť podľa configuration. Nevracia však external database writes ani provider side effects.

Blue/green model oddeľuje replacement task set a traffic shift. Stále potrebuje immutable image, target-group identity, drain, business canary a rollback eligibility.

## 9. ECS task role a execution role sú odlišné identity

**Task execution role** používa ECS agent alebo Fargate platforma na image pull, log delivery a secret injection podľa feature contractu. **Task role** používa application container na AWS API calls.

```text
platform startup action
→ task execution role

application SDK call
→ task role credentials
```

Broad execution role nevyrieši chýbajúce application permission. Broad task role zase zbytočne rozširuje blast radius každého compromised containeru.

Na EC2 capacity treba navyše oddeliť container instance role. Application nesmie získavať node/instance credentials ako fallback.

## 10. ECS networking a target eligibility

Pri `awsvpc` mode dostáva task vlastnú ENI/IP a Security Groups. Packet path:

```text
client/LB
→ listener/rule/target group
→ task ENI Security Group
→ route/NACL
→ container port/process
→ response path
```

Scale-out spotrebúva subnet IPs. Task môže byť `RUNNING`, ale target zostane unhealthy pre wrong port, SG, health path, startup delay alebo application dependency.

Service discovery DNS success len dokazuje name resolution. Neoveruje listener, task identity ani application readiness.

## 11. EKS compute modely

EKS môže používať:

- EKS Auto Mode;
- managed node groups;
- self-managed nodes;
- AWS Fargate;
- podporované hybrid modely.

EKS Auto Mode automatizuje väčšiu časť compute, networking, storage a load-balancing infrastructure a používa service-managed node lifecycle. Zákazník stále vlastní workload specification, Pod disruption a NodePool policies, application compatibility, identity, data, SLO a acceptance.

Managed node group koordinuje časť EC2 node lifecycle-u, ale tím stále rieši AMI/version policy, instance types, labels/taints, scaling, PDB, capacity a add-on compatibility.

Self-managed nodes dávajú najviac kontroly a najväčšiu host responsibility. Fargate odstraňuje node fleet, ale obmedzuje host-level capabilities a stále spotrebúva subnet IPs.

## 12. EKS control plane nie je celý cluster

Kubernetes request prejde viacerými nezávislými vrstvami:

```text
AWS caller
→ EKS endpoint/network
→ EKS authentication a access entry
→ Kubernetes user/groups
→ RBAC/admission
→ API object persistence
→ controller reconciliation
→ scheduler
→ Node/kubelet/runtime
→ CNI/CSI
→ Service/Ingress dataplane
```

`aws eks` API success neznamená, že Kubernetes authorization prešla. `kubectl Forbidden` nie je VPC Security Group problém. `Deployment Available` zase neoveruje external ALB, DNS ani business journey.

## 13. EKS access a workload identity

Rozlišuj:

- cluster IAM role a service-linked roles;
- IAM principal pristupujúci ku clusteru;
- EKS access entry/policy alebo Kubernetes group mapping;
- Kubernetes RBAC;
- node IAM role;
- Pod Identity alebo iný supported workload identity model;
- service account a application permissions.

EKS access entry rieši human/automation access ku Kubernetes API. Pod Identity rieši AWS permissions workloadu. Nie sú to dve mená pre tú istú vec.

EKS Pod Identity používa association medzi IAM role a Kubernetes service accountom; podľa compute modelu potrebuje supporting agent alebo service-managed integration. Application SDK musí používať supported credential chain. Node role nesmie byť implicitný workload credential source.

## 14. EKS networking je scheduling aj runtime dependency

Pri Amazon VPC CNI Pods typicky spotrebúvajú VPC IP capacity podľa node/ENI/prefix modelu. Chain:

```text
Pod scheduled
→ CNI allocates address
→ network namespace/routes created
→ Security Group/NetworkPolicy verdicts
→ CoreDNS/service discovery
→ Service/load-balancer dataplane
→ application connection
```

Subnet free IPs, instance ENI limits, prefix delegation, warm IP/prefix targets a CNI generation ovplyvňujú počet reálne spustiteľných Pods.

NetworkPolicy deklarácia nemá účinok bez dataplane implementation, ktorá ju enforce-uje. Security Groups a Kubernetes NetworkPolicy pozorujú odlišnú identity a vrstvu.

## 15. EKS storage a topology

PersistentVolume claim môže byť bound, ale Pod sa nemusí dať umiestniť do AZ kompatibilnej s volume. CSI controller/node components, IAM, KMS, topology a mount permissions sú samostatné gates.

Stateful workload update navyše potrebuje:

- stable identity;
- quorum/replication awareness;
- ordered drain;
- fencing;
- backup/recovery;
- application-consistent validation.

Orchestrator replacement nesmie byť jediným recovery mechanizmom pre corrupted durable state.

## 16. Add-ons a controllers rozširujú upgrade graph

Kritické components môžu zahŕňať:

- VPC CNI;
- CoreDNS;
- kube-proxy alebo alternate dataplane;
- CSI drivers;
- load balancer controller;
- metrics/logging/security agents;
- admission webhooks a operators;
- CRDs.

Managed add-on znižuje packaging toil, ale configuration conflicts, IAM, compatibility a rollout health zostávajú. Add-on môže byť `ACTIVE`, kým časť Pods na novej Node generation zlyháva.

## 17. EKS upgrade je compatibility program

Upgrade subject:

```text
current control-plane version
→ target supported version
→ deprecated API/CRD inventory
→ add-on/controller matrix
→ Node/runtime generations
→ admission/client compatibility
→ workload disruption/capacity
→ staged transition
→ application/business acceptance
```

Control plane, nodes, Fargate/Auto Mode infrastructure, add-ons, controllers, CRDs a workloads sa nemenia ako jedna atomická operácia. Simple control-plane rollback nemusí byť k dispozícii; prioritou je compatibility evidence a pripravený roll-forward.

PDB chráni application availability iba ak je správne nastavený a existuje replacement capacity. Príliš prísny PDB môže blokovať safe node drain. Príliš voľný PDB môže povoliť plošný výpadok.

## 18. Autoscaling má tri odlišné otázky

1. Koľko workload replicas je potrebných?
2. Existuje pre ne schedulable compute/network/storage capacity?
3. Je downstream schopný nový concurrency absorbovať?

ECS Service Auto Scaling alebo Kubernetes HPA mení desired workload count. Capacity provider, Cluster Autoscaler, Karpenter/Auto Mode alebo node-group scaling realizuje host capacity podľa zvoleného modelu. VPA alebo rightsizing mení resource request model.

Scale-out podľa CPU môže zhoršiť incident, ak bottleneck je database connection, provider quota alebo subnet IP. Business queue age a downstream saturation musia byť súčasťou guardrailov.

## 19. Drain a termination sú correctness boundary

Bezpečný drain:

```text
mark workload ineligible for new traffic
→ stop new leases/jobs
→ complete alebo hand off in-flight work
→ flush durable state/telemetry
→ deregistration delay alebo endpoint removal
→ process termination
→ host/node termination
```

SIGTERM alebo Kubernetes termination signal sám negarantuje, že load balancer prestal posielať traffic. ECS task protection, deployment settings, PDB, preStop, termination grace a LB deregistration musia vytvoriť konzistentný časový contract.

Pri queue consumerovi treba oddeliť message lease/visibility od process termination. Node drain počas spracovania môže vytvoriť duplicate delivery.

## 20. Observability podľa orchestration vrstvy

### ECS evidence

- service desired/running/pending counts;
- deployment/task-set generation;
- service events;
- task stopped reason a container exit code;
- capacity-provider a host capacity;
- ENI/IP a target health;
- image pull/startup latency;
- task role/execution role denies;
- application/business metrics.

### EKS evidence

- API object generation, ownerReferences a Events;
- controller conditions;
- scheduler decisions;
- Pod status, container states a exit codes;
- Node conditions a kubelet/runtime;
- CNI/CSI/add-on logs;
- EndpointSlice/Service/Ingress/controller state;
- access/RBAC audit;
- application/business metrics.

Application logs často neexistujú, keď failure nastal pred process startom. Orchestrator events sú preto first-class evidence, nie doplnok.

## 21. Worked failure: scale-out vyčerpá subnet IPs

Po marketingovej kampani sa desired count zvýši z 24 na 40. ECS service aj EKS Deployment nedosiahnu požadovanú kapacitu.

### Competing hypotheses

1. cluster nemá dostatok CPU alebo memory;
2. image revision 7.17.0 sa nedá pull-nuť;
3. task execution role alebo Pod Identity zlyháva;
4. ALB health check odmieta nový release;
5. subnet IP alebo ENI capacity blokuje runtime networking;
6. EKS CNI generation je chybná.

### Discriminating evidence

ECS service events uvádzajú `RESOURCE:ENI`; časť tasks zostáva `PENDING` ešte pred image pullom. EKS scheduler niektoré Pods bindne na Nodes, ale Pod Events následne ukazujú `FailedCreatePodSandBox` a VPC CNI `ipamd` nevie prideliť adresu.

EC2 subnet evidence ukazuje:

```text
subnet-a free IPv4 = 2
subnet-b free IPv4 = 1
subnet-c free IPv4 = 3
```

CPU na existujúcich ECS instances a EKS Nodes je len 45 %. Pridanie ďalších Nodes bez nového address space-u spotrebuje ďalšie IPs a situáciu zhorší. Root cause je shared VPC address capacity, nie nedostatok CPU.

### Evidence-preserving containment

- zastaví sa ďalší neobmedzený workload/node scale-out;
- healthy old cohort zostáva target-eligible;
- rollout 7.17.0 sa pozastaví bez mazania pending evidence;
- batch/noncritical consumers sa dočasne obmedzia;
- traffic sa podľa capacity presunie na zdravé AZ cohorts;
- nevykoná sa broad SG alebo CNI reset bez hypotézy.

### Authoritative recovery

1. vytvorí sa nová subnet/address generation s dostatočným headroomom;
2. ECS capacity provider a service network configuration dostanú approved subnets;
3. EKS node/NodePool a VPC CNI IPAM model sa upravia podľa instance density a prefix strategy;
4. nové canary tasky/Pods sa vytvoria v každej AZ;
5. overí sa ENI/Pod IP, DNS, target health, workload identity a dependency path;
6. desired count sa zvyšuje vo vlnách;
7. old subnet generation sa vyradí až po drain a address-release verification.

### Acceptance verdict

Recovery nie je uzavretá pri `RUNNING=40` alebo `AvailableReplicas=40`. Potrebný je dôkaz, že:

- všetkých 40 workloads má approved image digest a configuration;
- placement je rozdelený cez tri AZs;
- subnet free-IP headroom spĺňa rollout a failure budget;
- každý task/Pod je target-eligible a obslúži exact payment request;
- workload používa task role alebo Pod Identity, nie host role;
- scale-in/drain nevytvorí dropped ani duplicate payment;
- forbidden scale test nedosiahne IP exhaustion skôr než alert/guardrail;
- old capacity a network generation je bezpečne vyradená.

Skorší control: release capacity gate počíta workload ENI/Pod IP demand, node overhead, rollout surge, AZ-loss reserve a expected autoscaling ceiling pred zmenou desired count-u.

## 22. ECS troubleshooting walkthrough

### Task zostáva `PENDING`

Najprv identifikuj service/deployment/task-definition/capacity-provider generation. Potom rozlíš resource placement, subnet/IP, quota, architecture a capacity-provider state. Image, secret a process logiku rieš až keď task prešiel placementom.

### Task sa okamžite zastaví

Použi stopped reason, essential container exit code, platform logs, command/entrypoint, secret injection a health. `CannotPullContainerError` nie je application crash.

### Deployment sa neukončí

Porovnaj new/old cohort, target health, deployment limits, circuit-breaker evidence, startup grace, drain a headroom. Desired count bez eligible targets nie je successful rollout.

## 23. EKS troubleshooting walkthrough

### `kubectl` nefunguje

Rozlíš DNS/network k EKS endpointu, AWS authentication/access entry a Kubernetes RBAC. `Unauthorized` a `Forbidden` majú odlišné observation points.

### Pod zostáva `Pending`

Najprv scheduler Events: requests, taints, affinity, topology, PVC a compute. Ak je Pod bound, ale nie `Running`, pokračuj kubelet, image pull, CNI, CSI a runtime.

### Pod je `Ready`, ale klient zlyháva

Over Service selector, EndpointSlice cohort, target registration, load-balancer controller, SG/NetworkPolicy, port/protocol a application request. Probe path môže byť zelený, kým business path zlyháva.

### Node update stojí

Over PDB, unavailable capacity, taints, local/stateful workloads, finalizers, drain timeout, add-on compatibility a replacement Node readiness. Force eviction bez state/availability modelu môže incident zväčšiť.

## 24. ECS alebo EKS: rozhodovací model

Vyber podľa required control-plane contractu:

| Otázka | ECS skôr vyhovuje | EKS skôr vyhovuje |
|---|---|---|
| Authoritative API | AWS-native task/service model | Kubernetes API/controllers/CRDs |
| Operations surface | menší orchestrator surface | širší Kubernetes ecosystem a day-2 ownership |
| Portability requirement | image/application portability | orchestrator API/tooling portability s AWS integrations |
| Custom controllers/operators | obmedzenejší model | natívny Kubernetes extension model |
| Team capability | AWS/ECS operations | Kubernetes platform engineering |
| Upgrade burden | task/platform/capacity lifecycle | control plane + nodes + add-ons + APIs + workloads |

Rozhodnutie sa nemá robiť podľa popularity. Porovnáva sa total operational ownership, reliability requirements, ecosystem need, portability boundary, security model a TCO.

## 25. Security a cost boundaries

Security:

- immutable image digest, provenance, scan a signing policy;
- least-privilege task/Pod identity;
- oddelené host, execution a workload roles;
- private registry a controlled egress;
- secret redaction a rotation;
- runtime capabilities/read-only filesystem podľa workloadu;
- admission/deployment policy;
- audit trail a break-glass access.

Cost:

```text
workload compute duration
+ idle/surge capacity
+ control plane
+ load balancers
+ storage
+ logs/metrics/traces
+ NAT/data transfer
+ operations labor
```

Fargate alebo managed capacity môže znížiť host toil a zvýšiť unit compute cenu. Self-managed density môže znížiť infra účet a zvýšiť patching, upgrade a incident cost. Najnižší resource price nie je automaticky najnižší TCO.

## 26. Kontrolné otázky

1. Aký je spoločný orchestration lifecycle ECS a EKS?
2. Čo tvorí exact ECS/EKS deployment subject?
3. Prečo scheduler success nie je application acceptance?
4. Ako sa líši ECS task role, execution role a container-instance role?
5. Čo mení Fargate, ECS Managed Instances a ASG capacity provider?
6. Kde sa odlišuje EKS access entry od Pod Identity?
7. Prečo môže scale-out zlyhať pri voľnom CPU?
8. Ktoré vrstvy patria do EKS upgrade graphu?
9. Ako sa koordinuje process termination, target drain a queue lease?
10. Aký dôkaz uzatvára container deployment na business úrovni?

## Glossary impact

Relevantné pojmy: container orchestration subject, desired-state generation, placement verdict, capacity realization, target-eligibility cohort, orchestration acceptance verdict, workload identity chain, rollout headroom, address-capacity boundary, drain completion a cluster upgrade graph.

## Oficiálna dokumentácia

- [Amazon ECS Developer Guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html)
- [Amazon ECS services](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html)
- [Amazon ECS capacity providers](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/capacity-launch-type-comparison.html)
- [Amazon ECS Managed Instances](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ManagedInstances.html)
- [ECS deployment circuit breaker](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-circuit-breaker.html)
- [Amazon EKS User Guide](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html)
- [EKS compute options](https://docs.aws.amazon.com/eks/latest/userguide/eks-compute.html)
- [EKS Auto Mode](https://docs.aws.amazon.com/eks/latest/userguide/automode.html)
- [EKS access entries](https://docs.aws.amazon.com/eks/latest/userguide/access-entries.html)
- [EKS Pod Identity](https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html)
- [EKS cluster upgrades](https://docs.aws.amazon.com/eks/latest/userguide/update-cluster.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Lambda](lambda.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CloudWatch a CloudTrail →](cloudwatch-cloudtrail.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
