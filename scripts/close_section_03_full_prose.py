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


# Pull-request checkout normally uses a synthetic merge ref. Work on the actual
# head branch so the generated closeout commit can be pushed without a merge.
run("git", "fetch", "origin", BRANCH)
run("git", "checkout", "-B", BRANCH, f"origin/{BRANCH}")

section = REPO / "docs/03-git-and-automation"
parts_dir = REPO / "scripts/section03_practical_parts"
parts = sorted(parts_dir.glob("part-*.txt"))
if len(parts) != 10:
    raise RuntimeError(f"Expected 10 practical parts, found {len(parts)}")

practical_path = section / "git-automation-practical-walkthrough.md"
practical = "".join(part.read_text(encoding="utf-8") for part in parts)
practical_path.write_text(practical, encoding="utf-8")

readme = (section / "README.md").read_text(encoding="utf-8")
chapter_links = re.findall(r"^\d+\. \[[^\]]+\]\(([^)]+\.md)\)$", readme, re.MULTILINE)
if len(chapter_links) != 15:
    raise RuntimeError(f"Expected 15 authoritative chapter links, found {len(chapter_links)}")
if chapter_links[-2:] != [
    "yaml-json-regular-expressions.md",
    "git-automation-practical-walkthrough.md",
]:
    raise RuntimeError(f"Unexpected final chapter ordering: {chapter_links[-2:]}")
for chapter in chapter_links:
    if not (section / chapter).is_file():
        raise RuntimeError(f"README references missing chapter: {chapter}")

for required in (
    "git init --bare origin.git",
    "git rebase origin/main",
    "git reflog -5",
    "desiredFingerprint",
    "stale plan",
    "second apply je no-op",
    "Verification vs. validation",
):
    if required not in practical:
        raise RuntimeError(f"Practical walkthrough is missing required content: {required}")

ledger_path = REPO / "DOCUMENTATION-REVIEW-STATUS.md"
ledger = ledger_path.read_text(encoding="utf-8")
new_row = (
    "| `03-git-and-automation` — Git and Automation Basics | "
    "15/15 full prose and practical revalidation | Ready for user review | 2026-08-01 | "
    "Všetkých 14 pôvodných authoritative kapitol bolo kompletne prepísaných a pribudla "
    "15. praktická kapitola. Sekcia používa jeden plynulý Atlas change `ORD-8421` od working "
    "tree a indexu cez content-addressed blobs/trees/commits, refs, remotes, fetch/push, merge, "
    "rebase, reset/revert/restore, cherry-pick, stash, conflicts a branching/repository topology "
    "až po Bash, PowerShell, Python a structured-data automation. Každá kapitola oddeľuje file "
    "content, object, tree snapshot, commit, local/remote ref, release tag, automation plan a "
    "verified runtime state a vkladá CLI alebo code priamo k vysvetľovanému state transitionu. "
    "Nový `git-automation-practical-walkthrough.md` vytvára lokálny bare remote, seed repository, "
    "Alice/Bob clones, non-fast-forward rejection, fetch/rebase conflict, semantic resolution, "
    "annotated tag, reflog recovery a fingerprintovaný Python `plan → apply → verify` tool s Bash "
    "a PowerShell wrappermi, unit tests, dirty-tree gate, stale-plan rejection a druhým no-op behom. "
    "Praktický Git/Python/Bash flow bol reálne vykonaný lokálne; Python compile, Bash syntax, tests, "
    "first apply, second no-op a stale-plan exit 3 prešli. PowerShell zostáva platformovou runtime "
    "validation hranicou. Sekcia je pripravená na používateľskú kontrolu, nie automaticky Accepted, "
    "Verified ani Stable. |"
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

# Remove the staging chunks, temporary workflow hook and this script from the
# final pull-request diff after the authoritative file and generated outputs exist.
for part in parts:
    part.unlink()
parts_dir.rmdir()

workflow_path = REPO / ".github/workflows/knowledge-navigation.yml"
workflow = workflow_path.read_text(encoding="utf-8")
temporary_step = """
      - name: Close Section 03 full prose rewrite
        if: github.event_name == 'pull_request'
        shell: bash
        run: |
          set -euo pipefail
          "$PYTHON_BIN" scripts/close_section_03_full_prose.py
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
    print("Section 03 closeout produced no changes")
    raise SystemExit(0)
if status.returncode != 1:
    raise RuntimeError("Unable to inspect staged closeout changes")

run("git", "commit", "-m", "docs: close Section 03 full prose rewrite")
run("git", "push", "origin", f"HEAD:{BRANCH}")
