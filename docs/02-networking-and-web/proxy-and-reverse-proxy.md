# Proxy a reverse proxy

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [DNS](dns.md), [Ports a sockets](ports-and-sockets.md), [Firewally](firewalls.md)
- Súvisiace témy: load balancing, HTTP, TLS termination, caching, service discovery, service mesh, WAF

## 1. Problém, ktorý proxy rieši

Atlas nechce, aby internetový klient poznal adresu každého Orders backendu. Chce jeden stabilný endpoint, jednotnú TLS policy, centralizované request logy a miesto, kde možno aplikovať routing, limity a bezpečnostné kontroly.

Klient preto nekomunikuje priamo s Orders procesom. Komunikuje s reverse proxy:

```text
client
→ atlas.example.com:443
→ reverse proxy
→ orders-service:8080
```

Proxy nie je iba router ani NAT. Prijme downstream communication, ukončí ju vo vlastnom socket/protocol state a vytvorí samostatnú upstream communication.

```text
Client -- downstream connection --> Proxy -- upstream connection --> Backend
```

Downstream a upstream majú nezávislé:

- endpointy a source identity,
- TCP alebo QUIC state,
- TLS session,
- timeouty,
- buffery a queues,
- protocol verziu,
- retry lifecycle,
- observability a failure reason.

Toto rozdelenie na dva flows je dominantný model celej kapitoly.

## 2. Proxy verzus router, NAT a load balancing

```text
router
→ prepošle IP packet podľa route

NAT
→ prepíše endpoint fields v jednom transportnom path-e

proxy
→ ukončí jeden flow a vytvorí druhý

load balancing
→ vyberie backend pre flow alebo request
```

Proxy môže zároveň load-balancovať, ale tieto pojmy nie sú totožné. Proxy opisuje connection boundary. Load balancing opisuje selection decision.

Pre Atlas to znamená:

```text
DNAT doručí packet na proxy listener
→ firewall ho povolí
→ proxy prijme downstream connection
→ proxy vyberie Orders backend
→ proxy vytvorí upstream connection
```

Každá šípka má iný state owner a inú failure boundary.

## 3. Carried scenario: jeden Orders request

Klient odošle:

```http
POST /orders HTTP/1.1
Host: atlas.example.com
Idempotency-Key: order-7f31
Content-Type: application/json
```

Request prejde proxy lifecycle-om:

```text
1. DNS vyberie proxy endpoint
2. klient otvorí downstream TCP connection
3. klient a proxy vykonajú TLS handshake
4. proxy načíta a validuje HTTP headers
5. proxy vyhodnotí host/path route
6. proxy získa eligible upstream endpoint
7. proxy vezme pooled connection alebo otvorí novú
8. proxy prípadne vykoná upstream TLS
9. proxy odošle request
10. backend spracuje objednávku
11. proxy prijme response
12. proxy ju pošle klientovi
13. obe connections sa zachovajú, drainujú alebo zatvoria
```

Celková latency je súčet čakania v týchto fázach. Status `504` alebo „proxy timeout“ sám neurčuje, v ktorej fáze sa čas minul.

## 4. Forward proxy a reverse proxy

### Forward proxy

Forward proxy zastupuje klienta voči externému originu:

```text
Orders workload
→ corporate egress proxy
→ payment API
```

Klient proxy pozná explicitne alebo je traffic transparentne presmerovaný. Forward proxy môže vynucovať egress policy, auditovať destination a pri HTTP CONNECT vytvoriť tunnel.

```http
CONNECT payments.example:443 HTTP/1.1
Host: payments.example:443
```

Pri bežnom CONNECT proxy prenáša TLS bytes a nevidí plaintext HTTP. Pri TLS inspection vytvorí dve TLS sessions a stane sa interným MITM endpointom, ktorému musí klient dôverovať.

### Reverse proxy

Reverse proxy zastupuje serverovú službu:

```text
internet client
→ Atlas edge proxy
→ Orders backend
```

Klient nemusí poznať backend topology. Proxy vlastní frontend endpoint a podľa requestu vytvára upstream flow.

Rozdiel nie je iba smer šípky. Forward proxy dôveruje klientom a riadi ich egress; reverse proxy chráni serverovú službu a riadi ingress.

## 5. TLS boundary určuje vlastníctvo identity

Atlas môže použiť tri základné modely.

### Termination a plaintext upstream

```text
Client --TLS--> Proxy --HTTP--> Backend
```

Proxy vlastní edge certificate a plaintext je viditeľný v internom segmente.

### Termination a re-encryption

```text
Client --TLS A--> Proxy --TLS B--> Backend
```

