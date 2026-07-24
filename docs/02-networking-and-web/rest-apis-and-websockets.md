# REST APIs a WebSockets

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [HTTP](http.md), [HTTPS, TLS, certificates a PKI](https-tls-certificates-pki.md), [Proxy a reverse proxy](proxy-and-reverse-proxy.md)
- Súvisiace témy: API design, idempotency, authentication, event-driven systems, streaming

## 1. Definícia

REST je architectural style pre distribuované hypermedia systémy. V praxi sa jeho princípy používajú na navrhovanie resource-oriented HTTP APIs s jednotným interfaceom, explicitnými representations, cache semantics a stateless request contractom.

WebSocket je samostatný protokol poskytujúci dlhodobý full-duplex message channel medzi klientom a serverom. Začína HTTP-based handshakeom, ale po úspešnom upgrade už nepoužíva bežný HTTP request-response model.

Tieto prístupy riešia odlišné komunikačné potreby:

- REST-like HTTP API — diskrétne operácie s jasným začiatkom, statusom a výsledkom;
- WebSocket — dlhodobá obojsmerná komunikácia, subscriptions, realtime events alebo interaktívne sessions.

Nie každé JSON API je RESTful a WebSocket automaticky neposkytuje business-level reliability.

## 2. Dva odlišné lifecycle modely

### Request-response API

```text
client vytvorí request
  ↓
server autentifikuje a autorizuje
  ↓
validuje preconditions a payload
  ↓
vykoná alebo naplánuje operáciu
  ↓
vráti status a representation
  ↓
request state sa uzavrie
```

### WebSocket

```text
HTTP/TLS handshake
  ↓
connection authentication
  ↓
dlhodobý message channel
  ↓ subscriptions, heartbeats, buffers
reconnect / close / draining
  ↓
state recovery alebo resume
```

REST-like API optimalizuje izolované operations. WebSocket vytvára dlhodobý distributed state medzi clientom, proxy, server instance a prípadným message backendom.

## 3. REST constraints

Klasické REST constraints:

### Client-server separation

Client rieši user interaction a presentation. Server vlastní resources a business rules. Oddelenie umožňuje meniť obe strany nezávisle, ak zostáva zachovaný contract.

### Stateless communication

Každý request obsahuje informácie potrebné na jeho spracovanie. Server nemá vyžadovať skrytý conversational state naviazaný na konkrétnu transportnú connection alebo poradie predchádzajúcich requests.

Stateless neznamená „bez databázy“ alebo „bez session“. Session môže existovať v cookie, token-e alebo central store. Podstatné je, že server vie request interpretovať z explicitného request contextu.

### Cacheability

Response musí mať definované cache semantics. Cache môže znížiť latency a server load, ale iba pri správnom cache key, validators a data-isolation policy.

### Uniform interface

Resources sa ovládajú konzistentnou kombináciou URI, HTTP methods, representations, status codes a hypermedia links. Klient nemusí poznať internú implementáciu každého resource.

### Layered system

Client nemusí vedieť, či komunikuje priamo s originom alebo cez CDN, gateway, proxy či cache. Každá vrstva však musí zachovať end-to-end contract a trust boundaries.

### Code on demand

Voliteľný constraint umožňuje serveru poslať executable code, napríklad JavaScript. Pri API návrhu zvyčajne nie je centrálnym mechanizmom.

## 4. Resource-oriented model

URI má pomenovať resource alebo kolekciu:

```text
/orders
/orders/42
/orders/42/items
/customers/18/addresses
```

Príklady operácií:

```text
GET    /orders/42
POST   /orders
PUT    /orders/42
PATCH  /orders/42
DELETE /orders/42
GET    /orders/42/items
```

Resource nemusí byť databázový riadok. Môže reprezentovať:

- business objekt;
- výsledok výpočtu;
- workflow;
- report;
- export;
- permission grant;
- reservation;
- command result.

Dobrý resource model oddeľuje public contract od internej tabuľkovej štruktúry.

## 5. Business actions ako resources

Nie každá operácia je prirodzený CRUD nad existujúcim objektom. Namiesto RPC-like endpointu:

```text
POST /orders/42/cancel
```

možno modelovať auditovateľný event alebo request:

```text
POST /orders/42/cancellations
POST /payments/42/refunds
POST /users/42/password-reset-requests
```

Výhody:

- operácia má vlastnú identity a stav;
- možno ju idempotentne opakovať;
- vzniká audit trail;
- možno vrátiť `201` alebo `202` a operation resource;
- failure a retry semantics sú explicitnejšie.

Action endpoint nie je automaticky zlý. Dôležité je, aby mal stabilný contract a nebol náhodným mapovaním internej function name.

## 6. Representations a media types

Resource môže mať viac representations:

```http
Accept: application/json
Accept: text/csv
```

Server odpovedá:

```http
Content-Type: application/json
```

Media type je súčasť contractu. Určuje syntax a často aj semantics.

Zmena typu poľa, významu enum hodnoty alebo nullability pri nezmenenom media type môže byť breaking change, hoci JSON zostáva syntakticky platný.

Pre špecializované errors možno použiť media type typu:

```text
application/problem+json
```

Pre versioning možno použiť vendor media types, ale zvyšujú tooling a negotiation complexity.

## 7. Method a status contract

### Create

```http
POST /orders
```

Úspešné vytvorenie:

```http
HTTP/1.1 201 Created
Location: /orders/42
Content-Type: application/json
```

`Location` pomáha klientovi identifikovať nový resource. Response body môže obsahovať jeho representation.

### Read

```http
GET /orders/42
```

- `200` s representation;
- `304` pri cache revalidation;
- `404`, ak resource nie je dostupný;
- `410`, ak contract explicitne rozlišuje permanentne odstránený resource.

### Replace/update

`PUT` nastavuje celý známy resource state. `PATCH` aplikuje čiastočnú zmenu podľa definovaného patch formátu.

### Delete

`DELETE` môže vrátiť:

- `204` po synchronickom odstránení;
- `202`, ak cleanup pokračuje asynchrónne;
- `404`, ak resource neexistuje podľa zvolenej semantics.

### Business conflict

`409 Conflict` opisuje konflikt s aktuálnym stavom, napríklad duplicate unique value alebo zakázaný state transition.

### Failed precondition

`412 Precondition Failed` je vhodný pri `If-Match` alebo inej HTTP precondition.

### Validation error

`422 Unprocessable Content` môže vyjadriť syntakticky správny payload, ktorý nespĺňa field alebo business pravidlá.

API nemá vracať `200` pre každú chybu iba preto, že body je JSON.

## 8. Idempotencia transportu verzus business operácie

Network timeout vytvára neistotu:

```text
request odoslaný
  ↓
server možno operáciu dokončil
  ↓
response sa stratila
  ↓
client nevie výsledok
```

Retry môže byť bezpečný iba ak:

- operácia je prirodzene idempotentná;
- server poskytuje deduplication;
- client vie zistiť výsledok podľa operation identity;
- alebo existuje dôkaz, že request nebol spracovaný.

Transportný timeout nie je dôkaz neúspechu business operácie.

## 9. Idempotency keys

Pre create/payment alebo inú ne-idempotentnú operáciu môže klient poslať:

```http
Idempotency-Key: 2de98f98-2ed2-4ea2-a76f-5158a7b0f3ae
```

Server musí atomicky evidovať:

```text
scope identity/tenant/operation
+ idempotency key
+ payload fingerprint
+ execution state
+ final status/body/reference
+ retention expiry
```

Možný lifecycle:

1. prvý request rezervuje key;
2. súbežný request s rovnakým key čaká alebo dostane „in progress“;
3. server vykoná business operáciu;
4. uloží canonical výsledok;
5. retry s rovnakým key a payloadom dostane rovnaký výsledok;
6. rovnaký key s iným payloadom dostane conflict.

Ak sa key uloží až po business zápise, dve súbežné requests môžu operáciu vykonať dvakrát. Deduplikačný zápis musí byť concurrency-safe a transakčne koordinovaný s účinkom.

## 10. Optimistic concurrency control

Server vráti version validator:

```http
ETag: "order-42-v7"
```

Client pri update pošle:

```http
If-Match: "order-42-v7"
```

Server vykoná zápis iba ak resource stále zodpovedá version 7. Inak:

```http
412 Precondition Failed
```

Tým sa predchádza lost update:

```text
A číta v7
B číta v7
A uloží v8
B sa pokúsi uložiť z v7 → odmietnuté
```

Precondition musí byť overená atomicky s write. Kontrola v application code pred samostatným databázovým updateom môže stále obsahovať race condition.

## 11. Partial updates a patch semantics

`PATCH` potrebuje presne definovaný formát.

JSON Merge Patch-like semantics:

```json
{
  "status": "paid",
  "note": null
}
```

môžu znamenať „nastav status“ a „odstráň note“.

JSON Patch-like semantics:

```json
[
  {"op":"replace","path":"/status","value":"paid"}
]
```

explicitne pomenúvajú operácie.

API musí definovať:

- rozdiel medzi absent, null a empty;
- povolené fields;
- atomicitu viacerých zmien;
- validation order;
- idempotency konkrétnych patch operations;
- conflict behavior.

## 12. Pagination ako consistency contract

Veľká kolekcia sa nemá vracať bez limitu. Pagination nie je iba performance parameter; určuje, čo klient uvidí pri súbežných zmenách.

### Offset pagination

```text
GET /orders?limit=50&offset=100
```

Výhody:

- jednoduchá implementácia a navigácia na konkrétnu stranu;
- vhodná pre malé alebo stabilné datasety.

Nevýhody:

- insert/delete pred offsetom spôsobí duplicate alebo missing records;
- veľký offset môže byť databázovo drahý;
- ordering musí byť explicitný.

### Cursor pagination

```text
GET /orders?limit=50&after=eyJjcmVhdGVkX2F0IjoiLi4uIiwiaWQiOjQyfQ
```

Cursor reprezentuje pozíciu v stabilnom ordering-u. Má byť:

- opaque pre clienta;
- podpísaný alebo validovaný proti manipulácii;
- viazaný na filter/sort context;
- časovo alebo version-aware podľa potreby.

### Snapshot pagination

Pri exporte alebo audite môže API vytvoriť snapshot identity, aby všetky pages reprezentovali jeden konzistentný dataset. Je to drahšie, ale odstraňuje ambiguity live pagination.

## 13. Deterministic ordering

Pagination potrebuje úplné stabilné poradie.

```text
ORDER BY created_at
```

nie je deterministické, ak viac records má rovnaký timestamp. Doplň tie-breaker:

```text
ORDER BY created_at, id
```

Cursor musí obsahovať všetky ordering keys. Inak records na hranici page môžu byť preskočené alebo duplikované.

## 14. Filtering, sorting a field selection

```text
GET /orders?status=pending&sort=-created_at&fields=id,status,total
```

Každá dynamická query dimenzia potrebuje:

- allowlist fields a operators;
- type validation;
- cost limit;
- bezpečné mapovanie na query engine;
- index/capacity model;
- maximum result window;
- authorization aplikovanú pred alebo počas query;
- ochranu pred vysokou metric cardinality.

Neprenášaj raw query syntax priamo do SQL, Elasticsearch alebo expression engine.

## 15. Error contract

Konzistentná error response môže používať problem details model:

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

Dobrý error contract oddeľuje:

- machine-readable stable code;
- user-safe message;
- correlation ID;
- field-level details;
- retryability;
- documentation reference.

Nesmie odhaľovať:

- stack trace;
- SQL alebo interné queries;
- filesystem paths;
- credentials a tokens;
- interné hostnames;
- security-policy detail, ktorý umožní enumeration.

## 16. Authentication, authorization a tenancy

Authentication určí identity. Authorization rozhodne, či identity smie vykonať konkrétnu operáciu nad konkrétnym resource.

Kontroly:

- endpoint-level permission;
- object-level permission;
- field-level permission;
- tenant isolation;
- state-transition permission;
- delegated scopes;
- rate-limit identity.

Častý failure je IDOR/BOLA: client zmení `/orders/42` na `/orders/43` a server overí iba „user je prihlásený“, nie ownership resource.

Authorization sa musí vyhodnocovať server-side pri každom prístupe. Skryté buttony alebo nepredvídateľné IDs nie sú control.

## 17. Rate limits, quotas a load shedding

Rate limit obmedzuje frekvenciu requests. Quota obmedzuje použitie počas dlhšieho obdobia alebo počet resources.

Dimenzie:

- identity;
- tenant;
- API key;
- source IP;
- endpoint;
- operation cost;
- concurrent requests;
- data volume.

Response:

```http
429 Too Many Requests
Retry-After: 30
```

Limiter potrebuje definovať:

- algorithm a window;
- distributed state consistency;
- burst allowance;
- fail-open/fail-closed behavior;
- priority traffic;
- exemptions;
- retry guidance.

Rate limiting nie je úplná DDoS ochrana. Musí byť umiestnený dostatočne skoro, aby drahý request nevyčerpal resources pred rozhodnutím.

## 18. Asynchronous operations

Dlhá operácia nemá držať HTTP connection neobmedzene.

Request:

```http
POST /exports
```

Response:

```http
202 Accepted
Location: /operations/abc123
Retry-After: 5
```

Operation resource:

```json
{
  "id": "abc123",
  "state": "running",
  "progress": 0.45,
  "created_at": "...",
  "result": null,
  "error": null
}
```

Lifecycle:

```text
pending → running → succeeded
                  ↘ failed
                  ↘ cancelled
```

Contract má definovať:

- status transitions;
- cancellation semantics;
- progress accuracy;
- result location;
- error model;
- retention;
- idempotency;
- retry a duplicate scheduling;
- notification alebo polling.

`202` znamená prijatie, nie dokončenie.

## 19. API versioning

Versioning je iba technika identifikácie contract generation. Nenahrádza compatibility policy.

Možnosti:

- URI: `/v1/orders`;
- media type alebo `Accept` parameter;
- custom header;
- postupná backward-compatible evolution bez explicitnej major version.

Každý model má trade-offy pre caching, routing, documentation a client libraries.

Potrebný lifecycle:

1. publish contract a changelog;
2. označ deprecated fields/endpoints;
3. poskytnúť migration path;
4. merať active clients;
5. komunikovať sunset date;
6. testovať compatibility;
7. odstrániť starú version až po overení adoption.

## 20. Backward-compatible evolution

Typicky bezpečnejšie zmeny:

- nový optional response field;
- nový endpoint;
- nový optional request parameter;
- rozšírenie capability s explicitným defaultom.

Potenciálne breaking zmeny:

- odstránenie alebo rename field;
- zmena type alebo meaning;
- zmena required/optional;
- sprísnenie validation;
- zmena pagination ordering;
- zmena default behavior;
- pridanie enum hodnoty, ak klient používa exhaustive switch;
- zmena status code, ktorý klient interpretuje špeciálne.

Robustný klient má tolerovať neznáme response fields. Nemá však automaticky ignorovať neznáme security-sensitive enum hodnoty alebo state transitions.

## 21. Schema a contract testing

OpenAPI alebo iná schema môže definovať paths, payloads, statusy a types. Schema sama negarantuje runtime compatibility.

Použi:

- producer tests;
- consumer-driven contract tests;
- backward-compatibility diff;
- example validation;
- negative tests;
- authz tests;
- idempotency/concurrency tests;
- pagination consistency tests;
- fuzzing parserov a boundary values.

Dokumentácia, gateway validation a server implementation musia vychádzať z rovnakého source of truth alebo byť pravidelne porovnávané.

## 22. WebSocket handshake

Pri HTTP/1.1 klient pošle upgrade request:

```http
GET /socket HTTP/1.1
Host: realtime.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: <random-base64>
Sec-WebSocket-Version: 13
Origin: https://app.example
```

