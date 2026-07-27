# Roles a collections

Role je reusable configuration capability. Collection je versionovaný distribution a execution dependency balík, ktorý môže niesť roles, modules, plugins, playbooks a dokumentáciu. Ich hlavná hodnota nie je directory layout, ale stabilný contract medzi ownerom, publisherom, execution environmentom a consumerom.

Hlavný model:

```text
capability intent a owner
→ role public contract
→ immutable collection source a artifact
→ resolved dependency a execution-environment subject
→ caller inputs a target context
→ expanded role execution graph
→ host runtime outcome
→ test, release a upgrade evidence
→ consumer inventory, deprecation a recovery
```

Rovnaký playbook commit nemusí znamenať rovnaký run, ak sa zmení collection artifact, transitive dependency alebo execution environment.

## 1. Atlas scenár: Payments service capability

Atlas platform team publikuje role:

```text
company.platform.payments_service
```

Role má nainštalovať package, vyrenderovať config, spravovať systemd unit, notify-nuť runtime transition a overiť health. Consumer playbook používa:

```yaml
- name: Configure Atlas Payments
  hosts: payments_app
  roles:
    - role: company.platform.payments_service
      atlas_payments_release: v43
      atlas_payments_port: 8443
      atlas_payments_tls_enabled: true
```

Role je distribuovaná v collection `company.platform` a execution environment pinne:

```text
ansible-core version
collection artifact version/digest
Python dependencies
system packages a CLI tools
```

Bez tejto identity môže developer testovať inú capability než production controller.

## 2. Kedy vzniká role boundary

Role má zmysel, keď existuje samostatná capability s:

- verejnými inputs a defaults;
- vlastnými tasks, templates alebo handlers;
- jasnými side effects a privilege požiadavkami;
- podporovanými platforms;
- testovacím a release lifecycle-om;
- viacerými consumers alebo opakovateľným použitím;
- ownerom a support policy.

Dvojriadkový task file nemusí byť role. Naopak jedna mega-role pre celý host skrýva rozdielne ownership, failure a upgrade boundaries.

Boundary vyber podľa capability a change couplingu, nie podľa počtu files.

## 3. Role contract

Public contract role zahŕňa:

```text
purpose a non-goals
namespaced inputs, types a defaults
required values a validation
published facts alebo outputs
notification topics
created a modified resources
privilege, network a package dependencies
supported platforms a core versions
idempotency a check/diff-mode expectations
upgrade, rollback a recovery behavior
```

`defaults/main.yml` je vhodný pre podporované customization points:

```yaml
atlas_payments_port: 8443
atlas_payments_tls_enabled: true
atlas_payments_config_path: /etc/atlas/payments.yml
```

`vars/main.yml` má vyššiu precedence a je vhodný len pre skutočné interné constants. Environment data v role vars môže blokovať caller override a vytvoriť skrytý production mismatch.

## 4. Role implementation lifecycle

Typická role organizuje:

```text
defaults a validation
→ installation
→ configuration artifact
→ service/runtime transition
→ verification
→ handlers a recovery
```

```text
roles/payments_service/
├── README.md
├── defaults/main.yml
├── tasks/main.yml
├── handlers/main.yml
├── templates/payments.yml.j2
├── meta/main.yml
└── tests/
```

Directory layout je pomôcka. `tasks/main.yml` má viesť capability lifecycle a importovať menšie files podľa významu, nie vytvárať jeden file na každý task.

## 5. Namespacing ako isolation contract

Generic values typu `port`, `user`, `enabled` alebo handler `restart service` môžu kolidovať medzi roles.

Preferuj:

```yaml
atlas_payments_port: 8443
atlas_payments_user: atlas
atlas_payments_enabled: true
```

Rovnako namespacuj:

- published facts;
- registered values s dlhším scope-om;
- handler alebo `listen` topics;
- tags;
- template data structures.

Namespacing nerieši zlé precedence ani contract design, ale znižuje accidental cross-role coupling.

