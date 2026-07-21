# Ansible idempotencia

Idempotentný Ansible run pri opakovaní s rovnakými vstupmi a rovnakým požadovaným stavom nevykoná ďalšiu zmenu. Druhý run má typicky skončiť bez nečakaného `changed: true` a bez ďalších side effects.

Idempotencia nie je vlastnosť YAML syntaxe ani Ansible ako celku. Vzniká kombináciou:

- správneho module behavioru,
- stabilných vstupov,
- presného current-state detection,
- deterministických templates,
- správneho `changed` signal-u,
- bounded external side effects,
- explicitného ownershipu.

## 1. Formálny model

Pre automation operáciu `f` a stav `S`:

```text
f(f(S)) = f(S)
```

Prvý run môže stav zmeniť:

```text
current state ≠ desired state
→ change
```

Druhý run s rovnakými inputs:

```text
current state = desired state
→ no change
```

Tento model neznamená, že run musí mať rovnaký textový output. Dôležitý je výsledný stav a pravdivý change signal.

## 2. Idempotencia a convergence

Configuration management smeruje systém k desired state:

```text
observe current state
→ compare with desired state
→ apply required delta
→ verify
```

Idempotencia opisuje správanie opakovanej operácie. Convergence opisuje, či opakovanie vedie k požadovanému stabilnému stavu.

Operácia môže byť idempotentná, ale konvergovať k nesprávnemu desired state-u. Preto treba validovať aj správnosť deklarácie.

## 3. Module idempotencia

Declarative modules typicky načítajú current state a zmenia iba potrebný rozdiel:

```yaml
- name: Ensure package is installed
  ansible.builtin.package:
    name: nginx
    state: present
```

Druhý run má reportovať `changed: false`, pokiaľ package zostáva nainštalovaný.

Module môže mať caveats:

- remote API nevracia stabilný stav,
- provider normalizuje hodnoty,
- module spravuje iba časť objektu,
- defaulty sa menia podľa platformy,
- resource je immutable a replacement je jediná zmena,
- module má bug alebo neúplnú check-mode podporu.

Idempotenciu nikdy nepredpokladaj iba podľa názvu modulu.

## 4. Declarative state namiesto sequence

Preferuj state-oriented module:

```yaml
- name: Ensure service is enabled and running
  ansible.builtin.service:
    name: example
    enabled: true
    state: started
```

Namiesto:

```yaml
- name: Start service every run
  ansible.builtin.command: systemctl start example
```

Druhý variant nevyjadruje current-state detection a môže nesprávne reportovať change.

## 5. `command` a `shell`

`command` a `shell` sú často ne-idempotentné, pretože spustia príkaz bez znalosti desired state-u.

Rizikový príklad:

```yaml
- name: Append configuration
  ansible.builtin.shell: echo 'feature=true' >> /etc/example.conf
```

Každý run pridá ďalší riadok.

Lepšie:

```yaml
- name: Ensure configuration line exists
  ansible.builtin.lineinfile:
    path: /etc/example.conf
    regexp: '^feature='
    line: 'feature=true'
```

Najlepšie je použiť module, ktorý spravuje celý configuration contract, alebo deterministický template.

## 6. `creates` a `removes`

Niektoré command operations možno ohraničiť:

```yaml
- name: Initialize application database
  ansible.builtin.command: /opt/example/bin/init-database
  args:
    creates: /var/lib/example/.initialized
```

`creates` zabráni opakovaniu, ak file existuje.

Limity:

- marker nemusí dokazovať správny stav,
- external operation mohla zlyhať po vytvorení markeru,
- marker môže byť stale,
- command môže mať ďalšie inputs, ktoré sa zmenili.

Marker je zjednodušený state model, nie automaticky spoľahlivý dôkaz.

## 7. `changed_when`

Task, ktorý current state iba číta, má explicitne reportovať no change:

```yaml
- name: Read service state
  ansible.builtin.command: systemctl is-active example
  register: example_service_state
  changed_when: false
  failed_when: example_service_state.rc not in [0, 3]
```

Task vykonávajúci custom operation môže odvodiť change:

```yaml
- name: Reconcile custom configuration
  ansible.builtin.command: /opt/example/bin/reconcile --format json
  register: reconcile_result
  changed_when: (reconcile_result.stdout | from_json).changed | bool
```

`changed_when: false` na reálne mutujúcom tasku nie je idempotencia. Iba skrýva zmenu.

## 8. `failed_when`

Idempotentný workflow potrebuje správne rozlíšiť:

- success bez zmeny,
- success so zmenou,
- permanent failure,
- transient failure,
- acceptable absent state.

Príklad:

```yaml
failed_when: command_result.rc not in [0, 3]
changed_when: command_result.rc == 3
```

Exit-code contract musí byť dokumentovaný a testovaný.

## 9. Templates

Deterministický template pri rovnakých inputs vytvorí rovnaký obsah:

```yaml
- name: Render configuration
  ansible.builtin.template:
    src: example.conf.j2
    dest: /etc/example/example.conf
    owner: root
    group: example
    mode: "0640"
```

