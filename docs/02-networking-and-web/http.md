# HTTP

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [TCP a UDP](tcp-and-udp.md), [Ports a sockets](ports-and-sockets.md), [Proxy a reverse proxy](proxy-and-reverse-proxy.md)
- Súvisiace témy: caching, cookies, authentication, REST APIs, HTTP/2, HTTP/3

## 1. Definícia

HTTP je aplikačný request-response protokol používaný na prenos reprezentácií resources a vykonávanie operácií nad nimi.

HTTP semantics sú oddelené od konkrétneho transportu:

- HTTP/1.1 typicky používa TCP,
- HTTP/2 používa multiplexované streams nad jedným TCP connection,
- HTTP/3 používa QUIC nad UDP.

## 2. Request a response

HTTP request obsahuje:

```text
method + target + version
headers
prázdny riadok
voliteľné body
```

Príklad:

```http
GET /orders/42?include=items HTTP/1.1
Host: api.example.com
Accept: application/json
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 27

{"id":42,"status":"paid"}
```

## 3. Resources a representations

Resource je logický objekt adresovaný URI. Representation je konkrétny formát jeho stavu, napríklad JSON, HTML alebo image.

```text
/orders/42          resource
application/json    representation format
```

URI neznamená automaticky súbor na disku.

## 4. Methods

### GET

Číta resource alebo representation. Má byť safe a idempotentný.

### HEAD

Rovnaké semantics ako GET, ale bez response body.

### POST

Typicky vytvára podriadený resource alebo spúšťa spracovanie. Nie je automaticky idempotentný.

### PUT

Nahrádza alebo vytvára resource na známom URI. Má byť idempotentný.

### PATCH

Aplikuje čiastočnú zmenu. Idempotencia závisí od patch formátu a operácie.

### DELETE

Odstráni resource alebo nastaví jeho odstránený stav. Má byť idempotentný na úrovni výsledného stavu.

### OPTIONS

Opisuje podporované komunikačné možnosti a používa sa aj pri CORS preflight.

## 5. Safe a idempotent semantics

- **Safe** method nemá meniť server state ako zamýšľaný efekt.
- **Idempotent** method môže byť opakovaný bez ďalšej zmeny výsledného stavu.

To neznamená nulové vedľajšie efekty. GET môže zapisovať access log alebo metriku.

Retry policy sa má opierať o reálne operation semantics, nie iba názov method.

## 6. Status codes

### 1xx — informational

Priebežný protocol stav, napríklad `100 Continue`.

### 2xx — success

- `200 OK`
- `201 Created`
- `202 Accepted`
- `204 No Content`

### 3xx — redirection a caching

- `301 Moved Permanently`
- `302 Found`
- `303 See Other`
- `304 Not Modified`
- `307 Temporary Redirect`
- `308 Permanent Redirect`

`307` a `308` zachovávajú method a body. Historické client správanie pri `301/302` môže method meniť.

### 4xx — client-side request problem

- `400 Bad Request`
- `401 Unauthorized` — v praxi chýbajúca alebo neplatná authentication
- `403 Forbidden` — identity je známa, ale operácia nie je povolená
- `404 Not Found`
- `409 Conflict`
- `412 Precondition Failed`
- `413 Content Too Large`
- `429 Too Many Requests`

### 5xx — server-side failure

- `500 Internal Server Error`
- `502 Bad Gateway`
- `503 Service Unavailable`
- `504 Gateway Timeout`

Status kód je súčasť aplikačného kontraktu, nie iba textový popis.

## 7. Headers

Headers nesú metadata o requeste, response, representation a intermediaries.

Dôležité skupiny:

- content negotiation: `Accept`, `Content-Type`, `Accept-Encoding`,
- caching: `Cache-Control`, `ETag`, `Last-Modified`, `Vary`,
- authentication: `Authorization`, `WWW-Authenticate`,
- routing: `Host`, `Forwarded`, `Via`,
- conditional requests: `If-None-Match`, `If-Match`, `If-Modified-Since`,
- cookies: `Cookie`, `Set-Cookie`,
- security: `Strict-Transport-Security`, `Content-Security-Policy`.

