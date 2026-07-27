# Modules

Terraform module je versionovaná capability a contract boundary. Root module skladá environment-specific systém; child modules poskytujú opakovateľné capabilities cez inputs, outputs, provider requirements a migration semantics. Module nie je automaticky samostatný deployment ani state boundary.

Dominantný model:

```text
consumer intent
→ immutable module source/version
→ typed public contract
→ caller-owned provider a environment mapping
→ expanded graph a state addresses
→ narrow outputs a runtime behavior
→ tested upgrade/migration
→ consumer inventory, support a retirement
```

Modul má znižovať počet nebezpečných rozhodnutí callerovi, nie iba premenovať provider arguments.

## 1. Atlas scenár: interný service-platform module

Atlas Payments používa interný module:

```hcl
module "payments_service" {
  source  = "app.terraform.io/atlas/service-platform/aws"
  version = "3.4.2"

  service = {
    name        = "payments-api"
    environment = "prod"
    replicas    = 6
  }

  providers = {
    aws = aws.production
  }
}
```

Module vytvorí compute, load-balancer integration, IAM a observability resources. Caller očakáva:

- immutable source `3.4.2`;
- production-safe defaults a validation;
- explicitný provider target;
- stabilné outputy `service_id`, `endpoint` a `runtime_role_arn`;
- zdokumentované replacement a migration semantics;
- podporovanú upgrade path z `3.3.x`.

Caller nemusí poznať každú internú resource address-u, ale musí rozumieť capability, permissions, side effects a blast radiusu.

## 2. Root module a child module

Root module je configuration subject, nad ktorým sa spúšťa plan/apply a ktorý vlastní:

- backend a state boundary;
- environment composition;
- provider configurations a credentials;
- top-level inputs a policy;
- orchestration medzi capabilities.

Child module je reusable implementation volaná cez `module` block. Všetky jeho resources sa rozvinú do dependency graphu a state-u root module-u:

```text
root module payments-prod
→ module.payments_service
→ module.payments_service.aws_lb.this
→ module.payments_service.aws_iam_role.runtime
```

Child module preto neizoluje lock, permissions ani blast radius. Samostatný state vzniká iba samostatným root/backend lifecycle-om.

## 3. Module source je executable dependency

Source môže byť local path, registry, VCS alebo podporovaný archive/object source. Dôveryhodný source subject obsahuje:

```text
registry/VCS identity
+ immutable version, tag alebo commit
+ checksum/provenance podľa distribution modelu
+ owner a release policy
```

Mutable branch `main` znamená, že rovnaký consumer commit môže pri neskoršom `init` načítať iný kód. Plan potom závisí od skrytej supply-chain zmeny.

Root configuration má pinovať alebo kontrolovane obmedziť module version. Upgrade je samostatná dependency zmena, nie vedľajší efekt bežného `init`.

## 4. Public contract modulu

Contract netvoria iba variable a output tabuľky. Obsahuje:

- purpose a non-goals;
- typed inputs, defaults, validation a null semantics;
- stable outputs;
- required providers a aliases;
- resources a external side effects;
- naming, tagging a identity model;
- security a permission assumptions;
- replacement/destruction behavior;
- compatibility, deprecation a upgrade policy;
- testované supported versions.

Generated documentation je referenčný doplnok. Caller potrebuje vedieť, aké rozhodnutie modul robí a ktoré invarianty garantuje.

## 5. Inputs ako intent, nie provider passthrough

Slabý wrapper vystaví desiatky provider fields 1:1. Caller potom stále navrhuje celý low-level resource a modul nepridáva capability ani policy.

Lepší contract prijme domain intent:

```hcl
variable "service" {
  type = object({
    name        = string
    environment = string
    replicas    = optional(number)
    exposure    = optional(string, "internal")
  })

  validation {
    condition = (
      var.service.environment != "prod" ||
      coalesce(var.service.replicas, 0) >= 2
    )
    error_message = "Production service requires at least two replicas."
  }
}
```

Module môže odvodiť bezpečné implementation detaily, ale nesmie skryť risk-significant behavior za nejasným defaultom.

