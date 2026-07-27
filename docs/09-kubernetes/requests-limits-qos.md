# Requests, limits a QoS

Kubernetes resource configuration nie je jeden limit. Je to chain medzi workload demand modelom, admitted requests/limits, scheduler reservation, Node cgroup enforcement, runtime usage a pressure/eviction behavior. QoS class je odvodená classification; nie je performance SLA ani záruka, že Pod nezlyhá.

Táto kapitola používa jeden dominantný lifecycle:

```text
workload demand, SLO a failure model
→ container/Pod resource intent
→ admission, defaults, quota a effective contract
→ scheduler request a Node reservation
→ cgroup/resource-manager realization
→ runtime usage, throttling, OOM alebo pressure
→ QoS, eviction a autoscaling feedback
→ application a business outcome
→ tuning, redeploy, capacity alebo code recovery
```

## 1. Atlas Payments resource subject

Payments API 5.3.0 má latency-sensitive autorizáciu. Reviewed contract pre jednu repliku:

```text
main container:
  request: 750m CPU, 768Mi memory
  limit: 2 CPU, 1536Mi memory

telemetry sidecar:
  request: 100m CPU, 128Mi memory
  limit: 300m CPU, 256Mi memory

RuntimeClass overhead:
  50m CPU, 64Mi memory

SLO:
  p99 authorization < 350 ms
  no cgroup OOM
  CPU throttled-period ratio < reviewed threshold
  rollout zachová aspoň 5 accepted endpoints
```

Exact resource subject zahŕňa:

```text
Pod UID a template/admission generation
container names a runtime container IDs
source requests/limits a admitted effective values
LimitRange/ResourceQuota generation
init, sidecar a RuntimeClass overhead calculation
Node UID, allocatable a scheduler reservation
Pod/container cgroup path a configured CPU/memory controls
actual usage, working set, throttling a memory events
QoS class, PriorityClass a eviction evidence
HPA/VPA metric/recommendation generation
request alebo payment operation ID
```

Graf „Pod používa 60 % CPU“ bez denominatora, cgroup subjectu a time windowu nie je diagnostický dôkaz.

## 2. Requests a limits majú rozdielne mechanizmy

### Request

Request je hlavne scheduling a capacity signal. Scheduler porovná admitted effective requests s Node allocatable a existing reservations.

CPU request môže ovplyvniť aj relatívnu CPU weight pri contention. Memory request ovplyvňuje placement, QoS a pressure decisions, ale nie je automaticky preallocated physical memory.

### Limit

Limit je runtime boundary podľa resource type-u:

- CPU limit sa typicky realizuje cgroup quota a môže vyvolať throttling;
- memory limit je hard cgroup boundary a môže viesť k OOM kill;
- ephemeral-storage limit/request vstupuje do kubelet accounting a eviction;
- huge pages a extended resources majú vlastné nekompresibilné semantics.

```text
request odpovedá: kam sa Pod zmestí a akú reservation deklaruje?
limit odpovedá: aký runtime ceiling alebo enforcement boundary platí?
```

## 3. Source manifest nie je effective contract

Admission môže doplniť alebo odmietnuť resource fields cez LimitRange, policy, mutation alebo Pod-level resource support.

```text
Git template
→ API defaulting/admission
→ effective Pod spec
→ scheduler calculation
→ kubelet/cgroup realization
```

Preto vždy over actual Pod spec. Ak container má limit a nemá request, applicable defaulting môže request odvodiť alebo doplniť. LimitRange môže zároveň nastaviť default, defaultRequest, minimum alebo maximum.

Release evidence má zachytiť:

- source contract;
- admitted effective contract;
- object generation a field owner;
- policy/default generation, ktorá hodnoty vytvorila.

## 4. Effective Pod request nie je iba main container

Pre bežné application containers sa requests sčítavajú. Init containers sa posudzujú podľa ich lifecycle-u; effective scheduling request zohľadňuje najvyššiu relevantnú init fázu oproti súbežným running containers. Restartable init/sidecar model môže meniť výpočet. RuntimeClass pridáva overhead.

Zjednodušený subject:

```text
running-container sum
+ relevantný sidecar/restartable-init contribution
porovnaný s init-phase maximum
+ Pod/RuntimeClass overhead
= effective scheduler request
```

Capacity review iba nad main containerom systematicky podhodnotí Node reservation.

Pod-level requests/limits môžu byť dostupné podľa Kubernetes verzie a feature state-u. Pred použitím over API discovery, admission, kubelet/cgroup a metrics/tooling support. Container-level contract ostáva najportable základ.

## 5. CPU lifecycle: reservation, burst a throttling

```text
request 750m
→ scheduler rezervuje 0.75 CPU
→ cgroup dostane CPU weight
→ process môže burstovať
→ limit 2 CPU vytvorí quota
→ po vyčerpaní quota v period-e process čaká
```

CPU je kompresibilný: process sa typicky neskončí, ale dostane menej execution time-u.

### Prečo throttling vznikne pri voľnom Node-e

CPU quota je local container boundary. Container môže vyčerpať svoj limit počas krátkeho burstu, aj keď ostatné CPU sú idle.

```text
request burst 10 ms potrebuje 4 cores
→ cgroup limit povoľuje ekvivalent 2 cores
→ quota sa vyčerpá
→ threads sú throttled do ďalšej period-y
→ latency stúpne
```

Node average utilization môže zostať nízka. Rozhodujúce sú container throttled periods/seconds, runnable threads a request latency v rovnakom intervale.

## 6. Memory lifecycle: reservation, working set a OOM

```text
request 768Mi
→ scheduler reservation
→ process alokuje heap/native/cache/tmpfs
→ cgroup usage rastie
→ limit 1536Mi
→ reclaim alebo memory pressure
→ cgroup OOM a process kill pri prekročení boundary
```

Memory je nekompresibilná. Usage môže zahŕňať heap, native allocations, page cache podľa accounting modelu, memory-backed `emptyDir`, shared memory, JIT a sidecars.

### Cgroup OOM vs. Node OOM vs. eviction

- **cgroup OOM:** container/Pod cgroup prekročil svoju boundary; Node môže mať voľnú memory;
- **Node OOM:** host memory je vyčerpaná a kernel vyberá victim v širšom scope;
- **kubelet eviction:** kubelet ukončí Pod podľa Node pressure policy, často skôr než host OOM;
- **application kill:** process dostal SIGKILL z iného dôvodu; exit 137 sám o sebe OOM nepreukazuje.

Over `lastState`, `reason`, cgroup memory events, kernel logs, kubelet Events, Node pressure a exact container ID.

## 7. QoS je odvodený verdict

Kubernetes priradí Podu `Guaranteed`, `Burstable` alebo `BestEffort` podľa effective CPU/memory resource contractu relevantných containers a podporovaných Pod-level fields.

### Guaranteed

Všetky relevantné containers majú CPU aj memory request a limit a request sa rovná limitu podľa QoS pravidiel.

Poskytuje predvídateľnejší reservation model a lepšiu relatívnu ochranu pri niektorých pressure decisions. Nechráni pred application bugom, hard limit OOM, Node loss, preemption ani nesprávnym sizingom.

### Burstable

Pod nie je Guaranteed, ale má aspoň niektorý CPU/memory request alebo limit. Umožňuje burst a overcommitment. Pri memory pressure záleží na usage voči requestu, priority a Node eviction policy.

### BestEffort

Pod nemá CPU ani memory requests/limits podľa QoS calculation. Scheduler nepozná jeho potrebu a pri pressure je typicky prvý kandidát na eviction. Je vhodný iba pre skutočne postrádateľný workload.

QoS class nie je „bronze/silver/gold“ application tier.

## 8. Node allocatable a runtime reality

Scheduler vidí Node `allocatable`, nie celú hardware capacity. Rozdiel zahŕňa system/kube reservations, eviction thresholds, platform agents a ďalší overhead.

Po bindingu môže na Node-e nastať:

- CPU contention medzi cgroups;
- memory overcommitment, lebo súčet limits môže presahovať physical memory;
- ephemeral storage/inode pressure;
- PID pressure;
- device/NUMA/topology constraints;
- kernel alebo runtime overhead, ktorý dashboard nezobrazuje ako workload request.

