# Probes

Kubernetes probes dávajú kubeletu tri odlišné signály o containeri. Startup probe chráni pomalú inicializáciu. Liveness probe rozhoduje, či má kubelet container reštartovať. Readiness probe rozhoduje, či má Pod prijímať traffic. Ak tieto otázky zlejeme do jedného endpointu bez premysleného contractu, môžeme vytvoriť restart storm, odpojiť celý fleet pri shared dependency incidente alebo pustiť traffic na aplikáciu, ktorá ešte nie je pripravená.

Pre `payments-api` používame `/healthz` ako veľmi plytký process-health endpoint a `/readyz` ako readiness kontrolu loaded configuration a kritickej lokálnej inicializácie. Business correctness overuje samostatný syntetický payment request, nie kubelet probe každých päť sekúnd.

## HTTP probe

```yaml
readinessProbe:
  httpGet:
    path: /readyz
    port: http
    scheme: HTTP
  periodSeconds: 5
  timeoutSeconds: 2
  failureThreshold: 3
  successThreshold: 1
```

Kubelet posiela request z Node contextu na Pod IP a port podľa probe semantics. Nejde cez Service, Gateway ani external DNS. Zelená HTTP readiness preto nepreukazuje celý používateľský path.

Named port znižuje coupling na numeric port:

```yaml
ports:
  - name: http
    containerPort: 8080
```

Ak application počúva iba na `127.0.0.1`, probe na Pod IP môže zlyhať, hoci process odpovedá vo vlastnom loopbacku.

## TCP probe

```yaml
livenessProbe:
  tcpSocket:
    port: http
```

TCP probe overí, že sa dá otvoriť connection. Neoverí protokol, loaded config ani dependency. Service, ktorá akceptuje socket a okamžite vracia 500, môže mať zelenú TCP probe.

TCP probe je vhodná iba vtedy, keď otvorený listener skutočne odpovedá na požadovanú liveness otázku.

## Exec probe

```yaml
livenessProbe:
  exec:
    command:
      - /usr/local/bin/payments-api
      - healthcheck
```

Exec probe spustí process v containeri. Je užitočná pre distroless image s vlastným health subcommandom alebo pre kontrolu lokálneho Unix socketu. Každé spustenie však spotrebúva CPU, memory a PID. Drahý shell script môže sám vytvoriť pressure.

Probe command nesmie vypisovať secrets ani vykonávať ne-idempotentný side effect.

## gRPC probe

Kubernetes podporuje gRPC health probing podľa API contractu. Aplikácia musí implementovať gRPC health checking protocol a probe používa numeric port podľa podporovaných fields.

Pri použití over konkrétnu Kubernetes verziu a obmedzenia. HTTP a gRPC probes nie sú zameniteľné iba zmenou scheme.

## Startup probe

Pomalá Java alebo data-initialization aplikácia môže potrebovať desiatky sekúnd, kým je schopná reagovať. Ak liveness začne príliš skoro, kubelet container reštartuje ešte pred dokončením startupu.

```yaml
startupProbe:
  httpGet:
    path: /healthz
    port: http
  periodSeconds: 2
  failureThreshold: 30
```

Tento contract dáva približne 60 sekúnd podľa period/failure semantics. Kým startup probe neuspeje, liveness a readiness sa neaplikujú podľa probe lifecycle-u.

Startup probe nie je bezodný timeout. Ak aplikácia potrebuje čoraz dlhší štart pre narastajúce dáta, treba opraviť startup model alebo kapacitu, nie len neustále zvyšovať failure threshold.

## Liveness probe

Liveness má odpovedať: je process v stave, z ktorého sa bez reštartu pravdepodobne neobnoví?

Dobrá liveness býva lokálna a stabilná. Nemá priamo závisieť od databázy, DNS alebo external provideru, ak reštart containeru tieto dependencies neopraví.

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: http
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3
```

Ak databáza vypadne a liveness ju kontroluje, všetky Pods sa môžu naraz reštartovať. Tým sa zvýši load na runtime, DNS, image filesystem a databázu pri obnove.

## Readiness probe

Readiness má odpovedať: smie tento Pod teraz prijímať nový traffic?

Pre `payments-api` môže kontrolovať:

```text
process dokončil startup
+ loaded config generation je validná
+ worker queue prijíma prácu
+ local resource pressure nie je kritická
+ critical dependency path je dostupná v rozumnom, plytkom rozsahu
```

Readiness failure odstráni Pod z ready Service endpoints podľa controller convergence. Process zostáva bežať a môže sa zotaviť bez restartu.

Ak readiness kontroluje shared database príliš agresívne, krátky database incident môže odpojiť všetky Pods a vytvoriť úplnú nedostupnosť aj pre endpointy, ktoré databázu nepotrebujú. Dependency design musí zohľadniť degraded modes.

## Business check nepatrí do každej probe

Payment POST môže mať external side effect a nemá sa vykonávať ako readiness probe. Business synthetics patria do rollout verification alebo monitoring-u s explicitným test accountom a idempotency.

```text
kubelet readiness
→ lacný per-Pod serving signal

