# HTTP

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [TCP a UDP](tcp-and-udp.md), [Ports a sockets](ports-and-sockets.md), [Proxy a reverse proxy](proxy-and-reverse-proxy.md)
- Súvisiace témy: caching, cookies, authentication, REST APIs, HTTP/2, HTTP/3

## 1. Definícia

HTTP je aplikačný request-response protokol. Definuje, ako klient pomenuje cieľ, vyjadrí zamýšľanú operáciu, pošle metadata alebo body a ako server alebo intermediary vráti status, metadata a reprezentáciu výsledku.

HTTP neurčuje, ako aplikácia interne uloží dáta ani ako implementuje business logiku. Poskytuje spoločný komunikačný kontrakt medzi klientmi, origin servermi, reverse proxy, cache, gateway a ďalšími intermediaries.

HTTP semantics sú oddelené od konkrétneho transportu:

- HTTP/1.1 typicky prenáša textovo formátované messages cez TCP connection;
- HTTP/2 prenáša binárne frames a multiplexované streams nad jednou TCP connection;
- HTTP/3 prenáša HTTP semantics cez QUIC streams nad UDP.

Rovnaká metóda, status alebo header má mať rovnaký význam bez ohľadu na použitú verziu, hoci wire representation a failure model sa líšia.

## 2. Celý request lifecycle

Zjednodušený tok:

```text
URL alebo API target
  ↓ DNS a výber IP
transport connection
  ↓ prípadný TLS handshake
HTTP request
  ↓ proxy/cache/routing/policy
origin application
  ↓ business spracovanie
HTTP response
  ↓ cache/proxy/client processing
používateľský výsledok
```

HTTP diagnostika preto nezačína automaticky status kódom. Request môže zlyhať pred HTTP vrstvou pri DNS, route, TCP alebo TLS. Naopak úspešný HTTP status nemusí znamenať správny business výsledok.

Pri každom incidente urč:

1. či vznikla transportná connection;
2. či bol odoslaný platný HTTP request;
3. ktorý komponent odpoveď vytvoril;
4. či response prešla cez cache alebo transformáciu;
5. či klient výsledok interpretoval podľa očakávania.

## 3. Resource, representation a operation

**Resource** je logická entita pomenovaná URI, napríklad objednávka, používateľ alebo kolekcia reportov. URI nemusí zodpovedať súboru na disku.

```text
/orders/42
```

môže pomenovať resource „objednávka 42“ bez ohľadu na to, či je uložená v databáze, vypočítaná alebo agregovaná z viacerých systémov.

**Representation** je konkrétny prenosový tvar resource alebo výsledku:

```text
application/json
text/html
image/png
application/problem+json
```

**Method** vyjadruje zamýšľanú operáciu nad targetom. Význam requestu teda vzniká kombináciou:

```text
method + target + headers + body + application contract
```

## 4. URI, URL a request target

HTTP klient typicky začína URL:

```text
https://api.example.com:8443/orders/42?include=items#summary
```

Časti:

- `https` — scheme, ktorý určuje protokolový a bezpečnostný kontext;
- `api.example.com` — host identity pre DNS, TLS SNI a HTTP authority;
- `8443` — explicitný port;
- `/orders/42` — path;
- `include=items` — query;
- `#summary` — fragment spracovaný klientom, neposiela sa serveru v HTTP requeste.

V HTTP/1.1 sa authority typicky prenáša cez `Host`. V HTTP/2 a HTTP/3 sa používa pseudo-header `:authority`.

Request target môže mať viac foriem podľa kontextu, napríklad origin-form pre bežný origin request alebo authority-form pri `CONNECT`. Proxy a server musia správne validovať, či target zodpovedá očakávanému typu requestu.

## 5. HTTP/1.1 request a response

Request:

```http
GET /orders/42?include=items HTTP/1.1
Host: api.example.com
Accept: application/json
User-Agent: example-client/1.4

```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 27
Cache-Control: private, max-age=30

