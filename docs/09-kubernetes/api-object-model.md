# API a object model

Kubernetes object nie je iba YAML dokument. Je to versionovaný, serverom spravovaný **record of intent a observed state** s vlastnou identitou, concurrency modelom, field ownershipom, dependent graphom a deletion lifecycle-om.

Dominantný lifecycle:

```text
resource schema a caller intent
→ API request subject
→ decoding, conversion, defaulting a admission
→ persisted object UID/resourceVersion/generation
→ field-manager a selector ownership
→ controller observation a status/conditions
→ dependent graph a external state
→ update, conflict alebo drift
→ deletionTimestamp, finalizers a garbage collection
→ verified cleanup alebo recovery
```

Pri diagnostike sa nepýtaj iba „čo je v manifeste“, ale:

```text
Aký GVK/GVR a cluster boli cieľom?
Aká object UID a generation reálne vznikla?
Kto vlastní relevantné fields?
Ktorý status zodpovedá ktorej generation?
Ktoré dependents a external resources patria tejto UID?
Je object active, replacing, deleting alebo iba menovite rovnaký?
```

## 1. Atlas object subject

Atlas Payments release `4.2.0` používa:

```text
cluster: atlas-prod-eu1
GVK: apps/v1, Kind=Deployment
GVR: apps/v1/deployments
namespace/name: production/payments-api
UID: D42
metadata.generation: 12
resourceVersion: RV9081
field managers:
  atlas-delivery → image, strategy, replicas baseline
  platform-policy → securityContext, tolerations
  payments-hpa → scale replicas
selector: app=payments-api
Pod template digest: PT420
```

Správny object outcome:

```text
request je admitted pre správny GVK a namespace
→ server vytvorí generation 12
→ field ownership ostane konzistentný
→ controller observedGeneration dosiahne 12
→ dependents nesú owner UID D42 a template PT420
→ conditions opisujú generation 12
→ deletion/replacement nezasiahne cudzie objects
```

## 2. Resource type, object a endpoint

Resource type je API schema a REST collection, napríklad:

```text
apps/v1/deployments
```

Object je konkrétna inštancia:

```text
Deployment/production/payments-api UID D42
```

Rozlišuj:

- **GVK** — Group, Version, Kind; schema reprezentácie;
- **GVR** — Group, Version, Resource; REST endpoint;
- **name/namespace** — human-facing scoped meno;
- **UID** — immutable server-generated identita jednej object inštancie.

Object zmazaný a znovu vytvorený s rovnakým menom dostane nové UID. Staré owner references, audit records alebo external bindings nesmú byť automaticky priradené novej inštancii iba podľa mena.

## 3. Request subject

Pred create/update/apply zafixuj:

```text
cluster endpoint a CA
caller identity a groups
verb a subresource
GVR, namespace a name
request content digest
field manager a force-conflict flag
precondition UID/resourceVersion podľa operácie
API discovery/schema generation
admission a policy generation
```

Rovnaký YAML aplikovaný:

- do iného clusteru;
- pod iným field managerom;
- proti inej API version;
- s inou admission konfiguráciou;

nie je rovnaký change subject.

## 4. API request pipeline mení effective object

Zjednodušený write lifecycle:

```text
wire representation
→ decode podľa requested API version
→ conversion do internal/storage modelu
→ defaulting
→ mutating admission
→ validation
→ validating admission/policy/quota
→ persistence
→ response v requested representation
```

Manifest v Git-e preto nemusí byť byte-for-byte zhodný s persisted objectom.

### Failure boundary: green manifest, iný admitted object

Mutating webhook môže:

- prepísať image registry;
- pridať sidecar;
- doplniť labels;
- zmeniť security context;
- pridať toleration;
- vložiť environment variable.

Release evidence musí podľa rizika zachytiť aj **admitted object**, nie iba source YAML.

## 5. `spec`, `status` a generation

`spec` vyjadruje desired state. `status` reportuje observed state.

