# ReplicaSet

ReplicaSet je Kubernetes controller pre jednu množinu navzájom zameniteľných Pod replík. Jeho základný contract nie je „udržuj konkrétne Pod mená“, ale „udržuj požadovaný počet Podov, ktoré patria do môjho selector a ownership boundary a vznikajú z môjho Pod template-u“.

Dominantný lifecycle tejto kapitoly:

```text
ReplicaSet UID, generation, desired replicas a selector
→ list/watch matching Pods
→ classify controlled, adoptable, terminating a failed Pods
→ compare desired count s active controlled count
→ bounded create, delete alebo adoption decision
→ nový Pod UID z template-u
→ scheduler a worker-node execution
→ ready/available replica evidence
→ Service a business verification
→ scale, drift, deletion alebo higher-level rollout recovery
```

Pri diagnostike sa nepýtaj iba „koľko Podov vidím“. Pýtaj sa:

```text
Ktorý ReplicaSet UID a generation ich má vlastniť?
Ktoré Pods iba matchujú selector a ktoré majú správny controller ownerReference?
Počítam active, ready, available alebo terminating replicas?
Kto vlastní desired replica field: ReplicaSet, Deployment, HPA alebo GitOps?
```

## 1. Atlas replica subject

Atlas Payments Deployment generation 12 vytvoril ReplicaSet:

```text
Deployment UID: D42
ReplicaSet: production/payments-api-7d6f9d8b7b
ReplicaSet UID: RS42
ReplicaSet generation: 3
Pod template hash: 7d6f9d8b7b
desired replicas: 6
selector:
  app.kubernetes.io/name=payments-api
  pod-template-hash=7d6f9d8b7b
image digest: sha256:4a20...
config generation: C52
secret epoch: SE08
```

Pôvodný outcome:

- presne šesť active Pods vlastní RS42;
- všetky vznikli z rovnakého admitted template-u;
- šesť Pods je Ready a po `minReadySeconds` dostupných pre Deployment;
- Service nevyberá cudzie alebo staré Pods;
- scale-down neodstráni nevhodnú repliku kvôli nejasnej identite;
- ďalší reconcile bez zmeny vstupu je no-op.

## 2. Selector je control boundary

ReplicaSet selector nie je iba filter pre `kubectl get`. Je to vstup controlleru pre určenie candidate množiny Podov.

```text
selector match
+ namespace scope
+ ownerReference/adoption pravidlá
+ Pod lifecycle classification
→ controller-visible replica set
```

Pod, ktorý matchuje selector, nemusí automaticky patriť ReplicaSetu. Rozlišuj:

- **controlled Pod** — ownerReference ukazuje na UID ReplicaSetu s controller ownershipom;
- **adoptable Pod** — matchuje selector a nemá conflicting controller ownera;
- **foreign Pod** — matchuje labels, ale vlastní ho iný controller;
- **orphaned Pod** — nemá pôvodného controllera po orphan deletion alebo manual zásahu;
- **non-matching Pod** — labels sa zmenili a controller ho už nepočíta.

Prekrývajúce selectors dvoch ReplicaSetov v jednom namespace vytvárajú conflicting instructions a nepredvídateľnú ownership boundary.

## 3. Selector a template labels musia tvoriť jeden contract

Minimálny tvar:

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: payments-api-7d6f9d8b7b
spec:
  replicas: 6
  selector:
    matchLabels:
      app.kubernetes.io/name: payments-api
      pod-template-hash: 7d6f9d8b7b
  template:
    metadata:
      labels:
        app.kubernetes.io/name: payments-api
        pod-template-hash: 7d6f9d8b7b
    spec:
      containers:
        - name: payments-api
          image: registry.atlas.example/payments-api@sha256:4a20...
```

Template labels musia spĺňať selector. Selector je po vytvorení zásadná identity boundary; rollout-mutable hodnoty sa riešia novým ReplicaSetom cez Deployment, nie nejasným prepisom existujúceho selectoru.

## 4. Reconciliation subject

ReplicaSet controller pri každom reconcile rekonštruuje subject:

```text
cluster a namespace
ReplicaSet UID/resourceVersion/generation
spec.replicas
selector
Pod template hash a effective spec
matching Pod UID inventory
ownerReferences a lifecycle state
higher-level owner a field ownership
```

Potom vypočíta bounded delta:

```text
active controlled Pods < desired
→ vytvor chýbajúce Pod objects

active controlled Pods > desired
→ vyber Pods na deletion podľa controller policy

matching orphan/adoptable Pod existuje
→ adoptuj iba pri splnení ownership pravidiel

