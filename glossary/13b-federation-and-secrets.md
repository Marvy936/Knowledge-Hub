# Federation and secrets glossary entries

## Access token

Credential vydaný authorization serverom a určený pre resource server na vykonanie obmedzených API operácií. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Assertion Consumer Service — ACS

Service Provider endpoint prijímajúci a validujúci SAML Response pri browser SSO. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Audience — OAuth/OIDC/SAML

Identifier zamýšľaného konzumenta tokenu alebo assertion; musí byť validovaný, aby sa artifact nedal použiť voči inému clientovi alebo resource serveru. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md), [OpenID Connect](docs/13-security-and-identity/openid-connect.md) a [SAML](docs/13-security-and-identity/saml.md).

## Authorization code

Krátkodobý jednorazový OAuth grant, ktorý client vymieňa na token endpoint-e za access token. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Authorization server

OAuth server, ktorý vyhodnocuje grant, autentizuje relevantných principals a vydáva access a refresh tokens. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Authorization Server Metadata

Štandardizovaný dokument publikujúci issuer, endpoints a supported OAuth capabilities pre bezpečnejšiu client konfiguráciu. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Auto unseal — Vault

Vault model, v ktorom Cloud KMS, HSM alebo iný trusted seal mechanism dešifruje root-key material pri štarte bez manuálneho zadávania Shamir shares. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Back-channel logout

OIDC logout model, pri ktorom OpenID Provider posiela signed logout token priamo backendu Relying Party. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Bearer token

Token použiteľný každým držiteľom bez ďalšieho proof-of-possession; jeho leakage predstavuje credential compromise počas platnosti. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Client — OAuth

Aplikácia požadujúca token a používajúca ho voči resource serveru. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Client Credentials grant

OAuth machine-to-machine grant, pri ktorom client získava token vo vlastnom identity kontexte bez používateľskej delegation. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Client authentication

Mechanizmus, ktorým confidential OAuth client preukazuje svoju identitu token endpointu, napríklad secretom, private-key JWT alebo mTLS. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Code challenge

PKCE hodnota odvodená z code verifiera a odoslaná v authorization requeste. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Code verifier

Náhodná PKCE hodnota uchovaná clientom a predložená pri authorization-code exchange. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Confused deputy

Situácia, v ktorej privileged komponent vykoná operáciu v prospech nesprávneho alebo neautorizovaného actora pre chýbajúci audience, subject alebo delegation binding. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Consent — OAuth

User-facing authorization interaction zobrazujúca clienta a požadovaný access; nenahrádza server-side policy. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Device Authorization flow

OAuth flow pre zariadenia s obmedzeným inputom, pri ktorom používateľ autorizuje device code na inom zariadení. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Dynamic secret

Credential generovaný on demand pre konkrétnu identity alebo role s krátkym lease a revocation lifecycle-om. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Encryption barrier — Vault

Vault cryptographic boundary chrániaca storage data; sealed Vault nemá v memory kľúče potrebné na ich decryption. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## End-User — OIDC

Používateľ, ktorého authentication event OpenID Provider potvrdzuje Relying Party. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Entity ID — SAML

Stabilný identifier SAML Identity Providera alebo Service Providera používaný v metadata a issuer/audience trust contracte. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Front-channel logout

OIDC logout model využívajúci browser na komunikáciu s logout endpoints jednotlivých clients. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## ID Token

Signed OIDC JWT určený Relying Party, ktorý obsahuje issuer, subject, audience a authentication context claims. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Identity Provider — SAML

SAML entita autentizujúca principal-a a vydávajúca signed assertions. Pozri [SAML](docs/13-security-and-identity/saml.md).

## InResponseTo — SAML

Identifier viažuci SAML Response alebo SubjectConfirmationData na konkrétny AuthnRequest. Pozri [SAML](docs/13-security-and-identity/saml.md).

## JWKS

JSON Web Key Set publikujúci public cryptographic keys používané napríklad na validáciu OIDC ID Token signatures. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Lease — secrets management

Časovo obmedzený contract pre vydaný secret s TTL, renewal a revocation semantics. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## NameID — SAML

SAML subject identifier s definovaným formatom, napríklad persistent alebo transient. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Nonce — OIDC

Jednorazová hodnota viažuca ID Token na konkrétny authentication request a pomáhajúca proti replay a injection. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## OAuth 2.0

Authorization framework na delegovaný alebo workload access k protected APIs pomocou obmedzených tokens. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## OIDC discovery

Štandardizované získanie OpenID Provider metadata vrátane issuer, endpoints a JWKS URI. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Opaque token

Access token bez self-contained claims, ktorého stav a metadata resource server zisťuje typicky cez introspection. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## OpenID Connect

Federated authentication a identity layer nad OAuth 2.0 používajúca ID Tokens a štandardné claims. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## OpenID Provider

OIDC authorization server, ktorý autentizuje End-Usera a vydáva ID Tokens. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Pairwise subject

OIDC subject identifier odlišný medzi sectors alebo clients na zníženie cross-application correlation. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## PKCE

Proof Key for Code Exchange, ktorý viaže authorization-code exchange na client instance cez code challenge a verifier. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Public subject

OIDC subject identifier spoločný pre clients v príslušnom issuer scope-e. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Recovery keys — Vault

Quorum material používaný pri vybraných privileged Vault operations v auto-unseal modeli; nenahrádza stratený auto-unseal key. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Redirect URI

Pre-registered client endpoint, na ktorý authorization server vracia browser authorization response. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Refresh token

Dlhšie žijúci OAuth credential používaný na získanie nových access tokens bez opakovanej user interaction. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Refresh-token rotation

