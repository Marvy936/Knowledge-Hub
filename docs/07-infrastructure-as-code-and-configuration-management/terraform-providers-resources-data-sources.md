# Terraform providers, resources a data sources

Terraform používa providers ako pluginy, ktoré prekladajú deklaratívnu konfiguráciu na volania konkrétnych cloud, SaaS alebo lokálnych API. Providers definujú resource types, data sources, schemas, CRUD behavior a spôsob čítania remote objektov.

## 1. Provider ako plugin boundary

Terraform Core:

- načíta konfiguráciu,
- zostaví dependency graph,
- vyhodnotí expressions,
- vytvorí plan,
- koordinuje apply a state.

Provider:

- pozná API platformy,
- validuje provider-specific arguments,
- vytvára, číta, mení a maže resources,
- mapuje remote odpovede na Terraform attributes,
- definuje data sources.

Provider je samostatne versionovaný executable dependency.

## 2. Required providers

Každý modul má deklarovať provider requirements:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
```

`source` určuje registry address a `version` povolený compatibility rozsah.

Root module typicky rozhoduje o konkrétnych provider versions pre celý configuration graph. Dependency lock file potom zachytáva vybrané versions a checksums.

## 3. Provider configuration

Provider block nastavuje runtime konfiguráciu:

```hcl
provider "aws" {
  region = var.aws_region
}
```

Credentials nemajú byť hardcoded v source. Preferuj:

- workload identity,
- environment alebo platform credential chain,
- short-lived federation,
- external secret manager.

Provider configuration patrí primárne do root module. Child modules majú deklarovať requirements a prijímať provider configurations od caller-a.

## 4. Provider aliases

Viac konfigurácií rovnakého providera sa rozlišuje aliasom:

```hcl
provider "aws" {
  region = "eu-central-1"
}

provider "aws" {
  alias  = "secondary"
  region = "eu-west-1"
}
```

Resource môže použiť alternatívnu konfiguráciu:

```hcl
resource "aws_s3_bucket" "replica" {
  provider = aws.secondary
  bucket   = "example-replica"
}
```

Alias je súčasť dependency a identity modelu. Pri modules sa explicitne mapuje cez `providers` argument.

## 5. Provider versions a lock file

Version constraint komunikuje povolený rozsah. Lock file zaznamenáva konkrétnu vybranú version a package checksums.

Dobrý model:

```text
required_providers constraint
→ terraform init
→ dependency selection
→ .terraform.lock.hcl
→ reviewed upgrade
```

Lock file patrí do version controlu pre root configurations. Provider upgrade má prejsť planom, testami a review.

## 6. Resource block

Resource reprezentuje objekt, ktorého lifecycle Terraform spravuje:

```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "main"
  }
}
```

Resource type je `aws_vpc`, local name je `main` a adresa je:

```text
aws_vpc.main
```

V module alebo pri multiple instances môže byť plná adresa napríklad:

```text
module.network.aws_subnet.private["eu-central-1a"]
```

## 7. Arguments a attributes

Arguments sú hodnoty dodané konfiguráciou.

Attributes sú hodnoty exportované providerom, vrátane computed hodnôt:

```hcl
output "vpc_id" {
  value = aws_vpc.main.id
}
```

Niektoré polia môžu byť:

- required,
- optional,
- computed,
- ForceNew/replacement-sensitive podľa provider schema.

Presný behavior sa overuje vo versionovanej provider dokumentácii a v plan-e.

## 8. Resource lifecycle

Základné operácie:

```text
Create
Read
Update
Delete
```

Pri refresh provider číta remote objekt. Pri plan-e Core porovná configuration, prior state a refreshed values.

Zmena môže viesť na:

- no-op,
- in-place update,
- replacement,
- destroy,
- create.

Replacement môže mať výrazný dopad na identity, adresy, dáta a availability.

## 9. Resource identity

Terraform resource address nie je remote ID.

```text
aws_vpc.main
→ vpc-0123456789
```

State mapuje deklarovanú adresu na provider-specific object identity.

Premenovanie resource labelu bez `moved` blocku môže vyzerať ako destroy/create, aj keď remote objekt zostáva rovnaký.

## 10. Data source

Data source číta informácie bez správy lifecycle remote objektu:

```hcl
data "aws_ami" "base" {
  most_recent = true
  owners      = ["self"]

  filter {
    name   = "tag:Role"
    values = ["base"]
  }
}
```

Referencia:

```hcl
image_id = data.aws_ami.base.id
```

Data source nie je „importovaný resource“. Terraform ho používa ako read-only query podľa provider behavioru.

## 11. Resources vs. data sources

| Vlastnosť | Resource | Data source |
|---|---|---|
| Spravuje lifecycle | áno | nie |
| Vytvára remote objekt | typicky áno | nie |
| Má state mapping | áno | výsledky čítania sú súčasťou run/state modelu |
| Použitie | desired managed object | external/existing information |

Ak objekt vlastní iný team alebo systém, data source môže byť vhodnejší než pokus spravovať ho z dvoch states.

## 12. Plan-time a apply-time hodnoty

Ak sú všetky arguments data source známe počas planu, Terraform ho môže prečítať pri refresh/plan fáze.

Ak argument závisí od hodnoty známej až po apply, výsledok bude:

```text
(known after apply)
```

To môže preniesť unknown hodnoty do ďalších resources a znížiť presnosť planu.

## 13. Implicitné dependencies

Referencia automaticky vytvorí dependency edge:

```hcl
resource "aws_subnet" "app" {
  vpc_id = aws_vpc.main.id
}
```

Terraform vie, že VPC musí existovať pred subnetom.

Preferuj value references pred explicitným `depends_on`, pretože zároveň prenášajú konkrétnu hodnotu a presnejšie vysvetľujú vzťah.

## 14. Explicitné `depends_on`

Použi ho iba pri hidden dependency, ktorú nemožno vyjadriť cez hodnotu:

```hcl
resource "example_service" "app" {
  depends_on = [example_policy.runtime]
}
```

Nevýhody nadmerného `depends_on`:

- konzervatívnejší plan,
- viac unknown hodnôt,
- znížená paralelizácia,
- nejasný architecture contract.

Každý explicitný dependency edge má mať komentár s dôvodom.

## 15. `count` a `for_each`

Viac instances resource možno vytvoriť pomocou meta-arguments.

### `count`

```hcl
resource "example_instance" "worker" {
  count = 3
  name  = "worker-${count.index}"
}
```

Identity používa numerický index. Odstránenie položky zo stredu listu môže posunúť identity.

### `for_each`

```hcl
resource "example_subnet" "app" {
  for_each = var.subnets
  cidr     = each.value.cidr
}
```

Identity používa stabilný key:

```text
example_subnet.app["private-a"]
```

Pre dlhodobo identifikovateľné objekty je `for_each` často bezpečnejší.

## 16. Provider configuration inheritance

Child module automaticky používa default provider configuration podľa pravidiel Terraformu, ale aliases sa musia explicitne deklarovať a mapovať.

Príklad:

```hcl
module "replication" {
  source = "./modules/replication"

