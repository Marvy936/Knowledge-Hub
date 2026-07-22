# Secrets management

Secrets management je disciplína bezpečného vytvárania, vydávania, distribúcie, používania, obnovovania, rotácie, revocation, auditovania a odstránenia citlivých credentials a cryptographic materialu. Secret nie je iba password. Je to každý údaj alebo capability, ktorého získanie umožňuje impersonation, neautorizovaný access, decryption, signing alebo privileged operation.

Cieľom nie je iba uložiť secret v šifrovanej database. Dobrý systém znižuje počet držiteľov, lifetime, počet copies a blast radius compromise-u. Ideálny workload nepozná permanentný shared credential; preukáže runtime identity a dostane krátkodobý, presne scoped credential s auditovateľným lifecycle-om.

```text
workload alebo human identity
→ authentication voči secrets platforme
→ authorization podľa role, resource-u a contextu
→ retrieval alebo dynamic issuance
→ secure delivery
→ bounded use a cache
→ renewal, rotation alebo revocation
→ audit a incident evidence
→ recovery, retention a destruction
```

## 1. Čo je secret a prečo je to capability

Secret má hodnotu preto, že cieľový systém mu dôveruje. Database password umožňuje vytvoriť authenticated session. API token môže autorizovať operation. Private key môže podpisovať alebo decryptovať. Recovery code môže obísť primárny authenticator.

Príklady secrets:

- database password alebo connection credential;
- API key, webhook secret alebo package-registry token;
- OAuth client secret alebo refresh token;
- cloud access key alebo temporary session credential;
- SSH private key alebo machine certificate private key;
- TLS, signing alebo encryption private key;
- Kubernetes ServiceAccount token;
- bootstrap token, unseal share alebo recovery code.

Nie každý citlivý údaj má rovnaké semantics. Bearer token môže použiť každý držiteľ bez ďalšieho proof-of-possession. Encryption key poskytuje cryptographic capability. Recovery material môže obísť bežný login. Classification preto musí zachytiť typ a cieľový authorization model, nie iba label `secret`.

## 2. Secret oproti identity

Identity odpovedá, kto alebo čo actor je. Secret je jeden z možných authenticatorov alebo capabilities, ktorými identity preukazuje alebo vykonáva operation.

Shared password často splýva s identity: všetky instances sa prihlasujú rovnakým menom a audit nevie rozlíšiť callerov. Workload identity oddelí stable identity od krátkodobého credentialu. Platforma overí Pod, VM alebo CI job a následne mu vydá scoped token alebo database usera.

Tento rozdiel umožňuje revoke-nuť jednu instance, obmedziť audience a zachovať attribution bez distribúcie permanentného secretu.

## 3. Secret lifecycle

Secret lifecycle nezačína uložením hodnoty. Začína rozhodnutím, prečo credential existuje, kto ho vlastní a aký cieľový systém mu dôveruje.

```text
purpose a classification
→ generation alebo import
→ registration v authoritative systéme
→ storage a access policy
→ issuance alebo distribution
→ use a caching
→ renewal alebo rotation
→ revocation
→ retention alebo archival podľa potreby
→ secure destruction
```

Každá fáza potrebuje ownera, audit evidence, failure model a recovery. Ak organization vie secret vytvoriť, ale nevie ho revoke-nuť alebo nájsť všetkých consumers, lifecycle je neúplný.

## 4. Secret classification

Pre každý secret dokumentuj:

- purpose a cieľový systém;
- authoritative ownera;
- human alebo workload consumers;
- environment, tenant a data scope;
- credential semantics — bearer, password, private key, recovery material;
- lifetime a renewal model;
- rotation a revocation mechanism;
- storage a delivery pattern;
- compromise impact a blast radius;
- recovery dependencies;
- logging a audit requirements.

Príklad:

```text
Secret: payments database dynamic credential
Owner: Payments platform
Consumer: payments-api production workload identity
Lifetime: 30 minút
Renewal: nový credential pred expiry
Revocation: Vault lease revoke + database user deletion
Blast radius: jedna workload role a krátke časové okno
Audit: workload identity, Vault token accessor, lease ID, DB username
```

Classification nie je administratívna tabuľka. Určuje, či je prijateľná environment variable, aká cache TTL je bezpečná a čo má incident tím revoke-nuť.

## 5. Static secret

Static secret existuje dlhšie a používa sa opakovane. Typickým príkladom je fixed API key, shared database password alebo manually issued long-lived certificate.

Static credential je jednoduchý pre legacy systems, ale má vysoký operational cost:

- kopíruje sa medzi consumers a environments;
- ownership sa časom stráca;
- rotation vyžaduje coordinated update;
- old copies ostávajú v files, backups alebo memory dumps;
- audit často ukazuje iba shared account;
- compromise window môže trvať mesiace.

Ak cieľový systém nevie vytvoriť dynamic credentials, zníž risk krátkou rotation, úzkym scope-om, oddelenými values per consumer a automatizovanou distribution.

## 6. Dynamic secret

Dynamic secret sa generuje on demand pre konkrétnu identity, role alebo workload. Secrets platforma vytvorí temporary database usera, cloud credential alebo certificate a pripojí mu TTL a revocation lifecycle.

```text
workload sa autentizuje
→ policy povolí konkrétnu dynamic role
→ platforma vytvorí unique credential v target systéme
→ credential dostane lease
→ workload ho používa počas TTL
→ platforma ho renew-ne alebo revoke-ne
```

Výhody sú per-client attribution, kratší compromise interval a menší shared blast radius. Dynamic secret však vytvára runtime dependency na issuer-a a target system. Ak revocation plugin zlyhá, orphan credential môže zostať platný.

## 7. Secret zero

