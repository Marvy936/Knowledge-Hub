# Variables, facts a templates

Variables, facts a templates tvoria jeden host-specific configuration pipeline. Variable sources vyjadrujú intent a environment data, precedence vytvorí effective value set, facts doplnia runtime observations a template z týchto vstupov vytvorí konkrétny artifact, ktorý sa validuje, publikuje a načíta do procesu.

Hlavný model:

```text
declared variable contracts a sources
→ precedence a host scope
→ effective host value subject
→ fresh facts a external lookups
→ derived values
→ deterministic template render
→ parser validation a atomic publication
→ handler/runtime transition
→ loaded-artifact verification a provenance
```

Keď host dostane nesprávnu konfiguráciu, nestačí čítať template. Treba rekonštruovať celý effective input subject vrátane zdrojov, precedence, freshness a controller runtime.

## 1. Atlas scenár: host-specific service configuration

Atlas Payments renderuje `/etc/atlas/payments.yml` pre každý application host. Verejný role contract obsahuje:

```yaml
atlas_environment: production
atlas_listen_port: 8443
atlas_tls_enabled: true
atlas_database_endpoint: db.prod.internal:5432
atlas_release_version: v43
```

Host-specific runtime observations dopĺňajú:

```text
stable host ID
OS family a major version
primary address
available memory
installed runtime capability
```

Template následne vytvorí artifact:

```jinja2
# managed by Ansible
release: {{ atlas_release_version }}
environment: {{ atlas_environment }}
listen:
  address: {{ ansible_facts.default_ipv4.address }}
  port: {{ atlas_listen_port }}
tls:
  enabled: {{ atlas_tls_enabled | bool | to_json }}
database:
  endpoint: {{ atlas_database_endpoint }}
workers: {{ atlas_effective_workers }}
```

Task musí artifact validovať pred nahradením aktívneho súboru:

```yaml
- name: Render validated Atlas configuration
  ansible.builtin.template:
    src: payments.yml.j2
    dest: /etc/atlas/payments.yml
    owner: root
    group: atlas
    mode: "0640"
    validate: /usr/bin/atlas-payments validate --config %s
  notify: Atlas payments configuration changed
```

Correctness závisí od hodnôt aj ich provenance. Rovnaký text `8443` môže pochádzať z role defaultu, inventory, extra vars alebo stale cached fact-derived výpočtu; tieto zdroje nemajú rovnaký ownership ani audit význam.

## 2. Variable contract, source, scope a precedence

Variable je typed-by-convention dátový vstup. Ansible môže hodnotu načítať z role defaults, inventory, play vars, role parameters, `vars_files`, facts, registered results, `set_fact`, includes alebo extra vars.

Pre každú významnú hodnotu definuj:

```text
name a domain meaning
expected type a valid range
default alebo required status
allowed override sources
host/play/run scope
secret classification
owner a compatibility policy
```

Vyššia precedence znamená, že hodnota vyhrá. Neznamená, že zdroj je architektonicky správny.

Praktický contract:

```yaml
atlas_listen_port: 8443       # overridable role default
atlas_unit_name: atlas-payments.service  # internal constant
```

Role defaults sú vhodné pre podporované customization points. Role vars s vysokou precedence patria skôr interným constants; environment-specific hodnoty v nich môžu znemožniť callerovi vyjadriť správny intent.

## 3. Effective host value subject

Pred mutáciou treba vedieť, aké hodnoty konkrétny host reálne použije. Effective subject zahŕňa:

```text
run/source revision
inventory sources a host identity
group memberships
role a collection version
play/role parameters
facts a cache generation
registered a set_fact values
extra vars a controller-injected values
lookup/plugin version a external query identity
```

Ansible neposkytuje jeden univerzálny bezpečný príkaz, ktorý vysvetlí provenance každého value bez rizika secret leakage. Kombinuj:

- `ansible-inventory --host <host>` pre resolved inventory variables;
- `ansible-config dump --only-changed` pre effective engine configuration;
- explicitné redacted preflight assertions;
- controller job metadata;
- role contract a source review;
- task-level debug iba pre allowlisted non-secret fields.

## 4. Required values, defaults a validation

Required input má zlyhať pred side effects:

```yaml
- name: Validate Atlas inputs
  ansible.builtin.assert:
    that:
      - atlas_environment in ['dev', 'stage', 'production']
      - atlas_listen_port | int > 0
      - atlas_listen_port | int < 65536
      - atlas_tls_enabled | bool or atlas_environment != 'production'
      - atlas_database_endpoint is defined
      - atlas_database_endpoint | length > 0
    fail_msg: Atlas configuration contract is invalid
```

`default()` je vhodný iba pre bezpečný a dokumentovaný fallback. Použitie defaultu na production database endpoint alebo TLS flag konvertuje missing intent na tichú konfiguráciu.

Dátový typ je súčasť contractu. Text `"false"` a boolean `false` nemusia mať rovnaké správanie pri každej expression. Critical inputs validuj a normalizuj raz, nie ad hoc v každom tasku.

## 5. Facts sú observations, nie desired state

Facts opisujú host v čase gather-u:

```yaml
ansible_facts.os_family
ansible_facts.distribution_major_version
ansible_facts.default_ipv4.address
ansible_facts.memtotal_mb
```

Sú vhodné na platform capability selection a host-specific render. Nie sú automaticky authoritative CMDB ani immutable identity proof.

Fact lifecycle:

```text
connection a module runtime
→ setup alebo custom fact read
→ host-scoped observation
→ optional cache write
→ later condition/render use
→ expiry alebo invalidation
```

Fact cache potrebuje backend, TTL, source/run identity, invalidation a maximum acceptable age. Host môže byť preinštalovaný, IP sa môže zmeniť a custom fact môže zostať na disku po starom deploymente.

## 6. Worked failure: stale fact cache vybral starý platform path

Host `app-09` bol aktualizovaný z OS major version 8 na 9. Fact cache má TTL 24 hodín a production run použije cached value `8`.

```text
host runtime je OS 9
→ stale fact tvrdí OS 8
→ condition načíta legacy task path
→ template používa deprecated directive
→ parser validation zlyhá až po package alebo file side effects
```

Fix nie je zvýšiť počet retries. Pre platform migration vyžaduj fresh gather alebo explicitný capability probe a viaž cache generation na run evidence.

## 7. Registered values a `set_fact`

Registered result je host-scoped observation z konkrétneho tasku:

```yaml
- name: Read Atlas runtime metadata
  ansible.builtin.command:
    argv: [/usr/bin/atlas-payments, runtime, --json]
  register: atlas_runtime_result
  changed_when: false
  failed_when: atlas_runtime_result.rc != 0
```

Jeho schema závisí od task outcome. Skipped alebo failed result nemusí mať rovnaké nested fields ako successful result.

`set_fact` vytvára derived host value počas runu:

```yaml
- name: Derive bounded worker count
  ansible.builtin.set_fact:
    atlas_effective_workers: "{{ [ansible_facts.memtotal_mb // 1024, 8] | min }}"
```

Používaj ho pre jasné derivácie, nie ako imperative mutable store. `cacheable` môže preniesť hodnotu do budúcich runs a zmeniť freshness aj precedence behavior; preto potrebuje explicitný lifecycle.

## 8. Cross-host data a stable service contracts

Prístup cez `hostvars` je možný, ale krehký:

```jinja2
{{ hostvars[groups['database'][0]].ansible_host }}
```

Tento expression predpokladá, že group existuje, ordering má význam, prvý host je správny endpoint a jeho values sú dostupné a fresh.

Pre shared service endpoint preferuj explicitný contract z inventory, service discovery alebo controlled lookup:

```yaml
atlas_database_endpoint: db.prod.internal:5432
```

Cross-host inference je execution dependency. Musí mať identity, availability a freshness semantics, nie iba fungovať v jednom inventory snapshot-e.

