# Roles a collections

Ansible role je reusable configuration capability. Collection je versionovaný distribution artifact, ktorý môže obsahovať roles, modules, action/inventory/lookup/filter plugins, playbooks a dokumentáciu. Ich hlavná hodnota nie je directory layout, ale provider–consumer contract medzi ownerom, publisherom, execution environmentom a playbookom. Rovnaký playbook commit nemusí vykonať rovnakú automation, ak sa zmení collection artifact, transitive Python dependency alebo plugin search path.

Kapitola otvára incident `IAC-PAY-79`. Atlas platform team publikuje collection `atlas.platform`. Consumer pinne iba broad version range, controller image používa mutable tag a role premenovala public handler topic bez compatibility aliasu. Nový artifact sa načíta bez consumer source diffu, zmení module result schema a config file sa síce aktualizuje, ale runtime handler sa nespustí. Supply-chain a role contract drift sa tvária ako playbook success.

## 1. Dominantný capability-to-runtime lifecycle

```text
capability intent a owner
→ role public contract
→ collection source a dependency graph
→ immutable artifact build a provenance
→ pinned execution environment
→ caller inputs, providers/plugins a target context
→ expanded task/handler graph
→ host artifact a runtime outcome
→ second-run, upgrade a recovery evidence
→ consumer inventory, deprecation a retirement
```

## 2. Kedy vzniká role boundary

Role má zmysel, keď capability má:

- jasný purpose a non-goals;
- verejné inputs a defaults;
- vlastné tasks/templates/handlers;
- privilege, package a network dependencies;
- supported platforms;
- idempotency a recovery behavior;
- ownera a release lifecycle;
- viac consumers alebo opakovateľné použitie.

Dvojriadkový task file nemusí byť role. Jedna mega-role pre celý server naopak skrýva odlišné ownership a failure domains.

## 3. Role public contract

```yaml
roleContract:
  fqcn: atlas.platform.payments_runtime
  version: 3.4.2
  purpose: configure-and-verify-payments-runtime
  inputs:
    atlas_payments_release:
      required: true
      type: string
    atlas_payments_port:
      default: 8443
      type: integer
    atlas_payments_tls_enabled:
      default: true
      type: boolean
  notifications:
    - Atlas Payments configuration changed
  privileges:
    become: root-for-install-and-service
  supportedPlatforms:
    - rhel-9
    - debian-12
  secondRunExpectation: no-unintended-change
```

Contract zahŕňa variable semantics, modified resources, notification topics, side effects, check/diff expectations, upgrade a rollback behavior.

## 4. Defaults verzus role vars

```yaml
# defaults/main.yml
atlas_payments_port: 8443
atlas_payments_tls_enabled: true
```

Defaults sú public customization points s nízkou precedence.

```yaml
# vars/main.yml
atlas_payments_unit_name: atlas-payments.service
```

Role vars majú vyššiu precedence a patria iba skutočným interným constants. Environment-specific database endpoint v `vars/main.yml` môže prepísať caller production intent a je zlý contract.

## 5. Namespacing

Generic variables a topics kolidujú:

```yaml
port: 8443
restart_service: true
```

Preferuj:

```yaml
atlas_payments_port: 8443
atlas_payments_restart_policy: reload
```

Namespacuj variables, published facts, handler topics, tags a template data. Namespacing nevyrieši zlú precedence, ale obmedzí accidental cross-role coupling.

## 6. Role structure ako lifecycle, nie cieľ

```text
roles/payments_runtime/
├── README.md
├── defaults/main.yml
├── tasks/main.yml
├── handlers/main.yml
├── templates/payments.yml.j2
├── meta/main.yml
└── tests/
```

`tasks/main.yml` má viesť capability lifecycle:

```yaml
- name: Validate contract
  ansible.builtin.import_tasks: validate.yml

- name: Install runtime
  ansible.builtin.import_tasks: install.yml

- name: Configure runtime
  ansible.builtin.import_tasks: configure.yml

- name: Verify runtime
  ansible.builtin.import_tasks: verify.yml
```

Rozdelenie po mechanistických phases je čitateľnejšie než jeden file na každý task.

## 7. Static a dynamic role reuse

```yaml
- name: Import role statically
  ansible.builtin.import_role:
    name: atlas.platform.payments_runtime
```

```yaml
- name: Include role dynamically
  ansible.builtin.include_role:
    name: atlas.platform.payments_runtime
  when: atlas_payments_enabled | bool
```

