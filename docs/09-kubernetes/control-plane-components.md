# Control plane components

Kubernetes control plane nie je jeden process ani jeden health endpoint. Je to sada navzájom previazaných capabilities, ktoré musia zachovať API read/write path, persistent cluster state, scheduling, reconciliation a integration transitions.

Dominantný lifecycle:

```text
client intent a cluster endpoint
→ API load balancer a server readiness
→ authentication a authorization
→ mutation, validation a admission
→ etcd persistence a watch publication
→ scheduler alebo controller queue
→ leader-owned decision a API write
→ cloud/platform integration
→ effective workload transition
→ capability-specific verification a recovery
```

Pri incidente sa nepýtaj iba „je control plane up?“. Pýtaj sa:

```text
Ktorá capability mala vykonať ktorý transition?
Bol request prijatý, povolený, admitted a persistovaný?
Videli ho watches a queues?
Mal príslušný component leadera, permissions a capacity?
Bol jeho output uložený a následne vykonaný?
```

## 1. Atlas control-plane subject

Atlas Payments rollout `4.2.0` používa:

```text
cluster: atlas-prod-eu1
API endpoint: api.atlas-prod-eu1.example
Kubernetes version: v1.x supported release line
Deployment UID/generation: D42/12
expected Pods: 6
control-plane topology:
  3 API servers za load balancerom
  3-member etcd cluster
  3 scheduler replicas s leader election
  3 controller-manager replicas s leader election
admission generation: AP17
cloud-controller generation: CC9
required outcome:
  write/read/watch funguje
  generation 12 sa reconcile-ne
  Pods sa naplánujú
  Service traffic vykoná payment transaction
```

Control-plane success nie je iba:

```text
TCP 6443 open
```

Je to:

```text
request reaches correct cluster
+ identity/policy decision is correct
+ object persists durably
+ watches and queues progress
+ scheduler/controllers produce valid outputs
+ outputs reach workload and business state
```

## 2. Capability inventory

| Capability | Hlavný owner | Primary state/output |
|---|---|---|
| API serving | API server + load balancer | request/response, discovery, read/write/watch |
| Persistence | etcd cez API server | durable object revisions |
| Authentication | API server authenticators | user/groups/extra identity |
| Authorization | API server authorizers | allow/deny verdict |
| Admission | built-in plugins/webhooks | mutated alebo accepted/rejected object |
| Scheduling | kube-scheduler | Pod-to-Node binding |
| Built-in reconciliation | kube-controller-manager | dependent objects a status |
| Cloud reconciliation | cloud-controller-manager/provider controllers | Nodes, routes, load balancers podľa platformy |
| API extension | CRDs/aggregated APIs | additional resource contracts |
| Leadership | Lease coordination | active scheduler/controller instance |

Jedna capability môže byť healthy, kým iná zlyháva. `kubectl get` môže fungovať pri nefunkčných writes. Existing Pods môžu bežať pri nefunkčnom schedulerovi. API môže byť ready pre reads, ale matching writes môžu timeoutovať na admission webhooku.

## 3. API endpoint a load-balancer boundary

Client path:

```text
kubeconfig context
→ DNS
→ route/firewall
→ API load balancer
→ selected API server
→ TLS a HTTP request
```

Load balancer má odstraňovať unhealthy API instances, ale jeho TCP healthcheck nepreukazuje semantic API readiness.

Relevantné stavy:

- `/livez` — process nemá byť reštartovaný;
- `/readyz` — instance je pripravená obsluhovať relevantný traffic;
- verbose readiness — ukáže jednotlivé failing checks;
- API request metrics — ukážu latency, response codes a saturation.

### Failure boundary: TCP success, API write failure

```text
load balancer otvorí TCP
→ API process odpovie
→ readiness dependency na etcd zlyháva
→ read alebo cached path môže čiastočne fungovať
→ writes timeoutujú
```

Health model musí testovať capability, ktorú traffic potrebuje.

## 4. API write-path subject

Pre jeden write zafixuj:

```text
cluster endpoint a CA
API server instance/request ID
caller identity a groups
verb, GVR, namespace, name/subresource
request object digest
field manager a preconditions
admission configuration generation
response code a latency
etcd revision/resourceVersion outcome
audit record
```

Rovnaký error text bez request subjectu môže patriť inému clusteru, API serveru, webhooku alebo object generation.

## 5. Authentication, authorization a admission

### Authentication

Odpovedá:

```text
Kto je caller?
```

