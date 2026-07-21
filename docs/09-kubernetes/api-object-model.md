# API a object model

Kubernetes API je versionované rozhranie, cez ktoré users, `kubectl`, controllers, operators a node components čítajú a menia cluster state. Kubernetes object je persistentný **record of intent** uložený cez API server. Object model poskytuje spoločnú syntax pre desired state, status, identity, ownership, selection, versioning a lifecycle.

## 1. Resource a object

**Resource type** je API endpoint a schema určitého druhu dát, napríklad Pods, Deployments alebo Nodes.

**Object** je konkrétna inštancia resource type-u:

```text
resource type: pods
object: Pod/default/web-7d9f6b8d9c-x2abc
```

API operácie typicky zahŕňajú:

- `get`,
- `list`,
- `watch`,
- `create`,
- `update`,
- `patch`,
- `delete`.

Podporované verbs sa môžu líšiť podľa resource a subresource.

## 2. Group, version a kind

Kubernetes object identifikuje API schema cez:

- **group** — API family,
- **version** — konkrétna externá API verzia,
- **kind** — typ objektu.

Príklady:

```yaml
apiVersion: v1
kind: Pod
```

```yaml
apiVersion: apps/v1
kind: Deployment
```

Core API group používa skrátené `v1`. Ostatné groups používajú formu `group/version`.

## 3. GVK a GVR

### GVK — GroupVersionKind

Opisuje schema objektu:

```text
apps / v1 / Deployment
```

### GVR — GroupVersionResource

Opisuje REST resource endpoint:

```text
apps / v1 / deployments
```

Kind býva singular CamelCase. Resource býva plural lowercase. Klienti používajú API discovery na mapovanie medzi nimi.

## 4. Povinné polia manifestu

Bežný objekt obsahuje:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web
  namespace: default
spec:
  containers:
    - name: web
      image: nginx:1.27
```

Kľúčové polia:

- `apiVersion` — použitá API group/version,
- `kind` — schema objektu,
- `metadata` — identity a organizačné metadata,
- `spec` — desired state, ak ho resource používa,
- `status` — observed/current state spravovaný systémom.

Presný obsah `spec` a `status` závisí od kind-u.

## 5. `spec` a `status`

### `spec`

Vyjadruje intent používateľa alebo vyššieho controlleru.

Príklady:

- image a containers v Pode,
- počet replicas v Deploymente,
- selector v Service,
- storage request v PVC.

### `status`

Vyjadruje pozorovaný stav:

- Pod phase a conditions,
- available replicas,
- assigned addresses,
- bound volume,
- Node conditions.

Controller nemá prepisovať desired state iba preto, aby sa zhodoval s aktuálnym stavom. Má meniť actual state alebo reportovať status.

## 6. Metadata identity

### `name`

User-defined meno unikátne v príslušnom scope.

### `namespace`

Logická namespaced boundary. Nie všetky resources sú namespaced.

### `uid`

Server-generated immutable identity konkrétnej object inštancie. Zmazaný a znovu vytvorený object s rovnakým menom dostane iné UID.

### `creationTimestamp`

Čas vytvorenia pridelený API serverom.

### `generateName`

Prefix, z ktorého server vytvorí unikátne meno:

```yaml
metadata:
  generateName: batch-
```

Používa sa pre nahraditeľné alebo jednorazové objects.

## 7. Namespaced a cluster-scoped resources

Namespaced resources:

- Pod,
- Deployment,
- ConfigMap,
- Secret,
- Service,
- Role.

Cluster-scoped resources:

- Node,
- Namespace,
- ClusterRole,
- PersistentVolume,
- CustomResourceDefinition.

Overenie:

```bash
kubectl api-resources
```

Namespace nie je iba prefix mena. Ovplyvňuje API path, RBAC, quota, policy a ownership constraints.

## 8. Labels

Labels sú indexovateľné key/value metadata určené na selection a grouping.

```yaml
metadata:
  labels:
    app.kubernetes.io/name: web
    app.kubernetes.io/component: frontend
    environment: production
