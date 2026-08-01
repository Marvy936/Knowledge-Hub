# StatefulSet

StatefulSet riadi Pods, pri ktorých záleží na stabilnej identite, poradí a väzbe na persistentný storage. Nie je to automatická databázová HA vrstva. Poskytuje predvídateľné mená Podov, ordinal identity, controlled creation/termination a cez `volumeClaimTemplates` stabilné PVC pre jednotlivé repliky. Aplikácia stále musí riešiť leader election, quorum, replication, fencing, backup a recovery.

V Atlas scenári budeme mať službu `settlement-ledger`, ktorá drží lokálny write-ahead log a replikuje ho medzi troma členmi. Pods `settlement-ledger-0`, `-1` a `-2` nie sú zameniteľné ako bežné web repliky. Každý ordinal má vlastný PVC a členstvo v replikačnom protokole.

## Stabilné Pod mená a headless Service

StatefulSet typicky používa headless Service:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: settlement-ledger
  namespace: production
spec:
  clusterIP: None
  selector:
    app: settlement-ledger
  ports:
    - name: peer
      port: 7000
```

A samotný StatefulSet:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: settlement-ledger
  namespace: production
spec:
  serviceName: settlement-ledger
  replicas: 3
  selector:
    matchLabels:
      app: settlement-ledger
  template:
    metadata:
      labels:
        app: settlement-ledger
    spec:
      containers:
        - name: ledger
          image: registry.example.com/atlas/ledger@sha256:ledger310
          ports:
            - name: peer
              containerPort: 7000
          volumeMounts:
            - name: data
              mountPath: /var/lib/ledger
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 100Gi
        storageClassName: fast-zonal
```

Pod DNS identity môže byť napríklad:

```text
settlement-ledger-0.settlement-ledger.production.svc.cluster.local
```

Stabilné DNS meno neznamená, že process je leader alebo ready. Je to discovery identity pre daný ordinal.

## Ordinal identity

StatefulSet vytvára Pods s poradovými číslami. Ordinal sa používa v mene Podu a PVC.

```bash
kubectl get pods -n production -l app=settlement-ledger
kubectl get pvc -n production -l app=settlement-ledger
```

Pri replacement-e `settlement-ledger-1` vznikne nový Pod UID, ale znovu použije PVC určený pre ordinal 1, ak lifecycle policy a objekty ostali zachované. Stabilná je logická identita ordinalu a storage claimu, nie runtime process alebo Pod UID.

## OrderedReady a Parallel

Predvolený `podManagementPolicy: OrderedReady` vytvára a škáluje Pods v poradí a čaká na readiness pred ďalším ordinalom. To je užitočné pre niektoré bootstrapping protokoly, ale môže zablokovať celý scale-up, ak nižší ordinal nikdy nebude Ready.

```yaml
spec:
  podManagementPolicy: OrderedReady
```

`Parallel` umožní vytvárať alebo odstraňovať Pods súbežne, pričom stabilné identity ostávajú.

```yaml
spec:
  podManagementPolicy: Parallel
```

Voľba musí zodpovedať aplikácii. Kubernetes nepozná interné členstvo replikačného protokolu.

## PersistentVolumeClaims a retention

`volumeClaimTemplates` vytvoria samostatný PVC pre každý ordinal. Scale-down StatefulSetu historicky PVC automaticky neodstraňoval; aktuálne API podporuje retention policy podľa cluster verzie a konfigurácie.

Explicitný model:

```yaml
spec:
  persistentVolumeClaimRetentionPolicy:
    whenDeleted: Retain
    whenScaled: Retain
```

`Retain` chráni dáta pred automatickým zmazaním, ale môže ponechať nepoužívané volumes a náklady. `Delete` môže byť vhodné pre rekonštruovateľné replicas, ale vyžaduje dôkaz, že jediná durable kópia nezanikne.

PVC retention nie je backup. Korupcia sa môže replikovať na všetky členy a volumes.

## Update stratégia

StatefulSet podporuje `RollingUpdate` a `OnDelete`.

```yaml
spec:
  updateStrategy:
    type: RollingUpdate
```

Pri RollingUpdate controller typicky aktualizuje Pods v zostupnom ordinal poradí. Partition môže obmedziť, od ktorého ordinalu sa nová revision aplikuje:

```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 2
```

Pri troch replikách tak možno najprv aktualizovať iba najvyšší ordinal. Partition je rollout control, nie automatický canary verdict. Aplikácia musí overiť mixed-version compatibility a replikačné zdravie.

`OnDelete` znamená, že zmena template sama nevytvorí replacement. Operátor alebo automation musí Pods postupne zmazať. To dáva väčšiu kontrolu, ale ľahko ponechá mixed generations dlhšie, než bolo plánované.

## Readiness a replikačný stav

Readiness StatefulSet člena nemá kontrolovať iba otvorený port. Pre ledger môže rozlišovať:

```text
process žije
→ local storage mount je správny
→ člen pozná cluster identity
→ replikačný lag je v limite
→ člen smie prijímať svoj typ trafficu
```

Leader a follower môžu mať odlišné readiness pre write a read paths. Jeden spoločný Service selector nemusí stačiť. Aplikácia môže používať samostatné Services alebo vlastný routing podľa role.

Kubernetes nepozná quorum. Tri Ready Pods nemusia znamenať, že všetky patria do rovnakého replikačného clusteru.

## Scale-up

