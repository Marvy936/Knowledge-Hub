# Modules, tasks, plays a playbooks

Ansible automation nie je vykonanie YAML súboru ako jedného shell scriptu. Playbook sa rozloží na plays, každý play vyberie host set a execution policy, každý task vytvorí samostatnú operáciu pre každý eligible host a module alebo action/plugin vykoná konkrétnu observation či mutation. Globálny process exit code je iba súhrn. Dôveryhodný verdict musí vedieť, ktoré tasks sa pre ktorý host vykonali, preskočili, zlyhali, boli rescued a aký effective runtime state zostal po handleroch a recovery vetvách.

Kapitola pokračuje incidentom `IAC-PAY-78`. Atlas Payments rollout odstráni current batch z load balancera, nainštaluje package, vyrenderuje config, validuje ho, notify-ne restart handler a po health checku vráti hosts do trafficu. Operátor však použije `--tags config`, čím preskočí package prerequisite. Na jednom hoste config validation zlyhá po zápise file-u, na ďalšom `changed_when` nesprávne vráti false a handler sa nespustí. Playbook môže mať partial green výsledok, ale fleet outcome nie je uzavretý.

## 1. Dominantný intent-to-per-host-transition lifecycle

```text
run intent a resolved target manifest
→ play target, privilege, strategy a batch policy
→ ordered/static/dynamic content graph
→ per-host task eligibility
→ action/plugin/module execution
→ structured result: ok | changed | failed | unreachable | skipped
→ handler, rescue, always alebo host-removal transition
→ per-host postcondition
→ fleet coverage a runtime verification
→ second converge run a recovery closure
```

## 2. Module ako operation contract

Module je executable capability s argument schema, current-state observation behaviorom, mutation semantics a result schema. Oficiálna dokumentácia opisuje modules ako discrete units code používané v ad-hoc commands alebo playbook tasks; module môže vytvoriť change event, ktorý notify-ne handler. citeturn329472search21

```yaml
- name: Ensure payments package is installed
  ansible.builtin.package:
    name: atlas-payments
    state: present
```

FQCN určuje content namespace. Neviaže task automaticky na immutable collection version; tú určuje execution environment a collection manifest.

State-aware module typicky:

```text
pozoruje relevantný current state
→ porovná requested state
→ vykoná bounded mutation, ak treba
→ vráti structured result
```

`command` a `shell` tento model automaticky neposkytujú. Autor musí vyriešiť quoting, idempotency, exit-code semantics, side effects a truthfulness `changed` resultu.

## 3. Task ako per-host invocation

```yaml
- name: Render Atlas configuration
  ansible.builtin.template:
    src: payments.yml.j2
    dest: /etc/atlas/payments.yml
    owner: root
    group: atlas
    mode: '0640'
    validate: /usr/bin/atlas-payments validate --config %s
  notify: Restart Atlas Payments
```

Pre každý target host vzniká vlastný result:

```text
app-01 → ok
app-02 → changed
app-03 → failed
app-04 → unreachable
app-05 → skipped
```

Task result nie je iba UI farba. `changed` môže spustiť handler; `failed` môže host vyradiť z ďalšieho flow; `skipped` môže znamenať legitímnu condition aj chybný variable path.

## 4. Registered result a custom verdicts

```yaml
- name: Read runtime state
  ansible.builtin.command:
    argv:
      - /usr/bin/atlas-payments
      - runtime
      - --json
  register: atlas_runtime
  changed_when: false
  failed_when:
    - atlas_runtime.rc != 0
    - atlas_runtime.stdout | length == 0
```

Registered result je host-scoped. `changed_when` a `failed_when` sú domain verdicty a musia zodpovedať reálnej operation semantics.

False `changed: false`:

```text
file alebo remote state sa zmenil
→ task tvrdí no-change
→ handler notification nevznikne
→ runtime ostane na starom loaded state-e
```

False `changed: true` môže spúšťať zbytočné restarty pri každom run-e a rozbiť idempotency signal.

## 5. Action location a delegation

Task môže vykonávať action logic na controlleri a module na managed node-e. Lookup, template rendering, cloud modules a delegated tasks môžu vykonávať významnú operáciu lokálne.

```yaml
- name: Remove host from load balancer
  company.platform.load_balancer_member:
    host_id: "{{ atlas_instance_id }}"
    state: absent
  delegate_to: localhost
```

`delegate_to` mení execution location, nie host iteration count. Pri dvanástich target hosts môže task vytvoriť dvanásť delegated API calls.

Run evidence oddeľuje:

```text
inventory host identity
connection/become identity
controller execution identity
cloud/API account a region
```

## 6. Play ako target a execution policy

```yaml
- name: Roll out payments configuration
  hosts: payments_app:&production:!maintenance
  gather_facts: true
  become: true
  serial: 2
  max_fail_percentage: 0
  any_errors_fatal: true

  roles:
    - atlas.payments.runtime
```

Play určuje:

- host pattern;
- fact gathering;
- connection/privilege;
- strategy a batch;
- variables a roles;
- pre/tasks/post/handlers;
- failure thresholds.

`serial: 2` obmedzí batch, ale nevytvorí automaticky health gate. Post-task alebo orchestration logic musí potvrdiť, že batch je safe pred pokračovaním.

## 7. Playbook ako orchestration medzi capabilities

```yaml
- name: Validate database compatibility
  hosts: database:&production
  roles:
    - atlas.database.preflight

- name: Roll out application
  hosts: payments_app:&production:!maintenance
  serial: 2
  roles:
    - atlas.payments.runtime
```

Playbook má vyjadrovať orchestration. Reusable detailed implementation patrí do roles/collections. Monolitický playbook s hundreds tasks skrýva ownership, dependencies a support boundaries.

## 8. Kompletný rolling example

```yaml
- name: Roll out Atlas Payments configuration
  hosts: payments_app:&production:!maintenance
  serial: 2
  any_errors_fatal: true
  become: true

  pre_tasks:
    - name: Remove current host from traffic
      company.platform.load_balancer_member:
        instance_id: "{{ atlas_instance_id }}"
        state: absent
      delegate_to: localhost

    - name: Wait until active connections drain
      ansible.builtin.uri:
        url: "https://{{ inventory_hostname }}:8443/metrics/drain"
        return_content: true
        validate_certs: true
      register: drain_status
      until: drain_status.json.active_connections == 0
      retries: 30
      delay: 5
      changed_when: false

  tasks:
    - name: Install supported package version
      ansible.builtin.package:
        name: "atlas-payments-{{ atlas_release_version }}"
        state: present

    - name: Render validated configuration
      ansible.builtin.template:
        src: payments.yml.j2
        dest: /etc/atlas/payments.yml
        owner: root
        group: atlas
        mode: '0640'
        validate: /usr/bin/atlas-payments validate --config %s
      notify: Restart Atlas Payments

    - name: Flush restart before runtime verification
      ansible.builtin.meta: flush_handlers

    - name: Verify loaded version
      ansible.builtin.uri:
        url: https://127.0.0.1:8443/runtime
        return_content: true
        validate_certs: true
      register: runtime_status
      failed_when: runtime_status.json.config_version != atlas_release_version
      changed_when: false

  post_tasks:
    - name: Return host to traffic
      company.platform.load_balancer_member:
        instance_id: "{{ atlas_instance_id }}"
        state: present
      delegate_to: localhost
```

Tento example stále potrebuje account read-back pre delegated API, expected target manifest a fleet-level business verifier.

## 9. Static imports verzus dynamic includes

```yaml
- name: Import invariant preparation
  ansible.builtin.import_tasks: prepare.yml

- name: Include OS-specific tasks
  ansible.builtin.include_tasks: "{{ ansible_facts.os_family | lower }}.yml"
```

Static import sa rozbalí pri parse phase. Dynamic include sa vyhodnotí počas executionu per host/context. Rozdiel ovplyvňuje task visibility, tags, conditions a failure timing.

Production evidence má vedieť, ktorý dynamic path sa pre každý host skutočne načítal.

## 10. Blocks, rescue a always

```yaml
- name: Update one host safely
  block:
    - name: Install configuration
      ansible.builtin.template:
        src: payments.yml.j2
        dest: /etc/atlas/payments.yml
        validate: /usr/bin/atlas-payments validate --config %s
      notify: Restart Atlas Payments

    - name: Flush handlers
      ansible.builtin.meta: flush_handlers

  rescue:
    - name: Capture diagnostics
      ansible.builtin.command:
        argv: [/usr/bin/atlas-payments, diagnostics]
      register: diagnostics
      changed_when: false

    - name: Mark host unavailable for traffic
      ansible.builtin.set_fact:
        atlas_recovery_required: true

  always:
    - name: Record transition closure
      ansible.builtin.debug:
        msg: "recovery_required={{ atlas_recovery_required | default(false) }}"
```

`rescue` nie je rollback transakcia. Pred failure už mohli vzniknúť file, package, API alebo service side effects. Recovery musí inventoryovať confirmed, partial a unknown transitions.

## 11. Tags ako selection, nie dependency graph

```bash
ansible-playbook site.yml --tags config
```

Ak package prerequisite nemá tag `config`, template môže použiť syntax nepodporovanú starým binary.

```text
tag subset
→ prerequisite skipped
→ config mutation prebehne
→ validation/restart failure po side effecte
```

Podporované tag paths potrebujú vlastné tests. Tags nesmú byť ad-hoc alternatívou k complete workflowu.

## 12. `run_once` nie je distributed lock

```yaml
- name: Run shared schema migration
  ansible.builtin.command: /opt/atlas/bin/migrate
  run_once: true
```

Pri batched execution môže semantics závisieť od play/batch flow. `run_once` nepreukazuje global exactly-once, idempotency ani external lock.

Shared migration patrí do samostatného singleton playu alebo external coordination mechanizmu:

```yaml
- name: Run schema migration once
  hosts: migration_controller
  tasks:
    - name: Acquire migration lock and migrate
      atlas.database.migrate:
        release: "{{ atlas_release_version }}"
```

## 13. Delegation a shared API fan-out

Dvanásť inventory hosts vytvorí dvanásť delegated task instances. Ak všetky menia jeden load-balancer listener, môžu konfliktovať.

Riešenia:

- host-specific idempotent member operation;
- aggregation do jednej reviewed manifest mutation;
- `throttle` alebo serializácia;
- samostatný orchestration play;
- external controller.

## 14. Handler semantics a explicitný flush

Handlers sa spúšťajú po notifications. Ak runtime verification musí vidieť loaded config v tom istom play flow, použije sa explicitný `meta: flush_handlers` na správnom mieste.

`flush_handlers` však môže vykonať všetky pending handlers a meniť failure timing. Je to deliberate state transition, nie iba convenience.

## 15. Worked incident: validation failure po file mutation

Template module používa `validate`, ktoré typicky validuje temporary file pred final replace. Custom shell task však najprv prepísal destination a až potom spustil validator.

```text
file mutation complete
→ validator fails
→ host enters rescue
→ service stále beží so starým loaded state
→ disk obsahuje invalid new config
```

Recovery musí rozhodnúť, či obnoviť backup file, opraviť a restartovať alebo host izolovať. Zelený `rescue` branch nesmie konvertovať host na complete success.

## 16. Worked incident: false changed zabránil restartu

Custom command aktualizoval config, ale:

```yaml
changed_when: false
```

bolo pridané na odstránenie noise.

```text
remote mutation
→ result ok/no-change
→ handler not notified
→ process používa starý loaded config
```

Skorší control je state-aware module alebo checksum comparison, nie manuálne potlačenie `changed`.

## 17. Competing hypotheses pri mixed runtime

Symptom: playbook success, dva hosts používajú starú runtime version.

```text
H1: tasks boli skipped condition/include pathom
H2: tags preskočili prerequisite alebo handler definition
H3: task mutoval, ale changed=false
H4: handler notification vznikla, ale handler neprebehol
H5: failure/rescue nechal partial state
H6: verifier kontroloval iba jeden host alebo wrong endpoint
H7: service číta iný config path
H8: hosts neboli v target inventory
```

Dôkazy:

- per-host events a task path H1/H2/H5;
- file checksum, result a notification H3/H4;
- process start time a runtime endpoint H4/H7;
- exact host verifier manifest H6;
- expected/resolved inventory H8.

## 18. Evidence-preserving containment a recovery

1. pozastaviť ďalšie batches;
2. zachovať run events, target manifest, vars fingerprints a file checksums;
3. odstrániť unverified hosts z trafficu;
4. klasifikovať skipped, false-changed, handler-failed a partial-rescue hosts;
5. vykonať najmenší reviewed recovery per host;
6. overiť loaded config/version a local health;
7. vrátiť host do trafficu až po LB health;
8. vykonať fleet-level business journey;
9. spustiť complete second converge run.

## 19. Acceptance a forbidden paths

Execution blok je prijatý, keď:

```text
module/collection identity je pinned
+ expected task path je známy
+ per-host results sú complete
+ changed signal je pravdivý
+ config mutation a handler execution sú korelované
+ rescue/ignored failure nie je complete success
+ delegated API identity je správna
+ unsupported tag subset je odmietnutý
+ batch health gate funguje
+ second full run converguje bez mutation
```

Forbidden tests:

- `--tags config` bez prerequisite;
- false `changed_when` pri mutation;
- delegated staging identity;
- handler failure po file change;
- rescue branch interpretovaný ako pass;
- `run_once` migration v batched flow bez locku.

## 20. Kontrolné otázky

1. Aký rozdiel je medzi module, task, play a playbook?
2. Prečo result patrí per host?
3. Čo FQCN preukazuje a čo nepreukazuje?
4. Ako `changed_when` ovplyvňuje convergence?
5. Čo mení `delegate_to` a čo nemení?
6. Ako sa static import líši od dynamic include?
7. Prečo rescue nie je rollback?
8. Prečo tags nie sú dependency solver?
9. Prečo `run_once` nie je exactly-once guarantee?
10. Kedy je potrebný `flush_handlers`?
11. Aké evidence odlíšia skipped task od handler failure?
12. Ako sa dokazuje complete fleet outcome?

## Glossary impact

Relevantné pojmy: Ansible module, task, play, playbook, FQCN, registered result, changed_when, failed_when, delegation, static import, dynamic include, block, rescue, always, handler flush, tag selection, run_once, per-host task path a partial state.

## Primárne zdroje

- [Working with playbooks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks.html)
- [Introduction to modules](https://docs.ansible.com/projects/ansible/latest/module_plugin_guide/modules_intro.html)
- [Conditionals](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_conditionals.html)
- [Executing playbooks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_execution.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Inventory](inventory.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Variables, facts a templates →](variables-facts-templates.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
