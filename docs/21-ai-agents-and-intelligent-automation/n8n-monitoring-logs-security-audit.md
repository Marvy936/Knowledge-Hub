# n8n monitoring, logs a security audit

Prevádzková viditeľnosť n8n vzniká kombináciou health checks, metrics, application logs, execution data, distributed traces, streamed events, provider audit a business records. Žiadny jednotlivý signal nepreukazuje, že workflow vykonal správny side effect pre správneho tenant-a a že recovery je úplná.

Táto kapitola uzatvára incident `AGENT-N8N-09`. Dashboard scrapoval iba main process a zobrazoval zdravý HTTP endpoint, zatiaľ čo workers strácali PostgreSQL readiness. Viaceré workers zapisovali event log na spoločný path, takže recovery stream bol neúplný. OpenTelemetry nebolo zapnuté na webhook processors a sampling vyradil affected trace; security audit sa spustil až po incidente a našiel risky nodes, ale nevysvetlil database a storage failure.

Nosný observability lifecycle je:

```text
business objective a failure boundaries
→ exact instance, role, release a workflow identities
→ health, metrics, logs, events a trace instrumentation
→ secure collection a correlation
→ alert condition a incident classification
→ evidence preservation a competing hypotheses
→ containment a recovery verification
→ business, security a second-operation acceptance
→ retention, access a control-effectiveness review
```

## 1. Observability purpose

Observability umožňuje odvodiť internal state zo signals, ktoré systém produkuje. V n8n musí vysvetliť ingress, queue, worker, database, node, storage, credential a external-provider path.

Cieľom nie je zbierať maximum dát. Cieľom je zachovať enough identity a causal evidence na určenie first divergence a bezpečné recovery.

## 2. Signal taxonomy

Health checks odpovedajú na bounded availability otázku, metrics agregujú numerické správanie, logs zaznamenávajú udalosti a context, traces spájajú execution path a audit events preukazujú citlivé zmeny alebo actions. Business records potvrdzujú reálny outcome.

Signals sa dopĺňajú, ale nie sú zameniteľné. Trace sampling nemá odstrániť required audit event a security audit report nenahrádza runtime monitoring.

## 3. Exact telemetry subject

Každý signal nesie instance ID, process role, n8n version, image/config generation, workflow ID/version, execution ID a podľa potreby project/tenant a node type. Bez týchto dimensions aggregate mieša incompatible generations.

Sensitive tenant alebo resource identifiers sa pseudonymizujú alebo ukladajú v controlled fields. Correlation musí zostať možná bez raw secretu.

## 4. Intended, loaded a exercised instrumentation

Configuration môže deklarovať metrics alebo tracing, ale collector nemusí byť reachable a worker nemusí setting načítať. Loaded state sa overí process metadata a test signalom.

Exercised state znamená, že representative execution vytvorila expected metric, log/event a trace path. Dashboard existence nie je instrumentation proof.

## 5. Health checks

Liveness zisťuje, či process beží. Readiness zisťuje, či je pripravený obsluhovať work s critical dependencies, napríklad PostgreSQL a Redis pri workerovi.

Health endpoint má narrow semantics a nie je SLO. Worker môže byť ready, ale external provider môže byť unavailable alebo workflow môže používať nesprávny credential.

## 6. Main-process health

Main process môže odpovedať na editor a internal API, zatiaľ čo queue execution stojí. Dashboard, ktorý kontroluje iba main HTTP 200, preto môže hlásiť green počas production outage.

Service check zahŕňa representative workflow alebo synthetic journey. UI availability a automation availability sa merajú oddelene.

## 7. Worker health

Pri zapnutých queue health endpoints worker poskytuje liveness a readiness, ktorá zahŕňa database a Redis connections podľa n8n modelu. Scheduler počíta iba ready workers ako usable capacity.

Readiness flapping je signal dependency alebo resource pressure. Automatický restart bez preservation môže opakovať churn a zničiť in-memory evidence.

## 8. Prometheus metrics

