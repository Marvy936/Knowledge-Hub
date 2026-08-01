from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "07-infrastructure-as-code-and-configuration-management"

GENERIC_CLOSURES = {
    "Každý prvok sa viaže na exact run, host alebo item a následne na loaded runtime, nie iba na aggregate recap.",
    "Každý prvok sa viaže na rovnakú configuration, state a provider generation, aby sa vylúčil wrong-target alebo lost-binding outcome.",
    "Všetky prvky patria jednej generation a authority boundary; chýbajúci prvok robí verdict neúplným.",
    "Paths sa vyhodnocujú oddelene, aby positive success nezakryl porušenú security, ownership alebo recovery hranicu.",
    "Poradie chráni evidence a zabraňuje tomu, aby ďalšia mutation prekryla partial alebo unknown outcome.",
    "Canonical inputs, stable serialization a druhý no-op run musia odlíšiť presentation rozdiel od skutočnej mutation.",
}

FINITE_VERBS = re.compile(
    r"\b(určuje|obmedzuje|môže|testujú|testuje|je|sú|viaže|volá|implementuje|"
    r"spracúva|distribuuje|používa|preukazuje|chráni|mení|obsahuje|závisí|"
    r"potrebujú|vracia|referencujú|spájajú|uspel|zlyhal|vytvoril|vytvára|"
    r"patrí|číta|zapisuje|ukazuje|odmietne|povoľuje)\b",
    re.IGNORECASE,
)

EXECUTION_EXACT = {
    "environmentu, ownera, consumer scope-u, rotation lifecycle-u, blast radiusu a decryption authorization.":
        "Pri návrhu Vault domainu sa hodnotí environment, owner, consumer scope, rotation lifecycle, blast radius a decryption authorization.",
    "controller memory, temporary files, rendered target files, module arguments a registered results, validator stderr a callback/debug logs.":
        "Exposure inventory zahŕňa controller memory, temporary files, rendered target files, module arguments, registered results, validator stderr a callback/debug logs.",
    "controller temp, remote temp, backup file, workspace, diff artifact a registered result.":
        "Plaintext inventory zahŕňa controller temp, remote temp, backup file, workspace, diff artifact a registered result.",
    "source ciphertext-u/vars plugin, controller decryption identity a password-client audit, target file ACL a checksum, process-loaded credential epoch, application DB identity a business verifier output.":
        "Investigation koreluje source ciphertext alebo vars plugin, controller decryption identity a password-client audit, target file ACL a checksum, process-loaded credential epoch, application DB identity a business verifier output.",
    "duplicate logical name s odlišným instance ID, conflicting `ansible_host`, conflicting environment/role, unexpected variable override a source ownership.":
        "Conflict gate kontroluje duplicate logical name s odlišným instance ID, conflicting `ansible_host`, conflicting environment alebo role, unexpected variable override a source ownership.",
    "valid production metadata, missing role/environment, case normalization, forbidden overlaps, plugin version upgrade a null values.":
        "Constructed-group contract testuje valid production metadata, missing role alebo environment, case normalization, forbidden overlaps, plugin version upgrade a null values.",
    "host pattern, fact gathering, connection/privilege, strategy a batch, variables a roles a pre/tasks/post/handlers.":
        "Play contract zahŕňa host pattern, fact gathering, connection a privilege, strategy a batch, variables a roles a pre-tasks, tasks, post-tasks a handlers.",
    "host-specific idempotent member operation, aggregation do jednej reviewed manifest mutation, `throttle` alebo serializácia, samostatný orchestration play a external controller.":
        "Shared API mutation môže používať host-specific idempotent member operation, agregáciu do jednej reviewed manifest mutation, `throttle` alebo serializáciu, samostatný orchestration play alebo external controller.",
    "publisher/source repository, release a maintenance history, artifact provenance/integrity, custom controller-side plugins, shell/command usage a logging a secret behavior.":
        "Supply-chain review zahŕňa publishera a source repository, release a maintenance history, artifact provenance a integrity, custom controller-side plugins, shell alebo command usage a logging a secret behavior.",
}

