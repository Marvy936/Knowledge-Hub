# Load balancing

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [Proxy a reverse proxy](proxy-and-reverse-proxy.md), [TCP a UDP](tcp-and-udp.md), [DNS](dns.md)
- Súvisiace témy: health checks, high availability, autoscaling, consistent hashing, service discovery

## 1. Definícia

Load balancing je distribúcia requestov alebo network flows medzi viaceré backendy s cieľom zlepšiť dostupnosť, kapacitu a odolnosť systému.

Load balancer neodstraňuje potrebu kapacitného plánovania ani zdravého backend designu. Iba rozhoduje, kam konkrétnu prácu poslať.

## 2. Mentálny model

```text
Clients
  ↓
Load balancer
  ├── backend A
  ├── backend B
  └── backend C
```

Rozhodnutie môže vzniknúť:

- pred vytvorením spojenia cez DNS,
- pri transportnom spojení na L4,
- pri aplikačnom requeste na L7,
- na klientovi cez service discovery alebo client-side load balancing.

## 3. Server-side vs. client-side balancing

### Server-side

Klient komunikuje s jedným stabilným endpointom. Load balancer vyberie backend.

Výhody:

- centralizovaná policy,
- jednoduchší klient,
- jednotný TLS a observability bod.

Nevýhody:

- ďalší hop,
- centralizovaná failure boundary,
- potreba škálovania samotného balancera.

### Client-side

Klient dostane zoznam endpointov zo service discovery a vyberie backend sám.

Výhody:

- menej proxy hopov,
- jemnejšie request-aware rozhodnutia,
- horizontálne škálovanie rozhodovania.

Nevýhody:

- komplexnejší klient,
- library/version drift,
- náročnejšia konzistentná policy.

## 4. DNS load balancing

DNS môže vrátiť viac A/AAAA records alebo geograficky odlišné odpovede.

```text
api.example.com → 192.0.2.10
                  192.0.2.11
                  192.0.2.12
```

Obmedzenia:

- resolver a client caching,
- TTL nie je okamžitý failover,
- client nemusí records rotovať rovnomerne,
- DNS nevie spoľahlivo reagovať na každý request,
- existujúce connections zostávajú na starej adrese.

DNS balancing je vhodný pre hrubé rozdelenie trafficu medzi regióny alebo balancer tiers, nie ako jediný jemný per-request mechanizmus.

## 5. L4 load balancing

L4 balancer rozhoduje podľa flow metadata:

- source/destination IP,
- source/destination port,
- protocol,
- connection state.

Typicky vyberie backend pri začiatku connection a celý flow zostane na tom istom backende.

Výhody:

- nízky overhead,
- podpora ne-HTTP protokolov,
- možný TLS passthrough.

Nevýhody:

- nevidí HTTP path alebo headers,
- menej jemné routing pravidlá,
- health môže byť iba transportný, ak nie je implementovaný aplikačný check.

## 6. L7 load balancing

L7 balancer interpretuje aplikačný protokol a môže rozhodovať podľa:

- hostname,
- path,
- method,
- headerov,
- cookie,
- identity alebo tenant contextu,
- request body metadata, ak je to bezpečné a podporované.

L7 balancing umožňuje canary routing a service partitioning, ale zvyšuje protocol a security komplexitu.

## 7. Algoritmy

### Round robin

Backendy sa vyberajú postupne.

Vhodné pri približne rovnako náročných requestoch a homogénnych backendoch.

### Weighted round robin

Backendy majú rozdielnu váhu podľa kapacity alebo rollout policy.

### Least connections

Vyberie backend s najmenším počtom aktívnych spojení.

Môže byť lepší pri dlhých connections, ale connection count nie je rovnaký ako aktuálna computational load.

### Least requests / latency-aware

Používa počet rozpracovaných requestov alebo meranú latency.

Riziko: feedback loop môže byť nestabilný, ak sa rozhodovanie opiera o hlučné alebo oneskorené metriky.

### Random choice

Jednoduchý random výber, prípadne power-of-two choices, kde sa porovnajú dva náhodné backendy.

### Hashing

Hash podľa client IP, cookie, key alebo objektu mapuje traffic stabilnejšie na backend.

## 8. Consistent hashing

Pri bežnom modulo hashingu zmena počtu backendov presunie veľkú časť keys.

Consistent hashing minimalizuje množstvo remappingu pri pridaní alebo odstránení backendu.

Použitie:

- distributed cache,
- sharded state,
- request affinity,
- partition ownership.

Nie je to automatická záruka rovnomerného loadu. Používajú sa virtual nodes, weights a hot-key mitigation.

## 9. Health checks

Health check určuje, či backend môže prijímať traffic.

### TCP check

Overí, že port prijme connection.

### HTTP check

Overí endpoint, status a prípadne response body.

### Deep health check

Overuje dependencies alebo schopnosť vykonať business operáciu.

Deep check môže spôsobiť zbytočné vyradenie služby pri čiastočnom dependency incidente. Health endpoint má reprezentovať schopnosť prijímať nový traffic, nie úplnú diagnózu celého systému.

## 10. Liveness, readiness a startup semantics

- **Liveness**: proces je v stave, z ktorého má zmysel pokračovať.
- **Readiness**: instance má prijímať nový traffic.
- **Startup**: aplikácia ešte inicializuje stav a nemá byť predčasne hodnotená ako chybná.

Load balancer typicky potrebuje readiness, nie liveness.

## 11. Active vs. passive health

### Active

Balancer periodicky posiela health requests.

### Passive

Balancer vyhodnocuje reálne connection failures, resets alebo response statuses.

Kombinácia je užitočná: active checks odhalia chybu bez klientského requestu, passive checks reagujú na reálne failure patterns.

