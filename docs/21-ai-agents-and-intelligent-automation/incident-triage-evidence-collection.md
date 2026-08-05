# Incident triage a evidence collection

Agentický incident responder môže korelovať alerts, deployments, logs, traces, tickets a runbooks, sumarizovať timeline a navrhovať hypotheses. Nesmie však meniť neúplnú telemetry na fakt, model confidence na severity authority ani runbook execution na potvrdenú recovery.

Incident `AGENT-DELIVERY-12` vyvrcholil po zelenom CI a `Synced` GitOps stave. Alert ukazoval zvýšené duplicate charges iba v jednej route. Triage agent použil orezané deployment logs, nevidel prvotný race error a pripísal incident cache latency. Po rescale sa latency znížila a agent odporučil incident uzavrieť, hoci duplicate-charge reconciliation nebola vykonaná.

Nosný lifecycle je:

```text
alert alebo report
→ incident identity, severity a ownership
→ immutable evidence snapshot
→ timeline a change correlation
→ competing hypotheses
→ read-only diagnostic actions
→ containment proposal a approval
→ bounded remediation
→ technical a business verification
→ evidence-preserving recovery
→ post-incident review a second-scenario acceptance
```

## 1. Incident subject

Incident má stable ID, service, environment, start window, severity, commander a affected business capability. Related alerts a tickets sa linkujú, ale nezamieňajú za jeden event bez correlation evidence.

Agent vždy uvádza exact incident a evidence cutoff. Summary bez časovej hranice môže miešať stav pred a po remediation.

## 2. Declaration a acknowledgment

AI môže navrhnúť incident fields z popisu, no človek alebo deterministic policy potvrdí severity a ownership. Harness AI SRE dokumentácia odporúča generated fields reviewovať.

Acknowledgment znamená, že responder prevzal koordináciu a zastavil escalation na danej úrovni. Neznamená potvrdenie príčiny ani mitigácie.

## 3. Impact assessment

Prvé minúty určujú affected services, users, geography, revenue, compliance a SLA. Technical error rate bez business contextu nemusí zodpovedať severity.

Agent používa authoritative business metrics a customer reports. Model nesmie znižovať severity iba preto, že infra dashboard je zelený.

## 4. Incident timeline

Timeline uchováva alerts, deployments, feature flags, commands, approvals, runbooks a status changes s timestampom a actorom. Automated activity sa označuje ako automated.

Generated narrative je view nad events. Source events zostávajú immutable alebo append-only evidence.

## 5. Evidence classes

Evidence sa delí na configuration, execution, telemetry, provider, business a human decision. Každá class má ownera, retention a trust level.

Log line je observation; deployment commit je declared change; provider read-back je effective state. Agent ich nesmie zlúčiť do jednej neurčitej „platform evidence“.

## 6. Collection plan

Pred širokým zberom sa definuje question, source, time window a expected discriminating value. Tým sa obmedzí privacy exposure a noise.

Agent nepoužíva `collect everything` ako default. High-cardinality dumps môžu zničiť incident store alebo prekročiť retention a access policy.

## 7. Time synchronization

Correlation vyžaduje UTC timestamps, clock-skew awareness a ingestion delay. Event time a observation time sú rozdielne fields.

Agent nesmie vyhlásiť poradie udalostí z UI sortu, ak sources majú rozdielne clocks. Evidence record uchová oba časy.

## 8. Logs

Logs poskytujú application a platform observations, ale môžu byť sampled, truncated, dropped alebo redacted. Harness dokumentácia uvádza limits a truncation behavior.

Zber zaznamená query, source, time window, completeness a checksum exportu. Chýbajúca line v orezanom logu nie je negatívny dôkaz.

## 9. Metrics

Metrics agregujú behavior v intervaloch a môžu skryť jednotlivé side effects. Labels a aggregation musia zodpovedať tenant, route a release cohort.

Agent porovná baseline, canary a current window a kontroluje no-data. Pri absent series sa result označí unknown.

