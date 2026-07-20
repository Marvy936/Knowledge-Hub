# REST APIs a WebSockets

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [HTTP](http.md), [HTTPS, TLS, certificates a PKI](https-tls-certificates-pki.md), [Proxy a reverse proxy](proxy-and-reverse-proxy.md)
- Súvisiace témy: API design, idempotency, authentication, event-driven systems, streaming

## 1. Definícia

REST je architectural style pre distributed hypermedia systems. WebSocket je protokol poskytujúci dlhodobý full-duplex message channel medzi klientom a serverom.

Nie každé HTTP JSON API je automaticky RESTful a WebSocket nie je náhradou za všetky request-response API.

## 2. REST constraints

Klasické REST constraints:

- client-server separation,
- stateless communication,
- cacheability,
- uniform interface,
- layered system,
- voliteľne code-on-demand.

Najdôležitejšia praktická myšlienka je uniform interface nad resources a representations, nie mapping každej business funkcie na náhodný endpoint.

## 3. Resource-oriented design

Príklady:

```text
GET    /orders/42
POST   /orders
PATCH  /orders/42
DELETE /orders/42
GET    /orders/42/items
```

URI má reprezentovať resource alebo collection. Action endpoints môžu byť primerané pre operácie, ktoré sa nedajú prirodzene modelovať ako CRUD:

```text
POST /orders/42/cancellations
POST /payments/42/refunds
```

Takýto model často lepšie zachytáva auditovateľný business event než `/orders/42/cancel`.

## 4. Statelessness

Každý request má obsahovať informácie potrebné na jeho spracovanie. Server nemá spoliehať na skrytý conversational state konkrétneho frontend connectionu.

Stateless neznamená, že server nemá databázu alebo sessions. Znamená, že request processing contract nie je závislý od neviditeľného poradia predchádzajúcich requests.

## 5. Representations

Resource môže mať viac representations:

```http
Accept: application/json
Accept: application/xml
```

Response má explicitne uviesť media type:

```http
Content-Type: application/json
```

Media type je súčasť contractu. Zmena významu polí pri nezmenenom media type môže byť breaking change.

## 6. Status codes a API semantics

Príklady:

- `200 OK` — úspešné čítanie alebo operácia s body,
- `201 Created` — nový resource, ideálne s `Location`,
- `202 Accepted` — asynchrónne prijatá práca ešte nie je dokončená,
- `204 No Content` — úspech bez body,
- `400 Bad Request` — syntakticky alebo všeobecne neplatný request,
- `401 Unauthorized` — chýbajúca/neplatná authentication,
- `403 Forbidden` — operation nie je povolená,
- `404 Not Found`,
- `409 Conflict`,
- `412 Precondition Failed`,
- `422 Unprocessable Content` — syntakticky platný, ale semanticky neplatný request,
- `429 Too Many Requests`.

API nemá vracať `200` pre každú chybu iba preto, že response obsahuje JSON.

## 7. Idempotency

Network timeout nevie klientovi povedať, či server request spracoval.

Pre ne-idempotentnú create/payment operáciu možno použiť:

```http
Idempotency-Key: 2de98f98-...
```

Server eviduje key, operation scope a výsledok. Opakovaný request s rovnakým key vráti pôvodný výsledok alebo konzistentný conflict.

Key musí mať:

- definovaný scope,
- retention period,
- ochranu pred reuse s iným payloadom,
- concurrency-safe zápis.

## 8. Optimistic concurrency

ETag alebo explicitná version:

```http
ETag: "version-7"
If-Match: "version-7"
```

Ak medzičasom resource zmenil iný klient:

```http
412 Precondition Failed
```

To zabraňuje lost update bez globálneho locku.

## 9. Pagination

### Offset pagination

```text
GET /orders?limit=50&offset=100
```

Jednoduchá, ale pri meniacich sa dátach môže preskakovať alebo duplikovať records a pri veľkom offsete byť drahá.

### Cursor pagination

