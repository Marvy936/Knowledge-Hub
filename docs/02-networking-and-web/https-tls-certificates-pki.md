# HTTPS, TLS, certificates a PKI

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [HTTP](http.md), [DNS](dns.md), [TCP a UDP](tcp-and-udp.md)
- Súvisiace témy: mTLS, certificate rotation, OCSP, HSTS, cipher suites, trust stores

## 1. Definícia

HTTPS je HTTP prenášané cez TLS. TLS vytvorí autentifikovaný a šifrovaný channel medzi dvoma transportnými endpointmi.

TLS typicky poskytuje:

- dôvernosť dát počas prenosu;
- integritu a detekciu neoprávnenej zmeny;
- autentifikáciu servera cez certificate a proof of private-key possession;
- voliteľnú autentifikáciu klienta cez mutual TLS;
- negotiation verzie, cryptographic algorithms a aplikačného protokolu.

TLS neposkytuje:

- dôveryhodnosť business obsahu;
- správnu authorization policy;
- ochranu dát po dešifrovaní na endpoint-e;
- ochranu kompromitovaného private key alebo procesu;
- automatickú ochranu proti aplikačným chybám, phishingu alebo SSRF.

## 2. Celý HTTPS lifecycle

```text
URL
  ↓ DNS resolution
IP a route
  ↓ TCP alebo QUIC connection
TLS ClientHello
  ↓ negotiation a certificate
certificate path validation
  ↓ key agreement a Finished
šifrovaný channel
  ↓ HTTP request/response
session reuse alebo close
  ↓ certificate renewal/rotation/revocation
```

Pri incidente urč, v ktorej fáze sa komunikácia zastavila. HTTP status existuje až po úspešnom TLS handshake. Certificate error preto nie je HTTP chyba a `503` nie je TLS negotiation failure.

## 3. Threat model TLS

TLS chráni proti protivníkovi, ktorý dokáže pozorovať, blokovať, meniť alebo vkladať traffic na network path, ale nemá platnú endpoint identity ani session keys.

TLS má tri hlavné ciele:

1. **Authentication** — klient overí, že peer prezentuje identity akceptovanú trust policy.
2. **Key agreement** — obe strany odvodia spoločné session secrets bez ich priameho prenosu.
3. **Record protection** — application data sa šifrujú a autentifikujú odvodenými keys.

Ak klient vypne certificate verification, stále môže mať šifrované spojenie, ale nevie, s kým komunikuje. Aktívny útočník môže vytvoriť dve samostatné TLS sessions a vystupovať ako man-in-the-middle.

## 4. Symmetric a asymmetric cryptography

TLS kombinuje viac cryptographic primitív.

### Asymmetric cryptography

Používa odlišný public a private key. V TLS slúži najmä na:

- podpis handshake transcriptu;
- preukázanie držby private key zodpovedajúceho certifikátu;
- autentifikáciu CA signatures;
- key agreement cez ephemeral Diffie-Hellman mechanizmy.

### Symmetric cryptography

Používa rovnaký odvodený secret pre encryption/decryption v danom smere. Je výrazne efektívnejšia pre bulk data.

Server private key teda nešifruje každý HTTP byte. Handshake vytvorí session traffic keys a tie chránia TLS records.

### Hash a AEAD

Moderné TLS používa hash functions pre transcript a key derivation. AEAD algoritmy kombinujú encryption a integrity tak, aby receiver vedel odhaliť zmenu ciphertextu alebo associated metadata.

## 5. X.509 certificate

Certificate je podpísaný dokument, ktorý viaže public key na identity claims a policy metadata.

Typické polia:

- **Subject** — pomenovanie držiteľa; pri server identity nie je samo osebe rozhodujúce;
- **Subject Alternative Name** — DNS names alebo IP identities, pre ktoré je certificate platný;
- **Issuer** — CA, ktorá certificate podpísala;
- **Validity** — `notBefore` a `notAfter`;
- **Public key** — key a algoritmus;
- **Key Usage** — povolené kryptografické použitia;
- **Extended Key Usage** — napríklad server authentication alebo client authentication;
- **Basic Constraints** — či certificate môže byť CA;
- **Name Constraints** — obmedzenie names, ktoré môže podriadená CA vydávať;
- **Serial Number** — identifikátor v rámci issuera;
- **Signature Algorithm** — algoritmus, ktorým issuer podpísal certificate;
- **Authority/Subject Key Identifier** — pomoc pri zostavovaní chainu;
- **CRL Distribution Points a AIA** — odkazy súvisiace s revocation a issuerom.

