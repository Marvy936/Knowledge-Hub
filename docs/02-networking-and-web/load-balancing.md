# Load balancing

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [Proxy a reverse proxy](proxy-and-reverse-proxy.md), [TCP a UDP](tcp-and-udp.md), [DNS](dns.md)
- Súvisiace témy: health checks, high availability, autoscaling, consistent hashing, service discovery, retries

## 1. Definícia

Load balancing je výber jedného alebo viacerých backendov pre nové flows alebo requests tak, aby sa traffic rozdelil podľa kapacity, health, locality, policy a failure-domain cieľov.

Load balancer nevytvára backend capacity. Rozdeľuje existujúcu prácu medzi existujúce resources.

```text
incoming work
    ↓
endpoint inventory
    ↓
health a eligibility
    ↓
selection algorithm
    ↓
selected backend
    ↓
connection/request lifecycle
```

Úspešný návrh musí odpovedať:

- kto pozná backendy,
- čo je jednotka výberu,
- podľa čoho sa backend považuje za zdravý,
- ako sa zohľadní kapacita,
- čo sa stane pri failure,
- kto retryuje,
- ako sa backend bezpečne pridá a odoberie,
- ako sa overí rovnomernosť a používateľský výsledok.

## 2. Jednotka balancing rozhodnutia

Balancing rozhodnutie môže platiť pre rôzne jednotky práce.

### DNS odpoveď

Resolver alebo klient dostane jednu či viac IP adries. Rozhodnutie môže pretrvať podľa cache a existujúcej connection.

### Transportný flow

L4 balancer vyberie backend pri vzniku TCP alebo UDP flowu. Celý flow zostáva typicky na rovnakom backende.

### Aplikačný request

L7 balancer môže vybrať backend pre každý HTTP request. Pri HTTP/1.1 keep-alive, HTTP/2 alebo HTTP/3 sa viac requestov môže prenášať jedným downstream flowom a rozdeliť do viacerých upstream flows.

### Logical key

Hash alebo shard key môže viazať tenant, cache key, session alebo objekt na konkrétny backend.

### Klientská session

Affinity môže viazať používateľa alebo cookie na backend dlhšie než jeden request.

Bez pomenovania selection granularity nemožno správne interpretovať algoritmus ani metrics.

## 3. Server-side load balancing

Pri server-side modeli klient používa stabilný frontend endpoint.

```text
Client
    ↓ frontend address
Load balancer
    ├── backend A
    ├── backend B
    └── backend C
```

Výhody:

- jednoduchší klient,
- centralizovaná policy,
- jednotný TLS alebo observability bod,
- jednoduchšie skrývanie backend topology,
- konzistentné retries, timeouts a health.

Nevýhody:

- ďalší hop,
- samostatný scaling a availability problém,
- centralizovaná blast radius,
- možné source identity zmeny,
- queue a state v balancer tieri.

Server-side tier musí byť sám redundantný a nesmie sa stať kapacitným choke pointom.

## 4. Client-side load balancing

Klient získa endpoint inventory zo service discovery a vyberie backend sám.

```text
service discovery
    ↓ endpoint set
client library
    ↓ selection
backend
```

Výhody:

- bez centrálneho proxy hopu,
- rozhodovanie môže poznať request context,
- load-balancing capacity rastie s počtom klientov,
- priame end-to-end spojenie.

Nevýhody:

- komplexná klientská knižnica,
- version a policy drift,
- rozdielne retry a health správanie,
- endpoint cache v každom klientovi,
- ťažšie globálne observability a rollout policy.

Client-side model potrebuje konzistentnú library governance alebo sidecar/local proxy abstrakciu.

## 5. DNS load balancing

DNS môže vrátiť viac A alebo AAAA records alebo odpoveď meniť podľa geografie, health a policy.

```text
api.example.com
    → 192.0.2.10
    → 192.0.2.11
    → 192.0.2.12
```

