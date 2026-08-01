# Taints, tolerations, affinity a topology

Kubernetes placement sa neskladá z jedného „kam Pod patrí“ field-u. Taints odpudzujú Pods, tolerations povoľujú výnimku, node affinity vyberá vlastnosti Node-u, Pod affinity/anti-affinity pracuje s inými workloadmi a topology spread riadi rozloženie medzi failure domains. Tieto mechanizmy sa vyhodnocujú spolu so resource requests, volumes a ďalšími scheduler constraints.

Pri `payments-api` chceme šesť replík rozložiť cez zones, zabrániť colocation dvoch replík na rovnakom hoste a povoliť ich iba na general-purpose production Nodes. Zároveň potrebujeme surge počas rollout-u. Príliš veľa hard pravidiel môže vytvoriť „bezpečný“ manifest, ktorý sa nedá schedulovať.

## Taint na Node-i

```bash
kubectl taint nodes worker-eu1-a-17 dedicated=payments:NoSchedule
```

Taint má key, optional value a effect. `NoSchedule` blokuje nové Pods bez toleration. `PreferNoSchedule` je mäkká preferencia. `NoExecute` ovplyvňuje aj už bežiace Pods bez toleration a môže spustiť eviction.

Taint neznamená, že Node je vyhradený iba pre payments workload. Pods s toleration ho môžu použiť, ale bez ďalšieho node affinity môžu payments Pods stále ísť aj na bežné Nodes.

## Toleration v Pode

```yaml
spec:
  tolerations:
    - key: dedicated
      operator: Equal
      value: payments
      effect: NoSchedule
```

Toleration je povolenie zniesť taint, nie príkaz vybrať Node. Dedicated placement sa typicky skladá:

```text
Node taint dedicated=payments:NoSchedule
+ payments Pod toleration
+ payments Pod required node affinity na dedicated=payments
```

Ostatné Pods taint netolerujú a payments Pods sú affinity pravidlom priťahované na správnu skupinu.

## `NoExecute` a `tolerationSeconds`

```yaml
spec:
  tolerations:
    - key: node.kubernetes.io/not-ready
      operator: Exists
      effect: NoExecute
      tolerationSeconds: 300
```

Pod môže dočasne tolerovať Node NotReady stav. Po uplynutí času môže byť evictovaný podľa controller semantics.

Dlhá tolerácia znižuje zbytočné replacementy pri krátkom výpadku, ale predlžuje čas, počas ktorého controller považuje repliku za viazanú na nedostupný Node. Pri stateful writerovi môže byť potrebný fencing pred novou inštanciou.

## Node affinity

Required node affinity je hard scheduling filter:

```yaml
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: atlas.example/workload-class
                operator: In
                values: [general-production]
```

Preferred affinity ovplyvňuje score:

```yaml
preferredDuringSchedulingIgnoredDuringExecution:
  - weight: 80
    preference:
      matchExpressions:
        - key: atlas.example/node-generation
          operator: In
          values: [v2]
```

`IgnoredDuringExecution` znamená, že zmena labelu po scheduling-u Pod automaticky nepresunie. Na enforcement po zmene Node state-u treba iný controller alebo replacement workflow.

Node labels používané ako security boundary musia byť chránené. Nedôveryhodný kubelet nesmie vedieť sám pridať label, ktorý ho zaradí do PCI alebo trusted workload poolu.

## Pod anti-affinity

Required anti-affinity na hostname:

```yaml
podAntiAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    - labelSelector:
        matchLabels:
          app: payments-api
      topologyKey: kubernetes.io/hostname
```

Tým zabránime dvom matching Pods na jednom Node-e. Dostupnosť sa zlepší pri Node failure, ale rollout surge potrebuje extra eligible Node. Pri presne šiestich Nodes a šiestich replikách siedmy Pod nemá placement.

Preferred anti-affinity:

```yaml
preferredDuringSchedulingIgnoredDuringExecution:
  - weight: 100
    podAffinityTerm:
      labelSelector:
        matchLabels:
          app: payments-api
      topologyKey: kubernetes.io/hostname
```

Scheduler sa snaží repliky rozložiť, ale pri nedostatku kapacity môže colocate-nuť. Po rollout-e treba overiť actual distribution.

## Pod affinity

Pod affinity môže priblížiť workload k cache alebo helper službe:

```yaml
podAffinity:
  preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 50
      podAffinityTerm:
        labelSelector:
          matchLabels:
            app: risk-cache
        topologyKey: topology.kubernetes.io/zone
```

Silné required coupling na inú dynamickú službu môže vytvoriť deadlock. Ak cache Pods dočasne neexistujú v novej zone, payments Pods sa tam nikdy neschedulujú, hoci aplikácia by vedela fungovať cez network.

Affinity má vyjadrovať skutočný locality alebo failure-domain benefit, nie náhodnú historickú colocation.

## Topology spread

```yaml
spec:
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels:
          app: payments-api
    - maxSkew: 1
      topologyKey: kubernetes.io/hostname
      whenUnsatisfiable: ScheduleAnyway
      labelSelector:
        matchLabels:
          app: payments-api
```

Prvý constraint tvrdo drží zonálny skew. Druhý preferuje host spread, ale nezablokuje scheduling.

