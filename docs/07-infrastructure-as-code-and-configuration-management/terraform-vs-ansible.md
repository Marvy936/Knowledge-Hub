# Terraform vs. Ansible

Terraform a Ansible sa často označujú ako Infrastructure as Code nástroje, ale používajú odlišné execution, identity a state modely. Terraform je primárne resource lifecycle engine s persistentným state-om a dependency graphom. Ansible je primárne task-oriented automation a configuration-management engine pracujúci nad inventory targets.

Otázka preto nie je iba „ktorý nástroj je lepší“, ale:

- aký objekt a lifecycle spravujeme,
- kto vlastní desired state,
- akú identitu má resource alebo host,
- ako sa deteguje current state,
- aký recovery a drift model potrebujeme,
- kde má byť boundary medzi provisioningom a konfiguráciou.

## 1. Základné mentálne modely

### Terraform

```text
configuration
+ prior state
+ refreshed remote observations
→ dependency graph
→ plan
→ apply
→ new state
```

Terraform pracuje s resource instances, addresses, providers, remote identities a persistentným state-om.

### Ansible

```text
playbook
+ inventory
+ variables/facts
→ ordered tasks per host
→ module/API operations
→ per-task results
```

Ansible pracuje s inventory hosts alebo API targets, plays, tasks, modules a runtime results. Nemá univerzálny persistentný state mapujúci každý spravovaný objekt.

## 2. Primárna doména Terraformu

Terraform je vhodný najmä na lifecycle resources, ako sú:

- virtual networks a subnets,
- cloud compute instances,
- managed databases,
- load balancers,
- IAM resources,
- DNS records,
- Kubernetes clusters,
- SaaS alebo platform resources s providerom,
- infrastructure dependencies medzi týmito objektmi.

Silné stránky:

- resource identity,
- dependency graph,
- plan pred apply,
- create/update/delete lifecycle,
- replacement analysis,
- persistentný state,
- import a moved history,
- drift detection,
- reusable modules,
- Policy as Code nad planom.

## 3. Primárna doména Ansible

Ansible je vhodný najmä na:

- konfiguráciu operačných systémov,
- package, user, file a service management,
- application deployment,
- orchestráciu postupných krokov,
- patching a maintenance workflows,
- sieťové zariadenia,
- ad hoc alebo event-driven operations,
- post-provisioning konfiguráciu,
- cross-system runbooks.

Silné stránky:

- agentless push model,
- inventory a host grouping,
- ordered orchestration,
- conditional execution,
- loops a handlers,
- široký module/plugin ecosystem,
- configuration templating,
- jednoduché operatívne workflows,
- postupný rollout cez batches.

## 4. Declarative vs. imperative nie je binárne delenie

Terraform configuration je prevažne deklaratívna: opisuje požadované resources a relationships.

Ansible playbook je ordered sequence tasks, ale jednotlivé modules môžu byť deklaratívne:

```yaml
- name: Ensure service is running
  ansible.builtin.service:
    name: example
    state: started
```

Ansible teda kombinuje:

- deklaratívny module state,
- imperatívnejšie task ordering,
- orchestration controls.

Terraform tiež môže obsahovať sekvenčné alebo imperatívne prvky cez provisioners alebo external scripts, ale tie oslabujú jeho resource model.

## 5. State model

### Terraform state

Terraform state mapuje:

```text
resource address
→ provider context
→ remote object identity
→ known attributes
```

State je základ ďalšieho plan/apply lifecycle.

### Ansible state

Ansible typicky načíta current state pri každom module tasku:

```text
module arguments
→ inspect target
→ decide whether change is required
→ return changed/failed/result
```

Persistentné dáta môžu existovať ako:

- inventory,
- fact cache,
- external CMDB,
- application migration ledger,
- controller job history,
- resource-specific API state.

Nie je to však univerzálny Terraform-like binding model.

## 6. Resource identity

Terraform potrebuje stabilnú resource addressu a remote identity.

Príklad:

```text
module.network.aws_subnet.private["eu-central-1a"]
```

Ansible inventory používa stabilnú host identity:

```text
inventory_hostname = web-01
ansible_host = 10.20.1.11
```

Ansible task môže navyše pracovať s resources v module/API bez trvalého globálneho address mappingu.

Rozdiel ovplyvňuje refaktoring, import, drift aj replacement behavior.

## 7. Dependency model

### Terraform graph

References vytvárajú directed dependency graph:

```text
network
→ subnet
→ load balancer
→ service
```

Terraform môže nezávislé vertices vykonávať paralelne.

### Ansible order

Ansible používa najmä:

- poradie tasks,
- plays,
- role/import/include composition,
- handlers,
- per-host strategy,
- `serial`, `throttle` a delegation.

Dependency je často zapísaná explicitným workflow orderingom, nie odvodená z data references.

## 8. Plan model

### Terraform plan

Plan je explicitný model navrhovaných resource actions:

- create,
- update in place,
- replace,
- destroy,
- read,
- output changes.

Saved plan môže byť reviewovaný artifact, hoci zostáva citlivý a časovo viazaný na state a inputs.

### Ansible check mode

Ansible `--check` je best-effort predikcia podľa podpory konkrétnych modules.

```bash
ansible-playbook site.yml --check --diff
```

Nie je to transakčný saved plan. Niektoré modules:

- check mode nepodporujú,
- task preskočia,
- nevedia predikovať runtime výsledok,
- potrebujú reálne API side effects.

Terraform plan a Ansible check mode preto nie sú ekvivalentné assurances.

## 9. Drift

### Terraform

Refresh porovná remote objects so state-om a configuration. Drift sa objaví v plane.

### Ansible

Drift sa zistí pri ďalšom module run-e alebo samostatnej validation kontrole:

```text
expected file content
≠ actual file content
→ changed task
```

Ansible nemá automaticky centralizovaný report všetkého driftu, pokiaľ ho nevytvorí scheduled run, audit alebo external inventory/compliance systém.

## 10. Idempotencia

Terraform sa snaží dosiahnuť no-op plan pri zhode configuration, state a remote reality.

Ansible sa snaží dosiahnuť druhý converge run bez nečakaných changes.

Oba modely môžu zlyhať pri:

- unstable provider/module behavior,
- mutable external inputs,
- eventual consistency,
- ownership konflikte,
- nebezpečných scripts,
- nesprávnom current-state detection.

## 11. Provisioning a configuration management

Typická boundary:

### Terraform vlastní

- network,
- instance/VM lifecycle,
- security groups,
- managed service resources,
- load balancer,
- DNS,
- IAM identity a role bindings,
- cluster alebo platform primitives.

### Ansible vlastní

- OS packages,
- system users,
- service configuration,
- application files,
- agents,
- certificates podľa určeného lifecycle,
- service restart/reload,
- host-level verification.

Boundary nie je absolútna. Dôležité je, aby jeden object attribute nemal dvoch authoritative writers.

## 12. Host bootstrap

Príklad hybridného workflowu:

```text
Terraform creates VM
→ cloud-init establishes minimum bootstrap
→ host registers in inventory/CMDB
→ Ansible configures OS and application
→ verification
```

Bootstrap má zabezpečiť iba minimum potrebné na bezpečnú správu:

- identity/SSH alebo management channel,
- trusted CA,
- base package/runtime podľa potreby,
- inventory registration,
- security baseline potrebný pred prvým Ansible runom.

Neukladaj celý dlhodobý configuration lifecycle do jednorazového user data scriptu.

## 13. Terraform provisioners

Terraform provisioners ako remote-exec môžu spúšťať scripts alebo configuration počas resource lifecycle.

Riziká:

- side effect nie je plnohodnotný resource,
- slabý state a retry model,
- partial failure,
- tajné údaje v plan/state/logoch,
- tight coupling infrastructure create s host configuration,
- náročný re-run bez replacementu resource.

Provisioner používaj ako výnimočný bootstrap alebo bridge, nie ako náhradu Ansible architecture.

## 14. Ansible na provisioning resources

Ansible collections obsahujú cloud a platform modules schopné vytvárať resources.

To môže byť vhodné pre:

- krátke orchestration workflows,
- operatívne one-shot actions,
- platformu bez vhodného Terraform providera,
- workflow, kde persistentný Terraform state nie je žiaduci,
- API operation viazanú na širší runbook.

Pri dlhodobom resource lifecycle si polož otázky:

- kde je resource identity?
- ako sa plánuje destroy/replacement?
- ako sa deteguje drift?
- ako sa importuje existujúci object?
- ako sa chráni concurrent writer?
- ako sa reviewuje proposed change?

## 15. Immutable infrastructure

Terraform prirodzene podporuje model, kde sa infra resources nahrádzajú novými.

Ansible prirodzene podporuje mutable in-place configuration, ale môže sa používať aj pri image build pipeline:

```text
Ansible configures image builder VM
→ image artifact created
→ Terraform deploys immutable instances from image
```

Tento model oddeľuje:

- image construction,
- infrastructure deployment,
- runtime configuration.

## 16. Golden image pattern

