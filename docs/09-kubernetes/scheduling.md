# Scheduling

Kubernetes scheduler rozhoduje, na ktorom Node-e má nový Pod bežať. Nevykonáva image pull, nemountuje volume a nespúšťa process. Jeho výsledkom je binding medzi Podom a Node-om. Placement vzniká z kombinácie hard constraints, resource requests, storage topology, taints, affinity, topology spread, priority a scheduler plugins.

Pri `payments-api` chceme šesť replík rozložiť medzi tri zones, nepoložiť dve repliky na ten istý host, vyhnúť sa GPU Nodes a zároveň rešpektovať memory requests. Každé pravidlo samostatne vyzerá rozumne, ale ich kombinácia môže vytvoriť Pod, pre ktorý neexistuje žiadny vhodný Node.

## Od unscheduled Podu k bindingu

Pod po vytvorení nemá `.spec.nodeName`. Scheduler ho zaradí do queue, vytvorí snapshot Node inventory a vykoná filter a score fázy.

```text
Pod bez nodeName
→ pre-filter výpočty
→ filter nevhodných Nodes
→ score vhodných Nodes
→ reserve/permit podľa pluginov
→ bind Pod na Node
```

Po bindingu kubelet na vybranom Node-e prevezme runtime realizáciu.

```bash
kubectl get pod -n production <pod-name> \
  -o custom-columns='NAME:.metadata.name,NODE:.spec.nodeName,SCHEDULED:.status.conditions[?(@.type=="PodScheduled")].status'
```

Prázdny Node a `PodScheduled=False` znamenajú, že sme stále v scheduling boundary.

## Resource requests ako placement input

Scheduler nepoužíva aktuálnu memory usage aplikácie pri základnom fit rozhodnutí. Používa requests a Node allocatable minus už rezervované requests.

```yaml
resources:
  requests:
    cpu: 250m
    memory: 256Mi
```

Ak application reálne používa 1 GiB, ale requestuje 256 MiB, scheduler môže Node preplniť. Ak requestuje 4 GiB a používa 256 MiB, Pod môže zostať Pending napriek voľnej reálnej memory.

```bash
kubectl describe node <node-name>
```

Sekcia `Allocated resources` sumarizuje requests/limits podľa API objektov, nie presný runtime usage.

## Node labels a nodeSelector

Najjednoduchší hard placement:

```yaml
spec:
  nodeSelector:
    kubernetes.io/os: linux
    atlas.example/workload-class: general
```

Všetky labels musia sedieť. Labels, ktoré reprezentujú security alebo compliance boundary, musia byť chránené pred zmenou nedôveryhodným kubeletom alebo workloadom. Built-in NodeRestriction model chráni vybrané prefixy, no custom governance treba navrhnúť explicitne.

`nodeSelector` je presný a čitateľný, ale nevyjadruje preference alebo viac alternatív.

## Node affinity

Required affinity je hard filter:

```yaml
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: topology.kubernetes.io/zone
                operator: In
                values: [eu1-a, eu1-b, eu1-c]
```

Viac expressions v jednom term-e sa kombinuje ako AND. Viac terms sa kombinuje ako OR.

Preferred affinity pridáva score, ale Pod sa môže umiestniť aj inde:

```yaml
preferredDuringSchedulingIgnoredDuringExecution:
  - weight: 50
    preference:
      matchExpressions:
        - key: atlas.example/node-generation
          operator: In
          values: [v2]
```

`IgnoredDuringExecution` znamená, že neskoršia zmena labelu automaticky neevictuje už bežiaci Pod.

## Pod affinity a anti-affinity

Anti-affinity môže zabrániť colocation replík na rovnakom hoste:

```yaml
podAntiAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchLabels:
          app: payments-api
      topologyKey: kubernetes.io/hostname
```

Required anti-affinity zvyšuje availability, ale pri malom počte Nodes môže zablokovať rollout surge. Ak máme šesť replík a iba šesť eligible Nodes, nový siedmy surge Pod nemá kam ísť.

Preferred anti-affinity je pružnejšia, ale nepreukazuje, že repliky sú skutočne rozložené. Po rollout-e čítaj actual placement.

Pod affinity/anti-affinity môže byť výpočtovo náročná vo veľkých clustroch a závisí od konzistentných labels.

## Topology spread constraints

Topology spread vyjadruje rovnomernosť medzi domains:

```yaml
spec:
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels:
          app: payments-api
```

Scheduler porovnáva počet matching Podov v eligible domains podľa semantics constraintu. `maxSkew: 1` neznamená presne dve repliky v každej zone za každých okolností; výsledok závisí od eligible domains, existing Pods, node affinity a minDomains configuration.

`ScheduleAnyway` používa spread ako preference. `DoNotSchedule` je hard constraint.

## Taints a tolerations v scheduling flow

Node taint odpudzuje Pods, ktoré ho netolerujú. Toleration iba povoľuje scheduling; nepriťahuje Pod na daný Node.

```yaml
spec:
  tolerations:
    - key: dedicated
      operator: Equal
      value: payments
      effect: NoSchedule
```

Aby bol Node skutočne dedicated, toleration sa kombinuje s node affinity. Inak `payments-api` toleruje Node, ale scheduler ho môže umiestniť aj na bežný Node.

## Volume binding

