# Kerberos

Kerberos V5 je ticket-based network authentication protocol. Umožňuje clientovi a network service-u vzájomne overiť identity bez toho, aby user alebo service posielali svoj long-term password či key každej protistrane. Centrálna Key Distribution Center — KDC — infraštruktúra vydáva časovo obmedzené tickets a session keys.

Kerberos rieši authentication a distribúciu session keys. Neurčuje celý directory model, business authorization ani transportnú ochranu každej application. Po úspešnom Kerberos exchange musí service stále rozhodnúť, ktoré actions a resources smie authenticated principal používať.

```text
principal + long-term credential
→ Authentication Service exchange
→ Ticket-Granting Ticket
→ Ticket-Granting Service exchange
→ service ticket
→ Application exchange
→ client a service sa autentizujú
→ application vykoná vlastnú authorization
```

## 1. Prečo Kerberos existuje

V jednoduchom password modeli by user zadával credential každej službe alebo by každá služba potrebovala overovať password voči centrálnej database. Tým by sa password dostával do mnohých application boundaries a každá compromised service by ho mohla ukradnúť.

Kerberos tento problém rieši nepriamo. User najprv preukáže control nad long-term credentialom KDC. KDC vydá Ticket-Granting Ticket — TGT. Client následne používa TGT na získanie service-specific tickets bez opätovného zadávania passwordu.

Service nikdy nepotrebuje user password. Dostane ticket encrypted keyom, ktorý pozná iba service a KDC, a authenticator vytvorený clientom pomocou session keyu.

## 2. Realm

Realm je Kerberos administrative a naming boundary. Typický realm vyzerá ako uppercase DNS domain:

```text
EXAMPLE.COM
```

Realm obsahuje principals, KDC database, long-term keys, ticket policy a trust relationships k ďalším realms. Názov sa často podobá DNS domainu, ale nejde o rovnaký objekt. DNS pomáha discovery a service naming-u; realm určuje Kerberos identity namespace a trust boundary.

Production a test realms majú byť oddelené. Ticket vydaný test KDC nemá byť trusted production service-om iba preto, že hostname alebo username vyzerá rovnako.

## 3. Principal

Principal je Kerberos identity usera, hosta alebo service-u. Zapisuje sa typicky ako components a realm:

```text
alice@EXAMPLE.COM
host/server01.example.com@EXAMPLE.COM
HTTP/app.example.com@EXAMPLE.COM
```

`alice` je user principal. `host/server01.example.com` a `HTTP/app.example.com` sú service principals. Service principal určuje, pre ktorú logical service a hostname KDC vydáva ticket.

Principal name nie je iba display label. Je súčasť cryptographic a authorization bindingu. Client žiada ticket pre presný service principal; service musí mať corresponding long-term key.

## 4. Service Principal Name

Service Principal Name — SPN — identifikuje service instance, napríklad HTTP service na konkrétnom hostname. V Active Directory je SPN attribute priradený accountu, pod ktorým service používa Kerberos key.

```text
HTTP/app.example.com
→ ticket bude encrypted keyom accountu vlastniaceho tento SPN
```

Ak SPN chýba, client nevie získať service ticket. Ak je duplicate, KDC nevie bezpečne určiť správneho ownera. Ak service beží pod iným accountom než SPN owner, nedokáže ticket decryptovať.

Load balancer, DNS alias a service migration preto potrebujú SPN plán. Client vytvára service principal podľa mena, ktorým service oslovuje, nie podľa interného názvu procesu.

## 5. KDC

Key Distribution Center logicky obsahuje dve protocol services a principal database:

- Authentication Service — AS — vydáva TGT;
- Ticket-Granting Service — TGS — vydáva service tickets;
- principal database — uchováva long-term keys a policy.

AS a TGS môžu bežať v jednom process-e. V Active Directory ich poskytujú domain controllers spolu s directory a ďalšími services.

KDC je vysoko dôveryhodný control plane. Compromise KDC alebo jeho database môže umožniť vydávať forged tickets, kradnúť keys alebo impersonovať principals podľa zasiahnutého key materialu. Production realm preto potrebuje redundant KDCs, protected administration, backup a recovery plan.