Static a dynamic reuse ovplyvňujú parse/execution visibility, tags, conditions, variables a handler loading. Supported invocation modes patria do tests; caller nesmie predpokladať identické behavior bez contractu.

## 8. Handler topic ako public API

```yaml
handlers:
  - name: Reload Atlas Payments
    ansible.builtin.service:
      name: atlas-payments
      state: reloaded
    listen: Atlas Payments configuration changed
```

Consumer môže notify-nuť topic bez znalosti interného handler name. Topic rename je compatibility change.

Worked failure:

```text
role 3.5 premenovala topic
→ external consumer stále notify-uje old topic
→ file changed
→ žiadny listener
→ runtime old
```

Kompatibilný release môže dočasne listenovať na oba topics alebo poskytnúť migration guide a consumer inventory.

## 9. Role dependencies

`meta/main.yml` môže deklarovať dependencies, ale hidden chain znižuje auditovateľnosť:

```text
payments runtime
→ repository configuration
→ base hardening
→ firewall
```

Dependency patrí do role metadata iba ak je invariant capability. Environment orchestration je čitateľnejšia explicitne v playbooku.

Skrytá dependency môže meniť package repositories, firewall, privileges alebo handler ordering bez caller awareness.

## 10. Collection ako executable artifact

Collection namespace:

```text
atlas.platform
```

Môže obsahovať:

```text
roles/
plugins/modules/
plugins/action/
plugins/inventory/
plugins/lookup/
plugins/filter/
plugins/callback/
playbooks/
docs/
tests/
```

Oficiálna dokumentácia definuje collection ako distribution format pre roles, modules, plugins a ďalší content. citeturn329472search22turn329472search19

Custom plugin môže bežať na controlleri s accessom k credentials a networku. Collection je supply-chain code, nie iba YAML package.

## 11. Artifact subject

```yaml
collectionArtifact:
  namespace: atlas
  name: platform
  version: 3.4.2
  sourceRevision: 71ad...
  artifactDigest: sha256:11cf...
  publisher: atlas-platform-ci
  ansibleCoreRange: ">=2.x,<next-breaking"
  dependencies:
    ansible.posix: 2.1.0
    community.general: 11.2.0
  provenanceDigest: sha256:77ef...
```

FQCN identifikuje namespace, nie exact bytes. Artifact version/digest a execution environment identifikujú implementation subject.

## 12. Requirements a pinning

```yaml
# requirements.yml
collections:
  - name: atlas.platform
    version: 3.4.2
  - name: ansible.posix
    version: 2.1.0
```

Install:

```bash
ansible-galaxy collection install \
  -r requirements.yml \
  --collections-path ./collections

ansible-galaxy collection list
```

List preukazuje installed names/versions v path-e. Nepreukazuje source provenance, artifact integrity po install-e ani transitive Python/system dependencies.

Produkčný execution environment pinne image digest a obsahuje resolved manifest.

## 13. Broad range failure

```yaml
version: ">=3.0.0,<4.0.0"
```

Nový minor release zmení module return field. Role `failed_when` číta staré field a authorization failure sa interpretuje ako success.

```text
rovnaký playbook commit
→ iný resolved collection
→ odlišný result schema
→ false green verdict
```

Upgrade sa má vykonať ako explicitný dependency change s contract tests, nie vedľajší efekt image rebuild-u.

## 14. Execution environment manifest

```bash
ansible --version
ansible-galaxy collection list
python -m pip freeze > python-packages.txt
sha256sum requirements.yml python-packages.txt
```

Observed manifest je evidence aktuálneho runtime. Silnejší build pipeline generuje signed SBOM/provenance pre execution image a kontroluje digest pred runom.

## 15. Supply-chain review

Pred adopciou external collection over:

- publisher/source repository;
- release a maintenance history;
- artifact provenance/integrity;
- custom controller-side plugins;
- shell/command usage;
- logging a secret behavior;
- network/privilege requirements;
- direct/transitive dependencies;
- supported core/runtime matrix.

Download count nie je security verdict.

## 16. Role a collection test lifecycle

```text
contract fixtures
→ syntax/lint
→ first converge
→ artifact a runtime assertions
→ handler integration
→ second converge
→ forbidden inputs
→ upgrade fixture
→ cleanup/recovery
```

Praktický playbook fixture:

```yaml
- name: Test Atlas role
  hosts: test_host
  roles:
    - role: atlas.platform.payments_runtime
      atlas_payments_release: payments-v43
      atlas_payments_port: 8443
```

Assertions kontrolujú package version, config checksum, service state, loaded version a second-run changes.

