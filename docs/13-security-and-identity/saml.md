# SAML

Security Assertion Markup Language 2.0 — SAML — je XML-based federation framework. Identity Provider autentizuje principal-a a vydá assertion pre konkrétneho Service Providera. Service Provider vytvorí local application session až po cryptographic, structural, semantic a transaction validation.

SAML signature nepotvrdzuje „používateľ je dôveryhodný“. Potvrdzuje, že konkrétny signed XML element vytvoril držiteľ trusted signing keyu. Service Provider musí stále overiť entity/issuer, audience, destination, recipient, čas, request binding, replay, subject mapping, attribute authority a local resource authorization.

## 1. Dominantný metadata-to-session lifecycle

```text
federation contract a metadata trust
→ SP AuthnRequest a pending transaction
→ IdP authentication a attribute resolution
→ signed Response/Assertion generation
→ browser binding a ACS receipt
→ secure XML parsing a signed-node validation
→ issuer, audience, destination, recipient, time a replay verdict
→ NameID a attribute mapping
→ local session generation
→ resource authorization
→ logout, key rollover a incident revocation
```

SAML assertions, protocols, bindings, profiles a metadata sú rozdielne vrstvy. Assertion opisuje subject a statements. Protocol `Response` nesie status a correlation. Binding určuje transport. Metadata určujú entities, endpoints, keys a supported profiles. Web Browser SSO profile ich skladá do jedného login flowu.

## 2. Exact SAML subject

Pri incidente zachovaj:

```text
trusted metadata generation
+ IdP entity ID a SP entity ID
+ signing/encryption key generation
+ AuthnRequest ID a expected ACS
+ binding a RelayState transaction
+ Response/Assertion IDs
+ signed element identity
+ Issuer, Audience, Destination, Recipient a InResponseTo
+ NameID format/value a attribute mapping revision
+ local account, session a requested resource
+ replay/logout/revocation state
```

Connected subject `SAML-PAY-49`:

```text
production SP entity: urn:atlas:payments-admin:prod
expected IdP: https://id.atlas.example/prod/saml
accepted Issuer: https://id.atlas.example/staging/saml
ACS: https://payments-admin.atlas.example/saml/acs
signing key: FED-SIGN-07
NameID: marta.novak@atlas.example
Role attribute: SettlementAdmin
local session: SAML-SESS-77104
```

## 3. Metadata je trust bootstrap

Metadata určujú:

- entity ID;
- SSO/SLO a ACS endpoints;
- bindings;
- signing a encryption keys;
- NameID formats;
- validity a cache policy;
- key rollover overlap.

Trusted flow:

```text
approved federation partner/entity
→ signed alebo out-of-band trusted metadata
→ entity ID exact binding
→ endpoints a keys pod touto entity generation
→ bounded refresh a last-known-good policy
```

Certificate nie je samostatná federation identity. Rovnaký public key použitý dvoma entities alebo environments nerobí tieto entities ekvivalentnými. SP musí najprv vybrať trusted entity a až potom key patriaci jej metadata generation.

User-provided metadata URL alebo certificate nesmie automaticky rozšíriť trust.

## 4. SP-initiated transaction

SP-initiated flow vytvára explicitný request/response binding:

```text
SP vytvorí unique AuthnRequest ID
→ uloží expected IdP, ACS, time a browser transaction
→ browser odošle request IdP
→ IdP autentizuje usera
→ Response a SubjectConfirmation obsahujú InResponseTo
→ SP exactne nájde a atomicky spotrebuje pending request
```

`InResponseTo` chráni proti unsolicited response confusion a pomáha viazať browser na konkrétny login intent. V HA SP potrebuje shared alebo consistent transaction store.

IdP-initiated response nemá SP request ID. Môže byť podporovaná pre legacy requirement, ale má slabší transaction binding a potrebuje samostatný login-CSRF, replay, RelayState a tenant-routing model. Nemá byť povolená iba preto, že library ju akceptuje.

