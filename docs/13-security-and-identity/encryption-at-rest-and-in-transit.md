# Encryption at rest a in transit

Encryption chráni confidentiality transformáciou plaintextu na ciphertext pomocou cryptographic algoritmu a keyu. Moderný návrh má zároveň chrániť integrity ciphertextu, pretože attacker nesmie vedieť data meniť bez detekcie.

„Encryption enabled“ nie je kompletný security control. Účinnosť závisí od threat modelu, cryptographic boundary, key lifecycle-u, authorization, plaintext accessu, audit evidence a recovery. Full-disk encryption môže chrániť odcudzený vypnutý notebook, ale nie data čítané compromised processom po odomknutí systému.

```text
data asset a threat model
→ určiť at-rest / in-transit / in-use boundary
→ zvoliť authenticated cryptographic mechanism
→ vytvoriť a chrániť key material
→ autorizovať encrypt/decrypt alebo session establishment
→ auditovať key a plaintext access
→ rotate, revoke, archive alebo destroy keys
→ testovať recovery a compromise response
```

## 1. Security properties cryptography

Encryption primárne poskytuje confidentiality: bez správneho keyu nemá attacker získať plaintext. Authenticated encryption pridáva integrity a authenticity ciphertextu.

Cryptography môže poskytovať rôzne properties:

- confidentiality — data nie sú čitateľné neautorizovaným actorom;
- integrity — zmena data je detegovateľná;
- origin authentication — receiver overí, ktorý key holder message vytvoril;
- peer authentication — endpoint overí identity druhej strany;
- non-repudiation v obmedzenom právnom/technical zmysle pri signatures;
- key establishment — parties vytvoria shared secret cez nedôveryhodný channel.

Jeden algorithm alebo product neposkytuje automaticky všetky properties. AES-GCM chráni data, ale nevyrieši, komu KMS dovolí decrypt. TLS autentizuje endpoint podľa certificate validation, ale application stále potrebuje user authorization.

## 2. Data at rest, in transit a in use

**Data at rest** sú persistentné alebo dlhšie uložené data: disks, database files, logs, object storage, snapshots, backups, queues, indexes, container layers, swap a crash dumps.

**Data in transit** sa prenášajú medzi components: client a server, service a service, application a database, control plane a node, replication stream alebo CI runner a registry.

**Data in use** sú plaintext v process memory, CPU registers, caches alebo application objects počas spracovania. Bežné storage a transport encryption ich pred compromised authorized processom nechráni.

Tieto states sa prekrývajú. TLS decryptne request na serveri a data sa stanú „in use“. Application ich môže zapísať do logu, kde sa z nich stanú ďalšie „at rest“ copy.

## 3. Threat model pred výberom algoritmu

Najprv definuj attacker-a a boundary. At-rest threats môžu byť stolen disk, leaked backup, unauthorized object-storage access, media disposal alebo cross-tenant storage failure.

In-transit threats zahŕňajú packet capture, man-in-the-middle, DNS/routing manipulation, rogue proxy, compromised trust store, downgrade alebo plaintext segment za TLS terminatorom.

In-use threats zahŕňajú compromised application, memory dump, debug endpoint, overprivileged operator alebo injection, ktorá prinúti application vykonať authorized decrypt.

Rovnaký control má inú hodnotu proti rôznym threats. Disk encryption chráni lost device, ale nie root account na running hoste. Application-level field encryption môže chrániť pred database operatorom, ale application runtime sa stáva high-value plaintext boundary.

## 4. Encryption nie je encoding

Encoding mení representation pre transport alebo compatibility a nepoužíva secret key. Base64, hexadecimal a URL encoding neposkytujú confidentiality.

```text
Base64(secret)
→ každý ho vie dekódovať

Encrypt(secret, key)
→ plaintext získa iba actor s vhodným key accessom
```

Base64 sa často používa na serialization encrypted bytes alebo Kubernetes Secret fields. To nemení jeho security property.

## 5. Encryption, hashing, MAC a signature

**Encryption** je reverzibilná transformácia s keyom. **Hash** vytvára one-way digest bez secret keyu. **Message Authentication Code — MAC** používa shared secret na integrity a origin authentication medzi parties, ktoré key zdieľajú. **Digital signature** používa private key na podpis a public key na verification.

