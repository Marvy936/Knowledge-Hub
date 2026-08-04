# Deterministic workflow, probabilistic component a autonomous agent

Agentická architektúra nezačína výberom frameworku, ale rozhodnutím, ktorá časť systému má zostať deterministická a kde je skutočne potrebné modelové rozhodovanie. Každé pridanie autonómie zvyšuje priestor možných trajectories, počet failure modes, potrebu observability a náklady na acceptance. Správny návrh preto nepovažuje „agent“ za synonymum pre každú aplikáciu s LLM, tool callingom alebo viacerými krokmi.

V incidente `AGENT-OPS-01` checkout alert vstúpil priamo do broad operations agenta. Deterministický enrichment alertu, tenant resolution, deployment read-back a policy routing boli nahradené promptom „diagnostikuj a oprav problém“. Agent dostal read aj mutation tools, z neúplných metrík usúdil, že payment workload potrebuje restart, po timeoute tool zopakoval a za úspech označil vlastné summary. Business checkout conversion sa pritom neobnovila. Root cause nebol iba nesprávny modelový úsudok; architektúra odovzdala probabilistickému komponentu rozhodnutia, ktoré mali mať deterministický contract a acceptance.

## 1. Exact architecture subject

Hodnotenie sa robí pre konkrétny business task, environment, risk tier, available evidence a side-effect boundary. Veta „používame agentov na incident response“ nehovorí, čo model rozhoduje, ktoré kroky sú fixné a aký outcome smie meniť.

```yaml
architecture_subject:
  capability: checkout-incident-assistance
  business_goal: restore-checkout-conversion
  environment: production-eu
  risk_tier: high
  workflow_release: incident-flow-v12
  model_route_policy: ops-router-v8
  tool_catalog: ops-tools-v14
  autonomy_policy: diagnosis-readonly-v5
```

Bez exact subjectu nemožno porovnať intended design s runtime behaviorom. Rovnaký prompt môže byť bezpečný v read-only sandboxe a neprijateľný pri produkčných mutation tools.

## 2. Deterministický workflow

Deterministický workflow má vopred definované states, transitions, inputs, validations a failure branches. Rovnaký validný vstup a rovnaký authoritative state vedú cez rovnakú control-flow štruktúru, aj keď niektoré kroky môžu volať externé alebo probabilistické služby.

```text
alert received
→ validate schema
→ resolve service and tenant
→ collect pinned metric window
→ read deployment and config state
→ classify severity by policy
→ route to read-only diagnosis or human owner
```

Deterministický neznamená, že každý výstup je matematicky identický. Znamená to, že orchestration, policy boundaries a allowed transitions neurčuje voľne model počas runtime.

## 3. Probabilistický komponent

Probabilistický komponent vykonáva ohraničenú úlohu v deterministickom procese. Môže klasifikovať ticket, zhrnúť logy, extrahovať entities alebo navrhnúť hypotheses, ale jeho input, output schema a downstream použitie sú vopred určené.

```text
workflow step: summarize incident evidence
input: exact evidence bundle
output: typed summary + uncertainty + cited artifact IDs
next transition: fixed policy code
```

Modelový výstup nie je sám rozhodovací authority. Workflow ho validuje a používa len v rozsahu contractu.

## 4. Autonomous agent

Autonomous agent dynamicky volí ďalšie kroky, tools alebo poradie práce podľa observations, state a cieľa. Autonómia preto nie je vlastnosť modelu samotného, ale orchestration boundary, ktorá modelu povoľuje meniť control flow.

```text
observe current state
→ choose next action
→ execute bounded tool
→ inspect result
→ update plan and state
→ terminate or continue
```

Agent môže byť stále silno obmedzený tool catalogom, budgetmi a approval gates. Autonómia nie je binárna vlastnosť „má alebo nemá“; je to rozsah decisions, resources, času a side effects, ktoré systém deleguje.

## 5. Agentic system versus agent

Agentic system je širší pojem. Môže obsahovať deterministické workflow patterns, modelové routery, evaluator-optimizer loop alebo plne dynamického agenta.

Architektúra musí pomenovať, ktorý element riadi control flow. Ak branch vyberá program podľa fixných rules, ide o workflow aj vtedy, keď branch obsahuje LLM call. Ak model vyberá ďalší tool a rozhoduje, či pokračovať, vzniká agentická decision boundary.

## 6. Augmented LLM

LLM s retrievalom, memory alebo tools ešte nemusí byť agent. Augmentation rozširuje dostupný context alebo capabilities, ale agent vzniká až vtedy, keď model používa tieto capabilities na dynamické riadenie trajectory.

