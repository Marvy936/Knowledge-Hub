from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from section_04_connected_prose_blocks import BLOCKS as SECTION_04_BLOCKS
from section_05_connected_prose_blocks import BLOCKS as SECTION_05_BLOCKS

ROOT = Path(__file__).resolve().parents[1]
TEMP_PATHS = [
    Path("scripts/section_04_connected_prose_blocks.py"),
    Path("scripts/section_05_connected_prose_blocks.py"),
    Path("scripts/close_sections_04_05_connected_prose.py"),
    Path(".github/workflows/sections-04-05-connected-prose-final.yml"),
]

BLOCK_RE = re.compile(
    r"(?ms)^## Doplnenie výkladu:[^\n]*\n\n.*?(?=^## )"
)


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def replace_block(path: str, replacement: str) -> None:
    full_path = ROOT / path
    text = full_path.read_text(encoding="utf-8")
    updated, count = BLOCK_RE.subn(replacement.rstrip() + "\n\n", text, count=1)
    if count != 1:
        raise AssertionError(f"{path}: expected one explanation block, replaced {count}")
    if "## Doplnenie výkladu:" in updated:
        raise AssertionError(f"{path}: retired explanation heading remains")
    full_path.write_text(updated, encoding="utf-8")


def update_readmes() -> None:
    path04 = ROOT / "docs/04-testing-and-quality/README.md"
    text04 = path04.read_text(encoding="utf-8")
    text04, count04 = re.subn(
        r"(?ms)^## Rozšírený výklad pojmov, kódu a výsledkov\n\n.*?(?=^## Čo má čitateľ po sekcii vedieť)",
        "## Výklad pojmov je súčasťou príbehu kapitoly\n\n"
        "Každá kapitola vysvetľuje odborné pojmy, setup, príkazy a výsledky súvislými odsekmi priamo pred scenárom alebo failure, v ktorom sa používajú. Nový text nie je oddelený ako slovník ani postavený na opisných odrážkach. Zoznamy zostávajú iba tam, kde sú prirodzeným porovnaním, acceptance contractom, kontrolnými otázkami alebo inventárom evidence.\n\n"
        "Kód a konfigurácia sú vložené pri mechanizme, ktorý demonštrujú. Nasledujúci text vždy vysvetľuje, čo sa pri vykonaní stane, čo výsledok preukazuje a ktorú časť runtime alebo business správania ešte treba overiť iným testom.\n\n",
        text04,
        count=1,
    )
    if count04 != 1:
        raise AssertionError(f"Section 04 README replacement count: {count04}")
    path04.write_text(text04, encoding="utf-8")

    path05 = ROOT / "docs/05-ci-cd-and-release/README.md"
    text05 = path05.read_text(encoding="utf-8")
    text05, count05 = re.subn(
        r"(?ms)^## Rozšírený výklad pojmov, príkazov a release dôkazov\n\n.*?(?=^## Cieľ zvládnutia)",
        "## Výklad pojmov je integrovaný do release lifecycle-u\n\n"
        "Integration candidate, pipeline execution, artifact, cache, digest, promotion, cohort, rollout a recovery sú vysvetlené súvislým textom v tom kroku lifecycle-u, kde menia stav alebo podporujú rozhodnutie. Príkazy a controller transitions sú spojené s vysvetlením vstupu, vykonanej mutácie, read-backu a dôkaznej hranice.\n\n"
        "Opisné odrážkové dodatky boli nahradené explicitne napísanými odbornými podkapitolami. Zoznamy zostávajú pri presných porovnaniach deployment stratégií, acceptance podmienkach, zdrojoch a evidence inventories; nenahrádzajú základný výklad.\n\n",
        text05,
        count=1,
    )
    if count05 != 1:
        raise AssertionError(f"Section 05 README replacement count: {count05}")
    path05.write_text(text05, encoding="utf-8")


