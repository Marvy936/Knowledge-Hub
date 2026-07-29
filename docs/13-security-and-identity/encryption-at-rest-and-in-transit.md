# Encryption at rest a in transit

Encryption je cryptographic mechanism na ochranu confidentiality. Moderné použitie zároveň chráni integrity ciphertextu cez authenticated encryption. Security výsledok však nevzniká z checkboxu `encrypted`. Vzniká z threat modelu, exact data a key subjectu, algorithm/mode correctness, key authorization, plaintext boundaries, consumer behavior, rotation, revocation a recovery.

At-rest encryption môže chrániť ukradnutý disk alebo leaked etcd backup. TLS môže chrániť packet path. Ani jedno automaticky nechráni plaintext pred workloadom, ktorý ho smie načítať, pred debug Podom s indirect Secret accessom alebo pred application processom oprávneným volať KMS `Decrypt`.

## 1. Dominantný asset-to-key-boundary lifecycle

```text
data alebo trust asset a threat model
→ exact protection subject a state: rest/transit/use
→ required confidentiality/integrity/authentication property
→ algorithm, protocol a format generation
→ key purpose, owner, scope a cryptographic boundary
→ authorized encrypt/decrypt/sign/verify/session operation
→ ciphertext alebo protected-channel publication
→ consumer validation a plaintext boundary
→ rotation, rekey, rewrap, revocation a migration
→ restore, compromise response a forbidden-old-path validation
```

Jedna kapitola musí držať oddelené tri otázky:

1. Čo chráni cryptography?
2. Pred ktorým attackerom a na ktorej boundary?
3. Kto stále môže oprávnene získať plaintext alebo vykonať signing/decrypt operation?

## 2. Exact cryptographic subject

Pri návrhu alebo incidente zachovaj:

```text
asset/data set alebo signed-artifact class
+ confidentiality/integrity/authentication objective
+ at-rest, in-transit a in-use copies
+ algorithm, mode, protocol a format version
+ key ID, version, purpose a cryptoperiod
+ nonce/IV/tag/AAD alebo signature context
+ KMS/HSM/store a authorization policy
+ producers, consumers a loaded trust generation
+ ciphertext/session/artifact inventory
+ backup, recovery, revocation a destruction state
```

Connected subject `CRYPTO-PAY-49`:

```text
key: FED-SIGN-07
algorithm: RSA signature key
purposes: OIDC JWS + SAML XML Signature
environments: staging + production
storage: Kubernetes Secret encrypted in etcd cez KMS v2
transport: API/kubelet TLS
plaintext boundary: projected file v IdP Pod-e
trust consumers: OIDC JWKS caches + SAML metadata caches
exposure result: forged or attacker-controlled federation assertions
```

## 3. Encryption, hashing, MAC a signature

Tieto mechanisms majú rozdielne properties:

- encryption — reversible confidentiality s keyom;
- hash — one-way digest bez secret keyu;
- MAC — integrity a origin authentication medzi holders shared secretu;
- digital signature — private-key signing a public-key verification;
- key establishment/KEM — vytvorenie shared secretu pre ďalšiu symmetric protection.

Hash file-u bez trusted signature nepreukazuje origin. Encryption bez integrity môže byť malleable. Signature neposkytuje confidentiality. Signing private key a encryption private key nemajú byť zdieľané iba preto, že oba sú RSA alebo EC material.

## 4. Data at rest, in transit a in use

```text
at rest
→ disks, object storage, databases, etcd, snapshots, backups, logs

in transit
→ client–server, service–service, replication, CI–registry

in use
→ process memory, CPU, file descriptor, decrypted object, debug dump
```

TLS decryptne traffic na endpoint-e. Storage encryption decryptne data pre authorized readera. Po decryption vzniká plaintext boundary, ktorú chránia identity, authorization, process isolation, minimal lifetime, logging discipline a memory controls.

Rovnaké data sa môžu presúvať medzi states. Encrypted request sa po TLS termination stane plaintextom a môže byť neúmyselne zapísaný do logu ako nová at-rest copy.

