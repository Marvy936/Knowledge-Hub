# Desired state a reconciliation loops

Kubernetes funguje ako distribuovaný systém control loops. Používateľ alebo vyšší controller zapíše do API **desired state**. Controllers a node agents priebežne pozorujú **current/observed state**, porovnávajú rozdiel a vykonávajú kroky, ktoré systém približujú požadovanému výsledku. Reconciliation nie je jednorazová deployment procedúra; je to opakovaný, failure-tolerant proces.

## 1. Desired, observed a actual state

### Desired state

To, čo je deklarované v object `spec` alebo odvodené z vyššieho resource-u.

Príklad:

```yaml
spec:
  replicas: 3
```

### Observed state

Stav, ktorý controller alebo agent zistil z API, runtime alebo external systému.

### Actual state

Reálny stav systému v danom okamihu:

- existujúce Pods,
- bežiace processes,
- attached volumes,
- load balancer rules,
- cloud instances,
- DNS records.

Observed state môže za actual state zaostávať kvôli cache, network latency alebo neukončenému reconciliation kroku.

## 2. Reconciliation loop

Základný algoritmus:

```text
observe desired state
observe current state
compute difference
perform bounded action
record result/status
repeat
```

Príklad ReplicaSet:

```text
desired replicas = 3
currently controlled Pods = 2
→ create one Pod
```

Ak je Pods 4:

```text
desired replicas = 3
currently controlled Pods = 4
→ delete one Pod podľa controller policy
```

## 3. Controller nie je shell script

Imperatívny script často predpokladá:

1. krok A uspeje,
2. potom krok B,
3. potom krok C,
4. celý proces sa skončí.

Controller musí tolerovať:

- reštart medzi krokmi,
- opakované events,
- stale cache,
- partial failure,
- concurrent writers,
- external API timeout,
- object deletion počas práce,
- leader transition,
- retry po neznámom výsledku.

Preto má reconciliation vychádzať z aktuálneho state-u, nie iba z pamäte predchádzajúceho kroku.

## 4. Level-based model

Robustný controller sa správa **level-based**:

```text
Aktuálny stav je X, desired state je Y. Čo treba urobiť teraz?
```

Nie iba edge-based:

```text
Prišiel event „create“, preto vykonaj presne jednu sekvenciu.
```

Events slúžia ako trigger na skoršie prehodnotenie. Autoritatívny je aktuálny object state v API a external systéme.

Ak controller zmešká event, resync alebo ďalší relevantný event musí stále viesť ku konvergencii.

## 5. Watch, informer a cache

Typický controller používa:

1. `list` na získanie počiatočného snapshotu,
2. `watch` na zmeny od `resourceVersion`,
3. local cache na efektívne reads,
4. event handlers na enqueue reconciliation key,
5. work queue na retries a rate limiting.

Zjednodušený model:

```text
API server
   ↓ list/watch
shared informer/cache
   ↓ event handler
work queue: namespace/name
   ↓
reconcile worker
   ↓ read current state
API/external writes
```

Cache znižuje API load, ale môže byť krátkodobo stale. Critical write-after-read workflow musí poznať consistency a conflict model.

## 6. Reconciliation key

Queue často neobsahuje celý event payload, ale identity key:

```text
default/web
```

Worker po dequeue znovu načíta aktuálny object.

Výhody:

- viac events pre ten istý object sa môže zlúčiť,
- controller nepracuje so starým snapshotom z eventu,
- retry používa aktuálny desired state,
- object mohol byť medzičasom zmazaný.

## 7. Idempotencia

Reconcile krok má byť bezpečný pri opakovaní.

Nesprávne:

```text
pri každom reconcile vytvor nový external load balancer
```

Správnejšie:

```text
nájdi external resource podľa stabilnej identity
ak neexistuje, vytvor ho
ak existuje, porovnaj configuration
uprav iba rozdiel
```

Pri create timeout-e nemusíš vedieť, či server resource vytvoril. Použi idempotency key alebo následné lookup podľa deterministic identity.

