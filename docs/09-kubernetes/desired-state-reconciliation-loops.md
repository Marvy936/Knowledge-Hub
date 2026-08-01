# Desired state a reconciliation loops

Kubernetes funguje tak, že controllers opakovane porovnávajú požadovaný stav uložený v API s tým, čo momentálne pozorujú, a vykonávajú malé kroky smerom ku konvergencii. Nie je to jednorazový skript, ktorý po `apply` odbehne od začiatku do konca. Rovnaký reconcile sa spustí po používateľskej zmene, po resynchronizácii cache, po výpadku Node-u aj po ručnom drift-e.

Pre `payments-api` je desired state jednoduchý: Deployment chce šesť replík z template generation 12. Reálny systém je však rozdelený. Deployment controller vytvorí ReplicaSet, ReplicaSet controller vytvorí Pods, scheduler doplní Node assignment, kubelet vytvorí runtime a EndpointSlice controller publikuje ready endpoints. Každý controller vidí iba časť celého príbehu.

## Reconcile nie je workflow s globálnym commitom

Predstavme si, že pipeline zmení image digest:

```yaml
spec:
  template:
    spec:
      containers:
        - name: api
          image: registry.example.com/atlas/payments-api@sha256:payments420
```

API server uloží novú Deployment generation. Deployment controller ju neskôr uvidí cez informer cache a vytvorí nový ReplicaSet. Ak controller po create requeste stratí spojenie skôr, než dostane odpoveď, nevie automaticky predpokladať, že operácia zlyhala. Pri ďalšom reconcile musí znovu pozorovať API stav a zistiť, či ReplicaSet už existuje.

Toto je dôležitý rozdiel oproti lineárnemu shell skriptu:

```text
observe
→ compute desired delta
→ perform bounded change
→ observe again
```

Controller nesmie postaviť correctness na tom, že si pamätá predchádzajúci úspešný krok iba v process memory.

## Informer cache, watch a pracovný rad

Typický controller najprv vykoná list existujúcich objektov a potom sleduje zmeny cez watch. Shared informer udržiava lokálnu cache a event handler zaradí kľúč objektu do work queue.

```text
API list/watch
→ informer cache
→ object key v queue
→ worker načíta aktuálny stav
→ reconcile
→ success alebo rate-limited retry
```

Queue často obsahuje iba kľúč, napríklad `production/payments-api`, nie celý starý event payload. Worker si pred rozhodnutím načíta najnovší stav z cache. Tým sa viac rýchlych zmien môže zlúčiť do jedného reconcile nad aktuálnou generáciou.

Cache však môže byť krátko za API serverom. Controller preto používa optimistic concurrency a nesmie považovať cache snapshot za nemennú globálnu pravdu.

## Desired state patrí objektu, nie procesu controllera

Ak controller-manager reštartuje, desired state zostáva v API. Nová inštancia znovu listne objekty, naplní cache a pokračuje. To je jeden z dôvodov, prečo Kubernetes dokáže obnoviť control loops bez ručného spustenia pôvodného deploy skriptu.

Rovnaký princíp platí pre vlastné operators. Dlhodobý workflow nesmie existovať iba ako neuložená sekvencia v pamäti. Potrebný progress, external identity a condition sa ukladajú do API objektu alebo iného autoritatívneho state-u.

## Reconcile musí byť idempotentný

Idempotencia neznamená, že každý API call sa musí vykonať iba raz. Znamená, že opakované vyhodnotenie rovnakého desired state-u vedie ku konvergencii, nie k násobeniu side effects.

ReplicaSet controller napríklad nehovorí „pri každom evente vytvor šesť Podov“. Najprv spočíta aktívne Pods patriace ReplicaSetu a vytvorí iba chýbajúci rozdiel.

```text
desired replicas = 6
observed active Pods = 4
→ create 2 Pods
```

Pri externých systémoch je situácia ťažšia. Controller, ktorý vytvára cloud load balancer, potrebuje stabilný idempotency key alebo uloženú external resource identity. Blind retry po timeout-e môže vytvoriť druhý load balancer.

