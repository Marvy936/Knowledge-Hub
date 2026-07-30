# Consistency models

Consistency model je contract nad tým, ktoré histories operations systém povoľuje. Nehovorí iba, či sa replicas „nakoniec zosúladia“. Určuje, čo môže client pozorovať po completed write-e, pri concurrency, medzi sessions, počas failover-u, cez cache/projection a pred external side effectom.

```text
business invariant a user expectation
→ exact objects, operations a clients
→ real-time, program a causal order
→ transaction a visibility scope
→ named consistency model
→ database/replica/cache mechanism
→ observed history + revision evidence
→ allowed alebo forbidden outcome
→ conflict/reconciliation decision
→ second-client, failover a partition validation
```

`Strong`, `eventual` alebo `read replica` bez formálnej properties, scope-u a failure behavioru nie sú testovateľné architecture contracts.

## 1. Consistency subject a history

Exact subject musí pomenovať objects alebo key range, operation a transaction scope, clients/sessions, primary/replica/cache path, required real-time order, causal dependencies, acknowledgement boundary, partition/failover scenario a external effects.

Príklad current route contractu:

```text
write generation 912 completes
→ provider-selection read starts neskôr
→ read musí vrátiť 912 alebo novšiu
→ response nesie observed revision/term
→ settlement persistuje used generation
→ až potom provider effect
```

Consistency sa overuje cez invocation, response a observed values viacerých operations. Jeden successful request alebo converged final snapshot nedokazuje, že forbidden intermediate history nenastala.

Transaction isolation a distributed consistency sa prekrývajú, ale nie sú totožné. Database môže mať serializable local transactions a stale replica reads. Iný store môže poskytovať linearizable single-key operations bez multi-key transaction. End-to-end contract musí pokryť obe vrstvy.

## 2. Silné models a real-time order

**Linearizability** vyžaduje, aby každá operation vyzerala ako atomic point medzi invocation a response a rešpektovala real-time order non-overlapping operations. Completed write `912` nesmie byť pri neskoršom current read-e nasledovaný `911`.

Je vhodná pre leader/lease ownership, create-if-absent idempotency, current revocation, provider route a ďalšie reads, ktoré autorizujú non-mergeable mutation alebo external effect. Cena môže byť quorum latency a refusal počas partition-u.

**Sequential consistency** poskytuje jedno global order zachovávajúce program order každého clienta, ale nemusí rešpektovať real time medzi clients. User expectation `po dokončení zmeny ju nový request vidí` preto môže vyžadovať linearizability, nie iba sequential consistency.

**Serializability** usporiada transactions ako nejakú serial execution, no nemusí rešpektovať wall-clock completion. **Strict serializability** kombinuje serializability s real-time orderom. Ani strict serializable database transaction automaticky nezahŕňa provider call mimo transaction boundary.

Model musí byť naviazaný na exact scope: single key, range, transaction, replicated log alebo celý workflow. `Store is linearizable` neznamená, že cache a gateway nad ním sú linearizable.

## 3. Causal, eventual a bounded-stale models

**Causal consistency** zachováva happens-before dependencies. Ak settlement referencuje policy generation `912`, observer musí byť schopný vidieť tú policy pred dependent state-om. Potrebuje causal/version context; timestamp sám osebe nemusí zachytiť dependency ani trustworthy order.

**Eventual consistency** zvyčajne znamená, že bez nových updates a pri obnovenej komunikácii replicas nakoniec konvergujú. Neurčuje maximálnu staleness, monotonic reads, read-your-writes, conflict winnera, ordering ani správnosť external effects vykonaných pred convergence.

**Bounded staleness** pridáva explicitnú hranicu: time age, revision lag, event offset, count versions alebo business generation gap. Generation bound je často silnejší než `age < 30 s`:

```text
required_generation = 912
observed_generation = 911
→ read nesmie autorizovať provider effect
```

**Consistent prefix** dovoľuje clientovi vidieť starší prefix ordered streamu, ale nie event `102` bez `101`. Je dôležitý pre projections a dependent schema/state transitions.

Conflict resolution musí byť domain-specific: last-write-wins s akceptovanou stratou, application merge, reject/manual resolution alebo CRDT. Replica convergence nevráti external call vykonaný zo stale state-u.

## 4. Session guarantees a version tokens

Slabší global model môže poskytovať useful per-session properties:

- read-your-writes: session vidí vlastný completed write alebo novší state;
- monotonic reads: po pozorovaní `912` už neuvidí `911`;
- monotonic writes: writes jedného clienta sa aplikujú v program order;
- writes-follow-reads: write je usporiadaný po state-e, ktorý client predtým čítal.

Sticky connection sama osebe nie je guarantee. Failover, process restart, cache alebo endpoint change ju môžu porušiť. Client/SDK potrebuje session identity a minimum observed revision/generation token.

```text
response observed_revision=18420
→ client carries minimum_revision=18420
→ later read returns >=18420
   alebo explicitne odmietne/degraduje
```

