# HPA a autoscaling

Autoscaling je feedback control system, nie príkaz „pridaj Pody pri vysokej metrike“. Controller pozoruje definovaný signal pre konkrétnu workload generation, prepočíta ho na odporúčanú kapacitu, aplikuje tolerance a behavior policy, zapíše nový desired state a čaká na scheduler, Nodes, startup, readiness a downstream systém. Zelený HPA condition nepreukazuje, že business bottleneck sa škáluje alebo že nové replicas zlepšili výsledok.

Táto kapitola používa jeden dominantný lifecycle:

```text
business demand, SLO a capacity model
→ scaling subject a field ownership
→ metric definition, labels, window a pipeline
→ fresh sample a eligible Pod cohort
→ normalization a per-metric recommendation
→ tolerance, stabilization a rate policy
→ scale subresource write
→ workload controller, scheduler, Nodes a readiness
→ downstream a business feedback
→ containment, recovery a skorší control
```

## 1. Atlas Payments scaling subject

Payments API 5.3.1 má baseline 6 replík. Pri incidente fixuj:

```text
HPA UID a generation
scaleTargetRef a target UID/generation
owner poľa replicas
metric type, query, labels, aggregation window a freshness
target value a unit
current ready/not-ready/missing-metric Pod cohort
per-metric recommendation
tolerance/stabilization/rate-policy state
current, desired, min a max replicas
Deployment/ReplicaSet rollout generation
Pending/Ready replica counts a Node capacity
DB connection, retry a payment outcome
```

Názov HPA alebo údaj `desiredReplicas: 18` bez metric a cohort identity nestačí.

## 2. Control loop musí mať správny causal signal

Signal má odpovedať na otázku:

```text
Keď zvýšime kapacitu cieľového workloadu,
ako a s akým oneskorením sa má táto metrika zmeniť?
```

CPU môže byť vhodný pre CPU-bound stateless service. Queue age môže byť vhodnejšia pre workers. Request rate môže byť zlý signal, ak zahŕňa retry amplification alebo ak bottleneckom je databáza, ktorá sa neškáluje s počtom API Podov.

Metric contract potrebuje:

- unit a business význam;
- source a owner;
- label/tenant scope;
- aggregation a sampling window;
- freshness a missing-data semantics;
- expected response na replica change;
- downstream capacity envelope;
- attack/manipulation model.

## 3. HPA scale subject a field ownership

HPA upravuje replica count resource-u, ktorý poskytuje `/scale` subresource, typicky Deployment alebo StatefulSet.

```text
HPA recommendation
→ scale subresource desired replicas
→ workload controller
→ ReplicaSet/Pod creation alebo deletion
```

HPA nevytvára Nodes, nerieši Pod placement, neinicializuje aplikáciu a nekoordinuje databázové connection limity.

`spec.replicas` musí mať jedného autoritatívneho runtime writera. Ak GitOps controller vynucuje statickú hodnotu a HPA ju mení, vzniká reconciliation fight. Declarative config má vlastniť HPA policy, min/max a metric contract; HPA má vlastniť live scale field podľa zvoleného operating modelu.

## 4. Metric pipeline je súčasť control-plane trust boundary

Resource metrics typicky prichádzajú cez `metrics.k8s.io`; custom a external metrics cez príslušné adapters/APIs. HPA musí dostať správny signal pre správnu workload population.

```text
application/kubelet/external source
→ scrape alebo adapter query
→ label a tenant filtering
→ aggregation/window
→ Kubernetes metrics API
→ HPA sample timestamp a value
```

Stará, duplicovaná alebo cross-tenant metrika môže vytvoriť scale-out, scale-in alebo denial-of-wallet incident. Metrics adapter credentials, query definitions a label isolation sú security controls.

Metrics Server je autoscaling/resource-metrics komponent, nie plnohodnotný historický observability systém. Incident stále potrebuje metrics/traces/logs s dlhšou retenciou.

## 5. Resource utilization používa effective requests

Pri CPU alebo memory `averageUtilization` sa usage normalizuje voči relevantnému requestu. Zjednodušene:

```text
utilization per Pod = observed usage / effective request
```

Nízky request zväčší percento a môže spustiť skorší scale-out. Vysoký request percento zníži a môže oddialiť reakciu. Chýbajúci request môže znemožniť použitie Podu v resource-utilization výpočte podľa metric/cohort semantics.

HPA preto závisí od admitted/effective Pod resource contractu, nie iba od hodnoty v Git source manifeste.

## 6. Recommendation model