Pri scale-up vznikne nový ordinal a nový PVC. Aplikácia musí bezpečne pridať člena:

```text
Pod a volume vytvorené
→ process načíta správnu cluster identity
→ pripojí sa ako non-voting alebo learner podľa protokolu
→ dobehne snapshot/log
→ prejde consistency kontrola
→ vstúpi do voting alebo serving role
```

Ak readiness prejde pred dokončením catch-upu, nový člen môže prijímať stale reads alebo narušiť quorum.

## Scale-down

Zníženie replicas odstráni najvyššie ordinaly. Aplikácia však môže potrebovať najprv zmeniť membership a presunúť leadership.

```bash
kubectl scale statefulset settlement-ledger -n production --replicas=2
```

Tento príkaz nemení external membership automaticky. Ak `-2` stále patrí do quorum configuration, jeho odstránenie môže znížiť toleranciu výpadku alebo cluster zablokovať.

Bezpečný scale-down často vyzerá:

```text
vyber člena
→ odstráň ho z replikačného membershipu
→ potvrď nové quorum
→ až potom zníž StatefulSet replicas
→ rozhodni o PVC retention
```

## Scheduling a zone topology

PVC s `ReadWriteOnce` a zonálnym diskovým backendom viaže Pod na zone, v ktorej možno volume pripojiť. Pri Node failure scheduler nemôže ľubovoľne presunúť Pod do inej zone.

`WaitForFirstConsumer` StorageClass pomáha zosúladiť provisioning s prvým scheduling rozhodnutím. Po vytvorení je však volume topology konkrétna.

```bash
kubectl get pvc,pv -n production
kubectl get pod settlement-ledger-1 -n production -o wide
```

Pri Pending replacement-e kontroluj PV node affinity, dostupné Nodes v zone, taints a attach state.

## Force delete a split brain

Ak Node prestane komunikovať, Pod objekt môže zostať terminating alebo unknown. Force delete odstráni API identitu bez potvrdenia, že starý process prestal zapisovať.

```bash
kubectl delete pod settlement-ledger-1 -n production \
  --grace-period=0 --force
```

Tento príkaz je nebezpečný pre single-writer storage alebo databázový člen. Pred replacementom treba mať fencing dôkaz: starý Node je vypnutý, storage attachment je odpojený alebo application membership starú inštanciu definitívne vylúčil.

Bez fencing-u môže vzniknúť nový Pod s rovnakou logickou identitou, zatiaľ čo starý process stále vykonáva side effects.

## Backup a restore

StatefulSet a PVC opisujú runtime placement, nie recovery plan. Backup musí zachytiť application-consistent generation a dependencies. Restore potrebuje nový alebo vyčistený runtime subject, správne identity a kontrolu, že starí writers sú zastavení.

```text
snapshot diskov
≠ konzistentný replikačný cluster snapshot
≠ overený restore
```

Pri ledger systéme môže byť potrebný protocol-native snapshot, WAL position, encryption keys a external transaction reconciliation.

## Incident: Pod sa obnovil, ale pripojil nesprávne dáta

Po manuálnom zásahu operátor zmazal PVC pre `settlement-ledger-1` a vytvoril nový s podobným názvom. StatefulSet Pod sa spustil a readiness kontrolovala iba port. Člen začal ako prázdna databáza s novou internal cluster ID.

Headless DNS meno bolo správne a Pod bol Ready, no replikačný cluster ho odmietal. Oprava obnovila správny volume zo snapshotu, overila data generation a membership a až potom vrátila člena do služby.

Skorší control je nemenná väzba ordinal–PVC–backend volume ID, readiness kontrolujúca replikačný stav a policy zakazujúca ručné nahradenie claimu bez restore workflowu.

## Incident: rolling update zastal na prvom členovi

`settlement-ledger-2` po update-e neprešiel readiness, pretože nová binary vyžadovala storage format migration. Ordered rolling update nepokračoval na nižšie ordinaly. Staré dva členy boli zdravé.

Správne containment bolo pause release-u a zachovanie mixed-version compatibility. Tím vytvoril samostatný migration plan, otestoval downgrade boundary a publikoval opravenú revision. Ručné zmazanie ďalších Podov by zmenšilo quorum a rozšírilo incident.

## Incident: force delete vytvoril dvoch writerov

Node bol network-partitioned od control plane-u, ale stále mal prístup k storage a downstream systému. Operátor force-delete-ol Pod a nový Pod s rovnakým ordinalom sa spustil na inom Node-e po manuálnom force-detach volume-u. Starý process pokračoval v odosielaní external settlements.

Recovery vyžadovala zastavenie oboch writers, reconciliation external transaction IDs a obnovenie jedného autoritatívneho člena. Skorší control je infrastructure fencing a application lease viazaný na generation, nie iba Kubernetes Pod meno.

## Model, ktorý si treba odniesť

StatefulSet poskytuje stabilné ordinal identity, controlled ordering a per-replica PVC lifecycle. Neposkytuje automaticky quorum, replication, leader safety ani backup. Pri každej zmene spájaj Pod UID, ordinal, PVC UID, PV/backend volume, application member ID a data generation. Replacement je bezpečný až po fencing-u starej inštancie a overení správneho state-u.

## Referencie

- [StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)
- [Force Delete StatefulSet Pods](https://kubernetes.io/docs/tasks/run-application/force-delete-stateful-set-pod/)
