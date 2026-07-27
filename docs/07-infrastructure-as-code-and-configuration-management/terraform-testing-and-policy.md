# Terraform testing a policy

Terraform configuration je executable specification, ktorá môže meniť identity, sieťové hranice, dáta a produkčnú dostupnosť. Dôveryhodný quality gate preto nemôže byť zoznam príkazov ani jedno manuálne čítanie planu. Musí vytvoriť subject-bound evidence, rozlíšiť chýbajúci dôkaz od čistého výsledku a preniesť rozhodnutie až k reálne aplikovanému planu a runtime outcome-u.

Táto kapitola používa jeden priebežný scenár. Atlas Payments vydáva modul `payments-database` vo verzii `4.3.0`. Zmena pridáva mandatory encryption, upravuje replica topology a presúva resource addresses cez `moved` blocks. Ten istý module release musí prejsť od statického contractu cez plan a apply testy, policy rozhodnutie, production saved plan, post-apply verification až po cleanup a continuous validation.

## 1. Dominantný model: risk-to-runtime evidence lifecycle

```text
change subject a risk model
→ expected evidence inventory
→ format/static/contract checks
→ plan a upgrade evidence
→ real provider/apply evidence
→ immutable plan subject
→ policy verdict a bounded exception
→ apply presne toho istého planu
→ runtime verification
→ cleanup verdict
→ drift a continuous validation
```

Každá vrstva odpovedá na inú otázku. Nižšia vrstva môže byť rýchlejšia, ale nesmie predstierať dôkaz, ktorý môže poskytnúť iba provider API alebo runtime.

## 2. Atlas change subject

Test a policy výsledok je dôveryhodný iba vtedy, keď je viazaný na presnú zmenu:

```text
source revision: 8c91...
module: payments-database 4.3.0
Terraform version: 1.x pinned
provider selection a checksums
resolved variables a test fixture
prior module/provider version pri upgrade teste
backend/state lineage a serial pre production plan
target account/region a workload identity
plan artifact digest
policy package version a exception set
```

Toto je **Terraform evidence subject**. Zelený test nad iným providerom, mockom, fixture alebo regenerated planom nemusí hovoriť nič o schválenom production change-i.

## 3. Expected evidence inventory

Pred spustením pipeline definuj, aké dôkazy musia existovať pre danú risk class.

Pre Atlas release je inventory:

```text
fmt verdict
validate verdict
static/security scan report
module contract plan tests
upgrade test 4.2.x → 4.3.0
real-provider apply test
post-apply database capability check
cleanup verdict
production saved plan digest
policy verdicts
required approvals alebo exceptions
post-production runtime verification
scheduled drift/continuous validation registration
```

Ak apply test job nebol vytvorený pre nesprávne `rules`, pipeline nemá „nula failures“. Má **incomplete evidence**.

Quality gate musí rozlišovať:

- pass;
- test alebo policy violation;
- tool error;
- missing/skipped evidence;
- stale evidence;
- cleanup-incomplete;
- external dependency outage.

## 4. Najlacnejšie vrstvy: format, syntax a static model

### `terraform fmt`

```bash
terraform fmt -check -recursive
```

Potvrdzuje kanonické formátovanie a znižuje diff noise. Nepotvrdzuje semantics, provider compatibility ani bezpečnosť.

### `terraform validate`

```bash
terraform init -backend=false
terraform validate
```

Kontroluje konfiguračnú konzistenciu voči dostupným schemas. Neoveruje:

- credentials a authorization;
- quotas;
- organization policy;
- remote API behavior;
- eventual consistency;
- runtime capability;
- cleanup.

### Static analysis

Scanner môže detegovať public exposure, unpinned sources, deprecated fields, secret patterns alebo organization conventions. Výsledok však závisí od:

```text
analyzer version
+ ruleset
+ resolved source visibility
+ supported provider schemas
+ baseline/exception context
```

Scanner job success nie je automaticky validný report a „nula findings“ nie je clean bez coverage evidence.

## 5. Contract invariants v konfigurácii

Niektoré pravidlá patria priamo do module contractu, pretože musia platiť pri každom použití.

### Input validation

```hcl
variable "database" {
  type = object({
    environment = string
    encrypted   = bool
    multi_az    = bool
  })

  validation {
    condition = (
      var.database.environment != "prod" ||
      (var.database.encrypted && var.database.multi_az)
    )
    error_message = "Production database must be encrypted and multi-AZ."
  }
}
```

### Preconditions a postconditions

```hcl
resource "example_database" "this" {
  # ...

  lifecycle {
    precondition {
      condition     = var.replica_count >= 2
      error_message = "At least two replicas are required."
    }

    postcondition {
      condition     = self.encrypted
      error_message = "Provider returned an unencrypted database."
    }
  }
}
```

