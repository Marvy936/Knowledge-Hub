# Deployment

Deployment je higher-level Kubernetes controller pre riadený prechod medzi Pod template revisions. Nevytvára Pody priamo: vytvára a škáluje ReplicaSety, ktoré vytvárajú Pody. Jeho correctness preto nie je iba „nový ReplicaSet existuje“, ale bezpečná výmena kapacity, trafficu a application behavior medzi starou a novou revision.

Dominantný lifecycle tejto kapitoly:

```text
release intent a Deployment UID/generation
→ admitted Pod template a field ownership
→ template hash a nová ReplicaSet revision
→ rolling alebo recreate capacity transition
→ Pod scheduling, execution a readiness
→ availability a EndpointSlice traffic eligibility
→ starý ReplicaSet scale-down a termination
→ rollout status a business acceptance
→ revision retention, rollback alebo roll-forward
→ recovery a closure
```

Pri diagnostike sa nepýtaj iba „je rollout complete?“. Pýtaj sa:

```text
Ktorú Deployment generation a template digest realizujeme?
Ktoré old/new ReplicaSet UIDs sú active?
Aká kapacita je desired, updated, ready, available a terminating?
Ktoré Pod UIDs reálne prijímajú traffic?
Je nová revision application a data-compatible so starou aj downstream state-om?
```

## 1. Atlas rollout subject

Atlas Payments nasadzuje release `4.2.0`:

```text
cluster: atlas-prod-eu1
Deployment: production/payments-api
Deployment UID: D42
generation: 12
desired replicas: 6
old ReplicaSet: RS41, template hash 6c4f8c7d6f, digest sha256:3f10...
new ReplicaSet: RS42, template hash 7d6f9d8b7b, digest sha256:4a20...
config generation: C52
secret epoch: SE08
strategy: RollingUpdate
maxSurge: 2
maxUnavailable: 1
minReadySeconds: 20
progressDeadlineSeconds: 600
```

Pôvodný outcome:

- new revision postupne získa šesť business-ready replicas;
- availability neklesne pod reviewovaný budget;
- Service posiela traffic iba na Ready a accepted Pod UIDs;
- old a new application versions bezpečne koexistujú počas overlap-u;
- old ReplicaSet sa scale-downuje až po new-capacity acceptance;
- žiadny payment request nie je stratený ani autorizovaný dvakrát;
- po rollout-e nezostane starý digest alebo staging dependency v active path-e.

## 2. Ownership chain

```text
Deployment D42 generation 12
├─ old ReplicaSet RS41 revision 11
│  └─ old Pod UIDs
└─ new ReplicaSet RS42 revision 12
   └─ new Pod UIDs
```

Deployment vlastní desired transition medzi ReplicaSets. ReplicaSet vlastní count a Pod creation. Scheduler a worker nodes vlastnia execution. Service/EndpointSlice a application vlastnia traffic a business outcome.

Ručná zmena child ReplicaSetu alebo Podu obchádza vyšší desired-state contract a môže byť pri ďalšom reconcile prepísaná.

## 3. Deployment release subject

Rollout musí byť viazaný na immutable subject:

```text
cluster a namespace
Deployment UID
generation a resourceVersion
field managers
strategy a replica budget
admitted Pod template
image digest
config/secret generations
template hash
old/new ReplicaSet UIDs a revisions
required compatibility a business outcome
```

Deployment name a image tag samotné nestačia. Mutable tag môže ukazovať na nový content bez zmeny Pod template-u, takže nevznikne nová revision ani jednoznačný rollout audit.

## 4. Čo vytvára novú revision

Relevantná zmena `.spec.template` vytvorí nový template hash a typicky nový ReplicaSet.

Príklady:

- image digest;
- command a args;
- environment alebo references;
- Pod labels/annotations v template;
- resources;
- probes a readiness gates;
- volumes a mounts;
- service account alebo security context;
- init/sidecar configuration.

Zmena `.spec.replicas` sama osebe nie je nová application revision. Scale subject a release subject sú odlišné.

Mechanizmus:

```text
Pod template generation T12
→ hash H12
→ ReplicaSet RS42
→ Pods s template hash H12
```

Existing Pods sa neprepíšu in-place. Nový template sa realizuje replacementom cez nový ReplicaSet.

## 5. RollingUpdate ako capacity exchange

