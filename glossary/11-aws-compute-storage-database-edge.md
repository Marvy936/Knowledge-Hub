# AWS compute, storage, database and edge glossary entries

## ALB listener rule

Prioritizované Layer 7 pravidlo Application Load Balancera, ktoré vyhodnocuje host, path, header, method, query alebo source-IP conditions a vykoná forward, redirect, fixed-response alebo podporovanú authentication action. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Amazon CloudFront

AWS content-delivery service, ktorá distribuuje a cache-uje content cez global edge locations a smeruje cache misses na nakonfigurované origins. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Amazon EC2

AWS compute služba poskytujúca virtuálne instances s voliteľnou instance family, image, networking, storage, IAM a lifecycle konfiguráciou. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Amazon EBS

Zonálny durable block-storage service pre EC2 a podporované AWS compute služby, sprístupnený ako block device s voliteľným typom, IOPS, throughputom, snapshotmi a encryption. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Amazon EFS

Managed NFS file service poskytujúci shared POSIX filesystem pre viac clients cez mount targets vo VPC. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Amazon RDS

Managed relational database service, ktorý spravuje časť database infrastructure, backup, maintenance a failover lifecycle-u, pričom zákazník zostáva zodpovedný za schema, queries, access, data a application recovery. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Amazon Route 53

AWS authoritative DNS, domain registration, health-check a DNS traffic-steering service s public/private hosted zones a hybrid Resolver capabilities. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Amazon S3

Regional object-storage service ukladajúci objects identifikované bucketom a key, dostupné cez API a podporujúce storage classes, lifecycle, versioning, replication a retention controls. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## AMI — Amazon Machine Image

Versionovateľný EC2 boot-image a block-device contract používaný pri vytváraní nových instances. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## Application Load Balancer — ALB

Layer 7 Elastic Load Balancing variant pre HTTP/HTTPS traffic s listener rules, host/path routing, target groups a application health checks. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## application-consistent snapshot

Snapshot vytvorený po koordinovanom flush, quiesce alebo engine-native checkpoint-e tak, aby obnovené dáta reprezentovali validný application transaction state. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Auto Scaling Group — ASG

EC2 fleet controller udržiavajúci minimum, desired a maximum capacity cez launch template, health evaluation, replacement a scaling policies. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## automated backup — RDS

RDS-managed backup a transaction-log retention používaný na point-in-time recovery v rámci nakonfigurovaného retention windowu. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Blue/Green Deployment — RDS

RDS workflow pre vytvorenie synchronizovaného staging environmentu a riadený switchover pri podporovaných engine a configuration zmenách. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## cache behavior — CloudFront

Ordered distribution rule mapujúca path pattern na origin a definujúca viewer protocol, allowed methods, cache policy, origin request policy, headers a private-content behavior. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## cache hit ratio — CloudFront

Podiel requests obslúžených z CloudFront cache bez potreby fetchu z originu; ovplyvňuje latency, origin load a cost. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## cache key — CloudFront

Kombinácia pathu a vybraných query strings, headers, cookies alebo compression variantu, podľa ktorej CloudFront rozhoduje, či requests zdieľajú cached response. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## cache policy — CloudFront

Policy určujúca cache-key inputs a minimum, default a maximum TTL pre CloudFront cache behavior. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Capacity Rebalancing — EC2 Auto Scaling

Auto Scaling capability, ktorá môže proaktívne spustiť náhradu Spot Instance pri zvýšenom interruption risku, pričom workload stále potrebuje drain a idempotentný recovery model. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## CloudFront Functions

Lightweight JavaScript edge runtime pre viewer-request a viewer-response transformácie s nízkou latency a obmedzeným execution modelom. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## connection draining — ELB

Riadené ukončovanie targetu, pri ktorom load balancer prestane posielať nové requests a ponechá existujúce connections alebo requests dobehnúť v rámci deregistration contractu. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## DB instance — RDS

Konkrétne managed database environment s engine, instance class, storage, network, parameter a backup configuration. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## DB parameter group — RDS

Versionovateľná sada engine parameters priradená DB instance alebo clusteru, s dynamic alebo reboot-required semantics podľa konkrétneho parameteru. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## DB snapshot — RDS

