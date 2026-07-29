# Federation, secret and cryptographic trust lifecycle glossary entries

## Assertion acceptance verdict — SAML

Dôkaz, že signed XML element, trusted metadata entity, issuer, audience, destination, recipient, time, request binding, replay state, identity mapping a local authorization vytvárajú správny session outcome a odmietajú wrong-entity, replay, wrapping a untrusted-attribute paths. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Bootstrap identity boundary — secrets

Prvotná platformová alebo cryptographic identity, ktorou workload preukáže oprávnenie získať ďalší secret alebo vykonať cryptographic operation bez permanentného shared bootstrap credentialu. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Capability target — secret

Cieľový systém a operácie, ktorým secret alebo private key poskytuje authority, napríklad database session, token issuance, decryption alebo federation signing. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Claims-authority contract — federation

Versionovaný contract určujúci, ktorý issuer alebo IdP smie vydávať konkrétny claim/attribute, jeho typ, cardinality, allowed values, freshness a spôsob mapovania na local identity alebo entitlement. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md) a [SAML](docs/13-security-and-identity/saml.md).

## Consumer-loaded secret generation

Exact secret alebo key version reálne načítaná konkrétnym processom, agentom alebo workload replica, odlíšená od current source a delivered file/object generation. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Cross-environment key reuse

Použitie rovnakého private alebo symmetric key materialu v staging, production alebo ďalších environmentoch, ktoré mení compromise menej dôveryhodného environmentu na širší production trust incident. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Cross-purpose key reuse

Použitie jedného keyu pre nesúvisiace cryptographic purposes alebo protocols, napríklad OIDC a SAML signing, čím sa spájajú ich attack surface, authorization a revocation blast radius. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Cryptographic acceptance verdict

Dôkaz, že asset, format, algorithm, key purpose/version, nonce/AAD alebo signed subject, caller authorization, loaded verifier state, recovery a old-key rejection spĺňajú intended confidentiality, integrity alebo authentication outcome. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Cryptographic protection subject

Exact data alebo artifact class, protection property, state at rest/transit/use, algorithm/format generation, key ID/purpose/version, producers, consumers, cryptographic boundary, plaintext points a recovery state analyzovanej protection. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Entity-bound signing key — SAML

Signing public key dôveryhodný iba ako súčasť konkrétnej SAML metadata entity a generation, nie ako samostatná federation identity použiteľná naprieč issuers alebo environments. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Federation identity key

Stable external identity zložená z federation trust namespace-u a subject identifiera, napríklad OIDC `issuer + sub` alebo SAML `IdP entity ID + NameID format + NameID value`. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md) a [SAML](docs/13-security-and-identity/saml.md).

## ID Token acceptance verdict

Dôkaz, že trusted issuer/client transaction, signature, `iss`, `aud`, `azp`, time, nonce, assurance, `issuer + sub` mapping, claims authority, local session a resource authorization vytvárajú intended login a odmietajú wrong-issuer alebo token-substitution paths. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Indirect Secret access — Kubernetes

Schopnosť získať Kubernetes Secret bez priameho `get`, napríklad vytvorením Podu s oprávnenou ServiceAccount, mountom Secretu, `exec`, debug containerom alebo node/kubelet accessom. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Issuer trust generation — OIDC

Versionovaná väzba exact OIDC issuer-a na approved discovery metadata, endpoints, JWKS, algorithms, client registration a tenant/environment policy. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Metadata trust generation — SAML

Versionovaný SAML trust state spájajúci entity ID, endpoints, bindings, signing/encryption keys, NameID/attribute contract a validity/rollover metadata. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Non-exportable signing capability

Model, v ktorom workload môže po authorization požiadať KMS, HSM alebo signing service o podpis, ale raw private key material neopustí cryptographic boundary. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md) a [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## OIDC subject

Exact issuer/discovery generation, client registration, transaction state, token header/claims, identity mapping, claims revision, local session, requested resource a revocation descendants analyzovaného OIDC loginu. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Old-key forbidden path

Negative acceptance test dokazujúci, že retired alebo compromised key už nedokáže decryptovať, podpisovať accepted artifact, vytvoriť session ani byť znovu načítaný cez stale cache, backup alebo alternate verifier. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Plaintext boundary

Miesto, kde sa encrypted data alebo secret po authorized decryption stane čitateľným, napríklad process memory, TLS terminator, Pod volume, environment alebo debug output. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## Protection-state verdict

Rozhodnutie, či konkrétna data copy je at rest, in transit alebo in use a ktorý attacker/control model sa na túto boundary reálne vzťahuje. Pozri [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).

## SAML subject

Exact trusted metadata/entity/key generation, request and assertion IDs, signed XML element, semantic constraints, NameID/attributes, local session, replay a logout/revocation state analyzovaného SAML loginu. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Secret acceptance verdict

Dôkaz, že intended identity môže získať alebo použiť correct secret generation, consumers ju skutočne načítali, target dôveruje new generation a old direct, indirect, copied a derived credential paths sú neplatné. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secret lifecycle subject

Exact purpose, target, credential type, secret/key ID a generation, source, owner, policies, consumers, delivery, loaded state, target trust, descendants, backup a destruction state analyzovaného secretu. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secret revocation graph

Inventory vzťahov od source secretu cez distributed copies a loaded processes po target sessions, issued tokens/assertions/certificates, exchanged descendants, caches a backups, ktoré musia byť pri compromise zneplatnené alebo posúdené. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Signed-node binding — SAML

Požiadavka, aby application claims spracovala presne XML element, ktorého reference, digest a signature boli overené, a odmietla duplicate IDs, extra assertions alebo ambiguous document shape. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Target-trust generation — secret

Exact target-side credential alebo public-key state, ktorý rozhoduje, či secret/key generation zostáva použiteľná, odlíšený od value uloženej v secret store. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Verifier trust generation

Versionovaný set issuer/entity bindings, public keys, algorithms, audience/resource rules a cache state skutočne načítaný Relying Party, Service Provider alebo iným signature consumerom. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md), [SAML](docs/13-security-and-identity/saml.md) a [Encryption at rest a in transit](docs/13-security-and-identity/encryption-at-rest-and-in-transit.md).