Server odpovie:

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: <derived-value>
```

Handshake overí, že obe strany súhlasia s prechodom protokolu a chráni proti niektorým cross-protocol confusions. `Sec-WebSocket-Accept` nie je authentication.

Pre HTTP/2 existuje extended CONNECT model; proxy a client support musia byť kompatibilné.

## 23. WebSocket origin a authentication

Browser pri WebSocket handshake typicky posiela `Origin`. Server má validovať povolené origins, pretože browserové cookies alebo credentials môžu byť automaticky použité.

Authentication možnosti:

- session cookie;
- bearer token v podporovanom handshake mechanizme;
- short-lived connection ticket získaný cez HTTPS API;
- mTLS;
- prvá aplikačná authentication message.

Token v query stringu môže skončiť v access logoch, browser history alebo telemetry. Preferuj krátko žijúci opaque ticket a redaction.

Authentication pri otvorení connection nestačí pre nekonečnú session. Potrebný je model pre:

- token expiry;
- permission zmenu;
- revocation;
- tenant switch;
- reauthentication;
- forced disconnect.

## 24. WebSocket framing

WebSocket prenáša frames, ktoré sa skladajú do messages.

Typy:

- text frames s UTF-8 payloadom;
- binary frames;
- continuation frames;
- ping;
- pong;
- close.

Client-to-server frames sú maskované podľa protokolu. Masking nie je encryption; TLS poskytuje dôvernosť.

Message môže byť fragmentovaná do viacerých frames. Aplikačný parser nesmie predpokladať, že jeden network read zodpovedá jednej message.

## 25. Aplikačný message protocol

WebSocket definuje channel a framing, nie business semantics.

Aplikačný protocol musí definovať napríklad:

```json
{
  "type": "subscribe",
  "id": "req-123",
  "topic": "orders:42",
  "version": 1,
  "payload": {}
}
```

Potrebné rozhodnutia:

- schema a versioning;
- message type registry;
- correlation IDs;
- request-response alebo event semantics;
- ordering scope;
- acknowledgements;
- duplicate handling;
- error messages;
- authorization per subscription/message;
- maximum message size;
- compression policy;
- close codes;
- resume checkpoint.

Bez tohto contractu je WebSocket iba nedefinovaný bidirectional byte/message channel.

## 26. Delivery semantics

WebSocket cez TCP poskytuje ordered transport bytes počas živej connection. Negarantuje:

- že server business message spracoval;
- že response bola persistovaná;
- že event prežije reconnect;
- exactly-once delivery;
- durable subscription;
- duplicate suppression po retry.

Aplikačný protocol môže implementovať:

### At-most-once

Message sa neposiela znova. Môže sa stratiť, ale nevznikne retry duplicate.

### At-least-once

Sender opakuje message, kým nedostane acknowledgement. Receiver musí deduplikovať.

### Effectively-once

Business effect je deduplikovaný transakčne pomocou message ID alebo operation key. Samotný transport exactly-once neposkytuje.

## 27. Ordering

Jedna WebSocket connection zachová transportné poradie messages. Global business ordering však nemusí existovať, ak:

- viac server instances publishuje events;
- backend používa partitioned broker;
- client reconnectne na inú instance;
- subscriptions sa obnovujú paralelne;
- messages sa retryujú.

Definuj ordering scope:

```text
per connection
per topic
per resource
per tenant
per partition key
```

Použi sequence number alebo version, aby client vedel odhaliť gap a spustiť resync.

## 28. Connection state a server architecture

Dlhodobá connection môže držať:

- authenticated identity;
- subscriptions;
- last acknowledged sequence;
- outbound queue;
- rate-limit counters;
- presence;
- compression context;
- protocol version;
- connection metadata.

Ak je state iba v memory jednej instance, load balancer potrebuje affinity alebo reconnect recovery. Lepší scalable model často externalizuje durable subscription/event state, ale ephemeral socket state stále zostáva na konkrétnej instance.

## 29. Heartbeats a dead-peer detection

TCP connection môže zostať z pohľadu procesu otvorená aj po strate network pathu, kým neprebehne write, retransmission timeout alebo keepalive.

WebSocket ping/pong umožňuje rýchlejšiu protocol-level liveness kontrolu.

Heartbeat policy definuje:

- interval;
- timeout;
- počet missed replies;
- kto iniciuje ping;
- či pong obsahuje correlation payload;
- reakciu na event-loop lag;
- interakciu s proxy/LB idle timeoutom.

Interval musí byť kratší než najkratší middlebox idle timeout, ale nie tak krátky, aby heartbeat load dominoval pri veľkom počte connections.

TCP keepalive a WebSocket heartbeat sledujú inú vrstvu a môžu mať rozdielne časy.

## 30. Backpressure

Ak producer generuje dáta rýchlejšie než client prijíma:

```text
producer rate > network/consumer rate
  ↓
outbound queue rastie
  ↓
memory rastie a latency starne
  ↓
