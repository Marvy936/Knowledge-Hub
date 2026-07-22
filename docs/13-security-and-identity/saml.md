# SAML

Security Assertion Markup Language 2.0 je XML-based federation framework, ktorým Identity Provider odovzdáva Service Providerovi cryptographically protected assertions o authenticated subjecte a jeho attributes. Najčastejšie sa používa pri enterprise browser Single Sign-On, kde používateľ autentizuje na IdP a application SP vytvorí vlastnú session až po kompletnej validácii SAML transaction.

SAML neprenáša user password do každej application. Prenáša assertion: časovo obmedzené vyhlásenie vydané konkrétnym issuerom pre konkrétny audience a recipient. Platná XML signature je iba jedna podmienka. SP musí overiť aj issuer, audience, destination, recipient, čas, request binding, replay state a local identity mapping.

```text
browser otvorí Service Provider
→ SP vytvorí AuthnRequest a uloží transaction state
→ browser prenesie request na Identity Provider
→ IdP autentizuje usera a vyhodnotí federation policy
→ IdP vydá signed Response/Assertion
→ browser odošle message na SP Assertion Consumer Service
→ SP bezpečne parsuje a validuje celú transaction
→ SP mapuje subject/attributes na local account
→ application vytvorí vlastnú session a vykonáva local authorization
```

## 1. Prečo federation existuje

Bez federation musí každá application spravovať vlastné passwords, MFA, recovery a identity lifecycle. To zvyšuje počet credentials, nekonzistentné controls a offboarding delay.

Pri SAML federation sa authentication centralizuje na IdP. SP dôveruje definovanému issuerovi, jeho signing keys a agreed identity/attribute contractu. SP však stále vlastní local session a resource-level authorization.

Federation presúva risk. Compromise IdP signing authority alebo attribute source môže ovplyvniť množstvo applications naraz. Metadata, key rotation, incident coordination a assurance mapping sú preto súčasť protocol designu, nie iba onboarding configuration.

## 2. Štyri vrstvy SAML štandardu

SAML 2.0 nie je jeden XML dokument. OASIS štandard oddeľuje viac vrstiev:

- **Assertions** definujú statements o subjecte.
- **Protocols** definujú request/response messages ako `AuthnRequest`, `Response` a logout messages.
- **Bindings** určujú, ako sa protocol message prenesie cez HTTP Redirect, HTTP POST, SOAP alebo artifact mechanismus.
- **Profiles** kombinujú assertions, protocols a bindings do konkrétneho interoperabilného use case-u, napríklad Web Browser SSO.
- **Metadata** opisujú identities, endpoints, bindings, keys a capabilities federation entities.
- **Authentication Context** štandardizuje claims o spôsobe alebo assurance authentication.

Táto separácia vysvetľuje, prečo rovnaký `AuthnRequest` možno preniesť rôznymi bindings a prečo samotná assertion nepopisuje celý browser flow.

## 3. Hlavné role

**Principal** je subject, najčastejšie human user, ktorého authentication assertion opisuje.

**Identity Provider — IdP** autentizuje principal-a, získava identity attributes a vydáva SAML assertions podľa federation contractu.

**Service Provider — SP** poskytuje application. Prijíma SAML messages, validuje ich, mapuje external subject na local identity a vytvára application session.

**User agent** je browser prenášajúci front-channel messages. Browser nie je trusted message processor; user môže payload pozorovať, zopakovať alebo zmeniť. Security preto musí vychádzať zo signatures, transaction bindingu, TLS, replay cache a strict validation.

## 4. Assertion ako security artifact

SAML assertion je XML element s statements o subjecte. Môže obsahovať:

- `Issuer` — entity, ktorá assertion vydala;
- `Subject` — identity a SubjectConfirmation;
- `Conditions` — časové a audience obmedzenia;
- `AuthnStatement` — informáciu o authentication evente;
- `AttributeStatement` — identity alebo entitlement attributes;
- voliteľné authorization statements;
- XML Signature.

