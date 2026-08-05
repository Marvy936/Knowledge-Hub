# Intelligent automation troubleshooting

Troubleshooting inteligentnej automatizácie musí rozlíšiť modelový omyl od chyby workflowu, identity, policy, retrievalu, connectora, side effectu, state store alebo telemetry pipeline. Najčastejšia zlá reakcia je upraviť prompt pri každom nečakanom výsledku. Agent môže mať úplne správny reasoning a napriek tomu vykonať akciu pod nesprávnym účtom, dvakrát alebo bez business efektu.

## 1. Business outcome

Cieľom je bezpečne obnoviť definovaný service a business invariant, vysvetliť competing hypotheses a vytvoriť evidence, ktorá zabráni opakovaniu. Troubleshooting sa nekončí, keď execution zmení stav na `success`.

Incident sa uzatvára až po authoritative read-backu, reconciliation a stabilizačnom okne.

## 2. Exact incident subject

Troubleshooting envelope viaže incident ID, affected tenant, environment, workflow execution, source commit, prompt, model, tool catalog, policy, credentials, index, memory session, event identity, operation ID, resource generation a telemetry pipeline generation.

Bez exact subjectu sa ľahko porovnávajú stopy z iného runu alebo inej release.

## 3. Preserve before mutate

Pred rerunom alebo editom sa zachová execution graph, inputs, outputs, tool arguments, approvals, logs, traces, provider audit events, queue state, database rows a business ledger. Citlivé dáta sa redigujú podľa policy, nie vymazaním identity evidence.

„Skúsme to znovu“ môže zničiť jediný dôkaz a vytvoriť druhý side effect.

## 4. Symptom versus outcome

Symptóm je napríklad timeout, halucinovaná odpoveď, stuck approval alebo missing trace. Outcome je nedoručený ticket, duplicitná platba, neaplikovaný deployment alebo zablokovaný používateľ.

Rovnaký symptóm môže mať viac príčin a rovnaká príčina môže vytvoriť rôzne symptómy.

## 5. Layered fault model

Intelligent automation sa rozkladá na trigger, orchestration, state, model, retrieval, memory, tool selection, connector, identity, policy, approval, downstream system, telemetry a business domain. Každá vrstva má vlastný authority source a failure evidence.

Troubleshooter nezačne pri modeli iba preto, že systém obsahuje LLM.

## 6. Known-good path

Najprv sa identifikuje posledná known-good composed generation a porovná sa s failing generation. Diff zahŕňa configuration, model alias resolution, tool schemas, policies, credentials, data sources a runtime dependencies.

Porovnanie iba Git commitov prehliadne mutable external state.

## 7. Correlation identity

Trace ID, workflow execution ID, event ID, operation ID, approval ID a provider request ID sa prepájajú explicitne. Jeden identifikátor zriedka pokrýva celý distributed path.

Ak correlation chýba, incident sa označí evidence gap; nesmie sa doplniť domnienkou modelu.

## 8. Timeline reconstruction

Timeline používa authoritative timestamps a rozlišuje event time, ingestion time, execution time, approval time a provider apply time. Clock skew a delayed delivery sa zaznamenajú.

Zoradenie podľa jedného logového timestampu môže vytvoriť falošnú causal story.

## 9. Trigger failures

Trigger môže event neprijať, prijať viackrát, overiť zlý signature, nesprávne parseovať schema alebo spustiť nesprávnu workflow version. Evidence zahŕňa ingress logs, delivery attempts, event envelope a route resolution.

Absence workflow execution neznamená, že upstream event nevznikol.

## 10. Event identity a duplicates

Pri at-least-once delivery sa kontroluje stable event ID, semantic operation key, inbox record a duplicate decision. Nový transport delivery ID nesmie vytvoriť novú business operation.

Rerun s novým idempotency key je nový side effect, nie diagnostika.

## 11. Orchestration state

Skúma sa current state machine state, checkpoint, wait, retry count, timeout, cancellation a ownership lease. `Running` môže znamenať blocked worker, lost callback alebo legitímny durable wait.

UI label bez underlying state recordu nie je dostatočný dôkaz.

## 12. Queue a worker path

Queue troubleshooting overí enqueue, visibility, claim, heartbeat, acknowledgment, redelivery a dead-letter behavior. Worker success log sa porovná s durable commitom.

Crash po provider apply a pred queue acknowledgmentom je klasický duplicate risk.

