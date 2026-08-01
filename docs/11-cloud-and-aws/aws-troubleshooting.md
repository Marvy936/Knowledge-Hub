# AWS troubleshooting

AWS troubleshooting začína presnou identitou, nie názvom služby. Rovnaký resource name môže existovať v inom account-e alebo regione, alias môže smerovať na inú version, DNS meno na iný load balancer a IAM principal môže používať session policy odlišnú od svojej identity policy. Pred akoukoľvek zmenou preto zaznamenaj account, partition, region, principal/session, resource ARN/ID, control-plane generation, runtime artifact a business operation.

Preserve-first model:

```text
používateľský alebo operational symptom
→ account/region/principal/resource/request identity
→ UTC timeline a recent changes
→ control-plane configuration
→ data-plane/runtime observation
→ authorization, network, compute, data a dependency hypotheses
→ CloudTrail/CloudWatch/service-native evidence
→ bounded containment
→ authoritative configuration alebo release recovery
→ original, forbidden a second-operation verification
```

## Minimálny incident manifest

Incident manifest fixuje identity skôr, než sa symptoms interpretujú alebo začne containment. AWS CLI profile a shell region sú iba klientsky context; authoritative subject vzniká až z STS caller identity, partition, account, region, resource ARN alebo ID, request ID a relevantnej configuration alebo artifact generation. Pri assumed role sa zaznamenáva aj session name, source identity, credential expiry a session policy boundary.

Manifest musí odlíšiť caller identity od workload identity. Operátor môže používať správny account, zatiaľ čo Lambda, EC2 instance profile, ECS task role alebo EKS Pod používa inú principal generation. Zozbierané network, KMS, deployment a business fields vytvoria korelačný contract pre CloudTrail, CloudWatch a service-native read-back; samotný zoznam resource names bez UTC timeline a immutable IDs nie je incident subject.

```bash
aws sts get-caller-identity
aws configure list
printf 'AWS_REGION=%s AWS_PROFILE=%s\n' "${AWS_REGION:-}" "${AWS_PROFILE:-}"
```

Zaznamenaj:

```text
AWS partition, account a organization/OU
region a availability zone
principal ARN, session name, source identity a credential expiry
request ID, operation ID a UTC čas
resource ARN/ID, tags a configuration revision
artifact/version/digest alebo AMI ID
VPC/subnet/route/SG/NACL/endpoints
KMS key, secret/config generation
deployment/Auto Scaling/ECS/EKS/Lambda generation
business outcome a retry identity
```

`aws sts get-caller-identity` je read-back aktuálneho credentialu. Neoveruje, že aplikácia, instance profile, Pod role alebo Lambda execution role používa rovnakú identity.

## 1. API request skončil `AccessDenied`

AWS authorization môže zahŕňať identity policy, resource policy, permission boundary, session policy, organization SCP/RCP, VPC endpoint policy, KMS key policy a service-specific controls. Explicitný deny má prednosť; implicitný deny znamená, že neexistuje použiteľný allow.

Najprv zachovaj celý error vrátane action, resource a request ID. Potom over principal:

```bash
aws sts get-caller-identity
aws iam get-role --role-name ROLE_NAME
aws iam list-role-policies --role-name ROLE_NAME
aws iam list-attached-role-policies --role-name ROLE_NAME
```

Competing hypotheses:

```text
policy nepovoľuje exact action/resource
explicitný deny v SCP, boundary alebo resource policy
temporary session má užšiu session policy
credential patrí inému accountu/role
resource ARN alebo region je iný
KMS key policy/grant chýba
iam:PassRole nie je povolené alebo role service trust nesedí
VPC endpoint policy request odmieta
ABAC tag/condition context sa nezhoduje
```

IAM Policy Simulator môže pomôcť pri identity policies, ale nereprezentuje každú runtime vrstvu a external state. CloudTrail event ukáže evaluated identity, request parameters a error, ak bol event zaznamenaný.

Neopravuj problém pridaním `Action: "*", Resource: "*"`. Vytvor minimum capability, over positive action a forbidden adjacent action. Po incidentnej broad permission ju odstráň a revoke-ni session, ak je to potrebné.

## 2. Credential fungoval a náhle expiroval

