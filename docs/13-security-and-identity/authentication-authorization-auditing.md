# Authentication, authorization a auditing

Authentication, authorization a auditing sú tri samostatné bezpečnostné funkcie v jednom access lifecycle-e. Authentication vytvára dôveryhodný principal a session context. Authorization rozhoduje o jednej konkrétnej action nad jedným resource-om v konkrétnom context-e. Auditing zachováva actora, delegated identities, policy generation, enforcement a výsledok tak, aby bolo možné vysvetliť allow, deny aj vykonaný side effect.

Platná authentication nie je všeobecné povolenie. Platne podpísaný token nie je dôkaz správneho audience, tenant scope-u ani resource ownershipu. Audit event nie je užitočný, ak zachová iba display name alebo effective workload a stratí pôvodného actora.

## 1. Dominantný access lifecycle

```text
identity proofing a eligibility
→ account enrollment
→ authenticator/credential generation
→ authentication event a assurance
→ session alebo token generation
→ local principal mapping
→ principal–action–resource–context request
→ PIP attributes a policy generation
→ PDP decision
→ PEP enforcement na skutočnej boundary
→ operation result a side effects
→ actor/delegation audit chain
→ review, revocation a recovery
→ positive, forbidden a forensic validation
```

Tento lifecycle oddeľuje:

```text
authenticator bol správne overený
≠ session stále reprezentuje aktuálnu eligibility
≠ principal smie konkrétnu action na konkrétnom resource-e
≠ operation bola vykonaná podľa decisionu
≠ audit zachoval celý causal chain
```

## 2. Exact access subject

Pre connected incident používame:

```text
access subject: ACCESS-PAY-47
security subject: SEC-PAY-47
identity source record: HR-7421 generation 118
human identity: urn:atlas:human:7421
account: atlas-idp/7421
IdP issuer: https://id.atlas.example
authenticator: WebAuthn credential WAC-220
session: SESSION-771
session authentication time: 11:51 UTC
federated group claim: prod-payment-operators
Kubernetes user mapping: oidc:atlas:7421
requested actions:
  create pods
  patch configmaps
  patch deployments/scale
namespace: payments-prod
policy generation: RBAC-PAY-63
audit generation: AUDIT-SEC-28
```

Exact subject musí obsahovať identity, credential/session, request tuple, policy a evidence generation. Samotné meno používateľa alebo názov role nestačí.

## 3. Identity, account, subject, principal, credential a authenticator

- **Identity** — reprezentácia osoby, workloadu, zariadenia alebo organizácie.
- **Account** — administratívny záznam identity v konkrétnom systéme.
- **Subject** — entita pokúšajúca sa vykonať operáciu.
- **Principal** — security identity použitá verifierom alebo authorizerom.
- **Credential** — secret, key, token seed, certificate alebo iný dôkaz naviazaný na account/principal.
- **Authenticator** — prostriedok, ktorým claimant dokazuje kontrolu nad jedným alebo viacerými authentication faktormi.
- **Session** — dlhšie trvajúci lokálny authenticated context vytvorený po authentication evente.
- **Token** — prenosný artifact s claims alebo reference na server-side state.

Jedna osoba môže mať bežný account, privileged account, federated principal a workload delegation. Korelácia podľa emailu alebo display name-u je nedostatočná. Používaj stabilný `issuer + subject`, account ID, workload identity a explicitný delegation chain.

## 4. Identity proofing, enrollment a eligibility

Identity proofing určuje, komu má digitálna identity patriť. Enrollment viaže account a authenticator na túto identity. Eligibility určuje, či osoba alebo workload stále smie používať daný service či privilege.

```text
real-world alebo organizational evidence
→ identity record
→ account
→ authenticator binding
→ role/entitlement eligibility
→ authentication
```