## 13. Model request

Modelová vrstva sa overuje až po pinning requestu: exact model resolution, system a developer instructions, user content, tool definitions, response format, token limits, sampling a safety filters.

Replay s iným current model aliasom nereprodukuje pôvodný incident.

## 14. Model output

Raw response sa oddeľuje od parser outputu a downstream normalized decisionu. Truncation, invalid JSON, refusal, tool-call omission alebo multiple calls majú rozdielne recovery paths.

Parser nesmie premeniť missing field na permissive default.

## 15. Prompt hierarchy

Troubleshooting kontroluje, či untrusted ticket, retrieved document alebo tool output nebol vložený do vyššej instruction role. Prompt injection je trust-boundary chyba, nie iba „zlá odpoveď modelu“.

Fix musí zmeniť data/instruction separation a authority, nie len pridať vetu „ignoruj útoky“.

## 16. Retrieval path

RAG incident sa rozkladá na source revision, ACL generation, ingestion, parser, chunk, embedding, index alias, filters, query, top-k, reranking a citations. Správna odpoveď zo stale dokumentu je stále failure.

Missing document môže byť permission denial, indexing lag alebo query mismatch; tieto hypotézy sa testujú oddelene.

## 17. Memory path

Memory troubleshooting overí session key, tenant scope, read/write order, trimming, summary generation a stale facts. Cross-session contamination sa rieši ako security incident.

Vymazanie memory môže odstrániť symptóm, ale nepreukazuje root cause.

## 18. Tool selection

Kontroluje sa, aké tools model videl, ich descriptions, schemas, versions a policy classification. Tool nemusí byť zvolený pre ambiguous description, context overflow alebo explicitný refusal.

Pridanie generic HTTP toolu ako fallback zväčšuje capability surface a nie je bezpečný fix.

## 19. Tool arguments

Arguments sa porovnajú s schema, authoritative resource identifiers, user intentom a approval digestom. `$fromAI()` alebo podobná modelová parameterizácia nesmie určovať tenant, principal alebo permission scope bez deterministic bindingu.

Valid JSON môže stále označovať nesprávny resource.

## 20. Connector path

Connector troubleshooting rozlišuje DNS, TLS, proxy, authentication, authorization, rate limit, request transformation, API version, response parsing a provider outage. HTTP 200 nemusí znamenať semantic apply.

Provider request ID a read-back sú silnejšie evidence než connector node status.

## 21. Identity path

Skúma sa workload identity, delegated user, tenant, scopes, role assignments, credential generation a token audience. Rovnaký display name alebo service alias môže existovať vo viacerých scopes.

„Funguje manuálne pod adminom“ nepreukazuje správnosť produkčnej identity.

## 22. Policy path

Policy input, bundle version, decision, explanation a enforcement point sa zachovajú. Guidance warning, dry-run alebo UI validation sa nesmie zameniť za runtime deny.

Ak policy služba neodpovedá, fail-open versus fail-closed je explicitný contract, nie náhodný exception handler.

## 23. Approval path

Approval incident kontroluje envelope digest, reviewer authorization, expiry, callback identity, decision persistence a precondition revalidation. Approved plan nesmie byť po kliknutí zmenený modelom.

Stuck approval môže byť channel delivery failure, lost callback alebo už expirovaný decision.

## 24. Side-effect path

Execution success sa porovná s downstream resource, audit eventom a domain ledgerom. Timeout po requeste môže znamenať rejected, accepted, partial alebo unknown outcome.

Blind retry je zakázaný, kým reconciliation nerozhodne, čo sa skutočne stalo.

## 25. Business path

Technický stav sa doplní business query: zákazník dostal správu, entitlement je účinný, objednávka existuje raz, deployment prijíma traffic alebo incident communication má správnych recipientov.

Modelový summary ani workflow completion nie sú business evidence.

## 26. Telemetry pipeline

Pred záverom „nič sa nestalo“ sa overí, či telemetry vznikla, bola prijatá, spracovaná, sampled, redigovaná a exportovaná. OpenTelemetry troubleshooting odporúča kontrolovať každý hop a rozlišovať receive, process a export problémy.

No-data je competing hypothesis: healthy system, zero traffic alebo broken observability.

## 27. Sampling a cardinality

Tail sampling, head sampling, attribute drops a cardinality limits môžu odstrániť práve failed traces. High-risk operations potrebujú deterministic audit record mimo sampled telemetry.