Ansible môže vytvoriť alebo nakonfigurovať image počas build pipeline. Terraform potom nasadí konkrétny image ID/version.

Výhody:

- rýchlejší a predvídateľnejší startup,
- menší runtime configuration drift,
- testovateľný artifact,
- jednoduchšia replacement stratégia.

Runtime Ansible stále môže spravovať malé množstvo environment-specific configuration, ale nemá meniť základ image bez jasného ownershipu.

## 17. Inventory integrácia

Terraform outputs možno publikovať do inventory alebo CMDB:

```text
Terraform state/output
→ stable integration contract
→ dynamic inventory
→ Ansible target selection
```

Nevhodný model:

```text
Ansible číta celý citlivý Terraform state
→ závisí od interných addresses a všetkých attributes
```

Preferuj úzky contract:

- hostname/ID,
- management address,
- environment,
- role/group metadata,
- region,
- immutable deployment identity.

## 18. Pipeline ordering

Bezpečný hybridný pipeline:

```text
terraform validate/test
→ terraform plan + policy
→ approval
→ terraform apply
→ wait for readiness
→ publish/update inventory
→ ansible syntax/lint/check
→ ansible canary converge
→ ansible rollout
→ verification
```

Každý krok potrebuje:

- vlastnú identity,
- scoped permissions,
- explicitné artifacts,
- failure a retry behavior,
- audit trail.

## 19. Failure boundaries

### Terraform apply failure

Môže zanechať partial resource changes a nový alebo neúplný state update.

### Ansible failure

Môže zanechať niektoré hosts alebo tasks zmenené a iné nezmenené.

Hybridný recovery musí vedieť:

- či infrastructure resource existuje,
- či je host reachable a ready,
- ktoré Ansible tasks prebehli,
- či handler prebehol,
- či možno run bezpečne zopakovať,
- či treba replacement alebo in-place repair.

## 20. Concurrency

Terraform backend lock typicky serializuje writes nad jedným state-om.

Ansible potrebuje concurrency control podľa resource a workflowu:

- controller job lock,
- deployment lock,
- `serial`,
- `throttle`,
- resource-specific mutex,
- API idempotency key.

Terraform lock nechráni Ansible run a Ansible controller lock nechráni manuálny Terraform apply.

## 21. Secrets

### Terraform

Secrets môžu skončiť v:

- variables,
- plans,
- state,
- provider request/response,
- outputs,
- logs.

### Ansible

Secrets môžu skončiť v:

- variables/Vault,
- module arguments,
- templates,
- target files,
- callback logs,
- registered results.

Používaj external secret manager, short-lived identities a presný runtime scope. `sensitive` ani `no_log` nie sú encryption a access-control náhradou.

## 22. Testing

### Terraform testing

- `fmt`,
- `validate`,
- static/IaC scanning,
- native tests,
- plan assertions,
- policy,
- integration apply tests,
- drift/continuous validation.

### Ansible testing

- YAML/syntax/lint,
- role/unit/plugin tests,
- isolated converge,
- assertions,
- second-run idempotency,
- check/diff,
- canary inventory,
- runtime verification.

Hybridný system potrebuje contract test medzi Terraform outputom a Ansible inventory/inputom.

## 23. Versioning

Versionuj samostatne:

- Terraform modules,
- providers a lock files,
- Ansible collections/roles,
- execution environments,
- machine images,
- inventory schema,
- cross-tool contract.

Upgrade jedného nástroja môže zmeniť správanie druhého bez priameho source diffu, napríklad zmena Terraform output type alebo inventory hostname format.

## 24. Ownership matrix

Príklad:

| Objekt/atribút | Terraform | Ansible |
|---|---:|---:|
| VPC/subnet | owner | consumer |
| VM lifecycle | owner | target consumer |
| Security group | owner | no write |
| OS packages | no write | owner |
| Application config file | no write | owner |
| DNS record | owner | read only |
| Service restart | no write | owner |
| Host image ID | owner | build-input producer podľa workflowu |

Každý mutable attribute má mať jedného authoritative writera.

## 25. Rozhodovací rámec

Použi Terraform, keď:

- objekt má dlhodobý resource lifecycle,
- potrebuje stable identity a dependency graph,
- create/update/delete/replace musia byť plánované,
- persistentný state prináša hodnotu,
- provider vie čítať a spravovať objekt,
- drift má byť viditeľný v plane.

Použi Ansible, keď:

- potrebuješ host alebo device configuration,
- workflow je ordered orchestration,
- current state vie zistiť module pri run-e,
- potrebuješ batches, handlers a conditional tasks,
- operácia patrí do runbooku,
- universal persistent resource state by bol zbytočný.

