from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "07-infrastructure-as-code-and-configuration-management"
FINDINGS = SECTION / "SECTION-07-FINDINGS-TEMP.md"

HEADING_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$")
FILE_RE = re.compile(
    r"^### `docs/07-infrastructure-as-code-and-configuration-management/([^`]+)`$"
)
FINDING_RE = re.compile(
    r"^- \*\*(CRITICAL|HIGH)\*\* line \d+, `([^`]+)` — \*\*(.+?)\*\*:"
)
LIST_RE = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.+?)\s*$")

ANSIBLE_FILES = {
    "ansible-architecture.md",
    "ansible-idempotency.md",
    "ansible-practical-walkthrough.md",
    "handlers-loops-conditionals.md",
    "inventory.md",
    "modules-tasks-plays-playbooks.md",
    "roles-and-collections.md",
    "variables-facts-templates.md",
    "vault.md",
}


def normalize(value: str) -> str:
    value = value.replace("`", "").replace("_", " ").casefold()
    value = re.sub(r"[^\w]+", " ", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip()


def parse_findings() -> dict[tuple[str, str], set[str]]:
    parsed: dict[tuple[str, str], set[str]] = defaultdict(set)
    current_file: str | None = None
    for line in FINDINGS.read_text(encoding="utf-8").splitlines():
        file_match = FILE_RE.match(line)
        if file_match:
            current_file = file_match.group(1)
            continue
        finding_match = FINDING_RE.match(line)
        if current_file and finding_match:
            _severity, kind, heading = finding_match.groups()
            parsed[(current_file, normalize(heading))].add(kind)
    return parsed


def heading_positions(lines: list[str]) -> list[tuple[int, int, str]]:
    positions: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if match:
            positions.append((index, len(match.group(1)), normalize(match.group(2))))
    return positions


def section_end(
    positions: list[tuple[int, int, str]], position_index: int, total_lines: int
) -> int:
    _line, level, _name = positions[position_index]
    for line, next_level, _next_name in positions[position_index + 1 :]:
        if next_level <= level:
            return line
    return total_lines


def family(filename: str) -> str:
    if filename in ANSIBLE_FILES:
        return "ansible"
    if filename == "terraform-vs-ansible.md":
        return "handoff"
    return "terraform"


def prose_word_count(lines: list[str]) -> int:
    prose: list[str] = []
    in_fence = False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or LIST_RE.match(line) or HEADING_RE.match(line):
            continue
        prose.append(line)
    return len(re.findall(r"\b\w+\b", " ".join(prose), flags=re.UNICODE))


def context_intro(filename: str, heading: str) -> str:
    lower = heading.casefold()
    group = family(filename)

    if group == "ansible":
        subject = "Ansible run, host alebo item subject"
        chain = (
            "resolved inventory a variables cez task/module result, handler a loaded process "
            "až po serving outcome"
        )
        closure = (
            "complete per-host coverage, pravdivý result a runtime/business read-back"
        )
    elif group == "handoff":
        subject = "Terraform-to-Ansible capability subject"
        chain = (
            "resource a state transition cez readiness contract až po per-host convergence"
        )
        closure = (
            "single-writer ownership, fresh handoff evidence a combined business test"
        )
    else:
        subject = "Terraform configuration, state a remote-resource subject"
        chain = (
            "resolved inputs a graph cez provider API mutation až po state binding"
        )
        closure = (
            "exact provider target, remote/state reconciliation a druhý no-op plan"
        )

    exact = {
        "remote lifecycle change": (
            "Remote lifecycle change ponecháva Terraform address, ale provider môže vykonať "
            "in-place update alebo replacement a zmeniť remote ID. Availability, data a "
            "downstream references preto patria do transition contractu; plan summary bez "
            "remote/state read-backu nestačí."
        ),
        "ownership adoption": (
            "Ownership adoption pripája existujúci remote objekt ku konkrétnej Terraform "
            "address-e a provider configuration. Import nevytvára správny HCL ani neoveruje "
            "target identity, preto musí po bindingu nasledovať fresh plan a remote inventory."
        ),
        "address refactor": (
            "Address refactor presúva existujúci binding medzi old a new address bez zamýšľanej "
            "remote mutation. Úplný `moved` chain musí zachovať rovnaký remote ID aj pre neskorých "
            "consumerov; inak plan navrhne destroy/create namiesto identity migration."
        ),
        "target credential rotation verzus vault rekey": (
            "Vault rekey mení kľúč, ktorým je chránený ciphertext, ale nemení heslo, token ani "
            "session na target systéme. Target credential rotation vytvorí novú capability, "
            "nasadí ju do všetkých consumerov, overí loaded epoch a starú capability explicitne "
            "revokuje. Tieto lifecycle-y majú odlišný owner aj acceptance."
        ),
        "reconciliation decision matrix": (
            "Decision matrix spája pôvod rozdielu, jeho authority a ownership s povolenou "
            "reakciou. Unauthorized drift sa revertuje alebo izoluje, schválený override sa "
            "adoptuje alebo nechá expirovať a provider noise sa opravuje v modeli či providerovi. "
            "Automatický apply bez tejto klasifikácie môže odstrániť legitímne containment."
        ),
    }
    if lower in exact:
        return exact[lower]

    if "exact" in lower or "subject" in lower:
        return (
            f"Táto podsekcia definuje presný {subject}. Názov alebo locator nestačí: subject "
            f"musí niesť generation, authority a target identity potrebné na koreláciu reťazca {chain}. "
            f"Až {closure} ukáže, že ďalší command alebo YAML patrí správnemu objektu."
        )
    if "lifecycle" in lower or "state machine" in lower or "model" in lower:
        return (
            f"Nasledujúci model opisuje prechody jedného {subject}, nie iba poradie krokov. "
            f"Failure môže nastať v ktoromkoľvek bode reťazca {chain} a zanechať partial alebo "
            f"unknown outcome. Každý transition preto potrebuje vlastný read-back a closure tvorí {closure}."
        )
    if "incident" in lower or "worked failure" in lower:
        return (
            f"Incident sa rekonštruuje ako causal chain nad jedným {subject}. Observations určujú "
            f"prvý divergentný bod v reťazci {chain}; samy osebe nie sú success alebo failure verdictom. "
            f"Recovery sa vyberá až po zachovaní evidence a uzatvára ju {closure}."
        )
    if "hypoth" in lower:
        return (
            "Hypotézy sú navzájom konkurenčné vysvetlenia rovnakého symptómu. Každá musí "
            "predpovedať konkrétny observation result a zároveň výsledok, ktorý ju oslabí; inak "
            f"nejde o discriminating test. Dôkazy sa viažu na rovnaký {subject} a finálny verdict potvrdí {closure}."
        )
    if "acceptance" in lower or "forbidden" in lower:
        return (
            f"Acceptance uzatvára celý {subject}, nie iba posledný command. Positive path dokazuje "
            "požadovanú capability, forbidden path zachovanie ownership alebo security hranice a "
            f"recovery/second-operation path stabilitu successor generation. Spoločným oracle-om je {closure}."
        )
    if "recovery" in lower or "containment" in lower:
        return (
            "Containment zastaví ďalšie writers alebo batches a zachová volatile evidence; ešte "
            f"nemení autoritatívny intent. Recovery opraví prvý chybný transition v reťazci {chain} "
            f"a každý krok read-backne pred ďalšou mutation. Closure nastane až po {closure}."
        )
    if "handler" in lower or "loaded" in lower:
        return (
            "Uložený artifact a loaded runtime sú dve odlišné generations. Notification iba "
            "zaradí handler; až handler result, process start/version a endpoint dokazujú, že nová "
            f"konfigurácia bola načítaná. Host sa považuje za converged až po {closure}."
        )
    if "unknown" in lower or "retry" in lower or "idempot" in lower:
        return (
            "Timeout alebo stratená odpoveď nehovoria, či vzdialený side effect prebehol. "
            "Operation preto potrebuje stabilný identifier, status lookup alebo server-side "
            f"deduplication a retry musí použiť rovnaký subject. Bez toho nevzniká {closure}, ale riziko duplicate state-u."
        )
    if "vault" in lower or "secret" in lower or "credential" in lower or "plaintext" in lower:
        return (
            "Secret lifecycle pokračuje po decryption aj po update source súboru. Plaintext môže "
            "existovať v controller memory, temporary files, module arguments, target files a active "
            "sessions; rekey preto nie je target credential rotation. Closure vyžaduje loaded consumer "
            "generation, provider-side revocation a forbidden test starého credentialu."
        )
    if "drift" in lower or "noise" in lower or "decision matrix" in lower:
        return (
            "Rovnaký diff môže reprezentovať unauthorized drift, expiring incident override, delegated "
            "ownership, provider normalization alebo lost binding. Najprv sa určí writer, authority, "
            "attribute owner a exact state/remote subject; až potom možno bezpečne zvoliť revert, adoption alebo recovery."
        )
    if "replacement" in lower or "import" in lower or "moved" in lower:
        return (
            "Táto transition mení remote identity, state ownership alebo Terraform address binding. "
            "Create/delete order, old/new address a provider target ovplyvňujú availability, data a "
            "rollback aj pri ekvivalentnom HCL. Fresh plan a remote/state read-back musia odlíšiť "
            "zachovaný remote objekt od skutočného replacementu."
        )
    if "test" in lower or "policy" in lower or "evidence" in lower:
        return (
            "Každá testovacia alebo policy vrstva má vlastný subject a oracle. Parser/schema pass "
            "nepreukazuje remote authorization, report existence nepreukazuje processing a isolated "
            "apply nepreukazuje production runtime. Gate preto odlišuje violation, missing/invalid evidence, tool failure a stale subject."
        )
    if heading.startswith("„") or "anti pattern" in lower:
        return (
            f"Tento anti-pattern zamieňa čiastkový signal za úplný verdict nad {subject}. Vynecháva "
            f"jednu alebo viac vrstiev reťazca {chain}, takže úspešný command môže koexistovať so "
            f"stale, partial, duplicate alebo wrong-target state-om. Bezpečná alternatíva vyžaduje explicitný subject a {closure}."
        )

    return (
        f"Táto podsekcia vysvetľuje konkrétnu časť {subject}. Source deklarácia sa nesmie zameniť "
        f"za effective reťazec {chain}; treba pomenovať aj partial a unknown outcomes. Výsledok sa "
        f"prijíma až po {closure}."
    )


def clean_item(value: str) -> str:
    value = value.strip().rstrip(";.")
    value = re.sub(r"\*\*(.+?)\*\*", r"\1", value)
    return value


def natural_join(items: list[str]) -> str:
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} a {items[1]}"
    return ", ".join(items[:-1]) + f" a {items[-1]}"


