# Kubernetes architecture

Kubernetes je distribuovaný riadiaci systém pre aplikácie, nie vzdialená verzia príkazu `docker run`. Používateľ alebo pipeline pošle cez API želaný stav, control plane ho uloží ako versionovaný objekt a niekoľko nezávislých control loops postupne vytvorí nižšie objekty, vyberie Node, pripraví runtime a zapojí výsledný Pod do prevádzky. Medzi prijatím YAML-u a úspešným používateľským requestom preto neexistuje jedna synchronná transakcia.

V celej sekcii budeme sledovať službu `payments-api` v clusteri `atlas-prod-eu1`. Release `4.2.0` má bežať v namespace `production` ako šesť replík. Aplikácia používa image digest `sha256:payments420`, konfiguráciu `C52`, secret epoch `SE08` a Service `payments-api`. Úspešný rollout neznamená iba existenciu šiestich Podov. Znamená, že správny image a konfigurácia bežia na vhodných Nodes, readiness odráža skutočnú schopnosť spracovať platbu, Service posiela traffic iba na prijaté repliky a payment authorization vznikne práve raz.

## Od YAML-u k bežiacemu procesu

Začnime príkazom:

```bash
kubectl apply -f deployment.yaml
```

`kubectl` najprv použije aktuálny kubeconfig context, cluster endpoint a identitu používateľa. YAML skonvertuje na API request a odošle ho `kube-apiserver`-u. API server vykoná authentication, authorization, defaulting, admission a schema validation. Až keď je objekt prijatý a zapísaný do etcd, vráti úspešnú odpoveď.

Tento úspech dokazuje iba to, že nová generácia objektu bola prijatá a persistovaná. Deployment ešte nemusí mať nový ReplicaSet, Pod nemusí existovať a žiadny proces nemusí bežať.

```text
kubectl apply
→ API server prijme request
→ etcd uloží Deployment generation
→ Deployment controller vytvorí ReplicaSet
→ ReplicaSet controller vytvorí Pods
→ scheduler pridelí Pods Nodes
→ kubelet pripraví sandbox, network, volumes a containers
→ readiness sprístupní Pods cez EndpointSlice
→ Service pošle request na application process
```

Každý šíp má iného vlastníka. Práve toto rozdelenie ownershipu je základom Kubernetes architektúry aj troubleshooting-u.

## API server ako spoločná hranica

Control-plane komponenty, kubelety, add-ons aj ľudskí používatelia pracujú s cluster state-om cez API server. API server nie je iba HTTP proxy pred databázou. Uplatňuje identity, RBAC, admission policies, API conversion, validation, optimistic concurrency a audit.

Praktický prvý read-back vyzerá takto:

```bash
kubectl config current-context
kubectl auth whoami
kubectl get deployment payments-api -n production -o yaml
```

Prvý príkaz odpovedá, do ktorého contextu posielame operácie. Druhý ukáže identitu, ktorú API server vyhodnotí. Tretí číta persistovaný Deployment objekt. Ani jeden príkaz ešte nepreukazuje stav Pod procesu alebo dostupnosť služby.

API server udržiava aj `resourceVersion`, cez ktorý klienti a controllers sledujú zmeny. Namiesto neustáleho plného pollingu používajú list/watch mechanizmus. Keď sa Deployment zmení, príslušný controller sa o novej generácii dozvie a zaradí objekt na spracovanie.

## etcd ako autoritatívny cluster state

Kubernetes API objekty sú uložené v etcd. Ak etcd nemá quorum, bezpečné writes sa zastavia, aj keď už bežiace aplikácie môžu určitý čas pokračovať. To vysvetľuje zdanlivo paradoxný stav: používateľské requesty fungujú, ale nový Deployment nemožno vytvoriť alebo zmeniť.

```bash
kubectl get --raw='/readyz?verbose'
```

