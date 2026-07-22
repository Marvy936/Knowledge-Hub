# Authentication, authorization a auditing

Authentication, authorization a auditing tvoria tri odlišné bezpečnostné funkcie. Authentication overuje identitu alebo platnosť credentials, authorization rozhoduje, či konkrétny principal smie vykonať konkrétnu action voči konkrétnemu resource-u, a auditing vytvára evidence o tom, čo sa stalo. Ich zamieňanie vedie k nejasným trust boundaries, príliš širokým oprávneniam a incidentom bez použiteľnej dôkazovej stopy.

## 1. Mentálny model

```text
identity proofing a enrollment
→ credential issuance
→ authentication
→ session alebo token
→ authorization decision
→ protected operation
→ audit event
→ detection, investigation a accountability
```

Každý krok má vlastný owner, failure modes a assurance level.

## 2. Identity, subject, principal a account

- **Identity** reprezentuje osobu, workload, zariadenie alebo organizáciu.
- **Account** je administratívny záznam v konkrétnom systéme.
- **Subject** je entita, ktorá sa pokúša vykonať operáciu.
- **Principal** je security identity používaná pri authentication alebo authorization.
- **Credential** je dôkaz alebo secret naviazaný na principal.
- **Authenticator** je prostriedok, ktorým claimant preukazuje kontrolu nad credentialom.

Jedna osoba môže mať viac accounts a principals. Jeden workload môže používať service account, cloud role, Kubernetes ServiceAccount a database user. Identity correlation musí byť explicitná.

## 3. Identity proofing nie je authentication

Identity proofing overuje, komu má byť digitálna identita priradená. Authentication pri neskoršom prístupe overuje, že claimant kontroluje príslušný authenticator.

Príklad:

```text
HR overí zamestnanca
→ identity system vytvorí account
→ authenticator sa zaregistruje
→ používateľ sa neskôr autentizuje
```

Silné MFA neopraví nesprávne identity proofing ani account priradený zlej osobe.

NIST SP 800-63-4 rozlišuje Identity Assurance Level, Authentication Assurance Level a Federation Assurance Level. Požadovaná úroveň má vychádzať z risku a dopadu, nie z univerzálneho pravidla pre všetky aplikácie.

## 4. Authentication

Authentication odpovedá:

```text
Ktorý principal predkladá request a s akou mierou dôvery?
```

Faktory:

- niečo, čo používateľ vie,
- niečo, čo vlastní,
- niečo, čím je,
- device alebo cryptographic identity,
- contextual/risk signals ako doplnok.

### Single-factor a multi-factor

Dva secrets z rovnakej kategórie nie sú plnohodnotné MFA. Password a security question sú oba knowledge factors.

MFA má odolávať relevantným attacks:

- phishing,
- credential stuffing,
- replay,
- SIM swap,
- malware,
- session theft,
- MFA fatigue.

Phishing-resistant authenticators používajú cryptographic binding na verifier alebo origin, napríklad FIDO/WebAuthn alebo vhodne navrhnutú certificate-based authentication.

### Human a workload authentication

Human identities:

- password + MFA,
- passkey,
- smart card,
- federated sign-in.

Workload identities:

- short-lived cloud role credentials,
- mTLS certificate,
- Kubernetes projected ServiceAccount token,
- SPIFFE identity,
- Kerberos service principal a keytab.

Workload nemá používať osobný user account ani statický secret, keď platforma podporuje short-lived identity.

## 5. Credential lifecycle

```text
enrollment
→ issuance
→ activation
→ use
→ rotation/renewal
→ suspension
→ revocation
→ recovery
→ deletion
```

Kontroluj:

- kto smie credential vydať,
- kde je uložený,
- ako sa chráni private material,
- expiration,
- rotation overlap,
- revocation propagation,
- recovery a break-glass,
- audit registrácie a zmeny.

Credential compromise sa nerieši iba zmenou hesla, ak zostali aktívne sessions, refresh tokens, certificates alebo delegated grants.

## 6. Session a token

Úspešná authentication často vytvorí session alebo token.

Rozlišuj:

- authentication event,
- session cookie,
- access token,
- refresh token,
- ID token,
- Kerberos ticket,
- API key.

Session security zahŕňa:

- expiration a idle timeout,
- token audience a scope,
- replay protection,
- secure storage,
- revocation,
- step-up authentication,
- device/context binding,
- logout semantics.

`Authenticated once` neznamená `trusted forever`.

## 7. Authorization

Authorization odpovedá:

```text
Smie principal P vykonať action A voči resource R v context-e C?
```

Formálne:

```text
allow = policy(principal, action, resource, context)
```

Context môže zahŕňať:

- role a group membership,
- resource ownera,
- environment,
- time,
- network alebo device posture,
- tenant,
- data classification,
- approval state,
- session assurance.

### Enforcement point

Authorization musí byť presadená pri skutočnej resource boundary.

Príklady:

- API gateway môže overiť token, ale application stále musí kontrolovať object-level authorization,
- UI skryté tlačidlo nie je authorization control,
- Kubernetes admission policy nenahrádza runtime access control,
- database role môže byť posledná boundary aj keď application už kontrolovala access.

## 8. Policy decision a enforcement

Useful model:

```text
Policy Administration Point
→ vytvára a spravuje policy

Policy Decision Point
→ vyhodnotí request

Policy Enforcement Point
→ povolí alebo zamietne operation

Policy Information Point
→ poskytne attributes a context
```

Rozdelenie umožňuje analyzovať, kde vznikla chyba:

- nesprávna policy,
- stale attributes,
- nesprávne decision,
- chýbajúce enforcement,
- bypass path.

## 9. Default deny a explicit deny

Bez explicitného allow má byť request zamietnutý.

Policy systémy sa líšia:

- first match,
- deny overrides,
- allow overrides,
- additive permissions,
- intersection viacerých boundaries.

Pri troubleshooting nepredpokladaj univerzálnu evaluation logiku. Zdokumentuj poradie policies, inheritance, explicit deny a session restrictions.

## 10. Authorization models

### ACL

Permissions sú naviazané na resource a konkrétnych principals alebo groups.

### RBAC

Permissions sú združené v roles, ktoré sa priraďujú principals.

### ABAC

Decision používa attributes principalu, resource-u, action a environmentu.

### Relationship-based access control

Decision závisí od vzťahov, napríklad owner, member, parent alebo delegated admin.

### Policy-based access control

Centrálne alebo distribuované policy vyhodnocuje komplexný context.

Reálne systémy často kombinujú viac modelov.

## 11. Authentication nie je authorization

Platný token neznamená oprávnenie na každý resource.

Klasické chyby:

- IDOR/BOLA: používateľ zmení object ID a pristúpi k cudziemu objektu,
- backend dôveruje role z client payloadu,
- service overí signature, ale nie audience alebo scope,
- admin UI a API používajú odlišné rules,
- broad group membership dá neplánovaný transitive access.

Každá protected operation potrebuje authorization decision na serverovej strane.

## 12. Auditing

Auditing vytvára evidence pre:

- security monitoring,
- incident response,
- compliance,
- accountability,
- forensic analysis,
- change review.

Audit record má typicky obsahovať:

- event time,
- actor/principal,
- authentication method alebo session identity,
- source device/network,
- action,
- target resource,
- result,
- authorization context,
- delegated/impersonated identity,
- correlation ID,
- policy alebo change revision.

Audit log nemá obsahovať passwords, private keys, raw session tokens ani nadbytočné sensitive data.

## 13. Authentication, authorization a audit eventy

### Authentication events

- login success/failure,
- MFA challenge,
- authenticator enrollment,
- credential reset,
- session creation/revocation,
- suspicious authentication.

### Authorization events

- allow/deny pre sensitive action,
- role alebo group change,
- policy update,
- privilege escalation,
- break-glass activation,
- impersonation/delegation.

### Administrative events

- account creation/deletion,
- key/certificate rotation,
- directory schema/config zmena,
- audit configuration change,
- log deletion alebo export failure.

## 14. Audit integrity a availability

Audit je security asset.

Controls:

- centralizovaný append-oriented storage,
- oddelený account/tenant/failure domain,
- obmedzený delete access,
- encryption,
- retention a legal hold,
- clock synchronization,
- integrity validation,
- monitoring ingestion gaps,
- export a recovery tests.

Ak kompromitovaný workload môže prepísať vlastný audit trail, evidence assurance je nízka.

