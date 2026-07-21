# Pod

Pod je najmenší deployable compute object v Kubernetes. Reprezentuje jednu alebo viac úzko spolupracujúcich containers, ktoré zdieľajú Pod-level network identity, lifecycle boundary a explicitne pripojené volumes. Pod nie je malá VM ani iba synonymum pre container. Je to runtime envelope, ktorý scheduler pridelí jednému Node-u a kubelet na danom Node-e realizuje.

## 1. Prečo existuje Pod

Samotný container abstraction nestačí pre prípady, keď viac processes musí:

- zdieľať jednu IP a port space,
- komunikovať cez `localhost`,
- zdieľať volumes,
- byť schedulingovo umiestnených spolu,
- mať spoločný lifecycle a security context,
- byť spravovaných ako jedna workload replica.

Pod poskytuje túto co-location a co-scheduling jednotku.

## 2. Základný manifest

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web
  labels:
    app: web
spec:
  containers:
    - name: web
      image: nginx:1.27
      ports:
        - name: http
          containerPort: 80
```

Vytvorenie:

```bash
kubectl apply -f pod.yaml
kubectl get pod web -o wide
```

Pri produkčnom stateless workload-e sa Pod zvyčajne nevytvára priamo. Vytvára ho Deployment/ReplicaSet alebo iný workload controller.

## 3. Pod identity

Pod má:

- `metadata.name`,
- namespace,
- immutable UID konkrétnej inštancie,
- labels a annotations,
- pridelený Node,
- Pod IP podľa network modelu,
- spec a status.

Ak controller nahradí Pod, nový Pod:

- môže mať podobný generated name,
- dostane nové UID,
- môže dostať inú IP,
- môže bežať na inom Node-e,
- vytvorí nové container instances.

Preto application nemá používať Pod UID/IP ako dlhodobú externú identity bez vyššej abstraction.

## 4. Pod je viazaný na jeden Node

Všetky containers jedného Podu bežia na rovnakom Node-e.

Po scheduling-u Pod typicky zostáva viazaný na daný Node až do:

- dokončenia,
- zmazania,
- eviction,
- Node failure,
- terminálneho Pod failure.

Kubernetes nepresúva bežiaci Pod na iný Node. Vyšší controller vytvorí nový Pod.

## 5. Shared network namespace

Containers v Pode typicky zdieľajú:

- jednu Pod IP,
- rovnaký port namespace,
- loopback interface,
- network routes,
- DNS configuration.

Komunikácia:

```text
container A → localhost:9000 → container B
```

Dôsledky:

- dva containers nemôžu bindovať rovnaký port/address súčasne,
- `localhost` označuje celý Pod network namespace,
- network policy typicky cieli Pod endpoint, nie jednotlivý container,
- všetky containers zdieľajú Pod-level network identity.

## 6. Pod sandbox

Container runtime vytvorí Pod sandbox, ktorý drží zdieľané runtime resources, najmä network namespace.

Zjednodušený flow:

```text
Pod spec
→ kubelet
→ CRI RunPodSandbox
→ CNI setup
→ init containers
→ application containers
```

Ak sandbox creation zlyhá, Pod môže zostať v `Pending`/`ContainerCreating` s Events ako `FailedCreatePodSandBox`.

## 7. Shared volumes

Pod definuje volumes v `spec.volumes` a jednotlivé containers ich mountujú cez `volumeMounts`.

```yaml
spec:
  volumes:
    - name: shared
      emptyDir: {}
  containers:
    - name: producer
      image: example/producer:1
      volumeMounts:
        - name: shared
          mountPath: /shared
    - name: consumer
      image: example/consumer:1
      volumeMounts:
        - name: shared
          mountPath: /shared
```

Volume lifecycle závisí od typu:

- `emptyDir` je viazané na Pod lifecycle na Node-e,
- PVC môže odkazovať na persistent storage,
- projected volumes môžu poskytovať ConfigMaps, Secrets alebo service account data,
- hostPath viaže Pod na host filesystem a predstavuje vysoké security riziko.

## 8. Shared process a IPC namespaces

Defaultne containers nemusia vidieť processes ostatných containers.

Pod môže podľa configuration zdieľať process namespace:

```yaml
spec:
  shareProcessNamespace: true
