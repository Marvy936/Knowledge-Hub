# Authentication, authorization a auditing

Authentication, authorization a auditing sú tri rozdielne bezpečnostné funkcie, ktoré spolu tvoria jeden access lifecycle. Authentication vytvorí dôveryhodný kontext o principalovi, authorization rozhodne o konkrétnej operácii a auditing zachová evidence o tom, ako rozhodnutie vzniklo a čo systém skutočne vykonal. Ak sa tieto vrstvy zlúčia do jednej neurčitej predstavy „používateľ je prihlásený“, systém typicky povoľuje príliš veľa, nevie korektne revoke-nuť access a po incidente nedokáže vysvetliť udalosti.

## 1. Mentálny model celého access lifecycle-u

```text
identity proofing a enrollment
→ account a credential issuance
→ authentication request
→ session alebo token
→ authorization decision
→ enforcement pri resource boundary
→ audit event a telemetry
→ review, revocation a recovery
```

Každý krok rieši inú otázku. Identity proofing zisťuje, komu má digitálna identita patriť. Authentication overuje, kto alebo čo predkladá request a akú assurance má toto tvrdenie. Authorization vyhodnocuje konkrétnu action voči konkrétnemu resource-u. Auditing zaznamenáva actora, context, decision a výsledok tak, aby sa dali neskôr overiť.

Dôležitý dôsledok je, že silná jedna vrstva neopraví chybu v inej. Phishing-resistant MFA nepomôže, ak bol účet pri enrollment-e priradený nesprávnej osobe. Platne podpísaný token nepomôže, ak API nekontroluje tenant ownership. Detailný audit nepomôže, ak workload môže vlastné logy prepísať.

## 2. Identity, account, subject, principal a credential

Tieto pojmy sa často zamieňajú, hoci označujú rôzne vrstvy modelu.

- **Identity** je reprezentácia osoby, workloadu, zariadenia alebo organizácie.
- **Account** je administratívny záznam identity v konkrétnom systéme.
- **Subject** je entita, ktorá sa pokúša vykonať operáciu.
- **Principal** je security identita, ktorú systém používa pri authentication alebo authorization.
- **Credential** je secret, key, token alebo iný dôkaz naviazaný na principal.
- **Authenticator** je mechanizmus alebo zariadenie, ktorým claimant preukazuje kontrolu nad credentialom.

Jedna osoba môže mať bežný účet, privilegovaný účet, lokálny application account a federovaný principal. Jeden workload môže súčasne používať Kubernetes ServiceAccount, cloud role a database usera. Preto audit a authorization nesmú identity korelovať iba podľa display name-u alebo emailu. Potrebujú stabilný issuer, subject, account ID alebo inú explicitnú väzbu.

## 3. Identity proofing a enrollment

Identity proofing je proces, ktorým sa overuje, komu má byť digitálna identita pridelená. Enrollment potom túto identitu spojí s accountom a authenticatorom. Authentication prebieha až pri neskoršom používaní.

```text
HR alebo registračný proces overí osobu
→ identity platforma vytvorí account
→ používateľ zaregistruje authenticator
→ authenticator sa naviaže na konkrétny principal
→ neskôr sa vykonáva authentication
```

Ak helpdesk pri recovery priradí nový authenticator útočníkovi, následné MFA bude cryptographically správne, ale dokazuje kontrolu nad nesprávne prideleným accountom. Enrollment, reset a recovery preto potrebujú vlastnú assurance, audit a separation of duties.

NIST Digital Identity Guidelines rozlišujú Identity Assurance Level, Authentication Assurance Level a Federation Assurance Level. Tieto úrovne sa nevyberajú podľa prestíže technológie, ale podľa rizika nesprávneho identity proofingu, kompromitácie authenticatora a federovaného assertion flowu.

## 4. Authentication ako dôkaz kontroly

Authentication odpovedá:

```text
Ktorý principal predkladá request,
aký authenticator kontroluje
a akú mieru dôvery má výsledok?
```

