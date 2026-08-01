# Variables, facts a templates

Variables, facts a templates tvoria jeden host-specific artifact-generation pipeline. Variable sources vyjadrujú intent a environment data, precedence z nich vyberie effective values, facts pridajú časovo ohraničené runtime observations a Jinja template vytvorí konkrétny configuration artifact. Template syntax môže byť úplne správna a napriek tomu vytvoriť nebezpečný výsledok, ak vyššia-precedence extra var prepíše production endpoint, stale fact vyberie starý OS path alebo nondeterministic timestamp spôsobí restart pri každom run-e.

Kapitola pokračuje incidentom `IAC-PAY-78`. Atlas Payments renderuje `/etc/atlas/payments.yml` pre každý application host. Host `app-07` dostane staging database endpoint z recovery-job extra vars, `app-09` použije stale cached OS fact a ďalšie hosts sa reštartujú pri každom convergence run-e, pretože template obsahuje `generated_at`. Root cause nie je v jednom Jinja riadku; je v neauditovateľnom effective input subjecte a nedeterministickom artifact lifecycle.

## 1. Dominantný intent-to-loaded-artifact lifecycle

Nasledujúci model opisuje prechody jedného Ansible run, host alebo item subject, nie iba poradie krokov. Failure môže nastať v ktoromkoľvek bode reťazca resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome a zanechať partial alebo unknown outcome. Každý transition preto potrebuje vlastný read-back a closure tvorí complete per-host coverage, pravdivý result a runtime/business read-back.


```text
declared variable contracts a allowed sources
→ precedence a per-host flattening
→ effective non-secret value manifest
→ fresh facts a external lookup identities
→ derived values
→ deterministic template render
→ parser/domain validation
→ atomic publication
→ handler reload/restart
→ loaded artifact a runtime verification
→ second-run checksum/convergence closure
```

Ansible variable precedence určí, ktorá definition vyhrá. Neurčí, či zdroj je architektonicky správny. Oficiálna dokumentácia odporúča definovať value na jednom zrozumiteľnom mieste namiesto spoliehania sa na komplikovanú precedence. citeturn329472search2turn329472search6

## 2. Exact host configuration subject

Táto podsekcia definuje presný Ansible run, host alebo item subject. Názov alebo locator nestačí: subject musí niesť generation, authority a target identity potrebné na koreláciu reťazca resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome. Až complete per-host coverage, pravdivý result a runtime/business read-back ukáže, že ďalší command alebo YAML patrí správnemu objektu.


```yaml
hostConfigurationSubject:
  host:
    inventoryHostname: app-07
    immutableAssetId: i-0app07
    environment: prod-eu
  run:
    sourceRevision: 42ad9c1
    role: atlas.payments.runtime@2.7.0
    executionEnvironmentDigest: sha256:71ca...
  variables:
    inventoryDigest: sha256:40d9...
    playParametersDigest: sha256:90ab...
    extraVarsPresent: false
  facts:
    gatheredAt: 2026-07-31T08:05:00Z
    cacheUsed: false
  template:
    sourceDigest: sha256:21ab...
    renderedDigest: sha256:77ef...
    destination: /etc/atlas/payments.yml
  runtime:
    expectedConfigVersion: payments-v43
```

Manifest nesmie obsahovať secret values. Má obsahovať identity, source classes, allowed non-secret values alebo fingerprints, aby sa artifact dal reprodukovať a auditovať.

## 3. Variable contract

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


Pre každú významnú variable definuj:

```text
name a domain meaning
expected type a valid range
required/default/null behavior
allowed source layer
host/play/role scope
secret classification
owner a compatibility policy
effect na target, privilege alebo artifact identity
```

Príklad role defaults:

```yaml
# roles/runtime/defaults/main.yml
atlas_listen_port: 8443
atlas_tls_enabled: true
atlas_worker_limit: 8
```

Environment-specific endpoint nemá mať univerzálny fallback:

```yaml
# required from environment inventory or role parameter
atlas_database_endpoint: null
```