Secret zero je prvotný trust anchor, ktorým workload získa ďalšie secrets. Ak aplikácia potrebuje Vault token, musí najprv preukázať identity Vault auth methodu. Ak tento bootstrap rieši permanentným tokenom v image, problém sa iba presunul.

Vhodné bootstrap sources sú:

- cloud instance alebo task identity;
- Kubernetes projected ServiceAccount token;
- CI OIDC token;
- hardware-backed machine identity;
- short-lived mTLS certificate;
- SPIFFE workload identity;
- one-time operator enrollment.

Secret zero sa nedá úplne odstrániť; dá sa presunúť do dôveryhodnejšej platform boundary, skrátiť jeho lifetime a viazať ho na runtime context.

## 8. Workload identity ako bootstrap

Workload identity je overiteľná identity running software-u nezávislá od shared passwordu. Platforma môže viazať credential na VM instance, Kubernetes ServiceAccount, CI repository/workflow alebo SPIFFE selector.

Secrets platforma následne mapuje identity na secret paths alebo dynamic roles:

```text
identity: payments-api v production namespace
→ môže požiadať iba database role payments-readwrite
→ nemôže listovať celý KV namespace
→ token a DB credential majú krátku TTL
```

Trust policy musí validovať issuer, audience, subject a environment. Wildcard mapping `system:serviceaccount:*:*` by zmenil workload identity na cluster-wide shared trust.

## 9. Human access

Humans by bežne nemali čítať production application secrets. Debugging sa má opierať o metadata, health, version, lease a authorization evidence, nie o copy-paste hodnoty.

Keď human access musí existovať, preferuj:

- just-in-time approval;
- vygenerovaný temporary credential namiesto zobrazenia shared value;
- session recording alebo detailed audit;
- oddelené break-glass identities;
- automatic expiry;
- zákaz prenosu cez chat, ticket alebo clipboard workflow;
- post-use rotation pri disclosure static secretu.

„Admin môže vidieť všetko“ je veľká compromise boundary a ničí attribution medzi application a operator accessom.

## 10. Secret storage

Secrets store má poskytovať authenticated API, encryption at rest, version alebo lease metadata, least-privilege authorization, audit, high availability, backup a recovery.

Storage encryption chráni proti disk alebo database-only compromise. Nechráni pred callerom s broad `read` permission ani pred compromised application, ktorá smie secret oprávnene získať.

Dôležitá je separation:

```text
secret ciphertext v storage
→ encryption barrier alebo DEK
→ root/seal key v oddelenej KMS/HSM boundary
→ access cez identity a policy
```

Storage backend, encryption keys, API policies a audit logs nemajú byť pod kontrolou jednej neobmedzenej identity.

## 11. Envelope encryption v secrets platforme

Secrets platforma typicky šifruje stored payloads pomocou data keys a tieto keys chráni root alebo seal keyom. Root key môže byť ďalej chránený KMS/HSM alebo Shamir shares podľa produktu.

Envelope model umožňuje rotate vyššiu key layer bez decrypt/re-encrypt každého payloadu. Vytvára však strict recovery dependency: backup ciphertext bez dostupného root/seal mechanismu je nepoužiteľný.

Broad decrypt permission alebo compromise unsealed core-u môže sprístupniť mnoho secrets naraz. Encryption hierarchy preto musí byť kombinovaná s API authorization a runtime isolation.

## 12. Delivery pattern: environment variable

Environment variable je široko podporovaný spôsob delivery. Orchestrator alebo process manager vloží value pri štarte procesu.

Výhodou je jednoduchosť. Nevýhody:

- secret môže byť viditeľný cez process inspection, crash dump alebo debug output;
- child process ho zdedí;
- value sa typicky neaktualizuje bez restartu;
- accidental environment dump unikne celý set;
- application nerozlišuje version ani lease metadata.

Environment je vhodnejší pre krátko žijúci process a low-complexity rotation, nie pre credential s častou renewal požiadavkou.

## 13. Delivery pattern: file alebo mounted volume

Secret uložený ako file môže používať filesystem permissions a atomic replacement. Application môže sledovať zmenu a reloadnúť credential bez restartu.

Risk boundary sa presunie na node/container filesystem. Pod alebo process s read accessom file získa plaintext. Backup, core dump, debug shell alebo symlink/permission chyba môže value odhaliť.

Atomic update často používa nový file a rename alebo symlink switch. Application, ktorá drží otvorený file descriptor, nemusí novú hodnotu načítať. Rotation preto potrebuje explicitný reload contract.

## 14. Delivery pattern: sidecar alebo node agent

Agent autentizuje workload, získava secrets, obnovuje leases a zapisuje templates alebo files. Application nemusí implementovať celý client protocol.

Agent prináša renewal a centralizovanú logiku, ale vytvára shared trust boundary:

- application a agent často zdieľajú filesystem;
- agent outage môže zablokovať refresh;
- race pri file replacement môže spôsobiť partial read;
- misconfigured template môže zalogovať secret;
- node-level agent má veľký blast radius pri compromise.

Policy musí overiť identity konkrétneho workloadu, nie iba fakt, že request prichádza z trusted node.

## 15. Delivery pattern: direct API retrieval

Application sa autentizuje voči secrets platforme a volá jej API. Dostane secret value, lease ID, TTL a metadata a môže riadiť refresh presne podľa lifecycle-u.

Tento pattern minimalizuje persistent local copy, ale pridáva application complexity a runtime dependency. Client potrebuje timeouts, retry s backoffom, cache, renewal, revocation response a observability.

Naivný startup, pri ktorom stovky replicas naraz volajú Vault, môže počas rollout-u vytvoriť retry storm. Jitter, agent cache alebo staged rollout znižujú thundering herd.

## 16. Cache a plaintext lifetime

