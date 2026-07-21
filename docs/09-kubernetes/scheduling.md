# Scheduling

Kubernetes scheduling je proces výberu vhodného Node-u pre Pod, ktorý ešte nemá `spec.nodeName`. `kube-scheduler` sleduje pending Pods, vyhodnotí constraints a dostupné resources, zoradí feasible Nodes a zapíše binding rozhodnutie do API. Scheduler Pod nespúšťa; po bindingu ho realizuje kubelet na vybranom Node-e.

## 1. Základný flow

```text
Pod bez nodeName
→ scheduling queue
→ filtering
→ scoring
→ reserve/permit/pre-bind
→ binding
→ kubelet sync
→ container runtime
```

Pod môže zostať `Pending`, aj keď cluster má voľné CPU alebo memory, pretože placement blokujú iné podmienky:

- taints a tolerations,
- node affinity/selector,
- Pod affinity/anti-affinity,
- topology spread,
- PVC topology,
- host ports,
- resource requests,
- volume attach limits,
- runtime class,
- admission alebo custom scheduler constraints.

## 2. Scheduling queue

Scheduler spracúva Pods v queue. Reálne môže používať viac interných queue stavov, napríklad:

- active queue,
- backoff queue,
- unschedulable pool.

Keď sa cluster state zmení — pribudne Node, uvoľnia sa resources alebo sa zmení constraint — Pod môže byť znovu zaradený na vyhodnotenie.

Queue latency je dôležitý control-plane signal. Dlhé čakanie nemusí znamenať iba nedostatok kapacity; môže ísť o scheduler throughput, plugin latency alebo veľké množstvo unschedulable Pods.

## 3. Scheduling Framework

Moderný `kube-scheduler` používa pluggable Scheduling Framework.

Hlavné extension points zahŕňajú:

- `PreEnqueue`,
- `QueueSort`,
- `PreFilter`,
- `Filter`,
- `PostFilter`,
- `PreScore`,
- `Score`,
- `NormalizeScore`,
- `Reserve` / `Unreserve`,
- `Permit`,
- `PreBind`,
- `Bind`,
- `PostBind`.

Nie každý plugin používa každý extension point. Scheduler profile určuje, ktoré pluginy sú aktívne a s akou konfiguráciou.

## 4. Filtering

Filter fáza odstráni Nodes, ktoré Pod nemôžu hostiť.

Príklady filter dôvodov:

- insufficient CPU/memory/ephemeral storage,
- nesplnený node selector alebo required affinity,
- neakceptovaný taint,
- konflikt host portu,
- volume node affinity conflict,
- volume attach limit,
- required Pod anti-affinity,
- nekompatibilný RuntimeClass overhead alebo handler,
- Node unschedulable/cordoned.

Výsledkom je množina feasible Nodes.

## 5. Scoring

Score fáza zoradí feasible Nodes podľa preferencií.

Príklady:

- resource balance alebo utilization strategy,
- preferred node affinity,
- topology spread,
- image locality,
- inter-Pod affinity,
- storage capacity/topology podľa konfigurácie,
- custom plugin score.

Najvyššie skóre nie je absolútna „najlepšia mašina“. Je výsledok aktuálneho scheduler profile-u a váh.

Pri rovnosti môže scheduler vybrať jeden z top kandidátov podľa interného selection mechanizmu.

## 6. Binding

Binding zapíše vybraný Node do Podu.

Po úspešnom bindingu:

- Pod má `spec.nodeName`,
- scheduler už bežne neriadi jeho runtime,
- kubelet na danom Node-e začne realizovať Pod,
- CNI/CSI/runtime failures môžu nastať až po úspešnom scheduling-u.

Scheduled neznamená Running ani Ready.

## 7. `nodeName`

Priame nastavenie:

```yaml
spec:
  nodeName: worker-1
```

obchádza bežné scheduler rozhodovanie.

Dôsledky:

- scheduler nevyhodnotí resource fit,
- neaplikuje affinity, topology alebo scoring,
- môže sa obísť `WaitForFirstConsumer` storage koordinácia,
- kubelet môže Pod odmietnuť alebo ho nevedieť spustiť.

Používaj iba pre úzky bootstrap/debug contract. Pre bežné placement používaj selectors, affinity, taints/tolerations a scheduler.

## 8. `schedulerName`

Pod môže vybrať iný scheduler:

```yaml
spec:
  schedulerName: custom-scheduler
```

Ak príslušný scheduler nebeží alebo nesleduje dané meno, Pod zostane bez Node-u.

Multiple schedulers vyžadujú:

- jednoznačný ownership,
- kompatibilné policies,
- observability,
- upgrade/version contract,
- ochranu pred konfliktmi a starvation.

## 9. Resource requests pri scheduling-u

Scheduler používa requests, nie aktuálnu okamžitú spotrebu.