## 6. Long-term keys

Každý principal má long-term key material. User key môže byť odvodený z passwordu alebo viazaný na iný credential mechanismus. Service key sa typicky uchováva v keytab-e alebo platform-managed account-e.

Long-term key sa bežne nepoužíva na encryption application payloadu. KDC ho používa na ochranu bootstrap response-u alebo tickets a na distribúciu krátkodobejších session keys.

Slabý service-account password znamená slabý Kerberos key. Attacker môže získať service ticket a skúšať offline password guesses proti encrypted časti ticketu, čo je základ Kerberoasting risku v AD prostredí.

## 7. Ticket anatomy

Kerberos ticket je KDC-issued structure určená konkrétnemu service principalu. Obsahuje najmä:

- client principal;
- server/service principal;
- client-service session key;
- validity interval;
- flags;
- optional addresses a authorization data;
- key version a encryption information podľa encodingu.

Ticket je encrypted long-term keyom cieľovej service. Client ho môže prenášať, ale bežne nevie prečítať alebo meniť jeho protected obsah.

Ticket je bearer-like credential v tom zmysle, že ukradnutý ticket spolu s potrebným session keyom môže umožniť impersonation počas validity.

## 8. Ticket-Granting Ticket

TGT je ticket určený Ticket-Granting Service principalu realm-u. Client ho používa na získavanie service tickets bez opätovného preukazovania passwordu.

TGT obsahuje client/TGS session key. Samotný TGT je encrypted long-term keyom TGS, ktorý je v praxi jedným z najcitlivejších realm keys.

Client uchováva TGT a corresponding session key v credential cache. Krádež cache môže umožniť pass-the-ticket: attacker nemusí poznať user password, ak má usable ticket a session material.

## 9. Service ticket

Service ticket je vydaný pre konkrétny service principal. KDC vytvorí client/service session key a doručí ho clientovi aj service-u v rozdielnych protected častiach:

- client dostane session key protected client/TGS session keyom;
- service dostane rovnaký session key vo vnútri ticketu encrypted svojím long-term keyom.

Service po decrypt-e ticketu pozná authenticated client principal a shared session key. Následne overí authenticator a vytvorí security context.

Platný service ticket nie je permission na všetky operations. Application môže mapovať principal na local account, groups, ACLs alebo resource-level policy.

## 10. AS exchange

Authentication Service exchange získava TGT.

```text
client → KDC AS:
  AS-REQ pre client principal a TGS principal

KDC → client:
  AS-REP obsahujúci
  - TGT encrypted TGS keyom
  - client/TGS session key protected client long-term keyom
```

Client decryptne svoju časť pomocou keyu odvodeného z passwordu alebo získaného iným credential mechanismom. Ak credential nesedí, client nezíska usable session key.

AS exchange neautentizuje application service. Vytvára bootstrap credential pre ďalšiu komunikáciu s TGS.

## 11. Pre-authentication

Pre-authentication vyžaduje, aby client preukázal control nad credentialom ešte pred tým, než KDC vydá response vhodný na offline guessing.

Tradičný timestamp pre-auth mechanismus odošle timestamp encrypted client long-term keyom. KDC ho decryptne a overí freshness. Moderné deployments môžu používať ďalšie pre-auth methods, smart cards alebo FAST-protected exchanges.

Ak password principal nemá required pre-authentication, attacker môže požiadať o AS response a skúšať password candidates offline. V AD security terminológii sa tento pattern označuje ako AS-REP roasting.

Pre-authentication nevyrieši slabý password úplne, ale odstráni unauthenticated offline-verification path pre bežný AS request.

## 12. TGS exchange

Client používa TGT na získanie service ticketu.

```text
client → KDC TGS:
  TGT
  authenticator encrypted client/TGS session keyom
  requested service principal

KDC → client:
  service ticket encrypted service keyom
  client/service session key protected client/TGS session keyom
```

TGS overí TGT, authenticator, ticket validity a realm policy. Môže tiež vyhodnotiť delegation, transited realms a requested ticket flags.

TGS response neznamená, že service je reachable alebo že client má application permission. Dokazuje, že KDC bol ochotný vydať authentication credential pre tento service principal.

## 13. AP exchange

