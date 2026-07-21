# Requests, limits a QoS

Kubernetes resources majú dva odlišné účely. **Requests** vyjadrujú množstvo resource-u používanú schedulerom a capacity planningom. **Limits** určujú runtime maximum alebo enforcement boundary podľa resource type-u. Z kombinácie requests a limits Kubernetes odvodzuje Pod Quality of Service (QoS) class, ktorá ovplyvňuje najmä behavior pri resource pressure a eviction.

## 1. Resource contract

Najčastejšie resources:

- CPU,
- memory,
- ephemeral storage,
- huge pages,
- extended resources ako GPU alebo device resources.

Container môže deklarovať:

```yaml
resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: "1"
    memory: 512Mi
```

Tento contract je súčasťou Pod template-u a mení scheduling, runtime isolation, QoS a autoscaling semantics.

## 2. CPU units

CPU je kompresibilný resource.

```text
1 CPU = 1 cloud vCPU alebo 1 hyperthread/core unit podľa Node prostredia
1000m = 1 CPU
250m = 0.25 CPU
```

CPU request ovplyvňuje:

- scheduler fit,
- relatívnu CPU weight/shares pri contention,
- HPA utilization denominator pri resource metrics,
- capacity planning.

CPU limit sa typicky enforcementuje cez cgroup quota. Pri prekročení môže process dostať menej CPU času — **throttling** — nie OOM kill.

## 3. Memory units

Memory je nekompresibilný resource.

Odporúčané binary suffixes:

```text
Ki, Mi, Gi, Ti
```

Pozor:

```text
400m memory = 0.4 bytes, nie 400 MiB
```

Memory request ovplyvňuje scheduler a QoS. Memory limit je cgroup boundary; pri prekročení môže kernel ukončiť process cez OOM mechanizmus.

Memory usage môže zahŕňať:

- anonymous memory,
- page cache podľa accounting modelu,
- tmpfs/`emptyDir` memory-backed content,
- runtime/JIT overhead,
- sidecars a helper processes.

## 4. Requests pri scheduling-u

Scheduler pracuje s deklarovanými requests:

```text
sum requests Podov + nový Pod request ≤ Node allocatable
```

Live utilization scheduler bežne nepoužíva ako hlavný placement constraint.

Dôsledky:

- nízky request umožní vysokú overcommitment,
- vysoký request môže znížiť bin-packing a vytvoriť pending Pods,
- nulový request skryje reálnu capacity potrebu,
- presný request je ekonomický aj availability parameter.

## 5. Limits a defaulting

Ak container deklaruje limit, ale nie request, Kubernetes alebo admission policy môže request odvodiť alebo doplniť podľa platných pravidiel a LimitRange. Bez externého defaultingu Kubernetes pri niektorých resources kopíruje limit do requestu.

Preto always inspect resolved Pod spec:

```bash
kubectl get pod <pod> -o yaml
```

Manifest v Git-e nemusí byť totožný s admitted objectom.

## 6. CPU request vs. limit

Príklad:

```yaml
requests:
  cpu: 500m
limits:
  cpu: "2"
```

Pod rezervuje 0.5 CPU pre scheduling, ale môže burstovať do 2 CPU, ak má Node capacity a quota period to dovolí.

Riziká príliš nízkeho CPU limitu:

- latency spikes,
- timeouty,
- pomalé garbage collection,
- readiness/liveness failures,
- rollout alebo leader-election instability.

CPU throttling môže nastať aj pri nízkom priemernom Node utilization, ak container vyčerpá vlastnú quota v krátkych intervaloch.

## 7. Memory request vs. limit

Príklad:

```yaml
requests:
  memory: 512Mi
limits:
  memory: 1Gi
```

Scheduler rezervuje 512 MiB. Container môže rásť do limitu 1 GiB. Node však môže byť overcommitted, pretože súčet memory limits môže presahovať fyzickú memory.

Pri pressure môže nastať:

- container cgroup OOM,
- Node-level OOM,
- kubelet eviction pred OOM podľa thresholds,
- application degradation kvôli reclaimu alebo swap policy.

## 8. OOMKilled

Container status môže ukázať:

```text
reason: OOMKilled
exitCode: 137
```

Ale samotný exit code 137 iba znamená ukončenie cez `SIGKILL`; nemusí vždy dokazovať cgroup memory limit.

Over:

- container `lastState`,
- `reason: OOMKilled`,
- Node kernel logs,
- kubelet Events,
- cgroup memory events,
- Node pressure,
- application memory profile.

Rozlišuj container limit OOM a host/Node OOM.

## 9. Pod resource calculation

Pre bežné application containers sa Pod request/limit počíta ako súčet relevantných container requests/limits.

Init containers majú odlišný lifecycle a effective scheduling calculation zohľadňuje najvyšší init-container request oproti súčtu bežných containers podľa resource semantics.

