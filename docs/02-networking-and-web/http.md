# HTTP

HTTP je aplikačný request-response protokol. Definuje method, target, headers, message body a response status, ale nedefinuje interný database model ani automaticky nezaručuje business side effect. Jeden HTTP request môže prejsť cez cache, proxy alebo load balancer a môže byť prenášaný cez HTTP/1.1, HTTP/2 alebo HTTP/3.

URL obsahuje scheme, authority, path a voliteľný query a fragment. DNS používa hostname, TLS ho môže používať pri SNI a certificate validation a HTTP routing používa `Host` alebo `:authority`. Path pomenúva aplikačný target v rámci originu.

Methods majú semantics. `GET` a `HEAD` majú byť safe z pohľadu zamýšľanej state change. `PUT` a `DELETE` majú idempotentný zamýšľaný výsledok. `POST` je všeobecná processing metóda a nie je implicitne idempotentná. Tieto vlastnosti sú contract, nie vynútenie protokolom.

Status code opisuje HTTP outcome. `2xx` neznamená automaticky dokončený business proces. `202 Accepted` napríklad potvrdzuje prijatie na neskoršie spracovanie. `4xx` a `5xx` tiež potrebujú stabilný machine-readable error model.

HTTP caching používa cache key, freshness, validators a directives ako `Cache-Control`, `ETag`, `If-None-Match` a `Vary`. Cache hit môže obslúžiť klienta bez kontaktu s originom. Úspešný response preto nemusí dokazovať aktuálne zdravie backendu.

Neutrálny request:

```http
GET /items/42 HTTP/1.1
Host: api.example.test
Accept: application/json
```

Response representation má `Content-Type`; JSON syntax sama nehovorí o domain schéme. Conditional request s `If-Match` alebo `If-None-Match` môže poskytovať optimistic concurrency alebo cache validation.

HTTP/2 multiplexuje viac streams v jednom TCP connection. HTTP/3 prenáša HTTP semantics cez QUIC nad UDP. Connection-level health preto nemusí reprezentovať každý request stream.

Retry mutating requestu musí rešpektovať idempotency key alebo iný deduplication contract. Timeout môže znamenať unknown business outcome, nie jednoznačné zlyhanie servera.

Po DNS, routing, TCP a TLS dostane Atlas reverse proxy aplikačný request:

```http
POST /v1/orders HTTP/1.1
Host: api.atlas.example
Content-Type: application/json
Idempotency-Key: op-8421
X-Request-ID: req-7f31

{"customerId":"cus-742","currency":"EUR","amount":"59.90"}
```

HTTP definuje semantics requestu a response medzi clientom, intermediaries a originom. Neurčuje interný database model ani zaručený business commit. Správna diagnostika preto odlišuje protocol outcome od application outcome.

## Target, authority a representation

URL `https://api.atlas.example/v1/orders` obsahuje scheme, authority a path. DNS a TLS používajú hostname, HTTP routing používa `Host` alebo `:authority` a application používa path a method.

Representation je prenášaný tvar resource alebo výsledku. `application/json` hovorí o media type, nie automaticky o schéme a semantics. Rovnaké JSON fields môžu mať odlišný význam v inej API verzii.

Client môže cez `Accept` vyjadriť podporované response types a server cez `Content-Type` oznámiť skutočný typ. Nesprávne media metadata môže rozbiť cache alebo parser, hoci body vyzerá čitateľne.

## Method semantics

`GET` a `HEAD` majú byť safe z pohľadu zamýšľanej application state change. `PUT` a `DELETE` majú idempotentný zamýšľaný výsledok. `POST` je všeobecná processing metóda a protokol negarantuje idempotenciu. `PATCH` závisí od konkrétneho patch dokumentu.

Safe a idempotent neznamená „bez akýchkoľvek side effects“. GET môže zapisovať access log. Opakovaný PUT môže vytvoriť ďalší audit event. Dôležité je, či opakovanie mení zamýšľaný resource state inak.

Atlas `POST /v1/orders` používa `Idempotency-Key`. Server viaže key na tenant, operation a canonical request hash. Po nejasnom timeout-e môže klient request zopakovať a dostať pôvodný výsledok bez druhej objednávky.