Certificate je verejný. Security závisí od ochrany private key a od validity trust pathu.

## 6. Hostname verification

Klient neoveruje iba podpis chainu. Musí overiť, že hostname použitý pre connection zodpovedá certificate identity.

Pre URL:

```text
https://api.example.com/
```

klient hľadá `api.example.com` v SAN DNS entries.

Wildcard:

```text
*.example.com
```

typicky pokrýva `api.example.com`, ale nie `a.b.example.com` ani apex `example.com`.

Pri connection na IP adresu musí certificate obsahovať zodpovedajúcu IP SAN; DNS SAN s textom podobným IP nie je to isté.

Common Name je historický fallback a nemá byť jediným identity source v modernom návrhu.

## 7. PKI a chain of trust

```text
Trust anchor / Root CA
  ↓ podpis a constraints
Intermediate CA
  ↓ podpis a constraints
Leaf/server certificate
```

Klient má lokálny trust store s roots alebo explicitnými trust anchors. Server typicky posiela:

- leaf certificate;
- jeden alebo viac intermediate certificates.

Root sa zvyčajne neposiela ako dôkaz dôvery, pretože peer si nemôže sám vytvoriť dôveryhodnosť tým, že pošle vlastný root. Dôvera vzniká z klientovej local policy.

## 8. Certificate path building a validation

Klient musí najprv zostaviť možnú path a potom ju validovať.

Zjednodušený validation model:

1. leaf zodpovedá požadovanému hostname;
2. každý certificate je v platnom časovom intervale;
3. signature každého child certificate overí issuer public key;
4. chain končí v trusted anchor;
5. intermediate certificates majú `CA=true` a správne key usage;
6. path length a name constraints sa neporušujú;
7. leaf má povolené server authentication usage;
8. algorithms a key sizes spĺňajú client policy;
9. prípadná revocation policy je splnená;
10. application-specific policy neodmietla issuer alebo identity.

Rôzne klienty môžu zostaviť odlišnú chain path, ak existujú cross-signatures alebo viac intermediates. Preto „funguje v jednom browseri“ nie je dôkaz univerzálnej interoperability.

## 9. Root a intermediate CA lifecycle

Root private key predstavuje najvyšší blast radius. Bežne je:

- offline alebo v silno chránenom HSM;
- používaný zriedka;
- dlhšie platný;
- chránený multiperson controlom.

Intermediate CA umožňuje:

- oddeliť issuance policy;
- obmedziť name scope;
- použiť kratšiu validity;
- rotovať issuing layer bez okamžitej výmeny všetkých roots;
- oddeliť server, client, device alebo environment identity.

Kompromitovaný intermediate môže vydávať identity v rozsahu svojich constraints. Preto nesmie byť „bežným signing key“ uloženým rovnako ako application secret.

## 10. TLS 1.3 handshake

Zjednodušený full handshake:

```text
Client                                               Server
  | ---- ClientHello -------------------------------> |
  |      versions, cipher suites, key_share,           |
  |      SNI, ALPN, extensions                         |
  | <--- ServerHello -------------------------------- |
  |      selected version, cipher, key_share           |
  | <--- EncryptedExtensions ------------------------- |
  | <--- Certificate -------------------------------- |
  | <--- CertificateVerify -------------------------- |
  | <--- Finished ----------------------------------- |
  | ---- Finished ----------------------------------> |
  | ===== application data protected by traffic keys = |
```

`ClientHello` je dôležitý control message. Obsahuje capabilities a kontext, podľa ktorého server alebo edge vyberie virtual host a protokol.

Po ephemeral key agreement obe strany odvodia handshake keys. Server pošle certificate a `CertificateVerify`, ktorým podpisuje handshake transcript. Tým preukáže držbu private key.

`Finished` autentifikuje celý dovtedajší transcript. Ak bol handshake po ceste zmenený, verification zlyhá.

TLS 1.3 šifruje väčšinu serverových handshake messages po `ServerHello`, ale počiatočný ClientHello môže byť bez ďalších mechanizmov pozorovateľný.