Silná authentication neopraví chybný enrollment alebo stale eligibility. Ak helpdesk naviaže passkey na nesprávnu osobu alebo mover workflow ponechá starý entitlement, cryptographic proof môže byť úplne správny a výsledný access stále neautorizovaný.

NIST SP 800-63-4 oddeľuje:

- Identity Assurance Level — identity proofing;
- Authentication Assurance Level — control nad authenticatorom;
- Federation Assurance Level — federovaný assertion flow.

Tieto assurance axes sa vyberajú podľa risku príslušnej chyby, nie podľa prestíže použitej technológie.

## 5. Authentication ako dôkaz kontroly

Authentication odpovedá:

```text
Ktorý claimant preukázal kontrolu nad ktorým authenticatorom,
voči ktorému verifierovi, akou metódou a s akou assurance?
```

Faktory:

- knowledge — napríklad password;
- possession — zariadenie alebo cryptographic key;
- inherence — biometric characteristic, typicky použitá na aktiváciu possession authenticatora.

Dva knowledge secrets nie sú dve odlišné compromise boundaries. Password plus security question zostáva single-factor model.

Phishing-resistant protocol viaže authenticator output na legitímny verifier alebo channel. WebAuthn používa verifier-name binding cez relying-party identity. Manuálne prepísaný OTP nie je phishing-resistant, pretože impostor ho môže relay-nuť.

## 6. Human a workload authentication

Human authentication rieši enrollment, recovery, phishing, interactive step-up a session theft. Workload authentication rieši runtime binding, automated issuance a rotation.

Human patterns:

- passkeys/WebAuthn;
- smart cards;
- password plus MFA;
- federation;
- managed-device conditional access.

Workload patterns:

- cloud workload identity;
- short-lived OIDC assertion;
- Kubernetes projected ServiceAccount token;
- mTLS/SPIFFE identity;
- Kerberos service principal;
- short-lived database credential.

Workload nemá používať osobný account developera. User lifecycle, audit semantics a permission scope nezodpovedajú service boundary.

## 7. Credential a authenticator lifecycle

```text
generation alebo enrollment
→ issuance a binding
→ activation
→ protected storage a use
→ renewal alebo rotation
→ suspension
→ invalidation/revocation
→ recovery/rebinding
→ destruction
```

Pri compromise inventarizuj aj derived artifacts:

- active browser sessions;
- access a refresh tokens;
- API keys;
- certificates;
- delegated grants;
- workload credentials vydané na základe pôvodnej session;
- local caches a offline tickets.

Zmena passwordu sama nemusí zneplatniť existujúce sessions ani refresh tokens.

## 8. Authentication event, session a token

```text
authentication event
→ session/token issuance
→ opakované resource requests
→ authorization pri každom relevantnom requeste
→ reauthentication, expiration alebo revocation
```

Session dedí assurance z authentication eventu; nemá získať vyššiu assurance iba plynutím času. Potrebuje:

- overall a inactivity timeout;
- secure session-secret storage;
- logout a server-side invalidation;
- CSRF a replay protection;
- session theft detection;
- step-up pre sensitive action;
- explicitné behavior pri group/eligibility zmene.

NIST SP 800-63B-4 vyžaduje periodickú reauthentication a rozlišuje overall a inactivity timeout. Konkrétne limity závisia od AAL a risku aplikácie; nejde o univerzálnu hodnotu pre každý systém.

## 9. Step-up a freshness

Sensitive action môže vyžadovať čerstvejšiu alebo silnejšiu authentication než bežné čítanie.

```text
existing session
→ sensitive action classification
→ required AAL/authentication age/device context
→ step-up alebo deny
→ action-bound audit
```

Príklady:

- pridelenie production role;
- zmena provider credentialu;
- vypnutie auditu;
- break-glass activation;
- export citlivých dát;
- impersonation.

Step-up musí byť viazaný na sensitive action a bounded čas. Všeobecný „MFA completed sometime today“ nemusí byť dostatočný.

## 10. Authorization decision

