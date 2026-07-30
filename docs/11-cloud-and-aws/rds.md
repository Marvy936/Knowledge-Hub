# Amazon RDS

Amazon Relational Database Service presúva host, storage platform, service orchestration, backups a failover mechanisms na AWS podľa zvoleného engine a deployment modelu. Neodstraňuje database engineering. Zákazník stále vlastní schema, transactions, queries, indexes, users, privileges, connection pools, retries, idempotency, data classification, compatibility a business recovery.

```text
business transaction
→ endpoint DNS and network path
→ TLS, authentication and database authorization
→ session and transaction
→ reads, locks, writes and log records
→ commit or rollback
→ application acknowledgement
→ failover, scale or upgrade transition
→ backup/PITR and reconciliation
→ business outcome
```

Najnebezpečnejší failure nie je vždy `connection failed`, ale unknown commit outcome. Writer môže transaction durable commitnúť a connection sa preruší pred client acknowledgementom. Blind retry potom vytvorí duplicate side effect.

## 1. Exact database subject

Atlas Payments používa RDS subject `DB-PAY-42` v `eu-central-1`. Engine je PostgreSQL-compatible generation `PG-16-GEN-7`. Deployment model je Multi-AZ DB cluster `db-pay-prod-17` s writerom v AZ-a a readable instances v AZ-b/c.

Writer endpoint je `db-pay-prod.cluster-xyz.eu-central-1.rds.amazonaws.com`, reader endpoint `db-pay-prod.cluster-ro-xyz.eu-central-1.rds.amazonaws.com`. Subnet group generation je `DBSUB-12`, Security Group `SG-DB-14`, parameter group `PGPAR-21`, RDS CA `RDS-CA-8`, KMS `KMS-DB-11`, secret `SEC-DB-34` a schema `SCHEMA-215`.

Application release `7.15.0` používa RDS Proxy `PROXY-9`. Transaction je payment `P-884` a idempotency key `pay-P884`. Forbidden outcomes sú stale reader pre consistency-sensitive read, duplicate payment po lost acknowledgement, failover prijatý iba podľa console statusu a blue/green cutover s dvoma writable authorities.

## 2. Connection path má viac nezávislých gates

```text
endpoint DNS
→ route, DB subnet and Security Group
→ TLS handshake and hostname validation
→ database authentication
→ role and object privileges
→ connection/session budget
→ query/transaction
→ response
```

Timeout môže byť DNS, network, failover, pool saturation alebo listener. TLS error znamená, že transport sa dostal ďalej, ale trust/protocol zlyhal. Password failure potvrdzuje funkčnejší network/listener path. SQL `permission denied` je database authorization, nie Security Group.

Praktický preflight z application contextu:

```bash
getent ahostsv4 db-pay-prod.cluster-xyz.eu-central-1.rds.amazonaws.com
nc -vz -w 3 db-pay-prod.cluster-xyz.eu-central-1.rds.amazonaws.com 5432
openssl s_client \
  -connect db-pay-prod.cluster-xyz.eu-central-1.rds.amazonaws.com:5432 \
  -starttls postgres \
  -servername db-pay-prod.cluster-xyz.eu-central-1.rds.amazonaws.com \
  -verify_return_error </dev/null
```

TCP/TLS success nepreukazuje database login alebo query. Ďalší test musí použiť actual application identity.

## 3. RDS deployment model v Terraform-e

```hcl
resource "aws_rds_cluster" "payments" {
  cluster_identifier = "db-pay-prod-17"
  engine             = "postgres"
  engine_version     = "16.4"
  database_name      = "payments"
  master_username    = "bootstrap_admin"

  manage_master_user_password = true

  db_subnet_group_name   = aws_db_subnet_group.payments.name
  vpc_security_group_ids = [aws_security_group.database.id]
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.payments.name

  storage_encrypted = true
  kms_key_id        = aws_kms_key.database.arn

  backup_retention_period = 14
  preferred_backup_window = "01:00-02:00"

  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "db-pay-prod-17-final"

  tags = {
    Generation = "DB-PAY-42"
  }
}

resource "aws_rds_cluster_instance" "payments" {
  count = 3

  identifier         = "db-pay-prod-${count.index + 1}"
  cluster_identifier = aws_rds_cluster.payments.id
  instance_class     = "db.r7g.large"
  engine             = aws_rds_cluster.payments.engine
  engine_version     = aws_rds_cluster.payments.engine_version

  publicly_accessible = false
}
```

