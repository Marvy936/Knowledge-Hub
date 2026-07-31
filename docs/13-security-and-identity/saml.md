# SAML

Security Assertion Markup Language 2.0 — SAML — je XML-based federation framework. Identity Provider autentizuje principal-a a vydá Response alebo Assertion pre konkrétneho Service Providera. Service Provider vytvorí local application session až po cryptographic, structural, semantic a transaction validation.

SAML signature nepotvrdzuje, že „používateľ je dôveryhodný“. Potvrdzuje iba, že konkrétny signed XML element vytvoril držiteľ trusted signing keyu a nebol po podpise zmenený. Service Provider musí navyše overiť exact entity/issuer, audience, destination, recipient, time conditions, request binding, replay, subject mapping, attribute authority a local resource authorization.

## Metadata-to-session lifecycle

SAML session je dôveryhodná iba vtedy, keď metadata, signed XML node a pending transaction opisujú rovnaký issuer, SP a ACS boundary. Lifecycle preto oddeľuje key trust, XML validation, semantic checks a local session creation.

```text
federation contract a metadata generation
→ IdP/SP entity IDs, endpoints, bindings a keys
→ AuthnRequest a pending transaction
→ IdP authentication a attribute projection
→ signed Response alebo Assertion
→ browser binding a ACS delivery
→ secure XML parse a signed-node validation
→ issuer, audience, destination, recipient, time a replay
→ NameID/attribute mapping
→ local session a resource authorization
→ logout, key rollover, revocation a second-session validation
```

Valid XML, trusted certificate a HTTP success sú iba medzistavy. Acceptance vznikne až vtedy, keď SP spracuje presne signed node určený pre jeho entity a transaction a následne vykoná local authorization.

## Exact SAML subject SEC-PAY-49

Subject viaže Response a Assertion na exact entity IDs, ACS, request ID, metadata generation a key purpose. Tým bráni tomu, aby certificate thumbprint alebo shared ACS nahradili production federation contract.

```yaml
incident: SEC-PAY-49
idpEntityId: https://id.atlas.example/saml/production
stagingEntityId: https://id.staging.atlas.example/saml/staging
spEntityId: https://admin.atlas.example/saml
acs: https://admin.atlas.example/saml/acs
binding: HTTP-POST
requestId: _REQ-884
responseId: _RESP-884
assertionId: _ASSERT-884
nameIdFormat: persistent
sharedSigningKey: FED-SIGN-07
expectedMetadataGeneration: SAML-META-44
forbidden:
  - unsolicited-privileged-response
  - wrong-destination
  - staging-issuer
  - direct-role-attribute-to-admin
```

Subject viaže assertion na federation metadata a pending request. Thumbprint bez entity metadata nepreukazuje, ktorý IdP a purpose smie key reprezentovať.

## Metadata je trust contract

SAML metadata publikuje entity ID, SSO/SLO endpoints, supported bindings, signing/encryption certificates a validity. SP nemá dôverovať certificate-u izolovane od entity a metadata source-u. Rovnaký key použitý pre staging a production zničí environment boundary aj pri platnej signature.

```bash
curl -fsS https://id.atlas.example/saml/production/metadata \
  -o /tmp/idp-production-metadata.xml

grep -E 'entityID=|SingleSignOnService|KeyDescriptor' \
  /tmp/idp-production-metadata.xml
```

Výstup preukazuje metadata dostupné z endpointu. Nepreukazuje, že SP načítal rovnakú generation, metadata bola podpísaná alebo získaná cez approved trust channel, certificate je current alebo runtime verifier odmietne staging entity.

Certificate z metadata sa kontroluje ako identity a lifecycle artifact:

```bash
openssl x509 -in /tmp/idp-signing.pem -noout \
  -subject -issuer -serial -fingerprint -sha256 -dates
```

Výstup preukazuje properties konkrétneho certificate file-u. Nepreukazuje private-key custody, authorization key-u pre exact entity, loaded verifier trust ani successful signed-node validation.

## SP-initiated a IdP-initiated SSO

