# Logging, metrics a events

Kubernetes neposkytuje jeden kompletný observability backend. Platforma produkuje logs, metrics, Events, audit records a API status, ale ich dlhodobé uloženie, korelácia, alerting a vizualizácia vyžadujú samostatné components. Každý signál odpovedá na inú otázku a má odlišnú retenciu, cardinality a failure boundary.

## 1. Signály

### Logs

Chronologické textové alebo štruktúrované záznamy z applications, containers, Nodes a control-plane components.

### Metrics

Číselné time series vhodné na trendy, alerting, capacity a SLI výpočty.

### Events

Kubernetes API objekty reprezentujúce významné pozorovania controllerov, scheduleru, kubeletu a ďalších components. Sú diagnostické a krátkodobé, nie audit log ani business event store.

### Traces

Distribuované request spans s causality a latency contextom. Kubernetes ich automaticky nevytvorí pre application requests bez instrumentation.

### Audit logs

Bezpečnostný záznam Kubernetes API requests podľa audit policy. Odpovedá na otázku kto, čo, kedy a s akým výsledkom požadoval od API servera.

## 2. Container logging model

Odporúčaný application model:

```text
application
→ stdout/stderr
→ container runtime CRI log file
→ kubelet log access
→ node log agent
→ central backend
```

Application nemá závisieť od ručného čítania writable layer. Logs potrebujú lifecycle oddelený od Podu a Node-u.

## 3. `kubectl logs`

```bash
kubectl logs -n production pod-name -c app
kubectl logs -n production pod-name -c app --previous
kubectl logs -n production deployment/web --all-pods=true
```

`kubectl logs` číta container logs dostupné cez kubelet/runtime na konkrétnom Node-e.

Limity:

- Node alebo log file môže byť nedostupný,
- rotation mohla odstrániť staré dáta,
- zmazaný Pod nemusí mať logs,
- `--previous` typicky vidí iba predchádzajúcu container instance,
- nie je to central search ani compliance archive.

## 4. CRI log format

Container runtime zapisuje stdout/stderr do Node-local files podľa CRI logging convention. Záznam obsahuje napríklad:

- timestamp,
- stream `stdout` alebo `stderr`,
- full/partial marker,
- payload.

Multi-line stack trace môže byť rozdelený na viac records. Log collector musí správne pracovať s partial lines a application multiline semantics.

## 5. Log rotation

Kubelet/runtime spravujú Node-local container log rotation podľa konfigurácie.

Sleduj:

- maximum file size,
- počet files,
- scan/rotation interval,
- disk a inode pressure,
- collector schopnosť sledovať rename/truncate.

Príliš malá retencia odstráni incident evidence skôr, než collector obnoví spojenie. Príliš veľká retencia môže zaplniť Node disk.

## 6. Cluster-level logging

Bežné architektúry:

### Node agent

DaemonSet ako Fluent Bit, Vector alebo iný collector číta Node/container logs a odosiela ich do backendu.

Výhody:

- jeden agent na Node,
- zachytí viac workloadov,
- lifecycle oddelený od application Podu.

### Sidecar collector

Sidecar číta application-specific file alebo stream.

Použi iba pri špecifickom formáte/protokole. Zvyšuje resource overhead, configuration duplicitu a failure surface.

### Application direct shipping

Application posiela logs priamo do backendu.

Riziká:

- application coupling,
- credentials v každom workload-e,
- blocking/backpressure,
- zložitejšia platform governance.

## 7. Structured logging

Preferuj štruktúrovaný JSON alebo stabilný key/value formát s fields:

- timestamp v UTC,
- severity,
- service a environment,
- namespace/Pod/container enrichment,
- request/trace/correlation ID,
- error type a stack,
- release/version,
- bounded business identifiers.

Nevkladaj:

- passwords/tokens,
- celé request bodies bez redakcie,
- private keys,
- nekontrolovanú high-cardinality payload,
- osobné údaje bez retention a access policy.

## 8. Log metadata enrichment

Node collector môže doplniť:

- cluster,
- namespace,
- Pod name/UID,
- container,
- Node,
- labels a annotations,
- workload owner,
- image a restart count.

Nekopíruj všetky labels automaticky. Dynamic alebo user-controlled labels môžu vytvoriť vysokú cardinality, storage cost a injection risk.

## 9. System component logs

Control-plane a Node components môžu logovať cez:

- systemd journal,
- container/static Pod files pod `/var/log`,
- provider-managed logging service,
- vendor-specific backend.

Príklady:

```bash
journalctl -u kubelet
journalctl -u containerd
crictl ps -a
crictl logs <container-id>
```

Pri static Pods rozlišuj kubelet/service logs od samotných component container logs.

Kubernetes system log message format nie je stabilné API. Parser nemá závisieť od konkrétneho textu bez version kontroly.

## 10. Metrics categories

### Resource metrics

CPU a memory usage Podov a Nodes, typicky poskytované Metrics API cez metrics-server.

Používa ich napríklad:

```bash
kubectl top nodes
kubectl top pods -A
```

