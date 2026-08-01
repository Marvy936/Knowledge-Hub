# Handlers, loops a conditionals

Conditionals, loops a handlers nie sú tri nesúvisiace syntax features. Spolu vytvárajú per-host control-flow state machine: condition určí eligibility, loop vytvorí item inventory a per-item operations, `changed` signal agreguje mutation evidence a handler z queued notification vykoná runtime reload alebo restart. Ak je input type, item completeness alebo changed signal chybný, handler môže správne vykonať nesprávnu reakciu alebo sa nevykonať vôbec.

Kapitola uzatvára incident `IAC-PAY-78`. Atlas Payments spravuje sadu proxy virtual-host configurations. Dynamic inventory vráti string `"false"`, ktorý condition vyhodnotí ako truthy a povolí admin listener. Iný host zlyhá na treťom loop iteme po tom, čo prvé dva files zmenil; host sa vyradí pred handler phase. Na ďalšom hoste retry zopakuje non-idempotentný delegated POST a vytvorí duplicate deployment record. Všetky failures vznikajú z neuzavretého per-host/item/handler lifecycle-u.

## 1. Dominantný eligibility-to-runtime lifecycle

Lifecycle je per-host a per-item state machine. Condition rozhoduje eligibility nad typed inputs, loop vytvára complete item inventory, každý item vracia vlastný mutation verdict a handler je až následný synchronization transition do loaded runtime-u. Failure v strede loopu preto môže zanechať partial artifacts bez handlera.

```text
validated host/item inputs a fresh facts
→ condition eligibility decision
→ stable item inventory
→ per-item operation a result
→ aggregate changed/failed/skipped state
→ handler topic notification queue
→ handler synchronization point
→ runtime transition
→ per-host loaded-state verification
→ partial-item recovery a second-run convergence
```

## 2. Condition je policy decision

```yaml
when:
  - atlas_environment == 'prod-eu'
  - vhost.enabled | bool
  - ansible_facts.os_family == 'Debian'
```

Condition subject zahŕňa:

```text
host identity
effective variable values a types
fact/registered-result freshness
current loop item
include/role scope
filter/test implementation
```

Condition false znamená `skipped`, nie automaticky correct. Neplatný alebo chýbajúci critical input má zlyhať preflight assertionom namiesto tichého skipu.

Oficiálna dokumentácia umožňuje conditions nad variables, facts a registered results a odporúča default empty iterator pri optional loop inpute. To je execution mechanism; risk-significant missing collection však nemá byť ticho konvertovaná na empty set. citeturn329472search7

## 3. Boolean a type contract

Rizikový input:

```yaml
atlas_admin_enabled: "false"
```

Riziková condition:

```yaml
when: atlas_admin_enabled
```

Non-empty string môže byť truthy. Bezpečný pattern:

```yaml
- name: Validate admin flag type and value
  ansible.builtin.assert:
    that:
      - atlas_admin_enabled is boolean

- name: Render admin listener
  ansible.builtin.template:
    src: admin.conf.j2
    dest: /etc/atlas/vhosts/admin.conf
  when: atlas_admin_enabled
```

Ak source plugin poskytuje strings, normalizuj a validuj pri boundary. Filter `| bool` znižuje ambiguity, ale nemá ticho prijať arbitrary text bez allowed-value contractu.

## 4. Facts a registered results v conditions

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


```yaml
- name: Read migration status
  ansible.builtin.command:
    argv: [/opt/atlas/bin/migration-status, --json]
  register: migration_status
  changed_when: false
  failed_when: migration_status.rc not in [0, 3]

- name: Run migration
  atlas.database.migrate:
    release: "{{ atlas_release_version }}"
  when:
    - migration_status is succeeded
    - migration_status.rc == 3
```

Skipped alebo failed registered result nemusí mať rovnaké fields. Downstream conditions musia rozlíšiť undefined, skipped, failed a success paths.

## 5. Loop je item inventory, nie transakcia

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


