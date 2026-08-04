# Agent loop, state, observation, action a termination

Agent loop je runtime mechanizmus, ktorý opakovane skladá current state, získava observation, vyberá action, vykoná ju a rozhoduje, či task pokračuje alebo končí. Bez explicitného loop contractu sa agent redukuje na neobmedzenú sériu model calls a tool calls, kde nie je jasné, čo je authoritative state, ktorá akcia už prebehla a prečo bol run označený ako dokončený.

V incidente `AGENT-OPS-01` operations agent po checkout alerte načítal neúplné metriky, vybral restart payment workloadu a po tool timeoute action zopakoval. Runtime uchovával iba conversation transcript, nie durable operation state, takže nový turn nevedel rozlíšiť „akcia zlyhala“ od „výsledok je neznámy“. Agent následne ukončil loop po vete toolu „request accepted“, hoci business conversion zostala znížená. Loop zlyhal v state identity, observation semantics, action outcome aj termination contracte.

## 1. Exact run subject

Každý loop sa viaže na exact run, business operation, release a principal. Conversation ID alebo trace ID samostatne nestačí, pretože jeden business task môže prežiť viac model sessions a retries.

```yaml
agent_run:
  run_id: run-ops-8841
  operation_id: restore-checkout-eu-20260804-17
  task_type: incident-diagnosis
  principal: ops-agent-session-212
  release_manifest: agent-ops-release-v9
  state_schema: ops-run-state-v4
  autonomy_policy: diagnosis-readonly-v5
```

Run identity sa propaguje do model calls, tool calls, approvals a business read-backu. Bez nej nemožno zostaviť causal trajectory.

## 2. Loop contract

Loop contract definuje allowed states, available actions, budgets, interruption behavior a termination reasons. Model môže navrhnúť ďalší krok iba v rámci tohto contractu.

```yaml
loop_contract:
  max_turns: 10
  max_tool_calls: 16
  max_wall_clock: 120s
  max_cost_usd: 0.80
  allowed_terminal_states:
    - completed
    - blocked
    - escalated
    - cancelled
    - budget_exhausted
```

Contract je application policy. Nemá byť iba textovou inštrukciou v prompt-e.

## 3. Canonical loop

Praktický loop sa dá vyjadriť ako state machine:

```text
initialize
→ observe
→ decide
→ validate proposed action
→ execute or interrupt
→ record outcome
→ update state
→ evaluate termination
→ observe again or finish
```

Každý transition vytvára durable event. Model response je iba jeden input do decision transitionu.

## 4. State versus transcript

Transcript je chronologický zoznam messages a tool outputs. State je canonical representation toho, čo systém považuje za aktuálne platné.

Transcript môže obsahovať zastarané hypotheses, neplatné plans a tool result pred následným rollbackom. State preto nesmie byť odvodený iba tak, že sa celý transcript znova pošle modelu a očakáva sa správna interpretácia.

## 5. State schema

State schema oddeľuje task facts, hypotheses, completed actions, pending approvals, budgets a terminal status. Typed state umožňuje validation a migration.

```yaml
state:
  goal: restore-checkout-conversion
  facts:
    affected_region: eu
    checkout_error_rate: 0.18
  hypotheses:
    - id: h1
      claim: payment-deployment-regression
      status: open
  actions:
    - id: a1
      type: read_deployment
      status: completed
  pending_approvals: []
  budgets:
    turns_remaining: 7
  terminal: null
```

Free-form memory môže state dopĺňať, ale nemá nahradiť fields potrebné pre correctness a recovery.

## 6. State ownership

Nie všetky state fields vlastní model. Identity, authorization, budgets, tool outcomes a approvals vlastní runtime alebo authoritative systems.

Model môže navrhnúť hypothesis alebo plan update. Nemôže sám prepísať `action.status=completed`, ak tool executor alebo business read-back neposkytol dôkaz.

## 7. State generations

State mutation má generation alebo version. Každý turn číta konkrétnu version a zapisuje novú cez compare-and-set alebo event append.

