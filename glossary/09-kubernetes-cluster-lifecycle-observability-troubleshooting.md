# Kubernetes lifecycle, recovery, observability and troubleshooting glossary entries

## API-state RPO

Maximálna prijateľná strata Kubernetes API object zmien medzi posledným použiteľným etcd snapshotom a incidentom. Musí byť koordinovaná s RPO application dát. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## Add-on compatibility — Kubernetes

Overený vzťah medzi Kubernetes verziou a verziami CNI, CSI, CoreDNS, ingress/Gateway, admission, metrics a ďalších cluster-critical components. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Bootstrap token — kubeadm

Časovo obmedzený credential používaný pri kubeadm node discovery a TLS bootstrap workflowe; musí overovať CA identity a nesmie byť dlhodobo uložený. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Canary node pool

Malá skupina Nodes s novou Kubernetes, OS, runtime alebo add-on verziou použitá na overenie compatibility pred širším rolloutom. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Certificate lifecycle — Kubernetes

Riadenie vydania, distribúcie, expirácie, obnovy, reloadu a zrušenia control-plane, etcd, kubelet a administrator certificates. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Cluster add-on

Component dopĺňajúci Kubernetes cluster o DNS, networking, storage, metrics, routing, policy alebo inú platformovú schopnosť mimo základného API/control-plane procesu. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Cluster bootstrap

Proces vytvorenia prvého funkčného control plane, PKI, etcd, kubeconfigs, bootstrap identity a základných resources pred pripojením Nodes a add-ons. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Cluster decommission

Riadené ukončenie clusteru zahŕňajúce data retention, traffic/DNS, PV a cloud resources, credentials, audit evidence a bezpečné odstránenie hosts. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Cluster-level logging

Architektúra, ktorá prenáša container, Node a control-plane logs do backendu s lifecycle a retenciou nezávislou od jednotlivých Podov a Nodes. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Cluster-wide symptom

Failure pozorovaný naprieč namespaces, Nodes alebo services, ktorý zvyšuje pravdepodobnosť problému v control plane, shared add-on, network, storage alebo external dependency. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Component metrics — Kubernetes

Prometheus-style metrics publikované API serverom, schedulerom, controller-managerom, kubeletom, etcd a ďalšími system components. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Control-plane endpoint

Stabilná DNS/IP a load-balancer identity, cez ktorú clients a Nodes pristupujú ku Kubernetes API server replicas. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Control-plane health gate

Súbor podmienok ako API readiness, etcd quorum, Node/add-on health, certificate stav a backup readiness, ktoré musia prejsť pred upgrade alebo zásahom. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Controlled reproduction — Kubernetes

Najmenší bezpečný experiment reprodukujúci failure s rovnakou identity, policy, network, storage alebo Node boundary bez zbytočných production side effects. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## CRI log

Node-local container stdout/stderr záznam v Container Runtime Interface logging formáte s timestampom, streamom a full/partial markerom. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Cross-system recovery consistency

Súlad času a verzie obnoveného etcd API state-u, persistent application dát, schema, credentials a external resources. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## Debug container — Kubernetes

Ephemeral container pridaný do existujúceho Podu na diagnostiku pomocou schváleného debug image-u, RBAC a auditu. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Deprecated API caller

Klient, controller, chart, operator alebo automation používajúca Kubernetes API verziu, ktorá bude alebo už bola odstránená, aj keď deklaratívne manifests už môžu byť migrované. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Disaster recovery — Kubernetes

Koordinovaný proces obnovy control-plane state-u, PKI, encryption keys, external infrastructure a application dát po strate authoritative cluster state-u. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## etcd compaction marker — restore

Restore voľba označujúca staršiu revision históriu ako compacted, aby watchers vykonali relist namiesto používania stale cache assumptions. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## etcd member health

Stav konkrétneho etcd člena z pohľadu endpoint dostupnosti, Raft membership, leader/quorum participation, revision a disk/network health. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## etcd quorum

Väčšina etcd členov potrebná na bezpečné consensus writes, vypočítaná ako `floor(N/2)+1`. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## etcd revision bump

Posunutie revision pri snapshot restore tak, aby nová logical história prekonala revisions pozorované clients pred incidentom. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## etcd snapshot

Point-in-time backup etcd key-value state-u vytvorený cez snapshot API a overený integrity/status toolingom. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## Event series — Kubernetes