Assertion nie je iba data container. Je bearer-like security artifact v bežnom Web SSO profile. Každý, kto ju dokáže replay-nuť v platnom okne a pre správneho recipienta, môže potenciálne získať session, ak SP nemá request a replay controls.

## 5. Response oproti Assertion

`Response` je protocol message. Obsahuje status, issuer, destination, correlation metadata a jednu alebo viac plain alebo encrypted assertions.

Signature môže chrániť Response, Assertion alebo obe podľa federation profile-u a implementation contractu. SP musí presne vedieť, ktorý element vyžaduje podpísaný a ktorý element application spracuje.

Nebezpečný model je „v dokumente sa nachádza jedna validná signature“. XML document môže obsahovať viac elements; security library a business logic musia pracovať s tým istým signed node-om.

## 6. AuthnRequest

Pri SP-initiated login-e SP vytvorí `AuthnRequest`. Typicky obsahuje:

- unique request ID;
- SP entity ID v `Issuer`;
- IdP destination;
- requested ACS URL alebo index;
- expected response binding;
- optional NameID policy;
- `ForceAuthn` alebo `IsPassive` flags;
- optional `RequestedAuthnContext`.

SP uloží request ID, creation time, expected IdP a return state. IdP overí, že requester je registrovaný SP, requested ACS patrí k jeho metadata a optional signed request používa trusted SP key.

## 7. SP-initiated browser SSO

SP-initiated flow poskytuje explicitný request/response binding.

```text
GET protected resource
→ SP zistí chýbajúcu session
→ vytvorí AuthnRequest ID=_abc a server-side transaction state
→ Redirect browser na IdP
→ IdP autentizuje usera
→ POST Response InResponseTo=_abc na registered ACS
→ SP overí signature, issuer, audience, recipient, time a replay
→ SP spotrebuje transaction state
→ vytvorí local session
```

`InResponseTo` a stored request state znižujú login CSRF, unsolicited response confusion a replay. Return URL sa má uchovať server-side alebo integrity-protected, nie ako ľubovoľný redirect parameter.

## 8. IdP-initiated browser SSO

Pri IdP-initiated flowe user klikne application tile v IdP portáli a SP dostane unsolicited Response bez svojho `AuthnRequest`.

Chýba transaction ID, ktorý by dokazoval, že konkrétny browser začal login na konkrétnom SP. SP musí preto zvlášť chrániť login CSRF, account confusion, replay a RelayState.

IdP-initiated flow môže byť business requirement pre legacy SaaS, ale má slabší transaction binding. Nemal by sa automaticky povoľovať len preto, že knižnica unsolicited responses akceptuje.

## 9. Web Browser SSO profile

Najbežnejšia kombinácia používa HTTP Redirect pre AuthnRequest a HTTP POST pre Response. Browser je transport medzi IdP a SP, ale sensitive message validity nevychádza z browser trustu.

Flow musí používať TLS na oboch legs. XML Signature poskytuje message integrity/authenticity, ale TLS chráni transport metadata, cookies, credentials na IdP a application session na SP.

Response býva väčšia pre XML, certificates, attributes a encryption, preto sa bežne posiela form POST namiesto URL query.

## 10. HTTP Redirect binding

Redirect binding serializuje SAML message, aplikuje raw DEFLATE podľa binding rules, base64 a URL encoding a prenesie výsledok v query parameters.

Ak sa podpisuje query-level message, signature covers presnú kombináciu encoded `SAMLRequest`/`SAMLResponse`, optional `RelayState` a `SigAlg` v definovanom ordering-u. Framework nesmie parameters dekódovať a znovu serializovať pred verification.

URL size limits a proxy normalization môžu spôsobovať interoperability failures. Redirect binding je preto častejší pre menší AuthnRequest než pre veľkú Response.

## 11. HTTP POST binding

POST binding vloží base64-encoded SAML message do hidden form field-u, typicky `SAMLResponse`, a browser form automaticky odošle na ACS. `RelayState` je samostatné field.