def sentence_like(value: str) -> bool:
    lower = f" {clean_item(value).casefold()} "
    verbs = (
        " je ", " sú ", " viaže ", " volá ", " implementuje ", " môže ",
        " určuje ", " vytvára ", " spracúva ", " distribuuje ", " používa ",
        " znamená ", " preukazuje ", " chráni ", " mení ", " obsahuje ",
    )
    return any(verb in lower for verb in verbs)


def ensure_sentence(value: str) -> str:
    value = clean_item(value)
    if not value:
        return value
    value = value[0].upper() + value[1:]
    return value if value.endswith((".", "!", "?")) else value + "."


def list_paragraphs(filename: str, heading: str, items: list[str]) -> list[str]:
    cleaned = [clean_item(item) for item in items]
    lower = heading.casefold()
    group = family(filename)

    if all(sentence_like(item) for item in cleaned):
        sentences = [ensure_sentence(item) for item in cleaned]
        return [" ".join(sentences[index : index + 4]) for index in range(0, len(sentences), 4)]

    if "hypoth" in lower:
        lead = "Discriminating evidence porovnáva"
        closure = "Každá observation musí potvrdiť alebo oslabiť konkrétnu hypotézu nad rovnakou identity a časovou osou."
    elif "acceptance" in lower or "forbidden" in lower:
        lead = "Acceptance matrix pokrýva"
        closure = "Paths sa vyhodnocujú oddelene, aby positive success nezakryl porušenú security, ownership alebo recovery hranicu."
    elif "incident" in lower or "failure" in lower or "recovery" in lower or "containment" in lower:
        lead = "Recovery postupuje cez"
        closure = "Poradie chráni evidence a zabraňuje tomu, aby ďalšia mutation prekryla partial alebo unknown outcome."
    elif "contract" in lower or "subject" in lower or "boundary" in lower:
        lead = "Contract eviduje"
        closure = "Všetky prvky patria jednej generation a authority boundary; chýbajúci prvok robí verdict neúplným."
    elif "version" in lower or "compatibility" in lower or "upgrade" in lower:
        lead = "Compatibility review sleduje"
        closure = "Každá zmena sa posudzuje nad existujúcim consumer state-om, pretože syntakticky platný upgrade môže meniť identity alebo behavior."
    elif "noise" in lower or "deterministic" in lower:
        lead = "Nondeterminism alebo noise môže pochádzať z"
        closure = "Canonical inputs, stable serialization a druhý no-op run musia odlíšiť presentation rozdiel od skutočnej mutation."
    elif group == "ansible":
        lead = "Execution contract zahŕňa"
        closure = "Každý prvok sa viaže na exact run, host alebo item a následne na loaded runtime, nie iba na aggregate recap."
    elif group == "handoff":
        lead = "Handoff contract zahŕňa"
        closure = "Producer a consumer musia čítať rovnakú generation bez implicitného zdieľania interného state layoutu."
    else:
        lead = "Terraform transition sleduje"
        closure = "Každý prvok sa viaže na rovnakú configuration, state a provider generation, aby sa vylúčil wrong-target alebo lost-binding outcome."

    paragraphs: list[str] = []
    for index in range(0, len(cleaned), 6):
        chunk = cleaned[index : index + 6]
        paragraphs.append(f"{lead if index == 0 else 'Ďalej sleduje'} {natural_join(chunk)}.")
    paragraphs.append(closure)
    return paragraphs