```

Použitie:

- selectors,
- Service-to-Pod matching,
- controller ownership tracking,
- policy targeting,
- scheduling/topology,
- cost alebo inventory grouping.

Label value má byť stabilná kategória, nie veľký alebo citlivý text.

## 9. Selectors

Label selector vyberá množinu objects.

Equality-based:

```text
app=web
environment!=development
```

Set-based:

```text
environment in (production,staging)
tier notin (cache)
```

Príkaz:

```bash
kubectl get pods -l app=web
```

Selector je často súčasťou controller alebo Service contractu. Nesprávny selector môže adoptovať, ignorovať alebo smerovať traffic na nesprávne Pods.

## 10. Annotations

Annotations ukladajú neidentifikačné metadata:

```yaml
metadata:
  annotations:
    example.com/change-ticket: CHG-1234
    example.com/checksum-config: abcdef
```

Vhodné pre:

- tool metadata,
- external identifiers,
- checksums,
- build/release references,
- controller hints,
- human-readable descriptions.

Annotations nie sú určené na efektívnu selection a nemajú obsahovať secrets.

## 11. `resourceVersion`

`metadata.resourceVersion` reprezentuje storage version objektu alebo collection snapshotu pre:

- optimistic concurrency,
- change detection,
- list/watch continuity.

Nie je to business version ani monotónne číslo, ktoré má application interpretovať numericky.

Pri replace/update môže stale `resourceVersion` viesť ku konfliktu namiesto prepísania novšej zmeny.

## 12. `generation` a `observedGeneration`

`metadata.generation` sa typicky zvyšuje pri relevantnej zmene desired state.

Controller môže v status conditions reportovať `observedGeneration`, aby klient vedel, či status zodpovedá aktuálnemu specu.

```text
metadata.generation = 8
status.observedGeneration = 7
```

Tento stav znamená, že status môže ešte opisovať predchádzajúcu generáciu.

Nie každý resource používa generation a observedGeneration identicky; vždy over konkrétnu API schema.

## 13. List a watch

Controller alebo klient typicky:

1. vykoná `list`,
2. získa current objects a collection `resourceVersion`,
3. otvorí `watch` od tejto version,
4. spracúva create/update/delete events,
5. po prerušení watch obnoví stream alebo vykoná nový list.

Watch je efektívnejší než neustále full polling. Event však nie je authoritative state; klient musí byť schopný znovu zostaviť stav z API.

## 14. Object updates

### Replace/update

Odosiela kompletnú novú reprezentáciu objektu a používa optimistic concurrency.

### Patch

Mení iba vybrané fields. Kubernetes podporuje viac patch typov podľa resource a klienta.

### Apply

Deklaratívne spravuje fields podľa field ownership modelu.

Nemiešaj bez rozmyslu viac management techník a field managers nad rovnakými fields.

## 15. Server-side apply a field ownership

Server-side apply:

- posiela deklaratívny intent,
- API server sleduje field manager ownership v `managedFields`,
- konflikt vznikne, keď iný manager vlastní rovnaký field a zmena nie je force prevzatá,
- rôzni managers môžu bezpečne vlastniť odlišné fields.

Príklad:

```bash
kubectl apply --server-side --field-manager=platform-team -f manifest.yaml
```

`--force-conflicts` používaj iba po pochopení, koho ownership preberáš.

## 16. Subresources

Subresource poskytuje samostatný API endpoint pre časť resource behavior.

Bežné príklady:

- `/status`,
- `/scale`,
- `/exec`,
- `/log`,
- `/portforward`,
- `/eviction`.

Výhoda `/status`:

- controller môže aktualizovať observed state,
- user alebo config manager pritom neprepisuje spec,
- RBAC môže oddeliť oprávnenia na spec a status.

## 17. Conditions

Status conditions sú štruktúrované signály:

```yaml
status:
  conditions:
    - type: Ready
      status: "True"
      reason: MinimumReplicasAvailable
      message: Deployment has minimum availability
