# Cloud and AWS

Táto sekcia vysvetľuje cloud computing od service a deployment modelov cez AWS global infrastructure, governance, identity, networking, compute, storage, databázy, serverless, containers, observability, operations, security, backup a FinOps. Záver sekcie tvorí prípravný track pre AWS Certified CloudOps Engineer – Associate (`SOA-C03`).

Cieľom nie je memorovať názvy služieb. Každá kapitola vysvetľuje responsibility boundary, exact subject identity, control/data/recovery path, failure domains, security model, cost drivers, operational evidence, recovery a business acceptance.

## Section-wide mentálny model

Všetkých 28 authoritative kapitol používa connected Atlas Payments cloud-adoption subject `CAP-PAY-42` a tvorí jeden learning chain:

```text
business capability a service/deployment responsibility
→ Region/AZ/account placement a shared-responsibility contract
→ scalability, availability, recovery a governance foundation
→ principal/request authorization
→ address, route, egress a packet-filter realization
→ compute fleet, load-balancer a target eligibility
→ object/block/file a database state lifecycle
→ DNS, edge, cache a origin isolation
→ event-driven/serverless a container workload realization
→ operational telemetry, audit a fleet automation
→ cryptographic key, secret, credential a consumer-loaded state
→ protected recovery generation, clean restore a business reconciliation
→ architecture-risk closure a cross-pillar trade-off
→ attributed cost, unit value a realized optimization
→ current SOA-C03 capability contract
→ question-decision reasoning
→ evidence-producing lab experiment
→ subject-bound incident closure
```

Sekcia opakovane oddeľuje stavy, ktoré bývajú nesprávne považované za ekvivalentné:

```text
configured resource ≠ effective runtime capability
service health ≠ business correctness
replication ≠ historical clean recovery
backup completion ≠ recoverable business generation
IAM allow ≠ complete authorization verdict
resource creation ≠ workload readiness
metric existence ≠ correct evidence identity
estimated saving ≠ normalized realized value
practice score ≠ certification readiness
symptom removal ≠ incident closure
```

Každý významný worked scenario preto končí allowed outcome, forbidden outcome, recovery alebo bounded-change validation a earlier controlom.

## Ako sekciu používať

1. Čítaj kapitoly v authoritative poradí; neskoršie modely predpokladajú identity, network, state a recovery boundaries z predchádzajúcich kapitol.
2. Pri service kapitole sleduj exact resource/request/data generation, nie iba názov capability.
3. Pri incidente najprv zachovaj subject a evidence, až potom vykonaj containment alebo repair.
4. Po recovery over business invariant a zakázané paths, nie iba AWS status.
5. SOA-C03 track používaj až po core kapitolách; mapuje current exam guide na už vysvetlené modely a nevytvára paralelný skrátený syllabus.
6. Hands-on a troubleshooting zadania vykonávaj v izolovanom cost-safe sandboxe s explicitným cleanup contractom.

## Predpoklady

Odporúča sa najprv dokončiť:

- [DevOps Foundations](../00-foundations/README.md),
- [Linux and Systems](../01-linux-and-systems/README.md),
- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [Infrastructure as Code and Configuration Management](../07-infrastructure-as-code-and-configuration-management/README.md),
- [Container Fundamentals and Docker](../08-container-fundamentals-and-docker/README.md),
- [Kubernetes](../09-kubernetes/README.md).

## Odporúčané poradie

1. [IaaS, PaaS a SaaS](iaas-paas-saas.md)
2. [Public, private a hybrid cloud](public-private-hybrid-cloud.md)
3. [Regions a Availability Zones](regions-availability-zones.md)
4. [Shared responsibility model](shared-responsibility-model.md)
5. [Scalability, elasticity a fault tolerance](scalability-elasticity-fault-tolerance.md)
6. [High availability a disaster recovery](high-availability-disaster-recovery.md)
7. [AWS Organizations a accounts](aws-organizations-accounts.md)
8. [IAM](iam.md)
9. [VPC, subnets a route tables](vpc-subnets-route-tables.md)
10. [Internet Gateway a NAT Gateway](internet-gateway-nat-gateway.md)
11. [Security Groups a Network ACLs](security-groups-network-acls.md)
12. [EC2 a Auto Scaling](ec2-auto-scaling.md)
13. [Elastic Load Balancing](elastic-load-balancing.md)
14. [S3, EBS a EFS](s3-ebs-efs.md)
15. [RDS](rds.md)
16. [Route 53 a CloudFront](route53-cloudfront.md)
17. [Lambda](lambda.md)
18. [ECS a EKS](ecs-eks.md)
19. [CloudWatch a CloudTrail](cloudwatch-cloudtrail.md)
20. [Systems Manager](systems-manager.md)
21. [KMS a Secrets Manager](kms-secrets-manager.md)
22. [AWS Backup](aws-backup.md)
23. [Well-Architected Framework](well-architected-framework.md)
24. [Cost management a FinOps](cost-management-finops.md)
25. [AWS Certified CloudOps Engineer – Associate (SOA-C03)](cloudops-engineer-associate-soa-c03.md)
26. [CloudOps domain review a timed reasoning](cloudops-domain-review-timed-reasoning.md)
27. [CloudOps hands-on labs](cloudops-hands-on-labs.md)
28. [CloudOps troubleshooting drills](cloudops-troubleshooting-drills.md)

Praktické vykonávacie scenáre sú oddelené v:

- [AWS CloudOps laby](../../labs/aws-cloudops/README.md),
- [AWS CloudOps troubleshooting scenáre](../../troubleshooting/aws-cloudops/README.md).

