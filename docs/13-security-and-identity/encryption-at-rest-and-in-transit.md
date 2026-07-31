# Encryption at rest a in transit

Encryption je cryptographic mechanism na ochranu confidentiality. Moderné použitie zároveň chráni integrity ciphertextu cez authenticated encryption. Security výsledok však nevzniká z checkboxu `encrypted`. Vzniká z threat modelu, exact data a key subjectu, algorithm a mode correctness, key authorization, plaintext boundaries, consumer behavior, rotation, revocation a recovery.

At-rest encryption môže chrániť ukradnutý disk alebo leaked backup. TLS môže chrániť packet path. Ani jedno automaticky nechráni plaintext pred workloadom, ktorý ho smie načítať, pred debug Podom s indirect Secret accessom alebo pred application processom oprávneným volať KMS `Decrypt`. Cryptography chráni konkrétnu boundary pred konkrétnym attackerom; nie celý systém pred každým principalom.

## Asset-to-key-boundary lifecycle

```text
asset, business use a threat model
→ exact data state: rest, transit alebo use
→ confidentiality, integrity a authenticity requirements
→ algorithm, protocol a format generation
→ key purpose, owner, scope a trust boundary
→ authorized encrypt/decrypt/sign/verify operation
→ ciphertext alebo secure channel publication
→ consumer validation a plaintext boundary
→ rotation, rekey, rewrap a revocation
→ restore, old-path rejection a crypto-agility closure
```

„KMS key enabled“ nepreukazuje, že application používa intended key. „TLS handshake successful“ nepreukazuje hostname, client identity ani application authorization. „Encrypted backup“ nepreukazuje dostupnosť decrypt key-u počas restore.

## Exact cryptographic subject SEC-PAY-49

```yaml
incident: SEC-PAY-49
asset: federation-signing-authority
keyId: FED-SIGN-07
algorithm: RSA
keyState: exportable-private-key
purposes:
  - oidc-production-signing
  - oidc-staging-signing
  - saml-production-signing
  - saml-staging-signing
storageProtection: Kubernetes etcd KMS v2
transportProtection: TLS
plaintextBoundary: idp-runtime Pod filesystem and memory
compromisePath: create-pod -> service-account -> secret-projection -> exec
requiredReplacement:
  - non-exportable production OIDC key
  - non-exportable staging OIDC key
  - non-exportable production SAML key
  - non-exportable staging SAML key
```

Subject ukazuje, že storage a transport protection boli správne, ale key purpose separation a runtime plaintext boundary zlyhali.

## Encryption, encoding, hashing, MAC a signature

Encoding mení reprezentáciu, napríklad base64; neposkytuje secrecy. Hash vytvára fixed-size digest a používa sa na integrity comparison alebo password derivation s vhodným password-hashing algorithmom. MAC preukazuje integrity a authenticity medzi stranami so shared secretom. Digital signature používa private/public key pair a umožňuje verifierom potvrdiť signer control bez shared signing secretu.

Encryption chráni plaintext pred neautorizovaným čítaním. Symmetric encryption používa rovnaký secret pre encrypt/decrypt a je efektívna pre dáta. Asymmetric cryptography používa key pair a typicky chráni key exchange, signatures alebo malé hodnoty. Hybridný model používa asymmetric alebo KMS boundary na ochranu symmetric Data Encryption Key.

## AEAD, nonce a AAD

Authenticated Encryption with Associated Data spája confidentiality a ciphertext integrity. Nonce alebo IV musí spĺňať algorithm-specific uniqueness/randomness contract. Opakovanie nonce-u s rovnakým keyom môže zničiť security aj pri silnom algorithm-e. Additional Authenticated Data nie je encrypted, ale je integrity-protected a môže viazať ciphertext na tenant, object type, schema alebo key context.

Praktický Python example s AES-GCM:

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

key = AESGCM.generate_key(bit_length=256)
nonce = os.urandom(12)
aad = b"tenant=orion;type=settlement;schema=v3"
plaintext = b"provider-token-reference"

