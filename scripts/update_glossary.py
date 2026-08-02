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
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GLOSSARY = ROOT / "GLOSSARY.md"
FRAGMENTS = ROOT / "glossary"
ENTRY_RE = re.compile(r"(?ms)^##\s+(.+?)\n(.*?)(?=^##\s+|\Z)")


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


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write synchronized glossary")
    mode.add_argument("--check", action="store_true", help="fail when synchronization is needed")
    args = parser.parse_args()

    try:
        current = GLOSSARY.read_text(encoding="utf-8")
        desired = render()
    except (OSError, ValueError) as exc:
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
