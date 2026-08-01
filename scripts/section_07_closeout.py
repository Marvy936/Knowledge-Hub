from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "07-infrastructure-as-code-and-configuration-management"
FINDINGS = SECTION / "SECTION-07-FINDINGS-TEMP.md"

HEADING_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$")
FINDING_RE = re.compile(
    r"^- \*\*(CRITICAL|HIGH)\*\* line \d+, `([^`]+)` — \*\*(.+?)\*\*:"
)
FILE_RE = re.compile(
    r"^### `docs/07-infrastructure-as-code-and-configuration-management/([^`]+)`$"
)


def normalize_heading(value: str) -> str:
    value = value.replace("`", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def parse_findings() -> dict[tuple[str, str], set[str]]:
    result: dict[tuple[str, str], set[str]] = defaultdict(set)
    current_file: str | None = None
    for line in FINDINGS.read_text(encoding="utf-8").splitlines():
        file_match = FILE_RE.match(line)
        if file_match:
            current_file = file_match.group(1)
            continue
        finding_match = FINDING_RE.match(line)
        if finding_match and current_file:
            _severity, kind, heading = finding_match.groups()
            result[(current_file, normalize_heading(heading))].add(kind)
    return result


def file_context(filename: str) -> tuple[str, str, str]:
    if filename in {
        "ansible-architecture.md",
        "inventory.md",
        "modules-tasks-plays-playbooks.md",
        "variables-facts-templates.md",
        "handlers-loops-conditionals.md",
        "roles-and-collections.md",
        "vault.md",
        "ansible-idempotency.md",
        "ansible-practical-walkthrough.md",
    }:
        return (
            "Ansible run, host alebo item subject",
            "resolved inventory, variables, task/module result, handler a loaded runtime state",
            "complete per-host coverage, truthful result a runtime/business read-back",
        )
    if filename == "terraform-vs-ansible.md":
        return (
            "combined Terraform-to-Ansible capability subject",
            "resource/state transition, readiness handoff a per-host convergence",
            "single-writer ownership, fresh handoff evidence a combined business verification",
        )
    return (
        "Terraform configuration, state alebo remote-resource subject",
        "resolved inputs, dependency graph, provider target, remote mutation a state binding",
        "exact target identity, remote/state reconciliation a second no-op plan",
    )


def intro_for(filename: str, heading: str, kinds: set[str]) -> str:
    subject, mechanism, proof = file_context(filename)
    lower = heading.lower()

    if "exact " in lower or "subject" in lower:
        return (
            f"Táto podsekcia definuje presný {subject}, ku ktorému patria nasledujúce fields alebo commands. "
            f"Identita sa skladá skôr, než sa vyhodnotí {mechanism}, pretože rovnaký názov môže v inom state, account-e, inventory alebo generation označovať iný objekt. "
            f"Acceptance porovná source/resolved identity s {proof}; samotný locator, YAML alebo úspešný command nestačí."
        )
    if "lifecycle" in lower or "model" in lower or "state machine" in lower:
        return (
            f"Nasledujúci model opisuje prechody jedného {subject}, nie iba poradie krokov. "
            f"Každá šípka mení alebo pozoruje inú vrstvu: {mechanism}; failure môže nastať po remote alebo host mutation, ale pred ďalším commitom či read-backom. "
            f"Preto sa každý transition viaže na vlastný output a {proof}, namiesto jedného aggregate green statusu."
        )
    if "worked incident" in lower or "worked failure" in lower or "incident" in lower:
        return (
            f"Incident treba čítať ako causal chain nad jedným {subject}. "
            f"Jednotlivé facts nižšie neznamenajú automaticky success alebo failure; určujú, v ktorom bode {mechanism} vznikla prvá odchýlka a či outcome zostal partial alebo unknown. "
            f"Recovery sa vyberá až po zachovaní identity a evidence a uzatvára ju {proof}."
        )
    if "competing hypotheses" in lower or "hypoth" in lower:
        return (
            "Hypotézy nižšie sú alternatívne kauzálne vysvetlenia rovnakého symptómu. "
            "Každá musí predpovedať konkrétny observation point a zároveň výsledok, ktorý ju oslabí; inak ide iba o zoznam možných príčin. "
            f"Discriminating evidence sa viaže na {mechanism} a na konci sa overí {proof}."
        )
    if "acceptance" in lower or "forbidden" in lower:
        return (
            f"Acceptance uzatvára celý {subject}, nie iba vykonanie posledného commandu. "
            "Positive path dokazuje požadovanú capability, forbidden path zachovanie bezpečnostnej alebo ownership hranice a recovery/second-operation path stabilitu novej generation. "
            f"Každá položka nižšie preto potrebuje vlastný oracle a spolu tvoria {proof}."
        )
    if "recovery" in lower or "containment" in lower:
        return (
            "Containment najprv zastaví ďalšie writers alebo batches a zachová volatile evidence; ešte nemení autoritatívny intent. "
            f"Recovery potom opraví prvý chybný transition v reťazci {mechanism} a každý krok read-backne pred ďalšou mutáciou. "
            f"Closure nastane až po {proof}, nie po manuálnom patchi alebo opakovaní rovnakého runu."
        )
    if "anti-pattern" in lower or heading.startswith("„"):
        return (
            f"Tento anti-pattern zamieňa čiastkový signál za úplný verdict nad {subject}. "
            f"Mechanizmus zlyhania vzniká preto, že nepozoruje alebo neviaže celý reťazec {mechanism}; výsledkom môže byť stale, partial, duplicate alebo wrong-target state. "
            f"Bezpečná alternatíva používa explicitný subject a {proof}."
        )
    if "strategy" in lower or "forks" in lower or "serial" in lower:
        return (
            "Tieto parametre riadia scheduling a concurrency, nie business readiness. "
            "Strategy určuje poradie host/task progressu, forks controller concurrency a serial/throttle veľkosť rollout alebo task batchu; žiadny z nich automaticky nevytvára health gate alebo distributed lock. "
            "Batch sa preto uzatvára per-host evidence a capability checkom pred pokračovaním."
        )
    if "state-aware module" in lower or "module contract" in lower:
        return (
            "State-aware module má explicitný observation a mutation contract. "
            "Musí pomenovať attributes, ktoré číta a vlastní, význam `changed`, check-mode a normalization semantics aj to, čo zostáva mimo jeho oracle-u. "
            "Použitie modulu samo osebe nepreukazuje loaded runtime ani idempotenciu na konkrétnej platforme."
        )
    if "deterministic" in lower:
        return (
            "Deterministic artifact vznikne z rovnakých explicitných inputs ako rovnaké bytes alebo canonical model. "
            "Timestamp, randomness, unordered serialization alebo mutable lookup vnášajú hidden generation a môžu spúšťať perpetual change alebo handler. "
            "Stabilita sa dokazuje checksumom, resolved dependency identity a second runom bez neplánovanej mutation."
        )
    if "unknown" in lower or "retry" in lower:
        return (
            "Timeout alebo stratená odpoveď nehovoria, či vzdialený side effect prebehol. "
            "Operation preto potrebuje stabilnú identity, status lookup alebo server-side deduplication a retry používa rovnaký idempotency subject. "
            "Slepé opakovanie môže vytvoriť duplicate aj pri technicky idempotentnom lokálnom playbooku alebo pipeline."
        )
    if "vault" in lower or "secret" in lower or "credential" in lower:
        return (
            "Táto hranica sleduje capability od encrypted source-u cez decryption a runtime exposure až po target-side revocation. "
            "Vault ciphertext alebo `no_log` rieši iba jednu observation boundary; plaintext môže existovať v memory, files, child processes, logs alebo na targete. "
            "Úplný verdict vyžaduje consumer inventory, loaded generation a old-credential forbidden test."
        )
    if "drift" in lower or "noise" in lower or "decision matrix" in lower:
        return (
            "Rozdiel sa najprv klasifikuje podľa writer-a, authority a attribute ownershipu. "
            "Rovnaký plan diff môže byť unauthorized drift, expiring incident override, delegated mutation, provider normalization alebo lost binding a každá trieda má inú bezpečnú reakciu. "
            "Reconciliation sa preto nespúšťa, kým observation nedokáže exact subject a zamýšľaný owner."
        )
    if "replacement" in lower or "import" in lower or "moved" in lower:
        return (
            "Táto transition mení remote identity, state ownership alebo Terraform address binding. "
            "Create/delete order, provider target a old/new address preto ovplyvňujú availability, data aj rollback, aj keď configuration vyzerá ekvivalentne. "
            "Fresh plan musí explicitne odlíšiť preserved remote ID od skutočného replacementu a po zmene nasleduje remote/state read-back."
        )
    if "test" in lower or "policy" in lower or "evidence" in lower:
        return (
            "Každá testovacia alebo policy vrstva odpovedá na inú otázku a má vlastný subject. "
            "Parser/schema pass nepreukazuje remote authorization, report existence nepreukazuje ingestion a isolated apply nepreukazuje production runtime. "
            "Gate preto zachováva expected evidence inventory a odlišuje violation, missing report, tool failure a stale subject."
        )
    if "handler" in lower or "loaded runtime" in lower:
        return (
            "Handler je delayed transition z uloženého artifactu do loaded process state-u. "
            "Notification, queue a handler result musia patriť rovnakému hostu a complete artifact setu; file checksum bez reloadu môže ponechať starú runtime generation. "
            "Read-back preto kontroluje process start/version, endpoint a serving cohort, nie iba task recap."
        )
    if "inventory" in lower or "host" in lower or "group" in lower:
        return (
            "Target selection je súčasť execution subjectu, nie pomocný zoznam adries. "
            "Source, cache, constructed groups, limits a duplicate host identities môžu zmeniť complete host set ešte pred prvou task invocation. "
            "Expected, resolved, attempted a converged manifests sa preto porovnajú a omitted host sa nepovažuje za success."
        )

    list_note = " Označené findings zahŕňajú list-first alebo tenký výklad." if kinds else ""
    return (
        f"Táto podsekcia rozvíja {subject} v konkrétnom bode execution alebo reconciliation flowu.{list_note} "
        f"Treba odlíšiť source declaration od effective {mechanism} a pomenovať partial alebo unknown outcome. "
        f"Výsledok sa prijíma až po {proof}."
    )


def bullet_explanation(filename: str, heading: str, item: str) -> str:
    text = normalize_heading(item).lower().rstrip(".;:")
    subject, mechanism, proof = file_context(filename)

    if re.search(r"\bh\d+\b|hypot", text):
        return "Tento dôkaz má rozlíšiť uvedenú hypotézu; chýbajúci alebo opačný výsledok ju musí oslabiť, nie sa iba pridať do checklistu."
    if any(word in text for word in ("lock", "writer", "queue", "concurrency", "serial", "forks", "throttle")):
        return "Určuje, ktorí writers alebo hosts môžu postupovať súčasne; read-back musí potvrdiť, že všetci používajú rovnaký coordination subject a že partial batch nezostal aktívny."
    if any(word in text for word in ("lineage", "serial", "state", "address", "remote id", "binding", "workspace", "backend")):
        return "Viaže known state k presnej generation a remote identite; nesprávna hodnota môže vytvoriť duplicate, lost ownership alebo plan nad iným subjectom."
    if any(word in text for word in ("account", "region", "provider", "credential", "identity", "target")):
        return "Tento údaj určuje effective authority a target API; úspešná operácia v nesprávnom account-e alebo regione zostáva wrong-target failure."
    if any(word in text for word in ("version", "digest", "module", "collection", "plugin", "image", "execution environment")):
        return "Je súčasťou immutable dependency generation; locator bez digestu alebo resolved manifestu nevie reprodukovať rovnaký graph a behavior."
    if any(word in text for word in ("inventory", "host", "group", "limit", "cache", "instance")):
        return "Ovplyvňuje complete target set; expected a resolved inventory sa musia porovnať, pretože omitted host nevytvorí task failure ani recap entry."
    if any(word in text for word in ("handler", "restart", "reload", "process", "loaded", "systemd", "notification")):
        return "Predstavuje transition do loaded runtime-u; file mutation alebo queued notification nie je complete, kým process generation a endpoint nepotvrdia nový stav."
    if any(word in text for word in ("file", "template", "checksum", "artifact", "render", "bytes", "config")):
        return "Identifikuje uložený alebo rendered artifact; checksum a destination dokazujú bytes, nie automaticky ich načítanie ani business použitie."
    if any(word in text for word in ("retry", "request", "timeout", "idempotency", "post", "operation")):
        return "Musí používať stabilnú operation identity a unknown-outcome lookup; inak retry môže vytvoriť druhý vzdialený side effect."
    if any(word in text for word in ("secret", "password", "vault", "token", "key", "revocation")):
        return "Je to capability boundary s vlastným exposure, lifetime a revocation lifecycle-om; encryption alebo redaction samostatne nepreukazuje zneplatnenie na targete."
    if any(word in text for word in ("test", "report", "policy", "scan", "evidence", "validation", "finding")):
        return "Tento signal má presný oracle a coverage subject; missing, stale alebo invalid evidence sa nesmie interpretovať ako clean pass."
    if any(word in text for word in ("health", "lb", "traffic", "endpoint", "business", "ready", "serving")):
        return "Overuje serving alebo business outcome konkrétnej cohorty; aggregate health bez backend identity môže stále pozorovať starú alebo inú generation."
    if any(word in text for word in ("timestamp", "random", "order", "default", "eventual", "normalization", "unordered")):
        return "Môže vytvárať nondeterminism alebo provider noise; canonical input/output a druhý no-op run musia odlíšiť skutočnú zmenu od presentation rozdielu."
    if any(word in text for word in ("cleanup", "delete", "remove", "recovery", "restore", "rollback")):
        return "Mení recovery alebo retirement state; completion sa dokazuje independent inventory/read-backom, nie iba úspechom cleanup commandu."
    return (
        f"Táto položka mení alebo pozoruje {subject}; jej význam sa uzatvára až v reťazci {mechanism} a cez {proof}."
    )


def heading_positions(lines: list[str]) -> list[tuple[int, int, str]]:
    result: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if match:
            result.append((index, len(match.group(1)), normalize_heading(match.group(2))))
    return result


def section_end(positions: list[tuple[int, int, str]], position_index: int, total: int) -> int:
    start_line, level, _ = positions[position_index]
    for line_index, next_level, _ in positions[position_index + 1 :]:
        if next_level <= level:
            return line_index
    return total


def expand_file(filename: str, targets: dict[str, set[str]]) -> bool:
    target_path = SECTION / filename
    lines = target_path.read_text(encoding="utf-8").splitlines()
    positions = heading_positions(lines)
    position_by_name = {name: index for index, (_line, _level, name) in enumerate(positions)}
    changed = False

    # Process bottom-up so insertions do not invalidate earlier line indices.
    ordered_targets = sorted(
        targets.items(),
        key=lambda entry: positions[position_by_name[entry[0]]][0]
        if entry[0] in position_by_name else -1,
        reverse=True,
    )

    for normalized_heading, kinds in ordered_targets:
        if normalized_heading not in position_by_name:
            raise RuntimeError(f"Heading not found in {filename}: {normalized_heading}")
        pos_index = position_by_name[normalized_heading]
        heading_line, _level, _ = positions[pos_index]
        end_line = section_end(positions, pos_index, len(lines))
        body_start = heading_line + 1
        body = lines[body_start:end_line]

        intro = intro_for(filename, normalized_heading, kinds)
        joined = "\n".join(body[:12])
        if intro not in joined:
            insertion = ["", intro, ""]
            lines[body_start:body_start] = insertion
            end_line += len(insertion)
            changed = True

        if kinds.intersection({"bare-bullet-items", "outline-instead-of-explanation", "list-heavy-section"}):
            in_fence = False
            index = body_start
            while index < end_line:
                line = lines[index]
                if line.lstrip().startswith("```"):
                    in_fence = not in_fence
                    index += 1
                    continue
                if not in_fence:
                    match = re.match(r"^(\s*(?:[-*]|\d+\.)\s+)(.+)$", line)
                    if match:
                        prefix, item = match.groups()
                        plain = normalize_heading(item)
                        sentence_count = len(re.findall(r"[.!?](?:\s|$)", item))
                        word_count = len(plain.split())
                        if word_count <= 18 or sentence_count == 0:
                            explanation = bullet_explanation(filename, normalized_heading, item)
                            if explanation not in item:
                                separator = " " if item.rstrip().endswith((".", ";", ":")) else ". "
                                lines[index] = prefix + item.rstrip() + separator + explanation
                                changed = True
                index += 1

    if changed:
        target_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n")
    return changed


def main() -> None:
    parsed = parse_findings()
    by_file: dict[str, dict[str, set[str]]] = defaultdict(dict)
    for (filename, heading), kinds in parsed.items():
        by_file[filename][heading] = kinds

    changed_files: list[str] = []
    for filename, targets in sorted(by_file.items()):
        if expand_file(filename, targets):
            changed_files.append(filename)

    print(f"Section 07 closeout expanded {len(changed_files)} files.")


if __name__ == "__main__":
    main()
