# DaemonSet

DaemonSet zabezpečuje, aby na každom vhodnom Node-e bežal Pod určitej template. Nepoužíva sa na ľubovoľný počet business replík, ale na Node coverage: CNI agent, log collector, node exporter, storage plugin alebo security sensor má byť prítomný všade, kde jeho schopnosť potrebujeme.

V Atlas clustri používa DaemonSet `atlas-node-agent` na zber Node metrics a lokálnych runtime udalostí. Ak pribudne nový worker Node, DaemonSet controller preň vytvorí Pod. Ak Node prestane spĺňať selector alebo zanikne, príslušný Pod lifecycle sa ukončí.

## Ktoré Nodes sú vhodné

DaemonSet template môže používať `nodeSelector`, node affinity a tolerations:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: atlas-node-agent
  namespace: platform-system
spec:
  selector:
    matchLabels:
      app: atlas-node-agent
  template:
    metadata:
      labels:
        app: atlas-node-agent
    spec:
      serviceAccountName: atlas-node-agent
      nodeSelector:
        kubernetes.io/os: linux
      tolerations:
        - operator: Exists
      containers:
        - name: agent
          image: registry.example.com/atlas/node-agent@sha256:agent91
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
```

Tolerácia všetkých taints môže byť potrebná pre infraštruktúrny agent, ale výrazne rozširuje coverage a privilege boundary. Agent na control-plane, GPU alebo security-isolated Nodes musí byť zámerné rozhodnutie, nie vedľajší efekt `operator: Exists`.

## Desired count sa odvodzuje z Node inventory

DaemonSet `.status.desiredNumberScheduled` nie je statická hodnota z manifestu. Controller ju vypočíta z Nodes, ktoré spĺňajú placement pravidlá.

```bash
kubectl get daemonset atlas-node-agent -n platform-system
kubectl get daemonset atlas-node-agent -n platform-system -o yaml
```

Dôležité status hodnoty zahŕňajú desired, current, ready, available a misscheduled count. `desired=20` a `ready=19` znamená chýbajúcu alebo nezdravú Node coverage. `numberMisscheduled>0` ukazuje Pods na Nodes, ktoré už nemajú byť eligible.

## DaemonSet Pods a scheduling

DaemonSet controller vytvára Pod pre každý vhodný Node a zabezpečí jeho Node affinity/assignment podľa aktuálneho mechanizmu. Scheduler stále rieši ďalšie constraints a resource availability. Infra agent teda môže zostať Pending, ak má príliš vysoké requests alebo konfliktné pravidlá.

```bash
kubectl get pods -n platform-system -l app=atlas-node-agent -o wide
```

Pri coverage incidente porovnávaj zoznam vhodných Nodes s Pod UIDs a Node assignmentom. Samotný count nemusí odhaliť, že nový Node pool používa inú label generation a preto vôbec nepatrí do desired setu.

## Host access a security boundary

Node agents často potrebujú host paths, host network, privileged capability alebo runtime socket. Každý taký prístup zväčšuje blast radius.

```yaml
spec:
  hostPID: true
  containers:
    - name: agent
      securityContext:
        privileged: false
        readOnlyRootFilesystem: true
      volumeMounts:
        - name: host-log
          mountPath: /host/var/log
          readOnly: true
  volumes:
    - name: host-log
      hostPath:
        path: /var/log
        type: Directory
```

Aj read-only hostPath odhaľuje host dáta. Mount container runtime socketu často dáva prakticky node-admin authority, preto sa mu treba vyhnúť alebo ho oddeliť do veľmi úzkej trusted platform vrstvy.

## Rolling update

DaemonSet predvolene používa RollingUpdate. `maxUnavailable` riadi, koľko Node agent Podov môže byť počas update-u nedostupných. Novšie API podľa verzie podporuje aj surge semantics pre DaemonSet.

```yaml
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
```

Pri kritickom CNI alebo storage DaemonSete môže výmena agentov priamo ovplyvniť workload dataplane. Rollout sa má vykonávať po failure domains a s capability canary, nie iba čakať na `updatedNumberScheduled`.

```bash
kubectl rollout status daemonset/atlas-node-agent \
  -n platform-system --timeout=10m
