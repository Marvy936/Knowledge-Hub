# Durable execution, retries a resumability

Durable agent nie je agent, ktorý beží dlho v jednom procese. Je to execution model, v ktorom možno po páde procesu, strate workera, prerušení siete alebo dlhom čakaní obnoviť **rovnakú business operation** z authoritative persisted state bez straty už potvrdených rozhodnutí a bez nevedomého zopakovania externých side effectov.

Táto kapitola pokračuje v incidentoch `AGENT-OPS-01` a `AGENT-OPS-02` cez `AGENT-OPS-03`. Checkout remediation run prežil reštart orchestration workera, ale po obnove znovu odoslal už commitnutú failover operáciu cez remote tool. Workflow engine obnovil control flow, no tool request nemal stabilnú operation identity a timeout bol nesprávne vyhodnotený ako „akcia sa nestala“. Výsledkom boli dve failover mutácie, rozdielne task IDs a nejasný business stav.

Nosný model kapitoly je:

```text
business operation identity
→ immutable input a loaded generations
→ durable orchestration history alebo checkpoint
→ deterministic decision transition
→ external activity s stable operation ID
→ recorded attempt a authoritative result
→ interruption, timer alebo retry policy
→ resume z posledného committed boundary
→ unknown-outcome reconciliation
→ technical a business read-back
→ terminal state alebo explicit escalation
```

## 1. Business outcome

Cieľom durable execution nie je maximalizovať počet úspešne obnovených procesov. Cieľom je dokončiť alebo bezpečne zastaviť konkrétnu business operation tak, aby po páde nebolo potrebné hádať, ktoré kroky sa už stali a ktoré sa ešte len plánovali.

Pre `AGENT-OPS-03` je subjectom `checkout-recovery-021`, nie Python proces, worker Pod ani model turn. Operácia má obnoviť checkout conversion bez duplicity failoveru, zachovať incident evidence a ukončiť sa iba po authoritative business read-backu.

## 2. Process lifetime verzus operation lifetime

Process lifetime je technická vlastnosť jedného runtime procesu. Operation lifetime môže trvať sekundy, dni alebo týždne a prežiť mnoho procesov, deploymentov a credential rotations.

Ak systém uchováva state iba v pamäti procesu, process crash je zároveň loss of truth. Durable systém externalizuje relevantný state tak, aby nový worker vedel rozlíšiť committed transition od rozpracovaného attemptu.

## 3. Durable execution nie je „retry wrapper“

Retry wrapper opakuje volanie po chybe. Durable execution uchováva identity, transition history, timers, pending external operations, approval state a terminal conditions tak, aby obnovenie pokračovalo z definovaného boundary.

Bez tejto vrstvy môže retry síce zvýšiť dostupnosť, ale zároveň zväčšiť duplicate side effects. Čím dlhší a agentickejší je flow, tým menej je bezpečné považovať každú exception za dôkaz, že predchádzajúca akcia neprebehla.

## 4. Exact run a operation identity

Každé obnovenie musí niesť stabilnú operation identity a novú attempt identity. Operation ID zostáva rovnaké počas celého business procesu; run attempt ID sa mení pri novom workerovi, replayi alebo explicitnom continue-as-new transitione.

```yaml
operation_id: checkout-recovery-021
workflow_type: checkout-remediation/v4
workflow_generation: sha256:7b4d...
run_id: run-20260804-01
attempt_id: attempt-03
tenant: retail-eu
environment: production
input_digest: sha256:61aa...
started_at: 2026-08-04T15:31:12Z
```

Ak sa po páde vytvorí nové `operation_id`, downstream deduplication ho považuje za inú business akciu. Stabilná identity je preto súčasť correctness, nie iba observability metadata.

## 5. Authoritative persisted state

Persisted state musí obsahovať iba dáta potrebné na korektné pokračovanie, audit a recovery. Nestačí uložiť posledný model output, pretože ten nemusí obsahovať approved action digest, pending timer, loaded policy generation alebo unknown external outcome.

Authoritative state typicky zahŕňa exact inputs, plan generation, completed transitions, pending activities, approvals, budgets, external correlation IDs, retry counters, cancellation request a terminal reason. Derived prose summary môže pomáhať modelu, ale nie je jediným recovery source.

## 6. Event history verzus checkpoint

