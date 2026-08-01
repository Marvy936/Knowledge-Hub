# Ansible troubleshooting

Ansible troubleshooting musí odlíšiť control-node problém, inventory a variable resolution, connection a privilege escalation, module execution, task/handler control flow, per-host partial state a skutočný application outcome. Play recap je agregovaný report. `changed=0 failed=0` nepreukazuje, že bol zasiahnutý správny fleet, že template obsahoval správne values ani že service načítala novú generation.

Dominantný model:

```text
change intent
→ control node a execution environment
→ config, collection a plugin graph
→ inventory sources a resolved host set
→ per-host variable/fact result
→ connection, identity a become
→ task/module execution
→ handler a rolling-batch transition
→ loaded runtime state
→ fleet a business verification
→ rerun a convergence evidence
```

## Zachovanie subjectu

Pred zásahom zaznamenaj:

```text
repository commit/tree
ansible-core a execution-environment image
ansible.cfg source a effective settings
collection/role versions
automation controller job ID
inventory source a cache generation
limit, tags, strategy, forks a serial
resolved hosts a immutable asset IDs
credential/become identity
UTC timeline a per-host results
```

```bash
ansible --version
ansible-config dump --only-changed
ansible-galaxy collection list
ansible-inventory --graph
```

Tieto commands opisujú control plane aktuálneho procesu. `ansible-inventory --graph` bez rovnakého inventory, variables a cache contextu nemusí reprodukovať job z Automation Controllera alebo CI.

## 1. Configuration sa načítala z iného miesta

Ansible hľadá configuration podľa precedence a bezpečnostných pravidiel. Working directory, `ANSIBLE_CONFIG`, home a system config môžu viesť k odlišným settings.

```bash
ansible --version
ansible-config view
ansible-config dump --only-changed
```

`ansible --version` uvádza použitý config file. Pri incidente kontroluj inventory path, collections paths, callbacks, forks, timeout, host-key checking, interpreter discovery a privilege settings. Kopírovanie „správneho ansible.cfg“ do repository nepomôže, ak process používa iný file.

## 2. Inventory má nesprávny host set

Najprv nepúšťaj playbook. Vyrieš inventory:

```bash
ansible-inventory -i inventories/prod --graph
ansible-inventory -i inventories/prod --list > /tmp/inventory.json
ansible -i inventories/prod 'payments:&prod' --list-hosts
```

Competing hypotheses:

```text
zlý inventory source alebo environment
stale dynamic-inventory cache
hostname/alias collision
pattern alebo group intersection chyba
limit z CI jobu
host disabled alebo chýbajúci tag
plugin authentication/API pagination
```

Počet hostov nestačí. Porovnaj immutable asset identity, account/region, IP a intended role. Dynamic inventory môže vrátiť rovnaký počet, ale inú cohortu po replacement-e.

Pred production mutation vytvor expected-vs-resolved manifest a failni pri chýbajúcom alebo extra hoste. `--limit` je filter nad resolved inventory; nie je authorization boundary.

## 3. Variable má neočakávanú hodnotu

Variables pochádzajú z role defaults, inventory/group/host vars, facts, play vars, include vars, role params, block/task vars a extra vars. Vysoká precedence extra vars môže prebiť reviewed environment config.

```bash
ansible-inventory -i inventories/prod --host app-01
ansible -i inventories/prod app-01 -m debug -a 'var=service_port'
```

Debug výpis nesmie odhaliť secrets. Pre citlivé values porovnaj fingerprint, reference alebo metadata. Pri variable incidente zaznamenaj provenance, nie iba final value.

Príklad: `group_vars/all.yml` nastaví `service_port: 8080`, production group 8443, no CI posiela `-e service_port=8080`. Template je syntakticky správny a handler restartuje službu, ale production listener je chybný. Oprava odstráni broad override a pridá assertion:

```yaml
- name: Validate production service port
  ansible.builtin.assert:
    that:
      - service_port == 8443
    fail_msg: "Unexpected production service_port"
```

Assertion je oracle pre konkrétny invariant, nie všeobecný dôkaz správnosti všetkých vars.

## 4. Facts sú stale alebo chýbajú

Fact gathering používa remote execution a môže byť cacheovaný. Template alebo conditional založený na starej OS verzii môže vybrať nesprávny package path.

```bash
ansible -i inventories/prod app-01 -m setup -a 'filter=ansible_distribution*'
ansible -i inventories/prod app-01 -m setup -a 'filter=ansible_default_ipv4'
```

