# Modules

Terraform module je versionovaná capability a provider–consumer contract. Root module skladá environment-specific systém, vyberá backend a provider configurations a vlastní plan/apply lifecycle. Child module poskytuje reusable implementation cez inputs, outputs, provider requirements, resource identity a migration semantics. Module nie je automaticky samostatný deployment, lock ani state boundary; jeho resources sa rozvinú do graphu a state-u caller root module-u.

Kapitola pokračuje incidentom `IAC-PAY-76`. Atlas Payments publikuje interný module `service-platform`. Consumer ho pinne na verziu, no wrapper module neforwardne replica provider alias a release presunie stateful load balancer do nested modulu bez retained `moved` chainu. Upgrade preto zároveň mieri do nesprávneho regionu a plánuje remote replacement objektu, ktorý sa mal iba adresovo refaktorovať.

## 1. Dominantný module-consumer lifecycle

Nasledujúci model opisuje prechody jedného Terraform configuration, state a remote-resource subject, nie iba poradie krokov. Failure môže nastať v ktoromkoľvek bode reťazca resolved inputs a graph cez provider API mutation až po state binding a zanechať partial alebo unknown outcome. Každý transition preto potrebuje vlastný read-back a closure tvorí exact provider target, remote/state reconciliation a druhý no-op plan.

```text
consumer capability intent
→ immutable module source a release identity
→ typed inputs, defaults a validations
→ caller-owned provider mappings
→ expanded resource/module graph
→ stable addresses a state bindings
→ narrow outputs a runtime capability
→ upgrade/moved compatibility
→ consumer inventory, support a retirement
```

Dobrý module znižuje počet nebezpečných rozhodnutí, ktoré musí robiť každý caller, a zároveň neschováva risk-significant behavior. Nie je to iba wrapper, ktorý premenuje provider arguments.

## 2. Root module verzus child module

Root module je deployment a state owner. Vyberá backend/state subject, environment composition, provider configurations a credentials, top-level inputs, apply identity, queue, recovery a acceptance lifecycle. Jeho repository a pipeline preto určujú, nad akým remote subjectom sa reusable code vykoná.

Child module poskytuje versionovanú capability cez inputs, outputs, required providers, resources a migration semantics. Caller ho instancuje `module` blockom a jeho resources sa rozvinú do caller graphu a state-u, napríklad `module.payments_service.aws_lb.api`.

Child module teda automaticky nedostáva vlastný lock, permissions ani blast-radius isolation. Samostatná state boundary vzniká iba samostatným root module-om, backendom a execution lifecycle-om. Module boundary rieši code/interface coupling; root/state boundary rieši ownership a failure domain.

Transition eviduje backend a state subject, environment composition, provider configurations a credentials, top-level inputs a policy, plan/apply identity a queue a recovery a acceptance lifecycle.

Child module je volaný cez `module` block:

```hcl
module "payments_service" {
  source  = "app.terraform.io/atlas/service-platform/aws"
  version = "3.4.2"

  environment  = "prod-eu"
  image_digest = "sha256:8f7c..."
  replicas     = 6

  providers = {
    aws = aws.production
  }
}
```

State addresses sa rozvinú napríklad takto:

```text
module.payments_service.aws_lb.api
module.payments_service.aws_iam_role.runtime
module.payments_service.aws_ecs_service.api
```

Child module teda nezískava vlastný lock ani izolovaný blast radius. Samostatný state vzniká až samostatným root module a backend lifecycle-om.

## 3. Module source je executable dependency

Module source môže byť local path, registry alebo VCS reference. Dôveryhodný subject obsahuje:

```yaml
moduleDependency:
  source: app.terraform.io/atlas/service-platform/aws
  version: 3.4.2
  packageDigest: sha256:31bd...
  publisher: atlas-platform
  releaseCommit: 2ac9...
  compatibilityFrom:
    - 3.3.0
    - 3.4.0
```

Mutable source:

```hcl
module "service" {
  source = "git::ssh://git.example/atlas/service-platform.git?ref=main"
}
```