```

Dôležité fields:

- `type`,
- `status`,
- `reason`,
- `message`,
- `lastTransitionTime`,
- často `observedGeneration`.

Condition nie je iba event log. Opisuje aktuálne významný aspekt state-u.

## 18. Events

Kubernetes Event je časovo obmedzený diagnostický object viazaný na involved object.

Príklady:

- scheduling failure,
- image pull failure,
- volume attach error,
- probe failure,
- eviction.

```bash
kubectl get events -A --sort-by=.metadata.creationTimestamp
kubectl describe pod web
```

Events nie sú dlhodobý audit trail a môžu byť agregované alebo odstránené retention policy.

## 19. Owner references

Controller vytvára dependent objects s `ownerReferences`.

Príklad hierarchy:

```text
Deployment
└─ ReplicaSet
   └─ Pods
```

Owner reference obsahuje UID ownera, nie iba meno. Pomáha:

- controllers rozlíšiť vlastné dependents,
- garbage collectoru spracovať deletion,
- tools zobraziť hierarchy.

Cross-namespace a scope pravidlá owner references sú obmedzené.

## 20. Garbage collection

Pri zmazaní ownera môže garbage collector spracovať dependents podľa propagation policy:

- background,
- foreground,
- orphan.

Deletion nie je vždy okamžité odstránenie zo storage. Objekt môže vstúpiť do terminating stavu.

## 21. Finalizers

Finalizer je qualified string v `metadata.finalizers`, ktorý blokuje finálne odstránenie objektu, kým príslušný controller nevykoná cleanup.

Deletion flow:

1. user požiada o delete,
2. API server nastaví `deletionTimestamp`,
3. objekt zostáva viditeľný ako terminating,
4. controllers vykonajú cleanup,
5. odstránia svoj finalizer,
6. po vyprázdnení finalizers sa object odstráni.

Ručné odstránenie finalizeru môže opustiť external resources, volumes alebo cloud objects.

## 22. Deletion grace period

Niektoré resources podporujú graceful deletion.

Pri Pode:

- nastaví sa termination intent,
- kubelet spustí shutdown lifecycle,
- po grace period môže process dostať force kill,
- object sa nakoniec odstráni.

API deletion a okamžité ukončenie processu nie sú tá istá operácia.

## 23. API discovery

Klient môže zistiť dostupné groups, versions, resources a verbs.

```bash
kubectl api-resources
kubectl api-versions
kubectl explain deployment
kubectl explain deployment.spec.template.spec.containers
```

Discovery je dôležité, pretože:

- cluster môže mať CRDs,
- niektoré API versions môžu byť vypnuté,
- distribution môže pridať resources,
- klient a server môžu mať odlišné capabilities.

## 24. Validation, defaulting a admission

Pri create/update requeste sa môžu uplatniť:

- decoding a conversion,
- schema validation,
- defaulting,
- mutating admission,
- validating admission,
- policy a quota checks.

Manifest, ktorý je syntakticky validný YAML, nemusí byť validný Kubernetes object.

Použi server-side dry run:

```bash
kubectl apply --dry-run=server -f manifest.yaml
```

Client-side validation nepozná všetky server-side webhooks a dynamic policy.

## 25. API versioning a conversion

Resource môže byť dostupný vo viacerých external API versions. API server môže:

- prijať jednu version,
- convertovať ju na storage version,
- pri čítaní ju vrátiť v requested version.

Upgrade riziká:

- deprecated API version,
- removed API version,
- zmenené defaults,
- conversion loss,
- webhook unavailability,
- CRD schema incompatibility.

Pred upgrade skenuj manifests a live objects na deprecated APIs.

## 26. Custom resources

CustomResourceDefinition pridáva nový resource type do Kubernetes API.

CRD môže definovať:

- group/version/kind,
- schema,
- namespaced alebo cluster scope,
- status subresource,
- scale subresource,
- printer columns,
- conversion webhooks.

CRD sama nevykonáva business logiku. Potrebuje controller/operator alebo external consumer.

## 27. Declarative a imperative management

### Imperative command

```bash
kubectl create deployment web --image=nginx
```

Vhodné pre rýchle learning alebo diagnostic operácie.

### Declarative manifest

```bash
kubectl diff -f manifests/
kubectl apply -f manifests/
```

Vhodné pre version control, review a opakovateľnosť.

Jeden object nemá byť súčasne nejasne spravovaný viacerými technikami a automation vlastníkmi.

## 28. Security hranice API

Request pipeline typicky zahŕňa:

```text
TLS
→ authentication
→ authorization
→ mutating admission
→ validation/defaulting
→ validating admission
→ persistence
```

Chráň:

- kubeconfig a bearer tokens,
- client certificates,
- service account identities,
- API server endpoint,
- admission webhooks,
- audit logs,
- Secrets a etcd encryption,
- field managers a automation credentials.

## 29. Diagnostika objektu

Základný postup:

```bash
kubectl get <resource> <name> -o yaml
kubectl describe <resource> <name>
kubectl get events --field-selector involvedObject.name=<name>
kubectl api-resources
kubectl explain <resource>
```

Kontroluj:

- GVK a namespace,
- spec,
- status a conditions,
- generation/observedGeneration,
- labels/selectors,
- ownerReferences,
- finalizers/deletionTimestamp,
- managedFields,
- events.

## 30. Časté omyly

### `status` je to, čo chcem

`spec` vyjadruje intent. `status` reportuje observed state.

### Meno jednoznačne identifikuje objekt navždy

UID odlišuje zmazanú a znovu vytvorenú inštanciu s rovnakým menom.

### Annotation a label sú zameniteľné

Labels sú určené na selection; annotations na neidentifikačné metadata.

### Delete okamžite odstráni resource

Finalizers a graceful termination môžu objekt ponechať v terminating stave.

### Event je trvalý audit záznam

Events sú krátkodobé diagnostické objekty.

### CRD automaticky poskytuje controller

CRD rozšíri API schema, nie reconciliation behavior.

## 31. Troubleshooting

### `no matches for kind`

Over API group/version, CRD existence, discovery cache a cluster capabilities.

### `field not declared in schema`

Manifest obsahuje typo, nepodporované pole alebo používa inú API version.

### `object has been modified`

Optimistic concurrency conflict. Načítaj nový `resourceVersion`, znovu vyhodnoť zmenu alebo použi správny patch/apply workflow.

### Object ostáva `Terminating`

Over finalizers, owner dependencies a controller, ktorý má vykonať cleanup. Finalizer nemaž naslepo.

### Controller ignoruje objects

Over labels/selectors, namespace, ownerReferences, generation a controller logs.

### Apply hlási field conflict

Pozri `managedFields` a identifikuj iného field managera. Rozhodni ownership namiesto automatického force.

## 32. Kontrolné otázky

1. Aký je rozdiel medzi resource type a objectom?
2. Čo je GVK a čo GVR?
3. Aký je rozdiel medzi `spec` a `status`?
4. Prečo je UID dôležitejšie než meno pri ownership vzťahu?
5. Kedy použiť label a kedy annotation?
6. Na čo slúži `resourceVersion`?
7. Ako funguje list/watch pattern?
8. Čo riešia ownerReferences, garbage collection a finalizers?
9. Aký je rozdiel medzi CRD a controllerom?
10. Ako diagnostikuješ object, ktorý sa nereconcile-uje?

## Glossary impact

Relevantné pojmy: Kubernetes API, Kubernetes resource, Kubernetes object, API group, API version, kind, GVK, GVR, namespaced resource, cluster-scoped resource, spec, status, object UID, resourceVersion, generation, observedGeneration, label, selector, annotation, field manager, server-side apply, subresource, condition, Kubernetes Event, ownerReference, garbage collection, finalizer, deletionTimestamp, API discovery, CustomResourceDefinition a storage version.

## Oficiálna dokumentácia

- [Objects in Kubernetes](https://kubernetes.io/docs/concepts/overview/working-with-objects/)
- [Kubernetes API concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/)
- [Labels and selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/)
- [Annotations](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/)
- [Owners and dependents](https://kubernetes.io/docs/concepts/overview/working-with-objects/owners-dependents/)
- [Finalizers](https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/)
- [Server-side apply](https://kubernetes.io/docs/reference/using-api/server-side-apply/)
- [Custom resources](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/)
