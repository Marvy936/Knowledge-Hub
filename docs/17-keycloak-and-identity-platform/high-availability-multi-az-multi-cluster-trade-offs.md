# High availability, multi-AZ a multi-cluster trade-offs

Keycloak high availability nie je počet replicas ani zelený load balancer. Availability vzniká iba vtedy, keď surviving Keycloak capacity, database writer a synchronous replicas, cache/session model, network latency, TLS/DNS/load-balancer paths, external identity dependencies a operational fencing spolu umožnia dokončiť intended identity journey po definovanom failure scenári. Dve Pods na rovnakom node, tri Pods s jednou databázou bez failoveru alebo dve sites bez synchronizovanej session authority nie sú high-availability architektúra.

Architektúra sa musí pomenovať presne. Multi-node single cluster, single Kubernetes cluster rozprestretý cez availability zones, dva nezávislé Kubernetes clusters v supported multi-cluster v1 modeli a preview multi-cluster v2/stateless model majú odlišné network, cache, database, upgrade a failover semantics. Zamieňanie týchto modelov vedie k nepravdivému RPO/RTO, split-brainu alebo k site failoveru, ktorý zachová login page, ale stratí in-progress authentication, session alebo fresh authorization state.

## 1. Dominantný failure-to-business-recovery lifecycle

```text
business availability objective
→ exact architecture a failure-domain generation
→ active traffic, capacity a dependency topology
→ Pod/node/AZ/cluster/database/network failure
→ health detection a evidence correlation
→ traffic removal, fencing alebo site offlining
→ surviving database/cache/session authority
→ load-balancer/DNS traffic convergence
→ identity journey retry alebo continuation
→ downstream application/business acceptance
→ failback, resynchronization a second-failure test
```

Každá šípka má vlastný timeout a authority. Kubernetes môže odobrať Pod z Service endpoints, ale global load balancer môže site stále považovať za healthy. Database môže promote-nuť writer, ale existing JDBC transactions majú unknown outcome. Infinispan môže stratiť cross-site connectivity, no obe Keycloak sites naďalej odpovedajú. Login canary môže prejsť, zatiaľ čo refresh, broker callback, password reset alebo Admin REST mutation zlyháva. HA verdict preto potrebuje failure-specific journey a business operation, nie iba `/health/ready`.

## 2. Exact HA subject

```yaml
haSubject:
  keycloak:
    version: 26.7.0
    releaseGeneration: kc-release-52
    realm: atlas-prod
    canonicalIssuer: https://sso.atlas.example/realms/atlas-prod
  architecture:
    model: multi-cluster-v1-two-site
    architectureRevision: ha-31
    trafficMode: active-active
    sites:
      - name: az-a
        clusterUid: 27c7...
        keycloakCrUid: 6ae4...
        replicas: 4
        readyCapacityRps: 900
      - name: az-b
        clusterUid: 91d2...
        keycloakCrUid: 8bf1...
        replicas: 4
        readyCapacityRps: 900
  database:
    engine: aurora-postgresql
    clusterId: atlas-keycloak-db-7
    writerGeneration: db-writer-92
    replication: synchronous
    replicationStateGeneration: db-repl-109
    rpoSeconds: 0
    failoverTargetSeconds: 60
  cache:
    model: external-infinispan-cross-site
    clusterGeneration: ispn-44
    siteViewGeneration: xsite-88
    syncMode: synchronous
  traffic:
    globalLoadBalancerRevision: ga-81
    siteLoadBalancerRevisions: [lb-a-31, lb-b-29]
    healthPath: /lb-check
    dnsGeneration: dns-204
    tlsCertificateGeneration: edge-cert-88
  operation:
    journey: authorization-code-plus-refresh
    userSessionId: 4c71...
    operationId: settlement-read-2026-08-02-118
  objectives:
    rtoSeconds: 120
    rpoSeconds: 0
    maxDegradedDuration: PT30M
```