## 11. TLS 1.2 verzus TLS 1.3

TLS 1.3 odstránilo alebo zjednodušilo viac legacy možností:

- nepoužíva statický RSA key exchange;
- vyžaduje moderné AEAD ciphers;
- znižuje počet round trips;
- oddeľuje cipher suite od authentication a key-exchange voľby;
- preferuje ephemeral key agreement a forward secrecy;
- mení session resumption na PSK/ticket model;
- podporuje 0-RTT early data s replay rizikom.

Staršie protokolové verzie zvyšujú compatibility, ale aj attack surface a policy complexity. Support matrix musí byť explicitný a meraný podľa reálnych klientov.

## 12. SNI

Server Name Indication prenáša hostname v ClientHello:

```text
SNI = api.example.com
```

Jeden endpoint tak môže vybrať správny certificate a TLS policy pre viac domains.

Bez SNI alebo pri nesprávnom SNI môže server poslať default certificate. Handshake môže kryptograficky prebehnúť, ale hostname verification zlyhá.

Test:

```bash
openssl s_client \
  -connect 203.0.113.10:443 \
  -servername api.example.com
```

Pri testovaní cez IP musíš oddeliť:

- destination IP pre TCP;
- SNI pre TLS virtual host;
- HTTP `Host` alebo `:authority` pre aplikačný route.

Tieto tri hodnoty môžu byť rovnaké logicky, ale sú spracované v rozdielnych fázach.

## 13. ALPN

Application-Layer Protocol Negotiation umožní stranám počas TLS handshake vybrať aplikačný protokol.

Príklady:

```text
http/1.1
h2
h3
```

ALPN zabráni tomu, aby obe strany po úspešnom TLS spojení očakávali inú wire syntax.

Ak client ponúka `h2,http/1.1` a server vyberie `h2`, následné bytes musia byť HTTP/2 frames. Nesprávna proxy, ktorá tvrdí `h2`, ale spracúva iba HTTP/1.1, vytvorí protocol failure po úspešnom handshake.

## 14. Cipher suites, groups a signatures

Cryptographic negotiation má viac samostatných častí:

- protocol version;
- symmetric AEAD cipher a hash;
- key-exchange group, napríklad elliptic curve;
- server certificate key type;
- signature algorithm;
- client authentication policy.

V TLS 1.3 cipher suite už neurčuje celý balík key exchange + authentication ako v starších verziách.

Policy má odstrániť zastarané versions, weak ciphers, anonymous suites, slabé signatures a nevyhovujúce key sizes. Nemá však byť kopírovaná bez overenia klientov, HSM podpory, compliance a performance.

## 15. Forward secrecy

Pri ephemeral Diffie-Hellman key agreement nevznikne session secret iba z dlhodobého server private key. Každý handshake má ephemeral contribution.

Dôsledok:

```text
neskorší únik server private key
≠
automatické dešifrovanie historicky zachytených sessions
```

Forward secrecy nechráni session, ak útočník kompromitoval endpoint počas jej behu, získal session keys alebo aktívne ovládal server.

## 16. TLS records a application data

Po handshake TLS rozdelí application bytes do records. Každý smer má vlastné traffic keys a sequence state.

Record protection zabezpečuje:

- encryption;
- integrity;
- ordering/detection podľa record state;
- oddelenie handshake a application traffic phases.

TLS zachováva transport semantics. Nad TCP stále vidí ordered byte stream; nad QUIC sú encryption a packet/stream vrstvy integrované odlišne.

Packet capture bez session keys neukáže HTTP payload, ale stále môže ukázať IPs, ports, packet sizes, timing, handshake metadata a niektoré negotiation fields.

## 17. Session resumption

Full handshake je nákladnejší než obnovenie existujúceho security contextu. TLS podporuje resumption cez tickets alebo PSK model.

Výhody:

- menej round trips;
- menej asymmetric operations;
- nižšia CPU záťaž;
- rýchlejšie short-lived requests.

Prevádzkové požiadavky:

- ticket encryption keys musia mať rotation lifecycle;
- load-balanced endpoints musia zdieľať alebo koordinovať resumption state, ak sa očakáva cross-node reuse;
- kompromitovaný ticket key môže zväčšiť blast radius;
- monitoring musí odlíšiť full a resumed handshakes;
- staré ticket keys sa musia držať dostatočne dlho pre overlap, ale nie neobmedzene.

