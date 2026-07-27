# Variables, locals a outputs

Variables, locals a outputs tvoria interface medzi caller intentom, internou module implementáciou a downstream consumers. Nie sú iba tri syntaxické kategórie. Spoločne rozhodujú, ktoré hodnoty smie caller meniť, ako sa vstupy validujú a normalizujú, aké dependencies vzniknú a ktoré výsledky sa stanú stabilným verejným contractom.

Kapitola pokračuje v scenári Atlas Payments. Root configuration `prod-eu` volá module `service-platform` pre release `3.14.0`. Module prijíma environment, image digest, replica policy, subnet mapu a secret reference; interne vytvára canonical names a tags a publikuje iba endpoint a stabilné resource IDs.

## 1. Dominantný model

```text
caller intent
→ typed input contract
→ source, precedence a validation
→ default/null resolution
→ local normalization a derived values
→ resource graph a provider operations
→ output postconditions
→ stable consumer contract
→ interface evolution a deprecation
```

Tri vrstvy majú odlišný účel:

- **Variable:** externý input, ktorý caller môže poskytnúť.
- **Local:** interná odvodená hodnota, ktorú caller nemôže override-nuť.
- **Output:** explicitne publikovaný výsledok modulu.

Dôveryhodný interface zachováva význam hodnoty od input source-u až po consumer. Nestačí, že Terraform dokáže hodnotu typovo spracovať.

## 2. Atlas module contract

Root module volá:

```hcl
module "payments" {
  source = "./modules/service-platform"

  environment  = "prod"
  image_digest = "sha256:314..."
  replicas     = 6
  secret_ref   = "vault://payments/prod/runtime"

  subnets = {
    private_a = {
      cidr = "10.40.10.0/24"
      zone = "eu-central-1a"
    }
    private_b = {
      cidr = "10.40.20.0/24"
      zone = "eu-central-1b"
    }
  }
}
```

Module contract nie je iba zoznam argumentov. Pre každý input určuje:

```text
name + semantic purpose
+ exact type
+ required/optional/null behavior
+ validation
+ sensitive handling
+ compatibility policy
+ effect on resource identity a risk
```

`replicas = 6` je capacity intent. `image_digest` je immutable release identity. `secret_ref` je referencia, nie samotný secret. Zamenenie týchto významov za všeobecné stringy oslabí review aj policy.

## 3. Typed variables sú executable contracts

```hcl
variable "subnets" {
  description = "Stable subnet definitions keyed by logical identity."

  type = map(object({
    cidr = string
    zone = string
  }))
}
```

Presný typ:

- odhalí chybu skôr než provider;
- stabilizuje module API;
- objasní collection identity;
- umožní zmysluplnú validation;
- zníži implicitné konverzie.

`type = any` prenáša chybu hlbšie do expressions alebo provider schema a robí interface neauditovateľný.

Object type môže úmyselne zahodiť extra attributes pri konverzii. Caller preto nemá predpokladať, že module zachová dáta mimo deklarovaného contractu.

## 4. Required, optional a bezpečné defaults

Variable bez `default` vyžaduje explicitný caller intent. Default je vhodný iba vtedy, keď je bezpečný a rovnaký význam platí pre všetkých callerov.

```hcl
variable "replicas" {
  type = number

  validation {
    condition     = var.replicas >= 2 && var.replicas <= 20
    error_message = "Replica count must be between 2 and 20."
  }
}
```

Atlas zámerne nepoužíva produkčný default `replicas = 2`. Chýbajúci capacity intent má zlyhať pri plan-e, nie ticho znížiť production capacity.

Optional object attributes sú vhodné pre kompatibilnú evolúciu:

```hcl
variable "runtime" {
  type = object({
    cpu_architecture = optional(string, "amd64")
    enable_metrics   = optional(bool, true)
  })
}
```

Veľké množstvo optional fields a boolean flags však vytvára neotestovateľný behavior state space. Vtedy module pravdepodobne spája viac capabilities, než by mal.

## 5. `null` je súčasť semantics

`null` nie je prázdny string, nula ani prázdna kolekcia. Podľa contextu môže znamenať omission, inherit/default alebo explicitnú neprítomnosť.

```hcl
variable "custom_domain" {
  type     = string
  nullable = true
  default  = null
}
```

Module musí definovať:

```text
null → nepoužívaj custom domain
""   → invalid input
value → vytvor DNS/TLS contract
```

Ak caller pošle `null`, môže tým potlačiť default alebo vyvolať provider-specific omission behavior. Null semantics patria do testov a compatibility dokumentácie.

## 6. Validation chráni domain invariant

```hcl
variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "stage", "prod"], var.environment)
    error_message = "Environment must be dev, stage, or prod."
  }
}
```

Dobrá validation:

- zlyhá pred remote mutation;
- kontroluje domain contract, nie iba syntax;
- vysvetľuje opravu;
- pokrýva identity a risk hranice;
- používa fixture tests.

Atlas validuje aj to, že `image_digest` je digest, nie mutable tag, subnet keys sú stabilné a production replica count neporušuje capacity minimum.

Validation však nenahrádza provider alebo runtime kontrolu. Formát CIDR môže byť správny, ale stále kolidovať s existujúcou sieťou.

## 7. Root input sources a effective value

Root variables môžu prísť z:

- `-var`;
- `-var-file`;
- auto-loaded variable files;
- `TF_VAR_*` environment variables;
- remote workspace variable setu;
- pipeline orchestration vrstvy.

Dôveryhodný plan musí vedieť zostaviť non-secret provenance:

```text
replicas
→ prod.tfvars = 6
→ žiadny vyšší override
→ effective value = 6
```

Skryté source a precedence kombinácie komplikujú reprodukciu. Atlas preto vytvára input manifest s keyom, source class, version/fingerprintom a sensitive markerom bez logovania secret values.

Apply musí použiť rovnaký resolved input subject ako approved saved plan.

## 8. Sensitive hodnoty a secret references

```hcl
variable "api_token" {
  type      = string
  sensitive = true
}
```

`sensitive` obmedzuje zobrazenie v štandardnom outpute. Nezaručuje:

- encryption v state;
- bezpečný provider alebo job;
- ochranu pred `terraform output -raw`;
- odstránenie z plan artifactu;
- provider-side revocation.

Atlas preto module nedáva samotný runtime secret. Poskytne `secret_ref`, z ktorej workload identity načíta secret až v runtime. Ak provider musí dostať citlivú hodnotu, state/backend a log lifecycle sa navrhnú ako secret-bearing boundary.

Secret commitnutý v `.tfvars` sa najprv revokuje u providera. History rewrite nie je revokácia.

## 9. Locals ako normalization vrstva

```hcl
locals {
  canonical_name = "atlas-payments-${var.environment}"

  common_tags = {
    Application = "payments"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
```

Locals sú vhodné na:

- canonical naming;
- normalizáciu vstupov;
- derived identifiers;
- common tags;
- transformáciu collections;
- interný compatibility adapter.

Local nie je override point ani runtime resource. Referencie cez local zachovávajú dependency provenance.

Príliš komplexné locals môžu skryť business decision tree. Keď review nevie vysvetliť, ako input vytvorí resource identity a plan action, transformácia patrí do menšieho contractu, testu alebo samostatného module.

## 10. Stable identity cez normalized keys

Atlas subnet map používa keys `private_a` a `private_b` ako module-level logical identity. Local ich môže zoradiť alebo doplniť tags, ale nesmie ich premenovať podľa mutable display name-u.

```hcl
locals {
  subnet_contract = {
    for key, subnet in var.subnets : key => {
      cidr = subnet.cidr
      zone = subnet.zone
      name = "${local.canonical_name}-${key}"
    }
  }
}
```

Key zmena môže viesť na resource address change a replacement. Preto je input interface zároveň identity contractom.

## 11. Outputs sú verejné API modulu

```hcl
output "service_endpoint" {
  description = "HTTPS endpoint for the deployed service."
  value       = "https://${example_lb.payments.hostname}"
}

output "service_security_group_id" {
  description = "Stable security-group identifier for approved consumers."
  value       = example_security_group.service.id
}
```

Output má publikovať minimum stabilných capabilities, ktoré consumer potrebuje. Nemá exportovať celý provider resource object:

```hcl
# slabý contract
output "everything" {
  value = example_lb.payments
}
```

Taký output viaže caller na provider internals, computed fields a upgrade behavior. Explicitné outputs obmedzujú coupling a umožňujú semantické versionovanie module interface-u.