Jednorazový call s povinným `search_policy` toolom a následným typed outputom môže byť deterministicky orchestrated component. Rovnaký model s voľbou medzi search, ticket read, deployment inspection, restart a termination už riadi významnú časť procesu.

## 7. Control-flow authority

Najdôležitejšia otázka je, kto určuje ďalší krok. Authority môže byť v application code, policy engine, human approval alebo v modelovej decision.

```yaml
control_flow:
  intake_validation: deterministic-code
  evidence_collection: deterministic-code
  hypothesis_generation: model
  mutation_selection: forbidden
  mutation_approval: human-owner
  post-change_verification: deterministic-code
```

Toto rozdelenie je presnejšie než marketingový label „agent“. Ukazuje, kde je modelový judgment povolený a kde nie.

## 8. Decision uncertainty

Probabilistický output má uncertainty a distribučný charakter. Aj pri nízkej temperature môžu model version, context ordering alebo provider behavior zmeniť výsledok.

Preto sa model nepoužíva ako skrytá implementácia deterministic policy. Ak business rule znie „refund nad 500 € vyžaduje dve approvals“, pravidlo patrí do policy engine, nie do promptu.

## 9. Predictability a flexibility

Workflow poskytuje vysokú predictability, jednoduchší testing a menší search space. Agent poskytuje flexibility pri tasks, kde nemožno vopred rozumne enumerovať všetky kroky alebo observations.

Trade-off nie je „starý workflow verzus inteligentný agent“. Je to výmena medzi kontrolou a adaptivitou, ktorá musí mať merateľný business dôvod.

## 10. Complexity budget

Každý agentický element spotrebúva complexity budget. Pridáva trajectories, tool combinations, state transitions, retry paths a evaluation cases.

```yaml
complexity_budget:
  max_turns: 8
  max_tools_per_run: 12
  max_parallel_actions: 2
  max_external_writes: 0
  max_cost_usd: 0.50
  max_wall_clock_seconds: 90
```

Budget obmedzuje blast radius a zároveň núti návrh pomenovať, koľko autonomy je pre task skutočne potrebné.

## 11. Autonomy dimensions

Autonómia má viac osí. Agent môže voľne plánovať, ale používať iba read tools; alebo môže mať fixný plan, no vykonávať high-impact writes.

Relevantné dimensions sú tool selection, step ordering, resource scope, number of turns, delegation, external communication, financial impact a reversibility. Risk assessment sa robí nad každou osou samostatne.

## 12. Read-only diagnosis

Read-only diagnosis je typický prvý agentický use case. Agent môže dynamicky vyberať queries a prepájať evidence, ale nemôže meniť produkčný stav.

Aj read-only agent však môže spôsobiť disclosure, vysoké náklady alebo incident amplification cez broad queries. Read-only preto znamená nulový mutation authority, nie nulové riziko.

## 13. Recommendation agent

Recommendation agent navrhne akciu, no nevykoná ju. Výstup obsahuje exact target, preconditions, expected effect, risk a evidence.

Human alebo deterministic policy potom rozhodne, či sa návrh zmení na executable command. Text „odporúčam restart“ bez exact workload generation, reason a verification plan nie je production-ready recommendation.

## 14. Approval-bound agent

Approval-bound agent môže pripraviť mutation, ale execution sa pozastaví na explicitnom gate. Approval musí zobrazovať canonical action, resource, arguments, expected impact a rollback.

Generic otázka „Proceed?“ nie je dostatočná. Schválenie sa viaže na action digest, aby agent po approval nemohol zmeniť target alebo payload.

## 15. Bounded autonomous agent

Bounded agent môže samostatne vykonávať iba nízkorizikové a reverzibilné operations. Napríklad môže vytvoriť diagnostický snapshot alebo dočasne zvýšiť log level v sandboxe.

Boundary je enforce-nutá mimo modelu. Prompt „nevykonávaj nebezpečné akcie“ nie je authorization control.

## 16. Fully autonomous high-impact agent

Agent s broad production writes, externým egressom a voľným termination rozhodnutím má veľký blast radius. Taký návrh potrebuje výnimočne silný business case, independent policy enforcement, durable audit, kill switch a recovery evidence.

Defaultný postoj nemá byť „agent to možno zvládne“. Default je najmenšia autonómia, ktorá dosiahne požadovaný outcome.

## 17. Task suitability

