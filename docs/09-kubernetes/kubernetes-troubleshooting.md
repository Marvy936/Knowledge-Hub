# Kubernetes troubleshooting

Kubernetes troubleshooting nie je zoznam príkazov, ktoré sa spustia nad každým incidentom. Je to postupné hľadanie prvej vrstvy, na ktorej sa očakávaný prechod nestal. Používateľský request môže zlyhať na DNS, Gateway, Service dataplane, Pod sockete, konfigurácii alebo databáze. Nový Pod môže chýbať pre admission, controller, scheduling, CNI, image alebo mount. Rovnaký symptom `timeout` preto nemá jednu univerzálnu príčinu.

Dobrý postup začína presným symptómom, zachová volatile evidence a rozdelí control path od data pathu. Až potom vytvorí konkurenčné hypotézy a vyberie observation point, ktorý ich najrýchlejšie rozdelí. Reštart, delete, rollback alebo Node reboot sa vykonáva až vtedy, keď rozumieme, aký state zmení a aký dôkaz môže odstrániť.

## Začni používateľským výsledkom

Namiesto:

```text
Kubernetes nefunguje.
```

použi statement:

```text
Od 06:12 UTC vracia približne 20 % POST /payments odpoveď 502.
Zlyhania vznikajú iba pri backend Pods na Node pool-e np-136-v1.
Deployment má šesť available replicas a Pods sú Ready.
Posledná zmena bol rollout novej Node image generation.
Retries môžu vytvoriť duplicate authorization.
```

Taký opis určuje čas, scope, affected cohort, recent change a business riziko. Zároveň pomenúva, čo funguje: control plane a controller readiness sú green. Tým sa znižuje počet hypotéz.

## Zafixuj presný subject

Názov `payments-api` nestačí. Pred diagnostikou zachovaj identities:

```text
cluster context, API endpoint a operator identity
incident a release/upgrade operation ID
Deployment UID/generation a ReplicaSet UID
Pod namespace/name/UID, imageID a config generation
container ID a restart attempt
Node name/UID, Node image, kubelet/runtime a CNI generation
Service UID, EndpointSlice a backend targetRef UID
PVC/PV/backend identity pri storage incidente
request, trace a payment ID s timestampom
```

Praktické minimum:

```bash
kubectl config current-context
kubectl cluster-info
kubectl auth whoami

kubectl get deployment payments-api -n production \
  -o custom-columns='NAME:.metadata.name,UID:.metadata.uid,GEN:.metadata.generation,OBSERVED:.status.observedGeneration'

kubectl get pods -n production -l app.kubernetes.io/name=payments-api \
  -o custom-columns='NAME:.metadata.name,UID:.metadata.uid,NODE:.spec.nodeName,IP:.status.podIP,IMAGE_ID:.status.containerStatuses[0].imageID,READY:.status.containerStatuses[0].ready'
```

Ak pracuješ s nesprávnym contextom alebo namespace, každý ďalší dôkaz môže byť presvedčivý a zároveň irelevantný.

## Preserve-first boundary

Pred `kubectl delete pod`, rollbackom, drainom alebo restartom komponentu ulož stav, ktorý sa môže stratiť:

```bash
mkdir -p evidence

kubectl get deployment,replicasets,pods,service,endpointslices \
  -n production -o yaml \
  > evidence/payments-objects.yaml

kubectl get events -n production --sort-by=.lastTimestamp \
  > evidence/production-events.txt

kubectl logs -n production <pod-name> -c api \
  --timestamps \
  > evidence/pod-current.log

kubectl logs -n production <pod-name> -c api \
  --previous --timestamps \
  > evidence/pod-previous.log 2>/dev/null || true
```

Pod delete odstráni Pod UID, container IDs, `emptyDir`, current logs a časť network state-u. Node reboot odstráni conntrack, process a runtime evidence. Etcd restore prepíše cluster-wide state. Destructive operácia môže symptom dočasne odstrániť a zároveň znemožniť root-cause analýzu.

Preserve neznamená slepo exportovať celý cluster a všetky Secrets. Evidence má byť scoped, bezpečne uložené a redigované.

## Control path a data path

Control path vytvára runtime:

```text
client request
→ API authentication, authorization a admission
→ persisted object generation
→ controller reconciliation
→ scheduler binding
→ kubelet, CRI, CNI a CSI
→ Pod status, readiness a EndpointSlice
```

