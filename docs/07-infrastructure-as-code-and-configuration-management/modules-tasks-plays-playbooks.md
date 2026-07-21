# Modules, tasks, plays a playbooks

Ansible automation je vrstvená. Module vykonáva konkrétnu operáciu, task určuje jej arguments a execution controls, play aplikuje ordered tasks na vybranú skupinu hosts a playbook skladá jeden alebo viac plays do orchestration workflowu.

Presné rozlíšenie týchto vrstiev je dôležité pri čítaní výsledkov, návrhu reusable contentu a diagnostike partial failures.

## 1. Module

Module je executable jednotka implementujúca konkrétnu schopnosť. Príklady:

- `ansible.builtin.package`,
- `ansible.builtin.service`,
- `ansible.builtin.user`,
- `ansible.builtin.copy`,
- `ansible.builtin.template`,
- `ansible.builtin.uri`,
- modules z cloud, network alebo vendor collections.

Module má:

- argument schema,
- execution behavior,
- result schema,
- check-mode podporu podľa implementácie,
- idempotency semantics podľa implementácie.

Module nie je automaticky shell command. Väčšina modules sa pokúša načítať current state a vykonať iba potrebnú zmenu.

## 2. Fully Qualified Collection Name

Odporúčaný zápis explicitne uvádza collection namespace:

```yaml
- name: Ensure NGINX is installed
  ansible.builtin.package:
    name: nginx
    state: present
```

FQCN:

- znižuje collision risk,
- ukazuje source contentu,
- zlepšuje documentation lookup,
- uľahčuje dependency review.

Short names môžu byť čitateľné v malom controlled repository, ale v multi-collection prostredí môžu byť nejednoznačné.

## 3. Module arguments

YAML mapping forma:

```yaml
- name: Ensure application user exists
  ansible.builtin.user:
    name: example
    system: true
    shell: /usr/sbin/nologin
    state: present
```

Free-form syntax existuje pri niektorých modules, ale structured arguments sú spravidla čitateľnejšie a jednoduchšie validovateľné.

Pri každom module over:

- required arguments,
- defaults,
- aliases a deprecations,
- platform support,
- check/diff support,
- returned values,
- idempotency caveats.

## 4. Module result

Bežný result môže obsahovať:

```yaml
changed: true
failed: false
msg: configuration updated
```

Ďalšie fields závisia od module. Task môže result uložiť:

```yaml
- name: Query service
  ansible.builtin.command: systemctl is-active example
  register: service_state
  changed_when: false
```

Registered result je host-scoped variable. Pri loop-e obsahuje často `results` list s resultom pre každý item.

## 5. Action plugin

Task syntax môže aktivovať action plugin, ktorý vykonáva control-node časť operácie a koordinuje remote module.

Preto názov task action nemusí znamenať, že celý implementation path beží na managed node. Action plugins môžu napríklad:

- pripravovať alebo transferovať files,
- renderovať templates,
- spracovať includes,
- optimalizovať remote execution,
- meniť result pred návratom engine-u.

## 6. Task

Task je jedna deklarovaná automation operácia aplikovaná na každý relevantný host v aktuálnom play execution context-e.

```yaml
- name: Render application configuration
  ansible.builtin.template:
    src: app.conf.j2
    dest: /etc/example/app.conf
    owner: root
    group: root
    mode: "0644"
  notify: Restart example service
```

Task môže obsahovať execution controls ako:

- `when`,
- `loop`,
- `register`,
- `notify`,
- `become`,
- `delegate_to`,
- `run_once`,
- `retries` a `until`,
- `changed_when`,
- `failed_when`,
- `check_mode`,
- `tags`,
- `environment`.

Task name má vysvetliť desired outcome, nie iba zopakovať module name.

## 7. Task execution per host

Task sa logicky aplikuje na host set playu. Result môže byť odlišný pre každý host:

```text
web-01 → ok
web-02 → changed
web-03 → failed
web-04 → unreachable
```

Ansible preto nepracuje iba s jedným global task resultom. Failure jedného hostu môže odstrániť tento host z ďalšieho play executionu, zatiaľ čo ostatné pokračujú podľa strategy a failure settings.

## 8. Changed state

`changed: true` znamená, že module tvrdí, že task zmenil target state. Je to dôležité pre:

- handlers,
- change reporting,
- idempotency tests,
- audit,
- rollout decisions.

Customizácia:

```yaml
- name: Check application state
  ansible.builtin.command: /opt/example/bin/status
  register: status_result
  changed_when: false
```

Nesprávne `changed_when: false` môže skryť reálnu zmenu. Nesprávne `changed_when: true` môže spúšťať handlers pri každom run-e.

## 9. Failure state

Module failure možno doplniť alebo predefinovať:

```yaml
- name: Validate application health
  ansible.builtin.command: /opt/example/bin/healthcheck
  register: health
  changed_when: false
  failed_when: health.rc not in [0, 2]
```

`failed_when` má reprezentovať domain contract. Nemá sa používať iba na „urobenie pipeline zelenej“.

## 10. Command vs. shell

