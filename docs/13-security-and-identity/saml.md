# SAML

Security Assertion Markup Language 2.0 je XML-based federation framework na výmenu authentication, attribute a authorization assertions medzi Identity Providerom a Service Providerom. Najčastejšie sa používa pre enterprise browser Single Sign-On, kde Service Provider dôveruje signed SAML assertions vydaným Identity Providerom.

## 1. Mentálny model

```text
používateľ otvorí Service Provider
→ SP vytvorí AuthnRequest
→ browser presmeruje request na Identity Provider
→ IdP autentizuje používateľa
→ IdP vytvorí signed SAML Response/Assertion
→ browser odošle response na Assertion Consumer Service
→ SP validuje XML signature, issuer, audience, recipient a čas
→ SP vytvorí lokálnu application session
```

SAML je federation protocol. Neprenáša používateľské heslo zo Service Providera do Identity Providera.

## 2. Hlavné role

### Principal

Používateľ alebo iný subject, ktorého sa assertion týka.

### Identity Provider

Autentizuje principal-a a vydáva SAML assertions.

### Service Provider

Poskytuje aplikáciu alebo službu a dôveruje assertions od nakonfigurovaného Identity Providera.

### User agent

Browser, ktorý prenáša protocol messages medzi SP a IdP pri Web Browser SSO profile.

## 3. Assertion, protocol, binding a profile

SAML 2.0 sa skladá z viacerých vrstiev.

### Assertion

XML dokument obsahujúci statements o subjecte.

### Protocol

Definuje request a response messages, napríklad `AuthnRequest` a `Response`.

### Binding

Definuje transport SAML message cez konkrétny protocol, napríklad HTTP Redirect alebo HTTP POST.

### Profile

Kombinuje assertions, protocols a bindings pre konkrétny use case, napríklad Web Browser SSO.

## 4. SAML assertion

Assertion môže obsahovať:

- issuer,
- subject,
- conditions,
- authentication statement,
- attribute statement,
- authorization decision statement,
- signature.

Najčastejšie enterprise SSO používa:

- authentication statement,
- attribute statement.

Assertion je security artifact a musí byť validovaná ako celok, nie iba parsovaná.

## 5. SAML Response

`Response` je protocol message, ktorá môže obsahovať jednu alebo viac assertions.

Dôležité fields:

- `ID`,
- `InResponseTo`,
- `IssueInstant`,
- `Destination`,
- `Issuer`,
- `Status`,
- `Assertion` alebo `EncryptedAssertion`,
- signature.

SP musí rozhodnúť, či vyžaduje signature na Response, Assertion alebo oboch, podľa interoperability a threat modelu.

## 6. AuthnRequest

SP-initiated login začína `AuthnRequest`.

Typicky obsahuje:

- request ID,
- issuer/entity ID SP,
- Assertion Consumer Service URL alebo index,
- protocol binding,
- requested NameID format,
- force authentication alebo passive flags,
- requested authentication context.

IdP musí validovať, že request pochádza od dôveryhodného SP a že ACS endpoint je registrovaný v metadata.

## 7. SP-initiated flow

```text
SP vytvorí AuthnRequest
→ uloží request ID a RelayState
→ presmeruje browser na IdP
→ IdP autentizuje používateľa
→ signed Response na SP ACS
→ SP overí InResponseTo
→ vytvorí session
```

Výhody:

- request/response binding,
- kontrola cieľového SP endpointu,
- možnosť step-up alebo requested contextu,
- bezpečnejší návrat na pôvodnú resource.

## 8. IdP-initiated flow

Pri IdP-initiated flowe používateľ spustí aplikáciu z IdP portálu a SP dostane unsolicited Response bez vlastného AuthnRequestu.

Riziká:

- chýba `InResponseTo` binding,
- vyššie riziko login CSRF alebo account confusion,
- komplikovanejšie RelayState validation,
- slabšia transaction correlation.

Používaj iba s explicitným threat modelom a robustnou replay, recipient, audience a session ochranou.

## 9. Web Browser SSO profile

Najbežnejší SAML profile používa:

- HTTP Redirect binding pre AuthnRequest,
- HTTP POST binding pre SAML Response,
- browser form auto-submit na ACS endpoint.

SAML Response môže byť veľká kvôli XML, signatures, certificates a attributes. Preto sa bežne neposiela query stringom.

