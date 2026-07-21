# Expressions a dependency graph

Terraform expressions vypočítavajú hodnoty a references medzi hodnotami zároveň vytvárajú dependency graph. Graph určuje, ktoré objekty možno plánovať a aplikovať paralelne a ktoré musia čakať na upstream dependencies.

## 1. Expressions

Expression môže byť jednoduchý literal:

```hcl
name    = "api"
enabled = true
count   = 3
```

Alebo odvodená hodnota:

```hcl
name = "${var.project}-${var.environment}"
```

Terraform expressions podporujú:

- references,
- operators,
- conditional expressions,
- `for` expressions,
- splat expressions,
- function calls,
- string templates,
- collection transformations.

## 2. Typy a hodnoty

Terraform pracuje s typmi:

- string,
- number,
- bool,
- list/tuple,
- map/object,
- set,
- `null`,
- unknown value počas planu.

Typ hodnoty a type constraint nie sú vždy totožné. Terraform môže vykonať bezpečné konverzie, napríklad tuple na list alebo object na obmedzenejší object type.

Implicitná konverzia môže zahodiť extra object attributes. Preto module interfaces majú používať presné typy a testy.

## 3. References

Named value references:

```hcl
var.environment
local.name_prefix
module.network.vpc_id
data.aws_ami.base.id
aws_vpc.main.id
```

Referencia plní dve úlohy:

1. poskytne hodnotu expression,
2. vytvorí dependency edge k objektu, ktorý hodnotu produkuje.

## 4. Unknown values

Pri plan-e Terraform používa unknown values pre údaje, ktoré poskytne až apply:

```text
id = (known after apply)
```

Unknown value nie je wildcard ani `null`. Terraform zachová typ a dependency, ale konkrétnu hodnotu ešte nepozná.

Príklad:

```hcl
resource "example_record" "app" {
  value = example_service.app.hostname
}
```

Ak hostname vznikne až po create, record možno naplánovať iba čiastočne.

## 5. Graph-shaping expressions

Niektoré hodnoty musia byť známe pred apply, pretože určujú samotnú štruktúru graphu:

- `count`,
- `for_each` keys,
- module source/version selection,
- provider configuration v relevantných contextoch,
- resource addresses.

Toto nefunguje bezpečne:

```hcl
resource "example_item" "child" {
  for_each = toset(example_parent.main.generated_names)
}
```

Ak `generated_names` nie sú známe pri plan-e, Terraform nevie, aké resource instances majú existovať.

Stabilné identity keys majú pochádzať z configuration inputs, nie z remote-generated values.

## 6. Conditional expression

```hcl
instance_type = var.environment == "prod" ? "large" : "small"
```

Obe vetvy musia mať kompatibilný result type.

Conditional expression je vhodná pre jednoduché value rozhodnutie. Veľké nested conditions znižujú čitateľnosť a komplikujú test matrix.

## 7. `for` expressions

Transformácia mapy:

```hcl
locals {
  subnet_cidrs = {
    for name, subnet in var.subnets :
    name => subnet.cidr
  }
}
```

Filtrovanie:

```hcl
locals {
  public_subnets = {
    for name, subnet in var.subnets :
    name => subnet
    if subnet.public
  }
}
```

Groupovanie, duplicate keys a ordering semantics treba navrhovať vedome. Sets nemajú stabilné používateľsky významné poradie.

## 8. Splat expressions

```hcl
aws_instance.worker[*].id
```

Splat je skrátenie transformácie collection objektov. Pri resources s `for_each` je často jasnejšie použiť explicitný `for`:

```hcl
[for instance in values(aws_instance.worker) : instance.id]
```

## 9. Functions

Terraform obsahuje built-in functions pre:

- strings,
- numeric operations,
- collections,
- encoding/decoding,
- filesystem a paths,
- date/time,
- cryptographic hashes,
- type conversions.

Príklad:

```hcl
name = lower(join("-", [var.project, var.environment]))
```

Funkcie nemajú byť používané na vytvorenie nečitateľnej jednej expression. Komplexnú transformáciu rozdeľ do pomenovaných locals.

## 10. String templates

Interpolation:

```hcl
name = "${var.project}-${var.environment}"
```

Template directives:

```hcl
user_data = <<-EOT
%{ for server in var.servers ~}
server=${server}
%{ endfor ~}
EOT
```

Pri generovaní JSON/YAML preferuj `jsonencode` alebo `yamlencode` pred ručným skladaním textu. Encoder správne escapuje hodnoty a zachová dátový model.

## 11. Dynamic blocks

Dynamic block generuje opakované nested blocks:

```hcl
resource "example_firewall" "main" {
  dynamic "rule" {
    for_each = var.rules

    content {
      port     = rule.value.port
      protocol = rule.value.protocol
    }
  }
}
```

Používaj ho iba tam, kde provider schema vyžaduje nested blocks. Dynamic blocks nemôžu generovať meta-arguments ako `lifecycle`.

Nadmerná dynamika robí konfiguráciu podobnú generickému programovaciemu frameworku a oslabuje čitateľnosť.

## 12. Implicitný dependency graph

Terraform analyzuje references:

```hcl
resource "aws_subnet" "app" {
  vpc_id = aws_vpc.main.id
}
```

Graph obsahuje edge:

```text
aws_vpc.main
→ aws_subnet.app
```

Pri create sa VPC vytvorí prvé. Pri destroy sa poradie obráti.

## 13. Dependency cez locals a outputs

Dependency sa nestratí, keď referencia prejde cez local:

```hcl
locals {
  vpc_id = aws_vpc.main.id
}

resource "aws_subnet" "app" {
  vpc_id = local.vpc_id
}
```

Rovnako module output prenáša dependency medzi modules.

Terraform sleduje expression provenance, nie iba textové poradie blockov v súbore.

## 14. Explicitný `depends_on`

```hcl
resource "example_service" "app" {
  depends_on = [example_policy.runtime]
}
```

Použi ho, keď dependency existuje behaviorálne, ale neexistuje value reference.

Príklady:

- policy musí byť aplikovaná pred vytvorením workloadu,
- logging service musí byť pripravený pred aktiváciou audit source,
- external side effect nie je vyjadrený argumentom.

`depends_on` má byť last resort a komentovaný.

## 15. Prečo široký `depends_on` škodí

`depends_on = [module.platform]` môže znamenať, že consumer čaká na všetky actions a reads v module.

Dôsledky:

- znížená paralelizácia,
- viac hodnôt `known after apply`,
- väčší blast radius planu,
- falošné dependencies,
- dlhší apply.

Preferuj konkrétny output contract.

## 16. Data sources a dependency graph

Data source sa môže načítať počas planu, ak sú jeho arguments známe.

Ak závisí od resource vytvoreného v rovnakom apply:

```hcl
data "example_object" "current" {
  id = example_object.managed.id
}
```

Read môže byť odložený do apply fázy a downstream hodnoty budú unknown.

Explicitný `depends_on` na data source môže tiež odložiť read a zhoršiť plan precision.

## 17. Parallel execution

Objekty bez dependency vzťahu môže Terraform spracovať paralelne.

```text
network ──→ subnet ──→ instance
storage ─────────────→ application
identity ────────────→ application
```

Parallelism skracuje apply, ale môže naraziť na:

- API rate limits,
- quotas,
- provider concurrency bugs,
- shared external locks,
- network saturation.

`-parallelism` je execution tuning, nie oprava chýbajúcej dependency.

## 18. Cycles

Cycle vznikne, keď objekt nepriamo závisí sám od seba:

```text
A → B → C → A
```

Typické príčiny:

- vzájomne referencované security groups,
- module outputs spätne použité ako inputs rovnakého graphu,
- provider configuration závislá od resource spravovaného tým providerom,
- circular locals.

Riešenie je zmeniť architecture boundary alebo rozdeliť lifecycle fázy, nie náhodne pridávať `depends_on`.

## 19. `count` identity

```hcl
resource "example_user" "member" {
  count = length(var.users)
  name  = var.users[count.index]
}
```

Pri vložení položky do stredu listu sa indexy posunú. Terraform môže plánovať zmeny viacerých instances.

`count` je vhodný pre:

- homogénny počet instances,
- optional single resource cez `0/1`,
- prípady, kde index je skutočná identita.

## 20. `for_each` identity

```hcl
resource "example_user" "member" {
  for_each = toset(var.users)
  name     = each.key
}
```

