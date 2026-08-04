# Planning, decomposition a replanning

Agentický plan je explicitná, versioned predstava o tom, ako sa má current goal rozložiť na overiteľné kroky. Nie je to neomylný program ani povinné zverejnenie interného chain-of-thought. Je to operational artifact, ktorý pomenúva subgoals, dependencies, preconditions, expected observations, risk a termination evidence tak, aby runtime, tools a človek vedeli kontrolovať execution.

V incidente `AGENT-OPS-01` operations agent vytvoril implicitný plan „pozri metriky, restartuj payment workload, over zdravie“. Plan neuviedol, že checkout error môže pochádzať z gateway, dependency alebo stale telemetry; nevyžadoval deployment generation ani approval a po tool timeoute nereplanoval podľa unknown outcome-u. Agent pokračoval podľa pôvodného predpokladu a uzavrel task po technickom health checku bez business conversion evidence. Problém nebol iba zlý prvý krok, ale chýbajúca plan identity, preconditions, observation-driven replanning a acceptance.

## 1. Exact planning subject

Plan sa viaže na exact goal, run state, release, principal a autonomy policy. Rovnaký text plánu nad iným environmentom alebo tool catalogom nie je rovnaký execution subject.

```yaml
planning_subject:
  plan_id: plan-ops-8841-v3
  run_id: run-ops-8841
  goal: restore-checkout-conversion
  state_generation: 17
  tool_catalog: ops-tools-v14
  autonomy_policy: diagnosis-readonly-v5
  created_at: 2026-08-04T14:14:00Z
```

Plan musí uvádzať state generation, z ktorej vychádza. Po podstatnej state zmene sa revaliduje alebo nahradí.

## 2. Goal contract

Planning začína goal contractom. Goal obsahuje desired outcome, scope, constraints, forbidden outcomes a completion evidence.

```yaml
goal:
  desired_outcome: checkout-conversion-within-slo
  scope: production-eu
  constraints:
    - read-only-diagnosis
    - no-cross-tenant-data
  forbidden:
    - production-mutation-without-approval
  completion_evidence:
    - root-cause-supported-by-authoritative-evidence
    - bounded-remediation-recommendation
```

Vágny goal „oprav checkout“ vedie k vágnej trajectory a nebezpečnému termination rozhodnutiu.

## 3. Plan versus policy

Plan navrhuje sequence práce; policy určuje, ktoré actions sú povolené. Agent nemôže plánom rozšíriť vlastné permissions.

Ak plan obsahuje restart, no autonomy policy povoľuje iba read tools, runtime action odmietne alebo vytvorí approval-bound recommendation. Policy je authoritative boundary mimo plánu.

## 4. Plan versus chain-of-thought

Production plan nemá obsahovať raw private reasoning tokeny. Potrebuje stručné, auditovateľné steps, dependencies a evidence expectations.

```text
subgoal: overiť deployment regression
reason code: recent-release-correlation
required observation: loaded image, rollout generation, error-rate split
```

Tento artifact je dostatočný pre debugging bez požiadavky na interný chain-of-thought.

## 5. Explicit a implicit planning

Implicit planning vzniká, keď model vyberá ďalší action bez samostatného plan artifactu. Je vhodné pre krátke a nízkorizikové tasks.

Explicit planning je vhodnejšie pri long-horizon, costly alebo consequential tasks. Umožňuje precondition validation, approval, progress tracking a controlled replanning.

## 6. Planning horizon

Planning horizon určuje, koľko krokov sa navrhne dopredu. Príliš krátky horizon môže viesť k myopickým actions; príliš dlhý plan sa rýchlo stane stale.

Praktický agent vytvára high-level milestones a detailne plánuje iba najbližší bounded segment. Po nových observations rozšíri alebo upraví ďalšie kroky.

## 7. Decomposition

Decomposition rozdeľuje goal na subgoals, ktoré majú vlastný output a acceptance. Dobré subgoals znižujú uncertainty alebo vytvárajú prerequisite pre neskorší action.

```text
1. potvrď rozsah incidentu
2. zisti first-change correlation
3. over service a dependency state
4. vyraď competing hypotheses
5. priprav bounded recommendation
6. over recommendation proti policy a rollbacku
```

Zoznam nie je úspešný plan, kým steps nemajú dependencies a expected evidence.

## 8. Atomicity kroku

Step má byť dosť malý na jednoznačný outcome, ale nie taký malý, aby plan kopíroval každý model token alebo HTTP call. Atomicity sa riadi decision boundary.

„Diagnostikuj databázu“ je príliš široké. „Porovnaj current connection saturation s pre-incident baseline pre exact cluster“ má jasný subject a observation.

