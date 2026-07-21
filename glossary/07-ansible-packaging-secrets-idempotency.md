# Ansible packaging, secrets, idempotency and tool-boundary glossary entries

## Ansible collection artifact

Versionovaný distribuovateľný balík collection contentu obsahujúci roles, modules, plugins, playbooks, metadata a dokumentáciu, ktorý má byť vytvorený z testovaného commitu a spotrebovaný cez explicitnú verziu. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Ansible idempotencia

Vlastnosť automation runu, pri ktorej opakovanie s rovnakými vstupmi a požadovaným stavom nevykoná ďalšie neplánované zmeny a pravdivo reportuje no-change výsledok. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Ansible role

Reusable Ansible capability organizujúca súvisiace defaults, variables, tasks, handlers, templates, files a metadata do definovaného contractu. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Ansible Vault

Mechanizmus šifrovania Ansible variables alebo files pre ochranu citlivého obsahu at rest; nechráni automaticky plaintext počas executionu, logs ani výslednú konfiguráciu na targete. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Authoritative writer

Jediný systém alebo workflow oprávnený meniť konkrétny mutable object alebo attribute; viac writerov vytvára ownership conflict a perpetual drift. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Bootstrap configuration

Minimálna počiatočná konfigurácia potrebná na bezpečné pripojenie targetu k dlhodobému management workflowu, napríklad identity, trusted CA, management transport a inventory registration. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Break-glass secret

Silno chránený emergency credential dostupný cez auditovaný a obmedzený recovery postup, po ktorého použití nasleduje kontrola a typicky rotation. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Change budget — Ansible

Explicitný limit alebo allowlist opakovaných zmien povolených pri idempotency teste; všetky ostatné recurring changes sa považujú za chybu alebo drift. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Collection dependency — Ansible

Versionovaný vzťah collection k inej collection, ktorý ovplyvňuje resolved executable content, compatibility a supply-chain risk. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Configuration management

Riadenie požadovaného runtime stavu operačných systémov, aplikácií, zariadení alebo služieb pomocou opakovateľných a overiteľných zmien. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Convergence — configuration management

Proces, pri ktorom opakované pozorovanie a aplikovanie automation vedie target k stabilnému požadovanému stavu. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Cross-tool contract

Úzke, versionované rozhranie medzi automation systémami, napríklad Terraform outputs publikované ako inventory metadata pre Ansible, s explicitným ownershipom a compatibility policy. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Current-state detection — Ansible

Mechanizmus, ktorým module alebo workflow zistí aktuálny stav targetu pred rozhodnutím, či je potrebná zmena. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Data at rest

Dáta uložené na disku, v repository, databáze alebo inom persistentnom storage; Ansible Vault chráni tento stav, nie automaticky dáta po dešifrovaní. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Encrypted file — Ansible Vault

Súbor, ktorého celý obsah je zašifrovaný Ansible Vaultom a musí byť dešifrovaný pri načítaní alebo použití. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Encrypted variable — Ansible Vault

Jednotlivá YAML hodnota uložená ako `!vault` encrypted block v inak čitateľnom súbore. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Golden image

Versionovaný immutable machine image obsahujúci vopred zostavený a otestovaný základ systému; configuration tool môže image vytvoriť a provisioning tool nasadiť jeho konkrétnu verziu. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## `import_role`

Statické načítanie Ansible role spracované počas parse fázy, ktoré sa líši od runtime `include_role` v condition, tag a variable semantics. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## `include_role`

Dynamické načítanie Ansible role počas executionu podľa runtime contextu. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Idempotency test — Ansible

Test vykonávajúci po prvom converge ďalší run s rovnakými inputs a overujúci, že nevzniknú neplánované changes ani side effects. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Multi-writer automation

Stav, keď viac automation systémov alebo runs súbežne mení ten istý resource alebo attribute bez spoločnej ownership a concurrency policy. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md) a [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## `no_log` — Ansible

Task alebo block control obmedzujúci zobrazenie citlivých arguments a results v bežnom Ansible outpute; nechráni všetky external logs, memory ani výsledný target state. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Ownership matrix

Dokumentované priradenie authoritative writera ku každému resource alebo mutable attribute naprieč provisioning, configuration a runtime systémami. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Password-client script — Ansible Vault

Executable helper poskytujúci vault password z chráneného zdroja, typicky po autentifikácii job identity voči secret manageru. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Perpetual drift

Opakovaný konflikt, pri ktorom viac actorov striedavo prepisuje ten istý stav podľa rozdielnych desired-state deklarácií. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Provisioning

Vytváranie a lifecycle správa infraštruktúrnych resources, napríklad networks, compute, databases, load balancers a IAM objektov. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Provisioning/configuration boundary

Explicitná hranica určujúca, ktoré resources a attributes vlastní provisioning engine a ktoré configuration-management engine. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Readiness boundary

Podmienka dokazujúca, že novovytvorený resource je nielen prítomný, ale pripravený na ďalší configuration alebo deployment krok. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Rekey — Ansible Vault

Zmena passwordu alebo vault identity použitej na šifrovanie existujúceho Vault contentu; nemení automaticky samotný cieľový application credential. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Resource lifecycle engine

Automation model sledujúci identity resources a plánujúci ich create, update, replacement a destroy operácie, typicky cez dependency graph a persistentný state. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Role contract — Ansible

Verejné a prevádzkové rozhranie role tvorené inputs, defaults, outputs/facts, handlers, side effects, supported platforms, privileges, idempotency a upgrade behaviorom. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Role defaults — Ansible

Ľahko override-nuteľné public defaults uložené typicky v `defaults/main.yml`, ktoré tvoria podporované customization points role. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Role dependency — Ansible

Metadata vzťah spôsobujúci vykonanie inej role pred závislou role; pri nadmernom používaní môže skryť orchestration graph. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Role vars — Ansible

Role variables s vyššou precedence uložené typicky vo `vars/main.yml`, vhodné najmä pre interné constants namiesto bežných environment overrides. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).

## Second converge

Druhý automation run nad už nakonfigurovaným targetom používaný na overenie, že desired state je stabilný a nevznikajú recurring changes. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Secret rotation

Riadená zmena cieľového credentialu vrátane distribúcie novej hodnoty, overenia consumers a revokácie starej hodnoty. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Stable input — automation

Vstup s kontrolovanou identitou, typom a lifecycle, ktorého neočakávaná mutácia nespôsobuje nepredvídateľné recurring changes. Pozri [Ansible idempotencia](docs/07-infrastructure-as-code-and-configuration-management/ansible-idempotency.md).

## Task-oriented automation

Automation model skladajúci ordered tasks, conditions a orchestration controls nad targets namiesto univerzálneho persistentného resource graphu. Pozri [Terraform vs. Ansible](docs/07-infrastructure-as-code-and-configuration-management/terraform-vs-ansible.md).

## Vault ID — Ansible

Label priradený k encrypted Vault contentu a password source-u na oddelenie environmentov alebo security domains; sám nie je secret ani access-control mechanizmus. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## Vault password — Ansible

Secret použitý na šifrovanie a dešifrovanie Ansible Vault contentu, ktorý musí byť uložený oddelene od encrypted repository dát. Pozri [Vault](docs/07-infrastructure-as-code-and-configuration-management/vault.md).

## `requirements.yml` — Ansible

Dependency manifest používaný na deklarovanie a inštaláciu požadovaných Ansible roles alebo collections a ich version constraints. Pozri [Roles a collections](docs/07-infrastructure-as-code-and-configuration-management/roles-and-collections.md).