{"id":42,"status":"paid"}
```

Message obsahuje:

1. start line;
2. headers;
3. prázdny riadok;
4. voliteľné body.

Wire syntax HTTP/2 a HTTP/3 je odlišná, ale logický model method, target, headers, body a status zostáva.

## 6. Method semantics

### GET

`GET` žiada aktuálnu reprezentáciu resource. Má byť **safe**: jeho zamýšľaným efektom nemá byť zmena aplikačného stavu.

To nevylučuje prevádzkové vedľajšie efekty, napríklad access log, audit event alebo cache warming. Znamená to, že klient môže GET považovať za čítaciu operáciu a browser, crawler alebo cache ho môže vykonať bez potvrdenia business zmeny.

### HEAD

`HEAD` má rovnaké semantics ako GET, ale response neobsahuje body. Headers by mali opisovať rovnakú reprezentáciu, akú by vrátil GET.

Používa sa na kontrolu metadata, validity alebo veľkosti bez prenosu celého obsahu. Aplikácia však musí zabezpečiť, aby HEAD nešiel úplne odlišnou logikou s nekonzistentnými headers.

### POST

`POST` odovzdáva dáta resource na spracovanie. Môže:

- vytvoriť podriadený resource;
- spustiť command alebo workflow;
- odoslať formulár;
- vykonať ne-idempotentnú business operáciu.

POST nie je automaticky ne-idempotentný, ale protokol to negarantuje. Bez idempotency key alebo aplikačnej deduplikácie je retry po nejasnom timeout-e rizikový.

### PUT

`PUT` nastavuje reprezentáciu resource na známom URI. Je idempotentný na úrovni zamýšľaného výsledného stavu:

```text
PUT rovnakého obsahu raz
≈
PUT rovnakého obsahu viackrát
```

To neznamená, že každé vykonanie musí mať identický log, timestamp alebo interný event.

### PATCH

`PATCH` aplikuje čiastočnú zmenu. Jeho idempotencia závisí od patch dokumentu.

Operácia „nastav status na paid“ môže byť idempotentná. Operácia „pridaj 10 k balance“ nie je idempotentná bez dodatočného identifikátora operácie.

### DELETE

`DELETE` žiada odstránenie alebo prechod resource do odstráneného stavu. Opakovaný request môže vrátiť iný status, ale zamýšľaný výsledný stav zostáva odstránený.

### OPTIONS

`OPTIONS` zisťuje komunikačné možnosti targetu alebo servera. Browser ho používa aj pri CORS preflight, ale OPTIONS sám nevykonáva autentifikáciu ani negarantuje, že následná operácia uspeje.

## 7. Safe, idempotent a cacheable nie sú synonymá

- **Safe** — zamýšľaná operácia nemení aplikačný stav.
- **Idempotent** — opakovanie rovnakej operácie nemení výsledný stav po prvom úspechu.
- **Cacheable** — response možno podľa HTTP pravidiel a explicitnej policy uložiť a neskôr znovu použiť.

GET je typicky safe, idempotentný a cacheable. PUT je idempotentný, ale bežne nie cacheable. POST môže byť cacheable iba za konkrétnych podmienok, hoci väčšina systémov ho necachuje.

Retry policy musí zohľadniť business semantics a informáciu, či server request už mohol spracovať. Samotný názov metódy nestačí, ak aplikácia protokolový kontrakt porušuje.

## 8. Status kód ako výsledok konkrétnej vrstvy

Status kód patrí tomu komponentu, ktorý vytvoril HTTP response. Môže to byť origin, reverse proxy, WAF, API gateway alebo cache.

Preto pri chybe zisťuj:

```text
kto status vytvoril
+ v ktorej fáze requestu
+ či existuje origin response
```

### 1xx — priebežný protocol stav

- `100 Continue` — server povoľuje klientovi pokračovať s body po `Expect: 100-continue`;
- `101 Switching Protocols` — zmena protokolu, napríklad historický WebSocket upgrade cez HTTP/1.1;
- `103 Early Hints` — predbežné headers pred finálnou response.

### 2xx — request bol úspešne spracovaný podľa konkrétnej semantics

- `200 OK` — všeobecný úspech;
- `201 Created` — vznikol nový resource, často s `Location`;
- `202 Accepted` — request bol prijatý na asynchrónne spracovanie, výsledok ešte nemusí existovať;
- `204 No Content` — úspech bez response body;
- `206 Partial Content` — odpoveď na validný range request.

`200` negarantuje správnosť business dát. `202` negarantuje dokončenie práce.

### 3xx — ďalší krok, presmerovanie alebo cache revalidation

- `301` a `308` — permanentné presmerovanie;
- `302` a `307` — dočasné presmerovanie;
- `303` — klient má výsledok načítať typicky GET requestom;
- `304` — klient môže použiť uloženú reprezentáciu, response body sa neposiela.

`307` a `308` zachovávajú method a body. Historické správanie klientov pri `301` a `302` môže zmeniť POST na GET, preto musí byť redirect contract explicitný.

### 4xx — request nie je prijateľný v aktuálnom client kontexte

- `400 Bad Request` — syntax, framing alebo základná validácia;
- `401 Unauthorized` — authentication chýba alebo nie je prijateľná; často obsahuje `WWW-Authenticate`;
- `403 Forbidden` — server request rozumie, ale policy ho nepovoľuje;
- `404 Not Found` — resource nie je dostupný; môže sa použiť aj na zámerné skrytie existencie;
- `405 Method Not Allowed` — target nepodporuje danú metódu;
- `409 Conflict` — request koliduje s aktuálnym stavom;
- `412 Precondition Failed` — zlyhala podmienka, napríklad `If-Match`;
- `413 Content Too Large` — body prekročilo limit;
- `415 Unsupported Media Type` — server nevie spracovať `Content-Type`;
- `422 Unprocessable Content` — syntax je platná, ale obsah nespĺňa aplikačné pravidlá;
- `429 Too Many Requests` — rate limit; môže obsahovať `Retry-After`.

### 5xx — serverová alebo intermediary vrstva request nedokončila

- `500 Internal Server Error` — neočakávané zlyhanie komponentu;
- `502 Bad Gateway` — proxy nedostala platnú upstream response;
- `503 Service Unavailable` — dočasná nedostupnosť, overload, maintenance alebo žiadny eligible backend;
- `504 Gateway Timeout` — intermediary nedostala upstream výsledok v timeout budgete.

Konkrétny produkt môže statusy mapovať odlišne, preto koreluj response headers a proxy logs.

## 9. Headers a ich scope

HTTP headers prenášajú metadata. Ich význam závisí od toho, či opisujú request, response, representation, connection alebo intermediary.

Dôležité skupiny:

- routing a authority — `Host`, `Forwarded`, `Via`;
- representation — `Content-Type`, `Content-Encoding`, `Content-Language`;
- negotiation — `Accept`, `Accept-Encoding`, `Accept-Language`;
- framing — `Content-Length`, `Transfer-Encoding` v HTTP/1.1;
- caching — `Cache-Control`, `Age`, `ETag`, `Last-Modified`, `Vary`;
- authentication — `Authorization`, `Proxy-Authorization`, `WWW-Authenticate`;
- conditional operations — `If-None-Match`, `If-Match`, `If-Modified-Since`;
- cookies — `Cookie`, `Set-Cookie`;
- security — `Strict-Transport-Security`, `Content-Security-Policy`, `X-Content-Type-Options`;
- tracing — štandardizované alebo interné request/trace identifiers.

Header names sú case-insensitive. Hodnoty však majú vlastnú syntax a nie všetky možno bezpečne zlúčiť či rozdeliť.

## 10. Authority, Host a virtual hosting

Viac služieb môže zdieľať jednu IP a port. HTTP authority určuje, ktorú virtuálnu službu klient žiada.

```http
Host: api.example.com
```

Reverse proxy môže routeovať podľa Host. Aplikácia môže z Host zostavovať absolute URL, tenant context alebo security decision.

Host je nedôveryhodný vstup. Server alebo proxy musí:

- povoliť iba očakávané authority values;
- prepísať neautorizované forwarding headers;
- neodvodzovať password reset link alebo redirect z nekontrolovaného Host;
- zosúladiť TLS SNI, HTTP authority a route policy.

## 11. Message body a framing

HTTP receiver musí vedieť jednoznačne určiť hranicu každej message.

HTTP/1.1 body môže byť rámcované napríklad:

- `Content-Length`;
- chunked transfer encoding;
- semantics statusu alebo metódy, pri ktorých body nie je;
- ukončením connection v obmedzených legacy prípadoch.

Ak proxy a origin rozdielne interpretujú `Content-Length`, `Transfer-Encoding`, neplatné whitespace alebo duplicate headers, môže vzniknúť request smuggling:

```text
frontend vidí request A
backend vidí request A + začiatok requestu B
```

Bezpečný parser musí odmietnuť nejednoznačné framing combinations, normalizovať podľa špecifikácie a nepokračovať s „najlepším odhadom“.

HTTP/2 a HTTP/3 používajú explicitné frame lengths, ale downgrade alebo konverzia na HTTP/1.1 môže znovu vytvoriť framing boundary. Celý proxy chain musí mať kompatibilnú policy.

## 12. Request body lifecycle

Body môže byť:

- načítané celé do memory;
- spoolované na disk;
- streamované upstreamu;
- odmietnuté podľa size limitu;
- spracovávané po chunks.

Rozhodnutie ovplyvňuje:

- latency prvého spracovania;
- memory a disk pressure;
- schopnosť retry;
- ochranu upstreamu pred pomalým klientom;
- streaming a backpressure;
- reakciu na klientské odpojenie.

Pri upload incidente sleduj limit a timeout na každej vrstve: browser, CDN, load balancer, proxy, application server a samotná aplikácia.

## 13. Persistent connections a pooling

HTTP/1.1 predvolene podporuje persistent connections. Jedna TCP/TLS connection môže obslúžiť viac po sebe idúcich requestov.

Výhody:

- menej handshakes;
- nižšia latency;
- menší CPU a port overhead;
- lepšia efektivita congestion window.

Riziká:

- stale connections po backend restarte;
- idle timeout mismatch medzi vrstvami;
- nerovnomerný load pri dlhých pools;
- file-descriptor pressure;
- HTTP/1.1 head-of-line, ak requesty čakajú sériovo.

Connection pool má vlastný lifecycle a nie je totožný s request lifecycle. DNS alebo backend membership zmena nepresmeruje už existujúcu connection automaticky.

## 14. HTTP/1.1 pipelining

HTTP/1.1 umožňuje poslať viac requestov bez čakania na predchádzajúcu response. Responses však musia prísť v rovnakom poradí.

Ak prvý request trvá dlho, ďalšie responses čakajú aj vtedy, keď by ich server vedel dokončiť skôr. Pre interoperability, retry ambiguity a head-of-line problémy bolo pipelining v praxi málo používané.

Bežnejším riešením boli viaceré parallel connections a neskôr HTTP/2 multiplexing.

## 15. HTTP/2 lifecycle

HTTP/2 používa jednu connection s viacerými logickými streams. Každá message sa skladá z binárnych frames.

Dôležité mechanizmy:

- stream identifiers oddeľujú súbežné requesty;
- HPACK komprimuje headers pomocou zdieľaného state;
- flow control existuje na stream aj connection úrovni;
- server môže limitovať concurrent streams;
- `GOAWAY` oznamuje, že connection sa má postupne prestať používať;
- reset jedného streamu nemusí ukončiť celú connection.

HTTP/2 odstraňuje aplikačné poradie responses medzi streams, ale všetky streams zdieľajú jeden TCP byte stream. Stratený TCP segment môže dočasne blokovať doručenie frames všetkým streams.

Pri diagnostike sleduj nielen počet connections, ale aj active streams, flow-control windows, resets, `GOAWAY` a protocol negotiation cez ALPN.

## 16. HTTP/3 lifecycle

HTTP/3 používa QUIC. QUIC integruje TLS 1.3 a poskytuje samostatné reliable streams.

Dôsledky:

- packet loss v jednom stream-e nemusí blokovať dáta ostatných streams;
- connection môže prežiť zmenu klientovej IP pomocou connection identifiers;
- transport handshake a security negotiation sú integrované;
- UDP path, firewall a NAT timeouty sa stávajú súčasťou failure modelu;
- QPACK header compression musí riešiť blocking medzi encoder/decoder state.

HTTP/3 nie je iba HTTP/2 „prepnuté na UDP“. Má odlišný transportný state, observability a fallback behavior. Klient môže pri nefunkčnom UDP/QUIC prepnúť na HTTP/2 alebo HTTP/1.1, čo môže skryť selektívny problém.

## 17. Content negotiation

Klient môže deklarovať prijateľné reprezentácie:

```http
Accept: application/json
Accept-Language: sk
Accept-Encoding: gzip, br
```

Server vyberie variantu alebo vráti chybu, ak nevie požiadavku splniť.

Ak response závisí od request headera, shared cache musí túto dimenziu zahrnúť do cache key. Server preto používa `Vary`:

```http
Vary: Accept-Encoding, Accept-Language
```

Chýbajúci `Vary` môže spôsobiť, že cache doručí komprimovanú, jazykovú alebo inú variantu nesprávnemu klientovi. Príliš široký `Vary` znižuje hit ratio a môže vytvoriť nekontrolovanú cardinality.

## 18. Freshness a `Cache-Control`

Cache nepoužíva response iba preto, že ju má uloženú. Musí posúdiť freshness, scope a request directives.

Príklady:

```http
Cache-Control: public, max-age=300
Cache-Control: private, max-age=60
Cache-Control: no-cache
Cache-Control: no-store
```

- `public` povoľuje uloženie shared cache, ak ostatné pravidlá nebránia;
- `private` povoľuje uloženie klientskou cache, nie zdieľanou proxy cache;
- `max-age` určuje freshness lifetime;
- `no-cache` povoľuje uloženie, ale pred použitím vyžaduje revalidation;
- `no-store` zakazuje uloženie response;
- `must-revalidate` obmedzuje použitie stale response po expiracii.

Cache policy musí zohľadniť Authorization, cookies, personalizáciu, invalidation a chyby originu. „Nastav vysoký TTL“ nie je bezpečný návrh bez cache key a data-classification modelu.

## 19. Validators a revalidation

Validator umožní overiť, či uložená reprezentácia stále zodpovedá originu.

Strong ETag:

```http
ETag: "order-42-v7"
```

Klient môže poslať:

```http
If-None-Match: "order-42-v7"
```

Ak sa representation nezmenila, server vráti:

```http
304 Not Modified
```

bez body. Klient použije svoje uložené body a aktualizované metadata.

`Last-Modified` a `If-Modified-Since` používajú časový validator, ktorý má nižšiu presnosť a môže byť problematický pri rýchlych zmenách alebo clock inconsistencies.

## 20. Conditional writes a lost updates

HTTP preconditions možno použiť aj na optimistic concurrency control.

Klient načíta resource s ETag:

```http
ETag: "v42"
```

Pri zmene pošle:

```http
If-Match: "v42"
```

Server vykoná write iba ak aktuálna verzia stále zodpovedá. Inak vráti `412 Precondition Failed`.

Tým sa zabráni scenáru:

```text
klient A načíta v42
klient B načíta v42
klient A uloží v43
klient B nevedome prepíše zmenu A
```

Aplikačný backend musí condition vyhodnotiť atomicky so zápisom. Samotný header bez transakčnej kontroly lost update nevyrieši.

## 21. Redirect lifecycle

Redirect response obsahuje status a `Location`:

```http
HTTP/1.1 308 Permanent Redirect
Location: https://www.example.com/new-path
```

Klient vytvorí nový request. To znamená nový target a potenciálne nový DNS, TCP a TLS lifecycle.

Riziká:

- redirect loop medzi proxy a aplikáciou;
- zmena method pri nesprávnom status kóde;
- open redirect cez nekontrolovaný parameter;
- strata Authorization pri cross-origin presmerovaní;
- cacheovanie permanentného redirectu;
- downgrade na nezabezpečený scheme.

Za reverse proxy musí aplikácia správne dôverovať `Forwarded` alebo `X-Forwarded-Proto`, inak môže stále považovať request za HTTP a presmerovávať ho na HTTPS, ktoré proxy znovu terminovala.

## 22. Cookies a browser session state

Server nastaví cookie:

```http
Set-Cookie: session=opaque-value; Secure; HttpOnly; SameSite=Lax; Path=/
```

Browser ju neskôr automaticky pridá podľa scope:

```http
Cookie: session=opaque-value
```

Dôležité atribúty:

- `Secure` — posielať iba v secure context-e;
- `HttpOnly` — neprístupná bežnému JavaScript API;
- `SameSite` — obmedzuje cross-site odosielanie;
- `Domain` — rozširuje host scope; vynechanie vytvorí host-only cookie;
- `Path` — určuje URL path matching, nie security boundary;
- `Max-Age` alebo `Expires` — persistence;
- prefixy ako `__Host-` môžu vynútiť prísnejšie atribúty v podporovaných browseroch.

Cookie scope a automatické odosielanie sú základom CSRF threat modelu. `HttpOnly` chráni pred čítaním cez script, ale nezabráni browseru cookie odoslať.

## 23. Authentication a authorization

HTTP poskytuje mechanizmy na prenesenie credentials a challenges:

```http
Authorization: Bearer <token>
WWW-Authenticate: Bearer realm="api"
```

Rozlišuj:

- authentication — kto je volajúci;
- authorization — čo smie vykonať;
- session management — ako sa identity state zachová medzi requestmi;
- transport security — kto môže credentials po ceste pozorovať alebo meniť.

Basic authentication iba zakóduje credentials; bez TLS nie je bezpečná. Bearer token môže použiť každý, kto ho získa. Access logy, trace headers a error dumps nesmú credentials zapisovať.

## 24. CORS

CORS je browser-enforced mechanizmus, ktorý rozhoduje, či script z jedného originu smie čítať response iného originu.

Origin je kombinácia:

```text
scheme + host + port
```

Server môže odpovedať:

```http
Access-Control-Allow-Origin: https://app.example
Access-Control-Allow-Methods: GET, POST
Access-Control-Allow-Credentials: true
```

Pri nejednoduchom requeste browser najprv vykoná preflight `OPTIONS`.

CORS:

- nie je server-side authentication;
- neblokuje `curl`, backend klienta ani útočníkov server-to-server;
- nemusí zabrániť samotnému odoslaniu requestu, iba sprístupneniu response scriptu;
- pri credentials nemôže bezpečne používať wildcard origin rovnakým spôsobom ako public response;
- vyžaduje `Vary: Origin`, ak response závisí od originu a prechádza cache.

## 25. Compression

Response compression znižuje prenesené bytes:

```http
Accept-Encoding: gzip, br
Content-Encoding: br
```

Trade-offy:

- CPU náklady na kompresiu;
- latency pre malé responses;
- memory a buffering;
- cache varianty podľa `Accept-Encoding`;
- zbytočná práca pre už komprimované formáty;
- riziko side-channel útokov pri kombinácii secrets a attacker-controlled textu.

Proxy a origin musia koordinovať, kto komprimuje a či `Content-Length`, ETag a cache key opisujú komprimovanú alebo pôvodnú variantu.

## 26. Range requests

Klient môže žiadať časť representation:

```http
Range: bytes=0-999
```

Server môže odpovedať:

```http
HTTP/1.1 206 Partial Content
Content-Range: bytes 0-999/5000
```

Použitie:

- pokračovanie downloadu;
- media seeking;
- selektívne čítanie veľkého objektu.

Server musí správne riešiť invalid ranges, validators a zmenu objektu medzi časťami. Inak klient môže poskladať nekonzistentný obsah.

## 27. Intermediaries a transformácie

HTTP request môže prejsť cez CDN, WAF, reverse proxy, service mesh alebo API gateway. Každý intermediary môže:

- terminovať connection;
- meniť headers;
- normalizovať path;
- cacheovať response;
- vykonať retry;
- komprimovať alebo dekomprimovať;
- generovať vlastný status;
- pridať tracing metadata.

Preto end-to-end contract musí definovať:

- ktoré headers sú hop-by-hop a ktoré end-to-end;
- kto je trusted proxy;
- kto vlastní timeout a retry;
- ako sa zachová client identity;
- ako sa korelujú request IDs;
- kto môže transformovať body.

## 28. Timeouty a client cancellation

HTTP request môže mať viac timeoutov:

- DNS a connect timeout;
- TLS handshake timeout;
- request-header timeout;
- request-body timeout;
- upstream connect timeout;
- time to first byte;
- idle timeout;
- total deadline.

Klient môže request zrušiť, ale server alebo upstream mohol business operáciu už dokončiť. Cancellation nie je rollback.

Deadline má byť prenášaný alebo prepočítaný cez proxy chain tak, aby downstream vrstva nečakala dlhšie než jej caller. Nesprávne timeout poradie vytvára orphan work a retry amplification.

## 29. Observability

Meraj oddelene:

- request rate podľa normalizovanej route a method;
- status class a konkrétny status;
- origin status versus proxy-generated status;
- end-to-end latency a jednotlivé fázy;
- request/response body size;
- active connections a streams;
- HTTP protocol version;
- cache hit, miss, stale a revalidation;
- retries, redirects a resets;
- malformed alebo rejected messages;
- queueing a body buffering;
- client cancellation;
- trace/request identifier.

Nevkladaj raw resource IDs, query strings alebo celé URL do metric labels. Vytvorilo by to vysokú cardinality a mohlo by odhaliť citlivé dáta.

## 30. Diagnostický postup

Request `https://api.example.com/orders/42` zlyháva:

```bash
curl -v https://api.example.com/orders/42
curl -I https://api.example.com/orders/42
curl --http1.1 -v https://api.example.com/orders/42
curl --http2 -v https://api.example.com/orders/42
curl --resolve api.example.com:443:<IP> -v https://api.example.com/orders/42
```

Postup:

1. potvrď používateľský symptóm a presný request;
2. odlíš DNS, TCP a TLS od HTTP;
3. zaznamenaj negotiated protocol version;
4. over method, authority, path, query a body;
5. sleduj redirects vrátane každého nového targetu;
6. identifikuj komponent, ktorý status vytvoril;
7. porovnaj request/response headers pred a za proxy;
8. over framing, size limits a buffering;
9. otestuj cache bypass alebo revalidation bez zmazania dôkazov;
10. koreluj request ID cez proxy a origin logs;
11. porovnaj origin priamym testom iba ako kontrolovaný experiment;
12. po náprave over business výsledok, nie iba status.

## 31. Typické failure patterns

### `400 Bad Request`

Môže ho vytvoriť klientský parser, edge proxy, WAF alebo origin. Hľadaj neplatný request target, Host, framing, duplicate headers, body encoding alebo normalization mismatch.

### `401` verzus `403`

`401` typicky znamená, že authentication nie je prijateľná. `403` znamená, že request bol identifikovaný alebo pochopený, ale policy ho nepovoľuje. Aplikácie však niekedy zámerne mapujú oba stavy inak, preto over contract.