Agregovaný Kubernetes Event reprezentujúci opakovaný rovnaký reason/message v čase namiesto neobmedzeného vytvárania samostatných objektov. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Evidence preservation — Kubernetes

Zachovanie object statusu, Events, logs, metrics, timestamps a configuration pred restartom, delete, rollbackom alebo restore operáciou. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Failure-domain narrowing

Postupné vylučovanie API, controller, scheduler, Node, runtime, CNI, CSI, Service/DNS, application a external dependency vrstiev pomocou overiteľných hypotéz. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Immutable node replacement

Upgrade alebo oprava Node-u vytvorením novej versionovanej instance, validáciou, controlled drainom starého Node-u a následným odstránením starej infraštruktúry. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Kubernetes audit log

Bezpečnostný záznam API requests podľa audit policy, odlišný od diagnostických Events a application business events. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Kubernetes Event

Krátkodobý API objekt s diagnostickým pozorovaním componentu o konkrétnom resource alebo cluster stave. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Kubernetes incident timeline

Chronologický záznam faktov, hypotéz, testov, zmien a recovery milestones s UTC časom počas incidentu. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Kubernetes version skew

Maximálny podporovaný rozdiel verzií medzi API servers, kubelets, controller-managerom, schedulerom, kube-proxy, kubectl a deployment toolingom. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Kubeadm

Bootstrap a lifecycle nástroj poskytujúci `init`, `join`, `upgrade`, certificate a configuration workflows pre Kubernetes na už pripravenej infraštruktúre. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Managed control plane

Kubernetes control plane, ktorého availability, etcd a upgrade lifecycle čiastočne alebo úplne prevádzkuje provider podľa definovanej support boundary. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Metrics stability — Kubernetes

Alpha, beta alebo stable lifecycle contract system metrics ovplyvňujúci ich deprecation a removal pri Kubernetes upgrades. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Metrics-server

Cluster add-on implementujúci Resource Metrics API pre aktuálne CPU/memory údaje používané napríklad `kubectl top` a resource-metric HPA; nie je dlhodobý monitoring backend. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Mixed-version control plane

Dočasný podporovaný stav HA control plane počas sekvenčného upgrade-u, keď API server replicas nemajú rovnakú verziu. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Node log agent

DaemonSet alebo host agent čítajúci Node/container logs, dopĺňajúci Kubernetes metadata a odosielajúci dáta do central backendu. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Object-first troubleshooting

Diagnostický prístup začínajúci exact Kubernetes objectom, jeho spec/status, conditions, ownerReferences, Events a controller state-om. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Ownership matrix — Kubernetes platform

Explicitné rozdelenie zodpovednosti medzi provider, platform team a application team pre control plane, Nodes, add-ons, identity, backup, upgrade a incident response. Pozri [Cluster installation a lifecycle](docs/09-kubernetes/cluster-installation-lifecycle.md).

## Recovery set — Kubernetes

Súbor artifacts potrebný na obnovu, zahŕňajúci etcd snapshot, PKI, encryption configuration/keys, component config, infrastructure source a application data backups. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## Remediation hierarchy — Kubernetes

Preferované poradie opráv od úzkeho declarative rollbacku alebo obnovy dependency cez Pod/Node replacement a roll-forward až po disaster recovery. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Resource metrics pipeline

Cesta kubelet resource údajov cez metrics-server a `metrics.k8s.io` API ku klientom a HPA. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Restore rehearsal

Pravidelný test obnovy reálneho backup artifactu v izolovanom prostredí vrátane merania RTO a application consistency validation. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## Restored etcd cluster identity

Nové member a cluster metadata vytvorené snapshot restore operáciou; starý a obnovený member state sa nesmie nekontrolovane miešať. Pozri [etcd backup a restore](docs/09-kubernetes/etcd-backup-restore.md).

## Service troubleshooting chain

Diagnostické poradie Service selector → EndpointSlice readiness → targetPort → dataplane → Pod listen socket → application behavior. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Storage troubleshooting chain

Diagnostické poradie PVC → StorageClass/provisioner → PV binding → scheduling topology → VolumeAttachment → CSI node mount → application I/O. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Telemetry retention

Čas a storage policy pre logs, metrics, Events, traces a audit records odvodená od incident, compliance, forensic a cost požiadaviek. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Time-series cardinality

Počet unikátnych kombinácií metric label values; nekontrolované dynamické labels výrazne zvyšujú memory, storage a query náklady. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Unsupported cluster version