Customer-retained point-in-time storage snapshot RDS database používaný na restore, migration alebo dlhšiu retenciu mimo automated-backup lifecycle-u. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## DB subnet group — RDS

Kolekcia VPC subnets vo viacerých Availability Zones, z ktorej RDS vyberá database placement. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## delete marker — S3

Špeciálna current version vytvorená pri delete requeste vo versioning-enabled buckete, ktorá skryje predchádzajúcu object version bez jej okamžitého odstránenia. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## deregistration delay — ELB

Target-group interval, počas ktorého deregistrovaný target zostáva v draining stave pre dokončenie existujúcich requests alebo connections. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## desired capacity — Auto Scaling

Počet instances alebo weighted capacity units, ktoré sa Auto Scaling Group v aktuálnom čase snaží udržať. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## DNS delegation

Publikovanie NS records v parent DNS zone, ktorým sa authoritative zodpovednosť za domain alebo subdomain odovzdá konkrétnym name serverom. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## DNSSEC

DNS security extension používajúca cryptographic signatures a chain of trust na overenie authenticity a integrity DNS odpovedí. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## EBS Multi-Attach

Capability vybraných Provisioned IOPS EBS volumes umožňujúca pripojenie k viacerým podporovaným instances v rovnakej AZ; vyžaduje cluster-aware filesystem/application a fencing. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## EBS snapshot

Point-in-time block snapshot EBS volume-u používaný na restore, copy, migration alebo backup; bez application koordinácie môže byť iba crash-consistent. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## EBS volume

Persistent block device v jednej Availability Zone, ktorý možno attachnúť k EC2 instance v rovnakej AZ. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## EC2 instance

Konkrétna spustená alebo zastavená virtual machine identity vytvorená z AMI a launch configuration, s vlastným instance ID, network interfaces, storage a lifecycle stavom. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## EFS access point

Application-specific EFS entry point vynucujúci root directory a voliteľnú POSIX identity pre mounted clienta. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## EFS mount target

ENI-based VPC endpoint v konkrétnej Availability Zone, cez ktorý clients pristupujú k EFS filesystemu protokolom NFS. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Elastic Load Balancing — ELB

AWS managed load-balancing family zahŕňajúca Application, Network a Gateway Load Balancers. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Elastic Volumes — EBS

EBS capability na online zmenu veľkosti, typu, IOPS alebo throughputu podporovaného volume-u, po ktorej môže byť potrebné samostatne rozšíriť partition a filesystem. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## fail-open — load balancer

Failure behavior, pri ktorom load balancer za určitých all-target-unhealthy podmienok stále routuje traffic na dostupné registrované targets namiesto úplného zastavenia trafficu. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## failover routing — Route 53

DNS routing policy s primary a secondary records, ktorá mení odpovede podľa health state-u a active-passive designu. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Fast Snapshot Restore — EBS

Platená EBS feature enabled pre konkrétny snapshot a Availability Zone, ktorá umožňuje volumes vytvorené zo snapshotu poskytovať plný provisioned výkon bez lazy first-read initialization latency. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Gateway Load Balancer — GWLB

Elastic Load Balancing variant pre transparentné smerovanie flows cez virtual network appliances pomocou GENEVE encapsulation. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## health-check matcher — ELB

Sada HTTP success codes alebo iné protocol-specific kritérium, podľa ktorého target-group health check vyhodnotí odpoveď ako úspešnú. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## hosted zone — Route 53

Container authoritative DNS records pre konkrétny public alebo private DNS namespace. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## IAM database authentication — RDS

RDS authentication model pre podporované engines, pri ktorom client generuje krátkodobý signed token cez IAM namiesto dlhodobého database passwordu. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## IMDSv2

Token-based druhá verzia EC2 Instance Metadata Service používaná na získanie instance metadata a temporary role credentials s lepšou ochranou proti niektorým SSRF a proxy útokom. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## instance profile — EC2

IAM container, cez ktorý sa jedna IAM role pripája k EC2 instance a poskytuje jej temporary credentials cez metadata service. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## instance refresh — Auto Scaling

Riadený Auto Scaling workflow postupne nahrádzajúci fleet instances podľa novej launch template alebo desired configuration pri zachovaní nastavenej healthy capacity. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## instance store — EC2