## 6. Caller-owned provider mapping

Reusable child module deklaruje `required_providers`. Authentication, account/region a environment target má typicky vlastniť root caller:

```hcl
module "replica" {
  source  = "./modules/database"
  version = "2.1.0"

  providers = {
    aws = aws.replica
  }
}
```

Provider mapping je súčasť execution subjectu. Hidden provider configuration v child module môže nasadiť resource do nesprávneho accountu alebo znemožniť callerovi uplatniť least privilege.

Module documentation musí uviesť očakávané aliases a required capabilities plan/apply identity.

## 7. Outputs ako úzke capability API

Output celého provider objectu:

```hcl
output "everything" {
  value = aws_lb.this
}
```

prenáša provider schema a interné attributes do caller contractu. Provider alebo module refactor potom vytvorí breaking change aj bez zmeny reálnej capability.

Publikuj iba stabilné hodnoty:

```hcl
output "endpoint" {
  value = aws_lb.this.dns_name
}

output "runtime_role_arn" {
  value = aws_iam_role.runtime.arn
}
```

Output contract má definovať typ, význam, sensitivity, availability phase a compatibility.

## 8. Composition a dependency

Root module skladá capabilities cez explicitné outputs a inputs:

```hcl
module "network" {
  source  = "./modules/network"
  version = "4.2.0"
}

module "service" {
  source  = "./modules/service"
  version = "3.4.2"

  subnet_ids = module.network.private_subnet_ids
}
```

Referencia prenáša hodnotu aj dependency edge. Široké `depends_on = [module.network]` často vytvára false dependencies, viac unknown values a pomalší graph. Module contract má publikovať konkrétnu readiness alebo identity hodnotu, ktorú consumer skutočne potrebuje.

## 9. Module boundary podľa capability a change coupling-u

Modul je primeraný, keď má:

- jednu koherentnú capability;
- jasného ownera;
- spoločný lifecycle a upgrade cadence;
- testovateľný state space;
- stabilný public contract;
- pridanú policy alebo abstraction hodnotu.

Mega-modul pre celý cloud account vytvára desiatky modes, široký blast radius a upgrade, ktorý môže meniť nesúvisiace systémy. Extrémne tenký wrapper zvyšuje nesting bez stability.

Boundary sa nevyberá podľa počtu `.tf` súborov, ale podľa ownershipu, behavioru a coupling-u.

## 10. Module instance identity

Pri `for_each`:

```hcl
module "service" {
  for_each = var.services
  source   = "./modules/service"

  name = each.key
}
```

vznikajú addresses:

```text
module.service["payments"]
module.service["orders"]
```

Key je súčasť state identity. Premenovanie display name použitého ako key môže vyzerať ako odstránenie starej module instance a vytvorenie novej. Použi stabilný business identifier a pri refaktoringu versionované `moved` mappings.

## 11. Versioning je contract promise

Semantic Versioning má význam iba vtedy, keď module owner klasifikuje zmeny podľa reálneho contractu:

### Kompatibilná zmena

- nový optional input s bezpečným defaultom;
- nový output;
- interný refactor s úplným moved chainom;
- oprava bez zmeny identity alebo behavior contractu.

### Potenciálne breaking zmena

- zmena default semantics;
- premenovanie alebo odstránenie inputu/outputu;
- zmena provider requirementu;
- zmena instance keys alebo resource addresses bez migration;
- nový replacement/destruction behavior;
- zmena permissions alebo exposure.

„Minor release“ nie je dôkaz bezpečnosti. Consumer plan a upgrade test zostávajú autoritatívne.

## 12. Worked failure: mutable source zmenil production plan bez local diffu

Atlas consumer používal:

```hcl
source = "git::ssh://git/atlas/service-platform.git?ref=main"
```

Module owner zmenil default `exposure` z `internal` na `public`. Consumer repository nemal žiadny diff, ale nový CI runner nemal module cache a načítal aktuálny `main`.

```text
rovnaký consumer commit
→ nový module source content
→ load balancer scheme sa zmení
→ production plan otvorí internet exposure
```