release synthetic
→ end-to-end Service/edge/business outcome
```

Zelená readiness je nutná pre traffic eligibility, nie dostatočná pre release acceptance.

## Timing parameters

Probe timing vzniká kombináciou:

```text
initialDelaySeconds
periodSeconds
timeoutSeconds
failureThreshold
successThreshold
```

`initialDelaySeconds` sa pri startup probe interpretuje v kontexte probe lifecycle-u; často je čitateľnejšie nechať startup budget riadiť startup probe.

Readiness môže mať `successThreshold > 1`, aby sa Pod nevrátil do trafficu po jednom náhodnom úspechu. Liveness success threshold má obmedzené semantics podľa API contractu.

Timeout musí byť kratší než period a zodpovedať Node/app latency. Príliš nízky timeout vytvára false failures pri CPU throttlingu. Príliš vysoký odkladá detection.

## Probe load

Šesť Podov s troma HTTP probes každé dve sekundy môže vytvoriť významný QPS. Pri stovkách replík sa probes stávajú vlastným traffic source-om.

Endpoint má byť lacný, bounded a bez high-cardinality logovania. Logovanie každého probe requestu na info level môže zahltiť pipeline a disk.

## Readiness gates

Pod readiness gates pridávajú custom Pod conditions:

```yaml
readinessGates:
  - conditionType: atlas.example/edge-registered
```

Kubelet môže mať všetky containers Ready, ale Pod zostane NotReady, kým external controller nezapíše condition `True`.

Custom controller musí condition viazať na Pod UID a generation. Ak zapíše starý result na nový Pod s podobným menom, môže pustiť traffic pred registráciou.

## Conditions a EndpointSlice

```bash
kubectl get pod -n production <pod-name> \
  -o jsonpath='{range .status.conditions[*]}{.type}{"="}{.status}{" reason="}{.reason}{"\n"}{end}'

kubectl get endpointslices -n production \
  -l kubernetes.io/service-name=payments-api -o yaml
```

Pod `Ready=True` a endpoint `ready=true` sú blízke, ale aktualizácia nie je jedna okamžitá transakcia. Pri termination alebo rýchlom flappingu môže existovať krátke convergence okno.

## Probe failures a logs

`kubectl describe pod` ukazuje probe Events, ale Events sú agregované a rate-limited. Application logs a kubelet logs môžu ukázať presný timeout alebo response.

```bash
kubectl describe pod -n production <pod-name>
kubectl logs -n production <pod-name> -c api
kubectl logs -n production <pod-name> -c api --previous
```

Previous logs sú dôležité po liveness restart-e.

## Probes a graceful termination

Pri termination má application readiness prejsť na false skôr, než ukončí listener, aby nové requests prestali prichádzať. Kubelet a EndpointSlice convergence však nie sú okamžité.

Aplikácia má zároveň reagovať na SIGTERM a dokončiť in-flight requesty v grace period. `preStop` sleep používaný ako jediný drain mechanizmus je krehký; potrebuje meranie reálneho propagation času a connection lifecycle-u.

## Incident: liveness spôsobila cluster-wide restart storm

Liveness endpoint kontroloval databázové `SELECT 1`. Databáza mala 30-sekundový failover. Všetky Pods po troch zlyhaniach reštartovali. Pri štarte vytvorili nové connection pools a zvýšili load na obnovujúcu sa databázu.

Oprava odstránila shared dependency z liveness. Readiness naďalej signalizovala neschopnosť obslúžiť payment path, ale process ostal bežať a connection pools sa obnovili bez fleet restartu.

## Incident: readiness bola zelená pred načítaním novej konfigurácie

Aplikácia otvorila HTTP listener a `/readyz` vracala 200 ešte pred dokončením asynchronous config loadu. Deployment začal scale-downovať staré Pods. Prvé requesty na nové Pods používali default staging endpoint.

Oprava zaviedla internal startup state machine. Readiness sa stala green až po validácii config generation a dependency targetu. Release test navyše overil `/version` cez Service.

## Incident: CPU throttling vyzeral ako liveness failure

Probe timeout bol 100 ms a container mal nízky CPU limit. Pri traffic burstoch health handler nedostal CPU včas, liveness zlyhala a kubelet process reštartoval. Restart zhoršil cache warmup a latency.

Root cause bol resource/probe contract. Oprava zvýšila timeout, upravila CPU limit a sledovala cgroup throttling. Health handler zostal lacný, ale dostal realistický execution budget.

## Incident: readiness odpojila všetky repliky pri DNS incidente

Readiness vykonávala lookup troch optional partner endpoints. Výpadok cluster DNS spôsobil `Ready=False` na všetkých Pods, vrátane interných payment read endpointov, ktoré partnerov nepotrebovali.

Oprava rozdelila critical a optional dependencies a zaviedla degraded behavior. Readiness ostala viazaná iba na serving contract konkrétnej služby.

## Model, ktorý si treba odniesť

Startup, liveness a readiness odpovedajú na rozdielne otázky. Startup chráni inicializáciu, liveness opravuje neobnoviteľný process state reštartom a readiness riadi traffic eligibility. Probe endpoint musí byť lacný, bezpečný a zodpovedať tomu, čo kubelet dokáže svojou reakciou skutočne opraviť. Business acceptance patrí do samostatného end-to-end testu.

## Referencie

- [Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Requests, limits a QoS](requests-limits-qos.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Taints, tolerations, affinity a topology →](taints-tolerations-affinity-topology.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