Po dokončení tejto sekcie pokračuje lineárna dokumentácia sekciou [Observability](../12-observability/README.md).

## Cieľ zvládnutia

### Cloud foundations a governance

- rozlíšiť service a deployment modely podľa responsibility boundary,
- vysvetliť Region, Availability Zone, regional/zonal/global scope a Multi-AZ/multi-Region trade-offy,
- vytvoriť shared-responsibility matrix,
- rozlíšiť scalability, elasticity, fault tolerance, HA a DR,
- definovať BIA, RTO, RPO, failover a failback,
- navrhnúť Organizations, OU, SCP, delegated administration a multi-account model.

### Identity a networking

- vyhodnotiť IAM policies, roles, STS sessions, federation, boundaries, SCPs a cross-account trust,
- diagnostikovať `AccessDenied` cez všetky applicable policy vrstvy,
- navrhnúť VPC CIDR, subnets, route tables, endpoints a hybrid connectivity,
- rozlíšiť IGW, NAT Gateway, egress-only IGW, Security Groups a NACLs,
- diagnostikovať network path cez routes, SG, NACL, Flow Logs a return traffic.

### Compute, storage a data

- prevádzkovať EC2 fleet cez AMI, launch template, ASG, health checks a instance refresh,
- navrhnúť ELB listeners, target groups, health, TLS a draining,
- rozlíšiť S3 object, EBS block a EFS shared-file contracts,
- navrhnúť RDS HA, read scaling, backup, PITR, upgrades a recovery,
- používať Route 53 routing/Resolver a CloudFront caching/origin security.

### Serverless, containers a operations

- navrhnúť Lambda invocation, concurrency, retries, idempotenciu a deployment,
- rozlíšiť ECS a EKS orchestration, identity, capacity a upgrade ownership,
- korelovať CloudWatch operational telemetry s CloudTrail auditom,
- používať Systems Manager na fleet access, patching, configuration a automation,
- spravovať KMS key policies, envelope encryption a Secrets Manager rotation.

### Recovery, architecture a FinOps

- navrhnúť AWS Backup plans, isolated copies, Vault Lock a restore testing,
- odlíšiť backup success od preukázanej application recovery,
- vykonávať evidence-driven Well-Architected reviews cez šesť pilierov,
- vytvoriť improvement plan, risk ownership a milestones,
- analyzovať cost cez allocation, Cost Explorer, Budgets, anomaly detection a Cost Optimization Hub,
- vyhodnotiť rightsizing, commitments, data transfer, telemetry cost a unit economics.

### SOA-C03 readiness

- viazať prípravu na current SOA-C03 exam-guide generation,
- mapovať vedomosti na domény s váhami 22/22/22/16/18,
- riešiť scenario questions podľa outcome, constraints, scope a complete pathu,
- vykonať 65-question/130-minute simuláciu bez time collapse,
- prakticky vykonávať cost-safe AWS laby s evidence a cleanupom,
- diagnostikovať IAM, networking, compute, storage, backup, observability a automation failures,
- vysvetliť, prečo sú distractors nesprávne, nie iba označiť správnu odpoveď,
- uzavrieť practical incident až po original, forbidden, adjacent a second-operation validation.

## Section-level completion gate

Sekcia je pripravená na používateľskú kontrolu až keď:

- všetkých 28 authoritative kapitol prešlo manuálnym strict narrative/mechanism/scenario gate-om;
- connected `CAP-PAY-42` subject zostáva terminologicky konzistentný;
- kapitoly rozlišujú exact subject generations, configured/effective state a technical/business verdict;
- každý komplexný failure cluster obsahuje competing hypotheses, discriminating evidence, containment, authoritative recovery a outcome validation;
- glossary fragments a generated `GLOSSARY.md` sú synchronizované;
- navigation chain je obojsmerný od predchádzajúcej Helm/CKA sekcie až po nasledujúcu Observability sekciu;
- SOA-C03 current facts sú overené proti oficiálnemu AWS exam guide-u;
- generated navigation, glossary a learning-depth audit prejdú bez reportovaného failure-u.

`Ready for user review` znamená ukončenú internú strict revalidation, nie automatické používateľské schválenie alebo garanciu exam výsledku.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| IaaS, PaaS a SaaS | Learning | L2 |
| Public, private a hybrid cloud | Learning | L2 |
| Regions a Availability Zones | Learning | L2 |
| Shared responsibility model | Learning | L2 |
| Scalability, elasticity a fault tolerance | Learning | L2 |
| High availability a disaster recovery | Learning | L2 |
| AWS Organizations a accounts | Learning | L2 |
| IAM | Learning | L2 |
| VPC, subnets a route tables | Learning | L2 |
| Internet Gateway a NAT Gateway | Learning | L2 |
| Security Groups a Network ACLs | Learning | L2 |
| EC2 a Auto Scaling | Learning | L2 |
| Elastic Load Balancing | Learning | L2 |
| S3, EBS a EFS | Learning | L2 |
| RDS | Learning | L2 |
| Route 53 a CloudFront | Learning | L2 |
| Lambda | Learning | L2 |
| ECS a EKS | Learning | L2 |
| CloudWatch a CloudTrail | Learning | L2 |
| Systems Manager | Learning | L2 |
| KMS a Secrets Manager | Learning | L2 |
| AWS Backup | Learning | L2 |
| Well-Architected Framework | Learning | L2 |
| Cost management a FinOps | Learning | L2 |
| AWS Certified CloudOps Engineer – Associate (SOA-C03) | Learning | L2 |
| CloudOps domain review a timed reasoning | Learning | L2 |
| CloudOps hands-on labs | Practicing | L3 |
| CloudOps troubleshooting drills | Practicing | L3 |