Príčina bola mutable executable dependency. Náprava: immutable release, reviewed upgrade, module provenance a policy blokujúca unexpected public exposure.

## 13. Worked failure: bezpečne vyzerajúci default zmenil kapacitu

Module `3.5.0` zaviedol `replicas = optional(number, 2)`. Starší caller input field neposielal, pretože predchádzajúca verzia odvodzovala produkčné minimum 6.

```text
upgrade 3.4.2 → 3.5.0
→ caller config bez replicas ostáva syntakticky validná
→ effective default klesne na 2
→ apply prejde
→ produkcia stratí failure tolerance
```

Default je súčasť public behavior contractu. Upgrade test musí vyhodnotiť effective inputs pre existujúcich consumers, nie iba validate nového module source-u.

## 14. Worked failure: provider alias sa stratil v kompozícii

Root module mal `aws.production` a `aws.replica`. Nový wrapper module neforwardol replica mapping do nested database module-u.

```text
root caller očakáva replica region
→ wrapper použije inherited default provider
→ nested resources vzniknú v primary regione
→ state address vyzerá správne, target identity nie
```

Module composition test musí overovať effective provider configuration address a cloud target, nie iba resource count.

## 15. Upgrade lifecycle

Dôveryhodný upgrade:

```text
consumer inventory a supported source version
→ release notes a migration contract
→ immutable new version selection
→ init/lock-file update
→ static/module tests
→ plan nad reprezentatívnym current state-om
→ address/replacement/default/provider diff review
→ staged apply a runtime verification
→ consumer status a support update
```

Upgrade plan má osobitne označiť:

- resource moves;
- replacements a destroys;
- permission/exposure changes;
- effective default changes;
- output schema changes;
- provider target changes.

## 16. Moved history a neskorí consumers

Reusable module consumers neupgradujú naraz. Consumer môže preskočiť z `2.8.0` na `3.4.2`. Ak module owner odstráni intermediate `moved` blocks, tento consumer uvidí destroy/create aj keď latest-to-latest test prechádza.

Module support policy musí definovať:

- minimálnu podporovanú source version;
- retained moved/deprecation chain;
- testované upgrade paths;
- breaking release boundary;
- retirement deadline.

## 17. Testing ako contract evidence

Test portfolio:

```text
format/validate
→ input validation fixtures
→ plan assertions pre supported modes
→ policy a security checks
→ apply/integration behavior
→ runtime verification
→ upgrade tests z podporovaných versions
→ cleanup/recovery test
```

Examples sú executable documentation iba vtedy, keď sa pravidelne plánujú alebo aplikujú v izolovanom targete.

Module tests musia pokrývať defaulty, null semantics, provider aliases, instance keys, output types a destructive upgrade boundaries.

## 18. Consumer inventory a lifecycle

Owner interného modulu potrebuje vedieť:

- ktorí consumers používajú ktorú version;
- ktoré provider/Terraform versions používajú;
- ktoré environments sú produkčné;
- kto je owner;
- či majú deprecated alebo vulnerable release;
- či je upgrade z ich verzie testovaný.

Bez inventory nemožno bezpečne odstrániť moved history, output alebo starú release ani koordinovať security fix.

## 19. Kauzálny diagnostický walkthrough

Symptom: upgrade module-u `service-platform` z `3.4.2` na `3.5.0` plánuje replacement load balancera, IAM role a všetkých compute instances.

### Krok 1 — stabilizuj subject

```text
consumer commit C52
old module 3.4.2 / new 3.5.0
state lineage L-prod / serial 220
provider lock a target account
module instance key payments
```

### Krok 2 — konkurenčné hypotézy

```text
H1: interné resource addresses sa zmenili bez moved blocks
H2: instance keys alebo module call name sa zmenili
H3: nový default zmenil replace-sensitive argument
H4: provider version/schema zmenila replacement behavior
H5: provider alias mapping mieri na iný target
H6: source artifact nepatrí deklarovanej version
H7: state používa starú alebo chybnú binding históriu
```