Base64 neposkytuje confidentiality ani integrity. Message môže user dekódovať a meniť; SP musí overiť XML Signature a všetky semantic constraints.

ACS má používať request size limit a nelogovať raw form body, pretože assertion môže obsahovať personal data a reusable authentication artifact.

## 12. HTTP Artifact binding

Artifact binding prenáša cez browser krátky opaque artifact. SP potom cez authenticated back-channel SOAP exchange získa plnú SAML message od IdP.

Výhodou je menší front-channel payload a skrytie assertion pred browserom. Nevýhodou je ďalšia network/TLS/authentication dependency medzi SP a IdP a komplexnejší failure model.

Artifact musí byť single-use, krátkodobý a viazaný na intended requester. Back-channel endpoint a certificate trust patria do metadata contractu.

## 13. Metadata ako trust bootstrap

SAML metadata sú signed alebo out-of-band trusted XML configuration describing federation entity. Môžu obsahovať:

- entity ID;
- SSO a SLO endpoints;
- Assertion Consumer Service endpoints a indexes;
- supported bindings;
- signing a encryption certificates;
- NameID formats;
- validity a cache metadata;
- organization/contact information.

Metadata nie sú iba convenience auto-configuration. Určujú, komu SP dôveruje, kam sa messages posielajú a ktoré keys sa používajú.

User-provided metadata URL nesmie automaticky rozšíriť trust. Bootstrap má určiť authoritative source, metadata signature validation, refresh, certificate rollover a emergency revocation.

## 14. Entity ID

Entity ID je stable federation identifier IdP alebo SP. Často vyzerá ako URL alebo URN, ale nemusí byť browsable endpoint.

SP porovná assertion `Issuer` s configured trusted entity ID. Certificate samotný nestačí na issuer identity: rovnaký key môže byť omylom použitý viacerými entities alebo environments.

Production a test entity IDs majú byť oddelené. Assertion vydaná test IdP nemá byť akceptovaná production SP iba preto, že zdieľajú certificate chain.

## 15. Assertion Consumer Service

ACS je SP endpoint, ktorý prijíma browser-delivered SAML Response a mení federation artifact na local session. Je preto high-risk authentication boundary.

ACS musí:

- používať HTTPS;
- akceptovať iba configured binding a registered endpoint identity;
- používať secure XML parser a bounded payload;
- validovať signature a semantic constraints;
- používať replay cache a transaction state;
- chrániť local session pred fixation a CSRF;
- nelogovať assertion plaintext;
- odmietnuť ambiguous alebo extra unsigned assertions.

Ak je SP za reverse proxy, musí bezpečne rekonštruovať external URL. Attacker-controlled forwarding headers nesmú ovplyvniť recipient/destination validation.

## 16. Subject a NameID

Assertion `Subject` identifikuje principal-a a obsahuje SubjectConfirmation rules. `NameID` je jeden identifier s declared formatom.

Persistent opaque NameID je typicky vhodnejší ako email. Email sa môže zmeniť, recyklovať, líšiť case normalizationom a vytvárať privacy correlation naprieč SPs.

Local identity key má obsahovať issuer/entity context aj external subject identifier:

```text
IdP entity ID + NameID value + NameID format
→ stable federation identity key
```

SP nemá account linkovať iba podľa display emailu bez verified linking processu.

## 17. SubjectConfirmation

Web Browser SSO typicky používa bearer SubjectConfirmation. `SubjectConfirmationData` môže obsahovať:

- `Recipient` — ACS endpoint, kde možno assertion použiť;
- `NotOnOrAfter` — expiry bearer confirmation;
- `InResponseTo` — request ID pri SP-initiated flowe.

SP musí validovať všetky applicable fields. Signature over assertion neznamená, že ju možno použiť na ľubovoľnom endpoint-e alebo opakovane.

Recipient binding a krátke expiry obmedzujú stolen assertion. Replay cache a request state poskytujú ďalšiu vrstvu.

## 18. Conditions

