# Deployment

Deployment je vyšší Kubernetes workload controller pre deklaratívne riadenie stateless alebo navzájom zameniteľných Podov. Nevytvára Pody priamo. Vytvára a škáluje ReplicaSety, ktoré následne vytvárajú Pody.

Hlavná hodnota Deploymentu je riadený prechod medzi starou a novou Pod template revision s rollout statusom, availability constraints, history a rollback mechanizmom.

## 1. Ownership model

```text
Deployment web
  ├─ ReplicaSet web-7d9f...  revision 3, replicas 3
  └─ ReplicaSet web-648c...  revision 2, replicas 0
         ↓
       Pods
```

Každá relevantná zmena `.spec.template` vytvorí novú Deployment revision a typicky nový ReplicaSet.

## 2. Minimálny manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: registry.example.com/web@sha256:...
          ports:
            - containerPort: 8080
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
```

Selector musí zodpovedať template labelom a po vytvorení je zásadnou immutable identity boundary.

## 3. Čo spúšťa rollout

Rollout spúšťa zmena Pod template-u, napríklad:

- image reference,
- command/args,
- environment,
- Pod labels alebo annotations,
- probes,
- resources,
- volumes,
- security context.

Zmena iba Deployment fields mimo template-u, napríklad `.spec.replicas`, nevytvára novú revision.

Ak používaš mutable image tag bez zmeny template-u, Kubernetes nemusí vytvoriť rollout. Digest pinning alebo explicitná version annotation zlepšuje identitu rollout-u.

## 4. RollingUpdate

Default stratégia je typicky `RollingUpdate`:

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```

Deployment controller:

1. vytvorí nový ReplicaSet,
2. postupne ho scale-upuje,
3. sleduje readiness a availability,
4. postupne scale-downuje starý ReplicaSet,
5. dokončí rollout pri splnení desired state-u.

### `maxUnavailable`

Maximálny počet alebo percento desired replík, ktoré môžu byť počas update nedostupné.

### `maxSurge`

Maximálny počet alebo percento Podov nad desired replica count počas update.

Availability a capacity sa preto plánujú spolu. Surge potrebuje voľné Node resources.

## 5. Recreate

```yaml
spec:
  strategy:
    type: Recreate
```

Staré Pody sa odstránia pred vytvorením nových.

Použitie:

- workload nepodporuje mixed-version overlap,
- single-writer alebo port/resource constraint,
- downtime je prijateľný,
- databázová alebo protocol compatibility neumožňuje rolling coexistence.

`Recreate` nie je automaticky bezpečný pre state. Rieši iba Pod replacement order.

## 6. Availability

Deployment status rozlišuje:

- desired replicas,
- updated replicas,
- ready replicas,
- available replicas,
- unavailable replicas,
- terminating replicas podľa podporovanej API/feature konfigurácie,
- conditions `Progressing` a `Available`.

`Ready=True` je vstup do availability, ale `.spec.minReadySeconds` môže vyžadovať, aby Pod zostal Ready určitý čas.

```yaml
spec:
  minReadySeconds: 20
```

To znižuje riziko, že krátko Ready a následne padajúci Pod bude okamžite považovaný za stabilnú náhradu.

## 7. Progress deadline

```yaml
spec:
  progressDeadlineSeconds: 600
```

Ak Deployment v limite nepostupuje, status môže dostať condition s dôvodom `ProgressDeadlineExceeded`.

Dôležité:

- controller neuskutoční automatický rollback iba preto, že deadline vypršal,
- deployment systém alebo operator musí rozhodnúť o pause, rollbacku alebo roll-forward,
- deadline má byť dlhší než reálny startup a minReady profil.

## 8. Rollout commands

```bash
kubectl rollout status deployment/web --timeout=10m
kubectl rollout history deployment/web
kubectl rollout undo deployment/web
kubectl rollout pause deployment/web
kubectl rollout resume deployment/web
kubectl get deployment web -o yaml
```

Rollback používa zachovanú ReplicaSet revision history. Nie je bezpečný, ak nová verzia vykonala nekompatibilnú databázovú alebo external-state zmenu.

## 9. Revision history

```yaml
spec:
  revisionHistoryLimit: 5
```

Staré ReplicaSety s nulovým počtom replík uchovávajú Pod template revisions.

Trade-off:

- vyšší limit uľahčuje rollback a audit,
- príliš veľa revisions zvyšuje API clutter,
- limit `0` odstráni možnosť Deployment rollbacku cez staré ReplicaSety.

Revision history nie je náhrada za source control, artifact retention ani database recovery.

## 10. Pause a resume

Pri paused Deploymente možno meniť Pod template bez okamžitého vytvorenia viacerých čiastkových rolloutov.

```bash
kubectl rollout pause deployment/web
kubectl set image deployment/web web=registry.example.com/web@sha256:...
kubectl patch deployment/web --patch-file resources.yaml
kubectl rollout resume deployment/web
```

Pause nepozastaví už bežiace Pody ani automaticky nezmrazí HPA alebo external writers.

## 11. Scaling a HPA

```bash
kubectl scale deployment web --replicas=5
```

Ak Deployment škáluje HPA, ručná zmena `.spec.replicas` môže byť rýchlo prepísaná.

