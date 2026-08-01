from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRANCH = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
if not BRANCH:
    raise SystemExit("Unable to resolve pull request branch")

START = "<!-- CONCEPT-FIRST:START -->"
END = "<!-- CONCEPT-FIRST:END -->"


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=REPO, check=True)


def load_blocks(parts_dir: Path) -> dict[str, str]:
    blocks: dict[str, str] = {}
    for part in sorted(parts_dir.glob("part-*.txt")):
        current: str | None = None
        lines: list[str] = []
        for line in part.read_text(encoding="utf-8").splitlines():
            if line.startswith("@@ "):
                if current is not None:
                    blocks[current] = "\n".join(lines).strip()
                current = line[3:].strip()
                lines = []
            else:
                lines.append(line)
        if current is not None:
            blocks[current] = "\n".join(lines).strip()
    return blocks


run("git", "fetch", "origin", BRANCH)
run("git", "checkout", "-B", BRANCH, f"origin/{BRANCH}")

section = REPO / "docs/04-testing-and-quality"
parts_dir = REPO / "scripts/section04_concept_parts"
blocks = load_blocks(parts_dir)
if len(blocks) != 15:
    raise RuntimeError(f"Expected 15 concept blocks, found {len(blocks)}")

for filename, block in blocks.items():
    target = section / filename
    if not target.is_file():
        raise RuntimeError(f"Missing target chapter: {target}")

    text = target.read_text(encoding="utf-8")
    if START in text:
        pattern = (
            rf"\n{{2}}{re.escape(START)}.*?{re.escape(END)}\n{{2}}"
            r"## Atlas scenár a praktické použitie\n\n"
        )
        text, count = re.subn(pattern, "\n\n", text, count=1, flags=re.DOTALL)
        if count != 1:
            raise RuntimeError(f"Unable to replace existing concept block in {filename}")

    title, rest = text.split("\n", 1)
    rest = rest.lstrip("\n")
    expanded = (
        f"{title}\n\n{START}\n{block}\n{END}\n\n"
        "## Atlas scenár a praktické použitie\n\n"
        f"{rest}"
    )
    target.write_text(expanded, encoding="utf-8")

readme_path = section / "README.md"
readme = readme_path.read_text(encoding="utf-8")
anchor = (
    "Po tejto sekcii nasleduje CI/CD and Release Engineering. Testovacie stratégie sa tam "
    "premenia na konkrétne pipeline stages, quality gates, promotion rules a progressive "
    "delivery mechanizmy.\n\n## Cieľ zvládnutia"
)
replacement = (
    "Po tejto sekcii nasleduje CI/CD and Release Engineering. Testovacie stratégie sa tam "
    "premenia na konkrétne pipeline stages, quality gates, promotion rules a progressive "
    "delivery mechanizmy.\n\n"
    "## Výkladový štandard\n\n"
    "Každá kapitola najprv samostatne vysvetlí, čo daný testovací typ, technika alebo stratégia "
    "znamená, aký failure mode alebo riziko rieši, aký subject a scope používa, akú fidelity "
    "potrebuje a aký oracle vytvára pass/fail verdict. Nasleduje neutrálny príklad a hranica "
    "dôkazu — teda čo test preukazuje a čo z neho nemožno odvodiť. Až potom kapitola prejde k "
    "sekcii `Atlas scenár a praktické použitie`, kde sa model aplikuje na Atlas Orders release, "
    "doplnia sa artifacts, failure path, diagnosis a recovery. Scenár upevňuje všeobecný výklad; "
    "nenahrádza ho.\n\n"
    "Hlavný výklad nesú súvislé odseky. Inventáre, matice a checklisty zostávajú iba tam, kde "
    "pomáhajú presne porovnať scope, evidence alebo acceptance podmienky.\n\n"
    "## Cieľ zvládnutia"
)
if anchor not in readme:
    raise RuntimeError("README insertion anchor not found")
readme_path.write_text(readme.replace(anchor, replacement, 1), encoding="utf-8")

