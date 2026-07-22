# Encryption at rest a in transit

Encryption chráni dôvernosť dát transformáciou plaintextu na ciphertext pomocou cryptographic algoritmu a keyu. Samotné zapnutie encryption však nevytvára kompletný security control. Účinnosť závisí od threat modelu, integrity protection, key lifecycle-u, identity a authorization boundaries, recovery a od miest, kde sa plaintext stále objavuje.

## 1. Mentálny model

```text
data asset
→ určiť stav dát a threat model
→ zvoliť cryptographic boundary
→ vytvoriť a chrániť keys
→ encrypt + authenticate data alebo channel
→ autorizovať decrypt/use operation
→ auditovať key a plaintext access
→ rotate, revoke, archive alebo destroy keys
→ pravidelne overovať recovery a účinnosť controlov
```

Encryption môže chrániť confidentiality a pri authenticated encryption aj integrity ciphertextu. Sama však neurčuje, kto smie plaintext použiť, nechráni kompromitovaný application process a nerieši availability pri strate keyu.

## 2. Data at rest, in transit a in use

### Data at rest

Persistentné alebo dlhšie uložené dáta:

- disks a filesystems,
- database files a transaction logs,
- object storage,
- snapshots a backups,
- queues a indexes,
- container layers,
- swap a crash dumps.

### Data in transit

Dáta prenášané medzi komponentmi:

- client ↔ server,
- service ↔ service,
- application ↔ database,
- node ↔ control plane,
- replication a backup streams,
- CI runner ↔ registry.

### Data in use

Plaintext spracúvaný v CPU, process memory, cache alebo application runtime. Bežné at-rest a transport encryption ho pred autorizovaným alebo kompromitovaným procesom nechráni.

## 3. Threat model pred algoritmom

Najprv definuj, pred čím má encryption chrániť.

At-rest threats:

- odcudzený disk alebo notebook,
- uniknutý snapshot či backup,
- neoprávnený storage access,
- chybná likvidácia média,
- cross-tenant storage failure.

In-transit threats:

- passive packet capture,
- man-in-the-middle,
- DNS alebo routing manipulation,
- rogue proxy,
- kompromitovaná CA alebo trust store,
- downgrade,
- ukradnutý TLS private key,
- plaintext segment za TLS terminatorom.

Full-disk encryption napríklad chráni vypnuté zariadenie, ale typicky nechráni dáta pred root používateľom na odomknutom systéme.

## 4. Encryption nie je encoding

Encoding mení reprezentáciu dát pre transport alebo kompatibilitu. Base64, hexadecimal a URL encoding nemajú secret key a neposkytujú confidentiality.

```text
Base64(secret) ≠ encrypted secret
```

## 5. Encryption, hashing, MAC a digital signature

- **Encryption** je reverzibilná transformácia s keyom určená primárne na confidentiality.
- **Cryptographic hash** je jednosmerný digest bez secret keyu.
- **MAC** je keyed integrity a authenticity control.
- **Digital signature** poskytuje asymmetric integrity a origin authentication.

Encryption bez authentication môže umožniť nepozorovanú manipuláciu ciphertextu. Pre nové návrhy preferuj authenticated encryption.

## 6. Symmetric, asymmetric a hybrid cryptography

Symmetric cryptography používa rovnaký secret key na encryption a decryption. Je výkonná a vhodná pre bulk data, ale potrebuje bezpečný key distribution model.

Asymmetric cryptography používa public/private key pair na signatures, authentication a key establishment alebo encapsulation.

Reálne systémy často používajú hybridný model:

```text
asymmetric mechanism
→ vytvorí alebo prenesie shared secret
→ symmetric AEAD chráni bulk data
```

Samotný názov `AES-256` nepopisuje bezpečný návrh. Rozhodujú aj mode, nonce, authentication tag, key generation, storage a lifecycle.

## 7. Authenticated Encryption with Associated Data — AEAD

AEAD poskytuje:

- confidentiality plaintextu,
- integrity ciphertextu,
- authentication tag,
- integrity pre Additional Authenticated Data.

Príklady sú AES-GCM a ChaCha20-Poly1305. Decryption musí zlyhať, ak tag nie je validný. Aplikácia nesmie použiť unauthenticated plaintext ani vytvárať detailnými chybami cryptographic oracle.

## 8. Nonce a Initialization Vector

Nonce alebo IV sa používa spolu s keyom a algoritmom. Podľa schémy musí byť unikátny, nepredvídateľný alebo oboje; nemusí byť secret.

