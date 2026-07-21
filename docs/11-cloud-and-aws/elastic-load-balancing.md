# Elastic Load Balancing

Elastic Load Balancing distribuuje traffic medzi viaceré targets a Availability Zones. Load balancer však nie je iba „jedna IP pred servermi“. Je to managed dataplane s listeners, rules, target groups, health checks, TLS, connection lifecycle, zonálnym modelom a vlastnými observability a security hranicami.

## 1. Mentálny model

```text
client
→ DNS name load balancera
→ listener
→ listener rule
→ target group
→ healthy target
→ application
```

Pri diagnostike oddeľ:

- DNS resolution,
- client-to-load-balancer path,
- listener a TLS,
- rule matching,
- target registration,
- health-check path,
- load-balancer-to-target path,
- application response.

## 2. Typy load balancerov

### Application Load Balancer — ALB

Layer 7 HTTP/HTTPS load balancer.

Použitie:

- host-based routing,
- path-based routing,
- HTTP headers, methods, query strings alebo source-IP conditions,
- redirects a fixed responses,
- WebSockets a HTTP/2 podľa supported pathu,
- container a microservice routing,
- integration s AWS WAF a identity capabilities.

### Network Load Balancer — NLB

Layer 4 load balancer pre TCP, TLS, UDP a ďalšie podporované transportné protokoly.

Použitie:

- vysoký connection throughput,
- statické zonálne IP addresses alebo Elastic IPs podľa configuration,
- preserved client-address use cases podľa target type/protocol semantics,
- TLS pass-through alebo termination,
- non-HTTP protocols.

### Gateway Load Balancer — GWLB

Transparentná distribúcia trafficu cez virtual network appliances pomocou GENEVE encapsulation.

Použitie:

- firewally,
- IDS/IPS,
- packet inspection,
- centralized security appliance fleets.

### Classic Load Balancer — CLB

Predchádzajúca generation. Pri novom návrhu preferuj ALB alebo NLB podľa protocol a routing requirements. Migrácia musí overiť rozdiely v health checks, stickiness, TLS, source IP, logging a target registration.

## 3. Regional a zonálny model

ELB je regional service, ale používa nodes v enabled Availability Zones/subnets.

Multi-AZ návrh potrebuje:

- load balancer subnets vo viacerých AZ,
- healthy targets vo viacerých AZ,
- dostatočnú subnet IP capacity,
- zonálne neviazané dependencies,
- správny cross-zone model,
- capacity headroom po strate AZ.

Load balancer s tromi subnetmi nie je odolný, ak všetky targets, NAT path, database alebo application state zostávajú v jednej AZ.

## 4. DNS name

ELB poskytuje DNS name, nie stabilnú jednu public IP pri každom type/configuration.

Používaj:

- Route 53 alias record,
- application DNS name,
- nie hard-coded resolved IP addresses.

DNS resolver cache, TTL a connection pooling môžu ovplyvniť failover a traffic distribution. Test jedného `dig` výsledku nie je úplný pohľad na load-balancer dataplane.

## 5. Listeners

Listener prijíma connections na definovanom protocol/porte.

Príklady:

```text
ALB: HTTPS :443
NLB: TCP :5432
NLB: TLS :443
```

Listener obsahuje default action a pri ALB aj ordered rules.

Over:

- správny protocol a port,
- certificate a TLS policy,
- listener rule priority,
- default action,
- target-group protocol/port,
- Security Group/NACL path.

## 6. ALB listener rules

Rule môže obsahovať conditions a actions.

Conditions môžu zahŕňať:

- host header,
- path pattern,
- HTTP header,
- HTTP method,
- query string,
- source IP.

Actions môžu zahŕňať:

- forward,
- redirect,
- fixed response,
- authentication podľa podporovanej integration.

Rules sa vyhodnocujú podľa priority. Chybná priorita môže poslať traffic do default target groupu, hoci všetky targets sú healthy.

## 7. Target groups

Target group definuje backend contract:

- target type,
- protocol a port,
- VPC,
- health-check configuration,
- deregistration delay,
- routing attributes.

Target types môžu podľa load-balancer type zahŕňať:

- instances,
- IP addresses,
- Lambda,
- ďalší ALB pri podporovanom NLB use case.

