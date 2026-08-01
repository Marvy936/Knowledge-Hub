# Praktický Ansible projekt od inventory po overený rolling configuration rollout

Táto kapitola materializuje Ansible pojmy do jedného súvislého projektu. Nakonfigurujeme službu `payments-api` na štyroch produkčných VM v dvoch availability zones. Playbook bude meniť versionovaný YAML configuration file, pred výmenou hosta z trafficu ho odstaví z load balancera, po zmene reštartuje systemd service, overí lokálny runtime stav a host vráti do trafficu.

Nejde iba o ukážku syntaxe. Budeme sledovať celý lifecycle:

```text
versionovaný Ansible content
→ pinned execution environment
→ inventory sources a immutable asset identities
→ expected-vs-resolved target manifest
→ effective per-host variables
→ check/diff prediction
→ rolling batch
→ atomic template validation
→ handler a process reload
→ local runtime verification
→ load-balancer rejoin
→ fleet a business verification
→ second no-change run
→ recovery a evidence closure
```

Ansible nie je jedna transakcia nad fleetom. Každý host môže skončiť v inom stave. Úspešný process exit code preto nestačí. Musíme vedieť, ktoré hosty sme očakávali, ktoré inventory resolve-nul, ktoré sa pokúsil meniť, ktoré sa zmenili, ktoré reštartovali službu a ktoré sú po rune skutočne zdravé a v trafficu.

## 1. Výsledná štruktúra projektu

Vytvor adresáre:

```bash
mkdir -p atlas-ansible/inventories/prod/group_vars
mkdir -p atlas-ansible/inventories/prod/manifests
mkdir -p atlas-ansible/playbooks
mkdir -p atlas-ansible/roles/payments_runtime/{defaults,tasks,handlers,templates}
cd atlas-ansible
```

Výsledná štruktúra:

```text
atlas-ansible/
├── ansible.cfg
├── requirements.yml
├── inventories/
│   └── prod/
│       ├── hosts.yml
│       ├── group_vars/
│       │   ├── all.yml
│       │   └── payments_app.yml
│       └── manifests/
│           └── expected-assets.json
├── playbooks/
│   └── payments.yml
└── roles/
    └── payments_runtime/
        ├── defaults/
        │   └── main.yml
        ├── tasks/
        │   └── main.yml
        ├── handlers/
        │   └── main.yml
        └── templates/
            └── payments.yml.j2
```

Repository source nie je run subject. Exact run pridáva `ansible-core` a collection versions, execution image digest, inventory snapshot, cache age, pattern, `--limit`, credentials, `ansible.cfg`, extra vars a target runtime state.

## 2. `requirements.yml`: reusable content contract

Walkthrough používa najmä `ansible.builtin`, ale collection manifest aj tak pinne explicitne:

```yaml
collections:
  - name: ansible.posix
    version: 1.6.2
```

Nainštaluj dependencies:

```bash
ansible-galaxy collection install \
  --requirements-file requirements.yml \
  --collections-path .ansible/collections
```

Výstup preukazuje, že controller nainštaloval požadovaný collection artifact do zvoleného pathu. Nepreukazuje dôveryhodný pôvod artifactu, jeho nemennosť v cache ani to, že `ANSIBLE_COLLECTIONS_PATH` pri produkčnom rune ukazuje na tento adresár.

V produkcii je vhodnejší immutable execution-environment image obsahujúci presne schválené `ansible-core`, Python dependencies, collections a helper binaries.

## 3. `ansible.cfg`: controller execution policy

Vytvor `ansible.cfg`:

```ini
[defaults]
inventory = inventories/prod/hosts.yml
roles_path = roles
collections_path = .ansible/collections
host_key_checking = True
retry_files_enabled = False
forks = 8
timeout = 15
interpreter_python = auto_silent
stdout_callback = default
bin_ansible_callbacks = True

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
```

Tento file mení runtime behavior. Preto jeho digest patrí do run subjectu:

```bash
sha256sum ansible.cfg
ansible-config dump --only-changed
```

`host_key_checking = True` chráni target identity pri SSH handshake. Ak ho vypneš, platný credential môže vykonať mutation na nesprávnom hoste pri DNS/IP hijacku alebo recyklovanej adrese.

Globálne `become = True` je v walkthrough zjednodušenie. V citlivejšom projekte používaj privilege escalation iba pri tasks alebo blocks, ktoré ju skutočne potrebujú.

## 4. Static inventory s logical a immutable identitou

