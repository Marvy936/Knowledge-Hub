# Agent reliability, fallback a kill switch

Agent reliability neznamená, že model vždy odpovie alebo že workflow nikdy nezlyhá. Znamená, že systém pri modelovej, toolovej, sieťovej, dátovej, policy alebo orchestration chybe prejde do predvídateľného stavu, zachová business a bezpečnostné invarianty a dokáže preukázať, čo sa vykonalo a čo nie.

Táto kapitola pokračuje v incidente `AGENT-GOV-06`. Po prekročení latency budgetu sa remediation agent prepol na lacnejší fallback model a po ďalšom timeoute na náhradný tool endpoint. Fallback route však nebola semanticky ekvivalentná: nepodporovala rovnaký structured output, používala odlišný tool catalog a nepoznala current approval digest. Keď sa objavil tenantový data-mixing alert, operátor stlačil globálny kill switch, ale command išiel cez rovnakú queue ako bežné runy a spracoval sa až po ďalších dvoch mutation dispatchoch.

Nosný lifecycle je:

```text
exact operation, release a reliability objective
→ dependency health a failure classification
→ retry, circuit breaker a bounded recovery policy
→ semantic fallback eligibility
→ state, identity, approval a side-effect transfer
→ degraded deterministic alebo human path
→ out-of-band kill authority a scoped stop
→ in-flight cancellation a unknown-outcome reconciliation
→ recovery, re-enable a canary
→ positive, forbidden a second-operation acceptance
```

## 1. Reliability subject

Reliability sa meria na konkrétnom business journey a composed release. Provider uptime alebo model request success rate nemôže nahradiť úspech operationu, ktorý vyžaduje retrieval, approvals, tools a authoritative read-back.

Subject obsahuje tenant, workflow, service tier, release generations, operation class a požadovaný outcome. Rovnaký agent môže mať iné reliability kontrakty pre read-only diagnosis a pre production mutation.

## 2. Reliability dimensions

Reliability zahŕňa availability, correctness, safety, durability, recoverability, timeliness a observability completeness. Systém môže byť technicky dostupný a zároveň nespoľahlivý, ak vracia fluent, ale stale alebo neautorizovaný výsledok.

Každá dimension má vlastný failure signal a acceptance. Jeden aggregate success rate nesmie skryť, že safe denials, unknown outcomes alebo cross-tenant violations sú nesprávne zaradené ako úspešné odpovede.

## 3. Failure taxonomy

Failure sa klasifikuje podľa vrstvy a semantiky. Rozlišuje sa invalid input, policy denial, model refusal, malformed output, model timeout, rate limit, tool timeout, tool permanent error, unknown side-effect outcome, stale state, dependency incompatibility, approval expiry a operator stop.

Taxonómia určuje ďalší krok. Retry pri malformed deterministic schema môže byť rozumný s opraveným promptom alebo modelom, ale retry neznámeho payment alebo infrastructure mutation outcome-u bez read-backu môže zdvojiť side effect.

## 4. Retry nie je fallback

Retry zopakuje rovnakú alebo ekvivalentnú operáciu proti rovnakej semantickej dependency. Fallback zmení model, provider, tool, workflow alebo authority path a preto vytvára nový compatibility subject.

Ak sa zmení dependency generation, systém musí znovu vyhodnotiť schema, policy, data residency, latency, cost a safety. Označiť každú zmenu ako „retry“ skrýva významný release transition.

## 5. Retry budget

Retry budget je obmedzený počtom pokusov, časom, costom a remaining deadline. Každý ďalší pokus potrebuje klasifikovaný dôvod a ideálne novú diskriminačnú zmenu, napríklad refill po rate limite alebo nový healthy endpoint.

OpenAI Agents SDK napríklad poskytuje `max_turns`, tool timeout exceptions a error handlers, ale tieto mechanizmy samy neurčujú business-safe retry policy. Aplikácia musí rozlíšiť model turn od tool attemptu a od durable workflow recovery.