Agent je vhodný tam, kde je task open-ended, observations vznikajú postupne a ďalší krok závisí od predchádzajúceho výsledku. Príkladom môže byť komplexná read-only incident diagnosis cez heterogénne systémy.

Workflow je vhodnejší tam, kde sú steps, validations a error paths dobre známe. Password reset, invoice approval policy alebo schema migration promotion sa nemajú stať agentickými len preto, že LLM vie generovať text.

## 18. Environment uncertainty

Agentická flexibilita má zmysel, keď environment nemožno kompletne modelovať vopred. Zároveň však observations musia mať provenance a freshness.

Agent, ktorý reaguje na stale cache alebo neúplný log sample, nevykazuje inteligentnú adaptáciu. Iba dynamicky koná nad nesprávnym state representation.

## 19. Business invariant

Každý agentický task potrebuje invariant, ktorý model nesmie prekročiť. Invariant je deterministic rule alebo authoritative postcondition.

```yaml
business_invariants:
  - no_cross_tenant_access
  - no_duplicate_refund
  - no_production_restart_without_approval
  - checkout_conversion_must_not_decrease
```

Invariant sa overuje pred aj po action. Fluent agent response ho nemôže nahradiť.

## 20. Outcome contract

Task completion sa definuje cez business outcome, nie cez modelový pocit dokončenia. Agent môže správne vytvoriť ticket, ale task „obnov checkout“ nie je hotový, kým authoritative metric a transaction flow nepotvrdia recovery.

Outcome contract obsahuje success, forbidden a unknown states. Unknown outcome vedie k read-backu alebo eskalácii, nie k optimistickému successu.

## 21. Architecture ladder

Návrh začína najjednoduchšou architektúrou a autonomy pridáva iba po preukázanej potrebe.

```text
rules / code
→ single model call
→ model call with retrieval
→ fixed workflow with several model calls
→ router or evaluator workflow
→ read-only agent
→ approval-bound mutation agent
→ bounded autonomous agent
```

Preskočenie priamo na broad agent zväčšuje eval a operations burden bez dôkazu, že jednoduchší pattern nestačí.

## 22. Hybrid architecture

Najpraktickejšie systems sú hybridné. Deterministický shell riadi identity, policy, budgets, retries, approvals a acceptance; agentická časť rieši iba nepredvídateľnú diagnosis alebo planning časť.

```text
fixed intake and enrichment
→ bounded agentic diagnosis
→ typed recommendation
→ deterministic policy and approval
→ deterministic execution
→ authoritative verification
```

Taký návrh zachováva flexibility bez odovzdania celého lifecycle modelu.

## 23. Framework versus architecture

Framework môže poskytovať agent loop, persistence alebo tools, ale neurčuje správnu business boundary. Použitie `Agent`, `Runner` alebo graph node triedy samo osebe nepreukazuje agentický design.

Architecture decision record musí vysvetliť control-flow authority, tool permissions, state ownership a termination. Framework je implementačný mechanizmus, nie evidence správneho návrhu.

## 24. Testing surface

Workflow testuje known transitions a branch conditions. Agent potrebuje navyše trajectory tests, tool-selection tests, budget tests, adversarial observations a outcome evaluation.

Počet možných paths rastie kombinatoricky. Preto sa high-risk operations presúvajú do deterministických gates, ktoré dramaticky zmenšia acceptance surface.

## 25. Observability surface

Workflow trace ukazuje execution predefined steps. Agent trace musí zachytiť observations, selected actions, tool calls, state mutations, budgets, approvals a termination reason.

Raw chain-of-thought sa nepovažuje za požadovaný observability artifact. Potrebný je stručný structured decision record a causal operation graph, nie skryté interné reasoning tokeny.

## 26. Cost a latency

Agentická slučka zvyšuje počet model calls, tool calls a retry paths. Vyššia task success môže byť legitímna výmena za cost a latency, ale musí sa merať per accepted outcome.

Porovnanie iba ceny jedného model callu zavádza. Workflow s tromi callmi môže byť lacnejší a spoľahlivejší než agent s priemerom dvanásť turns.

## 27. Security boundary

Autonómia zosilňuje účinok prompt injection, tool poisoning a confused-deputy problémov. Neoverená observation môže zmeniť plan a následne vyvolať privileged action.

Security controls preto obmedzujú capability mimo modelu: least privilege, resource authorization, egress policy, typed tools, approval a sandboxing. Model refusal je defense-in-depth, nie primary boundary.

## 28. Human role

Human-in-the-loop nie je univerzálna náhrada za design. Operátor potrebuje jasnú evidence, bounded choice a dostatok času; inak vzniká automation bias a rubber-stamp approval.

