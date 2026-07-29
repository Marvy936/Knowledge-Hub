from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        if new in text:
            return text
        raise RuntimeError(f"Missing expected marker for {label}")
    return text.replace(old, new, 1)


readme_path = Path("docs/15-databases-and-distributed-systems/README.md")
text = readme_path.read_text(encoding="utf-8")

text = replace_once(
    text,
    """16. [Retry, timeout a circuit breaker](retry-timeout-and-circuit-breaker.md)

Aktuálny authoritative stav sekcie je **16/18 · In progress**.""",
    """16. [Retry, timeout a circuit breaker](retry-timeout-and-circuit-breaker.md)
17. [Rate limiting](rate-limiting.md)
18. [Idempotency a backpressure](idempotency-and-backpressure.md)

Aktuálny authoritative stav sekcie je **18/18 · Ready for user review**.""",
    "active chapter list",
)

text = replace_once(
    text,
    """## Plánované pokračovanie

Authoritative poradie bude pokračovať bez zmeny roadmapy:

17. Rate limiting
18. Idempotency a backpressure""",
    """## Completion state

Všetkých 18 authoritative kapitol je vytvorených. Sekcia prešla finálnym section-level consistency gate-om a je pripravená na používateľskú kontrolu; nie je tým automaticky používateľsky schválená, Accepted, Verified ani Stable.""",
    "planned continuation",
)

scenario_marker = "### `DB-PAY-60` — fair admission, stable operation identity a bounded flow"
if scenario_marker not in text:
    scenario = r'''
### `DB-PAY-60` — fair admission, stable operation identity a bounded flow

Release `payments 8.4` otvoril partnerom bulk replay po 47-minútovom provider outage-i. Gateway fleet mal `80` Podov a každý Pod vlastný token bucket:

```text
sustained per Pod:       450 requests/s
burst per Pod:           900 requests
fleet sustained:         36 000 requests/s
fleet immediate burst:   72 000 requests
```

Safe downstream envelope providera P2 bol približne `6 500 attempts/s` a `1 200` in-flight attempts. Limiter počítal raw HTTP attempts, nemal global/provider/tenant hierarchy a nerozlišoval expensive create od status alebo reconciliation requestu.

Počas 14 minút:

- partner replay dosiahol `21 600 requests/s` pri približne `3 200 requests/s` normal trafficu;
- gateway prijala `6.9 milióna` requests;
- jeden partner spotreboval `71 %` admitted create capacity;
- `429` responses nemali `Retry-After` a SDK retryovala po fixných `100 ms`;
- HTTP-attempt amplification dosiahla `2.4×`;
- oldest provider command dosiahol age `54 minút`.

Idempotency registry bola mimo authoritative settlement transaction:

```text
SELECT key
→ generate new operation_id
→ commit settlement + outbox
→ autocommit key mapping
```

Key nemal semantic payload fingerprint, cleanup ho mazal `20 minút` po `first_seen` aj pri non-terminal operation a provider key sa odvodzoval z internal `operation_id`.

Dôsledky:

- `12 480` duplicate submissions použilo rovnaké business operation IDs;
- `1 906` retries prišlo po registry expiry;
- `143` concurrent duplicate pairs prešlo check-before-insert race-om;
- vzniklo `83` duplicate authoritative operations;
- provider potvrdil `31` duplicate effects;
- `29` effects bolo automaticky reversed a `2` vyžadovali manuálnu remediation.

Provider fleet mal `48` worker Podov, každý s async limitom `2 000`, teda theoretical fleet in-flight `96 000`. Kafka consumer polloval do prakticky unbounded executor queue a partitions pause-ol až pri heap utilization nad `85 %`; po rebalance sa pause state neobnovil.

```text
Kafka backlog:              2.7 milióna commands
oldest command:             54 minút
queued executor tasks:      približne 348 000
worker OOM kills:           17
provider-pool wait p99:     11.2 s
safe provider in-flight:    1 200
```

Causal boundaries:

- **Rate-limiting root cause:** process-local request counter bez fleet, tenant, operation-cost a downstream-provider envelope-u.
- **Idempotency root cause:** claim nebol atomic s authoritative operation, nemal semantic fingerprint a expiroval pred terminal/reconciliation lifecycle-om.
- **Backpressure root cause:** API admission, consumer polling a executor submission neboli riadené downstream completion credits; buffers a in-flight concurrency boli rádovo väčšie než safe envelope.
- **Amplifiers:** autoscale, fixed-delay client retry, shared create/status budget, short key retention, provider key podľa attempt-derived operation ID, rebalance pause loss a immediate retry flow.

Authoritative redesign:

```text
global/provider/tenant/operation-class admission
→ provider P2 rate 5 800/s + hard in-flight 1 200
→ reserved status/cancellation/reconciliation capacity
→ atomic PostgreSQL idempotency claim + settlement + outbox
→ semantic fingerprint a stable business/provider identity
→ durable status/result reuse for duplicate requests
→ bounded consumer credits, poll a executor queues
→ pause/resume re-derived after rebalance
→ backlog-age-driven admission and delayed retry
→ provider lookup/reconciliation before unknown retry
→ bounded drain and second-overload validation
```

Final recovery vytvorila operation-equivalence groups podľa tenant, business operation ID a semantic payloadu, porovnala ich s provider ledgerom, zastavila duplicate attempts, vykonala reversals a drainovala oldest safe work pod hard provider credits. Pokles queue depth nebol považovaný za closure bez final business reconciliation.
'''.strip()
    text = text.replace(
        "## Cieľ zvládnutia prvého bloku",
        scenario + "\n\n## Cieľ zvládnutia prvého bloku",
        1,
    )