Application exchange prebieha priamo medzi clientom a service-om.

```text
client → service:
  AP-REQ = service ticket + authenticator

service → client:
  optional AP-REP pre mutual authentication
```

Service decryptne ticket vlastným long-term keyom, získa client/service session key a tým overí authenticator. Authenticator obsahuje client identity a fresh time/subkey/sequence context podľa use case-u.

AP-REP umožní clientovi overiť, že protistrana skutočne pozná session key získaný z ticketu. Tým Kerberos podporuje mutual authentication.

## 14. Authenticator

Authenticator je fresh client-created structure encrypted session keyom. Viaže presentation ticketu na aktuálny client request a pomáha chrániť pred replayom.

Ticket môže byť validný niekoľko hodín, ale authenticator používa current timestamp a podľa protocol contextu sequence/subkey information. Service alebo replay cache odmietne duplicate authenticator v povolenom time windowe.

Ticket bez corresponding session keyu nestačí na vytvorenie validného authenticatora. Preto ochrana credential cache zahŕňa oba artifacts, nie iba ticket bytes.

## 15. Session keys

Kerberos vytvára viac session keys:

- client/TGS session key pre TGS exchanges;
- client/service session key pre application security context;
- optional negotiated subkeys pre konkrétny application exchange.

Session key je kratšie žijúci než long-term key a obmedzuje exposure. Application protocol alebo GSS-API mechanismus ho môže použiť na message integrity a confidentiality.

Kerberos ticket authentication automaticky neznamená, že celý application payload je encrypted. To závisí od protocolu a zvolených GSS-API protection services.

## 16. Credential cache

Credential cache uchováva TGT, service tickets a corresponding session keys pre user/session context. Implementácia môže byť file, kernel keyring, memory, Windows LSA alebo iný platform store.

MIT Kerberos tools:

```bash
kinit alice@EXAMPLE.COM
klist
kdestroy
```

`kinit` získa alebo obnoví initial credentials. `klist` zobrazí principal, validity, service principals a flags. `kdestroy` odstráni cache reference, ale neznamená universal server-side revocation všetkých už vytvorených application sessions.

Cache permissions, process isolation, forwarding a cleanup sú critical. Root alebo compromised same-user process môže podľa platformy credentials získať.

## 17. Keytab

Keytab je file alebo protected store obsahujúci long-term keys pre service/host principals. Entry typicky obsahuje principal, Key Version Number — KVNO — encryption type a key material.

Keytab je ekvivalent passwordu alebo private keyu. Kto ho skopíruje, môže impersonovať service, decryptovať relevantné tickets alebo podľa permissions získať ďalšie credentials.

Controls:

- restrictive owner/mode;
- no Git, image layer, ticket alebo chat storage;
- secure automated distribution;
- minimal principals;
- managed rotation;
- protected backup iba ak recovery vyžaduje;
- no broad shared keytab across unrelated services;
- audit accessu.

## 18. KVNO

Key Version Number identifikuje version long-term keyu principalu. Pri password/key rotation KDC zvýši KVNO a začne vydávať tickets encrypted novým keyom.

Service musí dostať keytab s corresponding KVNO. Controlled overlap môže ponechať old key krátko dostupný na decrypt tickets vydaných pred cutoverom.

```text
KDC vydáva ticket kvno=8
service keytab obsahuje iba kvno=7
→ service nevie ticket decryptovať
```

Príliš skoré odstránenie old keyu preruší in-flight tickets. Príliš dlhý overlap predlžuje trust compromised keyu.

## 19. Encryption types

Kerberos encryption type — enctype — definuje cryptographic algorithm a associated key derivation/protection semantics. Client, KDC a service musia mať spoločný supported secure enctype.

Treba rozlišovať:

- enctypes dostupné pre principal long-term keys;
- enctype ticket encryption;
- enctype session keyu;
- application/GSS protection support;
- policy preference a downgrade behavior.

Moderné deployments preferujú AES-based enctypes a odstraňujú DES/RC4 podľa platform supportu a migration planu. Jednostranné vypnutie legacy enctype môže rozbiť starý device; jeho ponechanie však zachová weak attack path.

## 20. String-to-key a password strength

