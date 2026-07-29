# Databases and Distributed Systems — CAP, consistency, consensus a resilience lifecycles

## CAP subject

Exact replicated data, operations, clients, topology, partition scenario, consistency definition, availability contract a business invariant analyzované CAP rozhodnutím. Pozri [CAP theorem](../docs/15-databases-and-distributed-systems/cap-theorem.md).

## Atomic consistency — CAP

Single-copy property používaná v CAP formalizácii, pri ktorej operation vyzerá, že nastala atomicky medzi invocation a response a neskoršie non-overlapping operations rešpektujú jej dokončenie. Pozri [CAP theorem](../docs/15-databases-and-distributed-systems/cap-theorem.md).

## CAP availability

Liveness property, podľa ktorej každý request prijatý non-failed node-om nakoniec dostane response; nejde o percentuálne SLO. Pozri [CAP theorem](../docs/15-databases-and-distributed-systems/cap-theorem.md).

## Network partition

Stav, v ktorom sa distributed participants nemôžu spoľahlivo navzájom dorozumieť, hoci niektoré nodes a links môžu zostať funkčné. Pozri [CAP theorem](../docs/15-databases-and-distributed-systems/cap-theorem.md).

## Per-operation partition contract

Explicitné rozhodnutie, či konkrétna read alebo write operation počas partition-u odmietne, čaká, používa stale/local state alebo prijme mergeable local progress. Pozri [CAP theorem](../docs/15-databases-and-distributed-systems/cap-theorem.md).

## Quorum side

Partition cohort obsahujúci dostatočný počet voting members na vytvorenie majority a commitovanie consensus decisions. Pozri [CAP theorem](../docs/15-databases-and-distributed-systems/cap-theorem.md).

## Minority side

Partition cohort bez majority quorum, ktorá nemôže bezpečne commitovať nové consensus decisions a musí odmietnuť, čakať alebo používať explicitne slabší local contract. Pozri [CAP theorem](../docs/15-databases-and-distributed-systems/cap-theorem.md).

## Partition refusal

Consistency-preserving outcome, pri ktorom operation bez required quorum alebo current authority nedostane success acknowledgement. Pozri [CAP theorem](../docs/15-databases-and-distributed-systems/cap-theorem.md).

## Partition-local progress

Availability-preserving local operation počas partition-u, ktorá potrebuje explicitný conflict, merge a heal-time reconciliation model. Pozri [CAP theorem](../docs/15-databases-and-distributed-systems/cap-theorem.md).

## Partition-heal reconciliation

Proces po obnovení connectivity, ktorý porovná committed histories, local attempts, caches, sessions, retries a external effects a obnoví authoritative business outcome. Pozri [CAP theorem](../docs/15-databases-and-distributed-systems/cap-theorem.md).

## Stale-authority read

Read zo starej replica/cache generation použitý na authorization, routing, dedupe alebo external side effect, hoci operation vyžaduje current authority. Pozri [CAP theorem](../docs/15-databases-and-distributed-systems/cap-theorem.md).

## Minimum acceptable generation

Najnižšia revision alebo business generation, ktorú musí read vrátiť, aby ju caller mohol bezpečne použiť. Pozri [CAP theorem](../docs/15-databases-and-distributed-systems/cap-theorem.md).

## PACELC question

Doplnková design otázka: počas partition-u consistency vs. availability; mimo partition-u latency vs. consistency. Pozri [CAP theorem](../docs/15-databases-and-distributed-systems/cap-theorem.md).

## CAP acceptance verdict

Dôkaz, že per-operation partition behavior, quorum/minority semantics, stale-read limits, acknowledgement, conflict handling, heal reconciliation a second-partition tests chránia required business invariant. Pozri [CAP theorem](../docs/15-databases-and-distributed-systems/cap-theorem.md).

## Consistency subject

Exact objects, operations, clients/sessions, transaction scope, replica/cache paths, ordering requirements, failure scenarios a external effects analyzované consistency modelom. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Operation history

Usporiadaný záznam invocation a response events reads, writes a transactions používaný na overenie, či execution spĺňa consistency model. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Linearizability

Single-object consistency model, v ktorom každá operation vyzerá, že nastala atomicky medzi invocation a response a rešpektuje real-time order non-overlapping operations. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Sequential consistency

