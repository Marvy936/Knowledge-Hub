# Kubernetes

Táto sekcia vysvetľuje Kubernetes ako jeden súvislý systém od API requestu až po používateľský výsledok. Začína tým, čo sa stane po `kubectl apply`: API server request autentizuje, autorizuje, prijme cez admission a uloží do etcd. Controllers z uloženého intentu vytvoria dependent objects, scheduler vyberie Node a kubelet s CRI, CNI a CSI pripraví skutočný Pod runtime. Service, DNS a Gateway potom vedú request ku konkrétnemu application procesu a jeho dependencies.

Cieľom nie je memorovať desiatky YAML fields alebo `kubectl` príkazov. Čitateľ má vedieť určiť, ktorý component vlastní ďalší transition, čo konkrétny status alebo condition dokazuje a kde jeho dôkazová hranica končí. `kubectl apply` nepreukazuje vytvorený Pod, `Pod Running` nepreukazuje readiness, `EndpointSlice ready=true` nepreukazuje funkčný external route a `Deployment availableReplicas=6` nepreukazuje správny payment outcome.

Celou sekciou prechádza jeden cluster a jedna hlavná služba. Cluster `atlas-prod-eu1` prevádzkuje `payments-api` v namespace `production`. Release `4.2.0` používa immutable image digest, configuration generation `C52`, secret epoch `SE08`, šesť replík a Service `payments-api`. Rovnaké identity sa používajú pri API modeloch, rollout-e, probes, NetworkPolicy, HPA, upgrade-e aj troubleshooting-u. Stateful kapitola pridáva `settlement-ledger` a batch kapitola `settlement-export`, aby sa vysvetlili stabilné identity, storage a completion semantics bez miešania s webovým Deploymentom.

Sekcia nadväzuje na [Linux and Systems](../01-linux-and-systems/README.md), [Networking and Web Fundamentals](../02-networking-and-web/README.md), [CI/CD and Release Engineering](../05-ci-cd-and-release/README.md), [Infrastructure as Code and Configuration Management](../07-infrastructure-as-code-and-configuration-management/README.md) a najmä [Container Fundamentals and Docker](../08-container-fundamentals-and-docker/README.md). Docker sekcia pripravila image, process, network, volume a runtime model. Kubernetes k nemu pridáva versionované API, control loops, scheduling, multi-node dataplane, policy a cluster lifecycle.

## Authoritative poradie kapitol

1. [Kubernetes architecture](kubernetes-architecture.md)
2. [API a object model](api-object-model.md)
3. [Desired state a reconciliation loops](desired-state-reconciliation-loops.md)
4. [Control plane components](control-plane-components.md)
5. [Worker node components](worker-node-components.md)
6. [Pod](pod.md)
7. [ReplicaSet](replicaset.md)
8. [Deployment](deployment.md)
9. [StatefulSet](statefulset.md)
10. [DaemonSet](daemonset.md)
11. [Job a CronJob](job-cronjob.md)
12. [ConfigMap a Secret](configmap-secret.md)
13. [ServiceAccount](serviceaccount.md)
14. [Service a EndpointSlice](service-endpointslice.md)
15. [Ingress a Gateway API](ingress-gateway-api.md)
16. [Cluster DNS](cluster-dns.md)
17. [CNI a NetworkPolicy](cni-networkpolicy.md)
18. [Volumes, PV, PVC a StorageClass](volumes-pv-pvc-storageclass.md)
19. [Scheduling](scheduling.md)
20. [Requests, limits a QoS](requests-limits-qos.md)
21. [Probes](probes.md)
22. [Taints, tolerations, affinity a topology](taints-tolerations-affinity-topology.md)
23. [HPA a autoscaling](hpa-autoscaling.md)
24. [RBAC](rbac.md)
25. [SecurityContext a Pod Security](securitycontext-pod-security.md)
26. [ResourceQuota a LimitRange](resourcequota-limitrange.md)
27. [Cluster installation a lifecycle](cluster-installation-lifecycle.md)
28. [etcd backup a restore](etcd-backup-restore.md)
29. [Upgrades](upgrades.md)
30. [Logging, metrics a events](logging-metrics-events.md)
31. [Praktický Kubernetes projekt od manifestov po overený rollout](kubernetes-practical-walkthrough.md)
32. [Kubernetes troubleshooting](kubernetes-troubleshooting.md)

Poradie je zámerné. Prvých päť kapitol vysvetlí control path od API po Node runtime. Nasledujúce kapitoly rozdelia workload controllers podľa ich identity a replacement modelu. Config, workload identity, Service, edge, DNS a CNI potom vytvoria celý request path. Storage, scheduling, resources, probes, topology a autoscaling ukážu, prečo sa Pod môže vytvoriť, ale nebyť schedulovateľný, pripravený alebo výkonný. Bezpečnostný a cluster-lifecycle blok spojí RBAC, process confinement, namespace governance, bootstrap, disaster recovery a upgrades. Observability, praktický walkthrough a troubleshooting nakoniec používajú všetky predchádzajúce vrstvy naraz.

