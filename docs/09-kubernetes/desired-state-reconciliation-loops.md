# Desired state a reconciliation loops

Kubernetes funguje ako distribuovaný systém control loops. Reconciliation nie je jednorazová deployment procedúra ani sekvencia shell krokov. Je to opakovaný protocol, ktorý z versionovaného intentu a aktuálnych observations vypočíta bounded transition, vykoná ho bezpečne pri retries a reportuje, čo bolo skutočne dosiahnuté.

Dominantný lifecycle:

```text
object intent a generation
→ list/watch a cache observation
→ reconciliation key
→ subject reconstruction
→ desired/current/external-state comparison
→ bounded idempotent action
→ optimistic object/status write
→ condition, requeue a backoff
→ convergence verification
→ deletion/finalizer cleanup
→ drift, partial-failure a ownership recovery
```

Controller je správny iba vtedy, keď zostane bezpečný pri:

- zmeškanom alebo duplicitnom evente;
- stale cache;
- process restarte;
- leader transition;
- API conflict-e;
- external timeout-e s unknown outcome;
- object update alebo delete počas práce;
- opakovanom reconcile rovnakého subjectu.

## 1. Atlas controller scenár

Atlas používa custom resource:

```text
Kind: PaymentGateway
namespace/name: production/eu-gateway
UID: PG42
metadata.generation: 7
spec:
  serviceRef: payments-api
  replicas: 6
  publicHostname: pay.example.com
  cloudLoadBalancerClass: premium
```

Controller vlastní:

- Kubernetes Service a Endpoint policy;
- external cloud load balancer `LB-PG42`;
- DNS binding;
- status/conditions;
- cleanup finalizer.

Desired outcome:

```text
PaymentGateway generation 7
→ correct Service subject
→ one external LB tagged ownerUID=PG42
→ listener a backend set match ready Pods
→ DNS points to current LB
→ external transaction succeeds
→ status observedGeneration=7 a Ready=True
```

Forbidden outcomes:

- dva external load balancers pre jednu UID;
- LB patriaci starej UID po name reuse;
- DNS na partially configured LB;
- finalizer removed pri existujúcom external resource;
- `Ready=True` pre starú generation.

## 2. Desired, observed a effective state

### Desired state

Intent z `spec`, field ownershipu a dependent contracts.

### Observed state

To, čo controller momentálne pozná z:

- API cache alebo fresh read-u;
- dependent objects;
- external APIs;
- runtime statusu;
- vlastných bindings.

### Effective/actual state

To, čo reálne existuje a ovplyvňuje používateľa:

- running processes;
- cloud load balancer rules;
- DNS records;
- mounted data;
- active endpoints;
- accepted payment operation.

Observed state môže za effective state zaostávať. Status môže za desired generation zaostávať. External API môže potvrdiť request, no client nemusí dostať response.

## 3. Level-based reconciliation

Robustný controller odpovedá:

```text
Ak desired state je Y a current effective state je X,
aký najmenší bezpečný transition je potrebný teraz?
```

Nie:

```text
Prišiel event Create, preto vykonaj steps A, B, C presne raz.
```

Events sú triggers. Autoritatívny je current object a relevantný external state.

Dôsledok:

- zmeškaný event nesmie trvalo blokovať convergence;
- duplicate event nesmie vytvoriť duplicate side effect;
- retry musí znovu načítať latest intent;
- resync musí vedieť opraviť drift.

## 4. List, watch, cache a work queue

Typický control path:

```text
API LIST snapshot
→ WATCH od collection resourceVersion
→ informer cache
→ event handler
→ queue key namespace/name alebo UID-aware key
→ reconcile worker
```

Queue zvyčajne nenesie authoritative event payload. Nesie key, podľa ktorého worker znovu načíta current state.

Výhody:

- viac events sa deduplikuje;
- stale payload sa nepoužije ako source of truth;
- object mohol byť medzičasom updated alebo deleted;
- retry pracuje s latest generation.

### Failure boundary: cache ešte nie je synced

Controller začne workers skôr, než initial list dokončí cache sync.

```text
cache vyzerá prázdna
→ controller interpretuje dependents ako missing
→ vytvorí duplicate resources
```

