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

# Cloud/AWS README
p = REPO / "docs/11-cloud-and-aws/README.md"
t = p.read_text(encoding="utf-8")
t = t.replace("Všetkých 28 authoritative kapitol", "Všetkých 30 authoritative kapitol", 1)
anchor = "28. [CloudOps troubleshooting drills](cloudops-troubleshooting-drills.md)\n"
addition = anchor + "29. [Praktický AWS projekt od lokálneho artifactu po overenú Lambda release](aws-practical-walkthrough.md)\n30. [AWS troubleshooting](aws-troubleshooting.md)\n"
if t.count(anchor) != 1:
    raise RuntimeError("Cloud ordering anchor mismatch")
t = t.replace(anchor, addition, 1)

old_practical = """Praktické vykonávacie scenáre sú oddelené v:

- [AWS CloudOps laby](../../labs/aws-cloudops/README.md),
- [AWS CloudOps troubleshooting scenáre](../../troubleshooting/aws-cloudops/README.md).
"""
new_practical = """## Hlavný AWS walkthrough a troubleshooting

[Praktický AWS projekt od lokálneho artifactu po overenú Lambda release](aws-practical-walkthrough.md) vytvára cost-bounded serverless release v sandbox account-e. Spája STS identity, IAM execution role, DynamoDB conditional idempotency, reproducible Lambda zip a `CodeSha256`, immutable published versions, alias-based exposure, CloudWatch logs, CloudTrail management evidence, broken candidate, alias compare-and-swap recovery a úplný cleanup.

[AWS troubleshooting](aws-troubleshooting.md) používa preserve-first postup naprieč account/region/principal identity, IAM authorization, VPC path, EC2/ASG/ELB, Lambda/ECS/EKS, storage a databases, messaging, telemetry, KMS/secrets, CloudFormation a backup/restore. Connected incident ukazuje false-green Lambda release, stale alias a duplicate business operation.

Ďalšie praktické vykonávacie scenáre zostávajú v:

- [AWS CloudOps laby](../../labs/aws-cloudops/README.md),
- [AWS CloudOps troubleshooting scenáre](../../troubleshooting/aws-cloudops/README.md).
"""
if t.count(old_practical) != 1:
    raise RuntimeError("Cloud practical block mismatch")
t = t.replace(old_practical, new_practical, 1)

# Replace old checklist-heavy goal/status tail with prose state while preserving completion principles.
t = re.sub(
    r"(?ms)^## Cieľ zvládnutia\n.*\Z",
    """## Čo má čitateľ po sekcii vedieť

Čitateľ má vedieť začať explicitnou AWS account, region, principal a resource identity a až potom vyhodnocovať service status. Musí odlíšiť control-plane configuration od data-plane a application outcome-u, vysvetliť IAM allow/deny chain, prejsť celý VPC path a rozlíšiť compute, storage, database, serverless, container, telemetry a recovery failure domains.

Pri release-i má vedieť viazať source artifact na immutable AMI, image digest alebo Lambda version, oddeliť publication od alias/traffic exposure a overiť loaded runtime generation aj business operation. Pri incidente má zachovať request IDs, CloudTrail, CloudWatch a service-native evidence, riešiť unknown outcomes stabilnou operation identity a uzatvoriť recovery forbidden-path a second-operation testom.

Cost, security a recovery sú súčasťou každého designu. Sandbox lab musí mať tags, budget/cost hranicu a cleanup. Backup alebo replication status sa nepovažuje za recovery dôkaz bez izolovaného restore-u a application validation.

## Stav

Všetkých 30 authoritative kapitol vrátane samostatného AWS walkthroughu a troubleshooting kapitoly je pripravených na používateľskú kontrolu. Stav neznamená automatické používateľské schválenie, certifikačný výsledok ani runtime overenie labu v každom AWS account-e. SOA-C03 fakty a tool-specific syntax zostávajú viazané na uvedené official source a toolchain generation.
""",
    t,
)
write(p, t)

