# Deployment

Deployment riadi prechod medzi revíziami zameniteľných Podov. Neštartuje containers priamo. Pri zmene `.spec.template` vytvorí nový ReplicaSet, postupne mu pridáva kapacitu a znižuje starý ReplicaSet. Deployment preto treba chápať ako controller výmeny revízií, nie ako obyčajný počet replík.

Pre `payments-api` nasadzujeme release `4.2.0`. Starý ReplicaSet používa digest `sha256:payments410`, nový digest `sha256:payments420`. Počas rolling update-u môžu obe revízie krátko prijímať traffic, takže aplikácia, databáza, events aj configuration musia byť kompatibilné v overlap období.

## Deployment manifest ako rollout contract

Základný manifest:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payments-api
  namespace: production
spec:
  replicas: 6
  revisionHistoryLimit: 5
  progressDeadlineSeconds: 600
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2
      maxUnavailable: 1
  selector:
    matchLabels:
      app: payments-api
  template:
    metadata:
      labels:
        app: payments-api
    spec:
      terminationGracePeriodSeconds: 45
      containers:
        - name: api
          image: registry.example.com/atlas/payments-api@sha256:payments420
          ports:
            - name: http
              containerPort: 8080
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
            periodSeconds: 5
          resources:
            requests:
              cpu: 250m
              memory: 256Mi
            limits:
              cpu: "1"
              memory: 512Mi
```

Selector je po vytvorení zásadná identita controlleru. Template labels ho musia spĺňať. Image digest, probes, resources, environment, volumes a security context patria do Pod template-u; ich zmena vytvorí novú revision.

Zmena `.spec.replicas` sama osebe nevytvára novú application revision. Scale a release sú dve odlišné zmeny.

## Čo vytvorí nový ReplicaSet

Deployment porovnáva aktuálnu Pod template s existujúcimi ReplicaSets. Ak template zodpovedá starej revision, použije ju. Ak je nová, vytvorí nový ReplicaSet s novým template hashom.

```bash
kubectl get deployment payments-api -n production \
  -o custom-columns='GEN:.metadata.generation,OBSERVED:.status.observedGeneration,UPDATED:.status.updatedReplicas,READY:.status.readyReplicas,AVAILABLE:.status.availableReplicas'

kubectl get rs -n production -l app=payments-api \
  -o custom-columns='NAME:.metadata.name,DESIRED:.spec.replicas,CURRENT:.status.replicas,READY:.status.readyReplicas,IMAGE:.spec.template.spec.containers[0].image'
```

Deployment name nestačí na release identity. Pri audite sleduj Deployment UID a generation, old/new ReplicaSet UIDs, template hashes a resolved Pod image digest.

## RollingUpdate ako výmena kapacity

Pri `replicas: 6`, `maxSurge: 2` a `maxUnavailable: 1` môže controller dočasne vytvoriť až o dve nové repliky viac a zároveň dovoliť najviac jednu nedostupnú repliku podľa rollout pravidiel.

Zjednodušený cyklus:

```text
vytvor nové Pods v surge limite
→ čakaj na readiness a availability
→ zníž starý ReplicaSet v unavailable limite
→ opakuj
```

Tento mechanizmus funguje iba vtedy, keď cluster má reálnu kapacitu pre surge. Pri `maxUnavailable: 0` a plnom clusteri sa rollout môže zastaviť: starý Pod nemožno odstrániť a nový Pod nemožno schedulovať.

`maxSurge` a `maxUnavailable` sú kapacitný a availability budget. Neoverujú databázovú kompatibilitu ani správnosť payment transakcie.

## Readiness je súčasť rollout controlu

Deployment považuje Pod za dostupný podľa readiness a `minReadySeconds`, ak je nastavený. Ak je readiness príliš plytká, nový Pod začne nahrádzať starú kapacitu skôr, než je aplikácia skutočne pripravená. Ak je príliš prísna alebo závislá od spoločnej zlyhávajúcej služby, môže odpojiť všetky repliky naraz.

```yaml
spec:
  minReadySeconds: 20