znamená, že rovnaký consumer commit môže pri neskoršom `terraform init` stiahnuť iný code. Source diff v consumer repository potom nie je kompletný dependency diff.

Upgrade sa vykonáva vedome:

```bash
terraform init -upgrade
terraform providers
terraform plan -out=module-upgrade.tfplan
terraform show -json module-upgrade.tfplan > module-upgrade.json
```

`init -upgrade` resolve-ne nové allowed module/provider selections. Nepreukazuje compatibility. Plan a upgrade tests musia overiť addresses, defaults, replacements, permissions a runtime behavior.

## 4. Public contract modulu

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

Module contract obsahuje viac než variable/output tabuľku:

```text
purpose a non-goals
typed inputs a null/default semantics
validations a invariants
required providers a aliases
stable instance identity model
managed resources a side effects
permissions a exposure assumptions
outputs a sensitivity
replacement/destruction behavior
upgrade a migration policy
supported Terraform/provider versions
owner, support a retirement
```

Generated reference dokumentácia je užitočná, ale neodpovedá na otázku, akú capability module garantuje a ktoré risk decisions vykonáva za caller-a.

## 5. Domain intent namiesto provider passthrough

Slabý wrapper:

```hcl
variable "lb_internal" { type = bool }
variable "lb_idle_timeout" { type = number }
variable "lb_security_groups" { type = list(string) }
variable "lb_subnets" { type = list(string) }
```

iba presúva provider schema o jednu vrstvu vyššie.

Silnejší capability contract:

```hcl
variable "service" {
  type = object({
    name        = string
    environment = string
    exposure    = optional(string, "internal")
    replicas    = number
  })

  validation {
    condition = (
      var.service.environment != "prod-eu" ||
      (var.service.exposure == "internal" && var.service.replicas >= 2)
    )
    error_message = "Production service must be internal and have at least two replicas."
  }
}
```

Module preloží business intent na implementáciu a chráni invariant. Risk-significant choices ako public exposure, data destruction alebo privileged identity však nesmie skryť za prekvapivým defaultom.

## 6. Caller vlastní provider target

Reusable module deklaruje provider requirements a aliases, ale root caller typicky vlastní account, region a credentials.

Child module:

```hcl
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      configuration_aliases = [
        aws.primary,
        aws.replica
      ]
    }
  }
}
```

Caller:

```hcl
module "database" {
  source  = "./modules/database"
  version = "2.3.1"

  providers = {
    aws.primary = aws.production
    aws.replica = aws.replica
  }
}
```

Provider mapping patrí do execution subjectu. Hidden provider configuration v child module môže zasiahnuť nesprávny target a sťažuje least privilege.

## 7. Narrow outputs ako capability API

Slabý output:

```hcl
output "load_balancer" {
  value = aws_lb.api
}
```

vystaví provider internals.

Silnejší contract:

```hcl
output "endpoint" {
  value       = "https://${aws_lb.api.dns_name}"
  description = "HTTPS service endpoint."
}

output "runtime_role_arn" {
  value       = aws_iam_role.runtime.arn
  description = "Role assumed by the runtime workload."
}
```

Output contract definuje typ, význam, sensitivity, availability phase a compatibility. Caller sa nemá viazať na undocumented computed field provider objectu.

## 8. Module composition a dependencies

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

```hcl
module "network" {
  source  = "app.terraform.io/atlas/network/aws"
  version = "4.2.0"
}

module "service" {
  source  = "app.terraform.io/atlas/service-platform/aws"
  version = "3.4.2"

  subnet_ids = module.network.private_subnet_ids
}
```

Output reference prenáša value aj dependency edge. Toto je presnejšie než:

```hcl
module "service" {
  depends_on = [module.network]
  # ...
}
```

Module-wide `depends_on` môže vytvoriť false uncertainty a odložiť reads unrelated resources. Contract má publikovať konkrétnu hodnotu alebo readiness capability, ktorú consumer potrebuje.

## 9. Module boundary podľa capability a coupling-u

Primeraný module reprezentuje jednu koherentnú capability so známym ownerom, spoločným lifecycle-om a release cadence. Jeho public contract má stabilné inputs/outputs, zvládnuteľný state space a jasnú policy alebo abstraction hodnotu.

