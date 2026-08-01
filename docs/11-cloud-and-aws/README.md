# Cloud and AWS

Táto sekcia vysvetľuje cloud computing od service a deployment modelov cez AWS global infrastructure, governance, identity, networking, compute, storage, databázy, serverless, containers, observability, operations, security, backup a FinOps. Záver sekcie tvorí prípravný track pre AWS Certified CloudOps Engineer – Associate (`SOA-C03`).

Cieľom nie je memorovať názvy služieb. Každá kapitola vysvetľuje responsibility boundary, exact subject identity, control/data/recovery path, failure domains, security model, cost drivers, operational evidence, recovery a business acceptance.

## Section-wide mentálny model

Všetkých 30 authoritative kapitol používa connected Atlas Payments cloud-adoption subject `CAP-PAY-42` a tvorí jeden learning chain:

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
29. [Praktický AWS projekt od lokálneho artifactu po overenú Lambda release](aws-practical-walkthrough.md)
30. [AWS troubleshooting](aws-troubleshooting.md)

## Hlavný AWS walkthrough a troubleshooting

[Praktický AWS projekt od lokálneho artifactu po overenú Lambda release](aws-practical-walkthrough.md) vytvára cost-bounded serverless release v sandbox account-e. Spája STS identity, IAM execution role, DynamoDB conditional idempotency, reproducible Lambda zip a `CodeSha256`, immutable published versions, alias-based exposure, CloudWatch logs, CloudTrail management evidence, broken candidate, alias compare-and-swap recovery a úplný cleanup.

[AWS troubleshooting](aws-troubleshooting.md) používa preserve-first postup naprieč account/region/principal identity, IAM authorization, VPC path, EC2/ASG/ELB, Lambda/ECS/EKS, storage a databases, messaging, telemetry, KMS/secrets, CloudFormation a backup/restore. Connected incident ukazuje false-green Lambda release, stale alias a duplicate business operation.

Ďalšie praktické vykonávacie scenáre zostávajú v:

- [AWS CloudOps laby](../../labs/aws-cloudops/README.md),
- [AWS CloudOps troubleshooting scenáre](../../troubleshooting/aws-cloudops/README.md).

Po dokončení tejto sekcie pokračuje lineárna dokumentácia sekciou [Observability](../12-observability/README.md).

## Čo má čitateľ po sekcii vedieť

Čitateľ má vedieť začať explicitnou AWS account, region, principal a resource identity a až potom vyhodnocovať service status. Musí odlíšiť control-plane configuration od data-plane a application outcome-u, vysvetliť IAM allow/deny chain, prejsť celý VPC path a rozlíšiť compute, storage, database, serverless, container, telemetry a recovery failure domains.

Pri release-i má vedieť viazať source artifact na immutable AMI, image digest alebo Lambda version, oddeliť publication od alias/traffic exposure a overiť loaded runtime generation aj business operation. Pri incidente má zachovať request IDs, CloudTrail, CloudWatch a service-native evidence, riešiť unknown outcomes stabilnou operation identity a uzatvoriť recovery forbidden-path a second-operation testom.

Cost, security a recovery sú súčasťou každého designu. Sandbox lab musí mať tags, budget/cost hranicu a cleanup. Backup alebo replication status sa nepovažuje za recovery dôkaz bez izolovaného restore-u a application validation.

## Stav

Všetkých 30 authoritative kapitol vrátane samostatného AWS walkthroughu a troubleshooting kapitoly je pripravených na používateľskú kontrolu. Stav neznamená automatické používateľské schválenie, certifikačný výsledok ani runtime overenie labu v každom AWS account-e. SOA-C03 fakty a tool-specific syntax zostávajú viazané na uvedené official source a toolchain generation.
