# StatefulSet

StatefulSet je Kubernetes workload controller pre repliky, ktorých identita, dáta alebo poradie nie sú vzájomne zameniteľné. Jeho úloha nie je „spustiť databázu“, ale udržiavať stabilné **ordinal slots** a riadiť ich Pod, network a storage lifecycle.

StatefulSet sám neposkytuje replikáciu dát, quorum, leader election, fencing, backup ani application-consistent failover. Tieto mechanizmy musí poskytovať aplikácia, operator alebo externá storage/platformová vrstva.

Dominantný lifecycle:

```text
stateful workload intent a membership contract
→ StatefulSet UID, generation a revision
→ stabilný ordinal slot
→ per-ordinal DNS a storage identity
→ ordered alebo parallel Pod realization
→ application membership, role a fencing
→ readiness a client-serving eligibility
→ scale, update alebo replacement
→ backup, restore a decommission
→ data-retention a cleanup verdict
```

Kľúčová diagnostická otázka nie je „koľko Podov beží?“, ale:

```text
Ktorý ordinal, Pod UID, PVC/PV a application member predstavujú jednu repliku?
Aká data, membership a fencing epoch je autoritatívna?
Je replika iba Running, alebo je synchronized a bezpečne client-serving?
```

## 1. Atlas scenár

Atlas prevádzkuje trojčlenný ledger cluster:

```text
StatefulSet: production/ledger-db
StatefulSet generation: 18
application release: 15.4.2
replicas: 3
ordinals: ledger-db-0, ledger-db-1, ledger-db-2
headless Service: ledger-db
PVCs: data-ledger-db-0 .. data-ledger-db-2
application members: member-0 .. member-2
expected leader term: T884
configuration generation: C52
credential epoch: SE08
```

Acceptance contract:

- každý ordinal používa svoj canonical PVC a backend volume;
- existuje presne jeden aktívny leader pre term `T884` alebo novší;
- aspoň dve synchronized replicas tvoria quorum;
- readiness povoľuje client traffic iba client-serving memberom;
- žiadny starý process alebo volume clone nesmie zapisovať bez platnej fencing epoch;
- backup a restore patria k explicitnej data generation;
- payment ledger append sa po recovery vykoná presne raz.

## 2. StatefulSet subject

Pre bezpečný rollout alebo incident zaznamenaj:

```text
cluster a namespace
StatefulSet name, UID, generation a resourceVersion
currentRevision a updateRevision
replica count, podManagementPolicy a updateStrategy
serviceName a headless Service UID/generation
ordinal range a start ordinal, ak sa používa
Pod names, UIDs, revisions, Nodes a IPs
PVC UIDs, PV names, backend volume IDs a retention policy
application member IDs, roles, terms a replication positions
backup/restore lineage a data generation
configuration, secret a image digests
authoritative writer a fencing epoch
```

Meno `ledger-db-1` je stabilný logical slot. Nie je to lifetime identity processu. Replacement má rovnaké meno a ordinal, ale nový Pod UID, IP, sandbox a process generation.

## 3. Ordinal slot

Pri troch replikách vznikajú sloty:

```text
ordinal 0 → ledger-db-0
ordinal 1 → ledger-db-1
ordinal 2 → ledger-db-2
```

StatefulSet garantuje predvídateľné pomenovanie a väzbu lifecycle-u na ordinal. Aplikácia môže ordinal použiť ako vstup do membership konfigurácie, ale ordinal nie je bezpečný fencing token.

Starý process `ledger-db-1` môže počas network partition pokračovať, zatiaľ čo control plane vytvorí replacement `ledger-db-1` inde. Bez application lease, term alebo storage fencing mechanizmu môžu oba procesy považovať rovnaký logical slot za aktívny.

## 4. Network identity a headless Service

StatefulSet používa `.spec.serviceName`, typicky odkaz na headless Service:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ledger-db
  namespace: production
spec:
  clusterIP: None
  selector:
    app: ledger-db
  ports:
    - name: peer
      port: 7000
    - name: client
      port: 7432