`inventories/prod/hosts.yml`:

```yaml
all:
  children:
    production:
      children:
        payments_app:
          hosts:
            payments-a-01:
              ansible_host: 10.40.10.21
              asset_id: i-0a111111111111111
              availability_zone: eu-central-1a
            payments-a-02:
              ansible_host: 10.40.10.22
              asset_id: i-0a222222222222222
              availability_zone: eu-central-1a
            payments-b-01:
              ansible_host: 10.40.20.21
              asset_id: i-0b111111111111111
              availability_zone: eu-central-1b
            payments-b-02:
              ansible_host: 10.40.20.22
              asset_id: i-0b222222222222222
              availability_zone: eu-central-1b
```

Rozlišuj:

```text
inventory_hostname = payments-a-01
ansible_host        = 10.40.10.21
asset_id            = i-0a111111111111111
```

`inventory_hostname` je logický Ansible key. `ansible_host` je connection endpoint. `asset_id` je immutable cloud identity, ktorú budeme porovnávať s očakávaným fleet manifestom.

Static inventory je pre walkthrough čitateľný. V reálnej autoscaling infraštruktúre môže dynamic inventory načítať instances z AWS API. Aj vtedy musíš zachovať source account/region, plugin version, filters, cache generation a immutable instance IDs.

## 5. Expected asset manifest

`inventories/prod/manifests/expected-assets.json`:

```json
[
  {
    "inventory_hostname": "payments-a-01",
    "asset_id": "i-0a111111111111111",
    "availability_zone": "eu-central-1a"
  },
  {
    "inventory_hostname": "payments-a-02",
    "asset_id": "i-0a222222222222222",
    "availability_zone": "eu-central-1a"
  },
  {
    "inventory_hostname": "payments-b-01",
    "asset_id": "i-0b111111111111111",
    "availability_zone": "eu-central-1b"
  },
  {
    "inventory_hostname": "payments-b-02",
    "asset_id": "i-0b222222222222222",
    "availability_zone": "eu-central-1b"
  }
]
```

Tento manifest má pochádzať z autoritatívneho provisioning alebo asset systému, nie ručne kopírovať ten istý inventory source. Inak porovnávame source s jeho vlastnou kópiou a nedostávame nezávislý coverage dôkaz.

## 6. `group_vars/all.yml`: connection a global metadata

```yaml
ansible_user: automation

atlas_environment: production
atlas_owner: payments-platform
atlas_runbook: PAY-CONFIG-17

load_balancer_api: https://lb-admin.example.com/api/v1
load_balancer_pool: payments-production
```

Sem patria hodnoty spoločné pre celý inventory scope. Secret pre load-balancer API sem nepatrí v plaintext forme. Controller ho má získať cez short-lived workload identity alebo external secret provider a sprístupniť iba konkrétnym delegated tasks.

## 7. `group_vars/payments_app.yml`: service configuration

```yaml
payments_service_name: payments-api
payments_config_path: /etc/atlas-payments/payments.yml
payments_config_owner: root
payments_config_group: payments
payments_config_mode: "0640"

payments_port: 8080
payments_log_level: info
payments_config_generation: cfg-2026-07-31-01

payments_database:
  endpoint: payments-db.internal.example.com
  port: 5432
  name: payments
  tls_mode: verify-full

payments_feature_flags:
  async_settlement: true
  legacy_authorizer: false

expected_payments_host_count: 4
```

`payments_config_generation` je explicitná logical generation. Aplikácia ju vráti na `/version`, aby sme neoverovali iba file checksum, ale aj process-loaded state.

Database password nie je súčasťou tejto hodnoty. Konfigurácia môže odkazovať na file alebo runtime credential path spravovaný samostatným secret lifecycle-om.

## 8. Role defaults

`roles/payments_runtime/defaults/main.yml`:

```yaml
payments_health_scheme: http
payments_health_host: 127.0.0.1
payments_health_path: /readyz
payments_version_path: /version
payments_health_retries: 12
payments_health_delay: 5

payments_binary: /usr/local/bin/payments-api
payments_config_validator: >-
  /usr/local/bin/payments-api
  check-config
  --config %s
```

Defaults sú overridable public role inputs. Environment-specific values patria do inventory variables. Kritické production invariants však nemajú závisieť iba od slabého defaultu; role ich má overiť cez `assert`.

## 9. Jinja template

`roles/payments_runtime/templates/payments.yml.j2`:

```jinja2
# Managed by Ansible. Manual edits will be overwritten.
service:
  name: {{ payments_service_name | to_json }}
  environment: {{ atlas_environment | to_json }}
  config_generation: {{ payments_config_generation | to_json }}

server:
  listen_address: "0.0.0.0"
  port: {{ payments_port }}

logging:
  level: {{ payments_log_level | to_json }}

database:
  endpoint: {{ payments_database.endpoint | to_json }}
  port: {{ payments_database.port }}
  name: {{ payments_database.name | to_json }}
  tls_mode: {{ payments_database.tls_mode | to_json }}
  credential_file: "/run/secrets/payments-db"

feature_flags:
{% for flag_name, enabled in payments_feature_flags | dictsort %}
  {{ flag_name }}: {{ enabled | bool | lower }}
{% endfor %}
```

`dictsort` stabilizuje ordering feature flags. `to_json` bezpečne quote-ne strings podľa JSON syntaxe, ktorá je validná aj v YAML scalar context-e.

Explicitné boolean `false` sa renderuje ako `false`, nie ako empty value. Template output je configuration artifact. Stále nepreukazuje, že proces ho načítal.

## 10. Handler

`roles/payments_runtime/handlers/main.yml`:

```yaml
- name: Restart payments service
  ansible.builtin.systemd_service:
    name: "{{ payments_service_name }}"
    state: restarted
    daemon_reload: true
  listen: Restart payments service
```

Handler sa notifikuje iba pri `changed` result-e template tasku. Ak template validation zlyhá, destination file sa nemá nahradiť a handler sa nemá vykonať.

Handler success preukazuje systemd operation result. Nepreukazuje, že process načítal správnu generation alebo je dostupný cez load balancer.

## 11. Role tasks: complete rolling host transition

`roles/payments_runtime/tasks/main.yml`:

```yaml
- name: Validate required payments variables
  ansible.builtin.assert:
    that:
      - payments_service_name | length > 0
      - payments_config_generation | length > 0
      - payments_port | int > 0
      - payments_port | int < 65536
      - payments_database.endpoint | length > 0
      - payments_database.tls_mode in ['require', 'verify-ca', 'verify-full']
    fail_msg: "Payments configuration contract is incomplete."

- name: Verify expected binary exists
  ansible.builtin.stat:
    path: "{{ payments_binary }}"
  register: payments_binary_stat

- name: Reject host without the expected binary
  ansible.builtin.assert:
    that:
      - payments_binary_stat.stat.exists
      - payments_binary_stat.stat.executable
    fail_msg: "{{ payments_binary }} is missing or not executable."

- name: Ensure configuration directory exists
  ansible.builtin.file:
    path: "{{ payments_config_path | dirname }}"
    state: directory
    owner: "{{ payments_config_owner }}"
    group: "{{ payments_config_group }}"
    mode: "0750"

- name: Render and validate payments configuration atomically
  ansible.builtin.template:
    src: payments.yml.j2
    dest: "{{ payments_config_path }}"
    owner: "{{ payments_config_owner }}"
    group: "{{ payments_config_group }}"
    mode: "{{ payments_config_mode }}"
    backup: true
    validate: "{{ payments_config_validator }}"
  register: payments_config_result
  notify: Restart payments service

- name: Transition changed host through drain, restart and rejoin
  when: payments_config_result.changed
  block:
    - name: Drain host from the load balancer
      ansible.builtin.uri:
        url: "{{ load_balancer_api }}/pools/{{ load_balancer_pool }}/members/{{ asset_id }}/drain"
        method: POST
        headers:
          Authorization: "Bearer {{ load_balancer_token }}"
          Content-Type: application/json
        body_format: json
        body:
          reason: "Ansible config generation {{ payments_config_generation }}"
          runbook: "{{ atlas_runbook }}"
        status_code: [200, 202]
        return_content: true
      delegate_to: localhost
      become: false
      no_log: true
      register: drain_result

    - name: Execute notified restart before runtime verification
      ansible.builtin.meta: flush_handlers

    - name: Wait for local readiness after restart
      ansible.builtin.uri:
        url: "{{ payments_health_scheme }}://{{ payments_health_host }}:{{ payments_port }}{{ payments_health_path }}"
        method: GET
        status_code: 200
        return_content: true
      register: local_readiness
      retries: "{{ payments_health_retries }}"
      delay: "{{ payments_health_delay }}"
      until: local_readiness.status == 200

    - name: Verify process-loaded configuration generation
      ansible.builtin.uri:
        url: "{{ payments_health_scheme }}://{{ payments_health_host }}:{{ payments_port }}{{ payments_version_path }}"
        method: GET
        status_code: 200
        return_content: true
      register: local_version

    - name: Assert loaded generation is current
      ansible.builtin.assert:
        that:
          - local_version.json.service == payments_service_name
          - local_version.json.config_generation == payments_config_generation
        fail_msg: >-
          Process did not load expected generation
          {{ payments_config_generation }}.

    - name: Return healthy host to the load balancer
      ansible.builtin.uri:
        url: "{{ load_balancer_api }}/pools/{{ load_balancer_pool }}/members/{{ asset_id }}/enable"
        method: POST
        headers:
          Authorization: "Bearer {{ load_balancer_token }}"
          Content-Type: application/json
        body_format: json
        body:
          config_generation: "{{ payments_config_generation }}"
          runbook: "{{ atlas_runbook }}"
        status_code: [200, 202]
        return_content: true
      delegate_to: localhost
      become: false
      no_log: true

  rescue:
    - name: Record failed host transition
      ansible.builtin.debug:
        msg: >-
          Host {{ inventory_hostname }} / {{ asset_id }} failed after
          configuration transition. Keep it drained and investigate the
          preserved template backup, service logs and load-balancer state.

    - name: Stop the play for this failed transition
      ansible.builtin.fail:
        msg: "Payments rollout failed on {{ inventory_hostname }}."

- name: Verify service is active even when configuration was unchanged
  ansible.builtin.systemd_service:
    name: "{{ payments_service_name }}"
    state: started
  register: payments_service_state

- name: Read current runtime generation
  ansible.builtin.uri:
    url: "{{ payments_health_scheme }}://{{ payments_health_host }}:{{ payments_port }}{{ payments_version_path }}"
    method: GET
    status_code: 200
    return_content: true
  register: final_version
  changed_when: false

- name: Assert final runtime generation
  ansible.builtin.assert:
    that:
      - final_version.json.config_generation == payments_config_generation
    fail_msg: "Host is active but runs a stale configuration generation."
```

