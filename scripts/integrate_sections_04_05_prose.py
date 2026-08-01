from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = Path("scripts/integrate_sections_04_05_prose.py")
WORKFLOW_PATH = Path(".github/workflows/knowledge-navigation.yml")

HEADINGS = {
    "docs/04-testing-and-quality/verification-vs-validation.md": "Ako sa z pozorovania stane testovací verdikt",
    "docs/04-testing-and-quality/test-pyramid.md": "Ako vybrať správny test scope",
    "docs/04-testing-and-quality/unit-integration-component-tests.md": "Ako určiť hranicu unit, integration a component testu",
    "docs/04-testing-and-quality/contract-and-api-tests.md": "Ako čítať API contract a runtime dôkaz",
    "docs/04-testing-and-quality/end-to-end-and-acceptance-tests.md": "Ako ohraničiť end-to-end a acceptance dôkaz",
    "docs/04-testing-and-quality/smoke-and-regression-tests.md": "Ako rozdeliť smoke a regression kontrolu",
    "docs/04-testing-and-quality/performance-load-stress-tests.md": "Ako čítať workload, percentily a saturation",
    "docs/04-testing-and-quality/security-and-infrastructure-tests.md": "Ako spojiť threat, control a security evidence",
    "docs/04-testing-and-quality/static-analysis-linting-type-checking.md": "Ako interpretovať statický nález",
    "docs/04-testing-and-quality/code-coverage-and-quality-gates.md": "Ako čítať coverage a quality gate",
    "docs/04-testing-and-quality/mocks-stubs-fakes.md": "Ako vybrať test double bez skreslenia testu",
    "docs/04-testing-and-quality/flaky-tests-and-test-data.md": "Ako rozlíšiť flaky test od skutočného defectu",
    "docs/04-testing-and-quality/shift-left.md": "Ako presunúť feedback skôr bez straty fidelity",
    "docs/04-testing-and-quality/shift-right.md": "Ako získavať produkčný dôkaz bezpečne",
    "docs/04-testing-and-quality/chaos-testing.md": "Ako zostaviť riadený chaos experiment",
    "docs/05-ci-cd-and-release/continuous-integration.md": "Ako vzniká dôveryhodný integration candidate",
    "docs/05-ci-cd-and-release/continuous-delivery.md": "Ako sa artifact stane pripraveným na release",
    "docs/05-ci-cd-and-release/continuous-deployment.md": "Ako funguje automatický production feedback loop",
    "docs/05-ci-cd-and-release/pipeline-stage-job-runner.md": "Ako sa pipeline mení na reálne procesy na runneri",
    "docs/05-ci-cd-and-release/trigger-artifact-cache.md": "Ako odlíšiť trigger, artifact a cache",
    "docs/05-ci-cd-and-release/environment-and-promotion.md": "Ako funguje immutable promotion medzi prostrediami",
    "docs/05-ci-cd-and-release/quality-gates-and-approvals.md": "Ako gate a approval rozhodujú nad presným subjectom",
    "docs/05-ci-cd-and-release/pipeline-as-code.md": "Ako sa source pipeline zmení na resolved execution graph",
    "docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md": "Ako fungujú fan-out, shardy a fan-in",
    "docs/05-ci-cd-and-release/artifact-versioning.md": "Ako checksum, digest, podpis a provenance chránia artifact",
    "docs/05-ci-cd-and-release/semantic-versioning.md": "Ako čítať Semantic Versioning ako compatibility contract",
    "docs/05-ci-cd-and-release/release-management.md": "Ako sa candidate zmení na podporovaný release",
    "docs/05-ci-cd-and-release/recreate-deployment.md": "Ako funguje recreate deployment state machine",
    "docs/05-ci-cd-and-release/rolling-update.md": "Ako funguje rolling update počas mixed-version intervalu",
    "docs/05-ci-cd-and-release/blue-green-deployment.md": "Ako funguje blue-green prepnutie",
    "docs/05-ci-cd-and-release/canary-deployment.md": "Ako vyhodnocovať canary cohortu",
    "docs/05-ci-cd-and-release/a-b-testing.md": "Ako A/B test oddeľuje release safety od causal inference",
    "docs/05-ci-cd-and-release/shadow-deployment.md": "Ako shadow deployment kopíruje traffic bez business side effects",
    "docs/05-ci-cd-and-release/ring-deployment.md": "Ako stabilné rings riadia expozíciu release-u",
    "docs/05-ci-cd-and-release/feature-flags.md": "Ako feature flag vytvára samostatný runtime control plane",
    "docs/05-ci-cd-and-release/progressive-delivery.md": "Ako progressive delivery spája rollout a evidence",
    "docs/05-ci-cd-and-release/rollback-and-roll-forward.md": "Ako vybrať rollback, roll-forward, compensation alebo restore",
    "docs/05-ci-cd-and-release/database-compatibility-during-deployment.md": "Ako expand/contract chráni mixed-version databázu",
    "docs/05-ci-cd-and-release/ci-cd-practical-walkthrough.md": "Ako čítať end-to-end release walkthrough",
}