Host-local ephemeral block storage, ktorého dáta sa môžu stratiť pri stop, termination alebo host failure. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## instance warmup — Auto Scaling

Interval reprezentujúci čas, kým newly launched instance dosiahne plnú application a metric readiness pre scaling decisions. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## invalidation — CloudFront

Požiadavka na odstránenie object pathov z CloudFront edge caches pred prirodzenou TTL expiráciou. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Lambda@Edge

CloudFront-integrated Lambda runtime pre pokročilé viewer alebo origin request/response transformácie distribuované do edge locations podľa service modelu. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## latency routing — Route 53

DNS routing policy vyberajúca resource v AWS lokalite, ktorá má podľa Route 53 latency measurements najnižšiu očakávanú latency pre query source. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## launch template — EC2

Versionovaný EC2 launch contract definujúci AMI, instance type, network, storage, IAM, metadata, user data a ďalšie launch settings. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## lifecycle hook — Auto Scaling

Auto Scaling extension, ktorá pozastaví launch alebo termination transition, aby automation vykonala bootstrap, registration, drain alebo evidence-preservation action. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## listener — ELB

Load-balancer frontend contract prijímajúci connections na konkrétnom protocol a porte a vykonávajúci default alebo rule-selected action. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Multi-AZ DB cluster — RDS

RDS deployment model s writer DB instance a dvoma readable instances v troch Availability Zones pri podporovaných engines, určený pre HA a read capacity. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Multi-AZ DB instance deployment — RDS

RDS high-availability model s primary DB instance a synchronously maintained standby v inej Availability Zone, ktorý pri klasickom modeli neobsluhuje reads. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## multipart upload — S3

S3 upload protocol rozdeľujúci veľký object na samostatne prenášané parts a dokončený explicitným complete requestom. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## Network Load Balancer — NLB

Layer 4 Elastic Load Balancing variant pre TCP, TLS, UDP a vysoký connection throughput so zonálnymi IP capabilities podľa configuration. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## option group — RDS

Engine-specific RDS configuration object povoľujúci vybrané database features alebo integrations s vlastným lifecycle, restart a licensing modelom. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Origin Access Control — OAC

CloudFront mechanismus na SigV4-signed private access k podporovanému S3 originu bez verejného bucketu. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## origin group — CloudFront

CloudFront primary/secondary origin pair s definovanými failover status codes pre podporovaný origin-failover workflow. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## origin request policy — CloudFront

Policy určujúca headers, cookies a query strings posielané CloudFront originu bez ich automatického zahrnutia do cache key. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Origin Shield — CloudFront

Voliteľná regionálna caching vrstva pred originom, ktorá konsoliduje cache misses z viacerých edge locations a znižuje duplicate origin fetches. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## placement group — EC2

EC2 placement constraint optimalizujúci cluster latency/throughput, spread failure isolation alebo partitioned distributed-system topology. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## point-in-time recovery — RDS

Obnova novej RDS database do vybraného času v automated-backup recovery windowe pomocou snapshots a retained transaction logs. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## read replica — RDS

Asynchronously replicated readable database copy používaná na read scaling, reporting, migration alebo promotion-based recovery. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## replication lag — RDS

Časový alebo log-position rozdiel medzi source database a asynchronously applying read replica, ktorý určuje stale-read a recovery exposure. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## response headers policy — CloudFront

CloudFront policy pridávajúca alebo upravujúca CORS, security alebo custom response headers nezávisle od origin application code. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## RDS endpoint

DNS name poskytujúci stable logical connection identity pre RDS database, ktorého resolved address sa môže zmeniť pri failover-e alebo maintenance. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## RDS failover

Riadený alebo automatický presun writer/primary database role na standby alebo reader target pri Multi-AZ failure alebo maintenance udalosti. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## RDS Proxy

Managed database proxy a connection-pooling vrstva pre podporované RDS/Aurora engines, ktorá znižuje connection churn a pomáha pri burst a failover scenarios. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## Route 53 alias record

AWS-specific DNS record smerujúci zone apex alebo subdomain na podporovaný AWS resource či iný record bez bežného CNAME obmedzenia apexu. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Route 53 health check

Externá, alarm-based alebo calculated health evaluation používaná pri Route 53 DNS traffic steeringu a failover-e. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## Route 53 Resolver