## 5. Threat model pred algoritmom

At-rest threats:

- ukradnuté médium alebo snapshot;
- leaked backup;
- etcd/object-storage-only compromise;
- nesprávna media disposal;
- storage operator bez decrypt permission.

In-transit threats:

- packet capture;
- MITM a rogue proxy;
- DNS/routing manipulation;
- disabled hostname validation;
- plaintext internal leg;
- protocol downgrade.

In-use threats:

- compromised application;
- broad decrypt/sign permission;
- debug/exec access;
- memory dump;
- injection, ktorá prinúti application vykonať validnú cryptographic operation.

Disk encryption nechráni running root compromise. KMS nechráni pred callerom s broad `Decrypt`. HSM chráni key extraction, nie authorized malicious signing request.

## 6. Authenticated encryption, nonce a AAD

AEAD chráni plaintext confidentiality aj ciphertext integrity. Decryption musí overiť tag pred použitím plaintextu.

AAD nie je šifrované, ale je viazané k ciphertextu. Môže obsahovať tenant ID, object ID, schema version alebo purpose:

```text
ciphertext documentu
+ AAD tenant=atlas-payments, object=PAY-884219, schema=3
→ nemožno bezpečne presunúť do iného tenant/object contextu
```

Nonce/IV rules sú algorithm-specific. AES-GCM nonce reuse pod rovnakým keyom môže poškodiť confidentiality aj integrity. Distributed producer potrebuje collision-safe generation, operation limits a key rotation policy.

AAD serialization musí byť canonical a versionovaná. Wrong ordering alebo encoding vytvorí legitimate decrypt failures; missing tenant context môže umožniť ciphertext substitution.

## 7. Key separation

Key má byť oddelený podľa:

- purpose — encryption, signing, MAC, wrapping;
- environment — staging, production;
- tenant alebo data domain;
- protocol a trust domain;
- actor alebo workload scope;
- cryptoperiod a compromise boundary.

```text
prod OIDC signing key
≠ prod SAML signing key
≠ staging OIDC signing key
≠ data-encryption KEK
```

Cross-purpose reuse zvyšuje blast radius a môže porušiť protocol assumptions. Cross-environment reuse mení staging compromise na production compromise.

Key separation možno realizovať independent keys alebo approved domain-separated derivation. Human-readable label bez policy a key identity nie je separation.

## 8. Envelope encryption

Envelope encryption používa Data Encryption Key — DEK — na payload a Key Encryption Key — KEK — na wrapping DEK-u:

```text
vygenerovať DEK
→ AEAD encrypt payload
→ KMS wrap DEK pod KEK a encryption contextom
→ uložiť ciphertext, wrapped DEK, nonce, tag a format version
→ authorized consumer unwrapne DEK
→ plaintext existuje iba v bounded process memory
```

Rewrap mení KEK protection wrapped DEK-u bez full payload re-encryption. Rekey/re-encrypt vytvorí nový data key a nový ciphertext. Tieto operations nie sú synonymá.

Envelope encryption centralizuje key authorization, ale compromised application s broad unwrap permission stále môže decryptovať všetky data. Encryption context/AAD, resource scoping a audit sú kritické.

## 9. KMS a HSM boundaries

KMS poskytuje versionované keys, cryptographic operations, policies, disable/delete states, rotation a audit. HSM je hardware cryptographic boundary s obmedzeným key exportom.

```text
HSM-backed alebo non-exportable key
→ znižuje theft raw private keyu
→ nebráni authorized malicious sign/decrypt requestu
```

Policy obmedzuje principal, operation, key, environment a context. Broad `Decrypt` alebo `Sign` na všetky keys je cryptographic equivalent broad admin role.

KMS/HSM availability, throttling, cache a disaster recovery sú runtime dependencies. Backup ciphertext bez recoverable key hierarchy je data loss. Backup key bez policy/audit recovery môže obnoviť zakázaný trust.

## 10. Key lifecycle a cryptoperiod