PVC môže pridať topology constraints. Pri `WaitForFirstConsumer` scheduler koordinuje placement a provisioning. Pri existujúcom zonálnom PV musí Pod ísť do kompatibilnej zone.

```text
Pod constraints
+ PV node affinity
+ available Nodes
→ feasible set
```

Event `volume node affinity conflict` nie je runtime mount failure. Pod ešte nebol pridelený.

## Host ports a devices

Pod s `hostPort` rezervuje konkrétny port na Node-i:

```yaml
ports:
  - containerPort: 8080
    hostPort: 18080
```

Dva Pods s rovnakým hostPortom nemožno umiestniť na rovnaký Node podľa IP/port semantics. HostPort znižuje scheduling flexibilitu a typicky nie je potrebný pre Service-routed workload.

Extended resources, napríklad GPU, sú whole-number resources publikované Node pluginom. Scheduler ich zohľadní podľa requests, ale device initialization a health patria node runtime vrstve.

## Priority a preemption

PriorityClass ovplyvňuje queue order a môže umožniť preemption nižšie prioritných Podov.

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: production-critical
value: 100000
preemptionPolicy: PreemptLowerPriority
```

Vysoká priority nevytvára kapacitu. Môže odstrániť iné Pods a rozšíriť incident. Kritický workload potrebuje aj quota, requests, disruption a capacity planning.

Preemption candidate nemusí Pod okamžite schedulovať; victims potrebujú termination a ďalšie constraints môžu stále blokovať placement.

## Scheduler profiles a custom schedulers

Cluster môže mať viac scheduler profiles alebo samostatný custom scheduler. Pod vyberá scheduler cez `schedulerName`.

```yaml
spec:
  schedulerName: default-scheduler
```

Ak zadá neexistujúce meno, default scheduler Pod ignoruje a zostane Pending. Custom scheduler musí zapisovať binding a mať správne RBAC a HA.

## Framework plugins a status

Moderný scheduler používa framework extension points ako QueueSort, PreFilter, Filter, PostFilter, PreScore, Score, Reserve, Permit, PreBind a Bind. Konkrétna konfigurácia distribúcie môže meniť enabled plugins a weights.

Pri diagnostike sa neoplatí hádať iba podľa defaultov z dokumentácie. Zachovaj scheduler config generation a component logs/metrics.

## Events a unschedulable message

```bash
kubectl describe pod -n production <pod-name>
```

Typická správa:

```text
0/12 nodes are available: 3 Insufficient memory, 4 node(s) had untolerated taint, 5 node(s) didn't match Pod's node affinity.
```

Nie je to presné rozdelenie jednej disjunktnej množiny; dôvody sa môžu prekrývať podľa vyhodnotenia. Potrebujeme nájsť, či existuje aspoň jeden Node spĺňajúci všetky hard constraints.

## Scheduler neoveruje runtime success

Po bindingu môže Pod zlyhať na:

```text
image pull
CNI sandbox
volume attach/mount
local resource admission
device plugin
process startup
probe
```

Scheduler úspech je iba Node assignment. Ak `.spec.nodeName` existuje, presuň diagnostiku na worker-node vrstvu.

## Incident: rollout surge sa nedal schedulovať

Deployment mal šesť replík, required podAntiAffinity na hostname a presne šesť eligible Nodes. `maxSurge: 1` vytvoril siedmy Pod, no žiadny Node nemohol hostiť dve matching replicas.

Rollout zastal, hoci všetky old Pods boli zdravé. Oprava dočasne pridala siedmy Node a neskôr zmenila availability design: anti-affinity ostala required, no capacity gate zabezpečil surge headroom pred releaseom.

## Incident: pridané Nodes nepomohli

Stateful Pod s PVC v zone `eu1-a` bol Pending. Autoscaler pridal Nodes v `eu1-b`, pretože node group konfigurácia nepoznala volume topology požiadavku v očakávanom čase. Pod zostal unschedulable.

Root cause nebol celkový počet Nodes, ale nesprávna failure-domain kapacita. Oprava pridala zonálnu node group a zladila StorageClass `WaitForFirstConsumer`.

## Incident: vysoká priorita vyradila DNS

Tím dal všetkým production workloadom rovnakú extrémne vysokú PriorityClass. Pri memory pressure preemptovali platform DNS Pods s nižšou priority. Payments rollout síce získal Node, ale následne zlyhávala Service discovery v celom clustri.

Oprava vytvorila vrstvený priority model a rezervovala kapacitu pre critical add-ons. Priority sa prestala používať ako náhrada resource planningu.

## Model, ktorý si treba odniesť

Scheduler vyberá Node z množiny, ktorá spĺňa všetky hard constraints, a score-uje vhodných kandidátov. Requests, labels, taints, affinity, topology, volumes, host ports, devices a priority sa skladajú do jedného placement contractu. `PodScheduled=True` končí scheduler verdict; runtime úspech sa overuje na Node-e.

## Referencie

- [Kubernetes Scheduler](https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/)
- [Assigning Pods to Nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
- [Pod Topology Spread Constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/)
- [Pod Priority and Preemption](https://kubernetes.io/docs/concepts/scheduling-eviction/pod-priority-preemption/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Volumes, PV, PVC a StorageClass](volumes-pv-pvc-storageclass.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Requests, limits a QoS →](requests-limits-qos.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
