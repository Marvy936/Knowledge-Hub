# Expressions a dependency graph

Terraform expressions nepočítajú iba hodnoty. References medzi values zároveň vytvárajú dependency edges a collection keys vytvárajú addresses jednotlivých resource alebo module instances. Z expressions preto vzniká execution graph, ktorý určuje, ktoré objekty existujú, ktoré hodnoty sú známe počas planu, ktoré operácie musia čakať a ktoré remote mutations možno vykonať paralelne.

Kapitola pokračuje incidentom `IAC-PAY-75`. Atlas Payments vytvára VPC, subnets, security policy, runtime service a DNS record. Subnets sú však definované ako list a resources používajú `count`. Tím vloží nový subnet na začiatok listu, čím posunie indexové identities. Široký module-level `depends_on` navyše odloží data-source reads do apply a policy gate nevidí konkrétny endpoint ani exposure. Plan je veľký a nepresný, hoci business intent bol pridať jediný subnet.

## 1. Dominantný value-to-operation lifecycle

Nasledujúci model opisuje prechody jedného Terraform configuration, state a remote-resource subject, nie iba poradie krokov. Failure môže nastať v ktoromkoľvek bode reťazca resolved inputs a graph cez provider API mutation až po state binding a zanechať partial alebo unknown outcome. Každý transition preto potrebuje vlastný read-back a closure tvorí exact provider target, remote/state reconciliation a druhý no-op plan.


```text
configuration inputs a collection keys
→ expressions vytvoria values
→ references vytvoria dependency provenance
→ count/for_each vytvoria instance addresses
→ unknown values obmedzia plan precision
→ graph scheduler vyberie ready operations
→ provider calls vyriešia computed values
→ state uloží addresses a remote bindings
→ runtime read-back overí outcome
```

Graph odpovedá na tri odlišné otázky:

1. **Inventory:** ktoré resource a module instances existujú?
2. **Causality:** ktoré values alebo behaviors závisia od upstream objektov?
3. **Execution:** ktoré create/update/destroy operations možno vykonať a v akom poradí?

Textové poradie `.tf` súborov nie je execution order. Terraform načíta module configuration ako celok a graph odvodí z references, meta-arguments, provider configurations, lifecycle a state.

## 2. Exact graph subject

Atlas zachováva pre každý saved plan:

```yaml
graphSubject:
  sourceRevision: 71c4f2a
  rootModule: environments/prod-eu
  state:
    lineage: 37fd...
    serial: 208
  inputKeySets:
    subnets: [az_a, az_b]
    services: [payments-api]
  providerLockDigest: sha256:4d5f...
  moduleManifestDigest: sha256:2c91...
  unknownInventory:
    - aws_lb.api.dns_name
    - aws_lb.api.zone_id
  plannedAddresses:
    - aws_vpc.main
    - aws_subnet.private["az_a"]
    - aws_subnet.private["az_b"]
    - aws_lb.api
    - aws_route53_record.api
```

Graph identity závisí od input key sets a state addresses. Rovnaký počet resources nepreukazuje rovnakú identity. Zmena `az_a` na `private_a` môže byť address migration, aj keď CIDR ostane rovnaký.

## 3. Expressions ako value a dependency provenance

Literal:

```hcl
replicas = 6
```

Derived expression:

```hcl
name = "${var.application}-${var.environment}"
```

Reference:

```hcl
subnet_ids = module.network.private_subnet_ids
```

Reference plní dve úlohy:

```text
prenáša value
+ vytvára graph edge
```

Ak runtime service potrebuje subnet IDs z network modulu, Terraform vie, že consumer nemôže byť kompletne naplánovaný alebo vytvorený skôr než upstream values existujú. Locals a outputs túto dependency nestrácajú; iba ju pomenúvajú a vedú cez module interface.

## 4. Types a collection semantics

Collection type ovplyvňuje identity a determinism:

```text
list/tuple
→ poradie je súčasť values

set
→ unikátne values bez stabilného business poradia

map/object
→ explicitné keys môžu tvoriť management identity

null
→ omission alebo absence podľa contextu

unknown
→ type a dependency sú známe, konkrétna hodnota nie
```