Po tejto sekcii nasleduje [Helm and CKA](../10-helm-and-cka/README.md). Helm preberá Kubernetes manifesty ako renderovaný release subject a CKA kapitoly používajú rovnaké object, controller, Node, network a troubleshooting boundaries v časovo obmedzených úlohách.

## Výkladový štandard sekcie

Všetkých tridsaťdva kapitol je písaných v rovnakom plynulom štýle ako sekcie CI/CD, Docker a Keycloak. Kapitola najprv stanoví konkrétny problém alebo request, potom vysvetlí mechanizmus na spoločnom Atlas scenári a vloží YAML, CLI alebo JSON priamo k miestu, kde je potrebný. Bezprostredne po príklade vysvetlí, čo command alebo objekt mení, aký output očakávame a čo zelený výsledok ešte nedokazuje.

Odrážky zostávajú iba pri krátkom inventári, identity manifest-e alebo acceptance kontrole. Nenahrádzajú hlavný výklad. Incidenty nie sú izolované „tipy“; vždy sledujú presný cluster, object generation, Pod UID, Node generation, data identity alebo request flow a vedú od competing hypotheses cez diskriminačné observation points po containment, autoritatívnu opravu a overenie pôvodného aj zakázaného outcome-u.

Sekcia dôsledne rozlišuje päť vrstiev:

```text
source intent
→ API admitted a persisted object
→ controller-resolved object graph
→ effective Node/runtime/dataplane state
→ application a business outcome
```

Source Deployment môže mať správny image digest, ale mutating admission môže doplniť sidecar. Admitted Pod môže byť správny, ale scheduler ho nevie umiestniť. Scheduled Pod môže zlyhať na CNI alebo volume mount-e. Ready Pod môže byť mimo Service selectoru. Service request môže fungovať, ale payment commit môže mať unknown outcome. Každá vrstva potrebuje vlastný read-back.

## Praktický walkthrough

Kapitola [Praktický Kubernetes projekt od manifestov po overený rollout](kubernetes-practical-walkthrough.md) vytvorí celý malý projekt:

```text
Namespace a Pod Security labels
→ ServiceAccount bez implicitného API tokenu
→ ConfigMap a external Secret contract
→ hardenovaný Deployment
→ Service a EndpointSlice
→ PodDisruptionBudget
→ default-deny a explicitné NetworkPolicies
→ voliteľný HPA ownership hand-off
→ Kustomize render
→ server-side dry-run a diff
→ apply a rollout
→ runtime image/config read-back
→ Service request
→ no-op druhý apply
→ configuration-driven replacement
→ Pod replacement
→ broken Service selector
→ Running-but-NotReady revision
→ forbidden privileged Pod
→ evidence a cleanup
```

Projekt používa immutable image placeholders, ktoré treba nahradiť schválenými digestmi. Secret value sa do repozitára neukladá; vytvára ho samostatný secret-management flow. Deployment používa non-root UID, RuntimeDefault seccomp, capability drop, read-only root filesystem, explicitné writable volumes, requests/limits, startup/readiness/liveness probes, topology spread a preferred anti-affinity.

Verification script nekontroluje iba `kubectl rollout status`. Číta Deployment generation a observedGeneration, ReplicaSets, Pod UIDs, Node assignment, source image a runtime imageID, configuration annotation, ready EndpointSlice a request cez Service z verifier Podu s presnou NetworkPolicy identitou. Forbidden dry-run zároveň overí, že Restricted Pod Security odmieta privileged workload.

Dve failure overlays ukážu rozdiel medzi application a routing state-om. Broken Service selector ponechá Pods Ready, ale odstráni endpoints. Broken readiness vytvorí novú revision, ktorej process beží a liveness prechádza, no Pod nie je Ready a rollout nerobí progress. Recovery vždy znovu aplikuje authoritative base a overí controller, endpoint aj request outcome.

Practical walkthrough je dokumentačne a syntakticky auditovaný. Repository workflow ho nespúšťa proti skutočnému Kubernetes clusteru, registry, CNI, metrics pipeline ani cloud providerovi. Reálne `Verified` vyžaduje cieľový cluster, skutočné image digests, dostupný Secret, podporovanú NetworkPolicy implementáciu a vykonanie positive aj forbidden paths.

## Čo má čitateľ po sekcii vedieť