Target sa môže nachádzať vo viacerých target groups. Target-group health je kontextový; rovnaká instance môže byť healthy na porte 80 a unhealthy na porte 8080.

## 8. Health checks

Health check je aktívna kontrola dostupnosti targetu.

Konfigurácia môže obsahovať:

- protocol,
- port,
- path,
- interval,
- timeout,
- healthy/unhealthy threshold,
- success-code matcher.

Health endpoint má overovať schopnosť bezpečne obsluhovať traffic, nie iba existenciu processu.

Príliš plytký endpoint:

```text
200 OK, aj keď application nevie čítať configuration
```

Príliš hlboký endpoint:

```text
zlyhanie jednej nepovinnej dependency odstráni všetky targets
```

Navrhni readiness contract podľa kritických dependencies, failure mode-u a graceful degradation stratégie.

## 9. Target health states a reason codes

Targets môžu byť napríklad:

- initial,
- healthy,
- unhealthy,
- unused,
- draining,
- unavailable.

Presné states a reason codes závisia od load-balancer type.

Diagnostický postup:

```text
target registered?
→ target AZ enabled?
→ health-check port/path/protocol?
→ LB SG/NACL to target?
→ application listening?
→ success code/timeout?
→ target response logs?
```

Reason code je silnejší dôkaz než všeobecné tvrdenie „load balancer nefunguje“.

## 10. Fail-open hranica

Pri niektorých ELB typoch/configurations môže nastať fail-open behavior. Napríklad ALB pri target groupe, kde sú všetky registrované targets unhealthy, môže routovať requests na všetky targets bez ohľadu na health status.

Dôsledok:

- health checks nie sú úplný circuit breaker,
- application musí zvládnuť failure a overload,
- monitoring musí alarmovať na healthy-host count,
- incident runbook musí rozlišovať partial target failure od all-target failure.

## 11. Cross-zone load balancing

Bez cross-zone modelu load-balancer node typicky posiela traffic iba targets v rovnakej AZ. S cross-zone môže využívať healthy targets naprieč enabled AZ.

Trade-offy:

- lepšie vyrovnanie pri nerovnomerných targets,
- cross-AZ data transfer a latency considerations,
- failure behavior pri strate AZ,
- rozdielne defaults a configurable attributes podľa ELB type.

Nespoliehaj sa na zapamätaný default. Over live load-balancer a target-group attributes.

## 12. TLS termination

TLS môže byť ukončené:

- na ALB/NLB,
- na targete,
- na oboch vrstvách pri re-encryption.

TLS termination na ELB poskytuje central certificate management a offload.

Over:

- ACM certificate Region a status,
- SNI/domain coverage,
- certificate chain,
- listener security policy,
- backend TLS validation semantics,
- client protocol compatibility,
- rotation a expiry alerts.

TLS listener bez správneho certificate alebo policy môže zlyhať pred akýmkoľvek target-group requestom.

## 13. Security Groups

ALB používa Security Groups na client-to-LB a LB-to-target traffic.

Odporúčaný contract:

```text
internet/client SG
→ ALB SG :443
→ application SG :target-port
```

Application SG môže povoľovať source SG load balancera namiesto širokého VPC CIDR.

Pri NLB over podporu a konkrétny security-group/source-IP model použitej konfigurácie. Nesprávny predpoklad o preserved client IP môže viesť k chybným target SG alebo application ACL rules.

## 14. Network ACLs a ephemeral ports

NACL je stateless. Musí povoľovať request aj return path na subnet boundaries.

Pri troubleshooting over:

- client/listener port,
- target port,
- ephemeral return ports,
- load-balancer subnet NACL,
- target subnet NACL,
- source/destination addresses po prípadnom translation.

Timeout často signalizuje path/filter/drop. Connection refused skôr ukazuje dostupný host bez listenera, ale presná interpretácia závisí od protokolu a middleboxes.

## 15. Deregistration delay a connection draining

Pri deregistration load balancer prestane posielať nové requests a nechá existujúce requests/connections dokončiť podľa target-group behavioru a timeoutu.

Použitie:

- ASG scale-in,
- deployment rollout,
- instance maintenance,
- application shutdown.

Application termination grace musí byť zosúladená s:

- deregistration delay,
- ASG lifecycle hook,
- process shutdown timeout,
- client timeout,
- maximum request/job duration.

