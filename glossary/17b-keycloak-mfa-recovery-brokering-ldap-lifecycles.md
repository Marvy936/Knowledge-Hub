## Authentication level

Numeric assurance level achieved by a Keycloak authentication flow and stored in the user session. OIDC ACR values or SAML authentication contexts may map to this level, but the resulting claim must reflect the level actually achieved, not merely requested.

## Brokered identity context

Temporary Keycloak representation of identity data received from an external OIDC, SAML or social identity provider. Identity-provider mappers can transform this context before First Broker Login creates or links a local user.

## Changed-users sync

LDAP synchronization mode that imports or updates entries changed since the provider's previous synchronization boundary. It is cheaper than a full sync but may miss deletions, group-membership changes or directory-specific modifications that do not advance the expected change attribute.

## Discoverable credential

WebAuthn credential that an authenticator can find for a relying party without the server first supplying a credential identifier. It enables username-less or loginless passkey flows when the authenticator returns the user handle associated with the credential.

## Federated identity link

Durable Keycloak relation between one local realm user and an external identity-provider subject. A secure link is identified by the local user ID, provider identity and stable external subject; email or username alone is insufficient.

## First Broker Login

Authentication flow executed when a valid external identity has no existing federated link in the realm. It controls profile review, local user creation, existing-account discovery, account-link verification and final link creation.

## Full LDAP sync

Synchronization operation that enumerates the configured LDAP population and creates or updates corresponding imported Keycloak users. A successful job proves processing of the configured search result, not correctness of the search base, filter, mappers or downstream sessions.

## Identity-provider sync mode

Policy controlling when a Keycloak identity-provider mapper writes upstream profile data to the local user. `IMPORT` applies the mapping during first creation or linking, `FORCE` reapplies it at broker logins, `INHERIT` follows the provider-level setting and `LEGACY` preserves older behavior.

## Keycloak LDAP edit mode

Ownership policy for federated user attributes and passwords. `READ_ONLY` rejects supported writes, `WRITABLE` propagates them to LDAP and `UNSYNCED` stores supported changes locally, deliberately allowing Keycloak and LDAP state to diverge.

## Keycloak recovery code

One-time backup authentication secret generated and stored by Keycloak for use when the primary second factor is unavailable. It is a phishing-prone bearer credential; consumption, regeneration, replay denial and descendant-session handling require explicit validation.

## LDAP imported user

Local Keycloak user representation linked to a stable LDAP entry identifier when `Import Users` is enabled. Profile and Keycloak-specific metadata may be stored locally, but LDAP passwords are never imported and authentication still validates against the directory unless a deliberate local credential path exists.

## Passkey mediation

Browser interaction policy controlling how discoverable passkeys are offered on the Keycloak login page. Conditional mediation uses autofill-style suggestions, optional mediation may open an account chooser automatically, and none requires an explicit user action.

## Post Login Flow

Authentication flow executed after successful authentication at an external identity provider and local account resolution. It can enforce local MFA, required actions or assurance checks before Keycloak creates the final local client session.

## Relying Party ID

WebAuthn domain identifier to which a credential and assertion are scoped. Keycloak's public hostname, browser origin and configured RP ID must form a consistent trust boundary; a valid signature for a different RP ID must be rejected.

## Sequential LDAP failover

Behavior of a Keycloak LDAP provider configured with multiple space-separated connection URLs. The underlying provider tries URLs from left to right when creating a connection; it is failover, not load balancing, and all endpoints must be replicas preserving the same entry UUIDs.

## Step-up authentication

Authentication transition that raises an existing Keycloak user session from its current assurance level to a higher level required by a client or protected operation. Acceptance requires the intended additional authenticator, a correct resulting ACR or authentication context, freshness evidence and downstream enforcement.

## Trust Email

Identity-provider setting delegating email-verification authority to the upstream provider. It may mark brokered email as verified, but it does not make email a stable person identifier and must not by itself authorize account linking, tenant membership or privileged recovery.

## WebAuthn user verification

Authenticator evidence that the person operating a WebAuthn credential completed a local verification gesture such as a PIN or biometric check. Passwordless or high-assurance policy commonly requires this flag; user presence alone does not provide the same assurance.
