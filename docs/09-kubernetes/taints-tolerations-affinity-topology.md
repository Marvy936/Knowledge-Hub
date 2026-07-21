# Taints, tolerations, affinity a topology

Kubernetes scheduler nerozhoduje iba podľa voľného CPU a memory. Placement ovplyvňujú labels, node affinity, Pod affinity/anti-affinity, taints/tolerations a topology spread constraints. Tieto mechanizmy riešia odlišné otázky: **kam Pod smie ísť, kam preferuje ísť, od ktorých Nodes má byť odpudzovaný a ako sa majú repliky rozložiť medzi failure domains**.

## 1. Základný mentálny model

Pri placement-e rozlišuj:

- hard constraints — Node musí podmienku spĺňať,
- soft preferences — scheduler zvýhodní Node, ale môže zvoliť iný,
- repulsion — taint odrádza alebo vylučuje Pody bez toleration,
- attraction — affinity priťahuje Pod k Node-u alebo iným Podom,
- spreading — topology constraints obmedzujú nerovnomerné rozloženie replík.

Žiadny z týchto mechanizmov sám osebe negarantuje application availability. Potrebuješ dostatočný počet Nodes, správne labels, kapacitu, storage topology a workload replicas.

## 2. Node labels

Node labels opisujú vlastnosti alebo administratívnu klasifikáciu Node-u:

```bash
kubectl label node worker-1 workload-tier=payments
kubectl label node worker-1 topology.kubernetes.io/zone=eu-central-1a
```

Labels môžu reprezentovať:

- zone alebo region,
- architecture a operating system,
- instance class,
- GPU/device pool,
- compliance alebo isolation tier,
- dedicated workload pool.

Bezpečnostne citlivé placement labels musí kontrolovať dôveryhodná platformová identita. Workload nemá byť schopný sám označiť Node tak, aby získal prístup k izolovanému poolu.

## 3. `nodeSelector`

Najjednoduchší hard placement constraint:

```yaml
spec:
  nodeSelector:
    workload-tier: payments
    kubernetes.io/os: linux
```

Node musí mať všetky uvedené labels. `nodeSelector` je vhodný pre jednoduché equality pravidlá, ale nevie vyjadriť zložitejšie množiny alebo soft preferences.

## 4. Node affinity

Node affinity poskytuje expresívnejší model.

### Required počas scheduling-u

```yaml
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: workload-tier
                operator: In
                values: [payments]
```

Pod sa naplánuje iba na matching Node.

### Preferred počas scheduling-u

```yaml
spec:
  affinity:
    nodeAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          preference:
            matchExpressions:
              - key: topology.kubernetes.io/zone
                operator: In
                values: [eu-central-1a]
```

Scheduler preferenciu zahrnie do scoring-u, ale môže zvoliť iný feasible Node.

`IgnoredDuringExecution` znamená, že neskoršia zmena Node labelu automaticky neevictne už bežiaci Pod.

## 5. Node affinity operátory

Bežné operátory:

- `In`,
- `NotIn`,
- `Exists`,
- `DoesNotExist`,
- `Gt`,
- `Lt`.

Viac expressions v jednom term-e sa vyhodnocuje ako AND. Viac `nodeSelectorTerms` sa typicky vyhodnocuje ako OR.

Negatívne pravidlá používaj opatrne. `NotIn` nad neúplne riadenou label taxonómiou môže povoliť nečakané Nodes.

## 6. Taints

Taint sa aplikuje na Node:

```bash
kubectl taint nodes worker-1 dedicated=payments:NoSchedule
```

Tvar:

```text
key=value:effect
```

Podstatné effects:

- `NoSchedule` — nový Pod bez matching toleration sa nenaplánuje,
- `PreferNoSchedule` — scheduler sa mu pokúsi vyhnúť,
- `NoExecute` — ovplyvňuje nové aj už bežiace Pody; bez toleration môžu byť evictnuté.

Taint **nepriťahuje** workload. Iba odpudzuje Pody, ktoré ho netolerujú.

## 7. Tolerations

```yaml
spec:
  tolerations:
    - key: dedicated
      operator: Equal
      value: payments
      effect: NoSchedule
```

Toleration umožní Podu prejsť cez konkrétny taint, ale negarantuje placement na taký Node.

Pre dedicated Node pool typicky potrebuješ kombináciu:

- taint, aby iné workloads neprišli dovnútra,
- label a required node affinity, aby určený workload neodišiel mimo poolu.

## 8. Toleration operators

### `Equal`

Matching key, value a effect podľa deklarácie.

### `Exists`

```yaml
- key: dedicated
  operator: Exists
  effect: NoSchedule
```