## Eventual consistency a prechodné stavy

Po apply sa object graph mení postupne. Na krátky čas môže existovať nový Deployment generation, ale starý ReplicaSet. Neskôr vznikne nový ReplicaSet, ale Pods sú ešte `Pending`. Potom sú Pods `Running`, no readiness ešte neprešla.

```text
Deployment generation 12 prijatá
→ observedGeneration stále 11
→ nový ReplicaSet vytvorený
→ Pods Pending
→ Pods Running/NotReady
→ Pods Ready
→ old ReplicaSet scale-down
```

Takéto prechodné kombinácie nie sú samy osebe bug. Dôležité je, či systém robí progress v rámci očakávaných časových a kapacitných hraníc.

## Generation a observedGeneration

Mnohé controllers zapisujú do statusu generáciu, ktorú naposledy spracovali.

```bash
kubectl get deployment payments-api -n production \
  -o jsonpath='generation={.metadata.generation} observed={.status.observedGeneration}{"\n"}'
```

Ak sa hodnoty nezhodujú, status môže patriť k staršiemu desired state-u. Zelená condition bez korelácie na generation môže viesť k false-green záveru.

Nie každý resource používa `observedGeneration` rovnako, preto sa treba riadiť contractom konkrétneho kindu. Všeobecný princíp však zostáva: stav musí byť priradený k verzii intentu, ktorú opisuje.

## Owner graph rozdeľuje veľký problém

Deployment nevytvára každý Pod sám. Vytvorí ReplicaSet a tým deleguje replica management. OwnerReferences udržujú väzbu medzi vrstvami.

```text
Deployment UID D42
→ ReplicaSet UID RS42
→ Pod UIDs P1...P6
```

Pri diagnostike kontrolujeme každý okraj graphu:

```bash
kubectl get rs -n production -l app=payments-api -o wide
kubectl get pods -n production -l app=payments-api \
  -o custom-columns='NAME:.metadata.name,OWNER:.metadata.ownerReferences[0].uid,NODE:.spec.nodeName,READY:.status.containerStatuses[0].ready'
```

Ak Pod existuje bez očakávaného owner UID, môže ísť o ručne vytvorený alebo osirelý objekt. Taký Pod môže zdieľať labels a dostať sa do Service, hoci nie je súčasťou rollout authority.

## Finalizers a external cleanup

Delete request nemusí znamenať okamžité odstránenie objektu. Controller môže cez finalizer zablokovať fyzické zmazanie, kým nedokončí cleanup externého resource.

```text
delete request
→ deletionTimestamp
→ controller vykoná cleanup
→ odstráni finalizer
→ objekt zmizne
```

Ak controller nebeží alebo external API zlyháva, objekt zostane `Terminating`. Rýchle ručné odstránenie finalizera síce odblokuje API objekt, ale môže ponechať disk, IP alebo load balancer bez vlastníka.

Reconcile cleanup-u musí byť rovnako idempotentný ako create. Timeout pri delete operácii vyžaduje opätovné zistenie stavu externého resource, nie automatické opakovanie nevratnej operácie.

## Resync nie je náhrada za správny watch model

Controllers môžu používať periodický resync, aby objekty opäť zaradili na spracovanie aj bez novej API udalosti. Resync pomáha pri drift-e alebo strate lokálnej udalosti, ale nie je ospravedlnením pre nepravdivý status alebo závislosť na presnom poradí eventov.

Reconcile musí byť správny aj vtedy, keď dostane:

- viac rovnakých eventov,
- iba poslednú z viacerých rýchlych zmien,
- delete tombstone namiesto plného objektu,
- stale cache snapshot,
- event po reštarte controllera.

Tieto prípady sú prirodzenou súčasťou distribuovaného systému.

## Dvaja controllers nad rovnakým fieldom