## 6. Static a dynamic role reuse

Role možno načítať cez `roles:`, `import_role` alebo `include_role`.

```yaml
- name: Load Atlas role statically
  ansible.builtin.import_role:
    name: company.platform.payments_service
```

```yaml
- name: Load Atlas role dynamically
  ansible.builtin.include_role:
    name: company.platform.payments_service
  when: atlas_payments_enabled | bool
```

Static loading zviditeľňuje graph pri parse phase. Dynamic include rozhoduje počas executionu a môže závisieť od runtime value.

Rozdiel ovplyvňuje:

```text
task listing
tags a condition propagation
variable availability
handler loading
failure timing
```

Supported invocation modes patria do role tests. Caller nemá predpokladať, že tags alebo handler visibility budú identické pri každom reuse mechanizme.

## 7. Handler topic ako public transition contract

Reusable role nemá nútiť callerov poznať interný handler name:

```yaml
handlers:
  - name: Reload Atlas Payments process
    ansible.builtin.service:
      name: atlas-payments
      state: reloaded
    listen: Atlas Payments configuration changed
```

Stable `listen` topic je public event contract. Jeho premenovanie môže byť breaking change, aj keď task syntax a variables zostanú rovnaké.

Handler contract musí definovať, čo notification znamená, kedy je safe reload/restart a akú runtime verification role vykoná.

## 8. Role dependencies a explicitná composition

`meta/main.yml` môže deklarovať role dependencies. Skrytý chain však znižuje auditovateľnosť:

```text
payments role
→ runtime role
→ repository role
→ base hardening role
```

Dependency patrí do metadata iba keď je invariantom capability. Environment orchestration a voliteľné capabilities sú čitateľnejšie explicitne v playbooku.

Skrytá dependency môže:

- zmeniť firewall alebo package repository bez caller awareness;
- rozšíriť privilege requirements;
- notify-nuť handlers v nečakanom poradí;
- zmeniť tag a skip semantics;
- skomplikovať upgrade a rollback.

## 9. Collection ako artifact a namespace

Collection je versionovaný artifact s namespace:

```text
company.platform
```

Môže obsahovať:

```text
roles/
plugins/modules/
plugins/action/
plugins/inventory/
plugins/filter/
plugins/lookup/
playbooks/
docs/
tests/
```

FQCN, napríklad `company.platform.payments_service`, identifikuje source namespace. Bez immutable artifact version alebo digest však neidentifikuje presný executable content.

Collection artifact subject zahŕňa:

```text
source revision
collection name a version
built artifact digest
publisher a provenance
resolved dependencies
supported ansible-core range
release notes a compatibility contract
```

## 10. Dependency resolution a execution environment

`requirements.yml` môže deklarovať versions:

```yaml
collections:
  - name: company.platform
    version: "3.4.2"
  - name: ansible.posix
    version: "2.1.0"
```

Broad ranges umožňujú, aby rovnaký playbook commit neskôr načítal iný implementation set.

Produkčný runtime subject má pinovať:

```text
execution image digest
ansible-core
collection artifacts a digests
Python wheels/packages
system tools
configuration a plugin search paths
```

Samotný `requirements.yml` nemusí zachytiť transitive Python dependency ani system package behavior.

## 11. Supply-chain boundary

Collection je executable code. Custom action, lookup, callback alebo inventory plugin môže bežať na control node-e s prístupom k credentials, filesystemu a networku.

Pred adopciou over:

- publisher a source repository;
- release a maintenance history;
- artifact provenance/integrity;
- direct a transitive dependencies;
- custom plugins a local execution paths;
- shell/command usage;
- secret a logging behavior;
- required permissions a egress;
- supported runtime matrix.

Popularita alebo počet downloads nie je security verdict.

## 12. Testing role a collection

Role test lifecycle:

```text
contract fixture
→ syntax a lint
→ isolated first converge
→ artifact a runtime assertions
→ handler verification
→ second converge
→ expect no unintended changes
→ cleanup verdict
```

