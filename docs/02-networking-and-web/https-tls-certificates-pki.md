# HTTPS, TLS, certifikáty a PKI

<!-- CONCEPT-FIRST:START -->
## Čo sú TLS, certifikát a PKI

TLS vytvára šifrovaný a integrity-protected channel medzi dvoma endpoints a typicky overuje identity servera. HTTPS je HTTP prenášané cez TLS. Šifrovanie platí iba medzi konkrétnymi TLS endpoints; reverse proxy môže channel ukončiť a vytvoriť ďalší upstream channel.

Handshake dohodne protocol version, cryptographic parametre a session keys. ClientHello môže obsahovať SNI pre výber virtual hostu a ALPN pre dohodu aplikačného protokolu, napríklad HTTP/2.

Server posiela certificate chain. Client overuje podpisy, trust anchor, časovú platnosť, key usage, constraints a hostname v Subject Alternative Name. Certifikát podpísaný dôveryhodnou CA nie je platný pre ľubovoľný hostname.

Typický chain:

```text
server leaf certificate
→ intermediate CA
→ root CA v client trust store
```

Server zvyčajne neposiela root. Chýbajúci intermediate môže fungovať na clientovi s cached chainom a zlyhať na čistom zariadení.

PKI je celý lifecycle identity: issuance, key generation a protection, deployment, trust distribution, renewal, revocation a retirement. Úspešné vydanie certifikátu nepreukazuje, že listener načítal nový file. Runtime handshake je samostatný read-back.

Private key dokazuje possession identity a musí zostať v kontrolovanom termination boundary. Forward secrecy používa ephemeral key agreement, aby neskorší únik dlhodobého key automaticky neodhalil staré sessions.

Pri mTLS posiela certificate aj client. Authentication certifikátom ešte nie je authorization; certificate identity sa musí mapovať na konkrétne permissions a audience.

Neutrálny príklad: client sa pripája na `api.example.test`, ale server pošle certificate iba pre `other.example.test`. TCP a cryptography môžu fungovať, no hostname validation musí handshake odmietnuť.

TLS troubleshooting preto oddeľuje transport connect, certificate chain, hostname, trust store, protocol negotiation a následný HTTP outcome.
<!-- CONCEPT-FIRST:END -->

## Atlas scenár a praktické použitie

Atlas klient sa pripája na `https://api.atlas.example`. TCP handshake potvrdil transport, ale klient ešte nevie, kto je na druhej strane. TLS vytvorí cryptographic channel, dohodne parametre a overí peer identity podľa certificate chainu a hostname policy.

HTTPS je HTTP prenášané cez TLS. Šifrovanie chráni obsah medzi TLS endpoints, nie automaticky za reverse proxy, v logoch alebo v backend storage.

## ClientHello a server identity

ClientHello obsahuje podporované protocol versions, cipher suites, key-share údaje a extensions. SNI oznamuje hostname potrebný pre výber certifikátu a virtual hostu. ALPN umožní dohodnúť napríklad `h2` alebo `http/1.1`.

Server odpovie zvolenými parametrami a certificate chainom. Client následne overuje:

```text
podpisy v chain-e
→ dôveryhodný trust anchor
→ časovú platnosť
→ key usage a constraints
→ hostname v Subject Alternative Name
→ prípadnú revocation policy
```

Platný podpis nestačí. Certifikát pre `other.example` nie je platnou identitou `api.atlas.example`, aj keby ho vydala dôveryhodná CA.

```bash
openssl s_client \
  -connect 203.0.113.40:443 \
  -servername api.atlas.example \
  -showcerts </dev/null
```

Tento command ukáže serverom poslaný chain a handshake details. Defaultné `s_client` použitie sa nesmie automaticky interpretovať ako rovnaká hostname validation, akú robí browser alebo `curl`.

```bash
curl --verbose https://api.atlas.example/
```

`curl` s dôveryhodným CA store typicky overí hostname aj chain a ukáže negotiated protocol.

## Certificate chain

