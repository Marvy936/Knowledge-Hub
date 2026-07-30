# SAML clients, metadata, assertions a bindings

Keycloak SAML client je registrácia Service Providera v konkrétnom realm-e, kde Keycloak vystupuje ako Identity Provider. Client určuje SP entity ID, Assertion Consumer Service endpoints, browser bindings, signing a encryption požiadavky, NameID format, attribute a role mappers, logout semantics a session behavior. SAML Core vysvetľuje message model; Keycloak client configuration rozhoduje, ktorú konkrétnu application a metadata generation server obsluhuje.

Platná XML signature sama osebe nepreukazuje správny client. Keycloak môže korektne podpísať Response pre clienta, ktorého ACS je príliš široký, ktorého mapper publikuje neautorizovanú role alebo ktorého IdP-initiated path nemá request binding. Downstream SP môže správne overiť certificate a zároveň prijať assertion pre nesprávny entity ID, destination alebo local account. SAML client acceptance preto musí spájať metadata, AuthnRequest, binding, signed element, assertion semantics, Keycloak client session a local application session.

## 1. Dominantný metadata-to-session model

```text
application ownership a federation requirement
→ exact Keycloak realm a SAML client generation
→ SP entity ID a trusted metadata contract
→ ACS/SLO endpoints a supported bindings
→ signing, encryption a key generations
→ SP AuthnRequest alebo explicitne povolený IdP-initiated intent
→ Keycloak authentication a user/client session
→ attributes, roles a NameID resolution
→ signed/encrypted Response alebo Assertion
→ browser Redirect/POST delivery
→ SP structural, cryptographic a semantic validation
→ local account a application session
→ resource authorization
→ logout, key rollover, revocation a second-login validation
```

Každý krok je samostatná boundary. Metadata import môže byť správny, ale neskorší manual edit rozšíri ACS. Assertion môže byť podpísaná, ale mapper vloží role z nesprávnej authority. SLO request môže prejsť, ale local API token zostane aktívny.

## 2. Exact SAML client subject

Pri incidente zachovaj:

```text
Keycloak deployment a realm identity
+ SAML client internal UUID
+ Client ID / SP entity ID
+ client enabled state
+ metadata import/source generation
+ Master SAML Processing URL
+ ACS a SLO endpoint inventory
+ POST/Redirect binding configuration
+ client-signature requirement
+ Keycloak signing/encryption key generation
+ NameID format a mapper generation
+ role/attribute mapper generation
+ AuthnRequest ID a RelayState
+ Response/Assertion IDs a SessionIndex
+ Keycloak user/client session
+ downstream SP release a local session
```

Rovnaký certificate alebo ACS hostname neznamená rovnaký client. Client ID je protocol identity. Delete a recreate s rovnakým Client ID môže zmeniť internal UUID, keys, mappers a session state.

## 3. Client ID ako SP entity ID

Pri Keycloak SAML clientovi Client ID typicky reprezentuje SP entity ID a musí zodpovedať issuer-u v AuthnRequest-e. Entity ID je logical federation identity, nie nutne resolvable URL. Môže byť URI alebo URN, pokiaľ je stabilný a jednoznačný.

```text
SP metadata entityID
↔ Keycloak SAML Client ID
↔ AuthnRequest Issuer
↔ AudienceRestriction expected value
```

Ak staging a production používajú rovnaký entity ID, Keycloak ich nevie bezpečne odlíšiť podľa protocol identity. Odlišný ACS path nemusí stačiť. Environmenty a tenants majú mať samostatný client/entity contract alebo explicitný multi-tenant routing model s transaction bindingom.

Rename Client ID mení federation identity. SP metadata, Keycloak client, audience validation a trust configuration sa musia migrovať koordinovane.

## 4. Metadata ako versionovaný trust a interoperability contract

SAML metadata opisujú entity, endpoints, bindings, keys, NameID formats a ďalšie capabilities. Import metadata do Keycloaku môže zrýchliť onboarding, ale import nie je trvalá reconciliation automatika. Po importe môže administrator settings zmeniť. Upstream metadata rollover sa nemusí automaticky prejaviť bez definovaného refresh alebo change workflowu.