spec/status alebo cache je stale
→ nový read a prepočet, nie slepý opakovaný write
```

ReplicaSet controller vytvára Pod objects. Scheduler vyberá Nodes a kubelet realizuje containers. `FailedCreate` je teda pred schedulingom; `Pending` po vytvorení Podu je nižšia boundary.

## 5. Active, current, ready a available nie sú jedno číslo

ReplicaSet status môže obsahovať viac countov:

```text
spec.replicas
→ desired count

status.replicas
→ observed replica objects podľa controller semantics

status.readyReplicas
→ Pods s Ready condition

status.availableReplicas
→ Pods spĺňajúce availability timing/condition model

terminating Pods
→ môžu stále spotrebúvať resources alebo krátko obsluhovať traffic
```

Príklad:

```text
desired=6
replicas=6
ready=4
available=3
```

Replica count je správny, ale release capacity a Service eligibility nie. Controller splnil iba časť chainu.

## 6. Pod creation a immutable lineage

Pri scale-up alebo replacement-e ReplicaSet vytvorí nový Pod:

- s novým name a UID;
- s labels a spec z Pod template-u;
- s ownerReference na ReplicaSet UID;
- bez state-u predchádzajúceho Podu;
- s novým scheduling a worker-node lifecycle-om.

Lineage:

```text
Deployment D42 generation 12
→ ReplicaSet RS42 template hash 7d6f9d8b7b
→ Pod P42 admitted spec
→ Node N7 execution
```

Ručná oprava existujúceho Podu sa neprenesie do replacement-u. Autoritatívna zmena patrí do vyššieho template-u.

## 7. Replacement nie je container restart

```text
container restart
→ rovnaký Pod UID
→ kubelet a restartPolicy

Pod replacement
→ nový Pod UID
→ ReplicaSet count reconciliation
→ nový scheduler/node lifecycle
```

Ak application container padá, ReplicaSet nemusí okamžite vytvoriť nový Pod, pretože pôvodný Pod object stále existuje a počíta sa medzi replicas. Preto `replicas=6` môže koexistovať s nulovou readiness.

## 8. Scale-up lifecycle

```text
spec.replicas 4 → 6
→ controller pozoruje delta +2
→ vytvorí dva Pod objects
→ scheduler ich pridelí
→ kubelet ich spustí
→ readiness a availability sa reportujú späť
```

Scale-up môže byť blokovaný po Pod create:

- scheduler capacity alebo topology;
- image, CNI, CSI alebo config;
- startup/readiness;
- quota/admission ešte pred Pod persistence;
- external readiness gate.

ReplicaSet `status.replicas=6` nepreukazuje business throughput šiestich replicas.

## 9. Scale-down lifecycle

Pri scale-down controller vyberie konkrétne Pods na deletion podľa interných pravidiel a dostupných preferencií.

Application nesmie predpokladať, že prežije konkrétny Pod name, Node alebo local cache. Pri potrebe ovplyvniť preferenciu odstránenia existujú annotations, napríklad Pod deletion cost, ale ide o preferenciu, nie durable per-replica identity contract.

Bezpečný scale-down vyžaduje:

- readiness a traffic drain;
- termination grace;
- dostatok remaining capacity;
- žiadny unique local durable state;
- správny higher-level HPA/Deployment ownership;
- business verification po znížení kapacity.

## 10. Adoption

ReplicaSet môže adoptovať matching Pod bez conflicting controller ownera.

Mechanizmus:

```text
orphan Pod matchuje selector RS42
→ controller overí, že RS42 nie je deleting a ownership je prípustný
→ zapíše ownerReference na RS42 UID
→ Pod sa začne počítať do desired replica countu
```

Adoption je užitočná pre zotavenie z controller/owner race, ale nebezpečná pri broad selectors a debug Pods.

Adoptovaný Pod nemusel vzniknúť z aktuálneho template-u. Preto musíš porovnať:

- image digest;
- config a secret subject;
- service account a security context;
- probes a resources;
- owner history;
- business eligibility.

Selector match nepreukazuje template equivalence.

## 11. Orphaning a deletion propagation

Pri deletion ownera môžu dependents:

- zaniknúť cez foreground/background garbage collection;
- zostať orphaned;
- byť neskôr adoptované iným compatible controllerom.

Orphaning mení ownership, nie runtime content. Ponechaný Pod môže ďalej prijímať traffic, aj keď jeho pôvodný controller už neexistuje.

Break-glass orphan workflow potrebuje:

```text
Pod UID inventory
→ effective template/digest verification
→ nový authoritative owner alebo explicitný retirement
→ Service selector review
→ cleanup starých owner references a histories
```

## 12. Higher-level owner: Deployment

V bežnej stateless prevádzke ReplicaSet vlastní Deployment.

```text
Deployment D42
├─ old ReplicaSet RS41, replicas=0
└─ new ReplicaSet RS42, replicas=6
   └─ Pods
