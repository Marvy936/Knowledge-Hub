# Supervisor, router a specialist patterns

Supervisor, router a specialist nie sú zameniteľné názvy pre „viac agentov“. Router vykonáva bounded klasifikáciu alebo dispatch, supervisor udržiava operation context a koordinuje viac krokov a specialist rieši presne ohraničenú doménovú úlohu. Keď sa tieto role zmiešajú bez contractov, router začne plánovať, specialist začne meniť business state a supervisor prijíma vlastné predchádzajúce tvrdenia ako nezávislý dôkaz.

V incidente `AGENT-OPS-02` router vyhodnotil checkout incident ako `compute` podľa dominantného textu alertu a odoslal ho Kubernetes specialistovi. Supervisor neskôr paralelne zavolal database specialistu, ale obom poslal rovnaký voľný prompt „nájdi príčinu a oprav ju“. Specialists dostali zdieľaný context, všeobecný operations tool a žiadny output contract. Jeden vrátil hypotézu, druhý ju zopakoval a supervisor dve podobné formulácie interpretoval ako konsenzus. Chýbali route evidence, abstain path, bounded specialist scope, independent evidence a synthesis rules.

## 1. Router

Router prijíma input a vyberá jednu alebo viac destination podľa explicitnej taxonómie. Môže byť deterministický, rule-based, klasifikačný model alebo LLM so structured outputom. Router typicky nevlastní dlhý multi-turn plán; jeho úloha je rozhodnúť, kam má požiadavka pokračovať.

```text
input subject
→ feature extraction and policy checks
→ route decision
→ one destination, parallel fan-out, fallback or abstain
```

Router output je decision artifact, nie iba interná modelová veta.

## 2. Supervisor

Supervisor vlastní priebeh komplexnej operácie. Udržiava state, plán, budgets, unresolved hypotheses a rozhoduje, ktorého specialistu zavolať na základe doterajších observations. Môže specialistov volať sekvenčne alebo paralelne a následne syntetizovať výsledok.

Supervisor nemá byť neobmedzený „boss agent“. Jeho authority sa obmedzuje topology manifestom, tool contracts, approval gates, maximum depth, cost budgetom a single-writer pravidlami.

## 3. Specialist

Specialist má úzky domain scope, optimalizovaný context a presný output contract. Môže byť agent, deterministic workflow alebo obyčajný tool. Označenie „specialist“ samo osebe neznamená, že potrebuje vlastný agent loop.

Dobrý specialist contract odpovedá:

```text
Akú otázku rieši?
Aké inputs smie dostať?
Aké tools smie použiť?
Čo nesmie urobiť?
Aký evidence artifact musí vrátiť?
Kedy má abstain alebo eskalovať?
```

## 4. Router verzus supervisor

Router je spravidla jeden bounded dispatch krok. Supervisor je stateful orchestrator, ktorý môže opakovane delegovať podľa nových findings. LangChain dokumentácia túto hranicu opisuje explicitne: router typicky klasifikuje a dispatchuje bez ongoing conversation ownership, kým supervisor udržiava context a dynamicky volá subagentov naprieč turns.

Pri jasných kategóriách je router lacnejší a predvídateľnejší. Supervisor je vhodný až vtedy, keď destination nemožno určiť jedným krokom alebo keď treba postupne kombinovať viac domén.

## 5. Exact routing subject

Route decision musí byť viazaný na presný input, taxonomy generation a policy state:

```yaml
route_decision_id: route-2044-01
operation_id: checkout-incident-2044
router_generation: incident-router/v7
taxonomy_generation: ops-domains/v12
input_digest: sha256:...
auth_context_digest: sha256:...
features:
  service: checkout
  environment: production
  alert_family: latency
  affected_dependency: payment-provider
selected_routes:
  - business-metrics-specialist
  - provider-connectivity-specialist
confidence: 0.84
abstained: false
reason_codes:
  - CROSS_DOMAIN_SIGNAL
  - PAYMENT_DEPENDENCY_PRESENT
```

Bez taxonomy generation nemožno vyhodnotiť route drift po zmene kategórií alebo descriptions.

## 6. Deterministický router

Rule-based router je vhodný, keď routing vychádza z autoritatívnych polí alebo security policy. Napríklad tenant, environment, resource type alebo data classification sa nemajú odhadovať z voľného textu modelom.

