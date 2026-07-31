# Shared responsibility model

AWS Shared Responsibility Model sa často redukuje na dve vety: AWS chráni cloud a zákazník chráni to, čo v cloude vytvorí. Táto formulácia je správna, ale na prevádzku nestačí. Pri konkrétnom resource-e musí byť známe, kto konfiguruje control, kto pozoruje jeho effective state, kto drží evidence, kto reaguje na failure a kto dokáže recovery.

Responsibility preto nie je statický obrázok. Je to service-specific control lifecycle:

```text
business alebo security objective
→ exact service a resource generation
→ provider capability
→ customer configuration
→ effective runtime state
→ evidence a alerting
→ incident owner a support boundary
→ remediation a recovery
→ positive a forbidden verification
```

Ak niektorý krok nemá ownera, vzniká responsibility gap. Provider aj zákazník môžu splniť svoje čiastkové povinnosti a business capability napriek tomu zlyhá.

## 1. Exact responsibility subject

Pre `CAP-PAY-42` používame managed runtime `MR42`, managed database `DB42`, workload role `WR42`, KMS key `K42`, VPC `VPC42`, Security Group generation `SG42`, endpoint generation `EP42` a backup policy `BP7`. Application release tvorí image `I42`, configuration `C42` a credential epoch `SE10`.

Tvrdenie „AWS spravuje databázu“ je bez týchto identít nepresné. AWS môže vlastniť host replacement a engine platformu, zatiaľ čo Atlas vlastní users, schema, queries, KMS policy, network path, retention a restore test.

Responsibility matrix preto viažeme na exact subject, nie iba na service name.

## 2. Security **of** the cloud

AWS vlastní fyzické facilities, hardware, foundational network, host operating systems, virtualization layer a provider service control planes podľa konkrétneho service contractu. Zákazník nevstupuje do dátového centra a nepatchuje hypervisor. Tieto controls overuje cez service documentation, compliance reports, AWS Health, support a publikované service commitments.

Provider responsibility však nekončí customer incident. Ak fyzická alebo service vrstva zlyhá, AWS opravuje provider mechanismus. Atlas stále musí zistiť, ako tento failure ovplyvnil konkrétne payment operations a akú reconciliation potrebuje. AWS nevie rozhodnúť, či dve provider autorizácie predstavujú duplicate business settlement.

## 3. Security **in** the cloud

Atlas vlastní Organizations a account governance, identities, authorization, data classification, resource configuration, VPC topology, encryption choices, application code, dependency supply chain, logging coverage, backup policy, recovery design a business acceptance.

Jednoduché pravidlo je: ak Atlas môže field alebo policy meniť, musí mať ownera, review a effective-state test. AWS API môže prijať chybnú konfiguráciu presne podľa požiadavky. Infrastructure as Code nemení túto responsibility; iba zrýchľuje a opakuje mutation.

## 4. Shared control znamená spoločný mechanizmus, nie spoločnú nejasnosť

AWS poskytne IAM a STS. Atlas definuje principals, trust, permissions, session duration a revocation. AWS poskytne KMS. Atlas vyberie key, policy, grants, encryption context a deletion lifecycle. AWS poskytne Multi-AZ database capability. Atlas ju musí zapnúť, navrhnúť application reconnect a otestovať failover. AWS emituje CloudTrail events. Atlas musí zapnúť správne coverage, uchovať logy, korelovať alert a reagovať.

Každý shared control má dve časti:

```text
provider mechanism exists and operates
+
customer configuration is correct and effective
→ usable control
```

Ak CloudTrail služba funguje, ale Atlas trail nezahŕňa potrebné data events alebo bucket retention, audit control nefunguje pre daný incident.

## 5. Praktický control manifest

Kontroly sa dajú zapisovať ako versionovaný manifest. Nasledujúci príklad nie je AWS resource; je to interný operational contract.

