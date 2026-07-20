# HTTPS, TLS, certificates a PKI

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [HTTP](http.md), [DNS](dns.md), [TCP a UDP](tcp-and-udp.md)
- Súvisiace témy: mTLS, certificate rotation, OCSP, HSTS, cipher suites, trust stores

## 1. Definícia

HTTPS je HTTP prenášané cez TLS. TLS poskytuje:

- šifrovanie dát počas prenosu,
- integritu komunikácie,
- autentifikáciu servera pomocou certifikátu,
- voliteľne autentifikáciu klienta cez mTLS.

TLS nechráni kompromitovaný endpoint, neplatnú business authorization ani dáta po dešifrovaní v aplikácii.

## 2. Mentálny model

```text
DNS resolution
  ↓
TCP connection alebo QUIC connection
  ↓
TLS handshake
  ↓
HTTP request/response
```

Každá vrstva môže zlyhať samostatne. `curl: certificate verify failed` nie je HTTP chyba a `503` nie je TLS handshake chyba.

## 3. Symmetric a asymmetric cryptography

TLS kombinuje:

- asymmetric cryptography na authentication a key agreement,
- symmetric cryptography na efektívne šifrovanie aplikačných dát,
- hash/MAC alebo AEAD na integritu.

Server private key sa nepoužíva na šifrovanie celého HTTP prenosu. Handshake vytvorí session keys, ktorými sa následne šifrujú records.

## 4. Certificate

X.509 certificate viaže public key na identity claims a metadata.

Typické polia:

- Subject,
- Subject Alternative Name — SAN,
- Issuer,
- validity interval,
- public key,
- signature algorithm,
- key usage a extended key usage,
- serial number.

Hostname verification používa SAN. Common Name je historický mechanizmus a nemá byť jediným zdrojom identity.

## 5. PKI a chain of trust

```text
Root CA
  ↓ podpisuje
Intermediate CA
  ↓ podpisuje
Leaf/server certificate
```

Klient dôveruje root CA vo svojom trust store. Server počas handshake typicky posiela leaf certificate a potrebné intermediate certificates, nie root.

Klient overuje:

1. podpisový chain k dôveryhodnému rootu,
2. validity interval,
3. hostname v SAN,
4. key usage a policy,
5. prípadne revocation stav,
6. cryptographic algorithms.

## 6. Root a intermediate CA

Root private key je najcitlivejšia časť PKI a často zostáva offline.

Intermediate CA:

- obmedzuje blast radius,
- umožňuje oddeliť issuance policy,
- zjednodušuje rotation,
- môže mať kratšiu životnosť a constraints.

Kompromitovaný intermediate môže vydávať certifikáty v rozsahu svojich constraints.

## 7. TLS 1.3 handshake

Zjednodušene:

```text
ClientHello
- supported versions
- cipher suites
- key share
- SNI
- ALPN

ServerHello
- selected version
- selected parameters
- key share

EncryptedExtensions
Certificate
CertificateVerify
Finished

Client Finished
```

Po key agreement sú neskoršie handshake správy šifrované. TLS 1.3 odstránilo viacero legacy algoritmov a zjednodušilo cipher negotiation.

## 8. SNI

Server Name Indication prenáša hostname počas TLS handshake, aby jeden endpoint mohol prezentovať správny certifikát pre viac domén.

Bez správneho SNI môže server vrátiť default certificate.

Diagnostika:

```bash
openssl s_client -connect 203.0.113.10:443 -servername api.example.com
```

Pri testovaní IP adresy treba SNI a HTTP Host posudzovať samostatne.

## 9. ALPN

Application-Layer Protocol Negotiation umožní počas TLS handshake dohodnúť aplikačný protokol, napríklad:

- `http/1.1`,
- `h2` pre HTTP/2.

HTTP/3 používa QUIC a vlastné ALPN identifiers.

