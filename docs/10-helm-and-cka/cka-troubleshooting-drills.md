# CKA troubleshooting drills

CKA troubleshooting drill nie je hádanie príkazu podľa status reasonu. Je to opakovateľný evidence-to-recovery protocol: kandidát musí pomenovať exact incident subject, zúžiť failure domain, rozlíšiť competing hypotheses jedným diskriminačným pozorovaním, vykonať minimálnu autoritatívnu opravu a preukázať pôvodný aj zakázaný outcome.

> Scenáre v tejto kapitole sú originálne tréningové drilly, nie otázky zo skutočnej skúšky.

## 1. Dominantný drill lifecycle

```text
versionovaný expected state a fault injection
→ pozorovaný symptóm, scope a timeline
→ exact cluster/object/process/data/flow subject
→ volatile evidence preservation
→ control-path a data-path map
→ competing hypotheses
→ discriminating observation point
→ containment
→ minimálna authoritative repair
→ controller/runtime reconvergence
→ original outcome verification
→ forbidden a adjacent-cohort verification
→ recurrence control a scored closure
```

Drill musí trénovať diagnózu oddelene od editácie. Kandidát, ktorý náhodou odstráni symptóm bez správneho root cause-u, nemá plný výsledok.

## 2. Drill subject a expected-state contract

Každý drill má versionovaný subject:

```text
drill ID a generation
cluster/context a Kubernetes generation
namespace alebo Node/host
primary object UID/generation alebo host component
owner/controller chain
related Service/EndpointSlice/PVC/Node identities
expected configuration a outcome
injected fault a authoritative source
misleading evidence
forbidden changes
hard validation
časový budget
reset/cleanup procedure
```

Fault injection bez recorded expected state-u nevytvára kvalitný drill. Môže viesť k viacerým validným opravám alebo k prostrediu, ktoré sa po predchádzajúcom pokuse nedá spoľahlivo vyhodnotiť.

## 3. Scope-first failure-domain narrowing

### Jeden container

Začni process boundary:

- command/args,
- process-loaded ConfigMap/Secret,
- image/filesystem,
- security context,
- liveness/startup interaction,
- cgroup limit a OOM,
- application exit.

### Jeden Pod

Rozšír subject o:

- scheduler binding,
- kubelet PodWorker,
- sandbox/CRI,
- CNI/IPAM,
- CSI mount,
- init/sidecar,
- Node-local runtime alebo host dependency.

### Jeden workload alebo revision

Skontroluj:

- controller generation a observedGeneration,
- selector/ownership,
- old/new ReplicaSet cohort,
- rollout budget,
- admission/quota,
- HPA alebo field ownership,
- shared configuration alebo dependency.

### Jeden Node

Pravdepodobné boundaries:

- Node object/Lease verzus actual host,
- kubelet,
- runtime,
- CNI/CSI node plugin,
- routes/dataplane,
- disk/memory/PID pressure,
- certificate/time/API connectivity,
- host image generation.

### Celý cluster alebo request class

Preskúmaj:

- API write/read/watch path,
- etcd,
- admission webhook alebo APIService,
- DNS/Service dataplane,
- shared identity,
- cluster-wide policy alebo quota,
- shared external dependency.

Scope je prvý discriminating observation. Rovnaký `Pending`, `CrashLoopBackOff`, `503` alebo timeout môže mať desiatky príčin.

## 4. Evidence preservation pred repair

Pred restartom, delete alebo force zásahom zachovaj podľa subjectu:

```bash
kubectl get <object> -n <ns> -o yaml
kubectl describe <object> -n <ns>
kubectl get events -n <ns> --sort-by=.metadata.creationTimestamp
kubectl logs <pod> -n <ns> -c <container>
kubectl logs <pod> -n <ns> -c <container> --previous
```

Na Node-e:

```bash
journalctl -u kubelet --since '-15 min'
crictl ps -a
crictl inspect <container-id>
ip address
ip route
ss -lntup
df -h
df -i
```