Pri password-based principals sa long-term key odvodzuje z passwordu a salt-u pomocou enctype-specific string-to-key function. Security preto závisí od password entropy a derivation semantics.

Service account s human-chosen weak passwordom je vulnerable voči offline guessing z captured service ticketu. Long random managed password alebo platform-managed service account výrazne znižuje practical risk.

Password rotation bez aktualizácie service keytabu spôsobí KVNO mismatch. Managed account mechanisms môžu coordination automatizovať.

## 21. Time synchronization

Kerberos používa timestamps a ticket validity na freshness a replay protection. Clients, KDCs a services potrebujú čas v configured clock-skew intervale.

Typické symptoms:

- `Clock skew too great`;
- ticket je `not yet valid` alebo `expired`;
- iba časť hosts zlyháva;
- intermittent failures po VM suspend/resume;
- replay cache behavior je nepredvídateľné.

Time source, NTP hierarchy a monitoring sú security dependencies. Vypnutie time validation odstraňuje podstatnú replay ochranu; správna oprava je synchronizácia hodín.

## 22. DNS a service discovery

Kerberos často používa DNS na KDC discovery, realm mapping, hostname canonicalization a tvorbu service principalu. DNS SRV records môžu publikovať KDC endpoints.

Client žiada ticket podľa hostname, ktorý používa v application protocol-e. Alias alebo load balancer name preto musí mať zodpovedajúci SPN a service key ownership.

Troubleshooting musí porovnať:

- user-visible hostname;
- resolved canonical name;
- requested service principal v `klist`/trace;
- registered SPN;
- keytab principal;
- reverse proxy/load balancer behavior;
- realm mapping.

DNSSEC nie je inherentnou súčasťou Kerberos trustu; incorrect DNS môže stále poslať clienta na wrong endpoint alebo wrong SPN path.

## 23. Ticket lifetime

Ticket má start/end time a podľa policy renewable-until time. Krátka lifetime znižuje duration stolen ticketu, ale zvyšuje dependency na KDC a renewal.

TGT môže byť dlhší než service ticket. High-risk admin principal môže mať kratšie lifetimes než bežný workstation user.

Ticket expiry neukončí automaticky všetky application sessions vytvorené skôr. Service musí mať vlastný session lifecycle a incident revocation model.

## 24. Ticket flags

Flags menia ticket semantics:

- `initial` — vznikol cez initial AS exchange;
- `pre-authenticated` — client použil pre-authentication;
- `renewable` — možno získať nový ticket do renew-until limitu;
- `forwardable` — možno odvodiť/forwardovať credentials do ďalšieho host contextu;
- `proxiable` alebo proxy-related semantics podľa implementation;
- delegation-related flags;
- invalid/postdated podľa specialized use cases.

Flag nie je iba informational. Forwardable TGT zväčšuje credential theft blast radius. Service alebo KDC policy má povoľovať iba potrebné flags.

## 25. Renewal

Renewable ticket umožňuje predĺžiť usable lifetime bez opätovného zadania primary credentialu, ale iba do maximum renew-until time.

Long-running batch alebo workstation session môže TGT renewovať. Renewal process musí monitorovať failure a nesmie udržiavať credential nekonečne.

Ak account zablokuješ alebo key rotate-neš, already-issued renewable ticket behavior závisí od KDC policy a revocation modelu. Kerberos nemá univerzálny online status check pri každom AP requeste.

## 26. Delegation

Delegation umožňuje front-end service konať voči downstream service v user context-e. Používa sa napríklad pri web application → database alebo file service flowe.

Bez delegation downstream vidí iba service identity front-endu. S delegation môže downstream authorization zohľadniť user principal, ale front-end získava capability konať za usera.

Threats:

- credential forwarding alebo theft;
- broad transitive authority;
- compromised front-end impersonuje users downstream;
- confused deputy;
- nejasný audit actor chain;
- unconstrained access k services, ktoré user pôvodne nezamýšľal.

Preferuj constrained model viazaný na specific downstream service a preserve-ni initiating user aj executing service v audite.

## 27. Unconstrained a constrained delegation v AD

