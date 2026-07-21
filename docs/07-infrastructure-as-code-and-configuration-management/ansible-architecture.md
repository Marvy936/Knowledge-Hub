# Ansible architecture

Ansible je automation engine určený na configuration management, deployment, provisioning a orchestration. Jeho typický model je **agentless push execution**: automation sa spúšťa z control node a na managed nodes sa pripája cez existujúce transporty, najčastejšie SSH. Agentless však neznamená „bez runtime požiadaviek“ ani „bez dôveryhodnej infraštruktúry“.

Cieľom kapitoly je pochopiť, ktoré komponenty vykonávajú jednotlivé časti práce, kde vznikajú trust boundaries a prečo úspešný Ansible run nie je iba interpretácia YAML súboru.

## 1. Základné komponenty

### Control node

Systém, na ktorom beží:

- `ansible`,
- `ansible-playbook`,
- `ansible-inventory`,
- `ansible-doc`,
- `ansible-galaxy`,
- Python runtime,
- `ansible-core`, collections a plugins,
- inventory a playbook content.

Control node:

1. načíta configuration,
2. zostaví inventory,
3. vyhodnotí playbook a variables,
4. naplánuje tasks pre konkrétne hosts,
5. otvorí connections,
6. vykoná action/module workflow,
7. zhromaždí výsledky a rozhodne o ďalšom postupe.

Control node je privilegovaná automation boundary. Kto ovláda jeho content, credentials alebo plugin search path, môže často ovplyvniť všetky spravované systémy.

### Managed node

Host, zariadenie alebo API target spravovaný Ansible automation. Môže ísť napríklad o:

- Linux alebo Unix host,
- Windows host,
- network device,
- cloud API,
- Kubernetes API,
- storage alebo security appliance.

Nie každý target vykonáva Python module lokálne. Network a cloud collections často komunikujú cez API alebo špecializovaný connection/plugin model.

### Inventory

Inventory popisuje:

- hosts,
- groups a group hierarchy,
- connection metadata,
- host/group variables,
- dynamic discovery zdroje.

Inventory nie je iba zoznam IP adries. Je to topologický a behaviorálny model, podľa ktorého sa rozhoduje, na aké targets a s akými parametrami sa automation aplikuje.

### Playbook

Playbook je YAML dokument obsahujúci jeden alebo viac plays. Play mapuje:

- host pattern,
- variables,
- privilege escalation,
- execution strategy,
- ordered tasks,
- handlers a ďalšie execution controls.

### Module

Module implementuje konkrétnu operáciu, napríklad:

- správu package,
- vytvorenie usera,
- zápis file,
- volanie cloud API,
- správu service,
- načítanie facts.

Module typicky prijme arguments a vráti machine-readable result obsahujúci napríklad `changed`, `failed`, `msg`, `stdout` alebo module-specific fields.

### Plugin

Plugin rozširuje správanie Ansible control plane. Dôležité typy zahŕňajú:

- connection plugins,
- inventory plugins,
- action plugins,
- callback plugins,
- lookup plugins,
- filter a test plugins,
- strategy plugins,
- vars a cache plugins.

Plugin sa vykonáva na control node alebo ovplyvňuje jeho execution path. Neoverená collection preto nie je iba „knižnica YAML“; môže obsahovať executable Python code.

### Collection

Collection je distribuovateľný balík Ansible contentu, ktorý môže obsahovať:

- modules,
- plugins,
- roles,
- playbooks,
- documentation,
- tests.

Content sa identifikuje cez fully qualified collection name, napríklad:

```yaml
ansible.builtin.template:
  src: app.conf.j2
  dest: /etc/example/app.conf
```

FQCN znižuje nejednoznačnosť a explicitne určuje content namespace.

## 2. `ansible-core`, Ansible package a automation platforma

### `ansible-core`

Obsahuje základný execution engine, CLI, Ansible language, built-in plugins a minimálny core content.

