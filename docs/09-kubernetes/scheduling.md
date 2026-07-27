# Scheduling

Kubernetes scheduling je placement decision pre konkrétny Pod UID. Scheduler neštartuje container a nepreukazuje, že workload bude Ready. Vyhodnotí current Pod contract proti current cluster inventory, vyberie feasible Node, aplikuje scoring a zapíše binding. Následné CNI, CSI, image, kubelet alebo application failures patria do inej execution fázy.

Táto kapitola používa jeden dominantný lifecycle:

```text
placement intent a Pod generation
→ scheduling readiness, queue a profile identity
→ fresh Node/resource/topology/storage inventory
→ hard-constraint filtering
→ feasible-Node set
→ preference scoring
→ reserve, permit a pre-bind coordination
→ binding
→ kubelet acceptance a execution
→ placement, availability a business verification
→ reschedule, preemption, capacity alebo constraint recovery
```

## 1. Atlas Payments placement subject

Deployment Payments 5.3.0 potrebuje počas rollout-u šesť replík. Placement contract:

```text
workload: production/payments-api
Pod template generation: D53/RS53
schedulerName: default-scheduler
requests: 750m CPU, 768Mi memory
zones: najmenej dve
maxSkew: 1
required node pool: general-linux-v4
forbidden Nodes: PCI-isolated a control-plane
PVC: žiadne pre API repliku
hostPort: žiadny
availability invariant: najmenej 5 accepted endpoints počas rollout-u
```

Exact scheduling subject je konkrétny Pod UID a jeden scheduling attempt:

```text
Pod UID, generation a creation timestamp
schedulerName a scheduler profile/config generation
queue state, attempt number a backoff
admitted requests/overhead a scheduling gates
Node UID inventory, labels, taints, conditions a allocatable
existing Pod requests, host ports a device allocations
PVC/PV topology a attach limits
required/preferred affinity, topology spread a priorities
filter failure reasons a feasible-Node set
score vector a selected Node
reserve/permit/pre-bind/bind outcome
```

Rovnaký Pod template vytvorený o minútu neskôr môže dostať iné feasible Nodes, pretože cluster snapshot sa zmenil.

## 2. Queue a scheduling readiness

Pod bez `spec.nodeName` a s príslušným `schedulerName` čaká v scheduler workflow. Interný stav môže zahŕňať active, backoff a unschedulable queues.

```text
Pod create
→ admission/defaulting
→ scheduling gates odstránené alebo žiadne
→ active queue
→ scheduling attempt A17
→ success alebo unschedulable/backoff
```

Pod bez Eventov a bez Node-u môže znamenať:

- nesprávny `schedulerName`;
- scheduler/profile nebeží;
- Pod ešte nie je scheduling-ready;
- scheduler queue alebo API watch je degradovaný;
- admission vytvorila iný effective contract;
- Event/evidence už expirovali alebo nie sú pozorované správnym scope-om.

## 3. Scheduling cycle a binding cycle

Moderný scheduler používa pluggable Scheduling Framework. Pre výklad sú dôležité dve fázy:

```text
scheduling cycle
  pre-filter/filter
  → feasible Nodes
  → pre-score/score
  → selected Node

binding cycle
  reserve
  → permit
  → pre-bind
  → bind
  → post-bind
```

Reserve alebo permit state môže byť dočasný a potrebuje rollback cez `Unreserve`, ak neskorší krok zlyhá. External alebo custom plugin v synchronous scheduling path-e môže zablokovať veľké množstvo Pods.

## 4. Hard constraints vytvárajú feasible-Node set

Filter fáza odpovedá:

```text
Môže tento exact Pod bežať na tomto exact Node-e podľa current contractu?
```

Typical hard constraints:

- Node je Ready a schedulable;
- Pod requests sa zmestia do allocatable po započítaní existing reservations;
- required node selector/affinity sa zhoduje;
- všetky `NoSchedule`/`NoExecute` taints majú správne tolerations;
- required Pod affinity/anti-affinity je splnená;
- topology spread hard constraints sú splniteľné;
- host IP/port nie je v konflikte;
- RuntimeClass handler/overhead je dostupný;
- extended resource/device existuje;
- PVC topology a attach limity sú kompatibilné;
- max Pod count a ďalšie Node limity nie sú vyčerpané.

