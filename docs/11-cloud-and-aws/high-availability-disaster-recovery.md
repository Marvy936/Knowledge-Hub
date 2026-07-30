# High availability a disaster recovery

High availability a disaster recovery riešia odlišné failure scopes. High availability udržiava alebo rýchlo obnovuje business outcome pri očakávateľnom component alebo Availability Zone failure. Disaster recovery obnovuje capability po strate primárneho Regionu, dát, accountu alebo dôveryhodného identity plane-u podľa explicitných RTO a RPO.

HA typicky pracuje s current production state-om. DR môže zámerne použiť starší čistý recovery point a nové prostredie. Replication preto nie je backup: môže rýchlo preniesť logical delete, ransomware-encrypted data alebo chybnú schema. Backup zase nie je failover: restore môže vyžadovať nový resource, network, credentials, application startup a reconciliation.

```text
business capability a impact analysis
→ failure a disaster scenarios
→ RTO/RPO a minimum-capacity contract
→ HA a DR architecture
→ protected recovery set
→ detection a declaration
→ failover alebo restore
→ single-writer authority
→ business validation
→ failback a improvement
```

## 1. Recovery subject pre Atlas Payments

Atlas používa recovery subject `REC-PAY-42`. Primárny Region je `eu-central-1`, recovery Region `eu-west-1` a release generation `PAY-4.2.0`. Authoritative state sa skladá z ledger checkpointu `L842` a event offsetu `E91`. Recovery artifact set `R57` obsahuje image digest, Helm chart, IaC, PKI a secret generations. Backup generation je `B2026-07-28T0030Z` a replication checkpoint `RC-842991`.

Business RTO je 45 minút a RPO päť minút. Recovery prostredie musí vedieť obslúžiť najmenej 40 % peak trafficu, pričom settlement queue zachová zvyšnú prácu. Recovery ownerom je Payments Incident Commander. Duplicate authorization, strata potvrdeného settlementu a reuse kompromitovaného credentialu sú forbidden outcomes.

RTO a RPO bez exact state identity nemajú praktický význam. Päťminútové RPO musí odpovedať, ktorých dát a ktorého business checkpointu sa týka.

## 2. Availability je meraná na user outcome

Instance, Pod alebo load balancer môže byť healthy a payment journey môže zlyhávať. Availability musí definovať oprávneného clienta, operation, latency boundary a business result.

Pre Atlas:

```text
valid payment authorization request
→ authenticated and accepted
→ provider authorization
→ ledger and outbox commit
→ response within 800 ms p99
→ exactly one durable outcome
```

Availability numerator nie je počet HTTP 200 odpovedí. Response môže byť rýchla a duplicitne autorizovať platbu. SLI musí zahŕňať correctness invariant.

Praktická synthetic kontrola môže vytvoriť non-charge test transaction s deterministic idempotency key a overiť API, ledger aj outbox. Zelený ALB health check ostáva iba infraštruktúrny a readiness dôkaz.

## 3. High availability lifecycle

HA začína redundantnou serving capacity v nezávislých failure domains. Po failure musí monitoring odlíšiť unhealthy cohort, traffic alebo writer authority sa musí odobrať, remaining capacity musí absorbovať load a client musí bezpečne reconnectovať alebo retryovať.

```text
healthy multi-AZ capacity
→ failure detection
→ failed target alebo writer withdrawal
→ surviving capacity and authority check
→ reconnect/retry with idempotency
→ business outcome validation
→ failed component replacement
→ redundancy restoration
```

Multi-AZ design musí mať odpoveď pre compute, egress, database, caches, queues, secrets, DNS a observability. Tri application subnets nepomôžu, ak všetky používajú jednu zonálnu NAT Gateway.

HA tiež potrebuje statically stable minimum. Počas control-plane incidentu nemusí byť možné okamžite launchovať replacement. Existujúca capacity v surviving AZs musí obslúžiť kritickú časť trafficu bez predpokladu, že Auto Scaling vždy zafunguje v prvých minútach.

## 4. BIA ako versionovaný business input

Business Impact Analysis má byť konkrétny artefakt, nie veta „payments sú kritické“.

