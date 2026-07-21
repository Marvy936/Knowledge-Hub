# CKA troubleshooting drills

CKA troubleshooting nie je memorovanie zoznamu príkazov. Je to schopnosť rýchlo zúžiť failure domain, identifikovať owner component, zachovať evidence, vykonať minimálnu opravu a preukázať výsledok. Keďže troubleshooting má podľa aktuálneho CKA curriculum najvyššiu váhu, musí byť samostatnou tréningovou disciplínou.

> Scenáre v tejto kapitole sú originálne tréningové drilly, nie otázky zo skutočnej skúšky.

## 1. Univerzálny troubleshooting model

```text
symptóm a scope
→ správny context/namespace/Node
→ object spec, status a conditions
→ Events a logs
→ owner controller
→ scheduler alebo kubelet/runtime
→ CNI/CSI/Service/DNS
→ control plane a etcd
→ external dependency
→ minimálna oprava
→ validácia a recurrence control
```

Každý drill musí mať:

- presný symptóm,
- root cause,
- misleading evidence,
- požadovanú opravu,
- hard validation,
- časový limit.

## 2. Failure-domain narrowing

Najprv urč scope:

### Jeden container

Pravdepodobné vrstvy:

- command/args,
- config/Secret,
- application,
- resources,
- probe,
- image/filesystem.

### Jeden Pod

- scheduling,
- sandbox/CNI,
- volume mount,
- Pod security,
- init container,
- node-local runtime.

### Jeden workload

- controller spec,
- selector,
- rollout strategy,
- HPA,
- quota,
- dependency.

### Jeden Node

- kubelet,
- runtime,
- CNI/CSI node plugin,
- disk/memory/PID pressure,
- certificate/time/network.

### Celý cluster

- API server,
- etcd,
- admission/webhooks,
- DNS/Service dataplane,
- shared identity/network/storage dependency.

## 3. Evidence-first pravidlá

Pred reštartom alebo zmazaním zachovaj:

```bash
kubectl get <object> -o yaml
kubectl describe <object>
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl logs <pod> -c <container>
kubectl logs <pod> -c <container> --previous
```

Na Node-e podľa potreby:

```bash
journalctl -u kubelet
crictl ps -a
crictl inspect <container-id>
ip route
ss -lntup
df -h
df -i
```

Reštart môže odstrániť predchádzajúce logs, timing a transient failure state.

## 4. Drill format

Každý drill rieš v štyroch krokoch:

```text
1. Diagnose — pomenuj root cause
2. Repair — urob minimálnu zmenu
3. Verify — preukáž požadovaný stav
4. Explain — jednou vetou vysvetli mechanizmus
```

Self-grading:

- 40 % root-cause accuracy,
- 30 % správna oprava,
- 20 % validácia,
- 10 % čas a bezpečnosť.

## 5. Drill 1 — CrashLoopBackOff po configuration zmene

### Symptóm

Deployment `api` má všetky Pody v `CrashLoopBackOff`. Nová revision bola nasadená pred piatimi minútami.

### Možné evidence

- `kubectl logs --previous` ukazuje invalid database URL,
- ConfigMap key existuje pod iným názvom,
- liveness probe iba zrýchľuje restarty.

### Úloha

Nájdi presný configuration mismatch, oprav Deployment alebo ConfigMap podľa zadania a over stabilné Ready replicas.

### Validácia

```bash
kubectl rollout status deployment/api -n production
kubectl get pod -n production -l app=api
```

### Mechanizmus

Container process končí kvôli invalid runtime configuration; CrashLoopBackOff je retry/backoff symptom, nie root cause.

## 6. Drill 2 — Pod zostáva Pending

### Symptóm

Pod `worker` je `Pending` bez Node assignmentu.

### Variácie root cause

- requests presahujú Node allocatable,
- required node affinity nemá matching Node,
- netolerovaný taint,
- hostPort conflict,
- unbound immediate PVC,
- quota/admission rejection parent controlleru.

### Postup

```bash
kubectl describe pod worker -n batch
kubectl get nodes --show-labels
kubectl describe node <node>
kubectl get pvc -n batch
```

### Validácia

Pod je Scheduled na feasible Node bez odstránenia požadovaného placement contractu.

## 7. Drill 3 — Service nemá endpoints

### Symptóm

Service existuje a DNS funguje, ale connection zlyhá. EndpointSlice je prázdny.

### Root-cause varianty

