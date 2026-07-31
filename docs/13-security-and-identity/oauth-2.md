# OAuth 2.0

OAuth 2.0 je authorization framework pre delegovaný alebo workload access k protected API. Authorization Server vydá access token, ale Resource Server stále rozhoduje, či exact client alebo principal smie vykonať exact action nad exact resource-om v aktuálnom business context-e. Protocol-correct Authorization Code + PKCE flow preto nevyrieši stale identity input, broad audience, chýbajúcu tenant/object authorization ani neúplnú revocation.

OAuth sa nemá opisovať iba ako „login cez Google“ alebo ako JWT mechanizmus. Framework oddeľuje Resource Ownera, Clienta, Authorization Server a Resource Server a definuje, ako client získa obmedzené oprávnenie. Authentication usera je samostatná vrstva, ktorú typicky poskytuje OpenID Connect.

## Grant-to-resource lifecycle

OAuth grant je iba prechod k obmedzenej capability; konečný verdict vzniká až na Resource Serveri nad exact resource a current contextom. Lifecycle preto oddeľuje transaction binding, token generation, token validation a local business authorization.

```text
protected operation a delegation intent
→ issuer, client a resource registration
→ authorization transaction a user/session context
→ state, redirect URI a PKCE binding
→ authorization code alebo iný grant
→ token endpoint a client authentication
→ access/refresh token generation
→ audience, scope, lifetime a sender binding
→ Resource Server validation
→ tenant, object a business authorization
→ refresh, exchange, revocation a descendant closure
```

Úspech na token endpoint-e nie je resource access verdict. Platná signature nie je správny audience. Scope nie je object ownership. Revoked refresh token neznamená automaticky zrušenie všetkých už vydaných access tokens a application sessions.

## Exact OAuth subject SEC-PAY-48

Subject viaže protocol transaction na issuer, client, resource server, audience, scope, identity input generation a descendant tokens. Toto umožňuje rozlíšiť protocol-correct flow od authorization rozhodnutia založeného na stale directory state-e.

```yaml
issuer: https://id.atlas.example
clientId: settlement-approval-web
clientType: public-browser-client
redirectUri: https://approval.atlas.example/callback
resourceServer: https://api.payments.atlas.example
requestedOperation: approve-settlement
resource: settlement/op-884
authorizationCode: CODE-884
pkceMethod: S256
accessTokenAudience: atlas-internal
accessTokenScope: payments.approve
subject: urn:atlas:human:7421
identityInputGeneration: stale-AD-DC-FRA-02
accessTokenLifetime: 1h
refreshTokenFamily: RTF-991
incident: SEC-PAY-48
```

Subject ukazuje, že protocol transaction môže byť správna, zatiaľ čo issuer používa stale directory authorization input a Resource Server prijíma príliš broad audience a scope.

## Authorization Code + PKCE

Browser alebo native public client nemôže bezpečne chrániť static client secret. Authorization Code flow s PKCE vytvorí per-transaction secret `code_verifier`; authorization request posiela jeho derived `code_challenge` a token endpoint neskôr vyžaduje original verifier. `state` viaže callback na local transaction a chráni pred request/response mix-upom. Exact redirect URI bráni odoslaniu code-u na attacker-controlled endpoint.

Príprava PKCE hodnôt:

```bash
CODE_VERIFIER="$(openssl rand -base64 64 | tr -d '=+/' | cut -c1-64)"
CODE_CHALLENGE="$(printf '%s' "$CODE_VERIFIER" | openssl dgst -sha256 -binary | openssl base64 -A | tr '+/' '-_' | tr -d '=')"
printf 'verifier=%s\nchallenge=%s\n' "$CODE_VERIFIER" "$CODE_CHALLENGE"
```

Výstup preukazuje local generation verifier/challenge pair. Nepreukazuje, že Authorization Server vyžaduje `S256`, transaction používa unpredictable `state`, redirect URI je exact alebo code nebol replay-nutý.

Token exchange:

```bash
curl -fsS https://id.atlas.example/oauth2/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'grant_type=authorization_code' \
  --data-urlencode "code=$AUTHORIZATION_CODE" \
  --data-urlencode 'client_id=settlement-approval-web' \
  --data-urlencode 'redirect_uri=https://approval.atlas.example/callback' \
  --data-urlencode "code_verifier=$CODE_VERIFIER" \
  | jq '{token_type, expires_in, scope, access_token_present: has("access_token"), refresh_token_present: has("refresh_token")}'
```

