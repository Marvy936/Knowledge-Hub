# IaaS, PaaS a SaaS

IaaS, PaaS a SaaS nie sú tri úrovne toho istého produktu. Sú to tri odlišné dohody o tom, kto vlastní konkrétnu vrstvu systému počas návrhu, prevádzky, incidentu a obnovy. Vyššia abstrakcia môže odstrániť správu serverov alebo runtime-u, ale neodstraňuje zodpovednosť za business dáta, identitu, konfiguráciu, integrácie, recovery objective ani výsledok používateľskej operácie.

Preto nezačíname vetou „použijeme managed service“. Začíname business capability a rozkladáme ju na vrstvy, ktoré musí niekto bezpečne prevádzkovať.

```text
business outcome a SLO
→ dáta, identity a integrations
→ application behavior
→ runtime a data engine
→ operating system
→ compute, storage a network
→ physical infrastructure
```

Pri každej vrstve sa pýtame, kto ju provisionuje, kto ju konfiguruje, kto ju patchuje, kto ju pozoruje, kto reaguje na incident a kto dokáže recovery. Až tento rozklad ukáže skutočný service model.

## 1. Connected subject: Atlas Payments

Celá sekcia používa capability `CAP-PAY-42`. Payment API musí autorizovať platbu do 700 ms p99, mesačne dosahovať 99,95 % availability a pre potvrdené settlement transakcie má nulovú toleranciu straty. Customer-facing API má RTO 30 minút. Primárny workload beží v `eu-central-1`, no zároveň komunikuje s on-premises ledgerom `L17`.

Release identity nie je iba názov služby. Tvorí ju source commit `G42`, image digest `I42`, configuration generation `C42`, credential epoch `SE10`, databázová schema a presná network/identity cesta. Ak tím povie iba „bežíme na EC2“ alebo „presunuli sme sa na PaaS“, nevie ešte preukázať, ktorá z týchto generácií skutočne vytvára payment outcome.

## 2. Praktický responsibility manifest

Pred výberom konkrétnej služby je užitočné zapísať responsibility contract ako versionovaný dokument. Nemusí mať špeciálny formát; dôležité je, aby sa dal reviewovať spolu s architektúrou.

```yaml
capability: CAP-PAY-42
outcome:
  description: Authorize and settle one payment exactly once
  latencyP99Ms: 700
  availabilityMonthly: 99.95
  rtoMinutes: 30
  confirmedSettlementRpo: 0

layers:
  applicationCode:
    owner: atlas-payments
    evidence: image digest and deployment generation
  businessData:
    owner: atlas-payments
    evidence: ledger invariant and recovery test
  runtime:
    owner: undecided
  operatingSystem:
    owner: undecided
  virtualization:
    owner: provider
  physicalInfrastructure:
    owner: provider

recovery:
  authority: atlas-payments-incident-commander
  acceptedWhen:
    - one authorization and one settlement exist
    - old credential is rejected
    - second reconciliation pass is a no-op
```

Tento manifest nie je AWS configuration. Je to rozhodovací artefakt. Ak po výbere služby ostanú položky `undecided`, architektúra má nejasné vlastníctvo. Pri incidente sa potom rovnaká operácia môže považovať za úlohu providera, platform tímu aj application tímu a nikto ju nevykoná včas.

## 3. IaaS: provider dodá infraštruktúrny mechanizmus, zákazník prevádzkuje hostovaný systém

Pri Infrastructure as a Service poskytuje provider compute, storage, network a virtualization control plane. Na AWS je typickým príkladom EC2 spolu s VPC a EBS. AWS vlastní fyzické dátové centrá, hardware a hypervisorovú vrstvu. Atlas však naďalej vlastní guest OS, packages, runtime, application, host firewall, configuration, patching, image provenance, backup workflow aj spôsob, akým viac instances vytvorí dostupnú službu.

Reálny lifecycle preto vyzerá takto:

```text
launch-template a AMI intent
→ EC2 instance a block/network resources
→ guest OS boot
→ bootstrap a package/runtime state
→ application process
→ load-balancer eligibility
→ payment request
→ patch, replacement alebo recovery
```

EC2 stav `running` potvrdzuje iba určitú infraštruktúrnu boundary. Nehovorí, či je OS patchnutý, či systemd spustil správny binary, či aplikácia načítala `C42` a `SE10`, či filesystem nie je plný alebo či workload prežije stratu Availability Zone.

Nasledujúce príkazy ukazujú rozdiel medzi provider-visible a application-visible stavom:

```bash
aws ec2 describe-instances \
  --instance-ids i-0123456789abcdef0 \
  --query 'Reservations[0].Instances[0].{State:State.Name,Image:ImageId,AZ:Placement.AvailabilityZone,Profile:IamInstanceProfile.Arn}'

aws ec2 describe-instance-status \
  --instance-ids i-0123456789abcdef0 \
  --include-all-instances

aws ssm send-command \
  --instance-ids i-0123456789abcdef0 \
  --document-name AWS-RunShellScript \
  --parameters 'commands=["systemctl is-active atlas-payments","curl -fsS http://127.0.0.1:8080/readyz"]'
```

Prvý príkaz identifikuje instance generation, AMI, AZ a instance profile. Druhý ukazuje EC2 system a instance status checks. Až tretí kontroluje guest OS a local application path. Ani ten ešte neoveruje load balancer, external DNS, databázu ani skutočnú payment autorizáciu.

IaaS je správna voľba, keď workload potrebuje kernel alebo OS control, špecifický driver, legacy runtime, host agent alebo veľmi presnú host-level diagnostiku. Cena tejto kontroly je, že tím musí vedieť reprodukovateľne buildovať AMI, patchovať fleet, nahrádzať snowflake instances, spravovať capacity a testovať restore.

## 4. PaaS: provider preberie platformový mechanizmus, nie application contract

Platform as a Service presúva na providera viac OS a runtime práce. Managed relational database, Lambda, managed application runtime alebo Kubernetes control plane môžu automatizovať host replacement, patching, replication primitives a časť scalingu. Atlas však stále vlastní schema, queries, data classification, access policies, network exposure, retry semantics, quotas, backup retention, restore test a business acceptance.

Pri managed databáze lifecycle nevyzerá ako „AWS sa stará o databázu“. Vyzerá takto:

```text
customer schema a transaction intent
→ provider-managed engine a storage platform
→ customer endpoint, network, TLS a database identity
→ customer query/lock/transaction behavior
→ provider backup alebo failover mechanismus
→ customer application reconnect a reconciliation
→ business outcome
```

Praktický read-back ukazuje, čo provider skutočne vytvoril:

```bash
aws rds describe-db-instances \
  --db-instance-identifier atlas-payments-prod \
  --query 'DBInstances[0].{Status:DBInstanceStatus,Engine:Engine,Version:EngineVersion,MultiAZ:MultiAZ,Endpoint:Endpoint.Address,BackupRetention:BackupRetentionPeriod,LatestRestorable:LatestRestorableTime}'
```

Výstup môže potvrdiť, že DB instance je `available`, používa očakávaný engine, má Multi-AZ a definované backup retention. Nevie však potvrdiť, že application používa správny endpoint, schema je kompatibilná, transakcia `P-884` commitla presne raz alebo že point-in-time restore bol niekedy úspešne overený.

Preto musí nasledovať application-path test, napríklad read-only kontrola identity a schema generation cez presnú runtime credential:

```bash
psql "$ATLAS_DATABASE_URL" -v ON_ERROR_STOP=1 <<'SQL'
select current_database(), current_user;
select version from schema_generation where component = 'payments';
select count(*) from settlement where payment_id = 'P-884';
SQL
```