Intersection všetkých constraints môže byť prázdny, aj keď každá constraint samostatne má kandidátov.

```text
resource-fit Nodes {N1,N2,N3,N4}
∩ zone-B Nodes {N3,N4,N5}
∩ untainted-compatible Nodes {N4,N5}
∩ volume-compatible Nodes {N3}
= ∅
```

## 5. Requests, nie live usage, riadia resource fit

Scheduler typicky porovnáva:

```text
sum(admitted Pod requests na Node-e)
+ request nového Podu
+ relevantný overhead
≤ Node allocatable
```

Node môže mať 20 % live CPU utilization a zároveň vracať `Insufficient cpu`, pretože requests už rezervujú allocatable. Naopak nízke requests môžu umožniť placement, ktorý neskôr vytvorí runtime contention.

Requests sú placement/capacity contract, nie performance guarantee.

## 6. Node identity, labels a taints

### Required identity

`nodeSelector` alebo required affinity zužujú feasible set. Labels používané na compliance alebo security placement potrebujú dôveryhodného ownera. Kompromitovaný kubelet alebo voľne editovateľný Node label nesmie umožniť workloadu vstúpiť do privileged poolu.

### Taints a tolerations

Taint odpudzuje. Toleration iba povoľuje Podu zniesť taint; nepriťahuje ho na tento Node.

Pre dedicated Nodes je typický contract:

```text
taint chráni pool pred cudzími workloadmi
+ toleration povoľuje oprávnený workload
+ affinity vyberá dedicated pool
```

Toleration bez affinity môže umiestniť workload aj na general Nodes.

## 7. Affinity a topology sú capacity constraints

Required Pod anti-affinity môže vyžadovať jednu repliku na každý hostname alebo zone. Ak existujú iba tri eligible domains a workload chce šesť replík s hard one-per-domain contractom, ďalšie Pods sú permanentne unschedulable.

Topology spread používa matching Pod inventory, eligible domains, `maxSkew` a `whenUnsatisfiable`. Správne rozloženie labels nepreukazuje nezávislé failure domains, ak všetky zones zdieľajú rovnaký power, storage alebo network dependency.

Soft preference (`preferred`) ovplyvňuje score, ale nesmie byť interpretovaná ako guarantee.

## 8. Scoring vyberá medzi feasible Nodes

Score fáza neodstraňuje hard-invalid Nodes. Zoradí už feasible Nodes podľa active profile-u, napríklad:

- resource balance/bin packing;
- preferred affinity;
- topology spread preference;
- image locality;
- inter-Pod affinity;
- custom platform score.

Score je function current profile weights a snapshotu. „Najvyššie skóre“ neznamená objektívne najlepší Node pre business SLO.

Pri troubleshooting-u zachovaj scheduler profile/config generation. Hidden `addedAffinity` alebo custom plugin môže vytvoriť constraints, ktoré nie sú v Pod YAML-e.

## 9. Storage je súčasť placementu

Pod s PVC potrebuje Node kompatibilný s:

- PV node affinity/topology;
- StorageClass `WaitForFirstConsumer` decision;
- CSI storage capacity;
- volume attach limitom;
- access mode a existing attachment;
- všetkými claims naraz.

Pri delayed bindingu scheduler a provisioner koordinujú topology. `nodeName` tento mechanizmus obchádza a môže ponechať PVC bez správneho selected-node contextu.

## 10. Host ports a scarce resources

`hostPort`, GPU, FPGA, huge pages, local devices a exclusive CPU môžu vytvoriť per-Node scarcity, ktorú aggregate CPU/memory dashboard neukáže.

HostPort môže blokovať rollout:

```text
old Pod terminating na N4 stále drží TCP/8080
→ new Pod potrebuje rovnaký hostPort
→ N4 filter fail
→ ostatné Nodes blokuje topology alebo resources
→ rollout stojí
```

