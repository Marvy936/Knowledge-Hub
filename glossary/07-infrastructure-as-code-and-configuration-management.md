# Infrastructure as Code and Terraform glossary entries

## Address transition — Terraform

Versionovaná zmena resource alebo module instance address-y, pri ktorej má existujúci remote binding pokračovať pod novou address-ou bez neplánovaného destroy/create. Typicky sa deklaruje cez `moved` block. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Authoritative source — IaC

Systém alebo versionovaný artifact považovaný za rozhodujúcu deklaráciu požadovaného infraštruktúrneho stavu; manuálne runtime zmeny sa voči nemu musia adoptovať, vrátiť alebo explicitne vyriešiť. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md).

## Backend migration — Terraform

Riadený presun state lineage a snapshots z jedného backendu do druhého so zastavením writers, backupom, overením destination identity a následným planom. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Backend writer subject — Terraform

Presná identita state writera zahŕňajúca execution run, workload identity, backend endpoint, state key alebo workspace, lineage, prior serial, lock ID a operation purpose. Používa sa na rozlíšenie aktívneho, orphaned alebo nesprávne zacieleného writera. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Change subject — IaC

Presná identita infra zmeny zahŕňajúca source revision, resolved toolchain a dependencies, effective inputs, backend/state lineage a serial, target account/region, workload identity, saved plan a policy/approval context. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md).

## ClickOps

Primárna správa infraštruktúry manuálnymi zmenami v UI alebo konzole bez versionovaného, reviewovaného a reprodukovateľného change pathu. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md).

## Computed value — Terraform

Hodnota atribútu určená providerom alebo remote API, ktorá nemusí byť známa počas planu a môže sa zobraziť ako `known after apply`. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Consumer inventory — Terraform module

Evidencia module consumers, používaných versions, environments, owners, provider/Terraform constraints a podporovaných upgrade paths. Umožňuje bezpečné deprecation, security remediation a retirement starého contractu. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Cross-state contract

Explicitné rozhranie medzi samostatnými Terraform states, typicky cez publikované outputs alebo externý registry, ktoré musí mať ownership, compatibility a access policy. Pozri [Variables, locals a outputs](docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md).

## Data source — Terraform

Provider-defined read-only query, ktorá načíta informácie o existujúcom alebo odvodenom objekte bez správy jeho lifecycle Terraform resource bindingom. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Dependency cycle — Terraform

Kruhový vzťah v dependency grafe, pri ktorom objekt priamo alebo nepriamo závisí sám od seba a Terraform nevie zostaviť bezpečné execution poradie. Pozri [Expressions a dependency graph](docs/07-infrastructure-as-code-and-configuration-management/expressions-and-dependency-graph.md).

## Dependency graph — Terraform

Directed graph vytvorený z references, provider vzťahov a explicitných dependencies, ktorý určuje plan/apply poradie a možnú paralelizáciu objektov. Pozri [Expressions a dependency graph](docs/07-infrastructure-as-code-and-configuration-management/expressions-and-dependency-graph.md).

## Dependency lock file — Terraform

Súbor `.terraform.lock.hcl` zachytávajúci vybrané provider versions a package checksums pre reprodukovateľnejšiu inštaláciu dependencies. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Effective input subject — Terraform

Rekonštruovateľná množina root a module inputs po vyhodnotení source-u, precedence, default/null semantics, caller forwarding-u a sensitive markers, viazaná na konkrétny saved plan. Pozri [Variables, locals a outputs](docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md).

## Force unlock — Terraform

Riziková operácia odstránenia backend locku podľa lock ID bez ukončenia pôvodného procesu; smie sa použiť iba po potvrdení, že pôvodný writer už neexistuje. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Graph-shaping value — Terraform

Hodnota, ktorá určuje samotnú množinu alebo identity graph objektov, napríklad `count` alebo `for_each` keys, a preto musí byť známa pred apply. Pozri [Expressions a dependency graph](docs/07-infrastructure-as-code-and-configuration-management/expressions-and-dependency-graph.md).

## Infrastructure as Code — IaC

Správa infraštruktúry pomocou versionovanej deklarácie, automatizovaného plan/apply alebo reconciliation procesu, review, policy a auditovateľného recovery lifecycle. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md).

## Lineage — Terraform state