### Prečo je `validate` dôležité

`template` najprv vytvorí temporary candidate file a spustí:

```text
/usr/local/bin/payments-api check-config --config <temporary-file>
```

Destination sa nahradí iba pri úspešnej validácii. Tým sa oddeľuje render success od application-specific config validity.

Validation stále nepreukazuje, že database endpoint existuje alebo že credential file je použiteľný. Kontroluje iba to, čo implementuje `check-config`.

### Prečo sa drain vykonáva iba pri `changed`

Ak configuration bytes ostali rovnaké, host netreba vyberať z trafficu ani reštartovať. Druhý run má preto overiť health a generation, ale nemá vytvoriť ďalší rollout side effect.

### Prečo je `meta: flush_handlers` explicitné

Bez flush-u by handler typicky čakal do handler phase. Role by mohla vykonať runtime verification nad starým procesom, hoci file už obsahuje novú konfiguráciu. Explicitný flush vytvorí poradie:

```text
file changed
→ host drained
→ restart handler
→ local readiness
→ loaded generation
→ rejoin
```

## 12. Playbook s rolling batchom

`playbooks/payments.yml`:

```yaml
- name: Roll out payments configuration
  hosts: payments_app:&production
  gather_facts: true
  serial: 2
  max_fail_percentage: 0
  any_errors_fatal: true

  pre_tasks:
    - name: Verify resolved fleet size
      ansible.builtin.assert:
        that:
          - ansible_play_hosts_all | length == expected_payments_host_count
        fail_msg: >-
          Expected {{ expected_payments_host_count }} payments hosts but
          resolved {{ ansible_play_hosts_all | length }}.
      run_once: true

    - name: Show current batch identity
      ansible.builtin.debug:
        msg:
          runbook: "{{ atlas_runbook }}"
          batch_hosts: "{{ ansible_play_batch }}"
          config_generation: "{{ payments_config_generation }}"
      run_once: true

  roles:
    - role: payments_runtime

  post_tasks:
    - name: Verify load-balancer pool health after each batch
      ansible.builtin.uri:
        url: "{{ load_balancer_api }}/pools/{{ load_balancer_pool }}/health"
        method: GET
        headers:
          Authorization: "Bearer {{ load_balancer_token }}"
        status_code: 200
        return_content: true
      delegate_to: localhost
      become: false
      no_log: true
      register: pool_health
      run_once: true

    - name: Require healthy pool before next batch
      ansible.builtin.assert:
        that:
          - pool_health.json.unhealthy_members | int == 0
          - pool_health.json.enabled_members | int >= 2
        fail_msg: "Load-balancer pool is not safe for the next batch."
      run_once: true
```

