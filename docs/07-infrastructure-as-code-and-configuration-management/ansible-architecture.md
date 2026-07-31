# Ansible architecture

Ansible je automation engine, ktorý skladá versionovaný content, inventory, variables, credentials, connection plugins a execution strategy do série per-host alebo API operations. Typický model je agentless push z control node-u, ale „agentless“ neznamená bez runtime, identity alebo supply-chain dependencies. Každý run používa konkrétny `ansible-core`, Python environment, collections, plugins, inventory snapshot a credential context. Rovnaký playbook preto môže vykonať inú zmenu, ak sa zmení execution environment alebo resolved host context.

Kapitola otvára incident `IAC-PAY-78`. Atlas Payments má nasadiť novú konfiguráciu na dvanásť produkčných application hosts v troch availability zones. Dynamic inventory cache však vráti iba desať hosts, jeden host dostane z group precedence nesprávny port a na ďalšom hoste template zmení file, no validation failure zabráni handleru reštartovať službu. Controller job môže skončiť relatívne „zeleno“, hoci fleet je coverage, configuration aj runtime zmiešaný.

## 1. Dominantný run-subject-to-host-outcome lifecycle

```text
immutable playbook/role/collection content
+ pinned execution environment
+ inventory sources a cache generation
+ variables, facts a credentials
→ resolved target inventory
→ per-host execution context
→ strategy, serial a task scheduling
→ connection, authentication a become
→ action/plugin/module alebo API operation
→ structured per-host result
→ handler a failure transition
→ effective-state a service verification
→ fleet coverage, second run a recovery closure
```

Ansible run nie je jedna globálna transakcia. Každý host má vlastný task state a môže skončiť ako:

```text
ok
changed
failed
unreachable
skipped
rescued
ignored
not targeted at all
```

Posledná kategória je kritická: host vynechaný inventory resolverom sa neobjaví ako `unreachable`, pretože Ansible sa ho nikdy nepokúsil spravovať.

## 2. Exact Ansible run subject

```yaml
ansibleRunSubject:
  repository: atlas/configuration
  sourceRevision: 42ad9c1
  playbook: playbooks/payments.yml
  ansibleCoreVersion: 2.x-pinned
  executionEnvironmentDigest: sha256:71ca...
  collectionsManifestDigest: sha256:009a...
  ansibleConfigDigest: sha256:8d10...
  inventory:
    sources:
      - inventories/prod/static.yml
      - inventories/prod/cloud.aws_ec2.yml
    cacheGeneratedAt: 2026-07-31T08:00:00Z
    pattern: payments_app:&production
    limit: none
  expectedHosts:
    count: 12
    manifestDigest: sha256:f39c...
  credentials:
    connectionIdentity: payments-config-prod
    becomeRole: payments-service-admin
  execution:
    strategy: linear
    forks: 8
    serial: 4
  runId: gitlab-98122
```

Rovnaký `payments.yml` nie je rovnaký run, ak sa zmení collection, inventory cache, variable source, execution image alebo credential injection.

## 3. Control node ako privilegovaná boundary

Control node alebo automation controller:

```text
načíta ansible.cfg a runtime
→ resolve-ne inventory, variables a content paths
→ vyhodnotí host pattern a limit
→ vytvorí per-host task contexts
→ otvorí connections alebo vykoná local/API action
→ zhromaždí results, notifications a callback evidence
```

Control node má často prístup k SSH keys, Vault password source-u, cloud credentials, inventory API a množstvu produkčných hosts. Kompromitovaný execution image, collection plugin alebo checkout preto môže zasiahnuť celý target scope.

Controls:

- immutable execution environment digest;
- pinned collections;
- read-only source checkout;
- short-lived credentials;
- restricted network egress;
- oddelené untrusted validation a production execution pools;
- audit callback a log redaction.

## 4. Managed node a API target

Target nemusí byť Linux host. Môže to byť Windows, network device, Kubernetes API, cloud API alebo appliance. Execution location závisí od module/action/connection designu.

Bežný remote flow:

```text
action plugin na controlleri
→ connection plugin
→ temporary module payload alebo remote command
→ managed-node execution
→ JSON-like result
```

