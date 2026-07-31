# Inventory

Ansible inventory určuje, ktoré targety automation pozná, pod akou logickou identitou ich adresuje, do akých groups patria a s akým connection a variable contextom sa na ne pripája. Nie je to iba zoznam IP adries. Je to target-authority graph medzi cloudom alebo CMDB, inventory plugins, cache, logical host identities, group inheritance, connection metadata a playbook patternom.

Kapitola pokračuje incidentom `IAC-PAY-78`. Atlas Payments má dvanásť produkčných application hosts. Dynamic cloud inventory ich objavuje podľa tags, static source pridáva bastion a `maintenance` exclusions. Stale cache však vynechá dva nové hosts, stará static entry smeruje recyklovanou IP na testovací host a typo `Role=payments_app` zaradí database node do application group. Playbook je správny, ale resolved target graph nie.

## 1. Dominantný source-to-coverage lifecycle

```text
authoritative asset sources
→ inventory plugin parsing a source order
→ logical inventory_hostname a immutable asset identity
→ groups a parent/child membership
→ host/group connection a variable data
→ cache generation a freshness
→ pattern a --limit set evaluation
→ expected-vs-resolved target manifest
→ per-host execution coverage
→ fleet runtime verification
→ source/cache reconciliation
```

Ansible môže zlyhať iba na targetoch, ktoré pozná. Inventory omission preto nevytvorí `unreachable`; vytvorí tiché nepokrytie.

## 2. Exact inventory resolution subject

```yaml
inventorySubject:
  sourceRevision: 42ad9c1
  sources:
    - path: inventories/prod/01-static.yml
      digest: sha256:11aa...
    - path: inventories/prod/10-cloud.aws_ec2.yml
      digest: sha256:2bb9...
      pluginVersion: amazon.aws-pinned
      account: "771100001234"
      regions: [eu-central-1]
  cache:
    backend: redis-prod-inventory
    generatedAt: 2026-07-31T08:00:00Z
    maxAgeSeconds: 300
  pattern: payments_app:&production:!maintenance
  limit: none
  expectedManifestDigest: sha256:f39c...
  expectedCount: 12
  resolutionTime: 2026-07-31T08:02:00Z
```

Rovnaký pattern môže vybrať inú množinu hosts, keď sa zmení source order, plugin version, cache, tags, group construction alebo `--limit`.

## 3. Inventory source verzus resolved inventory

Source môže byť YAML/INI file, directory, dynamic plugin config, legacy script alebo external service. Ansible skladá inventory z jedného alebo viacerých sources. Pri viacerých sources môže load order ovplyvniť konfliktné variables a empty groups sa môžu správať podľa pluginu. citeturn329472search1

Praktický read-back:

```bash
ansible-inventory \
  -i inventories/prod/01-static.yml \
  -i inventories/prod/10-cloud.aws_ec2.yml \
  --list > resolved-inventory.json

ansible-inventory -i inventories/prod --graph
```

`--list` preukazuje resolved inventory model pre aktuálny Ansible runtime a source set. Nepreukazuje connectivity, current cloud asset existence ani SSH host identity.

## 4. Stable logical a immutable remote identity

```yaml
all:
  hosts:
    payments-app-a1:
      ansible_host: 10.40.11.21
      atlas_instance_id: i-0abc123
      atlas_environment: prod-eu
```

```text
inventory_hostname = payments-app-a1
connection address = 10.40.11.21
immutable asset ID = i-0abc123
```

Logical alias môže zostať stabilný pri IP change. IP sama je slabá identity, pretože sa môže recyklovať. Pre-run verifier porovná inventory asset ID s cloud API a SSH host key/certificate.

## 5. Worked failure: recyklovaná IP

Static inventory stále mapuje `payments-app-b2` na `10.40.12.44`. Pôvodný production host bol odstránený a IP neskôr dostal test host v peered networke. Host-key checking bolo vypnuté.

```text
stale logical mapping
+ recyklovaná IP
+ credential accepted na test hoste
+ bez host identity verification
→ production play zasiahne test object
```

Recovery:

1. zastaviť run;
2. zachovať inventory/source a SSH evidence;
3. overiť cloud instance IDs a host keys;
4. odstrániť stale static entry;
5. obnoviť dynamic authoritative mapping;
6. auditovať test host mutation;
7. otestovať forbidden identity mismatch.

## 6. Groups ako membership a variable graph

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

Host môže patriť do viacerých groups. Groups reprezentujú role, environment, AZ, ring, OS alebo maintenance state. Built-in `all` zahŕňa všetky hosts; privilegované connection alebo become defaults v `all` preto môžu nečakane zasiahnuť celý inventory.

Pred playom sa inventory/group variables flattenujú na host. Parent/child/host specificity a source/load rules ovplyvňujú effective value. citeturn329472search1turn329472search2

## 7. Dynamic inventory ako executable query

Ilustračný AWS plugin config:

