# Pod

Pod je najmenšia Kubernetes runtime jednotka, ktorú scheduler pridelí jednému Node-u. Nie je to synonymum containeru ani malá virtuálna mašina. Pod môže obsahovať jeden alebo viac containers, ale všetky zdieľajú spoločnú Pod identitu, placement, network namespace a replacement lifecycle. Keď Pod zanikne, controller typicky vytvorí nový Pod s novým UID; neopravuje pôvodnú runtime inštanciu na mieste.

Pri `payments-api` bude jeden Pod predstavovať jednu aplikačnú repliku. Deployment generation 12 vytvorí ReplicaSet a ten vytvorí Pod s konkrétnym UID, image digestom, configuration generation `C52` a service accountom `payments-api`. Práve Pod spája deklarovaný template so skutočným Node runtime-om.

## Pod nie je iba zoznam containers

Zjednodušený manifest:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: payments-api-example
  namespace: production
  labels:
    app: payments-api
spec:
  serviceAccountName: payments-api
  containers:
    - name: api
      image: registry.example.com/atlas/payments-api@sha256:payments420
      ports:
        - name: http
          containerPort: 8080
```

`containers` sú iba časť Pod specu. Pod zároveň definuje volumes, init containers, scheduling constraints, restart policy, security context, DNS policy, termination grace period a probe contract.

Containers v jednom Pode zdieľajú Pod IP a port namespace. Ak sidecar počúva na `localhost:15000`, hlavný container sa k nemu môže pripojiť cez loopback. Dva containers však nemôžu bindovať rovnaký port na rovnakej adrese.

Spoločné umiestnenie dáva zmysel iba pri silnom coupling-u. Dve nezávislé business služby s odlišným scalingom a rolloutom patria do samostatných Podov.

## Pod identity a replacement

Presná identita Podu zahŕňa cluster, namespace, meno a `metadata.uid`.

```bash
kubectl get pod -n production <pod-name> \
  -o custom-columns='NAME:.metadata.name,UID:.metadata.uid,NODE:.spec.nodeName,IP:.status.podIP'
```

Controller replacement vytvorí nový UID, nový sandbox, nové container IDs a často novú IP. Meno môže byť podobné, ale runtime lifetime je nový.

To má praktické dôsledky. `emptyDir` dáta zaniknú s Pod UID. Writable layer containeru zanikne s containerom. In-memory connections, process state a lokálne caches sa nevynesú do replacementu. Durable state musí mať explicitného vlastníka mimo tejto runtime inštancie.

## Pod template je snapshot

Deployment vytvára Pods zo svojej `.spec.template`. Keď sa template zmení, existujúci Pod sa bežne neprepíše. Vznikne nový ReplicaSet a nové Pods.

```text
Deployment template T12
→ Pod UID P12-A

Deployment template T13
→ nový ReplicaSet
→ Pod UID P13-A
```

Environment variables z ConfigMap alebo Secretu sú snapshot pri container start-e. Zmena source objektu nemení environment už bežiaceho procesu. Mounted projected files sa môžu časom aktualizovať, ale aplikácia ich nemusí automaticky reloadnúť.

Ručná úprava súboru v containeri nevytvára novú Pod template ani auditovateľný release. Pri replacement-e sa stratí.

## Ako Pod vzniká

Po vytvorení Pod objektu scheduler vyberie Node. Kubelet na danom Node-e potom pripraví runtime:

```text
Pod admitted v API
→ scheduler doplní nodeName
→ kubelet pripraví volumes a projected data
→ runtime vytvorí sandbox
→ CNI pridá network a Pod IP
→ runtime stiahne image
→ init containers
→ application containers
→ probes a status
```

Pri troubleshootingu sa oplatí určiť prvý chýbajúci krok. Pod bez Node assignmentu je scheduling problém. Pod s `FailedCreatePodSandBox` ešte nemá funkčný network sandbox. `ErrImagePull` vzniká pred application processom. `Running` s `Ready=False` už presúva pozornosť k probes, dependencies alebo aplikácii.

## Pod phase a conditions

Pod phase je hrubá kategória ako `Pending`, `Running`, `Succeeded`, `Failed` alebo `Unknown`. Nie je to kompletný health model.

```bash
kubectl get pod -n production <pod-name> -o yaml
```

Dôležitejšie sú conditions a container statuses. Pod môže mať phase `Running`, ale condition `Ready=False`. Container môže byť v stave `Waiting` s reason `CrashLoopBackOff`, hoci Pod object stále existuje.

```bash
kubectl get pod -n production <pod-name> \
  -o jsonpath='{range .status.conditions[*]}{.type}{"="}{.status}{" reason="}{.reason}{"\n"}{end}'

