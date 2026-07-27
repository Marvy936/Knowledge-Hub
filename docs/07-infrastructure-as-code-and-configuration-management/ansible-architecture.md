# Ansible architecture

Ansible je automation engine, ktorý typicky vykonáva agentless push automation z control node-u na množinu managed nodes alebo API targetov. „Agentless“ však neznamená bez runtime, identity, transportu ani supply-chain dependencies. Každý run vzniká z konkrétneho execution environmentu, inventory snapshotu, variable contextu, credentials a content graphu; následne sa rozvetví na samostatné host execution paths.

Táto kapitola používa jeden priebežný scenár. Atlas Payments nasadzuje novú konfiguráciu služby na 12 produkčných application hosts v troch availability zones. Playbook má postupovať po štyroch hostoch, vyrenderovať config, reštartovať službu cez handler a po každom batchi overiť health endpoint. Cieľom nie je iba „playbook skončil zeleno“, ale dokázať, ktoré hosty, pod akými identitami a s akou verziou contentu dosiahli požadovaný runtime stav.

## 1. Dominantný model: run-subject-to-host-outcome lifecycle

```text
immutable automation content a execution environment
+ inventory/variable/credential subject
→ resolved target inventory
→ per-host execution context
→ strategy, batch a task scheduling
→ connection/authentication/become
→ action/plugin/module alebo API operation
→ structured result a handler transition
→ host-level failure/continuation decision
→ effective-state verification
→ run coverage, audit a recovery closure
```

Ansible run nie je jedna globálna transakcia. Každý host má vlastný task state a môže skončiť ako changed, failed, unreachable, skipped, rescued alebo nedosiahnutý. Dôveryhodný verdict preto potrebuje host inventory a coverage, nie iba process exit code.

## 2. Atlas Ansible run subject

Pred vykonaním musí pipeline vedieť spätne zrekonštruovať:

```text
source revision a playbook path
ansible-core version
execution environment image digest
collections a versions/checksums
ansible.cfg a relevant environment
inventory sources, plugin versions a cache timestamp
resolved host pattern a limit
variable/secret source identities
controller job/run ID
connection credential a become role
strategy, forks, serial a failure policy
```

Toto je **Ansible run subject**. Rovnaký `site.yml` môže vykonať odlišnú zmenu, ak sa zmení collection, inventory, configuration precedence, execution environment alebo credential injection.

## 3. Komponenty ako execution boundaries

### Control node

Control node alebo automation controller:

1. načíta configuration a execution environment;
2. načíta inventory sources a plugins;
3. rozlíši playbook, roles, includes a collections;
4. vytvorí variable context pre každý host;
5. naplánuje tasks podľa strategy a batch pravidiel;
6. otvorí connections alebo vykoná local/API actions;
7. zhromaždí results, notifications a callback evidence.

Je to privilegovaná automation boundary. Ovládnutie source checkout-u, plugin pathu, execution image alebo credentials môže ovplyvniť všetky targety.

### Managed node alebo API target

Target môže byť Linux host, Windows host, network device, cloud API, Kubernetes API alebo appliance. Nie každý module payload beží ako Python na remote hoste. Niektoré collections vykonávajú API calls z control node-u alebo používajú špecializovaný connection plugin.

### Inventory

Inventory určuje host identity, groups, connection metadata a variables. Je to target-selection a blast-radius contract, nie iba address book.

### Playbook, play a task

Playbook obsahuje plays. Play spája host pattern s ordered task flow, variables, privilege, strategy a failure policy. Task volá module/action alebo riadi execution (`include`, `block`, `rescue`, `meta`, handler notification).

### Module a action plugin

Module implementuje state observation a mutation. Action plugin beží na control node-e a môže pripraviť arguments, transfer alebo časť logiky. Pri bežnom remote flow:

```text
action plugin na controlleri
→ connection context
→ module payload/command/API request
→ remote alebo API execution
→ structured result
→ changed/failed/facts/notifications
```

### Plugin a collection

Connection, inventory, action, callback, lookup, filter, vars, cache a strategy plugins menia execution path. Collection môže obsahovať executable Python code, roles aj modules. Je preto supply-chain dependency, nie iba balík YAML.

Používaj fully qualified collection names:

```yaml
- name: Render payments configuration
  ansible.builtin.template:
    src: payments.conf.j2
    dest: /etc/payments/payments.conf
```

FQCN určuje namespace, ale stále potrebuje pinned collection release a execution environment.

## 4. Execution environment a content resolution

Reprodukovateľný run potrebuje pinované:

- `ansible-core`;
- Python/runtime dependencies;
- collections;
- system packages a SSH tooling;
- callback a inventory plugins;
- CA certificates a helper binaries.

Mutable image tag `latest` môže spôsobiť, že lokálny a controller run použijú odlišný module behavior.