Metrics-server nie je dlhodobý monitoring backend.

### Component metrics

Kube-apiserver, scheduler, controller-manager, kubelet, etcd a ďalšie components expose-ujú Prometheus-style `/metrics` podľa konfigurácie a authorization.

### Object-state metrics

Kube-state-metrics prekladá Kubernetes API object status/spec do metrics, napríklad:

- desired/available replicas,
- Pod phases,
- HPA conditions,
- PV/PVC status,
- Node conditions.

Nečíta process CPU alebo application latency.

### Application metrics

Workload-specific request rate, errors, latency, queues a business signals.

## 11. Resource Metrics Pipeline

Zjednodušene:

```text
kubelet/cAdvisor summary
→ metrics-server
→ metrics.k8s.io API
→ kubectl top / HPA resource metrics
```

Failure môže byť v:

- kubelet authentication/TLS,
- Node reachability,
- API aggregation,
- APIService availability,
- metrics-server resources,
- clock skew,
- missing requests pre HPA utilization.

## 12. Metrics API vrstvy

Rozlišuj:

- `metrics.k8s.io` — resource metrics,
- `custom.metrics.k8s.io` — custom metrics via adapter,
- `external.metrics.k8s.io` — metrics mimo Kubernetes object modelu.

API adapter je control dependency pre HPA. Stale alebo chýbajúce metrics musia mať jasný scaling failure model.

## 13. Prometheus-style scraping

Scraper potrebuje:

- target discovery,
- authentication a TLS,
- RBAC pre protected endpoints,
- scrape interval a timeout,
- relabeling a cardinality controls,
- retention a remote storage,
- HA/deduplication podľa požiadaviek.

ServiceMonitor/PodMonitor sú operator-specific CRDs, nie core Kubernetes API.

## 14. Component metrics stability

Kubernetes metrics môžu byť:

- alpha,
- beta,
- stable.

Stability ovplyvňuje deprecation a removal policy. Pred upgrade kontroluj:

- removed/renamed metrics,
- label changes,
- histogram bucket changes,
- hidden metrics flags,
- dashboard a alert dependencies.

Alert založený na nestabilnej metric potrebuje version-aware migration.

## 15. Cardinality

Time-series cardinality rastie kombináciou label values.

Rizikové labels:

- Pod UID/name pri krátko žijúcich Jobs,
- request ID,
- user/account ID,
- URL s dynamickým path segmentom,
- error message,
- image digest v každom series,
- arbitrary annotations.

Dôsledky:

- vysoká memory a storage spotreba,
- pomalé queries,
- drahé remote write,
- nestabilný monitoring backend.

Používaj bounded labels a high-cardinality detail presuň do logs/traces.

## 16. Kubernetes Events

```bash
kubectl get events -A --sort-by=.metadata.creationTimestamp
kubectl describe pod -n production <pod>
```

Event obsahuje napríklad:

- involved/regarding object,
- reason,
- type `Normal` alebo `Warning`,
- message/note,
- reporting controller/instance,
- timestamps a occurrence count/series.

Events môžu byť agregované, rate-limited a po krátkej retencii odstránené.

## 17. Events nie sú audit trail

Event:

```text
FailedScheduling: 0/5 nodes are available...
```

je diagnostické pozorovanie scheduleru.

Audit log zaznamenáva napríklad:

```text
user X požiadal UPDATE deployments/scale a API server odpovedal 200
```

Business event je napríklad:

```text
order 123 bol zaplatený
```

Tieto tri typy sa nesmú zamieňať.

## 18. Event export

Ak potrebuješ dlhodobejšiu históriu, exportuj Events do central backendu.

Zohľadni:

- duplicate/series behavior,
- object UID a namespace,
- short-lived Jobs,
- retention a search,
- sensitive messages,
- rate limits,
- cluster a version metadata.

Event exportér nesmie spôsobiť API overload cez neefektívny polling.

## 19. Audit logging

API server audit policy určuje, ktoré requests a na akej úrovni zaznamenať:

- Metadata,
- Request,
- RequestResponse podľa policy a rizika.

Audit records môžu obsahovať citlivé dáta. Potrebujú:

- secure backend,
- redaction/policy,
- restricted access,
- integrity a retention,
- časovú synchronizáciu,
- alerting na privilege changes a denied requests.

Full RequestResponse pre Secrets môže vytvoriť závažný disclosure risk.

## 20. Correlation

Incident analyzuj cez spoločné identifiers:

- cluster,
- namespace,
- object UID,
- Pod UID,
- Node,
- container ID,
- request/trace ID,
- deployment revision/image digest,
- timestamp.

Pod name sa môže opakovať pri StatefulSet identity alebo meniť pri Deploymente. UID presne odlišuje object instance.

## 21. Time synchronization

Bez synchronizovaného času:

- logs sa zle zoradia,
- token/certificate validity môže zlyhať,
- trace spans majú nesprávnu latency,
- audit correlation je nepresná,
- etcd a distributed systems diagnostika je ťažšia.

