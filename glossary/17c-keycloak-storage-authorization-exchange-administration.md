## Administrative operation subject

Complete identity of a Keycloak administrative change: actor and authentication realm, target deployment and realm, resource internal ID, predecessor representation, request body and operation identity, Admin Event, successor read-back and dependent runtime outcome.

## Admin Event

Keycloak audit record for an administrative operation. It can identify actor, realm, resource path, operation type, time and optionally a representation, but it does not by itself prove downstream session, token or business-state convergence.

## Admin permissions client

Keycloak client created or used by Fine-Grained Admin Permissions to hold authorization resources, policies and permissions for delegated administration. Its authorization graph is separate from broad built-in realm-management roles.

## Authorization permission

Keycloak Authorization Services object that binds resources or authorization scopes to one or more policies. A policy without a permission is reusable logic but is not applied to a protected resource request.

## Authorization resource

Object, resource type or protected URI registered in a Keycloak resource server. Its internal resource ID must remain correlated with the real application object; URI or display name alone is not durable business identity.

## Authorization scope

Action or bounded capability over an Authorization Services resource, such as `view`, `export` or `approve`. It is distinct from an OAuth scope string and from a Keycloak client-scope configuration object.

## Cached user model

In-memory Keycloak representation of a user copied from local or external storage. It can include provider-specific metadata through `OnUserCache`, but it is a snapshot and not an authoritative audit record.

## Client internal UUID

Server-generated Keycloak identifier used by many Admin REST endpoints for a client. It is different from the protocol-facing `clientId` and changes when a client is deleted and recreated.

## Delegated administrator

Administrator or automation principal whose allowed operations are limited to specific resources or actions through scoped realm-management roles and Fine-Grained Admin Permissions rather than broad realm-wide administration.

## Exchange descendant

Access or refresh token issued from a token-exchange request. It has its own identifier, audience, lifetime and revocation behavior; invalidating the predecessor access token does not automatically prove immediate invalidation of every access-token descendant.

## Fine-Grained Admin Permissions

Keycloak authorization model for delegating administration of supported users, groups, clients, roles, organizations and related resources through explicit policies and permissions. Broad admin roles can bypass this graph and therefore must not be assigned by default.

## Imported user validation

User Storage SPI callback that validates or proxies an imported local user against its external source when the local record is loaded. A cache hit may avoid that load, so validation latency depends on cache and invalidation behavior.

## Import synchronization

User Storage SPI capability for full or changed-since reconciliation of external users into Keycloak local storage. A successful synchronization count proves processing of the configured population, not correctness of filters, deletion semantics or active session descendants.

## OnUserCache

User Storage SPI callback invoked when Keycloak caches a user model. Providers can add custom values to the cached representation, but must define authoritative invalidation or a bounded cache lifetime for security-relevant data.

## Partial import

Keycloak Admin REST operation that imports selected realm resources according to conflict strategy. It may create, overwrite, skip or fail different items independently and must not be treated as one all-or-nothing transaction.

## Permission ticket

Short-lived UMA authorization-request artifact representing a requested resource and scopes. A client exchanges the ticket at the token endpoint; the ticket itself is not a granted permission.

## Policy Decision Point

Component that evaluates Keycloak Authorization Services policies and permissions for a subject, client, resource, scopes and context. Its decision becomes effective only when a Policy Enforcement Point applies it to the real request.

## Policy Enforcement Point

Application, gateway or policy-enforcer component that maps a real request to a Keycloak resource and scopes, obtains or validates an authorization decision, fails closed when required and blocks the business handler after denial.

## Protection API Token

Access token used by a Keycloak resource server to call the Authorization Services Protection API, commonly carrying `uma_protection`. It is a privileged machine credential and must not be exposed to browser clients.

## Requesting Party Token

Access token issued through UMA with an `authorization.permissions` claim describing granted resource IDs and scopes. It is a snapshot of a policy decision and still requires normal issuer, audience, expiry and resource-binding validation.

## Standard Token Exchange V2

Supported Keycloak token-exchange implementation for exchanging an internal Keycloak access token for another internal token in the same realm. The requester client must have the capability enabled and be authorized for the subject token and target audience.

## Legacy Token Exchange V1

Deprecated preview Keycloak exchange implementation covering historical external-token and impersonation scenarios. It has different permission and parameter semantics and requires an explicit migration plan rather than silent coexistence with Standard V2.

## Stale administrative plan

Previously approved desired-state diff whose target predecessor generation has changed before mutation. Safe automation refuses the plan instead of overwriting an intervening administrative change.

## User Storage SPI

Keycloak extension contract for integrating external identity and credential sources through capability interfaces such as lookup, query, registration, credential validation, imported-user validation, synchronization and caching.