Presná resource shape závisí od engine a current RDS deployment supportu. Terraform apply môže vytvoriť cluster a instances, no nepreukazuje schema, roles, application connectivity ani failover behavior.

## 4. Live RDS topology read-back

```bash
aws rds describe-db-clusters \
  --db-cluster-identifier db-pay-prod-17 \
  --region eu-central-1 \
  --query 'DBClusters[0].{Status:Status,Engine:Engine,Version:EngineVersion,Endpoint:Endpoint,ReaderEndpoint:ReaderEndpoint,Members:DBClusterMembers,BackupRetention:BackupRetentionPeriod,LatestRestorable:LatestRestorableTime,Kms:KmsKeyId}'
```

Instance details:

```bash
aws rds describe-db-instances \
  --region eu-central-1 \
  --query 'DBInstances[?DBClusterIdentifier==`db-pay-prod-17`].{Id:DBInstanceIdentifier,Status:DBInstanceStatus,Class:DBInstanceClass,Az:AvailabilityZone,Endpoint:Endpoint.Address,ParameterGroups:DBParameterGroups}'
```

`available` je service state. NePreukazuje, že application pool používa current writer alebo schema generation.

## 5. Database identity and schema test

```bash
psql "$PAYMENTS_DATABASE_URL" -v ON_ERROR_STOP=1 <<'SQL'
select current_database(), current_user, inet_server_addr(), inet_server_port();
select pg_is_in_recovery() as is_replica;
select version
from schema_generation
where component = 'payments';
SQL
```

`pg_is_in_recovery=false` pomáha overiť PostgreSQL writer session. Engine-specific query sa musí prispôsobiť databáze. Schema generation sa má čítať z application-owned table alebo migration ledgeru.

Application user nemá byť master/bootstrap administrator. Privilege review:

```sql
select grantee, table_schema, table_name, privilege_type
from information_schema.role_table_grants
where grantee = 'payments_runtime'
order by table_schema, table_name, privilege_type;
```

## 6. Multi-AZ DB instance a Multi-AZ DB cluster

Klasický Multi-AZ DB instance model používa primary a synchronously maintained standby v inej AZ. Standby je failover resource a typicky neobsluhuje application reads.

Multi-AZ DB cluster pri podporovaných engines/configurations používa writer a dve readable DB instances v troch AZs. Readable instances môžu obsluhovať reads a byť promotion candidates.

Oba modely riešia zonal/instance availability, nie logical corruption alebo Region disaster. Read replicas a cross-Region strategies majú asynchronous semantics a vlastné RPO.

## 7. Writer a reader endpoint semantics

Writer endpoint smeruje na current writer. Reader endpoint distribuuje connections medzi readable instances podľa service semantics. Nezaručuje read-after-write freshness pre business transaction.

```text
payment write committed on writer
→ replication/apply to readers
→ reader endpoint chooses readable instance
→ state may be older than just-committed transaction
```

Consistency-sensitive payment status po write má čítať writer alebo používať explicitný session/consistency contract. Reporting môže tolerovať lag, ak je budget meraný.

## 8. Transaction a stable idempotency key

```sql
begin;

insert into payment_operation (
  idempotency_key,
  payment_id,
  state
) values (
  'pay-P884',
  'P-884',
  'accepted'
)
on conflict (idempotency_key) do nothing;

insert into payment_outbox (
  idempotency_key,
  event_type,
  payload
) values (
  'pay-P884',
  'PaymentAccepted',
  '{"paymentId":"P-884"}'::jsonb
)
on conflict (idempotency_key, event_type) do nothing;

commit;
```

Unique constraints a transactional outbox vytvárajú internal atomic boundary. External provider request potrebuje rovnaký stable idempotency key a reconciliation. Lambda/HTTP request ID nie je stabilný business key pre nový attempt.

Ak client timeoutne po `COMMIT` send-e, najprv query-ne operation state:

```sql
select payment_id, state, updated_at
from payment_operation
where idempotency_key = 'pay-P884';
```

Blind replay nie je bezpečný.

## 9. Connection pool a total fleet budget

Ak 12 application instances používa pool maximum 100, database môže vidieť 1 200 connections. Po scale-out-e na 24 je maximum 2 400. CPU môže byť nízke a database môže zlyhávať na connection memory, lock contention alebo authentication churn.

Pool contract zahŕňa maximum per instance, acquisition timeout, idle lifetime, validation, failover eviction a fleet-wide budget.