DNS balancing sa hodí na:

- rozdelenie medzi regióny,
- geografické smerovanie,
- weighted migration,
- výber frontend tieru,
- disaster-recovery endpoint.

Limity:

- resolver a application cache,
- TTL nie je presný switch timer,
- clients nemusia odpovede používať rovnomerne,
- negatívne cache a stale answers,
- existujúce connections zostávajú na starom endpoint-e,
- health sa vyhodnocuje mimo konkrétneho requestu,
- recursive resolver locality nemusí zodpovedať client locality.

DNS je coarse-grained steering, nie connection-aware per-request balancing.

## 6. L4 load balancing

L4 balancer vyberá backend podľa transportného flowu.

Match alebo hash môže používať:

- source a destination IP,
- source a destination port,
- protocol,
- interface alebo zone,
- TLS ClientHello metadata podľa implementácie.

Typický lifecycle:

```text
new SYN/flow
    ↓ backend selection
connection state
    ↓ všetky packets flowu na rovnaký backend
close/timeout
    ↓ state removal
```

Výhody:

- nízky protocol overhead,
- podpora databáz, mailu, custom TCP a UDP,
- možný TLS passthrough,
- vysoká throughput kapacita.

Limity:

- nevie path alebo method routing bez L7 parsing-u,
- jeden long-lived flow môže niesť veľa loadu,
- health môže byť príliš plytký,
- flow state komplikuje failover a HA.

## 7. L7 load balancing

L7 balancer rozumie aplikačnému protokolu.

Pri HTTP môže vyberať podľa:

- hostname alebo authority,
- path,
- method,
- headers,
- cookie,
- tenant alebo identity,
- canary flagu,
- request metadata.

Umožňuje:

- per-request selection,
- canary a blue/green routing,
- retry podľa request semantics,
- request-level metrics,
- content alebo tenant partitioning.

Zvyšuje však:

- parsing complexity,
- CPU a memory nároky,
- attack surface,
- závislosť na protocol correctness,
- riziko retry duplication.

## 8. Pass-through, proxy a direct-routing dataplane

Load balancing môže byť implementovaný rôzne.

### Full proxy

Balancer ukončí downstream connection a vytvorí upstream connection.

### NAT

Balancer preloží destination alebo source tuple a udržiava state.

### Direct server return

Ingress path ide cez balancer, response môže ísť priamo z backendu ku klientovi.

### Tunnel alebo overlay

Balancer encapsuluje packet a backend ho decapsuluje.

### eBPF alebo kernel dataplane

Výber a translation sa vykonáva v kernel hooku bez klasického userspace proxy pathu.

Dataplane určuje source-IP preservation, state ownership, return path, observability a failover behavior.

## 9. Endpoint discovery

Balancer musí vedieť, ktoré backendy existujú.

Zdroje:

- statická konfigurácia,
- DNS,
- registry API,
- cloud target group,
- Kubernetes EndpointSlices,
- xDS/control plane,
- autoscaling lifecycle eventy.

Discovery lifecycle:

```text
backend created
    ↓ registered/discovered
    ↓ readiness/health validation
    ↓ becomes eligible
    ↓ receives traffic
    ↓ draining
    ↓ removed from inventory
```

Riziká:

- stale endpoint,
- duplicate registration,
- endpoint dostupný skôr než ready,
- removal delay,
- control-plane outage,
- rozdiel medzi desired a effective target set.

## 10. Eligibility

Nie každý známy backend je okamžite vhodný na výber.

Eligibility môže závisieť od:

- readiness,
- active health,
- passive health,
- zone availability,
- weight väčší než nula,
- maintenance alebo drain state,
- circuit breaker,
- capacity limit,
- protocol alebo tenant compatibility,
- rollout cohort.

Selection algorithm sa aplikuje až na eligible set. Ak je set prázdny, balancer musí mať explicitný failure model: fail closed, fallback pool, stale endpoint, maintenance response alebo queue.