SP-initiated flow vytvorí AuthnRequest s unique ID, ACS, requested context a transaction state. Response potom musí byť viazaná cez `InResponseTo` na pending request. To obmedzuje unsolicited response a mix-up medzi transactions.

IdP-initiated flow začína bez AuthnRequestu. Môže byť funkčne potrebný pre legacy applications, ale nemá request binding a vyžaduje prísnejší replay, issuer, audience, destination a session policy. Privileged admin application by nemala prijímať unsolicited assertion len preto, že signature sedí.

RelayState nesie application navigation state, nie authorization. Musí byť integrity-protected, bounded a viazaný na transaction. Open redirect alebo untrusted URL v RelayState môže presmerovať usera po login-e na attacker-controlled destination.

## Secure XML parsing a signature validation

SAML processing musí vypnúť external entities a nebezpečné DTD behavior, používať schema-aware parser podľa library contractu a validovať signature nad elementom, ktorý application následne skutočne spracuje. XML Signature Wrapping využíva rozdiel medzi signed node-om a node-om vybraným business logicou.

Simplified assertion shape:

```xml
<samlp:Response ID="_RESP-884" Destination="https://admin.atlas.example/saml/acs">
  <saml:Issuer>https://id.atlas.example/saml/production</saml:Issuer>
  <ds:Signature>...</ds:Signature>
  <saml:Assertion ID="_ASSERT-884">
    <saml:Issuer>https://id.atlas.example/saml/production</saml:Issuer>
    <saml:Subject>
      <saml:NameID>248c16a9-3ea0-4f2a-8a17-f9a88421c0aa</saml:NameID>
      <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
        <saml:SubjectConfirmationData
          Recipient="https://admin.atlas.example/saml/acs"
          InResponseTo="_REQ-884"
          NotOnOrAfter="2026-07-29T12:20:00Z" />
      </saml:SubjectConfirmation>
    </saml:Subject>
    <saml:Conditions NotBefore="2026-07-29T12:14:00Z" NotOnOrAfter="2026-07-29T12:20:00Z">
      <saml:AudienceRestriction>
        <saml:Audience>https://admin.atlas.example/saml</saml:Audience>
      </saml:AudienceRestriction>
    </saml:Conditions>
  </saml:Assertion>
</samlp:Response>
```

Example vysvetľuje semantic fields, nie complete production assertion. Signature verification musí potvrdiť reference URI, unique IDs, transforms, canonicalization a trusted key; application potom používa presne verified Assertion/Response object.

## Issuer, audience, destination a recipient

Issuer musí presne zodpovedať trusted IdP entity. Audience musí obsahovať exact SP entity. Response `Destination` a SubjectConfirmationData `Recipient` musia zodpovedať canonical ACS. Reverse proxy alebo alternate hostname sa rieši správnou external URL configuration, nie vypnutím checks.

Time validation zahŕňa `NotBefore`, `NotOnOrAfter` a bounded clock skew. Predĺženie skew na desiatky minút kvôli zlému NTP zväčší replay window. Replay cache ukladá Response/Assertion IDs aspoň počas validity a musí byť zdieľaná naprieč SP replicas.

## NameID, attributes a local identity

NameID format určuje semantics identifiera. Email alebo transient display value nie je stabilný identity key, pokiaľ federation contract explicitne negarantuje jeho uniqueness a lifecycle. Application mapuje external identity cez `entityID + persistent NameID` alebo iný immutable contract.

Attributes majú authority a projection scope. IdP group alebo `Role=Admin` nie je automaticky local admin entitlement. SP potrebuje allowlist attribute source-u, client-specific mapping a current resource authorization. Attribute names, formats a multi-value behavior musia byť versionované; first-value wins môže vytvoriť ambiguity alebo bypass.

## Signing a encryption keys

Signing poskytuje authenticity a integrity assertionu. XML encryption chráni confidentiality assertionu na browser/front-channel path-e, ale nepridáva authorization. Key reuse medzi signing a encryption, medzi staging/production alebo OIDC/SAML zväčšuje blast radius a komplikuje revocation.

