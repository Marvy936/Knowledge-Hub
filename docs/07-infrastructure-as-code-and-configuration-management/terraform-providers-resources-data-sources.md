# Terraform providers, resources a data sources

Terraform Core nevie samo spravovať cloud alebo SaaS objekty. Providers sú versionované executable pluginy, ktoré prekladajú Terraform graph na operácie konkrétneho API a späť mapujú remote objekty do state. Preto provider nie je iba syntaxická knižnica. Je to trust, behavior a object-identity boundary.

Kapitola pokračuje v scenári Atlas Payments. Root configuration `prod-eu` má spravovať primary network v `eu-central-1`, replica storage v `eu-west-1` a čítať už existujúcu DNS zone, ktorú vlastní samostatný platform state.

## 1. Dominantný model

```text
provider requirement + locked package
→ provider configuration a caller identity
→ resource/data-source address
→ plan-time read a change decision
→ provider API operation
→ remote identity
→ state binding a refreshed attributes
→ consumer dependency a runtime verification
```

Každá vrstva musí zostať identifikovateľná:

- **Requirement:** ktorý provider source a compatibility range configuration povoľuje?
- **Locked package:** ktoré konkrétne bytes a checksums sa vykonajú?
- **Configuration:** s akým accountom, regionom, endpointom a aliasom provider pracuje?
- **Address:** ktorý Terraform objekt vlastní alebo pozoruje remote objekt?
- **Operation:** aký Create/Read/Update/Delete alebo read request provider vykonal?
- **Remote identity:** ktorý cloud alebo SaaS objekt bol zasiahnutý?
- **State binding:** na ktorú resource address sa remote ID uložilo?

Ak sa pomýli alias, credentials, state alebo resource address, HCL môže byť syntakticky správny a mutation napriek tomu zasiahne nesprávny target.

## 2. Terraform Core verzus provider

Terraform Core:

```text
načíta configuration
→ vyhodnotí expressions
→ zostaví dependency graph
→ koordinuje plan a apply
→ pracuje so state
```

Provider:

```text
načíta provider configuration
→ autentizuje caller-a
→ interpretuje resource/data-source schema
→ volá remote API
→ čaká, polluje a normalizuje response
→ vracia remote identity a attributes
```

Provider definuje aj to, či zmena znamená in-place update alebo replacement, ktoré hodnoty sú computed a ako sa rieši eventual consistency. Upgrade providera preto môže zmeniť plan bez zmeny business intentu.

## 3. Requirement, selection a lock

Atlas root module deklaruje provider requirement:

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

Lifecycle dependency je:

```text
source + version constraint
→ init resolution
→ selected provider version
→ package checksums
→ .terraform.lock.hcl
→ reviewed upgrade
```

Constraint komunikuje podporovaný rozsah. Lock file identifikuje konkrétnu selected version a checksums pre root configuration. Obe vrstvy patria do change subjectu.

Mutable alebo neobmedzený provider výber môže spôsobiť, že rovnaký source commit vytvorí neskôr iný plan. Provider upgrade sa preto posudzuje ako executable supply-chain a behavior change, nie ako housekeeping.

## 4. Provider configuration a target identity

Atlas používa dve configurations rovnakého providera:

```hcl
provider "aws" {
  region = "eu-central-1"
}

provider "aws" {
  alias  = "replica"
  region = "eu-west-1"
}
```

Runtime configuration zahŕňa viac než region:

```text
provider alias
+ credentials/workload identity
+ account/subscription/project
+ region a endpoints
+ retry/polling settings
+ organization policy context
```

Credentials nemajú byť hardcoded v provider blocku. Atlas používa short-lived workload identity, ktorej claims povoľujú iba správny environment a state scope.

Pred mutation sa nezávisle overí caller account a region. Alias `replica` je scheduling aj authorization input, nie iba pohodlné meno.

## 5. Child module provider contract

Child module deklaruje requirements, ale root caller mu odovzdáva konkrétne configurations.

