# Vault

Ansible Vault rieši jednu konkrétnu časť secret lifecycle-u: chráni citlivé hodnoty **at rest** v repository alebo distribuovanom automation contente. Nechráni automaticky plaintext po dešifrovaní, consumer rollout, revocation ani incident response.

Preto sa Vault nemá chápať ako príkaz `ansible-vault encrypt`, ale ako súčasť jedného end-to-end modelu:

```text
secret intent, owner a consumer inventory
→ storage a encryption boundary
→ encrypted artifact + vault ID
→ decryption identity a runtime authorization
→ bounded plaintext exposure
→ consumer publication a loaded-state verification
→ old-credential revocation
→ workspace cleanup, audit a incident closure
```

Ak chýba ktorýkoľvek prechod, repository môže byť šifrované a systém napriek tomu používať starý credential, leakovať plaintext alebo ponechať kompromitovaný secret aktívny.

## 1. Atlas scenár

Atlas Payments potrebuje zmeniť produkčný database credential.

Zmena má tieto identity:

```text
secret logical ID: payments-db/runtime-password
secret epoch: 2026-07-27-02
owner: Payments Platform
consumers: app hosts app-01 až app-12
vault domain: prod-database
vault artifact: group_vars/production/vault.yml@commit S417
decryption identity: controller job J882 / workload identity WI-PROD-ANSIBLE
runtime destination: /etc/atlas-payments/runtime.env
process verification field: credential_epoch=2026-07-27-02
old credential epoch: 2026-06-10-01
```

Úspech nie je „file sa podarilo dešifrovať“. Úspech je:

```text
všetci oprávnení consumers načítali nový credential
+ nový credential funguje
+ starý credential je revokovaný
+ plaintext nezostal v logs, artifacts ani workspace
+ audit spája artifact, identity, consumers a revocation
```

## 2. Threat model a ochranná hranica

Vault transformuje plaintext na encrypted content:

```text
plaintext value
→ encryption s vault passwordom
→ encrypted file alebo !vault value
→ versionovanie v repository
```

Tým znižuje riziko, že človek s read accessom k repository okamžite prečíta secret. Nechráni však automaticky:

- controller process memory;
- decrypted temporary file;
- rendered target configuration;
- module arguments alebo registered results;
- callback, debug a external-process logs;
- shell history, editor swap a crash dump;
- používateľa alebo job s decryption accessom;
- kompromitovaný plugin alebo execution environment;
- starý credential, ktorý nebol revokovaný.

Mechanizmus je teda presne ohraničený:

```text
repository confidentiality ≠ runtime confidentiality ≠ credential lifecycle completion
```

Pri dynamic credentials, automatickej rotation, per-secret authorization alebo centrálnom revoke modeli je vhodnejší external secret manager. Vault môže zostať bootstrap vrstvou, ale iba s explicitným dôvodom a rotation pathom.

## 3. Secret subject

Pred encryption definuj secret ako riadený subject, nie iba YAML hodnotu.

Minimálny subject obsahuje:

```text
logical secret ID
credential type a target system
environment a trust boundary
owner a approver
consumer inventory
secret epoch/version
storage artifact a vault domain
decryption identity
runtime destinations
rotation deadline
revocation status
```

Bez logical ID a consumer inventory nevieš rozlíšiť:

- ktorý database password sa mení;
- ktoré hosts ho majú načítať;
- či stará hodnota môže byť zrušená;
- či rovnaký encrypted block niekto skopíroval do ďalšieho prostredia;
- či incident zasahuje jeden alebo viac credentials.

Názov variable má vyjadrovať contract:

```yaml
atlas_payments_database_password: "{{ vault_atlas_payments_database_password }}"
```

Repository-visible variable opisuje consumer interface. `vault_...` hodnota opisuje storage implementation. Tým sa dá neskôr zmeniť backend bez prepisovania templates a roles.

## 4. Encrypted artifact a vault ID

Celý file možno šifrovať:

```bash
ansible-vault encrypt \
  --vault-id prod-database@prompt \
  group_vars/production/vault.yml
```

Alebo jednu hodnotu:

```bash
ansible-vault encrypt_string \
  --vault-id prod-database@prompt \
  --name vault_atlas_payments_database_password \
  'sensitive-value'
```

Vault header môže niesť label:

```text
$ANSIBLE_VAULT;1.2;AES256;prod-database
```

Vault ID je routing label pre decryption source. Nie je to secret ani samostatná kryptografická authorization policy.

Rozdelenie vault domains má kopírovať reálne boundaries:

- environment;
- credential owner;
- rotation lifecycle;
- consumer scope;
- incident blast radius;
- decryption authorization.

Jeden password pre development aj production znamená, že development compromise otvára production encrypted content.

## 5. Encrypted file verzus encrypted value

Encrypted file skrýva celý obsah a zjednodušuje storage, ale zhoršuje semantic review a merge. Inline encrypted value zachová názvy a non-secret metadata, ale veľké množstvo blokov znižuje čitateľnosť.

Rozhodnutie má vychádzať z review a ownership modelu:

```text
potrebujem skryť celú štruktúru?
→ encrypted file

potrebujem viditeľný variable contract a malú secret unit?
→ encrypted value
```

Ani jeden model nezaručuje, že reviewer rozumie zmene. Encrypted diff dokazuje iba zmenu ciphertextu.

Review preto potrebuje autorizovanú plaintext comparison v chránenom prostredí a non-secret summary:

```text
secret epoch 01 → 02
consumer set unchanged: app-01..app-12
rotation reason: scheduled
old credential revocation after fleet verification
```

Secret sa nikdy nekopíruje do merge-request komentára.

## 6. Decryption identity a authorization

Encrypted artifact a decryption material musia zostať oddelené.

Password source môže byť:

- interactive prompt;
- protected password file mimo repository;
- executable password-client;
- automation-controller credential;
- external secret manager integration.

Produkčný run subject musí zaznamenať aspoň:

```text
vault IDs requested
decryption workload identity
protected ref/job template
execution image digest
secret scope
environment authorization
controller run ID
```

Password file v CI image je iba statický secret premiestnený do iného artifactu. Password-client script je lepší iba vtedy, keď používa minimum-scope short-lived identity, neloguje response a má auditovateľný read.

```text
controller workload identity
→ authenticate to secret service
→ retrieve only prod-database decryption material
→ pass value directly to Ansible
→ discard process/workspace state
```

CI nesmie poskytnúť decryption access neoverenému merge-request contentu. Inak môže útočník zmeniť playbook alebo plugin tak, aby secret odoslal mimo trust boundary.

## 7. Runtime plaintext exposure path

Po dešifrovaní treba sledovať celý plaintext path:

```text
decryption source
→ Ansible variable memory
→ Jinja/module argument
→ temporary transfer
→ target file alebo API request
→ application process
→ logs, callbacks a registered results
```

Každý krok je samostatná exposure boundary.

`no_log: true` redukuje bežný output, ale:

- neodstráni secret z memory;
- nechráni malicious plugin;
- nechráni target file;
- nezastaví external command, aby secret vypísal;
- nenahrádza access control;
- nerevokuje už uniknutý credential.

Secret-bearing task má vypnúť diff a zachovať samostatnú non-secret evidence:

```yaml
- name: Publish Atlas Payments runtime credential
  ansible.builtin.template:
    src: runtime.env.j2
    dest: /etc/atlas-payments/runtime.env
    owner: root
    group: atlas-payments
    mode: "0640"
    validate: /usr/local/bin/atlas-env-validate %s
  no_log: true
  diff: false
  notify: Reload Atlas Payments
```

Non-secret verification môže publikovať destination checksum, secret epoch, process reload time a authentication probe verdict bez hodnoty credentialu.

## 8. Temporary files a artifact hygiene

Plaintext môže prežiť run v:

- editor swap alebo backup file;
- controller temporary directory;
- remote temporary directory;
- CI workspace;
- debug log;
- diff artifact;
- cached fact alebo registered result;
- crash dump;
- backup vytvorený file module-om.

Cleanup nie je iba `rm -f`. Potrebuje overiteľný verdict:

```text
workspace destroyed
+ artifacts neobsahujú secret-bearing files
+ logs prešli redaction kontrolou
+ remote temp a backup policy je splnená
+ credential zostáva dostupný iba oprávnenému processu
```

Ak cleanup nevieš potvrdiť, run je `cleanup-incomplete`, nie plný success.

## 9. Consumer rollout

Atlas nemá meniť credential ako jeden neviditeľný file edit. Rotation je koordinovaný consumer transition.

Bezpečný model:

```text
create credential epoch 02
→ encrypt/publish subject S417
→ preflight consumer inventory
→ canary decrypt a render
→ reload canary process
→ verify authentication s epoch 02
→ rollout remaining consumers
→ verify all expected consumers
→ revoke epoch 01
→ verify epoch 01 rejected
→ close audit a cleanup
```

Niektoré systems podporujú overlap window, počas ktorého platia oba credentials. Iné vyžadujú presne koordinovaný cutover. Model musí poznať capabilities cieľového systému.