Hash sám nepreukazuje origin: attacker môže zmeniť file aj publikovaný hash. Signature alebo authenticated metadata viažu digest na trusted identity.

Encryption bez authentication môže umožniť controlled modification ciphertextu alebo oracle attacks. Pre nové designs preferuj approved authenticated encryption scheme namiesto ručného skladania cipher + checksum.

## 6. Symmetric cryptography

Symmetric cryptography používa rovnaký secret alebo closely related key material na encryption a decryption. Je efektívna pre bulk data.

Main challenge je distribution a lifecycle. Každý actor s decrypt keyom môže čítať data a pri shared MAC keyu môže vytvárať validné messages. Shared key preto často neposkytuje precise attribution medzi participants.

Examples authenticated symmetric algorithms sú AES-GCM a ChaCha20-Poly1305. Bezpečnosť závisí aj od nonce rules, tag validation a usage limits, nie iba od key size.

## 7. Asymmetric cryptography

Asymmetric cryptography používa public/private key pair. Public key možno distribuovať, private key musí zostať chránený.

Používa sa na digital signatures, key agreement a key encapsulation. Bulk data sa zvyčajne nešifrujú priamo public-key algorithmom; asymmetry vytvorí shared secret a následne sa použije symmetric AEAD.

Private key compromise umožní podľa use case-u podpisovať, decryptovať alebo impersonovať. Jeden key nemá byť automaticky používaný na viac purposes; key usage a policy majú byť explicitné.

## 8. Hybrid cryptography

Reálne protocols kombinujú asymmetric a symmetric mechanisms:

```text
asymmetric key agreement alebo KEM
→ vytvorí shared secret
→ KDF odvodí session keys
→ symmetric AEAD chráni bulk traffic
```

TLS 1.3 je hybridný protocol v tomto zmysle. Certificate signature autentizuje endpoint, ephemeral key agreement vytvára shared secret a AEAD chráni records.

„RSA certificate“ neznamená, že celý traffic je RSA-encrypted. Certificate algorithm, key exchange a data-encryption cipher sú samostatné choices.

## 9. AEAD

Authenticated Encryption with Associated Data — AEAD — poskytuje confidentiality plaintextu a integrity ciphertextu aj additional authenticated data.

Encryption vytvorí ciphertext a authentication tag. Decryption najprv overí tag; pri failure nesmie application použiť plaintext.

AAD sa nešifruje, ale je cryptographically viazané k ciphertextu. Môže obsahovať tenant ID, record ID, message type, protocol version alebo key version.

```text
ciphertext pre tenant A
+ AAD tenant=A
→ validation zlyhá, ak sa data interpretujú ako tenant B
```

AAD representation musí byť canonical. Odlišné ordering alebo encoding spôsobí legitimate validation failures.

## 10. Nonce a IV

Nonce alebo Initialization Vector je per-operation value používaná s keyom. Nemusí byť secret, ale scheme určuje, či musí byť unique, unpredictable alebo oboje.

Pri AES-GCM reuse rovnakého nonce pod rovnakým keyom môže odhaliť plaintext relationships a umožniť tag forgery. Distributed system preto potrebuje collision-safe generation strategy.

Random 96-bit nonce s secure RNG môže byť vhodný pri bounded operation count. Counter-based scheme potrebuje koordináciu a persistence cez restarts. Usage limit má vyvolať key rotation skôr, než collision risk narastie.

## 11. Key separation

Jeden key nemá byť používaný na unrelated purposes, tenants alebo environments bez explicitného analysis. Compromise potom zasiahne všetky domains a misuse môže porušiť algorithm assumptions.

Key separation možno dosiahnuť independent keys alebo derivation z master secretu s domain-separated contextom.

```text
master secret
→ KDF(context="tenant-A:data")
→ tenant A data key

master secret
→ KDF(context="tenant-B:data")
→ tenant B data key
```

KDF context musí byť unambiguous a versioned. Derived keys stále závisia od ochrany master keyu.

## 12. Key a ciphertext separation

Ciphertext a key material nemajú byť v rovnakej compromise boundary s rovnakými permissions.

```text
ciphertext v database alebo object storage
→ DEK chránený KEK-om
→ KEK v KMS/HSM s oddeleným IAM a auditom
```

