# Volumes, PV, PVC a StorageClass

Kubernetes storage nie je iba mount directory. Je to koordinovaný lifecycle medzi logical data identity, namespaced claimom, cluster-scoped PV objektom, external backing assetom, scheduler topology rozhodnutím, CSI attach/mount operáciami a application data generation. PVC `Bound` alebo Pod `Running` samy osebe nepreukazujú správne dáta, bezpečný writer model ani obnoviteľnosť.

Táto kapitola používa jeden dominantný lifecycle:

```text
data, durability a recovery intent
→ logical data identity a owner
→ PVC request a StorageClass policy
→ topology-aware provision/bind
→ PV a backing-volume identity
→ scheduler placement
→ attach, stage, publish a mount
→ application initialization a durable I/O
→ snapshot, backup a restore evidence
→ resize, replacement a detach
→ reclaim, retention a decommission verdict
```

## 1. Atlas Payments storage subject

Payments API používa retry ledger, aby po timeoutoch nezopakovala autorizáciu. Produkčný storage contract je:

```text
logical data identity: payments-retry-ledger/prod/generation-53
owner: Payments platform team
writer model: jeden canonical writer cohort
RPO: 0 pre committed retry records
RTO: 30 minút
PVC: production/retry-ledger-prod-v53
StorageClass: encrypted-zonal-ssd-v3
access: ReadWriteOncePod, ak ho stack podporuje
filesystem: ext4
backup: application-consistent snapshot + cross-account copy
forbidden outcome: prázdny/staging/stale ledger pripojený k production workloadu
```

Exact runtime subject zahŕňa:

```text
PVC UID a resourceVersion
PV UID a claimRef
StorageClass generation a provisioner
CSI driver a volumeHandle
external backend volume ID, zone a encryption key generation
VolumeAttachment UID a attached Node UID
Pod UID, Node UID, mount generation a filesystem identity
application schema/data generation a writer/fencing epoch
snapshot/backup/restore generation
```

PVC name bez UID, PV phase bez volumeHandle alebo mount path bez data generation nestačia.

## 2. Volume, PVC, PV a StorageClass majú rôzne úlohy

### Pod volume a mount contract

Pod spec určuje, ktorý source sa má sprístupniť a kde:

```yaml
volumes:
  - name: retry-ledger
    persistentVolumeClaim:
      claimName: retry-ledger-prod-v53
containers:
  - name: payments-api
    volumeMounts:
      - name: retry-ledger
        mountPath: /var/lib/payments/retry-ledger
```

Toto je consumer contract. Neurčuje samo osebe physical disk, zone, encryption key ani backup stav.

### PersistentVolumeClaim

PVC je namespaced storage request a stable claim identity pre workload. Vyjadruje napríklad capacity, access mode, volume mode a StorageClass.

### PersistentVolume

PV je cluster-scoped Kubernetes reprezentácia konkrétneho storage resource-u. Nie je samotný disk. Kľúčový bridge k external assetu je pri CSI typicky `volumeHandle`.

### StorageClass

StorageClass je provisioning a lifecycle policy. Určuje provisioner, parameters, reclaim policy, binding mode, expansion a topology defaults. Nie je namespaced tenant boundary a jej zmena môže ovplyvniť nové claims bez zmeny workload YAML-u.

## 3. Claim-to-asset identity chain

Dynamic provisioning typicky vytvorí:

```text
PVC C53
→ StorageClass SC3
→ CSI provision request OP53
→ backend volume BV53
→ PV PV53 s volumeHandle=BV53
→ claimRef na C53
→ PVC Bound
```

Binding je one-to-one ochrana medzi konkrétnym claimom a PV. Nepotvrdzuje:

- že backend obsahuje očakávané dáta;
- že filesystem je zdravý;
- že schema generation zodpovedá aplikácii;
- že volume nie je zároveň používaný stale writerom;
- že existuje použiteľný backup.

Pri static provisioningu existuje backing asset pred PVC. Import workflow musí preukázať volumeHandle, data lineage, encryption a absence active writera pred bindingom.

## 4. Default StorageClass je hidden input

