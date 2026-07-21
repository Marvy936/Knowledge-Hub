# Terraform testing a policy

Terraform configuration je executable specification, ktorá môže meniť reálnu infraštruktúru, identity, sieťové hranice a dáta. Kvalita preto nemá stáť na jednom `terraform plan` review. Potrebuje vrstvený testovací a policy model.

Cieľom je zachytiť chyby čo najskôr, ale zároveň overiť behavior na dostatočne realistickej vrstve.

## 1. Testovací model

Praktické vrstvy:

```text
format a syntax
→ static analysis
→ validation a conditions
→ plan assertions
→ module tests
→ integration/apply tests
→ policy evaluation
→ post-apply verification
→ drift a continuous validation
```

Žiadna vrstva sama nepokrýva celý risk.

## 2. `terraform fmt`

```bash
terraform fmt -check -recursive
```

Overuje kanonické formátovanie Terraform configuration.

Poskytuje:

- konzistentný diff,
- menej review noise,
- jednoduchú automatickú opravu.

Nepotvrdzuje semantics, provider compatibility ani bezpečnosť infraštruktúry.

## 3. `terraform validate`

```bash
terraform init -backend=false
terraform validate
```

Validate kontroluje internú syntaktickú a konfiguračnú konzistenciu modulu vrátane provider schemas dostupných po init-e.

Neoveruje:

- reálne credentials,
- remote API behavior,
- quotas,
- policy compliance,
- production data a dependencies,
- či apply bude úspešný.

`-backend=false` je vhodné pre reusable module validation, keď backend nie je potrebný.

## 4. Static analysis

Doplňujúce nástroje môžu kontrolovať:

- deprecated provider arguments,
- cloud security misconfigurations,
- naming/tagging pravidlá,
- nepoužité declarations,
- module source pinning,
- unsafe public access,
- secret patterns,
- organization-specific conventions.

Každý scanner potrebuje version pinning, pravidlá, baseline, ownership a false-positive proces.

## 5. Input validation

```hcl
variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "stage", "prod"], var.environment)
    error_message = "environment musí byť dev, stage alebo prod."
  }
}
```

Input validation chráni module contract pri každom plan/apply.

Validuj najmä:

- povolené enumy,
- rozsahy,
- cross-field constraints, ak sú vyjadriteľné,
- formát identifiers,
- zakázané nebezpečné kombinácie.

Chybová správa musí vysvetliť opravu.

## 6. Preconditions a postconditions

```hcl
resource "example_database" "this" {
  # ...

  lifecycle {
    precondition {
      condition     = var.production ? var.multi_az : true
      error_message = "Production databáza musí používať multi-AZ."
    }

    postcondition {
      condition     = self.encrypted
      error_message = "Provider vrátil nešifrovanú databázu."
    }
  }
}
```

- precondition overuje predpoklad,
- postcondition overuje result alebo observed attribute,
- zlyhanie zastaví relevantný Terraform workflow.

Tieto podmienky sú súčasťou module behavioru a musia byť stabilné, zrozumiteľné a testované.

## 7. `check` blocks

Check block vyjadruje assertion, ktorú Terraform vyhodnocuje ako validation/health signal bez rovnakého blocking behavioru ako precondition alebo postcondition.

Vhodné použitie:

- dostupnosť endpointu,
- expirácia certificate,
- externý health signal,
- kontinuálna validácia infra capability.

Check nesmie byť jedinou kontrolou kritickej invariantu, ktorá musí apply zablokovať.

## 8. Native Terraform tests

Terraform test files používajú:

```text
*.tftest.hcl
*.tftest.json
```

Štandardný adresár je:

```text
tests/
```

Spustenie:

```bash
terraform test
```

Terraform načíta test files, vykoná definované plan alebo apply runs a vyhodnotí assertions.

## 9. Základ test file

```hcl
run "default_plan" {
  command = plan

  variables {
    environment = "dev"
  }

  assert {
    condition     = output.environment == "dev"
    error_message = "Module nepublikuje očakávané environment output."
  }
}
```

