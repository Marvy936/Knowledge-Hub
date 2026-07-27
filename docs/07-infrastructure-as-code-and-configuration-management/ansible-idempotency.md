# Ansible idempotencia

Ansible idempotencia znamená, že opakovanie rovnakého automation intentu nad už zosúladeným systémom nevytvorí ďalšiu neplánovanú mutáciu ani side effect. Samotné `changed: 0` však nestačí: run môže byť stabilne nesprávny, môže skrývať zmenu cez `changed_when: false` alebo môže vynechať časť fleet-u.

Dominantný model je preto širší:

```text
immutable run subject a authoritative desired state
→ fresh current-state observation
→ classified delta
→ bounded mutation so stable identity
→ truthful per-host/per-item result
→ handler a runtime convergence
→ complete fleet verification
→ second-run no-op evidence
→ partial-state, drift a multi-writer recovery
```

Idempotencia je výsledok celého chainu. Nie je to vlastnosť YAML syntaxe, názvu modulu ani jedného `changed_when` výrazu.

## 1. Atlas scenár

Atlas Payments spravuje na dvanástich application hosts:

- package `atlas-payments-3.13.0`;
- configuration artifact `C44`;
- systemd service;
- database migration epoch `M27`;
- registráciu hosta v load balanceri.

Run subject:

```text
playbook revision: A417
execution image: EE93
collection set: CS18
inventory subject: INV-882
expected hosts: app-01..app-12
effective config: C44
package version: 3.13.0
migration epoch: M27
external API idempotency namespace: rollout-913
```

Desired outcome:

```text
všetkých 12 hosts má package 3.13.0
+ file checksum C44
+ process načítal C44
+ migration M27 je aplikovaná práve raz
+ každý healthy host je registrovaný práve raz
+ druhý complete run nevytvorí nečakanú zmenu
```

## 2. Idempotencia, convergence a correctness

Formálny model jednej operácie `f` nad stavom `S` je:

```text
f(f(S)) = f(S)
```

Configuration management však potrebuje tri odlišné vlastnosti:

### Idempotencia

Opakovanie už úspešnej operácie nemení výsledný stav znova.

### Convergence

Opakované vykonanie vedie systém k stabilnému desired state-u aj po partial failure alebo drift-e.

### Correctness

Desired state zodpovedá skutočnému business a security intentu.

Príklad:

```text
playbook konzistentne nastaví staging database endpoint v production
→ druhý run je changed=0
→ operácia je idempotentná
→ systém konverguje
→ výsledok je stále nesprávny
```

Preto acceptance nemôže byť iba second-run `changed=0`. Potrebuje runtime oracle.

## 3. Run a state subject

Idempotency test je platný iba pre rekonštruovateľný subject:

```text
source revision
execution environment a collections
inventory a target manifest
effective variables a secret epochs
facts/lookups a freshness
external dependency versions
desired artifact identities
controller run a concurrency context
```

„Rovnaký playbook“ nemusí znamenať rovnaký input. Package repository, DNS, fact cache, secret manager alebo dynamic inventory sa mohli zmeniť.

Ak `state: latest` dnes nainštaluje inú verziu než včera, task môže byť idempotentný voči aktuálnemu repository, ale run nie je reprodukovateľný v čase.

## 4. Current-state observation

Každá mutácia potrebuje observation model:

```text
stable target identity
→ read relevant current state
→ normalize provider/module representation
→ compare s authoritative desired state
→ classify no-op, update, create, delete alebo unknown
```

Observation musí čítať celý stav, ktorý task tvrdí, že vlastní.

Ak template task spravuje content, owner, group a mode, všetky tieto fields sú súčasťou porovnania. Ak ďalší actor mení ACL alebo ownership, vznikne recurring drift.

Observation môže byť nepresná pre:

- eventually consistent API;
- server-side defaults;
- unordered rules;
- computed fields;
- stale facts;
- neúplný module schema;
- process, ktorý načítava iný file než ten na disku.

## 5. Declarative modules a operation contract

State-aware module typicky vykonáva:

```text
read current state
→ compare relevant attributes
→ mutate iba rozdiel
→ return changed/result
```

Príklad:

```yaml
- name: Ensure Atlas Payments is enabled and running
  ansible.builtin.service:
    name: atlas-payments
    enabled: true
    state: started
```