Response preukazuje token-endpoint outcome pre konkrétny code transaction. Nepreukazuje access-token signature, audience, sender binding, Resource Server acceptance ani business authorization. Token values sa nesmú logovať do CI alebo incident artifacts.

## Access token, authorization code a refresh token

Authorization code je krátkodobý one-time grant určený pre token endpoint. Access token je capability prezentovaná Resource Serveru. Refresh token umožňuje získať nové access tokens a má dlhší lifecycle, preto potrebuje silnejšie storage, rotation a reuse detection. Client credential alebo private key je autentikátor clienta, nie user access token.

Opaque token vyžaduje introspection alebo gateway lookup. JWT token môže Resource Server validovať lokálne, ale revocation je ťažšia a claims môžu zostať stale do expiry. Voľba nie je iba performance rozhodnutie; určuje availability, revocation latency, privacy a key-distribution boundary.

## Audience a scope

Audience identifikuje Resource Server alebo resource set, pre ktorý je token určený. Scope opisuje delegated capability. Broad audience `atlas-internal` umožňuje confused-deputy a token replay medzi APIs. Resource-specific audience `payments-api` a narrow scope `settlements.approve` znižujú blast radius, no stále nehovoria, ktorý settlement alebo tenant principal smie schváliť.

Resource Server musí po token validation vykonať local authorization:

```text
validated issuer + subject/client
+ exact audience
+ scope
+ tenant membership
+ object ownership/workflow state
+ current JIT/revocation context
→ allow alebo deny
```

`scope=payments.approve` nie je náhrada `settlement op-884 patrí tenant-u X, čaká na approval a principal má current approval assignment`.

## Resource Server validation a 401/403

JWT validation zahŕňa trusted issuer bootstrap, allowed algorithms, signature, key selection, audience, expiration/not-before, token type a required claims. Client-supplied `jku`, `x5u` alebo arbitrary issuer URL nesmie určovať trust source bez allowlistu.

API call s explicitným audience-bound tokenom:

```bash
curl -i https://api.payments.atlas.example/v1/settlements/op-884/approve \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H 'Idempotency-Key: approval-op-884-SEC-PAY-48'
```

`401 Unauthorized` typicky znamená chýbajúcu alebo neplatnú authentication/token boundary. `403 Forbidden` znamená, že token bol rozpoznaný, ale operation nie je povolená. Implementácia musí neodhalovať sensitive object existence a súčasne auditovať exact deny reason interne. HTTP code sám nepreukazuje, ktorá policy alebo business check rozhodla.

## Public a confidential clients

Public client nedokáže chrániť static secret a používa PKCE. Confidential client beží v kontrolovanom backend-e a autentizuje sa na token endpoint-e, ideálne asymmetric private-key metódou alebo mTLS namiesto shared secretu. „Confidential“ nie je vlastnosť názvu clienta; závisí od deployment boundary a credential protection.

Client Credentials flow reprezentuje workload/client, nie usera. Device Authorization flow podporuje input-constrained device, ale phishing a user-code handling vyžadujú pozornosť. Token Exchange môže vytvoriť downstream token s novým audience a scope; exchange graph musí zachovať original actor, effective client a revocation descendants.

## Refresh rotation a reuse detection

Refresh-token rotation vydá pri každom použití nový token a zneplatní previous member family. Ak sa starý token objaví znovu, reuse detection má revoke-nuť celú family, pretože nevie rozlíšiť legitímny client od attacker copy.

Rotation state musí byť atomic. Dva concurrent refresh requests môžu inak vytvoriť false reuse alebo dve platné branches. Client potrebuje bounded retry a recovery pre unknown token-endpoint outcome; blind retry po timeout-e môže použiť už spotrebovaný token.

Revocation endpoint:

```bash
curl -fsS https://id.atlas.example/oauth2/revoke \
  -u "settlement-approval-backend:$CLIENT_SECRET" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "token=$REFRESH_TOKEN" \
  --data-urlencode 'token_type_hint=refresh_token'
```