Separation je meaningful iba pri odlišných identities, administrators a access paths. Ak application account má broad database read aj unrestricted KMS decrypt, compromise applicationu stále odhalí všetky data.

Defense value je často ochrana proti storage-only compromise, backup leak alebo limited operator role, nie proti fully compromised application.

## 13. DEK, KEK a envelope encryption

Data Encryption Key — DEK — šifruje payload. Key Encryption Key — KEK — wrapuje DEK alebo iný key material.

Envelope encryption flow:

```text
workload vygeneruje alebo získa DEK
→ lokálne encryptne data pomocou AEAD
→ KMS wrapne DEK pomocou KEK
→ uloží ciphertext, wrapped DEK, nonce, tag a metadata
→ pri čítaní authorized workload požiada o unwrap
→ decrypt vykoná v controlled process memory
```

Výhody sú výkon a centralizovaný KEK authorization. Rewrap umožní rotate KEK bez re-encryption všetkých payloads.

Risks sú plaintext DEK v memory, broad decrypt permission, unsafe cache a missing AAD/encryption context.

## 14. KMS

Key Management Service poskytuje creation/import keys, policies, cryptographic operations, versions, rotation, disable/delete states a audit.

KMS centralizuje control, ale application stále rozhoduje, kedy požiada o decrypt. Ak compromised application má validnú permission a correct context, KMS môže operation oprávnene vykonať.

Policy má obmedziť principal, operation, key, environment a encryption context. `kms:Decrypt` na všetky keys je opakom least privilege.

KMS availability je application dependency. Cache a degraded mode musia byť navrhnuté podľa data criticality a revocation requirements.

## 15. HSM

Hardware Security Module — HSM — je tamper-resistant hardware boundary pre key generation, storage a cryptographic operations s obmedzeným exportom key materialu.

HSM znižuje risk key extraction, ale nezabráni authorized malicious signing alebo decrypt requestu. Access control, quorum a audit zostávajú potrebné.

Cloud KMS môže používať HSM-backed keys, ale KMS je management service a HSM je cryptographic boundary. Pojmy nie sú synonymá.

## 16. Key metadata a inventory

Key inventory musí vedieť:

- stable key ID a versions;
- ownera a business purpose;
- algorithm, strength a allowed operations;
- environment a tenant scope;
- activation, expiration a cryptoperiod;
- parent KEK alebo trust root;
- consumers a protected data sets;
- backup/recovery policy;
- compromise, disable a deletion state.

Metadata sú security-relevant. Zámena key purpose alebo environmentu môže byť rovnako nebezpečná ako leakage raw key bytes.

## 17. Key lifecycle

Key lifecycle:

```text
requirements a classification
→ generation alebo import
→ registration a activation
→ authorized use
→ rotation / rekey / rewrap
→ deactivation
→ archival alebo recovery retention
→ revocation pri compromise
→ destruction
```

Key creation bez retirement planu vedie k permanentne active keys. Deletion bez dependency mappingu môže spôsobiť irreversible data loss.

Lifecycle events majú byť auditované a podľa impactu chránené separation of duties alebo delayed deletion.

## 18. Key generation

Keys musia vzniknúť z approved cryptographically secure random source alebo approved derivation mechanismu. Timestamp, username, predictable PRNG a human-generated phrase nie sú vhodný raw key material.

Generation environment musí chrániť seed, entropy source a output. Imported key potrebuje secure transfer a evidence originu.

Key size musí zodpovedať algorithmu a required security strength. „Viac bitov“ nevyrieši broken mode, nonce reuse alebo key exposure.

## 19. Cryptoperiod

Cryptoperiod je obdobie alebo usage limit, počas ktorého key smie vykonávať operations. Závisí od algorithmu, data volume, threat exposure, protected-data lifetime a ability revoke.

Session key môže žiť minúty. Database KEK roky s controlled rotation. Certificate private key má validity a operational lifecycle.

Rotation interval bez usage a threat modelu je arbitrary compliance ritual. Naopak permanentný key zvyšuje accumulated exposure a incident scope.

## 20. Rotation, rekey, re-encryption a rewrap

**Rotation** aktivuje novú key version pre nové operations. **Rekey** nahrádza key alebo hierarchy. **Re-encryption** decryptuje data starým keyom a encryptuje novým. **Rewrap** ponechá DEK, ale wrapne ho novým KEK-om.

