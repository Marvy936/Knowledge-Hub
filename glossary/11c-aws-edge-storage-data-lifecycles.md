# AWS edge, storage and database lifecycle glossary entries

## Traffic-distribution subject

Versionovaná identita load balancera, listenera, TLS policy, ordered rule, target-group cohortu, target health/drain attributes, zonálneho placementu a business requestu použitá na ELB rozhodovanie. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Viewer connection — ELB

Client-to-load-balancer connection s vlastným DNS, source, listener, Security Group, TLS a request contractom; pri ALB je oddelená od backend target connection. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Backend target connection

Nová load-balancer-to-target connection vyhodnocovaná podľa target portu, source identity, SG/NACL, backend TLS/listener a application readiness, nezávisle od viewer connection. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## First-match routing verdict — ALB

Výsledok ordered listener-rule evaluation, pri ktorom prvá matching rule určí action; broad higher-priority rule môže shadowovať presnejšiu canary rule. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Target eligibility set

Množina targets, ktoré sú registered, v enabled AZ scope, v použiteľnom lifecycle state a spĺňajú health/attribute contract pre konkrétnu target group. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Target health oracle

Konkrétny protocol, port, path, matcher, timeout, interval a threshold contract odpovedajúci, či target môže bezpečne prijať nový traffic; nie všeobecný business-health dôkaz. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Load-balancer fail-open

Availability behavior, pri ktorom ELB môže pri all-unhealthy alebo inom service-defined nedostatku healthy targets routovať aj na unhealthy/all registered targets namiesto úplného blackhole. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Weighted-exposure evidence

Request-level dôkaz viazaný na matched rule, target group, target/release identity a stickiness/connection cohort, ktorý overuje reálne canary exposure namiesto samotnej configured weight. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Drain completion — load balancer

Dôkaz, že target už neprijíma nové requests, dokončil alebo odovzdal in-flight work, uzavrel business acknowledgement a môže byť bezpečne deregistrovaný a terminated. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Load-balancing acceptance verdict

Closure dôkaz, že exact request matchuje approved listener/rule generation, používa eligible zonálny target cohort, dokončí business outcome a forbidden host/path/direct-target/fail-open/drain outcomes zostanú kontrolované. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Storage subject

Versionovaná identita business data, authoritative ownera, S3 object/version, EBS volume/snapshot/checkpoint alebo EFS filesystem/access-point generation, encryption, retention a recovery objective-u. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Object-generation identity

S3 object identity viazaná minimálne na bucket, key, version ID, checksum, encryption a retention metadata; key bez version ID môže označovať meniacu sa current version. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Current-version semantics

S3 behavior, pri ktorom request bez version ID pracuje s current version alebo delete markerom daného key, nie automaticky s business-authoritative historickou version. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Version-bound manifest

Immutable manifest generation, ktorá referencuje exact S3 object keys, version IDs a checksums a tým vytvára konzistentnejší multi-object publication contract. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Replication acceptance — S3

Dôkaz, že exact eligible object version bola úspešne prenesená do intended destination podľa replication rule, IAM/KMS a status contractu; source PUT success ho nenahrádza. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Block commit boundary

Application/filesystem/database moment, po ktorom required writes a metadata boli flushnuté alebo checkpointnuté na EBS tak, aby recovery semantics boli explicitné. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Application-consistent snapshot set

EBS snapshot alebo coordinated multi-volume snapshots viazané na application checkpoint/LSN po quiesce/flush procedure, nie iba crash-consistent block capture. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Volume initialization readiness

Stav restored EBS volume-u, pri ktorom required snapshot blocks sú dostupné s predvídateľným performance contractom cez default initialization, Fast Snapshot Restore, provisioned initialization rate alebo completed pre-read. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Time-to-full-performance

Recovery interval od incident decisionu po restored storage/application schopnú spĺňať production latency a throughput, nie iba po resource state `available`. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Shared-file namespace

EFS file/directory identity zdieľaná concurrent NFS clients s POSIX ownership, permission, locking a publication semantics. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Access-point identity enforcement

EFS behavior, pri ktorom access point obmedzí root path a nahradí client operation UID/GID configured POSIX identity, pričom filesystem policy, SG a file permissions zostávajú samostatnými gates. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Mount authorization chain

End-to-end EFS path `DNS → mount target → route/SG/NACL → NFS/TLS → IAM/filesystem policy → access point → POSIX permission → operation`. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Storage recovery acceptance verdict

