# Inventory

Ansible inventory určuje, ktoré targety automation pozná, pod akou logickou identitou ich adresuje, do akých groups patria a s akým connection a variable contextom sa na ne pripája. Inventory nie je iba zoznam hostnames. Je to prekladová vrstva medzi externou infraštruktúrnou realitou a konkrétnym execution scope-om playbooku.

Táto kapitola používa jeden priebežný scenár. Atlas Payments má 12 produkčných application hosts v troch availability zones. Dynamic cloud inventory ich objavuje podľa tags, static inventory dopĺňa bastion a explicitné maintenance exclusions a playbook cieli `payments_app:&production:!maintenance`. Pred každým rolloutom musí pipeline dokázať, že resolved target set obsahuje presne očakávané host identity a že connection metadata smerujú na správne produkčné nodes.

## 1. Dominantný model: source-to-target-coverage lifecycle

```text
authoritative host sources
→ plugin parsing a source aggregation
→ stable inventory host identity
→ group membership a hierarchy
→ variable a connection-context resolution
→ pattern a limit evaluation
→ expected-vs-resolved target inventory
→ host execution coverage
→ runtime fleet verification
→ cache/source reconciliation a audit
```

Správny playbook nad nesprávnym resolved inventory je stále nebezpečná automation. Target identity a coverage preto musia byť schvaľovanou evidence rovnako ako samotný task content.

## 2. Atlas inventory subject

Pred production runom zaznamenaj:

```text
inventory source paths a plugin configuration digests
inventory plugin/collection versions
cloud/CMDB account a region identity
source query, filters a tag schema
cache backend, generation a age
static inventory revision
host/group vars source revisions
resolved host identities a connection addresses
pattern, limit a controller job template
expected target manifest a count
resolution timestamp
```

Toto je **inventory resolution subject**. Rovnaký playbook pattern môže vybrať inú množinu hosts, ak sa zmení cloud tag, plugin version, cache, source order alebo group construction rule.

## 3. Inventory source verzus resolved inventory

Source je vstup parsovaný inventory pluginom. Môže byť:

- YAML alebo INI file;
- directory viacerých sources;
- dynamic inventory plugin configuration;
- legacy script;
- external CMDB, cloud alebo service registry.

CLI môže agregovať viac sources:

```bash
ansible-inventory \
  -i inventories/prod-static \
  -i inventories/prod-cloud.yml \
  --list
```

Resolved inventory je výsledok po:

```text
parse každého source
→ merge duplicate host identities
→ build groups a hierarchy
→ load vars plugins/group_vars/host_vars
→ resolve connection metadata
```

Source success neznamená správny výsledok. Dynamic plugin môže úspešne vrátiť prázdnu množinu alebo stale cache.

## 4. Stable host identity

Základnou logickou identitou je `inventory_hostname`.

```yaml
all:
  hosts:
    payments-app-a1:
      ansible_host: 10.40.11.21
```

Tu:

```text
inventory_hostname = payments-app-a1
connection address = 10.40.11.21
```

Stabilný alias umožňuje meniť IP bez zmeny automation identity. Zároveň vytvára riziko, ak sa alias zlúči s iným source-om alebo `ansible_host` ukazuje na nesprávny objekt.

Host identity contract má podľa potreby obsahovať:

```text
stable inventory name
cloud/CMDB immutable instance ID
environment/account
region/AZ
role
lifecycle state
connection address a host-key identity
```

IP adresa sama osebe je slabá dlhodobá identita. Môže byť recyklovaná.

## 5. Worked failure: recyklovaná IP za stabilným aliasom

Static inventory stále obsahuje:

```yaml
payments-app-b2:
  ansible_host: 10.40.12.44
```

Pôvodný production instance bol odstránený. IP neskôr dostal testovací host v peered networke. Host-key checking bolo vypnuté a connection credential sa na test hoste tiež akceptovalo.

Mechanizmus:

```text
stable logical alias
+ stale address mapping
+ recyklovaná IP
+ chýbajúca remote identity verification
→ správny host pattern vyberie nesprávny remote objekt
```

Controls:

- dynamic source viazaný na immutable instance ID;
- host-key/certificate identity verification;
- environment/account assertion;
- pre-run comparison inventory identity vs. cloud asset identity;
- retirement reconciliation starej static entry.

## 6. Groups ako scope a inheritance graph

Groups môžu reprezentovať:

- environment;
- service role;
- region/AZ;
- deployment ring;
- ownership;
- OS family;
- maintenance state;
- compliance alebo failure domain.

Príklad:

```yaml
all:
  children:
    production:
      children:
        payments_app:
          hosts:
            payments-app-a1:
            payments-app-a2:
    maintenance:
      hosts:
        payments-app-a2:
```

Host môže patriť do viacerých groups. Group hierarchy vytvára membership a variable inheritance, nie filesystem poradie.