```text
full re-encryption
→ mení payload ciphertext a je drahšie

DEK rewrap
→ mení iba envelope a je lacnejšie
```

Read path musí vedieť vybrať historical key version. Write path má používať current active version. Rotation bez version metadata spôsobí data loss alebo manual guessing.

## 21. Revocation a compromise

Compromise response nie je iba create new key:

```text
zastaviť nové use compromised keyu
→ identifikovať protected data, certificates a consumers
→ určiť exposure interval
→ revoke/disable a obmedziť sessions
→ rekey, rewrap alebo re-encrypt
→ redeploy consumers
→ overiť starú cestu ako neplatnú
→ zachovať audit evidence
```

Rotation obmedzí future impact, ale nevráti leaked plaintext. Signing-key compromise môže zneplatniť trust k artifacts vytvoreným počas exposure interval-u.

## 22. Backup a key recovery

Encrypted backup je obnoviteľný iba spolu s keys, trust roots, KMS/HSM availability, IAM a configuration metadata.

Restore test musí pokrývať historical key versions a disaster scenario. Backup stored v region-e A s key dostupným iba cez destroyed region-A control plane nie je recoverable design.

Key backup/escrow zvyšuje availability, ale vytvára ďalšiu compromise path. Split knowledge, quorum a offline storage môžu znižovať risk podľa use case-u.

## 23. Crypto-shredding

Crypto-shredding zneprístupní ciphertext zničením všetkých potrebných key copies. Je useful pre large encrypted datasets, kde physical overwrite každej replica nie je practical.

Funguje iba pri úplnom key inventory. Backups, exports, caches, escrow alebo copied plaintext môžu zachovať alternate path.

Deletion keyu musí byť deliberate, auditované a po retention checks. Accidental crypto-shredding je irreversible availability incident.

## 24. Full-disk a volume encryption

Full-disk encryption chráni device, keď je vypnutý alebo locked. Boot authentication odomkne volume a running OS vidí plaintext.

Threaty, ktoré nerieši:

- malware po login-e;
- root/admin access;
- application authorization flaws;
- plaintext network transfer;
- copied backups mimo encrypted volume.

Volume encryption v cloud storage chráni media a snapshots podľa provider boundary. KMS access model určuje, kto môže attach/read volume.

## 25. File, record a field encryption

Jemnejšia granularita umožňuje oddeliť data sets a identities. File encryption chráni individual object, record/field encryption môže viazať key na tenant alebo data class.

Trade-offs sú key lookup, query/index support, rotation, migration, backup consistency a application complexity.

Granularity má nasledovať threat boundary. Encrypt každý field vlastným keyom bez operational tooling môže zhoršiť reliability viac než security zlepší.

## 26. Database encryption

Transparent Data Encryption chráni database files, WAL/transaction logs a backups pred storage-level compromise. Database engine decryptuje pages pre authorized operations.

TDE nechráni pred SQL accountom s `SELECT`, compromised database processom ani application accountom s broad access.

Application-level field encryption môže skryť plaintext pred database administrators a replicas, ale application/KMS boundary sa stane kritickou. Queries, indexes a analytics sa komplikujú.

## 27. Deterministic encryption

Randomized encryption vytvára pre rovnaký plaintext rozdielny ciphertext. Lepšie skrýva equality patterns.

Deterministic encryption umožňuje equality lookup, ale rovnaké plaintexty majú rovnaký ciphertext. Attacker vidí frequency a pri small domain môže hodnoty enumerate-nuť.

Použitie musí byť explicitný trade-off s domain-size analysis a access controls. Nie je to default pre convenience search.

## 28. Object storage, snapshots a backups

Data-copy graph zahŕňa live objects, replicas, versions, snapshots, cross-region copies, exports a lifecycle archives.

Encryption policy musí byť konzistentná cez celý graph. Primary bucket s customer-managed key nepomôže, ak export job uloží plaintext do analytics bucketu.

Key disable/delete môže zneprístupniť všetky copies. Lifecycle policy a retention musia byť coordinated s key lifecycle-om.

## 29. Logs, caches a temporary data