Bez architecture modelu sa `site` môže zamieňať s availability zone, cluster alebo region. Bez traffic mode-u nevieme, či survivor už nesie časť loadu alebo celý load príde naraz. Bez capacity after failure je failover iba routing test. Bez database/cache/site view generation sa split-brain alebo stale session nedá rozlíšiť od aplikácie. Bez journey a business operation ID zelený endpoint nepreukazuje usable identity service.

## 3. Architektonické úrovne

### Single instance

```text
1 Keycloak process
+ 1 database path
+ 1 network path
→ development alebo akceptovaný single point of failure
```

Single instance môže mať database backup a rýchly restart, ale nie je HA. RTO zahŕňa detection, restart, cache/session recovery, DNS/LB a business verification.

### Multi-node single cluster v jednej failure zone

```text
viac Keycloak nodes
→ tolerancia jedného process/node failure
→ shared database a distributed cache
→ stále spoločná zone/network/control-plane failure domain
```

Tento model zvyšuje process availability a throughput, nie zone alebo cluster availability.

### Single cluster across multiple AZs

```text
jeden transparentný Kubernetes/network cluster
→ Pods spread cez zones
→ embedded Infinispan cluster cez low-latency network
→ synchronously replicated HA database
→ jeden regional load-balancer a control plane
```

Je to preferovaný jednoduchší HA model, ak transparentná network a latency podmienky vyhovujú. Stále môže zlyhať celý Kubernetes cluster, regionálny load balancer alebo shared control plane.

### Multi-cluster v1

```text
dva nezávislé Keycloak/Kubernetes clusters
→ external Infinispan cross-site
→ synchronously replicated database
→ global load balancer a site health/fencing automation
```

Tento podporovaný blueprint cieli na dve sites v jednom low-latency regionálnom prostredí. Nie je generickým multi-region active-active modelom.

### Multi-cluster v2 / stateless

```text
dva alebo viac nezávislých clusters
→ synchronously replicated database ako session/volatile-state authority
→ local realm caches + DB outbox invalidation
→ no external Infinispan cross-site
```

V Keycloak 26.7 je tento model preview. Je vhodný na evaluáciu a benchmark, nie na prezentovanie ako stabilný production default bez explicitného risk acceptance.

## 4. Availability objectives a failure catalog

HA design začína failure catalogom:

```text
Pod/process failure
Kubernetes node failure
availability-zone failure
Kubernetes cluster/control-plane failure
load-balancer/site-routing failure
database writer failure
database replication degradation
Infinispan member/site failure
inter-site network partition
DNS/TLS/secret failure
external LDAP/IdP/SMTP dependency failure
bad rollout alebo schema migration
regional outage
```

Každý scenár má vlastný expected RPO, RTO, user-visible symptom a recovery owner. `99.99%` bez catalogu nehovorí, čo systém toleruje. Multi-AZ nepokrýva regionálny outage. Multi-cluster nepokrýva shared database corruption. Backup/restore nepokrýva low RTO.

## 5. Single-cluster multi-AZ prerequisites

Official single-cluster guidance predpokladá transparent networking a round-trip latency pod 10 ms; pod 5 ms je odporúčaný cieľ. Database musí synchronously replikovať medzi zones a tolerovať zone failure. Keycloak Pods sa rozkladajú cez zones aj nodes.

```yaml
spec:
  instances: 6
  scheduling:
    topologySpreadConstraints:
      - maxSkew: 1
        topologyKey: topology.kubernetes.io/zone
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app.kubernetes.io/component: server
      - maxSkew: 1
        topologyKey: kubernetes.io/hostname
        whenUnsatisfiable: DoNotSchedule
        labelSelector:
          matchLabels:
            app.kubernetes.io/component: server
```

Stored scheduling intent nepreukazuje actual placement. Read-back Pod zones, nodes, Pod UIDs a cache topology site/rack/machine. Cluster-autoscaler musí vedieť doplniť capacity v surviving zones.

## 6. Low latency nie je iba priemer

Priemerná RTT 3 ms môže skrývať spikes 100 ms. Keycloak request vykonáva viac synchronous database/cache/network interactions, takže tail latency sa násobí a vytvára queued requests a timeouty.