```yaml
capability: CAP-PAY-42
owner: payments-business-owner
criticalOperations:
  authorize:
    maximumTolerableDowntimeMinutes: 30
    rtoMinutes: 15
    rpoMinutes: 0
  settle:
    maximumTolerableDowntimeMinutes: 120
    rtoMinutes: 45
    rpoMinutes: 5
minimumRecoveryCapacity:
  percentOfPeak: 40
  backlogAllowed: true
manualWorkaround:
  available: false
dependencies:
  - payment-provider
  - ledger-database
  - settlement-queue
  - kms-and-secrets
  - dns-and-certificates
forbiddenOutcomes:
  - duplicate-authorization
  - lost-confirmed-settlement
  - use-of-revoked-credential
```

Tento dokument ukazuje, že authorize a settle môžu mať odlišné recovery objectives. Zero RPO pre potvrdenú autorizáciu nevznikne automaticky cross-Region backupom; application musí definovať, kedy môže klientovi potvrdiť výsledok.

## 5. RTO, RPO, RTA a RPA

RTO meria celý recovery interval, nie iba čas restore jobu:

```text
detection
+ escalation and disaster declaration
+ recovery access
+ provisioning or promotion
+ data restore/replay
+ application startup
+ validation
+ traffic cutover
= Recovery Time Actual
```

RPO určuje maximálny akceptovaný rozdiel medzi authoritative production state-om pred disaster eventom a obnoveným state-om. Recovery Point Actual sa meria po restore a reconciliation. Latest backup timestamp nie je automaticky RPA, pretože recovery point môže byť nečitateľný, nekonzistentný alebo poškodený.

AWS Well-Architected používa RTO a RPO ako workload restoration objectives; pravidelný DR test má preukázať, či implementácia tieto ciele reálne spĺňa. citeturn398658search3turn398658search11turn398658search16

## 6. Recovery-set manifest

Databázový snapshot nie je celý systém. Recovery set viaže data, artifacts, identity, network a external integration state do jednej generácie.

```yaml
recoverySet: R57
capability: CAP-PAY-42
cleanBoundary: "2026-07-28T00:30:00Z"
data:
  database:
    recoveryPoint: arn:aws:rds:eu-west-1:200000000042:snapshot:payments-20260728-0030
    ledgerCheckpoint: L842
  queue:
    replayManifest: s3://atlas-recovery/manifests/E91.json
    offset: E91
  receipts:
    manifestVersion: RM81
artifacts:
  imageDigest: sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
  helmChartDigest: sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
  infrastructureCommit: 4f57c9a
identity:
  recoveryRole: arn:aws:iam::200000000042:role/AtlasRecoveryOperator
  kmsKeyArn: arn:aws:kms:eu-west-1:200000000042:key/11111111-2222-3333-4444-555555555555
  secretGeneration: SEC-REC-11
network:
  vpcGeneration: VPC-REC-11
  dnsGeneration: DNS-REC-7
external:
  providerEgressIdentity: EIP-REC-3
validation:
  syntheticPaymentId: DR-CANARY-884
  forbiddenCredentialGeneration: SE10
```

Manifest znemožňuje náhodne skombinovať najnovší database snapshot s neskorším queue offsetom. Každá položka má ownera, version, location a restore dependency.

## 7. DR stratégie a ich skutočný prepared state

Backup and restore udržiava protected data a deployable IaC, no väčšinu runtime vytvorí až po incidente. Má najnižší steady-state cost a najvyššie RTO.

Pilot light udržiava kritický state alebo identity layer, zatiaľ čo application capacity sa doplní pri disaster declaration. Je rýchlejší než čistý restore, ale recovery scale-out môže zlyhať na quota, subnet alebo artifact drift.

Warm standby beží ako zmenšená funkčná kópia. Dá sa priebežne testovať, no potrebuje overený scale-up a single-writer contract.

Multi-site active-active obsluhuje traffic vo viacerých Regions. Znižuje RTO, ale vytvára najťažší data consistency, routing, conflict a failback model. Nesmie sa vybrať iba preto, že pôsobí „najodolnejšie“.