Headers majú case-insensitive names, ale hodnoty majú vlastnú syntax.

## 8. Message body framing

HTTP/1.1 body môže byť určené cez:

- `Content-Length`,
- chunked transfer encoding,
- connection close v obmedzených prípadoch,
- method/status semantics bez body.

Nejednoznačné framing rules medzi proxy a backendom môžu viesť k HTTP request smugglingu.

Proxy chain musí konzistentne validovať `Content-Length` a `Transfer-Encoding`.

## 9. Persistent connections

HTTP/1.1 predvolene používa persistent connections.

Výhody:

- menej TCP/TLS handshakes,
- nižšia latency,
- menší CPU overhead.

Riziká:

- idle connection limits,
- stale pooled connections,
- head-of-line blocking pri sériovom HTTP/1.1 použití,
- nerovnomerné rozdelenie cez load balancer.

## 10. HTTP/1.1 pipelining

Klient môže poslať viac requestov bez čakania na response, ale responses musia zostať v poradí. Praktická podpora bola obmedzená pre head-of-line a proxy interoperability problémy.

## 11. HTTP/2

HTTP/2 zavádza:

- binary framing,
- multiplexované streams,
- header compression HPACK,
- stream priorities v historickom modeli,
- jeden connection pre viac súbežných requestov.

Odstraňuje HTTP/1.1 aplikačný head-of-line medzi requestmi, ale všetky streams stále zdieľajú TCP. Strata jedného TCP segmentu môže dočasne blokovať celý connection.

## 12. HTTP/3

HTTP/3 používa QUIC:

- samostatné reliable streams,
- TLS 1.3 integráciu,
- connection migration,
- menší cross-stream head-of-line dopad pri packet loss.

HTTP/3 nie je iba HTTP/2 nad UDP. Transport a framing sú prispôsobené QUIC.

## 13. Content negotiation

Klient môže deklarovať preferencie:

```http
Accept: application/json
Accept-Language: sk
Accept-Encoding: gzip, br
```

Server vyberie representation a môže pridať:

```http
Vary: Accept-Encoding
```

`Vary` je kritický pre cache key. Chýbajúci `Vary` môže cacheovať nesprávnu variantu.

## 14. Caching

`Cache-Control` príklady:

```http
Cache-Control: public, max-age=300
Cache-Control: private, no-cache
Cache-Control: no-store
```

- `no-cache` neznamená „nikdy neuložiť“; znamená revalidovať pred použitím.
- `no-store` zakazuje ukladanie.
- `private` obmedzuje shared caches.

Caching musí zohľadniť authorization, cookies, `Vary`, freshness a invalidation.

## 15. Validators a conditional requests

ETag:

```http
ETag: "v42"
If-None-Match: "v42"
```

Ak sa representation nezmenila:

```http
304 Not Modified
```

Pre optimistic concurrency:

```http
If-Match: "v42"
```

Server môže vrátiť `412 Precondition Failed`, ak klient mení zastaranú verziu.

## 16. Cookies

Server nastaví:

```http
Set-Cookie: session=abc; Secure; HttpOnly; SameSite=Lax; Path=/
```

Dôležité atribúty:

- `Secure` — cookie sa posiela iba cez secure transport,
- `HttpOnly` — JavaScript ju nemôže čítať cez bežné API,
- `SameSite` — obmedzuje cross-site odosielanie,
- `Domain` a `Path` — určujú scope,
- `Max-Age` alebo `Expires` — životnosť.

Cookies sú automaticky posielané podľa scope, čo je relevantné pre CSRF threat model.

## 17. Authentication a authorization

HTTP poskytuje framing pre authentication challenges a credentials, ale business authorization je aplikačná politika.

