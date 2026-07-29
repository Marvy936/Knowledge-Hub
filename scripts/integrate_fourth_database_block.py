from pathlib import Path


def update_readme() -> None:
    path = Path("docs/15-databases-and-distributed-systems/README.md")
    text = path.read_text(encoding="utf-8")

    active_old = """12. [Caching](caching.md)

Aktuálny authoritative stav sekcie je **12/18 · In progress**."""
    active_new = """12. [Caching](caching.md)
13. [CAP theorem](cap-theorem.md)
14. [Consistency models](consistency-models.md)
15. [Leader election a consensus](leader-election-and-consensus.md)
16. [Retry, timeout a circuit breaker](retry-timeout-and-circuit-breaker.md)

Aktuálny authoritative stav sekcie je **16/18 · In progress**."""
    if active_old in text:
        text = text.replace(active_old, active_new, 1)

    planned_old = """13. CAP theorem
14. Consistency models
15. Leader election a consensus
16. Retry, timeout a circuit breaker
17. Rate limiting
18. Idempotency a backpressure"""
    planned_new = """17. Rate limiting
18. Idempotency a backpressure"""
    if planned_old in text:
        text = text.replace(planned_old, planned_new, 1)

    scenario_marker = "### `DB-PAY-59` — partition, consistency, consensus a resilience amplification"
    if scenario_marker not in text:
        scenario = """
### `DB-PAY-59` — partition, consistency, consensus a resilience amplification

Release `payments 8.3` presunul provider-route control a reconciliation leadership do päťčlenného consensus clusteru:

```text
Region A: 3 voting members
Region B: 2 voting members
quorum:   3
```

Provider `P1` začal prevažne timeoutovať. Majority Region A commitla route generation `912`, ktorá presmerovala new settlements na `P2`. Deväťminútový network partition oddelil Region B.

Region B nemohol získať linearizable current route bez quorum, ale application wrapper použil member-local serializable read a desaťminútovú cache generation `911`. Stale route preto autorizovala side-effecting provider attempts, hoci consensus cluster mal jednu správnu majority history.

```text
quorum commits route generation 912
→ minority Region B reads generation 911 locally
→ stale route used as current authority
→ provider P1 timeout
→ blind multi-layer retries
→ unknown outcomes a attempt amplification
```

Reconciliation scheduler používal etcd election lease `15 s`. Old leader epoch `51` po strate lease pokračoval ďalších `42 s`, pretože worker držal process-local `isLeader=true` a provider boundary nekontrolovala fencing epoch. Region A už pritom zvolil current leader epoch `52`.

Retry composition:

```text
merchant SDK:    1 + 2 retries
API gateway:     1 + 1 retry
provider client: 1 + 2 retries
maximum:         18 physical attempts / logical operation
```

Breaker bol local v každom zo `72` worker Podov, počítal iba HTTP `5xx` a ignoroval timeouts. Za deväť minút:

- `24 600` logical settlement operations vytvorilo `68 240` provider attempts (`2.77×` amplification);
- `3 842` Region B operations načítalo stale route generation `911`;
- `1 126` attempts smerovalo na `P1` po commitnutí generation `912`;
- `1 384` operations skončilo ako `sent-unknown`;
- `74` operations dostalo attempts z leader epochs `51` aj `52`;
- `27` duplicate physical provider attempts vyžadovalo reconciliation;
- provider idempotency zabránila duplicate financial effects.

Causal boundaries:

- **CAP root cause:** current-route operation nemala explicitný partition contract; minority availability bola použitá pre side effect vyžadujúci current authority.
- **Consistency root cause:** interné `strong` neznamenalo pomenovaný model, revision evidence ani minimum generation; history porušila linearizable a monotonic-read expectations.
- **Consensus/leadership root cause:** election fungovala správne, ale application leadership nebola priebežne guardovaná a external mutation nemala fencing token.
- **Resilience root cause:** timeouty, retries a breaker scopes nemali jeden logical-operation/deadline/retry-budget contract.
- **Amplifiers:** stale cache, 60-sekundový batch, per-Pod breaker, timeouty mimo failure countera, nested retries a shared resource pools.

Authoritative redesign:

```text
current provider-route side effect
→ linearizable read + minimum generation
→ settlement persists used revision/generation
→ quorum uncertainty = explicit refusal/defer

reconciliation worker
→ current election leader key
→ short bounded work unit
→ monotonically increasing fencing epoch
→ destination rejects stale epoch

provider execution
→ one retry owner
→ propagated deadline / async acceptance split
→ stable provider idempotency key
→ aggregate retry budget
→ provider+Region circuit breaker
→ provider lookup before unknown retry
```

Partition heal a recovery porovnávajú consensus revision/term, loaded route generations, leader epochs, logical operation/attempt trees a provider ledger. Replicas converging na majority history nie je closure, kým external attempts a unknown outcomes nie sú reconciled.

"""
        text = text.replace(
            "## Cieľ zvládnutia prvého bloku",
            scenario + "## Cieľ zvládnutia prvého bloku",
            1,
        )

    goals_marker = "## Cieľ zvládnutia štvrtého bloku"
    if goals_marker not in text:
        goals = """
## Cieľ zvládnutia štvrtého bloku

### CAP theorem

- používať presné definície consistency, availability a partition;
- odmietnuť slogan `pick two` a rozhodovať per operation;
- rozlíšiť quorum-side progress, minority refusal a mergeable local progress;
- definovať stale-read allowed use, generation bound a heal reconciliation;
- mapovať partition decision na business invariant a external effect.

### Consistency models

- rozlíšiť linearizable, sequential, serializable, strict-serializable, causal a eventual histories;
- oddeliť transaction isolation od distributed consistency;
- navrhnúť bounded staleness, read-your-writes a monotonic session guarantees;
- používať revision/generation tokens a explicitný conflict model;
- overiť replicas, projections, caches, failover a second-client histories.

### Leader election a consensus

- odvodiť quorum a failure tolerance z membershipu;
- rozlíšiť proposal, replicated, committed, applied a visible state;
- chápať term, election timeout, lease a membership reconfiguration;
- viazať application leadership na current leader key a fencing epoch;
- testovať stale leader, minority partition, process pause a second election.

### Retry, timeout a circuit breaker

- rozlíšiť deadline, attempt timeout, failure a unknown outcome;
- určiť jedného retry ownera a stable operation/attempt identity;
- používať remaining budget, aggregate retry budget, backoff a jitter;
- navrhovať breaker scope/signals a bounded Half-Open probes;
- overiť retry storm, lost response, recovery a duplicate-effect forbidden outcome.

"""
        text = text.replace("## Dominantný model sekcie", goals + "## Dominantný model sekcie", 1)

    text = text.replace(
        "→ concurrency, replication, delivery, routing a coherence mechanisms",
        "→ concurrency, replication, partition, consistency, consensus, delivery, routing, cache a resilience mechanisms",
        1,
    )
    text = text.replace(
        "→ bounded write/read/route/retry/recovery decision",
        "→ bounded write/read/partition/leadership/route/retry/recovery decision",
        1,
    )

    marker = "- cache hit/miss od freshness a business existence;"
    expanded = """- cache hit/miss od freshness a business existence;
- quorum/current authority od member-local alebo cached state;
- consensus leader od process-local leadership a fenced mutation;
- deadline/timeout od failure a unknown outcome;
- logical operation od nested physical retry tree a aggregate budget;"""
    if marker in text and "- quorum/current authority od member-local" not in text:
        text = text.replace(marker, expanded, 1)

    replacements = {
        "| CAP theorem | Not Started | L0 |": "| CAP theorem | Learning | L2 |",
        "| Consistency models | Not Started | L0 |": "| Consistency models | Learning | L2 |",
        "| Leader election a consensus | Not Started | L0 |": "| Leader election a consensus | Learning | L2 |",
        "| Retry, timeout a circuit breaker | Not Started | L0 |": "| Retry, timeout a circuit breaker | Learning | L2 |",
    }
    for old, new in replacements.items():
        text = text.replace(old, new, 1)

    path.write_text(text, encoding="utf-8")