- selector mismatch,
- Pods nie sú Ready,
- wrong namespace,
- Service bez selectoru a bez manual EndpointSlice,
- terminating-only endpoints.

### Diagnostický chain

```text
Service selector
→ matching Pods
→ readiness
→ EndpointSlice
→ targetPort
→ application listen socket
```

### Validácia

EndpointSlice obsahuje ready endpointy a test Pod sa pripojí cez Service name.

## 8. Drill 4 — Service má endpoints, traffic stále zlyhá

### Root-cause varianty

- `targetPort` nesedí,
- application počúva iba na `127.0.0.1`,
- NetworkPolicy blokuje traffic,
- kube-proxy/alternate dataplane problém,
- MTU alebo return path,
- client používa stale connection.

### Test

Porovnaj:

```text
client → PodIP:port
client → ServiceIP:port
client → ServiceDNS:port
```

Tým oddelíš application, Service dataplane a DNS.

## 9. Drill 5 — CoreDNS failure

### Symptóm

Väčšina workloadov nevie resolve-nuť cluster-local ani external mená.

### Postup

```bash
kubectl get pod,service -n kube-system -l k8s-app=kube-dns
kubectl logs -n kube-system -l k8s-app=kube-dns
kubectl get configmap coredns -n kube-system -o yaml
kubectl run dns-test --rm -it --restart=Never --image=busybox:1.36 -- nslookup kubernetes.default.svc
```

### Root-cause varianty

- Corefile syntax,
- upstream resolver loop,
- Service/EndpointSlice chyba,
- CNI/dataplane,
- Node-local DNS cache,
- NetworkPolicy.

### Validácia

Cluster-local aj vybraný external hostname sa resolve-nú z Podu.

## 10. Drill 6 — ImagePullBackOff

### Root-cause varianty

- typo v repository/tag,
- private registry bez credentials,
- Secret v inom namespace,
- nesprávny `imagePullSecrets`,
- registry TLS/CA,
- architecture mismatch sa prejaví až po pull-e ako runtime error,
- rate limit alebo network egress.

### Evidence

```bash
kubectl describe pod <pod> -n <ns>
kubectl get secret -n <ns>
```

### Validácia

Image sa úspešne pullne a container prejde do Running/Ready bez použitia broad credentials.

## 11. Drill 7 — PVC Pending

### Root-cause varianty

- StorageClass neexistuje,
- default StorageClass nie je nastavená,
- provisioner/controller nebeží,
- `WaitForFirstConsumer` čaká na Pod scheduling,
- topology conflict,
- quota,
- unsupported access mode/volume mode.

### Postup

```bash
kubectl get pvc,pv -A
kubectl describe pvc <pvc> -n <ns>
kubectl get storageclass
kubectl get events -n <ns> --sort-by=.metadata.creationTimestamp
```

### Validácia

PVC je Bound a consumer Pod má volume mounted.

## 12. Drill 8 — Multi-Attach alebo FailedMount

### Symptóm

Pod je `ContainerCreating`; Events ukazujú attach alebo mount failure.

### Root-cause varianty

- RWO volume stále attached k starému Node-u,
- stale VolumeAttachment,
- CSI node plugin chýba,
- filesystem corruption,
- wrong secret/credentials,
- topology mismatch,
- permission/SELinux issue.

### Bezpečnostná hranica

Force detach/delete môže vytvoriť concurrent writer alebo data corruption. Najprv over workload identity, old Pod/Node a storage backend state.

## 13. Drill 9 — Node NotReady

### Postup

```bash
kubectl describe node <node>
kubectl get lease -n kube-node-lease <node> -o yaml
systemctl status kubelet
journalctl -u kubelet
crictl info
```

### Root-cause varianty

- kubelet stopped,
- expired certificate,
- API connectivity,
- container runtime down,
- disk/memory/PID pressure,
- time skew,
- CNI initialization.

### Validácia

Node je Ready a system Pods/workloads sa obnovia bez odstránenia evidencie alebo dát.

## 14. Drill 10 — Static Pod control-plane component

### Symptóm

API server, scheduler alebo controller-manager na jednom control-plane Node-e nebeží.

### Postup

- skontroluj `/etc/kubernetes/manifests`,
- YAML syntax a flags,
- certificate paths,
- hostPath mounts,
- container runtime logs,
- port conflict,
- etcd connectivity.

Kubelet sleduje static Pod manifest directory. Chybný manifest môže component odstrániť alebo opakovane reštartovať.

### Validácia

