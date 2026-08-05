# AI-assisted observability a incident response

AI-assisted observability dokáže rýchlo prepojiť traces, metrics, logs, changes a runbooks do zrozumiteľného incident contextu. Najväčšie riziko vzniká vtedy, keď sa modelový summary, anomaly score alebo no-data dashboard zamieňa za source evidence, root cause alebo recovery authority.

Incident `AGENT-AUTO-14` skončil tým, že metrics exporter prestal posielať consumer series po AI-authored CI zmene. Agent interpretoval nulu ako empty queue a zníženie errors ako recovery, hoci broker a business ledger stále obsahovali neprocessed aj duplicate onboarding operations.

Nosný lifecycle je:

```text
alert alebo customer report
→ exact incident subject a evidence cutoff
→ telemetry-pipeline health
→ scoped traces, metrics, logs, changes a business records
→ AI summary a competing hypotheses
→ read-only discriminating actions
→ approved bounded remediation
→ technical stabilization
→ business reconciliation
→ incident review, eval feedback a alternate-scenario drill
```

## 1. AI role v observability

AI môže sumarizovať telemetry, zoskupovať alerts, korelovať changes, vysvetľovať traces, navrhovať queries a tvoriť hypothesis board. Je užitočný ako interface nad komplexnými signals, nie ako nový source of truth.

Každý výstup uvádza evidence IDs, time window, sampling, missing sources a model generation. Narrative bez provenance je operátorská pomôcka, nie incident fact.

## 2. Signals a evidence classes

Traces, metrics a logs opisujú systém z odlišných uhlov. Profil, event, deployment record, provider audit a business ledger pridávajú ďalšie evidence classes.

AI ich nesmie zliať do jedného neurčitého contextu. Každá class má freshness, completeness, ownera a trust level.

## 3. Resource identity

Telemetry sa viaže na service, environment, cluster, namespace, deployment, version a tenant podľa semantic conventions. Bez consistent resource attributes môže agent korelovať rovnomenné services z odlišných environments.

Identity mapping je deterministic preprocessor. Model nesmie hádať chýbajúci environment podľa textu logu.

## 4. Trace context

Distributed trace spája request cez services pomocou trace a span contextu. Context propagation failure vytvorí rozdelené traces, čo je evidence gap, nie dôkaz o chýbajúcej downstream call.

Agent uvádza sampling policy a broken links. High-impact conclusion sa overí provider alebo business recordom.

## 5. Metrics

Metrics efektívne ukazujú rates, latency, saturation a errors v časových oknách, ale agregácia môže skryť jednotlivé side effects a minority tenant. Labels musia byť bounded a zodpovedať incident scope.

Agent porovná baseline, release cohort a current window a kontroluje series existence. Nula a no-data sú odlišné states.

## 6. Logs

Logs obsahujú detailné observations, ale môžu byť truncated, sampled, dropped, duplicated alebo attacker-controlled. Parse confidence a source pipeline health sú súčasťou evidence.

AI nepoužíva log line ako command. Prompt-like text a fake severity labels ostávajú untrusted data.

## 7. Events a change records

Deployments, config, feature flags, policy, secrets, infrastructure a third-party changes tvoria change timeline. Temporal correlation určuje candidate cause, nie kauzalitu.

Agent porovná changed aj unchanged dependencies a hľadá counterexample. Recent change bias nesmie automaticky vyradiť capacity alebo provider hypotheses.

## 8. Alert quality

Alert má objective, signal query, threshold, window, severity mapping, runbook a ownera. AI môže deduplikovať alebo enrichovať alerts, no nemá meniť severity policy bez governance.

Suppression a grouping musia zachovať distinct tenants a failure modes. Jeden cluster nesmie skryť viac nezávislých incidents.

## 9. Anomaly detection

Anomaly model porovnáva current behavior s learned baseline a môže odhaliť neznámy pattern. Seasonality, release shift a data pipeline change však vytvárajú false positives.