```yaml
plugin: amazon.aws.aws_ec2
regions:
  - eu-central-1
filters:
  tag:Environment: prod-eu
  instance-state-name: running
keyed_groups:
  - key: tags.Role
    prefix: role
  - key: placement.availability_zone
    prefix: az
compose:
  ansible_host: private_ip_address
```

Dynamic inventory failure boundaries:

```text
wrong account/region
broad alebo chybný filter
partial API result
stale cache
plugin upgrade/normalization
missing alebo typo tag
empty result interpretovaný ako no-op
```

Dynamic neznamená current ani correct. Query, caller identity, plugin version a cache generation tvoria subject.

## 8. Worked failure: tag typo zaradil database host

Database instance dostane `Role=payments_app`. `keyed_groups` ju vloží do application group a playbook nainštaluje application package.

```text
cloud tag
→ group construction
→ pattern membership
→ correct task on wrong resource class
```

Critical group membership potrebuje viac invariantov:

```text
role tag
+ asset type
+ image/OS family
+ environment/account
+ forbidden group overlaps
```

Validation script môže odhaliť overlap:

```bash
jq -e '
  [
    ._meta.hostvars
    | to_entries[]
    | select(
        (.value.atlas_role == "payments_app") and
        (.value.atlas_asset_type == "database")
      )
  ] | length == 0
' resolved-inventory.json
```

## 9. Static inventory ako vlastnená exception

```yaml
all:
  children:
    bastions:
      hosts:
        prod-bastion-01:
          ansible_host: 10.40.0.10
          atlas_instance_id: i-0bastion
```

Static entry potrebuje ownera, review a retirement. Dobrý model používa dynamic source pre ephemeral fleet a static source iba pre explicitné stabilné exceptions, ktoré sa pravidelne porovnávajú s asset inventory.

## 10. Source order a duplicate identities

Directory:

```text
inventories/prod/
├── 01-static.yml
├── 10-cloud.aws_ec2.yml
├── group_vars/
│   ├── all.yml
│   └── payments_app.yml
└── host_vars/
    └── payments-app-a1.yml
```

Ansible môže zlúčiť duplicate `inventory_hostname` z viacerých sources. Kontroluj:

- duplicate logical name s odlišným instance ID;
- conflicting `ansible_host`;
- conflicting environment/role;
- unexpected variable override;
- source ownership.

Critical semantics sa nemajú spoliehať na to, že alphabetic load order náhodou vyberie správnu hodnotu.

## 11. Connection variables sú execution controls

```text
ansible_host
ansible_port
ansible_user
ansible_connection
ansible_python_interpreter
ansible_become*
```

Zmena `ansible_connection: ssh` na `local` presunie execution na controller. Zmena `ansible_user` alebo `become_user` mení effective identity. Preto connection variables patria do auditovateľného inventory contractu, nie do neprehľadného override mixu.

## 12. Pattern ako set algebra

Patterns môžu robiť union, intersection a exclusion. Oficiálny model používa pattern na výber hostov zo resolved inventory. citeturn329472search3

```text
payments_app:database
→ union

payments_app:&production
→ intersection

production:!maintenance
→ exclusion
```

Atlas používa:

```bash
ansible-playbook playbooks/payments.yml \
  -i inventories/prod \
  --limit 'payments_app:&production:!maintenance' \
  --list-hosts
```

`--limit` zužuje pattern, ale nie je environment security boundary. Pattern a inventory sa môžu medzi review a execution zmeniť, preto target manifest musí byť bound k runu.

## 13. Expected target manifest

```yaml
expectedTargets:
  environment: prod-eu
  service: payments-app
  minCount: 12
  maxCount: 12
  requiredAvailabilityZones:
    eu-central-1a: 4
    eu-central-1b: 4
    eu-central-1c: 4
  forbiddenGroups:
    - database
    - retired
  maximumInventoryCacheAgeSeconds: 300
```

Resolved comparison:

```text
expected 12
resolved 12
maintenance excluded 1
attempted 11
converged 11
runtime verified 11
```

Fixed count nie je vždy vhodný pri autoscaling fleet. Vtedy sa používa release/deployment manifest, min/max bounds a exact asset IDs pre current rollout cohort.

## 14. Empty a undersized inventory verdict

Dynamic source môže pri API failure vrátiť empty result a playbook vypíše `no hosts matched` s process success.

```text
source failure
→ empty inventory
→ zero task attempts
→ nič nemôže failnúť
→ false rollout success
```

Gate musí rozlišovať:

```text
VALID_EMPTY_BY_CONTRACT
SOURCE_OR_PLUGIN_FAILURE
STALE_CACHE_FALLBACK
FILTER_MATCHED_ZERO
UNEXPECTED_UNDERSIZED
```

Production mutation má pri nečakanom empty/undersized targete fail-closed.

## 15. Cache freshness

Inventory cache má contract:

```yaml
cachePolicy:
  backend: redis-prod-inventory
  ttlSeconds: 300
  maximumAgeForMutationSeconds: 300
  apiOutageBehavior: fail-closed
  owner: platform-inventory
```