## 17. Compatibility policy

Breaking changes zahŕňajú:

- variable rename/type/default change;
- new required privilege;
- handler topic rename;
- generated config format change;
- package removal/replacement;
- published result/fact schema change;
- supported platform/core change.

Semantic version je owner claim. Consumer integration a upgrade tests sú evidence.

## 18. Consumer inventory

```yaml
consumer:
  repository: atlas/payments-live
  playbook: playbooks/payments.yml
  collectionVersion: 3.4.2
  executionEnvironmentDigest: sha256:71ca...
  environments: [stage, prod-eu]
  owner: payments-platform
  lastVerified: 2026-07-31
```

Bez inventory nemožno bezpečne odstrániť variable, topic alebo old release.

## 19. Worked incident `IAC-PAY-79`

Controller image `latest` rebuildol collection 3.5.0. Role topic sa zmenil a transitive module result schema tiež.

```text
mutable execution image
→ new collection bytes
→ file mutation reports changed
→ old notification topic has no listener
→ module failure classifier reads missing field
→ run green, runtime old
```

Root cause bol unresolved reusable dependency a breaking public contract bez consumer migration.

## 20. Competing hypotheses pri local/controller rozdiele

```text
H1: collection versions/digests sa líšia
H2: transitive Python/system dependency sa líši
H3: plugin search path resolve-ne iný content
H4: static/dynamic invocation mení handler visibility
H5: role defaults/vars sa líšia
H6: controller cache má stale content
H7: target inventory/values sa líšia
```

Dôkazy:

- image/collection digests H1;
- package/SBOM H2;
- FQCN/search config H3;
- task/handler graph H4;
- source checksums/effective values H5/H7;
- cache path/timestamps H6.

## 21. Evidence-preserving containment a recovery

1. pozastaviť rollout;
2. zachovať local aj controller images/manifests;
3. identifikovať exact collection bytes a topic/result changes;
4. obnoviť pinned known-good image alebo publikovať compatible fix;
5. overiť handler execution a runtime version na canary hoste;
6. spustiť second converge;
7. aktualizovať consumer inventory a deprecation controls.

## 22. Acceptance a forbidden paths

```text
role contract je documented a namespaced
+ collection artifact/version/digest sú immutable
+ execution environment je pinned
+ transitive dependency manifest je zachovaný
+ static/dynamic invocation modes sú testované
+ handler topics sú compatibility-tested
+ invalid inputs sú odmietnuté
+ mutable branch/range fixture je odmietnutý
+ first/second converge a runtime verification prejdú
+ consumer inventory pokrýva production users
```

## 23. Anti-patterny

### „Role je iba folder structure“

Bez public contractu je to iba reorganizovaný task code.

### „FQCN pinne version“

Identifikuje namespace, nie artifact bytes.

### „Broad range automaticky prijíma kompatibilné minor releases“

Compatibility musí byť testovaná.

### „Handler topic je interný detail“

Ak ho consumers notify-ujú, je public API.

### „Controller image `latest` je pohodlná“

Ruší reproducibility a approval identity.

## 24. Kontrolné otázky

1. Kedy má capability tvoriť role?
2. Čo patrí do role public contractu?
3. Aký rozdiel je medzi defaults a vars?
4. Prečo namespacing nestačí na ownership?
5. Ako static a dynamic role reuse menia behavior?
6. Prečo handler topic môže byť breaking API?
7. Čo collection artifact môže vykonávať na controlleri?
8. Čo FQCN preukazuje a čo nie?
9. Prečo broad version range oslabuje reproducibility?
10. Aké vrstvy má role/collection test lifecycle?
11. Prečo je consumer inventory potrebný pre deprecation?
12. Ako sa testuje forbidden mutable-dependency path?

## Glossary impact

Relevantné pojmy: Ansible role, role contract, defaults, role vars, namespacing, import_role, include_role, handler topic, role dependency, collection, FQCN, collection artifact, requirements manifest, execution environment, transitive dependency, consumer inventory a deprecation.

## Primárne zdroje

- [Roles](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_reuse_roles.html)
- [Using collections in playbooks](https://docs.ansible.com/projects/ansible/latest/collections_guide/collections_using_playbooks.html)
- [Developing collections](https://docs.ansible.com/projects/ansible/latest/dev_guide/developing_collections.html)
- [Ansible collections](https://docs.ansible.com/collections.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
[← Predchádzajúca: Handlers, loops a conditionals](handlers-loops-conditionals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Vault →](vault.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