## 9. Step contract

Každý step má input state, preconditions, allowed actions, expected observation, success a failure branch.

```yaml
step:
  id: s3
  subgoal: verify-payment-rollout
  preconditions:
    - affected_region_resolved
    - deployment_read_permission
  allowed_tools:
    - kubernetes.read_rollout
    - metrics.query
  success_evidence:
    - rollout_generation
    - image_digest
    - error_rate_by_replica
```

Contract umožňuje deterministic validation pred modelovým action selectionom.

## 10. Dependencies

Dependencies tvoria directed graph. Step nemá začať, kým jeho required artifacts neexistujú alebo nie sú fresh.

Parallelization sa povoľuje iba medzi nezávislými steps. Shared resource mutation alebo spoločný budget môže vytvoriť hidden dependency, ktorú plan musí uviesť.

## 11. Critical path

Critical path je sequence, ktorá určuje minimálny čas dokončenia. Agent môže prioritizovať observations s najvyššou informačnou hodnotou alebo blokujúcim významom.

Latency optimization nesmie preskočiť safety preconditions. Rýchlejší plan, ktorý spustí write pred authorization alebo unknown-outcome reconciliation, je nesprávny.

## 12. Evidence-first planning

Plan nezačína obľúbenou remediation. Začína evidence potrebnou na rozlíšenie competing hypotheses.

V `AGENT-OPS-01` musí agent najprv potvrdiť incident scope, deployment generation a dependency health. Restart bez tejto evidence iba mení environment a komplikuje root-cause analysis.

## 13. Hypothesis-driven planning

Hypothesis má claim, supporting evidence, contradicting evidence a next discriminating action. Plan vyberá krok, ktorý najlepšie zníži uncertainty.

```yaml
hypothesis:
  id: h1
  claim: new-payment-image-causes-errors
  supports: [recent-rollout]
  contradicts: []
  next_test: compare-error-rate-by-image-digest
```

Agent nemá uzatvoriť hypothesis po jednom korelovanom signále.

## 14. Information value

Nie všetky tool calls majú rovnakú hodnotu. Query, ktorá odlíši tri root-cause paths, môže byť užitočnejšia než desať broad log searches.

Plan môže odhadovať expected information gain, cost a risk. Runtime nemusí akceptovať numerickú presnosť od modelu, ale môže vyžadovať reason code pre každý step.

## 15. Feasibility

Plan sa validuje proti current tool catalogu, permissions, budgets a environmentu. Model môže navrhnúť conceptually správny krok, ktorý nie je executable.

Feasibility checker označí chýbajúci tool, forbidden resource alebo nedostatočný čas. Agent potom replan-ne na alternate evidence path alebo eskaláciu.

## 16. Plan validation

Pred execution sa kontroluje schema, goal alignment, dependency graph, policy, cycles, budgets a terminal evidence. Deterministické validators majú prednosť pred modelovým reviewerom.

Modelový critic môže identifikovať semantic gaps, ale nemá sám schvaľovať vlastný high-risk plan. Independent policy alebo človek zostáva authority.

## 17. Risk-aware planning

Každý step nesie risk metadata. High-impact alebo irreversible action sa posúva neskôr, až po získaní evidence a approval.

```text
read exact state
→ simulate or dry-run
→ prepare action preview
→ obtain approval
→ execute bounded mutation
→ verify and reconcile
```

Toto poradie znižuje blast radius a podporuje recovery.

## 18. Plan approval

Pri consequential tasku môže človek schváliť celý bounded plan alebo konkrétny step. Approval zobrazuje canonical targets, expected side effects a rollback.

Blanket approval „vykonaj plán“ je nebezpečný, ak plan povoľuje dynamic target alebo future replanning. Replanned high-risk step potrebuje nové approval.

## 19. Execution plan a runtime state

Plan nie je jediný source of truth. Runtime state zaznamenáva completed, skipped, failed, blocked a invalidated steps.

Plan version zostáva immutable a zmeny vytvárajú novú version alebo amendment event. Tým sa zachová, čo agent pôvodne zamýšľal a prečo trajectory zmenil.

## 20. Observation-driven progress

Step sa nepovažuje za completed len preto, že tool call skončil. Musí vzniknúť expected observation alebo explicitný terminal outcome.

Ak query vráti partial data, step môže byť `incomplete` alebo `blocked`. Model summary nesmie premeniť chýbajúci artifact na success.

## 21. Replanning trigger

Replanning sa spustí pri novej evidence, failed precondition, tool error, budget zmene, policy zmene, approval rejection, detected cycle alebo environment drift-e. Trigger je explicitný event.