Temporary credentials majú access key, secret, session token a expiry. Application môže refreshovať cez SDK provider chain, ale staticky skopírované environment variables alebo file credentials expirovanú session neobnovia.

Kontroluj:

```text
credential source a provider chain
role ARN a session name
expiry a clock
OIDC/SAML/web-identity trust
IMDS/ECS task credentials endpoint
session duration a max session duration
SDK refresh errors
```

Na EC2 over IMDSv2 token a role metadata bez zverejnenia secretu. V ECS/EKS/Lambda používaj service-native identity evidence. Clock skew môže spôsobiť signature errors, no vypnutie TLS alebo opakovaný retry nie je oprava.

## 3. Resource „neexistuje“, ale console ho ukazuje

Najčastejšie ide o account/region/partition, eventual listing, alias alebo soft-deleted state.

```bash
aws sts get-caller-identity
aws ec2 describe-regions --all-regions
aws resourcegroupstaggingapi get-resources --region REGION
```

Service APIs majú vlastný regional/global model. IAM, Route 53 a CloudFront majú odlišný scope než EC2 alebo Lambda. CLI default region môže byť iný než console selector.

Používaj ARN/ID, nie iba display name. Pri Route 53 hosted zone, KMS alias, Lambda alias alebo Secrets Manager staging label rozlišuj name od versioned targetu.

## 4. EC2 instance je running, ale nedostupná

Rozlož path:

```text
client DNS a route
→ internet/VPN/TGW/Direct Connect path
→ route table
→ NACL
→ security group
→ ENI a source/destination check
→ host firewall/listener
→ application readiness
→ dependency/business outcome
```

Read-back:

```bash
aws ec2 describe-instances --instance-ids i-... | jq .
aws ec2 describe-route-tables --filters Name=association.subnet-id,Values=subnet-...
aws ec2 describe-security-groups --group-ids sg-...
aws ec2 describe-network-acls --filters Name=association.subnet-id,Values=subnet-...
```

Security groups sú stateful a NACLs stateless. Otvorený SG port nepreukazuje route, NACL return path ani host listener. Public IP bez internet gateway route a subnet/network policy nie je internet reachability.

Použi Systems Manager Session Manager, ak je agent/role/network pripravený; nezväčšuj SSH exposure iba kvôli diagnostike. VPC Reachability Analyzer vie analyzovať modelovaný network path, ale neoveruje application process alebo runtime packet loss.

## 5. Load balancer je healthy, používateľ dostáva chybu

Rozlišuj ALB/NLB listener, rules, target group, target health, DNS, TLS certificate a application behavior.

```bash
aws elbv2 describe-load-balancers --names NAME
aws elbv2 describe-listeners --load-balancer-arn ARN
aws elbv2 describe-rules --listener-arn ARN
aws elbv2 describe-target-health --target-group-arn TG_ARN
```

Healthy target znamená, že health-check request splnil matcher. Nemusí používať rovnaký host header, path, auth, payload, dependency alebo business oracle ako používateľský request.

Competing hypotheses:

```text
DNS/alias smeruje na starý LB
listener/rule priority alebo host/path mismatch
certificate/SNI/chain problém
health check je plytký
target group port/protocol mismatch
security group return path
cross-zone/zone target availability
application 4xx/5xx alebo timeout
WAF/rate limit
```

Correlate ALB access log alebo connection log, target application log a request ID. `502`, `503` a `504` majú odlišné probable boundaries; neinterpretuj ich všetky ako „backend down“.

## 6. Auto Scaling nahrádza instances alebo neškáluje

Read-backni group, launch template version, scaling activities, lifecycle hooks a health sources:

```bash
aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names ASG
aws autoscaling describe-scaling-activities --auto-scaling-group-name ASG --max-items 20
aws ec2 describe-launch-template-versions --launch-template-id lt-... --versions '$Default' '$Latest'
```

`$Latest` a `$Default` sú mutable selectors. ASG môže používať inú version než operátor očakáva. Instance refresh má vlastný ID, preferences a checkpoints.

Neustále replacement môže spôsobiť failing ELB health, bootstrap/user-data failure, capacity/spot interruption, image architecture, IAM/SSM/network alebo lifecycle hook timeout. Zdravá instance na SSH nie je dôkazom, že splnila ASG health a application acceptance.

## 7. Lambda function je Active, invocation zlyháva