Node môže mať nízke reálne utilization, ale Pod sa nezmestí, ak:

```text
sum(requests existujúcich Podov) + request nového Podu > Node allocatable
```

Naopak Pod s príliš nízkym requestom môže byť schedulovaný na preťažený Node a neskôr vytvoriť contention.

Requests sú placement a capacity-reservation signál, nie garantované performance SLO.

## 10. Node capacity a allocatable

Node publikuje:

- `capacity` — celkové resources,
- `allocatable` — resources dostupné pre Pods po rezervách platformy.

Rozdiel môže zahŕňať:

- OS/system daemons,
- kubelet reservations,
- eviction thresholds,
- RuntimeClass overhead,
- extended resources.

Scheduler porovnáva Pod requests s allocatable a už rezervovanými requests.

## 11. Node selector a affinity

### `nodeSelector`

Jednoduché exact-match labels:

```yaml
spec:
  nodeSelector:
    kubernetes.io/os: linux
    workload-tier: backend
```

### Required node affinity

Hard constraint. Ak ho žiadny Node nespĺňa, Pod je unschedulable.

### Preferred node affinity

Soft preference so score váhou. Pod sa môže umiestniť aj inde.

Labels používané na security-sensitive placement musia byť chránené pred kompromitovaným kubeletom alebo neautorizovanou zmenou.

## 12. Pod affinity a anti-affinity

Pod affinity umiestňuje workload blízko matching Podov. Anti-affinity ich oddeľuje.

Používa:

- label selector,
- namespace scope,
- topology key, napríklad hostname alebo zone.

Hard anti-affinity môže dramaticky znížiť schedulovateľnosť. Ak požaduješ jednu repliku na každý Node/zone, cluster musí mať dostatočný počet topology domains a kapacitu.

## 13. Topology spread constraints

Topology spread vyjadruje rovnomernejšie rozloženie matching Pods cez failure domains.

Príklady topology keys:

- `kubernetes.io/hostname`,
- `topology.kubernetes.io/zone`,
- `topology.kubernetes.io/region`.

Relevantné koncepty:

- `maxSkew`,
- `whenUnsatisfiable`,
- label selector,
- eligible domains,
- min domains podľa podporovaného API.

Spread nezaručuje dostupnosť, ak všetky Nodes alebo zones zdieľajú inú spoločnú failure dependency.

## 14. Taints a tolerations

Taint je Node-side odpudzovací signál. Toleration umožní Podu taint tolerovať, ale sama o sebe Node nevyberie.

Effects:

- `NoSchedule`,
- `PreferNoSchedule`,
- `NoExecute`.

Pre dedikované Nodes typicky kombinuješ:

- taint,
- toleration,
- node affinity/selector.

Samotná toleration môže Pod umiestniť aj na nededikovaný Node.

## 15. Host ports

Pod žiadajúci host port vytvára per-Node konflikt:

```yaml
ports:
  - containerPort: 8080
    hostPort: 8080
```

Na jednom Node-e môže danú host IP/port/protocol kombináciu používať iba kompatibilná množina workloadov.

HostPort znižuje scheduling flexibility a komplikuje rolling updates. Preferuj Service networking, ak application nemusí bindovať priamo Node socket.

## 16. Volumes a scheduling

Storage môže ovplyvniť placement cez:

- PV node affinity,
- zone/topology,
- attach limits,
- access mode,
- `WaitForFirstConsumer`,
- local PV,
- CSI capacity.

Pod s viacerými PVCs potrebuje Node kompatibilný so všetkými volume constraints.

Unschedulable Event môže obsahovať kombináciu resource a volume dôvodov.

## 17. PriorityClass

PriorityClass nastavuje Pod priority.

Vyššia priorita môže ovplyvniť:

- queue ordering,
- preemption,
- eviction decisions v určitých mechanizmoch,
- kritickosť platformových workloadov.

Priority nie je automatická rezervácia capacity. Vysoká priorita bez kontroly môže vytlačiť dôležité workloady alebo vytvoriť preemption churn.

## 18. Preemption

Ak pending Pod nemá feasible Node, PostFilter plugin môže skúsiť preemption nižšie prioritných Pods.

Zjednodušene:

1. scheduler hľadá Node, kde by odstránenie victims umožnilo placement,
2. vyberie kandidáta,
3. nastaví nominated node podľa mechanizmu,
4. victims sú odstránené,
5. Pod čaká na uvoľnenie resources a znovu scheduling/binding.

Preemption:

- negarantuje okamžitý scheduling,
- rešpektuje časť PodDisruptionBudget logiky, ale nemusí nájsť bezporušujúce riešenie,
- nerieši cross-node preemption pre komplexné anti-affinity prípady,
- môže byť zbytočná, ak hard constraint nie je resource-related.

## 19. Nominated Node

Pending Pod môže mať `status.nominatedNodeName` ako signal, že scheduler očakáva placement po preemption alebo inom mechanizme.

