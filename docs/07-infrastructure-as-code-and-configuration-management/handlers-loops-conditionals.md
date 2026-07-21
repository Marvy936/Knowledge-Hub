# Handlers, loops a conditionals

Handlers, loops a conditionals riadia, **kedy**, **koľkokrát** a **na základe čoho** sa Ansible task vykoná. Tieto mechanizmy umožňujú vytvárať efektívne a adaptívne playbooks, ale pri nejasnom `changed` stave, nestabilnom loop inpute alebo komplikovaných conditions môžu skryť reálny execution graph.

## 1. Conditionals

Conditional task sa vykoná iba vtedy, keď expression v `when` vyhodnotí pravdivú hodnotu.

```yaml
- name: Install Red Hat package
  ansible.builtin.dnf:
    name: example
    state: present
  when: ansible_facts['os_family'] == 'RedHat'
```

`when` je Jinja expression context, ale expression sa nepíše do `{{ }}`:

```yaml
when: example_enabled | bool
```

Nie:

```yaml
when: "{{ example_enabled }}"
```

## 2. Boolean semantics

Variables môžu pochádzať z YAML, inventory, CLI alebo textového external source. Hodnota string `"false"` nemusí mať rovnaké semantics ako boolean `false`.

Pri inputoch, ktoré môžu byť textové, používaj vedomú konverziu:

```yaml
when: example_enabled | bool
```

Ešte lepšie je validovať type a source contract pred kritickým taskom.

## 3. Viac podmienok

YAML list sa typicky vyhodnocuje ako logical AND:

```yaml
when:
  - example_enabled | bool
  - ansible_facts['os_family'] == 'Debian'
  - example_environment != 'development'
```

OR expression:

```yaml
when: example_environment == 'stage' or example_environment == 'prod'
```

Pri komplexných podmienkach vytvor pomenovaný derived variable alebo assertion. Dlhá inline expression znižuje auditovateľnosť.

## 4. Tests

Jinja/Ansible tests vyhodnocujú vlastnosť hodnoty:

```yaml
when:
  - example_result is defined
  - example_result is succeeded
```

Bežné tests zahŕňajú napríklad:

- `defined` / `undefined`,
- `succeeded` / `failed`,
- `changed`,
- `skipped`,
- type alebo collection tests,
- version comparisons podľa dostupných plugins.

Test a filter nie sú synonymá. Test vracia condition, filter hodnotu transformuje.

## 5. Conditions založené na facts

```yaml
when: ansible_facts['distribution_major_version'] | int >= 9
```

Riziká:

- fact nemusí byť gathered,
- platform field nemusí existovať,
- hodnota môže byť stale z cache,
- string/numeric comparison môže byť nesprávna,
- OS detection nie je vždy dostatočný capability signal.

Preferuj capability checks tam, kde je platform labeling príliš hrubý.

## 6. Conditions založené na registered result

```yaml
- name: Check whether migration is required
  ansible.builtin.command: /opt/example/bin/migration-status
  register: migration_status
  changed_when: false
  failed_when: migration_status.rc not in [0, 3]

- name: Run migration
  ansible.builtin.command: /opt/example/bin/migrate
  when: migration_status.rc == 3
```

Result contract musí byť explicitný. Parsing voľného `stdout` textu je krehkejší než exit codes alebo structured JSON.

## 7. Conditional imports a includes

Condition na static import a dynamic include môže mať odlišné practical semantics.

Dynamic include:

```yaml
- name: Include platform tasks
  ansible.builtin.include_tasks: "{{ ansible_facts['os_family'] | lower }}.yml"
```

Static import môže aplikovať condition na importované tasks pri parse/execution model-i inak, než operator intuitívne očakáva. Pri reusable content-e testuj listovanie, tags a variable availability.

## 8. Loops

Loop opakuje task pre sequence items:

```yaml
- name: Ensure packages are installed
  ansible.builtin.package:
    name: "{{ item }}"
    state: present
  loop:
    - curl
    - jq
    - rsync
```

Loop je host-local. Každý host spracuje vlastný item set v rámci strategy a concurrency modelu.

## 9. Preferovanie module-level list support

