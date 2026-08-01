from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRANCH = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
if not BRANCH:
    raise SystemExit("Unable to resolve pull request branch")

SECTIONS = {
    "02": REPO / "docs/02-networking-and-web",
    "03": REPO / "docs/03-git-and-automation",
    "04": REPO / "docs/04-testing-and-quality",
}
EXPECTED_CONCEPT_FILES = {"02": 16, "03": 14, "04": 15}


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=REPO, check=True)


def replace_section(text: str, heading: str, replacement: str) -> str:
    pattern = re.compile(
        rf"(?ms)^## {re.escape(heading)}\n.*?(?=^## |^<!-- KNOWLEDGE-NAVIGATION:START -->|\Z)"
    )
    updated, count = pattern.subn(replacement.rstrip() + "\n\n", text, count=1)
    if count != 1:
        raise RuntimeError(f"Expected one '{heading}' section, found {count}")
    return updated


def flatten_concept_intro(text: str, path: Path) -> str:
    start = "<!-- CONCEPT-FIRST:START -->"
    end = "<!-- CONCEPT-FIRST:END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        raise RuntimeError(f"Unexpected concept marker count in {path}")

    before, remainder = text.split(start, 1)
    block, after = remainder.split(end, 1)
    lines = block.strip().splitlines()
    if not lines or not lines[0].startswith("## "):
        raise RuntimeError(f"Concept block in {path} does not start with an H2")

    # Recent Keycloak/CI/CD/Helm/Docker chapters begin with prose directly below H1.
    # Remove the artificial concept heading and keep its explanatory paragraphs as
    # the natural chapter introduction.
    intro = "\n".join(lines[1:]).strip()
    text = before.rstrip() + "\n\n" + intro + "\n\n" + after.lstrip()

    for wrapper in (
        "## Atlas scenár a praktické použitie",
        "## Detailný výklad a Atlas aplikácia",
    ):
        text = re.sub(rf"(?m)^{re.escape(wrapper)}\n+", "", text, count=1)

    return text


def remove_metadata(text: str, path: Path) -> str:
    pattern = re.compile(
        r"(?ms)^## Metadata\n.*?(?=^## |^<!-- KNOWLEDGE-NAVIGATION:START -->|\Z)"
    )
    updated, count = pattern.subn("", text, count=1)
    if count > 1:
        raise RuntimeError(f"Expected at most one Metadata section in {path}, found {count}")
    return updated


