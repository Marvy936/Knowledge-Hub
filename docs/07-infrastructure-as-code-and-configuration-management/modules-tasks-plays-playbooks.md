# Modules, tasks, plays a playbooks

Ansible automation nie je vykonanie YAML súboru ako jedného skriptu. Je to per-host execution graph, v ktorom play vyberie targety a execution policy, task vytvorí operáciu pre každý relevantný host, action plugin pripraví control-node časť a module alebo API call vykoná konkrétnu state transition.

Hlavný model kapitoly:

```text
run intent a resolved target manifest
→ play policy a ordered content graph
→ per-host task eligibility
→ action/module execution
→ structured result: ok | changed | failed | unreachable | skipped
→ handler, rescue alebo host removal transition
→ postcondition a fleet coverage verification
```

Globálny process exit code je iba súhrn. Bez per-host a per-task evidence nemusí dokazovať, že všetky očakávané targety dosiahli desired state.

## 1. Atlas scenár: rolling configuration update

Atlas Payments aktualizuje konfiguráciu na dvanástich application hosts. Jeden host je v maintenance, preto approved target manifest obsahuje jedenásť hosts. Playbook má:

1. odstrániť aktuálny batch z load balancera;
2. nainštalovať podporovaný package;
3. vyrenderovať konfiguráciu;
4. validovať ju;
5. reštartovať službu iba po zmene;
6. overiť runtime verziu a health;
7. vrátiť host do load balancera.

```yaml
- name: Roll out Atlas Payments configuration
  hosts: payments_app
  serial: 2
  any_errors_fatal: true

  pre_tasks:
    - name: Remove current batch from traffic
      company.platform.load_balancer_member:
        host_id: "{{ atlas_host_id }}"
        state: absent
      delegate_to: localhost

  roles:
    - role: company.platform.payments_service

  post_tasks:
    - name: Verify loaded configuration version
      ansible.builtin.uri:
        url: https://127.0.0.1:8443/runtime
        return_content: true
      register: runtime_status
      failed_when: runtime_status.json.config_version != atlas_release_version
      changed_when: false

    - name: Return current batch to traffic
      company.platform.load_balancer_member:
        host_id: "{{ atlas_host_id }}"
        state: present
      delegate_to: localhost
```

Tento scenár spája všetky vrstvy. Module pozná jednu operáciu, task jej dáva arguments a execution controls, play určuje host set a batch policy a playbook skladá traffic, configuration a verification phases.

## 2. Module: operation contract

Module je executable capability s argument schema, state-observation behaviorom a result schema. Používaj Fully Qualified Collection Name:

```yaml
- name: Ensure package is installed
  ansible.builtin.package:
    name: atlas-payments
    state: present
```

FQCN viaže task na konkrétny content namespace. Neviaže ho však automaticky na immutable version; tú určuje resolved collection a execution environment.

State-aware module sa typicky pokúsi:

```text
read relevant current state
→ compare requested state
→ perform bounded mutation, ak treba
→ return structured result
```

`command` a `shell` tento model samy nemajú. Pri shell operácii musí autor explicitne vyriešiť quoting, idempotency, current-state detection, exit-code contract a side effects.

## 3. Task: per-host transition

Task je module/action invocation plus execution policy:

```yaml
- name: Render Atlas configuration
  ansible.builtin.template:
    src: payments.yml.j2
    dest: /etc/atlas/payments.yml
    owner: root
    group: atlas
    mode: "0640"
    validate: /usr/bin/atlas-payments validate --config %s
  notify: Atlas payments configuration changed
```

Pre každý host vzniká samostatný task result. Rovnaký task môže skončiť:

```text
app-01 → ok
app-02 → changed
app-03 → failed
app-04 → unreachable
app-05 → skipped
```

Dôležité result fields zahŕňajú `changed`, `failed`, `skipped`, `msg`, návratový kód a module-specific údaje. Registered result je host-scoped:

```yaml
- name: Read current runtime state
  ansible.builtin.command:
    argv: [/usr/bin/atlas-payments, runtime, --json]
  register: atlas_runtime
  changed_when: false
  failed_when: atlas_runtime.rc != 0
```

`changed_when` a `failed_when` sú domain verdicty. Nesmú iba meniť farbu pipeline. False `changed` môže spustiť zbytočný handler; false `ok` môže zabrániť potrebnému runtime transitionu.

## 4. Action location nie je host pattern

Task syntax môže aktivovať action plugin na control node-e a module na managed node-e. Lookup, template rendering, includes a delegated alebo cloud/API tasks môžu vykonávať významnú časť práce lokálne.