Názov modulu však nie je dôkaz. Contract treba overiť pre konkrétnu version a platformu:

- ktoré attributes číta a vlastní;
- ako normalizuje hodnoty;
- či podporuje check mode;
- čo znamená `changed`;
- ako rieši replacement alebo restart;
- aké external defaults nevie modelovať.

## 6. Command guard nie je plný state model

`creates` a `removes` môžu ohraničiť command:

```yaml
- name: Initialize Atlas Payments database
  ansible.builtin.command: /opt/atlas/bin/init-db
  args:
    creates: /var/lib/atlas/.db-initialized
```

Marker odpovedá iba na otázku „existuje file?“. Neodpovedá:

- či database initialization uspela;
- či marker patrí správnej database;
- či schema version je správna;
- či command skončil pred všetkými side effects;
- či sa zmenili inputs.

Silnejší contract používa migration ledger alebo structured status API:

```text
read database identity a schema epoch
→ determine missing migration M27
→ apply M27 so stable migration ID
→ commit ledger entry M27
→ verify schema invariant
```

## 7. Truthful result contract

Ansible potrebuje rozlišovať:

```text
success/no change
success/changed
skipped
failed permanent
failed transient
unknown remote outcome
acceptable absent state
```

Read-only command:

```yaml
- name: Read Atlas Payments state
  ansible.builtin.command:
    argv:
      - /opt/atlas/bin/status
      - --format=json
  register: atlas_status
  changed_when: false
  failed_when: atlas_status.rc != 0
```

Custom reconciler:

```yaml
- name: Reconcile Atlas Payments configuration
  ansible.builtin.command:
    argv:
      - /opt/atlas/bin/reconcile
      - --format=json
  register: atlas_reconcile
  changed_when: (atlas_reconcile.stdout | from_json).changed | bool
  failed_when: (atlas_reconcile.stdout | from_json).status != 'success'
```

`changed_when: false` na mutujúcom tasku iba falšuje evidence. Môže zabrániť handleru a vytvoriť green run s old runtime state-om.

## 8. Deterministic artifacts

Pri rovnakom artifact subjecte musí render vytvoriť rovnaký obsah:

```text
template digest
+ effective values
+ filter/plugin versions
+ canonical ordering/serialization
→ configuration artifact digest C44
```

Zdroje perpetual change:

- timestamp každého runu;
- random value;
- unordered dictionary alebo set;
- mutable lookup;
- newline alebo whitespace drift;
- secret version bez explicitnej epoch;
- locale/timezone-dependent custom filter.

Nevkladaj do managed configu:

```jinja2
# Generated at {{ ansible_date_time.iso8601 }}
```

ak timestamp nie je runtime requirement. Inak sa artifact mení pri každom run-e a handler sa stále spúšťa.

## 9. Changed signal a runtime transition

File mutation a runtime convergence sú odlišné transitions:

```text
artifact before ≠ artifact C44
→ template changed
→ handler notification
→ process reload/restart
→ loaded runtime C44
```

Ak artifact už je C44, handler nemá bežať. Ak artifact sa zmenil a `changed` je false, runtime zostane na starej verzii.

Dôkaz preto obsahuje:

- destination checksum;
- `changed` result;
- handler notification a execution;
- process start/reload time;
- loaded configuration version;
- health a traffic membership.

## 10. External API a idempotency identity

Rovnaké HTTP arguments neznamenajú idempotentnú operáciu.

```text
POST /register-host
```

môže pri opakovaní vytvoriť duplicate registráciu. Bezpečný model potrebuje podľa API:

- stable remote object ID;
- GET/read-before-write;
- upsert alebo compare-and-set;
- idempotency key;
- request ID a audit;
- known conflict semantics;
- bounded retry;
- reconciliation po timeout-e.

Idempotency key musí byť viazaný na business operation, nie na jednotlivý network attempt:

```text
rollout-913/app-07/load-balancer-registration
```

## 11. Unknown remote outcome

Timeout neznamená, že operácia neprebehla.

```text
controller odošle request
→ server commitne mutation
→ response sa stratí
→ Ansible vidí timeout
```

Blind retry môže vytvoriť duplicate side effect.

Pred retry:

```text
lookup podľa idempotency key alebo request ID
→ read remote object state
→ classify not-applied, applied, partial alebo unknown
→ retry, complete alebo compensate
```

