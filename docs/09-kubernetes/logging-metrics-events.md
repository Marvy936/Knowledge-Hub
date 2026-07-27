# Logging, metrics a events

Kubernetes observability nie je zbierka dashboardov. Je to evidence lifecycle, ktorý musí preniesť dôveryhodné pozorovanie od konkrétneho processu, objektu, Node-u alebo API requestu až k rozhodnutiu o incidente, upgrade-e alebo business SLO. Signál môže byť emitovaný a pritom nikdy zozbieraný, prijatý backendom a pritom nevyhľadateľný, alebo správne zobrazený a pritom patriť inej Pod či release generácii.

Táto kapitola používa jeden dominantný lifecycle:

```text
incident, SLO, security a audit otázka
→ signal contract a source identity
→ instrumentation a emission
→ node/component collection
→ transport, buffering a backpressure
→ enrichment, redaction a cardinality policy
→ backend ingestion, indexing a retention
→ query, correlation a alert verdict
→ operational alebo business decision
→ replay, recovery, deletion a evidence closure
```

## 1. Atlas observability subject

Atlas Payments potrebuje korelovať jednu payment požiadavku cez edge, Service, Pod, databázu aj cluster zmenu. Exact correlation envelope obsahuje:

```text
cluster a environment
upgrade/deployment operation ID
release a image digest
namespace a workload revision
Pod UID, container ID a restart generation
Node UID a Node-image generation
request/trace/payment ID
Service a EndpointSlice generation
collector Pod/config/offset generation
backend tenant, stream/index a retention class
UTC timestamp a clock-quality verdict
```

Pod meno alebo label `app=payments` nestačí. Po replacement-e môže rovnakú logickú rolu vykonávať iný Pod UID, iný container ID a iná Node generation.

## 2. Päť rozdielnych evidence typov

### Logs

Chronologické records o konkrétnych udalostiach procesu alebo componentu. Poskytujú detail, ale nie automaticky agregovaný rozsah ani úplnosť.

### Metrics

Numerické time series vhodné na rate, latency, saturation, capacity a SLO výpočty. Agregácia je efektívna, ale môže skryť jednotlivý request alebo chybnú cohortu.

### Kubernetes Events

Krátkodobé API objekty s diagnostickým pozorovaním scheduleru, kubeletu alebo controlleru. Môžu byť agregované, rate-limited a expirované.

### Audit records

Záznamy Kubernetes API requests: kto, s akou identitou, nad ktorým resource-om, aký operation požadoval a aký bol API verdict. Audit nepreukazuje, že controller alebo workload následne dosiahol business outcome.

### Traces a business events

Trace spája latency a causality requestu medzi services. Business event reprezentuje doménový fakt, napríklad autorizovanú platbu. Ani jeden nevzniká automaticky iba preto, že workload beží v Kubernetes.

Tieto signály sa dopĺňajú, ale nie sú vzájomne zameniteľné:

```text
Kubernetes Event: scheduler nenašiel feasible Node
Audit record: identita požiadala o scale update
Application log: worker začal spracúvať payment
Trace: request čakal 700 ms na DB
Business event: payment P-884 bol committed exactly once
```

## 3. Emission nie je collection

Odporúčaný container logging chain:

```text
application stdout/stderr
→ CRI runtime log record na Node-e
→ kubelet/runtime log access
→ node collector
→ transport/buffer
→ central backend
→ indexed a queryable record
```

Každá šípka je samostatná failure boundary. `kubectl logs` môže fungovať, hoci central backend nemá record, pretože kubelet stále číta lokálny runtime log. Naopak collector môže odoslať record, ale backend ho odmietne pre credential, tenant quota, schema alebo timestamp.

Application file v writable layeri nie je automaticky súčasť CRI logging pathu. Ak aplikácia musí používať file, potrebuje explicitný volume, collector contract, rotation a retention.

## 4. Collection subject a offset identity

Node collector musí vedieť, čo presne sleduje:

```text
Node UID a host-image generation
runtime a CRI log-path convention
Pod UID, container ID a log stream
file/inode alebo runtime source identity
collector Pod UID a config hash
read offset/checkpoint
buffer generation a destination
```

Sledovanie iba pathname môže po rotation, truncate alebo Node replacement-e viesť k duplicite či medzere. Collector readiness, ktorá testuje iba vlastný HTTP endpoint, nepreukazuje, že číta všetky expected sources.

## 5. Rotation, buffering a backpressure