Application zvyčajne cache-uje secret v memory, pretože volať secrets platformu pri každom requeste je drahé a zvyšuje availability coupling.

Cache policy definuje:

- TTL a refresh-before-expiry;
- jitter;
- behavior pri refresh failure;
- maximum stale interval;
- revocation latency;
- process restart semantics;
- memory exposure a dump policy;
- version-aware replacement.

Fail-open s neobmedzene starým credentialom neguje expiry a revocation. Fail-closed môže spôsobiť outage. Napríklad read-only service môže pokračovať s ešte platným cached DB credentialom, ale signing service môže pri issuer outage odmietnuť nové operations.

## 17. Rotation oproti revocation

Rotation nahradí credential novou hodnotou. Revocation technicky zneplatní starú hodnotu v authoritative target systéme.

```text
rotation
→ create new credential
→ update consumers
→ verify new use

revocation
→ old credential už target system neprijme
```

Zmena value v secret store nie je revocation, ak starý database password, API key alebo token zostáva platný. Bezpečný lifecycle potrebuje oba kroky.

## 18. Bezpečný rotation flow

Rotation bez outage-u typicky používa overlap:

```text
vytvoriť novú value/version
→ distribuovať ju consumers
→ overiť successful authentication
→ nechať krátke overlap okno
→ revoke-nuť old credential
→ monitorovať failures
→ odstrániť old value a history podľa retention
```

Niektoré target systems podporujú dva active keys; iné vyžadujú coordinated cutover. Application connection pools musia otvoriť nové sessions s novým credentialom, pretože existing database connections môžu zostať validné aj po password change.

## 19. Rotation frequency

Frequency závisí od lifetime, exposure, revocation capability, automation maturity a impactu compromise-u. Častá manuálna výmena môže vytvárať outages a viesť k obchádzaniu processu.

Automatizovaný 30-minútový dynamic credential je často bezpečnejší než 90-dňový calendar rotation shared passwordu. Krátka lifetime však vyžaduje spoľahlivý issuer a renewal.

Rotation interval nie je jediná kontrola. Credential s broad permissions a 15-minútovou TTL môže počas compromise-u stále spôsobiť veľký impact.

## 20. Lease

Lease je časovo obmedzený contract medzi secrets platformou a vydaným dynamic secretom. Obsahuje lease ID, TTL, renewability a revocation behavior.

Application musí credential renew-nuť alebo nahradiť pred expiry. Po expiry Vault môže revoke-nuť target credential; consumer už nemôže predpokladať, že je validný.

```text
issued credential + lease_id + TTL
→ refresh/renew pred expiry
→ success: predĺžiť alebo vymeniť
→ failure: prejsť na nový credential alebo degraded/fail state
```

Vault KV static secret nemá rovnaký dynamic lease lifecycle ako database credential. TTL metadata v response nemusí znamenať automatickú revocation stored value.

## 21. Versioning static secrets

Versioning umožňuje controlled rollout, recovery z accidental overwrite a audit. KV v2 vo Vault-e napríklad uchováva versions a metadata.

Old versions zostávajú citlivé. Broad history read zväčšuje compromise scope a rollback môže znovu aktivovať compromised value.

Version retention a deletion policy musí byť prepojená s target credential lifecycle-om. Odstránenie version zo store neznamená zneplatnenie credentialu v external systeme.

## 22. Least-privilege authorization

Secrets authorization má rozlišovať identity, operation, resource/path, environment, tenant a context. Permission „read celý namespace“ je často príliš broad.

Oddel capabilities:

- read current value;
- list names alebo metadata;
- read historical versions;
- create/update;
- rotate target credential;
- revoke lease alebo credential;
- meniť policy;
- čítať audit;
- vykonávať root/recovery operations.

Workload, ktorý potrebuje jeden dynamic database role, nemá vedieť listovať všetky secrets ani meniť engine configuration.

## 23. Listing risk

Secret names a paths môžu prezradiť services, customers, environments, databases a privileged integrations. Metadata sú preto citlivé aj bez values.

`list` a `watch` môžu mať iné semantics než `read`, ale v niektorých APIs odhalia values alebo veľký inventory. Policy a audit majú vychádzať zo skutočného API behavioru.

Naming convention nemá obsahovať unnecessary customer identifiers alebo secret values.

## 24. CI/CD secrets

CI job vykonáva repository-controlled code a často používa third-party actions. Je preto high-risk secret consumer.

Untrusted pull-request context nesmie dostať production cloud key, registry push token ani signing identity. Preferred model je OIDC federation:

```text
protected workflow
→ short-lived OIDC assertion
→ cloud/Vault trust policy overí repository, workflow, branch a environment
→ vydá scoped temporary credential
```

Self-hosted runner persistence, caches, logs a artifacts sú exposure paths. Masking je defense in depth, nie guarantee; encoded alebo transformed value môže filter obísť.

## 25. Build secrets

Build potrebuje niekedy private package token alebo license credential. Secret nesmie byť uložený v Dockerfile `ARG`, `ENV`, image layer alebo build cache.

BuildKit secret mount sprístupní value iba počas konkrétneho `RUN` step-u bez automatického uloženia do layeru. Build command ho však stále môže skopírovať do outputu alebo logu.

Release job s high-impact credentials má používať trusted source a isolated runner. Untrusted build code nemá dostať signing alebo production publish capability.

## 26. Git a encrypted-secret patterns

Plaintext secret nepatrí do Git-u ani v private repository. History, forks, clones, caches a backups vytvárajú durable copies.

Encrypted-secret manifest môže byť prijateľný, ak:

- recipients a encryption keys sú oddelené od repository;
- decrypt access je least-privilege a auditovaný;
- CI nepublikuje plaintext;
- key rotation a re-encryption fungujú;
- old encrypted history má posúdený compromise impact;
- metadata neprezrádzajú citlivý context.

