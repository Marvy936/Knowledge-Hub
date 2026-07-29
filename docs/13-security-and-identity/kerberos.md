# Kerberos

Kerberos V5 je ticket-based network authentication protocol. KDC vydáva časovo obmedzené tickets a session keys, aby client nemusel posielať svoj long-term password alebo service key každej protistrane. Platný ticket však dokazuje iba Kerberos authentication context. Nezaručuje aktuálnu account eligibility, správnu group generation, application authorization ani revocation downstream sessions.

## 1. Dominantný lifecycle

```text
principal, realm a long-term credential
→ KDC discovery a pre-authentication
→ AS exchange a TGT
→ TGS exchange pre exact service principal
→ service ticket, KVNO, enctype a flags
→ AP exchange, authenticator a replay verdict
→ GSS/application security context
→ PAC/group/local-principal mapping
→ resource/business authorization
→ ticket, session a delegated-credential lifecycle
→ revocation, rotation a second-ticket validation
```

Oddeľuj:

```text
TGT bol vydaný
≠ service ticket bol vydaný
≠ service ticket bolo možné decryptovať
≠ AP exchange a mutual authentication uspeli
≠ current directory eligibility je správna
≠ application operation je povolená
```

## 2. Exact Kerberos subject

Pri incidente zaznamenaj:

```text
realm a KDC/DC identity
client principal a credential/logon generation
requested service principal/SPN
AS, TGS alebo AP stage
ticket start/end/renew-until a flags
KVNO a encryption types
credential cache alebo keytab identity
PAC/authorization-data generation, ak je relevantná
GSS/SPNEGO mechanismus a fallback
application principal mapping a resource decision
```

Connected Atlas subject:

```text
security incident: SEC-PAY-48
Kerberos subject: KRB-PAY-48
realm: CORP.ATLAS.EXAMPLE
client: martina.kovacova@CORP.ATLAS.EXAMPLE
KDC/DC: DC-FRA-02
service principal: HTTP/settlement-console.corp.atlas.example
TGT issuance: 2026-07-29 08:11 UTC
privileged group removal: 2026-07-29 07:40 UTC na DC-BTS-01
```

## 3. Realm, principal a SPN

Realm je Kerberos naming a administrative boundary. Často sa podobá DNS domainu, ale nie je to ten istý objekt.

Principals:

```text
martina.kovacova@CORP.ATLAS.EXAMPLE
host/node01.corp.atlas.example@CORP.ATLAS.EXAMPLE
HTTP/settlement-console.corp.atlas.example@CORP.ATLAS.EXAMPLE
```

Service Principal Name viaže logical service a hostname na account/key, ktorým service decryptuje tickets. Client žiada ticket pre meno použité v protocol path-e. DNS alias, load balancer alebo proxy preto potrebuje explicitný SPN a key-ownership plán.

```text
requested SPN
→ owner account
→ long-term key generation/KVNO
→ deployed keytab alebo managed service identity
```

Missing, duplicate alebo wrong-owner SPN vedie k odlišným failures. Test cez `localhost` alebo interný hostname nemusí používať rovnaký SPN ako production client.

## 4. KDC, AS a TGS

KDC logicky obsahuje:

- Authentication Service — AS — vydávajúcu TGT;
- Ticket-Granting Service — TGS — vydávajúcu service tickets;
- principal/key a policy database.

V AD DS ich poskytujú domain controllers. KDC je vysoko dôveryhodný control plane; compromise realm/TGS keys môže umožniť forged tickets a realm-wide impersonation.

### AS exchange

```text
client → AS-REQ + pre-auth evidence
KDC → AS-REP:
  TGT encrypted TGS keyom
  client/TGS session key protected client credentialom
```

AS success preukazuje, že KDC akceptoval client principal a pre-authentication. Nepreukazuje availability konkrétnej application service.

### TGS exchange

```text
client → TGT + authenticator + requested SPN
KDC → service ticket + client/service session key
```