## 11. Round robin

Round robin vyberá backendy postupne.

```text
A → B → C → A → B → C
```

Je vhodný, keď:

- backends majú podobnú kapacitu,
- requests majú podobnú cenu,
- selection je per-request alebo connections majú podobný profil.

Nerovnomerný výsledok vznikne, ak:

- jeden request trvá sekundy a iný milisekundy,
- connection nesie rôzny počet requestov,
- jeden backend je pomalší,
- sticky sessions narušia distribúciu.

Round robin rozdeľuje počet výberov, nie automaticky CPU alebo latency.

## 12. Weighted round robin

Backend dostane váhu podľa relatívnej kapacity alebo rollout policy.

```text
A weight 5
B weight 3
C weight 2
```

Váha môže reprezentovať:

- väčší instance size,
- viac workerov,
- canary percento,
- zonálnu kapacitu,
- dočasný slow start.

Váha nie je absolútna kapacitná rezervácia. Reálny traffic ovplyvňujú connection persistence, request cost, retries a affinity.

## 13. Least connections

Least-connections vyberie backend s najmenším počtom aktívnych connections.

Hodí sa pri dlhších transportných sessions, ak je connection count rozumný proxy pre load.

Slabé miesta:

- jedna connection môže byť idle a iná veľmi aktívna,
- HTTP/2 connection môže niesť stovky streams,
- backendy môžu mať rozdielnu kapacitu,
- race medzi distribuovanými balancermi,
- stale connection count.

Weighted least-connections kombinuje active count s kapacitnou váhou.

## 14. Least requests a concurrency-aware výber

L7 proxy môže používať počet rozpracovaných requests alebo streams.

To lepšie reprezentuje request concurrency než connection count, ale stále nepozná cenu jednotlivého requestu.

Dôležité signály:

- active requests,
- queue depth,
- recent service time,
- backend concurrency limit,
- rejection rate.

Algoritmus musí zabrániť tomu, aby jeden dočasne pomalý backend zostal navždy bez trafficu a nemal šancu preukázať recovery.

## 15. Latency-aware balancing

Balancer môže preferovať backend s nižšou observed latency.

Riziko feedback loopu:

```text
backend A má krátky spike
→ balancer odoberie traffic
→ B a C sa preťažia
→ ich latency rastie
→ traffic sa presúva späť
→ systém osciluje
```

Latency metric je oneskorená a ovplyvnená request mixom. Potrebné sú smoothing, minimum samples, hysteresis a capacity bounds.

## 16. Random a power of two choices

Random výber je jednoduchý a pri veľkom počte requestov môže byť dostatočne rovnomerný.

Power of two choices:

1. vyberie dva náhodné backendy,
2. porovná ich load signal,
3. zvolí menej zaťažený.

Dosahuje dobré rozdelenie bez globálneho zoradenia všetkých backendov a škáluje vo veľkých pools.

## 17. Hash-based balancing

Hash key môže byť:

- source IP,
- cookie,
- tenant ID,
- object key,
- URL,
- explicitný shard key.

Výhoda je stabilnejšia affinity. Riziká:

- nerovnomerné key distribution,
- hot key,
- zmena backend count presunie keys,
- source-IP hash zoskupí veľa klientov za NATom,
- attacker môže manipulovať key.

Hash key musí byť stabilný, dôveryhodný a dostatočne rozložený.

## 18. Consistent hashing

Pri modulo hashingu:

```text
hash(key) mod N
```

zmena `N` presunie veľkú časť keys.

Consistent hashing minimalizuje remapping pri pridaní alebo odstránení backendu.

Použitie:

- distributed cache,
- shard ownership,
- sticky routing,
- locality pre stateful workload.

Na rovnomernosť sa používajú:

- virtual nodes,
- weighted tokens,
- bounded-load varianty,
- hot-key replication.

