# Inventory

Ansible inventory určuje, **ktoré targety existujú pre automation**, ako sú zoskupené a aké connection alebo behavior metadata sa na ne viažu. Inventory nie je iba statický zoznam hostname. Je to runtime model, ktorý môže vzniknúť zlúčením viacerých files, directories, plugins a external systems.

Nesprávny inventory môže spôsobiť, že správny playbook vykoná zmenu na nesprávnych hosts. Preto je inventory samostatná trust a blast-radius boundary.

## 1. Inventory source

Inventory source je vstup, ktorý Ansible dokáže parsovať cez inventory plugin. Môže ním byť:

- INI file,
- YAML file,
- directory obsahujúci viac sources,
- plugin configuration file,
- legacy dynamic inventory script,
- external system poskytujúci host/group metadata.

CLI môže dostať jeden alebo viac sources:

```bash
ansible-inventory -i inventories/prod -i inventories/shared --graph
```

Výsledný inventory sa agreguje. Poradie, duplicate host identity a variable precedence preto musia byť vedomé.

## 2. Host identity

Základnou inventory identitou je `inventory_hostname`.

Príklad:

```yaml
all:
  hosts:
    web-01:
      ansible_host: 10.20.1.11
```

Tu:

- `inventory_hostname` je `web-01`,
- connection address je `10.20.1.11`.

Alias umožňuje používať stabilnú logickú identitu aj pri zmene IP alebo DNS. Zároveň môže skryť omyl, ak alias a real target nie sú kontrolované.

## 3. Groups

Groups reprezentujú množiny hosts podľa napríklad:

- role,
- environmentu,
- regionu,
- ownershipu,
- OS family,
- lifecycle stage,
- deployment ring.

Príklad YAML inventory:

```yaml
all:
  children:
    production:
      children:
        web:
          hosts:
            web-01:
              ansible_host: 10.20.1.11
            web-02:
              ansible_host: 10.20.1.12
        database:
          hosts:
            db-01:
              ansible_host: 10.20.2.21
```

Host môže patriť do viacerých groups. Group hierarchy nie je filesystem hierarchy; vytvára parent/child membership a variable inheritance model.

## 4. Built-in groups

Ansible poskytuje špeciálne groups:

- `all` — všetky inventory hosts,
- `ungrouped` — hosts, ktoré nepatria do žiadnej user-defined group okrem `all`.

Tieto groups sú vhodné pre globálne defaults, ale ukladať do `all` široké privilegované variables môže vytvoriť nebezpečný implicitný scope.

## 5. Static inventory

### INI

```ini
[web]
web-01 ansible_host=10.20.1.11
web-02 ansible_host=10.20.1.12

[database]
db-01 ansible_host=10.20.2.21

[production:children]
web
database
```

INI syntax je stručná, ale typing hodnôt môže byť menej intuitívny. Hodnoty definované inline na host line a hodnoty v `:vars` sections nemusia byť interpretované rovnakým spôsobom.

### YAML

```yaml
all:
  children:
    web:
      hosts:
        web-01:
          ansible_host: 10.20.1.11
```

YAML poskytuje čitateľnejšiu nested štruktúru a explicitnejšie dátové typy, ale stále vyžaduje validáciu parserom, nie iba YAML linterom.

## 6. Dynamic inventory

Dynamic inventory plugin načíta hosts a groups z external source, napríklad:

- cloud API,
- CMDB,
- virtualization platformy,
- service registry,
- Kubernetes alebo iného infrastructure API.

Typický plugin configuration file:

```yaml
plugin: some.collection.inventory_plugin
regions:
  - eu-central-1
keyed_groups:
  - key: tags.environment
    prefix: env
compose:
  ansible_host: private_ip_address
```

Presná schema závisí od pluginu.

Dynamic inventory má výhody:

- menej ručnej synchronizácie,
- väzbu na authoritative source,
- automatické groups podľa metadata,
- aktuálnejšie ephemeral hosts.

Riziká:

- API outage,
- stale cache,
- rate limits,
- credential scope,
- neočakávané group composition,
- zmena plugin version behavioru,
- prázdny inventory interpretovaný ako úspešný no-op.

## 7. Inventory plugins vs. scripts

Inventory plugins sú preferovaný extension model. Poskytujú:

- dokumentovanú configuration schema,
- integration s cache a Ansible plugin modelom,
- verify/parse behavior,
- collection versioning.

Legacy scripts typicky vypisujú JSON. Stále môžu fungovať, ale často majú slabšiu integráciu, validation a lifecycle.

## 8. Inventory directory

Directory môže obsahovať viac inventory sources:

```text
inventories/prod/
├── 01-static.yml
├── 10-cloud.yml
├── group_vars/
│   ├── all.yml
│   └── web.yml
└── host_vars/
    └── web-01.yml
```

