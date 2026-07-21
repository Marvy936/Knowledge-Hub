# Monitoring vs. observability

Monitoring a observability súvisia, ale nie sú synonymá. Monitoring sleduje známe stavy a podmienky pomocou vopred definovaných signals, queries a thresholds. Observability je schopnosť porozumieť internému stavu systému z jeho externých výstupov a skúmať aj neočakávané otázky bez nasadenia novej diagnostickej verzie.

## 1. Mentálny model

```text
systém
→ instrumentation
→ telemetry signals
→ collection a processing
→ storage a query
→ dashboards, alerts a investigation
→ diagnosis, decision a improvement
```

Observability nie je produkt ani počet dashboardov. Je to vlastnosť systému a jeho operating modelu, ktorú umožňuje kvalitná instrumentation, korelovateľná telemetry, vhodné tools a ľudia schopní tieto dáta interpretovať.

## 2. Monitoring

Monitoring typicky odpovedá na známe otázky:

- Je služba dostupná?
- Prekročila error rate limit?
- Je disk takmer plný?
- Zlyhal backup job?
- Je latency nad SLO thresholdom?
- Je Node alebo target unhealthy?

Monitoring používa:

- metriky,
- health checks,
- log patterns,
- synthetics,
- alarms,
- dashboards,
- scheduled checks.

Je nevyhnutný pre detection a alerting. Sám však nemusí vysvetliť, prečo neznámy failure vznikol.

## 3. Observability

Observability umožňuje skúmať otázky, ktoré neboli presne známe pri návrhu dashboardu:

- Prečo zlyhávajú iba requests konkrétneho tenanta po novej verzii?
- Ktorá downstream dependency spôsobuje p99 latency?
- Prečo sa problém prejavuje iba v jednej AZ a iba pri určitom payload type?
- Ktorý deployment, feature flag alebo configuration change zmenil správanie?
- Kde sa stráca trace context alebo correlation ID?

Vyžaduje dostatočne bohaté a korelovateľné signals, nie neobmedzené množstvo dát.

## 4. Monitoring a observability sa dopĺňajú

```text
monitoring
→ detekuje známy zlý stav

observability
→ pomáha vysvetliť stav, scope, príčinu a súvislosti
```

Dobrá observability bez actionable monitoring-u môže viesť k tomu, že systém je detailne analyzovateľný až po tom, čo používateľ nahlási incident. Monitoring bez observability môže vytvárať alarmy bez dostatočného kontextu na rýchlu diagnostiku.

## 5. Telemetry

Telemetry sú dáta generované systémom o jeho správaní a stave.

Typické signals:

- metrics,
- logs,
- traces,
- events,
- profiles,
- audit records,
- synthetics,
- continuous profiling alebo eBPF-derived signals podľa platformy.

OpenTelemetry štandardizuje instrumentation, generation, collection a export telemetry, najmä traces, metrics a logs. Telemetry sama osebe nevytvára observability; musí byť správne modelovaná, korelovaná a použiteľná.

## 6. Metrics

Metric je agregovateľný číselný signal v čase.

Vhodná na:

- rates,
- latency distributions,
- utilization,
- saturation,
- error ratios,
- capacity a SLO.

Výhody:

- efektívne agregácie,
- dlhšia retention,
- vhodné alerting,
- trend a forecasting.

Limity:

- agregácia môže skryť jednotlivý request,
- high cardinality môže výrazne zvýšiť memory a storage cost,
- nesprávne labels vytvoria neobmedzený počet time series.

## 7. Logs

Log je časovo označený record udalosti alebo stavu.

Vhodný na:

- detailné error context,
- audit,
- application events,
- stack traces,
- state transitions.

Production logs majú byť structured a obsahovať stabilné fields. Free-text logs sa horšie parsujú, korelujú a validujú.

Citlivé údaje, secrets a personal data do logs nepatria bez explicitného protection modelu.

## 8. Traces

Distributed trace zachytáva cestu requestu alebo operácie cez services a dependencies.

Trace pozostáva zo spans, ktoré nesú:

- operation name,
- start a duration,
- parent/child relation,
- attributes,
- status,
- events,
- resource/service identity.

Trace pomáha lokalizovať latency a failure v distributed path-e. Sampling však znamená, že nie každý request musí byť zachovaný.

## 9. Events a audit

Events zachytávajú významné state changes:

- deployment,
- scaling,
- failover,
- configuration change,
- scheduler decision,
- backup failure,
- security finding.

Audit records odpovedajú hlavne na:

- kto,
- čo,
- kedy,
- odkiaľ,
- voči akému resource-u,
- s akým výsledkom.

