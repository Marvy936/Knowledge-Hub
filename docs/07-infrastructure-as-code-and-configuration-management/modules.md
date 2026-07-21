# Modules

Terraform **module** je kolekcia konfiguračných súborov, ktoré Terraform vyhodnocuje ako jednu kompozičnú jednotku. Každá Terraform konfigurácia má root module; `module` blocky volajú child modules.

Modul nemá byť iba priečinok so skopírovanými resources. Má predstavovať stabilný contract, ktorý skrýva primeranú implementačnú komplexitu a umožňuje callerovi vyjadriť architektonický zámer.

## 1. Root a child module

- **root module** je konfigurácia spustená príkazom `terraform plan` alebo `terraform apply`,
- **child module** je reusable konfigurácia volaná z iného modulu,
- child module môže volať ďalšie child modules,
- všetky resources z celej module hierarchy patria do jedného dependency graphu a state-u konkrétneho root module runu.

Module nie je samostatná state boundary automaticky. Samostatný state vzniká až samostatným root module/backend lifecycle.

## 2. Module block

```hcl
module "network" {
  source  = "app.terraform.io/example/network/aws"
  version = "~> 3.4"

  name       = "payments-prod"
  cidr_block = "10.40.0.0/16"
}
```

Caller určuje:

- source,
- pri podporovanom source type aj version constraint,
- input values,
- provider mappings,
- `count`, `for_each` alebo dependencies podľa potreby.

Po zmene module source alebo version sa pracovný adresár znovu inicializuje cez `terraform init`.

## 3. Module source

Bežné source modely:

- local relative path,
- Terraform registry,
- private registry,
- Git/VCS source,
- podporované archive alebo object-storage zdroje.

Source je executable dependency. Potrebuje:

- dôveryhodného ownera,
- immutable alebo presne pinovanú verziu,
- review zmien,
- release notes,
- provenance a access controls,
- kontrolovaný upgrade proces.

Použitie mutable branch bez commit/tag/version identity oslabuje reprodukovateľnosť planu.

## 4. Modulový contract

Contract tvoria najmä:

- input variables,
- output values,
- required providers,
- resource behavior a lifecycle assumptions,
- naming a tagging conventions,
- compatibility a upgrade policy,
- dokumentované side effects.

Caller nemá byť nútený poznať interné resource addresses, pokiaľ nejde o vedomý operational contract.

## 5. Input variables

Inputs majú byť:

- typované,
- pomenované podľa doménového významu,
- validované,
- s rozumnými defaults iba tam, kde sú bezpečné,
- bez skrytých environment assumptions.

Príliš veľa boolean switches často signalizuje, že modul obsahuje viac nesúvisiacich produktov alebo modes.

```hcl
variable "service" {
  type = object({
    name        = string
    environment = string
    replicas    = optional(number, 2)
  })

  validation {
    condition     = contains(["dev", "stage", "prod"], var.service.environment)
    error_message = "environment musí byť dev, stage alebo prod."
  }
}
```

## 6. Outputs

Outputs majú publikovať stabilné capability alebo identity:

```hcl
output "subnet_ids" {
  value = values(aws_subnet.this)[*].id
}
```

Nevystavuj celý provider resource object iba pre pohodlie. Caller sa tým naviaže na internú implementáciu, provider schema a budúce refaktoringy.

Dobré outputy sú:

- úzke,
- pomenované podľa významu,
- typovo predvídateľné,
- dokumentované,
- kompatibilné naprieč minor releases modulu.

## 7. Providers v moduloch

Reusable child module má deklarovať `required_providers`, ale provider configurations typicky vlastní root module.

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}
```

Caller môže odovzdať alias:

```hcl
module "replica" {
  source = "./modules/database"

  providers = {
    aws = aws.replica
  }
}
```

Tým zostáva authentication, account/region selection a environment identity v orchestration vrstve.

## 8. Module composition

Preferovaný model:

```text
root module
→ skladá menšie capability modules
→ prepája outputs na inputs
→ vlastní environment-specific policy
```

Príklad:

```hcl
module "network" {
  source = "./modules/network"
  cidr   = var.network_cidr
}

module "service" {
  source     = "./modules/service"
  subnet_ids = module.network.private_subnet_ids
}
```

Reference vytvorí implicitnú dependency medzi module outputs a caller inputs.

## 9. Úroveň abstrakcie

Modul má zmysel, keď:

- reprezentuje opakovateľnú capability,
- vynucuje bezpečné defaults,
- kodifikuje organizačnú policy,
- znižuje počet rozhodnutí callerovi,
- má jasného ownera a lifecycle.

Modul bez pridanej hodnoty, ktorý iba premapuje každé provider pole 1:1 na input, vytvára wrapper layer bez abstrakcie.

## 10. Veľkosť modulu

Príliš veľký modul má:

- veľký blast radius,
- veľa inputs a conditional paths,
- pomalé testy,
- komplikované upgrades,
- nejasné ownership boundaries.

Príliš malý modul:

- nepridáva stabilný contract,
- zvyšuje nesting,
- komplikuje navigáciu a debugging,
- môže iba premenovať jeden resource.

Boundary vyber podľa capability, ownershipu, lifecycle a change coupling-u.

## 11. `count` a `for_each` na module calls

```hcl
module "service" {
  for_each = var.services
  source   = "./modules/service"