instance môže zlyhať
```

Backpressure policy musí byť explicitná:

- bounded per-connection queue;
- bounded per-tenant aggregate;
- drop newest;
- drop oldest;
- coalescing, napríklad poslať iba najnovší stav;
- sampling;
- disconnect slow consumer;
- application credit/window;
- acknowledgment-based pacing;
- presun durable events do brokeru a klientský pull/resume.

Neobmedzený buffer nie je stratégia. Iba odkladá incident a zväčšuje blast radius.

## 31. Inbound pressure a abuse

Klient môže posielať messages príliš rýchlo alebo príliš veľké payloady.

Kontroly:

- maximum frame a message size;
- maximum decompressed size;
- message rate limit;
- concurrent subscriptions;
- validation pred drahou operáciou;
- per-message authorization;
- CPU/JSON parse limit;
- compression-bomb ochrana;
- idle a unauthenticated handshake timeout;
- maximum connection duration podľa potreby.

Connection-level authentication nie je povolenie vykonať ľubovoľnú message.

## 32. Reconnect lifecycle

Disconnect môže nastať bez clean close handshakeu. Client potrebuje reconnect policy:

```text
connection lost
  ↓
wait backoff + jitter
  ↓
re-resolve endpoint
  ↓
new TLS/WebSocket handshake
  ↓
reauthenticate
  ↓
restore subscriptions
  ↓
resume from checkpoint alebo full resync
```

Backoff chráni server pred reconnect stormom. Jitter zabráni synchronizovanému návratu tisícov clients.

Client musí rozlišovať:

- transient network failure;
- authentication failure;
- incompatible protocol version;
- server overload;
- permanent authorization deny;
- graceful migration request.

Nekonečný okamžitý retry môže zmeniť lokálny outage na fleet-wide incident.

## 33. Resume a gap recovery

Ak client potrebuje event continuity, každá event message môže mať sequence alebo cursor:

```json
{
  "type": "order.updated",
  "sequence": 1042,
  "resource_version": 7,
  "payload": {}
}
```

Po reconnecte client pošle posledný potvrdený checkpoint. Server:

- replayne chýbajúce events;
- alebo oznámi, že retention už nestačí a client musí načítať snapshot cez REST API.

Robustný model často kombinuje:

```text
REST snapshot
+ WebSocket incremental events
+ sequence gap detection
```

WebSocket sám neposkytuje durable replay log.

## 34. Close handshake a close codes

Jedna strana pošle close frame s code a voliteľným reason. Druhá strana odpovie close frameom a transport sa uzavrie.

Close code môže rozlíšiť:

- normal shutdown;
- protocol error;
- invalid payload;
- policy violation;
- message too large;
- internal error;
- service restart podľa application-defined rozsahu.

Network loss alebo process crash nemusia vytvoriť close frame. Observability preto musí rozlíšiť clean close, reset, timeout a silent disappearance.

## 35. Deployment a draining

Pri deploymente alebo scale-in:

1. instance prestane byť ready pre nové connections;
2. load balancer ju odstráni z nového trafficu;
3. server môže poslať migration/reconnect signal;
4. existujúce connections dostanú grace period;
5. subscriptions a checkpoints sa zachovajú alebo obnovia;
6. po deadline sa zvyšné connections ukončia;
7. client reconnectne s backoff/jitter.

Ak process skončí okamžite, tisíce clients môžu naraz reconnectovať a preťažiť nové instances.

Pre veľmi dlhé connections môže byť potrebná maximálna connection lifetime s randomizovaným renewal oknom, aby sa fleet prirodzene rozložil.

## 36. WebSocket cez proxy a load balancer

Proxy/LB musí podporovať handshake a následný tunnel/stream lifecycle.

Kontroluj:

- upgrade alebo extended CONNECT podporu;
- HTTP version conversion;
- TLS termination;
- idle timeout;
- maximum connection duration;
- connection count limits;
- per-connection buffer;
- compression;
- affinity;
- readiness a draining;
- source identity;
- observability po upgrade.

L7 proxy môže zaznamenať handshake ako jeden `101`, ale nevidieť jednotlivé application messages v štandardných HTTP metrics.

## 37. WebSocket compression

Extension `permessage-deflate` môže znížiť bandwidth, ale prináša:

- CPU overhead;
- memory per connection;
- context takeover state;
- compression bomb risk;
- side-channel riziká pri secrets;
- odlišnú podporu klientov a proxy.

Limit sa má aplikovať na decompressed message size, nie iba wire bytes.

## 38. WebSocket verzus SSE verzus polling

### WebSocket

- full-duplex;
- binary aj text;
- vlastný message protocol;
- dlhodobý state a reconnect complexity.

Vhodný pre interaktívnu obojsmernú komunikáciu, multiplayer state, collaboration alebo vysokofrekvenčné commands/events.

### Server-Sent Events

- server → browser stream;
- text event model;
- beží nad HTTP;
- browser podporuje automatic reconnect a last event ID;
- jednoduchší proxy a auth model než WebSocket v niektorých prostrediach.

Vhodný pre notifications, progress alebo event feed bez potreby obojsmerného channelu.

### Long polling

Client odošle request, server čaká na event alebo timeout a client request zopakuje.

Výhody sú jednoduchá compatibility a bežný HTTP observability model. Nevýhody sú request overhead a reconnect latency.

### Short polling

Client pravidelne číta stav. Je najjednoduchší, ale môže byť neefektívny alebo pomalý podľa intervalu.

Výber závisí od directionality, delivery semantics, frequency, scale, proxy support, mobile power use a recovery modelu.

## 39. Kombinovaný REST + WebSocket návrh

Praktický systém často používa oba mechanizmy:

```text
REST:
- create/update commands
- initial snapshot
- history
- recovery po gap-e

