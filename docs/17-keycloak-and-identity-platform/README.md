# Keycloak and Identity Platform

Táto sekcia vysvetľuje Keycloak ako identity platformu, nie iba ako login obrazovku alebo implementáciu OAuth 2.0. Stabilné protokolové a bezpečnostné princípy zostávajú autoritatívne v sekcii [Security and Identity](../13-security-and-identity/README.md). Tu sa sleduje, ako ich Keycloak prevádza na realm, client, user, group, role, session, protocol mapper, authentication flow, storage, cache, clustering, administration a operational lifecycle.

Keycloak sa neposudzuje podľa toho, či sa používateľ vie prihlásiť. Platný login môže stále skončiť v nesprávnom realm-e, clientovi, tenantovi, local account-e alebo privilege scope-e. Každá kapitola preto spája configuration generation, exact protocol subject, Keycloak session state, application session, token alebo assertion, downstream authorization a revocation evidence.

## Predpoklady

Odporúča sa najprv dokončiť:

- [Networking and Web Fundamentals](../02-networking-and-web/README.md),
- [Kubernetes](../09-kubernetes/README.md),
- [Cloud and AWS](../11-cloud-and-aws/README.md),
- [Security and Identity](../13-security-and-identity/README.md),
- [SRE and Operations](../14-sre-and-operations/README.md),
- [Databases and Distributed Systems](../15-databases-and-distributed-systems/README.md),
- [GitOps and Platform Engineering](../16-gitops-and-platform-engineering/README.md).

## Authoritative poradie — aktívne kapitoly

1. [Keycloak architecture a responsibility boundary](keycloak-architecture-and-responsibility-boundary.md)
2. [Realm, client, user, group, role a session](realm-client-user-group-role-session.md)
3. [OIDC clients, redirect URIs, scopes a PKCE](oidc-clients-redirect-uris-scopes-pkce.md)
4. [SAML clients, metadata, assertions a bindings](saml-clients-metadata-assertions-bindings.md)
5. [Tokens, claims, protocol mappers a client scopes](tokens-claims-protocol-mappers-client-scopes.md)
6. [Public, confidential a bearer-only client model](public-confidential-and-bearer-only-clients.md)
7. [Service accounts a machine-to-machine authentication](service-accounts-and-machine-to-machine-authentication.md)
8. [Authentication flows, executions a required actions](authentication-flows-executions-and-required-actions.md)
9. [MFA, WebAuthn, passkeys a step-up authentication](mfa-webauthn-passkeys-step-up-authentication.md)
10. [Password policies, brute-force protection a account recovery](password-policies-brute-force-protection-account-recovery.md)
11. [Identity brokering](identity-brokering.md)
12. [LDAP a Active Directory federation](ldap-active-directory-federation.md)

Aktuálny authoritative stav sekcie je **12/30 · In progress**. Kapitoly 1–12 teraz pokrývajú Keycloak deployment a core identity model, OIDC/SAML clients, token projection, client a machine capabilities, authentication flows, MFA/passkeys/step-up, password a recovery controls, identity brokering a LDAP/Active Directory federation. Sekcia zatiaľ nie je `Ready for user review`; ďalší blok začína user-storage/cache semantics, Authorization Services, token exchange/delegated access a Admin API automation.

## Plánované pokračovanie

13. User storage, synchronization a cache semantics  
14. Authorization Services, resources, scopes, policies a permissions  
15. Token exchange, impersonation a delegated access  
16. Admin Console, Admin REST API a automation  
17. Events, audit, metrics a observability  
18. Themes, email templates a localization  
19. Keycloak server configuration, hostname a reverse proxy  
20. TLS, truststores, cookies, headers a production hardening  
21. Database, transactions, connection pools a schema lifecycle  
22. Infinispan caches, clustering a session behavior  
23. Keycloak Operator a Kubernetes deployment  
24. High availability, multi-AZ a multi-cluster trade-offs  
25. Backup, restore, realm import/export a disaster recovery  
26. Upgrades, migration guides a rollback boundaries  
27. Custom providers, SPI a extension lifecycle  
28. Securing APIs, microservices a MCP servers cez Keycloak  
29. Keycloak performance, sizing a load testing  
30. Keycloak troubleshooting

## Connected learning scenario

### `KC-PAY-65` — inherited realm privilege, broad protocol clients a incomplete session revocation

Atlas prevádzkuje Keycloak cluster pre production realm `atlas-payments-prod`. Realm obsahuje OIDC client `payments-admin-web` a SAML client `settlement-partner-sp`. Organizational group `/payments` dostal realm role `settlement-admin`; subgroup `/payments/partners/vega` zdedil parent role, hoci jeho členovia mali mať iba partner read access.