### `command`

Spustí executable bez shell parsing-u. Je bezpečnejší pri práci s arguments a znižuje shell-injection surface.

```yaml
ansible.builtin.command:
  argv:
    - /usr/bin/examplectl
    - validate
    - /etc/example/app.conf
```

### `shell`

Spustí command cez shell a podporuje pipes, redirects a shell syntax.

Použi ho iba vtedy, keď shell semantics skutočne potrebuješ. Pri untrusted variables musíš riešiť quoting a injection.

Ani `command`, ani `shell` nepoznajú automaticky desired state. Idempotenciu možno podporiť cez `creates`, `removes`, explicitné checks alebo vhodnejší state-aware module.

## 11. Ad hoc command

Ad hoc command vykoná jednu action bez playbooku:

```bash
ansible web -i inventories/prod -m ansible.builtin.ping
```

Je vhodný na:

- connectivity test,
- read-only diagnostiku,
- jednorazový bounded incident action.

Nie je vhodným trvalým change recordom pre opakovateľnú produkčnú konfiguráciu.

## 12. Play

Play mapuje host pattern na ordered automation policy.

```yaml
- name: Configure web servers
  hosts: web
  become: true
  serial: 25%
  vars:
    app_port: 8080
  tasks:
    - name: Install package
      ansible.builtin.package:
        name: example-web
        state: present
```

Play môže definovať:

- `hosts`,
- connection a become policy,
- fact gathering,
- strategy a serial,
- variables,
- pre/post tasks,
- roles,
- tasks a handlers,
- failure thresholds.

## 13. Playbook

Playbook je YAML list plays:

```yaml
---
- name: Configure databases
  hosts: database
  roles:
    - database

- name: Configure application
  hosts: web
  roles:
    - application
```

Plays sa vykonávajú v deklarovanom poradí. Každý play znovu vyhodnotí svoj host pattern a vytvorí vlastný execution context.

Playbook je orchestration document. Nemal by obsahovať všetku detailnú reusable logiku inline; väčší content sa rozdeľuje do roles, task files a collections.

## 14. YAML documents a syntax validation

Playbook musí byť validný YAML a zároveň validný Ansible language document.

```bash
ansible-playbook site.yml --syntax-check
```

Syntax check neoverí:

- target connectivity,
- module runtime behavior,
- remote permissions,
- template result correctness,
- API quotas,
- produkčnú idempotenciu.

## 15. Pre-tasks, roles, tasks a post-tasks

Play môže skladať execution phases:

```yaml
- hosts: web
  pre_tasks:
    - name: Remove node from load balancer
      ...
  roles:
    - application
  tasks:
    - name: Run smoke check
      ...
  post_tasks:
    - name: Return node to load balancer
      ...
```

Tento model je vhodný pre orchestration, ale failure handling musí zabezpečiť, že host nezostane mimo load balancera alebo v maintenance stave bez recovery pathu.

## 16. Includes a imports

Reusable content možno načítať staticky alebo dynamicky.

### Import

Statický import sa spracúva skôr pri parse phase. Tasks sú známe pred execution a spravidla lepšie viditeľné pre listovanie a tags.

### Include

Dynamic include sa vyhodnocuje počas executionu a môže závisieť od runtime variables alebo loop items.

Rozdiel ovplyvňuje:

- variable evaluation,
- condition application,
- tags,
- handler visibility,
- task listing,
- debugging.

Použi explicitný model a testuj edge cases namiesto náhodného miešania.

## 17. Blocks

Block zoskupuje tasks a môže mať spoločné directives:

```yaml
- name: Deploy application
  block:
    - name: Write configuration
      ...
    - name: Restart service
      ...
  rescue:
    - name: Collect diagnostics
      ...
  always:
    - name: Release maintenance lock
      ...
```

`rescue` nie je plná transakčná rollback garancia. Musí poznať, ktoré side effects už nastali.

## 18. Delegation

Task možno vykonať na inom hoste:

```yaml
- name: Remove current host from load balancer
  ansible.builtin.uri:
    url: "https://lb.example/api/nodes/{{ inventory_hostname }}"
    method: DELETE
  delegate_to: localhost
```

Delegation mení:

- execution location,
- connection context,
- dostupné credentials,
- facts a variable interpretation,
- concurrency risk.

Task delegovaný na localhost môže byť spustený paralelne pre mnoho hosts. Shared API alebo file operations preto potrebujú serialization alebo idempotency.

## 19. `run_once`

`run_once: true` vyberie jeden host z aktuálneho batchu na vykonanie tasku.

Nie je to globálny distributed lock. Pri `serial` môže byť task vykonaný raz v každom batchi podľa execution semantics.

Pre globálnu jednorazovú operáciu navrhni explicitný play alebo dedicated host/group a jasný concurrency model.

## 20. Tags

Tags umožňujú vybrať časť contentu:

```yaml
- name: Configure firewall
  ansible.builtin.template:
    ...
  tags:
    - firewall
```

```bash
ansible-playbook site.yml --tags firewall
```

