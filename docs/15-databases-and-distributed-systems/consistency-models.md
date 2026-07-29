# Consistency models

Consistency model je contract nad tým, ktoré histories operations systém povoľuje. Nehovorí iba, či sa replicas „nakoniec zosúladia“. Určuje, čo môže konkrétny client pozorovať po writes, pri concurrency, počas partition-u, po failover-e a medzi viacerými objects alebo services.

Správny návrh začína operation history a business invariantom, nie názvom databázy alebo marketingovým slovom `strong`.

## 1. Dominantný model

```text
business invariant a user expectation
→ exact objects/operations/clients
→ real-time, program a causal order
→ required visibility a transaction scope
→ consistency model
→ implementation/read-write mechanism
→ observed history
→ allowed/forbidden outcome verdict
→ reconciliation alebo stronger-control decision
→ second-client/failover validation
```

Consistency sa overuje na histories, nie na jednom úspešnom requeste.

## 2. Consistency model vs. database isolation

Tieto oblasti sa prekrývajú, ale nie sú totožné.

### Transaction isolation

Rieši concurrent transactions nad datastore-om:

- read committed;
- repeatable read;
- snapshot isolation;
- serializable;
- strict serializable.

### Distributed consistency

Rieši pozorovanie operations medzi replicas, clients a časom:

- linearizable;
- sequential;
- causal;
- eventual;
- bounded staleness;
- session guarantees;
- consistent prefix.

Database môže napríklad poskytovať serializable local transactions, ale stale replicated reads. Alebo linearizable single-key operations bez multi-key serializable transaction.

## 3. Exact consistency subject

Pred výberom modelu treba pomenovať:

- objects alebo key range;
- single operation vs. transaction;
- participating clients/sessions;
- primary/replica/cache path;
- real-time requirement;
- causal dependencies;
- conflict model;
- failure a partition scenario;
- acknowledgement boundary;
- external side effects.

```text
„route config je strongly consistent“
```

je slabé tvrdenie.

Presnejšie:

```text
completed route-generation write
→ všetky neskoršie provider-selection reads
→ musia vidieť rovnakú alebo novšiu generation
→ pred vykonaním external effectu
```

## 4. Linearizability

Linearizability vyžaduje, aby každá operation vyzerala, že nastala atomicky v jednom bode medzi invocation a response, a rešpektovala real-time order non-overlapping operations.

```text
write 912 completes
→ read starts later
→ read nesmie vrátiť 911
```

Je vhodná pre:

- current leader/ownership;
- lock a lease state;
- idempotency create-if-absent;
- account balance invariant;
- current security/revocation state;
- provider route autorizujúci side effect.

Cena môže zahŕňať quorum latency a refusal počas partition-u.

## 5. Sequential consistency

Sequential consistency povoľuje jedno globálne usporiadanie operations, ktoré rešpektuje program order každého clienta, ale nemusí rešpektovať real-time order medzi clients.

Client A môže dokončiť write skôr, než Client B začne read, no history môže stále umiestniť B read pred A write, ak zachová per-client order.

Pre user-facing „po dokončení zmeny ju každý nový request vidí“ je sequential consistency často príliš slabá.

## 6. Serializability a strict serializability

### Serializability

Multi-operation transactions sa správajú ako nejaké serial order. Nemusí rešpektovať wall-clock real-time order.

### Strict serializability

Spája serializability s real-time order podobným linearizability.

```text
transaction T1 dokončí route + policy change
→ T2 začne neskôr
→ T2 musí byť usporiadaná po T1
```

Strict serializability je silný end-to-end database contract, ale stále nepokrýva arbitrary external provider call mimo transaction-u.

## 7. Causal consistency

Ak operation B kauzálne závisí od A, každý observer musí vidieť A pred B.

Príklad:

```text
policy generation 912 published
→ settlement created using generation 912
```

Observer nesmie vidieť settlement referencing generation `912` bez možnosti vidieť príslušnú policy.

Causal consistency nemusí globálne usporiadať concurrent unrelated operations.

Potrebuje causal metadata alebo session/context propagation. Timestamp bez causal modelu nestačí.

## 8. Eventual consistency

Eventual consistency zvyčajne znamená, že ak neprichádzajú nové updates a komunikácia funguje, replicas sa nakoniec zblížia.

Neurčuje automaticky:

- maximálnu staleness;
- monotonic reads;
- read-your-writes;
- conflict winnera;
- ordering;
- converged value correctness;
- správanie počas continuous writes;
- external effects vykonané zo stale state-u.

„Eventual“ bez convergence, conflict a allowed-use contractu je nedostatočné.

## 9. Bounded staleness

Bounded staleness povoľuje stale reads, ale s explicitnou hranicou:

- časová age;
- revision/sequence lag;
- počet versions;
- event backlog age;
- business generation gap.

