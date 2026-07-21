# Infrastructure as Code and Configuration Management

Táto sekcia vysvetľuje deklaratívnu správu infraštruktúry a konfigurácie ako versionovaný, auditovateľný a obnoviteľný change-control systém. Prvá časť sa sústreďuje na Terraform execution model; nasledujúca časť rozšíri tému o modules, lifecycle, import, drift, testing, Policy as Code a Ansible configuration management.

Cieľom nie je memorovať HCL syntax alebo cloud-specific resources. Dôležité je rozumieť desired state, provider boundary, dependency graphu, resource identity, state a backendu, blast radiusu, driftu, module contracts a bezpečnému plan/apply lifecycle.

## Predpoklady

Odporúča sa najprv dokončiť:

- [DevOps Foundations](../00-foundations/README.md),
- [Linux and Systems](../01-linux-and-systems/README.md),
- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [Git and Automation Basics](../03-git-and-automation/README.md),
- [Testing and Software Quality](../04-testing-and-quality/README.md),
- [CI/CD and Release Engineering](../05-ci-cd-and-release/README.md),
- [GitLab](../06-gitlab/README.md).

## Odporúčané poradie

1. [Infrastructure as Code principles](infrastructure-as-code-principles.md)
2. [Terraform providers, resources a data sources](terraform-providers-resources-data-sources.md)
3. [Variables, locals a outputs](variables-locals-outputs.md)
4. [Expressions a dependency graph](expressions-and-dependency-graph.md)
5. [Terraform state](terraform-state.md)
6. [Remote backend a state locking](remote-backend-and-state-locking.md)

Nasledujúci Terraform blok doplní modules, lifecycle, import a `moved` blocks, drift, Terraform testing a Policy as Code. Potom sekcia prejde na Ansible architecture, inventory, playbooks, variables, templates, handlers, roles, collections, Vault a idempotenciu.

## Cieľ zvládnutia

Po dokončení aktuálneho bloku má byť možné:

- vysvetliť Infrastructure as Code ako change-control a reconciliation model, nie iba automatizačný skript,
- rozlíšiť deklaratívny a imperatívny prístup, desired state, actual state a Terraformom známy state,
- vysvetliť idempotenciu, reproducibility, drift, blast radius a authoritative source,
- navrhnúť version-control, review, plan, policy, apply a verification workflow,
- rozdeliť infraštruktúru na state boundaries podľa ownershipu, lifecycle, security a failure domain,
- rozlíšiť Terraform Core, provider, backend a remote platform responsibilities,
- deklarovať a bezpečne versionovať provider requirements, configurations, aliases a dependency lock file,
- rozlíšiť managed resource a read-only data source,
- vysvetliť resource address, remote identity, computed values a replacement behavior,
- používať implicitné dependencies a rozpoznať prípady, keď je legitímny explicitný `depends_on`,
- navrhnúť variables s presnými type constraints, validation, null semantics a bezpečným sensitive handlingom,
- používať locals na pomenovanie interných expressions bez skrytia neprimeranej business logiky,
- publikovať stabilné module outputs bez coupling-u na celý provider resource object,
- vysvetliť Terraform expressions, unknown values, plan-time a apply-time hodnoty,
- používať conditionals, `for` expressions, functions, dynamic blocks, `count` a `for_each` s vedomým identity modelom,
- diagnostikovať dependency graph, cycles, nečakanú serializáciu a graph-shaping unknown values,
- vysvetliť účel Terraform state, resource bindings, lineage, serial a state snapshots,
- bezpečne používať inspection a state-surgery príkazy s backupom, lockom a následným planom,
- navrhnúť state backup a recovery postup vrátane testovaného restore,
- rozlíšiť local a remote backend, remote state storage a remote execution,
- vysvetliť backend initialization, migration, partial configuration a environment isolation,
- navrhnúť state locking, CI concurrency, force-unlock a network-partition recovery model,
- chrániť state pomocou least privilege, short-lived identity, encryption, versioning, retention a auditu.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Infrastructure as Code principles | Learning | L2 |
| Terraform providers, resources a data sources | Learning | L2 |
| Variables, locals a outputs | Learning | L2 |
| Expressions a dependency graph | Learning | L2 |
| Terraform state | Learning | L2 |
| Remote backend a state locking | Learning | L2 |