```

Canonical peer meno môže byť:

```text
ledger-db-1.ledger-db.production.svc.cluster.local
```

DNS poskytuje discovery, nie membership correctness. Rozlišuj:

- DNS record generation;
- Pod UID a IP za menom;
- application member ID;
- readiness/publication policy;
- client alebo peer DNS cache;
- negative caching po skorom lookup-e;
- staré spojenie na replacement predchádzajúcu IP.

Peer protocol musí overovať member identity a epoch, nie iba úspešné DNS resolution.

## 5. Per-ordinal storage identity

`volumeClaimTemplates` vytvára claim pre každý ordinal:

```yaml
spec:
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: fast-regional
        resources:
          requests:
            storage: 200Gi
```

Výsledok:

```text
ordinal 0 → PVC data-ledger-db-0 → PV pv-a17 → volume vol-a17
ordinal 1 → PVC data-ledger-db-1 → PV pv-b24 → volume vol-b24
ordinal 2 → PVC data-ledger-db-2 → PV pv-c31 → volume vol-c31
```

Replacement ordinalu sa má pripojiť k rovnakému canonical claimu. To však nepreukazuje:

- že volume obsahuje správnu data generation;
- že filesystem je konzistentný;
- že starý Node je bezpečne odpojený a fenced;
- že restore nepochádza zo staršieho alebo cudzieho clusteru;
- že application member metadata sú kompatibilné;
- že volume je synchronized s quorum.

PVC `Bound` je storage-control-plane evidence. Nie je to application data acceptance verdict.

## 6. Identity chain jednej repliky

Pre ordinal `1` musí byť rekonštruovateľný chain:

```text
StatefulSet UID/generation
→ ControllerRevision
→ ordinal 1
→ Pod UID
→ Node UID
→ PVC UID
→ PV a backend volume ID
→ filesystem/data generation
→ application member ID
→ membership term a fencing epoch
→ readiness/client-serving verdict
```

Ak ktorákoľvek väzba patrí inej generation, stabilné meno môže zakryť nesprávny state.

## 7. Ordered a parallel realization

### `OrderedReady`

Controller typicky:

```text
vytvorí ordinal 0
→ čaká na Ready
→ vytvorí ordinal 1
→ čaká na Ready
→ vytvorí ordinal 2
```

Pri scale-down alebo rolling update používa opačné ordinal poradie podľa príslušnej transition semantics.

Ordering je užitočný iba vtedy, keď readiness reprezentuje potrebný bootstrap invariant. Plytká TCP readiness môže povoliť ďalší ordinal pred synchronizáciou. Príliš široká readiness závislá od celého clusteru môže vytvoriť deadlock.

### `Parallel`

`Parallel` odstráni controller-level čakanie medzi ordinalmi. Neodstraňuje application-level ordering, membership alebo data-safety požiadavky.

Použi ho iba vtedy, keď každá replika dokáže bezpečne bootstrapovať a ukončiť sa nezávisle.

## 8. Application membership a quorum

Kubernetes vidí Pods, conditions a storage objects. Nevidí automaticky:

- leader/follower alebo primary/replica role;
- committed log index;
- replication lag;
- quorum membership;
- fencing term;
- safe decommission;
- on-disk format compatibility.

Pre trojčlenný consensus cluster:

```text
3 Running Pods
≠ 3 synchronized members
≠ quorum
≠ jeden bezpečný leader
≠ client-serving cluster
```

Readiness a Service routing musia byť odvodené z application role a synchronization contractu. Peer discovery endpoint a client-serving endpoint môžu potrebovať odlišné publication pravidlá.

## 9. Update revisions

Relevantná zmena Pod template-u vytvára novú revision. Sleduj:

```text
StatefulSet generation
currentRevision
updateRevision
Pod revision label per ordinal
image/config/secret generation
application protocol a storage format
```

### `RollingUpdate`

Controller nahrádza ordinaly v definovanom poradí. Kubernetes overuje Pod readiness, nie mixed-version, quorum alebo downgrade safety.

### `OnDelete`

Template sa zmení, ale existujúci Pod ostáva na starej revision, kým ho operátor alebo automation explicitne nezmaže. Tento model je vhodný, keď application-aware runbook musí pred každým replacementom:

- preniesť leadership;
- potvrdiť quorum;
- vytvoriť backup/checkpoint;
- vykonať membership remove/add;
- overiť on-disk migration;
- rozhodnúť o pokračovaní.

### Partition

Partition udrží nižšie ordinaly na current revision a aktualizuje ordinaly od určenej hranice. Je to selection control, nie canary verdict. Controller nevie, či aktualizovaný ordinal používa správnu data generation alebo či klientská operácia prešla.

## 10. Scale transition

Scale-up pridáva nové ordinal slots. Scale-down odstraňuje najvyššie ordinaly, ale nevykonáva application decommission.

Bezpečný scale-down:

```text
vyber ordinal
→ presuň leadership a traffic
→ drain-ni client work
→ odstráň membera z quorum/configuration
→ potvrď data placement a redundancy
→ zastav Pod
→ rozhodni o PVC retention
→ over cluster a business outcome
```

Samotné nastavenie `.spec.replicas` z `3` na `2` môže odstrániť Pod skôr, než application dokončí rebalance alebo membership transition.

## 11. PVC retention a deletion

Rozlišuj lifecycle:

```text
StatefulSet object
Pod ordinal slot
PVC
PV
backend volume
snapshot/backup
application member record
DNS a external identity
```

PVC retention policy a StorageClass reclaim policy rozhodujú o Kubernetes/storage cleanup behavior-e. Ani jedna nenahrádza:

- backup retention;
- legal/audit retention;
- orphan-volume inventory;
- secure data destruction;
- rollback window;
- restore validation.

Automatické deletion po scale-down môže byť vhodné pre regenerovateľné dáta, ale je nebezpečné bez explicitného data-classification a restore contractu.

## 12. Worked failure: stabilné meno vytvorilo falošný pocit fencing-u

Node `N4` s Podom `ledger-db-1` stratil spojenie s API a väčšinou clusteru. Process na N4 pokračoval a držal volume pripojený. Po node timeout-e bol vytvorený replacement rovnakého ordinalu na N7.

```text
starý Pod UID P-old na N4
+ replacement Pod UID P-new na N7
+ rovnaké meno ledger-db-1
+ delayed storage detach
+ application fencing iba podľa ordinalu
→ dva procesy považujú member-1 za aktívny
→ split writer alebo divergent log
```

StatefulSet zachoval logical slot, ale neposkytol distributed fencing.

Bezpečný design používa application term/lease, storage fencing alebo operator protocol, ktorý nový writer nepovolí, kým stará epoch nie je preukázateľne neplatná.

## 13. Worked failure: scale-up znovu použil stale retained PVC

Cluster bol dočasne zmenšený z troch na dve repliky. PVC `data-ledger-db-2` zostal zachovaný. O dva mesiace scale-up znovu vytvoril `ledger-db-2` a automaticky pripojil starý claim.

```text
retained PVC obsahuje starú membership a log generation
→ nový Pod má správne meno a mount
→ plytká readiness prejde
→ member sa pripojí so stale state-om
→ cluster vykoná nákladný recovery alebo prijme nebezpečný member state
```

Retention chráni dáta pred deletion-om. Neznamená, že retained dáta sú bezpečný bootstrap source.

Pred reuse musí aplikácia overiť cluster ID, member ID, data generation, snapshot lineage a resynchronization protocol.

## 14. Worked failure: ordered rollout sa zablokoval

Nová revision pre `ledger-db-2` obsahovala nekompatibilný on-disk reader. Pod sa spustil, ale readiness ostala false. Pri ordered update controller nepokračoval k nižším ordinalom.

To je správne controller správanie. Root cause nie je „StatefulSet sa zasekol“, ale neplatný transition medzi application a data generations.

Nútené zmazanie ďalších ordinalov by zväčšilo blast radius. Recovery má rozhodnúť medzi kompatibilným roll-forwardom, obnovením predchádzajúcej revision alebo restore/repair podľa data state-u.

## 15. Causal troubleshooting walkthrough: replacement ordinalu je Ready, cluster neprijíma writes

`ledger-db-1` bol nahradený po Node failure. Kubernetes ukazuje tri Ready Pods, ale klientské writes timeoutujú a application hlási, že nemá stabilné quorum.

### 1. Zafixuj subject a pôvodný outcome

Zaznamenaj:

```text
StatefulSet UID/generation/currentRevision/updateRevision
ordinal 1 old a new Pod UID/Node/IP
PVC UID, PV, backend volume ID a attach history
filesystem/data generation a restore lineage
application cluster/member ID
leader term a fencing epoch
peer DNS answers a connection targets
replication positions a quorum view každého membera
image/config/secret generations
business operation ID, ktorý musí commitnúť presne raz
```

### 2. Competing hypotheses

1. Starý process na pôvodnom Node-e stále beží.
2. Storage backend nepovolil bezpečný detach/fencing.
3. Replacement pripojil správny PVC, ale stale alebo poškodenú data generation.
4. PVC/PV mapping patrí inému clusteru alebo restore-u.
5. Peer DNS cache stále smeruje na starú IP.
6. Nový member nie je synchronized, hoci readiness je green.
7. Application member ID alebo cluster ID sa nezhoduje.
8. Mixed-version protocol alebo on-disk format nie je kompatibilný.
9. Partition/update strategy ponechala neočakávanú revision.
10. NetworkPolicy, MTU alebo peer TLS blokujú iba replication path.
11. Quorum existuje, ale client Service smeruje na non-serving followers.
12. Status a dashboard miešajú Pods podľa mena namiesto UID.

### 3. Discriminating observation points

- old/new Pod UIDs, Node status a deletion timeline;
- storage attach/detach a fencing audit;
- PVC UID → PV → backend volume correlation;
- application cluster/member IDs z data directory;
- leader term, commit index a replication lag per member;
- DNS answers z každého Podu a active peer sockets;
- StatefulSet Pod revision labels;
- imageID, config a secret loaded epoch;
- EndpointSlice targetRef UIDs a application roles;
- packet/TLS evidence na peer porte;
- backup/restore manifest a data checksum.

Observation `Pod Ready=True` nevylučuje stale data ani split writer. Observation `old Node je NotReady` nevylučuje, že starý process alebo volume session stále existuje.

### 4. Containment

- zastav alebo obmedz writes, ak fencing nie je preukázané;
- neforce-detach-ni volume bez storage a application ownership rozhodnutia;
- nevymazávaj PVC ani data directory;
- zachovaj old/new Pod, storage, DNS a application logs;
- odstráň non-serving memberov z client endpointov;
- pozastav ďalší rollout a scale transition;
- zafixuj canonical cluster a backup subject.

### 5. Recovery podľa boundary

- old writer → fence-ni starú epoch a potvrď process/volume termination;
- stale DNS/socket → obnov discovery a peer connection generation;
- wrong volume/data generation → odpoj nesprávny subject a obnov canonical data podľa runbooku;
- unsynchronized member → vykonaj bounded resync alebo snapshot restore;
- protocol/storage incompatibility → nasadi kompatibilný artifact alebo reviewovaný roll-forward;
- wrong client routing → viaž readiness/endpoints na client-serving role;
- corrupted member → odstráň ho z membershipu pred rebuildom a rejoinom.

### 6. Over pôvodný outcome

Potvrď:

- presne jeden process vlastní každý ordinal a fencing epoch;
- každý Pod UID používa správny PVC/PV/backend volume;
- všetci members majú správny cluster ID a kompatibilnú data generation;
- quorum a leader term sú stabilné;
- replication lag sa vrátil do limitu;
- client EndpointSlice obsahuje iba client-serving UIDs;
- payment ledger append sa vykonal presne raz;
- ďalší member restart/reconcile je bezpečný;
- backup po recovery je čitateľný a restore test prejde.

### 7. Posuň control skôr

Pridaj:

- UID/ordinal/PVC/member/data-epoch manifest;
- storage fencing a partition test;
- retained-PVC reuse preflight;
- application-aware readiness a membership metrics;
- mixed-version a downgrade compatibility gate;
- backup/restore proof pred rolloutom;
- operator alebo runbook pre membership transitions;
- alert na duplicate member ID, old writer alebo revision drift.

## 16. Observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| Controller | StatefulSet UID/generation | revisions, strategy, partition, status |
| Slot | ordinal + Pod UID | old/new UID, Node, lifecycle |
| Network | headless Service/DNS generation | records, cache, sockets, peer TLS |
| Storage | PVC/PV/backend volume | binding, attach, filesystem, data epoch |
| Membership | cluster/member ID | role, term, quorum, replication position |
| Revision | Pod revision + artifact | imageID, config, secret, format compatibility |
| Readiness | Pod UID + application role | synchronized/client-serving verdict |
| Retention | data/backup subject | PVC policy, snapshots, restore proof |
| Business | operation ID | commit, downstream audit, exactly-once invariant |

## 17. Referenčné príkazy

```bash
kubectl get statefulset <name> -n <namespace> -o yaml
kubectl describe statefulset <name> -n <namespace>
kubectl get pods -n <namespace> -l '<selector>' -o wide
kubectl get pvc,pv -o wide
kubectl get controllerrevision -n <namespace>
kubectl get endpointslice -n <namespace> -o yaml
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Príkazy poskytujú Kubernetes observations. Membership, fencing a data correctness musia pochádzať aj z aplikácie a storage platformy.