Workers alebo leader readiness musia čakať na required cache sync.

## 5. Reconciliation subject

Každý reconcile potrebuje presnú identity:

```text
controller name a version
leader/replica identity
cluster a API endpoint
object GVK, namespace, name, UID
metadata.generation a resourceVersion
field-manager/ownership context
dependent object UIDs
external resource IDs a owner tags
reconcile ID a queue attempt
credential/config generation
```

Namespace/name bez UID nestačí pri delete/recreate collision. Event bez current generation nestačí pri update burst-e.

## 6. Observe before mutate

Reconcile má zostaviť current state inventory:

```text
top-level object
+ owned Kubernetes dependents
+ external resource lookup
+ status/binding metadata
+ deletion state
+ policy a permissions
```

Potom klasifikuje delta:

- no-op/converged;
- create missing resource;
- update owned fields;
- replace incompatible resource;
- wait for dependency;
- report permanent invalid intent;
- delete/cleanup;
- unknown outcome requiring reconciliation;
- ownership conflict requiring human/policy decision.

Nerozlišovať tieto states vedie k blind create, hot retry alebo destructive overwrite.

## 7. Stable identity a idempotent action

External create potrebuje deterministic identity alebo idempotency mechanism.

Atlas používa:

```text
external owner tag: kubernetesUID=PG42
operation key: paymentgateway/PG42/lb-generation-7
```

Create protocol:

```text
lookup external resource podľa stable owner identity
→ ak existuje, observe current owned fields
→ ak neexistuje, create s idempotency key
→ po timeout-e znovu lookup
→ nikdy nevytváraj druhý resource iba preto, že response chýbala
```

Idempotencia neznamená iba „rovnaký call nevadí“. Znamená, že opakovaný reconcile konverguje k jednej intended identity bez duplicate side effects.

## 8. Bounded transition

Jeden reconcile nemá robiť neobmedzenú orchestration sekvenciu bez checkpoints.

Vhodnejší protocol:

```text
ensure finalizer
→ return/requeue
ensure external LB identity
→ record binding/status
→ return/requeue
ensure listeners/backends
→ return/requeue
ensure DNS
→ verify
→ Ready=True
```

Každý krok je reconstructable z current state-u.

Dlhá blokujúca operácia:

- zvyšuje queue latency;
- komplikuje cancellation;
- drží stale assumptions;
- zvyšuje blast radius pri process failure;
- môže preťažiť external API.

## 9. Optimistic concurrency a conflict recovery

Viac actors môže meniť object.

```text
controller načíta RV10
user alebo iný manager uloží RV11
controller odošle update založený na RV10
→ Conflict
```

Správne:

```text
načítaj latest object
→ over UID/generation/deletion state
→ znovu vypočítaj owned delta
→ patch/update iba intended fields
```

Nesprávne:

- blind retry starej kompletnej reprezentácie;
- force overwrite cudzieho fieldu;
- status write, ktorý omylom vracia starý spec.

## 10. Field ownership a multiple writers

Reconciliation je bezpečná iba pri explicitnom ownership contracte.

Príklad:

```text
PaymentGateway controller owns:
  status
  Service annotations pre external LB
  external LB listeners/backends

platform policy owns:
  Pod security fields

DNS controller owns:
  DNS provider record
```

Ak dva controllers vlastnia rovnaký mutable field alebo external object bez coordination:

```text
controller A nastaví X
→ controller B nastaví Y
→ A deteguje drift a vráti X
→ nekonečná oscillation
```

Oba môžu byť individuálne idempotentné a systém ako celok nekonverguje.

## 11. Status a conditions

Status má odpovedať:

```text
Videl controller latest generation?
Aký external/dependent state vytvoril?
Čo je ready, progressing alebo degraded?
Čo ho blokuje?
Je failure permanent alebo transient?
```

Relevantné fields:

- `observedGeneration`;
- stable condition types;
- machine-readable reasons;
- external resource IDs bez secretov;
- progress counters;
- last known failure summary.

### Failure boundary: stale success status

Controller zmení spec generation 7, no ponechá `Ready=True` z generation 6 bez observedGeneration update-u.

Consumer, ktorý condition neviaže na generation, vyhlási nový rollout za úspešný.