## 4. Precedence ako execution mechanism

Values môžu pochádzať z role defaults, inventory/group/host vars, play vars, role parameters, `vars_files`, facts, registered results, `set_fact` a extra vars. Ansible načíta definitions a podľa precedence vyberie effective value. Extra vars majú veľmi vysokú precedence a môžu prepísať environment contract. citeturn329472search2

Precedence nie je bezpečnostný model. Ak produkčný endpoint existuje v piatich layers, úspešné resolution neznamená jasné ownership.

Pravidlo:

```text
one critical value
→ one authoritative source class
→ explicit allowed overrides
→ resolved-value assertion
```

## 5. Preflight validation pred side effects

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


```yaml
- name: Validate Atlas configuration contract
  ansible.builtin.assert:
    that:
      - atlas_environment == 'prod-eu'
      - atlas_listen_port | int > 0
      - atlas_listen_port | int < 65536
      - atlas_tls_enabled | bool
      - atlas_database_endpoint is defined
      - atlas_database_endpoint is match('^db\.prod\.internal:[0-9]+$')
      - atlas_release_version is match('^payments-v[0-9]+$')
    fail_msg: Effective Atlas configuration is invalid for production
```

`assert` preukazuje, že current effective values spĺňajú expressions v tomto task context-e. Nepreukazuje, že endpoint existuje, je správna database identity alebo že secret/access policy funguje.

## 6. Redacted effective-value manifest

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


```yaml
- name: Build non-secret effective-value manifest
  ansible.builtin.set_fact:
    atlas_effective_manifest:
      environment: "{{ atlas_environment }}"
      listen_port: "{{ atlas_listen_port | int }}"
      tls_enabled: "{{ atlas_tls_enabled | bool }}"
      database_endpoint: "{{ atlas_database_endpoint }}"
      release_version: "{{ atlas_release_version }}"
      host_id: "{{ atlas_instance_id }}"

- name: Persist manifest for audit
  ansible.builtin.copy:
    content: "{{ atlas_effective_manifest | to_nice_json }}"
    dest: /var/lib/atlas/config-subject.json
    owner: root
    group: atlas
    mode: '0640'
```

Manifest preukazuje effective allowlisted values použité týmto flowom. Nezobrazuje provenance automaticky; source ownership sa kombinuje s inventory/job metadata. Secret values ani tokens sa do manifestu nedávajú.

## 7. Facts ako observations

Facts opisujú host v čase gathering-u:

```yaml
ansible_facts.os_family
ansible_facts.distribution_major_version
ansible_facts.default_ipv4.address
ansible_facts.memtotal_mb
```

Oficiálna dokumentácia rozlišuje facts a magic variables; `inventory_hostname` je inventory identity, zatiaľ čo `ansible_hostname` môže pochádzať z gathered facts. `ansible_play_batch` označuje current batch podľa `serial`. citeturn329472search4

Fact nie je desired state ani immutable asset identity. Má observation time, collection method a freshness.

## 8. Fact cache a freshness contract

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


```yaml
factCacheSubject:
  backend: redis-ansible-facts
  generatedAt: 2026-07-31T07:50:00Z
  ttlSeconds: 900
  hostAssetId: i-0app09
  gatheringSubset: [min, network]
```

Stale facts môžu vybrať nesprávny OS template, interpreter alebo network address. Production migration môže vyžadovať fresh gather:

```bash
ansible payments_app \
  -i inventories/prod \
  -m ansible.builtin.setup \
  -a 'gather_subset=min,network' \
  --tree /secure/evidence/facts
```

Výstup preukazuje gathered module observations pre reachable hosts. Nepreukazuje business health ani nemennosť po gather-e.

## 9. Worked failure: stale OS fact

Host bol upgradovaný z OS 8 na 9, ale cache stále vracia `distribution_major_version=8`.

```text
stale observation
→ legacy include/template path
→ deprecated directive
→ package/file side effects prebehnú
→ validation zlyhá neskoro
```

