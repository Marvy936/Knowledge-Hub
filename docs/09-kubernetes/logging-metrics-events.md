# Logging, metrics a events

Kubernetes observability nie je jeden dashboard ani jeden agent. Logs, metrics, Events, audit records a traces vznikajú na rozdielnych miestach a odpovedajú na rozdielne otázky. Dobrá observability architektúra nezačína výberom produktu, ale otázkou, ktorú potrebujeme zodpovedať: ktorý request zlyhal, ktorý component urobil rozhodnutie, či Node trpel resource pressure, kto zmenil objekt alebo kde sa stratila end-to-end latency.

Pri `payments-api` potrebujeme prepojiť external request ID s Gateway, Service backendom, Pod UID, container ID, Node generation, image digestom, config generation a downstream payment commitom. Ak central log collector nevidí iba novú Node cohortu, chýbajúce dáta sú samostatný observability incident a zároveň komplikujú diagnostiku pôvodného problému.

## Logs odpovedajú, čo konkrétny proces zaznamenal

Container má zapisovať application logs na stdout a stderr. Kubelet a runtime ich ukladajú a sprístupňujú cez Pod log API.

```bash
kubectl logs -n production <pod-name> -c api
kubectl logs -n production <pod-name> -c api --previous
```

`--previous` číta log predchádzajúcej container inštancie v tom istom Pod lifetime, ak je ešte dostupný. Po zániku Podu alebo log rotation nemusia byť lokálne logs dostupné.

Application log má obsahovať bounded, korelovateľné fields:

```json
{
  "timestamp": "2026-08-01T06:15:04.123Z",
  "level": "error",
  "service": "payments-api",
  "request_id": "req-81f2",
  "payment_id": "pay-100",
  "release": "4.2.0",
  "config_generation": "C52",
  "message": "database commit timeout"
}
```

Nemá vypisovať password, bearer token, celý card payload alebo high-cardinality neobmedzené objekty. Redakcia sa má diať pri source-i a znovu na ingest boundary.

## Kubernetes container log lifecycle

Kubelet riadi rotation container logs podľa Node configuration. `kubectl logs` nie je dlhodobý archive. Pri vysokom log volume sa staršie súbory môžu otočiť skôr, než incident začne.

Node log agent typicky sleduje runtime log files, dopĺňa Kubernetes metadata a posiela ich do central backendu:

```text
application stdout/stderr
→ container runtime log file
→ kubelet rotation
→ node collector DaemonSet
→ buffer/queue
→ central ingest
→ index/retention/query
```

Každý šíp môže stratiť alebo oneskoriť dáta. Zelený collector Pod nepreukazuje, že sleduje správnu runtime path, parsuje multiline records alebo úspešne dostáva acknowledgement od backendu.

## Node a component logs

Control-plane a Node components majú vlastné logs. V managed clustri môžu byť dostupné cez provider logging. V self-managed clustri cez journal alebo static Pod logs.

Relevantné sources:

```text
API server
controller-manager a scheduler
etcd
kubelet a container runtime
CNI a CSI agents/controllers
Gateway/Ingress a DNS
autoscalers a admission webhooks
```

Pri incidente nezhromažďuj všetko bez hranice. Vyber component, ktorý vlastní prvý chybný transition, a presný čas/subject.

## Metrics odpovedajú, koľko, ako často a ako dlho

Metrics sú numerické časové rady. V Kubernetes potrebujeme viac vrstiev:

```text
application a business metrics
Pod/container resource metrics
kubelet/runtime/Node metrics
Kubernetes object-state metrics
control-plane component metrics
CNI/CSI/Gateway/DNS metrics
```

`kubectl top` používa resource metrics pipeline a poskytuje CPU/memory sample:

```bash
kubectl top pod -n production -l app=payments-api
kubectl top node
```

Neukazuje CPU throttling, disk inodes, packet loss ani application latency. Na tieto otázky potrebujeme ďalšie metrics.

## Metrics labels a cardinality

Labels umožňujú rozdeliť metric podľa service, namespace, Pod, Node alebo statusu. Nekontrolovaná cardinality však môže preťažiť collector a backend.

Nebezpečný label:

```text
payment_id=<unikátne ID každej transakcie>
```

Každý payment by vytvoril novú time series. Request/payment ID patrí skôr do logu alebo trace-u. Metric môže používať bounded labels ako status class, region alebo release.

