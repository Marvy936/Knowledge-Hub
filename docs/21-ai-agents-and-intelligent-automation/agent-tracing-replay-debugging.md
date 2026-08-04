# Agent tracing, replay a debugging

Agent tracing vytvára časovo a kauzálne prepojený záznam observable udalostí počas runu. Replay používa tento záznam alebo zachytené vstupy na kontrolované znovuvykonanie a debugging z neho hľadá first divergence medzi intended, loaded, executed a effective state.

Táto kapitola uzatvára incident `AGENT-EVAL-05`. Produkčný trace zachytil model turns a názvy toolov, ale nie loaded catalog digest, token audience, policy decision ani external issue write, pretože remote span nepropagoval context a sensitive tool data boli úplne vypnuté bez náhradných digestov. Neskorší replay použil aktuálny opravený tool server, takže incident nereprodukoval a tím pôvodne uzavrel chybu ako „model nondeterminism“. Až external audit log a historický catalog artifact ukázali first divergence.

Nosný lifecycle je:

```text
exact operation a composed release
→ trace/span/event identity a context propagation
→ model, tool, handoff, policy, approval a state telemetry
→ secure payload references, digests a data classification
→ immutable export, retention a completeness evidence
→ trace reconstruction a causal timeline
→ replay mode, pinned dependencies a side-effect isolation
→ competing hypotheses a first divergence
→ containment, fix, recovery replay a outcome verification
→ second-operation observability proof
```

## 1. Trace nie je iba log

Log je jednotlivý záznam udalosti. Trace spája units of work cez trace ID, span IDs, parent-child alebo link relationships a timestamps, takže ukazuje cestu operation cez model, orchestrator, tools, queues a remote agents.

Trace bez správnej identity a context propagation je iba kolekcia logs. Môže byť užitočný, ale nedokáže spoľahlivo preukázať causal chain alebo priradiť side effect ku konkrétnemu runu.

## 2. Exact trace subject

Root trace sa viaže na business operation, agent run a composed release. Trace ID nie je business idempotency key ani authorization subject; je observability correlation identifier.

```yaml
trace_subject:
  operation_id: op_checkout_8f2
  run_id: run_8291
  trace_id: trace_01J8...
  workflow_name: checkout-support-remediation
  agent_release: support-agent/5.8.1
  model_snapshot: gpt-5.6-2026-07-15
  prompt_bundle: sha256:9bd1...
  tool_catalog: sha256:41c0...
  policy_bundle: sha256:0ab8...
  environment: prod-eu/2026-08-04
```

Trace metadata odkazuje na immutable manifests. Kopírovanie celých promptov, schemas alebo secrets do root attributes zvyšuje exposure a nie je potrebné pre exact subject.

## 3. Spans

Span reprezentuje unit of work s start/end časom, parent alebo links, attributes, events a statusom. Agentický span môže reprezentovať run, turn, model generation, function tool, MCP discovery/call, handoff, guardrail, approval alebo custom business read-back.

Span status `OK` znamená, že instrumentovaná operácia podľa svojho local contractu neskončila errorom. Neznamená, že business outcome alebo security invariant sú splnené.

## 4. Span hierarchy

Parent-child hierarchy je vhodná pre synchronous nesting. Asynchronous queue, retry, fan-out/fan-in alebo remote callback môže potrebovať span links, pretože jeden event má viac causal predecessors alebo pokračuje po skončení pôvodného procesu.

Násilné vkladanie všetkého do stromu môže skryť realitu. Debugger musí rozlišovať structural parentage od logical operation, message causality a business dependency.

## 5. Context propagation

Trace context sa prenáša cez HTTP headers, queue metadata, workflow state, MCP/A2A messages a internal task envelopes. Propagation musí byť explicitne podporovaná na každej boundary a chránená pred spoofingom.

Inbound trace ID nie je trusted authorization data. Gateway môže prijať alebo regenerovať context podľa trust policy, ale business operation a caller identity sa validujú samostatne.

## 6. Operation context verzus observability baggage

Baggage alebo custom context môže niesť tenant, operation class alebo experiment cohort pre telemetry correlation. Sensitive PII, credentials a authorization claims sa do neho nevkladajú, pretože sa môže šíriť do viacerých services a exportérov.

Authoritative tenant a actor sa získajú z trusted identity envelope. Trace attributes môžu obsahovať pseudonymous IDs alebo references, ale nesmú sa stať source pre policy enforcement.