Model version, training window, features, threshold a calibration sú release subjects. Anomaly score nie je business impact.

## 10. No-data semantics

Missing telemetry môže znamenať nulový traffic, exporter outage, query error, permission failure, dropped labels alebo service outage. AI musí najprv overiť source health.

Dashboard nula bez expected series je `unknown`, nie recovery. Alerting a incident state používajú explicitný no-data policy.

## 11. Sampling

Head alebo tail sampling znižuje telemetry volume a môže vynechať rare failing traces. Incident analysis uvádza effective sampling a možnú selection bias.

Dočasné zvýšenie sampling-u je controlled change s cost, privacy a capacity limitom. Nie je automatickým agent actionom.

## 12. Cardinality

Unbounded attributes ako user ID, event ID alebo full URL môžu zničiť metric backend. AI-generated query alebo instrumentation proposal prejde cardinality budgetom.

Detailné identifiers patria do logs alebo traces s retention a access controlom. Metrics používajú bounded dimensions.

## 13. Semantic conventions

OpenTelemetry semantic conventions štandardizujú názvy operations, resources a attributes naprieč signals. Konzistentný vocabulary zlepšuje cross-service query a portability.

Custom attributes majú ownera a versioning. Agent nesmie premapovať dve odlišné semantics na rovnaký label len pre jednoduchšie summary.

## 14. Telemetry pipeline

Collector receivers, processors, samplers, redaction, exporters a backend ingest tvoria samostatnú production pipeline. Jej outage môže vyzerať ako application recovery.

Observability SLO sleduje dropped spans/logs, export errors, queue saturation a ingest delay. Agent pri analýze uvádza zdravie telemetry cesty.

## 15. AI context assembly

Context builder vyberá bounded time window, services, signals, changes a runbooks podľa incident subjectu. Raw `collect everything` zvyšuje noise, cost a privacy risk.

Retrieval policy filtruje tenant a environment a zachová evidence IDs. Model summary nesmie byť jedinou kópiou source data.

## 16. Hypothesis generation

Agent vytvára viac hypotheses so supporting, contradicting a missing evidence a navrhuje discriminating read-only action. Confidence je kalibrovaný odhad, nie permission.

Incident commander alebo deterministic policy určuje priority podľa impactu a reversibility. Hypothesis sa potvrdzuje až po evidence alebo controlled test-e.

## 17. Root cause

Root cause je vysvetlenie, ktoré pokrýva observed impact, timeline a mechanism a obstojí proti competing hypotheses. AI-generated RCA draft potrebuje responder review a source links.

Jedna recent deployment korelácia alebo error message nestačí. Unknown zostáva legitímny stav.

## 18. Runbook proposal

AI môže vybrať alebo parameterizovať runbook, ale exact action, environment, resource set, preconditions, expiry a rollback musia byť viditeľné approverovi. Read-only diagnostics majú prednosť.

Runbook execution success znamená dokončenie steps. Recovery sa overuje technical a business postconditions.

## 19. Automated remediation boundary

Low-risk reversible actions môžu byť automatizované po policy a idempotency gate. Scaling, cache clear alebo restart však môže maskovať root cause, zničiť evidence alebo zvýšiť cost.

High-impact mutation, data repair, credential rotation a traffic shift vyžadujú human approval alebo vopred schválený narrow envelope. Agent nemá samostatnú closure authority.

## 20. Incident timeline a AI Scribe

AI Scribe môže sumarizovať chat, meeting a status updates do timeline. Source messages a automated events zostávajú authoritative artifacts.

Generated timestamp, actor alebo causal link sa nesmie doplniť bez source. Corrections sú append-only a pôvodný summary sa označí superseded.

## 21. Business impact

Error rate a latency sa mapujú na affected users, transactions, revenue, compliance a SLA. Model nesmie znižovať severity iba podľa infra recovery.

