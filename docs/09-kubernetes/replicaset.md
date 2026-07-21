# ReplicaSet

ReplicaSet je Kubernetes workload controller, ktorý udržiava požadovaný počet navzájom zameniteľných Podov zodpovedajúcich label selectoru. Jeho úlohou nie je vykonávať rollout novej verzie aplikácie, ale priebežne vyrovnávať rozdiel medzi `.spec.replicas` a počtom aktívnych matching Podov.

V bežnej prevádzke ReplicaSet typicky nevytvára človek priamo. Vlastní ho Deployment, ktorý používa viac ReplicaSetov na revision history a rolling update.

## 1. Základný mentálny model

```text
ReplicaSet spec
  replicas: 3
  selector: app=web,version=v1
  template: Pod v1
          ↓ reconcile
matching Pods: 2
          ↓
controller vytvorí 1 nový Pod
```

ReplicaSet neudržiava konkrétne Pod UID. Udržiava **počet Podov**, ktoré zodpovedajú selectoru a patria do jeho control scope-u.

## 2. Minimálny manifest

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: web-v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
      version: v1
  template:
    metadata:
      labels:
        app: web
        version: v1
    spec:
      containers:
        - name: web
          image: registry.example.com/web@sha256:...
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
```

`spec.selector` musí zodpovedať labelom v `spec.template.metadata.labels`. Inak API server objekt odmietne alebo controller nebude riadiť očakávané Pody.

## 3. Selector je control boundary

ReplicaSet používa label selector na zistenie, ktoré Pody patria do jeho desired replica setu.

Podstatné dôsledky:

- selector nie je iba query filter,
- prekrývajúce sa selectory dvoch controllerov sú nebezpečné,
- nezávisle vytvorený Pod so zodpovedajúcimi labelmi môže byť adoptovaný,
- zmena labels na Pode môže spôsobiť, že ReplicaSet vytvorí náhradu,
- selector ReplicaSetu je po vytvorení prakticky immutable API contract.

Selectors navrhuj ako stabilné a jednoznačné identity workloadu, nie ako dočasný operátorský filter.

## 4. Pod template

`spec.template` je šablóna pre nové Pody. Zmena template-u na samostatnom ReplicaSete nezabezpečuje bezpečný rolling update existujúcich Podov.

Existujúce Pody sa automaticky „neprepíšu“. ReplicaSet ich považuje za vhodné, pokiaľ stále zodpovedajú selectoru a počtu replík.

Pre deklaratívne rollouty používaj Deployment:

```text
Deployment revision
      ↓
nový ReplicaSet
      ↓
nové Pody
```

## 5. Reconciliation

ReplicaSet controller opakovane:

1. číta ReplicaSet a matching Pody,
2. vyhodnotí active/terminating/failed stav,
3. porovná observed count s `.spec.replicas`,
4. vytvorí chýbajúce Pody alebo vyberie Pody na deletion,
5. aktualizuje status a conditions,
6. opakuje postup pri ďalšej udalosti alebo resyncu.

Reconciliation je level-based. Ak controller dočasne vypadne, po obnove znovu vypočíta rozdiel z aktuálneho stavu.

## 6. Vytvorenie Podu

Nový Pod dostane:

- labels z template-u,
- owner reference na ReplicaSet,
- nový name/UID,
- celý Pod spec z template-u.

ReplicaSet nevykonáva scheduling ani container start. Iba vytvorí Pod object. Scheduler ho pridelí Node-u a kubelet realizuje runtime stav.

## 7. Replacement nie je restart

Ak Pod zanikne alebo prestane patriť do selectoru, ReplicaSet vytvorí **nový Pod**:

- s novým UID,
- potenciálne na inom Node-e,
- s novou Pod IP,
- bez pôvodnej writable layer,
- s novým lifecycle.

Kubelet restartuje containers v rámci toho istého Podu podľa `restartPolicy`. ReplicaSet rieši replacement celého Pod objectu.

## 8. Scale

```bash
kubectl scale replicaset web-v1 --replicas=5
kubectl get rs web-v1
```

Pri scale-up ReplicaSet vytvára ďalšie Pody. Pri scale-down vyberá Pody na odstránenie podľa controller logic; aplikácia nesmie predpokladať, že zostane konkrétna Pod identity.

Ručný scale ReplicaSetu vlastneného Deploymentom môže byť neskôr prepísaný Deployment controllerom alebo HPA. Meníš nesprávnu vrstvu desired state-u.

## 9. Status

```bash
kubectl get rs
kubectl describe rs web-v1
kubectl get rs web-v1 -o yaml
```

Dôležité fields:

- `spec.replicas` — požadovaný počet,
- `status.replicas` — pozorované repliky,
- `status.fullyLabeledReplicas`,
- `status.readyReplicas`,
- `status.availableReplicas`,
- `status.observedGeneration`,
- conditions a Events.

`replicas=3` neznamená automaticky tri Ready alebo Available Pody.

## 10. Ready a Available

ReplicaSet rozlišuje existenciu Podu od jeho použiteľnosti.

Pod môže byť:

- vytvorený, ale `Pending`,
- `Running`, ale `Ready=False`,
- Ready, ale ešte nespĺňa availability timing vyššej vrstvy,
- terminating a stále dočasne spotrebúva resources.

Service routing typicky používa readiness cez EndpointSlice, nie samotný ReplicaSet count.

## 11. Adoption a orphaning

Controller môže adoptovať matching Pod bez controller owner reference, ak spĺňa ownership podmienky.

Pri deletion možno podľa propagation policy:

- odstrániť ReplicaSet aj dependent Pody,
- orphanovať Pody a ponechať ich bez pôvodného ownera.

Orphaned matching Pody môže následne adoptovať vhodný controller. Toto je citlivá operácia; prekrývajúce selectors môžu vytvoriť nepredvídateľný ownership race.

## 12. Owner references

ReplicaSet vytvára Pody s `ownerReferences`, kde je spravidla `controller: true`.

Deployment zas vlastní ReplicaSet:

```text
Deployment
  └─ ReplicaSet
       └─ Pods
