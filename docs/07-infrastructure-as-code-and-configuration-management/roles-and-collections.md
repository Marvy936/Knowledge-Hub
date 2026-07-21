# Roles a collections

Ansible role organizuje súvisiace tasks, handlers, variables, templates, files a metadata do opakovateľnej capability. Collection je vyššia distribučno-verzovacia jednotka, ktorá môže obsahovať viac roles, modules, plugins, playbooks a dokumentáciu.

Role a collection neriešia iba poriadok v adresároch. Vytvárajú **reusable contract**, dependency a supply-chain boundary, ktorú treba versionovať, testovať, publikovať a bezpečne upgradovať.

## 1. Kedy vytvoriť role

Role má zmysel, keď automation predstavuje opakovateľnú capability, napríklad:

- konfiguráciu web servera,
- nasadenie application agentu,
- hardening Linux hostu,
- správu používateľov a SSH policy,
- konfiguráciu databázového klienta,
- deployment jednej služby.

Jednorazový trojriadkový task file nemusí byť role. Role je vhodná, keď existuje:

- verejný input contract,
- viac súvisiacich krokov,
- handlers alebo templates,
- potreba testovania,
- viac callerov,
- samostatný lifecycle a ownership.

## 2. Štandardná štruktúra role

Typická role:

```text
roles/example_service/
├── README.md
├── defaults/
│   └── main.yml
├── vars/
│   └── main.yml
├── tasks/
│   └── main.yml
├── handlers/
│   └── main.yml
├── templates/
├── files/
├── meta/
│   └── main.yml
└── tests/
```

Adresáre sú voliteľné. Nepridávaj prázdnu štruktúru iba preto, že ju generator vytvoril.

## 3. `defaults` ako public contract

`defaults/main.yml` obsahuje ľahko override-nuteľné defaults:

```yaml
example_service_package: example-service
example_service_enabled: true
example_service_port: 8080
example_service_config_path: /etc/example/service.yml
```

Dobré defaults:

- majú namespaced names,
- majú stabilný type,
- sú dokumentované,
- neobsahujú secrets,
- reprezentujú podporované customization points.

Caller nemá potrebovať poznať internú task implementáciu.

## 4. `vars` ako interné constants

`vars/main.yml` má vyššiu variable precedence. Používaj ho opatrne na hodnoty, ktoré caller bežne nemá meniť:

```yaml
example_service_system_user: example
example_service_unit_name: example-service.service
```

Environment-specific hodnoty v `vars` sa ťažko override-ujú a často signalizujú zlý contract.

## 5. Tasks role

`tasks/main.yml` je entry point role:

```yaml
- name: Validate role inputs
  ansible.builtin.assert:
    that:
      - example_service_port | int > 0
      - example_service_port | int < 65536

- name: Install service package
  ansible.builtin.package:
    name: "{{ example_service_package }}"
    state: present

- name: Render service configuration
  ansible.builtin.template:
    src: service.yml.j2
    dest: "{{ example_service_config_path }}"
    owner: root
    group: root
    mode: "0640"
    validate: "/usr/bin/example-service validate --config %s"
  notify: Restart example service
```

Entry point môže importovať menšie task files:

```yaml
- name: Load installation tasks
  ansible.builtin.import_tasks: install.yml

- name: Load configuration tasks
  ansible.builtin.import_tasks: configure.yml
```

Task decomposition má sledovať capability a lifecycle, nie vytvárať jeden file na každý task.

## 6. Handlers role

`handlers/main.yml` definuje change-driven reakcie:

```yaml
- name: Restart example service
  ansible.builtin.service:
    name: "{{ example_service_unit_name }}"
    state: restarted
```

Pre reusable contract je vhodný `listen` topic:

```yaml
- name: Restart example service process
  ansible.builtin.service:
    name: "{{ example_service_unit_name }}"
    state: restarted
  listen: example service changed
```

Tasks potom používajú stabilný notification topic namiesto závislosti na internom názve handlera.

## 7. Templates a files

### `templates/`

Obsahuje Jinja templates renderované podľa host contextu.

### `files/`

Obsahuje statické artifacts kopírované bez templatingu.

Do role neukladaj:

- reálne secrets,
- environment-specific private keys,
- veľké mutable binaries bez artifact lifecycle,
- generated files, ktoré možno deterministicky vytvoriť.

## 8. Metadata role

`meta/main.yml` môže deklarovať:

- platform metadata,
- author/license metadata,
- role dependencies,
- collection search behavior podľa podporovanej syntaxe.