Precondition chráni known assumption pred operáciou. Postcondition overuje provider result dostupný v Terraform evaluation modeli. Ani jedna automaticky nedokazuje, že aplikácia sa k databáze pripojí a vykoná transakciu.

### `check` blocks

Check môže poskytovať kontinuálny health signal bez rovnakého blocking behavioru. Kritický invariant, ktorý musí zastaviť apply, nesmie byť chránený iba non-blocking checkom.

## 6. Native test lifecycle

Terraform test files používajú `*.tftest.hcl` alebo `*.tftest.json` a spúšťajú sa cez:

```bash
terraform test
```

Test run musí mať jasný subject:

```text
test fixture
→ module/provider versions
→ command plan alebo apply
→ expected assertions
→ target identity
→ generated resources
→ cleanup state
```

### Plan test

```hcl
run "production_plan" {
  command = plan

  variables {
    environment   = "prod"
    encryption    = true
    replica_count = 3
  }

  assert {
    condition     = output.replica_count == 3
    error_message = "Production topology is incorrect."
  }
}
```

Plan test je vhodný pre:

- typed input a validation behavior;
- conditional resource inventory;
- stable `for_each` identities;
- tags a known arguments;
- output contract;
- expected replacement alebo no-replacement intent.

Nemôže spoľahlivo overiť apply-time unknowns, reálne permissions, quotas, provider defaults a runtime reachability.

### Apply test

Apply test vytvorí reálne resources v disposable environment-e. Dokáže pozorovať:

- provider create/update/delete behavior;
- organization policy a IAM;
- API normalization;
- eventual consistency;
- reálne outputy;
- network a service capability.

Potrebuje izolovaný account/project, short-lived identity, unique namespace, resource limits, TTL a recovery ownera.

## 7. Worked failure: mock green, provider apply zlyhá

Atlas mock test nastaví `encrypted = true` a všetky assertions prejdú. Reálny provider apply v test account-e však zlyhá, pretože organization policy vyžaduje customer-managed key a test identity nemá oprávnenie key použiť.

Mechanizmus:

```text
mock reprodukuje iba explicitne namodelované attributes
→ nepozná organization policy ani authorization
→ module expressions sú správne
→ remote mutation je neautorizovaná
```

Záver nie je „mocky sú zlé“. Mock je vhodný pre module logiku, ale risk provider/API boundary vyžaduje aspoň reprezentatívnu integration vrstvu.

Portfólio môže používať:

```text
mock provider
→ plan s reálnou schema
→ apply v disposable targete
→ read-only external capability verification
```

## 8. Assertions a oracle fidelity

Dobrá assertion overuje stabilný contract:

- resource inventory a identity keys;
- zakázanú kombináciu;
- security invariant;
- minimálny output contract;
- dokumentovaný replacement behavior;
- runtime capability z nezávislého observation pointu.

Krehká assertion porovnáva:

- celý serializovaný provider object;
- exact human-readable plan text;
- náhodné IDs;
- ordering bez contract významu;
- provider default, ktorý modul negarantuje.

Oracle musí byť na správnej vrstve. Terraform state môže potvrdiť `status = available`, ale aplikačný smoke test musí potvrdiť, že Payments API vytvorí a načíta testovaciu transakciu.

## 9. Upgrade test ako stateful scenár

Reusable module musí testovať podporovaný upgrade path:

```text
apply payments-database 4.2.x
→ zachovaj remote objects a state
→ upgrade module/provider na 4.3.0
→ fresh plan
→ over moved mappings, defaults a replacements
→ apply
→ runtime verify
→ second no-op plan
→ cleanup
```

Tento test zachytí chyby, ktoré clean-room apply novej verzie neuvidí:

- chýbajúce `moved` blocks;
- zmenu `for_each` keys;
- incompatible output types;
- nový unsafe default;
- provider state migration;
- nečakaný replacement stateful resource.

## 10. Worked failure: chýbajúci moved mapping

Clean apply modulu `4.3.0` prejde. Upgrade z `4.2.4` však plánuje zničenie a vytvorenie databázy, pretože resource sa presunul do child module bez `moved` blocku.

```text
clean install test
→ neobsahuje starú address a binding history
→ nový graph je interne správny
→ upgrade consumer vidí old removed + new added
→ replacement risk zostane neodhalený
```

Preto test inventory musí obsahovať podporované upgrade paths, nie iba najnovšiu verziu na prázdnom state-e.

## 11. Test isolation a cleanup verdict

Každý apply test potrebuje:

- unique run ID a naming prefix;
- samostatný state;
- isolated identity a target;
- bounded network exposure;
- resource count/cost limits;
- TTL;
- destroy attempt a výsledok;
- janitor alebo manual recovery path.

