# Proxy a reverse proxy

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [DNS](dns.md), [Ports a sockets](ports-and-sockets.md), [Firewally](firewalls.md)
- Súvisiace témy: load balancing, HTTP, TLS termination, caching, service discovery, service mesh, WAF

## 1. Definícia

Proxy je sprostredkovateľ, ktorý prijme komunikáciu od jednej strany a vytvorí samostatnú komunikáciu k druhej strane.

- Forward proxy zastupuje klienta voči externým serverom.
- Reverse proxy zastupuje serverovú službu voči klientom.

Proxy nie je iba router alebo NAT. Typicky ukončí transportné alebo aplikačné spojenie, prijme dáta do vlastných bufferov, aplikuje policy a vytvorí nový upstream flow.

```text
Client
    ↓ downstream connection
Proxy
    ↓ upstream connection
Server
```

Downstream a upstream connection majú samostatné:

- source a destination endpointy,
- TCP alebo QUIC state,
- TLS session,
- timeouty,
- buffery,
- protocol verziu,
- retry lifecycle,
- observability,
- failure mode.

To je základný mentálny model celej kapitoly.

## 2. Proxy verzus router, NAT a load balancer

### Router

Router forwarduje IP packets podľa routing table. Bežne nevytvára nové aplikačné spojenie.

### NAT

NAT prepíše address alebo port fields a udržiava translation state. Endpointy stále komunikujú v rámci jedného transportného flowu, hoci middlebox mení tuple.

### Proxy

Proxy ukončí jeden flow a vytvorí druhý. Môže čítať a meniť aplikačný protokol.

### Load balancer

Load balancing je funkcia rozdelenia trafficu medzi backends. Môže byť implementovaná proxy modelom, NAT modelom, direct routingom, DNS alebo client-side výberom.

```text
proxy
= connection termination a sprostredkovanie

load balancing
= backend selection
```

Jedno zariadenie môže vykonávať obe funkcie.

## 3. Forward proxy

Forward proxy je explicitný alebo transparentný egress bod pre klientov.

Použitie:

- riadený outbound access,
- egress filtering,
- audit a attribution,
- malware alebo content filtering,
- caching,
- anonymizácia source adresy voči originu,
- prístup z izolovanej siete,
- vynútenie corporate identity alebo DLP policy.

Explicitná konfigurácia môže používať environment:

```text
HTTP_PROXY=http://proxy.example:3128
HTTPS_PROXY=http://proxy.example:3128
NO_PROXY=localhost,127.0.0.1,.internal.example,10.0.0.0/8
```

Nie každá aplikácia interpretuje tieto premenné rovnako. Rozdiely môžu zahŕňať:

- case sensitivity názvu premennej,
- CIDR podporu v `NO_PROXY`,
- matching subdomén,
- IPv6 literal syntax,
- port-specific entries,
- DNS resolution pred alebo po proxy výbere.

Efektívnu proxy konfiguráciu treba overiť v konkrétnom runtime, nie iba v shell environment-e.

## 4. Transparentný forward proxy

Transparentný proxy path presmeruje traffic bez explicitného client nastavenia.

```text
client believes it connects to origin
    ↓ network redirect/interception
proxy
    ↓ origin
```

Riziká:

- aplikácia nemusí očakávať sprostredkovateľa,
- TLS nemožno transparentne interpretovať bez interception modelu,
- original destination treba zachovať v dataplane metadata,
- asymmetric routing môže obísť proxy,
- proxy failure môže zablokovať celý egress,
- troubleshooting je ťažší, pretože client config proxy neukazuje.

Transparentný režim musí mať explicitný fail-open alebo fail-closed model.

## 5. HTTP CONNECT

Pri HTTPS cez explicitný forward proxy klient typicky požiada o tunel:

```http
CONNECT api.example.com:443 HTTP/1.1
Host: api.example.com:443
```

Proxy:

1. autentizuje alebo autorizuje klienta,
2. vyhodnotí destination policy,
3. vyrieši meno alebo použije klientom určený target podľa implementácie,
4. vytvorí TCP connection k originu,
5. vráti úspech klientovi,
6. prenáša bytes oboma smermi.

