# Synchronous vs. asynchronous communication

Synchronous a asynchronous communication nie sú dva názvy pre `HTTP` a `queue`. Opisujú, **kedy caller očakáva výsledok, ako dlho drží execution dependency, kde sa nachádza acknowledgement boundary a čo sa stane pri timeout-e, retry, partial failure alebo oneskorenom dokončení**.

Synchronous call môže používať HTTP, gRPC, database protocol alebo lokálne function call. Asynchronous workflow môže používať broker, durable outbox, polling, callback, webhook alebo workflow engine. Rovnaký transport môže niesť odlišné semantics: HTTP `202 Accepted` môže spustiť asynchronous processing, zatiaľ čo request/reply nad message brokerom môže byť stále synchronný z pohľadu callerovho deadline-u.

```text
business operation a user expectation
→ exact communication subject
→ required immediate a deferred outcomes
→ dependency a deadline graph
→ request/command/event contract
→ acknowledgement boundary
→ execution, cancellation a retry semantics
→ result delivery a status visibility
→ business reconciliation
→ second-attempt a dependency-failure validation
```

## 1. Exact communication subject

Tvrdenie `služby komunikujú asynchrónne` je neúplné. Subject musí uvádzať:

- logical business operation;
- caller a callee identity/generation;
- request, command alebo event type a schema generation;
- immediate response contract;
- final business outcome;
- deadline a cancellation boundary;
- acknowledgement semantics;
- retry owner a idempotency identity;
- ordering a freshness požiadavky;
- failure a recovery model;
- observation point a authoritative evidence.

Príklad:

```text
operation: submit merchant settlement
caller: public settlement API 8.2
callee: settlement command core 8.2
immediate result: 202 + stable operation_id after settlement/outbox commit
final result: completed, rejected alebo failed-final
caller deadline: 900 ms
provider execution deadline: 20 s per bounded attempt
status visibility: GET /settlements/{operation_id} + event stream
retry identity: merchant_id + idempotency_key
```

Ak sa immediate a final outcome nerozlíšia, `request succeeded` môže znamenať iba prijatie bytes, durable command, začatie práce alebo dokončený business effect.

## 2. Synchronous communication

Pri synchronous interaction caller čaká na response v rámci jedného request lifetime-u.

```text
caller intent
→ connection/request creation
→ routing a admission
→ callee execution
→ downstream dependencies
→ response generation
→ response delivery
→ caller decision
```

Výhody:

- jednoduchý lokálny control flow;
- okamžitý success/failure result;
- prirodzené request-scoped authentication a tracing;
- vhodné pre queries a krátke commands s bounded latency;
- jednoduchšia user interaction, keď výsledok musí byť okamžite známy.

Náklady:

- caller a callee musia byť súčasne dostupné;
- downstream latency sa skladá do jednej critical path;
- timeout môže nastať po vykonaní side effectu;
- cancellation nemusí zastaviť už commitnutú alebo external operation;
- retries môžu zosilniť overload;
- dlhé dependency chains znižujú availability celého workflowu.

Synchronous nie je automaticky silne konzistentné. Caller môže dostať odpoveď zo stale replica, callee môže commitnúť iba lokálnu časť workflowu alebo response môže byť stratená po úspešnom side effecte.

## 3. Deadline budget a propagation

Caller timeout nie je iba UI nastavenie. Je to budget rozdelený cez celý dependency graph.

```text
end-to-end deadline
= gateway/routing
+ queueing/admission
+ application execution
+ downstream calls
+ response transport
+ safety reserve
```

Príklad:

```text
client deadline:            900 ms
gateway + auth:             90 ms
command admission:          80 ms
PostgreSQL transaction:    180 ms
provider p95:            2 400 ms
```

Takýto provider call sa do 900 ms contractu nezmestí. Zvýšenie timeoutu môže iba presunúť problém do connection pools, thread pools a user latency. Správne možnosti môžu byť:

- zmeniť product expectation;
- vrátiť durable acceptance a final result doručiť neskôr;
- použiť bounded degraded path;
- znížiť dependency work;
- rozdeliť operation na immediate validation a deferred execution.