Resource acceptance preto potrebuje placement aj runtime evidence.

## 9. Ephemeral storage je samostatný failure domain

Local ephemeral storage môže zahŕňať writable layers, logs a disk-backed `emptyDir`. Pod môže byť evicted pri vlastnom limit-e alebo Node disk pressure.

```text
unbounded logs
→ node filesystem/inodes sa plnia
→ DiskPressure
→ kubelet eviction
→ replacement Pod začne a znovu loguje
→ incident sa opakuje
```

Capacity bytes a inodes sú odlišné. `df -h` môže byť zelené pri vyčerpaných inodes.

Memory-backed `emptyDir` vstupuje do memory accounting, nie do persistent storage contractu.

## 10. Huge pages, devices a RuntimeClass overhead

Huge pages a extended resources sú nekompresibilné a typicky sa neovercommitujú. Node object môže resource publikovať, ale to nepreukazuje driver/device health.

RuntimeClass overhead musí vstupovať do scheduling aj runtime accounting. Rovnaký workload bez správneho overheadu môže systematicky preplniť sandboxed-runtime Nodes.

CPU Manager, Memory Manager a Topology Manager môžu vytvoriť node-specific allocation semantics. Guaranteed Pod s integer CPU requestom môže pri vhodnej Node policy dostať exclusive CPU set, ale QoS class sama túto konfiguráciu negarantuje.

## 11. Requests sú aj autoscaling denominator

HPA resource utilization typicky porovnáva usage s requestom:

```text
utilization = current usage / request
```

Príliš nízky request nafúkne percento a môže spustiť skorý scale-out. Príliš vysoký request zníži percento a oddiali scale-out.

VPA môže meniť alebo odporúčať requests. Ak HPA aj VPA zapisujú alebo používajú nekompatibilný resource subject bez ownership policy, vzniká oscilácia:

```text
VPA zvýši request
→ HPA utilization percento klesne
→ HPA scale-in
→ per-Pod load stúpne
→ VPA/HPA reagujú znova
```

Autoscaler evidence musí patriť current Pod/resource generation a stabilnému metric definition.

## 12. Metrics majú rôzne významy

Memory dashboard môže ukazovať working set, RSS, cache alebo total cgroup usage. CPU dashboard môže ukazovať usage rate, request utilization, limit utilization alebo throttled time.

Pred záverom „memory je pod limitom“ alebo „CPU je voľné“ urč:

```text
metric name a definition
subject/container ID
scrape interval a freshness
time aggregation
request/limit denominator
effective cgroup boundary
```

Stará Pod UID alebo agregácia cez replaced containers môže skryť krátky OOM/throttling burst.

## 13. Worked failure: CPU limit vytvoril latency pri 30 % Node usage

Payments main container mal limit 500m po accidental LimitRange defaulting-u. Počet request threads krátkodobo rástol.

```text
Node mal idle cores
→ container cgroup vyčerpal 500m quota
→ GC a request workers boli throttled
→ readiness začala timeoutovať
→ rollout odoberal endpointy
```

Zvýšenie replík či Node capacity bez opravy per-container quota problém neriešilo. Recovery opravila admitted limit, validovala load profile a zaviedla throttling-to-latency gate.

## 14. Worked failure: OOMKilled pri voľnej Node memory

Container limit bol 1 GiB. JVM heap mal 900 MiB, ale native buffers, threads a memory-backed `emptyDir` pridali ďalších 250 MiB.

```text
cgroup usage > 1GiB
→ local cgroup OOM
→ process killed
→ Node mal stále niekoľko GiB free
```

Node utilization nebol relevantný k hard cgroup boundary. Fix zahŕňal application memory envelope, heap/native budget a reviewed limit s load testom, nie iba restart.

## 15. Worked failure: init container blokoval scheduling

Main container žiadal 500m CPU, ale migration init container 4 CPU. Dashboard zobrazoval main resource policy a tím očakával, že Pod sa zmestí na 2-CPU Nodes.

Effective scheduling request zohľadnil init maximum, preto žiadny Node nebol feasible. Recovery rozdelila migration na explicitný Job a nastavila samostatný capacity/result contract.

## 16. Worked failure: Guaranteed Pod bol evicted