Agent nemá prepisovať plan po každom turne bez dôvodu. Excessive replanning znižuje auditability a spotrebúva tokens bez progressu.

## 22. Replanning scope

Replan môže upraviť jeden step, zostávajúci segment alebo celý plan. Scope sa volí podľa veľkosti divergence.

Tool rate limit môže zmeniť iba timing. Zistenie, že incident postihuje inú dependency, môže invalidovať celú root-cause branch.

## 23. Preserve completed work

Replanning nemá opakovať completed side effects alebo fresh observations bez dôvodu. State označuje reusable artifacts a ich validity window.

Ak sa však zmenil relevantný resource generation, starý observation sa invaliduje. Reuse je policy rozhodnutie, nie modelový odhad.

## 24. Unknown outcome

Unknown tool outcome je špeciálny replanning trigger. Plan nesmie zaradiť rovnakú mutation ako nový krok, kým read-back neurčí, či pôvodná action commitla.

Reconciliation step má vyššiu prioritu než pokračovanie k ďalšiemu subgoalu. Inak plan vytvára duplicate side effects.

## 25. Failed action

Explicitný failure môže viesť k retry, alternate toolu, zmenenému argumentu alebo eskalácii. Výber závisí od error taxonomy a retry contractu.

Agent nemá interpretovať authorization denial ako technický failure, ktorý obíde iným toolom. Denial mení feasible action space.

## 26. Counterevidence

Nová observation môže priamo vyvrátiť plan assumption. Replan zaznamená, ktorý assumption sa stal invalidný a ktoré steps tým strácajú význam.

Táto causal link je dôležitá pre debugging a evals. Bez nej sa trajectory javí ako náhodné preskakovanie medzi tools.

## 27. Plan drift

Plan drift vzniká, keď execution pokračuje podľa starého planu napriek zmene state, policy alebo goalu. Runtime kontroluje state generation a preconditions pred každým stepom.

Dlhé sessions a external changes zvyšujú drift risk. Periodic revalidation je potrebná aj bez explicitného tool failure.

## 28. Goal drift

Agent môže počas dlhého runu zmeniť interpretáciu goalu. Summary task sa môže nepozorovane zmeniť na remediation task.

Goal contract je immutable alebo sa mení explicitným user/human eventom. Model nemôže sám rozšíriť scope na základe retrieved instruction.

## 29. Plan loops

Plan loop vzniká, keď agent opakuje rovnaké subgoals bez nového evidence. Cycle detector porovnáva step signatures, state a observations.

Runtime môže vyžiadať replan s explicitným alternate strategy alebo ukončiť run ako blocked. Nekonečný reasoning nie je progress.

## 30. Parallel planning

Nezávislé read-only steps sa môžu vykonať paralelne. Planner však musí uviesť join condition a conflict handling.

Parallel writes nad shared resource sú defaultne zakázané. Aj read queries môžu prekročiť rate alebo cost budget, preto scheduler zostáva authoritative.

## 31. Plan-and-execute pattern

Plan-and-execute oddeľuje planning call od executor loopu. Planner vytvorí steps, executor vykoná current step a replanner aktualizuje remaining plan podľa observation.

Pattern zlepšuje auditability pri dlhších tasks, ale pridáva model calls a synchronization. Pre krátky bounded task môže byť jednoduchý observe-act loop vhodnejší.

## 32. ReAct pattern

ReAct interleavuje reasoning a actions, takže observations môžu priebežne meniť ďalší krok. Praktická implementácia zachováva structured decision records a tool traces bez požiadavky ukladať private chain-of-thought.

Pattern je užitočný pri environmentoch, kde nemožno spoľahlivo naplánovať celú trajectory vopred. Runtime stále enforce-uje tools, budgets a termination.

## 33. Evaluator-optimizer pattern

Evaluator-optimizer vytvorí candidate a následne ho posúdi podľa success criteria. Feedback vedie k ďalšej iterácii.

Evaluator nemá byť jediný authority pre security alebo business policy. Deterministické validators a human approval zostávajú oddelené gates.

## 34. Planner quality

Planner sa hodnotí podľa goal coverage, dependency correctness, feasibility, risk ordering, efficiency a adaptability. Pekne formulovaný zoznam krokov nie je dôkaz quality.

Offline eval obsahuje tasks s missing toolom, conflicting evidence, approval rejectionom a dynamic environment change. Outcome eval musí overiť aj execution, nie iba plan text.

## 35. Plan compression

Dlhý plan a history môžu prekročiť context budget. Compression vytvára structured summary s preserved IDs, state versions, open hypotheses a pending actions.

