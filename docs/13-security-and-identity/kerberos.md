# Kerberos

Kerberos V5 je ticket-based network authentication protocol. Key Distribution Center vydáva časovo obmedzené tickets a session keys, aby client neposielal long-term password alebo service key každej protistrane. Platný ticket však dokazuje iba konkrétny Kerberos authentication context. Nezaručuje aktuálnu account eligibility, správnu group generation, application authorization ani revocation downstream sessions.

Kerberos incident sa preto neanalyzuje vetou „ticket je validný“. Potrebujeme vedieť, ktorý principal a realm, ktorý KDC, aká long-term key generation, ktorý SPN, aký ticket lifetime, aké authorization data a ktorú local resource policy service použila.

## Ticket lifecycle

```text
principal, realm a long-term credential
→ DNS/KDC discovery a clock state
→ AS exchange, pre-auth a TGT
→ TGS exchange pre exact service principal
→ service ticket, session key a authorization data
→ AP exchange, authenticator a replay check
→ service identity/keytab/KVNO validation
→ local principal mapping a resource authorization
→ ticket renewal, delegation, cache a session descendants
→ key rotation, revocation a second-ticket validation
```

AS, TGS a application exchange sú odlišné boundaries. KDC môže vydať TGT, ale odmietnuť service ticket. Service ticket môže byť cryptographically validný, ale service ho nevie dešifrovať pre wrong KVNO. Service môže authentication prijať a následne správne vrátiť authorization deny.

## Exact Kerberos subject

```yaml
incident: SEC-PAY-48
realm: CORP.ATLAS.EXAMPLE
clientPrincipal: 7421@CORP.ATLAS.EXAMPLE
selectedKdc: DC-FRA-02.corp.atlas.example
tgtIssuedAt: 2026-07-29T08:11:00Z
tgtExpiresAt: 2026-07-29T18:11:00Z
servicePrincipal: HTTP/settlement-approval.atlas.example@CORP.ATLAS.EXAMPLE
serviceKeytabGeneration: 18
expectedKvno: 18
directoryGroupExpectedAbsent: GG-PAY-Settlement-Approvers
pacObservedGroup: GG-PAY-Settlement-Approvers
applicationSession: APP-SESSION-884
```

Subject viaže ticket na KDC a service key generation. Bez KDC identity a issue time-u nemožno rozlíšiť stale cached TGT od fresh ticketu vydaného zo stale directory replica.

## AS exchange a TGT

Client najprv objaví KDC a pošle AS request. Pre-authentication typicky dokazuje znalosť long-term key a chráni pred jednoduchým offline guessing scenárom. KDC po úspechu vydá TGT zašifrovaný kľúčom `krbtgt` a client-KDC session key.

```bash
kdestroy
kinit 7421@CORP.ATLAS.EXAMPLE
klist -ef
```

`kdestroy` odstráni local credential cache, `kinit` vyžiada fresh TGT a `klist -ef` ukáže principal, validity, flags a encryption types. Výstup preukazuje local ticket cache a časy ticketov. Nepreukazuje current directory convergence, správnosť PAC/group authorization data ani to, že application nezachová starú session.

Clock je protocol dependency. Authenticator a ticket validity používajú časové okná; veľký skew môže spôsobiť failure aj pri správnych credentials. Synchronizovaný clock však nepreukazuje security freshness identity state-u.

## TGS exchange a service principal

Client požiada TGS o ticket pre exact service principal, napríklad `HTTP/settlement-approval.atlas.example`. SPN musí jednoznačne identifikovať service account/key. Duplicate alebo wrong SPN môže presmerovať ticket na nesprávnu key generation alebo vytvoriť `KRB_AP_ERR_MODIFIED`.

```bash
kvno HTTP/settlement-approval.atlas.example@CORP.ATLAS.EXAMPLE
klist
```

`kvno` vyžiada service ticket a vypíše key version number podľa client-visible ticketu. Nepreukazuje, že server keytab obsahuje rovnaký KVNO alebo že load-balanced replicas majú konzistentnú keytab generation.

V AD prostredí sa SPN inventory kontroluje napríklad:

```powershell
setspn -Q HTTP/settlement-approval.atlas.example
setspn -L svc-settlement-approval
```

Prvý príkaz pomáha odhaliť duplicates, druhý ukáže SPNs accountu. Neoveruje keytab contents, service process identity ani DNS path, ktorú client reálne použil.

## AP exchange, authenticator a replay

Client pošle service ticket a nový authenticator service-u. Service ticket dešifruje svojím long-term key, overí authenticator freshness a replay a môže odpovedať pre mutual authentication. GSS-API alebo SPNEGO nad tým vytvorí application security context.

Replay cache chráni proti opakovanému použitiu rovnakého authenticatora v povolenom time window. Nie je to business idempotency. Dva samostatné, platné Kerberos contexts môžu stále vyvolať duplicate payment, ak application nemá semantic idempotency.

## Keytab, KVNO a encryption types

Keytab je long-term credential pre service principal a musí byť chránený ako secret. Rotation zvýši KVNO; počas bounded overlapu môže service potrebovať current aj previous key, aby prijala in-flight tickets. Predčasné odstránenie starej key generation spôsobí availability incident, príliš dlhý overlap predlžuje compromise window.