## 8. Convergence

Systém **konverguje**, keď opakované control loops vedú desired a actual state k zhode.

Konvergenciu môžu blokovať:

- nedostatok capacity,
- invalid configuration,
- denied permissions,
- unavailable dependency,
- permanent external API error,
- conflicting controllers,
- selector/ownership chyba,
- stuck finalizer,
- rate limit,
- stale alebo nekonzistentný status.

Controller nemá nekonečne retry-ovať maximálnou rýchlosťou. Potrebuje backoff, conditions a observability.

## 9. Eventual consistency

Kubernetes operácie sú často asynchrónne.

Po:

```bash
kubectl apply -f deployment.yaml
```

môže API okamžite potvrdiť uloženie desired state-u, ale:

- controller ešte nevytvoril ReplicaSet,
- scheduler ešte nepridelil Pods,
- kubelet ešte nepullol image,
- readiness ešte nie je splnená.

API success neznamená workload readiness.

## 10. Controller chaining

Vyšší controller často nevykonáva low-level operáciu priamo.

```text
Deployment controller
→ desired ReplicaSet

ReplicaSet controller
→ desired Pods

Scheduler
→ Pod-to-Node assignment

Kubelet
→ containers running
```

Každá vrstva má vlastný object contract a conditions. Zlyhanie sa diagnostikuje sledovaním chainu downward.

## 11. Ownership a selectors

Controller potrebuje vedieť, ktoré dependent objects vlastní.

Používa:

- ownerReferences,
- labels a selectors,
- UID ownera,
- controller-specific annotations alebo status.

Nesprávne prekrývajúce sa selectors môžu spôsobiť:

- adoption cudzieho objectu,
- súboj controllers,
- nečakané scale/down,
- Service traffic na nesprávne Pods.

## 12. Optimistic concurrency

Viac actors môže čítať a zapisovať rovnaký object. API server používa `resourceVersion` na detekciu stale update-u.

Flow:

1. controller načíta version 10,
2. iný writer vytvorí version 11,
3. controller odošle update založený na version 10,
4. API vráti conflict,
5. controller načíta nový state a prepočíta zmenu.

Conflict nie je dôvod slepo zopakovať starý write. Je to signál znovu reconcile-nuť aktuálny state.

## 13. Field ownership

Pri server-side apply môžu rôzni field managers vlastniť odlišné fields.

Príklad:

- platform team vlastní security context,
- application team vlastní image a replicas,
- autoscaler vlastní `/scale` replicas field.

Nejasné ownership hranice vedú k field conflicts alebo perpetual overwrites.

## 14. Status reporting

Controller má reportovať:

- observed generation,
- conditions,
- relevant counters,
- assigned external identifiers,
- last known error reason,
- progress state.

Status má pomôcť userovi odpovedať:

```text
Controller videl môj najnovší spec?
Čo už dokončil?
Čo ho blokuje?
Je chyba transient alebo permanent?
```

Status nemá obsahovať secrets ani nekontrolované external payloads.

## 15. Conditions

Dobrá condition používa stabilný `type` a machine-readable `reason`.

```yaml
status:
  conditions:
    - type: Ready
      status: "False"
      reason: DependencyUnavailable
      message: Waiting for database endpoint
      observedGeneration: 7
```

Condition transition a repeated retry sú odlišné udalosti. `lastTransitionTime` sa nemá meniť pri každom identickom reconcile pokuse.

## 16. Requeue a retry

Reconciliation môže byť opätovne naplánovaná:

- pri watched evente,
- po explicitnom časovom intervale,
- po transient error-e,
- po dependency zmene,
- pri periodic resync.

Retry policy potrebuje:

- exponential backoff,
- maximum concurrency,
- rate limiting,
- distinction permanent/transient error,
- dead-letter alebo visible degraded state podľa use case-u.

Hot loop môže preťažiť API server aj external dependency.

## 17. Partial failure

Príklad:

1. controller vytvorí cloud load balancer,
2. pred zapísaním external ID do statusu zlyhá,
3. retry nevie, či už resource existuje.