Compromise decryption keyu môže spätne odhaliť všetky historical encrypted values v Git history. Rotation target credentialu a rotation encryption recipient keyu sú samostatné operácie.

## 27. Terraform state

Terraform state môže obsahovať secrets aj keď input alebo output je označený `sensitive`. `sensitive` primárne obmedzuje CLI/UI display, nie storage.

State potrebuje encrypted remote backend, strict IAM, locking, versioning, audit a secure backup. Preferuj resources, ktoré ukladajú reference alebo konfigurujú dynamic retrieval namiesto kopírovania secret value do state.

Provider schema určuje, ktoré attributes sa persistujú. Plan JSON a CI artifacts môžu obsahovať rovnaké values ako state a potrebujú rovnakú ochranu.

## 28. Container images

Secret pridaný do image layeru zostáva v content-addressed history aj po neskoršom `rm`. Každý s accessom k layeru ho môže extrahovať.

Neukladaj secrets do:

- Dockerfile `ARG` alebo `ENV` určeného pre secret;
- copied configuration vo build context-e;
- package-manager credentials vo final image;
- build cache alebo exported layer;
- image labels alebo provenance parameters.

Po leakage treba credential revoke-nuť a rebuildnúť image; samotné odstránenie file-u z latest layeru nestačí.

## 29. Secret scanning

Secret scanner hľadá high-entropy values, known token formats, private-key headers alebo verified credentials v Git history, working tree, images, logs, packages a tickets.

Detection nie je remediation. Pri náleze:

```text
classify secret a authoritative target
→ revoke alebo disable
→ identify consumers/sessions
→ preserve evidence a exposure window
→ rotate dependent systems
→ remove active source leakage
→ rewrite history iba keď má operational význam
→ add prevention a tests
```

Priority je zneplatnenie capability. Delete commit-u bez revocation necháva credential použiteľný.

## 30. Kubernetes Secret object

Kubernetes Secret je namespaced API object určený na citlivé configuration data. Poskytuje API semantics, RBAC, projection do Pods a object lifecycle, ale nie je automaticky plnohodnotný external secrets manager.

Values v `.data` sú base64 encoded, nie encrypted. Bez EncryptionConfiguration sú Secret objects v etcd uložené bez additional encryption at rest. Kubernetes dokumentácia preto odporúča encryption at rest a obmedzenie `get`, `list` a `watch` permissions.

Secret môže byť typu Opaque, TLS, Docker config alebo ServiceAccount token podľa schema/use case-u. Type neposkytuje automatickú rotation ani target-system revocation.

## 31. Kubernetes indirect access paths

Permission vytvoriť Pod v namespace môže byť nepriamy access k Secrets, ktoré workload smie mountnúť. `pods/exec`, ephemeral containers, privileged node access alebo kubelet APIs môžu odhaliť environment, files alebo memory.

Preto Secret security nemožno posúdiť iba cez direct `get secrets` RBAC. Threat model zahŕňa:

- Pod creation a ServiceAccount use;
- exec/debug permissions;
- node a kubelet compromise;
- CSI/provider permissions;
- admission controls;
- namespace boundaries;
- backup a etcd access.

Namespace nie je strong tenant boundary, ak administrators alebo node workloads sú shared a broad.

## 32. Kubernetes delivery semantics

Environment variable sa načíta pri container startup-e a neskorší Secret update sa do existing processu nepremietne.

Secret volume je projected do Pod filesystemu. Kubelet aktualizuje mounted content podľa cache/watch/update semantics, ale application musí file znovu načítať. `subPath` mount nemá rovnaké automatic update behavior ako celý projected volume.

Rotation je preto end-to-end contract:

```text
source secret update
→ Kubernetes object alebo CSI mount update
→ file/symlink change
→ application reload alebo restart
→ new outbound connection/session
→ old credential revocation
```

## 33. Kubernetes controls

Defense in depth zahŕňa:

- etcd encryption at rest, ideálne s KMS boundary podľa threat modelu;
- least-privilege RBAC a obmedzenie `list/watch`;
- admission policy pre unsafe Pod mounts a privileged debug;
- secure ServiceAccounts a projected short-lived tokens;
- audit API accessu;
- node hardening a kubelet protection;
- namespace/tenant isolation;
- external secret store alebo workload identity pre high-impact credentials;
- no plaintext manifests v Git-e.

Encryption at rest nechráni authorized API read ani mounted plaintext v Pod-e.

## 34. External Secrets Operator pattern

External Secrets Operator — ESO — reconciliuje declarative `ExternalSecret` resource s external providerom a vytvorí alebo aktualizuje Kubernetes Secret.

```text
ExternalSecret reference
→ operator autentizuje provider identity
→ načíta remote keys
→ transformuje/template-ne data
→ vytvorí alebo aktualizuje target Secret
→ opakuje refresh podľa policy/interval-u
```

Výhodou je central external source a Git bez values. Secret sa však stále materializuje v Kubernetes API, etcd a Pod projections.

Operator má broad provider aj cluster permissions a stáva sa high-impact controllerom. Potrebuje tenant isolation, scoped SecretStore/ClusterSecretStore policy, refresh/deletion semantics, metrics a provider outage model.

## 35. ESO refresh, ownership a deletion

Refresh policy určuje, kedy controller znovu načíta remote value. Refresh interval vytvára maximum expected staleness, ale actual update závisí aj od reconciliation health a provider availability.

Creation/ownership policy určuje, kto vlastní target Secret a či sa smie meniť alebo mazať. Deletion policy určuje behavior, keď remote key zmizne.