```text
requirement a purpose
→ generation/import
→ registration a activation
→ authorized use
→ rotation alebo migration
→ deactivation/revocation
→ archival podľa recovery potreby
→ destruction
```

Rotation pri routine expiry môže používať controlled overlap. Compromise potrebuje rýchle zastavenie new operations, removal trustu a posúdenie artifacts/sessions z exposure interval-u.

Key deletion bez dependency inventory môže spôsobiť irreversible data loss. Permanentne active key bez ownera a retirement planu vytvára hidden trust.

## 11. At-rest layers

### Full-disk alebo volume encryption

Chráni lost/offline media. Running host po unlocku vidí plaintext.

### Database/TDE alebo object-storage encryption

Chráni files, devices a vybrané backups. SQL principal alebo object API caller s read permission stále dostane plaintext.

### Application/field-level encryption

Môže chrániť pred database operatorom a viazať tenant/object context. Application runtime a KMS authorization sa stávajú high-value boundary.

### Backup encryption

Backup potrebuje independent access, integrity, key retention a restore rehearsal. Encryption bez recoverable keyu nie je backup. Key dostupný rovnakému compromised production administratorovi znižuje isolation.

## 12. Kubernetes encryption boundary

Kubernetes Secret values sú base64 representation. API-layer encryption at rest musí byť explicitne configured. KMS v2 používa envelope model pre data uložené v etcd.

```text
etcd ciphertext
→ chráni etcd/storage-only compromise
→ API server authorized read decryptne object
→ kubelet projektuje plaintext do Podu
→ application alebo debug path môže key čítať
```

Zmena EncryptionConfiguration automaticky nepreukazuje rewrite existing objects. Provider order, data rewrite generation, old key retention a restore musia byť overené.

At-rest encryption neodoberá RBAC `get/list/watch`, Pod-mount, exec, node alebo backup access.

## 13. TLS in transit

TLS poskytuje endpoint authentication, key establishment a record confidentiality/integrity:

```text
client validates certificate chain a hostname
→ handshake vytvorí shared secrets
→ session keys chránia application records
```

Certificate chain bez hostname/SAN matchu neautentizuje intended service. Vypnuté hostname verification ponecháva active MITM path.

TLS terminator je plaintext boundary. Re-encryption vytvára nový proxy–backend TLS session; passthrough nechá L4 intermediate bez plaintextu. Service mesh mTLS chráni iba paths, ktoré skutočne prechádzajú proxies a nie sú v permissive/plaintext mode.

mTLS identifikuje endpoint key. Business authorization, tenant a initiating user stále rieši application policy.

## 14. TLS 1.3, forward secrecy a 0-RTT

TLS 1.3 oddeľuje certificate authentication, ephemeral key agreement a AEAD record protection. Long-term certificate key nešifruje priamo celý traffic.

Ephemeral key agreement poskytuje forward secrecy proti neskoršiemu compromise certificate keyu pre zaznamenané sessions. Nechráni endpoint compromised počas session ani plaintext logs.

0-RTT early data môže byť replayed. Payment approval, secret rotation, one-time grant alebo iná state-changing operation nemá byť defaultne povolená v 0-RTT bez application replay protection.

## 15. Signing a verification trust

Digital signature acceptance lifecycle:

```text
artifact class a signer identity
→ exact signing key/purpose generation
→ private-key authorization
→ signature nad canonical subjectom/contextom
→ public-key publication pod trusted identity
→ verifier key, algorithm a subject binding
→ semantic authorization
```

Signature verification sama nepreukazuje správny issuer, entity, environment alebo purpose. OIDC potrebuje `iss`/`aud`; SAML potrebuje entity/metadata/audience/recipient. Shared verification key bez identity bindingu je incomplete trust model.

## 16. Worked failure — encryption green, trust boundary broken

Atlas cluster používal Kubernetes KMS v2 encryption at rest. API server, kubelet a IdP traffic používali TLS s validnými certificates. Storage a transport controls boli technicky účinné.