Niektoré modules prijmú list priamo:

```yaml
- name: Ensure packages are installed
  ansible.builtin.package:
    name:
      - curl
      - jq
      - rsync
    state: present
```

To môže byť efektívnejšie a atomickejšie z pohľadu package managera než tri oddelené module calls. Vždy over module semantics.

## 10. Loop cez dictionaries

```yaml
- name: Create application users
  ansible.builtin.user:
    name: "{{ item.name }}"
    groups: "{{ item.groups }}"
    state: present
  loop:
    - name: app-reader
      groups: example-readers
    - name: app-writer
      groups: example-writers
```

Data model má byť validovaný. Missing key uprostred loop-u môže zanechať predchádzajúce items aplikované a ďalšie nevykonané.

## 11. `loop_control`

```yaml
- name: Configure endpoints
  ansible.builtin.template:
    src: endpoint.conf.j2
    dest: "/etc/example/endpoints/{{ endpoint.name }}.conf"
  loop: "{{ example_endpoints }}"
  loop_control:
    loop_var: endpoint
    label: "{{ endpoint.name }}"
    index_var: endpoint_index
```

Výhody:

- `loop_var` zabraňuje collision s vnoreným `item`,
- `label` znižuje hlučný output,
- `index_var` poskytuje stabilný index pre diagnostiku.

Label nie je secret protection. Citlivý item môže byť stále v result data.

## 12. Registered loop results

```yaml
- name: Check endpoints
  ansible.builtin.uri:
    url: "{{ item }}"
  loop: "{{ example_urls }}"
  register: endpoint_checks
```

Výsledok obsahuje `results` list. Každá položka môže mať vlastné:

- `item`,
- `changed`,
- `failed`,
- status a module fields,
- attempt metadata.

Downstream logic nemá predpokladať iba jeden top-level `stdout` alebo `rc`.

## 13. Nested loops

Vnorené loops sa často riešia cez `include_tasks` a pomenované `loop_var`:

```yaml
- name: Configure regions
  ansible.builtin.include_tasks: region.yml
  loop: "{{ example_regions }}"
  loop_control:
    loop_var: region
```

Vo vnútri included file používaj `region`, nie implicitný `item`. Inak nested content môže prepisovať outer loop variable.

## 14. Product loops

Cartesian product môže prudko zvýšiť počet operations:

```text
50 hosts × 20 users × 10 permissions = 10 000 task iterations
```

Pred použitím product alebo nested loops odhadni:

- API calls,
- runtime,
- rate limits,
- log volume,
- failure recovery,
- idempotency.

## 15. Lookups a `query`

Loop input môže pochádzať z lookup pluginu. `query()` typicky poskytuje list-oriented interface vhodný pre loops.

```yaml
loop: "{{ query('ansible.builtin.fileglob', 'files/*.conf') }}"
```

Lookup sa často vykonáva na control node a môže čítať files, environment alebo external systems. Je to trust a reproducibility boundary.

## 16. Retries a `until`

Retry loop opakuje rovnaký task, kým condition neprejde alebo sa nevyčerpá limit:

```yaml
- name: Wait for application health
  ansible.builtin.uri:
    url: https://127.0.0.1:8443/health
    validate_certs: false
  register: health_result
  until: health_result.status == 200
  retries: 12
  delay: 5
  changed_when: false
```

Rozlišuj:

- loop cez business items,
- retry tej istej transient operácie.

Retry bez timeout budgetu a klasifikácie permanentných failures predlžuje incident namiesto zvýšenia reliability.

## 17. Handlers

Handler je task spustený na základe notification od changed tasku.

```yaml
- name: Render application configuration
  ansible.builtin.template:
    src: app.conf.j2
    dest: /etc/example/app.conf
  notify: Restart example application

handlers:
  - name: Restart example application
    ansible.builtin.service:
      name: example
      state: restarted
```

Ak template skončí `ok`, handler sa nenotify-ne. Ak skončí `changed`, handler je zaradený do handler queue pre daný host.

## 18. Handler deduplication

Ak viac tasks notify-ne rovnaký handler, handler sa typicky vykoná iba raz v príslušnej handler phase pre host.