Data path nesie používateľský request:

```text
client DNS a TLS
→ Gateway alebo Ingress
→ Service dataplane
→ EndpointSlice backend
→ Pod network a socket
→ application process a loaded config
→ dependency alebo storage
→ response a business commit
```

Control path môže byť zelený a data path chybný. Deployment môže mať available replicas, no Gateway route môže smerovať na zlý Service. Naopak, existujúce requesty môžu fungovať počas etcd quorum outage, kým sa nepokúsime meniť objekty.

## Hľadaj prvý chýbajúci transition

Pri rollout-e čítaj graph zhora nadol:

```bash
kubectl get deployment payments-api -n production -o yaml
kubectl get rs -n production -l app.kubernetes.io/name=payments-api -o wide
kubectl get pods -n production -l app.kubernetes.io/name=payments-api -o wide
```

Ak nová Deployment generation neexistuje, problém je v client/API/admission. Ak generation existuje, ale nový ReplicaSet nie, problém je v Deployment controlleri alebo jeho create requeste. Ak ReplicaSet existuje bez Podov, kontroluj ReplicaSet conditions, Events, quota a Pod admission. Ak Pod existuje bez Node, kontroluj scheduler. Ak Node existuje a Pod je `ContainerCreating`, presuň sa na kubelet, CNI, CSI alebo image.

Tento postup je presnejší než okamžité čítanie application logov, ktoré možno ešte ani neexistujú.

## API request zlyhal

Pri `Forbidden`, `Invalid`, webhook timeout-e alebo conflict-e zachovaj HTTP status a server response:

```bash
kubectl apply --server-side --dry-run=server \
  --field-manager=atlas-release \
  -f manifest.yaml -o yaml
```

Over identitu a permission:

```bash
kubectl auth whoami
kubectl auth can-i patch deployments.apps -n production
```

`Forbidden` patrí authorization vrstve. `Invalid` môže byť schema alebo immutable-field problém. Admission webhook error patrí webhook Service/TLS/configuration pathu. `Conflict` pri server-side apply ukazuje field ownership, nie automaticky nedostupný API server.

Ak request vôbec nedorazil do očakávaného API endpointu, audit event môže chýbať. Client kubeconfig, proxy a DNS control-plane endpointu sú pred API serverom.

## Controller nerobí progress

Porovnaj generation a observedGeneration:

```bash
kubectl get deployment payments-api -n production \
  -o jsonpath='generation={.metadata.generation} observed={.status.observedGeneration}{"\n"}'
```

Ak observed zaostáva, controller nemusí spracúvať latest intent. Skontroluj leader election, controller logs/metrics a API watches. Ak observed sedí, čítaj conditions a child objects.

Events sú užitočné, ale nie úplné:

```bash
kubectl get events -n production --sort-by=.lastTimestamp
```

Controller môže opakovane zlyhávať na quota, admission alebo external API. Restart controller-managera nie je oprava neplatného desired state-u.

## Pod je Pending bez Node

```bash
kubectl describe pod -n production <pod-name>
```

Scheduling message môže kombinovať insufficient resources, taints, affinity a volume topology. Potrebujeme zistiť, či existuje aspoň jeden Node spĺňajúci všetky hard constraints.

Skontroluj requests, Node labels/taints, PVC topology a host ports. Pridanie všeobecnej Node kapacity nepomôže, ak volume je viazaný na inú zone alebo required anti-affinity už obsadila všetky eligible hosts.

Scheduler diagnosis končí, keď Pod dostane `.spec.nodeName`. Ďalšie zlyhanie patrí Node vrstve.

## Pod má Node, ale container nevznikol

`ContainerCreating`, `ErrImagePull`, `FailedCreatePodSandBox`, `FailedMount` a `FailedAttachVolume` vznikajú pred application serving state-om.

```bash
kubectl describe pod -n production <pod-name>
kubectl get pod -n production <pod-name> -o yaml
```

Rozlišuj:

```text
sandbox/CNI failure
image resolution alebo pull
volume provision/attach/mount
local Node admission a resource pressure
container create security/config error
```

Pri Node-local diagnostike použite nástroje platformy, napríklad `crictl`, kubelet/runtime/CNI/CSI logs a host filesystem/network state. Zachovaj sandbox/container ID a správny CRI endpoint.

Application logs pri `FailedCreatePodSandBox` nedávajú zmysel, pretože process nevznikol.