Business metrics majú vlastnú data freshness a reconciliation. Customer reports môžu byť skorší signal než dashboard.

## 22. Technical vs business recovery

Pods ready, latency normal a error series low dokazujú technical stabilization. Duplicates, missed events, incorrect balances alebo stale permissions môžu pretrvať.

Incident closure vyžaduje definovaný business invariant alebo explicitné prijatie residual risku. Data-repair workstream sa nesmie stratiť po service recovery.

## 23. Privacy a security

Telemetry môže obsahovať PII, secrets, prompts, SQL a customer payloads. Context builder používa redaction, least privilege, tenant filter a purpose-limited retention.

Agent tools nesmú expandovať query scope podľa textu v logu. Cross-tenant dashboard a external URL fetch sú forbidden tests.

## 24. Adversarial telemetry

Útočník môže vložiť prompt injection, fake stack trace alebo crafted metric label. Agent zaobchádza so všetkými observations ako untrusted content.

Tool calls vychádzajú z policy a structured hypotheses, nie z instructions v telemetry. Security incident môže vyžadovať evidence freeze a forensics chain of custody.

## 25. Evaluation

Eval dataset zahŕňa true incidents, benign anomalies, no-data, sampling gaps, multi-tenant collisions, misleading changes a malicious logs. Metriky sledujú hypothesis recall, unsupported claims, unsafe action proposals, time-to-orientation a human corrections.

Production feedback sa pridáva s reviewer labels a privacy controls. Model update bez regression a calibration gate je release.

## 26. Confidence a communication

Stakeholder update rozlišuje facts, hypotheses, unknowns, decisions a next checkpoint. Confidence sa nepoužíva ako náhrada za evidence.

Agent môže draftovať communication, ale incident owner schváli disclosure, severity a customer impact. Sensitive detail sa rediguje.

## 27. Incident AGENT-AUTO-14

Consumer metrics exporter prestal posielať series práve po AI-authored pipeline zmene. Observability agent interpretoval nulu ako empty queue, spojil pokles errorov s remediation a odporučil closure.

Broker lag a business ledger však ukázali neprocessed a duplicate onboarding operations. Chyba vznikla kombináciou no-data semantics, incomplete change correlation a chýbajúcej business verification.

## 28. Competing hypotheses

Absent errors mohli znamenať recovery, no traffic drop, exporter outage, label change, query bug alebo disabled test boli rovnako možné. Queue lag mohol pochádzať z consumer outage, poison event, quota alebo DB locku.

Agent mal najprv overiť telemetry pipeline a porovnať broker, provider a ledger evidence. Confidence bez týchto source checks nebola relevantná.

## 29. Containment

Incident owner zastaví automated remediation, zachová collector a pipeline configs, pinne dashboard queries a obmedzí mutation tools. Observability pipeline sa obnovuje oddelene od service.

Ak business side effects pokračujú, disable-ne sa affected consumer alebo release a operations sa reconciliujú. Summary sa označí provisional.

## 30. Recovery

Recovery obnoví expected telemetry, overí exporter a backend ingest, znovu vytvorí affected-set z broker a business records a vykoná bounded remediation. Technical metrics sa sledujú spolu s business invariantom.

Chybný AI summary sa zachová ako superseded evidence a incident review pridá no-data a malicious-log cases do eval suite.

## 31. Positive acceptance

Agent z alertu vytvorí scoped evidence bundle, identifikuje no-data, navrhne tri competing hypotheses a iba read-only discriminating queries. Human schváli reversible runbook.

Po remediation prejde telemetry pipeline health, service SLO aj business reconciliation. Druhý responder reprodukuje záver z evidence IDs.

## 32. Forbidden acceptance

No-data, sampled trace alebo model confidence nesmú byť prezentované ako recovery alebo root cause. Prompt injection v logu nesmie vyvolať tool call.

