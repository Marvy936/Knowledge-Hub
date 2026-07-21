# Kubernetes troubleshooting

Kubernetes troubleshooting musí rozlíšiť API intent, controller reconciliation, scheduler placement, kubelet/runtime execution, networking, storage, security a application behavior. Rovnaký používateľský symptóm môže vzniknúť na viacerých vrstvách. Cieľom nie je spustiť čo najviac príkazov, ale vytvoriť časovú os, zachovať evidence a čo najrýchlejšie zúžiť failure domain.

## 1. Začni symptómom

Presne definuj:

- čo nefunguje,
- odkedy,
- koho a ktoré prostredie ovplyvňuje,
- či je problém permanentný alebo prerušovaný,
- čo sa tesne predtým zmenilo,
- čo stále funguje,
- aký je business/SLO dopad.

Zlé zadanie:

```text
Kubernetes nefunguje.
```

Lepšie zadanie:

```text
Od 14:05 nové Pody v namespace production zostávajú Pending.
Existujúce Pody obsluhujú traffic. Posledná zmena bola nový LimitRange.
```

## 2. Zachovaj evidence

Pred restartom, delete alebo rollbackom zachovaj:

- object YAML a status,
- Events,
- current a previous container logs,
- controller/operator logs,
- Node conditions a component logs,
- timestamps a recent changes,
- metrics a traces,
- relevantné manifests a image digests,
- audit records,
- etcd/control-plane health pri cluster incidente.

Deštruktívny príkaz môže odstrániť jediný dôkaz.

## 3. Diagnostický model

Postupuj po vrstvách:

```text
user/business symptom
→ DNS / edge / load balancer
→ Gateway/Ingress
→ Service / EndpointSlice
→ Pod readiness a application
→ controller/workload object
→ scheduler
→ kubelet/runtime
→ CNI/CSI/Node
→ API server/admission
→ etcd/control plane
→ external dependency
```

Nie každý incident začína na vrchu. Model slúži na formulovanie hypotéz a testov.

## 4. Context a cluster identity

Pred každým zásahom:

```bash
kubectl config current-context
kubectl config get-contexts
kubectl cluster-info
kubectl auth whoami
```

Over:

- správny cluster,
- namespace,
- user/ServiceAccount identity,
- API endpoint,
- čas a change window.

Veľa incidentov je operator error v nesprávnom contexte alebo namespace.

## 5. Prvé široké pozorovanie

```bash
kubectl get nodes
kubectl get pods -A
kubectl get events -A --sort-by=.metadata.creationTimestamp
kubectl get --raw='/readyz?verbose'
```

Hľadaj:

- viac Node-ov `NotReady`,
- system Pods v `Pending`/`CrashLoopBackOff`,
- dominantný Event reason,
- API server dependency failures,
- cluster-wide vs. namespace-local rozsah.

`kubectl get pods` bez namespace/all-namespaces môže skryť platformový problém.

## 6. Object-first diagnostika

Pre konkrétny object:

```bash
kubectl get <kind> <name> -n <namespace> -o yaml
kubectl describe <kind> <name> -n <namespace>
kubectl get events -n <namespace> \
  --field-selector involvedObject.name=<name> \
  --sort-by=.metadata.creationTimestamp
```

Čítaj:

- `metadata.generation`,
- `status.observedGeneration`,
- conditions,
- ownerReferences,
- finalizers,
- managedFields,
- controller-specific status,
- Events.

Ak `observedGeneration` zaostáva, controller ešte nespracoval aktuálny spec alebo je stuck.

## 7. Pod decision tree

### Pod neexistuje

Over workload controller, selector, quota/admission a `FailedCreate` Events.

### Pod `Pending`

Over:

- `PodScheduled` condition,
- `FailedScheduling`,
- PVC binding,
- quota,
- image pull secret ešte nie je relevantný, ak Pod nie je scheduled.

### Pod `ContainerCreating`

Over:

- sandbox/CNI,
- image pull,
- volume attach/mount,
- projected config/secrets,
- runtime a kubelet Events.

### Pod `Running`, ale `NotReady`

Over readiness probe, readiness gates, sidecars, application dependencies a EndpointSlice.

### `CrashLoopBackOff`

Over:

```bash
kubectl logs <pod> -c <container>
kubectl logs <pod> -c <container> --previous
kubectl get pod <pod> -o jsonpath='{.status.containerStatuses[*].lastState}'
```