Testuj minimálne:

- documented defaults a required inputs;
- supported overrides a invalid combinations;
- platform matrix;
- static a dynamic invocation modes;
- handler topics;
- deterministic templates;
- partial failure a recovery;
- idempotency a second-run behavior;
- upgrade z podporovanej predchádzajúcej version.

Collection pipeline navyše overuje metadata, docs, custom plugins/modules, artifact build/inspection, dependency resolution a publication provenance.

Publikovaný artifact musí pochádzať z testovaného source subjectu, nie z lokálneho neauditovaného buildu.

## 13. Release a compatibility policy

Version má význam iba s explicitným compatibility contractom. Breaking change môže byť:

- premenovanie alebo type change variable;
- zmena default portu alebo TLS behavioru;
- nový required privilege;
- zmena handler topicu;
- iný generated configuration format;
- package removal alebo replacement;
- zmena published fact/result schema;
- odlišný supported platform alebo core range.

Release lifecycle:

```text
reviewed source
→ contract a integration tests
→ version/changelog
→ immutable artifact build
→ artifact inspection a provenance
→ publication
→ consumer pinning
→ canary upgrade
→ fleet verification
```

## 14. Consumer inventory a deprecation

Owner potrebuje vedieť:

```text
ktorý repository/playbook používa role
collection a role version
execution environment digest
environments a target scope
consumer owner
supported upgrade path
last verified runtime outcome
```

Bez consumer inventory nemožno bezpečne odstrániť old variable, handler topic alebo module behavior. Deprecation potrebuje deadline, migration guide, telemetry a owner escalation.

## 15. Worked failure: mutable branch zmenila behavior bez playbook diffu

Consumer používa Git branch `main` ako collection source. Medzi check-mode reviewom a production runom owner zmení default reload na hard restart.

```text
playbook commit je rovnaký
→ mutable dependency resolves nový content
→ role public behavior sa zmení
→ production controller vykoná hard restart
→ approval sa nevzťahoval na executed implementation
```

Fix zahŕňa immutable artifact version/digest, resolved dependency manifest a nový test/review pri upgrade.

## 16. Worked failure: role vars zablokovali production override

Role definuje v `vars/main.yml`:

```yaml
atlas_payments_database_endpoint: db.stage.internal:5432
```

Production inventory definuje správny endpoint, ale role vars majú vyššiu precedence.

```text
caller vyjadruje production intent
→ internal role var ho prepíše
→ template je syntakticky validný
→ production service používa staging dependency
```

Environment hodnoty patria do caller-owned inputs alebo external service contractu. Role vars majú niesť iba vedomé interné constants.

## 17. Worked failure: handler topic rename zlomil runtime convergence

Version 3.5 premenovala topic:

```text
Atlas Payments configuration changed
→ Atlas Payments reload required
```

Consumer task mimo role stále notify-uje starý topic. File sa zmení, ale handler sa nespustí.

```text
artifact mutation prebehla
→ notification nemá listener
→ run môže zostať green
→ process používa starú config verziu
```

Topic je public contract a rename vyžaduje compatibility alias alebo major migration s consumer inventory a tests.

## 18. Worked failure: broad range načítal nekompatibilnú transitive collection

Execution environment build používa:

```yaml
version: ">=3.0.0,<4.0.0"
```

Nový minor release zmení module return schema. Role používa staré field v `failed_when` a interpretuje authorization failure ako success.

```text
broad dependency range
→ nový artifact bez consumer source diffu
→ result schema sa zmení
→ failure classifier číta missing field
→ neúplná mutácia dostane green verdict
```

Resolved lock/manifest a compatibility tests musia viazať presný dependency set na execution environment.

## 19. Causal troubleshooting walkthrough: rovnaký playbook sa správa lokálne a v controlleri odlišne

Developer run je no-change. Controller run mení config a reštartuje všetky hosts.

### 1. Zafixuj supply-chain subject