n8n používa `prom-client` a `/metrics` endpoint je defaultne vypnutý. Zapína sa explicitne cez `N8N_METRICS=true` a dostupné include flags určujú ďalšie labels a metric groups.

Main aj worker instances môžu expose metrics. Scraping iba jedného procesu nevytvorí complete distributed view.

## 9. Metrics endpoint security

`/metrics` môže odhaliť workflow, queue, process a resource information a nemá byť verejne dostupný. Prístup dostanú iba internal collectors cez network a authentication controls podľa platformy.

Public endpoint nie je prijateľný kompromis za jednoduchší scrape. Monitoring architecture musí rešpektovať rovnaké trust boundaries ako application.

## 10. Queue metrics

Queue metrics zahŕňajú waiting, active, completed a failed jobs podľa current n8n integration. Queue depth sa kombinuje s oldest age, enqueue/completion rate a ready-worker denominatorom.

Na multi-main deployment-e treba rozlíšiť leader a neagregovať duplicated alebo role-specific metrics nesprávne. Metric semantics sa validujú po upgrade-e.

## 11. Process metrics

CPU, memory, event-loop lag, restarts, open file descriptors a garbage collection pomáhajú určiť resource saturation. Container CPU nízke pri vysokom latency môže znamenať I/O alebo dependency wait.

Process metrics sa korelujú s workflow classou. Jeden memory-heavy binary workflow môže skryť healthy behavior väčšiny executions.

## 12. Dependency metrics

PostgreSQL connections, locks, latency, WAL a storage; Redis queue, memory a latency; object-storage requests a errors; provider rate limits a response classes tvoria rovnaký service graph.

n8n metric bez downstream signalov neukáže, či bottleneck vznikol v engine alebo mimo neho. Ownership map určuje, kto reaguje na každý dependency alert.

## 13. Business metrics

Technical success sa porovnáva s accepted business outcomes: created tickets, completed refunds, delivered notifications alebo reconciled resources. Denominator zahŕňa eligible operations, nie iba n8n executions.

Green execution rate môže skryť wrong-tenant alebo partial per-item failure. Outcome metrics a forbidden-event counters sú release gate.

## 14. Application logging

n8n používa Winston a podporuje levels `silent`, `error`, `warn`, `info` a `debug`. Output môže smerovať do console, file alebo oboch podľa configuration.

Production default nie je automaticky správny pre každý incident. Debug level zvyšuje volume a potential sensitive exposure, preto sa zapína bounded a časovo obmedzene.

## 15. Log structure

Log message obsahuje human-readable význam a structured metadata, najmä execution ID, workflow ID, process role, node type a release generation. Duplicate text a metadata môžu zlepšiť search aj filtering.

Raw token, credential, document alebo prompt sa neloguje bez explicitnej policy. Redaction sa testuje na error paths, nie iba happy path.

## 16. Console verzus file

Console logs prirodzene zbiera orchestrator alebo runtime platforma a zachová process stream. File logs potrebujú persistent path, rotation, disk capacity a collector ownership.

Kombinovaný output môže zdvojiť volume. Design určuje authoritative operational log a nepredpokladá, že lokálny file prežije Pod reschedule.

## 17. Log rotation

`N8N_LOG_FILE_SIZE_MAX` a `N8N_LOG_FILE_COUNT_MAX` obmedzujú file volume. Retention musí zodpovedať incident detection a disk budgetu.

Rotation success sa monitoruje. Full disk môže zastaviť application alebo stratiť evidence presne počas incidentu.

## 18. Per-process files

Queue workers na shared writable filesysteme nesmú zapisovať event log do rovnakého file. Concurrent append môže interleave alebo corrupt records a poškodiť recovery forwarding.

`N8N_EVENTBUS_LOGWRITER_LOGFULLPATH` sa nastaví na unique absolute path pre každý process, ak sa používa file-backed event log. Uniqueness je responsibility orchestrátora.

## 19. Log streaming

Enterprise log streaming posiela selected workflow, node, audit, worker, runner a queue events do external destinations. Local event log pomáha re-emitnúť events, ktoré sa nepodarilo doručiť pred restartom.

