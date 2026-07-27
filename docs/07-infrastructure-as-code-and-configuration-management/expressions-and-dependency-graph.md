# Expressions a dependency graph

Terraform expressions nepočítajú iba hodnoty. References medzi hodnotami zároveň vytvárajú dependency edges a resource addresses. Z expressions preto vzniká execution graph, ktorý určuje identity objektov, poradie create/destroy operácií, paralelizáciu, unknown values a hranice plan-time rozhodovania.

Kapitola pokračuje v scenári Atlas Payments. Configuration `prod-eu` vytvára network, private subnets, security policies, runtime service a DNS record. Cieľom nie je zapamätať všetky expression formy, ale vedieť vysvetliť, ako input identity vytvorí graph a ako graph vedie k remote mutations.

## 1. Dominantný model

```text
configuration inputs a stable identity keys
→ expressions vypočítajú hodnoty
→ references vytvoria dependency edges
→ plan-time známy graph shape
→ scheduler vyberie ready vertices
→ provider operations vyriešia unknown values
→ state uloží instance addresses a remote bindings
→ runtime verification potvrdí outcome
```

Graph odpovedá na tri samostatné otázky:

1. **Identity:** ktoré resource/module instances existujú a aké majú addresses?
2. **Dependency:** ktorý objekt potrebuje hodnotu alebo behavior upstream objektu?
3. **Execution:** ktoré operations možno vykonať paralelne a ktoré musia čakať?

Textové poradie `.tf` súborov tieto otázky nerieši. Rozhodujú expressions, references, meta-arguments, provider configurations a state.

## 2. Atlas graph subject

Zjednodušený graph:

```text
var.subnets
    ↓
module.network
    ├──→ private subnets ──→ runtime service
    └──→ load balancer ─────→ DNS record

module.identity ─────────────→ runtime service
module.security-policy ──────→ runtime service
```

Každý vertex má Terraform address a podľa lifecycle aj remote identity. Každý edge musí mať vysvetliteľný value alebo behavior contract.

Atlas uchováva pre plan:

```text
configuration revision
+ effective input keys
+ module/provider revisions
+ state lineage/serial
+ graph-affecting unknown inventory
+ resource change addresses
```

Bez stabilných instance keys sa môže zmeniť identity graphu aj pri malej úprave input listu.

## 3. Expressions ako value provenance

Expression môže byť literal:

```hcl
replicas = 6
```

alebo odvodená hodnota:

```hcl
name = "${var.project}-${var.environment}"
```

Reference:

```hcl
module.network.private_subnet_ids
```

plní dve úlohy:

```text
poskytne hodnotu
+ vytvorí dependency provenance
```

Ak runtime service používa subnet IDs z network module outputu, Terraform vie, že ich nemôže plne naplánovať alebo aplikovať pred upstream výsledkom.

Locals a module outputs túto dependency nestrácajú. Iba ju pomenúvajú a prenášajú cez interface.

## 4. Types, collections a identity

Terraform hodnoty zahŕňajú strings, numbers, bools, lists/tuples, maps/objects, sets, `null` a unknown values.

Collection semantics ovplyvňujú graph:

- **list/tuple** — majú poradie;
- **set** — nemá business-stabilné poradie;
- **map/object** — keys poskytujú explicitnú identity;
- **null** — reprezentuje absenciu/omission podľa contractu;
- **unknown** — hodnota ešte nie je známa, ale type a dependency áno.

Konverzia setu na list alebo použitie mutable display name-u ako map key môže vytvoriť nestabilné addresses. Graph identity musí vychádzať zo stabilných configuration inputs.

## 5. Plan-time a apply-time values

Provider môže hodnotu poskytnúť až po remote create:

```text
example_service.payments.hostname
= (known after apply)
```

Unknown value nie je chyba. Terraform zachová dependency a vie, že DNS record potrebuje výsledný hostname.

Niektoré hodnoty však musia byť známe už pred apply, pretože určujú graph shape:

- `count`;
- `for_each` keys;
- module instance keys;
- provider configuration v relevantných contextoch;
- resource addresses.

Toto je problematické:

```hcl
resource "example_monitor" "service" {
  for_each = toset(example_service.payments.generated_instance_names)
}
```

Ak names vzniknú až po create, Terraform nevie pred apply určiť, koľko monitor resources existuje ani aké majú addresses.

Riešením je použiť stable desired keys z configuration alebo rozdeliť lifecycle boundary. Hardcoded placeholder iba predstiera presnosť a vytvára nesprávny desired state.

## 6. `for_each` ako identity contract

Atlas subnets používa mapu:

```hcl
resource "example_subnet" "private" {
  for_each = var.subnets

  cidr = each.value.cidr
  zone = each.value.zone
}
```

Addresses:

```text
example_subnet.private["private_a"]
example_subnet.private["private_b"]
```

Key je identity. Zmena `private_a` na `app_a` nie je iba rename stringu; môže vyzerať ako remove/create, pokiaľ sa identity migration nezachytí `moved` contractom.

`for_each` je vhodný, keď objekty majú stabilné logické alebo business identifiers.

## 7. `count` ako indexová identity

```hcl
resource "example_worker" "node" {
  count = length(var.workers)
  name  = var.workers[count.index]
}
```

Addresses:

```text
example_worker.node[0]
example_worker.node[1]
```

Ak sa vloží položka do stredu listu, indexy a tým identities sa posunú. Terraform môže meniť alebo nahrádzať viac remote objektov, hoci business intent bol „pridať jedného workera“.

`count` je primeraný pre homogénny počet instances alebo optional `0/1`, keď index skutočne predstavuje identity. Nie je vhodný pre dlhodobo pomenované objekty s nezávislým lifecycle.

## 8. Conditional a `for` expressions

Jednoduché value rozhodnutie:

```hcl
instance_size = var.environment == "prod" ? "large" : "small"
```

Transformácia mapy:

```hcl
locals {
  subnet_ids_by_key = {
    for key, subnet in example_subnet.private :
    key => subnet.id
  }
}
```

Filtrovanie môže meniť graph inventory:

```hcl
locals {
  enabled_checks = {
    for key, check in var.checks : key => check
    if check.enabled
  }
}
```

Review musí vedieť, či expression iba transformuje value alebo mení počet a identity vertices. Nested conditions a generické transforms môžu skryť deštruktívny identity change pred plan reviewerom.

## 9. String, JSON a dynamic generation

Pri generovaní structured data preferuj encoders:

```hcl
policy = jsonencode({
  Version = "2012-10-17"
  Statement = local.policy_statements
})
```

Ručné skladanie JSON/YAML môže rozbiť escaping alebo zmeniť typy.

Dynamic block je vhodný, keď provider schema vyžaduje opakované nested blocks:

```hcl
resource "example_firewall" "service" {
  dynamic "rule" {
    for_each = var.rules

    content {
      port     = rule.value.port
      protocol = rule.value.protocol
    }
  }
}
```

Dynamic blocks nemenia základnú potrebu stable keys, types a testovateľného contractu. Nadmerná dynamika mení module na neprehľadný generický framework.

## 10. Implicitný dependency edge

```hcl
resource "example_runtime" "payments" {
  subnet_ids = module.network.private_subnet_ids
}
```

Reference vytvorí edge:

```text
module.network
→ example_runtime.payments
```

Pri create upstream predchádza consumerovi. Pri destroy sa poradie podľa dependency obráti.

Value reference je najpresnejší dependency contract, pretože pomenúva, ktorú konkrétnu hodnotu consumer potrebuje.

## 11. Explicitný `depends_on`

Behaviorálna dependency niekedy nemá value edge:

```hcl
resource "example_runtime" "payments" {
  depends_on = [example_policy.runtime_authorization]
}
```

Legitímny príklad: authorization policy musí byť propagovaná pred vytvorením workloadu, hoci workload nepoužíva jej ID ako argument.

Každý explicitný edge musí vysvetliť:

```text
ktorý upstream behavior musí byť complete
→ prečo value reference neexistuje
→ aký failure nastane bez edge-u
→ ako sa completion overuje
```

`depends_on` nie je univerzálna oprava pre race. Môže skryť chýbajúci provider waiter, external reconciliation alebo zlú architecture boundary.

## 12. Prečo široký dependency edge škodí

```hcl
module "application" {
  depends_on = [module.platform]
}
```

môže spôsobiť:

- čakanie na celý upstream module;
- zníženú paralelizáciu;
- data-source reads odložené do apply;
- viac unknown values;
- širší replacement a plan blast radius;
- nejasný contract.

Preferuj konkrétny output alebo úzky behavior edge. Graph má reprezentovať skutočné causality, nie organizačné želanie „platforma musí byť hotová“.

## 13. Data-source edges a deferred reads

Data source s plne známymi arguments sa môže načítať pri plan-e. Ak argument závisí od created resource, read sa odloží:

```hcl
data "example_endpoint" "current" {
  service_id = example_runtime.payments.id
}
```

```text
runtime ID unknown
→ data read deferred to apply
→ downstream endpoint unknown
```