Runtime verification nemá kontrolovať iba file content. Potrebuje process-level alebo end-to-end oracle:

- proces načítal novú epoch;
- database authentication funguje;
- všetci expected consumers sú healthy;
- stará epoch už nie je používaná;
- traffic sa nevrátil na neaktualizovaný host.

## 10. Worked failure: rekey sa považoval za rotation

Database credential epoch 01 unikol do CI logu. Tím vykonal:

```bash
ansible-vault rekey vault.yml
```

Rekey zmenil iba encryption password chrániaci repository artifact. Cieľový database password zostal rovnaký.

Mechanizmus:

```text
credential value je kompromitovaná
→ zmení sa iba Vault wrapping key
→ encrypted artifact má nový ciphertext
→ database stále prijíma starú hodnotu
→ útočník s uniknutým plaintextom zostáva autorizovaný
```

Recovery musí zmeniť target credential, aktualizovať consumers, overiť novú hodnotu a revoke-nuť starú. Rekey môže byť doplnkový krok, ak bol kompromitovaný aj vault password.

## 11. Worked failure: untrusted pipeline dostala decryption access

Protected variable s vault passwordom bola dostupná jobu, ktorý spúšťal merge-request branch. Útočník pridal custom lookup plugin zapisujúci resolved variable do outbound HTTP requestu.

```text
repository ciphertext zostáva bezpečný
→ trusted CI identity dešifruje secret
→ untrusted executable content ovláda plaintext path
→ plugin exfiltruje hodnotu
```

`no_log` nepomôže, pretože exfiltration neprebieha cez bežný task output.

Required controls:

- decryption iba na protected reviewed revision;
- trusted immutable execution environment;
- obmedzené plugin/search paths;
- environment-scoped workload identity;
- egress control;
- oddelenie plan/check jobov od production secret jobu.

## 12. Worked failure: nový secret funguje, starý zostal aktívny

Všetkých dvanásť hosts dostalo epoch 02 a authentication probe prešiel. Pipeline skončila green, ale revocation job bol optional a nebežal.

```text
new credential publication succeeded
→ consumer verification succeeded
→ old credential remained valid
→ compromise window zostal otvorený
→ rollout success bol nesprávne stotožnený s rotation closure
```

Rotation verdict musí rozlišovať:

```text
published
consumer-partial
consumer-complete
revocation-pending
revocation-complete
cleanup-incomplete
incident-required
```

## 13. Worked failure: `no_log` skryl task, validation command leakol secret

Template task mal `no_log: true`, ale validation command pri chybe vypísal celý parsed environment na stderr. Callback ho pridal do controller logu.

```text
Ansible task output je redacted
→ external validator dostane plaintext file
→ validator vypíše secret
→ callback uloží stderr
→ log artifact prežije workspace
```

Secret-bearing validator musí mať redacted failure contract. Po exposure treba credential považovať za kompromitovaný, obmedziť log access, rotate/revoke a auditovať použitie.

## 14. Causal troubleshooting walkthrough: po rotation funguje iba časť fleet-u

Po rotácii epoch 02 je osem hosts healthy, štyri hlásia database authentication failure. Ansible job je green.

### 1. Zafixuj secret a run subject

Zaznamenaj:

- logical secret ID a epoch;
- encrypted artifact revision a vault ID;
- decryption workload identity;
- expected consumer inventory;
- target file checksum a owner/mode;
- handler/reload events;
- process-loaded epoch;
- old/new credential status v database;
- controller run a cleanup verdict.

### 2. Súťažiace hypotézy

1. Štyri hosts neboli v resolved target inventory.
2. Použili iný vault ID alebo password source.
3. Stale extra var prepísala dešifrovanú hodnotu.
4. File sa aktualizoval, ale handler neprebehol.
5. Process načítava iný config path.
6. Database credential cutover nastal pred consumer rolloutom.
7. Backup alebo druhý writer vrátil epoch 01.
8. Verifier kontroluje file, nie loaded process state.
9. Secret unikol a database ho bezpečnostný systém automaticky revoke-ol.

### 3. Diskriminačné observation points

- expected vs. resolved/attempted/verified host IDs;
- vault ID a password-source metadata bez secretu;
- redacted effective-value epoch manifest;
- destination checksum a file modification timeline;
- handler notification/execution a process start time;
- process environment alebo runtime credential epoch endpoint;
- database authentication audit podľa principalu a hostu;
- old/new credential enabled state;
- controller log/artifact redaction scan.

### 4. Containment

