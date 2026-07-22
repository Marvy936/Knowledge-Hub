# Secrets management

Secrets management je disciplína bezpečného vytvárania, distribúcie, používania, rotácie, revocation, auditovania a odstránenia citlivých credentials a cryptographic materialu. Secret nie je iba password. Patrí sem každý údaj alebo capability, ktorého získanie umožňuje neautorizovaný access, impersonation, decryption, signing alebo privileged operation.

## 1. Mentálny model

```text
identity a workload trust
→ authentication voči secrets platforme
→ authorization policy
→ secret issuance alebo retrieval
→ secure delivery do workloadu
→ bounded use
→ lease/rotation/revocation
→ audit
→ recovery a destruction
```

Cieľom nie je iba uložiť secret šifrovane. Cieľom je znížiť jeho životnosť, distribúciu, počet držiteľov a blast radius compromise-u.

## 2. Čo je secret

Príklady:

- database password,
- API key,
- OAuth client secret,
- private key,
- TLS certificate private key,
- SSH key,
- cloud access key,
- signing key,
- encryption key,
- webhook secret,
- package registry token,
- Kubernetes service-account token,
- recovery code,
- bootstrap credential.

Nie každý citlivý údaj je rovnaký typ secretu. Rozlišuj:

- authentication credential,
- encryption/signing key,
- bearer token,
- recovery material,
- configuration s citlivým obsahom,
- identity assertion s krátkou lifetime.

## 3. Secret lifecycle

```text
creation alebo import
→ classification
→ storage
→ authorization
→ distribution
→ use
→ renewal/rotation
→ revocation
→ archival podľa policy
→ secure destruction
```

Každá fáza potrebuje:

- ownera,
- policy,
- audit evidence,
- failure model,
- recovery postup.

## 4. Static a dynamic secrets

### Static secret

Existuje dlhšie obdobie a používa sa opakovane.

Príklady:

- fixed API key,
- long-lived database password,
- manually issued certificate.

Riziká:

- kopírovanie,
- reuse,
- nejasný ownership,
- zabudnutá rotation,
- dlhý compromise window.

### Dynamic secret

Generuje sa on demand pre konkrétnu identity, role alebo workload.

Príklady:

- krátkodobý database user,
- temporary cloud credentials,
- short-lived certificate,
- leased SSH credential.

Výhody:

- kratšia lifetime,
- lepší audit,
- per-client attribution,
- jednoduchšia revocation,
- menší blast radius.

Dynamic secret je preferovaný tam, kde ho cieľový systém podporuje.

## 5. Secret zero

Secret zero je prvotný credential alebo trust anchor potrebný na získanie ďalších secrets.

Príklady:

- workload identity token,
- cloud instance identity,
- Kubernetes service account token,
- machine certificate,
- Vault unseal alebo recovery material,
- bootstrap token.

Secret-zero problém nemožno vyriešiť uložením ďalšieho statického secretu vedľa aplikácie.

Preferuj bootstrap cez:

- platform workload identity,
- hardware-backed identity,
- mutual TLS,
- short-lived signed identity token,
- attestation,
- operator-mediated one-time enrollment.

## 6. Workload identity

Workload má autentizovať svoju runtime identitu, nie držať shared permanent credential.

Trust môže vychádzať z:

- cloud instance/task identity,
- Kubernetes ServiceAccount a projected token,
- SPIFFE identity,
- CI OIDC token,
- machine certificate,
- managed identity.

Authorization policy potom mapuje workload identity na konkrétne secrets alebo dynamic roles.

Controls:

- audience restriction,
- short token lifetime,
- namespace/repository/environment conditions,
- no wildcard subject mapping,
- explicit tenant boundary,
- audit actor identity.

## 7. Secret storage

Dobrý secrets store poskytuje:

- encryption at rest,
- authenticated a authorized API,
- versioning alebo lifecycle metadata,
- rotation/revocation integration,
- audit,
- high availability,
- backup/recovery,
- access separation,
- secure key hierarchy.

