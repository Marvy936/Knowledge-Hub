# Single-agent a multi-agent architecture

Single-agent a multi-agent nie sú marketingové úrovne zrelosti. Sú to dve odlišné topológie riadenia, contextu, ownershipu a failure propagation. Jeden agent môže používať veľa nástrojov, dynamicky načítavať skills a vykonávať dlhý plán bez toho, aby išlo o multi-agent systém. Multi-agent architektúra vzniká až vtedy, keď viac samostatných agent loops alebo agent roles dostáva vlastný context, instructions, tool boundary a zodpovednosť za čiastkové rozhodnutie alebo výstup.

V incidente `AGENT-OPS-02` tím rozdelil incident response na supervisor, Kubernetes specialistu a database specialistu. Cieľom bolo paralelne skrátiť diagnostiku, ale obaja specialisti dostali mutation tools, zdieľaný scratchpad a nejasný task contract. Supervisor nevedel, ktorý agent vlastní finálnu remediation action, preto prijal dve podobné odporúčania a spustil ich paralelne. Multi-agent topológia nezlyhala preto, že mala „príliš veľa modelov“, ale preto, že neexistovali ownership, context-isolation, delegation, side-effect a synthesis pravidlá.

## 1. Single-agent architektúra

Single-agent architektúra má jeden agent loop, ktorý vlastní aktuálny plán, user-facing odpoveď a rozhodovanie o nástrojoch. Môže používať retrieval, memory, dynamic tool catalog, deterministic workflow nodes a approval gates. Kľúčové je, že neexistuje druhý samostatný agent loop s vlastnou decision authority.

Typický tok:

```text
input
→ one agent state and plan
→ one or more tool calls
→ observations
→ final answer or bounded action proposal
```

Single-agent neznamená monolitický kód. Tool executors, retrieval služby a policy engine môžu byť samostatné komponenty, ale nie sú agenti, pokiaľ samy nevykonávajú model-driven loop.

## 2. Multi-agent architektúra

Multi-agent architektúra koordinuje viac agentov, z ktorých každý môže mať vlastné instructions, model, context, tools, state a termination podmienky. Koordinácia môže byť centralizovaná supervisorom, riadená routerom, realizovaná handoffom alebo vložená do explicitného graphu.

Typický tok:

```text
input
→ routing or supervisor decision
→ specialist agent runs
→ typed specialist outcomes
→ synthesis or delegated ownership
→ business validation
```

Každý additional agent pridáva nový failure a cost surface. Preto sa multi-agent architektúra používa iba vtedy, keď merateľne zlepší outcome, izoláciu alebo paralelizáciu oproti jednoduchšiemu single-agent návrhu.

## 3. Agent count nie je architecture proof

Tri model calls neznamenajú tri agenti. Jeden workflow môže volať planner model, extractor model a evaluator model po pevnej trase; ide o multi-model workflow, nie nevyhnutne multi-agent systém. Naopak jeden model deployment môže obsluhovať viac logických agentov s rozdielnymi instructions, tools a state boundaries.

Architektúra sa identifikuje podľa control-flow authority:

```text
Kto rozhoduje o ďalšom kroku?
Kto vlastní context a state?
Kto môže delegovať?
Kto smie vykonať side effect?
Kto formuluje finálny outcome?
```

Odpovede sú dôležitejšie než počet model endpointov.

## 4. Exact architecture subject

Pri diagnostike a release musí byť topológia versioned artifact. Minimálny manifest obsahuje:

```yaml
agent_topology_id: checkout-incident-team/v3
release_manifest: agent-release-2026.08.04.2
orchestration_pattern: supervisor-with-specialists
agents:
  - id: incident-supervisor
    generation: 8
    model_route: reasoning-medium/v5
    owns:
      - operation_state
      - final_hypothesis_set
      - remediation_proposal
    tools:
      - query_metrics/read
      - call_specialist/execute
  - id: kubernetes-specialist
    generation: 4
    model_route: ops-fast/v3
    owns:
      - kubernetes_evidence
    tools:
      - kubernetes_read/read
  - id: database-specialist
    generation: 5
    model_route: ops-fast/v3
    owns:
      - database_evidence
    tools:
      - database_read/read
side_effect_owner: remediation-executor
synthesis_contract: incident-findings/v2
```

