# Temporary Section 17 block 05–08 gate diagnostic

> Branch-only diagnostic. It does not activate README or ledger state and must be removed before merge.

| Chapter | Words | Code fences | Missing requirements | Result |
|---|---:|---:|---|---|
| `keycloak-architecture-and-responsibility-boundary.md` | 2674 | 24 | tokens: deploymentGeneration | **FAIL** |
| `realm-client-user-group-role-session.md` | 2548 | 32 | — | **PASS** |
| `oidc-clients-redirect-uris-scopes-pkce.md` | 2954 | 32 | — | **PASS** |
| `saml-clients-metadata-assertions-bindings.md` | 3428 | 28 | — | **PASS** |
| `tokens-claims-protocol-mappers-client-scopes.md` | 1880 | 6 | — | **PASS** |
| `public-confidential-and-bearer-only-clients.md` | 1793 | 12 | — | **PASS** |
| `service-accounts-and-machine-to-machine-authentication.md` | 2257 | 30 | — | **PASS** |
| `authentication-flows-executions-and-required-actions.md` | 2668 | 40 | — | **PASS** |

## Verdict

Gate is **not ready**. Failures: 1.

- keycloak-architecture-and-responsibility-boundary.md: tokens: deploymentGeneration
