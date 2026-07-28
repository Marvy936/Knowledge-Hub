# Route 53 a CloudFront

Amazon Route 53 rozhoduje, ktoré DNS odpovede dostane resolver pre konkrétne meno, typ a routing/health state. Amazon CloudFront po DNS resolution ukončí viewer connection na global edge dataplane-e, vyberie cache behavior, vytvorí cache key a pri cache miss-e vytvorí origin request. DNS steering a CDN caching sú preto dva odlišné decision systems:

```text
DNS query subject
→ authoritative Route 53 verdict
→ resolver/client cache
→ CloudFront viewer endpoint
→ viewer TLS a request normalization
→ ordered cache-behavior verdict
→ cache-key identity
→ cache hit alebo origin request
→ origin authorization a response
→ cache/response publication
→ application business outcome
```

Route 53 nepresúva otvorené connections a CloudFront cache nie je iba performance layer. TTL, cache key, minimum TTL, origin request policy, error caching a deployment propagation priamo ovplyvňujú correctness, privacy, availability a recovery.

## 1. Exact edge-delivery subject

Atlas Payments používa edge subject `EDGE-PAY-42`:

```text
public namespace = example.com
hosted zone = HZ-EXAMPLE-17
delegation generation = DNS-NS-8
record = pay.example.com A/AAAA alias
record generation = DNS-REC-31

CloudFront distribution = D-PAY-17
alternate domain = pay.example.com
distribution generation = CF-44
viewer certificate generation = CERT-CF-12
viewer TLS policy generation = TLS-CF-8

ordered behaviors =
  /assets/*
    → S3 origin atlas-pay-assets-prod
    → OAC generation OAC-7
    → cache policy ASSET-CACHE-19

  /api/payments/*
    → ALB origin alb-pay-public-17
    → cache policy API-NOCACHE-9
    → origin request policy API-ORIGIN-14

  default
    → portal origin
    → cache policy PORTAL-CACHE-21

payment status request =
  GET /api/payments/P-884
  Host = pay.example.com
  Authorization = Bearer <tenant token>
  X-Tenant-ID = tenant-a

business outcome =
  tenant-a receives only its own payment P-884 representation

forbidden outcomes =
  tenant-b receives a cached tenant-a response
  stale DNS or cache state is declared recovered without client verification
  private S3 origin becomes public to fix CloudFront 403
  API request is routed to static origin alebo cached despite no-cache contract
  origin failover accepts writes against unsynchronized secondary
  invalid DNSSEC/delegation change creates SERVFAIL
```

Incident identity musí zachovať queried name/type, resolver context, authoritative answer, TTL, distribution/config ETag/generation, edge request ID/POP, matched behavior, cache key inputs, `X-Cache`/`Age`, origin identity, CloudFront/origin status, tenant/auth subject a business object ID.

## 2. DNS resolution je cached authority chain

Public DNS query pre `pay.example.com` prechádza približne:

```text
client stub resolver
→ recursive resolver cache
→ root delegation
→ TLD delegation
→ example.com authoritative Route 53 name servers
→ record/routing/health verdict
→ cached response according to TTL
```

Hosted zone je authoritative record container; domain registration a parent delegation sú samostatné. Nová hosted zone môže obsahovať správne records a byť úplne neviditeľná, ak registrar/parent stále deleguje na staré name servers.

Subdomain delegation potrebuje NS records v parent zone. Pri incidente sa porovná parent delegation, hosted-zone assigned NS set, DNSSEC DS chain a queried record. Query iba na jeden chosen authoritative server môže maskovať delegation alebo propagation problém.

## 3. Record identity a alias

Bežné records zahŕňajú `A`, `AAAA`, `CNAME`, `MX`, `TXT`, `NS`, `SOA`, `CAA` a `SRV`. Route 53 alias je AWS-specific record, ktorý môže smerovať zone apex aj subdomain na podporované AWS resources, napríklad CloudFront alebo ELB.

Alias nie je general CNAME syntax. Target type a health integration sú service-specific. Alias na CloudFront distribution vyžaduje:

```text
alternate domain name in distribution
+ matching viewer certificate
+ distribution deployed
+ Route 53 alias A and optionally AAAA
```

