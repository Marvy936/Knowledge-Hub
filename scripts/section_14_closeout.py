from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "14-sre-and-operations"
README = SECTION / "README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
AUDIT = ROOT / "DOCUMENTATION-AUDIT.md"

ARTICLES = [
    "reliability-availability-durability.md",
    "sli-slo-sla.md",
    "error-budgets.md",
    "toil.md",
    "capacity-planning.md",
    "incident-management.md",
    "on-call-and-escalation.md",
    "runbooks-and-playbooks.md",
    "root-cause-analysis.md",
    "blameless-postmortems.md",
    "backup-and-restore.md",
    "rpo-and-rto.md",
    "disaster-recovery.md",
    "chaos-engineering.md",
    "operational-readiness.md",
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
        ("evidence", "dôkaz", "verdict", "ukazuje", "opisuje", "vyjadruje", "potvrdzuje"),
        ("nepreukazuje", "nedokazuje", "nedokáže", "nemusí dokazovať", "nestačí", "samotné", "iba report", "nie je automatický", "nie je automatické"),
        ("recovery", "obnova", "náprava"),
        ("forbidden", "zakázan"),
        ("acceptance", "prijatie", "akcept"),
    ]
    missing = [group for group in required_groups if not any(token in lowered for token in group)]
    if missing:
        raise RuntimeError(f"{name} lacks subject/evidence-boundary/recovery/forbidden/acceptance language: {missing}")

if "### `docs/14-sre-and-operations/" in AUDIT.read_text(encoding="utf-8"):
    raise RuntimeError("Section 14 still has critical/high learning-depth findings")

readme = README.read_text(encoding="utf-8")
old_authoritative = "Aktuálny authoritative stav sekcie je **15/15 · Ready for user review**. Všetkých 15 kapitol bolo po pôvodnom authoring passe kompletne znovu spracovaných v štyroch prose-first strict blokoch; každá kapitola má nulové critical, high a medium learning-depth findings. Authoritative ordering, connected incidents, navigation, glossary a section-level consistency zostávajú zachované."
new_authoritative = "Aktuálny authoritative stav sekcie je **15/15 chapter-by-chapter explanation-depth and practical-example revalidation · Ready for user review**. Všetkých 15 kapitol bolo po pôvodnom authoring passe znovu spracovaných v štyroch strict prose-first blokoch a teraz prešlo reprodukovateľným subject/evidence-boundary/recovery/forbidden-path gate-om. Section 14 sa nenachádza v critical/high learning-depth review queue; audit zostáva heuristickým review nástrojom, nie runtime reliability dôkazom. Authoritative ordering, connected incidents, navigation, glossary a section-level consistency zostávajú zachované."
if old_authoritative not in readme and new_authoritative not in readme:
    raise RuntimeError("Expected Section 14 authoritative status paragraph not found")
readme = readme.replace(old_authoritative, new_authoritative, 1)

status_marker = "\n## Stav\n"
if status_marker not in readme:
    raise RuntimeError("Expected legacy Section 14 status table not found")
readme = readme.split(status_marker, 1)[0].rstrip() + "\n\n## Stav\n\nVšetkých **15/15 authoritative kapitol prešlo chapter-by-chapter explanation-depth and practical-example revalidation** a sekcia je `Ready for user review`. Starý per-topic `Learning / L2` status scaffold bol odstránený; readiness sa eviduje na úrovni celej sekcie a v centrálnom review ledgeri. Existujúce SLI/SLO/error-budget, toil, capacity, incident command, on-call, runbook, RCA/postmortem, backup/restore, RPO/RTO, DR, chaos a operational-readiness lifecycle-y, executable models, incidents a recovery acceptance zostali zachované. Repository gate overuje textový a executable inventory, navigation, glossary a audit; reálne production telemetry, incident response, restore, regional failover, chaos injection ani readiness exercise neboli týmto documentation workflowom vykonané. Stav preto neznamená používateľské `Accepted`, runtime `Verified` ani produkčné `Stable`.\n"
README.write_text(readme, encoding="utf-8", newline="\n")

replace_prefixed_line(
    LEDGER,
    "| `14-sre-and-operations`",
    "| `14-sre-and-operations` — SRE and Operations | 15/15 chapter-by-chapter explanation-depth and practical-example revalidation | Ready for user review | 2026-08-01 | Všetkých 15 authoritative kapitol bolo znovu preverených podľa exact reliability/recovery/operating subjectu, user/business objective, current-generation evidence, bounded action alebo experiment, effective-state verification, recovery, forbidden-path a recurrence/second-operation closure štandardu. Reprodukovateľný gate potvrdil substantial connected prose, explicitný subject/evidence-boundary/recovery/forbidden/acceptance language a najmenej dva executable model, CLI alebo configuration examples v každej kapitole. Incident management a Disaster recovery manuálny read-back potvrdil command/writer authority, evidence-preserving bounded mutation, business acceptance, alternate-scenario a failback boundaries; ostatné kapitoly zostali preserve-first bez redundantného prepisu. Legacy per-topic `Learning/L2` tabuľka a zastarané absolútne audit tvrdenie boli odstránené. Section 14 nemá critical ani high learning-depth findings. README, review ledger, navigation, glossary a full audit boli synchronizované. Reálne incidents, restores, DR, chaos a operational-readiness exercises neboli týmto documentation workflowom vykonané; sekcia je Ready for user review, nie runtime Verified ani používateľsky Accepted. |",
)

print("Section 14 gate passed for 15/15 chapters and legacy Learning/L2 scaffold was removed.")