Proxy musí samostatne validovať upstream certificate, SNI a trust chain.

### Passthrough

```text
Client --TLS------------------> Backend
             proxy forwards flow
```

Proxy nevidí HTTP plaintext. Môže rozhodovať podľa IP/portu alebo ClientHello metadata, ale nie podľa HTTP pathu.

TLS termination určuje, kto vlastní:

- private key a certificate lifecycle,
- SNI a ALPN negotiation,
- client-certificate validation,
- handshake logs,
- TLS session resumption,
- policy pre upstream trust.

Ak downstream TLS funguje, upstream TLS môže stále zlyhať a proxy vrátiť vlastný `502`.

## 6. Client identity sa musí preniesť cez dôveryhodný chain

Backend pri bežnom proxy modeli vidí source IP proxy, nie klienta. Atlas môže preniesť metadata:

```http
Forwarded: for=198.51.100.25;proto=https;host=atlas.example.com
X-Forwarded-For: 198.51.100.25
X-Forwarded-Proto: https
```

Tieto headers môže odoslať aj nedôveryhodný klient. Bezpečný model:

```text
client
→ edge proxy odstráni inbound forwarding headers
→ proxy zapíše vlastné overené hodnoty
→ backend prijíma traffic iba z trusted proxy pathu
→ aplikácia dôveruje iba definovanému počtu alebo rozsahu proxy hops
```

Pri chain-e:

```text
client → CDN → edge proxy → ingress proxy → application
```

musí byť určené, ktorá vrstva je autoritatívna pre original client identity.

L4 proxy môže použiť PROXY protocol. Obe strany musia mať rovnaké očakávanie. Backend bez PROXY supportu bude prefix interpretovať ako aplikačné dáta; backend očakávajúci PROXY protocol odmietne priameho klienta bez headera.

## 7. Route selection a normalizácia sú súčasť correctness

Atlas routuje:

```text
Host atlas.example.com + /orders/* → orders pool
Host atlas.example.com + /users/*  → users pool
```

Proxy však môže pred routingom meniť request representation:

- percent-decoding,
- `.` a `..` normalizáciu,
- viacnásobné slash-e,
- trailing slash,
- case,
- odstránenie prefixu,
- prepis Host alebo authority.

Ak proxy a backend používajú rozdielnu canonical form, môže vzniknúť route confusion alebo authorization bypass.

```text
proxy autorizuje jednu reprezentáciu
→ backend interpretuje inú reprezentáciu
→ request dosiahne neočakávaný handler
```

Routing, caching a authorization musia používať konzistentnú normalizáciu. Nejednoznačný framing alebo Host treba odmietnuť, nie „opraviť“ rozdielne na každej vrstve.

## 8. Buffery neodstraňujú backpressure

Proxy môže bufferovať request body pred odoslaním upstreamu.

Výhody:

- chráni backend pred pomalým klientom,
- overí body limit skôr,
- umožní niektoré bezpečné retries,
- môže skenovať alebo uložiť upload.

Nevýhody:

- rast memory alebo disk pressure,
- vyššia latency pred upstream startom,
- veľký upload spotrebuje proxy capacity,
- streaming semantics sa stratia.

Pri response bufferi:

```text
fast backend
→ proxy buffer rastie
→ slow client
```

Keď buffer nestačí, tlak sa prenesie späť cez TCP flow control alebo na disk. Backpressure sa nedá odstrániť; možno ju iba umiestniť a ohraničiť.

Streaming, WebSockets a SSE preto potrebujú osobitnú policy pre buffering, idle timeout, heartbeat a draining.

## 9. Timeout budget musí mať vlastníka

Proxy nepoužíva jeden timeout. Má najmenej:

```text
downstream accept/TLS/header/body/write timeouts
+ upstream discovery/connect/TLS/header/body timeouts
+ pool queue/idle/max-age/drain timeouts
```

Atlas nastaví budget:

```text
client total timeout:       10 s
edge proxy total:            9 s
ingress proxy total:         8 s
Orders application:          7 s
payment dependency:          5 s
```

Vnútorná vrstva tak môže vrátiť kontrolovanú chybu predtým, než nadradená connection náhle zanikne.

Chybný model:

```text
client 5 s
proxy 30 s
backend 60 s
```

spôsobí, že proxy a backend pokračujú v práci po odchode klienta. Klient následne retryuje a vytvára duplicate alebo wasted work.

## 10. Retry je business rozhodnutie, nie iba network mechanizmus

Nebezpečný scenár:

```text
proxy odošle POST /orders
→ backend objednávku vytvorí
→ response sa stratí pred proxy
→ proxy nevie, či side effect prebehol
→ proxy retryuje na inom backende
→ druhá objednávka
```

Transportný reset neposkytuje exactly-once informáciu. Bezpečný retry potrebuje:

- idempotentnú operáciu alebo idempotency key,
- znalosť fázy odoslania,
- bounded attempts,
- per-try timeout,
- backoff a jitter,
- retry budget,
- zákaz retry po čiastočnej response,
- explicitného vlastníka retry policy.

Ak klient, edge proxy, ingress a application library vykonajú po tri pokusy:

```text
3 × 3 × 3 = až 27 backend attempts
```

Retry amplification môže počas incidentu zničiť zostávajúcu capacity.

## 11. Upstream connection pooling mení failure aj load model

Proxy znovu používa upstream connections, čím znižuje TCP/TLS handshake overhead a ephemeral-port pressure.

Pool však vytvára state:

- stale connection po backend restart-e,
- stará IP po DNS zmene,
- veľa idle sockets,
- per-backend connection skew,
- HTTP/2 multiplexing mnohých requests na jednom flowe.

`dig` ukazujúci novú IP neznamená, že proxy zatvorila staré pooled connections. Pool policy musí mať max connections, idle timeout, maximum age a drain behavior.

## 12. Discovery, health a draining tvoria jeden endpoint lifecycle

```text
backend vznikne
→ discovery ho oznámi proxy
→ readiness/health ho označí eligible
→ proxy naň posiela traffic
→ backend sa označí draining
→ nové requests sa zastavia
→ existujúca práca skončí alebo timeoutuje
→ endpoint sa odstráni
```

TCP health check dokazuje iba listener. Orders readiness má odpovedať na otázku: „Môže tento backend prijať nový request?“

Príliš plytký check pustí broken backend. Príliš deep check závislý od shared database môže pri databázovom incidente vyradiť celý pool a odstrániť možnosť degradovanej odpovede.

Draining musí koordinovať proxy timeout, application shutdown grace a dlhé WebSocket alebo gRPC sessions.

## 13. Worked failure: upstream funguje priamo, ale nie cez proxy

Administrátor z laptopu úspešne volá:

```text
http://10.20.3.21:8080/orders
```

Klient cez `https://atlas.example.com/orders` dostáva `502`.

„Backend funguje priamo“ ešte neoverilo path z proxy namespace ani rovnaký request contract.

Postup:

1. Over client → proxy DNS, TCP a TLS.
2. Nájdite request v proxy access logu podľa request ID.
3. Zistite matched route a selected upstream.
4. Otestujte upstream z proxy network namespace.
5. Porovnajte Host, path rewrite a headers s direct testom.
6. Overte upstream TLS/SNI, ak sa používa re-encryption.
7. Overte protocol verziu a PROXY protocol expectation.
8. Určte, či `502` vytvorila proxy alebo backend.

Možný dôkaz:

```text
client TLS succeeds
+ proxy route matches orders
+ proxy connects to 10.20.3.21:8443
+ backend počúva plaintext na 8080
→ upstream protocol/port mismatch
```

Oprava je zmeniť konkrétny upstream endpoint contract, nie predĺžiť všetky timeouty.

## 14. Worked failure: klient dostáva 504, backend nevidí request

Atlas vidí:

```text
client request reaches proxy
→ 8 s čakanie
→ proxy vráti 504
→ Orders access log nemá request
```

Request mohol zlyhať pred odoslaním upstream headers:

- discovery timeout,
- queue wait,
- connection-pool saturation,
- TCP connect timeout,
- upstream TLS timeout.

Potrebné fázy:

```text
request accepted time
downstream TLS time
route decision
queue wait
upstream DNS/discovery
connect time
upstream TLS time
request sent timestamp
response-header time
```

Ak queue wait trvá 7,8 sekundy a upstream connect sa ani nezačne, backend log správne nič neobsahuje. Zvýšenie upstream response timeoutu by bolo irelevantné.

## 15. Status attribution

Proxy-generated status je diagnostická klasifikácia, nie univerzálna root cause.

- `502` — proxy nezískala platnú upstream response; napríklad reset, protocol mismatch alebo upstream TLS failure.
- `503` — proxy nemá eligible backend alebo zámerne odmieta traffic pre maintenance, circuit breaker či capacity limit.
- `504` — definovaná upstream fáza neukončila progres v budgete.

Implementácie sa líšia. Log musí rozlíšiť downstream status, upstream status a proxy failure reason.

## 16. Observability musí oddeliť obe strany proxy

### Downstream