fifth_marker = "## Cieľ zvládnutia piateho bloku"
if fifth_marker not in text:
    fifth = r'''
## Cieľ zvládnutia piateho bloku

### Rate limiting

- definovať exact admission subject, key, units, cost, scope a generation;
- rozlíšiť rate, quota, concurrency, burst a downstream capacity envelope;
- vysvetliť fixed/sliding windows, token/leaky bucket a distributed counters;
- odvodiť hierarchical global/provider/tenant/operation-class fairness;
- vytvoriť truthful `429`, `Retry-After`, priority a recovery-reserve contract;
- overiť autoscale, one-tenant flood, burst, counter failure a retry storm.

### Idempotency a backpressure

- definovať key scope, semantic fingerprint a atomic claim;
- modelovať accepted, processing, completed, failed-final a reconciliation-required states;
- zachovať stable operation identity cez outbox, broker, consumer a provider;
- odvodiť retention z retry, backlog, replay a reconciliation window-u;
- inventarizovať a hard-boundovať queues, buffers, pools a in-flight work;
- prenášať downstream credits cez poll/pause/executor/admission boundaries;
- overiť concurrent duplicate, lost response, rebalance, sustained overload a bounded drain.
'''.strip()
    text = text.replace(
        "## Dominantný model sekcie",
        fifth + "\n\n## Dominantný model sekcie",
        1,
    )

text = replace_once(
    text,
    "→ concurrency, replication, partition, consistency, consensus, delivery, routing, cache a resilience mechanisms",
    "→ concurrency, replication, partition, consistency, consensus, delivery, routing, cache, resilience, admission, idempotency a backpressure mechanisms",
    "dominant mechanisms",
)
text = replace_once(
    text,
    "→ bounded write/read/partition/leadership/route/retry/recovery decision",
    "→ bounded write/read/partition/leadership/route/retry/admission/flow/recovery decision",
    "dominant decision",
)

if "- configured local limit od effective fleet/global admission;" not in text:
    text = text.replace(
        "- logical operation od nested physical retry tree a aggregate budget;",
        "- logical operation od nested physical retry tree a aggregate budget;\n"
        "- configured local limit od effective fleet/global admission;\n"
        "- rate/quota policy od current downstream backpressure;\n"
        "- idempotency key od semantic operation equivalence;\n"
        "- queue depth od queue age, deadlines a drain capacity;\n"
        "- accepted durable work od completed/reconciled business effect;",
        1,
    )