Response evidence môže obsahovať datastore revision, commit sequence, event offset, policy generation, ETag, leader term, observed timestamp a stale marker. Bez týchto tokenov sa freshness iba predpokladá.

## 5. End-to-end visible consistency

User observation prechádza viacerými layers:

```text
authoritative database
→ replication
→ CDC/event delivery
→ projection apply
→ distributed/local cache
→ gateway/client cache
→ user alebo side-effecting service
```

Silná primary consistency sa môže stratiť na async replica, skipped consumer offset, out-of-order projection, stale cache, mixed deployment alebo client reuse. End-to-end property je najslabší effective link pre danú operation.

Read-only endpoint môže byť correctness-critical. Dashboard môže tolerovať bounded stale marker. Current provider selection, revocation alebo dedupe decision pred external callom potrebuje current authority alebo minimum generation. Klasifikácia sa robí podľa toho, čo read autorizuje, nie podľa HTTP methodu.

Projection musí trackovať source offset/generation a vedieť rozlíšiť complete prefix od hole. Cache key musí niesť immutable generation. `Projection healthy` bez source position a affected key scope nie je consistency evidence.

## 6. Connected incident `DB-PAY-59`

Control store commitol route generation `912` na quorum side. Region B počas partition-u používal member-local serializable read a cache `911`. etcd response obsahovala cluster ID, member ID, revision a Raft term, ale application tieto evidence nezapisovala a interný wrapper local read označoval ako `strong`.

Observed history pre merchant `M-8842`:

```text
18:02:11 write generation 912 completed v Region A
18:02:14 settlement S1 použil 912 / P2
18:02:17 status read ukázal 912
18:02:22 settlement S2 v Region B použil 911 / P1
```

History porušila linearizable current-route read, monotonic-read expectation session a business invariant, že po activation `912` nové settlements nesmú smerovať na `P1`.

Root cause bol neformálny `strong` label bez operation scope-u, named modelu a revision evidence. Route generation sa nepersistovala pri každom decision-e, session neniesla minimum revision, cache freshness nebola business signal a failover zmenil read source.

## 7. Redesign a acceptance paths

Provider route používa linearizable read s `required_generation`, response revision/term a persisted used generation. Dashboard môže používať bounded stale projection s `observed_generation`, `projected_at` a stale markerom, ale nemá authority nad external retryom. SDK prenáša minimum observed route revision. Projections trackujú source offset a missing prefix blokuje `current` verdict.

**Positive path** preukáže completed write nasledovaný current readom `>=` write revision a external effectom s persisted generation.

**Session path** prepne endpoint alebo Pod a stále zachová read-your-writes/monotonic minimum token, prípadne explicitne odmietne slabší result.

**Recovery path** počas replica lag/cache lossu použije authority alebo bounded stale result iba pre povolenú operation class; po convergence reconciliuje affected decisions.

**Forbidden path** odmietne non-monotonic `912 → 911`, stale authority pre side effect, lost event prefix, `strong` label bez evidence a conflict resolution, ktorá silentne zahodí non-mergeable update.

Acceptance zahŕňa concurrent clients, failover, replica read, cache loss, projection gap, retry bez/so session tokenom a partition heal.

## 8. Troubleshooting a anti-patterny

Diagnostika začína exact operation history, client/session identities a invocation/response times. Potom mapuje transaction/isolation scope, replica read mode, revision/term/offset/generation evidence, projections/caches, causal dependencies, conflict policy a external effect.

Najčastejšie anti-patterny sú nešpecifikované `strong`, eventual consistency považovaná za časový bound, serializability zamieňaná s linearizability, replica read označený iba za performance optimization, sticky session vydávaná za read-your-writes, timestamp vydávaný za causality a convergence považovaná za opravu side effects.

## 9. Kontrolné otázky

1. Čo je consistency model a ako sa testuje na history?
2. Ako sa líši od transaction isolation?
3. Čo garantuje linearizability?
4. Ako sa sequential consistency líši od real-time orderu?
5. Ako serializability a strict serializability súvisia?
6. Čo vyžaduje causal consistency?
7. Čo eventual consistency negarantuje?
8. Ako session token poskytuje monotonic reads?
9. Prečo end-to-end property môže byť slabšia než primary database?
10. Ktoré positive, session, recovery a forbidden paths musia prejsť?

## Glossary impact

Relevantné pojmy: consistency subject, operation history, linearizability, sequential consistency, serializability, strict serializability, causal consistency, eventual consistency, bounded staleness, read-your-writes, monotonic reads, monotonic writes, writes-follow-reads, consistent prefix, minimum observed revision, conflict resolution, read repair, anti-entropy a consistency acceptance verdict.

## Primárne zdroje

- [etcd API guarantees](https://etcd.io/docs/v3.7/learning/api_guarantees/)
- [etcd API — linearizable a serializable reads](https://etcd.io/docs/v3.6/learning/api/)
- [Jepsen — Consistency Models](https://jepsen.io/consistency/models)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CAP theorem](cap-theorem.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Leader election a consensus →](leader-election-and-consensus.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