Encryption storage backendu sama nestačí, ak aplikácia alebo operátor má broad read access ku všetkým secrets.

## 8. Envelope encryption

Typický model:

```text
data secret
→ zašifrovaný data encryption keyom
→ data encryption key chránený root/master keyom
→ master key chránený KMS/HSM alebo seal mechanizmom
```

Výhody:

- key hierarchy,
- rotation master keyu bez re-encryption každého payloadu podľa implementácie,
- centralizovaný audit cryptographic operations.

Riziká:

- strata alebo zmazanie root/seal keyu,
- broad decrypt permissions,
- unavailable KMS/HSM,
- neoverený backup recovery.

## 9. Secret delivery patterns

### Environment variable

Výhody:

- jednoduché,
- široká compatibility.

Riziká:

- viditeľnosť v process environment,
- accidental dumps/logs,
- neaktualizuje sa bez reštartu,
- dedenie child processes,
- platform inspection access.

### File alebo mounted volume

Výhody:

- filesystem permissions,
- možnosť atomic update,
- application môže reloadnúť obsah.

Riziká:

- node/container filesystem exposure,
- backup/core dump,
- stale file,
- permission alebo symlink chyba.

### Sidecar alebo agent

Agent autentizuje workload a zapisuje/obnovuje secrets.

Výhody:

- oddelenie client logic,
- renewal,
- templates.

Riziká:

- shared filesystem trust,
- agent availability,
- race pri rotation,
- resource overhead.

### Direct API retrieval

Application volá secrets platformu.

Výhody:

- najaktuálnejší secret,
- explicitný lifecycle,
- no persistent local copy podľa designu.

Riziká:

- application complexity,
- runtime dependency,
- retry storm,
- cache a outage model.

## 10. Caching

Aplikácia typicky potrebuje krátkodobý cache.

Definuj:

- cache TTL,
- refresh-before-expiry,
- stale-on-error policy,
- memory protection,
- process restart behavior,
- revocation latency,
- zeroization limitations.

Fail-open s expired secretom môže porušiť authorization. Fail-closed môže spôsobiť outage. Rozhodnutie musí vychádzať z konkrétneho secret type-u a business risku.

## 11. Rotation

Rotation nahrádza credential alebo key novou hodnotou.

Bezpečný rotation flow:

```text
vytvor novú hodnotu/version
→ distribuuj ju consumerom
→ over successful use
→ prechodné overlap okno
→ revoke-ni starú hodnotu
→ monitoruj failures
→ odstráň starú hodnotu
```

Nie každý systém podporuje overlap. Vtedy potrebuješ coordinated cutover alebo dual credentials.

## 12. Rotation frequency

Frequency závisí od:

- secret lifetime,
- exposure surface,
- schopnosti revoke-nuť,
- automation maturity,
- compliance,
- credential type-u,
- incident response času.

Častá manuálna rotation môže zvyšovať outage risk. Automatizovaná krátka lifetime býva účinnejšia než kalendárna výmena dlhodobých secrets.

## 13. Revocation

Revocation musí byť technicky vynútiteľná.

Príklady:

- zmazanie database usera,
- disable API keyu,
- certificate revocation alebo short expiry,
- token denylist/session revoke,
- cloud role session policy,
- lease revoke v secrets platforme.

Zmena hodnoty v secrets store nestačí, ak starý credential zostáva platný v cieľovom systéme.

## 14. Lease

Lease je časovo obmedzený contract medzi secrets platformou a vydaným secretom.

Obsahuje typicky:

- lease ID,
- TTL,
- renewable flag,
- revocation behavior,
- owner/role context.

Application musí vedieť:

- kedy obnoviť,
- čo robiť pri renewal failure,
- ako graceful-ly prepnúť credential,
- ako ukončiť lease pri shutdown-e.

## 15. Versioning

Static secrets môžu mať versions.

Versioning umožňuje:

- controlled rollout,
- rollback po chybnej zmene,
- audit,
- recovery z accidental overwrite.

Riziko:

- staré versions zostávajú citlivé,
- broad read history access,
- rollback na compromised secret,
- retention bez deletion policy.

## 16. Secret classification

Pre každý secret dokumentuj:

- owner,
- purpose,
- environment/tenant,
- consumers,
- source system,
- credential type,
- lifetime,
- rotation/revocation method,
- compromise impact,
- storage/delivery pattern,
- recovery dependency.

Príklad:

```text
Secret: payments DB dynamic credential
Owner: Payments platform
Consumer: payments-api production
Lifetime: 30 min
Rotation: lease renewal/new credential
Revocation: revoke lease/database user
Blast radius: one workload role
Audit: workload identity + lease ID
```

## 17. Access control

Secrets authorization má byť jemnejšia než „môže čítať celý namespace“.

Policy dimensions:

- identity/workload,
- path alebo secret role,
- operation,
- environment,
- tenant,
- time,
- source/network context,
- approval.

Oddel:

- secret read,
- secret metadata/list,
- create/update,
- rotate,
- revoke,
- policy administration,
- audit access,
- root/recovery operations.

## 18. Listing risk

Aj zoznam názvov secrets môže odhaliť:

- services,
- environments,
- database names,
- customer identifiers,
- privileged integration.

Preto `list` a `read` môžu mať samostatné permissions a audit requirements.

## 19. Human access

Humans nemajú bežne čítať production application secrets.

Preferuj:

- break-glass alebo approved temporary access,
- generated credential namiesto zobrazenia shared secretu,
- session recording/audit,
- separation of duties,
- no clipboard/chat/ticket transfer,
- automatic expiry.

Operational debugging má byť možný bez disclosure secret value, napríklad cez metadata, version a health status.

## 20. CI/CD secrets

Riziká:

- forked pull requests,
- untrusted build scripts,
- third-party actions,
- self-hosted runner persistence,
- log output,
- artifact/cache leakage,
- environment promotion.

Controls:

- OIDC workload federation namiesto static cloud keys,
- environment approvals,
- protected branches/tags,
- short-lived tokens,
- masked logs, ale nie spoliehanie iba na masking,
- isolated runners,
- minimal scopes,
- no secrets pre untrusted PR context.

## 21. Kubernetes Secrets

Kubernetes Secret je API object pre citlivé dáta, ale nie plnohodnotná externá secrets-management platforma.

Dôležité:

- base64 encoding nie je encryption,
- Secret data môžu byť v etcd bez encryption-at-rest konfigurácie,
- RBAC `get`, `list` a `watch` predstavujú významný access,
- Pod, ktorý môže mountnuť Secret, môže hodnotu prečítať,
- environment variables sa neaktualizujú automaticky,
- mounted projected data majú vlastný update interval a application reload model.

## 22. Kubernetes security controls

- encryption at rest pre etcd,
- least-privilege RBAC,
- obmedziť `list/watch` Secrets,
- namespace/tenant isolation,
- audit accessu,
- admission policy,
- no Secret manifest v Git-e,
- restrict debug/exec/ephemeral-container access,
- secure node/kubelet boundary,
- external secrets integration podľa threat modelu.

Access vytvárať Pods v namespace môže byť nepriamy access k Secrets, ktoré možno mountnuť do workloadu.

## 23. External secrets synchronization

Controller môže synchronizovať hodnoty z externého secrets store do Kubernetes Secrets.

Výhody:

- central source,
- Git obsahuje reference, nie hodnotu,
- rotation workflow.

Riziká:

- secret sa stále materializuje v Kubernetes,
- controller má broad permissions,
- sync latency,
- stale value,
- deletion semantics,
- source outage,
- tenant crossing.

Alternatíva je runtime mount alebo direct retrieval bez persistent Kubernetes Secretu.

## 24. CSI a volume-based retrieval

Secret Store CSI pattern môže mountovať external secret do Pod filesystemu.

