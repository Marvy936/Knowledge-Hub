from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRANCH = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
if not BRANCH:
    raise SystemExit("Unable to resolve pull request branch")


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=REPO, check=True)


def write(path: Path, text: str) -> None:
    path.write_text(re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n", encoding="utf-8")


run("git", "fetch", "origin", BRANCH)
run("git", "checkout", "-B", BRANCH, f"origin/{BRANCH}")

# Section 05
p = REPO / "docs/05-ci-cd-and-release/README.md"
t = p.read_text(encoding="utf-8")
anchor = "23. [Databázová kompatibilita počas deploymentu](database-compatibility-during-deployment.md)\n"
addition = anchor + "24. [Praktický CI/CD projekt od source change po overený production release](ci-cd-practical-walkthrough.md)\n"
if t.count(anchor) != 1:
    raise RuntimeError("Section 05 ordering anchor mismatch")
t = t.replace(anchor, addition, 1)
t = t.replace("všetkých 23 authoritative kapitol", "všetkých 24 authoritative kapitol")
t = t.replace("všetkých 23 authoritative", "všetkých 24 authoritative")
t = t.replace("23 authoritative kapitol", "24 authoritative kapitol")
insert = """## Hlavný praktický walkthrough

[Praktický CI/CD projekt od source change po overený production release](ci-cd-practical-walkthrough.md) vytvára vendor-neutral executable flow nad malou Python aplikáciou. Zachová exact commit/tree a build-script identity, spustí unit a forbidden test, vytvorí deterministic tar artifact pomenovaný SHA-256 digestom, publikuje release manifest a staging evidence a promovuje tie isté bytes do production. Candidate deployment, canary, atomický active-generation switch a business verification sú oddelené transitions.

Walkthrough obsahuje aj dve failure paths. Neoverený rebuild nedokáže použiť approval viazané na pôvodný digest a lost response po traffic switchi sa rieši read-backom active/candidate generation a ledgeru, nie blind retryom. Kapitola tak spája CI, delivery, deployment, progressive exposure a recovery bez závislosti od konkrétneho CI produktu.

"""
marker = "## Connected learning scenarios\n"
if t.count(marker) != 1:
    raise RuntimeError("Section 05 scenario marker mismatch")
t = t.replace(marker, insert + marker, 1)
# Replace obsolete in-progress footer with truthful current state.
t = re.sub(
    r"(?ms)^## Aktuálny stav revalidácie\n.*\Z",
    "## Aktuálny stav revalidácie\n\nVšetkých 24 authoritative kapitol vrátane end-to-end CI/CD walkthroughu je pripravených na používateľskú kontrolu. Stav neznamená automatické používateľské schválenie ani runtime overenie každého deployment targetu.\n",
    t,
)
write(p, t)

# Section 06
p = REPO / "docs/06-gitlab/README.md"
t = p.read_text(encoding="utf-8")
anchor = "11. [Security scanning](security-scanning.md)\n"
addition = anchor + "12. [GitLab troubleshooting](gitlab-troubleshooting.md)\n"
if t.count(anchor) != 1:
    raise RuntimeError("Section 06 ordering anchor mismatch")
t = t.replace(anchor, addition, 1)
t = t.replace("11 authoritative kapitol", "12 authoritative kapitol")
t = t.replace("všetkých 11 authoritative kapitol", "všetkých 12 authoritative kapitol")
t = t.replace("strict learning-depth audit je 11/11", "strict learning-depth audit je 12/12")
insert = """## GitLab troubleshooting

[GitLab troubleshooting](gitlab-troubleshooting.md) používa jeden preserve-first model naprieč pipeline source, resolved YAML, runner eligibility, variables a workload identity, artifacts/cache, registry digest, environment deployment, runtime generation a security evidence. Kapitola ukazuje, prečo `green pipeline`, `successful deployment` alebo `closed finding` nie sú samostatne complete verdicty.

Connected incident `green pipeline, old production image` sa diagnostikuje cez pipeline/job/deployment IDs, expected job inventory, producer artifact checksum, OCI digest, target identity, live workload a business operation. Recovery overuje aj forbidden alternate path a druhú operáciu.

"""
marker = "## Connected learning scenarios\n"
if t.count(marker) != 1:
    raise RuntimeError("Section 06 scenario marker mismatch")
t = t.replace(marker, insert + marker, 1)
t = t.replace("| End-to-end GitLab pipeline walkthrough | 1/1 | Complete |", "| End-to-end GitLab pipeline walkthrough | 1/1 | Complete |\n| GitLab troubleshooting | 1/1 | Complete |")
t = t.replace("**11/11 · Ready for user review**", "**12/12 · Ready for user review**")
write(p, t)

# Section 07
p = REPO / "docs/07-infrastructure-as-code-and-configuration-management/README.md"
t = p.read_text(encoding="utf-8")
old = """10. [Terraform testing a policy](terraform-testing-and-policy.md)
11. [Praktický Terraform projekt od prázdneho adresára po overený remote state](terraform-practical-walkthrough.md)
12. [Ansible architecture](ansible-architecture.md)
13. [Inventory](inventory.md)
14. [Modules, tasks, plays a playbooks](modules-tasks-plays-playbooks.md)
15. [Variables, facts a templates](variables-facts-templates.md)
16. [Handlers, loops a conditionals](handlers-loops-conditionals.md)
17. [Roles a collections](roles-and-collections.md)
18. [Vault](vault.md)
19. [Ansible idempotencia](ansible-idempotency.md)
20. [Praktický Ansible projekt od inventory po overený rolling configuration rollout](ansible-practical-walkthrough.md)
21. [Terraform vs. Ansible](terraform-vs-ansible.md)
"""
new = """10. [Terraform testing a policy](terraform-testing-and-policy.md)
11. [Praktický Terraform projekt od prázdneho adresára po overený remote state](terraform-practical-walkthrough.md)
12. [Terraform troubleshooting](terraform-troubleshooting.md)
13. [Ansible architecture](ansible-architecture.md)
14. [Inventory](inventory.md)
15. [Modules, tasks, plays a playbooks](modules-tasks-plays-playbooks.md)
16. [Variables, facts a templates](variables-facts-templates.md)
17. [Handlers, loops a conditionals](handlers-loops-conditionals.md)
18. [Roles a collections](roles-and-collections.md)
19. [Vault](vault.md)
20. [Ansible idempotencia](ansible-idempotency.md)
21. [Praktický Ansible projekt od inventory po overený rolling configuration rollout](ansible-practical-walkthrough.md)
22. [Ansible troubleshooting](ansible-troubleshooting.md)
23. [Terraform vs. Ansible](terraform-vs-ansible.md)
"""
if t.count(old) != 1:
    raise RuntimeError("Section 07 ordering block mismatch")
t = t.replace(old, new, 1)
t = t.replace("Všetkých 21 kapitol", "Všetkých 23 kapitol")
t = t.replace("všetkých 21 authoritative kapitol", "všetkých 23 authoritative kapitol")
t = t.replace("dve referenčné executable kapitoly", "dve referenčné executable kapitoly a dve samostatné troubleshooting kapitoly")
insert = """[Terraform troubleshooting](terraform-troubleshooting.md) sleduje failure od backend/workspace/lineage identity cez provider/module resolution, saved plan a lock až po partial alebo unknown apply outcome, remote read-back, state binding recovery a druhý no-op plan. Osobitne vysvetľuje, prečo `force-unlock`, `state rm`, `import` a `-target` nie sú univerzálne opravy.

[Ansible troubleshooting](ansible-troubleshooting.md) rozkladá incident na control-node configuration, resolved inventory, variable/fact provenance, connection a become identity, module result, handler/batch state, loaded application generation a full-fleet verification. Zelený recap a `changed=0` sú akceptované iba spolu s complete target setom a independent runtime oracle-om.

"""
marker = "Tieto walkthroughy sú referenčným štandardom"
if t.count(marker) != 1:
    raise RuntimeError("Section 07 walkthrough marker mismatch")
t = t.replace(marker, insert + marker, 1)
t = t.replace("Celkový authoritative stav", "Celkový authoritative stav")
t = t.replace("21/21", "23/23")
write(p, t)

# Central ledger counts and summaries.
ledger_path = REPO / "DOCUMENTATION-REVIEW-STATUS.md"
ledger = ledger_path.read_text(encoding="utf-8")
ledger = re.sub(r"^\| `05-ci-cd-and-release`[^\n]*$", "| `05-ci-cd-and-release` — CI/CD and Release Engineering | 24/24 prose-first practical revalidation | Ready for user review | 2026-08-01 | Pôvodných 23 release-engineering kapitol dopĺňa samostatný executable walkthrough od exact Git candidate-u cez build-once digest, complete evidence, staging acceptance a production canary po atomický active-generation switch, business verification a unknown-outcome recovery. Navigation a full documentation audit boli synchronizované. |", ledger, count=1, flags=re.MULTILINE)
ledger = re.sub(r"^\| `06-gitlab`[^\n]*$", "| `06-gitlab` — GitLab | 12/12 prose-first practical and troubleshooting revalidation | Ready for user review | 2026-08-01 | K existujúcemu end-to-end GitLab pipeline walkthroughu pribudla samostatná preserve-first troubleshooting kapitola pokrývajúca pipeline creation/resolved graph, runner, variables, artifacts/cache, registry digest, deployments a security-evidence completeness. Navigation a full documentation audit boli synchronizované. |", ledger, count=1, flags=re.MULTILINE)
ledger = re.sub(r"^\| `07-infrastructure-as-code`[^\n]*$", "| `07-infrastructure-as-code` — Infrastructure as Code and Configuration Management | 23/23 prose-first practical and troubleshooting revalidation | Ready for user review | 2026-08-01 | Dva existujúce Terraform/Ansible executable walkthroughy dopĺňajú samostatné troubleshooting kapitoly. Terraform kapitola rieši backend/state/provider/plan/partial-apply a binding recovery; Ansible kapitola rieši config/inventory/variables/connection/tasks/handlers/partial fleet a second-run convergence. Navigation a full documentation audit boli synchronizované. |", ledger, count=1, flags=re.MULTILINE)
write(ledger_path, ledger)

python_bin = os.environ.get("PYTHON_BIN", "python")
run(python_bin, "scripts/update_navigation.py", "--write")
run(python_bin, "scripts/update_glossary.py", "--write")
run(python_bin, "scripts/audit_learning_depth.py", "--all-docs", "--report", "DOCUMENTATION-AUDIT.md", "--json", "documentation-audit.json")

run("git", "config", "user.name", "github-actions[bot]")
run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
run("git", "add", "docs", "DOCUMENTATION-REVIEW-STATUS.md", "DOCUMENTATION-AUDIT.md", "documentation-audit.json", "GLOSSARY.md", "glossary")
run("git", "commit", "-m", "docs: close walkthrough and troubleshooting extensions")
run("git", "push", "origin", f"HEAD:{BRANCH}")