Recovery invaliduje cache, gather-ne fresh facts, overí package/file partial state a vykoná správny platform-specific recovery. Skorší gate porovná fact age a immutable host image/build identity.

## 10. Registered values

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


```yaml
- name: Read current runtime metadata
  ansible.builtin.command:
    argv: [/usr/bin/atlas-payments, runtime, --json]
  register: atlas_runtime_result
  changed_when: false
  failed_when: atlas_runtime_result.rc != 0

- name: Parse runtime metadata
  ansible.builtin.set_fact:
    atlas_runtime: "{{ atlas_runtime_result.stdout | from_json }}"
```

Registered result schema sa líši pri success, skip a failure. Condition nesmie slepo čítať nested field bez testu `is defined`.

## 11. `set_fact` a derived values

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


```yaml
- name: Derive bounded worker count
  ansible.builtin.set_fact:
    atlas_effective_workers: >-
      {{ [([ansible_facts.memtotal_mb | int // 1024, atlas_worker_limit | int] | min), 1] | max }}
```

`set_fact` je vhodný pre zrozumiteľnú deriváciu. Nie je vhodný ako neprehľadný mutable store medzi roles. `cacheable: true` prenáša value do ďalších runs a mení lifecycle/freshness; používa sa iba s explicitnou cache policy.

## 12. Cross-host values a `hostvars`

Krehký pattern:

```jinja2
{{ hostvars[groups['database'][0]].ansible_host }}
```

Predpokladá existenciu group, význam orderingu, správnosť first hostu a dostupnosť/freshness jeho vars.

Preferuj explicitný service contract:

```yaml
atlas_database_endpoint: db.prod.internal:5432
```

alebo controlled service-discovery lookup s identity, version a failure semantics.

## 13. Deterministic template rendering

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


```jinja2
# managed by Ansible
release: {{ atlas_release_version | to_json }}
environment: {{ atlas_environment | to_json }}
listen:
  address: {{ ansible_facts.default_ipv4.address | to_json }}
  port: {{ atlas_listen_port | int }}
tls:
  enabled: {{ atlas_tls_enabled | bool | to_json }}
database:
  endpoint: {{ atlas_database_endpoint | to_json }}
workers: {{ atlas_effective_workers | int }}
features:
{{ atlas_features | dictsort | items2dict | to_nice_yaml(indent=2) | indent(2, true) }}
```

Render závisí od template source, Jinja/filters, values, facts a lookups. Collections alebo custom filters sú executable dependencies.

Nedeterministické values ako `now()`, random alebo unordered serialization spôsobujú perpetual `changed` a handler churn.

## 14. Template task a validation

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


```yaml
- name: Render validated Atlas configuration
  ansible.builtin.template:
    src: payments.yml.j2
    dest: /etc/atlas/payments.yml
    owner: root
    group: atlas
    mode: '0640'
    backup: true
    validate: /usr/bin/atlas-payments validate --config %s
  register: atlas_template
  notify: Restart Atlas Payments
```

Lifecycle:

```text
render temporary file
→ validation command
→ atomic destination replace, ak podporované
→ content-delta changed result
→ handler notification
```

Validation preukazuje parser/domain checks implementované command-om. Nepreukazuje loaded process state ani downstream connectivity.

## 15. Rendered artifact checksum

Táto podsekcia vysvetľuje konkrétnu časť Ansible run, host alebo item subject. Source deklarácia sa nesmie zameniť za effective reťazec resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; treba pomenovať aj partial a unknown outcomes. Výsledok sa prijíma až po complete per-host coverage, pravdivý result a runtime/business read-back.


```yaml
- name: Read rendered configuration checksum
  ansible.builtin.stat:
    path: /etc/atlas/payments.yml
    checksum_algorithm: sha256
  register: atlas_config_stat

- name: Record checksum
  ansible.builtin.debug:
    msg:
      host: "{{ inventory_hostname }}"
      config_sha256: "{{ atlas_config_stat.stat.checksum }}"
```