Napriek tomu `FED-SIGN-07` unikol:

```text
KMS decrypt pre authorized API server
→ authorized Secret read pre kubelet
→ authorized projection do attacker-created Podu
→ plaintext private key file
→ key copy mimo cluster
```

Key bol navyše použitý pre staging aj production a pre OIDC aj SAML. Attacker therefore získal signing authority naprieč štyrmi trust subjects.

Production verifiers overili signatures, ale OIDC RP neoverilo exact issuer a SAML SP neviazalo key na exact metadata entity. `Encryption enabled` tak chránilo storage a packet path, ale nie authorization, plaintext runtime ani key-purpose separation.

## 17. Competing hypotheses a discriminating evidence

Hypotézy:

1. KMS master-key compromise;
2. etcd ciphertext decryptnutý offline;
3. TLS interception;
4. weak RSA algorithm;
5. private key export z authorized Pod pathu;
6. verifier trust-binding defect.

Evidence:

- KMS audit neukázal attacker principal ani unauthorized cryptographic request;
- etcd remained ciphertext a storage snapshot neunikol;
- TLS certificate/hostname validation bola successful;
- private-key fingerprint z incident copy sedel s projected Secretom;
- Kubernetes audit dokázal Pod create, mount a exec chain;
- rovnaký public key bol v staging/prod JWKS a SAML metadata;
- production sessions prijali artifacts s wrong issuer/entity.

Root cause je shared exportable key a incomplete authorization/trust binding. KMS/TLS neboli broken; chránili iné threat boundaries.

## 18. Evidence-preserving containment

- disable new signing operations `FED-SIGN-07`;
- odstrániť key z verifier trustu podľa coordinated emergency procedure;
- quarantine workloads, ServiceAccounts a nodes involved v plaintext access path-e;
- preserve-nuť key fingerprint, KMS/API/kubelet audit, Pod UID, trust metadata/JWKS generations a session artifacts hashes;
- revoke-nuť affected OIDC/SAML sessions a downstream credentials;
- neodstrániť old public key bez inventory historical verification/recovery requirement;
- neprepnúť transport alebo signature validation do insecure compatibility mode.

## 19. Authoritative recovery

1. vytvoriť independent non-exportable keys per environment a protocol purpose;
2. zúžiť KMS/HSM `Sign` policy na exact issuer workload identity;
3. odstrániť private-key Secret projection, ak signing service/HSM supports required protocol;
4. publikovať new OIDC JWKS a SAML metadata s bounded overlapom;
5. overiť loaded signer generation na každej issuer replica;
6. overiť loaded verifier generation na každej RP/SP replica;
7. odstrániť old key z signing aj trust paths;
8. revoke-nuť sessions/artifacts z exposure interval-u;
9. testovať storage restore, key hierarchy recovery a emergency disable;
10. vykonať second rotation bez cross-purpose reuse.

## 20. Acceptance verdict

- etcd backup bez KMS authorization zostáva nečitateľný;
- authorized API read stále podlieha least privilege a indirect Pod tests;
- old `FED-SIGN-07` nedokáže vytvoriť accepted OIDC ani SAML artifact;
- each environment/protocol akceptuje iba vlastný key a identity context;
- wrong nonce/AAD/tag, key version alebo signature context zlyhá;
- TLS client odmietne wrong hostname, chain a plaintext fallback;
- new signing keys zostávajú non-exportable a audit ukazuje exact workload actor-a;
- backup/restore zachová current data bez resurrectovania revoked trust;
- second key rollover prejde bez outage-u a bez old-key acceptance;
- pôvodný settlement workflow funguje a forged/cross-environment paths zlyhávajú.

## 21. Troubleshooting flow

### Decrypt alebo verify failure

```text
asset/artifact a format generation
→ algorithm/mode/purpose
→ key ID/version/state
→ nonce/tag/AAD alebo signed subject
→ caller identity a authorization
→ KMS/HSM/store availability
→ consumer loaded generation
→ semantic identity/resource binding
```

