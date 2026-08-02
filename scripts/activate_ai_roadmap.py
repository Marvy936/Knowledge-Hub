from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ROOT_README = ROOT / "README.md"
ROADMAP = ROOT / "ROADMAP.md"
FUTURE = ROOT / "FUTURE-IDENTITY-AI-ROADMAP.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"

TODAY = "2026-08-02"
AI_START = "<!-- ACTIVE-AI-ROADMAP:START -->"
AI_END = "<!-- ACTIVE-AI-ROADMAP:END -->"

SECTIONS = [
    {
        "number": 18,
        "slug": "machine-learning-fundamentals",
        "title": "Machine Learning Fundamentals",
        "phase": "Fáza 7 — Machine Learning a MLOps",
        "source_heading": "Machine Learning Fundamentals",
        "next_title": "MLOps and ML Platforms",
        "purpose": (
            "Sekcia vysvetľuje machine learning z pohľadu DevOps, platform a operations roly. "
            "Cieľom nie je nahradiť matematický alebo data-science odbor, ale presne rozumieť tomu, "
            "aký dataset, feature contract, model artifact a evaluation verdict vzniká, čo daný dôkaz "
            "preukazuje a prečo sa offline úspech nemusí preniesť do produkčného outcome-u."
        ),
        "dependencies": [
            "Testing and Software Quality",
            "Databases and Distributed Systems",
            "Observability",
            "Security and Identity",
        ],
        "lab": "raw dataset → validation a preprocessing → baseline model → train/validation/test evaluation → experiment comparison → packaged inference artifact",
    },
    {
        "number": 19,
        "slug": "mlops-and-ml-platforms",
        "title": "MLOps and ML Platforms",
        "phase": "Fáza 7 — Machine Learning a MLOps",
        "source_heading": "MLOps and ML Platforms",
        "next_title": "LLM and GenAI Engineering",
        "purpose": (
            "Sekcia sleduje ML systém ako lifecycle dát, kódu, environmentu, experimentu, modelu, "
            "feature pipeline, deploymentu a produkčného feedbacku. Každý promotion alebo rollback "
            "musí byť viazaný na presný model artifact, dataset a feature generation, serving runtime, "
            "evaluation evidence a business acceptance."
        ),
        "dependencies": [
            "Machine Learning Fundamentals",
            "CI/CD and Release Engineering",
            "Kubernetes",
            "Observability",
            "GitOps and Platform Engineering",
        ],
        "lab": "Git + dataset version → pipeline validation → train a evaluate → MLflow tracking → registry promotion → containerized serving → canary deployment → monitoring a drift signal → controlled retraining",
    },
    {
        "number": 20,
        "slug": "llm-and-genai-engineering",
        "title": "LLM and GenAI Engineering",
        "phase": "Fáza 8 — LLM, GenAI a agentická automatizácia",
        "source_heading": "LLM and GenAI Engineering",
        "next_title": "AI Agents and Intelligent Automation",
        "purpose": (
            "Sekcia vysvetľuje LLM application lifecycle od modelu, tokenizácie, promptu a structured "
            "contractu cez retrieval, tool calling a inference serving až po evals, tracing, security, "
            "cost a production troubleshooting. Demo odpoveď nie je acceptance verdict; rozhoduje "
            "reprodukovateľný dataset, exact model/prompt/retrieval generation a merateľný outcome."
        ),
        "dependencies": [
            "Machine Learning Fundamentals",
            "MLOps and ML Platforms",
            "Security and Identity",
            "Observability",
            "Keycloak and Identity Platform",
        ],
        "lab": "versioned prompt alebo RAG corpus → model/retrieval execution → grounded structured answer → eval dataset → tracing, latency, security a cost verdict → controlled promotion",
    },
    {
        "number": 21,
        "slug": "ai-agents-and-intelligent-automation",
        "title": "AI Agents and Intelligent Automation",
        "phase": "Fáza 8 — LLM, GenAI a agentická automatizácia",
        "source_heading": "AI Agents and Intelligent Automation",
        "next_title": "Learning Roadmap",
        "purpose": (
            "Sekcia začína hranicou medzi deterministickým workflowom, probabilistickým komponentom "
            "a autonómnym agentom. Agentické rozhodovanie sa pripúšťa iba s explicitným state, tool "
            "contractom, least privilege, approval hranicou, side-effect identity, auditom, kill switchom "
            "a overiteľným recovery pathom."
        ),
        "dependencies": [
            "LLM and GenAI Engineering",
            "Git and Automation Basics",
            "CI/CD and Release Engineering",
            "SRE and Operations",
            "Keycloak and Identity Platform",
        ],
        "lab": "alert alebo ticket → deterministic enrichment → agentic diagnosis → read-only tools → evidence a confidence → human approval → bounded remediation tool → validation → audit trail a rollback",
    },
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def section_body(source: str, heading: str, next_heading: str | None) -> str:
    start_marker = f"## {heading}\n"
    start = source.find(start_marker)
    if start < 0:
        raise RuntimeError(f"Missing future-roadmap heading: {heading}")
    start += len(start_marker)
    if next_heading is None:
        end = source.find("# Cross-section flagship projekty", start)
    else:
        end = source.find(f"## {next_heading}\n", start)
    if end < 0:
        raise RuntimeError(f"Missing end boundary for future-roadmap heading: {heading}")
    return source[start:end]


def extract_topics(source: str, heading: str, next_heading: str | None) -> list[str]:
    body = section_body(source, heading, next_heading)
    topics: list[tuple[int, str]] = []
    for line in body.splitlines():
        match = re.match(r"^(\d+)\.\s+(.+?)\s*$", line)
        if match:
            topics.append((int(match.group(1)), match.group(2)))
    if not topics:
        raise RuntimeError(f"No numbered topics found for {heading}")
    numbers = [number for number, _ in topics]
    if numbers != list(range(1, len(numbers) + 1)):
        raise RuntimeError(f"Non-contiguous topic numbering for {heading}: {numbers}")
    return [topic for _, topic in topics]


def build_section_readme(section: dict[str, object], topics: list[str]) -> str:
    deps = "\n".join(f"- {item}" for item in section["dependencies"])
    ordering = "\n".join(f"{index}. {topic}" for index, topic in enumerate(topics, start=1))
    return f"""# {section['title']}

{section['purpose']}

## Predpoklady

Odporúčané predchádzajúce oblasti:

{deps}

## Plánované authoritative poradie

Nasledujúci inventory je schválený plán sekcie. Položka sa zmení na aktívny Markdown link až v pracovnom bloku, ktorý vytvorí a validuje príslušnú kapitolu. Tým sa plánovaný obsah nezamieňa za hotovú dokumentáciu.

{ordering}

## Authoring a evidence štandard

Každá kapitola bude používať rovnaký prose-first štandard ako sekcie 00–17:

```text
business alebo user outcome
→ exact data/model/prompt/agent subject a generation
→ authority, trust a ownership boundary
→ internal lifecycle alebo mutation path
→ authoritative read-back a proof boundary
→ failure a competing hypotheses
→ containment a recovery
→ positive, forbidden a second-operation acceptance
```

Rýchlo sa meniace produkty, API a protokoly sa pri každom bloku znovu overia proti aktuálnym primárnym zdrojom. Dokumentácia nesmie zamieňať offline eval, control-plane status alebo úspešný tool call za produkčný business outcome.

## Praktická vrstva

Nosný end-to-end smer sekcie:

```text
{section['lab']}
```

Samostatné laby a troubleshooting drilly sa aktivujú až po dostatočnom koncepčnom základe. Dokumentačný workflow môže overiť súbory, príkazy a konzistenciu modelu, ale nepreukazuje vykonanie tréningu, inference, agentického side effectu ani produkčného outcome-u.

## Stav

Aktuálny authoritative stav sekcie je **0/{len(topics)} · In progress**. Inventory a dependencies sú aktivované; prvé kapitoly ešte nie sú označené ako spracované. Po tejto sekcii nasleduje **{section['next_title']}**.
"""


def update_root_readme() -> None:
    text = read(ROOT_README)
    anchor = "18. [Keycloak and Identity Platform](docs/17-keycloak-and-identity-platform/README.md)"
    additions = """18. [Keycloak and Identity Platform](docs/17-keycloak-and-identity-platform/README.md)
19. [Machine Learning Fundamentals](docs/18-machine-learning-fundamentals/README.md)
20. [MLOps and ML Platforms](docs/19-mlops-and-ml-platforms/README.md)
21. [LLM and GenAI Engineering](docs/20-llm-and-genai-engineering/README.md)
22. [AI Agents and Intelligent Automation](docs/21-ai-agents-and-intelligent-automation/README.md)"""
    if additions not in text:
        if anchor not in text:
            raise RuntimeError("Root README Keycloak section anchor not found")
        text = text.replace(anchor, additions, 1)

    old = (
        "Hlavná roadmapa pokračuje aktívnou sekciou Keycloak and Identity Platform. "
        "Budúce ML, MLOps, LLM a agentické oblasti zostávajú rozpracované v "
        "[FUTURE-IDENTITY-AI-ROADMAP.md](FUTURE-IDENTITY-AI-ROADMAP.md)."
    )
    new = (
        "Sekcie 00–17 boli používateľom schválené v aktuálnom rozsahu. Machine Learning Fundamentals, "
        "MLOps and ML Platforms, LLM and GenAI Engineering a AI Agents and Intelligent Automation sú "
        "aktivované ako sekcie 18–21 s plánovaným inventorym; ich kapitoly sa budú spracúvať po blokoch. "
        "Pôvodné rozhodnutia, flagship projekty a produktové tracky zostávajú v "
        "[FUTURE-IDENTITY-AI-ROADMAP.md](FUTURE-IDENTITY-AI-ROADMAP.md)."
    )
    if old in text:
        text = text.replace(old, new, 1)
    elif new not in text:
        raise RuntimeError("Root README future-roadmap status paragraph not found")
    write(ROOT_README, text)


def build_active_roadmap_block(topic_map: dict[int, list[str]]) -> str:
    lines = [AI_START, "", "## Fáza 7 — Machine Learning a MLOps", ""]
    for section in SECTIONS[:2]:
        lines.extend([f"### {section['title']}", ""])
        lines.extend(f"- [ ] {topic}" for topic in topic_map[int(section["number"])])
        lines.append("")
    lines.extend(["## Fáza 8 — LLM, GenAI a agentická automatizácia", ""])
    for section in SECTIONS[2:]:
        lines.extend([f"### {section['title']}", ""])
        lines.extend(f"- [ ] {topic}" for topic in topic_map[int(section["number"])])
        lines.append("")
    lines.append(AI_END)
    return "\n".join(lines).rstrip()


def update_roadmap(topic_map: dict[int, list[str]]) -> None:
    text = read(ROADMAP)
    block = build_active_roadmap_block(topic_map)
    marker_re = re.compile(
        rf"\n?{re.escape(AI_START)}.*?{re.escape(AI_END)}\n?",
        re.DOTALL,
    )
    if AI_START in text:
        text = marker_re.sub("\n\n" + block + "\n", text).rstrip() + "\n"
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    write(ROADMAP, text)


def update_future_roadmap() -> None:
    text = read(FUTURE)
    replacements = {
        (
            "Tento dokument pôvodne plánoval identity, ML, LLM a agentické sekcie po dokončení základnej roadmapy. "
            "Sekcia Keycloak and Identity Platform je od 30. júla 2026 aktivovaná v hlavnom poradí; dokument "
            "naďalej plánuje jej zostávajúce bloky a budúce ML, MLOps, LLM a agentické sekcie."
        ): (
            "Tento dokument zachytáva schválené rozhodnutia pre identity, ML, MLOps, LLM a agentickú automatizáciu. "
            "Keycloak and Identity Platform je dokončená ako sekcia 17 a používateľom schválená v aktuálnom rozsahu. "
            "Sekcie 18–21 sú od 2. augusta 2026 aktivované v hlavnej roadmape; tento súbor zostáva detailným planning "
            "inventorym pre ich kapitoly, laby, troubleshooting drilly a cross-section flagship projekty."
        ),
        "→ Keycloak and Identity Platform — aktívna sekcia 17": "→ Keycloak and Identity Platform — 30/30 · User reviewed",
        (
            "Číslovanie priečinkov je predbežné. Ak existujúce sekcie Observability, Security and Identity, SRE, "
            "Databases a GitOps získajú očakávané čísla `12` až `16`, nové sekcie môžu pokračovať ako `17` až `21`."
        ): (
            "Číslovanie je stabilizované: Keycloak používa sekciu `17` a nové oblasti pokračujú ako "
            "`18-machine-learning-fundamentals`, `19-mlops-and-ml-platforms`, `20-llm-and-genai-engineering` "
            "a `21-ai-agents-and-intelligent-automation`."
        ),
        (
            "> Stav: aktívna sekcia [`docs/17-keycloak-and-identity-platform/`](docs/17-keycloak-and-identity-platform/README.md), "
            "prvý authoritative blok 4/30 je spracovaný."
        ): (
            "> Stav: sekcia [`docs/17-keycloak-and-identity-platform/`](docs/17-keycloak-and-identity-platform/README.md) "
            "je dokončená **30/30 · User reviewed**. Praktické runtime laby zostávajú samostatnou budúcou vrstvou."
        ),
        (
            "Tento plán je pripravený, ale ešte nie je súčasťou aktívnej lineárnej dokumentácie. Keď sa dokončí "
            "aktuálna roadmapa, témy sa prenesú do `ROADMAP.md`, vytvoria sa sekčné `README.md` súbory a zapoja "
            "sa do automatickej navigácie, glossary a review workflowu."
        ): (
            "Plán je aktivovaný v hlavnej lineárnej dokumentácii. Sekcie 18–21 majú vlastné `README.md`, ich "
            "topic inventory je prenesený do `ROADMAP.md` a budú sa plniť po authoritative blokoch. Tento súbor "
            "naďalej vlastní širšie sequencing rozhodnutia, praktické tracky a flagship projekty; stav jednotlivých "
            "kapitol vlastní hlavná roadmapa a sekčné README súbory."
        ),
    }
    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new, 1)
        elif new not in text:
            raise RuntimeError(f"Future roadmap replacement anchor missing: {old[:80]!r}")
    write(FUTURE, text)


