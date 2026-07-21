# Route 53 a CloudFront

Amazon Route 53 poskytuje authoritative DNS, domain registration, health checks a DNS-based traffic steering. Amazon CloudFront poskytuje global edge delivery a caching pred origins. Spolu často tvoria verejný vstup aplikácie:

```text
user DNS query
→ Route 53 alias
→ CloudFront edge
→ cache behavior
→ origin request
→ ALB / S3 / API / custom origin
```

DNS, CDN a origin sú samostatné failure domains. Chyba v jednej vrstve sa nemá diagnostikovať zmenami vo všetkých troch naraz.

## 1. Route 53 capability model

Route 53 zahŕňa:

- domain registration,
- public hosted zones,
- private hosted zones,
- authoritative DNS records,
- routing policies,
- health checks,
- Route 53 Resolver pre hybrid DNS,
- DNSSEC capabilities podľa public/private use case.

Route 53 nie je general-purpose load balancer na úrovni jednotlivých TCP connections. DNS resolver cache a TTL znamenajú, že zmena odpovede nemusí okamžite presunúť všetkých clients.

## 2. Hosted zones

Hosted zone je container pre DNS records konkrétneho namespace-u.

### Public hosted zone

Authoritative records dostupné cez verejný DNS.

### Private hosted zone

Records dostupné pre asociované VPCs podľa Route 53 Resolver a association modelu.

Hosted zone a registered domain nie sú to isté. Domain registrar deleguje namespace cez NS records na authoritative name servers hosted zone-u.

## 3. DNS delegation

Pre domain `example.com` registrar parent zóne publikuje NS records Route 53 hosted zone-u.

Pri subdomain delegation:

```text
parent: example.com
child:  dev.example.com
```

parent zone musí obsahovať NS records child zone-u.

Častý incident:

- nová hosted zone existuje,
- records sú správne,
- registrar stále deleguje na staré name servers.

Vždy over chain:

```bash
dig +trace example.com
dig NS example.com
dig A app.example.com
```

## 4. Record types

Bežné records:

- `A` — IPv4,
- `AAAA` — IPv6,
- `CNAME` — alias na iný DNS name mimo zone apex obmedzení,
- `MX` — mail exchange,
- `TXT` — verification/policy text,
- `NS` — delegation,
- `SOA` — zone authority metadata,
- `CAA` — povolené certificate authorities,
- `SRV` — service location,
- Route 53 **alias** record pre podporované AWS resources.

## 5. Alias vs CNAME

Route 53 alias je AWS-specific extension.

Výhody aliasu:

- môže byť použitý na zone apex,
- smeruje na podporované AWS resources, napríklad CloudFront alebo load balancer,
- môže použiť `EvaluateTargetHealth` pri podporovanom targete,
- Route 53 vracia výslednú hodnotu namiesto bežného CNAME chainu.

CNAME nemožno štandardne použiť na zone apex, pretože apex musí zároveň obsahovať SOA/NS records.

Alias nie je univerzálny pointer na ľubovoľný hostname; target types sú definované Route 53.

## 6. TTL

TTL určuje, ako dlho resolver cache-uje record response.

Nízky TTL:

- rýchlejšia zmena/failover pre nové queries,
- viac DNS queries,
- stále nezruší existujúce TCP/TLS connections,
- recursive resolver môže mať vlastné behavior hranice.

Vysoký TTL:

- nižší query volume,
- pomalšia propagation zmeny.

Pred plánovanou migráciou zníž TTL s dostatočným predstihom. Zníženie v momente cutover-u nepomôže resolverom, ktoré už cache-ujú starú hodnotu s pôvodným TTL.

## 7. Routing policies

### Simple

Jedna alebo viac hodnôt bez advanced steeringu.

### Weighted

Rozdeľuje DNS odpovede podľa relatívnych weights.

Použitie:

- canary traffic,
- migration,
- postupný shift,
- active-active distribution.

Weight nie je presný request-level percentuálny load balancer. DNS caching a client concentration môžu vytvoriť odchýlku.

### Latency

Vyberá AWS Region/resource, ktorý má podľa Route 53 measurements najnižšiu latency pre resolver/client path.

Nie je to real-time application latency ani guarantee najrýchlejšej odpovede.

### Failover

Primary/secondary active-passive routing podľa health.

### Geolocation

Routing podľa geografickej location DNS query source modelu.

### Geoproximity

Routing podľa proximity k resources a optional bias.

### Multivalue answer

Vracia viac healthy records, typicky do ôsmich podľa aktuálneho service contractu.

Nie je náhradou ELB; poskytuje DNS-level distribution a health filtering.

### IP-based