Sidecar containers implementované ako restartable init containers ovplyvňujú effective resources podľa ich lifecycle modelu.

Preto nepočítaj Pod capacity iba podľa hlavného application containeru.

## 10. Pod-level resources

Novšie Kubernetes verzie môžu podporovať Pod-level requests/limits pre vybrané resource types podľa feature state a cluster konfigurácie.

Pred použitím over:

- Kubernetes verziu,
- feature gate/state,
- admission support,
- kubelet/cgroup behavior,
- resource manager integrations,
- tooling a metrics compatibility.

Container-level resources zostávajú základným a najportable modelom.

## 11. QoS classes

Kubernetes priradí Podu jednu z QoS classes:

- `Guaranteed`,
- `Burstable`,
- `BestEffort`.

QoS sa určuje z requests a limits všetkých relevantných containers a prípadne Pod-level resources podľa podporovaného API.

QoS nie je SLA ani performance guarantee. Je to classification použitá najmä pre runtime resource a eviction decisions.

## 12. Guaranteed

Pod je `Guaranteed`, keď každý relevantný container má pre CPU aj memory request a limit a request sa rovná limitu podľa QoS pravidiel.

Príklad:

```yaml
resources:
  requests:
    cpu: "1"
    memory: 1Gi
  limits:
    cpu: "1"
    memory: 1Gi
```

Výhody:

- najpredvídateľnejší reservation model,
- vyššia ochrana pri niektorých Node pressure eviction decisions,
- možnosť exclusive CPU placement pri integer CPU a static CPU Manager policy podľa Node konfigurácie.

Nevýhody:

- slabšie burstovanie nad request,
- potenciálne nižšie utilization,
- nesprávne vysoké hodnoty blokujú capacity.

## 13. Burstable

Pod je `Burstable`, ak nie je Guaranteed a aspoň jeden relevantný CPU/memory request alebo limit existuje.

Je to bežný model:

```yaml
requests:
  cpu: 250m
  memory: 256Mi
limits:
  cpu: "1"
  memory: 512Mi
```

Burstable umožňuje overcommitment a burst, ale pri memory pressure sú eviction/OOM decisions citlivejšie na usage voči requestu a priority.

## 14. BestEffort

Pod je `BestEffort`, ak nemá CPU ani memory requests/limits podľa QoS calculation pravidiel.

Dôsledky:

- scheduler nemá deklarovanú CPU/memory potrebu,
- workload môže spotrebovať dostupné resources,
- pri pressure je typicky najzraniteľnejší,
- capacity planning a autoscaling sú nepresné.

BestEffort je vhodný iba pre skutočne postrádateľnú prácu s kontrolovaným blast radiusom.

## 15. Ephemeral storage

Container môže deklarovať:

```yaml
resources:
  requests:
    ephemeral-storage: 1Gi
  limits:
    ephemeral-storage: 4Gi
```

Local ephemeral storage zahŕňa podľa Node/runtime layoutu napríklad:

- writable layers,
- container logs,
- disk-backed `emptyDir`,
- ďalší kubelet-accounted local content.

Pri prekročení limitu alebo Node disk pressure môže kubelet Pod evictovať.

Capacity a inode exhaustion sú odlišné problémy. `df -h` môže vyzerať dobre, kým `df -i` ukazuje vyčerpané inodes.

## 16. Huge pages

Huge pages sú nekompresibilný resource. Musia byť vopred dostupné na Node-e a request sa musí zmestiť.

Typy sú page-size-specific, napríklad:

```text
hugepages-2Mi
hugepages-1Gi
```

Huge page limit nemožno burstovať nad deklarovanú hodnotu. Workload potrebuje compatible runtime a memory allocation model.

## 17. Extended resources

Device plugins alebo platform components môžu publikovať resources ako:

```text
vendor.example/gpu
vendor.example/fpga
```

Extended resources:

- sú integer quantities,
- typicky nie sú overcommitted,
- limit a request semantics sa často rovnajú,
- ovplyvňujú scheduler fit,
- potrebujú device plugin/runtime integration.

Resource availability v Node objecte nepreukazuje funkčný driver alebo device health.

## 18. RuntimeClass overhead

RuntimeClass môže deklarovať overhead, napríklad pre sandboxed runtime alebo VM-like isolation.

Scheduler zohľadní overhead pri placement-e a kubelet pri Pod cgroup accounting podľa podpory.

Bez overhead modelu môže cluster systematicky podhodnotiť memory/CPU potrebu sandbox vrstvy.

## 19. CPU Manager a Memory Manager

Node môže mať pokročilé resource managers:

- CPU Manager,
- Memory Manager,
- Topology Manager,
- device/resource managers.

Príklad static CPU Manager policy môže prideliť exclusive CPU set containerom, ktoré spĺňajú podmienky, typicky Guaranteed QoS a integer CPU request.

Tieto features sú Node-level policy. Rovnaký Pod manifest môže mať iné runtime placement na Node-e s odlišnou konfiguráciou.

