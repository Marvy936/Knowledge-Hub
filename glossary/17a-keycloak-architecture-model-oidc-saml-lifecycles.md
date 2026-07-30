## Administration endpoint

Keycloak endpoint group pre Admin Console a Admin REST API, cez ktoré sa mení realm configuration. Potrebuje samostatnú network a authorization boundary; skrytie UI alebo odlišný hostname nenahrádza server-side admin permission.

## Authentication session

Dočasný Keycloak state rozpracovaného login alebo action transaction-u pred vznikom user session. Viaže browser, client, flow, tab a protocol parameters a má odlišný lifecycle od už autentizovanej user session.

## Backchannel endpoint

Server-to-server endpoint Keycloaku používaný napríklad pre token exchange, introspection, UserInfo, JWKS alebo logout. Môže mať inú routovaciu cestu než browser frontend, ale musí zostať viazaný na trusted realm issuer a client configuration.

## Client internal UUID

Keycloak interný identifier client objectu používaný v administračných API paths a relations. Nie je totožný s protocolovým `clientId`; delete/recreate môže zachovať `clientId`, ale vytvoriť nový internal object.

## Client role

Role definovaná v namespace konkrétneho Keycloak clienta. Je vhodná pre application-specific permissions a znižuje riziko, že unrelated clients dostanú realm-wide entitlement.

## Client session

Väzba Keycloak user session na konkrétny client, jeho protocol state a logout/session descendants. Jeden user session môže obsahovať viac client sessions.

## Client scope

Realm-level reusable Keycloak configuration pre protocol mappers a role scope mappings, ktorú možno linkovať k clients ako default alebo optional. Nie je totožná s OAuth scope ani Authorization Services scope.

## Composite role

Keycloak role obsahujúca ďalšie realm alebo client roles. User s composite role získava transitive effective roles, preto access review musí počítať celý expansion graph.

## Dedicated client scope

Client-specific scope a mapper configuration vytvorená pre jeden Keycloak client. Oddeľuje jeho claims a role projection od reusable realm-level client scopes.

## Effective role graph

Transitive výsledok direct user roles, group a parent-group roles, composite roles a default mappings pred client-scope obmedzením. Screenshot direct mappings nepreukazuje celý effective access.

## Entitlement generation

Versionovaný stav group, role, composite a scope mappings, z ktorého vznikol token alebo assertion. Umožňuje odlíšiť current membership od privilege snapshotu v staršej session.

## Frontend endpoint

Browser-visible Keycloak endpoint group pre login, redirects, account actions, email action links a discovery. Jeho public URL a hostname sú súčasťou issuer a credential-delivery trust contractu.

## Full Scope Allowed

Keycloak client setting, pri ktorom je role scope clienta broad a môže sprístupniť všetky effective user roles podľa mapper configuration. Pre least privilege sa vypína a nahrádza explicitnými role scope mappings.

## Group inheritance

Keycloak behavior, pri ktorom člen child groupy dedí attributes a role mappings parent groups. Organizačná hierarchy preto môže neúmyselne vytvoriť transitive application privilege.

## Hostname authority

Explicitná public URL configuration, z ktorej Keycloak odvodzuje issuer, discovery endpoints, redirects a action links. Dynamické prijatie untrusted Host alebo forwarded headeru môže zmeniť identity-provider trust boundary.

## Identity-platform acceptance verdict

End-to-end rozhodnutie, že exact Keycloak deployment, realm, client, identity source, session, protocol artifact a downstream authorization vytvárajú intended outcome a odmietajú wrong realm, client, redirect, role a stale-session paths.

## Keycloak deployment subject

Exact operational identity Keycloak servera vrátane version/image, feature profile, node, server configuration, public/admin URLs, providers, realm a relevantnej loaded generation. Všeobecný názov „production Keycloak“ nie je dostatočný incident subject.

## Keycloak SAML client generation

Versionovaný effective SP registration v Keycloak realm-e vrátane entity ID, ACS/SLO endpoints, bindings, keys, NameID, mappers, scopes a session settings.

## Keycloak user identity