```

Táto hodnota vyžaduje, aby Pod zostal Ready bez prerušení aspoň definovaný čas pred započítaním ako available. Pomáha odhaliť okamžité post-start zlyhania, ale nie je to dlhý soak test.

Rollout status:

```bash
kubectl rollout status deployment/payments-api -n production --timeout=10m
```

Úspešný príkaz znamená, že Deployment controller dosiahol svoj rollout condition. Neznamená automaticky úspešný external request, správny secret epoch alebo zero duplicate payments.

## Progress deadline

`progressDeadlineSeconds` určuje, kedy controller označí rollout ako bez progressu. Deployment môže dostať condition s reason `ProgressDeadlineExceeded`.

```bash
kubectl get deployment payments-api -n production \
  -o jsonpath='{range .status.conditions[*]}{.type}{"="}{.status}{" reason="}{.reason}{"\n"}{end}'
```

Kubernetes Deployment sám automaticky nevykoná business rollback iba preto, že deadline uplynul. Release automation alebo operátor musí rozhodnúť, či rollout pause-ne, opraví novou revision alebo vráti starú revision.

## Pause a resume

Deployment možno pozastaviť:

```bash
kubectl rollout pause deployment/payments-api -n production
```

Počas pause možno pripraviť viac zmien template-u bez spustenia každej medzirevízie. Resume potom začne realizovať výslednú template.

```bash
kubectl rollout resume deployment/payments-api -n production
```

Pause nie je traffic stop. Existujúce Pods a Service pokračujú. Ak potrebujeme okamžité containment, potrebujeme samostatný traffic alebo feature control podľa incidentu.

## Rollback a revision history

Deployment udržiava staré ReplicaSets podľa `revisionHistoryLimit`. História umožňuje:

```bash
kubectl rollout history deployment/payments-api -n production
kubectl rollout undo deployment/payments-api -n production --to-revision=<n>
```

Rollback vytvorí novú Deployment generation s predchádzajúcou Pod template. Nie je to návrat celého sveta v čase. Databázová schema, external events, secrets alebo cloud state sa automaticky nevrátia.

Pred rollbackom treba overiť, či stará application revision stále rozumie aktuálnym dátam a contracts. Pri expand/contract databázových zmenách môže byť artifact rollback bezpečný iba počas definovaného compatibility okna.

## Recreate stratégia

Pri `strategy.type: Recreate` sa staré Pods odstránia pred vytvorením nových. To vytvára očakávané okno bez replík.

```yaml
strategy:
  type: Recreate
```

Recreate je vhodný iba vtedy, keď application contract neumožňuje overlap a outage je akceptovaný alebo pokrytý vyššou vrstvou. Ani Recreate však negarantuje, že starý process už nepôsobí v externom systéme pri partitioned Node-e; stateful writer môže potrebovať fencing.

## Apply a field ownership

Versionovaný rollout má používať server-side apply alebo iný jasný ownership model:

```bash
kubectl apply --server-side \
  --field-manager=atlas-release \
  -f deployment.yaml
```

Ak HPA vlastní replicas, manifest nemá neustále vynucovať rovnaké pole. Ak secret reloader pridáva checksum annotation, jeho ownership musí byť kompatibilný s GitOps managerom.

Pred mutation:

```bash
kubectl apply --server-side --dry-run=server \
  --field-manager=atlas-release \
  -f deployment.yaml -o yaml
```

Dry-run ukáže admitted template, ale nevytvorí nový ReplicaSet.

## Rollout evidence po vrstvách

Rozumná kontrola ide od controller state-u k business výsledku:

```bash
kubectl get deployment payments-api -n production -o yaml
kubectl get rs -n production -l app=payments-api -o wide
kubectl get pods -n production -l app=payments-api -o wide
kubectl get endpointslices -n production \
  -l kubernetes.io/service-name=payments-api -o yaml