kubectl get pod -n production <pod-name> \
  -o jsonpath='{.status.containerStatuses}' | jq .
```

`restartCount` sa vzťahuje na container v jednom Pod lifetime. Po replacement-e novým Pod UID sa počítadlo začne odznova.

## Init containers

Init containers bežia pred bežnými application containers a dokončujú sa postupne. Sú vhodné na lokálnu prípravu volume-u, validáciu konfigurácie alebo získanie immutable artifactu.

```yaml
initContainers:
  - name: validate-config
    image: registry.example.com/atlas/config-validator@sha256:validator7
    args:
      - /config/application.yaml
    volumeMounts:
      - name: config
        mountPath: /config
```

Init container nie je vhodné miesto pre ne-idempotentnú globálnu databázovú migráciu bez coordination. Pod replacement môže init krok zopakovať. Ak sa po partial side effectu vytvorí marker príliš skoro, ďalší pokus môže nesprávne preskočiť nedokončenú operáciu.

Pri zaseknutom Pode čítaj `status.initContainerStatuses` oddelene od hlavného containeru.

## Sidecars a spoločný lifecycle

Sidecar môže poskytovať proxy, log forwarding alebo lokálnu pomocnú funkciu. Jeho failure však ovplyvňuje celý Pod outcome. Ak proxy sidecar nie je ready, hlavná aplikácia môže byť zdravá na localhoste, ale Service traffic nebude fungovať.

Kubernetes podporuje sidecar lifecycle modely podľa API a cluster verzie. Pri návrhu vždy over konkrétny contract init/sidecar semantics v cieľovej verzii. Dôležité je, aby startup a termination poradie zodpovedali dependency medzi containers.

## Volumes v Pode

Pod deklaruje volumes a jednotlivé containers si ich mountujú.

```yaml
volumes:
  - name: config
    configMap:
      name: payments-api-config
  - name: work
    emptyDir:
      sizeLimit: 256Mi
```

`emptyDir` prežije restart containeru v tom istom Pode, ale neprežije zánik Pod UID. PVC-backed volume môže prežiť replacement, ak storage a access mode umožnia nové pripojenie. Projected Secret alebo ConfigMap prináša bytes z API source-u, nie automaticky process-loaded state.

Mount môže zakryť obsah image-u na rovnakom path-e. Ak image obsahoval `/app/defaults`, ale volume sa mountne na `/app`, pôvodné súbory v runtime pohľade zmiznú.

## Environment a loaded configuration

Source objekt, Pod spec a application-loaded hodnota sú tri vrstvy.

```text
Secret SE09 existuje
→ Pod template stále odkazuje na starý checksum
→ starý Pod používa environment zo SE08
→ nový Pod môže dostať SE09
→ application ešte musí úspešne otvoriť connection
```

Aplikácia by mala vedieť bezpečne publikovať configuration generation bez odhalenia secretu, napríklad cez `/version` alebo metrics label s bounded cardinality.

## Resource requests a limits

Pod template definuje resources pre každý container. Scheduler používa requests pri placement-e. Runtime a kernel uplatňujú limits.

```yaml
resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: "1"
    memory: 512Mi
```

Pod môže byť schedulovaný podľa requests a neskôr CPU throttled alebo OOM-killed pri limite. `Running` neznamená, že resource contract stačí na SLO.

## Probes a readiness

Startup probe chráni pomalý štart pred liveness zásahom. Liveness rozhoduje, či kubelet reštartuje container. Readiness rozhoduje, či je Pod pripravený prijímať traffic.

```yaml
startupProbe:
  httpGet:
    path: /healthz
    port: http
  failureThreshold: 30
  periodSeconds: 2

readinessProbe:
  httpGet:
    path: /readyz
    port: http
  periodSeconds: 5

livenessProbe:
  httpGet:
    path: /healthz
    port: http
  periodSeconds: 10