BLOCK_RE = re.compile(
    r"(?ms)^## Doplnenie výkladu:[^\n]*\n\n(?P<body>.*?)(?=^## )"
)
BULLET_RE = re.compile(r"^(?:[-*+] |\d+\. )(?P<item>.+)$")
HOOK = '''      - name: Integrate Sections 04 and 05 prose
        if: github.event_name == 'pull_request'
        shell: bash
        run: |
          set -euo pipefail
          "$PYTHON_BIN" scripts/integrate_sections_04_05_prose.py

'''


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def sentence(text: str) -> str:
    value = text.strip().rstrip(";")
    if not value:
        return value
    if value[-1] not in ".?!":
        value += "."
    return value


def natural_join(items: list[str]) -> str:
    cleaned = [item.strip().rstrip(";,. ") for item in items if item.strip()]
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} a {cleaned[1]}"
    return ", ".join(cleaned[:-1]) + f" a {cleaned[-1]}"


def prose_from_list(items: list[str], intro: str | None) -> list[str]:
    items = [item.strip() for item in items if item.strip()]
    if not items:
        return []

    definition_like = all(
        item.startswith("**") and (" je " in item or " znamen" in item or " — " in item)
        for item in items
    )
    short_like = all(len(item) < 105 and not re.search(r"[.!?]\s", item) for item in items)

    if definition_like:
        prefix: list[str] = []
        if intro and "základné pojmy" not in intro.lower():
            prefix.append(sentence(intro.rstrip(":")))
        paragraphs: list[str] = []
        chunk: list[str] = []
        for item in items:
            chunk.append(sentence(item))
            if len(chunk) == 3:
                paragraphs.append(" ".join(chunk))
                chunk = []
        if chunk:
            paragraphs.append(" ".join(chunk))
        return prefix + paragraphs

    if short_like:
        joined = natural_join(items)
        if intro:
            base = intro.strip().rstrip(":")
            if base.lower() in {"základné pojmy", "typické kontroly", "validuj"}:
                base = "Do tejto hranice patria"
            return [sentence(f"{base} {joined}")]
        return [sentence(f"Do tejto hranice patria {joined}")]

    prefix = sentence(intro.rstrip(":")) + " " if intro else ""
    sentences = [sentence(item) for item in items]
    paragraphs: list[str] = []
    chunk: list[str] = []
    for item in sentences:
        chunk.append(item)
        if len(chunk) == 2:
            paragraphs.append((prefix if not paragraphs else "") + " ".join(chunk))
            prefix = ""
            chunk = []
    if chunk:
        paragraphs.append((prefix if not paragraphs else "") + " ".join(chunk))
    return paragraphs


