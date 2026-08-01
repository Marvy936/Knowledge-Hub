# Variables, locals a outputs

Variables, locals a outputs tvoria verejný a interný value contract Terraform modulu. Variable určuje, čo smie caller ovplyvniť. Local pomenúva alebo normalizuje interný expression. Output publikuje minimálny výsledok, na ktorý sa môžu naviazať downstream consumers. Keď sú tieto vrstvy navrhnuté slabo, konfigurácia môže byť syntakticky validná a napriek tomu použiť nesprávny environment, tichý development default, mutable artifact tag alebo nestabilný resource key.

Kapitola pokračuje incidentom `IAC-PAY-75`. Atlas Payments volá module `service-platform` pre `prod-eu`. Pipeline očakáva šesť replicas a immutable image digest, ale `prod.tfvars` sa nenačíta. Module použije development default `replicas = 2`, environment variable prepíše image digest mutable tagom a local vytvorí subnet keys z pozície v liste. Plan je platný, no effective value subject nezodpovedá schválenému release intentu.

## 1. Dominantný caller-to-consumer lifecycle

Nasledujúci model opisuje prechody jedného Terraform configuration, state a remote-resource subject, nie iba poradie krokov. Failure môže nastať v ktoromkoľvek bode reťazca resolved inputs a graph cez provider API mutation až po state binding a zanechať partial alebo unknown outcome. Každý transition preto potrebuje vlastný read-back a closure tvorí exact provider target, remote/state reconciliation a druhý no-op plan.


```text
caller intent
→ variable declaration a type contract
→ value source a precedence
→ validation, nullable a sensitive semantics
→ effective resolved value
→ local normalization a stable identity derivation
→ resource/module graph
→ output value a precondition
→ downstream consumer contract
→ versioning, deprecation a migration
```


Input variable je explicitné API modulu. Local value je interná implementácia, ktorú caller nemôže override-nuť. Output value je publikované API smerom von.


Dôveryhodnosť nevzniká iba z typu. Potrebujeme poznať aj source hodnoty, precedence, semantic meaning, effect na identity a risk a spôsob, akým sa hodnota dostane do downstream systému.

## 2. Exact value subject

Atlas root module volá:

```hcl
module "payments" {
  source = "./modules/service-platform"

  environment  = "prod-eu"
  image_digest = "sha256:8f7c..."
  replicas     = 6
  secret_ref   = "vault://payments/prod/runtime"

  subnets = {
    az_a = {
      cidr = "10.40.10.0/24"
      zone = "eu-central-1a"
    }
    az_b = {
      cidr = "10.40.20.0/24"
      zone = "eu-central-1b"
    }
  }
}
```

Value subject pre plan zahŕňa:

```yaml
values:
  environment:
    effective: prod-eu
    sourceClass: explicit-root-argument
  replicas:
    effective: 6
    sourceClass: prod.tfvars
  image_digest:
    effectiveFingerprint: sha256:8f7c...
    sourceClass: release-manifest
  secret_ref:
    effectiveFingerprint: sha256:reference-only
    sensitive: false
  subnets:
    keySet: [az_a, az_b]
    sourceDigest: sha256:31cd...
```

Manifest nesmie logovať secret value. Má však zachovať non-secret effective values, key sets, source classes a fingerprints tak, aby reviewer vedel vysvetliť, z čoho vznikol plan.

## 3. Typed variables ako executable API

```hcl
variable "subnets" {
  description = "Production subnets keyed by stable logical identity."

  type = map(object({
    cidr = string
    zone = string
  }))
}
```

Presný type constraint:

```text
odhalí neplatný shape pred provider operation
→ stabilizuje module interface
→ objasní collection identity
→ umožní validation
→ znižuje implicitné conversion surprises
```

`type = any` je vhodný iba vtedy, keď module skutočne odovzdáva opaque value bez interpretácie. Ak module číta fields, filtruje collection alebo podľa nej vytvára resources, potrebuje explicitný type contract.

