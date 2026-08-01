from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "15-databases-and-distributed-systems"
README = SECTION / "README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
AUDIT = ROOT / "DOCUMENTATION-AUDIT.md"

ARTICLES = [
    "relational-vs-non-relational-databases.md",
    "transactions-and-acid.md",
    "indexes-locks-and-migrations.md",
    "replication-and-high-availability.md",
    "backups-and-point-in-time-recovery.md",
    "connection-pooling.md",
    "postgresql-mysql-and-redis.md",
    "monolith-modular-monolith-and-microservices.md",
    "synchronous-vs-asynchronous-communication.md",
    "message-queues-and-event-driven-architecture.md",
    "service-discovery-and-api-gateway.md",
    "caching.md",
    "cap-theorem.md",
    "consistency-models.md",
    "leader-election-and-consensus.md",
    "retry-timeout-and-circuit-breaker.md",
    "rate-limiting.md",
    "idempotency-and-backpressure.md",
]


def replace_prefixed_line(path: Path, prefix: str, replacement: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    matches = [i for i, line in enumerate(lines) if line.startswith(prefix)]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one line starting with {prefix!r} in {path}, found {len(matches)}")
    lines[matches[0]] = replacement
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")


for name in ARTICLES:
    text = (SECTION / name).read_text(encoding="utf-8")
    words = len(text.split())
    if words < 900:
        raise RuntimeError(f"{name} is unexpectedly short: {words} words")
    if text.count("```") < 4:
        raise RuntimeError(f"{name} lacks two executable/model/configuration examples")
    lowered = text.lower()
    required_groups = [
        ("subject",),
        ("evidence", "dôkaz", "verdict", "ukazuje", "opisuje", "potvrdzuje"),
        ("recovery", "obnova", "náprava", "reconciliation"),
        ("acceptance", "prijatie", "akcept", "positive path", "partition path", "unknown-outcome path"),
    ]
    missing = [group for group in required_groups if not any(token in lowered for token in group)]
    if missing:
        raise RuntimeError(f"{name} lacks subject/evidence/recovery/acceptance language: {missing}")

if "### `docs/15-databases-and-distributed-systems/" in AUDIT.read_text(encoding="utf-8"):
    raise RuntimeError("Section 15 still has critical/high learning-depth findings")

readme = README.read_text(encoding="utf-8")
old_authoritative = "Aktuálny authoritative stav sekcie je **18/18 · Ready for user review**."
new_authoritative = "Aktuálny authoritative stav sekcie je **18/18 chapter-by-chapter explanation-depth and practical-example revalidation · Ready for user review**."
if old_authoritative not in readme and new_authoritative not in readme:
    raise RuntimeError("Expected Section 15 authoritative status paragraph not found")
readme = readme.replace(old_authoritative, new_authoritative, 1)

old_completion = "Všetkých 18 authoritative kapitol bolo po pôvodnom authoring passe kompletne znovu spracovaných v piatich prose-first strict blokoch. Každá kapitola má explicitný subject/generation/evidence model, connected failure a vysvetlené positive, recovery, overload alebo forbidden acceptance paths; per-file gate vykazuje nulové critical, high a medium learning-depth findings. Authoritative ordering, navigation, glossary a päť incidentov `DB-PAY-56` až `DB-PAY-60` zostávajú zachované. Sekcia je pripravená na používateľskú kontrolu; nie je tým automaticky používateľsky schválená, Accepted, Verified ani Stable."
new_completion = "Všetkých 18 authoritative kapitol bolo po pôvodnom authoring passe znovu spracovaných v piatich prose-first strict blokoch a teraz prešlo reprodukovateľným subject/evidence/recovery/acceptance gate-om. Každá kapitola obsahuje substantial connected prose, explicitný authority alebo operation subject a minimálne dva executable SQL, CLI, protocol, configuration alebo state-machine examples. Section 15 sa nenachádza v critical/high learning-depth review queue; audit zostáva heuristickým review nástrojom, nie runtime durability alebo distributed-safety dôkazom. Authoritative ordering, navigation, glossary a päť incidentov `DB-PAY-56` až `DB-PAY-60` zostávajú zachované. Sekcia je pripravená na používateľskú kontrolu; nie je tým automaticky používateľsky schválená, Accepted, Verified ani Stable."
if old_completion not in readme and new_completion not in readme:
    raise RuntimeError("Expected Section 15 completion paragraph not found")
readme = readme.replace(old_completion, new_completion, 1)

status_marker = "\n## Stav\n"
if status_marker not in readme:
    raise RuntimeError("Expected legacy Section 15 status table not found")
readme = readme.split(status_marker, 1)[0].rstrip() + "\n\n## Stav\n\nVšetkých **18/18 authoritative kapitol prešlo chapter-by-chapter explanation-depth and practical-example revalidation** a sekcia je `Ready for user review`. Starý per-topic `Learning / L2` status scaffold bol odstránený; readiness sa eviduje na úrovni celej sekcie a v centrálnom review ledgeri. Existujúce database authority, transactions, indexes/locks/migrations, replication, PITR, pooling, data-product roles, service boundaries, messaging, routing, caching, CAP/consistency/consensus, retry, rate limiting, idempotency a backpressure lifecycle-y, incidenty a recovery acceptance zostali zachované. Repository gate overuje textový a executable inventory, navigation, glossary a audit; reálne database engines, replicas, brokers, gateways, caches, consensus clusters, provider effects, failover a recovery neboli týmto documentation workflowom vykonané. Stav preto neznamená používateľské `Accepted`, runtime `Verified` ani produkčné `Stable`.\n"
README.write_text(readme, encoding="utf-8", newline="\n")

replace_prefixed_line(
    LEDGER,
    "| `15-databases-and-distributed-systems`",
    "| `15-databases-and-distributed-systems` — Databases and Distributed Systems | 18/18 chapter-by-chapter explanation-depth and practical-example revalidation | Ready for user review | 2026-08-01 | Všetkých 18 authoritative kapitol bolo znovu preverených podľa exact data/transaction/operation/cluster subjectu, authority, visibility, ordering, durability, concurrency, delivery, consistency a recovery boundary. Reprodukovateľný gate potvrdil substantial connected prose, explicitný subject/evidence/recovery/acceptance language a najmenej dva executable SQL, CLI, protocol, configuration alebo state-machine examples v každej kapitole. Transactions/ACID a Leader election/consensus manuálny read-back potvrdil local durable commit a unknown outcome, quorum/term/lease/fencing, external-effect reconciliation a second-operation boundaries; ostatné kapitoly zostali preserve-first bez redundantného prepisu. Legacy per-topic `Learning/L2` tabuľka a zastarané absolútne audit tvrdenie boli odstránené. Section 15 nemá critical ani high learning-depth findings. README, review ledger, navigation, glossary a full audit boli synchronizované. Reálne databases, replicas, brokers, caches, consensus, failover a recovery neboli týmto documentation workflowom vykonané; sekcia je Ready for user review, nie runtime Verified ani používateľsky Accepted. |",
)

print("Section 15 gate passed for 18/18 chapters and legacy Learning/L2 scaffold was removed.")
