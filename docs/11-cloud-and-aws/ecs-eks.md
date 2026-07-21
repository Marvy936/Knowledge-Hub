# ECS a EKS

Amazon ECS a Amazon EKS riešia orchestráciu kontajnerových workloadov, ale používajú odlišný control-plane model. ECS používa AWS-native task a service API. EKS poskytuje managed Kubernetes control plane a zachováva Kubernetes API, controllers a ecosystem. Výber nie je len otázka syntaxe; mení ownership, portability, operations surface, upgrade model a troubleshooting evidence.

## 1. Porovnávací mentálny model

```text
ECS:
task definition → task/service → cluster capacity → ENI/load balancer/logs

EKS:
Kubernetes manifest → API/controller/scheduler → Pod → node/Fargate → CNI/CSI/Service
```

ECS abstrahuje väčšiu časť orchestrátora ako AWS service. EKS abstrahuje Kubernetes control plane, ale zákazník stále vlastní podstatnú časť cluster data plane, add-ons, workload policies a upgrade kompatibility.

## 2. Amazon ECS základné objekty

- **cluster** — logická skupina tasks/services a capacity,
- **task definition** — versionovaný container runtime contract,
- **task** — jedna bežiaca inštancia task definition,
- **service** — controller udržiavajúci desired count tasks,
- **capacity provider** — spôsob poskytnutia compute capacity,
- **service scheduler** — placement, replacement a deployment,
- **container instance** — EC2 node registrovaný do ECS clusteru.

Task definition môže definovať image, CPU, memory, ports, environment, secrets, IAM roles, logging, health check a volumes.

## 3. ECS task definition revisions

Task definition revision je immutable deployment contract. Pri zmene vzniká nová revision.

Rozlišuj:

- **task execution role** — permissions ECS agent/Fargate platformy na image pull, logs alebo secret injection,
- **task role** — permissions application containers,
- **network mode**,
- **requires compatibilities**,
- **runtime platform**,
- **container definitions**,
- **ephemeral a persistent storage**.

Príliš široká execution role nerieši chýbajúce application permissions v task role a naopak.

## 4. ECS service lifecycle

ECS service:

- udržiava desired task count,
- nahrádza stopped tasks,
- vykonáva rolling alebo blue/green deployment podľa konfigurácie,
- registruje targets v load balanceri,
- môže používať service autoscaling,
- rozdeľuje tasks cez Availability Zones podľa dostupnej capacity a constraints.

Deployment môže zlyhať, aj keď nová task definition je validná, napríklad pre:

- image pull,
- task role/execution role,
- subnet IP exhaustion,
- Security Group,
- nedostatok CPU/memory/GPU,
- unsupported platform version,
- load-balancer health,
- secrets/KMS,
- volume attachment.

## 5. ECS capacity providers

Capacity provider určuje, kde tasks bežia. Aktuálna ECS dokumentácia preferuje capacity-provider strategy pred priamym launch-type rozhodovaním.

Možnosti môžu zahŕňať:

- AWS Fargate,
- Fargate Spot,
- ECS Managed Instances,
- EC2 Auto Scaling Group capacity provider.

Strategy používa:

- `base` — minimálny počet tasks na konkrétnom providerovi,
- `weight` — relatívne rozdelenie zvyšných tasks.

Capacity provider nevyrieši application-level graceful shutdown ani state migration.

## 6. ECS na Fargate

Fargate odstraňuje správu host fleet-u. Zákazník stále vlastní:

- task sizing,
- image a vulnerabilities,
- task/execution roles,
- network a Security Groups,
- logging,
- secrets,
- deployment,
- application health,
- cost a quotas.

Každý task v `awsvpc` mode používa ENI/IP contract. Subnet IP capacity preto môže limitovať škálovanie.

## 7. ECS na EC2

Pri EC2 capacity zákazník spravuje alebo spoluspravuje:

- AMI a ECS agent,
- OS patching,
- instance role,
- Auto Scaling Group,
- capacity headroom,
- bin packing,
- drain pri scale-in/maintenance,
- host security a observability.