```yaml
controlId: ENC-PAY-42
objective: Only the payments workload may decrypt settlement credentials
resource:
  kmsKeyArn: arn:aws:kms:eu-central-1:100000000042:key/11111111-2222-3333-4444-555555555555
  secretArn: arn:aws:secretsmanager:eu-central-1:100000000042:secret:prod/payments/provider
providerResponsibilities:
  - operate KMS control plane and protected key material
  - enforce accepted key-policy and grant semantics
customerResponsibilities:
  - maintain workload role and key policy
  - bind decrypt to the required encryption context
  - monitor denied and unexpected decrypt attempts
  - test allowed and forbidden callers
  - protect recovery keys and key-deletion workflow
evidence:
  configuration: git://security/kms/payments-key-policy.json
  runtime: CloudTrail cryptographic events and application request IDs
  retentionDays: 365
recovery:
  owner: payments-security-oncall
  forbiddenOutcome: non-payments role decrypts the credential
```

Manifest oddeľuje provider mechanismus od Atlas configuration a validation. Pri review sa dá položiť konkrétna otázka: existuje forbidden test pre inú workload role?

## 6. EC2 responsibility rozdelená po vrstvách

Pri EC2 AWS vlastní facilities, hardware, hypervisor, physical network a EC2 control plane. Atlas vlastní AMI provenance, guest OS, packages, agents, runtime, application, instance role, Security Groups, EBS encryption choice, patching, fleet availability a recovery.

Praktické rozlíšenie:

```bash
aws ec2 describe-instance-status \
  --instance-ids i-0123456789abcdef0 \
  --include-all-instances

aws ssm send-command \
  --instance-ids i-0123456789abcdef0 \
  --document-name AWS-RunShellScript \
  --parameters 'commands=["uname -r","dnf check-update || true","systemctl is-active atlas-payments"]'
```

EC2 status checks patria bližšie k provider infrastructure a VM boundary. Kernel/package/application state je customer boundary. Green prvý príkaz neanuluje failure v druhom.

Pri patch incidente preto AWS Support nie je prvý owner guest package conflictu. Atlas musí zachovať package transaction logs, AMI generation a application outcome. AWS sa zapája, ak evidence ukazuje platform alebo host failure mimo guest controlu.

## 7. Managed database responsibility

AWS pri RDS prevádzkuje host, storage platform, control plane a service-specific patch/failover/backup mechanisms. Atlas vlastní engine version choice v dostupnom contracte, users, authentication, schema, migrations, query plans, network exposure, KMS key, parameter configuration, backup retention, restore test a client failover behavior.

Nasledujúci príkaz ukáže provider-visible configuration:

```bash
aws rds describe-db-instances \
  --db-instance-identifier atlas-payments-prod \
  --query 'DBInstances[0].{Status:DBInstanceStatus,Engine:Engine,Version:EngineVersion,MultiAZ:MultiAZ,Public:PubliclyAccessible,Retention:BackupRetentionPeriod,KmsKey:KmsKeyId}'
```

Výstup môže potvrdiť Multi-AZ, encryption key a backup retention. Nevie zodpovedať, či application user má zbytočné `DROP` oprávnenie, či schema migration bola backward-compatible alebo či restore spĺňa RTO.

Customer-side SQL control:

```sql
select current_user;
select grantee, privilege_type
from information_schema.role_table_grants
where table_schema = 'payments'
order by grantee, table_name, privilege_type;
```

Tento query testuje database authorization. AWS managed service nemôže automaticky rozhodnúť, že application role nemá mať delete permission nad určitým business table.

## 8. Serverless a managed runtime responsibility

Pri Lambda alebo managed container runtime AWS vlastní host provisioning, runtime platform a service scaling mechanismus. Atlas vlastní code, dependencies, execution role, event-source policy, input validation, concurrency, retries, idempotency, secrets, outbound dependencies a business recovery.

`Invocations` bez `Errors` nepreukazuje correctness. Handler môže swallow-nuť chybu alebo vykonať duplicate side effect. Reserved concurrency je customer configuration a môže byť nastavená príliš vysoko voči database capacity.

Praktický read-back:

```bash
aws lambda get-function-configuration \
  --function-name payments-settlement \
  --query '{Version:Version,Role:Role,Timeout:Timeout,Memory:MemorySize,ReservedEnv:Environment.Variables.CONFIG_GENERATION,Vpc:VpcConfig}'

aws lambda get-policy --function-name payments-settlement
```