Streaming destination môže zlyhať a circuit breaker môže zastaviť delivery. Local durability, backlog a destination health sa monitorujú oddelene.

## 20. Event completeness

Subscribed event list určuje, čo sa forwarduje. Missing category alebo new event type môže vytvoriť audit gap aj pri healthy destination.

Schema/version a configuration generation sa evidujú. Consumer, ktorý nepozná critical field, nesmie event ticho interpretovať ako complete.

## 21. Operational logs verzus audit events

Operational log je určený na debugging a môže byť sampled, rotated alebo zmenený levelom. Audit event zachytáva sensitive action, identity a decision s požadovanou integrity a retention.

Jeden stream môže technicky prenášať oba typy, ale governance a completeness requirements zostávajú odlišné. Debug log nie je tamper-evident ledger.

## 22. OpenTelemetry tracing

Current n8n documentation opisuje OpenTelemetry tracing workflow a node executions ako vyvíjanú feature. Workflow span nesie workflow/execution identity a node spans zachytávajú node type, version a item counts.

Trace pomáha určiť latency a first divergence. Neobsahuje automaticky authoritative provider outcome alebo complete audit history.

## 23. Queue-mode trace propagation

V queue mode sa tracing configuration nastavuje na všetkých relevantných instances a trace context sa prenáša medzi roles. Webhook ingress môže nadviazať na W3C `traceparent` a outbound HTTP helper ho môže propagovať downstream.

Chýbajúca instrumentation na webhook alebo workerovi rozbije causal chain. Collector test iba z main procesu nie je dostatočný.

## 24. Sub-workflow a resume traces

Sub-workflow span môže byť child parent workflow span-u a resumed workflow používa link na predošlý span podľa current n8n modelu. Tým sa dá sledovať distributed a waiting lifecycle bez predstierania jednej nepretržitej process session.

Correlation sa overí v reálnom wait/resume teste. Backend UI môže links zobrazovať odlišne a nesmie meniť underlying semantics.

## 25. Sampling

Trace ratio sampling znižuje cost, ale môže vynechať rare incident. Sampling policy sa segmentuje podľa risku a môže vždy zachovať errors alebo high-impact workflows v collector layeri podľa architecture.

Sampled-out trace neznamená, že execution neexistovala. Required audit a business ledger musia zostať complete nezávisle od trace samplingu.

## 26. Sensitive trace data

Custom attributes, prompts, tool arguments, responses a node expressions môžu obsahovať sensitive data. Current agent tracing options preto umožňujú vypnúť recording inputs a outputs.

Attributes používajú low-cardinality a non-secret values. Tenant correlation sa rieši scoped pseudonymous ID, nie emailom alebo tokenom.

## 27. Trace exporter failure

Collector outage nesmie zastaviť critical workflow, pokiaľ policy neurčuje fail-closed audit path. Export queue, drops a retry pressure však môžu spotrebovať resources.

Observability backend má vlastný SLO. Absence traces sa alertuje ako telemetry failure, nie interpretuje ako absence incidents.

## 28. Execution history

n8n execution data poskytuje detail node inputs, outputs a errors podľa save/retention settings. Je užitočné pre debugging, ale môže byť pruned, redacted alebo inaccessible po workflow deletion.

Incident preservation preto exportuje bounded evidence pred remediation. Execution UI nie je immutable audit store.

## 29. Custom execution data

Supported editions umožňujú ukladať custom searchable values, ktoré pomáhajú correlation podľa operation alebo tenant class. Hodnoty musia byť minimalizované a nesmú obsahovať secrets.

Custom field nie je substitute pre stable business ledger. Je to index do authoritative records.

## 30. Security audit purpose

`n8n audit`, owner-authenticated `/audit` API alebo n8n Audit node detegujú common configuration a workflow risks. Report pokrýva credentials, database expressions, filesystem nodes, risky/community/custom nodes a instance findings.

Audit je point-in-time heuristic control. Nevykonáva penetration test, tenant isolation test ani runtime outcome verification.