PVC bez `storageClassName` môže dostať cluster default. Ak platforma zmení default z `encrypted-ssd-v2` na `general-hdd-v1`, nové claims môžu mať iný performance, topology, reclaim alebo compliance contract bez zmeny aplikácie.

```text
source manifest bez class
→ admission/defaulting v čase create
→ actual PVC storageClassName
→ nový backend type
```

Pre kritické dáta používaj explicitnú reviewed class alebo platform policy s jasným versionovaným contractom. `storageClassName: ""` nie je to isté ako chýbajúce pole.

## 5. Binding mode koordinuje storage a scheduler

### Immediate

```text
PVC create
→ volume provisioned v zone A
→ Pod neskôr potrebuje zone B
→ žiadny Node nespĺňa Pod aj PV topology
```

### WaitForFirstConsumer

```text
Pod + PVC čakajú
→ scheduler vyhodnotí workload constraints
→ vyberie kompatibilnú topology
→ provisioner vytvorí volume v tejto topology
→ binding a Pod placement pokračujú
```

`WaitForFirstConsumer` je coordination boundary medzi schedulingom a provisioningom. Priame `nodeName` môže túto koordináciu obísť a ponechať claim alebo Pod v neobnoviteľnom stave.

## 6. CSI execution lifecycle

Pre attachable block storage je typický chain:

```text
PVC/PV bound
→ scheduler vyberie Node N9
→ external attacher vytvorí VolumeAttachment VA53
→ backend attach BV53 k N9
→ CSI node stage
→ CSI node publish do Pod mount path
→ kubelet spustí containers
→ application otvorí filesystem/data
```

Pri cleanup-e:

```text
application stop a flush
→ unmount/node unpublish
→ node unstage
→ detach backend volume
→ VolumeAttachment cleanup
→ Pod/Node replacement eligibility
```

Network filesystem nemusí používať rovnaký attach krok. Diagnostika musí najprv identifikovať backend a driver lifecycle.

## 7. Access mode nie je application locking

- `ReadWriteOnce` typicky obmedzuje read-write mount na jeden Node, nie nevyhnutne jeden Pod.
- `ReadWriteMany` umožňuje mount z viacerých Nodes, ale neposkytuje transaction coordination.
- `ReadWriteOncePod` poskytuje užšiu single-Pod boundary pri podporovanom CSI stacku.
- `ReadOnlyMany` nepovoľuje writerov, ale stále potrebuje content integrity a versioning.

Ani RWOP nie je distribuovaný fencing token pre starý process mimo kontrolovaného mount lifecycle-u. Application membership a storage/provider fencing ostávajú samostatné controls.

## 8. Topology a storage placement

PV môže byť dostupný iba v konkrétnej zone, racku alebo Node-e. Scheduler musí nájsť intersection:

```text
Pod resource fit
∩ node affinity/taints/topology
∩ všetky PVC/PV topology constraints
∩ attach limits
∩ host/device constraints
```

Ak intersection neexistuje, Pod je unschedulable, aj keď každá constraint samostatne vyzerá splniteľná.

Local PV je extrémny prípad: backing asset je viazaný na Node. Kubernetes môže zachovať object identity, ale Node failure neposkytne data availability. HA musí vytvoriť application replication alebo explicitný restore/failover protocol.

## 9. Mount nie je data acceptance

Po mount-e musí application overiť:

- filesystem UUID alebo backend identity;
- expected data/schema generation;
- ownership a permissions;
- encryption/key state;
- writer lease alebo fencing epoch;
- recovery/checkpoint/WAL integrity;
- environment/tenant marker;
- absence staging alebo restored-old data.

Readiness, ktorá testuje iba zapisovateľný directory, môže prijať prázdny alebo nesprávny volume.

## 10. Permissions a security context

Effective access vzniká kombináciou:

```text
filesystem ownership/mode
+ runtime UID/GID
+ fsGroup a supplemental groups
+ mount options
+ SELinux/AppArmor a node policy
+ readOnly flag
+ backend export policy
```

`permission denied` preto neopravuj automaticky `chmod 777`. Najprv identifikuj vlastníka data contractu a enforcement boundary. Broad write permission môže zmeniť confidential data incident na integrity incident.