Prvý príkaz ukazuje runtime configuration a execution role. Druhý ukazuje resource-based invoke policy. Ani jeden nepreukazuje downstream idempotency. Tá ostáva application responsibility.

## 9. IAM ako shared authorization system

AWS poskytuje IAM policy engine a STS. Atlas vytvára policy graph. Effective authorization môže zahŕňať identity policy, resource policy, permissions boundary, session policy, SCP, KMS key policy a request conditions.

Ukážková identity policy pre workload role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadProviderSecret",
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:eu-central-1:100000000042:secret:prod/payments/provider-*"
    },
    {
      "Sid": "DecryptOnlyForPaymentsContext",
      "Effect": "Allow",
      "Action": "kms:Decrypt",
      "Resource": "arn:aws:kms:eu-central-1:100000000042:key/11111111-2222-3333-4444-555555555555",
      "Condition": {
        "StringEquals": {
          "kms:EncryptionContext:application": "payments",
          "kms:EncryptionContext:environment": "prod"
        }
      }
    }
  ]
}
```

Táto policy je iba candidate grant. KMS key policy musí umožniť relevantný IAM path a žiadny SCP alebo boundary nesmie action blokovať. Forbidden test má použiť inú role alebo iný encryption context a očakávať deny.

Praktická simulácia môže pomôcť, ale musí používať exact action, resource a context:

```bash
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::100000000042:role/payments-runtime \
  --action-names kms:Decrypt \
  --resource-arns arn:aws:kms:eu-central-1:100000000042:key/11111111-2222-3333-4444-555555555555 \
  --context-entries \
    ContextKeyName=kms:EncryptionContext:application,ContextKeyValues=payments,ContextKeyType=string \
    ContextKeyName=kms:EncryptionContext:environment,ContextKeyValues=prod,ContextKeyType=string
