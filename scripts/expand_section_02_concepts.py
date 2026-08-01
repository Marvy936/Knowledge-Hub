from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRANCH = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
if not BRANCH:
    raise SystemExit("Unable to resolve pull request branch")

START = "<!-- CONCEPT-FIRST:START -->"
END = "<!-- CONCEPT-FIRST:END -->"


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=REPO, check=True)


def load_blocks(parts_dir: Path) -> dict[str, str]:
    blocks: dict[str, str] = {}
    for part in sorted(parts_dir.glob("part-*.txt")):
        current: str | None = None
        lines: list[str] = []
        for line in part.read_text(encoding="utf-8").splitlines():
            if line.startswith("@@ "):
                if current is not None:
                    blocks[current] = "\n".join(lines).strip()
                current = line[3:].strip()
                lines = []
            else:
                lines.append(line)
        if current is not None:
            blocks[current] = "\n".join(lines).strip()
    return blocks


run("git", "fetch", "origin", BRANCH)
run("git", "checkout", "-B", BRANCH, f"origin/{BRANCH}")

section = REPO / "docs/02-networking-and-web"
parts_dir = REPO / "scripts/section02_concept_parts"
blocks = load_blocks(parts_dir)
if len(blocks) != 16:
    raise RuntimeError(f"Expected 16 concept blocks, found {len(blocks)}")

for filename, block in blocks.items():
    target = section / filename
    if not target.is_file():
        raise RuntimeError(f"Missing target chapter: {target}")

    text = target.read_text(encoding="utf-8")
    if START in text:
        pattern = (
            rf"\n{{2}}{re.escape(START)}.*?{re.escape(END)}\n{{2}}"
            r"## Atlas scenár a praktické použitie\n\n"
        )
        text, count = re.subn(pattern, "\n\n", text, count=1, flags=re.DOTALL)
        if count != 1:
            raise RuntimeError(f"Unable to replace existing concept block in {filename}")

    title, rest = text.split("\n", 1)
    rest = rest.lstrip("\n")
    expanded = (
        f"{title}\n\n{START}\n{block}\n{END}\n\n"
        "## Atlas scenár a praktické použitie\n\n"
        f"{rest}"
    )
    target.write_text(expanded, encoding="utf-8")

readme_path = section / "README.md"
readme = readme_path.read_text(encoding="utf-8")
old_standard = (
    "Každá kapitola najprv položí konkrétnu otázku z rovnakého requestu a až potom vysvetlí "
    "protokol alebo mechanizmus. CLI, packet fields, konfigurácia a HTTP ukážky sú vložené "
    "priamo pri kroku, ktorý objasňujú. Po každom pozorovaní je uvedené, čo dôkaz potvrdzuje "
    "a kde sa jeho platnosť končí.\n\n"
    "Odrážky zostávajú iba pri krátkom inventári fields, stavov alebo acceptance podmienok. "
    "Hlavný výklad nesú súvislé odseky a jeden priebežný scenár. Incidenty používajú presnú "
    "flow identity, čas, direction a observation points; nekončia neurčitým záverom „bol problém v sieti“."
)
new_standard = (
    "Každá koncepčná kapitola najprv samostatne vysvetlí, čo protokol alebo mechanizmus je, "
    "aký problém rieši, ktoré identity a vrstvy stavu vlastní a ako funguje bez väzby na Atlas "
    "topológiu. Nasleduje jednoduchý neutrálny príklad a jasná hranica toho, čo daný dôkaz "
    "potvrdzuje. Až potom kapitola prejde k sekcii `Atlas scenár a praktické použitie`, kde sa "
    "model aplikuje na spoločný request, doplnia sa CLI, packet fields, konfigurácia, incident "
    "a recovery. Scenár je teda aplikáciou už vysvetleného modelu, nie jeho náhradou.\n\n"
    "Odrážky zostávajú iba pri krátkom inventári fields, stavov alebo acceptance podmienok. "
    "Hlavný výklad nesú súvislé odseky. Incidenty používajú presnú flow identity, čas, direction "
    "a observation points; nekončia neurčitým záverom „bol problém v sieti“."
)
if old_standard not in readme:
    raise RuntimeError("README standard paragraph not found")
readme_path.write_text(readme.replace(old_standard, new_standard, 1), encoding="utf-8")

ledger_path = REPO / "DOCUMENTATION-REVIEW-STATUS.md"
ledger = ledger_path.read_text(encoding="utf-8")
new_row = (
    "| `02-networking-and-web` — Networking and Web Fundamentals | "
    "17/17 concept-first full prose and practical revalidation | Ready for user review | "
    "2026-08-01 | Všetkých 16 koncepčných kapitol bolo po full prose rewritingu rozšírených "
    "podľa concept-first štandardu. Každá kapitola teraz najprv vysvetľuje definíciu protokolu "
    "alebo mechanizmu, problém, ktorý rieši, vlastnené identity/state, vnútorný dataplane alebo "
    "control model a neutrálny príklad; až potom nasleduje Atlas request, CLI/capture read-back, "
    "failure path a recovery. Rozšírenie pokrýva vrstvenie a encapsulation, Ethernet/VLAN/ARP/NDP, "
    "IPv4/IPv6 prefixy, route selection, TCP/UDP semantics, sockets, DNS, DHCP, NAT, firewall hooks, "
    "proxy trust boundaries, load-balancer eligibility, HTTP semantics, TLS/PKI, REST/WebSocket "
    "lifecycle a systematický preserve-first troubleshooting. Praktický namespace walkthrough "
    "zostáva záverečnou integráciou už vysvetlených mechanizmov. Navigation, glossary a full "
    "learning-depth audit boli znovu synchronizované. Sekcia je pripravená na používateľskú "
    "kontrolu, nie automaticky Accepted, Verified ani Stable. |"
)
ledger, count = re.subn(
    r"^\| `02-networking-and-web`[^\n]*$",
    new_row,
    ledger,
    count=1,
    flags=re.MULTILINE,
)
if count != 1:
    raise RuntimeError(f"Section 02 ledger row: expected one match, found {count}")
ledger_path.write_text(ledger, encoding="utf-8")

for filename in blocks:
    text = (section / filename).read_text(encoding="utf-8")
    if text.count(START) != 1 or text.count(END) != 1:
        raise RuntimeError(f"Concept marker mismatch in {filename}")
    if "## Atlas scenár a praktické použitie" not in text:
        raise RuntimeError(f"Atlas section missing in {filename}")

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
      - name: Expand Section 02 concept-first explanations
        if: github.event_name == 'pull_request'
        shell: bash
        run: |
          set -euo pipefail
          "$PYTHON_BIN" scripts/expand_section_02_concepts.py
"""
if workflow.count(temporary_step) != 1:
    raise RuntimeError("Temporary workflow step was not found exactly once")
workflow_path.write_text(workflow.replace(temporary_step, "", 1), encoding="utf-8")

shutil.rmtree(parts_dir)
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
    print("Section 02 concept expansion produced no changes")
    raise SystemExit(0)
if status.returncode != 1:
    raise RuntimeError("Unable to inspect staged changes")

run("git", "commit", "-m", "docs: expand Section 02 concept-first explanations")
run("git", "push", "origin", f"HEAD:{BRANCH}")