Plaintext často uniká do debug logs, traces, metrics labels, search indexu, Redis cache, temporary file-u, swapu, core dumpu, dead-letter queue alebo CI artifactu.

Data-flow inventory má zahrnúť derived a transient copies. „Database is encrypted“ nie je statement o celom data lifecycle.

Redaction má prebehnúť pred telemetry exportom. Encrypted observability backend nechráni sensitive value pred broad dashboard userom.

## 30. Multi-tenant encryption

Tenant-specific keys môžu zmenšiť blast radius a podporiť crypto-shredding tenant data. Potrebujú stable tenant identity, key hierarchy, quotas a recovery.

Jedna global application key je jednoduchšia, ale compromise zasiahne všetkých tenants. Key-per-record môže byť operationally expensive.

AAD má viazať ciphertext na tenant a object context. Application authorization stále musí overiť, či caller smie požiadať o decrypt.

## 31. Data in use

Po decrypt-e sa plaintext nachádza v process memory a môže byť dostupný debuggeru, memory dumpu, compromised dependency alebo injection útoku.

Controls zahŕňajú least privilege, process isolation, minimal plaintext lifetime, memory-safe code, disabling unsafe dumps, protected enclaves podľa threat modelu a strict logging.

Confidential computing môže chrániť memory pred určitými host/hypervisor threats, ale neprenáša automaticky trust do application code-u. Remote attestation a key release policy sú ďalšie boundaries.

## 32. TLS security model

TLS chráni application traffic medzi two endpoints. Poskytuje server authentication, optional client authentication, key establishment a record confidentiality/integrity.

```text
client validates server certificate a hostname
→ handshake establishes shared secrets
→ session keys are derived
→ AEAD protects application records
```

TLS endpoint je plaintext boundary. Reverse proxy môže decryptnúť external TLS a poslať plaintext backendu, ak internal leg nie je chránený.

## 33. TLS 1.3 handshake

TLS 1.3 odstraňuje legacy algorithms a skracuje handshake. ClientHello ponúkne protocol/cipher parameters a key share. ServerHello vyberie parameters a key share; parties odvodia handshake secrets.

Server posiela certificate a CertificateVerify signature, ktorou dokazuje control private keyu nad handshake transcriptom. Finished messages overujú integrity handshake-u.

Po úspechu parties odvodia application traffic secrets. Certificate iba viaže public key na identity claims; client musí validovať chain, validity, hostname a usage.

## 34. Certificate chain a trust store

Server certificate je podpísaný intermediate CA, ktorá chainuje k trusted root v client trust store. Root sa zvyčajne neposiela a je trust bootstrap.

Validation zahŕňa:

- signatures v chain-e;
- validity periods;
- hostname/SAN match;
- key usage a extended key usage;
- basic constraints;
- algorithm policy;
- revocation/status policy podľa environmentu.

Installing private CA root do broad trust store dáva tejto CA authority nad všetky relevantné names. Root distribution je high-impact change.

## 35. Hostname validation

Valid certificate chain pre `example.com` nesmie autentizovať `payments.internal`, ak SAN neobsahuje expected name.

Client, ktorý vypne hostname verification, chráni traffic iba proti passive observerovi, nie proti active MITM s ľubovoľným trusted certificate-om.

IP access, wildcard certificates a service aliases potrebujú explicitný identity design. SNI určuje requested server name počas connection setupu, ale nie je replacement za certificate validation.

## 36. mTLS

Mutual TLS vyžaduje certificate od servera aj clienta. Obe strany cryptographically autentizujú endpoint key.

mTLS poskytuje service/device identity a encrypted channel, ale neurčuje business permissions, tenant scope ani user delegation. Application alebo proxy policy mapuje certificate identity na actions/resources.

Certificate issuance a rotation sú kritické. Long-lived shared client certificate znižuje attribution a revocation granularity.

## 37. TLS termination, re-encryption a passthrough

**Termination** decryptuje TLS na load balanceri/proxy. Backend leg môže byť plaintext alebo nový TLS session.

**Re-encryption** vytvorí separate TLS connection proxy → backend. Chráni internal transit, ale proxy stále vidí plaintext.

**Passthrough** prenáša encrypted stream k backendu bez decryption na intermediate L4 component-e. Znižuje proxy visibility a L7 routing capabilities.

