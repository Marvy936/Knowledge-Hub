# Synchronous vs. asynchronous communication

Synchronous a asynchronous communication neopisujú konkrétny transport. Opisujú, kedy caller očakáva výsledok, ako dlho drží runtime dependency, kde sa nachádza acknowledgement boundary a čo sa stane pri timeout-e, cancellation, retry alebo oneskorenom dokončení. HTTP môže niesť asynchronous contract cez `202 Accepted`; request/reply nad brokerom môže byť z pohľadu callerovho deadline-u stále synchronous.

```text
business operation a user expectation
→ exact caller/callee a contract generation
→ immediate vs. final outcome
→ dependency a deadline graph
→ request, command alebo event boundary
→ durable acceptance alebo immediate completion
→ execution, cancellation a unknown outcome
→ status/result delivery a backlog
→ reconciliation a final business verdict
→ mixed-generation, lost-response a second-attempt test
```

Najdôležitejšie rozlíšenie je medzi tým, čo caller vie po pôvodnom requeste, a tým, čo sa skutočne stalo v authoritative systéme alebo u external providera.

## 1. Communication subject a outcome contract

Exact communication subject musí pomenovať logical business operation, caller a callee generation, request/command/event schema, immediate response, final business outcome, deadline a cancellation boundary, acknowledgement semantics, retry owner, stable identity, ordering a freshness požiadavky a observation point, z ktorého sa outcome dokazuje.

Pre Atlas Payments je public contract:

```text
operation: submit merchant settlement
caller: public API v8.2
callee: settlement command core v8.2
immediate outcome:
  202 + stable operation_id
  až po settlement + outbox commit-e
final outcome:
  completed | rejected | failed-final | reconciliation-required
public deadline: 900 ms
provider attempt deadline: bounded independently
retry identity: merchant_id + idempotency_key
status authority: GET /settlements/{operation_id}
```

`Request succeeded` bez pomenovania boundary môže znamenať iba prijaté bytes, successful validation, durable command, broker publication, consumer processing alebo final provider effect. Jedno HTTP status code nesmie reprezentovať všetky tieto states.

## 2. Synchronous dependency a deadline graph

Pri synchronous interaction caller drží request otvorený, kým očakáva response:

```text
caller intent
→ routing a admission
→ callee execution
→ downstream dependencies
→ response generation
→ response delivery
→ caller decision
```

Tento model je vhodný pre queries a krátke commands, pri ktorých user alebo ďalší krok potrebuje immediate result. Výhodou je jednoduchý control flow a request-scoped identity/tracing. Cena je runtime coupling: caller, callee a critical downstream dependencies musia dokončiť prácu v jednom deadline budgete.

Deadline nie je lokálny timeout každej vrstvy. Je to end-to-end budget:

```text
900 ms public deadline
- gateway, auth a routing
- queue/admission wait
- database transaction
- response transport
- safety reserve
= maximum remaining child dependency budget
```

Ak provider p95 trvá `2.4 s`, provider call sa do truthful `900 ms` contractu nezmestí. Zvýšenie timeoutu môže iba zvýšiť open connections, worker concurrency, queueing a retry amplification. Správnym riešením môže byť oddelenie immediate validation a durable acceptance od deferred provider execution.

Deadline sa propaguje ako remaining absolute budget alebo explicitný child budget. Každá vrstva nesmie začať nový plný timeout. Inak trojsekundový request môže cez niekoľko dependencies trvať desiatky sekúnd.

## 3. Timeout, cancellation a unknown outcome

Timeout znamená, že caller nedostal odpoveď včas. Nehovorí, či callee request prijal, či database commitla alebo či provider vykonal side effect.

```text
caller odošle command
→ callee commitne durable intent
→ provider prijme operation
→ response sa stratí
→ caller vidí timeout
```

Correct classification je `unknown`, nie `failed`. Blind retry môže vytvoriť duplicate physical attempt. Bezpečný retry používa stable operation identity a najprv queryuje authoritative status alebo provider idempotency ledger.

Cancellation je samostatný mechanizmus. Client disconnect môže zastaviť prácu ešte pred admission alebo pred local commitom. Nemôže automaticky rollbacknúť už commitnutú transaction, broker record ani external effect. Každý krok musí byť označený ako cancellable, committed-and-noncancellable, compensatable alebo reconcile-only.

Retry ownership musí byť jednoznačné. Gateway, SDK, service a worker nesmú nezávisle retryovať tú istú operation. Shared attempt budget, stable identity, backoff a outcome lookup chránia capacity aj correctness.

## 4. Asynchronous acceptance a final-state visibility

Pri asynchronous workflow caller nečaká na final execution v pôvodnom requeste:

```text
caller command
→ validation
→ durable acceptance
→ stable operation identity
→ deferred execution
→ intermediate states
→ final outcome
→ query, callback alebo event delivery
```

Výhodou je oddelenie public latency od dlhého processingu, buffering, controlled concurrency a replay/recovery. Cena sú duplicate delivery, backlog, ordering, schema evolution, delayed failure visibility a potreba explicitného status modelu.

Asynchronous neznamená fire-and-forget. `202 Accepted` je správne iba vtedy, keď durable authority prevzala zodpovednosť a operation je queryable. Ak process po `202` môže stratiť in-memory task, acceptance je nepravdivé.

Final result možno sprístupniť cez status resource, webhook, event alebo subscription. Každý model potrebuje authorization, retry, duplicate handling, ordering, retention a freshness contract. Webhook delivery success nie je final business outcome; status cache nesmie skryť authoritative transition.

