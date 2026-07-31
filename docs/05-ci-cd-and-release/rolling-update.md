# Rolling update

Rolling update postupne vymieňa starú runtime fleet za novú. Dostupnosť sa zachováva tým, že určitý čas existujú obe generations súčasne. Práve mixed-version interval je hlavná failure boundary: old a new code musia bezpečne zdieľať API, database, events, caches, sessions, queues a external dependencies.

Rolling strategy nie je iba hodnota `maxSurge` a `maxUnavailable`. Je to controller state machine, ktorá potrebuje healthy baseline, capacity headroom, readiness contract, stable traffic eligibility, drain semantics a shared-state compatibility. Ak fleet už pred rolloutom nemá desired healthy capacity, percent-based limits môžu vytvoriť väčší outage než tím očakáva.

## 1. Dominantný batch-exchange model

```text
healthy old fleet a compatible shared state
→ create bounded new batch
→ startup, functional readiness a capacity validation
→ add new batch do eligible endpointov
→ observe technical a business cohort
→ remove/drain bounded old batch
→ repeat exchange
→ full new fleet observation
→ old ReplicaSet/runtime retirement
```

Controller readiness je iba jedna condition. New Pod môže byť Ready, ale používať wrong secret generation alebo emitovať incompatible events. Old Pod môže byť removed z Service, ale stále dokončovať in-flight request. Acceptance musí sledovať workload aj operation lifecycle.

## 2. Exact rolling subject

```yaml
rollingSubject:
  workload: payments-api
  releaseManifestDigest: sha256:release1000rc4
  oldRevision:
    deploymentRevision: 280
    artifactDigest: sha256:pay993
    configurationSha: 5f91420
  newRevision:
    deploymentRevision: 281
    artifactDigest: sha256:pay1000api
    configurationSha: 71ac290
  environmentGeneration: prod-eu-1844
  strategy:
    desiredReplicas: 20
    maxSurge: 25%
    maxUnavailable: 10%
    minReadySeconds: 30
    progressDeadlineSeconds: 900
  compatibility:
    database: settlement-schema-v42-expand
    events: settlement-events-v18-compatible
  drain:
    terminationGraceSeconds: 45
    loadBalancerDrainSeconds: 60
```

Deployment revision bez artifact/config identity je slabá. Desired replicas a baseline availability sú súčasťou subjectu, pretože rovnaké percentages znamenajú iné absolute capacity pri 4 a 100 replicas.

## 3. Capacity math

Pre desired replicas `R` controller interpretuje surge/unavailable podľa Kubernetes rounding rules. Operational plan má prepočítať absolute bounds a zároveň zohľadniť baseline unavailable Pods.

Pri `R=20`, `maxSurge=25%` a `maxUnavailable=10%`:

```text
maximum total Pods počas rollout-u = 25
minimum available Pods podľa strategy = 18
```

Ak však pred rolloutom sú healthy iba 17 Pods, strategy neobnoví chýbajúcu capacity magicky. Release gate má vyžadovať healthy baseline a resource headroom pre surge na nodes, IPs, volumes, quotas a dependencies.

Praktický read-back:

```bash
kubectl -n payments get deployment payments-api -o json | jq '{desired:.spec.replicas,maxSurge:.spec.strategy.rollingUpdate.maxSurge,maxUnavailable:.spec.strategy.rollingUpdate.maxUnavailable,available:.status.availableReplicas,updated:.status.updatedReplicas,unavailable:.status.unavailableReplicas}'
```

Output preukazuje desired strategy a controller status v čase query. Nepreukazuje actual application capacity, request concurrency alebo dependency quotas. One Ready Pod nemusí poskytovať rovnakú throughput ako old Pod.

## 4. New batch creation a scheduler dependencies

New ReplicaSet sa môže zaseknúť na image pull, scheduling, CNI IP, volume, admission alebo quota. Rolling plan musí odlíšiť application readiness failure od infrastructure capacity failure.

```bash
kubectl -n payments get rs -l app=payments-api \
  -o custom-columns='NAME:.metadata.name,REVISION:.metadata.annotations.deployment\.kubernetes\.io/revision,DESIRED:.spec.replicas,READY:.status.readyReplicas,AVAILABLE:.status.availableReplicas'

kubectl -n payments get pods -l app=payments-api -o wide
```