To umožňuje:

```text
package changed
config changed
certificate changed
→ jeden service restart
```

Deduplication závisí od handler identity/name alebo listen topic modelu, nie od textovej podobnosti module arguments.

## 19. Handler execution timing

Handlers sa štandardne spúšťajú v definovaných synchronization bodoch, typicky na konci relevantnej play section, nie okamžite po každom notify.

To znamená:

- viac zmien sa skombinuje do jedného restartu,
- downstream task pred handler phase môže stále vidieť starý runtime state,
- failure pred handler phase môže ovplyvniť, či handler prebehne.

Keď downstream task potrebuje nový runtime state, použi explicitný flush s rozvahou.

## 20. `meta: flush_handlers`

```yaml
- name: Apply pending handlers now
  ansible.builtin.meta: flush_handlers
```

Flush vykoná pending handlers v danom execution context-e. Nadmerné používanie ruší batching benefit a komplikuje reasoning.

Použi ho iba pri jasnej dependency:

```text
render config
→ restart service
→ run smoke test against new process
```

## 21. `listen` topics

Viac handlers môže počúvať rovnakú topic:

```yaml
- name: Update application config
  ansible.builtin.template:
    ...
  notify: Reload application stack

handlers:
  - name: Reload web proxy
    ansible.builtin.service:
      name: nginx
      state: reloaded
    listen: Reload application stack

  - name: Restart application
    ansible.builtin.service:
      name: example
      state: restarted
    listen: Reload application stack
```

Topic vytvára event-like contract. Musí mať stabilný name a jasný ownership.

## 22. Handler ordering

Execution order handlers je určený ich resolved definition/order modelom, nie poradím notify statements.

Ak existuje tvrdá dependency medzi handlers, explicitne ju navrhni. Spoliehanie sa na implicitné merge order roles/includes je krehké.

## 23. Handlers a failures

Ak task neskôr zlyhá, notified handler nemusí pre daný host prebehnúť podľa default failure behavioru. To môže zanechať:

- nový config na disku,
- starý service process,
- inconsistent runtime state.

Možnosti zahŕňajú:

- block/rescue recovery,
- explicitné flush pred riskantným downstream krokom,
- `force_handlers` podľa use case,
- transaction-like staging a validation,
- roll-forward task.

`force_handlers` nie je univerzálna oprava; handler môže byť nebezpečný po partial failure.

## 24. Handlers s loops

Ak looping task reportuje change aspoň pre relevantnú iteration, handler sa notify-ne pre host.

```yaml
- name: Render virtual hosts
  ansible.builtin.template:
    src: vhost.conf.j2
    dest: "/etc/nginx/conf.d/{{ item.name }}.conf"
  loop: "{{ virtual_hosts }}"
  notify: Reload nginx
```

Výsledkom má byť jeden reload, nie reload po každom iteme.

## 25. `changed_when` a handlers

Handler correctness závisí od správneho changed signal-u.

```yaml
- name: Run custom configuration tool
  ansible.builtin.command: /opt/example/bin/reconcile
  register: reconcile_result
  changed_when: "'updated' in reconcile_result.stdout"
  notify: Restart example
```

Text parsing je krehký. Preferuj structured output alebo state-aware module.

## 26. Conditions na handlers

Handler môže mať `when`, ale variable context musí byť dostupný pri handler execution time.

Riziká:

- registered variable pochádza iba z niektorých paths,
- condition sa zmení medzi notify a handler phase,
- handler je shared medzi roles s odlišnými assumptions.

Notification contract má byť jednoduchší než samotný handler decision tree.

## 27. Conditions a loops spolu

`when` sa vyhodnotí pre každú iteration:

```yaml
- name: Configure enabled features
  ansible.builtin.template:
    src: feature.conf.j2
    dest: "/etc/example/features/{{ feature.name }}.conf"
  loop: "{{ example_features }}"
  loop_control:
    loop_var: feature
  when: feature.enabled | bool
```

Skipped items zostanú v registered `results` a musia sa pri downstream processingu rozlíšiť.

## 28. Failure v loop-e