Routing podľa configured client CIDR collections.

## 8. Route 53 health checks

Health check môže sledovať:

- endpoint cez HTTP/HTTPS/TCP,
- CloudWatch alarm,
- calculated health z ďalších checks.

Dôležité:

- health checker musí vedieť endpoint dosiahnuť,
- Host header/path/port musia sedieť,
- firewall musí povoliť health-check source ranges podľa modelu,
- checking record name cez rovnaký failover record môže vytvoriť recursive alebo nepredvídateľný design,
- health check nie je application transaction test automaticky.

Pre alias na AWS resource môže `EvaluateTargetHealth` použiť health targetu podľa podporovanej integrácie.

## 9. DNS failover semantics

Active-passive failover:

```text
primary healthy → Route 53 vracia primary
primary unhealthy → Route 53 vracia secondary
```

Skutočný recovery time zahŕňa:

- health detection interval/threshold,
- DNS authoritative update,
- resolver/client TTL cache,
- connection retry,
- secondary capacity/readiness,
- state/data failover.

DNS failover nemôže opraviť databázový split-brain alebo nepripravenú secondary application.

## 10. Private DNS

Private hosted zone môže poskytovať internal names pre VPCs.

Over:

- VPC DNS support/hostnames settings,
- zone-VPC association,
- account/Region association authorization pri cross-account modeli,
- overlapping private zones,
- resolver rules a forwarding,
- split-horizon behavior.

Rovnaký name môže mať inú public a private odpoveď. Troubleshooting musí vykonať query z reálneho client network contextu.

## 11. Route 53 Resolver

VPC používa Route 53 Resolver pre recursive DNS.

Hybrid DNS používa:

- inbound Resolver endpoints — on-premises clients sa pýtajú AWS private zones,
- outbound Resolver endpoints — VPC queries sa forwardujú do on-premises DNS,
- Resolver rules — domains a target DNS servers,
- rule sharing cez AWS RAM podľa governance modelu.

Endpointy používajú ENIs v subnets. Potrebujú:

- viac AZ pre HA,
- Security Groups,
- route/connectivity,
- capacity/QPS monitoring,
- redundant on-premises DNS targets.

Forwarding loop môže vzniknúť, keď AWS forwarduje domain on-premises a on-premises ho pošle späť do AWS.

## 12. DNSSEC

DNSSEC chráni authenticity/integrity DNS odpovedí pomocou signatures a chain of trust.

Operational requirements:

- key-signing key a KMS dependency podľa service modelu,
- DS record v parent zone/registrar,
- rotation a monitoring,
- bezpečný disable proces.

Chybný DS record môže spôsobiť `SERVFAIL` validujúcim resolverom aj keď records vyzerajú správne pri non-validating teste.

DNSSEC nezašifruje DNS query ani nezabezpečí application TLS.

## 13. CloudFront mentálny model

CloudFront distribution obsahuje:

- viewer-facing domain a TLS configuration,
- origins,
- origin groups,
- default cache behavior,
- additional ordered cache behaviors,
- cache policy,
- origin request policy,
- response headers policy,
- logging, security a edge-compute integrations.

Request flow:

```text
viewer request
→ nearest/selected edge
→ cache key lookup
→ cache hit: response
→ cache miss: origin request
→ cache response podľa policy
```

## 14. Origins

Origin môže byť napríklad:

- S3 bucket origin,
- Application Load Balancer,
- API endpoint,
- EC2/custom HTTP server,
- MediaStore/MediaPackage alebo ďalší supported service,
- VPC origin pri podporovanom private-resource modeli.

Origin contract obsahuje:

- origin domain,
- protocol policy,
- origin path,
- custom headers,
- connection attempts/timeouts,
- Origin Shield,
- origin access control pri S3.

Origin domain nemá smerovať späť na rovnakú CloudFront distribution, inak môže vzniknúť loop.

## 15. Cache behaviors

Distribution má jeden default cache behavior a môže mať ďalšie path-pattern behaviors.

Príklad:

```text
/static/* → S3 origin, long TTL
/api/*    → ALB origin, caching disabled/minimal
*         → default application origin
```

Behavior určuje:

- path pattern,
- origin,
- allowed/cached methods,
- viewer protocol policy,
- cache policy,
- origin request policy,
- response headers policy,
- signed URL/cookie requirement,
- edge function associations.

Additional behaviors sa vyhodnocujú podľa precedence. Chybný path pattern môže poslať API request do static originu.

## 16. Cache key

Cache key určuje, ktoré viewer requests zdieľajú cached object.

Môže obsahovať:

- path,
- query strings,
- selected headers,
- cookies,
- compression variant.