Evidence musí byť viazaná na UID, container ID, Node boot/generation a čas. Logs zo replacement Podu nie sú evidence o pôvodnom procese.

## 5. Competing hypotheses a discriminating observations

Kvalitný drill vyžaduje aspoň dve realistické hypotézy. Príklad pre Service `503`:

1. Route/controller nevytvoril platnú backend konfiguráciu;
2. Service má zero ready endpoints;
3. `targetPort` nesedí s listenerom;
4. edge dataplane má stale config iba na časti instances;
5. NetworkPolicy alebo return path blokuje flow;
6. application vracia `503` sama.

Diskriminačný postup:

```text
response source/header a edge instance
→ Route/Gateway/Ingress conditions
→ Service port contract
→ celý EndpointSlice cohort a targetRef UIDs
→ direct PodIP:port
→ ServiceIP:port
→ DNS/edge path
→ packet/policy observation podľa scope-u
```

Jeden test má zmenšiť hypothesis set. Séria náhodných zmien diagnózu ničí.

## 6. Containment a repair hierarchy

Containment má chrániť funkčný stav a evidence:

- zastav ďalší rollout alebo writer,
- cordon chybný Node cohort bez okamžitého drainu, ak treba evidence,
- zachovaj old serving cohort,
- obmedz traffic na známu zdravú generáciu,
- nepoužívaj broad policy disable alebo `cluster-admin`,
- pri storage/etcd nevytváraj druhého writera.

Preferovaná repair hierarchy:

```text
oprava authoritative source
→ controller reconciliation
→ bounded object/Pod/Node replacement
→ compatible rollback alebo roll-forward
→ external compensation
→ restore iba pri preukázanej potrebe
```

Manual live edit môže byť exam-appropriate podľa zadania, ale musí opraviť správny subject a nesmie porušiť explicitný contract.

## 7. Worked drill: Service endpoints sú green, traffic zlyháva iba z jednej Node cohorty

### Expected state

```text
drill: CKA-NET-17 generation D17
context: cluster-a
namespace: payments
client Deployment: checkout generation 8
backend Service: ledger UID S31, ClusterIP 10.96.42.17, port 5432
EndpointSlice cohort: ES31-a/ES31-b, štyri ready Pod UIDs
healthy Node generation: NG41
faulted Node generation: NG42
expected: checkout → ledger Service TCP/5432 funguje zo všetkých client Podov
forbidden: zmeniť Service identity, selector alebo vypnúť NetworkPolicy cluster-wide
```

### Symptóm

Približne polovica checkout requests timeoutuje. Service má ready endpointy a backend Pods sú Ready.

### Scope

Rozdelenie podľa client Pod Node-u ukáže, že všetky failures pochádzajú z Nodes generácie NG42. To odfiltruje globálnu Service, DNS a backend-process hypotézu.

### Competing hypotheses

1. NG42 má stale Service dataplane;
2. CNI route/tunnel chýba iba na NG42;
3. NetworkPolicy agent nenačítal current policy generation;
4. conntrack obsahuje stale translation;
5. backend return path nevie smerovať k NG42 PodCIDR;
6. application client cache/retry vytvára zdanie Node-specific failure.

### Evidence a discriminating observations

```bash
kubectl get pod -n payments -l app=checkout -o wide
kubectl get service ledger -n payments -o yaml
kubectl get endpointslice -n payments -l kubernetes.io/service-name=ledger -o yaml
kubectl get node -L node.kubernetes.io/image-generation
```

Z affected client Podu porovnaj:

```text
ledger PodIP:5432
ledger ClusterIP:5432
ledger DNS:5432
```

Finding:

- direct PodIP funguje;
- ClusterIP timeoutuje iba z NG42;
- policy verdict je allow;
- per-Node Service translation state na NG42 chýba pre current Service generation;
- NG42 node-agent DaemonSet Pod je `Ready`, ale načítal chybný host prerequisite po image update.

### Containment