Dashboard bez incident trace nie je dôkaz, že run neexistoval.

## 28. Logs, metrics a traces

Logs vysvetľujú lokálne udalosti, metrics trend a rozsah a traces distributed path. Každý signal má blind spots; correlation zvyšuje hodnotu.

Jedna zelená metrika nemôže prebiť provider audit event alebo business ledger.

## 29. Competing hypotheses

Pre každý symptóm sa udržujú aspoň dve plausible hypotézy a disconfirming test. Napríklad missing tool call môže byť prompt issue, absent tool exposure, policy denial alebo truncated context.

Model-generated root cause bez falsification je hypothesis, nie RCA.

## 30. Minimal reproduction

Reproduction používa sanitized fixed input, pinned dependencies a read-only alebo sandbox tools. Cieľom je izolovať najmenší failing boundary bez produkčnej mutation.

Reproduction, ktorá používa iný model, inú identity a fake connector, má obmedzenú evidenčnú hodnotu.

## 31. Safe replay

Replay zachová event a operation identity alebo explicitne používa simulation namespace. Non-idempotent tool calls sa stubujú alebo smerujú do test accountu.

Produkčný „retry execution“ nie je bezpečný debug mechanizmus.

## 32. Generation bisection

Keď existuje viac zmien, bisection oddelí prompt, model, tool, policy, index a runtime generations. Candidate sa testuje proti frozen datasetu a rovnakým dependencies.

Súčasná zmena piatich vrstiev a následný prompt tweak znemožňujú attribution.

## 33. Cache effects

Model cache, retrieval cache, DNS, token, connector a application cache môžu vytvoriť nereprodukovateľné správanie. Cache key a generation patria do incident evidence.

Cache flush môže dočasne pomôcť, ale nie je root-cause proof.

## 34. Rate limits a backpressure

429, queue saturation, circuit breakers a slow downstream môžu meniť trajectory, timeouty a fallback model selection. Troubleshooting sleduje budgets a retry storms.

Zvýšenie timeoutu bez backpressure analýzy môže iba predĺžiť incident a zväčšiť concurrency.

## 35. Fallback behavior

Fallback model, connector alebo manual path má rovnakú alebo menšiu authority a vlastnú observability. Fallback nesmie ticho meniť output schema, tool support alebo tenant scope.

Successful fallback sa eviduje ako degraded mode, nie normálny pass.

## 36. Data privacy počas debugovania

Debug exports minimalizujú secrets, PII, prompts a retrieved documents. Redaction musí zachovať correlation a semantic shape potrebnú na analýzu.

Kopírovanie celého production trace do verejného modelu je samostatný incident.

## 37. Incident AGENT-EVAL-16

Po false promotion candidate vytvorí duplicate onboarding. Operátor vidí modelový plán bez chyby a predpokladá, že problém je v prompt wording. Upraví prompt a rerun spustí s novým operation ID.

Pôvodná provider odpoveď bola accepted pred timeoutom, no trace exporter dropped failed run a business ledger sa nekontroloval.

## 38. False fix

Nový prompt vytvorí stručnejší plán a execution UI je green. Duplicitný entitlement ostane a druhá e-mailová správa sa odošle zákazníkovi.

Prompt change odstránil viditeľný symptom, ale pridal ďalšiu generation a zničil reprodukovateľnosť.

## 39. Containment

Mutation tools sa odpoja, workflow sa prepne do read-only diagnosis a všetky related operation IDs sa označia `reconciliation_required`. Ochranný gate zablokuje reruns bez explicitného simulation mode.

Provider records, queue history, eval manifest a telemetry gaps sa zachovajú.

## 40. Recovery

Reconciliation nájde dve accepted operations, zruší duplicate entitlement a odošle opravenú komunikáciu podľa business ownera. Workflow dostane stable operation key, inbox/outbox ledger, unknown-outcome state a mandatory read-back.

Telemetry pipeline sa opraví a incident case sa pridá do critical eval slice.

## 41. Positive acceptance

Troubleshooter identifikuje exact failing generation, zachová evidence, falsifikuje competing hypotheses, reprodukuje problém bez side effectu a preukáže technický aj business recovery. Druhý run s rovnakým eventom je no-op alebo reconcile.

## 42. Forbidden acceptance