```text
P50 RTT
P95/P99 RTT
packet loss/retransmits
failure-detection timeout
state-transfer throughput
DB synchronous commit latency
```

Acceptance používa sustained a failure load. Ping nestačí; meraj application transaction a database commit latency počas zone/node loss, rebalance a writer failover.

## 7. Capacity po failure

N+1 alebo site-failure capacity je povinná:

```text
normal total capacity = 1800 RPS
one-site survivor capacity = 900 RPS
normal load = 1100 RPS
→ failover overload, hoci routing funguje
```

Active-active má každá site niesť normálny podiel aj celý critical load po failure podľa objective. Active-passive standby musí byť warm, synchronized, routable a pravidelne testovaný. Database, connection pools, thread pools, external IdPs a downstream APIs musia zvládnuť survivor burst.

Load shedding cez `http-max-queued-requests` môže chrániť survivor pred collapse a vracať bounded `503`, ale musí byť zapojené do retry/backoff a alertingu.

## 8. Database ako shared consistency boundary

Supported HA model používa synchronously replicated database, aby committed identity/session state nestratilo writes pri site failoveri. `RPO=0` platí iba pre úspešne synchronously committed state a zdravú replication generation.

```text
request v site A
→ database transaction
→ synchronous replica acknowledgement
→ commit response
→ site A failure
→ writer/endpoint failover
→ site B reads committed state
```

Ak replication je degraded alebo failover prebehne po ambiguous timeout-e, operation outcome môže byť unknown. Read-back podľa internal object/operation ID je potrebný pred retry. Database corruption alebo operator error sa synchronously replikuje a vyžaduje backup/PITR, nie failover.

## 9. Multi-cluster v1: supported two-site model

V1 používa dva independent Keycloak deployments, synchronously replicated database a external Infinispan s cross-site replication. Keycloak nodes v každej site používajú local cluster; cross-site state/invalidation prechádza cez external Infinispan.

```text
site A Keycloak cluster
↘
 external Infinispan cross-site + synchronous database
↗
site B Keycloak cluster
```

Blueprint je postavený pre dve sites. Tri alebo viac sites menia quorum, replication a fencing complexity a nie sú implicitne podporované týmto modelom. Sites majú byť v low-latency prostredí, typicky dve availability zones v jednom region-e, nie geograficky vzdialené regions.

## 10. Cross-site Infinispan failure semantics

V1 external Infinispan je critical dependency. Pri cross-site connectivity failure nemajú obe sites pokračovať nezávisle bez explicitného offlining/fencing contractu, pretože session/cache state a invalidácie sa môžu rozísť.

```text
cross-site link failure
→ detect degraded Infinispan site
→ choose authoritative/serving site
→ offline/fence affected site
→ global LB removes site
→ repair connectivity
→ resynchronize state
→ verify site health
→ re-enable traffic
```

Failover automation musí používať Infinispan/site evidence, nie iba Keycloak HTTP health. Site, ktorá odpovedá na `/health/ready`, nemusí mať safe cross-site state.

## 11. `/lb-check` a layered health

HA deployment môže zapnúť load-balancer probe `/lb-check`. Tento endpoint je určený pre site-level routing, ale stále nie je business acceptance.

```text
Pod startup/liveness/readiness
→ local process health

site load balancer
→ healthy Pod population

/lb-check
→ site suitability pre global LB podľa feature/modelu

synthetic OIDC/SAML journey
→ protocol usability

business canary
→ downstream authorization a operation
```

Global LB nemá routovať podľa jedného Podu. Site health zahŕňa minimum ready capacity, database writer access, cache/site state, certificate/route a error/latency thresholds.

## 12. Traffic mode: active-active vs active-passive

### Active-active

Obe sites prijímajú traffic. Výhody: resources sa priebežne používajú a failures sa objavia skôr. Nevýhody: cross-site state a capacity musia byť stále zdravé; users môžu prepínať site pri každom requeste, ak LB nemá locality/affinity.

### Active-passive