API/local flow:

```text
action alebo module na controlleri
→ cloud/API credential chain controllera
→ remote service API
→ result viazaný na inventory host alebo localhost
```

`delegate_to: localhost` mení execution a credential boundary. Production host pattern nepreukazuje production cloud account pre delegated task.

## 5. Content graph: playbook, play, task, module, plugin

- **Playbook** je ordered collection plays.
- **Play** viaže host pattern na tasks, variables, privilege, strategy a failure policy.
- **Task** volá module/action alebo riadi flow.
- **Module** implementuje observation a mutation unit.
- **Action plugin** môže vykonať časť logiky na controlleri.
- **Connection plugin** určuje transport.
- **Inventory plugin** vytvára host graph.
- **Callback plugin** spracúva výsledky.
- **Collection** distribuuje modules, plugins, roles a ďalší content.

Používaj FQCN:

```yaml
- name: Render payments configuration
  ansible.builtin.template:
    src: payments.conf.j2
    dest: /etc/payments/payments.conf
    owner: root
    group: payments
    mode: '0640'
```

FQCN znižuje namespace ambiguity. Nepreukazuje pinned collection bytes ani správny execution environment.

## 6. Execution environment ako reproducibility subject

Reprodukovateľný run pinne:

```text
ansible-core
Python a system libraries
collections a dependencies
SSH/WinRM/cloud tooling
CA certificates
inventory/callback plugins
helper binaries
```

Praktický read-back:

```bash
ansible --version
ansible-galaxy collection list
ansible-config dump --only-changed
python --version
```

Výstupy preukazujú observed runtime a config v aktuálnom controller process-e. Nepreukazujú image provenance, že collection directory nebola modifikovaná ani že remote hosts používajú očakávaný interpreter.

Container image sa používa digestom, nie tagom `latest`:

```text
registry.example/automation/ansible@sha256:71ca...
```

## 7. Inventory resolution pred execution

Play:

```yaml
- name: Roll out payments configuration
  hosts: payments_app:&production
  serial: 4
  gather_facts: true
```

Pred taskom Ansible:

```text
načíta inventory sources
→ merge-ne hosts, groups a variables
→ vyhodnotí pattern a --limit
→ flatten-ne variables per host
→ vytvorí target list
```

Official inventory model umožňuje viac sources a ich load order môže meniť variable výsledok. Target inventory je preto artifact, nie implicitný detail. citeturn329472search1turn329472search3

Praktický read-back:

```bash
ansible-inventory -i inventories/prod --graph
ansible-inventory -i inventories/prod --list > resolved-inventory.json
ansible-playbook playbooks/payments.yml --list-hosts
```

`--list-hosts` preukazuje host pattern resolution pre tento command context. Nepreukazuje connectivity ani host identity po DNS/SSH handshake.

## 8. Variable context per host

Effective host variables môžu pochádzať z inventory, `group_vars`, `host_vars`, play/role vars, facts, registered values a extra vars. Ansible načíta dostupné definitions a použije precedence rules; odporúčaný design však nevyužíva precedence ako neprehľadný programming model, ale definuje každý významný variable v jednej autoritatívnej vrstve. citeturn329472search2turn329472search6

Read-back:

```bash
ansible-inventory -i inventories/prod --host app-01
```

Výstup preukazuje inventory-resolved vars pre hosta. Nezahŕňa automaticky všetky play/task/extra vars a môže obsahovať sensitive hodnoty, preto potrebuje redaction a controlled access.

## 9. Connection a effective mutation identity

```text
inventory_hostname a ansible_host
→ DNS/route
→ transport handshake
→ host identity verification
→ connection authentication
→ remote interpreter/runtime
→ become
→ effective mutation
```

Connection identity a `become` identity sú odlišné:

```yaml
- name: Install configuration
  hosts: payments_app
  remote_user: automation
  become: true
  become_user: root
```

Globálne `become: true` rozširuje privilege na všetky tasks. Preferuj úzky task/block scope, keď iba časť operácií potrebuje root.

