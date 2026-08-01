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


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


# The pull_request checkout is normally a synthetic merge ref. Work on the actual
# head branch so the generated closeout commit can be pushed without introducing
# an accidental merge commit.
run("git", "fetch", "origin", BRANCH)
run("git", "checkout", "-B", BRANCH, f"origin/{BRANCH}")

practical_path = REPO / "docs/09-kubernetes/kubernetes-practical-walkthrough.md"
practical = practical_path.read_text(encoding="utf-8")

practical = replace_once(
    practical,
    """│   ├── broken-readiness/\n│   │   └── kustomization.yaml\n└── scripts/\n""",
    """│   ├── broken-readiness/\n│   │   └── kustomization.yaml\n│   └── hpa/\n│       └── kustomization.yaml\n└── scripts/\n""",
    "project tree HPA overlay",
)

practical = replace_once(
    practical,
    """  - networkpolicy.yaml\n  - hpa.yaml\ncommonLabels:\n""",
    """  - networkpolicy.yaml\ncommonLabels:\n""",
    "base kustomization HPA ownership",
)

practical = replace_once(
    practical,
    """HPA môže meniť replicas nad šesť. Verification script preto nepredpokladá vždy presne šesť Podov; porovnáva desired a ready state.\n\n## 11. Kustomization\n""",
    """HPA zámerne nevkladáme do základného `kustomization.yaml`. Základný walkthrough najprv overí statický šesť-replikový rollout a no-op druhý apply. Autoscaler a deklaratívny manager tak počas hlavného flowu nebojujú o `.spec.replicas`.\n\n### HPA overlay bez konfliktu writera\n\nVytvor `overlays/hpa/kustomization.yaml`:\n\n```yaml\napiVersion: kustomize.config.k8s.io/v1beta1\nkind: Kustomization\nresources:\n  - ../..\n  - ../../hpa.yaml\npatches:\n  - target:\n      group: apps\n      version: v1\n      kind: Deployment\n      name: payments-api\n    patch: |-\n      - op: remove\n        path: /spec/replicas\n```\n\nTento overlay odstráni statický replica field ešte pred prijatím Deploymentu a pridá HPA. Použi ho od prvého apply v samostatnom autoscaling lab-e. Neprepínaj už bežiaci statický production flow na HPA bez samostatného ownership a capacity plánu; odstránenie field-u, HPA reconciliation, quota a rollout môžu vytvoriť prechodnú zmenu kapacity.\n\n## 11. Kustomization\n""",
    "HPA explanation and overlay",
)

practical = replace_once(
    practical,
    """Secret vzor nie je medzi resources. Pred apply musí Secret existovať z externého flowu.\n\n`commonLabels` doplní management label. Pri použití Kustomize transformerov vždy skontroluj rendered selectors; plošné label transformácie môžu meniť selector semantics podľa verzie a configuration.\n""",
    """Secret vzor ani `hpa.yaml` nie sú medzi základnými resources. Pred apply musí Secret existovať z externého flowu. HPA sa používa iba cez samostatný overlay, ktorý zároveň odstráni statické vlastníctvo `.spec.replicas`.\n\n`commonLabels` doplní management label. Pri použití Kustomize transformerov vždy skontroluj rendered selectors; plošné label transformácie môžu meniť selector semantics podľa verzie a configuration.\n""",
    "base kustomization explanation",
)

hpa_section = re.compile(
    r"## 26\. HPA observation\n.*?(?=\n## 27\. Forbidden security test)",
    re.DOTALL,
)
hpa_replacement = """## 26. Voliteľný HPA flow\n\nZákladný walkthrough používa statických šesť replík a HPA nevytvára. Autoscaling test vykonaj v samostatnom lab-e od prvého apply cez HPA overlay:\n\n```bash\nkubectl apply \\\n  --server-side \\\n  --field-manager=atlas-kubernetes-walkthrough \\\n  -k overlays/hpa\n```\n\nOverlay odstráni `.spec.replicas` zo zdrojového Deploymentu a vytvorí HPA, takže aktuálny replica count vlastní autoscaler namiesto deklaratívneho managera. Over:\n\n```bash\nkubectl get hpa payments-api -n production\nkubectl describe hpa payments-api -n production\nkubectl get deployment payments-api -n production \\\n  -o jsonpath='{.spec.replicas}{"\\n"}'\n```\n\nAk resource metrics pipeline neexistuje, HPA condition môže ukázať metric error. V takom prostredí nepovažuj autoscaling za overený. HPA, quota, Node capacity, Deployment rollout a readiness tvoria jeden scale chain.\n\nNevytváraj umelý CPU load v production clustri bez guardrails. V reprezentatívnom lab-e sleduj celý prechod:\n\n```text\nmetric rastie\n→ HPA desired replicas\n→ Deployment scale\n→ nové Pod objekty\n→ scheduling a Node capacity\n→ runtime a readiness\n→ Service capacity\n```\n\nPo autoscaling lab-e odstráň HPA a znovu aplikuj základný model iba vtedy, keď je tento ownership prechod súčasťou explicitného test plánu.\n"""
practical, count = hpa_section.subn(hpa_replacement, practical, count=1)
if count != 1:
    raise RuntimeError(f"HPA observation section: expected one match, found {count}")

