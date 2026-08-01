# Public, confidential a bearer-only client model

Keycloak client type nie je UI label podľa toho, či aplikácia má frontend alebo backend. Je to threat a capability contract: kde kód beží, či dokáže chrániť client credential, ktoré OAuth/OIDC grants môže používať, či iniciuje browser authentication, či má vlastnú service account identity a či iba prijíma access tokens ako resource server.

```text
application/runtime architecture
→ exact client responsibility a trust boundary
→ public, confidential alebo bearer-only capability model
→ enabled grants a endpoints
→ client authentication method
→ redirect/backchannel a token-storage contract
→ issued token a audience
→ resource-server validation
→ credential rotation, revocation a second-instance test
```

Najčastejšia chyba nie je zvolený nesprávny názov. Je to jeden client, ktorý súčasne reprezentuje desktop CLI, browser app, backend service a API. Taká registrácia nemá jednu bezpečnostnú boundary a každá pohodlná capability rozširuje blast radius ostatných runtimes.

## 1. Current Keycloak configuration a historické názvy

V súčasnom Keycloak Admin Console sa public a confidential model primárne prejavuje prepínačom `Client authentication`. Keď je authentication vypnutá, client je public a pri token endpoint-e nemá client credential. Keď je zapnutá, client je confidential a musí nakonfigurovať secret, private-key JWT, mTLS alebo inú supported client-authentication metódu.

Pojem bearer-only zostáva dôležitý pre resource-server model a niektoré adapters/representations. Bearer-only client neinitiates browser login a nepoužíva interactive redirect flow. Prijíma bearer token, validuje ho a chráni resources. V modernom service design-e môže byť resource-server registration reprezentovaná clientom s vypnutými interactive a machine grants a s audience/client-role contractom; exact product/configuration generation treba overiť, nie spoliehať sa iba na starý access-type label.

Public/confidential opisuje schopnosť autentizovať clienta voči authorization serveru. Bearer-only opisuje jeho runtime responsibility voči incoming access tokenom. Resource server môže mať confidential outbound identity pre iné calls, ale tá má byť samostatným client registrationom, aby sa inbound audience a outbound credentials nezliali.

## 2. Exact client-mode subject

Acceptance subject zahŕňa realm a client generation, application components a deployment locations, code distribution, secret/key storage, enabled Standard/Implicit/Direct Access Grants/Service Accounts/Device/CIBA/token-exchange capabilities, redirect URIs, PKCE, client authenticator, service-account roles, linked scopes, token lifetimes, audiences a logout/revocation behavior.

Tento subject spája configuration s konkrétnou runtime boundary. Samotný prepínač `Client authentication` nevysvetľuje, kto client používa, kde sa credential nachádza ani ktoré granty zostali zapnuté. Pri incident analysis sa preto musí preukázať celý capability set a jeho effective použitie, nie iba export client representation alebo názov access modelu.

Rozmery subjectu sa hodnotia spolu. Public binary s náhodne vloženým secretom sa nestane confidential clientom, pretože každý používateľ vlastní jeho kópiu. Naopak server-side workload s chráneným keyom nie je bezpečný, ak má zároveň nepotrebné redirects, Direct Grants a broad service-account roles. Exact subject umožňuje vytvoriť positive aj negative matrix pre každý samostatný runtime job.

```text
client settlement-ops-cli
→ native desktop binary distribuovaný používateľom
→ public
→ Authorization Code + PKCE S256 alebo Device Grant
→ no secret
→ no service account
→ exact loopback/custom redirect contract
```

```text
client settlement-batch
→ server-side Kubernetes workload
→ confidential
→ client_credentials only
→ private-key JWT alebo mTLS
→ scoped service account
→ no browser redirect
```

```text
client settlement-api
→ resource server
→ bearer-only/inbound API contract
→ no interactive grants
→ audience settlement-api
→ local authorization
```

## 3. Public clients

Public client beží v prostredí, kde credential nemožno udržať dôverný: browser JavaScript, desktop/mobile package alebo distributed CLI. Secret vložený do bundle, executable, source map, mobile APK alebo user config je shared identifier, nie autentizácia client instance-u. Útočník ho môže extrahovať a použiť mimo application.

Public interactive client používa Authorization Code + PKCE, typicky `S256`. PKCE viaže authorization code na per-transaction verifier a znižuje riziko code interception. Stále potrebuje exact redirect allowlist, `state`, OIDC `nonce`, issuer validation a secure token storage primeraný platforme.