Host-key checking je target identity control. Jeho vypnutie môže umožniť mutation nesprávneho hosta aj s platným credentialom.

## 10. Strategy, forks a serial

- **strategy** určuje, ako hosts postupujú tasks;
- **forks** obmedzuje controller concurrency;
- **serial** určuje rollout batch;
- **throttle** môže obmedziť konkrétnu task concurrency.

```yaml
- name: Rolling configuration rollout
  hosts: payments_app:&production
  serial: 4
  max_fail_percentage: 0

  tasks:
    - name: Configure host
      ansible.builtin.include_role:
        name: atlas.payments.runtime
```

`serial: 4` preukazuje intended batch size, nie health gate medzi batches. Playbook musí explicitne overiť readiness a zastaviť ďalší batch pri failure.

## 11. Structured result a truthfulness

Module result môže obsahovať:

```yaml
changed: true
failed: false
msg: configuration updated
```

`changed` je tvrdenie module/task logic o mutation, nie nezávislá remote proof. Custom `changed_when` môže byť nesprávny a shell command môže meniť systém bez truthful resultu.

Register:

```yaml
- name: Read service state
  ansible.builtin.command: systemctl is-active payments
  register: service_state
  changed_when: false
  failed_when: service_state.rc != 0
```

Output preukazuje command result v danom remote execution context-e. Nepreukazuje business capability ani že load balancer posiela traffic na host.

## 12. Handlers ako delayed state transition

```yaml
- name: Render configuration
  ansible.builtin.template:
    src: payments.conf.j2
    dest: /etc/payments/payments.conf
    mode: '0640'
  notify: Restart payments

handlers:
  - name: Restart payments
    ansible.builtin.service:
      name: payments
      state: restarted
```

Notification vznikne iba pri `changed`. Handler sa vykoná podľa play/handler semantics. Ak host zlyhá pred handler phase, file môže byť nový, process starý.

Dôveryhodný flow overuje:

```text
file content/version
→ handler execution
→ process PID/start time
→ local health
→ load-balancer/backend health
→ payment journey
```

## 13. Failure a coverage model

```text
UNREACHABLE
TASK_FAILED
SKIPPED
IGNORED
RESCUED
HANDLER_FAILED
OMITTED_FROM_INVENTORY
PARTIAL_BATCH
RUNTIME_VERIFY_FAILED
```

Global process exit code nestačí. Run verdict potrebuje:

```text
expected hosts
vs resolved hosts
vs attempted hosts
vs converged hosts
vs runtime-healthy hosts
```

## 14. Check mode a diff mode

```bash
ansible-playbook playbooks/payments.yml \
  -i inventories/prod \
  --check \
  --diff
```

Check mode simuluje changes iba pri modules, ktoré ho podporujú. Tasks závislé od registered resultu predchádzajúcej mutation môžu mať neúplný flow. Diff môže obsahovať sensitive file content. Oficiálna dokumentácia výslovne opisuje check mode ako simuláciu a module-dependent capability. citeturn329472search0

Preto verdict je:

```text
CHECK_PREDICTION_VALID_FOR_SUPPORTED_TASKS
```

nie „production-safe plan“.

## 15. Worked incident: inventory vynechal dva hosts

Dynamic inventory cache bola vytvorená pred autoscaling replacementom. Dva nové hosts neboli v cache a dva staré už neexistovali. Pattern resolve-nul desať hosts namiesto očakávaných dvanástich.

```text
omission pred execution
→ chýbajúce hosts nemajú task result
→ desať targetovaných hosts prejde
→ recap vyzerá green
→ fleet ostáva mixed
```

Controls:

```bash
ansible-playbook playbooks/payments.yml \
  -i inventories/prod \
  --list-hosts > target-hosts.txt

test "$(grep -c '^    ' target-hosts.txt)" -eq 12
```

Počet je sanity check. Silnejší manifest porovná expected instance IDs/hostnames a inventory cache age.

## 16. Worked incident: mutable execution environment

Developer používal collection 2.4; controller tag `latest` už obsahoval 3.0 s odlišným restart defaultom.

```text
rovnaký YAML
+ iný collection/runtime graph
→ iný module behavior
→ hard restart celej batch
```