Príliš široký cache key:

- nízky cache hit ratio,
- veľa origin requests,
- vyšší cost/latency.

Príliš úzky cache key:

- nesprávne zdieľanie personalized alebo language/device response,
- data leakage medzi users.

Do cache key pridávaj iba hodnoty, ktoré reálne menia response representation.

## 17. Cache policy vs origin request policy

### Cache policy

Určuje:

- cache key values,
- minimum/default/maximum TTL,
- compression settings.

Values zahrnuté v cache key sa zároveň posielajú originu.

### Origin request policy

Posiela originu ďalšie headers, cookies alebo query strings, ktoré nemajú byť súčasťou cache key.

Príklad:

- `Authorization` alebo viewer metadata môže byť potrebná originu,
- ale caching authenticated content musí mať explicitný bezpečnostný design.

Nesprávne preposlanie `Host` headera môže poškodiť origin virtual-host routing alebo TLS.

## 18. TTL a origin headers

CloudFront caching ovplyvňujú:

- cache policy TTL,
- origin `Cache-Control`,
- origin `Expires`,
- minimum/maximum TTL,
- error caching TTL.

Pri mutable assetoch používaj versioned filenames:

```text
app.7f23a1.js
```

Namiesto častých invalidations rovnakého key. Versioned names zlepšujú rollback a immutable caching.

## 19. Invalidations

Invalidation odstráni matching objects z edge caches pred TTL expiration.

Použitie:

- urgentný security fix,
- chybný mutable content,
- migration.

Riziká:

- cost po free allowance,
- propagation time,
- wildcard blast radius,
- origin load spike po cache missoch.

Invalidation neopraví chybný origin object ani browser/downstream cache automaticky.

## 20. S3 origin access

Pre private S3 origin používaj Origin Access Control — OAC — podľa aktuálneho odporúčaného modelu.

OAC umožňuje CloudFront podpisovať origin requests cez SigV4 a bucket policy povoľuje konkrétnu distribution/service principal path.

Odlišuj:

- S3 REST endpoint origin — podporuje private origin access,
- S3 static website endpoint — custom origin, verejný website behavior a odlišný TLS/access model.

Neotváraj bucket public iba preto, že CloudFront dostáva `403`. Over OAC, bucket policy, KMS a object key.

## 21. Origin Shield

Origin Shield pridáva regionálnu caching vrstvu pred originom.

Výhody:

- menej duplicate origin fetches z viacerých edge locations,
- lepšia cache consolidation,
- ochrana originu pri miss bursts.

Trade-offy:

- additional request/transfer cost,
- výber Shield Regionu,
- nie je náhrada origin HA.

## 22. Origin groups a failover

Origin group definuje primary a secondary origin a failover criteria podľa supported HTTP status codes.

Vhodné pre:

- static/content origin failover,
- read-only recovery,
- degraded fallback.

Limit:

- failover nemusí fungovať pre všetky HTTP methods,
- writes a state consistency potrebujú application-specific design,
- cached errors/objects môžu ovplyvniť observation,
- secondary musí mať synchronizované content a permissions.

## 23. Viewer TLS

CloudFront môže používať:

- default CloudFront certificate pre distribution hostname,
- ACM certificate pre alternate domain names.

Pre CloudFront viewer certificate sa ACM certificate spravuje v required control Region podľa služby, typicky `us-east-1`.

Over:

- alternate domain names/SAN,
- Route 53 alias,
- certificate Region/status,
- TLS security policy,
- SNI/client compatibility,
- DNS validation records.

Certificate v `eu-central-1` vhodný pre ALB nie je automaticky použiteľný pre CloudFront.

## 24. Origin TLS

Pri HTTPS custom origin CloudFront overuje origin certificate a hostname podľa origin domain/configuration.

`502` môže vzniknúť pre:

- expired origin certificate,
- hostname mismatch,
- incomplete chain,
- unsupported protocol/cipher,
- origin reset/timeout.

Viewer TLS môže byť healthy, aj keď edge-to-origin TLS zlyháva.

## 25. AWS WAF a Shield

CloudFront možno integrovať s AWS WAF pre Layer 7 rules:

- managed rule groups,
- IP sets,
- rate-based rules,
- bot/application protections podľa configuration.

AWS Shield Standard poskytuje baseline DDoS protection pre supported services; Shield Advanced pridáva ďalšie capabilities a cost/support model.

WAF rule môže blokovať legitímny traffic. Zachovaj sampled requests/logs a používaj count mode alebo staged rollout pri nových rules.

## 26. Signed URLs a signed cookies

Používajú sa na private content distribution.

