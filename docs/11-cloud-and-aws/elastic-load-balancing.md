# Elastic Load Balancing

Elastic Load Balancing (ELB) vytvára managed traffic-distribution boundary medzi clients a meniacou sa množinou backend targets. Load balancer nie je jedna stabilná IP pred servermi a target group nie je iba zoznam instances. Reálny request outcome vznikne až vtedy, keď DNS dovedie clienta k správnemu load-balancer dataplane-u, listener prijme connection, TLS a listener rules vytvoria routing verdict, target group určí eligible cohort, selection algorithm vyberie target, backend connection prejde network controls a application vráti správny business response.

Dominantný lifecycle:

```text
client business request
→ DNS a load-balancer node selection
→ viewer/client connection
→ listener a TLS acceptance
→ ordered listener-rule verdict
→ target-group generation
→ registered + enabled + healthy target eligibility
→ routing algorithm a zonal/cross-zone decision
→ independent backend connection
→ application response
→ load-balancer response a logs
→ scale, drain, deployment alebo zonal recovery
→ business a forbidden-outcome acceptance
```

Stav `Healthy` dokazuje iba konkrétny health-check contract. Nedokazuje, že správny listener rule vybral správnu release generation, že payment request prešiel exactly once ani že load balancer pri strate healthy targets traffic zastaví.

## 1. Exact traffic-distribution subject

Atlas Payments používa parent subjects `CAP-PAY-42`, `NET-PAY-42` a `FLEET-PAY-42`. Load-balancing subject je `LB-PAY-42`:

```text
account = 100000000042
Region = eu-central-1
public hostname = pay.example.com
load balancer = alb-pay-public-17
scheme = internet-facing
subnets = ingress-a / ingress-b / ingress-c
load-balancer SG generation = SG-LB-18

viewer connection =
  client 203.0.113.77:ephemeral
  → HTTPS pay.example.com:443

listener generation = LIS-24
certificate generation = CERT-11
TLS policy generation = TLS-8

ordered rules =
  priority 10: Host=pay.example.com + Path=/api/payments/*
               → weighted forward tg-pay-v714 90 / tg-pay-v715 10
  priority 20: Host=pay.example.com + Path=/api/*
               → tg-pay-v714
  default: fixed 404

target groups =
  tg-pay-v714 / HTTPS:8443 / release 7.14.0
  tg-pay-v715 / HTTPS:8443 / release 7.15.0

health contract =
  HTTPS /readyz
  success matcher = 200
  unhealthy threshold = 2
  healthy threshold = 3
  deregistration delay = 120 seconds
  slow start = 60 seconds

business request = payment P-884
business outcome = authorize and persist payment exactly once
forbidden outcomes =
  direct client connection to target ENI
  request routed to wrong host/path/release cohort
  unhealthy target treated as safe merely because fail-open occurs
  target terminated before request drain
  canary evidence attributed to a cohort that did not receive the request
```

Pri incidente treba zachovať presný request timestamp, `Host`, path, method, client/request ID, listener/rule generation, target-group ARN, target ID/AZ, release generation, load-balancer status, target status a business transaction ID. Bez toho možno analyzovať zdravý target alebo správnu rule, ktoré konkrétny request vôbec nepoužil.

## 2. ELB typ vyberá observation a routing boundary

### Application Load Balancer

ALB ukončuje HTTP/HTTPS connection a vytvára novú connection k targetu. Rozumie application-layer údajom, preto môže routovať podľa host headera, pathu, methodu, headers, query strings alebo source-IP conditions. Podporuje redirects, fixed responses, weighted forwarding, authentication integrations, WebSockets, WAF a ďalšie HTTP capabilities.

ALB je vhodný, keď routing verdict závisí od HTTP representation alebo application identity. Jeho hlavná prevádzková výhoda nie je iba „Layer 7“, ale schopnosť oddeliť:

```text
viewer connection lifecycle
od
backend target connection lifecycle
```

Client môže mať HTTP/2 alebo HTTP/3-facing behavior podľa podporovanej konfigurácie, zatiaľ čo backend používa iný protocol/version contract. Viewer TLS môže byť zdravé a backend TLS môže zlyhávať nezávisle.