Content resolution zahŕňa:

```text
ansible.cfg a environment
→ collection/role/plugin search paths
→ playbook relative paths
→ group_vars/host_vars discovery
→ templates/includes/files
```

Relatívny path a short module name môžu smerovať na iný content podľa execution contextu. Repository layout, FQCN a immutable execution environment znižujú nejednoznačnosť.

## 5. Inventory resolution pred taskom

Atlas play používa:

```yaml
- name: Roll out payments configuration
  hosts: payments_app:&production
  serial: 4
```

Pred prvým taskom musí Ansible:

```text
načítať inventory sources
→ zlúčiť host a group identity
→ vyhodnotiť pattern a limit
→ vyriešiť variables a connection data per host
→ vytvoriť target inventory
```

Ak dynamic inventory vynechá dva hosts, playbook môže byť úplne zelený pre zvyšných desať. Architektúra preto potrebuje expected target count alebo explicitný target manifest.

## 6. Variables a effective host context

Každý host dostane effective context z viacerých vrstiev:

- inventory host/group vars;
- vars plugins;
- facts;
- play a task vars;
- role defaults/vars;
- registered values;
- extra vars;
- secret injection.

Configuration precedence a variable precedence nie sú totožné. Pri diagnostike controller behavioru používaj napríklad:

```bash
ansible-config dump --only-changed
ansible-inventory -i inventories/prod --host app-01
```

Dôveryhodná evidence nemusí zverejňovať secret values, ale má zaznamenať source identity a scope významných variables.

## 7. Connection, authentication a runtime discovery

Pre host execution treba odlíšiť observation points:

```text
resolved host identity/address
→ DNS a route
→ transport handshake
→ host identity verification
→ authentication
→ shell/runtime/interpreter discovery
→ temporary module path
→ privilege escalation
→ module operation
```

Connection plugin môže používať SSH, local, WinRM/PSRP, network CLI, HTTP API alebo container transport.

Agentless model stále potrebuje:

- dostupný network path;
- credential;
- podporovaný connection plugin;
- remote shell alebo API;
- kompatibilný Python pri mnohých POSIX modules;
- temporary filesystem permissions;
- scoped privilege escalation.

`raw` môže bootstrapovať Python, ale nemá nahradiť state-aware modules.

## 8. Connection identity a `become`

Oddeľ:

```text
connection identity
→ transport authentication
→ become mechanism
→ effective mutation identity
```

Globálne `become: true` rozširuje privilege na všetky tasks vrátane tých, ktoré ho nepotrebujú. Preferuj úzky scope a audit sudo/become transitions.

Host-key checking je target identity control. Jeho globálne vypnutie môže spôsobiť, že platný key autentifikuje spojenie k nesprávnemu hostu alebo intermediary.

## 9. Strategy, forks a `serial`

Tieto controls riešia odlišné vrstvy:

- **strategy** — ako hosts postupujú cez tasks;
- **forks** — koľko workerov môže control node spracovať paralelne;
- **serial** — koľko hosts patrí do rollout batchu.

Atlas používa `serial: 4`. Linear strategy znamená, že hosts aktuálneho batchu typicky dokončia task barrier pred prechodom na ďalší task. Free-like strategy môže umožniť rýchlejším hosts pokračovať skôr.

Vyššie `forks` môže zvýšiť:

- connection burst;
- API throttling;
- load na shared service;
- počet súbežných failure paths;
- tlak na control node CPU/memory.

Concurrency nastavenie nie je náhrada za správne dependency, batch safety a runtime verification.

## 10. Task result, handler a host state

Module vracia štruktúrovaný result, napríklad:

```text
changed
failed
skipped
msg
stdout/stderr
facts alebo module-specific fields
```

Task, ktorý reportuje `changed`, môže notify handler. Handler sa typicky vykoná v handler phase podľa play semantics. Ak host zlyhá skôr alebo notification nevznikne, config file môže byť zmenený bez reštartu služby.

Atlas flow:

```yaml
- name: Render config
  ansible.builtin.template:
    src: payments.conf.j2
    dest: /etc/payments/payments.conf
  notify: Restart payments

handlers:
  - name: Restart payments
    ansible.builtin.service:
      name: payments
      state: restarted
```

Dôveryhodný outcome musí overiť aj runtime service state, nie iba `template: changed`.

## 11. Failure model a partial success

Rozlišuj:

- **unreachable** — connection path nevznikol;
- **failed** — task/module operation zlyhala;
- **skipped** — task sa pre host neaplikoval;
- **ignored** — failure bola vedome potlačená;
- **rescued** — block failure prešla recovery branchom;
- **handler failure** — mutation prebehla, convergence action zlyhala;
- **omitted target** — host nebol vo resolved target inventory.