Checksum preukazuje bytes na destination path v čase stat tasku. Nepreukazuje, že process ich načítal. Runtime endpoint má publikovať loaded config version/checksum.

## 16. Worked failure: stale extra var smeruje do staging DB

Recovery job template ponechal `atlas_database_endpoint: db.stage.internal:5432` ako extra var. Extra var mala vyššiu precedence než production inventory, template bola syntakticky validná a process sa úspešne pripojil do staging databázy. Parser ani service health preto chybu neodhalili.

Containment odoberie affected hosts z trafficu a zachová job metadata, variable provenance, rendered files, process environment/command line a database audit. Security/data owner posúdi cross-environment access skôr, než sa logs alebo sessions odstránia.

Autoritatívna oprava odstráni stale override, definuje allowed source policy pre endpoint a pridá assertion `database_environment == prod-eu`. Host sa re-renderuje, handler reloadne process a runtime endpoint aj DB identity probe potvrdia production target. Forbidden fixture so staging extra-varom musí zlyhať pred file mutation.

Recovery job template ponechal:

```yaml
atlas_database_endpoint: db.stage.internal:5432
```

ako extra var.

```text
inventory production endpoint
→ extra var má vyššiu precedence
→ template validný
→ process sa pripojí do staging database
```


Recovery postupuje cez odobrať hosts z trafficu, zachovať job extra-var metadata a rendered files, auditovať cross-environment data access, odstrániť stale override, pridať production endpoint assertion a allowed source policy a re-render/restart/verify.

Poradie chráni evidence a zabraňuje tomu, aby ďalšia mutation prekryla partial alebo unknown outcome.


## 17. Worked failure: timestamp spôsobí restart loop

Incident sa rekonštruuje ako causal chain nad jedným Ansible run, host alebo item subject. Observations určujú prvý divergentný bod v reťazci resolved inventory a variables cez task/module result, handler a loaded process až po serving outcome; samy osebe nie sú success alebo failure verdictom. Recovery sa vyberá až po zachovaní evidence a uzatvára ju complete per-host coverage, pravdivý result a runtime/business read-back.


```jinja2
generated_at: {{ now(utc=true).isoformat() }}
```

```text
každý run nové bytes
→ template changed
→ handler restart
→ second run nikdy nekonverguje
```

Timestamp patrí do evidence manifestu alebo commentu, ktorý nie je súčasť functional artifactu, ak nemá runtime význam.

## 18. Secrets v variable/template lifecycle

`no_log: true` obmedzuje task output. Nešifruje controller memory, rendered file, fact cache ani validation logs.

```yaml
- name: Render credential file
  ansible.builtin.template:
    src: credentials.j2
    dest: /etc/atlas/credentials
    owner: root
    group: atlas
    mode: '0600'
  no_log: true
```

Secret lifecycle potrebuje short-lived acquisition, minimum scope, file permissions, diff suppression, process reload, revocation a audit. Exposed credential sa rotuje u authority; pridanie `no_log` spätne exposure neodstráni.

## 19. Loaded artifact verification

Uložený artifact a loaded runtime sú dve odlišné generations. Notification iba zaradí handler; až handler result, process start/version a endpoint dokazujú, že nová konfigurácia bola načítaná. Host sa považuje za converged až po complete per-host coverage, pravdivý result a runtime/business read-back.


```yaml
- name: Query loaded runtime configuration
  ansible.builtin.uri:
    url: https://127.0.0.1:8443/runtime
    validate_certs: true
    return_content: true
  register: atlas_runtime_status
  changed_when: false
  failed_when:
    - atlas_runtime_status.status != 200
    - atlas_runtime_status.json.config_version != atlas_release_version
    - atlas_runtime_status.json.database_environment != 'prod-eu'
```

Preukazuje local process response a allowlisted runtime fields. Nepreukazuje load-balancer route, full business transaction ani every host unless run coverage je complete.

## 20. Competing hypotheses pri wrong endpoint na jednom hoste

