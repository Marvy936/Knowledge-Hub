# Cost, latency a token budgets

Agentický systém nespotrebúva iba jeden model request. Jeden business operation môže vytvoriť viac model turns, tool calls, retrieval reads, handoffs, retries, approvals, background tasks a následné reconciliation reads. Cost a latency preto nemožno riadiť iba cez `max_output_tokens` jedného requestu alebo cez mesačný cloud budget.

Táto kapitola otvára incident `AGENT-GOV-06`. Checkout remediation agent dostal jednoduchú diagnostickú úlohu, ale retrieval v každom turne znovu pripojil celý incident timeline, supervisor opakovane delegoval rovnaký subtask a provider timeout bol interpretovaný ako bezpečný dôvod na nový model call. Run síce skončil správnou odpoveďou, ale prekročil tenantový cost budget, zákaznícky latency SLO a vytvoril tri duplicate read-only investigations. Následný fallback na lacnejší model znížil tokenovú cenu, no predĺžil trajektóriu a zvýšil počet tool calls, takže celkový cost aj tail latency vzrástli.

Nosný lifecycle je:

```text
business operation a service tier
→ exact composed release a price catalog generation
→ end-to-end deadline a cost envelope
→ per-run, per-turn, per-tool a per-tenant sub-budgets
→ preflight estimation a admission decision
→ measured model, retrieval, tool, queue a approval consumption
→ in-flight budget updates a escalation policy
→ graceful degradation, stop alebo human handoff
→ authoritative usage a billing reconciliation
→ technical, business a second-operation acceptance
```

## 1. Budget nie je iba limit

Limit hovorí, za akou hranicou sa operácia zastaví. Budget je riadiaci kontrakt, ktorý zároveň určuje ownera, meranú jednotku, časové okno, enforcement bod, povolené prekročenie, degraded mode a dôkaz, podľa ktorého sa spotreba uzavrie.

Bez týchto vlastností môže rovnaké číslo znamenať request cap, dennú kvótu, forecast alebo iba dashboard alert. Agent potom nevie, či má zmeniť plán, prepnúť model, vynechať voliteľný krok, čakať na refill alebo bezpečne skončiť.

## 2. Exact budget subject

Budget sa viaže na business operation a service tier, nie iba na API key alebo proces. Rovnaký tenant môže mať interaktívne support runy s nízkou latency a offline reconciliation runy s väčším tokenovým priestorom.

Subject musí obsahovať minimálne tenant, operation, workflow, release, environment, service tier a price catalog generation. Bez price generation nemožno spätne vysvetliť, prečo rovnaký token count vytvoril odlišný finančný výsledok.

```yaml
budget_subject:
  tenant_id: tenant_acme
  operation_id: op_checkout_913
  workflow: checkout-remediation
  service_tier: interactive-premium
  agent_release: support-agent/5.9.0
  model_route: route/support-prod@sha256:77a1
  price_catalog: pricing/2026-08-04T00:00Z
  currency: EUR
```

## 3. Hierarchia budgetov

Jedna globálna kvóta nevie chrániť jednotlivý request ani tenant. Bez hierarchie môže jeden loop spotrebovať denný pool, pričom ostatné runy sa zastavia až po oneskorenej billing metrike.

Praktická hierarchia používa organization alebo product envelope, tenant quota, workflow budget, operation budget, turn budget a tool-specific budget. Nižšia úroveň nesmie zvýšiť nadradený limit; môže iba rezervovať alebo spotrebovať jeho časť.

## 4. Hard, soft a forecast hranice

Hard budget zastaví alebo zablokuje ďalšiu spotrebu. Soft budget vyvolá zmenu stratégie, napríklad lacnejší model, kratší context, menej alternatív alebo human handoff, ale nepovoľuje neobmedzené pokračovanie.

Forecast hranica odhaduje, že aktuálny plán pravdepodobne prekročí budget ešte pred vykonaním ďalšieho kroku. Je užitočná najmä pri drahom tool calle alebo ďalšom handoffe, no zostáva odhadom a musí sa po run-e porovnať s authoritative usage.

## 5. Cost dimensions

Modelový token cost je iba jedna zložka. Celkový cost môže zahŕňať retrieval, embeddings, vector queries, sandbox compute, browser alebo code execution, externé API, storage, egress, queue time, human review a následné reconciliation operácie.