def update_ledger(topic_map: dict[int, list[str]]) -> None:
    text = read(LEDGER)
    lines = text.splitlines()
    changed = 0
    output: list[str] = []
    for line in lines:
        match = re.match(r"^\| `([0-9]{2})-[^`]+`", line)
        if match and 0 <= int(match.group(1)) <= 17:
            if "| Ready for user review |" in line:
                line = line.replace("| Ready for user review |", "| User reviewed |", 1)
                changed += 1
            parts = line.split("|")
            if len(parts) >= 7:
                parts[4] = f" {TODAY} "
                line = "|".join(parts)
        output.append(line)
    text = "\n".join(output)
    if changed not in (0, 18):
        raise RuntimeError(f"Expected to approve 18 existing section rows, changed {changed}")

    approval_note = (
        "Používateľ 2. augusta 2026 schválil aktuálny dokumentačný rozsah sekcií 00–17. Stav `User reviewed` "
        "vyjadruje prijatie dokumentácie, nie automatické vykonanie labov, runtime verifikáciu ani úroveň zvládnutia "
        "v `REVIEW.md`."
    )
    note_anchor = "## Stav sekcií\n"
    if approval_note not in text:
        if note_anchor not in text:
            raise RuntimeError("Ledger section-status heading not found")
        text = text.replace(note_anchor, note_anchor + "\n" + approval_note + "\n", 1)

    if "`18-machine-learning-fundamentals`" not in text:
        new_rows = []
        for section in SECTIONS:
            number = int(section["number"])
            count = len(topic_map[number])
            new_rows.append(
                f"| `{number:02d}-{section['slug']}` — {section['title']} | 0/{count} planning inventory activated | "
                f"In progress | {TODAY} | Schválený topic inventory bol prenesený z `FUTURE-IDENTITY-AI-ROADMAP.md`; "
                "sekčný README, dependencies a prose-first evidence model sú aktívne. Žiadna plánovaná kapitola ešte "
                "nie je označená ako authoritative spracovaná ani runtime Verified. |"
            )
        row_anchor = next(
            (line for line in text.splitlines() if line.startswith("| `17-keycloak-and-identity-platform`")),
            None,
        )
        if row_anchor is None:
            raise RuntimeError("Section 17 ledger row not found")
        text = text.replace(row_anchor, row_anchor + "\n" + "\n".join(new_rows), 1)
    write(LEDGER, text)


