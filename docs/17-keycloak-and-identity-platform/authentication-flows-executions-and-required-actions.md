# Authentication flows, executions a required actions

Keycloak authentication flow nie je zoznam login obrazoviek. Je to server-side decision graph, ktorý pre konkrétnu authentication transaction vyhodnocuje existujúcu SSO session, credentials, MFA, identity brokering, conditions, required actions a client-specific policy. Poradie executions, ich requirement, subflow structure, authenticator configuration a realm alebo client binding určujú, či transaction skončí challenge, success, failure alebo redirectom do ďalšieho lifecycle-u.

Najčastejší omyl je pridať OTP execution do flowu a považovať MFA za povinnú. Ak Cookie authenticator ako `ALTERNATIVE` uspokojí top-level flow cez remembered SSO session, neskorší forms/MFA branch sa nemusí vykonať. Ak client používa Direct Access Grant, Browser flow sa nevykonáva vôbec. Ak required action nastavíš ako default, existujúci users ju automaticky nemusia dostať. Authentication acceptance preto musí testovať fresh login, remembered SSO, client-specific step-up, required action, Direct Grant negative path, second browser a session revocation.

## 1. Dominantný transaction-to-session model

Flow evaluation začína authorization alebo token requestom a exact clientom. Keycloak vytvorí authentication session a vyberie realm flow binding alebo client override. Executions a subflows sa vyhodnotia podľa requirement a aktuálneho contextu. Po úspešnej credential a authenticator fáze sa vykonajú pending required actions; až potom vznikne alebo sa rozšíri user/client session a vydá protocol response.

```text
login alebo token request
→ exact realm, client a flow-binding generation
→ authentication session, tab/transaction a protocol inputs
→ top-level flow a ordered executions/subflows
→ cookie, username/password, federation alebo broker authentication
→ MFA, conditional a step-up evaluation
→ authenticated user identity
→ pending required actions
→ Keycloak user a client session
→ code/token/SAML response
→ local application session a resource authorization
→ logout/revocation, second-login a failure-path validation
```

Žiadna fáza sa nemá inferovať z finálneho tokenu. Token s `amr` alebo `acr` claimom môže pomôcť, ale downstream musí vedieť, ktorá flow a authenticator generation ho vytvorila a či claim zodpovedá aktuálnemu security contractu. Zelený login nepreukazuje fresh authentication, step-up ani vykonanie intended required action.

## 2. Exact authentication transaction subject

Pri incidente „MFA sa preskočila“ nestačí screenshot Browser flowu. Zachovaj:

```yaml
authenticationTransactionSubject:
  keycloak:
    publicBaseUrl: https://sso.atlas.example
    deploymentGeneration: kc-2026-08-01-17
    realm: atlas-prod
    realmIssuer: https://sso.atlas.example/realms/atlas-prod
  client:
    clientId: payments-admin-web
    internalId: 7f00e85a-8d89-4f18-8a5c-c3e2135d0cb6
    configurationRevision: client-184
    authenticationFlowOverrides:
      browser: atlas-privileged-browser-v4
      directGrant: null
  request:
    protocol: oidc
    responseType: code
    redirectUri: https://payments-admin.atlas.example/oauth/callback
    stateHash: sha256:...
    nonceHash: sha256:...
    codeChallengeMethod: S256
    prompt: login
    maxAge: 0
  authenticationSession:
    rootSessionId: 67df...
    tabId: I3f...
    startedAt: 2026-08-01T09:17:23Z
  flow:
    alias: atlas-privileged-browser-v4
    internalId: 4b23...
    revision: auth-flow-72
    executionIds: [cookie-v1, forms-subflow-v4, webauthn-stepup-v3]
  user:
    userId: 1d86...
    existingUserSessionId: 42b1...
  requiredActions:
    pending: [VERIFY_EMAIL, CONFIGURE_TOTP]
    configurationRevision: required-actions-19
```

Rovnaký client môže používať realm Browser flow alebo client-specific override. Rovnaký flow alias po copy/delete/recreate môže mať nové execution IDs a priorities. Rovnaký user môže mať remembered SSO session, ale nový authentication session pre ďalší client. Exact subject preto zahŕňa request, flow binding, execution graph, user session a pending actions.

## 3. Top-level flows a realm bindings