## 10. Traces

Trace spája distributed operations cez trace a span IDs. OpenTelemetry umožňuje correlovať logs s traces pomocou TraceId, SpanId a resource contextu.

Sampling môže odstrániť failing trace. Agent uvádza sampling policy a nepovažuje chýbajúci span za nevykonanú operáciu.

## 11. Change events

Deployments, pipeline executions, config, secrets, feature flags a infrastructure changes sú candidate causes. Harness AI SRE koreluje change events z viacerých sources.

Correlation určuje časovú a topologickú blízkosť, nie kauzalitu. Competing unchanged dependencies zostávajú v hypothesis set-e.

## 12. Git a release evidence

Incident bundle viaže source commit, manifest commit, artifact digest, GitOps sync a live resource versions. Branch alebo tag bez resolution je nedostatočný.

Agent kontroluje, či všetky replicas skutočne používajú rovnaký digest. Mixed rollout môže vysvetliť partial impact.

## 13. Pipeline evidence

Execution ID, resolved pipeline revision, inputs, step statuses, logs a outputs identifikujú delivery path. Green conclusion sa rozloží na jednotlivé gates a skipped paths.

Agent explicitne hľadá skipped verification, ignored failure a missing artifact output. Summary pipeline runu nie je úplná execution proof.

## 14. External provider evidence

Cloud, payment, identity alebo messaging provider môže potvrdiť operation reference, effective state a čas spracovania. Provider log sa viaže stable business operation key, tenant a exact downstream principal.

Timeout klienta vytvára unknown outcome, nie failed operation. Reconciliation cez provider API alebo ledger má prednosť pred retry, ktorý by mohol side effect zopakovať.

## 15. Business evidence

User-facing synthetic transaction, ledger count, order state alebo payment reconciliation uzatvára business outcome. CPU a pod readiness sú iba supporting signals.

Incident sa neuzatvára, kým business invariant nie je obnovený v definovanom window-e alebo kým owner explicitne neprijme residual risk.

## 16. Privacy a access

Incident evidence môže obsahovať PII, secrets a customer payload. Agent používa least-privilege connectors, redaction a purpose-limited storage.

Raw evidence a shareable summary sú oddelené. Prompt alebo ticket nesmie dostať viac dát než je potrebné.

## 17. Chain of custody

Critical export obsahuje source, collector identity, timestamp, query, checksum, classification a storage location. Transformácie zachovajú origin, parent digest a informáciu o redaction alebo sampling-u.

Agent-generated summary odkazuje na evidence IDs a nesmie meniť source artifact. Ručne skopírovaný fragment bez originu alebo completeness metadata má nižšiu trust class.

## 18. Hypothesis board

Triage vytvorí viac hypotheses so supporting, contradicting a missing evidence, affected boundaries a expected observable consequences. Každá má confidence, ownera a next discriminating action.

Najvyššia confidence nie je automatická pravda ani povolenie na mutation. Incident commander rozhoduje o prioritách a containment podľa impactu, reversibility a nákladov omylu.

## 19. Counterfactual tests

Hypothesis sa posilní, keď controlled change odstráni symptom pri zachovaní ostatných conditions. V produkcii sa preferuje safe canary alebo replay.

Agent nesmie vykonať destructive experiment bez approval. Observed improvement po rescale môže byť coincidence alebo dočasná maska.

## 20. Read-only diagnostics

Prvá agent capability je čítanie statusov, logs, metrics, Git diffs a provider records. Tool allowlist obmedzí namespaces, accounts a time windows.

Read-only label musí zodpovedať reálnemu behavioru. Query tool nesmie podporovať hidden mutation alebo unrestricted network.

## 21. Containment proposal

Containment znižuje impact bez potreby úplnej root cause: stop promotion, disable mutation tool, route traffic, suspend reconciliation alebo freeze feature.

Proposal obsahuje expected effect, blast radius, rollback a evidence to watch. High-risk containment vyžaduje human approval.

## 22. Runbooks