## 7. Core agent spans

Minimálny trace zachytáva run/task, model turns, tool calls, handoffs, guardrails a custom state/outcome events. OpenAI Agents SDK napríklad poskytuje built-in tracing pre runner, turns, agents, generations, function tools, guardrails a handoffs.

Framework defaults však nie sú úplná domain observability. Durable checkpoints, approval versions, policy decisions, credential handles, external commits a business read-backs často vyžadujú custom spans alebo events.

## 8. Model span

Model span zaznamená provider/model snapshot, request ID, prompt bundle digest, token usage, latency, finish reason, tool-choice output a error class. Full input/output capture je samostatné privacy rozhodnutie.

Ak content capture vypneme, zachováme message count, content types, secure payload references, hashes, classifications a output schema result. Úplne prázdny span s názvom modelu často nestačí na debugging context assembly alebo tool-selection regresie.

## 9. Tool span

Tool span obsahuje exact server/tool/schema generation, canonical arguments digest, operation/idempotency key, policy/approval references, attempt, timeout, result digest, error semantics a effective destination. Raw arguments sa capture-ujú iba podľa classification a retention policy.

Tool response `success` a span `OK` sa doplnia authoritative read-back eventom. Unknown outcome sa označí explicitne a linked reconciliation span ukáže, ako sa stav uzavrel.

## 10. Policy a guardrail span

Policy span zaznamená policy generation, subject/action/resource, relevant data classes, decision, reason code a enforcement point. Probabilistický detector pridá score a threshold, no deterministic authorization decision zostáva oddelený.

Guardrail `triggered` bez následného blocku alebo replacementu nie je containment. Trace musí ukázať enforcement result a či side effect už neprebehol pred post-tool output guardrailom.

## 11. Approval span

Approval trace obsahuje proposal digest, reviewer ID/reference, authorization evidence, decision, edits, TTL a resume revalidation. Sensitive argument preview sa môže uložiť v secure approval store a trace nesie iba reference a digest.

Execution span linkuje exact approval. Ak catalog alebo arguments driftujú, trace ukáže invalidation a nový approval, nie tiché reuse.

## 12. State a memory spans

State transition event zachytí old/new state, generation, triggering event a durable history position. Memory span pridá namespace, tenant, provenance, operation, write/read digest, TTL a invalidation.

Obsah memory môže byť citlivý alebo veľký. Secure reference umožní forenzný read podľa oprávnenia, zatiaľ čo bežný observability backend dostane iba metadata.

## 13. Business outcome spans

Custom outcome span číta authoritative technical a business source: provider status, deployment generation, conversion metric, case resolution alebo external ledger. Je oddelený od final answer span-u.

Outcome môže dozrievať neskôr. Delayed label sa linkuje na pôvodnú operation a uvádza observation window, source a confidence/causal boundary.

## 14. Sensitive data

Tracing môže zachytiť user data, prompts, tool arguments, outputs, audio alebo secrets. Capture policy je field- a span-type-specific, nie iba globálny boolean.

Redaction pred exportom používa allowlist, secret detection, classification a tokenization. Hash sa nepovažuje automaticky za anonymizáciu; malé alebo predvídateľné hodnoty môžu byť dictionary-attacknuteľné.

## 15. Secure evidence references

Pri high-sensitivity incidentoch sa raw payload uloží v oddelenom encrypted evidence store s krátkym retentionom a audited accessom. Trace obsahuje reference, digest, size, media type, classification a deletion time.

Tým sa zachová debug capability bez replikácie secretu do každého observability backendu. Evidence store a trace backend majú oddelené access roles.

## 16. Sampling

Head sampling rozhodne na začiatku trace-u a môže minúť rare failure. Tail sampling rozhodne po udalostiach a vie preferovať errors, policy denials, long latency alebo sensitive tool chains.

Sampling policy je súčasť release a evidence modelu. Critical security/audit events sa exportujú cez nezávislý guaranteed channel; observability sample nesmie byť jediný compliance record.

## 17. Adaptive sampling bias

Risk-based oversampling je užitočný pre debugging, ale mení population distribution. Dashboard percentá z sampled traces sa nemajú prezentovať ako production prevalence bez weights alebo samostatných metrics.