H1/H3 porovnávajú inventory host/group provenance a duplicate membership. H2 číta controller job metadata a explicitné extra vars. H4 overuje fact timestamp a branch, ktorá z factu odvodila endpoint.

H5/H6 auditujú `hostvars` selection a lookup path/credential, pretože controller mohol načítať správny key z nesprávneho environment store-u. H7 porovná destination file s process command line a loaded runtime fields. H8 používa filesystem audit timeline na odhalenie druhého writera po run-e.

Každý dôkaz je host-scoped a časovo korelovaný. Až po potvrdení source-u sa opravuje precedence, cache, lookup alebo writer ownership; jednoduché re-renderovanie môže nesprávnu hodnotu iba zopakovať.

```text
H1: host/group variable override
H2: stale extra var
H3: duplicate inventory identity/group membership
H4: stale fact/derived branch
H5: unstable hostvars selection
H6: lookup čítal wrong environment path
H7: process číta iný destination
H8: second writer zmenil file po run-e
```


Discriminating evidence porovnáva inventory host/group output H1/H3, controller job metadata H2, fact timestamps H4, lookup audit H5/H6, file checksum/process command line/runtime endpoint H7 a filesystem audit timeline H8.

Každá observation musí potvrdiť alebo oslabiť konkrétnu hypotézu nad rovnakou identity a časovou osou.


## 21. Recovery a acceptance

Host zostáva mimo trafficu, kým sa nezachová a nevyhodnotí run/value/fact/template evidence a neurčí prvý nesprávny source alebo stale observation. Oprava mení autoritatívnu value, cache alebo lookup contract, potom vykoná deterministic render, parser validation a handler transition.

Loaded config endpoint musí potvrdiť release aj environment a fleet manifest musí ukázať complete coverage. Second no-change run dokazuje stabilitu template inputs a absenciu second writera. Acceptance zároveň vyžaduje, aby extra-var wrong endpoint a timestamp fixture skončili failureom alebo no-op podľa explicitného contractu.

```text
host removed from traffic
→ preserve run/value/fact/template evidence
→ identify wrong source or stale observation
→ correct authoritative value/cache/lookup
→ deterministic render + validate
→ handler reload/restart
→ loaded config verification
→ fleet manifest verification
→ second no-change run
```

Acceptance:

```text
critical values majú one-source contract
+ facts sú fresh pre risk class
+ rendered checksums sú deterministic
+ parser validation prešla
+ process načítal expected version/environment
+ extra-var wrong endpoint je odmietnutý
+ timestamp fixture nevytvára perpetual change
+ secret nie je v diff/log/cache
+ second run reports no unintended change
```

## 22. Kontrolné otázky

1. Prečo precedence neurčuje správneho ownera?
2. Čo musí obsahovať host configuration subject?
3. Aký rozdiel je medzi variable a fact?
4. Prečo fact cache potrebuje freshness policy?
5. Kedy je `set_fact cacheable` rizikový?
6. Prečo `hostvars[groups[x][0]]` vytvára skrytý contract?
7. Čo template validation preukazuje a čo nie?
8. Prečo checksum nepreukazuje loaded runtime state?
9. Ako môže extra var prekonať production inventory?
10. Prečo nondeterministic template ničí idempotency signal?
11. Čo `no_log` chráni a čo nechráni?
12. Ako sa overí forbidden wrong-environment value path?

## Glossary impact

Relevantné pojmy: Ansible variable, variable precedence, effective host context, fact, fact cache, registered result, set_fact, magic variable, hostvars, deterministic template, rendered artifact, validate, atomic publication, checksum, loaded configuration a value provenance.

## Primárne zdroje

- [Using variables](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_variables.html)
- [Facts and magic variables](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_vars_facts.html)
- [Template module](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/template_module.html)
- [Precedence rules](https://docs.ansible.com/projects/ansible/latest/reference_appendices/general_precedence.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Modules, tasks, plays a playbooks](modules-tasks-plays-playbooks.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Handlers, loops a conditionals →](handlers-loops-conditionals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