## 18. Referenčné pravidlá

- StatefulSet stabilizuje ordinal slots, nie process UIDs.
- Stabilné Pod meno nie je fencing token.
- Headless Service poskytuje discovery, nie membership correctness.
- Per-ordinal PVC poskytuje identity väzbu, nie replikáciu alebo backup.
- PVC `Bound` nepreukazuje správnu data generation.
- Ready replica nemusí byť synchronized, quorum-valid ani client-serving.
- Ordered rollout nevyrieši mixed-version alebo on-disk incompatibility.
- Partition vyberá ordinaly; neposkytuje canary acceptance verdict.
- Scale-down nevykoná application decommission.
- Retained PVC nemusí byť bezpečný bootstrap source.
- Deletion StatefulSetu, Podov, PVCs, PVs a backend dát sú odlišné transitions.
- Recovery musí overiť fencing, data lineage, membership, endpoints a business outcome.

## 19. Kontrolné otázky

1. Aký lifecycle spája StatefulSet generation s client-serving stateful replikou?
2. Čo sa pri replacement-e ordinalu zachová a čo dostane novú identity?
3. Prečo ordinal ani stabilné Pod meno nie sú fencing token?
4. Čo headless Service poskytuje a čo neposkytuje?
5. Ako overíš, že PVC obsahuje správnu data generation?
6. Prečo tri Ready Pods nemusia znamenať quorum?
7. Kedy je `OnDelete` bezpečnejší než automatický rolling update?
8. Aké riziko má reuse PVC po scale-down/scale-up?
9. Prečo partition nie je application canary verdict?
10. Čo musí StatefulSet recovery verdict overiť?

## Glossary impact

Relevantné pojmy: StatefulSet lifecycle subject, ordinal slot, ordinal replacement subject, per-ordinal storage identity, stateful membership subject, fencing epoch, data generation, retained-PVC reuse boundary, headless-Service discovery generation, application-aware readiness, partitioned revision subject, stateful scale transition, stateful decommission subject, stateful observation matrix a stateful acceptance verdict.

## Oficiálna dokumentácia

- [StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [Headless Services](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services)
- [Persistent volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Deployment](deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: DaemonSet →](daemonset.md)
<!-- KNOWLEDGE-NAVIGATION:END -->