Ak ALPN negotiation zlyhá alebo proxy protokol nepodporuje, klient môže použiť fallback alebo connection ukončiť.

## 10. Cipher suites

Cipher suite určuje cryptographic primitives. V TLS 1.3 je oddelená od key exchange a authentication algoritmov viac než v starších verziách.

Policy má zakázať:

- zastarané protocol versions,
- slabé ciphers,
- nebezpečné hash/signature algorithms,
- export alebo anonymous suites.

Príliš agresívna policy však môže vyradiť legitímnych starších klientov. Rozhodnutie musí vychádzať z support matrix a threat modelu.

## 11. Forward secrecy

Ephemeral Diffie-Hellman key agreement poskytuje forward secrecy: neskorší únik dlhodobého server private key automaticky neumožní dešifrovať staré zachytené sessions.

## 12. Session resumption

TLS môže obnoviť predchádzajúcu session cez tickets alebo pre-shared keys.

Výhody:

- nižšia handshake latency,
- menší CPU overhead.

Riziká:

- ticket key lifecycle,
- zdieľanie keys medzi load-balanced endpoints,
- replay considerations pri TLS 1.3 0-RTT.

## 13. 0-RTT

TLS 1.3 môže umožniť klientovi poslať early data pred dokončením plného handshake.

Early data môže byť replayed. Preto sa nemá používať pre ne-idempotentné alebo citlivé operácie bez explicitného replay-safe designu.

## 14. Certificate issuance

Typický lifecycle:

```text
key generation
  ↓
CSR
  ↓
identity validation
  ↓
certificate issuance
  ↓
deployment
  ↓
monitoring
  ↓
renewal/rotation
  ↓
revocation alebo expiry
```

Private key má vzniknúť a zostať v kontrolovanej security boundary, ak architektúra nevyžaduje centralizovaný key management.

## 15. ACME

Automatic Certificate Management Environment automatizuje domain validation, issuance a renewal.

Automation musí riešiť:

- challenge type,
- DNS alebo HTTP ownership,
- rate limits,
- secure account keys,
- deployment nového certifikátu,
- reload služby,
- monitoring expiry.

Automatické vydanie bez automatického nasadenia a reloadu nie je kompletný lifecycle.

## 16. Wildcard certificates

Wildcard `*.example.com` pokrýva jednu úroveň subdomén, napríklad `api.example.com`, ale nie automaticky `a.b.example.com` ani apex `example.com`.

Výhody:

- menej certifikátov.

Riziká:

- väčší blast radius private key,
- širší scope identity,
- komplikovanejšie ownership boundaries.

## 17. mTLS

Mutual TLS autentifikuje aj klienta certifikátom.

```text
server certificate → klient overí server
client certificate → server overí klienta
```

Použitie:

- service-to-service identity,
- device identity,
- administratívne API,
- zero-trust segmenty.

mTLS nerieši automaticky business authorization. Certificate identity musí byť mapovaná na policy a lifecycle.

## 18. Trust stores

Rôzne runtime môžu používať rozdielne trust stores:

- operačný systém,
- Java truststore,
- browser store,
- application-bundled CA bundle,
- container image bundle.

Preto certifikát môže fungovať v browseri a zlyhať v Java aplikácii alebo kontajneri.

## 19. Revocation

Mechanizmy:

- CRL — Certificate Revocation List,
- OCSP — online status query,
- OCSP stapling — server priloží podpísaný status.

Revocation kontrola má availability a privacy trade-offy. Klient behavior sa líši; nie všetci klienti pri nedostupnom responderi fail-closed.

Krátko žijúce certificates znižujú závislosť od revocation, ale vyžadujú spoľahlivú automatizáciu.

## 20. Certificate expiry a rotation

Najčastejšie TLS incidenty vznikajú z lifecycle zlyhania, nie z cryptographic útoku.

Monitoruj:

- dni do expiry,
- chain completeness,
- hostname coverage,
- deployed serial/fingerprint,
- issuer a algorithm policy,
- renewal job success,
- reload a rollout stav.

