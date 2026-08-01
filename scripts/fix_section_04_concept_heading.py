from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRANCH = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
if not BRANCH:
    raise SystemExit("Unable to resolve pull request branch")

OLD = "## Atlas scenár a praktické použitie"
NEW = "## Detailný výklad a Atlas aplikácia"


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=REPO, check=True)


run("git", "fetch", "origin", BRANCH)
run("git", "checkout", "-B", BRANCH, f"origin/{BRANCH}")

section = REPO / "docs/04-testing-and-quality"
changed = 0
for path in sorted(section.glob("*.md")):
    if path.name == "README.md":
        continue
    text = path.read_text(encoding="utf-8")
    if "<!-- CONCEPT-FIRST:START -->" not in text:
        continue
    if text.count(OLD) != 1:
        raise RuntimeError(f"Expected one old heading in {path.name}")
    path.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    changed += 1

if changed != 15:
    raise RuntimeError(f"Expected 15 chapter heading changes, found {changed}")

readme_path = section / "README.md"
readme = readme_path.read_text(encoding="utf-8")
old_phrase = "sekcii `Atlas scenár a praktické použitie`"
new_phrase = "sekcii `Detailný výklad a Atlas aplikácia`"
if readme.count(old_phrase) != 1:
    raise RuntimeError("README heading reference not found exactly once")
readme_path.write_text(readme.replace(old_phrase, new_phrase, 1), encoding="utf-8")

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
      - name: Fix Section 04 concept headings
        if: github.event_name == 'pull_request'
        shell: bash
        run: |
          set -euo pipefail
          "$PYTHON_BIN" scripts/fix_section_04_concept_heading.py
"""
if workflow.count(temporary_step) != 1:
    raise RuntimeError("Temporary workflow step was not found exactly once")
workflow_path.write_text(workflow.replace(temporary_step, "", 1), encoding="utf-8")
Path(__file__).unlink()

run("git", "config", "user.name", "github-actions[bot]")
run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
run(
    "git",
    "add",
    "DOCUMENTATION-AUDIT.md",
    "documentation-audit.json",
    "GLOSSARY.md",
    "glossary",
    "docs",
    ".github/workflows/knowledge-navigation.yml",
    "scripts",
)
run("git", "commit", "-m", "docs: clarify Section 04 concept and scenario headings")
run("git", "push", "origin", f"HEAD:{BRANCH}")