```text
GET /orders?limit=50&after=eyJpZCI6...
```

Cursor reprezentuje stabilnú pozíciu podľa ordering key. Je vhodnejší pre veľké a meniace sa datasety.

API musí definovať deterministic ordering.

## 10. Filtering, sorting a field selection

Príklady:

```text
GET /orders?status=pending&sort=-created_at
GET /orders?fields=id,status,total
```

Dynamické query parametre potrebujú:

- allowlist polí,
- input validation,
- query cost limits,
- bezpečné mapovanie na databázu,
- ochranu pred neobmedzenou cardinality a expensive queries.

## 11. Error model

Konzistentná error response:

```json
{
  "type": "https://errors.example/validation",
  "title": "Validation failed",
  "status": 422,
  "detail": "Two fields are invalid",
  "instance": "/requests/abc123",
  "errors": [
    {"field": "email", "code": "invalid_format"}
  ]
}
```

Error response nemá odhaľovať stack traces, SQL, secrets ani interné topology detaily.

## 12. API versioning

Možnosti:

- URI versioning: `/v1/orders`,
- header/media type versioning,
- backward-compatible evolution bez explicitnej version pri aditívnych zmenách.

Versioning nezastupuje compatibility policy. Potrebné sú:

- deprecation notice,
- migration window,
- telemetry používania,
- sunset policy,
- contract tests.

## 13. Backward compatibility

Typicky bezpečnejšie zmeny:

- pridať optional response field,
- pridať nový endpoint,
- rozšíriť enum iba ak klienti tolerujú neznáme hodnoty.

Rizikové zmeny:

- premenovať/odstrániť field,
- zmeniť type alebo semantics,
- sprísniť validation,
- meniť ordering,
- zmeniť default behavior.

Klienti majú ignorovať neznáme response fields, ale nesmú slepo ignorovať neznáme security-relevant values.

## 14. Authentication a authorization

API môže používať:

- session cookies,
- bearer tokens,
- OAuth 2.x/OIDC flows,
- mTLS identities,
- signed requests.

Authentication určí identity. Authorization rozhodne, či identity môže vykonať konkrétnu operáciu nad konkrétnym resource.

Object-level authorization musí byť kontrolovaná pri každom resource access; nepostačuje skryť ID vo frontend-e.

## 15. Rate limiting a quotas

Limity môžu byť podľa:

- identity,
- API key,
- tenant,
- source IP,
- endpointu,
- operation cost.

Response:

```http
429 Too Many Requests
Retry-After: 30
```

Rate limiting chráni kapacitu, ale nie je úplná DDoS ochrana. Distributed limiter potrebuje konzistentný alebo približný state model.

## 16. Async operations

Dlhá operácia môže vrátiť:

```http
202 Accepted
Location: /operations/abc123
```

Klient sleduje operation resource:

```text
GET /operations/abc123
```

Operation má mať stav, progress, výsledok, error a retention semantics.

## 17. WebSocket handshake

WebSocket začína HTTP upgrade requestom:

```http
GET /socket HTTP/1.1
Host: example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: ...
Sec-WebSocket-Version: 13
```