# GitOps README
p = REPO / "docs/16-gitops-and-platform-engineering/README.md"
t = p.read_text(encoding="utf-8")
anchor = "15. [Multi-tenancy](multi-tenancy.md)\n"
addition = anchor + "16. [Praktický GitOps projekt od Git revision po overený runtime](gitops-practical-walkthrough.md)\n17. [GitOps troubleshooting](gitops-troubleshooting.md)\n"
if t.count(anchor) != 1:
    raise RuntimeError("GitOps ordering anchor mismatch")
t = t.replace(anchor, addition, 1)
t = t.replace("**15/15 · Ready for user review**", "**17/17 · Ready for user review**", 1)
t = t.replace("Všetkých 15 authoritative kapitol", "Všetkých 17 authoritative kapitol", 1)
insert = """## Hlavný GitOps walkthrough a troubleshooting

[Praktický GitOps projekt od Git revision po overený runtime](gitops-practical-walkthrough.md) vytvára pinned kind cluster a Argo CD installation, versionovaný Kustomize environment, scoped AppProject a automated Application. Walkthrough overuje resolved Git revision, controller render, Kubernetes generations, Pod imageID, EndpointSlice a application version/business outcome. Reprodukuje Git-owned manual drift, self-heal, broken image release, Git revert recovery a prune/finalizer safety.

[GitOps troubleshooting](gitops-troubleshooting.md) rozkladá incident na source/auth, revision resolution, render inputs, desired/live diff, field ownership, apply/prune, runtime health, secrets, promotion a multi-tenancy. Connected false-green incident ukazuje rozídený Git, hidden override, live patch a ignored fields a uzatvára ho jediným authoritative release manifestom a druhou reconciliation.

"""
marker = "## Connected learning scenarios\n"
if t.count(marker) != 1:
    raise RuntimeError("GitOps scenario marker mismatch")
t = t.replace(marker, insert + marker, 1)
write(p, t)

# Ledger
ledger_path = REPO / "DOCUMENTATION-REVIEW-STATUS.md"
ledger = ledger_path.read_text(encoding="utf-8")
ledger = re.sub(
    r"^\| `11-cloud-and-aws`[^\n]*$",
    "| `11-cloud-and-aws` — Cloud and AWS | 30/30 prose-first practical and troubleshooting revalidation | Ready for user review | 2026-08-01 | Pôvodný cloud/AWS a SOA-C03 chain dopĺňa cost-bounded executable Lambda/DynamoDB/IAM walkthrough s immutable version/alias release a samostatná preserve-first AWS troubleshooting kapitola. README už nepoužíva starú Learning/L2 status tabuľku. Navigation, glossary a full documentation audit boli synchronizované. |",
    ledger,
    count=1,
    flags=re.MULTILINE,
)
ledger = re.sub(
    r"^\| `16-gitops-and-platform-engineering`[^\n]*$",
    "| `16-gitops-and-platform-engineering` — GitOps and Platform Engineering | 17/17 prose-first practical and troubleshooting revalidation | Ready for user review | 2026-08-01 | Pôvodných 15 GitOps/platform kapitol dopĺňa pinned kind/Argo CD/Kustomize executable walkthrough a samostatná troubleshooting kapitola od source/revision/renderu cez ownership/reconciliation po runtime a business outcome. Navigation, glossary a full documentation audit boli synchronizované. |",
    ledger,
    count=1,
    flags=re.MULTILINE,
)
write(ledger_path, ledger)

python_bin = os.environ.get("PYTHON_BIN", "python")
run(python_bin, "scripts/update_navigation.py", "--write")
run(python_bin, "scripts/update_glossary.py", "--write")
run(python_bin, "scripts/audit_learning_depth.py", "--all-docs", "--report", "DOCUMENTATION-AUDIT.md", "--json", "documentation-audit.json")

run("git", "config", "user.name", "github-actions[bot]")
run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
run("git", "add", "docs", "DOCUMENTATION-REVIEW-STATUS.md", "DOCUMENTATION-AUDIT.md", "documentation-audit.json", "GLOSSARY.md", "glossary")
run("git", "commit", "-m", "docs: close Cloud and GitOps walkthrough extensions")
run("git", "push", "origin", f"HEAD:{BRANCH}")
