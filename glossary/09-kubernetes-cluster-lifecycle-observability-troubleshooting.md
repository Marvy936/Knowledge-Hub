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
