# CKA troubleshooting drills

CKA troubleshooting drill nie je hádanie príkazu podľa status reasonu. Je to opakovateľný evidence-to-recovery protocol: kandidát identifikuje exact incident subject, zúži failure domain, vytvorí realistické competing hypotheses, vyberie diskriminačné pozorovanie, vykoná minimálnu autoritatívnu opravu a preukáže pôvodný aj zakázaný outcome.

Scenáre v tejto kapitole sú originálne tréningové drilly, nie otázky zo skutočnej skúšky. Ich cieľom je trénovať causal diagnosis pod časom. Kandidát, ktorý náhodným restartom odstráni symptóm bez identifikácie mechanizmu, netrénuje spoľahlivý troubleshooting.

## 1. Dominantný drill lifecycle

Kvalitný drill má versionovaný expected state a presne jednu primary injected cause. Po symptóme sa fixne scope a subject, zachová volatile evidence a zmapuje control a data path. Hypotézy sa následne zmenšujú pozorovaniami, nie sériou náhodných zmien.

```text
versionovaný expected state a fault injection
→ symptóm, scope, timeline a recent change
→ exact object/process/Node/data/flow subject
→ volatile evidence preservation
→ owner/controller a control/data path
→ competing hypotheses
→ discriminating observation
→ containment
→ minimálna authoritative repair
→ controller/runtime reconvergence
→ original outcome verification
→ forbidden a adjacent-cohort verification
→ earlier control a scored closure
```

Repair je správna iba vtedy, keď opravuje authoritative cause a zachováva constraints. Odstránenie NetworkPolicy, affinity, probes alebo RBAC restriction môže obnoviť funkčnosť, ale vytvoriť forbidden outcome a znehodnotiť úlohu.

## 2. Drill subject a expected-state contract

Každý drill uvádza ID/generation, cluster/context a Kubernetes generation, namespace alebo host, primary object UID/generation alebo component identity, owner chain, súvisiace Service/EndpointSlice/PVC/Node identities, expected config a outcome, injected fault, misleading evidence, forbidden changes, hard validation, časový budget a reset procedure.

Fault injection bez initial-state checksumu je nekvalitný. Predchádzajúci pokus môže zanechať drift a vytvoriť druhú príčinu, ktorú scoring nepozná. Injector preto musí byť deterministic pri apply aj reset-e a validation script musí potvrdiť expected starting state.

Subject identity chráni aj evidence. Logs replacement Podu nie sú dôkazom o pôvodnom containeri; Node `Ready` po reboot-e nemusí hovoriť nič o faulted boot generation. UID, container ID, Node generation a timestamps sa zaznamenajú pred destructive repair.

## 3. Scope-first failure-domain narrowing

Scope je prvé diskriminačné pozorovanie. Ak zlyháva jeden container, začína sa command/args, loaded config, image, security context, probes, cgroup/OOM a process exit. Jeden Pod pridáva scheduler, kubelet, runtime, sandbox, CNI, CSI, init/sidecars a Node-local dependencies.

Workload alebo revision scope pridáva controller generation, selector/ownership, ReplicaSet cohorts, rollout budget, admission/quota a shared config. Node-specific scope smeruje ku kubeletu, runtime, CNI/CSI node plugins, pressure, cert/time/API connectivity a host image generation. Cluster-wide alebo request-class problem otvára API/etcd, webhooks/APIServices, DNS/Service dataplane, shared identity, policy a external dependencies.

Rovnaký `Pending`, `CrashLoopBackOff`, `NotReady`, `503` alebo timeout môže vzniknúť na každej z týchto hraníc. Status reason je symptóm a queue/state description, nie root cause.

## 4. Evidence preservation a hypothesis discipline

Pred restartom, delete alebo force zásahom sa podľa subjectu zachová live YAML, describe, sorted Events, current a previous logs a owner/resource generations. Na Node-e sa podľa potreby čítajú kubelet logs, CRI state, interfaces/routes/listeners, disk/inodes a component manifests.