Public client nemá dostať service-account capability. `client_credentials` bez client authentication by nepreukázal machine identity. Device Authorization Grant môže byť vhodný pre CLI alebo limited-input device, ale device code/user code lifecycle, phishing resistance a token storage sú samostatné boundaries.

Direct Access Grants/Resource Owner Password Credentials prenášajú user credential clientovi a obchádzajú browser authentication capabilities. Pre nové designs sa nemajú používať ako náhrada za native/browser flow. Zapnutie grant-u pre debug môže neskôr vytvoriť permanentný alternate authentication path bez MFA, WebAuthn alebo broker policy.

## 4. Confidential clients

Confidential client beží v controlled server-side environment-e a vie chrániť credential. `Client authentication` je zapnutá a token endpoint overuje secret, signed JWT/private key, mTLS alebo supported federated credential. Credential musí byť scoped, rotovateľný a viazaný na konkrétnu workload identity/deployment boundary.

Client secret je bearer-like shared credential. Každá replica, backup, CI variable a support dump môže byť jeho copy. Private-key JWT alebo mTLS znižujú zdieľanie symmetric secretu, ale private key lifecycle, assertion audience/jti/time a certificate rotation musia byť správne.

Confidential web application môže používať Authorization Code flow a server-side code exchange. To neznamená, že nepotrebuje PKCE; PKCE môže chrániť transaction aj pri authenticated clientovi. Confidential machine client môže používať client credentials a vôbec nemať browser endpoints. Tieto responsibilities sa nemajú kombinovať automaticky len preto, že obe vedia chrániť credential.

## 5. Bearer-only resource server

Resource server prijíma access token v `Authorization: Bearer` a nevytvára OIDC login redirect. API request bez tokenu má dostať protocol-appropriate `401`, nie HTML login page alebo browser redirect. Resource server validuje exact issuer, signature/key generation, lifetime, token type, audience a local policy.

Bearer-only neznamená, že API dôveruje každému tokenu z realm-u. Musí kontrolovať intended `aud`, caller/client identity podľa contractu, subject type, scopes/roles, tenant a requested resource. Token issued to Account Console alebo unrelated client nemá byť prijatý iba preto, že používa rovnaký realm signing key.

Ak service potrebuje volať downstream API, outbound identity je separate confidential client. Inak jedna registration môže mať inbound client roles, browser redirect, service account a downstream audience naraz. Incident response potom nevie revoke-nuť outbound credential bez ovplyvnenia inbound API identity.

## 6. Grant capability matrix

Client capabilities majú byť allowlist podľa runtime jobu:

```text
public SPA/native
→ Standard Flow + PKCE
→ optional Device Grant podľa jobu
→ no service accounts
→ no secret

confidential web/BFF
→ Standard Flow + client authentication + PKCE
→ no service account, ak nepotrebuje machine identity

confidential daemon
→ Service Accounts/client_credentials
→ no redirects, no Standard Flow

resource server
→ no issuance grant
→ incoming bearer validation only
```

Implicit Flow zvyšuje token exposure vo front-channeli a pre nové designs sa nepoužíva. Direct grants, token exchange, CIBA a device flow sa povoľujú iba pri explicitnom use case, client policy a negative tests. Prepínač zapnutý pre test je production attack surface.

Client Policies a profiles môžu enforce-nuť requirements pre public/confidential clients, ale effective coverage potrebuje inventory a match evidence. Policy existence bez client matchu nevytvára protection.

## 7. Redirect, browser, backchannel a credential surfaces

Public/confidential mode nemení redirect URI na menej dôležitý. Confidential client secret nechráni pred authorization code doručeným útočníkovmu redirect endpointu. Exact alebo bounded redirects, external hostname a proxy trust zostávajú required.

Browser surface zahŕňa authorization endpoint, cookies, callback a front-channel logout. Backchannel surface zahŕňa token, introspection, revocation a backchannel logout endpoints. Machine client môže potrebovať iba token endpoint. Resource server môže potrebovať JWKS/discovery alebo introspection. Každý unnecessary endpoint/grant rozširuje test a incident boundary.

Credential rotation musí overiť všetky replicas a old-credential denial. Rotation secretu neinvaliduje už vydané access tokens. Public client nemá credential rotation; potrebuje application release, redirect registration a token/session incident controls.

## 8. Client separation a stable identities