def update_ledger() -> None:
    path = Path("DOCUMENTATION-REVIEW-STATUS.md")
    text = path.read_text(encoding="utf-8")
    prefix = "| `15-databases-and-distributed-systems` — Databases and Distributed Systems |"
    new_row = "| `15-databases-and-distributed-systems` — Databases and Distributed Systems | 16/18 authoritative drafting | In progress | 2026-07-29 | Sekcia má šestnásť authoritative kapitol a štyri connected incidenty. `DB-PAY-56` pokrýva data-model authority, ACID transaction boundary, indexed migration a replication/HA; `DB-PAY-57` recovery/PITR, pooling, product roles a architecture boundaries; `DB-PAY-58` synchronous/asynchronous communication, durable messaging, route/discovery generations a cache coherence. Štvrtý blok `DB-PAY-59` oddeľuje CAP partition decision, consistency history, consensus leadership a resilience amplification. Päťčlenný consensus cluster sa rozdelil na quorum `3` a minority `2`; majority commitla provider-route generation `912`, zatiaľ čo Region B použil member-local serializable read/cache generation `911` pre side-effecting operation. etcd election správne zvolila epoch `52`, no old worker epoch `51` pokračoval 42 sekúnd bez destination fencing. Nested SDK/gateway/provider retries mali teoretické maximum 18 attempts; 72 Pod-local breakers ignorovalo timeouty, takže `24 600` logical operations vytvorilo `68 240` provider attempts (`2.77×`), `1 384` sent-unknown outcomes a `27` duplicate physical attempts, pri nulových duplicate financial effects vďaka provider idempotency. Redesign používa per-operation partition contracts, linearizable minimum-generation reads pre side effects, revision/session evidence, quorum-safe consensus, lease-loss cancellation, monotonic fencing epochs, one retry owner, propagated deadlines, aggregate retry budget, provider+Region breaker a provider lookup pred unknown retryom. Section README je `16/18 · In progress`, roadmap a navigation vedú cez CAP, consistency, leader election/consensus a retry/timeout/circuit breaker, glossary fragments `15a`–`15d` sú synchronizované a audit-failure artifacts sú prázdne. Zostávajú `Rate limiting`, `Idempotency a backpressure` a finálny section-level pass. |"

    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            lines[index] = new_row
            break
    else:
        insert_at = next(
            (i for i, line in enumerate(lines) if line.startswith("## Section-level completion criteria")),
            len(lines),
        )
        lines.insert(insert_at, new_row)
        lines.insert(insert_at + 1, "")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    update_readme()
    update_ledger()