Control-plane `State=Active` a successful update dokazujú accepted function configuration. Invocation failure môže byť handler/import, execution role, VPC networking, dependency, timeout, concurrency, payload alebo alias/version mismatch.

```bash
aws lambda get-function --function-name FUNCTION
aws lambda get-alias --function-name FUNCTION --name live
aws lambda invoke --function-name FUNCTION:live --payload file://event.json response.json > invoke.json
jq '{StatusCode,FunctionError,ExecutedVersion}' invoke.json
```

Kontroluj `CodeSha256`, `RevisionId`, environment, role, timeout, memory, VPC config, layers, architectures, reserved/provisioned concurrency a alias target. `$LATEST` test nepreukazuje published version alebo alias.

CloudWatch logs používaj s request ID. Timeout po business commite je unknown outcome; read-backni DynamoDB/RDS/event ledger pred retryom. VPC-enabled Lambda bez NAT alebo VPC endpointu môže stratiť internet/AWS API connectivity podľa target service a DNS/network designu.

## 8. ECS task alebo service sa nespustí

Rozlišuj placement, image pull, task execution role, task role, network, secrets, container start, health a deployment circuit breaker.

```bash
aws ecs describe-services --cluster CLUSTER --services SERVICE
aws ecs list-tasks --cluster CLUSTER --service-name SERVICE
aws ecs describe-tasks --cluster CLUSTER --tasks TASK_ARN
```

Service events často obsahujú prvú diskriminačnú správu. `CannotPullContainerError`, `ResourceInitializationError`, stopped reason a container reason patria iným boundaries.

Execution role získava image/secrets/log capability pre agent; task role používa application. Ich zámena vedie buď k start failure, alebo runtime AccessDenied. Read-backni task definition revision a image digest, nie iba family name.

## 9. EKS control plane je zdravý, workload nie

EKS API health nepreukazuje nodes, CNI, DNS, storage, admission ani application. Rozlož AWS a Kubernetes identity:

```text
AWS account/region/cluster ARN
→ EKS control plane version/config
→ access entry/IAM authentication
→ node group/Fargate/Auto Mode capacity
→ VPC CNI/subnet/IP capacity
→ Kubernetes RBAC/admission
→ Pod scheduling/image/storage/network
→ Service/Ingress/LB
→ business request
```

```bash
aws eks describe-cluster --name CLUSTER
aws eks list-nodegroups --cluster-name CLUSTER
kubectl get nodes,pods -A -o wide
kubectl get events -A --sort-by=.lastTimestamp | tail -100
```

`kubectl` môže používať iný AWS profile alebo role než AWS CLI shell. `aws eks update-kubeconfig` mení local kubeconfig a nie je authorization fix. Over current context a caller identity.

## 10. S3 request je denied alebo object je „starý“

S3 authorization môže zahŕňať IAM, bucket policy, access point, Block Public Access, object ownership, KMS a VPC endpoint policy. Pri 403 nevie anonymný caller vždy odlíšiť missing object od denied access.

```bash
aws s3api head-bucket --bucket BUCKET
aws s3api head-object --bucket BUCKET --key KEY
aws s3api get-bucket-policy-status --bucket BUCKET
aws s3api get-public-access-block --bucket BUCKET
```

Rozlišuj object key, VersionId, ETag a checksum. ETag nie je univerzálny MD5, najmä pri multipart a encryption. CloudFront alebo application cache môže vracať starú representation, hoci S3 object version je nová.

Pri accidental delete používaj versioning/object lock evidence. Lifecycle transition/deletion je asynchronous policy outcome, nie okamžitá file operation.

## 11. EBS/EFS/storage problém

EBS volume má AZ boundary a attachment state; filesystem a mount sú ďalšie vrstvy. Snapshot completion nepreukazuje application-consistent backup.

```bash
aws ec2 describe-volumes --volume-ids vol-...
aws ec2 describe-volume-status --volume-ids vol-...
aws ec2 describe-snapshots --snapshot-ids snap-...
```

Na hoste kontroluj block device, filesystem, mount, capacity, inode a I/O errors. Pri Nitro device name sa guest path môže líšiť od requested name.

EFS pridáva mount target per AZ/subnet, SG pre NFS, DNS a access point identity. Mount success nepreukazuje POSIX UID/GID a application permission contract.