- accepted connections,
- TLS handshake výsledok,
- request read time,
- client disconnect,
- bytes a total latency.

### Routing a queue

- route identity,
- selected cluster,
- queue wait,
- retry count,
- cache decision.

### Upstream

- endpoint identity,
- discovery time,
- connect a TLS time,
- time to response headers,
- reset reason,
- upstream status.

### End-to-end

- request/trace ID,
- proxy-generated alebo upstream-generated response,
- total attempts,
- total bytes a outcome.

Bez oddelenia downstream a upstream metrík vyzerá proxy ako jedna čierna skrinka.

## 17. Referenčné rozšírenia

Nasledujúce funkcie nemenia základný model dvoch samostatných connections.

### L4 a L7 proxy

L4 proxy rozhoduje primárne podľa transportného flowu a podporuje ne-HTTP protokoly. L7 proxy interpretuje request a môže routovať podľa Host, path, method alebo identity.

### Caching

Cache key musí zahrnúť všetky fields, ktoré menia representation a authorization context. Chybný key môže doručiť personalizovaný response inému používateľovi.

### Compression

Znižuje bandwidth, ale zvyšuje CPU, mení cache variants a môže vyžadovať buffering.

### Protocol translation

HTTP/3 downstream a HTTP/1.1 upstream majú odlišné multiplexing, cancellation a backpressure semantics. Translation nie je bezvýznamný format conversion.

### Request smuggling

Vzniká, keď proxy a backend rozdielne interpretujú request framing. Nejednoznačné `Content-Length`, `Transfer-Encoding` alebo duplicitné headers sa majú odmietnuť.

### Forward-proxy TLS inspection

Proxy drží citlivú CA authority, vidí plaintext a musí bezpečne validovať origin. mTLS, pinning alebo custom trust store môžu inspection zablokovať.

## 18. Časté omyly

### „Reverse proxy je DNS alias“

DNS iba vyberie endpoint. Proxy prijme downstream flow a vytvorí upstream flow.

### „L4 proxy zachová jednu end-to-end TCP connection“

Full L4 proxy typicky vlastní dve transportné connections, aj keď nečíta HTTP.

### „X-Forwarded-For je automaticky client IP“

Je dôveryhodný iba cez kontrolovaný proxy chain, ktorý odstraňuje klientom dodané hodnoty.

### „502 znamená chybu aplikačnej logiky“

Môže vzniknúť pred platnou HTTP response pri connect, TLS alebo framing failure.

### „Proxy retry je vždy bezpečný“

Po ambiguous failure môže zopakovať side effect.

### „Buffering odstráni backpressure“

Iba presunie tlak do proxy memory, disku alebo queue.

### „DNS TTL určuje okamžitý prechod proxy na nový backend“

Proxy môže používať vlastnú cache a staré pooled connections.

## 19. Kontrolné otázky

1. Prečo proxy vytvára downstream a upstream connection?
2. Aký je rozdiel medzi routerom, NATom, proxy a load balancingom?
3. Ako sa líši forward a reverse proxy trust model?
4. Čo robí HTTP CONNECT?
5. Ako TLS termination mení ownership identity a certifikátov?
6. Kedy sú forwarding headers dôveryhodné?
7. Aký failure spôsobí PROXY protocol mismatch?
8. Prečo path normalization patrí do security modelu?
9. Kam sa presunie backpressure pri response bufferingu?
10. Ako zostaviť timeout budget cez viac proxy vrstiev?
11. Prečo môže retry duplicitne vykonať POST?
12. Ako vzniká retry amplification?
13. Ako pooling ovplyvní DNS change a load distribution?
14. Čo znamená endpoint lifecycle od discovery po draining?
15. Prečo direct backend test nemusí reprodukovať proxy path?
16. Ako rozlíšiš queue timeout od upstream response timeoutu?
17. Čo typicky odlišuje `502`, `503` a `504`?
18. Ktoré downstream a upstream metriky treba sledovať samostatne?

## 20. Zhrnutie

Proxy je aktívna connection boundary. Ukončí downstream communication, interpretuje alebo prenesie jej protokol, vyberie upstream a vytvorí samostatný flow. Preto má dve identity, dve TLS sessions, dve sady timeoutov, buffery a failure modes.

Troubleshooting sleduje jeden request po jednotlivých fázach od downstream acceptu cez route a queue až po upstream connect, TLS a response. Status alebo celková latency bez tejto dekompozície nestačia. Bezpečný návrh navyše koordinuje trusted client identity, canonical request representation, retry semantics, pooling, health a draining ako jeden lifecycle.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Firewally](firewalls.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Load balancing →](load-balancing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