Samostatné client registrations nie sú administratívny overhead, ale isolation. Web, CLI, batch a API majú odlišné:

```text
client authentication
→ grant types
→ redirect URIs
→ token storage
→ audiences
→ role scopes
→ lifetimes
→ revocation blast radius
```

Client ID je protocol identity a má byť environment-specific. Staging a production sharing one client/secret spája redirect a credential trust. Internal client UUID sa môže zmeniť pri delete/recreate/import; automation a audit nemajú používať display name bez realm/generation.

Separation potrebuje ownership a inventory. Orphan client s enabled grantom a valid secretom zostáva attack path. Decommission zahŕňa traffic/token evidence, secret/key revoke, sessions/tokens, mapper/scope removal a negative authentication test.

## 9. Connected incident `KC-PAY-66`

`settlement-ops` bol pôvodne desktop CLI, no neskôr ho batch tím použil aj pre automation. Client authentication sa zapla a secret `s-ops-17` sa vložil do CLI balíka `4.6`. Standard Flow, Direct Access Grants a Service Accounts zostali enabled. Client mal redirect URIs pre desktop aj web preview a broad scopes.

O `09:17 UTC` útočník extrahoval secret. Nemusel kompromitovať human MFA ani browser session. O `09:21 UTC` zavolal token endpoint s `grant_type=client_credentials` a získal service-account access token. Rovnaký client bol zároveň považovaný za audience/caller pre `settlement-api`.

Resource server nebol prevádzkovaný ako úzky bearer-only contract. Registration mala interactive grants a service account, takže client identity neodlišovala user-facing CLI od machine daemonu. Do `10:08 UTC` útočník exportoval `1 148` records a odoslal `83` reconciliation commands.

Primary client-mode root cause bolo zmiešanie public distributed application, confidential machine clienta a resource-server access contractu do jednej registration. Secret leakage bol trigger; broad roles/mappers a API authorization boli amplifiers.

## 10. Authoritative redesign a acceptance paths

`settlement-ops-cli` má `Client authentication=Off`, Standard Flow + PKCE S256 alebo approved Device Flow, no Service Accounts, no Direct Grants a exact redirects. Binary ani config neobsahujú client secret.

`settlement-batch` má `Client authentication=On`, Service Accounts enabled, private-key JWT/mTLS a no browser grants/redirects. `settlement-api` má iba resource-server/bearer-only role/audience contract a nemôže iniciovať login ani získať service-account token.

Positive test overí každý intended grant. Negative matrix odmietne client credentials pre CLI, authorization redirect pre batch/API, direct grant, wrong client secret/key, wrong audience a mixed environment. Secret extraction z public package nesmie poskytnúť žiadnu machine capability. Second workload rotation overí old credential denial a existing-token incident behavior.

## 11. Troubleshooting a anti-patterny

Pri unexpected token issuance sa inventarizuje client mode, runtime locations, `Client authentication`, enabled grants, redirect URIs, PKCE, client authenticator, service-account roles, linked scopes, token endpoint event a actual caller. Pri API redirect loop-e sa overí, či resource server omylom iniciuje browser flow. Pri `unauthorized_client` sa neprepína náhodne capability; porovná sa requested grant s registered jobom.

Anti-patterny sú: `secret v SPA/CLI je confidential`, `jeden client pre frontend, backend aj API`, `Client authentication On vyrieši redirect security`, `bearer-only znamená validovať iba signature`, `zapnime všetky grants pre flexibilitu`, `debug Direct Grant ponecháme`, `staging a production môžu zdieľať secret` a `credential rotation zruší tokens`.

## Glossary impact

Relevantné pojmy: Keycloak client capability model, public client, confidential client, bearer-only resource server, Client authentication, grant allowlist, mixed-purpose client, distributed secret anti-pattern, outbound client identity, resource-server audience contract a client-mode acceptance matrix.

## Primárne zdroje

- [Keycloak — Server Administration Guide: Managing OpenID Connect clients](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak — Securing applications and services with OpenID Connect](https://www.keycloak.org/securing-apps/oidc-layers)
- [OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700.html)
- [RFC 8252 — OAuth 2.0 for Native Apps](https://www.rfc-editor.org/rfc/rfc8252.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Tokens, claims, protocol mappers a client scopes](tokens-claims-protocol-mappers-client-scopes.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Service accounts a machine-to-machine authentication →](service-accounts-and-machine-to-machine-authentication.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