  providers = {
    aws.source      = aws
    aws.destination = aws.secondary
  }
}
```

Provider mappings sú súčasť module contractu.

## 17. Authentication a authorization

Provider potrebuje dve odlišné veci:

- authentication: kto je caller,
- authorization: čo smie vykonať.

Pipeline identity má mať minimum permissions potrebné pre daný state scope.

Oddel:

- plan/read identity podľa platformy,
- apply identity,
- environment-specific roles,
- break-glass admin identity.

## 18. Provider behavior a eventual consistency

Cloud API môže po create vrátiť objekt skôr, než je dostupný vo všetkých subsystémoch.

Provider rieši časť retry a polling behavioru, ale stále môžu vzniknúť:

- transient 404,
- propagation delay,
- throttling,
- timeout,
- partial create,
- inconsistent read-after-write.

Náhodné `sleep` provisioners nie sú dobré univerzálne riešenie. Preferuj provider-native waits, explicitné health checks alebo oddelený verification krok.

## 19. Provider schema a upgrades

Provider upgrade môže zmeniť:

- default values,
- validation,
- normalization,
- computed attributes,
- replacement behavior,
- deprecated fields,
- resource migration logic.

Preto upgrade vykonávaj ako riadenú dependency zmenu s čerstvým planom.

## 20. Anti-patterny

### Neobmedzené provider versions

Budúci `init` môže vybrať nekompatibilnú release.

### Credentials v provider blocku

Secrets skončia v source, plan logs alebo history.

### Dva states spravujú rovnaký remote objekt

Vzniká ownership konflikt a oscilujúci drift.

### Data source vyberá „most recent“ mutable artifact bez policy

Rovnaký commit môže neskôr nasadiť iný image alebo objekt.

### `depends_on` medzi celými modules bez dôvodu

Graf sa stane zbytočne serializovaný a plan konzervatívny.

### Mutable provider/module source

Reprodukcia starého planu nie je dôveryhodná.

## 21. Troubleshooting

### Provider sa neinštaluje

Over source address, version constraints, lock file, registry/network access a platform checksum.

### Resource sa plánuje nahradiť

Skontroluj provider schema, changed argument, identity, normalization a lifecycle behavior.

### Data source je `known after apply`

Nájdi argument závislý od computed hodnoty a zváž oddelenie states alebo stabilnejší input contract.

### Resource používa zlý account/region

Over provider alias, module provider mapping, credentials a environment context.

### Terraform plánuje duplicate object

Over state mapping, import/adoption stav, resource address a workspace/backend identity.

## 22. Kontrolné otázky

1. Ktoré úlohy vykonáva Terraform Core a ktoré provider?
2. Aký je rozdiel medzi provider requirement a provider configuration?
3. Na čo slúži dependency lock file?
4. Čo tvorí resource address?
5. Aký je rozdiel medzi argumentom a computed attribute?
6. Kedy použiť data source namiesto resource?
7. Ako referencia vytvára implicitnú dependency?
8. Kedy je legitímny `depends_on`?
9. Prečo môže byť `for_each` stabilnejší než `count`?
10. Aké riziká prináša provider upgrade?

## Glossary impact

Relevantné pojmy: Terraform provider, provider requirement, provider configuration, provider alias, dependency lock file, Terraform resource, resource address, resource identity, data source, computed value, implicit dependency, explicit dependency, `count`, `for_each` a provider schema.

## Oficiálna dokumentácia

- [Providers](https://developer.hashicorp.com/terraform/language/providers)
- [Provider requirements](https://developer.hashicorp.com/terraform/language/providers/requirements)
- [Resources](https://developer.hashicorp.com/terraform/language/resources)
- [Data sources](https://developer.hashicorp.com/terraform/language/data-sources)
