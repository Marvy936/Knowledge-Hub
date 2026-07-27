# Handlers, loops a conditionals

Conditionals, loops a handlers nevytvárajú tri oddelené syntax features. Spolu určujú per-host control-flow state machine: či je operácia eligible, nad ktorými items sa vykoná, ako sa agreguje `changed` signal a kedy sa z queued notification stane runtime transition.

Hlavný model:

```text
validated host inputs a facts
→ task condition
→ stable item inventory
→ per-item operation a result
→ aggregate changed/failed/skipped state
→ handler notification queue
→ handler synchronization point
→ runtime verification
→ recovery alebo convergence closure
```

Ak condition, item inventory alebo changed signal nie je dôveryhodný, handler môže správne vykonať nesprávnu reakciu alebo sa nevykonať vôbec.

## 1. Atlas scenár: virtual-host rollout

Atlas Payments spravuje na každom proxy hoste sadu virtual-host konfigurácií:

```yaml
atlas_virtual_hosts:
  - name: payments-api
    enabled: true
    port: 8443
  - name: payments-admin
    enabled: false
    port: 9443
  - name: payments-metrics
    enabled: true
    port: 9100
```

Playbook má:

1. validovať všetky items;
2. renderovať iba enabled virtual hosts;
3. odstrániť disabled konfigurácie;
4. reloadnúť proxy iba pri reálnej content zmene;
5. overiť, že process načítal presnú očakávanú sadu listenerov.

```yaml
- name: Validate virtual-host contract
  ansible.builtin.assert:
    that:
      - atlas_virtual_hosts | map(attribute='name') | list | unique | length == atlas_virtual_hosts | length
      - atlas_virtual_hosts | map(attribute='port') | map('int') | min > 0

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

Jeden host môže mať v tom istom tasku changed, skipped aj failed items. Handler correctness preto závisí od celého item result setu, nie iba od top-level zelenej farby.

## 2. Condition je eligibility decision

`when` sa vyhodnocuje pre konkrétny host a pri loop-e pre konkrétny item:

```yaml
when:
  - atlas_environment == 'production'
  - vhost.enabled | bool
  - ansible_facts.os_family == 'Debian'
```

Condition subject zahŕňa:

```text
host identity
variable values a types
fact/registered-result freshness
current item
include/role scope
controller runtime a filter/test implementation
```

Complex condition má byť pomenovaná a testovaná. Dlhá inline expression skrýva business policy v task syntaxe.

```yaml
atlas_should_render_vhost: >-
  {{ vhost.enabled | bool
     and atlas_environment in ['stage', 'production']
     and vhost.port | int > 0 }}
```

Pre kritické rozhodnutia je lepší explicitný preflight assertion než tiché skipnutie nevalidnej hodnoty.

## 3. Boolean a type semantics

Hodnota môže prísť ako YAML boolean, string z inventory pluginu alebo extra var. Text `"false"` nie je bezpečné považovať za správne typed boolean bez normalizácie.

```yaml
when: atlas_feature_enabled | bool
```

Filter znižuje ambiguity, ale stále treba validovať allowed source a type contract. Invalid text nemá byť ticho konvertovaný na production decision.

## 4. Facts a registered results v conditions

Fact-based branch:

```yaml
when: ansible_facts.distribution_major_version | int >= 9
```

Registered-result branch:

```yaml
- name: Read migration status
  ansible.builtin.command: /opt/atlas/bin/migration-status --json
  register: migration_status
  changed_when: false
  failed_when: migration_status.rc not in [0, 3]

- name: Run required migration
  ansible.builtin.command: /opt/atlas/bin/migrate
  when: migration_status.rc == 3
```

Condition musí rozlíšiť successful, failed, skipped a undefined result paths. Parsing voľného stdout textu je krehkejší než explicitný exit-code alebo JSON contract.

## 5. Loop je item inventory, nie transakcia

Loop vytvorí sériu per-item operations na každom hoste:

```text
host × item inventory
→ item 1 result
→ item 2 result
→ item 3 result
```

Ak item 3 zlyhá, items 1 a 2 už mohli zmeniť target. Loop neposkytuje automatický rollback.

Pred mutation validuj celý item set:

- uniqueness identity keys;
- required fields a types;
- stable ordering tam, kde má význam;
- forbidden combinations;
- expected item count;
- side-effect a retry semantics.

Ak module podporuje list argument atomickejšie alebo efektívnejšie, preferuj ho pred task loop-om. Semantics však treba overiť v module contracte.

## 6. `loop_control` a nested execution

Explicitný `loop_var` chráni pred collision:

```yaml
- name: Configure Atlas regions
  ansible.builtin.include_tasks: region.yml
  loop: "{{ atlas_regions }}"
  loop_control:
    loop_var: atlas_region
    label: "{{ atlas_region.name }}"