`Conditions` definujú global validity assertion. Najdôležitejšie sú `NotBefore`, `NotOnOrAfter` a `AudienceRestriction`.

`NotOnOrAfter` je exclusive boundary: assertion nie je validná presne v uvedenom čase ani neskôr. Clock-skew tolerance má byť malá a zdokumentovaná, nie vypnutá.

SP má odmietnuť unknown critical condition, ktorú nevie bezpečne interpretovať podľa profile-u. Ignorovanie conditions mení scoped assertion na broad bearer credential.

## 19. AudienceRestriction

Audience určuje intended relying party. SP akceptuje assertion iba ak jeho expected entity ID spĺňa AudienceRestriction podľa agreed semantics.

Valid signature pre audience `https://staging.example/sp` nesmie vytvoriť production session na `https://prod.example/sp`. Audience je protection against token substitution medzi applications a environments.

Audience nie je URL, na ktorú sa message posiela; to riešia Destination a Recipient. Je to logical intended consumer identity.

## 20. Destination, Recipient a ACS URL

`Destination` patrí protocol Response a označuje endpoint, kam bola message adresovaná. `Recipient` patrí bearer SubjectConfirmationData a označuje endpoint, kde možno assertion prezentovať.

Obe hodnoty majú zodpovedať configured external ACS URL podľa profile-u. Porovnávanie musí riešiť scheme, host, port a path presne podľa implementation policy.

Reverse proxy mismatch často spôsobí validáciu proti internal `http://service:8080/acs` namiesto external `https://login.example/acs`. Oprava patrí do trusted proxy configuration, nie do vypnutia recipient validation.

## 21. InResponseTo a transaction state

SP vytvorí high-entropy request ID a uloží ho s expected IdP, ACS, timestampom, requested resource a browser transaction state. Response a SubjectConfirmation ho referencujú cez `InResponseTo`.

SP pri prijatí:

1. nájde non-expired pending request;
2. overí exact match;
3. overí, že response prišla v správnom browser transaction context-e;
4. po successful consumption state atomicky odstráni;
5. odmietne ďalšie použitie.

V clusteri potrebuje state shared store alebo sticky transaction design. Request ID uložené iba na jednom node spôsobí intermittent `unknown InResponseTo`.

## 22. RelayState

RelayState prenáša application state mimo samotnej SAML message, často pôvodnú resource URL. Jeho integrity a confidentiality nie sú automaticky poskytované každým bindingom/profile-om.

Najbezpečnejší model je random server-side handle viazaný na pending request a browser cookie. Ak sa prenáša URL, musí byť allowlisted/relative a chránená pred tamperingom a open redirectom.

RelayState nemá obsahovať secret, token ani personal data. IdP-initiated RelayState potrebuje zvlášť strict destination mapping.

## 23. AuthnStatement

`AuthnStatement` opisuje authentication event: `AuthnInstant`, optional `SessionIndex`, session expiry a `AuthnContext`.

Nevyjadruje automaticky, že authentication je dosť silná pre každú SP operation. SP musí mapovať context na vlastnú assurance policy.

Old IdP session môže umožniť SSO bez fresh user interaction. Pre sensitive operation môže SP požadovať `ForceAuthn`, stricter RequestedAuthnContext alebo local reauthentication podľa federation capabilities.

## 24. Authentication Context

Authentication Context Class Reference je URI označujúca class authentication mechanismu alebo assurance. IdP a SP musia mať shared interpretation.

SP nemá neznámu URI považovať za „aspoň MFA“. RequestedAuthnContext môže používať comparison semantics ako exact/minimum/better/maximum, ale interoperability závisí od IdP implementation a agreed ordering.

Security contract má presne uviesť, ktoré context values znamenajú phishing-resistant, MFA, password-only alebo other assurance. Display label v IdP UI nie je protocol guarantee.

## 25. AttributeStatement

AttributeStatement prenáša named attributes, napríklad employee ID, department, group, tenant alebo role. Každý attribute má Name, optional NameFormat a jednu alebo viac values.

