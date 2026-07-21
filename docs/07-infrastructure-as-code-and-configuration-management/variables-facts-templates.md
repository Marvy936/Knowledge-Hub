# Variables, facts a templates

Ansible používa variables na oddelenie reusable automation logic od rozdielov medzi hosts, groups, environments a run contexts. Facts dopĺňajú runtime informácie o managed nodes a templates premieňajú variables na výsledný textový configuration artifact.

Táto flexibilita je zároveň častým zdrojom nečitateľnosti. Ak rovnaká hodnota môže vzniknúť z inventory, role, playbooku, facts, registered resultu alebo extra vars, bez jasného ownershipu je ťažké vysvetliť, prečo host dostal konkrétnu konfiguráciu.

## 1. Variable ako dátový vstup

Variables môžu obsahovať:

- scalar,
- list,
- dictionary,
- nested combinations,
- hodnotu získanú počas runu,
- fact alebo magic variable.

Príklad:

```yaml
app_port: 8080
app_features:
  - audit
  - metrics
app_database:
  host: db.internal
  port: 5432
```

Referencia používa Jinja expression syntax:

```yaml
- name: Open application port
  ansible.builtin.debug:
    msg: "Application listens on {{ app_port }}"
```

## 2. Variable sources

Variables môžu pochádzať napríklad z:

- role defaults,
- inventory group vars,
- inventory host vars,
- play vars,
- `vars_files`,
- role vars,
- block alebo task vars,
- `include_vars`,
- facts,
- registered results,
- `set_fact`,
- role/include parameters,
- command-line extra vars.

Ansible načíta relevantné definitions a aplikuje precedence rules. Vyššia precedence neznamená, že zdroj je architektonicky správny.

## 3. Variable precedence

Variable precedence je rozsiahly model. Praktické pravidlá:

- role defaults sú zámerne ľahko override-nuteľné,
- host-specific values sú spravidla konkrétnejšie než group defaults,
- explicitné runtime values majú vysokú precedence,
- extra vars majú veľmi vysokú precedence,
- rovnaký name v mnohých sources znižuje vysvetliteľnosť.

Pri návrhu sa nepýtaj iba „čo vyhrá“, ale:

1. kto hodnotu vlastní,
2. na akej úrovni sa smie meniť,
3. či je súčasťou reusable contractu,
4. či ide o secret,
5. ako sa validuje.

## 4. Scope variables

Prakticky možno rozlišovať:

### Global scope

Configuration, environment alebo CLI behavior relevantný pre celý run.

### Play scope

Variables viazané na play a jeho tasks/roles.

### Host scope

Inventory variables, facts, registered results a `set_fact` hodnoty priradené konkrétnemu hostu.

`hostvars` poskytuje prístup k host-scoped dátam iných hosts, ale vytvára cross-host coupling a závislosť od toho, či boli facts alebo variables už dostupné.

## 5. Role defaults a role vars

### Defaults

`defaults/main.yml` definuje overridable public defaults role.

```yaml
example_service_port: 8080
example_service_enabled: true
```

### Vars

`vars/main.yml` má vyššiu precedence a je vhodný skôr pre interné constants, ktoré caller nemá bežne meniť.

Používanie role vars na bežné environment values robí role ťažko konfigurovateľnou.

## 6. Naming a namespacing

Generic names ako `port`, `user` alebo `path` sa ľahko zrazia.

Preferuj domain prefix:

```yaml
example_web_port: 8080
example_web_user: example
example_web_config_path: /etc/example/web.conf
```

Role a collection content má definovať stabilný variable contract s documentation a validation.

## 7. Required a optional values

Optional value môže mať default. Required value má zlyhať s jasným message.

Template alebo task môže použiť `mandatory` filter, assertion alebo explicitnú validation task.

```yaml
- name: Validate required configuration
  ansible.builtin.assert:
    that:
      - example_api_endpoint is defined
      - example_api_endpoint | length > 0
    fail_msg: example_api_endpoint must be configured
```

