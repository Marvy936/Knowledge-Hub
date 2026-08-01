# Terraform providers, resources a data sources

Terraform Core nevie priamo vytvoriť VPC, DNS record ani databázu. Provider je samostatne versionovaný executable plugin, ktorý implementuje schemas a prekladá Terraform graph na operácie konkrétneho API. Provider preto nie je iba knižnica syntaxe. Je to zároveň supply-chain dependency, target-resolution boundary, authentication boundary, remote-object identity boundary a zdroj plan/apply behavioru.

Táto kapitola pokračuje incidentom `IAC-PAY-75`. Atlas Payments chce spravovať primary platformu v `eu-central-1`, replica storage v `eu-west-1` a iba čítať DNS zone vlastnenú centrálnym platform tímom. Root module má dve AWS provider configurations, no child module nedostane alias mapping. Resource sa vytvorí cez default provider v primary regione, zatiaľ čo mutable data source vyberie nový „latest“ image bez source diffu.

## 1. Dominantný provider-to-object lifecycle

Provider lifecycle prepája tri identity domains: executable dependency, effective API target a Terraform management address. Provider requirement vyberá plugin family, dependency lock stabilizuje konkrétnu package selection a provider configuration určuje endpoint, account, region a credentials. Až potom resource alebo data-source address vstupuje do graphu.

```text
provider source a version constraint
→ selected package a checksums
→ provider configuration a alias
→ workload identity, account a region
→ resource alebo data-source address
→ plan-time read alebo CRUD decision
→ remote API request a response
→ remote object identity
→ state binding alebo read-only value
→ downstream dependency a runtime verification
```

Resource address je Terraform ownership identity; remote ID je platform identity a state binding ich spája. Data source remote lifecycle nevlastní, ale jeho resolved value môže zmeniť graph alebo release. Syntakticky platná HCL preto môže zasiahnuť nesprávny target alebo vybrať inú immutable dependency bez source diffu.

## 2. Terraform Core verzus provider responsibility

Terraform Core:

```text
načíta configuration a state
→ vyhodnotí expressions
→ zostaví dependency graph
→ požiada provider o schemas/read/plan/apply operácie
→ koordinuje graph execution
→ pripraví nový state snapshot
```

Provider:

```text
načíta provider configuration
→ autentizuje caller-a
→ interpretuje resource/data-source schema
→ volá remote API
→ retryuje, polluje a normalizuje response
→ vracia remote identity a attributes
```

Provider určuje aj to, ktoré zmeny možno vykonať in-place, ktoré vyžadujú replacement, ktoré attributes sú computed a ako sa správa pri eventual consistency. Provider upgrade preto môže zmeniť plan bez zmeny HCL. Je to behavior change, ktorý patrí do review a compatibility testov.

## 3. Requirement, selected version a lock file

Root module deklaruje provider requirement:

```hcl
terraform {
  required_version = "~> 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
```

Version constraint neidentifikuje presný executable package. `terraform init` vyrieši konkrétnu verziu a zapíše selection a checksums do `.terraform.lock.hcl`.

Praktický verification:

```bash
terraform init -input=false
terraform providers
sha256sum .terraform.lock.hcl
```

`terraform providers` preukazuje, ktoré provider requirements a configurations Terraform rozpoznal v aktuálnom resolved module graph-e. Digest lock file-u preukazuje integritu konkrétneho súboru. Nepreukazuje, že provider package pochádza z dôveryhodného mirroru, že child module používa správny alias ani že credentials smerujú do správneho accountu.

Provider lock file sa commitne do root configuration repository. Upgrade sa vykonáva ako vedomá dependency change:

```bash
terraform init -upgrade
terraform plan -out=provider-upgrade.tfplan
terraform show -json provider-upgrade.tfplan > provider-upgrade.json
```

Review porovná plan actions, replacement reasons a provider release compatibility. „Iba lockfile diff“ nie je administratívna zmena, ak mení executable behavior.

## 4. Provider configuration je target identity

Atlas používa primary a replica configuration:

```hcl
provider "aws" {
  region = "eu-central-1"

  default_tags {
    tags = {
      Environment = "prod-eu"
      ManagedBy   = "terraform"
    }
  }
}

provider "aws" {
  alias  = "replica"
  region = "eu-west-1"
}
```