Server odpovie:

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: ...
```

Po upgrade už connection používa WebSocket framing, nie bežné HTTP request-response messages.

## 18. WebSocket message model

WebSocket poskytuje:

- text a binary messages,
- fragmentation,
- ping/pong control frames,
- close handshake,
- full-duplex komunikáciu.

Aplikačný protokol nad WebSocket musí definovať:

- message schema,
- correlation IDs,
- ordering,
- acknowledgements,
- retries,
- authentication refresh,
- error a close semantics.

## 19. WebSocket connection lifecycle

Dlhodobý connection prináša state:

- prihlásená identity,
- subscriptions,
- server-side buffers,
- presence,
- routing na konkrétnu instance.

Pri deploymente alebo scale-in treba:

- prestať prijímať nové connections,
- oznámiť reconnect,
- drainovať existujúce connections,
- mať reconnect s backoff a jitter,
- obnoviť subscriptions idempotentne.

## 20. Heartbeats

Ping/pong alebo aplikačné heartbeat messages odhaľujú dead connections a udržiavajú state v middleboxes.

Interval musí byť kratší než relevantný idle timeout, ale nie tak krátky, aby vytváral zbytočný load.

TCP keepalive a WebSocket heartbeat riešia odlišné vrstvy a nemusia mať rovnaký failure detection čas.

## 21. Backpressure

Ak producer posiela rýchlejšie než consumer spracúva:

```text
producer rate > consumer rate → buffer rastie → memory/latency incident
```

Možnosti:

- bounded queue,
- drop policy,
- sampling/coalescing,
- per-client rate limit,
- disconnect pomalého klienta,
- application acknowledgements,
- flow-control protocol.

Neobmedzený buffer nie je backpressure stratégia.

## 22. WebSocket cez proxy a load balancer

Proxy musí podporovať upgrade alebo príslušný extended CONNECT model.

Kontroluj:

- idle timeout,
- connection duration limit,
- buffering,
- sticky routing alebo shared subscription state,
- max connections,
- TLS termination,
- health a draining.

L7 request metrics nemusia po upgrade zachytiť jednotlivé aplikačné messages.

## 23. WebSocket vs. SSE vs. polling

### WebSocket

Full-duplex, vhodný pre interaktívnu obojsmernú komunikáciu.

### Server-Sent Events

Server → browser stream nad HTTP, automatický reconnect a text event model.

### Long/short polling

Jednoduchší compatibility model, ale vyšší request overhead a latency trade-off.

Výber závisí od directionality, scale, proxies, delivery semantics a client support.

## 24. Observability

REST API:

- request rate, latency a status,
- operation cost,
- auth failures,
- rate-limit decisions,
- idempotency hits/conflicts,
- pagination a query shape,
- version usage.

WebSocket:

- active connections,
- connection duration,
- reconnect rate,
- messages/bytes in/out,
- queue depth a dropped messages,
- ping latency,
- close codes,
- connections per instance/tenant.

## 25. Diagnostický postup

REST request timeout:

1. koreluj idempotency/request ID,
2. zisti, či server operáciu spracoval,
3. skontroluj proxy timeout a retry,
4. over downstream dependencies,
5. opakuj iba podľa operation semantics.

WebSocket sa odpája:

1. zaznamenaj close code a initiator,
2. porovnaj interval s proxy/LB idle timeoutom,
3. over ping/pong,
4. skontroluj deployment/draining,
5. sleduj buffer a slow consumer,
6. over auth token expiry,
7. testuj reconnect/backoff.

## 26. Časté omyly

### „REST znamená JSON cez HTTP“

Nie. REST je architectural style s constraints.

### „Stateless znamená bez databázy“

Nie. Týka sa request contextu, nie absencie persistent state.

### „POST sa po timeout-e môže bezpečne zopakovať“

Nie bez idempotency alebo dôkazu, že operácia neprebehla.

### „WebSocket garantuje doručenie business message“

Transportný connection neposkytuje aplikačné acknowledgement alebo deduplication automaticky.

### „Dlhý connection nepotrebuje deployment lifecycle“

Potrebuje draining, reconnect a state recovery.

## 27. Kontrolné otázky

1. Aké sú hlavné REST constraints?
2. Aký je rozdiel medzi resource a action endpointom?
3. Ako idempotency key rieši nejasný timeout?
4. Načo slúži `If-Match`?
5. Aký je rozdiel medzi offset a cursor pagination?
6. Ako navrhneš backward-compatible API zmenu?
7. Čo sa deje pri WebSocket handshake?
8. Prečo WebSocket potrebuje vlastný message protocol?
9. Ako riešiš backpressure pri pomalom klientovi?
10. Kedy zvoliť WebSocket, SSE alebo polling?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: HTTPS, TLS, certificates a PKI](https-tls-certificates-pki.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Network troubleshooting →](network-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