Posledný stav sa nemusí objaviť ako failure. Ak inventory vynechá host, Ansible ho nevie označiť `unreachable`.

Run verdict preto potrebuje:

```text
expected target inventory
vs. resolved target inventory
vs. attempted hosts
vs. successful effective-state verification
```

## 12. Worked failure: zelený run vynechal dva hosts

Dynamic inventory API vráti desať z dvanástich produkčných hosts pre stale cache/filter issue. Všetky targetované hosts prejdú a controller označí job ako success.

Mechanizmus:

```text
inventory omission nastane pred play execution
→ chýbajúce hosts nemajú task state
→ recap obsahuje iba desať hosts
→ bez expected inventory gate-u je partial coverage interpretovaná ako success
```

Skoršie controls:

- expected production host count alebo immutable deployment manifest;
- forbidden empty/undersized target set;
- inventory cache age evidence;
- target summary pred approval;
- post-run fleet-level version inventory.

## 13. Worked failure: mutable execution environment

Developer lokálne používa collection `vendor.service` 2.4. Controller image `latest` už obsahuje 3.0, ktorá zmenila default restart behavior. Lokálny check mode ukáže bezpečný update, controller vykoná hard restart všetkých hosts.

```text
rovnaký playbook source
+ rozdielny core/collection runtime
→ rozdielna module schema/default/implementation
→ rozdielny remote outcome
```

Fix nie je pinovať iba YAML repository. Pinuj execution image digest a collection lock/requirements, uchovaj ich v run subjecte a testuj upgrade samostatne.

## 14. Worked failure: local delegation zasiahla nesprávny účet

Task používa:

```yaml
- name: Update load balancer registration
  vendor.cloud.target:
    instance_ids: "{{ batch_ids }}"
  delegate_to: localhost
```

Module sa vykoná na control node-e a použije controller cloud credential chain, nie SSH identity managed hostu. Controller mal default credential pre staging účet.

Dôsledok:

```text
host batch je production
→ delegated action je local
→ effective provider identity je staging
→ playbook host context neznamená remote API target identity
```

Pre API/local tasks zaznamenávaj provider account/region identity a používaj environment-scoped credential injection.

## 15. Idempotencia a state awareness

Ansible engine negarantuje idempotenciu každého tasku. Závisí od module behavioru, arguments, current-state observation, external API a custom conditions.

Neidempotentný príklad:

```yaml
- name: Append configuration every run
  ansible.builtin.shell: echo 'feature=true' >> /etc/payments/app.conf
```

State-aware model:

```yaml
- name: Render complete desired configuration
  ansible.builtin.template:
    src: app.conf.j2
    dest: /etc/payments/app.conf
    mode: '0640'
```

Aj template môže byť stále `changed`, ak obsahuje timestamp alebo nondeterministic ordering. Second-run convergence je dôležitý test.

## 16. Check mode a diff mode

```bash
ansible-playbook site.yml --check --diff
```

Check mode je module-dependent predikcia, nie Terraform saved plan. Niektoré modules:

- ho nepodporujú;
- vrátia neúplný result;
- potrebujú current remote state;
- nevedia predikovať external side effects;
- môžu pri lookup/action fáze stále vykonať local reads alebo calls.

Diff môže obsahovať secrets alebo celé konfigurácie. Potrebuje redaction, restricted logs a retention.

Check mode evidence musí byť označená ako prediction, nie potvrdený runtime outcome.

## 17. Worked failure: config zmenený, handler neprebehol

Na hoste `app-07` template task reportuje `changed`. Nasledujúci validation task zlyhá a host je vyradený pred handler phase. Ostatné hosts službu reštartujú.

Výsledok:

```text
app-07 má nový file content
+ starý process state
→ fleet je konfiguračne a runtime zmiešaný
```

Recovery musí určiť, či starý process bezpečne beží s novým file-om, následne vykonať handler/revert a overiť health. Run nemá byť zhrnutý iba globálnym počtom failed tasks.

## 18. Causal troubleshooting walkthrough: run green, fleet používa dve verzie configu

Po rolloute telemetry ukazuje, že desať hosts používa config `v43`, dva stále `v42`. Controller job je zelený.

### 1. Zafixuj run subject

Zaznamenaj source revision, execution image digest, core/collections, inventory sources/cache age, pattern/limit, variables, strategy/serial, credential identity a run ID.

### 2. Súťažiace hypotézy

1. Dva hosts neboli v resolved inventory.
2. Hosty boli `skipped` pre condition/group var.
3. Failures boli ignored alebo rescued bez convergence.
4. Template reportoval no-change pre stale rendered input.
5. Handler nebol notified alebo sa nevykonal.
6. Hosts boli unreachable a failure policy ich neblokovala.
7. Free/parallel strategy umožnila neskorší batch pred úplným verification.
8. Runtime verifier číta stale cache alebo nesprávny fleet identity source.