### `304`, ale klient vidí staré dáta

Skontroluj validator, cache key, `Vary`, freshness, service worker alebo application cache. `304` prikazuje použiť uložené body; chyba môže byť práve v tom uloženom variante.

### Funguje HTTP/1.1, nie HTTP/2

Over ALPN, proxy podporu, concurrent stream limits, HTTP/2 flow control, `GOAWAY`, header size a downgrade path.

### Redirect loop

Porovnaj external scheme/host s tým, čo vidí aplikácia. Skontroluj trusted forwarding headers, route rewrite a permanent redirect cache.

### Malé requesty fungujú, veľké nie

Skontroluj body limit, `Expect: 100-continue`, proxy buffering, disk spool, timeout, flow control, compression a upstream limit.

### Občasný duplicate write po timeout-e

Request mohol byť spracovaný pred stratou response a retry vytvoril druhú operáciu. Potrebná je idempotency alebo deduplication, nie iba dlhší timeout.

## 32. Časté omyly

### „HTTP status 200 znamená správny business výsledok“

Nie. Body môže byť nesprávne, neúplné alebo môže aplikácia vracať business chybu v úspešnom transportnom obale.

### „GET nikdy nič nemení“

Má byť safe podľa kontraktu. Zle navrhnutá aplikácia to môže porušiť, čím sa stáva nebezpečnou pre prefetch, crawler, cache a retry.