Realm typicky binduje samostatné flows pre Browser, Direct Grant, Registration, Reset Credentials, Client Authentication a ďalšie protocol-specific lifecycles. Client môže mať authentication-flow overrides pre vybrané bindings.

```text
realm browserFlow = browser
client payments-admin-web browser override = atlas-privileged-browser-v4
→ authorization request pre payments-admin-web používa override

client inventory-ui bez override
→ používa realm browserFlow
```

Realm binding zmena má široký blast radius. Client override znižuje scope, ale môže vytvoriť policy drift medzi privileged clients. Flow acceptance preto potrebuje expected-client inventory a negative test, že susedný client zostal na svojom intended flowe.

Built-in flow sa nemá upravovať ako production-owned artifact. Bezpečný lifecycle je copy, versionovaný alias, reviewed execution graph, test client override, staged client cohort a až potom realm-level promotion, ak je to zámer.

## 4. Executions, priorities a requirement semantics

Flow obsahuje authenticator executions a subflows. Priority určuje order. Requirement určuje, ako výsledok executionu ovplyvní parent flow.

**REQUIRED** execution sa musí úspešne dokončiť. Failure blokuje flow.

**ALTERNATIVE** executions reprezentujú viac ciest, z ktorých jedna môže uspokojiť danú úroveň. Typický Browser flow používa Cookie authenticator ako alternatívu k interactive forms. Ak validná SSO cookie uspeje, username/password a MFA branch sa nemusí vykonať.

**CONDITIONAL** sa používa pre subflow, ktorý sa správa ako required iba vtedy, keď jeho condition executions vyhodnotia true. Condition a authenticator musia patriť do správnej subflow a priority.

**DISABLED** execution sa nevyhodnocuje.

```text
Cookie [ALTERNATIVE]
Forms subflow [ALTERNATIVE]
  Username Password Form [REQUIRED]
  Conditional OTP subflow [CONDITIONAL]
    Condition - user configured [REQUIRED]
    OTP Form [REQUIRED]
```

Miešanie `REQUIRED` a `ALTERNATIVE` executions na rovnakej úrovni je často nesprávny graph. Required path môže zmeniť alebo zatieniť očakávanú alternative semantics. Review má čítať tree, level, priority a requirement spolu, nie iba názvy authenticators.

## 5. Cookie authenticator a remembered SSO

Cookie authenticator validuje existujúcu Keycloak user session a môže autentizovať nový client bez nového credential promptu. To je základ SSO, nie chyba. Chybou je predpokladať, že každé prihlásenie do privileged clienta automaticky vykoná rovnakú MFA ako fresh login.

```text
existing Keycloak user session
→ Cookie authenticator success
→ Browser flow satisfied
→ new client session
→ code/token
```

Citlivý client môže potrebovať fresh authentication, vyšší ACR/LoA, step-up alebo explicitný client-specific flow. Request parameters ako `prompt` a `max_age`, Authentication Context/LoA policy a client overrides musia byť navrhnuté ako jeden contract. Samotné skrytie „Remember me“ alebo skrátenie browser cookie nestačí.

Acceptance testuje:

```text
fresh browser bez SSO session
existing SSO session s dostatočným authentication levelom
existing SSO session s nedostatočným levelom
session staršia než max-age contract
susedný non-privileged client
```

## 6. Conditional MFA a step-up

Conditional subflow rozhoduje, či sa MFA execution vykoná. Condition môže zohľadniť, či user má OTP/WebAuthn credential, requested authentication level, client, user role alebo ďalší context podľa dostupných authenticators a extension generation.

Bezpečnostne kritická condition potrebuje explicitnú false semantics. Napríklad `Condition - user configured` môže pri userovi bez OTP vyhodnotiť false a preskočiť OTP. Ak policy vyžaduje MFA pre každého privileged usera, chýbajúca credential má viesť k required action enrollment alebo denial, nie k single-factor loginu.

```text
privileged client + user bez MFA credential
→ enrollment required action alebo deny
≠ conditional branch silently skipped
```

Step-up musí byť viazaný na protected operation a current session. Aplikácia nemá iba skontrolovať, že user niekedy použil MFA. Potrebuje current authentication context alebo fresh authentication podľa risk contractu. Downstream API môže vyžadovať `acr`/`amr` a auth-time/max-age, ale claim values musia mať stabilnú Keycloak flow mapping a consumer validation.