Pri AES-GCM je reuse rovnakého nonce s rovnakým keyom kritické zlyhanie. Distributed systém preto potrebuje explicitnú nonce-allocation stratégiu, nie iba lokálny counter bez koordinácie.

## 9. Additional Authenticated Data — AAD

AAD sa nešifruje, ale je cryptographically viazané k ciphertextu.

Vhodné hodnoty:

- tenant ID,
- record ID,
- object type,
- schema alebo protocol version,
- key version.

```text
ciphertext pre tenant A
+ AAD tenant=A
→ nesmie byť použiteľný ako tenant B
```

AAD musí mať stabilnú canonical representation. Rozdielna serializácia spôsobí validation failure.

## 10. Key a ciphertext separation

Key a ciphertext nemajú byť v rovnakej compromise boundary s rovnakými permissions.

```text
ciphertext v storage
→ DEK chránený KEK-om
→ KEK v KMS/HSM s oddeleným IAM a auditom
```

Oddelenie má význam iba pri odlišných identities, administrators, permissions, audit paths a recovery postupoch.

## 11. DEK, KEK a envelope encryption

**Data Encryption Key — DEK** šifruje application dáta. **Key Encryption Key — KEK** chráni DEK alebo iný key material.

Envelope encryption:

```text
workload získa alebo vygeneruje DEK
→ lokálne zašifruje payload
→ KMS/HSM wrap-ne DEK pomocou KEK
→ uloží ciphertext + wrapped DEK + metadata
→ pri čítaní autorizovaný workload unwrap-ne DEK
→ decrypt vykoná v controlled runtime
```

Výhodou je výkon, centralizovaný KEK access control a jednoduchšia rotation. Rizikom zostáva plaintext DEK v memory, neobmedzený cache, broad decrypt permission a nesprávny encryption context.

## 12. KMS a HSM

KMS poskytuje key creation/import, cryptographic operations, policies, rotation, lifecycle states a audit. HSM je hardware security boundary určená na ochranu keys a vykonávanie operations s obmedzeným exportom key materialu.

HSM nezabráni škodlivej autorizovanej decrypt operácii, plaintext leakage v aplikácii ani príliš broad policy. KMS môže HSM používať, ale pojmy nie sú totožné.

## 13. Key lifecycle

```text
classification a requirements
→ generation alebo import
→ activation
→ use
→ rotation alebo rekey
→ deactivation
→ archival podľa retention
→ revocation pri compromise
→ destruction
```

Každý key potrebuje ownera, účel, algorithm, environment, allowed operations, version, activation/expiry, parent KEK, backup policy a compromise state.

## 14. Key generation a cryptoperiod

Keys musia vzniknúť z cryptographically secure random source alebo schváleného derivation mechanismu. Timestamps, usernames, predictable PRNG a ručne zadané krátke strings nie sú bezpečný zdroj.

Cryptoperiod je obdobie alebo usage limit, počas ktorého možno key používať. Závisí od množstva dát, algoritmu, exposure, možnosti revocation, data lifetime a impactu compromise. Neexistuje univerzálny rotation interval bez threat modelu.

## 15. Rotation, rekey, re-encryption a rewrap

- **Rotation** aktivuje novú key version pre nové operations.
- **Rekey** nahrádza key a môže meniť key hierarchy.
- **Re-encryption** decryptuje dáta starým keyom a encryptuje ich novým.
- **Rewrap** ponechá DEK a znovu ho wrap-ne novým KEK-om.

```text
full data re-encryption
→ drahšie, mení ciphertext

DEK rewrap
→ mení iba key envelope
```

Rotation bez schopnosti čítať historické versions spôsobí data loss. Neobmedzené zachovanie všetkých versions zväčšuje blast radius.

## 16. Revocation a key compromise

Key compromise vyžaduje viac než vytvorenie novej version:

```text
zastaviť nové použitie compromised keyu
→ identifikovať ciphertext, certificates a consumers
→ určiť exposure window
→ obmedziť decrypt/sign operations
→ rotate alebo revoke
→ re-encrypt/rewrap podľa threatu
→ obnoviť workloads a sessions
→ overiť starú cestu ako neplatnú
→ zachovať audit evidence
```

Rotation obmedzí budúci dopad, ale nevráti už uniknutý plaintext.

## 17. Backup, recovery a crypto-shredding