```

Garbage collection a rollout diagnostika preto začínajú kontrolou ownership chainu.

```bash
kubectl get pod <pod> -o jsonpath='{.metadata.ownerReferences}'
kubectl get rs <rs> -o jsonpath='{.metadata.ownerReferences}'
```

## 13. Deployment ako odporúčaná vyššia vrstva

Deployment poskytuje nad ReplicaSetom:

- revision history,
- rolling update alebo recreate stratégiu,
- rollout status,
- pause/resume,
- rollback,
- riadené scale-up/scale-down starých a nových ReplicaSetov.

Pri stateless aplikácii preto vytváraj Deployment, nie samostatný ReplicaSet, pokiaľ vedome nepotrebuješ vlastnú update orchestration.

## 14. Failure scenáre

### Desired 3, current 2

ReplicaSet vytvorí ďalší Pod. Ak nový Pod ostáva Pending, počet objects môže byť správny, ale služba nie je dostupná.

### Desired 3, current 4

Controller odstráni prebytočný Pod. Graceful termination môže dočasne znamenať, že cluster stále spotrebúva resources pre viac než desired count.

### Pody existujú, ale selector ich nevidí

Over labels a selector. Controller môže vytvárať ďalšie Pody a pôvodné zostať bez správneho ownerstva.

### `FailedCreate`

Over Events, admission, quota, PodSecurity, ServiceAccount, image pull secrets, invalid Pod spec a API dependencies.

### Pody sa stále obnovujú

ReplicaSet iba plní desired count. Root cause je často v Pod template-e, probe, config, resource limite alebo runtime dependency.

## 15. Anti-patterny

### Priamy ReplicaSet pre bežnú web aplikáciu

Chýba bezpečný rollout a revision management.

### Editovanie Podu namiesto template-u

Replacement Pod znovu použije template a ručná oprava zanikne.

### Scale ReplicaSetu vlastneného Deploymentom

Desired state vlastní vyšší controller.

### Prekrývajúce sa selectors

Controllers môžu bojovať o tie isté Pody.

### Selector obsahuje rollout-mutable hodnotu bez higher-level modelu

Zmena identity vedie k novej skupine, nie k riadenému update-u.

### Replica count považovaný za availability

Existencia objectov nepreukazuje Ready endpoints ani funkčnú aplikáciu.

## 16. Troubleshooting

```bash
kubectl get rs -o wide
kubectl describe rs <name>
kubectl get pods -l app=web,version=v1 -o wide
kubectl get pod <pod> -o yaml
kubectl get events --sort-by=.metadata.creationTimestamp
```

Postup:

1. over selector a template labels,
2. over owner references,
3. porovnaj desired/current/ready/available,
4. čítaj ReplicaSet Events,
5. diagnostikuj konkrétne Pody,
6. skontroluj higher-level Deployment alebo HPA,
7. over admission, quota a scheduler capacity.

## 17. Kontrolné otázky

1. Aký stav ReplicaSet skutočne udržiava?
2. Prečo selector tvorí control boundary?
3. Čo sa stane po zmazaní jedného Podu?
4. Ako sa líši container restart od Pod replacementu?
5. Prečo sa Pod template update samostatného ReplicaSetu nerovná rolloutu?
6. Ako funguje adoption?
7. Prečo sú prekrývajúce selectors nebezpečné?
8. Aký je ownership chain Deployment → ReplicaSet → Pod?
9. Prečo `status.replicas` nie je availability metrika?
10. Kedy má zmysel použiť ReplicaSet priamo?

## Glossary impact

Relevantné pojmy: ReplicaSet, desired replicas, current replicas, ready replicas, available replicas, Pod selector, Pod adoption, orphaned Pod, controller owner reference, replacement Pod a overlapping selectors.

## Oficiálna dokumentácia

- [ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)
- [Workload management](https://kubernetes.io/docs/concepts/workloads/controllers/)
- [Garbage collection](https://kubernetes.io/docs/concepts/architecture/garbage-collection/)