### Network Load Balancer

NLB distribuuje TCP, TLS, UDP a podporované transportné flows. Je vhodný pre non-HTTP protocols, statické zonálne IP/EIP requirements, vysoký connection throughput, PrivateLink provider services a TLS pass-through alebo termination.

Pri NLB je kritické poznať target type, protocol a client-IP preservation semantics. Application ACL alebo target SG navrhnutá podľa nesprávneho predpokladu o visible source address môže blokovať správny flow alebo otvoriť príliš široký scope. Long-lived connection zostáva na existujúcom targete; zmena healthy cohortu automaticky nepremiestni už otvorenú session.

### Gateway Load Balancer

GWLB transparentne vkladá appliance fleet do packet pathu cez GENEVE. Routing verdict vzniká kombináciou route-table steeringu, GWLB endpointu, appliance target groupu, flow affinity, health a symmetric return pathu. Je vhodný pre firewall, IDS/IPS a inspection appliances, nie pre application HTTP routing.

### Classic Load Balancer

CLB je staršia generation. Migrácia na ALB alebo NLB nie je rename. Mení health semantics, source identity, TLS, stickiness, logging, target registration a connection behavior; preto potrebuje explicitnú compatibility matrix a traffic canary.

## 3. Regional service, zonálny dataplane

ELB je regional service, ale load-balancer nodes a ENIs sa realizujú v enabled Availability Zones/subnets. Multi-AZ názov preto treba rozložiť:

```text
regional control plane
→ enabled LB subnet/AZ inventory
→ zonal LB nodes a addresses
→ target registration v enabled AZ
→ zonal alebo cross-zone selection
→ target a dependency capacity
→ failure a recovery behavior
```

Tri load-balancer subnets nevytvoria HA, ak application targets, NAT, EFS mount path, database writer alebo state zostávajú závislé od jednej AZ. Po zonal shift-e musia zostávajúce AZs absorbovať DNS/client distribution, target load, database connections aj downstream throughput.

Subnet IP headroom je súčasť load-balancer capacity. Managed nodes môžu pri scale alebo maintenance potrebovať ďalšie addresses. IP-exhausted ingress subnet môže obmedziť dataplane expansion aj pri healthy targets.

## 4. DNS dovedie clienta k service, nie k jednej nemennej IP

ELB poskytuje DNS name. Application hostname typicky používa Route 53 alias. Resolved addresses sa môžu meniť podľa zonal state, scalingu alebo maintenance, preto sa neukladajú ako statická application configuration.

```text
pay.example.com
→ Route 53 alias
→ current ELB DNS answers
→ client/resolver cache
→ selected zonal load-balancer node
```

Jeden `dig` result nepreukazuje všetky adresy ani všetky client cohorts. Existing connections zostávajú otvorené aj po DNS zmene. Zonal recovery preto zahŕňa resolver TTL, application DNS cache, connection reuse a reconnect behavior.

## 5. Listener je front-door protocol contract

Listener definuje protocol, port, TLS policy/certificates a default action. Connection môže zlyhať ešte pred target selection:

```text
TCP path
→ listener exists on expected port
→ TLS SNI/certificate/security-policy match
→ HTTP parse a limits
→ rule evaluation
```

Pri HTTPS môže listener používať viac certificates. SNI a certificate selection musia pokryť alternate hostnames; default certificate nesmie maskovať chýbajúci SAN pre určitý client cohort. ACM status, Region, chain, expiry a listener attachment sú samostatné observation points.

TLS termination na load balanceri centralizuje certificate lifecycle. Backend môže byť HTTP, HTTPS alebo pass-through podľa ELB typu. Re-encryption chráni backend path, ale vyžaduje vlastný protocol a trust contract. Viewer handshake success nedokazuje backend TLS success.

## 6. Ordered listener rules vytvárajú routing program

ALB listener rules sa vyhodnocujú podľa priority. Prvá matching rule určí actions; default rule sa použije až keď žiadna custom rule nematchne.