```

Implicitný `item` v nested includes môže prepísať outer context a aplikovať inner operation na nesprávny region alebo host group.

`label` zlepšuje output, ale nechráni secret. Full item môže zostať v registered result alebo callback evente.

## 7. Registered loop result

Registered loop task vracia per-item `results`:

```yaml
- name: Verify Atlas endpoints
  ansible.builtin.uri:
    url: "{{ endpoint.url }}"
  loop: "{{ atlas_endpoints }}"
  loop_control:
    loop_var: endpoint
  register: atlas_endpoint_checks
  changed_when: false
```

Downstream logic musí pre každý result rozlíšiť:

```text
item identity
attempt count
changed
failed
skipped
module-specific status
last observed state
```

Top-level result nesmie nahradiť per-item completeness decision.

## 8. Loop a retry sú odlišné mechanizmy

Business loop spracúva viac predmetov. `until` retry opakuje jednu operation pre transient condition:

```yaml
- name: Wait for loaded configuration version
  ansible.builtin.uri:
    url: https://127.0.0.1:8443/runtime
    return_content: true
  register: runtime_result
  until: runtime_result.json.config_version == atlas_release_version
  retries: 12
  delay: 5
  changed_when: false
```

Retry contract potrebuje:

- maximum attempts alebo total timeout;
- classification transient vs. permanent failure;
- idempotent operation alebo idempotency key;
- last observation a request ID evidence;
- abort a recovery path.

Retry non-idempotent POST-u môže vytvoriť duplicate remote objects, ak prvý request uspel a response sa stratila.

## 9. Handler ako queued runtime transition

Handler sa notify-ne iba keď notifying task reportuje `changed: true`:

```yaml
handlers:
  - name: Reload Atlas proxy process
    ansible.builtin.service:
      name: atlas-proxy
      state: reloaded
    listen: Atlas proxy configuration changed
```

Handler lifecycle:

```text
task detects real state delta
→ task mutates artifact
→ changed signal
→ notification topic queued per host
→ later handler synchronization point
→ runtime reload/restart
→ health a loaded-state verification
```

Viac notifications sa typicky deduplikuje do jedného handler executionu pre host a phase. Handler order vyplýva z resolved definition orderu, nie z poradia notify statements.

## 10. Handler timing a `flush_handlers`

Handler sa štandardne nevykoná okamžite. Downstream task pred handler phase môže vidieť nový file, ale starý process state.

Keď existuje tvrdá dependency:

```text
render config
→ reload process
→ smoke test nového runtime
```

použi explicitný synchronization point:

```yaml
- name: Apply pending Atlas handlers
  ansible.builtin.meta: flush_handlers