- cordon NG42 Nodes;
- nepresúvať stateful backendy ani nemať zbytočný blast radius;
- presmerovať client replicas na NG41 podľa lab contractu;
- zachovať node-agent logs a dataplane dump.

### Authoritative repair

Oprav host image/bootstrap prerequisite pre NG42, vytvor novú immutable Node generation NG43 a spusti capability canary:

```text
PodIP flow
ServiceIP flow
DNS flow
NetworkPolicy allow flow
NetworkPolicy deny flow
```

Až potom vráť application workloady.

### Closure

Original outcome: checkout requests cez ledger Service fungujú zo všetkých accepted Nodes.

Forbidden outcomes:

- default-deny policy zostáva účinná;
- Service UID/selector/ClusterIP sa nezmenili;
- nebol vytvorený broad bypass;
- old faulty Node generation už neprijíma workload.

Earlier control: Node-generation capability acceptance test, nie iba `Node Ready` a DaemonSet Pod readiness.

## 8. Drill design podľa mechanizmu

Nasledujúce drilly sú fault-injection families. Každý run vyberie jednu exact root cause variantu, pridá misleading evidence a explicitnú validation.

### A. Process, configuration a probes

#### CrashLoopBackOff po config zmene

Varianty:

- wrong ConfigMap/Secret key;
- malformed process-loaded value;
- stale env snapshot;
- command/args regression;
- liveness urýchľujúca bootstrap failure;
- cgroup OOM.

Hard validation: correct process-loaded value, stable restart count a Ready endpoint cohort.

#### Probe failure

Varianty:

- chýba startup probe;
- readiness závisí od nesprávnej external dependency;
- liveness používa Service path namiesto local health;
- port/path mismatch;
- termination/drain race.

Forbidden repair: odstrániť všetky probes bez náhradného acceptance contractu.

### B. Scheduling a controllers

#### Pod Pending bez Node assignmentu

Varianty:

- requests > allocatable;
- empty hard-constraint intersection;
- wrong trusted label;
- netolerovaný taint;
- hostPort conflict;
- PVC topology;
- admission/quota blokuje parent controller ešte pred Pod create.

Hard validation: Pod je Scheduled na feasible Node bez odstránenia požadovaného placement contractu.

#### Deployment rollout stuck

Varianty:

- readiness/startup;
- surge capacity;
- quota/admission;
- image pull;
- PDB/termination overlap;
- mutable/immutable selector;
- HPA alebo iný field writer;
- application compatibility.

Hard validation: desired updated/ready/available replicas, correct new ReplicaSet cohort a bounded old-cohort scale-down.

#### HPA neškáluje alebo škáluje škodlivo

Varianty:

- metrics API;
- missing resource requests;
- stale/unknown metric;
- maxReplicas;
- scale write succeeds, Pods ostávajú Pending;
- retry-amplified causal metric;
- stabilization policy.

Hard validation: metric provenance a desired-to-serving capacity chain, nie iba HPA desiredReplicas.

### C. Service, DNS a edge

#### Service nemá endpoints

Chain:

```text
Service selector
→ matching Pod UIDs
→ readiness
→ EndpointSlice cohort
→ targetPort
→ application listener
```

Varianty: selector mismatch, zero Ready Pods, wrong namespace, selectorless Service bez explicitných endpoints, terminating-only cohort.

#### Service má endpoints, ale flow zlyhá

Porovnaj PodIP, ServiceIP a DNS. Varianty: targetPort, listener na loopback, policy, per-Node dataplane, MTU/return path, stale connection.

#### DNS failure

Varianty: Pod resolver/search/ndots, Corefile, upstream loop, kube-dns Service path, NodeLocal generation, TCP/53 block, negative application cache.

Hard validation: cluster-local aj relevantný external FQDN a následný fresh connection.

#### Gateway/Ingress `503`

Chain:

```text
external DNS/LB
→ controller/class
→ accepted/resolved/programmed route
→ per-instance loaded config
→ backend reference
→ Service/EndpointSlice
→ Pod listener
```