Riešenia:

- deterministic tags/idempotency token,
- lookup podľa owner UID,
- external resource status sync,
- finalizer pred vytvorením external state-u,
- compensation/cleanup workflow.

Distributed transaction cez Kubernetes API a cloud API typicky neexistuje. Controller musí navrhnúť recoverable protocol.

## 18. Finalizers a external cleanup

Ak object vlastní external resource:

1. controller pridá finalizer,
2. vytvorí alebo spravuje external state,
3. pri `deletionTimestamp` prestane vytvárať nový desired state,
4. odstráni external resource,
5. overí cleanup,
6. odstráni finalizer.

Riziká:

- controller je vypnutý,
- credentials expirovali,
- external API nefunguje,
- resource bol ručne zmenený,
- finalizer zostane stuck.

Ručné odstránenie finalizeru je break-glass operácia s možným resource leakom.

## 19. Garbage collection a dependent resources

Pre Kubernetes-native dependents používaj ownerReferences a garbage collection, nie vlastný neauditovaný delete traversal.

Controller však musí zvážiť:

- foreground/background deletion,
- orphan policy,
- cross-namespace obmedzenia,
- external resources mimo API,
- cleanup ordering,
- finalizer interactions.

## 20. Leader election

Controller môže bežať vo viacerých replicas pre availability. Ak jeho execution model vyžaduje jedného aktívneho leadera, použije leader election, typicky cez Lease.

Leader election:

- rieši active instance selection,
- nerieši idempotenciu,
- nezaručuje exactly-once execution,
- nevylučuje krátke overlap alebo retry scenáre pri partitions,
- nenahrádza optimistic concurrency.

Controller musí zostať bezpečný pri opakovanom reconcile aj s leader election.

## 21. Multiple controllers

Kubernetes používa veľa špecializovaných controllers namiesto jedného monolitu.

Výhody:

- menší responsibility scope,
- samostatné retries,
- failure isolation,
- extensibility,
- jasnejší resource ownership.

Riziko vzniká, keď dva controllers menia rovnaký field alebo external resource bez contractu.

## 22. Admission vs. reconciliation

### Admission

Synchronous request-time decision:

- mutate,
- validate,
- reject.

### Reconciliation

Asynchronous ongoing process po uložení objectu.

Admission webhook nemá vykonávať dlhú external orchestration. Request môže nakoniec odmietnuť iná admission vrstva a side effect by zostal bez ownera.

External side effects patria do controlleru s cleanup a retry modelom.

## 23. Drift

Drift vznikne, keď actual state nezodpovedá desired state-u.

Príklady:

- user ručne zmaže Pod,
- cloud load balancer rule je zmenené mimo controlleru,
- Node prestane reportovať,
- volume attach zmizne,
- image tag ukazuje na iný digest.

Controller môže drift:

- opraviť,
- reportovať,
- odmietnuť prepis pri shared ownership,
- vyžadovať human decision.

Nie každý drift má byť automaticky overwrite-nutý. Ownership policy musí byť explicitná.

## 24. Broken desired state

Kubernetes spoľahlivo reconcile-uje aj chybný intent.

Príklady:

- neexistujúci image,
- nemožné scheduling constraints,
- selector bez Pods,
- neplatný health endpoint,
- príliš nízky memory limit,
- chýbajúci Secret.

Control loop nepozná business správnosť. Potrebuje validation, testing, policy a observability.

## 25. Backpressure a work queues

Pri veľkom event burst-e controller potrebuje:

- bounded workers,
- rate-limited queue,
- deduplication keys,
- priority podľa potreby,
- queue depth metrics,
- latency SLO,
- protection external APIs.

Neobmedzená goroutine/thread per event stratégia môže preťažiť API server alebo cloud provider.

## 26. Reconciliation observability

Sleduj:

- reconcile count a duration,
- success/error/requeue rate,
- work queue depth,
- oldest queue item age,
- API request latency/errors,
- conflict rate,
- external API latency/rate limits,
- condition transitions,
- leader status,
- cache sync status,
- generation lag.