```

Deployment vlastní:

- revision a Pod template transition;
- scale rozdelenie medzi old/new ReplicaSets počas rollout-u;
- rolling strategy;
- revision history a rollback subject.

Ručný scale alebo edit child ReplicaSetu je write na nesprávnej vrstve desired state-u a vyšší controller ho môže prepísať.

## 13. Replica field ownership

Desired count môže ovplyvňovať:

- Deployment controller;
- HPA cez scale subresource;
- GitOps alebo manifest manager;
- manual `kubectl scale`;
- custom autoscaler.

Pred zmenou zisti:

```text
Kto vlastní Deployment .spec.replicas alebo /scale?
Je ReplicaSet samostatný alebo child revision?
Prebieha rollout s viacerými active ReplicaSets?
Ktorý writer vykonal posledný scale transition?
```

Dva writers s odlišnými desired counts môžu vytvoriť oscillation bez toho, aby bol ktorýkoľvek jednotlivo „neidempotentný“.

## 14. Service selector je iný contract než ReplicaSet selector

ReplicaSet selector určuje controller candidate Pods. Service selector určuje network backends.

```text
ReplicaSet selector
→ ownership/count reconciliation

Service selector
→ EndpointSlice membership a traffic
```

Ak je Service selector širší, môže posielať traffic na:

- debug Pod bez controller ownera;
- starý ReplicaSet;
- canary alebo migration helper;
- Pod s rovnakou `app` label, ale inou release identity.

Controller count môže byť správny a Service path nesprávny.

## 15. Status, Events a observed generation

Status verdict viaž na:

```text
ReplicaSet UID
+ metadata.generation
+ status.observedGeneration
+ desired/current/ready/available counts
+ Pod UID inventory
+ exact observation time
```

Events pomáhajú vysvetliť `FailedCreate`, admission, quota alebo deletion, ale nie sú trvalý audit. Audit logs a live ownerReferences sú potrebné pri adoption alebo conflicting writer incidente.

## 16. Failure boundary: `FailedCreate`

ReplicaSet potrebuje úspešne vytvoriť Pod object. Request môže zlyhať kvôli:

- admission policy alebo webhook;
- ResourceQuota;
- PodSecurity alebo security policy;
- invalid/missing ServiceAccount;
- schema alebo Pod template problému;
- API/etcd write failure;
- rate limiting alebo permissions.

Scheduler, image pull ani kubelet nie sú relevantné, kým Pod object nevznikol.

## 17. Failure boundary: count je správny, workload nie

```text
spec.replicas=6
status.replicas=6
status.readyReplicas=0
```

ReplicaSet už vytvoril objekty. Ďalšia diagnóza ide cez Pods:

```text
Pod scheduling
→ worker-node execution
→ startup/readiness
→ Service eligibility
→ application outcome
```

Scale-up na 12 môže iba zdvojnásobiť počet nefunkčných Podov a zvýšiť pressure.

## 18. Failure boundary: labels sa zmenili na live Pode

Ak actor odstráni selector label z controlled Podu:

```text
Pod stále beží
→ ReplicaSet ho prestane počítať ako matching
→ vytvorí replacement
→ pôvodný Pod môže zostať bez správneho Service/owner contractu
```

Ak Service selector pôvodný Pod stále vyberá cez inú label, môže dočasne existovať viac traffic-serving processes než desired replicas.

Ručná relabel operácia je preto state transition s controller aj routing dôsledkami.

## 19. Worked failure: debug Pod bol adoptovaný a production Pod odstránený

Engineer vytvoril debug Pod:

```yaml
metadata:
  labels:
    app.kubernetes.io/name: payments-api
    pod-template-hash: 7d6f9d8b7b