## 10. HTTP Redirect binding

Message je:

- DEFLATE-compressed podľa binding pravidiel,
- base64-encoded,
- URL-encoded,
- prenesená v query parameters.

Voliteľná query-level signature používa presné canonical parameter ordering semantics.

Proxy, WAF alebo application framework nesmie meniť signed bytes pred validáciou.

## 11. HTTP POST binding

SAML message sa prenáša ako base64 value v HTML form field-e.

Typické fields:

- `SAMLResponse`,
- `RelayState`.

Base64 nie je encryption. Confidentiality závisí od TLS alebo XML Encryption.

## 12. Artifact binding

Browser prenáša krátky artifact a SP následne získa plnú message cez back-channel SOAP exchange.

Výhody:

- assertion nie je priamo v browseri,
- menší front-channel payload.

Nevýhody:

- back-channel connectivity,
- ďalšia availability dependency,
- TLS a client authentication,
- komplexnejšia prevádzka.

## 13. Metadata

SAML metadata vytvára trust a configuration contract.

Môže obsahovať:

- entity ID,
- SSO/SLO endpoints,
- ACS endpoints,
- supported bindings,
- signing a encryption certificates,
- NameID formats,
- organization/contact údaje,
- valid-until a cache duration.

Metadata nemajú byť načítavané z ľubovoľnej user-provided URL.

Trust bootstrap musí určiť:

- autoritatívny source,
- signature validation,
- certificate rollover,
- refresh interval,
- emergency revocation.

## 14. Entity ID

Entity ID je stabilný identifier IdP alebo SP.

Môže vyzerať ako URL, ale nemusí byť browsable endpoint.

SP musí validovať očakávaného `Issuer` proti dôveryhodnej metadata konfigurácii.

Rovnaký certificate použitý viacerými entities neznamená, že issuers sú zameniteľní.

## 15. Assertion Consumer Service

ACS je endpoint SP, ktorý prijíma SAML Response.

Controls:

- HTTPS,
- exact metadata registration,
- povolené bindings,
- CSRF/login transaction protection,
- payload size limits,
- secure XML parser,
- replay cache,
- no sensitive response logging.

SP nemá dôverovať ľubovoľnej ACS URL dodanej v requeste bez metadata validation.

## 16. NameID

NameID identifikuje subject podľa konkrétneho format-u.

Možné formats:

- persistent,
- transient,
- email address,
- unspecified,
- ďalšie definované formáty.

Preferuj stabilný opaque identifier.

Email ako NameID prináša riziká:

- zmena,
- recyklácia,
- case normalization,
- cross-tenant kolízia,
- privacy correlation.

Internal identity key má zahŕňať aj issuer/entity context.

## 17. SubjectConfirmation

Bearer Web SSO assertion typicky používa `SubjectConfirmationData` s fields ako:

- `Recipient`,
- `NotOnOrAfter`,
- `InResponseTo`.

SP musí validovať:

- správny recipient/ACS,
- časové obmedzenie,
- request binding pri SP-initiated flowe.

Ignorovanie SubjectConfirmation validation umožňuje replay alebo token substitution.

## 18. Conditions

`Conditions` obmedzujú platnosť assertion.

Dôležité:

- `NotBefore`,
- `NotOnOrAfter`,
- `AudienceRestriction`,
- ďalšie profile-specific conditions.

SP musí používať bounded clock-skew tolerance, nie vypnúť time validation.

## 19. AudienceRestriction

Audience určuje, pre ktorý SP je assertion určená.

SP musí odmietnuť assertion:

- bez očakávaného audience podľa policy,
- určenú pre inú aplikáciu,
- z iného environmentu alebo tenant trustu.

Valid signature bez správnej audience nestačí.

## 20. Destination a Recipient

### Destination

Určuje endpoint pre protocol Response.

### Recipient

Určuje endpoint pre bearer subject confirmation.

Obe hodnoty musia zodpovedať reálnemu a registrovanému ACS endpointu podľa profile pravidiel.

Reverse proxy configuration musí správne rekonštruovať external scheme, host a port.

## 21. InResponseTo

`InResponseTo` viaže Response alebo SubjectConfirmationData na konkrétny AuthnRequest.

SP musí:

- uložiť request ID,
- validovať exact match,
- použiť jednorazový request state,
- po úspechu ID odstrániť,
- nastaviť krátku expiry.

