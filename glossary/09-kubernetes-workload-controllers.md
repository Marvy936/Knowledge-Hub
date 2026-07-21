# Kubernetes workload controller glossary entries

## Active deadline — Job

Maximálny celkový čas, počas ktorého môže Kubernetes Job zostať aktívny; po jeho prekročení controller ukončí aktívne Pody a Job označí ako failed. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Available replicas — Kubernetes

Počet replík, ktoré sú Ready a spĺňajú príslušné availability timing podmienky controlleru; nie je totožný s počtom existujúcich alebo Running Podov. Pozri [Deployment](docs/09-kubernetes/deployment.md) a [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Completion index — Job

Stabilný index konkrétneho logical completion slotu pri Indexed Job-e, používaný na deterministické rozdelenie batch práce medzi Pody. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Concurrency policy — CronJob

Pravidlo `Allow`, `Forbid` alebo `Replace`, ktoré určuje, ako CronJob reaguje, keď má začať nový scheduled run a predchádzajúci Job ešte beží. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## ControllerRevision — Kubernetes

API object uchovávajúci revision metadata workload controllerov, napríklad StatefulSetu, pre rollout history a porovnanie current/update revision. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Current replicas — ReplicaSet

Počet Podov aktuálne pozorovaných ReplicaSet controllerom ako súčasť jeho replica population; nemusí byť zhodný s Ready alebo Available počtom. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## DaemonSet

Kubernetes workload controller zabezpečujúci Pod na každom eligible Node-e alebo na každom Node-e z vybranej množiny. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## DaemonSet `OnDelete`

Update stratégia, pri ktorej nový DaemonSet Pod template začne platiť pre konkrétny Node až po odstránení starého Podu. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## DaemonSet rolling update

Riadené postupné nahrádzanie DaemonSet Podov novou template revision pri zachovaní nastavenej unavailable alebo surge hranice. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Deployment

Kubernetes workload controller, ktorý deklaratívne riadi ReplicaSety a rollout zameniteľných Podov. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Deployment revision

Verzia Deployment Pod template-u reprezentovaná príslušným ReplicaSetom a použitá pre rollout history alebo rollback. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Desired replicas — Kubernetes

Počet replík požadovaný v workload spec-e alebo odvodený controllerom, ku ktorému sa controller snaží priblížiť observed replica population. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Eligible Node — DaemonSet

Node, ktorý spĺňa DaemonSet placement podmienky vrátane labels, affinity, taints/tolerations, platformy, admission a scheduling constraints. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Headless Service

Kubernetes Service bez virtuálnej ClusterIP, ktorý publikuje priamo endpoint identities a často poskytuje stabilnú DNS vrstvu pre StatefulSet Pody. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Idempotent batch execution

Batch návrh, pri ktorom opakované alebo duplicitné vykonanie toho istého logical work itemu nevytvorí nekonzistentné dodatočné side effects. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Indexed Job

Kubernetes Job s `completionMode: Indexed`, kde každý completion slot dostáva stabilný index pre statické alebo deterministické rozdelenie práce. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Job

Kubernetes workload controller, ktorý vytvára Pody a retryuje ich dovtedy, kým sa nedosiahne požadovaný completion alebo failure stav. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Job completion

Úspešne dokončený logical execution slot Jobu potvrdený Podom alebo controller statusom podľa zvoleného completion modelu. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Job history limit — CronJob

Počet úspešných alebo failed Job objektov, ktoré CronJob zachováva ako krátkodobú API históriu; nejde o dlhodobú log alebo audit retention. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Node bootstrap dependency

Cyklická alebo kritická závislosť, pri ktorej Node potrebuje systémový DaemonSet agent na plnú funkčnosť, zatiaľ čo agent sám potrebuje funkčný scheduling, runtime alebo časť node infraštruktúry. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Node-local agent

Workload poskytujúci funkciu konkrétnemu Node-u, napríklad logging, monitoring, networking, storage alebo device integration, typicky nasadený cez DaemonSet. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Number misscheduled — DaemonSet

Počet DaemonSet Podov bežiacich na Nodes, ktoré podľa aktuálneho DaemonSet placement modelu už nie sú eligible. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## `OrderedReady` — StatefulSet

Defaultný usporiadaný StatefulSet Pod management model, ktorý vytvára alebo aktualizuje ordinaly postupne a čaká na readiness pred pokračovaním. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Orphaned Pod — Kubernetes

Pod bez controller owner reference, ktorý môže zostať po orphan deletion alebo strate ownershipu a môže byť adoptovaný matching controllerom. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Overlapping selectors — Kubernetes

Nebezpečný stav, keď viac controllerov zodpovedá rovnakým Pod labelom a môže sa pokúšať adoptovať alebo riadiť tú istú population. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Parallel Pod management — StatefulSet

StatefulSet policy umožňujúca vytváranie alebo odstraňovanie Podov bez čakania na ordered readiness predchádzajúceho ordinalu. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Per-node overhead — DaemonSet

CPU, memory, storage, network a operational cost jedného DaemonSet Podu vynásobený počtom eligible Nodes v clustri. Pozri [DaemonSet](docs/09-kubernetes/daemonset.md).

## Per-replica PVC — StatefulSet

PersistentVolumeClaim viazaný na konkrétny StatefulSet ordinal a znovu použitý náhradným Podom s rovnakou logical identity. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Pod adoption — Kubernetes

Proces, pri ktorom controller prevezme matching Pod bez controller owner reference a nastaví ho ako svoj dependent object. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Pod selector — workload controller

Label selector určujúci population Podov, ktorú workload controller pozoruje a riadi; tvorí zásadnú ownership a reconciliation boundary. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Progress deadline — Deployment

Časová hranica, po ktorej Deployment status označí rollout ako nepostupujúci; sama osebe nevykoná automatický rollback. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## PVC retention policy — StatefulSet

Policy určujúca, či sa StatefulSet-created PVCs zachovajú alebo odstránia pri scale-down alebo deletion podľa podporovaného API a storage lifecycle modelu. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Ready replicas — Kubernetes

Počet replík, ktorých Pody majú aktuálne Ready condition; nevypovedá automaticky o dlhodobej availability alebo business correctness. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Recreate strategy — Deployment

Deployment stratégia, ktorá odstráni starú Pod population pred vytvorením novej, čím akceptuje downtime alebo minimalizuje mixed-version overlap. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Replacement Pod

Nový Pod object vytvorený controllerom ako náhrada zaniknutého alebo nevyhovujúceho Podu; má nový UID, IP a runtime lifecycle aj pri podobnom mene alebo template. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## ReplicaSet

Kubernetes workload controller udržiavajúci požadovaný počet matching zameniteľných Podov. Pozri [ReplicaSet](docs/09-kubernetes/replicaset.md).

## Rollout rollback — Deployment

Návrat Deployment Pod template-u na zachovanú staršiu revision; nevracia databázu, queues ani iný external state. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## Stable network identity — StatefulSet

Predvídateľné per-ordinal DNS meno StatefulSet Podu, ktoré pretrváva ako logical slot identity naprieč Pod replacementom. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Stable ordinal identity — StatefulSet

Logical identita StatefulSet repliky odvodená z názvu a ordinalu, napríklad `db-0`, zachovaná pri replacement-e, hoci Pod UID a process sa zmenia. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Starting deadline — CronJob

Maximálne oneskorenie po plánovanom čase, počas ktorého môže CronJob controller ešte vytvoriť príslušný Job. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## StatefulSet

Kubernetes workload controller poskytujúci skupine Podov stabilné ordinal identities, ordered lifecycle a možnosť per-replica persistent storage. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## StatefulSet partition

RollingUpdate hranica, ktorá aktualizuje iba StatefulSet Pody s ordinalom väčším alebo rovným nastavenej partition hodnote. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Suspended Job

Job s pozastaveným execution lifecycle, ktorý nevytvára novú prácu a po resume pokračuje z persisted Job statusu, nie z memory state-u ukončeného procesu. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## TTL-after-finished

Controller mechanizmus odstraňujúci dokončený alebo failed Job a jeho dependent resources po uplynutí `ttlSecondsAfterFinished`. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).

## Updated replicas — Deployment

Počet Deployment replík bežiacich z aktuálnej Pod template revision. Pozri [Deployment](docs/09-kubernetes/deployment.md).

## `volumeClaimTemplates` — StatefulSet

StatefulSet šablóny, z ktorých controller vytvára samostatné PVCs pre jednotlivé ordinal replicas. Pozri [StatefulSet](docs/09-kubernetes/statefulset.md).

## Work queue Job

Job model, v ktorom viac worker Podov odoberá položky z external queue a completion correctness závisí od acknowledgment, retry a deduplication semantics tejto queue. Pozri [Job a CronJob](docs/09-kubernetes/job-cronjob.md).