CloudFront alias target nepodporuje `EvaluateTargetHealth` rovnakým spôsobom ako niektoré regional AWS alias targets. Multi-distribution DNS failover preto potrebuje explicitný supported health-check/control design; nemožno predpokladať health propagation iba z alias checkboxu.

CNAME sa štandardne nepoužíva na zone apex, pretože apex musí obsahovať SOA/NS. Hard-coded resolved CloudFront alebo ELB IP obchádza DNS service identity a je nesprávny recovery contract.

## 4. TTL je migration a recovery parameter

TTL určuje, ako dlho recursive resolver/client môže používať response. Nízky TTL znižuje maximum intended cache duration pre nové queries, ale:

- nezruší existing TCP/TLS/HTTP connections;
- neovláda všetky application DNS caches;
- nepomôže resolveru, ktorý už cache-uje starú odpoveď s pôvodným vysokým TTL;
- zvyšuje authoritative query volume.

Pred plánovaným cutover-om sa TTL zníži skôr než starý TTL interval uplynie. Po cutover-e sa sledujú authoritative answers, multiple recursive resolvers, actual client connections a origin/business traffic. „Route 53 record je updated“ je control-plane state, nie client migration verdict.

Negative responses majú vlastný caching behavior odvodený aj zo SOA settings. Po oprave chýbajúceho recordu môže časť clients stále dostávať cached `NXDOMAIN`.

## 5. Routing policy je DNS-answer algorithm

### Simple

Vracia configured value/values bez health-aware advanced steeringu.

### Weighted

Vyberá record podľa relatívnych weights. Je vhodný pre DNS-level migration alebo active-active distribution, ale nie je presné request percentage:

```text
resolver receives one answer
→ caches it
→ many clients/requests reuse same answer
```

Malý počet veľkých resolvers môže výrazne skresliť traffic distribution. Weighted DNS canary potrebuje request-level observability na targets, nie iba record weights.

### Latency

Vyberá AWS Region/resource podľa Route 53 latency measurements pre query source model. Nejde o real-time application p95 ani záruku najrýchlejšieho business response.

### Failover

Primary/secondary routing podľa health. Reálny RTO zahŕňa health detection, authoritative verdict, resolver/client TTL, reconnect a secondary data/capacity readiness.

### Geolocation, geoproximity a IP-based

Routujú podľa geographic alebo configured source cohort modelu. Potrebujú default/fallback handling a test z relevantných client networks. Geo routing nie je security boundary; source/VPN/resolver location môže ovplyvniť result.

### Multivalue answer

Vracia viac healthy records v service limits a poskytuje jednoduchú DNS distribution. Nie je connection-aware load balancer a nedrží target/session state.

## 6. Route 53 health je samostatný oracle

Route 53 health check môže sledovať public HTTP/HTTPS/TCP endpoint, CloudWatch alarm alebo calculated combination. Check musí mať presný hostname, port, path a expected response.

```text
health checker request
→ public reachability/firewall
→ TLS/Host/path
→ endpoint result
→ threshold calculation
→ record health verdict
```

Health check na rovnaký failover hostname môže po DNS presmerovaní testovať secondary namiesto pôvodného primary a vytvoriť recursive/ambiguous result. Preferuj direct health endpoint identity alebo CloudWatch/ARC control, ktorý jednoznačne reprezentuje exact Region/resource.

Health checker success nie je business transaction. Secondary môže vracať `200` a mať stale database, read-only state alebo nedostatočnú capacity. DNS failover sa prijíma až po business a forbidden tests.

## 7. Active-active a active-passive failure model

Active-active odpovede obsahujú healthy records z viacerých active resources. Application/data musia tolerovať concurrent writes alebo používať single-writer authority.

Active-passive:

```text
primary health fails
→ Route 53 stops returning primary for new uncached queries
→ secondary answer returned
→ clients resolve/reconnect
→ secondary handles business request
```

Po recovery sa nesmie automaticky prepnúť write authority späť iba preto, že health endpoint je green. Failback potrebuje data reconciliation, capacity preflight a controlled TTL/traffic shift.

DNS failover neodstraňuje cached primary answer ani long-lived connection. Client retry musí poznať idempotency a unknown outcome rovnako ako RDS/ELB failure.