## 12. Condition transitions a retry noise

Condition transition nie je každý reconcile attempt.

Ak stav zostáva:

```text
Ready=False
Reason=DependencyUnavailable
```

`lastTransitionTime` sa nemá meniť pri každom retry. Inak:

- alerting interpretuje permanent failure ako čerstvé zmeny;
- incident timeline sa stratí;
- controller generuje zbytočné writes a vlastné events.

Status update sa má vykonať iba pri semantic zmene.

## 13. Requeue, retry a backpressure

Reconcile môže byť znovu spustený:

- watched eventom;
- explicitným intervalom;
- transient errorom;
- dependency eventom;
- periodic resyncom.

Retry policy potrebuje:

- exponential backoff;
- jitter;
- bounded concurrency;
- per-key deduplication;
- rate limiting;
- permanent/transient classification;
- queue age/depth observability;
- external API protection.

### Failure boundary: hot loop

Permanentne invalid credential vedie k immediate requeue bez backoffu.

```text
reconcile
→ external 401
→ immediate retry
→ vysoké CPU a API traffic
→ ďalšie keys čakajú
→ controller lag rastie
```

Retry bez zmeny vstupu nie je progress.

## 14. Controller chaining

Kubernetes behavior vzniká reťazou owners:

```text
Deployment controller
→ ReplicaSet intent

ReplicaSet controller
→ Pod intent

scheduler
→ Node assignment

kubelet/runtime
→ running containers

EndpointSlice controller
→ service endpoints
```

Každý chain segment má:

- vstupný object subject;
- ownera;
- queue a retry;
- output/dependent subject;
- status/events;
- failure boundary.

Troubleshooting ide downward a overuje, či owner vytvoril správny output pre latest generation.

## 15. Admission vs. reconciliation

### Admission

Synchronný request-time gate:

```text
mutate, validate alebo reject pred persistence
```

### Reconciliation

Asynchrónny ongoing control loop po persistence.

Admission webhook nemá robiť dlhú external orchestration s irreversible side effects. Neskoršia admission vrstva môže request odmietnuť a external resource by zostal bez persisted ownera.

External side effects patria controlleru s:

- stable identity;
- retries;
- status;
- finalizer;
- cleanup;
- observability.

## 16. Partial failure a unknown outcome

Distributed transaction cez API server a cloud API typicky neexistuje.

Atlas failure:

```text
controller odošle CreateLoadBalancer(PG42)
→ cloud LB vznikne
→ response sa stratí
→ controller crashne pred status write
```

Po restarte môže controller vidieť:

- object bez external ID v status-e;
- external LB existujúci pod owner tagom;
- žiadny reliable memory checkpoint.

Správny reconcile external resource adoptuje podľa UID/idempotency key. Nesprávny vytvorí druhý LB.

## 17. Finalizer lifecycle

Controller, ktorý vlastní external state, pridá finalizer **pred** vytvorením resource-u.

```text
ensure finalizer persisted
→ create/manage external state
```

Deletion:

```text
deletionTimestamp observed
→ zastav create/update desired path
→ locate exact external resources podľa UID
→ delete alebo transfer ownership
→ verify absence/closure
→ remove finalizer
```

### Failure boundary: finalizer bez recoverable ownera

Operator/controller bol odinštalovaný, no objects zostali s jeho finalizerom. Delete requests sú stuck.

Recovery potrebuje:

- obnoviť compatible cleanup controller;
- alebo vykonať break-glass external inventory/cleanup;
- až potom finalizer odstrániť.

## 18. Garbage collection a Kubernetes dependents

Kubernetes-native dependents majú používať ownerReferences a garbage collector podľa scope pravidiel.

Controller stále musí rozhodnúť:

- foreground/background/orphan semantics;
- cleanup ordering;
- cross-namespace constraints;
- finalizer interactions;
- external resources mimo API.

Vlastný delete traversal bez UID checks môže zmazať cudzie alebo name-reused objects.

## 19. Leader election

Viac replicas môže používať Lease-based leader election.

Leader election rieši:

```text
ktorá replica aktívne spracúva leader-only loop
```

Nerieši:

- idempotenciu;
- exactly-once execution;
- external unknown outcomes;
- optimistic concurrency;
- short overlap pri lease/partition timing;
- stale in-flight request po leadership loss.

Controller musí byť bezpečný aj vtedy, keď starý leader dokončí request a nový leader začne reconcile bez knowledge o response.

## 20. Broken desired state

Kubernetes spoľahlivo reconcile-uje aj chybný intent:

- neexistujúci image;
- nemožné constraints;
- selector bez targetov;
- príliš nízky memory limit;
- chýbajúci Secret;
- invalid external class;
- circular dependency.

Controller má:

- odmietnuť schema/semantic chybu čo najskôr, ak je deterministická;
- reportovať permanent condition;
- nehot-loopovať;
- neprepisovať user intent, aby status vyzeral green;
- poskytovať actionable reason.

## 21. Drift a ownership policy

Actual state môže byť zmenený mimo controlleru.

Controller podľa contractu:

- drift automaticky vráti;
- adoptuje a zapíše nový desired state iba explicitným workflowom;
- reportuje konflikt;
- vyžaduje human decision;
- prestane mutovať shared field.

Nie každý drift sa má okamžite overwrite-nuť. Pri incidentnom break-glass zásahu musí byť jasné, kto a kedy authoritative ownership obnoví.

## 22. Worked failure: duplicate load balancers po timeoute

PaymentGateway `PG42` generation 7 skončil so statusom:

```text
Ready=False
Reason=Provisioning
externalID: empty
```

Cloud účet obsahoval dva load balancers s podobným názvom.

### Subject inventory

```text
PaymentGateway UID/generation/resourceVersion
controller version, replica a leader timeline
reconcile IDs a queue attempts
external create request IDs
idempotency/owner tags
LB IDs, creation timestamps a configuration
status write audit
finalizer presence timeline
cloud API logs
```

### Competing hypotheses

1. Create response sa stratila a retry vytvoril duplicate.
2. Dve controller replicas konali súčasne po leader transition.
3. Owner lookup používal meno namiesto UID.
4. Old object PG41 zanechal LB a nový PG42 vytvoril ďalší.
5. Status write conflict zmazal external ID.
6. External provider ignoroval idempotency key.
7. User alebo iný controller vytvoril druhý LB.
8. Cache bola stale a nevidela binding object.
9. Finalizer bol pridaný až po external create.
10. Reconcile create path beží pri každom evente namiesto current-state lookup-u.

### Discriminating observation points

- external request/idempotency IDs;
- tags s owner UID;
- controller leader Lease timeline;
- API audit pre status/finalizer writes;
- managedFields/resourceVersion conflicts;
- cloud creation audit caller identities;
- object UID/name histories;
- controller logs s reconcile ID;
- cache sync/read source;
- exact LB configuration a traffic/DNS binding.

### Containment

- zastav ďalší create path pre PG42;
- neodstraňuj náhodný LB podľa mena;
- zachovaj cloud/API/controller audit;
- zafixuj active DNS a backend subject;
- zamedz trafficu na incomplete LB;
- pozastav deletion, kým nie je určený owner každého LB.

### Recovery

- identifikuj canonical LB podľa owner UID, operation key a effective traffic state;
- zapíš verified binding do statusu alebo dedicated objectu;
- odstráň duplicate cez audited cleanup;
- oprav lookup/idempotency protocol;
- zabezpeč finalizer-before-create;
- zaveď status patch s conflict-aware retry;
- otestuj leader failover a lost-response scenár.

### Over pôvodný outcome

Potvrď:

- presne jeden LB pre UID PG42;
- listeners/backends a DNS pre generation 7;
- status observedGeneration 7 a correct external ID;
- žiadny resource pre stale PG41;
- payment transaction exactly once;
- second reconcile je no-op;
- delete test odstráni external state pred finalizer removalom.

### Posuň control skôr

Pridaj deterministic external identity, provider idempotency key, UID-based lookup, request correlation, leader-transition test, unknown-outcome integration test a external-resource inventory alert.

## 23. Worked failure: controller sa self-triggeruje statusom

Controller pri každom reconcile zapisoval aktuálny timestamp do status message.