Node-local rotation chráni disk, ale vytvára evidence window. Ak collector zaostáva dlhšie než lokálna retencia, incident data sa nenávratne stratia.

Transport musí mať explicitný model:

```text
read source
→ bounded memory/disk buffer
→ batch/retry
→ backend acknowledgement
→ durable checkpoint/offset advance
```

Failure boundaries:

- offset sa posunie pred durable backend acknowledgementom;
- backend odpoveď sa stratí a retry vytvorí duplicates;
- buffer zaplní disk a vyvolá Node pressure;
- collector dropne records bez per-source counters;
- credential expiry zastaví export, ale collector ostane `Ready`;
- rotation odstráni unread file.

Observability pipeline je produkčný distributed system. Potrebuje capacity, retries, idempotency alebo deduplication, SLO a recovery.

## 6. Enrichment, provenance a redaction

Enrichment musí zachovať provenance a nezmeniť identity význam:

```text
source timestamp a stream
cluster/namespace
Pod UID a owner UID
container ID a image digest
Node UID/generation
release a operation ID
request/trace ID
collector a pipeline generation
```

Nekopíruj automaticky všetky labels a annotations. Dynamic labels ako request ID, account ID, Job/Pod UID alebo error message vytvárajú vysokú cardinality a môžu obsahovať nedôveryhodné dáta.

Redakcia musí prebehnúť pred širokým backend accessom. Logs a audit records nesmú nekontrolovane obsahovať:

- ServiceAccount alebo external tokens;
- Secret payloady;
- private keys;
- celé citlivé request/response bodies;
- osobné alebo platobné údaje bez policy;
- environment dumpy.

## 7. Metrics ako versionovaný contract

Metric nie je iba názov. Contract obsahuje:

```text
source component a version
metric name, type a units
labels a ich bounded domain
collection interval a freshness
aggregation/window semantics
missing-data behavior
expected causal interpretation
retention a query owner
```

Rozlišuj:

- resource metrics z metrics-server pipeline-u;
- component metrics API servera, scheduleru, kubeletu, etcd a add-ons;
- object-state metrics odvodené zo spec/status objektov;
- application a business metrics;
- custom/external metrics používané autoscalingom.

Metrics-server poskytuje aktuálne resource metrics pre `kubectl top` a HPA. Nie je dlhodobý monitoring backend ani úplný incident archive.

## 8. Cardinality ako capacity a availability boundary

Počet time series rastie kartézskym súčinom label values. Rizikové dimensions:

- Pod UID pri krátko žijúcich Jobs;
- request, payment alebo user ID;
- dynamická URL;
- raw error message;
- unbounded annotation;
- duplicita target discovery;
- per-object image digest tam, kde nie je potrebný.

Cardinality explosion spôsobí ingest backpressure, vysokú memory, pomalé queries a oneskorené alerty. Detail requestu patrí typicky do logs alebo traces, nie do metric labelu.

## 9. Events, audit a business truth

Kubernetes Event je observation jedného reporteru v konkrétnom čase. Event series môže agregovať opakovania. Retencia býva kratšia než incident detection delay.

Audit record pre successful `PATCH deployments/scale` znamená iba, že API server request autorizoval a prijal. Neznamená, že:

- Deployment controller vytvoril ReplicaSet;
- Pods prešli admission a quota;
- scheduler ich umiestnil;
- readiness a traffic sa zvýšili;
- business latency sa zlepšila.

Business event store musí mať vlastný durability, idempotency a audit contract. Kubernetes Events ho nenahrádzajú.

## 10. Correlation a čas

Incident timeline potrebuje UTC a clock-quality evidence. Clock skew môže:

- obrátiť zdanlivé poradie logs;
- poškodiť trace latency;
- skryť causal vzťah Events a requests;
- spôsobiť token/certificate failure;
- zaradiť records mimo query window.

Koreluj cez immutable alebo generation-aware identifiers. Pod name a timestamp bez UID sú slabé identity.

## 11. Telemetry coverage a acceptance

Observability acceptance nie je „collector Pods sú Ready“. Potrebuje end-to-end test pre každú expected cohortu:

```text
emit known test record/metric/event
→ potvrď local source
→ potvrď collector discovery a offset
→ potvrď transport a backend acknowledgement
→ potvrď query v správnom tenantovi a time range
→ potvrď alert/rule alebo dashboard path
→ potvrď retention a redaction
```