Fail early je lepší než zlyhanie uprostred rollout-u po čiastočných zmenách.

## 8. Undefined values

Undefined variable typicky spôsobí failure pri evaluation. Filter `default` môže poskytnúť fallback:

```jinja2
workers = {{ example_workers | default(4) }}
```

Nadmerné používanie `default` môže skryť missing required configuration. Default používaj iba tam, kde existuje bezpečný a dokumentovaný fallback.

## 9. Registered variables

Task result možno registrovať:

```yaml
- name: Read application status
  ansible.builtin.command: /opt/example/bin/status --json
  register: example_status
  changed_when: false
```

Použitie:

```yaml
- name: Show version
  ansible.builtin.debug:
    var: example_status.stdout
```

Registered variable existuje pre host, aj keď task skončí skipped alebo failed; presná result štruktúra sa však môže líšiť. Pred prístupom k nested fields over status.

## 10. `set_fact`

`set_fact` vytvorí host-scoped value počas runu:

```yaml
- name: Calculate endpoint
  ansible.builtin.set_fact:
    example_endpoint: "https://{{ inventory_hostname }}:{{ example_port }}"
```

Je vhodný pre runtime-derived hodnoty. Nevhodné použitie:

- simulovanie imperative mutable variables,
- komplikované business transformations,
- skryté cross-play state,
- secrets bez lifecycle.

`cacheable` môže ovplyvniť fact cache a precedence pri ďalších runs. Tento behavior treba testovať s konkrétnou core/cache konfiguráciou.

## 11. Facts

Facts sú údaje objavené o managed node, napríklad:

- OS family a distribution,
- network interfaces a addresses,
- CPU a memory,
- filesystems a mounts,
- hostname,
- Python runtime,
- devices.

Typický prístup:

```yaml
ansible_facts['os_family']
ansible_facts['default_ipv4']['address']
```

Facts sa často získajú module `ansible.builtin.setup` pri začiatku playu.

## 12. `gather_facts`

```yaml
- hosts: all
  gather_facts: true
```

Výhody:

- jednotný runtime context,
- platform-aware branching,
- templates založené na host properties.

Náklady:

- extra connections a runtime,
- dependency na remote Python a fact modules,
- veľký variable payload,
- stale data pri dlhom playbooku,
- potenciálna expozícia system metadata.

Ak facts nepotrebuješ, vypni ich. Ak potrebuješ iba subset, zvažuj explicitný `setup` filter podľa use case.

## 13. Fact caching

Fact cache umožňuje použiť objavené údaje aj mimo okamžitého gather runu.

Musí mať definované:

- backend,
- TTL,
- invalidation,
- encryption/access,
- behavior pri stale values,
- ownership a observability.

Fact cache nie je authoritative CMDB. Runtime host sa mohol zmeniť po poslednom gather-e.

## 14. Custom facts

Managed node môže poskytovať local/custom facts, napríklad cez `facts.d` na podporovaných POSIX systems.

Použitie:

- lokálny application metadata,
- deployment marker,
- site-specific capability.

Riziká:

- target môže fact manipulovať,
- stale file,
- nejednotný format,
- privilege a trust ambiguity.

Custom fact nie je bezpečný dôkaz identity bez ďalšej attestation vrstvy.

## 15. Magic variables

Ansible poskytuje reserved variables opisujúce execution context. Bežné príklady:

- `inventory_hostname`,
- `hostvars`,
- `groups`,
- `group_names`,
- `ansible_play_hosts`,
- `ansible_play_batch`,
- `playbook_dir`,
- `role_path`,
- `ansible_version`.

Magic variable names neprepisuj vlastnými values.

### Cross-host data

```jinja2
{{ hostvars[groups['database'][0]]['ansible_host'] }}
```

Tento pattern je krehký, ak:

- group je prázdna,
- ordering nie je contract,
- `ansible_host` chýba,
- first host nie je leader,
- inventory sa dynamicky zmení.

Lepšie je publikovať explicitný service endpoint contract.