## 20. Vertical a Horizontal autoscaling

HPA pri resource utilization typicky používa pomer aktuálnej spotreby k requestu.

Príliš nízky request:

- nafúkne utilization percento,
- spustí scale-out skôr,
- môže viesť k oscilácii.

Príliš vysoký request:

- zníži utilization percento,
- oddiali scale-out,
- zvýši reserved capacity.

VPA môže odporúčať alebo meniť requests podľa režimu. Requests preto prepájajú scheduling, autoscaling a cost model.

## 21. LimitRange a ResourceQuota

Detailne sa im venuje samostatná kapitola, ale v resource contracte majú dôležitú úlohu:

- LimitRange môže nastaviť defaults a min/max per object/container,
- ResourceQuota obmedzuje aggregate requests/limits alebo počet resources v namespace.

Admission môže Pod odmietnuť alebo mutovať defaults pred schedulingom.

## 22. Metrics a working set

Memory metric nie je vždy totožná s resident set ani cgroup limit usage. Monitoring stack môže zobrazovať:

- working set,
- RSS,
- cache,
- usage,
- limit,
- request,
- OOM events.

Pri capacity rozhodnutí poznaj definíciu konkrétnej metriky.

CPU metrics odlišuj:

- usage rate,
- throttled seconds/periods,
- request utilization,
- limit utilization,
- Node saturation/run queue.

## 23. Observability

```bash
kubectl top pod -A --containers
kubectl top node
kubectl describe pod -n production <pod>
kubectl get pod -n production <pod> -o jsonpath='{.status.qosClass}'
kubectl describe node <node>
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Ďalej sleduj:

- cgroup CPU throttling,
- memory OOM events,
- kubelet eviction metrics,
- Node pressure conditions,
- ephemeral storage/inodes,
- scheduler `FailedScheduling`,
- HPA/VPA recommendations.

## 24. Troubleshooting

### Pod je Pending kvôli `Insufficient cpu` alebo memory

Over requests všetkých Podov, Node allocatable, reservations, DaemonSet overhead a affinity/topology constraints.

### Application je pomalá bez vysokej Node CPU

Over container CPU throttling. Nízky limit môže obmedzovať burst aj na prázdnom Node-e.

### Container sa reštartuje s OOMKilled

Over memory limit, heap/native memory, tmpfs, sidecars, cache, leak a Node-level OOM evidence.

### Pod bol `Evicted`

Skontroluj reason/message, Node pressure condition, local storage, inodes a usage voči requests. Eviction nie je to isté ako container OOM.

### HPA škáluje nečakane

Over requests, metrics freshness, missing metrics, startup behavior a target calculation.

## 25. Anti-patterny

### Žiadne requests v produkcii

Scheduler a capacity planning nepoznajú workload potrebu.

### CPU limit nastavený veľmi nízko „pre bezpečnosť“

Vytvára throttling a latency bez ochrany downstream dependencies.

### Memory limit rovný priemernej spotrebe

Bežný burst alebo GC peak vyvolá OOM.

### Requests rovné maximálnym historickým peakom pre všetko

Cluster má nízke utilization a Pods ostávajú Pending.

### BestEffort pre kritický system component

Pri pressure bude workload nestabilný a scheduling nepredvídateľný.

### QoS považované za high-availability garanciu

Guaranteed Pod môže zlyhať, byť preempted, evicted alebo stratiť Node.

### Zmena limitu bez load testu

Resource policy môže zmeniť latency, throughput, GC a probe behavior.

## 26. Kontrolné otázky

1. Aký je rozdiel medzi requestom a limitom?
2. Prečo scheduler nepoužíva live CPU utilization?
3. Ako sa enforcementuje CPU limit a memory limit?
4. Ako rozlíšiš cgroup OOM od Node-level OOM?
5. Aké sú QoS classes a z čoho sa odvodzujú?
6. Prečo Guaranteed nie je automaticky „najlepšie“ nastavenie?
7. Ako ephemeral storage ovplyvňuje eviction?
8. Ako requests ovplyvňujú HPA?
9. Čo je RuntimeClass overhead?
10. Ako diagnostikuješ CPU throttling bez vysokej Node utilization?

## Glossary impact

Relevantné pojmy: resource request, resource limit, CPU millicore, CPU throttling, memory limit, cgroup OOM, Node OOM, Node allocatable, Guaranteed QoS, Burstable QoS, BestEffort QoS, ephemeral-storage request, huge pages, extended resource, RuntimeClass overhead, CPU Manager a resource overcommitment.

## Oficiálna dokumentácia

- [Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Pod Quality of Service Classes](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [Resource Managers](https://kubernetes.io/docs/concepts/workloads/resource-managers/)
- [Manage Memory, CPU, and API Resources](https://kubernetes.io/docs/tasks/administer-cluster/manage-resources/)