Rollover má overlap: metadata publikuje old a new verification keys, signer prejde na new, SP loaded state sa overí a old trust sa odstráni až po bounded assertion/session window. Certificate expiry date nie je celý rotation plan; metadata cache a SP reload behavior sú samostatné boundaries.

## Session a Single Logout

SP session je lokálna a môže prežiť IdP session. SAML Single Logout je distribuovaný best-effort workflow cez viac SPs a browser/server paths. Jedna nedostupná aplikácia môže logout chain prerušiť. High-risk revocation preto nemá spoliehať iba na front-channel SLO; používa short sessions, local revocation a downstream token/session inventory.

## Incident SEC-PAY-49

Key `FED-SIGN-07` sa používal pre staging aj production a pre OIDC aj SAML. Staging debug principal získal private key cez Kubernetes workload projection. Production SAML SP dôveroval certificate thumbprintu bez exact metadata entity bindingu, povoľoval IdP-initiated response pre privileged console a mal vypnuté Destination/Recipient checks kvôli proxy mismatchu. Attribute `Role=Admin` mapoval priamo na local admin.

Attacker podpísal staging assertion shared keyom, nastavil production audience a admin attribute a doručil ju na shared ACS. Signature bola validná. SP však neoveril trusted production issuer/entity contract ani transaction binding. Root cause bol shared exportable key a key-centric trust; unsolicited flow, disabled destination checks a direct role mapping boli amplifiers.

Competing hypotheses zahŕňali stolen production session, compromised production IdP, XML wrapping, metadata cache poisoning, shared key a local mapping defect. Assertion issuer, signature key lineage, absent `InResponseTo`, verifier configuration a Kubernetes audit ukázali shared-key wrong-entity path.

## Containment a authoritative recovery

Containment vypne privileged unsolicited flow, zablokuje shared key/entity combination, revoke-ne affected SP sessions a zachová raw assertion, verified-node identity, metadata generations, verifier logs, account mapping a application audit. XML artifact sa ukladá ako sensitive evidence a nesmie sa zobrazovať v bežných logs.

Recovery vytvorí oddelené non-exportable keys pre staging/production a OIDC/SAML purpose, obnoví exact metadata entity trust, SP-initiated transaction pre privileged access, Destination/Recipient/InResponseTo checks a allowlisted attribute mapping. Proxy canonical URL sa opraví namiesto vypnutých validations. Coordinated rollover overí loaded metadata na každej SP replica.

Acceptance vyžaduje successful production SP-initiated login, deny pre staging issuer s cryptographically validným keyom, deny pre unsolicited privileged assertion, wrong destination, reused assertion ID a unapproved Role attribute. Existing sessions z old trustu musia byť revoke-nuté. Druhý key rollover musí prejsť bez cross-environment alebo cross-protocol reuse.

## Kontrolné otázky

1. Prečo certificate thumbprint bez entity metadata nie je úplný trust contract?
2. Ako sa SP-initiated a IdP-initiated flow líšia v transaction bindingu?
3. Čo je XML Signature Wrapping a ako mu bráni signed-node validation?
4. Prečo vypnutie Destination checku kvôli proxy problému nie je bezpečná oprava?
5. Ako NameID a attribute authority ovplyvnia local identity?
6. Prečo SLO nie je spoľahlivá globálna revocation?
7. Ktoré tests odlišia validnú signature od správnej production federation?

## Referencie

- [SAML 2.0 Technical Overview](https://docs.oasis-open.org/security/saml/Post2.0/sstc-saml-tech-overview-2.0.html)
- [SAML 2.0 Profiles](https://docs.oasis-open.org/security/saml/v2.0/saml-profiles-2.0-os.pdf)
- [SAML 2.0 Metadata](https://docs.oasis-open.org/security/saml/v2.0/saml-metadata-2.0-os.pdf)
- [OWASP SAML Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SAML_Security_Cheat_Sheet.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OpenID Connect](openid-connect.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Secrets management →](secrets-management.md)
<!-- KNOWLEDGE-NAVIGATION:END -->