Evidence sa zbiera účelovo. Dump celého clusteru spotrebuje čas a zhorší orientáciu. Každý command má potvrdiť alebo vyvrátiť konkrétnu hypothesis. Pre Service 503 napríklad rozlišujeme route/controller config, zero endpoints, port mismatch, per-edge stale config, policy/return path a application-generated response.

Diskriminačný chain môže ísť od response source a route conditions cez Service/EndpointSlice k direct PodIP, ServiceIP a external pathu. Ak direct PodIP funguje a ClusterIP nie, application a listener sa stávajú menej pravdepodobné; focus sa presunie na Service dataplane alebo policy.

## 5. Containment a repair hierarchy

Containment chráni fungujúci state, obmedzuje blast radius a zachováva evidence. Môže zastaviť rollout, cordonovať faulted Node cohort, ponechať old serving generation, dočasne smerovať traffic na known-good cohort alebo fence-nuť stateful writera.

Broad bypass nie je containment. Vypnutie NetworkPolicy, udelenie cluster-admin alebo force detach môže vytvoriť väčší incident. Pri storage/etcd sa nevytvára druhý writer pred overením fencing a backend state-u.

Preferovaná repair hierarchy opravuje authoritative source a nechá controller reconcile-nuť. Nasleduje bounded replacement objektu, Podu alebo Node generation, compatible roll-forward/rollback, external compensation a restore iba pri skutočnej potrebe. Exam task môže vyžadovať live edit, ale aj ten musí meniť správny subject a preserving constraints.

## 6. Connected drill: Service flow zlyháva iba z jednej Node cohorty

Drill `CKA-NET-17` generation `D17` beží v contexte `cluster-a`, namespace `payments`. Checkout Deployment generation 8 volá ledger Service UID `S31`, ClusterIP `10.96.42.17`, port 5432. EndpointSlices obsahujú štyri ready backend Pod UIDs. Accepted Nodes používajú generation `NG41`; faulted cohort používa `NG42`. Service identity, selector a default-deny NetworkPolicy sa nesmú meniť.

Symptómom sú timeouty približne polovice checkout requests, hoci Service aj backend Pody vyzerajú green. Rozdelenie requests podľa client Pod Node-u ukáže, že všetky failures pochádzajú z NG42. To výrazne oslabuje globálnu DNS, Service-selector a backend-process hypotézu.

Competing causes sú stale Service dataplane, CNI route/tunnel, policy agent generation, conntrack, backend return path k NG42 PodCIDR a application client behavior. Z affected Podu sa porovná direct ledger PodIP:5432, ClusterIP:5432 a DNS path. Direct PodIP funguje, ClusterIP timeoutuje iba z NG42 a policy verdict je allow.

Per-Node dataplane evidence ukáže missing current Service translation na NG42. Node-agent DaemonSet Pod je Ready, ale po host image update-e načítal chybný prerequisite. `Ready` na Pode aj Node-e teda nepotvrdilo Service capability.

Containment cordonuje NG42, zachová agent logs/dataplane dump a presunie stateless checkout replicas na NG41 bez zásahu do stateful backendov. Authoritative repair opraví host-image/bootstrap prerequisite, vytvorí immutable Node generation NG43 a spustí canary pre PodIP, ServiceIP, DNS a NetworkPolicy allow/deny flows.

Closure potvrdí checkout→ledger flow zo všetkých accepted Nodes. Forbidden checks zachovajú default-deny, Service UID/selector/ClusterIP, nepridajú broad bypass a vylúčia NG42 z workload placementu. Earlier control je Node-generation capability acceptance, nie iba `Node Ready` a DaemonSet readiness.

## 7. Process, configuration a probe drills

CrashLoopBackOff family rotuje wrong ConfigMap/Secret key, malformed loaded value, stale environment snapshot, command/args regression, liveness urýchľujúcu bootstrap failure a OOM. Hard validation kontroluje správnu process-loaded generation, stabilný restart count a Ready/serving cohort.