Output preukazuje controller objects a Pod placement. Nepreukazuje endpoint eligibility alebo business behavior. Events a scheduler conditions rozlišujú placement root cause.

## 5. Readiness, startup a functional eligibility

Readiness probe má signalizovať, či Pod môže prijímať work, nie iba či process beží. Startup probe chráni pomalý initialization pred liveness restartom. Liveness nemá testovať downstream dependency tak, aby spoločný outage reštartoval celú fleet.

New release potrebuje release-aware capability check. `minReadySeconds` zabráni okamžitému available verdictu, no nepreukazuje stabilitu po cache warm-up alebo credential expiry.

EndpointSlice read-back:

```bash
kubectl -n payments get endpointslice -l kubernetes.io/service-name=payments-api -o json | jq '[.items[].endpoints[]|{addresses,ready:.conditions.ready,serving:.conditions.serving,terminating:.conditions.terminating,targetRef}]'
```

Output preukazuje Service endpoint conditions podľa controller state-u. Nepreukazuje dataplane propagation na každom node/proxy ani actual request distribution.

## 6. Mixed-version compatibility

Počas rollout-u môže old producer komunikovať s new consumerom a opačne. Database schema musí podporovať oba binaries; events a caches musia mať tolerant readers; session format nesmie vyžadovať atomic fleet switch.

```text
expand schema
→ deploy tolerant readers/writers
→ rolling application exchange
→ confirm no old consumers/backlog
→ contract cleanup neskôr
```

Breaking change skrytá v config default-e môže mixed-version interval rozbiť rovnako ako schema. Compatibility matrix sa viaže na old/new artifact, configuration, data a event generations.

## 7. Traffic a cohort identity

Service typicky rozdeľuje traffic medzi Ready old a new Pods. Percentage new traffic preto závisí od replica counts, connection reuse, session affinity a endpoint propagation. Replica ratio nie je automaticky request ratio.

Telemetry má labelovať release a operation, nie Pod name ako primary business cohort. Long-lived connections môžu zostať na old endpoints aj po desired weight zmene. Rolling update nie je causally controlled A/B experiment.

## 8. Old batch drain a termination

Pred ukončením old Podu sa endpoint označí terminating/not-ready, preStop môže spustiť application drain a termination grace poskytne čas na dokončenie. External load balancer môže mať vlastný deregistration delay.

```text
remove endpoint eligibility
→ stop new admission
→ wait connection/request drain
→ checkpoint consumer ownership
→ finish alebo hand off in-flight work
→ terminate process
→ verify no unresolved operations
```

`preStop` nie je garantovaná distributed transaction. Node failure alebo hard deadline ho môže prerušiť. Business operation potrebuje idempotency/reconciliation mimo process lifecycle-u.

## 9. PDB a rollout strategy

PodDisruptionBudget obmedzuje voluntary disruptions, ktoré používajú eviction API, napríklad node drain. Deployment controller rolling update riadi vlastným `maxUnavailable` a PDB ho priamo neobmedzuje. Tím nemá predpokladať, že PDB zachráni agresívnu rollout strategy.

PDB je stále relevantný počas súbežných node maintenance alebo autoscaling operations. Release gate má inventarizovať concurrent capacity writers a disturbance budget.

## 10. Pause, progress deadline a rollback

Deployment môže prestať progresovať, hoci niektoré new Pods sú Ready. Progress deadline vytvorí controller condition, no automatická recovery musí poznať shared-state eligibility.

```bash
kubectl -n payments rollout status deployment/payments-api --timeout=15m
kubectl -n payments get deployment payments-api \
  -o jsonpath='{range .status.conditions[*]}{.type}{"="}{.status}{" reason="}{.reason}{"\n"}{end}'
```

Condition preukazuje controller interpretation. Nepreukazuje business acceptance ani že `rollout undo` je data-compatible. Previous ReplicaSet môže existovať, ale old version nemusí vedieť čítať current state.

## 11. Connected incident `REL-PAY-69`

Atlas mal desired `20` replicas, strategy `maxSurge=25%`, `maxUnavailable=10%`. Pred rolloutom boli tri Pods unavailable kvôli CNI IP pressure, takže baseline available bolo `17`. Gate kontroloval iba, že Deployment condition `Available=True`.