def validate(topic_map: dict[int, list[str]]) -> None:
    expected = {18: 26, 19: 34, 20: 37, 21: 62}
    for number, count in expected.items():
        actual = len(topic_map[number])
        if actual != count:
            raise RuntimeError(f"Section {number} topic count mismatch: expected {count}, got {actual}")
        section = next(item for item in SECTIONS if int(item["number"]) == number)
        readme = DOCS / f"{number:02d}-{section['slug']}" / "README.md"
        if not readme.exists():
            raise RuntimeError(f"Missing activated section README: {readme}")
        content = read(readme)
        if f"**0/{count} · In progress**" not in content:
            raise RuntimeError(f"Activated section status missing in {readme}")

    ledger = read(LEDGER)
    for number in range(18):
        row = next(
            (line for line in ledger.splitlines() if line.startswith(f"| `{number:02d}-")),
            None,
        )
        if row is None or "| User reviewed |" not in row:
            raise RuntimeError(f"Section {number:02d} is not User reviewed in ledger")

    root = read(ROOT_README)
    for number in range(18, 22):
        section = next(item for item in SECTIONS if int(item["number"]) == number)
        expected_link = f"docs/{number:02d}-{section['slug']}/README.md"
        if expected_link not in root:
            raise RuntimeError(f"Root README lacks activated section {number}: {expected_link}")


future = read(FUTURE)
heading_order = [
    ("Machine Learning Fundamentals", "MLOps and ML Platforms"),
    ("MLOps and ML Platforms", None),
    ("LLM and GenAI Engineering", "AI Agents and Intelligent Automation"),
    ("AI Agents and Intelligent Automation", None),
]

topic_map: dict[int, list[str]] = {}
for section, (_, next_heading) in zip(SECTIONS, heading_order, strict=True):
    number = int(section["number"])
    topic_map[number] = extract_topics(future, str(section["source_heading"]), next_heading)
    readme_path = DOCS / f"{number:02d}-{section['slug']}" / "README.md"
    write(readme_path, build_section_readme(section, topic_map[number]))

update_root_readme()
update_roadmap(topic_map)
update_future_roadmap()
update_ledger(topic_map)
validate(topic_map)

print("Activated AI roadmap sections 18-21 and recorded user approval for sections 00-17.")
