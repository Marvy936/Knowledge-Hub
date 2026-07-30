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

Aktuálny authoritative stav sekcie je **4/30 · In progress**.

## Plánované pokračovanie

5. Tokens, claims, protocol mappers a client scopes  
6. Public, confidential a bearer-only client model  
7. Service accounts a machine-to-machine authentication  
8. Authentication flows, executions a required actions  
9. MFA, WebAuthn, passkeys a step-up authentication  
10. Password policies, brute-force protection a account recovery  
11. Identity brokering  
12. LDAP a Active Directory federation  
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
