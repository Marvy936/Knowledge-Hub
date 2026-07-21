# Ansible fundamentals glossary entries

## Action plugin — Ansible

Control-node plugin, ktorý pripravuje alebo koordinuje vykonanie Ansible action, napríklad spracuje arguments, transfer files alebo remote module result. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Agentless automation — Ansible

Model, v ktorom Ansible typicky nepotrebuje dlhodobo bežiaceho agenta na managed node a používa existujúci transport alebo API; stále však vyžaduje connection, identity a runtime capabilities. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Ansible collection

Versionovaný distribuovateľný balík modules, plugins, roles, playbooks, documentation a ďalšieho executable Ansible contentu. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Ansible conditional

Expression, typicky v `when`, ktorá rozhoduje, či sa task, block alebo iný podporovaný content vykoná pre konkrétny host a item context. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## Ansible control node

Systém alebo execution environment, na ktorom beží `ansible-core`, načítava sa inventory a content, plánujú sa tasks a spravujú connections k targets. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Ansible facts

Host-scoped runtime údaje objavené o managed node, napríklad OS, addresses, filesystems alebo hardware metadata, dostupné najmä cez `ansible_facts`. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## Ansible handler

Task zaradený do handler queue na základe notification od tasku, ktorý reportoval zmenu; typicky aplikuje runtime reakciu ako reload alebo restart. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## Ansible inventory

Výsledný runtime model hosts, groups, connection metadata a variables vytvorený z jedného alebo viacerých inventory sources. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Ansible module

Executable automation jednotka implementujúca konkrétnu operáciu a vracajúca štruktúrovaný result, napríklad `changed`, `failed` a module-specific fields. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Ansible play

Časť playbooku mapujúca host pattern na ordered tasks, roles, variables, privilege a execution controls. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Ansible playbook

YAML dokument obsahujúci jeden alebo viac plays, ktorý zaznamenáva opakovateľný configuration, deployment alebo orchestration workflow. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Ansible task

Jedna deklarovaná action s module arguments a execution controls aplikovaná na relevantný host context v playi. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Ansible variable

Pomenovaná hodnota použitá na parametrizáciu playbooku, role, inventory, tasku alebo template, ktorej výsledok závisí od source, scope a precedence. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## `ansible_host`

Connection address alebo hostname použitý Ansible transportom pre inventory host, ktorý môže byť odlišný od jeho logickej identity `inventory_hostname`. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Callback plugin — Ansible

Plugin spracúvajúci execution events a výsledky pre console output, logs, profiling alebo external observability integrations. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Changed state — Ansible

Task result signal `changed: true`, ktorým module alebo custom `changed_when` oznamuje, že target state bol zmenený; používa sa aj na handler notifications. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Check mode — Ansible

Best-effort režim predikcie zmien bez ich vykonania pri modules, ktoré ho podporujú; nie je transakčnou ani saved-plan garanciou. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Connection plugin — Ansible

Plugin definujúci transport a remote execution semantics medzi control node a targetom, napríklad SSH, local, WinRM alebo network API connection. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Constructed inventory — Ansible

Inventory transformation model vytvárajúci derived variables a groups z existujúcich host metadata pomocou expressions a grouping pravidiel. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Diff mode — Ansible

Režim zobrazujúci content rozdiel pri podporovaných modules; output môže obsahovať citlivé údaje a potrebuje access a retention policy. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Dynamic include — Ansible

Reusable task, role alebo playbook content načítaný počas executionu podľa runtime contextu, na rozdiel od skoršie spracovaného static importu. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Dynamic inventory — Ansible

Inventory získaný cez plugin alebo external script z API, CMDB, cloud platformy alebo iného meniaceho sa source-u. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Execution environment — Ansible

Versionovaný runtime image alebo prostredie obsahujúce `ansible-core`, Python dependencies, collections a system tools potrebné na reprodukovateľné vykonanie automation. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Fact cache — Ansible

Cache backend uchovávajúci host facts medzi runs podľa definovanej freshness, access a invalidation policy. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## FQCN — Ansible

Fully Qualified Collection Name explicitne identifikujúci module, plugin alebo iný content cez namespace, collection a object name, napríklad `ansible.builtin.template`. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Handler notification — Ansible