Sampling decisions sa zaznamenajú a monitoring rozlišuje operational aggregate metrics od debug corpus. Eval dataset mining používa provenance vrátane sampling rule.

## 18. Async export a loss

Batch processors exportujú spans asynchrónne a môžu stratiť posledné udalosti pri crashi, queue overflow alebo network failure. `flush` znižuje riziko na controlled boundary, ale nie je náhradou za durable audit ledger.

Trace completeness metric sleduje dropped spans, exporter queue, late spans a expected terminal events. Missing data sa neinterpretuje ako absence action.

## 19. Clock a ordering

Distributed clocks majú skew a timestamps nemusia dokazovať causality. Parent/link relationships, message IDs, workflow history sequence a downstream commit versions poskytujú silnejšie ordering evidence.

Debugger používa monotonic duration v procese a logical sequence cez boundaries. „Span B začal o 2 ms skôr“ nie je automatický dôkaz, že B spôsobil A.

## 20. High-cardinality attributes

Operation IDs, tool generations a tenant pseudonyms sú diagnosticky hodnotné, ale môžu zvyšovať cost alebo rozbiť metrics backend. Traces znesú vyššiu cardinality než metrics labels, no retention a indexing sa plánujú.

Raw prompt alebo arbitrary user text sa nepoužíva ako attribute key/value pre index. Ukladá sa ako protected event payload alebo secure reference.

## 21. Logs, metrics, traces a audit

Metrics ukazujú agregáty, logs detail udalosti, traces causal path a audit ledger authoritative security/business mutations. Žiadny signal nenahrádza ostatné.

Incident triage často začína metricou, lokalizuje affected traces, číta structured logs a potvrdzuje side effects v audit/operation ledgeri. Trace dashboard bez authoritative target read-backu neuzatvára incident.

## 22. Trace schema versioning

Span names, attributes a event taxonomy sa versionujú. Instrumentation upgrade môže zmeniť význam alebo prítomnosť fieldov a vytvoriť falošný trend.

Collector alebo normalization pipeline zachová raw schema version a mapuje do stable internal model. Unknown fields sa nestratia a bridge validation overí dashboards/eval graders pred rolloutom.

## 23. Trace completeness contract

Pre každý workflow sa definuje expected minimum: root subject, model/tool spans, policy/approval events, terminal state a outcome read-back. Completeness grader označí trace ako incomplete, nie ako successful.

```yaml
trace_contract:
  required_events:
    - composed_release_loaded
    - tool_catalog_resolved
    - policy_decision
    - terminal_state
    - outcome_readback
  conditional:
    - when: mutation_dispatched
      require: [approval_reference, idempotency_key, external_commit_or_reconciliation]
  privacy:
    forbid_raw_fields: [access_token, password, customer_email]
```

Contract slúži aj CI/integration tests, aby instrumentation regresia nebola objavená až počas incidentu.

## 24. Replay nie je jedna vec

Workflow replay z durable history znovu vykonáva deterministic orchestration decisions. Model/tool replay môže použiť recorded responses alebo simulators. Live replay posiela podobný request do aktuálneho systému a má úplne inú risk boundary.

Dokumentácia vždy uvedie replay type, dependencies, side-effect mode a objective. Slovo „reprodukované“ bez týchto detailov je nepresné.

## 25. Deterministic workflow replay

Durable engine replay číta history a očakáva rovnaké orchestration commands pre rovnakú code version alebo explicitné version markers. Activities a external side effects sa počas history replayu nemajú znovu vykonávať.

Nondeterministic time, randomness, unordered iteration alebo current network read v orchestration code spôsobia divergence. Tieto vstupy sa zaznamenajú alebo presunú do activity boundary.

## 26. Recorded-response replay

Recorded replay vracia pôvodné model/tool responses a testuje orchestrator, policy alebo evaluator. Je reprodukovateľnejší, ale nedokáže overiť nový model behavior alebo external integration.

Payloady sa používajú podľa privacy policy a exact schema generation. Ak current adapter nevie prečítať historical response, migration test musí byť explicitný, nie tiché premapovanie.

## 27. Stub a simulator replay

Stub replay používa controlled outputs a faults. Je vhodný pre timeout, partial commit, poisoning, retry a recovery tests, pretože side effects sú izolované.

Simulator fidelity je eval subject. Passing stub test nepreukazuje production behavior; report uvádza, ktoré protocol, timing, consistency a auth vlastnosti simuluje.

