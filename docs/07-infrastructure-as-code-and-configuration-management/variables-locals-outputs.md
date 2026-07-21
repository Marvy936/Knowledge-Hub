# Variables, locals a outputs

Input variables, local values a outputs tvoria interface Terraform modulov. Variables prinášajú vstupy, locals pomenúvajú interné expressions a outputs publikujú výsledky pre callerov, operátorov alebo ďalšie automatizácie.

Dobrý module interface oddeľuje stabilný kontrakt od implementačných detailov.

## 1. Input variables

Variable block definuje vstup modulu:

```hcl
variable "environment" {
  description = "Deployment environment name."
  type        = string
}
```

Referencia:

```hcl
var.environment
```

V child module je variable argument, ktorý poskytuje caller. V root module možno hodnotu dodať cez CLI, variable files, environment variables alebo remote execution platformu.

## 2. Povinná a voliteľná variable

Variable bez `default` je povinná:

```hcl
variable "region" {
  type = string
}
```

Variable s defaultom je voliteľná:

```hcl
variable "replica_count" {
  type    = number
  default = 2
}
```

Default má byť bezpečný a predvídateľný. Produkčné rizikové správanie nemá byť skryté za pohodlným defaultom.

## 3. Type constraints

Type constraint dokumentuje a validuje vstupný kontrakt.

Primitívne typy:

- `string`,
- `number`,
- `bool`.

Kolekcie a štruktúry:

- `list(T)`,
- `set(T)`,
- `map(T)`,
- `tuple([...])`,
- `object({...})`.

Príklad:

```hcl
variable "subnets" {
  type = map(object({
    cidr              = string
    availability_zone = string
    public            = bool
  }))
}
```

Presný typ znižuje runtime prekvapenia a zlepšuje editor/tooling support.

## 4. Optional object attributes

Komplexný input môže mať optional fields:

```hcl
variable "service" {
  type = object({
    name        = string
    port        = number
    enable_tls  = optional(bool, true)
    description = optional(string)
  })
}
```

Optional fields pomáhajú evolúcii module interface, ale veľké množstvo voliteľných kombinácií môže vytvoriť neotestovateľný „univerzálny“ modul.

## 5. Validation

Custom validation kontroluje business alebo domain invariant:

```hcl
variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "stage", "prod"], var.environment)
    error_message = "Environment must be dev, stage, or prod."
  }
}
```

Validácia má:

- zlyhať skoro,
- vysvetliť opravu,
- overovať skutočný contract,
- nezdvojovať provider validation bez pridanej hodnoty.

## 6. `nullable`

Variable môže explicitne riadiť, či prijíma `null`:

```hcl
variable "description" {
  type     = string
  nullable = true
  default  = null
}
```

`null` typicky znamená omission alebo neprítomnosť hodnoty podľa kontextu. Nie je to to isté ako prázdny string, nula alebo prázdna kolekcia.

Module contract má presne definovať semantics `null`.

## 7. Sensitive variables

```hcl
variable "api_token" {
  type      = string
  sensitive = true
}
```

`sensitive` obmedzuje zobrazovanie hodnoty v bežnom CLI/UI outpute. Neznamená:

- encryption v state,
- ochranu pred škodlivým providerom,
- ochranu pred job scriptom,
- bezpečné uloženie v source alebo `.tfvars`.

Secrets majú prichádzať zo secure identity alebo secret-management workflowu.

## 8. Hodnoty root variables

Root module môže dostať hodnoty napríklad cez:

```text
-var
-var-file
*.auto.tfvars
terraform.tfvars
TF_VAR_<name>
HCP Terraform workspace variables
```

Precedence a source hodnoty musia byť zrozumiteľné. Skrytá kombinácia viacerých files a environment variables komplikuje reprodukciu planu.

V CI zachovaj evidence:

- ktorý variable set bol použitý,
- ktorý environment ho poskytol,
- ktoré hodnoty boli sensitive,
- ktorý commit a plan ich vyhodnotil.

## 9. Variable files

Príklad `prod.tfvars`:

```hcl
environment   = "prod"
replica_count = 6
```

Variable files s necitlivou environment konfiguráciou môžu byť versionované.

Do repository nepatria:

- passwords,
- private keys,
- dlhodobé cloud credentials,
- customer secrets.

## 10. Local values

Locals pomenúvajú expressions v module:

```hcl
locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  name_prefix = "${var.project}-${var.environment}"
}
```

Referencia:

```hcl
local.common_tags
```

Local nie je vstup a caller ho nemôže override-nuť.

## 11. Na čo sú locals vhodné

Použi locals na:

- pomenovanie opakovanej expression,
- normalizáciu vstupov,
- odvodené názvy,
- common tags/labels,
- transformáciu collections,
- interný compatibility adapter.

Nepoužívaj locals na skrytie stoviek riadkov business logiky. Príliš komplexné locals znižujú čitateľnosť planu a module contractu.

## 12. Locals a dependencies

Local môže referencovať variables, resources, data sources a iné locals:

```hcl
locals {
  endpoint = "https://${example_service.app.hostname}"
}
```

Dependency sa zachová cez expression. Local nevytvára runtime objekt; iba pomenúva hodnotu a dependency path.

Circular local references nie sú povolené.

## 13. Outputs

Output publikuje hodnotu modulu:

```hcl
output "service_url" {
  description = "Public service endpoint."
  value       = "https://${example_service.app.hostname}"
}
```

V caller module:

```hcl
module.app.service_url
```

Root outputs možno čítať cez:

```bash
terraform output
terraform output -json
```

## 14. Output ako module API