Service-specific restore dôkaz viažuci správnu S3 version, EBS checkpoint/full-performance alebo EFS namespace/permissions k application a business outcome-u vrátane forbidden data identity/access paths. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Database subject

Versionovaná identita RDS deploymentu, endpointu, writer/reader topology, engine/schema/parameter/TLS/secret/KMS generations, application pool/proxy pathu a business transactionu. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Writer-generation identity

Exact current RDS writer resource, AZ, endpoint mapping, engine/schema/parameter generation a failover timeline, ktoré určujú write authority. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Endpoint remap — RDS

Failover transition, pri ktorom logical RDS endpoint zostáva rovnaký, ale DNS mapping začne smerovať na promoted primary/writer; clients musia obnoviť DNS a connections. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Unknown commit outcome

Stav, keď database mohla transaction durable commitnúť, ale application nedostala acknowledgement pre connection failure; vyžaduje idempotency a reconciliation pred retryom. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Business idempotency boundary

Stable operation identity a uniqueness/reconciliation contract pokrývajúci database changes aj external side effects, nie iba jeden local table insert. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Readable-replica freshness contract

Maximum tolerovaný replication lag a explicitný set business reads, ktoré smú používať reader endpoint/replica bez porušenia read-after-write alebo decision correctness. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Promotion authority — database

Riadené rozhodnutie, ktorá replica/Region/topology sa stáva jediným accepted writerom po failover/DR, vrátane fencing, endpoint cutover a failback reconciliation. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Database restore generation

Nový RDS instance/cluster vytvorený zo snapshotu alebo PITR s exact restore time, KMS, parameter, network, secret, schema a application compatibility identity. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Blue/Green switchover subject

Versionovaný blue a green RDS topology, replication state, engine/schema/parameter delta, cutover preconditions, application/proxy endpoints a post-write rollback eligibility. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## Database recovery acceptance verdict

Closure dôkaz, že writer/connection topology, transaction outcome, data invariants, idempotency, performance a forbidden stale-reader/old-writer/master/public paths sú po failover alebo restore správne. Pozri [Amazon RDS](docs/11-cloud-and-aws/rds.md).

## DNS-answer subject

Exact queried name/type, public/private resolver context, hosted-zone/delegation/DNSSEC generation, routing policy, health state, authoritative answer a TTL used for DNS reasoning. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Resolver-cache cohort

Množina clients alebo recursive resolvers, ktoré počas TTL/application cache lifetime používajú rovnakú DNS answer generation a preto nemusia prejsť na nový target súčasne. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## DNS failover realization

End-to-end transition `health detection → authoritative Route 53 verdict → resolver/client cache expiry → reconnect → secondary capacity/data/business acceptance`. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Edge-delivery subject

Versionovaná identita Route 53 aliasu, CloudFront distribution/certificate, ordered behavior, cache/origin policies, edge code, origin a exact viewer/business requestu. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Behavior-routing verdict

Prvá matching CloudFront cache behavior, ktorá pre normalized viewer path určí origin, methods, viewer policy, cache key, origin request policy a edge-function chain. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Cache-key identity

Path a selected query/header/cookie/compression inputs, podľa ktorých CloudFront rozhodne, či dve viewer requests môžu bezpečne zdieľať jednu cached representation. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Representation isolation

Požiadavka, aby viewer requests s rozdielnou tenant/user/language alebo inou content-changing identity nemohli zdieľať nesprávnu cached response. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Origin-request-only input

Header, cookie alebo query value forwardovaná CloudFront originu cez origin request policy, ale nezahrnutá v cache key; nesmie meniť cacheable representation bez ďalšieho bezpečného contractu. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Minimum-TTL override

CloudFront behavior, pri ktorom positive cache-policy minimum TTL vynúti caching aspoň na tento čas aj pri origin directives `no-cache`, `no-store` alebo `private`. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## OAC origin authorization

CloudFront-to-S3 REST origin contract, v ktorom Origin Access Control podpisuje SigV4 request a bucket/KMS policy povoľuje exact distribution/service path bez public bucket accessu. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## VPC-origin path

Private CloudFront-to-supported-ALB/NLB/EC2 origin connection realizovaná cez CloudFront VPC origin configuration, subnet/SG a service-supported regional lifecycle. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Edge-delivery acceptance verdict

Closure dôkaz, že approved DNS/distribution/behavior/cache/origin generations poskytujú správnu a izolovanú representation, origin authorization a recovery behavior pri zachovaných forbidden tenant/public/stale/wrong-origin paths. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).