Recovery pinne image digest, obnoví known-good collection release, overí affected hosts a pridá execution-environment manifest do approval subjectu.

## 17. Worked incident: delegated API task v nesprávnom účte

```yaml
- name: Register batch in load balancer
  vendor.cloud.target:
    instance_ids: "{{ ansible_play_batch }}"
  delegate_to: localhost
```

Task používa controller cloud credentials. Controller mal staging default account.

```text
production inventory hosts
≠ production API identity
```

API task musí pred mutation read-backnúť account/region a používať environment-scoped workload identity.

## 18. Competing hypotheses pri mixed fleet

Symptom: controller job success, ale dva hosts používajú starú konfiguráciu.

```text
H1: hosts chýbali v resolved inventory
H2: pattern/limit ich vylúčil
H3: connection failed a failure bol ignored
H4: variable precedence vyrenderovala starý content
H5: template changed, handler neprebehol
H6: service reštartoval, ale load balancer stále routuje starý backend
H7: post-run verifier číta stale cache
```

Dôkazy:

- expected/resolved/recap manifests testujú H1–H3;
- per-host vars a rendered checksum H4;
- notifications/handler results/process start time H5;
- LB target health/version endpoint H6;
- direct host query a cache timestamps H7.

## 19. Evidence-preserving containment a recovery

Atlas:

1. zastaví ďalší batch;
2. zachová inventory JSON, run events, per-host results a rendered checksums;
3. identifikuje omitted, failed a mixed-state hosts;
4. odoberie unhealthy hosts z trafficu;
5. opraví inventory cache a variable contract;
6. vykoná targeted recovery s explicitným `--limit` nad reviewed host manifestom;
7. overí process, endpoint a business journey;
8. spustí full-fleet second converge run;
9. potvrdí `changed=0` pre managed config tasks a complete host coverage.

## 20. Acceptance a forbidden paths

Architecture blok je prijatý, keď:

```text
execution environment a collections sú pinned
+ expected a resolved host manifests sú rovnaké
+ per-host effective identity/variables sú auditovateľné
+ API delegated tasks read-backnú target account
+ serial batch má health gate
+ handler completion je overený
+ omitted host nie je success
+ check-mode unsupported task je incomplete evidence
+ full-fleet second run converguje
+ runtime payment journey prejde
```

Forbidden tests:

- undersized inventory;
- staging controller credential pri production play;
- mutable execution tag;
- unsupported check-mode task interpretovaný ako pass;
- handler skipped po config mutation.

## 21. Kontrolné otázky

1. Prečo agentless neznamená bez runtime a identity dependencies?
2. Čo musí obsahovať Ansible run subject?
3. Aký rozdiel je medzi control-node, managed-node a API execution?
4. Čo FQCN preukazuje a čo nepreukazuje?
5. Prečo resolved inventory patrí do evidence?
6. Ako sa connection identity líši od become identity?
7. Aký rozdiel je medzi forks, serial a strategy?
8. Prečo `changed` nie je nezávislý remote proof?
9. Ako môže host chýbať bez `unreachable` resultu?
10. Aké limity má check mode?
11. Ako sa odlíši handler failure od inventory omission?
12. Prečo acceptance potrebuje full-fleet second converge run?

## Glossary impact

Relevantné pojmy: Ansible control node, managed node, execution environment, collection, action plugin, connection plugin, inventory plugin, callback plugin, run subject, target manifest, strategy, forks, serial, become, handler, unreachable, omitted host, check mode, diff mode a per-host convergence.

## Primárne zdroje

- [Introduction to Ansible](https://docs.ansible.com/projects/ansible/latest/getting_started/introduction.html)
- [Ansible architecture](https://docs.ansible.com/projects/ansible/latest/dev_guide/overview_architecture.html)
- [Working with playbooks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks.html)
- [Introduction to modules](https://docs.ansible.com/projects/ansible/latest/module_plugin_guide/modules_intro.html)
- [Check mode and diff mode](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
[← Predchádzajúca: Terraform testing a policy](terraform-testing-and-policy.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Inventory →](inventory.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
