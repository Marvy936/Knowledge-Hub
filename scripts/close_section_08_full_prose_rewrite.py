from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
WORKFLOW = REPOSITORY / ".github/workflows/knowledge-navigation.yml"
LEDGER = REPOSITORY / "DOCUMENTATION-REVIEW-STATUS.md"
SCRIPT = Path(__file__).resolve()

START_MARKER = "      # SECTION08_FULL_REWRITE_CLOSEOUT_START"
END_MARKER = "      # SECTION08_FULL_REWRITE_CLOSEOUT_END"

NEW_LEDGER_ROW = (
    "| `08-container-fundamentals-and-docker` — Container Fundamentals and Docker "
    "| 19/19 full prose and practical revalidation | Ready for user review | 2026-08-01 "
    "| Všetkých 19 authoritative kapitol bolo kompletne prepísaných, nie iba doplnených o praktický walkthrough. "
    "Sekcia teraz používa jeden plynulý `payments-api` výklad od Linux procesu, VM a kernel isolation cez namespaces, "
    "cgroups, capabilities, OCI index/manifest/config/layers, copy-on-write, registry, packet path, storage a security "
    "až po Docker Engine, Dockerfile, build context/cache, multi-stage graph, mounts, port publishing, environment, "
    "health, Compose, BuildKit/Buildx a evidence-preserving troubleshooting. Každá kapitola vysvetľuje mechanizmus "
    "súvislým textom, vkladá CLI, Dockerfile, YAML alebo JSON priamo k vysvetľovanému kroku a oddeľuje source, resolved, "
    "effective, runtime a business evidence. Praktická kapitola vytvára Go aplikáciu, unit a forbidden-path testy, "
    "multi-stage Dockerfile, explicitný BuildKit test target, hardenovaný non-root runtime, named-volume persistence, "
    "celý Compose model, no-op a configuration-driven reconciliation, broken-bind a volume-permission failure, "
    "multi-platform publication a digest read-back. Go source prešiel lokálnym `gofmt` a `go test` na dostupnom Go 1.23.2 "
    "toolchaine po dočasnom znížení `go` directive; dokumentovaný contract zostáva Go 1.25. Repository workflow overuje "
    "navigation, glossary a learning depth, nie reálne Docker Engine, platform-native images alebo registry publication. "
    "Sekcia je pripravená na používateľskú kontrolu, nie automaticky Accepted, Verified ani Stable. |"
)


def run(*args: str) -> None:
    subprocess.run(args, cwd=REPOSITORY, check=True)


def checkout_head_branch() -> str:
    branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    if not branch:
        raise RuntimeError("Unable to resolve the pull-request head branch.")
    run("git", "fetch", "origin", branch)
    run("git", "checkout", "-B", branch, f"origin/{branch}")
    return branch


def update_ledger() -> None:
    text = LEDGER.read_text(encoding="utf-8")
    pattern = re.compile(
        r"^\| `08-container-fundamentals-and-docker` — Container Fundamentals and Docker \|.*$",
        re.MULTILINE,
    )
    updated, count = pattern.subn(NEW_LEDGER_ROW, text)
    if count != 1:
        raise RuntimeError(f"Expected one Section 08 ledger row, replaced {count}.")
    LEDGER.write_text(updated, encoding="utf-8")


def synchronize_and_validate() -> None:
    run(sys.executable, "scripts/update_glossary.py", "--write")
    run(sys.executable, "scripts/update_navigation.py", "--write")
    run(sys.executable, "scripts/audit_learning_depth.py", "--all-docs")


def remove_temporary_closeout() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    start = workflow.find(START_MARKER)
    end = workflow.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        raise RuntimeError("Temporary workflow closeout markers were not found.")

    end += len(END_MARKER)
    if end < len(workflow) and workflow[end] == "\n":
        end += 1
    WORKFLOW.write_text(workflow[:start] + workflow[end:], encoding="utf-8")
    SCRIPT.unlink()


def commit_and_push(branch: str) -> None:
    run("git", "config", "user.name", "github-actions[bot]")
    run(
        "git",
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
    )
    run("git", "add", "-A")
    run("git", "commit", "-m", "docs(docker): close full section rewrite")
    run("git", "push", "origin", f"HEAD:{branch}")


def main() -> None:
    branch = checkout_head_branch()
    update_ledger()
    synchronize_and_validate()
    remove_temporary_closeout()
    commit_and_push(branch)


if __name__ == "__main__":
    main()
