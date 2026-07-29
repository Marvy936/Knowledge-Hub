# Instrumentation a telemetry

Instrumentation je production mechanismus, ktorý rozhoduje, ktoré system occurrences sa zmenia na telemetry records, s akou identitou, semantics a failure behavior. Telemetry je výsledok tohto mechanizmu a jeho ďalšieho delivery/processing lifecycle-u. Collector ani backend nedokážu spätne doplniť business meaning, ktorý producer nikdy nevytvoril.

Preto sa instrumentation navrhuje od business a operational questions smerom k observation points. Nie od zoznamu dostupných agentov alebo dashboardov smerom k náhodným dátam.

## 1. Dominantný lifecycle

```text
business outcome a investigation otázky
→ exact operation a failure-boundary inventory
→ telemetry requirements a authority
→ instrumentation generation
→ code-based, zero-code a platform observation points
→ resource, instrumentation-scope a context identity
→ local SDK/agent processing a bounded buffering
→ collector topology, policy a routing generation
→ sampling, filtering, redaction a enrichment
→ export, ingestion a consumer compatibility
→ coverage, overhead, privacy a failure-behavior validation
→ rollout, loaded-state verification a rollback
→ telemetry acceptance a retirement
```

Tento lifecycle oddeľuje:

```text
instrumentation je nakonfigurovaná
≠ instrumentation je načítaná
≠ record bol vytvorený
≠ record bol exportovaný
≠ backend ho ingestoval
≠ dashboard alebo alert používa správnu generation
```

## 2. Exact instrumentation subject

Pre Atlas Payments používame:

```text
instrumentation subject: INS-PAY-43
business capability: CAP-PAY-42
observed journey: enterprise payment settlement
release generation: 7.19.0
instrumentation generation: OTEL-PAY-12
semantic-convention selection: SEMCONV-PAY-5
collector agent config: COL-AGENT-18
collector gateway config: COL-GW-22
backend route generation: OBS-ROUTE-9
environment: production
Regions/AZs: eu-central-1 / two AZ cohorts
```

Subject musí zahŕňať producer release aj telemetry configuration. Rovnaký application artifact môže pri inom agentovi, resource detectori, sampling policy alebo collector route produkovať odlišný evidence model.

## 3. Requirements vznikajú z journey a failure modelu

Najprv definuj, ktoré decisions má telemetry podporiť. Pre settlement journey:

```text
Je final settlement úspešný a v SLO?
Ktorý cohort alebo release zlyháva?
Kde vzniká latency?
Koľko provider attempts vykonala jedna logical operation?
Bol ledger commit durable?
Stratila sa queue acknowledgement alebo context?
Ktorá config generation bola skutočne načítaná?
```

Z týchto otázok vzniká expected evidence inventory:

- logical-operation counters a duration distribution;
- provider-attempt metrics oddelené od logical outcomes;
- server, messaging, provider a ledger spans;
- structured final-outcome a error events;
- release/configuration/resource identity;
- context propagation cez HTTP, queue a worker;
- telemetry canary a collector self-telemetry.

Infrastructure telemetry zostáva dôležitá, ale nevie sama určiť success business transactionu.

## 4. Observation points a authority

Jedna operation môže byť pozorovaná na viacerých boundaries:

```text
client
→ edge/proxy
→ application handler
→ queue producer
→ consumer
→ provider client
→ database/ledger
→ business reconciler
```

Každá boundary vidí inú časť reality. Client vidí end-to-end outcome, server handler vlastné spracovanie, provider client technical attempt a ledger durable state transition. Instrumentation contract určuje, ktorý observation point je autoritatívny pre konkrétny numerator, denominator alebo duration.

Duplicitné observation points sa nesmú bez identity sčítať. Edge a application counters môžu merať rovnaký request z dvoch perspektív, nie dve business operations.

## 5. Code-based instrumentation

Code-based instrumentation používa explicitné APIs a SDKs. Je potrebná tam, kde iba application pozná business semantics:

- začiatok a final outcome logical operation;
- idempotency alebo reconciliation result;
- partial success;
- fallback považovaný za degraded outcome;
- domain-safe bounded attributes;
- custom async links;
- loaded config alebo feature generation.

Library by mala závisieť primárne na OpenTelemetry API, nie vynucovať konkrétny SDK a exporter. Runnable service konfiguruje SDK, sampling, processors a export podľa environmentu.

Code-based instrumentation prináša presnosť, ale je súčasťou application change-u. Potrebuje code review, schema test, overhead benchmark, compatibility window a rollout.

## 6. Zero-code a automatic instrumentation

Zero-code instrumentation pridáva API/SDK behavior agentom alebo agent-like mechanizmom bez úpravy source code. Podľa language/runtime môže používať bytecode injection, monkey patching, runtime hooks alebo eBPF.

Typicky pozoruje edges application:

- inbound/outbound HTTP a RPC;
- database a messaging libraries;
- runtime metrics;
- common framework operations;
- standard context propagation.

Nepozná však automaticky business completion, correct denominator, idempotency outcome ani custom protocol. Preto automatic baseline a code-based business instrumentation tvoria komplementárny model, nie alternatívy.

Zero-code generation musí byť version-pinned a testovaná proti runtime/library versions. Agent upgrade môže zmeniť operation names, captured attributes, overhead alebo semantic-convention generation aj bez application source diffu.

## 7. Platform telemetry

Cloud service, load balancer, Kubernetes, service mesh, database, runtime alebo kernel môže emitovať telemetry nezávisle od application instrumentation. Platform signal pomáha pri route, capacity, scheduling, network a service-state mechanizmoch.

Healthy target alebo successful control-plane update však nepreukazuje final business outcome. Platform evidence sa koreluje s application a client observation, nie používa ako univerzálny oracle.

## 8. Resource identity

Resource opisuje observed entity. Logical service identity musí byť stabilná cez restart, scaling a Pod replacement:

```text
service.name = provider-adapter
service.version = 7.19.0
deployment.environment.name = production
cloud.region = eu-central-1
cloud.availability_zone = eu-central-1b
k8s.cluster.name = atlas-prod
k8s.namespace.name = payments
k8s.pod.name = ephemeral instance identity
```

`service.name` nesmie byť nahradený Pod name, hostname alebo container ID. Ephemeral identity patrí do samostatného attribute-u. Inak sa logical service rozpadne na množstvo pseudo-services, dashboards stratia continuity a cardinality rastie s churnom.

Resource merge a detector precedence sú preto change contract. Over effective records po všetkých processors, nie iba application environment variables.

## 9. Instrumentation scope

Instrumentation scope identifikuje logical library alebo component, ktorý record vytvoril. Typicky obsahuje name a version a môže niesť schema URL.

Pomáha odlíšiť:

- application-owned settlement instrumentation;
- HTTP framework instrumentation;
- database client library;
- messaging instrumentation;
- automatic agent generation.

Pri telemetry regresii možno zistiť, či chybný span name alebo attribute vytvorila application, framework alebo konkrétna agent version. Scope nie je resource identity: library, ktorá meria `provider-adapter`, nie je samotná service.

## 10. Semantic conventions ako versionovaný contract

Semantic conventions štandardizujú span names, metric instruments, units, attributes, events a entity/resource semantics. Aktuálny OpenTelemetry model používa per-group maturity levels ako development, alpha, beta, release candidate a stable. Jednotlivé domains môžu mať zmiešanú stabilitu.

Preto nestačí povedať „používame OpenTelemetry conventions“. Eviduj:

```text
convention domain a version
→ stability status
→ instrumentation default/opt-in behavior
→ emitted old/new/dual schema
→ consumer compatibility
→ retirement plan
```

Pri migration môže byť potrebný dual emit alebo compatibility query window. Metric rename, unit change alebo operation-name transition bez consumer inventory môže vytvoriť false no-data alert aj keď producer funguje.

