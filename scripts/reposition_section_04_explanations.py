from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRANCH = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
if not BRANCH:
    raise SystemExit("Unable to resolve pull request branch")


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=REPO, check=True)


run("git", "fetch", "origin", BRANCH)
run("git", "checkout", "-B", BRANCH, f"origin/{BRANCH}")

section = REPO / "docs/04-testing-and-quality"
files = [path for path in section.glob("*.md") if path.name != "README.md"]
block_re = re.compile(r"(?ms)^## Doplnenie výkladu:.*?(?=^## |^<!-- KNOWLEDGE-NAVIGATION:START -->)")
anchor_re = re.compile(
    r"(?m)^## (?:\d+\.\s*)?(?:Worked failure|Connected incident|Incident|Atlas incident|Troubleshooting flow|Zhrnutie|Anti-patterny)"
)

for path in files:
    text = path.read_text(encoding="utf-8")
    match = block_re.search(text)
    if not match:
        raise RuntimeError(f"Explanation block missing in {path.name}")
    block = match.group(0).rstrip() + "\n\n"
    without = text[: match.start()] + text[match.end() :]
    anchor = anchor_re.search(without)
    if anchor:
        updated = without[: anchor.start()] + block + without[anchor.start() :]
    else:
        nav = "<!-- KNOWLEDGE-NAVIGATION:START -->"
        if nav not in without:
            raise RuntimeError(f"No final anchor in {path.name}")
        updated = without.replace(nav, block + nav, 1)
    path.write_text(updated, encoding="utf-8")

run("python", "scripts/update_navigation.py", "--check")
run("python", "scripts/update_glossary.py", "--check")
run("python", "scripts/audit_learning_depth.py", "--all-docs")

workflow_path = REPO / ".github/workflows/knowledge-navigation.yml"
workflow = workflow_path.read_text(encoding="utf-8")
step = '''      - name: Reposition Section 04 explanations
        if: github.event_name == 'pull_request'
        shell: bash
        run: |
          set -euo pipefail
          "$PYTHON_BIN" scripts/reposition_section_04_explanations.py

'''
if workflow.count(step) != 1:
    raise RuntimeError("Temporary positioning step missing")
workflow_path.write_text(workflow.replace(step, "", 1), encoding="utf-8")
Path(__file__).unlink()

run("git", "config", "user.name", "github-actions[bot]")
run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
run("git", "add", "docs/04-testing-and-quality", ".github/workflows/knowledge-navigation.yml", "scripts")
run("git", "commit", "-m", "docs(testing): position explanations before failure scenarios")
run("git", "push", "origin", f"HEAD:{BRANCH}")