Successful response preukazuje, že Authorization Server request prijal podľa svojho contractu. Nepreukazuje okamžitú invalidáciu self-contained access tokens, application cookies, exchanged tokens alebo cached authorization decisions. Secret v command line môže uniknúť process listingom; production automation používa bezpečný credential injection.

## Bearer a sender-constrained tokens

Bearer token môže použiť ktokoľvek, kto ho získa. mTLS-bound alebo DPoP-bound token viaže capability na key proof a znižuje replay z ukradnutého tokenu. Sender constraint však nevyrieši malware ovládajúci legitímny client key ani chýbajúcu object authorization.

Resource Server musí validovať binding na každom requeste a token exchange musí zachovať alebo explicitne zmeniť binding. Gateway, ktorá binding overí, ale downstream service prijme token priamo bez overenia, vytvorí bypass path.

## Deprecated a nebezpečné patterns

Implicit flow odovzdáva token cez browser front channel a pre nové návrhy sa nepoužíva. Resource Owner Password Credentials grant obchádza modernú authentication orchestration, MFA a federation a nové návrhy ho nemajú používať. Static long-lived bearer tokens a shared client secrets bez rotation vytvárajú nejasnú attribution a vysokú revocation latency.

## Incident `SEC-PAY-48`

Authorization Code + PKCE transaction bola protocol-correct. `state`, exact redirect a verifier sedeli. Authorization Server však autentizoval principal cez fresh Kerberos ticket, ktorého PAC vznikol na stale AD replica. Následne vydal hodinový JWT s audience `atlas-internal` a scope `payments.approve`.

Resource Server validoval signature, issuer, expiration, broad audience a scope, ale nekontroloval current JIT assignment, tenant, exact settlement object ani directory generation. Privileged approval preto prešla. Root cause bol neconverged AD state; broad audience, long token lifetime a scope-only authorization boli causal amplifiers.

Competing hypotheses zahŕňali stolen code, PKCE bypass, forged JWT, wrong issuer, stale token, Resource Server object-authorization defect a stale directory input. Fresh issue times a valid protocol evidence vylúčili replay starého tokenu. AD replica metadata a PAC/claim lineage ukázali stale authority.

## Containment a authoritative recovery

Containment zablokuje approval operation pre affected principal/tenant, revoke-ne refresh family a application session a zachová authorization request, token metadata bez secret values, issuer/key IDs, Resource Server decision log a business side effect. Global token-key rotation sa nevykonáva bez dôkazu signing-key compromise.

Recovery obnoví directory convergence, vydá resource-specific token s audience `payments-api`, zúži scope, pridá current JIT a object-level authorization a zavedie short lifetime alebo online revocation pre high-risk operations. Existing refresh, exchanged tokens a application cookies sa revoke-nú ako descendant graph.

Acceptance vyžaduje, aby validný authorized principal schválil intended settlement, affected principal dostal deny cez existing aj fresh token, token s wrong audience zlyhal, scope bez object assignment zlyhal, reused refresh token revoke-nul family a audit zachoval issuer, subject, client, audience, scope, policy revision, object a result. Druhý authorization po membership change musí odrážať current authority bez čakania na starú hodinovú token lifetime.

## Kontrolné otázky

1. Prečo protocol-correct PKCE flow nepreukazuje business authorization?
2. Aký rozdiel je medzi audience a scope?
3. Prečo `payments.approve` nestačí bez object-level checku?
4. Čo revocation endpoint nepreukazuje pre JWT descendants?
5. Ako refresh rotation rieši stolen-token reuse a aký concurrency problém vytvára?
6. Kedy sender-constrained token stále nezabráni abuse?
7. Prečo root cause incidentu nebol OAuth protocol?

## Referencie

- [OAuth 2.0 Authorization Framework](https://www.rfc-editor.org/rfc/rfc6749)
- [OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700)
- [PKCE](https://www.rfc-editor.org/rfc/rfc7636)
- [OAuth 2.0 Token Revocation](https://www.rfc-editor.org/rfc/rfc7009)
- [OAuth 2.0 Token Introspection](https://www.rfc-editor.org/rfc/rfc7662)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Kerberos](kerberos.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: OpenID Connect →](openid-connect.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