```text
metadata.generation = 12
status.observedGeneration = 11
```

znamená, že status môže stále opisovať predchádzajúci intent.

### Failure boundary: stale `Available=True`

Deployment generation 12 zmenila image. Status stále obsahoval `Available=True` z generation 11 a controller ešte nový spec nespracoval.

```text
user číta iba condition status
→ ignoruje observedGeneration
→ vyhlási rollout za úspešný
→ traffic stále obsluhuje starý digest
```

Condition je použiteľná iba v kontexte object UID, desired generation a semantics konkrétneho controlleru.

## 6. `resourceVersion` a optimistic concurrency

`resourceVersion` pomáha chrániť pred lost update a podporuje list/watch continuity.

```text
writer A načíta RV10
writer B uloží RV11
writer A pošle replace založený na RV10
→ API vráti conflict
```

Conflict nie je transportný šum. Znamená, že assumption writera o current object state už neplatí.

Správny recovery:

```text
načítaj latest object
→ znovu vyhodnoť intent a ownership
→ vypočítaj nový patch/apply
→ over resulting generation
```

Slepý retry starej kompletnej reprezentácie môže prepísať cudziu legitímnu zmenu.

## 7. List/watch a reconstructable state

Controller typicky používa:

```text
LIST snapshot + collection resourceVersion
→ WATCH changes
→ local cache
→ reconcile key
```

Watch event je notification, nie jediný source of truth. Klient musí vedieť:

- obnoviť watch po prerušení;
- relistovať po expired/compacted version;
- deduplikovať alebo opakovane spracovať events;
- znovu načítať current object;
- tolerovať krátko stale cache.

Business logika nesmie interpretovať `resourceVersion` ako business sequence number.

## 8. Labels a selectors ako dynamic ownership contract

Labels sú machine-selectable identity attributes. Annotations sú neindexované metadata a hints.

Selector môže určovať:

- ktoré Pods vlastní ReplicaSet;
- kam Service smeruje traffic;
- ktoré objects zasiahne policy;
- kde scheduler uplatní topology rules;
- ktoré resources nájde controller.

### Failure boundary: široký selector adoptuje cudzie Pods

Dva controllers použili:

```text
app=payments-api
```

bez environment alebo release boundary. Nový controller začal považovať staré diagnostické Pods za svoj target inventory.

Dôsledky:

- nesprávny replica count;
- neočakávané deletion/adoption;
- Service traffic na debug Pod;
- policy alebo cost attribution na nesprávne objects.

Selector je súčasť stable ownership contractu, nie iba pohodlný filter pre `kubectl get`.

## 9. Server-side apply a field ownership

Server-side apply eviduje field managers v `managedFields`.

Príklad hraníc:

```text
atlas-delivery owns:
  spec.template.spec.containers[*].image
  spec.strategy

platform-policy owns:
  spec.template.spec.securityContext

payments-hpa owns:
  scale/replicas
```

Field conflict je signál prekrytia ownershipu.

### Failure boundary: `--force-conflicts` zruší autoscaler ownership

Delivery pipeline force-applied `spec.replicas: 6` a prevzala field od HPA.

```text
release je green
→ HPA už nevlastní replicas podľa očakávania
→ scale behavior sa zmení
→ peak traffic spôsobí capacity incident
```

Force nie je univerzálny conflict resolver. Je to explicitný ownership transfer s blast radiusom.

## 10. Subresources oddeľujú authority

Relevantné subresources:

- `/status` — observed state;
- `/scale` — replica interface;
- `/exec`, `/log`, `/portforward` — operational access;
- `/eviction` — policy-aware eviction.

Oddelenie umožňuje samostatný RBAC a ownership model.

Application delivery identity nemusí mať právo zapisovať status. Controller nemusí mať právo meniť celý spec. User s `get pods` nemá automaticky právo na `pods/exec`.

## 11. Conditions ako current semantic state

Dobrá condition obsahuje:

```text
type
status: True/False/Unknown
reason
message
lastTransitionTime
observedGeneration podľa API contractu
```

Condition nie je event log. Má opisovať aktuálne relevantný aspekt state-u.

Zlé použitie:

- meniť `lastTransitionTime` pri každom rovnakom retry;
- používať iba voľný text bez stable reason;
- hlásiť `Ready=True` pre starú generation;
- skrývať permanent failure za nekonečný `Progressing=True`.

## 12. Events, audit a status sú tri odlišné evidence

### Status/conditions

Current summarized state resource-u.

### Events

Krátkodobé diagnostické observations, napríklad scheduling alebo pull failure. Môžu byť agregované a expirovať.

### Audit

Request-level evidence o callerovi, verb-e, targete a výsledku podľa audit policy.

Žiadna z týchto vrstiev sama osebe nevysvetľuje celý incident. Event nie je permanentný audit. Audit write nepreukazuje effective workload outcome. Status môže byť stale.

## 13. Owner references a dependent graph

Owner reference používa owner UID.

```text
Deployment D42
└─ ReplicaSet RS84 ownerUID=D42
   └─ Pods P1..P6 ownerUID=RS84
```

Owner references pomáhajú:

- controllerom nájsť svoje dependents;
- garbage collectoru určiť lifecycle;
- tools zostaviť hierarchy.

Scope a namespace pravidlá sú obmedzené. External cloud resource nemá Kubernetes ownerReference; potrebuje vlastný binding a cleanup protocol.

## 14. Garbage collection a propagation

Pri delete ownera môže API garbage collection použiť:

- foreground;
- background;
- orphan propagation.

Voľba ovplyvňuje:

- či owner zostáva viditeľný počas dependent cleanup;
- poradie deletion;
- observability;
- možnosť orphaned dependents;
- interaction s finalizers.

Delete request nie je okamžité fyzické odstránenie všetkých dependents ani runtime processes.

## 15. Finalizers a external cleanup

Finalizer deklaruje:

```text
pred finálnym odstránením musí konkrétny owner dokončiť cleanup
```

Lifecycle:

```text
delete request
→ deletionTimestamp
→ object ostáva viditeľný
→ controller zastaví create/update path
→ vyčistí external alebo dependent state
→ overí cleanup
→ odstráni svoj finalizer
→ object sa odstráni
```

### Failure boundary: ručné odstránenie finalizeru leakne load balancer

Object ostal `Terminating`, preto operator vymazal finalizer bez kontroly external resource identity.

```text
Kubernetes object zmizne
→ cloud load balancer a DNS ostanú
→ billing a attack surface pokračujú
→ nový object s rovnakým menom môže vytvoriť druhý resource
```

Break-glass finalizer removal potrebuje explicitný leak inventory, ownera a následný cleanup.

## 16. Object name reuse a stale identity

Meno nie je lifetime identity.

```text
Deployment production/payments-api UID D41 deleted
Deployment production/payments-api UID D42 created
```

External automation, caches a dependents musia rozlíšiť D41 a D42.

Failure patterns:

- stale controller zapisuje status novej inštancii podľa mena;
- external load balancer tag obsahuje iba namespace/name;
- cleanup D41 zmaže resource patriaci D42;
- audit alebo alert spojí dve nesúvisiace generations.

Stabilný external binding používa UID alebo vlastný collision-safe operation/resource identity.

## 17. API discovery, versions a conversion

Klient musí poznať aktuálne cluster capabilities:

```bash
kubectl api-resources
kubectl api-versions
kubectl explain deployment.spec
```

API version lifecycle môže zahŕňať:

```text
external version v1beta1
→ conversion
→ storage version v1
→ read ako v1
```

Upgrade risks:

- removed API version;
- changed defaults;
- conversion webhook outage;
- lossy conversion;
- CRD schema incompatibility;
- stale client discovery.

YAML syntakticky validný pre jeden cluster/version nemusí byť validný alebo významovo rovnaký v inom.