## 6. Backoff a jitter

Exponential backoff s jitterom znižuje synchronizovaný tlak po výpadku. Backoff sa však nesmie plánovať za end-to-end deadline ani držať scarce worker alebo credential lease bez potreby.

Server-provided retry hints sú vstup, nie absolútna autorita. Policy ich porovná s operation deadline, tenant priority a outage state a potom rozhodne o čakaní, queue alebo degraded path.

## 7. Circuit breaker

Circuit breaker zastaví nové calls do dependency, ktorá opakovane zlyháva alebo vracia nebezpečné outcomes. Stav `open` neznamená, že už dispatchnuté calls nevytvorili side effects; tie sa musia samostatne reconciliovať.

Breaker scope môže byť endpoint, tool action, model route, region alebo tenant-specific integration. Globálny breaker pri lokálnom tenant credential incidente zbytočne poškodí zdravé operácie.

## 8. Bulkhead

Bulkhead izoluje capacity pooly, queues, workers, credentials alebo connections medzi workflowmi a tenantmi. Cieľom je zabrániť, aby slow alebo looping agent vyčerpal zdroje pre kritické deterministic paths.

Izolácia musí zahŕňať aj provider quotas a shared tool limits. Oddelené interné queues nepomôžu, ak všetky používajú rovnaký neobmedzený API key alebo database connection pool.

## 9. Health signals

Dependency health sa neodvodzuje iba z HTTP statusu. Zahŕňa schema compatibility, latency percentily, error classes, data freshness, policy generation, outcome read-back a security anomaly signals.

Healthy control-plane status nie je dôkaz healthy business journey. Canary alebo synthetic operation musí prejsť rovnakou exercised path ako produkčný run, ale bez nebezpečného side effectu.

## 10. Fallback hierarchy

Fallback hierarchy sa navrhuje vopred a používa najmenšiu semantickú zmenu. Typicky ide od retry rovnakého healthy subjectu cez equivalent endpoint alebo model, degraded read-only workflow, deterministic rules, human queue až po explicitný stop.

Hierarchy nie je automatický rebrík, po ktorom agent zostupuje bez kontroly. Každý transition má eligibility policy, required evidence a forbidden actions.

## 11. Model fallback

Model fallback je bezpečný iba vtedy, ak náhradný model prešiel workflow-specific evaly pre output schema, tool selection, argument quality, refusals, latency a forbidden invariants. Rovnaké API rozhranie neznamená rovnaké správanie.

Fallback route musí pinovať model snapshot alebo minimálne versioned alias policy. Implicitný SDK default sa nemá používať ako reliability control, pretože default môže byť zmenený release-om knižnice.

## 12. Provider fallback

Provider fallback mení nielen model, ale často aj tokenization, safety behavior, retention, region, tool semantics a usage reporting. Pred transitionom sa vyhodnotí data residency, contractual scope a capability compatibility.

Conversation alebo session state sa nesmie bez kontroly preniesť medzi providermi. State adapter musí zachovať authoritative facts a odstrániť provider-specific interné items, ktoré druhá strana nevie bezpečne interpretovať.

## 13. Tool fallback

Náhradný tool endpoint musí mať rovnaký action contract, idempotency semantics, authorization scope a read-back authority. Rovnaký názov `update_ticket` alebo `restart_service` nie je dostatočný.

Ak fallback tool podporuje iba širšiu resource scope alebo chýba conditional write, mutation sa nepovolí. Degraded read-only diagnosis je prijateľnejší než „best effort“ zápis bez ochrany.

## 14. Retrieval fallback

Pri výpadku primárneho indexu môže fallback použiť snapshot, secondary search alebo deterministic document store. Každý výsledok musí niesť freshness a authority label, aby stale fallback nebol prezentovaný ako current fact.

Ak required evidence nie je dostupná, agent má abstain alebo eskalovať. Vymyslený answer z modelovej pamäte nie je reliability recovery.

## 15. Deterministic degraded mode