Toleruje ľubovoľnú value daného key.

Príliš široké tolerations, najmä bez key alebo effect, môžu workloadu umožniť scheduling na pressure, control-plane alebo inak izolované Nodes.

## 9. `NoExecute` a `tolerationSeconds`

```yaml
spec:
  tolerations:
    - key: node.kubernetes.io/not-ready
      operator: Exists
      effect: NoExecute
      tolerationSeconds: 300
```

Pod môže zostať na Node-e po aplikovaní taintu počas definovaného času. Použitie ovplyvňuje failover latency:

- krátke okno zrýchli replacement, ale môže reagovať na krátky network glitch,
- dlhé okno znižuje churn, ale predĺži nedostupnosť pri skutočnom Node failure.

Controller replacement a storage attach/detach majú vlastné ďalšie časové hranice.

## 10. Node-condition taints

Control plane môže mapovať Node conditions na taints, napríklad:

- `node.kubernetes.io/not-ready`,
- `node.kubernetes.io/unreachable`,
- `node.kubernetes.io/memory-pressure`,
- `node.kubernetes.io/disk-pressure`,
- `node.kubernetes.io/pid-pressure`,
- `node.kubernetes.io/network-unavailable`.

Tolerovať pressure taint neznamená, že Node má dostatok resources alebo že workload bude zdravý. Systémové DaemonSety ich niekedy tolerujú zámerne, application workloads spravidla nie plošne.

## 11. Pod affinity

Pod affinity umiestňuje Pod blízko matching Podov.

```yaml
spec:
  affinity:
    podAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchLabels:
              app: cache
          topologyKey: topology.kubernetes.io/zone
```

Význam: Pod musí ísť do topology domain, v ktorej už existuje matching Pod.

Použitie:

- latency-sensitive spoluumiestnenie,
- locality k cache alebo data service,
- zoskupenie súvisiacich workloadov.

Riziko: hard affinity môže vytvoriť deadlock pri prvom Pode alebo znížiť počet feasible Nodes.

## 12. Pod anti-affinity

Anti-affinity oddeľuje matching Pody.

```yaml
spec:
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
        - weight: 100
          podAffinityTerm:
            labelSelector:
              matchLabels:
                app: web
            topologyKey: kubernetes.io/hostname
```

Použitie:

- rozloženie replík medzi Nodes,
- oddelenie tenantov alebo noisy workloads,
- zníženie correlated failure.

Hard anti-affinity na malom alebo nevyváženom clustri môže spôsobiť Pending Pody počas rollout-u alebo Node maintenance.

## 13. Namespace scope pri Pod affinity

Pod affinity term môže vyberať Pody:

- v rovnakom namespace,
- v explicitných namespaces,
- cez namespace selector podľa podporovaného API modelu.

Prázdny alebo nesprávny namespace scope je častý dôvod, prečo pravidlo matchuje inú population, než autor očakáva.

## 14. Topology key

`topologyKey` označuje Node label, ktorého hodnoty tvoria domains.

Príklady:

- `kubernetes.io/hostname` — Node domain,
- `topology.kubernetes.io/zone` — availability zone,
- `topology.kubernetes.io/region` — region,
- vlastný rack alebo failure-domain label.

Ak Nodes label nemajú alebo label taxonómia nie je konzistentná, scheduling pravidlo môže zlyhať alebo vytvoriť falošné rozloženie.

## 15. Topology spread constraints

Topology spread constraints deklarujú prípustnú nerovnomernosť replikácie.

```yaml
spec:
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels:
          app: web
```

Kľúčové polia:

- `maxSkew` — maximálny tolerovaný rozdiel medzi domains podľa pravidiel,
- `topologyKey` — definícia domain,
- `whenUnsatisfiable` — hard `DoNotSchedule` alebo soft `ScheduleAnyway`,
- `labelSelector` — population, ktorej rozloženie sa počíta,
- `minDomains` a ďalšie fields podľa podporovanej verzie.

## 16. Spread na viacerých úrovniach

Bežný model:

```yaml
spec:
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels:
          app: web
    - maxSkew: 1
      topologyKey: kubernetes.io/hostname
      whenUnsatisfiable: ScheduleAnyway
      labelSelector:
        matchLabels:
          app: web
```

Takýto workload vyžaduje zone-level distribution a preferuje Node-level distribution. Hard pravidlá navrhuj podľa minimálneho počtu replík, zones a rollout surge capacity.

## 17. Affinity vs. topology spread

Pod anti-affinity hovorí najmä „nedávaj matching Pody do rovnakej domain“.