```python
def route(event: IncidentEvent) -> list[str]:
    routes = ["business-metrics-specialist"]
    if event.resource_kind in {"Deployment", "Pod"}:
        routes.append("kubernetes-specialist")
    if event.dependency_type == "database":
        routes.append("database-specialist")
    if event.data_classification == "restricted":
        routes.append("security-review-workflow")
    return routes
```

Deterministický router môže používať LLM na enrichment, ale finálny security-sensitive dispatch kontroluje code alebo policy engine.

## 7. Probabilistický router

Probabilistický router pomáha pri neštruktúrovaných požiadavkách a nejasných domain boundaries. Musí však vracať structured decision, confidence alebo margin, reason codes a abstain možnosť.

Router sa kalibruje na route-level precision a recall, nie iba overall accuracy. False negative pre security route môže mať vyšší risk než extra read-only specialist call.

## 8. Abstain a fallback

Router nesmie byť nútený vybrať kategóriu pri nedostatku evidence. `abstain` môže viesť na deterministic enrichment, broad read-only triage alebo human intake.

```text
high confidence → selected specialist
medium confidence → safe multi-route or supervisor review
low confidence → abstain and request evidence
policy conflict → fail closed or human escalation
```

Fallback nemá automaticky znamenať „pošli všetko všeobecnému agentovi s plnými právami“.

## 9. Single-route a multi-route

Single-route vyberie jedného specialistu. Multi-route fan-out vyberie viac nezávislých domén a môže ich spustiť paralelne. Multi-route vyžaduje deduplication, budget a synthesis contract.

Pri `AGENT-OPS-02` bol multi-route diagnosticky správny, ale mutation authority mala zostať centralizovaná. Parallel evidence gathering a parallel remediation sú dve odlišné rozhodnutia.

## 10. Route taxonomy

Taxonómia musí byť versioned a bez nejasných overlapov. Každá route obsahuje domain definition, inclusion, exclusion, required inputs, specialist generation a fallback.

```yaml
route: database-specialist
description: Diagnose database availability, saturation, locks and replication.
include_when:
  - authoritative dependency graph contains database
  - SQL error or connection-pool signal is present
exclude_when:
  - request is only about data-policy approval
required_inputs:
  - service
  - environment
  - time_window
specialist_contract: database-diagnostics/v5
```

Prompt-only descriptions bez versioned registry sťažujú audit a compatibility testing.

## 11. Router evaluation

Eval dataset obsahuje jednoznačné cases, ambiguous cases, multi-domain cases, out-of-scope requests a adversarial inputs. Meria sa:

```text
route precision and recall
abstain precision
required-route miss rate
unnecessary fan-out rate
latency and cost
policy-route bypass rate
segment performance by language, tenant and modality
```

Overall route accuracy môže skryť zlyhanie zriedkavej, ale kritickej security kategórie.

## 12. Supervisor state

Supervisor state obsahuje operation identity, plan, invoked specialists, task statuses, findings, conflicts, budgets, approvals a pending actions. Specialists nemajú zapisovať priamo do neštruktúrovaného supervisor scratchpadu.

```yaml
supervisor_state:
  operation_id: checkout-incident-2044
  plan_version: 3
  unresolved_hypotheses:
    - id: H1
      claim: payment-provider latency
      status: plausible
    - id: H2
      claim: database saturation
      status: untested
  specialist_tasks:
    task-provider-1: completed
    task-db-1: running
  action_state: none
  remaining_budget_eur: 1.70
```

State schema generation je súčasť release manifestu.

## 13. Supervisor planning

Supervisor rozkladá operation na observations a decision points. Nemá delegovať všeobecné „vyrieš problém“ tasks, pretože specialist potom preberá nejasnú planning a action authority.

Dobrý task je bounded:

```text
Zisti, či p95 database connection acquisition medzi 14:00–14:20 UTC
prekročila 200 ms. Použi iba read-only metrics a vráť source refs,
threshold a unresolved gaps podľa database-findings/v2.
```

Takýto task je evalovateľný a neumožňuje specialistovi improvizovať mutáciu.

## 14. Delegation identity

Každá delegácia má stabilný business subtask ID a samostatné technical attempt IDs. Retry nesmie vytvoriť nový nezávislý task bez deduplication.