Password je knowledge factor. Security key alebo telefón môže byť possession factor. Biometria je inherence factor, ale často iba lokálne odomyká zariadenie, ktoré potom používa cryptographic key. Contextual signals, napríklad location alebo device risk, môžu rozhodnutie doplniť, no samy nemusia byť samostatným authentication faktorom.

Dva knowledge secrets nie sú skutočné multi-factor authentication. Password a security question zlyhávajú podobným spôsobom. MFA má zmysel vtedy, keď faktory majú odlišné compromise boundaries.

Phishing-resistant authentication navyše viaže cryptographic operation na legitímny verifier alebo origin. FIDO2/WebAuthn authenticator napríklad podpisuje challenge pre konkrétny relying-party identifier. Používateľ preto nemôže jednoduchým prepísaním OTP do phishing stránky autorizovať session pre inú doménu.

## 5. Human a workload authentication

Human authentication rieši interaktívneho používateľa, recovery, phishing a session theft. Workload authentication rieši non-human process, jeho runtime context a automatickú rotation.

Human mechanizmy zahŕňajú password s MFA, passkeys, smart cards a federation. Workload mechanizmy zahŕňajú cloud workload identities, mTLS certificates, Kubernetes projected ServiceAccount tokens, SPIFFE identities alebo Kerberos service principals.

Workload nemá používať osobný účet developera. Taký účet má nesprávny lifecycle, môže byť blokovaný pri odchode človeka, vytvára nejasný audit a zväčša má širšie permissions než konkrétna služba potrebuje. Preferovaný model je krátkodobá platformou vydaná identity viazaná na repository, namespace, service account, node alebo inú runtime boundary.

## 6. Credential lifecycle

Credential nie je statická hodnota, ale objekt s lifecycle-om:

```text
enrollment alebo generation
→ issuance
→ activation
→ storage a use
→ renewal alebo rotation
→ suspension
→ revocation
→ recovery
→ destruction
```

Pri každej fáze treba vedieť, kto ju smie vykonať, kde sa private material nachádza, ako dlho je credential platný a ako rýchlo sa zneplatnenie rozšíri ku všetkým verifierom.

Credential compromise sa nevyrieši iba zmenou passwordu. Aktívne session cookies, refresh tokens, API keys, certificates alebo delegated grants môžu zostať použiteľné. Incident response preto potrebuje inventory všetkých artifacts odvodených z pôvodného credentialu.

## 7. Authentication event, session a token nie sú to isté

Authentication event je okamih, keď verifier akceptuje dôkaz. Session je dlhšie trvajúci lokálny security context. Token je prenosný artifact s claims alebo reference na serverový stav.

```text
authentication event
→ vytvorí session alebo vydá token
→ session/token sa používa pri ďalších requestoch
→ authorization sa vyhodnocuje opakovane
```

ID Token potvrdzuje OIDC authentication event pre clienta. Access token je určený resource serveru. Refresh token umožňuje vydávať ďalšie access tokens. Kerberos ticket reprezentuje ticket-based session key a principal context. API key býva dlhodobejší bearer credential bez samostatného user authentication eventu.

Session potrebuje idle a absolute timeout, secure storage, replay ochranu, revocation, step-up model a jednoznačné logout semantics. „Authenticated once“ nesmie znamenať „trusted forever“.

## 8. Step-up a reauthentication

Nie každá operácia potrebuje rovnakú assurance. Čítanie interného dashboardu môže akceptovať existujúcu session, zatiaľ čo zmena bankového účtu, vydanie production credentialu alebo deaktivácia auditu môže vyžadovať čerstvú phishing-resistant authentication.

Step-up zvýši požadovanú assurance v konkrétnom bode. Reauthentication overí používateľa znovu, často s podmienkou maximálneho veku predchádzajúcej authentication. Systém musí zachovať, ktorá metóda bola použitá, kedy prebehla a na aký sensitive action sa vzťahovala.

## 9. Authorization ako rozhodnutie nad operáciou

Authorization odpovedá:

```text
Smie principal P
vykonať action A
voči resource R
v context-e C?
```