Výsledok zahŕňa user, groups a extra attributes.

### Authorization

Odpovedá:

```text
Môže táto identita vykonať verb nad týmto resource/subresource v tomto scope?
```

`pods` a `pods/exec` sú odlišné authorization targets.

### Admission

Po identity a authorization rozhodnutí môže request:

- mutovať;
- defaultovať;
- validovať;
- odmietnuť;
- podliehať quota alebo policy.

Tieto boundaries majú odlišné evidence:

```text
Unauthorized
≠ Forbidden
≠ admission rejection
≠ schema validation error
≠ persistence timeout
```

## 6. Admission webhook ako synchronous dependency

Matching API request čaká na webhook response podľa timeout/failure policy.

Webhook contract potrebuje:

- narrow match scope;
- vysokú dostupnosť;
- nízku latency;
- správny CA/DNS/network path;
- bounded timeout;
- reviewovaný fail-open/fail-closed model;
- side-effect discipline;
- upgrade compatibility;
- break-glass postup.

### Failure boundary: webhook závisí od workloadu, ktorý sám blokuje

Policy webhook mal jednu repliku. Pri rollout-e starej repliky sa nový Pod nedal vytvoriť, pretože webhook fail-closed blokoval všetky Pod creates vrátane vlastného replacementu.

```text
webhook unavailable
→ API odmietne create webhook Podu
→ webhook sa nemôže obnoviť cez bežný controller path
→ matching writes v clusteri ostanú blokované
```

Availability dependency graph musí zabrániť self-deadlocku.

## 7. Persistence cez etcd

API server používa etcd ako authoritative backing store pre Kubernetes API state.

Write transition:

```text
admitted object
→ etcd quorum proposal
→ durable commit
→ new revision/resourceVersion
→ API response
→ watch delivery
```

etcd potrebuje:

- quorum;
- stabilnú nízku disk latency;
- dostatok capacity/IOPS;
- nízku peer latency;
- správne certificates;
- compaction/defragmentation policy;
- quota monitoring;
- snapshots a testovaný restore.

## 8. Quorum a availability

Pri troch voting members treba väčšinu dvoch. Pri piatich troch.

Strata quorum znamená:

```text
existing workload processes môžu pokračovať
+ niektoré reads môžu byť dočasne možné podľa pathu
− bezpečné persistent writes nemôžu pokračovať
− controllers/scheduler nemôžu spoľahlivo commitovať transitions
```

Neobnovuj quorum náhodným force-new-cluster postupom bez identity, revision a restore protocolu. Nesprávna obnova môže vytvoriť divergent cluster state.

## 9. etcd latency ako system-wide amplifier

Pomalé fsync/commit operations spôsobia:

```text
etcd latency
→ API write latency a timeouts
→ watch disconnects alebo lag
→ controller client retries
→ scheduler/controller queues rastú
→ viac API pressure
→ ďalšia latency
```

Ide o reinforcing loop. Restart clients nemusí odstrániť storage príčinu a môže pressure zvýšiť.

Observation points:

- etcd leader/member health;
- proposal failures;
- fsync a commit latency;
- database size/quota alarms;
- peer RTT;
- API etcd request duration;
- watch reconnects;
- controller client throttling.

## 10. Scheduler capability

Scheduler input:

```text
Pod bez nodeName
+ current Node/resource/topology inventory
+ scheduling profile/plugins
```

Output:

```text
binding na konkrétny Node
```

Scheduler:

- filtruje hard constraints;
- skóruje candidates;
- rieši queueing/backoff a podľa konfigurácie preemption;
- zapisuje assignment cez API.

Nevytvára container a neoveruje readiness.

### Failure boundary: scheduler down

```text
existing assigned Pods bežia
new Pods existujú v API bez nodeName
→ Pending
```

Toto je iný incident než Pod s `nodeName`, ktorý nevie vytvoriť sandbox alebo container.

## 11. Scheduler subject a queues

Zafixuj:

```text
Pod UID/generation
schedulerName
active scheduler leader
scheduler version/profile digest
queue state a attempts
Node inventory generation
requests/constraints/PVC/host-port state
binding audit
```

Observation points:

- `FailedScheduling` Events;
- pending/unschedulable queue metrics;
- scheduling attempt latency;
- plugin latency/reasons;
- leader Lease;
- API conflicts/throttling;
- Node/PVC/topology state.

Permanent unschedulable input nemá byť zamieňaný s nefunkčným scheduler processom.

## 12. Controller-manager capability