Encrypted backup je obnoviteľný iba spolu s dostupným key recovery modelom. Restore test musí zahŕňať historical key versions, KMS/HSM dependency, IAM, trust stores a break-glass access.

Crypto-shredding zneprístupní ciphertext zničením všetkých potrebných key copies. Funguje iba pri úplnom key inventory; backups, caches alebo escrow môžu zachovať alternate recovery path.

## 18. Full-disk, volume a file encryption

Full-disk encryption chráni médium po vypnutí alebo uzamknutí. Po odomknutí však OS a privileged processes vidia plaintext.

Jemnejšia granularita môže byť:

- block device,
- volume,
- filesystem,
- directory,
- file,
- record alebo field.

Vyššia granularita umožňuje presnejšiu isolation, ale komplikuje key lookup, indexing, backup consistency, rotation a application design.

## 19. Database encryption

Transparent Data Encryption typicky chráni database files, logs a backups pred storage-level compromise. Nechráni pred SQL principalom s `SELECT`, kompromitovaným database processom ani application accountom s broad accessom.

Column alebo field-level encryption zmenšuje plaintext boundary, ale prináša trade-offy:

- queries a indexes,
- key-per-tenant lifecycle,
- deterministic encryption leakage,
- migration a rotation,
- application-side authorization.

Application-level encryption môže skryť plaintext pred database administratorom, ale application runtime a jeho KMS permissions sa stanú kritickou boundary.

## 20. Deterministic encryption

Randomized encryption vytvára pre rovnaký plaintext rozdielny ciphertext a lepšie skrýva equality patterns.

Deterministic encryption umožňuje equality search, ale odhaľuje, ktoré hodnoty sú rovnaké. Pri malom domain-e môže attacker obsah odhadnúť frequency analysis alebo enumeration. Je to explicitný security trade-off, nie pohodlný default.

## 21. Object storage, snapshots a backups

Over celý data-copy graph:

```text
live object
→ replicas
→ version history
→ snapshots
→ backup copies
→ cross-region copies
→ exports
→ lifecycle archive
```

Customer-managed key zvyšuje control a audit, ale vytvára availability a lifecycle dependency. Disable alebo deletion keyu môže zneprístupniť veľké množstvo dát.

## 22. Logs, caches a temporary data

Primary database môže byť encrypted, zatiaľ čo plaintext unikne do:

- logs a debug traces,
- APM payloads,
- search indexes,
- Redis/cache,
- temporary files,
- swap a core dumps,
- analytics exports,
- dead-letter queues.

Data-flow inventory musí zahŕňať derived a transient copies.

## 23. Multi-tenant encryption

Možnosti:

- shared key pre environment,
- key per application,
- key per tenant,
- key per data class,
- DEK per object s tenant-specific KEK.

Key-per-tenant znižuje blast radius a umožňuje tenant-specific revocation, ale zvyšuje KMS quotas, cache complexity, recovery a migration náklady. Tenant identity musí byť viazaná na decrypt request cez policy, encryption context alebo AAD; nestačí post-decryption kontrola v aplikácii.

## 24. Client-side a server-side encryption

Server-side encryption vykoná storage alebo service provider po prijatí plaintextu. Integrácia je jednoduchšia, ale provider boundary plaintext vidí.

Client-side encryption zašifruje dáta pred odoslaním providerovi. Zmenšuje provider-side plaintext boundary, no prenáša na clienta key distribution, recovery, sharing, search a interoperability.

## 25. TLS mentálny model

```text
client pozná zamýšľanú service identity
→ nadviaže TLS handshake
→ server predloží certificate a proof private keyu
→ client validuje chain, identity, čas a policy
→ strany odvodia session keys
→ application data sa prenášajú cez authenticated encryption
```

TLS neposkytuje security, ak client nevaliduje správnu endpoint identity.

## 26. TLS handshake a certificate validation

Handshake vyjednáva protocol version, algorithms, key establishment, server authentication a voliteľne client authentication.

Client typicky validuje:

- certificate signature chain,
- trust anchor,
- validity period,
- key usage a extended key usage,
- policy a constraints,
- hostname alebo service identity v SAN,
- revocation model podľa ecosystemu.

Platná signature od trusted CA nestačí, ak certificate nie je vydaný pre správny endpoint.

## 27. Certificate lifecycle

```text
key generation
→ CSR alebo automated enrollment
→ issuance
→ deployment
→ renewal
→ rollover overlap
→ revocation alebo expiry
→ private-key destruction
```