Probe family rozlišuje startup, readiness a liveness semantics. Variants zahŕňajú missing startup probe, readiness závislú od external dependency, liveness cez Service namiesto local health, port/path mismatch a termination/drain race. Zakázaná oprava je odstrániť probes bez náhradného health contractu.

Tieto drilly učia odlišovať object configuration od process-effective state-u. Current ConfigMap alebo mounted file neznamená, že process reloadol hodnotu.

## 8. Scheduling, controllers a autoscaling drills

Pending Pod môže mať requests nad allocatable, empty intersection hard constraints, wrong trusted label, untolerated taint, hostPort conflict, PVC topology alebo quota/admission failure ešte pred Pod creation. Oprava nesmie odstrániť placement/security requirement iba preto, aby scheduler našiel Node.

Stuck rollout variants zahŕňajú readiness/startup, surge capacity, quota, image pull, PDB/termination overlap, selector immutability, competing field writer a application compatibility. Validation kontroluje desired/updated/ready/available replicas, new ReplicaSet cohort a bounded old scale-down.

HPA drill sleduje metric provenance, requests, unknown/stale metrics, maxReplicas, Pending capacity a stabilization. `desiredReplicas` bez serving capacity nie je success. Kandidát musí prepojiť metric→scale write→scheduled/ready/serving Pody.

## 9. Service, DNS a edge drills

Zero-endpoint drill sleduje Service selector, matching Pod UIDs, readiness, EndpointSlice cohort, targetPort a listener. Service s endpoints, ale failed flowom, sa rozkladá na PodIP, ServiceIP, DNS, policy a Node dataplane.

DNS variants zahŕňajú Pod resolver/search/ndots, CoreDNS config/upstream loop, kube-dns Service path, NodeLocal generation, TCP/UDP 53 policy a negative application cache. Closure overuje cluster-local aj relevantný external FQDN a fresh connection po oprave.

Gateway/Ingress 503 chain začína external DNS/LB, pokračuje controller/class a accepted/resolved/programmed conditions, per-instance loaded config, backend reference, Service/EndpointSlice a Pod listener. API condition sama nestačí; external request sa testuje z relevantných edge cohorts.

## 10. Storage, Node a control-plane drills

PVC Pending variants pokrývajú StorageClass/provisioner, WaitForFirstConsumer, topology, quota a access/volume mode. Hard validation ide až po correct backend/PV identity a mounted consumer.

Multi-Attach alebo FailedMount vyžaduje writer/Node fencing pred force detach/delete. Kandidát rozlišuje stale VolumeAttachment, CSI node plugin, filesystem, secret, topology a security permission. Storage shortcut bez backend verification môže vytvoriť corruption.

Node NotReady drill porovnáva Node object/Lease s actual host, kubelet, runtime, certifikát/API path, pressure, clock a CNI initialization. Recovery sa uzatvára capability canary workloadom, nie iba `Ready=True`.

Control-plane family pokrýva static Pod manifests/flags/certs/hostPaths, API path timeouts cez etcd/webhook/APIService/inflight saturation, etcd snapshot identity a nedokončený kubeadm/Node upgrade. Etcd drill nemení data directory a overuje endpoint health, snapshot status a recovery-set metadata.

## 11. Identity, policy a object-lifecycle drills

RBAC 403 sa diagnostikuje cez authenticated subject/groups, Role/ClusterRole, binding scope, API group, resource/subresource a verb. Hard validation obsahuje intended allow aj forbidden operation.

NetworkPolicy DNS drill povoľuje exact DNS path podľa cluster modelu vrátane UDP a TCP 53 bez otvorenia ostatného egressu. Stuck Terminating drill identifikuje finalizer owner, webhook/APIService, unreachable Node/process, volume detach, preStop/grace alebo namespace finalization. Force delete bez writer/process verification je forbidden repair.