`kube-controller-manager` hostí viac built-in control loops, napríklad:

- Deployment/ReplicaSet-related controllers;
- Node controller;
- Job controller;
- EndpointSlice controller;
- Namespace controller;
- ServiceAccount/token-related controllers;
- garbage collector;
- certificate controllers;
- attach/detach controller podľa architektúry.

Controller-manager process môže byť healthy, ale konkrétna queue môže byť preťažená alebo controller môže zlyhávať na permissions či object contracte.

### Failure boundary: API writes fungujú, dependents nevznikajú

```text
Deployment create accepted
→ etcd persistence successful
→ controller-manager bez active leader alebo reconcile capability
→ žiadny ReplicaSet
```

Scheduler nie je relevantný, kým Pod objects nevzniknú.

## 13. Leader election

Scheduler a controller-manager replicas typicky koordinujú active leadera cez Lease.

Leader election poskytuje:

- active instance selection;
- failover po lease loss;
- standby readiness.

Neposkytuje:

- exactly-once execution;
- idempotenciu;
- external transaction atomicity;
- nulový overlap pri partitions/timeouts;
- automatický queue recovery verdict.

Po leader transition treba overiť queue progress, stale in-flight operations a generation closure.

## 14. Cloud-controller boundary

Cloud-controller-manager alebo provider-specific controllers môžu spravovať:

- Node cloud identity/initialization;
- routes;
- Service load balancers;
- cloud metadata a lifecycle.

Core API môže byť healthy, hoci:

- LoadBalancer Service ostáva pending;
- Node má cloud initialization taint;
- route sa nevytvorí;
- cloud API rate limituje requests.

Cloud API request IDs, workload identity, region/account a external resource IDs patria do control-plane subjectu.

## 15. Aggregated APIs a CRDs

### CRD

Používa core API server storage/schema model.

### Aggregated API

`APIService` smeruje danú API group/version na extension API server.

Failure aggregated API môže poškodiť konkrétnu discovery/resource capability bez toho, aby core Pods API bolo down.

Diagnostika rozlišuje:

- core discovery;
- `APIService` availability condition;
- extension Service/endpoints/TLS;
- aggregation proxy path;
- extension backend logs.

## 16. Certificates, signing keys a time

Control plane závisí od:

- API server serving certificates;
- client certificates;
- etcd peer/client certificates;
- service account signing keys;
- webhook certificates;
- front-proxy/aggregation trust;
- presného času.

Expiry alebo clock skew môže spôsobiť:

- TLS failures;
- unauthorized component requests;
- webhook outage;
- etcd peer loss;
- leader-election instability;
- token validation failure.

Certificate inventory potrebuje ownera, expiration monitoring, rotation protocol a post-rotation verification.

## 17. Static Pod a packaging boundary

V kubeadm-like clusteri môžu control-plane components bežať ako static Pods:

```text
local manifest
→ kubelet
→ container runtime
→ mirror Pod
```

Pri nefunkčnom API:

- `kubectl logs` nemusí fungovať;
- mirror Pod nemusí byť authoritative;
- treba host filesystem, kubelet, runtime a journal evidence;
- restart mechanism je zmena local manifestu alebo kubelet/runtime lifecycle podľa platformy.

Iné distribúcie môžu používať systemd, dedicated VMs alebo managed provider control plane. Diagnostika musí poznať packaging a ownership.

## 18. Stacked a external etcd

### Stacked

etcd zdieľa control-plane Nodes.

Výhoda: jednoduchšia topológia.

Riziko: zdieľaný host/resource/failure domain.

### External

etcd má samostatné Nodes a lifecycle.

Výhoda: oddelený failure/resource domain.

Riziko: viac network, certificate, bootstrap a restore complexity.

Topológia musí byť súčasťou incident subjectu; inak operator môže diagnostikovať nesprávny host alebo failure domain.

## 19. Worked failure: reads fungujú, writes timeoutujú a rollout laguje

Atlas observuje:

- `kubectl get pods` väčšinou funguje;
- create/update requests občas timeoutujú;
- Deployment generation 12 má starý `observedGeneration`;
- scheduler a controller queues rastú;
- existujúce Payments Pods ďalej obsluhujú traffic.

### 1. Zafixuj subject

```text
cluster endpoint/CA a API server instances
request IDs, verbs, GVRs a response latency
API server readiness a version
admission generation a matching webhook inventory
etcd cluster/member IDs, leader, revision, DB size a disk
scheduler/controller leader a queue generations
certificate/time state
audit sink/config generation
last upgrade/config change
Deployment D42 generation 12
required workload/business outcome
```