Human gate sa umiestňuje pred consequential action alebo pri uncertainty, ktorú nemožno bezpečne vyriešiť automaticky. Rutinné deterministické validations sa nemajú presúvať na človeka.

## 29. Incident diagnosis

Pri incidente sa najprv zisťuje, či zlyhal deterministický shell, probabilistický komponent alebo agentická control-flow decision. Rovnaký user-visible symptom môže mať odlišný recovery path.

V `AGENT-OPS-01` sa overuje, či alert enrichment poskytol správny tenant a time window, či agent dostal správny tool catalog, či mutation policy dovolila restart a či business acceptance vôbec prebehla. Root cause sa nehľadá iba v poslednej model response.

## 30. Failure hypotheses

Pri agentickom incidente zostávajú otvorené viaceré competing hypotheses. Architecture classification môže byť nesprávna, deterministický step mohol byť omylom delegovaný modelu, autonomy policy mohla mať broad scope alebo runtime mohol načítať inú generation než desired state.

Ďalšou cestou je nesprávny observation bundle, tool authorization gap, chýbajúca approval binding alebo termination podľa self-reported successu. Každá hypotéza má vlastný authoritative read-back a nesmie sa uzavrieť iba replayom jednej modelovej odpovede.

## 31. Containment

Containment znižuje autonomy skôr, než sa začne prompt tuning. High-risk tools sa odoberú, flow sa prepne do read-only alebo recommendation mode a zachová sa operation evidence.

Ak je bezpečné pokračovať, deterministický fallback môže vykonať známy runbook. Ak nie, task sa eskaluje človeku s exact state a unresolved hypotheses.

## 32. Recovery

Recovery obnoví known-good architecture release vrátane workflow graphu, model route, tool catalogu, autonomy policy a approval rules. Nestačí zmeniť model alias.

Po obnove sa overí loaded state a spustí incident case aj benign controls. Business read-back musí potvrdiť outcome a absenciu duplicate alebo unauthorized side effects.

## 33. Positive acceptance

Pozitívna acceptance dokazuje, že zvolený architecture level rieši reprezentatívne tasks s požadovanou quality, latency, cost a operator burden. Pri workflow sa overujú transitions; pri agente aj trajectory a termination.

Acceptance musí porovnať jednoduchšiu baseline. Agent sa neakceptuje iba preto, že dokáže task dokončiť; musí priniesť merateľnú hodnotu oproti menej autonómnej alternatíve.

## 34. Forbidden acceptance

Forbidden acceptance dokazuje, že agent nemôže prekročiť resource, tenant, cost, turn, egress alebo mutation boundary. Prompt injection, stale observation a tool timeout nesmú viesť k unauthorized alebo duplicate action.

Kontrola sa vykonáva authoritative business read-backom. Absencia modelového priznania nie je dôkaz, že side effect nevznikol.

## 35. Second-operation acceptance

Second-operation test spustí ďalší task po policy, model alebo workflow update. Overí, že runtime načítal novú generation a nepoužil stale session, plan alebo tool catalog.

Alternate-scenario test zmení tenant, severity a typ incidentu. Cieľom je potvrdiť architecture boundary, nie memorovaný happy path `AGENT-OPS-01`.

## 36. Čo dokumentačná validácia nepreukazuje

Repository checks môžu overiť prose, links, schemas a konzistenciu architecture modelu. Nepreukazujú reálnu trajectory quality, tool authorization, operator approvals, production side effects ani business recovery.

Runtime stav `Verified` vyžaduje vykonané workflow a agent evals na exact release. Produkčný stav `Stable` vyžaduje časové evidence, incident handling a úspešné recovery drills.

## Primárne zdroje

- [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [OpenAI Agents SDK — Running agents](https://openai.github.io/openai-agents-python/running_agents/)
- [LangGraph — Workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)

## Kontrolné otázky

1. Ktoré decisions musí vykonať deterministic code a ktoré skutočne potrebujú modelový judgment?
2. Kto riadi ďalší krok: program, policy engine, človek alebo model?
3. Aký je najnižší autonomy level, ktorý dosiahne požadovaný business outcome?
4. Sú invariants a side-effect boundaries enforce-nuté mimo promptu?
5. Porovnáva acceptance agenta s jednoduchšou workflow baseline?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: LLM application troubleshooting](../20-llm-and-genai-engineering/llm-application-troubleshooting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Agent loop, state, observation, action a termination →](agent-loop-state-observation-action-termination.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