### „`no-cache` znamená necachovať“

Nie. Znamená, že uložená response sa pred použitím musí revalidovať. `no-store` zakazuje uloženie.

### „CORS chráni API pred ľubovoľnými klientmi“

Nie. CORS vynucuje browser pre script access. Server stále potrebuje authentication, authorization a CSRF ochranu podľa modelu.

### „HTTP/2 otvorí connection pre každý request“

Nie. Typicky multiplexuje viac streams nad jednou connection.

### „Client timeout znamená, že server nič nevykonal“

Nie. Timeout opisuje chýbajúci výsledok v klientskom budgete, nie stav business transakcie.

## 33. Praktický checklist

Pred produkčným nasadením HTTP služby over:

- canonical scheme, host a path behavior;
- explicitné method semantics a idempotency;
- konzistentné status codes a error body contract;
- request body size a timeout limits;
- framing a parser consistency cez proxy chain;
- cache key, `Cache-Control`, validators a `Vary`;
- trusted forwarding headers;
- cookie security attributes;
- CORS policy pre konkrétne origins;
- HTTP/1.1, HTTP/2 a prípadný HTTP/3 fallback;
- observability bez credentials a high-cardinality labels;
- graceful draining a client cancellation behavior.

## 34. Kontrolné otázky

1. Aký je rozdiel medzi resource, representation a operation?
2. Prečo fragment URL nie je súčasť serverového HTTP requestu?
3. Aký je rozdiel medzi safe, idempotent a cacheable metódou?
4. Prečo môže retry idempotentnej metódy stále vytvoriť prevádzkové side effects?
5. Ako rozlíšiš status vytvorený originom od statusu vytvoreného proxy?
6. Prečo je HTTP/1.1 message framing bezpečnostne kritické?
7. Ako sa líši request multiplexing v HTTP/1.1, HTTP/2 a HTTP/3?
8. Čo znamená `Vary` pre cache key?
9. Aký je rozdiel medzi `no-cache` a `no-store`?
10. Ako ETag podporuje revalidation aj optimistic concurrency control?
11. Prečo CORS nie je authentication ani firewall?
12. Ako diagnostikuješ redirect loop za reverse proxy?
13. Prečo client cancellation negarantuje rollback serverovej operácie?
14. Ako zistíš, ktorý limit zastavil veľký upload?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Load balancing](load-balancing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: HTTPS, TLS, certificates a PKI →](https-tls-certificates-pki.md)
<!-- KNOWLEDGE-NAVIGATION:END -->