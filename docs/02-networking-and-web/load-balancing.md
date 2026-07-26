# Load balancing

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [Proxy a reverse proxy](proxy-and-reverse-proxy.md), [TCP a UDP](tcp-and-udp.md), [DNS](dns.md)
- Súvisiace témy: health checks, high availability, autoscaling, consistent hashing, service discovery, retries

## 1. Problém, ktorý load balancing rieši

Atlas prevádzkuje tri Orders backendy:

```text
orders-a 10.20.3.21:8080
orders-b 10.20.3.22:8080
orders-c 10.20.3.23:8080
```

Jeden backend neposkytuje dostatočnú kapacitu ani požadovaný failure model. Reverse proxy preto musí pri každom novom flowe alebo requeste rozhodnúť, ktorý backend dostane prácu.

Load balancing je tento selection proces:

```text
incoming work
→ známy endpoint inventory
→ health a eligibility
→ selection unit a algorithm
→ selected backend
→ request/connection lifecycle
→ outcome a feedback
```

Load balancer nevytvára backend capacity. Môže ju iba rozdeliť, chrániť queue alebo limitmi a pri overload-e časť práce odmietnuť.

## 2. Dominantný mentálny model

Balancing decision nie je iba „round robin“. Potrebuje odpoveď na šesť previazaných otázok:

1. **Inventory** — ktoré endpointy balancer pozná?
2. **Eligibility** — ktoré z nich smú dostať nový traffic?
3. **Granularity** — vyberá sa pre DNS odpoveď, connection, request, session alebo key?
4. **Selection** — podľa akého signálu sa backend zvolí?
5. **Lifecycle** — ako sa endpoint pridá, warmuje, drainuje a odstráni?
6. **Feedback** — ako health, capacity, retries a používateľský outcome menia ďalšie rozhodnutia?

Chyba v ktorejkoľvek fáze môže vytvoriť nerovnomerný load alebo čiastočné zlyhanie, aj keď samotný algoritmus funguje presne podľa konfigurácie.

## 3. Carried scenario: jeden Orders request

Klient odošle `POST /orders` na Atlas reverse proxy. Proxy má aktuálny pool:

```text
orders-a: eligible, weight 1
orders-b: eligible, weight 1
orders-c: eligible, weight 1
```

Request path:

```text
request dorazí na proxy
→ route vyberie orders pool
→ proxy načíta effective endpoint set
→ odstráni unhealthy alebo draining endpointy
→ algorithm zvolí orders-b
→ proxy získa upstream connection
→ request odošle
→ outcome sa zapíše k orders-b
```

Ak `orders-b` vráti reset, proxy môže backend označiť ako suspect, ale retry na inom backende je bezpečný iba podľa request semantics a idempotency state.

## 4. Jednotka výberu mení význam distribúcie

### DNS selection

DNS vráti jednu alebo viac frontend adries. Rozhodnutie môže prežiť v resolver cache a existujúcej connection.

### L4 connection selection

Balancer vyberie backend pri vzniku TCP alebo UDP flowu. Celý flow zostáva typicky na jednom backende.

### L7 request selection

Proxy môže vyberať backend pre každý HTTP request. Jedna downstream HTTP/2 connection môže obsahovať veľa requests smerovaných do viacerých upstream connections.

### Session alebo key selection

Cookie, tenant, object key alebo shard key môže viazať súvisiacu prácu na rovnaký backend.

Dôsledok:

```text
5 % nových connections
≠
5 % requestov
≠
5 % CPU práce
```

Pri long-lived alebo multiplexed connections môže malý connection share niesť veľký request share.

## 5. Endpoint discovery a effective inventory

Balancer môže získať backendy zo statickej konfigurácie, DNS, registry API, cloud target groupy alebo Kubernetes EndpointSlices.

Endpoint lifecycle:

```text
backend vznikne
→ zaregistruje sa alebo je objavený
→ readiness a health sa overia
→ endpoint sa stane eligible
→ prijíma traffic
→ označí sa draining
→ nové selections sa zastavia
→ aktívna práca skončí alebo timeoutuje
→ endpoint sa odstráni
```

Treba odlíšiť:

```text
desired endpoint set
≠
discovered endpoint set
≠
eligible endpoint set
≠
endpointy, ktoré reálne dostávajú traffic
```

Control-plane delay môže spôsobiť, že odstránený backend zostane v effective sete. Naopak nový backend môže byť známy, ale ešte not ready.

## 6. Eligibility je brána pred algoritmom

Selection algorithm sa má aplikovať iba na endpointy, ktoré smú dostať nový traffic.

Eligibility môže závisieť od:

- readiness,
- active a passive health,
- zone alebo region policy,
- maintenance a drain state,
- weight väčšie než nula,
- capacity alebo concurrency limit,
- protocol a tenant kompatibility,
- rollout cohort.

Ak je eligible set prázdny, balancer potrebuje explicitný failure model:

- vrátiť `503`,
- použiť fallback pool,
- krátko queueovať,
- servovať stale cache,
- vedome použiť posledný známy endpoint.

Tiché „vyber čokoľvek“ môže poslať traffic na endpoint, ktorý bol zámerne vyradený.

## 7. Health check musí odpovedať na správnu otázku

Load balancer potrebuje najmä readiness odpoveď:

```text
Má tento backend prijať nový traffic teraz?
```

### Príliš plytký check

TCP connect potvrdí listener, ale Orders worker môže byť deadlocked alebo databáza nedostupná.

### Príliš deep check

Ak readiness vyžaduje úspech všetkých shared dependencies, databázový incident môže označiť všetky backends unhealthy a úplne vyprázdniť pool, hoci služba mohla vrátiť kontrolovanú degraded response.

### Hysteresis

Jedno zlyhanie nemá typicky okamžite meniť state:

```text
healthy
→ viac consecutive failures
→ unhealthy
→ viac consecutive successes
→ healthy
```

Interval, timeout, thresholds a cooldown musia zabrániť flappingu bez neprimerane pomalej reakcie.

## 8. Active a passive health poskytujú odlišný dôkaz

Active probe testuje pravidelne definovaný endpoint. Vie odhaliť failure aj bez trafficu, ale môže používať inú path a request class než reálni klienti.

Passive health sleduje skutočné resets, timeouty a statusy. Odráža produkčný traffic, ale reaguje až po používateľskom dopade a môže zameniť zlý request za chybný backend.

Kombinácia:

```text
active health
+ passive outcome
+ minimum sample
+ ejection limit
→ stabilnejší eligibility state
```

Outlier detection musí mať maximum ejection percentage. Inak môže pri shared dependency incidente vyradiť väčšinu poolu a preťažiť zvyšok.

## 9. Selection algorithm musí zodpovedať load signálu

### Round robin

Rozdeľuje počet selections. Funguje dobre pri podobných backendoch a podobnej cene práce.

```text
A → B → C → A
```

Nezaručuje rovnaké CPU, ak requests majú rozdielnu cenu.

### Weighted selection

Weight vyjadruje relatívny share alebo rollout zámer. Effective share stále menia connection persistence, affinity a retries.

### Least connections alebo requests

Používa aktuálnu concurrency ako aproximáciu loadu. Connection count je slabý signál pri HTTP/2, idle sessions alebo rozdielnych request costs.

### Hash selection

Stabilizuje affinity podľa cookie, tenant ID alebo object key. Môže však vytvoriť hot key alebo nerovnomernú distribúciu.

Dôležité pravidlo:

```text
algoritmus nerozdeľuje to, čo nemeria
```

Ak Atlas chce vyrovnať active request concurrency, samotný počet TCP connections nemusí byť vhodný signal.

## 10. Consistent hashing a affinity nemenia state ownership

Affinity môže zlepšiť cache locality alebo podporiť legacy in-memory session:

```text
tenant-42 → orders-b
```

Nevýhody:

- load skew,
- horší failover,
- pomalší scale-in,
- stale mapping po removal,
- veľa klientov za jednou NAT source IP,
- závislosť na lokálnom state.

Consistent hashing obmedzí remapping keys pri zmene pool membership. Nezabezpečí však replikáciu session ani dostupnosť dát po zlyhaní backendu.

Load balancer vyberá ownera práce. Neudržuje automaticky konzistentný aplikačný state.

## 11. Slow start chráni nový backend

Nový `orders-d` prejde health checkom, ale má cold cache, prázdny connection pool a JIT warm-up.

Bez slow startu:

```text
health success
→ plný traffic share
→ latency spike
→ health failures
→ ejection
→ recovery
→ plný share znova
→ flapping
```

Slow start zvyšuje effective weight postupne:

```text
0 % → 10 % → 30 % → 60 % → 100 %
```

Tým sa backend warmuje pod kontrolovaným loadom a health systém dostáva reprezentatívne samples.

## 12. Draining koordinuje endpoint removal

Pri deploymente Atlas označí `orders-b` ako draining:

```text
eligible
→ draining
→ žiadne nové selections
→ existujúce requests a streams pokračujú
→ active work dosiahne nulu alebo timeout
→ process sa ukončí
```

Treba koordinovať:

```text
readiness removal
→ discovery propagation
→ balancer drain
→ application shutdown grace
→ process termination
```

Ak process skončí skôr než balancer prestane posielať traffic, vzniknú resets. Ak drain trvá neobmedzene, WebSocket alebo gRPC session môže blokovať rollout.

## 13. Retry a backend reselection

Balancer môže po failure vybrať iný backend. To pomáha pri instance-local chybe, ale nie pri shared dependency alebo overload-e.

Nebezpečný flow:

```text
orders-a vykoná side effect
→ response sa stratí
→ balancer retryuje na orders-b
→ side effect sa zopakuje
```

Bezpečnosť retry závisí od:

- idempotency,
- fázy odoslania requestu,
- response progress,
- per-try timeoutu,
- bounded attempts,
- retry budgetu.

Retry budget obmedzuje extra traffic. Pri `1000` originálnych requests/s a budgete `10 %` môže systém dovoliť približne `100` retry attempts/s, nie neobmedzené opakovanie každej chyby.

## 14. Queueing a load shedding

Keď arrival rate prekročí backend service rate:

```text
arrival > throughput
→ queue rastie
→ tail latency rastie
→ timeouty
→ retries
→ ešte vyšší arrival rate
```

Queue absorbuje krátky burst, ale nevytvára capacity. Musí mať max length, max wait a rejection behavior.

Pri trvalom overload-e je často bezpečnejší load shedding:

- rýchlo odmietnuť low-priority request,
- chrániť kritickú operáciu,
- obmedziť expensive endpoint,
- servovať stale cache,
- degradovať voliteľnú funkciu.

Rýchly `503` môže byť systémovo lepší než pomalý timeout každého requestu.

## 15. Load balancer a autoscaler tvoria feedback loop

```text
load rastie
→ queue alebo CPU rastie
→ autoscaler vytvorí backendy
→ startup a warm-up
→ discovery ich oznámi
→ health ich označí eligible
→ balancer rozdelí traffic
→ load per backend klesne
```

Riziká:

- autoscaler reaguje na retry-generated load,
- health pustí cold backend priskoro,
- všetky nové backends naraz zaťažia shared database,
- scale-in odstráni endpoint bez drainu,
- control-plane delay spôsobí neskorú reakciu.

Balancing, health a autoscaling preto nemožno ladiť ako nezávislé podsystémy.

## 16. Worked failure: každý tretí request zlyhá

Atlas vidí približne `33 %` error rate. Backends pri direct teste vyzerajú väčšinou zdravo.

### Hypotéza

Jeden z troch endpointov zostal eligible, hoci má chybnú konfiguráciu.

### Predikcie