Coverage inventár má zahŕňať:

- všetky Nodes a Node generations;
- control-plane a system components;
- workload stdout/stderr a required files;
- audit a Event export;
- metrics targets a business SLIs;
- buffering pri backend outage-i;
- forbidden secret fields.

## 12. Causal walkthrough: central logs chýbajú iba z novej Node cohorty

### Symptom

Po Kubernetes upgrade-e hlásia používatelia intermittent `502`. Infra dashboard je prevažne green. `kubectl logs` na affected Payments Pod-e obsahuje timeouty, ale central log search nevracia žiadne application ani CNI records z nových Nodes.

### Exact subject

Fixuj:

- payment request a UTC time window;
- release/image, Pod UID, container ID a restart generation;
- old/new Node UID, image a runtime generation;
- CRI local log path/file identity;
- collector DaemonSet revision, Pod UID a config hash;
- hostPath mounts, discovery rules a read offsets;
- buffer state, backend credential/tenant/index;
- backend ingest acknowledgement a query filters.

### Competing hypotheses

1. application na nových Nodes neloguje;
2. logs idú do file-u mimo stdout/stderr;
3. runtime nevytvára CRI records;
4. collector nie je naplánovaný na target Nodes;
5. collector má nesprávny hostPath alebo discovery pattern;
6. rotation odstránila records pred prečítaním;
7. collector buffer je plný;
8. backend odmieta iba target-cohort metadata;
9. query používa zlý cluster/tenant/time range;
10. clock skew posúva records mimo incident window.

### Discriminating observations

Vytvor bounded test record s unikátnym correlation ID na jednom old a jednom target Node-e. Over ho postupne v `kubectl logs`, runtime log file-e, collector discovery/state/offsete, bufferi, transport acknowledgement a backend query.

Finding:

```text
nový Node image používa odlišnú runtime log-path/symlink generation
→ kubelet vie log čítať cez runtime
→ collector DaemonSet je Ready
→ collector hostPath/config sleduje iba legacy Node layout
→ records z target Nodes nikdy nevstúpia do pipeline
→ dashboard metrics zostávajú green
→ incident diagnostika má cohort-specific blind spot
```

### Containment

- nezmazávaj affected Pods ani lokálne files pred exportom evidence;
- zastav Node rollout, ak telemetry blind spot znemožňuje bezpečný verdict;
- zachovaj collector config, offsets, buffers a backend rejection logs;
- použi kontrolovaný node-local zber s auditovaným accessom;
- obmedz retry amplification v application path-e;
- nevypínaj redakciu ani neposielaj raw Secrets ako rýchlu opravu.

### Authoritative recovery

- versionuj collector mounts/discovery pre current runtime layout;
- zaveď Node-generation aware conformance test;
- rolloutni collector canary na target cohortu;
- replay-ni zachované buffers alebo files, ak to identity/dedup model umožňuje;
- pridaj per-Node source/collected/exported/accepted counters;
- pridaj business SLI a external synthetic nezávislý od platform dashboardu;
- retire-ni legacy config až po complete cohort coverage.

### Verify original a forbidden outcomes

Over:

1. test record je queryable z každého Node generation;
2. source, collector a backend counts sa vysvetliteľne zhodujú;
3. rotation a backend outage nespôsobia tichú stratu;
4. CNI, kubelet a application records sú korelovateľné s requestom;
5. Events a audit records sú odlíšené od business eventov;
6. metrics a alerts pokrývajú target cohortu;
7. sensitive values sú redacted a access ostáva least privilege;
8. payment journey a jeho error path sú viditeľné end-to-end;
9. collector replacement zachová offset/dedup contract.

### Earlier controls

Použi telemetry conformance canary v Node-image CI, source-to-query synthetic, per-cohort coverage SLO, bounded cardinality budget, retention dlhšiu než detection delay, off-cluster buffer/evidence a alert na chýbajúce expected sources.

## 13. Ďalšie failure boundaries

### `kubectl logs` je prázdne

Over exact container, current/previous container ID, stdout/stderr, runtime record, Node availability a rotation. Nezamieňaj application file logging s CRI streamom.

### `kubectl top` alebo HPA metric chýba

Sleduj kubelet resource source → metrics-server → APIService/aggregation → client/HPA. Over TLS, RBAC, freshness a requests denominator.

### Prometheus backend rastie bez zvýšenia trafficu

