# API a object model

Kubernetes riadi systém cez versionované API objekty. YAML súbor nie je sám o sebe „resource v clusteri“; je to jeden možný zápis requestu, z ktorého API server po autentizácii, autorizácii, defaultingu, admission a validácii vytvorí uložený objekt. Pri čítaní manifestu preto nestačí poznať názvy fields. Potrebujeme rozumieť identite objektu, jeho generácii, vlastníctvu fields a rozdielu medzi požadovaným stavom v `spec` a pozorovaným stavom v `status`.

Budeme pokračovať s Deploymentom `production/payments-api`. Pipeline chce zmeniť image na digest release `4.2.0` a configuration generation na `C52`. Rovnaké meno `payments-api` môže existovať v inom namespace, starý objekt mohol byť zmazaný a vytvorený nanovo s novým UID a viac automation nástrojov môže vlastniť rôzne fields. Presná identita je preto dôležitejšia než názov zobrazený v termináli.

## Ako API identifikuje typ objektu

Manifest začína kombináciou `apiVersion` a `kind`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payments-api
  namespace: production
```

`apiVersion` určuje API group a version. `kind` pomenúva typ objektu v dokumente. Klienti pri práci s API používajú aj resource endpoint, napríklad `deployments`. V praxi sa preto stretneme s dvoma pohľadmi:

```text
GVK: group / version / kind
GVR: group / version / resource
```

GVK je prirodzený pri YAML a serializovaných objektoch. GVR sa používa pri REST endpointoch a discovery. Overiť serverom podporované resources možno takto:

```bash
kubectl api-resources
kubectl api-versions
kubectl explain deployment.spec.template.spec.containers
```

`kubectl explain` číta schema informácie pre konkrétnu API verziu. Neoveruje však, že celý manifest prejde admission policies alebo že použitý image je povolený.

## Metadata vytvárajú identitu a lifecycle

Kubernetes objekt má `metadata.name` a podľa scope aj `metadata.namespace`. Server mu pri vytvorení pridelí `metadata.uid`. UID odlišuje dve rôzne životnosti objektu s rovnakým menom.

```bash
kubectl get deployment payments-api -n production \
  -o custom-columns='NAME:.metadata.name,UID:.metadata.uid,GEN:.metadata.generation,RV:.metadata.resourceVersion'
```

`generation` sa zvyšuje pri relevantnej zmene desired state-u. `resourceVersion` označuje verziu uloženého objektu a používa sa pri watches a optimistic concurrency. Tieto dve hodnoty nie sú zameniteľné. Controller často porovnáva `.status.observedGeneration` s `.metadata.generation`, aby ukázal, či už spracoval najnovšiu želanú generáciu.

```bash
kubectl get deployment payments-api -n production \
  -o jsonpath='{.metadata.generation}{"\t"}{.status.observedGeneration}{"\n"}'
```

Ak je `generation=12` a `observedGeneration=11`, API zmenu prijalo, ale Deployment controller ešte nepotvrdil spracovanie najnovšej generácie.

## `spec` a `status` nie sú dva názvy pre to isté

`spec` vyjadruje požadovaný stav. `status` je pozorovanie, ktoré zapisuje controller alebo agent oprávnený používať status subresource.

Zjednodušený Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payments-api
  namespace: production
spec:
  replicas: 6
  selector:
    matchLabels:
      app: payments-api
  template:
    metadata:
      labels:
        app: payments-api
    spec:
      containers:
        - name: api
          image: registry.example.com/atlas/payments-api@sha256:payments420
status:
  observedGeneration: 12
  replicas: 6
  readyReplicas: 6
  availableReplicas: 6
```

Bežný používateľ deklaruje `spec`, nie `status`. Ak lokálne pridáme falošné `readyReplicas: 6`, API server ho pri bežnom apply neprevezme ako dôkaz reality. Status vzniká z observation control loopu.

Ani `availableReplicas: 6` ešte nepotvrdzuje správnu konfiguráciu aplikácie alebo úspešnú payment transakciu. Je to controller-level výsledok založený na Pod readiness a Deployment availability pravidlách.