Formálne:

```text
allow = policy(principal, action, resource, context)
```

Context môže obsahovať role, groups, resource ownership, tenant, environment, time, device posture, session assurance, approval state alebo data classification. Platný principal je iba jeden input. Authorization musí stále určiť, či tento principal smie vykonať práve túto operáciu.

Príklad: access token môže povoľovať `orders.read`, ale API musí ešte overiť, že objednávka patrí rovnakému tenantovi a že používateľ má access k danému customer accountu. Inak vzniká object-level authorization chyba, často označovaná ako IDOR alebo BOLA.

## 10. Authorization models a ich úloha

ACL viaže permissions priamo na resource a principals. RBAC zoskupuje permissions do roles. ABAC používa attributes principalu, resource-u a environmentu. Relationship-based model vyhodnocuje väzby ako owner, parent, member alebo delegated administrator.

Tieto modely sa nevylučujú. Cloud systém môže použiť RBAC role na základnú capability, resource policy na cross-account access, ABAC condition na tags a explicitný deny z organizačného guardrailu. Výsledné oprávnenie vzniká až z evaluation semantics všetkých vrstiev.

## 11. Policy administration, decision, information a enforcement

Policy systém možno rozložiť na štyri logické komponenty:

- **Policy Administration Point (PAP)** spravuje policy, jej revision, rollout a lifecycle.
- **Policy Decision Point (PDP)** vyhodnocuje request a vracia decision.
- **Policy Information Point (PIP)** poskytuje attributes a supporting data.
- **Policy Enforcement Point (PEP)** zachytí operáciu a presadí výsledok.

Toto rozdelenie pomáha pri diagnostike. Nesprávny allow môže vzniknúť zlou policy v PAP, stale group membershipom z PIP, chybnou evaluation v PDP alebo bypassom PEP. Bez tohto modelu sa všetky chyby označia neurčito ako „RBAC problém“.

## 12. Enforcement musí byť pri skutočnej boundary

UI, ktoré skryje tlačidlo, nie je authorization control. Útočník môže zavolať API priamo. API gateway môže overiť token, ale backend stále musí kontrolovať resource ownership. Kubernetes admission môže odmietnuť chybný manifest, ale nekontroluje každé neskoršie API alebo data-plane volanie.

PEP musí byť na ceste ku chránenej operácii a nesmie existovať jednoduchý alternate path. Ak služba dôveruje identity headers od gatewaya, musí odstrániť rovnaké headers z untrusted requestu a prijať ich iba z autentizovaného proxy spojenia.

## 13. Default deny, explicit deny a combining semantics

Default deny znamená, že neznámy alebo neúplný prípad sa nepovolí bez explicitného allow. Neurčuje však, ako sa kombinujú viaceré policies.

Niektoré platformy používajú additive allow. Iné používajú explicit deny, ktorý prevažuje nad allow. Ďalšie počítajú intersection identity policy, permissions boundary a organization guardrail. Pri troubleshooting preto treba poznať konkrétny evaluation model, inheritance, priority a cache semantics.

## 14. Federation presúva authentication, nie resource authorization

Federation umožňuje relying party dôverovať assertionu od Identity Providera. Trust contract zahŕňa issuer, audience, signing keys, protocol, claims, assurance, lifetime a key rotation.

Po úspešnej federácii aplikácia stále musí mapovať external identity na local principal a vykonať vlastnú authorization. Group alebo role claim z IdP nie je automaticky vhodný ako application permission. Potrebuje schema, authoritative source, normalization, tenant boundary a deprovisioning lifecycle.

## 15. Delegation, impersonation a confused deputy

Pri impersonation systém vykonáva operáciu ako iná identity. Audit musí zachovať pôvodného actora aj impersonovaného subjecta. Pri delegation principal odovzdá obmedzenú authority ďalšiemu principalu alebo službe.

Confused deputy vzniká, keď privilegovaná služba použije vlastnú authority v prospech žiadateľa bez správneho resource alebo actor contextu. Typickým príkladom je backend, ktorý má široký database access a vykoná request podľa user-provided object ID bez kontroly ownershipu.