Jedna site obsluhuje traffic a druhá je warm standby. Výhody: jednoduchšie incident reasoning a menší normal cross-site traffic. Nevýhody: standby drift a cold dependencies sa môžu odhaliť až pri failoveri; kapacita sa neoveruje priebežne.

```text
traffic mode
→ normal load distribution
→ failover trigger
→ survivor load
→ user/session continuity
→ failback policy
```

Traffic mode musí byť explicitný v runbooku a testoch. „Obe sites existujú“ nehovorí, či majú obsluhovať requests.

## 13. Global load balancer, DNS a origin identity

Global load balancer alebo accelerator smeruje canonical hostname na healthy site. Certificate a issuer zostávajú rovnaké naprieč sites. Origin/service routes musia chrániť direct bypass.

```text
sso.atlas.example
→ global LB generation
→ site LB A alebo B
→ Keycloak Pods
```

DNS-only failover má TTL, recursive cache a client connection persistence. Global Accelerator/Anycast má iné convergence semantics. Test musí merať actual request switch time, nie iba control-plane health change.

Direct site hostname môže byť diagnostický, ale token issuer a public action links musia zostať canonical. Site-specific hostname nesmie vytvoriť dva issuers pre jeden realm contract.

## 14. Sticky sessions a site affinity

Affinity znižuje cross-node/cache remote access, ale nesmie byť durability mechanismus. Global site affinity môže zlepšiť latency, no pri site failure musí client bezpečne prejsť na druhú site.

```text
normal request → preferred site
site failure → affinity override
→ survivor site
→ session reload/replicated state
```

Hard cookie pinning na dead site zvyšuje RTO. Authentication session, action token, refresh a offline-token journeys sa testujú po site switchi samostatne.

## 15. Fencing a split-brain authority

Pri network partition môže každá site vidieť vlastné Pods ako healthy. Potrebujeme jedinú authority, ktorá rozhodne, ktorá site smie prijímať writes/traffic.

```text
partition evidence
→ deterministic policy alebo operator decision
→ fence/offline one site
→ verify database/cache authority
→ remove global traffic
```

Fencing môže byť LB disable, Kubernetes scale-to-zero, Infinispan site offline alebo database access revoke podľa modelu. Manuálny fencing má vyšší RTO; automatic fencing môže false-positive vypnúť zdravú site. Decision inputy, timeouty a rollback musia byť explicitné.

## 16. Failback a resynchronization

Failover nie je incident closure. Po oprave sa recovered site nesmie okamžite pridať do trafficu.

```text
repair infrastructure
→ database/cache replication healthy
→ Infinispan site state resynchronized podľa supported procedure
→ Keycloak rollout/config/image parity
→ warm caches/capacity
→ protocol a business canary
→ gradual traffic re-enable
→ second failure test
```

Failback počas stale cache alebo incomplete resync môže znovu zaviesť predecessor state. Evidence zahŕňa replication lag/state transfer, cluster/site views a object/session comparisons.

## 17. Multi-cluster v2 / stateless preview

Keycloak 26.7 poskytuje preview `stateless` feature. Authentication sessions, action tokens a brute-force counters sa presúvajú do database; regular sessions sú už database-backed. Realm/authorization caches zostávajú local a cross-cluster invalidácie používa database outbox/polling. External Infinispan cross-site sa odstráni.

```bash
# Cluster A
bin/kc.sh start \
  --features=stateless \
  --spi-cache-embedded--default--cluster-name=ATLAS-A

# Cluster B
bin/kc.sh start \
  --features=stateless \
  --spi-cache-embedded--default--cluster-name=ATLAS-B
```

Clusters musia mať odlišné names. Model stále vyžaduje synchronously replicated database a low latency. Database CPU a write IOPS môžu približne zdvojnásobiť podľa workloadu a authentication interaction môže mať ďalšiu latency. Preview status znamená possible breaking changes a production risk acceptance.

## 18. V1 versus v2 trade-off