Component mirror Pod je Running a príslušný health endpoint/API function funguje.

## 15. Drill 11 — API server je dostupný, ale requests timeoutujú

### Root-cause varianty

- etcd latency/quorum,
- admission webhook timeout,
- aggregated APIService,
- API server saturation,
- DNS/network dependency webhooku,
- certificate issue.

### Postup

```bash
kubectl get --raw='/readyz?verbose'
kubectl get apiservices
kubectl get validatingwebhookconfigurations,mutatingwebhookconfigurations
```

Rozlišuj global API outage od konkrétneho resource/admission pathu.

## 16. Drill 12 — RBAC Forbidden

### Symptóm

ServiceAccount dostáva `403 Forbidden`.

### Postup

```bash
kubectl auth can-i get pods \
  --as=system:serviceaccount:team-a:reader \
  -n team-a
```

Skontroluj:

- subject namespace/name,
- Role vs. ClusterRole,
- RoleBinding namespace,
- API group,
- resource/subresource,
- verb.

### Validácia

Požadovaná operácia je povolená a nepožadované writes/secrets access zostávajú zakázané.

## 17. Drill 13 — Deployment rollout stuck

### Root-cause varianty

- readiness failure,
- insufficient capacity pre surge,
- quota,
- image pull,
- PDB/termination overlap,
- immutable selector change,
- application startup regression.

### Postup

```bash
kubectl rollout status deployment/<name> -n <ns>
kubectl describe deployment/<name> -n <ns>
kubectl get rs,pod -n <ns>
kubectl get events -n <ns> --sort-by=.metadata.creationTimestamp
```

### Validácia

Deployment má desired updated/ready/available replicas a stará ReplicaSet je škálovaná podľa strategy.

## 18. Drill 14 — HPA neškáluje

### Root-cause varianty

- metrics API nedostupná,
- CPU requests chýbajú,
- target selector/scale subresource problém,
- HPA max reached,
- quota alebo scheduler blokuje nové Pody,
- metric je stale/unknown,
- stabilization policy.

### Postup

```bash
kubectl describe hpa <name> -n <ns>
kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes
kubectl get events -n <ns>
```

### Validácia

HPA má valid metric a workload dosiahne očakávaný replica count, alebo je presne zdokumentovaný capacity limit.

## 19. Drill 15 — NetworkPolicy blokuje DNS

### Symptóm

Po zavedení default-deny egress aplikácia nevie resolve-nuť DNS.

### Root cause

Policy povoľuje application destinations, ale nie DNS traffic k cluster DNS endpointu na UDP/TCP 53 podľa cluster modelu.

### Validácia

DNS funguje, pričom ostatný nepožadovaný egress zostáva blokovaný.

## 20. Drill 16 — Gateway alebo Ingress vracia 503

### Diagnostický chain

```text
external DNS/LB
→ Gateway/Ingress status
→ listener/rule/host/path
→ backend reference
→ Service
→ EndpointSlice
→ Pod readiness/listen port
```

### Root-cause varianty

- Route nie je Accepted,
- unresolved backend reference,
- Service port mismatch,
- zero ready endpoints,
- controller class mismatch,
- TLS/host/path mismatch.

## 21. Drill 17 — etcd snapshot command zlyhá

### Root-cause varianty

- wrong endpoint,
- CA/cert/key paths,
- certificate identity,
- endpoint unhealthy,
- disk full,
- tool/version mismatch.

### Oprava

Nemeň etcd data directory. Oprav connection/tool invocation a následne validuj snapshot cez `etcdutl snapshot status` podľa podporovanej verzie.

## 22. Drill 18 — Upgrade kubeadm Node-u nedokončený

### Symptóm

Node zostal cordoned alebo kubelet version/service je nekonzistentná.

### Postup

- over control-plane/API version,
- package/binary version,
- `kubeadm upgrade` fázu,
- kubelet config,
- service logs,
- drain/uncordon stav,
- workload health.

### Validácia

Node je Ready na podporovanej verzii a workloady sa bezpečne vrátili.

## 23. Drill 19 — Resource pressure

### Symptóm

Pody sú Evicted alebo OOMKilled, prípadne Node hlási DiskPressure.

### Rozlíš:

- container memory limit OOM,
- Node-level OOM,
- kubelet memory eviction,
- ephemeral-storage eviction,
- inode exhaustion,
- CPU throttling.

### Evidence

```bash
kubectl describe pod <pod>
kubectl describe node <node>
kubectl top pod,node
dmesg | tail
df -h
df -i
```