Pri GitOps/HPA modeli musí byť jasné:

- kto vlastní replica field,
- či manifest obsahuje `.spec.replicas`,
- ako sa rieši field ownership,
- ako rollout ovplyvní capacity metrics.

## 12. Readiness a traffic

Deployment môže byť rolloutovo „aktívny“, kým nové Pody ešte nie sú Ready. Service/EndpointSlice typicky posiela traffic iba Ready endpointom.

Správna readiness probe preto tvorí rollout safety signal.

Chybná readiness:

- príliš plytká — traffic ide na nefunkčný Pod,
- príliš závislá od external systému — všetky Pody sa odpoja pri dependency incidente,
- príliš pomalá — rollout zbytočne stagnuje,
- nestabilná — spôsobuje flapping a capacity loss.

## 13. Termination a surge

Pri rollout-e môže dočasne existovať viac procesov než `replicas + maxSurge`, ak terminating Pody ešte spotrebúvajú resources a status/API ich nezapočítava rovnakým spôsobom ako active replicas.

Plánuj:

- `terminationGracePeriodSeconds`,
- `preStop`,
- connection draining,
- load balancer endpoint removal,
- Node capacity pre surge aj termination overlap.

## 14. PodDisruptionBudget

PDB môže obmedzovať voluntary disruptions, ale Deployment rollout a PDB majú rozdielne semantics. PDB nie je rollout strategy a nechráni pred všetkými failures.

Over kombináciu:

- Deployment `maxUnavailable`,
- PDB `minAvailable` alebo `maxUnavailable`,
- replica count,
- Node drain,
- topology spread,
- readiness behavior.

Nesprávna kombinácia môže blokovať maintenance alebo znižovať dostupnosť.

## 15. Update safety

Rolling update predpokladá, že stará a nová verzia môžu určitý čas koexistovať.

Over:

- API backward/forward compatibility,
- database expand-contract,
- event schema compatibility,
- session handling,
- cache format,
- background workers,
- feature flags,
- shared filesystem/data semantics.

Kubernetes rieši replica orchestration, nie application compatibility.

## 16. Observability

```bash
kubectl get deployment web
kubectl describe deployment web
kubectl get rs -l app=web
kubectl get pods -l app=web -o wide
kubectl rollout status deployment/web
kubectl get events --sort-by=.metadata.creationTimestamp
```

Sleduj:

- `metadata.generation` vs. `status.observedGeneration`,
- desired/updated/ready/available/unavailable replicas,
- Deployment conditions,
- nový a starý ReplicaSet,
- Pod readiness a restart count,
- scheduler/image/probe/volume Events,
- application SLI per revision.

## 17. Failure scenáre

### Rollout stojí na `0/3 available`

Over new ReplicaSet Pody, scheduling, image pull, startup, readiness, config, mounts a admission.

### `ProgressDeadlineExceeded`

Je to status evidence, nie automatická náprava. Urči, či rollback alebo roll-forward je bezpečnejší.

### Starý ReplicaSet sa nescale-downuje

Over readiness/availability nových Podov, PDB, terminating Pody a controller Events.

### Nová verzia funguje iba na časti Podov

Porovnaj image IDs, config, Node architecture, zones, traffic segmenty a revision-specific telemetry.

### Rollback obnoví Pody, ale služba stále nefunguje

State/schema alebo external dependency už nemusí byť kompatibilná so starou aplikáciou.

## 18. Anti-patterny

### Editovanie ReplicaSetu vlastneného Deploymentom

Deployment ho v ďalšom reconcile zmení alebo nahradí.

### Mutable tag bez jasnej rollout identity

Rovnaká template môže viesť k rozdielnemu contentu na Nodes.

### `kubectl rollout undo` považované za univerzálny recovery plán

Nevracia databázu, queues ani external state.

### Readiness `true` hneď po štarte

Rollout môže scale-downovať starú kapacitu skôr, než je nová verzia použiteľná.

### `maxUnavailable: 0` bez surge capacity

Rollout môže ostať Pending, ak cluster nemá miesto pre nový Pod.

### Deployment pre workload vyžadujúci stabilnú per-replica identity

Použi StatefulSet alebo iný vhodný controller.

## 19. Kontrolné otázky

1. Prečo Deployment nevytvára Pody priamo?
2. Ktoré zmeny spúšťajú novú revision?
3. Ako sa líšia `maxSurge` a `maxUnavailable`?
4. Čo znamená available replica?
5. Čo `ProgressDeadlineExceeded` urobí a neurobí?
6. Ako funguje revision history?
7. Prečo rollback nemusí byť bezpečný po databázovej migrácii?
8. Ako readiness ovplyvňuje rollout?
9. Ako HPA mení ownership `.spec.replicas`?
10. Kedy použiť `Recreate` namiesto `RollingUpdate`?

## Glossary impact

Relevantné pojmy: Deployment, Deployment revision, rolling update, Recreate strategy, `maxSurge`, `maxUnavailable`, updated replicas, available replicas, `minReadySeconds`, progress deadline, revision history, paused Deployment a rollout rollback.

## Oficiálna dokumentácia

- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Managing workloads](https://kubernetes.io/docs/concepts/workloads/management/)
- [Pod disruption budgets](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)
