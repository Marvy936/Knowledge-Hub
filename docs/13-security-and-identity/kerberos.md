# Kerberos

Kerberos je ticket-based network authentication protocol navrhnutý pre vzájomnú authentication clientov a services v nedôveryhodnej sieti bez posielania passwordu každej službe. Centrálna Key Distribution Center (KDC) infraštruktúra vydáva časovo obmedzené tickets založené na shared cryptographic keys.

Kerberos rieši authentication a session-key distribution. Neurčuje kompletný directory model, application authorization ani audit policy.

## 1. Mentálny model

```text
principal + long-term key
→ Authentication Service request
→ Ticket-Granting Ticket
→ Ticket-Granting Service request
→ service ticket
→ application service
→ mutual authentication a session key
→ application authorization
```

Password sa typicky používa na odvodenie long-term key pre získanie počiatočného ticketu; service password sa neposiela cez network pri každom requeste.

## 2. Realm

Realm je Kerberos administrative namespace.

Príklad:

```text
EXAMPLE.COM
```

Realm name sa často podobá DNS domainu, ale ide o odlišný concept.

Realm obsahuje:

- principals,
- KDC database,
- KDC services,
- policy,
- trust/cross-realm relationships.

## 3. Principal

Principal identifikuje user, service alebo host.

Príklady:

```text
alice@EXAMPLE.COM
host/server01.example.com@EXAMPLE.COM
HTTP/app.example.com@EXAMPLE.COM
```

Service principal name musí zodpovedať službe, hostname canonicalization a application expectations.

Duplicate alebo nesprávne SPNs sú častou príčinou Kerberos failure v AD DS prostredí.

## 4. KDC

KDC logicky obsahuje:

- Authentication Service (AS),
- Ticket-Granting Service (TGS),
- principal database a long-term keys.

Production realm potrebuje redundant KDCs a bezpečnú database/key lifecycle správu.

KDC compromise môže umožniť falšovanie alebo dešifrovanie tickets podľa kompromitovaných keys a platformy. KDC preto patrí do vysoko dôveryhodného tieru.

## 5. Ticket-Granting Ticket

TGT umožňuje clientovi žiadať service tickets bez opätovného zadávania passwordu.

TGT je:

- časovo obmedzený,
- šifrovaný key-om Ticket-Granting Service,
- uložený v credential cache clienta,
- potenciálne renewable alebo forwardable podľa policy.

TGT je bearer-like high-value credential. Jeho krádež môže viesť k impersonation počas platnosti.

## 6. Service ticket

Service ticket je vydaný pre konkrétny service principal.

Obsahuje client identity a session information a je chránený long-term key-om služby.

Service používa vlastný key/keytab na spracovanie ticketu. Následne musí vykonať application authorization.

Platný service ticket neznamená automaticky access k všetkým operáciám služby.

## 7. AS exchange

Zjednodušený flow:

```text
client → KDC AS: žiadosť o TGT
KDC → client: TGT + client/TGS session key
```

Pre-authentication typicky dokazuje, že client pozná alebo kontroluje long-term credential pred vydaním použiteľného response.

Bez vhodnej pre-authentication môže password-derived key čeliť offline guessing risku podľa konkrétneho setupu.

## 8. TGS exchange

```text
client → KDC TGS:
  TGT + authenticator + requested service principal

KDC → client:
  service ticket + client/service session key
```

KDC overí TGT a policy a vydá ticket určený konkrétnej službe.

## 9. AP exchange

```text
client → service:
  service ticket + authenticator

service → client:
  optional mutual-auth response
```

Authenticator pomáha chrániť pred replayom a viaže request na aktuálnu session/time context.

Mutual authentication umožňuje clientovi overiť, že komunikuje so službou, ktorá pozná správny service key.

## 10. Credential cache

Client ukladá TGT a service tickets do credential cache.

MIT Kerberos commands:

```bash
kinit alice@EXAMPLE.COM
klist
kdestroy
```

Cache môže byť file, keyring, memory alebo platform-specific store.

Security závisí od:

- filesystem/process isolation,
- session lifecycle,
- forwarding,
- cleanup,
- privilege boundaries.

## 11. Keytab

Keytab je súbor obsahujúci long-term keys pre principals, typicky services alebo hosts.

Entry zahŕňa:

- principal,
- key version number (kvno),
- encryption type,
- key material,
- metadata.

Keytab je credential ekvivalent passwordu/private key. Musí mať:

- minimálne filesystem permissions,
- bezpečnú distribution,
- rotation,
- backup/recovery policy,
- žiadne uloženie v Git-e alebo image.

## 12. Key version number

KVNO identifikuje verziu long-term key-u principalu.

Pri rotation:

- KDC začne používať novú key version,
- services musia dostať zodpovedajúci keytab,
- overlap môže byť potrebný podľa rollout modelu.