Deadline sa má propagovať ako absolútny remaining budget alebo explicitný child budget. Každá vrstva nemá začínať nový plný timeout, pretože tak vzniká unbounded tail latency.

## 4. Timeout, cancellation a unknown outcome

Timeout znamená iba, že caller nedostal výsledok včas. Neznamená automaticky:

- callee request neprijal;
- transaction rollbackla;
- provider operation sa nevykonala;
- server prestal pracovať;
- retry je bezpečný.

```text
caller odošle command
→ callee commitne operation
→ callee zavolá provider
→ provider vykoná side effect
→ response sa stratí alebo príde po deadline-e
→ caller vidí timeout
```

Výsledok je `unknown`, nie `failed`. Retry musí použiť stable idempotency identity a pred novým side effectom overiť authoritative operation/provider evidence.

Cancellation je samostatný contract. TCP disconnect alebo gRPC cancellation môže prerušiť lokálnu prácu, no nemusí odvolať už odoslaný provider request, database commit alebo broker publication. Callee potrebuje vedieť, ktoré kroky sú:

- bezpečne cancellable;
- commitnuté a necancellable;
- compensatable;
- reconcile-only.

## 5. Asynchronous communication

Pri asynchronous workflow caller nečaká na final execution v pôvodnom requeste.

```text
caller command
→ validation a durable acceptance
→ stable operation identity
→ deferred execution
→ intermediate states
→ final outcome
→ status query, callback alebo event
```

Výhody:

- oddelenie caller latency od dlhého downstream processingu;
- buffering a controlled concurrency;
- lepšia absorpcia transient spikes;
- nezávislé scaling a failure recovery;
- replay a audit trail pri durable logu.

Náklady:

- accepted nie je completed;
- treba status model a result delivery;
- duplicate delivery a retry sú normálne failure modes;
- ordering a freshness sú explicitné, nie implicitné;
- backlog predlžuje business latency;
- schema evolution, retention a replay menia operational surface;
- debugging vyžaduje end-to-end identity a evidence chain.

Asynchronous neznamená fire-and-forget. Bez durable acceptance, ownershipu, retry policy, final-state visibility a reconciliation je to iba strata kontroly nad outcome-om.

## 6. Commands, events a queries

### Query

Žiada current representation alebo odvodené dáta. Typicky nemá meniť authoritative state.

### Command

Žiada konkrétnemu ownerovi vykonať business transition.

```text
SubmitSettlement(operation_id, merchant_id, amount, policy_generation)
```

Command môže byť odmietnutý, accepted alebo completed. Má explicitného recipienta a očakávaný outcome.

### Event

Oznamuje fact, ktorý už nastal.

```text
SettlementAccepted(operation_id, committed_at, schema_version)
```

Event nemá predstierať future intent. Názov `SettlementCompleted` je nesprávny, ak provider side effect ešte neprebehol.

## 7. Acknowledgement levels

Komunikačný contract musí pomenovať, čo acknowledgement dokazuje:

1. bytes boli prijaté socketom;
2. request bol parsed;
3. command prešiel admission;
4. intent bol durable commitnutý;
5. message broker prevzal zodpovednosť;
6. consumer message prijal;
7. consumer local transaction commitla;
8. external side effect bol potvrdený;
9. final business outcome bol reconciled.

Jedno `200`, `202` alebo broker acknowledgement nemá reprezentovať všetky úrovne.

Pre Atlas settlement API je immediate acceptance:

```text
HTTP 202
→ settlement row + outbox row committed v jednej PostgreSQL transaction
→ stable operation_id možno queryovať
→ final status príde neskôr
```

Nie je to tvrdenie, že provider už settlement dokončil.

## 8. Result delivery patterns

Asynchronous result možno sprístupniť cez:

- polling stable status resource-u;
- long polling;
- webhook/callback;
- server-sent events;
- WebSocket subscription;
- downstream event topic;
- notification service.

Každý model potrebuje:

- identity a authorization;
- delivery retry semantics;
- duplicate handling;
- current versus historical generation;
- retention;
- ordering;
- final-state authority.