Pri unconstrained delegation môže service host získať forwardable user TGT alebo broad delegated credential a použiť ho voči ďalším services. Compromise takého hosta má vysoký impact, najmä ak sa naň prihlási privileged user.

Constrained delegation obmedzuje, ku ktorým service SPNs môže front-end delegovať. Resource-based constrained delegation presúva rozhodnutie na target resource account podľa AD modelu.

Protocol transition môže umožniť service získať Kerberos delegation context aj po inom upstream authentication mechanizme. Je high-impact a potrebuje explicitný authorization design.

## 28. Cross-realm trust

Cross-realm trust umožňuje principalovi realm-u A získať service ticket pre realm B cez inter-realm TGTs.

```text
client@A
→ TGT pre krbtgt/B@A alebo trust path
→ KDC B
→ service ticket pre service@B
```

Trust má direction, transitivity, shared/inter-realm keys, name mapping a path selection. Authentication path neznamená automatic authorization v target realm-e.

Transited realm information a local policy pomáhajú service/KDC posúdiť trust chain. Long trust paths a bidirectional transitive trusts zväčšujú systemic blast radius.

## 29. Realm trust keys

Inter-realm trust používa long-term keys medzi TGS principals. Compromise trust key môže umožniť forged cross-realm tickets v danom direction/scope.

Keys potrebujú rotation coordinated oboma realms, overlap a audit. Abandoned trust bez ownera je permanentný hidden authentication path.

## 30. Kerberos v Active Directory

Active Directory Domain Services integruje directory identities, KDC, DNS, SPNs, machine accounts, group data, Windows logon a service authentication.

Domain controller poskytuje AS/TGS. User alebo computer account password reprezentuje Kerberos long-term keys. SPNs sú attributes accountov. Domain/forest trust vytvára cross-domain authentication paths.

Kerberos authentication je iba časť Windows access token creation. Group SIDs, local groups, user rights a ACLs určujú authorization po logine.

## 31. Privilege Attribute Certificate

Privilege Attribute Certificate — PAC — je Microsoft authorization-data structure v Kerberos tickets. Nesie user SID, group memberships a ďalšie identity/authorization data vytvorené domain infrastructure.

Service/OS môže PAC použiť na vytvorenie Windows access tokenu. PAC má signatures a validation rules, aby arbitrary client nemohol pridať admin group.

PAC nie je súčasť generic application authorization modelu vo všetkých Kerberos implementations. Service stále potrebuje správne mapovať identity a overovať resource permissions.

## 32. Kerberos a LDAP

Kerberos a LDAP riešia odlišné vrstvy:

- Kerberos — authentication a session-key distribution;
- LDAP — directory queries a modifications;
- ACL/RBAC/application policy — authorization.

AD client môže získať TGT cez Kerberos, použiť Kerberos/GSSAPI na authenticated LDAP connection a následne čítať directory attributes podľa LDAP access controls.

LDAP Simple Bind s passwordom nie je Kerberos, hoci endpoint poskytuje domain controller. Authentication mechanismus musí byť overený, nie odvodený iba z portu alebo server role.

## 33. Kerberos a TLS

Kerberos môže autentizovať endpoints a GSS-API môže poskytovať message integrity/confidentiality. Nie každá Kerberos-enabled application však tieto protection services používa.

HTTP Negotiate/SPNEGO môže autentizovať browser usera, zatiaľ čo HTTPS stále poskytuje server certificate, transport encryption a protection pred intermediaries.

TLS a Kerberos sa dopĺňajú. TLS termination za proxy musí zachovať trustworthy client identity path; spoofable `X-User` header nie je náhrada backend authentication.

## 34. GSS-API

Generic Security Service Application Program Interface — GSS-API — poskytuje application-neutral interface pre authentication mechanismy, vrátane Kerberos V5.

Application vytvára security context a môže žiadať:

- mutual authentication;
- integrity protection (`wrap`/MIC semantics);
- confidentiality;
- replay a sequence detection;
- delegated credentials.

GSS-API status rozlišuje generic major status a mechanism-specific minor status. Troubleshooting preto potrebuje application log aj Kerberos trace.

## 35. SPNEGO a HTTP Negotiate