## 5. Browser bindings

HTTP Redirect často prenáša menší AuthnRequest. HTTP POST prenáša Response v browser form-e. Base64 je encoding, nie confidentiality ani integrity.

Browser je nedôveryhodný transport. Môže payload pozorovať, zopakovať alebo meniť. Bezpečnosť preto vychádza z:

- TLS;
- XML signature;
- exact endpoint a entity bindingu;
- request/response state;
- time conditions;
- replay cache;
- local session controls.

Raw SAML message nepatrí do access logu, trace ani error page. Môže obsahovať personal data a reusable bearer assertion.

## 6. Secure XML a signed-node binding

XML Signature podpisuje referenced XML element, nie automaticky celý parsed document. Verification musí:

1. použiť secure XML parser bez DTD, external entities a remote schemas;
2. limitovať payload, depth, elements a attributes;
3. odmietnuť duplicate IDs;
4. resolve-nuť unique signed element;
5. použiť key iba z trusted entity metadata;
6. overiť canonicalization, digest, signature a algorithm policy;
7. odovzdať claims processoru presne verified element;
8. odmietnuť extra, ambiguous alebo unsigned assertions.

```text
v dokumente existuje validná signature
≠ application spracovala signed assertion
```

XML Signature Wrapping vzniká, keď library overí benign signed element, ale application prečíta attacker-controlled sibling alebo iný XPath node. Mitigation je structural binding signed node-u, nie iba ďalší signature check.

## 7. Issuer a entity binding

`Issuer` sa porovná s exact trusted IdP entity ID z federation configuration. SP nesmie vybrať trust iba podľa certificate thumbprintu.

```text
valid signature keyom K
+ Issuer staging
≠ production IdP assertion
```

Test a production entities majú samostatné IDs, metadata, keys a sessions. Shared certificate je anti-pattern, pretože key compromise alebo configuration bug prekročí environment boundary.

## 8. Audience, Destination a Recipient

Tieto fields chránia rozdielne bindings:

- `AudienceRestriction` — logical intended SP entity;
- `Destination` — endpoint, kam bola protocol Response adresovaná;
- `Recipient` — ACS, kde možno bearer assertion prezentovať.

Všetky applicable hodnoty sa validujú voči configured external identity. Reverse proxy musí mať trusted external-URL configuration. Vypnutie recipient/destination validation kvôli internal URL mismatchu odstráni protection proti assertion substitution.

## 9. Čas a replay

SAML používa `IssueInstant`, `NotBefore`, `NotOnOrAfter`, SubjectConfirmation expiry a request lifetime. Clock-skew tolerance je bounded a monitorovaná.

SP uchová consumed Response a Assertion IDs do konca validity plus safety interval. Replay cache musí byť shared alebo consistent naprieč ACS replicas. Pri high-risk login-e je unavailable replay control dôvod na fail-closed, nie tichý bypass.

`NotOnOrAfter` je exclusive boundary. Veľká skew tolerancia predlžuje stolen-assertion window.

## 10. Subject a identity mapping

Local federation identity key je:

```text
IdP entity ID
+ NameID format
+ NameID value
```

Email môže byť NameID formatom, ale stále je mutable a potentially reassigned identifier. SP nemá linkovať existing privileged account iba podľa emailu.

JIT provisioning potrebuje allowed tenant/entity, duplicate prevention, ownera, deprovisioning a unlink/recovery lifecycle.

## 11. Attribute authority

AttributeStatement môže prenášať department, tenant, group alebo role. Každý attribute potrebuje contract:

```text
IdP entity + attribute Name/NameFormat
→ expected XML type, cardinality a size
→ normalization
→ authoritative source a allowed values
→ local attribute alebo entitlement input
→ policy revision
```

Cryptographically valid `Role=SettlementAdmin` je nebezpečný, ak federation partner nemá authority danú role vydávať. Missing, duplicate alebo truncated group list musí mať explicitné fail behavior.

## 12. Authentication context a fresh login

