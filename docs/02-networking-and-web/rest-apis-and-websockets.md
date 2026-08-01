# REST API a WebSockety

HTTP poskytuje transportné semantics pre aplikačné messages. REST API pridáva resource-oriented contract a WebSocket vytvára dlhodobý obojsmerný channel. Obe riešenia používajú sieťový path z predchádzajúcich kapitol, ale majú odlišný state, retry, scaling a observability model.

## Resource-oriented API

Atlas modeluje objednávku ako resource:

```http
POST /v1/orders
GET /v1/orders/ord-8421
PATCH /v1/orders/ord-8421
```

URI pomenúva resource alebo kolekciu; method vyjadruje zamýšľanú operáciu. Contract zahŕňa schemas, authorization, state transitions, error model, idempotency, concurrency a version lifecycle. „REST“ nie je synonymum pre JSON cez HTTP.

Create request môže vrátiť `201 Created` a `Location`, alebo `202 Accepted`, ak processing pokračuje asynchrónne. Výber má odrážať durable business state, nie preferenciu frameworku.

## Idempotency a unknown outcome

Po client timeout-e nie je známe, či server request nespracoval alebo iba stratil response. Atlas používa:

```http
Idempotency-Key: op-8421
```

Server uloží operation record spolu s canonical request hashom. Rovnaký key a rovnaký request vráti pôvodný výsledok; rovnaký key s iným payloadom je konflikt. Deduplication scope zahŕňa tenant a operation type, aby sa keys medzi users nezrazili.

Idempotency key nie je retry counter. Musí prežiť všetky backends a mať retention dlhšiu než maximum retry window.

## Pagination a consistency

Kolekcia objednávok môže používať cursor pagination:

```http
GET /v1/orders?limit=50&after=eyJpZCI6...
```

Cursor má viazať ordering a filter state. Offset pagination sa pri súbežných inserts môže posúvať a vytvoriť duplicates alebo omissions. Ani cursor automaticky negarantuje snapshot consistency; contract musí vysvetliť, čo client môže očakávať.

Response má mať bounded page size a stabilný next link. Neobmedzený endpoint je capacity a denial-of-service risk.

## Versioning a compatibility

API sa vyvíja additive zmenami, tolerantnými readers a explicitným deprecation lifecycle-om. Pridanie required response field býva pre JSON clients často kompatibilné iba vtedy, ak ignorujú unknown fields. Zmena semantics existujúceho field-u môže byť breaking aj bez schema diffu.

Atlas sleduje aktívne consumer versions a usage, publikuje contract artifact a testuje production deployment matrix. „Latest provider vs latest client“ nie je dostatočná compatibility evidence.

## Authorization a object scope

Authentication určí identity, authorization rozhodne o konkrétnej operácii nad konkrétnym resource. Endpoint `GET /orders/{id}` musí viazať order na tenant a principal, nie iba overiť platný token.

Negative tests sú rovnako dôležité ako happy path: iný tenant nesmie resource prečítať, zmeniť ani odvodiť jeho existenciu z rozdielneho timing alebo error detailu.

## WebSocket upgrade

WebSocket začne HTTP handshakeom:

```http
GET /v1/order-events HTTP/1.1
Connection: Upgrade
Upgrade: websocket
```

Po úspešnom upgrade vznikne dlhodobý obojsmerný channel. Proxy musí podporovať upgrade, správne timeouts a connection draining. Bežný request timeout nie je vhodný pre channel, ktorý má trvať hodiny.

TLS, DNS a load balancing stále platia. Po zmene DNS alebo backend poolu existujúci WebSocket zostáva na pôvodnej connection, kým sa nezatvorí.

## Message identity, ordering a reconnect

WebSocket transport zachová poradie frames v jednom connection, ale reconnect vytvorí nový channel. Client môže stratiť messages medzi disconnectom a resubscription alebo dostať duplicates pri replay.

Atlas events používajú monotonický stream cursor:

```json
{
  "eventId": "evt-9182",
  "orderId": "ord-8421",
  "sequence": 1042,
  "type": "OrderConfirmed"
}
```

Client potvrdzuje posledný spracovaný cursor a po reconnecte žiada replay. UI deduplikuje podľa `eventId`. Bez tohto contractu heartbeat a auto-reconnect poskytujú iba transportnú dostupnosť, nie konzistentný event view.

## Heartbeat a liveness

TCP keepalive môže odhaliť mŕtvy peer pomaly. WebSocket ping/pong alebo application heartbeat poskytuje kratší channel health contract. Interval musí byť dlhší než bežné jitter a proxy scheduling, ale kratší než požadovaný detection time.

Heartbeat success nepreukazuje, že consumer spracúva business messages. Potrebné sú queue depth, last processed sequence a end-to-end synthetic event.

## Backpressure

Rýchly producer a pomalý client vytvárajú buffer. Neobmedzená queue vedie k memory exhaustion alebo veľmi stale data. Server potrebuje limit a policy: spomaliť producer, odpojiť client s resumable cursorom, zahodiť nahraditeľné updates alebo prejsť na snapshot.

Policy závisí od semantics. Price ticker môže zahodiť intermediate values, payment state transitions nie. Backpressure nie je iba socket tuning; je to aplikačné rozhodnutie o strate a obnove.

## Incident: reconnect vytvára duplicate notifications

Mobile client po krátkom network výpadku otvorí nový WebSocket, no starý channel na proxy ešte chvíľu žije. Server registruje dve subscriptions a pošle `OrderConfirmed` dvakrát. UI nemá event deduplication a používateľ vidí dve notifications.

Oprava používa stable session/subscription identity, lease alebo replacement semantics a event IDs. Proxy drain a heartbeat skrátia zombie interval. Verification reprodukuje overlapping reconnect a potvrdí jeden user-visible outcome, hoci transport môže doručiť duplicate message.

## Zhrnutie

REST API potrebuje resource, state, idempotency, compatibility a authorization contract. WebSocket potrebuje channel lifecycle, resume cursor, deduplication, heartbeat, backpressure a draining. Transportný success bez aplikačnej identity neposkytuje správny distributed outcome.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: HTTPS, TLS, certifikáty a PKI](https-tls-certificates-pki.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Praktický sieťový projekt od namespace po HTTPS request →](networking-practical-walkthrough.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