Ak instance skončí skôr, draining neposkytne ochranu.

## 16. Slow start

ALB target-group slow start môže postupne zvyšovať traffic pre newly healthy target.

Vhodné pre:

- cache warmup,
- JIT initialization,
- connection-pool buildup,
- workloady citlivé na okamžitý plný load.

Slow start nenahrádza readiness. Target musí byť funkčný ešte pred zaradením.

## 17. Stickiness

Stickiness viaže clienta na target podľa cookie alebo flow semantics podporovaných daným typom.

Riziká:

- nerovnomerné load distribution,
- skrytý local session state,
- komplikovaný rollout,
- hotspot pri long-lived clients,
- failover stále presunie klienta.

Preferuj externalizovaný session state, ak architecture vyžaduje zameniteľné targets.

## 18. ALB routing patterns

### Host-based

```text
api.example.com → api target group
admin.example.com → admin target group
```

### Path-based

```text
/catalog/* → catalog
/payments/* → payments
```

### Weighted forwarding

Použiteľné pre canary alebo postupný traffic shift medzi target groups.

Weighted forwarding sám negarantuje session alebo database compatibility. Potrebuje release metrics, rollback criteria a mixed-version contract.

## 19. NLB patterns

NLB je vhodný pre:

- TCP/TLS/UDP služby,
- static IP requirements,
- PrivateLink provider services,
- high-throughput low-level connections,
- pass-through TLS.

Pri long-lived connections traffic redistribution nepresunie existujúce sessions automaticky. Failover behavior závisí od client reconnect logic, DNS/cache a target state.

## 20. Gateway Load Balancer patterns

GWLB kombinuje transparent network gateway a load balancer pre appliance fleet.

Architecture potrebuje:

- GWLB endpoints,
- route-table steering,
- symmetric routing,
- appliance health,
- state synchronization alebo flow affinity,
- scale a failure model.

Asymmetric routing môže obísť stateful appliance alebo znefunkčniť return traffic.

## 21. Access logs a connection logs

Podľa ELB type môžeš používať:

- access logs,
- connection logs,
- target health reason codes,
- CloudWatch metrics,
- CloudTrail configuration events.

ALB access log môže obsahovať:

- request time,
- client a target address,
- processing times,
- ELB a target status code,
- request line,
- user agent,
- TLS details,
- matched rule/action metadata podľa formátu.

Chráň log bucket policy, retention, encryption a query access. Logs môžu obsahovať citlivé URL/query/header metadata.

## 22. CloudWatch metrics

Relevantné metrics podľa type zahŕňajú:

- request/connection count,
- target response time,
- healthy/unhealthy host count,
- ELB 4xx/5xx,
- target 4xx/5xx,
- rejected connections,
- active/new flows,
- processed bytes,
- TLS negotiation errors,
- consumed capacity units.

Rozlišuj:

- **ELB-generated 5xx** — load balancer/proxy/path problém,
- **target-generated 5xx** — application odpoveď.

## 23. Zonal shift a zonálna odolnosť

Pri podporovaných službách môže AWS Application Recovery Controller pomôcť presunúť traffic z impaired AZ.

Zonal shift je užitočný iba ak:

- zostávajúce AZ majú capacity,
- targets sú zdravé,
- stateful dependencies prežijú,
- DNS/client behavior nebráni recovery,
- scaling dokáže doplniť fleet.

Nie je náhradou Multi-AZ designu.

## 24. Troubleshooting `unhealthy`

Postup:

```text
health reason code
→ target registration a AZ
→ health-check port/path/protocol/matcher
→ LB-to-target SG
→ NACL a route
→ listener na targete
→ application logs
→ dependency latency
```

Príklady:

- health path vracia redirect mimo matcheru,
- application počúva iba na `127.0.0.1`,
- target SG povoľuje client CIDR, ale nie LB SG,
- NACL blokuje ephemeral return,
- TLS target používa nekompatibilný protocol,
- startup trvá dlhšie než thresholds,
- health endpoint čaká na zlyhanú dependency.

## 25. Troubleshooting 502/503/504

### 502

Možné príčiny:

- invalid target response,
- reset connection,
- TLS/backend protocol mismatch,
- closed connection,
- Lambda target error.