## 8. Praktický recovery preflight

Pred incidentom sa pravidelne overuje, či recovery account a Region skutočne obsahujú dependencies.

```bash
aws sts get-caller-identity --profile atlas-recovery

aws ec2 describe-subnets \
  --profile atlas-recovery \
  --region eu-west-1 \
  --filters Name=tag:RecoveryGeneration,Values=VPC-REC-11 \
  --query 'Subnets[].{Id:SubnetId,Az:AvailabilityZoneId,FreeIps:AvailableIpAddressCount}'

aws rds describe-db-snapshots \
  --profile atlas-recovery \
  --region eu-west-1 \
  --snapshot-type manual \
  --query 'DBSnapshots[?contains(DBSnapshotIdentifier, `payments`)].{Id:DBSnapshotIdentifier,Time:SnapshotCreateTime,Status:Status,Kms:KmsKeyId}'

aws kms describe-key \
  --profile atlas-recovery \
  --region eu-west-1 \
  --key-id arn:aws:kms:eu-west-1:200000000042:key/11111111-2222-3333-4444-555555555555
```

Tieto príkazy preukazujú recovery identity, subnet inventory, snapshot inventory a KMS key state. Nevykonávajú restore, neoverujú application compatibility a nepreukazujú provider allowlist. Sú preflightom, nie DR testom.

## 9. Isolated restore experiment

Restore sa vykonáva v recovery account-e a izolovanej VPC, aby test consumer neposlal reálne payment alebo email side effects.

Ukážkový RDS restore command:

```bash
aws rds restore-db-instance-from-db-snapshot \
  --profile atlas-recovery \
  --region eu-west-1 \
  --db-instance-identifier payments-dr-test-20260730 \
  --db-snapshot-identifier payments-20260728-0030 \
  --db-instance-class db.r7g.large \
  --db-subnet-group-name atlas-recovery-db \
  --vpc-security-group-ids sg-0recoverydb \
  --no-publicly-accessible
```

API acceptance iba vytvorí restore workflow. Potom sa čaká na resource state:

```bash
aws rds wait db-instance-available \
  --profile atlas-recovery \
  --region eu-west-1 \
  --db-instance-identifier payments-dr-test-20260730
```

`available` stále nie je business verdict. Nasleduje schema a data validation s recovery application role:

```bash
psql "$RECOVERY_DATABASE_URL" -v ON_ERROR_STOP=1 <<'SQL'
select current_database(), current_user;
select version from schema_generation where component = 'payments';
select max(checkpoint_id) from ledger_checkpoint;
select count(*) from settlement where payment_id = 'P-884';
SQL
```

Potom sa deployne presný image digest a spustí synthetic payment, ktorý používa test provider endpoint alebo hard safety gate. Recovery test nesmie mať production charge capability.

## 10. Disaster declaration a authority transfer

Failover nie je technická improvizácia každého tímu. Incident Commander deklaruje disaster, zvolí recovery set a prenesie authority.

```text
incident classification
→ disaster declared
→ production mutations fenced
→ recovery set selected
→ recovery identity activated
→ environment restored or scaled
→ single-writer verified
→ business canary
→ traffic opened by cohorts
```

Fencing starej production authority je zásadné. Ak primary writer alebo deployment credentials zostanú použiteľné, recovery environment môže vytvoriť split brain.

Praktická fencing evidence môže obsahovať disabled old KMS grant, revoked provider credential, database writer endpoint isolation a SCP/role session revocation podľa incidentu. Samotné presmerovanie DNS nie je fencing.

## 11. Worked incident: technický restore je zelený, recovery nie je dôveryhodná

Security incident kompromitoval primary account a deployment credentials. Incident Commander deklaroval DR do `eu-west-1`. Database restore a application startup skončili za 28 minút, ale production traffic nebolo možné bezpečne otvoriť ani po 90 minútach.

Hypotézy zahŕňali poškodený backup, KMS deny, chýbajúcu capacity, DNS/certificate failure, kompromitované secret replicas, nekompatibilný ledger a queue checkpoint, provider allowlist a stále aktívneho primary writera.