## 7. Inventory flow bindings a executions

Realm bindings:

```bash
kcadm.sh get realms/atlas-prod \
  --fields realm,browserFlow,directGrantFlow,resetCredentialsFlow,clientAuthenticationFlow
```

Output preukazuje uložené aliases realm bindings v danom admin targete. Nepreukazuje client overrides, execution graph ani runtime login path.

Client overrides:

```bash
CLIENT_UUID="$({
  kcadm.sh get clients \
    -r atlas-prod \
    -q clientId=payments-admin-web \
    --fields id,clientId,authenticationFlowBindingOverrides
} | jq -er '.[0].id')"

kcadm.sh get "clients/${CLIENT_UUID}" \
  -r atlas-prod \
  --fields id,clientId,authenticationFlowBindingOverrides
```

Flow inventory:

```bash
kcadm.sh get authentication/flows \
  -r atlas-prod \
  --fields id,alias,description,providerId,topLevel,builtIn

kcadm.sh get 'authentication/flows/atlas-privileged-browser-v4/executions' \
  -r atlas-prod \
  | jq '[.[] | {id,displayName,requirement,priority,level,flow,authenticationConfig}]'
```

Execution list preukazuje stored graph representation pre alias. Nepreukazuje, že request použil tento flow, že authenticator provider bol loaded alebo že condition vyhodnotila intended context. Runtime acceptance potrebuje authentication events, request correlation a token/session outcome.

## 8. Copy a promotion flowu

Production zmena má predecessor a successor flow generation. Copy built-in alebo current custom flow, zmeň alias a description, uprav executions, priraď test clientovi a až po acceptance rozšír binding.

Admin REST copy operation má exact source alias a successor name:

```bash
ADMIN_TOKEN="$(kcadm.sh config credentials \
  --server https://sso-admin.atlas.example \
  --realm master \
  --client admin-cli \
  --user "$KC_ADMIN_USER" \
  --password "$KC_ADMIN_PASSWORD" \
  >/dev/null && kcadm.sh config token)"

curl --fail --silent --show-error \
  --request POST \
  --header "Authorization: Bearer ${ADMIN_TOKEN}" \
  --header 'Content-Type: application/json' \
  --data '{"newName":"atlas-privileged-browser-v4"}' \
  'https://sso-admin.atlas.example/admin/realms/atlas-prod/authentication/flows/browser/copy'
```

Operation success preukazuje, že Admin API prijalo copy request. Nepreukazuje exact child execution configuration, priority, client binding ani login outcome. Nasleduje read-back nového flowu, execution tree diff a client-specific test.

Credential v command example sa nesmie objaviť v shell history alebo logs. Reálny automation používa short-lived workload identity a secret source; admin token a server-side Admin API endpoint majú vlastný audit a least-privilege contract.

## 9. Direct Access Grant je samostatný flow

Direct Access Grant spracúva Resource Owner Password Credentials-style token request. Browser flow, redirects, identity brokering, remembered SSO a väčšina interactive authenticators sa nevykonávajú. Aktuálny OAuth 2.0 Security Best Current Practice tento grant neodporúča a moderný production design má používať Authorization Code + PKCE, Device Authorization alebo workload-specific grants.

```text
username + password na token endpoint
→ directGrantFlow
→ direct-grant executions
→ token response
```

Zapnutá MFA v Browser flowe nechráni Direct Grant automaticky. Direct Grant môže mať vlastný OTP execution, ale stále vystavuje user password clientovi, nepodporuje moderný browser security a required actions vyžadujúce interactive UI sa cez tento path nedajú bezpečne dokončiť.

Legacy exception musí mať exact client allowlist, owner, deadline, password handling, brute-force/MFA behavior, telemetry a migration plan. Forbidden test overí, že všetky non-exception clients dostanú pri `grant_type=password` rejection.

## 10. Required actions ako post-authentication lifecycle

Required action sa vykonáva po úspešnej identity/credential authentication a pred dokončením loginu a vydaním protocol response. Príklady sú Verify Email, Update Password, Configure OTP, Update Profile alebo WebAuthn registration podľa enabled providers.

```text
authenticator graph success
→ user identified
→ pending required-action set
→ action challenge a action-token/session validation
→ action-specific authoritative mutation
→ pending action removed alebo retained
→ user/client session completion
→ code/token/assertion
```