## 12. Output postconditions a unknown values

Output môže mať precondition:

```hcl
output "service_endpoint" {
  value = local.service_endpoint

  precondition {
    condition     = startswith(local.service_endpoint, "https://")
    error_message = "Service endpoint must use HTTPS."
  }
}
```

Počas planu môže byť endpoint unknown, pretože hostname vznikne až po create. Unknown nie je `null` ani wildcard. Zachová type a dependency, ale konkrétnu hodnotu poskytne apply.

Riziko vzniká, ak unknown ovplyvňuje:

- `for_each` keys;
- `count`;
- provider configuration;
- policy decision;
- target identity;
- module source.

Graph shape a authorization inputs musia byť známe pred mutation.

## 13. Module composition

```hcl
module "network" {
  source  = "./modules/network"
  subnets = var.subnets
}

module "payments" {
  source     = "./modules/service-platform"
  subnet_ids = module.network.private_subnet_ids
}
```

Output reference prenáša hodnotu aj dependency edge. Consumer nemá čítať upstream internals priamo ani zdieľať celý state, ak stačí užší publish contract.

Cross-state contract môže byť publikovaný cez service catalog, parameter store, DNS, registry manifest alebo riadený remote-state read. Remote state access často poskytuje širšiu visibility než logický output contract a musí sa posudzovať ako security boundary.

## 14. Interface evolution

Backward-compatible zmeny môžu byť:

- nový optional input s bezpečným defaultom;
- nový output;
- nový optional object field;
- interná local transformácia bez zmeny semantics.

Potentially breaking zmeny:

- premenovanie inputu alebo outputu;
- zmena type constraint;
- zmena default/null semantics;
- odstránenie outputu;
- zmena collection keys;
- zmena sensitive alebo ownership behavioru.

Module release musí komunikovať compatibility a supported upgrade path. Deprecation má ownera, deadline a migration guidance.

## 15. Worked failure: production capacity ticho použila default

Root caller zabudol poslať `replicas`. Module mal pohodlný default `2`, ktorý vznikol pre development.

```text
production caller omitne replicas
→ module default = 2
→ plan je validný
→ apply prejde
→ load balancer posiela production traffic na poddimenzovanú service
```

### Príčina

Interface nerozlišoval environment-specific required intent od bezpečného univerzálneho defaultu.

### Náprava

`replicas` sa stala required variable. Root environment policy kontroluje minimum a post-apply capacity oracle potvrdzuje healthy replicas. Development convenience sa rieši v development caller configuration, nie v shared module default-e.

## 16. Worked failure: output celého objectu rozbil consumera

Network module exportoval celý provider subnet object. Consumer používal field, ktorý nebol súčasťou dokumentovaného module contractu. Provider upgrade field premenoval alebo zmenil jeho computed behavior.

```text
provider internals leaknú cez output
→ consumer sa na ne naviaže
→ provider upgrade zmení object shape/semantics
→ downstream plan zlyhá bez vedomej module API zmeny
```

### Náprava

Module publikuje iba `private_subnet_ids` a explicitné metadata potrebné consumerom. Contract tests pokrývajú output types a upgrade path.

## 17. Worked failure: sensitive output unikol cez automation

Module publikoval generated password ako sensitive output. Pipeline následne použila:

```bash
terraform output -json
```

Výsledný JSON bol uložený ako diagnostický artifact.

`sensitive` skryl hodnotu v bežnom CLI zobrazení, ale oprávnený command ju exportoval v plain texte.

### Náprava

Credential sa revokoval, artifact access a downloads sa auditovali a password lifecycle sa presunul do secret managera. Terraform output publikuje iba secret reference a version ID.

## 18. Kauzálny diagnostický walkthrough

Symptom: approved production plan očakával šesť replicas, ale nový plan na rovnakom source commite ukazuje dve.

### Krok 1 — stabilizuj value subject

```text
root configuration    C74
module version        M14
environment           prod-eu
saved plan            PL430
expected input        replicas = 6
observed plan input   replicas = 2
```

### Krok 2 — konkurenčné hypotézy

```text
H1: prod.tfvars nebol načítaný
H2: TF_VAR_replicas alebo workspace variable prepísali hodnotu
H3: root module prestal forwardovať replicas do child module
H4: child module default sa zmenil
H5: null semantics aktivovali default
H6: pipeline použila iný module version alebo variable set
H7: zobrazený plan patrí inému environmentu
```