Tým sa znižuje replay, login CSRF a response confusion.

## 22. RelayState

RelayState prenáša application state, napríklad pôvodnú URL.

Musí byť:

- chránený integrity mechanizmom alebo server-side reference,
- viazaný na session/request,
- validovaný proti open redirectu,
- bez citlivých údajov.

Útočník nesmie pomocou RelayState presmerovať používateľa na ľubovoľnú doménu.

## 23. Authentication statement

Authentication statement opisuje:

- čas authentication,
- session index,
- authentication context,
- subject local session.

SP musí rozhodnúť:

- akú authentication freshness potrebuje,
- ktoré contexts akceptuje,
- či vyžaduje MFA alebo phishing-resistant method,
- kedy spustiť step-up.

Samotná existencia assertion neznamená požadovanú assurance úroveň.

## 24. Authentication context

SAML authentication context vyjadruje class alebo declaration použitej authentication.

Interoperability vyžaduje dohodu medzi IdP a SP.

SP nesmie interpretovať neznámu URI ako ekvivalent silnej MFA.

RequestedAuthnContext môže byť:

- exact,
- minimum,
- better,
- maximum,

podľa profile semantics a implementácie.

## 25. Attribute statement

Attributes prenášajú identity alebo entitlement údaje.

Príklady:

- department,
- employee identifier,
- email,
- group,
- role,
- tenant.

SP potrebuje explicitný mapping:

```text
attribute Name/NameFormat
→ expected type a cardinality
→ normalization
→ internal attribute
→ authorization policy
```

Attribute prítomnosť nie je automaticky dôveryhodná pre privileged access.

## 26. Attribute governance

Kontroluj:

- autoritatívny source,
- required a optional attributes,
- multi-value behavior,
- maximum count/size,
- case sensitivity,
- stale directory data,
- group overage/truncation,
- privacy a minimization,
- deprovisioning latency.

Role alebo admin access nemajú byť odvodené z neovereného display attribute-u.

## 27. XML Signature

XML Signature poskytuje integrity a issuer authenticity pre signed element.

Validácia musí:

- používať dôveryhodný metadata certificate/key,
- overiť signature nad správnym elementom,
- overiť reference URI,
- odmietnuť duplicate IDs,
- používať bezpečnú canonicalization implementation,
- zakázať weak algorithms,
- nevyberať assertion jednoduchým XPath bez signature bindingu.

## 28. XML Signature Wrapping

Wrapping attack využíva rozdiel medzi elementom overeným signature knižnicou a elementom spracovaným application logic.

Mitigácie:

- používať udržiavanú SAML knižnicu,
- secure ID registration,
- spracovať presne signed element,
- odmietnuť duplicate/ambiguous structures,
- strict schema/profile validation,
- neimplementovať vlastnú XML signature logiku.

## 29. XML Encryption

Assertion alebo vybrané elements môžu byť šifrované pre SP.

Encryption poskytuje confidentiality, ale:

- nenahrádza TLS,
- komplikuje key rotation,
- zvyšuje payload a CPU,
- vyžaduje bezpečný parser,
- môže spôsobiť outage pri certificate mismatch.

Signing a encryption majú odlišné key lifecycle-y.

## 30. Certificate model

SAML metadata často obsahujú X.509 certificates ako key containers.

Trust typicky nevychádza z public Web PKI hostname validation, ale z explicitnej metadata trust konfigurácie.

Certificate expiry, rollover a overlap musia byť riadené.

Bezpečný rollover:

1. publikovať nový key spolu so starým,
2. počkať na metadata propagation,
3. začať podpisovať novým key,
4. sledovať validation failures,
5. odstrániť starý key po overlap intervale.

## 31. Clock synchronization

SAML assertions majú krátke time windows.

Potrebné:

- spoľahlivý NTP/time service,
- bounded skew tolerance,
- monitoring clock offsetu,
- UTC logging,
- správna interpretácia `NotOnOrAfter` ako exclusive boundary.

Veľké skew tolerance predlžuje replay window.

## 32. Replay protection

SP má uchovávať krátkodobú cache:

- assertion IDs,
- response IDs,
- request IDs,
- session indexes podľa potreby.

Pri opakovanom ID musí response odmietnuť.

Replay cache potrebuje:

- HA/shared-state model,
- expiry,
- memory/storage limits,
- tenant isolation,
- fail-safe behavior.

## 33. Local application session

Po úspešnej SAML validation SP vytvorí vlastnú session.

Session controls:

- secure, HttpOnly a SameSite cookies,
- session fixation protection,
- idle/absolute timeout,
- local revocation,
- CSRF protection,
- reauthentication pre citlivé operácie,
- audit.

SAML assertion sa nemá používať opakovane ako session bearer artifact.

## 34. Single Logout

SLO sa pokúša koordinovať ukončenie sessions medzi IdP a SPs.

Komponenty:

- `LogoutRequest`,
- `LogoutResponse`,
- NameID,
- SessionIndex,
- front-channel alebo back-channel binding podľa implementácie.

Riziká:

- partial failure,
- browser restrictions,
- unavailable SP,
- stale session indexes,
- logout loops,
- signed-message requirements.

SLO nie je automaticky spoľahlivá globálna revocation všetkých tokens a sessions.

## 35. IdP discovery

V multi-IdP prostredí musí SP vybrať správneho providera.

Možnosti:

- tenant-specific URL,
- organization discovery,
- preconfigured domain mapping,
- federation metadata.

Nepoužívaj user-provided IdP metadata alebo entity ID bez allowlist/trust policy.

Email-domain discovery môže byť iba routing hint, nie proof organizácie.

## 36. Federation trust

Trust contract zahŕňa:

- entity IDs,
- signing/encryption keys,
- endpoints a bindings,
- attribute contract,
- authentication assurance,
- certificate rotation,
- incident contacts,
- deprovisioning latency,
- metadata refresh,
- audit a privacy.

Technicky validná assertion môže stále porušiť business federation contract.

## 37. SAML oproti OpenID Connect

| Vlastnosť | SAML 2.0 | OpenID Connect |
|---|---|---|
| Formát | XML | JSON/JWT |
| Typický use case | enterprise browser SSO | web, mobile, API ecosystem |
| Hlavný identity artifact | SAML Assertion | ID Token |
| Configuration | metadata XML | discovery JSON + JWKS |
| Transport | browser bindings, SOAP | OAuth endpoints cez HTTP |
| Modern native/mobile fit | slabší | silnejší |

Výber závisí od ekosystému, nie od tvrdenia, že jeden protocol je univerzálne bezpečnejší.

## 38. SAML a authorization

SAML môže preniesť role/group attributes, ale SP stále vykonáva local authorization.

```text
IdP assertion
→ identity a attributes
→ SP normalization
→ local account/session
→ application authorization
```

IdP nemá automaticky rozhodovať o každom resource-level action, pokiaľ federation contract výslovne neurčuje inak.

## 39. Security controls

Minimálny production baseline:

- TLS,
- trusted metadata,
- XML signature validation,
- strict issuer/audience/recipient/destination validation,
- time validation,
- replay cache,
- `InResponseTo` pre SP-initiated flow,
- RelayState protection,
- secure XML parser,
- attribute allowlist,
- bounded payload size,
- certificate rollover,
- safe audit logging.

## 40. Secure XML processing

Parser musí zakázať alebo bezpečne riadiť:

- external entities,
- DTDs,
- entity expansion,
- external resource resolution,
- oversized documents,
- excessive nesting,
- duplicate IDs.

XXE alebo XML bomb môže ohroziť confidentiality aj availability ACS endpointu.

## 41. Troubleshooting SSO flow

```text
SP metadata a entity ID?
→ AuthnRequest destination/binding/signature?
→ IdP authentication a policy?
→ Response status?
→ ACS URL a proxy reconstruction?
→ XML parse/decode?
→ signature a certificate?
→ issuer/audience/destination/recipient?
→ time a clock skew?
→ InResponseTo/replay cache?
→ NameID a attribute mapping?
→ local session/authorization?
```

## 42. Typické chyby

### Invalid signature

Over:

- správny metadata certificate,
- signing key rollover,
- signed element,
- canonicalization,
- message transform/proxy,
- algorithm policy.

### Audience mismatch

Assertion je určená pre inú SP entity ID alebo environment.

### Recipient/Destination mismatch

Často spôsobené reverse proxy scheme/host/port alebo nesprávnym ACS endpointom.

### Assertion expired alebo not yet valid