### Ansible community package

Distribúcia, ktorá kombinuje `ansible-core` s výberom community collections. Jej version lifecycle nie je totožný s version lifecycle `ansible-core`.

### Automation platforma

Nad core engine môže existovať controller, execution environments, credential management, job templates, RBAC, audit, scheduling a workflow orchestration.

Pri diagnostike vždy rozlišuj:

```text
playbook behavior
vs.
ansible-core behavior
vs.
collection behavior
vs.
platform/controller behavior
```

## 3. Typický execution lifecycle

Zjednodušený playbook run:

```text
CLI alebo controller spustí run
→ načíta ansible.cfg a environment
→ načíta inventory sources a plugins
→ vyrieši host pattern
→ načíta playbook, roles, includes a collections
→ zostaví variable context pre každý host
→ strategy plugin plánuje tasks
→ action plugin pripraví vykonanie
→ connection plugin otvorí transport
→ module alebo API operation sa vykoná
→ result sa vráti control node
→ callback zobrazí alebo uloží výsledok
→ changed tasks môžu notify handlers
→ failure policy rozhodne o pokračovaní
```

Execution nie je jedna globálna sekvencia. Každý host má vlastný task state a pri paralelnom vykonávaní môžu byť rôzne hosts v rôznych časoch na odlišných tasks.

## 4. Action plugin a module execution

Pri bežnom remote module workflow:

1. action plugin beží na control node,
2. pripraví arguments a connection context,
3. Ansible prenesie alebo zostaví module payload,
4. target runtime module vykoná,
5. module vráti štruktúrovaný result,
6. control node spracuje `changed`, `failed`, facts a notifications.

Niektoré actions prebiehajú prevažne alebo úplne lokálne, napríklad:

- `debug`,
- `include_*`,
- niektoré lookup operácie,
- cloud/API modules podľa implementácie,
- `delegate_to: localhost` workflows.

Preto otázka „kde task beží?“ nemá univerzálnu odpoveď. Treba overiť module/action/connection documentation.

## 5. Agentless model a runtime požiadavky

Ansible typicky neinštaluje dlhodobo bežiaceho agenta. Stále však potrebuje:

- sieťový path,
- autentifikáciu,
- podporovaný connection plugin,
- shell alebo API podľa targetu,
- pri mnohých POSIX modules kompatibilný Python runtime,
- privilege escalation podľa operácie,
- dočasný execution priestor a oprávnenia.

Modul `raw` môže vykonať príkaz bez bežného Python module subsystemu a používa sa napríklad pri bootstrap-e Pythonu. Nie je však náhradou za idempotentné modules.

## 6. Connection plugins

Connection plugin určuje transport a remote execution semantics. Príklady:

- SSH,
- local,
- WinRM/PSRP,
- network CLI,
- HTTP API,
- container-oriented connections.

Connection context môže obsahovať:

- remote user,
- port,
- private key alebo iný credential,
- proxy/jump host,
- timeout,
- host-key verification,
- privilege escalation.

### Connection reuse

Persistent connections môžu znížiť latency, ale pridávajú lifecycle, socket a credential considerations. Pri chybe treba rozlíšiť:

```text
DNS/routing
→ transport handshake
→ authentication
→ shell/runtime discovery
→ privilege escalation
→ module execution
```

## 7. Privilege escalation

`become` umožňuje vykonať task pod inou identitou. Najčastejšie používa `sudo`, ale podporovaný mechanizmus závisí od platformy a pluginov.

Bezpečný návrh oddeľuje:

- connection identity,
- become identity,
- credential source,
- tasks, ktoré privilege skutočne potrebujú,
- logging a audit.

Globálne `become: true` pre celý play je jednoduché, ale môže zbytočne rozšíriť blast radius.

## 8. Strategy, forks a execution order

### Strategy

Strategy plugin určuje, ako Ansible posúva hosts cez tasks.

