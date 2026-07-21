# StatefulSet

StatefulSet je Kubernetes workload controller pre skupinu Podov, ktoré nie sú navzájom úplne zameniteľné. Každej replike poskytuje stabilnú ordinal identity, predvídateľné network meno a možnosť viazať ju na vlastný persistent storage claim.

StatefulSet nerobí z ľubovoľnej aplikácie distribuovaný systém. Poskytuje identity a lifecycle primitives; replikácia dát, leader election, quorum, consistency, failover a backup zostávajú zodpovednosťou aplikácie alebo operátora.

## 1. Deployment vs. StatefulSet

### Deployment

- Pody sú zameniteľné,
- identita konkrétnej repliky nie je stabilná,
- rollout optimalizuje dostupnosť stateless služby,
- storage je typicky shared/external alebo bez per-replica väzby.

### StatefulSet

- Pody majú stabilné ordinaly,
- každá replika môže mať vlastné PVC,
- creation, update a deletion môžu byť usporiadané,
- aplikácia môže používať stabilnú per-replica network identity.

StatefulSet používaj iba vtedy, keď workload tieto vlastnosti reálne potrebuje.

## 2. Stabilná identita

Pre StatefulSet `db` s tromi replikami vzniknú Pody:

```text
db-0
db-1
db-2
```

Ordinal je súčasť identity. Ak `db-1` zanikne, náhradný Pod má opäť meno `db-1`, ale nový UID.

Stabilné meno teda neznamená rovnaký Pod object alebo process. Znamená stabilnú logical slot identity.

## 3. Headless Service

StatefulSet typicky používa headless Service:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: db
spec:
  clusterIP: None
  selector:
    app: db
  ports:
    - name: client
      port: 5432
```

StatefulSet:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: db
spec:
  serviceName: db
  replicas: 3
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
        - name: db
          image: registry.example.com/db@sha256:...
          ports:
            - name: client
              containerPort: 5432
```

Stabilná DNS identita môže vyzerať:

```text
db-0.db.<namespace>.svc.cluster.local
```

DNS caching a negative caching môžu spôsobiť oneskorenie pri novo vzniknutých identitách. Aplikácia musí mať retry/discovery model.

## 4. `volumeClaimTemplates`

```yaml
spec:
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: fast
        resources:
          requests:
            storage: 20Gi
```

Každý Pod dostane vlastný claim, napríklad:

```text
data-db-0
data-db-1
data-db-2
```

Replacement Pod s rovnakým ordinalom sa pripojí k zodpovedajúcemu PVC, pokiaľ storage topology a attach semantics umožnia mount na novom Node-e.

## 5. Storage nie je automatická HA

Per-replica PVC neposkytuje automaticky:

- replikáciu medzi volumes,
- konzistentný distributed database cluster,
- leader election,
- application-consistent backup,
- regionálne failover,
- fencing proti split-brain,
- kompatibilný restore.

StatefulSet iba zachová mapovanie ordinal → claim identity.

## 6. Pod management policy

### `OrderedReady`

Default model typicky:

- vytvára Pody v rastúcom poradí,
- čaká na Ready pred ďalším ordinalom,
- scale-down vykonáva v opačnom poradí,
- zachováva usporiadané lifecycle guarantees.

### `Parallel`

```yaml
spec:
  podManagementPolicy: Parallel
```

Umožňuje vytváranie alebo odstraňovanie Podov bez čakania na predchádzajúce ordinaly.

Použi iba ak aplikácia nepotrebuje ordered bootstrap alebo termination.

## 7. Update strategies

### `RollingUpdate`

Controller postupne nahrádza Pody podľa ordinal orderu a readiness.

```yaml
spec:
  updateStrategy:
    type: RollingUpdate
```

### `OnDelete`

```yaml
spec:
  updateStrategy:
    type: OnDelete
```

Template sa zmení, ale existujúce Pody sa nahradia až po ich ručnom alebo externom deletion-e.

Použitie:

- aplikácia potrebuje explicitnú operátorskú koordináciu,
- update musí nasledovať application-level failover postup,
- automatický ordered rollout nie je bezpečný.

## 8. Partitioned rolling update

Partition umožňuje rollout iba pre ordinaly väčšie alebo rovné stanovenej hodnote.

```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 2
```

Pri replikách `0..4` sa aktualizujú najprv `4`, `3`, `2`; `0` a `1` zostanú na starej revision.

Použitie:

- canary konkrétneho ordinalu,
- staged update,
- kontrolovaný cluster membership postup.

Partition sám neanalyzuje health ani business correctness.

## 9. Revision a status

```bash
kubectl rollout status statefulset/db
kubectl rollout history statefulset/db
kubectl get statefulset db -o yaml
kubectl get controllerrevision
```

StatefulSet používa ControllerRevision objects na uchovanie revision metadata.

Sleduj:

- `currentRevision`,
- `updateRevision`,
- `currentReplicas`,
- `updatedReplicas`,
- `readyReplicas`,
- `availableReplicas`,
- observed generation,
- Pod ordinaly a PVC binding.

## 10. Scale-up a scale-down

```bash
kubectl scale statefulset db --replicas=5
```

Pri scale-up vznikajú nové ordinaly. Pri scale-down sa vyššie ordinaly odstránia ako prvé pri ordered policy.

Aplikácia musí bezpečne zvládnuť:

- membership join/leave,
- data rebalance,
- quorum zmenu,
- leadership transfer,
- long-running graceful termination.

Kubernetes scale command nevykoná application-specific decommission automaticky.

## 11. PVC retention

Historicky sa PVC pri scale-down alebo deletion StatefulSetu zámerne ponechávajú na ochranu dát. Moderný StatefulSet môže mať explicitnú retention policy podľa podporovanej cluster verzie a API.