Cost model preto používa samostatné dimensions a potom ich mapuje na spoločnú menu alebo interné units. Tým sa zabráni situácii, v ktorej agent „optimalizuje tokeny“, ale presunie náklady do opakovaných drahých toolov.

## 6. Token accounting

Token accounting rozlišuje input, output, cached input a reasoning tokens tam, kde ich provider reportuje. OpenAI Agents SDK napríklad zhromažďuje request count, input, output, total, cached a reasoning usage na úrovni runu a jednotlivých requestov, ale aplikácia stále určuje budget policy a enforcement.

Reported token count je authoritative pre provider request, nie automaticky pre internú fakturáciu. Billing pipeline môže používať iný price catalog, rounding, batch discount alebo enterprise contract, preto sa usage a money ledger uzatvárajú oddelene.

## 7. Context amplification

Agent môže posielať rovnaké history, tool schemas, policies a retrieved documents v každom turne. Malé predĺženie trajektórie tak znásobí input tokeny, pretože každý nový request opakuje veľkú časť contextu.

Context budget musí rozlišovať invariantný prefix, session history, current working set, retrieved evidence, tool catalog a output reserve. Optimalizácia potom cieli na konkrétnu vrstvu namiesto slepého truncation, ktorý by mohol odstrániť approval alebo tenant identity.

## 8. Prompt caching a jeho hranice

Prompt caching môže znížiť účtovanú alebo výpočtovú cenu opakovaného stabilného prefixu. Cache hit však nie je dôkaz, že content je aktuálny, autorizovaný alebo tenant-safe.

Cache key musí zahŕňať všetky semanticky významné generations a tenant boundary. Ak sa policy bundle, tool catalog alebo data classification zmení, starý cached prefix sa nesmie považovať za current authority iba preto, že ho provider dokáže znovu použiť.

## 9. Output budget

Výstupný token cap chráni pred nekontrolovanou dĺžkou odpovede, ale môže odrezať structured output, citation block alebo recovery evidence. Agent musí vedieť rozlíšiť „stručná úspešná odpoveď“ od „truncated neplatný kontrakt“.

Pre structured output sa budget kombinuje so schema validation a explicitným termination statusom. Pri nedostatku priestoru agent radšej vráti typed `budget_exhausted` alebo minimal safe result než syntakticky poškodený objekt interpretovaný ako úspech.

## 10. Latency nie je jedno číslo

End-to-end latency obsahuje admission, queue, retrieval, model time-to-first-token, model completion, tool execution, network, handoff, approval wait, retry backoff a authoritative read-back. Priemer maskuje pomalé tail operations, ktoré sú často najdôležitejšie pre interaktívny business journey.

Pre každý krok sa zaznamenáva start, first-byte alebo first-token, completion a wait reason. Bez wait reason sa dlhá approval prestávka môže nesprávne pripísať modelu alebo providerovi.

## 11. Deadline, timeout a latency SLO

Deadline je najneskorší čas dokončenia celej operation. Timeout je lokálna hranica jedného requestu alebo activity a SLO je cieľ správania populácie operationov, napríklad percentil za časové okno.

Lokálne timeouty sa odvodzujú z remaining end-to-end deadline. Ak každý z piatich krokov dostane nezávislých 30 sekúnd, workflow s 60-sekundovým deadline nemá reálnu šancu splniť kontrakt.

## 12. Critical path a parallel work

Paralelné specialist tasks znižujú wall-clock čas iba vtedy, keď sú skutočne nezávislé a ich výsledky sú potrebné. Zároveň zvyšujú request count, peak concurrency, rate-limit pressure a riziko redundantného tool accessu.

Planner má označiť required, optional a speculative branches. Optional branch sa nespustí, ak remaining budget nestačí na jej dokončenie a vyhodnotenie; speculative branch musí mať samostatný cap a cancellation path.

## 13. Queueing a concurrency

Concurrency limit chráni downstream systém, no môže presunúť latency do queue. Queue time je preto súčasťou operation budgetu a admission controller nesmie prijímať viac práce, než dokáže dokončiť pred deadline.

Fair scheduling rozlišuje tenant, service tier a operation class. Bez tenant-aware fairness môže jeden zákazník zaplniť všetky model alebo tool slots a vytvoriť noisy-neighbor incident aj bez prekročenia vlastnej tokenovej kvóty.

## 14. Rate limits

