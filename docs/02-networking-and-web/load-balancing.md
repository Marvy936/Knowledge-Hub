# Load balancing

Load balancing rozdeľuje connections alebo requests medzi viac eligible targets. Nie je to iba výber algoritmu. Zahŕňa backend inventory, health, readiness, capacity, selection, draining a feedback z reálnych outcomes.

L4 load balancer rozhoduje najmä podľa transportných fields a pracuje s TCP alebo UDP flows. L7 load balancer rozumie aplikačnému protokolu, typicky HTTP, a môže routovať podľa hostname, pathu, headers alebo cookies.

Backend môže byť configured, ale neeligible. Môže zlyhávať health check, byť v drain stave, mať nulovú weight alebo byť vyradený outlier detectionom. Runtime inventory je preto dôležitejší než samotný source configuration.

Bežné algoritmy:

```text
round robin
strieda eligible targets

least connections
uprednostní target s menším počtom aktívnych connections

weighted selection
zohľadní rozdielnu kapacitu

hash alebo affinity
viaže cohort na stabilný target
```

Algoritmus musí zodpovedať workloadu. Pri rozdielne dlhých requests nemusí round robin rozdeliť prácu rovnomerne. Pri HTTP/2 nemusí počet TCP connections zodpovedať počtu requestov.

Active health check vytvára umelý probe. Passive health sleduje reálne errors alebo latency. Plytký endpoint môže byť zelený, hoci business dependency nefunguje. Príliš hlboký health check môže pri shared dependency brownout-e vyradiť všetky backends a premeniť degradáciu na úplný outage.

Draining znamená zastaviť nové assignments a ponechať in-flight requests alebo long-lived connections dokončiť do definovaného deadline. Okamžité odstránenie môže resetnúť uploady alebo WebSockety; nekonečný drain blokuje rollout.

Session affinity môže pomôcť legacy stateful aplikácii, ale zhoršuje rebalancing a fault tolerance. Source-IP affinity za NAT-om môže poslať veľkú user cohortu na jediný backend.

Zelený VIP alebo jeden úspešný request nepreukazuje zdravie všetkých backend cohorts. Overenie potrebuje target identity, distribution, business outcome a správanie pri removal alebo recovery.

Atlas reverse proxy má dva backendy: `10.60.1.21:8080` a `10.60.1.22:8080`. Load balancing nie je iba algoritmus „round robin“. Je to lifecycle, ktorý udržiava inventory, rozhoduje o eligibility, vyberá target, sleduje health a capacity a bezpečne vyraďuje backend počas rollout-u.

```text
backend inventory
→ eligibility a health
→ selection
→ connection/request assignment
→ feedback o error, latency a capacity
→ draining alebo removal
```

## L4 a L7 rozhodnutie

L4 load balancer pracuje s transportnými fields a často forwarduje alebo proxyuje TCP/UDP bez pochopenia HTTP pathu. L7 load balancer ukončuje aplikačný protokol a môže routovať podľa hostname, path, headers alebo cookies.

L4 zachováva širšiu protocol transparentnosť a môže mať nižší overhead. L7 poskytuje bohatšie policy a observability, ale vytvára aplikačný trust boundary. Jeden produkt môže kombinovať oba režimy; treba pomenovať konkrétny listener.

## Inventory a eligibility

Backend môže byť registrovaný, ale neeligible. Dôvody zahŕňajú failing health, draining, circuit breaker, outlier ejection, zone policy alebo nulovú capacity weight.

Control plane môže ukázať dva configured backends, kým data plane používa iba jeden. Runtime stats sú preto dôležitejšie než source config pri otázke „kam sa requesty skutočne posielajú“.

HAProxy príklad:

```haproxy
backend orders
    balance roundrobin
    option httpchk GET /readyz
    http-check expect status 200
    server app1 10.60.1.21:8080 check
    server app2 10.60.1.22:8080 check
```

Health check potvrdzuje odpoveď konkrétneho endpointu z proxy pathu. Nepreukazuje business dependency ani user request s auth, payloadom a tenant contextom.

## Selection algorithms

Round robin strieda eligible targets. Least connections uprednostní backend s menším počtom aktívnych connections. Weighted varianty zohľadnia rozdielnu kapacitu. Hash-based selection môže poskytovať affinity podľa source, cookie alebo application key.

Algoritmus treba hodnotiť podľa workloadu. Pri veľmi rozdielnej dĺžke requests môže round robin rozdeliť počet requestov rovnomerne, ale nie prácu. Least connections môže reagovať na dlhé connections, no pri HTTP/2 multiplexingu počet connections nemusí zodpovedať request loadu.

## Health, readiness a passive feedback

Active health check pravidelne vytvára probe. Passive health sleduje reálne errors, resets alebo latency. Oba môžu klamať iným spôsobom.

Príliš plytký `/healthz` odpovedá `200`, hoci backend nemá DB connection. Príliš hlboký check môže pri dependency brownout-e vyradiť všetky backends a zmeniť degraded service na úplný outage. Readiness contract má odrážať schopnosť obslúžiť routing cohort bez vytvorenia synchronizovaného failure.

## Draining

Pri deploymente sa backend najprv prestane vyberať pre nové requests a existujúce connections alebo in-flight requests dostanú čas dokončiť. Až potom sa process ukončí.

```text
eligible
→ drain requested
→ no new assignments
→ in-flight count klesne
→ connection deadline
→ backend removed
```

Okamžité odstránenie môže resetnúť WebSockety, uploady alebo payment requests. Nekonečný drain zase blokuje rollout. Potrebný je maximum connection age a application shutdown contract.

## Session affinity

Affinity drží klienta alebo session na rovnakom backend-e. Môže pomôcť pri lokálnom cache alebo legacy session state, ale zhoršuje rebalancing a recovery. Ak state musí prežiť backend failure, má byť v zdieľanom alebo replikovanom systéme, nie chránený iba cookie stickiness.

Source-IP affinity za NAT-om môže poslať tisíce users na jeden backend. Cookie affinity musí mať integrity a lifecycle policy a nesmie obísť authorization.

## Global a local balancing

DNS môže rozdeľovať clients medzi regióny, L4 balancer medzi nodes a L7 proxy medzi application instances. Každá vrstva má vlastný health a cache interval. Region môže byť odstránený z DNS, ale clients so starým answerom a existujúcimi connections ho stále používajú.

Recovery preto potrebuje transition plan cez všetky balancing layers, nie iba zmenu jedného poolu.

## Incident: každý druhý request zlyhá

Po deploymente Atlas vidí približne 50 % error rate. DNS aj edge sú stabilné. Runtime LB stats ukážu dva eligible backends; `app2` vracia `503` na business request, ale `/healthz` stále `200`.

Round robin vytvára pravidelný pattern. Containment vyradí `app2` a zachová capacity. Root cause je chybná configuration generation, ktorú health check neoveroval. Oprava pridá readiness kontrolu loaded configu a release-aware backend metadata. Po návrate sa overí rovnomerné rozdelenie aj business outcome na oboch targets.

## Zhrnutie

Load balancing je control loop nad backend inventory a request assignmentom. Algoritmus je iba jedna časť. Health depth, eligibility, capacity, draining, affinity a viac vrstiev balancingu určujú dostupnosť. Zelený VIP nepreukazuje zdravie každého backend cohortu.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Proxy a reverse proxy](proxy-and-reverse-proxy.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: HTTP →](http.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