## 28. Model re-execution replay

Re-execution pošle historical input do pinned alebo candidate modelu a porovná observable behavior. Aj pinned snapshot môže mať probabilistickú variabilitu alebo provider-side changes, preto sa vykonáva viac samples.

Private user data sa nesmie automaticky replayovať do iného provider/model regionu. Data-use approval a minimization sa kontrolujú pred requestom.

## 29. Tool re-execution

Skutočný tool sa pri debugging replayi defaultne nevolá, ak môže mutovať, účtovať alebo exfiltrovať. Read-only tool môže byť povolený v isolated test tenant-e s pinned generation a egress policy.

Mutation sa nahradí fake executorom alebo ephemeral environmentom. Ak je potrebný production read-back, vykoná ho explicitný read-only diagnostic run, nie hidden replay side effect.

## 30. Historical dependency pinning

Incident replay potrebuje historical model/prompt/tool/policy/schema a relevantný state snapshot. Použitie current repaired dependency môže odstrániť failure a vytvoriť false non-reproduction.

Ak historical artifact už nie je dostupný, replay verdict to uvedie. Trace a provenance môžu stále podporiť root-cause inference, no nemožno tvrdiť full reproduction.

## 31. Time, randomness a external state

Replay manifest zachytí logical time, timezone, random inputs, feature flags, rate-limit state a external snapshots. Hard-coded current time alebo live search môže zmeniť branch.

Nie všetko sa dá snapshotovať. Volatile dependency sa nahradí contract fixture alebo sa replay označí partial a výsledok sa interpretuje opatrne.

## 32. Side-effect isolation

Replay generuje nové replay/run IDs, ale zachová reference na original operation. Nikdy nereuse original idempotency key proti live targetu, pretože to môže vrátiť starý result alebo kolidovať s production ledgerom.

Network, filesystem, credentials a queues sú default deny. Explicitný manifest povoľuje iba test destinations a teardown overí, že nevznikol external residue.

## 33. Replay manifest

```yaml
replay:
  original_operation: op_checkout_8f2
  original_trace: trace_01J8...
  replay_id: replay_20260804_004
  mode: recorded-model-and-tool-responses
  agent_release: support-agent/5.8.1
  tool_catalog: sha256:41c0...
  policy_bundle: sha256:0ab8...
  state_snapshot: snapshot://agent-evidence/op_checkout_8f2
  network: deny
  mutations: stub
  sensitive_payloads: secure-reference-only
  objective: reproduce catalog-to-exfiltration first divergence
```

Manifest sa uloží s výsledkom a diffom. Bez neho sa dva replay runs nedajú zmysluplne porovnať.

## 34. Debugging ladder

Debugging začína exact incident subjectom a business/security impactom. Potom porovná intended configuration, resolved manifest, loaded runtime, exercised path a effective outcome.

Táto ladder zabraňuje preskakovaniu k promptu alebo modelu. Veľa „agent failures“ vzniká v catalog resolution, policy, identity, tool adapteri, state alebo observability gap-e.

## 35. Evidence freeze

Pred retry, restartom alebo config change sa zachovajú traces, histories, catalogs, policy bundles, approvals, operation ledgers, external audit a secure payload references. Mutation evidence má prioritu pred snahou rýchlo reprodukovať.

Freeze nezastavuje nevyhnutné containment. Zaznamená sa každá emergency action a jej generation, aby timeline oddelila incident behavior od response zásahu.

## 36. Causal timeline

Timeline spája model/tool events s durable history, network/proxy logs a external commits. Používa IDs, versions a links, nie iba wall-clock sort.

Každý významný transition má evidence source a confidence. Gaps sa označia explicitne; nevymýšľa sa missing reasoning alebo event.

## 37. First divergence

First divergence je najskorší bod, kde actual state alebo action prestali zodpovedať expected contractu. Oprava neskorého symptómu môže incident dočasne skryť bez odstránenia príčiny.

V `AGENT-EVAL-05` first divergence bol neapproved catalog load, nie external issue write. Trace bez catalog digest tento bod neukázal, preto tím pôvodne obvinil model selection.

## 38. Competing hypotheses

Debugging udržuje viac hypotéz: model vybral zlý tool, host načítal poisoned catalog, proxy zlyhala v audience validation, policy nevidela data lineage, trace stratil remote span alebo external issue vzniklo iným procesom. Každá hypotéza má diskriminačný dôkaz.