Model, v ktorom každé použitie refresh tokenu vydá nový token a umožňuje detegovať reuse staršej hodnoty. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## RelayState — SAML

Application state prenášaný spolu so SAML protocol message, ktorý potrebuje integrity a open-redirect ochranu. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Relying Party

OIDC client, ktorý dôveruje validovanému ID Token-u od OpenID Providera a vytvára vlastnú application session. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Resource owner

OAuth entita schopná autorizovať access ku protected resource. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Resource server

API alebo služba validujúca access token a presadzujúca resource-level authorization. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## SAML

XML-based federation framework na prenos authentication a attribute assertions medzi Identity Providerom a Service Providerom. Pozri [SAML](docs/13-security-and-identity/saml.md).

## SAML assertion

Signed alebo encrypted XML security artifact obsahujúci statements o subjecte, authentication a attributes. Pozri [SAML](docs/13-security-and-identity/saml.md).

## SAML binding

Definícia transportu SAML messages, napríklad HTTP Redirect, HTTP POST alebo Artifact binding. Pozri [SAML](docs/13-security-and-identity/saml.md).

## SAML metadata

XML trust a configuration dokument obsahujúci entity IDs, endpoints, bindings a signing/encryption certificates. Pozri [SAML](docs/13-security-and-identity/saml.md).

## SAML profile

Kombinácia assertions, protocols a bindings pre konkrétny use case, napríklad Web Browser SSO. Pozri [SAML](docs/13-security-and-identity/saml.md).

## SAML protocol

Request/response messages definované SAML, napríklad AuthnRequest, Response alebo LogoutRequest. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Secret

Citlivý credential alebo cryptographic material, ktorého získanie umožňuje access, impersonation, decryption, signing alebo privileged operation. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secret classification

Dokumentovaný contract secretu zahŕňajúci ownera, účel, consumers, lifetime, rotation, revocation, delivery a compromise impact. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secret lifecycle

Proces creation, storage, authorization, distribution, use, rotation, revocation a destruction secretu. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secret revocation

Technické zneplatnenie credentialu v authoritative cieľovom systéme. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secret rotation

Nahradenie credentialu alebo keyu novou hodnotou s bezpečným cutover a následnou revocation starej hodnoty. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secret zero

Prvotný trust anchor alebo credential potrebný na získanie ďalších secrets. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Secrets engine — Vault

Vault component mountnutý na path, ktorý ukladá, generuje alebo cryptographically spracúva citlivé dáta. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Sender-constrained token

Access token viazaný na client key alebo proof mechanizmus, napríklad mTLS alebo DPoP. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Service Provider — SAML

Aplikácia alebo služba dôverujúca validovaným assertions od SAML Identity Providera. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Shamir shares — Vault

Threshold shares používané na rekonštrukciu Vault unseal materialu v manuálnom Shamir seal modeli. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Single Logout — SAML

SAML protocol na koordináciu logoutu medzi IdP a SP sessions, ktorý môže zlyhať čiastočne a nepredstavuje automatickú globálnu revocation. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Static secret

Dlhšie žijúca a opakovane používaná secret hodnota, ktorá potrebuje explicitnú rotation a revocation. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Subject identifier — OIDC

Hodnota `sub`, ktorá spolu s issuerom stabilne identifikuje End-Usera v OIDC trust doméne. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## SubjectConfirmation — SAML

SAML element určujúci spôsob, recipienta, request binding a časové podmienky, za ktorých možno assertion použiť. Pozri [SAML](docs/13-security-and-identity/saml.md).

## Token endpoint

OAuth endpoint, ktorý vymieňa authorization grant alebo refresh token za access token. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Token exchange

OAuth extension na výmenu subject alebo actor tokenu za nový token s vhodným audience, scope a delegation contextom. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Token introspection

OAuth endpoint umožňujúci resource serveru zistiť active stav a metadata opaque alebo centrally validated tokenu. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Token revocation

OAuth mechanizmus na zneplatnenie tokenu alebo grant lifecycle-u. Pozri [OAuth 2.0](docs/13-security-and-identity/oauth-2.md).

## Transit secrets engine — Vault

Vault engine poskytujúci encryption, decryption, signing alebo HMAC operations bez vydania underlying key materialu clientovi. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Unseal — Vault

Proces sprístupnenia root-key materialu potrebného na odomknutie Vault encryption barrieru. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## UserInfo endpoint

OIDC protected endpoint vracajúci štandardizované claims o subjecte po predložení access tokenu. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md).

## Vault audit device

Vault component zaznamenávajúci API requests a responses do file, syslog alebo socket destination a ovplyvňujúci request availability pri úplnom write failure. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Vault auth method

Mechanizmus, ktorý autentizuje human alebo workload identity vo Vault a vydá client token s príslušnými policies. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Vault policy

Path-based authorization pravidlá definujúce capabilities dostupné Vault tokenu alebo identity. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Vault token

Bearer credential vydaný Vaultom s policies, TTL, renewal a revocation lifecycle-om. Pozri [Secrets management](docs/13-security-and-identity/secrets-management.md).

## Workload identity federation

Trust model, v ktorom workload používa krátkodobú platform identity assertion na získanie accessu bez statického external credentialu. Pozri [OpenID Connect](docs/13-security-and-identity/openid-connect.md) a [Secrets management](docs/13-security-and-identity/secrets-management.md).

## XML Signature Wrapping

Útok využívajúci rozdiel medzi XML elementom overeným signature knižnicou a elementom spracovaným application logic. Pozri [SAML](docs/13-security-and-identity/saml.md).