```yaml
- name: Render enabled virtual hosts
  ansible.builtin.template:
    src: vhost.conf.j2
    dest: "/etc/atlas/vhosts/{{ vhost.name }}.conf"
    validate: /usr/sbin/atlas-proxy --check-config %s
  loop: "{{ atlas_virtual_hosts }}"
  loop_control:
    loop_var: vhost
    label: "{{ vhost.name }}"
  when: vhost.enabled | bool
  notify: Atlas proxy configuration changed
```

Execution:

```text
host × item A
host × item B
host × item C
```

Ak C zlyhá, A a B už mohli mutovať target. Loop neposkytuje rollback. Pred mutation sa validuje celý item set.

## 6. Complete item preflight

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


```yaml
- name: Validate virtual-host inventory
  ansible.builtin.assert:
    that:
      - atlas_virtual_hosts is sequence
      - atlas_virtual_hosts | length > 0
      - atlas_virtual_hosts | map(attribute='name') | list | unique | length == atlas_virtual_hosts | length
      - atlas_virtual_hosts | map(attribute='port') | map('int') | min > 0
      - atlas_virtual_hosts | map(attribute='port') | map('int') | max < 65536
    fail_msg: Virtual-host inventory is incomplete or invalid
```

Assertion preukazuje listed invariants pre effective item set. Nepreukazuje port availability, parser success ani absence external config files.

## 7. Stable item identity

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


Item `name` je destination identity:

```text
payments-api → /etc/atlas/vhosts/payments-api.conf
```

Duplicate alebo mutable name môže prepísať iný artifact. Item inventory manifest:

```yaml
- name: Build expected vhost manifest
  ansible.builtin.set_fact:
    atlas_expected_vhosts: >-
      {{ atlas_virtual_hosts
         | selectattr('enabled', 'equalto', true)
         | map(attribute='name')
         | sort
         | list }}
```

## 8. Nested loops a `loop_var`

```yaml
- name: Configure regions
  ansible.builtin.include_tasks: region.yml
  loop: "{{ atlas_regions }}"
  loop_control:
    loop_var: atlas_region
    label: "{{ atlas_region.name }}"
```

Implicitný `item` v outer aj inner loop-e môže prepísať context. Named loop vars sú contract, nie iba readability.

`label` obmedzí zobrazený label, ale full item môže zostať v registered results/callbacks. Nie je to secret protection.

## 9. Registered loop result

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


```yaml
- name: Verify endpoints
  ansible.builtin.uri:
    url: "{{ endpoint.url }}"
    validate_certs: true
    return_content: true
  loop: "{{ atlas_endpoints }}"
  loop_control:
    loop_var: endpoint
  register: endpoint_checks
  changed_when: false
```

Per-item evaluation:

```yaml
- name: Assert every endpoint succeeded
  ansible.builtin.assert:
    that:
      - item.status == 200
      - item.json.release == atlas_release_version
  loop: "{{ endpoint_checks.results }}"
  loop_control:
    label: "{{ item.endpoint.url | default('unknown') }}"
```

Top-level task status nemá nahradiť per-item completeness a identity.

## 10. Retry verzus business loop

Timeout alebo stratená odpoveď nehovoria, či vzdialený side effect prebehol. Operation preto potrebuje stabilný identifier, status lookup alebo server-side deduplication a retry musí použiť rovnaký subject. Bez toho nevzniká complete per-host coverage, pravdivý result a runtime/business read-back, ale riziko duplicate state-u.


`loop` spracúva viac items. `until` opakuje jednu operation pri transient condition:

```yaml
- name: Wait for loaded configuration
  ansible.builtin.uri:
    url: https://127.0.0.1:8443/runtime
    return_content: true
    validate_certs: true
  register: runtime_result
  until:
    - runtime_result.status == 200
    - runtime_result.json.config_version == atlas_release_version
  retries: 12
  delay: 5
  changed_when: false
```

Retry contract:

```text
transient condition
bounded attempts/time
idempotent read alebo mutation identity
last observation evidence
permanent-failure classification
recovery path
```

## 11. Non-idempotent retry a unknown outcome

Delegated POST:

```yaml
- name: Create deployment record
  ansible.builtin.uri:
    url: https://deployments.example/api/deployments
    method: POST
    body_format: json
    body:
      release: "{{ atlas_release_version }}"
      cohort: "{{ ansible_play_batch }}"
    headers:
      Idempotency-Key: "{{ atlas_run_id }}-{{ atlas_batch_id }}"
    status_code: [200, 201]
```

Bez idempotency key môže response timeout po successful commit vyvolať duplicate pri retry. Unknown outcome sa najprv queryuje podľa request ID/idempotency key.

## 12. Handler ako queued runtime transition

Uložený artifact a loaded runtime sú dve odlišné generations. Notification iba zaradí handler; až handler result, process start/version a endpoint dokazujú, že nová konfigurácia bola načítaná. Host sa považuje za converged až po complete per-host coverage, pravdivý result a runtime/business read-back.


```yaml
handlers:
  - name: Reload Atlas proxy
    ansible.builtin.service:
      name: atlas-proxy
      state: reloaded
    listen: Atlas proxy configuration changed
```

Lifecycle:

```text
task pozoruje content delta
→ artifact mutation
→ changed=true
→ topic queued per host
→ handler phase alebo flush
→ reload/restart
→ loaded-state verification
```

Viac notifications sa deduplikuje podľa handler semantics. Handler order nevyplýva jednoducho z poradia notify statements.

## 13. `listen` topic ako reusable event contract

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


```yaml
notify: Atlas proxy configuration changed
```

Topic oddeľuje caller od interného handler name. Musí mať stable, namespaced meaning. Generic `restart service` môže kolidovať medzi roles alebo spustiť viac handlers, než caller očakáva.

## 14. Handler timing a `flush_handlers`

Ak smoke test potrebuje nový loaded state:

```yaml
- name: Render configurations
  ansible.builtin.template:
    # ...
  notify: Atlas proxy configuration changed

- name: Flush pending handlers before verification
  ansible.builtin.meta: flush_handlers

- name: Verify listeners
  ansible.builtin.command:
    argv: [/usr/sbin/atlas-proxy, --runtime-listeners, --json]
  register: listeners
  changed_when: false
```

`flush_handlers` je synchronization point. Môže vykonať všetky pending handlers a meniť restart frequency/failure timing. Každý flush má mať jasný dependency dôvod.

## 15. Partial item failure pred handler phase

Items A a B zmenia files, item C zlyhá pre missing port:

```text
A changed
→ B changed
→ C failed
→ host vypadne
→ queued reload nemusí prebehnúť
→ disk partial-new, process old
```

Spustiť handler naslepo môže načítať incomplete configuration. Recovery najprv validuje complete artifact set.

Silnejší deployment model:

```text
render všetky files do staging directory
→ validate complete directory
→ atomic symlink/directory switch
→ reload
→ runtime verify
```

## 16. Complete-set staging example

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


```yaml
- name: Create staging directory
  ansible.builtin.file:
    path: "/var/lib/atlas/vhosts-{{ atlas_release_version }}"
    state: directory
    owner: root
    group: atlas
    mode: '0750'

- name: Render all enabled vhosts to staging
  ansible.builtin.template:
    src: vhost.conf.j2
    dest: "/var/lib/atlas/vhosts-{{ atlas_release_version }}/{{ vhost.name }}.conf"
    mode: '0640'
  loop: "{{ atlas_virtual_hosts }}"
  loop_control:
    loop_var: vhost
  when: vhost.enabled | bool

- name: Validate complete staged configuration
  ansible.builtin.command:
    argv:
      - /usr/sbin/atlas-proxy
      - --check-directory
      - "/var/lib/atlas/vhosts-{{ atlas_release_version }}"
  changed_when: false

- name: Activate staged configuration
  ansible.builtin.file:
    src: "/var/lib/atlas/vhosts-{{ atlas_release_version }}"
    dest: /etc/atlas/vhosts-active
    state: link
    force: true
  notify: Atlas proxy configuration changed
```

Symlink switch atomicity závisí od filesystem a module behavioru. Runtime stále musí verify-nuť loaded listeners.

## 17. False `changed` signal