## 8. Private hosted zones a split-horizon

Private hosted zone answers sú dostupné z associated VPCs cez Route 53 Resolver. Rovnaké meno môže mať public aj private odpoveď.

Effective private DNS závisí od:

- VPC DNS support/hostnames settings;
- exact hosted-zone/VPC association;
- cross-account association authorization;
- overlapping private zone specificity;
- Resolver forwarding rules;
- endpoint private DNS;
- client network context.

Troubleshooting query sa vykonáva z affected client VPC/host/container. Laptop query cez public resolver nepreukazuje internal answer. Overlapping private zones môžu zmeniť, ktorá zone je authoritative pre suffix; Route 53 neforwarduje automaticky chýbajúci record do public DNS, ak matching private zone existuje.

## 9. Route 53 Resolver a hybrid DNS

Inbound Resolver endpoint umožňuje on-premises clients query-nuť AWS private namespaces. Outbound endpoint forwarduje selected domains z VPC do external DNS podľa Resolver rules.

```text
VPC query for corp.internal
→ outbound Resolver rule
→ outbound endpoint ENIs
→ hybrid route/SG/NACL
→ on-prem DNS targets
→ response
```

Endpoints potrebujú multiple AZs, subnet IP capacity, SGs, routes, target redundancy a QPS monitoring. Shared rules cez AWS RAM potrebujú ownership/versioning.

Forwarding loop vznikne, ak AWS forwarduje suffix on-prem a on-prem ho bez authoritative answeru pošle späť do AWS. Symptóm môže byť timeout alebo `SERVFAIL`; packet/DNS query logs a rule chain rozlišujú loop od missing recordu.

## 10. DNSSEC je integrity chain, nie encryption

DNSSEC podpisuje DNS data a vytvára chain of trust cez DS record v parent zone. Operational subject zahŕňa signing state, KSK/KMS dependency, DS generation, rotation a emergency disable procedure.

Chybný alebo stale DS record spôsobí validating resolverom `SERVFAIL`, aj keď non-validating resolver alebo direct authoritative query ukazuje správny record. DNSSEC nechráni confidentiality query ani application TLS; rieši authenticity/integrity DNS response.

Safe enablement:

```text
zone signing prepared
→ KSK/KMS verified
→ DNSKEY/RRSIG observation
→ DS published at parent
→ validating resolver tests
→ monitoring/rotation
```

Disable sa vykonáva v správnom poradí, aby parent neočakával signatures, ktoré už zone neposkytuje.

## 11. CloudFront distribution je global request program

Distribution obsahuje viewer aliases/certificate, origins/origin groups, ordered cache behaviors, cache/origin-request/response-header policies, edge code, logging a security integrations.

```text
viewer request
→ edge POP and viewer TLS
→ URI normalization
→ first matching cache behavior
→ cache key construction
→ cache lookup
→ hit: cached response
→ miss: origin request policy + origin connection
→ response/cacheability/TTL
→ viewer response
```

Distribution deployment do global edge network nie je okamžitý single-object update. Config status `Deployed` dokazuje propagation completion podľa service control plane, nie correctness všetkých behaviors/origins/client cohorts.

## 12. Viewer TLS a alternate domains

CloudFront viewer certificate pre custom domain sa spravuje v required ACM control Region, typicky `us-east-1`. Certificate pre regional ALB v `eu-central-1` nie je automaticky použiteľný na CloudFront.

Viewer handshake závisí od:

- requested SNI/Host;
- alternate domain configuration;
- certificate SAN/status/chain;
- security policy;
- client protocol/cipher support;
- Route 53 alias.

Viewer TLS success nepreukazuje origin TLS. Edge môže akceptovať client connection a následne vrátiť `502` pre origin hostname/certificate/protocol mismatch.

## 13. Ordered cache behaviors sú routing rules

Distribution má default behavior a optional path-pattern behaviors. Prvá matching behavior podľa precedence vyberie origin a policy set.

```text
/assets/*            → private S3 origin, long immutable caching
/api/payments/*      → ALB origin, caching disabled
*                    → portal origin
```