Required action nie je iba UI prompt. Mení authoritative user state: credential, email verification, profile alebo terms acceptance. Každá action potrebuje exact user ID, action provider ID, initiating admin/application, action-token generation, expiry, redirect/client context a resulting user/session state.

## 11. Default action, per-user assignment a Application-Initiated Action

Required action môže byť enabled v realm-e, označená ako default pre nových users, priradená konkrétnemu userovi alebo vyvolaná aplikáciou cez Application-Initiated Action contract.

Default action je creation-time behavior pre nových users. Označenie action ako default automaticky nepridá pending action všetkým existujúcim users. Existing population potrebuje explicitný inventory, migration a staged assignment.

Per-user assignment je viditeľný v `requiredActions` user state:

```bash
USER_ID="$({
  kcadm.sh get users \
    -r atlas-prod \
    -q username=alice.payments \
    --fields id,username,enabled,requiredActions
} | jq -er '.[0].id')"

kcadm.sh get "users/${USER_ID}" \
  -r atlas-prod \
  --fields id,username,emailVerified,requiredActions
```

Output preukazuje pending actions uložené pri userovi. Nepreukazuje, že action challenge bola doručená, že user ju dokončil, že nový credential funguje alebo že stará application session bola zrušená.

Application-Initiated Action umožní clientovi požiadať o podporovanú action v OIDC transaction context-e. Client musí validovať návrat a action status a nesmie považovať redirect za dôkaz authoritative mutation bez user-state read-backu.

## 12. Required-action tokens a email links

Email verification alebo admin-initiated action používa signed action token s userom, action, lifespanom a redirect/client contextom. Threat model zahŕňa mailbox compromise, forwarded link, replay, wrong environment, stale user state a redirect manipulation.

```text
action-token issue generation
→ email delivery
→ link open v browseri
→ token signature/time/user/action validation
→ required-action transaction
→ user mutation
→ action-token replay denial
→ second login verification
```

Short lifespan znižuje exposure, ale môže zhoršiť usability pri oneskorenej email delivery. Dlhý lifespan zvyšuje replay window. Admin-initiated action a user-generated action môžu mať odlišné lifespan settings. Acceptance testuje intended link, expired link, replay, wrong user/browser context a redirect allowlist.

## 13. Required action a session descendants

Update Password alebo Configure OTP nemení automaticky všetky downstream sessions podľa jedného univerzálneho pravidla. Keycloak user sessions, refresh/offline tokens a local application sessions majú odlišné lifecycles. Security policy musí určiť, či credential change vyžaduje sign-out other sessions, refresh-token invalidation a application-session reset.

```text
password update completed
→ authoritative credential generation P-18
→ current auth session continues alebo sa obnoví podľa policy
→ existing Keycloak sessions inventory
→ refresh/offline token descendants
→ application sessions
→ protected API validation
```

„User zmenil password“ nie je incident closure. Leaver, compromised credential alebo forced recovery potrebuje explicitný descendant revocation a second-login acceptance.

## 14. Connected incident `KC-PAY-66` — interactive path

Mixed-purpose client `settlement-ops` mal Standard Flow, Direct Access Grants aj Service Accounts. Atlas pridal WebAuthn execution do custom Browser flow, ale Forms subflow zostala `ALTERNATIVE` vedľa Cookie authenticatora. Existing Keycloak SSO session preto otvorila settlement UI bez fresh WebAuthn.

Zároveň bol `CONFIGURE_TOTP` označený ako default required action. Existing settlement operators ho nemali v per-user `requiredActions`, takže sa im enrollment nezobrazil. Legacy CLI používal Direct Access Grant; jeho direct-grant flow obsahoval iba username/password a token vydal bez Browser WebAuthn.

```text
remembered SSO cookie
→ Cookie ALTERNATIVE success
→ privileged client session bez fresh step-up

existing user
→ default required action nebola spätne priradená
→ no enrollment

legacy CLI password grant
→ Direct Grant flow
→ Browser MFA sa nevykonala
→ access token
```

Incident tím najprv pridal OTP ako ďalšiu Browser execution, ale bez opravy graphu a client bindingu to nezmenilo remembered-SSO path. Authoritative redesign oddelil clients, zaviedol privileged browser override s explicitným step-up/LoA contractom, staged per-user MFA enrollment a zakázal Direct Access Grant.