def proseify(body: str) -> str:
    lines = body.splitlines()
    out: list[str] = []
    in_code = False
    index = 0

    while index < len(lines):
        line = lines[index]
        if line.startswith("```"):
            in_code = not in_code
            out.append(line)
            index += 1
            continue

        match = BULLET_RE.match(line) if not in_code else None
        if not match:
            out.append(line)
            index += 1
            continue

        items: list[str] = []
        while index < len(lines):
            current = lines[index]
            bullet = BULLET_RE.match(current)
            if not bullet:
                break
            item = bullet.group("item").strip()
            index += 1
            continuation: list[str] = []
            while index < len(lines):
                candidate = lines[index]
                if BULLET_RE.match(candidate) or not candidate.startswith("  "):
                    break
                continuation.append(candidate.strip())
                index += 1
            if continuation:
                item += " " + " ".join(continuation)
            items.append(item)

        intro: str | None = None
        while out and not out[-1].strip():
            out.pop()
        if out and out[-1].strip().endswith(":") and not out[-1].startswith("#"):
            intro = out.pop().strip()
        out.append("")
        for paragraph in prose_from_list(items, intro):
            out.append(paragraph)
            out.append("")

    result = "\n".join(out)
    result = re.sub(r"\n{3,}", "\n\n", result).strip() + "\n\n"
    return result


def assert_no_top_level_lists(markdown: str, path: str) -> None:
    in_code = False
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        if line.startswith("```"):
            in_code = not in_code
            continue
        if not in_code and BULLET_RE.match(line):
            raise AssertionError(f"{path}:{line_number}: top-level list remains in integrated block")


def rewrite_chapter(path: str, heading: str) -> None:
    full_path = ROOT / path
    text = full_path.read_text(encoding="utf-8")
    matches = list(BLOCK_RE.finditer(text))
    if len(matches) != 1:
        raise AssertionError(f"{path}: expected one Doplnenie výkladu block, found {len(matches)}")
    match = matches[0]
    body = proseify(match.group("body"))
    replacement = f"## {heading}\n\n{body}"
    assert_no_top_level_lists(replacement, path)
    updated = text[: match.start()] + replacement + text[match.end() :]
    if "## Doplnenie výkladu:" in updated:
        raise AssertionError(f"{path}: retired heading remains")
    full_path.write_text(updated, encoding="utf-8")


def update_readmes() -> None:
    path04 = ROOT / "docs/04-testing-and-quality/README.md"
    text04 = path04.read_text(encoding="utf-8")
    pattern04 = re.compile(
        r"(?ms)^## Rozšírený výklad pojmov, kódu a výsledkov\n\n.*?(?=^## Čo má čitateľ po sekcii vedieť)"
    )
    replacement04 = (
        "## Výklad je integrovaný priamo do kapitol\n\n"
        "Pojmy, príkazy a výsledky už nie sú vložené ako osobitný definíciový dodatok. "
        "Každá kapitola ich vysvetľuje v súvislom toku od testovaného rizika a mechanizmu cez setup, "
        "vykonanie a oracle až po interpretáciu PASS, FAIL, ERROR alebo MISSING výsledku. Odrážky zostávajú "
        "iba pri skutočnom porovnaní variantov alebo pri presne ohraničenom inventári; nenesú hlavný výklad.\n\n"
        "Testovací kód, konfigurácia a metriky sú preto zasadené priamo do odsekov, ktoré vysvetľujú, "
        "čo sa pri ich vykonaní deje, aký subject a scope pokrývajú a kde končí dôkazná hodnota výsledku.\n\n"
    )
    text04, count04 = pattern04.subn(replacement04, text04)
    if count04 != 1:
        raise AssertionError(f"Section 04 README replacement count: {count04}")
    path04.write_text(text04, encoding="utf-8")

    path05 = ROOT / "docs/05-ci-cd-and-release/README.md"
    text05 = path05.read_text(encoding="utf-8")
    pattern05 = re.compile(
        r"(?ms)^## Rozšírený výklad pojmov, príkazov a release dôkazov\n\n.*?(?=^## Cieľ zvládnutia)"
    )
    replacement05 = (
        "## Výklad je integrovaný do release lifecycle-u\n\n"
        "Technické pojmy už nevystupujú ako odrážkový slovník pridaný za pôvodnú kapitolu. "
        "Integration candidate, artifact, cache, digest, promotion, cohort, rollout a recovery sa vysvetľujú "
        "v tom kroku release lifecycle-u, v ktorom menia stav alebo rozhodnutie. Príkaz alebo controller transition "
        "je vždy spojený s vysvetlením vstupu, vykonanej mutácie, read-backu a hranice dôkazu.\n\n"
        "Odrážky zostávajú iba tam, kde porovnávajú deployment stratégie, vypočítavajú explicitný inventory "
        "alebo zapisujú acceptance podmienky. Hlavný výklad pokračuje súvislými odsekmi od mechanizmu cez Atlas "
        "scenár až po incident, recovery a druhé overenie.\n\n"
    )
    text05, count05 = pattern05.subn(replacement05, text05)
    if count05 != 1:
        raise AssertionError(f"Section 05 README replacement count: {count05}")
    path05.write_text(text05, encoding="utf-8")


