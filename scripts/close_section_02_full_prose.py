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


# Pull-request checkout normally points at a synthetic merge ref. Switch to the
# actual head branch so the closeout commit can be pushed without a merge commit.
run("git", "fetch", "origin", BRANCH)
run("git", "checkout", "-B", BRANCH, f"origin/{BRANCH}")

ledger_path = REPO / "DOCUMENTATION-REVIEW-STATUS.md"
ledger = ledger_path.read_text(encoding="utf-8")
new_row = (
    "| `02-networking-and-web` — Networking and Web Fundamentals | "
    "17/17 full prose and practical revalidation | Ready for user review | 2026-08-01 | "
    "Všetkých 16 pôvodných authoritative kapitol bolo kompletne prepísaných a pribudla "
    "17. praktická kapitola. Sekcia používa jeden plynulý Atlas request od application callu "
    "cez DNS, IPv4/IPv6 addressing, route a neighbor resolution, TCP/UDP a socket state, DHCP, "
    "NAT a firewall až po proxy, load balancing, HTTP, TLS/PKI, REST/WebSocket contract a "
    "preserve-first troubleshooting. Každá kapitola vkladá packet fields, CLI, konfiguráciu "
    "alebo HTTP ukážku priamo k vysvetľovanému transitionu a oddeľuje hostname/DNS answer, "
    "IP packet a route, transportný flow, socket/process, TLS peer identity, HTTP request a "
    "business operáciu. Nový `networking-practical-walkthrough.md` vytvára päť Linux network "
    "namespaces, dve bridge broadcast domény, dnsmasq resolver, edge DNAT a nftables policy, "
    "HAProxy TLS termination a round-robin load balancing, dva Python backends, runtime read-back, "
    "packet captures, zelený-health/chybný-business failure a post-DNAT firewall-identity failure "
    "s recovery a cleanupom. Python backend prešiel kompiláciou a všetkých sedem shell skriptov "
    "prešlo `bash -n`; repository workflow overuje navigation, glossary a learning depth, nie "
    "reálne vykonanie namespace labu proti Linux kernelu. Sekcia je pripravená na používateľskú "
    "kontrolu, nie automaticky Accepted, Verified ani Stable. |"
)
ledger, count = re.subn(
    r"^\| `02-networking-and-web`[^\n]*$",
    new_row,
    ledger,
    count=1,
    flags=re.MULTILINE,
)
if count != 1:
    raise RuntimeError(f"Section 02 ledger row: expected one match, found {count}")
ledger_path.write_text(ledger, encoding="utf-8")

section = REPO / "docs/02-networking-and-web"
readme = (section / "README.md").read_text(encoding="utf-8")
chapter_links = re.findall(r"^\d+\. \[[^\]]+\]\(([^)]+\.md)\)$", readme, re.MULTILINE)
if len(chapter_links) != 17:
    raise RuntimeError(f"Expected 17 authoritative chapter links, found {len(chapter_links)}")
if chapter_links[-2:] != ["networking-practical-walkthrough.md", "network-troubleshooting.md"]:
    raise RuntimeError(f"Unexpected final chapter ordering: {chapter_links[-2:]}")
for chapter in chapter_links:
    if not (section / chapter).is_file():
        raise RuntimeError(f"README references missing chapter: {chapter}")

practical = (section / "networking-practical-walkthrough.md").read_text(encoding="utf-8")
for required in (
    "net-client net-dns net-edge net-app1 net-app2",
    "Failure 1: zelený health, chybný business backend",
    "Failure 2: allow rule na nesprávnej NAT identite",
    "nft monitor trace",
    "sudo ./cleanup.sh",
):
    if required not in practical:
        raise RuntimeError(f"Practical walkthrough is missing required content: {required}")

troubleshooting = (section / "network-troubleshooting.md").read_text(encoding="utf-8")
for required in (
    "Path MTU Discovery",
    "Competing hypotheses",
    "Autoritatívna oprava",
    "business outcome",
):
    if required not in troubleshooting:
        raise RuntimeError(f"Troubleshooting chapter is missing required content: {required}")

python_bin = os.environ.get("PYTHON_BIN", "python")
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

# Remove the temporary workflow hook and this closeout script from the final diff.
workflow_path = REPO / ".github/workflows/knowledge-navigation.yml"
workflow = workflow_path.read_text(encoding="utf-8")
temporary_step = """
      - name: Close Section 02 full prose rewrite
        if: github.event_name == 'pull_request'
        shell: bash
        run: |
          set -euo pipefail
          "$PYTHON_BIN" scripts/close_section_02_full_prose.py
"""
if workflow.count(temporary_step) != 1:
    raise RuntimeError("Temporary workflow step was not found exactly once")
workflow_path.write_text(workflow.replace(temporary_step, "", 1), encoding="utf-8")
Path(__file__).unlink()

run("git", "config", "user.name", "github-actions[bot]")
run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
run(
    "git",
    "add",
    "DOCUMENTATION-REVIEW-STATUS.md",
    "DOCUMENTATION-AUDIT.md",
    "documentation-audit.json",
    "GLOSSARY.md",
    "glossary",
    "docs",
    ".github/workflows/knowledge-navigation.yml",
    "scripts",
)

status = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=REPO)
if status.returncode == 0:
    print("Section 02 closeout produced no changes")
    raise SystemExit(0)
if status.returncode != 1:
    raise RuntimeError("Unable to inspect staged closeout changes")

run("git", "commit", "-m", "docs: close Section 02 full prose rewrite")
run("git", "push", "origin", f"HEAD:{BRANCH}")
