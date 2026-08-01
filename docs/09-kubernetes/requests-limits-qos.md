# Requests, limits a QoS

Requests a limits riešia dve rozdielne otázky. Requests hovoria scheduleru a resource managementu, koľko kapacity má workload dostať pri placement-e a contention. Limits určujú hornú hranicu, ktorú runtime a kernel uplatňujú podľa typu resource. QoS class je odvodená z kombinácie requests a limits a ovplyvňuje správanie pri Node pressure. Žiadna z týchto hodnôt automaticky neurčuje výkon alebo SLO aplikácie.

Pre `payments-api` chceme request, ktorý reprezentuje bežnú potrebnú kapacitu jednej repliky, a limit, ktorý zabráni jednej chybnej replike vyčerpať celý Node. Zároveň nesmie byť limit taký nízky, aby normálny burst spôsoboval throttling alebo OOM.

## CPU request

```yaml
resources:
  requests:
    cpu: 250m
```

`250m` znamená štvrtinu jedného CPU v Kubernetes quantity modeli. Scheduler používa request pri fit rozhodnutí. Na Node-e CPU shares/weight ovplyvňujú relatívny prístup pri contention.

Request nie je tvrdá rezervácia fyzického core v bežnom shared model-e. Ak Node nemá contention, process môže používať viac CPU až po limit alebo dostupnú kapacitu.

## CPU limit a throttling

```yaml
resources:
  limits:
    cpu: "1"
```

CPU limit sa typicky realizuje cgroup quota. Workload môže v krátkom období spotrebovať svoj budget a byť throttled, aj keď application vidí dostupné CPU a host má iné idle cores podľa runtime/kernel konfigurácie.

```text
CPU usage rastie
→ cgroup vyčerpá quota v period
→ tasks čakajú do ďalšej period
→ latency rastie bez container restartu
```

Kubernetes Pod status nemusí ukázať explicitnú chybu. Potrebujeme cgroup throttling metrics a application latency.

`kubectl top` ukazuje usage sample, nie throttled time ani runnable pressure.

## Memory request

```yaml
resources:
  requests:
    memory: 256Mi
```

Scheduler používa memory request pri placement-e. Kubelet a eviction manager ho zohľadňujú pri niektorých pressure rozhodnutiach cez QoS a usage nad requestom.

Ak request výrazne podhodnotíme, scheduler môže na Node umiestniť viac Podov, než reálne zvládne. Ak ho nadhodnotíme, cluster bude vyzerať plný napriek nízkemu usage.

## Memory limit a OOM

```yaml
resources:
  limits:
    memory: 512Mi
```

Memory nie je throttlovaná rovnako ako CPU pri prekročení hard limitu. Kernel môže spustiť cgroup OOM a ukončiť process.

```bash
kubectl get pod -n production <pod-name> \
  -o jsonpath='{.status.containerStatuses[0].lastState.terminated}' | jq .
```

Reason `OOMKilled` je dôležitý dôkaz, ale root cause môže byť memory leak, legitimate burst, nesprávny limit, page cache, sidecar alebo zmena trafficu.

Container sa môže podľa restart policy spustiť znova v tom istom Pod UID. Readiness flapping a restart storm potom ovplyvnia rollout aj Service capacity.

## Ephemeral storage

Requests a limits možno definovať aj pre `ephemeral-storage`:

```yaml
resources:
  requests:
    ephemeral-storage: 256Mi
  limits:
    ephemeral-storage: 1Gi
```

Ephemeral storage zahŕňa podľa Node/runtime modelu writable layers, logs a `emptyDir` na local storage. Prekročenie limitu alebo Node disk pressure môže viesť k eviction.

Aplikácia, ktorá nekontrolovane loguje do container filesystemu, môže poškodiť celý Node. Log rotation a central collection ostávajú potrebné.

## QoS classes