Príklady:

```http
Authorization: Bearer <token>
Authorization: Basic <credentials>
```

Credentials, tokens a osobné dáta nepatria do access logov.

## 18. CORS

Cross-Origin Resource Sharing je browser policy mechanizmus.

Server odpovedá napríklad:

```http
Access-Control-Allow-Origin: https://app.example
Access-Control-Allow-Methods: GET, POST
```

Pri niektorých requests browser najprv vykoná preflight `OPTIONS`.

CORS nie je firewall ani server-side authentication. Nebrowserový klient ho nemusí rešpektovať.

## 19. Compression

HTTP compression znižuje prenesené bytes, ale spotrebúva CPU a môže meniť security risk pri secrets kombinovaných s attacker-controlled inputom.

Sleduj:

- komprimovateľný content type,
- minimum size,
- CPU overhead,
- cache variants,
- already-compressed formats.

## 20. Range requests

```http
Range: bytes=0-999
```

Server môže vrátiť `206 Partial Content`.

Použitie:

- resumable downloads,
- media seeking,
- paralelné sťahovanie.

## 21. Observability

Sleduj:

- request rate podľa method/path/status,
- latency percentily,
- response size,
- active connections a streams,
- retries a redirects,
- cache hit ratio,
- client/proxy/upstream protocol version,
- malformed requests,
- body limit failures,
- timeout source.

Path labels v metrikách musia byť normalizované, aby nevznikla neobmedzená cardinality.

## 22. Diagnostický postup

Pri HTTP zlyhaní:

```bash
curl -v https://example.com/path
curl -I https://example.com/path
curl --http1.1 -v https://example.com/path
curl --http2 -v https://example.com/path
```

Postup:

1. odlíš DNS, TCP a TLS od HTTP,
2. zachyť request method, target a Host,
3. skontroluj redirects,
4. over request/response headers,
5. porovnaj status source v proxy chain-e,
6. otestuj protocol version,
7. skontroluj body limits a framing,
8. porovnaj cache a origin response,
9. koreluj request ID v logoch,
10. over používateľský výsledok.

## 23. Typické symptómy

### `400 Bad Request`

Malformed request, protocol framing, neplatný Host alebo proxy normalization.

### `401` vs. `403`

Authentication chýba/zlyhala vs. operácia nie je povolená.

### `304`, ale klient vidí staré dáta

Nesprávny ETag, cache key, TTL alebo invalidation.

### Funguje HTTP/1.1, nie HTTP/2

ALPN, proxy protocol support, stream limits alebo implementation bug.

### Redirect loop

Proxy nesprávne prenáša scheme/host a aplikácia stále presmerúva na „správnu“ URL.

## 24. Časté omyly

### „HTTP status 200 znamená správny business výsledok“

Nie. Body môže obsahovať chybný alebo neúplný výsledok.

### „GET nikdy nič nemení“

Má byť safe podľa contractu, ale zle navrhnutá aplikácia to môže porušiť.

### „no-cache znamená necachovať“

Znamená revalidovať pred použitím.

### „CORS chráni API pred všetkými klientmi“

Je to primárne browser-enforced policy.

### „HTTP/2 otvorí connection pre každý request“

Typicky multiplexuje viac streams nad jedným connection.

## 25. Kontrolné otázky

1. Aký je rozdiel medzi resource a representation?
2. Čo znamenajú safe a idempotent method?
3. Aký je rozdiel medzi `401` a `403`?
4. Prečo je message framing bezpečnostne kritické?
5. Ako sa líši HTTP/1.1, HTTP/2 a HTTP/3 multiplexing?
6. Čo znamená `Vary` pre cache?
7. Aký je rozdiel medzi `no-cache` a `no-store`?
8. Ako ETag podporuje caching aj concurrency control?
9. Prečo CORS nie je authentication mechanizmus?
10. Ako diagnostikuješ redirect loop za reverse proxy?