### Krok 3 — diskriminačné observation points

- invocation arguments a loaded variable-file inventory testujú H1;
- redacted variable provenance testuje H2;
- root module call diff testuje H3;
- module source/digest a variable block testujú H4;
- plan JSON value path a caller expression testujú H5;
- resolved module/input manifest testuje H6;
- backend/workspace/target identity testuje H7.

Atlas zistí, že pipeline refactor prestal odovzdávať `replicas`; child module použil default `2`. H3/H4 vysvetľujú plan.

### Krok 4 — contain-ni nesprávny subject

Plan `PL430` sa označí invalid a apply sa nespustí. Neopravuje sa ručným zvýšením capacity po deploymente.

### Krok 5 — obnov správny contract

Root module explicitne forwarduje `replicas`, shared module odstráni production-unsafe default a validation/policy vyžaduje explicitnú capacity hodnotu.

### Krok 6 — over outcome

```text
input provenance = prod capacity contract V33
saved plan = 6 replicas
runtime healthy replicas = 6
module output endpoint = stable
no secret value v logs/artifacts
```

### Krok 7 — skorší control

Finding sa mení na module interface fixture, required-input test a resolved value manifest porovnávaný medzi plan a apply.

## 19. Diagnostický runbook

1. Urči root/module revision, environment, plan a input subject.
2. Klasifikuj hodnotu ako public config, sensitive value, identity alebo release input.
3. Inventarizuj všetky root input sources a effective value.
4. Over required/default/optional/null semantics a custom validation.
5. Sleduj caller argument do child variable a local normalization.
6. Pri unknown hodnote nájdi upstream computed producer a graph dopad.
7. Over output type, postcondition a consumer contract.
8. Pri secret incidente revokuj provider capability a audituj state/log/artifact exposure.
9. Invaliduj stale alebo wrong-input plan pred apply.
10. Zmeň finding na type, validation, default, provenance alebo API stability control.

## 20. Referenčné pravidlá

- Variables sú caller-controlled inputs.
- Locals sú internal normalization, nie hidden override points.
- Outputs sú stabilné verejné contracts.
- Presný type je súčasť compatibility policy.
- Produkčný risk intent nemá byť skrytý v pohodlnom default-e.
- `null`, empty a omitted majú odlišnú semantics.
- `sensitive` chráni presentation, nie celý lifecycle.
- Secret reference je bezpečnejší contract než secret value.
- Collection keys sú resource identity inputs.
- Output nemá exportovať celý provider object.
- Plan a apply musia používať rovnaký effective input subject.

## 21. Časté omyly

### „Default znižuje množstvo konfigurácie“

Môže ticho nahradiť chýbajúci production intent.

### „Presný typ je iba dokumentácia“

Určuje konverziu, validation, compatibility aj collection identity.

### „Sensitive output je bezpečný secret store“

Hodnota môže zostať v state a byť exportovaná oprávneným commandom.

### „Local skryje komplexitu“

Môže skryť aj business decisions a identity transformácie pred reviewom.

### „Viac outputs je flexibilnejšie“

Export provider internals zväčšuje coupling a breaking surface.

## 22. Zhrnutie

Dôveryhodný module value lifecycle je:

```text
caller intent
→ typed a validated inputs
→ explicit source/default/null semantics
→ local normalization so stable identity
→ resource graph
→ postconditioned minimal outputs
→ versionovaný consumer contract
```

Troubleshooting nekontroluje iba declaration variable. Rekonštruuje effective source, caller forwarding, local transformáciu, unknown dependency a output consumer a overuje, že plan aj runtime použili rovnaký interface subject.

## Oficiálna dokumentácia

- [Manage values in modules](https://developer.hashicorp.com/terraform/language/values)
- [Input variables](https://developer.hashicorp.com/terraform/language/values/variables)
- [Local values](https://developer.hashicorp.com/terraform/language/block/locals)
- [Output values](https://developer.hashicorp.com/terraform/language/values/outputs)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Terraform providers, resources a data sources](terraform-providers-resources-data-sources.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Expressions a dependency graph →](expressions-and-dependency-graph.md)
<!-- KNOWLEDGE-NAVIGATION:END -->