## 31. Credential findings

Audit môže identifikovať unused credentials alebo credentials nepoužívané active/recent workflows. Taký nález podporuje cleanup a ownership review.

Používaný credential však môže byť stále over-privileged alebo wrong-tenant. Positive absence finding nie je least-privilege proof.

## 32. Database findings

Audit upozorňuje na expressions v SQL query alebo parameter fields a unused query parameter configuration. Pomáha odhaliť injection alebo unsafe query construction patterns.

Nedokáže dokázať database user permissions, TLS, row-level authorization ani correctness každého dynamic query. Findings sa analyzujú v workflow contextu.

## 33. Filesystem a node findings

Filesystem-interacting, official risky, community a custom nodes rozširujú capability surface. Nález vedie k owner, necessity, sandbox, network a credential review.

Rizikový node nie je automaticky malicious a official node nie je automaticky safe pre každý tenant. Effective capabilities rozhodujú.

## 34. Instance findings

Audit môže odhaliť unprotected webhooks, missing security settings alebo outdated instance. Tieto findings sú dôležité, ale report nemusí pokryť external proxy, firewall, object store, Redis alebo provider IAM.

Security posture je composed system property. n8n audit je jedna control vrstva.

## 35. Audit scheduling

Security audit sa spúšťa po relevantnej zmene a periodicky. Výstup sa versionuje, priraďuje ownerom a porovnáva s previous baseline.

Automatický report bez remediation SLA vytvára compliance theater. Critical finding môže blokovať release alebo aktivovať containment.

## 36. Alert design

Alert má symptom, threshold, duration, scope, owner a runbook. Queue age, no-ready-workers, database saturation, execution failure, missing binary reference, log-stream drop a security finding majú odlišnú urgency.

Alerts sa deduplikujú podľa incident subjectu. Jeden dependency outage nemá vytvoriť stovky nezávislých tickets bez causal grouping.

## 37. SLO a burn rate

SLO môže merať accepted automation completion latency a correctness pre defined workflow class. Burn-rate alert odhalí rýchle alebo dlhodobé vyčerpávanie error budgetu.

Process uptime nie je dostatočný SLI. User outcome zahŕňa queue wait, execution, provider commit a reconciliation.

## 38. Shared incident `AGENT-N8N-09`

Main `/healthz` a metrics boli green, ale workers strácali PostgreSQL readiness po connection exhaustion. Dashboard nescrapoval worker endpoints ani queue oldest age, preto incident vyzeral ako krátky traffic burst.

Workers na shared volume zapisovali event logs na rovnaký path a časť records sa nedala spoľahlivo replaynúť. OTel bol enabled iba na main a sampled trace neobsahoval affected execution.

## 39. Competing failure hypotheses

Prvá hypotéza je worker CPU saturation, druhá database connection failure, tretia Redis delay, štvrtá binary storage read failure a piata telemetry gap bez actual runtime outage. Signals môžu byť chybné alebo neúplné.

Diagnosis porovná direct readiness, PostgreSQL a Redis authority, execution state, object read a external outcome. Dashboard color nie je authoritative evidence.

## 40. Evidence preservation

Zachová sa dashboard query/version, raw metrics, worker inventory, logs, event-file state, trace IDs, execution IDs, audit report, config generations a collector health. Timestamps sa normalizujú a source clock drift eviduje.

Pred zmenou sampling alebo log levelu sa snapshotne current configuration. Nové verbose logs nesmú byť prezentované ako pôvodná evidence.

## 41. Containment

Alerting sa prepne na direct worker readiness a database/Redis signals, autoscaling sa pozastaví a event-log paths sa oddelia. Sensitive debug logging sa zapne iba pre affected cohort a krátke okno.

Unprotected webhook alebo dangerous node finding môže vyžadovať okamžité disable/deny. Observability remediation nesmie odkladať security containment.

## 42. Recovery

Metrics sa zbierajú zo všetkých process roles, OTel sa nastaví konzistentne a representative trace overí context propagation. Event streaming dostane unique local files, destination health a replay test.