## 11. Context propagation

Context propagation prenáša trace identity a sampling decision cez protocol boundaries. HTTP používa headers, gRPC metadata, messaging headers/properties a batch/async workflows môžu potrebovať span links.

```text
HTTP request context
→ queue publish context
→ message metadata
→ consumer extraction
→ linked processing span
→ provider call
→ ledger commit
```

Prerušenie propagation neznamená vždy stratu samotnej operation. Znamená stratu causal continuity v trace. Responder potom vidí viac unrelated trace fragments a môže nesprávne vyhodnotiť latency alebo retries.

Baggage je propagovaný contextual key/value model, nie secret store ani univerzálny payload. Potrebuje allowlist, size limit, trust-boundary stripping a zákaz sensitive alebo unbounded values.

## 12. Local SDK a agent failure behavior

Instrumentation beží v business process-e alebo tesne vedľa neho, preto môže ovplyvniť request latency, allocations, startup, thread contention a memory.

Production contract musí určiť:

- synchronous alebo asynchronous export;
- batch size a flush interval;
- memory queue a max age;
- retry policy;
- shutdown flush behavior;
- čo sa stane pri exporter/backend outage;
- či telemetry môže blokovať business thread.

Default bezpečnostný cieľ je bounded failure. Telemetry loss môže byť vážny operational incident, ale nemá nekontrolovane vyčerpať application memory alebo zastaviť settlement processing.

## 13. Collector topology

OpenTelemetry Collector môže byť nasadený ako agent, sidecar, gateway alebo tiered kombinácia.

### Agent pattern

Agent beží pri workload-e alebo na Node-e. Poskytuje local endpoint, host/container metadata a distribuuje collection load. Je vhodný na local buffering a source-near redaction.

### Sidecar pattern

Sidecar poskytuje application-specific isolation, ale násobí resource a configuration footprint. Pri stovkách Pods môže zvýšiť cost a drift.

### Gateway pattern

Gateway centralizuje policy, backend fan-out, tenant routing a stateful processing. Zároveň vytvára shared capacity a failure boundary. Potrebuje HA, load model, queue limits a per-signal routing.

Stateful functions ako tail sampling potrebujú trace affinity. Náhodné rozdelenie spans jedného trace-u medzi nezávislé gateways vytvorí incomplete decision state.

## 14. Receivers, processors a exporters

Collector pipeline je explicitný directed path:

```text
receiver
→ ordered processors
→ exporter
```

Receiver acceptance nepreukazuje exporter success. Processor môže record zmeniť, zahodiť, rozdeliť alebo routovať inam. Export success nepreukazuje backend query visibility, ak ingestion/indexing ešte zlyhá alebo laguje.

Processors môžu vykonávať batching, memory limiting, filtering, redaction, resource enrichment, transformation, routing a sampling. Ich poradie je semantics. Redaction po exporter fan-out je neskoro; resource overwrite po enrichment môže zničiť stable identity.

Collector nie je automaticky durable broker. Memory queue, persistent queue alebo retry komponenty majú konkrétny capacity a loss contract, ktorý treba testovať.

## 15. Sampling, filtering a views

Sampling a filtering znižujú volume a cost, ale menia evidence coverage. Každá policy potrebuje:

```text
input records
→ match/decision reason
→ kept, transformed alebo dropped count
→ affected signal/use case
→ owner a version
```

Nesmie bez explicitného decisionu odstrániť SLO numerator/denominator, rare errors, high-latency traces, audit/security events alebo final business failures.

Metrics views a attribute processors sú vhodné na bounded cardinality a unit/aggregation control. Musia však byť versionované a porovnané s dashboard, alert a recording-rule consumers.

## 16. Privacy a security boundaries

Instrumentation môže zachytiť authorization headers, cookies, tokens, database statements, request bodies, file paths, user identifiers, prompts alebo internal topology.

Controls musia fungovať pred uložením:

- producer-side minimization;
- attribute allowlist;
- source-near redaction;
- TLS a authenticated export;
- least-privilege collector identity;
- tenant isolation;
- data residency;
- retention/deletion;
- audit pre telemetry access a policy changes.

Redaction iba v dashboarde je presentation filter, nie data-protection control.

## 17. Telemetry self-observability

Každý SDK/agent/collector/backend path potrebuje vlastné signals:

```text
accepted records
refused records
dropped records podľa reason
queue size/capacity
retry count a max age
export failures
batch latency
CPU/memory/disk
config reload generation
backend ingestion lag
end-to-end canary freshness
```

Bez end-to-end canary môže byť každý component lokálne green a signal sa napriek tomu nedostane do query alebo alertu.

## 18. Instrumentation migration a release acceptance

Telemetry schema a identity sú production interfaces. Migration prebieha podobne ako API change:

```text
consumer inventory
→ new generation design
→ compatibility/dual-write window
→ canary emission
→ backend read-back
→ dashboard/rule/query tests
→ overhead a cardinality validation
→ bounded rollout
→ old generation retirement
```

Loaded-state verification je kritická. IaC alebo environment variable môže deklarovať novú generation, ale long-lived process, sidecar alebo collector stále používa starú config.

## 19. Worked failure: stable service identity prepísaná Pod menom

### Exact subject

```text
INS-PAY-43
application release: 7.19.0
instrumentation generation: OTEL-PAY-12
agent config: COL-AGENT-18
gateway config: COL-GW-22
resource processor change: RP-7
expected service.name: provider-adapter
affected cohort: new Pods after 09:05 UTC
```

### Symptom

Po collector rollout-e dashboard `provider-adapter` ukazuje partial no-data. Alerting rule pre service error rate prestane vidieť nové Pods. Trace backend súčasne zobrazuje desiatky nových „services“ s názvami podobnými Pod names.

Business traffic stále prechádza a exporters nehlásia failures.

### Competing hypotheses

1. application SDK sa nenačítal v nových Pods;
2. OTLP traffic blokuje network alebo authentication;
3. agent prijíma records, ale gateway ich filtruje;
4. backend tenant alebo query scope je nesprávny;
5. resource detector/processor prepísal stable service identity;
6. semantic-convention migration zmenila service attribute name;
7. dashboard používa stale data-source generation.

### Discriminating observations

```text
application SDK startup/resource dump
→ raw OTLP record pri agent receiveri
→ record po resource processors
→ gateway accepted/exported counters
→ backend service.name distribution
→ collector config generation a processor order
```

Evidence ukáže:

- application emituje `service.name=provider-adapter`;
- agent receiver record prijme správne;
- processor `RP-7` mapuje `k8s.pod.name` do `service.name` s overwrite semantics;
- exporter a backend fungujú;
- backend preto indexuje `provider-adapter-7f9...` ako nové logical services;
- alert query na exact `service.name="provider-adapter"` nové records nevidí;
- ephemeral service identity zvyšuje cardinality a rozbíja service graph continuity.

Root cause je resource-processing generation, nie exporter outage. Local component health bol green, ale effective telemetry identity bola chybná.

### Evidence-preserving containment

- zastaviť collector/config rollout;
- zachovať raw receiver sample a post-processor sample;
- dočasne rozšíriť investigation query o affected Pod-name pattern, nie však SLO contract;
- neprepájať paging rule na unbounded Pod identities ako permanentný fix;
- nedovoliť telemetry exportu blokovať business traffic.

### Authoritative recovery

1. vrátiť `service.name` na application-owned stable logical identity;
2. ponechať `k8s.pod.name` ako instance attribute;
3. pridať processor policy, ktorá stable service name neprepisuje;
4. vykonať canary emission cez agent, gateway a backend read-back;
5. overiť dashboard, alert, trace service graph a log correlation;
6. rollout-nuť po bounded cohortách;
7. odstrániť ephemeral pseudo-services až po retention a query-impact analýze.