## 9. Template rendering a artifact identity

Jinja rendering typicky prebieha na control node-e v host-specific variable context-e. Výsledok preto závisí od:

- source template revision;
- execution environment, `ansible-core` a Jinja version;
- filter, test a lookup plugins;
- effective host values;
- external lookup results;
- locale/timezone alebo custom code podľa implementácie.

Configuration artifact subject má obsahovať aspoň:

```text
template source digest
execution environment digest
host stable identity
effective non-secret input manifest
fact/cache generation
lookup dependency identities
rendered artifact checksum
validation command/result
destination path a ownership
```

## 10. Deterministic rendering

Rovnaký subject má vytvoriť rovnaký artifact. Nondeterminism vzniká z timestampov, random hodnôt, unordered collections alebo volatile lookups.

Zlé:

```jinja2
generated_at: {{ now() }}
```

Každý run zmení checksum, template task reportuje `changed` a handler reštartuje službu aj bez functional change.

Pre structured configuration používaj serializačné filters:

```jinja2
{{ atlas_feature_map | to_nice_json }}
```

Ručné skladanie JSON/YAML cez string concatenation poškodzuje escaping a typy.

## 11. Validation, atomic publication a runtime load

Template success má viac fáz:

```text
render temporary artifact
→ validate parser/domain invariants
→ atomic replace, ak filesystem podporuje
→ report changed podľa content delta
→ notify handler
→ process reload/restart
→ verify loaded artifact checksum/version
```

`validate` musí byť side-effect free a reprezentatívny pre runtime parser. Atomic file replace chráni pred partial reads, ale nie pred semantic incompatibility, nesprávnym destination pathom ani procesom, ktorý config znovu nenačíta.

Fallback typu unsafe writes zvyšuje race a corruption risk a musí byť explicitne zdôvodnený podľa filesystem/runtime boundary.

## 12. Worked failure: extra vars ticho prepli production endpoint

Controller job template povoľuje operator-defined extra vars. Operátor pri rerun-e ponechá starú hodnotu:

```text
atlas_database_endpoint=db.stage.internal:5432
```

Extra vars majú vysokú precedence:

```text
inventory definuje production endpoint
→ controller injektuje stale extra var
→ effective value je staging endpoint
→ template a parser validation prejdú
→ production process sa pripojí do staging databázy
```

Syntax a parser correctness neoverujú environment identity. Production preflight musí porovnať endpoint s allowlisted environment/service identity a uchovať redacted effective input evidence.

## 13. Worked failure: timestamp vytvoril perpetual restart loop

Template zapisuje current timestamp. Pri každom scheduled convergence run-e:

```text
nový timestamp
→ nový artifact checksum
→ template reports changed
→ handler restartuje service
→ druhý run nie je no-change
```

Dôsledkom môže byť pravidelný availability drop, session loss a alert noise. Generated timestamp patrí do deployment evidence alebo runtime metadata, nie do desired configu, ak nemá functional význam.

## 14. Secrets v values a artifacts

`no_log: true` obmedzuje bežný task output, ale nie je secret lifecycle:

- secret stále existuje v controller memory;
- lookup alebo custom plugin ho môže leaknúť;
- rendered file ho môže obsahovať;
- validation command alebo process ho môže vypísať;
- diff, callback a downstream debug môžu secret odhaliť;
- cached fact alebo registered result môže predĺžiť exposure.

Secret načítaj čo najneskôr, používaj v najmenšom scope, neukladaj do fact cache a po exposure ho revoke/rotate. Dodatočné pridanie `no_log` neopraví kompromitovaný credential.

## 15. Causal troubleshooting walkthrough: jeden host používa nesprávny database endpoint

`app-07` po green run-e používa staging endpoint. Ostatné production hosts používajú správny endpoint.

### 1. Zafixuj artifact subject

Zaznamenaj host stable ID, run/source revision, role/collection a execution image, inventory sources, group membership, fact cache generation, template digest, destination checksum a loaded runtime version.