## 18. TLS 1.3 0-RTT

Pri 0-RTT môže klient poslať early application data spolu s resumed handshake.

Výhodou je nižšia latency. Zásadným obmedzením je replay:

```text
útočník zachytí validné early data
  ↓
odošle ich znova inému alebo rovnakému endpointu
```

0-RTT sa nemá používať pre ne-idempotentné operácie, finančné transakcie, token issuance ani state changes bez explicitnej anti-replay a deduplication architektúry.

Transportné označenie „early data accepted“ nie je business idempotency.

## 19. Certificate issuance lifecycle

```text
identity a scope definition
  ↓
private key generation
  ↓
CSR alebo automatizovaný request
  ↓
identity validation
  ↓
issuance
  ↓
secure distribution
  ↓
deployment a reload
  ↓
validation a monitoring
  ↓
renewal/rotation overlap
  ↓
revocation alebo expiry
```

Každá fáza môže zlyhať. Najčastejší outage nevzniká zlomením cryptography, ale tým, že nový certificate nebol vydaný, distribuovaný, načítaný alebo dôveryhodný pre všetkých klientov.

## 20. Private key ownership

Private key má byť generovaný a uložený v security boundary, ktorá zodpovedá threat modelu:

- local file s prísnymi permissions;
- OS key store;
- cloud key manager;
- HSM;
- secrets platforma;
- workload identity agent.

Otázky:

- kto môže key čítať alebo používať;
- či je exportovateľný;
- ako sa zálohuje alebo obnovuje;
- ako sa rotuje;
- ako sa auditujú podpisové operácie;
- čo sa stane pri kompromitácii;
- či všetky replicas používajú rovnaký key.

Kopírovanie jedného wildcard private key na desiatky tímovo nezávislých serverov zvyšuje blast radius aj revocation náročnosť.

## 21. CSR a proof of possession

Certificate Signing Request obsahuje public key a požadované identity alebo attributes, podpísané zodpovedajúcim private key.

CSR dokazuje držbu private key, ale CA musí stále overiť, či requester smie získať dané names a usages.

CA nemá automaticky dôverovať všetkým fields z CSR. Issuance policy má určovať:

- povolené SANs;
- validity;
- key algorithms;
- EKU;
- CA constraints;
- environment a owner;
- audit metadata.

## 22. ACME

ACME automatizuje domain validation, issuance a renewal.

Bežné challenge modely:

- HTTP challenge — CA overí token cez konkrétny HTTP path;
- DNS challenge — CA overí TXT record a umožňuje aj wildcard issuance;
- TLS-based challenge — overenie cez TLS endpoint podľa implementácie.

Kompletná automatizácia musí riešiť:

1. account key a oprávnenia;
2. challenge routing alebo DNS write;
3. rate limits a retry policy;
4. key generation;
5. issuance;
6. atomic deployment certifikátu a key;
7. syntax validation;
8. reload bez výpadku;
9. post-deploy handshake test;
10. expiry a renewal monitoring.

„Certificate bol vydaný“ nie je úspech, ak služba stále prezentuje starý serial.

## 23. Wildcard a multi-SAN certificates

Wildcard znižuje počet certifikátov, ale rozširuje scope private key.

Multi-SAN certificate môže pokrývať viac konkrétnych names. Trade-offy:

- jednoduchšie centralizované endpointy;
- väčší blast radius pri key compromise;
- zložitejšia ownership koordinácia;
- certificate transparency odhalí všetky public names;
- zmena jedného name môže vyžadovať rotation celého certificate;
- veľký SAN list zväčšuje handshake metadata.

Preferuj scope zodpovedajúci jednej prevádzkovej a bezpečnostnej hranici, nie najväčší možný certificate.

## 24. Trust stores

Dôvera je lokálna client policy. Rôzne runtime môžu používať odlišné stores:

- operačný systém;
- browser-specific store;
- Java truststore;
- Python/OpenSSL CA bundle;
- container image CA package;
- application-bundled trust anchors;
- device firmware store.

Preto môže endpoint fungovať v browseri a zlyhať v Java service.

Trust-store drift vzniká, keď:

- image má starý CA bundle;
- runtime ignoruje OS store;
- private CA nebola distribuovaná do všetkých workloads;
- starý root bol odstránený;
- cross-signed chain sa zostavila inak;
- proxy pridáva vlastnú inspection CA.

