# Workflow engine oproti agent frameworku

Workflow engine a agent framework riešia prekrývajúce sa problémy, ale nemajú rovnakú authority. Workflow engine vlastní dlhodobý control flow, retries, timers, persistence, concurrency a operational state. Agent framework vlastní probabilistické rozhodovanie, model context, tool selection a trajectory. Bez tejto hranice sa modelový checkpoint môže omylom stať business ledgerom alebo deterministic engine začne predstierať, že vie riadiť nepredvídateľné reasoning paths.

Incident `AGENT-GOV-13` používal agent graph ako jediný runtime pre produkčný release approval. Po interrupt-e sa node pri resume spustil od začiatku a code pred interruptom znovu vytvoril provider request. Checkpoint uchoval conversation state, ale nie authoritative operation ledger. Súčasne outer pipeline nevedela, či agent waiting state predstavuje approval, retry alebo abandoned execution. Výsledkom bol nejednoznačný owner side effectu.

Nosný architecture lifecycle je:

```text
business process a invariants
→ determinism, duration a failure model
→ state a side-effect authority
→ workflow-engine responsibilities
→ agent-framework responsibilities
→ typed boundary contracts
→ retries, interrupts a idempotency design
→ observability a audit correlation
→ failure injection a replay tests
→ effective business acceptance
```

## 1. Business process first

Výber technológie začína procesom: duration, number of steps, human waits, side effects, compliance, throughput a recovery objective. „Chceme AI agent“ nie je architecture requirement.

Business invariant určí, čo sa nesmie stratiť alebo zopakovať. Payment capture, release approval a ticket summarization majú odlišnú kritickosť.

## 2. Deterministic orchestration

Workflow engine očakáva explicitný graph alebo code path s definovanými transitions. Runtime ukladá execution state a rozhoduje, kedy je task ready, waiting, retrying alebo terminal.

Deterministic neznamená, že tasks nemôžu volať LLM. Znamená, že orchestration semantics nie sú ponechané na modelový text.

## 3. Agentic decision

Agent framework umožňuje modelu zvoliť tool, ďalší krok alebo termination podľa contextu. Trajectory je probabilistická a môže sa medzi runs meniť.

Agent decision je bounded proposal v rámci workflow state. High-impact transition potvrdzuje policy, approval alebo deterministic validator.

## 4. State authority

Workflow state obsahuje process position, timers, retries, operation IDs a approvals. Agent state obsahuje messages, plan, observations, memory a intermediate reasoning artifacts.

Business record ostáva v domain systeme. Žiadny z týchto runtime stores ho automaticky nenahrádza.

## 5. Durable execution

Temporal deklaruje durable execution, pri ktorom application pokračuje po crashes a outages. Taká guarantee je vhodná pre long-running mission-critical processes, ak workflow code dodrží deterministic constraints.

Durability engine-u neznamená idempotent external API. Activities alebo side effects stále potrebujú operation keys a reconciliation.

## 6. DAG orchestration

Airflow modeluje workflow ako Dag s tasks, dependencies, schedules a task instances. Je silný pre batch, data a scheduled orchestration.

Dag `success` môže závisieť od leaf tasks a trigger rules; preto ani engine terminal status automaticky neznamená business correctness. Agent task musí odovzdať typed result.

## 7. Visual automation

n8n kombinuje nodes, triggers, expressions, credentials a execution history pre integration workflows. Vie obsahovať AI Agent nodes aj deterministic branches.

n8n execution success je workflow-engine result. External provider a business outcome sa overujú samostatne.

## 8. Agent graph

LangGraph poskytuje state graph, persistence, interrupts, memory a durable execution primitives pre agents. Checkpoints umožňujú resume, replay a human-in-the-loop.

Je to silný agent runtime, ale architecture musí stále určiť, či má vlastniť business-critical orchestration alebo byť child componentom robustnejšieho process engine-u.

## 9. Persistence semantics

LangGraph checkpointuje state pri steps a viaže ho na `thread_id`. Replay preskočí steps pred checkpointom a znovu vykoná steps po ňom vrátane LLM calls, API requests a interrupts.

To je debugging a recovery capability, nie exactly-once side-effect guarantee. Nodes po checkpoint-e musia byť idempotent alebo reconciled.

## 10. Interrupt semantics

LangGraph `interrupt()` uloží state a pri resume znovu spustí celý node od začiatku. Code pred interruptom sa preto vykoná znova.

Side effect pred interruptom je zakázaný alebo musí byť idempotent. Approval request sa vytvorí pred mutation a exact subject sa uchová v durable store.

## 11. Workflow tasks a agent tools

Workflow task je engine-owned unit s retry a timeout contractom. Agent tool je model-visible capability s schema, authorization a side-effect contractom.

Rovnaká function môže mať obe wrappers, ale semantics sa nesmú miešať. Model nerozhoduje o engine retry count-e bez policy.

## 12. Control-flow ownership

