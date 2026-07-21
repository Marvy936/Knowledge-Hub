# Volumes, PV, PVC a StorageClass

Kubernetes storage model oddeľuje **Pod mount contract**, **storage request**, **cluster storage resource** a **provisioning policy**. Volume v Pod spec-e určuje, čo sa má mountnúť. PersistentVolumeClaim (PVC) vyjadruje workload požiadavku. PersistentVolume (PV) reprezentuje konkrétny storage resource. StorageClass definuje spôsob dynamického provisioningu a lifecycle defaults.

## 1. Prečo storage potrebuje samostatný model

Pod je nahraditeľný a jeho container writable layer nie je stabilná data identity.

Stateful workload potrebuje oddeliť:

- Pod/process lifecycle,
- logical data identity,
- physical storage asset,
- attach/mount lifecycle,
- topology,
- access mode,
- backup a restore,
- deletion/reclaim policy.

Kubernetes vytvára orchestration primitives, ale negarantuje application consistency ani správny databázový failover.

## 2. Pod volumes

Pod spec obsahuje `volumes` a containers obsahujú `volumeMounts` alebo `volumeDevices`.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example
spec:
  containers:
    - name: app
      image: example/app:1
      volumeMounts:
        - name: data
          mountPath: /var/lib/example
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: example-data
```

Volume existuje v Pod lifecycle kontexte, ale jeho backing storage môže byť ephemeral alebo persistent.

## 3. Ephemeral volume types

Príklady:

- `emptyDir`,
- ConfigMap/Secret/projected volume,
- Downward API,
- CSI ephemeral volume,
- generic ephemeral volume,
- `image` volume podľa podporovanej verzie/platformy.

`emptyDir` prežije restart containeru v rovnakom Pode, ale nie odstránenie Podu. Môže byť disk-backed alebo memory-backed.

Ephemeral neznamená bez limitov. Dáta môžu spotrebovať local ephemeral storage a vyvolať Node pressure/eviction.

## 4. PersistentVolume

PV je cluster-scoped API object reprezentujúci konkrétny storage resource.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-example
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: fast-ssd
  csi:
    driver: storage.example.com
    volumeHandle: volume-12345
```

PV obsahuje napríklad:

- capacity,
- access modes,
- volume mode,
- storage class,
- reclaim policy,
- node affinity,
- CSI volume handle,
- claim reference,
- status phase.

PV object nie je samotný disk. Je Kubernetes reprezentácia external alebo local storage assetu.

## 5. PersistentVolumeClaim

PVC je namespaced request na storage.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: example-data
  namespace: production
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: fast-ssd
```

Claim definuje požadované:

- capacity,
- access modes,
- volume mode,
- StorageClass,
- selector alebo explicitný `volumeName` v špecifických prípadoch.

Pod používa PVC vo svojom namespace. PV je cluster-scoped, ale binding je one-to-one medzi konkrétnym PVC a PV.

## 6. Binding

PV/PVC controller hľadá kompatibilný PV podľa:

- requested capacity,
- access modes,
- volume mode,
- StorageClass,
- selector,
- topology a binding timing,
- explicitných references.

Po bindingu:

- PVC status je `Bound`,
- PV má `claimRef`,
- binding chráni storage pred náhodným použitím iným claimom.

Binding neoveruje, či application schema alebo filesystem content zodpovedá workloadu.

## 7. Static a dynamic provisioning

### Static provisioning

Administrator vytvorí PV object pre už existujúci storage asset. PVC sa naň neskôr bindne.

Použitie:

- import existujúcich diskov,
- presná kontrola identity,
- špecifický storage appliance workflow.

### Dynamic provisioning

PVC odkazuje na StorageClass a external provisioner vytvorí nový backing volume a PV.

```text
PVC
→ StorageClass
→ CSI provisioner
→ storage API
→ backing volume
→ PV
→ binding
```

Dynamic provisioning znižuje manuálnu prácu, ale zvyšuje význam StorageClass defaults a delete policy.

## 8. StorageClass

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: csi.example.com
parameters:
  type: ssd
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

StorageClass definuje najmä:

- provisioner,
- implementation-specific parameters,
- reclaim policy pre dynamicky provisioned PVs,
- volume binding mode,
- expansion capability,
- mount options,
- allowed topologies.

StorageClass je cluster-scoped policy object. Nie je namespaced tenant boundary.

## 9. Default StorageClass

PVC bez explicitného `storageClassName` môže použiť default StorageClass podľa cluster configuration.

Riziká:

- migration default class zmení backing storage nových claims,
- viac default classes vytvára nejasné správanie,
- cost/performance/compliance sa zmení bez zmeny workload manifestu.

Pre kritický state explicitne deklaruj očakávanú class alebo použi platform policy s jasným contractom.

`storageClassName: ""` má odlišný význam od neuvedeného poľa: žiada claim bez StorageClass podľa podporovaného binding modelu.

## 10. Access modes

Bežné access modes:

- `ReadWriteOnce` (RWO),
- `ReadOnlyMany` (ROX),
- `ReadWriteMany` (RWX),
- `ReadWriteOncePod` (RWOP).

Access mode opisuje podporovaný mount/access contract, nie application-level distributed locking.

Dôležité:

- RWO typicky znamená read-write mount z jedného Node-u, nie automaticky iba jeden Pod,
- RWX neznamená, že application bezpečne podporuje concurrent writers,
- RWOP poskytuje užšiu single-Pod write boundary pri podporovanom CSI stacku.

## 11. Volume mode

### Filesystem

Defaultný model. Node mountne filesystem a container dostane directory.

### Block

PVC/PV môže používať raw block device:

```yaml
spec:
  volumeMode: Block