SP potrebuje explicitný contract:

```text
SAML attribute Name/NameFormat
→ expected XML value type a cardinality
→ normalization
→ local identity field alebo entitlement input
→ authorization policy
```

Attribute prítomnosť nie je automaticky dôveryhodná pre admin permission. Dôležité je, či IdP číta hodnotu z authoritative source, ako rýchlo sa deprovisionuje a či federation partner smie daný entitlement vydávať.

## 26. Attribute governance

Pre každý attribute definuj:

- authoritative source;
- required/optional status;
- single alebo multi-value semantics;
- case, Unicode a whitespace normalization;
- maximum count a size;
- privacy purpose a minimization;
- stale-data/deprovisioning latency;
- allowed values a mapping owner;
- behavior pri missing alebo duplicate value.

Group list môže byť truncated alebo príliš veľký. Privileged role nemá byť derived z arbitrary display stringu alebo email domainu.

SP local authorization má používať normalized, allowlisted claims a auditovať mapping revision.

## 27. XML Signature model

XML Signature podpisuje selected XML element reference, nie automaticky celý parsed document. Verification zahŕňa reference URI resolution, canonicalization, digest validation a signature verification proti trusted keyu.

Bezpečný SAML implementation musí:

- používať key z trusted metadata, nie embedded untrusted certificate ako nový trust root;
- registrovať ID attributes bezpečným spôsobom;
- odmietnuť duplicate IDs;
- overiť expected signed element;
- spracovať presne element, ktorý verification vrátila ako signed;
- zakázať weak algorithms a external references;
- nepoužívať custom ad hoc XML signature code.

Cryptographic success bez application bindingu k signed node-u je nedostatočný.

## 28. XML Signature Wrapping

Wrapping attack vloží alebo premiestni XML elements tak, aby signature library overila benign signed assertion, ale application spracovala attacker-controlled unsigned assertion na inom XPath location.

Mitigation je structural, nie iba cryptographic:

```text
parse secure schema/profile shape
→ resolve unique signed element by verified ID
→ reject duplicate/extra assertions a ambiguous nesting
→ pass verified element directly to claims processing
```

Library musí byť SAML-aware a maintained. Generic XML parser + ručný XPath je vysoké riziko.

## 29. Secure XML processing

XML parser na ACS spracúva attacker-controlled input. Zakáž DTD, external entities, external schema/resource resolution a unsafe entity expansion. Nastav size, depth, attribute a element count limits.

XXE môže čítať local files alebo volať internal services. Billion Laughs/entity expansion môže spôsobiť DoS. Oversized base64/XML môže vyčerpať memory ešte pred signature validation.

Schema validation pomáha, ale nesmie načítavať remote schemas pri requeste. Použi locally pinned schemas a profile-specific structural checks.

## 30. XML Encryption

Assertion alebo selected elements môžu byť encrypted pre SP public key. IdP encryptuje content a SP používa private decryption key.

XML Encryption poskytuje front-channel confidentiality nad rámec base64 a môže chrániť attributes pred browserom alebo intermediaries. Nenahrádza TLS, pretože TLS chráni cookies, endpoints a surrounding transport.

Signing a encryption keys majú odlišný purpose a lifecycle. Encryption certificate rollover musí byť koordinovaný tak, aby IdP nezačal encryptovať novým keyom skôr, než všetky SP nodes majú private key.

Po decryption musí SP stále vykonať signature a semantic validation. „Dalo sa decryptovať“ nie je authentication proof.

## 31. Certificate a key trust model

SAML metadata často používajú X.509 certificates ako containers public keys. Trust typicky nevychádza z Web PKI hostname validation; SP explicitne dôveruje keys publikovaným trusted metadata entity.

Certificate expiry môže byť relevantná podľa library/policy, ale federation trust lifecycle sa riadi metadata validity a rollover contractom. Nepredpokladaj, že rovnaké rules ako browser TLS sa aplikujú automaticky.

Bezpečný signing rollover:

1. IdP publikuje nový aj starý verification key v metadata;
2. SPs metadata načítajú a potvrdia;
3. IdP začne podpisovať novým keyom;
4. monitoring sleduje failures;
5. starý key sa odstráni po bounded overlap;
6. emergency process existuje pre compromise.

## 32. Clock a time validation

SAML používa krátke validity windows a `IssueInstant`, `NotBefore`, `NotOnOrAfter`, SubjectConfirmation expiry a request expiration.

IdP aj SP potrebujú reliable time synchronization a monitoring clock offsetu. Logs majú používať UTC a zachytiť local receive time aj message timestamps.

Veľká skew tolerance zvyšuje replay window. Zero tolerance môže spôsobovať outages pre malé network/clock differences. Policy má byť bounded a testovaná.

## 33. Replay protection

SP ukladá consumed Response IDs a Assertion IDs minimálne do konca ich validity plus small safety interval. Duplicate ID sa odmietne.

SP-initiated flow navyše atomicky spotrebuje pending request ID. Replay cache v HA deployment-e musí byť shared alebo consistent pre všetky ACS nodes.

Cache potrebuje tenant/issuer separation, expiry a bounded storage. Pri cache outage má high-risk login typicky fail-closed; inak attacker môže využiť práve unavailable replay control.

## 34. Local identity a session

Po successful SAML validation SP mapuje issuer + NameID a attributes na local account. JIT provisioning môže account vytvoriť, ale potrebuje duplicate prevention, allowed tenant a lifecycle ownera.

SP potom vytvorí vlastnú session cookie s Secure, HttpOnly a appropriate SameSite, regeneruje session ID a nastaví idle/absolute timeout. Assertion sa nemá používať ako opakovane prezentovaný application bearer token.

Local session môže prežiť IdP session alebo SAML assertion expiry. SP preto potrebuje vlastnú revocation, risk re-evaluation a reauthentication pre sensitive actions.

## 35. SAML authentication oproti authorization

SAML úspešne odpovie, kto user je a ktoré attributes IdP vydal. Application stále rozhoduje, či user smie čítať invoice, meniť production alebo spravovať tenant.

```text
validated assertion
→ external subject identity
→ local account/link
→ normalized attributes
→ local roles/policies
→ resource-level authorization
```

Priamy mapping broad IdP groupu na application admin rolu vytvára federation-wide privilege path. Mapping má byť explicitný, versionovaný a auditovaný.

## 36. Single Logout

SAML Single Logout používa `LogoutRequest`, `LogoutResponse`, NameID a optional SessionIndex na koordináciu IdP a SP sessions cez front alebo back channel.

SLO nie je atomic distributed transaction. Niektorý SP môže byť unavailable, browser môže blokovať front-channel request, session index môže chýbať a local API tokens môžu mať vlastný lifecycle.

SP musí vždy vedieť ukončiť local session nezávisle. Security incident nemá spoliehať iba na „global logout succeeded“ UI status; treba revoke-nuť relevantné local sessions a downstream tokens.

## 37. Federation discovery a multi-tenant trust

V multi-IdP SP musí vybrať správny trust configuration. Routing môže používať tenant-specific URL, organization selection alebo verified domain mapping.

Email domain je routing hint, nie proof organization. User-provided entity ID alebo metadata URL nesmie automaticky vytvoriť trusted issuer.

Každý tenant trust má oddelené entity IDs, keys, attribute contract, assurance mapping a account-linking boundary. Assertion jedného tenant IdP nesmie provisionovať account v inom tenantovi podľa rovnakého emailu.

## 38. Federation contract

Technická metadata konfigurácia je iba časť contractu. Production federation agreement má definovať:

- entity IDs, endpoints a bindings;
- signing/encryption requirements;
- supported key rollover process;
- required NameID format;
- attribute names, types a authorities;
- authentication assurance semantics;
- clock/skew a replay policy;
- provisioning/deprovisioning latency;
- incident contacts a emergency key removal;
- logging, privacy a data retention;
- test a change-management process.