```text
request Host/path/method/headers/query/source
→ normalize podľa ALB semantics
→ priority 1, 2, 3 ...
→ first matching rule
→ forward / redirect / fixed response / authentication
```

Broad rule s vyššou prioritou môže shadowovať presnejšiu canary rule. Všetky target groups môžu byť healthy a request napriek tomu smeruje do nesprávnej cohorty. Rule test preto musí používať skutočný `Host`, path, method a relevantné headers. `curl` na raw ALB hostname bez production Host headera nemusí testovať intended routing.

Weighted forwarding rozdeľuje nové eligible requests medzi target groups podľa weights, ale nie je samo o sebe experiment contract. Stickiness, long-lived connections, client retries a malá sample size môžu skresliť observed percentage. Každý target response musí niesť release/cohort identity, aby metrics neboli pripísané iba podľa zamýšľanej konfigurácie.

## 7. Target group je backend protocol a eligibility boundary

Target group definuje:

```text
target type
+ protocol/port
+ health-check contract
+ deregistration delay
+ routing algorithm/attributes
+ cross-zone behavior
+ slow start/stickiness
→ eligible backend cohort
```

Target health je kontextová. Rovnaká instance môže byť healthy v jednej target group na `8443`, unhealthy v inej na `9443` a vôbec neregistrovaná v tretej. Target group musí byť v správnom VPC a target AZ musí byť enabled pre load balancer podľa service semantics.

Target types môžu byť instance, IP, Lambda alebo podporované service-specific targets. Instance target používa instance identity a port; IP target viaže health/routing na konkrétnu address identity. Replacement alebo container rescheduling preto potrebuje registration reconciliation, nie iba healthy EC2 state.

## 8. Health check je explicitný oracle

Health check definuje protocol, port, path, timeout, interval, thresholds a success matcher. Jeho otázka má byť:

> Môže tento target teraz bezpečne prijať nový request patriaci k tejto target group?

Príliš plytký check vracia `200`, hoci application nemá configuration, credentials alebo mandatory dependency. Príliš hlboký check viazaný na každú optional dependency môže naraz vyradiť celý fleet pri degradácii, ktorú by application vedela obslúžiť fallbackom.

Rozumné vrstvy:

```text
liveness = process sa nezasekol nenávratne
readiness = target môže bezpečne prijať nový traffic
business canary = konkrétna transaction/journey je správna
```

ELB health check nie je business canary. Matcher `200` tiež neoveruje response body alebo tenant correctness. Thresholds vytvárajú detection a recovery delay; musia byť zosúladené so startupom, transient errors a failure objective.

## 9. Fail-open je availability mechanism s correctness rizikom

Ak ALB nemá dostatok healthy targets a v target group sú všetky registrované targets unhealthy, môže routovať na všetky targets bez ohľadu na health status. NLB má tiež fail-open hranice vrátane prázdnej alebo all-unhealthy target group podľa service behavioru.

Causal model:

```text
health oracle označí celý cohort unhealthy
→ load balancer nemá healthy selection set
→ fail-open zabráni úplnému blackhole
→ traffic vstúpi aj do unhealthy targets
→ application môže vrátiť chybu, overload alebo nekorektný side effect
```

Fail-open preto nie je dôkaz recovery. Alarmy musia sledovať healthy-host count, all-unhealthy state, target errors a business outcomes. Health check sa nesmie používať ako jediný security alebo circuit-breaker mechanismus.

## 10. Selection algorithm, slow start a anomaly mitigation

Po vytvorení eligible setu vyberá load balancer target podľa podporovaného routing algorithmu a target-group attributes. ALB target groups môžu podporovať round robin, least outstanding requests a weighted-random behavior vrátane Automatic Target Weights/anomaly mitigation v podporovaných configurations.

Algorithm nemení target capacity na rovnakú. Heterogénny fleet alebo mixed release môže mať rozdielne latency a concurrency limits. Selection evidence musí korelovať request count, outstanding work, target latency a errors podľa target/release/AZ.