Pri replacement-e hosta sa hostname môže zachovať a fact cache patriť starej machine identity. Cache key a invalidation musia byť viazané na immutable asset alebo generation. `gather_facts: false` je performance voľba iba vtedy, keď playbook facts nepotrebuje alebo ich získava iným explicitným spôsobom.

## 5. Host je `UNREACHABLE`

`UNREACHABLE` znamená, že Ansible nevykonal module contract na hoste. Rozlišuj:

```text
DNS alebo route
SSH/WinRM transport
host key
port/firewall
user/private key/certificate
bastion/ProxyJump
remote shell/interpreter discovery
connection plugin configuration
timeout alebo saturation
```

```bash
ansible -i inventories/prod app-01 -m ping -vvvv
ssh -vvv app-01 true
```

Ansible `ping` nie je ICMP; spustí malý module cez connection plugin a Python/interpreter path. Úspešné `ssh host true` nepreukazuje become ani module transfer/execution.

Pri `--ignore-unreachable` môže play pokračovať a vytvoriť mixed fleet. Recovery preto sleduje failed cohort a re-run subject; zelený recap iba pre reachable hosts nie je complete success.

## 6. `become` alebo permissions zlyhávajú

Connection identity a effective module identity sú odlišné. Kontroluj remote user, become method/user, password/ticket lifecycle, sudoers command restrictions, TTY a environment preservation.

```bash
ansible -i inventories/prod app-01 -m command -a 'id'
ansible -i inventories/prod app-01 -b -m command -a 'id'
```

Prvý command dokazuje connection usera, druhý effective become identity pre daný module execution. Nezobrazuj credential v verbose logu. Ak become funguje pre `id`, stále nemusí povoľovať package manager, service manager alebo write do target pathu.

## 7. Module hlási failure

Čítaj structured result: `msg`, `rc`, `stdout`, `stderr`, `exception`, `invocation` a module-specific fields. Module failure môže pochádzať z input validation, remote commandu, package repository, API, filesystemu alebo parsera.

```bash
ansible-playbook -i inventories/prod site.yml --limit app-01 -vvv
```

`-vvv` môže obsahovať paths, commands a variables; používaj controlled artifact handling. Namiesto okamžitého `ignore_errors: true` klasifikuj error. Ignorovaný critical failure môže umožniť handler alebo ďalšie tasks nad partial state-om.

`failed_when` a `changed_when` menia Ansible verdict. Musia interpretovať native command contract presne:

```yaml
- name: Check configuration
  ansible.builtin.command: /usr/local/bin/payments-api validate-config
  register: validate
  changed_when: false
  failed_when: validate.rc != 0
```

Ak command používa `rc=1` pre „diff exists“ a `rc=2` pre error, generic `rc != 0` je nesprávne. Semantics patria do tasku a testov.

## 8. Template je správny na disku, ale služba používa starý state

`template` result `changed=true` dokazuje zmenu target file-u podľa module comparison. Nezaručuje handler execution, successful reload ani loaded generation.

```yaml
- name: Render payments config
  ansible.builtin.template:
    src: payments.conf.j2
    dest: /etc/payments/payments.conf
    owner: root
    group: payments
    mode: '0640'
    validate: '/usr/local/bin/payments-api validate-config %s'
  notify: Restart payments
```

Troubleshooting chain:

```text
resolved vars
→ rendered temporary file
→ validator result
→ atomic destination replacement
→ handler notification
→ handler execution
→ process restart/reload
→ loaded config generation
→ service/business probe
```

Handler sa typicky spustí na konci play alebo explicitnom `meta: flush_handlers`. Ak neskoršia task zlyhá pred flushom, file môže byť nový a process starý. Pri rolling rollout-e to vytvára rôzne loaded generations.

## 9. Handler nebežal alebo bežal neskoro

Handler sa notify-ne iba pri `changed=true` a rovnaké listen/name notifications sa deduplikujú. Skontroluj task result, handler name/listen, tags a failure path.

```bash
ansible-playbook -i inventories/prod site.yml --list-tasks
ansible-playbook -i inventories/prod site.yml --tags config --check --diff
```

Spustenie iba tagovaných tasks môže vynechať handler alebo preconditions podľa tag inheritance. `--start-at-task` takisto neobnoví implicitný state predchádzajúcich tasks. Tieto možnosti sú diagnostické/recovery nástroje, nie bezpečný substitute za celý play contract.

## 10. Check mode klame alebo modul ho nepodporuje

`--check --diff` je predikcia. Niektoré modules nepoznajú budúci stav bez mutation, iné check mode nepodporujú alebo vracajú partial data. Registered variables z skipped tasks môžu meniť conditionals.

```bash
ansible-playbook -i inventories/prod site.yml --check --diff --limit app-01
```