Prompt tweak, rerun success, zmiznutie erroru, absence trace, model explanation alebo provider 200 nesmú byť acceptance. Admin-only reproduction, destructive cache flush alebo nový idempotency key nesmú maskovať pôvodný path.

## 43. Recovery acceptance

Po oprave sa vykoná failure injection pre accept-then-timeout, duplicate delivery, stale approval, wrong tenant a telemetry outage. Systém musí zastaviť, reconcile alebo deny bez neautorizovaného a duplicitného side effectu.

Business ledger a user-visible state musia zostať konzistentné.

## 44. Practical troubleshooting envelope

Evidence manifest núti incident tím rozlíšiť generations, correlation a authority. Unknown polia ostávajú unknown namiesto doplnenia modelovou domnienkou.

```yaml
troubleshooting:
  incident_id: INC-AGENT-EVAL-16
  symptom: duplicate-onboarding
  subject:
    tenant: tenant-42
    environment: production
    workflow_execution: exec-771
    workflow_commit: 8bba6ff080b6
    prompt_digest: sha256:prompt-v22
    model: provider/model@2026-08-01
    tool_catalog: onboarding-tools-v14
    policy_bundle: agent-policy-v31
    operation_id: onboard:tenant-42:user-903
  correlation:
    event_id: evt-551
    trace_id: unknown
    provider_request_id: req-1198
    approval_id: apr-88
  evidence:
    queue_record: preserved
    model_response: preserved
    tool_arguments: preserved
    provider_audit: accepted
    business_ledger: duplicate
    telemetry_completeness: failed
  hypotheses:
    - prompt-selection-error
    - accept-then-timeout-with-blind-retry
    - cross-worker-idempotency-loss
  containment:
    mode: proposal-only
    rerun_policy: simulation-required
  acceptance:
    provider_readback: required
    ledger_reconciliation: required
    stabilization_minutes: 30
```

Failure injection odstráni trace, oneskorí provider audit event a reštartuje worker po mutation. Správny proces zachová unknown outcome, nevyrobí nový operation ID a skončí domain reconciliation.

## 45. Troubleshooting decision tree

Prvý rozcestník sa pýta, či business side effect vznikol. Ak je odpoveď unknown, pokračuje reconciliation; ak nie, skúma sa trigger a orchestration; ak áno viackrát, skúma sa idempotency, queue acknowledgment a event identity.

Až po potvrdení transportu, authority a state pathu sa analyzuje modelová quality.

## 46. Runbook ownership

Troubleshooting runbook má ownera, tested commands, required evidence, forbidden actions, escalation a last-validated date. Model môže runbook vyhľadať a sumarizovať, ale nemôže si vytvoriť vyššiu authority.

Runbook, ktorý iba hovorí „retry workflow“, je pre side-effecting automation nebezpečný.

## 47. Post-incident closure

RCA rozlíši initiating fault, latent controls, detection gap a recovery gap. Follow-up zahŕňa product fix, eval case, observability fix, runbook test a owner acceptance.

Incident nie je uzavretý, kým nový control neprešiel second-operation alebo alternate-scenario testom.

## 48. Primary sources

OpenTelemetry Collector troubleshooting dokumentuje internal telemetry, debug exporter, zPages a hop-by-hop kontrolu receive, process a export pipeline. Jeho model je užitočný aj mimo telemetry: distributed automation sa diagnostikuje po hraniciach, nie jedným globálnym statusom.

NIST AI RMF zdôrazňuje dokumentované measurement a management procesy. OpenAI a LangSmith evaluation guidance podporujú logovanie, representative cases, offline regression a production feedback loop; OpenAI legacy Evals platform má oznámený koniec v roku 2026, preto troubleshooting evidence a datasets nesmú byť viazané na jeden zanikajúci UI alebo endpoint.

## Zhrnutie

Intelligent automation troubleshooting je evidence-driven distributed-systems disciplína. Model, prompt a output sú iba jedna vrstva. Bez exact generations, correlation, preserved state, safe replay, competing hypotheses, downstream read-back, telemetry validation a business reconciliation sa incident ľahko „opraví“ ďalším side effectom.

Týmto sa uzatvára authoritative obsah Section 21. Dokumentačný closeout môže potvrdiť konzistenciu a learning depth, nie živú production stabilitu alebo user acceptance.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Evaluation-driven automation lifecycle](evaluation-driven-automation-lifecycle.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