```

To umožní cross-container process inspection/signal use cases, ale rozširuje coupling a security exposure.

IPC a host namespaces sa konfigurujú samostatne. Host PID/network/IPC používaj iba pri jasnom system workload threat modeli.

## 9. Containers

Každý container má vlastné:

- image,
- command/args,
- environment,
- mounts,
- resource requests/limits,
- probes,
- lifecycle hooks,
- security context.

Containers v Pode zdieľajú Pod-level resources, ale stále majú oddelený root filesystem, process a cgroup scope podľa runtime configuration.

## 10. Single-container Pod

Najbežnejší model:

```text
1 Pod = 1 application container
```

Pod abstraction je stále potrebná pre:

- scheduler,
- network identity,
- volumes,
- probes,
- service selection,
- policy,
- status,
- future auxiliary containers.

## 11. Multi-container Pod

Viac containers patrí do jedného Podu iba ak sú úzko viazané lifecycle-om a placementom.

Vhodné patterns:

- sidecar proxy/agent,
- log/format adapter pri opodstatnenom modeli,
- local helper server,
- content synchronizer,
- init/migration helper,
- service mesh proxy.

Nevhodné:

- dve nezávislé business services,
- components s odlišným scalingom,
- components s odlišným rollout lifecycle,
- zdieľanie Podu iba kvôli „úspore“.

Ak sa components musia škálovať alebo nasadzovať nezávisle, majú byť samostatné workloads.

## 12. Init containers

Init containers bežia pred bežnými application containers.

```yaml
spec:
  initContainers:
    - name: prepare
      image: busybox:1.37
      command: ["sh", "-c", "cp /source/config /work/config"]
      volumeMounts:
        - name: work
          mountPath: /work
```

Vlastnosti:

- bežia postupne,
- každý musí úspešne skončiť,
- používajú vlastný image a resources,
- môžu pripravovať shared volume,
- nemajú slúžiť ako nebezpečný nekonečný dependency wait loop.

Zlyhávajúci init container blokuje štart application containers.

## 13. Sidecar containers

Sidecar je auxiliary container, ktorý beží popri hlavnom application containeri.

Use cases:

- proxy,
- telemetry agent,
- config/content synchronizer,
- local security helper.

Sidecar musí mať:

- definovaný startup ordering podľa reálne podporovaného Pod lifecycle modelu,
- shutdown behavior,
- resources,
- probes,
- failure policy,
- log/metric ownership.

Neformálny „bežný container ako sidecar“ môže mať problematické shutdown ordering. Používaj podporované lifecycle semantics a testuj konkrétnu Kubernetes verziu.

## 14. Ephemeral containers

Ephemeral containers sa pridávajú do existujúceho Podu na troubleshooting.

Použitie:

```bash
kubectl debug pod/web -it --image=busybox:1.37
```

Charakteristiky:

- nie sú súčasťou pôvodného desired workload contractu,
- nemajú rovnaké možnosti ako bežné application containers,
- typicky sa nereštartujú,
- zvyšujú debugging access a musia byť RBAC/policy kontrolované,
- nemajú slúžiť na trvalú opravu production Podu.

## 15. Pod phase

Pod `.status.phase` je high-level summary:

- `Pending`,
- `Running`,
- `Succeeded`,
- `Failed`,
- `Unknown`.

Phase nie je kompletný state machine a nemá obsahovať všetky dôvody.

`CrashLoopBackOff`, `ContainerCreating` alebo `Terminating` sú CLI/status reasons alebo display states, nie samostatné Pod phases.

## 16. Pod conditions

Bežné Pod conditions môžu zahŕňať:

- `PodScheduled`,
- `Initialized`,
- `ContainersReady`,
- `Ready`,
- ďalšie platformové alebo scheduling conditions podľa verzie/features.

Pod môže byť:

```text
phase=Running
Ready=False
```

To znamená, že processy bežia, ale Pod nemá prijímať traffic podľa readiness contractu.

## 17. Container status

Každý container status obsahuje stav:

- `Waiting`,
- `Running`,
- `Terminated`.

Dôležité fields:

- reason,
- exit code,
- signal,
- started/finished time,
- restart count,
- ready,
- image/imageID,
- last state.

Diagnostika:

```bash
kubectl get pod web -o jsonpath='{.status.containerStatuses}'
kubectl describe pod web
kubectl logs web --previous
```

## 18. Restart policy

Pod `restartPolicy`:

- `Always`,
- `OnFailure`,
- `Never`.

Policy sa aplikuje na containers v Pode podľa workload semantics.

Pri Deployment workload-e je typicky `Always`.

Container restart:

- nemení Pod UID,
- nemusí meniť Pod IP,
- zachová Pod volumes ako `emptyDir`,
- zvyšuje restart count.

## 19. CrashLoopBackOff

CrashLoopBackOff znamená, že container opakovane štartuje a zlyháva, pričom kubelet aplikuje backoff.

Diagnostika:

```bash
kubectl describe pod <pod>
kubectl logs <pod> -c <container>
kubectl logs <pod> -c <container> --previous
```

Kontroluj:

- command/args,
- exit code,
- missing config/secret,
- permissions,
- liveness probe,
- dependencies,
- OOM,
- architecture/runtime dependencies.

Restartovanie Podu bez root cause môže iba resetovať časť evidence.

## 20. Image pull policy

Bežné values:

- `Always`,
- `IfNotPresent`,
- `Never`.

Policy spolu s tagom/digestom a local image cache určuje pull behavior.

Produkčný model:

- immutable artifact identity,
- controlled registry authentication,
- predictable pull policy,
- multi-platform manifest,
- scan/signature/provenance policy.

`Always` neznamená, že sa vždy prenesú všetky layers; runtime môže overiť registry reference a znovu použiť content-addressed blobs.

## 21. Commands a arguments

Kubernetes fields:

- `command` prepisuje image `ENTRYPOINT`,
- `args` prepisuje image `CMD`.

```yaml
containers:
  - name: app
    image: example/app:1
    command: ["/usr/local/bin/app"]
    args: ["serve", "--port", "8080"]