def previous_label_start(lines: list[str], list_start: int, body_start: int) -> int:
    index = list_start - 1
    while index >= body_start and not lines[index].strip():
        index -= 1
    if index < body_start:
        return list_start
    candidate = lines[index].strip()
    if candidate.endswith(":") and not candidate.startswith(("#", "```", ">")) and len(candidate.split()) <= 8:
        return index
    return list_start


def convert_short_lists(
    lines: list[str], body_start: int, body_end: int, filename: str, heading: str
) -> tuple[list[str], bool]:
    changed = False
    index = body_start
    in_fence = False

    while index < body_end:
        line = lines[index]
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            index += 1
            continue
        if in_fence:
            index += 1
            continue

        match = LIST_RE.match(line)
        if not match or match.group(1):
            index += 1
            continue

        list_start = index
        items: list[str] = []
        while index < body_end:
            current = LIST_RE.match(lines[index])
            if not current or current.group(1):
                break
            item = current.group(3)
            if len(re.findall(r"\b\w+\b", clean_item(item), flags=re.UNICODE)) > 24:
                items = []
                break
            items.append(item)
            index += 1

        if len(items) < 2:
            index = list_start + 1
            continue

        replace_start = previous_label_start(lines, list_start, body_start)
        replacement = [""]
        for paragraph in list_paragraphs(filename, heading, items):
            replacement.extend([paragraph, ""])
        old_length = index - replace_start
        lines[replace_start:index] = replacement
        body_end += len(replacement) - old_length
        index = replace_start + len(replacement)
        changed = True

    return lines, changed