Custom task mutuje files, ale `changed_when: false` odstráni noise:

```text
mutation complete
→ changed=false
→ no notification
→ old process state
```

Opačný failure: task vždy reports changed a service sa reštartuje pri každom run-e. Správny changed signal pochádza z state-aware comparison.

## 18. Handler failure a forced handlers

`force_handlers` môže spustiť notified handlers aj po neskoršom failure, ale nepreukazuje, že artifacts sú complete a valid. Reload partial config setu môže incident zhoršiť.

Rozhodovací contract:

```text
complete validated artifact set
→ handler allowed

incomplete/unknown artifact set
→ isolate, restore alebo complete roll-forward
```

## 19. Worked incident: string boolean otvoril admin listener

Incident sa rekonštruuje ako causal chain nad jedným Ansible run, host alebo item subject. Observations určujú prvý divergentný bod v reťazci resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; samy osebe nie sú success alebo failure verdictom. Recovery sa vyberá až po zachovaní evidence a uzatvára ju complete per-host coverage, pravdivý result a runtime/business read-back.


```yaml
atlas_admin_enabled: "false"
```

Condition bez type validation ho vyhodnotila truthy:

```text
admin template rendered
→ changed notification
→ proxy reload
→ production admin exposure
```

Recovery odstráni listener, overí network exposure, opraví inventory typing/preflight a pridá forbidden string-boolean fixture.

## 20. Worked incident: duplicate deployment POST

Prvý delegated POST vytvoril deployment record a server ho commitol, ale response sa stratila. Controller vyhodnotil timeout ako `not applied` a retry bez stabilnej idempotency identity vytvoril druhý record; dva rollout controllers začali spravovať rovnakú cohortu.

Containment zastaví oba controllers a zachová request IDs, audit events, body hash a cohort membership. Remote API sa queryuje podľa immutable run/cohort identity a owner vyberie authoritative record; duplicate sa cancelne až po kontrole, ktorý controller vykonal side effects.

Recovery pridá server-side idempotency key stabilný cez retries jednej logical operation a unknown-outcome lookup pred opakovaním. Acceptance simuluje lost response a musí skončiť presne jedným deployment recordom a jednou active cohort authority.

Prvý POST commitol, response sa stratila a retry bez idempotency identity vytvoril druhý deployment record. Dvaja controllers začali spravovať rovnakú cohortu.


Recovery postupuje cez zastaviť rollout controllers, zachovať request IDs a API audit, určiť authoritative deployment record, cancel/close duplicate, reconcile host cohort a pridať idempotency key a unknown-outcome query.

Poradie chráni evidence a zabraňuje tomu, aby ďalšia mutation prekryla partial alebo unknown outcome.


## 21. Competing hypotheses pri files-new/process-old

H1–H3 skúmajú eligibility a item completeness: condition mohla skipnúť items, input type mohol byť chybný alebo loop skončil partial failureom. Per-item results a expected item manifest určia, ktoré artifacts vznikli.

H4/H5 porovnávajú actual mutation, `changed` signal, notification topic a resolved handler definition. H6/H7 čítajú host task timeline a synchronization point, aby odlíšili host failure pred handler phase od príliš skorého flushu.

H8 porovná active symlink, open files a process-loaded config; H9 overuje direct process observation a cache timestamps. Recovery sa vyberá až po zistení, či je problém v artifact set-e, notification alebo observation path-e.

```text
H1: condition skipla niektoré items
H2: item input type bol chybný
H3: partial loop failure
H4: changed=false zabránil notification
H5: handler topic nebol resolved
H6: host failed pred handler phase
H7: flush prebehol príliš skoro
H8: process číta iný active directory
H9: verifier číta stale endpoint
```


Discriminating evidence porovnáva condition inputs/types a per-item results H1–H3, changed/notify events H4/H5, host task timeline H6/H7, active symlink/open files/process config H8 a direct process observation H9.

Každá observation musí potvrdiť alebo oslabiť konkrétnu hypotézu nad rovnakou identity a časovou osou.


## 22. Evidence-preserving containment a recovery

