# Infrastructure as Code and Configuration Management

Táto sekcia vysvetľuje deklaratívnu správu infraštruktúry a konfigurácie ako versionovaný, auditovateľný a obnoviteľný change-control systém. Prvá časť pokrýva Terraform execution model, state, modules, bezpečné refaktoringy, drift management, testing a Policy as Code. Druhá časť aplikuje rovnaké princípy na Ansible control node, inventory, playbooks, variables, templates, reusable content, secrets a idempotentnú konfiguráciu.

Cieľom nie je memorovať HCL alebo YAML syntax ani cloud-specific resources. Dôležité je rozumieť desired state, provider a connection boundaries, dependency graphu, resource a host identity, state, inventory, blast radiusu, driftu, reusable contracts, testovateľnosti a bezpečnému execution lifecycle.

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
11. [Ansible architecture](ansible-architecture.md)
12. [Inventory](inventory.md)
13. [Modules, tasks, plays a playbooks](modules-tasks-plays-playbooks.md)
14. [Variables, facts a templates](variables-facts-templates.md)
15. [Handlers, loops a conditionals](handlers-loops-conditionals.md)
16. [Roles a collections](roles-and-collections.md)
17. [Vault](vault.md)
18. [Ansible idempotencia](ansible-idempotency.md)
19. [Terraform vs. Ansible](terraform-vs-ansible.md)

Po tejto sekcii nasleduje [Container Fundamentals and Docker](../08-container-fundamentals-and-docker/README.md). Terraform resource lifecycle, Ansible host configuration, Linux namespaces/cgroups a artifact/registry princípy tam vytvoria základ pre pochopenie images, containers, runtime a Docker build/deployment modelu.

## Cieľ zvládnutia

Po dokončení sekcie má byť možné:

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
- prepojiť delivery tests s continuous validation, drift detection a security rescanning,
- vysvetliť Ansible control node, managed node, agentless execution, inventory, modules, plugins a collections,
- rozlíšiť action, connection, strategy, callback a inventory plugin responsibilities,
- navrhnúť bezpečný connection, privilege-escalation, concurrency, batch a execution-environment model,
- diagnostikovať unreachable host, module/runtime failure, incorrect targeting a non-idempotent change reporting,
- vytvoriť static alebo dynamic inventory so stabilnou host identity, groups a explicitným variable ownershipom,
- používať inventory patterns, `--limit`, cache a constructed groups bez neúmyselného rozšírenia target scope-u,
- overovať resolved inventory graph, host variables, target count a environment isolation pred produkčným runom,
- rozlíšiť module, action plugin, task, play a playbook a interpretovať per-host `changed`, `failed`, `skipped` a `unreachable` výsledky,
- používať FQCN, structured arguments, registers, `changed_when`, `failed_when`, blocks, delegation a controlled error handling,
- rozlíšiť static imports a dynamic includes a navrhnúť check/diff, tags, batching a idempotency verification workflow,
- vysvetliť variable sources, scope a precedence a vytvoriť stabilný role/inventory variable contract,
- používať facts, fact cache, magic variables a registered values s explicitným freshness a coupling modelom,
- vytvárať deterministické Jinja templates s validáciou, bezpečnou serializáciou, atomic update a secret-aware loggingom,
- používať `when`, tests, loops, `loop_control`, retry/`until` a registered loop results bez skrytého partial state-u,
- navrhnúť handlers, notifications, `listen` topics, deduplication a flush/failure správanie podľa správneho changed signal-u,
- navrhnúť Ansible role contract, namespaced variables, defaults, handlers, dependencies a supported platform matrix,
- rozlíšiť role od collection a bezpečne versionovať collection artifacts, dependencies a execution environments,
- používať FQCN, immutable collection versions a supply-chain review pre external automation content,
- vysvetliť, čo Ansible Vault chráni a prečo encryption at rest nenahrádza runtime secret management,
- navrhnúť vault IDs, password sources, `no_log`, diff protection, rotation a break-glass lifecycle,
- rozlíšiť encryption-key rekey od rotation cieľového credentialu,
- vytvárať idempotentné modules/tasks/templates a pravdivý `changed` signal bez skrývania side effects,
- overiť idempotenciu cez druhý converge run a diagnostikovať recurring change, partial failure a ownership conflict,
- rozlíšiť idempotenciu, convergence a reproducibility,
- porovnať Terraform resource lifecycle/state/graph model s Ansible inventory/task/configuration modelom,
- definovať provisioning/configuration boundary a jedného authoritative writera pre každý mutable attribute,
- navrhnúť hybridný Terraform–Ansible pipeline, inventory contract, readiness gate a recovery workflow.

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
| Ansible architecture | Learning | L2 |
| Inventory | Learning | L2 |
| Modules, tasks, plays a playbooks | Learning | L2 |
| Variables, facts a templates | Learning | L2 |
| Handlers, loops a conditionals | Learning | L2 |
| Roles a collections | Learning | L2 |
| Vault | Learning | L2 |
| Ansible idempotencia | Learning | L2 |
| Terraform vs. Ansible | Learning | L2 |
