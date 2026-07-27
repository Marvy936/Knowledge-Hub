# Taints, tolerations, affinity a topology

Taints, tolerations, affinity a topology spread nie sú štyri názvy pre rovnaké placement pravidlo. Spolu vytvárajú contract medzi dôveryhodnou Node/topology inventory, Pod požiadavkami, existujúcou workload population a scheduler rozhodnutím. Taint odpudzuje, toleration iba odstraňuje časť odpudenia, affinity určuje attraction alebo hard eligibility a topology spread riadi distribúciu medzi domains.

Táto kapitola používa jeden dominantný lifecycle:

```text
availability, isolation a locality intent
→ trusted Node labels, taints a topology inventory
→ Pod placement generation a population selector
→ hard Node eligibility
→ taint/toleration verdict
→ affinity a topology-domain calculation
→ soft scoring a binding
→ runtime label/condition drift
→ rollout, failover a autoscaling verification
→ recovery a skorší control
```

## 1. Atlas Payments placement subject

Payments API 5.3.1 má šesť replík a potrebuje:

```text
iba trusted payments Node pool
minimálne dve zones, preferované tri
maximálne prijateľný zone skew 1
žiadne dve kritické replicas na rovnakom Node-e, ak je kapacita
kompatibilnú PVC/volume topology
rollout surge 2
```

Pri diagnostike fixuj:

```text
Deployment a Pod template generation
Pod UID a scheduler profile
nodeSelector/nodeAffinity/tolerations generation
topologySpreadConstraints a labelSelector
existujúcu old/new revision population
Node UID, labels, taints, conditions a allocatable
eligible topology domains a current counts
PVC/PV topology
FailedScheduling Events a binding outcome
```

Samotný názov Node poolu alebo cloud autoscaling groupy nie je Kubernetes placement evidence.

## 2. Placement sa skladá z hard eligibility a soft preference

Scheduler najprv vytvorí feasible set. Placement controls môžu Nodes odstrániť ešte pred scoringom:

```text
Node resource fit
∩ required node selector/affinity
∩ tolerated taints
∩ required Pod affinity/anti-affinity
∩ hard topology spread
∩ storage/device/port constraints
= feasible Nodes
```

Preferred affinity, `PreferNoSchedule` a soft spread až potom ovplyvňujú poradie feasible Nodes. Soft preference nevie vrátiť Node, ktorý vypadol na hard constraint.

## 3. Trusted Node a topology inventory

Node labels môžu reprezentovať OS, architecture, zone, region, instance class, compliance tier alebo dedicated pool. Security-sensitive labels musí vlastniť dôveryhodná platformová identita a ich taxonómia potrebuje schema a audit.

```text
Node label key/value
+ Node UID a pool generation
+ owner a mutation path
+ topology completeness
= trusted placement fact
```

Kompromitovaný alebo nesprávne oprávnený kubelet/workload nesmie vedieť označiť všeobecný Node ako PCI alebo payments pool a tým získať citlivý workload.

Chýbajúci `topology.kubernetes.io/zone` nevytvára „štvrtú prázdnu zónu“. Mení množinu Nodes/domains, ktoré scheduler vie pre konkrétny constraint hodnotiť.

## 4. Node selector a node affinity

### `nodeSelector`

Jednoduchý equality hard constraint:

```yaml
spec:
  nodeSelector:
    workload-tier: payments
    kubernetes.io/os: linux
```

Node musí spĺňať všetky položky.

### Required node affinity

Required affinity vyjadruje hard množinové pravidlá:

```yaml
requiredDuringSchedulingIgnoredDuringExecution:
  nodeSelectorTerms:
    - matchExpressions:
        - key: workload-tier
          operator: In
          values: [payments]
```

Expressions v jednom term-e tvoria AND; viac terms predstavuje alternatívy. Nesprávne OR/AND rozdelenie môže buď odstrániť všetky Nodes, alebo povoliť neželaný pool.

### Preferred node affinity

Preferred affinity pridáva score, ale negarantuje placement. Je vhodná pre cost, image locality alebo latency preferenciu, ktorú možno porušiť pri nedostatku kapacity.