## 16. Templates

Template je source text spracovaný Jinja templating engine-om na control node a následne doručený na target.

Source:

```jinja2
# templates/app.conf.j2
listen_port = {{ example_app_port }}
environment = {{ example_environment }}
{% for peer in example_peers %}
peer = {{ peer }}
{% endfor %}
```

Task:

```yaml
- name: Render application configuration
  ansible.builtin.template:
    src: app.conf.j2
    dest: /etc/example/app.conf
    owner: root
    group: root
    mode: "0640"
  notify: Restart example application
```

## 17. Templating location

Jinja evaluation typicky prebieha na control node v host-specific variable context-e. To znamená:

- filters/plugins musia existovať v execution environment-e,
- local timezone/locale môže ovplyvniť custom logic,
- lookup môže čítať control-node resources,
- rendered secret existuje v controller memory a možno temporary files/logs.

Template nie je vykonávaný managed node Jinja interpreterom.

## 18. Jinja expressions, filters a tests

### Filter

Transformuje hodnotu:

```jinja2
{{ example_hosts | sort | join(',') }}
```

### Test

Vyhodnocuje vlastnosť alebo condition:

```jinja2
{% if example_feature is defined %}
...
{% endif %}
```

### Lookup/query

Načíta dáta z control-node alebo external source podľa pluginu.

Lookup plugin je executable dependency a môže pristupovať k environmentu, filesystemu alebo API. Pinned collections a least privilege sú nevyhnutné.

## 19. Native types a serialization

Variables nie sú vždy strings. YAML, filters a module arguments môžu pracovať s boolean, integer, list a mapping typmi.

Kritické pravidlá:

- nepredpokladaj, že text `false` je boolean `false`,
- serializuj JSON/YAML cez filters namiesto ručného skladania,
- explicitne quote file mode ako string,
- testuj templating pri upgrade `ansible-core` a Jinja behavioru.

Moderné `ansible-core` verzie sprísnili niektoré templating semantics. Content musí byť testovaný proti pinned runtime verzii a porting guide.

## 20. Safe serialization

Pre structured config:

```jinja2
{{ example_config | to_nice_json }}
```

alebo:

```jinja2
{{ example_config | to_nice_yaml }}
```

Neskladaj JSON pomocou string concatenation. Escaping a data types sa ľahko poškodia.

## 21. Template validation

`template` module môže pred replacementom spustiť validation command:

```yaml
- name: Render sudo configuration
  ansible.builtin.template:
    src: sudoers.j2
    dest: /etc/sudoers.d/example
    mode: "0440"
    validate: /usr/sbin/visudo -cf %s
```

Validation znižuje risk neplatného configu, ale musí byť:

- side-effect free,
- dostupná na targete,
- správne quote-nutá podľa module semantics,
- reprezentatívna pre runtime parser.

## 22. Atomic file update

File-oriented modules sa často snažia použiť temporary file a atomic replace. To pomáha zabrániť partial reads.

Atomicity môže zlyhať alebo byť obmedzená na špecifických filesystems, containers či mountoch. `unsafe_writes` alebo obdobné fallbacky zvyšujú risk corruption/race conditions.

## 23. Secrets v variables a templates

`no_log: true` môže obmedziť zobrazenie task arguments/resultu, ale:

- neodstráni secret z target file,
- nechráni pred malicious taskom,
- nezaručí, že callback alebo dependent command secret nevypíše,
- nerieši access k inventory/controller credentials,
- komplikuje troubleshooting.

Secrets majú byť načítané čo najneskôr, používané v najmenšom scope a zapisované iba tam, kde je to nevyhnutné.

## 24. Deterministické templates

Template má pri rovnakom inpute vytvoriť rovnaký output.

Nondeterminism spôsobujú napríklad:

- current timestamp,
- náhodné hodnoty,
- unordered data,
- host-dependent lookup bez contractu,
- volatile external API.

Ak sa do configu zapisuje timestamp pri každom run-e, task bude stále `changed` a handler sa stále spustí.

