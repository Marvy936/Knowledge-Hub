from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "docs" / "07-infrastructure-as-code-and-configuration-management" / "README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"

OLD_README = (
    "Celkový authoritative stav: **23/23 · Ready for user review**. Pôvodný "
    "19-kapitolový prose-first pass zostáva zachovaný a dva nové walkthroughy "
    "dopĺňajú súvislé code, command, output a runtime-verification flows. Tento stav "
    "neznamená automatické používateľské schválenie, Accepted, Verified ani Stable."
)

NEW_README = (
    "Celkový authoritative stav: **23/23 · Ready for user review**. Všetkých 23 kapitol "
    "prešlo chapter-by-chapter explanation-depth revalidáciou pri zachovaní existujúceho "
    "HCL, Ansible YAML, incidentov, recovery modelov, dvoch executable walkthroughov a "
    "samostatných troubleshooting kapitol. Cielený pass doplnil exact subject a generation "
    "boundaries, provider/state/binding semantics, graph-shape a replacement dôsledky, "
    "inventory a per-host completeness, handler/loaded-runtime transition, Vault exposure a "
    "revocation a Terraform–Ansible single-writer handoff. Section 07 už nemá critical ani "
    "high learning-depth findings. Repository workflow overuje dokumentačnú konzistenciu, "
    "navigation a audit; Terraform apply, cloud APIs, Ansible fleet execution, target "
    "credentials a runtime/business capability neboli týmto documentation passom vykonané "
    "proti reálnemu prostrediu. Stav preto neznamená používateľské schválenie ani runtime "
    "Verified alebo Stable."
)

NEW_LEDGER_ROW = (
    "| `07-infrastructure-as-code` — Infrastructure as Code and Configuration Management | "
    "23/23 chapter-by-chapter explanation-depth revalidation | Ready for user review | "
    "2026-08-01 | Všetkých 23 authoritative kapitol bolo znovu prečítaných podľa exact "
    "configuration/provider/module/backend/state/remote-object a inventory/host/task/secret "
    "subjectu, mutation, read-back, partial/unknown outcome, recovery a second-operation "
    "štandardu. Existujúci odborný základ, HCL, Terraform CLI/JSON, Ansible YAML/CLI, "
    "`IAC-PAY-75` až `IAC-PAY-79`, dva end-to-end walkthroughy a samostatné Terraform/Ansible "
    "troubleshooting kapitoly zostali zachované. Preserve-first pass doplnil state boundary a "
    "wrong-target semantics, provider alias a data-source evidence, stable collection/address "
    "identity, import/moved/replacement recovery, drift classification, testing-evidence "
    "completeness, control-node/execution-environment authority, expected-vs-resolved fleet, "
    "per-host/task/item truthfulness, handler a loaded-runtime closure, role/collection supply "
    "chain, Vault plaintext/revocation lifecycle, idempotency a Terraform–Ansible single-writer "
    "handoff. Bare outline bloky boli premenené na connected prose bez odstránenia pôvodných "
    "ukážok. Section 07 nemá critical ani high learning-depth findings. README, review ledger, "
    "navigation, glossary a full audit boli synchronizované. Terraform/cloud a Ansible/fleet "
    "runtime neboli týmto documentation workflowom vykonané; sekcia je Ready for user review, "
    "nie runtime Verified ani používateľsky Accepted. |"
)


def update_readme() -> None:
    text = README.read_text(encoding="utf-8")
    if NEW_README in text:
        return
    if OLD_README not in text:
        raise RuntimeError("Expected Section 07 README status paragraph not found")
    README.write_text(text.replace(OLD_README, NEW_README, 1), encoding="utf-8", newline="\n")


def update_ledger() -> None:
    lines = LEDGER.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.startswith("| `07-infrastructure-as-code` —"):
            lines[index] = NEW_LEDGER_ROW
            LEDGER.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
            return
    raise RuntimeError("Section 07 ledger row not found")


def main() -> None:
    update_readme()
    update_ledger()
    print("Section 07 README and review ledger finalized.")


if __name__ == "__main__":
    main()