Consistent hashing nezaručuje dostupnosť dát. Pri odobratí backendu musí existovať recovery alebo replication model.

## 19. Maglev a rendezvous hashing

Ďalšie stabilné hashing modely môžu poskytovať:

- konzistentné mapovanie naprieč balancermi,
- rýchly lookup,
- obmedzený remapping,
- jednoduchšie weighted varianty.

Konkrétny algoritmus je menej dôležitý než jeho vlastnosti:

- distribúcia,
- stabilita pri zmene membership,
- weight support,
- memory a computation cost,
- konzistencia medzi dataplane nodes.

## 20. Session affinity

Affinity smeruje súvisiaci traffic na rovnaký backend.

Mechanizmy:

- cookie,
- source IP,
- consistent hash,
- application session ID,
- transport flow state.

Výhody:

- lokálny session state,
- cache locality,
- jednoduchší legacy workload.

Nevýhody:

- nerovnomerný load,
- horší failover,
- pomalší scale-in,
- závislosť na konkrétnej instance,
- source-IP collision za NATom,
- stale affinity po backend removal.

Externalizovaný alebo replikovaný state znižuje potrebu sticky sessions, ale má vlastný latency a availability cost.

## 21. Cookie affinity a security

Balancer-generated cookie môže obsahovať opaque backend key. Musí byť:

- nefalšovateľná alebo validovaná,
- bezpečne scoped,
- primerane expirovaná,
- kompatibilná s failoverom,
- nesmie odhaľovať citlivú topológiu.

Ak klient môže zvoliť ľubovoľný backend ID, môže obísť rollout weights alebo cieliť na slabú instance.

## 22. Health check taxonomy

### TCP health

Overí, že port prijme connection. Neoverí aplikačnú pripravenosť.

### TLS health

Overí handshake, SNI, certificate alebo ALPN podľa konfigurácie.

### HTTP health

Overí path, status a prípadne response body.

### Protocol-specific health

Napríklad databázový ping, gRPC health alebo SMTP greeting.

### Deep health

Overí dependencies alebo business operáciu.

Health check má odpovedať na otázku „má backend prijímať nový traffic?“, nie „je celý svet dokonale zdravý?“

## 23. Liveness, readiness a startup

- Liveness — proces je schopný pokračovať alebo potrebuje restart.
- Readiness — backend má prijímať nový traffic.
- Startup — backend ešte inicializuje a nemá byť predčasne označený za chybný.

Load balancer potrebuje predovšetkým readiness.

Backend môže byť live, ale not ready počas:

- warm-up,
- dependency incidentu,
- drainingu,
- overloadu,
- maintenance.

## 24. Active a passive health

### Active health

Balancer posiela pravidelné probes.

Výhody:

- odhalí chybu aj bez client trafficu,
- konzistentný test,
- rýchly návrat po recovery.

Nevýhody:

- probe môže byť príliš plytká,
- veľký fleet vytvára health-check load,
- check source môže mať inú network path než klient.

### Passive health

Balancer vyhodnocuje reálne resets, timeouty a statusy.

Výhody:

- odráža skutočný traffic,
- odhalí request-specific failures.

Nevýhody:

- potrebuje klientský traffic,
- zlá request class môže označiť zdravý backend za chybný,
- môže reagovať až po používateľskom dopade.

Kombinácia poskytuje lepší obraz než jeden model.

## 25. Health thresholds a hysteresis

Jedno zlyhanie nemá typicky okamžite vyradiť backend.

Parametre:

- interval,
- timeout,
- unhealthy threshold,
- healthy threshold,
- cooldown,
- observation window,
- slow start.

Hysteresis zabraňuje flappingu:

```text
healthy
→ niekoľko po sebe idúcich failures
→ unhealthy
→ niekoľko po sebe idúcich successes
→ healthy
```

Príliš agresívny check môže vyradiť veľa backendov pri krátkom latency spike a preťažiť zvyšok poolu.