Konverzia setu na list a následné používanie indexu môže vytvoriť nestabilné ordering. Terraform nemusí zachovať business poradie, ktoré caller implicitne očakáva.

## 5. Unknown values a hranica plan-time rozhodovania

Unknown value znamená, že Terraform pozná type a dependency edge, ale konkrétnu hodnotu poskytne provider až počas apply. Taká hodnota môže bezpečne napĺňať argument existujúceho graph vertexu, napríklad DNS target vytvoreného load balancera.

Graph shape však musí byť známy pred remote mutation. `count`, `for_each` keys, module instance keys, provider configuration selection a resource addresses určujú, aké vertices Terraform plánuje a ktoré state identities vzniknú. Apply-time unknown value preto nesmie byť zdrojom ich identity.

```hcl
resource "example_monitor" "instance" {
  for_each = toset(aws_service.payments.generated_instance_names)
  name     = each.key
}
```

Ak names vzniknú až po create, Terraform nevie zostaviť complete inventory ani addresses monitorov. Riešením sú desired stable keys z configuration alebo samostatný discovery/controller lifecycle. Placeholder alebo `-target` graph deterministickým neurobí.

Provider môže hodnotu poskytnúť až po remote create:

```hcl
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

Počas planu môže byť `aws_lb.api.dns_name` unknown. Terraform však pozná type, consumer a dependency edge.

Niektoré values musia byť známe pred apply, pretože určujú graph shape:


Terraform transition sleduje `count`, `for_each` keys, module instance keys, provider configuration selection a resource addresses.

Každý prvok sa viaže na rovnakú configuration, state a provider generation, aby sa vylúčil wrong-target alebo lost-binding outcome.


Toto je problematické:

```hcl
resource "example_monitor" "instance" {
  for_each = toset(aws_service.payments.generated_instance_names)
  name     = each.key
}
```

Ak names vzniknú až po create, Terraform nevie pred apply určiť inventory ani addresses monitorov. Riešením je použiť desired keys z configuration alebo monitorovať dynamické instances cez service discovery/controller, nie hardcoded placeholderom predstierať známy graph.

## 6. `for_each` ako identity contract

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.


```hcl
variable "subnets" {
  type = map(object({
    cidr = string
    zone = string
  }))
}

resource "aws_subnet" "private" {
  for_each = var.subnets

  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value.cidr
  availability_zone = each.value.zone
}
```

Addresses:

```text
aws_subnet.private["az_a"]
aws_subnet.private["az_b"]
```

Key je identity. Zmena keya môže navrhnúť destroy/create, pokiaľ sa address transition nezachytí `moved` blockom. Key preto musí byť stabilný logical identifier, nie mutable display name, generated timestamp alebo apply-time provider value.

## 7. `count` a indexová identity

```hcl
resource "aws_subnet" "private" {
  count = length(var.subnets)

  cidr_block        = var.subnets[count.index].cidr
  availability_zone = var.subnets[count.index].zone
}
```

Addresses:

```text
aws_subnet.private[0]
aws_subnet.private[1]
```

Keď tím vloží položku na index `0`, existujúce values sa posunú. Terraform môže aktualizovať alebo nahradiť viac remote objektov, hoci business intent bol pridať jeden nový.

`count` je primeraný pre homogénny počet alebo optional `0/1`, keď index skutočne predstavuje identity. Nie je vhodný pre dlhodobo pomenované resources s nezávislým lifecycle.

## 8. Transformácie a filtrovanie graph inventory

```hcl
locals {
  production_subnets = {
    for key, subnet in var.subnets :
    key => subnet
    if subnet.enabled && subnet.environment == "prod-eu"
  }
}
```

Taký `for` expression nemení iba values. Mení key set a tým počet a identity graph vertices.

Reviewer musí vedieť rozlíšiť:

```text
value-only transform
→ zmení argument existujúceho objectu

