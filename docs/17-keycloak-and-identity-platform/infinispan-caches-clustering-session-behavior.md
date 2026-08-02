# Infinispan caches, clustering a session behavior

Keycloak cache nie je jeden transparentný memory layer. Embedded Infinispan drží local, replicated, distributed a invalidation caches s odlišnou authority a failure semantics. Realm, user a authorization data zostávajú authoritative v databáze a cache ich urýchľuje. Regular user/client sessions sú pri default persistent-session modeli uložené v databáze a načítané do cache. Pri volatile-session modeli sa cache stáva source of truth pre sessions. Authentication sessions, action tokens a brute-force counters majú vlastné caches a lifecycle. Výrok „session je v Infinispane“ preto nestačí na posúdenie durability ani failoveru.

Cluster membership navyše nie je to isté ako application readiness. Pod môže byť Ready, ale ešte nemusí mať stabilnú cache topology. Dva Pods môžu používať rovnakú databázu a napriek tomu vytvoriť oddelené clusters, čo vedie k stale invalidation state. Naopak dva deploymenty, ktoré mali byť oddelené, sa cez default `jdbc-ping` môžu nájsť v spoločnej databáze a nechcene vytvoriť jeden cluster.

## 1. Dominantný authoritative-state-to-cache lifecycle

```text
realm/user/session/authentication operation
→ exact database a Keycloak cluster generation
→ cache type a authority model
→ owner/replica/topology resolution
→ local alebo remote cache read/write
→ database commit podľa state type
→ work/invalidation message
→ other-node visibility
→ protocol response a next request
→ node/site failure, recovery a second-session test
```

Cache hit preukazuje iba value v konkrétnom node/topology generation. Cache miss neznamená data loss, ak database je source of truth. Database row nepreukazuje, že other nodes invalidovali predecessor value. Session cookie alebo token môže odkazovať na session, ktorá je durable v databáze, volatile iba v cache alebo už revoked, ale stale node ju ešte neinvalidoval.

## 2. Exact cache a cluster subject

```yaml
cacheSubject:
  keycloak:
    version: 26.7.0
    deploymentGeneration: kc-2026-08-02-25
    podUid: b874...
    nodeName: atlas-kc-a-2
  cluster:
    cacheMode: ispn
    clusterName: atlas-prod-kc
    transportStack: jdbc-ping
    topologyId: 412
    viewId: 88
    members: [atlas-kc-a-1, atlas-kc-a-2, atlas-kc-a-3]
    siteName: az-a
    rackName: rack-4
    machineName: node-17
  state:
    cacheName: sessions
    authority: database-persistent-with-memory-cache
    keyHash: sha256:10fe...
    sessionId: 4c71...
    owners: [atlas-kc-a-2]
    databaseGeneration: db-tx-991
    cacheEntryGeneration: session-cache-182
  configuration:
    persistentUserSessions: true
    cacheConfigRevision: cache-44
    maxCount: 10000
    affinityRevision: lb-71
```

Bez cluster/view/topology identity sa rebalancing alebo split cluster interpretuje ako náhodný miss. Bez authority modelu sa eviction zamieňa s data loss. Bez database generation sa stale cache nedá porovnať s durable state. Bez site/rack/machine labels sa `num_owners=2` môže fyzicky ocitnúť v rovnakej failure domain.

## 3. Cache modes

Production `start` používa distributed Infinispan cache:

```bash
bin/kc.sh start --cache=ispn
```

Development `start-dev` používa local cache a nevytvára distributed cluster. Local mode je vhodný na development, nie na multi-node production.

```text
cache=local
→ každý process má izolovaný cache state
→ no cluster invalidation/distribution

cache=ispn
→ JGroups transport a Infinispan cluster
→ distributed/replicated/invalidation semantics
```

Pod count > 1 s `cache=local` môže vytvoriť inconsistent sessions, brute-force counters a cached configuration. Load balancer affinity tento základný problém neopraví, pretože failover request prejde na node bez state-u.

## 4. Cache categories

Dôležité caches:

```text
realms, users, authorization
→ local/invalidation-oriented entity caches
→ database authoritative
→ work cache distribuuje invalidácie

sessions, clientSessions
→ regular user/client session cache
→ pri persistent sessions database authoritative

offlineSessions, offlineClientSessions
→ offline session cache
→ database-backed, on-demand reload

authenticationSessions
→ pre-login authentication transaction state

actionTokens
→ action-token metadata a replay/lifecycle state

loginFailures
→ brute-force failed-login state

work
→ cluster invalidation/control messages
```

