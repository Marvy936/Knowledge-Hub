# OpenID Connect

OpenID Connect — OIDC — je authentication a identity vrstva nad OAuth 2.0. Jej úlohou nie je vydať všeobecnú application permission, ale umožniť Relying Party dôveryhodne rozhodnúť, ktorý OpenID Provider autentizoval ktorý subject pre konkrétneho clienta, v akej transaction a s akým authentication contextom.

ID Token je assertion pre Relying Party. Access token je credential pre Resource Server. Local application session a resource authorization vznikajú až v aplikácii. Zámena týchto artifacts vytvára token-substitution, account-linking a stale-session failures aj vtedy, keď je JWT signature platná.

## 1. Dominantný issuer-to-session lifecycle

```text
login alebo step-up intent
→ exact issuer, client a redirect contract
→ transaction state, nonce a PKCE
→ OP authentication a authorization response
→ code exchange na trusted token endpoint-e
→ ID Token cryptographic a semantic validation
→ issuer + subject identity mapping
→ authoritative claims mapping
→ local session generation
→ resource-level authorization
→ logout, revocation a second-session validation
```

Každá boundary odpovedá na inú otázku. Signature dokazuje control nad signing keyom. `iss` určuje trust namespace. `aud` a `azp` určujú intended clienta. `nonce` viaže token na login transaction. `issuer + sub` určuje external identity. Claims mapping rozhoduje, ktoré assertions sa smú stať local attributes. Local policy až následne rozhoduje o konkrétnej operation.

## 2. Exact OIDC subject

Pri security alebo login incidente nestačí veta „OIDC token bol validný“. Zachovaj subject:

```text
OP issuer a discovery generation
+ client ID, type a redirect URI
+ authorization transaction ID
+ state, nonce a PKCE generation bez secret values
+ token endpoint a client-auth method
+ ID Token kid/alg/iss/sub/aud/azp/time claims
+ claims-mapping revision
+ local account a session ID
+ requested action/resource/tenant
+ logout a revocation descendants
```

V connected incidente je subject `OIDC-PAY-49`:

```text
production RP: https://payments-admin.atlas.example
expected issuer: https://id.atlas.example/prod
accepted issuer: https://id.atlas.example/staging
client_id: atlas-payments-admin
signing key: kid=FED-SIGN-07
external subject: partner-487
email claim: marta.novak@atlas.example
group claim: settlement-admin
local session: OIDC-SESS-90218
```

## 3. OAuth a OIDC nie sú rovnaká decision boundary

OAuth rieši delegated access clienta k Resource Serveru. OIDC pridáva authentication assertion pre clienta:

```text
OAuth access token
→ consumer je API
→ audience je resource
→ scope a local policy povoľujú API operation

OIDC ID Token
→ consumer je RP/client
→ audience je client ID
→ claims opisujú subject a authentication event
```

ID Token sa neposiela ako API credential. Access token sa nepoužíva ako generic login proof. Oba môžu byť JWT, ale rovnaká serialization neznamená rovnakú semantics.

## 4. Transaction: state, nonce a PKCE

Authorization Code flow má tri samostatné bindings:

```text
state
→ callback patrí k browser/RP transaction

nonce
→ ID Token patrí k authentication requestu

PKCE
→ authorization code môže vymeniť iba client instance s verifierom
```

RP uloží expected issuer, redirect URI, state, nonce, PKCE verifier, requested assurance a return destination do jednej pending transaction. Values sú random, bounded a single-use. Po úspechu sa transaction atomicky spotrebuje.

Tieto controls neopravia nesprávny trust bootstrap. Transaction môže byť protocol-correct a stále skončiť tokenom od neautorizovaného issuer-a.

## 5. Trusted issuer a discovery

Issuer je primary OIDC trust namespace. RP ho získa pri controlled onboarding-u alebo z tenant mappingu, nie z arbitrary user URL.

```text
approved issuer
→ issuer-derived discovery URL
→ metadata issuer exact match
→ trusted authorization/token/UserInfo/JWKS endpoints
→ bounded metadata cache a last-known-good policy
```

Token `iss` sa porovná exactne vrátane scheme, hosta, portu a path-u. Zdieľaný signing key medzi dvoma issuers nerobí tieto issuers ekvivalentnými.

Discovery automatizuje configuration; nevytvára trust. User-controlled `?issuer=https://attacker.example` nesmie pridať nového OP do allowlistu.

## 6. ID Token validation

RP validuje ID Token v context-e pending transaction:

1. parser prijme iba bounded JWT shape;
2. JOSE algorithm a key type sú na allowliste;
3. key pochádza iba z trusted issuer JWKS;
4. signature je validná;
5. `iss` exactne sedí s expected issuerom;
6. `aud` obsahuje client ID a `azp` je správne pri multiple audiences;
7. `exp`, `iat` a optional `nbf` sú v bounded time policy;
8. `nonce` sedí s transaction;
9. `auth_time`, `acr` a `amr` spĺňajú requested assurance, ak sú required;
10. optional token hashes sa validujú podľa flowu;
11. transaction sa spotrebuje;
12. až potom sa claims mapujú na local account.