Vyhodnoť:

- či sa vytvára aj Kubernetes Secret,
- node plugin trust,
- rotation update,
- application reload,
- filesystem permissions,
- node compromise,
- provider availability.

Volume mount nevyrieši secret exposure v application memory.

## 25. HashiCorp Vault model

Vault je identity-based secrets a encryption management system.

Základný flow:

```text
client/workload
→ auth method
→ Vault identity a policies
→ client token
→ secrets engine
→ static secret, dynamic credential, certificate alebo crypto operation
→ lease/revocation
→ audit devices
```

Vault centralizuje access control a audit, ale jeho dostupnosť a recovery sa stávajú kritickou platform dependency.

## 26. Vault auth methods

Auth method overuje external identity a vydáva Vault token s policies.

Príklady:

- Kubernetes,
- cloud IAM,
- OIDC/JWT,
- AppRole,
- TLS certificates,
- LDAP/userpass pre vybrané use cases.

Preferuj identity, ktorú platforma vytvára a rotuje automaticky.

AppRole `role_id + secret_id` stále vytvára bootstrap/distribution problém; nie je automaticky lepší než iný static credential.

## 27. Vault policies

Vault policy povoľuje capabilities nad paths.

Príklady capabilities:

- `read`,
- `create`,
- `update`,
- `delete`,
- `list`,
- `sudo` pre chránené operations.

Policy má byť viazaná na role/use case, nie na každú individual instance bez potreby.

Rozlišuj:

- identity group mapping,
- auth role constraints,
- token policy,
- secrets-engine path semantics.

## 28. Vault token

Vault token je bearer credential s:

- policies,
- TTL,
- renewability,
- parent-child lifecycle,
- optional use limits,
- accessorom pre audit/revocation.

Root token obchádza bežné policy restrictions a nemá sa používať na application operations.

Root token po inicializácii bezpečne zruš a regeneruj iba cez kontrolovaný quorum proces pri výnimočnej potrebe.

## 29. Vault secrets engines

Secrets engine môže:

- ukladať static data,
- generovať dynamic credentials,
- vydávať certificates,
- vykonávať encryption/signing,
- integrovať external systems.

Engine je mountnutý na path a má vlastnú configuration/lifecycle.

Príklady:

- KV,
- database,
- cloud secrets,
- PKI,
- Transit,
- SSH.

## 30. KV secrets engine

KV je vhodný pre static secrets, ktoré nemožno dynamicky generovať.

KV v2 pridáva versioning a check-and-set semantics podľa configuration.

Controls:

- obmedziť history access,
- retention/deletion,
- metadata privacy,
- rotation mimo samotného storage,
- no broad prefix read,
- no secret values v Terraform state alebo CI logs.

KV uloženie samo nezmení credential v cieľovom systéme.

## 31. Dynamic database credentials

Database secrets engine môže vytvoriť per-client database usera s TTL.

```text
workload sa autentizuje vo Vault
→ požiada database role
→ Vault vytvorí unique DB credential
→ workload používa credential počas lease
→ Vault ho po expiry/revocation odstráni
```

Výhody:

- attribution,
- krátka lifetime,
- no shared password,
- automatic revocation.

Riziká:

- database admin credential vo Vault configuration,
- creation/revocation failure,
- connection pool a rotation,
- database outage,
- orphan users.

## 32. Static database roles

Niektoré systémy vyžadujú fixed username, ktorému Vault rotuje password.

Potrebný je coordinated model:

- Vault pozná authoritative credential,
- consumers používajú aktuálnu hodnotu,
- connection pools sa obnovia,
- old password sa zneplatní,
- rotation failure sa monitoruje.

Static role má väčší shared blast radius než dynamic per-client credential.

## 33. PKI secrets engine

PKI engine vydáva krátkodobé certificates podľa role policy.

Controls:

- allowed domains/SANs,
- max TTL,
- key type/size,
- issuer hierarchy,
- CRL/OCSP podľa ecosystemu,
- certificate renewal,
- private-key delivery,
- CA key protection.