Monitoruj NTP/chrony offset na Nodes a observability backend hosts.

## 22. Retention model

Definuj samostatne:

- Node-local container logs,
- central application logs,
- control-plane logs,
- audit logs,
- metrics high-resolution a downsampled data,
- Events,
- traces.

Retention vychádza z:

- incident detection delay,
- compliance,
- capacity/cost,
- forensic požiadaviek,
- RTO a postmortem procesu.

## 23. Security

Observability pipeline má často široký read access.

Chráň:

- log collector ServiceAccounts,
- host `/var/log` mounts,
- kubelet/API metrics credentials,
- central backend write tokens,
- tenant isolation,
- query access a exports,
- secret redaction,
- audit log integrity.

Monitoring stack nie je automaticky dôveryhodnejší než workload.

## 24. SLO-oriented monitoring

Platform metrics doplň application SLIs:

- request success rate,
- latency distribution,
- availability,
- queue lag,
- data freshness,
- saturation.

Pod Ready alebo Deployment Available nie je business SLI. Kubernetes control signals hovoria o orchestrator stave, nie automaticky o používateľskom výsledku.

## 25. Alert design

Alert má mať:

- actionable condition,
- owner,
- severity a urgency,
- runbook,
- deduplication/grouping,
- symptom alebo cause classification,
- suppression počas maintenance,
- test a review cadence.

Príklady:

- API error-rate/SLO burn,
- etcd quorum alebo latency,
- Nodes NotReady,
- CNI/CSI/DNS availability,
- certificate expiry,
- backup/restore-test failure,
- workload SLO burn.

Nealertuj na každý Warning Event samostatne.

## 26. Troubleshooting

### `kubectl logs` je prázdne

Over container selection, stdout/stderr behavior, current/previous instance, runtime log path, rotation a Node availability.

### Logs chýbajú iba z jedného Node-u

Over node agent, permissions/SELinux, filesystem, collector buffer, network a backend rejection.

### `kubectl top` nefunguje

Over metrics-server Pods, `v1beta1.metrics.k8s.io` APIService, kubelet TLS/connectivity a aggregator path.

### HPA hlási `FailedGetResourceMetric`

Over metrics API, Pod requests, eligible Pods, stale metrics a adapter logs.

### Prometheus memory rastie

Analyzuj active series, top labels/metrics, short-lived workloads, scrape duplication a unbounded labels.

### Events chýbajú po incidente

Ich retencia bola kratšia než detection delay. Potrebuješ Event export alebo central logs/audit.

### Dashboard ukazuje healthy, používatelia hlásia outage

Dashboard sleduje infra state, nie end-to-end SLI. Over DNS/LB/Gateway/Service/application a business metrics.

## 27. Anti-patterny

### Application loguje iba do file-u vo writable layeri

Collector ani `kubectl logs` ho nemusí zachytiť a replacement ho odstráni.

### Metrics-server považovaný za monitoring systém

Nemá dlhodobú retenciu ani plný alerting/query model.

### Všetky Kubernetes labels kopírované do metrics

Vzniká nekontrolovaná cardinality.

### Events považované za permanentný incident záznam

Môžu expirovať a byť agregované.

### Audit RequestResponse bez redakcie

Do backendu sa môžu dostať Secrets a citlivé payloady.

### Alert na každý container restart

Vytvára noise bez kontextu SLO, restart rate a failure reason.

### Observability backend v rovnakom failure domaine bez bufferu

Pri cluster incidente zmizne aj evidence.

## 28. Kontrolné otázky

1. Aký je rozdiel medzi logs, metrics, Events, traces a audit logs?
2. Ako funguje stdout/stderr container logging path?
3. Aké limity má `kubectl logs`?
4. Čo poskytuje metrics-server a čo neposkytuje?
5. Ako sa líši kube-state-metrics od resource metrics?
6. Prečo Events nie sú audit trail?
7. Čo spôsobuje time-series cardinality explosion?
8. Ako koreluješ Pod replacement naprieč logs a Events?
9. Prečo Pod readiness nie je application SLI?
10. Čo musí obsahovať bezpečný cluster-level logging model?

## Glossary impact

Relevantné pojmy: cluster-level logging, CRI log, log rotation, node log agent, resource metrics pipeline, metrics-server, kube-state-metrics, component metrics, metrics stability, time-series cardinality, Kubernetes Event, Event series, audit log, observability correlation a telemetry retention.

## Oficiálna dokumentácia

- [Logging Architecture](https://kubernetes.io/docs/concepts/cluster-administration/logging/)
- [System Logs](https://kubernetes.io/docs/concepts/cluster-administration/system-logs/)
- [Observability](https://kubernetes.io/docs/concepts/cluster-administration/observability/)
- [Metrics for Kubernetes system components](https://kubernetes.io/docs/concepts/cluster-administration/system-metrics/)
- [Events API](https://kubernetes.io/docs/reference/kubernetes-api/cluster-resources/event-v1/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Upgrades](upgrades.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Kubernetes troubleshooting →](kubernetes-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