Použi oba, keď:

- Terraform vytvára platform resources,
- Ansible konfiguruje ich runtime,
- boundary a data contract sú explicitné,
- pipeline a identities sú oddelené,
- nevznikajú dvaja writers rovnakého state-u.

## 26. Praktické scenáre

### Cloud VM s aplikáciou

```text
Terraform: network, VM, disk, IAM, DNS
Ansible: packages, user, config, service
```

### Managed database

```text
Terraform: instance, subnet group, security, parameter group podľa ownershipu
Ansible: optional schema/bootstrap orchestration iba s migration ledgerom
```

### Kubernetes cluster

```text
Terraform: cluster, nodes, cloud IAM/network integrations
Ansible: host bootstrap alebo operational runbook podľa platformy
Kubernetes/GitOps: application manifests a continuous reconciliation
```

### Network devices

```text
Terraform: vhodné resources tam, kde provider má robustný lifecycle model
Ansible: configuration push, validation, backups a multi-device orchestration
```

### Golden image

```text
Ansible: configure image build instance
Image pipeline: publish immutable image
Terraform: deploy image version
```

## 27. Anti-patterny

### Terraform spravuje každý config file cez provisioner

State nepozná skutočný file/configuration lifecycle.

### Ansible vytvára dlhodobú cloud infra bez identity a drift modelu

Destroy, import a replacement sú nejasné.

### Oba nástroje menia rovnaký attribute

Vzniká perpetual drift a ownership konflikt.

### Terraform output čítaný priamo z citlivého celého state-u

Ansible dostáva širší access a coupling než potrebuje.

### Ansible sa spúšťa pred readiness

Nové hosts sú unreachable alebo ešte nemajú stabilný management channel.

### Infrastructure a configuration používajú jednu admin identity

Kompromitácia jedného jobu má zbytočne široký blast radius.

### Nástroj vybraný podľa popularity

Execution a lifecycle model nezodpovedá spravovanému objektu.

## 28. Troubleshooting

### Terraform vytvoril VM, Ansible ju nevidí

Over output/inventory contract, host identity, DNS/IP readiness, inventory refresh/cache a network path.

### Ansible zmení hodnotu, Terraform ju vracia späť

Ide o ownership conflict. Urči authoritative writer a odstráň druhý write path alebo explicitne zmeň contract.

### Terraform apply prešiel, Ansible je unreachable

Infrastructure existence nie je runtime readiness. Over boot, cloud-init, firewall, route, SSH/WinRM, identity a host-key behavior.

### Ansible run zlyhal a Terraform chce resource nahradiť

Rozlíš host configuration failure od infrastructure lifecycle failure. Replacement používaj iba pri immutable/recovery policy, nie automaticky pri každom task error-e.

### Inventory obsahuje staré hosts

Over dynamic inventory cache, Terraform destroy events, CMDB reconciliation a stable host IDs.

### Pipeline nevie bezpečne zopakovať krok

Over partial state, Terraform lock/state serial, Ansible idempotenciu, migration ledger a external side effects.

## 29. Kontrolné otázky

1. Aký je hlavný rozdiel medzi Terraform state-om a Ansible runtime state detection?
2. Ako sa líši Terraform dependency graph od Ansible task orderingu?
3. Prečo Terraform plan nie je ekvivalent Ansible check mode?
4. Ktoré resources má typicky vlastniť Terraform?
5. Ktorú konfiguráciu má typicky vlastniť Ansible?
6. Prečo sú Terraform provisioners rizikové?
7. Ako bezpečne prepojiť Terraform outputs s inventory?
8. Ako vzniká ownership conflict medzi nástrojmi?
9. Kedy je vhodný golden-image pattern?
10. Ako navrhnúť recovery po partial Terraform a Ansible failure?

## Glossary impact

Relevantné pojmy: provisioning, configuration management, resource lifecycle engine, task-oriented automation, provisioning/configuration boundary, cross-tool contract, authoritative writer, golden image, bootstrap configuration, readiness boundary a ownership matrix.

## Oficiálna dokumentácia

- [What is Terraform](https://developer.hashicorp.com/terraform/intro)
- [Terraform core workflow](https://developer.hashicorp.com/terraform/intro/core-workflow)
- [Integrate Terraform with Ansible Automation Platform](https://developer.hashicorp.com/validated-patterns/terraform/terraform-integrate-ansible-automation-platform)
- [Ansible playbooks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/index.html)
- [Ansible concepts](https://docs.ansible.com/projects/ansible/latest/getting_started/basic_concepts.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Ansible idempotencia](ansible-idempotency.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