Bez topology generation nemožno porovnať dva runs ani zistiť, či sa zmenil supervisor prompt, specialist toolset alebo ownership.

## 5. Prečo začať single-agent návrhom

Single-agent návrh má menšiu coordination surface, jednoduchší trace, nižšiu latency a nižší token cost. Ak jeden agent s dobre navrhnutými tools a contextom spoľahlivo plní úlohu, pridanie agentov je zbytočný complexity tax. Baseline nie je iba lacnejší prototyp; poskytuje porovnávací outcome, voči ktorému sa musí preukázať hodnota samostatných context windows, delegation alebo privilege separation.

Single-agent je vhodný najmä v nasledujúcich situáciách:

- **Jeden koherentný context** — všetky rozhodujúce facts a constraints patria do jedného task subjectu, takže rozdelenie by vytvorilo compression a handoff loss bez reálnej izolácie.
- **Silné sekvenčné dependencies** — každý krok potrebuje authoritative outcome predchádzajúceho kroku, preto paralelní specialists nemajú nezávislú prácu a iba duplikujú assumptions.
- **Jeden outcome owner** — jedna rola musí formulovať finálnu odpoveď, udržiavať unresolved hypotheses a niesť zodpovednosť za business postcondition; ďalší agent by rozmazal ownership.
- **Jedna bezpečnostná contract boundary** — tools a credentials možno obmedziť jedným catalogom a policy contextom, takže ďalšie agent identities neprinášajú privilege separation.
- **Prísna latency alebo cost hranica** — route, nested inference, specialist queue a synthesis by prekročili SLO alebo ekonomický budget bez primeranej kvalitatívnej návratnosti.
- **Evals nepreukazujú benefit špecializácie** — multi-agent candidate nezlepšuje business accuracy, unsupported-action rate, recovery alebo segment outcomes oproti jednoduchšiemu baseline-u.

Toto nie je zákaz multi-agent architektúry. Je to requirement, aby zložitosť mala merateľný dôvod a jasný failure, ktorý rieši. Architecture review má pomenovať očakávaný benefit, experiment, cost a rollback path; ak multi-agent variant neprinesie lepší authoritative outcome, systém zostáva pri single-agent alebo deterministic workflow návrhu.

## 6. Kedy multi-agent prináša hodnotu

Multi-agent systém môže byť vhodný, keď úloha obsahuje nezávislé paralelné vetvy, viac odlišných knowledge alebo tool domén, context väčší než jeden agent dokáže efektívne kurátorovať alebo potrebu oddeliť privileges a ownership.

Anthropic pri produkčnom research systéme opisuje orchestrator-worker pattern, kde lead agent deleguje samostatné research vetvy paralelným subagentom. Benefit vzniká najmä pri breadth-first úlohách s nezávislými smermi a veľkým objemom informácií. Rovnaký pattern nie je automaticky vhodný pre remediation, kde dve paralelné mutácie môžu vytvoriť konflikt alebo duplicate side effect.

## 7. Context-window scaling

Jednou z hlavných výhod multi-agent architektúry sú samostatné context windows. Specialist môže spracovať veľký domain context a vrátiť iba typed summary alebo evidence set. Supervisor tak nemusí niesť všetky raw tool outputs.

Compression však môže stratiť dôležité detaily. Specialist output preto potrebuje provenance, confidence, unresolved hypotheses a source references. Veta „database je healthy“ bez query, time window a threshold nie je použiteľný evidence artifact.

## 8. Parallelizácia