Nie je to finálny binding. Cluster sa môže zmeniť a Pod môže skončiť na inom Node-e.

## 20. Scheduling profiles

`kube-scheduler` môže mať viac profiles s rozdielnym `schedulerName` a plugin configuration.

Použitie:

- workload classes,
- custom scoring,
- added affinity,
- špeciálne batch/latency placement.

Riziká:

- neviditeľné cluster-wide added constraints,
- nekompatibilita pri upgrade,
- zložitejšie troubleshooting,
- rozdiel medzi manifestom a resolved scheduler behavior.

Profile config je kritická control-plane configuration.

## 21. Extenders a custom plugins

Scheduler možno rozšíriť cez framework pluginy alebo legacy/external extender model podľa deploymentu.

Custom scheduling code musí riešiť:

- deterministic decisions,
- API latency a failure,
- cache consistency,
- retries,
- version compatibility,
- metrics a traces,
- security a availability.

Synchronous external dependency v scheduling path-e môže zablokovať veľkú časť clusteru.

## 22. Scheduler performance

Veľký cluster nevyhodnocuje nevyhnutne každý Node pre každý Pod. Scheduler môže zastaviť hľadanie po nájdení dostatočnej vzorky feasible Nodes podľa konfigurácie.

Sleduj:

- pending queue size,
- scheduling attempts,
- scheduling latency,
- plugin execution duration,
- unschedulable reasons,
- API list/watch latency,
- preemption attempts,
- binding errors.

Optimalizácia throughputu nesmie skryť systematicky zlé placement alebo starvation.

## 23. Observability

```bash
kubectl get pod -A --field-selector=status.phase=Pending
kubectl describe pod -n production <pod>
kubectl get events -n production --sort-by=.metadata.creationTimestamp
kubectl get nodes
kubectl describe node <node>
kubectl get priorityclass
```

Dôležitý Event:

```text
FailedScheduling
```

Message môže agregovať dôvody:

- insufficient cpu,
- untolerated taint,
- node affinity mismatch,
- volume node affinity conflict,
- too many pods,
- host port conflict,
- preemption not helpful.

Čítaj celý message, nie iba prvú frázu.

## 24. Troubleshooting

### `0/N nodes are available`

Roztrieď dôvody na:

1. resources,
2. labels/affinity,
3. taints,
4. topology/anti-affinity,
5. storage,
6. ports,
7. node readiness/cordon,
8. custom scheduler/plugin.

### `Insufficient cpu` pri nízkom utilization

Scheduler porovnáva requests s allocatable, nie live CPU usage. Skontroluj requests všetkých Podov a Node reservations.

### Preemption is not helpful

Pod blokuje hard constraint, ktorú odstránenie nižšie prioritných Podov nevyrieši, napríklad label, taint, topology alebo volume mismatch.

### Pod bez Eventov a bez Node-u

Over `schedulerName`, scheduler availability, queue metrics, API watch a admission status.

### Pod je Scheduled, ale stále `Pending`

Scheduling už prebehlo. Pokračuj kubelet/runtime/CNI/CSI/image troubleshootingom.

## 25. Anti-patterny

### `nodeName` ako bežná placement stratégia

Obchádza scheduler a storage topology coordination.

### Required anti-affinity všade

Môže vytvoriť permanentne unschedulable Pods pri malej kapacite.

### Toleration bez affinity pre dedicated Nodes

Workload môže skončiť aj na všeobecných Nodes.

### Requests nastavené podľa priemeru bez burst/risk analýzy

Scheduler preplní Nodes a runtime trpí contention.

### Vysoká priority pre všetko

Priority prestane rozlišovať kritické workloady a preemption bude nepredvídateľná.

### HostPort pre bežnú service exposure

Znižuje rollout a scheduling flexibilitu.

### Ručné mazanie pending Podov bez opravy template-u

Controller vytvorí rovnaký unschedulable Pod znova.

## 26. Kontrolné otázky

1. Aký je rozdiel medzi schedulingom a spustením Podu?
2. Čo robí filter a čo score fáza?
3. Prečo scheduler používa requests namiesto live utilization?
4. Čo sa stane po bindingu?
5. Prečo je `nodeName` nebezpečný pre bežné workloady?
6. Ako sa líši required a preferred affinity?
7. Prečo toleration nevyberá konkrétny Node?
8. Ako storage ovplyvňuje scheduling?
9. Čo preemption rieši a čo nevyrieši?
10. Ako systematicky analyzuješ `FailedScheduling` Event?

## Glossary impact

Relevantné pojmy: Kubernetes scheduling, scheduling queue, feasible Node, Scheduling Framework, filter plugin, score plugin, binding, scheduler profile, `schedulerName`, Node allocatable, required/preferred affinity, topology spread, PriorityClass, preemption, nominated Node a `FailedScheduling`.

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