Event vytvorený changed taskom cez `notify`, ktorý zaradí pomenovaný handler alebo `listen` topic do pending handler queue pre host. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## Handler deduplication — Ansible

Správanie, pri ktorom viac notifications rovnakého handlera v príslušnej handler phase vedie typicky k jednému vykonaniu handlera na host. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## `hostvars` — Ansible

Magic mapping poskytujúci prístup k host-scoped variables iných inventory hosts; jeho použitie vytvára cross-host coupling a závisí od dostupnosti dát. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## Inventory cache — Ansible

Cache výsledkov dynamic inventory discovery, ktorá znižuje API náklady, ale vytvára freshness a stale-target riziko. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Inventory group — Ansible

Pomenovaná množina inventory hosts alebo child groups používaná na targeting, topology model a group variables. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Inventory host — Ansible

Logická target identita v Ansible inventory, ktorá môže používať samostatnú connection addressu cez `ansible_host`. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## `inventory_hostname`

Stabilná logická identita hostu v Ansible inventory a host variable context-e, ktorá nemusí byť DNS alebo connection addressou. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Inventory pattern — Ansible

Expression vyberajúca hosts alebo groups pomocou union, intersection a exclusion semantics pre play alebo CLI run. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Inventory plugin — Ansible

Plugin parsujúci static alebo dynamic inventory source a vytvárajúci hosts, groups a variables v runtime inventory model-i. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Inventory source — Ansible

File, directory, plugin configuration, script alebo external source, z ktorého Ansible vytvára časť výsledného inventory. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Jinja template — Ansible

Textový template renderovaný typicky na control node v host-specific variable context-e a následne použitý ako configuration alebo iný artifact. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## `listen` topic — Ansible

Pomenovaný notification contract, na ktorý môže reagovať viac handlers bez priameho viazania notifying tasku na konkrétne handler names. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## Loop control — Ansible

Task loop metadata a správanie riadené cez `loop_control`, napríklad pomenovaný `loop_var`, label, index alebo pause. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## Magic variable — Ansible

Reserved variable poskytovaná Ansible engine-om na opis inventory alebo execution contextu, napríklad `hostvars`, `groups` alebo `inventory_hostname`. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## Managed node — Ansible

Host, zariadenie alebo API target, na ktorý Ansible aplikuje automation cez connection plugin alebo provider-specific module workflow. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Registered variable — Ansible

Host-scoped variable vytvorená cez `register`, ktorá uchováva štruktúrovaný result konkrétneho tasku pre ďalšie conditions, loops alebo reporting. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## Retry loop — Ansible

Opakovanie rovnakého tasku podľa `until`, `retries` a `delay`, určené pre bounded transient conditions, nie pre iteráciu business items. Pozri [Handlers, loops a conditionals](docs/07-infrastructure-as-code-and-configuration-management/handlers-loops-conditionals.md).

## Static import — Ansible

Reusable content spracovaný staticky pri parse phase, čím sa od dynamic include odlišuje v timing-u, listovaní, tags a variable/condition semantics. Pozri [Modules, tasks, plays a playbooks](docs/07-infrastructure-as-code-and-configuration-management/modules-tasks-plays-playbooks.md).

## Static inventory — Ansible

Inventory hosts, groups a variables deklarované v versionovanom INI alebo YAML source namiesto runtime discovery cez external API. Pozri [Inventory](docs/07-infrastructure-as-code-and-configuration-management/inventory.md).

## Strategy plugin — Ansible

Plugin určujúci, ako Ansible plánuje postup hosts cez tasks a synchronization body počas play executionu. Pozri [Ansible architecture](docs/07-infrastructure-as-code-and-configuration-management/ansible-architecture.md).

## Template validation — Ansible

Kontrola renderovaného dočasného file-u pomocou target parsera alebo validatora pred jeho nahradením na destination path. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).

## Variable precedence — Ansible

Pravidlá rozhodujúce, ktorá z viacerých definitions rovnakého variable name sa použije podľa source a explicitnosti. Pozri [Variables, facts a templates](docs/07-infrastructure-as-code-and-configuration-management/variables-facts-templates.md).