Nezávislé tasks možno vykonať paralelne:

```text
Kubernetes evidence ┐
Database evidence   ├→ supervisor synthesis
Provider status     ┘
```

Parallelizácia znižuje wall-clock latency iba vtedy, keď tasks skutočne nemajú dependency. Ak database specialist potrebuje najprv deployment generation od Kubernetes specialistu, paralelné spustenie vytvorí stale assumptions alebo duplicated retrieval.

Každá paralelná vetva potrebuje join policy, timeout, partial-result semantics a cancellation behavior.

## 9. Cost model

Multi-agent architektúra spotrebuje viac model calls, context tokens, tool calls a trace storage. Anthropic pri research systéme uvádza, že multi-agent runs môžu byť výrazne drahšie než bežný chat, preto ich ekonomická hodnota závisí od úloh, kde vyššia kvalita alebo paralelizácia preváži cost.

Cost budget sa prideľuje topology-wide, nie každému agentovi bez spoločného limitu:

```yaml
run_budget:
  max_total_tokens: 180000
  max_specialist_runs: 5
  max_parallel_agents: 3
  max_wall_clock_seconds: 240
  max_cost_eur: 2.50
```

Supervisor nesmie spawnovať ďalších agentov iba preto, že každý specialist ešte neprekročil svoj lokálny budget.

## 10. Latency model

Multi-agent latency zahŕňa routing, specialist queue, specialist inference, tools, join, synthesis a prípadný retry. Paralelné vetvy znižujú sumu serial time, ale tail latency určuje najpomalší required specialist.

Diagnostika rozkladá latency:

```text
router 120 ms
supervisor plan 1.8 s
specialists fan-out 80 ms
kubernetes specialist 6.2 s
database specialist 11.4 s
provider specialist 3.7 s
join wait 11.5 s
synthesis 2.1 s
```

„Multi-agent je pomalý“ bez takéhoto decomposition nie je actionable diagnosis.

## 11. Centralizované ownership

Supervisor pattern ponecháva operation ownership jednému agentovi. Specialists poskytujú bounded outputs a nemajú automatickú authority meniť business state. Centralizácia zjednodušuje finálnu syntézu a guardrails, ale supervisor môže byť bottleneck alebo single point of behavioral failure.

Centralizovaný model je vhodný, keď jeden actor musí zjednotiť conflicting evidence, kontrolovať budgets a vlastniť user-facing communication.

## 12. Decentralizované ownership

Pri handoff pattern-e môže špecialista prevziať aktívnu konverzáciu alebo task. Decentralizácia znižuje potrebu, aby supervisor rozumel každej doméne, ale komplikuje ownership transitions, approval, memory a final responsibility.

Každý handoff musí definovať:

```text
čo sa odovzdáva
ktorý state zostáva spoločný
ktoré tools sa menia
kto teraz vlastní user interaction
ako sa riadenie vráti alebo ukončí
```

Bez explicitného ownership transferu môže pôvodný aj nový agent konať súčasne.

## 13. Agents as tools

Manager alebo supervisor môže volať specialistov ako tools. Specialist vykoná nested run a vráti result, zatiaľ čo manager zostáva ownerom hlavného threadu a finálnej odpovede. OpenAI Agents SDK tento pattern odlišuje od handoffu, kde nový agent prevezme aktívnu konverzáciu.

Agents-as-tools je vhodný pre bounded subtask, napríklad „analyzuj Kubernetes events a vráť findings podľa schema“. Specialist nemá dostať viac contextu ani privileges než subtask vyžaduje.

## 14. Handoffs

Handoff mení aktívneho agenta v tom istom top-level run-e. Je vhodný, keď specialist má priamo komunikovať s používateľom alebo vlastniť ďalšiu časť procesu. Handoff nie je iba tool call s iným menom; mení conversation ownership a instruction context.