Monitoruj days to expiry, failed renewals, stale deployment, trust-store propagation a unsupported algorithms. Úspešné vydanie neznamená, že service nový certificate načítala.

## 28. Private-key protection a mTLS

TLS private key má byť čitateľný iba potrebnou service identity, bezpečne distribuovaný, nelogovaný, rotovaný a oddelený medzi environments a services.

Pri mTLS sa autentizuje server aj client pomocou certificates. mTLS poskytuje channel-level mutual authentication, ale application authorization stále musí určiť resource, action, tenant a context. Certificate subject alebo SPIFFE-like identity musí byť bezpečne mapovaná na application principal-a.

## 29. TLS termination

TLS môže končiť na edge load balanceri, reverse proxy, ingress controlleri, API gateway, service-mesh proxy alebo aplikácii.

```text
internet client
→ TLS terminator
→ plaintext alebo nový TLS channel
→ backend
```

Termination vytvára novú trust boundary. Treba určiť:

- či backend hop používa TLS,
- kto môže čítať plaintext,
- ako sa propaguje client identity,
- či trusted headers možno spoofovať,
- kde sa logujú payloads,
- kto spravuje certificates.

HTTPS na edge neznamená end-to-end encryption až po database alebo downstream service.

## 30. Reverse proxy a trusted identity headers

Backend smie dôverovať proxy-generated identity headers iba vtedy, keď je dostupný výhradne cez autorizovaný proxy path. Controls:

- backend network isolation,
- mTLS proxy ↔ backend,
- strip a overwrite trusted headers,
- explicit trusted-proxy configuration,
- cryptographic token propagation.

Pri direct access by attacker mohol rovnaké headers injektovať sám.

## 31. TLS versions a forward secrecy

Pre moderné návrhy preferuj TLS 1.3. TLS 1.2 môže byť potrebné pre kompatibilitu, ale iba s bezpečným profile-om. Zakáž SSLv2/3, TLS 1.0/1.1, export/NULL ciphers, anonymous authentication a nebezpečné downgrade fallbacky.

Forward secrecy znamená, že neskorší compromise dlhodobého private keyu neumožní decryptovať predtým zachytené sessions. Nechráni plaintext logs, live endpoint compromise ani ukradnuté application tokens.

## 32. Session resumption a 0-RTT

Session resumption znižuje handshake latency, ale zavádza ticket alebo PSK lifecycle. TLS 1.3 0-RTT early data môže byť replay-nuté. Nepoužívaj ho pre non-idempotent alebo security-sensitive operations bez application-level replay protection.

Nevhodné príklady:

- vytvorenie platby,
- credential reset,
- zmena policy,
- jednorazová administratívna operácia.

## 33. Metadata leakage

TLS neukrýva všetky metadata. Viditeľné môžu zostať source/destination IP, timing, packet sizes, connection patterns, časť DNS a podľa protokolu/deploymentu niektoré handshake signals.

Encryption contentu nie je anonymity ani traffic-flow confidentiality.

## 34. Internal traffic nie je automaticky trusted

Private network alebo VPC neposkytuje rovnaké vlastnosti ako authenticated encryption. Hrozby zahŕňajú compromised workload, lateral movement, malicious insider, host packet capture a cross-account connectivity.

Service-to-service TLS alebo mTLS má zmysel tam, kde threat model vyžaduje channel a peer identity protection aj vo vnútri siete.

## 35. Kubernetes encryption at rest

Kubernetes API data sú uložené v etcd. Resource `Secret` používa base64 reprezentáciu, nie automatickú encryption.

Encryption at rest vyžaduje encryption provider konfiguráciu, napríklad KMS provider alebo schválený local provider. Prevádzka musí:

- určiť resources, ktoré sa encryptujú,
- chrániť KMS permissions a provider keys,
- rewrite-núť existujúce plaintext records,
- testovať backup/restore spolu s KMS dependency,
- monitorovať provider latency a decrypt failures,
- obmedziť direct etcd access.

Etcd encryption nechráni Secret pred Podom alebo používateľom s autorizovaným API accessom.

## 36. Service mesh encryption

Service mesh môže automatizovať workload certificates a mTLS. Treba však rozumieť workload identity issuance, rotation, sidecar/node proxy trust, strict vs permissive mode, bypass paths, ingress/egress boundaries a telemetry metadata.

„Mesh enabled“ neznamená, že každý flow je encrypted. Over reálnu policy a packet path.

## 37. CI/CD a artifact transport