Object conversion môže zahodiť extra attributes, ktoré contract nepozná. Caller nesmie predpokladať, že undeclared metadata prežijú cez module boundary.

## 4. Required values a bezpečné defaults

Variable bez `default` vyžaduje explicitný caller intent. To je správny contract pre hodnoty, ktoré určujú production capacity, exposure, data retention alebo management identity.

```hcl
variable "replicas" {
  description = "Desired production service capacity."
  type        = number

  validation {
    condition     = var.replicas >= 2 && var.replicas <= 30
    error_message = "replicas must be between 2 and 30."
  }
}
```

Default je bezpečný iba vtedy, keď má rovnaký význam pre všetkých podporovaných callerov a jeho použitie neoslabuje security, availability ani compliance. Nesmie neočakávane meniť resource identity a musí byť pokrytý contract testom. Zmena defaultu je interface change s vlastnou compatibility policy, pretože caller bez source diffu môže dostať nový effective behavior.

Development convenience, napríklad `replicas = 1`, preto nepatrí do shared production module-u. Ak caller vynechá risk-significant hodnotu, plan má zlyhať namiesto tichého doplnenia lacného alebo menej bezpečného variantu.

Variable bez `default` vyžaduje explicitný caller intent:

```hcl
variable "replicas" {
  description = "Desired production service capacity."
  type        = number

  validation {
    condition     = var.replicas >= 2 && var.replicas <= 30
    error_message = "replicas must be between 2 and 30."
  }
}
```

Shared module nemá používať development convenience ako production default. Ak `replicas` vyjadruje capacity a availability intent, chýbajúca hodnota má zlyhať pri plan-e.


Terraform transition sleduje má rovnaký význam pre všetkých supported callers, neoslabuje security, availability ani compliance, nemení resource identity neočakávaným spôsobom, je pokrytý contract testami a jeho zmena má explicitnú compatibility policy.

Každý prvok sa viaže na rovnakú configuration, state a provider generation, aby sa vylúčil wrong-target alebo lost-binding outcome.


## 5. Optional attributes a state-space risk

Terraform umožňuje optional object attributes:

```hcl
variable "runtime" {
  type = object({
    architecture   = optional(string, "amd64")
    enable_metrics = optional(bool, true)
    log_level      = optional(string, "info")
  })
}
```

Taký contract podporuje backward-compatible rozšírenie. Veľké množstvo optional booleans však vytvára combinatorial behavior state space:

```text
enable_x × enable_y × mode_a × mode_b × environment
→ množstvo neotestovaných configurations
```

Keď module obsahuje desiatky feature switches, často spája viac capabilities a ownership boundaries, než by mal.

## 6. `null`, empty a omission nie sú to isté

```hcl
variable "custom_domain" {
  type     = string
  nullable = true
  default  = null

  validation {
    condition     = var.custom_domain == null || length(trimspace(var.custom_domain)) > 0
    error_message = "custom_domain must be null or a non-empty hostname."
  }
}
```

Contract musí vysvetliť:

```text
null
→ custom domain sa nevytvorí alebo argument sa omitne

""
→ invalid caller input

"api.payments.example.com"
→ vytvor DNS a TLS dependencies
```

`null` môže spôsobiť, že Terraform argument považuje za omitted a provider použije default. To môže byť žiadané, ale musí to byť explicitná semantics, nie náhodný výsledok conditional expression.

Prázdna mapa, prázdny list a `null` majú odlišný graph effect. Prázdna mapa pri `for_each` znamená nula instances; `null` môže byť pre `for_each` neplatný.

## 7. Validation chráni domain invariant

Táto podsekcia vysvetľuje konkrétnu časť Terraform configuration, state a remote-resource subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inputs a graph cez provider API mutation až po state binding; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po exact provider target, remote/state reconciliation a druhý no-op plan.