`IgnoredDuringExecution` znamená, že neskoršia zmena labelu automaticky neevictne bežiaci Pod. Running Pod preto môže zostať na Node-e, ktorý už nespĺňa current placement intent; replacement bude hodnotený nanovo.

## 5. Taint je repulsion, toleration nie attraction

Node taint:

```text
dedicated=payments:NoSchedule
```

môže odpudiť nové Pody bez matching toleration. Toleration:

```yaml
tolerations:
  - key: dedicated
    operator: Equal
    value: payments
    effect: NoSchedule
```

iba dovolí Podu tento taint prejsť. Nevyžaduje, aby Pod skončil na dedicated Node-e.

Bezpečný dedicated-pool pattern kombinuje:

```text
taint na dedicated Nodes
+ matching toleration na určenom workloade
+ trusted label na dedicated Nodes
+ required node affinity na workloade
```

Taint drží ostatných vonku; required affinity drží určený workload vo vnútri.

### Effects

- `NoSchedule` blokuje nový placement bez toleration;
- `PreferNoSchedule` je soft repulsion;
- `NoExecute` môže ovplyvniť aj bežiace Pody.

Príliš široká `Exists` toleration bez úzkeho key/effect contractu môže povoliť pressure, control-plane alebo inak izolované Nodes.

## 6. Node-condition taints a failover čas

Control plane mapuje niektoré Node conditions na taints, napríklad `not-ready`, `unreachable`, `memory-pressure` alebo `disk-pressure`.

`tolerationSeconds` pri `NoExecute` je súčasťou failover policy:

```text
Node signal delay
→ NoExecute taint
→ toleration window
→ eviction/deletion
→ replacement scheduling
→ storage/network reattachment
→ application recovery
```

Príliš krátke okno mení transient partition na fleet churn. Príliš dlhé okno predlžuje outage a pri stateful writerovi môže blokovať bezpečný failover. Toleration sama nerieši fencing ani storage detach.

## 7. Pod affinity a anti-affinity používajú workload population

Pod affinity/anti-affinity nehodnotí iba incoming Pod. Potrebuje selector, namespace scope, matching existujúce Pody a topology key.

```text
incoming Pod
+ exact peer population selector
+ namespace population
+ topology key/value na Nodes
= affinity/anti-affinity verdict
```

Hard affinity môže vyžadovať blízkosť cache alebo data service, ale pri prvom Pode môže vytvoriť bootstrap deadlock. Hard anti-affinity znižuje correlated failure, ale môže zablokovať rollout alebo maintenance, ak počet eligible domains nestačí.

Namespace scope je súčasť identity population. Prázdny alebo príliš široký namespace selector môže počítať tenantov či stages, ktoré do placement contractu nepatria.

## 8. Topology spread riadi rozdiel počtov

Topology spread constraint opisuje povolený skew medzi eligible domains:

```yaml
spec:
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels:
          app: payments
```

Výpočet potrebuje:

```text
incoming Pod placement contract
→ eligible Nodes/domains
→ matching existing Pod population
→ count per domain
→ skew po hypotetickom placement-e
→ hard filter alebo score
```

`DoNotSchedule` je hard constraint. `ScheduleAnyway` ovplyvňuje scoring. `maxSkew` nemá význam bez správneho selectoru a kompletnej topology inventory.

Novšie API umožňuje jemnejšie určiť, ako sa pri výpočte eligible domains zohľadňuje node affinity a taints. Použitie musí byť viazané na podporovanú Kubernetes verziu a scheduler configuration.

## 9. Rollout mení population počas výpočtu

Počas Deployment rollout-u súčasne existujú old a new ReplicaSet Pody. Topology selector musí vedome určovať, či počíta:

- celú Service population;
- všetky revisions Deploymentu;
- iba release-specific cohortu;
- širší tenant alebo shard.

Ak selector zahŕňa staré aj nové Pody, surge musí mať kapacitu v požadovaných domains. Ak selector matchuje iba novú revision, nová cohorta sa môže zdať vyvážená, zatiaľ čo celkový traffic je koncentrovaný.

Placement acceptance preto nie je iba `Pod Scheduled=True`. Over distribution ready a serving endpointov počas aj po rolloute.