Slow start postupne zvyšuje traffic pre newly healthy target. Pomáha pri cache/JIT/pool warmup, ale target musí byť funkčný ešte pred vstupom do slow startu. Slow start nenahrádza readiness ani downstream capacity gate.

## 11. Cross-zone a zonal affinity

Cross-zone load balancing určuje, či zonálny load-balancer node môže routovať na targets v iných enabled AZs. Defaults a configurable scope sa líšia podľa ELB typu a target-group behavioru; live attributes sú authoritative.

Cross-zone zapnuté:

- lepšie využije nerovnomerne rozdelené healthy targets;
- môže skryť chýbajúcu zonálnu capacity;
- môže vytvoriť cross-AZ data path a dependency coupling.

Cross-zone vypnuté:

- zachová silnejšiu zonálnu affinity;
- vyžaduje dostatočné healthy targets v každej traffic-serving AZ;
- zonal shift zároveň odstráni load-balancer address aj target capacity danej AZ.

Rozhodnutie musí byť súčasťou failure experimentu. „Targets sú spolu zdravé“ nestačí; treba overiť per-AZ eligible capacity pred a po strate jednej AZ.

## 12. Dve connection vrstvy a source identity

Pri ALB requeste existujú minimálne dve connections:

```text
A: viewer → ALB listener
B: ALB node → application target
```

Connection A používa client source, listener port, ALB SG/NACL a viewer TLS. Connection B používa load-balancer node source semantics, target port, target SG/NACL a backend TLS/listener. Application client identity sa typicky prenáša v HTTP forwarding headers, ale network source backend connection nie je pôvodný client.

Security contract:

```text
internet/client CIDR
→ ALB SG :443
→ application SG from ALB SG :8443
```

Target SG otvorená svetu obchádza load-balancer ingress boundary. Pri NLB treba overiť security-group support, target type a preserved-source semantics konkrétneho flowu; všeobecný ALB model sa naň nesmie preniesť mechanicky.

NACL je stateless a musí povoliť service aj ephemeral return ports na LB a target subnet boundaries. `Connection refused` a timeout majú odlišnú dôkaznú hodnotu, ale middleboxes ich môžu meniť; preto sa korelujú s Flow Logs, packet evidence a target listenerom.

## 13. Response ownership a status codes

ALB access logs a metrics odlišujú load-balancer-generated a target-generated responses. Pri incidente sa sledujú minimálne:

```text
ELB status code
+ target status code
+ request-processing time
+ target-processing time
+ response-processing time
+ matched rule a target identity
+ target application trace
```

Praktická interpretácia:

- `502` často znamená invalid/reset backend response, backend TLS/protocol mismatch alebo connection closure;
- `503` často znamená chýbajúci usable target alebo load-balancer capacity/path problém;
- `504` často znamená backend/network timeout alebo dependency latency.

Status code nie je root cause. `504` zvýšený po release môže byť pomalý query, connection-pool starvation, NACL drop alebo response timeout. Timeout zvýš až po identifikácii operation budgetu; inak iba predĺži resource occupancy a retry amplification.

## 14. Stickiness a long-lived sessions

Stickiness viaže clienta k targetu podľa cookie alebo supported flow semantics. Môže byť oprávnená pre session affinity, ale vytvára:

- nerovnomerné load distribution;
- hotspoty pri long-lived clients;
- mixed-release bias;
- komplikovaný failover;
- skrytý local session state.

Externalizovaný session state zvyšuje zameniteľnosť targets. Stickiness sa nemá používať na maskovanie application state coupling. Canary verification musí vedieť, či client zostal na old cohort-e napriek weights.

WebSocket, streaming a long-lived TCP connections sa nepresunú iba zmenou weights alebo health. Recovery závisí od disconnect, client reconnect a idempotent session resumption.

## 15. Deregistration a drain sú koordinovaný state transition

Keď sa target deregistruje, load balancer prestane posielať nové requests podľa service semantics a target zostáva v draining state počas deregistration delay. Bezpečné odstránenie vyžaduje koordináciu:

```text
mark target for removal
→ stop new selection
→ drain in-flight requests/connections
→ application stops acquiring new background work
→ business commit alebo checkpoint
→ response/acknowledgement completion
→ target deregistration complete
→ ASG lifecycle completion
→ process/instance termination
```

Ak ASG alebo process skončí pred drain completion, nastavený `120 s` delay nepomôže. Ak request vykonal external side effect a connection sa prerušila pred response, client retry vytvára unknown outcome. Load balancer lifecycle preto potrebuje application idempotency a reconciliation.

Deregistration delay príliš dlhý môže spomaliť rollout a držať stale generation. Príliš krátky prerušuje legitimate long requests. Contract vychádza z maximum accepted request duration, client timeoutu, shutdown grace a business semantics.

## 16. ASG, target registration a release transition

ASG launch/terminate event mení target inventory. Serving capacity vzniká až po:

```text
instance ready
→ target registered
→ health thresholds passed
→ optional slow start
→ selected traffic
→ business canary
```

Pri instance refresh sa musí zosúladiť minimum healthy percentage, ASG warmup, target health thresholds, deregistration delay a application shutdown. ASG `InService` a target `Healthy` sú rôzne gates.

Weighted target groups umožňujú canary medzi release cohorts. Safe transition potrebuje immutable target/release identity, mixed-version data compatibility, subject-bound metrics, rollback criteria a old-cohort drain. Zmena weight bez overenia matched rule a actual target cohort je iba control-plane intent.

## 17. Zonal shift a zonal recovery

Application Recovery Controller môže pri podporovaných ALB/NLB configurations začať zonal shift, ktorý odstráni zonálny load-balancer address z service pathu. Úspech závisí od:

```text
remaining LB nodes
+ remaining target capacity
+ cross-zone attribute
+ application/database/downstream headroom
+ DNS/client reconnect
+ state consistency
→ surviving business throughput
```

Zonal shift nie je náhrada za Multi-AZ design. Pred shiftom treba overiť, či strata zonálnej target capacity pri vypnutom cross-zone nespôsobí ďalší overload. Po shift-e treba sledovať request distribution, healthy targets, errors, latency a business backlog; `shift active` nie je acceptance verdict.

## 18. Access logs, metrics a request correlation

Relevantná evidence:

| Observation point | Rozlišuje |
|---|---|
| Route 53/resolver a ELB DNS answers | DNS/client cohort od backend failure |
| listener/certificate configuration | TCP path od TLS/SNI failure |
| matched rule/action | routing intent od actual verdictu |
| target health reason code | registration/AZ/health failure class |
| ALB/NLB access alebo connection logs | viewer, target, timings, status a TLS metadata |
| CloudWatch healthy/unhealthy host count | partial cohort od all-unhealthy/fail-open state |
| request/flow count per AZ/target | control-plane weights od actual selection |
| target application trace | backend connection od business operation |
| CloudTrail | kto zmenil listener/rule/TG/LB attributes |
| payment idempotency ledger | transport error od duplicate/unknown business outcome |

Logs môžu obsahovať URL/query/user-agent a identity-related metadata, preto bucket policy, encryption, retention a query access patria do security contractu. Log delivery nemusí byť okamžitá; incident používa request IDs a viac observation points.

## 19. Connected failure — healthy fleet, shadowovaná canary rule

### Symptóm

Release `7.15.0` má dostať 10 % `/api/payments/*` trafficu. Deployment dashboard hlási obe target groups healthy a listener configuration deployed. Po 30 minútach však `tg-pay-v715` eviduje iba health checks, žiadne production requests. Release team napriek tomu pripisuje celkovú nízku error rate canary cohort-e a chce zvýšiť weight na 50 %.

### Competing hypotheses

1. Client requests používajú iný hostname alebo path.
2. Route 53/DNS stále smeruje na starý ALB.
3. Listener `443` používa inú generation alebo certificate.
4. Canary rule nematchuje normalized path/method/header.
5. Broad `/api/*` rule má vyššiu priority a shadowuje canary rule.
6. Weighted forwarding je prebitý stickiness.
7. `tg-pay-v715` targets nie sú enabled/eligible napriek health dashboardu.
8. Cross-zone alebo AZ registration odstraňuje canary cohort z selection setu.
9. Access logs/metrics používajú wrong load balancer alebo dimensions.
10. Application neposiela release identity, takže requests sa nedajú priradiť.

