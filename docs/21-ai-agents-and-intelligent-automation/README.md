# AI Agents and Intelligent Automation

Sekcia začína hranicou medzi deterministickým workflowom, probabilistickým komponentom a autonómnym agentom. Agentické rozhodovanie sa pripúšťa iba s explicitným state, tool contractom, least privilege, approval hranicou, side-effect identity, auditom, kill switchom a overiteľným recovery pathom.

## Predpoklady

Odporúčané predchádzajúce oblasti:

- LLM and GenAI Engineering
- Git and Automation Basics
- CI/CD and Release Engineering
- SRE and Operations
- Keycloak and Identity Platform

## Authoritative poradie — aktívne kapitoly

1. [Deterministic workflow, probabilistic component a autonomous agent](deterministic-workflow-probabilistic-component-autonomous-agent.md)
2. [Agent loop, state, observation, action a termination](agent-loop-state-observation-action-termination.md)
3. [Tool calling a tool contracts](tool-calling-tool-contracts.md)
4. [Planning, decomposition a replanning](planning-decomposition-replanning.md)

## Plánované authoritative poradie

Nasledujúci inventory je schválený plán sekcie. Položka sa zmení na aktívny Markdown link až v pracovnom bloku, ktorý vytvorí a validuje príslušnú kapitolu. Tým sa plánovaný obsah nezamieňa za hotovú dokumentáciu.

5. Short-term state, long-term memory a external memory
6. Single-agent a multi-agent architecture
7. Supervisor, router a specialist patterns
8. Human-in-the-loop a approval gates
9. Durable execution, retries a resumability
10. Idempotency a side-effect control
11. Model Context Protocol
12. Agent interoperability a protocol evolution
13. Agent identity, authentication a authorization
14. Least privilege pre tools a credentials
15. Sandboxing a code execution
16. Prompt injection cez tools a retrieved content
17. Tool poisoning, confused deputy a data exfiltration
18. Agent evaluation
19. Trajectory, tool-selection a outcome evaluation
20. Agent tracing, replay a debugging
21. Cost, latency a token budgets
22. Agent reliability, fallback a kill switch
23. Multi-tenant isolation
24. Agent governance a audit
25. n8n architecture a execution model
26. Triggers, nodes, expressions a data mapping
27. Webhooks a API integrations
28. Credentials, secrets a access control
29. Error workflows, retries a partial execution
30. Idempotency a duplicate-event handling
31. Sub-workflows a reusable workflow contracts
32. Source control a environments
33. Self-hosting s PostgreSQL
34. Queue mode, Redis, workers a scaling
35. Binary data, storage a execution retention
36. n8n monitoring, logs a security audit
37. AI Agent nodes, tools a memory
38. Human approval pre citlivé tool calls
39. RAG a knowledge workflows v n8n
40. Production hardening a troubleshooting
41. Harness AI platform overview
42. DevOps Agent pre pipeline a resource operations
43. Worker Agents v pipelines
44. MCP connectors a external tools
45. AI-assisted pipeline creation a failure analysis
46. Agentický code review, testing a remediation
47. GitOps a release agents
48. Incident triage a evidence collection
49. Policy generation a policy validation
50. Human approval, audit a rollback
51. Vendor lock-in a portability agentických workflowov
52. Workflow engine oproti agent frameworku
53. n8n oproti Temporal, Airflow a Prefect use cases
54. Event-driven automation
55. AI-assisted CI/CD
56. AI-assisted observability a incident response
57. AI-assisted security operations
58. Knowledge assistants a enterprise search
59. Ticket, email a chat automation
60. Autonomous remediation boundaries
61. Evaluation-driven automation lifecycle
62. Intelligent automation troubleshooting

## Authoring a evidence štandard

Každá kapitola bude používať rovnaký prose-first štandard ako sekcie 00–17:

```text
business alebo user outcome
→ exact data/model/prompt/agent subject a generation
→ authority, trust a ownership boundary
→ internal lifecycle alebo mutation path
→ authoritative read-back a proof boundary
→ failure a competing hypotheses
→ containment a recovery
→ positive, forbidden a second-operation acceptance
```

Rýchlo sa meniace produkty, API a protokoly sa pri každom bloku znovu overia proti aktuálnym primárnym zdrojom. Dokumentácia nesmie zamieňať offline eval, control-plane status alebo úspešný tool call za produkčný business outcome.

## Praktická vrstva

Nosný end-to-end smer sekcie:

```text
alert alebo ticket → deterministic enrichment → agentic diagnosis → read-only tools → evidence a confidence → human approval → bounded remediation tool → validation → audit trail a rollback
```

Samostatné laby a troubleshooting drilly sa aktivujú až po dostatočnom koncepčnom základe. Dokumentačný workflow môže overiť súbory, príkazy a konzistenciu modelu, ale nepreukazuje vykonanie tréningu, inference, agentického side effectu ani produkčného outcome-u.

## Stav

Aktuálny authoritative stav sekcie je **4/62 · In progress**. Prvý authoritative blok aktivuje kapitoly 1–4 a incident `AGENT-OPS-01`. Architecture kapitola oddeľuje deterministic workflow, bounded probabilistic component a autonomous agent cez control-flow authority, autonomy dimensions, business invariants, complexity budget a architecture ladder. Agent-loop kapitola definuje exact run a operation identity, typed state, observation provenance a freshness, action outcomes, interruptions, budgets, cycle detection a deterministic termination. Tool-contract kapitola oddeľuje model proposal od schema a semantic validation, canonical resource resolution, authorization, approval, idempotency, timeout a retry semantics, postconditions, trust a versioned catalog. Planning kapitola zavádza explicitný versioned operational plan bez private chain-of-thought, evidence-first decomposition, dependencies, feasibility, risk ordering, observation-driven replanning, unknown-outcome reconciliation a trajectory acceptance. Kapitoly 1–4 sú pripravené na repository closeout; reálne agent runs, production tools, approvals, side effects, failure injection, recovery drills ani business outcomes neboli vykonané. Sekcia zostáva `In progress`, nie runtime `Verified`, production `Stable` ani user `Accepted`. Ďalší blok sú kapitoly 5–8: memory, single/multi-agent architecture, supervisor/router/specialist patterns a human approval gates.