## Container crashuje

Prečítaj current a previous state:

```bash
kubectl get pod -n production <pod-name> \
  -o jsonpath='{.status.containerStatuses[0]}' | jq .

kubectl logs -n production <pod-name> -c api --previous
```

Exit code a reason sú signály, nie úplná príčina. `OOMKilled` smeruje k memory/cgroup analýze. `Error` s exit 1 potrebuje application logs. Exit 137 môže byť OOM alebo iný SIGKILL. `permission denied` môže byť filesystem, seccomp, capabilities alebo LSM.

`CrashLoopBackOff` je backoff po opakovaných failures, nie root cause. Hľadaj prvý terminated state a startup inputs.

## Running nie je Ready

Ak process beží, ale readiness zlyháva:

```bash
kubectl describe pod -n production <pod-name>
kubectl get pod -n production <pod-name> \
  -o jsonpath='{range .status.conditions[*]}{.type}{"="}{.status}{" reason="}{.reason}{"\n"}{end}'
```

Testuj endpoint z relevantného pathu. Kubelet HTTP probe ide priamo na Pod IP, nie cez Service. Application môže odpovedať na localhost a nie na Pod interface. Readiness môže používať zlý path, port alebo Host header.

Ak dependency zlyháva, rozhodni, či readiness contract správne odpojuje Pod alebo zbytočne premieňa shared incident na total outage. Vypnutie readiness iba skryje problematický serving state.

## Service nemá endpoints

```bash
kubectl get service payments-api -n production -o yaml
kubectl get endpointslices -n production \
  -l kubernetes.io/service-name=payments-api -o yaml
kubectl get pods -n production --show-labels
```

Prázdny EndpointSlice backend inventory zvyčajne znamená selector mismatch alebo žiadne Ready matching Pods. Kontroluj named targetPort a targetRef UID.

Service selector nepozná Deployment ownership. Debug Pod s rovnakým labelom môže byť nesprávne vybraný.

## Direct Pod funguje, Service nie

Controlled debug Pod môže porovnať:

```text
Pod IP:containerPort
Service DNS/ClusterIP:servicePort
```

Ak direct Pod path funguje a Service path nie, hypotézy zahŕňajú Service port mapping, EndpointSlice, NetworkPolicy, per-Node Service dataplane alebo return path.

Test musí pochádzať z affected source Node/Pod identity. Service dataplane môže byť chybný iba na jednej Node generácii.

## DNS zlyháva

Zachovaj exact query a Pod resolver config:

```bash
kubectl exec -n production <pod-name> -- cat /etc/resolv.conf
```

Porovnaj krátke meno, namespace-qualified meno a FQDN, A/AAAA, UDP/TCP a affected/unaffected Node.

CoreDNS Pod Ready nepreukazuje Service path z affected Node-u. NodeLocal DNSCache pridáva per-Node failure boundary. NetworkPolicy musí povoľovať actual resolver destination a TCP fallback.

## NetworkPolicy alebo CNI

Pri network failure fixuj source Pod UID/IP/Node, destination UID/IP/Node, port, protocol a timestamp. Potom oddeľ:

```text
application bind/listener
NetworkPolicy verdict
same-Node path
cross-Node route/tunnel
Service NAT/translation
MTU a conntrack
reverse path
```

Policy YAML môže vyzerať správne, ale selector môže vybrať inú množinu. Allowed flow musí prejsť a forbidden flow musí zlyhať z očakávaného dôvodu.

Plošné zmazanie NetworkPolicy počas incidentu rozšíri exposure a môže odstrániť dôkaz. Bezpečnejšie je controlled temporary allow pre presný subject s ownerom a expiry, ak je containment rozhodnutie schválené.

## Storage

```bash
kubectl get pvc -n production -o wide
kubectl get pv
kubectl get volumeattachments.storage.k8s.io
kubectl describe pod -n production <pod-name>
```

`PVC Bound` nepreukazuje attach alebo mount. `Mounted` nepreukazuje správnu data generation. Sleduj PVC UID, PV UID, CSI volumeHandle, topology, attachment a backend state.

Force detach alebo force delete bez fencing-u môže vytvoriť dvoch writerov. Pri stateful incidente najprv potvrď, že starý Node/process už nemôže zapisovať.

## CPU, memory a Node pressure

`kubectl top` je začiatok:

```bash
kubectl top pod -n production <pod-name> --containers
kubectl top node <node-name>
```

CPU throttling nemusí byť viditeľný z usage sample. Memory limit môže spôsobiť OOM. Node disk/inode/PID pressure môže evictovať Pods alebo zablokovať image pull.

Čítaj Pod terminated reason, Node conditions a Node-local cgroup/pressure/filesystem evidence. Rozlišuj container OOM restart v rovnakom Pod UID od Pod eviction a replacementu.

## HPA nereaguje alebo scale nepomáha

```bash
kubectl describe hpa payments-api -n production
kubectl get deployment payments-api -n production
kubectl get events -n production --sort-by=.lastTimestamp
```

HPA môže nemať fresh metrics, môže byť na min/max limite alebo môže správne zvýšiť desired replicas, ktoré sa následne nevytvoria pre quota alebo sa neschedulujú.

End-to-end autoscaling chain je:

```text
metric
→ HPA desired replicas
→ Deployment scale
→ Pod create/admission
→ scheduling/Node capacity
→ runtime/readiness
→ Service capacity
```

Zelený HPA condition nie je serving capacity.

## API server alebo etcd

Ak writes zlyhávajú cluster-wide, over stable endpoint a readiness:

```bash
kubectl get --raw='/readyz?verbose'
```

API server listener môže byť dostupný a etcd quorum nie. Bežiace workloads môžu pokračovať. Nevykonávaj etcd restore ako prvú reakciu na transient latency alebo jeden broken API server backend.

Etcd recovery vyžaduje snapshot identity, fencing a cluster-wide DR runbook. Najprv preserve component logs, member state a exact error.

## Observability môže klamať absenciou

Ak central logs neobsahujú errors z affected cohorty, over telemetry coverage:

```text
má každý affected Node collector Pod?
sleduje správnu runtime log path?
kedy prišiel posledný record z Pod UID?
funguje local kubectl logs?
majú metrics/traces rovnakú medzeru?
```

Chýbajúce telemetry je vlastný failure. Nemusí byť root cause application incidentu.

## Detailný incident: green cluster, intermittent 502 po Node upgrade-e

### Symptom

Po rollout-e Node poolu `np-136-v1` začalo približne 20 % payment requestov vracať 502. Deployment `payments-api` mal desired, ready aj available replicas. Pods boli rozdelené medzi staré a nové Nodes. Zlyhané requesty sa vždy mapovali na Pod na novej Node generation. Central logs z týchto Podov chýbali, ale logs zo starých Nodes boli normálne.

### Zafixovanie requestu

Z edge logu sa vybral request `req-81f2`, payment ID `pay-100` a backend Pod IP. EndpointSlice targetRef priradil IP ku konkrétnemu Pod UID.

```bash
kubectl get endpointslices -n production \
  -l kubernetes.io/service-name=payments-api -o json \
  > evidence/endpointslices.json

kubectl get pod -n production <affected-pod> -o json \
  > evidence/affected-pod.json

kubectl get node <affected-node> -o json \
  > evidence/affected-node.json
```

Zaznamenal sa imageID, config generation, Node UID, Node image label, kubelet/runtime a CNI DaemonSet revision.

### Konkurenčné hypotézy

Aplikácia mohla mať inú konfiguráciu, readiness mohla byť plytká, CPU mohol byť throttled, Service selector mohol publikovať nesprávny Pod, NetworkPolicy mohla blokovať iba novú cohortu, CNI route/tunnel alebo Service dataplane mohli byť partial a chýbajúci collector mohol skrývať application error.

Namiesto okamžitého restartu sa porovnal jeden zdravý old-Node Pod a jeden zlyhávajúci new-Node Pod s rovnakým imageID a config generation.

### Rozdelenie application a network hypotéz

Z affected Node-u fungoval request na application localhost v Pode a same-Node Pod-to-Pod traffic. Cross-Node direct Pod IP a Service path intermittently zlyhávali pri väčších payloads. Application logs cez `kubectl logs` neukazovali request, ktorý sa k procesu nikdy nedostal.

EndpointSlice bol správny a NetworkPolicy engine reportoval allow verdict. Packet capture ukázal packet na source Node-i, ale nie na destination Node-i pri tunelovanej ceste.

### Root cause

Nový Node image nepoužil kernel module a MTU configuration očakávanú CNI revision. CNI agent process a shallow health endpoint boli zelené, no dataplane initialization bola partial. Malé a same-Node flows fungovali, cross-Node payloads sa strácali.