Effective target zahŕňa viac než `region` v HCL:

```text
provider configuration address
+ environment variables a shared config
+ workload credentials
+ account/organization context
+ region a custom endpoints
+ assume-role chain
+ provider retries a feature flags
```

Pred apply sa target overí nezávisle:

```bash
aws sts get-caller-identity --output json
aws configure get region
```

Observed account/ARN a region preukazujú caller context pre tieto CLI requesty. Nepreukazujú, že Terraform provider používa úplne rovnaký credential source alebo alias. Najsilnejší model používa rovnakú workload identity a explicitné provider configuration inputs, ktoré pipeline read-backne bez secretov.

## 5. Provider aliases v child module contracte

Child module, ktorý potrebuje viac configurations, musí aliasy deklarovať:

```hcl
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      configuration_aliases = [
        aws.source,
        aws.destination
      ]
    }
  }
}
```

Caller ich explicitne mapuje:

```hcl
module "replication" {
  source = "./modules/replication"

  providers = {
    aws.source      = aws
    aws.destination = aws.replica
  }

  source_bucket      = module.primary.bucket_name
  destination_bucket = "atlas-payments-replica"
}
```

Provider alias mapping je súčasť resolved configuration subjectu. Bez explicitného mappingu môže child resource zdediť default provider a vytvoriť objekt v primary regione. Green API response potom preukazuje iba úspešnú mutation v effective targete, nie správnosť zamýšľaného targetu.

## 6. Managed resource: address, remote ID a binding

Managed resource:

```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.40.0.0/16"
}
```

má tri odlišné identity:

```text
configuration/resource address
aws_vpc.main

provider configuration
provider["registry.terraform.io/hashicorp/aws"]

remote identity
account 7711 / eu-central-1 / vpc-0a42
```

State ich spojí:

```text
aws_vpc.main
→ provider aws default
→ vpc-0a42
```

Address nie je cloud ID. Premenovanie resource blocku bez `moved` contractu môže vyzerať ako destroy/create. Strata bindingu môže viesť k duplicate create. Rovnaký remote ID spravovaný dvoma addresses alebo states vytvára conflict ownership incident.

Inspection:

```bash
terraform state list
terraform state show aws_vpc.main
```

`state show` preukazuje známu state reprezentáciu a binding pre aktuálny backend subject. Nepreukazuje live health, správny traffic ani to, že objekt nezmenil druhý writer. Pre current remote observation treba refresh/plan alebo provider-native read API.

## 7. Arguments, attributes a unknown values

Resource configuration poskytuje arguments. Provider vracia attributes, z ktorých niektoré vzniknú až po create:

```hcl
output "vpc_id" {
  value = aws_vpc.main.id
}
```

Počas planu môže byť hodnota:

```text
(known after apply)
```

Unknown value nie je wildcard ani `null`. Terraform pozná type a dependency, ale nie konkrétnu hodnotu. To je bezpečné pre downstream argument, ktorý môže čakať na apply. Nie je to bezpečné pre graph-shaping keys, provider target alebo authorization decision, ktoré musia byť známe pred mutation.

## 8. Data source je read contract, nie lifecycle ownership

Centrálny platform state vlastní DNS zone. Application configuration ju iba queryuje:

```hcl
data "aws_route53_zone" "payments" {
  name         = "payments.example.com."
  private_zone = false
}

resource "aws_route53_record" "api" {
  zone_id = data.aws_route53_zone.payments.zone_id
  name    = "api.payments.example.com"
  type    = "A"

  alias {
    name                   = aws_lb.api.dns_name
    zone_id                = aws_lb.api.zone_id
    evaluate_target_health = true
  }
}
```

Data source načíta hodnoty cez provider, ale lifecycle queryovaného objektu nespravuje. Jeho output môže vytvoriť dependency a môže sa zmeniť bez source diffu.

Praktický risk je nejednoznačná query:

```hcl
data "aws_ami" "runtime" {
  most_recent = true
  owners      = ["self"]

  filter {
    name   = "name"
    values = ["atlas-runtime-*"]
  }
}
```