`kubectl top` je len momentka a nevysvetľuje historický peak ani kernel OOM decision.

## 24. Drill 20 — Stuck Terminating

### Root-cause varianty

- finalizer,
- unavailable webhook/APIService,
- kubelet/Node unreachable,
- volume detach,
- preStop/termination grace,
- namespace finalization.

### Bezpečnostná hranica

Force deletion odstráni API object bez záruky, že process alebo storage writer prestal existovať.

## 25. Fault injection design

Scenár vytváraj jednou presnou chybou:

- zmeň selector key,
- nastav chybný targetPort,
- odstráň CPU request,
- pridaj netolerovaný taint,
- zmeň kubelet config path,
- poškod CoreDNS forward target,
- zmeň static Pod certificate path,
- vytvor NetworkPolicy bez DNS egressu.

Neskôr kombinuj dve súvisiace chyby, ale vyhni sa náhodnému chaosu bez známého expected state-u.

## 26. Time-boxing drillov

Začni:

- jednoduché: 5 minút,
- stredné: 8–10 minút,
- cluster/control-plane: 12–15 minút.

Meraj zvlášť:

- čas na identifikáciu root cause,
- čas na opravu,
- čas na validáciu.

Pomalá diagnóza a pomalá editácia sú odlišné tréningové problémy.

## 27. Drill review template

```text
Scenár:
Symptóm:
Scope:
Prvá hypotéza:
Dôkazy:
Root cause:
Oprava:
Validácia:
Čas diagnose/repair/verify:
Chybný pokus:
Čo precvičiť:
```

Tento záznam patrí do learning logu, nie do reálneho exam scratchpadu.

## 28. Anti-patterny

### Okamžitý restart

Odstráni evidence a môže dočasne skryť root cause.

### `kubectl delete pod` pri každom probléme

Controller vytvorí rovnaký chybný Pod.

### Úprava viacerých vrstiev naraz

Nie je jasné, ktorá zmena pomohla.

### `cluster-admin` pri RBAC chybe

Získaš funkčnosť za cenu privilege escalation.

### Force delete pri storage probléme

Môže vytvoriť concurrent writer.

### Diagnostika iba cez `kubectl get pods`

Chýbajú Events, conditions, owner a Node/component evidence.

### Memorovanie root cause podľa symptómu

Rovnaký `Pending` alebo `CrashLoopBackOff` má mnoho príčin.

## 29. Praktický master checklist

```text
[ ] správny context a namespace
[ ] presný symptóm a scope
[ ] object spec/status/conditions
[ ] Events chronologicky
[ ] current/previous logs
[ ] owner controller
[ ] scheduling a Node conditions
[ ] kubelet/runtime/CNI/CSI podľa fázy
[ ] Service/EndpointSlice/DNS/edge chain
[ ] RBAC/admission/quota/policy
[ ] requests/limits/OOM/pressure/probes
[ ] control plane/etcd pri cluster-wide scope
[ ] minimálna oprava
[ ] hard validation
[ ] recurrence alebo explanation
```

## 30. Kontrolné otázky

1. Ako zúžiš failure domain podľa scope-u?
2. Ktoré evidence zachováš pred restartom?
3. Ako odlíšiš Service selector problém od targetPort problému?
4. Aké sú hlavné príčiny Pending Podu?
5. Ako rozlíšiš cgroup OOM, eviction a Node OOM?
6. Prečo force delete predstavuje riziko pri storage?
7. Ako diagnostikuješ `403 Forbidden` bez broad role?
8. Ktoré vrstvy overíš pri API timeout-e?
9. Ako navrhneš fault injection drill s jednoznačným root cause?
10. Prečo musí self-grading hodnotiť diagnózu oddelene od opravy?

## Praktické drilly

Spustiteľný scenárový index a review template patria do [CKA troubleshooting drills](../../troubleshooting/cka/README.md).

## Glossary impact

Relevantné pojmy: CKA troubleshooting drill, failure-domain narrowing, root-cause accuracy, hard validation, fault injection, previous container logs, Service troubleshooting chain, control-plane drill, repair time, diagnosis time a drill review.

## Oficiálne zdroje

- [Certified Kubernetes Administrator](https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/)
- [Troubleshooting Kubernetes](https://kubernetes.io/docs/tasks/debug/)
- [Debug Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/)
- [Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/)
- [Troubleshoot Clusters](https://kubernetes.io/docs/tasks/debug/debug-cluster/)
