# OpenID Connect

OpenID Connect — OIDC — je authentication a identity vrstva nad OAuth 2.0. Jej úlohou nie je vydať všeobecnú application permission, ale umožniť Relying Party dôveryhodne rozhodnúť, ktorý OpenID Provider autentizoval ktorý subject pre konkrétneho clienta, v akej transaction a s akým authentication contextom.

ID Token je assertion určená pre Relying Party. Access token je credential pre Resource Server. UserInfo je voliteľný claims endpoint a local application session vzniká až v aplikácii. Ak sa tieto artifacts zamieňajú, validná JWT signature môže stále viesť k token substitution, wrong-issuer account linking, stale entitlements alebo neúplnému logoutu.

## Issuer-to-session lifecycle

OIDC trust začína explicitným issuer contractom. Discovery a JWKS sa používajú až po tom, čo application vie, ktorému issuerovi smie dôverovať; user-supplied issuer URL nesmie dynamicky vytvoriť trust root. Authentication transaction následne viaže state, nonce, PKCE, redirect a client session. Po code exchange Relying Party validuje ID Token a mapuje `issuer + subject` na lokálnu identity.

```text
login alebo step-up intent
→ exact issuer, client a redirect registration
→ state, nonce a PKCE transaction
→ OP authentication a authorization code
→ token endpoint a client binding
→ ID Token cryptographic a semantic validation
→ issuer + subject identity mapping
→ claims-authority a assurance mapping
→ local session a resource authorization
→ logout, revocation a second-session validation
```

Úspešné OIDC login UI nepreukazuje správne account mapping ani resource authorization. Local session môže prežiť OP logout a access token môže prežiť local cookie deletion.

## Exact OIDC subject SEC-PAY-49

OIDC trust sa musí viazať na exact issuer, client, redirect, subject identity a signing-key purpose. Subject explicitne oddeľuje staging a production, aby shared key alebo email collision nemohli nahradiť issuer-bound identity.

```yaml
incident: SEC-PAY-49
productionIssuer: https://id.atlas.example/realms/production
stagingIssuer: https://id.staging.atlas.example/realms/staging
clientId: settlement-admin-console
redirectUri: https://admin.atlas.example/oidc/callback
identityKeyExpected: issuer-plus-subject
subject: 248c16a9-3ea0-4f2a-8a17-f9a88421c0aa
emailClaim: marcel.novak@atlas.example
acrRequired: urn:atlas:assurance:phishing-resistant
sharedSigningKey: FED-SIGN-07
localSession: OIDC-SESSION-991
forbiddenMapping: groups-direct-to-admin
```

Subject ukazuje dva oddelené trust problems: rovnaký signing key bol použitý cez staging/production aj OIDC/SAML a Relying Party neviazal validnú signature na exact production issuer.

## Discovery a trusted issuer bootstrap

Discovery document publikuje endpoints, supported capabilities a `jwks_uri`. Client ho smie načítať iba pre staticky alebo administratívne schválený issuer a musí overiť, že returned `issuer` presne zodpovedá configured value.

```bash
curl -fsS \
  https://id.atlas.example/realms/production/.well-known/openid-configuration \
  | jq '{issuer, authorization_endpoint, token_endpoint, jwks_uri, id_token_signing_alg_values_supported}'
```

Výstup preukazuje discovery metadata dostupné z konkrétneho endpointu. Nepreukazuje, že application používa túto metadata generation, že TLS trust je správne pinned podľa policy alebo že runtime nepovolí staging issuer s rovnakým key ID.

JWKS read-back:

```bash
JWKS_URI="$(curl -fsS https://id.atlas.example/realms/production/.well-known/openid-configuration | jq -r .jwks_uri)"
curl -fsS "$JWKS_URI" | jq '[.keys[] | {kid, kty, use, alg}]'
```

JWKS preukazuje public verification keys publikované issuerom. Nepreukazuje private-key protection, signer runtime generation, certificate lifecycle ani authorization konkrétneho key-u pre production OIDC purpose.

## State, nonce, PKCE a redirect binding

`state` viaže callback na local login transaction a chráni proti CSRF a response mix-upu. `nonce` viaže ID Token na transaction a bráni replayu tokenu z iného loginu. PKCE viaže authorization code na client instance. Exact redirect URI zabraňuje odoslaniu code-u na attacker-controlled endpoint.

Tieto hodnoty riešia odlišné threats a nesmú sa zlúčiť do jedného reused random stringu bez lifecycle-u. Transaction state sa po použití atomicky spotrebuje; callback s unknown, expired alebo reused state musí zlyhať closed.

## ID Token validation

Relying Party validuje signature iba kľúčom z trusted issuer JWKS a povoľuje explicitný algorithm set. Potom kontroluje `iss`, `aud`, prípadne `azp`, `exp`, `iat`, `nonce` a podľa use case-u `auth_time`, `acr` a `amr`. `kid` iba vyberá candidate key; nie je trust decision.

Claims inspection pre debugging:

```bash
ID_TOKEN_PAYLOAD="$(printf '%s' "$ID_TOKEN" | cut -d. -f2 | tr '_-' '/+' | base64 -d 2>/dev/null)"
printf '%s' "$ID_TOKEN_PAYLOAD" | jq '{iss, sub, aud, azp, exp, iat, nonce, auth_time, acr, amr, email, groups}'
```

Tento príkaz iba dekóduje payload. **Neoveruje** signature, issuer trust, nonce, expiry ani audience. Je vhodný na evidence capture claims po tom, čo verifier verdict existuje; nesmie sa používať ako authentication implementation.

## Identity mapping: issuer + subject