### 3. Diskriminačné observation points

- expected vs. `--list-hosts` target inventory;
- inventory plugin/cache timestamp;
- per-host recap a event stream;
- resolved variables pre affected hosts;
- template checksum pred/po;
- handler notification a execution events;
- connection/unreachable history;
- service process start time a loaded config version;
- batch/strategy timeline.

### 4. Containment

Pozastav ďalšie batches alebo následné deploymenty. Vyraď neoverené hosts z trafficu, ak mixed configuration nie je bezpečná.

### 5. Recovery

- omitted target → oprav inventory a spusti explicitne scoped recovery run;
- skipped condition → oprav variable/condition contract;
- ignored/rescued failure → zmeň verdict a recovery semantics;
- handler gap → vykonaj bounded restart alebo revert;
- stale render input → oprav source/fact/cache freshness;
- unreachable → obnov connection path a zopakuj host-level operation.

### 6. Over pôvodný outcome

Potvrď všetkých 12 stable host identities, config checksum `v43`, service health a traffic inclusion. Potom vykonaj second run, ktorý má byť no-change okrem vedomých health checks.

### 7. Posuň control skôr

Pridaj expected host inventory, per-host version oracle, handler regression test a batch gate, ktorý nepokračuje bez complete verification.

## 19. Security boundaries

### Control node/execution environment

Chráň source checkout, plugin paths, temporary files, callback output, process environment, SSH sockets, cloud tokens a Vault credentials.

### Collections a plugins

Používaj approved sources, version pinning, artifact integrity, controlled upgrades a minimálne runtime permissions.

### Inventory a variables

Zmena target group alebo `ansible_connection` môže mať väčší blast radius než zmena tasku. Inventory a variable source sú code/trust boundaries.

### Managed nodes

Použi host identity verification, least-privilege connection identity, scoped `become`, bounded batches, timeouts a audit.

## 20. Run evidence a observability

Uchovaj bez secret leakage:

```text
run subject
→ resolved target inventory a count
→ per-host effective context identity
→ task/handler event stream
→ unreachable/failed/skipped/changed/rescued verdicts
→ batch progression
→ runtime verification inventory
→ recovery/cleanup actions
```

Sleduj:

- expected vs. targeted vs. verified host count;
- unreachable a omitted targets;
- task/host duration;
- handler failures;
- repeated changed tasks;
- inventory freshness;
- core/collection drift;
- controller/local reproducibility;
- batch abort a recovery rate;
- secret-redaction failures.

## 21. Referenčné pravidlá

- Ansible run je subject z contentu, runtime, inventory, variables a credentials.
- Agentless neznamená bez target runtime a transport assumptions.
- Host pattern sa vyhodnocuje pred task execution; omitted host nie je unreachable host.
- Action/plugin môže bežať lokálne, aj keď play cieli remote hosts.
- `forks`, strategy a `serial` riadia odlišné concurrency vrstvy.
- `changed` nie je runtime verification.
- Handler transition je súčasť desired-state convergence.
- Check mode je predikcia s module-specific fidelity.
- Globálny process success nenahrádza per-host coverage a outcome.
- Druhý no-change run je dôležitý dôkaz idempotencie.

## 22. Kontrolné otázky

1. Čo tvorí Ansible run subject?
2. Ktoré kroky prebiehajú na control node-e a ktoré na managed node-e?
3. Prečo inventory omission nevytvorí `unreachable` failure?
4. Ako sa líšia connection a become identity?
5. Kedy môže task cieliaci production hosts volať staging API?
6. Aký je rozdiel medzi strategy, forks a `serial`?
7. Prečo `template: changed` nepotvrdzuje nový runtime stav?
8. Čo check mode dokáže a čo nedokáže?
9. Ako mutable execution environment mení behavior rovnakého playbooku?
10. Aké evidence dokazujú complete fleet convergence?

## Glossary impact

Relevantné pojmy: Ansible run subject, control node, managed node, execution environment, agentless push execution, action plugin, module execution, connection identity, become identity, strategy, forks, serial batch, host execution state, omitted target, handler transition, check-mode prediction, fleet convergence a run coverage.

## Oficiálna dokumentácia

- [Ansible concepts](https://docs.ansible.com/projects/ansible/latest/getting_started/basic_concepts.html)
- [Ansible architecture](https://docs.ansible.com/projects/ansible-core/devel/dev_guide/overview_architecture.html)
- [Controlling playbook execution](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_strategies.html)
- [Connection methods and details](https://docs.ansible.com/projects/ansible/latest/inventory_guide/connection_details.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Terraform testing a policy](terraform-testing-and-policy.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Inventory →](inventory.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