Service networking je zvyčajne flexibilnejšie než hostPort pre bežnú exposure.

## 11. Binding je point of placement authority

Po úspešnom bindingu má Pod `spec.nodeName`. Scheduler už spravidla nerieši jeho runtime realization.

```text
binding P53 → N9
→ kubelet N9 pozoruje Pod
→ volume/CNI/image/runtime execution
→ container start
→ probes/readiness
```

Pod `Scheduled=True` a stále `Pending` preto presúva diagnostiku na kubelet, runtime, CNI, CSI, image alebo admission/runtime config. Opakované mazanie Podu môže iba meniť Node a maskovať node-specific failure.

## 12. Priority a preemption

Priority ovplyvňuje queue ordering a môže umožniť preemption lower-priority Pods. Preemption je candidate recovery pre resource scarcity, nie universal solver.

```text
high-priority Pod nemá feasible Node
→ scheduler skúsi odstrániť lower-priority victims
→ ak po ich odstránení vznikne feasible Node, nominuje candidate
→ victims terminujú
→ Pod sa znovu vyhodnotí a bindne
```

Preemption nepomôže pri:

- required label/affinity mismatch;
- neakceptovanom taint-e;
- wrong volume zone;
- chýbajúcom device/RuntimeClass;
- hostPort, ktorý drží non-preemptable alebo terminating state;
- topology contracte bez dostatku domains.

`nominatedNodeName` nie je final binding. Preemption tiež môže porušiť availability, vytvoriť churn alebo čakať na termination budget.

## 13. Cluster autoscaler nie je constraint solver

Autoscaler môže pridať Nodes, ak existuje node-group template, na ktorom by Pod bol schedulovateľný. Nepomôže, ak:

- žiadna node group nemá required label/device/zone;
- PVC je viazané na inú topology;
- hard anti-affinity je logicky nemožná;
- quota/admission blokuje Pod;
- custom scheduler nebeží;
- hostPort/topology contract nemá validný shape.

`Pod didn't trigger scale-up` je signál pre feasibility analýzu, nie automaticky autoscaler bug.

## 14. Worked failure: toleration bez affinity poslala workload do nesprávneho poolu

Payments workload mal toleration pre `pci=true:NoSchedule`, pretože časť deploymentu mala byť schopná bežať na PCI Nodes. Chýbala však affinity na general pool pre bežnú cohortu.

```text
toleration odstránila taint barrier
→ PCI Node sa stal feasible
→ scoring ho vybral pre nízku utilization
→ non-PCI workload získal reachability k citlivejším platform resources
```

Fix rozdelil workload identities/profiles, pridal required pool affinity a admission testoval forbidden placement.

## 15. Worked failure: `nodeName` obišlo storage topology

Operator nastavil `nodeName: worker-b7` na debug Pod používajúci PVC s `WaitForFirstConsumer`.

```text
scheduler bol obídený
→ provisioner nedostal štandardný scheduling context
→ PVC ostala Pending alebo vznikol topology conflict
```

Fix odstránil `nodeName`, použil node affinity a nechal scheduler koordinovať claim. Priamy Node binding nebol „silnejšia preference“, ale obídenie placement protocolu.

## 16. Worked failure: preemption vytvorila churn bez feasible Node-u

Critical Pod mal vysokú priority, required zone C a volume v zone B. Scheduler skúšal preemption, ale odstránenie victims nemohlo zmeniť volume topology.

Dôsledok:

```text
victim analysis/preemption attempts
→ workload disruption
→ critical Pod stále unschedulable
```

Recovery opravila data/placement contract. Zvýšenie priority by iba zväčšilo blast radius.

## 17. Worked failure: hidden scheduler profile constraint

Manifest povoľoval všetky general Nodes, ale scheduler profile obsahoval `addedAffinity` na `scheduler-tier=gold`. Nové Nodes nemali label.

```text
source YAML feasible podľa reviewera
→ resolved scheduler profile pridal hard constraint
→ 0/N nodes available
```

Rozhodujúci subject bol profile generation, nie iba Pod manifest. Platform doplnila resolved-placement evidence a profile conformance test pri Node join-e.