## Conditions sú vysvetliteľný stav, nie jednoduchý boolean

Mnohé objekty používajú `status.conditions`. Condition má typ, status, reason, message a transition time. Napríklad Deployment môže mať `Available=True` a zároveň `Progressing=False` s reason `ProgressDeadlineExceeded`.

```bash
kubectl get deployment payments-api -n production \
  -o jsonpath='{range .status.conditions[*]}{.type}{"="}{.status}{" reason="}{.reason}{"\n"}{end}'
```

Condition treba čítať spolu s `observedGeneration`. Starý zelený condition nemusí patriť k aktuálnej generácii. Tiež nemožno predpokladať, že každý `False` znamená incident; význam závisí od typu condition.

## Labels a selectors vytvárajú dynamické skupiny

Labels sú indexované metadata používané na výber objektov. Service, ReplicaSet a mnoho nástrojov pracuje cez selectors.

```yaml
metadata:
  labels:
    app: payments-api
    component: api
    environment: production
```

```bash
kubectl get pods -n production -l app=payments-api,component=api
```

Label nie je nemenná identita. Zmena labelu môže Pod odstrániť zo Service selectoru alebo ho priradiť k nesprávnej automation skupine. Ownership a release identitu preto neviažeme iba na label; používame ownerReferences, UID, template hash a immutable artifact identity.

Annotations sú neindexované metadata pre integrácie, build information alebo checksums. Nemajú automatickú bezpečnostnú autoritu. Controller môže interpretovať konkrétnu annotation, ale jej význam musí byť definovaný daným controllerom.

## Namespaced a cluster-scoped objekty

Deployment, Pod, Service, ConfigMap alebo Secret sú namespaced. Node, Namespace, PersistentVolume a ClusterRole sú cluster-scoped.

```bash
kubectl api-resources --namespaced=true
kubectl api-resources --namespaced=false
```

Namespace tvorí dôležitú organizačnú, policy a naming boundary, ale nie je automaticky úplnou tenant izoláciou. Cluster-scoped resources, Nodes, CRDs, webhooks, storage backends a zle navrhnuté RBAC môžu prekročiť namespace hranicu.

Pri každom príkaze je bezpečnejšie uviesť namespace explicitne:

```bash
kubectl get deployment payments-api -n production
```

Inak môže aktuálny context použiť iný default namespace a rovnaký názov v stagingu vytvorí presvedčivý, ale nesprávny výsledok.

## Object creation, replacement a immutable fields

Nie všetky fields možno meniť in-place. Niektoré zmeny API odmietne, iné controller realizuje vytvorením novej dependent generation. Deployment zmena `.spec.template` vytvorí nový ReplicaSet a nové Pods. Zmazanie a opätovné vytvorenie Service s rovnakým menom vytvorí nový UID a môže zmeniť pridelené hodnoty.

```text
rovnaký namespace/name
+ nový UID
→ nový object lifetime
```

Pre incident timeline preto nestačí povedať „Service existuje“. Potrebujeme vedieť, či ide o rovnaký UID ako pred zmenou.

## Server-side apply a field ownership

Viac nástrojov môže meniť jeden objekt. Server-side apply eviduje field managerov v `metadata.managedFields`. To umožňuje zistiť, kto vlastní konkrétne fields a odhaliť konflikty.

```bash
kubectl get deployment payments-api -n production \
  -o json | jq '.metadata.managedFields[] | {manager,operation,apiVersion}'
```

Praktický apply s explicitným managerom:

```bash
kubectl apply --server-side \
  --field-manager=atlas-release \
  -f deployment.yaml
```

Ak HPA vlastní `.spec.replicas`, GitOps manifest by nemal neustále prepisovať rovnaké pole na statickú hodnotu. Dvaja správne fungujúci controllers môžu vytvoriť oscillation, ak im pridelíme konfliktné ownership contracts.

`--force-conflicts` nie je bežná oprava. Znamená násilné prevzatie fields a vyžaduje vedomé rozhodnutie o zmene autority.

## Optimistic concurrency a bezpečná zmena