Každý cache type má iný blast radius. Stale realm/client cache môže publikovať predecessor mapper alebo redirect policy. Strata authentication session preruší login flow, ale nevytvorí automaticky user-session data loss. Strata loginFailures môže oslabiť brute-force enforcement. Work cache failure môže ponechať stale local entity caches.

## 5. Persistent regular sessions

Pri default persistent-session modeli sa regular user a client sessions ukladajú v databáze a cache poskytuje performance layer. Session cache má defaultný limit počtu entries na node; evicted session sa načíta z databázy.

```text
login commit
→ user/client session persisted
→ session cached na owner node
→ subsequent request cache hit alebo database reload
```

Node failure preto nemusí znamenať session loss. Môže však zvýšiť database load a latency, kým sa cache znovu naplní. Database failover a connection pool kapitola zostávajú critical dependency.

Persistent session row existence nepreukazuje, že session je stále authorized. User disable, role removal alebo logout musia ovplyvniť session/token acceptance podľa vlastného lifecycle-u.

## 6. Volatile user sessions

Vypnutie `persistent-user-sessions` presunie regular sessions do cache-only authority:

```bash
bin/kc.sh start \
  --features-disabled=persistent-user-sessions
```

```text
volatile session
→ cache is source of truth
→ all-node/cache loss = session loss
→ higher memory demand
```

Tento model môže znížiť database writes, ale zvyšuje memory a availability risk. Keycloak upravuje cache copies/size pre volatile sessions, no operator musí testovať full-cluster restart, topology loss a capacity. Volatile mode nie je synonymum „stateless“.

## 7. Offline sessions

Offline tokens vytvárajú offline user/client sessions. Caches `offlineSessions` a `offlineClientSessions` majú defaultný per-node limit a evicted entries sa načítajú z database.

Offline session lifetime môže byť výrazne dlhší než browser session. Cache reset neznamená revocation. Incident closure musí kontrolovať database-backed offline descendants, nie iba current in-memory entries.

## 8. Authentication sessions, action tokens a brute-force state

Authentication session existuje pred user session a spája browser tab, flow execution, client a protocol state. Action-token cache chráni asynchrónne links/required actions. `loginFailures` koordinuje brute-force data medzi nodes.

```text
node loss počas loginu
→ authentication journey môže zlyhať alebo retryovať
→ user session ešte nemusí existovať

node loss po login commit-e
→ persistent user session sa môže reloadnúť
```

Tieto state types majú rozdielne RPO. Testovanie iba refresh tokenu nepokrýva password reset alebo multi-step broker flow.

## 9. Stateless preview mode

Keycloak 26.7 obsahuje preview `stateless` feature. Authentication sessions, action tokens a login-failure data sa ukladajú do database a user entity data sa necachujú; realm a authorization data zostávajú cached a `work` cache sa používa pre invalidácie v rámci clusteru. Medzi nezávislými clusters sa invalidácie môžu prenášať cez database outbox.

```bash
bin/kc.sh start --features=stateless
```

Preview znamená, že feature nie je stabilný production default a môže mať breaking changes. Dokumentácia ju musí jasne označiť. Vyšší database CPU/write IOPS a latency sú súčasťou trade-offu.

Každý nezávislý cluster potrebuje unique cluster name. Používanie odlišných cluster names bez stateless cross-cluster invalidation vedie k stale caches a incorrect behavior.

## 10. Cluster discovery cez `jdbc-ping`

Default production transport stack používa `jdbc-ping`, ktorý eviduje nodes v configured database. Transparentná network connectivity musí umožniť JGroups TCP communication medzi Pods.

```text
Pod startup
→ writes/reads discovery record v database
→ discovers members
→ establishes JGroups channels
→ installs cluster view
→ Infinispan topology rebalance
```

Database discovery success nepreukazuje network reachability medzi nodes. Kubernetes NetworkPolicy, DNS alebo service mesh môže blokovať JGroups traffic. Startup log a cluster member metrics/read-back musia potvrdiť expected view.

Dva environments zdieľajúce database a default cluster name môžu objaviť jeden druhého. Oddelenie vyžaduje database/schema boundary alebo supported cluster design, nie náhodné network blocky.

## 11. Cluster a node names

Experimental cluster-name option:

```bash
bin/kc.sh start \
  --spi-cache-embedded--default--cluster-name=atlas-prod-kc \
  --spi-cache-embedded--default--node-name=atlas-kc-a-2
```

Stable human-readable node name zlepšuje log/metric correlation. Cluster name musí byť súčasť deployment contractu. Rozdelenie same production workloadu na dva cluster names bez cross-cluster invalidation je unsafe mimo explicitného stateless/multi-cluster modelu.