Unsafe default môže zmazať production Secret po accidental provider deletion alebo naopak ponechať stale credential navždy. Policy musí zodpovedať target-system revocation a application reload modelu.

## 36. Secrets Store CSI Driver

Secrets Store CSI Driver integruje external secret stores cez CSI volume. Pri Pod mount-e kubelet zavolá driver, provider plugin autentizuje workload a zapíše values do mounted filesystemu.

```text
Pod references SecretProviderClass
→ kubelet/CSI NodePublishVolume
→ provider získa external secret
→ driver mountne files do Podu
→ application ich číta z filesystemu
```

Secret nemusí byť persistentne uložený ako Kubernetes Secret, pokiaľ nie je zapnutá sync feature. Node plugin a provider však majú prístup k plaintextu a sú critical node-level boundary.

## 37. CSI rotation

Auto rotation periodicky re-fetchne values a aktualizuje Pod mount; voliteľne môže aktualizovať aj synced Kubernetes Secret. Application musí mounted file sledovať alebo reloadovať.

Rotation poll interval určuje staleness a provider load. Krátky interval zvyšuje API calls, dlhý predlžuje revocation window.

Missing provider secret môže spôsobiť mount alebo refresh failure. Startup a running-Pod behavior majú byť testované, nie odhadnuté.

## 38. ESO oproti CSI oproti direct API

**ESO** materializuje Secret ako Kubernetes API object a je kompatibilný s applications očakávajúcimi native Secret.

**CSI** mountuje file pri Pod lifecycle-e a môže sa vyhnúť persistent Kubernetes Secretu, ale viaže availability na node driver/provider a filesystem reload.

**Direct API** dáva application plný lease/metadata lifecycle, ale zvyšuje client complexity.

Výber závisí od application interface-u, desired staleness, etcd threat, node trust, issuer availability a target rotation semantics. Neexistuje univerzálne „najbezpečnejší“ pattern bez threat modelu.

## 39. HashiCorp Vault mentálny model

Vault je identity-based secrets a encryption management system. Client sa autentizuje cez auth method, Vault mapuje external identity na policies a vydá Vault token. Token autorizuje API paths, kde secrets engines ukladajú static data, generujú dynamic credentials, vydávajú certificates alebo poskytujú cryptographic operations.

```text
external identity
→ auth method
→ Vault entity/group a policies
→ Vault token
→ secrets-engine API path
→ secret/credential/crypto result
→ lease a expiration manager
→ audit devices
```

Vault centralizuje trust a audit, ale stáva sa kritickou availability a security dependency. Root/seal, storage, identity mappings a policies patria do disaster-recovery modelu.

## 40. Vault auth methods

Auth method overuje external credential alebo identity a vytvorí Vault token s policies. Príklady sú Kubernetes, cloud IAM, JWT/OIDC, TLS certificate, AppRole, LDAP a userpass.

Auth role typicky obmedzuje accepted issuers, service accounts, namespaces, cloud roles alebo token claims. Po úspechu Vault identity system môže mapovať alias na entity a groups.

Preferuj platform-generated short-lived identity. AppRole `role_id + secret_id` môže byť vhodný pre legacy machines, ale `secret_id` je bootstrap credential s distribution, response wrapping a rotation lifecycle-om.

## 41. Vault policies

Vault policy je path-based authorization. Capabilities ako `read`, `create`, `update`, `delete`, `list` a privileged `sudo` sa vzťahujú na API paths.

Path semantics závisia od engine-u. KV v2 read path obsahuje `/data/`, metadata/list path `/metadata/`; policy skopírovaná z KV v1 môže nefungovať alebo byť príliš broad.

Policies sa pripájajú k tokens priamo alebo cez identity entities/groups. Auth role constraints a policy capabilities riešia rozdielne kroky: prvé určujú, kto sa môže prihlásiť, druhé čo token smie robiť.

## 42. Vault token

Vault token je bearer credential a core authorization carrier. Obsahuje policies, TTL, renewability, parent/child lifecycle, optional use limits a accessor.

Accessor možno použiť na lookup alebo revocation bez uloženia raw tokenu v audit/workflowe. Raw token value je secret.

Service tokens môžu mať parent hierarchy; revocation parent tokenu môže revoke-nuť child tokens a leases. Batch tokens majú odlišné storage a feature semantics a treba ich voliť podľa use case-u.

Root token obchádza bežné policy restrictions. Po initialization sa má revoke-nuť a generovať iba controlled quorum processom pri výnimočnej potrebe.

## 43. Vault secrets engines

Secrets engine je mountnutý na API path a implementuje vlastný data a lifecycle model. Engine nemá relative access do iných mountov; core izoluje paths.

Príklady:

- KV — static key/value data;
- database/cloud — dynamic alebo rotated credentials;
- PKI — certificate issuance;
- Transit — encryption, signing a HMAC operations;
- SSH — SSH credentials alebo signing;
- key management — lifecycle external KMS keys podľa supported providers.

Disable engine-u môže revoke-nuť leases viazané na jeho path. Mount path je preto lifecycle identity, nie iba URL organization.

## 44. Vault KV v2

KV v2 ukladá versioned static secrets a oddelené metadata. Podporuje soft deletion, undelete, destroy a check-and-set semantics.

KV vyrieši storage a access, nie target credential rotation. Ak uložíš database password do KV a vytvoríš novú version, Vault automaticky nezmení password v database.

Policies majú oddeliť current data, version history a metadata/list. Retention a destroy majú zodpovedať incident a recovery requirements.

## 45. Vault dynamic database credentials

Database secrets engine používa configured privileged database connection a role templates na vytváranie unique users.

```text
payments-api authenticates to Vault
→ reads database/creds/payments-role
→ Vault plugin creates unique DB username/password
→ response includes lease ID and TTL
→ DB audit attributes sessions to that username
→ expiry/revoke triggers user deletion or revocation statements
```