## 11. Reclaim policy je destructive scope

### Delete

Po odstránení claimu môže controller odstrániť PV aj external backing asset.

### Retain

PV/backing asset ostanú pre manuálny recovery alebo decommission workflow.

Ani jedna politika nie je backup. Pred PVC deletionom musí byť explicitne známe:

```text
claim UID a data identity
reclaim policy
backend asset ID
latest accepted backup/restore generation
active consumers a rollback window
legal/security retention
expected finalizer a external cleanup
```

Destructive command subject je konkrétny PVC/PV/backend chain, nie názov workloadu.

## 12. Finalizers chránia incomplete cleanup

PVC/PV/CSI finalizer môže blokovať deletion, pretože:

- Pod claim stále používa;
- VolumeAttachment alebo detach nie je dokončený;
- CSI controller/backend API je nedostupný;
- external asset cleanup ešte nemá potvrdený outcome;
- protection finalizer správne zabraňuje data loss.

Ručné odstránenie finalizeru mení stav API objectu, nie external reality. Môže vytvoriť orphan asset, stale attachment alebo zmazanie bez evidencie.

## 13. Expansion je viacstupňová operácia

```text
PVC requested size 100Gi → 200Gi
→ CSI controller expand backend
→ PV/PVC capacity update
→ node/filesystem resize
→ application vidí 200Gi
```

Backend success a PVC capacity update nepreukazujú filesystem size v Pode. Recovery musí rozlíšiť controller expansion, node expansion, filesystem support, mount/remount a application-level capacity cache.

Zmenšenie volume nie je všeobecný bezpečný inverse operation.

## 14. Snapshot a backup nie sú synonymá

Storage snapshot môže byť crash-consistent. Application-consistent backup môže potrebovať:

```text
quiesce alebo transaction checkpoint
→ flush/WAL/binlog position
→ snapshot generation
→ immutable copy mimo primary failure domain
→ catalog s data/schema/key identity
→ clean restore
→ application verification
```

PV/PVC objects ani etcd backup neobsahujú samotný external volume content. Snapshot v rovnakom account-e/region-e/credential boundary nemusí spĺňať disaster-recovery contract.

## 15. StatefulSet a retained PVC

StatefulSet ordinal `ledger-db-1` môže pri replacement-e znovu použiť `data-ledger-db-1`. Stabilná claim väzba je užitočná, ale nepreukazuje, že retained PVC stále patrí current cluster membership a data generation.

Scale-down a neskorší scale-up môže pripojiť starý member state. Pred reuse treba overiť decommission marker, replication epoch, snapshot lineage a fencing.

## 16. Worked failure: default class zmenila data contract

Nový production namespace vytvoril PVC bez explicitnej class. Cluster default bol nedávno zmenený na lacnejší HDD class s `Delete` reclaim policy.

```text
rovnaký Git manifest
→ iný admission/defaulting time
→ iná StorageClass
→ iný backend, latency a deletion contract
```

Application začala timeoutovať a retry amplification zvýšila write load. Fix nebol iba väčší timeout: platforma zaviedla explicitnú approved class, policy test a storage-class generation do release manifestu.

## 17. Worked failure: PVC Bound, ale data generation bola nesprávna

Po restore vznikol PV s platným bindingom a Pod bol Ready. Mounted filesystem však obsahoval retry ledger zo staging prostredia.

```text
PVC Bound
→ mount success
→ writable healthcheck success
→ application prijatá do Service
→ idempotency lookup čítal nesprávny tenant
```

Kubernetes storage status bol green. Chýbal application data-identity gate. Recovery odobrala Pod z trafficu, identifikovala správny backup generation a po clean restore overila tenant, schema, checkpoint a payment invariants.

## 18. Worked failure: Immediate binding vytvoril volume v nesprávnej zone

PVC sa provisionol v zone A ešte pred Podom. Deployment vyžadoval zone B kvôli hard affinity a licensed device.

```text
PV node affinity=A
∩ Pod required affinity=B
= prázdna feasible množina
```