Deterministic fallback používa explicitné pravidlá, templates alebo runbook kroky pre úzky známy scenár. Má menšiu capability, ale predvídateľné boundaries a jednoduchšie acceptance.

Degraded mode musí byť samostatne testovaný a observovaný. Nie je bezpečné predpokladať, že kód, ktorý sa používa iba počas incidentu, bude fungovať bez pravidelných drillov.

## 16. Human fallback

Human queue je legitímny fallback pre high-risk alebo nejednoznačné prípady. Musí však zachovať complete evidence package, priority, deadline, tenant context a action restrictions.

Človek nesmie dostať iba fluent agent summary. Potrebuje authoritative references, unknowns, attempted steps, policy decisions a side-effect state, aby neopakoval neznámu mutation.

## 17. Fallback compatibility manifest

Compatibility manifest uvádza source a target generation, supported operation classes, schema adapter, tool differences, policy constraints a required eval evidence. Bez neho je fallback iba neformálny runtime branch.

Manifest sa vyhodnotí pri každom transitione a jeho digest sa uloží do trace a audit ledgeru. Historical incident potom dokáže vysvetliť, prečo bol konkrétny fallback považovaný za eligible.

## 18. State transfer

Fallback potrebuje explicitný state transfer contract. Prenášajú sa verified facts, operation identity, remaining budget, approvals, side-effect ledger a unresolved unknowns; neprenášajú sa implicitné modelové domnienky ako autorita.

Transfer vytvorí nový execution attempt, ale zachová business operation identity. Tým sa oddeľuje pokračovanie journey od predstierania, že náhradný runtime je rovnaký proces.

## 19. Approval revalidation

Approval je viazaný na action digest, resource, tool generation, arguments a čas. Fallback na iný tool alebo rozšírený scope zneplatní staré approval, aj keď business zámer znie podobne.

Pred execution sa znovu overí reviewer authority, expiry a current state. Dlhý outage môže zmeniť deployment generation alebo tenant entitlement a pôvodné schválenie už nemusí byť použiteľné.

## 20. Side-effect ownership

V jednom okamihu môže mať právo vykonať mutation iba jeden active executor s platným fencing tokenom. Fallback worker nesmie prebrať execution iba preto, že primary prestal odpovedať.

Unknown outcome sa najprv reconciliuje cez external operation key alebo authoritative read. Až known-not-committed stav umožní nový dispatch pod rovnakým business idempotency subjectom.

## 21. Kill switch

Kill switch je out-of-band control, ktorý zastaví nové agentické rozhodovanie alebo citlivé actions bez závislosti od samotného modelu. Model nesmie mať možnosť switch ignorovať, prepísať alebo presvedčiť policy layer, aby ho obišla.

Switch potrebuje ownera, scope, activation authority, propagation SLO, fail-safe behavior a audit. Samotný feature flag v rovnakej cache alebo queue ako incident workload nie je spoľahlivý emergency control.

## 22. Kill-switch scopes

Scope môže byť global, environment, tenant, workflow, agent release, model route, tool server, action class alebo resource set. Najmenší dostatočný scope obmedzí blast radius a zachová healthy deterministic služby.

Global stop je rezervovaný pre systemic alebo unknown-boundary incidenty. Tenantový isolation alert typicky najprv zastaví dotknutého tenanta, shared cache alebo konkrétny tool path a zároveň aktivuje broader monitoring.

## 23. Control-plane authority

Kill-switch command sa podpisuje alebo autentizuje cez oddelený operator identity path. Activation musí byť možná aj pri outage hlavného agent orchestration alebo provider identity systému.

Control plane udržiava desired stop state a executors ho pravidelne aj event-driven načítajú. Jednorazová správa bez authoritative desired state sa môže stratiť alebo prísť neskoro.

## 24. Propagation a loaded state

Dashboard status `disabled=true` nepreukazuje, že worker loaded nový state. Každý runtime reportuje loaded kill-switch generation a zastaví dispatch pred ďalším sensitive boundary.