Oba clients mali `Full Scope Allowed`. OIDC client povoľoval redirect wildcard `https://*.atlas.example/*` a nevyžadoval PKCE `S256`. Kompromitovaný preview host preto prijal authorization code a vymenil ho bez verifiera. SAML client povoľoval IdP-initiated login na shared ACS a mapper publikoval rovnakú realm role do assertion. Protokolové správy boli kryptograficky validné, ale client registration a role projection boli príliš široké.

Incident tím použil „Sign out all active sessions“ a videl pokles Keycloak browser sessions. Už vydané access tokens a local application sessions však zostali použiteľné podľa vlastných lifecycles. Útočník pokračoval v settlement API operáciách, kým neboli samostatne zrušené token descendants, application sessions a privilege mappings.

```text
organizational group hierarchy
→ inherited realm role
→ Full Scope Allowed na OIDC a SAML clients
→ broad redirect alebo unsolicited SAML path
→ protocol-correct authentication
→ privileged Keycloak user/client session
→ token alebo assertion s nesprávnym entitlementom
→ local application session
→ incomplete logout/revocation
→ continued business operation
```

Redesign používa client roles namiesto broad realm role, explicitné role scope mappings, exact OIDC redirects, povinné PKCE `S256`, SP-initiated SAML pre privilegovaný client, exact ACS a metadata contract, mapper allowlist, oddelený Keycloak/application/token revocation a second-login/second-client negative tests.

### `KC-PAY-66` — broad token projection, mixed-purpose client a bypassed step-up

Atlas použil client `settlement-ops` súčasne pre desktop CLI, browser administration aj Kubernetes batch workload. Client mal zapnuté Standard Flow, Direct Access Grants a Service Accounts, používal shared secret distribuovaný aj v CLI a zostal na `Full Scope Allowed`. Shared default client scope publikoval expanded realm roles, broad internal audience a custom claim `permissions`; dedicated mapper browser clienta zapisoval ten istý claim inou semantics.

Service-account user zdedil composite `settlement-operator`, ktorý zahŕňal reconcile aj export actions. Browser flow obsahoval WebAuthn execution, ale validná Cookie `ALTERNATIVE` uspokojila remembered-SSO path bez fresh step-up. `CONFIGURE_TOTP` bol označený ako default required action, no existujúcim users nebol spätne priradený. Legacy CLI použil Direct Access Grant, takže Browser flow a jeho WebAuthn branch sa nevykonali vôbec.

```text
mixed browser, native a machine responsibility
→ one confidential client a shared credential
→ broad role-scope a claim projection
→ remembered SSO alebo Direct Grant path
→ valid token bez intended fresh authentication
→ role-only API authorization
→ privileged reconciliation alebo export operation
→ secret rotation bez already-issued-token closure
```

Redesign rozdelí browser, native, machine a resource-server responsibilities do samostatných clients. Token projection používa dedicated/default/optional scopes s jedným ownerom claims, explicitný role-scope intersection a service-specific audience. Machine workload používa workload-bound confidential authentication, browser client má versionovaný step-up flow override, Direct Access Grant je zakázaný, existing users dostanú staged required-action assignment a downstream APIs validujú issuer, audience, caller, token type, tenant, resource a action. Recovery uzatvára old credential, stale token, remembered SSO, fresh login, second client, second token a second operation paths.

### `KC-PAY-67` — assurance downgrade, mailbox recovery, unsafe broker link a stale directory privilege

Atlas zaviedol passkeys pre privileged settlement clienta, ale ACR `gold` bol omylom namapovaný na nízku authentication level. Remembered brokered SSO session preto získala `acr=gold` bez fresh WebAuthn challenge. Recovery flow dôveroval verified emailu synchronizovanému z workforce directory; kompromitovaná alebo recyklovaná mailbox adresa mohla dokončiť password reset a pridať nový passkey.

Partner OIDC provider mal `Trust Email`, `FORCE` mappers a unsafe AutoLink. Nový upstream subject s recyklovaným emailom sa spojil so starým local userom. Súčasne Active Directory changed-users sync nezachytil intended nested-group removal a Keycloak cache/local group mapping ponechali privilege. Password alebo credential reset nezrušil offline token ani local application session.

```text
stale alebo low-assurance upstream/directory identity state
→ incorrect ACR/LoA alebo mapper/sync result
→ unsafe local account link alebo credential recovery
→ stale Keycloak group/role/session descendants
→ protocol-valid privileged token
→ settlement export alebo administration operation
```

Redesign viaže passkeys na exact RP/origin, required user verification a correct ACR-to-LoA mapping; credential management a recovery vyžadujú adequate current assurance a complete session/token closure. Broker linking používa stable external issuer+subject a verified existing-account proof namiesto email AutoLinku. LDAP federation používa stable `objectGUID`, explicitný mapper ownership, full/changed sync evidence, cache invalidation, local emergency admin a fresh-login/offboarding tests. Recovery uzatvára old credential, old broker subject, stale group mapping, offline/application sessions a second-login paths.