### 2. Competing hypotheses

1. API load balancer posiela writes na unready instance.
2. Authentication alebo authorization backend je pomalý.
3. Matching admission webhook timeoutuje.
4. etcd disk fsync latency je vysoká.
5. etcd stráca quorum alebo leadera.
6. API server je saturovaný inflight requests/watchmi.
7. Audit sink/backpressure blokuje request path podľa configuration.
8. Scheduler/controller queues sú príčina, nie následok persistence latency.
9. API client-side throttling sa javí ako server timeout.
10. Certificate expiry alebo clock skew spôsobuje intermittent component failures.
11. Aggregated API outage ovplyvňuje iba konkrétny resource, nie core writes.
12. Network partition je medzi API servermi a etcd members.
13. Recent admission/config upgrade vytvoril version-skew problém.
14. Existing workload success maskuje nefunkčný management plane.

### 3. Discriminating observations

- `/readyz?verbose` per API instance;
- API request duration histogram podľa verb/resource/code;
- admission webhook duration/rejection/timeout a audit annotations;
- etcd fsync/commit latency, leader changes, proposal failures a peer health;
- API-to-etcd network latency;
- API inflight, watch count a client throttling;
- scheduler/controller queue age vs. API latency timeline;
- leader Leases a component logs;
- certificate expiration a clock offsets;
- request ID correlation medzi API, webhook a audit;
- direct core API request vs. aggregated API request;
- static Pod/runtime logs na jednotlivých control-plane Nodes.

### 4. Containment

- zmraz nonessential writers a rollout automation;
- zachovaj API/etcd/component metrics, logs a request IDs;
- nereštartuj všetky control-plane components naraz;
- neforce-ni etcd membership alebo restore bez quorum/state analýzy;
- neodstraňuj admission policy naslepo; použi narrow, audited break-glass iba pri potvrdenej boundary;
- udržuj existujúce healthy workloads a minimalizuj ďalšie replacements;
- chráň etcd disk pred ďalším pressure.

### 5. Recovery podľa príčiny

- unready API instance/LB → oprav readiness routing a over každú instance;
- webhook latency → obnov endpoint, CA/network, zúž match scope/timeout a revalidate writes;
- etcd disk/quorum → obnov storage/network/member health podľa supported protocol;
- API saturation → odstráň dominantný request/watch source a obnov capacity/backpressure;
- audit pressure → obnov sink/policy podľa configured fail behavior;
- scheduler/controller queue → obnov leader, permissions alebo hot-loop príčinu až po potvrdení healthy API persistence;
- certificates/time → vykonaj riadenú rotation/synchronizáciu a component-by-component verification;
- client throttling → oprav client QPS/concurrency bez skrytia server SLO problému.

### 6. Over pôvodný outcome

Potvrď:

```text
API read/write/watch synthetics
+ /readyz na všetkých routovaných instances
+ etcd quorum, commit latency a snapshot freshness
+ admission write test
+ scheduler Pod binding test
+ controller dependent-object test
+ Deployment observedGeneration 12
+ six ready Payments Pods
+ Service payment transaction exactly once
```

„Writes už menej timeoutujú“ nie je úplný recovery verdict.

### 7. Posuň control skôr

Pridaj:

- control-plane capability matrix a synthetics;
- per-instance semantic API readiness;
- etcd fsync/commit SLO a disk isolation;
- webhook availability/match-scope tests;
- scheduler/controller queue-age alerts;
- certificate inventory/rotation rehearsal;
- control-plane request correlation IDs;
- restore a leader-failover drills;
- management-plane degradation runbook chrániaci existujúce workloads.

## 20. Worked failure: scheduler vyzerá down, ale Pod je permanentne unschedulable

Pod ostáva `Pending`. Scheduler leader a queue processing sú healthy. Event ukazuje kombináciu untolerated taint a unbound topology-constrained PVC.

```text
Pod v queue
→ scheduler vykoná filters
→ žiadny feasible Node
→ correct FailedScheduling condition
→ retry po relevantnej Node/PVC zmene
```

Restart schedulera by nezmenil input. Recovery musí opraviť requests/constraints/toleration/storage topology alebo capacity podľa workload contractu.

## 21. Worked failure: controller-manager process beží, queue je v hot loope

Jeden built-in alebo extension controller opakovane zapisuje status bez semantic zmeny.