## Status code a business result

Status code opisuje HTTP processing outcome. `2xx` signalizuje úspešné spracovanie podľa servera, `4xx` problém client requestu alebo policy a `5xx` server-side failure. Samotná trieda však nie je dostatočný oracle.

`202 Accepted` znamená prijatie na neskoršie spracovanie, nie dokončenú objednávku. `200 OK` môže obsahovať business field `status: rejected`. `503` môže byť retryable, ale iba v rámci deadline a idempotency contractu.

Error response má používať stabilný media type a machine-readable code:

```http
HTTP/1.1 409 Conflict
Content-Type: application/problem+json
Retry-After: 2
```

```json
{
  "type": "https://errors.atlas.example/order-version-conflict",
  "title": "Order version conflict",
  "status": 409,
  "instance": "req-7f31"
}
```

Client nemá parsovať náhodný ľudský text ako protocol.

## Headers a intermediaries

Headers môžu riadiť caching, conditional requests, content negotiation, authentication, tracing a forwarding. Proxy môže niektoré pridať, odstrániť alebo normalizovať. Security-sensitive headers sa nesmú slepo dôverovať od clienta.

`Connection` a ďalšie hop-by-hop headers patria konkrétnemu transportnému hopu. End-to-end metadata musia byť forwardované podľa HTTP pravidiel a proxy configuration. Nesprávne preposlanie môže viesť k request smuggling alebo cache confusion.

## Caching

Cache rozhoduje podľa method, status, request headers, response directives a cache key. `Cache-Control: private`, `no-store`, `max-age`, validators a `Vary` menia reuse semantics.

```http
ETag: "order-8421-v3"
Cache-Control: private, max-age=30
Vary: Accept-Encoding
```

Conditional GET s `If-None-Match` môže dostať `304 Not Modified`. Response nemá body; client použije uloženú representation. Cache hit dokazuje reuse cached response, nie čerstvý origin health.

Personalizovaný response uložený pod príliš širokým key môže spôsobiť cross-user data leak. Cache design je preto correctness a security contract, nie iba performance optimalizácia.

## Concurrency control

Client môže meniť resource iba ak pozná aktuálnu verziu:

```http
PATCH /v1/orders/ord-8421
If-Match: "order-8421-v3"
```

Ak sa resource zmenil, server vráti `412 Precondition Failed`. Bez precondition môže neskorší writer ticho prepísať novší state. Optimistic concurrency je aplikačný mechanizmus nad HTTP conditional semantics.

## HTTP/1.1, HTTP/2 a HTTP/3

HTTP/1.1 používa textové message framing nad TCP a môže využívať persistent connections. HTTP/2 používa binárne frames a multiplexované streams v jednom TCP spojení. HTTP/3 prenáša HTTP semantics cez QUIC nad UDP a oddelí transportné blocking medzi streams.

Multiplexing mení observation model. Jeden TCP alebo QUIC connection môže niesť mnoho requestov. Connection-level health preto nepreukazuje každý stream. Proxy a capture musia korelovať stream alebo request ID.

## Incident: `200 OK`, ale objednávka neexistuje

Po release-i API vracia `200` s JSON `{ "accepted": true }`, no worker queue publication zlyháva a objednávka sa nikdy nedostane do terminal state-u. Synthetic monitor kontroluje iba status code a hlási green.

Root cause nie je HTTP availability, ale slabý oracle. Contract sa zmení na `202` s operation resource a client sleduje stav, alebo synchronný path potvrdí durable commit. Monitoring overí business completion a audit identity. HTTP status zostáva súčasťou dôkazu, nie jeho náhradou.

## Zhrnutie

HTTP prenáša method, target, metadata a representations cez jeden alebo viac intermediaries. Method a status semantics musia byť spojené s aplikačným contractom, cachingom, idempotency a concurrency. Zelený protocol outcome sa uzatvára až business verification.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Load balancing](load-balancing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: HTTPS, TLS, certifikáty a PKI →](https-tls-certificates-pki.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