Webhook delivery success neznamená, že receiver business result spracoval. Polling cache nesmie skryť final transition. Event consumer môže byť oneskorený, preto status resource má uvádzať authoritative alebo explicitne derived freshness.

## 9. Backlog a business latency

Asynchronous architecture presúva časť čakania z request threadu do backlogu.

```text
business completion latency
= acceptance latency
+ queue age
+ consumer wait
+ execution latency
+ retry delay
+ reconciliation delay
```

API p95 môže klesnúť zo sekúnd na 150 ms, zatiaľ čo final completion p95 narastie na 20 minút. Preto treba samostatne merať:

- acceptance rate a latency;
- queue age, nie iba queue depth;
- time-to-first-attempt;
- final completion latency;
- final failure rate;
- sent-unknown cohort;
- backlog drain capacity.

## 10. Sync-over-async a async-over-sync

### Sync-over-async

Caller publikuje command a blokuje, kým nepríde reply event. Z pohľadu calleru je workflow stále synchronous a zdedí deadline/correlation/reply-loss problémy.

### Async-over-sync

Background worker vykonáva synchronous provider call. Top-level workflow je asynchronous, ale worker stále potrebuje timeout, cancellation, concurrency a unknown-outcome contract.

Architektúru treba analyzovať na každej hranici, nie jedným labelom pre celý systém.

## 11. Worked incident `DB-PAY-58`

Atlas Payments release `8.2` migroval provider execution z legacy synchronous request pathu na durable asynchronous flow.

Intended path:

```text
merchant request
→ API gateway
→ settlement command core
→ PostgreSQL transaction: settlement + outbox
→ HTTP 202 + operation_id
→ broker
→ provider worker
→ provider
→ final settlement event/state
```

Legacy `8.1` path stále vykonával provider call pred response:

```text
merchant request
→ gateway
→ legacy settlement service
→ provider call
→ PostgreSQL update
→ HTTP 200
```

Gateway a Service selectors počas rollout-u miešali oba contracts. Provider p95 latency súčasne stúpla z `420 ms` na `2.4 s`, kým public deadline zostal `900 ms`.

Počas 31 minút:

- `18 420` settlement requests prišlo do gatewaya;
- `31 %` trafficu skončilo na legacy synchronous cohort-e;
- `2 906` legacy calls prekročilo client deadline;
- clients vytvorili `4 118` retry attempts;
- `43` operations dosiahlo provider ako duplicate physical attempts;
- provider idempotency zabránila confirmed duplicate settlementu, ale outcome bol do reconciliation neznámy;
- async cohort vracal `202` za p95 `171 ms`, no dashboard sledoval iba acceptance latency.

### Communication root cause

Primary communication root cause bol **mixed immediate-result contract pod jedným endpointom a jedným client retry modelom**:

- v8.1 timeout mohol nastať po provider effecte;
- v8.2 `202` znamenalo iba durable acceptance;
- gateway neexponovala contract generation;
- clients nevedeli rozlíšiť unknown synchronous outcome od accepted asynchronous operation;
- status resource nebol povinnou súčasťou SDK retry flowu.

Provider slowdown bol trigger. Discovery/routing mix bol causal amplifier. Queue a cache failures v ďalších kapitolách vysvetľujú, prečo ani správne accepted async operations nemuseli dokončiť správne.

## 12. Evidence-preserving containment

```text
freeze gateway a Service selector changes
→ preserve route/discovery/backend generation per request
→ disable blind client retries
→ expose one stable operation lookup
→ classify v8.1 timed-out a v8.2 accepted cohorts
→ query PostgreSQL/outbox/broker/provider evidence
→ fence ambiguous legacy writes
→ continue iba bounded async acceptance
```

Každá operation bola klasifikovaná ako:

- rejected-before-commit;
- accepted-durable;
- provider-never-sent;
- provider-sent-unknown;
- provider-completed;
- final-failed;
- duplicate-attempt-with-single-effect.

## 13. Authoritative redesign

Nový public contract:

```text
POST /settlements
→ validate request a policy generation
→ atomic settlement + outbox commit
→ 202 Accepted
→ operation_id + status URL + accepted_at
```