SPNEGO umožňuje peers negotiate-nuť GSS mechanismus. HTTP `Negotiate` authentication ho často používa na výber Kerberos a v niektorých Windows environments fallback NTLM.

Ak application „funguje“, ale použila NTLM fallback, Kerberos SPN/DNS/keytab problém môže zostať skrytý. Monitoring má rozlišovať actual negotiated mechanism.

Browser allowlists, trusted zones, service hostname a proxy topology ovplyvňujú, či browser vôbec pošle Negotiate token.

## 36. Kerberos v containers a cloud-e

Ephemeral workloads komplikujú stable service identity, keytab distribution, DNS, clock, hostname canonicalization a rotation.

Mount jedného keytabu do mnohých replicas vytvára shared long-term credential. Compromise jednej Pod instance umožní impersonovať celý service principal, kým key rotate-neš.

Možnosti sú workload-specific principals, managed keytab injection, sidecar/agent, gMSA pre Windows containers alebo moderná workload identity federation, ak application nemusí používať Kerberos.

Node a image boundaries sú critical: keytab nesmie byť v image layeri a runtime mount má mať restrictive permissions.

## 37. Observability

KDC a service telemetry má rozlišovať protocol stage:

- AS request rate a pre-auth failures;
- unknown client principals;
- TGS request rate a unknown service principals;
- requested SPNs a enctypes;
- ticket lifetime/flags;
- clock-skew failures;
- KVNO/keytab decrypt failures;
- replay-cache failures;
- delegation use;
- cross-realm paths;
- KDC latency/availability;
- actual Kerberos vs NTLM mechanism;
- application authorization result po authentication.

Neloguj key material, session keys, raw keytab alebo reusable ticket blobs do bežných logs. Ticket/client/service identifiers sú citlivé metadata a potrebujú access/retention policy.

## 38. Client-side troubleshooting

Začni od initial credentials:

```bash
kinit alice@EXAMPLE.COM
klist -ef
kvno HTTP/app.example.com@EXAMPLE.COM
```

`kinit` testuje realm/KDC discovery, client principal, pre-auth a password/key. `klist` ukáže TGT, validity, flags a enctypes. `kvno` požiada o service ticket a ukáže jeho key version podľa toolu.

MIT Kerberos trace environment môže zobraziť discovery, requests, selected enctypes a cache behavior. Trace obsah môže byť citlivý a nemá sa bez redaction publikovať.

## 39. Service-side troubleshooting

Service musí vedieť:

- ktorý SPN client žiada;
- ktorý account/key SPN vlastní;
- ktoré principals/KVNO/enctypes obsahuje keytab;
- pod akou OS identity process beží;
- akú keytab/cache location používa;
- či hostname/proxy canonicalization sedí;
- či GSS mechanismus a mutual auth sú enabled;
- ako authenticated principal mapuje na local user/role.

Test musí používať rovnaký hostname a network path ako reálny client. Test cez `localhost` môže žiadať úplne iný SPN.

## 40. Failure-domain troubleshooting flow

```text
1. čas synchronizovaný?
2. DNS, realm a KDC discovery správne?
3. client principal existuje a pre-auth uspeje?
4. TGT bol vydaný a je validný?
5. client žiada správny service principal?
6. TGS vydal service ticket?
7. service keytab/account obsahuje správny principal, KVNO a enctype?
8. AP exchange a replay cache uspeli?
9. GSSAPI/SPNEGO vyjednali Kerberos, nie fallback?
10. application identity mapping a authorization uspeli?
```

„Kerberos nefunguje“ je príliš broad diagnóza. Rozdeľ AS, TGS, AP a application authorization.

## 41. Common errors vysvetlené

**Client not found in Kerberos database** — KDC nepozná requested client principal. Over realm suffix, account existence, aliases a správny KDC.

**Server not found in Kerberos database** — requested service principal/SPN neexistuje v realm-e alebo client vytvoril nesprávny hostname.

**Clock skew too great** — timestamp je mimo accepted window. Over client, KDC aj service time source, nie iba local clock display.

**Key table entry not found** — application nenašla requested principal/enctype v selected keytab-e alebo číta inú keytab path.

**Cannot decrypt ticket / KVNO mismatch** — ticket bol encrypted key versionou, ktorú service nemá, alebo SPN patrí inému accountu.