ledger_path = REPO / "DOCUMENTATION-REVIEW-STATUS.md"
ledger = ledger_path.read_text(encoding="utf-8")
new_row = (
    "| `04-testing-and-quality` — Testing and Software Quality | "
    "15/15 concept-first full prose revalidation | Ready for user review | 2026-08-01 | "
    "Všetkých 15 kapitol bolo rozšírených podľa concept-first štandardu. Každá kapitola teraz "
    "najprv vysvetľuje definíciu testovacieho typu alebo stratégie, test subject a scope, failure "
    "mode/risk, požadovanú fidelity, oracle, evidence boundary a neutrálny príklad; až potom "
    "nasleduje Atlas Orders scenár, failure, diagnosis a recovery. Rozšírenie pokrýva verification "
    "vs validation a traceability, risk-based test pyramid, unit/integration/component boundaries, "
    "contract vs runtime API tests, E2E/acceptance, smoke/regression, workload models pre load/stress, "
    "threat-informed security a IaC evidence, static analysis, coverage a quality gates, test doubles, "
    "flakiness/test-data isolation, shift-left, shift-right a chaos experiment state machine. README "
    "explicitne stanovuje, že scenár je aplikácia už vysvetleného modelu. Navigation, glossary a "
    "full learning-depth audit boli znovu synchronizované. Sekcia je pripravená na používateľskú "
    "kontrolu, nie automaticky Accepted, Verified ani Stable. |"
)
ledger, count = re.subn(
    r"^\| `04-testing-and-quality`[^\n]*$",
    new_row,
    ledger,
    count=1,
    flags=re.MULTILINE,
)
if count != 1:
    raise RuntimeError(f"Section 04 ledger row: expected one match, found {count}")
ledger_path.write_text(ledger, encoding="utf-8")

for filename in blocks:
    text = (section / filename).read_text(encoding="utf-8")
    if text.count(START) != 1 or text.count(END) != 1:
        raise RuntimeError(f"Concept marker mismatch in {filename}")
    if "## Atlas scenár a praktické použitie" not in text:
        raise RuntimeError(f"Atlas section missing in {filename}")

python_bin = os.environ.get("PYTHON_BIN", "python")
run(python_bin, "scripts/update_glossary.py", "--write")
run(python_bin, "scripts/update_navigation.py", "--write")
run(
    python_bin,
    "scripts/audit_learning_depth.py",
    "--all-docs",
    "--report",
    "DOCUMENTATION-AUDIT.md",
    "--json",
    "documentation-audit.json",
)

workflow_path = REPO / ".github/workflows/knowledge-navigation.yml"
workflow = workflow_path.read_text(encoding="utf-8")
temporary_step = """
      - name: Expand Section 04 concept-first explanations
        if: github.event_name == 'pull_request'
        shell: bash
        run: |
          set -euo pipefail
          "$PYTHON_BIN" scripts/expand_section_04_concepts.py
"""
if workflow.count(temporary_step) != 1:
    raise RuntimeError("Temporary workflow step was not found exactly once")
workflow_path.write_text(workflow.replace(temporary_step, "", 1), encoding="utf-8")

shutil.rmtree(parts_dir)
Path(__file__).unlink()

run("git", "config", "user.name", "github-actions[bot]")
run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
run(
    "git",
    "add",
    "DOCUMENTATION-REVIEW-STATUS.md",
    "DOCUMENTATION-AUDIT.md",
    "documentation-audit.json",
    "GLOSSARY.md",
    "glossary",
    "docs",
    ".github/workflows/knowledge-navigation.yml",
    "scripts",
)

status = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO)
if status.returncode == 0:
    print("Section 04 concept expansion produced no changes")
    raise SystemExit(0)
if status.returncode != 1:
    raise RuntimeError("Unable to inspect staged changes")

run("git", "commit", "-m", "docs: expand Section 04 concept-first explanations")
run("git", "push", "origin", f"HEAD:{BRANCH}")