Built-in groups:

- `all` — všetky inventory hosts;
- `ungrouped` — hosts mimo user-defined groups.

Ukladať privilegované defaults do `all` môže nečakane rozšíriť connection alebo become scope na každý target.

## 7. Dynamic inventory a authoritative metadata

Dynamic plugin môže objavovať hosts z cloud API, virtualization platformy, CMDB alebo Kubernetes API.

```yaml
plugin: vendor.cloud.compute
regions:
  - eu-central-1
filters:
  tag:Environment: production
keyed_groups:
  - key: tags.Role
    prefix: role
  - key: placement.availability_zone
    prefix: az
compose:
  ansible_host: private_ip_address
```

Výhody:

- automatická discovery ephemeral hosts;
- menšia manuálna synchronizácia;
- groups odvodené z authoritative metadata;
- jednoduchšia fleet coverage.

Failure boundaries:

- wrong cloud account/region;
- broad alebo zmenený filter;
- stale cache;
- API partial result;
- plugin version mení normalization;
- tag typo presunie host do iného scope-u;
- empty result sa interpretuje ako bezpečný no-op.

Dynamic neznamená automaticky aktuálny ani autoritatívny. Autoritatívny musí byť source, query a identity contract spolu.

## 8. Worked failure: tag typo presunul database host

Database instance dostane omylom tag `Role=payments_app`. Dynamic inventory z neho vytvorí group membership `role_payments_app`. Patch playbook cieli túto group a vykoná application package tasks aj na database hoste.

```text
cloud tag je automation input
→ keyed_groups vytvorí scope
→ playbook pattern dôveruje group membership
→ správny task zasiahne nesprávny resource class
```

Pre kritické groups používaj kombinovaný invariant:

```text
role tag
+ expected image/OS/service facts
+ forbidden group overlap
+ asset type
+ environment identity
```

CI má odmietnuť host, ktorý súčasne patrí do nezlučiteľných groups, napríklad `payments_app` a `database`.

## 9. Static inventory a explicitný ownership

YAML inventory:

```yaml
all:
  children:
    bastions:
      hosts:
        prod-bastion-01:
          ansible_host: 10.40.0.10
```

INI je stručnejšie, ale typing a `:vars` semantics môžu byť menej zrejmé. YAML linter sám nepotvrdí Ansible inventory schema ani výslednú group hierarchy.

Static entry potrebuje ownera a retirement lifecycle. Bez reconciliation môže prežiť odstránený host alebo starú IP celé mesiace.

Dobrý model:

```text
dynamic source pre ephemeral managed fleet
+ static source iba pre explicitne vlastnené stabilné exceptions
→ validation proti authoritative asset inventory
```

## 10. Inventory directories a source aggregation

Príklad layoutu:

```text
inventories/prod/
├── 01-static.yml
├── 10-cloud.yml
├── group_vars/
│   ├── all.yml
│   └── payments_app.yml
└── host_vars/
    └── payments-app-a1.yml
```

Directory loading závisí od plugin enablement, filenames, extensions a ignore patterns. Prefixy môžu zlepšiť čitateľnosť source orderu, ale critical semantics sa nemajú opierať o implicitné alfabetické poradie.

Duplicate `inventory_hostname` z dvoch sources sa môže zlúčiť. Preto validuj:

- duplicate logical identity;
- conflicting immutable instance IDs;
- conflicting `ansible_host`;
- source ownership;
- unexpected variable override.

## 11. Variables ako behavior a connection inputs

Inventory môže poskytovať:

- topology a environment data;
- connection address/user/plugin;
- interpreter;
- role/service parameters;
- references na secret sources.

Reusable role defaults a behavior nemajú byť nekontrolovane kopírované do inventory. Secrets nemajú byť plaintext inventory values.

Connection variables ako:

```text
ansible_host
ansible_port
ansible_user
ansible_connection
ansible_python_interpreter
ansible_become*
```

menia execution boundary. Zmena `ansible_connection: ssh` na `local` môže spôsobiť, že task pre host alias beží na control node-e.

## 12. Group variable conflicts

Host môže dediť rovnakú variable z viacerých groups. Výsledok ovplyvňuje group hierarchy, source ordering, group priority a vyššie precedence vrstvy.

Príklad:

```text
production: package_channel=stable
canary: package_channel=candidate
payments_app: package_channel=payments-stable
```

Host patriaci do všetkých troch potrebuje explicitný contract, nie nádej, že správna group „vyhrá“ alfabeticky.

Pri critical values:

- používaj jednoznačného ownera;
- validuj forbidden multiple definitions;
- publikuj resolved value identity pred runom;
- neodstraňuj ambiguity ďalším extra-var override-om.

## 13. Pattern a limit ako set algebra