`serial: 2` vytvára batches po dvoch hostoch. `run_once` sa pri serial play typicky vykonáva raz pre každý batch, nie iba raz za celý fleet. Preto pool health gate kontroluje stav medzi batches.

`max_fail_percentage: 0` a `any_errors_fatal: true` sú zámerne konzervatívne. Ich exact behavior treba testovať s použitou strategy a Ansible version; nie sú náhradou za explicitný per-host recovery model.

## 13. Inventory graph a host variables pred runom

Najprv over syntax inventory:

```bash
ansible-inventory --graph
```

Očakávaný graph:

```text
@all:
  |--@ungrouped:
  |--@production:
  |  |--@payments_app:
  |  |  |--payments-a-01
  |  |  |--payments-a-02
  |  |  |--payments-b-01
  |  |  |--payments-b-02
```

Tento output preukazuje logical group membership. Nezobrazuje všetky effective variables ani SSH identity.

Pozri konkrétny host:

```bash
ansible-inventory --host payments-a-01
```

Skontroluj najmä:

```json
{
  "ansible_host": "10.40.10.21",
  "asset_id": "i-0a111111111111111",
  "payments_config_generation": "cfg-2026-07-31-01"
}
```

Inventory-resolved output neobsahuje automaticky všetky play/task vars a extra vars. Je však vhodný na kontrolu connection a asset identity pred mutation.

## 14. Expected-vs-resolved asset manifest

Exportuj resolved inventory:

```bash
ansible-inventory --list > resolved-inventory.json
```

Vytvor normalizovaný asset list:

```bash
jq '
  [
    ._meta.hostvars
    | to_entries[]
    | select(.value.asset_id != null)
    | {
        inventory_hostname: .key,
        asset_id: .value.asset_id,
        availability_zone: .value.availability_zone
      }
  ]
  | sort_by(.asset_id)
' resolved-inventory.json > resolved-assets.json
```

Normalizuj expected manifest a porovnaj:

```bash
jq 'sort_by(.asset_id)' \
  inventories/prod/manifests/expected-assets.json \
  > expected-assets.sorted.json

diff --unified \
  expected-assets.sorted.json \
  resolved-assets.json
```

Prázdny diff preukazuje rovnosť troch vybraných fields medzi manifestmi. Nepreukazuje connectivity, host-key identity ani to, že expected manifest je fresh.

Počet `4 == 4` by nestačil. Jeden očakávaný host môže chýbať a jeden nesprávny môže byť navyše.

## 15. Playbook syntax a target list

```bash
ansible-playbook playbooks/payments.yml --syntax-check
ansible-playbook playbooks/payments.yml --list-hosts
ansible-playbook playbooks/payments.yml --list-tasks
```

`--syntax-check` preukazuje parse a časť statickej štruktúry. Nevykonáva inventory connectivity, template render pre každý host ani module operations.

`--list-hosts` preukazuje target set po pattern a `--limit` evaluation pre tento command context. Ak produkčný job používa `--limit`, musí byť zahrnutý aj v pre-run manifest evidence.

## 16. Check a diff prediction

```bash
ansible-playbook playbooks/payments.yml \
  --check \
  --diff
```

Check mode sa pokúsi predikovať changes bez mutation pre modules, ktoré ho podporujú. V našom flow delegated load-balancer tasks sú podmienene viazané na `payments_config_result.changed`; behavior závisí od check-mode resultu template module-u. Reálny handler, process restart a runtime request nemôžu byť plnohodnotne dokázané simuláciou.

Diff môže obsahovať configuration content. Ak template obsahuje secrets alebo sensitive endpoints, diff output musí byť obmedzený alebo task musí používať primeranú `diff: false` policy.

Check mode verdict preto znie:

```text
configuration prediction for supported tasks
```

nie:

```text
production rollout is safe
```

## 17. Získanie runtime credentialu

Walkthrough predpokladá environment variable `LOAD_BALANCER_TOKEN`, ktorú controller získa z external secret provideru cez short-lived identity.

Nevkladaj token priamo cez command-line extra vars:

```bash
ansible-playbook ... --extra-vars 'load_balancer_token=secret'
```