Rolling update nie je jednoduché „spusť nové a zmaž staré“. Je to opakovaný capacity exchange:

```text
observe old/new ReplicaSets a Pod availability
→ scale up new RS v surge limite
→ čakať na readiness a minReadySeconds
→ scale down old RS v unavailable limite
→ opakovať
→ old RS replicas=0, new RS=desired
```

### `maxSurge`

Určuje, koľko extra active Podov môže controller vytvoriť nad desired count počas update-u. Percentá sa vyhodnocujú z desired replica countu podľa API pravidiel.

### `maxUnavailable`

Určuje, koľko desired replicas môže byť počas update-u nedostupných.

Tieto hodnoty tvoria availability/capacity budget, nie application compatibility proof.

Príklad:

```text
desired=6
maxSurge=2
maxUnavailable=1

reviewovaný active budget:
minimum available: 5
maximum non-terminating desired+surge: 8
```

Terminating Pods môžu ešte spotrebúvať CPU, memory, connections a volumes, preto host-level peak consumption môže byť vyššia než jednoduchý active count.

## 6. Surge potrebuje reálnu kapacitu

`maxUnavailable: 0` a positive surge chránia dostupnosť iba vtedy, keď cluster dokáže nový Pod umiestniť a spustiť.

```text
žiadna voľná Node capacity
+ maxUnavailable=0
→ old Pod nemožno odstrániť
→ new Pod nemožno schedulovať
→ rollout stagnuje
```

Riešenie nie je automaticky zvýšiť `maxUnavailable`. Najprv rozhodni, či je bezpečnejšie:

- pridať kapacitu;
- znížiť requests po dôkaze;
- vykonať kontrolovaný unavailable transition;
- použiť inú rollout stratégiu;
- odložiť release.

## 7. Readiness a availability sú rollout control signals

Chain:

```text
container process Running
→ container readiness
→ Pod Ready + readiness gates
→ minReadySeconds
→ Deployment available replica
→ EndpointSlice traffic eligibility
```

`Ready=True` je potrebný, ale nie vždy postačujúci pre business acceptance. Readiness môže byť:

- príliš plytká a pustiť traffic pred warmupom alebo downstream compatibility;
- príliš závislá od shared dependency a odpojiť všetky replicas naraz;
- nestabilná a vytvoriť availability flapping;
- technicky správna, ale business synthetics stále zlyhávajú.

Deployment controller používa reportované readiness/availability. Nevie sám posúdiť payment correctness.

## 8. `minReadySeconds`

`minReadySeconds` vyžaduje, aby nový Pod zostal Ready určitý čas pred započítaním ako available.

Pomáha odhaliť:

```text
Pod sa krátko stane Ready
→ po warmup-e crashne alebo probe zlyhá
→ nemá okamžite nahradiť old stable capacity
```

Nie je to soak test ani business validation. Príliš krátka hodnota nezachytí delayed failure; príliš dlhá zvyšuje rollout čas a potrebu surge capacity.

## 9. Progress a deadline

Deployment reportuje conditions ako `Progressing` a `Available`. `progressDeadlineSeconds` určuje, kedy má byť rollout označený ako bez progressu.

Dôležité:

```text
ProgressDeadlineExceeded
→ evidence, že rollout nepostupuje
→ nie automatický rollback
```

Deployment alebo release automation musí vykonať explicitné rozhodnutie:

- continue po transient recovery;
- pause a vyšetrovať;
- roll-forward opravenou revision;
- rollback, ak je stará revision stále kompatibilná;
- contain traffic alebo celý release.

## 10. Recreate stratégia

```text
old Pods terminate
→ new Pods sa vytvoria
```

Recreate je vhodná iba pri explicitnom dôvode, napríklad:

- old/new versions nemôžu koexistovať;
- single-writer alebo exclusive local resource;
- downtime je prijateľný;
- protocol/data contract nepodporuje rolling overlap.

Recreate rieši order Pod replacementu. Nezabezpečuje:

- databázový rollback;
- external lock/fencing;
- data preservation;
- successful startup;
- business continuity.

Ak old process pri termination nezanikne alebo external lease neexspiruje, aj Recreate môže vytvoriť overlap.

## 11. Revision history

Staré ReplicaSets s nulovým countom uchovávajú Pod template revisions podľa `revisionHistoryLimit`.

Revision history poskytuje:

- template lineage;
- možnosť `rollout undo` v podporovanom rozsahu;
- audit old/new ReplicaSets;
- rýchlejší application-template recovery.

Nie je náhrada za:

- source control;
- immutable artifact retention;
- database backup/restore;
- event/schema compatibility;
- external configuration a secret history;
- business reconciliation.

## 12. Rollback je nový forward transition k starej template

`kubectl rollout undo` nevráti čas systému. Deployment vytvorí desired state z predchádzajúcej template revision.

```text
new application revision zmenila durable/external state
→ application template sa vráti
→ database, queue, cache alebo third-party state zostane nový
```

Rollback je bezpečný iba ak old application:

- rozumie aktuálnej databázovej schema a dátam;
- zvládne nové queue/event payloads;
- používa stále validné credentials;
- je kompatibilná s current feature flags a config;
- neporuší already-issued business operations.

Inak je potrebný roll-forward, compensation alebo data recovery.

## 13. Pause a resume

Pause umožňuje zostaviť viac template zmien pred pokračovaním rollout-u. Nie je to globálne zmrazenie systému.

Počas pause môžu stále konať:

- HPA;
- GitOps writer;
- manual scale;
- secret/config rotácie;
- Node failures a ReplicaSet replacement;
- Service a policy controllers.

Pred resume znovu načítaj effective Deployment spec, field ownership, active ReplicaSets a capacity. Nepracuj s pôvodným local manifestom ako s garantovane aktuálnym stavom.

## 14. Replica scaling a HPA ownership

HPA typicky vlastní scale transition cez Deployment `/scale`. GitOps alebo source manifest môže zároveň zapisovať `.spec.replicas`.

Nejasný ownership vytvára:

```text
HPA desired=10
→ GitOps apply replicas=6
→ HPA znovu 10
→ rollout capacity a metrics oscilujú
```

Pred rolloutom definuj:

- či source manifest obsahuje replicas;
- kto vlastní scale field;
- HPA min/max a stabilization behavior;
- ako sa metrics rozdelia medzi old/new revisions;
- či surge Pods ovplyvnia autoscaling signal.

Manual scale child ReplicaSetu nie je stabilná oprava Deployment/HPA subjectu.

## 15. Scale počas rollout-u

Ak sa desired replicas zmenia počas active rolling update-u, Deployment controller musí rozdeliť scale transition medzi active ReplicaSets podľa svojho rollout modelu.

Diagnostika preto nemá predpokladať:

```text
Deployment replicas=10
→ new ReplicaSet okamžite 10
```

Treba pozrieť:

- active old/new ReplicaSet desired counts;
- current rollout progress;
- HPA timeline;
- available capacity;
- controller Events a generation;
- Service traffic distribution.

## 16. Pod termination a capacity overlap

Scale-down old ReplicaSetu spustí Pod termination lifecycle:

```text
endpoint removal/readiness transition
→ PreStop
→ termination signal
→ connection drain
→ force kill po grace
→ CNI/CSI/runtime cleanup
```

Terminating Pods môžu:

- ešte držať connections;
- spotrebúvať resources;
- držať attached volumes alebo host ports;
- krátko zostať v endpoint state podľa timing-u;
- blokovať Node capacity pre surge.

Rollout capacity planning musí zahŕňať startup aj termination overlap.

## 17. Service traffic transition

Deployment controller priamo neprogramuje application traffic. Typický chain:

```text
new Pod Ready
→ EndpointSlice controller aktualizuje endpoint
→ Service dataplane začne routing
→ application SLI a business checks

old Pod terminating/not ready
→ EndpointSlice transition
→ dataplane prestane posielať nové requests
→ existing connections sa drainujú podľa vrstiev
```

Pre successful rollout over targetRef Pod UIDs a revision-specific telemetry. Aggregate Service success môže maskovať, že new revision neobsluhuje žiadny traffic.

## 18. PDB a Deployment rollout majú odlišné semantics

PodDisruptionBudget obmedzuje určité voluntary disruptions vykonané cez eviction API. Deployment rolling update riadi vlastný unavailable budget cez `maxUnavailable`.

PDB nie je náhrada za Deployment strategy. Pri súbehu rollout-u a Node drainu treba vyhodnotiť oba modely:

```text
Deployment unavailable/surge budget
+ PDB eviction budget
+ topology a remaining capacity
+ termination time
→ effective disruption risk
```