Audit a observability sa prekrývajú, ale majú odlišné retention, integrity a access požiadavky.

## 10. Profiles

Profile ukazuje, kde application trávi CPU time, alokuje memory alebo čaká.

Použitie:

- CPU hotspots,
- memory allocation,
- lock contention,
- inefficient code paths,
- performance regression.

Profiles sú doplnkový signal. Aktuálny OpenTelemetry ekosystém ich považuje za emerging signal a feature maturity treba overovať podľa konkrétneho SDK/backendu.

## 11. Instrumentation

Systém musí emitovať relevantné signals.

Modely:

- manual instrumentation,
- library/framework instrumentation,
- automatic instrumentation,
- agent/exporter,
- sidecar/collector,
- service mesh alebo eBPF-derived telemetry.

Auto-instrumentation poskytne rýchly baseline, ale nemusí poznať business semantics. Manual instrumentation dopĺňa kritické operations, attributes a outcomes.

## 12. Correlation

Silná observability prepája:

```text
metric spike
→ exemplar alebo timestamp
→ trace
→ service/span
→ correlated logs
→ deployment/configuration event
→ owner a runbook
```

Užitočné correlation fields:

- trace ID,
- span ID,
- request/correlation ID,
- service name,
- environment,
- version/revision,
- region/AZ/node,
- tenant alebo customer segment s privacy kontrolou,
- deployment ID.

## 13. Context propagation

Distributed tracing potrebuje propagovať context cez:

- HTTP headers,
- gRPC metadata,
- message headers,
- async jobs,
- queues a streams,
- background workers.

Prerušený context vytvorí oddelené traces a zníži schopnosť rekonštruovať end-to-end path.

Context propagation nesmie nekontrolovane prenášať sensitive data alebo nedôveryhodné baggage.

## 14. White-box a black-box monitoring

### White-box

Pozoruje interné signals systému:

- request rate,
- queue depth,
- database connections,
- GC,
- saturation.

### Black-box

Pozoruje systém ako používateľ alebo externý client:

- HTTP availability,
- DNS,
- TLS,
- login/checkout synthetic,
- end-to-end latency.

Interné metriky môžu byť zdravé, kým používateľský path zlyháva. Potrebné sú obe perspektívy.

## 15. Known-knowns a unknown-unknowns

Monitoring je silný pri known-knowns a known-unknowns, ktoré sa dajú modelovať vopred.

Observability znižuje čas potrebný na skúmanie unknown-unknowns tým, že systém zachováva relevantný context a umožňuje flexibilné queries.

To neznamená ukladať všetko navždy. Telemetry design potrebuje sampling, cardinality, retention a cost boundaries.

## 16. Symptoms, causes a outcomes

Rozlišuj:

- **symptom** — používateľ alebo systém pozoruje problém,
- **cause** — technický mechanizmus, ktorý ho vytvoril,
- **outcome** — business alebo SLO dopad.

CPU 95 % môže byť cause, symptom alebo normálny stav podľa workloadu. Alarmovať iba na infrastructure signal bez user-impact contextu často vytvára noise.

## 17. Observability a SLO

SLO poskytuje prioritizáciu telemetry.

Najprv definuj:

- čo používateľ považuje za úspech,
- ktoré requests alebo jobs sú validné,
- latency/error/availability objective,
- measurement window,
- exclusions.

Potom navrhni metrics, logs a traces, ktoré vysvetlia odchýlku od objective.

Observability bez service objectives môže produkovať veľa dát bez jasnej priority.

## 18. Alerting

Alert má signalizovať stav, ktorý potrebuje action.

Kvalitný alert obsahuje:

- symptom a impact,
- scope,
- severity,
- current value a threshold,
- relevantný dashboard/query,
- runbook,
- ownera,
- deduplication a routing,
- recovery condition.

Alert na každú internú anomáliu vytvára fatigue. Troubleshooting signals nemusia byť paging signals.

## 19. Telemetry pipeline

```text
instrumented sources
→ agents/exporters/SDKs
→ collectors
→ processing, enrichment a sampling
→ backend storage
→ query, visualization a alerting
```

Pipeline potrebuje vlastnú observability:

- dropped data,
- queue/backpressure,
- exporter failures,
- ingestion latency,
- cardinality,
- sampling rate,
- storage/query errors,
- cost.

„Backend neukazuje chyby“ nemusí znamenať, že application je zdravá; telemetry pipeline môže byť nefunkčná.

## 20. Cardinality

Cardinality je počet unikátnych kombinácií dimensions/attributes.

Rizikové values:

- user ID,
- request ID,
- raw URL,
- unbounded error message,
- timestamp,
- container/Pod identity s krátkym lifecycle-om bez aggregation modelu.

Metrics potrebujú bounded labels. High-cardinality detail patrí často do logs alebo traces s samplingom a retention kontrolou.

## 21. Sampling

Sampling znižuje volume a cost traces/logs/profiles.

Modely:

- head sampling,
- tail sampling,
- probabilistic,
- rate limiting,
- error/latency-aware,
- tenant/service priority.

Sampling policy musí zachovať rare failures a high-value transactions. Sto percent success traces a nula percent chýb je zlá optimalizácia.

## 22. Retention a tiers

Rozličné signals potrebujú rozdielnu retention:

- high-resolution recent metrics,
- downsampled long-term metrics,
- hot searchable logs,
- archived audit logs,
- sampled traces,
- incident evidence s legal hold.

Retention má vychádzať z SLO, incident detection time, compliance a cost.

## 23. Observability cost

Cost drivers:

- ingestion,
- high cardinality,
- retention,
- indexing,
- queries,
- cross-Region/account transfer,
- custom metrics,
- trace volume,
- real-time logs,
- duplicate pipelines.

Cost optimalizácia musí zachovať kritické SLO, audit a incident evidence.

## 24. Security a privacy

Telemetry môže obsahovať:

- personal data,
- credentials,
- tokens,
- request payloads,
- database queries,
- internal topology,
- customer identifiers.

Potrebné controls:

- minimization a redaction,
- encryption,
- access control,
- tenant isolation,
- retention/deletion,
- audit,
- secure collectors/exporters,
- field allow/deny policy.

## 25. Observability maturity

Príklad progresie:

1. resource health a basic logs,
2. centralized metrics/logs,
3. actionable alerts a dashboards,
4. distributed tracing a correlation,
5. SLO/error-budget integration,
6. standardized instrumentation a platform,
7. continuous cost/quality governance,
8. automated bounded diagnosis/remediation.

Viac tools neznamená vyššiu maturity, ak signals nie sú korelované alebo owned.

## 26. Troubleshooting observability gapu

```text
chýba signal alebo je systém zdravý?
→ instrumentation aktívna?
→ context propagation?
→ agent/collector pipeline?
→ filtering/sampling?
→ backend ingestion/indexing?
→ query scope/time range?
→ cardinality/retention?
→ dashboard/alert correctness?
```

Zachovaj source configuration, collector metrics/logs, timestamps, sample trace IDs a backend ingestion evidence.

## 27. Anti-patterny

### Observability = kúpa platformy

Bez instrumentation, context a ownershipu platforma nevytvorí insight.

### Logovanie všetkého

Zvyšuje cost, noise a security risk.

### Dashboard pre každú metriku

Dashboard bez decision/action modelu vytvára vizuálny inventory.

### Alerts na infrastructure thresholds bez user impactu

Vedie k fatigue a nízkej priorite.

### Unbounded labels

Môžu destabilizovať telemetry pipeline.

### Tri oddelené stacks bez correlation

Incident responder manuálne spája čas, identity a deployments.

### Telemetry pipeline bez vlastného monitoringu

Strata dát vyzerá ako zdravý systém.

## 28. Kontrolné otázky

1. Aký je rozdiel medzi monitoringom a observability?
2. Čo je telemetry a ktoré hlavné signals poznáš?
3. Prečo metrics, logs a traces nie sú navzájom zameniteľné?
4. Ako funguje correlation a context propagation?
5. Čo je cardinality a prečo je riziková?
6. Ako sa líši white-box a black-box monitoring?
7. Prečo observability potrebuje SLO?
8. Kedy použiť sampling?
9. Ako zistíš, že zlyhala telemetry pipeline?
10. Prečo viac dát automaticky neznamená viac insightu?

## Glossary impact

Relevantné pojmy: monitoring, observability, telemetry, signal, instrumentation, metric, log, distributed trace, span, event, audit record, profile, context propagation, correlation ID, white-box monitoring, black-box monitoring, cardinality, sampling, telemetry pipeline, observability maturity a observability gap.

## Primárne zdroje

- [OpenTelemetry observability primer](https://opentelemetry.io/docs/concepts/observability-primer/)
- [OpenTelemetry signals](https://opentelemetry.io/docs/concepts/signals/)
- [OpenTelemetry instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/)
- [Prometheus overview](https://prometheus.io/docs/introduction/overview/)
- [Prometheus instrumentation practices](https://prometheus.io/docs/practices/instrumentation/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CloudOps troubleshooting drills](../11-cloud-and-aws/cloudops-troubleshooting-drills.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