```

Container používa `volumeDevices`, nie `volumeMounts`.

Raw block vyžaduje application, ktorá pozná device semantics. Neobsahuje automatický filesystem, permissions ani directory hierarchy.

## 12. Reclaim policy

### `Delete`

Po odstránení PVC a uvoľnení PV môže controller odstrániť PV object aj external storage asset podľa drivera.

### `Retain`

PV a backing asset sa zachovajú pre manuálny recovery/reuse workflow.

Reclaim policy nie je backup policy.

Pri kritických dátach pred deletionom over:

- final backup/snapshot,
- restore test,
- external resource identity,
- retention/legal requirements,
- controller/finalizer status.

## 13. Deletion protection a finalizers

Storage controllers používajú finalizers na koordináciu deletionu PV/PVC a external assetov.

Stuck deletion môže znamenať:

- Pod stále používa PVC,
- attach/detach operácia nebola dokončená,
- CSI controller je nedostupný,
- external volume API zlyháva,
- protection finalizer stále správne blokuje nebezpečné odstránenie.

Neodstraňuj finalizer naslepo. Najprv zisti, aký cleanup chráni.

## 14. `Immediate` vs. `WaitForFirstConsumer`

### `Immediate`

Volume sa provisionuje/bindne hneď po vytvorení PVC.

Riziko pri topology-constrained storage:

- volume vznikne v zone A,
- Pod constraints vyžadujú zone B,
- Pod zostane `Pending`.

### `WaitForFirstConsumer`

Provisioning/binding počká, kým scheduler zohľadní Pod placement constraints.

Tým sa storage topology koordinuje s:

- node affinity,
- zones,
- Pod affinity/anti-affinity,
- taints/tolerations,
- resource capacity.

Pri tomto režime nepoužívaj `nodeName` ako náhradu scheduleru; môže obísť potrebnú scheduling/binding koordináciu.

## 15. CSI architecture

Container Storage Interface oddeľuje Kubernetes od vendor-specific storage implementation.

Typické komponenty:

- CSI controller plugin,
- external provisioner,
- external attacher,
- external resizer,
- snapshotter podľa nasadenia,
- CSI node plugin ako DaemonSet,
- kubelet volume manager.

Zjednodušený lifecycle:

```text
PVC
→ provision volume
→ scheduler vyberie Node
→ attach podľa potreby
→ node stage
→ node publish/mount
→ Pod používa volume
→ unpublish
→ unstage/detach
```

Nie každý backend potrebuje attach krok; network filesystem sa správa inak než block disk.

## 16. Node affinity a topology

PV môže mať node affinity určujúcu, kde je storage dostupný.

Príklady:

- cloud zone,
- konkrétny Node pri local volume,
- storage topology segment,
- rack alebo failure domain.

Scheduler musí nájsť Node, ktorý spĺňa workload aj volume constraints.

`volume node affinity conflict` znamená, že vybraný alebo dostupný PV nie je prístupný na kandidátnom Node-e.

## 17. Local PersistentVolume

Local PV reprezentuje storage fyzicky viazaný na Node.

Výhody:

- nízka latency,
- vysoký výkon,
- lokálne NVMe alebo špeciálny disk.

Riziká:

- Node failure znamená nedostupný volume,
- Pod sa nemôže jednoducho presunúť inde,
- potreba application replication,
- node replacement a data recovery workflow,
- topology-aware scheduling.

Local PV nie je high availability iba preto, že je spravovaný Kubernetesom.

## 18. Expansion

Ak StorageClass a CSI driver podporujú expansion, zväčšenie PVC requestu môže spustiť:

1. backend volume resize,
2. PV/PVC capacity update,
3. filesystem resize online alebo pri remounte podľa drivera/filesystemu.

Zmenšenie volume spravidla nie je všeobecne podporovaný bezpečný operation.

Sleduj:

- PVC conditions,
- controller logs,
- filesystem size v Pode,
- backend capacity,
- quota a cost.

## 19. Snapshots a backup

VolumeSnapshot API a CSI snapshotter môžu vytvoriť storage snapshot, ak ich cluster poskytuje.

Snapshot však môže byť iba crash-consistent. Pre databázu môže byť potrebné:

- quiesce/freeze,
- application-native backup,
- WAL/binlog coordination,
- consistency-group snapshot,
- cross-region/account copy,
- restore validation.

PV/PVC object nie je data backup. etcd backup tiež neobsahuje samotný external volume content.

## 20. StatefulSet a PVC

StatefulSet `volumeClaimTemplates` vytvára per-ordinal PVCs.

```text
data-db-0
data-db-1
data-db-2
```

Replacement Pod s rovnakým ordinalom používa ten istý claim podľa controller contractu.

StatefulSet deletion alebo scale-down nemusí automaticky odstrániť PVCs; závisí od retention policy a object lifecycle. Pred cleanupom over logical replica, backup a quorum.

## 21. Security

Storage môže obsahovať najcitlivejšie dáta systému.

Controls:

- encryption at rest a key ownership,
- transport encryption,
- least-privilege CSI/cloud credentials,
- namespace/RBAC nad PVCs,
- node access a mount namespace security,
- filesystem UID/GID/SELinux labeling,
- snapshot/backup access,
- secure deletion a retention,
- admission policy pre approved StorageClasses.

Pod s mountnutým volume má data access bez ohľadu na to, či smie čítať PVC object cez API.

## 22. Observability

```bash
kubectl get pv
kubectl get pvc -A
kubectl describe pvc -n production example-data
kubectl describe pv <pv>
kubectl get storageclass
kubectl get events -n production --sort-by=.metadata.creationTimestamp
kubectl get csinode
kubectl get volumeattachment
```

Sleduj:

- PVC phase a conditions,
- selected node annotation pri delayed bindingu,
- PV claimRef a node affinity,
- VolumeAttachment status,
- CSI controller/node logs,
- kubelet mount errors,
- backend storage events,
- filesystem capacity a I/O latency.

## 23. Troubleshooting

### PVC ostáva `Pending`

Over:

- StorageClass existenciu a defaulting,
- provisioner/controller readiness,
- capacity/quota,
- access/volume mode,
- selector,
- topology,
- `WaitForFirstConsumer` a existenciu schedulovateľného Podu,
- Events.

### Pod má `FailedMount`

Over Secret/config projection alebo PVC mount, CSI node plugin, filesystem, permissions, mount options a Node connectivity k storage backendu.

### `Multi-Attach error`

Volume je stále attached na inom Node-e alebo backend/driver nepovoľuje súbežný attach. Over starý Pod/Node, fencing a detach status. Neforce-detachuj bez rizikovej analýzy split-brain.

### `volume node affinity conflict`

PV topology sa nezhoduje s kandidátnym Node-om. Over StorageClass binding mode, Pod constraints a zone labels.

### PVC sa zväčšilo, filesystem nie

Over CSI resizer, filesystem expansion support, Pod remount/restart požiadavky a PVC conditions.

### PVC/PV ostáva `Terminating`

Over active Pod usage, protection finalizers, CSI deletion a external volume API.

## 24. Anti-patterny

### PVC považované za backup

Claim je iba reference na live storage.

### `Delete` reclaim policy bez vedomého data lifecycle

Odstránenie claimu môže zmazať external asset.

### RWX považované za databázový cluster

Filesystem access mode neposkytuje transaction coordination.

### `Immediate` binding pre zonálny storage bez topology analýzy

Volume môže vzniknúť v nesprávnej zone.

### Local PV bez application replication

Node failure sa stáva data-unavailability incidentom.

### Ručné odstránenie storage finalizerov

Môže vytvoriť orphan alebo nebezpečné zmazanie.

### Static cloud credential v CSI manifeste

Zväčšuje blast radius a komplikuje rotáciu.

## 25. Kontrolné otázky

1. Aký je rozdiel medzi volume, PVC, PV a StorageClass?
2. Ako sa líši static a dynamic provisioning?
3. Čo znamená one-to-one PV/PVC binding?
4. Ako sa líšia RWO, RWX a RWOP?
5. Aký je rozdiel medzi Filesystem a Block volume mode?
6. Čo robí reclaim policy a prečo nie je backup policy?
7. Prečo je `WaitForFirstConsumer` dôležitý pre zonálny storage?
8. Akú úlohu majú CSI controller a node plugin?
9. Prečo môže local PV blokovať failover na iný Node?
10. Ako diagnostikuješ PVC `Pending` oproti Pod `FailedMount`?

## Glossary impact

Relevantné pojmy: Kubernetes volume, ephemeral volume, PersistentVolume, PersistentVolumeClaim, StorageClass, static provisioning, dynamic provisioning, access mode, volume mode, reclaim policy, default StorageClass, volume binding mode, `WaitForFirstConsumer`, CSI, VolumeAttachment, local PV, volume expansion a application-consistent backup.

## Oficiálna dokumentácia

- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)
- [Dynamic Volume Provisioning](https://kubernetes.io/docs/concepts/storage/dynamic-provisioning/)
- [Volumes](https://kubernetes.io/docs/concepts/storage/volumes/)
- [Ephemeral Volumes](https://kubernetes.io/docs/concepts/storage/ephemeral-volumes/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CNI a NetworkPolicy](cni-networkpolicy.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Scheduling →](scheduling.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