- failures korelujú s jedným backend ID,
- configured pool obsahuje tri endpoints,
- effective selection je približne rovnomerný,
- health check je príliš plytký,
- chybný backend prijíma traffic aj počas incidentu.

### Overenie

1. Koreluj request ID s vybraným backendom.
2. Rozdeľ error rate podľa endpointu.
3. Porovnaj discovered a eligible set.
4. Skontroluj active-health path a Host/SNI.
5. Otestuj rovnaký request z proxy namespace.
6. Over backend version a config.

Mechanický dôkaz:

```text
orders-a success ≈ 100 %
orders-b success ≈ 0 %
orders-c success ≈ 100 %
+ round-robin selections ≈ 1/3 na každý
→ chybný eligible backend
```

Oprava:

- okamžite označiť `orders-b` draining alebo unhealthy,
- zmeniť readiness tak, aby overovala relevantný Orders contract,
- pridať version/config identity do endpoint metrics,
- otestovať recovery hysteresis pred návratom.

Zmena algoritmu na least-connections by root cause nevyriešila; iba by zmenila podiel failures.

## 17. Worked failure: canary s weight 5 dostáva 30 % requestov

Atlas nasadí canary backend s weight `5`, stable pool má weight `95`. Monitoring však ukáže, že canary spracúva približne `30 %` requests.

Možný mechanizmus:

```text
selection je per TCP connection
→ niekoľko klientov drží long-lived HTTP/2 connections
→ connection vytvorená počas canary selection nesie veľa streams
→ request share nezodpovedá connection weight
```

Diagnostika:

- urči selection granularity,
- porovnaj connections a requests per backend,
- skontroluj affinity,
- zmeraj lifetime a request count na connection,
- rozlíš configured a effective weight,
- over retries a reselection.

Riešením môže byť L7 per-request selection, connection rotation, menší canary connection share alebo rollout metrika založená na reálnom request share. Samotná konfigurácia `5 %` nie je dôkazom výsledku.

## 18. Worked failure: scale-in spôsobuje resets

Timeline:

```text
10:00 autoscaler zníži desired replicas
10:00 endpoint zmizne z application inventory
10:01 process dostane SIGTERM
10:02 balancer stále posiela nové requests
10:02 klienti vidia resets a retries
```

Root cause môže byť nesprávne poradie:

```text
process shutdown
pred
endpoint propagation a drain completion
```

Správny lifecycle:

```text
readiness false
→ počkaj na discovery propagation
→ no new selections
→ drain active work
→ shutdown process
```

Timers musia byť merané ako jeden chain, nie konfigurované izolovane v autoscaleri, balanceri a aplikácii.

## 19. Failure domains

Rozdelenie medzi troma procesmi nechráni pred shared failure:

```text
orders-a ┐
orders-b ├→ jedna databáza
orders-c ┘
```

Ak databáza zlyhá, všetky backendy môžu zostať procesne live, ale request outcome zlyhá.

Load balancing návrh musí zohľadniť host, rack, zone, region, software version a dependency cluster. Capacity reserve musí existovať aj po strate plánovaného failure domainu.

## 20. Observability

### Inventory a lifecycle

- discovered, eligible, unhealthy a draining endpoints,
- endpoint version, age a zone,
- discovery a removal delay.

### Selection

- connections alebo requests per backend,
- configured a effective weight,
- affinity-key distribution,
- selection skew.

### Capacity

- active requests a connections,
- queue depth a wait,
- backend concurrency limit,
- rejected a load-shed traffic.

### Health

- active probe result,
- passive failures,
- ejection a recovery eventy,
- flapping count.

### Outcome

- latency a error rate per backend,
- retry count,
- resets,
- client-visible status,
- drain duration.

Bez backend identity v request logu sa čiastočný failure ťažko odlíši od náhodného aplikačného erroru.

## 21. Referenčné balancing modely

Nasledujúce modely používajú rovnaký inventory–eligibility–selection lifecycle.

### Server-side a client-side balancing