## 12. Partial failure a resumability

Scenár:

```text
package updated
→ config C44 published
→ validation task fails
→ handler neprebehne
```

Host je v mixed state:

```text
new package + new file + old process
```

Nasledujúci run musí current state znovu prečítať a bezpečne pokračovať. Nemá predpokladať, že predchádzajúci run bol celý applied alebo celý rolled back.

Resumable workflow potrebuje:

- stable identities pre artifacts a external operations;
- pre-validation pred rozsiahlymi mutations;
- per-step postconditions;
- recoverable handlers;
- cleanup temporary state-u;
- explicitný partial verdict;
- scoped recovery run.

## 13. Worked failure: marker vznikol pred dokončením operácie

Initialization script vytvoril `.db-initialized` na začiatku a potom zlyhal pri tretej schema zmene.

```text
marker exists
→ ďalší run preskočí command cez creates
→ database ostáva partial
→ changed=0 vyzerá ako idempotentný success
```

Root cause je slabý observation contract. Marker sa nesmie stať authoritative dôkazom pred commitom celej operácie. Použi schema ledger a postcondition query.

## 14. Worked failure: retry vytvoril duplicate side effect

Task registruje host do load balancera cez non-idempotentný POST. Server operáciu vykonal, ale response timeoutla. `retries: 3` odoslal rovnaký request znova a vytvoril dve registrations.

```text
unknown remote outcome
→ retry bez stable idempotency identity
→ druhý create
→ duplicate traffic entry
```

Retry contract musí rozlišovať transient read failure od unknown write outcome a používať idempotency key alebo remote reconciliation.

## 15. Worked failure: `changed=0`, ale runtime je nesprávny

Task používal:

```yaml
changed_when: false
```

na custom command, ktorý prepísal config. Handler sa nenotify-ol.

```text
file je C44
+ process stále používa C43
+ recap changed=0
→ green second run neznamená convergence
```

Oprava vyžaduje truthful structured result a process-level loaded-config oracle.

## 16. Worked failure: concurrent writers vytvorili oscillation

Dva controller jobs začali s rozdielnymi variables:

```text
run A desired replicas=6
run B desired replicas=4
```

Oba prečítali current value 5 a postupne zapisovali svoj výsledok.

```text
A writes 6
→ B writes 4
→ scheduled A writes 6
→ scheduled B writes 4
```

Každý run môže byť individuálne idempotentný voči vlastnému intentu. Systém ako celok nekonverguje, pretože chýba jeden authoritative writer a concurrency boundary.

## 17. Second-run test

Základný acceptance lifecycle:

```text
create isolated representative target
→ first complete converge
→ verify desired runtime outcome
→ second complete converge s rovnakým subjectom
→ expect no unintended changes
→ verify runtime outcome znova
→ cleanup a verify cleanup
```

Machine-readable verdict má sledovať:

```text
expected hosts
resolved hosts
attempted hosts
verified hosts
changed tasks/items
handler transitions
external side-effect IDs
runtime invariants
cleanup verdict
```

`changed=0` je iba jedna položka.

## 18. Change budget

Niektoré recurring changes môžu byť vedomé, napríklad short-lived token refresh. Namiesto globálneho ignorovania definuj krátky allowlist:

```text
allowed recurring transition:
- rotate runtime token epoch podľa explicitného triggeru

forbidden recurring transitions:
- package update
- config rewrite
- service restart
- user recreation
```

Každá výnimka potrebuje ownera, dôvod, scope a test. Permanentný široký allowlist maskuje drift.

## 19. Causal troubleshooting walkthrough: service sa reštartuje pri každom run-e

Atlas Payments je healthy, ale každý scheduled run prepíše config a reštartuje všetkých dvanásť hosts.

### 1. Zafixuj run subject

Zaznamenaj source revision, execution environment, inventory, effective values, fact/lookup generations, template digest, destination checksums, module versions a competing writer inventory.

### 2. Súťažiace hypotézy

1. Template obsahuje timestamp alebo random value.
2. Input collection má nestabilné ordering.
3. Secret lookup vracia vždy novú version.
4. Newline, owner, group, mode alebo ACL sa mení medzi runs.
5. Module/provider normalizuje remote value odlišne.
6. Package script alebo application prepisuje file po Ansible run-e.
7. Dva automation systems majú odlišný desired state.
8. `changed_when` nesprávne reportuje change bez mutation.
9. Verifier porovnáva iný file než process používa.