Cluster autoscaling musí koordinovať pending tasks s ASG capacity. Instance môže mať voľný CPU, ale task nemusí byť placeable pre memory, port, ENI, architecture alebo attribute constraint.

## 8. ECS placement

Placement rozhoduje podľa:

- resource fit,
- Availability Zone,
- attributes,
- constraints,
- strategies ako `spread`, `binpack` alebo `random`,
- capacity-provider availability.

`RESOURCE:MEMORY`, `RESOURCE:CPU`, `RESOURCE:ENI` a port conflicts sú odlišné failure classes.

## 9. ECS networking

`awsvpc` mode poskytuje tasku vlastnú ENI a Security Groups. Výhody:

- task-level network identity,
- jednoduchšia integrácia s load balancerom,
- VPC Flow Logs,
- service-to-service security boundaries.

Diagnostický chain:

```text
DNS/service discovery
→ source task SG
→ route/NACL
→ destination task/target SG
→ listener/port
→ container process
```

## 10. ECS deployment safety

Rolling deployment používa minimum healthy percent a maximum percent. Bezpečný rollout potrebuje:

- immutable image digest,
- health check,
- startup grace,
- deregistration delay,
- graceful SIGTERM handling,
- circuit breaker/rollback podľa use case,
- alarms a deployment evidence.

Blue/green deployment môže používať oddelené target groups a traffic shift. Database alebo durable side effects zostávajú mimo rollback scope-u.

## 11. ECS observability

Sleduj:

- service desired/running/pending count,
- deployment state a events,
- task stopped reason,
- container exit code,
- CPU/memory utilization,
- target health,
- image pull a startup latency,
- ENI/IP capacity,
- application logs a traces,
- capacity provider a ASG metrics.

ECS service events často poskytujú presnejší placement alebo deployment dôvod než samotný container log.

## 12. Amazon EKS mentálny model

Amazon EKS spravuje Kubernetes control plane. Zákazník spravidla vlastní:

- VPC a cluster endpoint access,
- Kubernetes RBAC/access entries,
- nodes alebo Fargate profiles podľa modelu,
- CNI, CSI a ďalšie add-ons podľa zvoleného management modelu,
- workload manifests,
- namespaces, quotas a policies,
- upgrades a version skew,
- logging/metrics,
- backup a recovery workload resources.

Managed control plane neznamená managed application platform bez day-2 operations.

## 13. EKS compute modely

EKS môže plánovať Pods na kombináciu:

- EKS Auto Mode managed nodes,
- managed node groups,
- self-managed nodes,
- AWS Fargate,
- Hybrid Nodes podľa use case.

Každý model mení ownership:

| Model | AWS spravuje | Zákazník spravuje |
|---|---|---|
| Managed node group | node-group lifecycle integráciu | AMI/version policy, scaling, workload fit |
| Self-managed nodes | control plane | celý node fleet lifecycle |
| Fargate | host capacity | Pod sizing, profiles, networking, workload config |
| Auto Mode | väčšiu časť compute/add-on operácií | workload a policy contract |

Aktuálne capabilities treba overovať podľa Regionu, verzie a feature maturity.

## 14. EKS managed node groups

Managed node group používa EC2 Auto Scaling Group a EKS-integrated lifecycle.

Stále rieš:

- node IAM role,
- subnets a capacity,
- instance types,
- labels/taints,
- update strategy,
- PodDisruptionBudgets,
- drain failures,
- add-on compatibility,
- bootstrap a custom AMI contract.

Managed update môže zlyhať pre PDB, unavailable capacity alebo workload, ktorý sa nedá bezpečne evict-nuť.

## 15. EKS Fargate

Fargate profile vyberá Pods podľa namespace a labels. Nie každý Kubernetes workload alebo host-level capability je vhodný pre Fargate.

Over:

- profile selection,
- Pod execution role,
- subnet IP capacity,
- supported volumes/features,
- DaemonSet requirements,
- observability agent model,
- Security Groups a DNS.

Pod `Pending` môže znamenať, že neexistuje matching Fargate profile alebo compute capacity contract.

## 16. EKS networking

Kľúčové vrstvy:

- cluster API endpoint public/private access,
- requester-managed ENIs medzi control plane a VPC,
- Amazon VPC CNI alebo alternatívny kompatibilný model,
- Pod IP consumption,
- Security Groups,
- NetworkPolicy implementation,
- kube-proxy alebo alternate dataplane,
- CoreDNS,
- load balancer controller.

Subnet IP exhaustion môže blokovať Pods aj nodes. Pri VPC CNI sleduj IP allocation, prefix delegation a ENI limits podľa instance type-u.

## 17. EKS identity

Rozlišuj:

- AWS IAM identity pristupujúcu ku cluster API,
- EKS access entries/configuration,
- Kubernetes RBAC authorization,
- node IAM role,
- Pod identity alebo IAM role pre service account podľa modelu,
- service-linked roles.

AWS `AccessDenied` a Kubernetes `Forbidden` sú odlišné vrstvy.

Diagnostika:

```text
AWS caller identity
→ cluster endpoint/network
→ EKS authentication/access entry
→ Kubernetes user/groups
→ RBAC role binding
```

## 18. EKS add-ons

Critical add-ons zahŕňajú napríklad:

- VPC CNI,
- CoreDNS,
- kube-proxy,
- CSI drivers,
- load balancer controller,
- metrics/observability agents.

EKS managed add-on znižuje packaging toil, ale zákazník musí riešiť version compatibility, configuration conflicts, IAM permissions a rollout health.

## 19. EKS upgrades

Upgrade scope:

1. Kubernetes control plane,
2. managed/self-managed nodes,
3. Fargate platform compatibility,
4. EKS add-ons,
5. controllers/operators/CRDs,
6. workload APIs,
7. clients a automation.

Pred upgrade-om:

- skontroluj deprecated APIs,
- add-on matrix,
- node version skew,
- PDB a capacity,
- admission webhooks,
- backup/export critical resources,
- staging/canary cluster alebo node group.

Control-plane rollback nemusí byť dostupný ako jednoduchá operácia. Upgrade plán má preto preferovať compatibility a roll-forward preparedness.

## 20. ECS oproti EKS

### ECS je vhodný, keď

- chceš AWS-native orchestrator,
- nepotrebuješ Kubernetes API/ecosystem,
- preferuješ menší control-plane operations surface,
- deployment a service model ECS pokrýva requirements.

### EKS je vhodný, keď

- potrebuješ Kubernetes API a ecosystem,
- používaš operators, CRDs alebo Kubernetes tooling,
- potrebuješ portability na úrovni orchestrátora,
- tím vie prevádzkovať Kubernetes day-2 vrstvy.

Kubernetes portability nie je automatická application portability; AWS load balancers, IAM, storage a networking môžu zostať provider-specific.

## 21. Security

Spoločné princípy:

- immutable image digest,
- image scanning a signing podľa policy,
- least-privilege workload identity,
- read-only filesystem/capabilities podľa runtime,
- secret injection bez logovania,
- private registry/network path,
- runtime isolation,
- admission/deployment policy,
- audit trail.

ECS task role a EKS Pod identity musia byť oddelené od node/host permissions.

## 22. Cost model

### ECS

- Fargate vCPU/memory/storage duration,
- EC2 capacity a idle headroom,
- load balancer,
- logs,
- data transfer,
- NAT/endpoints.

### EKS

- cluster control plane,
- nodes/Fargate/Auto Mode resources,
- add-ons a load balancers,
- observability,
- storage,
- data transfer,
- operations labor.

Najlacnejší host model nemusí byť najnižší TCO.

## 23. Troubleshooting ECS

### Service tasks zostávajú Pending

Over service events, capacity provider, CPU/memory/ENI/port fit, subnets, quotas a task definition platform.

### Task sa okamžite zastaví

Over stopped reason, essential container exit code, command/entrypoint, secret injection, logs driver a application configuration.

### Deployment sa neukončí

Over target health, deployment minimum/maximum, circuit breaker, old tasks, connection draining a insufficient capacity.

### ImagePull failure

Over ECR permissions v execution role, repository policy, image digest/tag, network/NAT/endpoint a KMS.

## 24. Troubleshooting EKS

### Nodes sa nepripoja