Role dependency sa vykoná pred závislou role. Skryté dependency chains znižujú čitateľnosť:

```text
application role
→ runtime role
→ repository role
→ base hardening role
```

Preferuj explicitnú composition v playbooku, keď dependency nie je invariantom role contractu.

## 9. Volanie role

### `roles:`

```yaml
- name: Configure application hosts
  hosts: application
  roles:
    - role: example_service
      example_service_port: 8080
```

Role uvedené v `roles:` sa správajú ako statically loaded content.

### `import_role`

```yaml
- name: Import example role
  ansible.builtin.import_role:
    name: example_service
```

Obsah sa spracúva staticky.

### `include_role`

```yaml
- name: Include example role dynamically
  ansible.builtin.include_role:
    name: example_service
  when: example_service_enabled | bool
```

Obsah sa načíta počas runtime. Rozdiel ovplyvňuje:

- parsing,
- tags,
- conditions,
- variable availability,
- task listing,
- error timing.

## 10. Role contract

Role contract zahŕňa:

- podporované inputs a ich types,
- defaults,
- required variables,
- outputs alebo facts, ktoré role publikuje,
- notifications a handlers,
- podporované platforms,
- privilege requirements,
- network a package dependencies,
- created/modified resources,
- idempotency expectations,
- check/diff-mode support,
- upgrade a rollback behavior.

README role má contract vysvetliť bez potreby čítať všetky tasks.

## 11. Namespacing

Generic variable names ako `port`, `user`, `enabled` alebo `packages` kolidujú s inými roles.

Preferuj:

```yaml
example_service_port: 8080
example_service_user: example
example_service_enabled: true
```

Rovnaké pravidlo platí pre:

- facts vytvorené cez `set_fact`,
- handler names alebo `listen` topics,
- tags,
- template variables,
- registered results, ak presahujú jeden task file.

## 12. Ansible collection

Collection je versionovaný balík s namespace a názvom:

```text
company.platform
```

Môže obsahovať:

```text
ansible_collections/company/platform/
├── galaxy.yml
├── README.md
├── roles/
├── playbooks/
├── plugins/
│   ├── modules/
│   ├── action/
│   ├── inventory/
│   ├── filter/
│   └── lookup/
├── docs/
└── tests/
```

Collection je vhodná, keď treba spoločne distribuovať:

- viac roles,
- custom modules alebo plugins,
- playbooks,
- documentation,
- test utilities,
- spoločný release lifecycle.

## 13. Fully Qualified Collection Name

Collection content sa identifikuje cez FQCN:

```yaml
company.platform.example_service
company.platform.deploy_application
company.platform.lookup_secret
```

Built-in príklad:

```yaml
ansible.builtin.template
```

FQCN explicitne určuje source a znižuje ambiguity pri rovnakých short names.

## 14. Collection metadata

`galaxy.yml` typicky definuje:

- namespace,
- collection name,
- version,
- authors,
- description,
- license,
- repository a documentation URLs,
- build exclusions,
- dependencies na iné collections.

Metadata je súčasť release contractu. Nesprávna dependency range môže načítať nekompatibilnú collection.

## 15. Collection a role dependencies

Dependencies deklaruj explicitne a versionovane.

Príklad `requirements.yml`:

```yaml
collections:
  - name: ansible.posix
    version: "2.1.0"
  - name: community.general
    version: ">=10.0.0,<11.0.0"
```

Inštalácia:

```bash
ansible-galaxy collection install -r requirements.yml
```

Riziká broad ranges:

- neočakávaný behavior po novom release,
- transitive dependency zmena,
- module parameter alebo return-schema zmena,
- supply-chain compromise,
- nereprodukovateľné CI runs.

Produkčný execution environment má zachytiť konkrétny resolved set dependencies.

## 16. Versioning

Role alebo collection release potrebuje definovať, čo je compatibility contract:

- variable names a types,
- defaults,
- handler topics,
- module arguments a return values,
- supported platforms,
- generated configuration,
- resource ownership,
- upgrade path.

Breaking change môže byť aj:

- zmena default portu,
- premenovanie handler topicu,
- odstránenie package,
- zmena file ownershipu,
- zmena generated config syntaxe,
- nová required privilege.

Version number bez compatibility policy neposkytuje bezpečný upgrade model.

## 17. Execution environment

Collection dependencies, Python libraries a system tools by mali byť zabalené do versionovaného execution environmentu.

Tým sa viaže:

```text
playbook commit
+ ansible-core version
+ collections
+ Python dependencies
+ system tools
→ reprodukovateľný runtime
```

Samotný `requirements.yml` nemusí zachytiť system packages ani presnú Python dependency resolution.

## 18. Supply-chain security

Role a collection sú executable code.

Pred použitím external contentu over:

- publisher a repository,
- release history,
- source integrity,
- dependencies,
- supported Ansible verzie,
- permissions a network access,
- custom plugins,
- shell/command usage,
- secret handling,
- maintenance status.

Nespúšťaj neznámy Galaxy content s produkčnými credentials iba preto, že má veľa downloads.

## 19. Testing role

Minimálny test workflow:

```text
syntax/lint
→ isolated converge
→ assertions
→ second converge
→ expect zero unintended changes
→ cleanup
```

Testuj:

- defaults,
- supported overrides,
- platform matrix,
- handlers,
- template validation,
- check mode podľa podpory,
- idempotenciu,
- upgrade zo supported prior version,
- failure a recovery paths.

## 20. Testing collection

Collection pipeline môže obsahovať:

- schema a metadata validation,
- documentation build,
- `ansible-lint`,
- unit tests pre plugins/modules,
- integration tests,
- role scenarios,
- compatibility matrix,
- artifact build a inspection,
- signed publishing podľa platformy.

Publikovaný artifact musí byť výsledkom testovaného commitu, nie lokálneho neauditovaného buildu.

## 21. Release workflow

Odporúčaný model:

```text
change
→ review
→ lint/unit/integration tests
→ version update
→ changelog
→ build collection artifact
→ inspect artifact
→ sign/publish
→ consume by immutable version
```

Consumers nemajú automaticky prijímať najnovší mutable branch content.

## 22. Upgrade workflow

Pri upgrade collection alebo role:

1. prečítaj changelog a breaking changes,
2. over supported `ansible-core`,
3. zostav nový execution environment,
4. spusti lint a syntax checks,
5. spusti isolated integration tests,
6. vykonaj check/diff run na reprezentatívnom inventory,
7. aplikuj canary batch,
8. over idempotenciu,
9. rozšír rollout.

## 23. Anti-patterny

### Jedna obrovská role pre celý host

Ownership, testovanie a reuse sú nejasné.

### Role pre každý dvojriadkový task

Vzniká abstrakčná a dependency réžia bez reálneho contractu.

### Environment data v `vars/main.yml`

Caller nevie hodnoty rozumne override-núť.

### Generic variable names

Roles sa navzájom ovplyvňujú cez kolízie.

### Mutable Git branch ako production dependency

Rovnaký playbook commit môže zajtra načítať iný content.

### Neobmedzené collection version ranges

CI runtime sa mení bez review.

### Role dependencies ako skrytá orchestrácia

Execution graph nie je z playbooku zrejmý.

### Collection ako sklad nesúvisiaceho obsahu

Nemá jasný ownership ani release contract.

## 24. Troubleshooting

### Role sa nenašla

Over `roles_path`, collection path, execution environment, spelling, namespace a installed artifact version.

### Module alebo plugin sa nenašiel

Použi FQCN a over, že správna collection je nainštalovaná v runtime, nie iba na developer hoste.

### Role používa inú variable hodnotu

Over defaults, inventory, role parameters, extra vars a variable precedence. Použi namespaced variable names.

### Handler z role nereaguje

Over notification name alebo `listen` topic, load timing role, changed signal a duplicate handler names.

### Upgrade zmenil behavior bez playbook diffu

Porovnaj collection versions, execution environment digest a dependency resolution.

### Tags nefungujú podľa očakávania

Rozlíš `roles:`, `import_role` a `include_role`; static a dynamic reuse majú odlišný parsing a tag behavior.

## 25. Kontrolné otázky

1. Kedy task file prerásol do role?
2. Aký je rozdiel medzi role defaults a role vars?
3. Čo tvorí public contract role?
4. Aký je rozdiel medzi `import_role` a `include_role`?
5. Prečo role variables potrebujú namespacing?
6. Čo môže obsahovať collection?
7. Prečo používať FQCN?
8. Ako versionovať collection dependencies?
9. Prečo je external role supply-chain dependency?
10. Ako overiť idempotenciu role?

## Glossary impact

Relevantné pojmy: Ansible role, role contract, role defaults, role vars, role dependency, `import_role`, `include_role`, Ansible collection, collection artifact, FQCN, `requirements.yml`, execution environment a collection dependency.

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