### Krok 3 — diskriminačné observation points

- old/new address manifest a moved chain testujú H1/H2;
- effective input diff testuje H3;
- provider lock/schema a plan reasons testujú H4;
- provider configuration address/account audit testuje H5;
- registry/VCS digest testuje H6;
- state binding a serial history testujú H7.

Atlas zistí, že interný `aws_lb.this` sa presunul do `module.edge.aws_lb.this`, ale release neobsahovala moved mapping. H1 vysvetľuje replacement.

### Krok 4 — containment a oprava

Upgrade apply sa zablokuje. Module `3.5.1` pridá retained moved chain. Consumer nepoužije ručný `state mv`, pretože rovnakú migration potrebujú všetky states a neskorí consumers.

### Krok 5 — over outcome

Plan pre reprezentatívne `3.4.2 → 3.5.1` musí ukázať moves bez replacementu. Po apply sa overia rovnaké remote IDs, endpoint, traffic, IAM capability a nový state serial.

### Krok 6 — skorší control

Finding sa mení na automated address manifest diff, upgrade fixture matrix a release gate blokujúci removed address bez moved alebo explicitného breaking verdictu.

## 20. Diagnostický runbook

1. Urči consumer commit, module source/version/digest a current state.
2. Rekonštruuj effective inputs, defaults a provider mappings.
3. Porovnaj old/new public contract a interný address manifest.
4. Over `for_each` keys, module call names a moved history.
5. Oddel module zmenu od provider schema zmeny.
6. Klasifikuj plan podľa move/update/replace/destroy a security dopadu.
7. Zastav upgrade pri nejasnom destructive behavior-e.
8. Oprav module release versionovane, nie environment-specific surgery.
9. Over remote IDs, runtime capability a output contract.
10. Aktualizuj consumer inventory a supported upgrade path.

## 21. Referenčné pravidlá

- Module je capability contract, nie iba priečinok.
- Child module nie je automaticky state boundary.
- Module source je executable supply-chain dependency.
- Root caller vlastní environment a provider configurations.
- Inputs vyjadrujú intent; desiatky passthrough fields oslabujú abstraction.
- Outputs majú byť úzke a stabilné.
- Stable instance key je súčasť public identity contractu.
- Default zmena môže byť breaking aj bez type zmeny.
- Upgrade potrebuje plan nad aktuálnym state-om a runtime verification.
- Moved history sa zachováva podľa podporovaných consumer upgrade paths.
- Consumer inventory je podmienka deprecation a retirementu.

## 22. Časté omyly

### „Registry version garantuje kvalitný modul“

Registry distribuuje metadata; negarantuje bezpečné defaults, ownership ani compatibility.

### „Minor upgrade môžeme automaticky applynuť“

Môže meniť default, provider behavior, addresses alebo permissions.

### „Module izoluje blast radius“

Resources child module-u zostávajú v root graph/state a pod rovnakou apply identity.

### „Output celého resource objectu je flexibilnejší“

Caller sa naviaže na provider internals a budúce refaktoringy.

### „Ručný `state mv` vyrieši module refactor“

Iba v jednom state-e; reusable migration má byť versionovaná a testovateľná.

## Zhrnutie

Dôveryhodný module lifecycle je:

```text
versionovaný capability source
→ explicitný typed contract
→ caller-owned target identity
→ stable graph/state identities
→ narrow outputs a verified behavior
→ tested versioned migration
→ consumer inventory a support closure
```

Module troubleshooting začína rekonštrukciou source, contractu, provider mappingu a state addressov. Počet resources ani úspešný `init` nedokazujú compatibility.

## Oficiálna dokumentácia

- [Modules overview](https://developer.hashicorp.com/terraform/language/modules)
- [Use modules in your configuration](https://developer.hashicorp.com/terraform/language/modules/configuration)
- [Develop modules](https://developer.hashicorp.com/terraform/language/modules/develop)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Remote backend a state locking](remote-backend-and-state-locking.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Lifecycle, import a moved blocks →](lifecycle-import-moved-blocks.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