Event-history model ukladá sériu rozhodujúcich udalostí a z nich znovu zostavuje workflow state. Checkpoint model ukladá serializovaný snapshot state v konkrétnom boundary. Oba modely môžu byť durable, ale majú odlišnú recovery a compatibility surface.

Event history poskytuje podrobný causal audit a umožňuje deterministic replay. Checkpoint znižuje replay cost, ale vyžaduje bezpečnú schema migration a jasné pravidlo, ktoré side effects boli commitnuté pred snapshotom.

## 7. Deterministic replay

Pri replayi orchestration code znovu vyhodnocuje historické events a musí dospieť k rovnakým rozhodnutiam. Aktuálny čas, random value, unordered iteration alebo neversionovaný network read nesmú meniť historický control flow.

Nedeterministické hodnoty sa zaznamenajú ako event alebo sa získajú cez workflow-safe API. Inak nový deployment môže pri rovnakej history zvoliť inú vetvu, naplánovať nový tool call alebo preskočiť recovery transition.

```python
def decide_next(state: WorkflowState, history: History) -> Command:
    # current time and random choice must come from recorded workflow events
    now = history.recorded_time()
    route = history.recorded_choice("diagnostic-route")
    return transition(state, now=now, route=route)
```

## 8. Orchestration logic verzus activity

Orchestration logic rozhoduje, čo sa má stať a v akom poradí. Activity vykonáva nedeterministickú alebo externú prácu: API call, database query, command, model inference alebo tool invocation.

Toto oddelenie chráni replay. Orchestration môže byť znovu prehraná bez reálneho vykonania už zaznamenanej activity, zatiaľ čo activity retry má vlastnú identity, timeout a error policy.

## 9. Commit boundary

Commit boundary je bod, po ktorom persisted history jednoznačne dokazuje, že transition bola prijatá durable storeom. Process môže vykonať side effect a spadnúť skôr, než zapíše jeho result; preto external commit a orchestration commit nie sú jedna atomická operácia.

Tento rozdiel vytvára classic unknown outcome. Systém ho rieši stable operation ID, downstream status read-backom alebo reconciliation, nie slepým opakovaním.

## 10. Retry taxonomy

Retry policy sa volí podľa failure triedy. Transport timeout, rate limit, temporary unavailable, validation error, authorization denial a semantic business rejection nemajú rovnakú retry semantics.

```yaml
retry_policy:
  initial_interval: 2s
  backoff_coefficient: 2.0
  maximum_interval: 60s
  maximum_attempts: 6
  non_retryable_errors:
    - INVALID_ARGUMENT
    - AUTHORIZATION_DENIED
    - POLICY_REJECTED
    - RESOURCE_GENERATION_MISMATCH
```

Retryable neznamená safe-to-repeat. Policy povoľuje ďalší attempt iba vtedy, keď activity contract definuje idempotency alebo pred retry prebehne outcome reconciliation.

## 11. Attempt identity a operation identity

Attempt ID identifikuje jedno technické vykonanie. Operation ID identifikuje zamýšľaný business side effect naprieč attemptmi.

Downstream systém má deduplikovať podľa operation identity a uložiť výsledok prvého committed attemptu. Nový attempt potom dostane pôvodný result alebo conflict, nie nový side effect.

## 12. Timeouts

Timeout je limit čakania, nie dôkaz neúspechu. Start-to-close timeout, schedule-to-start timeout, heartbeat timeout a overall operation deadline odpovedajú na rôzne otázky.

Ak client timeoutne po odoslaní requestu, server mohol request prijať a commitnúť. Recovery flow musí preto prejsť do `outcome_unknown`, vyhľadať operation status a až potom rozhodnúť o retry.

## 13. Heartbeats a progress

Dlhá activity môže pravidelne zapisovať heartbeat s progressom a resumable cursorom. Heartbeat dokazuje, že worker žije a poskytuje checkpoint pre ďalší attempt, ale sám nepotvrdzuje business commit.

```json
{
  "operation_id": "checkout-recovery-021",
  "activity_id": "collect-provider-evidence",
  "attempt": 2,
  "cursor": "provider-log:2026-08-04T15:33:00Z",
  "processed_items": 1840,
  "last_authoritative_read": "req-993102"
}
```