Jedinečný identifikátor histórie state-u používaný na rozlíšenie nezávisle vzniknutých states a ochranu pred prepísaním nesúvisiaceho snapshotu. Pozri [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## Local value — Terraform

Pomenovaná interná expression modulu dostupná cez `local.<name>`, ktorú caller nemôže priamo nastaviť. Pozri [Variables, locals a outputs](docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md).

## Module interface contract — Terraform

Versionované rozhranie modulu tvorené typovanými inputs, validation/default/null semantics, internými identity assumptions, minimálnymi stabilnými outputs a compatibility/deprecation policy. Pozri [Variables, locals a outputs](docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md) a [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Module source subject — Terraform

Immutable identita reusable modulu zahŕňajúca registry alebo VCS source, version/tag/commit, content digest alebo provenance podľa distribution modelu, ownera a release policy. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Multi-writer race — Terraform

Concurrency stav, keď viac procesov číta rovnaký prior state a pokúša sa zapísať konfliktujúce snapshots alebo remote zmeny bez účinného locku a serialization. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Output value — Terraform

Explicitne publikovaná hodnota modulu tvoriaca jeho výstupný contract pre callerov, CLI alebo ďalšiu automatizáciu. Pozri [Variables, locals a outputs](docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md).

## Ownership adoption — Terraform

Riadené prevzatie existujúceho remote objektu do Terraform management modelu cez configuration, presný provider target, import mapping, nový state binding a reviewed post-import reconciliation. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Post-import reconciliation — Terraform

Review prvého planu po importe, ktorý rozhoduje, či sa remote hodnoty adoptujú do configuration, vrátia k desired state-u, rozdelí sa attribute ownership alebo sa chybný binding odstráni. Pozri [Lifecycle, import a moved blocks](docs/07-infrastructure-as-code-and-configuration-management/lifecycle-import-moved-blocks.md).

## Provider alias — Terraform

Pomenovanie alternatívnej konfigurácie rovnakého providera používané napríklad pre inú region, account alebo endpoint boundary. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Provider configuration — Terraform

Runtime nastavenie providera, napríklad region, endpoint alebo authentication context, ktoré resource alebo module používa na API operácie. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Provider requirement — Terraform

Deklarácia provider source addressu a povoleného version rozsahu v `required_providers`, ktorú modul potrebuje pre svoje resources a data sources. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Provider target identity — Terraform

Effective provider configuration address spolu s caller accountom, regionom, endpointom a workload identity, ktorá určuje, ktorú remote authorization a failure boundary provider API operácia zasiahne. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Remote backend — Terraform

Backend ukladajúci Terraform state mimo lokálneho working directory a podľa typu poskytujúci collaboration, locking, versioning alebo remote-operation capabilities. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Remote execution — Terraform

Model, v ktorom plan/apply nevykonáva lokálny CLI proces, ale spravovaný remote worker alebo platforma s vlastnou queue, identity, variables a policy vrstvou. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Resource address — Terraform

Jednoznačná konfiguračná adresa managed objektu vrátane module pathu, resource type/name a prípadného `count` indexu alebo `for_each` key. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Resource binding — Terraform

State mapovanie medzi Terraform resource instance addressou, provider contextom a konkrétnou remote object identity. Pozri [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## Saved plan subject — Terraform

Konkrétny plan artifact a digest viazaný na configuration, resolved dependencies, effective inputs, state lineage/serial, refresh observations, provider versions, target identity a policy/approval verdict. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md).

## Serial — Terraform state

Monotónne rastúce číslo snapshotu v jednej state lineage používané na rozpoznanie novšej verzie a ochranu pred stale overwrite. Pozri [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## Stable instance key — Terraform

Configuration-derived key s dlhodobým identity významom používaný v `for_each` addressách; jeho zmena je resource identity change a môže vyžadovať `moved` alebo state migration contract. Pozri [Expressions a dependency graph](docs/07-infrastructure-as-code-and-configuration-management/expressions-and-dependency-graph.md).

## State boundary — Terraform

Rozsah resources zdieľajúcich jeden state, lock, permissions, plan/apply lifecycle a failure blast radius. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md) a [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## State locking — Terraform

Backend-supported koordinácia, ktorá bráni súbežným Terraform write operáciám pracovať s rovnakým state-om a vytvoriť lost update alebo corruption. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## State snapshot — Terraform

Konkrétna verzia Terraform state-u obsahujúca resource bindings, known attributes, outputs a metadata ako lineage a serial. Pozri [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## State surgery — Terraform

Riadená zmena state metadata pomocou príkazov ako `state mv`, `state rm` alebo výnimočne recovery push, vykonaná s lockom, backupom, review a následným planom. Pozri [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## Supported upgrade path — Terraform module

Module ownerom deklarovaná a testovaná cesta zo staršej podporovanej version na novšiu, zahŕňajúca contract zmeny, retained moved history, provider constraints, plan assertions a runtime verification. Pozri [Modules](docs/07-infrastructure-as-code-and-configuration-management/modules.md).

## Terraform backend

Terraform Core komponent určujúci state storage a podľa backendu aj locking, workspaces alebo remote execution behavior. Pozri [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Terraform input variable

Deklarovaný vstup modulu dostupný cez `var.<name>` s type constraintom, defaultom, validation a ďalšími contract vlastnosťami. Pozri [Variables, locals a outputs](docs/07-infrastructure-as-code-and-configuration-management/variables-locals-outputs.md).

## Terraform provider

Samostatne versionovaný plugin implementujúci resource types, data sources, schemas a API operácie pre konkrétnu platformu alebo službu. Pozri [Terraform providers, resources a data sources](docs/07-infrastructure-as-code-and-configuration-management/terraform-providers-resources-data-sources.md).

## Terraform state

Persistentný model mapujúci Terraform resource addresses na remote identities a uchovávajúci metadata potrebné na ďalší plan/apply lifecycle. Pozri [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md).

## Unknown remote outcome — IaC

Failure stav, v ktorom pipeline nedostala spoľahlivý výsledok remote mutation a pred retry musí cez request IDs, provider logs, remote observation a state reconciliation určiť, či operácia neprebehla, prebehla čiastočne alebo uspela bez state commit-u. Pozri [Infrastructure as Code principles](docs/07-infrastructure-as-code-and-configuration-management/infrastructure-as-code-principles.md).

## Unknown state-write outcome — Terraform

Failure stav, keď Terraform odoslal successor snapshot, ale pre timeout alebo network partition nevie, či backend write commitol. Pred ďalším writerom treba overiť version history, lineage/serial, lock a remote mutation timeline. Pozri [Terraform state](docs/07-infrastructure-as-code-and-configuration-management/terraform-state.md) a [Remote backend a state locking](docs/07-infrastructure-as-code-and-configuration-management/remote-backend-and-state-locking.md).

## Unknown value — Terraform

Typovo známa, ale konkrétne neurčená hodnota počas planu, ktorú Terraform získa až pri apply alebo neskoršom provider read-e. Pozri [Expressions a dependency graph](docs/07-infrastructure-as-code-and-configuration-management/expressions-and-dependency-graph.md).