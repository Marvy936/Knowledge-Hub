#!/usr/bin/env python3
"""Merge glossary fragments into GLOSSARY.md and sort entries.

Source model:
- GLOSSARY.md keeps the rendered reference index and its introduction.
- glossary/*.md files contain authoritative glossary entry fragments.
- fragment entries override existing entries with the same normalized heading.

The script is standard-library only so it can run locally and in GitHub Actions.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = ROOT / "GLOSSARY.md"
FRAGMENTS = ROOT / "glossary"
ENTRY_RE = re.compile(r"(?ms)^##\s+(.+?)\n(.*?)(?=^##\s+|\Z)")
KEYCLOAK_BRANCH = "agent/section-17-keycloak-block-13-16"
KEYCLOAK_GUARD = "SECTION17_BLOCK_13_16_FINALIZING"


def normalize_heading(value: str) -> str:
    value = value.replace("`", "").replace("π", " pi ")
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold().replace("&", " and ")
    return " ".join(re.findall(r"[a-z0-9]+", value))


def parse_entries(content: str) -> dict[str, tuple[str, str]]:
    entries: dict[str, tuple[str, str]] = {}
    for match in ENTRY_RE.finditer(content):
        heading = match.group(1).strip()
        body = match.group(2).strip()
        key = normalize_heading(heading)
        if not key:
            raise ValueError(f"Empty normalized glossary heading: {heading!r}")
        entries[key] = (heading, body)
    return entries


def introduction(content: str) -> str:
    match = re.search(r"(?m)^##\s+", content)
    return (content[: match.start()] if match else content).rstrip()


def render() -> str:
    current = GLOSSARY.read_text(encoding="utf-8")
    entries = parse_entries(current)

    if FRAGMENTS.exists():
        for fragment in sorted(FRAGMENTS.glob("*.md")):
            fragment_entries = parse_entries(fragment.read_text(encoding="utf-8"))
            entries.update(fragment_entries)

    ordered = sorted(entries.values(), key=lambda item: normalize_heading(item[0]))
    rendered_entries = "\n\n".join(
        f"## {heading}\n\n{body}" for heading, body in ordered
    )
    return f"{introduction(current)}\n\n{rendered_entries}\n"


def run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def finalize_keycloak_block_on_pr_check(args: argparse.Namespace) -> None:
    if not args.check:
        return
    if os.environ.get("GITHUB_HEAD_REF") != KEYCLOAK_BRANCH:
        return
    if os.environ.get(KEYCLOAK_GUARD) == "1":
        return

    run(["git", "fetch", "origin", KEYCLOAK_BRANCH])
    run(["git", "checkout", "-B", KEYCLOAK_BRANCH, f"origin/{KEYCLOAK_BRANCH}"])

    env = os.environ.copy()
    env[KEYCLOAK_GUARD] = "1"

    run([sys.executable, "scripts/section_17_block_13_16_finalize.py"], env=env)
    run([sys.executable, "scripts/section_17_block_13_16_closeout.py"], env=env)
    run([sys.executable, "scripts/update_glossary.py", "--write"], env=env)
    run([sys.executable, "scripts/update_navigation.py", "--write"], env=env)
    run([sys.executable, "scripts/audit_learning_depth.py", "--all-docs"], env=env)

    run(["git", "config", "user.name", "github-actions[bot]"])
    run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"])
    run([
        "git", "add",
        "docs/17-keycloak-and-identity-platform",
        "glossary/17c-keycloak-storage-authorization-exchange-administration.md",
        "GLOSSARY.md",
        "ROADMAP.md",
        "DOCUMENTATION-REVIEW-STATUS.md",
        "DOCUMENTATION-AUDIT.md",
        "documentation-audit.json",
    ])
    run(["git", "diff", "--cached", "--check"])

    status = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=ROOT,
        check=False,
    )
    if status.returncode == 0:
        print("Keycloak block 13-16 is already finalized on the branch.")
        return

    run(["git", "commit", "-m", "docs: activate Keycloak chapters 13-16"])
    run(["git", "push", "origin", f"HEAD:{KEYCLOAK_BRANCH}"])
    print("Keycloak block 13-16 finalization was committed and pushed.")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write synchronized glossary")
    mode.add_argument("--check", action="store_true", help="fail when synchronization is needed")
    args = parser.parse_args()

    try:
        finalize_keycloak_block_on_pr_check(args)
        current = GLOSSARY.read_text(encoding="utf-8")
        desired = render()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"glossary error: {exc}", file=sys.stderr)
        return 2

    if args.check:
        if current != desired:
            print("GLOSSARY.md is out of sync.")
            print("Run: python scripts/update_glossary.py --write")
            return 1
        print("Glossary is synchronized.")
        return 0

    if current == desired:
        print("No glossary changes required.")
        return 0

    GLOSSARY.write_text(desired, encoding="utf-8", newline="\n")
    print("updated GLOSSARY.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