Pri failure jednej iteration môže task zlyhať po tom, čo predchádzajúce items už zmenili target.

Navrhni:

- pre-validation celého inputu,
- stable ordering,
- bounded side effects,
- resume/retry semantics,
- cleanup alebo reconciliation,
- per-item evidence.

Loop nie je transakcia.

## 29. Idempotencia

Handlers majú znížiť zbytočné restarts, nie maskovať ne-idempotentné tasks.

Správny model:

```text
state-aware task zistí rozdiel
→ vykoná zmenu
→ reportuje changed
→ notify handler
→ handler zosúladí runtime state
```

Nesprávny model:

```text
shell task je vždy changed
→ service sa vždy restartuje
→ druhý run nikdy nie je clean
```

## 30. Troubleshooting

### Task sa vykonal napriek očakávanej false condition

Over data type, operator precedence, string hodnotu, filter `bool`, undefined fallback a presný host variable context.

### Task je vždy skipped

Zobraz condition input bezpečným debugom, over facts, registered result a include scope. Pri secrets nevypisuj celé objects.

### Loop používa nesprávny `item`

Over nested includes a nastav explicitné `loop_var`.

### Registered loop result nemá očakávané field

Pracuj s `result.results` a rozlíš failed/skipped items.

### Handler sa nespustil

Over:

- notifying task mal `changed: true`,
- exact handler name alebo `listen` topic,
- handler bol loaded,
- host nevypadol pre failure,
- tags/include behavior,
- handler condition.

### Handler sa spustil príliš často

Over unique handler names, viac plays, `flush_handlers`, batch behavior a tasks, ktoré nesprávne reportujú change.

### Retry vyčerpal všetky attempts

Rozlíš transient failure od permanentnej chyby. Ulož posledný result, endpoint status, timeout a dependency evidence.

## 31. Anti-patterny

### `when` expression dlhá desiatky riadkov

Business policy je skrytá v inline syntax.

### String booleans bez validation

`"false"` môže byť interpretované neočakávane.

### Nested loops bez `loop_var`

Inner `item` prepisuje outer context.

### Handler name ako generický `restart service`

Roles môžu vytvoriť collision alebo nejasný notification contract.

### `flush_handlers` po každom tasku

Handler batching stráca význam.

### `force_handlers` globálne

Handler môže bežať po stave, pre ktorý nebol navrhnutý.

### Retry každej chyby

Permanentné validation alebo permission errors sa iba opakujú.

## 32. Rozhodovací rámec

1. Je condition založená na stabilnom a validovanom dátovom type?
2. Je complex decision pomenované a testovateľné?
3. Podporuje module list input bez task loop-u?
4. Aký je počet host × item operations?
5. Potrebujem loop alebo retry?
6. Čo sa stane pri failure uprostred loop-u?
7. Ktorý task presne vlastní changed signal?
8. Kedy musí handler prebehnúť?
9. Ako sa rieši failure pred handler phase?
10. Je notification topic stabilný reusable contract?

## 33. Kontrolné otázky

1. Ako sa zapisuje expression v `when`?
2. Ako sa kombinuje viac conditions?
3. Prečo sú string booleans rizikové?
4. Kedy preferovať module list argument pred loop-om?
5. Čo obsahuje registered result loop-u?
6. Aký je rozdiel medzi loop a `until` retry?
7. Kedy sa handler notify-ne?
8. Prečo sa handler typicky vykoná iba raz?
9. Na čo slúži `flush_handlers`?
10. Ako môže partial failure ovplyvniť handler correctness?

## Glossary impact

Relevantné pojmy: Ansible conditional, `when`, Jinja test, loop, `loop_control`, `loop_var`, registered loop result, retry loop, `until`, handler, notification, handler deduplication, `listen` topic, `flush_handlers`, `force_handlers`, changed signal a partial loop failure.

## Oficiálna dokumentácia

- [Conditionals](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_conditionals.html)
- [Loops](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_loops.html)
- [Handlers: running operations on change](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_handlers.html)
- [Error handling in playbooks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_error_handling.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Variables, facts a templates](variables-facts-templates.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Roles a collections →](roles-and-collections.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
