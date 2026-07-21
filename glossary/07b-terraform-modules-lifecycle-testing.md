# Terraform modules, lifecycle, drift and testing glossary entries

## Address refactoring — Terraform

Zmena resource alebo module addressy pri zachovaní identity toho istého remote objektu, typicky deklarovaná cez `moved` block, aby nevznikol neúmyselný destroy/create. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Advisory policy — Terraform

Policy as Code pravidlo, ktorého výsledok je viditeľný a auditovaný, ale samo neblokuje plan alebo apply. Používa sa pri kalibrácii alebo nízkom riziku. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Apply test — Terraform

Terraform test run, ktorý vykoná apply proti reálnemu alebo testovaciemu provider environmentu, vyhodnotí assertions a následne sa pokúsi vytvorenú infraštruktúru odstrániť. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Child module — Terraform

Reusable Terraform konfigurácia volaná z root alebo iného child modulu cez `module` block; jej resources sú súčasťou graphu a state-u caller root module runu. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Configuration drift — Terraform

Neželaný rozdiel medzi deklaráciami, ktoré majú reprezentovať rovnaký environment alebo policy, napríklad divergentné branches, repositories alebo neaplikované emergency zmeny. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Continuous validation — Terraform

Opakované overovanie infraštruktúrnych invariánt po apply pomocou checks, drift plans, asset policy, security rescanningu alebo runtime verification. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## `create_before_destroy` — Terraform

Lifecycle rule, ktorá pri replacement operácii žiada vytvorenie nového objektu pred zničením starého, ak platforma, názvy, capacity a dependencies umožnia ich súbežnú existenciu. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Drift detection cadence

Frekvencia, s akou sa pre konkrétny state alebo infra domain vykonáva refresh/plan a klasifikácia zmien podľa security, availability a change rizika. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Drift noise — Terraform

Opakovaný alebo nerelevantný plan diff spôsobený napríklad provider normalizáciou, server defaults, orderingom, timestamps alebo eventual consistency namiesto významnej ownership zmeny. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Drift reconciliation

Riadené rozhodnutie drift revertovať, adoptovať do configuration, zmeniť ownership alebo odstrániť Terraform management s následným overením state a remote výsledku. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Hard mandatory policy — Terraform

Policy as Code pravidlo blokujúce plan alebo apply bez bežného override pathu, používané pre stabilné invariants s vysokým rizikom porušenia. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## `ignore_changes` — Terraform

Lifecycle rule, ktorá pri update plánovaní ignoruje zmeny vybraných atribútov. Musí mať explicitný external owner a monitoring, pretože potláča Terraform remediation, nie existenciu driftu. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Import block — Terraform

Versionovaná configuration deklarácia mapujúca existujúci remote objekt cez provider identity na konkrétnu Terraform resource instance addressu. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Lifecycle meta-argument — Terraform

Built-in Terraform block meniaci plánovanie resource lifecycle cez pravidlá ako `create_before_destroy`, `prevent_destroy`, `ignore_changes`, `replace_triggered_by`, preconditions a postconditions. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Mock provider — Terraform test

Test double poskytujúci deterministické provider schemas a hodnoty pre native Terraform tests bez plného reálneho API behavioru; nenahrádza integration test permissions, quotas a runtime semantics. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Module composition — Terraform

Skladanie menších capability modules v root module prepájaním ich explicitných outputs a inputs do jedného dependency graphu. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Module contract — Terraform

Stabilné rozhranie reusable modulu tvorené inputs, outputs, provider requirements, behaviorom, lifecycle assumptions, compatibility policy a dokumentovanými side effects. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Module instance — Terraform

Konkrétna inštancia child module callu v graph-e, vrátane prípadného `count` indexu alebo `for_each` key v module address-e. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Module registry — Terraform

Distribučná služba publikujúca versionované Terraform modules a ich metadata pre verejnú alebo internú spotrebu; sama negarantuje bezpečnosť ani kompatibilitu modulu. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Module source — Terraform