Po úvodnom bloku má vedieť sledovať request od kubeconfig contextu cez API server, etcd, controllers, scheduler a kubelet. Má rozlišovať GVK a GVR, name a UID, generation a resourceVersion, `spec` a `status`, field ownership, ownerReferences, finalizers a admission. Pri reconcile má vedieť určiť authoritative writera a vysvetliť, prečo idempotentný controller musí po unknown outcome znovu pozorovať state.

Pri workloads má vedieť vysvetliť Pod ako jednu runtime repliku, ReplicaSet ako count controller, Deployment ako výmenu template revízií, StatefulSet ako ordinal/storage identity, DaemonSet ako Node capability coverage a Job/CronJob ako completion a retry systém bez exactly-once business garancie. Má vedieť rozlíšiť container restart od Pod replacementu a rolling overlap od jednoduchého scale-u.

Pri configuration a traffic má vedieť odlíšiť ConfigMap/Secret source od hodnoty materializovanej kubeletom a načítanej procesom. Má rozumieť ServiceAccount tokenu, RBAC a external workload identity ako samostatným rovinám. Request má vedieť sledovať cez DNS, Gateway/Ingress, Service, EndpointSlice, per-Node dataplane, NetworkPolicy, Pod interface a application socket a overiť allowed aj forbidden flows.

Pri storage a placement má vedieť prepojiť PVC UID, PV, CSI volumeHandle, topology a data generation. Má rozumieť requests ako scheduler a HPA inputu, limits ako runtime boundary a QoS ako pressure modelu. Má vedieť vysvetliť taints, affinity a topology ako skladajúce sa constraints a odhaliť neschedulovateľný rollout, ktorý nemožno opraviť pridaním nesprávnej Node kapacity.

Pri security má vedieť navrhnúť minimum RBAC, workload ServiceAccount bez nepotrebného tokenu, Restricted-compatible SecurityContext a úzke writable paths. Má chápať, že `pods/exec`, workload creation, impersonation, bind/escalate a cloud federation môžu vytvoriť nepriamu privilege path. ResourceQuota a LimitRange má interpretovať ako admission boundaries, ktoré môžu zastaviť rollout skôr, než vznikne Pod.

Pri cluster lifecycle má vedieť odlíšiť API/Node readiness od úplnej platform capability. Má vedieť navrhnúť immutable Node replacement, bootstrap taint a capability canary. Etcd snapshot má chápať ako Kubernetes API backup, nie application-data backup. Upgrade má vedieť rozdeliť na control plane, CRDs/webhooks, add-ons, Nodes a workloads s osobitnými compatibility a rollback hranicami.

Pri observability a incidente má vedieť vybrať log, metric, Event, audit alebo trace podľa otázky, kontrolovať telemetry coverage a nezamieňať absenciu dát so zdravím. Troubleshooting má začať exact subjectom, preserve-first evidence a prvým chýbajúcim transitionom. Oprava má meniť autoritatívnu vrstvu a uzavrieť sa business aj forbidden-outcome overením.

## Revalidation completion gate

Sekcia je `Ready for user review`, keď všetkých tridsaťjeden pôvodných kapitol a nový praktický walkthrough tvoria jeden plynulý learning path; každá kapitola obsahuje konkrétny mechanizmus, praktické observation points a najmenej jeden kauzálny failure model tam, kde je to relevantné; README ordering a navigation obsahujú 32 kapitol; praktický projekt má kompletné manifests, overlays a verification script; API, controller, runtime, dataplane a business evidence sa nezlievajú; a full glossary/navigation/learning-depth audit prejde bez dočasných closeout súborov v merge diff-e.

Tento gate neoznačuje príklady za reálne vykonané. Kubernetes, CNI, CSI, HPA, Gateway, etcd a upgrade outcomes sú závislé od konkrétnej cluster verzie a implementácie. Pri použití sa najprv overí API discovery, version-skew policy a platform-specific controller contract.

## Stav revalidácie

| Blok | Kapitoly | Stav |
|---|---:|---|
| API, reconciliation, control plane a worker Nodes | 5/5 | Complete |
| Pod a workload controllers | 6/6 | Complete |
| Configuration, identity, Service, edge, DNS a CNI | 6/6 | Complete |
| Storage, scheduling, resources, probes, topology a HPA | 6/6 | Complete |
| RBAC, workload security, quota a cluster lifecycle | 4/4 | Complete |
| etcd recovery, upgrades a observability | 3/3 | Complete |
| Practical walkthrough a troubleshooting | 2/2 | Complete |

Celkový authoritative stav je **32/32 · Ready for user review**. Znamená to dokončený full-section prose, practical, navigation a learning-depth pass. Neznamená automaticky používateľské `Accepted`, reálne cluster `Verified` ani produkčné `Stable`.