Výhody sú attribution a krátka lifetime. Risks sú protection root DB credentialu, plugin correctness, target availability, orphan users a connection-pool behavior.

Vault revocation je best-effort voči target systemu. Revocation failure musí byť monitored a reconciled.

## 46. Vault static database roles

Static role spravuje fixed database username a Vault periodicky rotuje jeho password. Je vhodná, keď application alebo database vyžaduje stable username.

Authoritative model musí byť jasný: Vault vlastní current password a consumers ho získavajú z Vault-u. Manual change mimo Vaultu vytvorí drift.

Rotation vyžaduje application reload a connection-pool reconnect. Shared username stále znižuje per-instance attribution a zväčšuje blast radius oproti dynamic roles.

## 47. Vault PKI engine

PKI engine spravuje issuer/role policy a vydáva short-lived X.509 certificates. Role obmedzuje allowed domains, SANs, key types, usages a maximum TTL.

Short-lived certificate znižuje dependency na revocation pre bežný lifecycle, ale vyžaduje reliable automated renewal. Expiry storm môže spôsobiť widespread outage.

CA private keys, issuer hierarchy, CRL/OCSP distribution a cross-sign/rotation sú samostatný PKI lifecycle. Application role nemá dostať permission signovať arbitrary names.

## 48. Vault Transit engine

Transit poskytuje cryptography as a service. Client odošle plaintext alebo ciphertext a Vault vykoná encrypt/decrypt, signing, verification, HMAC, data-key generation alebo rewrap podľa policy.

Underlying key neopustí Vault. Application však stále vidí plaintext pred encryption alebo po decryption a musí vykonať vlastnú data authorization.

Transit nie je storage engine pre application payloads. Client ukladá ciphertext a metadata sám. Availability a latency Vaultu sú súčasť read/write pathu, pokiaľ application nepoužíva envelope data keys a cache.

## 49. Vault seal a encryption barrier

Vault storage obsahuje ciphertext. Encryption keyring je chránený root keyom a root key je chránený seal mechanismom.

Pri sealed stave Vault môže pristupovať k physical storage, ale nemôže decryptovať data ani poskytovať bežné API operations. Unseal sprístupní root key potrebný na otvorenie encryption barrier a keyring-u.

Sealing odstráni root key z memory a zastaví secrets operations. Je to emergency containment tool, ale môže vytvoriť application outage.

## 50. Shamir unseal

Default Shamir seal rozdelí unseal key na viac shares s thresholdom. Operátori zadávajú shares, kým Vault nezrekonštruuje unseal key a neotvorí barrier.

Každý Vault node sa pri Shamir modeli unseal-uje samostatne. Shares majú byť u rôznych custodians, v oddelenom secure storage, nie v jednom chat-e alebo password manager recorde.

Rekey mení shares alebo threshold pri zmene custodians. Recovery drill má overiť dostupnosť threshold-u bez zhromažďovania shares mimo ceremony.

## 51. Auto unseal a recovery keys

Auto unseal deleguje ochranu unseal keyu na external KMS/HSM alebo supported seal service. Pri startup-e Vault požiada seal mechanismus o decrypt root key materialu.

To znižuje manual operations, ale vytvára strict lifecycle dependency. Ak KMS key alebo seal mechanismus zostane trvalo nedostupný alebo je zmazaný pred migráciou, cluster nemožno obnoviť ani zo storage backupu.

Recovery keys pri auto unseal autorizujú quorum operations, napríklad generate-root alebo rekey. Nedokážu nahradiť stratený auto-unseal key a samy root key nedecryptujú.

## 52. Vault audit devices

Vault audit device zaznamenáva API request a response metadata; sensitive fields sú podľa typu a configuration typicky hashované alebo redacted. Audit musí byť explicitne zapnutý.

Vault posiela entries do všetkých enabled devices a vyžaduje úspešný zápis aspoň do jedného. Ak nevie auditovať request ani response do žiadneho dostupného device-u, corresponding API request zlyhá. Audit je preto security control aj availability dependency.

HashiCorp odporúča minimálne dve independent audit destinations. Monitoruj write latency/failures, disk space, socket backpressure a log rotation. Audit logs potrebujú integrity, restricted read a external retention.

## 53. Vault Integrated Storage a HA

Integrated Storage používa Raft replication. Jeden active node spracúva writes a standby nodes udržiavajú replicated state; cluster potrebuje quorum pre consensus.

HA chráni pred failure jedného node-u, ale nerieši logical deletion, malicious policy, seal-key loss ani region-wide disaster.

Load balancer health check musí rozlišovať active/standby/sealed state podľa desired routing. Node process running neznamená, že cluster vie vydávať secrets.

## 54. Vault snapshots a recovery

Raft snapshot zachytáva encrypted storage state. Musí byť uložený external, chránený access controlom a pravidelne restore-testovaný.

Snapshot recovery potrebuje rovnaký compatible seal mechanism, relevantnú Vault version/configuration, TLS a auth dependencies. Backup bez seal key/KMS je encrypted, ale unrecoverable.

Restore test nemá skončiť pri štarte processu. Musí overiť unseal, cluster health, authentication, policy, retrieval dynamic/static test secretu, lease/revocation a audit continuity.

## 55. Disaster recovery model

Definuj RPO a RTO pre storage aj identity/seal dependencies. Recovery plán zahŕňa:

- Raft snapshot alebo Enterprise replication podľa edition;
- seal/KMS availability a permissions;
- DNS/load-balancer cutover;
- auth-method dependencies, napríklad Kubernetes API alebo cloud IAM;
- external database/cloud systems pre dynamic engines;
- audit destinations;
- application cache a outage behavior;
- post-recovery token/lease validation.