Kubernetes minor verzia mimo upstream alebo provider support window, pre ktorú nemusia byť dostupné security fixes, compatibility garancie ani support. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Upgrade abort criterion — Kubernetes

Vopred definovaná SLO, error-rate, control-plane alebo dataplane podmienka, pri ktorej sa upgrade zastaví a aktivuje recovery plán. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Upgrade health gate — Kubernetes

Pre-upgrade kontrola API, etcd, Nodes, add-ons, certificates, capacity a backup stavu zabraňujúca upgradu už degraded clusteru. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Adjacent-cohort verification — Kubernetes

Overenie, že recovery funguje nielen na pôvodnom affected subjecte, ale aj na susedných Node, zone, release, tenant alebo endpoint cohortách. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Absent-evidence verdict

Explicitné rozhodnutie, či chýbajúci signal znamená neprítomnosť udalosti alebo failure emission, collection, transport, ingestion, query či retention boundary. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Audit/Event/business-event separation

Rozlíšenie API audit requestu, krátkodobého Kubernetes diagnostického Eventu a durable application business udalosti. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Authoritative remediation subject — Kubernetes

Exact object, artifact, Node, data, policy alebo external state generation, ktorú remediation opravuje namiesto maskovania symptómu na inej vrstve. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Backend acknowledgement — telemetry

Dôkaz, že observability backend prijal konkrétny batch alebo record pred tým, než collector bezpečne posunie durable offset. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Canary capability verdict — Kubernetes upgrade

Verdikt, že target control-plane, add-on alebo Node cohort poskytuje požadované API, network, storage, security, telemetry a business capabilities pred širším rolloutom. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Cardinality budget

Versionovaný limit a ownership model pre počet time series a label domains, ktorý chráni observability backend pred unbounded ingestom a query degradáciou. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Cohort differential diagnosis

Porovnanie jedného úspešného a jedného zlyhávajúceho subjectu podľa release, Node, zone, config, endpoint alebo telemetry generation s cieľom izolovať meniacu sa príčinu. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Collection subject — telemetry

Exact Node, Pod/container stream, local file alebo runtime source, collector Pod/config, offset a destination používané pri zbere signálu. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Collector offset generation

Durable checkpoint určujúci, po ktorú source file/inode alebo stream pozíciu bol record bezpečne spracovaný a potvrdený backendom. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Compatibility graph — Kubernetes upgrade

Resolved vzťah medzi target Kubernetes verziou a etcd, Nodes, runtimes, add-ons, CRDs, webhooks, clients, workloads a persistent data contracts. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Containment generation — Kubernetes incident

Versionovaný stav trafficu, rolloutov, Nodes, retries a external reconcilers vytvorený na zastavenie ďalšieho dopadu bez zničenia evidence. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Control/data-path map — Kubernetes

Mapa API a reconciliation control pathu oddelená od client request, packet, storage a business data pathu pre jeden incident subject. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Correlation envelope — Kubernetes telemetry

Spoločná sada cluster, operation, release, Pod UID, container ID, Node generation, request/trace ID a UTC time identities umožňujúca spájať signals rovnakého subjectu. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Deprecated-API closure

Dôkaz, že všetci reálni callers používajú podporované endpointy, CRD storage/conversion je compatible a starú API generation možno bezpečne odstrániť. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Discriminating observation boundary

Observation point, ktorého výsledok rozdelí konkurenčné hypotézy s minimálnym rizikom a zmenou systému. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Emission boundary — telemetry

Hranica, na ktorej source process alebo component vytvoril log, metric, Event, audit record alebo trace pred ďalším zberom a transportom. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Forbidden-outcome verification — Kubernetes

Dôkaz, že po remediation zostávajú zakázané flows, permissions, credentials, duplicate side effects alebo stale generations skutočne nefunkčné. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Ingestion/query boundary — telemetry

Rozlíšenie backendom prijatého recordu od recordu správne indexovaného, retained a nájdeného v presnom tenantovi, time range a query. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Irreversible migration boundary — Kubernetes upgrade

Bod API storage, CRD conversion, schema, data alebo external-state transitionu, po ktorom stará generácia už nemusí byť bezpečná rollback target. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Kubernetes incident subject

Exact cluster, release, object UID/generation, Pod/container, Node, data, flow, request a time identity, ku ktorej sa viažu hypotheses a recovery verdict. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Kubernetes upgrade subject