## 12. RDS je Available, connection alebo query zlyháva

RDS `available` opisuje instance/cluster control-plane state. Application path potrebuje endpoint resolution, route, SG, TLS, database auth, connection pool, schema a query health.

```bash
aws rds describe-db-instances --db-instance-identifier DB
aws rds describe-db-clusters --db-cluster-identifier CLUSTER
```

Rozlišuj writer/reader/custom endpoint a failover generation. DNS cache alebo pool môže držať starý IP/connection po failoveri. Security group povolenie z application SG je lepšie než broad CIDR, ale stále potrebuje return path.

Performance Insights/CloudWatch, database logs a engine-native views odlíšia CPU, I/O, locks, connection exhaustion a slow query. Zvýšenie instance class bez workload diagnosis môže iba oddialiť recurrence.

Backup/restore drill musí overiť data a application outcome. Snapshot existence nie je RPO/RTO dôkaz.

## 13. DynamoDB throttling alebo conditional failure

Conditional failure môže byť očakávaný business verdict, napríklad idempotency duplicate. Throttling, validation a access denied sú odlišné classes.

```bash
aws dynamodb describe-table --table-name TABLE
aws cloudwatch get-metric-data --metric-data-queries file://queries.json
```

Pri on-demand aj provisioned mode sleduj partition-key distribution, hot keys, item size, GSI capacity a retry behavior. SDK retry môže zvýšiť latency a duplicate attempts; application idempotency zostáva potrebná.

`PutItem` bez condition prepíše rovnaký key. Pri incident recovery nepoužívaj blind put, ak potrebuješ compare-and-swap alebo create-only semantics.

## 14. SQS/SNS/EventBridge: messages chýbajú alebo sa opakujú

At-least-once delivery znamená, že duplicates sú normálne failure mode. Rozlišuj publish acceptance, queue/topic/rule policy, filtering, encryption, delivery retry, visibility timeout, DLQ/redrive a consumer commit.

```bash
aws sqs get-queue-attributes --queue-url URL --attribute-names All
aws sns get-subscription-attributes --subscription-arn ARN
aws events describe-rule --name RULE
aws events list-targets-by-rule --rule RULE
```

Approximate queue metrics nie sú exact ledger. Correlate message ID, business operation ID a consumer idempotency store. Pred redrive over, že fixed consumer dokáže spracovať payload a že replay nevytvorí duplicate side effect.

## 15. CloudWatch alarm je `INSUFFICIENT_DATA` alebo nealarmuje

Alarm závisí od metric namespace/name, dimensions, statistic, period, evaluation periods, missing-data policy a metric publication latency.

```bash
aws cloudwatch describe-alarms --alarm-names ALARM
aws cloudwatch get-metric-data --metric-data-queries file://queries.json
```

Wrong dimension často vytvára platný, ale prázdny timeseries. `treatMissingData=notBreaching` môže skryť telemetry outage; `breaching` môže vytvoriť false incident. Policy závisí od metric semantics.

Dashboard graph nie je alert verdict a log presence nie je metric publication. Over notification path cez SNS/Incident Manager a receiver acknowledgment.

## 16. CloudTrail event chýba

CloudTrail Event History typicky pokrýva regional management events; data events, Insights, organization trail a event data store majú odlišnú konfiguráciu. Chýbajúci event môže znamenať wrong region/account, data-event scope, delivery delay, selector, trail status alebo skutočne nevykonanú API call.

```bash
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=EVENT
aws cloudtrail get-trail-status --name TRAIL_ARN
aws cloudtrail get-event-selectors --trail-name TRAIL_ARN
```

CloudTrail log integrity a centralized delivery sú samostatné controls. Incident responder nesmie predpokladať, že default Event History je úplný forensic source pre S3 object access alebo Lambda invocation.

## 17. KMS decrypt/encrypt zlyháva

KMS authorization kombinuje IAM a key policy/grants. Alias je mutable pointer; key ARN/ID je stabilnejšia identity.

```bash
aws kms describe-key --key-id KEY
aws kms list-aliases --key-id KEY_ID
aws kms list-grants --key-id KEY_ID
```

Rozlišuj wrong region, key state, cross-account policy, encryption context, grant token, algorithm/key usage a service integration. Ciphertext blob je region/key/context-bound podľa operácie.

