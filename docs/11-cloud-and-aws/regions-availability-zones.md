# Regions a Availability Zones

Region a Availability Zone nie sú iba názvy lokality. Sú to placement a fault-isolation boundaries, ktoré rozhodujú, kde resource vznikne, ktoré kapacity môže použiť, aké dáta a služby má nablízku a aký failover je vôbec technicky možný.

Region je oddelená geografická oblasť a väčšina resources je regionálna alebo zonálna. Availability Zone je izolovanejšia lokalita v rámci Regionu. Jedna AZ obsahuje jednu alebo viac samostatných dátových centier a AZs v Regione sú prepojené low-latency vysokokapacitnou sieťou. To umožňuje Multi-AZ aplikácie, no neznamená to, že každý resource alebo každá dependency sa automaticky rozloží do viacerých AZs.

## 1. Placement subject pre Atlas Payments

Atlas Payments používa account `A42`, primárny Region `eu-central-1` a recovery Region `eu-west-1`. Production workload má bežať v troch fyzických AZ IDs: `euc1-az1`, `euc1-az2` a `euc1-az3`. Subnets `SUB42-a`, `SUB42-b` a `SUB42-c` mapujú každú application cohortu na jednu AZ. Load balancer `ALB42` je regionálny service contract s dataplane resources vo viacerých AZs. NAT gateways `NAT42-a/b/c` sú zonálne. Database `DB42` používa Multi-AZ generation `MZ9`.

Placement evidence preto nehovorí iba „beží to vo Frankfurte“. Musí viazať resource ARN alebo ID, Region, AZ ID, subnet, release generation a data generation.

```text
CAP-PAY-42
→ account A42
→ Region eu-central-1
→ AZ ID a subnet
→ zonal compute/network/storage
→ regional service coordination
→ serving release a data generation
```

## 2. Region selection je technické a business rozhodnutie

Region sa vyberá podľa data residency, latency, service availability, feature coverage, pricing, quotas, capacity, compliance a recovery strategy. Najbližší Region nemusí byť správny, ak v ňom chýba požadovaný engine, instance family alebo service feature. Rovnako lacnejší Region nemusí byť lacnejší po započítaní inter-Region transferu, support coverage a DR complexity.

Praktický preflight začína explicitnou identitou accountu a Regionu:

```bash
aws sts get-caller-identity
aws ec2 describe-regions \
  --all-regions \
  --query 'Regions[].{Region:RegionName,OptIn:OptInStatus}' \
  --output table
```

Prvý príkaz ukáže skutočný caller account a ARN. Druhý ukáže Regions a opt-in status dostupný pre konkrétny account. Výstup nepreukazuje, že všetky požadované služby a quotas sú pripravené. Preto treba pokračovať service-specific preflightom.

Napríklad:

```bash
aws service-quotas list-service-quotas \
  --service-code ec2 \
  --region eu-central-1 \
  --query 'Quotas[?contains(QuotaName, `Running On-Demand`)].{Name:QuotaName,Value:Value}'
```

Quota je regionálna boundary. Recovery Region môže mať správne Terraform templates a stále zlyhať, ak quota alebo capacity nie je dostupná.

## 3. AZ name a AZ ID nie sú vždy rovnaká fyzická identita

AZ name ako `eu-central-1a` je account-facing label. AZ ID ako `euc1-az2` identifikuje fyzickú zónu naprieč accounts. Pri cross-account shared subnets, coordinated placement alebo capacity reservation sa používa AZ ID.

```bash
aws ec2 describe-availability-zones \
  --region eu-central-1 \
  --filters Name=zone-type,Values=availability-zone \
  --query 'AvailabilityZones[].{Name:ZoneName,Id:ZoneId,State:State,OptIn:OptInStatus}' \
  --output table
```

Očakávaný výstup obsahuje dvojicu `ZoneName` a `ZoneId`. Ak dva accounts koordinujú placement, porovnávajú `ZoneId`, nie písmeno na konci name.

Tento detail je dôležitý aj pri dokumentácii incidentu. „AZ-a zlyhala“ je nejednoznačné v multi-account prostredí; `euc1-az2` je fyzicky stabilnejšia identita.

## 4. Resource scope určuje recovery mechanizmus

Zonal resource je viazaný na jednu AZ. EC2 instance, subnet, ENI a EBS volume patria do tejto kategórie. Pri strate AZ ich nemožno iba „prepnúť“ do druhej zóny; treba vytvoriť replacement, obnoviť volume zo snapshotu alebo použiť service-specific replication.

Regional resource existuje v scope Regionu, ale jeho data plane môže mať zonálne komponenty. VPC je regionálna, no subnets sú zonálne. Load balancer je regionálna služba, no používa enabled subnets/AZs a target cohorts. Regional control plane preto neznamená, že každá zóna má zdravú capacity.

Niektoré services majú global control alebo naming aspects. „Global“ však nesmie byť interpretované ako automatická multi-Region data durability. Presný scope sa vždy overuje pri konkrétnej službe.

## 5. Praktický Multi-AZ subnet návrh v Terraform-e