## 15. Evidence-preserving containment a recovery

Zachovaj:

```text
realm a client internal IDs
+ realm flow bindings a client overrides
+ flow aliases, internal IDs, execution tree, priorities a requirements
+ authenticator config IDs a provider generation
+ authentication session/tab correlation
+ existing user/client session IDs a authentication time/context
+ user pending required actions a credential inventory
+ login/direct-grant events a error reasons
+ issued token acr/amr/auth_time/sid/jti
+ downstream application session a business operation IDs
```

Containment môže disable-nuť affected Direct Grant capability, vynútiť fresh login pre privileged client, zastaviť high-risk operations a revoke-nuť affected sessions. Recovery kopíruje predecessor flow do versionovaného successor flowu, opraví graph, nastaví client override, priradí required action intended cohort-e, otestuje enrollment a potom migruje ďalších clients/users.

## 16. Positive, recovery a forbidden acceptance

Positive paths:

```text
fresh privileged login
→ password alebo broker identity
→ required MFA/step-up
→ pending required action dokončená
→ expected acr/amr/auth_time
→ intended operation succeeds

remembered SSO s dostatočným current levelom
→ policy akceptuje bez zbytočného promptu
→ intended operation succeeds
```

Forbidden paths:

```text
remembered low-assurance SSO session
→ privileged client vyžiada step-up
→ no token/session before completion

user bez required MFA credential
→ enrollment alebo denial
→ single-factor fallback absent

non-exception client grant_type=password
→ token endpoint rejects

expired alebo replayed action token
→ required action rejects

required action UI closed/cancelled
→ authoritative user mutation absent
→ app nesmie považovať redirect za success
```

Second-login test overí successor flow po novej SSO session aj po remembered SSO. Second-user test overí existing usera, nového usera a usera bez MFA credential. Second-client test potvrdí, že non-privileged client nezískal unintended step-up alebo broken login behavior.

## 17. Troubleshooting a anti-patterny

Pri preskočenej MFA sa najprv identifikuje exact client a flow override, potom authentication session a existing user session, použitý top-level flow, execution tree, requirement/priority, condition result, user credential inventory a token `acr/amr/auth_time`. Screenshot jedného flowu bez client bindingu a transaction evidence nestačí.

Pri required-action probléme sa oddeľuje provider enabled/default state, per-user pending action, action-token issuance, challenge delivery, action completion, user mutation a session descendants.

Anti-patterny sú: `OTP execution exists = MFA enforced`, `Cookie SSO = fresh authentication`, `default action = všetci users ju majú`, `browser MFA chráni Direct Grant`, `required-action redirect = mutation succeeded`, `flow alias = immutable generation`, `edit built-in flow in place`, `restart Keycloak opraví zlý graph` a `logout page = všetky sessions/tokens revoked`.

## 18. Kontrolné otázky

- Ktorý exact realm/client flow binding a execution generation spracoval transaction?
- Ktorý branch uspel a ktoré executions sa nevykonali?
- Je Cookie authenticator intended pre privileged remembered-SSO path?
- Ako sa vyžaduje fresh authentication alebo vyšší LoA/ACR?
- Je Direct Access Grant vypnutý alebo prísne ohraničený legacy exception contractom?
- Ktoré required actions sú enabled, default a per-user pending?
- Čo action dokončenie mutuje a ktoré session/token descendants treba zrušiť?
- Prešli fresh, remembered, low-assurance, missing-credential, Direct Grant, expired-link, replay, second-user a second-client paths?

## Glossary impact

Relevantné pojmy: Keycloak authentication flow, authentication execution, authentication session, flow binding, client flow override, REQUIRED, ALTERNATIVE, CONDITIONAL, DISABLED, Cookie authenticator, remembered SSO, conditional MFA, step-up authentication, Direct Access Grant, required action, default required action, per-user required action, Application-Initiated Action, action token a required-action descendant revocation.

## Primárne zdroje

- [Keycloak — Server Administration Guide: Authentication flows](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak — Server Administration Guide: Required actions and application-initiated actions](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak — Server Developer Guide: Authenticator and Required Action SPIs](https://www.keycloak.org/docs/latest/server_development/)
- [RFC 9700 — Best Current Practice for OAuth 2.0 Security](https://www.rfc-editor.org/rfc/rfc9700.html)