Rotation musí podporovať overlap, aby klienti a servery nemuseli prejsť na nový trust anchor v jednej sekunde.

## 21. HSTS

HTTP Strict Transport Security:

```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

Browser si zapamätá, že doména sa má používať iba cez HTTPS.

Riziká:

- chybná konfigurácia môže zneprístupniť subdomény,
- `includeSubDomains` rozširuje scope,
- preload je dlhodobý záväzok.

HSTS sa prijíma iba cez dôveryhodné HTTPS spojenie.

## 22. TLS termination a passthrough

### Termination

Proxy dešifruje traffic a môže vykonávať L7 routing, WAF, authentication alebo observability.

### Re-encryption

Proxy vytvorí nové TLS spojenie k upstreamu.

### Passthrough

Proxy neukončuje TLS a routuje podľa L4 alebo SNI metadata.

Každý model má iné vlastníctvo certifikátov, client identity a observability.

## 23. Certificate pinning

Klient môže obmedziť dôveru na konkrétny key alebo certificate chain.

Pinning znižuje dôveru v široký CA ekosystém, ale výrazne komplikuje rotation a recovery. Bez bezpečného backup pin a update mechanizmu môže spôsobiť dlhý outage.

## 24. Diagnostika

```bash
curl -v https://api.example.com/
openssl s_client -connect api.example.com:443 -servername api.example.com -showcerts
openssl x509 -in cert.pem -noout -text
```

Kontroluj:

1. DNS destination,
2. TCP alebo QUIC reachability,
3. SNI,
4. protocol version a cipher,
5. presented certificate chain,
6. SAN hostname,
7. validity interval,
8. trust store,
9. revocation/policy,
10. ALPN a aplikačný protokol.

## 25. Typické symptómy

### `certificate has expired`

Leaf alebo intermediate certificate je po `notAfter`, prípadne klient má nesprávny čas.

### `unable to get local issuer certificate`

Chýbajúci intermediate alebo klient nedôveruje issueru.

### Hostname mismatch

Použitý hostname nie je v SAN alebo server vrátil default certificate pre nesprávne SNI.

### Funguje v browseri, nie v aplikácii

Rozdielny trust store, proxy, TLS version, SNI alebo certificate chain recovery behavior.

### Po rotation časť klientov zlyháva

Neúplný chain, starý trust store, chýbajúci overlap alebo pinning.

## 26. Časté omyly

### „HTTPS znamená, že server je dôveryhodný“

TLS overuje kontrolu identity podľa PKI, nie obchodnú alebo obsahovú dôveryhodnosť služby.

### „Certificate šifruje dáta“

Certificate nesie public key a identity claims; session data šifrujú odvodené symmetric keys.

### „Keď certifikát nie je expired, je validný“

Musí sedieť hostname, chain, usage, trust a policy.

### „Root CA posiela server klientovi“

Server typicky posiela leaf a intermediates. Root má byť v trust store klienta.

### „mTLS vyrieši authorization“

Poskytne client identity, ale policy musí rozhodnúť, čo identity smie robiť.

## 27. Kontrolné otázky

1. Čo poskytuje TLS a čo neposkytuje?
2. Ako sa líšia asymmetric a symmetric cryptography v handshake a data phase?
3. Čo klient overuje v certificate chain-e?
4. Načo slúžia SNI a ALPN?
5. Čo znamená forward secrecy?
6. Aké riziko prináša TLS 1.3 0-RTT?
7. Prečo server neposiela root CA ako dôkaz dôvery?
8. Aký je rozdiel medzi termination, re-encryption a passthrough?
9. Prečo môže aplikácia zlyhať, aj keď browser certifikátu dôveruje?
10. Ako navrhneš certificate rotation bez outage?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: HTTP](http.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: REST APIs a WebSockets →](rest-apis-and-websockets.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