`terraform test` sa môže pokúsiť cleanup vykonať, no provider/API failure môže zanechať resources.

### Worked failure: zelený test, verejný bucket zostal

Assertions prejdú, ale cleanup zlyhá na bucket-e s objektom vytvoreným externým verifierom. Pipeline označí test ako success a zahodí state artifact.

Dôsledok:

```text
functional assertions pass
+ destroy incomplete
+ owner/state evidence lost
→ public test resource prežíva bez TTL a inventory
```

Celkový verdict musí byť `cleanup-incomplete`, nie plný success. Zachovaj state, resource IDs, logs a ownera; zastav konfliktné runs a vykonaj riadený cleanup.

## 12. Flakiness ako failure model

Terraform tests môžu byť flaky pre:

- eventual consistency;
- API throttling;
- mutable data sources;
- shared test target;
- name collisions;
- provider incident;
- fixed sleeps;
- residue po predchádzajúcom cleanup failure.

Fixed sleep nahrádza observation náhodným čakaním. Preferuj condition-based retry:

```text
poll konkrétny invariant
→ bounded timeout
→ record last observed state a request IDs
→ fail s recovery evidence
```

Quarantine testu potrebuje ownera, dôvod, expiráciu a alternatívny risk control. Permanentne ignorovaný flaky test je missing evidence.

## 13. Saved plan ako rozhodovací subject

Production workflow má zachovať identitu medzi review a apply:

```text
terraform plan -out=tfplan
→ digest a subject metadata
→ machine-readable policy evaluation
→ risk review/approval
→ terraform apply tfplan
```

Saved plan je viazaný na:

- configuration revision;
- provider/module selections;
- effective variables;
- refreshed observations;
- state lineage/serial;
- target identity.

Plan môže obsahovať sensitive hodnoty. Potrebuje restricted access, integrity protection a krátku retention.

Apply, ktorý plan znovu implicitne prepočíta, nevykonáva pôvodne schválené rozhodnutie.

## 14. Machine-readable plan a policy input

```bash
terraform show -json tfplan > tfplan.json
```

Policy consumer musí rozumieť:

- resource address a action sequence;
- `before`, `after` a unknown values;
- sensitive markers;
- replacement reasons;
- prior state a configuration metadata;
- environment a identity context.

Human-readable plan text nie je stabilné API.

Policy môže vyhodnocovať:

```text
source/configuration
+ resolved module/provider metadata
+ plan JSON
+ environment classification
+ change ticket a identity
+ external asset/risk data
```

Policy nad source nevidí všetky resolved values. Policy nad planom nemusí vidieť apply-time unknown alebo runtime business behavior. Policy coverage musí byť explicitná.

## 15. Policy verdict a exception lifecycle

Policy levels:

- **advisory** — signalizuje, neblokuje;
- **soft mandatory** — blokuje defaultne, povoľuje autorizovanú výnimku;
- **hard mandatory** — nemá bežný override path.

Exception nie je voľný text „approved“. Musí obsahovať:

```text
policy ID a version
affected plan/resource subject
business a technical dôvod
risk owner a approver
compensating controls
scope
environment
expiry
remediation plan
```

Permanentný globálny bypass vytvára governance drift.

Policy package potrebuje vlastné tests pre compliant/non-compliant fixtures, unknown fields, schema zmeny, boundary values a exception behavior.

## 16. Worked failure: policy engine outage sa interpretuje ako clean

Production plan pridáva public listener. Policy job nedokáže stiahnuť policy bundle a skončí s tool errorom. Pipeline wrapper však generuje prázdny report a gate ho interpretuje ako „0 violations“.

Mechanizmus:

```text
policy evaluation nevznikla
→ missing/tool-error evidence sa normalizuje na empty findings
→ fail-open behavior nie je explicitný
→ nevyhodnotený plan dostane clean verdict
```

Pre kritické production policies musí gate odlišovať:

```text
valid pass
valid violation
invalid/missing report
tool/service outage
expired exception
```

Fail-open alebo fail-closed behavior patrí do change policy a musí mať incidentný fallback, nie tichú konverziu chyby na pass.

## 17. Causal troubleshooting walkthrough: green pipeline, nebezpečný production plan

Atlas review ukazuje green pipeline, ale production saved plan otvára database endpoint do internetu.

### 1. Identifikuj evidence subject

Over:

- source revision;
- module/provider versions;
- effective variables;
- plan digest;
- state lineage/serial;
- target account/region;
- policy package a exception set;
- expected evidence inventory.

### 2. Súťažiace hypotézy