```bash
klist -kte /etc/security/keytabs/settlement-approval.keytab
```

Výstup preukazuje principals, KVNOs a enctypes prítomné v konkrétnom keytab file. Nepreukazuje file ownership/permissions, loaded key v bežiacom procese, KDC account state ani accepted runtime handshake na každej replica.

Moderný baseline nepoužíva deprecated slabé encryption types. Enctype compatibility sa overuje medzi KDC, clientom, service accountom a keytabom; globálne zapnutie legacy algoritmu kvôli jednému hostu zväčší security boundary.

## PAC a authorization snapshot

V AD-integrated Kerberos môže ticket obsahovať Privilege Attribute Certificate s group a authorization data. PAC je snapshot odvodený z directory state-u pri issuance. Ak KDC používa stale replica, **fresh** TGT môže niesť stale group membership. To je presne incident `SEC-PAY-48`.

Service musí odlíšiť Kerberos authentication od local resource authorization. PAC/group môže byť jeden trusted input, ale application stále kontroluje tenant, object ownership, workflow state, JIT grant a current high-risk revocation podľa svojho contractu. Scope-only alebo group-only authorization robí z directory lag priamy business privilege.

## Delegation a forwarding

Ticket forwarding a constrained delegation umožňujú service konať downstream v mene usera. Menia blast radius, pretože kompromitovaný frontend môže získať ďalšie service tickets. Delegation musí byť viazaná na exact service targets, protocol transition requirements a audit original/effective principalov.

Unconstrained delegation alebo exportovateľná forwardable credential cache je vysokoriziková. Moderné návrhy preferujú resource-specific, constrained delegation alebo workload token exchange s explicitným audience a krátkou lifetime.

## Cross-realm trust a fallback

Cross-realm authentication vytvára trust path cez realm keys. Acceptance závisí od transitive trust, name mapping a authorization policy v cieľovej doméne. Protocol success neznamená, že external principal smie lokálny resource.

NTLM alebo password fallback môže skryť Kerberos defect a znížiť assurance. Troubleshooting musí zaznamenať použitý protocol, nie iba „login funguje“. Ak Kerberos zlyhá pre wrong SPN a application potichu použije slabší fallback, availability sa zachová za cenu security regresie.

## Incident `SEC-PAY-48`: fresh TGT, stale PAC

Membership removal sa commitol na `DC-BTS-01`, ale nereplikoval sa na `DC-FRA-02`. Client po `kdestroy` vykonal fresh `kinit` o 08:11 a KDC na stale FRA replica vydal nový TGT. `klist` potvrdil nový issue time, čím sa vylúčila stará local cache. Application napriek tomu videla privileged group, pretože PAC vznikol zo stale directory generation.

Competing hypotheses boli prežitý TGT, application session cache, duplicate SPN, wrong service key, SIDHistory a stale KDC directory state. Fresh ticket issue time, KDC logs, PAC group a AD object metadata ukázali, že protocol fungoval správne nad neconverged authority.

Kerberos nebol root cause. Causal chain bol `replication defect → stale KDC read → fresh PAC → application group authorization → privileged session`. Dlhá ticket lifetime a downstream OAuth token boli amplifiers.

## Containment, recovery a revocation

Containment zablokuje privileged application action a zachová credential cache metadata, KDC selection, ticket times/flags/KVNO, service logs a PAC-derived authorization evidence. Global reset `krbtgt` sa nevykonáva naslepo; je to forest-wide security operation s významným availability a trust dopadom.

Recovery najprv obnoví directory convergence a správny DC selection. Potom zruší affected user sessions, purgne local caches, revoke-ne application a OAuth descendants a podľa compromise scope-u rotuje service keys. Fresh ticket sa vyžiada až po potvrdení authority state-u.

Acceptance vyžaduje fresh TGT z intended KDC bez privileged group, successful service authentication s current KVNO, denied application action, expired/revoked previous application session a no-fallback evidence. Druhý membership change musí vytvoriť očakávanú PAC generation po definovanom convergence intervale.

## Kontrolné otázky

1. Prečo fresh TGT nemusí obsahovať fresh authorization state?
2. Čo `klist` preukazuje a čo nepreukazuje?
3. Ako duplicate SPN a wrong KVNO vytvárajú odlišné failures?
4. Prečo replay cache nie je business idempotency?
5. Ako delegation mení effective principal graph?
6. Prečo NTLM fallback môže skryť security regresiu?
7. Kedy je ticket revocation nedostatočná bez downstream session revocation?

## Referencie

- [RFC 4120 — Kerberos V5](https://www.rfc-editor.org/rfc/rfc4120)
- [RFC 8429 — Deprecate 3DES and RC4 in Kerberos](https://www.rfc-editor.org/rfc/rfc8429)
- [Microsoft Kerberos authentication overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview)
- [MIT Kerberos documentation](https://web.mit.edu/kerberos/krb5-latest/doc/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: LDAP](ldap.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: OAuth 2.0 →](oauth-2.md)
<!-- KNOWLEDGE-NAVIGATION:END -->