```text
observed_generation >= required_generation
```

je často bezpečnejšie než samotné `age < 30 s`, pretože wall-clock vek nemusí korešpondovať s business updates.

## 10. Session guarantees

Slabšie globally consistent systémy môžu poskytovať užitočné per-session properties.

### Read-your-writes

Po vlastnom úspešnom write client uvidí tento write alebo novší state.

### Monotonic reads

Session neuvidí staršiu version po tom, čo už videla novšiu.

### Monotonic writes

Writes jedného clienta sa aplikujú v jeho program order.

### Writes-follow-reads

Write je usporiadaný po state-e, ktorý client predtým čítal.

Session guarantee vyžaduje session identity, version token alebo sticky/causal context. Load balancer affinity sama osebe nie je formálny proof.

## 11. Consistent prefix

Reads pozorujú prefix committed orderu, nie arbitrary reorder alebo holes.

```text
event 100
→ event 101
→ event 102
```

Client môže vidieť iba po `101`, ale nemá vidieť `102` bez `101`, ak model garantuje consistent prefix pre daný stream.

To je dôležité pre event projections, schema changes a dependent state transitions.

## 12. Stale reads a side effects

Read model sa musí hodnotiť podľa toho, čo read autorizuje.

| Read | Možný slabší model |
|---|---|
| historical report | eventual alebo bounded stale |
| merchant dashboard | bounded stale + marker |
| current provider selection | linearizable alebo minimum generation |
| permission revocation | current authority/short-bound session |
| dedupe existence pred external call | linearizable create-if-absent alebo authority lookup |

Read-only API môže byť correctness-critical, ak jeho result riadi write alebo external effect.

## 13. Replica, cache a projection consistency

End-to-end visible consistency je minimum cez všetky layers:

```text
authoritative database
→ replication
→ CDC/event delivery
→ projection apply
→ cache fill/invalidation
→ gateway/client cache
→ user observation
```

Silná primary database consistency sa môže stratiť cez:

- async replica;
- out-of-order events;
- skipped consumer offset;
- stale cache;
- mixed deployment generation;
- client-side reuse;
- retry na inom endpoint-e.

## 14. Version a evidence tokens

Consistency contract sa lepšie overuje, keď response obsahuje:

- datastore revision;
- commit sequence;
- event offset;
- policy generation;
- ETag/version;
- leader term/epoch;
- observed-at timestamp;
- stale/fresh verdict.

Client potom môže definovať:

```text
minimum_revision = 18420
→ read with observed_revision 18418 rejected
```

Bez tokenov sa „fresh“ často iba predpokladá.

## 15. Read repair a anti-entropy

Availability-oriented systems môžu convergence dosahovať cez:

- read repair;
- hinted handoff;
- anti-entropy/Merkle comparison;
- background reconciliation;
- last-write-wins;
- vector/causal clocks;
- CRDT merge.

Tieto mechanisms riešia replica convergence, nie automaticky external side effects vykonané z nesprávnej version.

## 16. Conflict resolution

Conflict policy musí byť domain-specific.

### Last-write-wins

Jednoduché, ale clock/order policy môže zahodiť legitimate concurrent update.

### Application merge

Business pravidlá rozhodnú, či operations možno spojiť.

### Reject/manual resolution

Bezpečné pre non-mergeable high-value invariants.

### CRDT

Data type a operations sú navrhnuté tak, aby replicas deterministicky konvergovali bez central coordination. Nie každá business operation má vhodnú CRDT reprezentáciu.

## 17. Connected incident `DB-PAY-59`

Control store commitol route generation `912` na quorum side. Region B počas partition-u používal member-local serializable read a cache generation `911`.

etcd response model umožňoval rozlíšiť:

```text
cluster_id
member_id
revision
raft_term
```

Application však:

- neukladala observed revision pri route decision-e;
- nepřenášala minimum acceptable generation;
- označovala local read ako `strong` v internom wrapperi;
- po failover-e dovolila jednej session vidieť `912` a neskôr `911` cez iný Pod;
- používala stale route na provider side effect.

Observed history pre merchant `M-8842`:

```text
18:02:11 route write generation 912 completed v quorum Regione A
18:02:14 settlement S1 v Region A použil 912 / P2
18:02:17 merchant status read ukázal current route 912
18:02:22 settlement S2 v Region B použil 911 / P1
```

Táto history porušila:

- linearizable current-route read;
- monotonic-read expectation pre merchant session;
- business rule „po activation generation 912 sa nové settlements nesmú poslať na P1“.

## 18. Consistency root cause

Primary root cause bol:

> Interný `strong` contract nebol mapovaný na konkrétny consistency model, operation scope ani revision evidence; member-local stale read a cache boli preto použité ako current authority.

Amplifiers:

- route generation nebola persisted na všetkých decisions;
- client session neniesla minimum observed revision;
- projection/cache freshness nebola business signal;
- endpoint failover zmenil read source;
- retries vytvárali ďalšie reads bez session contextu.

## 19. Evidence-preserving containment

```text
freeze routing mutations
→ preserve etcd terms/revisions a response headers
→ preserve per-request observed generation/read source
→ stop side effects bez current minimum generation
→ route authority reads na linearizable path
→ classify stale-read-generated provider attempts
→ reconcile provider outcomes
→ invalidate/retire stale loaded generations
```

## 20. Authoritative redesign

### Provider route

```text
linearizable read
+ required_generation
+ response revision/term
+ settlement persists used generation
```

### Merchant status/dashboard

```text
bounded stale projection allowed
+ observed_generation
+ projected_at
+ stale marker
+ no authority over external retry
```

### Session guarantees

Client/SDK prenáša:

```text
minimum_observed_route_revision
```

Subsequent reads musia vrátiť rovnakú alebo novšiu revision, alebo explicitne zlyhať/degradovať.

### Event projections

- partition key drží per-operation order;
- projection tracks source offset;
- missing prefix blokuje `current` verdict;
- cache key obsahuje immutable generation;
- reconciliation porovná authority, projection a external provider state.

## 21. Consistency acceptance verdict

Consistency design je prijatý, keď:

- exact objects, operations, clients a transaction scope sú explicitné;
- model je pomenovaný formálne, nie ako `strong` alebo `eventual` bez definície;
- real-time, program a causal order requirements sú uvedené;
- database isolation a distributed consistency sú rozlíšené;
- read/write paths vrátane replicas, projections a caches sú v scope;
- acknowledgement a visibility boundary sú explicitné;
- stale reads majú age/revision/generation bound a allowed-use contract;
- session guarantees majú identity a token propagation;
- conflicts majú deterministic merge/reject/manual policy;
- external side effects nepoužívajú slabší state než povoľuje invariant;
- response nesie evidence potrebné na overenie freshness/orderu;
- failover, retry, cache loss, concurrent clients a partition tests prejdú;
- forbidden non-monotonic, stale-authority, lost-prefix a divergent outcomes sú odmietnuté.

## 22. Troubleshooting flow

```text
stale/non-monotonic/divergent observation
→ exact operation history
→ client/session identities
→ invocation/response a real-time order
→ datastore transaction/isolation scope
→ replica/read consistency mode
→ revision/term/offset/generation evidence
→ projection/cache/client layers
→ causal/program dependencies
→ conflict/merge behavior
→ business/external effect
→ second-client/failover validation
```

## 23. Anti-patterny

### Strong consistency

Bez pomenovania modelu, scope-u a failure behavioru je tvrdenie neoveriteľné.

### Eventual consistency znamená niekoľko sekúnd

Eventual model sám o sebe neurčuje časový bound.

### Serializable = linearizable

Serializable transaction history nemusí rešpektovať real-time order; strict serializability ho zahŕňa.

### Replica read je iba performance optimization

Môže zmeniť authorization, routing, dedupe alebo user-visible monotonicity.

### Sticky session garantuje read-your-writes

Failover, replica lag, cache a process restart môžu guarantee porušiť bez version contextu.

### Timestamp vyrieši causality

Clock timestamp nemusí zachytiť causal dependency ani byť spoľahlivo usporiadaný.

### Convergence opraví external effects

Replica state môže konvergovať, no nesprávne provider calls zostávajú.

## 24. Kontrolné otázky

1. Čo je consistency model?
2. Ako sa líši od transaction isolation?
3. Čo garantuje linearizability?
4. Ako sa sequential consistency líši od linearizability?
5. Ako serializability a strict serializability súvisia?
6. Čo vyžaduje causal consistency?
7. Čo eventual consistency negarantuje?
8. Aké session guarantees poznáme?
9. Kedy je bounded staleness bezpečná?
10. Ktoré models porušilo `DB-PAY-59`?
11. Ako revision token pomáha klientovi?
12. Čo overuje consistency acceptance verdict?

## Glossary impact

Relevantné pojmy: consistency subject, operation history, linearizability, sequential consistency, serializability, strict serializability, causal consistency, eventual consistency, bounded staleness, read-your-writes, monotonic reads, monotonic writes, writes-follow-reads, consistent prefix, minimum observed revision, conflict resolution, read repair, anti-entropy a consistency acceptance verdict.

## Primárne zdroje

- [etcd API guarantees](https://etcd.io/docs/v3.7/learning/api_guarantees/)
- [etcd API — linearizable a serializable reads](https://etcd.io/docs/v3.6/learning/api/)
- [Jepsen — Consistency Models](https://jepsen.io/consistency/models)