## 12. Ownership, topology a rebalancing

Distributed cache entries majú owners. Pri node join/leave Infinispan mení topology a presúva state. Rebalance spotrebuje CPU, memory a network. Autoscaling príliš rýchlo môže udržiavať cluster v neustálej topology zmene.

```text
Pod join
→ new cluster view
→ segment ownership recalculated
→ state transfer
→ steady topology
```

Readiness po process štarte nemusí znamenať completed rebalance. Performance acceptance sleduje topology changes, state transfer, remote gets a request latency.

## 13. Site, rack a machine topology awareness

Keycloak môže dostať topology labels, aby Infinispan neumiestnil owners do rovnakej failure domain. Pri `num_owners=2` má zmysel iba vtedy, ak owners nie sú na tom istom node/rack/site.

```text
site = availability zone
rack = Kubernetes node pool alebo physical rack
machine = node/VM identity
```

Kubernetes labels a scheduling musia byť consistent s cache topology metadata. Nesprávny `site-name` môže vytvoriť false redundancy. Pri default persistent sessions sú user/client sessions durable v database, ale ostatné distributed caches a temporary state stále závisia od topology.

## 14. Session affinity

Distributed cache umožňuje request na ľubovoľný node, ale affinity preferuje node, ktorý session vytvoril. Znižuje remote cache access, state transfer a network cost.

```text
AUTH_SESSION_ID alebo load-balancer affinity key
→ route subsequent requests k primary owner/node
→ fallback na iný node pri failure
```

Affinity nesmie byť hard dependency. Ak fallback zlyhá, cluster/cache model nie je HA. Cookie format a owner hint sa nemajú používať ako authorization signal.

## 15. Cache size a eviction

Cache max count obmedzuje memory:

```bash
bin/kc.sh start \
  --cache-embedded-sessions-max-count=10000 \
  --cache-embedded-offline-sessions-max-count=10000
```

Presné option names závisia od cache option schema; generické pattern je `--cache-embedded-${CACHE_NAME}-max-count`. Pri persistent sessions eviction znamená database reload. Pri cache-authoritative state môže znamenať behavior change alebo loss podľa cache type.

Memory sizing musí zohľadniť entry size, owners, authentication peaks, realm/user cache, JVM heap a off-heap/native overhead. Count bez workload distribution nestačí.

## 16. Custom cache configuration

XML override default caches je technicky možné, ale nie bežný supported path. Preferujú sa `cache-*` options. Ak sa default cache config mutuje, `--cache-config-mutate=true` explicitne priznáva deviation.

```bash
bin/kc.sh start \
  --cache-config-file=cache-ispn.xml \
  --cache-config-mutate=true
```

Custom XML je high-risk extension. Potrebuje version compatibility, full cache inventory, upgrade diff a failure testing. Kopírovanie starej default XML môže zablokovať nové cache/settings po upgrade.

## 17. Remote Infinispan

Multi-cluster v1 používa external Infinispan podľa HA guide. Keycloak môže používať remote host/port/credentials/TLS options. External cache sa stáva samostatným availability a security dependency.

```bash
bin/kc.sh start \
  --cache-remote-host=infinispan.identity-prod.svc \
  --cache-remote-port=11222 \
  --cache-remote-username=keycloak \
  --cache-remote-password="${KC_CACHE_REMOTE_PASSWORD}" \
  --cache-remote-tls-enabled=true
```

Vypnutie remote TLS nie je production hardening. Remote cache credentials, certificate/trust generation, cache schema/marshalling compatibility a site state patria do evidence.

## 18. Cache invalidation a `work`

Entity mutation typicky commitne database a odošle invalidation cez `work` cache. Other nodes odstránia stale local entry a pri ďalšom read-e načítajú successor state.

```text
client mapper update na node A
→ database commit
→ work invalidation
→ node B evicts predecessor client cache
→ next token request načíta successor mapper
```

Ak invalidation chýba, node B môže vydávať predecessor token claims. Restart B môže incident „opraviť“, ale nepreukazuje zdravý mechanismus. Test musí vykonať second update bez restartu a overiť všetky nodes.

## 19. Cluster observability

Zachytávaj:

```text
cluster view a member count
cache topology ID
rebalance/state transfer status
remote/local hit ratio
entry count a memory
invalidations/work messages
JGroups transport errors
node restarts a view changes
session reload/database load
```

Aggregate member count bez expected deployment inventory nestačí. Split cluster môže mať dva zelené member counts menšie než expected. Stable node names a Pod UIDs umožnia correlation.