final_gate_marker = "## Finálny section-level consistency gate"
if final_gate_marker not in text:
    gate = r'''
## Finálny section-level consistency gate

Sekcia prešla finálnym gate-om nad celým authoritative poradím:

```text
data model a authority
→ transaction a physical access/concurrency
→ replication, backup a recovery
→ connection/product/architecture boundaries
→ synchronous/asynchronous communication
→ durable messaging, routing a cache coherence
→ partition a consistency model
→ consensus, leadership a resilience
→ fair admission, idempotency a bounded flow
→ business reconciliation a lifecycle closure
```

Overené bolo:

- presné poradie všetkých 18 kapitol podľa `ROADMAP.md`;
- päť connected incidentov `DB-PAY-56` až `DB-PAY-60` s oddelenými trigger, root-cause a amplifier boundaries;
- jednotná operation identity od client intentu cez transaction/outbox/message/provider až po final result;
- rozlíšenie authoritative, derived a cached state-u;
- rozlíšenie commit, acknowledgement, delivery, apply, visibility a completion boundaries;
- prepojenie consistency, availability, leadership, retries, rate limits, idempotency a backpressure s business invariantom;
- recovery cez reconciliation, fencing, replay/restore, bounded drain a second-operation/second-failure tests;
- glossary fragments `15a`–`15e`, generated `GLOSSARY.md`, roadmap a navigation chain;
- prázdne `DOCUMENTATION-AUDIT.md` a `documentation-audit.json` failure artifacts po finálnej synchronizácii;
- current primary-source semantics pre PostgreSQL, MySQL, Redis, Kafka, RabbitMQ, etcd, Kubernetes, HTTP, gRPC a Reactive Streams.

Stav **Ready for user review** znamená dokončené authoritative drafting a repository-level consistency gate. Neznamená automatické používateľské schválenie, produkčnú certifikáciu ani stav Verified alebo Stable.
'''.strip()
    text = text.replace("## Stav", gate + "\n\n## Stav", 1)

text = replace_once(
    text,
    "| Rate limiting | Not Started | L0 |",
    "| Rate limiting | Learning | L2 |",
    "rate limiting status",
)
text = replace_once(
    text,
    "| Idempotency a backpressure | Not Started | L0 |",
    "| Idempotency a backpressure | Learning | L2 |",
    "idempotency status",
)

text = replace_once(
    text,
    "Sekcia zostáva **In progress**. Stav **Ready for user review** možno použiť až po vytvorení všetkých 18 authoritative kapitol, overení navigation chainu, glossary, audit artifacts a finálnom section-level consistency passe.",
    "Sekcia je **18/18 · Ready for user review**. Všetky authoritative kapitoly, connected scenarios, navigation, glossary a audit gates sú dokončené; stav neznamená automatické používateľské schválenie.",
    "final section state",
)

readme_path.write_text(text, encoding="utf-8")

ledger_path = Path("DOCUMENTATION-REVIEW-STATUS.md")
lines = ledger_path.read_text(encoding="utf-8").splitlines()
prefix = "| `15-databases-and-distributed-systems` — Databases and Distributed Systems |"
replacement = (
    "| `15-databases-and-distributed-systems` — Databases and Distributed Systems | "
    "18/18 authoritative drafting | Ready for user review | 2026-07-29 | "
    "Všetkých 18 authoritative kapitol bolo vytvorených a sekcia prešla finálnym section-level consistency gate-om. "
    "Päť connected incidentov vytvára jeden stateful/distributed learning chain: `DB-PAY-56` pokrýva data-model authority, atomic settlement/outbox, indexed migration a fenced HA; "
    "`DB-PAY-57` PITR continuity, connection pooling, PostgreSQL/MySQL/Redis role a architecture ownership; `DB-PAY-58` communication, messaging acknowledgement, route generation a cache coherence; "
    "`DB-PAY-59` per-operation CAP decision, formal consistency history, quorum/leader fencing a retry/circuit amplification; `DB-PAY-60` fair hierarchical admission, atomic semantic idempotency a downstream-credit backpressure. "
    "Záverečný incident ukázal 80 Pod-local limiterov s effective admission 36 000 req/s proti provider capacity približne 6 500 attempts/s, 20-minútovú idempotency expiry pri 54-minútovom backlogu, "
    "83 duplicate authoritative operations, 31 duplicate provider effects a theoretical worker concurrency 96 000 proti safe in-flight 1 200. Redesign používa global/provider/tenant/operation-class budgets, reserved recovery capacity, "
    "atomic claim + settlement + outbox, semantic fingerprint, stable provider identity, bounded queues/credits, rebalance-safe pause state, backlog-age admission a reconciliation pred unknown retryom. "
    "Finálny gate overil authoritative ordering 18/18, celý navigation chain od SRE vstupu po `Idempotency a backpressure → ROADMAP`, glossary fragments `15a`–`15e`, generated `GLOSSARY.md`, roadmap, empty audit-failure artifacts a current primary-source semantics. "
    "Sekcia je pripravená na používateľskú kontrolu, nie automaticky používateľsky schválená, Accepted, Verified ani Stable. |"
)

matches = [i for i, line in enumerate(lines) if line.startswith(prefix)]
if len(matches) != 1:
    raise RuntimeError(f"Expected one database ledger row, found {len(matches)}")
lines[matches[0]] = replacement
ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