```hcl
variable "image_digest" {
  type        = string
  description = "Immutable OCI digest for the approved release."

  validation {
    condition     = can(regex("^sha256:[0-9a-f]{64}$", var.image_digest))
    error_message = "image_digest must be an immutable sha256 OCI digest."
  }
}
```

Validation preukazuje, že effective input spĺňa lokálny expression contract. Nepreukazuje, že digest existuje, že je podpísaný, že scan patrí danému digestu alebo že runtime neskôr spustí rovnaký platform manifest.

Ďalšie vhodné validations:

```hcl
variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "stage", "prod-eu"], var.environment)
    error_message = "Unsupported environment."
  }
}

variable "subnets" {
  type = map(object({
    cidr = string
    zone = string
  }))

  validation {
    condition = alltrue([
      for key in keys(var.subnets) :
      can(regex("^[a-z0-9_]+$", key))
    ])
    error_message = "Subnet keys must be stable machine identifiers."
  }
}
```

## 8. Root variable sources a precedence

Root values môžu prísť z viacerých vrstiev:

```text
variable default
→ environment-specific variable files
→ auto-loaded files
→ TF_VAR_* environment variables
→ command-line -var a -var-file
→ remote runner/workspace variables
→ orchestration wrapper
```

Presná precedence závisí od použitého interface-u a platformy. Praktický problém je rovnaký: reviewer môže čítať `prod.tfvars`, zatiaľ čo pipeline exportuje vyšší override.

Príklad diagnostiky:

```bash
printf 'TF_VAR_environment=%q\n' "${TF_VAR_environment-}"
printf 'TF_VAR_replicas=%q\n' "${TF_VAR_replicas-}"
terraform plan -var-file=prod.tfvars -out=tfplan
terraform show -json tfplan > tfplan.json
```

Taký log môže bezpečne ukázať non-secret overrides. Secret values sa nevypisujú. Plan JSON sa analyzuje na final resource arguments a output changes. Ani plan JSON nemusí bezpečne redigovať všetky citlivé údaje; access a retention sa navrhujú ako secret-bearing artifact boundary.

## 9. Effective input manifest

Atlas vytvára pred planom machine-readable manifest bez secret values:

```bash
jq -n \
  --arg environment "$TF_VAR_environment" \
  --arg replicas "$TF_VAR_replicas" \
  --arg image_digest "$TF_VAR_image_digest" \
  '{
    environment: {effective: $environment, sensitive: false},
    replicas: {effective: ($replicas|tonumber), sensitive: false},
    image_digest: {fingerprint: $image_digest, sensitive: false}
  }' > resolved-inputs.json

sha256sum resolved-inputs.json
```

Digest preukazuje integritu manifestu. Manifest preukazuje iba hodnoty, ktoré wrapper skutočne zaznamenal. Ak Terraform dostane ďalší override mimo wrappera, manifest môže byť neúplný. Najsilnejší design generuje plan a manifest z jedného orchestration source-u a policy porovná expected values s plan JSON.

## 10. Sensitive nie je encryption ani revocation

`sensitive = true` je presentation control v Terraform value propagation. Obmedzí bežné CLI zobrazenie, ale secret môže zostať v state-e alebo saved plane, provider ho môže zalogovať a oprávnený caller ho môže explicitne exportovať. Nechráni job memory, filesystem, artifacts ani backend recovery copies.

```hcl
variable "bootstrap_token" {
  type      = string
  sensitive = true
}
```

Flag tiež neurčuje lifetime a po exposure nevykoná provider-side revocation. Secret material preto vytvára citlivú boundary naprieč backendom, planom, logs a runnerom. Preferovaný interface prenáša secret-manager reference a workload získava krátkodobú hodnotu cez vlastnú identity.

```hcl
variable "secret_ref" {
  type        = string
  description = "Runtime secret-manager reference, not secret material."
}
```

Ak Terraform musí secret spravovať, lifecycle zahŕňa target revocation, consumer reload a old-credential forbidden test; redaction v CLI nie je closure.