## 25. Variable validation

Validuj:

- required values,
- allowed enum,
- numeric ranges,
- mutually exclusive options,
- list uniqueness,
- hostname/IP format podľa potreby,
- cross-variable invariants.

Príklad:

```yaml
- name: Validate application inputs
  ansible.builtin.assert:
    that:
      - example_replicas | int >= 1
      - example_environment in ['dev', 'stage', 'prod']
      - example_tls_enabled | bool or example_environment != 'prod'
```

## 26. Troubleshooting

### Variable je undefined

Over exact name, scope, host/group membership, include timing, registered task status a role contract.

### Hodnota je iná než očakávaná

Nájdi všetky definitions a porovnaj precedence. Extra vars alebo role vars často prepisujú nižšie sources.

### Fact chýba

Over `gather_facts`, `setup` success, platform support, remote Python, fact subset/filter a cache freshness.

### Template je stále changed

Porovnaj rendered diff, ordering collections, whitespace, timestamps, generated IDs a line endings.

### Template syntax zlyhá po upgrade

Over pinned `ansible-core`, collection/filter versions a porting guide. Spusti syntax, unit a representative rendering tests.

### Secret sa zobrazil v logu

Okamžite revoke/rotate secret, odstráň log access, audituj použitie a oprav task/callback design. Samotné dodatočné `no_log` nerieši kompromitovaný credential.

## 27. Anti-patterny

### Rovnaká variable definovaná na piatich úrovniach

Precedence nahrádza jasný contract.

### `extra-vars` ako bežná configuration databáza

Najvyššia precedence skryje repository defaults a znižuje reprodukovateľnosť.

### Facts ako permanentný source of truth

Facts sú runtime observation s freshness limitom.

### Celý `hostvars` object v template

Vytvára široký coupling a môže leaknúť citlivé variables.

### Business logika v Jinja template

Configuration generator sa stane nečitateľným programom bez testovateľného contractu.

### Timestamp v každom generated configu

Porušuje idempotenciu bez runtime prínosu.

### `default()` na povinné hodnoty

Missing configuration zostane skrytá.

## 28. Rozhodovací rámec

1. Kto vlastní variable a na akej úrovni sa smie override-nuť?
2. Je variable public role input alebo internal constant?
3. Aký type a validation contract potrebuje?
4. Je hodnota secret a aký má lifecycle?
5. Potrebujem fact, inventory metadata alebo external source?
6. Aká freshness facts je prijateľná?
7. Je cross-host referencia stabilný contract?
8. Je template deterministický a validovaný?
9. Ako sa testuje rendering proti podporovaným versions?
10. Aké logs, diffs a artifacts môžu obsahovať citlivé dáta?

## 29. Kontrolné otázky

1. Aký je rozdiel medzi variable source, scope a precedence?
2. Kedy používať role defaults a kedy role vars?
3. Čo je registered variable?
4. Aké riziká má `set_fact`?
5. Čo sú Ansible facts a magic variables?
6. Prečo fact cache potrebuje TTL?
7. Kde sa renderuje Jinja template?
8. Aký je rozdiel medzi filter, test a lookup?
9. Ako template validation znižuje risk?
10. Prečo `no_log` nie je kompletná secret ochrana?

## Glossary impact

Relevantné pojmy: Ansible variable, variable precedence, variable scope, role defaults, role vars, registered variable, `set_fact`, Ansible facts, fact gathering, fact cache, custom facts, magic variable, `hostvars`, Jinja template, filter, test, lookup plugin, template validation, deterministic template a `no_log`.

## Oficiálna dokumentácia

- [Using variables](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_variables.html)
- [Discovering variables: facts and magic variables](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_vars_facts.html)
- [Templating with Jinja2](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_templating.html)
- [Controlling how Ansible behaves: precedence rules](https://docs.ansible.com/projects/ansible/latest/reference_appendices/general_precedence.html)
- [`ansible.builtin.template`](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/template_module.html)