Stale cache môže obsahovať terminated hosts, vynechať replacements, zachovať staré groups alebo IPs a ignorovať quarantine tag. Read-only diagnostika môže mať iný fallback než mutation run.

## 16. Constructed groups a missing metadata

Rizikový rule:

```text
Environment != dev
→ production
```

Missing tag sa stane production. Bezpečnejší model používa positive equality a unknown/quarantine group.

Fixtures testujú:

- valid production metadata;
- missing role/environment;
- case normalization;
- forbidden overlaps;
- plugin version upgrade;
- null values.

## 17. Variable conflicts v inventory

```text
production: package_channel=stable
canary: package_channel=candidate
payments_app: package_channel=payments-stable
```

Host vo všetkých groups potrebuje explicitný contract. Ansible precedence dokáže vybrať jednu hodnotu, ale nepreukazuje, že organizačný intent je správny.

Pre critical variables:

```text
one authoritative source
+ duplicate-definition lint
+ resolved host var read-back
+ forbidden conflict fixture
```

## 18. Secrets a inventory output

Inventory nemá obsahovať plaintext credentials. Môže obsahovať secret reference alebo credential selector.

`ansible-inventory --list` môže zobraziť resolved vars, preto output potrebuje restricted access a redaction. Nezverejňuj ho ako verejný CI artifact.

## 19. Localhost boundary

```yaml
all:
  hosts:
    localhost:
      ansible_connection: local
      ansible_python_interpreter: "{{ ansible_playbook_python }}"
```

Local tasks používajú controller filesystem, network a credentials. `localhost` nie je automaticky bezpečný ani neprivilegovaný target.

## 20. Worked incident: stale cache vynechala dva hosts

Cloud replacement vytvoril nové instance IDs, ale cache ostala stará. Pattern vybral desať healthy old/current entries a play skončil success.

```text
expected manifest 12 current IDs
→ resolved cache 10 IDs
→ tasks pass na 10
→ 2 nové hosts ostanú unconfigured
```

Recovery:

1. zastaviť ďalší batch;
2. zachovať cache generation a source API response;
3. refreshnúť inventory cez correct account identity;
4. porovnať exact asset IDs;
5. nakonfigurovať missing hosts cez reviewed cohort manifest;
6. overiť fleet version endpoint;
7. full-fleet second run.

## 21. Competing hypotheses pri chýbajúcom hoste

```text
H1: source API ho nevrátil
H2: cache je stale
H3: filter/tag ho vylúčil
H4: pattern alebo --limit ho vylúčil
H5: duplicate inventory_hostname ho zlúčil
H6: host je v maintenance/quarantine
H7: porovnávame iný account/region
```

Dôkazy:

- direct source API vs cached output H1/H2;
- raw metadata/filter H3;
- `--list-hosts` H4;
- resolved hostvars/instance IDs H5;
- group graph H6;
- caller account/region H7.

## 22. Acceptance a forbidden paths

Inventory blok je prijatý, keď:

```text
sources, plugins, account a cache generation sú pinned/read-backnuté
+ logical hosts majú immutable asset IDs
+ duplicate identities sú odmietnuté
+ critical groups nemajú forbidden overlap
+ expected a resolved target manifests sú porovnané
+ empty/undersized result nie je success
+ stale cache nie je povolená pre mutation
+ wrong-account source je odmietnutý
+ recyklovaná IP neprejde host identity gateom
+ full-fleet runtime inventory zodpovedá rollout subjectu
```

## 23. Kontrolné otázky

1. Prečo inventory nie je iba address book?
2. Aký rozdiel je medzi inventory source a resolved inventory?
3. Prečo `inventory_hostname` a `ansible_host` nie sú tá istá identity?
4. Ako môže správny pattern zasiahnuť nesprávny asset?
5. Čo dynamic inventory preukazuje a čo nie?
6. Ako groups ovplyvňujú scope a variables?
7. Prečo `--limit` nie je security boundary?
8. Ako sa validuje empty a undersized inventory?
9. Aké riziká vytvára stale cache?
10. Ako sa odhalia duplicate logical identities?
11. Prečo inventory variable precedence nemá nahrádzať ownership design?
12. Aké forbidden fixtures má target-resolution pipeline testovať?

## Glossary impact

Relevantné pojmy: Ansible inventory, inventory source, inventory plugin, resolved inventory, inventory_hostname, ansible_host, asset identity, group graph, pattern, limit, target manifest, inventory cache, constructed group, duplicate host identity, empty inventory a coverage.

## Primárne zdroje

- [How to build your inventory](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_inventory.html)
- [Patterns: targeting hosts and groups](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_patterns.html)
- [Using variables](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_variables.html)
- [Ansible inventory command](https://docs.ansible.com/projects/ansible/latest/cli/ansible-inventory.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Ansible architecture](ansible-architecture.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Modules, tasks, plays a playbooks →](modules-tasks-plays-playbooks.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