```text
v1
+ supported blueprint
+ external Infinispan cross-site
+ explicit site offlining/resync complexity
- viac infra a environment-specific components

v2 preview
+ no external Infinispan
+ database-backed volatile state a simpler failover
- preview/experimental stability
- higher database CPU/IOPS and latency sensitivity
```

Migrácia v1 → v2 nie je iba odstránenie cache. Treba zmeniť feature/config, cluster names, monitoring, failover automation, capacity model a upgrade runbook. In-progress logins/login-failure state môže mať migration-specific behavior.

## 19. Multi-region hranica

Synchronous database replication a pod-10-ms round-trip typicky obmedzujú supported designs na jeden region alebo equivalent low-latency sites. Multi-region active-active s desiatkami milisekúnd je iný distributed-systems problem a nie je implicitne podporovaný týmito blueprints.

Pre regionálny disaster recovery môže byť vhodnejší active-passive DR s asynchronous backup/replica a explicitným non-zero RPO/RTO, nie predstierané synchronous active-active. Chapter 25 oddelí backup/DR od HA.

## 20. Maintenance a upgrades

Patch upgrades môžu mať rolling/zero-downtime path podľa supported version compatibility. Major/minor multi-cluster upgrades nesmú nechať sites dlhodobo na rozdielnych versions. Pre v2 guidance sa pri major/minor vypnú všetky sites okrem jednej, upgrade/verify sa jedna a potom ostatné.

```text
preflight compatibility + backup
→ drain/offline sites podľa version class
→ upgrade schema/runtime jednej authority site
→ protocol/business verify
→ upgrade remaining sites promptne
→ restore normal traffic
```

Mixed versions writing shared database/cache môžu vytvoriť incompatible assumptions. Upgrade success jednej site nie je closure bez failover/failback a second-site testu.

## 21. External dependencies

Keycloak HA je limitovaná LDAP/AD, external IdPs, SMTP, remote JWKS, KMS/secret manager, DNS a downstream applications. Ak oba sites používajú jeden non-HA LDAP endpoint, login stále zlyhá.

```text
per dependency:
expected endpoint/site affinity
failover/DNS behavior
TLS trust generation
timeout/retry/circuit breaking
capacity after failure
```

Brokered login, password reset a local-password login môžu mať odlišnú availability. HA SLO môže rozlišovať journeys, nie iba aggregate requests.

## 22. RPO/RTO matrix

| Failure | Expected data loss | Target recovery | Required evidence |
|---|---:|---:|---|
| Pod failure | 0 pre committed persistent state | sekundy | endpoint removal, session retry |
| Node failure | 0 | desiatky sekúnd | reschedule, cache/database recovery |
| AZ failure | 0 pri healthy sync replication | minúty | survivor capacity, writer/cache topology |
| Site/cluster failure | 0 v healthy v1/v2 sync model | minúty | global LB, DB/cache/session continuity |
| Database corruption | podľa backup/PITR | hodiny | restore generation, reconciliation |
| Region failure | architecture-specific, často >0 | hodiny | DR plan, DNS, restored dependencies |

Tabuľka je contract, nie wish list. Každý row potrebuje measured exercise a dated evidence.

## 23. Chaos a failure testing

Controlled tests:

```text
kill one Pod
cordon/drain one node
remove one AZ worker pool
block inter-site cache network
fail database writer
remove one site from global LB
expire/rotate site certificate
saturate survivor capacity
inject latency/packet loss
perform rolling/major upgrade rehearsal
```

Experiment má stop conditions a rollback. Network partition test nesmie poškodiť production bez fencing authority. Synthetic journey používa non-privileged test realm/user/client a durable operation ID.

## 24. Incident `KC-PAY-76`

Atlas deklaroval active-active HA medzi dvoma Kubernetes clusters. Každá site mala štyri Pods, ale survivor site zvládla iba 55 % production peak loadu. Global LB sledoval `/health/ready`; pri cross-site Infinispan partition zostali obe sites Ready a pokračovali v trafficu. Invalidácie sa rozdelili a site B vydávala predecessor role claims.