```hcl
variable "bootstrap_token" {
  type      = string
  sensitive = true
}
```

`sensitive = true` obmedzuje bežné CLI zobrazenie pri propagácii hodnoty. Neznamená:


Terraform transition sleduje že hodnota nebude v state alebo plan-e, že provider ju nezaloguje, že job memory/filesystem je bezpečný, že `terraform output -raw` ju nevydá oprávnenému callerovi, že credential je krátkodobý a že exposure vyvolá provider-side revocation.

Každý prvok sa viaže na rovnakú configuration, state a provider generation, aby sa vylúčil wrong-target alebo lost-binding outcome.


Preferovaný model je posielať referenciu:

```hcl
variable "secret_ref" {
  type        = string
  description = "Runtime secret-manager reference, not secret material."
}
```

Workload získa secret až cez workload identity. Keď provider musí secret material spravovať, backend, plan artifacts, logs a recovery copies sa považujú za citlivú boundary.

## 11. Locals ako normalizácia, nie druhý input systém

Locals transformujú už resolved inputs do canonical interného modelu. Sú vhodné na stabilné naming, opakované expressions, normalizáciu collections, derived tags a dočasný compatibility adapter medzi versionovanými input shapes.

```hcl
locals {
  canonical_name = "atlas-payments-${var.environment}"
  common_tags = {
    Application = "payments"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
  normalized_subnets = {
    for key, subnet in var.subnets : key => {
      name = "${local.canonical_name}-${key}"
      cidr = subnet.cidr
      zone = subnet.zone
    }
  }
}
```

Local nemá vytvárať skrytý druhý policy alebo input systém. Keď nested conditionals menia počet, keys alebo identity resources, ide o graph decision, ktorý potrebuje explicitný contract test a resolved-key evidence. Ak taká logika rastie, vhodnejšia je menšia capability boundary alebo verejný typed input než ďalšia neviditeľná transformácia.

```hcl
locals {
  canonical_name = "atlas-payments-${var.environment}"

  common_tags = {
    Application = "payments"
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  normalized_subnets = {
    for key, subnet in var.subnets : key => {
      name = "${local.canonical_name}-${key}"
      cidr = subnet.cidr
      zone = subnet.zone
    }
  }
}
```


Terraform transition sleduje canonical naming, opakované expressions, normalizáciu collections, derived tags a compatibility adapter medzi starým a novým input shape-om.

Každý prvok sa viaže na rovnakú configuration, state a provider generation, aby sa vylúčil wrong-target alebo lost-binding outcome.


Local nemá skrývať business decision tree, ktorý reviewer nevie vysvetliť. Ak local obsahuje veľa nested conditionals a mení počet/identity resources, potrebuje samostatný contract test alebo menší module boundary.

## 12. Stable keys sú management identity

`for_each` key nie je len label v source. Stáva sa súčasťou resource address-y v state-e, a preto jeho zmena môže znamenať ownership migration alebo replacement. Pred nasledujúcim HCL príkladom treba najprv rozhodnúť, ktorá business identity má prežiť display-name a ordering changes.

```hcl
resource "aws_subnet" "private" {
  for_each = local.normalized_subnets

  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value.cidr
  availability_zone = each.value.zone

  tags = merge(local.common_tags, {
    Name = each.value.name
  })
}
```

Key `az_a` je súčasť Terraform address-y:

```text
aws_subnet.private["az_a"]
```

Premenovanie keya na `private_a` môže byť identity migration, nie iba textový rename. Display name alebo list index nie sú automaticky stabilné keys.

## 13. Outputs sú verejné module API

```hcl
output "private_subnet_ids" {
  description = "Private subnet IDs keyed by stable logical identity."
  value = {
    for key, subnet in aws_subnet.private :
    key => subnet.id
  }
}

output "service_endpoint" {
  description = "HTTPS endpoint exposed to approved consumers."
  value       = "https://${aws_lb.api.dns_name}"

  precondition {
    condition     = startswith("https://${aws_lb.api.dns_name}", "https://")
    error_message = "Service endpoint must use HTTPS."
  }
}
```