PDB nechráni pred application crashom, Node hard failure ani chybnou readiness.

## 19. Application compatibility počas overlap-u

RollingUpdate predpokladá, že old a new revisions môžu určitý čas bežať súčasne.

Over:

- request a response API compatibility;
- database expand-contract fázu;
- event producer/consumer schema;
- cache a session formats;
- background workers a leader election;
- feature flags;
- shared files a locks;
- secret epoch overlap;
- external API side effects a idempotency.

Kubernetes orchestration nevie automaticky zistiť semantic incompatibility.

## 20. Deployment completion verdict

Technický completion subject typicky potrebuje:

```text
status.observedGeneration == metadata.generation
updated replicas == desired replicas
available replicas spĺňajú desired budget
old active ReplicaSets sú scale-downuté podľa strategy
žiadny nový Pod nie je stuck/unknown
```

Produkčný acceptance verdict navyše potrebuje:

- correct admitted template a image digest;
- correct config/secret generations;
- expected EndpointSlice cohort;
- revision-specific latency/error/saturation;
- critical business synthetic;
- forbidden old/staging outcomes absent;
- rollback/roll-forward a incident state uzatvorený.

## 21. Worked failure: mutable tag nevytvoril rollout

Registry tag `payments-api:stable` bol presunutý na nový digest, ale Deployment Pod template zostala textovo rovnaká.

```text
source tag content sa zmení
→ Deployment generation/template hash sa nezmení
→ nový ReplicaSet nevznikne
→ existing Pods zostanú na starom imageID
→ replacement na inom Node-e môže neskôr pullnúť nový digest
```

Výsledkom je mixed content bez explicitnej revision. Recovery vyžaduje immutable digest a reviewovaný template transition.

## 22. Worked failure: `maxUnavailable: 0` bez surge capacity

Deployment mal desired 6, `maxSurge: 1`, `maxUnavailable: 0`. Cluster nemal miesto pre siedmy Pod.

```text
new Pod Pending: insufficient CPU
→ nemôže sa stať Available
→ old Pod nemožno scale-downúť
→ rollout stojí
```

Controller fungoval správne. Chybný bol capacity/rollout contract.

## 23. Worked failure: plytká readiness odstránila old capacity príliš skoro

New Pods vracali `/ready=200` hneď po HTTP listener start-e. Cache warmup a database prepared statements trvali ďalších 90 sekúnd.

```text
readiness True
→ minReadySeconds krátke
→ Deployment scale-down old RS
→ new Pods dostanú plný traffic
→ latency a timeouty prudko rastú
```

Rollout bol podľa Kubernetes statusu progressing/available, ale business acceptance zlyhala. Fix patrí do readiness/warmup a staged exposure modelu.

## 24. Worked failure: application rollback bol data-incompatible

Release 4.2.0 začal zapisovať event schema v2. Po chybe bol vykonaný `rollout undo` na 4.1.3, ktorá čítala iba v1.

```text
Pod template rollback success
→ old Pods Ready
→ v2 backlog zostane
→ consumer 4.1.3 padá alebo zahadzuje events
```

Deployment rollback obnovil application artifact, nie celý system state. Potrebný bol compatible roll-forward alebo event/data recovery.

## 25. Worked failure: terminating Pods vyčerpali surge capacity

Old Pods mali 120-sekundový grace period a držali host ports. Deployment vytvoril new Pods, ale tie nemohli byť schedulované na rovnakých Nodes, kým terminating Pods neuvoľnili ports.

Status active counts neukázal plný host-level resource overlap. Recovery vyžadovala review termination/hostPort contractu, nie iba zvýšenie progress deadline.

## 26. Causal troubleshooting walkthrough: rollout prekročil progress deadline

Symptóm:

```text
Deployment D42 generation 12
Progressing=False, reason=ProgressDeadlineExceeded
old RS41: 5 available Pods
new RS42: 2 Pods, 0 available
Service stále obsluhuje väčšinu trafficu cez old revision
```

### 1. Zafixuj subject a pôvodný outcome

Zaznamenaj:

```text
cluster, namespace a Deployment UID
metadata.generation/status.observedGeneration
field managers a admission mutations
strategy, desired replicas, surge/unavailable budgets
minReadySeconds a progress deadline
old/new ReplicaSet UIDs, revisions a desired/current counts
new Pod UIDs, Nodes, imageIDs, config a secret generations
readiness/startup/gate evidence
EndpointSlice targetRef UIDs a traffic telemetry
HPA/scale timeline
application/data compatibility a required business outcome
```