Database synchronous replication bola zdravá, no external Infinispan site state nie. Automation nevykonala offlining/fencing. Keď operátor manuálne odobral site B, všetok traffic prešiel na site A, pool/thread queues sa saturovali a `/lb-check` začal flappovať. DNS clients držali persistent connections ešte niekoľko minút.

```text
HTTP-only site health
→ split cache authority neodhalená
→ both sites serve stale/divergent state

insufficient survivor capacity
→ routing failover succeeds
→ identity service collapses under load
```

Recovery pridala Infinispan/site health do fencing decisionu, deterministic authoritative-site runbook, survivor load shedding a capacity reserve. Global LB používa `/lb-check` plus minimum ready capacity a synthetic refresh/business canary. Failback vyžaduje cache resync a object/session comparison. V2/stateless zostalo oddelené v preview test environment-e.

## 25. Evidence-preserving containment a recovery

Zachovaj architecture diagram/revision, cluster/site/AZ UIDs, Keycloak/image/config generations, database writer/replication state, Infinispan site views/state-transfer evidence, LB/DNS/health configuration, Pod placement, capacity metrics, network RTT/loss, certificate/trust generations, user/session/token IDs a business operation IDs.

Containment môže fence-nuť degraded site, znížiť accepted traffic, zastaviť rollout/mutations a chrániť database/cache authority. Recovery obnoví replication, resynchronizuje state, doplní capacity, vykoná protocol/business canaries a až potom controlled failback.

## 26. Acceptance matrix

Positive:

```text
normal active traffic
→ expected site distribution
→ healthy DB/cache/session state
→ login, refresh a business operation succeed
```

Recovery:

```text
Pod/node/AZ/site alebo writer failure
→ detection
→ fence/route convergence
→ survivor capacity
→ session/business continuity podľa RPO/RTO
→ resync a failback
```

Forbidden:

```text
both partitioned sites continue writes bez authority
→ fencing policy rejects

survivor capacity below defined failure load
→ release/HA gate rejects

preview v2 označené ako supported production default
→ architecture review rejects

canonical realm používa dva issuer hostnames
→ protocol gate rejects
```

Second-failure test zopakuje failure po failbacku alebo počas degraded one-site state. Second-journey test overí login, refresh, offline token, broker callback, reset link, Admin REST a downstream operation.

## Kontrolné otázky

- Ktorý exact HA model používame: multi-node, multi-AZ single-cluster, v1 alebo preview v2?
- Ktoré failures architektúra toleruje a ktoré nie?
- Je inter-node/site/database RTT pod required limit aj na P99?
- Zvládne survivor celý defined failure load vrátane database a dependencies?
- Kto rozhoduje fencing a authoritative site pri partition?
- Sleduje LB site safety, nie iba jeden HTTP health endpoint?
- Sú database a cache/session authorities synchronizované pred failbackom?
- Zostáva issuer/hostname rovnaký naprieč sites?
- Je upgrade procedure compatible s shared schema/cache modelom?
- Sú backup/DR oddelené od HA a majú vlastné RPO/RTO?
- Prešli Pod, node, AZ, site, database, network-partition, capacity, upgrade, failback a second-failure testy?

## Primárne zdroje

- [Keycloak — High availability overview](https://www.keycloak.org/high-availability/introduction)
- [Keycloak — Single-cluster deployments](https://www.keycloak.org/high-availability/single-cluster/introduction)
- [Keycloak — Building blocks for single-cluster deployments](https://www.keycloak.org/high-availability/single-cluster/building-blocks)
- [Keycloak — Multi-cluster deployments v1](https://www.keycloak.org/high-availability/multi-cluster/introduction)
- [Keycloak — Concepts for multi-cluster deployments](https://www.keycloak.org/high-availability/multi-cluster/concepts)
- [Keycloak — Health checks for multi-cluster deployments](https://www.keycloak.org/high-availability/multi-cluster/health-checks)
- [Keycloak — Multi-cluster deployments v2](https://www.keycloak.org/high-availability/multi-cluster-v2/introduction)
- [Keycloak — Managing upgrades v2](https://www.keycloak.org/high-availability/multi-cluster-v2/upgrades)