Log fields:

- controller name,
- namespace/name,
- UID,
- generation,
- reconcile ID,
- action,
- reason,
- external resource ID bez secretov.

## 27. Diagnostika reconciliation chainu

Postup:

1. načítaj top-level object `spec`, `status`, conditions,
2. porovnaj `generation` a `observedGeneration`,
3. nájdi owner/dependent hierarchy,
4. skontroluj labels/selectors,
5. prečítaj Events,
6. over controller deployment/leader/logs,
7. sleduj ďalšiu nižšiu vrstvu,
8. over permissions a admission,
9. over external dependency,
10. identifikuj permanent vs. transient failure.

Príklad:

```text
Deployment not Available
→ ReplicaSet desired/current replicas
→ Pod status/conditions
→ scheduler Events
→ kubelet/runtime/probes
```

## 28. Časté anti-patterny

### Event payload ako jediný source of truth

Event môže byť stale alebo zmeškaný.

### Create on every reconcile

Vznikajú duplicate external resources.

### Status update, ktorý spustí nekonečný vlastný reconcile

Controller musí filtrovať nerelevantné updates alebo stabilne zapisovať iba skutočné zmeny.

### Immediate retry bez backoffu

Vznikne API/external hot loop.

### Dlhá blokujúca operácia v jednom workerovi

Zvyšuje queue latency a komplikuje cancellation.

### Finalizer bez dostupného cleanup controlleru

Objects zostanú trvalo terminating.

### Dvaja writers na rovnakom fielde

Vzniká konflikt alebo perpetual drift.

### Leader election považovaný za exactly-once garanciu

Retry a partial failure stále existujú.

## 29. Troubleshooting

### `observedGeneration` zaostáva

Controller ešte nespracoval nový spec, je nedostupný, queue je preťažená alebo reconciliation zlyháva.

### Object má opakovane rovnaký warning Event

Identifikuj permanent condition; nečakaj, že retry bez zmeny vstupu problém vyrieši.

### Controller používa vysoké CPU

Over hot reconciliation loop, status self-trigger, event storm, cache resync a retry bez backoffu.

### Duplicované cloud resources

Over idempotency key, external lookup, status persistence a create timeout recovery.

### Object je stuck terminating

Over deletionTimestamp, finalizers, controller logs, credentials a external cleanup state.

### Controllers sa prepisujú

Pozri managedFields, audit logs, field ownership a admission mutation.

## 30. Kontrolné otázky

1. Aký je rozdiel medzi desired, observed a actual state?
2. Prečo má controller po evente načítať aktuálny object?
3. Čo znamená level-based reconciliation?
4. Prečo musí byť reconcile idempotentný?
5. Ako funguje list/watch/cache/work-queue model?
6. Na čo slúži `observedGeneration`?
7. Ako sa controller zotaví z partial failure po external create requeste?
8. Aký je rozdiel medzi admission a reconciliation?
9. Prečo leader election neposkytuje exactly-once execution?
10. Ako diagnostikuješ nekonvergujúci top-level workload?

## Glossary impact

Relevantné pojmy: desired state, observed state, actual state, reconciliation loop, Kubernetes controller, level-based reconciliation, convergence, eventual consistency, informer, controller cache, work queue, reconciliation key, requeue, rate-limited retry, generation lag, idempotent reconcile, partial failure, field ownership, controller chaining, hot loop, external resource reconciliation a leader-elected controller.

## Oficiálna dokumentácia

- [Controllers](https://kubernetes.io/docs/concepts/architecture/controller/)
- [Objects in Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/)
- [Kubernetes API concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/)
- [Owners and dependents](https://kubernetes.io/docs/concepts/overview/working-with-objects/owners-dependents/)
- [Finalizers](https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/)
- [Leases](https://kubernetes.io/docs/concepts/architecture/leases/)
- [Admission webhook good practices](https://kubernetes.io/docs/concepts/cluster-administration/admission-webhooks-good-practices/)