Rovnaký source commit môže o týždeň resolve-nuť iné AMI. Plan potom navrhne replacement, hoci Git diff neexistuje. `most_recent` je discovery mechanism, nie immutable release identity.

Bezpečnejší release chain je:

```text
image build a scan
→ immutable AMI ID alebo OCI digest
→ approval/promotion
→ explicitný Terraform input
→ deployment
```

## 9. Data-source timing a deferred reads

Data source sa môže načítať pri plan-e, ak sú jeho arguments známe. Ak závisí od resource vytvoreného v rovnakom apply, read sa odloží:

```hcl
data "example_endpoint" "runtime" {
  service_id = example_service.payments.id
}
```

```text
service_id unknown
→ data read deferred to apply
→ endpoint unknown v plan-e
```

Plan potom poskytuje menej presnú evidence. Široký `depends_on` môže odložiť read aj bez skutočnej value dependency. To je dôvod, prečo sa dependencies vyjadrujú konkrétnymi outputs a references namiesto module-wide barriers.

## 10. Stable instance identity: `for_each` verzus `count`

Managed resources potrebujú stabilnú address identity.

```hcl
resource "aws_subnet" "private" {
  for_each = var.subnets

  vpc_id            = aws_vpc.main.id
  availability_zone = each.value.zone
  cidr_block        = each.value.cidr
}
```

Addresses:

```text
aws_subnet.private["az-a"]
aws_subnet.private["az-b"]
```

Keys `az-a` a `az-b` sú management identity. Zmena keya môže vyzerať ako remove/create, hoci CIDR ostane rovnaký. `count` používa indexy; vloženie položky do stredu listu môže posunúť viac identities.

`for_each` nie je automaticky bezpečný. Key musí byť stabilný a nesmie pochádzať z mutable display name-u alebo apply-time unknown value.

## 11. Provider failure semantics a eventual consistency

Provider request môže skončiť viacerými outcomes:

```text
remote request odmietnutý bez mutation
remote create complete a read-after-write ešte 404
remote create complete, provider timeout
partial object existuje
provider vráti ID, state write zlyhá
API normalizuje hodnotu inak než configuration
```

Náhodný `sleep 60` nevytvára dôkaz. Lepší model používa provider-native waiter, bounded retry a nezávislý post-apply read-back.

Pri timeout-e sa najprv overí request ID, remote object a state binding. Retry bez reconciliation môže vytvoriť duplicate resource alebo opakovať side effect.

## 12. Worked incident: alias sa nepreniesol

Atlas chcel replica bucket v `eu-west-1`. Root configuration poznala `aws.replica`, ale child module nedeklaroval `configuration_aliases` a caller neposlal explicitný mapping. Child resource preto zdedil default provider a validná workload identity vytvorila bucket v `eu-central-1`.

```text
root pozná aws.replica
→ child resource dostane default aws
→ API request uspeje v primary regione
→ state binding je technicky konzistentný
→ replication capability je business nesprávna
```

Containment zastaví ďalšiu replication promotion a zachová plan, provider mapping a audit events. Remote inventory musí identifikovať oba buckets podľa accountu, regionu, ARN a data state-u; názov alebo tag nestačí. Až potom sa pridá explicitný alias contract a zvolí copy, import alebo recreate podľa obsahu a consumers.

Recovery sa uzatvára správnym provider mappingom v module graph-e, presným state bindingom, replication journey testom a forbidden fixture, ktorá zámerne vynechá alias a musí zlyhať pred mutation. Nesprávny bucket sa odstraňuje až po potvrdení, že nie je jediným nositeľom dát alebo active consumer dependency.

## 13. Worked incident: mutable data source zmenil release

Application source, variables a module version sa nezmenili. Publisher však pridal nové AMI, ktoré splnilo `most_recent` filter.

```text
rovnaký Git commit
→ nový provider read
→ iné AMI ID
→ instance replacement
→ test evidence patrí starému image
```

Plan presne zobrazil replacement, ale process nesprávne považoval source equality za release identity equality. Náprava je explicitný immutable image input a resolved-input manifest.

## 14. Competing hypotheses pri wrong-region objekte

Symptom: `module.replication.aws_s3_bucket.replica` existuje v primary regione.