```

Simulator nie je náhrada reálneho service-specific testu. Nemusí modelovať všetky external policy alebo service boundaries rovnako ako live request. Výsledok treba korelovať s actual caller a CloudTrail.

## 10. Network responsibility

AWS prevádzkuje physical a virtual-network platformu. Atlas vlastní VPC CIDRs, subnets, route tables, Security Groups, NACLs, gateways, endpoints, hybrid routing, DNS a application TLS.

Keď connection timeoutuje, provider health status nemusí byť relevantný. Exact path treba rozložiť:

```text
source ENI a IP
→ subnet route table
→ gateway alebo endpoint
→ SG a NACL
→ destination listener
→ return path
→ TLS a application auth
```

Praktický `describe-route-tables` alebo Flow Log `ACCEPT` nepreukazuje remote listener. Responsibility closure vyžaduje observations z každej boundary.

## 11. Data, encryption a recovery responsibility

AWS môže poskytovať durable storage, snapshots, replication a encryption capabilities. Atlas určuje authoritative data, classification, access, key ownership, retention, immutability, recovery point, RPO/RTO a reconciliation.

`Encrypted=true` nepreukazuje least-privilege decrypt. `Backup job completed` nepreukazuje application-consistent restore. `Multi-AZ` nepreukazuje recovery z logical delete.

Praktický recovery control musí obsahovať restore experiment:

```text
select exact recovery point
→ restore into isolated environment
→ attach approved network and identity
→ validate schema and data invariants
→ run read/write canary
→ reconcile external provider state
→ measure RPO/RTO
→ delete test environment safely
```

Provider vykoná service-specific restore mechanismus. Atlas musí rozhodnúť, či restored result je business-valid.

## 12. Logging a detection responsibility

AWS emituje CloudTrail events, service metrics, logs, health events a security findings podľa configuration. Atlas musí zvoliť coverage, destination, retention, integrity, queries, alerts a response.

Napríklad CloudTrail Event history nie je dlhodobý central archive a data events nie sú automaticky zapnuté pre každý S3 object alebo Lambda invoke. Ak incident vyžaduje event, ktorý selector nikdy nezachytával, absence v logu nie je dôkaz absencie operation.

Control test preto nevykoná iba `aws cloudtrail get-trail-status`. Vytvorí canary API operation, overí event delivery do expected archive a spustí detection rule.

## 13. Worked incident: hlásený „KMS outage“, ale chybná policy generation

Po release `I42` prestali payment Pods dešifrovať settlement credential. Application vracala `AccessDeniedException`, KMS service health bol green. Subject zahŕňal workload role `WR42`, STS session `S-884`, key `K42`, key-policy generation `KP19`, identity-policy generation `IP31` a encryption context `application=payments, environment=prod`.

Hypotézy zahŕňali provider KMS outage, disabled key, wrong Region, chýbajúci identity grant, key-policy deny, nesprávny encryption context, endpoint policy a stale workload credentials. `aws sts get-caller-identity` z affected workloadu ukázal očakávanú role session. CloudTrail zaznamenal `Decrypt` requesty na správny key ARN, no context používal `app=payments` namiesto policy field `application=payments`.

AWS KMS vykonal policy presne podľa customer configuration. Root cause bol mismatch medzi application context generation a key policy. Containment zastavil retry storm a zachoval request IDs. Recovery obnovila kompatibilný context, potom prebehli allowed aj forbidden decrypt testy. Old malformed context bol odmietnutý a payment settlement skončil presne raz.

Incident sa neuzavrel vetou „KMS funguje“. Uzavrel sa dôkazom, že exact workload môže decryptovať iba s approved contextom a iná role alebo tenant context zlyhá.

## 14. Responsibility pri support eskalácii

Dobrý support case nezačína všeobecným „AWS service nefunguje“. Obsahuje account, Region, resource ARN, UTC timeline, request IDs, service error, recent configuration change, observed customer-side path a minimal reproducer.

Pred eskaláciou Atlas overí svoj account, Region, identity, policy, network a configuration. To neznamená, že provider nemôže byť root cause. Znamená to, že support dostane diskriminačné evidence a incident sa nebude zdržovať základným zisťovaním contextu.

## 15. Periodická revalidácia

Responsibility sa môže zmeniť, keď Atlas prejde z EC2 na RDS, z self-managed Kubernetes na EKS Auto Mode alebo zapne novú managed feature. Každá architektonická zmena preto aktualizuje control manifest, evidence path a recovery ownera.

Closure model je:

```text
provider capability je dostupná
+ customer configuration je reviewovaná
+ effective state je pozorovaný
+ evidence je uchovaná
+ incident owner a recovery sú známe
+ positive a forbidden tests prešli
→ control je accepted
```

## Kontrolné otázky

1. Prečo je shared responsibility model service-specific?
2. Ktoré EC2 layers vlastní AWS a ktoré Atlas?
3. Ktoré database responsibilities zostávajú Atlasu pri RDS?
4. Prečo identity policy sama nemusí vytvoriť KMS decrypt access?
5. Čo simulator preukazuje a čo musí overiť live request?
6. Kedy je absent CloudTrail event nedostatočný dôkaz?
7. Prečo encrypted resource ešte nemusí byť recoverable?
8. Aký forbidden test patrí ku credential alebo KMS controlu?
9. Aké údaje potrebuje kvalitná AWS Support eskalácia?
10. Kedy sa musí responsibility matrix znovu otvoriť?

## Oficiálna dokumentácia

- [AWS Shared Responsibility Model](https://aws.amazon.com/compliance/shared-responsibility-model/)
- [AWS Risk and Compliance — Shared responsibility model](https://docs.aws.amazon.com/whitepapers/latest/aws-risk-and-compliance/shared-responsibility-model.html)
- [IAM policy evaluation logic](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html)
- [AWS KMS key policies](https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html)
- [AWS CloudTrail User Guide](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html)
- [AWS CLI Command Reference](https://docs.aws.amazon.com/cli/latest/reference/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Regions a Availability Zones](regions-availability-zones.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Scalability, elasticity a fault tolerance →](scalability-elasticity-fault-tolerance.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
