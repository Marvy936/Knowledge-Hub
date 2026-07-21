# Vault

Ansible Vault šifruje variables a files, aby citlivé hodnoty nemuseli byť uložené v plaintext podobe v Git repository alebo distribuovaných automation artifacts. Vault však nie je plnohodnotný secret manager a nechráni secret po dešifrovaní počas executionu.

Správny návrh musí oddeliť:

- encrypted secret material,
- vault password alebo decryption identity,
- runtime access policy,
- log a artifact hygiene,
- rotation a incident response.

## 1. Čo Ansible Vault chráni

Vault chráni dáta **at rest**:

```text
plaintext secret
→ encrypt with vault password
→ encrypted file or value in repository
```

Nechráni automaticky:

- secret v process memory,
- rendered configuration na targete,
- debug output,
- module arguments v callback logu,
- temporary files,
- shell history,
- compromised control node,
- používateľa alebo job s decryption accessom.

## 2. Threat model

Vault rieši najmä riziko:

- accidental plaintext commit,
- čítanie repository bez vault passwordu,
- bezpečnejšie versionovanie malého množstva encrypted data,
- separáciu prostredí pomocou vault IDs.

Vault nerieši:

- automatickú rotation,
- dynamic short-lived credentials,
- fine-grained per-secret audit,
- automatic revocation,
- runtime injection bez plaintext exposure,
- kompromitovaný execution environment.

Pri väčšom alebo dynamickom secret lifecycle preferuj external secret manager.

## 3. Vault password

Každý encrypted content potrebuje password alebo secret source na dešifrovanie.

Password môže byť poskytnutý cez:

- interactive prompt,
- password file,
- executable password-client script,
- automation platform credential,
- integráciu s external secret managerom.

Vault password nesmie byť uložený vedľa encrypted file v rovnakom repository.

## 4. Vault ID

Vault ID je label spájajúci encrypted content s logickou decryption identitou:

```text
dev
stage
prod
network
cloud
```

Príklad:

```bash
ansible-vault encrypt --vault-id prod@prompt group_vars/production/vault.yml
```

Encrypted header môže obsahovať label:

```text
$ANSIBLE_VAULT;1.2;AES256;prod
```

Label nie je secret ani kryptografická access-control policy. Pomáha vybrať správny password source.

## 5. Viac vault IDs

Run môže potrebovať viac encrypted domains:

```bash
ansible-playbook site.yml \
  --vault-id prod@/secure/prod-password-client \
  --vault-id database@/secure/db-password-client
```

Rozdelenie používaj podľa:

- environmentu,
- ownershipu,
- rotation lifecycle,
- blast radiusu,
- decryption authorization.

Jeden globálny password pre všetky environments vytvára široký compromise scope.

## 6. Encrypted file

Celý file možno vytvoriť alebo zašifrovať:

```bash
ansible-vault create --vault-id prod@prompt group_vars/production/vault.yml
ansible-vault encrypt --vault-id prod@prompt existing-secrets.yml
```

Výhody:

- celý obsah je skrytý,
- file môže obsahovať viac variables,
- jednoduché presunutie a versionovanie.

Nevýhody:

- diff nie je semanticky čitateľný,
- celý file sa musí dešifrovať pri načítaní,
- review zmien je ťažšie,
- merge conflicts sú problematické.

## 7. Encrypted variable

Jednu hodnotu možno zašifrovať cez `encrypt_string`:

```bash
ansible-vault encrypt_string \
  --vault-id prod@prompt \
  --name 'example_database_password' \
  'sensitive-value'
```

Výsledok:

```yaml
example_database_password: !vault |
  $ANSIBLE_VAULT;1.2;AES256;prod
  6134...
```

Výhody:

- plaintext file structure a non-secret metadata ostávajú čitateľné,
- menšie encrypted units,
- jednoduchšie dokumentovanie variable contractu.

Nevýhody:

- encrypted block je stále nečitateľný v review,
- copy/paste je náchylný na chyby,
- veľa inline blocks znižuje udržiavateľnosť.

## 8. Oddelenie názvov a hodnôt

Odporúčaný pattern:

```text
group_vars/production/
├── vars.yml
└── vault.yml
```

`vars.yml`:

```yaml
example_database_host: db.prod.internal
example_database_user: example_app
example_database_password: "{{ vault_example_database_password }}"
```

`vault.yml`:

```yaml
vault_example_database_password: !vault |
  $ANSIBLE_VAULT;1.2;AES256;prod
  ...
```

Výhody:

- public variable contract je viditeľný,
- secret storage names sú explicitné,
- templates nemusia poznať vault implementation detail,
- budúci presun do external secret managera je jednoduchší.

## 9. Bežné príkazy

### Vytvorenie

```bash
ansible-vault create secret.yml
```

