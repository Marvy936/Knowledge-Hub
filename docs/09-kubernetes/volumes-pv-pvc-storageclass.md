# Volumes, PV, PVC a StorageClass

Kubernetes storage oddeľuje požiadavku aplikácie od konkrétneho storage backendu. Pod deklaruje volume, workload používa PersistentVolumeClaim a cluster cez PersistentVolume, StorageClass a CSI realizuje provisioning, attach, mount a lifecycle. Tieto objekty však nehovoria, či sú dáta aplikačne konzistentné, správne zašifrované alebo obnoviteľné.

Pri `settlement-ledger` potrebuje každý StatefulSet ordinal vlastný 100 GiB disk v správnej zone. PVC `data-settlement-ledger-1` musí zostať viazaný na konkrétny PV a backend volume. Keď Pod zanikne, nový Pod môže znovu použiť ten istý claim. To je iný lifecycle než `emptyDir` alebo writable container layer.

## Volume v Pod specu

Ephemeral volume:

```yaml
volumes:
  - name: work
    emptyDir:
      sizeLimit: 1Gi
```

Persistent claim:

```yaml
volumes:
  - name: data
    persistentVolumeClaim:
      claimName: payments-ledger-data
```

Container mount:

```yaml
volumeMounts:
  - name: data
    mountPath: /var/lib/payments
```

Pod volume declaration určuje, čo sa má mountnúť do Podu. Samotný mount path nevytvára durable storage. Pri `emptyDir` dáta prežijú container restart v tom istom Pode, ale zaniknú s Pod UID. PVC-backed volume môže prežiť Pod replacement podľa reclaim, backend a lifecycle contractu.

## PersistentVolumeClaim ako aplikačný request

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: payments-ledger-data
  namespace: production
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: fast-zonal
  resources:
    requests:
      storage: 100Gi
```

PVC je namespaced request na kapacitu, access mode a StorageClass. `Bound` znamená, že claim je priradený PV. Neznamená, že volume je attachnutý k aktuálnemu Node-u, mountnutý do Podu alebo obsahuje správnu data generation.

```bash
kubectl get pvc payments-ledger-data -n production -o yaml
```

Sleduj PVC UID, `volumeName`, capacity, access modes, conditions a events.

## PersistentVolume ako cluster resource

PV reprezentuje konkrétny storage resource alebo handle:

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pvc-1234
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: fast-zonal
  csi:
    driver: disk.csi.example.com
    volumeHandle: vol-0abc123
```

PV je cluster-scoped. `volumeHandle` prepája Kubernetes objekt s backend identity. Pri incidente musíš rozlíšiť PVC UID, PV UID, CSI handle, cloud disk ID, filesystem UUID a application data generation.

Rovnaké claim meno po zmazaní môže dostať nový UID a nový backend disk.

## StorageClass a dynamic provisioning

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-zonal
provisioner: disk.csi.example.com
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete
allowVolumeExpansion: true
parameters:
  type: premium-ssd
```

StorageClass je provisioning policy, nie existujúci disk. `provisioner` vyberá CSI driver. `parameters` sú driver-specific. `reclaimPolicy` určuje default PV lifecycle po uvoľnení claimu. `allowVolumeExpansion` povoľuje zväčšenie podľa driver a filesystem podpory.

`WaitForFirstConsumer` odkladá provisioning alebo binding, kým scheduler pozná placement constraints prvého Podu. To pomáha vytvoriť zonálny disk v zone vybraného Node-u.

Pri `Immediate` môže volume vzniknúť skôr a zablokovať Pod na zone bez vhodnej compute capacity.

## Access modes

Najčastejšie access modes:

```text
ReadWriteOnce
ReadOnlyMany
ReadWriteMany
ReadWriteOncePod
```

Access mode je storage attachment/mount contract podľa pluginu, nie automatický application lock. `ReadWriteOnce` často znamená writable mount z jedného Node-u; viac Podov na tom istom Node-e môže stále zdieľať volume podľa driver semantics.

`ReadWriteOncePod` poskytuje prísnejšie single-Pod použitie tam, kde je podporované. Ani to nenahrádza fencing voči starému partitioned writerovi mimo control-plane observation.

## CSI controller a node path

Dynamic storage lifecycle môže zahŕňať:

```text
PVC
→ external-provisioner vytvorí backend volume a PV
→ scheduler zohľadní topology
→ external-attacher vytvorí attachment
→ CSI node plugin stage/publish
→ kubelet mountne volume do Podu
```

Každý krok môže zlyhať samostatne. `PVC Bound` patrí pred attach/mount.

```bash
kubectl get volumeattachments.storage.k8s.io
kubectl describe pod -n production <pod-name>
```

Pri `FailedAttachVolume` kontroluj attachment a cloud API. Pri `FailedMount` kontroluj node plugin, device, filesystem, permissions a mount state.

## Volume topology

Zonálny disk má Node affinity:

```bash
kubectl get pv <pv-name> -o yaml
```

PV môže vyžadovať zone `eu1-a`. Replacement Pod musí bežať na Node-e, ktorý túto topology spĺňa. Ak zone nemá voľnú kapacitu alebo Nodes sú tainted, Pod zostane Pending.

Scheduler musí súčasne splniť volume topology, Pod affinity, taints, requests a ďalšie constraints. Chyba sa môže javiť ako „storage problém“, ale root cause je nesplniteľná kombinácia placement pravidiel.

## Reclaim policy

Pri `Delete` sa po odstránení claimu a release PV môže backend resource automaticky zmazať podľa controller semantics. Pri `Retain` PV a backend zostanú na manuálne rozhodnutie.

`Retain` chráni pred automatickým zmazaním, ale nevytvára backup a môže ponechať citlivé dáta alebo náklady. `Delete` je vhodné pre rekonštruovateľné dáta, iba ak lifecycle skutočne povoľuje destruction.

Pred `kubectl delete pvc` vždy identifikuj backend data owner a recovery path.

## Expansion

Ak StorageClass a driver podporujú expansion:

```bash
kubectl patch pvc payments-ledger-data -n production \
  --type=merge -p '{"spec":{"resources":{"requests":{"storage":"150Gi"}}}}'