Mega-module pre celý account mieša nezávislé security domains a vytvára široký upgrade blast radius. Extrémne tenký wrapper iba premenúva provider arguments a zvyšuje nesting bez stabilizácie behavioru. Počet `.tf` files preto nie je boundary criterion.

Boundary sa vyberá podľa change coupling-u, ownershipu, failure/recovery jednotky a support lifecycle-u. Consumer musí vedieť capability otestovať a upgradovať bez neúmyselného prebratia unrelated resources.

Contract eviduje jednu koherentnú capability, jasného ownera, spoločný lifecycle a release cadence, testovateľný state space, stabilný public contract a zmysluplnú policy/abstraction hodnotu.

Mega-module pre celý cloud account vytvára desiatky modes a široký upgrade blast radius. Extrémne tenký wrapper zvyšuje nesting bez pridanej stability.

Boundary sa nevyberá podľa počtu `.tf` files. Vyberá sa podľa ownershipu, behavioru, change coupling-u a support lifecycle-u.

## 10. Module instance identity

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

```hcl
module "service" {
  for_each = var.services
  source   = "./modules/service"

  name = each.key
}
```

Addresses:

```text
module.service["payments"]
module.service["orders"]
```

Key je state identity. Premenovanie `payments` na `payments-api` môže vyzerať ako odstránenie jednej module instance a vytvorenie druhej. Použi stable identifier a versionovaný `moved` contract.

## 11. Versioning ako compatibility promise

Module version je promise o caller contracte a existing-state transitione. Nový optional input s bezpečným defaultom, nový output alebo interný refactor s úplným `moved` chainom môžu byť kompatibilné, ak nemenia effective identity, exposure ani behavior existujúcich callerov.

Zmena default/null semantics, provider requirements, instance keys alebo resource addresses je risk-significant. Rovnako breaking môže byť nový replacement/destroy behavior alebo privilege/exposure expansion, aj keď HCL caller zostane syntakticky platný.

Semantic version label je deklarácia, nie dôkaz. Dôveryhodný release publikuje compatibility matrix a consumer upgrade test nad reprezentatívnym state-om. Plan musí vysvetliť migrations a runtime canary musí potvrdiť capability; druhý no-op plan uzatvára stabilitu successor verzie.

Compatibility review sleduje nový optional input s bezpečným defaultom, nový output, interný refactor s úplným moved chainom a bug fix bez zmeny identity a behavior contractu.

Každá zmena sa posudzuje nad existujúcim consumer state-om, pretože syntakticky platný upgrade môže meniť identity alebo behavior.

Compatibility review sleduje zmena default/null semantics, odstránenie alebo premenovanie inputu/outputu, zmena provider requirementu, zmena instance keys, resource address refactor bez migration a nový replacement alebo destroy behavior.

Dopĺňa ho privilege/exposure expansion.

Každá zmena sa posudzuje nad existujúcim consumer state-om, pretože syntakticky platný upgrade môže meniť identity alebo behavior.

Semantic version label nie je dôkaz compatibility. Autoritatívny je consumer upgrade plan a test.

## 12. Worked incident: mutable source zmenil exposure

Consumer používal VCS `ref=main`. Module owner zmenil default z `internal` na `public`. Nový CI runner bez cache načítal nový source:

```text
rovnaký consumer commit
→ iný module content
→ load balancer scheme public
→ production plan otvorí internet exposure
```

Recovery pinla immutable release, zablokovala apply, overila remote exposure a pridala policy, ktorá odmietne public load balancer bez explicitného approved intentu.

## 13. Worked incident: default znížil production capacity

Module `3.5.0` zaviedol:

```hcl
replicas = optional(number, 2)
```

Starší caller field neposielal, pretože predchádzajúci module odvodzoval production minimum 6.

```text
upgrade 3.4.2 → 3.5.0
→ caller ostáva syntakticky validný
→ effective replicas = 2
→ service technically healthy
→ capacity objective porušený
```