- signed URL — jednotlivý resource/request,
- signed cookie — skupina resources/pathov.

Trust model môže používať key groups/public keys.

Nespoliehaj sa iba na obscurity URL. Definuj expiry, path/IP constraints podľa use case a key rotation.

## 27. CloudFront Functions a Lambda@Edge

### CloudFront Functions

Lightweight JavaScript na viewer request/response events s veľmi nízkou latency a obmedzeným runtime modelom.

Use cases:

- redirects,
- URL normalization,
- header manipulation,
- jednoduché authorization/routing decisions.

### Lambda@Edge

Rozšírenejší runtime na viewer/origin events podľa supported Regions/runtime restrictions.

Use cases:

- complex request transformation,
- dynamic origin selection,
- advanced authentication/customization.

Edge code zväčšuje deployment a debugging surface. Versioning, replication time, logs Region a rollback musia byť explicitné.

## 28. Response headers policy

Môže pridávať alebo riadiť:

- CORS headers,
- security headers,
- custom headers,
- header removal podľa supported configuration.

Security headers nepomôžu, ak nesprávny cache key zdieľa private content.

## 29. CloudFront logging a metrics

Observability môže obsahovať:

- standard access logs,
- real-time logs,
- CloudWatch distribution metrics,
- origin logs,
- WAF logs,
- CloudTrail configuration changes,
- cache statistics.

Sleduj:

- requests/bytes,
- total/4xx/5xx error rate,
- cache hit rate,
- origin latency,
- status code distribution,
- edge location a result type,
- invalidation/deployment changes.

CloudFront access log delivery nie je vždy instantné. Pre incident koreluj edge request IDs a origin request IDs.

## 30. Cache status a headers

Relevantné response headers môžu zahŕňať:

- `X-Cache`,
- `Age`,
- `Via`,
- `X-Amz-Cf-Pop`,
- `X-Amz-Cf-Id`.

Príklad:

```bash
curl -I https://cdn.example.com/static/app.js
```

Prvý request môže byť miss, ďalší hit. Výsledok závisí od cache key, edge location a TTL.

## 31. Route 53 + CloudFront integration

Bežný pattern:

```text
Route 53 A/AAAA alias
→ CloudFront distribution
→ S3/ALB origins
```

Alias na CloudFront potrebuje:

- alternate domain name v distribution,
- matching certificate,
- distribution deployed,
- správny hosted zone record.

DNS môže ukazovať na distribution, ale CloudFront vráti `403`, ak requested Host nie je configured alternate domain alebo origin access zlyhá.

## 32. Route 53 troubleshooting

### `NXDOMAIN`

Over:

- record existuje v správnej hosted zone,
- delegation NS,
- exact name/type,
- private vs public context,
- negative caching TTL.

### `SERVFAIL`

Over:

- DNSSEC chain/DS,
- authoritative server availability,
- forwarding loop,
- resolver validation.

### Stará IP/target

Over:

- authoritative response,
- recursive resolver cache,
- client/application DNS cache,
- TTL pred zmenou,
- split-horizon zone.

### Failover neprepne

Over:

- health check status,
- record association,
- `EvaluateTargetHealth`,
- TTL/cache,
- secondary health/capacity,
- calculated check dependencies.

## 33. CloudFront `403`

Možné príčiny:

- S3 bucket policy/OAC,
- object neexistuje a S3 access model maskuje 404 ako 403,
- alternate domain/CNAME mismatch,
- WAF block,
- signed URL/cookie invalid,
- geo restriction,
- origin custom authorization,
- KMS permission.

Postup:

```text
viewer response headers/request ID
→ WAF/logs
→ behavior/origin mapping
→ direct controlled origin test
→ OAC/bucket/KMS policy
→ object key/case
```

## 34. CloudFront `404`

Over:

- requested path,
- origin path prefix,
- behavior mapping,
- S3 object key case,
- default root object,
- application route,
- cached error response.

Invalidation môže byť potrebná až po oprave origin content alebo behavioru.

## 35. CloudFront `502`

Over:

- origin DNS,
- origin TLS certificate/hostname/chain,
- origin protocol policy,
- Security Groups/NACL,
- origin listening port,
- Lambda@Edge failure,
- malformed origin response.

## 36. CloudFront `503/504`

### 503

- origin overload/unavailable,
- edge compute quota/error,
- capacity alebo custom origin failure.

### 504

- origin response timeout,
- network path drop,
- long application request,
- dependency latency.

CloudFront timeout zvýš až po pochopení application latency a client expectation. Dlhší timeout môže iba predĺžiť resource occupancy.

## 37. Cache poisoning a privacy risks

Nesprávny cache key môže zdieľať response medzi users.