Tento SQL už testuje databázovú session a business data path. Stále však nepreukazuje external provider side effect alebo recovery schopnosť. PaaS znižuje platform toil, ale neposúva application correctness na providera.

## 5. SaaS: provider prevádzkuje aplikáciu, zákazník vlastní tenant a proces

Software as a Service dodáva hotovú application capability. Provider spravuje application code, runtime aj infraštruktúru. Zákazník však spravuje tenant configuration, users, federation, role model, sharing, integrations, retention, export a spôsob, akým SaaS zapadá do business procesu.

Pri hypotetickom SaaS payment-gateway portáli by lifecycle vyzeral takto:

```text
Atlas tenant a federation configuration
→ provider application
→ provider internal runtime a storage
→ Atlas users, API clients a webhooks
→ Atlas ledger a reconciliation
→ customer business outcome
```

Provider status page môže byť zelená, ale Atlas tenant môže mať expirovaný webhook secret, chybný SSO claim mapping alebo príliš širokú admin role. SaaS tiež vytvára exit dependency. Tím musí vedieť, aké dáta vie exportovať, v akom formáte, s akou históriou a za aký čas.

Praktický SaaS acceptance test preto nečíta provider internú infraštruktúru. Testuje tenant-facing contract: federated login, API call s least-privilege tokenom, webhook delivery, audit export a obnovu konfigurácie. Ak provider neposkytuje potrebnú export alebo audit schopnosť, vyššia abstrakcia nie je vhodná pre daný business contract.

## 6. Rovnaká capability v troch modeloch

Nasledujúca tabuľka ukazuje zmenu ownershipu, nie „množstvo cloudu“.

| Vrstva | EC2/IaaS | Managed runtime alebo database | SaaS capability |
|---|---|---|---|
| Fyzická infraštruktúra | provider | provider | provider |
| Guest OS a host patching | Atlas | provider | provider |
| Application implementation | Atlas | Atlas | provider |
| Tenant/service configuration | Atlas | Atlas | Atlas |
| Identity a access model | Atlas/shared | Atlas/shared | Atlas/shared |
| Business data governance | Atlas | Atlas | Atlas/shared |
| Business RTO/RPO | Atlas | Atlas | Atlas |
| Recovery acceptance | Atlas | Atlas | Atlas podľa export/restore contractu |
| User-path telemetry | Atlas | Atlas | Atlas synthetic + provider evidence |

Dôležitý je posledný riadok každej vrstvy. Provider môže garantovať určitú service availability, no Atlas stále musí merať, či zákazník dokázal autorizovať a settle-nuť platbu. Service credit nie je recovery mechanizmus.

## 7. Worked incident: managed databáza funguje, settlement records chýbajú

Atlas presunul payment API z EC2 fleet-u na managed runtime a settlement databázu na managed relational service. Tím začal hovoriť, že „provider vlastní HA aj backup“, a prestal pravidelne testovať recovery.

Dňa 28. júla 2026 medzi 08:10 a 08:17 UTC application credential `SE10` vykonal chybnú delete operáciu nad settlement records. Databázový resource `DB42` v `eu-central-1` zostal `available`. Backup policy `BP7` mala sedemdňovú retention a latest automated recovery point `RP92`.

Prvé hypotézy zahŕňali provider storage corruption, failover na stale repliku, application migration, chybný customer credential, neúplné backup retention a čítanie nesprávneho endpointu. Diskriminačný dôkaz vznikol koreláciou database audit eventu, application operation ID, exact principalu, endpointu a transaction ledgeru. Audit ukázal delete cez Atlas application role. Provider platforma fungovala podľa contractu; root cause bol customer-owned authorization a application behavior. Neotestovaný recovery contract bol contributing control failure.

Containment najprv revoke-nul `SE10`, zastavil delete-capable writer a ďalšie settlement processing. Tím zachoval audit, request IDs, database logs a canonical ledger. Nerobil in-place restore cez production databázu, pretože by prepísal transakcie po incidentnom cut-offe.