  name = each.key
  port = each.value.port
}
```

Module instance address potom obsahuje key:

```text
module.service["payments"]
```

Rovnako ako pri resources, stabilné `for_each` keys sú vhodnejšie než indexy, keď identity objektov nie sú pozičné.

## 12. Versioning modulov

Module release má komunikovať:

- compatibility inputs/outputs,
- zmeny defaults,
- resource replacement risk,
- migration kroky,
- required Terraform/provider versions,
- `moved` blocks a deprecations.

Semantic Versioning je užitočný iba vtedy, keď je public contract explicitný a release proces ho reálne dodržiava.

## 13. Upgrade workflow

Bezpečný upgrade:

1. prečíta release notes,
2. aktualizuje version constraint alebo source ref,
3. spustí `terraform init -upgrade` v kontrolovanom prostredí,
4. overí provider/module selections,
5. vykoná static checks a tests,
6. vytvorí plan voči aktuálnemu state-u,
7. vyhodnotí replacements a address moves,
8. applyne s observability a recovery plánom.

„Minor update“ nie je dôvod ignorovať plan.

## 14. Module registry

Registry poskytuje distribution metadata, versions a dokumentáciu. Nezaručuje automaticky:

- bezpečný kód,
- kompatibilitu,
- kvalitný ownership,
- vhodnosť pre konkrétny environment,
- bezpečné defaults.

Pred adopciou over source, maintainers, releases, tests, provider constraints a upgrade históriu.

## 15. Dokumentácia modulu

Minimálne dokumentuj:

- purpose a non-goals,
- inputs a outputs,
- provider/Terraform requirements,
- príklad použitia,
- security assumptions,
- created resources a side effects,
- upgrade/migration notes,
- testing a support policy.

Generated input/output tables sú doplnok, nie náhrada architektonického contractu.

## 16. Testing

Module test portfolio má zahŕňať:

- formatting a validation,
- input validation,
- plan assertions,
- apply/integration tests pre kritické behavior,
- policy/security scans,
- upgrade test z podporovanej predchádzajúcej verzie,
- examples ako executable documentation.

Testy majú používať izolované names, účty/projects a cleanup mechanizmus.

## 17. Security

Module môže vytvárať privileged resources vo veľkom rozsahu. Kontroluj:

- source integrity,
- provider permissions,
- defaults pre public access a encryption,
- secret handling,
- network exposure,
- destructive lifecycle,
- cross-account alebo cross-project behavior,
- supply-chain updates.

Caller musí vedieť, aké permissions potrebuje plan a apply identity.

## 18. Observability a audit

Pre module consumption sleduj:

- používané versions,
- deprecated versions,
- upgrade lead time,
- plan/apply failure rate,
- replacement count,
- policy violations,
- adoption bezpečnostných opráv.

Bez inventory consumers nevie module owner bezpečne ukončiť starý contract.

## 19. Anti-patterny

### Jeden mega-modul pre celý cloud účet

Veľký blast radius a nejasný lifecycle.

### Module source na mutable `main`

Rovnaká konfigurácia môže neskôr načítať iný kód.

### Child module konfiguruje credentials

Authentication boundary je skrytá v reusable implementation.

### Výstupom je celý resource object

Caller sa viaže na internú provider schema.

### Desiatky boolean flags

Modul obsahuje príliš veľa nesúvisiacich modes.

### Kopírovanie modulu namiesto versioningu

Vznikajú divergentné forks bez centrálnej opravy.

## 20. Troubleshooting

### `Module not installed`

Spusti `terraform init` a over source, credentials, network a version availability.

### Caller nevie použiť provider alias

Over `required_providers`, alias mapping cez `providers` a očakávaný local provider name.

### Upgrade plánuje recreations

Skontroluj release notes, resource addresses, changed defaults, provider behavior a dostupné `moved` blocks.

### Module output je unknown

Output závisí od apply-time hodnoty. Nevyužívaj ho na graph-shaping `for_each` keys v tom istom plane.

### Module versions sa medzi CI a lokálom líšia

Over source/version constraint, `terraform init` režim, cache a či source nie je mutable.

## 21. Kontrolné otázky

1. Aký je rozdiel medzi root a child module?
2. Prečo module nie je automaticky state boundary?
3. Čo tvorí public contract modulu?
4. Prečo root module typicky vlastní provider configurations?
5. Kedy je modul príliš tenký alebo príliš veľký?
6. Ako `for_each` ovplyvňuje module addresses?
7. Prečo mutable source oslabuje reprodukovateľnosť?
8. Čo má obsahovať bezpečný module upgrade workflow?
9. Ako testovať backward compatibility modulu?
10. Ktoré metriky potrebuje owner interného module registry?

## Glossary impact

Relevantné pojmy: Terraform module, root module, child module, module source, module contract, module composition, module registry, provider mapping, module instance a module versioning.

## Oficiálna dokumentácia

- [Modules overview](https://developer.hashicorp.com/terraform/language/modules)
- [Use modules in your configuration](https://developer.hashicorp.com/terraform/language/modules/configuration)
- [Develop modules](https://developer.hashicorp.com/terraform/language/modules/develop)