Provider rate limits môžu byť requestové, tokenové alebo paralelné a ich stav sa môže meniť. Klient ich interpretuje ako capacity signal, nie ako dôvod na nekonečný retry.

Retry policy používa server hints, exponential backoff, jitter a remaining deadline. Ak refill nastane až po deadline, operation prejde do degraded alebo queued stavu namiesto toho, aby blokovala worker a držala reservations.

## 15. Preflight estimation

Pred spustením agent odhadne minimálny, očakávaný a worst-reasonable cost a latency. Odhad zahŕňa počet turnov, context veľkosť, expected tool path, retry allowance a povinný read-back.

Preflight nie je billing proof. Je admission evidence, ktoré sa po dokončení kalibruje proti skutočnej spotrebe, aby sa forecast model nezhoršoval bez povšimnutia.

## 16. Reservation model

Pri prijatí operation sa môže rezervovať časť tenantového a workflow budgetu. Reservation zabráni tomu, aby stovky súbežných runov všetky prešli preflightom proti rovnakému ešte nespotrebovanému zostatku.

Reservation sa pri každom kroku mení na actual consumption alebo sa uvoľní. Crash recovery musí vedieť nájsť orphan reservations podľa durable run identity a lease, inak sa quota javí vyčerpaná aj bez aktívnej práce.

## 17. In-flight accounting

Usage sa aktualizuje po každom model requeste, tool calle a významnom external charge. Agent tak nerozhoduje na základe stale hodnoty z úvodu runu.

Accounting event nesie operation, tenant, component, generation, units, authoritative source a observed timestamp. Duplicated telemetry sa deduplikuje cez stable consumption event ID, nie cez porovnanie približných súm.

## 18. Budget-aware planning

Planner dostáva remaining budget ako explicitný state, ale nesmie ho meniť. Pri každom replanningu musí vysvetliť, ktoré povinné kroky ostávajú a ktoré voliteľné kroky vypúšťa.

Budget-aware plan preferuje najlacnejší dôkaz, ktorý dokáže rozlíšiť konkurenčné hypotézy. To neznamená najlacnejší model za každú cenu; slabší model môže vytvoriť viac turnov, nesprávne tool calls a vyšší celkový cost.

## 19. Model routing

Model route sa vyberá podľa capability, risku, latency a cost envelope. Route je versionovaný policy artifact, nie nezdokumentovaný `if` v aplikácii.

Fallback model musí prejsť rovnaké schema, tool, safety a outcome evaly pre konkrétny workflow. Nižšia cena alebo nižší median latency nepreukazuje semantickú kompatibilitu.

## 20. Tool budgets

Tool budget môže obmedziť počet calls, cumulative execution time, monetary charge, transferred bytes alebo mutations. Read-only tool s veľkým exportom môže byť finančne aj bezpečnostne nákladnejší než malý mutation endpoint.

Tool wrapper rezervuje budget pred dispatchom a po výsledku zapíše authoritative consumption. Timeout s unknown outcome nevracia celú reservation automaticky, kým reconciliation nepotvrdí, či downstream charge alebo side effect vznikol.

## 21. Retrieval budgets

Retrieval budget určuje počet queries, candidate count, reranking depth, fetched bytes a maximálny context contribution. Viac dokumentov nezaručuje lepšiu grounded odpoveď a môže zvýšiť latency, tokeny aj prompt-injection surface.

Query reformulation sa obmedzuje podľa marginal gain. Ak ďalší retrieval nepriniesol nový authoritative evidence class, planner musí zvážiť stop alebo human escalation namiesto opakovania podobných searches.

## 22. Human-review budget

Human approval má latency, availability a finančný cost. Agent nesmie obchádzať review iba preto, že remaining automatic budget je nízky.

Policy vopred určí, ktoré action classes vyžadujú človeka bez ohľadu na cost. Pri nedostupnom reviewerovi sa operation bezpečne pozastaví, downgradne na read-only alebo skončí, ale neprejde do širšej autonómie.

## 23. Retry budget

Retry budget je podmnožina operation budgetu. Rozlišuje model request, idempotent tool read, unknown-outcome mutation a durable workflow retry, pretože každá kategória má iný risk aj cost.

Retry sa povoľuje iba pri klasifikovanom failure mode a dostatočnom remaining deadline. Rovnaká chyba cez rovnakú dependency generation nesmie spotrebovať celý budget bez novej diskriminačnej zmeny.