Wrong precedence alebo broad pattern môže poslať API path do static S3 origin, použiť signed-content requirement na public asset alebo zapnúť caching pre authenticated response. Behavior test musí zahŕňať exact path, method, headers a query.

Allowed methods a cached methods sú odlišné. CloudFront môže forwardovať write methods k custom originu, ale caching sa typicky týka safe read methods podľa behavior configuration. Origin failover má method/status limitations; nie je general write transaction failover.

## 14. Cache key je representation a isolation identity

Cache key určuje, ktoré viewer requests zdieľajú jednu cached response. Základom je path a podľa cache policy môže obsahovať selected query strings, headers, cookies a compression variant.

```text
request A and request B
→ same cache key
→ same cached object representation
```

Príliš široký key vytvára veľa variants, nízky hit ratio a origin load. Príliš úzky key môže zmiešať language, tenant, authorization alebo personalization a spôsobiť data leakage.

Ak origin response závisí od hodnoty, táto hodnota musí byť:

1. súčasť bezpečného cache key;
2. alebo behavior musí caching vypnúť;
3. alebo origin musí vrátiť representation, ktorá je bezpečne spoločná pre všetkých requests s rovnakým key.

Cache key nie je iba performance tuning. Je to data-isolation boundary.

## 15. Cache policy a origin request policy

Cache policy určuje cache-key inputs, TTL bounds a compression. Values zahrnuté v cache key sa automaticky posielajú originu.

Origin request policy môže poslať ďalšie headers, cookies a query strings originu bez ich zahrnutia do cache key.

```text
X-Tenant-ID forwarded to origin
but not in cache key
+ origin response depends on X-Tenant-ID
+ response cacheable
→ first tenant response can be reused for another tenant
```

AWS dokumentácia explicitne upozorňuje, že `Authorization` forwardovaný mimo cache key sa nesmie používať na access-control rozhodnutie cached contentu; buď ho zahrň do key podľa bezpečného designu, alebo caching vypni.

Forwardovanie viewer `Host` headera môže zmeniť origin virtual-host routing a TLS certificate requirement. Origin request policy je preto correctness/security config, nie iba „čo backend potrebuje vidieť“.

## 16. TTL, origin directives a minimum-TTL hranica

CloudFront freshness rozhodnutie kombinuje cache-policy minimum/default/maximum TTL, origin `Cache-Control`/`Expires` a error caching.

Kritická hranica: ak cache policy nastaví minimum TTL väčší než nula, CloudFront môže cache-ovať response minimálne tento čas aj keď origin posiela `Cache-Control: no-cache`, `no-store` alebo `private`.

```text
origin believes response is private/no-store
+ CloudFront minimum TTL = 60
→ shared edge may retain response for at least 60 seconds
```

Pre authenticated dynamic API behavior používaj managed/custom caching-disabled policy s minimum/default/maximum TTL `0` a over actual response headers/cache status. Origin header sám nie je bezpečnostná poistka proti nesprávnemu minimum TTL.

Error responses môžu byť cached podľa status/configuration. Po origin fix-e môže edge stále servovať stale `403/404/5xx`, kým error TTL neuplynie alebo sa vykoná cielená invalidation.

## 17. Immutable assets a invalidation

Static asset publication používa content-addressed/versioned keys:

```text
app.7f23a1.js
styles.a91c2e.css
manifest generation M-44
```

Dlhý TTL je bezpečný, pretože nový release vytvorí nové keys. Rollback zmení manifest/reference, nie obsah existujúceho immutable key.

Invalidation odstráni matching objects z edge caches pred expiry. Je vhodná pre urgentný mutable-content/security fix, ale:

- propaguje sa určitý čas;
- wildcard môže vytvoriť veľký miss/origin spike;
- neopraví origin object ani browser/downstream cache;
- pri bežnom release je horšia než immutable naming.

Acceptance overí nový key/manifest, cache hit po warmup a old-generation rollback path.

## 18. Origins a origin connection

Origin môže byť S3 REST origin, ALB/API/custom HTTP origin, podporovaný AWS service, origin group alebo VPC origin.

Origin contract obsahuje:

- exact origin domain a path;
- protocol policy a TLS hostname;
- connection attempts/timeouts;
- custom headers;
- Origin Shield;
- OAC alebo VPC-origin access;
- response/cache contract;
- capacity a health.

