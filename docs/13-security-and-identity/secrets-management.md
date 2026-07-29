# Secrets management

Secrets management je lifecycle disciplína pre credentials, private keys, tokens, recovery material a ďalšie capabilities. Cieľom nie je iba uložiť value do encrypted database. Cieľom je vedieť, prečo capability existuje, kto ju smie získať, ktorý target jej dôveruje, ktorá generation je načítaná v consumers, ako sa zneplatní a ako sa incident uzavrie bez ponechania old copies alebo derived sessions.

Secret je hodnotný preto, že ho cieľový systém akceptuje. Private signing key môže vytvárať dôveryhodné tokens alebo assertions. Database password vytvorí session. Refresh token vydáva ďalšie access tokens. Zmazanie jednej copy secretu preto nie je revocation.

## 1. Dominantný capability-to-revocation lifecycle

```text
business purpose a target trust
→ exact secret subject, owner a consumers
→ generation alebo import
→ authoritative registration a storage
→ bootstrap identity a authorization
→ issuance alebo distribution
→ consumer-loaded generation a bounded use
→ renewal, rotation alebo target mutation
→ revocation všetkých copies a descendants
→ audit, recovery, retention a destruction
```

Každá fáza má samostatný failure boundary. Secret môže byť bezpečne uložený, ale doručený wrong workloadu. Source môže mať novú version, ale application stále používa starú. Provider label môže ukazovať na nový value, ale target database ešte dôveruje starému passwordu. Key môže byť odstránený zo store-u, ale jeho public trust a sessions môžu prežiť.

## 2. Exact secret subject

Pri incidente alebo rotation zachovaj:

```text
purpose, credential type a target system
+ stable secret/key ID a generation/fingerprint
+ authoritative source path a version/lease
+ owner, environment, tenant a protocol purpose
+ bootstrap identity a policy revision
+ all direct a indirect consumers
+ delivery path a local copies
+ loaded generation per consumer
+ target trust/credential state
+ derived sessions, tokens, assertions alebo certificates
+ revocation, backup a destruction state
```

Connected subject `SECRET-PAY-49`:

```text
secret: FED-SIGN-07
material: RSA private signing key
source: Kubernetes Secret identity/federation-signing-key
consumers: staging-idp, production-idp
purposes: OIDC JWT signing + SAML XML signing
environments: staging + production
delivery: mounted file /var/run/atlas/federation/key.pem
loaded fingerprint: 5A:91:...:E7
trust descendants: two JWKS sets, two SAML metadata sets, RP/SP sessions
```

## 3. Secret, identity a capability

Identity určuje actor-a. Secret je authenticator alebo capability, ktorú actor používa. Shared static secret spája viac actors do jednej identity a znižuje attribution.

Preferovaný workload model:

```text
platform-generated workload identity
→ target-specific authentication
→ short-lived/scoped credential alebo cryptographic operation
→ per-workload audit
```

Private signing key nemusí byť exportovaný do workloadu vôbec. HSM/KMS alebo signing service môže vykonať bounded `sign` operation po authorization. Tým sa znižuje počet plaintext copies, hoci authorized malicious signing request zostáva threatom.

## 4. Classification podľa semantics

Secret inventory nemá byť iba zoznam paths. Pre každý subject urči:

- credential semantics — bearer, password, private key, recovery material;
- target system a accepted operations;
- ownera a consumers;
- environment, tenant a purpose;
- lifetime, cryptoperiod a maximum stale interval;
- rotation a revocation mechanism;
- target mutation a consumer reload requirement;
- compromise impact a derived credentials;
- backup/recovery dependencies;
- audit a privacy classification.

Private signing key má iný recovery model než database password. Jeho compromise môže spochybniť všetky assertions podpísané v exposure intervale, nie iba future login.

## 5. Static a dynamic secret

Static secret je opakovane používaná value. Je jednoduchý pre legacy integrations, ale kopíruje sa, stráca ownera, vyžaduje coordinated rotation a má dlhý compromise window.

Dynamic secret vzniká on demand pre konkrétnu identity alebo role:

```text
workload authenticates
→ policy povoľuje dynamic role
→ platforma vytvorí unique target credential
→ lease a TTL
→ use a renewal
→ revoke/expire v target systéme
```

Dynamic issuance zlepšuje attribution a skracuje lifetime. Neodstraňuje failure model: issuer alebo revocation plugin môže byť unavailable a orphan credential môže v target systéme prežiť.

Signing keys bývajú dlhšie žijúce než dynamic database users, ale môžu zostať non-exportable a versionované v KMS/HSM. „Dynamic je vždy lepšie“ nie je správne bez protocol a availability analýzy.