Harness incident lifecycle môže attachovať a executeovať runbooks. Runbook je versioned automation s inputs, ownerom, preconditions a postconditions.

Successful runbook execution znamená, že steps skončili podľa engine-u. Recovery musí potvrdiť technical a business postconditions.

## 23. Approval a separation of duties

Agent môže navrhnúť remediation, ale incident commander alebo authorized responder schváli exact action envelope. Approval má expiry a environment binding.

Agent, ktorý klasifikoval evidence, nemá sám uzavrieť incident po vlastnom remediation. Independent verification znižuje confirmation bias.

## 24. Idempotency

Incident actions používajú stable operation ID, atomic state transition a provider-native idempotency. Retry notification, runbook alebo pipeline nesmie zopakovať side effect ani vytvoriť paralelný recovery path.

Unknown action sa quarantinuje a reconciliuje proti authoritative provider state. Timeline oddeľuje request, jednotlivé attempts, acknowledgment a confirmed effect.

## 25. Severity changes

Severity sa mení podľa aktuálneho business impactu, affected scope a incident policy, nie podľa model sentimentu alebo počtu alertov. Každá zmena má actor, timestamp, evidence cutoff a justification.

Zníženie severity neukončuje investigation ani data-repair workstream. Residual customer harm, compliance notification a reconciliation môžu pokračovať po technical mitigation.

## 26. Technical mitigation

Technical mitigation môže obnoviť latency, availability alebo error rate. Window musí byť dostatočne dlhé a porovnané s baseline.

Jedna green datapoint nestačí. Monitoring source health a no-data status sa overia, aby outage observability nevyzeral ako recovery.

## 27. Business reconciliation

Pre duplicates, missed events alebo partial writes sa vytvorí authoritative affected-set a repair plan. Reconciliation je často oddelená od service recovery.

Incident `AGENT-DELIVERY-12` sa nemohol uzavrieť iba po rescale. Bolo potrebné identifikovať všetky duplicate charges a potvrdiť refunds alebo reversals.

## 28. Evidence freeze

Pred destructive cleanup, rollback, pod replacementom alebo retention expiry sa uloží minimálny evidence bundle s queries, exports a checksums. Zároveň sa neodkladá urgentné containment, ak impact pokračuje.

Freeze je risk-based, časovo ohraničený a podľa možnosti automatizovaný. Neznamená nekonečné kopírovanie citlivých dát ani plošné obchádzanie retention policy.

## 29. AI summary

AI summary zrýchľuje responder handoff, shift change a stakeholder update. Obsahuje facts, hypotheses, decisions, unknowns, rejected explanations a next actions v oddelených sekciách.

Model nesmie doplniť chýbajúci timestamp, actor ani causal link. Každé load-bearing tvrdenie odkazuje na evidence ID a uvádza freshness alebo completeness limit.

## 30. Communication

Public alebo executive update používa overené facts, impact range a next checkpoint. Internal hypotheses sa neprezentujú ako root cause.

Agent môže draftovať text, ale incident owner schvaľuje obsah a disclosure. Sensitive customer alebo security detail sa rediguje.

## 31. Resolve a review

Harness incident lifecycle zahŕňa resolve, AI Scribe outputs, action items a post-incident learning. Resolve status sa nastaví po obnove a agreed verification.

RCA môže zostať otvorená po mitigation, ale musí mať ownera a deadline. Incident closure nesmie odstrániť unresolved data-repair task.

## 32. Positive acceptance

Test vytvorí incident z alertu, agent zhromaždí bounded evidence, vytvorí competing hypotheses a navrhne read-only discriminating action. Authorized containment zníži impact.

Technical a business verification prejdú, timeline zachová source events a druhý responder reprodukuje záver z evidence IDs.

## 33. Forbidden acceptance

Test vloží prompt injection do logu alebo ticketu, ponúkne cross-tenant dashboard, incomplete log alebo no-data metric. Agent nesmie exfiltrovať data ani označiť absent evidence za recovery.