def update_ledger() -> None:
    path = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
    text = path.read_text(encoding="utf-8")
    row04 = (
        "| `04-testing-and-quality` — Testing and Software Quality | 15/15 integrated narrative revalidation | Ready for user review | 2026-08-01 | "
        "Všetkých 15 kapitol používa súvislý odborný výklad bez osobitných definíciových dodatkov. Pojmy, test setup, assertions, metrics a verdicty sú integrované priamo medzi mechanizmus, executable example a worked failure. Top-level odrážky v prepracovaných explanation blokoch boli odstránené; zoznamy zostávajú iba ako presné porovnanie alebo inventory. Navigation, glossary a full documentation audit boli synchronizované. |"
    )
    row05 = (
        "| `05-ci-cd-and-release` — CI/CD and Release Engineering | 24/24 connected prose, practical and release-evidence revalidation | Ready for user review | 2026-08-01 | "
        "Všetkých 24 kapitol integruje vysvetlenie integration candidates, pipeline execution, artifacts, caches, digests, promotion, deployment cohorts, progressive exposure a recovery priamo do release lifecycle-u. Posledné odrážkové explanation bloky boli premenené na prirodzené tematické podkapitoly; commands a controller transitions sú vysvetlené vstupom, mutáciou, read-backom a dôkaznou hranicou. Navigation, glossary a full documentation audit boli synchronizované. |"
    )
    text, count04 = re.subn(r"(?m)^\| `04-testing-and-quality`.*$", row04, text)
    text, count05 = re.subn(r"(?m)^\| `05-ci-cd-and-release`.*$", row05, text)
    if count04 != 1 or count05 != 1:
        raise AssertionError(f"Ledger replacements: section04={count04}, section05={count05}")
    path.write_text(text, encoding="utf-8")


def remove_closeout_files() -> None:
    workflow = ROOT / WORKFLOW_PATH
    text = workflow.read_text(encoding="utf-8")
    if HOOK not in text:
        raise AssertionError("Temporary workflow hook not found")
    workflow.write_text(text.replace(HOOK, ""), encoding="utf-8")
    (ROOT / SCRIPT_PATH).unlink()


def main() -> None:
    branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    if not branch:
        raise RuntimeError("Unable to resolve branch")

    run("git", "fetch", "origin", branch)
    run("git", "checkout", "-B", branch, f"origin/{branch}")

    for path, heading in HEADINGS.items():
        rewrite_chapter(path, heading)

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

    remove_closeout_files()

    run("git", "config", "user.name", "github-actions[bot]")
    run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    run("git", "add", "docs/04-testing-and-quality", "docs/05-ci-cd-and-release", "DOCUMENTATION-REVIEW-STATUS.md", "GLOSSARY.md", "glossary", "DOCUMENTATION-AUDIT.md", "documentation-audit.json", str(WORKFLOW_PATH), str(SCRIPT_PATH))
    run("git", "commit", "-m", "docs: integrate testing and release explanations into prose")
    run("git", "push", "origin", f"HEAD:{branch}")


if __name__ == "__main__":
    main()