Citlivé dáta sa do heartbeat payloadu neukladajú bez retention a encryption policy. Stačí reference alebo digest na durable evidence store.

## 14. Durable timers

Sleep v procese nie je durable timer. Po reštarte procesu sa stratí alebo sa spustí znova od nuly.

Durable timer je persisted command s fire time a cancellation identity. Používa sa na backoff, approval deadline, polling interval alebo scheduled verification bez držania workera počas celého čakania.

## 15. Signals, messages a external events

Dlhý workflow prijíma externé events, napríklad approval decision, cancellation, updated incident severity alebo provider recovery notification. Každý event potrebuje stable message ID, operation scope, authorization context a deduplication.

Event sa nepridáva priamo do model promptu ako trusted truth. Najprv sa validuje schema, caller, version, freshness a allowed state transition; až potom sa stane authoritative workflow eventom.

## 16. Pause a resume

Pause je persisted non-terminal state, nie zastavený thread. State obsahuje dôvod prerušenia, required input alebo approval, deadline, continuation token a allowed next transitions.

OpenAI Agents SDK používa serializovateľný run state pre interruptions a resume; produkčný orchestration model však stále musí vyriešiť durable storage, state schema, external effects a current authorization. Framework snapshot je recovery input, nie automatický dôkaz, že celý business workflow je exactly-once.

## 17. Resume token a continuation integrity

Continuation token odkazuje na exact operation, run generation a pending interruption. Musí byť neuhádnuteľný alebo kryptograficky chránený a nesmie umožniť pokračovať v inom tenantovi či po zmene approved action digestu.

```yaml
continuation:
  operation_id: checkout-recovery-021
  pending_transition: approval-04
  state_generation: 17
  expires_at: 2026-08-04T16:00:00Z
  integrity_digest: sha256:...
```

Resume požiadavka s nezhodnou generation sa odmietne alebo prevedie do explicitného merge/revalidation flow. Last-write-wins je nebezpečný, pretože môže zahodiť cancellation alebo novší approval decision.

## 18. State schema evolution

Durable run môže prežiť deployment novej verzie code. Nová verzia musí vedieť prečítať starý state alebo pinúť staré runs na kompatibilný worker generation.

Schema migration sa testuje na reálnych historických snapshots a event histories. Pridanie default field je jednoduchšie než zmena významu existujúceho enumu, task state alebo tool resultu.

## 19. Code versioning

Workflow code sa neupgraduje implicitne pre historické runs. Version marker alebo explicitná patch vetva určuje, či stará history pokračuje podľa pôvodnej alebo novej logiky.

```python
if workflow.version("approval-revalidation", default=1, new=2) == 1:
    return legacy_resume(state)
return resume_with_policy_and_identity_revalidation(state)
```

Bez version markeru môže rollout vytvoriť nondeterminism alebo zmeniť side-effect semantics uprostred operácie.

## 20. Continue-as-new a bounded history

Veľmi dlhý run môže akumulovať veľkú event history. Continue-as-new vytvorí novú run generation so zachovanou business operation identity a explicitne preneseným compacted stateom.

Compaction nesmie zahodiť pending side effects, unresolved unknown outcomes, approval digests ani audit lineage. Nový run odkazuje na predecessor run a dôvod history rotation.

## 21. Cancellation

Cancellation je request na transition, nie okamžité vymazanie procesu. Workflow musí vedieť, ktoré activities možno zrušiť, ktoré už commitli a ktoré vyžadujú compensation.

Pri cancellation po externom commite sa stav neoznačí jednoducho `canceled`. Najprv sa zaznamená `cancel_requested`, zistí sa effective state a vykoná sa povolený recovery alebo compensation flow.

## 22. Compensation

Compensation nie je databázový rollback. Je to nová business operation, ktorá sa pokúša znížiť alebo napraviť dôsledok už commitnutého side effectu.

Každá compensation má vlastnú identity, authorization, failure modes a acceptance. Napríklad návrat trafficu na pôvodný provider môže byť zakázaný, ak je pôvodný provider stále unhealthy; systém preto nemá predstierať atomickú reverzibilitu.

## 23. Durable execution a model inference

Model call je external activity. Rovnaký prompt nemusí vrátiť rovnaký output a provider request môže mať unknown outcome, preto sa historický model result zaznamená a pri replayi sa nepýta znova, pokiaľ flow explicitne nevytvorí nový inference attempt.