`AuthnStatement` opisuje authentication event a môže obsahovať `AuthnInstant`, `SessionIndex` a AuthnContext. SP mapuje AuthnContext iba podľa explicitného federation contractu.

`ForceAuthn` alebo RequestedAuthnContext nemajú zmysel bez validácie returned contextu. Fresh IdP interaction a strong method sú dve samostatné properties. Sensitive settlement action môže vyžadovať exact phishing-resistant context aj local JIT state.

## 13. Local session a authorization

Po successful assertion validation SP vytvorí vlastnú session:

```text
validated entity + subject
→ local account/link
→ normalized attributes
→ local session generation
→ tenant, JIT a workflow authorization
```

Assertion expiry, IdP session a local session expiry sa nemusia zhodovať. Local session potrebuje Secure/HttpOnly/SameSite cookie, fixation protection, idle/absolute timeout, revocation a step-up policy.

SAML Single Logout nie je atomic distributed transaction. Incident response musí vedieť zrušiť local sessions a downstream tokens aj keď IdP alebo iný SP nereaguje.

## 14. Worked failure — certificate trusted bez entity boundary

Atlas použil jeden RSA private key `FED-SIGN-07` pre staging aj production a zároveň pre OIDC a SAML signing. Staging key bol materializovaný do Kubernetes Secretu a dostupný broad debug workloadu.

Production SAML SP malo defects:

```text
trust podľa certificate thumbprintu
- exact Issuer/entity binding
+ IdP-initiated responses enabled
- required InResponseTo
- Destination/Recipient validation vypnutá kvôli proxy mismatchu
+ email-based account linking
+ direct Role attribute mapping
```

Attacker s keyom vytvoril signed Response:

```text
Issuer: https://id.atlas.example/staging/saml
Audience: urn:atlas:payments-admin:prod
Destination: https://payments-admin.atlas.example/saml/acs
NameID: marta.novak@atlas.example
Role: SettlementAdmin
Assertion validity: 5 minút
```

XML signature bola validná a audience obsahovala production SP. SP vyhľadal key podľa certificate thumbprintu, neoveril trusted entity ID, prijal unsolicited response a emailom spojil subject s production admin účtom. Vytvoril session `SAML-SESS-77104`.

## 15. Competing hypotheses a discriminating evidence

Hypotézy:

1. XML Signature Wrapping;
2. replay legitímnej production assertion;
3. wrong reverse-proxy URL;
4. compromised production IdP;
5. staging signing key akceptovaný v production;
6. unsafe account linking a role mapping.

Evidence:

- signature reference smerovala na presne spracovanú assertion; wrapping sa nepotvrdil;
- Response/Assertion IDs neboli v replay cache;
- Issuer bol staging entity;
- key thumbprint bol rovnaký v staging aj production metadata history;
- response nemala `InResponseTo`, ale IdP-initiated path ju povolil;
- production IdP audit nemal authentication event;
- local account bol nájdený emailom;
- admin role vznikla priamo z `Role` attribute.

Root cause je key-centric trust bez entity/metadata boundary. Unsolicited response, disabled recipient checks, email linking a direct role mapping sú amplifiers.

## 16. Evidence-preserving containment

- odstrániť `FED-SIGN-07` z production trusted metadata;
- zablokovať IdP-initiated login pre high-risk SP;
- zastaviť privileged session creation z affected entity/key interval-u;
- preserve-nuť metadata generations, Response/Assertion ID a hash, signed reference, issuer, session a mapping audit bez raw assertion;
- revoke-nuť affected local sessions a downstream credentials;
- nevypínať XML validation ani neakceptovať unsigned emergency assertions.

## 17. Authoritative recovery

