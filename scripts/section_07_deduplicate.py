from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "07-infrastructure-as-code-and-configuration-management"

REPLACEMENTS: dict[str, list[tuple[str, str]]] = {
    "ansible-architecture.md": [
        (
            "Contract eviduje immutable execution environment digest, pinned collections, read-only source checkout, short-lived credentials, restricted network egress a oddelené untrusted validation a production execution pools.\n\nDopĺňa ho audit callback a log redaction.\n\n",
            "",
        ),
        (
            "Playbook je ordered collection plays. Play viaže host pattern na tasks, variables, privilege, strategy a failure policy. Task volá module/action alebo riadi flow. Module implementuje observation a mutation unit.\n\nAction plugin môže vykonať časť logiky na controlleri. Connection plugin určuje transport. Inventory plugin vytvára host graph. Callback plugin spracúva výsledky.\n\nCollection distribuuje modules, plugins, roles a ďalší content.\n\n",
            "",
        ),
        (
            "Strategy určuje, ako hosts postupujú tasks, forks obmedzuje controller concurrency, serial určuje rollout batch a throttle môže obmedziť konkrétnu task concurrency.\n\n```yaml\n- name: Rolling configuration rollout\n  hosts: payments_app:&production\n  serial: 4\n  max_fail_percentage: 0\n\n  tasks:\n    - name: Configure host\n      ansible.builtin.include_role:\n        name: atlas.payments.runtime\n```\n\n`serial: 4` preukazuje intended batch size, nie health gate medzi batches. Playbook musí explicitne overiť readiness a zastaviť ďalší batch pri failure.\n\n",
            "",
        ),
    ],
    "vault.md": [
        (
            "Exposure inventory zahŕňa controller memory, temporary files, rendered target files, module arguments, registered results, validator stderr a callback/debug logs.\n\nDopĺňa ho malicious collection/plugin s decryption accessom, credential, ktorý unikol pred encryption a starý target credential bez revocation.\n\n",
            "",
        ),
        (
            "Vault ID je routing label pre password source. Nie je samostatná authorization policy ani secret identity.\n\nPri návrhu Vault domainu sa hodnotí environment, owner, consumer scope, rotation lifecycle, blast radius a decryption authorization.\n\nJeden password pre dev aj prod rozširuje production compromise boundary.\n\n",
            "",
        ),
    ],
}


def main() -> None:
    changed: list[str] = []
    for filename, replacements in REPLACEMENTS.items():
        path = SECTION / filename
        text = path.read_text(encoding="utf-8")
        original = text
        for old, new in replacements:
            if old in text:
                text = text.replace(old, new, 1)
        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
            changed.append(filename)
    print(f"Section 07 prose deduplication updated {len(changed)} files.")


if __name__ == "__main__":
    main()