Handoff input má byť typed a filtrovaný. Celá história sa neposiela automaticky, ak obsahuje irelevantné secrets alebo instructions z inej trust zóny.

## 15. Dynamic skills namiesto ďalších agentov

Niekedy sa multi-agent používa iba preto, aby sa oddelili prompts alebo knowledge. Jednoduchšou alternatívou je jeden agent, ktorý načítava schválené skills, tools alebo domain context podľa potreby. Tým sa zachová jeden operation owner a zníži koordinácia.

Rozhodnutie medzi specialist agentom a skillom závisí od toho, či treba samostatný loop, context isolation, parallelism alebo privilege boundary. Ak nie, skill je často lacnejší a pozorovateľnejší.

## 16. State ownership

Každý state field musí mať jedného writer ownera alebo deterministic merge rule. Shared mutable dictionary, do ktorého všetci agenti zapisujú ľubovoľný text, vytvára race conditions a authority confusion.

Príklad:

```yaml
state_ownership:
  incident_summary:
    writer: incident-supervisor
  kubernetes_findings:
    writer: kubernetes-specialist
    merge: replace_by_generation
  database_findings:
    writer: database-specialist
    merge: replace_by_generation
  remediation_action:
    writer: remediation-planner
    approval_required: true
```

Specialist nemá prepísať field vlastnený supervisorom iba preto, že jeho model output pôsobí presvedčivo.

## 17. Memory ownership

Supervisor môže vlastniť thread-scoped memory, zatiaľ čo specialists dostávajú izolovaný subtask context. Long-term memory writes sa centralizujú alebo prechádzajú review pipeline. Tým sa zabráni, aby jeden specialist uložil unreviewed assumption ako globálne pravidlo.

Ak specialists potrebujú vlastnú domain memory, namespaces a retention musia byť oddelené a supervisor dostáva iba typed retrieval result s provenance.

## 18. Tool a credential isolation

Každý agent má najmenší tool a credential scope potrebný pre jeho rolu. Research specialist nepotrebuje production mutation token; database diagnostický agent nepotrebuje Kubernetes delete permission.

Multi-agent architektúra nesmie používať jeden shared superuser credential pre pohodlné delegovanie. Inak izolácia promptov neposkytuje reálnu security boundary.

## 19. Side-effect ownership

Najbezpečnejší default je single-writer model. Specialists navrhujú alebo verifikujú, ale iba jeden bounded executor môže vykonať mutation po approval a idempotency kontrole.

```text
specialist evidence
→ supervisor synthesis
→ one remediation proposal
→ approval
→ one side-effect executor
→ authoritative read-back
```

Ak viacerí agenti môžu konať, resource locking, operation identity a conflict policy musia byť explicitné.

## 20. Delegation contract

Delegácia potrebuje contract, nie iba prirodzenú vetu. Contract definuje objective, inputs, allowed tools, output schema, budget, deadline, authority a forbidden actions.

```yaml
specialist_task_id: task-db-017
specialist: database-specialist/v5
objective: Determine whether database saturation contributes to checkout errors.
inputs:
  incident_id: INC-2044
  time_window: 2026-08-04T14:00:00Z/2026-08-04T14:20:00Z
allowed_tools:
  - query_database_metrics/read
forbidden:
  - execute_sql_mutation
  - restart_database
output_schema: database-findings/v2
budget:
  max_turns: 8
  max_seconds: 60
```

Supervisor validuje specialist output pred syntézou rovnako ako bežný tool response.

## 21. Specialist output contract

Výstup nemá byť iba prose summary. Potrebuje findings, evidence, confidence, unresolved questions, scope a timestamps.

```json
{
  "task_id": "task-db-017",
  "status": "completed",
  "findings": [
    {
      "claim": "Primary database CPU was below the saturation threshold.",
      "confidence": "high",
      "evidence_ref": "metrics://db-primary/cpu?window=...",
      "observed_at": "2026-08-04T14:19:30Z"
    }
  ],
  "unresolved": ["Replica apply lag was not available."],
  "mutation_performed": false
}
```