Origin domain nesmie smerovať späť na tú istú distribution, inak vznikne loop. Forwarded Host musí byť compatible s origin listener a certificate.

CloudFront VPC origins môžu pripojiť distribution k supported private ALB/NLB/EC2 origins cez private connection a odstrániť general public origin exposure. Majú service/Region/feature limitations a odlišné deployment/SG requirements; migration vyžaduje explicitný origin identity a rollback plan.

## 19. Private S3 origin cez OAC

Origin Access Control (OAC) umožňuje CloudFront podpisovať S3 REST origin requests cez SigV4. Bucket policy povoľuje CloudFront service principal pre konkrétnu distribution/source ARN podľa contractu.

```text
viewer request
→ CloudFront distribution
→ OAC-signed S3 request
→ bucket policy + KMS
→ object version
```

S3 static website endpoint je custom/public website origin s odlišným access/TLS modelom a OAC sa naň nepoužíva ako na S3 REST origin.

CloudFront `403` sa neopravuje otvorením bucketu public. Rozlišuje sa behavior/origin mapping, OAC attachment/signing, bucket policy, object key/case/version, KMS permission a WAF/signed-content controls.

## 20. Origin Shield, request collapsing a origin capacity

Origin Shield pridáva regional caching layer a môže konsolidovať misses z viacerých edge locations. Znižuje duplicate origin fetches, ale pridáva request/transfer cost a nie je origin HA.

CloudFront môže collapse-nuť simultaneous requests s rovnakým cache key, kým čaká na prvú origin response. To chráni origin pred thundering herd, ale mení concurrency observability. CachingDisabled a private/no-store behavior pri minimum TTL `0` majú odlišné request-collapsing semantics podľa origin/service modelu; critical API sa testuje actual trafficom.

Origin capacity musí zvládnuť cold cache po deployment, invalidation alebo staging distribution. CloudFront continuous deployment staging a primary distributions nezdieľajú cache, takže canary môže mať vyšší origin miss rate než warmed production.

## 21. Origin groups a failover

Origin group vyberá primary a secondary origin pri configured failure statusoch a supported methods.

```text
cache miss
→ primary origin attempt
→ configured failover status
→ secondary origin request
→ response/cache decision
```

Je vhodný pre static/read-only content a controlled degraded fallback. Pri writes alebo personalized state môže secondary byť stale, read-only alebo bez idempotency. CloudFront origin failover nie je distributed database failover.

Cached response/error môže skryť current origin health. Failover test musí force-núť miss alebo použiť unique key a overiť origin identity/data generation.

## 22. WAF, Shield a edge code

AWS WAF môže aplikovať managed rules, IP sets, rate-based rules a ďalšie Layer 7 controls. Rule rollout používa count/sampled-request/log evidence pred broad block. WAF `403` je edge security verdict, nie origin access failure.

Shield poskytuje DDoS capabilities podľa Standard/Advanced service modelu. Neopravuje application authorization ani cache-key isolation.

CloudFront Functions a Lambda@Edge môžu normalizovať URI, meniť headers, autentizovať alebo vyberať origin podľa event modelu. Edge code je globally deployed software generation s vlastnými logs, runtime restrictions, replication time a rollbackom. Transformácia pred cache-key evaluation môže zmeniť, ktoré requests sa považujú za rovnaké; ordering treba explicitne dokumentovať a testovať.

## 23. Signed URLs/cookies a response headers

Signed URLs/cookies obmedzujú access k private contentu podľa key group/public key, expiry a optional path/IP constraints. URL secrecy sama nie je authorization.

Response headers policy môže pridávať CORS/security/custom headers. Security headers neopravia nesprávne cached private body. CORS allow nie je backend authorization a browser enforcement nechráni non-browser clients.

Key rotation potrebuje overlap a revocation plan. Expired signature failure sa rozlišuje od OAC, WAF a origin `403` cez logs/request identity.

## 24. Continuous deployment a configuration rollout

CloudFront continuous deployment môže smerovať časť trafficu na staging distribution podľa weight alebo header-based contractu. Primary a staging majú oddelené caches.

Safe rollout:

```text
immutable policy/function/origin generations
→ staging distribution
→ synthetic positive/forbidden tests
→ header-based internal cohort
→ small weighted viewer cohort
→ cache-hit/miss, origin, privacy a error evidence
→ promote configuration
→ global deployment completion
→ old generation retention/rollback
```

Config references ako cache policy, origin request policy alebo edge function sa môžu meniť mimo distribution documentu. Exact acceptance subject preto obsahuje všetky referenced resource IDs/generations, nie iba distribution ETag.

DNS cutover na novú distribution nastane až po certificate, aliases, origins, logging a behavior tests. Staging cache je cold, takže origin-load alarm thresholds sa interpretujú podľa rollout phase.

## 25. Observability a correlation

| Observation | Rozlišuje |
|---|---|
| `dig +trace`, authoritative NS/DS | delegation/DNSSEC od record contentu |
| authoritative vs recursive/client answer + TTL | control-plane update od cache cohortu |
| CloudFront request ID, POP, `X-Cache`, `Age` | edge/cache state od origin state |
| matched behavior/cache-policy IDs | intended path od effective routing/config |
| cache-key inputs | correct variant od cross-tenant collision |
| CloudFront/WAF logs | viewer/security/cache result |
| origin logs + forwarded headers | cache hit od origin request and identity |
| S3/OAC/KMS evidence | edge success od private-origin authorization |
| CloudTrail/config deployment | who/when changed DNS/distribution/policies |
| payment/tenant audit | fast response od correct authorized representation |

Standard logs nemusia byť immediate; real-time logs majú cost a sampling/configuration. Incident koreluje CloudFront `X-Amz-Cf-Id`, origin request ID, application trace a tenant/payment subject.

`X-Cache: Hit from cloudfront` dokazuje cache reuse na konkrétnej edge path, nie correctness. `Miss` neznamená failure; po cold deployment je expected.

## 26. Connected failure — tenant header forwarded, ale nie izolovaný v cache key

### Symptóm

Po CloudFront configuration rollout-e tenant-b otvorí `GET /api/payments/P-884` a na krátky čas dostane response patriacu tenant-a. Origin application logs ukazujú správnu authorization pre tenant-a a žiadny request tenant-b v danom okamihu. CloudFront response má `X-Cache: Hit from cloudfront` a `Age: 18`.

### Competing hypotheses

1. Application authorization v ALB/origin-e zamenila tenantov.
2. Payment ID je globálne collision-prone.
3. Route 53 poslala tenant-b na inú distribution/generation.
4. Wrong cache behavior matchol API path.
5. `X-Tenant-ID` alebo Authorization nie sú forwardované originu.
6. Header je forwardovaný, ale chýba v cache key.
7. Origin poslal `private/no-store`, ale minimum TTL ho prebil.
8. Edge function odstránila/normalizovala tenant identity.
9. Stale object pochádza zo S3 static originu pre wrong behavior.
10. Browser/service-worker cache, nie CloudFront, vrátil response.
11. Cache invalidation/propagation mixuje old a new policy generations.

### Discriminating observations

| Observation | Čo rozlišuje |
|---|---|
| CloudFront request ID, POP, `X-Cache`, `Age` | shared edge hit od browser/origin response |
| matched behavior and policy IDs | wrong route/policy generation |
| cache-policy header/query/cookie allowlist | tenant key collision od forwarding failure |
| origin-request policy and origin logs | header forwarded/not forwarded |
| origin response `Cache-Control` + policy min TTL | origin intent od CloudFront enforced cacheability |
| tenant-a prior request with same path | cache population source |
| edge-function versions and transformed request | policy issue od code normalization |
| Route 53/distribution alias timeline | wrong distribution cohort |
| payment audit | representation leak od duplicate DB transaction |

### Finding

Rollout zamenil `API-NOCACHE-9` za cache policy s minimum TTL `60`. `X-Tenant-ID` a `Authorization` sa naďalej forwardovali originu cez origin request policy, ale neboli v cache key. Prvý tenant-a GET vytvoril cache entry iba podľa pathu. Origin poslal `Cache-Control: private, no-store`, no minimum TTL väčší než nula v CloudFront policy vynútil cache retention. Tenant-b request mal rovnaký cache key a dostal tenant-a response bez nového origin authorization callu.