TGS success preukazuje, že KDC vydal credential pre exact SPN podľa current KDC state/policy. Nepreukazuje reachability service ani business permission.

### AP exchange

```text
client → service ticket + fresh authenticator
service → optional AP-REP pre mutual authentication
```

Service decryptne ticket long-term keyom, overí authenticator, freshness a replay a vytvorí security context.

## 5. Tickets, authenticators a session keys

Ticket obsahuje client a service identity, session key, validity, flags a optional authorization data. Je encrypted keyom cieľovej service alebo TGS.

Authenticator je fresh client-created structure encrypted session keyom. Viaže prezentáciu ticketu na aktuálny request a replay cache.

```text
valid ticket
+ matching session key
+ fresh authenticator
+ acceptable clock skew
+ no replay
→ accepted AP context
```

Ticket bytes bez corresponding session keyu typicky nestačia. Ukradnutá credential cache však môže obsahovať oboje a umožniť pass-the-ticket.

Kerberos session key môže GSS/application protocol použiť na integrity alebo confidentiality. Samotná Kerberos authentication automaticky neznamená, že application payload je encrypted.

## 6. Pre-authentication

Pre-authentication vyžaduje dôkaz kontroly nad client credentialom pred vydaním usable AS response. Znižuje unauthenticated offline-guessing path, ale nerieši weak password úplne.

Pri password-based principaloch je security závislá od entropy a enctype-specific string-to-key semantics. Service account s human-chosen passwordom môže byť zraniteľný voči offline guessing z service ticketu.

Moderné deployments používajú required pre-auth, strong/managed credentials a podľa platformy smart-card alebo FAST-protected mechanisms.

## 7. Credential cache a keytab sú odlišné secrets

Credential cache drží TGT, service tickets a session material pre user/process session.

```bash
kinit martina.kovacova@CORP.ATLAS.EXAMPLE
klist -ef
kdestroy
```

`kdestroy` odstráni local cache reference. Nezruší automaticky application sessions alebo všetky tickets skopírované inde.

Keytab drží long-term service keys:

```text
principal
+ KVNO
+ enctype
+ key material
```

Keytab je ekvivalent service password/private keyu. Nesmie byť v Git-e, image layeri, ticket-e ani zdieľaný medzi nesúvisiacimi services. Potrebuje restrictive access, ownera, rotation a audit.

## 8. KVNO a service-key rotation

KVNO označuje version long-term keyu. Pri rotation KDC začne vydávať tickets pre novú version; fleet musí dostať corresponding key.

```text
KDC ticket kvno=8
service keytab iba kvno=7
→ ticket decrypt failure
```

Safe rotation:

```text
inventory principal/SPNs/consumers
→ vytvoriť new key generation
→ distribuovať do celej service cohorty
→ canary decrypt new ticket
→ bounded overlap old/new KVNO
→ odstrániť old key
→ reload a monitorovať
→ forbidden old-key test
```

Príliš skoré odstránenie old keyu zlomí ešte platné tickets. Príliš dlhý overlap predlžuje compromise window. Rotation service keyu neodstráni stolen user tickets ani application sessions.

## 9. Encryption types

Client, KDC a service potrebujú spoločný secure enctype. Oddeľuj long-term-key enctype, ticket encryption a session-key enctype.

Legacy RC4 a 3DES paths sú deprecated; migration musí inventarizovať principals, devices, keytabs a negotiated mechanisms. Jednostranné vypnutie môže spôsobiť outage, ale permanentný fallback zachováva weak offline-attack path.

Monitoring má ukazovať actual negotiated enctype, nie iba configured allowlist.

## 10. Time, freshness a replay

Kerberos používa timestamps a validity intervals. Client, KDC a service musia byť v accepted clock-skew windowe.

```text
service time
− authenticator time
→ freshness verdict
→ replay-cache lookup
```

Vypnutie time/replay validation nie je availability fix; odstraňuje security property. Oprav NTP hierarchy, suspend/resume behavior a secure time source.