Short-lived certificates môžu znížiť závislosť na revocation, ale vyžadujú spoľahlivé automated renewal.

## 34. Transit secrets engine

Transit poskytuje cryptographic operations bez vrátenia underlying encryption keyu clientovi.

Use cases:

- encrypt/decrypt application data,
- signing/verification,
- HMAC,
- key rotation.

Application stále musí:

- chrániť plaintext v memory,
- autorizovať cryptographic operation,
- viazať ciphertext na context podľa designu,
- riešiť Vault availability a latency.

Transit nie je generic storage engine pre application data.

## 35. Seal a unseal

Vault storage data sú chránené encryption barrierom.

Pri sealed stave Vault nemôže dešifrovať storage a neposkytuje bežné secrets operations.

Unseal modely:

- Shamir shares,
- auto unseal cez cloud KMS/HSM alebo transit seal podľa edition/configuration.

Auto unseal znižuje manuálnu prevádzku, ale vytvára strict dependency na seal mechanism a jeho key lifecycle.

Trvalá strata seal keyu môže znemožniť recovery aj z backupu.

## 36. Shamir shares a recovery keys

Shamir model rozdeľuje unseal material medzi viac shares s thresholdom.

Controls:

- rôzni custodians,
- oddelené secure storage,
- no sharing v chat/email,
- pravidelné recovery procedure testy,
- rekey pri zmene custodianov.

Pri auto unseal sa recovery keys používajú pre vybrané quorum operations, ale nedokážu nahradiť trvalo stratený auto-unseal key.

## 37. Vault audit devices

Audit devices zaznamenávajú Vault API requests a responses s ochranou citlivých values podľa configuration.

Dôležité operational behavior:

- audit musí byť explicitne zapnutý,
- používať aspoň dve independent audit destinations,
- monitorovať write failures,
- audit logs chrániť proti zmene a broad read accessu.

Ak sú audit devices nakonfigurované a Vault nedokáže zapísať request aspoň do jedného dostupného device-u, môže request odmietnuť. Audit je preto zároveň availability dependency.

## 38. Vault HA

Production Vault potrebuje:

- redundant nodes,
- supported HA storage/Integrated Storage,
- load balancer alebo service discovery,
- active/standby model,
- TLS,
- health-check semantics,
- unseal model,
- backup a restore,
- upgrade procedure.

HA nerieši:

- logical deletion,
- compromised policies,
- seal key loss,
- region-wide failure,
- invalid backup.

## 39. Integrated Storage a snapshots

Pri Raft Integrated Storage potrebuj:

- pravidelné snapshots,
- external protected storage,
- encryption a access control,
- restore testing,
- cluster identity/rejoin procedure,
- seal dependency recovery.

Backup bez dostupného seal mechanismu nemusí byť použiteľný.

## 40. Disaster recovery

Definuj:

- RPO/RTO,
- seal/KMS availability,
- storage backup alebo replication,
- DNS/load-balancer cutover,
- auth-method dependencies,
- external database/cloud systems,
- audit continuity,
- application behavior počas Vault outage.

Recovery test musí zahŕňať reálne vydanie alebo retrieval test secretu, nie iba štart processu.

## 41. Availability a fail behavior

Pri secrets-platform outage môže application:

- použiť ešte platný cached credential,
- pokračovať do jeho expiry,
- odmietnuť nové requests,
- prejsť do read-only/degraded mode,
- zastaviť startup.

Rozhodnutie musí byť explicitné.

Neobmedzený fallback na starý secret neguje rotation/revocation. Okamžitý fail-closed môže vytvoriť veľký outage.

## 42. Secret rotation v aplikácii

Aplikácia musí podporovať rotation bez permanentného outage-u.

Patterns:

- refresh pred expiry,
- dual credential overlap,
- atomic file replacement,
- connection-pool reconnect,
- hot reload,
- graceful restart,
- version-aware cache.