## Dominantný model sekcie

```text
business identity alebo access intent
→ exact Keycloak deployment, realm a client generation
→ user alebo workload identity source
→ group, role, client-scope a mapper resolution
→ authentication transaction
→ protocol-specific response validation
→ Keycloak authentication, user a client session state
→ token alebo SAML assertion
→ local application session
→ resource authorization
→ events, revocation, recovery a lifecycle closure
→ second-client, second-session a failure-path validation
```

Každá komplexná kapitola musí rozlišovať:

- Keycloak server deployment od realm configuration;
- realm name od realm issuer URL a internal identity;
- client `clientId` od internal client UUID;
- user identity od mutable username alebo emailu;
- organizational group od permission role;
- realm role od client role;
- direct role mapping od inherited alebo composite effective role;
- client scope od OAuth scope a Authorization Services scope;
- authentication session od user session, client session a application session;
- logout od access-token expiry, revocation a downstream session invalidation;
- protocol-valid response od correct client, tenant a resource authorization;
- Admin Console visibility od effective administrative permission;
- configuration existence od loaded runtime generation;
- successful login od accepted business authorization.

## Cieľ zvládnutia aktívneho bloku

### Keycloak architecture a responsibility boundary

- vysvetliť Keycloak ako authorization server, OpenID Provider, SAML IdP a identity-administration platform;
- rozlíšiť frontend, backchannel, administration a management endpoints;
- mapovať database, cache, session, keys, external identity sources a application dependencies;
- vysvetliť hostname a reverse-proxy trust ako issuer a endpoint authority;
- rozlíšiť server, realm, client a application responsibility;
- navrhnúť exact deployment/configuration/session subject;
- diagnostikovať login symptom naprieč proxy, server, realm, protocol a downstream application boundary.

### Realm, client, user, group, role a session

- rozlíšiť realm isolation od organization alebo tenant modelu;
- vysvetliť stable internal IDs, names, renames a import/export consequences;
- odlíšiť users, groups, realm roles, client roles a composite roles;
- vysvetliť group hierarchy a inherited attributes/roles;
- sledovať direct, inherited, composite a scoped effective role;
- rozlíšiť authentication session, user session, client session, offline session, token a local application session;
- navrhnúť joiner/mover/leaver a revocation behavior.

### OIDC clients, redirect URIs, scopes a PKCE

- definovať exact OIDC client-registration generation;
- rozlíšiť redirect URI, web origin, root URL, home URL a admin URL;
- vysvetliť Authorization Code + PKCE v Keycloak client context-e;
- vyžadovať exact alebo minimálne bounded redirect allowlisty;
- rozlíšiť client scopes, protocol mappers, role scope mappings a OAuth requested scope;
- vysvetliť `Full Scope Allowed`, audience a least-privilege token projection;
- overiť second redirect, second browser, replay, wrong client a logout behavior.

### SAML clients, metadata, assertions a bindings

- vysvetliť Keycloak SAML client ako SP registration v IdP;
- viazať client ID na SP entity ID a metadata generation;
- rozlíšiť ACS, Master SAML Processing URL, Redirect a POST binding;
- vysvetliť AuthnRequest, Response, Assertion, RelayState a local session;
- navrhnúť signing, encryption a key rollover contract;
- obmedziť NameID, role a attribute mappers podľa authority;
- diagnostikovať issuer, ACS, binding, signature, audience, time, mapper a logout failures.

### Tokens, claims, protocol mappers a client scopes

- definovať exact token-projection subject vrátane realm, client, session, requested scopes, mapper, role graph a signing-key generation;
- rozlíšiť access token, ID token, refresh token a UserInfo consumer contract;
- odlíšiť OAuth scope string, Keycloak client scope object a Authorization Services scope;
- vysvetliť default, optional a dedicated client scopes a ich blast radius;
- navrhnúť role scope mappings a vypnutie `Full Scope Allowed` bez straty intended role projection;
- používať protocol mappers ako explicitnú assertion authority s jediným ownerom claimu a stabilným JSON type-om;
- vysvetliť `aud`, `azp`, `scope`, realm/client roles a local resource permission;
- overiť stale token, key rotation, wrong audience, wrong client, second token a second operation.

### Public, confidential a bearer-only client model

- viazať client model na runtime architecture a schopnosť chrániť credential, nie na UI label;
- vysvetliť aktuálny `Client authentication` ON/OFF model a historické bearer-only terminology;
- oddeliť browser/native public clients, server-side confidential clients a resource-server responsibility;
- navrhnúť exact enabled-grant a endpoint capability matrix pre každý client;
- zakázať shared mixed-purpose clients, secrets v public binaries a nepotrebné Direct Access Grants;
- porovnať secret, private-key JWT, mTLS a workload-bound authentication;
- overiť redirect, PKCE, client authentication, audience, token storage a wrong-runtime paths;
- vykonať second-instance, old-credential, stolen-token a adjacent-client negative tests.