def normalize(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.rstrip() + "\n"


run("git", "fetch", "origin", BRANCH)
run("git", "checkout", "-B", BRANCH, f"origin/{BRANCH}")

# Flatten the artificial concept-first wrapper in every conceptual chapter.
for section_id, section_dir in SECTIONS.items():
    concept_files = []
    for path in sorted(section_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        if "<!-- CONCEPT-FIRST:START -->" not in text:
            continue
        concept_files.append(path)
        text = flatten_concept_intro(text, path)
        if section_id == "04":
            text = remove_metadata(text, path)
        path.write_text(normalize(text), encoding="utf-8")

    expected = EXPECTED_CONCEPT_FILES[section_id]
    if len(concept_files) != expected:
        raise RuntimeError(
            f"Section {section_id}: expected {expected} concept files, found {len(concept_files)}"
        )

# Replace README authoring guidance with the integrated prose model.
readme_02 = SECTIONS["02"] / "README.md"
text = readme_02.read_text(encoding="utf-8")
text = replace_section(
    text,
    "Výkladový štandard",
    """## Výkladový štandard

Každá kapitola začína priamo súvislým vysvetlením protokolu alebo mechanizmu: čo rieši, aké identity a state vlastní, ako sa rozhodnutie vykonáva a kde sa dá pozorovať. Atlas request sa do výkladu zapája priebežne ako konkrétna aplikácia všeobecného modelu; nevytvára sa samostatná školská vrstva s learning statusom alebo metadata blokom.

CLI, packet fields, konfigurácia a HTTP ukážky sú vložené pri mechanizme, ktorý objasňujú. Kapitola potom prirodzene pokračuje cez dôkaznú hranicu, konkrétny incident, competing hypotheses, recovery a overenie pôvodného business outcome-u. Odrážky zostávajú iba pri krátkom inventári fields, stavov alebo acceptance podmienok.

Sekcia dôsledne rozlišuje hostname a DNS answer, IP packet a route, transportný flow, socket a process, TLS peer identity, HTTP request a business operáciu. Proxy alebo NAT môže vytvoriť novú flow identity a retry môže vytvoriť viac requestov pre jednu používateľskú operáciu, preto sa každý dôkaz viaže na presný subject a čas.""",
)
text = text.replace("concept-first full prose", "integrated full prose")
readme_02.write_text(normalize(text), encoding="utf-8")

readme_03 = SECTIONS["03"] / "README.md"
text = readme_03.read_text(encoding="utf-8")
text = replace_section(
    text,
    "Výkladový štandard",
    """## Výkladový štandard

Každá kapitola začína priamo výkladom Git alebo automation mechanizmu. Najprv vysvetlí objektový alebo execution model, mutable a immutable state, dôsledok operácie a hranicu dôkazu. Change `ORD-8421` sa objavuje priebežne ako konkrétna aplikácia a diagnostický subject; nie je oddelený umelým nadpisom ani learning metadata blokom.

Príkazy sú umiestnené pri stave, ktorý čítajú alebo menia. Po každej operácii nasleduje read-back, vysvetlenie toho, čo výsledok preukazuje, a failure alebo recovery path. Pri Git histórii sa oddeľuje snapshot, commit identity, ref a remote state. Pri automatizácii sa oddeľuje source configuration, observed state, plan, mutation a verified runtime outcome.

Záverečný walkthrough zostáva integráciou už vysvetlených mechanizmov: nepoužíva sa ako náhrada definície, ale ako ich súvislé vykonanie od repository initialization po idempotentný apply a no-op verification.""",
)
text = text.replace("concept-first full prose", "integrated full prose")
readme_03.write_text(normalize(text), encoding="utf-8")

readme_04 = SECTIONS["04"] / "README.md"
text = readme_04.read_text(encoding="utf-8")
text = replace_section(
    text,
    "Výkladový štandard",
    """## Výkladový štandard

Každá kapitola začína priamo výkladom testovacieho typu, techniky alebo stratégie. Vysvetľuje subject, scope, failure mode, potrebnú fidelity, oracle a hranicu dôkazu a následne tieto pojmy priebežne aplikuje na Atlas Orders. Kapitola je jeden súvislý odborný text bez samostatnej learning alebo metadata vrstvy.

Konkrétne testy, konfigurácia, výsledky a failure artifacts sa objavujú pri rozhodnutí, ktoré podporujú. Výklad pokračuje od všeobecného mechanizmu cez experiment alebo test contract k Atlas incidentu, diagnosis, recovery a skoršiemu controlu. Inventáre, matice a checklisty zostávajú iba tam, kde presne porovnávajú scope, evidence alebo acceptance podmienky.""",
)
text = replace_section(
    text,
    "Cieľ zvládnutia",
    """## Čo má čitateľ po sekcii vedieť

Čitateľ má vedieť začať od rizika alebo failure mode-u a zvoliť najnižší test scope, ktorý poskytne dostatočný dôkaz. Musí odlíšiť verification od validation, pomenovať oracle a jeho false-positive alebo false-negative riziko a vysvetliť, pre ktorý artifact, prostredie, konfiguráciu a čas výsledok platí.

Má vedieť navrhnúť unit, integration, component, contract, API, E2E, acceptance, smoke a regression kontroly bez zamieňania ich boundaries. Pri performance experimente musí vedieť definovať workload model, tail-latency a saturation oracle; pri security a infrastructure testoch zase threat, control, plan a runtime evidence. Coverage, static analysis a quality gate má interpretovať ako ohraničený signál, nie ako priamy dôkaz kvality.

Pri nedeterministických alebo produkčných kontrolách má vedieť zachovať first-attempt evidence, izolovať test data, rozlíšiť flaky test od skutočného defectu a bezpečne používať shift-right a chaos experimenty. Výsledok sa uzatvára až recovery, business reconciliation a trvalým regression controlom.""",
)
text = replace_section(
    text,
    "Stav",
    """## Stav

Všetkých pätnásť kapitol je po integrovanom full prose rewritingu pripravených na používateľskú kontrolu. Tento stav neznamená automatické používateľské schválenie ani runtime overenie každého nástroja a experimentu.""",
)
text = text.replace("concept-first full prose", "integrated full prose")
readme_04.write_text(normalize(text), encoding="utf-8")

# Update the central ledger without retaining the temporary concept-first label.
ledger_path = REPO / "DOCUMENTATION-REVIEW-STATUS.md"
ledger = ledger_path.read_text(encoding="utf-8")
ledger = re.sub(
    r"^\| `02-networking-and-web`[^\n]*$",
    "| `02-networking-and-web` — Networking and Web Fundamentals | 17/17 integrated full prose and practical revalidation | Ready for user review | 2026-08-01 | Všetkých 16 koncepčných kapitol používa jeden súvislý prose flow bez learning metadát, concept markerov alebo oddeleného Atlas wrappera. Každá kapitola začína priamo vysvetlením protokolu alebo mechanizmu, priebežne zapája Atlas request, CLI alebo capture evidence a pokračuje cez incident, recovery a business verification. Praktický namespace walkthrough zostáva záverečnou integráciou. Navigation, glossary a full learning-depth audit boli znovu synchronizované. |",
    ledger,
    count=1,
    flags=re.MULTILINE,
)
ledger = re.sub(
    r"^\| `03-git-and-automation`[^\n]*$",
    "| `03-git-and-automation` — Git and Automation Basics | 15/15 integrated full prose and practical revalidation | Ready for user review | 2026-08-01 | Všetkých 14 koncepčných kapitol používa jeden súvislý prose flow bez learning metadát, concept markerov alebo oddeleného Atlas wrappera. Objektový alebo execution model, neutrálne vysvetlenie, change `ORD-8421`, CLI read-back, incident a recovery sú integrované v jednej kapitole. Praktický walkthrough zostáva záverečným vykonaním už vysvetlených mechanizmov. Navigation, glossary a full learning-depth audit boli znovu synchronizované. |",
    ledger,
    count=1,
    flags=re.MULTILINE,
)
ledger = re.sub(
    r"^\| `04-testing-and-quality`[^\n]*$",
    "| `04-testing-and-quality` — Testing and Software Quality | 15/15 integrated full prose revalidation | Ready for user review | 2026-08-01 | Všetkých 15 kapitol používa jeden súvislý odborný prose flow bez learning alebo metadata vrstvy, concept markerov alebo pomocného nadpisu medzi výkladom a Atlas aplikáciou. Subject, scope, fidelity, oracle, evidence, Atlas experiment, failure, diagnosis a recovery sú vysvetlené v jednej prirodzenej kapitole. README už neobsahuje starú statusovú tabuľku. Navigation, glossary a full learning-depth audit boli znovu synchronizované. |",
    ledger,
    count=1,
    flags=re.MULTILINE,
)
ledger_path.write_text(normalize(ledger), encoding="utf-8")

# Hard gate against the retired chapter scaffolding.
banned = (
    "CONCEPT-FIRST",
    "## Metadata",
    "Status: Learning",
    "Úroveň: L2",
    "Level: L2",
    "## Atlas scenár a praktické použitie",
    "## Detailný výklad a Atlas aplikácia",
    "| Learning | L2 |",
)
for section_dir in SECTIONS.values():
    for path in sorted(section_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for token in banned:
            if token in text:
                raise RuntimeError(f"Retired structure '{token}' remains in {path}")
        if path.name != "README.md":
            lines = text.splitlines()
            first_content = next((line for line in lines[1:] if line.strip()), "")
            if first_content.startswith("## "):
                raise RuntimeError(f"Chapter {path} still starts with an artificial H2 instead of prose")

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
      - name: Clean Sections 02-04 prose structure
        if: github.event_name == 'pull_request'
        shell: bash
        run: |
          set -euo pipefail
          "$PYTHON_BIN" scripts/cleanup_sections_02_04_prose_structure.py
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
    "docs/02-networking-and-web",
    "docs/03-git-and-automation",
    "docs/04-testing-and-quality",
    ".github/workflows/knowledge-navigation.yml",
    "scripts",
)

status = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO)
if status.returncode == 0:
    print("Prose-structure cleanup produced no changes")
    raise SystemExit(0)
if status.returncode != 1:
    raise RuntimeError("Unable to inspect staged changes")

run("git", "commit", "-m", "docs: integrate prose structure in Sections 02-04")
run("git", "push", "origin", f"HEAD:{BRANCH}")