```

Potom over image a config na konkrétnych Pods:

```bash
kubectl get pods -n production -l app=payments-api \
  -o custom-columns='NAME:.metadata.name,HASH:.metadata.labels.pod-template-hash,IMAGE:.spec.containers[0].image,IMAGE_ID:.status.containerStatuses[0].imageID,READY:.status.containerStatuses[0].ready'
```

Napokon vykonaj syntetický request cez Service alebo edge path a koreluj payment ID v downstream ledgeri.

## Mixed-version overlap

Rolling update znamená, že old a new revision môžu bežať súčasne. Musia zvládnuť:

```text
rovnakú databázovú schema
rovnaký event stream
rovnaký cache namespace alebo versioning
spoločné session/token formáty
spoločné Service contracty
```

Ak nová verzia publikuje event, ktorý stará nevie čítať, rollout sa môže poškodiť ešte pred dokončením. Deployment controller takúto business nekompatibilitu nepozná.

## Terminating Pods a reálna kapacita

Pri scale-down dostane starý Pod deletion timestamp a začne termination. Môže ešte chvíľu spotrebúvať CPU, memory, connections a volume attachment. Nové Pods zároveň využívajú surge kapacitu. Reálny peak môže byť vyšší než `replicas + maxSurge`, ak terminating workloads zostávajú dlhšie aktívne v host resources.

Dlhé `terminationGracePeriodSeconds` chráni in-flight requests, ale spomaľuje rollout a zvyšuje overlap. Príliš krátke okno môže prerušiť payment po external authorization, ale pred lokálnym commitom.

## Incident: rollout complete, ale časť requestov používa starý secret

Deployment hlásil complete a všetkých šesť Podov bolo Ready. Tri Pods však vznikli pred secret rotation a tri po nej, pretože Secret sa používal cez environment a template sa pri rotácii nezmenila.

Deployment controller nevidel novú revision. Staré Pods pokračovali s credential epoch `SE07`, nové s `SE08`. Databáza ešte krátko prijímala obe, takže readiness bola zelená, no po revokácii SE07 vznikli intermittent failures.

Oprava pridala explicitný secret checksum alebo versionovanú Secret reference do Pod template-u. Rotation lifecycle sa zmenil na: vytvor novú credential generation, rolloutni všetky Pods, over process-loaded epoch, potom revokuj starú.

## Incident: rollout sa zastavil bez chyby v aplikácii

`maxUnavailable: 0`, `maxSurge: 1` a desired replicas 6. Cluster nemal žiadnu voľnú memory request kapacitu a autoscaler nemohol pridať Node pre quota limit. Nový Pod zostal Pending. Staré Pods boli zdravé, preto Deployment nemohol odstrániť žiadnu repliku.

Riešením nebolo znižovať readiness. Tím dočasne zvýšil cluster capacity a neskôr pridal pre-release capacity gate. Rollout pokračoval po schedulovaní nového Podu.

## Incident: rollback obnovil Pods, ale nie business kompatibilitu

Release `4.2.0` začal zapisovať nový event field, ktorý consumer `4.1.0` nepoznal. Po rollbacku Deployment opäť spustil starý image, ale queue už obsahovala nové events. Pods boli Ready a rollout complete, no processing zlyhával.

Recovery vyžadovala roll-forward kompatibilným consumerom a reconciliation backlogu. Skorší control je schema evolution a mixed-version test, nie slepá dôvera v Deployment revision history.

## Model, ktorý si treba odniesť

Deployment je controller výmeny Pod template revízií cez ReplicaSets. RollingUpdate riadi kapacitu a dostupnosť, nie business kompatibilitu. Správny release verdict spája Deployment generation, old/new ReplicaSet identity, ready endpointy, resolved image/config a reálny používateľský outcome. Rollback je iba ďalšia template transition a musí byť kompatibilný s aktuálnymi dátami a external state-om.

## Referencie

- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Performing a Rolling Update](https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/)
- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: ReplicaSet](replicaset.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: StatefulSet →](statefulset.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