Mismatch spôsobí failures typu `key version number not found` alebo inability decrypt ticket.

## 13. Encryption types

Kerberos podporuje viac encryption types podľa implementation a policy.

Preferuj moderné interoperabilné algorithms a odstráň legacy types po compatibility teste.

Treba rozlíšiť:

- long-term key enctype,
- ticket encryption enctype,
- session-key enctype,
- client, KDC a service support.

Jednostranné zakázanie legacy enctype môže rozbiť staré services alebo devices; ponechanie slabých types zvyšuje risk.

## 14. Time synchronization

Kerberos používa timestamps a ticket lifetimes na replay protection.

Clients, KDCs a services musia mať čas v povolenom clock-skew okne.

Symptoms:

- `Clock skew too great`,
- authentication zlyháva iba na konkrétnych hosts,
- tickets vyzerajú not-yet-valid alebo expired.

Time source a hierarchy sú security dependency.

## 15. DNS a service discovery

Kerberos deployments často používajú DNS na:

- nájdenie KDC,
- canonical hostname,
- realm mapping,
- service principal construction.

DNS mismatch môže viesť k requestu na nesprávny SPN alebo realm.

Over:

- forward/reverse resolution podľa platformy,
- aliases/CNAME,
- load balancer name,
- canonicalization settings,
- DNS SRV records.

## 16. Ticket lifetime, renewal a flags

Tickets môžu mať flags:

- renewable,
- forwardable,
- proxiable podľa implementation/policy,
- initial,
- pre-authenticated.

Krátka lifetime znižuje exposure, ale zvyšuje dependency na KDC availability a renewal.

Forwardable TGT umožňuje delegation use cases, ale zvyšuje credential theft blast radius.

## 17. Delegation

Delegation umožňuje service konať voči downstream service v user context-e.

Riziká:

- service získa širšiu authority,
- transitive delegation,
- credential forwarding,
- confused deputy,
- nejasný audit actor chain.

Použi najobmedzenejší supported model, napríklad constrained alebo resource-based constrained delegation v AD DS podľa use case-u.

Unconstrained delegation predstavuje vysoký risk.

## 18. Cross-realm trust

Cross-realm trust umožňuje principalom jedného realm-u získavať tickets pre services v inom realm-e.

Treba definovať:

- direction,
- transitivity,
- name mapping,
- trust keys,
- authorization rules,
- path selection.

Trust umožňuje authentication path, nie automatický authorization allow.

## 19. Kerberos v Active Directory

AD DS integruje:

- directory identities,
- KDC na domain controllers,
- DNS discovery,
- SPNs,
- group information/PAC,
- Windows logon a service authentication.

Common issues:

- duplicate SPN,
- service beží pod iným accountom než SPN owner,
- machine account password mismatch,
- time skew,
- DNS alias,
- kvno mismatch,
- NTLM fallback.

## 20. PAC

Privilege Attribute Certificate v Microsoft Kerberos scenároch nesie authorization-related identity/group data podpísané KDC/domain infrastructure.

Service alebo operating system používa tieto informácie pri vytvorení authorization tokenu.

PAC obsah a validation sú platform-specific; Kerberos core protocol sám nedefinuje celý Windows authorization model.

## 21. Kerberos a LDAP

Kerberos a LDAP riešia odlišné úlohy:

- Kerberos — ticket-based authentication,
- LDAP — directory access a queries.

AD client môže:

1. použiť Kerberos na authentication,
2. použiť LDAP na čítanie directory,
3. použiť SIDs/groups a ACLs na authorization.

LDAP Simple Bind nie je Kerberos, hoci obe služby môže poskytovať domain controller.

## 22. Kerberos a TLS

Kerberos poskytuje authentication a session keys, ale application transport protection závisí od použitého protocolu a mechanismu.

Nie každé Kerberos-authenticated application spojenie automaticky šifruje celý payload.

Napríklad HTTP Negotiate môže autentizovať používateľa, zatiaľ čo HTTPS stále poskytuje transport confidentiality, integrity a server certificate model.

## 23. Kerberos a containers/cloud

Challenges:

- DNS a stable service names,
- keytab distribution,
- Pod/instance identity,
- clock,
- ephemeral hosts,
- secret rotation,
- SPN uniqueness,
- cross-realm connectivity.

Keytab mount do veľkého počtu replicas vytvára shared long-term credential. Preferuj workload-specific identity a automatizovanú rotation, ak platforma podporuje vhodnejší moderný model.

## 24. Observability a audit

Sleduj:

- AS/TGS request rate a failures,
- pre-authentication failures,
- unknown principal,
- expired/revoked tickets,
- clock skew,
- unsupported enctype,
- kvno mismatch,
- duplicate SPN,
- delegation use,
- unusual ticket lifetime/flags,
- KDC availability a latency,
- NTLM fallback v AD prostredí.

Audit musí zachovať client principal, service principal, source, result, ticket properties a correlation bez logovania secret key materialu.