## 24. Budget exhaustion state machine

Budget exhaustion nie je generická exception. Stavový model rozlišuje warning, soft breach, hard breach, pending reconciliation a closed.

Pri warningu sa zmení plán. Pri hard breach sa zastaví nová spotreba, ale povinné cancellation, ledger write a bezpečný read-back môžu mať rezervovaný emergency budget, aby systém nezanechal unknown side effect bez evidencie.

## 25. Graceful degradation

Degraded mode zachováva bezpečnosť a najdôležitejší business invariant, hoci poskytne menej funkcií. Môže vrátiť verified read-only diagnosis, odložiť non-urgent analysis alebo presunúť case do human queue.

Degradation nesmie potichu zmeniť význam výsledku. Response a audit event označia, ktoré capability boli vynechané, prečo a aký follow-up je potrebný.

## 26. Cost versus quality

Nižší cost je úspech iba pri zachovaní required outcome, safety a reliability. Optimalizácia, ktorá skráti context a zhorší tenant attribution alebo citation grounding, je regresia aj pri výraznej finančnej úspore.

Release gate preto používa Pareto pohľad na quality, security, cost a latency. Jedna agregovaná „efficiency score“ nesmie skryť forbidden event alebo kritický segmentový prepad.

## 27. Cost versus latency

Batching a queueing môžu znížiť jednotkový cost, ale zvýšiť waiting time. Paralelizácia môže znížiť wall-clock latency, no zvýšiť total compute a provider pressure.

Rozhodnutie sa robí podľa service tieru a business value of time. Offline backfill a interaktívny incident responder nemajú rovnaký optimálny bod.

## 28. Caching versus correctness

Response, semantic alebo tool-result cache môže odstrániť opakované výpočty. Cache však musí byť viazaná na subject, tenant, authorization, dependency generations, freshness a data classification.

Stale alebo cross-tenant cache hit je correctness a security incident, nie efektívna optimalizácia. Cache acceptance preto zahŕňa negative tests pre changed policy, revoked access a druhého tenanta.

## 29. Budget observability

Dashboard potrebuje planned, reserved, consumed, reconciled a billed values. Ak zobrazuje iba provider tokeny, nevysvetlí rozdiel medzi agentovým rozhodnutím a konečnou invoice.

Metriky sa segmentujú podľa workflow, tenant tieru, release, route, tool a outcome. Cost per successful accepted operation je užitočnejší než cost per request, pretože zahŕňa retry a failure waste.

## 30. Price catalog lifecycle

Price catalog je versionovaný vstup. Obsahuje provider rates, interné multipliers, currency conversion a effective interval, ale neukladá sa ako hardcoded nadčasová pravda do kapitoly alebo model promptu.

Historical reconciliation používa catalog účinný v čase requestu. Repricing nesmie spätne meniť uzavreté operation ledgers bez explicitnej correction event identity.

## 31. Forecast calibration

Forecast sa hodnotí podľa biasu a error distribúcie na segmentoch. Model, ktorý priemerne sedí, ale systematicky podhodnocuje dlhé multi-agent runy, nie je vhodný pre admission control.

Calibration job používa iba uzavreté a reconciled operations. Pending usage alebo oneskorené vendor charges sa nesmú považovať za nulový cost.

## 32. Abuse a denial of wallet

Útočník môže zámerne vytvoriť inputs, ktoré maximalizujú context, loops, tool fan-out alebo expensive routes. Denial of wallet sa rieši tenant/user quotas, anomaly detection, bounded turns, capability restrictions a paid-operation admission.

Bezpečnostný control nesmie čakať na mesačnú invoice. In-flight spend velocity a unusual trajectory shape musia vedieť zastaviť konkrétny subject alebo tenant skôr, než sa vyčerpá globálny budget.

## 33. Incident `AGENT-GOV-06`

Incident začal po release, ktorý zvýšil retrieval candidate count a povolil supervisorovi paralelné specialist calls. Každý specialist dostal celý incident timeline a tool catalog, provider timeout vrátil nejednoznačný status a orchestrator bez stable subtask identity vytvoril náhradný call.

Soft token budget prepol route na lacnejší model, ale route nemala trajectory compatibility gate. Slabší model vykonal viac replanning turns a opakoval retrieval, takže total tokens, tool count a p99 latency vzrástli. Tenantová denná kvóta sa kontrolovala iba po uzavretí runu, preto tri súbežné operations všetky prešli admission.