### Zašifrovanie

```bash
ansible-vault encrypt secret.yml
```

### Zobrazenie

```bash
ansible-vault view secret.yml
```

### Editácia

```bash
ansible-vault edit secret.yml
```

### Zmena passwordu

```bash
ansible-vault rekey \
  --vault-id old@prompt \
  --new-vault-id new@prompt \
  secret.yml
```

### Dešifrovanie

```bash
ansible-vault decrypt secret.yml
```

Permanentné decryptovanie versionovaného file-u je riziková operácia. Pred commitom over repository diff a secret scanning.

## 10. Password file

Password file môže obsahovať vault password, ale musí byť:

- mimo repository,
- s obmedzenými filesystem permissions,
- dostupný iba autorizovanej identity,
- chránený backup a rotation policy,
- auditovaný podľa platformy.

Príklad:

```bash
chmod 0600 ~/.config/ansible/prod-vault-password
ansible-playbook site.yml --vault-id prod@~/.config/ansible/prod-vault-password
```

Hardcoded password file v CI image je iba presunutý static secret.

## 11. Password-client script

Vault password source môže byť executable script:

```text
CI job identity
→ authenticate to secret manager
→ retrieve vault password
→ return it to Ansible
```

Script potrebuje:

- minimum-scope identity,
- bounded timeout,
- žiadny secret logging,
- definované exit codes,
- failure handling,
- audit trail,
- rotation-compatible behavior.

Lepším modelom môže byť načítať priamo cieľový secret z external managera a Vault úplne obísť.

## 12. Vault a external secret manager

### Vault je vhodný pre

- malé množstvo relatívne statických secrets,
- repository-oriented workflow,
- offline alebo disconnected automation,
- bootstrap secrets s riadenou rotation,
- environments bez dostupného secret API.

### External secret manager je vhodný pre

- krátkodobé credentials,
- automatickú rotation,
- per-secret access policy,
- audit každého readu,
- dynamic database/cloud credentials,
- centrálne revocation,
- veľké množstvo consumers.

Hybridný model môže používať Vault iba na bootstrap identity. Musí však mať jasný dôvod a rotation path.

## 13. `no_log`

Task spracúvajúci secret môže používať:

```yaml
- name: Configure secret value
  ansible.builtin.uri:
    url: https://service.internal/api/credential
    method: POST
    body_format: json
    body:
      password: "{{ example_database_password }}"
  no_log: true
```

`no_log: true` znižuje exposure v bežnom outpute, ale:

- sťažuje troubleshooting,
- nechráni malicious plugin,
- nemusí chrániť external process logs,
- nechráni rendered destination,
- neanuluje secret v memory.

Používaj ho cielene na secret-bearing tasks a súčasne zachovaj non-secret diagnostiku.

## 14. Template a secret exposure

Template môže zapísať secret na target:

```yaml
- name: Render application secrets
  ansible.builtin.template:
    src: application.env.j2
    dest: /etc/example/application.env
    owner: root
    group: example
    mode: "0640"
  no_log: true
```

Kontroluj:

- destination owner/group/mode,
- backup behavior,
- temporary-file umiestnenie,
- diff mode,
- process permissions,
- application logovanie,
- cleanup po rotation.

Vault šifrovanie repository neznamená, že výsledný file na hoste je encrypted.

## 15. Diff mode

`--diff` môže zobraziť starý a nový obsah file-u. Pri secret-bearing templates alebo files môže uniknúť plaintext.

Pre citlivé tasks zváž:

```yaml
diff: false
no_log: true
```

Globálne vypnutie diff mode však znižuje observability. Rozlišuj secret a non-secret configuration.

## 16. Temporary files

Pri `ansible-vault edit` alebo template execution môžu vzniknúť dočasné files.

Chráň:

- editor swap a backup files,
- temporary directory permissions,
- workstation disk encryption,
- shell history,
- crash dumps,
- CI artifacts,
- workspace cleanup.

Editor alebo plugin môže plaintext uložiť mimo očakávaného file-u.

## 17. CI/CD model

Odporúčaný workflow:

```text
protected pipeline
→ short-lived CI identity
→ retrieve vault password or secret
→ decrypt only in isolated runtime
→ run scoped playbook
→ redact logs
→ destroy workspace/runtime
```

CI job nemá poskytovať decryption access untrusted merge-request contentu.

Over:

- protected refs,
- trusted runner,
- environment approval,
- secret scope,
- fork pipeline behavior,
- artifact retention,
- debug flags,
- workspace cleanup.

## 18. Review encrypted zmien

Encrypted diff nedokazuje, čo sa zmenilo. Review proces môže obsahovať:

1. autorizovaný reviewer dešifruje old a new content v bezpečnom prostredí,
2. vytvorí non-secret change summary,
3. overí variable names a consumers,
4. overí rotation a rollout plan,
5. overí, že stará hodnota bude revokovaná,
6. zachová audit bez plaintext secretu.

Nikdy nekopíruj secret do merge-request komentára.

## 19. Rotation

Rotation nie je iba `ansible-vault rekey`.

Rozlišuj:

### Encryption-key rotation

Mení vault password chrániaci encrypted content.

### Secret-value rotation

Mení samotný database password, API token alebo private key.

Správny proces:

```text
create new credential
→ distribute/update consumers
→ verify new credential
→ revoke old credential
→ re-encrypt repository content if needed
→ audit completion
```

Rekey bez zmeny cieľového secretu nerieši kompromitovaný database password.

## 20. Break-glass

Produkčný vault password potrebuje recovery model:

- minimálny počet custodians,
- oddelené uloženie,
- audited retrieval,
- emergency approval,
- post-use rotation,
- testovaný recovery postup.

Break-glass secret, ktorý nikto nevie použiť, nie je recovery control. Secret dostupný každému nie je break-glass.

## 21. Secret scanning

Repository má skenovať:

- plaintext credentials,
- private keys,
- tokens,
- cloud access keys,
- accidental decrypted files,
- editor backups,
- CI logs a artifacts podľa platformy.

Scanner nezistí každý custom secret. Doplň ho naming, review a runtime controls.

## 22. Incident response

Pri podozrení na exposure:

1. považuj secret za kompromitovaný,
2. revoke alebo rotate cieľový credential,
3. zisti, ktoré identities a systems ho používali,
4. audituj access a použitie,
5. odstráň plaintext z aktívnych artifacts a caches,
6. podľa potreby rewrite-ni Git history,
7. zmeň vault password, ak bol kompromitovaný,
8. oprav pipeline alebo logging root cause.

Odstránenie secretu z posledného commitu ho neodstráni z Git history.

## 23. Anti-patterny

### Vault password v repository

Encryption a decryption material sú na rovnakom mieste.

### Jeden password pre všetky environments

Kompromitácia development accessu otvorí production secrets.

### `no_log: true` na celý playbook

Troubleshooting a audit sú slepé, hoci väčšina tasks secret nepotrebuje.

### Vault ako náhrada rotation procesu

Encrypted stale credential ostáva stale credential.

### Decrypted file ako CI artifact

Secret prežije job a môže mať široký access.

### Secret v role defaults

Default je public contract a často sa publikuje spolu s role.

### Password-client script loguje response

Secret uniká cez stderr alebo debug output.

### Inline encrypted blocks bez naming convention

Nie je zrejmé, čo sa rotuje a kto hodnotu vlastní.

## 24. Troubleshooting

### `Decryption failed`

Over vault ID, password source, content header, whitespace/corruption a to, či run dostal všetky potrebné IDs.

### Ansible skúša nesprávny password

Použi explicitné vault IDs a oddelené password sources. Nespoliehaj sa na nejasné poradie viacerých hesiel.

### Secret sa objavil v logu

Okamžite obmedz access k logu, rotate credential a skontroluj task output, callback plugins, verbosity, `no_log`, diff a external commands.

### `ansible-vault edit` zanechal temporary file

Zastav prácu, zabezpeč file, skontroluj editor configuration a workstation temp/swap behavior.

### CI decryptuje lokálne, ale nie na runneri

Porovnaj vault IDs, identity, password-client dependencies, filesystem permissions, network access a execution-environment content.

### Rekey prešiel, playbook zlyhal

Over, či všetky files boli rekey-nuté a pipeline používa nový password source. Rekey nemení cieľové application credentials.

## 25. Kontrolné otázky

1. Čo Ansible Vault chráni a čo nechráni?
2. Aký je rozdiel medzi encrypted file a encrypted variable?
3. Na čo slúži vault ID?
4. Prečo vault password nesmie byť v repository?
5. Kedy je vhodnejší external secret manager?
6. Čo robí `no_log` a aké má limity?
7. Ako môže diff mode odhaliť secret?
8. Aký je rozdiel medzi rekey a secret rotation?
9. Ako navrhnúť CI decryption boundary?
10. Čo urobiť po plaintext exposure?

## Glossary impact

Relevantné pojmy: Ansible Vault, vault password, vault ID, encrypted file, encrypted variable, `encrypt_string`, rekey, password-client script, data at rest, `no_log`, secret rotation a break-glass secret.

## Oficiálna dokumentácia

- [Ansible Vault](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault.html)
- [Encrypting content with Ansible Vault](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault_encrypting_content.html)
- [Using encrypted variables and files](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault_using_encrypted_content.html)
- [Managing vault passwords](https://docs.ansible.com/projects/ansible/latest/vault_guide/vault_managing_passwords.html)