Plan test je rýchlejší a nevytvára remote resources, ale nevie potvrdiť provider apply behavior.

## 10. Plan tests

Vhodné pre:

- conditional resources,
- `count`/`for_each` identity,
- naming a tagging,
- output composition,
- validation failures,
- lifecycle intent,
- resource arguments známe počas planu.

Limity:

- unknown values,
- provider-side defaults,
- eventual consistency,
- permissions a quotas,
- reálny networking alebo runtime behavior.

## 11. Apply tests

Apply run vytvára reálnu alebo testovaciu infraštruktúru a môže overiť výsledný state.

Riziká:

- náklady,
- leaked resources,
- quotas,
- dlhý runtime,
- eventual consistency,
- flaky external APIs,
- security exposure.

Použi:

- izolovaný test account/project/subscription,
- unique names,
- least-privilege identity,
- budget/quotas,
- explicitný cleanup,
- TTL alebo janitor reconciler.

## 12. Cleanup

`terraform test` sa pokúša vytvorenú infraštruktúru zničiť, ale cleanup môže zlyhať.

Preto eviduj:

- test run ID,
- vytvorené resource IDs,
- ownera,
- expiry/TTL,
- destroy výsledok,
- manual recovery postup.

Zelený test s neúspešným cleanupom nie je plný success.

## 13. Mocking a overrides

Native test syntax môže podľa podporovanej Terraform verzie používať mock providers a override mechanizmy na izoláciu provider behavioru.

Vhodné sú pre:

- module expressions,
- conditions,
- output contracts,
- branch logic,
- deterministic provider values.

Nevhodné sú ako jediný dôkaz:

- IAM correctness,
- API compatibility,
- network reachability,
- actual encryption,
- quotas a runtime semantics.

Mock model môže verne reprodukovať iba behavior, ktorý autor explicitne namodeloval.

## 14. Test doubles vs. reálni providers

Portfólio:

- mock provider pre rýchlu logiku,
- reálny provider v disposable test environment-e,
- read-only verification externým API klientom,
- smoke test reálnej capability.

Čím vyššie riziko provider/API behavioru, tým viac potrebuješ reálnu integration vrstvu.

## 15. Assertions

Dobrá assertion overuje stabilný contract:

- požadovaný resource existuje,
- security invariant je splnená,
- output má očakávaný význam,
- zakázaná kombinácia zlyhá,
- replacement alebo počet instances je očakávaný.

Krehká assertion overuje:

- celé serializované resource objekty,
- provider-generated ordering,
- náhodné IDs,
- default, ktorý nie je súčasťou module contractu,
- presný text planu.

## 16. Examples ako testované rozhranie

Každý podporovaný example má byť:

- syntakticky validovaný,
- inicializovateľný,
- planovateľný s test inputs,
- zahrnutý do upgrade testov,
- dokumentovaný ako supported alebo illustrative.

Neudržiavaný example je falošná dokumentácia.

## 17. Upgrade tests

Reusable module má testovať upgrade z podporovaných predchádzajúcich versions:

```text
apply old module version
→ zachovaj state a remote objects
→ upgrade module/provider
→ plan
→ očakávaj no-op alebo dokumentovanú migration
→ apply a verify
```

Test odhalí:

- chýbajúce `moved` blocks,
- changed defaults,
- nečakané replacements,
- incompatible output types,
- provider upgrade drift.

## 18. Version matrix

Test matrix môže pokrývať:

- podporované Terraform versions,
- provider version ranges,
- module upgrade paths,
- cloud regions alebo API variants,
- významné input modes.

Vyhni sa neobmedzenému Cartesian productu. Definuj support policy a representative combinations.

## 19. Integration verification

Po apply over reálnu capability:

- API endpoint odpovedá,
- DNS/TLS je funkčné,
- IAM principal má iba očakávané permissions,
- network path je otvorená/zatvorená podľa policy,
- storage je encrypted a versioned,
- monitoring/backup je aktívny.

Terraform state môže hovoriť, že resource existuje, ale nie že business capability funguje end-to-end.

## 20. Plan artifact

V CI sa odporúča:

```text
plan
→ uložiť immutable plan artifact
→ policy/review voči tomu istému artifactu
→ apply saved plan
```

Plan artifact musí byť:

- viazaný na commit/configuration,
- viazaný na variables/provider/module selections,
- chránený ako sensitive artifact,
- krátko uchovávaný,
- invalidovaný po state alebo policy zmene.

## 21. Machine-readable plan

```bash
terraform show -json tfplan > tfplan.json
```

JSON plan umožňuje:

- policy evaluation,
- change classification,
- replacement count,
- security scanning,
- custom approvals,
- audit summary.

Consumer musí rozumieť unknown, sensitive a before/after semantics. Neparsuj human-readable text ako stabilné API.

## 22. Policy as Code

Policy as Code zapisuje governance pravidlá ako versionovaný, testovaný a automaticky vyhodnocovaný kód.

Príklady:

- povolené regions,
- mandatory encryption,
- zakázaný public access,
- required tags a owner,
- maximum blast radius,
- zákaz wildcard IAM,
- approved module sources,
- review pre destructive changes.

Policy engine môže používať Sentinel, OPA/Rego alebo inú organizáciou zvolenú implementáciu. Dôležitý je contract a lifecycle, nie značka nástroja.

## 23. Policy input

Policy môže vyhodnocovať:

- configuration,
- resolved module/provider metadata,
- plan JSON,
- state metadata,
- environment classification,
- identity a change ticket,
- external asset alebo vulnerability data.

Policy nad source textom nevidí všetky resolved values. Policy nad planom nemusí vidieť apply-time unknown alebo runtime business behavior.

## 24. Policy levels

### Advisory

Výsledok je viditeľný, ale neblokuje.

### Soft mandatory

Blokuje defaultne, ale povoľuje autorizovaný override.

### Hard mandatory

Blokuje bez bežného override pathu.

Úroveň vyber podľa stability signálu, rizika a dostupnosti recovery/exception procesu.

## 25. Policy exceptions

Exception musí obsahovať:

- policy ID,
- affected resource/change,
- business a technical dôvod,
- compensating controls,
- ownera,
- schvaľovateľa,
- expiration,
- remediation plan.

Permanentný globálny bypass vytvára governance drift.

## 26. Policy testing

Policy potrebuje vlastné tests:

- compliant input prejde,
- non-compliant input zlyhá,
- boundary values,
- unknown/missing fields,
- renamed provider/resource schemas,
- exception behavior,
- backward compatibility policy package.

Security policy bez tests môže blokovať správne zmeny alebo prepustiť nebezpečné.

## 27. Quality gate design

Typický pipeline:

```text
fmt
→ validate
→ lint/security scan
→ native tests
→ plan
→ policy evaluation
→ human review podľa risku
→ apply saved plan
→ post-apply verification
```

Gate má rozlišovať:

- tool failure,
- missing evidence,
- policy violation,
- test failure,
- external service outage.

Fail-open/fail-closed behavior musí byť explicitný.

## 28. Cost a capacity checks

Pred apply možno vyhodnotiť:

- odhad cost delta,
- quota requirements,
- replica/capacity reduction,
- expensive instance classes,
- data transfer exposure,
- resource count explosion.

Cost estimate je model, nie faktúra. Unknown usage a runtime traffic môžu výsledok výrazne zmeniť.

## 29. Drift a continuous validation

Po apply pokračuje validácia:

- scheduled drift plan,
- `check` blocks alebo platform validation,
- policy nad asset inventory,
- security rescanning,
- backup restore tests,
- module/provider deprecation inventory.

Delivery gate potvrdzuje bod v čase; neudržiava infraštruktúru správnu navždy.

## 30. Test isolation

Každý test run má mať:

- unique namespace/name prefix,
- oddelený state,
- isolated credentials,
- bounded network scope,
- resource limits,
- cleanup ownership,
- žiadne production secrets alebo data.

Paralelné tests nad rovnakým state-om alebo názvami vytvárajú race conditions.

## 31. Flaky Terraform tests

Príčiny:

- eventual consistency,
- throttling,
- mutable external data,
- shared test environment,
- name collisions,
- provider/API incidents,
- fixed sleeps,
- neúplný cleanup.

Riešenia:

- condition-based retry s timeoutom,
- unique resources,
- isolated accounts/projects,
- bounded concurrency,
- provider/version pinning,
- quarantine iba s ownerom a expiry.

## 32. Security testu

Test alebo policy job môže čítať:

- source,
- plan/state,
- cloud metadata,
- credentials,
- outputs a secrets.

Chráň:

- runner isolation,
- short-lived identity,
- egress,
- artifact access,
- logs,
- third-party actions/images,
- test cleanup permissions.

## 33. Observability

Sleduj:

- fmt/validate/test pass rate,
- test duration a flakiness,
- leaked-resource count,
- policy violation trend,
- exception age,
- plans bez policy evidence,
- apply failure rate po green plan-e,
- module upgrade failure rate,
- missing drift/continuous validation runs.

## 34. Anti-patterny

### Iba `terraform validate`

Neoveruje provider runtime ani policy.

### Snapshot celého plan textu

Krehké voči ordering-u a provider presentation zmenám.

### Apply tests v production account-e

Test failure má produkčný blast radius.

### Mocks bez integration testu

Namodelované behavior nemusí zodpovedať API.

### Policy bez exception lifecycle

Tímy začnú hľadať bypass mimo platformy.

### Apply sa vykoná znovu namiesto saved planu

Review a apply nemusia pracovať s rovnakým rozhodnutím.

## 35. Troubleshooting

### `terraform test` vytvoril resources a cleanup zlyhal

Zachovaj run/state/logs, identifikuj IDs, zastav ďalšie runs a vykonaj riadený cleanup podľa ownera a TTL procesu.

### Plan test zlyháva na unknown value

Assertion overuje apply-time atribút. Presuň ju do apply runu alebo testuj plan-time contract.

### Mock test je zelený, reálny apply zlyhá

Mock nepokrýva provider/API semantics, permissions, quotas alebo eventual consistency.

### Policy nevie nájsť očakávaný field

Over plan JSON schema, resource change address, unknown/sensitive representation a provider version.

### CI a lokálny plan sa líšia

Porovnaj Terraform/provider/module versions, variables, backend state, credentials scope a refresh čas.

## 36. Rozhodovací rámec

1. Ktoré chyby zachytí najlacnejšia vrstva?
2. Ktoré invariants patria do variable validation alebo conditions?
3. Ktoré behavior potrebuje plan test a ktoré apply test?
4. Aký reálny environment je bezpečný pre integration test?
5. Ako garantujeme cleanup a TTL?
6. Ktoré module versions a providers podporujeme?
7. Ktoré policies sú advisory, overrideable alebo hard mandatory?
8. Ako testujeme policy a exceptions?
9. Ako zabezpečíme, že reviewed plan je applied plan?
10. Aké continuous checks bežia po apply?

## 37. Kontrolné otázky

1. Čo overuje `terraform validate` a čo nie?
2. Aký je rozdiel medzi plan a apply testom?
3. Prečo môže `terraform test` vytvárať náklady?
4. Kedy použiť mock provider?
5. Čo má overovať module upgrade test?
6. Prečo je JSON plan vhodnejší pre policy než human text?
7. Aký je rozdiel medzi advisory a hard mandatory policy?
8. Čo musí obsahovať policy exception?
9. Prečo saved plan potrebuje krátku retention?
10. Ako sa testing mení na continuous validation po apply?

## Glossary impact

Relevantné pojmy: Terraform test, test file, plan test, apply test, mock provider, upgrade test, plan artifact, machine-readable plan, Policy as Code, policy exception, advisory policy, hard mandatory policy a continuous validation.

## Oficiálna dokumentácia

- [Testing features in Terraform](https://developer.hashicorp.com/terraform/cli/test)
- [`terraform test` command](https://developer.hashicorp.com/terraform/cli/commands/test)
- [Terraform test files](https://developer.hashicorp.com/terraform/language/files/tests)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Drift](drift.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