## 6. Secret zero a bootstrap identity

Workload potrebuje prvotný trust anchor. Permanentný Vault token alebo cloud key v image iba presúva problém.

Vhodné bootstrap boundaries:

- Kubernetes projected ServiceAccount token s exact audience;
- cloud workload identity;
- CI OIDC identity viazaná na repository/workflow/environment;
- SPIFFE alebo platform-issued mTLS identity;
- hardware-backed machine identity;
- bounded one-time enrollment.

Bootstrap policy validuje exact issuer, subject, audience, environment a runtime selector. Wildcard mapping všetkých ServiceAccounts na privileged secret path zmení workload identity na shared cluster credential.

## 7. Storage encryption a access policy

Secrets store potrebuje encryption at rest, authentication, authorization, version/lease metadata, audit, HA a recoverable backup. Storage encryption rieši storage-only compromise. Nechráni pred principalom s `read`, Podom oprávneným mountnúť Secret ani compromised application, ktorá smie value získať.

```text
ciphertext storage
→ DEK alebo storage encryption layer
→ KEK/seal root v oddelenej boundary
→ API identity a policy
→ plaintext delivery a runtime use
```

Separation má hodnotu iba pri odlišných permissions a failure domains. Backup ciphertext bez root/seal recovery je nepoužiteľný. Root key pri rovnakom broad administratorovi ako secret data neposkytuje silnú separation.

## 8. Delivery a loaded state

### Environment variable

Jednoduchá, ale typicky create-time only. Child processes ju zdedia a debug/crash dump môže odhaliť celý environment. Rotation často vyžaduje process replacement.

### Mounted file

Umožňuje filesystem permissions a atomic replacement. Application však môže držať old file descriptor alebo key načítať iba pri štarte. Source update preto nepreukazuje loaded generation.

### Agent alebo sidecar

Agent rieši authentication, renewal a file templating. Stáva sa ďalšou high-trust boundary; node-level agent môže mať veľký blast radius.

### Direct API alebo cryptographic service

Application dostane lease metadata alebo požiada o non-exportable operation. Znižuje persistent copies, ale pridáva runtime dependency, queue, timeout, cache a degraded-mode semantics.

Pre každý pattern musí existovať read-back:

```text
source generation
→ delivered generation
→ process loaded generation
→ target operation používa new credential/key
```

## 9. Cache, renewal a unknown outcome

Plaintext cache znižuje availability coupling, ale predlžuje revocation latency. Policy určuje TTL, refresh-before-expiry, jitter, maximum stale use a behavior pri issuer outage.

Blind retry pri unknown issuance alebo target-mutation outcome môže vytvoriť duplicate users, certificates alebo keys. Pred opakovaním treba read-back target state a idempotency identity.

Fail-open s expired credentialom môže zachovať compromised access. Fail-closed môže spôsobiť outage. Rozhodnutie patrí do risk a business continuity contractu, nie do náhodného client defaultu.

## 10. Rotation nie je jedna operácia

Static credential rotation:

```text
inventory target a consumers
→ vytvoriť new generation
→ zaregistrovať ju v target truste
→ publikovať/doručiť consumers
→ overiť loaded state a new operation
→ bounded overlap
→ revoke old target credential/key trust
→ zrušiť old sessions/descendants
→ odstrániť copies a overiť forbidden old path
```

Ak iba zmeníš value v secret store, target môže stále akceptovať old password. Ak zmeníš target password skôr, než consumers načítajú nový, vznikne outage. Pri signing key rollover-e verifiers musia dostať public key skôr, než issuer začne podpisovať novým keyom.

## 11. Revocation graph

Compromise credentialu vyžaduje graph, nie jeden delete:

```text
source secret/key
→ distributed copies
→ loaded processes
→ target sessions alebo grants
→ issued access tokens/assertions/certificates
→ downstream exchanged credentials
→ cached trust a backups
```

Revocation môže znamenať disable target accountu, odstránenie public verification keyu, revoke lease/token family, ukončenie local sessions, rotate dependent webhook secret a rebuild artifactu.

Zmazanie Git commit-u alebo Kubernetes Secretu bez target revocation necháva capability použiteľnú.

## 12. Kubernetes Secret boundary

Kubernetes Secret je API object, nie automaticky external secrets manager. `.data` je base64 representation. At-rest encryption musí byť explicitne nakonfigurovaná.

High-impact access paths zahŕňajú:

- `get`, `list` alebo `watch` Secrets;
- permission vytvoriť Pod, ktorý Secret mountne;
- výber privileged ServiceAccountu;
- `pods/exec`, debug alebo ephemeral containers;
- node/kubelet access;
- CSI/provider permissions;
- backup alebo etcd access.