Collector failure bol druhý problém. Nový runtime zapisoval logs do zmenenej path generation a collector DaemonSet sledoval starý path. Preto central query bola slepá iba na nových Nodes.

### Containment

Nový Node pool sa zastavil. Affected Nodes sa cordonovali a application endpoints sa z nich postupne odobrali cez bezpečný drain, pričom sa rešpektoval PDB a payment idempotency. Nodes, CNI state, routes a packet captures sa zachovali pred replacementom.

NetworkPolicy ani TLS sa nevypínali plošne. Client retries sa dočasne obmedzili, aby nezosilňovali duplicate-payment riziko.

### Autoritatívna oprava

Platforma vytvorila immutable Node image `np-136-v2` s opraveným kernel/CNI prerequisite a zladenou MTU. Nové Nodes zostali pod bootstrap taintom, kým capability canary neoverila sandbox, DNS, same/cross-Node traffic, Service, allowed/forbidden NetworkPolicy, storage a telemetry.

Collector konfigurácia sa aktualizovala na nový runtime path a coverage gate vyžadovala fresh logs a metrics z každého Node-u.

### Recovery verification

Na novej cohort-e prešli:

```text
malé aj veľké cross-Node payloady
ClusterIP a Gateway request
allowed NetworkPolicy flow
forbidden NetworkPolicy flow
payment commit exactly once
image/config/secret identity
central aj local telemetry
Node replacement a druhý reconcile cycle
```

Starý chybný Node pool sa odstránil až po stabilnom canary a business SLO. Incident sa neuzavrel iba zmiznutím 502; overila sa aj absencia duplicate authorizations.

## Controlled reproduction

Keď production evidence nestačí, vytvor controlled reproduction s rovnakým image, config a Node generation, ale bez production trafficu. Meníš iba jednu premennú:

```text
old vs. new Node
same vs. cross-Node path
Service vs. direct Pod
small vs. MTU-sized payload
policy on vs. presný controlled allow
```

Reproduction nemá používať production Secret alebo vykonať reálny payment. Jej cieľom je rozdeliť technické hypotézy.

## Remediation podľa chybnej vrstvy

Restart je vhodný pri dočasnom process state-e, ktorý application nevie obnoviť. Recreate Podu je vhodný, keď Pod runtime/config generation je chybná, ale template je správna. Rebuild a rollout sú potrebné pri chybnom image alebo template. Node replacement rieši host/runtime drift. Etcd restore patrí cluster state disaster recovery.

```text
process state → restart container/Pod podľa contractu
effective Pod runtime → controlled recreate
source template/image → versionovaný roll-forward
Node/kernel/runtime → cordon, drain a immutable replacement
control-plane data loss → DR restore
```

Najnižší zásah, ktorý odstráni root cause a zachová safety, je lepší než plošný reboot.

## Recovery acceptance

Po oprave over pôvodný outcome aj zakázané outcomes:

```text
pôvodný request funguje
payment vznikne práve raz
nová aj susedné cohorts sú zdravé
forbidden network/RBAC/security paths zostávajú blokované
old digest/config/Node generation nie sú v serving inventory
telemetry pokrýva všetky sources
second reconcile/restart nemení verdict
```

Bez forbidden testu môže incidentná oprava obnoviť dostupnosť tým, že odstráni security control. Bez second-cycle testu môže byť oprava iba ručný drift.

## Model, ktorý si treba odniesť

Kubernetes incident rieš od používateľského symptómu k presnému cluster, object, Pod, Node, data a flow subjectu. Zachovaj evidence, rozdeľ control path a data path, nájdi prvý chýbajúci transition a vyber test, ktorý rozdelí viac hypotéz. Remediation musí meniť autoritatívnu vrstvu a recovery sa uzatvára technickým, business aj forbidden-outcome dôkazom.

## Referencie

- [Troubleshooting Applications](https://kubernetes.io/docs/tasks/debug/debug-application/)
- [Troubleshooting Clusters](https://kubernetes.io/docs/tasks/debug/debug-cluster/)
- [Debugging Kubernetes Nodes with crictl](https://kubernetes.io/docs/tasks/debug/debug-cluster/crictl/)
- [Services, Load Balancing, and Networking](https://kubernetes.io/docs/concepts/services-networking/service/)
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
