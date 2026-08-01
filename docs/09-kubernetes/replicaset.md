# ReplicaSet

ReplicaSet udržiava požadovaný počet Podov z jedného Pod template-u. Je vhodný pre zameniteľné repliky: ak jedna replika zmizne, controller vytvorí inú. ReplicaSet však nerobí riadený prechod medzi aplikačnými revíziami. Túto vrstvu zvyčajne vlastní Deployment, ktorý vytvára nový ReplicaSet pri zmene template-u.

V našom scenári Deployment generation 12 vytvorí ReplicaSet s template hashom pre release `payments-api 4.2.0`. ReplicaSet chce šesť aktívnych Podov. Jeho úlohou nie je overiť payment correctness, ale udržať count a owner graph.

## Selector musí presne zodpovedať template-u

Minimalistický ReplicaSet vyzerá takto:

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: payments-api-7d6f9d8b7b
  namespace: production
spec:
  replicas: 6
  selector:
    matchLabels:
      app: payments-api
      pod-template-hash: 7d6f9d8b7b
  template:
    metadata:
      labels:
        app: payments-api
        pod-template-hash: 7d6f9d8b7b
    spec:
      containers:
        - name: api
          image: registry.example.com/atlas/payments-api@sha256:payments420
```

Selector určuje, ktoré Pods ReplicaSet považuje za svoje candidates. Template labels musia selector spĺňať. Príliš široký selector môže zasiahnuť ručne vytvorený Pod alebo Pod iného controllera.

OwnerReference je silnejší lifecycle signál než samotný label. Controller pri adoption a release decisions používa pravidlá, ktoré treba chápať opatrne; ručný Pod s rovnakými labels môže byť nečakane zahrnutý do countu.

## Count reconciliation

ReplicaSet opakovane porovnáva desired počet s aktívnymi Pods.

```text
desired=6, observed=4
→ vytvor 2 Pods

desired=6, observed=8
→ vyber 2 Pods na odstránenie
```

Controller nečaká, že všetkých šesť Podov bude healthy. Count sa týka objektov a ich lifecycle state-u podľa controller pravidiel. Readiness a application outcome sú ďalšie vrstvy.

```bash
kubectl get rs -n production -l app=payments-api
kubectl get pods -n production -l pod-template-hash=7d6f9d8b7b
```

Stĺpce `DESIRED`, `CURRENT` a `READY` odpovedajú na rozdielne otázky. `CURRENT=6` neznamená `READY=6`.

## ReplicaSet a Deployment ownership

Bežný production ReplicaSet vytvára Deployment. Jeho ownerReference ukazuje na Deployment UID.

```bash
kubectl get rs -n production <rs-name> \
  -o jsonpath='{.metadata.ownerReferences}' | jq .
```

Ručná zmena ReplicaSet template-u alebo replica countu obchádza Deployment authority. Deployment controller môže zmenu neskôr upraviť alebo vytvoriť neočakávaný rollout state.

Ak potrebujeme zmeniť release, upravujeme Deployment template. Ak potrebujeme dočasne škálovať Deployment bez HPA, meníme Deployment replicas, nie child ReplicaSet.

## Template hash a revision identity

Deployment typicky vytvára ReplicaSet s labelom `pod-template-hash`. Hash pomáha odlíšiť Pod template revisions a zabrániť overlapu selectors.

Hash nie je release artifact digest. Rovnaký image digest s inou environment hodnotou vytvorí inú template revision. Naopak mutable image tag môže ukazovať na iný artifact bez zmeny template stringu a hash sa nezmení.

Pre release evidence preto sleduj:

```text
Deployment generation
+ ReplicaSet UID
+ template hash
+ admitted Pod template
+ resolved image digest v Pode/runtime
```

## Scale up a scale down

Pri scale-up ReplicaSet vytvára nové Pods. Scheduler a kubelety ich realizujú. Pri scale-down controller vyberie Pods na odstránenie podľa dostupných pravidiel a annotations.

Scale-down nie je application drain policy. Pod termination a Service endpoint removal musia správne spolupracovať s readiness, grace period a aplikáciou.

```bash
kubectl scale deployment payments-api -n production --replicas=8
```

Tento príkaz v bežnom modeli mení Deployment replicas. Ak HPA vlastní scale subresource, ručný scale môže byť pri ďalšom HPA reconcile prepísaný.

## Pod adoption a orphaning

Ak Pod spĺňa selector ReplicaSetu a nemá konfliktného controllera, ReplicaSet ho môže adoptovať. Pri delete s orphan propagation môžu child Pods zostať bez ownera.

To je dôvod, prečo produkčné selectors musia byť jednoznačné a ručné experimenty nemajú používať rovnaké labels v rovnakom namespace.

```bash
kubectl get pods -n production -l app=payments-api \
  -o custom-columns='NAME:.metadata.name,OWNER_KIND:.metadata.ownerReferences[0].kind,OWNER_UID:.metadata.ownerReferences[0].uid'
```

## Failure: desired count sedí, ale kapacita nie

ReplicaSet môže mať šesť Pod objektov, no iba tri Ready. Controller count splnil. Dôvodom môže byť scheduling, image pull, crash, probe alebo dependency failure.

```bash
kubectl get rs -n production <rs-name> -o yaml
kubectl get pods -n production -l pod-template-hash=<hash> -o wide
```

Ak `replicas=6`, `readyReplicas=3`, nehľadaj automaticky chybu v ReplicaSet controlleri. Rozdeľ Pods podľa Node-u a reasonu.

## Failure: selector zachytil debug Pod

Operátor vytvoril debug Pod s labelom `app=payments-api`. ReplicaSet selector bol iba tento jeden label. Controller započítal debug Pod do desired countu a odstránil jednu production repliku pri scale-down rozhodnutí. Service selector zároveň poslal traffic na debug Pod.

Oprava zaviedla jednoznačné labels vrátane component a template identity, debug namespace a policy zakazujúcu kolidujúce labels. Recovery overila owner graph aj EndpointSlice backends.

## Failure: ručne škálovaný ReplicaSet sa vrátil späť

Tím znížil child ReplicaSet na nulu, aby zastavil chybný release. Deployment controller ho pri ďalšom reconcile znovu škáloval podľa rollout state-u.

Správne containment rozhodnutie bolo pause Deploymentu alebo zmena top-level desired state-u, prípadne odstránenie trafficu cez samostatný control. Child mutation nebola autoritatívna.

## Model, ktorý si treba odniesť

ReplicaSet udržiava počet Podov jednej template revision. Zameniteľnosť replík, presný selector a owner graph sú jeho jadrom. Nevykonáva rollout medzi revíziami a neoveruje business readiness. V production ho preto čítame ako child Deploymentu a troubleshooting presúvame na ďalšiu vrstvu podľa toho, či chýbajú Pod objekty alebo iba ich runtime readiness.

## Referencie

- [ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)
- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Labels and Selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Pod](pod.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Deployment →](deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