## 18. Causal troubleshooting walkthrough: CPU je voľné, rollout Pods sú Pending

Symptóm:

```text
Deployment D53 chce 6 replík
old RS52 má 5 available
new RS53: 1 running, 3 Pending
cluster dashboard: priemerne 35 % CPU
FailedScheduling: 0/12 nodes are available
```

### 1. Zafixuj subject a availability outcome

Pre každý Pending Pod zaznamenaj:

```text
Pod UID/generation a owner revision
schedulerName/profile generation
admitted requests, RuntimeClass overhead a priority
queue attempt/backoff a FailedScheduling message
required/preferred affinity, taints/tolerations a topology spread
host ports/devices
PVC/PV topology a attach state
Node UID inventory, labels, taints, allocatable a existing requests
rollout surge/unavailable budget
```

Pôvodný outcome: počas rollout-u ostane minimálne 5 accepted endpoints a payment p99 neprekročí SLO.

### 2. Competing hypotheses

| Hypotéza | Diskriminačný dôkaz |
|---|---|
| requests vyčerpali allocatable | per-Node sum requests + new request |
| live CPU dashboard je zavádzajúci | requests vs. usage comparison |
| required affinity/label nemá kandidátov | exact Node label inventory |
| untolerated taint zužuje set | taints/effects a admitted tolerations |
| topology spread/anti-affinity je nemožná | eligible domains a matching Pod counts |
| hostPort držia old/terminating Pods | per-Node socket/Pod inventory |
| PVC topology intersection je prázdny | PV affinities a selected-node state |
| custom scheduler/profile je degraded | queue/plugin metrics a leader/config generation |
| preemption nepomôže kvôli hard constraint | scheduler Event a simulated post-victim feasibility |

### 3. Vytvor constraint matrix

Pre každý Node eviduj postupné vyradenie:

| Node | Resource fit | Affinity | Taint | Topology | Port | Storage | Feasible |
|---|---|---|---|---|---|---|---|
| N1 | áno | áno | nie | — | — | — | nie |
| N2 | nie | — | — | — | — | — | nie |
| N3 | áno | áno | áno | nie | — | — | nie |
| N4 | áno | áno | áno | áno | nie | — | nie |

Takto sa „0/12“ zmení na vysvetliteľný empty intersection.

### 4. Containment

- pozastav ďalší rollout scale-up/old-RS scale-down;
- zachovaj old accepted capacity;
- nevypínaj affinity/taints ani neznižuj requests naslepo;
- nezvyšuj priority bez victim/blast-radius analýzy;
- nemaž Pending Pods, kým template zostáva rovnaký;
- nepoužívaj `nodeName` ako bypass.

### 5. Authoritative recovery

Finding:

```text
new Pods requestovali 750m CPU
+ old Pods a DaemonSet requests rezervovali allocatable
+ topology spread vyžadoval zone C
+ zone C Nodes mali hostPort obsadený terminating old cohortou
```

Recovery:

1. predĺžila drain len tam, kde bolo potrebné dokončiť requests, ale odstránila zbytočný hostPort contract;
2. zachovala requests podľa load evidence;
3. pridala rollout capacity pre zone C;
4. prepočítala spread a surge feasibility pred ďalším reconcile;
5. obnovila rollout po jednej zone.

### 6. Over pôvodný a forbidden outcome

Potvrď:

- každý new Pod má zdokumentovaný scheduling attempt a correct Node binding;
- new cohort je rozložená cez požadované zones s `maxSkew` contractom;
- žiadny Pod nie je na PCI/control-plane Node-e;
- old capacity sa scale-downuje až po accepted new endpoints;
- kubelet/CNI/runtime execution prejde po bindingu;
- payment synthetic prejde cez každú zone cohortu;
- preemption nespôsobila neakceptovanú stratu iného critical workloadu;
- next replica a next Node join prejdú rovnakým preflightom.

### 7. Posuň control skôr

Pridaj:

- resolved scheduler profile/config do release evidence;
- preflight feasible-Node a topology intersection pre surge cohortu;
- request/allocatable reservation dashboard, nie iba usage;
- hostPort a terminating-overlap inventory;
- PVC topology/attach feasibility test;
- trusted Node label ownership policy;
- priority/preemption victim simulation;
- cluster-autoscaler node-group capability matrix;
- placement synthetic a per-zone business acceptance.

## 19. Observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| Intent | workload placement contract | availability, compliance, topology, forbidden Nodes |
| Pod | UID/generation | admitted spec, requests, affinity, priority, schedulerName |
| Queue | scheduling attempt | queue state, backoff, latency, gates |
| Profile | scheduler config generation | plugins, weights, added constraints, leader |
| Nodes | candidate inventory | UIDs, labels, taints, conditions, allocatable |
| Resources | reservation state | existing requests, overhead, device/port usage |
| Storage | PVC/PV placement subject | topology, capacity, attach limit, selected Node |
| Filter | feasible-Node set | per-plugin failure reasons |
| Score | score vector | preferences, weights, selected candidate |
| Binding | Pod→Node decision | reserve/permit/pre-bind/bind outcome |
| Execution | kubelet/runtime subject | sandbox, mount, image, probes |
| Business | revision/cohort | endpoints, SLO, failure-domain acceptance |

## 20. Referenčné príkazy

```bash
kubectl get pod -A --field-selector=status.phase=Pending -o wide
kubectl describe pod <pod> -n <namespace>
kubectl get events -A --sort-by=.metadata.creationTimestamp
kubectl get nodes --show-labels
kubectl describe node <node>
kubectl get priorityclass
kubectl get pvc,pv -A -o wide
```

Scheduler metrics doplň o queue size, attempts, plugin duration, unschedulable reasons, preemption a binding errors.

## 21. Referenčné pravidlá

- Scheduler priraďuje Pod k Node-u; kubelet ho až následne realizuje.
- Scheduling subject je exact Pod UID a attempt, nie iba Deployment.
- Filter vytvára feasible set; score iba zoradí feasible Nodes.
- Requests a overhead, nie live usage, určujú resource fit.
- Hard constraints sa skladajú ako intersection.
- Toleration povoľuje taint; nevyberá dedicated Node.
- Preferred affinity je preference, nie guarantee.
- `nodeName` obchádza scheduler a môže rozbiť storage coordination.
- Storage, host ports a devices môžu byť dominantná placement constraint.
- Priority nie je capacity; preemption nerieši non-resource hard mismatch.
- `nominatedNodeName` nie je binding.
- Scheduled neznamená Running, Ready ani business accepted.
- Recovery musí overiť placement, execution, failure-domain distribution a workload outcome.

## 22. Kontrolné otázky

1. Aký lifecycle spája Pod placement intent s accepted running cohortou?
2. Ako sa líšia scheduling cycle a binding cycle?
3. Prečo môže byť feasible-Node intersection prázdny pri voľnej CPU?
4. Prečo scheduler používa requests namiesto live usage?
5. Ako sa líšia taint, toleration a node affinity?
6. Kedy topology spread vytvorí hard unschedulability?
7. Ako storage a hostPort menia placement?
8. Čo preemption dokáže a čo nedokáže?
9. Prečo musíš poznať scheduler profile generation?
10. Čo musí scheduling acceptance verdict overiť?

## Glossary impact

Relevantné pojmy: scheduling lifecycle subject, Pod scheduling attempt, scheduling readiness, scheduler profile generation, Node candidate inventory, hard-constraint intersection, feasible-Node set, scheduler score vector, reserve/permit subject, binding subject, topology feasibility, storage-placement intersection, preemption recovery subject, resolved placement evidence, scheduling observation matrix a scheduling acceptance verdict.

## Oficiálna dokumentácia

- [Kubernetes Scheduler](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/)
- [Scheduling Framework](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/)
- [Scheduling, Preemption and Eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/)
- [Scheduler Configuration](https://kubernetes.io/docs/reference/scheduling/config/)
- [Pod Priority and Preemption](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Volumes, PV, PVC a StorageClass](volumes-pv-pvc-storageclass.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Requests, limits a QoS →](requests-limits-qos.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