```text
H1: child module zdedil default provider
H2: alias mapping existuje, ale credentials smerujú do iného accountu
H3: provider region prepísal environment/shared config
H4: state patrí inému backendu
H5: pozorujeme iný bucket s rovnakým menom
H6: provider/API ignoroval alebo normalizoval argument
```

Diskriminačné dôkazy:

```bash
terraform providers
terraform state show 'module.replication.aws_s3_bucket.replica'
aws sts get-caller-identity
aws s3api get-bucket-location --bucket atlas-payments-replica
```

`terraform providers` ukáže provider dependencies/configuration relationships, state show binding a AWS CLI remote location. Ani jeden výstup samostatne nepreukazuje celý chain. Spolu s planom, audit eventom a source mappingom môžu potvrdiť H1.

## 15. Acceptance a forbidden paths

Provider/object blok je prijatý až vtedy, keď:

```text
provider source/version/checksums sú pinned
+ primary a replica aliases sú explicitné
+ caller account/region sú read-backnuté
+ managed resources majú jediný state binding
+ data sources používajú jednoznačný read contract
+ release-critical image je immutable input
+ wrong-region provider mapping je policy/testom odmietnutý
+ second plan je no-op
+ runtime replication journey prejde
```

Forbidden test má zámerne prehodiť provider mapping v disposable fixture a potvrdiť, že policy alebo assertion run zastaví pred mutation. Pozitívny happy-path test bez forbidden variantu nepreukazuje enforcement.

## 16. Anti-patterny

### „Provider constraint stačí, lock file netreba“

Constraint povoľuje rozsah; lock identifikuje konkrétnu selection a checksums.

### „Alias je iba meno“

Alias vyberá konkrétnu provider configuration a tým endpoint, account, region aj credential chain. Zmena alebo chýbajúci mapping môže vytvoriť správny resource type v nesprávnom targete. Provider relationship sa preto read-backuje cez resolved graph a testuje forbidden mappingom.

### „Data source nič nemení, takže je bez rizika“

Data source priamo nevlastní remote lifecycle, ale jeho value môže vybrať image, subnet, policy alebo počet resource instances. Mutable query teda môže bez source diffu zmeniť plan a vyvolať replacement. Release-critical values sa pinujú ako immutable inputs a evidujú v resolved manifest-e.

### „State address a cloud ID sú to isté“

Address je Terraform management identity; remote ID je platform identity. Binding ich spája.

### „Successful API response znamená správny objekt“

API success dokazuje, že effective caller mohol vykonať operation v effective targete. Nehovorí, či account, region, remote ID alebo attribute set zodpovedali approved subjectu. Verdict dopĺňa target read-back, state binding a runtime/business test.

## 17. Kontrolné otázky

1. Prečo je provider executable trust boundary?
2. Aký rozdiel je medzi provider requirementom a dependency lockom?
3. Čo tvorí effective provider configuration?
4. Prečo musí child module explicitne deklarovať provider aliases?
5. Aký rozdiel je medzi resource address, provider configuration a remote ID?
6. Čo preukazuje `terraform state show` a čo nepreukazuje?
7. Prečo unknown value nie je `null`?
8. Kedy data source znižuje reproducibility?
9. Prečo `most_recent` nie je vhodná final release identity?
10. Ako `for_each` key ovplyvňuje state binding?
11. Aké dôkazy odlíšia wrong alias od wrong credentials?
12. Ako sa testuje forbidden provider mapping path?

## Glossary impact

Relevantné pojmy: Terraform Core, provider, provider requirement, dependency lock file, provider configuration, alias, managed resource, data source, resource address, remote identity, state binding, computed attribute, unknown value, configuration alias, immutable input, eventual consistency a provider failure semantics.

## Primárne zdroje

- [Terraform providers](https://developer.hashicorp.com/terraform/language/providers)
- [Provider requirements](https://developer.hashicorp.com/terraform/language/providers/requirements)
- [Terraform resources](https://developer.hashicorp.com/terraform/language/resources)
- [Terraform data sources](https://developer.hashicorp.com/terraform/language/data-sources)
- [Providers within modules](https://developer.hashicorp.com/terraform/language/modules/develop/providers)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Infrastructure as Code principles](infrastructure-as-code-principles.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Variables, locals a outputs →](variables-locals-outputs.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