Synthesis môže potom rozlišovať potvrdené findings od neúplných oblastí.

## 22. Synthesis

Synthesis spája výsledky, ale nesmie zahladiť konflikty. Supervisor musí zachovať competing hypotheses, source refs a specialist scope. Dve nezávislé „healthy“ odpovede nevytvárajú dôkaz o tretej vrstve.

Synthesis output môže mať:

```text
confirmed facts
conflicting findings
missing evidence
current leading hypotheses
proposed next observation
proposed action with risk
```

Finálna fluent veta bez tejto štruktúry môže skryť gap v diagnostike.

## 23. Router a supervisor sú rozdielne role

Router klasifikuje input a vyberá destination alebo fan-out. Supervisor udržiava context a rozhoduje naprieč viacerými turns, ktoré specialists zavolať a ako ich výsledky spojiť. Jeden komponent môže implementovať obe role, ale telemetry a contracts majú zostať oddelené.

Pri jasných kategóriách je deterministic alebo bounded router často vhodnejší než plný supervisor agent. Pri otvorenom multi-hop probléme môže supervisor reagovať na nové findings.

## 24. Topology cycles

Multi-agent graph môže vytvoriť loop: supervisor zavolá specialistu, ten handoffne späť, supervisor znovu deleguje rovnakú úlohu. Cycle detection sleduje delegation edges, task digests a progress.

```python
def allow_delegation(parent: str, child: str, task_digest: str, graph: TraceGraph) -> bool:
    if graph.same_task_edge_count(parent, child, task_digest) >= 2:
        return False
    if graph.depth >= 4:
        return False
    return graph.has_new_evidence_since_last_edge(task_digest)
```

Nový wording bez nového evidence nie je progress.

## 25. Failure isolation

Specialist failure nemusí zlyhať celý run. Join policy určí, či je specialist required, optional alebo nahraditeľný fallbackom. Partial success sa nesmie prezentovať ako úplná analýza.

Príklad:

```yaml
join_policy:
  required:
    - kubernetes-specialist
    - business-metrics-specialist
  optional:
    - provider-status-specialist
  on_timeout:
    required: escalate
    optional: continue_with_gap
```

Supervisor musí explicitne uviesť chýbajúcu vetvu.

## 26. Retry a duplicate specialist runs

Retry specialistu vytvára nový technical attempt, nie nový business subtask. Task ID zostáva stabilné a outputs sa deduplikujú podľa task generation. Mutation-capable specialist sa nereštartuje bez reconciliation predchádzajúceho outcome-u.

Pri read-only research môže retry zopakovať query, ale cost a duplicate evidence sa stále účtujú a deduplikujú.

## 27. Model heterogenita

Rôzni agents môžu používať rôzne model routes podľa úlohy. Lacný classifier môže routovať, silnejší model plánovať a menší specialist extrahovať štruktúrované dáta. Každý route je súčasťou composed release manifestu.

Heterogenita zvyšuje compatibility surface. Tool schema, context size, structured output a safety behavior sa musia testovať pre každý agent-model pair.

## 28. Evaluation

Single-agent a multi-agent návrh sa porovnávajú na rovnakom business eval sete. Nestačí ukázať, že multi-agent vytvára dlhšiu alebo sofistikovanejšiu odpoveď.

Metriky zahŕňajú:

```text
business outcome accuracy
unsupported action rate
duplicate side-effect rate
trajectory success
specialist routing precision and recall
latency p50/p95
total tokens and tool calls
human-review burden
recovery success
```

Architektúra sa mení iba pri merateľnom trade-offe.

## 29. Incident `AGENT-OPS-02`