```

Pod nemal controller ownerReference a matchoval RS42. ReplicaSet ho adoptoval. Pri desired count 6 controller následne videl šesť controlled Pods vrátane debug Podu a pri ďalšom scale-down odstránil jednu production repliku.

Dôsledky:

- debug image dostalo production service account;
- Service selector ho zaradil medzi endpoints;
- replica count zostal „správny“;
- effective release identity bola zmiešaná;
- production capacity klesla.

Root cause nebol scheduler ani náhodný scale-down. Bol to selector/adoption contract.

## 20. Worked failure: ručný scale child ReplicaSetu sa stratil

Operator zmenil RS42 z 6 na 10 replicas, aby riešil load. Deployment a HPA naďalej vlastnili higher-level desired count 6.

```text
manual child scale
→ dočasne 10 Podov
→ Deployment/HPA reconcile
→ RS42 späť na 6
```

Správna recovery vrstva je Deployment `/scale` alebo HPA policy. Child ReplicaSet nie je authoritative scale subject.

## 21. Worked failure: broad Service selector maskoval ReplicaSet correctness

RS42 vlastnil presne šesť správnych Pods, ale Service selector bol iba `app=payments-api`. Vybral aj dva staré Pods z RS40 bez template-hash restriction.

ReplicaSet status bol green. Business requests však náhodne používali starý protocol. Potrebné bolo diagnostikovať EndpointSlice targetRef UIDs a Service selector, nie meniť ReplicaSet count.

## 22. Causal troubleshooting walkthrough: po debug zásahu zmizla jedna production replika

Symptóm:

```text
RS42 desired=6, replicas=6, ready=5
Service má 6 ready endpoints
jeden endpoint beží z debug image
jedna pôvodná production Pod UID chýba
```

### 1. Zafixuj subject a pôvodný outcome

Zaznamenaj:

```text
Deployment D42 generation/revision
ReplicaSet RS42 UID/generation/resourceVersion
selector a Pod template hash
spec/status counts
všetky matching Pod UIDs, labels a ownerReferences
imageID, C52 a SE08 pre každý Pod
Service selector a EndpointSlice targetRefs
scale/write audit timeline
Pod deletion Events a grace state
required six-replica business outcome
```

### 2. Competing hypotheses

1. HPA alebo Deployment znížil desired count.
2. ReplicaSet scale-down náhodne odstránil Pod po reviewovanom scale transitione.
3. Debug Pod bol adoptovaný a započítaný do desired countu.
4. Service vyberá debug Pod, ale ReplicaSet ho nevlastní.
5. Dva ReplicaSets majú prekrývajúce selectors.
6. Production Pod stratil selector label a ReplicaSet vytvoril náhradu.
7. Pod bol evicted alebo preempted a replacement ešte nie je Ready.
8. Debug Pod použil rovnaké meno/label, ale iný UID a dashboard mieša histories.
9. ReplicaSet status/observedGeneration je stale.
10. Manual field manager alebo GitOps menil child ReplicaSet.
11. Old terminating Pod je stále endpointom.
12. Deployment rollout rozdelil replicas medzi dva active ReplicaSets.

### 3. Discriminating observation points

- live RS42 spec, status, observedGeneration a managed fields;
- matching Pods s UIDs, ownerReferences, creation times a images;
- API audit pre Pod ownerReference/label a scale writes;
- Deployment old/new ReplicaSet inventory a revision annotations;
- HPA desired/current metrics a scale Events;
- Pod deletion reason, controller reference a timeline;
- Service selector a EndpointSlice targetRef UIDs;
- controller-manager logs korelované podľa RS42 UID;
- overlap query pre selectors ostatných ReplicaSets;
- effective business telemetry per Pod UID/image digest.

OwnerReference na RS42 pri debug Pode diskriminuje adoption od iba broad Service selection. Chýbajúci controller owner pri debug Pode by posunul routing problém do Service boundary.

### 4. Containment

- odstráň debug Pod z trafficu explicitnou bezpečnou label/policy zmenou, ale najprv zachovaj owner/audit evidence;
- zastav ďalšie manual label a child-RS writes;
- nevymaž náhodne matching Pods podľa mena;
- ponechaj healthy production endpoints;
- pozastav rollout/scale-down, ak controller naďalej koná nad zmiešanou množinou;
- audituj credentials a operations vykonané debug image-om.

### 5. Recovery podľa boundary

- adopted debug Pod → vytvor audited retirement, odstráň ho z Service aj RS ownershipu a nechaj RS vytvoriť correct replacement;
- broad Service selector → zaveď release/workload identity contract bez prekrývania;
- overlapping ReplicaSets → oddel selectors a vykonaj reviewovaný owner transition;
- label drift → obnov authoritative template/labels cez higher-level controller;
- wrong scale writer → oprav Deployment/HPA field ownership;
- eviction/Node failure → dokonči replacement chain a readiness;
- stale status → počkaj na generation closure alebo obnov controller queue.

### 6. Over pôvodný outcome

Potvrď:

- RS42 vlastní presne šesť Pods s correct ownerReference;
- každý Pod má expected template hash, digest, C52 a SE08;
- žiadny debug ani old-revision Pod nematchuje Service;
- šesť Pods je Ready/Available podľa rollout contractu;
- EndpointSlice targetRef UIDs presne zodpovedajú production inventory;
- payment transaction prejde cez všetky backend cohorts;
- ďalší reconcile je no-op;
- debug credentials a side effects boli auditované a revoked/contained.

### 7. Posuň control skôr

Pridaj:

- admission policy blokujúcu reserved controller labels pre ad-hoc Pods;
- selector overlap test v CI/admission;
- Service-to-controller selector consistency test;
- dashboard viazaný na owner UID, template hash a image digest;
- alert na adoption alebo orphaned production-label Pod;
- zákaz manual child-ReplicaSet writes;
- per-Pod UID release telemetry.

## 23. ReplicaSet observation matrix

| Boundary | Subject | Kľúčové observations |
|---|---|---|
| Desired count | RS UID/generation | spec.replicas, field manager, higher owner |
| Selection | selector + namespace | matching Pod UID inventory, overlap |
| Ownership | RS UID ↔ Pod UID | ownerReferences, adoption/audit |
| Template | hash + effective spec | labels, image digest, config/security |
| Creation | Pod create request | Events, admission, quota, API write |
| Execution | Pod UID chain | scheduling, Node, readiness, imageID |
| Status | observedGeneration/counts | replicas, ready, available, terminating |
| Routing | Service/EndpointSlice | selectors, targetRef UIDs, endpoint state |
| Business | operation ID + backend UID | SLI, protocol, downstream audit |

## 24. Referenčné príkazy

```bash
kubectl get rs <rs> -n <namespace> -o yaml
kubectl describe rs <rs> -n <namespace>
kubectl get pods -n <namespace> -l '<selector>' -o wide
kubectl get pod <pod> -n <namespace> -o yaml
kubectl get deployment <deployment> -n <namespace> -o yaml
kubectl get hpa -n <namespace> -o yaml
kubectl get endpointslice -n <namespace> -o yaml
kubectl get events -A --sort-by=.metadata.creationTimestamp
```

## 25. Referenčné pravidlá

- ReplicaSet udržiava count nad selector a ownership boundary, nie konkrétne Pod mená.
- Selector match a controller ownership nie sú to isté.
- Adoptovaný Pod nemusel vzniknúť z aktuálneho template-u.
- Prekrývajúce selectors vytvárajú conflicting controller instructions.
- Replica count nie je readiness, availability ani business capacity.
- `FailedCreate` nastáva pred scheduler a kubelet boundary.
- Container restart nie je ReplicaSet replacement.
- Ručná oprava Podu sa neprenesie do template-u.
- Deployment alebo HPA môže prepísať manual scale child ReplicaSetu.
- ReplicaSet selector a Service selector majú odlišný účel a musia byť konzistentné.
- Scale-down potrebuje termination a capacity verification.
- Recovery musí overiť owner UIDs, effective templates, endpoints aj business outcome.

## 26. Kontrolné otázky

1. Aký subject ReplicaSet skutočne reconcile-uje?
2. Prečo selector nie je iba query filter?
3. Ako sa líši matching Pod od controlled Podu?
4. Kedy môže ReplicaSet adoptovať Pod?
5. Prečo adoptovaný Pod nemusí byť template-equivalentný?
6. Ako sa líšia replicas, readyReplicas a availableReplicas?
7. Prečo `FailedCreate` nie je scheduler problém?
8. Kto má meniť scale child ReplicaSetu vlastneného Deploymentom?
9. Ako môže Service posielať traffic mimo correct ReplicaSet inventory?
10. Čo musí ReplicaSet recovery verdict overiť?

## Glossary impact

Relevantné pojmy: ReplicaSet reconciliation subject, selector control boundary, controlled Pod, adoptable Pod, foreign Pod, orphaned Pod, template-equivalence verdict, active replica subject, ReplicaSet scale subject, child-ReplicaSet ownership, adoption event, selector overlap, Service-to-ReplicaSet selection drift, ReplicaSet observation matrix a replica-set acceptance verdict.

## Oficiálna dokumentácia

- [ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/)
- [Workload management](https://kubernetes.io/docs/concepts/workloads/controllers/)
- [Labels and selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)
- [Owners and dependents](https://kubernetes.io/docs/concepts/overview/working-with-objects/owners-dependents/)
- [Garbage collection](https://kubernetes.io/docs/concepts/architecture/garbage-collection/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Pod](pod.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Deployment →](deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