Metadata lifecycle:

```text
approved SP owner a entity
→ trusted metadata source alebo reviewed artifact
→ schema a signature/provenance validation
→ Keycloak client creation/update
→ effective settings diff
→ SP a IdP key/endpoint overlap
→ federation canary
→ old metadata/key retirement
```

Metadata URL zadaná neovereným userom nesmie automaticky rozšíriť trust. Import môže obsahovať endpoints na attacker-controlled host alebo weak algorithms. Platform má zachovať source revision/hash a reviewed effective client configuration.

## 5. ACS a Master SAML Processing URL

Assertion Consumer Service je SP endpoint, ktorý prijíma SAML Response. Keycloak môže používať Master SAML Processing URL ako spoločný target pre SSO, SLO alebo ďalšie protocol messages podľa configuration a request context-u. Presné správanie závisí od client settings a AuthnRequest-u.

ACS je credential-delivery boundary podobne ako OIDC redirect URI. Broad alebo shared ACS musí mať vlastný tenant/client routing a transaction validation. Samotný RelayState parameter nesmie byť jedinou autoritou, ktorá vyberie privileged tenant alebo local account.

```text
AuthnRequest Issuer + Request ID
→ registered client
→ requested ACS porovnaná s allowed endpoints
→ Response Destination
→ SubjectConfirmation Recipient
→ SP exact endpoint validation
```

Ak reverse proxy mení external scheme/host/path, Keycloak aj SP musia používať authoritative external URLs. Vypnutie Destination alebo Recipient validation kvôli proxy mismatchu odstraňuje security boundary.

## 6. HTTP Redirect a HTTP POST bindings

Binding určuje transport SAML protocol message-u. HTTP Redirect typicky prenáša deflated a encoded AuthnRequest v query stringu. HTTP POST typicky prenáša base64-encoded SAMLResponse v browser form-e. Encoding nie je encryption ani integrity.

```text
HTTP Redirect
→ vhodný pre menší AuthnRequest
→ query-string size, signature a logging considerations

HTTP POST
→ vhodný pre Response/Assertion
→ browser form, body-size a content handling
```

Browser je untrusted carrier. Môže message pozorovať, opakovať alebo meniť. Bezpečnosť pochádza z TLS, signature, exact endpoint/entity bindingu, time conditions, request correlation a replay protection.

Raw SAMLResponse nemá byť v access logoch, traces ani error pages. Môže obsahovať personal data, groups, roles a bearer assertion.

## 7. SP-initiated flow

SP-initiated flow vytvára pending transaction:

```text
SP vytvorí AuthnRequest ID
→ uloží expected IdP, ACS, RelayState a time
→ browser odošle request Keycloaku
→ Keycloak vyberie client podľa Issuer
→ autentizuje usera
→ Response/SubjectConfirmation nesie InResponseTo
→ SP nájde a atomicky spotrebuje request
```

`InResponseTo` viaže response na konkrétny login intent. V clustered SP deployment-e musí byť transaction store shared alebo consistent. Ak jedna replica request vytvorí a druhá response spracuje bez shared state-u, login môže intermittently zlyhávať alebo sa implementácia pokúsi correlation vypnúť.

Signed AuthnRequest môže byť required, najmä keď request ovplyvňuje ACS, NameID, requested authentication context alebo force-authentication behavior. Keycloak musí overovať client signature key z trusted client configuration.

## 8. IdP-initiated flow a unsolicited Response

IdP-initiated login vzniká bez predchádzajúceho SP AuthnRequest-u. Nemá `InResponseTo` binding na pending transaction. Môže byť potrebný pre legacy portal alebo application launcher, ale má slabší login-intent a tenant-routing context.

Safe design potrebuje:

- exact target client;
- allowlisted default ACS;
- bounded RelayState semantics;
- replay protection;
- login CSRF/open-redirect controls;
- client-specific role/attribute mapping;
- local session a tenant policy.