```text
status write
→ watch update
→ enqueue same key
→ new timestamp
→ ďalší status write
```

Výsledok:

- vysoké CPU;
- vysoký API write rate;
- queue starvation;
- etcd churn;
- noisy events;
- žiadny semantic progress.

Recovery:

- zapisovať status iba pri semantic zmene;
- oddeliť transition time od attempt time;
- filtrovať nerelevantné updates;
- pridať per-key rate limiting;
- overiť queue age a convergence po fix-e.

## 24. Reconciliation observability

Sleduj:

- reconcile count, duration a outcome;
- queue depth a oldest item age;
- requeue/error/backoff rate;
- cache sync a watch reconnects;
- API conflicts a client throttling;
- external API latency, request IDs a rate limits;
- generation lag;
- condition transitions;
- leader identity/transitions;
- finalizer age;
- duplicate/orphan external resources;
- second-reconcile no-op rate podľa controller contractu.

Logs majú obsahovať:

```text
controller
cluster
namespace/name/UID
generation
reconcile ID
queue attempt
action/reason
external resource ID/request ID bez secrets
```

## 25. Diagnostický walkthrough pre nekonvergujúci object

Postup:

```text
1. zafixuj object UID a desired generation
2. porovnaj status observedGeneration a conditions
3. nájdi controller/owner a jeho leader
4. over cache sync, queue a reconcile logs
5. zostav dependent a external inventory
6. over field ownership a conflicts
7. klasifikuj failure ako permanent, transient alebo unknown
8. zachovaj evidence pred restartom/finalizer editom
9. contain-ni side effects
10. obnov authoritative protocol a verify original outcome
```

Nezačni restartom controlleru. Restart môže odstrániť in-memory evidence, zmeniť leadera a vyvolať retry unknown operation.

## 26. Referenčné pravidlá

- Events sú triggers, nie source of truth.
- Reconcile key sa musí premeniť na fresh current-state subject.
- Controller má byť level-based a bezpečný pri opakovaní.
- Idempotencia potrebuje stable resource identity, nie iba retry rovnakého callu.
- Bounded transitions zlepšujú recovery a observability.
- Conflict vyžaduje nový read a prepočet.
- Status musí byť viazaný na observed generation.
- Retry bez backoffu a bez zmeny vstupu môže byť hot loop.
- Leader election neposkytuje exactly-once.
- External side effects potrebujú recoverable binding a finalizer.
- Dvaja idempotentní writers môžu vytvoriť oscillation.
- Second reconcile no-op je dôležitá, ale nie jediná correctness evidence.
- Convergence musí byť overená na effective a business state-e, nie iba na object status-e.

## 27. Kontrolné otázky

1. Aký je rozdiel medzi desired, observed a effective state?
2. Prečo je level-based controller odolnejší než event script?
3. Čo nesie work queue a prečo?
4. Ako cache sync ovplyvňuje correctness?
5. Čo tvorí reconciliation subject?
6. Ako sa controller zotaví z lost create response?
7. Prečo leader election nie je exactly-once garancia?
8. Kedy má controller použiť finalizer?
9. Ako vzniká status self-trigger hot loop?
10. Ako overíš convergence po recovery?

## Glossary impact

Relevantné pojmy: reconciliation subject, level-based control protocol, cache-sync boundary, bounded reconcile transition, external binding subject, unknown reconcile outcome, generation closure, semantic status transition, reconciliation hot loop, UID-based external ownership, finalizer-before-create invariant, second-reconcile evidence, controller convergence verdict a multi-controller oscillation.

## Oficiálna dokumentácia

- [Controllers](https://kubernetes.io/docs/concepts/architecture/controller/)
- [Objects in Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/)
- [Kubernetes API concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/)
- [Owners and dependents](https://kubernetes.io/docs/concepts/overview/working-with-objects/owners-dependents/)
- [Finalizers](https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/)
- [Leases](https://kubernetes.io/docs/concepts/architecture/leases/)
- [Admission webhook good practices](https://kubernetes.io/docs/concepts/cluster-administration/admission-webhooks-good-practices/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: API a object model](api-object-model.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Control plane components →](control-plane-components.md)
<!-- KNOWLEDGE-NAVIGATION:END -->