## 15. Accounting oproti auditing

AAA sa často uvádza ako Authentication, Authorization and Accounting.

Accounting sa zameriava na usage, session duration, consumption alebo billing. Auditing sa zameriava na security-relevant evidence a accountability. Jeden event môže slúžiť obom účelom, ale retention, schema a integrity požiadavky môžu byť odlišné.

## 16. Federation

Federation umožňuje relying party dôverovať authentication assertion od identity provider-a.

Trust contract zahŕňa:

- issuer,
- audience,
- signing keys,
- protocol,
- claims/attributes,
- assurance,
- token lifetime,
- revocation a key rotation,
- metadata distribution.

Federation presúva authentication, ale resource authorization zostáva responsibility relying party alebo resource servera.

## 17. Impersonation a delegation

### Impersonation

Systém vykonáva action ako používateľ. Audit musí zachovať:

- pôvodného actora,
- impersonovanú identity,
- dôvod,
- schválenie,
- duration.

### Delegation

Principal odovzdá obmedzenú authority ďalšiemu principalu alebo service.

Riziká:

- širšie scope než bolo potrebné,
- dlhá životnosť,
- transitive delegation,
- confused deputy,
- strata pôvodnej identity.

## 18. Break-glass access

Emergency access potrebuje:

- silnú oddelenú authentication,
- minimálny počet účtov,
- offline alebo nezávislú recovery cestu,
- okamžité alerting,
- time-bound use,
- post-use credential rotation,
- povinný review.

Break-glass account bez pravidelného testu môže počas incidentu zlyhať.

## 19. Troubleshooting authentication

```text
identity/account existuje a je enabled?
→ authenticator/credential validný?
→ clock, DNS a network?
→ verifier alebo IdP reachable?
→ issuer/audience/signature/certificate?
→ MFA/conditional policy?
→ session/token expiration?
→ revocation alebo lockout?
→ application mapping principalu?
```

Zachovaj exact error, timestamp, principal, correlation ID a authentication method.

## 20. Troubleshooting authorization

```text
ktorý principal a session?
→ aká action a resource?
→ ktoré policies sa aplikujú?
→ role/group/attributes aktuálne?
→ inheritance a explicit deny?
→ scope a tenant?
→ enforcement point?
→ cache alebo propagation delay?
→ decision/audit evidence?
```

Testuj pozitívne aj negatívne cases. `Admin funguje` nie je dôkaz správnej policy.

## 21. Troubleshooting auditing

```text
event vznikol pri source?
→ správny severity/category?
→ correlation a actor fields?
→ agent/exporter/queue?
→ central ingestion?
→ tenant/index/time range?
→ retention/filtering?
→ access a integrity?
```

Chýbajúci audit event je security incident alebo control gap, nie iba observability problém.

## 22. Anti-patterny

### Login úspešný, teda access je povolený

Authentication sa zamieňa s authorization.

### Role iba v UI

API možno volať priamo.

### Shared admin account

Nie je možné spoľahlivo určiť actora.

### Long-lived service credentials

Compromise má dlhé okno a zlá je revocation.

### Audit iba úspešných operácií

Denied a failed attempts chýbajú pri detekcii.

### Audit bez centralizácie

Útočník môže evidence zmazať spolu s workloadom.

### Token signature overená, audience ignorovaná

Token určený pre inú službu sa môže zneužiť.

## 23. Kontrolné otázky

1. Aký je rozdiel medzi identity proofing a authentication?
2. Čo odlišuje subject, principal, account a credential?
3. Prečo MFA nemusí byť phishing-resistant?
4. Čo tvorí authorization request?
5. Kde musí byť authorization presadená?
6. Aký je rozdiel medzi ACL, RBAC a ABAC?
7. Prečo federácia nerieši resource authorization?
8. Čo musí obsahovať security audit record?
9. Ako sa líši accounting a auditing?
10. Ako diagnostikuješ authentication, authorization a audit failure?

## Glossary impact

Relevantné pojmy: identity proofing, identity, account, subject, principal, credential, authenticator, authentication, authorization, auditing, accounting, session, token, Policy Administration Point, Policy Decision Point, Policy Enforcement Point, Policy Information Point, federation, impersonation, delegation, confused deputy a break-glass access.

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