Concurrent workers alebo resumed run tak nemôžu ticho prepísať novší state. Conflict vedie k reloadu a replanningu, nie k last-write-wins strate evidence.

## 8. Observation

Observation je runtime-visible evidence o environment-e. Môže pochádzať z user inputu, tool resultu, eventu, human approvalu alebo state read-backu.

Observation nie je automaticky pravda. Má source, timestamp, subject, trust level, completeness a freshness.

```yaml
observation:
  id: obs-771
  source: metrics-query
  subject: checkout-service/eu
  observed_at: 2026-08-04T14:10:00Z
  window: 5m
  trust: authoritative-telemetry
  completeness: partial
```

## 9. Observation normalization

Raw tool output sa normalizuje do typed observation. HTTP 200 s textom „accepted“ sa nemá interpretovať ako dokončený business side effect.

Normalizer rozlišuje transport success, operation acceptance, durable commit a postcondition verification. Tieto states sa nesmú zlúčiť do jedného boolean `success`.

## 10. Observation provenance

Agent potrebuje vedieť, či údaj pochádza z authoritative database, cache, user claimu alebo model-generated summary. Derived observations zachovávajú links na source artifacts.

Ak summary tvrdí, že deployment je healthy, runtime musí vedieť, ktoré rollout statusy a metric windows tento claim podporujú. Bez provenance sa hallucinated alebo stale fact môže stať ďalším action inputom.

## 11. Observation freshness

Freshness sa hodnotí podľa tasku. Päťminútová metrika môže byť vhodná pre trend, ale nevylučuje zmenu po poslednom deployment-e.

State obsahuje `valid_until` alebo freshness policy. Pri expirácii sa observation obnoví pred consequential decisionom.

## 12. Partial observation

Absencia evidence nie je evidence absencie. Tool timeout, permission filtering alebo sampling môže vytvoriť partial observation.

Agent má explicitne reprezentovať `unknown`, nie dopĺňať chýbajúci fakt parametric knowledge. High-impact action pri neúplnom state vedie k ďalšiemu readu, approval alebo eskalácii.

## 13. Action proposal

Model navrhuje action cez typed structure. Návrh obsahuje goal contribution, target, arguments, preconditions a expected observation.

```yaml
proposed_action:
  type: query_deployment
  target: payment-api/eu
  arguments:
    include_replicas: true
  purpose: test-hypothesis-h1
  expected_observation: loaded-image-and-rollout-state
```

Purpose umožňuje neskôr vyhodnotiť, či action skutočne znížila uncertainty alebo iba spotrebovala budget.

## 14. Action validation

Pred execution runtime overí schema, authorization, resource scope, budgets, policy a duplicate identity. Valid JSON neznamená validnú action.

Action môže byť syntakticky správna, ale zakázaná pre current autonomy mode. Validation decision sa zaznamená oddelene od model proposal-u.

## 15. Action identity

Každá action má stable business identity a môže mať viac technical attempts. Retry po timeoute používa rovnaký idempotency key, ak ide o tú istú zamýšľanú operáciu.

```yaml
action:
  action_id: restart-payment-eu-17
  idempotency_key: op-17/restart-payment-eu
  attempt: 2
  previous_attempt_outcome: unknown
```

Bez identity môže loop vytvoriť duplicate external effect.

## 16. Action execution

Executor je oddelený od modelu. Resolve-ne canonical resource, načíta credentials, vykoná authorization a zachytí request/response metadata.

Model nedostáva raw secrets ani priamy network socket. Tool runtime vytvára controlled bridge medzi probabilistickým decisionom a reálnym systémom.

## 17. Action outcome

Outcome má viac states než success/failure. Praktické hodnoty sú `committed`, `rejected`, `failed-before-submit`, `unknown-after-submit`, `pending` a `compensated`.

Unknown outcome je kritický pri writes. Loop musí najprv vykonať read-back alebo query podľa operation ID; blind retry je zakázaný.

## 18. Tool result versus observation

Tool result je technický response executor-a. Observation je interpretovaný, canonical fact použitý v state.