### 2. Súťažiace hypotézy

1. Host-specific alebo group variable prepísala production value.
2. Extra var alebo controller credential field bolo aplikované iba na recovery job.
3. Duplicate inventory definition zmenila host group membership.
4. Stale cached fact alebo `set_fact` zvolil nesprávnu derived branch.
5. `hostvars` vybral nestabilný prvý database host.
6. Lookup plugin čítal staging path alebo environment.
7. Správny artifact bol vyrenderovaný, ale proces načítava iný file path.
8. Artifact sa po Ansible run-e zmenil druhým writerom.

### 3. Diskriminačné observation points

- `ansible-inventory --host app-07` a group graph;
- controller job extra vars metadata bez secret values;
- redacted effective-value preflight;
- fact cache timestamp a raw fresh capability observation;
- lookup request identity a path;
- rendered artifact checksum/content allowlist comparison;
- process command line, open file/config endpoint a loaded version;
- host audit/file modification timeline.

### 4. Containment

Odstráň host z trafficu a zablokuj ďalší rollout s rovnakým value subjectom. Ak sa použili production credentials voči staging systému alebo opačne, začni identity a data-impact audit.

### 5. Recovery

- precedence/source error → odstráň nesprávny override a zúž allowed sources;
- stale fact → invaliduj cache a použi fresh observation;
- cross-host inference → nahraď explicitným service contractom;
- wrong lookup → oprav environment-scoped path/identity;
- wrong runtime path → zosúlaď destination a process config source;
- second writer → odstráň ownership konflikt a obnov artifact.

### 6. Over pôvodný outcome

Potvrď production endpoint cez process-level/runtime API na všetkých expected hosts, artifact checksum a fresh second run bez unintended changes.

### 7. Posuň control skôr

Pridaj effective-value manifest, environment identity assertion, cache-age gate, deterministic render regression test a loaded-config oracle.

## 16. Referenčné pravidlá

- Precedence určuje víťaza, nie správneho ownera.
- Critical value potrebuje type, scope, source a validation contract.
- Facts sú časovo ohraničené observations.
- Cached facts a `set_fact cacheable` menia lifecycle medzi runs.
- `hostvars` vytvára cross-host dependency.
- Jinja sa renderuje v controller runtime a používa executable plugins.
- Template output je deployovaný artifact s vlastnou identitou.
- Parser validation nenahrádza environment ani runtime verification.
- Deterministic template je predpoklad idempotencie.
- `no_log` nie je revocation, storage ani access-control mechanizmus.

## 17. Kontrolné otázky

1. Čo tvorí effective host value subject?
2. Prečo vysoká precedence neznamená správny ownership?
3. Kedy je `default()` bezpečný a kedy skrýva missing intent?
4. Prečo fact cache potrebuje generation a TTL?
5. Aké riziká má cached `set_fact`?
6. Prečo je výber `groups['database'][0]` krehký?
7. Ktoré identity určujú template artifact?
8. Ako timestamp v configu porušuje convergence?
9. Čo validation a atomic replace dokážu a čo nie?
10. Ako dokážeš, že proces načítal správny vyrenderovaný artifact?

## Glossary impact

Relevantné pojmy: effective host value subject, variable ownership contract, variable provenance, fact observation, fact cache generation, derived host value, cross-host value dependency, template artifact subject, deterministic rendering, parser validation, atomic configuration publication, loaded-artifact verification a secret-bearing render path.

## Oficiálna dokumentácia

- [Using variables](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_variables.html)
- [Discovering variables: facts and magic variables](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_vars_facts.html)
- [Templating with Jinja2](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_templating.html)
- [Controlling how Ansible behaves: precedence rules](https://docs.ansible.com/projects/ansible/latest/reference_appendices/general_precedence.html)
- [`ansible.builtin.template`](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/template_module.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Modules, tasks, plays a playbooks](modules-tasks-plays-playbooks.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Handlers, loops a conditionals →](handlers-loops-conditionals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->