## 18. CRD nie je controller

CustomResourceDefinition pridáva:

- GVK/GVR;
- schema;
- scope;
- storage/version conversion;
- status/scale subresources podľa konfigurácie.

Nevytvára automaticky business reconciliation.

```text
CR object accepted a persisted
+ žiadny active controller
→ intent existuje
→ external/runtime outcome nevznikne
```

Status, conditions, finalizers a upgrade conversion pre custom resources musia mať rovnakú disciplínu ako core resources.

## 19. Validation a dry-run boundaries

Client-side YAML alebo schema check nepozná celý server state.

```bash
kubectl apply --dry-run=server -f manifest.yaml
```

môže zachytiť:

- server schema/defaulting;
- admission mutation/rejection;
- quota/policy;
- aktuálne dostupné API resources.

Ani server dry-run nepreukazuje, že controller, scheduler, runtime alebo business outcome následne uspejú.

## 20. Worked failure: status je green, release stále používa starý digest

Atlas pipeline aplikovala generation 12 s image digestom `sha256:atlas420`. Dashboard čítal `Available=True` a označil release ako successful. Traffic však stále smeroval na generation 11.

### Subject inventory

```text
cluster identity
Deployment UID D42
metadata.generation 12
resourceVersion timeline
status.observedGeneration 11
condition generation semantics
managedFields a field-manager writes
ReplicaSet owner UID/revision/template hash
Pod image digests
Service/EndpointSlice selected Pod UIDs
admission mutations
```

### Competing hypotheses

1. Dashboard ignoruje `observedGeneration`.
2. Apply smeroval na iný cluster alebo namespace.
3. Admission vrátila old image.
4. Iný field manager prepísal image po apply.
5. Deployment controller nespracoval generation 12.
6. New ReplicaSet vznikol, ale selector vyberá staré Pods.
7. Deployment name bol znovu použitý s novým UID a dashboard mieša histories.
8. Status writer reportuje condition nesprávne.
9. EndpointSlice zaostáva za Pod readiness generation.
10. Mutable tag sa zmenil, dashboard sleduje tag namiesto digestu.

### Discriminating observations

- live object `metadata.uid`, generation, managedFields a spec image;
- audit writes zoradené podľa času a field managera;
- admitted object alebo webhook audit;
- ReplicaSet revisions, owner UID a Pod template hash;
- status observedGeneration;
- Pod exact image IDs/digests;
- EndpointSlice targetRef UIDs a readiness;
- cluster endpoint/CA;
- controller logs pre UID D42.

### Containment

- zastav ďalšie conflicting writes;
- neforce-ni field ownership;
- nevymaž starý ReplicaSet, kým nie je overený service outcome;
- zachovaj live YAML, audit, events a dependents inventory;
- explicitne označ dashboard verdict ako stale/incomplete.

### Recovery

- stale status consumer → viaž verdict na UID + desired/observed generation;
- wrong field owner → obnov authoritative ownership a apply latest intent;
- admission rewrite → oprav policy a validuj admitted object;
- selector mismatch → oprav immutable ownership/selection contract cez nový safe transition;
- controller lag/failure → obnov reconcile path a sleduj generation closure;
- EndpointSlice lag → over Pod readiness a controller/dataplane generation;
- name reuse → oddel histories podľa UID.

### Over pôvodný outcome

Potvrď:

- D42 generation 12 a observedGeneration 12;
- correct image digest v Pod template aj running Pods;
- dependents s correct owner UIDs;
- correct field managers;
- iba new-generation ready endpoints;
- payment transaction cez Service;
- absence old digestu a staging dependency.

### Posuň control skôr

Pridaj UID/generation-aware dashboards, admitted-object diff, field-ownership policy, immutable digest assertions, selector collision tests a endpoint targetRef verification.

## 21. Causal walkthrough: object ostáva `Terminating`

Object s external DNS finalizerom ostáva terminating 40 minút.

