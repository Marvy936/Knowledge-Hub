# Vault

Ansible Vault chráni sensitive values **at rest** v repository alebo automation contente. Nerobí z nich automaticky short-lived credentials, nechráni plaintext po dešifrovaní, neurčuje consumer rollout a nerevokuje starú hodnotu. Úspešný `ansible-vault encrypt` alebo `rekey` preto nie je complete secret-management outcome. Dôveryhodný lifecycle musí viesť od logical secret identity cez encrypted artifact a decryption authorization až po runtime publication, consumer verification, old-credential revocation a cleanup.

Kapitola pokračuje incidentom `IAC-PAY-79`. Database credential unikne do CI logu. Tím rekey-ne Vault file, takže ciphertext a vault password sa zmenia, ale samotný database password zostane platný. Neskôr sa nový credential dostane iba na osem z dvanástich hosts a optional revocation job nebeží. Repository vyzerá „bezpečne zašifrované“, no kompromitovaný credential zostáva aktívny a fleet používa dve epochs.

## 1. Dominantný secret-to-revocation lifecycle

Vault lifecycle nezačína ciphertextom, ale logical credentialom, ownerom a consumer inventory. Encryption chráni repository state; po decryption vzniká nový plaintext exposure graph a po publication musí nasledovať process reload, target-side revocation a forbidden-old-credential test.

```text
logical secret intent, owner a consumer inventory
→ target credential epoch creation
→ encrypted Vault artifact a vault ID
→ authorized decryption identity
→ bounded plaintext exposure
→ target file/API publication
→ process reload a consumer verification
→ old credential revocation
→ forbidden-old-credential test
→ workspace/log/artifact cleanup a audit closure
```

## 2. Exact secret subject

```yaml
secretSubject:
  logicalId: payments-db/runtime-password
  targetSystem: payments-production-database
  environment: prod-eu
  epoch: 2026-07-31-02
  owner: payments-platform
  consumersManifestDigest: sha256:f39c...
  vault:
    artifact: group_vars/prod/vault.yml
    sourceRevision: 991ad7e
    vaultId: prod-database
  decryption:
    workloadIdentity: ansible-prod-controller
    runId: gitlab-98231
  runtime:
    destination: /etc/atlas-payments/runtime.env
    expectedMode: '0640'
  previousEpoch: 2026-06-10-01
  revocationRequired: true
```

Bez logical ID, epoch a consumer inventory nemožno dokázať, čo sa rotuje, kto to používa a kedy je bezpečné starú hodnotu zrušiť.

## 3. Čo Vault chráni a čo nechráni

Vault šifruje variable alebo file content at rest v repository a automation artifacts. Tým obmedzuje náhodné čítanie source-u bez Vault password materialu. Nechráni však plaintext po autorizovanom dešifrovaní.

Controller memory, temporary files, rendered target files, module arguments, registered results, validator stderr, callbacks a debug logs sú samostatné exposure boundaries. Malicious collection/plugin s decrypt accessom môže value exfiltrovať a credential uniknutý pred encryption zostáva kompromitovaný.

Vault zároveň nevykonáva target credential lifecycle. Rekey mení wrapper key, nie database password alebo API token. Old credential bez provider-side revocation môže fungovať aj po perfektnom re-encryption. Dôkaz preto oddeľuje repository confidentiality, runtime plaintext confidentiality a revocation completion.

## 4. Encrypted file a encrypted value

Celý file:

```bash
ansible-vault encrypt \
  --vault-id prod-database@prompt \
  group_vars/prod/vault.yml
```

Jedna value:

```bash
ansible-vault encrypt_string \
  --vault-id prod-database@prompt \
  --name vault_atlas_payments_database_password \
  'sensitive-value'
```

Encrypted file skrýva štruktúru, ale zhoršuje semantic review. Inline value zachová názvy/non-secret metadata, ale veľa ciphertext blokov znižuje čitateľnosť.

Repository-visible contract:

```yaml
atlas_payments_database_password: "{{ vault_atlas_payments_database_password }}"
```

oddeľuje consumer interface od storage implementation.

## 5. Vault ID

Vault ID v headeri, napríklad `prod-database`, je routing label, ktorý vyberá password source pri decryption. Nie je samostatnou authorization policy, logical secret identity ani credential epoch.

Vault domains sa navrhujú podľa environmentu, ownera, consumer scope-u, rotation lifecycle-u, blast radiusu a decryption authorization. Jeden password pre dev a prod znamená, že compromise jednej boundary umožní decrypt druhej.

Execution subject preto zachováva vault ID aj workload identity a logical secret/epoch. Forbidden test musí potvrdiť, že non-production controller alebo untrusted source nedokáže použiť production password client.

## 6. Decryption identity

Password source môže byť prompt, protected file, executable password client, controller credential alebo external secret manager. Oficiálna dokumentácia podporuje `--vault-password-file` a `--vault-id` patterns. citeturn329472search27