Resource addresses používajú stabilné keys:

```text
example_user.member["alice"]
```

Key zmena je identity zmena. Nepoužívaj mutable display name ako key, ak objekt má stabilnejší business identifier.

## 21. Collection ordering

Lists/tuples majú poradie. Sets nie.

Konverzia setu na list môže vytvoriť ordering, ktorý nie je business-stabilný. Ak poradie ovplyvňuje resource identity alebo priority, definuj ho explicitne.

Pri maps je key stabilnejší contract než iteration order.

## 22. `terraform console`

Console umožňuje skúšať expressions:

```bash
terraform console
```

Príklady:

```hcl
> merge({a = 1}, {b = 2})
> [for x in [1,2,3] : x * 2]
> cidrsubnet("10.0.0.0/16", 8, 3)
```

Console používa configuration a dostupný state context. Je vhodná na overenie types a transformácií pred apply.

## 23. `terraform graph`

```bash
terraform graph | dot -Tsvg > graph.svg
```

Graph môže pomôcť pri:

- cycles,
- nečakanej serializácii,
- module dependencies,
- provider edges.

Veľký graph je hlučný. Začni konkrétnym symptomom a kombinuj ho s planom a configuration references.

## 24. Plan JSON

Machine-readable plan umožňuje analyzovať:

- resource changes,
- unknown values,
- replacement actions,
- sensitive markers,
- before/after hodnoty,
- policy decisions.

Plan file a JSON môžu obsahovať citlivé údaje. Chráň ich ako secrets/evidence artifacts.

## 25. Anti-patterny

### Dependencies cez názvy súborov

Terraform nevyhodnocuje `.tf` súbory sekvenčne podľa názvu.

### `depends_on` ako univerzálna oprava

Skryje chybný contract a serializuje graph.

### Unknown values nahradené hardcoded placeholderom

Plan môže vyzerať presnejšie, ale vytvára nesprávny desired state.

### `for_each` nad computed setom

Terraform nevie zostaviť instance addresses pred apply.

### Jeden obrovský nested expression

Review a troubleshooting sú neprimerane náročné.

### `timestamp()` v managed argumente

Každý plan môže produkovať zmenu a porušiť convergence.

## 26. Troubleshooting

### `Invalid for_each argument`

Keys alebo collection nie sú známe pri plan-e. Presuň identity do input configuration alebo rozdeľ states/lifecycle.

### `Cycle` error

Zobraz graph, nájdi spätnú referenciu a rozdeľ ownership alebo fázy.

### Príliš veľa `known after apply`

Skontroluj explicitné dependencies, data source deferral, module-level `depends_on` a provider computed attributes.

### Apply je zbytočne pomalý

Over critical dependency path, široké module dependencies, provider rate limits a `parallelism`.

### Resource instances sa masovo presúvajú

Skontroluj zmenu `count` indexov alebo `for_each` keys. Použi `moved` blocks pri legitímnej identity refaktorizácii.

## 27. Kontrolné otázky

1. Čo je unknown value a ako sa líši od `null`?
2. Ktoré expressions musia byť známe pred apply?
3. Ako reference vytvára dependency edge?
4. Prečo locals nezrušia dependency?
5. Kedy použiť explicitný `depends_on`?
6. Prečo module-level `depends_on` znižuje plan precision?
7. Aký je identity rozdiel medzi `count` a `for_each`?
8. Ako vzniká dependency cycle?
9. Na čo slúži `terraform console`?
10. Prečo dynamická konfigurácia môže zhoršiť maintainability?

## Glossary impact

Relevantné pojmy: Terraform expression, reference, unknown value, graph-shaping value, implicit dependency, explicit dependency, dependency graph, dependency cycle, `for` expression, dynamic block, `count` identity, `for_each` identity, plan-time value a apply-time value.

## Oficiálna dokumentácia

- [Expressions](https://developer.hashicorp.com/terraform/language/expressions)
- [References to values](https://developer.hashicorp.com/terraform/language/expressions/references)
- [`depends_on` meta-argument](https://developer.hashicorp.com/terraform/language/meta-arguments/depends_on)
- [Meta-arguments](https://developer.hashicorp.com/terraform/language/meta-arguments)