## 25. Troubleshooting s `kinit` a `klist`

```bash
kinit principal@REALM
klist
kvno HTTP/app.example.com@REALM
```

Over:

- default realm,
- KDC discovery,
- pre-authentication,
- TGT lifetime,
- requested service principal,
- kvno,
- cache location.

Service-side test musí používať rovnaký hostname/SPN ako reálny client path.

## 26. Troubleshooting flow

```text
čas synchronizovaný?
→ DNS/realm/KDC discovery?
→ principal existuje?
→ credentials/pre-auth?
→ TGT vydaný?
→ správny service principal?
→ service ticket vydaný?
→ service keytab obsahuje principal/enctype/kvno?
→ hostname/canonicalization?
→ application GSSAPI/SPNEGO config?
→ authorization po authentication?
```

Rozdeľ AS, TGS a AP failure. `Kerberos nefunguje` je príliš broad diagnóza.

## 27. Common errors

### Client not found in Kerberos database

Nesprávny principal/realm alebo chýbajúci account.

### Server not found in Kerberos database

Nesprávny SPN, hostname alebo chýbajúci service principal.

### Clock skew too great

Nesynchronizovaný client, KDC alebo service.

### Key table entry not found

Keytab neobsahuje požadovaný principal/enctype.

### Cannot decrypt ticket / kvno mismatch

Service keytab a KDC principal key versions nie sú zosúladené.

### Credentials cache not found

Client nemá TGT alebo používa inú cache/session identity.

## 28. Attacks a controls

Riziká:

- password guessing/offline attacks podľa pre-auth a key strength,
- stolen TGT/service tickets,
- pass-the-ticket,
- Kerberoasting v AD contexts,
- compromised keytab,
- forged tickets po KDC/domain compromise,
- unconstrained delegation,
- downgrade/legacy enctype.

Controls:

- silné passwords/keys pre service accounts,
- moderné enctypes,
- pre-authentication,
- short tickets podľa risku,
- protected credential caches,
- gMSA/managed rotation,
- constrained delegation,
- privileged tiering,
- detection a incident response.

## 29. Recovery a key rotation

Pri service key compromise:

1. identifikuj principal a dependencies,
2. zmeň/rotate long-term key,
3. distribuuj nový keytab bezpečne,
4. odstráň staré keys po overlap okne,
5. reštartuj/reload services,
6. invaliduj sessions/tickets podľa incident modelu,
7. monitoruj failures a abuse,
8. analyzuj source compromise.

Pri KDC/domain compromise je potrebný širší realm/forest recovery plán; rotation jedného service key nestačí.

## 30. Anti-patterny

### Keytab v container image alebo Git-e

Long-term service credential je kopírovateľný a ťažko revoke-nuteľný.

### DNS alias bez SPN plánu

Client žiada ticket pre name, ktorý service nepozná.

### Vypnutie time validation

Odstraňuje dôležitú replay ochranu.

### Unconstrained delegation pre pohodlie

Výrazne zväčšuje credential theft risk.

### NTLM fallback považovaný za úspešný Kerberos

Skutočný Kerberos problém zostane skrytý.

### Authentication success považovaný za authorization

Service stále musí overiť access.

## 31. Kontrolné otázky

1. Čo je realm, principal a KDC?
2. Ako sa líši TGT a service ticket?
3. Čo sa deje v AS, TGS a AP exchange?
4. Čo obsahuje keytab a prečo je citlivý?
5. Na čo slúži KVNO?
6. Prečo Kerberos závisí od času a DNS?
7. Aké riziká prináša delegation?
8. Ako Kerberos súvisí s AD DS, LDAP a TLS?
9. Ako rozlíšiť AS, TGS a service-side failure?
10. Ako reagovať na kompromitovaný keytab alebo KDC?

## Glossary impact

Relevantné pojmy: Kerberos, realm, principal, KDC, Authentication Service, Ticket-Granting Service, TGT, service ticket, authenticator, credential cache, keytab, KVNO, encryption type, pre-authentication, mutual authentication, ticket lifetime, renewable ticket, forwardable ticket, delegation, cross-realm trust, SPN, PAC a pass-the-ticket.

## Primárne zdroje

- [MIT Kerberos documentation](https://web.mit.edu/kerberos/krb5-latest/doc/)
- [MIT Kerberos application servers](https://web.mit.edu/kerberos/krb5-latest/doc/admin/appl_servers.html)
- [MIT Kerberos keytab](https://web.mit.edu/kerberos/krb5-latest/doc/basic/keytab_def.html)
- [MIT Kerberos encryption types](https://web.mit.edu/kerberos/krb5-latest/doc/admin/enctypes.html)
- [Kerberos V5 specification — RFC 4120](https://www.rfc-editor.org/rfc/rfc4120)
- [Kerberos authentication overview in Windows Server](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview)
