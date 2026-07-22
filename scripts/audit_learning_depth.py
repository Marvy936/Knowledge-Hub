#!/usr/bin/env python3
"""Audit whether learning documentation explains concepts instead of only listing them.

The audit is intentionally heuristic. It does not declare technical correctness.
It identifies sections that deserve human review because they are likely too terse,
list-heavy, or introduce terminology without enough local explanation.

Default scope:
- authoritative learning articles listed in docs/NN-*/README.md
- optionally all Markdown files under docs/ with --all-docs

The script is standard-library only so it can run in local development and CI.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DEFAULT_REPORT = ROOT / "DOCUMENTATION-AUDIT.md"
DEFAULT_JSON = ROOT / "documentation-audit.json"

ORDERED_LINK_RE = re.compile(r"^\s*\d+\.\s+\[([^\]]+)\]\(([^)#]+\.md)\)\s*$")
HEADING_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$")
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^\s*```")
SENTENCE_END_RE = re.compile(r"[.!?](?:\s|$)")
WORD_RE = re.compile(r"[\wÀ-ž][\wÀ-ž+./:#-]*", re.UNICODE)
INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9-]{1,12}\b")
ENGLISH_TERM_RE = re.compile(
    r"\b(?:attestation|posture|workload|policy|identity|resource|scope|"
    r"enforcement|delegation|freshness|failure semantics|blast radius|"
    r"control plane|data plane|trust domain|step-up|risk signal|"
    r"availability|durability|reliability|burn rate|error budget)\b",
    re.IGNORECASE,
)

EXEMPT_HEADINGS = {
    "kontrolné otázky",
    "glossary impact",
    "primárne zdroje",
    "zdroje",
    "referencie",
    "navigácia",
    "anti-patterny",
    "typické chyby",
    "troubleshooting",
    "metrics",
    "governance",
    "stav",
}

EXEMPT_TITLE_PARTS = (
    "kontrolné otázky",
    "glossary",
    "primárne zdroje",
    "navigácia",
)

MECHANISM_MARKERS = (
    "funguje", "prebieha", "vyhodnot", "vytvor", "odosiela", "overuje",
    "používa", "číta", "zapisuje", "mapuje", "viaže", "porovnáva",
    "rozhoduje", "presadí", "zlyhá", "dependency", "boundary", "tok",
    "flow", "intern", "mechaniz", "pretože", "dôvod", "následne",
)

EXAMPLE_MARKERS = (
    "napríklad", "príklad", "predstavme", "v praxi", "scenár",
    "typicky", "konkrétne", "napr.", "ak ",
)

FAILURE_MARKERS = (
    "zlyh", "chyba", "rizik", "trade-off", "tradeoff", "limit",
    "nedostup", "stale", "comprom", "bypass", "nespráv", "failure",
    "výpad", "latency", "rollback", "incident",
)


@dataclass
class Finding:
    path: str
    section: str
    line: int
    severity: str
    rule: str
    detail: str
    score: int


@dataclass
class FileStats:
    path: str
    title: str
    words: int
    headings: int
    sections: int
    findings: int
    critical: int
    high: int
    medium: int
    low: int
    score: int


@dataclass
class Section:
    title: str
    level: int
    line: int
    lines: list[str]


def normalize_heading(value: str) -> str:
    value = re.sub(r"^\d+\.\s*", "", value.strip().lower())
    value = re.sub(r"[`*_]", "", value)
    return " ".join(value.split())


def strip_markdown(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[`*_>#|]", " ", text)
    return " ".join(text.split())


def word_count(text: str) -> int:
    return len(WORD_RE.findall(strip_markdown(text)))


def sentence_count(text: str) -> int:
    clean = strip_markdown(text)
    if not clean:
        return 0
    count = len(SENTENCE_END_RE.findall(clean))
    if count == 0 and word_count(clean) >= 8:
        return 1
    return count


def authoritative_articles() -> list[Path]:
    result: list[Path] = []
    for readme in sorted(DOCS.glob("[0-9][0-9]-*/README.md")):
        for line in readme.read_text(encoding="utf-8").splitlines():
            match = ORDERED_LINK_RE.match(line)
            if not match:
                continue
            target = (readme.parent / match.group(2)).resolve()
            if target.name != "README.md":
                result.append(target)
    return result


def split_sections(lines: list[str]) -> tuple[str, list[Section]]:
    title = ""
    sections: list[Section] = []
    current: Section | None = None
    in_fence = False

    for number, line in enumerate(lines, start=1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
        if in_fence:
            if current:
                current.lines.append(line)
            continue

        if line.startswith("# ") and not title:
            title = strip_markdown(line[2:].strip())
            continue

        match = HEADING_RE.match(line)
        if match:
            if current:
                sections.append(current)
            current = Section(
                title=strip_markdown(match.group(2)),
                level=len(match.group(1)),
                line=number,
                lines=[],
            )
        elif current:
            current.lines.append(line)

    if current:
        sections.append(current)

    return title, sections


def section_content(section: Section) -> dict[str, object]:
    prose_lines: list[str] = []
    bullets: list[str] = []
    code_lines: list[str] = []
    meaningful: list[str] = []
    in_fence = False

    for line in section.lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--") or stripped == "---":
            continue
        if in_fence:
            code_lines.append(stripped)
            meaningful.append("code")
            continue
        bullet = BULLET_RE.match(line)
        if bullet:
            bullets.append(strip_markdown(bullet.group(1)))
            meaningful.append("bullet")
        else:
            prose_lines.append(strip_markdown(stripped))
            meaningful.append("prose")

    prose = " ".join(p for p in prose_lines if p)
    all_text = " ".join(prose_lines + bullets)
    return {
        "prose": prose,
        "bullets": bullets,
        "code_lines": code_lines,
        "meaningful": meaningful,
        "prose_words": word_count(prose),
        "all_words": word_count(all_text),
        "sentences": sentence_count(prose),
    }


def introduced_terms(data: dict[str, object]) -> list[str]:
    prose = str(data["prose"])
    bullets = list(data["bullets"])
    terms: list[str] = []

    bullet_text = " ".join(bullets)
    for match in INLINE_CODE_RE.findall(bullet_text):
        if 1 <= len(match.split()) <= 5 and match.lower() not in prose.lower():
            terms.append(match)

    for match in ACRONYM_RE.findall(bullet_text):
        if match not in prose and len(match) > 1:
            terms.append(match)

    for match in ENGLISH_TERM_RE.findall(bullet_text):
        if match.lower() not in prose.lower():
            terms.append(match)

    clean: list[str] = []
    seen: set[str] = set()
    for term in terms:
        key = term.lower().strip()
        if key and key not in seen:
            seen.add(key)
            clean.append(term.strip())
    return clean[:8]


def is_exempt(section: Section) -> bool:
    normalized = normalize_heading(section.title)
    return (
        normalized in EXEMPT_HEADINGS
        or any(part in normalized for part in EXEMPT_TITLE_PARTS)
        or normalized.startswith("mini príklad")
    )


def audit_section(path: Path, section: Section) -> list[Finding]:
    if is_exempt(section):
        return []

    data = section_content(section)
    prose_words = int(data["prose_words"])
    all_words = int(data["all_words"])
    sentences = int(data["sentences"])
    bullets = list(data["bullets"])
    meaningful = list(data["meaningful"])
    prose = str(data["prose"])
    lower = prose.lower()
    findings: list[Finding] = []

    def add(severity: str, rule: str, detail: str, score: int) -> None:
        findings.append(
            Finding(
                path=path.relative_to(ROOT).as_posix(),
                section=section.title,
                line=section.line,
                severity=severity,
                rule=rule,
                detail=detail,
                score=score,
            )
        )

    if all_words == 0:
        add("critical", "empty-section", "Sekcia nemá vysvetľovací obsah.", 12)
        return findings

    if meaningful and meaningful[0] in {"bullet", "code"} and prose_words < 35:
        add(
            "high",
            "list-first-introduction",
            "Sekcia začína zoznamom alebo kódom bez dostatočného úvodného mentálneho modelu.",
            8,
        )

    if len(bullets) >= 4 and prose_words < 35:
        add(
            "critical",
            "outline-instead-of-explanation",
            f"{len(bullets)} odrážok je podopretých iba {prose_words} slovami súvislého vysvetlenia.",
            12,
        )
    elif len(bullets) >= 6 and prose_words < 70:
        add(
            "high",
            "list-heavy-section",
            f"{len(bullets)} odrážok a iba {prose_words} slov súvislého vysvetlenia.",
            8,
        )

    if prose_words < 28 and bullets:
        add(
            "high",
            "thin-concept-section",
            "Konceptuálna sekcia má menej než 28 slov súvislého výkladu.",
            7,
        )
    elif prose_words < 45 and bullets:
        add(
            "medium",
            "short-concept-section",
            "Konceptuálna sekcia má menej než 45 slov súvislého výkladu.",
            4,
        )

    if sentences <= 1 and bullets and prose_words < 55:
        add(
            "medium",
            "single-sentence-explanation",
            "Jedna vysvetľovacia veta pravdepodobne nestačí na definíciu, mechanizmus a význam zoznamu.",
            4,
        )

    if all_words >= 45 and not any(marker in lower for marker in MECHANISM_MARKERS):
        add(
            "low",
            "mechanism-not-explicit",
            "Sekcia nespomína zreteľný mechanizmus, tok, rozhodovanie alebo internú väzbu.",
            2,
        )

    if all_words >= 55 and not any(marker in lower for marker in EXAMPLE_MARKERS):
        add(
            "low",
            "example-not-explicit",
            "Sekcia nemá zreteľný konkrétny príklad alebo praktický scenár.",
            1,
        )

    if all_words >= 70 and not any(marker in lower for marker in FAILURE_MARKERS):
        add(
            "low",
            "failure-mode-not-explicit",
            "Sekcia nemá zreteľnú hranicu, trade-off alebo failure mode.",
            1,
        )

    terms = introduced_terms(data)
    if terms and prose_words < 60:
        add(
            "high" if len(terms) >= 4 else "medium",
            "term-before-explanation",
            "Pojmy sa objavujú najmä v odrážkach bez lokálneho vysvetlenia: "
            + ", ".join(f"`{term}`" for term in terms),
            7 if len(terms) >= 4 else 4,
        )

    return findings


def audit_file(path: Path) -> tuple[FileStats, list[Finding]]:
    text = path.read_text(encoding="utf-8")
    title, sections = split_sections(text.splitlines())
    findings: list[Finding] = []
    for section in sections:
        findings.extend(audit_section(path, section))

    counts = Counter(f.severity for f in findings)
    score = sum(f.score for f in findings)
    stats = FileStats(
        path=path.relative_to(ROOT).as_posix(),
        title=title or path.stem,
        words=word_count(text),
        headings=len(sections),
        sections=len(sections),
        findings=len(findings),
        critical=counts["critical"],
        high=counts["high"],
        medium=counts["medium"],
        low=counts["low"],
        score=score,
    )
    return stats, findings


def grade(stats: FileStats) -> str:
    if stats.critical >= 3 or stats.score >= 70:
        return "D"
    if stats.critical or stats.high >= 4 or stats.score >= 35:
        return "C"
    if stats.high or stats.score >= 15:
        return "B"
    return "A"


def markdown_report(files: list[FileStats], findings: list[Finding]) -> str:
    counts = Counter(f.severity for f in findings)
    grades = Counter(grade(item) for item in files)
    sections = sum(item.sections for item in files)
    total_words = sum(item.words for item in files)

    lines = [
        "# Documentation learning-depth audit",
        "",
        "> Generated by `scripts/audit_learning_depth.py`. "
        "This is a heuristic review queue, not proof of technical correctness.",
        "",
        "## Summary",
        "",
        f"- Audited authoritative articles: **{len(files)}**",
        f"- Audited conceptual sections: **{sections}**",
        f"- Total words: **{total_words:,}**",
        f"- Findings: **{len(findings)}** "
        f"(critical {counts['critical']}, high {counts['high']}, "
        f"medium {counts['medium']}, low {counts['low']})",
        f"- File grades: A {grades['A']}, B {grades['B']}, "
        f"C {grades['C']}, D {grades['D']}",
        "",
        "## Interpretation",
        "",
        "- **Critical** usually means a heading is functioning as an outline: very little prose followed by several bullets.",
        "- **High** identifies thin conceptual explanations, list-first introductions, or terminology introduced mainly inside lists.",
        "- **Medium** identifies sections that likely need another paragraph, definitions, or a worked example.",
        "- **Low** is a review hint for an absent explicit mechanism, example, or failure boundary; it can be a false positive.",
        "",
        "The target is not to remove lists. A list should summarize a model that the surrounding prose has already explained.",
        "",
        "## Highest-priority files",
        "",
        "| Grade | Score | Critical | High | Medium | Low | Words | File |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]

    for item in sorted(files, key=lambda x: (-x.score, x.path)):
        lines.append(
            f"| {grade(item)} | {item.score} | {item.critical} | {item.high} | "
            f"{item.medium} | {item.low} | {item.words} | `{item.path}` |"
        )

    lines.extend(["", "## Critical and high findings", ""])

    important = [f for f in findings if f.severity in {"critical", "high"}]
    if not important:
        lines.append("No critical or high findings.")
    else:
        by_path: dict[str, list[Finding]] = defaultdict(list)
        for finding in sorted(
            important,
            key=lambda x: (-x.score, x.path, x.line, x.rule),
        ):
            by_path[finding.path].append(finding)

        for path, items in by_path.items():
            lines.extend(["", f"### `{path}`", ""])
            for finding in items:
                lines.append(
                    f"- **{finding.severity.upper()}** line {finding.line}, "
                    f"`{finding.rule}` — **{finding.section}**: {finding.detail}"
                )

    lines.extend([
        "",
        "## All findings by rule",
        "",
        "| Rule | Critical | High | Medium | Low | Total |",
        "|---|---:|---:|---:|---:|---:|",
    ])

    by_rule: dict[str, Counter[str]] = defaultdict(Counter)
    for finding in findings:
        by_rule[finding.rule][finding.severity] += 1
    for rule, counter in sorted(
        by_rule.items(),
        key=lambda item: (-sum(item[1].values()), item[0]),
    ):
        total = sum(counter.values())
        lines.append(
            f"| `{rule}` | {counter['critical']} | {counter['high']} | "
            f"{counter['medium']} | {counter['low']} | {total} |"
        )

    lines.extend([
        "",
        "## Required remediation pattern",
        "",
        "For each critical or high conceptual section:",
        "",
        "1. Add a short definition and state the problem the concept solves.",
        "2. Explain the mechanism or decision flow in connected prose.",
        "3. Explain unfamiliar terms before or where they first appear.",
        "4. Keep bullets as a summary; use `term — explanation` when each item has distinct semantics.",
        "5. Add at least one concrete example, boundary, trade-off, or failure mode where relevant.",
        "6. Cross-link a prior authoritative chapter when a full re-explanation would be redundant, but include a short local reminder.",
        "",
        "See [`AUTHORING-GUIDE.md`](AUTHORING-GUIDE.md).",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--all-docs",
        action="store_true",
        help="audit every docs/**/*.md file except section READMEs",
    )
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero when critical findings exist",
    )
    args = parser.parse_args()

    paths = (
        sorted(p for p in DOCS.rglob("*.md") if p.name != "README.md")
        if args.all_docs
        else authoritative_articles()
    )
    missing = [p for p in paths if not p.exists()]
    if missing:
        for path in missing:
            print(f"missing article: {path.relative_to(ROOT)}", file=sys.stderr)
        return 2

    files: list[FileStats] = []
    findings: list[Finding] = []
    for path in paths:
        stats, file_findings = audit_file(path)
        files.append(stats)
        findings.extend(file_findings)

    args.report.write_text(markdown_report(files, findings), encoding="utf-8", newline="\n")
    args.json.write_text(
        json.dumps(
            {
                "files": [asdict(item) | {"grade": grade(item)} for item in files],
                "findings": [asdict(item) for item in findings],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    counts = Counter(f.severity for f in findings)
    print(
        f"audited {len(files)} files; "
        f"critical={counts['critical']} high={counts['high']} "
        f"medium={counts['medium']} low={counts['low']}"
    )
    if args.check and counts["critical"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