Password client má používať short-lived minimum-scope workload identity:

```text
controller identity
→ authenticate to secret service
→ retrieve only prod-database decryption material
→ pass directly to Ansible
→ avoid persistent plaintext
```

Static password zabudovaný v execution image je iba secret presunutý do iného artifactu.

## 7. Trusted-content boundary

Production decryption nesmie byť dostupná untrusted merge-request contentu. Inak môže útočník zmeniť lookup/action/callback plugin a exfiltrovať dešifrovanú value.

Controls:

```text
protected reviewed source revision
+ immutable execution environment
+ restricted plugin/search paths
+ environment-scoped workload identity
+ egress policy
+ separate validation a production-secret jobs
```

`no_log` nezastaví malicious code, ktoré posiela secret cez network.

## 8. Plaintext path

```text
decryption source
→ Ansible variable memory
→ Jinja/module argument
→ controller/remote temporary path
→ target file alebo API request
→ application process
→ logs, callbacks, backups a crash artifacts
```

Každý krok je exposure boundary.

Secret-bearing task:

```yaml
- name: Publish runtime credential
  ansible.builtin.template:
    src: runtime.env.j2
    dest: /etc/atlas-payments/runtime.env
    owner: root
    group: atlas-payments
    mode: '0640'
    validate: /usr/local/bin/atlas-env-validate %s
  no_log: true
  diff: false
  notify: Reload Atlas Payments
```

`no_log` redukuje bežný task output. Nechráni memory, destination file, malicious plugin ani external validator, ktorý secret vypíše.

## 9. Non-secret evidence

Secret value sa neloguje. Evidence môže obsahovať:

```yaml
secretDeploymentEvidence:
  logicalId: payments-db/runtime-password
  epoch: 2026-07-31-02
  hostId: i-0app07
  destinationChecksum: sha256:71cc...
  fileMode: '0640'
  processReloadedAt: 2026-07-31T09:15:00Z
  authenticationProbe: pass
```

Destination checksum preukazuje bytes, nie správnosť secretu ani loaded process state. Authentication probe a process epoch dopĺňajú proof.

## 10. Target credential rotation verzus Vault rekey

### Vault rekey

```bash
ansible-vault rekey \
  --vault-id old@prompt \
  --new-vault-id new@prompt \
  group_vars/prod/vault.yml
```

Mení encryption wrapper/password chrániaci ciphertext.

### Target credential rotation

```text
vytvor nový DB password epoch 02
→ update encrypted artifact
→ rollout consumers
→ verify new auth
→ revoke epoch 01
```

Rekey kompromitovaný database password nezneplatní.

## 11. Worked incident: rekey namiesto rotation

CI log obsahoval plaintext DB password. Tím zmenil iba Vault password.

```text
plaintext credential leaked
→ ciphertext rewrapped
→ target DB credential unchanged
→ attacker stále autentizovaný
```

Recovery:

1. obmedziť access k logom;
2. auditovať použitie leaked credentialu;
3. vytvoriť nový target credential;
4. aktualizovať consumers;
5. overiť new auth;
6. revoke-nuť old credential;
7. otestovať old credential rejection;
8. rekey Vault iba ak unikol aj Vault password.

## 12. Consumer rollout

```text
create epoch 02
→ encrypt/publish artifact
→ resolve exact consumer manifest
→ canary decrypt/render/reload
→ verify process epoch a DB auth
→ rollout remaining hosts
→ verify all expected hosts
→ revoke epoch 01
→ forbidden old-credential probe
```

Niektoré systems povoľujú overlap dvoch credentials, iné potrebujú koordinovaný cutover. Capability cieľového systému je súčasť rotation designu.

## 13. Runtime verification

```yaml
- name: Query loaded credential epoch
  ansible.builtin.uri:
    url: https://127.0.0.1:8443/runtime
    validate_certs: true
    return_content: true
  register: runtime
  changed_when: false
  failed_when: runtime.json.credential_epoch != atlas_database_credential_epoch
```

Runtime endpoint nesmie publikovať secret. Preukazuje process-reported epoch. DB authentication probe potvrdí functional use; old credential rejection potvrdí revocation.

## 14. Old credential revocation

Rotation verdict classes:

```text
ENCRYPTED_ARTIFACT_UPDATED
CONSUMER_PARTIAL
CONSUMER_COMPLETE
REVOCATION_PENDING
REVOCATION_COMPLETE
CLEANUP_INCOMPLETE
INCIDENT_REQUIRED
```

Pipeline nesmie skončiť complete po consumer rollout-e, ak old credential stále funguje.

## 15. Worked incident: revocation job bol optional

Všetkých hosts načítalo epoch 02, ale optional revocation job sa nespustil.