```text
valid signature
≠ trusted issuer
≠ intended client
≠ correct subject mapping
≠ current business authorization
```

Unknown `kid` môže vyvolať jeden bounded JWKS refresh. Token header nesmie určiť arbitrary verification URL alebo algorithm.

## 7. Identity key je issuer + subject

OIDC `sub` je identifier v namespace konkrétneho issuer-a. External identity key je:

```text
issuer + sub
```

Email, username a display name sú mutable attributes. Rovnaký email od dvoch issuers neznamená rovnakú identity. Automatic linking podľa emailu umožní account takeover pri reassignment, malicious federation alebo environment collision.

Linking potrebuje authenticated proof oboch identities, authoritative enterprise identifier alebo explicitný administratívny workflow s auditom a unlink/recovery modelom.

## 8. Claims nie sú universal authority

Claim name štandardizuje syntax, nie business význam. `email_verified=true` nepreukazuje employment. `groups=[settlement-admin]` nepreukazuje, že issuer smie udeľovať production settlement privilege.

Claims mapping je versionovaný contract:

```text
issuer + claim name
→ expected type, cardinality a size
→ normalization
→ authoritative-source a allowed-value check
→ local attribute alebo entitlement input
→ local policy revision
```

Privileged entitlement musí byť allowlisted pre konkrétneho issuer-a, tenant-a a environment. Missing alebo malformed claim nesmie prepnúť usera do broad default role.

## 9. Authentication assurance

`auth_time`, `acr` a `amr` riešia odlišné facts:

- `auth_time` — kedy prebehla active authentication;
- `acr` — výsledná assurance alebo policy class podľa federation contractu;
- `amr` — použité methods podľa provider semantics.

Fresh login nemusí byť phishing-resistant. `prompt=login` nepreukazuje konkrétnu metódu. Sensitive settlement approval môže vyžadovať bounded `max_age`, exact approved `acr` a local JIT authorization.

## 10. Local session a authorization

Validated ID Token je input na vytvorenie local session, nie session samotná. RP regeneruje session ID, nastaví Secure/HttpOnly/SameSite cookie, idle a absolute timeout, CSRF control, session assurance a server-side revocation.

```text
validated OIDC identity
→ local account
→ local session generation
→ current tenant, JIT a workflow state
→ action/resource authorization
```

OP session, RP session, refresh token a API access tokens majú rozdielne lifecycles. „Logout succeeded“ na OP UI nie je dôkaz, že všetky local a downstream credentials sú neplatné.

## 11. Worked failure — staging issuer accepted v production

Atlas používal spoločný RSA private key `FED-SIGN-07` pre:

- staging aj production identity provider;
- OIDC ID Token signatures;
- SAML XML signatures.

Staging workload získaval key zo static Kubernetes Secretu. Broad debug permission umožnila vytvoriť Pod s rovnakou ServiceAccount a prečítať plaintext key. Attacker následne ovládol staging OP signing capability.

Production RP malo tieto defects:

```text
rovnaký client_id v staging a production
+ arbitrary tenant issuer routing
+ shared JWKS key/kid
+ signature a audience validation
- exact expected issuer validation
+ account linking podľa emailu
+ direct group-to-admin mapping
```

Attacker vytvoril legitimate OIDC transaction voči staging OP. `state`, nonce aj PKCE sedeli. Staging OP vydal token:

```json
{
  "iss": "https://id.atlas.example/staging",
  "sub": "partner-487",
  "aud": "atlas-payments-admin",
  "email": "marta.novak@atlas.example",
  "groups": ["settlement-admin"],
  "acr": "urn:atlas:phishing-resistant"
}
```

RP overilo signature keyom `FED-SIGN-07`, audience, expiry a nonce. Neoverilo exact issuer. Emailom našlo existujúci production účet a group claim preložilo na local admin role. Vytvorilo osemhodinovú session `OIDC-SESS-90218`, cez ktorú attacker zmenil settlement routing.

## 12. Competing hypotheses a discriminating evidence

Možné hypotézy boli:

1. authorization code interception;
2. nonce alebo login-CSRF failure;
3. compromised production OP;
4. account-linking collision;
5. key/JWKS poisoning;
6. staging issuer prijatý ako production trust.

Discriminating evidence:

- state, nonce a PKCE transaction boli korektné;
- token endpoint bol staging endpoint uložený v pending transaction;
- `iss` bol staging, nie production;
- `kid=FED-SIGN-07` existoval v oboch JWKS generations;
- local account vznikol cez email lookup, nie `issuer + sub`;
- role vznikla priamym mappingom `groups=settlement-admin`;
- production OP audit pre tento subject neobsahoval authentication event.

Root cause je chýbajúce issuer-bound trust a identity mapping. Shared key, reused client ID, email linking a direct role claim sú causal amplifiers. Key theft je upstream enabling compromise.

## 13. Evidence-preserving containment

