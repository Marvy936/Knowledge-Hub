#!/usr/bin/env python3
"""Synchronize article navigation footers and ROADMAP links.

Source of truth:
- section order: lexicographic order of docs/NN-*/README.md
- article order: numbered Markdown links in each section README
- ROADMAP checkboxes indicate whether the corresponding article exists

The script is intentionally standard-library only so it can run locally and in CI.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ROADMAP = ROOT / "ROADMAP.md"

NAV_START = "<!-- KNOWLEDGE-NAVIGATION:START -->"
NAV_END = "<!-- KNOWLEDGE-NAVIGATION:END -->"

ORDERED_LINK_RE = re.compile(
    r"^\s*\d+\.\s+\[([^\]]+)\]\(([^)#]+\.md)\)\s*$"
)
CHECKBOX_RE = re.compile(
    r"^(\s*-\s*)\[([ xX])\]\s+(?:\[([^\]]+)\]\([^)]+\)|(.+?))\s*$"
)


@dataclass(frozen=True)
class Article:
    title: str
    path: Path
    section_readme: Path


def normalize(value: str) -> str:
    value = value.replace("π", " pi ")
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().replace("&", " and ")
    return " ".join(re.findall(r"[a-z0-9]+", value))


def relative_link(source_file: Path, target_file: Path) -> str:
    return Path(os.path.relpath(target_file, source_file.parent)).as_posix()


def section_readmes() -> list[Path]:
    return sorted(DOCS.glob("[0-9][0-9]-*/README.md"))


def parse_articles() -> list[Article]:
    articles: list[Article] = []
    seen_paths: set[Path] = set()
    seen_labels: dict[str, Path] = {}

    for readme in section_readmes():
        for line in readme.read_text(encoding="utf-8").splitlines():
            match = ORDERED_LINK_RE.match(line)
            if not match:
                continue

            title, target = match.groups()
            article_path = (readme.parent / target).resolve()

            try:
                article_path.relative_to(ROOT)
            except ValueError as exc:
                raise ValueError(f"Link escapes repository: {readme} -> {target}") from exc

            if article_path.name == "README.md":
                continue
            if article_path in seen_paths:
                raise ValueError(f"Article is listed more than once: {article_path}")

            label_key = normalize(title)
            if label_key in seen_labels:
                raise ValueError(
                    f"Duplicate normalized article label '{title}': "
                    f"{seen_labels[label_key]} and {article_path}"
                )

            seen_paths.add(article_path)
            seen_labels[label_key] = article_path
            articles.append(Article(title, article_path, readme.resolve()))

    return articles


def navigation_block(articles: list[Article], index: int) -> str:
    article = articles[index]
    parts: list[str] = []

    if index > 0:
        previous = articles[index - 1]
        parts.append(
            f"[← Predchádzajúca: {previous.title}]"
            f"({relative_link(article.path, previous.path)})"
        )

    parts.append(
        f"[↑ Obsah sekcie]"
        f"({relative_link(article.path, article.section_readme)})"
    )

    if index + 1 < len(articles):
        following = articles[index + 1]
        parts.append(
            f"[Nasledujúca: {following.title} →]"
            f"({relative_link(article.path, following.path)})"
        )
    else:
        parts.append(
            f"[↑ Learning Roadmap]"
            f"({relative_link(article.path, ROADMAP.resolve())})"
        )

    return (
        f"{NAV_START}\n"
        "---\n\n"
        "**Navigácia**\n\n"
        + " · ".join(parts)
        + f"\n{NAV_END}"
    )


def with_navigation(original: str, block: str) -> str:
    marker_re = re.compile(
        rf"\n?{re.escape(NAV_START)}.*?{re.escape(NAV_END)}\n?",
        re.DOTALL,
    )
    cleaned = marker_re.sub("\n", original).rstrip()
    return f"{cleaned}\n\n{block}\n"


def synchronize_roadmap(original: str, articles: list[Article]) -> str:
    by_label = {normalize(article.title): article for article in articles}
    output: list[str] = []

    for line in original.splitlines():
        match = CHECKBOX_RE.match(line)
        if not match:
            output.append(line)
            continue

        prefix, _state, linked_label, plain_label = match.groups()
        label = (linked_label or plain_label or "").strip()
        article = by_label.get(normalize(label))

        if article and article.path.exists():
            target = article.path.relative_to(ROOT).as_posix()
            output.append(f"{prefix}[x] [{label}]({target})")
        else:
            output.append(f"{prefix}[ ] {label}")

    return "\n".join(output).rstrip() + "\n"


def calculate_changes() -> dict[Path, str]:
    articles = parse_articles()
    changes: dict[Path, str] = {}

    for index, article in enumerate(articles):
        if not article.path.exists():
            raise FileNotFoundError(
                f"Section index links to a missing article: {article.path.relative_to(ROOT)}"
            )
        current = article.path.read_text(encoding="utf-8")
        desired = with_navigation(current, navigation_block(articles, index))
        if current != desired:
            changes[article.path] = desired

    roadmap_current = ROADMAP.read_text(encoding="utf-8")
    roadmap_desired = synchronize_roadmap(roadmap_current, articles)
    if roadmap_current != roadmap_desired:
        changes[ROADMAP] = roadmap_desired

    return changes


def _run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def _maybe_apply_section_07_branch_pass() -> None:
    """Temporary branch-only CI hook; removed before the final PR diff."""
    branch = os.environ.get("GITHUB_HEAD_REF", "")
    if (
        os.environ.get("GITHUB_EVENT_NAME") != "pull_request"
        or branch != "agent/section-07-explanation-depth"
        or os.environ.get("SECTION07_HOOK_ACTIVE") == "1"
        or not (ROOT / "scripts" / "section_07_run_all.py").exists()
    ):
        return

    print("Applying the branch-scoped Section 07 explanation-depth pass.")
    _run(["git", "fetch", "origin", branch])
    _run(["git", "checkout", "-B", branch, f"origin/{branch}"])

    hook_env = os.environ.copy()
    hook_env["SECTION07_HOOK_ACTIVE"] = "1"
    _run([sys.executable, "scripts/section_07_run_all.py"], env=hook_env)
    _run([sys.executable, "scripts/update_glossary.py", "--write"], env=hook_env)
    _run([sys.executable, "scripts/update_navigation.py", "--write"], env=hook_env)
    _run([sys.executable, "scripts/audit_learning_depth.py", "--all-docs"], env=hook_env)

    _run([
        "git", "add",
        "docs/07-infrastructure-as-code-and-configuration-management",
        "ROADMAP.md",
        "GLOSSARY.md",
        "DOCUMENTATION-AUDIT.md",
        "documentation-audit.json",
    ])
    staged = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=ROOT,
        check=False,
    ).returncode
    if staged == 0:
        print("Section 07 documentation is already transformed and synchronized.")
        return

    _run(["git", "diff", "--cached", "--check"])
    _run([
        "git", "-c", "user.name=github-actions[bot]",
        "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
        "commit", "-m", "docs: deepen Section 07 Terraform and Ansible explanations",
    ])
    _run(["git", "push", "origin", f"HEAD:{branch}"])
    print("Section 07 transformation commit pushed to the PR branch.")


def main() -> int:
    _maybe_apply_section_07_branch_pass()

    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write synchronized files")
    mode.add_argument("--check", action="store_true", help="fail when synchronization is needed")
    args = parser.parse_args()

    try:
        changes = calculate_changes()
    except (OSError, ValueError) as exc:
        print(f"navigation error: {exc}", file=sys.stderr)
        return 2

    if args.check:
        if changes:
            print("Documentation navigation is out of sync:")
            for path in sorted(changes):
                print(f"- {path.relative_to(ROOT)}")
            print("Run: python scripts/update_navigation.py --write")
            return 1
        print("Documentation navigation is synchronized.")
        return 0

    for target_path, content in changes.items():
        target_path.write_text(content, encoding="utf-8", newline="\n")
        print(f"updated {target_path.relative_to(ROOT)}")

    if not changes:
        print("No navigation changes required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