### 3. Diskriminačné observation points

- exact before/after diff a checksums;
- redacted effective-value manifest;
- sorted/canonical render fixture;
- secret epoch a lookup request identity;
- file metadata, ACL a audit writer timeline;
- module raw result a normalization;
- process open-file/config path;
- controller/job overlap timeline;
- handler notifications a process restart events.

### 4. Containment

Pozastav scheduled writes alebo zníž rollout na canary, ak restarty ovplyvňujú availability. Nepridávaj `changed_when: false`, kým nie je známa príčina.

### 5. Recovery

- nondeterministic render → canonicalizuj inputs a odstráň volatile fields;
- secret churn → viaž render na explicitnú epoch;
- metadata drift → urč authoritative ownera a spravuj celý contract;
- provider normalization → uprav desired canonical representation alebo upgrade-ni module;
- second writer → odstráň write path alebo transferuj ownership;
- false result → oprav structured `changed` contract;
- wrong path → zosúlaď artifact destination a runtime source.

### 6. Over pôvodný outcome

Spusti first recovery converge, potvrď loaded C44 a health. Potom spusti druhý complete run: žiadny nečakaný artifact diff, žiadny handler restart a všetkých dvanásť hosts runtime-verified.

### 7. Posuň control skôr

Pridaj deterministic render regression test, second-converge gate, writer audit, explicit secret epoch a process-level loaded-artifact verifier.

## 20. Concurrency a ownership

Idempotencia jedného tasku nerieši multi-writer race. Potrebné controls môžu byť:

- controller job serialization;
- deployment lock;
- resource-specific mutex;
- API optimistic concurrency/version field;
- idempotency key;
- one-writer ownership policy;
- audit alert na neznámu mutation identity.

Rovnaký file alebo attribute nemajú súčasne spravovať Ansible, package script, application self-configuration, človek cez SSH a druhý controller bez explicitného ownership contractu.

## 21. Referenčné pravidlá

- Idempotencia, convergence, correctness a reproducibility sú odlišné vlastnosti.
- Run subject musí zahŕňať resolved external inputs.
- Current-state observation musí pokryť celý owned state.
- Command guard je zjednodušený state model, nie dôkaz correctness.
- `changed_when: false` nemôže nahradiť truthful mutation evidence.
- Deterministic artifact je predpoklad stabilného handler behavioru.
- File state a loaded process state sú samostatné postconditions.
- Retry write operácie potrebuje idempotency identity alebo reconciliation.
- Unknown timeout outcome sa nesmie automaticky opakovať.
- Partial failure potrebuje resumable current-state-based recovery.
- Second-run `changed=0` musí byť spojený s runtime a host coverage verification.
- Jeden idempotentný writer nezaručuje convergence pri viacerých writers.

## 22. Kontrolné otázky

1. Ako sa líši idempotencia, convergence a correctness?
2. Čo tvorí Ansible idempotency subject?
3. Prečo `creates` marker nemusí dokazovať správny stav?
4. Ako false `changed` signal poškodí handler convergence?
5. Prečo deterministic template potrebuje canonical inputs?
6. Čo je unknown remote outcome a prečo je blind retry nebezpečný?
7. Ako navrhnúť resumable run po partial failure?
8. Čo musí obsahovať second-converge verdict okrem `changed=0`?
9. Prečo dva individuálne idempotentné runs môžu vytvoriť oscillation?
10. Aké observation points odlíšia volatile input od competing writera?

## Glossary impact

Relevantné pojmy: Ansible idempotency subject, current-state observation contract, truthful changed signal, deterministic artifact, second-converge evidence, runtime convergence, command guard, unknown write outcome, resumable partial state, recurring-change budget, idempotency key, multi-writer convergence a consistently wrong state.

## Oficiálna dokumentácia

- [Validating tasks with check and diff mode](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html)
- [Error handling and changed conditions](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_error_handling.html)
- [Ansible Lint: no-changed-when](https://docs.ansible.com/projects/lint/rules/no-changed-when/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Vault](vault.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Terraform vs. Ansible →](terraform-vs-ansible.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