Database snapshot bol čitateľný a schema kompatibilná. Recovery Secrets Manager replica však obsahovala credentials vydané pred compromise a provider ich správne zablokoval. Ledger checkpoint `L842` bol navyše spárovaný s queue offsetom neskorším než clean boundary. Restore job bol technicky úspešný, no recovery set nebol konzistentný ani trust-clean.

Containment ponechalo traffic zatvorený, hard-fence-nulo primary writers, revoke-nulo kompromitované credentials a izolovalo recovery account od source automation. Tím zachoval backup, KMS, IAM a CloudTrail evidence.

Recovery vybrala canonical manifest, obnovila konzistentný ledger a queue point, vydala nové credentials a certificates z čistého trust rootu a reconciliovala provider operations. Minimum capacity sa otvorila až po synthetic payment bez real charge side effectu.

RTA bolo vyššie než cieľ a tento rozdiel sa zaznamenal ako risk, nie skryl úspešným database restore time-om.

## 12. Traffic cutover

DNS alebo routing change musí byť versionovaný a bounded. Pri Route 53 failover alebo weighted migration treba poznať TTL, client cache a existing connections.

Pred otvorením production trafficu sa overí:

```text
recovery endpoint and certificate
→ current writer authority
→ data checkpoint and reconciliation
→ minimum capacity
→ observability and incident access
→ external provider acceptance
→ canary cohort
→ gradual traffic increase
```

Route 53 record update preukazuje control-plane mutation. Neznamená, že všetky resolvers a clients už používajú recovery endpoint. Business telemetry musí ukázať actual arrival.

## 13. Failback

Failback nie je DNS prepnutie späť. Recovery environment medzitým vytvorilo nové authoritative data. Pôvodný Region sa musí rebuildnúť alebo synchronizovať z current authority.

```text
recovery environment stabilized
→ authoritative data and credential generation fixed
→ primary Region rebuilt from trusted source
→ delta replicated or exported
→ compatibility and capacity validated
→ controlled traffic shift
→ single-writer reverified
→ temporary recovery paths retired
```

Ak sa failback spustí proti starej primary databáze bez reconciliation, môže znovu zaviesť lost alebo divergent state.

## 14. DR game day

Tabletop preverí rozhodovanie a kontakty, ale nepreukazuje restore. Restore bez business testu nepreukazuje capability. Plný game day meria detection, declaration, access, provisioning, data restore, identity recovery, external integration, traffic cutover, failback a cleanup.

Test musí obsahovať forbidden paths: old credential nesmie fungovať, primary writer musí byť fenced a duplicate payment nesmie vzniknúť pri replayi. Po teste sa recovery resources bezpečne odstránia a evidence uchová.

AWS Reliability guidance explicitne odporúča pravidelne obnovovať dáta a testovať DR implementáciu, pretože iba experiment overí recovery integrity a proces. citeturn398658search8turn398658search16

## Kontrolné otázky

1. Aký failure scope rieši HA a aký DR?
2. Čo presne meria RTO a prečo restore job time nestačí?
3. Ktorý authoritative state tvorí RPO pre settlement?
4. Prečo replication nie je clean backup?
5. Čo musí obsahovať recovery-set manifest?
6. Ktoré CLI observations sú iba preflight a ktoré už testujú restored application?
7. Ako sa preukáže single-writer authority?
8. Prečo DNS cutover nie je fencing?
9. Aký trust state treba obnoviť po compromise?
10. Ako sa vykoná failback bez návratu stale state-u?

## Oficiálna dokumentácia

- [Disaster recovery objectives](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/disaster-recovery-dr-objectives.html)
- [Plan for disaster recovery](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/plan-for-disaster-recovery-dr.html)
- [Disaster Recovery of Workloads on AWS](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/introduction.html)
- [Reliability Pillar](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/reliability.html)
- [Restore a DB instance from a DB snapshot](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_RestoreFromSnapshot.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Scalability, elasticity a fault tolerance](scalability-elasticity-fault-tolerance.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: AWS Organizations a accounts →](aws-organizations-accounts.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
