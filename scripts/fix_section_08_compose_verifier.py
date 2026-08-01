from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
WORKFLOW = REPOSITORY / ".github/workflows/knowledge-navigation.yml"
SCRIPT = Path(__file__).resolve()
START_MARKER = "      # SECTION08_VERIFIER_FIX_START"
END_MARKER = "      # SECTION08_VERIFIER_FIX_END"

FILES = [
    REPOSITORY / "docs/08-container-fundamentals-and-docker/docker-compose.md",
    REPOSITORY / "docs/08-container-fundamentals-and-docker/docker-practical-walkthrough.md",
]

OLD = '''    command:
      - sh
      - -ec
      - |
        curl -fsS http://payments-api:8080/version
'''

NEW = '''    entrypoint: ["curl"]
    command: ["-fsS", "http://payments-api:8080/version"]
'''


def run(*args: str) -> None:
    subprocess.run(args, cwd=REPOSITORY, check=True)


def checkout_head_branch() -> str:
    branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    if not branch:
        raise RuntimeError("Unable to resolve pull-request head branch")
    run("git", "fetch", "origin", branch)
    run("git", "checkout", "-B", branch, f"origin/{branch}")
    return branch


def apply_replacements() -> None:
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        count = text.count(OLD)
        if count != 1:
            raise RuntimeError(f"Expected one verifier block in {path}, found {count}")
        text = text.replace(OLD, NEW)
        if path.name == "docker-practical-walkthrough.md":
            text = text.replace(
                "        published: ${HOST_PORT:-18080}\n",
                "        published: \"${HOST_PORT:-18080}\"\n",
                1,
            )
        path.write_text(text, encoding="utf-8")


def remove_temporary_files() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    start = workflow.find(START_MARKER)
    end = workflow.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        raise RuntimeError("Temporary workflow markers were not found")
    end += len(END_MARKER)
    if end < len(workflow) and workflow[end] == "\n":
        end += 1
    WORKFLOW.write_text(workflow[:start] + workflow[end:], encoding="utf-8")
    SCRIPT.unlink()


def main() -> None:
    branch = checkout_head_branch()
    apply_replacements()
    run(sys.executable, "scripts/update_glossary.py", "--write")
    run(sys.executable, "scripts/update_navigation.py", "--write")
    run(sys.executable, "scripts/audit_learning_depth.py", "--all-docs")
    remove_temporary_files()

    run("git", "config", "user.name", "github-actions[bot]")
    run(
        "git",
        "config",
        "user.email",
        "41898282+github-actions[bot]@users.noreply.github.com",
    )
    run("git", "add", "-A")
    run("git", "commit", "-m", "docs(docker): fix Compose verifier execution")
    run("git", "push", "origin", f"HEAD:{branch}")


if __name__ == "__main__":
    main()