```

Exec-array forma znižuje shell quoting a signal ambiguity.

Runtime config nemá permanentne opravovať chybný image contract množstvom environment-specific overrides.

## 22. Environment variables

Pod môže dodávať environment cez:

- literal `env`,
- ConfigMap/Secret key refs,
- `envFrom`,
- Downward API fields,
- service environment podľa cluster behavior.

```yaml
- name: APP_MODE
  value: production
- name: DATABASE_PASSWORD
  valueFrom:
    secretKeyRef:
      name: database
      key: password
```

Environment procesu sa po štarte dynamicky nemení. Zmena ConfigMap/Secret hodnoty použitej cez env typicky vyžaduje nový container/Pod.

## 23. Resource requests a limits

```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi
```

Requests ovplyvňujú scheduling a resource shares.

Limits ovplyvňujú runtime enforcement:

- CPU throttling,
- memory OOM behavior,
- ďalšie resource-specific controls.

Resources sa definujú per container a Pod-level výsledok závisí od sumy/Pod modelu a init-container calculation rules.

## 24. QoS úvod

Pod QoS class sa odvodzuje z requests/limits:

- `Guaranteed`,
- `Burstable`,
- `BestEffort`.

QoS ovplyvňuje resource pressure a eviction behavior. Detailne sa rieši v samostatnej kapitole Requests, limits a QoS.

## 25. Probes

### Startup probe

Chráni pomaly štartujúci workload pred predčasnou liveness/readiness evaluáciou.

### Liveness probe

Určuje, či má kubelet container reštartovať.

### Readiness probe

Určuje, či má byť Pod považovaný za ready pre Service endpoints.

Príklad:

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: http
  periodSeconds: 5

livenessProbe:
  httpGet:
    path: /live
    port: http
  periodSeconds: 10
```

Liveness nemá zlyhávať iba preto, že je krátkodobo nedostupná vzdialená dependency, ak restart nepomôže.

## 26. Lifecycle hooks

### `postStart`

Spustí hook okolo začiatku container lifecycle-u; nie je garantované, že prebehne pred samotným entrypointom.

### `preStop`

Spustí sa pri graceful termination pred termination signalom podľa lifecycle semantics.

Hooks:

- musia byť bounded,
- nemajú byť jediným miestom kritickej durable logiky,
- ich failure/timeout ovplyvňuje lifecycle,
- potrebujú observability.

## 27. Graceful termination

Zjednodušený Pod deletion flow:

1. API nastaví deletion timestamp a grace period.
2. Endpoint/traffic readiness sa začne meniť podľa controllers a Pod conditions.
3. Kubelet spustí `preStop`, ak existuje.
4. Runtime odošle termination signal PID 1.
5. Application ukončí prijímanie práce a dokončí in-flight requests.
6. Po grace period môže nasledovať force kill.
7. Kubelet a CNI/CSI vykonajú cleanup.