```

Readiness endpoint pre `payments-api` kontroluje, či aplikácia načítala config a môže používať kritickú dependency v rozsahu navrhnutom pre probe. Nemá vykonávať drahú payment transakciu pri každom probe ticku.

Zelená readiness stále nemusí dokazovať business správnosť. Preto rollout potrebuje aj syntetický request cez Service alebo edge path.

## Readiness gates

Pod môže mať custom readiness gates. Externý controller potom zapisuje condition, napríklad až po registrácii v externom load balanceri.

```yaml
readinessGates:
  - conditionType: atlas.example/lb-registered
```

Pod je Ready až keď sú splnené bežné container readiness aj custom condition. Ak controller prestane condition aktualizovať, Pods môžu zostať NotReady napriek zdravej aplikácii. Gate preto potrebuje jasného ownera a recovery model.

## Restart a replacement nie sú to isté

Pri liveness failure môže kubelet reštartovať container v rovnakom Pod UID. Network namespace a volumes Podu môžu zostať. Pri Node loss alebo rollout-e controller vytvorí nový Pod UID.

```text
container restart
→ rovnaký Pod UID
→ nový container ID

Pod replacement
→ nový Pod UID
→ nový sandbox, IP a container IDs
```

Pri incident review treba presne pomenovať, ktorý typ zmeny nastal.

## Graceful termination

Pri delete alebo rollout scale-down dostane Pod `deletionTimestamp`. Endpoint eligibility sa mení a kubelet spustí termination sequence. Application process dostane signal podľa runtime a image contractu a má čas v rámci `terminationGracePeriodSeconds`.

```yaml
terminationGracePeriodSeconds: 45
```

Aplikácia má prestať prijímať nové requesty, dokončiť alebo bezpečne prerušiť in-flight operácie a uzavrieť connections. `preStop` hook môže pomôcť, ale jeho trvanie sa započítava do rovnakého grace budgetu.

```bash
kubectl delete pod -n production <pod-name> --wait=false
kubectl get pod -n production <pod-name> -w
```

Force delete odstraňuje API objekt bez čakania na potvrdený Node cleanup a môže vytvoriť dve súčasné inštancie pri partitioned Node-e. Pri stateful alebo external writer workload-e je potrebné fencing.

## Ephemeral containers pre debugging

Ephemeral container možno pridať na diagnostiku bežiaceho Podu, keď production image nemá shell alebo nástroje.

```bash
kubectl debug -n production -it <pod-name> \
  --image=busybox:1.36 --target=api
```

Debug container nemení pôvodný image ani template. Má vlastné security a audit riziká. Nemá sa používať ako trvalá oprava alebo cesta na inštaláciu balíkov do production runtime-u.

## Incident: Pod je Running, ale payment traffic zlyháva

Pod mal phase `Running` a hlavný process počúval. Readiness však bola `False`, pretože aplikácia načítala config `C52`, ale Secret volume ešte obsahoval starú credential generation, ktorú databáza už zrušila.

```bash
kubectl describe pod -n production <pod-name>
kubectl logs -n production <pod-name> -c api
kubectl get pod -n production <pod-name> -o yaml
```

Service správne Pod nevložila do ready endpointov. Oprava nebola „vypnúť readiness“. Tím zladil secret rollout: nový Secret, checksum v Pod template, controlled Deployment rollout, loaded epoch read-back a až potom revokácia starej credential generation.

## Incident: container restart vyzeral ako nový release

Dashboard agregoval iba Pod name prefix a image tag. Container v tom istom Pod UID sa po OOM reštartoval, ale tag medzitým ukazoval na nový digest v registry. Tím nesprávne predpokladal, že nový artifact bol nasadený.

Runtime používal pôvodný resolved digest. Root cause bol memory limit a burst, nie release. Skorší control je digest-pinned image, Pod UID/container ID korelácia a cgroup/OOM evidence.

## Model, ktorý si treba odniesť

Pod je jedna plánovateľná a nahraditeľná runtime replika. Spája template snapshot, Node placement, sandbox, network, volumes, containers, probes, security a termination. Pri diagnostike odlišuj Pod UID od mena, container restart od Pod replacementu, process state od readiness a API source konfigurácie od hodnôt skutočne načítaných aplikáciou.

## Referencie

- [Pods](https://kubernetes.io/docs/concepts/workloads/pods/)
- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)
- [Init Containers](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/)
- [Container Lifecycle Hooks](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/)
- [Debugging Running Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-running-pod/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Worker node components](worker-node-components.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: ReplicaSet →](replicaset.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