Over node IAM role, bootstrap/user data, cluster endpoint, DNS, Security Groups, route, AMI/version a kubelet logs.

### Pods zostávajú Pending

Over scheduler Events, requests, taints/affinity, node capacity, Fargate profile, PVC topology a subnet IP capacity.

### Pods nemajú network

Over CNI Pods/logs, IPAM, ENI/IP limits, routes, SG/NACL, NetworkPolicy a DNS.

### `kubectl` access zlyhá

Rozlíš network timeout, AWS authentication failure a Kubernetes RBAC `Forbidden`.

### LoadBalancer Service nevznikne

Over controller, IAM, annotations/spec, subnets/tags, SG, quotas a Events.

## 25. SOA-C03 mapovanie

- **Domain 1** — ECS/EKS metrics, logs, task/Pod/node health a remediation.
- **Domain 2** — multi-AZ services, autoscaling, disruption, backup a recovery.
- **Domain 3** — task definitions, deployments, cluster/node provisioning, IaC a image promotion.
- **Domain 4** — task/Pod identity, image security, secrets, encryption, audit a policies.
- **Domain 5** — ENIs, VPC CNI, load balancers, service discovery, Security Groups a hybrid connectivity.

Praktické drilly:

- ECS task execution role nevie pull-nuť image,
- ECS service nemá capacity pre task placement,
- EKS node group update blokuje PDB,
- VPC CNI vyčerpá subnet IPs,
- Kubernetes RBAC povoľuje menej než EKS access entry očakáva,
- load balancer controller nemá IAM permissions,
- Fargate profile nevyberá Pod.

## 26. Anti-patterny

### ECS task role a execution role zlúčené do broad role

Rozširuje blast radius application aj platform operations.

### EKS považovaný za plne spravovanú aplikáciu

AWS spravuje control plane, nie celý cluster a workload lifecycle.

### Mutable image tag v production

Replacement task/Pod môže spustiť iný image pod rovnakou deklaráciou.

### Host patching cez ručné SSH bez fleet replacementu

Vytvára drift a neudržateľnú node population.

### Jeden subnet/AZ pre celý cluster

Orchestrator nevytvorí fault tolerance bez reálnej multi-AZ capacity.

### Diagnostika iba cez application logs

Placement, IAM, CNI, scheduler a service events môžu zlyhať pred štartom aplikácie.

## 27. Kontrolné otázky

1. Aký je rozdiel medzi ECS task definition, task a service?
2. Prečo ECS odporúča capacity-provider strategy?
3. Ako sa líši task role od task execution role?
4. Ktoré resources môžu blokovať ECS task placement?
5. Čo EKS spravuje a čo zostáva zákazníkovi?
6. Ako sa líši managed node group, self-managed nodes a Fargate?
7. Ako odlíšiš EKS authentication od Kubernetes authorization?
8. Prečo môže subnet IP exhaustion blokovať kontajnery?
9. Ktoré vrstvy patria do EKS upgrade-u?
10. Kedy je ECS vhodnejší než EKS?

## Glossary impact

Relevantné pojmy: Amazon ECS, ECS cluster, task definition, ECS task, ECS service, task role, task execution role, capacity provider, Fargate, ECS Managed Instances, task placement, Amazon EKS, managed node group, self-managed node, EKS Auto Mode, EKS Fargate profile, EKS access entry, Pod identity, EKS add-on a VPC CNI.

## Oficiálna dokumentácia

- [Amazon ECS Developer Guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html)
- [ECS clusters](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/clusters.html)
- [ECS services](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html)
- [ECS task definitions](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html)
- [ECS capacity providers](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/capacity-launch-type-comparison.html)
- [Amazon EKS User Guide](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html)
- [EKS compute options](https://docs.aws.amazon.com/eks/latest/userguide/eks-compute.html)
- [EKS managed node groups](https://docs.aws.amazon.com/eks/latest/userguide/managed-node-groups.html)
- [EKS Fargate](https://docs.aws.amazon.com/eks/latest/userguide/fargate.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Lambda](lambda.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CloudWatch a CloudTrail →](cloudwatch-cloudtrail.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