Output publikuje minimum stabilných capabilities. Tento anti-pattern exportuje provider internals:

```hcl
output "load_balancer" {
  value = aws_lb.api
}
```

Consumer sa potom môže naviazať na computed fields, ktoré module nikdy nesľúbil. Provider upgrade zmení shape alebo semantics a downstream consumer sa rozbije bez vedomej module API zmeny.

## 14. Output precondition a runtime proof boundary

Output precondition overuje invariant dostupný Terraform evaluation modelu. Nevykonáva externý HTTPS request ani business transaction.

```bash
terraform output -json > outputs.json
jq -r '.service_endpoint.value' outputs.json
```

Výstup preukazuje latest root output value v aktuálnom state subjecte. Nepreukazuje, že DNS už propagoval, TLS certifikát je dôveryhodný alebo endpoint spracuje payment request. Potrebný je samostatný runtime verifier.

## 15. Module composition a narrow contracts

```hcl
module "network" {
  source  = "./modules/network"
  subnets = var.subnets
}

module "payments" {
  source = "./modules/service-platform"

  subnet_ids  = module.network.private_subnet_ids
  image_digest = var.image_digest
  replicas     = var.replicas
}
```

Output reference prenáša hodnotu aj dependency edge. Consumer nemusí čítať celý upstream state ani provider resource object.

Cross-state contract je silnejší, keď producer publikuje úzky endpoint, parameter alebo registry record s ownerom a freshness semantics. Priamy access k remote state-u môže sprístupniť viac sensitive informácií, než consumer potrebuje.

## 16. Interface versioning

Module interface sa verzuje podľa effective behavioru a state identity, nie iba podľa syntaktickej kompatibility. Nový optional input s naozaj bezpečným defaultom, nový output alebo interná local transformácia bez zmeny external semantics môžu byť backward-compatible. Aj pri nich sa však testuje existing-state upgrade.

Premenovanie inputu/outputu, zmena type constraintu, default alebo `null` semantics, collection keys či sensitive behavioru je breaking alebo risk-significant transition. Rovnako nebezpečná je zmena immutable digest inputu na mutable tag, pretože mení release identity bez caller source diffu.

Version label je iba deklarácia autora. Dôkaz compatibility poskytuje consumer upgrade plan nad reprezentatívnym existing state-om, forbidden fixtures a druhý no-op plan. Support contract musí povedať, z ktorých verzií je upgrade podporovaný a aká migration je potrebná.


Compatibility review sleduje nový optional input s bezpečným defaultom, nový output, nový optional object field a internú local transformáciu bez zmeny external semantics.

Každá zmena sa posudzuje nad existujúcim consumer state-om, pretože syntakticky platný upgrade môže meniť identity alebo behavior.



Compatibility review sleduje premenovanie inputu/outputu, zmenu type constraint, zmenu default alebo `null` semantics, zmenu collection keys, zmenu sensitive behavioru a odstránenie outputu.

Ďalej sleduje zmenu z immutable digestu na mutable tag.

Každá zmena sa posudzuje nad existujúcim consumer state-om, pretože syntakticky platný upgrade môže meniť identity alebo behavior.


Module release potrebuje upgrade test nad existujúcim state-om, nie iba clean apply novej verzie.

## 17. Worked incident: production použila development default

Pipeline nevložila `-var-file=prod.tfvars`. Module mal:

```hcl
variable "replicas" {
  type    = number
  default = 2
}
```

```text
prod caller omitne replicas
→ shared module použije development default
→ plan je syntakticky a typovo validný
→ apply vytvorí dve replicas
→ load balancer je healthy
→ service poruší capacity a latency objective
```

Technical health nepreukázal správny business capacity outcome.