Experiment mení jednu vrstvu a používa controlled replay. Prompt tweak bez overenia loaded catalogu nedokáže rozlíšiť model a tool-supply-chain failure.

## 39. Trace diff

Trace diff porovná normalized events baseline a candidate alebo original a replay. Identifikuje first changed tool, arguments, state, policy, latency, cost a outcome.

Sequence diff musí rešpektovať alternative valid order a parallelism. Event matching používa semantic identity a parent/link graph, nie iba index v zozname.

## 40. Missing span diagnosis

Missing span môže znamenať neinstrumentovanú boundary, sampling, exporter loss, crash pred flushom, context propagation gap alebo malicious/buggy server. Každá možnosť má iný evidence source.

Expected-event contract a downstream audit umožnia rozlíšiť „call neprebehol“ od „call prebehol, trace chýba“. Absence telemetry sa nikdy automaticky neinterpretuje ako absence side effectu.

## 41. Debug mode risks

Verbose logging alebo full trace capture môže počas incidentu odhaliť viac secrets než pôvodná chyba. Debug mode preto má bounded scope, approval, expiry, destination a automatic cleanup.

Production debug zmena je release/config transition s auditom. Po incidente sa overí návrat k normal capture policy a odstránenie temporary accessov.

## 42. Incident `AGENT-EVAL-05`

Root trace obsahoval model generation a dva local function spans, no remote MCP call vytvoril nový trace bez operation linku. Tool data capture bolo vypnuté a local span nemal catalog/schema digest ani data classes.

Replay použil current server `3.4.1`, kde description a downstream behavior už boli opravené. Nereprodukcia sa mylne interpretovala ako náhodný model behavior, kým issue audit ukázal original operation ID v comment metadata a artifact registry našla historical server `3.4.0`.

## 43. Corrected replay

Tím vytvoril historical manifest, použil recorded server catalog/output, stubbed issue sink a original policy bundle. Replay reprodukoval plan drift a policy gap bez external side effectu.

Candidate replay potom pinol nový registry control a data-flow policy; run skončil deny pred credential handle resolution. Legitímny diagnostic variant stále prešiel read-only cestou.

## 44. Failure hypotheses

Tracing/debugging incident sa analyzuje od instrumentation contractu po replay fidelity. Najprv sa kontroluje root subject, context propagation a expected spans, pretože incomplete trace môže vytvoriť nesprávny causal story.

Potom sa overí payload/redaction policy, exporter loss a schema normalization. Pri replayi sa porovnajú historical dependencies, state, time, randomness a side-effect isolation; current environment nie je automaticky reprodukcia minulosti.

- **Propagation gap** — remote span nebol linked k operation.
- **Sampling loss** — critical trace alebo child span nebol exportovaný.
- **Redaction overreach** — odstránili sa aj digests/classifications potrebné na diagnosis.
- **Exporter loss** — crash alebo queue overflow zahodil late spans.
- **Schema drift** — dashboard/grader nesprávne interpretoval nový event model.
- **Historical artifact gap** — replay nemal original prompt, catalog alebo policy generation.
- **Live dependency drift** — current tool/model zmenil behavior a failure zmizol.
- **Unsafe replay** — debugging znovu vykonal production side effect.
- **False ordering** — clock timestamps boli zamenené za causality.
- **False model root cause** — chýbajúca platform evidence sa pripísala nondeterminismu.

Každá hypotéza sa testuje trace contractom, exporter telemetry, external ledgers, artifact registry a controlled replay manifestom. „Nevieme reprodukovať“ je stav evidence, nie dôkaz, že incident neexistoval.

## 45. Containment

Containment zapne guaranteed audit pre affected actions, quarantinuje tool generation a zachová trace/evidence artifacts. Replays sa nastavia na deny network a stub mutations.

Ak tracing pipeline uniká secrets, export sa zastaví alebo redakcia sprísni, no critical operation/audit ledger pokračuje oddeleným kanálom. Incident response nesmie zničiť jediný evidence source bez náhrady.

## 46. Recovery

Recovery opraví context propagation, trace schema, secure references, sampling a completeness alerts. Historical artifacts a replay fixtures sa uložia podľa retention a access policy.