Command line môže skončiť v process liste, shell history alebo job logu.

Praktický bounded file môže byť vytvorený v chránenom workspace:

```bash
umask 077
cat > /tmp/payments-runtime-secrets.yml <<EOF
load_balancer_token: "${LOAD_BALANCER_TOKEN}"
EOF
```

Run použije:

```bash
ansible-playbook playbooks/payments.yml \
  --extra-vars @/tmp/payments-runtime-secrets.yml
```

Po rune file bezpečne odstráň podľa runner threat modelu. `no_log: true` na URI tasks znižuje log exposure, ale nechráni controller memory ani malicious plugin s prístupom k task arguments.

## 18. Produkčný rolling run

Spusti:

```bash
ansible-playbook playbooks/payments.yml \
  --extra-vars @/tmp/payments-runtime-secrets.yml \
  --diff
```

Prvý batch:

```text
payments-a-01
payments-a-02
```

Druhý batch:

```text
payments-b-01
payments-b-02
```

Očakávaný recap pri zmene configuration:

```text
payments-a-01 : ok=14 changed=3 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
payments-a-02 : ok=14 changed=3 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
payments-b-01 : ok=14 changed=3 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
payments-b-02 : ok=14 changed=3 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0
```

Čísla sú ilustračné. `failed=0` nepreukazuje, že inventory obsahoval celý expected fleet; to dokazuje predchádzajúci manifest comparison. `changed=3` nepreukazuje correctness mutation; module a custom result semantics môžu byť chybné.

## 19. Per-host runtime read-back

Ad hoc read-only kontrola:

```bash
ansible payments_app \
  --module-name ansible.builtin.uri \
  --args 'url=http://127.0.0.1:8080/version return_content=true status_code=200' \
  --one-line
```

Očakávaný payload pre každý host obsahuje:

```json
{
  "service": "payments-api",
  "config_generation": "cfg-2026-07-31-01"
}
```

Tým overíme direct per-host process path. Neoveríme load-balancer routing ani external user path.

## 20. Fleet a load-balancer verification

Z controllera:

```bash
curl --fail --silent --show-error \
  -H "Authorization: Bearer ${LOAD_BALANCER_TOKEN}" \
  "https://lb-admin.example.com/api/v1/pools/payments-production/members" \
  | jq .
```

Očakávaj štyri enabled a healthy immutable asset IDs.

Potom vykonaj request cez používateľský endpoint:

```bash
for attempt in $(seq 1 20); do
  curl --fail --silent \
    -H 'x-atlas-verification: PAY-CONFIG-17' \
    https://payments.example.com/version
done | jq -s 'group_by(.config_generation) | map({generation: .[0].config_generation, count: length})'
```

Očakávaný výsledok:

```json
[
  {
    "generation": "cfg-2026-07-31-01",
    "count": 20
  }
]
```

Opakované requests zvyšujú šancu zasiahnuť viac backendov, ale nie sú matematický dôkaz úplného fleet coverage. Silnejší test koreluje response s backend identity alebo priamo kontroluje každý load-balancer member.

## 21. Druhý idempotentný run

Spusti rovnaký playbook druhýkrát s rovnakým contentom, inventory a variables:

```bash
ansible-playbook playbooks/payments.yml \
  --extra-vars @/tmp/payments-runtime-secrets.yml
```

Očakávaný recap:

```text
payments-a-01 : ok=8 changed=0 unreachable=0 failed=0
payments-a-02 : ok=8 changed=0 unreachable=0 failed=0
payments-b-01 : ok=8 changed=0 unreachable=0 failed=0
payments-b-02 : ok=8 changed=0 unreachable=0 failed=0
```

`changed=0` preukazuje, že module/task model v druhom rune nehlásil mutation. Role stále vykoná read-only service a generation verification. Ak druhý run znovu drain-ne hosty alebo reštartuje service, side-effect flow nie je idempotentný, aj keby file task hlásil `ok`.

## 22. GitLab pipeline pre Ansible validation a production run