Pod name je tiež dynamický. Pre dlhodobé SLO sa agreguje podľa workload/release, pričom Pod UID sa používa pri incidentnom drill-down-e.

## Object-state metrics

Kubernetes object status možno exportovať ako metrics, napríklad desired/ready replicas, Pod phases, PVC status alebo Job completion. Také metrics reprezentujú API state, nie vždy actual runtime alebo business outcome.

```text
Deployment available replicas=6
≠ šesť správne nakonfigurovaných procesov
≠ šesť úspešných payment paths
```

Dashboard má kombinovať controller, runtime a business signals bez ich zlievania.

## Events sú krátkodobé diagnostické správy

Events zaznamenávajú napríklad scheduling failure, image pull error, volume mount alebo probe failure.

```bash
kubectl get events -n production --sort-by=.lastTimestamp
kubectl describe pod -n production <pod-name>
```

Events sú rate-limited, agregované a majú obmedzenú retention. Nie sú audit log ani úplná timeline. Count a first/last timestamp môžu reprezentovať viac opakovaní jednej správy.

Chýbajúci Event nepreukazuje, že operácia prebehla bez chyby. Component mohol zlyhať pred emitovaním alebo event mohol expirovať.

## Audit logs odpovedajú, kto volal API

API audit môže zaznamenať caller identity, verb, resource, namespace, response code a podľa policy request/response metadata.

Použiteľné otázky:

```text
kto zmenil Deployment image?
kto force-delete-ol Pod?
ktorý controller vytvoril LoadBalancer Service?
ktorý client stále používa deprecated API?
```

Audit policy musí vyvažovať detail, objem a citlivosť. Request body pre Secret alebo TokenReview môže obsahovať citlivé dáta a má byť redigovaný alebo používať vhodnú audit level policy.

Audit log potrebuje immutable retention a oddelený access. Ak útočník s cluster-admin môže zmazať aj audit trail, investigation je oslabené.

## Distributed traces

Trace spája request cez viac služieb a network hops. `payments-api` môže prevziať trace context z Gateway a vytvoriť spans pre databázu a external risk provider.

```text
client span
→ Gateway span
→ payments-api span na konkrétnom Pod UID
→ database/risk spans
→ business result
```

Trace sampling musí zachovať dostatok errors a reprezentatívny baseline. Head sampling môže zahodiť zriedkavý failure skôr, než vznikne. Tail sampling potrebuje buffering a správny tenant/security model.

Trace nie je presný audit pre finančný commit, pokiaľ business ledger nie je autoritatívny. Je to latency a causal correlation signal.

## Kubernetes metadata enrichment

Collector môže doplniť namespace, Pod, container, Node, labels a annotations. Enrichment musí používať Pod UID a timestamp, aby nepriradil staré logy novému Podu s podobným menom alebo znovu použitou IP.

Broad metadata ingest môže preniesť secret-bearing annotations alebo high-cardinality labels. Povolené fields sa majú whitelistiť.

## Buffering a backpressure

Keď central backend nie je dostupný, collector môže bufferovať na Node disk alebo v pamäti. Buffer má limit a overflow policy.

```text
backend outage
→ local buffer rastie
→ Node disk pressure
→ collector alebo workloads sú ohrozené
```

Observability nesmie zmeniť monitorovaný incident na Node-wide outage. Buffer paths potrebujú size limits, rotation a priority.

At-least-once delivery môže vytvoriť duplicate log records po retry. Query a alerting majú používať event identity alebo tolerovať duplicates.

## Time synchronization

Korelácia vyžaduje konzistentný čas. Node clock drift môže spôsobiť, že log vyzerá pred requestom alebo audit event po response.

Sleduj time sync health a používaj UTC timestamps s presnosťou. Ingest timestamp a event timestamp sú dve rozdielne hodnoty; oneskorený buffer ich môže oddeliť o minúty.

## Retention

Rôzne signals potrebujú inú retention:

```text
high-volume debug logs → krátka retention
security audit → dlhšia immutable retention
SLO metrics → dostatočné okno pre trendy
traces → sampling a bounded retention
business ledger → podľa regulatory a recovery požiadaviek
```

Retention nie je iba cost parameter. Príliš krátke okno znemožní vyšetrovanie incidentu objaveného neskôr. Príliš dlhé plaintext logs zvyšujú privacy a breach impact.

## Alerts podľa používateľského outcome-u