Časté zdroje ne-idempotencie:

- aktuálny timestamp,
- náhodná hodnota,
- nestabilné iteration order,
- mutable external lookup,
- environment-specific newline behavior,
- generator pridávajúci whitespace,
- dynamic secret version bez explicitného pinningu.

Nevkladaj do managed file-u čas každého runu:

```jinja2
# Generated at {{ ansible_date_time.iso8601 }}
```

Tým sa file mení pri každom run-e a handler sa stále notify-uje.

## 10. Canonical serialization

Pri generovaní YAML, JSON alebo INI configuration používaj stabilné:

- ordering,
- quoting,
- indentation,
- newline convention,
- omission/null semantics,
- numeric a boolean types.

Semanticky rovnaký, ale textovo inak serializovaný file môže spúšťať zbytočné zmeny a restarty.

## 11. File ownership a mode

Task je idempotentný iba vtedy, keď spravuje celý relevantný stav:

```yaml
- name: Manage application directory
  ansible.builtin.file:
    path: /etc/example
    state: directory
    owner: root
    group: example
    mode: "0750"
```

Ak task spravuje obsah, ale nie ownership alebo permissions, ďalší actor môže vytvárať opakovaný drift.

## 12. Lists a ordering

Nestabilný input list môže meniť generated content:

```yaml
example_backends:
  - api-b
  - api-a
```

Ak ordering nemá business význam, normalizuj ho:

```jinja2
{% for backend in example_backends | sort %}
server {{ backend }};
{% endfor %}
```

Ak ordering význam má, nepreusporadúvaj ho iba kvôli stabilite. Contract musí povedať, kto poradie vlastní.

## 13. Package state

### `present`

Garantuje, že package existuje, ale nie konkrétnu verziu.

### `latest`

Môže vykonať zmenu pri každom novom repository release. Je opakovateľné voči aktuálnemu repository state-u, ale nie reprodukovateľné v čase.

### Pinned version

```yaml
name: example-service-2.4.1
state: present
```

Zvyšuje reproducibility, ale potrebuje explicitný upgrade a repository availability model.

Idempotencia a reproducibility nie sú to isté.

## 14. Service restarty

Service restart je side effect. Nemá sa vykonať pri každom run-e.

Správny pattern:

```yaml
- name: Render configuration
  ansible.builtin.template:
    src: example.conf.j2
    dest: /etc/example/example.conf
  notify: Restart example service
```

Handler sa spustí iba pri `changed: true`.

Ak template mení timestamp pri každom run-e, handler architecture je správna, ale upstream change detection je chybná.

## 15. API operations

API môže podporovať:

- declarative update,
- upsert,
- create-only,
- patch,
- non-idempotent action.

Pred volaním zisti:

- stabilný object identifier,
- GET/read path,
- create/update semantics,
- idempotency token,
- conflict behavior,
- eventual consistency,
- retry safety.

`POST /send-email` nie je idempotentné iba preto, že Ansible task má rovnaké arguments.

## 16. Cloud a network modules

Remote control plane môže:

- normalizovať hodnoty,
- dopĺňať defaults,
- meniť poradie rules,
- poskytovať eventually consistent read,
- vracať computed metadata,
- obmedzovať update na replacement.

Idempotency test musí bežať proti reprezentatívnemu API, nie iba syntax checkeru.

## 17. Database migrations

Migration je typicky forward-only side effect, nie jednoduchý desired-state resource.

Bezpečný model:

```text
read schema version
→ determine pending migrations
→ apply each migration once
→ record version
→ verify
```

Nespúšťaj rovnaký ne-idempotentný SQL script pri každom playbook run-e bez migration ledgeru.

## 18. User a credential operations

Creating user môže byť idempotentné, ale generating password alebo key pri každom run-e nie.

Rizikový pattern:

```text
generate random password every run
→ update account
→ restart consumers
```

Správny lifecycle potrebuje:

- stable secret source,
- explicitnú rotation udalosť,
- version/epoch,
- consumer rollout,
- revocation starého credentialu.

## 19. Facts a mutable external data

Task behavior môže závisieť od:

- facts,
- inventory API,
- DNS,
- package repositories,
- secret manager version,
- current time,
- service discovery.

Rovnaký Git commit preto nemusí mať rovnaké inputs. Pri kritických rozhodnutiach zachovaj resolved input evidence.

## 20. Check mode

```bash
ansible-playbook site.yml --check --diff
```

Check mode je best-effort predikcia. Module môže:

- plne podporovať check mode,
- podporovať ho čiastočne,
- task preskočiť,
- vrátiť nepresný predicted change,
- nemať dostatok current-state dát.

Check mode nie je dôkaz idempotencie. Dôkaz vyžaduje reálny druhý converge run.

## 21. Idempotency test

Základný test:

```text
clean environment
→ first converge
→ assert desired state
→ second converge
→ expect zero unintended changes
→ assert desired state again
```

Príklad acceptance kritéria:

```text
first run: changed > 0 allowed
second run: changed = 0
failed = 0
unreachable = 0
```