Pred použitím over:

- behavior `whenDeleted` a `whenScaled`,
- StorageClass reclaim policy,
- owner references na PVC,
- backup a legal retention,
- bezpečnosť automatického deletion-u.

Automatické mazanie storage musí byť vedomý policy decision, nie cleanup convenience.

## 12. Deletion

Zmazanie StatefulSetu neznamená, že všetky súvisiace dáta automaticky zmiznú.

Rozlišuj:

- StatefulSet object,
- Pody,
- PVCs,
- PVs,
- storage backend volumes,
- headless Service,
- snapshots a backups.

Pre ordered graceful shutdown môže byť vhodné najprv scale na nulu podľa application runbooku a až potom deletion controlleru.

## 13. Pod identity a replacement

Náhradný `db-1` má:

- rovnaký Pod name,
- rovnaký ordinal,
- rovnaký logical DNS slot,
- typicky rovnaký PVC,
- nový Pod UID,
- novú Pod IP,
- nový runtime process.

Aplikácia nemá viazať fencing iba na Pod name. Potrebuje bezpečný membership/lease/epoch mechanizmus.

## 14. Scheduling a topology

Stateful workload často kombinuje:

- volume topology,
- zone/node affinity,
- anti-affinity alebo topology spread,
- requests a limits,
- taints/tolerations,
- local persistent volumes.

Pod môže zostať Pending, ak jeho PVC je viazané na storage nedostupný v dostupných Nodes alebo ak affinity požiadavky nemajú kapacitu.

## 15. Availability a quorum

Ready replicas nie sú automaticky quorum.

Príklad päťčlenného consensus clusteru:

- päť Podov môže byť Running,
- iba tri majú aktuálny log,
- dva sú network-partitioned,
- Kubernetes Service môže stále smerovať na nevhodné endpoints, ak readiness nepozná application role.

Probes a Service routing musia reflektovať client-serving a cluster-role semantics.

## 16. Upgrade safety

Pred rolling update over:

- mixed-version compatibility,
- supported upgrade order,
- storage format a on-disk migrations,
- protocol version negotiation,
- leader/follower update sequence,
- quorum počas unavailable replica,
- backup a restore test,
- downgrade podporu.

Niektoré databázy vyžadujú operátor, ktorý vykonáva application-aware reconciliation nad StatefulSetom.

## 17. Observability

```bash
kubectl get statefulset db
kubectl describe statefulset db
kubectl get pods -l app=db -o wide
kubectl get pvc
kubectl get controllerrevision
kubectl rollout status statefulset/db
kubectl get events --sort-by=.metadata.creationTimestamp
```

Sleduj:

- ordinal progression,
- current/update revision,
- Ready/Available Pody,
- headless Service a DNS,
- PVC/PV binding a attach/mount Events,
- application membership, role a replication lag,
- storage latency/capacity,
- Pod termination a fencing.

## 18. Failure scenáre

### `db-0` nie je Ready a rollout stojí

Pri `OrderedReady` môže blokovať ďalšie ordinaly. Diagnostikuj konkrétny Pod, nie iba controller status.

### PVC ostáva Pending

Over StorageClass, provisioner, access mode, capacity, topology a `WaitForFirstConsumer` scheduling flow.

### Volume sa nepripojí na nový Node

Over detach z pôvodného Node-u, CSI controller/node plugins, topology a cloud volume state.

### DNS meno sa dočasne nerozlišuje

Over headless Service, selector, Pod readiness/publication policy, CoreDNS a DNS cache.

### Rollout je v broken state

Ordered rolling update môže vyžadovať manuálny zásah, ak nový Pod template nikdy nedosiahne Ready a controller zachováva update ordering.

### Scale-down poškodí quorum

Kubernetes splnil replica count, ale application decommission alebo quorum model nebol bezpečný.

## 19. Anti-patterny

### StatefulSet použitý iba preto, že aplikácia má disk

Stateless Deployment môže používať external state; stabilná per-replica identita nemusí byť potrebná.

### Zdieľanie jedného RWO claimu medzi viacerými replikami bez podpory backendu

Vzniknú attach/mount konflikty alebo unsafe writes.

### Predpoklad, že ordinal je fencing token

Starý process môže stále existovať počas partition alebo detach delay.

### Automatický update bez mixed-version analýzy

Ordered rollout nevyrieši protocol alebo storage incompatibility.

### Delete/scale-down bez PVC retention kontroly

Môže vzniknúť orphan storage alebo nevratná strata dát podľa policy.

### Readiness iba na otvorený TCP port

Pod môže byť process-ready, ale nie leader, synced alebo client-serving.

## 20. Kontrolné otázky

1. Akú stabilitu poskytuje StatefulSet?
2. Čo sa pri replacement-e Podu zachová a čo sa zmení?
3. Načo slúži headless Service?
4. Ako funguje `volumeClaimTemplates`?
5. Prečo PVC neznamená automatickú data HA?
6. Aký je rozdiel medzi `OrderedReady` a `Parallel`?
7. Ako sa líšia `RollingUpdate` a `OnDelete`?
8. Načo slúži partition?
9. Prečo Ready replicas nemusia znamenať quorum?
10. Kedy je namiesto čistého StatefulSetu vhodný operator?

## Glossary impact

Relevantné pojmy: StatefulSet, stable ordinal identity, headless Service, stable network identity, `volumeClaimTemplates`, per-replica PVC, `OrderedReady`, parallel Pod management, StatefulSet partition, ControllerRevision, current revision, update revision a PVC retention policy.

## Oficiálna dokumentácia

- [StatefulSets](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [Headless Services](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services)
- [Persistent volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