```yaml
subtask_id: diagnose-db-saturation
attempt_id: attempt-03
parent_operation_id: checkout-incident-2044
parent_run_id: supervisor-run-8
contract_digest: sha256:...
```

Stabilný subtask ID umožňuje rozpoznať duplicate specialist results a účtovať všetky attempts.

## 15. Context packaging

Supervisor vyberá minimum contextu potrebné pre specialistu. Package obsahuje objective, subject, time window, relevant evidence refs, constraints a output schema. Neobsahuje automaticky celú conversation history, cudzie specialist outputs alebo secrets.

```yaml
context_package:
  operation_id: checkout-incident-2044
  tenant: retail-eu
  service: checkout
  time_window: 2026-08-04T14:00:00Z/2026-08-04T14:20:00Z
  evidence_refs:
    - metrics://checkout/errors
    - topology://checkout/dependencies/v21
  assumptions: []
  forbidden_data:
    - customer_payloads
    - payment_tokens
```

Package digest sa uloží do trace.

## 16. Specialist independence

Nezávislí specialists nemajú dostávať leading conclusion, ak cieľom je získať nezávislé evidence. Veta „Kubernetes specialist si myslí, že je to database“ môže anchoringom znehodnotiť druhú vetvu.

Supervisor môže poslať potvrdené facts a explicitné hypotheses, ale musí označiť ich status. Specialist má vedieť vrátiť `contradicted` alebo `insufficient_evidence`.

## 17. Specialist capability registry

Capability registry je authoritative inventory specialistov, ich generations, tools, scopes, model requirements, cost profile a health. Router a supervisor resolve-ujú aktuálny specialist z registry, nie z promptovej domnienky.

```yaml
specialist_id: kubernetes-diagnostics
generation: 4
status: active
input_schema: k8s-diagnostic-task/v3
output_schema: k8s-findings/v4
tools:
  - kubernetes_get/read
  - metrics_query/read
privilege: read-only
max_parallel_runs: 20
fallback: deterministic-k8s-runbook/v2
```

Registry update je release change a potrebuje compatibility eval.

## 18. Specialist output

Specialist output sa validuje ako tool result. Obsahuje claims, evidence refs, observation timestamps, confidence, scope, contradictions, gaps a mutation flag.

Supervisor nesmie prijať output, ktorý tvrdí `mutation_performed: false`, ak trace ukazuje mutation tool call. Runtime evidence má prednosť pred self-reportom modelu.

## 19. Supervisor synthesis

Synthesis porovná findings podľa subject, time window a authority. Dve podobné vety nie sú dva nezávislé dôkazy, ak pochádzajú z rovnakého upstream metricu alebo zdieľanej memory.

Supervisor vytvára evidence graph:

```text
claim H1
├─ provider status API observation
├─ gateway timeout metrics
└─ specialist interpretation

claim H2
├─ database CPU metrics
└─ connection-pool observation
```

Common-source correlation sa označí, aby sa zabránilo falošnému konsenzu.

## 20. Majority vote nie je default

Viac agents neznamená, že majority answer je správny. Agents môžu zdieľať model bias, prompt, memory alebo chybný source. High-impact verdict vyžaduje authority-weighted evidence, nie počet prose summaries.

Voting môže byť vhodný pri bounded classification evale, ale remediation rozhodnutie musí rešpektovať business invariants a source-of-truth read-back.

## 21. Serial versus parallel specialists

Parallel fan-out je vhodný pre nezávislé observations. Serial delegation je vhodná, keď output jednej vetvy definuje subject druhej.

```text
parallel:
  provider status + Kubernetes health + business metrics

serial:
  resolve exact deployment generation
  → inspect matching configuration
  → test generation-specific hypothesis
```

Supervisor plán explicitne označuje dependencies a join points.

## 22. Join policy

Join určuje, kedy možno pokračovať. Required specialist timeout vedie k escalation alebo alternate evidence path; optional specialist timeout vytvorí explicitný gap.

```yaml
join:
  mode: all-required
  required:
    - business-metrics
    - side-effect-state-readback
  optional:
    - provider-public-status
  deadline_seconds: 90
  on_required_timeout: human-escalation
  on_optional_timeout: continue-with-warning
```

Supervisor nesmie silently pokračovať, ak chýba required evidence.

## 23. Cancellation