```hcl
module "replication" {
  source = "./modules/replication"

  providers = {
    aws.source      = aws
    aws.destination = aws.replica
  }
}
```

Module contract musí uviesť, ktoré provider aliases očakáva. Inak môže resource ticho zdediť default configuration a vytvoriť objekt v primary regione alebo pod nesprávnou identity.

Provider mapping patrí do resolved configuration identity rovnako ako module inputs.

## 6. Managed resource a identity binding

Resource reprezentuje objekt, ktorého lifecycle Terraform vlastní:

```hcl
resource "aws_vpc" "prod" {
  cidr_block = "10.40.0.0/16"
}
```

Terraform address:

```text
aws_vpc.prod
```

Remote identity:

```text
vpc-0714
```

State binding:

```text
aws_vpc.prod → vpc-0714
```

Address nie je cloud ID. Premenovanie address bez `moved` alebo adoption contractu môže vyzerať ako destroy/create. Rovnako strata state bindingu môže viesť k duplicate create, hoci remote objekt stále existuje.

Resource lifecycle cez providera je:

```text
configuration arguments
+ prior state
+ refreshed remote attributes
→ no-op | create | update | replace | destroy
→ provider operation
→ remote response
→ new state binding
```

Replacement je identity change. Môže zmeniť IP, endpoint, data-bearing volume, policy attachment alebo availability. Preto sa nesmie skrývať v súhrne „1 to change“.

## 7. Arguments, computed attributes a unknown values

Configuration poskytuje arguments. Provider vracia attributes, pričom niektoré sú computed až po remote operation.

```hcl
output "vpc_id" {
  value = aws_vpc.prod.id
}
```

Počas planu môže byť hodnota:

```text
(known after apply)
```

Unknown hodnota zachová typ a dependency, ale znižuje presnosť downstream planu. Ak ovplyvňuje graph-shaping key, provider configuration alebo policy decision, configuration boundary treba prepracovať.

## 8. Data source je read contract, nie ownership

Atlas DNS zone vlastní samostatný platform state. Application state ju iba číta:

```hcl
data "aws_route53_zone" "public" {
  name = "payments.example.com."
}
```

Data source:

- nevlastní lifecycle objektu;
- nevytvára remote resource;
- číta podľa provider query semantics;
- môže priniesť dependency a unknown hodnoty;
- môže byť mutable alebo nejednoznačný input.

Použitie data source je správne, keď external owner publikuje stabilný read contract. Nie je správne, keď query typu `most_recent = true` vyberá release-critical artifact bez digestu alebo policy. Taký výber mení resolved input bez source diffu.

## 9. Read timing a plan precision

Data source sa môže načítať pri plan-e, ak sú jeho arguments známe. Ak závisí od resource vytvoreného v rovnakom apply, read sa odloží:

```text
resource create
→ remote ID known after apply
→ data-source read deferred
→ downstream values unknown
```

Široký `depends_on` môže odložiť read aj bez skutočnej potreby. To zväčšuje množstvo unknown values a môže zmeniť policy alebo replacement visibility.

Plan precision preto závisí aj od toho, kde leží ownership a lifecycle boundary. Niekedy je správnejšie publikovať stabilný output contract z upstream state-u než znova queryovať mutable remote inventory.

## 10. Dependencies cez values

Referencia vytvára hodnotu aj graph edge:

```hcl
resource "aws_subnet" "app" {
  vpc_id = aws_vpc.prod.id
}
```

```text
aws_vpc.prod
→ aws_subnet.app
```

Preferuj value reference pred `depends_on`, pretože presne pomenúva prenášaný contract. Explicitný dependency edge je legitímny iba pri skrytej behaviorálnej závislosti, ktorú nemožno vyjadriť hodnotou.

Module-level `depends_on` môže serializovať celý subgraph a zmeniť množstvo plan-time reads na apply-time unknowns. Každý taký edge potrebuje konkrétny mechanistický dôvod.

## 11. Instance identity: `count` a `for_each`

`count` používa indexovú identity:

```text
example_worker.node[0]
example_worker.node[1]
```

`for_each` používa key:

```text
example_subnet.private["az-a"]
```

Pre dlhodobo identifikovateľné objekty je stabilný business key zvyčajne bezpečnejší než pozícia v liste. Zmena keya je však stále identity change. Display name, ktorý sa často mení, nie je dobrý key.

Instance identity ovplyvňuje state addresses, plan replacements, moved history a downstream references.

## 12. Eventual consistency a provider failure semantics

Po create môže remote API vrátiť ID skôr, než objekt vidia všetky subsystémy. Provider môže pollovať alebo retryovať, ale stále môžu nastať:

- transient 404;
- propagation delay;
- throttling;
- timeout po úspešnej mutation;
- partial create;
- inconsistent read-after-write;
- normalization drift.

Náhodný `sleep` nerieši identitu ani outcome. Preferuj provider-native waiter, explicitný readiness contract a post-apply verification.

Pri timeout-e sa najprv overí remote request a state binding. Retry bez reconciliation môže vytvoriť duplicate alebo znovu vykonať nevratný side effect.

## 13. Worked failure: alias sa nepreniesol do child module

Atlas chcel vytvoriť replica bucket v `eu-west-1`. Root module nakonfiguroval `aws.replica`, ale child module neuviedol alias contract a caller neposlal explicitný provider mapping.

```text
root pozná aws.replica
→ child resource použije default aws
→ apply identity je platná
→ bucket vznikne v eu-central-1
→ job skončí green
```

### Príčina

Configuration bola syntakticky platná a provider API uspelo. Chyba bola v effective provider mappingu, nie v cloud dostupnosti.

### Náprava

Module deklaruje požadované aliases, caller ich explicitne mapuje a plan evidence obsahuje provider configuration address, account a region pre každý citlivý resource.

## 14. Worked failure: mutable data source zmenil runtime image

Configuration používala data source `most_recent` na výber base image. Source commit, variables aj module version zostali rovnaké. O týždeň publisher pridal nový image.

```text
rovnaký source commit
→ nový plan vykoná nový data-source read
→ vyberie iné image ID
→ service replacement
→ test evidence zo starého image už neplatí
```

### Príčina

Data source bol release dependency bez immutable identity a bez resolved-input evidence.

### Náprava

Build/promotion workflow publikuje schválený image digest alebo immutable ID. Terraform dostane konkrétnu identity ako versionovaný input; discovery alias slúži iba na výber candidate-u pred approvalom.

## 15. Worked failure: provider upgrade zmenil replacement behavior

Atlas aktualizoval provider lock. Nová provider verzia zmenila normalizáciu jedného network argumentu a plan navrhol replacement load balancera.

```text
business configuration bez zmeny
→ provider executable behavior sa zmení
→ refreshed state sa normalizuje inak
→ plan ukáže replacement
```

Upgrade nebol bug automaticky. Bol to dependency change, ktorý potreboval compatibility review, fixture plan a rollout po environments.

## 16. Kauzálny diagnostický walkthrough

Symptom: replica storage po úspešnom apply existuje v primary regione, hoci configuration uvádza `eu-west-1`.

### Krok 1 — stabilizuj object subject

```text
resource address       module.replication.aws_s3_bucket.replica
state binding          bucket atlas-payments-replica
expected provider      aws.replica
expected target        atlas-prod/eu-west-1
actual target          atlas-prod/eu-central-1
provider lock          P6
apply plan             PL417
```

### Krok 2 — konkurenčné hypotézy

```text
H1: child module zdedil default provider
H2: alias mapping existuje, ale credentials smerujú do iného accountu
H3: region environment variable prepísal provider config
H4: state patrí inému backendu alebo workspace
H5: cloud UI ukazuje object s rovnakým názvom z iného subjectu
H6: provider/API ignoroval alebo normalizoval region argument
```

### Krok 3 — diskriminačné observation points

- resolved module provider mapping testuje H1;
- caller identity a account audit testujú H2;
- effective provider configuration bez secretov testuje H3;
- backend lineage, serial a resource address testujú H4;
- remote object ID, creation request a tags testujú H5;
- provider logs a schema testujú H6.

