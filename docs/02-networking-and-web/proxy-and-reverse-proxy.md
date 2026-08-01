# Proxy a reverse proxy

<!-- CONCEPT-FIRST:START -->
## Čo sú forward proxy a reverse proxy

Proxy prijme komunikáciu na jednej strane a vytvorí novú komunikáciu na druhej. Tým rozdelí pôvodnú cestu na samostatné connections, timeout budgets, identities a trust boundaries.

Forward proxy koná v mene klienta. Client vie, že request posiela proxy, ktorá následne komunikuje s vybraným destination. Používa sa pre outbound access control, inspection, caching alebo privacy.

Reverse proxy koná pred servermi. Client používa service hostname a proxy vyberá upstream backend. Môže terminovať TLS, routovať podľa hostname alebo pathu, autentizovať, rate-limitovať, bufferovať, retryovať a load-balancovať.

```text
client connection:
client → reverse proxy

upstream connection:
reverse proxy → backend
```

Tieto connections majú odlišné transportné tuples. Backend typicky vidí source adresu proxy, nie klienta. Pôvodnú address alebo scheme možno preniesť cez `Forwarded` alebo `X-Forwarded-*` headers, ale proxy musí odstrániť nedôveryhodné client-supplied hodnoty. Backend smie veriť týmto headers iba od explicitne trusted proxy chainu.

TLS môže skončiť na proxy a upstream môže byť plaintext alebo nové TLS spojenie. V druhom prípade client overuje proxy identity a proxy samostatne overuje backend identity. Jedna cryptographic session neprechádza automaticky cez oba hops.

Buffering mení backpressure a timing. Proxy môže prijať celé request body pred odoslaním upstreamu alebo bufferovať response pre pomalého klienta. To chráni resources, ale môže skryť pomalý backend a meniť streaming semantics.

Retry musí rešpektovať aplikačnú idempotenciu a unknown outcome. Proxy nevie bezpečne zopakovať mutating request iba preto, že nedostala response. Server mohol side effect dokončiť.

Proxy config v control plane nie je automaticky effective worker state. Po zmene treba overiť runtime route, listener, certificate a reálny request cez rovnakú cestu ako client.
<!-- CONCEPT-FIRST:END -->

## Atlas scenár a praktické použitie

Proxy ukončí jedno aplikačné alebo transportné spojenie a vytvorí ďalšie. Tým vzniká nová identity, nový timeout budget a nový trust boundary. Pri Atlas requeste klient komunikuje s edge proxy na `203.0.113.40:443`; proxy následne komunikuje s backendom `10.60.1.21:8080`.

```text
client connection
10.24.8.37:53144 → edge:443

upstream connection
edge:47012 → 10.60.1.21:8080
```

Tieto flows môžu mať odlišný protocol, TLS state, source IP, keepalive a failure outcome.

## Forward proxy a reverse proxy

Forward proxy koná v mene klienta. Client alebo jeho network policy vie, že request posiela proxy, ktorá potom vyberie destination. Používa sa pre outbound access control, caching, inspection alebo privacy.

Reverse proxy koná pred servermi. Klient používa service hostname a nevie, ktorý backend proxy vyberie. Reverse proxy poskytuje TLS termination, routing, authentication, rate limiting, buffering, retries a load balancing.

Rovnaký software môže podporovať oba režimy, ale trust model je odlišný. Forward proxy dôveruje client identity podľa enterprise mechanizmu; reverse proxy musí chrániť upstream a správne normalizovať nedôveryhodné headers.

## HTTP routing

Reverse proxy môže rozhodovať podľa authority, path, method alebo ďalších metadata:

```text
Host / :authority = api.atlas.example
path = /v1/orders
method = POST
→ orders-api pool
```

Routing success nepreukazuje backend readiness ani business compatibility. Proxy môže správne vybrať pool, ale poslať request na starú API verziu alebo backend s chybnou config generation.

Config preview a runtime read-back majú potvrdiť effective route. Pri dynamickom proxy treba odlíšiť control-plane accepted config od worker generation, ktorá requesty skutočne obsluhuje.

## Forwarded identity

Proxy mení transport source. Ak backend potrebuje pôvodnú address alebo scheme, používa štandardizovaný `Forwarded` alebo zvyklostné `X-Forwarded-*` headers.

Proxy musí odstrániť alebo prepísať client-supplied hodnoty na trust boundary. Inak útočník pošle:

```http
X-Forwarded-For: 127.0.0.1
X-Forwarded-Proto: https
```

a backend môže nesprávne považovať request za interný alebo secure. Backend smie dôverovať forwarded headers iba od známych proxy hops a musí poznať chain parsing policy.

## Buffering a backpressure

Proxy môže bufferovať request alebo response. Buffer chráni pomalý backend alebo client a umožní uvoľniť upstream connection, ale používa memory/disk a mení latency aj streaming semantics.

Pri veľkom upload-e proxy môže prijať celé body pred odoslaním backendu. Client capture ukazuje dokončený upload, no backend request ešte nezačal. Pri streaming API alebo WebSockete treba buffering vypnúť alebo nakonfigurovať podľa protokolu.

Backpressure musí prechádzať celým chainom. Neobmedzený proxy buffer môže skryť pomalý backend až do resource exhaustion.

## Timeouts a retries

Client, proxy a backend majú vlastné connect, header, idle a total timeouts. Proxy timeout musí byť kratší než upstream resource leak, ale dostatočný pre platný request. Dôležitý je spoločný deadline budget, nie nezávislé vysoké hodnoty.

Retry je bezpečný iba pre request, ktorý je opakovateľný podľa aplikačného contractu. `GET` môže mať side effects v zle navrhnutej aplikácii a `POST` môže byť bezpečný s idempotency key. Proxy nesmie rozhodovať iba podľa názvu metódy bez znalosti outcome semantics.

## TLS termination a re-encryption

Proxy môže ukončiť client TLS a poslať upstream plaintext v trusted segment-e, alebo vytvoriť druhé TLS spojenie. V druhom prípade existujú dve oddelené peer validations:

```text
client overuje edge certifikát pre api.atlas.example
edge overuje backend certifikát a identity
```

Client nevie automaticky dokázať backend identity. Backend zasa nevidí client certifikát bez mTLS passthroughu alebo explicitného identity forwarding mechanizmu.

## Incident: duplicate objednávky po proxy timeout-e

Backend spracuje `POST /v1/orders`, commitne objednávku, ale response prekročí proxy timeout. Proxy má generický retry pre všetky `5xx` a timeouts a request zopakuje na druhý backend. Bez stabilného idempotency key vzniknú dve objednávky.

Proxy logs ukážu dva upstream attempts pre jeden client request ID. Backend logs ukážu dva business IDs. Oprava vypne unsafe retry a API zavedie idempotency contract viazaný na tenant a operation. Verification testuje timeout po commite a potvrdí jeden business outcome.

## Zhrnutie

Proxy rozdeľuje end-to-end cestu na dve alebo viac connections. Mení source identity, TLS boundary, buffering, timeout a retry semantics. Diagnostika musí korelovať client request, proxy attempt a backend outcome namiesto predpokladu jedného flowu.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Firewally](firewalls.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Load balancing →](load-balancing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