Základný pomer možno chápať ako:

```text
desiredReplicas = ceil(currentReplicas × currentMetric / desiredMetric)
```

Príklad:

```text
current replicas = 6
current average = 90
metric target = 60
recommendation = ceil(6 × 90 / 60) = 9
```

Reálny controller navyše zohľadňuje tolerance, missing metrics, not-yet-ready Pods, metric errors a behavior history. Výsledok preto nemusí byť presne jednoduchý pomer z dashboardu.

Pri viacerých metrics sa pre každú vypočíta recommendation a scaling policy typicky použije najvyššiu požadovanú replica count. Partial metric failure môže blokovať alebo konzervatívne meniť scale-down behavior; čítaj HPA conditions a Events.

## 7. Eligible cohort a startup distortion

Nový Pod môže počas bootstrapu spotrebovať vysoké CPU, ešte nemá reprezentatívny throughput alebo nemá fresh metric. Controller používa readiness/startup informácie a konfigurované initialization boundaries, ale workload musí mať:

- správnu startup probe;
- readiness až po ukončení nereprezentatívneho warm-upu;
- realistický request denominator;
- bounded image pull a initialization;
- metric, ktorá nerozlišuje bootstrap ako production demand.

Ak nový Pod zvýši CPU metric skôr, než začne obsluhovať traffic, HPA môže vytvoriť pozitívnu feedback slučku: viac Podov → viac warm-up CPU → ďalší scale-out.

## 8. Tolerance, stabilization a rate policy

Control loop nemá reagovať na každý malý alebo krátky signal. Behavior policy môže obmedziť:

```text
ako rýchlo sa smie scale-up
ako rýchlo sa smie scale-down
ktoré historické recommendations sa použijú
koľko replík alebo percent sa smie zmeniť za interval
```

Scale-up príliš pomalý prehlbuje queue/latency. Scale-up príliš rýchly môže vytvoriť image-pull, connection, cold-cache alebo thundering-herd storm.

Scale-down potrebuje dlhší outcome model:

```text
nižší desired count
→ endpoint drain
→ in-flight work completion
→ Pod termination
→ queue/partition rebalancing
→ downstream connection release
```

Replica count sa môže znížiť skôr, než application business work bezpečne skončí. PDB, readiness, `preStop`, termination grace a idempotency zostávajú samostatnými contracts.

## 9. Min/max replicas sú policy hranice

`minReplicas` vyjadruje baseline availability a capacity počas reaction delay. `maxReplicas` chráni cluster, downstream a budget, ale negarantuje SLO.

Pri `ScalingLimited=True` alebo dosiahnutí maxima musí existovať explicitný saturation response:

- alert a incident owner;
- load shedding alebo rate limit;
- queue/degradation mode;
- downstream protection;
- capacity alebo architecture remediation.

HPA, ktoré korektne drží maximum počas rastúcej chybovosti, technicky funguje, ale business systém je saturovaný.

## 10. HPA, VPA a Node autoscaling sú oddelené loops

### HPA

Mení počet replík cieľového workloadu.

### VPA

Samostatne inštalovaný controller môže odporúčať alebo meniť resource requests. Zmena requests môže zmeniť CPU-utilization denominator HPA.

### Node autoscaling

Reaguje na unschedulable/capacity potrebu Node poolov. Typický chain:

```text
HPA požaduje viac replík
→ controller vytvorí Pody
→ scheduler ich nevie umiestniť
→ node autoscaler vyhodnotí node-group templates
→ nový Node sa provisionuje a bootstrapuje
→ scheduler bindne Pod
→ image/startup/readiness
→ až potom nová serving capacity
```

Celkový reaction time zahŕňa metric delay, reconciliation interval, Node provisioning, scheduling, image pull, startup, readiness a traffic propagation.

Loops musia mať oddelené field ownership a rozdielne signals. HPA a VPA nad rovnakým CPU signalom môžu oscilovať: HPA mení replicas, VPA requests, requests menia utilization denominator a HPA recommendation.

## 11. Queue a event-driven scaling

Pre workers je často reprezentatívnejšie:

```text
oldest unprocessed item age
backlog per ready worker
arrival rate vs. verified service rate
partition lag
```

Queue depth bez processing time, retries, partition distribution a downstream rate limitu je neúplný signal. Exactly-once, acknowledgment a work ownership zostávajú application/queue zodpovednosťou.

Event-driven controllery môžu poskytovať activation alebo scale-to-zero patterns, ale pridávajú vlastné CRDs, credentials, metric freshness a lost-wakeup failure modes. Cold-start a minimum concurrency musia byť súčasťou SLO.