Debug applied Infinispan configuration:

```bash
bin/kc.sh start \
  --log-level='info,org.keycloak.connections.infinispan.DefaultInfinispanConnectionProviderFactory:debug'
```

Debug output je temporary evidence; môže zvýšiť log volume.

## 20. Node failure a full restart

Node failure pri persistent sessions:

```text
owner node dies
→ load balancer reroutes
→ cache miss/remote owner/database reload
→ session continues podľa durable state
```

Full cluster restart:

```text
persistent sessions
→ reload from database

volatile sessions
→ lost

authentication in progress
→ likely interrupted podľa persisted/cache modelu
```

Acceptance musí testovať browser user session, refresh token, offline token, action token, brute-force state a in-progress login separately.

## 21. Incident `KC-PAY-74`

Atlas spustil production s tromi Pods, ale jeden mal `cache=local` kvôli environment override-u. Load balancer affinity skrývala problém, kým Pod A nebol drain-nutý. Password reset a broker login flows stratili authentication/action state na fallback node.

Ďalšie dva Pods používali `cache=ispn`, ale jeden mal odlišný cluster name. Oba clusters zdieľali database; persistent user sessions sa reloadli, no realm/client invalidations medzi clusters nefungovali. Jeden node vydával tokeny s predecessor protocol mapperom.

```text
mixed local/distributed cache config
→ partial session continuity

split cluster name + shared database
→ durable rows shared, invalidations isolated
→ stale token projection
```

Operátori restartli stale Pod a incident zmizol, ale mechanismus zostal chybný. Recovery zjednotila image/config hash, cluster name a transport, pridala expected member/topology gate, test invalidation bez restartu a oddelila preview stateless experiment od production deploymentu.

## 22. Evidence-preserving containment a recovery

Zachovaj image/config hashes, `cache` mode, cluster/node/site/rack/machine names, member views a topology IDs per Pod, applied cache configuration, database session/entity generation, affinity config, cache metrics, JGroups logs, discovery rows, Pod/network events a affected session/token IDs.

Containment môže odobrať misconfigured Pod z trafficu, zastaviť autoscaling/rebalance a zablokovať risky admin changes. Recovery zjednotí cluster generation, obnoví discovery/network, synchronizuje external sites podľa supported procedure a overí cache invalidation i session continuity bez restart workaroundu.

## 23. Acceptance matrix

Positive:

```text
login na node A
→ session durable/cached podľa modelu
→ request na node B
→ intended continuity a authorization
```

Recovery:

```text
owner node failure
→ reroute
→ database/remote cache recovery
→ second request succeeds
```

Forbidden:

```text
cache=local v multi-Pod production
→ deployment policy rejects

unexpected cluster name/member count
→ readiness/admission/operational gate rejects

remote Infinispan bez TLS/auth
→ security policy rejects
```

Second-invalidation test mení client/role/user state a overí successor result na každom node bez restartu. Second-mode test vykoná full-cluster restart a porovná persistent, volatile a preview stateless expectations.

## Kontrolné otázky

- Ktorá cache drží ktorý state a kto je authoritative writer?
- Sú regular sessions persistent alebo volatile?
- Čo sa stane pri eviction, node loss a full-cluster restart?
- Používajú všetky Pods rovnaký cache mode, cluster name a transport generation?
- Zodpovedá expected member view deployment inventory?
- Sú owners rozložené cez skutočné failure domains?
- Funguje affinity ako optimalizácia, nie hard dependency?
- Prechádzajú invalidácie medzi všetkými nodes/clusters podľa supported modelu?
- Je stateless/multi-cluster v2 jasne označený ako preview?
- Prešli node-loss, split-cluster, stale-invalidation, full-restart, offline-token a second-session testy?

## Primárne zdroje

- [Keycloak — Configuring distributed caches](https://www.keycloak.org/server/caching)
- [Keycloak — High availability overview](https://www.keycloak.org/high-availability/introduction)
- [Keycloak — Concepts for multi-cluster deployments](https://www.keycloak.org/high-availability/multi-cluster/concepts)
- [Keycloak — Multi-cluster deployments v2](https://www.keycloak.org/high-availability/multi-cluster-v2/introduction)
- [Keycloak — Storing sessions in Keycloak 26](https://www.keycloak.org/2024/12/storing-sessions-in-kc26)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Database, transactions, connection pools a schema lifecycle](database-transactions-connection-pools-schema-lifecycle.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Keycloak Operator a Kubernetes deployment →](keycloak-operator-kubernetes-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