Tickets majú start, end a optional renew-until. Expiry ticketu automaticky neukončí application session vytvorenú predtým.

## 11. DNS a service discovery

Kerberos používa DNS pre KDC discovery, hostname/SPN formation a realm mapping. Troubleshooting porovnáva:

```text
user-visible hostname
→ resolved/canonical hostname
→ requested SPN
→ directory SPN owner
→ keytab principal
→ proxy/load-balancer topology
```

DNS success nepreukazuje SPN correctness. HTTP proxy môže ukončiť Kerberos a vytvoriť nový backend identity path; spoofable `X-User` header nie je ekvivalent Kerberos authentication.

## 12. PAC a AD group generation

Active Directory tickets môžu obsahovať Privilege Attribute Certificate — PAC — s user SID, group memberships a ďalším authorization data. KDC ho vytvára z directory state-u, ktorý má k dispozícii.

```text
selected DC/KDC directory generation
→ PAC group generation
→ Windows/application principal mapping
→ resource authorization
```

Fresh ticket vydaný neconverged DC môže byť cryptographically validný a niesť stale group SID. Valid PAC signature chráni integrity structure; nepreukazuje, že underlying directory membership už convergovala na business-intended state.

Existing Windows logon token, service session alebo OAuth token odvodený z PAC/group claimu môže prežiť neskoršiu directory opravu.

## 13. Kerberos, LDAP a application authorization

```text
Kerberos
→ autentizuje principal a distribuuje session key

LDAP
→ poskytuje current alebo replica-local directory attributes

PAC/Windows token
→ prenáša vybrané identity/group data

application policy
→ rozhoduje action/resource/business state
```

LDAP Simple Bind na domain controller nie je Kerberos. Kerberos-authenticated LDAP connection stále podlieha directory ACL. Platný service ticket stále nepovoľuje cross-tenant alebo high-risk operation bez application authorization.

## 14. GSS-API, SPNEGO a HTTP Negotiate

GSS-API poskytuje application interface pre mutual authentication, integrity, confidentiality, replay/sequence detection a delegation. SPNEGO umožní negotiation mechanismu; HTTP `Negotiate` môže skončiť Kerberosom alebo fallbackom.

Monitoring musí odlíšiť:

- Kerberos accepted;
- NTLM fallback;
- anonymous/backend header path;
- mutual-auth result;
- delegated credential use;
- subsequent application authorization.

„Login funguje“ cez NTLM fallback môže skrývať broken SPN, DNS alebo keytab generation.

## 15. Delegation a actor chain

Delegation umožní front-end service konať voči downstream service v user context-e. Zväčšuje blast radius front-end compromise-u.

```text
initiating user
→ front-end service actor
→ delegated credential
→ exact downstream SPN
→ downstream authorization
```

Preferuj constrained/resource-based model viazaný na specific downstream services. Audit musí zachovať subject aj actor. Unconstrained delegation alebo forwardable TGT na low-trust hoste je high-impact credential path.

Protocol transition potrebuje explicitný threat a authorization model; nesmie sa stať implicitnou user impersonation capability.

## 16. Cross-realm trust

Cross-realm trust umožní authentication path cez inter-realm TGTs. Direction, transitivity, trust keys a name mapping určujú scope.

```text
principal@A
→ trust path
→ service ticket pre service@B
→ target realm/application authorization
```

Trust neudeľuje automatic resource access. Abandoned trust bez ownera a key rotation je hidden authentication path.

## 17. Containers a ephemeral workloads

Ephemeral replicas komplikujú stable SPN, keytab distribution, hostname canonicalization a rotation. Jeden shared keytab medzi všetkými Pods znamená spoločný long-term principal; compromise jednej replica umožní impersonovať celý service až do rotation.

Preferuj managed service identities, gMSA pre podporované Windows workloads alebo modernú workload federation, keď Kerberos nie je required compatibility boundary. Keytab nikdy nepatrí do image layeru.

## 18. Worked failure: fresh ticket, stale authorization data