Realm-scoped user record identifikovaný internal ID-om a prípadnou väzbou na external authority. Username a email sú mutable attributes, nie bezpečný universal identity key.

## Management interface

Oddelený Keycloak interface pre health a metrics, typicky na management porte. Nemá byť automaticky publikovaný rovnakým internetovým proxy pathom ako OIDC, SAML a Admin API.

## Master SAML Processing URL

Keycloak SAML client setting určujúci spoločný processing endpoint pre SAML messages podľa client configuration. Musí byť zosúladený s exact ACS/SLO a external proxy URL contractom.

## Metadata generation

Immutable alebo reprodukovateľná verzia SAML metadata s entity ID, endpoints, bindings a keys. Import metadata bez zachovania source/hash a effective diffu nie je auditovateľný trust change.

## OIDC client generation

Versionovaný effective Keycloak OIDC registration vrátane realm issueru, client UUID/ID, authentication method, grants, redirects, web origins, PKCE, scopes, mappers, roles a logout/session settings.

## OIDC client acceptance matrix

Sada positive a negative tests pre exact redirect, PKCE, role/scope/audience projection, wrong client/realm/verifier a logout/revocation behavior. Successful login samotný nie je client acceptance.

## Offline session

Dlhodobejší Keycloak session state pre offline access a refresh descendants. Má vlastný timeout a revocation lifecycle a nemusí zaniknúť s browser SSO session.

## Optional client scope

Client scope, ktorý sa nepoužije automaticky a môže sa aktivovať requested `scope` hodnotou podľa Keycloak client linku, consentu a policy. Requested name sám osebe nezaručuje udelenie claims.

## PKCE enforcement

Server-side požiadavka, aby authorization request niesol code challenge a token exchange správny verifier, typicky metódou `S256`. Optional PKCE ponecháva downgrade path pre request bez challenge.

## Protocol mapper

Keycloak komponent, ktorý prekladá user, group, role, session alebo custom data do OIDC claims alebo SAML attributes. Je authority boundary, pretože rozhoduje, ktoré interné údaje sa stanú externým assertionom.

## Proxy-header trust

Kontrakt, podľa ktorého Keycloak prijíma `Forwarded` alebo `X-Forwarded-*` údaje iba od trusted reverse proxy, ktorá client-supplied hodnoty prepíše. Chyba môže ovplyvniť issuer, redirects, origin a audit client IP.

## Realm issuer

Externá OIDC trust identity konkrétneho Keycloak realm-u, typicky URL obsahujúca realm path. Dva realms s rovnakými keys alebo client IDs zostávajú odlišnými issuer namespaces.

## Realm role

Role definovaná v realm-wide namespace a potenciálne použiteľná viacerými clients. Application-specific privilege ako broad realm role zvyšuje riziko neúmyselnej projection.

## Role scope mapping

Keycloak mapping určujúci, ktoré effective user roles smie konkrétny client alebo client scope dostať do token/assertion projection. Je samostatný od samotného user-role assignmentu.

## SAML client acceptance matrix

Positive a negative tests pre SP entity ID, ACS, binding, signature, audience, destination, recipient, replay, mapper a logout behavior konkrétnej Keycloak SAML client generation.

## SAML local session

Application session vytvorená Service Providerom po prijatí assertion. Je mimo Keycloak session store-u a môže prežiť IdP sign-out alebo SLO failure, pokiaľ ju SP samostatne nezruší.

## Session descendant graph

Väzby od authentication/user/client session cez refresh, offline a access-token artifacts po downstream application sessions a business workflows. Incident revocation musí určiť, ktoré descendants sa rušia samostatne.

## User session

Realm-level Keycloak state autentizovaného usera, ku ktorému sa pripájajú client sessions. Nie je totožný s browser cookie, access tokenom ani downstream application session.

## Valid redirect URI

Server-side allowlist destination, na ktorú Keycloak smie doručiť OIDC authorization response. Broad wildcard rozširuje credential-delivery trust na každý matching host a path.

## Web origin

Browser origin povolený pre CORS komunikáciu s Keycloak endpoints. Nie je totožný s redirect URI; oba controls chránia odlišné browser paths.
