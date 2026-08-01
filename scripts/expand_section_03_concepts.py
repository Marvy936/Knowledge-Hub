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


run("git", "fetch", "origin", BRANCH)
run("git", "checkout", "-B", BRANCH, f"origin/{BRANCH}")

section = REPO / "docs/03-git-and-automation"
blocks_dir = REPO / "scripts/section03_concept_blocks"
block_paths = sorted(blocks_dir.glob("*.md"))
if len(block_paths) != 14:
    raise RuntimeError(f"Expected 14 concept blocks, found {len(block_paths)}")

for block_path in block_paths:
    target = section / block_path.name
    if not target.is_file():
        raise RuntimeError(f"Missing target chapter: {target}")

    text = target.read_text(encoding="utf-8")
    block = block_path.read_text(encoding="utf-8").strip()

    if START in text:
        pattern = (
            rf"\n{{2}}{re.escape(START)}.*?{re.escape(END)}\n{{2}}"
            r"## Atlas scenár a praktické použitie\n\n"
        )
        text, count = re.subn(pattern, "\n\n", text, count=1, flags=re.DOTALL)
        if count != 1:
            raise RuntimeError(f"Unable to replace existing concept block in {target.name}")

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
old_standard = (
    "Každá kapitola začína konkrétnou zmenou alebo incidentom, nie slovníkovou definíciou. "
    "Príkazy sú vložené priamo pri stave, ktorý menia. Po každom dôležitom kroku nasleduje "
    "read-back cez `git status`, `git diff`, `git ls-files`, `git cat-file`, `git show-ref`, "
    "`git reflog`, JSON output alebo runtime verification.\n\n"
    "Odrážky zostávajú iba pri krátkom inventári states, acceptance podmienok alebo porovnaní. "
    "Hlavný výklad nesú súvislé odseky. Pri history rewrite sa vždy pomenúva collaboration "
    "boundary. Pri automatizácii sa oddelí source configuration, observed state, plan subject, "
    "mutation outcome a verified state."
)
new_standard = (
    "Každá koncepčná kapitola najprv samostatne vysvetlí, čo daný pojem znamená, aký problém "
    "rieši, ktoré objekty alebo vrstvy stavu zahŕňa a aký mechanizmus vykonáva. Nasleduje "
    "jednoduchý neutrálny príklad, ktorý nepredpokladá znalosť Atlas projektu. Až potom kapitola "
    "prejde k sekcii `Atlas scenár a praktické použitie`, kde sa pojem aplikuje na change "
    "`ORD-8421`, doplnia sa CLI príkazy, read-back, failure path a recovery. Scenár teda "
    "upevňuje už vysvetlený model; nenahrádza definíciu ani všeobecný výklad.\n\n"
    "Odrážky zostávajú iba pri krátkom inventári states, acceptance podmienok alebo porovnaní. "
    "Hlavný výklad nesú súvislé odseky. Pri history rewrite sa vždy pomenúva collaboration "
    "boundary. Pri automatizácii sa oddelí source configuration, observed state, plan subject, "
    "mutation outcome a verified state."
)
if old_standard not in readme:
    raise RuntimeError("README standard paragraph not found")
readme_path.write_text(readme.replace(old_standard, new_standard, 1), encoding="utf-8")

ledger_path = REPO / "DOCUMENTATION-REVIEW-STATUS.md"
ledger = ledger_path.read_text(encoding="utf-8")
new_row = (
    "| `03-git-and-automation` — Git and Automation Basics | "
    "15/15 concept-first full prose and practical revalidation | Ready for user review | "
    "2026-08-01 | Všetkých 14 koncepčných kapitol bolo po full prose rewritingu znovu "
    "rozšírených podľa concept-first štandardu. Každá kapitola teraz najprv samostatne "
    "vysvetľuje definíciu pojmu, problém, ktorý rieši, vlastnený state/object model, vnútorný "
    "mechanizmus a neutrálny príklad; až potom nasleduje Atlas change `ORD-8421`, CLI read-back, "
    "incident a recovery. Rozšírenie pokrýva blobs/trees/commits/tags, working tree/index/repository, "
    "refs a HEAD, distributed remotes, three-way merge a replay rebase, restore/reset/revert, "
    "cherry-pick/stash, textové aj semantic conflicts, branching a repository topology, Bash "
    "expansion/exit/idempotency model, PowerShell object pipeline/error streams/ShouldProcess, "
    "Python domain/I-O separation a stale-plan ochranu a JSON/YAML/regex boundaries. "
    "Praktický walkthrough zostáva záverečnou integráciou už vysvetlených mechanizmov. "
    "Navigation, glossary a full learning-depth audit boli znovu synchronizované. Sekcia je "
    "pripravená na používateľskú kontrolu, nie automaticky Accepted, Verified ani Stable. |"
)
ledger, count = re.subn(
    r"^\| `03-git-and-automation`[^\n]*$",
    new_row,
    ledger,
    count=1,
    flags=re.MULTILINE,
)
if count != 1:
    raise RuntimeError(f"Section 03 ledger row: expected one match, found {count}")
ledger_path.write_text(ledger, encoding="utf-8")

for block_path in block_paths:
    text = (section / block_path.name).read_text(encoding="utf-8")
    if text.count(START) != 1 or text.count(END) != 1:
        raise RuntimeError(f"Concept marker mismatch in {block_path.name}")
    if "## Atlas scenár a praktické použitie" not in text:
        raise RuntimeError(f"Atlas section missing in {block_path.name}")

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
      - name: Expand Section 03 concept-first explanations
        if: github.event_name == 'pull_request'
        shell: bash
        run: |
          set -euo pipefail
          "$PYTHON_BIN" scripts/expand_section_03_concepts.py
"""
if workflow.count(temporary_step) != 1:
    raise RuntimeError("Temporary workflow step was not found exactly once")
workflow_path.write_text(workflow.replace(temporary_step, "", 1), encoding="utf-8")

shutil.rmtree(blocks_dir)
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
    print("Section 03 concept expansion produced no changes")
    raise SystemExit(0)
if status.returncode != 1:
    raise RuntimeError("Unable to inspect staged changes")

run("git", "commit", "-m", "docs: expand Section 03 concept-first explanations")
run("git", "push", "origin", f"HEAD:{BRANCH}")