Secret platforma nemôže napraviť application, ktorá načíta credential iba pri prvom štarte a nikdy ho neobnoví.

## 43. Logging a telemetry

Nikdy neloguj:

- secret value,
- bearer token,
- private key,
- password,
- unseal/recovery share,
- database connection string s credentials.

Sleduj metadata:

- authentication success/failure,
- policy deny,
- secret path/role v bezpečnej forme,
- issuance/renewal/revocation,
- lease expiry,
- rotation failure,
- audit-device health,
- seal status,
- request latency/errors,
- cache refresh.

## 44. Secret scanning

Scanning hľadá secrets v:

- Git history,
- working tree,
- container images,
- build logs,
- artifacts,
- packages,
- tickets a documentation.

Detection nie je remediation.

Pri náleze:

1. revoke-ni credential,
2. rotate-ni závislosti,
3. analyzuj použitie,
4. odstráň hodnotu z aktívnych sources,
5. uprav history iba podľa potreby,
6. oprav distribution process,
7. pridaj prevention guardrail.

## 45. Git a encrypted-secret patterns

Plaintext secret nepatrí do Git-u ani v private repository.

Encrypted-secret manifest môže byť bezpečný iba ak:

- encryption keys sú oddelené,
- recipient policy je správna,
- decrypt access je auditovaný,
- rotation a re-encryption fungujú,
- CI neodhaľuje plaintext,
- metadata neprezrádzajú citlivé informácie.

Git history zachová všetky encrypted versions; compromise decryption keyu môže spätne odhaliť históriu.

## 46. Terraform a state

Terraform state môže obsahovať secret values aj keď sú inputs označené ako sensitive.

Controls:

- encrypted remote backend,
- strict access,
- state locking,
- audit,
- no output secretov,
- provider/resource semantics review,
- preferovať references alebo dynamic retrieval.

`sensitive = true` primárne obmedzuje zobrazenie, nie storage v state.

## 47. Container images

Secret nesmie byť:

- `ARG`/`ENV` baked do image,
- kopírovaný do layeru a neskôr zmazaný,
- uložený v build cache,
- súčasťou package manager configu vo final image.

Použi BuildKit secret mounts alebo platform-specific ephemeral build credential a over image history/layers.

Build secret môže stále uniknúť, ak ho build command zapíše do artifactu alebo logu.

## 48. Secret compromise response

```text
identifikovať secret a typ
→ zastaviť ďalšie použitie
→ revoke/rotate v authoritative systeme
→ identifikovať consumers a sessions
→ zachovať audit evidence
→ analyzovať access počas exposure window
→ obnoviť workloads s novým credentialom
→ overiť starý credential ako neplatný
→ odstrániť source leakage
→ pridať guardrails
```

Priority je revocation, nie iba odstránenie zo súboru.

## 49. Troubleshooting retrieval

```text
workload identity existuje?
→ auth token/certificate platný a správne audience?
→ secrets endpoint DNS/TLS/network?
→ auth method role mapping?
→ policy/path/capability?
→ secret/version/role existuje?
→ lease/quota/rate limit?
→ agent/CSI/controller sync?
→ file/env delivery a permissions?
→ application reload/cache?
```

## 50. Typické chyby

### Permission denied

Over identity, auth role constraints, policies, namespace/tenant, path a operation.

### Secret not found

Over mount/path/version, environment, soft deletion, sync a typo. Nezamieňaj authorization deny s missing resource podľa API behavior.

### Rotation prebehla, aplikácia zlyhala

Application drží starý connection pool, cache alebo file descriptor.

### Dynamic credential expired

Renewal neprebehol, workload stratil identity alebo agent/backend bol nedostupný.

### Kubernetes Secret sa nezmenil v procese

Environment variable sa neaktualizuje; mounted volume potrebuje update a application reload.

### Vault sealed

Over seal mechanism, KMS/HSM availability, key permissions, recovery process a node state.