Readiness API servera je užitočnejšia než obyčajný test otvoreného TCP portu. Otvorený port dokazuje iba dostupný listener. Readiness môže odhaliť problém s etcd, post-start hooks alebo internou inicializáciou.

Etcd však nepozná význam payment business flowu. Uloží objekt `Deployment`, ale nerozhoduje, či nové Pods používajú správnu databázu alebo či payment authorization nevznikne dvakrát.

## Controllers menia intent na dependent objects

Deployment controller sleduje Deployment objekty. Keď uvidí novú Pod template generation, vytvorí alebo upraví ReplicaSet. ReplicaSet controller potom vytvorí potrebný počet Pod objektov.

```bash
kubectl get deployment payments-api -n production
kubectl get replicasets -n production -l app=payments-api
kubectl get pods -n production -l app=payments-api
```

Tieto tri pohľady ukazujú tri rôzne vrstvy. Deployment popisuje rollout intent, ReplicaSet konkrétnu template revision a Pods jednotlivé runtime instances. Ak Deployment hlási novú generáciu, ale nový ReplicaSet nevznikol, problém je ešte v controller alebo admission vrstve. Ak ReplicaSet existuje, ale nevytvoril Pods, scheduler zatiaľ nie je relevantný.

Controllers nebežia ako jedna centrálna funkcia, ktorá drží globálnu transakciu. Každý opakovane pozoruje stav a vykonáva malý idempotentný krok. Preto je Kubernetes eventual-consistency systém: jednotlivé objekty sa môžu krátko nachádzať v prechodných kombináciách.

## Scheduler vyberá Node, ale nespúšťa container

Nový Pod bez `.spec.nodeName` vstúpi do scheduler queue. Scheduler najprv odfiltruje Nodes, ktoré nespĺňajú hard constraints, napríklad requests, taints, node affinity, topology alebo volume requirements. Z vhodných Nodes potom vyberie kandidáta a zapíše binding do API.

```bash
kubectl get pod -n production -l app=payments-api \
  -o custom-columns='NAME:.metadata.name,NODE:.spec.nodeName,PHASE:.status.phase'
```

Prázdny `NODE` pri existujúcom Pode ukazuje scheduling boundary. Ak je Node pridelený, scheduler už svoju hlavnú úlohu vykonal. Image pull, CNI, volume mount a process start sú zodpovednosťou worker-node vrstvy.

## Kubelet realizuje pridelený Pod

Kubelet na každom Node sleduje Pods, ktoré boli pridelené jeho Node-u. Z admitted Pod specu vytvorí lokálny runtime contract. Cez CRI požiada container runtime o sandbox a containers, cez CNI vznikne Pod network a cez CSI alebo interné volume plugins sa pripravia volumes.

```text
assigned Pod
→ kubelet local admission
→ volume a projected-data príprava
→ CRI sandbox
→ CNI network a Pod IP
→ image pull/unpack
→ init containers
→ application containers
→ probes, status a termination
```

Kubelet potom priebežne zapisuje Pod status späť cez API server. `Running` však iba znamená, že aspoň jeden hlavný container beží alebo sa spúšťa podľa Pod phase semantics. Neznamená, že application je ready alebo že Service path funguje.

```bash
kubectl get pods -n production -l app=payments-api -o wide
kubectl describe pod -n production <pod-name>
kubectl get pod -n production <pod-name> -o jsonpath='{.status.conditions}'
```

## Service traffic je ďalší samostatný systém

Keď readiness prejde, Pod sa môže objaviť ako ready endpoint v EndpointSlice. Service potom poskytuje stabilnú virtual identity nad meniacimi sa Pod IP adresami. Implementácia dataplane-u môže používať iptables, IPVS, eBPF alebo inú technológiu podľa platformy.

```bash
kubectl get service payments-api -n production -o yaml
kubectl get endpointslices -n production \
  -l kubernetes.io/service-name=payments-api -o yaml
```