## 34. Konkurenčné hypotézy

Prvá hypotéza tvrdí, že zdražel provider model. Druhá tvrdí, že narástol context amplification. Tretia hľadá duplicate work po timeoutoch a štvrtá predpokladá queue saturation alebo fallback trajectory regresiu.

Diskriminačné evidence sú price catalog generation, per-request usage, context layer sizes, stable subtask IDs, retry reasons, model route transitions, queue spans a tool-call graph. Samotná vysoká invoice nerozlíši príčinu.

## 35. Containment

Containment vypne nový route bundle pre dotknutý workflow, zníži speculative fan-out a nastaví tenant-aware admission. In-flight operations dostanú policy event, ktorý zakáže nové optional branches, ale ponechá emergency read-back budget.

Nie je bezpečné globálne zrušiť všetky worker procesy, ak existujú unknown-outcome tools. Najprv sa zastaví nová spotreba a potom sa reconciliujú dispatchnuté activities.

## 36. Recovery

Recovery obnoví stable subtask identity, per-tenant reservations, context-layer caps a route compatibility eval. Historical operations sa prepočítajú proti správnemu price catalogu a orphan reservations sa uvoľnia až po durable-state kontrole.

Canary používa rovnaké tenant a workload slices ako incident. Sleduje cost per accepted outcome, p50/p95/p99 latency, tool count, retry rate a forbidden budget breaches.

## 37. Positive acceptance

Pozitívny test dokončí reprezentatívnu operation v service-tier deadline, pod hard cost budgetom a s povinným technical aj business read-backom. Usage ledger sa zhoduje s provider usage v definovanej tolerancii a billing reconciliation je uzavretá.

Trace ukáže planned, reserved a actual consumption pre každý významný krok. Degraded mode sa nepoužije, ak budget ostáva dostatočný.

## 38. Forbidden acceptance

Release neprejde, ak správna finálna odpoveď maskuje prekročený tenant budget, chýbajúci read-back alebo duplicate work. Neprípustné je aj automaticky zvýšiť budget po loop-e bez novej autorizácie.

Rovnako neprípustný je fallback, ktorý zníži unit token price, ale zvýši celkový cost alebo bezpečnostné riziko. Aggregate priemer nesmie prebiť hard per-operation invariant.

## 39. Recovery acceptance

Recovery test zámerne vyvolá rate limit, model timeout, tool timeout a stale cache. Operation musí použiť klasifikovaný retry budget, zachovať deadline ownership a skončiť buď accepted outcome-om, alebo explicitným degraded/failed stavom bez orphan reservations.

Unknown-outcome charge sa uzavrie authoritative lookupom. Emergency budget sa použije iba na cancellation, ledger a reconciliation, nie na nový agentický plán.

## 40. Second-operation acceptance

Druhá operation od iného tenanta začne s fresh reservations, contextom a route decisionom. Nesmie zdediť budget warning, cached authorization ani remaining quota z prvého runu.

Test zároveň overí fair scheduling počas súbežného heavy runu. Premium latency tier môže dostať prioritu, ale nesmie obísť tenantový hard spend limit.

## 41. Praktický budget manifest

Manifest je authoritative vstup admission a in-flight policy, preto musí byť versionovaný a čitateľný aj bez modelu. Hodnoty nižšej úrovne rozdeľujú nadradený envelope; nepovoľujú agentovi zvýšiť celkový cost alebo deadline.

Príklad nepreukazuje, že provider usage, billing alebo cancellation skutočne fungujú. Loaded manifest digest, enforcement events a reconciled ledger sú samostatné acceptance evidence.

```yaml
agent_budget:
  version: budget-policy/v4
  service_tier: interactive-premium
  deadline_ms: 45000
  money:
    currency: EUR
    hard: 0.45
    soft: 0.30
    emergency_reconciliation: 0.03
  tokens:
    input: 70000
    output: 6000
    reasoning: 12000
  execution:
    model_requests: 8
    tool_calls: 10
    mutations: 1
    specialist_fanout: 2
  degradation:
    at_soft_budget: deterministic-read-only
    at_hard_budget: stop-new-work-and-reconcile
```

## 42. Praktický enforcement pseudocode