```yaml
- name: Update load-balancer membership
  company.platform.load_balancer_member:
    host_id: "{{ atlas_host_id }}"
    state: absent
  delegate_to: localhost
```

Host context je production application host, ale API identity pochádza z control-node credential chainu. Run evidence preto musí oddeliť:

```text
inventory host identity
connection/become identity
local action identity
remote API account a region
```

## 5. Play: target a execution policy

Play mapuje host pattern na execution context:

```yaml
- name: Configure Atlas application hosts
  hosts: payments_app
  gather_facts: true
  become: true
  serial: 2
  max_fail_percentage: 0
  roles:
    - company.platform.payments_service
```

Play vlastní najmä:

- target pattern;
- connection a privilege policy;
- fact gathering;
- strategy, forks interaction a `serial` batching;
- variables a roles;
- pre-tasks, tasks, post-tasks a handlers;
- failure thresholds.

Každý host má vlastný execution state. Pri failure môže byť odstránený z ďalších tasks, zatiaľ čo ostatné hosts pokračujú podľa strategy a error policy.

## 6. Playbook: orchestration medzi capabilities

Playbook je ordered list plays. Jednotlivé plays môžu cieliť rôzne groups a mať odlišný risk model:

```yaml
- name: Validate database compatibility
  hosts: database
  roles:
    - company.platform.database_preflight

- name: Roll out application
  hosts: payments_app
  roles:
    - company.platform.payments_service
```

Playbook má vyjadrovať orchestration a dependency medzi capabilities. Detailná reusable implementácia patrí do roles alebo collections. Monolitický playbook zvyšuje coupling, zhoršuje testing a skrýva ownership.

## 7. Static imports a dynamic includes

Static import sa rozbalí pri parse phase. Dynamic include sa rozhoduje počas executionu.

```yaml
- name: Load invariant preparation tasks
  ansible.builtin.import_tasks: prepare.yml

- name: Load platform-specific tasks
  ansible.builtin.include_tasks: "{{ ansible_facts.os_family | lower }}.yml"
```

Rozdiel ovplyvňuje task inventory, tags, variable availability, conditions a čas failure. Pri auditovanom production run-e musí byť možné vysvetliť, ktoré dynamic paths sa pre každý host reálne načítali.

## 8. Blocks, rescue a always

Block zoskupuje transitions a zdieľané directives:

```yaml
- name: Update one Atlas host
  block:
    - name: Render configuration
      ansible.builtin.template:
        src: payments.yml.j2
        dest: /etc/atlas/payments.yml
        validate: /usr/bin/atlas-payments validate --config %s

    - name: Restart service
      ansible.builtin.service:
        name: atlas-payments
        state: restarted

  rescue:
    - name: Capture runtime evidence
      ansible.builtin.command: /usr/bin/atlas-payments diagnostics
      changed_when: false

  always:
    - name: Record host transition outcome
      ansible.builtin.debug:
        msg: "host transition closed"
```

`rescue` nie je transakcia. Pred failure už mohli vzniknúť remote side effects. Recovery musí vedieť, ktoré transitions boli potvrdené, ktoré majú unknown outcome a či je bezpečný rollback, roll-forward alebo izolácia hostu.

## 9. Worked failure: tags preskočili prerequisite

Operátor spustí:

```bash
ansible-playbook site.yml --tags config
```

Task na render configu má tag `config`, ale package installation a schema preflight nie. Nový template používa syntax podporovanú iba novým package releaseom.

```text
operator vyberie tag subset
→ task selection nie je dependency graph
→ prerequisite package a preflight sa nevykonajú
→ config sa zapíše na časť hosts
→ validation alebo restart zlyhá po side effects
```

Tags sú selection mechanism, nie bezpečný alternate workflow. Podporované tag paths potrebujú vlastný contract a tests; kritické prerequisites možno označiť `always` iba vtedy, keď ich semantics zodpovedajú každému podporovanému partial runu.

## 10. Worked failure: `run_once` vykonal migráciu v každom batchi

Play používa `serial: 2` a migration task:

```yaml
- name: Run shared schema migration
  ansible.builtin.command: /opt/atlas/bin/migrate
  run_once: true
```

`run_once` vyberá jeden host z aktuálneho batch/execution contextu. Nie je distributed lock ani globálny exactly-once contract.

```text
batch 1 → migration execution
batch 2 → ďalšia run_once selection
batch 3 → ďalšia execution
```

Shared mutation patrí do samostatného playu s explicitným singleton targetom, idempotency key alebo external coordination mechanizmom. Database migration musí mať vlastný subject, lock a verification.

## 11. Worked failure: delegation znásobila shared API mutation