Acceptance meria čas od authorized activation po posledný povolený nový dispatch. In-flight calls, ktoré prekročili boundary pred activation, sa evidujú oddelene.

## 25. Pre-dispatch enforcement

Kill switch sa kontroluje tesne pred model callom, tool dispatchom, handoffom a side-effect commit boundary podľa scope. Check iba na začiatku runu je nedostatočný pre dlhé workflowy.

Pre approval-based tools sa switch znovu kontroluje po approval a pred execution. OpenAI Agents SDK podobne upozorňuje, že time-sensitive tool input guardrails majú byť revalidované pred execution; aplikácia musí rovnakú zásadu rozšíriť na vlastný emergency policy layer.

## 26. In-flight cancellation

Activation zastaví nové work, ale cancellation in-flight activity závisí od tool semantics. Cancel request môže byť best effort a response `cancelled` nemusí znamenať, že external mutation nebola commitnutá.

Každá activity prejde do known-cancelled, known-completed alebo unknown-outcome stavu. Unknown sa reconciliuje pred recovery alebo opätovným povolením.

## 27. Safe state po kill switchi

Safe state môže znamenať read-only, no-new-work, no-mutations alebo full stop podľa incidentu. Policy musí určiť, či sú povolené evidence export, cancellation a reconciliation operácie.

Emergency operations používajú oddelené capabilities a budget. Nesmú sa stať skrytým broad admin pathom dostupným modelu.

## 28. Re-enable policy

Re-enable nie je opačný boolean flip. Vyžaduje root-cause evidence, corrected release, clean pending-side-effect ledger, canary plan, approver a expiry.

Scope sa obnovuje postupne. Najprv synthetic alebo shadow path, potom limitovaný tenant alebo percentage canary a až následne širšia prevádzka.

## 29. Kill-switch drills

Drill overuje activation authority, propagation, worker loaded state, queue draining, in-flight classification a audit completeness. Musí používať bezpečný test subject, ale rovnaký control path ako produkcia.

Papierový runbook nestačí. Ak sa switch nikdy neaktivoval proti reálnym workers a tools, jeho propagation SLO je iba predpoklad.

## 30. Reliability SLI a SLO

SLI môže merať accepted outcome rate, safe termination rate, unknown-outcome backlog, fallback success, kill-switch propagation, recovery time a forbidden-event rate. Availability model requestov je len pomocná dependency metrika.

SLO sa segmentuje podľa operation class a tenant tieru. Mutation workflow môže mať nižší throughput, ale prísnejší forbidden-side-effect cieľ než read-only assistant.

## 31. Error budget

Reliability error budget kvantifikuje tolerovaný nesplnený outcome za okno. Bezpečnostné forbidden events však často nemajú spotrebovateľný budget a pri jednom incidente blokujú release.

Cost a reliability budgets sa nesmú zamieňať. Systém nemôže „ušetriť“ reliability error budget zvýšením tokenov bez kontroly ani akceptovať cross-tenant leak, pretože ostatné metriky sú zelené.

## 32. Brownout a shed load

Brownout vypína voliteľné features, napríklad deep retrieval alebo speculative specialists, aby zachoval core journey. Load shedding odmieta alebo odkladá nové low-priority work pred preťažením.

Obe stratégie musia byť visible a tenant-fair. Silent quality degradation bez response labelu alebo audit eventu je nesprávny outcome.

## 33. Incident `AGENT-GOV-06`

Primary model route prekročil latency budget po provider rate limite. Orchestrator prepol na fallback model a následne na secondary tool server, ale compatibility manifest neobsahoval approval a schema differences.

Fallback vytvoril broader mutation proposal a shared queue pokračovala aj po global kill-switch commande. Command bol spracovaný až po bežných jobs, preto dva workers vykonali ďalšie dispatch calls. Jeden skončil known-failed, druhý unknown a musel sa overiť cez external ledger.

