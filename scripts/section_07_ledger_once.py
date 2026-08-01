from pathlib import Path

root = Path(__file__).resolve().parents[1]
ledger = root / "DOCUMENTATION-REVIEW-STATUS.md"
lines = ledger.read_text(encoding="utf-8").splitlines()

new_row = "| `07-infrastructure-as-code` — Infrastructure as Code and Configuration Management | 23/23 chapter-by-chapter explanation-depth revalidation | Ready for user review | 2026-08-01 | Všetkých 23 authoritative kapitol bolo znovu prečítaných podľa exact configuration/provider/module/backend/state/remote-object a inventory/host/task/secret subjectu, mutation, read-back, partial/unknown outcome, recovery a second-operation štandardu. Existujúci odborný základ, HCL, Terraform CLI/JSON, Ansible YAML/CLI, `IAC-PAY-75` až `IAC-PAY-79`, dva end-to-end walkthroughy a samostatné Terraform/Ansible troubleshooting kapitoly zostali zachované. Preserve-first pass doplnil state boundary a wrong-target semantics, provider alias a data-source evidence, stable collection/address identity, import/moved/replacement recovery, drift classification, testing-evidence completeness, control-node/execution-environment authority, expected-vs-resolved fleet, per-host/task/item truthfulness, handler a loaded-runtime closure, role/collection supply chain, Vault plaintext/revocation lifecycle, idempotency a Terraform–Ansible single-writer handoff. Bare outline bloky boli premenené na connected prose bez odstránenia pôvodných ukážok. Section 07 nemá critical ani high learning-depth findings. README, review ledger, navigation, glossary a full audit boli synchronizované. Terraform/cloud a Ansible/fleet runtime neboli týmto documentation workflowom vykonané; sekcia je Ready for user review, nie runtime Verified ani používateľsky Accepted. |"

for index, line in enumerate(lines):
    if line.startswith("| `07-infrastructure-as-code` —"):
        lines[index] = new_row
        ledger.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print("Section 07 review ledger row updated.")
        break
else:
    raise SystemExit("Section 07 ledger row not found")