### Discriminating observations

| Observation | Čo rozlišuje |
|---|---|
| production request `Host`, raw path a method | wrong client request od rule-order chyby |
| Route 53 alias a ELB DNS/request ID | old distribution/LB od current listener |
| listener rules s priorities a ARNs | intended order od effective routing programu |
| access-log matched rule priority/target group | weight problem od shadowed rule |
| request count per target group excluding health checks | actual canary exposure |
| target response release header a trace | selected TG od actual application generation |
| stickiness cookie cohort | weight selection od persistent affinity |
| target health reason/AZ attributes | rule match od eligibility failure |
| CloudTrail change timeline | authoring error od later drift |

### Finding

IaC renderer pridelil broad rule `Host=pay.example.com + Path=/api/*` priority `10` a presnejšej payment canary rule priority `20`. ALB vyhodnotil broad rule ako prvú, preto všetky requests smerovali do `tg-pay-v714`. Canary targets boli healthy, ale health traffic nepreukazoval production exposure. Dashboard agregoval load-balancer-wide business metrics a vytvoril false-green rollout verdict.

### Evidence-preserving containment

- zastaviť weight progression; nemeníť target health alebo SG rules;
- exportovať listener rule generation, access logs, target-group counters a CloudTrail change;
- zachovať current target cohorts a nepripisovať aggregate metrics canary release-u;
- označiť predchádzajúci „10 % canary“ interval ako invalid experiment evidence;
- overiť, že release `7.15.0` nevykonala žiadne production side effects.

### Authoritative recovery

1. Zaviesť explicitnú deterministic priority allocation, kde narrower payment rule predchádza broad `/api/*` rule.
2. Vytvoriť novú listener generation, nie editovať audit identity bez provenance.
3. Pred deployom vykonať rule-overlap analysis s concrete Host/path/method cases.
4. Nasadiť configuration a overiť matched rule cez controlled requests.
5. Potvrdiť target/release identity v response a trace.
6. Obnoviť canary na malom weight-e so subject-bound technical, functional a business metrics.
7. Vykonať forbidden tests: `/api/catalog/*` nesmie ísť do payment TG; unknown host dostane fixed `404`; target ENI nie je direct-reachable.
8. Pokračovať až po dostatočnej sample size, nie iba po uplynutí času.

### Acceptance verdict

Load-balancing zmena je prijatá až keď:

- production request matchuje intended listener rule generation;
- observed target-group/release distribution zodpovedá canary contractu v tolerancii vysvetliteľnej stickiness/connections;
- viewer aj backend TLS sú validné;
- healthy target cohort má dostatočnú zonálnu capacity;
- payment P-884 prejde exactly once;
- wrong host/path/direct-target paths zostanú forbidden;
- all-unhealthy fail-open alarm a runbook sú overené;
- drain test dokončí in-flight request pred target termination.

## 20. Troubleshooting model podľa failure boundary

### Connection sa nevytvorí

```text
DNS/alias
→ LB scheme a enabled AZ addresses
→ route/IGW
→ SG/NACL
→ listener port
→ viewer TLS/SNI
```

### Request ide na nesprávny backend

```text
Host/path/method/header/query
→ listener generation
→ ordered rules a first match
→ weighted/sticky action
→ target group identity
→ target/release response identity
```

### Target je unhealthy

```text
registration a target type
→ enabled AZ
→ health protocol/port/path/matcher
→ LB-to-target SG/NACL/route
→ target listener/TLS
→ readiness dependency
→ thresholds a startup duration
```

### `502/503/504`

```text
ELB vs target status
→ matched rule/target ID
→ processing timings
→ backend connection/TLS
→ application/dependency trace
→ capacity a timeout budget
→ retry a business outcome
```

### Zonal incident