Široký explicitný dependency môže odložiť read aj vtedy, keď arguments už známe sú. To znižuje plan precision a môže zakryť replacement alebo policy finding.

## 14. Parallel execution a critical path

Vertices bez dependency vzťahu možno spracovať paralelne:

```text
network ─→ subnets ──────────→ runtime
identity ────────────────────→ runtime
storage ─────────────────────→ runtime
runtime ─→ load balancer ────→ DNS
```

Parallelism môže naraziť na API rate limits, quotas, shared locks alebo provider bugs. `-parallelism` je execution tuning. Nie je náhradou za chýbajúci dependency edge.

Pri pomalom apply treba nájsť critical path a observation points, nie mechanicky serializovať celý graph.

## 15. Cycles sú architecture signal

Cycle:

```text
A → B → C → A
```

Typické príčiny:

- security groups potrebujú navzájom computed IDs;
- provider configuration závisí od resource, ktorý má spravovať ten istý provider;
- module output sa vracia ako input do vlastného lifecycle;
- locals sa kruhovo referencujú.

Cycle sa rieši oddelením identity od attachmentu, rozdelením lifecycle fáz alebo zmenou ownership boundary. Pridanie ďalšieho `depends_on` cycle neodstráni.

## 16. State addresses a refactoring

Graph identity sa ukladá do state addresses. Legitímny refactor musí zachovať väzbu medzi starou a novou address:

```text
example_subnet.private[0]
→ example_subnet.private["private_a"]
```

Bez `moved` alebo riadenej state migration môže Terraform navrhnúť destroy/create. Plan reviewer musí rozlíšiť:

- skutočnú remote replacement;
- address-only refactor;
- key identity change;
- stratený state binding;
- provider-induced replacement.

## 17. Worked failure: `count` posunul production identities

Atlas spravoval firewall rules cez list a `count`. Tím vložil novú rule na začiatok listu.

```text
old rule[0] = payment-api
old rule[1] = monitoring

insert new rule at index 0
→ payment-api sa stane rule[1]
→ monitoring sa stane rule[2]
→ plan mení viac address bindings
→ provider navrhne replacement rules
```

### Príčina

Pozícia v liste bola použitá ako identity pre business-pomenované objekty.

### Náprava

Rules sa migrujú na `for_each` keyed stabilným policy ID. `moved` mappings zachovajú state identity a fixture plan overí, že pridanie jednej rule vytvorí jednu novú instance.

## 18. Worked failure: module-level `depends_on` vytvoril false uncertainty

Application module mal `depends_on = [module.platform]`. Platform module obsahoval aj unrelated audit resource, ktorého computed attribute bol známy až po apply.

```text
široký module dependency
→ application data-source read sa odloží
→ endpoint a policy inputs sú unknown
→ plan gate nevie vyhodnotiť exposure
→ reviewer vidí neúplný risk obraz
```

### Náprava

Consumer sa naviaže na konkrétny platform output. Skrytá behavior dependency dostane úzky explicitný edge a samostatný readiness oracle.

## 19. Worked failure: graph-shaping keys vznikali z remote API

Tím chcel vytvoriť monitoring checks pre dynamicky vygenerované runtime instance names:

```hcl
for_each = toset(example_runtime.payments.generated_names)
```

Plan zlyhal, pretože names boli known after apply.

### Príčina

Remote-generated values mali určovať Terraform instance addresses, ktoré musia byť známe pred apply.

### Náprava

Desired check identities sa definujú v configuration. Runtime-generated instances sa monitorujú cez service-level discovery alebo samostatný controller, nie ako graph-shaping Terraform resources.

## 20. Kauzálny diagnostický walkthrough

Symptom: pridanie jedného production consumeru spôsobí plan replacement pätnástich IAM bindings.

### Krok 1 — stabilizuj graph subject

```text
configuration       C82
state serial        S244
input consumers     before/after
resource addresses  example_binding.consumer[*]
provider lock       P8
plan                PL501
```

### Krok 2 — konkurenčné hypotézy

```text
H1: `count` indexy sa posunuli
H2: `for_each` key normalization sa zmenila
H3: set/list ordering nie je stabilný
H4: provider označil changed argument ako replacement
H5: address refactor nemá moved mapping
H6: state binding je stale alebo poškodený
H7: plan patrí inému variable setu alebo state-u
```

### Krok 3 — diskriminačné observation points

- before/after resource addresses testujú H1/H2/H5;
- input collection type a ordering testujú H3;
- plan replacement reasons a provider schema testujú H4;
- state list/show a lineage testujú H6;
- plan subject metadata testuje H7;
- Git diff ukáže, či sa zmenila iba collection alebo aj argument semantics.