## 26. Outlier detection a ejection

Passive health môže dočasne ejectnúť backend s výrazne horším správaním než peers.

Signály:

- consecutive errors,
- success-rate deviation,
- latency outlier,
- reset rate.

Bez limitov môže outlier detection odstrániť príliš veľkú časť capacity. Potrebné sú:

- maximum ejection percentage,
- minimum request volume,
- ejection duration,
- postupný recovery.

## 27. Slow start

Nový alebo obnovený backend nemusí okamžite zvládnuť plný share trafficu.

Dôvody:

- cold caches,
- JIT warm-up,
- connection pools,
- lazy initialization,
- disk cache,
- autoscaling startup.

Slow start postupne zvyšuje effective weight:

```text
0 % → 10 % → 30 % → 60 % → 100 %
```

Bez slow startu môže backend po prvom health success dostať burst, preťažiť sa a znovu vypadnúť.

## 28. Connection draining

Pri odoberaní backendu:

```text
eligible
    ↓ mark draining
no new selections
    ↓
existing work continues
    ↓ active reaches zero alebo timeout
remove endpoint
```

Draining musí zohľadniť:

- HTTP requests,
- keep-alive connections,
- HTTP/2 streams,
- WebSockets,
- gRPC streams,
- databázové sessions,
- UDP pseudo-flows.

Bez drainingu vznikajú resets. Príliš dlhý drain spomaľuje deploy a môže blokovať scale-in.

## 29. Deregistration delay

Cloud alebo managed balancer môže po removal evente držať endpoint v draining stave definovaný čas.

Ak application shutdown grace period je kratšia než deregistration delay, backend sa vypne skôr než balancer prestane posielať traffic.

Ak je shutdown grace výrazne dlhší, rollout sa zbytočne spomalí.

Lifecycle timers musia byť koordinované:

```text
readiness removal
→ endpoint propagation
→ LB draining
→ application grace
→ process termination
```

## 30. Retry a backend reselection

Balancer môže pri failure vybrať iný backend.

Bezpečnosť retry závisí od:

- idempotency,
- či request body už bol odoslaný,
- či upstream mohol operáciu spracovať,
- response progress,
- retry budgetu,
- per-try timeoutu.

Retry na inom backende môže pomôcť pri instance-local failure, ale nepomôže pri shared dependency failure. Namiesto recovery môže znásobiť load.

## 31. Retry budget

Retry budget obmedzuje podiel extra trafficu.

Príklad:

```text
1000 original requests/s
retry budget 10 %
→ maximálne približne 100 retry attempts/s
```

Budget chráni capacity pre nové requests a zabraňuje nekonečnému retry amplification.

Retry ownership musí byť koordinovaný medzi klientom, edge proxy, service mesh a application library.

## 32. Queueing

Balancer môže queueovať request, keď:

- všetky backend connections sú obsadené,
- concurrency limit je dosiahnutý,
- backend ešte nie je dostupný,
- rate limit riadi burst.

Queue absorbuje krátky burst, ale nezvýši service rate.

```text
arrival rate > backend throughput
→ queue rastie
→ latency rastie
→ timeouty
→ retries
→ ešte väčší arrival rate
```

Queue musí mať:

- maximálnu dĺžku,
- maximálny wait time,
- priority policy,
- rejection behavior,
- metrics.

## 33. Load shedding

Pri overload-e je často bezpečnejšie časť trafficu rýchlo odmietnuť než nechať všetko pomaly timeoutovať.

Možnosti:

- reject low-priority requests,
- obmedziť expensive endpoints,
- circuit breaker,
- concurrency limit,
- token bucket,
- serve stale cache,
- degrade optional functionality.

Load shedding potrebuje explicitnú business priority, nie náhodné zahadzovanie.

## 34. Circuit breaking

Circuit breaker obmedzí nové requests k backendu alebo clusteru pri zlyhaní.

Stavy:

```text
closed
→ failures exceed threshold
open
→ reject/fallback
half-open
→ limited probes
closed alebo open
```

Circuit breaker chráni caller resources a dependency pred retry stormom. Nesprávna konfigurácia môže vyradiť zdravú službu alebo maskovať dlhodobý incident.

## 35. Capacity-aware balancing

Backend capacity môže byť definovaná cez:

- statickú weight,
- max connections,
- max active requests,
- CPU alebo queue signal,
- explicitný admission-control token,
- autoscaling desired capacity.

Real-time utilization je noisy a oneskorená. Balancer má preferovať stabilné capacity bounds a lokálny concurrency signal pred chaotickým globálnym CPU feedbackom.

## 36. Autoscaling interakcia

Load balancer a autoscaler tvoria feedback loop.

```text
load rastie
→ queue/CPU rastie
→ autoscaler pridá backendy
→ startup a warm-up
→ LB ich začne používať
→ load per backend klesne
```

Riziká:

- health check pustí cold backend príliš skoro,
- scale-in odstráni backend bez drainingu,
- autoscaler reaguje na retry-generated load,
- metrika má dlhé oneskorenie,
- všetky backendy scaleujú súčasne a zaťažia dependency.

## 37. Cross-zone balancing

Cross-zone balancing môže distribuovať traffic cez viac availability zones.

Výhody:

- rovnomernejšie využitie celkovej capacity,
- jednoduchší failover pri nerovnomernom počte backendov.

Nevýhody:

- cross-zone latency,
- egress náklady,
- väčšie coupling medzi zones,
- data-locality alebo compliance problém.

Zonálny návrh musí určiť, či každá zone má samostatnú rezervnú capacity alebo sa spolieha na ostatné zones.

## 38. Multi-region balancing

Globálny traffic management môže používať:

- DNS,
- anycast,
- global proxy,
- client-side region selection.

Rozhodnutie zohľadňuje:

- latency,
- region health,
- data residency,
- session a state locality,
- capacity,
- cost,
- disaster-recovery policy.

Failover do druhého regiónu nie je úspešný, ak dáta, dependencies alebo credentials nie sú pripravené.

## 39. Anycast

Viac lokalít oznamuje rovnakú IP adresu cez routing.

```text
same frontend IP announced from region A, B, C
→ network vyberie topologicky preferovanú cestu
```

Anycast je routing selection, nie aplikačný health check.

Potrebné sú:

- route withdrawal pri failure,
- health-integrated control plane,
- state model kompatibilný so zmenou pathu,
- ochrana pred route leakom,
- region-local capacity.

Long-lived flow môže pri routing zmene skončiť v inom regione bez pôvodného connection state.

## 40. Source IP a identity

Balancer dataplane môže:

- zachovať source IP,
- SNATovať na balancer adresu,
- preniesť identity cez PROXY protocol,
- pridať HTTP forwarding headers.

Dôsledky:

- firewall policy backendu,
- audit,
- rate limiting,
- affinity,
- geolocation,
- abuse detection.

Source-IP hash je slabý pri veľa klientoch za NATom a pri IPv6 privacy adresách.

## 41. TLS a load balancing

Modely:

- TLS passthrough — backend vlastní certificate a TLS state,
- TLS termination — balancer vlastní edge certificate,
- re-encryption — balancer vytvorí TLS k backendu,
- mTLS — client alebo backend identity cez certificates.

TLS termination umožní L7 routing, ale balancer sa stáva critical security boundary.

SNI môže vybrať certificate alebo backend ešte pred HTTP requestom. ALPN môže rozlíšiť HTTP/1.1, HTTP/2 alebo iný protokol.

## 42. HTTP/2 a HTTP/3 vplyv

Pri HTTP/1.1 môže connection približne korelovať s request concurrency. Pri HTTP/2 a HTTP/3 jedna connection nesie veľa streams.

Dôsledky:

- least-connections môže byť zavádzajúci,
- long-lived connection fixuje traffic na jeden frontend alebo backend podľa architecture,
- multiplexing môže vytvoriť load skew,
- drain musí riešiť nové streams oddelene od connection close,
- per-request balancing môže vyžadovať proxy termination.

## 43. Stateful backends

Niektoré workloads majú lokálny state:

- in-memory session,
- websocket subscription,
- cache shard,
- game session,
- database transaction,
- file upload state.

Možné stratégie:

- affinity,
- externalized state,
- state replication,
- deterministic shard routing,
- reconnect/resume protocol.

Load balancer nemôže sám zabezpečiť state consistency.

## 44. Failure domains

Balancer má rozdeľovať traffic tak, aby neprekročil failure-domain cieľ.

Príklady:

- host,
- rack,
- zone,
- region,
- cloud provider,
- software version,
- dependency cluster.

Ak všetky backendy zdieľajú jednu databázu, balancing medzi nimi nechráni pred jej failure.

Capacity reserve musí existovať aj po strate plánovaného failure domainu.

## 45. Canary a weighted rollout

Canary routing pošle menší podiel trafficu na novú verziu.

```text
stable weight 95
canary weight 5
```

Treba kontrolovať:

- reálny request share, nie iba configured weight,
- affinity a connection persistence,
- request mix,
- error a latency confidence,
- rollback speed,
- shared dependency impact.

Pri L4 balancing môže 5 % nových connections viesť k inému podielu requestov, ak connections majú rozdielnu životnosť.

## 46. Shadow traffic

Balancer môže kopírovať request na testovací backend bez použitia jeho response.

Použitie:

- performance test novej verzie,
- compatibility validation,
- capacity profiling.

Riziká:

- duplicitné side effects,
- citlivé dáta,
- dvojnásobný downstream load,
- rozdielna timing a identity,
- test backend môže ovplyvniť shared dependency.

Shadow traffic musí byť read-only alebo bezpečne izolovaný.

## 47. Observability

Sleduj selection, health, capacity a outcome.

### Inventory

- discovered endpoints,
- eligible endpoints,
- healthy/unhealthy/draining count,
- endpoint age a version,
- zone/region distribution.

### Selection

- requests/connections per backend,
- configured a effective weight,
- selection skew,
- affinity key distribution,
- hash remapping.

### Capacity

- active requests/connections,
- queue depth a wait time,
- backend concurrency limit,
- rejected/load-shed traffic,
- balancer CPU, memory a socket pressure.

### Health

- active probe result a latency,
- passive errors,
- ejection events,
- recovery duration,
- flapping count.

### Outcome

- backend latency a error rate,
- retries,
- resets,
- client-visible status,
- drain duration,
- region/zone SLI.

## 48. Diagnostický postup

Časť requestov zlyháva.

1. Rozdeľ failures podľa frontend IP, regionu, zone, protocol family a balancer tieru.
2. Koreluj request ID s vybraným backendom.
3. Porovnaj healthy a eligible endpoint set.
4. Skontroluj health-check reason a čas prechodu state.
5. Porovnaj configured a effective weights.
6. Over selection granularity: connection alebo request.
7. Skontroluj affinity/hash key a distribution.
8. Porovnaj backend latency, errors, queue a capacity.
9. Skontroluj retries a retry amplification.
10. Over draining a deployment timeline.
11. Skontroluj DNS cache alebo endpoint discovery delay.
12. Over zone/region route a return path.
13. Po náprave over client-visible SLI a rovnomernosť distribúcie.

## 49. Typické symptómy

### Každý tretí request zlyhá

Jeden z troch backendov je chybný, ale stále eligible. Alternatívne môže zlyhávať jedna zone alebo hash partition.

### Nová verzia prijíma príliš veľa trafficu

Nesprávna effective weight, connection persistence, affinity, retry reselection alebo L4 connection granularity.