Cryptographically valid assertion môže porušiť business contract, napríklad obsahovať admin role od partnera, ktorý ju nesmie vydávať.

## 39. SAML oproti OpenID Connect

SAML používa XML assertions, browser bindings a XML metadata. OIDC používa OAuth 2.0 endpoints, JSON/JWT ID Tokens, discovery a JWKS.

SAML zostáva bežný pri enterprise SaaS a established workforce federation. OIDC lepšie zapadá do moderných web/native clients a API ecosystemu.

Bezpečnosť závisí od implementation a configuration. XML nie je automaticky menej bezpečné než JWT; má však odlišnú parser, canonicalization a signature-wrapping attack surface.

## 40. Observability

Sleduj protocol stage, nie iba „SSO failed“:

- AuthnRequest creation a redirect;
- IdP response status;
- parse/schema failures;
- signature/key/certificate failures;
- issuer, audience, recipient a destination failures;
- clock-skew a expiry;
- unknown `InResponseTo` a replay detection;
- NameID/account-linking failures;
- attribute mapping/JIT provisioning;
- local session creation;
- metadata refresh a key rollover;
- SLO partial failures.

Použi request/response IDs a redacted issuer/SP labels. Neloguj raw assertion, SAMLResponse form field ani sensitive attributes.

## 41. Troubleshooting flow

```text
SP entity ID a metadata?
→ AuthnRequest destination, binding a request state?
→ IdP authentication a response Status?
→ browser POST na správny ACS?
→ base64/XML parse a secure schema?
→ expected signing key a signed element?
→ issuer a audience?
→ destination a recipient?
→ time conditions?
→ InResponseTo a replay cache?
→ NameID/attribute mapping?
→ local session cookie a authorization?
```

Pri `invalid signature` najprv over key rollover a actual signed element, nie iba certificate expiry. Pri recipient mismatch over proxy external URL. Pri unknown request over shared transaction store a SameSite/cookie behavior.

Login loop môže vzniknúť po successful SAML authentication, keď local authorization odmietne usera alebo session cookie sa neuloží. Rozlišuj protocol success od application session success.

## 42. Incident response

Pri IdP signing-key compromise:

```text
identifikovať entity a key
→ zastaviť trust k compromised keyu
→ publikovať/načítať emergency metadata
→ posúdiť assertions z exposure intervalu
→ revoke-nuť local sessions podľa risku
→ monitorovať replay a anomalous provisioning
→ zaviesť nový key s controlled rollover
→ koordinovať všetkých federation partners
```

Pri attribute-source compromise analyzuj authorization impact: attacker mohol vydávať admin/group claims aj s validnou signature.

Pri SP decryption-key compromise posúď captured encrypted assertions a rotate encryption key. Pri ACS vulnerability izoluj endpoint a zachovaj raw malicious samples bezpečne mimo bežných logs.

## 43. Časté anti-patterny

**Base64 decode považovaný za authentication.** Payload je attacker-controlled, kým neprejde komplet validation.

**Valid signature = valid login.** Chýba issuer, audience, recipient, time, request a replay validation.

**Email ako global identity key.** Zmena alebo recyklácia spojí nesprávne accounts.

**Embedded certificate ako trust root.** Attacker pošle assertion podpísanú vlastným keyom aj vlastný certificate.

**Generic XPath po signature verification.** Application môže spracovať unsigned wrapped assertion.

**IdP-initiated login bez transaction threat modelu.** Login CSRF a account confusion ostávajú.

**Attributes priamo ako admin permissions.** Chýba authority, mapping a deprovisioning governance.

**SLO ako spoľahlivá global revocation.** Partial failures nechajú local sessions aktívne.

**Vypnutá destination/recipient validation za proxy.** Misconfiguration sa „opraví“ odstránením security bindingu.

## 44. Kompletný production príklad

Enterprise user otvorí `https://expenses.example/reports`.