TERRAFORM_EXACT = {
    "Ktorý state subject čítame a zapisujeme?, Kto je aktuálny writer a má exkluzívne oprávnenie?, Ktorý snapshot je authoritative predecessor? a Bol successor snapshot určite commitnutý, určite necommitnutý alebo je outcome neznámy?.":
        "Pred operáciou sa explicitne odpovedá na štyri otázky: ktorý state subject sa číta a zapisuje; kto je aktuálny writer a má exkluzívne oprávnenie; ktorý snapshot je authoritative predecessor; a či bol successor snapshot určite commitnutý, určite necommitnutý alebo zostal outcome neznámy.",
    "je versionovaný, prejde reviewom, môže byť súčasťou plan/policy evidence, koordinuje viac imports a zachová intent history.":
        "Configuration-driven import je versionovaný, prejde reviewom, môže byť súčasťou plan alebo policy evidence, koordinuje viac imports a zachová intent history.",
    "versionovaný a reviewovateľný, opakovateľný naprieč environments, vhodný pre reusable module releases, podporuje neskorých consumers a je súčasťou plan evidence.":
        "`moved` contract je versionovaný a reviewovateľný, opakovateľný naprieč environments, vhodný pre reusable module releases, podporuje neskorých consumers a je súčasťou plan evidence.",
    "má rovnaký význam pre všetkých supported callers, neoslabuje security, availability ani compliance, nemení resource identity neočakávaným spôsobom, je pokrytý contract testami a jeho zmena má explicitnú compatibility policy.":
        "Bezpečný default má rovnaký význam pre všetkých supported callers, neoslabuje security, availability ani compliance, nemení resource identity neočakávaným spôsobom, je pokrytý contract testami a jeho zmena má explicitnú compatibility policy.",
    "že hodnota nebude v state alebo plan-e, že provider ju nezaloguje, že job memory/filesystem je bezpečný, že `terraform output -raw` ju nevydá oprávnenému callerovi, že credential je krátkodobý a že exposure vyvolá provider-side revocation.":
        "`sensitive = true` nepreukazuje, že hodnota nebude v state alebo plane, že provider ju nezaloguje, že job memory alebo filesystem je bezpečný, že `terraform output -raw` ju nevydá oprávnenému callerovi, že credential je krátkodobý ani že exposure vyvolá provider-side revocation.",
    "canonical naming, opakované expressions, normalizáciu collections, derived tags a compatibility adapter medzi starým a novým input shape-om.":
        "Locals sú vhodné na canonical naming, opakované expressions, normalizáciu collections, derived tags a compatibility adapter medzi starým a novým input shape-om.",
}


def ensure_period(value: str) -> str:
    value = value.strip()
    return value if value.endswith((".", "!", "?")) else value + "."


def capitalize(value: str) -> str:
    value = value.strip()
    return value[:1].upper() + value[1:] if value else value


def clean_execution(line: str) -> str:
    rest = line.removeprefix("Execution contract zahŕňa ")
    if rest in EXECUTION_EXACT:
        return EXECUTION_EXACT[rest]
    if FINITE_VERBS.search(rest):
        return ensure_period(capitalize(rest))
    return line


def clean_terraform(line: str) -> str:
    rest = line.removeprefix("Terraform transition sleduje ")
    if rest in TERRAFORM_EXACT:
        return TERRAFORM_EXACT[rest]
    if rest.startswith(("ktorý ", "ktorá ", "ktoré ", "kto ", "či ")):
        return ensure_period("Transition eviduje, " + rest)
    if rest.startswith("že "):
        return ensure_period("Tento signal nepreukazuje, " + rest)
    if FINITE_VERBS.search(rest):
        return ensure_period(capitalize(rest))
    return ensure_period("Transition eviduje " + rest)


def clean_line(line: str) -> str | None:
    stripped = line.strip()
    if stripped in GENERIC_CLOSURES:
        return None
    if stripped.startswith("Execution contract zahŕňa "):
        return clean_execution(stripped)
    if stripped.startswith("Terraform transition sleduje "):
        return clean_terraform(stripped)
    if stripped.startswith("Contract eviduje ktoré "):
        return stripped.replace("Contract eviduje ktoré ", "Contract eviduje, ktoré ", 1)
    if stripped.startswith("Recovery postupuje cez "):
        rest = stripped.removeprefix("Recovery postupuje cez ")
        return ensure_period("Recovery workflow " + rest)
    if stripped.startswith("Discriminating evidence porovnáva "):
        rest = stripped.removeprefix("Discriminating evidence porovnáva ")
        if FINITE_VERBS.search(rest):
            return ensure_period(capitalize(rest))
        return ensure_period("Discriminating evidence zahŕňa " + rest)
    if stripped.startswith("Ďalej sleduje "):
        rest = stripped.removeprefix("Ďalej sleduje ")
        if re.match(r"^(overí|spustí|potvrdí|odstráni|obnoví|porovná|testuje)\b", rest):
            return ensure_period("Následne sa " + rest)
        return ensure_period("Dopĺňa ho " + rest)
    if stripped.startswith("Nondeterminism alebo noise môže pochádzať z timestamp,"):
        return stripped.replace("z timestamp,", "z timestampu,", 1)
    return line


def cleanup_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    result: list[str] = []
    changed = False
    for line in original.splitlines():
        cleaned = clean_line(line)
        if cleaned is None:
            changed = True
            continue
        if cleaned != line:
            changed = True
        result.append(cleaned)

    compact: list[str] = []
    blank_count = 0
    for line in result:
        if line.strip():
            blank_count = 0
            compact.append(line)
        else:
            blank_count += 1
            if blank_count <= 1:
                compact.append("")

    updated = "\n".join(compact).rstrip() + "\n"
    if updated != original:
        path.write_text(updated, encoding="utf-8", newline="\n")
        return True
    return changed


def main() -> None:
    changed = [path.name for path in sorted(SECTION.glob("*.md")) if cleanup_file(path)]
    print(f"Section 07 language cleanup updated {len(changed)} files.")


if __name__ == "__main__":
    main()