Nepridávaj broad key-policy principal iba na opravu. Over exact service/principal/action/context a forbidden decrypt z iného workloadu.

## 18. Secrets Manager/Parameter Store rotation

Name/ARN môže mať versions a staging labels. `AWSCURRENT` je mutable selector. Successful secret update nepreukazuje consumer reload ani provider credential validity.

```bash
aws secretsmanager describe-secret --secret-id SECRET
aws secretsmanager list-secret-version-ids --secret-id SECRET
```

Rotation lifecycle:

```text
nový provider credential
→ secret version
→ staging label transition
→ application reload/rollout
→ loaded fingerprint
→ successful provider operation
→ old credential revocation
→ second operation
```

Pri incidente nevypisuj `SecretString`. Použi version ID, label a non-sensitive fingerprint z application version endpointu alebo audit metadata.

## 19. CloudFormation stack je stuck alebo rollbackuje

Stack event history je primárny transition log:

```bash
aws cloudformation describe-stacks --stack-name STACK
aws cloudformation describe-stack-events --stack-name STACK --max-items 100
aws cloudformation list-stack-resources --stack-name STACK
aws cloudformation detect-stack-drift --stack-name STACK
```

Najprv nájdi first failing resource event, nie posledný `ROLLBACK_COMPLETE`. Custom resource alebo nested stack môže mať external side effect a timeout.

`continue-update-rollback`, resource skip alebo import sú recovery operations s debtom. Po recovery musí template/state/live inventory znovu konvergovať a drift sa klasifikovať.

## 20. AWS Backup/restore nie je overený

Backup job `COMPLETED` dokazuje vytvorenie recovery pointu podľa service. Neoveruje decrypt permissions, restore target, application consistency, dependencies ani RTO.

```bash
aws backup list-recovery-points-by-backup-vault --backup-vault-name VAULT
aws backup list-restore-jobs
```

Pravidelne vykonaj izolovaný restore, over data checksum/schema, application startup, business query a cleanup. Cross-account/cross-region recovery potrebuje KMS a vault policy verification.

## Connected incident: health green, starý Lambda alias a duplicate payment

Deployment job update-nul `$LATEST`, publikoval version 18, ale alias `live` zostala na 17 pre stale RevisionId conflict. Synthetic volal function name bez aliasu, takže testoval `$LATEST` a bol green. Client timeoutol po DynamoDB write a retry použil novú operation ID, čím vznikla druhá authorization.

Preserve-first evidence:

```text
pipeline artifact SHA
Lambda CodeSha256 a RevisionId
published versions 17/18
live alias FunctionVersion a RevisionId
invoke ExecutedVersion
CloudWatch request IDs
DynamoDB operation/authorization items
CloudTrail UpdateAlias event/error
client idempotency keys
```

Recovery:

```text
zastaviť ďalšie alias writers
→ zachovať versions a alias state
→ identifikovať accepted artifact/version
→ overiť candidate priamou version invocation
→ CAS-update live alias
→ business probe cez alias
→ reconcile duplicate podľa business policy
→ opraviť synthetic target a idempotency key lifecycle
→ testovať stale alias conflict a unknown response
```

Root cause nebol iba „alias sa neaktualizoval“. Deployment acceptance testovala inú invocation identity a client nemal stabilnú operation identity.

## Closure gate

AWS incident je uzatvorený až keď:

```text
account/region/principal/session sú explicitné
resource ARN/ID a runtime version/digest sú korelované
IAM allow/deny chain je vysvetlený
network forward aj return path sú overené
control-plane status je spojený s data-plane/runtime evidence
logs, metrics a CloudTrail majú známu coverage hranicu
business operation má stable identity a known outcome
recovery používa authoritative configuration/release
forbidden adjacent access alebo old version nie sú aktívne
druhá operácia a ďalší reconciliation nevytvoria drift
cost-generating temporary resources sú odstránené
```

AWS troubleshooting je korelácia distribuovaných control planes. Console status, CLI response, CloudWatch, CloudTrail a application ledger sú samostatné evidence sources; incident sa uzatvára až ich konzistentným spojením.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Praktický AWS projekt od lokálneho artifactu po overenú Lambda release](aws-practical-walkthrough.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Monitoring vs. observability →](../12-observability/monitoring-vs-observability.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
