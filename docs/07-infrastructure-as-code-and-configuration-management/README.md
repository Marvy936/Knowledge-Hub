# Infrastructure as Code and Configuration Management

Táto sekcia vysvetľuje Terraform a Ansible ako dva rozdielne change-control systémy nad vzdialeným stavom. Terraform skladá deklarovanú konfiguráciu, provider schemas, state bindings a remote observations do dependency graphu a plánu infraštruktúrnych mutations. Ansible skladá inventory, variables, facts, reusable content a per-host execution výsledky do riadenej konfigurácie existujúcich systémov. Ani jeden nástroj nie je bezpečný iba preto, že používa HCL alebo YAML. Dôveryhodnosť vzniká až vtedy, keď exact source, inputs, target, identity, state alebo inventory generation vedú k overenému remote a business outcome-u.

Sekcia sa znovu spracúva podľa rovnakého prose-first a practical-example štandardu ako Keycloak, Security, Observability, CI/CD a GitLab. Každá kapitola musí mať dominantný mechanistický lifecycle, presný change subject, reálne HCL/YAML/CLI alebo API walkthroughy, vysvetlené proof boundaries, competing hypotheses, evidence-preserving containment, authoritative recovery a validáciu pôvodnej, zakázanej aj druhej operácie.

## Section-wide infrastructure lifecycle

```text
business alebo platform intent
→ exact ownership a mutable attribute boundary
→ versionovaný Terraform/Ansible source
→ pinned toolchain, providers, modules, collections a execution environment
→ resolved inputs, variables, inventory a target identity
→ Terraform graph/state subject alebo Ansible host/task subject
→ plan/check/diff a policy evidence
→ serialized scoped mutation
→ remote read-back, state/inventory evidence a runtime verification
→ drift, partial/unknown outcome a recovery
→ forbidden-path a second-operation validation
→ evidence closure a control-model improvement
```

Počas celej sekcie zostávajú oddelené najmä tieto states:

- repository configuration nie je remote infrastructure;
- Terraform desired state nie je Terraform state ani actual provider state;
- state lock nie je ownership ani dôkaz, že neexistuje druhý writer;
- plan je predikcia nad konkrétnym state/target subjectom, nie všeobecné povolenie aplikovať branch;
- successful provider response nemusí znamenať úspešný state commit;
- Ansible inventory source nie je resolved host graph;
- `changed: false` nie je automaticky pravdivý dôkaz idempotencie;
- encrypted Vault file nie je runtime secret management ani revocation;
- Terraform a Ansible nesmú byť súčasne authoritative writerom toho istého mutable attribute bez explicitného contractu;
- technický apply alebo playbook success nepreukazuje správny business outcome.

## Predpoklady

Odporúča sa najprv dokončiť:

- [DevOps Foundations](../00-foundations/README.md),
- [Linux and Systems](../01-linux-and-systems/README.md),
- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [Git and Automation Basics](../03-git-and-automation/README.md),
- [Testing and Software Quality](../04-testing-and-quality/README.md),
- [CI/CD and Release Engineering](../05-ci-cd-and-release/README.md),
- [GitLab](../06-gitlab/README.md).

## Authoritative poradie — aktívne kapitoly

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

Po tejto sekcii nasleduje [Container Fundamentals and Docker](../08-container-fundamentals-and-docker/README.md). IaC ownership, state, immutable dependencies, Linux configuration a execution-environment model tam vytvoria základ pre image, container, runtime a registry lifecycle.

## Connected learning scenarios

### `IAC-PAY-75` — nesprávny Terraform subject vytvorí druhú produkčnú infraštruktúru

Prvý blok spája IaC authority, providers/resources/data sources, values, expressions/dependency graph a Terraform state. Atlas Payments chce zmeniť `prod-eu`, ale pipeline načíta nesprávny backend key, default provider smeruje do iného regionu, data source vyberá mutable „latest“ image a subnet identity je odvodená z nestabilného list indexu. Plan nad prázdnym state-om vyzerá ako legitímny create a apply vytvorí druhú sieť skôr, než zlyhá state commit.

```text
business intent prod-eu
→ source a variable set
→ nesprávny backend/state subject
→ default provider v inom regione
→ mutable data-source result
→ unstable resource keys
→ create graph nad prázdnym state-om
→ remote objects vzniknú
→ state write zlyhá
→ duplicate a orphaned infrastructure
```

Blok musí uzavrieť exact configuration/provider/input/state/target subject, rozdiel medzi managed resource a read-only query, stable instance identity, graph edges, unknown values, remote read-back a binding recovery.

### `IAC-PAY-76` — backend, module a address migration rozbijú ownership

Druhý blok spája remote backend/locking, modules a lifecycle/import/moved blocks. Shared module sa publikuje cez mutable ref, backend migration prebehne bez lineage/serial verifikácie a refactor presunie stateful database do child modulu bez `moved` contractu. Paralelný pipeline použije starý backend a stale module graph; jeden run plánuje replacement, druhý drží lock nad iným state subjectom.

```text
state/module ownership intent
→ backend a module source resolution
→ lineage/serial a lock
→ old a new configuration addresses
→ import/move/lifecycle decision
→ remote mutation alebo binding-only transition
→ state commit a upgrade compatibility
```

Acceptance musí rozlíšiť lock od správneho state targetu, module contract od state boundary, remote lifecycle zmenu od binding migration a configuration-driven refactor od ad-hoc state surgery.

### `IAC-PAY-77` — drift a policy gate schvália nesprávnu realitu

Tretí blok spája drift a Terraform testing/policy. Incident controller dočasne otvorí diagnostický endpoint, scheduled drift job nepozná emergency ownership transfer a automaticky ho odstráni. Zároveň mock plan test prejde, ale real provider apply zlyhá na organization policy. Policy engine outage sa normalizuje na prázdny report a pipeline interpretuje „žiadne findings“ ako pass.