## 34. Konkurenčné hypotézy

Prvá hypotéza hľadá provider outage. Druhá predpokladá nesprávny fallback compatibility verdict. Tretia skúma stale kill-switch state na workers a štvrtá queue priority inversion.

Evidence zahŕňa route transition, loaded manifest digests, approvals, tool schema, control-plane desired generation, worker acknowledgements, queue timestamps, fencing tokens a external operation ledger. Samotný dashboard `disabled` nevylučuje dispatch po activation.

## 35. Containment

Containment nastaví scoped stop pre dotknutý workflow a secondary tool, presunie control messages do dedicated priority channel a zakáže nové handoffs. Existing unknown outcomes sa označia a pridelia reconciliation workerom bez mutation capability.

Zdravý read-only support path zostáva dostupný, ak jeho dependencies a tenant boundaries sú známe. To znižuje business impact bez obnovenia nebezpečnej autonomy.

## 36. Recovery

Recovery pridá compatibility manifest, pre-dispatch loaded-generation check, dedicated kill control plane a fencing pre mutation executors. Fallback route sa znovu evalvuje na incident slices, malformed outputs, approval expiry a provider timeoutoch.

Re-enable začne synthetic runom, potom canary tenantom a až po clean side-effect ledger širším rolloutom. Historical traces zostanú čitateľné s pôvodnými generations.

## 37. Positive acceptance

Primary dependency failure aktivuje správny klasifikovaný path. Equivalent fallback dokončí operation v deadline, zachová schema, identity, approval, idempotency a business read-back.

Trace a audit ledger ukážu dôvod transitionu a loaded compatibility manifest. Nevznikne duplicate mutation ani neautorizovaný scope expansion.

## 38. Forbidden acceptance

Release neprejde, ak fallback vráti fluent odpoveď, ale použije širší tool, stale approval alebo iný tenant context. Neprípustný je aj kill switch, ktorý mení iba dashboard a nevie preukázať worker loaded state.

Globálny stop nesmie zanechať unknown outcomes bez reconciliation. „Žiadne nové logy“ nie je dôkaz, že in-flight external systém nič nevykonal.

## 39. Recovery acceptance

Test aktivuje kill switch počas model callu, read-only toolu, approval waitu a mutation dispatchu. Každý run skončí v definovanom stave a všetky external attempts sa klasifikujú.

Po oprave canary prejde primary aj fallback pathom. Re-enable sa odmietne, ak existuje stale worker, unresolved unknown alebo neplatný compatibility manifest.

## 40. Second-operation acceptance

Nová operation po re-enable používa fresh route decision, kill-switch generation, approval a fencing token. Nesmie zdediť degraded state alebo cancellation z incident runu.

Súbežná operation iného tenanta preukáže, že scoped containment nebolo neúmyselne globálne. Zároveň však nesmie pristúpiť k shared dependency, ktorá zostáva explicitne blocked.

## 41. Praktický reliability manifest

Manifest rozdeľuje retry, fallback a stop decisions na explicitné policy branches. Každá branch uvádza eligibility, hard restrictions a evidence, takže model ani orchestrator nemôžu voľne zamieňať recovery paths.

Príklad nie je runtime proof. Produkcia musí preukázať loaded digest, dependency health inputs, executed branch a side-effect reconciliation.

```yaml
reliability_policy:
  version: reliability/v7
  workflow: checkout-remediation
  primary_route: model-route/support-primary@sha256:1a2b
  retry:
    max_attempts: 2
    retryable: [rate_limit, transient_network]
    unknown_mutation_outcome: reconcile_only
  fallback:
    - target: model-route/support-secondary@sha256:9d8e
      requires: [schema_compatible, trajectory_eval_passed]
      actions: [diagnostics.read]
    - target: deterministic/read-only-runbook@v3
      actions: [diagnostics.read, case.enqueue_human]
  kill_switch:
    authority: emergency-policy/control-plane
    scopes: [tenant, workflow, tool_action, release, global]
    propagation_slo_ms: 3000
    emergency_actions: [cancel, reconcile, audit.write]
```