Server-side proxy centralizuje policy, ale vytvára ďalší availability a capacity tier. Client-side model odstráni centrálny hop, no distribuuje endpoint cache, retry a algorithm policy do klientov.

### DNS balancing

Je vhodný pre coarse region alebo frontend steering. Cache a existujúce connections bránia okamžitému per-request failoveru.

### L4, L7, NAT a direct-server-return dataplane

Dataplane určuje selection granularity, source-IP preservation, state ownership a return path. Direct server return môže obísť balancer na response path, no backend musí vlastniť potrebnú frontend identity a routing model.

### Cross-zone a multi-region

Cross-zone zlepšuje využitie capacity, ale pridáva latency, cenu a failure coupling. Multi-region selection musí rešpektovať data residency, state locality a pripravenosť dependencies.

### Anycast

Routing vyberie topologicky preferovanú lokalitu pre spoločnú IP. Nie je to aplikačný health check a path change môže prerušiť stateful flow.

## 22. Časté omyly

### „Round robin rozdelí CPU rovnomerne“

Rozdeľuje selections, nie cenu práce.

### „Healthy port znamená zdravú aplikáciu“

TCP check dokazuje iba transportný listener.

### „Weight 5 znamená presne 5 % requestov“

Nie pri connection-level výbere, affinity, retries a malom sample size.

### „Least connections vždy vyberie najmenej zaťažený backend“

Connection count nemusí reprezentovať requests, streams ani CPU.

### „Sticky session poskytne high availability“

Pri lokálnom state môže failover zhoršiť.

### „Viac retries zvyšuje spoľahlivosť“

Pri shared failure alebo overload-e zvyšujú load a spomaľujú recovery.

### „Load balancer vyrieši nedostatok capacity“

Môže iba rozdeliť, queueovať alebo odmietnuť existujúcu kapacitu.

### „Health check má overiť všetky dependencies“

Príliš deep check môže vyradiť celý pool pri shared incident-e.

## 23. Kontrolné otázky

1. Ktorých šesť častí tvorí load-balancing decision model?
2. Ako sa líši selection pre DNS, L4 connection a L7 request?
3. Prečo desired, discovered a eligible endpoint set nie sú totožné?
4. Čo má readiness health check dokazovať?
5. Prečo active a passive health poskytujú odlišný dôkaz?
6. Ako hysteresis zabraňuje flappingu?
7. Prečo round robin nemusí rozdeliť CPU rovnomerne?
8. Kedy je least-connections slabý signal?
9. Čo consistent hashing rieši a čo nerieši?
10. Aké riziká prináša affinity?
11. Prečo nový backend potrebuje slow start?
12. Ako má vyzerať drain lifecycle?
13. Kedy je retry na inom backende nebezpečný?
14. Ako retry budget chráni kapacitu?
15. Prečo queue nevytvára throughput?
16. Ako load shedding znižuje systemic failure?
17. Ako autoscaler a balancer tvoria feedback loop?
18. Ako diagnostikuješ každý tretí zlyhaný request?
19. Prečo configured canary weight nemusí zodpovedať request share?
20. Ktoré timers spôsobia resets pri scale-in-e?
21. Prečo viac backendov nechráni pred shared database failure?

## 24. Zhrnutie

Load balancing je lifecycle výberu backendu, nie názov jedného algoritmu. Balancer musí poznať endpointy, určiť ich eligibility, zvoliť správnu jednotku práce a selection signal, bezpečne spravovať warm-up a draining a používať health a outcome ako feedback.

Praktický troubleshooting preto začína effective endpoint setom a backend identity konkrétneho requestu. Až potom sa hodnotí algorithm, weight, affinity, health, queue, retry a capacity. Konfigurácia môže byť syntakticky správna a napriek tomu produkovať chybný výsledok, ak selection granularity alebo feedback loop nezodpovedá reálnemu workloadu.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Proxy a reverse proxy](proxy-and-reverse-proxy.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: HTTP →](http.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