Recovery odstránila shared default, pridala required variable, environment policy a post-apply capacity query. Forbidden test spúšťa production fixture bez `replicas` a očakáva plan failure.

## 18. Worked incident: sensitive output unikol

Module publikoval generated password:

```hcl
output "database_password" {
  value     = random_password.database.result
  sensitive = true
}
```

Pipeline vykonala:

```bash
terraform output -json > outputs.json
```

Artifact sa uložil do diagnostiky. `sensitive` chránil bežné zobrazenie, nie oprávnený export.

Recovery:

```text
revokovať/rotovať database credential
→ auditovať artifact downloads
→ odstrániť retention copies podľa policy
→ presunúť credential lifecycle do secret managera
→ publikovať iba secret reference/version
```

## 19. Competing hypotheses pri value mismatch

Symptom: schválený plan očakával šesť replicas, nový plan nad rovnakým source ukazuje dve.

```text
H1: prod.tfvars sa nenačítal
H2: TF_VAR_replicas prepísal hodnotu
H3: root module neforwarduje input
H4: child module default sa zmenil
H5: caller poslal null a spustil default semantics
H6: porovnávame iný workspace/backend
```

Dôkazy:

```bash
printenv | grep '^TF_VAR_' | sed 's/=.*$/=<redacted-or-recorded>/'
terraform workspace show
terraform show -json tfplan | jq '.resource_changes[] | select(.address|contains("service"))'
```

Environment inventory testuje H2, source/module diff H3/H4, plan JSON effective arguments H1/H5 a workspace/backend identity H6. Logs nesmú vypisovať secret values.

## 20. Acceptance a forbidden paths

Acceptance spája interface contract s graph a secret behaviorom. Nestačí, že happy-path plan prejde; musí sa preukázať odmietnutie chýbajúceho production intentu, mutable release identity a nebezpečného secret exportu. Druhý plan potom overí stabilitu effective inputs a management keys.

Value-contract blok je prijatý, keď:

```text
required production intent nemá unsafe default
+ effective sources a precedence sú auditovateľné
+ image input je immutable digest
+ sensitive values sa nepublikujú ako artifacts
+ stable keys zachovávajú resource identity
+ outputs sú minimálne a explicitné
+ downstream používa iba documented outputs
+ production fixture bez replicas zlyhá
+ mutable tag fixture zlyhá validation
+ second plan s rovnakými values je no-op
```

## 21. Kontrolné otázky

1. Aký rozdiel je medzi variable, local a output authority?
2. Prečo type constraint sám nestačí na semantic correctness?
3. Kedy je default bezpečný a kedy skrýva chýbajúci intent?
4. Aký rozdiel je medzi `null`, empty stringom a prázdnou mapou?
5. Čo variable validation preukazuje a čo nepreukazuje?
6. Prečo musí plan evidence obsahovať effective value provenance?
7. Čo `sensitive` chráni a čo nechráni?
8. Prečo stable map key tvorí management identity?
9. Prečo output celého provider objectu oslabuje module API?
10. Čo preukazuje `terraform output -json` a čo nepreukazuje?
11. Ako sa odlíši missing var-file od vyššieho override-u?
12. Aké forbidden fixtures má production module testovať?

## Glossary impact

Relevantné pojmy: input variable, type constraint, default, optional attribute, nullable, validation, value source, precedence, effective value, sensitive, local value, normalization, stable key, output, output precondition, module API, compatibility, value provenance a resolved-input manifest.

## Primárne zdroje

- [Terraform input variables](https://developer.hashicorp.com/terraform/language/values/variables)
- [Terraform local values](https://developer.hashicorp.com/terraform/language/values/locals)
- [Terraform outputs](https://developer.hashicorp.com/terraform/language/values/outputs)
- [Terraform types and values](https://developer.hashicorp.com/terraform/language/expressions/types)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Terraform providers, resources a data sources](terraform-providers-resources-data-sources.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Expressions a dependency graph →](expressions-and-dependency-graph.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