## 25. Private PKI

Interné služby často používajú private CA. Prevádzka private PKI zahŕňa viac než vydanie root certificate.

Potrebuje:

- offline alebo silno chránený root;
- issuing intermediates;
- issuance authentication a authorization;
- inventory identities a ownerov;
- krátke validity a automatickú rotation;
- trust distribution;
- revocation alebo rýchlu reissuance;
- audit a key ceremony;
- disaster recovery;
- oddelenie production a non-production trust domains.

Ak každý tím môže vydávať ľubovoľné names z jednej CA, mTLS identity prestáva byť spoľahlivou authorization input.

## 26. Mutual TLS

Pri mTLS sa autentifikujú obe strany.

```text
server certificate
  → klient validuje server identity

client certificate
  → server validuje client identity
```

Server môže poslať `CertificateRequest` s informáciou o akceptovaných authorities alebo signature algorithms.

Client certificate identity môže byť odvodená zo SAN, URI, SPIFFE-like identifier alebo explicitného mappingu.

mTLS rieši transportnú peer identity. Stále je potrebné rozhodnúť:

- ktoré CA sú akceptované;
- ktoré identity smú volať konkrétnu operáciu;
- ako sa mapuje certificate na service account alebo tenant;
- ako sa revokuje kompromitovaný workload;
- ako sa rotuje bez prerušenia long-lived connections;
- či proxy terminácia zachováva alebo nahrádza client identity.

## 27. TLS termination, re-encryption a passthrough

### Termination

```text
Client --TLS--> Proxy --HTTP--> Upstream
```

Proxy vlastní external certificate, dešifruje request a vidí L7 obsah. Interný plaintext môže byť prijateľný iba v explicitne dôveryhodnej boundary.

### Re-encryption

```text
Client --TLS--> Proxy --TLS--> Upstream
```

Existujú dve samostatné TLS sessions. Proxy je server voči klientovi a client voči upstreamu. Každá session má vlastný SNI, ALPN, trust store, certificate a timeout.

### Passthrough

```text
Client --TLS-----------------> Upstream
           L4/SNI routing
```

Balancer nevidí dešifrovaný HTTP obsah. Certificate a TLS policy vlastní upstream.

Pri diagnostike musíš presne vedieť, kde sa TLS končí. Inak budeš kontrolovať nesprávny certificate alebo trust store.

## 28. Client identity cez proxy

Ak edge terminates mTLS a upstream už nedostane client certificate, proxy môže preniesť overenú identity cez header alebo metadata channel.

Taký header je dôveryhodný iba ak:

- upstream prijíma traffic výhradne z trusted proxy;
- proxy odstráni client-supplied verziu;
- channel proxy → upstream je chránený;
- identity mapping je auditovaný;
- neexistuje bypass route k upstreamu.

„X-Client-Cert“ bez trust-boundary designu nie je mTLS end-to-end identity.

## 29. Revocation

Certificate môže byť zneplatnený pred expiry, napríklad po key compromise alebo chybnom issuance.

Mechanizmy:

- **CRL** — podpísaný zoznam revoked serials;
- **OCSP** — online query na status konkrétneho certificate;
- **OCSP stapling** — server prikladá časovo obmedzenú podpísanú odpoveď;
- krátko žijúce certificates — znižujú dobu expozície a závislosť od online revocation.

Revocation má trade-offy:

- responder outage;
- privacy, pretože query odhaľuje navštevovaný certificate;
- cache a freshness;
- rozdielny fail-open/fail-closed behavior klientov;
- propagation delay;
- operatívna zložitosť.

Revocation policy musí byť súčasťou client implementation, nie iba položka v CA dokumentácii.

## 30. Certificate Transparency

Verejne dôveryhodné certificates sú typicky zapisované do Certificate Transparency logs. CT umožňuje domain ownerom monitorovať nečakané issuance.

CT:

- nezabraňuje samotnému chybnému issuance;
- poskytuje auditovateľnú evidenciu;
- môže odhaliť subdomain names;
- vyžaduje monitoring a response proces;
- nie je náhradou za hostname validation alebo revocation.

## 31. Certificate rotation bez outage

Bezpečný rotation model:

1. vydaj nový certificate alebo trust anchor;
2. over SAN, chain, validity, key usage a private-key match;
3. distribuuj nový trust pred identity cutoverom, ak sa mení CA;
4. nasadzuj nový certificate postupne;
5. zachovaj overlap starého a nového trustu;
6. reloadni alebo reštartuj službu podľa podporovaného lifecycle;
7. over handshake na každom endpoint-e a každej path;
8. sleduj serial/fingerprint z reálneho klientského pohľadu;
9. odstráň starý certificate až po potvrdení adoption;
10. revoke starý key pri kompromitácii alebo podľa policy.

Pri load balanceri môže časť nodes stále prezentovať starý certificate. Jeden úspešný test nestačí; opakuj testy cez všetky VIPs, regions a backendy.

## 32. Trust-anchor rotation

Rotácia root alebo private CA je náročnejšia než leaf renewal.

Model „najprv trust, potom use, potom remove“:

```text
clients trust old CA
  ↓ pridaj new CA
clients trust old + new
  ↓ začni vydávať z new CA
servers používajú new chain
  ↓ počkaj na adoption
odstráň old CA
```

Ak server začne používať new CA skôr, než ju klienti trustujú, vznikne outage. Ak old CA zostane neobmedzene, znižuje sa bezpečnostný efekt rotation.

## 33. Expiry monitoring

Monitorovanie iba certificate súboru na disku nestačí. Potrebuješ testovať certificate prezentovaný reálnym endpointom.

Sleduj:

- dni do `notAfter`;
- `notBefore` a clock skew;
- hostname coverage;
- chain completeness;
- issuer a trust anchor;
- key a signature algorithm;
- leaf serial/fingerprint;
- renewal job;
- secret distribution;
- reload success;
- OCSP stapling status;
- všetky regions, listeners a SNI variants.

Alert musí mať dostatočný predstih na opravu issuance, DNS challenge, approval a deployment problémov.

## 34. HSTS

Server môže poslať:

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

Browser si zapamätá, že daný host má používať iba HTTPS. HSTS znižuje riziko downgrade a prvotného HTTP redirect interception po tom, čo policy bezpečne prijal.

Dôležité:

- header sa prijíma iba cez validné HTTPS;
- `includeSubDomains` rozširuje záväzok na všetky subdomains;
- preload je dlhodobé rozhodnutie a recovery je pomalá;
- všetky zahrnuté subdomains musia mať funkčné HTTPS;
- HSTS neopraví neplatný certificate.

## 35. Certificate pinning

Pinning obmedzí akceptovanú identity na konkrétny public key, SPKI hash alebo úzky chain.

Výhoda je menší trust scope. Nevýhoda je vysoké rotation a recovery riziko.

Bezpečný pinning potrebuje:

- aspoň jeden backup key/pin;
- overlap;
- update channel;
- emergency recovery;
- jasný expiry;
- monitoring pin adoption.

Hard-coded jediný leaf fingerprint môže zmeniť bežnú renewal na klientsky outage, ktorý nemožno opraviť server-side.

## 36. TLS inspection

Enterprise forward proxy môže terminovať client TLS a vytvoriť nové TLS spojenie k originu.

To vyžaduje, aby klient dôveroval inspection CA. Proxy potom môže vidieť a meniť plaintext.

Security dôsledky:

- proxy je high-value trust boundary;
- musí overovať origin certificates aspoň rovnako prísne ako klient;
- môže rozbiť certificate pinning alebo mTLS;
- dešifrované dáta a keys musia byť chránené;
- logging nesmie zachytávať credentials;
- používateľ musí rozumieť, že nejde o end-to-end TLS k originu.

## 37. Praktická diagnostika

```bash
curl -v https://api.example.com/

openssl s_client \
  -connect api.example.com:443 \
  -servername api.example.com \
  -showcerts

openssl x509 -in cert.pem -noout -text
openssl verify -CAfile ca-bundle.pem -untrusted intermediate.pem leaf.pem
```

Diagnostický tok:

1. over DNS a destination IP;
2. over TCP alebo QUIC reachability;
3. zaznamenaj ClientHello capabilities, ak je to potrebné;
4. pošli správne SNI;
5. zisti selected TLS version, cipher a ALPN;
6. ulož celý presented chain;
7. over SAN voči hostname;
8. over validity pri správnom čase;
9. over chain voči konkrétnemu trust store;
10. skontroluj EKU, constraints a algorithm policy;
11. skontroluj revocation/stapling podľa client policy;
12. až potom pokračuj HTTP diagnostikou.