```

Backend volume sa môže zväčšiť skôr než filesystem. Filesystem expansion môže prebehnúť online alebo vyžadovať remount/restart podľa drivera a filesystemu.

PVC requested size, PV capacity, backend disk size a filesystem size sa môžu dočasne líšiť. Recovery verdict musí čítať všetky relevantné vrstvy.

Zmenšenie persistent volume sa všeobecne nedá očakávať ako jednoduchý patch. Vyžaduje migráciu dát na nový menší resource.

## Snapshots

VolumeSnapshot API a CSI snapshotter vytvárajú storage snapshot contract podľa drivera:

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: payments-ledger-20260801
  namespace: production
spec:
  volumeSnapshotClassName: fast-zonal-snapshots
  source:
    persistentVolumeClaimName: payments-ledger-data
```

`readyToUse=true` znamená, že storage snapshot je pripravený podľa CSI/controller contractu. Neznamená application-consistent database checkpoint. Aplikácia môže mať dirty buffers alebo multi-volume transaction.

Pre consistent backup môže byť potrebný quiesce, protocol-native snapshot, coordinated freeze alebo log position.

## Clone a restore

Nový PVC môže použiť VolumeSnapshot alebo iný PVC ako data source podľa podpory:

```yaml
spec:
  dataSource:
    name: payments-ledger-20260801
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
```

Restore vytvorí nový volume/PVC generation. Application musí overiť data identity, encryption keys, schema, transaction position a external dependencies. Obnovený disk sa nemá automaticky pripojiť k production writerovi bez fencing-u starého state-u.

## Local, network a object storage

PVC model pokrýva block alebo filesystem storage cez pluginy. Object storage sa typicky používa cez application API/SDK, nie mount semantics. Local PersistentVolume viaže dáta na konkrétny Node a vyžaduje iný failure model než network disk.

Storage type sa vyberá podľa access, consistency, latency, topology a recovery požiadaviek, nie podľa toho, či sa dá „pripojiť do Podu“.

## Security a permissions

Mountnutý filesystem má ownership a mode. Pod `securityContext` môže používať `fsGroup` podľa driver podpory:

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 65532
    runAsGroup: 65532
    fsGroup: 65532
```

Recursive ownership change na veľkom volume môže výrazne spomaliť startup. `fsGroupChangePolicy` môže znížiť zbytočné operácie podľa podporovaných semantics.

SELinux labels, mount options a encryption keys sú ďalšie vrstvy. Chyba `permission denied` nemusí byť iba Unix UID/GID.

## Incident: PVC je Bound, Pod stále Pending

PVC `payments-ledger-data` bol Bound na PV v zone `eu1-a`. Deployment mal node affinity iba na `eu1-b`. Scheduler Event uvádzal volume node affinity conflict.

Storage provisioning bolo úspešné. Pod placement contract bol nesplniteľný. Oprava vytvorila nový claim cez `WaitForFirstConsumer` v správnej topology a migrovala dáta podľa recovery plánu.

## Incident: nový Pod mountol prázdny disk

Operátor zmazal PVC s `Delete` reclaim policy a vytvoril nový claim rovnakého mena. Kubernetes pridelil nový PVC UID a nový backend volume. Pod sa spustil a mount bol zdravý, ale application data chýbali.

Meno claimu vytvorilo falošný pocit kontinuity. Recovery použila posledný overený snapshot a external reconciliation. Skorší control je ochrana destructive operácií, Retain/backup policy a explicitný backend data manifest.

## Incident: snapshot bol technicky ready, databáza nekonzistentná

Snapshot vznikol počas zápisu medzi data a WAL volumes. Obe storage snapshots boli `readyToUse`, ale nepatrili k rovnakému transaction pointu. Restore neprešiel application recovery.

Oprava zaviedla protocol-native checkpoint a group-consistent workflow. Storage ready condition zostala iba infraštruktúrnym dôkazom.

## Incident: force detach vytvoril split writer

Node bol odrezaný od control plane-u, nie od storage siete. Operátor force-detach-ol disk a pripojil ho novému Podu. Starý process stále zapisoval cez existujúcu cestu a vznikla korupcia.

Kubernetes object state nepreukázal, že starý writer je zastavený. Recovery vyžadovala storage fencing a obnovu z clean generation. Skorší control je node power fencing a application lease.

## Model, ktorý si treba odniesť

PVC je namespaced request, PV cluster resource a StorageClass provisioning policy. CSI realizuje backend create, attach a mount. `Bound`, `Attached`, `Mounted`, `Filesystem ready` a `Application data correct` sú samostatné stavy. Pri každej operácii spájaj Kubernetes UIDs s backend volume, topology a data generation a nikdy nezamieňaj snapshot readiness s overeným restore-om.

## Referencie

- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)
- [Volume Snapshots](https://kubernetes.io/docs/concepts/storage/volume-snapshots/)
- [CSI Volume Cloning](https://kubernetes.io/docs/concepts/storage/volume-pvc-datasource/)