Kubernetes môže oscilovať aj vtedy, keď sú oba controllers samostatne idempotentné. Predstavme si, že GitOps nástroj stále nastavuje:

```yaml
spec:
  replicas: 6
```

HPA medzitým vypočíta desať replík. GitOps reconcile vráti šesť, HPA znovu desať a systém neustále mení desired state.

Riešením nie je spomaliť jeden controller. Treba určiť jedného authoritative writera pre `.spec.replicas`. GitOps môže vlastniť min/max HPA konfiguráciu a Pod template, zatiaľ čo HPA vlastní aktuálny replica count.

Field ownership možno overiť:

```bash
kubectl get deployment payments-api -n production -o json \
  | jq '.metadata.managedFields[] | {manager,fieldsType,subresource}'
```

## Status musí hovoriť pravdu aj pri partial failure

Controller nesmie publikovať success marker skôr, než je operácia skutočne dokončená. Pri vlastnom operatorovi je nebezpečný model:

```text
zapíš Ready=True
→ potom vytvor external resource
```

Ak druhý krok zlyhá, status klame. Bezpečnejší model používa explicitné phases alebo conditions a status aktualizuje až po read-backu výsledku.

```text
Progressing=True
→ external operation
→ read-back exact resource identity
→ Ready=True, Progressing=False
```

Status nie je log. Má byť stabilný, generáciou viazaný contract pre ďalších consumers.

## Incident: ručný Pod bol stále vracaný späť

Počas incidentu operátor zmazal failing Pod a ručne vytvoril nový s opraveným environmentom. Pod fungoval, ale o niekoľko minút zmizol a ReplicaSet vytvoril ďalší Pod z pôvodnej template.

Kubernetes neignoroval opravu. ReplicaSet správne realizoval svoj desired state. Ručný Pod nepatril do authoritative graphu a zmena environmentu nebola v Deployment template.

Správna remediation bola upraviť versionovaný Deployment manifest, použiť server-side dry-run, aplikovať novú generation a overiť nový ReplicaSet. Rýchly ručný Pod mohol poslúžiť ako controlled reproduction mimo Service, nie ako trvalá oprava.

## Incident: blind retry vytvoril dva external resources

Custom controller vytváral DNS record cez externé API. Request uspel, ale odpoveď sa stratila. Controller timeout interpretoval ako failure a vytvorenie zopakoval s novým provider-generated názvom. Vznikli dva records a status ukazoval iba druhý.

Oprava vyžadovala stabilný external key odvodený z Kubernetes UID, provider-side idempotency a read-before-create po unknown outcome. Status začal uchovávať exact external identity a generation.

## Ako čítať reconcile pri troubleshootingu

Pri zlyhaní sa pýtaj v tomto poradí:

1. Aký desired state je aktuálne persistovaný?
2. Ktorý controller vlastní ďalší transition?
3. Spracoval aktuálnu generation?
4. Aký dependent object alebo external effect mal vzniknúť?
5. Existuje, ale má zlý stav, alebo vôbec nevznikol?
6. Je retry bezpečný a idempotentný?
7. Ktorý writer vlastní problematický field?

Takto sa vyhneš plošnému restartovaniu controllerov bez pochopenia, či je problém v stale cache, admission, ownership konflikte alebo samotnom external API.

## Model, ktorý si treba odniesť

Kubernetes desired state je uložený v API. Controllers ho opakovane pozorujú a realizujú cez malé idempotentné transitions. Progress je eventual, status musí patriť ku konkrétnej generation a viac writerov potrebuje explicitné ownership hranice. Reconcile sa považuje za úspešný až po read-backu výsledku, nie po odoslaní mutation requestu.

## Referencie

- [Kubernetes Controllers](https://kubernetes.io/docs/concepts/architecture/controller/)
- [API Concepts: Efficient detection of changes](https://kubernetes.io/docs/reference/using-api/api-concepts/)
- [Server-Side Apply](https://kubernetes.io/docs/reference/using-api/server-side-apply/)
- [Finalizers](https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/)