practical = replace_once(
    practical,
    """Najprv odstráň resources z Kustomize modelu:\n\n```bash\nkubectl delete -k .\n```\n""",
    """Ak si použil autoscaling overlay, odstráň HPA osobitne:\n\n```bash\nkubectl delete -f hpa.yaml --ignore-not-found\n```\n\nPotom odstráň resources zo základného Kustomize modelu:\n\n```bash\nkubectl delete -k .\n```\n""",
    "cleanup HPA",
)

practical_path.write_text(practical, encoding="utf-8")

# Replace the central review-ledger row for Section 09.
ledger_path = REPO / "DOCUMENTATION-REVIEW-STATUS.md"
ledger = ledger_path.read_text(encoding="utf-8")
new_row = (
    "| `09-kubernetes` — Kubernetes | 32/32 full prose and practical revalidation | "
    "Ready for user review | 2026-08-01 | Všetkých 31 pôvodných authoritative kapitol bolo "
    "kompletne prepísaných a pribudla 32. praktická kapitola. Sekcia používa jeden plynulý "
    "`payments-api` chain od kubeconfig/API requestu cez etcd, controllers, scheduler, kubelet, "
    "CRI/CNI/CSI, workload controllers, configuration a identity, Service/EndpointSlice, Gateway, "
    "DNS, storage, resources, probes, placement, HPA, RBAC a Pod Security až po cluster lifecycle, "
    "etcd recovery, upgrades, observability a preserve-first troubleshooting. YAML, CLI a JSON sú "
    "vložené priamo pri vysvetľovanom mechanizme a každý output oddeľuje source, admitted, controller, "
    "effective runtime/dataplane a business evidence. Nový `kubernetes-practical-walkthrough.md` "
    "vytvára Namespace, ServiceAccount, ConfigMap/Secret contract, hardenovaný Deployment, Service, "
    "PDB, NetworkPolicies, voliteľný HPA ownership overlay, Kustomize render, server-side dry-run/diff, "
    "rollout, image/config/EndpointSlice read-back, no-op apply, configuration replacement, Pod "
    "replacement, broken-selector a Running-but-NotReady failure, forbidden Pod Security test a cleanup. "
    "Repository workflow overuje navigation, glossary a learning depth; manifesty neboli v tomto "
    "documentation workflowe vykonané proti reálnemu clusteru, CNI/CSI, metrics pipeline, registry ani "
    "cloud providerovi. Sekcia je pripravená na používateľskú kontrolu, nie automaticky Accepted, "
    "Verified ani Stable. |"
)
ledger, count = re.subn(
    r"^\| `09-kubernetes`[^\n]*$",
    new_row,
    ledger,
    count=1,
    flags=re.MULTILINE,
)
if count != 1:
    raise RuntimeError(f"Section 09 ledger row: expected one match, found {count}")
ledger_path.write_text(ledger, encoding="utf-8")

# Basic section assertions before generated-document synchronization.
readme = (REPO / "docs/09-kubernetes/README.md").read_text(encoding="utf-8")
chapter_links = re.findall(r"^\d+\. \[[^\]]+\]\(([^)]+\.md)\)$", readme, re.MULTILINE)
if len(chapter_links) != 32:
    raise RuntimeError(f"Expected 32 authoritative chapter links, found {len(chapter_links)}")
if chapter_links[-2:] != ["kubernetes-practical-walkthrough.md", "kubernetes-troubleshooting.md"]:
    raise RuntimeError(f"Unexpected final chapter ordering: {chapter_links[-2:]}")
if "- hpa.yaml\ncommonLabels:" in practical:
    raise RuntimeError("Base kustomization still owns HPA")
if "path: /spec/replicas" not in practical:
    raise RuntimeError("HPA ownership overlay is missing replicas removal")

run(os.environ.get("PYTHON_BIN", "python"), "scripts/update_glossary.py", "--write")
run(os.environ.get("PYTHON_BIN", "python"), "scripts/update_navigation.py", "--write")
run(
    os.environ.get("PYTHON_BIN", "python"),
    "scripts/audit_learning_depth.py",
    "--all-docs",
    "--report",
    "DOCUMENTATION-AUDIT.md",
    "--json",
    "documentation-audit.json",
)

# Remove the temporary workflow step and this script from the final PR diff.
workflow_path = REPO / ".github/workflows/knowledge-navigation.yml"
workflow = workflow_path.read_text(encoding="utf-8")
temporary_step = """
      - name: Close Section 09 full prose rewrite
        if: github.event_name == 'pull_request'
        shell: bash
        run: |
          set -euo pipefail
          "$PYTHON_BIN" scripts/close_section_09_full_prose.py
"""
if workflow.count(temporary_step) != 1:
    raise RuntimeError("Temporary workflow step was not found exactly once")
workflow_path.write_text(workflow.replace(temporary_step, "", 1), encoding="utf-8")
Path(__file__).unlink()

run("git", "config", "user.name", "github-actions[bot]")
run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
run("git", "add", "DOCUMENTATION-REVIEW-STATUS.md", "DOCUMENTATION-AUDIT.md", "documentation-audit.json", "GLOSSARY.md", "glossary", "docs", ".github/workflows/knowledge-navigation.yml", "scripts")

status = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO)
if status.returncode == 0:
    print("Section 09 closeout produced no changes")
    raise SystemExit(0)
if status.returncode != 1:
    raise RuntimeError("Unable to inspect staged closeout changes")

run("git", "commit", "-m", "docs: close Section 09 full prose rewrite")
run("git", "push", "origin", f"HEAD:{BRANCH}")