Hard validation: external request z relevantných edge cohorts, nie iba API conditions.

### D. Storage

#### PVC Pending

Varianty: chýbajúca StorageClass, provisioner, `WaitForFirstConsumer`, topology, quota, access/volume mode.

Hard validation: PVC Bound, correct PV/backend identity a mounted consumer.

#### Multi-Attach alebo FailedMount

Varianty: starý Node/writer stále aktívny, stale VolumeAttachment, CSI node plugin, filesystem, Secret, topology alebo LSM permission.

Forbidden repair: force detach/delete pred fencing a backend verification.

### E. Node a runtime

#### Node NotReady

Evidence:

```bash
kubectl describe node <node>
kubectl get lease -n kube-node-lease <node> -o yaml
systemctl status kubelet
journalctl -u kubelet
crictl info
```

Varianty: kubelet, certifikát, API path, runtime, pressure, clock, CNI initialization.

Hard validation: Node capability canary a workload acceptance, nie iba `Ready=True`.

#### ImagePullBackOff

Varianty: immutable reference typo, auth Secret scope, registry CA, egress/rate limit. Architecture mismatch sa môže prejaviť až po pull-e ako runtime failure.

Forbidden repair: broad registry credential alebo mutable fallback tag.

#### Resource pressure

Rozlišuj container limit OOM, Node OOM, kubelet eviction, ephemeral storage/inodes a CPU throttling. `kubectl top` je iba momentka.

### F. Control plane, API a etcd

#### Static Pod component

Over `/etc/kubernetes/manifests`, YAML/flags, cert paths, hostPath, ports, runtime a etcd connectivity. Hard validation musí pokryť component function alebo API capability.

#### API dostupný, ale request path timeoutuje

Varianty: etcd latency/quorum, webhook, APIService, inflight saturation, DNS/network dependency alebo certifikát. Rozlišuj globálny outage od konkrétneho resource/admission pathu.

#### etcd snapshot operation

Varianty: endpoint, CA/cert/key, tool/version, endpoint health alebo disk. Nemeň data directory. Over snapshot status a recovery-set metadata.

#### Nedokončený kubeadm/Node upgrade

Over version-skew, package/binary, kubeadm fázu, kubelet config/service, drain/cordon a workload state. Closure zahŕňa supported version a capability acceptance.

### G. Identity, policy a object lifecycle

#### RBAC `403`

Skontroluj authenticated subject/groups, Role/ClusterRole, binding scope, API group, resource/subresource a verb. Over povolenú aj zakázanú operáciu.

#### NetworkPolicy blokuje DNS

Povoľ exact DNS path podľa cluster modelu vrátane UDP/TCP 53 bez otvorenia ostatného egressu.

#### Stuck `Terminating`

Varianty: finalizer owner, webhook/APIService, unreachable Node/process, volume detach, preStop/grace alebo namespace finalization.

Forbidden repair: force delete bez overenia process/writer state-u.

## 9. Fault-injection quality gate

Dobrý injector:

- mení jednu authoritative príčinu;
- má deterministický apply aj reset;
- nemení unrelated resources;
- vytvára realistický, ale nie falošný symptom;
- zachováva dosť evidence;
- má explicitnú hard validation;
- podporuje rotáciu identities a parametrov.

Príklady:

```text
selector key drift
wrong named targetPort
missing CPU request
trusted Node label typo
CoreDNS upstream loop
static Pod certificate path drift
NetworkPolicy bez DNS egressu
Node image bez required CNI host prerequisite
stale process-loaded Secret epoch
```

Dve chyby kombinuj až v pokročilých drilloch a musí byť jasné, ktorá je root cause a ktorá contributing control failure.

## 10. Scoring a time-boxing

Self-grading:

```text
40 % root-cause accuracy
25 % minimálna správna repair
20 % original/forbidden validation
10 % evidence preservation a bezpečnosť
5 % čas
```

Meraj zvlášť:

- diagnosis time,
- repair time,
- reconvergence time,
- verification time.