AWS recursive DNS capability pre VPCs a hybrid DNS, zahŕňajúca inbound/outbound endpoints a forwarding rules. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## S3 Lifecycle

Bucket policy mechanizmus automatizujúci storage-class transitions, expiration current/noncurrent versions a cleanup incomplete multipart uploads. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## S3 Object Lock

S3 WORM retention mechanizmus chrániaci konkrétne object versions pomocou governance/compliance retention alebo legal hold. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## S3 Replication

Asynchronous copy mechanism pre S3 object versions medzi buckets v rovnakom alebo inom Regioni podľa replication rules a IAM/KMS permissions. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## S3 storage class

Per-object S3 storage tier s konkrétnym availability, retrieval latency, request, minimum-duration a cost contractom. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## S3 Versioning

Bucket capability zachovávajúca viac object versions a používajúca delete markers na recovery po overwrite alebo delete operations. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## scaling activity — Auto Scaling

Auditovateľný záznam Auto Scaling launch, terminate alebo capacity-change pokusu vrátane statusu a failure reasonu. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## scaling policy — Auto Scaling

Policy meniaca desired capacity Auto Scaling Groupu podľa target tracking, step, schedule, prediction alebo iného demand contractu. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## signed cookie — CloudFront

CloudFront private-content authorization token v cookies, ktorý môže oprávniť clienta na skupinu paths alebo resources podľa policy a expiry. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## signed URL — CloudFront

Časovo alebo policy obmedzená CloudFront URL podpísaná trusted keyom pre access ku konkrétnemu private resource-u. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## slow start — ELB

ALB target-group mechanismus postupne zvyšujúci traffic newly healthy targetu počas warmup intervalu. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## Spot Instance

EC2 capacity s nižšou cenou a možnosťou interruption zo strany AWS, vhodná pre interruption-tolerant workloady s drain, checkpoint a fallback modelom. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## stickiness — ELB

Load-balancer behavior smerujúci opakované requests alebo flows klienta na rovnaký target počas definovaného obdobia. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## storage autoscaling — RDS

RDS capability automaticky zvýšiť allocated database storage do nastavenej maximálnej hranice pri nedostatku free space podľa service rules. Pozri [RDS](docs/11-cloud-and-aws/rds.md).

## target group — ELB

Backend registration, protocol, port, health-check a traffic-lifecycle contract medzi load balancerom a jednou alebo viacerými targets. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## target health — ELB

Per-target-group stav vyjadrujúci, či registrovaný target prešiel health checks a je vhodný na routing trafficu. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## target tracking — Auto Scaling

Dynamic scaling policy snažiaca sa udržať zvolenú metric približne na target hodnote zmenou desired capacity. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## throughput mode — EFS

EFS configuration určujúca, ako filesystem získava a účtuje dostupný aggregate throughput, napríklad Bursting, Provisioned alebo Elastic. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## volume initialization — EBS

Proces načítania alebo zápisu všetkých blocks volume-u vytvoreného zo snapshotu alebo copy pred dosiahnutím plného stabilného výkonu. Pozri [S3, EBS a EFS](docs/11-cloud-and-aws/s3-ebs-efs.md).

## warm pool — Auto Scaling

Pool predinicializovaných EC2 instances mimo aktívnej `InService` capacity používaný na skrátenie scale-out startup latency. Pozri [EC2 a Auto Scaling](docs/11-cloud-and-aws/ec2-auto-scaling.md).

## weighted forwarding — ALB

ALB listener action rozdeľujúca traffic medzi viac target groups podľa relatívnych weights, často používaná pri canary alebo migration workflowe. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).

## weighted routing — Route 53

DNS routing policy rozdeľujúca odpovede medzi records podľa relatívnych weights, bez presnej request-level percentuálnej garancie kvôli DNS caching. Pozri [Route 53 a CloudFront](docs/11-cloud-and-aws/route53-cloudfront.md).

## zonal shift

Riadený presun podporovaného regional-service trafficu preč z impaired Availability Zone, ktorý stále vyžaduje zdravú capacity a dependencies v zostávajúcich AZ. Pozri [Elastic Load Balancing](docs/11-cloud-and-aws/elastic-load-balancing.md).