Supervisor vytvoril dve tasks s odlišnými IDs, ale rovnakým remediation objective. Kubernetes specialist navrhol rollout restart a database specialist cez všeobecný operations tool navrhol restart dependent workerov. Obaja mali mutation permission a supervisor spustil návrhy paralelne pred syntézou.

Správna architektúra mala byť:

```text
one incident operation owner
→ read-only specialist fan-out
→ typed findings and conflicts
→ supervisor synthesis
→ one remediation proposal
→ one approval-bound executor
→ business conversion read-back
```

Po incidente sa mutation tools odstránili zo specialist roles a topology manifest dostal explicitný `side_effect_owner`.

## 30. Failure hypotheses

Pri zlyhaní multi-agent systému netreba automaticky obviniť „coordination“. Najprv sa načíta composed topology manifest a effective registry state, potom sa rekonštruuje causal task graph od jedného business operation ID cez routing, subtask IDs, technical attempts, context packages, specialist outputs, state merges a synthesis. Tým sa odlíši nesprávna architektúra od správnej topológie s jedným chybným route rozhodnutím alebo nekompatibilnou specialist generation.

Dôležité je rozlišovať počet agentov od nezávislosti dôkazov. Dva specialist outputs môžu pochádzať z rovnakého shared memory recordu, rovnakého metric query alebo leading hypothesis, takže ich zhoda nie je konsenzus. Rovnako dva technical task IDs môžu predstavovať duplicate attempts jedného business subtasku. Falsifikácia preto používa contract a context digests, source lineage, writer ownership a downstream side-effect records, nie iba finálne prose summaries.

- **Wrong routing** — input bol poslaný nesprávnemu alebo nedostatočnému specialistovi; route features a taxonomy generation ukážu, či chyba vznikla pred specialist runom.
- **Missing specialist** — required domain vetva sa vôbec nespustila; topology plan a join policy určia, či išlo o omission, timeout alebo nesprávne označenie optionality.
- **Duplicate delegation** — rovnaký business subtask dostal viac technical task IDs; objective a contract digests odhalia duplikát aj pri rozdielnom wording-u.
- **Context contamination** — specialist dostal instructions alebo dáta z iného domainu alebo tenanta; context package digest a storage access log určia prvý leak.
- **State race** — paralelní writers prepísali shared field bez merge rule; checkpoint generations a writer ownership odhalia stratený update.
- **Privilege overlap** — viac agentov mohlo vykonať rovnaký side effect; loaded tool catalogs, credentials a action ledger určia skutočný mutation surface.
- **Synthesis loss** — supervisor odstránil conflict, uncertainty alebo source refs; porovnanie typed specialist outputs so synthesis artifactom ukáže stratený evidence.
- **Cycle** — delegation graph opakoval rovnakú prácu bez nového evidence; repeated task digest a absence nových observations potvrdia stagnáciu.
- **Budget fragmentation** — každý agent bol pod lokálnym limitom, ale topology prekročila global cost alebo latency budget; parent budget ledger musí zahrnúť všetky nested attempts.
- **Version skew** — supervisor a specialist používali nekompatibilné contract generations; loaded-state read-back a schema validation určia prvú nekompatibilnú edge.

Root cause verdict pomenúva exact run, task, agent a topology generation aj prvý chybný transition. Recovery sa prijme až po replayi incidentného task graphu, benign single-agent control-e, overení jedného side-effect ownera a druhej operácii bez preneseného state-u alebo duplicate delegation.

## 31. Observability

Trace musí zachytiť parent-child vzťahy medzi runmi, delegation contract digest, agent generation, model route, context digest, tool calls, specialist output schema a synthesis decision. Bez causal graphu vyzerá multi-agent run ako nezávislé model calls.

```text
business operation span
└─ supervisor run
   ├─ router decision
   ├─ specialist task A
   │  └─ tool observations
   ├─ specialist task B
   │  └─ tool observations
   ├─ synthesis
   └─ action proposal
```

Raw sensitive contexts sa neukladajú defaultne; používajú sa hashes, refs a policy-controlled captures.