## 10. Worked failure: správny spread, neaktuálna Node identity

Pri rolloute Payments 5.3.1 vznikol stav:

```text
3 staré replicas Ready v zones A, B a C
→ Deployment vytvorí 2 surge Pody
→ jeden nový Pod sa bindne v A
→ druhý zostane Pending
→ dashboard ukazuje voľné Nodes v C
→ Event hlási node affinity mismatch a topology spread
```

Zone C node pool bol nahradený. Nové Nodes mali:

```text
taint: dedicated=payments:NoSchedule
label: workload-tier=payment
```

Pod mal správnu toleration, ale required affinity vyžadovala `workload-tier=payments`. Taint/toleration teda neboli root cause a topology spread nebol chybný; zone C nepatrila do feasible setu, pretože trusted label generation driftovala.

Oprava iba na jednom Pode cez `nodeName` by obišla scheduler a storage coordination. Odstránenie spread constraintu by presunulo replicas do A/B a znížilo failure-domain odolnosť.

## 11. Causal troubleshooting walkthrough

### Subject a state identity

Fixuj Deployment/Pod template generation, incoming Pod UID, scheduler profile, affinity/toleration/spread generation, exact existing Pod population, Node UID/labels/taints/conditions, PVC topology a Event timestamp.

### Competing hypotheses

1. required node affinity nematchuje;
2. Pod netoleruje Node taint;
3. topology key alebo domain label chýba;
4. spread selector počíta nesprávnu population;
5. hard anti-affinity nemá dostatok domains;
6. old a new rollout cohort zablokovali surge;
7. Node resources/host ports sú vyčerpané;
8. PVC node affinity vylučuje zones;
9. scheduler profile pridáva hidden affinity;
10. Node autoscaler template nevie vytvoriť matching Node;
11. bežiace Pody ostali po label drift-e, ale replacements už neprejdú;
12. `NoExecute` timing vytvára churn alebo pomalý failover.

### Discriminating observations

```bash
kubectl describe pod -n production <pending-pod>
kubectl get events -n production --sort-by=.metadata.creationTimestamp
kubectl get nodes -L workload-tier,topology.kubernetes.io/zone
kubectl describe node <node>
kubectl get pod -n production -l app=payments -o wide --show-labels
kubectl get pv,pvc -A
```

Zostroj maticu kandidátnych Nodes a pre každý zaznamenaj prvý hard filter reason. Samostatne vypočítaj matching population a counts per topology domain. Čítaj celý agregovaný `FailedScheduling` message; prvá fráza nemusí byť jedinou príčinou.

### Containment

Pozastav rollout alebo autoscaling, ak vytvára ďalšie Pending Pody a surge pressure. Nemeň taints, labels ani hard constraints ad hoc na jednotlivých Nodes bez ownera. Zachovaj Node pool generation, scheduler Events a Pod templates.

### Authoritative recovery

- oprav Node-pool template a trusted label owner;
- zosúlaď taint, toleration a required affinity ako jeden dedicated-pool contract;
- oprav population selector alebo topology key, ak nezodpovedá availability intentu;
- pridaj capacity/domains, ak contract je správny, ale fyzicky nesplniteľný;
- uprav rollout surge alebo soft/hard hranice iba po failure-domain analýze;
- oprav PVC topology alebo scheduler profile, ak je root cause mimo Node labelu;
- nechaj controller vytvoriť novú Pod generation a scheduler vykonať nový binding.

### Verify original a forbidden outcomes

Over:

1. všetky desired replicas sú schedulovateľné;
2. ready endpoint cohort má požadovaný zone a Node distribution;
3. payments workload neskončí na general alebo pressure pool-e;
4. neautorizovaný workload sa nedostane do dedicated poolu;
5. Node loss vytvorí replacement v prijateľnom failover čase;
6. rollout surge a HPA scale-up zostávajú možné;
7. PVC/data identity je dostupná na vybraných Nodes;
8. label drift alertuje skôr než replacement incident.

### Earlier controls

Použi admission-managed placement profiles, chránené Node labels, node-pool conformance test, policy test feasible-setu, rollout capacity simulation, topology inventory SLO, autoscaler template validation a periodický replacement game day.