Privileged admin applications majú typicky preferovať SP-initiated flow. „Keycloak to podporuje“ nie je dôvod aktivovať unsolicited responses.

## 9. Signing direction a signature requirements

SAML má viac možných signatures. SP môže podpisovať AuthnRequest. Keycloak môže podpisovať Response, Assertion alebo obe podľa configuration. SP musí vedieť, ktorý element vyžaduje a presne verified element spracovať.

```text
client signature required
→ Keycloak overí signed AuthnRequest od SP

Sign Documents / Sign Assertions
→ Keycloak podpisuje Response a/alebo Assertion

SP verifier
→ vyberie trusted Keycloak realm/entity metadata
→ overí signed element
→ spracuje presne verified node
```

„V dokumente je validná signature“ nie je dostatočné. XML Signature Wrapping môže vzniknúť, ak verifier overí jeden element a application spracuje iný unsigned element. SP library musí viazať claims extraction na verified node a odmietnuť duplicate IDs či ambiguous assertions.

## 10. Encryption a confidentiality boundary

XML encryption môže chrániť assertion alebo NameID pred browserom a intermediaries, aj keď transport používa TLS. Keycloak potrebuje current SP encryption public key; SP potrebuje private key a rollover procedure.

Encryption nenahrádza signature. Encrypted unsigned assertion môže byť confidential, ale nie authenticated. Signed unencrypted assertion môže byť authenticated, ale browser vidí attributes. Requirement sa odvodzuje od threat modelu a data sensitivity.

Rollover musí pokryť overlap, metadata publication, decryption key availability a old assertion validity. Odstránenie old private key príliš skoro znemožní spracovať in-flight response.

## 11. NameID a local identity mapping

NameID je subject identifier v SAML assertion. Format môže byť persistent, transient, email-address alebo iný contract. Local identity key má zahŕňať trusted IdP/realm entity, NameID format a value. Email samotný je mutable a môže byť reassigned.

Keycloak mapper môže zvoliť username, email alebo attribute ako NameID source. Voľba musí zodpovedať downstream SP identity modelu. Persistent identifier znižuje rename coupling; transient identifier je vhodný pre privacy-preserving session, ale nehodí sa ako stable account key bez ďalšieho linking contractu.

JIT provisioning potrebuje duplicate detection, ownera, disable/deprovisioning a unlink/recovery behavior. Platná assertion s novým emailom nemá automaticky prevziať privileged existing account.

## 12. Attribute a role mappers

SAML mapper prekladá Keycloak user attribute, property, group alebo role do AttributeStatement alebo NameID. Mapper je authority boundary podobne ako OIDC protocol mapper.

```text
source identity/role authority
→ mapper generation
→ SAML Attribute Name a NameFormat
→ XML type a cardinality
→ assertion placement
→ SP normalization
→ local attribute alebo entitlement
→ resource authorization
```

Built-in role list mapper alebo custom mapper môže publikovať realm aj client roles. Privileged SP má dostať iba client-specific allowlisted vocabulary. Group hierarchy nemá byť automaticky serializovaná ako application permission.

Missing alebo multiple attribute values potrebujú explicitné behavior. SP nesmie prepnúť missing tenant na wildcard ani vybrať prvú hodnotu bez contractu.

## 13. Audience, Destination, Recipient a time

Keycloak ako IdP generuje fields, ktoré SP musí overiť:

- **AudienceRestriction** — logical SP entity, pre ktorý assertion platí;
- **Destination** — endpoint, kam je protocol Response adresovaná;
- **Recipient** — ACS, kde možno bearer assertion prezentovať;
- **InResponseTo** — pending request, ku ktorému response patrí;
- **NotBefore/NotOnOrAfter** — bounded validity;
- **SessionIndex** — identifier relevantný pre session/logout correlation.