Adresa, z ktorej Terraform počas initialization načíta child module, napríklad local path, registry alebo VCS source. Je to executable supply-chain dependency. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Module versioning — Terraform

Release a compatibility lifecycle reusable modulu zahŕňajúci version constraints, zmeny input/output contractu, provider requirements, migrations, deprecations a podporované upgrade paths. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## `moved` block — Terraform

Versionovaná deklarácia `from` a `to` addressy, ktorou Terraform zachová resource alebo module identity počas configuration refaktoringu bez state surgery v každom environment-e. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Moved history — Terraform

Sada `moved` blocks zachovaná naprieč module releases tak, aby consumers preskakujúci verzie mohli premapovať staré addresses bez neúmyselných replacements. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Plan artifact — Terraform

Uložený Terraform plan viazaný na configuration, variables, provider/module selections a prior state, ktorý má byť reviewovaný, policy-evaluovaný a následne aplikovaný ako ten istý immutable decision artifact. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Plan test — Terraform

Native Terraform test run používajúci `command = plan` na overenie plan-time contractu bez vytvorenia reálnej infraštruktúry. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Policy exception — Terraform

Časovo obmedzený a auditovaný override konkrétnej policy s ownerom, dôvodom, compensating controls, approvalom, expiration a remediation plánom. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Post-import plan — Terraform

Prvý fresh plan po vytvorení import bindingu, používaný na rozhodnutie, či configuration remote stav adoptuje, zmení alebo by nebezpečne vyvolala update či replacement. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## `prevent_destroy` — Terraform

Lifecycle rule blokujúca plánované zničenie resource, pokiaľ je pravidlo stále prítomné v configuration; nenahrádza remote deletion protection ani backup. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Provider interpretation drift

Plan rozdiel spôsobený zmenou provider schema, defaults, diff suppression alebo read normalizácie namiesto manuálnej zmeny samotného remote objektu. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Refresh-only plan — Terraform

Plan režim, ktorý ukáže zmeny state-u potrebné na zosúladenie s remote observations bez plánovania remote infraštruktúry k desired configuration. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Remote drift — Terraform

Rozdiel vzniknutý zmenou managed remote objektu mimo authoritative Terraform workflowu. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## `replace_triggered_by` — Terraform

Lifecycle rule vyžadujúca replacement resource, keď sa zmení referencovaný managed objekt alebo atribút predstavujúci explicitný lifecycle signal. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Root module — Terraform

Konfigurácia v working directory, nad ktorou sa vykonáva plan/apply; skladá child modules, vlastní environment orchestration a určuje state/backend lifecycle. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Terraform drift

Významný rozdiel medzi desired configuration, Terraform state a skutočným remote stavom, ktorý vyžaduje klasifikáciu ownershipu a vedomé reconciliation rozhodnutie. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Terraform import

Proces vytvorenia state bindingu medzi existujúcim remote objektom a deklarovanou Terraform resource addressou bez vytvorenia objektu Terraformom. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Terraform test

Native Terraform test execution definovaná v `.tftest.hcl` alebo `.tftest.json`, ktorá vykonáva plan/apply runs a assertions pre root alebo reusable module. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Terraform test file

Súbor testovacej konfigurácie načítaný Terraformom z root configuration alebo štandardne z adresára `tests`, obsahujúci runs, variables, providers, overrides a assertions. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).

## Unmanaged infrastructure — Terraform context

Remote objekt bez bindingu v danom Terraform state-e, ktorý bežný plan nemusí objaviť, pokiaľ ho explicitne nenačíta provider data source, import alebo externý asset inventory. Pozri [Drift](docs/07-infrastructure-as-code-and-configuration-management/drift.md).

## Upgrade test — Terraform module

Testovací workflow, ktorý vytvorí infraštruktúru podporovanou staršou module/provider verziou, následne vykoná upgrade plan/apply a overí compatibility, moved mappings a absence nečakaných replacements. Pozri [Terraform testing a policy](docs/07-infrastructure-as-code-and-configuration-management/terraform-testing-and-policy.md).