## 12. Ďalšie failure boundaries

### Toleration bez required affinity

Payments Pod môže skončiť na general Node-e. Toleration nie je attraction ani isolation guarantee.

### `IgnoredDuringExecution` a label drift

Running Pod zostane, ale po reschedule už rovnaký placement nemusí byť možný. Audit musí porovnávať current Nodes aj current running placements.

### Hard anti-affinity zablokuje surge

Tri replicas na troch Nodes plus surge 1 s hard hostname anti-affinity vyžadujú štvrtý eligible Node. Bez neho rollout stojí, aj keď každá súčasná replika je zdravá.

### Spread selector nematchuje vlastné Pody

Counts sú prázdne alebo neúplné a scheduler vytvorí iluzórne vyváženie. Selector musí byť testovaný proti resolved Pod labels.

### `NoExecute` bez fencing analýzy

Rýchly replacement môže pri stateful workloade vytvoriť druhého writera, ak starý Node iba stratil control-plane connectivity.

### Autoscaler nevie opraviť logický constraint

Nové Nodes nepomôžu, ak node-group template nemá required label/taint, požadovaná zone neexistuje alebo affinity population nemôže vzniknúť.

## 13. Referenčný katalóg

### Mechanizmy

| Mechanizmus | Hlavná otázka | Hard/soft |
|---|---|---|
| `nodeSelector` | Ktoré Nodes sú vôbec dovolené? | hard |
| required node affinity | Aká množina Node labels je povinná? | hard |
| preferred node affinity | Ktoré feasible Nodes preferujeme? | soft |
| taint + toleration | Ktoré Pody Node odpudzuje? | hard alebo soft podľa effectu |
| Pod affinity | Pri akej workload population má Pod byť? | hard/soft |
| Pod anti-affinity | Od akej population má byť oddelený? | hard/soft |
| topology spread | Aký count skew medzi domains je prijateľný? | hard/soft |

### Taint effects

- `NoSchedule`;
- `PreferNoSchedule`;
- `NoExecute` s voliteľným toleration time contractom.

### Topology evidence

- Node UID a label generation;
- topology key completeness;
- exact eligible domains;
- matching Pod population;
- count a skew per domain;
- old/new revision a serving endpoint distribution.

## 14. Anti-patterny

- toleration považovaná za attraction;
- nekontrolované security-sensitive Node labels;
- hard anti-affinity pre každú repliku bez surge capacity;
- spread selector, ktorý nematchuje workload;
- všetky preferences premenené na hard constraints;
- `nodeName` ako oprava placement incidentu;
- plošná toleration pressure/control-plane taintov;
- topology contract bez overenia node-autoscaler templates;
- availability posudzovaná iba podľa Scheduled Podov, nie ready serving cohorty.

## 15. Kontrolné otázky

1. Prečo toleration negarantuje placement na tainted Node?
2. Ako taint a required affinity spolu vytvoria dedicated-pool boundary?
3. Ktoré placement pravidlá filtrujú a ktoré iba skórujú?
4. Čo presne znamená `IgnoredDuringExecution` pri label drift-e?
5. Aké subjects tvoria Pod affinity population?
6. Ako sa vypočíta topology skew pre incoming Pod?
7. Prečo rollout surge mení topology feasibility?
8. Ako odlíšiš spread failure od Node-label identity driftu?
9. Prečo Node autoscaler nevyrieši logicky nemožný contract?
10. Ako overíš forbidden outcome, že workload neunikol mimo dedicated poolu?

## Glossary impact

Relevantné pojmy: placement generation, trusted Node label, Node-label generation, hard eligibility set, taint-repulsion verdict, toleration scope, dedicated-pool contract, affinity population subject, topology-domain inventory, topology-skew subject, rollout placement population, placement drift, replacement feasibility, NoExecute failover contract, subject-bound placement acceptance a forbidden-pool verification.

## Oficiálna dokumentácia

- [Taints and Tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)
- [Assigning Pods to Nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
- [Pod Topology Spread Constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/)
- [Scheduler Configuration](https://kubernetes.io/docs/reference/scheduling/config/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Probes](probes.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: HPA a autoscaling →](hpa-autoscaling.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