Application potrebuje:

- signal handling,
- connection draining,
- bounded shutdown,
- idempotent retry semantics pre nedokončenú prácu.

## 28. `terminationGracePeriodSeconds`

```yaml
spec:
  terminationGracePeriodSeconds: 30
```

Hodnota musí zodpovedať:

- maximum request/job duration,
- load balancer propagation,
- `preStop` času,
- storage flush,
- controller rollout budgetu.

Príliš krátky čas spôsobí force kill. Príliš dlhý spomaľuje rollout a drain.

## 29. Pod readiness gates

Readiness gates umožňujú zahrnúť custom Pod conditions do readiness rozhodnutia.

Použitie:

- external load balancer registration,
- platform-specific attachment,
- custom admission do trafficu.

Custom controller musí condition spoľahlivo nastavovať. Chýbajúca condition môže Pod ponechať non-ready.

## 30. Scheduling fields

Pod spec môže ovplyvniť placement cez:

- `nodeSelector`,
- affinity/anti-affinity,
- topology spread,
- taints/tolerations,
- priority,
- scheduler name,
- resource requests,
- volume topology,
- host ports.

Po scheduling-u je `.spec.nodeName` bežne nastavené na pridelený Node.

Priamy `nodeName` bypassuje časť scheduler logic a používa sa iba v špecifických system/debug prípadoch.

## 31. Pod overhead

Sandboxed runtime alebo RuntimeClass môže pridávať Pod overhead, ktorý scheduler zohľadňuje pri capacity calculation podľa konfigurácie.

Application resource requests nemusia byť jedinou spotrebou Podu. Existuje aj:

- sandbox overhead,
- sidecars,
- init containers,
- log buffers,
- kernel/network/storage overhead.

## 32. Security context

Pod-level a container-level security context môže nastavovať:

- runAsUser/runAsGroup,
- fsGroup,
- supplemental groups,
- capabilities,
- privilege escalation,
- read-only root filesystem,
- seccomp profile,
- SELinux options,
- privileged mode,
- host namespaces.

Container-level setting môže pre príslušné fields prepísať Pod-level default.

Security context neoveruje, že application reálne funguje ako non-root; image ownership a volume permissions musia byť kompatibilné.

## 33. Service account

Pod môže používať ServiceAccount identity.

Podľa configuration môže dostať projected token, CA data a namespace informáciu.

Princípy:

- dedicated service account pre workload,
- least privilege RBAC,
- vypnúť automount, ak API access netreba,
- krátkodobé projected tokens,
- nepoužívať default ServiceAccount s broad oprávneniami.

## 34. DNS a hostname

Pod má DNS configuration podľa cluster DNS, namespace, policy a explicitných overrides.

`hostname`, `subdomain`, Pod name a Service môžu ovplyvniť DNS identity.

Pod IP/name nie je automaticky stabilná service identity. Service alebo StatefulSet/headless Service model poskytuje vyššiu stabilitu podľa use case-u.

## 35. Host ports a host network

`hostPort` rezervuje port na Node-e a obmedzuje scheduling.

`hostNetwork: true` zdieľa host network namespace.

Riziká:

- port collisions,
- menšia isolation,
- exposure host interfaces,
- odlišné DNS behavior,
- node-specific coupling.

Používaj najmä pri system DaemonSet workload-e alebo jasnom network requirement-e.

## 36. Pod disruption

Pod môže zaniknúť kvôli:

- rollout/replacement,
- Node drain,
- eviction,
- preemption,
- Node failure,
- autoscaling,
- user deletion,
- controller scale-down.

Application musí predpokladať, že Pod je disposable a môže byť nahradený.

PodDisruptionBudget rieši iba určitú triedu voluntary disruptions a negarantuje dostupnosť pri všetkých failure modes.

## 37. Direct Pod vs. controller-managed Pod

Priamo vytvorený Pod:

- po Node failure nie je vyšším controllerom automaticky nahradený,
- nemá rollout/replica management,
- je vhodný najmä na learning/debug alebo veľmi špecifický singleton use case.

Controller-managed Pod:

- controller obnoví desired replica count,
- používa Pod template,
- podporuje rollout/identity semantics podľa controller type-u.

V produkcii preferuj vhodný workload controller.

## 38. Pod template

Vyššie resources obsahujú Pod template:

```yaml
spec:
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: example/web:1
```