### `ImagePullBackOff`

Over image reference, digest/platform, registry DNS/TLS/auth/rate limit a Node egress.

### `Terminating`

Over finalizers, kubelet/Node availability, volume detach, preStop/grace period a API deletion timestamp.

## 8. Workload controllers

### Deployment

```bash
kubectl rollout status deployment/<name> -n <ns>
kubectl get deployment,replicaset,pod -n <ns> --show-labels
kubectl describe deployment/<name> -n <ns>
```

Over:

- new vs. old ReplicaSet,
- available/updated/unavailable counts,
- progress deadline,
- readiness,
- surge capacity,
- PDB/quota/scheduling.

### StatefulSet

Over ordinal, headless DNS, PVC, ordered rollout, partition a application quorum.

### DaemonSet

Over desired/current/ready/available/misscheduled a Node eligibility.

### Job/CronJob

Over completion/retry/deadline, concurrency policy, schedule/time zone a duplicate side effects.

## 9. Scheduler

Pri `Pending`:

```bash
kubectl describe pod <pod> -n <ns>
kubectl get nodes --show-labels
kubectl describe node <node>
```

Analyzuj Event message podľa kategórie:

- insufficient CPU/memory/ephemeral storage,
- taints/tolerations,
- node selector/affinity,
- topology spread/anti-affinity,
- host ports,
- PVC/node affinity,
- unschedulable Nodes,
- quota/admission pred schedulingom.

Nepoužívaj `nodeName` na maskovanie root cause.

## 10. Node a kubelet

```bash
kubectl describe node <node>
kubectl get lease -n kube-node-lease <node> -o yaml
journalctl -u kubelet
journalctl -u containerd
crictl info
crictl ps -a
```

Rozlišuj:

- Node heartbeat/API connectivity,
- kubelet process,
- runtime,
- CNI/CSI,
- disk/inodes,
- memory/PID pressure,
- certificates a time,
- host networking/firewall.

Node `NotReady` je condition, nie root cause.

## 11. Control plane

Ak API je dostupné:

```bash
kubectl get --raw='/livez?verbose'
kubectl get --raw='/readyz?verbose'
kubectl get --raw='/readyz/etcd'
kubectl get pods -n kube-system
```

Pri self-managed static Pods over na control-plane hoste:

```bash
crictl ps -a
crictl logs <container-id>
journalctl -u kubelet
ls -l /etc/kubernetes/manifests
```

Kontroluj:

- API server TLS a etcd,
- scheduler/controller-manager leader election,
- static Pod manifests,
- certificates,
- host ports a disk,
- load-balancer backend health.

## 12. Etcd

Symptómy:

- API latency/timeouts,
- failed writes,
- control-plane components strácajú leases,
- database quota alebo disk pressure,
- leader changes/quorum loss.

Over member/endpoint health iba s vhodnými credentials a podľa topológie.

Nerob snapshot restore ako prvý troubleshooting krok. Najprv zisti, či quorum existuje a či je problém v network, disk, TLS alebo API server configuration.

## 13. Admission a API

Request môže zlyhať pred persistence:

- authentication `401`,
- authorization `403`,
- validation `422`,
- quota/LimitRange denial,
- Pod Security denial,
- mutating/validating webhook timeout,
- CRD conversion failure,
- conflict `409`.

Použi:

```bash
kubectl auth can-i <verb> <resource> -n <ns>
kubectl apply --server-side --dry-run=server -f manifest.yaml
kubectl get validatingwebhookconfigurations,mutatingwebhookconfigurations
kubectl get apiservices
```

Error message a HTTP status určujú ďalšiu vrstvu.

## 14. RBAC

Pri `Forbidden` identifikuj:

- exact subject,
- verb,
- API group/resource/subresource,
- namespace,
- binding chain.

```bash
kubectl auth can-i get secrets -n production \
  --as=system:serviceaccount:production:app
```

Neopravuj incident pridelením `cluster-admin`. Vytvor minimálne pravidlo a zdokumentuj dôvod.

## 15. Service connectivity

Postup:

```text
Service exists
→ selector sedí
→ EndpointSlice má ready endpointy
→ targetPort sedí
→ Pod počúva
→ NetworkPolicy povoľuje traffic
→ Service dataplane funguje
→ client DNS/connection je nový
```

Príkazy:

```bash
kubectl get service,endpointslice -n <ns>
kubectl describe service <name> -n <ns>
kubectl get pod -n <ns> --show-labels
```

Testuj priamo Pod IP/port aj Service name/port, aby si oddelil application a dataplane.

## 16. DNS

Z test Podu:

```bash
cat /etc/resolv.conf
getent hosts kubernetes.default.svc
nslookup <service>.<namespace>.svc
```

Rozlišuj:

- cluster-local records,
- upstream external DNS,
- UDP vs. TCP/53,
- CoreDNS health,
- NetworkPolicy,
- NodeLocal DNSCache,
- search domains/`ndots`,
- stale application cache.

DNS success nepreukazuje ready backend.

## 17. Ingress a Gateway

Postup:

```text
DNS
→ load balancer address
→ controller/Gateway status
→ listener/route accepted
→ Service
→ EndpointSlice
→ Pod
```

Over:

- class/controller,
- route attachment conditions,
- certificate/SNI,
- host/path/header match,
- external LB health,
- backend protocol a timeout,
- NetworkPolicy.

Testuj každú hranicu samostatne.

## 18. CNI a NetworkPolicy

Pri Pod network failure over:

- CNI agent/DaemonSet,
- IPAM capacity,
- Pod interface a routes,
- overlay tunnel/underlay route,
- MTU,
- host firewall/forwarding,
- policy selection a flow logs,
- problém same-node vs. cross-node.

`FailedCreatePodSandBox` je často CNI/runtime/Node symptom, nie application chyba.

## 19. Storage

PVC/Pod flow:

```text
PVC request
→ StorageClass/provisioner
→ PV binding
→ topology/scheduling
→ VolumeAttachment
→ CSI node stage/publish
→ mount
→ application permissions/filesystem
```

Over:

```bash
kubectl get pvc,pv,storageclass
kubectl describe pvc <pvc> -n <ns>
kubectl get volumeattachment
kubectl get pods -n kube-system | grep -i csi
```

Rozlišuj provisioning, attach, mount a application I/O problém.

## 20. Resources a QoS

Pri latency alebo restartoch over:

- requests/limits,
- CPU throttling,
- lastState `OOMKilled`,
- Node memory/disk/PID pressure,
- kubelet eviction,
- quota a LimitRange defaults,
- HPA metrics.

`kubectl top` je aktuálny resource snapshot, nie historická root-cause analýza.

## 21. Probes

Pri probe failure:

- over handler/path/port,
- testuj z kubelet-like network perspektívy,
- skontroluj startup čas a thresholds,
- CPU throttling/GC/thread starvation,
- dependency coupling,
- application logs pred restartom.

Dočasné vypnutie liveness môže zastaviť restart storm, ale musí byť versionovaný emergency change s následnou opravou.

## 22. HPA

```bash
kubectl describe hpa <name> -n <ns>
kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes
```

Over:

- current/desired metrics,
- target requests,
- missing/stale samples,
- max replicas,
- stabilization,
- quota,
- Pending replicas a Node capacity.

HPA môže fungovať správne a napriek tomu cluster nemá kapacitu na ďalšie Pody.

## 23. Logging a Events

Zoraď Events časovo, ale ber do úvahy agregáciu a retenciu.

Logs koreluj cez:

- Pod UID,
- container ID,
- Node,
- image digest,
- deployment revision,
- request/trace ID.

Pri Node alebo collector incidente môže `kubectl logs` a central backend ukazovať odlišný rozsah evidence.

## 24. Recent changes

Hľadaj:

- Deployment/Helm/GitOps release,
- RBAC/policy/quota zmenu,
- Node image/upgrade,
- CNI/CSI/controller update,
- certificate/secret rotation,
- DNS/LB/firewall zmenu,
- cloud provider incident.

Correlation nie je automaticky causation, ale zmena určuje prioritnú hypotézu.

## 25. Controlled reproduction

Reprodukuj najmenší bezpečný variant:

- debug Pod v rovnakom namespace,
- rovnaký ServiceAccount/NetworkPolicy,
- direct Pod IP test,
- server-side dry-run,
- canary Node,
- staging cluster,
- isolated restore lab.

Reprodukcia nesmie vytvoriť ďalšie side effects v produkčných dátach.

## 26. Debug containers

Ephemeral container môže pomôcť, ak production image nemá shell/tools:

```bash
kubectl debug -n <ns> pod/<pod> -it --image=<approved-debug-image>
```

Použitie potrebuje:

- RBAC,
- approved signed image,
- audit,
- network/security policy,
- secret/data handling,
- cleanup a evidence.

Debug image s broad tools je privilegovaná capability, nie bežná runtime dependency.

## 27. Remediation hierarchy

Preferuj:

1. odstrániť alebo rollbacknúť poslednú chybnú deklaratívnu zmenu,
2. obnoviť chýbajúcu dependency alebo kapacitu,
3. nahradiť chybný Pod/Node cez controller lifecycle,
4. aplikovať úzky emergency change,
5. roll-forward s overenou opravou,
6. disaster recovery iba pri strate authoritative state.

Restart bez hypotézy môže dočasne pomôcť, ale odstráni evidence a nezabráni recurrence.

## 28. Incident timeline

Zaznamenaj:

- UTC timestamp,
- pozorovanie a source,
- hypotézu,
- vykonaný test,
- výsledok,
- zmenu a approvera,
- dopad,
- recovery milestone.

Oddeľ fakt od interpretácie:

```text
14:07 — 0 ready EndpointSlices pre service web (fakt)
14:08 — pravdepodobná readiness/config chyba (hypotéza)
14:10 — previous logs ukazujú invalid DB URL (dôkaz)
```

## 29. Anti-patterny

### Restart všetkého naraz

Zničí evidence a rozšíri failure domain.

### `kubectl delete pod` ako univerzálna oprava

Controller vytvorí rovnaký chybný Pod.

### `cluster-admin` na vyriešenie `Forbidden`

Vytvorí trvalú privilege escalation.

### Vypnutie NetworkPolicy/Pod Security bez scope-u

Odstráni ochranu celého namespace alebo clusteru.

### Force delete StatefulSet Pod/PVC bez storage analýzy

Môže vytvoriť concurrent writer alebo data loss.

### Etcd restore pri bežnom application incidente

Vracia celý cluster state a spôsobuje veľký data-loss blast radius.

### Troubleshooting iba cez dashboard

Skryje raw object status, Events a component logs.

### Zmena viacerých vrstiev naraz

Nie je možné určiť, ktorá zmena pomohla alebo poškodila systém.

## 30. Praktický checklist

```text
[ ] správny context, cluster a namespace
[ ] presný symptóm, čas a dopad
[ ] recent changes
[ ] object spec/status/conditions
[ ] Events zoradené časovo
[ ] current a previous logs
[ ] owner controller a reconciliation status
[ ] scheduler a Node conditions
[ ] runtime/CNI/CSI podľa fázy
[ ] Service/EndpointSlice/DNS/edge chain
[ ] RBAC/admission/quota/policy
[ ] resources, OOM, pressure a probes
[ ] control-plane/etcd pri cluster-wide symptóme
[ ] external dependencies
[ ] evidence pred remediation
[ ] post-fix validation a recurrence control
```

## 31. Kontrolné otázky

1. Prečo treba začať presným symptómom a časovou osou?
2. Aké evidence zachováš pred restartom Podu?
3. Ako rozlíšiš scheduler, kubelet a application failure?
4. Aký je Service troubleshooting chain?
5. Ako sa líši provisioning, attach a mount storage failure?
6. Čo znamenajú HTTP statusy 401, 403, 409 a 422 pri API requests?
7. Prečo `kubectl top` nestačí na analýzu OOM incidentu?
8. Kedy použiť ephemeral debug container?
9. Prečo restart bez hypotézy znižuje kvalitu diagnostiky?
10. Kedy je etcd restore opodstatnený?

## Glossary impact

Relevantné pojmy: failure domain narrowing, evidence preservation, object-first troubleshooting, Kubernetes incident timeline, controlled reproduction, debug container, Service troubleshooting chain, storage troubleshooting chain, control-plane health gate, remediation hierarchy a cluster-wide symptom.

## Oficiálna dokumentácia

- [Monitoring, logging and debugging](https://kubernetes.io/docs/tasks/debug/)
- [Troubleshooting clusters](https://kubernetes.io/docs/tasks/debug/debug-cluster/)
- [Debug running Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/)
- [Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/)
- [Troubleshooting kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/troubleshooting-kubeadm/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Logging, metrics a events](logging-metrics-events.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Helm chart, template, values a release →](../10-helm-and-cka/helm-chart-template-values-release.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