Recovery vytvorila isolated point-in-time restore. Chýbajúce settlement rows sa porovnali s immutable ledgerom a doplnili idempotentnou reconciliation operáciou. Nový scoped credential `SE11` sa vydal až po read/write teste. Payment processing sa otvoril po overení, že každá potvrdená platba má presne jeden settlement record a druhý reconciliation pass je no-op.

Tento incident ukazuje podstatu service modelu: provider prevzal engine a storage platformu, nie customer authorization, transaction design ani business recovery.

## 8. Praktické rozhodovanie medzi modelmi

Výber sa dá zúžiť štyrmi otázkami. Prvá sa pýta, aký control je skutočne potrebný. Ak workload vyžaduje kernel module alebo host agent, SaaS ani väčšina PaaS možností ho neposkytnú. Druhá sa pýta, aký operational toil tím dokáže spoľahlivo vlastniť. IaaS bez reproducible image a patch programu je iba odložený incident.

Tretia otázka sa týka data a recovery contractu. Managed service je vhodná iba vtedy, keď podporuje potrebný RPO, restore, export, encryption a audit model. Štvrtá sa týka exit-u. Čím vyššia abstrakcia a viac provider-specific APIs, tým dôležitejší je preukázateľný data export, compatibility plan a bounded migration path.

Rozhodnutie má skončiť explicitným statementom, napríklad:

```text
CAP-PAY-42 používa managed relational PaaS,
pretože nepotrebuje host control a potrebuje Multi-AZ engine mechanismus.
Atlas naďalej vlastní schema, IAM, network path, idempotency,
backup retention, restore rehearsal a business reconciliation.
```

Tento statement je omnoho presnejší než „RDS sa stará o databázu“.

## 9. Verification checklist bez falošného green stavu

Pri IaaS acceptance musí byť známa AMI a launch generation, patch state, process health, load-balancer eligibility a business canary. Pri PaaS acceptance musí byť známy endpoint, engine/config generation, customer identity, schema, recovery point a restore result. Pri SaaS acceptance musí byť známa tenant configuration, federation, role scope, integration credential, export a audit path.

Spoločný closure model je:

```text
provider resource alebo service je healthy
+ customer configuration je effective
+ runtime alebo tenant používa approved identity
+ data invariant platí
+ recovery path bol otestovaný
+ forbidden access a stale credential zlyhávajú
→ business capability je accepted
```

## Kontrolné otázky

1. Ktoré vrstvy CAP-PAY-42 sa presunú na providera pri prechode z EC2 na managed database?
2. Prečo `DBInstanceStatus=available` nie je dôkazom správnej payment transakcie?
3. Ktoré customer responsibilities zostávajú aj pri SaaS?
4. Kedy je host-level control reálny requirement a kedy iba preferencia?
5. Aký artefakt preukáže, že responsibility owner nie je iba implicitný predpoklad?
6. Prečo provider SLA nenahrádza workload HA a recovery test?
7. Ktorý positive a forbidden test uzavrie credential rotation alebo recovery?
8. Ako by si pre CAP-PAY-42 zdokumentoval exit z vybraného PaaS alebo SaaS modelu?

## Oficiálna dokumentácia

- [AWS Shared Responsibility Model](https://aws.amazon.com/compliance/shared-responsibility-model/)
- [AWS Risk and Compliance — Shared responsibility model](https://docs.aws.amazon.com/whitepapers/latest/aws-risk-and-compliance/shared-responsibility-model.html)
- [Amazon EC2 documentation](https://docs.aws.amazon.com/ec2/)
- [Amazon RDS documentation](https://docs.aws.amazon.com/rds/)
- [AWS CLI Command Reference](https://docs.aws.amazon.com/cli/latest/reference/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Helm and CKA](../10-helm-and-cka/README.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Public, private a hybrid cloud →](public-private-hybrid-cloud.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