Pridanie Nodes v zone A nepomohlo, pretože Pod constraint ich odmietala. Recovery vytvorila nový claim cez `WaitForFirstConsumer` a bezpečne migrovala dáta; editácia PV node affinity by nepresunula physical asset.

## 19. Worked failure: expansion skončila medzi backendom a filesystemom

Backend volume mal 200 GiB a PVC status tiež, no application stále videla 100 GiB.

Finding:

```text
controller expand success
→ node filesystem expansion neprebehla
→ mount zostal na starej filesystem size
```

Recovery sa riadila CSI/filesystem contractom, nie opakovaným zväčšovaním PVC. Po remount/restart kroku sa overila filesystem a application capacity.

## 20. Causal troubleshooting walkthrough: Multi-Attach po Node partition

Symptóm:

```text
old Pod P52 bol na N8
N8 je NotReady po network partition
controller vytvoril replacement P53 na N9
PVC C53 je Bound
P53 ostáva ContainerCreating
Event: Multi-Attach error
```

### 1. Zafixuj storage subject a outcome

Zaznamenaj:

```text
cluster, namespace a workload generation
PVC UID C53, PV UID PV53, StorageClass SC3
CSI driver, volumeHandle a backend volume BV53
old/new Pod UIDs P52/P53 a Nodes N8/N9
VolumeAttachment UIDs a backend attachment state
access mode, filesystem a mount generation
application writer lease/fencing epoch
data/schema/checkpoint generation
latest accepted backup a restore test
payment/retry operation IDs v impact window
```

Pôvodný outcome: retry ledger musí zostať dostupný bez duplicate writera a bez straty committed records.

### 2. Competing hypotheses

| Hypotéza | Diskriminačný dôkaz |
|---|---|
| starý Pod/process stále píše | node/out-of-band process, application membership, writer lease |
| stale Kubernetes VolumeAttachment | object status vs. backend attachment API |
| backend detach ešte prebieha | provider operation ID, timestamps a device session |
| CSI controller/attacher je stale | leader/queue/log generation, reconcile attempts |
| replacement Node nie je topology-compatible | PV affinity, Node labels, selected-node evidence |
| claim/PV ukazuje nesprávny backend | volumeHandle, asset tags a data fingerprint |
| access mode/driver nepovoľuje transition | CSI capabilities a mount inventory |

### 3. Observation points

```text
StatefulSet/Deployment replacement decision
→ scheduler binding P53→N9
→ PVC/PV binding
→ VolumeAttachment desired/actual state
→ provider attach session
→ CSI node stage/publish
→ filesystem mount
→ application writer/member state
```

`kubectl delete pod --force` alebo force-detach bez old-writer evidence môže vytvoriť split brain.

### 4. Containment

- zastav nové writer replacements a automatické force-detach;
- odober affected workload z trafficu;
- fence N8 cez cloud/hypervisor/storage mechanizmus, nie iba Kubernetes Node condition;
- zachovaj VolumeAttachment, CSI logs, backend operation IDs a application membership evidence;
- nereplayuj payment operations bez retry-ledger audit lookupu;
- nevytváraj nový prázdny claim ako rýchly workaround.

### 5. Authoritative recovery

Finding bol, že N8 bol od control plane izolovaný, ale VM aj process zostali živé a backend volume držal active session.

Recovery:

1. hard-fence N8 a over absenciu writera;
2. potvrď application membership/lease expiry;
3. nechaj CSI/backend dokončiť detach s known operation outcome;
4. reconcile-ni stale VolumeAttachment;
5. attach BV53 k N9 a mountni ho iba raz;
6. over filesystem/checkpoint/data generation pred readiness;
7. spusti P53 s novou fencing epoch;
8. vráť traffic až po retry-ledger a payment syntheticoch.

### 6. Over pôvodný a forbidden outcome

Potvrď:

- BV53 je attached iba k N9 a existuje jeden writer;
- PVC C53, PV53 a volumeHandle tvoria správny chain;
- mounted filesystem a application data generation sú G53;
- latest committed retry records existujú;
- `pay-8842` má presne jeden accepted result;
- starý N8 process ani credential nemôžu zapisovať;
- backup po recovery je application-consistent a restore test prejde;
- ďalší controlled replacement prejde bez manual force.