Play pattern sa vyhodnocuje voči aktuálnemu resolved inventory:

```text
payments_app:database       union
payments_app:&production    intersection
production:!maintenance     exclusion
```

Atlas používa:

```text
payments_app:&production:!maintenance
```

`--limit` iba ďalej zužuje play pattern. Nie je samostatná environment safety boundary. Operator ho môže vynechať a dynamic inventory sa môže medzi review a runom zmeniť.

Pred citlivým runom:

```bash
ansible-playbook \
  -i inventories/prod \
  site.yml \
  --limit 'payments_app:&production:!maintenance' \
  --list-hosts
```

Target manifest má byť uchovaný ako subject-bound evidence.

## 14. Expected target inventory

Resolved target set musí byť porovnaný s očakávaním:

```text
expected stable host IDs: 12
resolved inventory hosts: 12
selected by pattern: 11
excluded maintenance: 1
attempted: 11
verified converged: 11
```

Expected inventory nemusí byť iba pevný count. Môže definovať:

- minimálny/maximálny count;
- presný release manifest;
- požadované AZ/ring zastúpenie;
- forbidden groups/overlaps;
- allowed lifecycle states;
- maximum cache age;
- required connection identity fields.

Prázdny target set musí mať explicitný verdict. Pre production rollout je typicky failure alebo manual review, nie green no-op.

## 15. Worked failure: API outage vytvoril green no-op

Dynamic inventory plugin pri API timeout-e vráti empty result a warning. Wrapper script warning nepropaguje a playbook skončí:

```text
skipping: no hosts matched
exit code 0
```

Mechanizmus:

```text
source failure
→ empty inventory namiesto invalid evidence
→ pattern vyberie nula hosts
→ žiadny task nemôže zlyhať
→ process success sa interpretuje ako rollout success
```

Gate musí rozlišovať:

- valid empty inventory podľa contractu;
- source/API/tool failure;
- stale-cache fallback;
- filter, ktorý legitímne vrátil nula;
- unexpected undersized target set.

## 16. Inventory cache a freshness

Cache znižuje API latency a rate pressure, ale mení target reality na snapshot.

Definuj:

```text
cache backend
generation/timestamp
TTL
source query identity
invalidation
behavior pri API outage
fail-open/fail-closed policy
maximum age pre production mutation
```

Stale cache môže:

- obsahovať terminated host;
- vynechať nový host;
- zachovať staré group membership;
- používať starú IP;
- skryť maintenance alebo quarantine tag.

Cache fallback môže byť vhodný pre read-only diagnostiku, ale production mutation potrebuje prísnejší freshness contract.

## 17. Constructed groups a hidden logic

Constructed inventory môže transformovať metadata a vytvárať groups cez expressions. Je užitočný, ale môže skryť business policy v target-resolution vrstve.

Príklad rizika:

```text
if tags.Environment != 'dev'
→ group production
```

Missing alebo typo tag by host zaradil do production. Bezpečnejšie je explicitné positive matching a quarantine pre unknown metadata.

Constructed logic testuj ako code:

- fixtures pre valid metadata;
- missing/null fields;
- case/normalization;
- forbidden overlaps;
- plugin upgrade behavior.

## 18. Localhost a local connection

Implicitný localhost má osobitné behavior a môže použiť control-node Python. Produkčný automation má local execution assumptions deklarovať explicitne.

```yaml
all:
  hosts:
    localhost:
      ansible_connection: local
      ansible_python_interpreter: "{{ ansible_playbook_python }}"
```

Localhost tasks majú prístup k controller filesystemu, tokens, networku a cloud credential chainu. Nie sú automaticky nízkorizikové.

## 19. Secrets a resolved inventory output

Do inventory repository nepatria plaintext passwords, private keys, tokens ani Vault passwords. Inventory môže niesť secret reference alebo credential selector, ale hodnotu má injektovať controller/Vault/external secret provider.

```bash
ansible-inventory -i inventories/prod --list
```

môže zobraziť resolved variables. Diagnostický output preto potrebuje redaction, restricted access a retention.

## 20. Environment isolation

Jedna group `prod` v globálnom inventory nie je dostatočná security boundary pre všetky organizácie.

Silnejší model môže oddeliť:

- inventory sources/directories;
- cloud accounts/subscriptions;
- controller credentials;
- execution environments/job templates;
- network paths;
- approval policy;
- logging a recovery owners.

Target pipeline má pred connection potvrdiť environment identity aj na provider/asset vrstve, nie iba podľa group name.

## 21. Causal troubleshooting walkthrough: rollout zmenil nesprávny host a vynechal dva správne

Atlas očakával 12 application hosts, jeden v maintenance. `--list-hosts` ukázal desať targetov a po run-e telemetry našla zmenu na testovacom hoste.

### 1. Zafixuj inventory subject