Server certificate býva podpísaný intermediate CA a tá root CA. Server zvyčajne posiela leaf a potrebné intermediates; root býva už v client trust store.

Chýbajúci intermediate môže fungovať na clientovi, ktorý ho má cached, a zlyhať na čistom systéme. Monitoring z jedného dlhodobo používaného hosta preto nemusí odhaliť neúplný chain.

Cross-signing a viac možných chains komplikujú rozdiely medzi platformami. Acceptance musí používať podporované client trust stores, nie iba serverový scanner.

## Session keys a forward secrecy

Moderný TLS používa asymmetric mechanizmy na authentication a key agreement a následne symmetric session keys pre efektívny prenos. Ephemeral key exchange poskytuje forward secrecy: kompromitácia dlhodobého private key neskôr nemá automaticky dešifrovať staré zachytené sessions.

Private key musí zostať v kontrolovanom signer alebo termination boundary. Jeho únik vyžaduje revocation, replacement, investigation a podľa identity modelu aj posúdenie historických rizík.

## TLS termination a re-encryption

Atlas edge terminates client TLS. Upstream môže byť plaintext na izolovanej sieti alebo druhé TLS spojenie:

```text
client TLS identity: api.atlas.example
edge → backend identity: orders-api.production.atlas.internal
```

Pri re-encryption musí edge overovať backend hostname alebo SPIFFE-like identity a trust bundle. `verify none` síce šifruje traffic, ale neposkytuje peer authentication a umožňuje man-in-the-middle v upstream sieti.

Client TLS session neprechádza proxy. Ak backend potrebuje authenticated client identity, používa mTLS passthrough alebo dôveryhodný identity assertion s jasným signing a audience contractom.

## Mutual TLS

Pri mTLS posiela certifikát aj client. Server overuje client chain a mapuje certificate identity na workload alebo user policy. Certificate possession neznamená automatické authorization; SAN alebo subject sa musí viazať na konkrétne permissions a environment.

Rotation musí zvládnuť prechod, keď sú dôveryhodné staré aj nové CA alebo certificates. Príliš skoré odstránenie starého trust anchoru odpojí ešte neobnovené workloads; príliš dlhý overlap zväčší trust surface.

## Certificate lifecycle

Certificate má ownera, issuer, key, names, validity, deployment targets a renewal mechanism. Renewal success v CA nepreukazuje, že proxy načítala nový certificate.

```text
renewal issued
→ secret alebo file aktualizovaný
→ proxy reload/restart
→ active listener používa nový leaf
→ clients overia nový chain
→ starý key a cert sú retired
```

Runtime read-back cez handshake je nevyhnutný. File timestamp na disku nestačí.

## Revocation

CRL a OCSP umožňujú signalizovať zrušenie certifikátu, ale client behavior, privacy, availability a stapling policy sa líšia. Krátko platné certifikáty znižujú reliance na revocation, no zvyšujú význam automatického renewal.

Pri kompromitácii nemožno predpokladať okamžitú globálnu revocation enforcement. Potrebný je defense-in-depth: key protection, krátka validity, rapid rotation, access logs a obmedzené authorization.

## Incident: certifikát je „platný“, ale časť clients zlyháva

Edge nasadí nový leaf a pošle iba leaf certificate bez intermediate. Browser na administrátorovom notebooku funguje vďaka cached intermediate; čisté mobile clients hlásia unknown issuer.

Server scanner z management siete je zelený, pretože používa odlišný chain builder. `openssl s_client -showcerts` z čistého containeru ukáže iba leaf. Oprava nasadí full chain, runtime listener sa reloadne a tests prejdú z viacerých trust stores. Renewal pipeline pridá chain-completeness a cold-client test.

## Zhrnutie

TLS chráni channel medzi konkrétnymi endpoints a overuje identity podľa chainu, trust store-u a hostname policy. Certificate issuance, file deployment a active listener sú tri rozdielne states. HTTPS je overené až po handshake z reprezentatívneho clienta a následnom HTTP/business teste.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: HTTP](http.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: REST API a WebSockety →](rest-apis-and-websockets.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