Analyzuj new series, label cardinality, duplicate scraping a short-lived objects. Nestačí zvýšiť memory bez odstránenia unbounded dimensionu.

### Events po incidente chýbajú

Retencia bola kratšia než detection delay alebo Event bol agregovaný. Exportuj dôležité Events a koreluj ich s logs/auditom.

### Dashboard je green, business SLO horí

Dashboard sleduje nesprávnu vrstvu, cohortu alebo query. Over external journey, release/Node split, raw target freshness a absent-evidence stav.

### Audit backend obsahuje Secret payload

Audit policy alebo redaction je príliš široká. Obmedz Request/Response capture, chráň backend a rotuj exponované credentials.

## 14. Retention, security a disaster evidence

Pre každý signal definuj:

```text
owner a consumers
retention a deletion policy
failure-domain umiestnenie
access a tenant isolation
integrity a immutability
redaction a legal/compliance scope
replay/export a incident recovery
```

Observability backend v rovnakom failure domain-e bez bufferu môže zmiznúť spolu s clusterom. Audit a recovery evidence potrebuje oddelenú trust a retention hranicu.

## 15. Alert a SLO closure

Alert má byť viazaný na actionable subject a runbook. Potrebuje:

- symptom alebo causal classification;
- owner, urgency a escalation;
- grouping/deduplication;
- maintenance suppression;
- data freshness a absent-series handling;
- test a review cadence;
- business alebo platform SLO, ktoré chráni.

Nealertuj na každý Warning Event alebo jeden container restart. Alertuj na failure model: napríklad rollout bez serving capacity, etcd write SLO burn, chýbajúcu telemetry cohortu alebo payment error-rate burn.

## 16. Referenčný katalóg

### Evidence boundaries

```text
emitted
collected
buffered
exported
accepted
indexed
queryable
retained
correlated
used in a verdict
```

### Základné source categories

- application stdout/stderr, metrics a traces;
- kubelet/runtime/Node logs a metrics;
- control-plane a etcd telemetry;
- Kubernetes Events a object status;
- API audit records;
- CNI/CSI/DNS/Gateway a policy signals;
- business events a external synthetics.

## 17. Anti-patterny

- collector `Ready` považovaný za coverage verdict;
- metrics-server považovaný za monitoring backend;
- Events považované za audit alebo business store;
- všetky labels kopírované do metrics;
- logs bez Pod UID/release/trace identity;
- backend acknowledgement ignorované pri offset avance;
- retention kratšia než detection delay;
- audit RequestResponse bez redakcie;
- dashboards bez freshness a cohort dimensions;
- observability stack bez vlastného SLO a recovery;
- green infra metrics považované za business success.

## 18. Kontrolné otázky

1. Ktoré boundaries oddeľujú emitted, collected a queryable record?
2. Prečo `kubectl logs` môže fungovať pri prázdnom central backend-e?
3. Ako sa líši Kubernetes Event, audit record a business event?
4. Ktoré identities tvoria correlation envelope jedného requestu?
5. Ako collector offset a backend acknowledgement ovplyvnia loss/duplicates?
6. Prečo metrics-server nie je dlhodobý monitoring systém?
7. Ako cardinality explosion ovplyvní availability observability backendu?
8. Ako preukážeš telemetry coverage každej Node generation?
9. Prečo absent data nie je automaticky dôkaz absent incidentu?
10. Ktoré dôkazy uzatvárajú observability recovery?

## Glossary impact

Relevantné pojmy: telemetry lifecycle subject, signal contract, correlation envelope, emission boundary, collection subject, collector offset generation, telemetry backpressure boundary, backend acknowledgement, ingestion/query boundary, telemetry coverage generation, absent-evidence verdict, observability acceptance, cardinality budget, telemetry retention verdict, audit/Event/business-event separation a subject-bound evidence closure.

## Oficiálna dokumentácia

- [Logging Architecture](https://kubernetes.io/docs/concepts/cluster-administration/logging/)
- [System Logs](https://kubernetes.io/docs/concepts/cluster-administration/system-logs/)
- [Observability](https://kubernetes.io/docs/concepts/cluster-administration/observability/)
- [Metrics for Kubernetes system components](https://kubernetes.io/docs/concepts/cluster-administration/system-metrics/)
- [Events API](https://kubernetes.io/docs/reference/kubernetes-api/cluster-resources/event-v1/)
- [Auditing](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Upgrades](upgrades.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Kubernetes troubleshooting →](kubernetes-troubleshooting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->