WebSocket:
- realtime notifications
- incremental changes
- presence
- low-latency interactive messages
```

Command cez REST môže vrátiť operation ID. Výsledný state change sa objaví cez WebSocket event s rovnakou correlation identity.

Klient nesmie predpokladať, že event príde presne raz alebo pred HTTP response. Potrebuje deduplication a authoritative state reconciliation.

## 40. Observability REST API

Sleduj:

- request rate podľa normalized route a method;
- latency percentily a queue time;
- status podľa originu;
- payload sizes;
- authn/authz failures;
- rate-limit decisions;
- idempotency hits, conflicts a in-progress collisions;
- optimistic-concurrency failures;
- pagination mode a page size;
- expensive query shapes;
- async operation duration a failure;
- version/client usage;
- retries a duplicate side effects.

## 41. Observability WebSocket

Sleduj:

- handshake attempts a failures;
- active connections podľa instance/tenant/version;
- connection duration;
- clean versus abnormal close;
- reconnect rate;
- messages a bytes in/out;
- per-connection queue depth;
- dropped/coalesced messages;
- slow-consumer disconnects;
- ping latency a missed pong;
- auth expiry/revocation disconnects;
- subscription count;
- sequence gaps a replay volume;
- drain duration;
- compression ratio a CPU cost.

Metriky nesmú používať raw connection ID, user ID alebo topic s neobmedzenou cardinality ako label.

## 42. Diagnostika REST timeoutu

Request na vytvorenie payment timeoutoval:

1. nájdi request ID a idempotency key;
2. zisti, či edge/proxy request prijali;
3. over, či origin začal spracovanie;
4. skontroluj database/event side effect;
5. over, či response vznikla a kde sa stratila;
6. porovnaj client, proxy a server timeout budget;
7. skontroluj retry na každej vrstve;
8. request opakuj iba s rovnakým idempotency key;
9. over canonical operation result;
10. po náprave testuj duplicate concurrency.

## 43. Diagnostika inconsistent pagination

Client vidí duplicate alebo missing records:

1. zaznamenaj filter, sort a cursor/offset;
2. over deterministic ordering;
3. zisti, či dataset sa medzi pages menil;
4. dekóduj cursor iba v kontrolovanom debug nástroji;
5. over tie-breaker;
6. skontroluj authorization filtering;
7. porovnaj snapshot versus live semantics;
8. testuj inserts/deletes na page boundary.

## 44. Diagnostika WebSocket disconnectu

1. zaznamenaj timestamp, connection ID a close code;
2. urč initiator: client, proxy, server alebo network timeout;
3. porovnaj interval s LB/proxy idle timeoutom;
4. over ping/pong a event-loop latency;
5. skontroluj token expiry a authorization revocation;
6. sleduj outbound queue a slow-consumer stav;
7. porovnaj deployment/draining timeline;
8. over maximum connection duration;
9. sleduj reconnect backoff a storm;
10. po reconnecte over subscription restore a sequence gap.

## 45. Typické failure patterns

### Duplicate create po timeout-e

Chýba idempotency alebo nie je atomicky koordinovaná s business write.

### `412 Precondition Failed`

Client mení stale version. Má znovu načítať aktuálny resource, zlúčiť zmenu alebo konflikt ukázať používateľovi; nemá slepo odstrániť `If-Match`.

### Cursor prestane fungovať po zmene filtra

Cursor nebol viazaný na query context alebo server zmenil ordering/encoding bez compatibility policy.

### Každý client môže čítať cudzie resources

Chýba object-level authorization alebo tenant filter.

### WebSocket sa odpája pravidelne po rovnakom čase

Pravdepodobný idle timeout, maximum lifetime alebo token expiry. Periodicita je silný diagnostický signál.

### Memory rastie s počtom pomalých clients

Outbound queues nie sú bounded alebo drop/disconnect policy sa neuplatňuje.

### Po deploymente vznikne reconnect storm

Chýba draining, jitter alebo connection lifetime rozloženie.

### Client po reconnecte vidí neaktuálny stav

Subscriptions sa obnovili bez replay/checkpointu alebo client neuskutočnil snapshot reconciliation.

## 46. Časté omyly

### „REST znamená JSON cez HTTP“

Nie. REST je architectural style a uniform interface. JSON je iba representation format.

### „Stateless znamená bez persistent state“

Nie. Znamená, že každý request má explicitný processing context a server nespolieha na skrytú conversation naviazanú na connection.

### „POST sa po timeout-e môže bezpečne zopakovať“

Nie bez idempotency, deduplication alebo dôkazu, že operácia neprebehla.

### „ETag je iba cache header“

Nie. `If-Match` ho môže použiť na optimistic concurrency control.

### „WebSocket garantuje doručenie business message“

Nie. Poskytuje transportný message channel počas živej connection. Acknowledgement, durability a deduplication musí definovať application protocol.

### „Jedna WebSocket connection znamená globálne ordering“

Nie po reconnecte, pri multi-instance publish alebo partitioned backend-e.

### „Dlhá connection nepotrebuje deployment lifecycle“

Potrebuje readiness, draining, reconnect a state recovery.

## 47. Praktický checklist

REST/API:

- resource model a method semantics;
- explicitné status codes;
- idempotency a duplicate concurrency;
- optimistic concurrency;
- deterministic pagination;
- error contract;
- object/tenant authorization;
- rate a cost limits;
- async operation lifecycle;
- compatibility a deprecation;
- contract tests a observability.

WebSocket:

- origin a authentication policy;
- message schema/version;
- delivery a ordering scope;
- bounded buffers a backpressure;
- heartbeat a middlebox timeout;
- token refresh/revocation;
- reconnect backoff/jitter;
- resume/checkpoint model;
- proxy/LB support;
- close codes a diagnostics;
- draining a reconnect-storm protection.

## 48. Kontrolné otázky

1. Aké hlavné constraints definuje REST?
2. Aký je rozdiel medzi stateless request contractom a absenciou serverového state?
3. Kedy je vhodné modelovať business action ako nový resource?
4. Ako musí server atomicky implementovať idempotency key?
5. Načo slúži `If-Match` a prečo musí byť check transakčný?
6. Aký je rozdiel medzi offset, cursor a snapshot pagination?
7. Prečo cursor potrebuje deterministic ordering a tie-breaker?
8. Ktoré zmeny API sú potenciálne breaking aj bez zmeny URL?
9. Čo presne sa stane pri WebSocket handshake?
10. Prečo WebSocket potrebuje vlastný application protocol?
11. Aký je rozdiel medzi transport orderingom a business orderingom?
12. Ako navrhneš backpressure pre pomalého klienta?
13. Ako client obnoví stav po reconnecte a event gap-e?
14. Prečo deployment bez drainingu spôsobuje reconnect storm?
15. Kedy zvoliť WebSocket, SSE alebo polling?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: HTTPS, TLS, certificates a PKI](https-tls-certificates-pki.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Network troubleshooting →](network-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->