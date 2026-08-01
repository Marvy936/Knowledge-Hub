# Ansible idempotencia

Ansible idempotencia znamená, že opakovanie rovnakého automation intentu nad už zosúladeným systémom nevytvorí ďalšiu neplánovanú mutation ani side effect. Samotný recap `changed=0` však nie je dôkaz correctness. Run môže stabilne konfigurovať production na staging endpoint, vynechať dva hosts, skryť mutation cez `changed_when: false` alebo preskočiť partial database initialization pre chybný marker. Idempotencia je preto vlastnosť celého subject → observation → mutation → runtime verification chainu, nie YAML syntaxe.

Kapitola pokračuje incidentom `IAC-PAY-79`. Atlas Payments používa custom command s `creates` markerom pre database migration, config template obsahuje timestamp a load-balancer registration používa retry bez idempotency key. Prvý run skončí partial, marker už existuje, druhý run reports no-change a external API obsahuje duplicate registration. Každý task sa tvári stabilne, no systém nekonverguje k správnemu business state-u.

## 1. Dominantný subject-to-convergence lifecycle

Convergence sa posudzuje nad immutable run subjectom a complete target/item inventory. Observation, mutation result, handler/runtime transition a external side effects musia patriť tým istým identities; až potom má second-run `changed=0` význam.

```text
immutable run subject a authoritative desired state
→ complete target/item inventory
→ fresh current-state observation
→ classified delta
→ bounded mutation so stable identity
→ truthful changed/failed/unknown result
→ handler a runtime transition
→ fleet a external-side-effect verification
→ second complete run
→ no unintended change + same correct outcome
→ drift/multi-writer recovery closure
```

## 2. Idempotencia, convergence, reproducibility a correctness

Pre jednu operation formálne platí `f(f(S)) = f(S)`: po dosiahnutí výsledku ďalšie opakovanie nevytvorí nový side effect. Configuration management však potrebuje aj convergence, teda schopnosť priblížiť partial alebo drifted system k desired state-u.

Reproducibility znamená, že rovnaký explicitný source, execution environment, inventory, variables, secret epoch a dependency graph vedú k porovnateľnému behavioru. Correctness je ešte vyššia vrstva: desired state musí byť správny pre business a security intent.

Production host môže stabilne používať staging DB. Druhý run bude `changed=0`, takže task je technicky idempotentný a converged, ale výsledok je business nesprávny. Acceptance preto kombinuje no-change signal s target identity a runtime/business oracle-om.

## 3. Exact convergence subject

```yaml
convergenceSubject:
  sourceRevision: 42ad9c1
  executionEnvironmentDigest: sha256:71ca...
  collectionManifestDigest: sha256:009a...
  inventoryManifestDigest: sha256:f39c...
  expectedHosts: 12
  effectiveConfigurationDigest: sha256:77ef...
  packageVersion: atlas-payments-3.13.0
  migrationEpoch: M27
  secretEpoch: 2026-07-31-02
  externalIdempotencyNamespace: rollout-913
```

„Rovnaký playbook“ nestačí, ak package repository, lookup, inventory, secret epoch alebo collection zmenili resolved subject.

## 4. Fresh current-state observation

```text
stable target identity
→ read current package/file/service/API/migration state
→ normalize representation
→ compare s desired subjectom
→ no-op | update | create | delete | unknown
```

Observation musí čítať celý state, ktorý task tvrdí, že vlastní. File content bez owner/mode/ACL, service `active` bez loaded config version alebo API list bez stable remote ID je neúplný model.

## 5. State-aware module contract

State-aware module musí explicitne pozorovať attributes, ktoré tvrdí, že vlastní, porovnať ich s requested state-om a mutovať iba rozdiel. Contract definuje význam `changed`, check-mode support, normalization a vedľajšie side effects.

```yaml
- name: Ensure Atlas Payments service is enabled and running
  ansible.builtin.service:
    name: atlas-payments
    enabled: true
    state: started
```

Pre konkrétnu module/version/platform kombináciu treba poznať aj failure a unknown-outcome semantics. Service `started` nemusí overovať loaded config alebo business readiness. Custom `changed_when` nesmie prepisovať actual mutation iba kvôli potlačeniu noise.

Module name preto nie je idempotency proof. First/second run sa dopĺňa independent state a runtime observationom a forbidden drift fixture-om.

## 6. Command guards sú slabý observation model

```yaml
- name: Initialize database
  ansible.builtin.command: /opt/atlas/bin/init-db
  args:
    creates: /var/lib/atlas/.db-initialized
```

Marker preukazuje iba existenciu file-u. Nepreukazuje správnu DB identity, schema epoch ani dokončenie operation.

Silnejší migration contract:

```yaml
- name: Read migration ledger
  ansible.builtin.command:
    argv: [/opt/atlas/bin/migration-status, --json]
  register: migration_status
  changed_when: false

- name: Apply migration epoch M27
  atlas.database.migrate:
    epoch: M27
  when: "'M27' not in (migration_status.stdout | from_json).applied_epochs"
```

## 7. Worked failure: marker vznikol pred completion

Script vytvoril `.db-initialized` na začiatku a zlyhal pri tretej schema step.

```text
marker exists
→ second run command skipped
→ partial DB remains
→ recap changed=0
```

Recovery odstráni marker ako authority, zistí actual schema ledger, dokončí alebo compensuje partial steps a pridá postcondition query.

## 8. Truthful result

Read-only task:

```yaml
- name: Read runtime state
  ansible.builtin.command:
    argv: [/opt/atlas/bin/status, --format=json]
  register: atlas_status
  changed_when: false
  failed_when: atlas_status.rc != 0
```

Custom reconciler:

```yaml
- name: Reconcile runtime
  ansible.builtin.command:
    argv: [/opt/atlas/bin/reconcile, --format=json]
  register: atlas_reconcile
  changed_when: (atlas_reconcile.stdout | from_json).changed | bool
  failed_when: (atlas_reconcile.stdout | from_json).status != 'success'
```

`changed_when: false` na mutujúcom tasku falšuje evidence a môže zabrániť handleru.

## 9. Deterministic artifacts

```text
template digest
+ effective values
+ fact/lookup identities
+ filter/Jinja versions
+ canonical ordering
→ artifact digest C44
```

Perpetual-change sources:

- timestamp;
- random value;
- unordered serialization;
- mutable lookup/tag;
- newline/whitespace drift;
- rotating secret bez explicitnej epoch;
- application, ktorá file prepíše.

Timestamp nepatrí do desired configu bez functional dôvodu.

## 10. Artifact verzus loaded runtime

```text
file before != C44
→ template changed
→ handler notification
→ service reload
→ process loaded C44
```

Evidence:

```yaml
- name: Verify loaded config version
  ansible.builtin.uri:
    url: https://127.0.0.1:8443/runtime
    validate_certs: true
    return_content: true
  register: runtime
  changed_when: false
  failed_when: runtime.json.config_version != 'C44'
```

File checksum bez process observation nepreukazuje convergence.

## 11. External API idempotency

Non-idempotent POST potrebuje business-operation identity:

```yaml
- name: Register host in load balancer
  ansible.builtin.uri:
    url: https://lb.example/api/registrations
    method: POST
    body_format: json
    body:
      host_id: "{{ atlas_instance_id }}"
    headers:
      Idempotency-Key: "rollout-913/{{ atlas_instance_id }}/registration"
    status_code: [200, 201]
```

Idempotency key má zostať rovnaký pre retries tej istej logical operation, nie generovať nový pri každom attempt-e.

## 12. Unknown remote outcome

```text
request commitol na serveri
→ response sa stratila
→ controller vidí timeout
```

Pred retry:

```text
query by idempotency key/request ID
→ applied | not-applied | partial | unknown
→ complete, retry alebo compensate
```

Blind retry môže vytvoriť duplicate.

## 13. Worked failure: duplicate registration

Prvý load-balancer POST uspel, response timeoutla a retry bez keya vytvoril druhý record.

Recovery:

1. zachovať request/audit IDs;
2. query remote registrations podľa immutable host ID;
3. vybrať authoritative record;
4. odstrániť duplicate;
5. pridať server-side idempotency identity;
6. verify-nuť exactly one healthy registration.

## 14. Partial failure a resumability

Partial run môže zanechať nový package, nový config file a starý process alebo remote API record bez local response. Nasledujúci run nesmie predpokladať all-applied ani all-rolled-back; musí znovu pozorovať každý owned state component a operation identity.

Resumability potrebuje stable artifact/remote IDs, pre-validation, per-step postconditions, explicitný partial/unknown verdict, recoverable handler a bounded cleanup. Marker alebo recap status nie sú sufficient ledgerom.

Acceptance reprodukuje failure medzi file mutation a handlerom a overí, že ďalší run bezpečne dokončí transition bez duplicate external side effectu.

## 15. Multi-writer oscillation

```text
Ansible run A desired replicas=6
Ansible run B desired replicas=4
```

Oba môžu byť individuálne idempotentné:

```text
A writes 6
→ B writes 4
→ A writes 6
→ B writes 4
```

Systém nekonverguje, pretože chýba jeden authoritative writer a serialized change subject.

## 16. Second-run acceptance

```text
first complete converge
→ verify file/service/API/business outcome
→ second complete run s rovnakým subjectom
→ expect no unintended changed tasks/items
→ verify same runtime outcome
→ cleanup verification
```