identity transform
→ pridá, odstráni alebo premenuje object address
```

Nested conditions môžu skryť deštruktívny identity change. Preto sa effective key sets ukladajú do input/plan evidence.

## 9. Conditional expressions a `null`

```hcl
resource "aws_lb" "api" {
  internal = var.environment == "prod-eu" ? true : false
}
```

Conditional branches musia mať kompatibilný type. Pri optional argumente sa často používa `null`:

```hcl
idle_timeout = var.custom_idle_timeout_enabled ? var.idle_timeout : null
```

`null` môže znamenať omission a provider default. Review musí vedieť, či výsledkom bude explicitná hodnota alebo delegovaný provider behavior.

Conditional použitý v `for_each` alebo `count` mení inventory:

```hcl
for_each = var.enable_public_endpoint ? { public = true } : {}
```

To je lifecycle decision a patrí do risk modelu, nie iba do value formattingu.

## 10. Structured generation cez `jsonencode` a `yamlencode`

Ručné skladanie JSON-u môže rozbiť escaping a typy. Preferovaný model:

```hcl
resource "aws_iam_policy" "runtime" {
  name = "atlas-payments-runtime"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = var.secret_arns
      }
    ]
  })
}
```

`jsonencode` preukazuje syntakticky správnu serializáciu Terraform value-u do JSON bytes. Nepreukazuje least privilege ani effective IAM behavior. Policy JSON potrebuje semantic policy test a cloud-side simulation/read-back podľa rizika.

## 11. Dynamic blocks a schema-driven repetition

```hcl
resource "aws_security_group" "api" {
  name   = "atlas-payments-api"
  vpc_id = aws_vpc.main.id

  dynamic "ingress" {
    for_each = var.ingress_rules

    content {
      protocol    = ingress.value.protocol
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      cidr_blocks = ingress.value.cidrs
    }
  }
}
```

Dynamic block je užitočný, keď provider schema vyžaduje opakované nested blocks. Nevytvára samostatné Terraform resource addresses pre jednotlivé rules; ich lifecycle môže byť viazaný na parent resource schema.

Ak každá rule potrebuje samostatný ownership, audit alebo lifecycle, samostatný resource type môže byť vhodnejší než jeden veľký dynamic block.

## 12. Implicitný dependency edge

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.


```hcl
resource "aws_ecs_service" "payments" {
  network_configuration {
    subnets         = values(aws_subnet.private)[*].id
    security_groups = [aws_security_group.api.id]
  }
}
```

References vytvoria edges:

```text
aws_subnet.private[*] ─┐
                       ├→ aws_ecs_service.payments
aws_security_group.api ┘
```

Value reference je najpresnejší dependency contract, pretože pomenúva, ktorú hodnotu consumer potrebuje.

## 13. Explicitný `depends_on`

Behaviorálna dependency niekedy nemá value edge:

```hcl
resource "aws_ecs_service" "payments" {
  depends_on = [aws_iam_role_policy_attachment.runtime]

  # ...
}
```

Legitímny dôvod môže byť, že role policy attachment musí existovať a byť propagovaný pred štartom tasks, hoci service nepoužíva attachment ID ako argument.

Každý explicitný edge potrebuje komentár alebo design explanation:

```text
ktorý upstream behavior musí byť complete
→ prečo value reference neexistuje
→ aký failure vznikne bez edge-u
→ ako sa completion overí
```

`depends_on` nie je univerzálny fix race condition. Môže skrývať chýbajúci provider waiter, external controller alebo zlú ownership boundary.

## 14. Prečo module-wide dependency znižuje plan precision

`depends_on = [module.platform]` vytvorí edge na celý expanded upstream module, hoci consumer často potrebuje iba jeden subnet output alebo jednu readiness capability. Terraform potom musí konzervatívne čakať na všetky upstream resources, čo znižuje paralelizáciu a môže odložiť data-source reads.

Široký edge zároveň vytvorí viac unknown values a zväčší apparent plan blast radius. Reviewer vidí uncertainty aj pri resources, ktoré s reálnym contractom nesúvisia, a konkrétna chýbajúca dependency zostane skrytá.

Preferovaný model prenáša narrow output, napríklad `subnet_ids = module.platform.private_subnet_ids`, čím vznikne value aj dependency contract. Ak existuje behaviorálna dependency bez value-u, musí pomenovať konkrétny completion condition, failure bez edge-u a independent verifier; module-wide edge je posledná, nie prvá možnosť.

```hcl
module "application" {
  source = "./modules/application"