**Credentials cache not found** — process nemá TGT, používa inú OS identity/session alebo environment ukazuje na inú cache.

**Message stream modified / integrity failure** — môže ísť o key mismatch, broken token handling, proxy modification alebo GSS protection error podľa protocolu.

## 42. Attacks

**Password guessing / AS-REP roasting** — principal bez pre-auth umožní offline verification password-derived keyu.

**Kerberoasting** — attacker s domain accessom získa service ticket a skúša offline guess service-account passwordu.

**Pass-the-ticket** — stolen TGT/service ticket a session material sa použije bez passwordu.

**Keytab theft** — attacker získa long-term service key a môže service impersonovať alebo decryptovať tickets.

**Forged tickets** — compromise TGS/domain keys umožní vytvoriť tickets, ktoré sa javia ako KDC-issued.

**Unconstrained delegation abuse** — compromised delegated host získa high-value user credentials.

**Legacy enctype downgrade** — slabší algorithm uľahčí offline attacks alebo poruší policy.

**SPN manipulation** — attacker s directory write permissions môže presmerovať service identity alebo vytvoriť delegation path.

## 43. Controls

- required pre-authentication a strong modern authentication;
- long random/managed service-account credentials;
- AES enctypes a removal legacy algorithms;
- protected KDC/domain-controller administration;
- restrictive keytab/cache permissions;
- short ticket lifetimes podľa risku;
- minimal forwarding/delegation;
- constrained/resource-based delegation;
- SPN ownership monitoring a duplicate detection;
- gMSA alebo managed key rotation v AD;
- privileged tiering;
- actual mechanism monitoring, aby NTLM fallback neukryl problém;
- incident response a realm/forest recovery drills.

Každý control rieši inú boundary. Strong service password nezabráni theft already issued TGT-u; short ticket lifetime nevyrieši KDC compromise.

## 44. Service-key rotation

Bezpečný rotation flow:

```text
inventarizovať principal, SPNs a consumers
→ vytvoriť novú key version
→ distribuovať nový keytab/managed credential
→ potvrdiť, že všetky service instances vedia decryptovať new tickets
→ ponechať bounded overlap pre old tickets
→ odstrániť old key
→ reload/restart services podľa implementation
→ monitorovať KVNO a authentication failures
```

Pri compromise overlap minimalizuj a posúď already-issued tickets a application sessions. Rotation keyu neodstráni stolen tickets automaticky.

## 45. KDC alebo domain compromise

Compromise KDC/TGS alebo AD domain trust keys má realm-wide impact. Rotation jedného service keyu nestačí.

Recovery môže vyžadovať:

- isolation affected domain controllers/KDCs;
- preservation security logs a directory state;
- rotation high-value realm keys podľa platform-specific staged procedure;
- reset privileged/user/service credentials;
- invalidation trust relationships;
- rebuild KDC/domain infrastructure zo trusted state;
- review forged tickets, delegation a persistence;
- forest/domain recovery plan v AD.

Improvised simultaneous key reset bez understanding replication/ticket overlap môže spôsobiť outage alebo incomplete recovery.

## 46. Časté anti-patterny

**Keytab v Git-e alebo image.** Long-term service credential sa stane durable a kopírovateľný.

**DNS alias bez SPN plánu.** Client žiada ticket pre name, ktorý service key nepozná.

**Shared keytab pre unrelated services.** Compromise jednej application otvorí viac principals.

**Vypnutá time validation.** Replay protection sa odstráni namiesto opravy clocku.

**Unconstrained delegation pre pohodlie.** Front-end host dostane neprimeranú user authority.

**NTLM fallback považovaný za Kerberos success.** SPN/keytab problem ostáva neviditeľný.

**Authentication považovaná za authorization.** Platný ticket neoveruje object, tenant ani business permission.

**Rotation bez KVNO/overlap plánu.** Časť fleet-u nedokáže decryptovať nové alebo ešte platné old tickets.

## 47. Kompletný príklad HTTP Kerberos loginu

User `alice@EXAMPLE.COM` otvorí `https://app.example.com` na domain workstation-e.