```yaml
stages:
  - validate
  - plan
  - deploy
  - verify

variables:
  ANSIBLE_CONFIG: "$CI_PROJECT_DIR/ansible.cfg"
  ANSIBLE_COLLECTIONS_PATH: "$CI_PROJECT_DIR/.ansible/collections"

ansible_validate:
  stage: validate
  image: registry.example/automation/ansible@sha256:<verified-execution-environment-digest>
  script:
    - ansible --version
    - ansible-config dump --only-changed
    - ansible-galaxy collection list
    - ansible-inventory --graph
    - ansible-inventory --list > resolved-inventory.json
    - ./scripts/compare-inventory-manifest.sh
    - ansible-playbook playbooks/payments.yml --syntax-check
    - ansible-playbook playbooks/payments.yml --list-hosts
  artifacts:
    expire_in: 14 days
    paths:
      - resolved-inventory.json
      - resolved-assets.json

ansible_check_prod:
  stage: plan
  image: registry.example/automation/ansible@sha256:<verified-execution-environment-digest>
  tags: [ansible-prod]
  needs:
    - job: ansible_validate
      artifacts: true
  script:
    - ./scripts/fetch-runtime-secrets.sh
    - ansible-playbook playbooks/payments.yml --check --diff --extra-vars @/tmp/payments-runtime-secrets.yml
  artifacts:
    when: always
    expire_in: 7 days
    paths:
      - check-mode.log

ansible_apply_prod:
  stage: deploy
  image: registry.example/automation/ansible@sha256:<verified-execution-environment-digest>
  tags: [ansible-prod]
  resource_group: payments-config-production
  needs:
    - job: ansible_validate
      artifacts: true
    - job: ansible_check_prod
  when: manual
  allow_failure: false
  environment:
    name: configuration/payments-production
  script:
    - ./scripts/fetch-runtime-secrets.sh
    - ansible-playbook playbooks/payments.yml --diff --extra-vars @/tmp/payments-runtime-secrets.yml | tee apply.log
    - ansible-playbook playbooks/payments.yml --extra-vars @/tmp/payments-runtime-secrets.yml | tee second-run.log
    - ./scripts/assert-second-run-no-change.sh second-run.log
  after_script:
    - rm -f /tmp/payments-runtime-secrets.yml
  artifacts:
    when: always
    expire_in: 14 days
    paths:
      - apply.log
      - second-run.log
```

Execution environment je digest-pinned. Production runner má restricted network path k hosts a load-balancer API. Merge-request jobs nesmú používať tento runner ani secret-fetch identity.

Check job je prediction evidence, nie approval substitute. Apply job musí byť viazaný na rovnaký source, inventory manifest, execution image a variable generation, ktoré boli skontrolované.

## 23. Worked failure: stale inventory vynechal host

Dynamic inventory cache obsahuje iba tri zo štyroch instances:

```text
expected asset IDs = 4
resolved asset IDs = 3
play recap hosts = 3
failed = 0
```

Bez expected-vs-resolved manifestu by run vyzeral zeleno. Chýbajúci host nie je `unreachable`, pretože sa nikdy nedostal do target setu.

Recovery:

```text
zastaviť promotion
→ zachovať inventory source/cache metadata
→ invalidovať alebo obnoviť cache
→ opraviť tag/filter/source
→ porovnať exact asset IDs
→ targeted run na chýbajúcom hoste
→ full fleet runtime verification
```

## 24. Worked failure: template validation odmietla candidate

Nová variable nastaví:

```yaml
payments_log_level: verbose-all
```

Aplikácia podporuje iba `debug`, `info`, `warn`, `error`. Jinja render vytvorí syntakticky validný YAML, ale `check-config` v `validate` vráti non-zero exit code.

Očakávaný outcome:

```text
temporary file rendered
→ validator failed
→ destination file unchanged
→ template task failed
→ handler not notified
→ host remains on previous config/process generation
```

Toto je bezpečnejšie než najprv prepísať destination a až potom zistiť, že service nedokáže štartovať.

## 25. Worked failure: restart prešiel, rejoin zlyhal

Host sa drain-ne, file sa zmení, handler reštartuje service a local readiness prejde. Load-balancer `enable` request však timeoutuje s unknown outcome.

```text
local host healthy
→ rejoin request timeout
→ nevieme, či LB mutation prebehla
→ automatický retry môže byť bezpečný iba s idempotency key/read-backom
```

Recovery musí najprv read-backnuť member state podľa immutable `asset_id`. Ak je enabled a healthy, retry netreba. Ak je drained, zopakuj bounded enable operation. Ak je stav neznámy, zastav ďalší batch, aby zostala dostatočná capacity.

## 26. Worked failure: nesprávne `changed_when` zablokovalo handler

Operátor obalí template task:

```yaml
changed_when: false
```

File sa môže reálne zmeniť, ale task nepošle notification. Výsledok:

```text
new file bytes
→ changed=false
→ handler nebeží
→ process používa starú generation
→ file checksum vyzerá správne
```