ciphertext = AESGCM(key).encrypt(nonce, plaintext, aad)
recovered = AESGCM(key).decrypt(nonce, ciphertext, aad)
assert recovered == plaintext
```

Example preukazuje AEAD round trip pre jednu in-memory key/nonce/AAD kombináciu. Nepreukazuje durable nonce management, key storage, authorization, side-channel resistance, backup/restore ani safe exception handling. Production code používa approved library a versionovaný ciphertext format s key reference a algorithm metadata.

## Envelope encryption: DEK a KEK

Envelope encryption generuje per-object alebo bounded Data Encryption Key, ktorým zašifruje payload. Key Encryption Key v KMS/HSM chráni DEK. Stored object obsahuje ciphertext, wrapped DEK, key reference, nonce, AAD context a format version. Application potrebuje `Decrypt` capability len pre intended key/context.

Tento model znižuje množstvo dát priamo spracovaných KMS a podporuje rewrap: wrapped DEK sa prešifruje novým KEK bez decrypt/re-encrypt celého payloadu. Rekey alebo full re-encryption mení data-encryption key a ciphertext. Rotation aliasu bez rewrap/re-encryption necháva historical ciphertext viazaný na old key generation.

KMS policy má oddeľovať key administration od cryptographic use. Principal, ktorý smie meniť key policy aj decryptovať production data, obchádza separation of duties. Encryption context/AAD môže viazať KMS operation na tenant a object, ale iba ak caller a policy ho konzistentne vyžadujú.

## At-rest boundaries

Full-disk alebo volume encryption chráni offline media a snapshot theft, nie process s filesystem accessom. File/object encryption môže oddeliť datasets, no metadata, filenames alebo indexes môžu zostať viditeľné. Database transparent encryption chráni files a backups, nie broad SQL principal ani application injection. Application-layer encryption znižuje trust v storage layer, ale komplikuje query, key availability a rotation.

Kubernetes encryption configuration môže chrániť Secret resources v etcd:

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - kms:
          apiVersion: v2
          name: atlas-kms
          endpoint: unix:///var/run/kmsplugin/socket.sock
          timeout: 3s
      - identity: {}
```

Configuration preukazuje desired provider order. `identity` fallback umožňuje čítať legacy plaintext a pri nesprávnom write path-e aj ukladať unencrypted values. Manifest nepreukazuje loaded API-server config, KMS health, actual ciphertext migration alebo runtime Pod projection.

Read-back kontrola storage bez zobrazenia secret value používa raw etcd backup inspection v izolovanom prostredí alebo API-server/KMS metrics a controlled canary. `kubectl get secret -o yaml` ukáže API representation po decryption a nie je dôkaz ciphertextu v etcd.

## Data in transit a TLS

TLS chráni confidentiality a integrity transportu a autentizuje server certificate chain/hostname. Handshake zahŕňa version/cipher negotiation, certificate validation, ephemeral key agreement a Finished messages. Forward secrecy znamená, že neskorší compromise long-term server key-u nemá odhaliť recorded historical sessions.

```bash
openssl s_client \
  -connect api.payments.atlas.example:443 \
  -servername api.payments.atlas.example \
  -verify_return_error \
  -showcerts </dev/null
```

Výstup preukazuje handshake, certificate chain a negotiated parameters z konkrétneho client observation pointu. Nepreukazuje application authorization, backend hop encryption, private-key custody, revocation behavior ani to, že všetky clients používajú rovnaký trust store.

TLS termination mení plaintext boundary. Ak load balancer terminates TLS a backend používa plaintext, packet path za load balancerom nie je chránený. Re-encryption alebo mTLS na upstream hop-e vytvorí novú session a identity contract; viewer TLS success nepreukazuje backend TLS.

## mTLS a workload identity

Mutual TLS autentizuje obe strany certificate-mi. Certificate identity sa mapuje na workload principal a local authorization. Trust „ľubovoľný certificate z corporate CA“ je príliš široký; verifier má kontrolovať SAN identity, trust domain, EKU, lifetime, revocation/rotation a resource policy.

Short-lived workload certificates znižujú revocation window, no issuance authority a renewal path sú availability dependencies. Cached TLS connections môžu prežiť certificate rotation. Loaded certificate generation sa preto overuje na každej replica a cez nový handshake, nie iba file timestamp.

## Key lifecycle a cryptoperiod

