# Keycloak-secured AI API runtime evidence

Status: `Pending`

Source implementation exists for the local Keycloak realm, browser PKCE flow helpers, service-account token helper and strict JWT authorization gateway. No live Keycloak 26.7.0 container, imported realm, JWKS fetch, Authorization Code exchange, Client Credentials exchange or protected HTTP request has been recorded as runtime evidence yet.

## Required closeout evidence

A future runtime gate must record one exact Git revision and prove at least:

1. `quay.io/keycloak/keycloak:26.7.0` starts on loopback with the imported `knowledge-hub` realm.
2. OIDC discovery issuer equals the configured issuer and JWKS is readable from the exact realm.
3. `knowledge-hub-web` uses Authorization Code with PKCE `S256`; implicit and password/direct grants stay disabled.
4. A human access token contains only the accepted API audience, `token_use=access` and the expected `knowledge-hub-api` client role.
5. `knowledge-hub-automation` obtains a Client Credentials access token without exposing its client secret or token in logs.
6. Browser token can access `rag.read` but is refused from automation-only agent routes.
7. Automation token is authorized only for roles actually present in its token.
8. Wrong issuer, wrong audience, additional audience, wrong signature/key, expired/not-yet-valid token, missing role, wrong `azp` and ID-token marker are refused with the expected 401/403 boundary.
9. Token/session runtime files are removed and container/volume cleanup is read back.

Until this evidence exists, `Implemented` must not be promoted to `Runtime verified`.