API server používa `resourceVersion` na zabránenie slepému prepísaniu novšieho stavu. Pri čítaj–zmeň–zapíš cykle môže klient dostať conflict, ak sa objekt medzitým zmenil.

```bash
kubectl get deployment payments-api -n production -o yaml > deployment.current.yaml
```

Ručné úpravy starého exportu a neskorší replace môžu prepísať medzitým vykonané zmeny. Deklaratívny apply s jasným field ownershipom je preto bezpečnejší než pravidelné nahrádzanie celého objektu.

## OwnerReferences a garbage collection

Dependent objekty môžu odkazovať na owner UID. ReplicaSet vlastní Pods, Deployment vlastní ReplicaSets.

```bash
kubectl get pod -n production <pod> \
  -o jsonpath='{.metadata.ownerReferences}' | jq .
```

Garbage collector používa ownerReferences pri kaskádovom odstraňovaní. Reference je viazaná na UID, nie iba na meno. To zabraňuje tomu, aby nový objekt s rovnakým názvom automaticky zdedil starých dependents.

OwnerReference však nie je business ownership. Databáza alebo cloud load balancer môžu existovať mimo Kubernetes API a ich lifecycle môže vyžadovať finalizer alebo samostatný controller.

## Finalizers odkladajú fyzické odstránenie

Pri delete requeste objekt často najprv dostane `deletionTimestamp`. Ak má finalizers, zostane v terminating stave, kým príslušný controller nedokončí cleanup a finalizer neodstráni.

```bash
kubectl get <kind> <name> -o jsonpath='{.metadata.deletionTimestamp}{"\n"}{.metadata.finalizers}'
```

Ručné odstránenie finalizera môže opustiť externý disk, load balancer alebo inú resource. Správny postup je zistiť, ktorý controller finalizer vlastní a prečo cleanup nepostupuje.

## Admission môže zmeniť výsledný objekt

Manifest, ktorý vidíme v Git repozitári, nemusí byť identický s admitted objektom. Mutating admission môže doplniť sidecar, labels, environment alebo security defaults. Defaulting môže doplniť fields. Validating admission môže request odmietnuť.

Preto po apply čítame serverový výsledok:

```bash
kubectl get deployment payments-api -n production -o yaml
```

A pred mutáciou možno použiť server-side dry-run:

```bash
kubectl apply --server-side --dry-run=server \
  --field-manager=atlas-release \
  -f deployment.yaml -o yaml
```

Dry-run overí API, admission a výslednú podobu bez persistovania. Nevykoná controller reconciliation ani runtime test.

## Incident: pipeline opravila nesprávny Deployment

Operátor videl failing `payments-api` a spustil:

```bash
kubectl set image deployment/payments-api api=registry.example.com/atlas/payments-api:4.2.1
```

Kubeconfig context smeroval na production cluster, ale default namespace bol `staging`. Príkaz úspešne zmenil staging Deployment. Production incident pokračoval a staging zároveň dostal neplánovaný release.

Oprava začala identifikáciou presného cluster endpointu, namespace, Deployment UID a aktuálnej generation. Potom sa staging vrátil na svoj immutable digest a production dostala versionovanú opravu cez GitOps flow.

Skorší control je jednoduchý: používať explicitný context a namespace, zobrazovať server endpoint a identitu pred mutation, pinovať digest a overovať UID/generation v release evidence.

## Model, ktorý si treba odniesť

Kubernetes objekt nie je iba YAML dokument. Je to serverom prijatá a versionovaná API identita s UID, generation, resourceVersion, field ownershipom, desired `spec`, observed `status`, conditions, owner graphom a prípadným deletion lifecycle-om. Každý výstup treba viazať na konkrétny cluster, namespace, name, UID a generation.

## Referencie

- [Kubernetes Objects](https://kubernetes.io/docs/concepts/overview/working-with-objects/)
- [Kubernetes API Concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/)
- [Server-Side Apply](https://kubernetes.io/docs/reference/using-api/server-side-apply/)
- [Owners and Dependents](https://kubernetes.io/docs/concepts/overview/working-with-objects/owners-dependents/)
- [Finalizers](https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/)