Key generation používa approved entropy a boundary. Key purpose a environment sa oddelia. Distribution ide cez wrapped alebo mediated operation, nie plaintext copy. Rotation pripraví new key, publikuje verifier trust podľa potreby, prejde consumers, revoke-ne old operation a retire-ne historical material podľa retention/recovery contractu.

Disable, revoke a destroy majú odlišný dopad. Disable môže byť reversible containment. Destruction je nevratná a bez decryptability inventory môže zničiť backups alebo legal retention. Crypto-shredding je bezpečné iba vtedy, keď neexistujú alternate key copies a recovery requirements dovoľujú stratu plaintextu.

## Backup, restore a key availability

Encrypted backup je recoverable iba spolu s key, policy, identity a dependency generation. Key v rovnakom blast radius-e ako backup neposkytuje ransomware isolation; key iba v primary KMS bez DR pathu môže zničiť availability počas regional recovery.

Restore rehearsal musí potvrdiť decrypt v isolated account/environment-e, schema/application integrity a business reconciliation. Technický decrypt jedného sample objectu nie je complete recovery proof.

## Crypto agility a post-quantum príprava

Crypto inventory mapuje algorithms, protocols, libraries, key sizes, certificate chains, formats, embedded devices, external partners a data longevity. Agility znamená schopnosť versionovať format a prejsť na nový algorithm/key type bez big-bang rewrite-u. Post-quantum migration sa riadi threat/data-longevity modelom a interoperabilitou; názov „quantum safe“ bez standardu a implementation assurance nie je security verdict.

## Incident SEC-PAY-49

`FED-SIGN-07` bol exportable RSA private key uložený ako Kubernetes Secret. Etcd používalo KMS v2 a API/Pod transport TLS. Staging debug principal však mohol vytvoriť Pod, použiť `idp-runtime` ServiceAccount, mountnúť Secret a cez `exec` prečítať runtime plaintext. Storage a transport controls fungovali na svojich boundaries.

Key sa navyše používal pre štyri purposes. Attacker preto vytvoril validné staging/production OIDC a SAML signatures. Root cause bol shared exportable key a key-centric verifier trust. Kubernetes indirect access bol acquisition path; wrong issuer/entity validation a direct claims mapping zväčšili impact.

## Containment, recovery a acceptance

Containment zablokuje accepted trust pre compromised key, izoluje workloads, revoke-ne sessions/tokens/assertions a zachová Secret generations, KMS audit, Pod audit a verifier evidence. Destroy old key pred zachovaním evidence a descendant inventory by sťažil investigation bez zaručenia revocation.

Recovery vytvorí purpose- a environment-specific non-exportable keys v KMS/HSM alebo mediated signing service. Signers dostanú iba `Sign` na exact key; nemajú `GetPrivateKey`. Verifiers pinujú exact issuer/entity/purpose. Coordinated rollover publikuje new public keys/metadata, overí loaded generation, prejde canary a odmietne old signatures po bounded window.

Acceptance vyžaduje successful legitimate OIDC/SAML operation s new keys, deny pre old key, staging key na production path-e, wrong purpose a indirect Pod access. Backup restore musí preukázať required historical verification/decryption bez reaktivácie compromised signer. Druhá rotation overí, že key separation a loaded-state evidence sú opakovateľné.

## Kontrolné otázky

1. Pred ktorým attackerom chráni disk encryption a pred ktorým nie?
2. Prečo AEAD nonce reuse môže zničiť security?
3. Aký rozdiel je medzi rotation, rewrap, rekey a re-encryption?
4. Čo `openssl s_client` nepreukazuje?
5. Prečo KMS `Decrypt` permission môže byť plaintext capability?
6. Ako TLS termination mení trust boundary?
7. Prečo shared key medzi environmentmi a protocols zvyšuje blast radius?

## Referencie

- [NIST Cryptographic Standards and Guidelines](https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines)
- [NIST SP 800-57 Key Management](https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final)
- [TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446)
- [Kubernetes Encrypting Confidential Data at Rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
- [NIST Post-Quantum Cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Secrets management](secrets-management.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Vulnerability a patch management →](vulnerability-and-patch-management.md)
<!-- KNOWLEDGE-NAVIGATION:END -->