### Symptom

Martina sa o `08:11 UTC` nanovo prihlási a settlement console prijme HTTP Negotiate. O `08:17 UTC` dostane `payments.approve`, hoci privileged AD membership bola odstránená o `07:40 UTC`.

### Exact subject

```text
Kerberos subject: KRB-PAY-48
client principal: martina.kovacova@CORP.ATLAS.EXAMPLE
KDC: DC-FRA-02
TGT issue time: 08:11 UTC
service SPN: HTTP/settlement-console.corp.atlas.example
service key KVNO: 12
negotiated mechanism: Kerberos, nie NTLM
PAC privileged SID: present
```

### Competing hypotheses

1. browser použil old pre-removal TGT;
2. SPNEGO fallbackol na NTLM;
3. duplicate/wrong SPN mapoval na iný service account;
4. service keytab/KVNO mismatch spôsobil fallback path;
5. KDC vytvoril PAC zo stale directory replica;
6. application ignorovala PAC a použila stale LDAP/cache claim;
7. application scope mapping povoľuje action bez current JIT eligibility.

### Discriminating evidence

```text
TGT issue time 08:11 UTC > removal time 07:40 UTC
KDC/DC identity: DC-FRA-02
DC-FRA-02 group state: user stále member
DC-BTS-01 group state: user removed
requested SPN: exact expected HTTP SPN
service ticket KVNO 12: keytab decrypt success
SPNEGO mechanism: Kerberos
PAC/group output: privileged SID present
new isolated session against converged DC: privileged SID absent
```

Fresh TGT diskriminuje old-cache hypotézu. Successful AP exchange diskriminuje SPN/KVNO failure. Root cause je fresh Kerberos credential vytvorený z stale KDC directory state-u.

### Evidence-preserving containment

- preserve-nuť TGT/service-ticket metadata, KDC identity, PAC/group output, SPN/KVNO a application audit bez raw reusable ticket blobu;
- revoke-nuť application/OAuth sessions odvodené z affected Kerberos session;
- zastaviť privileged operations pre affected principal/group generation;
- pri podozrení na credential theft disable-nuť account a analyzovať ticket use;
- neotáčať service keytab bez evidence, ak service key compromise nie je hypotéza;
- nevynucovať NTLM fallback ako workaround.

### Authoritative recovery

1. opraviť AD replication a site/subnet selection;
2. overiť group convergence na všetkých KDC/DCs;
3. zrušiť affected logon sessions a credential caches podľa platformy;
4. vydať fresh TGT cez intended/converged KDC a overiť PAC bez privileged SID;
5. revoke-nuť downstream application sessions, OAuth grants a exchanged tokens;
6. oddeliť high-risk capability od permanentného PAC/group snapshotu cez JIT/fresh authorization;
7. monitorovať actual Kerberos mechanism, KDC identity a privileged group generation.

### Acceptance verdict

- fresh AS/TGS/AP flow uspeje pre oprávneného principalu;
- removed principal dostane fresh TGT, ale bez privileged authorization data;
- old credential cache, application session a downstream token už action nepovolia;
- duplicate SPN, wrong audience, NTLM fallback a old KVNO fixtures zlyhajú podľa contractu;
- resource server stále vykoná object/business authorization aj pri validnom ticket-e;
- druhá controlled group removal prejde KDC failover a second-logon testom.

## 19. Troubleshooting flow

```text
realm, principal a time
→ KDC discovery
→ AS/pre-auth a TGT
→ requested SPN
→ TGS/service ticket
→ KVNO/enctype/keytab
→ AP/authenticator/replay
→ GSS/SPNEGO actual mechanism
→ PAC/local principal mapping
→ application authorization
→ session/delegation/revocation
```

Common evidence:

```bash
klist -ef
kvno HTTP/settlement-console.corp.atlas.example@CORP.ATLAS.EXAMPLE
```