Napríklad Kubernetes API môže prijať restart annotation. Observation „nové pods sú ready a checkout sa zotavil“ vznikne až z rollout a business telemetry read-backu.

## 19. State update

Po action sa state aktualizuje deterministickou reducer logikou alebo validovanou mutation. Model môže navrhnúť summary, ale authoritative fields sa menia podľa events.

Event-sourced prístup zachováva, prečo field vznikol. Snapshot zrýchľuje runtime, no musí byť odvodený z immutable history alebo versioned source.

## 20. Turn

Turn je jedna model invocation plus spracovanie jej outputu podľa runtime definície. Frameworky môžu turn počítať odlišne, preto je limit naviazaný na explicitnú metric.

Turn count je budget signal, nie measure progressu. Agent môže spotrebovať päť turns bez zníženia uncertainty.

## 21. Progress signal

Loop potrebuje merateľný progress. Môže ísť o uzavreté hypotheses, splnené plan preconditions, získané authoritative observations alebo zníženie unresolved risk.

Ak sa state nemení alebo agent opakuje rovnaké tool calls, loop detekuje stagnation. Následkom je replan, fallback alebo eskalácia.

## 22. Cycle detection

Cycle detection porovnáva action signatures, observations a state generations. Rovnaký query s rovnakými arguments a nezmeneným environmentom pravdepodobne neprinesie nový evidence.

Nie každý opakovaný action je chyba; polling môže byť zámerný. Contract preto definuje interval, max repeats a expected state transition.

## 23. Budgets

Budgets pokrývajú turns, tokens, tool calls, time, cost, bytes a side effects. Runtime ich odpočítava, model ich nemôže resetovať.

Pri approaching limit-e agent dostane structured budget observation. Termination alebo eskalácia sa vykoná podľa policy, nie podľa náhodného truncated outputu.

## 24. Interruptions

Loop sa môže pozastaviť pre human approval, chýbajúci input, rate limit alebo maintenance window. Pause nie je terminal state.

Durable interruption obsahuje pending action digest, expiry, required approver a resume token. Resume znovu overí authorization a preconditions, pretože environment sa mohol zmeniť.

## 25. Resume

Resumed run načíta durable state, nie iba poslednú conversation message. Overí release compatibility, state schema version a pending side-effect outcome.

Ak sa medzi pause a resume zmenil deployment alebo policy, plan sa revaliduje. Staré approval nemá automaticky platiť pre nový target state.

## 26. Cancellation

Cancellation zastaví nové model a tool work, ale nemusí zrušiť už odoslaný external operation. Runtime preto rozlišuje requested cancellation a confirmed cancellation.

Po cancellation sa vykoná reconciliation pending actions. Inak môže run vyzerať ukončený, hoci externý side effect pokračuje.

## 27. Termination contract

Termination je deterministic decision nad state, output contractom, budgets a business postconditions. Model môže navrhnúť `finish`, ale runtime overí, či je terminal state povolený.

```yaml
termination:
  reason: completed
  required:
    - all_required_facts_resolved
    - no_pending_actions
    - no_pending_approvals
    - business_postcondition_verified
```

Self-reported confidence alebo fluent answer nestačia.

## 28. Completed

`Completed` znamená, že task-specific success criteria sú authoritative potvrdené. Pri diagnosis môže byť completed stavom validated root cause a bounded recommendation; pri remediation musí zahŕňať business recovery.

Output schema a terminal evidence sa archivujú. Neskorší incident review tak vie odlíšiť skutočný completion od optimistického closure.

## 29. Blocked

`Blocked` znamená, že task nemôže pokračovať pre konkrétnu dependency: chýbajúce permission, unavailable system alebo absent evidence. State obsahuje blocker ownera a required next event.

Blocked nie je failure agenta, ak contract správne požaduje zastavenie. Je to bezpečný terminal alebo interrupted outcome podľa workflow designu.

## 30. Escalated

`Escalated` prenáša task človeku alebo inému authority s preserved evidence. Eskalácia musí byť actionable, nie iba „neviem pokračovať“.