### Competing hypotheses

- cleanup controller je down;
- finalizer owner nevlastní credentials;
- external API timeoutuje;
- DNS object už neexistuje, ale lookup používa stale ID;
- finalizer patrí odinštalovanému operatoru;
- dependent object má vlastný finalizer;
- admission alebo RBAC blokuje finalizer update;
- cleanup prebehol, ale status/write response sa stratila.

### Observation points

- UID, deletionTimestamp a finalizer list;
- owner/controller deployment, leader a logs;
- external resource ID a audit;
- dependent graph;
- RBAC `update .../finalizers`;
- API conflicts/resourceVersion;
- request IDs a external lookup.

### Recovery

Najprv obnov alebo nahradi cleanup ownera. Ak je potrebný break-glass removal, vytvor explicitný orphan inventory, zabezpeč manual cleanup a až potom odstráň finalizer s auditom.

## 22. Object inspection workflow

```bash
kubectl get <resource> <name> -n <namespace> -o yaml
kubectl describe <resource> <name> -n <namespace>
kubectl get events -A --sort-by=.metadata.creationTimestamp
kubectl api-resources
kubectl explain <resource>
```

Kontroluj v poradí:

```text
cluster a GVR
→ namespace/name/UID
→ spec a generation
→ managedFields
→ status/observedGeneration/conditions
→ selectors a labels
→ ownerReferences a dependents
→ deletionTimestamp/finalizers
→ events, audit a controller evidence
→ effective runtime/business outcome
```

## 23. Referenčné pravidlá

- YAML je request input; persisted admitted object je server-managed state.
- GVK opisuje schema, GVR endpoint.
- Name nie je lifetime identity; UID je identity jednej object inštancie.
- `resourceVersion` chráni concurrency a watch continuity, nie business ordering.
- `generation` a `observedGeneration` odlišujú intent od spracovaného intentu.
- Condition bez generation contextu môže byť stale.
- Selector je ownership a routing contract.
- `--force-conflicts` je ownership transfer, nie univerzálny fix.
- Status, Events a audit sú odlišné evidence vrstvy.
- Owner references riešia Kubernetes dependents, nie automaticky external resources.
- Finalizer blokuje deletion kvôli cleanup contractu.
- CRD pridáva API schema, nie controller behavior.
- Delete request, object removal a process/external cleanup sú odlišné transitions.

## 24. Kontrolné otázky

1. Aký je rozdiel medzi GVK, GVR a object UID?
2. Prečo source manifest nemusí byť zhodný s admitted objectom?
3. Ako `generation` a `observedGeneration` chránia rollout verdict?
4. Prečo conflict vyžaduje nový read a prepočet?
5. Ako selector ovplyvňuje ownership aj traffic?
6. Čo znamená server-side apply field ownership?
7. Prečo status, Event a audit nie sú zameniteľné?
8. Ako owner references a finalizers spolupracujú pri deletion?
9. Prečo name reuse môže poškodiť external cleanup?
10. Ako diagnostikuješ green condition patriacu starej generation?

## Glossary impact

Relevantné pojmy: Kubernetes object subject, API request subject, admitted object, object UID generation, field ownership subject, generation closure, selector ownership contract, owner-dependent graph, deletion subject, finalizer cleanup contract, name-reuse collision, status evidence subject, API conversion subject a object acceptance verdict.

## Oficiálna dokumentácia

- [Objects in Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/)
- [Kubernetes API concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/)
- [Labels and selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)
- [Annotations](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/)
- [Owners and dependents](https://kubernetes.io/docs/concepts/overview/working-with-objects/owners-dependents/)
- [Finalizers](https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/)
- [Server-side apply](https://kubernetes.io/docs/reference/using-api/server-side-apply/)
- [Custom resources](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Kubernetes architecture](kubernetes-architecture.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Desired state a reconciliation loops →](desired-state-reconciliation-loops.md)
<!-- KNOWLEDGE-NAVIGATION:END -->