`Server not found` smeruje k SPN/realm/hostname. `Cannot decrypt` smeruje k owner/keytab/KVNO/enctype. `Clock skew` smeruje k time boundary. `Kerberos success + 403` smeruje k application authorization, nie k ďalšiemu keytab retry.

## 20. Compromise a recovery model

### User ticket/cache compromise

- revoke application sessions a downstream grants;
- disable/reset identity podľa incident scope;
- posúdiť ticket lifetime, renewal, forwarding a copied caches;
- analyzovať service-ticket use a resource actions.

### Service keytab compromise

- isolate service cohort;
- rotate service key/KVNO a distribute trusted keytab;
- minimalizovať overlap;
- posúdiť impersonation/decryption exposure;
- validate old-key rejection.

### KDC/realm/domain compromise

- zachovať directory/KDC evidence;
- izolovať affected control plane;
- použiť platform-specific staged high-value key/forest recovery;
- reset privileged, service a trust credentials;
- hľadať forged tickets a delegation persistence;
- obnoviť z trusted state a vykonať realm-wide acceptance.

## 21. Earlier controls

- KDC/site identity v authentication audite;
- per-site fresh-group Kerberos canary;
- SPN uniqueness a ownership validation;
- KVNO/keytab fleet inventory;
- legacy enctype a NTLM fallback inventory;
- minimal delegation a actor-chain audit;
- ticket/session revocation workflow viazaný na mover/leaver events;
- negative test `valid ticket, forbidden resource`;
- tested KDC/domain/forest recovery.

## 22. Anti-patterny

### Platný ticket = permission

Kerberos autentizuje principal; resource policy stále rozhoduje.

### Keytab v image alebo shared Git secret

Long-term service identity sa stane durable a kopírovateľná.

### DNS alias bez SPN plánu

Client žiada ticket pre meno, ktoré service key nepozná.

### NTLM fallback ako recovery

Maskuje Kerberos defect a zachová slabší path.

### Rotation bez KVNO overlap/retirement contractu

Časť fleet-u odmietne nové alebo ešte platné old tickets.

### Group removal bez session revocation

PAC, Windows token, application session a downstream token môžu prežiť.

## 23. Kontrolné otázky

1. Čo tvorí exact Kerberos subject?
2. Ako sa AS, TGS a AP exchange líšia?
3. Čo ticket, authenticator a session key dokazujú?
4. Prečo SPN a user-visible hostname musia sedieť?
5. Ako sa credential cache líši od keytabu?
6. Prečo KVNO potrebuje bounded overlap?
7. Ako čas a replay cache chránia AP exchange?
8. Prečo valid PAC môže niesť stale group generation?
9. Ako sa Kerberos, LDAP, GSS a application authorization dopĺňajú?
10. Ako odlíšiš user-ticket, service-key a KDC compromise?

## Glossary impact

Relevantné pojmy: Kerberos subject, ticket-generation identity, KDC-selected directory generation, PAC group generation, fresh-but-stale Kerberos ticket, AS/TGS/AP verdict, SPN-to-key ownership, KVNO overlap generation, mechanism-fallback verdict, delegated actor chain a Kerberos acceptance verdict.

## Primárne zdroje

- [RFC 4120 — Kerberos V5](https://www.rfc-editor.org/rfc/rfc4120)
- [RFC 4121 — Kerberos GSS-API mechanism](https://www.rfc-editor.org/rfc/rfc4121)
- [RFC 6113 — Kerberos pre-authentication framework](https://www.rfc-editor.org/rfc/rfc6113)
- [RFC 8129 — Authentication indicators in Kerberos tickets](https://www.rfc-editor.org/rfc/rfc8129)
- [RFC 8429 — Deprecate 3DES and RC4 in Kerberos](https://www.rfc-editor.org/rfc/rfc8429)
- [MIT Kerberos documentation](https://web.mit.edu/kerberos/krb5-latest/doc/)
- [Microsoft Kerberos overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: LDAP](ldap.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: OAuth 2.0 →](oauth-2.md)
<!-- KNOWLEDGE-NAVIGATION:END -->