```text
nemôže get Secret
+ môže create Pod s oprávnenou ServiceAccount
→ môže získať Secret nepriamo
```

Environment value sa po update nezmení. Projected volume môže byť aktualizovaný, ale application ho musí reloadnúť. `subPath` a open file descriptor môžu zachovať old content.

## 13. External store patterns

External Secrets Operator materializuje provider value do Kubernetes Secretu. Centralizuje source, ale plaintext stále vstúpi do API, etcd a Pod projection. Operator má broad provider aj cluster permissions a potrebuje tenant isolation, refresh a deletion contract.

Secrets Store CSI Driver mountuje provider values cez node plugin. Môže sa vyhnúť persistent Kubernetes Secretu, ale node/provider path vidí plaintext a application musí reloadnúť file.

Direct API alebo signing service poskytne lease/operation semantics bez Kubernetes copy, za cenu runtime dependency.

Výber závisí od etcd, node, provider, application a availability threat modelu.

## 14. Vault model

Vault oddeľuje:

```text
external identity
→ auth method
→ entity/group a policies
→ Vault token
→ engine path
→ static value, dynamic credential alebo crypto operation
→ lease/revocation
→ audit device
```

Auth role určuje, kto sa môže autentizovať. Policy určuje, ktoré paths a capabilities token smie používať. KV version update nerotuje automaticky credential v target database. Transit `sign` alebo `encrypt` môže držať key non-exportable, ale caller authorization a key purpose zostávajú kritické.

Vault token je bearer credential. Root token obchádza bežné policies a nemá byť persistentný operational credential.

## 15. Build, Git, state a image copies

Secret nepatrí do Dockerfile `ARG/ENV`, image layer, build cache, Git history, plan artifact ani Terraform state bez explicitného protection modelu.

Build secret mount zabráni automatickému layer persistence, ale build command stále môže value skopírovať do outputu alebo logu. `sensitive` v Terraform obmedzuje display, nie automaticky state storage.

Pri leakage:

```text
classify target capability
→ revoke/disable
→ preserve evidence a exposure window
→ rotate consumers a descendants
→ odstrániť active leak
→ rebuild artifacts
→ až potom riešiť history cleanup
```

## 16. Worked failure — shared federation key získaný cez indirect Pod access

`FED-SIGN-07` vznikol ako temporary migration key. Nemal ownera, expiration ani inventory consumers. Bol skopírovaný do staging a production Kubernetes Secretu a používal sa pre OIDC aj SAML.

Staging debug role nemala direct `get secrets`, ale mala:

```text
create pods
+ use ServiceAccount idp-runtime
+ mount existing Secret federation-signing-key
+ exec do vytvoreného Podu
```

Attacker vytvoril `key-inspector` Pod, mountol Secret a skopíroval `/var/run/atlas/federation/key.pem`. Etcd encryption a TLS fungovali; API a kubelet však legitímne doručili plaintext oprávnenému workload path-u.

Key potom umožnil ovládnuť staging federation issuer a podpísať artifacts, ktoré production OIDC RP a SAML SP akceptovali pre shared key a chýbajúce issuer/entity bindingy.

## 17. Competing hypotheses a discriminating evidence

Hypotézy:

1. etcd storage leak;
2. CI/Git/image leakage;
3. direct Secret API read;
4. node compromise;
5. indirect Pod-mount access;
6. KMS/HSM compromise.

Evidence:

- etcd a KMS audit neukázali unauthorized storage read;
- secret scanner nenašiel key v Git ani image layers;
- Kubernetes audit neobsahoval `get secret` od debug principalu;
- obsahoval `create pod` s `idp-runtime` ServiceAccount a Secret volume;
- kubelet úspešne projektoval Secret do Podu;
- `pods/exec` audit nasledoval o 41 sekúnd;
- fingerprint stolen keyu sedel s `FED-SIGN-07`;
- key bol rovnaký v staging aj production a v OIDC aj SAML trust metadata.

Root cause je neoddelený secret subject a incomplete authorization graph. Indirect Pod capability, shared environments/purposes a exportovaný private key sú amplifiers.

## 18. Evidence-preserving containment

- odstrániť debug role permission vytvárať Pods s `idp-runtime` identity;
- quarantine affected ServiceAccount a Pods;
- zastaviť nové signing operations keyom `FED-SIGN-07`;
- odstrániť public trust keyu z production federation paths podľa coordinated incident planu;
- preserve-nuť Kubernetes audit, Pod spec/UID, node projection evidence, key fingerprint a signing/session audit;
- revoke-nuť sessions a tokens/assertions z exposure interval-u;
- nevymazať Secret pred inventory všetkých copies a consumers.