Nasledujúci príklad používa AZ IDs, nie hard-coded AZ names. To znižuje riziko, že rovnaká konfigurácia v inom account-e vyberie inú fyzickú zónu.

```hcl
variable "region" {
  type    = string
  default = "eu-central-1"
}

variable "application_az_ids" {
  type    = list(string)
  default = ["euc1-az1", "euc1-az2", "euc1-az3"]
}

data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  az_name_by_id = {
    for index, id in data.aws_availability_zones.available.zone_ids :
    id => data.aws_availability_zones.available.names[index]
  }

  subnet_cidrs = {
    "euc1-az1" = "10.42.16.0/20"
    "euc1-az2" = "10.42.32.0/20"
    "euc1-az3" = "10.42.48.0/20"
  }
}

resource "aws_vpc" "payments" {
  cidr_block           = "10.42.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "payments-prod"
  }
}

resource "aws_subnet" "application" {
  for_each = toset(var.application_az_ids)

  vpc_id            = aws_vpc.payments.id
  availability_zone = local.az_name_by_id[each.key]
  cidr_block        = local.subnet_cidrs[each.key]

  tags = {
    Name = "payments-${each.key}"
    AzId = each.key
    Tier = "application"
  }
}
```

Data source prečíta mapping aktuálneho accountu. `local.az_name_by_id` preloží stabilný AZ ID na account-specific AZ name, ktorý API vyžaduje pri tvorbe subnetu. `for_each` potom vytvorí jeden subnet v každej požadovanej fyzickej zóne.

Pred apply treba overiť, že každý AZ ID existuje v Regione a local map ho obsahuje. Terraform plan je desired-state dôkaz; nepreukazuje actual free IP capacity ani service capacity po apply.

## 6. Multi-AZ vzniká až naprieč celým dependency graphom

Tri subnets nevytvoria dostupnú aplikáciu, ak všetky instances používajú jeden zonálny NAT gateway, jeden EBS volume alebo database writer bez failoveru. Každá kritická vrstva musí odpovedať na otázku: čo zostane funkčné po strate jednej AZ?

Pre Atlas Payments musí surviving path obsahovať load-balancer nodes, application capacity, egress, database access, secrets/KMS, DNS, observability a deployment mechanismus. Ak scale-out závisí od subnetu s nulovým IP headroomom, Auto Scaling desired count je iba control-plane intent.

Praktický inventory:

```bash
aws ec2 describe-subnets \
  --region eu-central-1 \
  --filters Name=tag:Tier,Values=application \
  --query 'Subnets[].{Subnet:SubnetId,AzName:AvailabilityZone,AzId:AvailabilityZoneId,Cidr:CidrBlock,FreeIps:AvailableIpAddressCount}' \
  --output table
```

`AvailableIpAddressCount` je runtime capacity observation. Treba ho porovnať s rollout surge, failure-mode replacementom, load-balancer ENIs, endpoints a Pod/task IP demand. Steady-state voľné IPs nepreukazujú AZ-loss readiness.

## 7. Zonal capacity a statically stable design

Availability Zone môže byť healthy a predsa nemusí mať okamžitú capacity pre konkrétny instance type. Recovery preto potrebuje diversified instance families, quotas, subnet IPs a podľa criticality aj capacity reservation alebo warm capacity.

Auto Scaling policy, ktorá používa jediný large instance type, môže pri AZ failure opakovane dostávať insufficient-capacity errors. Flexibilnejší mixed-instances contract môže použiť viac kompatibilných typov a sizes, ale application musí byť otestovaná na rozdielnu architektúru, network a EBS envelope.

Pri kritickej službe treba tiež rozlíšiť control-plane scale-out od statically stable capacity. Ak failure zablokuje create APIs, už existujúca serving capacity v ostatných AZs musí uniesť minimálny business load bez okamžitého launchu nových instances.

## 8. Cross-AZ traffic nie je automaticky chyba ani výhra

Same-AZ affinity môže znížiť latency a transfer cost, no nesmie odstrániť failover. Cross-AZ routing zvyšuje flexibility, ale môže vytvoriť prekvapivý cost a skryť zonálne imbalance.

Dobrý design rozlišuje preferred path a failure path:

```text
same-AZ target alebo dependency
→ ak je healthy a má capacity
→ inak controlled cross-AZ fallback
→ po recovery rebalancing
```

Pri databáze alebo cache treba poznať consistency a write authority. Pri NAT treba vedieť, či každý subnet používa zonálny egress alebo regional NAT capability. Pri load balanceri treba poznať cross-zone behavior a target distribution.

## 9. Control plane a data plane počas incidentu

Control-plane operácie vytvárajú, menia a odstraňujú resources. Data-plane operácie obsluhujú packets, requests, reads a writes. Jedna vrstva môže zlyhať, zatiaľ čo druhá pokračuje.

Ak EC2 API dočasne nevytvorí nové instances, existujúce instances môžu stále obsluhovať traffic. Ak jedna AZ data-plane path zlyhá, regionálny API môže zostať zelený. Incident evidence preto musí obsahovať API request IDs aj per-AZ application behavior.