Model s jedným globálnym orderom rešpektujúcim program order každého clienta, ale nie nutne real-time order medzi clients. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Serializability

Transaction property, pri ktorej outcome concurrent transactions zodpovedá nejakému serial orderu, ktorý nemusí rešpektovať wall-clock order. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Strict serializability

Kombinácia serializability a real-time orderu, takže neskôr začatá transaction musí byť usporiadaná po už dokončenej transaction. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Causal consistency

Model, v ktorom všetci observers vidia kauzálne závislé operations v správnom poradí, hoci concurrent unrelated operations nemusia mať jeden global order. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Eventual consistency

Convergence property, podľa ktorej replicas bez nových updates a pri funkčnej komunikácii nakoniec dosiahnu rovnaký state; sama neurčuje časový bound ani session guarantees. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Bounded staleness

Read contract povoľujúci starší state iba v explicitnej časovej, revision, sequence alebo business-generation hranici. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Read-your-writes

Session guarantee, podľa ktorej client po vlastnom úspešnom write uvidí tento write alebo novší state. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Monotonic reads

Session guarantee zakazujúca, aby client po pozorovaní novšej version neskôr videl staršiu version. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Monotonic writes

Session guarantee, podľa ktorej writes jedného clienta nadobúdajú účinok v jeho program order. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Writes-follow-reads

Session guarantee, podľa ktorej client write nasleduje po state-e, ktorý client predtým čítal, a zachováva causal dependency. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Consistent prefix

Property, pri ktorej client môže pozorovať iba prefix ordered history a nie neskorší event bez jeho required predecessors. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Minimum observed revision

Version token prenášaný session/clientom, ktorý vyžaduje, aby ďalšie reads nevrátili starší state. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Conflict resolution

Domain-specific policy pre concurrent/divergent updates, napríklad deterministic merge, CRDT, last-write-wins, rejection alebo manual resolution. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Read repair

Mechanizmus, ktorý pri read-e porovná replicas a opraví stale copy podľa authoritative/conflict policy. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Anti-entropy

Background replica reconciliation, ktorá porovnáva state alebo summaries a opravuje divergence. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Consistency acceptance verdict

Dôkaz, že exact operation histories, real-time/program/causal orders, replicas, sessions, conflicts, caches, failover a external side effects spĺňajú pomenovaný consistency model. Pozri [Consistency models](../docs/15-databases-and-distributed-systems/consistency-models.md).

## Consensus subject

Exact coordination invariant, members, failure domains, quorum, terms, log, read/write paths, leases, fencing a external mutation scope chránený consensus návrhom. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Leader election

Protocol na výber dočasného coordinatora alebo writera; sám osebe negarantuje safe external side effects po strate leadership. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Consensus

Protocol, ktorým distributed participants vytvoria jednu usporiadanú committed history rozhodnutí napriek failures v podporovanom modeli. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Voting member

Consensus cluster member, ktorého vote sa počíta do quorum a ktorý participuje na commit decisions. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Learner member

Non-voting member dobiehajúci replicated state pred safe promotion na voting member. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Majority quorum

Najmenšia majority voting members potrebná na election a commit, typicky `floor(N/2)+1`. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Consensus term

Monotonically increasing election epoch, ktorá oddeľuje leadership generations a pomáha odmietnuť stale leaders/messages. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Replicated log

Ordered sequence consensus proposals replikovaná members a applied deterministic state machines. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Consensus proposal

Candidate log entry pred rozhodnutím, či ju quorum commitne. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Commit index

Najvyšší log position, o ktorom cluster rozhodol, že je committed podľa consensus protocolu. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Applied index

Najvyšší committed log position už vykonaný lokálnou state machine; môže krátko zaostávať za commit indexom. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Election timeout

Časová failure-detector hranica, po ktorej follower bez heartbeat-u začne election; nie je dôkazom leader crashu. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Leader lease

Časovo obmedzené coordination ownership viazané na authoritative renew/expiry semantics. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Leader key

Consensus-backed identity leadership generation, ktorú možno použiť na transactional guard, observation a resignation. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Fencing token

Monotonically increasing authority epoch, ktorý destination porovná s posledným accepted tokenom a odmietne stale writera. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Stale leader