```

Nadmerné flushovanie ruší batching a zvyšuje restart frequency. Každý flush má mať jasnú post-handler oracle.

## 11. Worked failure: partial loop mutation bez handler transitionu

Host má tri virtual hosts. Prvé dva templates sa úspešne zmenia. Tretí item má missing `port` a task zlyhá pred handler phase.

```text
item A changed
→ item B changed
→ item C failed
→ host vypadne z ďalšieho execution pathu
→ queued reload sa nevykoná
→ files sú čiastočne nové, process stále používa starý runtime
```

Recovery musí porovnať desired item inventory, files na disku a loaded process state. Možnosti sú doplniť missing input a roll-forwardnúť celý host alebo obnoviť prior complete artifact set. Spustiť handler naslepo môže načítať neúplnú konfiguráciu.

Skorší control: pre-validácia celého item setu a staging directory s complete-set validation pred atomickým activation switchom.

## 12. Worked failure: string boolean aktivoval disabled feature

Dynamic inventory vráti:

```yaml
atlas_admin_enabled: "false"
```

Condition používa priamo value bez validation:

```yaml
when: atlas_admin_enabled
```

Non-empty string sa správa truthy:

```text
text "false"
→ condition je true
→ admin listener sa vyrenderuje
→ handler reloadne proxy
→ production exposure vznikne bez intended approval
```

Fix zahŕňa typed source contract, explicitnú normalizáciu, preflight assertion a post-reload exposure verification.

## 13. Worked failure: retry vytvoril duplicate shared operation

Delegovaný task registruje hosty do external deployment API. Prvý POST uspel, ale response timeoutla. `until` task request zopakuje bez idempotency key.

```text
remote mutation commitla
→ client nepozná outcome
→ retry vytvorí druhý deployment record
→ dva controllers pokračujú v rovnakom rolloute
```

Unknown outcome sa najprv overuje cez request ID alebo remote query. Retry je bezpečný iba pri idempotentnej operation alebo server-side deduplication identity.

## 14. Handler failures a `force_handlers`

Ak host neskôr zlyhá, queued handler nemusí prebehnúť. `force_handlers` môže vynútiť execution, ale nie je univerzálny repair mechanism.

Handler smie bežať po partial failure iba ak sú splnené jeho preconditions. Reload neúplného config setu môže zhoršiť incident. Bezpečnejší model používa block/rescue a explicitne klasifikuje:

```text
artifact set complete a valid → reload
artifact set incomplete → revert alebo isolate
runtime transition unknown → observe pred retry
```

## 15. Notification topics a reusable contract

`listen` topic oddeľuje caller od interného handler názvu:

```yaml
notify: Atlas proxy configuration changed
```

Topic je reusable event contract. Potrebuje namespacing, stable meaning a dokumentáciu. Generic topic `restart service` môže kolidovať medzi roles alebo spustiť viac handlers, než caller očakáva.

Handler condition má byť jednoduchá. Variable context sa môže medzi notify a handler phase zmeniť alebo nemusí existovať na každom path-e.

## 16. Causal troubleshooting walkthrough: files sú nové, ale nie všetky hosts používajú nový runtime

### 1. Zafixuj control-flow subject

Zaznamenaj host IDs, effective inputs a types, fact generation, task/include path, item inventory digest, per-item results, changed signals, handler topic/definition, batch a run ID.

### 2. Súťažiace hypotézy

1. Condition skipla task pre časť hosts alebo items.
2. String/undefined type zmenil boolean decision.
3. Nested loop prepísal `item` a zmenil destination.
4. Item failure nastal po partial mutations.
5. Custom `changed_when` reportoval false no-change.
6. Handler nebol loaded alebo topic kolidoval.
7. Host zlyhal pred handler phase.
8. `flush_handlers` prebehol pred complete artifact setom.
9. Runtime verifier číta stale proces alebo nesprávny endpoint.

### 3. Diskriminačné observation points

- redacted condition inputs a exact type;
- per-host/per-item registered `results`;
- destination inventory a checksums;
- skipped/failed sequence timeline;
- changed result a notify event;
- resolved handler definitions a execution events;
- process start/reload time a loaded config version;
- batch/flush timeline.

### 4. Containment

Pozastav ďalšie batches a hosts bez complete runtime verification odstráň z trafficu. Nevykonávaj globálny forced reload bez validácie artifact setu.

### 5. Recovery

- condition/type error → oprav contract a rerun complete item inventory;
- nested loop collision → použij named loop vars a audit destinations;
- partial item set → complete roll-forward alebo restore prior set;
- false changed signal → oprav result contract a vykonaj bounded handler transition;
- handler resolution problem → oprav topic/load path a testuj role integration;
- stale verifier → použi process-level observation.

### 6. Over pôvodný outcome

Potvrď expected item inventory, artifact checksums, loaded listeners/config version a second-run convergence na každom expected hoste.

### 7. Posuň control skôr

Pridaj typed condition fixtures, complete item pre-validation, per-item evidence, handler integration test a fleet-level loaded-state gate.

## 17. Referenčné pravidlá

- Condition je host/item eligibility decision s typed input subjectom.
- Fact alebo registered result musí byť dostupný a fresh na každom path-e.
- Loop je per-item execution, nie transakcia.
- Nested loops používajú explicitné `loop_var`.
- Registered loop result sa hodnotí po items, nie iba top-level.
- Retry potrebuje transient classification a idempotency.
- `changed` je vstup do handler state machine.
- Handler je queued runtime transition, nie okamžitý side effect.
- `flush_handlers` je synchronization point s explicitnou dependency.
- `force_handlers` nevaliduje partial state.
- Complete success zahŕňa artifact aj loaded runtime state.

## 18. Kontrolné otázky

1. Čo tvorí conditional decision subject?
2. Prečo string `"false"` môže aktivovať task?
3. Čo sa stane pri failure uprostred loop-u?
4. Ako sa líši business loop od retry loop-u?
5. Prečo retry potrebuje idempotency key pri remote POST-e?
6. Kedy sa handler notify-ne?
7. Prečo nový file ešte neznamená nový runtime?
8. Kedy je `flush_handlers` správny synchronization point?
9. Prečo `force_handlers` môže byť po partial failure nebezpečný?
10. Aké evidence dokazujú complete item a runtime convergence?

## Glossary impact

Relevantné pojmy: control-flow subject, conditional eligibility, typed condition input, item inventory, per-item result, partial loop mutation, retry contract, unknown retry outcome, changed aggregation, handler notification queue, handler synchronization point, notification topic contract, forced-handler risk a loaded-runtime convergence.

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
