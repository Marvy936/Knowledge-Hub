# Proxy a reverse proxy

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [DNS](dns.md), [Ports a sockets](ports-and-sockets.md), [Firewally](firewalls.md)
- Súvisiace témy: load balancing, HTTP, TLS termination, caching, service mesh, WAF

## 1. Definícia

Proxy je sprostredkovateľ, ktorý prijme komunikáciu od jednej strany a vytvorí samostatnú komunikáciu k druhej strane.

- **Forward proxy** zastupuje klienta voči externým serverom.
- **Reverse proxy** zastupuje serverovú službu voči klientom.

Proxy nie je iba packet forwarder. Typicky ukončuje transportné alebo aplikačné spojenie, interpretuje protokol a vytvára nové upstream spojenie.

## 2. Mentálny model

```text
Client
  ↓ connection A
Proxy
  ↓ connection B
Upstream server
```

Connection A a connection B majú samostatný lifecycle, timeouts, buffers, TLS state a observability.

To je zásadný rozdiel oproti routeru, ktorý typicky forwarduje packets bez ukončenia aplikačného protokolu.

## 3. Forward proxy

Forward proxy používajú klienti napríklad na:

- riadený outbound access,
- egress filtering,
- audit a logging,
- content filtering,
- caching,
- anonymizáciu source address,
- prístup do externých sietí z izolovaného prostredia.

Konfigurácia môže byť explicitná:

```text
HTTPS_PROXY=http://proxy.example:3128
NO_PROXY=localhost,127.0.0.1,.internal.example
```

alebo transparentná, keď network infraštruktúra traffic presmeruje bez explicitného client nastavenia.

## 4. HTTP CONNECT

Pri HTTPS cez explicitný forward proxy klient často použije:

```http
CONNECT api.example.com:443 HTTP/1.1
Host: api.example.com:443
```

Proxy následne vytvorí TCP tunnel. Pri bežnom CONNECT proxy nevidí HTTP obsah vo vnútri TLS spojenia, ale vidí destination hostname/port a metadata spojenia.

TLS inspection je odlišný model: proxy dynamicky vystupuje ako TLS server voči klientovi a ako klient voči originu. Vyžaduje vlastnú dôveryhodnú CA v klientskych trust stores a predstavuje významnú security boundary.

## 5. Reverse proxy

Reverse proxy býva verejným alebo interným endpointom pred aplikáciami.

Použitie:

- TLS termination,
- host/path routing,
- load balancing,
- authentication a authorization integration,
- rate limiting,
- request/response transformations,
- compression,
- caching,
- WAF policy,
- access logging,
- connection pooling.

Príklad toku:

```text
https://shop.example/api/orders
  ↓ DNS
Reverse proxy :443
  ↓ route podľa Host + path
orders-service:8080
```

## 6. L4 vs. L7 proxy

### L4 proxy

Rozhoduje podľa transportných údajov:

- destination port,
- source/destination IP,
- TCP/UDP flow,
- prípadne TLS SNI bez plného HTTP spracovania.

Výhody:

- menší protocol overhead,
- vhodné aj pre ne-HTTP protokoly,
- môže zachovať end-to-end TLS.

### L7 proxy

Interpretuje aplikačný protokol, napríklad HTTP:

- Host header,
- path,
- method,
- headers,
- cookies,
- response status.

Umožňuje jemnejší routing a policy, ale proxy sa stáva súčasťou aplikačného failure modelu.

## 7. TLS termination a re-encryption

Modely:

```text
Client --TLS--> Proxy --plain HTTP--> Upstream
Client --TLS--> Proxy --TLS--> Upstream
Client --TLS passthrough--------------> Upstream
```

Plain HTTP za proxy môže byť prijateľné iba v jasne ohraničenej dôveryhodnej sieti. V zero-trust alebo multi-tenant prostredí sa používa re-encryption alebo mTLS.

TLS termination mení vlastníctvo certifikátov, cipher policy, protocol negotiation a auditovania.

## 8. Preservation client identity

Upstream pri bežnom proxy spojení vidí source IP proxy, nie pôvodného klienta.

HTTP proxy môže pridať:

```http
Forwarded: for=198.51.100.25;proto=https;host=app.example
X-Forwarded-For: 198.51.100.25
X-Forwarded-Proto: https
X-Forwarded-Host: app.example
```

Tieto headers sú dôveryhodné iba vtedy, keď aplikácia prijíma traffic výhradne od kontrolovaného proxy a proxy odstráni alebo prepíše client-supplied hodnoty.

Pri L4 proxy sa môže použiť PROXY protocol, ktorý prenesie source/destination metadata mimo aplikačného payloadu. Obe strany ho musia explicitne podporovať.

## 9. Host a path routing

Príklad:

```text
Host: api.example.com, path /billing/*  → billing-service
Host: api.example.com, path /users/*    → users-service
Host: static.example.com                → object storage
```

Riziká:

- nesprávna priorita routes,
- path normalization rozdiely,
- URL encoding ambiguity,
- nebezpečné trustovanie Host headera,
- chýbajúci default backend,
- rozdiel medzi trailing slash semantics.

## 10. Buffering a streaming

Proxy môže bufferovať request alebo response:

```text
Client → proxy buffer → upstream
Upstream → proxy buffer → client
```

Buffering chráni upstream pred pomalými klientmi a umožňuje retry pred odoslaním response. Zároveň môže:

- zvýšiť latency,
- spotrebovať memory/disk,
- rozbiť streaming,
- skryť backpressure,
- meniť timeout behavior.

Pre WebSockets, Server-Sent Events a veľké uploads treba explicitne overiť buffering a idle timeouts.

## 11. Timeouts

Proxy má viac nezávislých timeoutov:

- client header timeout,
- client body timeout,
- connect timeout k upstreamu,
- upstream response/header timeout,
- idle timeout,
- total request timeout,
- keep-alive timeout.

Príliš krátky timeout spôsobí falošné zlyhania. Príliš dlhý timeout drží sockets, memory a concurrency počas degradácie upstreamu.

Timeout budget musí byť koordinovaný naprieč celým request pathom.

## 12. Retry

Proxy môže opakovať request pri:

- connection failure,
- reset pred response,
- vybraných HTTP statusoch,
- timeoutoch.

Retry je bezpečný iba pri správnej idempotency semantics. Opakovanie `POST` po nejasnom zlyhaní môže vytvoriť duplicitnú business operáciu.

Dobrý retry model používa:

- bounded attempts,
- backoff a jitter,
- retry budget,
- per-try timeout,
- idempotency keys,
- circuit breaking alebo outlier detection.

## 13. Connection pooling

Proxy môže udržiavať persistent upstream connections.

Výhody:

- menej TCP/TLS handshakes,
- nižšia latency,
- menší CPU overhead.

Riziká:

- stale connections,
- nerovnomerné rozdelenie pri HTTP/2 multiplexingu,
- vyčerpanie upstream connection limitu,
- DNS zmena nemusí okamžite presmerovať existujúce pool connections.

## 14. Caching

Reverse proxy môže cacheovať odpovede podľa cache key.

Cache key môže zahŕňať:

- scheme,
- host,
- path,
- query,
- vybrané headers,
- cookies alebo identity context.

Chybný cache key môže spôsobiť únik personalizovaného obsahu medzi používateľmi.

Treba rešpektovať `Cache-Control`, `Vary`, authorization semantics a invalidation model.

## 15. Security hranice

Proxy často spracúva nedôveryhodný vstup a má prístup k interným upstreamom.

Riziká:

- request smuggling,
- header spoofing,
- open proxy konfigurácia,
- SSRF cez dynamický upstream,
- nebezpečné URL normalization,
- TLS downgrade alebo slabá cipher policy,
- príliš široký egress access,
- secrets v access logoch.

Forward proxy musí obmedziť povolené destinations. Reverse proxy musí validovať Host, path a protocol framing.

## 16. Observability

Sleduj oddelene client-side a upstream-side signály:

```text
client connections
request rate
HTTP status podľa proxy/upstream pôvodu
upstream connect time
upstream response time
total request time
retries
active/queued connections
bytes in/out
TLS handshake failures
```

Status `502`, `503` a `504` majú odlišný význam, ale konkrétna implementácia ich môže mapovať rozdielne.

## 17. Diagnostický postup

Pri zlyhaní cez reverse proxy:

1. over DNS na proxy endpoint,
2. otestuj TCP/TLS spojenie klient → proxy,
3. skontroluj proxy access/error log,
4. over route match podľa Host/path,
5. over DNS alebo service discovery pre upstream,
6. otestuj proxy → upstream connectivity,
7. skontroluj upstream listener a health,
8. porovnaj timeouty a retries,
9. over forwarding headers a protocol version,
10. otestuj upstream priamo iba ako kontrolovaný diagnostický experiment.

## 18. Typické symptómy

### `502 Bad Gateway`

Proxy prijala request, ale nedostala validnú upstream response. Príčina môže byť connection reset, protocol mismatch alebo chybný upstream.

### `503 Service Unavailable`

Žiadny zdravý upstream, overload, maintenance policy alebo circuit breaker.

### `504 Gateway Timeout`

Upstream neodpovedal v proxy timeout budgete.

### Funguje priamo, nie cez proxy

Skontroluj Host header, path rewrite, TLS SNI, proxy headers, body limits a timeouty.

### Fungujú malé requesty, veľké nie

Body size limit, buffering disk, timeout, MTU alebo upstream upload limit.

## 19. Časté omyly

### „Reverse proxy je iba DNS alias“

Nie. Vytvára samostatné spojenia a môže meniť protocol behavior.

### „X-Forwarded-For je vždy dôveryhodná client IP“

Nie. Dôveryhodnosť závisí od kontrolovaného proxy chainu.

### „502 znamená, že aplikácia vrátila chybu“

Často ide o chybu medzi proxy a upstreamom ešte pred platnou aplikačnou response.

### „Proxy retry je vždy bezpečný“

Nie pri ne-idempotentných operáciách alebo nejasnom stave spracovania.

### „TLS termination odstráni potrebu šifrovania interne“

Nie automaticky. Závisí od threat modelu a trust boundaries.

## 20. Kontrolné otázky

1. Aký je rozdiel medzi forward a reverse proxy?
2. Prečo proxy vytvára dve samostatné connections?
3. Aký je rozdiel medzi L4 a L7 proxy?
4. Kedy je `X-Forwarded-For` dôveryhodný?
5. Aké riziká prináša buffering?
6. Prečo retry môže duplikovať business operáciu?
7. Ako TLS termination mení security boundary?
8. Čo rozlišuje `502`, `503` a `504`?
9. Prečo môže connection pooling spomaliť reakciu na DNS zmenu?
10. Ako diagnostikuješ request fungujúci priamo, ale nie cez proxy?