### Evidence-preserving containment

- okamžite deaktivovať affected behavior caching cez novú scoped configuration, nie otvárať origin;
- zachovať policy IDs, distribution ETags, edge logs, request IDs, WAF/origin logs a sample leaked responses;
- vykonať cielenú invalidation affected API paths po oprave policy;
- obmedziť API behavior na safe methods/pathy a monitorovať cache hits, ktoré majú byť nulové;
- spustiť privacy incident process a identifikovať affected tenant/request cohort podľa logs;
- nerotovať všetky backend secrets ako náhradu za cache-policy root cause, ak evidence neukazuje compromise.

### Authoritative recovery

1. Obnoviť caching-disabled policy s minimum/default/maximum TTL `0` pre authenticated API.
2. Odstrániť unnecessary cacheable methods a overiť ordered behavior precedence.
3. Zachovať required auth/tenant headers v origin request policy.
4. Ak sa vybrané authenticated GETs majú cache-ovať, navrhnúť explicitný identity-aware key alebo private per-user mechanism; default je no shared caching.
5. Nasadiť cez staging distribution/header cohort.
6. Testovať tenant-a/tenant-b s rovnakým pathom a rozdielnou identity.
7. Overiť `X-Cache`, origin request count, body/headers a application audit.
8. Promote-nuť až po positive a forbidden tests; potom invalidate-nuť stale affected variants.
9. Pridať policy-as-code gate: authenticated origin headers mimo cache key + positive min TTL je forbidden combination.

### Acceptance verdict

Edge recovery je prijatá až keď:

- Route 53 alias smeruje na approved deployed distribution generation;
- `/api/payments/*` matchuje exact non-caching behavior;
- tenant-a a tenant-b requests vždy vykonajú independent origin authorization alebo bezpečne odlišný cache key;
- origin `private/no-store` nie je prebitý positive minimum TTL;
- S3 assets zostávajú private cez OAC a fungujú s immutable caching;
- payment P-884 representation je tenant-isolated;
- wrong tenant, wrong behavior, public bucket a stale error paths zostávajú forbidden;
- deployment gate zachytí rovnakú policy kombináciu pred production.

## 27. Troubleshooting podľa boundary

### `NXDOMAIN`

```text
exact name/type/case
→ parent delegation NS
→ correct public/private hosted zone
→ record existence
→ negative cache TTL
```

### `SERVFAIL`

```text
DNSSEC DS/DNSKEY/RRSIG chain
→ authoritative availability
→ Resolver forwarding loop
→ validating vs non-validating resolver comparison
```

### Stale DNS target

```text
authoritative response
→ recursive resolver cache/TTL
→ client/JVM/application cache
→ existing connections
→ actual target traffic
```

### CloudFront `403`

```text
request ID and WAF result
→ alternate domain/signed content/geo policy
→ matched behavior/origin
→ OAC/VPC-origin authorization
→ S3 bucket/KMS/object key
→ origin custom auth
```

### `404`

```text
normalized path
→ behavior precedence
→ origin path
→ S3 key case/default root
→ application route
→ cached error TTL
```

### `502`

```text
origin DNS
→ origin protocol/TLS hostname/chain
→ SG/NACL/VPC-origin path
→ listener/port
→ edge function/origin response format
```

### `503/504`

```text
edge/function capacity
→ origin availability/capacity
→ response timeout
→ application dependency latency
→ cached error and retry behavior
```

### Privacy/cache correctness

```text
matched behavior
→ cache policy and min TTL
→ exact cache-key inputs
→ origin request policy
→ origin response variation/cache headers
→ `X-Cache`/Age/logs
→ cross-identity forbidden test
```

## 28. Cost a architecture trade-off

Route 53 cost môže zahŕňať hosted zones, queries podľa routing type, health checks, domains a Resolver endpoints/queries. CloudFront cost môže zahŕňať viewer transfer, requests, invalidations, logs, Origin Shield, edge compute, WAF/Shield a origin data/request cost.

Vyšší cache hit ratio často znižuje origin cost a latency, ale hit ratio nikdy nemá prednosť pred representation correctness a tenant isolation. Všetky headers/cookies/query strings v key znižujú hit ratio; žiadne identity inputs pri personalized content vytvára leak. Optimálny key obsahuje presne values, ktoré bezpečne menia representation.