### Acceptance verdict

- všetky current Pods reportujú stable `service.name=provider-adapter`;
- Pod identity zostáva dostupná samostatne;
- new telemetry je viditeľná v metric, trace aj log backendoch;
- alert rule pre controlled error canary fire-ne a recover-ne;
- service count a cardinality sa vrátia do budgetu;
- forbidden overwrite sa pri config regression test-e odmietne;
- žiadny sensitive alebo raw business identifier sa nepridal do resource attributes;
- second collector restart zachová rovnakú effective identity.

### Earlier controls

- golden telemetry fixture pred/po processors;
- policy test nad required a forbidden resource attributes;
- end-to-end metric/log/trace canary;
- consumer inventory pre identity/schema changes;
- loaded collector config generation v self-telemetry;
- canary a rollback pre agent/gateway upgrades;
- cardinality budget alert podľa service identity churnu.

## 20. Troubleshooting instrumentation gapu

```text
správny release a process?
→ SDK/agent skutočne načítaný?
→ expected instrumentation scope/version?
→ raw producer record?
→ resource merge a detector precedence?
→ context injection/extraction?
→ sampling/filtering/view decision?
→ local queue a exporter?
→ collector receiver/pipeline route?
→ backend tenant/schema/time range?
→ consumer query používa current generation?
```

Pri každom observation point-e zachovaj sample record a config generation. Reštart alebo broad debug logging bez bounded planu môže odstrániť state, zvýšiť cost a leak-nuť sensitive values.

## 21. Anti-patterny

### Auto-instrumentation je hotová observability

Agent pozná protocol a library edges, nie final business semantics.

### Stable service identity odvodená z Pod name

Logical service sa rozpadne pri každom scalingu alebo restart-e.

### Semantic conventions bez version/stability evidence

Mixed-stability domains môžu meniť schema a consumer contract.

### Collector ako neobmedzený buffer

Backend outage vyčerpá memory alebo disk a môže zasiahnuť workload.

### Export success ako backend visibility verdict

Ingestion, indexing, tenant routing alebo query môžu stále zlyhať.

### Telemetry failure blokuje business operation

Observability dependency sa zmení na príčinu produkčného outage-u.

### Redaction iba v UI

Sensitive record už prešiel exportom a storage-om.

### Configured generation ako loaded-state dôkaz

Long-lived process alebo collector môže stále používať starú effective config.

## 22. Kontrolné otázky

1. Aký je rozdiel medzi instrumentation generation a telemetry recordom?
2. Prečo requirements vznikajú z business journey a failure modelu?
3. Kedy je code-based instrumentation nenahraditeľná?
4. Čo zero-code instrumentation typicky pozoruje a čo nevie?
5. Ako sa líši resource identity a instrumentation scope?
6. Prečo semantic conventions potrebujú version a stability contract?
7. Čo sa stane pri prerušenej context propagation?
8. Kedy použiť agent, sidecar alebo gateway topology?
9. Prečo processor order mení telemetry semantics?
10. Aký acceptance verdict uzavrel incident `INS-PAY-43`?

## Glossary impact

Relevantné pojmy: instrumentation subject, telemetry requirement inventory, observation-point authority, instrumentation generation, loaded instrumentation state, resource merge precedence, stable service identity, semantic-convention generation, collector topology generation, processor-order contract, bounded telemetry failure, telemetry read-back test, instrumentation acceptance verdict a telemetry generation retirement.

## Primárne zdroje

- [OpenTelemetry instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/)
- [OpenTelemetry zero-code instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/zero-code/)
- [OpenTelemetry code-based instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/code-based/)
- [OpenTelemetry Collector deployment patterns](https://opentelemetry.io/docs/collector/deploy/)
- [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/)
- [Prometheus instrumentation practices](https://prometheus.io/docs/practices/instrumentation/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Metrics, logs, traces a events](metrics-logs-traces-events.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: RED method →](red-method.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