Nový model call po recovery musí mať dôvod, novú inference identity a jasný vzťah k pôvodnému outputu. Inak sa plan môže potichu zmeniť iba preto, že worker spadol.

## 24. Tool execution

Tool call sa zaznamenáva ako proposal, authorized command, execution attempt a result. Durable engine nesmie po replayi znovu autorizovať pôvodný model text bez kontroly exact tool contract generation a argument digestu.

```text
proposal recorded
→ policy and approval recorded
→ command scheduled with operation key
→ executor acknowledged
→ result or unknown outcome recorded
→ postcondition read-back
```

Ak history obsahuje `command scheduled`, ale nie `result recorded`, systém prejde do reconciliation. Nevracia sa automaticky na proposal stage.

## 25. Remote tasks

Remote protocol môže vrátiť durable task handle namiesto finálneho výsledku. Client potom ukladá protocol version, remote task ID, context ID, endpoint identity, auth subject a last observed task state.

Reconnect alebo worker failover nesmie vytvoriť nový remote task, kým status pôvodného tasku nie je známy. Polling a subscription sú read operations; nový `send` je potenciálne nový business attempt.

## 26. Incident `AGENT-OPS-03`

Supervisor schválil failover payment trafficu a durable workflow naplánoval remote tool activity. MCP gateway odoslal request s request ID `req-781`, remote service commitol failover a odpoveď sa stratila pri gateway restarte. Workflow worker spadol pred zápisom resultu.

Po obnove orchestration history ukazovala pending activity, ale executor vytvoril nový operation key a request ID `req-912`. Remote service preto vykonal druhý failover transition a vrátil success. Technický workflow skončil zeleno, hoci checkout conversion ostala znížená a traffic weights boli nekonzistentné.

Správny recovery chain bol:

```text
recover operation checkout-recovery-021
→ detect scheduled activity without durable result
→ query remote status by stable operation key
→ bind discovered commit to original activity attempt
→ skip duplicate mutation
→ verify traffic generation and provider health
→ verify checkout conversion and error budget
→ record terminal business outcome
```

## 27. Failure hypotheses

Pri zlyhaní durable runu nie je dostatočné povedať „retry ho vykonal dvakrát“. Diagnostika najprv zostaví časovú os jednej business operation a oddelí orchestration transition, activity scheduling, remote acknowledgement, external commit a durable result persistence. Až táto chain of custody ukáže, či druhý efekt vznikol preto, že systém stratil history, zmenil identity alebo nesprávne vyhodnotil neznámy outcome.

Druhá vrstva porovná loaded workflow a state generation s generation, ktorá vytvorila pôvodný command. Ak replay zvolil inú vetvu, nový tool alebo iný argument digest, ide o determinism alebo compatibility failure; ak replay zvolil rovnaký command, ale executor mu pridelil nový operation key, ide o side-effect identity failure. Tieto prípady majú odlišný containment aj recovery.

Napokon sa overí terminal proof boundary. Stav `completed` v orchestration store je platný iba vtedy, keď executor ledger a downstream idempotency record vysvetľujú každý attempt a authoritative technical aj business read-back potvrdí zamýšľaný outcome. Nasledujúca taxonómia preto sumarizuje konkrétne miesta, kde môže táto evidence chain prvýkrát divergovat:

- **History gap** — command bol odoslaný, ale durable store neobsahuje scheduling alebo acknowledgement event; treba porovnať executor request log a workflow history.
- **Operation-key drift** — retry vytvoril nový business key namiesto nového attempt ID; downstream dedup store preto prijal druhý side effect.
- **Nondeterministic replay** — nový worker pri rovnakej history zvolil inú vetvu alebo tool; dôkazom je replay failure alebo rozdielny command digest.
- **Unsafe retry classification** — timeout alebo connection reset bol označený ako definitívny failure bez status reconciliation.
- **State-version mismatch** — nový code generation nesprávne interpretoval starý pending state alebo enum.
- **Lost cancellation** — stale snapshot prebil novší cancel request a workflow pokračoval v mutácii.
- **Heartbeat misuse** — progress marker bol považovaný za business commit alebo naopak ignorovaný pri resumable worku.
- **Remote-task duplication** — reconnect vytvoril nový task namiesto resubscribe alebo `get` pôvodného tasku.
- **Compensation loop** — recovery action zlyhala a bola opakovaná bez vlastnej idempotency identity.
- **False terminal success** — orchestration skončila `completed`, ale chýbal authoritative technical a business postcondition.