### Vault requesty zlyhávajú pri audit outage

Over všetky audit devices, filesystem, syslog/socket destination, permissions a backpressure.

## 51. Metrics a SLO

Sleduj:

- authentication/token issuance success,
- secret retrieval latency/error rate,
- lease renewal failures,
- secrets blízko expiry,
- rotation success/failure,
- revocation latency,
- audit-device health,
- sealed nodes,
- active/standby health,
- storage latency,
- dynamic credential creation/revocation,
- stale sync age,
- cache age.

Secret platforma potrebuje vlastný availability a security SLO, ale secrets values nesmú byť metric labels.

## 52. Governance

Organizácia potrebuje:

- approved secret stores,
- ownership model,
- naming/path conventions,
- dynamic-secret preference,
- maximum lifetimes,
- rotation SLAs,
- break-glass process,
- secret scanning,
- exception process,
- incident playbook,
- decommission lifecycle.

Bez governance vznikne viac paralelných stores a nejasná autorita.

## 53. Anti-patterny

### Secret v Git-e s plánom „neskôr ho zmeníme“

History a clones už vytvorili exposure.

### Base64 ako encryption

Encoding neposkytuje confidentiality.

### Jeden shared production password

Chýba attribution a blast radius je veľký.

### Rotation bez revocation

Stará hodnota zostáva použiteľná.

### Secret manager ako single point of failure bez cache/fail modelu

Výpadok platformy zastaví všetky workloads.

### Neobmedzený cache starého credentialu

Revocation a expiry strácajú význam.

### Root/admin token pre aplikáciu

Compromise poskytne platform-wide access.

### Secret value v Terraform outpute alebo CI logu

Masking nemusí zachytiť všetky reprezentácie.

### Backup bez seal/key recovery

Encrypted storage je prakticky neobnoviteľné.

### Human copy-paste do aplikácie

Chýba auditovaný a repeatable delivery lifecycle.

## 54. Kontrolné otázky

1. Čo všetko môže byť secret?
2. Ako sa líši static a dynamic secret?
3. Čo je secret zero a ako ho rieši workload identity?
4. Aké sú výhody a riziká environment variable, file, agent a API delivery?
5. Aký je rozdiel medzi rotation a revocation?
6. Čo je lease a ako ho application obnovuje?
7. Prečo Kubernetes Secret nie je automaticky šifrovaný bezpečný vault?
8. Ako funguje Vault auth method, policy, token a secrets engine?
9. Čo znamená seal/unseal a akú dependency vytvára auto unseal?
10. Prečo Vault audit môže ovplyvniť availability?
11. Ako reagovať na secret nájdený v Git history?
12. Ako testovať secrets-platform disaster recovery?

## Glossary impact

Relevantné pojmy: secret, secrets management, secret lifecycle, static secret, dynamic secret, secret zero, workload identity, secret delivery, secret cache, secret rotation, secret revocation, lease, secret versioning, secret classification, external secrets synchronization, Secret Store CSI, Vault auth method, Vault policy, Vault token, secrets engine, KV v2, dynamic database credential, PKI secrets engine, Transit secrets engine, seal, unseal, Shamir shares, recovery keys, auto unseal, encryption barrier, audit device, Integrated Storage, secret scanning a break-glass secret access.

## Primárne zdroje

- [NIST SP 800-57 Part 1 Rev. 5 — Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Good practices for Kubernetes Secrets](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)
- [HashiCorp Vault documentation](https://developer.hashicorp.com/vault/docs)
- [How Vault works](https://developer.hashicorp.com/vault/docs/about-vault/how-vault-works)
- [Vault secrets engines](https://developer.hashicorp.com/vault/docs/secrets)
- [Vault database secrets engine](https://developer.hashicorp.com/vault/docs/secrets/databases)
- [Vault seal and unseal](https://developer.hashicorp.com/vault/docs/concepts/seal)
- [Vault audit devices](https://developer.hashicorp.com/vault/docs/audit)