1. SP vytvorí random AuthnRequest ID, uloží return path server-side a presmeruje na configured workforce IdP.
2. IdP overí signed request/registered ACS podľa contractu a autentizuje usera phishing-resistant MFA.
3. IdP vydá Response s Assertion, persistent opaque NameID, employee ID a department attribute. Assertion je určená audience SP entity ID a bearer Recipient exact ACS.
4. Browser POSTne Response cez TLS.
5. ACS použije secure XML parser, overí expected signed assertion key z metadata a spracuje presne signed element.
6. SP overí issuer, audience, destination, recipient, time, `InResponseTo` a uniqueness Response/Assertion IDs.
7. Identity key `issuer + NameID` nájde local account. Department sa normalizuje, ale admin entitlement sa odvodzuje z separate allowlisted group contractu.
8. SP atomicky spotrebuje request state, regeneruje session ID a nastaví secure cookie.
9. Application vykoná local resource authorization pre konkrétny expense report.
10. Audit spojí request ID, assertion ID, IdP entity, local user, authentication context a authorization result bez uloženia raw assertion.

## 45. Kontrolné otázky

1. Aký je rozdiel medzi assertion, protocol, binding, profile a metadata?
2. Prečo browser nie je trusted SAML participant?
3. Ako sa Response líši od Assertion?
4. Čo vytvára SP-initiated transaction binding?
5. Aké additional risks má IdP-initiated flow?
6. Ako fungujú Redirect, POST a Artifact binding?
7. Prečo metadata predstavujú trust bootstrap?
8. Čo je entity ID a prečo certificate sám nestačí?
9. Ako sa NameID má mapovať na local identity?
10. Akú úlohu má SubjectConfirmation?
11. Ako sa audience, destination a recipient líšia?
12. Ako `InResponseTo` a replay cache spolupracujú?
13. Prečo RelayState môže vytvoriť login CSRF alebo open redirect?
14. Čo AuthnContext dokazuje a čo musí byť dohodnuté?
15. Ako sa attributes menia na local authorization inputs?
16. Ako funguje XML Signature Wrapping?
17. Prečo embedded signing certificate nesmie vytvoriť trust?
18. Ako bezpečne vykonať signing/encryption key rollover?
19. Prečo SLO nie je úplná session revocation?
20. Navrhni kompletnú validation pipeline SAML Response.

## Glossary impact

Relevantné pojmy: SAML, principal, Identity Provider, Service Provider, SAML assertion, SAML Response, AuthnRequest, SAML protocol, SAML binding, SAML profile, Web Browser SSO profile, HTTP Redirect binding, HTTP POST binding, HTTP Artifact binding, SAML metadata, entity ID, Assertion Consumer Service, NameID, SubjectConfirmation, Conditions, AudienceRestriction, Destination, Recipient, InResponseTo, RelayState, AuthnStatement, Authentication Context, AttributeStatement, XML Signature, XML Signature Wrapping, XML Encryption, SAML certificate rollover, replay cache, local application session, Single Logout, federation discovery a federation contract.

## Primárne zdroje

- [OASIS SAML V2.0 standard documents](https://docs.oasis-open.org/security/saml/v2.0/)
- [SAML V2.0 Core](https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf)
- [SAML V2.0 Bindings](https://docs.oasis-open.org/security/saml/v2.0/saml-bindings-2.0-os.pdf)
- [SAML V2.0 Profiles](https://docs.oasis-open.org/security/saml/v2.0/saml-profiles-2.0-os.pdf)
- [SAML V2.0 Metadata](https://docs.oasis-open.org/security/saml/v2.0/saml-metadata-2.0-os.pdf)
- [SAML V2.0 Authentication Context](https://docs.oasis-open.org/security/saml/v2.0/saml-authn-context-2.0-os.pdf)
- [OASIS SAML V2.0 Technical Overview](https://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0-cd-02.html)
- [OWASP SAML Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SAML_Security_Cheat_Sheet.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OpenID Connect](openid-connect.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Secrets management →](secrets-management.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