## 12. Fault-injection quality a scoring

Dobrý injector mení jednu authoritative cause, má deterministic apply/reset, nemení unrelated resources, vytvára realistický symptom, zachová evidence a podporuje rotáciu identities. Pokročilé drilly môžu pridať contributing control failure, ale scoring musí rozlíšiť primary root cause od amplifiera, napríklad broken host prerequisite plus readiness, ktorá ho neodhalí.

Scoring kladie najväčšiu váhu na root-cause accuracy, potom minimálnu správnu repair, original/forbidden validation, evidence safety a čas. Diagnosis, repair, reconvergence a verification time sa merajú oddelene. Pomalé observation a pomalé YAML editovanie potrebujú odlišné drills.

Review record obsahuje subject/outcome, symptom/scope/timeline, hypotheses, preserved evidence, discriminating observation, root cause, contributing failure, containment, repair, validations, times, chybný pokus, earlier control a follow-up drill. Tento learning log sa nevytvára počas reálnej skúšky; slúži príprave.

## 13. Anti-patterny a closure

Okamžitý restart/delete odstraňuje volatile evidence. Editovanie viacerých vrstiev znemožní causal attribution. Status reason nie je diagnóza. Broad bypass obnovuje funkčnosť za cenu forbidden security alebo availability outcome-u. Object existence nepreukazuje loaded, serving ani business-correct state.

Closure vyžaduje correct context/host, exact UID/process/flow identity, scope/timeline, preserved evidence, owner/control/data path, aspoň dve hypotézy, diskriminačný observation, bounded containment, authoritative repair, reconvergence, original outcome, forbidden/adjacent cohort a earlier control. Second run alebo reset musí potvrdiť, že drill aj oprava sú reprodukovateľné.

## Kontrolné otázky

1. Prečo status reason nie je root cause?
2. Ako scope zmenšuje hypothesis set?
3. Čo tvorí exact drill subject a initial-state contract?
4. Ktorú volatile evidence zachovať pred restartom alebo force delete?
5. Ako vybrať diskriminačné pozorovanie namiesto náhodnej zmeny?
6. Prečo Node alebo DaemonSet `Ready` nemusí byť capability verdict?
7. Ktoré boundaries testujú PodIP, ServiceIP, DNS a edge request?
8. Ako rozlíšiť primary cause od contributing control failure?
9. Čo je forbidden-outcome a adjacent-cohort validation?
10. Ako výsledok drill-u premeniť na targeted follow-up tréning?

## Praktické drilly

Spustiteľný scenárový index a review template patria do [CKA troubleshooting drills](../../troubleshooting/cka/README.md). Index materializuje mechanizmy z tejto kapitoly ako resetovateľné fault injections s initial-state validatorom, time budgetom a hard closure scriptom.

Po každom behu sa review record používa na výber ďalšieho variantu s rovnakým slabým reasoning krokom, ale inou identitou alebo root cause. Tým sa zabráni memorovaniu jedného injectoru a trénuje sa prenositeľná causal diagnosis.

## Glossary impact

Relevantné pojmy: CKA troubleshooting subject, expected-state contract, failure-domain narrowing, evidence preservation, competing hypotheses, discriminating observation, containment, authoritative repair, reconvergence, forbidden outcome, adjacent-cohort verification, fault-injection generation a drill score closure.

## Primárne zdroje

- [Linux Foundation — Certified Kubernetes Administrator](https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/)
- [Kubernetes — Troubleshooting](https://kubernetes.io/docs/tasks/debug/)
- [Kubernetes — Debug Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/)
- [Kubernetes — Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/)
- [Kubernetes — Troubleshoot Clusters](https://kubernetes.io/docs/tasks/debug/debug-cluster/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CKA timed labs](cka-timed-labs.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Praktický Helm chart — od prázdneho adresára po overený release →](helm-practical-chart-walkthrough.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