Over NTP, time zone logging, skew policy a IdP/SP clocks.

### InResponseTo unknown

Request state expiroval, session sa stratila, response patrí inému node-u alebo ide o unsolicited response.

### User authenticated, ale account nevznikol

Over NameID, required attributes, case/type normalization, JIT provisioning a duplicate identity.

### Login loop

Over session cookie, SameSite, IdP session, entity ID, proxy headers a authorization failure po login-e.

## 43. Observability a audit

Sleduj:

- AuthnRequest a Response success/failure rate,
- failures podľa IdP/SP v bounded labels,
- signature/certificate errors,
- issuer/audience/recipient failures,
- clock-skew failures,
- replay detections,
- attribute mapping/provisioning failures,
- local session creation,
- SLO failures,
- metadata refresh/expiry.

Neloguj plnú SAML Response, assertion alebo citlivé attributes. Použi request/response IDs a redacted audit fields.

## 44. Incident response

Pri signing-key compromise:

1. identifikuj affected IdP/SP entity a key,
2. odstráň compromised key z trustu,
3. publikuj/načítaj emergency metadata,
4. invaliduj relevantné sessions podľa risku,
5. analyzuj assertions vydané počas compromise window,
6. monitoruj replay a validation failures,
7. obnov certificate rollover process,
8. dokumentuj federation partner coordination.

Pri attribute-source compromise analyzuj aj authorization dopad, nie iba authentication.

## 45. Anti-patterny

### Base64 decode považovaný za validáciu

Assertion môže byť attacker-controlled.

### Signature validná, teda všetko je validné

Stále treba issuer, audience, recipient, time, request a replay validation.

### Email ako permanent identity key

Email sa môže meniť a recyklovať.

### Metadata fetch z user-provided URL

Umožňuje attacker-controlled issuer a keys.

### IdP-initiated flow bez replay a login-CSRF modelu

Chýba request binding.

### Vlastná XML Signature implementácia

Veľké riziko wrapping a canonicalization chýb.

### SAML attributes priamo ako admin permissions

Bez mapping, allowlist a authoritative contractu vzniká privilege escalation.

### SLO považované za spoľahlivú revocation

Partial failures a lokálne sessions môžu zostať aktívne.

## 46. Kontrolné otázky

1. Aký je rozdiel medzi assertion, protocol, binding a profile?
2. Aké role majú IdP a SP?
3. Ako sa líši SP-initiated a IdP-initiated flow?
4. Na čo slúžia metadata a entity ID?
5. Čo musí SP validovať v SAML Response?
6. Aký je rozdiel medzi audience, destination a recipient?
7. Na čo slúži `InResponseTo` a RelayState?
8. Ako funguje XML Signature a wrapping attack?
9. Prečo certificate rollover potrebuje overlap?
10. Ako sa líši NameID a attribute?
11. Ako SAML súvisí s local authorization?
12. Ako diagnostikuješ signature, time a ACS mismatch?

## Glossary impact

Relevantné pojmy: SAML, principal, Identity Provider, Service Provider, SAML assertion, SAML protocol, binding, profile, SAML Response, AuthnRequest, Web Browser SSO profile, HTTP Redirect binding, HTTP POST binding, artifact binding, SAML metadata, entity ID, Assertion Consumer Service, NameID, SubjectConfirmation, Conditions, AudienceRestriction, Destination, Recipient, InResponseTo, RelayState, authentication statement, authentication context, attribute statement, XML Signature, XML Signature Wrapping, XML Encryption, replay cache, Single Logout a SAML federation trust.

## Primárne zdroje

- [SAML 2.0 Core](https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf)
- [SAML 2.0 Bindings](https://docs.oasis-open.org/security/saml/v2.0/saml-bindings-2.0-os.pdf)
- [SAML 2.0 Profiles](https://docs.oasis-open.org/security/saml/v2.0/saml-profiles-2.0-os.pdf)
- [SAML 2.0 Metadata](https://docs.oasis-open.org/security/saml/v2.0/saml-metadata-2.0-os.pdf)
- [SAML 2.0 Authentication Context](https://docs.oasis-open.org/security/saml/v2.0/saml-authn-context-2.0-os.pdf)
- [SAML 2.0 Security and Privacy Considerations](https://docs.oasis-open.org/security/saml/v2.0/saml-sec-consider-2.0-os.pdf)