1. Workstation má validný TGT v user credential cache.
2. Browser podľa HTTP Negotiate policy vytvorí request pre SPN `HTTP/app.example.com@EXAMPLE.COM`.
3. Client pošle TGT + authenticator TGS-u a dostane service ticket.
4. Browser odošle SPNEGO/GSS token application endpointu cez HTTPS.
5. Service alebo front-end decryptne ticket keytabom/SPN account keyom a overí authenticator/replay.
6. Mutual authentication podľa GSS contextu môže potvrdiť service clientovi.
7. Application mapuje Kerberos principal na local account a načíta authorization attributes z trusted source.
8. Resource-level policy rozhodne, ktoré reports Alice smie čítať.
9. Audit spojí client principal, service principal, mechanism, source a authorization result.
10. Ak browser fallbackne na NTLM, monitoring to označí ako odlišný mechanismus a incident/troubleshooting signal.

## 48. Kontrolné otázky

1. Prečo Kerberos neposiela user password každej service?
2. Ako sa realm, DNS domain a principal líšia?
3. Čo SPN identifikuje a prečo duplicate SPN spôsobí problém?
4. Aké role majú AS, TGS a KDC database?
5. Ako sa TGT a service ticket líšia?
6. Čo sa deje v AS, TGS a AP exchange?
7. Čo authenticator dokazuje a ako pomáha proti replayu?
8. Aké session keys Kerberos vytvára?
9. Prečo credential cache a keytab predstavujú odlišné secrets?
10. Na čo slúži KVNO a ako vyzerá safe overlap pri rotation?
11. Ako sa long-term, ticket a session enctypes líšia?
12. Prečo Kerberos závisí od času a DNS?
13. Aké security dôsledky majú renewable a forwardable flags?
14. Ako delegation mení actor chain a blast radius?
15. Ako cross-realm trust vytvára authentication path bez automatic authorization?
16. Ako PAC súvisí s Windows authorization?
17. Ako sa Kerberos, LDAP, TLS a GSS-API dopĺňajú?
18. Ako rozlíšiť AS, TGS, AP a application-authorization failure?
19. Ako vzniká Kerberoasting a ktoré controls ho obmedzujú?
20. Ako reagovať na compromised service key oproti compromised KDC/domainu?

## Glossary impact

Relevantné pojmy: Kerberos, realm, principal, Service Principal Name, Key Distribution Center, Authentication Service, Ticket-Granting Service, long-term key, ticket, Ticket-Granting Ticket, service ticket, AS exchange, pre-authentication, TGS exchange, AP exchange, authenticator, session key, credential cache, keytab, Key Version Number, encryption type, string-to-key, clock skew, ticket lifetime, ticket flags, renewable ticket, forwardable ticket, delegation, unconstrained delegation, constrained delegation, cross-realm trust, inter-realm key, Active Directory Kerberos, Privilege Attribute Certificate, GSS-API, SPNEGO, HTTP Negotiate, pass-the-ticket, AS-REP roasting a Kerberoasting.

## Primárne zdroje

- [RFC 4120 — The Kerberos Network Authentication Service V5](https://www.rfc-editor.org/rfc/rfc4120)
- [RFC 4121 — Kerberos V5 GSS-API Mechanism](https://www.rfc-editor.org/rfc/rfc4121)
- [RFC 6113 — Kerberos Pre-Authentication Framework](https://www.rfc-editor.org/rfc/rfc6113)
- [MIT Kerberos documentation](https://web.mit.edu/kerberos/krb5-latest/doc/)
- [MIT Kerberos application servers](https://web.mit.edu/kerberos/krb5-latest/doc/admin/appl_servers.html)
- [MIT Kerberos keytab](https://web.mit.edu/kerberos/krb5-latest/doc/basic/keytab_def.html)
- [MIT Kerberos encryption types](https://web.mit.edu/kerberos/krb5-latest/doc/admin/enctypes.html)
- [Microsoft Kerberos authentication overview](https://learn.microsoft.com/en-us/windows-server/security/kerberos/kerberos-authentication-overview)
- [Microsoft Service Principal Names](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-service-accounts)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: LDAP](ldap.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: OAuth 2.0 →](oauth-2.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