Pod mal Guaranteed QoS, ale Node utrpel disk/inode pressure a kubelet ho evictoval podľa local storage behavioru. Tím predpokladal, že Guaranteed chráni pred každou eviction.

QoS CPU/memory class nie je všeobecná immortality garancia. Recovery opravila log retention, ephemeral-storage requests/limits a Node disk monitoring.

## 17. Causal troubleshooting walkthrough: latency a restarty pri voľných Nodes

Symptóm:

```text
Payments release D53
p99 stúplo z 180 ms na 1.4 s
časť containers sa reštartuje
Node CPU 40 %, Node memory 55 %
HPA zvýšil replicas zo 6 na 12
```

### 1. Zafixuj subject a outcome

Zaznamenaj:

```text
Pod UID/template generation a Node UID
main/sidecar container IDs
source a admitted requests/limits
LimitRange/ResourceQuota/policy generation
init/sidecar/RuntimeClass effective request
QoS a PriorityClass
cgroup CPU quota/weight a memory boundary
usage, throttling, memory.events, OOM/eviction evidence
Node allocatable, pressure a existing reservations
HPA target, current metrics a request denominator
payment operation IDs a endpoint cohort
```

Pôvodný outcome: autorizácia do 350 ms bez duplicate resultu. Forbidden outcome: staging fallback alebo retry storm.

### 2. Competing hypotheses

| Hypotéza | Diskriminačný dôkaz |
|---|---|
| CPU throttling | throttled periods/seconds korelované s latency |
| cgroup memory OOM | memory.events, `OOMKilled`, cgroup boundary |
| Node OOM/pressure eviction | kernel/kubelet Events, Node conditions, victim scope |
| application leak/GC issue | heap/native profile a growth pattern |
| sidecar alebo tmpfs spotrebúva budget | per-container a volume accounting |
| admitted defaults sa zmenili | actual Pod spec a LimitRange generation |
| HPA amplification | request denominator, metric freshness, per-Pod load |
| downstream dependency je pomalá | request trace bez local throttle/OOM evidence |
| ephemeral storage pressure | bytes/inodes, logs, eviction reason |

### 3. Observation sequence

```text
request latency trace
→ container CPU run/throttle evidence
→ memory/cgroup events
→ container termination reason
→ kubelet/Node pressure
→ admitted resource contract
→ scheduler/HPA decisions
→ downstream timing
```

Nehľadaj iba peak usage. Krátky quota alebo memory burst môže spôsobiť incident medzi scrape intervalmi.

### 4. Containment

- zastav rollout a ďalšie automatic resource mutations;
- odober affected cohort z trafficu bez globálneho restartu;
- zachovaj cgroup counters, lastState, Events a profiles;
- obmedz client retries a over idempotency;
- nezvyšuj všetky limits bez capacity/overcommit analýzy;
- neznižuj requests iba preto, aby sa Pods schedulovali.

### 5. Authoritative recovery

Finding:

```text
LimitRange LR8 začal defaultovať CPU limit 500m
→ main container source template limit neuvádzal
→ admitted D53 Pods dostali 500m
→ throttling zvýšil latency
→ readiness failures znížili endpoints
→ HPA scale-out zvýšil connection/retry pressure
```

Recovery:

1. opravila explicitný reviewed CPU contract v Pod template;
2. aktualizovala LimitRange policy a ownership;
3. vytvorila novú Pod generation;
4. canary overila throttling, latency, readiness a downstream load;
5. HPA sa vyhodnotil s current request denominatorom;
6. rollout pokračoval po bounded cohorts.

### 6. Over pôvodný a forbidden outcome

Potvrď:

- actual Pods majú reviewed effective requests/limits;
- cgroup controls zodpovedajú admitted contractu;
- throttling a OOM/eviction counters sú v accepted rozsahu;
- QoS a priority sú očakávané, ale nie jediný acceptance signal;
- HPA používa current metrics a request denominator;
- scheduler reservation a Node capacity zostávajú bezpečné;
- payment p99 a throughput prejdú cez každú cohortu;
- `pay-8842` má presne jeden downstream result;
- ďalší LimitRange alebo template change prejde resolved-contract testom.