## 12. Worked failure: scale-out zosilnil payment incident

Payments 5.3.1 používal external metric:

```text
payments_requests_total rate za poslednú minútu
```

Metric zahŕňala originálne klientské requesty aj interné retries po DB timeoutoch. Každá API replika zároveň otvárala pool 30 DB connections.

Incident:

```text
DB latency mierne vzrastie
→ API retry rate rastie
→ request-rate metric rastie bez nového business demandu
→ HPA škáluje 6 → 12 → 20 replík
→ connection pools rastú 180 → 600
→ DB connection queue a latency rastú
→ ďalšie timeouty a retries
→ HPA dosiahne maxReplicas
→ payment success rate klesá
```

HPA algoritmus reagoval podľa definovaného signalu. Chybný bol causal metric a downstream capacity model.

Zníženie CPU targetu alebo zvýšenie `maxReplicas` by incident zhoršilo. Vypnutie HPA bez retry containmentu by zase nemuselo odstrániť existujúcu amplification.

## 13. Causal troubleshooting walkthrough

### Subject a timeline

Fixuj HPA/target generation, exact metric query a labels, sample timestamps, ready/missing Pod cohort, recommendation history, scale writes, ReplicaSet/Pod generations, Pending/Ready counts, Node provisioning, connection pool a payment traces.

### Competing hypotheses

1. metrics API alebo adapter je nedostupný;
2. sample je stale alebo má nesprávne labels/tenant scope;
3. CPU request denominator je chybný;
4. startup Pods deformujú metric;
5. HPA je limitované min/max alebo rate policy;
6. GitOps prepisuje replicas;
7. nové Pody zostávajú Pending;
8. nové Pody nie sú Ready alebo sa zahrievajú príliš dlho;
9. load balancer neposiela traffic novej cohort-e;
10. bottleneck je DB/external dependency;
11. metric obsahuje retries alebo duplicate events;
12. každá replika pridáva väčší downstream load než serving capacity;
13. HPA/VPA loops menia rovnaký signal/denominator;
14. scale-down prerušuje in-flight work.

### Discriminating observations

```bash
kubectl get hpa -n production payments -o yaml
kubectl describe hpa -n production payments
kubectl get deployment,replicaset,pod -n production -l app=payments
kubectl get events -n production --sort-by=.metadata.creationTimestamp
kubectl get --raw /apis/metrics.k8s.io/
kubectl top pod -n production --containers
```

Koreluj:

- exact current/target metric values a timestamps;
- HPA conditions `AbleToScale`, `ScalingActive`, `ScalingLimited`;
- per-metric recommendation a behavior history;
- source vs. admitted requests;
- ready, not-yet-ready a missing-metric cohort;
- scale subresource field owner;
- Pending reasons a Node provisioning latency;
- per-replica throughput, connection pool a dependency saturation;
- retry, duplicate a payment outcome rates.

### Containment

Zastav retry amplification a chráň DB load sheddingom/rate limitom. Zachovaj HPA status, metric samples/query, recommendation history, Pod cohort a traces. Dočasný versionovaný cap alebo fixed replica count musí mať jedného ownera a nesmie vytvoriť fight s HPA/GitOps.

### Authoritative recovery

- oddeľ originálny demand od retry trafficu;
- používaj signal s overeným causal vzťahom ku serving capacity;
- nastav per-replica downstream connection/concurrency budget;
- oprav request denominator alebo startup/readiness contract;
- uprav min/max a behavior podľa measured reaction time;
- oprav scheduler/Node capacity, ak desired Pods nevznikajú ako Ready capacity;
- rozdeľ HPA/VPA field ownership a signals;
- rolloutni policy/metric generation a sleduj celý feedback loop.

### Verify original a forbidden outcomes

Over:

1. business demand rastie → serving capacity rastie v očakávanom čase;
2. krátky DB incident nespustí nekontrolovaný replica/connection storm;
3. HPA nepoužíva stale alebo cross-tenant metric;
4. nové replicas sú Scheduled, Ready a dostávajú traffic;
5. payment success/latency sa zlepšia, nie iba replica count;
6. scale-down nestratí ani neduplikuje in-flight work;
7. GitOps, HPA a VPA nebojujú o rovnaké fields;
8. maxReplicas saturation spustí ochranu a alert.

### Earlier controls

