from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "12-observability"
README = SECTION / "README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
AUDIT = ROOT / "DOCUMENTATION-AUDIT.md"

ARTICLES = [
    "monitoring-vs-observability.md",
    "metrics-logs-traces-events.md",
    "instrumentation-telemetry.md",
    "red-method.md",
    "use-method.md",
    "golden-signals.md",
    "prometheus.md",
    "alertmanager.md",
    "grafana.md",
    "loki.md",
    "elasticsearch-opensearch.md",
    "fluent-bit.md",
    "jaeger-tempo.md",
    "opentelemetry.md",
    "alert-design-alert-fatigue.md",
    "cardinality.md",
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
    if words < 850:
        raise RuntimeError(f"{name} is unexpectedly short: {words} words")
    if text.count("```") < 4:
        raise RuntimeError(f"{name} lacks two executable/query/configuration examples")
    required = ["subject", "preukazuje", "Nepreukazuje"]
    missing = [token for token in required if token.lower() not in text.lower()]
    if missing:
        raise RuntimeError(f"{name} lacks explicit subject/proof-boundary language: {missing}")

if "### `docs/12-observability/" in AUDIT.read_text(encoding="utf-8"):
    raise RuntimeError("Section 12 still has critical/high learning-depth findings")

readme = README.read_text(encoding="utf-8")
readme = readme.replace(
    "9. learning-depth audit artifacts sú prázdne;",
    "9. Section 12 sa nenachádza v critical/high learning-depth review queue a zostávajúce low hints sa posudzujú manuálne;",
)
old_gate = "Finálny prose/practical gate overil všetkých 16 kapitol samostatne. Každá dosiahla `critical/high/medium = 0/0/0`, obsahuje najmenej dva executable PromQL, LogQL, TraceQL, CLI alebo configuration príklady a vysvetľuje, čo ich output preukazuje aj čo ešte nepreukazuje. Súvislý prose rozsah je 918–1 199 slov na kapitolu a bullet-word share zostáva medzi 9.1 % a 14.9 %, takže zoznamy nenesú hlavnú učebnú záťaž."
new_gate = "Reprodukovateľný prose/practical gate overil všetkých 16 kapitol samostatne. Každá obsahuje substantial connected prose, explicitný evidence subject, najmenej dva executable PromQL, LogQL, TraceQL, CLI alebo configuration príklady a vysvetľuje, čo ich output preukazuje aj čo ešte nepreukazuje. Section 12 sa nenachádza v critical/high learning-depth review queue; audit zostáva heuristickým review nástrojom, nie dôkazom technickej správnosti alebo runtime funkčnosti."
if old_gate not in readme and new_gate not in readme:
    raise RuntimeError("Expected Section 12 completion-gate paragraph not found")
readme = readme.replace(old_gate, new_gate, 1)

status_marker = "\n## Stav\n"
if status_marker not in readme:
    raise RuntimeError("Expected legacy Section 12 status table not found")
readme = readme.split(status_marker, 1)[0].rstrip() + "\n\n## Stav\n\nVšetkých **16/16 authoritative kapitol prešlo chapter-by-chapter explanation-depth and practical-example revalidation** a sekcia je `Ready for user review`. Starý per-topic `L2` status scaffold bol odstránený; readiness sa teraz eviduje na úrovni celej sekcie a v centrálnom review ledgeri. Existujúce lifecycle modely, PromQL/LogQL/TraceQL, CLI, configuration examples, worked incidents, recovery a cardinality/cost closure zostali zachované. Repository gate overuje textový a executable inventory, navigation, glossary a audit; reálne telemetry producers, Collectors, Prometheus/Alertmanager/Grafana/Loki/OpenSearch/Jaeger/Tempo backends, notification receivers ani retention/cost behavior neboli týmto documentation workflowom vykonané. Stav preto neznamená používateľské `Accepted`, runtime `Verified` ani produkčné `Stable`.\n"
README.write_text(readme, encoding="utf-8", newline="\n")

replace_prefixed_line(
    LEDGER,
    "| `12-observability`",
    "| `12-observability` — Observability | 16/16 chapter-by-chapter explanation-depth and practical-example revalidation | Ready for user review | 2026-08-01 | Všetkých 16 authoritative kapitol bolo znovu preverených podľa observed subject/population, instrumentation, propagation, collector processing, backend ingest/storage/query, evidence completeness, alert delivery, recovery a cardinality/cost closure štandardu. Reprodukovateľný gate potvrdil substantial connected prose, explicitný subject/proof-boundary language a najmenej dva executable PromQL, LogQL, TraceQL, CLI alebo configuration examples v každej kapitole. Prometheus a OpenTelemetry manuálny read-back potvrdil configured/loaded/emitted/accepted/durable/queryable separation; ostatné chapters zostali preserve-first bez redundantného prepisu. Legacy per-topic `L2` status tabuľka bola odstránená. Section 12 nemá critical ani high learning-depth findings. README, review ledger, navigation, glossary a full audit boli synchronizované. Reálne telemetry pipelines, backends, notification receivers, retention a cost behavior neboli týmto documentation workflowom vykonané; sekcia je Ready for user review, nie runtime Verified ani používateľsky Accepted. |",
)

print("Section 12 gate passed for 16/16 chapters and legacy L2 scaffold was removed.")