Handoff package obsahuje exact subject, current state, attempted actions, unresolved hypotheses, risk a recommended next safe step. Human tak nemusí rekonštruovať trajectory z raw transcriptu.

## 31. Budget exhausted

Budget exhaustion je explicitný terminal reason. Runtime nesmie predstierať success iba preto, že model vyprodukoval poslednú správu pred limitom.

Partial results sa označia ako incomplete a pending actions sa reconciliujú. Následná retry politika rozhodne, či vznikne nový run alebo pokračovanie rovnakého operation.

## 32. Failure hypotheses

Pri loop incidente sa paralelne overuje state corruption, stale observation, wrong action resolution, authorization bypass, unknown outcome, cycle a nesprávny terminal condition. Každá hypotéza sa viaže na state versions, tool attempt IDs a authoritative read-back.

V `AGENT-OPS-01` môže byť prvou divergenciou už chýbajúca `operation_id`, nie samotný duplicate restart. Bez durable identity runtime nesprávne interpretoval timeout a povolil nový action namiesto reconciliation.

## 33. Containment

Containment zastaví nové high-impact actions, zachová state/event log a označí pending outcomes ako unknown. Loop sa prepne do read-only alebo paused mode.

Ak hrozí duplicate effect, executor blokuje nové attempts pre rovnaký resource a operation family. Až authoritative read-back rozhodne, či treba compensation.

## 34. Recovery

Recovery obnoví known-good loop release, state schema, reducers, budgets a termination rules. Existing runs sa migrujú alebo bezpečne uzavrú podľa compatibility policy.

Incident trajectory sa replay-ne bez side effects a potom s controlled sandbox tools. Produkčná obnova vyžaduje loaded-state read-back a business acceptance.

## 35. Positive acceptance

Pozitívna acceptance dokazuje, že loop získava fresh observations, volí allowed actions, aktualizuje state a končí iba po splnení postconditions. Test zahŕňa happy path aj legitímne blocked a escalated outcomes.

Meria sa trajectory efficiency a progress, nie iba final text. Agent, ktorý dosiahne outcome po zbytočných tool calls, môže byť funkčný, ale nie production-ready.

## 36. Forbidden acceptance

Forbidden acceptance vyvolá timeout po možnom commitnutí, stale observation, duplicate event, approval expiry a state version conflict. Loop nesmie vytvoriť duplicate write ani prehlásiť unknown outcome za success.

Test overuje aj max-turn a cost limits. Budgets musia zastaviť ďalšie work bez straty pending-action evidence.

## 37. Second-operation acceptance

Second-operation test spustí nový run po completed alebo failed run-e na rovnakom resource. Overí, že state, idempotency keys a observations neunikajú medzi operations.

Resume test pozastaví run na approval a obnoví ho po zmene environmentu. Precondition drift musí vyvolať revalidation alebo replan.

## 38. Čo dokumentačná validácia nepreukazuje

Markdown a schemas môžu správne popísať loop semantics. Nepreukazujú durable storage, atomic state updates, reálne tool outcomes, cycle detection ani termination correctness v produkcii.

Runtime `Verified` vyžaduje executed failure injection, resume a duplicate tests na exact release. Produkčný `Stable` stav vyžaduje časové evidence a úspešné incident recovery.

## Primárne zdroje

- [OpenAI Agents SDK — Running agents](https://openai.github.io/openai-agents-python/running_agents/)
- [OpenAI Agents SDK — Runner reference](https://openai.github.io/openai-agents-python/ref/run/)
- [LangGraph — Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

## Kontrolné otázky

1. Ktoré state fields vlastní runtime a ktoré smie navrhovať model?
2. Ako observation zachová source, freshness, completeness a subject?
3. Ako loop odlíši technical timeout od unknown durable outcome?
4. Ktoré deterministic conditions povoľujú `completed` terminal state?
5. Vie run bezpečne pause-núť, resume-núť a reconciliovať pending side effects?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Deterministic workflow, probabilistic component a autonomous agent](deterministic-workflow-probabilistic-component-autonomous-agent.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Tool calling a tool contracts →](tool-calling-tool-contracts.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