Current connections:

```sql
select application_name, state, count(*)
from pg_stat_activity
group by application_name, state
order by count(*) desc;
```

Long transactions:

```sql
select pid, usename, application_name, state,
       now() - xact_start as transaction_age,
       wait_event_type, wait_event, query
from pg_stat_activity
where xact_start is not null
order by xact_start;
```

## 10. RDS Proxy

RDS Proxy pools backend connections, can reduce connection churn and automatically tracks current writer for supported RDS/Aurora targets. It can reduce client impact of failover because applications connect to proxy endpoint rather than resolving database endpoint directly.

Terraform:

```hcl
resource "aws_db_proxy" "payments" {
  name                   = "payments-proxy-9"
  engine_family          = "POSTGRESQL"
  idle_client_timeout    = 1800
  require_tls            = true
  role_arn               = aws_iam_role.rds_proxy.arn
  vpc_security_group_ids = [aws_security_group.proxy.id]
  vpc_subnet_ids         = values(aws_subnet.application)[*].id

  auth {
    auth_scheme = "SECRETS"
    secret_arn  = aws_secretsmanager_secret.database_runtime.arn
    iam_auth    = "DISABLED"
  }
}

resource "aws_db_proxy_default_target_group" "payments" {
  db_proxy_name = aws_db_proxy.payments.name

  connection_pool_config {
    max_connections_percent      = 80
    max_idle_connections_percent = 40
    connection_borrow_timeout    = 30
  }
}
```

Session features môžu pin-nuť client k backend connection a znížiť multiplexing. Proxy neopraví slow query ani unlimited transaction concurrency.

Read-back:

```bash
aws rds describe-db-proxies --db-proxy-name payments-proxy-9 --region eu-central-1
aws rds describe-db-proxy-targets --db-proxy-name payments-proxy-9 --region eu-central-1
```

Pri Blue/Green switchover-e proxy target read-back môže reflectovať updated targets až po completion, hoci traffic routing sa zmení skôr; application a service events zostávajú potrebné.

## 11. Forced failover experiment

Multi-AZ DB cluster failover možno pri supported deployment-e spustiť:

```bash
aws rds failover-db-cluster \
  --db-cluster-identifier db-pay-prod-17 \
  --region eu-central-1
```

Experiment sa nevykonáva bez controlled traffic, idempotency a stop conditions. Sleduj old/new writer, DNS/proxy, connection pool, in-flight transactions a business outcomes.

```bash
aws rds describe-events \
  --source-type db-cluster \
  --source-identifier db-pay-prod-17 \
  --duration 60 \
  --region eu-central-1
```

Fresh SQL connection po failover-e musí ukázať writer. Existing sockets môžu byť broken a pool ich musí evictnúť.

## 12. Automated backups, snapshots a PITR

Automated backups a transaction logs vytvárajú restorable window podľa engine/service modelu. PITR vytvorí nový resource; nevracia existing DB in-place.

```bash
aws rds restore-db-cluster-to-point-in-time \
  --source-db-cluster-identifier db-pay-prod-17 \
  --db-cluster-identifier db-pay-restore-inc884 \
  --restore-to-time 2026-07-28T10:14:00Z \
  --db-subnet-group-name atlas-recovery-db \
  --vpc-security-group-ids sg-0recoverydb \
  --kms-key-id arn:aws:kms:eu-central-1:200000000042:key/key-recovery-11 \
  --region eu-central-1
```

Exact CLI shape sa líši podľa deployment/engine. Restore job vytvorí database resource. Potom treba instances, parameters, extensions, network, credentials, schema/data validation a application canary.

RPO sa meria last usable business checkpointom, nie iba `LatestRestorableTime`.

## 13. Parameter groups

Parameter group je engine configuration generation. Dynamic parameter môže byť effective bez rebootu, static parameter môže mať `pending-reboot` status.

```bash
aws rds describe-db-parameters \
  --db-parameter-group-name payments-pg16-21 \
  --region eu-central-1 \
  --query 'Parameters[?Source==`user`].{Name:ParameterName,Value:ParameterValue,ApplyType:ApplyType,ApplyMethod:ApplyMethod}'
```

Association s groupou nepreukazuje runtime effective value. Query engine setting a pending-modification state.

## 14. Blue/Green Deployment

RDS Blue/Green pri supported engines/configurations vytvorí synchronized green topology pre upgrade/config change a controlled switchover.