Preto role overuje `/version` aj pri unchanged path-e. Configured file a process-loaded state sú dve rozdielne vrstvy.

## 27. Worked failure: náhodný `--limit`

Pipeline variable ostane nastavená:

```bash
--limit payments-a-01
```

Playbook je správny, ale target set má jeden host. `expected_payments_host_count` assertion používa `ansible_play_hosts_all`, takže run sa zastaví ešte pred mutation.

Pri legitímnom targeted recovery musí byť expected scope explicitne zmenený a schválený, nie obídený odstránením assertionu.

## 28. Diagnostický walkthrough pri mixed fleet

Symptom: external `/version` vracia dve config generations.

Stabilizuj subject:

```text
source commit
execution image digest
ansible.cfg digest
collections manifest
inventory sources/cache timestamp
pattern a --limit
expected/resolved asset manifests
run ID a batches
per-host template checksums
handler events
service start times
LB member states
/version payloads
```

Competing hypotheses:

```text
H1: host chýbal v inventory
H2: host bol vylúčený patternom alebo --limit
H3: SSH mutation zlyhala alebo bola ignored
H4: host dostal inú variable generation
H5: file sa zmenil, handler nebežal
H6: handler bežal, process načítal starý file/path
H7: host je healthy lokálne, ale LB stále routuje starý member
H8: verifier alebo LB telemetry je stale
```

Discriminating evidence:

- expected/resolved/attempted manifests testujú H1–H3;
- `ansible-inventory --host`, rendered checksum a backup files testujú H4;
- callback/handler result a systemd start time testujú H5;
- process command line, loaded generation a open file path testujú H6;
- LB member inventory a backend identity testujú H7;
- direct per-host request a timestamps testujú H8.

## 29. Evidence-preserving containment a recovery

Pri partial rollout-e:

```text
zastav ďalší batch
→ zachovaj inventory JSON, run log a per-host results
→ identifikuj old/new/failed/omitted hosts
→ nechaj neoverené hosty drained
→ potvrď fleet capacity
→ oprav inventory/variable/template/handler root cause
→ targeted recovery podľa immutable asset IDs
→ per-host loaded-generation check
→ LB member check
→ external critical journey
→ second no-change run
```

Nespúšťaj celý playbook opakovane bez klasifikácie. Rerun môže zmeniť ďalšie hosty a zničiť hranicu medzi pôvodným a recovery outcome-om.

## 30. Acceptance checklist

Walkthrough je úspešný iba vtedy, keď vieš preukázať:

```text
execution environment a collections sú pinned a read-backnuté
+ ansible.cfg je súčasť run subjectu
+ inventory hostnames, addresses a immutable asset IDs sú rozlíšené
+ expected a resolved asset manifests sú rovnaké
+ play pattern a --limit dávajú očakávaný target set
+ syntax check a check/diff prediction prejdú
+ template candidate prejde application validatorom
+ changed host sa drain-ne pred restartom
+ handler sa vykoná pred runtime verification
+ process vráti očakávanú config generation
+ host sa rejoin-ne iba po health checku
+ každý batch zachová fleet capacity
+ všetky expected hosts sú healthy a enabled
+ external path vracia iba novú generation
+ druhý run má changed=0 a nevytvára drain/restart side effects
+ omitted, stale-variable a handler-bypass paths sú detegované
```

Takto sa Ansible neučí ako YAML zoznam tasks. Učí sa ako target resolution, per-host state transition a fleet verification systém. Inventory, variables, template, handler a recap sú iba čiastkové dôkazy; dôveryhodný outcome vzniká až spojením coverage, loaded runtime state-u a service-level verification.

## Primárne zdroje

- [Ansible playbooks](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_intro.html)
- [Ansible inventory](https://docs.ansible.com/projects/ansible/latest/inventory_guide/intro_inventory.html)
- [Ansible variables and facts](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_vars_facts.html)
- [Ansible check and diff mode](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_checkmode.html)
- [Ansible handlers](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_handlers.html)
- [Ansible error handling](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_error_handling.html)
- [Ansible template module](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/template_module.html)
- [Ansible URI module](https://docs.ansible.com/projects/ansible/latest/collections/ansible/builtin/uri_module.html)
- [Ansible playbook CLI](https://docs.ansible.com/projects/ansible/latest/cli/ansible-playbook.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Ansible idempotencia](ansible-idempotency.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ansible troubleshooting →](ansible-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