Atlas zistí, že bindings používali `count` nad zoradeným listom a nový consumer bol vložený na začiatok. H1 je potvrdená.

### Krok 4 — contain-ni deštruktívny graph

Apply sa zablokuje. IAM bindings sa nemenia ručne, pretože by vznikol ďalší ownership drift.

### Krok 5 — migruj identity

Configuration prejde na `for_each` keyed immutable consumer ID. `moved` mappings zachovajú existujúce bindings a nový plan vytvorí iba jednu novú instance.

### Krok 6 — over pôvodný outcome

```text
existujúce address → rovnaké remote bindings
nový consumer → jedna create action
žiadne unexpected replacements
permissions a access journey → správne
state serial → auditovaný
```

### Krok 7 — skorší control

Finding sa mení na graph-contract test: pridanie jedného keyed inputu nesmie zmeniť addresses existujúcich instances.

## 21. Diagnostické nástroje

`terraform console` pomáha overiť type a transformáciu:

```hcl
> keys(var.subnets)
> { for key, value in var.subnets : key => value.cidr }
```

`terraform graph` môže pomôcť pri cycle alebo nečakanej serializácii:

```bash
terraform graph | dot -Tsvg > graph.svg
```

Plan JSON umožňuje analyzovať:

- addresses a actions;
- before/after values;
- unknown inventory;
- replacement reasons;
- sensitive markers;
- policy evidence.

Tieto artifacts môžu obsahovať citlivé údaje a patria do chráneného evidence lifecycle-u.

## 22. Diagnostický runbook

1. Urči configuration, effective inputs, state a provider subject.
2. Zostav affected resource/module addresses pred a po zmene.
3. Rozlíš value transformáciu od graph-shaping expression.
4. Identifikuj unknown producer a fázu, v ktorej sa hodnota vyrieši.
5. Sleduj implicitné references cez locals a outputs.
6. Audituj explicitné a module-level dependencies a ich mechanistický dôvod.
7. Pri replacement-e odlíš key/index shift, provider behavior, refactor a state drift.
8. Pri cycle rozdeľ identity, attachment alebo lifecycle boundary.
9. Pri pomalom apply nájdi critical path a external rate/lock observation points.
10. Over remote bindings a pôvodný runtime outcome po graph zmene.

## 23. Referenčné pravidlá

- Expression nesie value aj dependency provenance.
- Graph shape musí byť známy pred apply.
- Unknown nie je `null` ani wildcard.
- Stable instance keys majú pochádzať z desired configuration.
- `count` používa indexovú identity.
- `for_each` key je resource identity.
- Value reference je preferovaný dependency contract.
- `depends_on` je úzky behavior edge, nie univerzálna oprava.
- Široké edges znižujú parallelism aj plan precision.
- Cycle signalizuje architecture alebo lifecycle konflikt.
- Address refactor potrebuje moved/state migration contract.

## 24. Časté omyly

### „Terraform vykonáva súbory podľa názvu“

Textové poradie `.tf` súborov neurčuje graph.

### „Known after apply je chyba providera“

Často je prirodzeným dôsledkom remote-generated value; problém je iba pri plan-time requirements.

### „`depends_on` opraví race“

Môže iba skryť chýbajúci readiness alebo ownership contract.

### „Set je vhodný pre stabilný zoznam“

Nemá business-stabilné poradie; identity musí niesť key.

### „Pridanie jednej položky znamená jednu create action“

Nie pri indexovej identity alebo zmenenej key normalizácii.

## 25. Zhrnutie

Dôveryhodný Terraform graph lifecycle je:

```text
stable desired identity keys
→ expressions a value provenance
→ explicitný dependency graph
→ plan-time známy inventory
→ bounded parallel execution
→ resolved provider values
→ preserved state addresses
→ verified remote outcome
```

Graph troubleshooting rekonštruuje addresses, keys, unknown producers a edges. Cieľom nie je iba odstrániť error, ale zachovať remote identity a zabezpečiť, že malá zmena intentu nevytvorí nečakaný deštruktívny graph.

## Oficiálna dokumentácia

- [Expressions](https://developer.hashicorp.com/terraform/language/expressions)
- [References to values](https://developer.hashicorp.com/terraform/language/expressions/references)
- [`depends_on` meta-argument](https://developer.hashicorp.com/terraform/language/meta-arguments/depends_on)
- [Meta-arguments](https://developer.hashicorp.com/terraform/language/meta-arguments)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Variables, locals a outputs](variables-locals-outputs.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Terraform state →](terraform-state.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