Vyber podľa plaintext boundary, inspection, certificate ownership, network threat a operational requirements.

## 38. Forward secrecy

Forward secrecy znamená, že neskorší compromise long-term certificate private keyu neumožní decrypt historical sessions, ak attacker iba zaznamenal traffic a sessions použili ephemeral key agreement.

TLS 1.3 bežne používa ephemeral (EC)DHE. Long-term key autentizuje handshake, ale session secret závisí od ephemeral private values, ktoré sa po use zahodia.

Forward secrecy nechráni sessions, ak endpoint bol compromised počas session alebo plaintext bol logovaný.

## 39. Session resumption a tickets

TLS resumption znižuje handshake latency použitím PSK odvodeného z previous session alebo session ticketu.

Ticket encryption keys sa stávajú security assets. Shared keys across fleet umožnia resumption na viacerých servers, ale zväčšia blast radius.

Ticket lifetime a rotation ovplyvňujú forward secrecy a revocation. Certificate revoke nemusí okamžite ukončiť already established/resumable sessions podľa implementation.

## 40. TLS 1.3 0-RTT

0-RTT umožňuje clientovi poslať early data pri resumed session pred dokončením full handshake-u. Znižuje latency, ale early data môže byť replayed.

Používaj iba pre idempotentné operations alebo implementuj application-level replay protection. Payment, state change alebo one-time token exchange nie sú bezpečný default pre 0-RTT.

Server môže 0-RTT odmietnuť a client musí request retry-nuť podľa protocol semantics.

## 41. TLS downgrade a legacy protocols

Protocol downgrade vzniká, keď attacker alebo misconfiguration prinúti endpoints použiť slabšiu version/cipher. Disable unsupported legacy versions a weak algorithms.

Compatibility fallback musí byť explicitný a monitored. „Temporary TLS 1.0 endpoint“ bez ownera a expiry sa stáva permanentným riskom.

Cipher suite name v TLS 1.3 opisuje record AEAD/hash, nie certificate a key-exchange algorithm rovnakým spôsobom ako legacy TLS naming.

## 42. Secret a certificate rotation

Certificate rotation zahŕňa new key/certificate issuance, distribution, overlap, activation a removal old identity.

Overlap zabraňuje outage-u pri distributed rollout-e. Consumer trust a server cert changes musia byť coordinated.

Rotation testuj pred expiry. Alert na 30 dní nestačí, ak manual approval, HSM ceremony alebo device update trvá dlhšie.

Private key compromise vyžaduje revocation/deny, replacement a investigation issued signatures/sessions, nie iba renewal.

## 43. Service mesh mTLS

Service mesh môže automatizovať workload certificates a mTLS medzi proxies. Znižuje manual certificate management a poskytuje service identity.

Mesh nešifruje traffic, ktorý proxy bypassuje, host-network process alebo external path mimo mesh. Permissive mode môže akceptovať plaintext a znižovať assurance.

Application authorization, tenant scope a compromised proxy/node threats zostávajú. Mesh identity issuance a trust domain patria do threat modelu.

## 44. Kubernetes data at rest

Kubernetes API resources sú v etcd bez additional API-layer encryption, ak encryption configuration používa default `identity` provider. Base64 v Secret manifeste nie je encryption.

EncryptionConfiguration určuje resource types a providers. Existing data sa po zmene configuration automaticky neprepíšu; treba controlled rewrite.

Local raw key v control-plane config chráni proti etcd-only compromise, ale host compromise môže získať key. KMS provider oddeľuje KEK do external service a používa envelope encryption.

KMS v2 je stable od Kubernetes v1.29 a je preferovaný oproti deprecated KMS v1. KMS outage a cached DEKs majú explicitné availability/revocation semantics.

## 45. Kubernetes Secrets boundary

At-rest encryption chráni etcd storage, nie authorized API reads ani Pod access. RBAC `get`, `list` alebo `watch` Secrets je high-impact permission.

Workload môže získať Secret cez environment alebo volume; plaintext potom existuje v process environment/filesystem. Rotation vyžaduje update source, projection/reload a consumer behavior.

Node compromise môže odhaliť mounted secrets a workload memory. External secret provider alebo short-lived workload identity môže zmenšiť static secret exposure, ale pridáva availability dependency.

## 46. CI/CD a artifact encryption