```text
per-AZ LB addresses
→ per-AZ eligible targets
→ cross-zone attribute
→ remaining capacity/downstream envelope
→ zonal shift
→ DNS/reconnect behavior
→ business throughput a forbidden bypass
```

## 21. Cost a consolidation trade-off

Cost môže zahŕňať load-balancer hours, capacity units, processed bytes, new/active connections, rule evaluations podľa typu, public/cross-AZ transfer, logging, WAF, Shield a origin dependencies.

Jeden shared ALB znižuje object count, ale spája certificate, rules, quotas, deployment cadence a incident blast radius viacerých applications. Dedicated ALB zvyšuje cost, no poskytuje jasnejšie ownership a failure isolation. Rozhodnutie má vychádzať z trust boundary, rule complexity, quota headroom a shared-change governance.

Cross-zone môže zlepšiť utilization, ale vytvoriť transfer a skryté zonálne coupling. Slow start môže znížiť startup errors, ale predĺžiť time-to-full-capacity. Long deregistration delay chráni requests, ale spomaľuje replacement. Každý parameter je lifecycle trade-off, nie univerzálny best practice.

## 22. Anti-patterny odvodené z modelu

- **Health check na `/` bez oracle contractu** — homepage nepreukazuje payment readiness.
- **All-healthy považované za správne routing** — listener rule môže posielať request do wrong cohortu.
- **Aggregate LB metrics použité pre canary verdict** — evidence nie je viazaná na target/release subject.
- **Broad rule s vyššou prioritou než specific rule** — first match shadowuje intended route.
- **Target SG otvorená svetu** — obchádza load-balancer ingress boundary.
- **Hard-coded resolved ELB IP** — DNS-backed dataplane identity sa mení.
- **Fail-open ignorované** — all-unhealthy target group nemusí znamenať traffic stop.
- **Slow start použitý namiesto readiness** — nefunkčný target dostane síce pomalšie, ale stále production traffic.
- **Weight change bez stickiness/connection analýzy** — actual exposure sa líši od control-plane čísla.
- **Deregistration delay bez shutdown koordinácie** — instance skončí pred drainom.
- **Zonal shift bez remaining-capacity preflightu** — recovery action vytvorí overload.
- **Jeden shared ALB bez owner/quota policy** — malá rule zmena má multi-application blast radius.

## 23. Kontrolné otázky

1. Prečo ALB request obsahuje dve samostatné connections?
2. Kedy je vhodnejší ALB, NLB a GWLB?
3. Čo presne dokazuje target state `Healthy`?
4. Ako first-match rule evaluation môže zneplatniť canary experiment?
5. Prečo weighted target groups negarantujú presné request percento?
6. Čo je fail-open a prečo je zároveň availability aj correctness riziko?
7. Ako sa slow start líši od readiness?
8. Ktoré timeouts a lifecycle gates musia byť zosúladené pri drain-e?
9. Ako odlíšiš ELB-generated a target-generated `5xx`?
10. Čo mení cross-zone pri strate jednej AZ?
11. Aké dôkazy viažu request na konkrétnu target/release generation?
12. Aký acceptance verdict požaduješ pred zvýšením canary weightu?

## Glossary impact

Táto kapitola zavádza alebo spresňuje pojmy: traffic-distribution subject, viewer connection, backend target connection, listener generation, first-match routing verdict, target-group generation, target eligibility set, target health oracle, load-balancer fail-open, weighted-exposure evidence, zonal target capacity, drain completion, matched-rule evidence a load-balancing acceptance verdict.

## Oficiálna dokumentácia

- [What is Elastic Load Balancing?](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html)
- [Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)
- [Listeners for Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-listeners.html)
- [Target groups for Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html)
- [Health checks for Application Load Balancer target groups](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html)
- [Target group attributes for Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/edit-target-group-attributes.html)
- [Network Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/introduction.html)
- [Gateway Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/gateway/introduction.html)
- [Zonal shift for an Application Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/zonal-shift.html)
- [Access logs for Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-access-logs.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: EC2 a Auto Scaling](ec2-auto-scaling.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: S3, EBS a EFS →](s3-ebs-efs.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