Enforcement potrebuje durable ledger a atomic reservation, nie iba mutable counter v process memory. Pred každým krokom porovná estimated charge, remaining deadline a mandatory recovery reserve; po kroku zapíše actual usage s deduplication identity.

Pseudocode ukazuje rozhodovací tok, ale nie distributed atomicity ani presnosť provider reportingu. Produkčný systém musí zvládnuť concurrent runs, crash po dispatchi a oneskorenú billing udalosť.

```python
async def dispatch_budgeted_step(run, step):
    estimate = estimator.for_step(run.loaded_release, step)
    reservation = await budget_ledger.reserve(
        tenant_id=run.tenant_id,
        operation_id=run.operation_id,
        step_id=step.stable_id,
        estimated_cost=estimate.cost,
        estimated_tokens=estimate.tokens,
        deadline=run.deadline,
        preserve_reconciliation_reserve=True,
    )

    if not reservation.allowed:
        return await degrade_or_stop(run, reservation.reason)

    try:
        result = await execute(step, timeout=reservation.step_timeout)
        usage = authoritative_usage(result)
        await budget_ledger.commit(reservation.id, usage)
        return result
    except UnknownOutcome as error:
        await budget_ledger.mark_pending_reconciliation(reservation.id, error.ref)
        return await reconcile_before_retry(run, step, error.ref)
```

## 43. Prevádzkové metriky

Kľúčové metriky sú cost per accepted operation, tokeny podľa vrstvy contextu, reservation utilization, forecast error, budget breach rate, duplicate-work rate, p50/p95/p99 end-to-end latency a remaining-budget-at-termination. Metriky sa rozdeľujú podľa tenant tieru, route, release a outcome class.

Samostatne sa sleduje waste: nevyužité speculative branches, cancelled tool work, retry bez novej evidence a output, ktorý neprešiel validation. Waste trend často odhalí regresiu skôr než mesačný spend.

## 44. Alerting

Alert má uviesť exact subject, budget generation, breach type, spend velocity, affected tenanty a current containment. Globálny cost spike bez segmentácie vedie k plošnému vypnutiu, ktoré môže poškodiť zdravé workflowy.

Alert pre soft breach je odlišný od hard breach alebo reconciliation backlogu. Hard breach s pokračujúcimi dispatchmi je policy enforcement incident, nie iba finančný warning.

## 45. Kapacitné plánovanie

Kapacitný plán používa arrival rate, service-time distribúcie, concurrency, tenant mix a retry amplification. Priemer requests per second nestačí, pretože agentické runy majú variabilný fan-out a dlhé approval waits.

Modeluje sa aj provider quota a interná tool capacity. Capacity shortage sa nesmie riešiť len zvýšením concurrency, ak downstream systém alebo tenant fairness nemá rovnakú rezervu.

## 46. Change management

Zmena model route, context policy, tool catalogu, retry pravidiel alebo budget manifestu je composed-release change. Každá z nich môže zmeniť cost aj latency bez úpravy agent promptu.

Canary porovnáva rovnaké slices a reportuje absolútne aj relatívne zmeny. Rollback obnoví všetky relevantné generations, nie iba model meno.

## 47. Primárne zdroje

- [OpenAI Agents SDK — Usage](https://openai.github.io/openai-agents-python/usage/)
- [OpenAI Agents SDK — Running agents](https://openai.github.io/openai-agents-python/running_agents/)
- [OpenAI Agents SDK — Guardrails](https://openai.github.io/openai-agents-python/guardrails/)
- [OpenAI API — API reference and rate-limit response headers](https://platform.openai.com/docs/api-reference/)
- [Kubernetes — Resource Quotas](https://kubernetes.io/docs/concepts/policy/resource-quotas/)

## 48. Zhrnutie

Cost, latency a token budget je end-to-end operation contract. Riadi admission, planning, model routing, tools, retries, degradation, reconciliation a tenant fairness; samotný provider token count alebo mesačný invoice nestačí.

Bezpečný systém používa exact subject, versionovaný price a budget catalog, hierarchical reservations, in-flight accounting, deadline-derived timeouts, hard forbidden invariants a authoritative read-back. Optimalizácia je prijateľná iba vtedy, keď znižuje cost alebo latency bez zhoršenia required quality, security, reliability a business outcome.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Agent tracing, replay a debugging](agent-tracing-replay-debugging.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