Service objekt dokazuje desired service contract. EndpointSlice ukazuje, ktoré Pod endpoints sú momentálne publikované a aké majú conditions. Ani zelený EndpointSlice však nedokazuje, že aplikácia správne vykoná platbu. Potrebný je reálny request cez rovnakú cestu, akú používa klient.

## Control plane a data plane

Pri incidente je užitočné oddeliť dve cesty. Control path vytvára a mení objekty:

```text
client
→ API server
→ etcd
→ controller
→ scheduler
→ kubelet
→ status
```

Data path nesie používateľský request:

```text
client
→ DNS a edge
→ Gateway alebo Ingress
→ Service dataplane
→ EndpointSlice backend
→ Pod socket
→ application dependency
→ response
```

Control plane môže byť zelený a data path chybný. Naopak, data path môže určitý čas fungovať, hoci control plane nevie prijímať nové writes. Tieto stavy sa nesmú zlúčiť do jednej otázky „je cluster zdravý?“.

## Čo znamená desired, observed a effective state

Deployment spec hovorí, čo chceme. Deployment status hovorí, čo controller naposledy pozoroval a vypočítal. Pod status zachytáva stav reportovaný kubeletom. Effective runtime zahŕňa skutočný process, loaded configuration, mounty, network a cgroups. Business outcome je výsledok requestu a prípadného commit-u.

```text
Deployment spec replicas=6
≠ šesť vytvorených Pod objektov
≠ šesť spustených procesov
≠ šesť Ready endpointov
≠ šesť business-correct replík
```

Preto pri každom `kubectl` výstupe treba pomenovať dôkazovú hranicu. `kubectl apply` potvrdzuje prijatú deklaráciu. `rollout status` hodnotí controller conditions. `get pods` číta Pod state. Syntetický payment test až nakoniec overí používateľsky významnú cestu.

## Incident: Deployment prijatý, ale nič sa nespustilo

Pipeline nasadila generation 12 a `kubectl apply` skončil úspešne. Po desiatich minútach však neexistoval nový Pod. Tím najprv kontroloval kubelet logy na Nodes, ale problém bol vyššie.

```bash
kubectl get deployment payments-api -n production -o yaml
kubectl get replicasets -n production -l app=payments-api
kubectl get events -n production --sort-by=.lastTimestamp
```

Deployment existoval, nový ReplicaSet však nie. Event ukázal, že controller create request odmietol validating admission webhook kvôli chýbajúcemu povinnému labelu. Scheduler ani kubelet nedostali žiadny objekt, ktorý by mohli spracovať.

Oprava spočívala v doplnení labelu do versionovaného manifestu a novom apply. Recovery sa uzavrela až po vzniku nového ReplicaSetu, pridelení Podov, readiness, EndpointSlice aktualizácii a úspešnom payment requeste. Tento incident ukazuje základný diagnostický princíp: začni pri prvej vrstve, kde sa expected transition neuskutočnil, nie pri najnižšej vrstve, ktorú poznáš.

## Architektonický model, ktorý si treba odniesť

Kubernetes je reťaz samostatných autorít. API server prijíma a chráni zmeny. Etcd uchováva cluster state. Controllers vytvárajú dependent objects. Scheduler vyberá Node. Kubelet s runtime-om, CNI a CSI realizuje pridelený Pod. Service a edge komponenty vedú traffic. Aplikácia a jej dependencies určujú business výsledok.

Pri návrhu aj incidente preto vždy sleduj konkrétny objekt, jeho UID a generation, component, ktorý vlastní ďalší prechod, a dôkaz, že prechod skutočne nastal.

## Referencie

- [Kubernetes Components](https://kubernetes.io/docs/concepts/overview/components/)
- [Kubernetes API concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/)
- [Kubernetes controllers](https://kubernetes.io/docs/concepts/architecture/controller/)
- [Scheduling, Preemption and Eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Docker troubleshooting](../08-container-fundamentals-and-docker/docker-troubleshooting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: API a object model →](api-object-model.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