## 38. Typické failure patterns

### `certificate has expired`

Leaf alebo intermediate je po `notAfter`, prípadne klientsky čas je nesprávny. Over certificate reálne prezentovaný endpointom, nie iba súbor v secret store.

### `certificate is not yet valid`

`notBefore` je v budúcnosti alebo klient/server má clock skew. Časté pri okamžitom cutover-e na nový certificate a nesynchronizovanom čase.

### `unable to get local issuer certificate`

Server neposlal potrebný intermediate, klient nemá správny issuer alebo chain builder zvolil inú path.

### Hostname mismatch

SNI/hostname nie je v SAN, client používa IP alebo server poslal default certificate.

### Funguje v browseri, nie v aplikácii

Rozdielny trust store, AIA fetching, proxy, TLS version, SNI, ALPN, hostname alebo chain building.

### Po rotation zlyháva iba časť klientov

Starý trust store, chýbajúci cross-sign/overlap, pinning, neúplný chain alebo časť balancer nodes stále prezentuje starý certificate.

### TLS handshake uspeje, ale HTTP/2 nie

Over ALPN, proxy protocol support, negotiated protocol a HTTP/2 implementation. TLS success neznamená správny application protocol.

### mTLS klient je odmietnutý

Over, či server vôbec žiada client certificate, akceptované issuers, client EKU, chain, validity, identity mapping a authorization policy.

## 39. Časté omyly

### „HTTPS znamená, že služba je obsahovo dôveryhodná“

Nie. TLS overuje identity podľa PKI a chráni channel. Nehodnotí business čestnosť ani správnosť obsahu.

### „Certificate šifruje všetky dáta“

Certificate nesie public key a identity claims. Session data chránia odvodené symmetric traffic keys.

### „Keď certificate nie je expired, je validný“

Musí sedieť hostname, chain, trust, usages, constraints, revocation a algorithm policy.

### „Server pošle root a tým dokáže dôveru“

Nie. Trust anchor musí byť lokálne akceptovaný klientom.

### „mTLS automaticky vyrieši authorization“

Nie. Poskytne peer identity. Aplikačná alebo infraštruktúrna policy musí rozhodnúť, čo identity smie robiť.

### „TLS termination na proxy znamená end-to-end encryption“

Nie, ak proxy posiela plaintext upstreamu. Existujú dve oddelené trust boundaries.

## 40. Praktický checklist

Pred nasadením TLS endpointu over:

- správne SANs a SNI routing;
- private key ownership a permissions;
- leaf + complete intermediate chain;
- server authentication EKU;
- podporované TLS versions, ciphers, groups a signatures;
- ALPN pre očakávané protokoly;
- session ticket rotation;
- 0-RTT policy;
- trust-store coverage klientov;
- expiry a presented-certificate monitoring;
- OCSP/revocation policy;
- HSTS scope;
- termination/re-encryption/passthrough boundary;
- mTLS identity a authorization mapping;
- rotation overlap a rollback path.

## 41. Kontrolné otázky

1. Ktoré bezpečnostné vlastnosti TLS poskytuje a ktoré nie?
2. Prečo server private key nešifruje celý HTTP prenos?
3. Aký je rozdiel medzi path building a certificate path validation?
4. Prečo server typicky neposiela root CA?
5. Ako CertificateVerify dokazuje držbu private key?
6. Načo slúžia SNI a ALPN a v ktorej fáze sa používajú?
7. Čo presne znamená forward secrecy?
8. Aké prevádzkové riziká prinášajú session tickets?
9. Prečo je TLS 1.3 0-RTT replay-sensitive?
10. Ako sa líši termination, re-encryption a passthrough?
11. Prečo mTLS identity nie je automaticky authorization?
12. Ako vzniká trust-store drift?
13. Ako navrhneš leaf certificate rotation bez outage?
14. Prečo musí trust-anchor rotation používať poradie trust → use → remove?
15. Ako diagnostikuješ endpoint fungujúci v browseri, ale nie v kontajnerovej aplikácii?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: HTTP](http.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: REST APIs a WebSockets →](rest-apis-and-websockets.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