Business latency sa meria ako acceptance latency plus queue age, consumer wait, execution, retry a reconciliation. API p95 `171 ms` môže byť zelené, zatiaľ čo settlement final completion trvá minúty alebo vôbec nenastane. Preto treba sledovať accepted-to-first-attempt, accepted-to-final, oldest backlog age a sent-unknown cohort.

## 5. Query, command a event semantics

Query žiada representation a typicky nemení authoritative state. Command žiada konkrétneho ownera vykonať transition a môže byť rejected, accepted alebo completed. Event oznamuje fact, ktorý už nastal.

```text
SubmitSettlement(operation_id, policy_generation)
SettlementAccepted(operation_id, committed_at)
SettlementCompleted(operation_id, provider_reference)
```

Názov eventu je súčasť correctness contractu. `SettlementCompleted` je nepravdivý, ak vznikol iba durable intent. Command transportovaný brokerom zostáva command; HTTP response nesie event semantics iba vtedy, keď oznamuje už committed fact.

Acknowledgement levels sa musia oddeľovať: socket prijal bytes, server request parsed, admission succeeded, database commitla intent, broker record durably prijal, consumer spracoval local transaction, provider effect bol potvrdený a final business outcome bol reconciled. Každý level má inú recovery zodpovednosť.

## 6. Connected incident `DB-PAY-58`

Release `8.2` migroval provider execution na durable asynchronous flow:

```text
merchant request
→ gateway
→ PostgreSQL settlement + outbox transaction
→ 202 + operation_id
→ broker
→ provider worker
→ provider
→ final state
```

Legacy `8.1` stále vykonával provider call pred response a vracal `200`. Gateway a Kubernetes Service počas rollout-u miešali obe generations pod jedným endpointom. Provider p95 sa zvýšilo z `420 ms` na `2.4 s`, public deadline zostal `900 ms`.

Za 31 minút prišlo `18 420` requests; `31 %` skončilo na legacy cohort-e; `2 906` calls prekročilo deadline a clients vytvorili `4 118` retry attempts. `43` operations dosiahlo provider ako duplicate physical attempts. Provider idempotency zabránila confirmed duplicate settlementu, ale outcome zostal do reconciliation unknown. Async cohort vracal `202` za p95 `171 ms`, čo zakrylo final completion problém.

Root cause bol mixed immediate-result contract pod jedným route a retry modelom. V8.1 timeout mohol nastať po provider effecte; v8.2 `202` znamenalo iba durable acceptance. Route neexponovala generation a SDK po timeout-e nebola povinná najprv queryovať status.

## 7. Redesign a acceptance paths

Public API teraz vracia `202`, `operation_id`, `status_url` a `accepted_at` až po atomic settlement + outbox commit-e. SDK používa stable idempotency key, po lost response-e queryuje status a rozlišuje `accepted`, `processing`, `completed`, `failed-final` a `reconciliation-required`. Provider worker má vlastný bounded attempt deadline, stable provider idempotency key a pri unknown outcome-e vykoná lookup namiesto blind retryu.

**Positive path** preukáže durable acceptance v public deadline-e a neskorší final outcome dostupný cez authoritative status.

**Recovery path** stratí public response po commite alebo oneskorí provider. SDK nájde existujúcu operation, worker klasifikuje unknown outcome a nevytvorí nový business effect.

**Failure path** odmietne request pred commitom alebo označí final failure explicitne. Accepted operation nesmie zmiznúť bez final alebo reconciliation state-u.

**Forbidden path** odmietne mixed sync/async generations, `202` bez durable operation, timeout interpretovaný ako rollback, viacvrstvové retries a false `completed` pred provider evidence.

Acceptance zahŕňa second attempt, lost response, slow dependency, delayed completion, cancellation pred a po commit-e a old-client/new-contract compatibility test.

## 8. Troubleshooting a anti-patterny

Diagnostika začína exact operation a caller/callee generations, potom immediate/final contractom, deadline graphom, commit/ack evidence, cancellation state, retry ownerom, downstream outcome-om, backlogom a result visibility. Až business reconciliation uzatvára verdict.

Najčastejšie anti-patterny sú `HTTP = sync`, `broker = async`, timeout označený za failure, plošné zvýšenie timeoutu, `202 = hotovo`, fire-and-forget bez durability, async považované za automatickú availability a retry povolený každej vrstve.

## 9. Kontrolné otázky

1. Čo tvorí exact communication subject?
2. Ako sa immediate outcome líši od final outcome-u?
3. Prečo transport neurčuje sync alebo async semantics?
4. Ako sa propaguje deadline budget?
5. Prečo timeout vytvára unknown outcome?
6. Ktoré kroky cancellation už nedokáže vrátiť?
7. Čo dokazujú jednotlivé acknowledgement levels?
8. Ako sa meria accepted-to-final business latency?
9. Prečo mixed v8.1/v8.2 contract spôsobil `DB-PAY-58`?
10. Ktoré positive, recovery, failure a forbidden paths musia prejsť?

## Glossary impact

Relevantné pojmy: communication subject, synchronous communication, asynchronous communication, immediate outcome, final outcome, deadline budget, deadline propagation, cancellation boundary, unknown synchronous outcome, durable acceptance, status resource, command, event, query, acknowledgement level, sync-over-async, async-over-sync, completion latency a communication acceptance verdict.

## Primárne zdroje

- [gRPC — Deadlines](https://grpc.io/docs/guides/deadlines/)
- [gRPC — Cancellation](https://grpc.io/docs/guides/cancellation/)
- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
- [Microsoft Azure Architecture Center — Asynchronous Request-Reply pattern](https://learn.microsoft.com/azure/architecture/patterns/async-request-reply)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Monolith, modular monolith a microservices](monolith-modular-monolith-and-microservices.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Message queues a event-driven architecture →](message-queues-and-event-driven-architecture.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