Rizikové inputs:

- `Authorization`,
- session cookies,
- tenant headers,
- language/device headers,
- query parameters ovplyvňujúce obsah.

Pre authenticated dynamic content často caching vypni alebo navrhni presný identity-aware key bez ukladania citlivých responses na shared edge.

Origin request headers, ktoré nie sú v cache key, nesmú meniť response content, ak sa response cache-uje.

## 38. Deployment a propagation

CloudFront distribution change sa propaguje do global edge network a nie je okamžitá.

Deployment workflow:

- validate configuration,
- staged/test distribution alebo continuous deployment capability podľa use case,
- monitor status `InProgress`/`Deployed`,
- test alternate domain a origins,
- verify logs/metrics,
- rollback previous configuration.

DNS cutover na distribution urob až po deployment a certificate/origin validation.

## 39. Cost model

### Route 53

- hosted zones,
- DNS queries podľa routing type,
- health checks,
- Resolver endpoints a queries,
- domains.

### CloudFront

- data transfer to viewers,
- HTTP/HTTPS requests,
- invalidations nad allowance,
- real-time logs,
- Origin Shield,
- edge functions,
- WAF/Shield,
- origin data transfer/request cost.

Vyšší cache hit ratio typicky znižuje origin load a latency, ale nesmie narušiť correctness alebo privacy.

## 40. SOA-C03 mapovanie

- **Domain 1** — DNS/CloudFront metrics, access logs, cache hit/error analysis,
- **Domain 2** — Route 53 health failover, CloudFront origin failover a global recovery,
- **Domain 3** — DNS/distribution provisioning, cache policies, invalidation a deployment automation,
- **Domain 4** — DNSSEC, TLS, OAC, signed content, WAF a logging security,
- **Domain 5** — hosted zones, routing policies, Resolver, CDN/origin networking a troubleshooting.

Praktické drilly:

- Route 53 wrong delegation,
- private hosted zone neasociovaná s VPC,
- failover health check sleduje nesprávny hostname,
- CloudFront OAC bucket policy `403`,
- cache key zdieľa tenant response,
- origin TLS `502`,
- path behavior posiela request na nesprávny origin,
- stale cached error po oprave originu.

## 41. Anti-patterny

### DNS failover považovaný za okamžitý

TTL, resolver cache a connections predlžujú recovery.

### Weighted routing považované za presné request percentá

DNS caching skresľuje distribution.

### Health check na rovnaký failover hostname

Môže testovať už presmerovaný endpoint a vytvoriť nejasný result.

### Public S3 bucket kvôli CloudFront

OAC umožňuje private origin access.

### Všetky headers/cookies/query strings v cache key

Znižuje hit ratio a zvyšuje cost.

### Authenticated content cache-ované bez identity contractu

Hrozí data leakage.

### Invalidation ako bežný release mechanizmus

Preferuj immutable versioned asset names.

### CloudFront považovaný za origin HA

Origin a state stále potrebujú resilience.

## 42. Kontrolné otázky

1. Aký je rozdiel medzi hosted zone, domain registration a recordom?
2. Kedy použiť Route 53 alias namiesto CNAME?
3. Ako TTL ovplyvňuje failover?
4. Ako sa líši weighted, latency a failover routing?
5. Čo je Route 53 Resolver inbound a outbound endpoint?
6. Čo určuje CloudFront cache behavior?
7. Ako sa líši cache policy a origin request policy?
8. Prečo je cache key security boundary?
9. Ako funguje OAC pre S3 origin?
10. Ktoré vrstvy preveríš pri CloudFront `502`?

## Glossary impact

Relevantné pojmy: Amazon Route 53, hosted zone, DNS delegation, alias record, routing policy, weighted routing, latency routing, failover routing, Route 53 health check, Route 53 Resolver, inbound Resolver endpoint, outbound Resolver endpoint, DNSSEC, Amazon CloudFront, distribution, edge location, origin, cache behavior, cache policy, origin request policy, response headers policy, cache key, cache hit ratio, invalidation, Origin Access Control, Origin Shield, origin group, signed URL, signed cookie, CloudFront Functions a Lambda@Edge.

## Oficiálna dokumentácia

- [Amazon Route 53 Developer Guide](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html)
- [Route 53 concepts](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/route-53-concepts.html)
- [Choosing a routing policy](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html)
- [Route 53 health checks](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover.html)
- [Route 53 Resolver](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver.html)
- [Amazon CloudFront Developer Guide](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html)
- [Cache policies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-the-cache-key.html)
- [Origin request policies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-origin-requests.html)
- [Restricting access to S3 origins](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html)