```text
new credential works
+ old credential still valid
→ expanded active credential set
→ compromise window remains
```

Quality gate vyžaduje `REVOCATION_COMPLETE` a forbidden old-auth test.

## 16. Validator/log leakage

Task mal `no_log`, ale external validator vypísal celý file na stderr pri chybe. Callback log ho uložil.

```text
Ansible output redacted
→ external process leaks plaintext
→ logs persist
```

Validator pre secret-bearing artifact musí mať redacted failure contract. Pri exposure sa credential rotuje; iba vymazanie logu nestačí.

## 17. Temporary files a cleanup

Plaintext môže prežiť v:

- controller temp;
- remote temp;
- backup file;
- workspace;
- diff artifact;
- registered result;
- fact cache;
- crash dump.

Cleanup verdict:

```text
workspace destroyed
+ logs/artifacts scanned for leakage
+ remote temp/backups handled
+ secret not cached as fact
+ only authorized target/process retains value
```

Neoverený cleanup je `CLEANUP_INCOMPLETE`.

## 18. External secret manager boundary

Vault je vhodný pre encrypted automation content. Ak potrebujeme dynamic credentials, central revocation, per-secret policy alebo leases, external secret manager je silnejší authority.

Hybrid:

```text
repository obsahuje secret reference
→ controller workload identity
→ runtime lookup short-lived credentialu
→ minimum plaintext lifetime
```

Custom lookup plugin je supply-chain dependency a potrebuje audit, version pinning a no-leak behavior.

## 19. Competing hypotheses pri partial fleet rotation

```text
H1: hosts chýbali v target inventory
H2: použili iný vault ID/password source
H3: extra var prepísala decrypted value
H4: file updated, handler skipped
H5: process číta iný path
H6: target credential cutover bol príliš skoro
H7: second writer obnovil old file
H8: verifier kontroluje file, nie process
```

Dôkazy:

- expected/resolved hosts H1;
- Vault run metadata H2;
- effective epoch manifest H3;
- checksum/handler/process start H4/H5/H8;
- database audit H6;
- filesystem timeline H7.

## 20. Evidence-preserving containment a recovery

```text
pause rollout/revocation
→ preserve encrypted artifact/run metadata bez plaintextu
→ remove unhealthy hosts from traffic
→ identify loaded epochs
→ repair missing decryption/render/handler path
→ verify all consumers on epoch 02
→ revoke epoch 01
→ test old rejection
→ cleanup and audit closure
```

Ak plaintext unikol, incident response a credential rotation sú povinné; masking po udalosti nestačí.

## 21. Acceptance a forbidden paths

```text
logical secret ID/epoch/owner sú explicitné
+ Vault artifact a decryption identity sú oddelené
+ untrusted content nemá decrypt access
+ plaintext path je bounded
+ no_log/diff/log/validator controls sú testované
+ exact consumer manifest je complete
+ process loaded epoch je verified
+ new credential works
+ old credential is rejected
+ cleanup verdict is complete
+ rekey-only fixture is rejected as rotation closure
```

## 22. Anti-patterny

### „Vault vyriešil secrets management“

Rieši storage encryption, nie celý lifecycle.

### „Rekey je rotation“

Mení wrapper key, nie target credential.

### „`no_log` zabráni všetkým leakom“

Nechráni malicious plugin, destination, validator ani memory.

### „Nový secret funguje, môžeme skončiť“

Old credential musí byť revoked a forbidden testom odmietnutý.

### „Vault password môže byť v image“

Iba presúva static secret do širšieho artifactu.

## 23. Kontrolné otázky

1. Čo Vault chráni a čo nechráni?
2. Čo musí obsahovať secret subject?
3. Aký rozdiel je medzi encrypted file a value?
4. Čo Vault ID znamená?
5. Prečo decryption identity musí byť oddelená od repository?
6. Aké boundaries má plaintext path?
7. Čo `no_log` chráni a čo nie?
8. Aký rozdiel je medzi rekey a target rotation?
9. Prečo rotation nekončí consumer rolloutom?
10. Ako sa dokazuje old credential revocation?
11. Kedy je external secret manager vhodnejší?
12. Ako sa testuje forbidden untrusted-decryption a rekey-only path?

## Glossary impact

Relevantné pojmy: Ansible Vault, encrypted artifact, encrypted value, vault ID, decryption identity, password client, logical secret ID, credential epoch, plaintext exposure, no_log, rekey, target credential rotation, consumer manifest, revocation, forbidden old credential a cleanup verdict.

## Primárne zdroje

- [Protecting sensitive data with Ansible Vault](https://docs.ansible.com/projects/ansible/latest/vault_guide/index.html)
- [Ansible Vault](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault.html)
- [Managing Vault passwords](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault_managing_passwords.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Roles a collections](roles-and-collections.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ansible idempotencia →](ansible-idempotency.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