QoS class sa vypočíta z requests a limits všetkých containers v Pode. `Guaranteed` vyžaduje pre každý CPU a memory resource rovnaký request a limit; `Burstable` pokrýva ostatné Pods s aspoň jedným requestom alebo limitom a `BestEffort` nemá ani jedno. Class je teda vlastnosť admitted Pod specu, nie voľne nastavený label.

Kubelet používa QoS spolu s usage, priority a Node pressure pri eviction rozhodovaní. Vyššia class znižuje relatívne riziko, ale negarantuje prežitie, výkon ani absenciu OOM v container limite. Read-back musí kontrolovať effective requests a limits po admission a skutočný Pod `status.qosClass`.

Kubernetes odvodzuje Pod QoS class.

### Guaranteed

Každý container má CPU aj memory request a limit a pre daný resource sa request rovná limitu.

```yaml
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

Guaranteed zvyšuje ochranu pri Node pressure, ale neznamená zero eviction ani garantovaný aplikačný výkon.

### Burstable

Aspoň jeden container má request alebo limit, ale Pod nespĺňa Guaranteed podmienky. Bežný model `request < limit` patrí sem.

### BestEffort

Žiadny container nemá CPU ani memory request/limit. Taký Pod je pri memory pressure najľahšie evictovateľný a scheduler nemá deklarovanú potrebu pre placement.

```bash
kubectl get pod -n production <pod-name> \
  -o jsonpath='{.status.qosClass}{"\n"}'
```

## Pod resources sú súčtom containers

Scheduler počíta requests všetkých regular containers a podľa init-container semantics aj efektívny Pod request. Sidecar, service mesh proxy alebo log agent môže výrazne meniť footprint.

```text
api request 250m/256Mi
+ proxy request 100m/128Mi
+ agent request 50m/64Mi
→ Pod request 400m/448Mi
```

Pri OOM sa pozri na každý container. Hlavná aplikácia môže byť v limite, no sidecar môže vyčerpať Pod/Node kapacitu.

## Init containers a scheduling

Regular init containers bežia sekvenčne. Scheduler pre príslušný resource zohľadňuje efektívnu hodnotu podľa kombinácie sumy app containers a maxima init requirements podľa API semantics.

Veľký init request môže zablokovať scheduling, aj keď dlhodobý application footprint je malý. Naopak, príliš malý request môže spôsobiť pressure počas startupu.

## LimitRange

LimitRange môže dopĺňať default requests/limits alebo vynucovať min/max v namespace.

```bash
kubectl get limitrange -n production -o yaml
```

Manifest bez resources môže po admission dostať defaults. Server-side dry-run ukáže admitted výsledok:

```bash
kubectl apply --dry-run=server -f deployment.yaml -o yaml
```

Default limit môže nečakane CPU throttliť legacy workload, ktorý predtým limit nemal.

## ResourceQuota

Quota obmedzuje súčet requests, limits alebo object count v namespace.

```bash
kubectl get resourcequota -n production -o yaml
```

Deployment controller môže vytvoriť ReplicaSet, ale Pod create zlyhá na quota. Scheduler Pod nikdy neuvidí. Events a ReplicaSet conditions ukážu admission failure.

HPA scale-up môže byť zablokovaný quota aj vtedy, keď Nodes majú voľnú kapacitu.

## Extended resources a hugepages

Devices alebo hugepages sa deklarujú ako resources podľa pluginu a API contractu. Extended resources sa typicky requestujú s rovnakou limit hodnotou a nie sú overcommitted ako CPU.

```yaml
resources:
  limits:
    nvidia.com/gpu: 1