def update_ledger() -> None:
    path = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
    text = path.read_text(encoding="utf-8")
    row04 = (
        "| `04-testing-and-quality` — Testing and Software Quality | 15/15 connected prose and explanation-depth revalidation | Ready for user review | 2026-08-01 | "
        "Všetkých 15 kapitol zachováva pôvodný odborný základ a používa explicitne napísaný connected prose pre oracle, test scope, API/E2E boundaries, performance, security, coverage, doubles, flakiness, shift-left/right a chaos. Posledné opisné explanation bloky boli nahradené prirodzenými podkapitolami; kód je vysvetlený mechanizmom, read-backom a dôkaznou hranicou. Navigation, glossary a full documentation audit boli synchronizované. |"
    )
    row05 = (
        "| `05-ci-cd-and-release` — CI/CD and Release Engineering | 24/24 connected prose, practical and release-evidence revalidation | Ready for user review | 2026-08-01 | "
        "Všetkých 23 koncepčných kapitol používa explicitne napísaný connected prose pre integration candidate, pipeline/runner, trigger/artifact/cache, promotion, gates, resolved graph, fan-in, checksum/digest/signature/provenance, SemVer, deployment strategies, experiments, flags, recovery a database compatibility. Executable walkthrough zostal zachovaný. Opisné dodatky už nie sú odrážkovým slovníkom. Navigation, glossary a full documentation audit boli synchronizované. |"
    )
    text, count04 = re.subn(r"(?m)^\| `04-testing-and-quality`.*$", row04, text)
    text, count05 = re.subn(r"(?m)^\| `05-ci-cd-and-release`.*$", row05, text)
    if count04 != 1 or count05 != 1:
        raise AssertionError(f"Ledger replacements: section04={count04}, section05={count05}")
    path.write_text(text, encoding="utf-8")


def validate_replacements() -> None:
    all_blocks = {**SECTION_04_BLOCKS, **SECTION_05_BLOCKS}
    if len(SECTION_04_BLOCKS) != 15:
        raise AssertionError(f"Expected 15 Section 04 blocks, got {len(SECTION_04_BLOCKS)}")
    if len(SECTION_05_BLOCKS) != 23:
        raise AssertionError(f"Expected 23 Section 05 blocks, got {len(SECTION_05_BLOCKS)}")
    if len(all_blocks) != 38:
        raise AssertionError(f"Expected 38 unique blocks, got {len(all_blocks)}")

    for path, replacement in all_blocks.items():
        if replacement.count("\n\n") < 3:
            raise AssertionError(f"{path}: replacement is too short for connected prose")
        if re.search(r"(?m)^[-*+] ", replacement):
            raise AssertionError(f"{path}: replacement contains a top-level bullet list")
        replace_block(path, replacement)


def remove_temp_files() -> None:
    for path in TEMP_PATHS:
        full_path = ROOT / path
        if not full_path.exists():
            raise AssertionError(f"Temporary file missing before cleanup: {path}")
        full_path.unlink()


def main() -> None:
    branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    if not branch:
        raise RuntimeError("Unable to resolve branch")

    run("git", "fetch", "origin", branch)
    run("git", "checkout", "-B", branch, f"origin/{branch}")

    validate_replacements()
    update_readmes()
    update_ledger()

    python_bin = os.environ.get("PYTHON_BIN", "python3")
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

    remove_temp_files()

    run("git", "config", "user.name", "github-actions[bot]")
    run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    run(
        "git",
        "add",
        "docs/04-testing-and-quality",
        "docs/05-ci-cd-and-release",
        "DOCUMENTATION-REVIEW-STATUS.md",
        "GLOSSARY.md",
        "glossary",
        "DOCUMENTATION-AUDIT.md",
        "documentation-audit.json",
        *(str(path) for path in TEMP_PATHS),
    )
    run("git", "commit", "-m", "docs: integrate testing and release explanations into prose")
    run("git", "push", "origin", f"HEAD:{branch}")


if __name__ == "__main__":
    main()