Tags sú operator selection mechanism, nie dependency solver. Spustenie podmnožiny tasks môže preskočiť prerequisites a vytvoriť nevalidný state.

## 21. Check mode

Task alebo playbook možno spustiť s `--check`. Module môže:

- presne predikovať zmenu,
- poskytnúť čiastočnú predikciu,
- byť preskočený,
- vykonať read operácie,
- nepodporovať check mode.

Task, ktorý závisí od resultu predchádzajúceho skipped tasku, môže v check mode zlyhať alebo sa správať inak.

## 22. Diff mode

Diff mode je užitočný pre file a template changes:

```bash
ansible-playbook site.yml --check --diff
```

Diff nemusí existovať pre každý module a môže obsahovať secrets. `no_log` alebo content design musí chrániť citlivé hodnoty.

## 23. Execution strategy a batches

Playbook order je deklarovaný, ale execution medzi hosts závisí od:

- strategy,
- forks,
- serial,
- delegation,
- async operations,
- failures a unreachable hosts.

Pri stateful rolling update definuj:

- batch size,
- health gates,
- maximum failure threshold,
- load balancer coordination,
- handler timing,
- rollback alebo roll-forward.

## 24. Error handling

Dôležité controls:

- `ignore_errors`,
- `ignore_unreachable`,
- `failed_when`,
- blocks s `rescue` a `always`,
- `any_errors_fatal`,
- `max_fail_percentage`,
- handler failure behavior.

Ignorovanie chyby má vytvoriť explicitný degraded state a evidence. Nemá iba odstrániť červenú farbu z runu.

## 25. Idempotency verification

Praktický test:

```text
first run  → očakávané changes
second run → changed=0
```

Výnimky musia byť vysvetlené, napríklad:

- rotating token,
- timestamped artifact,
- external system s nondeterministickým outputom,
- deliberately restarted service.

Druhý run bez changes je silný signal, ale nie dôkaz správnosti. Systém môže byť konzistentne nesprávny.

## 26. Troubleshooting

### `conflicting action statements`

Task obsahuje viac keys interpretovaných ako module/action. Over indentation a module syntax.

### Module neexistuje

Použi FQCN, over collection installation, version a execution environment.

```bash
ansible-doc <fqcn>
```

### Task je skipped

Over `when`, tags, host pattern, check mode, variable value a include/import behavior.

### Task je `ok`, ale target je nesprávny

Module možno porovnáva iba subset state-u alebo external mutation nie je v jeho model-i. Over module documentation a remote state.

### Playbook pokračuje po chybe

Over `ignore_errors`, block/rescue, failure thresholds a či failure nastal iba na niektorých hosts.

### Delegated task sa spustil príliš veľakrát

`delegate_to` nemení host loop. Použi explicitnú aggregation, `run_once`, dedicated play alebo serialization podľa požadovaných semantics.

## 27. Anti-patterny

### Task name `run command`

Neopisuje desired outcome ani dôvod.

### `shell` pre každú operáciu

Stráca state awareness, portability a structured output.

### `ignore_errors: true` bez následnej kontroly

Automation pokračuje v neznámom stave.

### Jeden monolitický playbook

Coupling a blast radius rastú, reusable contracts chýbajú.

### `run_once` ako distributed lock

Pri batches, retries alebo paralelných pipelines neposkytuje potrebnú koordináciu.

### Tags ako alternatívne dependency graphy

Operator môže spustiť nekonzistentnú podmnožinu tasks.

## 28. Rozhodovací rámec

1. Je operácia dostupná cez state-aware module?
2. Kde action a module skutočne bežia?
3. Aký result contract potrebujem registrovať?
4. Čo presne znamená `changed` a `failed`?
5. Patrí logika do tasku, role alebo samostatného playu?
6. Potrebujem static import alebo dynamic include?
7. Aký host concurrency a batch model používam?
8. Ktoré tasks podporujú check/diff mode?
9. Ako sa rieši partial failure a recovery?
10. Ako overím idempotenciu a post-condition?

## 29. Kontrolné otázky

1. Aký je rozdiel medzi module a task?
2. Aký je rozdiel medzi play a playbook?
3. Na čo slúži action plugin?
4. Prečo používať FQCN?
5. Čo znamená `changed` result?
6. Kedy použiť `command` a kedy `shell`?
7. Aký je rozdiel medzi import a include?
8. Prečo `run_once` nie je globálny lock?
9. Čo tags nedokážu garantovať?
10. Ako otestovať idempotenciu playbooku?

## Glossary impact

Relevantné pojmy: Ansible module, FQCN, task, module result, registered variable, changed state, failed state, play, playbook, ad hoc command, static import, dynamic include, block, rescue, delegation, `run_once`, tags, check mode a diff mode.

## Oficiálna dokumentácia

- [Using Ansible playbooks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/index.html)
- [Ansible playbooks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_intro.html)
- [Introduction to modules](https://docs.ansible.com/projects/ansible/latest/module_plugin_guide/modules_intro.html)
- [Controlling where tasks run](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_delegation.html)
- [Error handling in playbooks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_error_handling.html)