def expand_file(filename: str, targets: dict[str, set[str]]) -> bool:
    path = SECTION / filename
    lines = path.read_text(encoding="utf-8").splitlines()
    changed = False

    for target, kinds in targets.items():
        positions = heading_positions(lines)
        lookup = {name: idx for idx, (_line, _level, name) in enumerate(positions)}
        if target not in lookup:
            raise RuntimeError(f"Heading not found in {filename}: {target}")
        position_index = lookup[target]
        heading_line, _level, _name = positions[position_index]
        body_start = heading_line + 1
        body_end = section_end(positions, position_index, len(lines))
        body = lines[body_start:body_end]

        needs_intro = bool(kinds & {
            "empty-section", "list-first-introduction", "single-sentence-concept",
            "thin-concept-section", "no-prose-concept", "term-before-explanation",
        }) or prose_word_count(body) < 45

        if needs_intro:
            intro = context_intro(filename, target)
            if intro not in "\n".join(body[:18]):
                lines[body_start:body_start] = ["", intro, ""]
                changed = True
                positions = heading_positions(lines)
                lookup = {name: idx for idx, (_line, _level, name) in enumerate(positions)}
                position_index = lookup[target]
                heading_line, _level, _name = positions[position_index]
                body_start = heading_line + 1
                body_end = section_end(positions, position_index, len(lines))

        if kinds & {"bare-bullet-items", "outline-instead-of-explanation"}:
            lines, converted = convert_short_lists(lines, body_start, body_end, filename, target)
            changed = changed or converted

    if changed:
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    return changed


def main() -> None:
    parsed = parse_findings()
    by_file: dict[str, dict[str, set[str]]] = defaultdict(dict)
    for (filename, heading), kinds in parsed.items():
        by_file[filename][heading] = kinds

    changed_files: list[str] = []
    for filename, targets in sorted(by_file.items()):
        if filename == "SECTION-07-FINDINGS-TEMP.md":
            continue
        if expand_file(filename, targets):
            changed_files.append(filename)

    FINDINGS.unlink(missing_ok=True)
    print(f"Section 07 prose-first closeout updated {len(changed_files)} files.")


if __name__ == "__main__":
    main()