DR cluster, ktorý nevie komunikovať s IdP alebo KMS, nemusí byť operational napriek healthy Raft state-u.

## 56. Secrets-platform outage

Pri outage môže workload:

- používať ešte platný cached credential do expiry;
- odmietnuť nové sessions, ale dokončiť existing work;
- prejsť do read-only alebo degraded mode;
- zastaviť startup;
- použiť oddelený break-glass path pre recovery.

Behavior závisí od secret type-u. Neobmedzený fallback na old credential neguje revocation. Okamžitý global fail-closed môže vytvoriť cascading outage.

Outage plan má byť testovaný chaos alebo game-day scenárom vrátane restartu applications, pretože running cache a cold start majú odlišné behavior.

## 57. Application rotation support

Secrets platforma nemôže napraviť application, ktorá načíta credential iba pri prvom štarte a nikdy ho neread-ne.

Application patterns:

- refresh pred lease expiry;
- atomic file reload;
- connection-pool reconnect;
- dual credential overlap;
- version-aware in-memory cache;
- graceful restart pri non-reloadable library;
- retry s bounded backoff a jitter;
- explicit error rozlišujúci auth failure od issuer outage-u.

Rotation test má potvrdiť aj revocation old credentialu, nie iba successful new connection.

## 58. Logging a telemetry

Nikdy neloguj raw password, bearer token, private key, connection string s credentials ani recovery/unseal share.

Sleduj metadata:

- auth success/failure a role mapping;
- policy deny;
- issuance, renewal a revocation;
- lease near expiry;
- rotation result;
- cache age a refresh failure;
- provider/controller/CSI sync age;
- Vault sealed/active/standby state;
- audit-device failures;
- request latency a errors;
- orphan credential cleanup.

Secret path môže byť citlivý; labels a logs majú používať bounded safe identifiers. Secret value nikdy nepatrí do metric labelu.

## 59. Secret compromise response

Response začína authoritative revocation, nie editovaním source file-u.

```text
identifikovať secret type, issuer a target
→ zastaviť alebo scope-nuť ďalšie use
→ revoke/disable v authoritative systéme
→ určiť consumers, sessions a copies
→ zachovať audit evidence a exposure interval
→ rotate dependent credentials/keys
→ redeploy alebo reload workloads
→ overiť old credential ako neplatný
→ odstrániť source leakage
→ pridať guardrails a regression test
```

Pri private signing/encryption keyu treba analyzovať artifacts alebo ciphertexts z exposure intervalu. Pri bearer token-e hľadaj use v API logs a revoke-ni sessions.

## 60. Troubleshooting retrieval

Postupuj po identity-to-delivery chain-e:

```text
workload identity alebo human credential
→ issuer, audience, expiry a trust
→ network/DNS/TLS k secrets platforme
→ auth method a role constraints
→ Vault/secret-store policy a path
→ secret version, dynamic role alebo provider key
→ lease/quota/rate limit
→ ESO/CSI/agent reconciliation
→ file/env/API delivery
→ application cache/reload
→ target-system authentication
```

`permission denied` a `secret not found` môžu byť zámerne nerozlíšiteľné, aby API neodhaľovalo existence. Diagnostika potrebuje internal audit a policy evaluation, nie random path guessing.

## 61. Typické failure modes

**Rotation prebehla, application zlyhala.** Process drží old pool, file descriptor alebo environment value.

**Dynamic credential expired.** Renewal zlyhal pre lost workload identity, issuer outage alebo blocked network; application nemala refresh margin.

**Kubernetes Secret sa zmenil, process nie.** Environment sa neaktualizuje alebo application nereadla mounted file.

**ESO ukazuje stale Secret.** Provider call, auth, refresh policy alebo controller reconciliation zlyhali.

**CSI Pod sa nespustí.** NodePublishVolume alebo provider retrieval nevie získať referenced secret.

**Vault je sealed.** Seal mechanism/KMS nie je dostupný, permission chýba alebo node bol manuálne sealed.

**Vault API requests zlyhávajú počas audit outage-u.** Všetky enabled audit destinations sú blocked alebo unwritable.

**Database users zostávajú po lease expiry.** Target revocation failed a orphan cleanup/reconciliation chýba.

## 62. Metrics a SLO

Secrets platforma potrebuje availability aj security objectives:

- authentication a token issuance success rate;
- retrieval latency/error rate;
- lease renewal failure rate;
- rotation success a time-to-activation;
- revocation latency;
- secrets blízko expiry;
- stale ESO/CSI sync age;
- Vault sealed node count a Raft health;
- audit-device error rate;
- dynamic credential creation/revocation failures;
- cache age a fallback usage;
- orphan target credentials;
- restore-test freshness.

SLO nemá motivovať fail-open. Availability metric musí byť doplnená security correctness a audit completeness.

## 63. Governance

Organization potrebuje approved stores, ownership, naming/path conventions, dynamic-secret preference, maximum lifetimes, rotation SLAs, exception process, scanning a incident playbook.

Najdôležitejšia je autorita: pre každý credential type má existovať jeden source of truth a jasný target-system lifecycle. Paralelné stores a manual copies vytvárajú drift.

Governance má definovať onboarding nového secret type-u, periodic access review, decommission consumers, deletion old versions a recovery testing.

## 64. Časté anti-patterny

**Secret v Git-e s plánom „neskôr rotate-neme“.** History a clones už vytvorili exposure.

**Base64 ako encryption.** Encoding neposkytuje confidentiality.

**Jeden shared production password.** Chýba attribution a blast radius je celý fleet.

**Rotation bez revocation.** Old credential zostáva validný.