Topology spread hovorí „udrž rozdiel počtu matching Podov medzi domains pod kontrolou“.

Pre väčšie replica sets je topology spread často čitateľnejší a flexibilnejší než séria hard anti-affinity pravidiel.

## 18. Interakcia s rolloutom

Počas Deployment rollout-u existujú staré aj nové Pody. Placement selector musí zámerne určiť, či sa spread počíta:

- cez všetky revisions workloadu,
- iba cez konkrétnu release population,
- cez širšiu service population.

Príliš striktné pravidlá môžu zablokovať `maxSurge` Pod. Príliš úzke labels zas umožnia všetkým novým Podom skončiť v jednej zone.

## 19. Interakcia s autoscalingom

HPA môže zvýšiť replicas, ale scheduler ich musí vedieť umiestniť. Node autoscaler môže pridať Nodes iba ak:

- Pod constraints zodpovedajú existujúcemu node-group template-u,
- požadovaná zone alebo instance class je provisionovateľná,
- taints/labels a storage topology sú kompatibilné,
- quota a cloud limity to umožnia.

Autoscaler nevyrieši logicky nemožnú affinity alebo chýbajúci topology domain.

## 20. Interakcia so storage

PVC s topology-bound volume môže obmedziť Pod na konkrétnu zone alebo Node. Scheduler musí súčasne splniť:

- node affinity workloadu,
- taints/tolerations,
- Pod affinity/spread,
- PV node affinity a attach model.

Konflikt často končí ako `FailedScheduling`, nie ako storage chyba až po starte.

## 21. Bezpečný dedicated-node pattern

```yaml
spec:
  tolerations:
    - key: dedicated
      operator: Equal
      value: payments
      effect: NoSchedule
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: dedicated
                operator: In
                values: [payments]
```

Node zároveň nesie:

```text
taint: dedicated=payments:NoSchedule
label: dedicated=payments
```

Pre silnejšiu isolation stále potrebuješ RBAC, Pod Security, network policy, runtime isolation a dôveryhodnú správu Node labels.

## 22. Diagnostika

```bash
kubectl describe pod -n production <pod>
kubectl get events -n production --sort-by=.metadata.creationTimestamp
kubectl get nodes --show-labels
kubectl describe node <node>
kubectl get pod -n production -o wide
```

Pri `FailedScheduling` rozdeľ príčiny:

1. hard node selector/affinity,
2. untolerated taint,
3. Pod affinity/anti-affinity,
4. topology spread,
5. resource alebo host-port nedostatok,
6. PVC/storage topology,
7. quota/admission,
8. scheduler profile alebo plugin.

Event správa môže agregovať viac dôvodov naraz.

## 23. Anti-patterny

### Toleration považovaná za attraction

Pod môže skončiť na ľubovoľnom inom feasible Node-e.

### Hard anti-affinity pre každú repliku

Malý cluster alebo rollout surge sa zablokuje.

### Nekontrolované custom Node labels

Workload môže obísť isolation boundary.

### `NoExecute` bez premysleného failover času

Krátky transient Node problém spôsobí masový churn.

### Topology spread selector, ktorý nematchuje workload

Scheduler počíta inú alebo prázdnu population a ochrana je iluzórna.

### Povinná zone, ktorú node autoscaler nevie vytvoriť

Pod zostane Pending bez možnosti automatickej nápravy.

### Všetko ako hard constraint

Scheduler stratí flexibilitu a cluster capacity zostane nevyužitá.

## 24. Kontrolné otázky

1. Aký je rozdiel medzi taintom a toleration?
2. Prečo toleration negarantuje placement na tainted Node?
3. Ako sa líši `nodeSelector` od node affinity?
4. Čo znamená `IgnoredDuringExecution`?
5. Kedy použiť Pod affinity a kedy anti-affinity?
6. Čo tvorí topology domain?
7. Ako sa líši anti-affinity a topology spread constraint?
8. Prečo hard spread pravidlo môže zablokovať rollout?
9. Ako storage topology ovplyvňuje scheduling?
10. Ako navrhneš dedicated Node pool bez úniku workloadu mimo poolu?

## Glossary impact

Relevantné pojmy: Node label, `nodeSelector`, node affinity, Pod affinity, Pod anti-affinity, taint, toleration, `NoSchedule`, `PreferNoSchedule`, `NoExecute`, `tolerationSeconds`, topology domain, topology spread constraint, `maxSkew`, `DoNotSchedule`, `ScheduleAnyway`, dedicated Node pool a placement deadlock.

## Oficiálna dokumentácia

- [Taints and Tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)
- [Assigning Pods to Nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
- [Pod Topology Spread Constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/)