Check mode nepreukazuje, že package repository, restart, migration alebo external API mutation uspeje. Je výborný na diff a target review, ale production acceptance potrebuje real execution a read-back.

## 11. Rolling play zostal v partial fleet state

Pri `serial`, `max_fail_percentage`, `any_errors_fatal`, rescue/always a load-balancer drain logic závisí outcome od batchu a host failures.

Zachovaj per-host matrix:

```text
host identity
batch
drain result
config artifact/generation
task results
handler/restart
readiness
rejoin
serving status
```

Neopakuj playbook bez zistenia, ktoré hosts boli drained, zmenené, reštartované a znovu zaradené. Idempotentný playbook môže bezpečne pokračovať iba ak observe-nuje real state a partial steps majú stabilné identity.

Recovery často používa limit na failed cohort, ale po ňom musí nasledovať full-fleet verification. Inak zostanú nevidené extra alebo skipped hosts.

## 12. Idempotencia a false `changed=0`

Druhý run s `changed=0` je silný signál iba vtedy, keď modules správne pozorujú target a runtime oracle je nezávislý. Command task s hardcoded `changed_when: false` môže skryť každú mutation.

Overuj tri vrstvy:

```text
Ansible changed signal
remote desired file/package/service state
process-loaded a business state
```

Prvý run môže mať `changed>0`, druhý `changed=0`; zároveň service môže stále používať starú config pre missing reload. Idempotencia nie je iba tichý recap, ale convergence k správnemu effective outcome-u.

## 13. Role alebo collection sa zmenila

`requirements.yml` constraint bez immutable lock/artifact môže pri novom install-e resolve-nuť inú collection. Execution Environment image môže takisto niesť inú `ansible-core`, Python alebo dependencies generation.

```bash
ansible-galaxy collection list
ansible-galaxy collection verify namespace.collection
```

Pri incident reproduction zachovaj execution-environment digest a installed collection inventory. „Rovnaký playbook commit“ nie je úplný subject, ak reusable content alebo module implementation boli mutable.

## 14. Vault decryptuje, ale runtime credential je nesprávny

Successful Vault decryption dokazuje iba prístup k encrypted source. Neoveruje, že credential je active u providera, že správny consumer ho načítal ani že starý credential bol revoked.

Troubleshooting rotation:

```text
Vault file/version a vault ID
→ decryption identity
→ target Secret/file mutation
→ service reload/rollout
→ loaded credential fingerprint
→ provider audit/auth result
→ old credential revocation
```

`no_log: true` obmedzí bežný task output, ale nechráni custom scripts, remote temp files, process arguments alebo external validator. Secrets sa nesmú diagnostikovať ich plaintext výpisom.

## Connected incident: playbook je zelený, polovica fleet beží starú konfiguráciu

Dynamic inventory cache vrátila iba 8 z 10 hosts. V druhom batchi template zmenil file, no ďalšia task zlyhala pred handler flushom. `max_fail_percentage` neprekročil limit a CI interpretovala recap ako success. Dva chýbajúce hosts a tri nereštartované processes ostali na starej generation.

Recovery:

```text
zastaviť ďalší rollout
→ zachovať inventory cache, resolved host manifest a job events
→ porovnať expected asset inventory s resolved hosts
→ na všetkých hosts read-backnúť file checksum a loaded generation
→ identifikovať drained/changed/restarted/serving cohorts
→ opraviť inventory cache a handler/failure semantics
→ dokončiť failed cohort po batchoch
→ full-fleet verification
→ druhý complete run s changed=0
→ business probe a forbidden old-generation check
```

Root cause nie je iba „handler sa nespustil“. Delivery gate akceptoval aggregate recap bez fleet completeness a loaded-state oracle-u.

## Acceptance po recovery

Ansible incident je uzatvorený až keď:

```text
control node/config/execution environment sú identifikované
resolved inventory zodpovedá expected fleetu
variable a fact provenance sú vysvetlené
connection a become identity sú správne
každý host má klasifikovaný task/handler outcome
remote desired state je správny
process načítal expected generation
load balancer/serving cohort je úplný
business request prejde
zakázaná stará generation nie je aktívna
druhý full run konverguje bez nevysvetlených zmien
```

Najlepší Ansible troubleshooting postup preto nezačína `--limit failed-host` ani `--start-at-task`. Začína rekonštrukciou target setu a per-host state machine, aby recovery nevytvorila ďalšiu zmiešanú fleet generation.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Praktický Ansible projekt od inventory po overený rolling configuration rollout](ansible-practical-walkthrough.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Terraform vs. Ansible →](terraform-vs-ansible.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