  depends_on = [module.platform]
}
```


Terraform transition sleduje čakať na celý upstream module, znížiť paralelizáciu, odložiť data-source reads, vytvoriť viac unknown values, rozšíriť plan blast radius a skryť konkrétny contract.

Každý prvok sa viaže na rovnakú configuration, state a provider generation, aby sa vylúčil wrong-target alebo lost-binding outcome.


Preferuj konkrétny output:

```hcl
module "application" {
  source = "./modules/application"

  subnet_ids = module.platform.private_subnet_ids
}
```

Ak zostáva skrytá behavior dependency, má byť úzka a vysvetlená.

## 15. Vizualizácia graphu

Terraform CLI môže vytvoriť DOT representation:

```bash
terraform graph -type=plan > graph.dot
dot -Tsvg graph.dot -o graph.svg
```

Graph pomáha pri cycles a broad dependencies. Preukazuje Terraform dependency model pre aktuálnu configuration/plan context. Nepreukazuje remote API interné dependencies, eventual consistency ani runtime service causality.

Pri veľmi veľkom graph-e je užitočné filtrovať konkrétne addresses a kombinovať graph s plan JSON, nie vizuálne interpretovať tisíce edges bez subjectu.

## 16. Parallelism a critical path

Vertices bez edge-u možno vykonať paralelne:

```text
network ─→ subnets ───────────→ runtime
identity ─────────────────────→ runtime
storage ──────────────────────→ runtime
runtime ─→ load balancer ─────→ DNS
```

`-parallelism` je execution tuning. Neopravuje chýbajúce dependencies. Príliš vysoká parallelism môže zvýšiť API throttling; príliš nízka predĺži apply a lock duration.

Diagnostika pomalého apply sleduje:

```text
critical graph path
provider polling/waiters
API quotas a throttling
broad depends_on edges
state lock wait
runner capacity
```

## 17. Cycles ako architecture signal

Cycle `A → B → C → A` znamená, že graph nemá počiatočný vertex s dostatočne známymi inputs. Typicky provider configuration závisí od resource spravovaného tým istým providerom, dve security objects potrebujú navzájom computed IDs, module output sa vracia do vlastného lifecycle-u alebo locals vytvoria kruhový value chain.

Cycle sa neopravuje ďalším `depends_on`; ten pridáva edge a problém môže iba spraviť explicitnejším. Architecture musí oddeliť identity creation od attachments, rozdeliť bootstrap a steady-state lifecycle alebo zmeniť ownership/state boundary.

Acceptance po refaktore overí, že prvá fáza publikuje stabilný narrow contract a druhá ho spotrebuje bez reverse dependency. Druhý no-op plan dokazuje, že rozdelenie nevytvorilo oscilujúce transitions.

Cycle:

```text
A → B → C → A
```


Terraform transition sleduje provider configuration závisí od resource spravovaného tým istým providerom, dve security objects potrebujú vzájomne computed IDs, module output sa vracia ako input do vlastného lifecycle a locals sa kruhovo referencujú.

Každý prvok sa viaže na rovnakú configuration, state a provider generation, aby sa vylúčil wrong-target alebo lost-binding outcome.


Riešením je oddeliť identity creation od attachments, rozdeliť lifecycle fázy alebo zmeniť ownership boundary. Ďalší `depends_on` cycle neodstráni.

## 18. Worked incident: vloženie list itemu presunulo identities

Pôvodný input:

```hcl
subnets = [
  { name = "payments-a", cidr = "10.40.10.0/24" },
  { name = "payments-b", cidr = "10.40.20.0/24" }
]
```

Tím vložil nový management subnet na začiatok:

```hcl
subnets = [
  { name = "management", cidr = "10.40.5.0/24" },
  { name = "payments-a", cidr = "10.40.10.0/24" },
  { name = "payments-b", cidr = "10.40.20.0/24" }
]
```

Pri `count` sa indexy posunuli:

```text
old [0] payments-a → new [0] management
old [1] payments-b → new [1] payments-a
new [2] payments-b
```

Plan navrhol updates/replacements viacerých subnets. Root cause bol index použitý ako identity.

Recovery migruje input na mapu keyed stabilnými IDs a použije `moved` mappings v ďalšej kapitole. Fixture test overí, že pridanie management subnetu vytvorí presne jednu novú instance.

## 19. Worked incident: broad dependency skryl policy risk

Application module závisel od celého platform modulu. Unrelated audit resource mal computed value known after apply. Data source pre public endpoint sa preto odložil a plan policy nevedela vyhodnotiť exposure.

```text
module-wide depends_on
→ data read deferred
→ endpoint unknown
→ policy input incomplete
→ wrapper interpretuje missing field ako safe
```

Root cause bol dvojitý: broad graph edge a fail-open policy semantics. Náprava zúžila dependency na konkrétny output a policy začala rozlišovať unknown/missing od compliant.

## 20. Competing hypotheses pri veľkom replacement plane

Symptom: pridanie jedného consumeru navrhne replacement pätnástich IAM bindings.

```text
H1: count indexy sa posunuli
H2: for_each keys sa zmenili
H3: provider upgrade zmenil replacement behavior
H4: state addresses boli refactorované bez moved mappings
H5: broad dependency iba vytvorila unknown diff noise
H6: čítame nesprávny state serial
```

Dôkazy:

```bash
terraform state list | sort > state-addresses.txt
terraform show -json tfplan > tfplan.json
jq -r '.resource_changes[] | [.address, (.change.actions|join(","))] | @tsv' tfplan.json
terraform graph -type=plan > graph.dot
```

Address diff testuje H1/H2/H4, replacement reasons a provider lock H3, unknown inventory/graph edges H5 a lineage/serial H6.

## 21. Acceptance a forbidden paths

Graph acceptance overuje stable identity aj dependency precision. Positive fixture vytvorí očakávané keys a order, forbidden fixture vloží alebo premenuje list item a musí odhaliť neplánovaný address transition. Broad module dependency a cycle sa nesmú maskovať `-target` alebo nízkou parallelism.

Graph kapitola je prijatá, keď:

```text
instance keys sú známe a stabilné pred apply
+ references vyjadrujú konkrétne value dependencies
+ explicitné depends_on majú mechanistický dôvod
+ broad module barriers nie sú použité bez potreby
+ unknown fields sú v policy klasifikované ako incomplete
+ plan addresses zodpovedajú intended inventory
+ pridanie jedného subnetu vytvorí jednu instance
+ rename key bez moved mappingu je testom odmietnutý
+ second plan je no-op
```

## 22. Kontrolné otázky

1. Prečo textové poradie `.tf` súborov neurčuje execution order?
2. Aký rozdiel je medzi graph inventory, dependency a execution otázkou?
3. Prečo unknown value nie je chyba automaticky?
4. Ktoré hodnoty musia byť známe pred apply?
5. Prečo `for_each` key tvorí management identity?
6. Kedy je `count` vhodný a kedy nebezpečný?
7. Ako filtering expression mení graph inventory?
8. Čo `jsonencode` preukazuje a čo nepreukazuje?
9. Kedy je explicitný `depends_on` legitímny?
10. Prečo module-wide dependency znižuje plan precision?
11. Čo preukazuje `terraform graph` a čo nepreukazuje?
12. Ako sa testuje forbidden unstable-key path?

## Glossary impact

Relevantné pojmy: Terraform expression, reference, dependency edge, graph vertex, graph shape, unknown value, plan-time value, apply-time value, `for_each`, `count`, instance key, dynamic block, implicit dependency, explicit dependency, `depends_on`, critical path, cycle a address migration.

## Primárne zdroje

- [Terraform expressions](https://developer.hashicorp.com/terraform/language/expressions)
- [References to values](https://developer.hashicorp.com/terraform/language/expressions/references)
- [Terraform meta-arguments](https://developer.hashicorp.com/terraform/language/meta-arguments)
- [Terraform types and values](https://developer.hashicorp.com/terraform/language/expressions/types)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Variables, locals a outputs](variables-locals-outputs.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Terraform state →](terraform-state.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