Atlas potvrdí, že child module nemal explicitný alias mapping a použil default provider. H1 vysvetľuje outcome.

### Krok 4 — contain-ni ďalšiu mutation

Promotion sa zastaví. Nesprávny bucket sa nemaže, kým sa neoverí, či obsahuje dáta alebo ho nepoužíva downstream consumer.

### Krok 5 — recovery podľa actual state

Tím vytvorí opravený plan s explicitným mappingom. Podľa data inventory zvolí bezpečný copy/create flow, aktualizuje consumers a až potom odstráni nesprávny objekt.

### Krok 6 — over outcome

```text
plan provider address = aws.replica
caller account/region = atlas-prod/eu-west-1
remote object ID = expected replica
state binding = správny
replication journey = zdravá
```

### Krok 7 — skorší control

Finding sa mení na module provider-contract test, target attestation pred apply a policy, ktorá odmietne citlivý resource bez explicitnej provider configuration identity.

## 17. Diagnostický runbook

1. Urči Core/provider version, lock digest a platform package.
2. Identifikuj provider configuration address, alias, account, region a caller identity.
3. Urči Terraform resource/data address a remote object ID.
4. Over backend, workspace, lineage, serial a provider binding v state.
5. Rozlíš managed resource, data source, imported alebo unmanaged object.
6. Pri replacement-e nájdi konkrétny argument a provider schema behavior.
7. Pri unknown value sleduj upstream computed value a deferred read.
8. Pri timeout-e over remote request outcome pred retry.
9. Pri wrong-target incidente contain-ni mutation a inventarizuj dáta/consumers.
10. Zmeň finding na lock, mapping, identity, ownership alebo read-contract control.

## 18. Referenčné pravidlá

- Provider je versionovaný executable dependency.
- Requirement, lock a runtime configuration sú odlišné vrstvy.
- Provider alias je súčasť target identity.
- Child module má explicitný provider contract.
- Resource address nie je remote ID.
- State binding určuje managed object identity.
- Data source poskytuje read contract, nie lifecycle ownership.
- Mutable discovery query nie je release identity.
- Value reference je preferovaný dependency contract.
- Provider upgrade potrebuje čerstvý plan a compatibility review.
- API success bez správneho targetu nie je úspešný outcome.

## 19. Časté omyly

### „Provider block s regionom stačí“

Account, identity, alias mapping, endpoint a backend context môžu stále smerovať inam.

### „Data source je bezpečný, lebo iba číta“

Mutable alebo nejednoznačný read môže zmeniť plan a release input.

### „Resource name je cloud identity“

Terraform address a remote ID sú odlišné identity spojené state-om.

### „Provider upgrade nemení infra intent“

Môže zmeniť defaults, normalization, read behavior aj replacement semantics.

### „Timeout znamená, že create zlyhal“

Remote mutation mohla uspieť pred stratou response.

## 20. Zhrnutie

Dôveryhodný provider/object lifecycle je:

```text
locked provider package
→ explicitná provider a target identity
→ resource alebo data-source address
→ plan-time read/change decision
→ remote API operation
→ remote object identity
→ state binding
→ verified consumer/runtime outcome
```

Troubleshooting sa nekončí otázkou, či cloud API odpovedalo. Musí dokázať, ktorý provider executable a configuration bežali, ktorý object address a remote ID boli subjectom, kam sa binding uložil a či výsledok vznikol v správnom account/region ownership contexte.

## Oficiálna dokumentácia

- [Providers](https://developer.hashicorp.com/terraform/language/providers)
- [Provider requirements](https://developer.hashicorp.com/terraform/language/providers/requirements)
- [Resources](https://developer.hashicorp.com/terraform/language/resources)
- [Data sources](https://developer.hashicorp.com/terraform/language/data-sources)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Infrastructure as Code principles](infrastructure-as-code-principles.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Variables, locals a outputs →](variables-locals-outputs.md)
<!-- KNOWLEDGE-NAVIGATION:END -->