1. Security scanner alebo policy job nebol vytvorený.
2. Report existoval, ale schema/processing zlyhali.
3. Policy vyhodnotila iný regenerated plan.
4. Public exposure bolo unknown pri policy čase.
5. Exception mala príliš široký scope alebo neplatnú expiráciu.
6. Module default zmenil exposure po upgrade.
7. Test fixture neobsahovala production input combination.
8. Gate interpretoval tool outage ako clean.

### 3. Diskriminačné observation points

- pipeline graph a job applicability;
- report checksum/schema/processing verdict;
- saved plan digest použitý policy aj apply jobom;
- plan JSON address/action/unknown fields;
- variable source a effective input manifest;
- exception ID, resource scope a expiry;
- module release diff a upgrade test evidence;
- policy engine logs a bundle version.

### 4. Containment

Zastav apply a zneplatni approval pre affected plan. Neopravuj problém ručným kliknutím v cloud konzole.

### 5. Recovery

- missing evidence → oprav pipeline applicability a regeneruj celý evidence set;
- wrong plan subject → vytvor nový saved plan a zopakuj review;
- unknown field → pridaj blocking invariant na skoršiu vrstvu alebo post-plan policy;
- broad exception → zúž/revoke exception;
- unsafe default → oprav module contract a upgrade tests;
- tool outage → použi schválený fail-closed/fallback workflow.

### 6. Over pôvodný outcome

Nový plan nesmie obsahovať public exposure, policy evidence musí byť complete a post-apply verifier musí nezávisle potvrdiť, že endpoint nie je verejne routovateľný.

### 7. Posuň control skôr

Pridaj regression fixture pre production mode, expected report inventory, digest binding medzi plan/policy/apply a explicitný tool-error verdict.

## 18. Post-apply verification

Provider apply success znamená, že Terraform dokončil svoj operation graph a state transition. Neznamená automaticky, že capability funguje.

Atlas overí:

```text
resource identity a effective attributes
→ DNS/TLS/network reachability
→ IAM least privilege
→ application transaction
→ monitoring a backup registration
→ fresh no-op plan
```

Externý verifier má používať samostatný observation path a podľa možnosti read-only identity.

## 19. Continuous validation

Delivery gate je point-in-time evidence. Po apply pokračuje:

- scheduled drift plan;
- check/health evaluation;
- cloud asset policy;
- vulnerability a deprecation inventory;
- backup restore tests;
- module/provider support tracking;
- runtime security/configuration verification.

Nová policy alebo provider intelligence môže zmeniť verdict už nasadeného artifactu. Potrebná je korelácia supported module releases a deployed state subjects.

## 20. Referenčný quality-gate chain

```text
fmt
→ validate
→ static/security analyzers
→ contract a plan tests
→ upgrade tests
→ real-provider apply test
→ cleanup verdict
→ production saved plan
→ policy a risk review
→ apply saved plan
→ independent runtime verification
→ continuous validation
```

Referenčné pravidlá:

- Zelený job bez validného reportu nie je evidence.
- Skipped required test je incomplete, nie pass.
- Mock test nedokazuje provider/API behavior.
- Clean install nenahrádza upgrade test.
- Cleanup je súčasť test verdictu.
- Policy musí vyhodnotiť ten istý plan, ktorý sa applyne.
- Tool outage a empty findings sú odlišné stavy.
- Exception má ownera, scope a expiráciu.
- Apply success potrebuje runtime oracle.
- Point-in-time gate nenahrádza continuous validation.

## 21. Kontrolné otázky

1. Čo tvorí Terraform evidence subject?
2. Prečo expected evidence inventory odlišuje pass od false green?
3. Ktoré riziká nevie zachytiť `terraform validate`?
4. Kedy patrí invariant do validation, plan testu alebo apply testu?
5. Prečo mock provider nedokazuje authorization a organization policy?
6. Čo zachytí upgrade test, čo clean apply neuvidí?
7. Prečo cleanup failure mení celkový test verdict?
8. Ako sa viaže policy verdict na saved plan?
9. Ako má gate interpretovať policy engine outage?
10. Čo musí potvrdiť post-apply a continuous validation?

## Glossary impact

Relevantné pojmy: Terraform evidence subject, expected evidence inventory, contract test, plan test, apply test, upgrade test, mock provider, cleanup-incomplete verdict, saved plan evidence, policy input, policy verdict, policy exception, tool-error verdict, runtime verification a continuous validation.

## Oficiálna dokumentácia

- [Testing features in Terraform](https://developer.hashicorp.com/terraform/cli/test)
- [`terraform test` command](https://developer.hashicorp.com/terraform/cli/commands/test)
- [Terraform test files](https://developer.hashicorp.com/terraform/language/files/tests)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Drift](drift.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ansible architecture →](ansible-architecture.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