```

Úspešný rollout status nepreukazuje, že agent na každom Node-e zbiera správne logs alebo že CNI dataplane funguje.

## OnDelete update

Pri `OnDelete` sa existujúce Pods automaticky nenahradia po zmene template. Nová revision sa použije až keď sa Pod odstráni alebo Node zmení.

```yaml
spec:
  updateStrategy:
    type: OnDelete
```

Tento model umožňuje ručne kontrolovať poradie, ale vytvára dlhodobé mixed generations. Potrebuje presný inventory Pod image IDs a Node coverage.

## Priority a kritické add-ons

Node-level agent môže potrebovať vysokú PriorityClass, aby sa scheduloval aj pri tlaku na kapacitu. Priority však nevytvára resources; môže viesť k preemption iných workloadov.

Pre CNI, DNS alebo storage components treba navrhnúť bootstrap poradie. Ak nový Node potrebuje CNI DaemonSet na Pod networking, ale CNI Pod sám závisí od network pathu, platforma potrebuje host-network alebo bootstrap mechanizmus podľa implementácie.

## Node replacement a DaemonSet readiness

Pri immutable Node pool replacement-e je nový Node pripravený pre application workloads až po kritických DaemonSetoch: CNI, CSI, observability, security a prípadne service dataplane.

```text
Node registered
→ critical DaemonSet Pods scheduled
→ network/storage agents initialized
→ Node capability canary
→ až potom workload scheduling
```

`Node Ready=True` nemusí dokazovať, že všetky required platform agents dokončili vlastnú inicializáciu. Node admission alebo taint removal môže byť naviazaný na samostatnú capability verification.

## Incident: nový Node pool nemal log collector

Nové Nodes používali label `node-role.atlas.example/worker=true`, ale DaemonSet selector očakával starý label `node-role.kubernetes.io/worker`. DaemonSet status bol zelený pre svoj vypočítaný desired set, pretože nové Nodes vôbec nepovažoval za eligible.

Aplikácie na nových Nodes fungovali, no central logs chýbali. Root cause nebol collector process ani backend, ale Node-selection contract.

Oprava aktualizovala versionovaný selector, vykonala rollout a overila per-Node log delivery. Skorší control je expected Node inventory porovnaný s DaemonSet coverage, nie iba `desired=current`.

## Incident: CNI DaemonSet bol Ready, dataplane nie

Nová CNI agent revision označila readiness po štarte processu, ešte pred úplnou synchronizáciou routes a eBPF maps. DaemonSet rollout dokončil a Nodes dostali application Pods. Cross-Node traffic potom intermittentne zlyhával.

Containment cordonovalo novú Node cohortu. Oprava zmenila readiness na skutočný dataplane initialization contract a pridala cross-Node capability canary pred odstránením bootstrap taintu.

## Incident: agent update vyčerpal Node memory

Nový observability agent mal memory request 128 MiB, ale reálne pri cardinality spike používal viac než 1 GiB bez limitu. Keď sa DaemonSet rolloutol na každý Node, spoločne vytvoril cluster-wide pressure a kubelet začal evictovať business Pods.

Root cause nebol jeden Node ani Deployment `payments-api`, ale systematická per-Node amplification. Recovery rollbackla agent revision a obnovila workloads. Skorší control je per-Node resource test, bounded cardinality a staged DaemonSet rollout po malej Node cohort-e.

## Model, ktorý si treba odniesť

DaemonSet realizuje capability coverage nad množinou Nodes. Jeho desired count závisí od Node labels, taints a affinity. Zelený count nepreukazuje správne expected Node inventory ani funkčnosť poskytovanej capability. Pri návrhu spájaj Node generation, DaemonSet revision, Pod image ID, privilege boundary a reálny node-level outcome.

## Referencie

- [DaemonSet](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/)
- [Taints and Tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/)
- [Assigning Pods to Nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