## 32. Containment

Pri coordination incidente sa môže vypnúť parallel fan-out, handoffs alebo mutation tools pre konkrétnu topology generation. Systém sa degraduje na single-agent read-only mode alebo deterministic routing. Tým sa zníži blast radius bez úplného vypnutia služby.

Containment zachová traces a task graph. Automatické zrušenie všetkých specialist runs môže zničiť evidence o unknown side effects.

## 33. Recovery

Recovery môže vrátiť known-good topology manifest, opraviť routing descriptions, zmeniť state ownership, obmedziť privileges, invalidovať stale contexts alebo re-run synthesis z už získaných evidence. Nie vždy je potrebné zopakovať drahé specialist searches.

Ak sa vykonali duplicate actions, recovery zahŕňa business reconciliation a compensating action. Technický rollback agent topology sám neopraví dvojitý refund alebo dva restarty.

## 34. Positive acceptance

Pozitívny test musí preukázať správny routing, izolované specialist contexts, typed outputs, deterministic join a jedného side-effect ownera. Finálny business outcome sa overí authoritative read-backom.

## 35. Forbidden acceptance

Zakázaný test skúsi delegovať mutation read-only specialistovi, prekročiť tenant boundary, vytvoriť recursive delegation alebo zapísať shared state bez ownership. Systém musí akciu blokovať a auditovať bez toho, aby ju supervisor mohol obísť zmenou promptu.

## 36. Recovery acceptance

Recovery test preruší jedného required specialistu, simuluje version mismatch a vytvorí duplicate task. Orchestrator musí rozlíšiť partial result, zabrániť duplicate side effectu a pokračovať alebo eskalovať podľa join policy.

## 37. Second-operation acceptance

Druhý incident sa spustí po prvom s odlišným tenantom a service scope. Specialist sessions, task outputs, budgets a approvals sa nesmú preniesť. Topology však musí konzistentne uplatniť rovnaké ownership a routing pravidlá.

## 38. Alternate-scenario acceptance

Alternate scenario obsahuje úlohu, ktorá nebenefituje z multi-agent paralelizácie. Architecture selector alebo deterministic policy má zvoliť jednoduchší single-agent alebo workflow path. Systém, ktorý vždy spawnuje celý tím, nepreukazuje primerané riadenie complexity.

## 39. Rozhodovací rámec

Pred zavedením multi-agent architektúry tím porovná task decomposition, context isolation, parallelism, privilege boundaries, ownership, cost, latency a eval evidence. Rozhodnutie má byť versioned architecture record, nie iba preferencia frameworku.

Praktická otázka znie:

```text
Ktorý konkrétny failure alebo capacity limit single-agent návrhu rieši ďalší agent,
a ako preukážeme, že nový coordination surface neprináša väčšie riziko?
```

Bez odpovede je vhodnejší jednoduchší návrh.

## 40. Primárne zdroje a proof boundary

OpenAI Agents SDK rozlišuje manager pattern s agents-as-tools od handoffov, pri ktorých specialist prevezme aktívnu konverzáciu. LangChain dokumentácia odlišuje subagent supervisor pattern od routera a uvádza, že nie každá komplexná úloha vyžaduje multi-agent systém. Anthropic opisuje orchestrator-worker multi-agent research architektúru, jej výhody pri paralelných breadth-first tasks aj významný token a coordination cost.

Tieto zdroje poskytujú implementačné a architektonické príklady. Nepreukazujú, že konkrétna topológia je vhodná pre checkout remediation alebo že multi-agent systém dosiahol produkčný business outcome. Repository validácia kapitoly nevykonáva reálne specialist runs, parallel failure, approval, side effect, recovery ani cost measurement.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Short-term state, long-term memory a external memory](short-term-state-long-term-external-memory.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Supervisor, router a specialist patterns →](supervisor-router-specialist-patterns.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