Task delegovaný na localhost zostáva logicky v host loop-e. Dvanásť application hosts môže preto vyvolať dvanásť paralelných volaní na rovnaký load-balancer objekt.

```text
12 inventory hosts
→ 12 task instances
→ delegate_to mení execution location, nie iteration count
→ shared API dostane concurrent conflicting operations
```

Riešením môže byť host-specific idempotent operation, explicitná aggregation, samostatný orchestration play alebo riadená serialization. `run_once` sa nesmie použiť ako náhrada za distributed coordination bez analýzy batches a retries.

## 12. Causal troubleshooting walkthrough: playbook je green, dva hosts stále používajú starý runtime

### 1. Zafixuj execution subject

Zaznamenaj source revision, execution environment digest, collections, resolved target manifest, play pattern, tags/skip-tags, variables, strategy, `serial`, limit a run ID.

### 2. Súťažiace hypotézy

1. Config task bol pre dva hosts skipped cez condition alebo dynamic include.
2. Tags vybrali template, ale nie prerequisite alebo handler definition.
3. Module nesprávne reportoval `changed: false`.
4. Handler bol notified, ale host zlyhal pred handler phase.
5. `ignore_errors` alebo `rescue` konvertovali neuzavretý host state na green run.
6. Delegated verifier kontroloval nesprávny environment alebo iba jeden host.
7. Runtime proces načítava iný config path než ten, ktorý task zmenil.

### 3. Diskriminačné observation points

- parsed/listed task graph a dynamic include decisions;
- per-host task events vrátane skipped/failed/rescued;
- template destination a checksum;
- `changed` result a handler notification queue;
- handler execution event a service process start time;
- effective runtime config version z každého stable host ID;
- traffic membership a batch timeline.

### 4. Containment

Pozastav ďalšie batches. Hosts bez potvrdeného runtime state-u odstráň z trafficu, ak mixed version nie je bezpečná.

### 5. Recovery

- skipped path → oprav condition/include alebo explicitne scoped recovery run;
- false changed signal → oprav module/result contract a spusti handler transition;
- failure pred handlerom → rozhodni bounded restart, revert alebo roll-forward;
- tags gap → obnov podporovaný complete execution path;
- wrong verifier → oprav observation identity a zopakuj fleet verification.

### 6. Over pôvodný outcome

Potvrď všetkých očakávaných host IDs, config checksum, loaded runtime version, service health a traffic inclusion. Druhý complete run má byť no-change okrem vedomých health checks.

### 7. Posuň control skôr

Pridaj expected task/handler evidence, tests podporovaných tag paths, per-host runtime oracle a gate, ktorý neoznačí partial/rescued state ako complete success.

## 13. Referenčné pravidlá

- Module je operation contract; task je per-host invocation a policy.
- FQCN určuje namespace, nie automaticky immutable dependency version.
- Play určuje target a execution policy; playbook skladá capabilities.
- Task result je per host, nie iba globálny.
- `changed` riadi ďalšie transitions a musí byť pravdivý.
- Static import a dynamic include vytvárajú odlišnú task visibility.
- `delegate_to` nemení host iteration count.
- `run_once` nie je globálny lock ani exactly-once garancia.
- Tags nevyjadrujú dependencies.
- `rescue` musí pracovať s už vykonanými side effects.
- Complete success potrebuje per-host runtime a coverage verification.

## 14. Kontrolné otázky

1. Aký je rozdiel medzi module, task, play a playbook?
2. Kde môže action plugin vykonávať prácu?
3. Prečo `changed` nie je iba reporting field?
4. Ako sa líši static import od dynamic include?
5. Prečo tags nie sú dependency solver?
6. Čo `delegate_to` mení a čo nemení?
7. Prečo `run_once` nie je distributed lock?
8. Aké side effects môže zanechať rescued failure?
9. Ktoré evidence odlíšia skipped task od false `changed` resultu?
10. Ako sa dokazuje complete fleet outcome po green run-e?

## Glossary impact

Relevantné pojmy: Ansible operation contract, per-host task transition, play execution policy, playbook orchestration, action execution location, structured module result, changed signal, static import, dynamic include, delegated iteration, batch-scoped `run_once`, rescued partial state, task-path evidence a per-host outcome verification.

## Oficiálna dokumentácia

- [Using Ansible playbooks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/index.html)
- [Ansible playbooks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_intro.html)
- [Introduction to modules](https://docs.ansible.com/projects/ansible/latest/module_plugin_guide/modules_intro.html)
- [Controlling where tasks run](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_delegation.html)
- [Error handling in playbooks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_error_handling.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Inventory](inventory.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Variables, facts a templates →](variables-facts-templates.md)
<!-- KNOWLEDGE-NAVIGATION:END -->