Client SDK:

- používa stable idempotency key;
- po timeout-e queryuje operation status pred novým create attemptom;
- nerozlišuje success iba podľa HTTP response delivery;
- interpretuje `accepted`, `processing`, `completed`, `failed-final` a `reconciliation-required`;
- má bounded polling/backoff budget.

Provider worker:

- používa vlastný attempt deadline;
- prenáša stable provider idempotency key;
- po unknown outcome-e nerepeatne side effect bez provider lookupu;
- zapisuje durable attempt/result evidence.

## 14. Communication acceptance verdict

Communication design je prijatý, keď:

- exact logical operation a actors/generations sú explicitné;
- immediate a final outcome sú oddelené;
- synchronous dependency chain sa zmestí do truthful deadline budgetu;
- deadline propagation a cancellation semantics sú definované;
- timeout sa neinterpretuje automaticky ako failure;
- acknowledgement level je explicitný;
- asynchronous acceptance je durable a queryable;
- status/result delivery má authorization, retry a freshness contract;
- backlog age a final completion sú merané;
- retry owner, stable identity a unknown-outcome reconciliation sú overené;
- mixed contract generations sú odmietnuté;
- second attempt, slow dependency, lost response a delayed completion tests prejdú;
- forbidden duplicate external effect a false-completed outcome zlyhajú.

## 15. Troubleshooting flow

```text
request timeout, accepted-never-completed alebo duplicate attempt
→ exact operation/caller/callee generations
→ immediate vs final outcome contract
→ end-to-end deadline a queueing budget
→ commit/acknowledgement evidence
→ cancellation a in-flight work
→ retry identity a owner
→ downstream/provider outcome
→ async backlog a result visibility
→ business reconciliation
→ second-attempt/dependency-failure validation
```

## 16. Anti-patterny

### HTTP je synchronous, broker je asynchronous

Transport neurčuje caller wait a outcome semantics.

### Timeout = operation zlyhala

Operation mohla commitnúť alebo vykonať external effect.

### Zvýšime timeout

Môže iba zvýšiť concurrency, pool pressure a user latency.

### `202` znamená hotovo

Znamená iba to, čo explicitne definuje acceptance contract.

### Fire-and-forget

Bez durability, ownershipu a final-state visibility je to uncontrolled loss.

### Async vyrieši availability

Pridáva broker, backlog, duplicates, schema a recovery failure modes.

### Retry patrí každej vrstve

Nezávislé retries násobia attempts a ničia deadline/capacity budget.

### Cancellation rollbackne všetko

Commitnuté a external operations môžu pokračovať.

## 17. Kontrolné otázky

1. Čo tvorí exact communication subject?
2. Ako sa synchronous a asynchronous communication líšia od transportu?
3. Ako sa immediate a final outcome odlišujú?
4. Čo je deadline budget a ako sa propaguje?
5. Prečo timeout vytvára unknown outcome?
6. Kedy je cancellation účinná?
7. Ako command, event a query líšia intent?
8. Ktoré acknowledgement levels treba rozlíšiť?
9. Ako sa meria business latency asynchronous flowu?
10. Prečo mixed v8.1/v8.2 contract spôsobil `DB-PAY-58`?
11. Ako má client retryovať po stratenom response?
12. Čo musí overiť communication acceptance verdict?

## Glossary impact

Relevantné pojmy: communication subject, synchronous communication, asynchronous communication, immediate outcome, final outcome, deadline budget, deadline propagation, cancellation boundary, unknown synchronous outcome, durable acceptance, status resource, command, event, query, acknowledgement level, sync-over-async, async-over-sync, completion latency a communication acceptance verdict.

## Primárne zdroje

- [gRPC — Deadlines](https://grpc.io/docs/guides/deadlines/)
- [gRPC — Cancellation](https://grpc.io/docs/guides/cancellation/)
- [HTTP Semantics — RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Microsoft Azure Architecture Center — Asynchronous Request-Reply pattern](https://learn.microsoft.com/azure/architecture/patterns/async-request-reply)