Niektoré tasks môžu legitímne meniť telemetry, rotating token alebo cache. Tieto výnimky musia byť explicitné a nemajú zakrývať širší drift.

## 22. Idempotency a Molecule/test harness

Role test môže spustiť:

1. prepare,
2. converge,
3. verify,
4. idempotence converge,
5. verify,
6. cleanup.

Dôležité nie je konkrétne testovacie meno, ale izolovaný target a machine-readable second-run result.

## 23. Change budget

Namiesto absolútneho `changed = 0` môže workflow definovať explicitný allowlist:

```text
allowed recurring changes:
- refresh ephemeral access token
- rotate bounded temporary file

all other changes:
- fail test
```

Allowlist musí byť krátky, reviewovaný a časovo/architektonicky odôvodnený.

## 24. Idempotencia pri partial failure

Scenár:

```text
task A changes package
→ task B writes config
→ task C fails before handler
```

Nasledujúci run musí bezpečne pokračovať z partial state-u.

Navrhuj tasks tak, aby:

- current state určoval ďalší krok,
- side effects mali stabilné identity,
- temp artifacts mali cleanup,
- handler failure bol obnoviteľný,
- retries neopakovali unsafe operation.

## 25. Concurrency

Dva Ansible runs môžu porušiť idempotentný výsledok:

```text
run A reads old state
run B reads old state
run A writes
run B writes conflicting value
```

Potrebné môžu byť:

- deployment lock,
- automation-controller concurrency rule,
- resource-specific lock,
- serializácia citlivých jobs,
- API optimistic concurrency,
- idempotency token.

Idempotencia jedného runu nerieši multi-writer race.

## 26. Ownership conflict

Ak rovnaký file spravuje:

- Ansible,
- package post-install script,
- application self-configuration,
- človek cez SSH,
- iný automation system,

vzniká perpetual drift.

Riešenie je jasný authoritative owner, nie ďalší `changed_when: false`.

## 27. Observability

Sleduj:

- changed task count,
- second-run changes,
- hosts s opakovaným driftom,
- handlers spúšťané pri každom run-e,
- command/shell tasks bez `changed_when`,
- check-mode coverage,
- idempotency-test pass rate,
- top recurring changed resources,
- duration first vs. second converge.

`changed: 0` nie je cieľ samo osebe. Cieľ je pravdivý, stabilný desired state.

## 28. Anti-patterny

### `changed_when: false` na každom command tasku

Výsledky vyzerajú čisto, ale change evidence je falošná.

### Timestamp v každom template

Každý run mení file a spúšťa handler.

### `state: latest` bez upgrade policy

Environment sa mení podľa mutable repository obsahu.

### Append cez shell

Obsah sa pri každom run-e duplikuje.

### Random secret generation bez rotation triggeru

Credential sa stále mení.

### Fixed sleep namiesto state checku

Run je pomalý a stále nemusí čakať dosť dlho.

### Ignorovanie druhého converge runu

Nie je dôkaz, že role stabilizuje stav.

### Viac automation owners jedného file-u

Systémy si navzájom prepisujú desired state.

## 29. Troubleshooting

### Template sa mení pri každom run-e

Porovnaj diff a hľadaj timestamps, ordering, whitespace, newline, random values a mutable lookups.

### Package task stále reportuje change

Over package manager backend, desired state, package name/version, repository metadata a module bug/version.

### Command task vždy reportuje change

Použi state-aware module alebo odvoď pravdivé `changed_when` z machine-readable resultu.

### Handler sa stále spúšťa

Nájdi notifying task a over, prečo reportuje change. Handler deduplication nerieši chybný upstream signal.

### Druhý run mení permissions

Over competing actors, umask, ACLs, package scripts, parent directory behavior a exact mode/owner/group contract.

### API object sa stále aktualizuje

Porovnaj desired a normalized remote representation, ordering, defaults, computed fields a eventual consistency.

### Check mode hlási nulu, reálny run mení

Module má neúplný check-mode model alebo current-state query potrebuje runtime side effect.

## 30. Kontrolné otázky

1. Čo presne znamená idempotencia?
2. Aký je rozdiel medzi idempotenciou a convergence?
3. Prečo `changed_when: false` nemusí byť riešenie?
4. Ako `creates` a `removes` modelujú stav?
5. Prečo timestamp narúša template idempotenciu?
6. Aký je rozdiel medzi idempotenciou a reproducibility?
7. Ako otestovať role druhým converge runom?
8. Ako partial failure ovplyvňuje ďalší run?
9. Prečo idempotencia nerieši concurrency?
10. Ako ownership conflict vytvára perpetual drift?

## Glossary impact

Relevantné pojmy: Ansible idempotencia, convergence, idempotency test, second converge, recurring change, change budget, current-state detection, stable input, command guard, perpetual drift a multi-writer automation.

## Oficiálna dokumentácia

- [Validating tasks with check and diff mode](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html)
- [Error handling and changed conditions](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_error_handling.html)
- [Ansible Lint: no-changed-when](https://docs.ansible.com/projects/lint/rules/no-changed-when/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Vault](vault.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Terraform vs. Ansible →](terraform-vs-ansible.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