Tieto fields nie sú duplicity. Wrong audience môže znamenať token substitution medzi clients. Wrong destination/recipient môže znamenať callback confusion. Missing `InResponseTo` mení transaction model. Veľká clock-skew tolerancia predlžuje replay window.

## 14. Keycloak session a downstream SAML session

Po authentication Keycloak udržiava user a client session. SAML assertion má krátku validity, no SP vytvorí vlastnú session, ktorá môže trvať dlhšie. `SessionIndex` môže pomôcť SLO, ale local session zostáva vlastníctvom SP.

```text
Keycloak user session
→ Keycloak SAML client session
→ SAML assertion
→ SP local account
→ SP application session
→ downstream API tokens/workflows
```

Zrušenie Keycloak session nemusí automaticky zrušiť SP session. SAML Single Logout je distribuovaný best-effort protocol, nie atomic transaction. Client downtime, browser restrictions alebo endpoint mismatch môžu nechať časť sessions aktívnu.

## 15. Logout a revocation semantics

SP-initiated alebo IdP-initiated logout môže používať Redirect alebo POST binding a signed LogoutRequest/LogoutResponse podľa configuration. Keycloak a SP musia zdieľať SLO endpoint, key a SessionIndex semantics.

Incident response nesmie čakať iba na SLO. Potrebuje server-side SP session revocation, downstream token invalidation a business workflow containment. SLO failure má byť observovateľný per client/session, nie zhrnutý ako global success.

## 16. Connected incident `KC-PAY-65` — SAML path

Client `settlement-partner-sp` mal:

```text
Client ID: urn:atlas:settlement-partner
Master SAML Processing URL:
  https://settlements.atlas.example/saml/acs
IdP-initiated SSO: enabled
role mapper: effective realm roles
Full Scope Allowed: on
```

Shared ACS používal RelayState na výber tenant-a. Contractor z `/payments/partners/vega` zdedil realm role `settlement-admin`. Keycloak vytvoril protocol-valid signed assertion s role attribute. Keďže login bol IdP-initiated, SP nemal pending AuthnRequest a `InResponseTo`. RelayState vybral production admin route a SP mapoval role priamo na local admin session.

Po Keycloak sign-out-e local SP session zostala aktívna. Útočník pokračoval bez novej SAML assertion. Root cause nebola broken XML signature; bola to kombinácia broad role projection, unsolicited flow, weak shared-ACS routing a incomplete local-session revocation.

## 17. SAML redesign

Redesign používa:

```text
unique production SP entity ID
→ reviewed metadata artifact
→ exact ACS a SLO endpoints
→ SP-initiated flow pre privileged login
→ signed AuthnRequest required
→ InResponseTo a shared replay/transaction store
→ Keycloak realm/client-specific signing keys
→ client-role allowlist mapper
→ persistent non-email subject identifier
→ SP tenant/object authorization
→ server-side local session revocation
```

Ak IdP-initiated path zostane pre low-risk portal, použije samostatného clienta, default landing page bez privilege, strict RelayState a samostatný acceptance test.

## 18. Metadata a key rollover test

Rollover rehearsal má preukázať:

1. nový Keycloak signing certificate je publikovaný v IdP metadata;
2. SP trust store načíta old aj new certificate;
3. Keycloak začne podpisovať new keyom;
4. new assertions prejdú na všetkých SP replicas;
5. old in-flight assertions zostanú overiteľné počas overlapu;
6. old key sa odstráni až po expiry a verifier convergence;
7. forbidden old-key assertion po retirement zlyhá.

Encryption rollover vykoná zrkadlový test pre SP decryption keys.

## 19. Acceptance matrix

Pozitívne tests:

- SP-initiated AuthnRequest s correct issuer, signature, ACS a bindingom prejde;
- Response nesie expected audience, destination, recipient, time a `InResponseTo`;
- NameID a attributes majú expected type a authority;
- local session dostane iba client-specific permission;
- logout zruší Keycloak aj SP session podľa contractu.

Negatívne tests:

- wrong entity ID alebo unregistered ACS je odmietnuté;
- unsigned request je odmietnutý, ak signature required;
- unsolicited response je odmietnutá pre privileged clienta;
- wrong audience/destination/recipient alebo replay zlyhá;
- inherited unrelated realm role sa nepublikuje;
- old signing key po retirement zlyhá;
- SLO outage nebráni server-side local-session revocation.

## 20. Troubleshooting flow

Pri „invalid requester/client“ over:

```text
AuthnRequest Issuer
→ exact Keycloak Client ID
→ client enabled/protocol
→ request binding
→ signature requirement a trusted SP key
```

Pri wrong ACS alebo redirect loop:

```text
requested ACS
→ Master SAML Processing URL
→ registered endpoints
→ external proxy scheme/host/path
→ Response Destination
→ SubjectConfirmation Recipient
→ SP external URL validation
```

Pri invalid signature zachovaj metadata generation, certificate fingerprint, signed element ID, algorithm, canonicalization a raw-message hash bez citlivého payloadu. Neimportuj arbitrary certificate ako rýchly fix.

Pri missing role sleduj effective role graph, client scope, mapper generation, actual AttributeStatement a SP mapping. Pri logout probléme oddeľ Keycloak session, SAML SessionIndex a local application session.

## 21. Anti-patterny

### Shared entity ID pre staging a production

Rovnaká protocol identity rozmazáva environment trust. Samostatné URLs bez samostatného entity contractu nestačia.

### Shared ACS + RelayState ako tenant authority

RelayState je transaction/return-state value, nie bezpečný tenant authorization token. Tenant selection musí byť viazaný na client a authenticated local policy.

### Certificate-only trust

Certificate dokazuje key possession. Entity ID, metadata generation, audience a endpoint binding stále rozhodujú, komu assertion patrí.

### Effective realm roles do každého assertion

Broad role list prenáša unrelated permissions a organizačnú štruktúru. Použi client-specific allowlist.

### SLO ako incident revocation

Distributed logout môže byť partial. SP musí mať vlastný server-side session invalidation path.

## 22. Kontrolné otázky

1. Čo Keycloak SAML client reprezentuje?
2. Prečo Client ID typicky zodpovedá SP entity ID?
3. Prečo metadata import nie je automatická dlhodobá reconciliation?
4. Ako sa líši ACS od Master SAML Processing URL?
5. Čo prenáša Redirect a čo POST binding?
6. Prečo SP-initiated flow poskytuje silnejší transaction binding?
7. Čo musí Keycloak overiť pri signed AuthnRequest-e?
8. Aký je rozdiel medzi signing a encryption?
9. Ako NameID súvisí s local identity keyom?
10. Prečo role mapper potrebuje client-specific authority?
11. Prečo SLO nie je atomic revocation?
12. Ktoré negative tests by odhalili `KC-PAY-65`?

## Glossary impact

Relevantné pojmy: Keycloak SAML client generation, SP entity ID, metadata generation, Master SAML Processing URL, Assertion Consumer Service, HTTP Redirect binding, HTTP POST binding, SP-initiated SSO, IdP-initiated SSO, client signature requirement, SAML role mapper, SessionIndex, SAML local session, metadata/key rollover, SAML client acceptance matrix.

## Primárne zdroje

- [Keycloak — Server Administration Guide: Creating a SAML client](https://www.keycloak.org/docs/latest/server_admin/)
- [Keycloak — Planning for securing applications and services](https://www.keycloak.org/securing-apps/overview)
- [OASIS SAML 2.0 Technical Overview](https://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html)
- [OASIS SAML 2.0 Core](https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf)
- [OASIS SAML 2.0 Bindings](https://docs.oasis-open.org/security/saml/v2.0/saml-bindings-2.0-os.pdf)
- [OASIS SAML 2.0 Metadata](https://docs.oasis-open.org/security/saml/v2.0/saml-metadata-2.0-os.pdf)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OIDC clients, redirect URIs, scopes a PKCE](oidc-clients-redirect-uris-scopes-pkce.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