Keď sa leading hypothesis potvrdí alebo operation skončí, nepotrebné specialist runs sa zrušia. Cancellation však nesmie skryť už odoslaný side effect alebo unknown outcome. Read-only searches možno bezpečne zastaviť; mutation attempt potrebuje reconciliation.

Cancellation event je súčasť trace a cost accounting.

## 24. Handoff pattern

Pri handoffe router alebo agent odovzdá conversation ownership specialistovi. OpenAI Agents SDK reprezentuje handoffs ako tools dostupné modelu, ale runtime efekt je zmena aktívneho agenta v top-level run-e.

Handoff je vhodný pre customer support vertical, kde refund specialist priamo pokračuje s používateľom. Pre interný evidence collection býva vhodnejší agents-as-tools pattern, kde supervisor zostáva ownerom.

## 25. Supervisor-as-manager pattern

Supervisor volá specialists ako tools alebo nested runs a kombinuje ich výstupy. OpenAI Agents SDK označuje tento pattern ako manager/agents-as-tools. Je vhodný, keď jeden agent musí vlastniť finálnu odpoveď a spoločné guardrails.

Nested run má vlastný turn budget a môže vyvolať approval interruption, ale parent operation musí stále vidieť jeho state a outcome.

## 26. Router-to-specialist pattern

Router môže odoslať request priamo specialistovi bez ongoing supervisora. Je to vhodné pre stabilné vertikály s jasným ownershipom, napríklad billing, booking alebo technical support.

Pri cross-domain requeste môže router fan-outnúť viac specialists a deterministic synthesizer spojí structured results. Nie každý fan-out potrebuje agentického supervisora.

## 27. Hybrid pattern

Praktický systém často kombinuje deterministic policy router, bounded LLM router a supervisora:

```text
security and tenant policy routing
→ probabilistic domain classification
→ supervisor for complex multi-hop cases
→ specialists as read-only tools
→ approval-bound executor
```

Každá vrstva rieši inú neistotu a má vlastné telemetry.

## 28. Specialist recursion

Specialist, ktorý smie vytvárať ďalších specialistov, zvyšuje topology depth a cost. Recursion sa povoľuje iba s max depth, child capability allowlistom a inherited budgetom.

```python
child_budget = min(
    requested_budget,
    parent.remaining_budget,
    topology.max_child_budget,
)
```

Child agent nesmie resetovať budget alebo privileges novým runom.

## 29. Approval ownership

Supervisor môže pripraviť approval proposal, ale specialist evidence a executor action musia zostať identifikovateľné. Approval sa viaže na exact action digest, nie na všeobecný supervisor summary.

Ak specialist priamo vyvolá citlivý tool, interruption musí vystúpiť na parent operation a použiť rovnaké approval policy ako top-level agent. Approval nesmie zostať skrytý v nested run-e.

## 30. Multi-tenant isolation

Router, supervisor aj specialist registry musia používať tenant z autentifikovaného execution contextu. Route description alebo specialist prompt nesmie prepisovať tenant scope.

Parallel tasks rôznych tenantov nesmú zdieľať state, memory namespace, trace payload ani result cache. Parent-child IDs obsahujú tenant boundary a storage enforcement.

## 31. Security boundaries

Routing model nie je authorization engine. Aj správne zvolený specialist musí prejsť runtime authentication, authorization a tool policy. Malicious input sa môže pokúsiť vyvolať privileged route alebo vložiť falošné delegation instructions.

Route decision je untrusted proposal, kým policy engine nepotvrdí, že caller a operation smú zvolenú capability použiť.

## 32. Observability

Trace zachytáva:

```text
router input digest and taxonomy generation
route decision and confidence
supervisor plan version
specialist contract and context digests
parent-child run IDs
specialist tool calls and outputs
join decision
synthesis evidence graph
final action proposal and business outcome
```

Bez týchto údajov nemožno odlíšiť wrong route od specialist failure alebo synthesis loss.

## 33. Incident `AGENT-OPS-02`

Router vybral iba compute route, pretože alert title obsahoval `pod latency`. Dependency graph však ukazoval payment provider a business metrics ukazovali pokles conversion. Supervisor neskôr pridal database specialistu, ale obom poslal rovnaký shared context vrátane neoverenej hypotézy o deadlocku.

Správny tok bol:

```text
policy-enforced subject enrichment
→ multi-label route with abstain support
→ independent read-only specialist tasks
→ typed findings with source refs
→ authority-aware synthesis
→ one bounded remediation proposal
→ approval and business read-back
```