Pozastav ďalšiu rotation alebo rollback. Neaktualizované hosts odstráň z trafficu, ak nemajú funkčnú database session. Zablokuj plaintext-bearing logs a artifacts.

### 5. Recovery

- omitted hosts → oprav inventory a vykonaj explicitný scoped rollout;
- wrong vault source → oprav identity mapping a audituj nesprávne dešifrovaný domain;
- precedence override → odstráň stale value a zúž allowed sources;
- handler gap → vykonaj bounded reload a verify;
- wrong path → zosúlaď destination a process config contract;
- premature revoke → aktivuj kontrolovaný overlap alebo vydať novú epoch;
- second writer → odstráň ownership konflikt;
- exposure → rotate na ďalšiu epoch a vykonaj incident workflow.

### 6. Over pôvodný outcome

Potvrď všetkých dvanásť stable host IDs, loaded epoch 02, úspešnú database transaction, nulové použitie epoch 01, revocation epoch 01 a cleanup-complete evidence.

### 7. Posuň control skôr

Pridaj expected consumer manifest, epoch-aware process oracle, mandatory revocation gate, secret-bearing validator contract a redaction scan pred log/artifact publication.

## 15. Break-glass a recovery

Produkčný decryption path potrebuje testovaný break-glass model:

- minimálny počet custodians;
- oddelené uloženie;
- audited retrieval;
- emergency approval alebo policy;
- obmedzený čas použitia;
- post-use rotation;
- pravidelný recovery test.

Break-glass secret, ktorý sa nikdy netestoval, nemusí byť počas incidentu použiteľný. Secret dostupný každému nie je break-glass, ale trvalý široký access.

## 16. Secret scanning a incident response

Skenuj repository, workspaces, logs a artifacts na:

- plaintext credentials;
- private keys;
- editor backups;
- decrypted Vault files;
- debug output;
- generated environment files;
- provider/cloud tokens.

Scanner nenahrádza rotation a revocation.

Pri podozrení na exposure:

```text
contain access k plaintext artifactu
→ považuj credential za kompromitovaný
→ issue new epoch
→ update a verify consumers
→ revoke old epoch
→ audit historical use
→ odstráň aktívne copies/caches
→ podľa potreby rieš Git history
→ oprav root cause
```

Odstránenie secretu z posledného commitu neodstráni jeho hodnotu z Git history ani z už stiahnutých clones.

## 17. Referenčné pravidlá

- Vault chráni at-rest content, nie celý runtime secret lifecycle.
- Vault ID je routing label, nie access-control boundary.
- Encrypted diff potrebuje autorizovaný semantic review.
- Decryption identity musí byť oddelená od encrypted artifactu.
- Untrusted content nesmie dostať production decryption access.
- `no_log` je output-redaction control, nie revocation alebo sandbox.
- Secret-bearing render a validation path potrebuje samostatnú exposure analýzu.
- Rekey a target credential rotation sú odlišné operácie.
- Consumer rollout nie je kompletný bez runtime verification.
- Rotation nie je kompletná bez revocation starej hodnoty.
- Cleanup-incomplete secret run nie je plný success.
- Exposure vyžaduje rotate/revoke, nie iba lepšie maskovanie logs.

## 18. Kontrolné otázky

1. Ktorú časť secret lifecycle-u Ansible Vault chráni?
2. Čo tvorí secret subject a consumer inventory?
3. Prečo vault ID nie je authorization policy?
4. Ako sa líši encrypted file od encrypted value?
5. Prečo `no_log` nezastaví malicious plugin alebo external validator?
6. Aké identity tvoria production decryption subject?
7. Ako sa dokáže, že process načítal novú secret epoch?
8. Aký je rozdiel medzi rekey a target credential rotation?
9. Prečo rotation bez revocation nie je uzavretá?
10. Aké evidence odlíšia wrong vault source, stale override a missing reload?

## Glossary impact

Relevantné pojmy: secret lifecycle subject, secret epoch, consumer inventory, Vault artifact subject, vault ID, decryption identity, runtime plaintext path, secret-bearing render path, consumer rollout, revocation-complete verdict, cleanup-incomplete secret run, encryption-key rotation, target credential rotation a break-glass decryption.

## Oficiálna dokumentácia

- [Ansible Vault](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault.html)
- [Encrypting content with Ansible Vault](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault_encrypting_content.html)
- [Using encrypted variables and files](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault_using_encrypted_content.html)
- [Managing vault passwords](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault_managing_passwords.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Roles a collections](roles-and-collections.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ansible idempotencia →](ansible-idempotency.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
