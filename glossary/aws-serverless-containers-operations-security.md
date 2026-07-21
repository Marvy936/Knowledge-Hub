# AWS serverless, containers, operations and security glossary entries

## AWS Lambda

AWS event-driven compute služba, ktorá spúšťa function code v service-managed execution environments a škáluje invocations podľa event a concurrency modelu. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Lambda execution environment

Izolované runtime prostredie vytvorené AWS Lambda pre initialization a spracovanie jedného alebo viacerých sequential invocations; jeho reuse nie je durable-state garancia. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Cold start — Lambda

Invocation, pri ktorom Lambda musí pripraviť nové execution environment a vykonať runtime, extension a static initialization pred handlerom. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Warm start — Lambda

Invocation v už existujúcom Lambda execution environment, ktorý môže reuse-nuť initialized code, connections a temporary files bez garancie ďalšieho reuse. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Event source mapping — Lambda

Lambda resource s pollermi, ktoré čítajú batches z podporovaných queue alebo stream sources a invoke-ujú function podľa batching, concurrency a retry konfigurácie. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Reserved concurrency — Lambda

Per-function limit, ktorý rezervuje časť regional concurrency poolu a zároveň určuje maximálny počet concurrent invocations danej funkcie. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Provisioned concurrency — Lambda

Počet predinicializovaných Lambda execution environments pripravených na invocations pre konkrétnu version alebo alias s cieľom znížiť startup latency. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Lambda version

Immutable published snapshot Lambda function code a podporovaných configuration properties používaný ako stabilná release identity. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Lambda alias

Pomenovaný pointer na Lambda version, ktorý môže podporovať weighted routing medzi dvoma versions a slúži ako stabilný deployment target. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Partial batch response — Lambda

Event-source-mapping contract umožňujúci označiť iba konkrétne records v batchi ako neúspešné, aby sa nemuselo retryovať celé spracované batch. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Iterator age — Lambda

Metric vyjadrujúca oneskorenie medzi vznikom stream recordu a jeho spracovaním Lambda consumerom; rast signalizuje backlog alebo pomalé spracovanie. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Durable function — Lambda

Lambda execution model pre dlhšie workflowy so service-managed durable state a checkpointingom, odlišný od štandardného krátkodobého invocation contractu. Pozri [Lambda](docs/11-cloud-and-aws/lambda.md).

## Amazon ECS

AWS-native container orchestrator používajúci clusters, task definitions, tasks, services a capacity providers. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## ECS cluster

Logická skupina ECS tasks, services a compute capacity, nad ktorou scheduler vykonáva placement a service lifecycle. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## ECS task definition

Versionovaný immutable template určujúci containers, image, resources, ports, roles, logging, secrets, networking a storage pre ECS task. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## ECS task

Jedna runtime inštancia konkrétnej ECS task definition revision pozostávajúca z jedného alebo viacerých containers. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## ECS service

ECS controller udržiavajúci desired count tasks, vykonávajúci replacement, deployment a integráciu s load balancingom alebo service connectivity. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## ECS capacity provider

ECS abstraction určujúca compute capacity, napríklad Fargate, Fargate Spot, Managed Instances alebo EC2 Auto Scaling Group, a jej rozdelenie cez base/weight strategy. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## ECS task role

IAM role poskytujúca AWS permissions application containers bežiacim v ECS tasku. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## ECS task execution role

IAM role používaná ECS agentom alebo Fargate platformou napríklad na image pull, log delivery a secret injection pred alebo počas štartu tasku. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## AWS Fargate

Service-managed container compute engine pre ECS a EKS, pri ktorom zákazník spravuje workload sizing, identity, networking a application lifecycle bez priamej správy host nodes. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Amazon EKS

Managed Kubernetes služba poskytujúca AWS-managed Kubernetes control plane a integráciu s AWS networking, identity, compute a storage službami. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## EKS managed node group

EKS-integrated skupina EC2 worker nodes založená na Auto Scaling Group-e, pri ktorej AWS koordinuje časť node lifecycle a update operácií. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## EKS Auto Mode

EKS compute a infrastructure management model, v ktorom AWS automatizuje väčšiu časť node, networking, storage a load-balancing operations podľa aktuálnych service capabilities. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## EKS Fargate profile

Configuration vyberajúca Kubernetes Pods podľa namespace a labels a určujúca ich spustenie na AWS Fargate. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## EKS access entry

EKS resource mapujúci AWS IAM principal na cluster access configuration a Kubernetes identity/groups podľa podporovaného access modelu. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## VPC CNI — EKS

Kubernetes networking plugin integrujúci Pod networking s Amazon VPC ENIs a IP addressingom; jeho IPAM a subnet capacity ovplyvňujú Pod scheduling. Pozri [ECS a EKS](docs/11-cloud-and-aws/ecs-eks.md).

## Amazon CloudWatch

AWS observability služba pre metrics, logs, alarms, dashboards, queries, traces a automated operational reactions. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## CloudWatch dimension

Name-value attribute, ktorý spolu s namespace a metric name identifikuje konkrétnu CloudWatch time series. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## CloudWatch alarm

State machine hodnotiaca metric alebo query podľa period, statistic, threshold, evaluation a missing-data pravidiel a voliteľne spúšťajúca actions. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Composite alarm — CloudWatch

CloudWatch alarm kombinujúci boolean stav viacerých underlying alarmov na koreláciu, suppression alebo zníženie alert noise. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## CloudWatch log group

CloudWatch Logs policy, retention, encryption a access boundary obsahujúca jeden alebo viac log streams. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## CloudWatch Logs Insights