TLS chráni source fetch, dependency download, registry push/pull, artifact storage a deployment APIs počas transportu. Neoveruje však, že artifact je zamýšľaný a nepoškodený v supply chain. Na to sú potrebné immutable digests, signatures, provenance a trusted build controls.

## 38. Availability a key caching

Encryption vytvára dependency na KMS/HSM, CA, trust store, DNS/time, network path a historical key versions.

Fail-closed chráni confidentiality, ale môže zastaviť systém. Fail-open môže odhaliť plaintext alebo obísť identity validation. Rozhodnutie musí byť explicitné podľa data class a operation.

Key cache znižuje latency a KMS dependency, ale zväčšuje exposure window. Definuj maximum TTL, per-tenant separation, memory protection, eviction pri revocation, crash-dump policy a behavior počas outage-u. Neobmedzený cache neguje rotation a revocation.

## 39. Cryptographic agility

Crypto agility je schopnosť meniť algorithm, key length, protocol version, certificate profile, provider, key hierarchy a trust anchors.

Ciphertext a protocol metadata majú byť versionované:

```text
read: v1 + v2
write: iba v2
→ postupná migrácia
→ odstránenie v1 po overení
```

Hard-coded algorithm bez versioningu vytvára dlhodobý migration risk.

## 40. Post-quantum transition

NIST publikoval FIPS 203 pre ML-KEM a FIPS 204/205 pre post-quantum digital signatures. Organizácia potrebuje:

- cryptographic inventory,
- data-lifetime analýzu pre harvest-now-decrypt-later risk,
- crypto-agile interfaces,
- vendor roadmap,
- interoperability a performance testing,
- controlled migration podľa schválených profiles.

Post-quantum algorithm nerieši slabý key lifecycle, endpoint compromise ani nesprávnu authorization.

## 41. Logging a audit

Neloguj plaintext citlivých dát, DEK/KEK values, private keys, decrypted secrets ani session keys.

Audituj metadata:

- key creation/import,
- encrypt/decrypt/sign operation podľa sensitivity,
- principal a workload identity,
- key version a tenant context,
- result a policy deny,
- key disable/delete,
- certificate issuance/revocation,
- TLS handshake failures,
- insecure fallback attempts.

## 42. Incident response

Pri key alebo TLS private-key compromise:

```text
identifikovať key, účel a versions
→ obmedziť operations
→ identifikovať ciphertext a services
→ určiť exposure window
→ rotate/revoke key alebo certificate
→ re-encrypt/rewrap podľa threatu
→ obnoviť workloads a sessions
→ overiť starý path ako neplatný
→ analyzovať plaintext exfiltration
→ opraviť root cause
```

Forward secrecy môže obmedziť historical TLS exposure, ale treba overiť reálny handshake a session-key model.

## 43. Troubleshooting at-rest encryption

```text
data a metadata version správna?
→ správny DEK/KEK identifier?
→ KMS endpoint DNS/TLS/network?
→ workload identity a decrypt permission?
→ encryption context/AAD identické?
→ key enabled a správna region/account boundary?
→ authentication tag a ciphertext nepoškodené?
→ historical key version dostupná?
→ cache stale?
→ backup obsahuje potrebné metadata?
```

## 44. Troubleshooting TLS

```text
DNS smeruje na správny endpoint?
→ TCP/QUIC connectivity?
→ podporované protocol versions?
→ certificate chain kompletný?
→ trust anchor dostupný?
→ hostname/service identity sedí?
→ certificate platný v čase?
→ key usage a signature algorithm podporované?
→ SNI/ALPN správne?
→ mTLS client certificate a mapping?
→ proxy alebo mesh termination boundary?
→ application authorization po handshake?
```

## 45. Typické chyby

### Invalid authentication tag

Možné príčiny sú poškodený ciphertext, nesprávny key alebo nonce, odlišné AAD a zlá serialization/version. Tag failure nikdy neignoruj.

### Certificate valid, ale hostname mismatch

Certificate nemá správny SAN alebo connection smeruje na inú identity. Neobchádzaj validáciu cez `verify=false`.

### Certificate expired po úspešnom renewal

Service nový certificate nenačítala, load balancer drží starý secret alebo rollout neprebehol na všetkých nodes.

### TLS funguje na edge, backend je plaintext

Over termination point, backend listener, mesh/proxy policy a packet path.

### KMS outage zastavil aplikáciu