Outer workflow vlastní lifecycle: received, enriching, waiting approval, executing, reconciling, completed alebo failed. Agent vlastní iba bounded diagnosis alebo proposal state.

Agent nesmie vytvoriť hidden parallel process mimo outer execution ID. Každý tool call sa koreluje na workflow operation.

## 13. Composition pattern

Najbezpečnejší pattern je deterministic shell s agentic islands. Workflow engine pripraví context, zavolá agent task, validuje output, vyžiada approval a vykoná mutation cez idempotent activity.

Agent môže iterovať v rámci token, time a tool budgetu. Po limite vracia typed `inconclusive`, nie hidden loop.

## 14. Agent-first pattern

Agent-first runtime je vhodný pre exploratory analysis, support drafting alebo low-risk knowledge work, kde trajectory flexibility je hlavná hodnota.

Aj tu external writes potrebujú policy a approval. Agent framework nesmie dostať neobmedzenú mutation authority len preto, že workflow je conversational.

## 15. Engine-first pattern

Engine-first architecture je vhodná pre payments, onboarding, releases, compliance approvals a multi-day processes. State, timers a recovery sú first-class requirements.

Agent task je replaceable implementation detail. Process môže fallbacknúť na deterministic alebo human path.

## 16. Long waits

Human approval, provider callback alebo regulatory hold môžu trvať dni. Workflow engine spravuje timer, cancellation, expiry a wake-up.

Agent memory nie je spoľahlivý timer service. Waiting state musí byť queryable bez načítania model contextu.

## 17. Concurrency

Engine riadi parallel branches, resource limits, queues a ordering. Agent môže navrhnúť parallel tool calls, no deterministic executor uplatní concurrency policy.

Race-sensitive business operations používajú locks, compare-and-set alebo serializable ledger. Model confidence nevyrieši race.

## 18. Retries

Engine retryuje podľa typed failure class a backoffu. Agent môže meniť approach pri reasoning failure, ale external side effect retry zostáva deterministic.

Nested retries sú nebezpečné: agent tool retry, SDK retry a engine retry môžu násobiť attempts. Retry budget sa vlastní na jednej vrstve.

## 19. Timeouts

LLM call timeout, tool timeout, task timeout a whole-workflow deadline sú odlišné. Každý má vlastnú recovery semantics.

Agent timeout môže vrátiť inconclusive; workflow deadline môže spustiť escalation. Timeout external mutation vytvára unknown outcome.

## 20. Cancellation

Workflow cancellation zastaví nové work a signalizuje running tasks. External provider operation môže pokračovať.

Agent stop token nezaručuje rollback. Cancellation path reconciliuje possibly-executed side effects.

## 21. Versioning

Long-running workflows môžu prežiť code deploy. Engine potrebuje versioning strategy pre existing executions a worker compatibility.

Agent prompt, model, tool schema a policy versions sa pinne v execution. Resume nesmie silently použiť nové generation.

## 22. Serialization

Persisted workflow a agent state musí byť versioned a migratable. LangGraph Functional API vyžaduje JSON-serializable inputs a outputs pre checkpointing.

Custom Python object alebo vendor handle v state môže zablokovať restore. Canonical schemas majú migration tests.

## 23. Human-in-the-loop

Agent framework môže pause-nuť tool call a ponúknuť approve, edit alebo reject. Workflow engine môže mať approval step alebo awaiting-input state.

Architecture určí jednu approval authority. Dve nezávislé approval vrstvy nesmú umožniť bypass alebo conflicting decisions.

## 24. Observability

Workflow engine poskytuje execution, task a retry timeline. Agent framework poskytuje prompts, trajectories, tool calls a checkpoints.

Correlation spája workflow ID, agent run ID, tool operation ID, trace ID a business key. Jeden dashboard bez cross-links je neúplný.

## 25. Audit

Engine audit preukazuje transitions a actor actions. Agent trace ukazuje proposals a observations. Provider a business ledger preukazujú side effects.

Agent chain-of-thought nie je required audit artifact. Ukladajú sa decisions, tool arguments, evidence references a policy outcomes podľa privacy policy.

## 26. Scaling

Workflow engine škáluje schedulers, queues a workers podľa task loadu. Agent framework škáluje model calls, token throughput a tool concurrency.

Bottleneck môže byť provider rate limit, database connection alebo approval backlog. Replica count nie je univerzálna capacity metric.

## 27. Cost

Agent framework pridáva model latency a variable token cost. Engine pridáva persistence, queue a operations cost.

Cost model meria per business outcome. Lacnejší modelový call, ktorý zvyšuje retries alebo human review, nemusí znížiť total cost.

## 28. Failure domains

Engine outage, checkpoint store outage, model outage, tool outage a provider outage sú samostatné failure domains. Fallback matrix určí, čo môže pokračovať.

Pri model outage môže deterministic workflow queue-nuť alebo prepnúť na human path. Nesmie automaticky preskočiť safety gate.