VPC origin znižuje public exposure, ale pridáva deployment/Region/feature dependencies. Origin Shield chráni origin misses, ale pridáva cost a regional shield selection. Low DNS TTL zrýchľuje response na change, ale zvyšuje query volume a nepresúva sessions.

## 29. Anti-patterny odvodené z decision systems

- **Hosted zone považovaná za delegation** — records existujú, ale parent ich nepoužíva.
- **DNS failover považovaný za okamžitý** — TTL, caches a connections predlžujú transition.
- **Weighted DNS považované za request percentage** — resolver concentration skresľuje traffic.
- **Health check na failover hostname** — môže testovať už presmerovaný endpoint.
- **CloudFront alias `EvaluateTargetHealth` predpokladaný bez service supportu** — health design je neúplný.
- **Distribution `Deployed` považované za correctness** — origin/policy/cache behavior nemusí byť správny.
- **Authenticated header forwardovaný mimo cache key pri cacheable response** — origin auth sa pri hit-e nevykoná.
- **Origin `no-store` považované za absolútne pri positive minimum TTL** — CloudFront policy môže response cache-ovať.
- **Všetky viewer values v cache key** — origin overload a nízky hit ratio.
- **Žiadne varying values v key** — wrong representation/data leakage.
- **Public S3 bucket kvôli CloudFront `403`** — OAC/policy/KMS root cause sa maskuje exposure-m.
- **Invalidation ako bežný asset release** — mutable naming zhoršuje cache a rollback lifecycle.
- **Origin failover považovaný za write HA** — secondary data/authority môže byť nekompatibilná.
- **Response headers policy považovaná za privacy control body** — nesprávny cache key zostáva.
- **Edge function change bez version/request-order tests** — transformácia mení routing/cache identity.

## 30. Kontrolné otázky

1. Aký je rozdiel medzi domain registration, hosted zone, delegation a recordom?
2. Prečo Route 53 weighted policy nie je presný request-level load balancer?
3. Čo všetko tvorí DNS failover RTO?
4. Prečo health check nemá používať nejednoznačný failover hostname?
5. Ako sa private hosted zone a Resolver rule podieľajú na effective answeri?
6. Prečo chybný DNSSEC DS môže vytvoriť `SERVFAIL`?
7. Ako CloudFront vyberá cache behavior?
8. Čo je cache key a prečo je security boundary?
9. Ako sa líši cache policy a origin request policy?
10. Prečo minimum TTL môže prebiť origin `no-store/private`?
11. Ako OAC chráni private S3 origin?
12. Kedy je VPC origin vhodný a aké dependencies pridáva?
13. Prečo primary a staging distribution nemajú rovnaký cache state?
14. Aké positive a forbidden tests uzatvárajú authenticated CloudFront behavior?

## Glossary impact

Táto kapitola zavádza alebo spresňuje pojmy: DNS-answer subject, delegation generation, resolver-cache cohort, DNS failover realization, edge-delivery subject, behavior-routing verdict, cache-key identity, representation isolation, origin-request-only input, minimum-TTL override, cache publication generation, OAC origin authorization, VPC-origin path, edge configuration generation a edge-delivery acceptance verdict.

## Oficiálna dokumentácia

- [Amazon Route 53 concepts](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/route-53-concepts.html)
- [Choosing a routing policy](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html)
- [Configuring DNS failover](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover-configuring.html)
- [Route 53 Resolver](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver.html)
- [Routing traffic to CloudFront](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-to-cloudfront-distribution.html)
- [Amazon CloudFront introduction](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html)
- [Understand the cache key](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/understanding-the-cache-key.html)
- [Cache policies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/cache-key-understand-cache-policy.html)
- [Origin request policies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/controlling-origin-requests.html)
- [Restrict access to S3 origins with OAC](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html)
- [Restrict access with VPC origins](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-vpc-origins.html)
- [CloudFront continuous deployment](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/understanding-continuous-deployment.html)
- [CloudFront origin failover](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/high_availability_origin_failover.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: RDS](rds.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Lambda →](lambda.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