Alert iba na `Pod NotReady` môže byť hlučný pri bežnom rollout-e a slepý pri green-but-broken aplikácii. Lepší model kombinuje:

```text
payment success/error rate a latency
+ ready serving capacity
+ dependency health
+ saturation/throttling
+ rollout alebo Node generation
+ telemetry coverage
```

Alert má smerovať k rozhodnutiu. „CPU > 80 %“ bez trvania, workload baseline a SLO nemusí znamenať incident.

## Telemetry coverage ako vlastný signal

Chýbajúce logs alebo metrics sa nesmú interpretovať ako nulové chyby. Potrebujeme expected source inventory:

```text
počet eligible Nodes
→ počet collector Pods
→ počet aktívnych source streams
→ posledný ingest timestamp per Node/workload
```

Coverage SLO môže upozorniť, že nová Node cohorta neposiela logs alebo metrics, ešte pred aplikačným incidentom.

## Praktická korelácia jedného requestu

Začneme external request ID `req-81f2` a timestampom:

```bash
kubectl get pods -n production -l app=payments-api -o wide
kubectl get endpointslices -n production \
  -l kubernetes.io/service-name=payments-api -o yaml
```

Z edge logu zistíme backend Pod IP. Cez EndpointSlice targetRef priradíme Pod UID. Z Pod statusu získame Node, imageID a restart state. Logs a trace ukážu config generation a downstream call. Metrics ukážu CPU throttling alebo latency. Audit log ukáže prípadnú nedávnu config mutation.

Každý signal dopĺňa inú časť príbehu. Jeden stack trace bez Pod/Node/release identity nestačí.

## Incident: nová Node generation nemala central logs

Po upgrade-e približne 20 % payment requests zlyhávalo iba na nových Nodes. Central log query neukázala žiadne errors z affected cohorty. `kubectl logs` však lokálne logy zobrazil.

Collector DaemonSet bol `Ready` na všetkých Nodes, ale nová runtime konfigurácia používala inú log path. Collector sledoval starý adresár a neotvoril žiadne source files. Chýbajúce logs neboli root cause payment failure; boli samostatným coverage failure, ktorý diagnózu spomalil.

Oprava zladila collector config a pridala per-Node source coverage metric do Node admission gate-u. Payment root cause sa následne našiel v CNI dataplane prerequisite.

## Incident: metric cardinality vyradila monitoring

Nová release pridala `payment_id` ako Prometheus label. Počet series narástol o milióny, scraper a backend začali padať a alerty mali gaps. Aplikácia samotná bola zdravá.

Containment zakázalo problematický metric endpoint/filter. Oprava presunula payment ID do traces/logs a metric ponechala iba bounded status labels. Release gate pridal cardinality budget.

## Incident: Events expirovali pred vyšetrovaním

Nightly Job zlyhával o druhej ráno. Incident sa začal riešiť o desať hodín neskôr a relevantné aggregated Events už neboli dostupné. Pod bol odstránený TTL controllerom.

Central logs neobsahovali Pod UID a Job attempt identity, takže dôkaz bol neúplný. Oprava predĺžila failed Job history/TTL, zlepšila log metadata a vytvorila alert pri prvom failed completion.

## Incident: audit pipeline logovala Secret body

Audit policy nastavila vysoký level pre všetky core resources vrátane Secrets. Request body sa dostával do shared log backendu. RBAC pre cluster Secret bol úzky, ale observability backend mal širší okruh čitateľov.

Incident vyžadoval credential rotation, redakciu a audit policy zmenu. Observability pipeline sa stala secret exfiltration path. Skorší control je resource-aware audit level a data classification.

## Model, ktorý si treba odniesť

Logs opisujú process events, metrics merajú časové rady, Events sumarizujú Kubernetes lifecycle, audit zachytáva API actions a traces spájajú request path. Žiadny signal nie je kompletný. Produkčná observability potrebuje identity, čas, coverage, redakciu, cardinality, buffering a retention contracts. Chýbajúce telemetry je vlastný failure state, nie dôkaz zdravia.

## Referencie

- [Logging Architecture](https://kubernetes.io/docs/concepts/cluster-administration/logging/)
- [Resource Metrics Pipeline](https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/)
- [Kubernetes Events](https://kubernetes.io/docs/reference/kubernetes-api/cluster-resources/event-v1/)
- [Auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Upgrades](upgrades.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Praktický Kubernetes projekt od manifestov po overený rollout →](kubernetes-practical-walkthrough.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