## 29. Security boundary

Engine identity má access k orchestration store a task dispatchu. Agent identity má iba potrebné read tools alebo bounded mutation adapter.

Prompt injection nesmie získať engine admin capabilities. Tool broker enforce-uje scope mimo modelu.

## 30. Testing

Workflow tests pokrývajú transitions, retries, timers, cancellation a version upgrades. Agent evals pokrývajú tool selection, groundedness, trajectory a refusal.

Integration test spája obe vrstvy a injectne failures. Green eval bez durable recovery testu nestačí.

## 31. Decision matrix

Voľba nie je binary produkt comparison, ale rozdelenie responsibilities. Ak proces vyžaduje exact state, multi-day waits, retries a compliance audit, engine vlastní shell.

Ak hlavná hodnota vzniká flexible reasoningom nad read-only tools a low-risk outputom, agent framework môže vlastniť väčšiu časť flow. High-impact writes zostávajú bounded.

## 32. Anti-pattern: agent ako scheduler

Agent v slučke polluje ticket, čaká cez sleep a drží memory v process RAM. Crash stratí position a retry môže zopakovať action.

Scheduler, event trigger alebo durable timer má vlastniť wake-up. Agent sa spustí až s exact work itemom.

## 33. Anti-pattern: engine ako reasoning model

Pipeline obsahuje desiatky brittle branches, ktoré napodobňujú prirodzené rozhodovanie nad neštruktúrovaným textom. Maintenance rastie a exceptions explodujú.

Agent môže vytvoriť typed classification s confidence a evidence. Engine potom deterministicky routuje podľa contractu.

## 34. Positive acceptance

Engine vytvorí stable execution, agent v bounded tasku navrhne action, validator overí schema a policy, human schváli a idempotent activity vykoná side effect.

Po worker crashi sa execution obnoví bez duplicate operation. Audit koreluje engine, agent, provider a business evidence.

## 35. Forbidden acceptance

Agent checkpoint nesmie byť jediným approval ledgerom ani business recordom. Replay nesmie opakovať external mutation.

Workflow status `success` nesmie vzniknúť pri invalid alebo unknown agent outpute. Hidden agent loop nesmie obísť deadline a kill switch.

## 36. Recovery acceptance

Po crashi medzi provider acknowledgment a checkpointom engine obnoví execution do reconciliation state, nie do blind retry. Provider read-back potvrdí outcome.

Po model outage sa process prepne na human queue bez straty subjectu. Second scenario testuje cancellation počas approval waitu a code version upgrade.

## 37. Practical responsibility split

Responsibility manifest zabraňuje tomu, aby dva runtimes vlastnili rovnaký state alebo retry. Každá concern má jedného authority ownera a explicitné evidence.

Nasledujúci príklad používa agent framework iba ako bounded diagnostic activity:

```yaml
process:
  capability: production-incident-remediation
  workflow_engine:
    owns:
      - execution-state
      - timers
      - retries
      - approval-state
      - operation-ids
      - cancellation
    durable_store: workflow-db
  agent_runtime:
    owns:
      - diagnosis-trajectory
      - evidence-summary
      - remediation-proposal
    limits:
      max_iterations: 8
      mutation_tools: []
  domain_system:
    owns:
      - incident-record
      - business-state
  mutation_adapter:
    requires:
      - policy-allow
      - unexpired-approval
      - stable-operation-id
```

Manifest sa overí failure injectionom. Deklarácia bez crash, replay a duplicate tests nie je runtime proof.

## 38. Primary sources

Temporal dokumentácia na https://docs.temporal.io/ opisuje durable execution a obnovenie applications po crashes a outages. Apache Airflow 3.3 core model Dag, tasks, task instances a scheduler je na https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html, https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html a https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/scheduler.html.

LangGraph persistence, replay a checkpoint semantics dokumentuje https://docs.langchain.com/oss/python/langgraph/persistence. Interrupt behavior, vrátane opätovného spustenia celého node-u a požiadavky na idempotent side effects pred interruptom, je na https://docs.langchain.com/oss/python/langgraph/interrupts. Functional API serialization a determinism constraints sú na https://docs.langchain.com/oss/python/langgraph/functional-api. n8n execution history a retry s original alebo current saved workflow opisuje https://docs.n8n.io/workflows/executions/all-executions/. Tieto sources ukazujú odlišné execution semantics; architecture authority musí vychádzať z business invariants a failure modelu konkrétneho procesu.

## Zhrnutie

Workflow engine má vlastniť durable process state, timers, retries, concurrency a approval lifecycle. Agent framework má vlastniť probabilistické reasoning, memory a tool-selection trajectory v presne ohraničenom tasku. Najbezpečnejší pattern je deterministic shell s agentic islands, stable operation IDs a independent business verification.

Ďalšia kapitola porovná konkrétne use cases n8n, Temporal, Airflow a Prefect.