Odporúčané budgets:

```text
jednoduchý object/process drill: 5 min
stredný controller/network/storage drill: 8–10 min
Node/control-plane/etcd drill: 12–15 min
```

Pomalá diagnóza a pomalá editácia vyžadujú odlišný tréning.

## 11. Drill review template

```text
Drill ID/generation:
Expected subject a outcome:
Symptóm/scope/timeline:
Prvá hypotéza:
Competing hypotheses:
Preserved evidence:
Discriminating observation:
Root cause:
Contributing failure:
Containment:
Authoritative repair:
Original validation:
Forbidden/adjacent validation:
Diagnosis/repair/verify time:
Chybný pokus:
Earlier control:
Targeted follow-up drill:
```

Tento záznam patrí do learning logu, nie do reálneho exam scratchpadu.

## 12. Anti-patterny

### Okamžitý restart alebo delete

Odstráni volatile evidence a môže iba dočasne skryť root cause.

### Editovanie viacerých vrstiev naraz

Nie je možné určiť, ktorá zmena pomohla, a môžeš porušiť ďalší contract.

### Status reason ako diagnóza

`Pending`, `CrashLoopBackOff`, `ImagePullBackOff`, `NotReady` alebo `503` sú symptómy, nie mechanizmus.

### Broad bypass

`cluster-admin`, vypnutie NetworkPolicy, odstránenie affinity alebo force delete často obnovia funkčnosť za cenu neakceptovateľného forbidden outcome-u.

### Validácia iba cez object existence

Existujúci object nemusí byť effective, loaded, serving ani business-correct.

### Memorovanie jedného injectoru

Rotuj root causes a misleading evidence; inak trénuješ pattern recall namiesto causal diagnosis.

## 13. Master checklist

```text
[ ] správny context, namespace alebo host
[ ] exact subject UID/generation/process/flow/data identity
[ ] symptóm, scope, timeline a recent change
[ ] volatile evidence preserved
[ ] owner/controller a control/data path
[ ] aspoň dve competing hypotheses
[ ] discriminating observation
[ ] evidence-preserving containment
[ ] authoritative minimálna repair
[ ] controller/runtime reconvergence
[ ] original outcome verified
[ ] forbidden a adjacent cohort verified
[ ] earlier control a follow-up drill
```

## 14. Kontrolné otázky

1. Prečo status reason nie je root cause?
2. Ako scope zmenšuje hypothesis set?
3. Čo tvorí exact drill subject?
4. Ktoré evidence zachováš pred restartom alebo force delete?
5. Ako navrhneš discriminating observation namiesto náhodnej zmeny?
6. Kedy je Node `Ready` nedostatočný recovery verdict?
7. Prečo direct PodIP, ServiceIP a DNS testujú odlišné boundaries?
8. Ako odlíšiš root cause od contributing evidence-control failure?
9. Čo je forbidden-outcome validation?
10. Ako výsledok drill-u prevedieš na targeted follow-up tréning?

## Praktické drilly

Spustiteľný scenárový index a review template patria do [CKA troubleshooting drills](../../troubleshooting/cka/README.md).

## Glossary impact

Relevantné pojmy: CKA troubleshooting subject, expected-state contract, failure-domain narrowing, evidence preservation, competing hypothesis set, discriminating observation, containment, authoritative repair, reconvergence, original outcome, forbidden outcome, adjacent-cohort verification, root-cause accuracy, contributing control failure, fault-injection generation, drill score closure a targeted follow-up drill.

## Oficiálne zdroje

- [Certified Kubernetes Administrator](https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/)
- [Troubleshooting Kubernetes](https://kubernetes.io/docs/tasks/debug/)
- [Debug Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/)
- [Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/)
- [Troubleshoot Clusters](https://kubernetes.io/docs/tasks/debug/debug-cluster/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CKA timed labs](cka-timed-labs.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: IaaS, PaaS a SaaS →](../11-cloud-and-aws/iaas-paas-saas.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