Authorization vyhodnocuje:

```text
Smie principal P
vykonať action A
na resource R
v context-e C
pod policy generation G?
```

Formálne:

```text
decision = evaluate(P, A, R, C, G)
```

Context môže obsahovať:

- role a group memberships;
- tenant a resource ownership;
- environment a Region;
- session assurance a `auth_time`;
- device posture a network boundary;
- approval a workflow state;
- resource classification;
- delegation chain;
- explicit deny a maximum-permission envelope.

Authentication success poskytuje principal, nie finálny allow.

## 11. Authorization models

- **ACL** — permissions naviazané priamo na resource a principals.
- **RBAC** — principal získava permissions cez role.
- **ABAC** — decision používa trusted attributes principalu, resource-u, action a environmentu.
- **relationship-based access** — ownership, parent, membership alebo delegated relation.
- **policy-based model** — všeobecný evaluation engine a combining semantics.

Reálny systém často kombinuje viac vrstiev. Effective access vzniká až po vyhodnotení identity policy, resource policy, group inheritance, conditions, boundaries, organization guardrails, session restrictions a explicit denies podľa konkrétnej platformy.

## 12. PAP, PIP, PDP a PEP

- **Policy Administration Point** spravuje source, revision, approval a rollout policy.
- **Policy Information Point** dodáva group, ownership, risk, device alebo resource attributes.
- **Policy Decision Point** vyhodnotí request a vráti allow/deny/error.
- **Policy Enforcement Point** zachytí skutočnú operation a presadí decision.

Failure môže vzniknúť na každej vrstve:

```text
PAP: chybná alebo stale policy generation
PIP: stale group/tenant/ownership attribute
PDP: chybná evaluation alebo combining semantics
PEP: bypass, alternate path alebo ignored deny
```

UI-hidden button nie je PEP. Gateway token validation nie je object-level authorization v backend-e. Enforcement musí byť na každej skutočnej ceste k chránenému side effectu.

## 13. Federation a local authorization

Federation presúva authentication trust na Identity Provider. Trust contract zahŕňa issuer, audience, signature keys, claims, lifetime, assurance a rotation.

Relying party stále musí:

1. validovať assertion/token;
2. mapovať external identity na local principal;
3. normalizovať trusted attributes;
4. vykonať local authorization;
5. riadiť deprovisioning a session lifecycle.

IdP group claim nie je automaticky application permission. Potrebuje ownera, schema, scope, freshness a negative tests.

## 14. Delegation, impersonation a confused deputy

Pri **delegation** principal odovzdá bounded authority ďalšiemu principalu alebo službe. Pri **impersonation** systém vykonáva action ako iný principal.

Audit musí zachovať:

```text
original actor
→ delegating session/token
→ effective subject/workload
→ downstream action
→ target a result
```

Confused deputy vzniká, keď privilegovaná service použije vlastnú authority podľa caller-supplied resource ID bez overenia callerovho oprávnenia. Delegovaný artifact má viazať actor, subject, audience, scope, lifetime a chain depth.

## 15. Auditing ako security evidence lifecycle

```text
security-relevant occurrence
→ source audit record
→ schema a trusted timestamp
→ actor/delegation/policy context
→ append/queue/export
→ central ingestion a retention
→ protected query
→ correlation a investigation
→ evidence closure
```

Audit record má typicky obsahovať:

- event a observed time;
- stable actor/principal identity;
- delegated alebo impersonated subject;
- session/credential identifier bez secretu;
- action a target resource;
- source workload/device/network context;
- authorization decision a policy revision;
- operation result a error category;
- correlation/trace/operation ID.

Passwordy, raw access tokens, authorization codes, private keys a citlivé payloady do auditu nepatria.

## 16. Audit integrity, availability a separation

Audit je samostatný security asset. Compromised workload nemá mať authority meniť alebo mazať authoritative evidence o vlastných actions.

Controls:

- centralized append-oriented storage;
- oddelený account, tenant alebo failure domain;
- minimal delete permission;
- immutable retention podľa threat modelu;
- trusted time a sequence/correlation;
- ingestion-gap monitoring;
- independent export pre critical events;
- tested query availability počas incidentu.

`Audit enabled` nie je dôkaz completeness. Potrebný je canary od source eventu po central query.

## 17. Worked incident: authentication bola správna, access nie

### Subject a request chain

```text
ACCESS-PAY-47
actor: urn:atlas:human:7421
session: SESSION-771
authentication: WebAuthn success at 11:51 UTC
HR state: Finance Analytics since 08:00 UTC
stale claim: prod-payment-operators
action: create Pod settlement-debug-7f91
resource: namespace payments-prod
policy: RBAC-PAY-63
result: allow
```

### Symptóm

Security tím najprv predpokladá phishing-resistant authentication bypass, pretože human principal po team move vytvoril production Pod a následne došlo k Secret accessu a config mutation.

### Competing hypotheses

1. WebAuthn signature alebo verifier binding zlyhali;
2. IdP mapoval nesprávny account na subject `7421`;
3. session bola ukradnutá po validnej authentication;
4. application/Kubernetes použili stale group claim;
5. role assignment vznikol priamo mimo IdP groupu;
6. workload principal mal nezávislý broad access;
7. audit skryl skutočného human actora;
8. action bola approved break-glass operácia.

### Discriminating evidence

```text
WebAuthn challenge/verifier validation: success
credential binding: WAC-220 → account 7421
session cookie use: z nového endpointu po authentication
HR current department: Finance Analytics
IdP group graph: stale nested path present
session claim issue time: po HR mover evente
Kubernetes SubjectAccessReview: allow cez ClusterRoleBinding
no direct user binding: confirmed
Pod create audit actor: oidc:atlas:7421
Pod-selected ServiceAccount: settlement-debug
Secret read audit actor: system:serviceaccount:payments-prod:settlement-debug
break-glass reason/approval: absent
```

Authentication event bol cryptographically validný. Root cause bol stale PIP/entitlement state, ktorú PDP použil ako current. Broad RBAC permission umožnil delegated workload path. Session theft bol incident trigger; incomplete mover reconciliation a chýbajúca session revocation boli authorization/lifecycle failures.

### Evidence-preserving containment

- terminate `SESSION-771` a associated refresh/session artifacts;
- suspend account a invalidate authenticator podľa incident decisionu;
- remove stale nested membership a binding path;
- block ďalšie privileged requests pri PEP;
- preserve IdP authentication, token claims, group revisions, SubjectAccessReview, Kubernetes audit a workload identity events;
- isolate malicious workload bez odstránenia authoritative audit chainu;
- neinterpretovať password reset ako úplnú revocation;
- nezapnúť broad `cluster-admin` pre recovery.

### Authoritative recovery

1. opraviť mover desired-state reconciliation;
2. revoke-nuť sessions pri privileged entitlement removal;
3. skrátiť privileged claim lifetime a zaviesť risk-based session termination;
4. rozdeliť broad operator role na JIT mediated capabilities;
5. korelovať human actor → Pod create → ServiceAccount → Secret use;
6. pridať positive/negative access fixtures;
7. vykonať second-login a second-sync test.

### Acceptance verdict

Recovery je prijatá, keď:

- current HR state a effective group graph sú zhodné;
- nový aj predtým vydaný session/token už nemajú stale privilege;
- principal nevie create Pod, patch config, scale Deployment ani čítať Secret;
- approved JIT operator vykoná iba bounded task po step-up-e;
- alternate nested-group a direct-binding paths zlyhajú;
- audit zachová original human actora aj delegated workload;
- denied attempt aj successful approved task sú queryovateľné;
- druhý mover reconciliation cycle neobnoví odstránený entitlement.

## 18. Failure models

### Authentication failure