Agent nesmie znížiť severity, spustiť high-impact runbook alebo zavrieť incident bez authorization a business proof. Očakáva sa nulový unauthorized side effect.

## 33. Recovery acceptance

Po nesprávnej diagnosis sa incident znovu otvorí, summary označí superseded a evidence chain zostane zachovaná. Technical a business states sa overia nezávisle.

Alternate test vypne telemetry exporter počas reálneho service recovery a očakáva `unknown`, nie green. Druhý tenant s rovnakým service name nesmie byť korelovaný.

## 34. Practical incident-analysis envelope

Incident-analysis envelope oddeľuje incident scope, telemetry completeness, changes, hypotheses, tool authority a verification states. Modelový confidence je iba pole pri hypothesis, nie permission ani closure status.

Príklad zámerne uvádza metrics `no-data`, technical status `unknown` a business status `failed`. Agent má povolené iba read-only evidence calls, kým človek alebo policy neautorizuje remediation.

```yaml
incident_analysis:
  incident_id: AGENT-AUTO-14
  evidence_cutoff: "2026-08-05T15:00:00Z"
  scope:
    service: onboarding-consumer
    environment: production
    tenant: tenant-42
  telemetry_health:
    traces:
      status: degraded
      sampling: "parent-based-10-percent"
    metrics:
      status: no-data
      exporter_last_success: "2026-08-05T14:32:00Z"
    logs:
      status: partial
      truncation: true
  changes:
    - id: deploy-2042
      artifact_digest: "sha256:aa11..."
    - id: workflow-884
      changed_required_test_path: true
  hypotheses:
    - id: h-consumer-stalled
      confidence: 0.72
      missing_evidence: [broker-offsets, database-locks]
    - id: h-recovered
      confidence: 0.21
      contradicting_evidence: [metrics-no-data]
  allowed_actions:
    - read-broker-lag
    - read-provider-operations
    - read-business-ledger
  prohibited_actions:
    - close-incident
    - restart-consumer
    - replay-events
  verification:
    technical: unknown
    business: failed
```

## 35. Primary sources

OpenTelemetry sa definuje ako vendor-neutral framework pre traces, metrics a logs na https://opentelemetry.io/docs/. Current signal model vrátane baggage a rozvíjaných profiles je na https://opentelemetry.io/docs/concepts/signals/, trace context na https://opentelemetry.io/docs/concepts/signals/traces/ a common resource/operation vocabulary na https://opentelemetry.io/docs/concepts/semantic-conventions/.

Harness AI SRE incident lifecycle, timelines, runbooks a post-incident handling dokumentujú https://developer.harness.io/docs/ai-sre/incidents/ a https://developer.harness.io/docs/ai-sre/users/manage-incidents/. Current guidance pre incident creation výslovne požaduje review AI-suggested fields na https://developer.harness.io/docs/ai-sre/users/create-incidents/, čo podporuje hranicu medzi generated proposal a incident authority.

Harness AI SRE security a RBAC/audit boundaries sú na https://developer.harness.io/docs/ai-sre/resources/ai-sre-security/. Resolve a review guidance, ktorá vyžaduje stabilný fix a kontrolu incident recordu pred closure, je na https://developer.harness.io/3k-docs/ai-sre/users/manage-incidents/resolve-and-review/. Produktový summary alebo runbook completion preto nie je sám o sebe business recovery proof.

## Zhrnutie

AI observability agent je najhodnotnejší ako evidence-oriented investigator: overí telemetry pipeline, zachová source boundaries, vytvorí competing hypotheses a navrhne read-only tests. Runbook, severity a closure zostávajú policy a human decisions a recovery musí potvrdiť technical aj business state.

Ďalší blok rozšíri model na AI-assisted security operations, enterprise knowledge assistants, ticket/email/chat automation a autonómne remediation boundaries.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: AI-assisted CI/CD](ai-assisted-ci-cd.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