Delegovaný token má preto explicitne zachovať subject, actor, audience, scope, lifetime a chain depth. Downstream service nemá automaticky dediť všetky permissions upstream služby.

## 16. Break-glass access

Break-glass je núdzová cesta pre prípad, keď bežný identity alebo authorization plane nefunguje. Nie je to trvalý admin účet používaný pre pohodlie.

Potrebné sú oddelené credentials, minimálny počet účtov, time-bound use, okamžitý alert, povinný dôvod, audit a rotation po použití. Recovery cesta musí byť pravidelne testovaná. Netestovaný emergency account môže byť počas incidentu zablokovaný, expirovaný alebo závislý od rovnakého nefunkčného IdP.

## 17. Čo je security auditing

Auditing vytvára evidence pre detection, incident response, accountability, compliance a forensic analysis. Audit event nemá iba povedať, že „niečo zlyhalo“. Má umožniť rekonštruovať actora, target, decision context a výsledok.

Typický record obsahuje:

- event time a trusted time source,
- actor/principal a prípadne delegated subject,
- session alebo credential identifier bez secret value,
- action a target resource,
- source device, workload alebo network context,
- authorization decision a policy revision,
- result a error category,
- correlation alebo trace ID.

Passwordy, private keys, authorization codes, raw tokens a citlivé payloady do auditu nepatria.

## 18. Authentication, authorization a administrative events

Authentication audit zahŕňa login attempts, MFA challenge, authenticator enrollment, reset, session creation a revocation. Authorization audit zahŕňa sensitive allow/deny, role assignment, policy zmenu, impersonation a break-glass activation. Administrative audit zahŕňa account lifecycle, key rotation, audit configuration a deletion/export udalosti.

Nie je potrebné ukladať každý low-risk read ako drahý forensic event. Audit schema sa má riadiť threat modelom. Privileged changes, cross-tenant reads, security-control mutations a failed attempts však typicky potrebujú silnejšiu evidence než bežná telemetry.

## 19. Audit integrity, availability a separation

Audit je sám security asset. Ak kompromitovaný workload môže logy prepísať alebo zastaviť bez detekcie, ich dôkazová hodnota je nízka.

Production model preto používa centralizovaný append-oriented storage, oddelený account alebo failure domain, obmedzené delete permissions, retention, clock synchronization a monitoring ingestion gaps. Kritické events môžu vyžadovať immutable storage, cryptographic integrity alebo nezávislý export.

Audit pipeline musí byť tiež dostupná. Ak exporter alebo queue zlyhá, systém potrebuje buffer, backpressure alebo explicitný failure model. Tiché zahadzovanie events je control failure.

## 20. Accounting oproti auditing

Accounting sleduje usage, duration, consumption alebo billing. Auditing sleduje security-relevant actions a accountability. Rovnaký event môže slúžiť obom, ale požiadavky sa líšia.

Billing record môže agregovať počet requestov. Security audit musí zachovať actora, target a policy context. Naopak audit nemusí obsahovať všetky detailné metriky potrebné na cost allocation.

## 21. End-to-end príklad

Používateľ chce zmeniť production deployment configuration.

```text
IdP vykoná phishing-resistant authentication
→ application vytvorí session s auth_time a assurance
→ user požiada o privileged action
→ policy vyžaduje čerstvú step-up authentication
→ PDP overí role, environment, approval a resource scope
→ PEP povolí update iba konkrétneho deploymentu
→ operation sa vykoná
→ audit uloží actora, approvera, resource, diff a policy revision
```

Ak sa neskôr objaví incident, tím vie odlíšiť kompromitovaný authenticator, chybnú role assignment, policy bypass a neautorizovanú zmenu auditu.

## 22. Authentication failure model

Pri authentication probléme postupuj od identity lifecycle-u ku konkrétnemu verifieru:

```text
account existuje a je enabled?
→ authenticator je správne enrolled a platný?
→ DNS, clock a network fungujú?
→ IdP alebo verifier je reachable?
→ issuer, audience, signature a certificate sú správne?
→ MFA alebo conditional policy bola splnená?
→ session/token neexpiroval alebo nebol revoke-nutý?
→ aplikácia správne mapovala principal?
```

Zachovaj exact timestamp, principal, correlation ID a authentication method. Všeobecné hlásenie „login nefunguje“ nestačí na oddelenie enrollment, protocol, policy a session chyby.

## 23. Authorization failure model

Najprv identifikuj presný tuple principal–action–resource–context.

```text
správny principal a session?
→ presná action a resource?
→ role, groups a attributes?
→ scope, tenant a ownership?
→ boundaries a explicit deny?
→ PIP data fresh?
→ správny PEP?
→ policy/cache propagation?
→ decision log?
```

Testuj positive aj negative cases. To, že operácia funguje s admin rolou, iba dokazuje, že broad role obchádza chýbajúcu permission; nedokazuje správny least-privilege návrh.

## 24. Audit failure model

Pri chýbajúcom evente over celý pipeline:

```text
event vznikol pri source?
→ mal správnu category a schema?
→ exporter alebo agent ho prijal?
→ queue a transport ho doručili?
→ central ingestion ho zaindexoval?
→ hľadáš správny tenant, čas a index?
→ retention alebo filtering ho neodstránili?
```

Chýbajúci security audit je control gap. Ak sa týka privilegovanej alebo incidentnej operácie, môže byť sám security incidentom.

## 25. Typické anti-patterny

### Authentication úspešná, teda access je povolený

Authentication iba určila principal. Resource authorization stále chýba.

### Role sa kontroluje iba v UI

API zostáva priamo volateľné a enforcement je obíditeľný.

### Shared admin account

Nie je možné spoľahlivo určiť actora ani individuálne revoke-nuť access.

### Signature tokenu je validná, audience sa nekontroluje

Token určený pre inú službu sa môže zneužiť na cross-service access.

### Auditujú sa iba úspešné operácie

Failed a denied attempts, ktoré často tvoria detection signal, zostanú neviditeľné.

### Audit zostáva iba na kompromitovateľnom workload-e

Útočník môže odstrániť evidence spolu s workloadom.

## 26. Kontrolné otázky

1. Prečo identity proofing a authentication riešia odlišné riziká?
2. Aký je rozdiel medzi identity, accountom, subjectom, principalom a credentialom?
3. Prečo dva knowledge secrets netvoria kvalitné MFA?
4. Ako sa líši authentication event, session a token?
5. Z akých vstupov vzniká authorization decision?
6. Prečo musí byť enforcement pri skutočnej resource boundary?
7. Ako sa líšia PAP, PDP, PIP a PEP?
8. Prečo federácia neodstraňuje potrebu local authorization?
9. Ako sa líši delegation a impersonation?
10. Čo musí obsahovať audit record, aby bol použiteľný pri incidente?
11. Ako chrániť integrity a availability audit pipeline-u?
12. Ako oddelíš authentication failure od authorization failure?

## Glossary impact

Relevantné pojmy: identity proofing, identity, account, subject, principal, credential, authenticator, authentication, authorization, auditing, accounting, session, token, step-up authentication, Policy Administration Point, Policy Decision Point, Policy Enforcement Point, Policy Information Point, federation, impersonation, delegation, confused deputy a break-glass access.

## Primárne zdroje

- [NIST SP 800-63-4 Digital Identity Guidelines](https://pages.nist.gov/800-63-4/)
- [NIST SP 800-63B Authentication and Authenticator Management](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [NIST SP 800-63C Federation and Assertions](https://pages.nist.gov/800-63-4/sp800-63c.html)
- [NIST Authentication, Authorization and Accounting glossary](https://csrc.nist.gov/glossary/term/Authentication_Authorization_and_Accounting)
- [NIST Audit and Accountability glossary](https://csrc.nist.gov/glossary/term/audit_and_accountability)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CIA triáda](cia-triad.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Least privilege →](least-privilege.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