- zablokovať staging issuer a `kid=FED-SIGN-07` pre production RP;
- zastaviť nové privileged session creation z affected federation paths;
- preserve-nuť discovery/JWKS generations, token header/claims hash, transaction ID, mapping revision a session audit bez raw tokens;
- revoke-nuť sessions a refresh descendants vytvorené z affected issuer/key interval-u;
- neprepínať RP na signature-disable alebo broad fallback login;
- nevymazať identity link pred zachovaním actor-to-session evidence.

## 14. Authoritative recovery

1. vytvoriť samostatný OIDC signing key pre production OP;
2. odstrániť cross-environment a cross-protocol key reuse;
3. publikovať bounded JWKS overlap a následne odstrániť `FED-SIGN-07`;
4. pinúť client registration na exact production issuer a unique production client ID;
5. identitu mapovať výhradne cez `issuer + sub`;
6. zrušiť unsafe email links a vykonať controlled re-linking;
7. privileged claims povoľovať iba z approved issuer/claim/value contractu;
8. vyžadovať local JIT, tenant, object a workflow authorization;
9. revoke-nuť affected RP sessions, refresh families a downstream tokens;
10. auditovať actions a obnoviť affected settlement state.

## 15. Acceptance verdict

Recovery je prijatá až keď:

- production RP odmietne validly signed token zo staging issuer-a;
- token s wrong `aud`, `azp`, nonce, algorithm alebo expired time zlyhá;
- rovnaký email z iného issuer-a nevytvorí link ani prevezme účet;
- arbitrary group claim nevytvorí privileged role;
- approved production issuer a subject vytvoria správnu bounded session;
- old `FED-SIGN-07` tokeny a sessions sú neplatné;
- local logout, back-channel logout a incident revocation majú overený scope;
- druhý key rollover a second-login test prejdú bez fallbacku na starý key;
- oprávnený user dokončí settlement approval, zatiaľ čo staging, cross-tenant a non-JIT paths zlyhajú.

## 16. Troubleshooting flow

```text
expected issuer a client registration
→ trusted discovery/JWKS generation
→ state, nonce a PKCE transaction
→ OP authentication a code exchange
→ alg/kid/signature
→ iss/aud/azp/time/nonce/assurance
→ issuer+sub identity lookup
→ claims mapping revision
→ local session state
→ resource authorization
→ logout/revocation descendants
```

Login ending in `403` môže znamenať úspešnú authentication a správny local authorization deny. Redirect loop môže byť cookie/proxy/session defect. Unknown `kid` môže byť rotation alebo wrong issuer, nie dôvod trustovať key z tokenu.

## 17. Earlier controls

- unique client IDs a signing keys per environment a purpose;
- issuer allowlist a exact discovery consistency tests;
- negative fixtures pre shared key, wrong issuer a same-email subject;
- federation claim-authority registry;
- no automatic privileged linking podľa emailu;
- session inventory podľa issuer, key generation a mapping revision;
- bounded JWKS refresh a rollover rehearsal;
- back-channel logout a emergency session-revocation drill;
- canary, ktorý testuje povolený production token aj forbidden staging token.

## 18. Anti-patterny

### Signature validná, teda issuer je trusted

Key dokazuje signature authority, nie automaticky správny issuer alebo environment.

### Email je identity

Email je mutable claim a môže kolidovať alebo byť reassigned.

### Group claim je admin role

Bez authority contractu môže partner alebo compromised claim source udeliť privilege.

### ID Token je application session

Token a local session majú odlišný timeout, revocation a authorization lifecycle.

### Logout je global revocation

OP, RP, refresh a API credentials nie sú jedna atomic session.

## 19. Kontrolné otázky

1. Čo OIDC pridáva nad OAuth 2.0?
2. Prečo je issuer primary trust boundary?
3. Ako sa state, nonce a PKCE líšia?
4. Čo musí RP validovať na ID Token-e?
5. Prečo identity key tvorí `issuer + sub`?
6. Prečo email a group claims nie sú automatická business authority?
7. Ako sa ID Token, access token a local session líšia?
8. Ako sa `auth_time`, `acr` a `amr` dopĺňajú?
9. Prečo shared signing key nerobí dva issuers ekvivalentnými?
10. Čo musí overiť OIDC acceptance verdict?

## Glossary impact

Relevantné pojmy: OIDC subject, issuer trust generation, OIDC transaction generation, ID Token acceptance verdict, federation identity key, claims-authority contract, session-assurance generation, issuer-bound account linking, key-generation session inventory a OIDC revocation closure.

## Primárne zdroje

- [OpenID Connect Core 1.0 incorporating errata set 2](https://openid.net/specs/openid-connect-core-1_0.html)
- [OpenID Connect Discovery 1.0 incorporating errata set 2](https://openid.net/specs/openid-connect-discovery-1_0.html)
- [OpenID Connect Back-Channel Logout 1.0](https://openid.net/specs/openid-connect-backchannel-1_0.html)
- [OpenID Connect RP-Initiated Logout 1.0](https://openid.net/specs/openid-connect-rpinitiated-1_0.html)
- [RFC 9207 — Authorization Server Issuer Identification](https://www.rfc-editor.org/rfc/rfc9207)
- [RFC 9700 — OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OAuth 2.0](oauth-2.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: SAML →](saml.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