Topology labels musia byť konzistentné na všetkých eligible Nodes. Node bez zone labelu môže byť z výpočtu vylúčený alebo spôsobiť prekvapenie podľa constraint semantics.

## `maxSkew`, eligible domains a `minDomains`

`maxSkew` porovnáva počty matching Podov v relevantných domains. Výsledok závisí od node affinity, taints a ďalších eligibility pravidiel. Ak je dostupná iba jedna zone, `maxSkew: 1` nevytvorí multi-zone HA.

`minDomains` podľa podporovanej API verzie môže vyjadriť minimálny počet eligible domains, ktorý očakávame. Aj tak však potrebujeme reálnu Node kapacitu a health v týchto zones.

## `matchLabelKeys` a rollout isolation

Novšie Kubernetes semantics môžu umožniť, aby topology/affinity pracovala s vybranými label keys z incoming Podu, napríklad template hash. To pomáha odlíšiť revisions počas rollout-u. Pri použití treba overiť cieľovú verziu a admission behavior.

Bez revision-aware selectoru môže stará a nová Deployment revision ovplyvňovať spread count spôsobom, ktorý zablokuje surge alebo vytvorí nečakanú colocation.

## Node maintenance taints

Cordon nastaví Node unschedulable, ale nepridáva automaticky všeobecný custom taint ani neevictuje Pods:

```bash
kubectl cordon worker-eu1-a-17
```

Drain pridáva eviction workflow:

```bash
kubectl drain worker-eu1-a-17 \
  --ignore-daemonsets \
  --delete-emptydir-data=false
```

Drain rešpektuje PDB podľa flags a API behavior. Taints, cordon a drain majú odlišný účel. Ručný `NoExecute` taint počas maintenance môže evictovať workloads inak než plánovaný drain.

## Built-in Node conditions a taints

Node lifecycle controller používa taints spojené s NotReady, Unreachable, memory/disk/PID pressure alebo unschedulable state podľa Kubernetes modelu. Pods môžu mať default tolerations pre krátke NotReady/Unreachable obdobie.

Pri Node partitione API Pod status môže byť stale. Toleration expiry a controller replacement nepreukazujú, že starý process prestal vykonávať external side effects.

## Placement overenie

Po apply čítaj actual placement:

```bash
kubectl get pods -n production -l app=payments-api \
  -o custom-columns='POD:.metadata.name,NODE:.spec.nodeName,ZONE:.metadata.labels.topology\.kubernetes\.io/zone,HASH:.metadata.labels.pod-template-hash'
```

Pod metadata bežne neobsahujú Node zone label automaticky. Na spoľahlivý report treba spojiť Pod `.spec.nodeName` s Node labels, napríklad cez `kubectl get nodes` alebo skript.

Over:

```text
počet replík na Node
počet replík v zone
old/new revision distribution
eligible Nodes bez Podu
Pods na neočakávaných Nodes
```

## Incident: hard anti-affinity zablokovala opravu incidentu

Jeden Node zlyhal a controller vytvoril replacement Pod. Cluster mal voľnú CPU a memory na ostatných Nodes, ale required anti-affinity povoľovala iba jednu repliku na hoste a všetky ostatné hosty už jednu mali. Replacement zostal Pending.

Availability design vyžadoval sedem eligible Nodes pre šesť replík a one-Node failure, no cluster mal iba šesť. Oprava pridala capacity. Skorší control je failure-scenario capacity model, nie iba validný YAML.

## Incident: toleration otvorila workload na infra Nodes

`payments-api` dostala broad toleration `operator: Exists`, aby prešla dočasným taintom. Tým začala tolerovať aj control-plane a storage-dedicated taints. Bez node affinity scheduler umiestnil jednu repliku na infra Node s odlišnou network policy.

Oprava nahradila broad toleration konkrétnym key/value/effect a pridala required node affinity. Admission policy zakázala wildcard tolerations pre application namespaces.

## Incident: topology spread bola zelená, ale všetky Pods boli v jednej zone

Constraint používal `ScheduleAnyway` a cluster mal iba jednu zone s voľnou kapacitou. Scheduler všetky Pods umiestnil tam a manifest bol platný. Tím mylne považoval samotnú existenciu spread constraintu za HA proof.

Oprava pridala hard zonálny availability requirement tam, kde business SLO vyžadovalo multi-zone, a pre-release gate overil actual zone inventory a placement.

## Model, ktorý si treba odniesť

Taints/tolerations riadia odpudzovanie a výnimky. Node affinity vyberá Node vlastnosti. Pod affinity/anti-affinity pracuje s workloadmi a topology spread riadi rovnomernosť. Všetky sa skladajú do jedného scheduling contractu. Bez dostatočnej kapacity a správnych labels môže bezpečnostné alebo HA pravidlo zablokovať rollout alebo recovery. Vždy over actual placement, nie iba deklaráciu.

## Referencie

- [Taints and Tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)
- [Assigning Pods to Nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
- [Pod Topology Spread Constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/)
- [Safely Drain a Node](https://kubernetes.io/docs/tasks/administer-cluster/safely-drain-node/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Probes](probes.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: HPA a autoscaling →](hpa-autoscaling.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