Príklad:

```bash
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name payments-api-prod \
  --region eu-central-1 \
  --max-items 20 \
  --query 'Activities[].{Time:StartTime,Status:StatusCode,Cause:Cause,Description:Description}'

aws elbv2 describe-target-health \
  --target-group-arn "$TARGET_GROUP_ARN" \
  --region eu-central-1 \
  --query 'TargetHealthDescriptions[].{Target:Target.Id,Az:Target.AvailabilityZone,State:TargetHealth.State,Reason:TargetHealth.Reason}'
```

Prvý príkaz ukáže, či controller nedokáže launchovať replacement. Druhý ukáže serving target cohort po AZs. Ani jeden sám nepreukazuje payment success; treba ich korelovať s business SLI.

## 10. Multi-AZ a multi-Region riešia iné failures

Multi-AZ optimalizuje availability v jednom Regione. Využíva nízku latency medzi AZs a service-specific failover alebo replication. Multi-Region rieši regional disaster, data residency alebo global proximity. Pridáva asynchronous replication, DNS/traffic steering, identity/key distribution, quotas, capacity a failback.

Recovery Region preto potrebuje viac než IaC. Musí mať deployable artifacts, KMS keys, secret generation, network, quotas, data recovery point, observability, external integration allowlists a capacity canary.

```bash
aws ec2 describe-subnets --region eu-west-1
aws service-quotas list-service-quotas --service-code ec2 --region eu-west-1
aws rds describe-db-snapshots --region eu-west-1 --snapshot-type manual
```

Tieto príkazy sú inventory preflight. Nevykonávajú restore ani business validation. „Snapshot existuje“ nie je DR readiness.

## 11. Worked incident: Multi-AZ na diagrame, single-AZ business outcome

Atlas deklaroval payment API ako Multi-AZ. `ALB42` mal targets v troch AZs a `DB42` používal Multi-AZ. Po strate `euc1-az2` však error rate stúpol na 65 % a replacement instances v ostatných AZs nevznikli.

Incident evidence ukázalo, že `SUB42-b` mala 92 % address utilization a `SUB42-c` 89 %. Všetky private subnet route tables zároveň smerovali default IPv4 egress na jediný zonálny `NAT42-a` v zlyhanej AZ. Database writer failover prebehol správne a load balancer odstránil unhealthy targets. Root cause nebol regionálny AWS outage, ale customer placement a capacity contract.

Containment zastavil nonessential deployments a retry amplification. Existing healthy capacity zostala serving. Recovery vytvorila egress v surviving AZs, opravila route associations a uvoľnila alebo rozšírila subnet address space. Auto Scaling dostal diversified instance types a rollout pokračoval po jednej AZ cohort-e.

Closure vyžadovala, aby remaining AZs uniesli failure-mode load, každá mala funkčný egress a replacement capacity a synthetic payment skončil jedným settlementom. Forbidden policy test odmietol route table, ktorá by všetky subnets smerovala na jediný zonálny NAT resource. Druhý AZ-failure drill prešiel bez manuálnej opravy.

## 12. Failure testing

Zonal test nemá začať force ukončením polovice produkcie. Najprv sa definuje expected outcome, blast radius a stop condition. Overí sa capacity headroom a external dependencies. Potom sa fault injektuje do jednej cohorty a sleduje sa traffic withdrawal, scale, data failover a business SLI.

Test je úspešný až keď service prežije failure a následne obnoví redundanciu. Ak traffic zostane zdravý iba preto, že failure cohorta sa nikdy nepoužívala, test nepreukázal reálny failover.

## Kontrolné otázky

1. Prečo je AZ ID vhodnejší cross-account identifier než AZ name?
2. Ktoré resources sú zonálne a aký recovery mechanizmus potrebujú?
3. Prečo tri subnets nepreukazujú Multi-AZ capability?
4. Ako vypočítaš subnet headroom pre rollout a stratu jednej AZ?
5. Kedy má statically stable capacity väčšiu hodnotu než okamžitý Auto Scaling?
6. Čo rozlišuje control-plane a data-plane evidence?
7. Prečo Multi-Region nie je iba druhý Terraform apply?
8. Ktoré dependencies zmenili incident na single-AZ business outcome?
9. Aký forbidden policy test zabráni návratu single-AZ NAT designu?
10. Čo musí preukázať druhý failure drill po recovery?

## Oficiálna dokumentácia

- [AWS Regions and Availability Zones](https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions-availability-zones.html)
- [AWS Availability Zones](https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-availability-zones.html)
- [Availability Zone IDs](https://docs.aws.amazon.com/global-infrastructure/latest/regions/az-ids.html)
- [AWS Fault Isolation Boundaries](https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/welcome.html)
- [AWS CLI `describe-availability-zones`](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-availability-zones.html)
- [Terraform AWS provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Public, private a hybrid cloud](public-private-hybrid-cloud.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Shared responsibility model →](shared-responsibility-model.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