Vyhodnoť cache TTL, startup behavior, retries, regional dependency a explicitný fail model. Nezavádzaj neobmedzený plaintext fallback.

## 46. Metrics a SLO

Sleduj:

- percento classified data encrypted at rest,
- percento flows s required TLS/mTLS,
- key a certificate inventory coverage,
- keys/certificates blízko expiry,
- failed rotation a renewal,
- KMS latency a error rate,
- policy denies,
- stale cryptographic versions,
- plaintext listener detections,
- TLS handshake failures podľa reason,
- restore-test success,
- mean time to revoke compromised key.

Metric bez asset inventory nevie určiť skutočné coverage.

## 47. Governance

Organizácia potrebuje approved algorithms a protocol profiles, cryptographic inventory, key ownership, classification-to-control mapping, maximum cryptoperiods, certificate policy, KMS/HSM access model, backup/recovery pravidlá, compromise playbooks, exception process a deprecation plan.

## 48. Anti-patterny

- `AES-256` ako celý security design,
- key vedľa ciphertextu s rovnakými permissions,
- encryption bez integrity,
- nonce reuse,
- TLS bez hostname validation,
- `verify=false` ako trvalý workaround,
- jeden wildcard private key pre celý environment,
- rotation bez application compatibility,
- encrypted primary storage a plaintext backups,
- KMS administrator a data administrator bez separation,
- post-quantum marketing bez crypto inventory.

## 49. Kontrolné otázky

1. Aký threat model rieši full-disk encryption a čo nerieši?
2. Aký je rozdiel medzi encryption, hashing, MAC a digital signature?
3. Prečo sa pre nové návrhy používa AEAD?
4. Prečo je nonce reuse pri AES-GCM kritické?
5. Na čo slúži AAD?
6. Ako funguje DEK, KEK a envelope encryption?
7. Aký je rozdiel medzi rotation, re-encryption a rewrap?
8. Prečo backup potrebuje aj key recovery test?
9. Čo chráni TDE a pred čím nechráni?
10. Čo musí client validovať pri TLS certificate?
11. Kde vzniká trust boundary pri TLS termination?
12. Aký je rozdiel medzi TLS a mTLS?
13. Prečo 0-RTT nie je vhodné pre každú operation?
14. Ako Kubernetes encryption at rest súvisí s etcd a KMS?
15. Ako navrhnúť crypto agility a post-quantum readiness?

## Glossary impact

Relevantné pojmy: plaintext, ciphertext, encryption at rest, encryption in transit, data in use, symmetric cryptography, asymmetric cryptography, hybrid cryptography, AEAD, nonce, initialization vector, authentication tag, Additional Authenticated Data, Data Encryption Key, Key Encryption Key, envelope encryption, KMS, HSM, key lifecycle, cryptoperiod, key rotation, rekey, re-encryption, rewrap, crypto-shredding, full-disk encryption, Transparent Data Encryption, deterministic encryption, client-side encryption, server-side encryption, TLS, certificate chain, trust anchor, mutual TLS, TLS termination, forward secrecy, session resumption, 0-RTT, cryptographic agility a post-quantum cryptography.

## Primárne zdroje

- [NIST FIPS 197 — Advanced Encryption Standard](https://csrc.nist.gov/pubs/fips/197/final)
- [NIST SP 800-38D — GCM and GMAC](https://csrc.nist.gov/pubs/sp/800/38/d/final)
- [NIST SP 800-57 Part 1 Rev. 5 — Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
- [NIST SP 800-111 — Storage Encryption Technologies](https://csrc.nist.gov/pubs/sp/800/111/final)
- [NIST SP 800-52 Rev. 2 — TLS Implementations](https://csrc.nist.gov/pubs/sp/800/52/r2/final)
- [RFC 8446 — TLS 1.3](https://datatracker.ietf.org/doc/html/rfc8446)
- [RFC 9325 — Recommendations for Secure Use of TLS and DTLS](https://datatracker.ietf.org/doc/html/rfc9325)
- [RFC 5280 — Internet X.509 PKI Certificate and CRL Profile](https://datatracker.ietf.org/doc/html/rfc5280)
- [Kubernetes — Encrypting Confidential Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
- [NIST FIPS 203 — ML-KEM](https://csrc.nist.gov/pubs/fips/203/final)
- [NIST FIPS 204 — ML-DSA](https://csrc.nist.gov/pubs/fips/204/final)
- [NIST FIPS 205 — SLH-DSA](https://csrc.nist.gov/pubs/fips/205/final)