```

Scheduler vidí advertised inventory. Device plugin a runtime ešte musia konkrétne zariadenie prideliť a sprístupniť.

## Pod-level resources

Kubernetes verzie môžu podporovať Pod-level resource declarations pre vybrané resources a feature states. Pri ich použití treba overiť cieľovú API verziu, feature gate a interakciu s container-level values. Dokumentácia tejto sekcie používa všeobecne prenositeľný container-level model, kým platforma výslovne neschváli Pod-level contract.

## Sizing podľa meraní

Request sa nemá vyberať ako priemer bez kontextu. Potrebujeme distribúciu usage pri reprezentatívnom trafficu, startup burst, GC, sidecars, dependency latency a SLO.

Praktický proces:

```text
zmeraj per-replica usage a throttling
→ oddeľ steady state a burst
→ zohľadni startup a failover load
→ nastav request pre plánovanie a contention
→ nastav limit podľa ochrany a performance testu
→ over rollout a Node packing
→ pravidelne rekalibruj
```

P95 memory usage nie je automaticky bezpečný limit, ak nad ním existujú legitímne spikes alebo leak signature.

## CPU a HPA interaction

HPA CPU utilization sa pri resource metric modeli počíta voči CPU requestu. Ak request znížime na polovicu bez zmeny usage, reported utilization sa približne zdvojnásobí a HPA môže scale-upovať.

Request je teda nielen scheduler input, ale aj denominator autoscaling signálu. Zmena requests potrebuje HPA revalidation.

CPU limit môže zase spôsobiť throttling, ktorý zníži measured CPU usage a zároveň zvýši latency. HPA potom nemusí reagovať tak, ako očakávame.

## Node pressure a eviction

Kubelet sleduje memory, disk, inode a PID pressure. Pri prekročení thresholds môže reclaimovať resources a evictovať Pods podľa policy, QoS a usage.

Evicted Pod dostane nový lifecycle; controller vytvorí replacement. To sa líši od container OOM restartu v rovnakom Pode.

```bash
kubectl get pod -n production <pod-name> -o yaml
kubectl describe node <node-name>
```

Pri Node pressure incident-e potrebujeme Node-level evidence, nie iba Pod limits.

## Incident: CPU limit vytvoril latency bez errors

`payments-api` mala request 250m a limit 500m. Nová verzia robila viac JSON validation a pri traffic burstoch pravidelne vyčerpala CPU quota. Pods zostávali Running a Ready, no p99 latency stúpla nad timeout edge proxy.

HPA používala CPU utilization voči requestu, ale throttling obmedzil usage. Scale-up bol pomalší než očakávanie. Oprava zvýšila limit po performance teste, upravila request a pridala throttling metric do release gate-u.

## Incident: OOM vyzeral ako liveness problém

Container opakovane reštartoval a Events ukazovali liveness failures. `lastState.terminated.reason` však bol `OOMKilled`; liveness request iba zlyhal počas memory pressure tesne pred killom.

Vypnutie liveness by nepomohlo. Root cause bol neobmedzený in-memory batch po zmene configu. Oprava ohraničila batch, nastavila realistický limit a overila memory profile.

## Incident: quota blokovala rollout

Namespace quota povoľovala requests pre šesť replík, ale nie pre surge siedmu repliku. Deployment s `maxUnavailable: 0` nemohol odstrániť starý Pod a nový Pod create zlyhával na quota.

Nodes mali voľnú kapacitu. Oprava zvýšila reviewovanú rollout quota alebo upravila rollout budget podľa availability. Skorší control je quota-aware preflight nad admitted template.

## Model, ktorý si treba odniesť

Requests riadia scheduling a relatívne resource entitlement. Limits ohraničujú runtime spotrebu. CPU limit môže throttliť, memory limit môže vyvolať OOM a ephemeral-storage limit alebo Node pressure môže viesť k eviction. QoS class ovplyvňuje pressure behavior, nie business SLO. Sizing musí vychádzať z meraní a musí sa revalidovať spolu s HPA, rollout kapacitou a quota.

## Referencie

- [Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- [Pod Quality of Service Classes](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/)
- [Node-pressure Eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Scheduling](scheduling.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Probes →](probes.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