### Backend funguje priamo, ale balancer ho označuje unhealthy

Health path, Host header, SNI, source allowlist, certificate trust, timeout alebo response-body expectation.

### Po scale-in vznikajú resets

Chýbajúci drain, pomalá endpoint propagation alebo process skončil skôr než deregistration delay.

### Po incidente zostáva systém pomalý

Retry storm, dlhá queue, stale pooled connections, cold caches, circuit breaker half-open policy alebo pomalý autoscaling recovery.

### Jeden backend je preťažený, ostatné idle

Sticky session, hot key, long-lived multiplexed connection, nesprávny hash, rozdielna effective weight alebo discovery inconsistency.

### Health checks flappujú

Príliš krátky timeout, check závislý od nestabilnej dependency, chýbajúca hysteresis alebo samotné checks spôsobujú overload.

## 50. Časté omyly

### „Round robin rozdelí CPU load rovnomerne“

Nie. Rozdeľuje výbery, nie cenu práce.

### „Healthy port znamená zdravú aplikáciu“

TCP check dokazuje iba listener a transportnú cestu.

### „Sticky sessions riešia high availability“

Môžu failover zhoršiť, ak state nie je dostupný inde.

### „Viac retries zvyšuje spoľahlivosť“

Počas shared failure alebo overloadu zvyšujú load.

### „DNS TTL nula znamená okamžitý failover“

Nie. Resolver, application cache a existujúce connections môžu starý endpoint používať ďalej.

### „Least connections vždy vyberie najmenej zaťažený backend“

Connection count nemusí reprezentovať request alebo CPU load.

### „Load balancer vyrieši nedostatok capacity“

Nevyrieši. Môže iba queueovať, rejectovať alebo rozdeliť existujúcu capacity.

### „Health check má overiť všetky dependencies“

Príliš deep check môže pri shared dependency incidente vyradiť celý pool.

### „Weight 10 % znamená presne 10 % requestov“

Nie pri connection-level výbere, affinity, retries a malom sample size.

## 51. Kontrolné otázky

1. Čo je jednotka balancing rozhodnutia pri DNS, L4 a L7 modeli?
2. Aký je rozdiel medzi server-side a client-side load balancingom?
3. Prečo DNS balancing neposkytuje okamžitý per-request failover?
4. Aký je rozdiel medzi full proxy, NAT a direct-server-return dataplane?
5. Čo znamená endpoint eligibility?
6. Prečo round robin nemusí rovnomerne rozdeliť CPU load?
7. Kedy je least-connections vhodný a kedy zavádzajúci?
8. Aké riziko má latency-aware feedback loop?
9. Čo rieši consistent hashing a čo nerieši?
10. Aké riziká prináša source-IP affinity?
11. Aký je rozdiel medzi liveness, readiness a startup state?
12. Prečo active a passive health poskytujú odlišný dôkaz?
13. Načo slúži hysteresis pri health checks?
14. Čo je outlier ejection a prečo potrebuje limit?
15. Prečo nový backend potrebuje slow start?
16. Ako funguje draining a ktoré timers musia byť koordinované?
17. Kedy je retry na inom backende bezpečný?
18. Ako retry budget zabráni amplification?
19. Prečo queueing nevytvára capacity?
20. Kedy použiť load shedding?
21. Ako autoscaling a load balancing tvoria feedback loop?
22. Aké trade-offy má cross-zone balancing?
23. Prečo anycast nie je aplikačný health check?
24. Ako HTTP/2 multiplexing ovplyvňuje least-connections?
25. Prečo load balancing medzi stateless frontendmi nechráni pred shared database failure?
26. Ako overíš, že canary dostáva očakávaný traffic share?
27. Ktoré metriky potrebuješ na diagnostiku selection skew?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Proxy a reverse proxy](proxy-and-reverse-proxy.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: HTTP →](http.md)
<!-- KNOWLEDGE-NAVIGATION:END -->