Security audit findings sa priradia ownerom a corrective actions sa overia independent read-backom. Business synthetic potvrdí complete outcome.

## 43. Positive acceptance

Representative workflow vytvorí korelovateľný ingress, queue, worker, node, database a provider evidence. Alert sa spustí pri safe injected failure a runbook identifikuje first divergence.

Metrics endpoint ostáva internal, logs a traces neobsahujú secrets a required audit events sú complete aj pri trace samplingu.

## 44. Forbidden acceptance

Monitoring nie je prijatý iba preto, že dashboard existuje alebo main process je green. Neprípustné sú public metrics, shared corrupt event log, secrets v debug outpute, tracing iba jednej role a unresolved critical audit finding.

Nulový počet alerts môže znamenať zdravý systém alebo nefunkčnú telemetry. Control sa musí pravidelne testovať.

## 45. Recovery acceptance

Collector outage, worker restart, event destination failure a sampled trace drill preukážu, ktoré signals sa stratia a ktoré required records ostanú. Alert na telemetry failure sa odlíši od application failure.

Po recovery sa incident dá rekonštruovať z independent sources a second operation potvrdí, že fix nie je viazaný iba na jeden trace.

## 46. Second-workflow acceptance

Druhý workflow s binary payloadom a sub-workflowom vytvorí complete correlations bez cardinality explosion a cross-tenant data. Security audit a runtime controls odmietnu forbidden node alebo unprotected route.

Observability cost a latency zostanú v budgete. Zvýšený detail nesmie destabilizovať workers alebo collector.

## 47. Praktický telemetry manifest

Manifest viaže signal configuration na release a retention. Neobsahuje collector secret ani raw tenant data.

```yaml
telemetry_subject:
  release: n8n-prod-2.x-sha256
  metrics:
    enabled: true
    exposure: internal-only
    roles: [main, webhook, worker]
    queue_metrics: true
  logs:
    level: info
    output: console
    event_file_per_process: true
  tracing:
    enabled_roles: [main, webhook, worker]
    sample_rate: 0.10
    record_sensitive_inputs: false
  security_audit:
    cadence: weekly
    release_gate: critical-findings-zero
```

## 48. Prevádzkové metriky

Sledujú sa telemetry coverage podľa role/generation, scrape failures, log drops, event-stream backlog, corrupt event files, trace export failures, sampling rate, execution-to-trace correlation, audit finding age a synthetic journey success. Coverage má explicitný denominator všetkých active processes.

Metrika `100 % scrape targets up` je useful iba ak target inventory je complete. Missing workers mimo discovery môžu vytvoriť falošných sto percent.

## 49. Primárne zdroje

- [n8n Docs — Set up logging](https://docs.n8n.io/deploy/host-n8n/keep-n8n-running/set-up-logging/)
- [n8n Docs — Enable Prometheus metrics](https://docs.n8n.io/deploy/host-n8n/configure-n8n/basic-configuration/configuration-examples/enable-prometheus-metrics/)
- [n8n Docs — OpenTelemetry tracing](https://docs.n8n.io/deploy/host-n8n/keep-n8n-running/trace-executions-with-opentelemetry/)
- [n8n Docs — Log streaming](https://docs.n8n.io/administer/observe-and-log/stream-logs-to-external-systems/)
- [n8n Docs — Security audit](https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/run-security-audits/)
- [n8n Docs — Enable queue mode](https://docs.n8n.io/deploy/host-n8n/configure-n8n/scaling/enable-queue-mode/)

## 50. Zhrnutie

n8n observability musí pokrývať všetky process roles a dependencies a zachovať correlation až po business outcome. Main health, aggregate queue depth alebo jeden trace sú neúplné pohľady na distributed automation.

Security audit je užitočný point-in-time detector common risks, nie certifikát bezpečnosti. Accepted stav vyžaduje tested alerts, internal metrics, secure logs/traces, complete required events, incident reconstruction a second-workflow proof.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Binary data, storage a execution retention](binary-data-storage-execution-retention.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