Output má publikovať stabilný contract, nie celý provider resource object.

Slabý interface:

```hcl
output "everything" {
  value = aws_vpc.main
}
```

Lepší interface:

```hcl
output "vpc_id" {
  value = aws_vpc.main.id
}

output "private_subnet_ids" {
  value = values(aws_subnet.private)[*].id
}
```

Explicitné outputs znižujú coupling na provider schema a module internals.

## 15. Sensitive outputs

```hcl
output "generated_password" {
  value     = random_password.app.result
  sensitive = true
}
```

Sensitive output sa stále môže uložiť v state. Navyše `terraform output -json` alebo `-raw` môže hodnotu zobraziť v plain texte oprávnenému callerovi.

Sensitive output preto nie je náhrada za secret manager.

## 16. Output preconditions

Output môže kontrolovať invariant výsledku:

```hcl
output "service_url" {
  value = local.service_url

  precondition {
    condition     = startswith(local.service_url, "https://")
    error_message = "Service URL must use HTTPS."
  }
}
```

Precondition dokumentuje assumption, ktorý musí platiť pred publikovaním contractu.

## 17. Unknown values

Pri plan-e nemusí byť output známy:

```text
service_url = (known after apply)
```

Unknown nie je chyba. Znamená, že provider alebo upstream resource hodnotu určí až pri apply.

Riziko vzniká, keď unknown hodnoty ovplyvňujú:

- `for_each` keys,
- `count`,
- provider configuration,
- backend configuration,
- plan-time policy rozhodnutia.

Keys pre `for_each` musia byť známe dostatočne skoro na zostavenie resource graphu.

## 18. Module composition

Moduly sa skladajú cez explicitné inputs a outputs:

```hcl
module "network" {
  source = "./modules/network"
  cidr   = var.vpc_cidr
}

module "application" {
  source     = "./modules/application"
  subnet_ids = module.network.private_subnet_ids
}
```

Referencia na output zároveň vytvorí dependency.

## 19. Cross-state outputs

Zdieľanie outputs medzi oddelenými states vytvára external contract.

Možnosti:

- remote state data source,
- configuration registry,
- service catalog,
- DNS/service discovery,
- cloud-native parameter store,
- pipeline-publikovaný manifest.

Remote state consumer typicky potrebuje prístup k state snapshotu, nie iba k logicky publikovaným hodnotám. Pre citlivé boundaries môže byť bezpečnejší explicitný publish mechanizmus.

## 20. Naming a documentation

Variable a output názvy majú byť:

- stabilné,
- domain-oriented,
- bez zbytočnej implementačnej terminológie,
- konzistentné naprieč modules.

Každý významný input/output má mať `description`.

Dokumentuj aj:

- units,
- accepted values,
- null semantics,
- sensitive behavior,
- compatibility/deprecation policy.

## 21. Interface evolution

Backward-compatible zmeny:

- nový optional input s bezpečným defaultom,
- nový output,
- rozšírenie object inputu o optional field.

Potenciálne breaking zmeny:

- premenovanie inputu/outputu,
- zmena type constraint,
- zmena default semantics,
- odstránenie outputu,
- zmena identity keys v collection.

Module versioning má tieto zmeny komunikovať.

## 22. Anti-patterny

### `type = any` bez dôvodu

Contract je nejasný a chyby sa objavia hlboko v expressions alebo providerovi.

### Desiatky boolean flags

Modul má príliš veľa behavior kombinácií a slabú cohesion.

### Secrets v `.tfvars` commite

Version control history ich zachová aj po zmazaní aktuálneho súboru.

### Output celého resource objectu

Caller sa naviaže na provider internals.

### Locals ako skrytý programovací jazyk

Komplexná transformácia je ťažko testovateľná a čitateľná.

### `sensitive = true` ako jediná secret control

Hodnota môže zostať v state a byť dostupná jobu/providerovi.

## 23. Troubleshooting

### Terraform žiada hodnotu nečakanej variable

Variable nemá default alebo root input source nebol načítaný. Over názov, `-var-file`, workspace variables a environment.

### Type conversion mení dáta

Over object/tuple constraints, optional attributes a implicitné conversions. Použi presnejší typ.

### Output je unknown

Nájdi upstream computed value. Over, či unknown neblokuje graph-shaping expression.

### Sensitive hodnota sa objavila v logu

Masking nie je transitívna ochrana všetkých tools. Rotuj secret, audituj exfiltration path a oprav job/provider logging.

### Child module používa nesprávny default

Over caller arguments, default values, null semantics a module version.

## 24. Kontrolné otázky

1. Aký je rozdiel medzi variable, local a output?
2. Prečo je presný type constraint súčasťou module contractu?
3. Ako sa líši `null` od prázdnej hodnoty?
4. Čo `sensitive` chráni a čo nechráni?
5. Kedy použiť custom validation?
6. Ako locals zachovávajú dependency graph?
7. Prečo output celého resource objectu vytvára coupling?
8. Ako outputs skladajú modules?
9. Kedy unknown value komplikuje plan?
10. Ako bezpečne evolvovať module interface?

## Glossary impact

Relevantné pojmy: Terraform input variable, type constraint, optional attribute, variable validation, nullable value, sensitive value, local value, output value, module interface, unknown value, root module input a cross-state contract.

## Oficiálna dokumentácia

- [Manage values in modules](https://developer.hashicorp.com/terraform/language/values)
- [Input variables](https://developer.hashicorp.com/terraform/language/values/variables)
- [Local values](https://developer.hashicorp.com/terraform/language/block/locals)
- [Output values](https://developer.hashicorp.com/terraform/language/values/outputs)