CI logs, caches, artifacts a runner workspaces môžu obsahovať plaintext secrets alebo sensitive build outputs. Encryption backendu nerieši broad job access.

Build secrets používaj cez ephemeral secret mounts alebo identity federation. Nezapisuj ich do image layers, environment dumps ani provenance parameters.

Artifact encryption môže chrániť private binaries pri distribution, ale release consumer potrebuje key distribution a signature verification. Encryption nenahrádza artifact integrity a provenance.

## 47. Cryptographic agility

Crypto agility je schopnosť inventarizovať algorithms/keys/protocols a migrovať ich bez uncontrolled outage alebo data loss.

Potrebuje:

- cryptographic inventory;
- versioned algorithm identifiers;
- pluggable protocols/formats;
- dual-read/dual-trust migration;
- re-encryption/re-signing strategy;
- compatibility tests;
- deprecation policy;
- ownerov a timelines.

Hardcoded algorithm bez metadata komplikuje future migration. Data format musí vedieť, ktorou version/key bolo encrypted.

## 48. Post-quantum migration

Quantum-capable adversary by ohrozil widely used public-key algorithms pre key establishment a signatures. Symmetric algorithms potrebujú appropriate strength, ale hlavná migration sa týka public-key cryptography.

NIST v roku 2024 finalizoval FIPS 203 ML-KEM pre key establishment a FIPS 204/205 pre signatures. Adoption vyžaduje protocol a ecosystem support, performance testing, certificate/PKI decisions a inventory.

„Harvest now, decrypt later“ znamená, že long-lived sensitive traffic zachytený dnes môže byť targetom future decryption. Migration priority závisí od data confidentiality lifetime.

Hybrid classical + post-quantum mechanisms môžu znížiť transition risk, ale musia byť štandardne a bezpečne kombinované, nie ručne concatenate-nuté bez protocol analysis.

## 49. Cryptographic failure modes

Časté failures:

- nonce reuse;
- missing tag validation;
- hardcoded/shared keys;
- wrong AAD serialization;
- broad decrypt permissions;
- key deletion before data retention end;
- certificate hostname validation disabled;
- plaintext backend leg;
- stale trust store;
- unsupported legacy protocol fallback;
- backups bez keys alebo keys bez backups;
- secret leakage do logs/memory dumps;
- rotation, ktorá neaktualizuje consumers.

Cryptographic error message má byť diagnostikovateľná pre operatora, ale nemá vytvárať detailed oracle pre attacker-a.

## 50. Incident response

Pri key/certificate compromise:

```text
identifikovať key a purpose
→ zastaviť nové operations
→ určiť consumers, protected data a exposure interval
→ revoke/disable a zablokovať sessions
→ rotate/rekey/rewrap/re-encrypt
→ redeploy a reload consumers
→ hunt plaintext leakage alebo forged artifacts
→ overiť staré credentials ako neplatné
→ zachovať audit evidence
```

Pri storage ciphertext leak-u posúď, či key boundary ostala intact, algorithms/nonce usage sú validné a data lifetime odôvodňuje future cryptanalytic risk.

## 51. Kompletný príklad envelope encryption

Multi-tenant application ukladá tax documents.

1. Application vygeneruje random DEK pre document.
2. Encryptne document cez AEAD; AAD obsahuje tenant ID, document ID a schema version.
3. Pošle DEK do KMS `Encrypt/Wrap` s rovnakým encryption contextom.
4. Uloží ciphertext, nonce, tag, wrapped DEK a key version.
5. Read request prejde tenant authorization.
6. Application požiada KMS o unwrap s expected contextom.
7. Plaintext existuje iba krátko v process memory a nie je logovaný.
8. KEK rotation rewrapne DEKs bez full document re-encryption.
9. Incident disable keyu zablokuje new decrypt a audit ukáže affected tenants/documents.
10. Restore test overí historical wrapped DEKs, KMS policy a backup consistency.

## 52. Troubleshooting

Pri decrypt failure postupuj:

```text
ciphertext a format version
→ key ID/version a state
→ nonce/tag/AAD
→ caller identity a authorization
→ KMS/HSM availability
→ serialization/canonicalization
→ historical migration state
```

Pri TLS failure:

```text
DNS a endpoint
→ protocol/cipher negotiation
→ SNI
→ certificate chain
→ hostname/SAN
→ validity/time
→ trust store
→ mTLS client certificate
→ ALPN/application protocol
```

Pri Kubernetes decryption over EncryptionConfiguration provider order, key/KMS availability, data rewrite state a API server logs. Neodstraňuj old provider/key, kým všetky historical records neboli migrované a verified.

## 53. Časté anti-patterny

**Base64 equals encryption.** Representation sa zamieňa za confidentiality.

**AES-256 checkbox.** Mode, nonce, tag, key lifecycle a authorization sa ignorujú.

**Key vedľa ciphertextu s rovnakým accessom.** Separation je iba vizuálna.

**TDE equals application authorization.** SQL principal stále číta plaintext.

**TLS everywhere, hostname verification off.** Active MITM zostáva možný.

**One key for all tenants/environments.** Compromise má maximal blast radius.

**Rotation without historical read plan.** Data sa stanú nečitateľné.

**Encrypted backup without recovery keys.** Confidential, ale unrecoverable.

**KMS as magic security.** Compromised authorized application stále decryptuje.

## 54. Kontrolné otázky

1. Ako sa líšia data at rest, in transit a in use?
2. Prečo threat model predchádza výberu algoritmu?
3. Ako sa encryption, hash, MAC a signature líšia?
4. Čo poskytuje AEAD a akú úlohu má AAD?
5. Prečo je nonce reuse pri AES-GCM kritické?
6. Ako funguje envelope encryption?
7. Ako sa líšia KMS a HSM?
8. Čo musí obsahovať key inventory a lifecycle?
9. Ako sa rotation líši od re-encryption a rewrap?
10. Čo treba urobiť pri key compromise okrem rotation?
11. Aké threats rieši full-disk encryption a ktoré nie?
12. Prečo TDE nechráni pred authorized SQL principalom?
13. Aké leakage prináša deterministic encryption?
14. Ako TLS 1.3 autentizuje server a chráni records?
15. Prečo valid certificate chain bez hostname validation nestačí?
16. Čo mTLS dokazuje a čo neurčuje?
17. Kedy zvoliť termination, re-encryption alebo passthrough?
18. Aké riziko má TLS 1.3 0-RTT?
19. Ako funguje Kubernetes KMS envelope encryption?
20. Navrhni crypto-agility a PQC migration plan pre long-lived data.

## Glossary impact

Relevantné pojmy: plaintext, ciphertext, data at rest, data in transit, data in use, authenticated encryption, AEAD, nonce, initialization vector, authentication tag, Additional Authenticated Data, symmetric cryptography, asymmetric cryptography, hybrid cryptography, key separation, Data Encryption Key, Key Encryption Key, envelope encryption, key wrapping, Key Management Service, Hardware Security Module, key inventory, cryptoperiod, key rotation, rekey, re-encryption, rewrap, key revocation, key recovery, crypto-shredding, full-disk encryption, Transparent Data Encryption, deterministic encryption, TLS 1.3, certificate chain, trust store, hostname validation, mutual TLS, TLS termination, re-encryption, TLS passthrough, forward secrecy, session resumption, 0-RTT, Kubernetes EncryptionConfiguration, Kubernetes KMS v2, crypto agility, post-quantum cryptography a ML-KEM.

## Primárne zdroje

- [NIST SP 800-57 Part 1 Rev. 5 — Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
- [NIST SP 800-38D — GCM and GMAC](https://csrc.nist.gov/pubs/sp/800/38/d/final)
- [RFC 8446 — TLS 1.3](https://datatracker.ietf.org/doc/html/rfc8446)
- [RFC 9325 — Recommendations for Secure Use of TLS and DTLS](https://datatracker.ietf.org/doc/html/rfc9325)
- [Kubernetes Encrypting Confidential Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
- [Kubernetes KMS Provider](https://kubernetes.io/docs/tasks/administer-cluster/kms-provider/)
- [NIST FIPS 203 — ML-KEM](https://csrc.nist.gov/pubs/fips/203/final)
- [NIST Post-Quantum Cryptography Standards](https://csrc.nist.gov/News/2024/postquantum-cryptography-fips-approved)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Secrets management](secrets-management.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Vulnerability a patch management →](vulnerability-and-patch-management.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