## 19. Authoritative recovery

1. vytvoriť štyri samostatné key subjects: staging/prod × OIDC/SAML;
2. používať non-exportable KMS/HSM signing operations, ak platforma podporuje;
3. oddeliť namespaces, ServiceAccounts, policies a trust metadata;
4. zaviesť admission policy blokujúcu unauthorized Secret mount a ServiceAccount selection;
5. publikovať new public keys/certificates s bounded overlapom;
6. overiť loaded signing generation na všetkých issuer replicas;
7. overiť verifier trust generation na všetkých RPs/SPs;
8. odstrániť `FED-SIGN-07` z trustu, stores, Pods, backups podľa retention policy a debug paths;
9. revoke-nuť affected sessions, grants a descendants;
10. vykonať second rotation a recovery restore test.

## 20. Acceptance verdict

- debug principal nedokáže Secret čítať, mountnúť ani získať cez alternate ServiceAccount;
- staging workload nedokáže použiť production signing capability;
- OIDC key nedokáže podpisovať accepted SAML assertion a naopak;
- source, delivered a loaded generation sú rovnaké na intended consumers;
- old `FED-SIGN-07` signature je odmietnutá všetkými production verifiers;
- new key podpisuje iba intended issuer/protocol artifacts;
- provider/KMS outage má testovaný bounded behavior;
- backup restore obnoví potrebné encrypted state a policy bez resurrectovania revoked keyu;
- druhá rotation prejde bez outage-u a bez predĺženého old trustu;
- affected business sessions a settlement changes sú reconciled.

## 21. Troubleshooting flow

```text
purpose/target a exact key/secret generation
→ authoritative source a policy
→ bootstrap identity
→ direct aj indirect access graph
→ delivery path
→ consumer-loaded generation
→ target trust/credential state
→ issued sessions/descendants
→ rotation/revocation
→ forbidden old-path validation
```

## 22. Earlier controls

- secret owner, purpose, consumers a expiration ako required metadata;
- no cross-environment alebo cross-protocol key reuse;
- workload identity namiesto shared bootstrap secretu;
- indirect Kubernetes privilege analysis;
- non-exportable signing keys;
- loaded-generation telemetry bez secret value;
- automated consumer inventory a revocation graph;
- rotation a emergency compromise rehearsal;
- secret scanning spojený s automatic capability revocation workflowom.

## 23. Anti-patterny

### Secret je encrypted, teda bezpečný

Authorized runtime, Pod mount alebo broad API policy stále získa plaintext.

### Nemá `get secrets`, teda Secret neprečíta

Pod creation, ServiceAccount use, exec a node access sú indirect paths.

### Source version bola zmenená, teda rotation je hotová

Consumer a target môžu stále používať old generation.

### Jeden key pre viac purposes

Compromise prekročí environments, protocols a trust domains.

### Secret odstránený zo store-u = revoked

Sessions, tokens, public trust a copies môžu prežiť.

## 24. Kontrolné otázky

1. Prečo je secret capability, nie iba citlivý string?
2. Čo tvorí exact secret subject?
3. Ako sa static a dynamic credential líšia?
4. Čo je secret zero?
5. Ako sa source, delivered a loaded generation líšia?
6. Prečo rotation potrebuje target a consumer coordination?
7. Aké indirect Kubernetes Secret access paths existujú?
8. Ako sa ESO, CSI a direct API trade-offy líšia?
9. Prečo revocation potrebuje descendant graph?
10. Čo musí overiť secret acceptance verdict?

## Glossary impact

Relevantné pojmy: secret lifecycle subject, capability target, bootstrap identity boundary, consumer-loaded secret generation, target-trust generation, secret revocation graph, indirect Secret access, non-exportable signing capability, cross-purpose key reuse a secret acceptance verdict.

## Primárne zdroje

- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Good practices for Kubernetes Secrets](https://kubernetes.io/docs/concepts/security/secrets-good-practices/)
- [Kubernetes encrypting confidential data at rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
- [HashiCorp Vault concepts](https://developer.hashicorp.com/vault/docs/concepts)
- [HashiCorp Vault dynamic secrets](https://developer.hashicorp.com/vault/docs/secrets/databases)
- [HashiCorp Vault Transit secrets engine](https://developer.hashicorp.com/vault/docs/secrets/transit)
- [Secrets Store CSI Driver concepts](https://secrets-store-csi-driver.sigs.k8s.io/concepts.html)
- [External Secrets Operator guides](https://external-secrets.io/latest/guides/introduction/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: SAML](saml.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Encryption at rest a in transit →](encryption-at-rest-and-in-transit.md)
<!-- KNOWLEDGE-NAVIGATION:END -->