Containment zastaví ďalšie writers alebo batches a zachová volatile evidence; ešte nemení autoritatívny intent. Recovery opraví prvý chybný transition v reťazci resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome a každý krok read-backne pred ďalšou mutation. Closure nastane až po complete per-host coverage, pravdivý result a runtime/business read-back.


```text
pause ďalšie batches
→ preserve per-item results, file manifest a handler events
→ remove unverified host from traffic
→ classify partial artifact set
→ restore prior set alebo complete roll-forward
→ run handler only after complete validation
→ verify loaded listeners/version
→ verify expected endpoint inventory
→ second converge run
```

## 23. Acceptance a forbidden paths

Acceptance uzatvára celý Ansible run, host alebo item subject, nie iba posledný command. Positive path dokazuje požadovanú capability, forbidden path zachovanie ownership alebo security hranice a recovery/second-operation path stabilitu successor generation. Spoločným oracle-om je complete per-host coverage, pravdivý result a runtime/business read-back.


```text
condition inputs sú typed a validated
+ missing critical list nie je empty no-op
+ item identities sú unique/stable
+ per-item results sú complete
+ retries sú bounded a idempotent
+ changed signal koreluje s mutation
+ handler topic/definition/execution sú auditovateľné
+ partial artifact set sa nereloadne
+ string "false" fixture je odmietnutá
+ duplicate POST fixture sa deduplikuje
+ second run je converged
+ loaded runtime inventory zodpovedá expected setu
```

## 24. Anti-patterny

### „Skipped znamená, že task nebol potrebný“

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


Môže znamenať chybný condition input alebo missing fact.

### „Loop je all-or-nothing“

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


Pred failure mohli viaceré items mutovať target.

### „Retry vyrieši timeout“

Timeout alebo stratená odpoveď nehovoria, či vzdialený side effect prebehol. Operation preto potrebuje stabilný identifier, status lookup alebo server-side deduplication a retry musí použiť rovnaký subject. Bez toho nevzniká complete per-host coverage, pravdivý result a runtime/business read-back, ale riziko duplicate state-u.


Pri unknown non-idempotent mutation môže vytvoriť duplicate.

### „Handler sa spustí hneď“

Uložený artifact a loaded runtime sú dve odlišné generations. Notification iba zaradí handler; až handler result, process start/version a endpoint dokazujú, že nová konfigurácia bola načítaná. Host sa považuje za converged až po complete per-host coverage, pravdivý result a runtime/business read-back.


Je queued do synchronization pointu.

### „`force_handlers` dokončí partial rollout“

`force_handlers` môže vykonať queued handler aj po neskoršom task failure, ale nepreukazuje, že celý artifact set je complete a valid. Reload partial directory môže incident zhoršiť. Handler je povolený až po complete-set validation; inak sa host izoluje a vykoná restore alebo reviewed roll-forward.

Môže načítať incomplete artifact set.

## 25. Kontrolné otázky

1. Čo tvorí condition subject?
2. Prečo string `"false"` môže byť nebezpečný?
3. Ako sa validuje complete item inventory?
4. Prečo loop nie je transakcia?
5. Aký rozdiel je medzi loop a retry?
6. Kedy retry potrebuje idempotency key?
7. Ako `changed` ovplyvňuje handler state machine?
8. Čo `listen` topic poskytuje?
9. Kedy je `flush_handlers` potrebný?
10. Prečo forced handler nemusí byť bezpečný po failure?
11. Ako complete-set staging znižuje partial configuration risk?
12. Ako sa dokazuje loaded runtime state a second-run convergence?

## Glossary impact

Relevantné pojmy: Ansible conditional, eligibility decision, boolean normalization, loop, item identity, loop_var, registered loop result, retry, until, idempotency key, handler, notification topic, listen, flush_handlers, force_handlers, partial item state, staged artifact set a loaded-state verification.

## Primárne zdroje

- [Conditionals](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_conditionals.html)
- [Loops](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_loops.html)
- [Handlers](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_handlers.html)
- [Error handling](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_error_handling.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Variables, facts a templates](variables-facts-templates.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Roles a collections →](roles-and-collections.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