Zaznamenaj source digests, plugin versions, cloud account/region, filters, cache generation, static revision, pattern/limit a expected manifest.

### 2. Súťažiace hypotézy

1. Dynamic source vrátil partial result.
2. Cache bola stale.
3. Dva hosts stratili required tag/group membership.
4. Static alias ukázal na recyklovanú IP.
5. Duplicate `inventory_hostname` prepísal `ansible_host`.
6. Pattern/exclusion odstránil správne hosts.
7. Group variable zmenila `ansible_connection` alebo connection address.
8. Pipeline použila staging account/plugin config.

### 3. Diskriminačné observation points

- raw source API result a request ID;
- cache timestamp/generation;
- `ansible-inventory --graph`, `--list` a `--host`;
- immutable cloud instance IDs;
- duplicate identity validation;
- group/tag history v audit logu;
- exact pattern set algebra a `--list-hosts`;
- SSH host key/certificate a remote machine identity;
- resolved connection variables bez secret values.

### 4. Containment

Pozastav rollout. Izoluj nesprávne zmenený host a over, či nebol production credential použitý mimo production boundary.

### 5. Recovery

- partial API/cache → obnov fresh source a rerun target validation;
- tag/group error → oprav metadata a forbidden-overlap test;
- stale static alias → odstráň entry a obnov host identity trust;
- duplicate identity → rozdeľ/rename stable keys a audit affected runs;
- wrong pattern → oprav target contract;
- wrong account/config → revoke credentials a skontroluj zasiahnutý environment.

### 6. Over pôvodný outcome

Potvrď všetkých 12 immutable production instance IDs, jeden vedomý maintenance exclusion, správne connection identities a 11 verified converged hosts. Test host nesmie zostať s production configuration alebo credential residue.

### 7. Posuň control skôr

Pridaj immutable asset-ID binding, expected target manifest, cache-age gate, duplicate-host check, forbidden environment overlap a host identity verification.

## 22. Inventory validation pipeline

```text
load pinned plugin a source configuration
→ authenticate read-only source identity
→ build fresh resolved inventory
→ validate parser/source success
→ validate host identity uniqueness
→ validate required/forbidden groups
→ validate connection metadata
→ compare expected target inventory
→ evaluate production pattern a limit
→ publish redacted target manifest
→ approval
→ execute a compare verified coverage
```

Praktické inspection príkazy:

```bash
ansible-inventory -i inventories/prod --graph
ansible-inventory -i inventories/prod --list
ansible-inventory -i inventories/prod --host payments-app-a1
ansible-playbook -i inventories/prod site.yml --list-hosts
```

CI môže validovať machine-readable output, ale musí chrániť resolved secrets.

## 23. Evidence a observability

Uchovaj:

```text
inventory subject
→ source health/freshness
→ resolved host/group graph
→ expected target comparison
→ selected target manifest
→ per-host connection identity metadata
→ attempted a verified host inventory
→ exclusions/failures/recovery
```

Sleduj:

- unexpected host-count delta;
- empty/undersized inventories;
- cache age;
- duplicate identities;
- forbidden group overlaps;
- source API failures;
- hosts bez environment/owner metadata;
- stale static entries;
- selected-but-unverified hosts;
- inventory plugin/version drift.

## 24. Referenčné pravidlá

- Inventory source a resolved inventory sú odlišné objekty.
- `inventory_hostname` je automation identity; `ansible_host` je connection address.
- Dynamic inventory potrebuje source, filter, plugin a cache subject.
- Tag je executable scope input, nie iba metadata.
- Empty target set nesmie byť ticho interpretovaný ako success.
- Groups tvoria membership a variable inheritance graph.
- Critical variables nemajú implicitne súťažiť vo viacerých groups.
- `--limit` nie je environment security boundary.
- Cache freshness je súčasť production mutation evidence.
- Run success potrebuje expected-vs-verified host coverage.

## 25. Kontrolné otázky

1. Čo tvorí inventory resolution subject?
2. Ako sa líši inventory source od resolved inventory?
3. Prečo IP adresa nie je dostatočná stable host identity?
4. Ako duplicate `inventory_hostname` zmení connection target?
5. Prečo cloud tag patrí do automation trust boundary?
6. Ako group hierarchy a variable precedence ovplyvnia host behavior?
7. Kedy je empty inventory validný a kedy invalid evidence?
8. Prečo stale cache môže zasiahnuť nesprávny host?
9. Čo má obsahovať expected target inventory?
10. Aké dôkazy potvrdia complete host coverage po run-e?

## Glossary impact

Relevantné pojmy: inventory resolution subject, inventory source, resolved inventory, stable inventory host identity, connection address, dynamic inventory, constructed group, inventory cache generation, expected target inventory, target manifest, duplicate host identity, forbidden group overlap, empty-inventory verdict a host coverage.

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