OIDC subject je lokálne unikátny v rámci issueru. Stabilný external identity key je preto dvojica `iss + sub`. Email, preferred username a display name sú mutable a môžu byť recyklované alebo kolidovať medzi issuer-mi. Account linking podľa emailu umožní staging alebo kompromitovanému external issueru prevziať production účet s rovnakou adresou.

Pairwise subject identifiers znižujú koreláciu používateľa medzi clients, ale menia account-linking a migration contract. Public subject je stabilný naprieč clients jedného issueru. Relying Party musí vedieť, ktorý subject type používa, a migration nesmie potichu vytvoriť duplicate alebo merged accounts.

## Claims authority a local authorization

ID Token môže niesť groups alebo roles, no application musí vedieť, či issuer je authority pre konkrétny entitlement a client. Direct mapping `groups contains settlement-admin → local admin` spája directory lag, mapper bug alebo staging issuer s privileged application authorization.

Bezpečnejší chain používa allowlisted claim source, client-specific projection, current JIT/resource check a local policy revision. OIDC preukazuje authentication context; application authorization stále hodnotí tenant, object, workflow a current risk.

`acr`, `amr` a `auth_time` podporujú step-up. `amr` opisuje použité metódy, `acr` dosiahnutú assurance class a `auth_time` čas primary authentication. High-risk action môže vyžadovať recent phishing-resistant step-up, nie iba existenciu dlhej SSO session.

## UserInfo a access token boundary

UserInfo sa volá access tokenom a vracia claims podľa scopes. Response sa musí viazať na rovnaký `sub` ako ID Token; inak hrozí token substitution. UserInfo nie je autoritatívny entitlement read-back, pokiaľ issuer contract nehovorí presne, ktoré claims a freshness poskytuje.

Access token sa neposiela Relying Party ako náhrada ID Tokenu, pokiaľ client zároveň nie je intended Resource Server. ID Token sa neposiela API ako bearer access token. Každý artifact má vlastný audience a consumer.

## Session a logout semantics

Local application cookie je samostatná session generation. OP session, ID Token, access token, refresh token a downstream service sessions môžu mať odlišnú lifetime. Local logout odstráni application session, ale nemusí ukončiť OP SSO. Front-channel logout závisí od browser delivery, back-channel logout používa server-to-server notification a RP-initiated logout začína u clienta.

Logout acceptance potrebuje descendant inventory. Ak Relying Party zruší cookie, ale API access token ostane platný 60 minút, privileged capability prežije. High-risk revocation môže vyžadovať online session check alebo krátke token lifetimes.

## Workload identity federation

OIDC assertion môže autentizovať workload do cloud alebo CI platformy. Issuer, subject pattern, audience, repository/workflow/environment claims a token lifetime musia byť presne obmedzené. Trust „všetky tokens z GitHub issueru“ je príliš široký; policy má viazať repository, branch/ref, workflow identity a protected environment.

Workload federation odstraňuje long-lived cloud secret, ale presúva dôveru na issuer, claims a build/runtime policy. Compromised workflow s platným assertionom stále môže získať cloud token, ak trust policy je broad.

## Incident SEC-PAY-49

Static RSA key `FED-SIGN-07` sa používal pre staging aj production a zároveň pre OIDC JWT aj SAML XML signatures. Staging debug principal získal private key nepriamo cez `create Pod`, výber `idp-runtime` ServiceAccountu, Secret mount a `exec`. Etcd KMS encryption a TLS fungovali, no chránili storage a transport, nie authorized runtime plaintext projection.

Attacker vytvoril staging-issued ID Token s emailom production admina. Production Relying Party overila signature rovnakým trusted keyom, ale nevalidovala exact issuer. Account linkovala podľa emailu a group claim mapovala priamo na admin role. Signature bola cryptographically validná; trust a identity semantics boli nesprávne.

Competing hypotheses zahŕňali stolen production session, compromised production signer, JWKS cache poisoning, wrong-issuer acceptance, account-linking collision a local role mapper. Token `iss`, signer key lineage, staging audit a account-linking record ukázali shared-key/wrong-issuer path.

## Containment a authoritative recovery

Containment zablokuje affected issuer/key combination, revoke-ne local sessions a downstream tokens a zachová token headers/payloads, verifier decisions, JWKS generations, account-link records a Kubernetes audit. Global disable všetkých federation clients bez recovery path môže zničiť availability a evidence.

Recovery vytvorí oddelené non-exportable keys pre staging/production a OIDC/SAML purposes, pinne exact issuer, mapuje identity cez `issuer + subject`, zavádza claims-authority allowlist a current resource authorization. Coordinated rollover publikuje nový verification key, prejde canary, odstráni old trust až po expiry/revocation window a overí loaded verifier generation.

Acceptance vyžaduje successful production login s exact issuer, deny pre staging token podpísaný inak platným keyom, deny pre email collision, deny pre unapproved group claim a successful recent step-up pre legitímneho admina. Existing a fresh sessions vytvorené cez old path musia zlyhať. Druhý key rollover musí prejsť bez shared-purpose alebo cross-environment trustu.

## Kontrolné otázky

1. Prečo discovery nezačína dôverou k user-supplied issuer URL?
2. Čo odlišuje ID Token, access token, UserInfo a local session?
3. Prečo `issuer + subject` tvorí bezpečnejší identity key než email?
4. Čo payload decode nepreukazuje?
5. Ako `nonce`, `state` a PKCE riešia odlišné threats?
6. Prečo validná signature zo shared key-u nepreukázala production issuer?
7. Ktoré descendant sessions musí logout/revocation uzavrieť?

## Referencie

- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)
- [OpenID Connect Discovery](https://openid.net/specs/openid-connect-discovery-1_0.html)
- [OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700)
- [JSON Web Token Best Current Practices](https://www.rfc-editor.org/rfc/rfc8725)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OAuth 2.0](oauth-2.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: SAML →](saml.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