Typický linear model zachováva task barrier medzi hosts v aktuálnom batchi. Iné stratégie môžu umožniť rýchlejším hostom pokračovať bez čakania.

### Forks

`forks` obmedzuje počet paralelných worker procesov na control node. Vyššia hodnota môže zrýchliť run, ale zvyšuje:

- load control node,
- connection burst,
- API rate pressure,
- load managed services,
- počet súbežných failure paths.

### `serial`

Play môže rozdeliť hosty do batches, napríklad pre rolling update:

```yaml
- name: Rolling application update
  hosts: app
  serial: 10%
```

`forks`, strategy a `serial` riešia odlišné vrstvy concurrency.

## 9. Facts a implicitné úvodné tasks

Pri `gather_facts: true` Ansible pred bežnými tasks spustí fact gathering pre hosts v play. To môže ovplyvniť:

- čas runu,
- required Python/packages,
- network traffic,
- variable context,
- prvý failure point.

Ak play facts nepoužíva, môže ich vypnúť. Ak ich používa vo veľkom prostredí, môže zvážiť fact caching s jasnou freshness policy.

## 10. Idempotencia nie je vlastnosť engine-u

Ansible podporuje idempotentný configuration-management štýl, ale každý task nie je automaticky idempotentný.

Idempotencia závisí od:

- module implementácie,
- arguments,
- external API semantics,
- current state detection,
- command side effects,
- ordering a concurrency,
- custom `changed_when`/`failed_when` logiky.

Príklad problematického tasku:

```yaml
- name: Append configuration every run
  ansible.builtin.shell: echo 'feature=true' >> /etc/example.conf
```

Opakovaný run mení systém znova. Preferuj state-aware module alebo template s explicitným desired contentom.

## 11. Check mode a diff mode

### Check mode

Pokus o predikciu zmien bez ich vykonania:

```bash
ansible-playbook site.yml --check
```

Presnosť závisí od podpory modules. Check mode nie je transakčný plan ekvivalentný Terraform saved planu.

### Diff mode

Zobrazuje rozdiel pri podporovaných modules:

```bash
ansible-playbook site.yml --check --diff
```

Diff môže obsahovať citlivé dáta. CI logs a artifacts musia mať primeraný access a retention.

## 12. Configuration precedence

Behavior môže ovplyvniť:

- command-line options,
- environment variables,
- `ansible.cfg`,
- playbook keywords,
- variables,
- direct module arguments.

Configuration precedence a variable precedence nie sú totožné mechanizmy. Pri neočakávanom správaní over effective configuration:

```bash
ansible-config dump --only-changed
```

## 13. Search paths a content resolution

Ansible vyhľadáva:

- collections,
- roles,
- modules/plugins,
- inventory plugins,
- configuration files,
- `group_vars` a `host_vars`,
- templates a included files.

Relatívny path môže byť interpretovaný podľa typu contentu a execution contextu. Explicitné repository layout, FQCN a pinned collections znižujú nejednoznačnosť.

## 14. Security boundaries

### Control node

Chráň:

- source checkout,
- execution environment,
- SSH keys a tokens,
- Vault passwords,
- plugin/collection paths,
- temporary files,
- callback output,
- process environment.

### Collections

Collection je executable dependency. Potrebné sú:

- explicitné sources,
- version pinning,
- controlled upgrades,
- artifact integrity,
- review a testing,
- minimal runtime permissions.

### Inventory a variables

Inventory plugin alebo variable source môže meniť target set a credentials. Zmena host patternu môže mať väčší dopad než zmena samotného tasku.

### Managed nodes

Použi:

- host-key verification,
- least-privilege connection identity,
- scoped `become`,
- bounded batches,
- timeouts,
- audit,
- bezpečné temporary directory permissions.

## 15. Failure model

Ansible rozlišuje napríklad:

- unreachable host,
- failed task,
- changed task,
- skipped task,
- ignored failure,
- rescued failure,
- handler failure.

„Run skončil zeleno“ nemusí znamenať, že všetky hosts dosiahli desired state, ak boli failures ignorované alebo hosts vylúčené patternom.

## 16. Observability

Sleduj:

- target host count,
- unreachable/failed/changed/skipped counts,
- duration podľa tasku a hostu,
- retry a timeout rate,
- handler notifications,
- check-mode drift,
- collection a core versions,
- inventory source freshness,
- credential/connection failures,
- batch rollout progress.

Callback plugins môžu posielať výsledky do logov alebo external systems. Pred uložením vždy vyhodnoť secret exposure.

## 17. Troubleshooting

### Host je `UNREACHABLE`

Over inventory identity, resolved address, DNS, route, port, connection plugin, user, key, host-key policy a proxy settings.

### Module zlyhá na chýbajúcom Python-e

Over interpreter discovery a podporovanú Python version. Pri bootstrap-e použi úzko ohraničený `raw` task, potom prejdite na štandardné modules.

### Task funguje lokálne, ale nie v automation controlleri

Porovnaj:

- `ansible-core` version,
- collections,
- execution environment image,
- `ansible.cfg`,
- environment variables,
- inventory source,
- credential injection,
- network path.

### Zmenil sa nesprávny host

Over host pattern, inventory aliases, `ansible_host`, group membership, limit a dynamic inventory freshness.

### Task je stále `changed`

Over module semantics, rendered content, timestamps, ordering, nondeterministic template values, command/shell behavior a `changed_when`.

### Handler sa nespustil

Over, či notifying task reportoval `changed`, či handler name/listen topic sedí a či failure nezabránil handler phase.

## 18. Anti-patterny

### Jeden privilegovaný control node bez izolácie

Každý playbook a collection dostane implicitne široký trust.

### Mutable `latest` execution environment

Rovnaký commit môže používať iné core alebo collection versions.

### Všetko cez `shell`

Stráca sa state awareness, portability, structured result a často aj check mode.

### Globálne vypnuté host-key checking

Zjednoduší prvé pripojenie, ale oslabí identitu targetu.

### Secrets v inventory alebo logoch

Private Git repository ani masked callback nie sú secret manager.

### Ignorovanie failures bez klasifikácie

Zelený run môže skrývať nedokončenú konfiguráciu.

## 19. Rozhodovací rámec

1. Ktorý control node alebo execution environment bude autoritatívny?
2. Aké targety a connection plugins používame?
3. Kde sú credentials a ako sa rotujú?
4. Ktorý content pochádza z collections a ako je pinned?
5. Ktoré tasks potrebujú privilege escalation?
6. Aký concurrency a batch model je bezpečný?
7. Aké modules podporujú check/diff mode?
8. Ako sa odlíši unreachable, failed a partial success?
9. Aké logs a callbacks sú povolené vzhľadom na secrets?
10. Ako sa reprodukuje rovnaký run v CI a lokálne?

## 20. Kontrolné otázky

1. Aký je rozdiel medzi control node a managed node?
2. Čo vykonáva action plugin a čo module?
3. Prečo agentless neznamená bez runtime požiadaviek?
4. Ako sa odlišujú connection, strategy a callback plugins?
5. Aký je vzťah medzi `forks`, strategy a `serial`?
6. Prečo idempotencia nie je garantovaná engine-om?
7. Čo check mode nedokáže garantovať?
8. Prečo je collection supply-chain dependency?
9. Ako diagnostikovať rozdiel medzi lokálnym a controller runom?
10. Ktoré trust boundaries treba chrániť na control node?

## Glossary impact

Relevantné pojmy: Ansible control node, managed node, agentless automation, `ansible-core`, Ansible collection, module, action plugin, connection plugin, strategy plugin, callback plugin, execution environment, forks, privilege escalation, check mode a diff mode.

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
