# Infrastructure as Code and Configuration Management

Táto sekcia vysvetľuje deklaratívnu správu infraštruktúry a konfigurácie ako versionovaný, auditovateľný a obnoviteľný change-control systém. Prvá časť sa sústreďuje na Terraform execution model, reusable modules, bezpečné refaktoringy, drift management, testing a Policy as Code. Nasledujúca časť prejde na Ansible configuration management.

Cieľom nie je memorovať HCL alebo YAML syntax ani cloud-specific resources. Dôležité je rozumieť desired state, provider boundary, dependency graphu, resource identity, state a backendu, blast radiusu, driftu, module contracts, testovateľnosti a bezpečnému plan/apply lifecycle.

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
7. [Modules](modules.md)
8. [Lifecycle, import a moved blocks](lifecycle-import-moved-blocks.md)
9. [Drift](drift.md)
10. [Terraform testing a policy](terraform-testing-and-policy.md)

Nasledujúci blok začne Ansible časť: architecture, inventory, modules/tasks/plays/playbooks, variables/facts/templates, handlers/loops/conditionals, roles/collections, Vault, idempotencia a porovnanie Terraform vs. Ansible.

## Cieľ zvládnutia

Po dokončení Terraform časti má byť možné:

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
- chrániť state pomocou least privilege, short-lived identity, encryption, versioning, retention a auditu,
- vysvetliť root a child module, module source, contract, composition a registry model,
- navrhnúť typované module inputs, stabilné outputs, provider mappings a compatibility policy,
- vybrať primeranú module boundary podľa capability, ownershipu, lifecycle a blast radiusu,
- versionovať a bezpečne upgradovať reusable modules bez mutable source dependencies,
- používať `count` a `for_each` na module calls so stabilnou instance identitou,
- testovať examples, module releases a podporované upgrade paths,
- správne aplikovať `create_before_destroy`, `prevent_destroy`, `ignore_changes` a `replace_triggered_by`,
- rozlíšiť configuration-driven import od CLI state mutation a vykonať bezpečný post-import review,
- používať `moved` blocks na versionovaný refaktoring resource a module addresses,
- rozlíšiť `moved` block od `terraform state mv` a zachovať podporovanú moved history,
- klasifikovať remote, configuration, state, provider a dependency drift,
- používať refresh-only workflow bez automatického adoptovania nesprávneho remote stavu,
- navrhnúť scheduled drift detection, classification, ownership a reconciliation proces,
- odlíšiť drift od unmanaged infrastructure a state recovery incidentu,
- vrstviť `fmt`, `validate`, static analysis, native tests, integration tests a post-apply verification,
- používať `.tftest.hcl` plan/apply runs, assertions, mocks a izolované test environments,
- vytvoriť module upgrade testy a reprezentatívnu Terraform/provider version matrix,
- pracovať s immutable saved planom a machine-readable plan JSON ako policy evidence,
- navrhnúť Policy as Code rules, advisory/mandatory gates, exceptions a policy tests,
- prepojiť delivery tests s continuous validation, drift detection a security rescanning.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| Infrastructure as Code principles | Learning | L2 |
| Terraform providers, resources a data sources | Learning | L2 |
| Variables, locals a outputs | Learning | L2 |
| Expressions a dependency graph | Learning | L2 |
| Terraform state | Learning | L2 |
| Remote backend a state locking | Learning | L2 |
| Modules | Learning | L2 |
| Lifecycle, import a moved blocks | Learning | L2 |
| Drift | Learning | L2 |
| Terraform testing a policy | Learning | L2 |