### 503

Možné príčiny:

- žiadne registered/usable targets,
- target group unavailable,
- capacity alebo routing failure.

### 504

Možné príčiny:

- target timeout,
- network timeout,
- application/dependency latency,
- mismatched idle/response timeout.

Vždy koreluj ELB status, target status, processing times, target logs a metrics.

## 26. Troubleshooting chybných rules

Over:

- request `Host` header,
- URL path po normalization,
- rule priorities,
- wildcard matching,
- default rule,
- redirect loop,
- weighted target groups,
- deployment automation drift.

`curl` priamo na load-balancer DNS bez správneho Host headera nemusí testovať zamýšľanú host-based rule.

Príklad:

```bash
curl -vk https://<alb-dns>/catalog -H 'Host: shop.example.com'
```

## 27. Troubleshooting TLS

Over:

```bash
openssl s_client -connect example.com:443 -servername example.com
```

Následne:

- certificate SAN,
- expiry a chain,
- listener certificate selection,
- security policy/ciphers,
- DNS target,
- backend protocol,
- ACM deployment Region,
- client trust store.

## 28. Cost model

Cost drivers môžu zahŕňať:

- load-balancer hours,
- capacity units,
- processed bytes,
- new/active connections alebo rules podľa type,
- cross-zone/cross-AZ data path,
- public data transfer,
- access-log storage,
- WAF a additional security services.

Consolidácia mnohých applications na jeden ALB znižuje počet load balancerov, ale zväčšuje blast radius, rule complexity a shared quota dependency.

## 29. SOA-C03 mapovanie

- **Domain 1** — metrics, access logs, unhealthy targets a latency analysis,
- **Domain 2** — Multi-AZ traffic, health routing, connection draining a failover,
- **Domain 3** — automated target registration, ASG integration a deployment traffic shifting,
- **Domain 4** — TLS, Security Groups, WAF a log protection,
- **Domain 5** — listeners, target groups, DNS, NACLs a end-to-end connectivity.

Praktické drilly:

- ALB target unhealthy pre SG reference,
- wrong target port,
- host rule priority chyba,
- NLB long-lived connection behavior,
- TLS certificate/SNI mismatch,
- all-target-unhealthy fail-open incident.

## 30. Anti-patterny

### Health check na `/` bez contractu

Homepage môže byť healthy, hoci kritické application paths nefungujú, alebo naopak závisí od nepovinnej služby.

### Target SG otvorená svetu

Obchádza intended load-balancer ingress boundary.

### Jeden target v jednej AZ

Load balancer nevytvorí redundancy.

### Hard-coded ELB IP

DNS-backed infrastructure sa môže meniť.

### Deregistration bez application shutdown koordinácie

Existing requests sa prerušia.

### Jeden shared ALB bez ownership a quota modelu

Chybná rule alebo certificate zmena ovplyvní mnoho tímov.

## 31. Kontrolné otázky

1. Ako sa líši ALB, NLB a GWLB?
2. Čo je listener, rule a target group?
3. Prečo target health nie je vlastnosť instance všeobecne?
4. Ako funguje deregistration delay?
5. Kedy je relevantné cross-zone load balancing?
6. Ako odlíšiš ELB-generated a target-generated 5xx?
7. Prečo ALB môže pri všetkých unhealthy targets predstavovať fail-open riziko?
8. Ako navrhneš Security Group contract medzi ALB a application?
9. Ktoré vrstvy preveríš pri 504?
10. Prečo load balancer sám negarantuje Multi-AZ high availability aplikácie?

## Glossary impact

Relevantné pojmy: Elastic Load Balancing, Application Load Balancer, Network Load Balancer, Gateway Load Balancer, listener, listener rule, target group, target type, target health, health-check matcher, cross-zone load balancing, deregistration delay, connection draining, slow start, stickiness, weighted forwarding, fail-open, load-balancer access log a zonal shift.

## Oficiálna dokumentácia

- [What is Elastic Load Balancing?](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html)
- [Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)
- [Network Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/introduction.html)
- [Gateway Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/gateway/introduction.html)
- [ALB target groups](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html)
- [ALB target health checks](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: EC2 a Auto Scaling](ec2-auto-scaling.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: S3, EBS a EFS →](s3-ebs-efs.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