Každá hypotéza sa testuje proti exact operation/run/attempt IDs, persisted history, executor ledger, downstream idempotency record a business telemetry. Log posledného workera nie je úplný causal record; bez prepojenia týchto artifactov sa incident nesmie uzavrieť ako „transient retry issue“.

## 28. Containment

Pri duplicate alebo replay incidente sa zastaví scheduling nových mutation activities pre affected workflow a tool generation. Existing runs sa presunú do `reconciliation_required`, nie do hromadného retry.

Containment zachová event histories, snapshots, executor logs, remote task IDs a approval artifacts. Worker queue možno ponechať pre read-only diagnostics, zatiaľ čo mutation capability je dočasne odobratá.

## 29. Recovery

Recovery najprv zostaví authoritative operation ledger: ktoré commands boli iba navrhnuté, naplánované, acknowledged, commitnuté alebo neznáme. Potom sa unknown outcomes reconciliujú proti downstream systému a až následne sa rozhodne o resume, retry, compensation alebo manual escalation.

Code fix sa nasadí s explicitnou workflow version branchou. Historické runs sa replay-testujú pred odblokovaním a nový canary run overí crash pred activity, crash po remote commit, timeout, cancellation a resume po deployment upgrade.

## 30. Positive acceptance

Pozitívny test spustí operation, vykoná read-only activity, approval interruption, jednu idempotent mutation activity a business verification. Worker sa počas každej fázy zámerne reštartuje a run musí pokračovať bez straty state alebo duplicate side effectu.

Acceptance zahŕňa rovnaké operation ID, očakávané nové attempt IDs, úplnú history, jeden downstream commit a potvrdený checkout outcome. Samotný workflow status `completed` nestačí.

## 31. Forbidden acceptance

Zakázaný test po nejasnom timeoute vytvorí nový operation key alebo znovu odošle mutation bez status lookupu. Executor musí taký transition odmietnuť alebo presmerovať do reconciliation.

Ďalší test nasadí nekompatibilný code generation nad historickú history. Worker musí failnúť bezpečne, nie potichu zmeniť decision path.

## 32. Recovery acceptance

Recovery test simuluje loss workera po remote commite, corrupted local cache, delayed event delivery, duplicate signal, stale continuation token a rotated credentials. Systém musí zostaviť rovnaký effective state z durable evidence a dokončiť alebo eskalovať operation bez druhej mutácie.

## 33. Second-operation acceptance

Po úspešnom recovery sa spustí nová, odlišná checkout operation. Musí dostať nový operation ID, nesmie zdediť staré pending approvals, retry counters ani remote task handle a zároveň musí používať opravenú workflow generation.

Tým sa overí, že deduplication nie je globálne „už nikdy nevykonaj failover“, ale správne scoped pravidlo pre konkrétnu business operation.

## 34. Praktický checklist

Pred produkčným nasadením musí byť možné zodpovedať, čo je stable operation identity, kde je authoritative history, ktoré transitions sú replay-safe, ktoré activities majú idempotency key, ako sa zisťuje unknown outcome a čo je terminal business proof. Každá odpoveď musí odkazovať na konkrétny schema field, store, query alebo runbook krok.

Ak tím nevie vysvetliť rozdiel medzi worker retry, activity retry a novou business operation, systém ešte nie je pripravený na autonomous mutation. Najbezpečnejší fallback je read-only agent s deterministic human-operated execution.

## 35. Zhrnutie

Durable execution externalizuje operation state a umožňuje pokračovať po páde, ale neodstraňuje distribuované transaction boundaries. Replay chráni orchestration decision history; idempotency a reconciliation chránia externé side effects.

Správna otázka preto nie je „obnovil sa agent?“, ale „obnovila sa rovnaká operation z authoritative state, bez duplicate side effectu, s potvrdeným business outcome-om a reprodukovateľnou causal history?“

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Human-in-the-loop a approval gates](human-in-the-loop-approval-gates.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Idempotency a side-effect control →](idempotency-side-effect-control.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