Použi metric contract review, closed-loop load test, per-replica service-rate model, downstream capacity budget, startup/cold-start test, HPA/VPA ownership policy, autoscaling chaos experiment, metric provenance/freshness alert a payment-level SLO gate.

## 14. Ďalšie failure boundaries

### HPA ukazuje `<unknown>`

Rozlišuj metrics API availability, adapter RBAC, query/selector chybu, missing requests a stale samples. Nezvyšuj replicas manuálne bez poznania demandu a capacity.

### HPA škáluje, Pody sú Pending

HPA loop dosiahol scale write. Zlyháva placement, capacity, PVC alebo node-autoscaler template. Desired replicas nie sú serving capacity.

### HPA škáluje, latency stále rastie

Over downstream bottleneck, cold start, traffic distribution, lock contention, connection pool a per-replica throughput. Horizontálne škálovanie môže zvýšiť pressure na nescalable dependency.

### Neustále scale up/down

Signal, window a control delays sú nekompatibilné. Skontroluj stabilization, readiness warm-up, cache/queue dynamics a HPA/VPA interactions.

### Scale-down prerušuje prácu

Replica deletion predchádza drain/acknowledgment. Oprav work ownership, readiness drain, termination grace a idempotency; samotné dlhšie stabilization window nie je úplná náprava.

### Memory metric škáluje leak

Viac replík vytvorí viac leakujúcich processov. Autoscaling nemá nahradiť opravu unbounded memory growth.

## 15. Referenčný katalóg

### Metric source typy v `autoscaling/v2`

- `Resource`;
- `ContainerResource`;
- `Pods`;
- `Object`;
- `External`.

### Scaling evidence

```text
metric definition a timestamp
eligible Pod cohort
per-metric recommendation
behavior/stabilization verdict
scale write
created/Pending/Ready Pods
traffic a downstream utilization
business SLO
```

### Control boundaries

| Loop | Mení | Nezaručuje |
|---|---|---|
| HPA | replica count | Node capacity, readiness, downstream scalability |
| VPA | requests/recommendations | application correctness alebo horizontal capacity |
| Node autoscaler | Node capacity | logicky splniteľný placement alebo Pod readiness |

## 16. Anti-patterny

- CPU utilization target bez správnych requests;
- signal obsahujúci retries/duplicates bez business semantics;
- HPA nad bottleneckom, ktorý sa horizontálne neškáluje;
- GitOps staticky prepisujúci HPA-owned replicas;
- veľmi vysoké maximum bez downstream/budget guardrail;
- veľmi nízke maximum bez saturation response;
- memory autoscaling ako „oprava“ leak-u;
- scale-down bez drain a idempotency;
- hodnotenie úspechu iba podľa desired/current replicas;
- HPA a VPA nad rovnakým signalom bez ownership modelu.

## 17. Kontrolné otázky

1. Aký causal vzťah musí mať metric ku replica capacity?
2. Ktoré identities tvoria HPA scaling subject?
3. Prečo CPU utilization závisí od effective requests?
4. Ako missing a not-yet-ready Pods menia jednoduchý ratio model?
5. Prečo desired replicas nie sú serving capacity?
6. Ako stabilization a rate policy súvisia s reaction delay?
7. Ako HPA môže zosilniť downstream incident?
8. Prečo GitOps a HPA potrebujú explicitný field ownership?
9. Ako sa líši HPA, VPA a Node autoscaling loop?
10. Ako overíš payment outcome, nie iba scale action?

## Glossary impact

Relevantné pojmy: autoscaling control subject, metric contract, metric provenance a freshness, eligible autoscaling cohort, resource-utilization denominator, per-metric recommendation, HPA behavior generation, scale-field ownership, serving-capacity realization, autoscaling reaction time, downstream capacity envelope, retry-amplified metric, scaling saturation verdict, multi-loop ownership, subject-bound scaling verification a forbidden feedback outcome.

## Oficiálna dokumentácia

- [Horizontal Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)
- [HorizontalPodAutoscaler v2 API](https://kubernetes.io/docs/reference/kubernetes-api/autoscaling-resources/horizontal-pod-autoscaler-v2/)
- [Autoscaling Workloads](https://kubernetes.io/docs/concepts/workloads/autoscaling/)
- [Vertical Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/)
- [Node Autoscaling](https://kubernetes.io/docs/concepts/cluster-administration/node-autoscaling/)
- [Resource metrics pipeline](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Taints, tolerations, affinity a topology](taints-tolerations-affinity-topology.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: RBAC →](rbac.md)
<!-- KNOWLEDGE-NAVIGATION:END -->