1. vytvoriť unique production SAML signing key a samostatný OIDC key;
2. publikovať trusted production metadata s exact entity ID;
3. vykonať bounded rollover a odstrániť starý key po session/assertion cleanup-e;
4. obnoviť exact Destination, Recipient, Audience a InResponseTo validation;
5. opraviť trusted proxy external-URL configuration;
6. vypnúť unsolicited responses alebo ich izolovať do explicitného low-risk profile-u;
7. mapovať identity cez entity + NameID format/value;
8. odstrániť direct partner-role mapping a zaviesť authority allowlist;
9. revoke-nuť local sessions a auditovať actions;
10. obnoviť settlement state z authoritative business records.

## 18. Acceptance verdict

- validly signed staging assertion je v production odmietnutá;
- wrong entity, audience, destination, recipient, time alebo replay zlyhá;
- unsigned/extra/ambiguous assertion a wrapping fixture zlyhajú;
- same-email subject z inej entity neprevezme účet;
- untrusted Role attribute nevytvorí privilege;
- approved production assertion vytvorí bounded session;
- old key a sessions sú neplatné;
- second metadata rollover prejde na všetkých SP replicas;
- local logout a emergency revocation zrušia relevantné sessions bez závislosti na global SLO úspechu;
- oprávnený JIT user môže schváliť settlement, forbidden staging a non-JIT paths zlyhajú.

## 19. Troubleshooting flow

```text
trusted metadata generation
→ entity IDs, endpoints a keys
→ AuthnRequest/pending transaction
→ binding a ACS external URL
→ secure XML shape
→ exact signed element
→ issuer/audience/destination/recipient/time
→ InResponseTo a replay
→ NameID identity mapping
→ attribute authority mapping
→ local session a authorization
→ logout/key revocation
```

## 20. Earlier controls

- separate keys, entity IDs a metadata per environment a protocol purpose;
- signed metadata refresh a rollover canary;
- required SP-initiated flow pre privileged applications;
- secure parser a wrapping regression fixtures;
- exact external ACS test za reverse proxy;
- identity key bez email linking;
- federation attribute-authority registry;
- session inventory podľa entity, key a mapping revision;
- emergency metadata/key removal rehearsal.

## 21. Anti-patterny

### Trusted certificate = trusted IdP

Certificate key musí byť viazaný na exact metadata entity.

### Valid signature = valid SAML login

Stále chýba semantic, transaction, replay a local policy validation.

### Recipient validation vypnutá za proxy

Správna oprava je trusted external URL reconstruction.

### IdP role = application role

Attribute authority a local resource policy zostávajú samostatné.

### SLO = complete revocation

Local sessions a API credentials môžu prežiť.

## 22. Kontrolné otázky

1. Ako assertions, protocols, bindings, profiles a metadata súvisia?
2. Prečo certificate nie je federation identity?
3. Čo chráni `InResponseTo`?
4. Ako sa Audience, Destination a Recipient líšia?
5. Ako XML Signature Wrapping obíde naive validation?
6. Prečo je signed-node binding kritický?
7. Ako sa entity ID + NameID líši od email identity?
8. Prečo attribute nie je automatická authorization authority?
9. Prečo SLO nie je atomic revocation?
10. Čo musí overiť SAML acceptance verdict?

## Glossary impact

Relevantné pojmy: SAML subject, metadata trust generation, entity-bound signing key, SAML transaction generation, signed-node binding, assertion acceptance verdict, federation attribute authority, unsolicited-response risk, SAML session generation a SAML revocation closure.

## Primárne zdroje

- [SAML 2.0 Core](https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf)
- [SAML 2.0 Profiles](https://docs.oasis-open.org/security/saml/v2.0/saml-profiles-2.0-os.pdf)
- [SAML 2.0 Bindings](https://docs.oasis-open.org/security/saml/v2.0/saml-bindings-2.0-os.pdf)
- [SAML 2.0 Metadata](https://docs.oasis-open.org/security/saml/v2.0/saml-metadata-2.0-os.pdf)
- [SAML 2.0 Security and Privacy Considerations](https://docs.oasis-open.org/security/saml/v2.0/saml-sec-consider-2.0-os.pdf)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OpenID Connect](openid-connect.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Secrets management →](secrets-management.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