Nie každý file v directory musí byť inventory source; extension a ignore patterns ovplyvňujú, čo sa načíta. Explicitné naming conventions znižujú nejasnosť.

## 9. Host a group variables

Variables možno definovať:

- inline v inventory,
- pod `vars` v YAML inventory,
- v `group_vars/`,
- v `host_vars/`,
- cez vars plugins,
- z dynamic inventory metadata.

Odporúčaný model:

- inventory definuje topology a environment-specific data,
- roles definujú reusable defaults a behavior,
- secrets sú v secret-management vrstve,
- playbook explicitne prepája capability s target groups.

### `group_vars`

```yaml
# group_vars/web.yml
http_port: 8080
app_environment: production
```

### `host_vars`

```yaml
# host_vars/web-01.yml
maintenance_window: sunday-02:00
```

Host vars majú užší scope než group vars, ale celkový variable precedence model zahŕňa aj playbook, role, facts, registered values a extra vars.

## 10. Group variable conflicts

Host môže patriť do viacerých groups, ktoré definujú rovnaký variable name. Výsledok môže závisieť od:

- parent/child hierarchy,
- group priority,
- inventory source ordering,
- vars plugin behavior,
- neskorších higher-precedence definitions.

Neopieraj kritickú konfiguráciu o implicitné alfabetické poradie groups. Pri prekrývajúcich sa groups definuj jasný ownership alebo explicitnú priority policy.

## 11. Connection variables

Bežné connection variables zahŕňajú napríklad:

- `ansible_host`,
- `ansible_port`,
- `ansible_user`,
- `ansible_connection`,
- `ansible_python_interpreter`,
- privilege-escalation variables,
- proxy alebo SSH common arguments.

Connection variables môžu zásadne zmeniť trust boundary. Napríklad zmena `ansible_connection` zo SSH na local môže spôsobiť vykonanie tasku na control node.

## 12. Inventory patterns

Play alebo CLI command vyberá hosts cez pattern:

```yaml
- hosts: web
```

Príklady kombinácií:

```text
web:database
web:&production
production:!maintenance
```

Význam:

- union,
- intersection,
- exclusion.

Pattern sa vyhodnocuje voči **aktuálne načítanému inventory**. Neexistujúca group môže viesť k nulovému target setu, nie automaticky k bezpečnému failure podľa očakávania workflowu.

Pred citlivým runom over target set:

```bash
ansible-playbook -i inventories/prod site.yml --limit 'web:&production' --list-hosts
```

## 13. `--limit`

`--limit` zužuje host pattern z playbooku. Nemal by byť jedinou production safety kontrolou, pretože:

- operator ho môže zabudnúť,
- pattern môže byť nesprávny,
- inventory sa môže zmeniť,
- automation controller môže používať vlastný limit field.

Bezpečnosť má kombinovať environment isolation, approvals, inventory review a bounded rollout.

## 14. Inventory inspection

### Graph

```bash
ansible-inventory -i inventories/prod --graph
```

Ukáže group hierarchy a hosts.

### List

```bash
ansible-inventory -i inventories/prod --list
```

Vypíše resolved inventory data v machine-readable forme.

### Host view

```bash
ansible-inventory -i inventories/prod --host web-01
```

Zobrazí resolved variables pre konkrétny host.

### Playbook target set

```bash
ansible-playbook -i inventories/prod site.yml --list-hosts
```

Každý production pipeline by mal uchovať target summary ako evidence bez leaknutia secrets.

## 15. Dynamic groups

Inventory plugin môže vytvárať groups z metadata cez `keyed_groups` alebo obdobný mechanizmus.

Príklad výsledku:

```text
env_production
role_web
region_eu_central_1
```

Group naming musí byť stabilné a normalizované. Zmena tagu v cloud-e môže automaticky presunúť host do iného automation scope-u.

## 16. Constructed inventory

Constructed plugin dokáže:

- vytvárať variables cez expressions,
- skladať groups podľa podmienok,
- transformovať metadata z iných sources.

Je výkonný, ale môže skryť komplexnú business logiku v inventory vrstve. Výsledný graph treba testovať ako code.

## 17. Inventory caching

Cache znižuje API latency a rate pressure, ale vytvára freshness trade-off.

Definuj:

- TTL,
- cache backend,
- invalidation,
- behavior pri API outage,
- fail-open/fail-closed model,
- observability cache age.

Stale inventory môže obsahovať odstránený host alebo vynechať nový kritický node.

## 18. Localhost

Ak play používa `localhost` bez explicitného inventory entry, Ansible môže vytvoriť implicitný localhost s osobitným správaním. Pre produkčný automation je vhodnejšie explicitne definovať local execution assumptions.

Príklad:

```yaml
all:
  hosts:
    localhost:
      ansible_connection: local
      ansible_python_interpreter: "{{ ansible_playbook_python }}"
```

Localhost tasks majú prístup k control-node credentials, filesystemu a network pathu. Nie sú automaticky nízkorizikové.