Pri bežnom CONNECT tuneli proxy nevidí plaintext HTTP vo vnútri TLS. Vidí však:

- destination hostname a port z CONNECT requestu,
- client identity,
- čas a objem spojenia,
- TLS metadata, ak ich pasívne pozoruje,
- network failure a timeouty.

## 6. TLS inspection cez forward proxy

Pri TLS inspection proxy nevytvorí iba tunnel. Vystupuje ako dva TLS endpointy:

```text
Client --TLS A--> Inspection proxy --TLS B--> Origin
```

Proxy dynamicky vydá certifikát pre origin hostname pomocou internej CA. Klient musí tejto CA dôverovať.

Security dôsledky:

- proxy vidí plaintext,
- proxy drží alebo používa vysoko citlivý signing key,
- compromise proxy alebo CA má veľký blast radius,
- certificate pinning môže zlyhať,
- privacy a compliance scope sa rozšíri,
- aplikácie s mTLS alebo custom trust store môžu byť nekompatibilné,
- proxy musí validovať origin certifikát rovnako prísne ako klient.

Inspection bez správnej origin validation iba presunie MITM riziko do vlastnej infraštruktúry.

## 7. Reverse proxy

Reverse proxy je frontend pred jednou alebo viacerými službami.

Typické funkcie:

- TLS termination,
- virtual hosting,
- host a path routing,
- load balancing,
- authentication alebo authorization integration,
- rate limiting,
- request/response transformácie,
- compression,
- caching,
- WAF policy,
- access logging,
- connection pooling,
- protocol translation,
- maintenance a draining.

Príklad:

```text
https://api.example.com/orders/123
    ↓ DNS
reverse proxy :443
    ↓ TLS termination
    ↓ Host/path route
orders-service:8080
```

Klient nemusí vedieť, ktorý konkrétny backend request spracoval.

## 8. L4 proxy

L4 proxy pracuje primárne s transportným flowom.

Môže rozhodovať podľa:

- destination IP a portu,
- source IP,
- TCP alebo UDP tuple,
- connection state,
- TLS ClientHello metadata ako SNI alebo ALPN bez úplnej TLS terminácie,
- platformovej identity alebo marku.

Výhody:

- podporuje ne-HTTP protokoly,
- menší aplikačný parsing overhead,
- môže zachovať end-to-end TLS,
- menšia závislosť od konkrétnej aplikačnej syntaxe.

Limity:

- nevie routovať podľa HTTP path alebo method bez L7 parsing-u,
- health check nemusí overiť aplikačnú operáciu,
- source identity sa môže stratiť,
- connection-level výber môže viazať veľa requestov na jeden backend.

## 9. L7 proxy

L7 proxy interpretuje aplikačný protokol.

Pri HTTP môže používať:

- scheme,
- Host alebo `:authority`,
- path,
- method,
- headers,
- cookies,
- query parameters,
- response status,
- identity claims.

Výhody:

- jemný routing,
- aplikačné rate limits,
- retries podľa request semantics,
- caching,
- header transformations,
- WAF a authorization.

Náklady:

- protocol parsing a normalization,
- vyššie CPU/memory nároky,
- nové request-smuggling a parser-difference riziká,
- proxy sa stáva súčasťou aplikačného correctness modelu,
- nesprávny rewrite môže zmeniť business semantics.

## 10. Downstream a upstream lifecycle

Jeden klientský request prechádza viacerými fázami:

```text
1. accept downstream connection
2. optional downstream TLS handshake
3. parse request headers
4. optional request body read/buffering
5. route selection
6. upstream endpoint selection
7. obtain/create upstream connection
8. optional upstream TLS handshake
9. send request
10. receive upstream response
11. optional buffering/transformation
12. send response to client
13. keep alive, close alebo drain
```

Každá fáza môže zlyhať odlišne. Jeden celkový údaj „proxy latency“ nestačí na root cause analýzu.

## 11. TLS termination modely

### Edge termination a plaintext upstream

```text
Client --TLS--> Proxy --HTTP--> Upstream
```

Jednoduchší model, ale interný segment musí byť explicitne dôveryhodný a chránený.

### Edge termination a re-encryption