Process, ktorý stratil current consensus leadership alebo lease, ale stále sa pokúša vykonávať work. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Application split brain

Concurrent application execution viacerých actorov, hoci underlying consensus cluster uznáva iba jedného leadera; typicky vzniká chýbajúcim fencingom. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Quorum-safe reconfiguration

Sequential membership change, ktorý zachováva available majority a overí synchronizáciu nového membera pred ďalšou zmenou. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Consensus acceptance verdict

Dôkaz, že membership, quorum, terms, commit/apply, reads, leases, fencing, reconfiguration, external outcomes a second-election tests zabraňujú stale alebo dual authority. Pozri [Leader election a consensus](../docs/15-databases-and-distributed-systems/leader-election-and-consensus.md).

## Resilience subject

Exact logical operation, physical attempts, dependency/failure domain, deadline, retry/circuit policies, queues, pools, identities a business outcome analyzované resilience návrhom. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## End-to-end deadline

Najneskorší čas, po ktorom caller už result nepotrebuje alebo ho nemôže bezpečne použiť; downstream stages musia dostať remaining budget. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Remaining deadline budget

Čas zostávajúci z pôvodného end-to-end deadline-u po odpočítaní už spotrebovaného processingu a queueing-u. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Attempt timeout

Maximálna duration jedného physical dependency attemptu; jeho prekročenie nemusí znamenať, že effect nenastal. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Unknown timeout outcome

Timeout state, pri ktorom caller nevie, či request nebol spracovaný, commitol alebo vykonal external effect. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Retry eligibility

Explicitný verdict, či failure class, remaining deadline, idempotency, capacity a business semantics povoľujú ďalší attempt. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Retry owner

Jediná primary vrstva zodpovedná za retries konkrétnej dependency boundary, aby sa attempts nenásobili medzi SDK, gateway, service, mesh a driver. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Retry multiplication

Násobenie physical attempts pri nested retry policies, napríklad `3 × 2 × 3 = 18` attempts pre jeden logical request. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Retry budget

Aggregate limit retry attempts pre service/dependency/cohort v časovom intervale, ktorý chráni capacity nad rámec per-request limitu. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Exponential backoff

Retry schedule s rastúcimi intervalmi medzi attempts, ktorý znižuje pressure na recovering dependency. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Retry jitter

Randomizácia retry delay-u, ktorá zabraňuje synchronized waves medzi mnohými clients. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Hedged request

Dodatočný concurrent attempt spustený pre zníženie tail latency; bezpečný iba pri idempotentnom/deduplicated a capacity-bounded worku. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Circuit breaker

State machine, ktorá po evidence pretrvávajúceho dependency failure-u dočasne odmieta nové calls a neskôr povoľuje bounded recovery probes. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Circuit Closed state

Breaker state, v ktorom requests prechádzajú a rolling observations rozhodujú o prípadnom otvorení. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Circuit Open state

Breaker state, v ktorom requests failnú alebo použijú truthful degraded path bez dependency callu. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Circuit Half-Open state

Recovery state povoľujúci malý počet probes na overenie, či dependency unesie návrat trafficu. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Breaker scope

Failure-domain key breaker state-u, napríklad provider, Region, shard, tenant alebo operation type. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Breaker signal

Observation použitý na transition breaker state-u, napríklad timeout, connect failure, `5xx`, latency, saturation, throttling alebo unknown-outcome rate. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Recovery probe

Bounded representative request povolený v Half-Open state-e na overenie dependency recovery bez vypustenia celého backlogu. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Graceful degradation

Truthful reduced capability, stale-marked response, durable defer alebo explicitná unavailability použitá namiesto false success pri dependency failure. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Dependency bulkhead

Oddelený capacity pool pre dependency alebo workload, ktorý bráni tomu, aby jeho waits/retries vyčerpali resources ostatných paths. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).

## Retry/timeout/circuit-breaker acceptance verdict

Dôkaz, že deadline propagation, failure classification, stable identity, retry ownership/budgets, breaker scope/signals, bulkheads, unknown reconciliation a recovery tests nevytvárajú storm ani duplicate effect. Pozri [Retry, timeout a circuit breaker](../docs/15-databases-and-distributed-systems/retry-timeout-and-circuit-breaker.md).