Mutation bez approvalu a incident closure bez business reconciliation sú blocked. Očakáva sa nulový unauthorized side effect.

## 34. Recovery acceptance

Po nesprávnej agent diagnosis sa summary označí superseded, evidence zostane zachovaná a hypothesis board sa obnoví. Chybná remediation sa rollbackne alebo opraví podľa provider state.

Incident sa znovu overí na technical aj business layer a alternate scenario testuje susedný service alebo cohort. Action items zachytia control failure, nie iba prompt wording.

## 35. Practical evidence index

Evidence index je append-only mapa medzi incident subjectom, evidence cutoffom, source artifacts, completeness limits, hypotheses a resolution states. Udržiava rozdiel medzi technical mitigation a business reconciliation a umožňuje druhému responderovi reprodukovať záver bez spoliehania sa na modelový summary text.

Nasledujúci príklad zámerne ponecháva `business_verified: false`, hoci technical verification prešla. Tým demonštruje, že incident nesmie byť uzavretý iba na základe zlepšených infra metrík alebo úspešného runbooku.

```yaml
incident:
  id: AGENT-DELIVERY-12
  severity: P1
  service: payments
  environment: prod
  evidence_cutoff: 2026-08-05T12:00:00Z
  evidence:
    - id: ev-release
      type: release-manifest
      digest: sha256:aa11...
    - id: ev-pipeline
      type: pipeline-execution
      execution_id: exec-1042
      completeness: partial-logs
    - id: ev-trace
      type: trace-export
      sampling: parent-based-10-percent
    - id: ev-ledger
      type: business-reconciliation
      completeness: complete
  hypotheses:
    - id: h-race
      status: confirmed
      supporting: [ev-trace, ev-ledger]
    - id: h-cache
      status: rejected
  resolution:
    technical_verified: true
    business_verified: false
```

Index zabraňuje, aby `technical_verified` automaticky znamenalo resolved. Business evidence musí byť doplnená pred closure.

## 36. Primary sources

Harness AI SRE dokumentácia opisuje acknowledgment, triage, impact assessment, timeline, runbooks, action items a incident review. Harness Continuous Verification dokumentácia opisuje log/metric analysis, no-data a retention. OpenTelemetry definuje correlation logs a traces cez execution a resource context.

Harness incident lifecycle, ownership, timelines, runbooks, actions a review je popísaný na https://developer.harness.io/docs/ai-sre/users/manage-incidents/. Acknowledge a triage semantics, vrátane review generated fields a impact assessment, rozvíja https://developer.harness.io/docs/ai-sre/users/manage-incidents/acknowledge-and-triage/, zatiaľ čo širší AI SRE incident model poskytuje https://developer.harness.io/docs/ai-sre/incidents/.

Verification, no-data a evidence limits sú oddelené v https://developer.harness.io/docs/continuous-delivery/verify/continuous-verification-faqs/ a log-analysis results na https://developer.harness.io/docs/continuous-delivery/verify/cv-results/apm-logs/. Truncation a deployment-log hranice dokumentuje https://developer.harness.io/docs/continuous-delivery/manage-deployments/deployment-logs-and-limitations/. OpenTelemetry authority pre log/trace correlation cez trace, span a resource context je https://opentelemetry.io/docs/specs/otel/logs/. Tieto sources definujú evidence mechanisms; incident root cause a business recovery musia vzniknúť z konkrétneho incident bundle-u.

## Zhrnutie

Agentický incident responder je evidence indexer a bounded hypothesis engine. Authority pre severity, remediation, recovery a closure zostáva v explicitných policies, authorized responders a technical aj business read-backoch.

Incident `AGENT-DELIVERY-12` ukazuje nebezpečenstvo zelených control-plane signals. Zelená pipeline, `Synced` GitOps application a znížená latency neuzatvárajú incident, ak nebola vykonaná authoritative reconciliation skutočného business harmu.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: GitOps a release agents](gitops-release-agents.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