```text
Client --TLS--> Proxy --TLS--> Upstream
```

Proxy validuje upstream identity. Certifikát, trust store a SNI pre upstream sú samostatná konfigurácia.

### TLS passthrough

```text
Client --TLS------------------> Upstream
             proxy forwards flow
```

Proxy môže routovať podľa IP/portu alebo parsovaného ClientHello SNI, ale nevidí HTTP plaintext.

### mTLS

Proxy môže autentizovať client certificate a samostatne používať client certificate voči upstreamu. Tieto identity nemusia byť rovnaké a ich mapovanie musí byť explicitné.

## 12. TLS ownership

TLS termination určuje, kto vlastní:

- server private key,
- certificate lifecycle,
- SNI routing,
- cipher a protocol policy,
- ALPN negotiation,
- OCSP alebo stapling správanie,
- client certificate validation,
- handshake logs,
- TLS session resumption.

Ak TLS končí na proxy, backendový certificate problém nemusí byť viditeľný klientovi pri plaintext upstream modeli. Pri re-encryption môže backend TLS failure viesť k proxy-generated `502` alebo podobnej chybe.

## 13. Client identity a trusted proxy chain

Backend pri bežnom proxy spojení vidí source IP proxy.

HTTP metadata:

```http
Forwarded: for=198.51.100.25;proto=https;host=app.example
X-Forwarded-For: 198.51.100.25
X-Forwarded-Proto: https
X-Forwarded-Host: app.example
```

Tieto headers nie sú automaticky dôveryhodné. Klient ich môže poslať sám.

Bezpečný model:

1. Backend prijíma traffic iba od známych proxy endpointov.
2. Edge proxy odstráni nedôveryhodné forwarding headers.
3. Každý trusted proxy pridá alebo prepíše hodnotu podľa definovaného modelu.
4. Aplikácia pozná počet alebo rozsah trusted hops.
5. Authorization nepoužíva client IP ako jediný silný identity faktor.

Pri proxy chain-e:

```text
client → CDN → edge LB → ingress proxy → application
```

musí byť jasné, ktorá vrstva je autoritatívna pre pôvodnú client IP.

## 14. PROXY protocol

PROXY protocol prenesie original source/destination metadata pred aplikačnými dátami.

Používa sa najmä pri L4 proxy, kde backend inak vidí iba source IP proxy.

```text
PROXY TCP4 198.51.100.25 10.0.1.20 52000 443
```

Obe strany musia byť nakonfigurované konzistentne:

- proxy musí prefix odosielať,
- backend listener ho musí očakávať,
- plaintext klient nesmie mať možnosť priamo injektovať dôveryhodný PROXY header,
- health checks musia používať správny režim.

Mismatch typicky vedie k protocol error alebo k interpretácii PROXY riadku ako aplikačných dát.

## 15. Host routing

Reverse proxy môže vybrať backend podľa host identity:

```text
api.example.com    → API pool
admin.example.com  → admin pool
static.example.com → object storage
```

Pri HTTP/1.1 ide typicky o `Host`; pri HTTP/2 a HTTP/3 o `:authority`. Pri TLS môže pred HTTP existovať SNI routing.

Riziká:

- Host header injection,
- mismatch medzi SNI a HTTP authority,
- chýbajúci default virtual host,
- absolute-form URL parsing,
- upstream generovanie odkazov z nedôveryhodného hostu.

Proxy má validovať povolené hostnames a nepresúvať neoverený Host do security-sensitive logiky.

## 16. Path routing a normalization

Príklad:

```text
/api/billing/* → billing-service
/api/users/*   → users-service
```

Pred routingom môže proxy path:

- percent-decodovať,
- normalizovať `.` a `..`,
- zlučovať viac slashov,
- meniť case podľa protokolu alebo platformy,
- odstraňovať prefix,
- pridávať trailing slash.

Ak proxy a upstream normalizujú rozdielne, môže vzniknúť:

- authorization bypass,
- cache poisoning,
- route confusion,
- request smuggling medzi vrstvami,
- nesprávny redirect loop.

Routing a authorization majú používať konzistentnú canonical representation.

## 17. Header transformations