Query engine na interaktívnu analýzu CloudWatch log events v zadaných log groups a time window. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Embedded Metric Format

Structured log format, z ktorého CloudWatch extrahuje custom metrics a dimensions bez samostatného per-metric API publish callu. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## AWS CloudTrail

AWS audit služba zaznamenávajúca API a ďalšiu account activity vrátane identity, action, time, request context, resources a výsledku. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## CloudTrail management event

CloudTrail event pre control-plane operáciu nad AWS resources alebo account configuration. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## CloudTrail data event

High-volume CloudTrail event pre data-plane operáciu nad vybranými resource types, ktorý sa zapína cez event selectors. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## CloudTrail Event history

Regionálny recent view management events, typicky za posledných 90 dní, určený na rýchle vyhľadávanie a nie ako dlhodobý central audit archive. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## CloudTrail trail

Configuration zabezpečujúca priebežný výber a delivery CloudTrail events do S3 a voliteľných integrations. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## Organization trail — CloudTrail

Trail vytvorený pre AWS Organization, ktorý centralizuje event coverage member accounts do chráneného audit destination modelu. Pozri [CloudWatch a CloudTrail](docs/11-cloud-and-aws/cloudwatch-cloudtrail.md).

## AWS Systems Manager

AWS operations platforma pre central management managed nodes a AWS resources cez remote commands, sessions, patching, state, inventory, automation a configuration storage. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Managed node — Systems Manager

EC2 alebo non-EC2 machine zaregistrovaná v Systems Manager s funkčnou identity, agentom a network connectivity. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## SSM Agent

Node-side agent komunikujúci so Systems Manager control plane a vykonávajúci podporované command, session, inventory, patch a state operations. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Run Command — Systems Manager

Capability na vzdialené vykonanie versionovaného command documentu na jednom alebo viacerých managed nodes s targetingom, rate controls a per-node outputom. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Session Manager

Systems Manager capability poskytujúca IAM-authorized interactive shell alebo port-forwarding sessions bez potreby inbound SSH/RDP portu. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## State Manager

Systems Manager capability periodicky aplikujúca idempotentné document associations na target managed nodes na udržiavanie desired configuration. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Patch Manager

Systems Manager capability pre patch scan, installation, baselines, policies a compliance reporting na managed nodes. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Automation runbook — Systems Manager

Versionovaný YAML alebo JSON workflow obsahujúci sequential Automation actions, parameters, branching, outputs, approvals a AWS resource operations. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Systems Manager rate controls

Concurrency a error-threshold nastavenia obmedzujúce paralelný rollout command alebo automation operácie a zastavujúce ďalšie targets po failure prahu. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## Parameter Store

Systems Manager configuration store pre hierarchické String, StringList a KMS-protected SecureString parameters. Pozri [Systems Manager](docs/11-cloud-and-aws/systems-manager.md).

## AWS KMS

Managed cryptographic key service poskytujúca KMS keys, policy/grant authorization a cryptographic operations pre applications a AWS services. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## KMS key

Logical AWS KMS resource reprezentujúci cryptographic key, jeho metadata, policy, state, aliases a key-material lifecycle. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Customer managed key — KMS

KMS key v zákazníckom account-e, ktorého policy, aliases, rotation, enablement, grants a deletion lifecycle spravuje zákazník. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Key policy — KMS

Resource policy priamo pripojená ku KMS key, ktorá je fundamentálnou súčasťou autorizácie management a cryptographic operations. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## KMS grant

Programaticky vytvorený permission objekt umožňujúci grantee principalovi konkrétne cryptographic operations na KMS key, často používaný AWS service integrations. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Envelope encryption

Model, v ktorom data key šifruje application data a dlhodobejší KMS key šifruje samotný data key. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Data key — KMS

Symmetric key vygenerovaný cez KMS na local encryption dát, poskytovaný ako plaintext pre okamžité použitie a ako encrypted copy na uloženie. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Encryption context — KMS

Non-secret key-value context kryptograficky viazaný na podporovanú KMS encrypt/decrypt operation a použiteľný v policy conditions a audite. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Multi-Region key — KMS

Súvisiace KMS key resources v rôznych Regions zdieľajúce key material a key ID properties, ale s oddelenými policies, grants a lifecycle. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## AWS Secrets Manager

Managed secret lifecycle služba pre encrypted storage, retrieval, versioning, staging labels, rotation a monitoring credentials a ďalších secret values. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Secret version — Secrets Manager

Immutable secret value revision identifikovaná version ID a voliteľnými staging labels. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Secret staging label

Pomenovaný movable label, napríklad `AWSCURRENT`, `AWSPREVIOUS` alebo `AWSPENDING`, ktorý označuje úlohu konkrétnej secret version v lifecycle. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Secret rotation

Proces vytvorenia novej secret version, zmeny credentials v target service, overenia funkčnosti a presunu current staging labelu. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Managed rotation — Secrets Manager

Rotation model, pri ktorom podporovaná managed service integrácia riadi rotation bez zákazníckej Lambda rotation function. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Lambda rotation — Secrets Manager

Rotation model používajúci Lambda function na create, set, test a finish kroky pre secret a target service. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Secret resource policy

Resource-based policy na Secrets Manager secret-e určujúca principals a conditions pre access, najmä pri cross-account modeli. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).

## Secret replication — Secrets Manager

Service capability vytvárajúca regionálne replicas secretu s vlastným per-Region encryption a status contractom. Pozri [KMS a Secrets Manager](docs/11-cloud-and-aws/kms-secrets-manager.md).