```text
identity/account enabled?
→ authenticator binding a state?
→ verifier/origin/protocol?
→ clock/DNS/network/TLS?
→ assurance a conditional policy?
→ session issuance?
→ expiration/revocation?
→ local principal mapping?
```

### Authorization failure

```text
exact principal–action–resource–context?
→ role/group/attribute path?
→ tenant/ownership?
→ policy generation a combining semantics?
→ PIP freshness?
→ PDP decision?
→ PEP a alternate paths?
→ cache/session propagation?
```

### Audit failure

```text
source event vznikol?
→ actor/delegation/schema complete?
→ exporter/queue accepted?
→ central ingestion acknowledged?
→ správny tenant/time/index?
→ retention/filtering?
→ tamper/delete path?
```

## 19. Break-glass access

Break-glass je oddelená recovery cesta pre failure identity plane-u, nie convenience admin account.

Potrebuje:

- oddelený credential a storage;
- minimálny počet eligible principals;
- explicitný trigger a reason;
- step-up alebo equivalent assurance;
- bounded duration a scope;
- okamžitý alert;
- complete audit;
- rotation/revocation po použití;
- pravidelnú rehearsal bez závislosti od rovnakého failed IdP.

## 20. Anti-patterny

### Authenticated = authorized

Platný principal je iba jeden authorization input.

### Signature validná, audience sa nekontroluje

Token pre inú resource service sa použije ako confused-deputy credential.

### Role kontrolovaná iba v UI

API alebo alternate path zostáva priamo volateľný.

### Group claim ako permanentná pravda

Session prežije mover/leaver zmenu bez revocation alebo freshness contractu.

### Shared admin account

Nie je možné individuálne revoke-nuť access ani spoľahlivo určiť actora.

### Audit iba successful actions

Denied pokusy, recovery a policy mutations zostanú neviditeľné.

### Audit iba na workload-e

Compromised workload môže evidence odstrániť spolu so sebou.

## 21. Kontrolné otázky

1. Čo tvorí exact access subject?
2. Ako sa líši identity proofing, enrollment, authentication a eligibility?
3. Aký je rozdiel medzi identity, accountom, subjectom a principalom?
4. Prečo dva knowledge secrets nie sú kvalitné MFA?
5. Ako sa líši authentication event, session a token?
6. Z čoho vzniká principal–action–resource–context decision?
7. Ako sa líšia PAP, PIP, PDP a PEP?
8. Prečo federation neodstraňuje local authorization?
9. Ako audit zachová delegation a impersonation?
10. Prečo validná WebAuthn authentication nevylučuje authorization incident?
11. Ako preukážeš úplnú session a credential revocation?
12. Čo musí overiť second-login a second-sync acceptance test?

## Glossary impact

Relevantné pojmy: access subject, identity eligibility generation, authenticator binding, authentication-event generation, session-assurance state, principal mapping generation, authorization request tuple, policy-information freshness, policy-decision verdict, enforcement-path coverage, delegated-actor chain, session revocation closure, audit-generation subject, audit completeness verdict a access acceptance verdict.

## Primárne zdroje

- [NIST SP 800-63-4 Digital Identity Guidelines](https://pages.nist.gov/800-63-4/)
- [NIST SP 800-63A-4 Identity Proofing and Enrollment](https://pages.nist.gov/800-63-4/sp800-63a.html)
- [NIST SP 800-63B-4 Authentication and Authenticator Management](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [NIST SP 800-63C-4 Federation and Assertions](https://pages.nist.gov/800-63-4/sp800-63c.html)
- [NIST Authentication, Authorization and Accounting glossary](https://csrc.nist.gov/glossary/term/Authentication_Authorization_and_Accounting)
- [NIST Audit and Accountability glossary](https://csrc.nist.gov/glossary/term/audit_and_accountability)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CIA triáda](cia-triad.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Least privilege →](least-privilege.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