**Secret manager bez outage modelu.** Cold-start všetkých workloads závisí od jedného API.

**Unlimited stale cache.** Expiry a incident revoke strácajú význam.

**Root/admin token v application.** Compromise poskytne platform-wide authority.

**Human copy-paste delivery.** Chýba repeatability, audit a reliable rotation.

**Backup bez seal/key recovery.** Encrypted storage nemožno obnoviť.

**Kubernetes Secret považovaný za complete vault.** Chýba external rotation, target revocation a broader lifecycle.

## 65. Kompletný production príklad

Payments API beží v Kubernetes a pristupuje k PostgreSQL.

1. Pod používa dedicated ServiceAccount a projected audience-bound token.
2. Vault Kubernetes auth overí token review, namespace a ServiceAccount mapping.
3. Vault vydá short-lived token s policy iba pre `database/creds/payments-api`.
4. Database engine vytvorí unique PostgreSQL usera s 30-minútovou lease.
5. Agent alebo application dostane credential a otvorí connection pool.
6. Refresh začne s marginom a jitterom; nový credential vytvorí nový pool.
7. Po successful health checku sa old pool drain-ne a lease revoke-ne.
8. Vault audit prepája ServiceAccount identity, token accessor, lease ID a DB username.
9. Pri Vault outage-u existing valid DB sessions pokračujú krátko; nové cold-start Pods failnú controlled spôsobom a alertujú.
10. Pri incident revoke prefixu zneplatní tokeny a child leases; DB plugin odstráni users a runtime verification potvrdí closure.
11. Raft snapshots, KMS auto-unseal dependency a auth-method connectivity sa pravidelne testujú v DR drill-e.

Tento flow ukazuje, že secrets management nie je file injection. Je to identity, issuance, target credential, application reload, revocation, audit a recovery v jednom contracte.

## 66. Kontrolné otázky

1. Prečo je secret capability a nie iba citlivý string?
2. Ako sa identity líši od credentialu?
3. Ako sa static a dynamic secret líšia v lifecycle a attribution?
4. Čo je secret zero a prečo ho nemožno vyriešiť ďalším secretom vedľa aplikácie?
5. Ako workload identity mapuje na secret role?
6. Aké risks majú environment, file, agent a direct API delivery?
7. Ako navrhnúť cache bez negovania revocation?
8. Aký je rozdiel medzi rotation a revocation?
9. Čo je lease a ako sa líši od KV version metadata?
10. Prečo `list` alebo indirect Pod access môže odhaliť Kubernetes Secrets?
11. Ako sa ESO, CSI a direct API patterny líšia?
12. Čo musí application urobiť po file alebo credential rotation?
13. Ako Vault auth method, policy, token a secrets engine tvoria jeden flow?
14. Ako fungujú dynamic database credentials a čo sa stane pri revocation failure?
15. Čo Vault Transit chráni a kde stále existuje plaintext?
16. Ako funguje Vault seal/unseal hierarchy?
17. Prečo recovery keys nenahradia stratený auto-unseal KMS key?
18. Prečo audit device outage môže zastaviť Vault API?
19. Čo musí overiť Raft snapshot restore test?
20. Navrhni compromise response pre secret nájdený v Git history.

## Glossary impact

Relevantné pojmy: secret, secrets management, secret capability, secret lifecycle, static secret, dynamic secret, secret zero, workload identity, secret classification, secret delivery, secret cache, secret rotation, secret revocation, lease, secret versioning, External Secrets Operator, ExternalSecret, refresh policy, Secret Store CSI Driver, SecretProviderClass, Vault auth method, Vault policy, Vault token, token accessor, secrets engine, KV v2, dynamic database credential, static database role, PKI secrets engine, Transit secrets engine, seal, unseal, encryption barrier, Shamir shares, recovery keys, auto unseal, audit device, Integrated Storage, Raft snapshot, secret scanning a break-glass secret access.

## Primárne zdroje

- [NIST SP 800-57 Part 1 Rev. 5 — Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Good practices for Kubernetes Secrets](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)
- [Kubernetes RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
- [External Secrets Operator — ExternalSecret](https://external-secrets.io/main/api/externalsecret/)
- [External Secrets Operator — lifecycle, ownership a deletion](https://external-secrets.io/latest/guides/ownership-deletion-policy/)
- [Secrets Store CSI Driver](https://secrets-store-csi-driver.sigs.k8s.io/introduction/)
- [Secrets Store CSI Driver — auto rotation](https://secrets-store-csi-driver.sigs.k8s.io/topics/secret-auto-rotation)
- [HashiCorp Vault documentation](https://developer.hashicorp.com/vault/docs)
- [How Vault works](https://developer.hashicorp.com/vault/docs/about-vault/how-vault-works)
- [Vault authentication](https://developer.hashicorp.com/vault/docs/concepts/auth)
- [Vault policies](https://developer.hashicorp.com/vault/docs/concepts/policies)
- [Vault tokens](https://developer.hashicorp.com/vault/docs/concepts/tokens)
- [Vault leases](https://developer.hashicorp.com/vault/docs/concepts/lease)
- [Vault database secrets engine](https://developer.hashicorp.com/vault/docs/secrets/databases)
- [Vault PKI secrets engine](https://developer.hashicorp.com/vault/docs/secrets/pki)
- [Vault Transit secrets engine](https://developer.hashicorp.com/vault/docs/secrets/transit)
- [Vault seal and unseal](https://developer.hashicorp.com/vault/docs/concepts/seal)
- [Vault audit devices](https://developer.hashicorp.com/vault/docs/audit)
- [Vault Integrated Storage](https://developer.hashicorp.com/vault/docs/concepts/integrated-storage)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: SAML](saml.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Encryption at rest a in transit →](encryption-at-rest-and-in-transit.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