## 19. Inventory a secrets

Do inventory repository nepatria plaintext:

- passwords,
- private keys,
- API tokens,
- Vault passwords,
- cloud secret keys.

Inventory môže obsahovať referencie alebo identity metadata, ale secret value má prísť cez Vault/external secret provider/controller credential injection.

`ansible-inventory --list` môže zobraziť resolved variables. Preto aj diagnostický output potrebuje access control.

## 20. Environment isolation

Model jedného inventory s group `dev`, `stage`, `prod` je jednoduchý, ale nemusí byť dostatočná security boundary.

Silnejšie oddelenie môže používať:

- samostatné inventory directories,
- samostatné cloud identities,
- samostatné controller credentials,
- protected job templates,
- odlišné network paths,
- environment-specific approvals.

Inventory separation nerieši všetko, ale znižuje accidental cross-environment targeting.

## 21. Testing inventory

Testuj:

- parser success,
- očakávaný host count,
- required groups,
- forbidden overlaps,
- mandatory variables,
- duplicate logical identities,
- valid connection metadata,
- production targets bez public/untrusted addresses,
- dynamic inventory freshness.

Príklad jednoduchého CI checku:

```bash
ansible-inventory -i inventories/prod --list > inventory.json
python scripts/validate_inventory.py inventory.json
```

## 22. Troubleshooting

### Inventory je prázdny

Over `-i` path, current working directory, plugin enablement, file extension, YAML schema, credentials a plugin logs. Prázdny dynamic result môže byť API/filter problém.

### Host nie je v očakávanej group

Over source metadata, parent/child structure, `keyed_groups`, composition expression, cache age a exact group name.

### Host používa nesprávnu IP

Porovnaj `inventory_hostname`, `ansible_host`, duplicate definitions a variable precedence cez:

```bash
ansible-inventory -i inventories/prod --host <host>
```

### Variables sa prepisujú

Zisti všetky groups hostu a sources rovnakej variable. Neopravuj problém pridaním ďalšieho higher-precedence override bez odstránenia ambiguity.

### Plugin sa nepoužil

Over plugin configuration `plugin:` field, filename suffix, collection availability, enablement a verify conditions.

### `--limit` vybral neočakávané hosts

Použi `--list-hosts`, rozlož union/intersection/exclusion pattern a over group graph.

## 23. Anti-patterny

### Inventory ako CMDB dump bez ownershipu

Veľké množstvo metadata nemá jasný význam ani lifecycle.

### Secrets inline pri hosts

Resolved inventory ich môže zobraziť v CLI, logs alebo debug outpute.

### Jeden globálny inventory pre všetky boundaries

Operator typo môže zasiahnuť development aj production.

### Group names podľa dočasných organizačných tímov

Topology a lifecycle sa menia inak než org chart.

### Dynamic inventory bez cache observability

Nie je známe, či automation používa aktuálny alebo starý target set.

### Kritické variables definované vo viacerých groups

Výsledok závisí od precedence detailov namiesto explicitného contractu.

## 24. Rozhodovací rámec

1. Ktorý systém je authoritative source host identity?
2. Ktoré inventory sources sa agregujú?
3. Ako sa definuje stabilný `inventory_hostname`?
4. Aké groups reprezentujú role, environment a failure domain?
5. Kde patria host/group variables a kde už role defaults?
6. Ako sú oddelené secrets?
7. Aký freshness model má dynamic inventory a cache?
8. Ako CI overí target count a forbidden overlaps?
9. Aká je production environment isolation?
10. Aká evidence target setu sa uchová pred runom?

## 25. Kontrolné otázky

1. Aký je rozdiel medzi inventory source a výsledným inventory?
2. Aký je rozdiel medzi `inventory_hostname` a `ansible_host`?
3. Ako fungujú parent a child groups?
4. Prečo host v mnohých groups komplikuje variables?
5. Aké výhody a riziká má dynamic inventory?
6. Na čo slúži inventory cache?
7. Ako overiť resolved variables hostu?
8. Prečo `--limit` nie je dostatočná safety boundary?
9. Aké riziká má implicitný localhost?
10. Ako testovať inventory v CI?

## Glossary impact

Relevantné pojmy: Ansible inventory, inventory source, inventory plugin, static inventory, dynamic inventory, inventory host, inventory group, `inventory_hostname`, `ansible_host`, host variables, group variables, inventory pattern, constructed inventory, inventory cache a implicit localhost.

## Oficiálna dokumentácia

- [Building Ansible inventories](https://docs.ansible.com/projects/ansible/latest/inventory_guide/index.html)
- [How to build your inventory](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_inventory.html)
- [Working with dynamic inventory](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_dynamic_inventory.html)
- [Patterns: targeting hosts and groups](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_patterns.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Ansible architecture](ansible-architecture.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Modules, tasks, plays a playbooks →](modules-tasks-plays-playbooks.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