New release používal schema field, ktorý old worker nepoznal. Readiness kontrolovala `/healthz`, nie provider credential a event compatibility. New Pods sa rýchlo stali available; controller odstránil old batch podľa strategy. CNI nedokázalo vytvoriť full surge a actual request capacity klesla pod 70 %.

```text
baseline deficit
→ percentage strategy bez absolute capacity gate-u
→ partial surge
→ readiness bez functional contractu
→ mixed-version event incompatibility
→ old removal
→ queue a retry amplification
```

Po pokuse `rollout undo` old Pods nedokázali spracovať nové eventy. 6 412 settlement operations ostalo v backlogu.

Root cause bol rollout subject bez baseline, capacity a shared-state compatibility.

## 12. Redesign a acceptance verdict

Redesign vyžaduje healthy baseline, surge resource reservation, CNI/IP preflight, functional readiness a event replay compatibility. Rollout postupuje batch po batchi s release-aware metrics. Old removal čaká na drain a business cohort acceptance. Rollback eligibility sa vyhodnotí pred každým destructive contract stepom.

Rolling update je prijatý iba vtedy, keď:

```text
old fleet a dependencies majú healthy baseline
+ absolute surge/unavailable bounds sú známe
+ scheduler/network/storage capacity je dostupná
+ new batch prejde functional readiness
+ old/new data/event/session contracts sú compatible
+ endpoint a actual traffic cohort sú observed
+ old batch je drained a ownership uzavreté
+ rollback/roll-forward eligibility je current
+ forbidden new-event-to-old-consumer path je testovaný
+ second batch a full-fleet delayed watch prejdú
```

## 13. Troubleshooting flow

Pri stalled alebo degrading rollout-e sleduj:

```text
deployment revision/strategy a baseline
→ ReplicaSets a desired counts
→ Pod scheduling/startup/readiness
→ EndpointSlice a dataplane eligibility
→ old/new traffic a business cohorts
→ shared-state compatibility
→ drain/termination ownership
→ controller conditions a recovery eligibility
```

Competing hypotheses môžu byť baseline deficit, no surge capacity, image pull, admission, CNI IP, readiness error, dependency quota, mixed-version incompatibility, stuck connections alebo invalid rollback. `kubectl rollout status` je začiatok, nie root-cause verdict.

## 14. Anti-patterny

### Percentá bez absolute výpočtu

Operational capacity sa riadi počtom healthy instances a throughputom, nie iba YAML percentom.

### Rollout pri unhealthy baseline

Strategy môže odstrániť ďalšiu capacity a skryť pôvodný incident.

### Process health ako readiness

Pod môže byť alive a zároveň neschopný bezpečne obslúžiť business operation.

### PDB ako ochrana pred Deployment rolloutom

PDB a rolling strategy chránia odlišné disruption paths.

### `rollout undo` ako univerzálny rollback

Old ReplicaSet nepreukazuje data/event compatibility.

## 15. Kontrolné otázky

1. Prečo je mixed-version interval hlavná rolling boundary?
2. Čo tvorí exact rolling subject?
3. Ako sa prepočítajú surge a unavailable absolute bounds?
4. Prečo healthy baseline patrí do gate-u?
5. Čo preukazuje EndpointSlice a čo nie?
6. Ako sa odlišuje replica ratio od request ratio?
7. Čo musí obsahovať old Pod drain?
8. Ako PDB súvisí a nesúvisí s rolling update-om?
9. Prečo rollback v `REL-PAY-69` nebol bezpečný?
10. Ktorá readiness otázka chýbala?
11. Ako sa testuje old/new event compatibility?
12. Čo musí prejsť pred odstránením ďalšieho batchu?

## Glossary impact

Relevantné pojmy: rolling update, mixed-version interval, maxSurge, maxUnavailable, healthy baseline, absolute capacity bound, ReplicaSet revision, functional readiness, EndpointSlice eligibility, traffic cohort, old-batch drain, disruption path, progress deadline a rolling recovery eligibility.

## Primárne zdroje

- [Kubernetes documentation — Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes documentation — Probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/)
- [Kubernetes documentation — Pod termination](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#pod-termination)
- [Kubernetes documentation — Disruptions and PDBs](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)
- [Kubernetes documentation — EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Recreate deployment](recreate-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Blue-green deployment →](blue-green-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