Complete current-to-target transition identity zahŕňajúca cluster, component, etcd, Node, runtime, add-on, API/CRD, workload, data a recovery generations. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Node-generation acceptance

Verdikt, že nový Node image/runtime/kubelet a jeho CNI, CSI, DNS, Service, policy, telemetry a workload capabilities fungujú pred prijatím produkčnej záťaže. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Observability acceptance

End-to-end dôkaz, že expected source je emitovaný, zozbieraný, potvrdený, queryable, retained, redacted a použiteľný pri alert alebo incident rozhodnutí. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Old-generation retirement — Kubernetes upgrade

Overené odstránenie starej control-plane, Node, add-on, credential a telemetry generation po prijatí target platformy. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Original-outcome verification — Kubernetes

Opätovné overenie pôvodného používateľského alebo business cieľa po remediation, nie iba technického stavu komponentu. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Second-reconciliation verdict — Kubernetes

Dôkaz, že ďalší controller reconcile, retry, replacement alebo failover zostane bounded a nevytvorí znovu drift, duplicate alebo chybný side effect. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Signal contract

Versionovaný význam telemetry signálu vrátane source, units/schema, labels, freshness, missing-data semantics, retention a očakávanej causal interpretácie. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Subject-bound evidence closure

Verdikt, že dôkazy pre exact incident, release, Pod, Node a request subject pokrývajú source-to-query chain a podporujú prijaté rozhodnutie. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Subject-bound incident closure

Záverečný verdict spájajúci root cause, authoritative remediation, original/forbidden outcomes, adjacent cohorts, telemetry coverage a preventive control s exact incident subjectom. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Subject-bound upgrade closure

Verdikt, že target platform generation je prijatá, mixed-version stav skončil, business a telemetry fungujú a stará generácia bola bezpečne retired. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Symptom-to-subject translation

Prevod user alebo business symptómu na konkrétne cluster, release, object, process, data, flow a time identities vhodné na falsifikovateľnú diagnostiku. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Target platform generation — Kubernetes

Schválená kombinácia Kubernetes, etcd, Node image/runtime, add-ons, APIs, controllers a workload compatibility, do ktorej upgrade konverguje. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Telemetry backpressure boundary

Miesto, kde collector buffer, transport alebo backend capacity spomaľuje či dropuje signals a môže ovplyvniť Node disk, offset alebo evidence completeness. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Telemetry blind-spot subject

Exact Node, component, source alebo time cohort, pre ktorú evidence chýba pre pipeline failure, nie nevyhnutne pre absenciu incidentu. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Telemetry coverage generation

Versionovaný inventár expected sources, collectors, configs a backend paths, ktoré musia byť end-to-end pozorovateľné pre konkrétnu cluster alebo Node generation. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Telemetry lifecycle subject

Súvislý identity chain od source emission cez collection, buffer, transport, backend acknowledgement, indexing, query a retention po operational verdict. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Telemetry retention verdict

Dôkaz, že logs, metrics, Events, audit a traces zostanú dostupné dostatočne dlho pre detection, incident, forensic a compliance potreby bez neprimeraného cost alebo exposure. Pozri [Logging, metrics a events](docs/09-kubernetes/logging-metrics-events.md).

## Unknown-operation outcome — Kubernetes

Stav, keď request timeoutol alebo response zanikla, ale Kubernetes controller alebo external provider mohol side effect dokončiť; pred retry je potrebný authoritative read-back. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Upgrade cohort

Množina control-plane, Node, add-on alebo workload subjects s rovnakou current alebo target generation používaná na oddelené meranie transitionu. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Upgrade recovery gate

Pre-upgrade verdict zahŕňajúci health, spare capacity, backup, complete recovery set, restore rehearsal a rollback/roll-forward boundaries. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).

## Volatile evidence envelope

Súbor object statusov, Events, logs, container/Node state-u, packets, offsets, external auditov a timestamps, ktoré môžu remediation alebo retention rýchlo odstrániť. Pozri [Kubernetes troubleshooting](docs/09-kubernetes/kubernetes-troubleshooting.md).

## Workload-plane abort criterion

Vopred definovaná Pod sandbox, network, storage, DNS, policy, telemetry alebo business podmienka, ktorá zastaví upgrade aj pri green control plane. Pozri [Upgrades](docs/09-kubernetes/upgrades.md).