Zaznamenaj playbook revision, execution image digest, `ansible-core`, collection artifact versions/digests, dependency manifest, role invocation mode, effective inputs, inventory a controller configuration.

### 2. Súťažiace hypotézy

1. Local a controller používajú inú collection version.
2. Transitive dependency alebo Python library sa resolve-la odlišne.
3. Execution environment má iný template/filter behavior.
4. FQCN alebo plugin search path načítal iný module.
5. Role je lokálne importovaná staticky, controller ju includuje dynamicky cez odlišný path.
6. Role vars/defaults sa líšia medzi artifacts.
7. Controller má stale cached role/collection content.
8. Runtime target alebo effective variables sa líšia, nie supply chain.

### 3. Diskriminačné observation points

- execution image a collection artifact digests;
- resolved dependency/requirements manifest;
- `ansible-core`, Python a system-tool versions;
- FQCN a plugin path output;
- role source checksum a changelog;
- invocation mode a task listing;
- redacted effective inputs;
- rendered artifact checksum a module result schema.

### 4. Containment

Pozastav production rollout a zachovaj oba execution environments. Neopravuj rozdiel náhodným reinstallom, ktorý zničí comparison evidence.

### 5. Recovery

- dependency mismatch → rebuildni pinned known-good environment;
- transitive drift → vytvor resolved lock/manifest;
- incompatible release → rollbackni exact artifact alebo apply-ni tested migration;
- plugin collision → použi FQCN a zúž search path;
- invocation contract gap → zjednoť podporovaný reuse mode a tests;
- stale cache → invaliduj ju a over artifact digest.

### 6. Over pôvodný outcome

Canary run musí použiť nový immutable runtime subject, dosiahnuť expected artifact a loaded service state a druhý run musí byť no-change. Potom rozšír rollout.

### 7. Posuň control skôr

Pridaj execution subject manifest, artifact digest verification, compatibility matrix, consumer inventory a controller/local reproducibility test.

## 20. Referenčné pravidlá

- Role je versionovaný capability contract, nie iba directory.
- Defaults sú public customization; vars sú silné interné constants.
- Namespacing znižuje cross-role collisions.
- Static a dynamic reuse majú odlišné graph semantics.
- Handler topic môže byť public breaking contract.
- Role dependency nemá skrývať environment orchestration.
- FQCN určuje namespace; artifact digest určuje presný content.
- Collection a plugin sú executable supply-chain dependencies.
- Execution environment je súčasť run subjectu.
- Upgrade testuje contract, runtime outcome aj second-run convergence.
- Deprecation potrebuje consumer inventory.

## 21. Kontrolné otázky

1. Kedy task group tvorí samostatnú role capability?
2. Čo patrí do public role contractu?
3. Prečo environment values nepatria do role vars?
4. Ako sa líši `import_role` od `include_role`?
5. Prečo je handler topic compatibility contract?
6. Čo FQCN identifikuje a čo neidentifikuje?
7. Čo tvorí collection artifact subject?
8. Prečo `requirements.yml` nemusí stačiť na reprodukovateľný runtime?
9. Aké tests potrebuje supported role upgrade?
10. Ako consumer inventory umožňuje bezpečnú deprecation?

## Glossary impact

Relevantné pojmy: Ansible capability contract, role public contract, role internal constant, role execution graph, notification topic compatibility, collection artifact subject, resolved collection dependency, execution-environment subject, collection supply-chain boundary, role upgrade evidence, consumer inventory a role deprecation lifecycle.

## Oficiálna dokumentácia

- [Reusing Ansible artifacts](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_reuse.html)
- [Roles](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_reuse_roles.html)
- [Using collections in a playbook](https://docs.ansible.com/ansible/latest/collections_guide/collections_using_playbooks.html)
- [Installing collections](https://docs.ansible.com/projects/ansible/latest/collections_guide/collections_installing.html)
- [Galaxy user guide](https://docs.ansible.com/projects/ansible/latest/galaxy/user_guide.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Handlers, loops a conditionals](handlers-loops-conditionals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Vault →](vault.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