Proxy často upravuje headers:

- odstráni hop-by-hop headers,
- nastaví forwarding metadata,
- prepíše Host pre upstream,
- pridá request ID alebo trace context,
- upraví compression negotiation,
- odstráni interné response headers.

Hop-by-hop a end-to-end semantics sa líšia podľa HTTP verzie. Mechanické kopírovanie všetkých headers môže byť nesprávne.

Citlivé headers ako `Authorization`, cookies a tracing baggage musia mať explicitný propagation model.

## 18. Request buffering

Proxy môže najprv načítať celý request body a až potom ho poslať upstreamu.

Výhody:

- chráni upstream pred pomalým klientom,
- body-size policy sa vyhodnotí pred upstream requestom,
- retry môže byť možný, ak je body bezpečne uložené,
- proxy môže skenovať alebo transformovať obsah.

Nevýhody:

- vyššia latency pred začiatkom upstream spracovania,
- memory alebo disk pressure,
- veľké uploads blokujú proxy capacity,
- klient môže dokončiť upload, hoci upstream neskôr okamžite odmietne,
- streaming semantics sa stratia.

Request buffering limit musí byť koordinovaný s upload limitmi, temporary storage a timeoutmi.

## 19. Response buffering a backpressure

Proxy môže bufferovať upstream response pred odoslaním klientovi.

To izoluje upstream od slow clienta, ale presúva tlak do proxy.

```text
fast upstream
    ↓
proxy buffer grows
    ↓
slow client
```

Ak buffer nestačí:

- proxy môže zapisovať na disk,
- upstream sa môže zablokovať cez TCP flow control,
- request môže zlyhať,
- memory pressure môže ovplyvniť iné requests.

Backpressure sa nedá odstrániť; iba sa presúva medzi klienta, proxy, upstream a storage.

## 20. Streaming, WebSockets a SSE

Streaming workloads potrebujú odlišnú policy:

- vypnuté alebo obmedzené buffering,
- dlhšie idle timeouty,
- správny protocol upgrade,
- flow control,
- heartbeat,
- draining pri deploymente,
- connection limits.

WebSocket handshake môže uspieť, ale connection sa neskôr zatvorí na idle timeout-e proxy. Server-Sent Events môžu byť oneskorené, ak proxy response buffer neflushuje priebežne.

## 21. Timeout taxonomy

Proxy má viac nezávislých timeoutov.

### Downstream

- accept alebo handshake timeout,
- TLS handshake timeout,
- request header timeout,
- request body timeout,
- downstream idle timeout,
- response write timeout.

### Upstream

- DNS/service-discovery timeout,
- connect timeout,
- upstream TLS handshake timeout,
- request send timeout,
- response header timeout,
- response body idle timeout,
- total request timeout.

### Pool

- idle connection lifetime,
- maximum connection age,
- queue timeout,
- endpoint drain timeout.

Celkový timeout musí byť väčší než súčet relevantných per-stage budgetov a menší než timeout klienta alebo nadradenej proxy tak, aby chyba vznikla na kontrolovanej vrstve.

## 22. Timeout budget naprieč chainom

Príklad:

```text
client timeout:       10 s
edge proxy timeout:    9 s
ingress timeout:       8 s
application timeout:   7 s
database timeout:      5 s
```

Takýto model umožní vnútornej vrstve vrátiť kontrolovanú chybu skôr, než nadradená vrstva connection náhle ukončí.

Nesprávne poradie:

```text
client 5 s
proxy 30 s
backend 60 s
```

spôsobí, že backend a proxy pokračujú v práci po tom, čo klient už odišiel. To zvyšuje wasted work a retry amplification.

## 23. Retry semantics

Proxy môže retryovať pri:

- connect failure,
- reset pred odoslaním request body,
- reset pred response headers,
- timeout-e,
- vybraných HTTP statusoch,
- unhealthy endpoint selection.

Retry je bezpečný iba vtedy, keď proxy pozná stav odoslania a request semantics.

Nebezpečný scenár:

```text
POST payment
    ↓ upstream spracuje transakciu
    ↓ response sa stratí
proxy retry
    ↓ druhá transakcia
```

Dobrý model:

- retry iba idempotentné operácie alebo requesty s idempotency key,
- bounded attempts,
- per-try timeout,
- exponential backoff a jitter,
- retry budget,
- zákaz retry po čiastočnom response stream-e,
- rozlíšenie connect failure a ambiguous processing failure.

## 24. Retry amplification

Ak každý klient, proxy a service retryuje nezávisle, počet pokusov sa násobí.

```text
client 3 attempts
× edge proxy 3 attempts
× service 3 attempts
= až 27 backend pokusov
```

Počas dependency outage môže retry storm znemožniť recovery.

Retry ownership má byť explicitný. Vrstva s najlepším poznaním idempotency a failure state má rozhodovať o opakovaní.

## 25. Connection pooling

Proxy môže znovu používať upstream connections.

Výhody:

- menej TCP a TLS handshakes,
- nižšia latency,
- menší CPU overhead,
- stabilnejšia ephemeral-port a conntrack spotreba.

Riziká:

- stale connection po upstream restart-e,
- veľa idle sockets,
- nerovnomerné rozdelenie loadu,
- starý DNS target zostane v poole,
- per-backend connection cap,
- HTTP/2 multiplexing koncentruje veľa requests do jedného flowu.

Pool policy má definovať maximum connections, idle timeout, max age, health validation a draining.

## 26. Queueing a concurrency

Ak proxy nemá voľnú upstream connection alebo worker capacity, request môže čakať v queue.

Queue chráni backend pred okamžitým overloadom, ale zvyšuje latency.

```text
arrival rate > service rate
→ queue rastie
→ tail latency rastie
→ timeouty
→ retries
→ ešte vyšší arrival rate
```

Potrebné metriky:

- active downstream connections,
- active upstream connections,
- queued requests,
- queue wait time,
- rejected requests,
- connection pool saturation.

## 27. Service discovery a DNS

Proxy potrebuje získať upstream endpoints.

Modely:

- DNS resolution,
- statická konfigurácia,
- API-based service discovery,
- Kubernetes EndpointSlices,
- xDS alebo control plane,
- local sidecar registry.

Dôležité otázky:

- kedy proxy re-resolvuje meno,
- rešpektuje TTL,
- drží existujúce pool connections,
- odstráni endpoint po health failure,
- ako rýchlo aplikuje control-plane update,
- čo sa stane pri discovery outage.

`dig` správna odpoveď nedokazuje, že proxy už používa nové endpoints.

## 28. Health checks

Proxy môže používať:

### Passive health

Vyhodnocuje reálne failures: resets, timeouts, statusy.

### Active health

Pravidelne posiela probe.

Health check musí overiť správnu vrstvu. TCP connect dokazuje listener, nie aplikačnú pripravenosť. HTTP `/health` môže byť príliš plytký alebo naopak závislý od všetkých downstream systémov.

False positive odstráni zdravý endpoint; false negative posiela traffic na nefunkčný endpoint.

## 29. Draining

Pri odstránení proxy alebo upstream endpointu treba oddeliť:

- zákaz nových connections/requests,
- dokončenie existujúcich requests,
- dlhé streaming connections,
- timeout po ktorom sa zostávajúce flows ukončia.

```text
ready
→ draining
→ no new traffic
→ active work reaches zero alebo timeout
→ shutdown
```

Bez drainingu deploy vytvára resets a retries. Príliš dlhý drain blokuje rollout.

## 30. Caching

Reverse proxy môže cacheovať response podľa cache key.

Cache key môže zahŕňať:

- scheme,
- host,
- path,
- query,
- method,
- vybrané headers,
- `Vary`,
- content encoding,
- tenant alebo identity context.

Riziká:

- únik personalizovaného obsahu,
- cache poisoning,
- stale authorization decision,
- nesprávne ignorovaný query parameter,
- rozdiel medzi normalized a raw path,
- nebezpečné cacheovanie error response.

Cache policy musí rešpektovať `Cache-Control`, `Vary`, cookies, authorization a invalidation model.

## 31. Compression

Proxy môže komprimovať alebo dekomprimovať response.

Trade-offy:

- nižší bandwidth,
- vyšší CPU,
- zmena cache key podľa `Accept-Encoding`,
- buffering,
- security riziká pri kompresii secrets s attacker-controlled inputom,
- double compression alebo content-length mismatch.

Compression má byť explicitne testovaná pre streaming a range requests.

## 32. Request size a protocol limits

Proxy môže odmietnuť request ešte pred upstreamom podľa:

- header size,
- počet headers,
- request-line length,
- body size,
- chunk framing,
- HTTP/2 stream limits,
- decompressed size.

Fungovanie malých requestov neznamená, že path podporuje veľké uploads. Limit môže existovať na každej proxy vrstve aj v aplikácii.

## 33. Protocol translation

Proxy môže prepájať odlišné protokoly:

- HTTP/3 downstream → HTTP/2 upstream,
- HTTP/2 downstream → HTTP/1.1 upstream,
- TLS downstream → plaintext upstream,
- gRPC → HTTP/2 upstream,
- WebSocket upgrade → raw framed stream.

Translation môže meniť:

- multiplexing,
- connection count,
- header representation,
- backpressure,
- cancellation,
- retry možnosti,
- observability.

HTTP/2 multiplexing na jednej strane nezaručuje multiplexing na druhej.

## 34. Status attribution

Bežné proxy-generated statusy:

### `502 Bad Gateway`

Proxy nedostala platnú upstream response. Možnosti:

- connection refused alebo reset,
- upstream TLS failure,
- protocol mismatch,
- invalid response framing,
- upstream zavrel connection pred headers.

### `503 Service Unavailable`

Proxy nemá dostupný backend alebo policy vedome odmieta traffic:

- všetky endpoints unhealthy,
- maintenance,
- circuit breaker,
- queue alebo concurrency limit,
- discovery bez endpoints.

### `504 Gateway Timeout`

Upstream nedokončil požadovanú fázu v timeout budgete.

Konkrétna implementácia môže statusy mapovať odlišne. Access/error log musí určiť, či status vytvorila proxy alebo upstream.

## 35. Security hranice

Proxy spracúva nedôveryhodný traffic a často má prístup do internej siete.

Riziká:

- open forward proxy,
- SSRF cez dynamický upstream,
- request smuggling,
- response splitting,
- header spoofing,
- path normalization bypass,
- Host header injection,
- slabá TLS origin validation,
- neobmedzený CONNECT,
- secrets v logoch,
- admin endpoint na verejnom listeneri,
- plugin alebo scripting escape.

Proxy má používať least privilege egress a presný allowlist upstream destinations.

## 36. Request smuggling

Request smuggling vzniká, keď dve HTTP vrstvy nesúhlasia, kde request končí.

Príčiny môžu zahŕňať rozdielnu interpretáciu:

- `Content-Length`,
- `Transfer-Encoding`,
- duplicitných headers,
- whitespace,
- HTTP/2 → HTTP/1 translation,
- neplatného framingu.

Proxy má nejednoznačný request odmietnuť alebo canonicalizovať konzistentne. Backend nemá dostávať framing, ktorý proxy interpretovala inak.

## 37. Observability

Sleduj downstream a upstream samostatne.

### Downstream

- accepted connections,
- TLS handshake failures,
- request rate,
- client disconnects,
- request body read time,
- downstream bytes,
- downstream status.

### Routing a queue

- route name,
- selected cluster/pool,
- queue wait,
- retries,
- circuit breaker action,
- cache hit/miss.

### Upstream

- DNS/discovery time,
- connect time,
- TLS time,
- time to response headers,
- response body duration,
- reset reason,
- endpoint identity,
- upstream status.

### End-to-end

- total request time,
- request ID alebo trace ID,
- proxy-generated vs upstream-generated response,
- bytes in/out,
- retry count.

Pri logovaní chráň authorization headers, cookies, query secrets a request bodies.

## 38. Diagnostický postup

Request funguje priamo na upstream, ale nie cez proxy.