## 42. Praktický pre-dispatch pseudocode

Pre-dispatch gate číta authoritative desired stop state, porovná ho s runtime loaded generation a až potom povoľuje konkrétny action. Rozhodnutie je viazané na tenant, operation, release a tool semantics, nie iba na procesový flag.

Pseudocode zároveň ukazuje, že unknown outcome sa nerieši fallback dispatchom. Reconciliation je samostatná povinná branch, ktorá zachová single-writer a idempotency boundaries.

```python
async def dispatch_with_reliability_policy(run, action):
    stop_state = await emergency_control.read_authoritative_state()
    runtime = await worker_state.loaded_generation(run.worker_id)

    decision = reliability_policy.evaluate(
        tenant=run.tenant_id,
        workflow=run.workflow,
        release=run.release_digest,
        action=action.contract,
        stop_state=stop_state,
        loaded_stop_generation=runtime.kill_generation,
        dependency_health=health_snapshot(action.dependency),
        remaining_deadline=run.remaining_deadline,
    )
    if decision.stop:
        return await enter_safe_state(run, decision)

    try:
        return await action.execute(fencing_token=run.fencing_token)
    except UnknownOutcome as error:
        return await reconcile_external_outcome(run, action, error.operation_ref)
    except decision.retryable_errors as error:
        return await bounded_retry_or_fallback(run, action, error, decision)
```

## 43. Prevádzkové metriky

Sleduje sa accepted outcome rate, safe failure rate, fallback activation a success, retry amplification, circuit state, unknown-outcome age, kill-switch propagation, stale-worker count, cancellation completion a recovery time. Metriky sa segmentujú podľa tenant, workflow, route a tool action.

Osobitne sa sleduje semantic fallback regression. Nízka error rate náhradného modelu nestačí, ak rastie tool count, approval mismatch alebo forbidden event rate.

## 44. Alerting

Alert uvádza exact dependency a policy subject, current route, failure class, fallback branch, kill-switch generation a side-effect state. Bez toho operátor nevie, či má meniť provider route, tool policy alebo control-plane propagation.

Kill-switch alert je dvojstupňový: activation accepted a enforcement complete. Ak worker acknowledgements alebo last-dispatch watermark neprejdú propagation SLO, ide o critical control failure.

## 45. Change management

Reliability policy, fallback manifest, queue priority, health classifier a kill-switch implementation sú release artifacts. Zmena jedného z nich vyžaduje scenario evaly a drill, aj keď agent prompt zostal rovnaký.

Rollback obnoví coordinated set. Starý fallback manifest s novým tool catalogom môže byť nebezpečnejší než aktuálny release.

## 46. Primárne zdroje

- [OpenAI Agents SDK — Running agents](https://openai.github.io/openai-agents-python/running_agents/)
- [OpenAI Agents SDK — Guardrails](https://openai.github.io/openai-agents-python/guardrails/)
- [OpenAI Agents SDK — Runner API](https://openai.github.io/openai-agents-python/ref/run/)
- [OpenAI Agents SDK — Release process and changelog](https://openai.github.io/openai-agents-python/release/)
- [NIST AI RMF Playbook — Manage](https://airc.nist.gov/airmf-resources/playbook/manage/)

## 47. Zhrnutie

Agent reliability je vlastnosť end-to-end operationu, nie model endpointu. Retry, fallback, degraded mode a kill switch musia zachovať identity, policy, approval, side-effect a outcome semantics aj pri zmene runtime dependency.

Bezpečný systém používa klasifikované failures, bounded retries, versionované compatibility manifests, single-writer execution, out-of-band scoped kill authority, loaded-state evidence a pravidelné drilly. Fallback alebo stop je úspešný až vtedy, keď technický aj business stav a všetky descendant effects prejdú authoritative reconciliation.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Cost, latency a token budgets](cost-latency-token-budgets.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
