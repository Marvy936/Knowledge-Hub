# Modules, tasks, plays a playbooks

Ansible automation nie je vykonanie YAML súboru ako jedného shell scriptu. Playbook sa rozloží na plays, každý play vyberie host set a execution policy, každý task vytvorí samostatnú operáciu pre každý eligible host a module alebo action/plugin vykoná konkrétnu observation či mutation. Globálny process exit code je iba súhrn. Dôveryhodný verdict musí vedieť, ktoré tasks sa pre ktorý host vykonali, preskočili, zlyhali, boli rescued a aký effective runtime state zostal po handleroch a recovery vetvách.

Kapitola pokračuje incidentom `IAC-PAY-78`. Atlas Payments rollout odstráni current batch z load balancera, nainštaluje package, vyrenderuje config, validuje ho, notify-ne restart handler a po health checku vráti hosts do trafficu. Operátor však použije `--tags config`, čím preskočí package prerequisite. Na jednom hoste config validation zlyhá po zápise file-u, na ďalšom `changed_when` nesprávne vráti false a handler sa nespustí. Playbook môže mať partial green výsledok, ale fleet outcome nie je uzavretý.

## 1. Dominantný intent-to-per-host-transition lifecycle

Lifecycle sa číta ako rozklad jedného rollout intentu na host-scoped state machines. Play vyberie target a policy, task vytvorí per-host invocation, module vráti structured result a handler/rescue mení ďalší flow. Fleet verdict vzniká až po agregácii complete per-host postconditions a runtime observation.

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

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.

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

Play viaže host pattern na celý execution contract. Určuje, či sa zbierajú facts, akou connection a privilege identity sa tasks vykonajú, aká strategy/batch policy sa použije a ktoré variables, roles, pre/tasks, post/tasks a handlers tvoria content graph.

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

`serial: 2` iba rozdelí target set. Readiness gate musí byť explicitný a failure thresholds sa interpretujú nad current batchom a resolved host countom. Broad `become: true` rozširuje privilege na celý play, preto sa pri mixed tasks preferuje užší block/task scope.

Review subject obsahuje resolved host manifest aj effective play policy. Rovnaký YAML s iným inventory alebo `--limit` nie je rovnaký rollout.

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

Play contract zahŕňa host pattern, fact gathering, connection a privilege, strategy a batch, variables a roles a pre-tasks, tasks, post-tasks a handlers.

Dopĺňa ho failure thresholds.

`serial: 2` obmedzí batch, ale nevytvorí automaticky health gate. Post-task alebo orchestration logic musí potvrdiť, že batch je safe pred pokračovaním.

## 7. Playbook ako orchestration medzi capabilities

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.

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

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.

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

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.

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

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.

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

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.

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

Delegated task sa stále instancuje pre každý inventory host. Dvanásť hosts preto môže vytvoriť dvanásť controller-side API calls, aj keď všetky menia jeden shared listener alebo deployment object.

Ak API podporuje host-scoped idempotent member operation, každý call používa immutable host ID a stable idempotency key. Pri shared manifest-e sa items najprv agregujú do jednej reviewed mutation. `throttle`, `serial` alebo samostatný orchestration play obmedzujú concurrency, ale nenahrádzajú server-side operation identity.

External controller je vhodný, keď shared object potrebuje vlastný reconciliation lifecycle. Evidence vždy oddeľuje inventory host, controller credential/account a remote object identity; `delegate_to: localhost` nie je distributed lock.

Dvanásť inventory hosts vytvorí dvanásť delegated task instances. Ak všetky menia jeden load-balancer listener, môžu konfliktovať.

Shared API mutation môže používať host-specific idempotent member operation, agregáciu do jednej reviewed manifest mutation, `throttle` alebo serializáciu, samostatný orchestration play alebo external controller.

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

H1/H2 sledujú content eligibility: condition, dynamic include alebo tags mohli preskočiť task, prerequisite či handler definition. H3/H4 porovnávajú actual file mutation, `changed` result, notification a handler execution. H5 skúma partial state po failure/rescue.

H6 overuje exact verifier host manifest a endpoint, H7 porovnáva process command line/loaded path s destination file-om a H8 porovnáva expected a resolved inventory. Per-host event timeline spája tieto observations s jedným run ID.

Takto sa odlíši omitted host od false-changed, handler failure alebo stale observation. Aggregate process status bez per-host subjectu nedokáže žiadnu z hypotéz potvrdiť.

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

Discriminating evidence zahŕňa per-host events a task path H1/H2/H5, file checksum, result a notification H3/H4, process start time a runtime endpoint H4/H7, exact host verifier manifest H6 a expected/resolved inventory H8.

Každá observation musí potvrdiť alebo oslabiť konkrétnu hypotézu nad rovnakou identity a časovou osou.

## 18. Evidence-preserving containment a recovery

Ďalšie batches sa pozastavia a zachová sa target manifest, task path, vars fingerprints, per-host results, file checksums a notifications. Unverified hosts sa odstránia z trafficu a klasifikujú ako skipped, false-changed, handler-failed, rescued-partial alebo omitted.

Recovery je najmenšia operation, ktorá uzavrie konkrétny host transition: dokončenie prerequisite, obnova file-u, explicitný handler alebo oprava inventory. Host sa vracia do trafficu až po loaded version a LB health.

Full-fleet business journey a second complete converge run dokazujú, že targeted recovery nevytvorila alternate workflow a že všetky expected hosts dosiahli rovnaký successor subject.

Recovery workflow pozastaviť ďalšie batches, zachovať run events, target manifest, vars fingerprints a file checksums, odstrániť unverified hosts z trafficu, klasifikovať skipped, false-changed, handler-failed a partial-rescue hosts, vykonať najmenší reviewed recovery per host a overiť loaded config/version a local health.

Dopĺňa ho vrátiť host do trafficu až po LB health, vykonať fleet-level business journey a spustiť complete second converge run.

## 19. Acceptance a forbidden paths

Execution acceptance vyžaduje pinned module/collection identity, known task path, complete per-host results a pravdivý `changed` signal. Config mutation musí byť korelovaná s handler executionom a loaded process generation; rescued alebo ignored failure nesmie byť complete success.

Forbidden tests pokrývajú `--tags config` bez prerequisite, false `changed_when`, wrong delegated account, handler failure, rescue-as-pass a `run_once` migration bez external locku. Každý musí zlyhať pred fleet closure.

Po positive batch flow nasleduje second full run bez unintended mutation a business verifier cez serving path.

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

Acceptance matrix pokrýva `--tags config` bez prerequisite, false `changed_when` pri mutation, delegated staging identity, handler failure po file change, rescue branch interpretovaný ako pass a `run_once` migration v batched flow bez locku.

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