Kompresia nesmie odstrániť authorization, unknown outcomes alebo approval bindings. Lossy natural-language summary bez provenance môže zmeniť semantics.

## 36. Cost a latency

Planning a replanning spotrebúvajú model calls. Meria sa cost per accepted outcome a avoided harmful action, nie iba token count planu.

Explicitný plan môže znížiť zbytočné tools, ale pri jednoduchom tasku môže byť overhead. Architecture ladder preto používa planning iba tam, kde prináša merateľnú hodnotu.

## 37. Security

Retrieved content alebo tool result môže navrhnúť malicious plan step. Planner input rozlišuje trusted instructions od untrusted data.

Plan validator blokuje egress, secret access a privilege escalation mimo task contractu. Human-readable plan nie je security control, ak runtime stále povoľuje forbidden tool.

## 38. Observability

Trace zaznamenáva plan ID, version, step IDs, replanning triggers, invalidated assumptions a terminal reason. Tool calls sa viažu na step a hypothesis.

Taký graph umožňuje nájsť first divergence: nesprávny goal, chybná decomposition, stale observation, wrong action alebo nesprávny replan. Samotný final answer túto diagnózu neumožní.

## 39. Failure hypotheses

Pri planning incidente sa paralelne overuje vague goal, missing decomposition, incorrect dependency, infeasible step, policy conflict, stale plan, unknown-outcome reuse, cycle, goal drift a nesprávna termination evidence. Každá hypotéza má plan/state/version evidence.

V `AGENT-OPS-01` prvou divergenciou mohol byť plan, ktorý spojil technical health s business recovery. Aj keby restart prebehol raz a správne, task by sa nesmel uzavrieť bez checkout conversion read-backu.

## 40. Containment

Containment pozastaví current plan, zablokuje pending high-risk steps a zachová completed action identities. Agent môže pokračovať iba v read-only evidence collection podľa novej policy.

Ak plan obsahuje malicious alebo broad steps, celý catalog/session sa revaliduje. Approval tokens sa revoke-nú, ak ich digest už nezodpovedá current planu.

## 41. Recovery

Recovery obnoví known-good planner prompt/release, state schema, tool catalog, policy a plan validator. Existing runs sa replan-nú alebo eskalujú podľa compatibility.

Incident task sa replay-ne so preserved observations a controlled tools. Acceptance musí potvrdiť nielen nový plan text, ale aj trajectory, side effects a business outcome.

## 42. Positive acceptance

Pozitívna acceptance dokazuje správnu decomposition, dependencies, evidence-first ordering a adaptáciu na nové observations. Agent dokončí task v budgete a s povolenými tools.

Porovnáva sa aj jednoduchší no-plan alebo fixed-workflow baseline. Explicitné planning sa akceptuje iba pri merateľnom zlepšení outcome alebo risk controlu.

## 43. Forbidden acceptance

Forbidden acceptance vloží prompt injection do observation, zmení resource generation po approval a vyvolá unknown tool outcome. Plan nesmie rozšíriť goal, obísť policy ani zopakovať mutation.

Cycle a budget tests musia skončiť blocked alebo escalated stavom s preserved evidence. Agent nesmie generovať nekonečné replans.

## 44. Second-operation acceptance

Second-operation test spustí podobný task po planner alebo tool update. Nový plan musí používať current catalog a nesmie zdediť hypotheses alebo approval z predchádzajúceho runu.

Alternate-scenario test zmení incident domain a required evidence. Cieľom je potvrdiť planning mechanismus, nie zapamätanú checkout trajectory.

## 45. Čo dokumentačná validácia nepreukazuje

Repository checks môžu overiť plan schemas a prose model. Nepreukazujú planner quality, replanning behavior, runtime policy, tool outcomes ani business acceptance.

Runtime `Verified` vyžaduje executed trajectory evals, dynamic-state tests a failure injection. Produkčný `Stable` stav vyžaduje časové evidence, incident response a recovery drills.

## Primárne zdroje

- [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- [OpenAI Agents SDK — Running agents](https://openai.github.io/openai-agents-python/running_agents/)
- [LangGraph — Workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents)

## Kontrolné otázky

1. Má plan exact goal, state generation, dependencies a completion evidence?
2. Rozlišuje explicitný operational plan od private chain-of-thought?
3. Ktoré observations, errors alebo policy changes spúšťajú replanning?
4. Ako sa unknown side-effect outcome reconciliuje pred zmenou planu?
5. Overuje acceptance execution trajectory a business outcome, nie iba kvalitu plan textu?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Tool calling a tool contracts](tool-calling-tool-contracts.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