Route taxonomy sa doplnila o dependency a business-impact features a specialists prišli o všeobecný mutation tool.

## 34. Failure hypotheses

Pri nesprávnom supervisor outcome zostáva otvorených viacero failure paths. First divergence sa hľadá od input enrichmentu cez route decision, capability resolution, context packaging, specialist execution, join až po synthesis.

- **Feature omission** — router nedostal dependency, tenant, environment alebo risk signal.
- **Taxonomy overlap** — route descriptions boli nejednoznačné alebo nekompatibilné.
- **Forced classification** — router nemal abstain a zvolil nesprávnu destination.
- **Capability drift** — registry resolve-ovala inú specialist generation než release manifest.
- **Context leakage** — specialist dostal cudzie alebo leading údaje.
- **Contract violation** — specialist prekročil tools, scope, time window alebo output schema.
- **Join error** — supervisor pokračoval bez required resultu alebo čakal na nepotrebnú vetvu.
- **False consensus** — viac outputs pochádzalo z jedného upstream source alebo zdieľanej hypotézy.
- **Synthesis omission** — conflict alebo uncertainty sa stratili vo finálnom summary.
- **Hidden nested approval** — citlivá akcia zostala v specialist run-e bez parent policy.

Hypotézy sa falsifikujú loaded-state read-backom a causal trace, nie podľa posledného model outputu.

## 35. Containment

Containment môže vypnúť problémovú route, zmeniť specialists na read-only, zakázať parallel fan-out alebo presmerovať ambiguous cases na deterministic triage. Pri capability registry incidente sa pinne known-good specialist generation.

Systém nemá globálne povoliť všeobecnému fallback agentovi všetky tools. Safe fallback je užší, nie širší.

## 36. Recovery

Recovery zahŕňa opravu taxonomy alebo features, nový router eval, capability registry rollback, regenerovanie context package, re-run chýbajúceho specialistu a opätovnú syntézu z preserved evidence. Ak došlo k side effectu, vykoná sa authoritative read-back a compensating business action.

Po oprave sa replay-ne incident aj benign single-domain controls, aby multi-route fix nezvyšoval unnecessary fan-out.

## 37. Positive acceptance

Pozitívny test preukáže správny single-route aj multi-route dispatch, validné specialist contracts, izolované contexts, required join a evidence-aware synthesis. Supervisor musí navrhnúť iba jednu bounded action a business outcome sa overí autoritatívne.

## 38. Forbidden acceptance

Zakázaný test skúsi vynútiť privileged specialistu promptom, prekročiť tenant, zavolať mutation tool z read-only specialistu, pokračovať bez required evidence alebo skryť conflict. Každý pokus musí byť deterministicky blokovaný a auditovaný.

## 39. Recovery acceptance

Recovery test simuluje unavailable specialist, stale registry generation, wrong route a false consensus z jedného source. Systém musí degrade-núť podľa policy, zachovať evidence a po oprave obnoviť správny dispatch bez duplicate side effectov.

## 40. Second-operation acceptance

Druhá operácia použije podobný text alertu, ale inú dependency topology. Router sa musí rozhodnúť podľa aktuálneho exact subjectu, nie podľa cache predchádzajúcej route. Specialist state, findings a approvals sa nesmú preniesť.

## 41. Alternate-scenario acceptance

Alternate scenario je jasná single-domain otázka. Router má zvoliť jedného specialistu alebo deterministic workflow bez spustenia supervisora. Tým sa overí, že orchestration complexity sa používa iba tam, kde prináša hodnotu.

## 42. Primárne zdroje a proof boundary

LangChain dokumentácia rozlišuje router ako klasifikačný dispatch od stateful supervisora, ktorý dynamicky koordinuje subagentov. OpenAI Agents SDK dokumentuje agents-as-tools a handoff patterns s rozdielnym ownershipom konverzácie. Anthropic produkčný research systém používa orchestrator-worker pattern a zdôrazňuje potrebu presných delegation tasks, parallelism budgetu a evaluation.

Tieto zdroje sú implementačné príklady, nie dôkaz vhodnosti konkrétneho patternu. Repository validácia nevykonáva reálny routing, specialist isolation, nested approval, parallel failure, synthesis ani business outcome.