## 12. Failure thresholds

Jedno zlyhanie nemá automaticky vyradiť backend.

Typické parametre:

- interval,
- timeout,
- unhealthy threshold,
- healthy threshold,
- cooldown,
- slow start.

Príliš agresívny check môže pri krátkom spomalení vyradiť veľa backendov a preťažiť zvyšok — load balancer potom incident zosilní.

## 13. Connection draining

Pri odoberaní backendu:

```text
stop new traffic
  ↓
allow existing requests/connections to finish
  ↓
terminate remaining work after grace period
```

Bez drainingu sa pri deploymente alebo autoscalingu objavia resets a nedokončené requesty.

Pre dlhé WebSocket alebo streaming connections treba samostatný lifecycle model.

## 14. Session affinity

Sticky sessions smerujú klienta opakovane na rovnaký backend podľa:

- cookie,
- source IP,
- consistent hash key.

Výhody:

- podpora lokálneho session state,
- cache locality.

Nevýhody:

- nerovnomerný load,
- horší failover,
- komplikovaný autoscaling,
- skrytá závislosť na konkrétnej instance.

Preferovaný design je externalizovaný alebo replikovaný session state, ak to workload umožňuje.

## 15. Cross-zone a multi-region balancing

Rozhodnutie musí zohľadniť:

- latency,
- data locality,
- failure domains,
- egress náklady,
- regulatory boundaries,
- capacity v každej zóne,
- failover blast radius.

Globálny balancer môže používať DNS, anycast alebo global proxy tier. Regionálny balancer následne distribuuje traffic v rámci regiónu.

## 16. Anycast

Viac lokalít oznamuje rovnakú IP adresu cez routing. Network path privedie klienta k topologicky preferovanému endpointu.

Anycast je routing mechanizmus, nie aplikačný health check. Potrebuje kontrolované route withdrawal a stabilný state model.

## 17. Capacity a overload

Load balancer nemôže vytvoriť kapacitu.

Pri overload-e môže:

- queueovať,
- odmietať requesty,
- shedovať load,
- preferovať priority traffic,
- aktivovať autoscaling,
- obmedziť retries.

Neobmedzené queueing zvyšuje latency a memory pressure. Explicitné load shedding býva bezpečnejšie než pomalé zlyhanie všetkých requestov.

## 18. Retry amplification

Ak klient, proxy a load balancer každý vykoná tri retries:

```text
1 pôvodný request
× 3 client attempts
× 3 proxy attempts
× 3 upstream attempts
= potenciálne 27 pokusov
```

Počas incidentu retries môžu preťaženie násobiť.

Použi spoločný retry budget, bounded attempts, backoff, jitter a jasné vlastníctvo retry vrstvy.

## 19. Observability

Sleduj:

- requests alebo connections per backend,
- active a queued connections,
- healthy/unhealthy backend count,
- health-check failures,
- backend latency a error rate,
- retries a resets,
- connection draining duration,
- selection skew,
- rejected/load-shed requests,
- zone/region distribution.

Pri nerovnomernom loade odlišuj algoritmus od rozdielnej request cost a connection persistence.

## 20. Diagnostický postup

Keď časť klientov zlyháva:

1. rozdeľ symptómy podľa backendu, zóny, IP a protocol family,
2. skontroluj health-check state a dôvod vyradenia,
3. porovnaj request distribution s očakávanými weights,
4. over connection draining a deployment timeline,
5. skontroluj sticky-session alebo hashing key,
6. porovnaj backend capacity, latency a errors,
7. over DNS caching alebo global routing,
8. skontroluj retry amplification,
9. zachyť request IDs naprieč balancerom a backendom,
10. potvrď, že náprava obnovila používateľský výsledok.

## 21. Typické symptómy

### Každý tretí request zlyhá

Jeden z troch backendov je chybný, ale health check ho stále považuje za zdravý.

### Nová verzia prijíma príliš veľa trafficu

Nesprávna weight konfigurácia, rozdiel v connection persistence alebo hashing.

### Backend je zdravý priamo, ale unhealthy v balanceri

Health path, Host header, TLS SNI, source allowlist alebo timeout mismatch.

### Po scale-in vznikajú resets

Chýbajúci alebo príliš krátky connection draining.

### Po incidente všetko zostáva pomalé

Retry storm, dlhé queues, stale pooled connections alebo cold caches.

## 22. Časté omyly

### „Round robin rozdelí CPU load rovnomerne“

Nie, ak requesty majú rozdielnu cenu alebo connections obsahujú rôzny počet requestov.

### „Healthy port znamená zdravú aplikáciu“

TCP check dokazuje iba transportnú dostupnosť.

### „Sticky sessions riešia high availability“

Naopak môžu failover zhoršiť, ak state existuje iba lokálne.

### „Viac retries zvyšuje spoľahlivosť“

Počas overloadu môžu zlyhanie zosilniť.

### „DNS TTL nula znamená okamžitý failover“

Resolver a client behavior nemusia rešpektovať okamžitú zmenu.

## 23. Kontrolné otázky

1. Aký je rozdiel medzi DNS, L4 a L7 load balancingom?
2. Kedy je vhodný least-connections algoritmus?
3. Čo rieši consistent hashing?
4. Aký je rozdiel medzi liveness a readiness?
5. Prečo môže agresívny health check incident zosilniť?
6. Načo slúži connection draining?
7. Aké riziká prinášajú sticky sessions?
8. Prečo retries spôsobujú amplification?
9. Čo load balancer nedokáže vyriešiť bez dostatočnej backend capacity?
10. Ako diagnostikuješ situáciu, keď každý tretí request zlyhá?