```text
expected authority a risk model
→ observed configuration/state/remote delta
→ drift classification
→ static, plan, apply a runtime evidence
→ policy verdict alebo missing evidence
→ reconciliation, adoption, exception alebo containment
→ second no-op plan a business verification
```

Blok musí odlíšiť harmful drift od delegated mutation, clean result od missing/tool-error evidence a plan-time policy od real provider/runtime acceptance.

### `IAC-PAY-78` — Ansible trafí správny playbook na nesprávne hosty

Štvrtý blok spája Ansible architecture, inventory, modules/tasks/plays/playbooks, variables/facts/templates a handlers/loops/conditionals. Dynamic inventory cache vráti stale production membership, group precedence prepíše environment-specific port, stale fact vyberie nesprávny template branch a handler sa flushne po partial batch failure. Play recap je zelený pre preživšie hosty, no časť fleet zostane na starej konfigurácii.

```text
change intent
→ inventory sources a cache generation
→ resolved host graph a variables
→ play/task/module execution subject
→ per-host changed/failed/unreachable/skipped evidence
→ handler a batch transition
→ service/runtime read-back
→ rerun a convergence verification
```

Acceptance musí preukázať target count, host identities, variable provenance, fact freshness, template determinism, pravdivý changed signal, batch/failure semantics a druhý converge run.

### `IAC-PAY-79` — reusable automation a secrets vytvoria dvoch writerov

Záverečný blok spája roles/collections, Vault, Ansible idempotency a Terraform-versus-Ansible boundary. Collection dependency sa resolve-ne na novší artifact, Vault rekey sa zamieňa za rotation cieľového credentialu a Ansible role mení cloud security-group attribute, ktorý zároveň spravuje Terraform. Oba nástroje sú jednotlivo „idempotentné“, no spolu oscilujú medzi dvoma desired states.

```text
capability contract a ownership
→ immutable role/collection/execution-environment graph
→ encrypted secret source a runtime credential acquisition
→ Terraform resource writer alebo Ansible configuration writer
→ converge/read-back
→ second run a cross-tool drift
→ revocation, reconciliation a ownership closure
```

Sekcia sa uzatvára až vtedy, keď každý mutable attribute, secret lifecycle a reusable dependency má jedného autoritatívneho ownera a overený second-operation outcome.

## Cieľ zvládnutia

Po dokončení sekcie má byť možné navrhnúť a diagnostikovať change chain, ktorý:

- identifikuje exact Terraform configuration, provider, module, variables, backend, state lineage/serial a target;
- rozlišuje managed resource, data source, remote object, resource address a state binding;
- používa typed variables, validations, stable locals a minimálny output contract;
- vysvetľuje unknown values, implicitné dependencies, `for_each` identity a replacement graph;
- chráni state remote backendom, lockingom, least privilege, versioningom a testovaným restore;
- vykonáva module upgrade, import, move a lifecycle zmeny bez neúmyselného replacementu;
- klasifikuje drift podľa authority a intentu namiesto automatického apply;
- vrství `fmt`, `validate`, plan/apply tests, saved plan JSON, Policy as Code a runtime verification;
- identifikuje Ansible control node, execution environment, inventory, connection, strategy a module boundaries;
- overuje resolved inventory, host variables, facts, templates, handlers a per-host outcomes;
- používa roles a collections ako versionované provider–consumer contracts;
- chápe Vault ako encryption-at-rest vrstvu, nie ako úplný runtime secret lifecycle;
- overuje idempotenciu pravdivým `changed` signalom a druhým converge runom;
- definuje Terraform–Ansible handoff a jedného writer ownera pre každý mutable attribute;
- rieši partial a unknown outcomes evidence-preserving containmentom a authoritative recovery;
- overuje original, forbidden, alternate-target a second-operation paths.

## Revalidation completion gate

Sekcia bude označená `Ready for user review` iba po splnení všetkých podmienok:

1. všetkých 19 authoritative kapitol používa connected Keycloak-style prose a dominantný lifecycle;
2. každá kapitola definuje exact configuration, provider, state, module, host, inventory, task, secret alebo ownership subject;
3. každá kapitola obsahuje reálne HCL, Terraform CLI/JSON, Ansible YAML/CLI, shell alebo API walkthroughy tam, kde to téma umožňuje;
4. každý významný output vysvetľuje, čo preukazuje a čo nepreukazuje;
5. configured, resolved, planned, applied, state-recorded, effective, runtime a business states sa nezlievajú;
6. komplexné failures používajú competing hypotheses, discriminating evidence a evidence-preserving containment;
7. recovery obsahuje authoritative mutation alebo binding reconciliation a allowed, forbidden aj second-operation validation;
8. strict learning-depth audit pre všetkých 19 kapitol je `0/0/0` a practical gate nemá failures;
9. README, navigation, glossary a centrálny review ledger sú synchronizované;
10. čistý PR head bez dočasných workflowov alebo skriptov prejde štandardným documentation workflowom.

## Aktuálny stav revalidácie

| Blok | Kapitoly | Stav |
|---|---:|---|
| `IAC-PAY-75` — Terraform authority, graph a state binding | 0/5 | In progress |
| `IAC-PAY-76` — backend, modules a address/lifecycle migration | 0/3 | Not started |
| `IAC-PAY-77` — drift, testing a policy | 0/2 | Not started |
| `IAC-PAY-78` — Ansible execution, inventory a configuration | 0/5 | Not started |
| `IAC-PAY-79` — reusable content, secrets, idempotency a ownership | 0/4 | Not started |

Celkový authoritative stav: **0/19 · In progress**.