```text
blue production
→ green creation and synchronization
→ engine/schema/application validation
→ switchover preconditions
→ bounded cutover
→ application reconnect
→ green business acceptance
```

Blue/Green znižuje switchover downtime, no nie je univerzálny rollback. Po green writes blue nie je automaticky current authoritative copy. Reverse switch môže vyžadovať reconciliation alebo forward recovery.

Inventory:

```bash
aws rds describe-blue-green-deployments \
  --filters Name=blue-green-deployment-name,Values=payments-pg17 \
  --region eu-central-1
```

Switchover:

```bash
aws rds switchover-blue-green-deployment \
  --blue-green-deployment-identifier bgd-0payments \
  --switchover-timeout 900 \
  --region eu-central-1
```

Pred switchoverom over replication lag, long transactions, unsupported changes, proxy integration, application driver a schema compatibility.

## 15. Worked incident: failover úspešný, payment outcome neznámy

RDS Multi-AZ DB cluster po impairment-e promovoval reader v AZ-b. Console ukázala `available`; API mala 90-sekundový spike connection resetov. Reconciliation našla dve provider autorizácie pre `P-884`.

Database audit ukázal, že old writer durable commitol ledger/outbox, ale connection sa resetla pred acknowledgementom. API klasifikovala timeout ako rollback a retry-la celý workflow s novým provider request ID. Internal unique constraint chránila ledger insert, no external provider call nemal stable idempotency key.

RDS failover a writer promotion fungovali. Correctness failure bol application unknown-outcome contract.

Containment pozastavil automatic retries pre affected cohort, zachoval DB logs, RDS events, pool/proxy metrics a provider IDs a obmedzil reconnect storm. Recovery reconciliovala DB/outbox/provider, kompenzovala duplicate authorization a zaviedla end-to-end `pay-P884` key.

Closure vyžadovala fresh connections na new writer, bounded pool recovery, jeden business outcome pri lost acknowledgement, writer/reader separation a controlled second failover.

## 16. Storage, locks a query diagnosis

RDS instance scale-up môže maskovať missing index alebo lock wait. Pred mutation zachovaj query fingerprint, plan, wait events, lock graph, transaction duration, storage latency and release timeline.

PostgreSQL lock sample:

```sql
select blocked.pid as blocked_pid,
       blocking.pid as blocking_pid,
       blocked.query as blocked_query,
       blocking.query as blocking_query
from pg_stat_activity blocked
join pg_locks blocked_locks on blocked.pid = blocked_locks.pid and not blocked_locks.granted
join pg_locks blocking_locks
  on blocking_locks.locktype = blocked_locks.locktype
 and blocking_locks.database is not distinct from blocked_locks.database
 and blocking_locks.relation is not distinct from blocked_locks.relation
 and blocking_locks.granted
join pg_stat_activity blocking on blocking.pid = blocking_locks.pid;
```

Scale-up nie je prvý diagnosis krok.

## 17. Monitoring and evidence

Control-plane evidence zahŕňa RDS events, CloudTrail and pending modifications. Connection evidence zahŕňa pool/proxy metrics and auth logs. Engine evidence zahŕňa query plans, waits, locks and logs. Storage/replication evidence zahŕňa IOPS, latency, free space and replica lag. Business evidence zahŕňa idempotency ledger and provider outcome.

Žiadna jedna metric neuzatvára transaction incident.

## Kontrolné otázky

1. Prečo `available` nie je database business verdict?
2. Aký rozdiel je medzi writer a reader endpointom?
3. Čo vytvára unknown commit outcome?
4. Ako stable idempotency key chráni DB aj provider?
5. Prečo pool maximum musí byť fleet-wide budget?
6. Kedy RDS Proxy pomáha a kedy nepomôže?
7. Čo musí failover experiment sledovať okrem RDS eventu?
8. Prečo PITR vytvára nový resource?
9. Prečo Blue/Green nie je jednoduchý rollback po writes?
10. Aký dôkaz uzavrie duplicate-payment incident?

## Oficiálna dokumentácia

- [Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html)
- [Multi-AZ deployments](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html)
- [Multi-AZ DB clusters](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/multi-az-db-clusters-concepts.html)
- [RDS Proxy](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html)
- [Backups and PITR](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_CommonTasks.BackupRestore.html)
- [Blue/Green Deployments](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/blue-green-deployments.html)
- [RDS monitoring](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Monitoring.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: S3, EBS a EFS](s3-ebs-efs.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Route 53 a CloudFront →](route53-cloudfront.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