Machine-readable summary má obsahovať:

```yaml
convergenceEvidence:
  expectedHosts: 12
  attemptedHosts: 12
  verifiedHosts: 12
  changedTasksFirstRun: 37
  changedTasksSecondRun: 0
  handlerFailures: 0
  externalDuplicateObjects: 0
  runtimeBusinessProbe: pass
  cleanup: complete
```

`changedTasksSecondRun: 0` je iba časť verdictu.

## 17. Allowed recurring transitions

Niektoré transitions sú vedomé, napríklad explicitne triggerovaná short-lived token rotation. Definuj úzky change budget:

```yaml
allowedRecurringChanges:
  - task: rotate-runtime-token
    trigger: token-epoch-changed
forbiddenRecurringChanges:
  - package-install
  - config-render
  - service-restart
  - user-recreation
```

Výnimka potrebuje ownera a test. Široký allowlist maskuje drift.

## 18. Check mode nie je idempotency proof

Check mode je simulation závislá od module supportu a current observations. Tasks založené na registered outpute simulated mutation môžu byť incomplete. citeturn329472search0

Idempotency sa dokazuje reálnym first/second converge v representative isolated targete a runtime oracle-om.

## 19. Competing hypotheses pri perpetual restartoch

H1–H4 porovnávajú exact before/after bytes a metadata: timestamp, random, unstable ordering, mutable lookup alebo owner/mode/ACL oscillation. H5 číta module/version normalization a current-state output. H6/H7 používajú filesystem audit na odhalenie application alebo druhého automation writera.

H8 porovná `changed` result s actual mutation. Task môže reportovať change bez byte/state rozdielu alebo naopak zmenu zatajiť. Každá hypotéza sa testuje na canary s rovnakým immutable subjectom a zachovaným diffom.

Recovery odstráni nondeterministic input alebo ownership conflict a potom vyžaduje runtime correctness aj second no-change run; potlačenie handlera nie je oprava.

## 20. Evidence-preserving containment a recovery

```text
pause scheduled runs
→ preserve first/second-run evidence a file/API timelines
→ identify nondeterministic input alebo second writer
→ remove ownership conflict
→ repair observation/changed contract
→ converge canary
→ verify runtime/business outcome
→ second no-change run
→ resume fleet schedule
```

## 21. Acceptance a forbidden paths

Acceptance vyžaduje complete immutable run subject, fresh current-state observation, truthful results, deterministic artifacts a stable external idempotency identity. Unknown remote outcome sa queryuje pred retry a partial run musí byť resumable.

Forbidden fixtures pokrývajú marker pred completion, mutating task s `changed_when: false`, timestamp template, duplicate POST retry, omitted host a dvoch writerov s opposing values. Každý musí odhaliť neúplnosť alebo konflikt.

Second complete run bez unintended changes je prijatý iba pri complete target coverage a správnom loaded/business outcome-e.

## 22. Anti-patterny

### „Použil som Ansible module, takže task je idempotentný“

Behavior závisí od module/version/platform a observation modelu.

### „`changed=0` znamená správny stav“

Môže byť stabilne nesprávny alebo neúplný.

### „`creates` dokazuje completion“

Dokazuje iba marker existence.

### „Retry je bezpečný pri timeout-e“

Nie pri unknown non-idempotent write outcome-e.

### „Dva idempotentné runy sa nebudú biť“

S odlišným desired state-om vytvoria oscillation.

## 23. Kontrolné otázky

1. Ako sa idempotencia líši od correctness a convergence?
2. Čo musí obsahovať convergence subject?
3. Prečo marker nie je plný state model?
4. Ako `changed_when` ovplyvňuje runtime transition?
5. Prečo deterministic artifact patrí do idempotency?
6. Čo preukazuje file checksum a čo nie?
7. Kedy API retry potrebuje idempotency key?
8. Ako sa rieši unknown remote outcome?
9. Čo robí workflow resumable po partial failure?
10. Ako môžu dva idempotentné writers oscilovať?
11. Čo musí obsahovať second-run evidence?
12. Ako sa testujú forbidden marker, retry a multi-writer paths?

## Glossary impact

Relevantné pojmy: Ansible idempotencia, convergence, correctness, reproducibility, current-state observation, truthful changed signal, deterministic artifact, idempotency key, unknown remote outcome, partial state, resumability, second-run test, change budget, multi-writer oscillation a runtime oracle.

## Primárne zdroje

- [Introduction to modules](https://docs.ansible.com/projects/ansible/latest/module_plugin_guide/modules_intro.html)
- [Check mode and diff mode](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html)
- [Error handling](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_error_handling.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Vault](vault.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Praktický Ansible projekt od inventory po overený rolling configuration rollout →](ansible-practical-walkthrough.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