### Service accounts a machine-to-machine authentication

- definovať exact service-account subject vrátane client internal ID, linked service-account usera, credential, role-scope a workload generation;
- vysvetliť client-credentials grant bez human browser/MFA lifecycle-u;
- preukázať intersection service-account roles a client/client-scope role scope mappings;
- navrhnúť explicitné resource-server client roles a service-specific audience;
- oddeliť credential rotation od already-issued-token descendants;
- porovnať client secret, private-key JWT, mTLS a federovanú workload identity;
- viazať token na caller client, tenant, resource, action a durable operation ID;
- overiť old credential, wrong audience, wrong tenant, stale token, retry a second-operation behavior.

### Authentication flows, executions a required actions

- definovať exact authentication transaction vrátane realm/client flow bindingu, execution graphu, authentication session a existing user session;
- vysvetliť `REQUIRED`, `ALTERNATIVE`, `CONDITIONAL` a `DISABLED` semantics spolu s priority a subflow levelom;
- rozlíšiť fresh login, remembered SSO Cookie path, client-specific step-up a insufficient authentication level;
- vysvetliť, prečo Browser MFA automaticky nechráni Direct Access Grant;
- kopírovať a versionovať flows, používať client overrides a staged promotion;
- rozlíšiť enabled/default/per-user required action a Application-Initiated Action;
- sledovať action-token issue, authoritative user mutation a session/token descendants;
- overiť fresh, remembered, missing-credential, expired-link, replay, second-user a second-client paths.

### MFA, WebAuthn, passkeys a step-up authentication

- rozlíšiť TOTP/HOTP, WebAuthn druhý faktor, passwordless a loginless discoverable passkey;
- definovať exact RP ID, origin, credential, policy, flow, user-session a client subject;
- vysvetliť WebAuthn registration a authentication ceremony vrátane challenge, signature, user presence a user verification;
- navrhnúť passkey mediation, fallback a recovery bez silent assurance downgrade-u;
- rozlíšiť attestation, AAGUID, authenticator class a privacy/usability trade-off;
- mapovať OIDC ACR alebo SAML authentication context na skutočne dosiahnutú Keycloak LoA;
- chrániť add/delete credential operations current step-upom a auditom;
- overiť wrong origin/RP, UV=false, stale SSO, used recovery code, second client a second-login paths.

### Password policies, brute-force protection a account recovery

- definovať password credential ownera, realm policy, hashing generation a LDAP/external boundary;
- vysvetliť composition rules, password history/expiry a migration existujúcich credentials;
- modelovať brute-force failure state, quick-login threshold, temporary/permanent/mixed lockout a DoS consequence;
- používať Attack Detection read-back a controlled unlock namiesto restartu alebo bulk clear-u;
- vysvetliť Reset Credentials flow, action-token issue/delivery/replay a account-enumeration boundary;
- oddeliť password mutation od Keycloak, offline-token a application-session descendants;
- navrhnúť mailbox/helpdesk recovery s adequate identity proofom;
- overiť old password, expired/replayed link, lockout DoS, old token a second-login paths.

### Identity brokering

- definovať exact external IdP alias/configuration, issuer/entity, external subject, local user a federated-link subject;
- vysvetliť OIDC/SAML upstream validation a oddeliť ju od local account correlation;
- navrhnúť First Broker Login create/link/verify flow bez unsafe AutoLinku;
- používať `Trust Email` iba ako explicitnú delegáciu email-verification authority, nie person identity;
- rozlíšiť IMPORT/FORCE/INHERIT mapper sync modes a ich stale/overwrite behavior;
- minimalizovať stored upstream token custody a read-token permission;
- vynútiť Post Login Flow step-up pre insufficient upstream assurance;
- overiť same-email/different-subject, wrong issuer, stale link, unlink/relogin a stored-token paths.

### LDAP a Active Directory federation

- definovať exact provider, directory namespace, secure connection, bind credential, stable UUID, mapper a sync generation;
- rozlíšiť Import Users ON/OFF a local versus transient user-state consequences;
- vysvetliť READ_ONLY, WRITABLE a UNSYNCED field/password ownership;
- používať multiple LDAP URLs ako sequential replica failover, nie identity-provider load balancing;
- modelovať on-demand, full a changed-users sync vrátane missed deletion/group-change risks;
- vysvetliť LDAP mappers, AD `objectGUID`, `sAMAccountName`, UPN, nested groups a account-control semantics;
- oddeliť directory disable/password state, Keycloak cache/session a token descendants;
- overiť first-server-down, wrong UUID, provider failure, removed group, local emergency admin a leaver paths.