1. Over DNS na proxy endpoint.
2. Over client → proxy route, TCP a TLS.
3. Skontroluj SNI, Host/authority a certificate.
4. Nájdite request v proxy access logu podľa request ID.
5. Over route match a rewrites.
6. Over body/header limity a protocol parsing.
7. Zisti vybraný upstream endpoint.
8. Over proxy → upstream DNS/service discovery.
9. Over connect a upstream TLS.
10. Porovnaj forwarding headers a Host používané pri direct teste.
11. Porovnaj timeouty, buffering a retries.
12. Skontroluj status origin: proxy alebo upstream.
13. Otestuj direct upstream z proxy network namespace, nie iba z administrátorského laptopu.
14. Po náprave over celý client path aj security policy.

## 39. Typické symptómy

### Funguje priamo, nie cez proxy

Často Host/SNI mismatch, path rewrite, forwarding header, TLS trust, body limit alebo upstream route.

### Funguje cez jednu proxy vrstvu, nie cez celý chain

Možná nedôveryhodná forwarding header chain, rozdielny timeout, request-size limit alebo protocol translation.

### Malé requesty fungujú, veľké nie

Body limit, request buffering storage, read timeout, MTU alebo upstream limit.

### Krátke requesty fungujú, streaming sa odpája

Idle timeout, buffering, chýbajúci upgrade alebo drain policy.

### Po DNS zmene proxy stále používa starý backend

Existujúci connection pool, vlastná DNS cache, control-plane delay alebo statická endpoint konfigurácia.

### Klient dostáva `504`, backend nevidí request

Timeout mohol vzniknúť pri DNS, connect, TLS alebo queue fáze pred odoslaním upstream requestu.

### Backend loguje proxy IP ako klienta

Chýba forwarding metadata alebo backend nepozná trusted proxy chain.

## 40. Časté omyly

### „Reverse proxy je iba DNS alias“

Nie. Proxy ukončuje downstream flow a vytvára upstream flow.

### „Forward proxy a reverse proxy sa líšia iba smerom šípky“

Líšia sa aj trust modelom, konfiguráciou klienta, identity ownershipom a policy účelom.

### „X-Forwarded-For je vždy client IP“

Nie. Je dôveryhodný iba cez kontrolovaný proxy chain.

### „502 znamená aplikačnú chybu backendu“

Často vznikne pred platnou upstream HTTP response.

### „Proxy retry je vždy bezpečný“

Nie. Ambiguous failure môže viesť k duplicitnej operácii.

### „TLS termination odstráni potrebu interného šifrovania“

Nie automaticky. Rozhoduje threat model a trust boundary.

### „Buffering vyrieši backpressure“

Nie. Iba ju presunie a dočasne absorbuje.

### „DNS TTL určuje, kedy proxy zmení backend“

Nie vždy. Proxy môže mať vlastnú cache a existujúce connection pools.

### „L4 proxy nemení connection semantics“

Aj L4 proxy typicky vytvára dva samostatné transportné flows.

## 41. Kontrolné otázky

1. Aký je rozdiel medzi routerom, NATom a proxy?
2. Prečo má proxy downstream a upstream connection?
3. Aký je rozdiel medzi forward a reverse proxy?
4. Čo presne robí HTTP CONNECT?
5. Aké riziká prináša TLS inspection?
6. Aký je rozdiel medzi L4 a L7 proxy?
7. Ako TLS termination mení certificate a trust ownership?
8. Kedy sú forwarding headers dôveryhodné?
9. Načo slúži PROXY protocol a aký mismatch môže vzniknúť?
10. Prečo rozdielna path normalization vytvára security riziko?
11. Aké trade-offy má request a response buffering?
12. Prečo backpressure nemožno odstrániť?
13. Ako koordinovať timeout budget cez viac vrstiev?
14. Kedy je proxy retry ambiguous a nebezpečný?
15. Ako vzniká retry amplification?
16. Prečo connection pooling oneskoruje reakciu na DNS zmenu?
17. Aký je rozdiel medzi passive a active health checkom?
18. Čo znamená draining?
19. Ako chybný cache key spôsobí únik dát?
20. Čo typicky rozlišuje `502`, `503` a `504`?
21. Aké metriky treba oddeliť na downstream a upstream strane?
22. Ako diagnostikuješ request fungujúci priamo, ale nie cez proxy?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Firewally](firewalls.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Load balancing →](load-balancing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->