### 7. Posuň control skôr

Pridaj:

- source-vs-admitted resource diff;
- per-container effective resource manifest;
- init/sidecar/RuntimeClass capacity preflight;
- throttling, OOM, eviction a inode release gates;
- load test s GC/native/tmpfs envelope;
- HPA denominator a metric-freshness audit;
- VPA/HPA field-ownership policy;
- quota/default policy versioning;
- rollout capacity model spájajúci requests, surge a failure domains.

## 18. Observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| Demand | workload resource envelope | SLO, burst, memory/CPU/storage model |
| Source | Pod template generation | per-container requests/limits |
| Admission | effective resource contract | defaults, LimitRange, quota, field owners |
| Pod calculation | Pod request/limit subject | containers, init, sidecars, overhead |
| Scheduling | reservation subject | Node allocatable, existing requests, placement |
| Runtime | cgroup/container generation | quota, weight, memory boundary, cpuset |
| Usage | metric subject | definition, freshness, working set, throttling |
| Failure | OOM/eviction subject | container vs. Node scope, reason, pressure |
| QoS | Pod QoS verdict | class inputs, priority, eviction context |
| Autoscaling | HPA/VPA generation | target, denominator, recommendation, ownership |
| Business | release/request cohort | latency, throughput, exactly-once result |

## 19. Referenčné príkazy

```bash
kubectl get pod <pod> -n <namespace> -o yaml
kubectl describe pod <pod> -n <namespace>
kubectl get pod <pod> -n <namespace> -o jsonpath='{.status.qosClass}'
kubectl top pod -A --containers
kubectl top node
kubectl describe node <node>
kubectl get limitrange,resourcequota -A -o yaml
kubectl get hpa -A -o yaml
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Doplň cgroup CPU/memory events, kubelet eviction metrics, kernel logs, ephemeral storage/inode state a application profiles.

## 20. Referenčné pravidlá

- Requests sú scheduling/capacity contract; limits sú runtime boundaries.
- Source YAML nemusí byť admitted effective contract.
- Effective Pod resources zahŕňajú viac než main container.
- Scheduler používa requests a overhead, nie live usage.
- CPU limit môže throttliť pri idle Node-e.
- Memory limit môže vyvolať cgroup OOM pri voľnej Node memory.
- Exit 137 sám nepreukazuje OOM root cause.
- QoS je odvodená classification, nie HA alebo performance guarantee.
- Guaranteed Pod môže zlyhať, byť preempted alebo evicted.
- Ephemeral storage bytes a inodes sú samostatné pressure subjects.
- HPA utilization závisí od request denominatora.
- Resource metrics treba interpretovať podľa definície a freshness.
- Recovery musí overiť cgroup realization, runtime failure mode, autoscaling a business outcome.

## 21. Kontrolné otázky

1. Aký lifecycle spája workload demand s accepted runtime behaviorom?
2. Ako sa líšia request a limit pre CPU a memory?
3. Prečo musíš poznať admitted effective resource contract?
4. Ako init containers, sidecars a RuntimeClass menia Pod request?
5. Prečo CPU throttling vznikne pri nízkej Node utilization?
6. Ako odlíšiš cgroup OOM, Node OOM a kubelet eviction?
7. Čo QoS class ovplyvňuje a čo negarantuje?
8. Ako ephemeral storage a inodes vedú k eviction?
9. Ako requests menia HPA behavior?
10. Čo musí resource acceptance verdict overiť?

## Glossary impact

Relevantné pojmy: resource lifecycle subject, effective resource contract, admission resource generation, Pod effective request, scheduler reservation subject, cgroup runtime generation, CPU throttling subject, cgroup memory OOM subject, Node pressure/eviction subject, QoS verdict, ephemeral-storage pressure, HPA denominator subject, resource metric definition, resource observation matrix a resource acceptance verdict.

## Oficiálna dokumentácia

- [Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Pod Quality of Service Classes](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [Resource Managers](https://kubernetes.io/docs/concepts/workloads/resource-managers/)
- [Manage Memory, CPU, and API Resources](https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Scheduling](scheduling.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Probes →](probes.md)
<!-- KNOWLEDGE-NAVIGATION:END -->