```text
status update
→ watch event
→ enqueue
→ status update
```

Process liveness je green, no queue age pre ďalšie objects rastie. Recovery vyžaduje zastaviť self-trigger, obnoviť backoff a overiť generation closure, nie iba reštartovať leadera.

## 22. Control-plane observation matrix

| Boundary | Subject | Diskriminačné observations |
|---|---|---|
| Endpoint | API LB a server instance | DNS/TLS, routing, `/readyz`, per-instance latency |
| Identity | caller/authenticator | audit user/groups, token/cert/OIDC latency |
| Authorization | verb/GVR/scope | allow/deny reason, RBAC evaluation |
| Admission | webhook/policy generation | mutation, reject, timeout, match scope |
| Persistence | etcd cluster/revision | quorum, fsync/commit, proposal, DB quota |
| API capacity | request class | inflight, codes, watch count, throttling |
| Scheduler | Pod UID/profile/leader | queue, FailedScheduling, binding audit |
| Controller | owner UID/generation/leader | queue age, reconcile errors, dependents |
| Cloud integration | external request/resource | provider audit, rate limits, external ID |
| Certificates/time | credential generation | expiry, trust chain, clock offset |
| Packaging | static Pod/systemd/managed | local manifests, runtime/journal/provider evidence |

## 23. Upgrade a configuration transitions

Control-plane upgrade musí rešpektovať:

- supported version skew;
- API removals a conversion;
- etcd compatibility;
- admission/webhook compatibility;
- scheduler profiles;
- controller flags/features;
- certificates/signing keys;
- rollback boundaries;
- API/queue/workload validation.

Pred transitionom:

```text
backup + restore proof
→ deprecated API inventory
→ webhook/add-on compatibility
→ HA/capacity check
→ staged component upgrade
→ write/read/watch/schedule/reconcile tests
→ workload business verification
```

Rollback binary version nemusí bezpečne rollbacknúť persisted API or etcd state.

## 24. Referenčné pravidlá

- Control plane je capability graph, nie jeden health status.
- TCP success nie je semantic API readiness.
- Authentication, authorization, admission, validation a persistence sú odlišné boundaries.
- Admission webhook je synchronous write-path dependency.
- etcd latency sa šíri do API, watches a controller queues.
- Strata etcd quorum neznamená okamžitý stop všetkých workloads, ale blokuje bezpečné state transitions.
- Scheduler vytvára binding, nie container.
- Running controller-manager process nepreukazuje progress každej queue.
- Leader election neposkytuje exactly-once.
- Core API, aggregated APIs a CRDs majú odlišné serving/storage boundaries.
- Static Pod mirror object nie je authoritative deployment source.
- Existujúce workloady môžu maskovať degraded management plane.
- Recovery musí overiť read, write, watch, schedule, reconcile aj pôvodný workload outcome.

## 25. Kontrolné otázky

1. Aký lifecycle tvorí Kubernetes control-plane write path?
2. Prečo load-balancer TCP check nestačí pre API readiness?
3. Ako odlíšiš authentication, authorization, admission a persistence failure?
4. Ako etcd disk latency ovplyvní controllers a scheduler?
5. Čo znamená strata etcd quorum pre existujúce a nové workloads?
6. Ako sa prejaví scheduler outage oproti unschedulable Podu?
7. Prečo controller-manager liveness nepreukazuje queue progress?
8. Aké riziko vytvára fail-closed admission webhook?
9. Ako static Pod topológia mení diagnostiku pri API outage?
10. Čo musí control-plane recovery verdict overiť?

## Glossary impact

Relevantné pojmy: control-plane capability subject, API write-path subject, semantic API readiness, admission dependency subject, etcd persistence subject, etcd latency amplification loop, scheduler capability subject, controller queue subject, control-plane leader generation, cloud reconciliation subject, static control-plane authority, control-plane observation matrix a control-plane recovery verdict.

## Oficiálna dokumentácia

- [Kubernetes components](https://kubernetes.io/docs/concepts/overview/components/)
- [`kube-apiserver`](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-apiserver/)
- [`kube-scheduler`](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-scheduler/)
- [`kube-controller-manager`](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-controller-manager/)
- [Admission control](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)
- [Scheduler configuration](https://kubernetes.io/docs/reference/scheduling/config/)
- [Operating etcd clusters for Kubernetes](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/)
- [API aggregation layer](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/apiserver-aggregation/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Desired state a reconciliation loops](desired-state-reconciliation-loops.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Worker node components →](worker-node-components.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