Zmena template-u typicky vedie k vytváraniu nových Pods. Existing Pod spec je z veľkej časti immutable; replacement je bežný update mechanismus.

## 39. Static a mirror Pods

Static Pod spravuje kubelet z local manifestu.

Mirror Pod je API reprezentácia static Podu.

Odlišnosti:

- bez bežného scheduleru,
- viazaný na konkrétny Node,
- authoritative source je local manifest,
- nemožno ho spravovať ako Deployment Pod.

## 40. Observability

Základné príkazy:

```bash
kubectl get pod <pod> -o wide
kubectl get pod <pod> -o yaml
kubectl describe pod <pod>
kubectl logs <pod> -c <container>
kubectl logs <pod> -c <container> --previous
kubectl top pod <pod> --containers
kubectl get events --field-selector involvedObject.name=<pod>
```

Kontroluj:

- owner references,
- assigned Node,
- Pod IP,
- phase a conditions,
- init/container statuses,
- restart count,
- image ID,
- requests/limits,
- probes,
- mounts,
- service account,
- security context,
- Events.

## 41. Diagnostika podľa stavu

### `Pending`, bez Node-u

Scheduling, resource, affinity, taint, PVC alebo admission problém.

### `Pending`/`ContainerCreating`, Node pridelený

Image, sandbox/CNI, volume/CSI, Secret/ConfigMap projection alebo runtime problém.

### `Running`, `Ready=False`

Readiness probe, custom readiness gate alebo container readiness problém.

### `CrashLoopBackOff`

Application exit, command, config, permissions, liveness alebo resources.

### `ImagePullBackOff`

Registry, credentials, image reference, platform, network, TLS alebo rate limit.

### `Terminating`

Graceful shutdown, finalizer, kubelet/node reachability, volume detach alebo API deletion flow.

### `Evicted`

Node pressure alebo eviction policy; skontroluj Events a Node conditions.

## 42. Anti-patterny

### Viac nezávislých services v jednom Pode

Nemožno ich samostatne škálovať, rolloutovať a izolovať.

### Pod vytvorený priamo pre produkčnú službu

Chýba controller replacement a rollout model.

### Liveness probe závislá od celej externej infraštruktúry

Spôsobí restart storm počas dependency outage.

### Secret v environment dump alebo annotation

Zvyšuje leakage cez API, logs a debug tooling.

### `latest` tag bez digest a rollout trigger policy

Nodes môžu spustiť odlišný image content.

### `hostNetwork`, `hostPID`, privileged alebo hostPath ako rýchla oprava

Odstraňuje isolation a zväčšuje blast radius.

### Neobmedzené resources

Zhoršuje scheduling, noisy-neighbor behavior a eviction predvídateľnosť.

### Sidecar bez resource/shutdown modelu

Môže blokovať termination alebo vyčerpať Pod capacity.

## 43. Kontrolné otázky

1. Prečo Pod nie je iba synonymum pre container?
2. Ktoré resources containers v Pode zdieľajú?
3. Prečo Kubernetes nepremiestňuje bežiaci Pod na iný Node?
4. Aký je rozdiel medzi init, sidecar a ephemeral containerom?
5. Aký je rozdiel medzi Pod phase, condition a container state?
6. Ako sa líši container restart a Pod replacement?
7. Akú úlohu majú startup, liveness a readiness probes?
8. Čo sa deje pri graceful Pod termination?
9. Prečo priamy Pod nie je bežný produkčný workload model?
10. Ako diagnostikuješ Pod v `ContainerCreating` oproti `CrashLoopBackOff`?

## Glossary impact

Relevantné pojmy: Pod, Pod UID, Pod sandbox, Pod IP, Pod phase, Pod condition, container status, init container, sidecar container, ephemeral container, `emptyDir`, restartPolicy, CrashLoopBackOff, imagePullPolicy, startup probe, liveness probe, readiness probe, Pod readiness gate, lifecycle hook, termination grace period, Pod template, direct Pod, controller-managed Pod, static Pod a mirror Pod.

## Oficiálna dokumentácia

- [Pods](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Init containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)
- [Sidecar containers](https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/)
- [Ephemeral containers](https://kubernetes.io/docs/concepts/workloads/pods/ephemeral-containers/)
- [Container lifecycle hooks](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/)
- [Configure a security context](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)
- [Static Pods](https://kubernetes.io/docs/concepts/workloads/pods/static-pods/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Worker node components](worker-node-components.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: ReplicaSet →](replicaset.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