Root cause fix prejde original/recovery replayom, trace diffom a end-to-end outcome testom. Observability fix sa prijíma iba ak nový trace dokáže preukázať controls bez raw secret exposure.

## 47. Positive acceptance

Kompletný trace spája root operation, agent turns, exact tool generations, policy/approval, external commit alebo reconciliation a authoritative outcome. Sensitive content je redacted alebo referenced a completeness contract prejde.

Recorded replay reprodukuje original decision path bez side effects. Candidate replay ukáže first divergence v očakávanom fixe a legitímny variant dosiahne outcome.

## 48. Forbidden acceptance

Trace s missing remote mutation, bez catalog generation alebo bez outcome read-backu nesmie byť označený complete. Span `OK` alebo final answer success nesmie uzavrieť incident.

Replay nesmie volať production mutation, používať current dependency bez disclosure ani kopírovať secrets do debug backendu. Nereprodukcia pod zmeneným environmentom nie je exoneration.

## 49. Recovery acceptance

Process crashne po remote commit-e a pred local result persistence. Audit ledger, linked trace a reconciliation musia rekonštruovať unknown outcome bez duplicate side effectu.

Exporter outage vytvorí completeness alert a guaranteed mutation audit zostane dostupný. Po obnove sa late spans deduplikujú a správne linkujú.

## 50. Second-operation acceptance

Nový independent run vytvorí fresh trace/operation IDs, current manifests a complete spans. Nesmie zdediť replay fixtures, debug capture mode ani old trace context.

Dashboard, trajectory grader a incident tooling musia nový run interpretovať podľa current schema, zatiaľ čo historical trace zostáva čitateľný pod pôvodnou generation.

## 51. Praktický tracing pseudocode

```python
from agents import Runner, RunConfig, trace, custom_span, flush_traces

async def execute_support_run(case):
    metadata = {
        "operation_id": case.operation_id,
        "agent_release": RELEASE_ID,
        "tool_catalog_digest": TOOL_CATALOG_DIGEST,
        "policy_bundle_digest": POLICY_DIGEST,
        "tenant_ref": pseudonymize(case.tenant),
    }

    with trace("checkout-support-remediation", group_id=case.thread_id, metadata=metadata):
        with custom_span("composed_release_loaded", metadata):
            validate_loaded_release()

        result = await Runner.run(
            support_agent,
            case.safe_input,
            run_config=RunConfig(
                workflow_name="checkout-support-remediation",
                trace_include_sensitive_data=False,
            ),
        )

        with custom_span("outcome_readback", {
            "source": "checkout_metrics_authority",
            "status": read_business_status(case.operation_id),
        }):
            pass

    await flush_traces()
    return result
```

Pseudocode ilustruje framework trace a custom domain events. Durable mutation audit a external outcome store musia existovať nezávisle od async trace exportu.

## 52. Primárne zdroje

- [OpenAI Agents SDK — Tracing](https://openai.github.io/openai-agents-python/tracing/)
- [OpenAI Agents SDK — Running agents and trace configuration](https://openai.github.io/openai-agents-python/running_agents/)
- [OpenAI — Trace grading](https://developers.openai.com/api/docs/guides/trace-grading)
- [OpenTelemetry — Traces](https://opentelemetry.io/docs/concepts/signals/traces/)
- [OpenTelemetry specification — Context](https://opentelemetry.io/docs/specs/otel/context/)
- [OpenTelemetry specification — Propagators API](https://opentelemetry.io/docs/specs/otel/context/api-propagators/)

## 53. Zhrnutie

Agent tracing zachytáva observable execution path cez model, tools, handoffs, policies, approvals, state a outcomes. Je kritickou evidence surface, ale sampling, exporter loss, redaction, schema drift a context gaps znamenajú, že trace nie je automaticky úplný audit.

Replay musí pomenovať svoj typ, pinovať historical dependencies, izolovať side effects a zachovať privacy. Debugging potom hľadá first divergence cez exact subject, causal timeline, competing hypotheses a trace/external-ledger diff. Najdôležitejšia otázka nie je „máme trace a podaril sa replay?“, ale „je trace pre exact operation dostatočne kompletný a bezpečný a reprodukoval replay pôvodný loaded environment bez vytvorenia nových side effects, aby podporil konkrétnu root-cause a recovery claim?“

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Trajectory, tool-selection a outcome evaluation](trajectory-tool-selection-outcome-evaluation.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->