### 7. Posuň control skôr

Pridaj:

- explicitnú data identity a generation marker;
- StorageClass/reclaim/topology policy v release gate;
- per-volume writer/fencing telemetry;
- out-of-band Node fencing runbook;
- attachment operation IDs a unknown-outcome reconciliation;
- application-aware mount/readiness gate;
- destructive PVC/PV cleanup inventory;
- scheduled restore drills a cross-failure-domain backup;
- retained-PVC reuse eligibility test.

## 21. Observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| Data intent | logical data generation | owner, RPO/RTO, writer model, tenant/schema |
| Claim | PVC UID | class, request, access/volume mode, selected node |
| Policy | StorageClass generation | provisioner, parameters, reclaim, binding mode |
| Cluster asset | PV UID | claimRef, affinity, capacity, volumeHandle |
| Backend | volume ID | zone, encryption, attachment/session, provider operations |
| Scheduling | Pod/Node/PVC intersection | topology, attach limits, resource fit |
| Attachment | VolumeAttachment UID | desired/actual node, driver status, operation ID |
| Mount | Pod UID + mount generation | stage/publish, filesystem, UID/GID/LSM, options |
| Application | writer/data subject | fencing, schema, checkpoint, durable I/O |
| Protection | snapshot/backup generation | consistency, copy domain, catalog, restore verdict |
| Cleanup | reclaim/decommission subject | consumers, finalizers, backend deletion, retention |
| Business | payment/retry ID | durable exactly-once result a forbidden-data proof |

## 22. Referenčné príkazy

```bash
kubectl get pvc -A -o wide
kubectl get pv -o wide
kubectl get storageclass -o yaml
kubectl describe pvc <name> -n <namespace>
kubectl describe pv <name>
kubectl get volumeattachment -o yaml
kubectl get csinode -o yaml
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

Doplň CSI controller/node logs, backend storage API, filesystem observations a application data-identity evidence.

## 23. Referenčné pravidlá

- Pod writable layer nie je persistent data identity.
- PVC je request/claim; PV je Kubernetes asset record; volumeHandle identifikuje backend.
- PVC `Bound` nepreukazuje správny content ani writer safety.
- Default StorageClass je hidden provisioning input.
- `WaitForFirstConsumer` koordinuje storage topology so schedulingom.
- RWO nie je automaticky one-Pod fencing; RWX nie je transaction coordination.
- VolumeAttachment a provider attachment sú odlišné states.
- Mount success nepreukazuje application data generation.
- Reclaim policy nie je backup policy.
- Finalizer chráni incomplete cleanup; neodstraňuj ho bez owner-state dôkazu.
- Snapshot môže byť iba crash-consistent.
- Local PV neposkytuje HA bez application replication/recovery.
- Recovery musí overiť backing asset, mount, data lineage, writer fencing a business outcome.

## 24. Kontrolné otázky

1. Aký lifecycle spája data intent s accepted mounted data generation?
2. Ako sa líšia PVC UID, PV UID, volumeHandle a backend volume ID?
3. Čo binding preukazuje a čo nepreukazuje?
4. Prečo je default StorageClass hidden input?
5. Ako `WaitForFirstConsumer` koordinuje storage a scheduler?
6. Prečo RWO ani RWX nie sú application locking model?
7. Aké kroky oddeľujú backend attach od application mountu?
8. Prečo reclaim policy ani snapshot nie sú automaticky backup?
9. Ako bezpečne riešiš Multi-Attach po Node partition?
10. Čo musí storage acceptance verdict overiť?

## Glossary impact

Relevantné pojmy: Kubernetes storage lifecycle subject, logical data identity, PVC claim subject, PV asset subject, backing-volume identity, StorageClass generation, topology-binding subject, VolumeAttachment generation, CSI attach-stage-publish lifecycle, mount generation, application data generation, storage fencing epoch, destructive reclaim subject, application-consistent backup, retained-PVC reuse boundary, storage observation matrix a storage acceptance verdict.

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