Default je súčasť public behavior contractu. Upgrade tests musia používať existujúce caller fixtures a overiť effective values aj runtime capacity.

## 14. Worked incident `IAC-PAY-76`: wrapper stratil provider alias

Root mal primary a replica providers. Nový wrapper module neforwardol alias do nested database modulu:

```text
root intent = replica eu-west-1
→ wrapper používa default aws.production
→ nested replica vznikne v eu-central-1
→ state addresses vyzerajú legitímne
→ remote target je nesprávny
```

Module composition test musí overovať effective provider configuration a remote target, nie iba resource inventory.

## 15. Upgrade lifecycle

Nasledujúci model opisuje prechody jedného Terraform configuration, state a remote-resource subject, nie iba poradie krokov. Failure môže nastať v ktoromkoľvek bode reťazca resolved inputs a graph cez provider API mutation až po state binding a zanechať partial alebo unknown outcome. Každý transition preto potrebuje vlastný read-back a closure tvorí exact provider target, remote/state reconciliation a druhý no-op plan.

```text
consumer inventory a current version
→ immutable candidate release
→ release notes a migration contract
→ init/lock update
→ static a contract tests
→ plan nad reprezentatívnym existing state-om
→ address/default/provider/permission diff
→ staged apply
→ runtime verification
→ second no-op plan
→ consumer status a support closure
```

Compatibility review sleduje moves, replacements a destroys, provider target changes, effective default changes, IAM/network exposure a output schema changes.

Každá zmena sa posudzuje nad existujúcim consumer state-om, pretože syntakticky platný upgrade môže meniť identity alebo behavior.

## 16. Retained moved history pre neskorých consumers

Consumers neupgradujú naraz. Niekto môže preskočiť z `2.8.0` na `3.5.1`. Ak owner odstráni intermediate moved blocks, latest-to-latest test prejde, ale starší consumer uvidí destroy/create.

Support policy definuje:

```text
minimum supported source version
retained moved/deprecation chain
supported Terraform/provider matrix
tested upgrade paths
breaking boundary a deadline
```

## 17. Module testing portfolio

Každá testovacia alebo policy vrstva má vlastný subject a oracle. Parser/schema pass nepreukazuje remote authorization, report existence nepreukazuje processing a isolated apply nepreukazuje production runtime. Gate preto odlišuje violation, missing/invalid evidence, tool failure a stale subject.

```text
fmt/validate
→ input validation fixtures
→ plan assertions pre supported modes
→ provider-alias tests
→ policy/security checks
→ apply/integration behavior
→ runtime capability verification
→ upgrade tests z supported versions
→ cleanup a recovery
```

Examples sú executable documentation iba vtedy, keď ich CI pravidelne plánuje alebo aplikuje v izolovanom targete.

Príklad native testu:

```hcl
run "production_contract" {
  command = plan

  variables {
    service = {
      name        = "payments"
      environment = "prod-eu"
      exposure    = "internal"
      replicas    = 6
    }
  }

  assert {
    condition     = output.endpoint != null
    error_message = "Module must publish an endpoint contract."
  }
}
```

Plan assertion preukazuje Terraform evaluation result. Nepreukazuje remote API behavior ani live endpoint.

## 18. Consumer inventory

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

Transition eviduje consumer repository/root module, current module version, environment a owner, Terraform/provider versions, deprecated/vulnerable status a supported upgrade path.

Dopĺňa ho posledný successful test/plan.

Bez inventory nemožno bezpečne odstrániť moved history alebo koordinovať security release.

## 19. Competing hypotheses pri nečakanom replacement plane

Symptom: upgrade `3.4.2 → 3.5.0` plánuje replacement load balancera a IAM role.

```text
H1: internal addresses sa zmenili bez moved blocks
H2: module instance key sa zmenil
H3: new default zmenil replace-sensitive argument
H4: provider upgrade zmenil replacement behavior
H5: provider alias mieri na iný target
H6: source artifact nezodpovedá version labelu
H7: state binding history je stará alebo poškodená
```

Dôkazy:

```bash
terraform show -json module-upgrade.tfplan > module-upgrade.json
jq -r '.resource_changes[] | [.address, (.change.actions|join(","))] | @tsv' module-upgrade.json
terraform providers
terraform state list | sort
```

Address diff testuje H1/H2, effective values H3, provider lock/reasons H4, provider mapping H5, package digest H6 a state history H7.

## 20. Authoritative recovery

Atlas zistil, že `aws_lb.api` sa presunul do `module.edge.aws_lb.api` bez moved blocku.

Recovery:

```text
zablokovať upgrade apply
→ publikovať module 3.5.1 s retained moved mappingom
→ planovať 3.4.2 → 3.5.1 nad real fixture state-om
→ potvrdiť move bez replacementu
→ apply v stage
→ overiť rovnaký remote LB ID a endpoint
→ production rollout
→ second no-op plan
```

Manuálny `state mv` v jednom environment-e by neopravil reusable contract pre ostatných consumers.

## 21. Acceptance a forbidden paths

Acceptance uzatvára celý Terraform configuration, state a remote-resource subject, nie iba posledný command. Positive path dokazuje požadovanú capability, forbidden path zachovanie ownership alebo security hranice a recovery/second-operation path stabilitu successor generation. Spoločným oracle-om je exact provider target, remote/state reconciliation a druhý no-op plan.

Module blok je prijatý, keď:

```text
source/version/package identity sú immutable
+ provider aliases sú explicitné
+ inputs/outputs sú typed a narrow
+ stable instance keys sú dokumentované
+ upgrade plan testuje supported old versions
+ moved history zostáva pre supported consumers
+ mutable-source fixture je odmietnutý
+ wrong-provider mapping fixture je odmietnutý
+ runtime capability prejde
+ second plan je no-op
```

## 22. Anti-patterny

### „Module je state boundary“

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

Child module zdieľa root state, lock, permissions a apply lifecycle.

### „Wrapper okolo resource je automaticky abstraction“

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

Bez domain contractu a invariantov iba pridáva nesting.

### „Version number zaručuje SemVer compatibility“

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

Consumer plan a upgrade tests sú dôkaz; label je tvrdenie ownera.

### „Module môže konfigurovať vlastný production provider“

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.

Target a credentials má spravidla explicitne vlastniť root caller.

### „Môžeme odstrániť staré moved blocks po jednom release“

Táto transition mení remote identity, state ownership alebo Terraform address binding. Create/delete order, old/new address a provider target ovplyvňujú availability, data a rollback aj pri ekvivalentnom HCL. Fresh plan a remote/state read-back musia odlíšiť zachovaný remote objekt od skutočného replacementu.

Neskorí consumers môžu preskakovať versions a potrebujú retained migration chain.

## 23. Kontrolné otázky

1. Aký rozdiel je medzi root a child module responsibility?
2. Prečo module nie je automaticky state boundary?
3. Čo tvorí immutable module dependency subject?
4. Ako sa domain intent líši od provider passthrough wrappera?
5. Prečo provider target typicky vlastní root caller?
6. Prečo output celého resource objectu oslabuje contract?
7. Ako module instance key ovplyvňuje state identity?
8. Prečo default change môže byť breaking?
9. Čo musí obsahovať module upgrade plan review?
10. Prečo sa retained moved history testuje z viacerých old versions?
11. Čo native plan test preukazuje a čo nepreukazuje?
12. Ako sa testuje forbidden mutable-source a wrong-provider path?

## Glossary impact

Relevantné pojmy: Terraform module, root module, child module, module source, module release, capability contract, provider mapping, public interface, narrow output, module instance key, compatibility, moved history, consumer inventory, upgrade fixture a module retirement.

## Primárne zdroje

- [Terraform modules](https://developer.hashicorp.com/terraform/language/modules)
- [Providers within modules](https://developer.hashicorp.com/terraform/language/modules/develop/providers)
- [Refactor Terraform modules](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring)
- [Terraform test](https://developer.hashicorp.com/terraform/language/tests)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Remote backend a state locking](remote-backend-and-state-locking.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Lifecycle, import a moved blocks →](lifecycle-import-moved-blocks.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