### 2. Competing hypotheses

1. Deployment controller ešte nespracoval generation 12.
2. Mutating admission zmenila new Pod template.
3. New ReplicaSet nevznikol alebo má wrong owner/template hash.
4. ReplicaSet nemôže vytvárať Pods pre admission/quota/RBAC failure.
5. Pods vznikli, ale sú unschedulable pre surge capacity, affinity, topology alebo host ports.
6. Worker-node image/CNI/CSI/config failure blokuje startup.
7. Application alebo init container padá.
8. Readiness probe alebo custom readiness gate zostáva False.
9. `minReadySeconds` je dlhší než pozorované Ready okno.
10. HPA alebo GitOps writer mení replicas/template počas rollout-u.
11. Old Pods sa terminujú pomaly a držia capacity.
12. New Pods sú Ready, ale EndpointSlice alebo traffic telemetry zaostáva.
13. Deployment je paused alebo strategy invariants blokujú ďalší transition.
14. Application compatibility check zlyhal, hoci Pods sú technicky healthy.

### 3. Discriminating observation points

- live Deployment YAML: UID, generation, observedGeneration, conditions, managed fields;
- old/new ReplicaSet ownerReferences, revision annotations, template hashes a scale counts;
- ReplicaSet Events pre Pod create failures;
- new Pod conditions, Events, imageID, init/container states a Nodes;
- scheduler capacity/topology a terminating Pod inventory;
- kubelet/runtime/CNI/CSI evidence pre assigned Pods;
- readiness probe/gate results a `minReadySeconds` timeline;
- EndpointSlice targetRef UIDs a revision-specific request counts;
- HPA desired replicas a audit writes;
- application logs/SLIs a database/event compatibility evidence.

Ak new Pod objects neexistujú, scheduler a readiness nie sú root-cause boundaries. Ak sú Running/Ready, ale `availableReplicas=0`, skontroluj `minReadySeconds`, observed generation a status freshness. Ak sú Available, ale nemajú traffic, posuň sa do EndpointSlice/Service boundary.

### 4. Containment

- ponechaj old healthy RS41 capacity;
- pause release automation alebo conflicting template writes, nie nevyhnutne celý Deployment controller;
- nevymaž old ReplicaSet ani jeho Pods;
- neforce-ni HPA/GitOps field ownership bez rozhodnutia;
- zachovaj Deployment/RS/Pod YAML, Events, audit a revision telemetry;
- obmedz new-revision traffic, ak porušuje forbidden outcome;
- nepridávaj replicas naslepo, ak failure spôsobuje per-Pod resource alebo dependency overload.

### 5. Recovery podľa boundary

- generation/controller lag → obnov controller queue/leadership a sleduj generation closure;
- admission/template → oprav policy/source a vytvor novú reviewovanú revision;
- Pod create failure → oprav quota/RBAC/admission;
- capacity/scheduling → pridaj capacity, zmeň reviewovaný budget alebo constraints;
- node execution → oprav image/CNI/CSI/config a over Pod lifecycle;
- readiness/gate → oprav application/platform readiness contract;
- minReady mismatch → zlaď startup profile a availability timing;
- slow termination → oprav draining/grace/host resource contract;
- field conflict → definuj authoritative scale/template ownera;
- application incompatibility → roll-forward compatible artifactom alebo vykonaj safe rollback/compensation podľa data state-u.

### 6. Over pôvodný outcome

Potvrď:

- D42 observed generation 12 alebo novšiu reviewovanú recovery generation;
- new canonical ReplicaSet má correct owner, template hash a digest;
- šesť new Pods je Ready a Available podľa timing contractu;
- EndpointSlice obsahuje iba accepted new-generation UIDs;
- old RS41 je scale-downutý až po new-capacity acceptance;
- termination dokončí in-flight requests bez duplicate paymentu;
- payment synthetic a downstream audit prejdú cez každú new-revision cohortu;
- žiadny old digest, v2-incompatible consumer alebo staging dependency nezostáva v active path-e;
- next reconcile a rollout status sú stabilné.

### 7. Posuň control skôr

Pridaj:

- immutable release manifest s Deployment UID/generation/template digestom;
- server-side admitted-template diff;
- rollout capacity preflight vrátane terminating overlapu;
- readiness/warmup a graceful-termination tests;
- revision-specific Service telemetry;
- HPA/GitOps field-ownership policy;
- compatibility gate pre DB/events/secrets;
- automated decision record pre rollback vs. roll-forward;
- business synthetic via Service path pred old-RS scale-downom.

## 27. Deployment observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| Release intent | Deployment UID/generation | spec, managed fields, admitted template |
| Revision | old/new RS UIDs a hashes | ownerReferences, revision, desired counts |
| Capacity exchange | strategy + replica budget | surge, unavailable, terminating inventory |
| Pod creation | RS/Pod UIDs | Events, quota, admission, scheduling |
| Execution | Pod/Node/image subjects | container states, probes, CNI/CSI, imageID |
| Availability | Pod UID + timing | Ready, gates, minReadySeconds, availableReplicas |
| Traffic | EndpointSlice targetRef UIDs | selector, endpoint conditions, per-revision traffic |
| Scale | Deployment `/scale` subject | HPA/GitOps/manual audit, active RS allocation |
| Compatibility | old/new/data generations | DB/event/cache/secret/feature evidence |
| Business | release + operation ID | SLI, synthetic, downstream audit, forbidden outcomes |

## 28. Referenčné príkazy

```bash
kubectl get deployment <name> -n <namespace> -o yaml
kubectl describe deployment <name> -n <namespace>
kubectl rollout status deployment/<name> -n <namespace>
kubectl rollout history deployment/<name> -n <namespace>
kubectl get rs -n <namespace> -l '<selector>' -o yaml
kubectl get pods -n <namespace> -l '<selector>' -o wide
kubectl get endpointslice -n <namespace> -o yaml
kubectl get hpa -n <namespace> -o yaml
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

## 29. Referenčné pravidlá

- Deployment riadi revision a capacity transition cez ReplicaSets; nevytvára Pody priamo.
- Novú revision vytvára Pod template transition, nie samotný scale.
- Mutable tag bez template zmeny nie je spoľahlivý rollout subject.
- `maxSurge` a `maxUnavailable` sú capacity budgets, nie compatibility proof.
- `Ready`, `Available`, endpoint eligible a business accepted sú odlišné states.
- `ProgressDeadlineExceeded` je evidence, nie automatický rollback.
- Revision history nevracia database, queues, credentials ani external state.
- Pause nezastaví HPA, GitOps, Node failures ani všetky controllers.
- PDB a Deployment rollout majú odlišné disruption semantics.
- Terminating Pods môžu spotrebúvať surge capacity a držať host resources.
- Rollback je bezpečný iba pri current data/external-state compatibility.
- Deployment completion musí byť doplnený business acceptance verdictom.

## 30. Kontrolné otázky

1. Aký lifecycle spája Deployment generation s accepted Service trafficom?
2. Prečo Deployment používa ReplicaSets namiesto priameho vytvárania Podov?
3. Ktoré zmeny vytvárajú novú revision a ktoré iba scale transition?
4. Ako spolu pôsobia `maxSurge`, `maxUnavailable` a reálna Node capacity?
5. Prečo Ready Pod nemusí byť business-ready?
6. Čo `ProgressDeadlineExceeded` urobí a neurobí?
7. Prečo `rollout undo` nie je system rollback?
8. Ako HPA a GitOps môžu vytvoriť replica-field oscillation?
9. Prečo terminating Pods patria do capacity modelu?
10. Čo musí Deployment recovery verdict overiť?

## Glossary impact

Relevantné pojmy: Deployment release subject, Deployment generation closure, Pod-template revision subject, rolling capacity exchange, surge-capacity subject, unavailable budget, terminating-replica overlap, availability timing subject, EndpointSlice revision cohort, Deployment scale ownership, rollout progress verdict, Recreate exclusivity boundary, rollback compatibility subject, revision-to-traffic lifecycle, Deployment observation matrix a rollout acceptance verdict.

## Oficiálna dokumentácia

- [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Update a Deployment without downtime](https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/)
- [Managing workloads](https://kubernetes.io/docs/concepts/workloads/management/)
- [Pod disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)
- [Pod disruption budgets](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: ReplicaSet](replicaset.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: StatefulSet →](statefulset.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