### TLS failure

```text
DNS a endpoint
→ protocol/cipher negotiation
→ SNI
→ certificate chain
→ hostname/SAN
→ validity/time
→ trust store
→ mTLS identity
→ ALPN/application protocol
```

### Kubernetes at-rest failure

```text
EncryptionConfiguration/provider order
→ API server loaded generation
→ KMS plugin health/policy
→ object ciphertext prefix
→ existing-object rewrite state
→ old key/provider retention
→ restore read-back
```

## 22. Crypto agility a post-quantum planning

Crypto agility znamená inventory algorithms, protocols, keys a protected data a schopnosť vykonať dual-trust/dual-read migration bez uncontrolled outage alebo data loss.

NIST FIPS 203, 204 a 205 štandardizujú ML-KEM, ML-DSA a SLH-DSA. Adoption nie je simple algorithm toggle. Potrebuje protocol support, key/certificate formats, performance, interoperability, inventory a data-confidentiality lifetime analysis.

Hardcoded algorithm alebo key without format version komplikuje akúkoľvek future migration, nielen post-quantum transition.

## 23. Earlier controls

- cryptographic inventory s ownerom, purpose a consumers;
- independent keys per environment, tenant a protocol;
- non-exportable private keys pre high-impact signing;
- encryption context/AAD a nonce tests;
- verifier tests pre wrong identity s valid signature;
- TLS hostname a plaintext-leg canaries;
- KMS policy a indirect Kubernetes access analysis;
- key rollover, emergency disable a restore rehearsal;
- old-key forbidden-path test po každej migration.

## 24. Anti-patterny

### Base64 je encryption

Je to iba representation.

### AES-256 checkbox

Mode, nonce, tag, key authorization a plaintext boundary zostávajú.

### KMS/HSM vyrieši compromised application

Authorized malicious operation môže byť stále úspešná.

### TLS všade, hostname verification vypnuté

Active MITM zostáva možný.

### Jeden key pre viac purposes a environments

Compromise prekročí trust domains.

### Key rotated = old trust odstránený

Verifiers, sessions, backups a caches môžu old generation stále používať.

## 25. Kontrolné otázky

1. Ako sa encryption, hash, MAC a signature líšia?
2. Aké threats riešia at-rest, in-transit a in-use controls?
3. Prečo AEAD potrebuje správny nonce a AAD?
4. Ako DEK, KEK, rewrap a rekey súvisia?
5. Čo KMS a HSM chránia a čo nie?
6. Prečo key purpose a environment separation znižujú blast radius?
7. Čo je plaintext boundary pri TLS a Kubernetes Secret-e?
8. Prečo valid signature nepreukazuje správny issuer alebo entity?
9. Ako sa routine rotation líši od compromise revocation?
10. Čo musí overiť cryptographic acceptance verdict?

## Glossary impact

Relevantné pojmy: cryptographic protection subject, plaintext boundary, key-purpose generation, cross-environment key reuse, non-exportable key boundary, verifier trust generation, cryptographic acceptance verdict, old-key forbidden path, rewrap/rekey distinction a protection-state verdict.

## Primárne zdroje

- [NIST SP 800-57 Part 1 Rev. 5 — Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
- [NIST SP 800-38D — GCM and GMAC](https://csrc.nist.gov/pubs/sp/800/38/d/final)
- [RFC 8446 — TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
- [Kubernetes encrypting confidential data at rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
- [Kubernetes KMS provider](https://kubernetes.io/docs/tasks/administer-cluster/kms-provider/)
- [FIPS 203 — ML-KEM](https://csrc.nist.gov/pubs/fips/203/final)
- [FIPS 204 — ML-DSA](https://csrc.nist.gov/pubs/fips/204/final)
- [FIPS 205 — SLH-DSA](https://csrc.nist.gov/pubs/fips/205/final)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Secrets management](secrets-management.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Vulnerability a patch management →](vulnerability-and-patch-management.md)
<!-- KNOWLEDGE-NAVIGATION:END -->