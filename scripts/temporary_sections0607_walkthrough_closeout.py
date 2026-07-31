from __future__ import annotations

import re
from pathlib import Path

SECTION_06 = Path("docs/06-gitlab/README.md")
SECTION_07 = Path("docs/07-infrastructure-as-code-and-configuration-management/README.md")
LEDGER = Path("DOCUMENTATION-REVIEW-STATUS.md")


def insert_ordered_entry(text: str, anchor_path: str, label: str, path: str) -> str:
    if f"]({path})" in text:
        return text

    heading = "## Authoritative poradie — aktívne kapitoly"
    start = text.index(heading)
    body_start = text.index("\n", start) + 1
    end = text.index("\n\nPo tejto sekcii", body_start)
    block = text[body_start:end]
    lines = [line for line in block.splitlines() if line.strip()]

    entries: list[str] = []
    inserted = False
    for line in lines:
        match = re.match(r"^\d+\.\s+(.*)$", line)
        if not match:
            raise RuntimeError(f"Unexpected ordering line: {line}")
        entry = match.group(1)
        entries.append(entry)
        if f"]({anchor_path})" in entry:
            entries.append(f"[{label}]({path})")
            inserted = True

    if not inserted:
        raise RuntimeError(f"Ordering anchor {anchor_path} not found")

    rebuilt = "\n".join(f"{index}. {entry}" for index, entry in enumerate(entries, start=1))
    return text[:body_start] + "\n" + rebuilt + text[end:]


def insert_before(text: str, marker: str, content: str) -> str:
    if content.splitlines()[0] in text:
        return text
    return text.replace(marker, content.rstrip() + "\n\n" + marker, 1)


section_06 = SECTION_06.read_text(encoding="utf-8")
section_06 = insert_ordered_entry(
    section_06,
    "gitlab-ci-cd-syntax.md",
    "Praktický GitLab pipeline od source change po overený deployment",
    "gitlab-pipeline-practical-walkthrough.md",
)

section_06_practical = """## Hlavný praktický walkthrough

Kapitola [Praktický GitLab pipeline od source change po overený deployment](gitlab-pipeline-practical-walkthrough.md) vytvára jeden celý executable release flow namiesto izolovaných YAML fragmentov. Začína repository layoutom a malou HTTP aplikáciou, pokračuje Dockerfile-om a Kubernetes manifestom a následne prechádza kompletný `.gitlab-ci.yml`.

Walkthrough vysvetľuje `workflow: rules`, job `rules`, `needs` DAG, JUnit a dotenv reports, trusted Docker build runner, build-once image digest, registry read-back, scanner nad exact digestom, server-side dry-run, `resource_group`, protected staging/production environments, rollout status, live Deployment image a Service/EndpointSlice smoke test. Pri každom kroku oddeľuje source YAML, resolved graph, runner execution, artifact/report state, GitLab deployment record, Kubernetes live state a aplikačný outcome.

Praktický acceptance contract pre túto sekciu preto vyžaduje, aby čitateľ vedel nielen vysvetliť GitLab concepts, ale aj prejsť konkrétny pipeline riadok po riadku, určiť trust boundary každého jobu, identifikovať artifact hand-off a dokázať, že staging aj production používajú rovnaký immutable image digest. Missing scanner job, mutable tag, nesprávny cluster context a rollout-ready-but-business-broken paths musia byť diagnostikovateľné z konkrétnych outputs.
"""
section_06 = insert_before(section_06, "## Connected learning scenarios", section_06_practical)
section_06 = section_06.replace(
    "1. všetkých 10 kapitol používa connected Keycloak-style prose a dominantný lifecycle;",
    "1. všetkých 11 authoritative kapitol vrátane end-to-end pipeline walkthroughu používa connected Keycloak-style prose, dominantný lifecycle a primeraný executable surface;",
)
section_06 = section_06.replace(
    "8. strict learning-depth audit je 10/10 `0/0/0` a practical gate nemá failures;",
    "8. strict learning-depth audit je 11/11 bez critical/high/medium findings a practical gate nemá failures;",
)
section_06 = re.sub(
    r"## Aktuálny stav revalidácie\n.*\Z",
    """## Aktuálny stav revalidácie

| Blok | Kapitoly | Stav |
|---|---:|---|
| `GL-PAY-72` — access, merge a protected boundaries | 3/3 | Complete |
| `GL-PAY-73` — CI graph, runner a secret capabilities | 3/3 | Complete |
| `GL-PAY-74` — artifacts, registry, deployments a security closure | 4/4 | Complete |
| End-to-end GitLab pipeline walkthrough | 1/1 | Complete |

Celkový authoritative stav: **11/11 · Ready for user review**. Pôvodný prose-first pass zostáva zachovaný a nový walkthrough dopĺňa chýbajúcu súvislú code-execution vrstvu. Tento stav neznamená automatické používateľské schválenie, Accepted, Verified ani Stable.
""",
    section_06,
    flags=re.DOTALL,
)
SECTION_06.write_text(section_06, encoding="utf-8", newline="\n")

section_07 = SECTION_07.read_text(encoding="utf-8")
section_07 = insert_ordered_entry(
    section_07,
    "terraform-testing-and-policy.md",
    "Praktický Terraform projekt od prázdneho adresára po overený remote state",
    "terraform-practical-walkthrough.md",
)
section_07 = insert_ordered_entry(
    section_07,
    "ansible-idempotency.md",
    "Praktický Ansible projekt od inventory po overený rolling configuration rollout",
    "ansible-practical-walkthrough.md",
)
section_07 = section_07.replace("Všetkých 19 kapitol", "Všetkých 21 kapitol", 1)

section_07_practical = """## Hlavné praktické walkthroughy

Sekcia obsahuje dve referenčné executable kapitoly, ktoré skladajú predchádzajúce concepts do celého projektu.

[Praktický Terraform projekt od prázdneho adresára po overený remote state](terraform-practical-walkthrough.md) vytvára root module, reusable AWS network module, typed variables, stable `for_each` identities, outputs, S3 backend configuration, `.terraform.lock.hcl` subject, native `.tftest.hcl` happy aj forbidden test, saved plan, `terraform show -json`, `jq` destructive-action gate, Rego policy, apply presne schváleného planu, state inspection, AWS CLI remote read-back a second no-op plan. Obsahuje aj GitLab plan/policy/apply flow a recovery pri nesprávnom backend key, chýbajúcom `moved` blocku a úspešnej remote mutation bez state commitu.

[Praktický Ansible projekt od inventory po overený rolling configuration rollout](ansible-practical-walkthrough.md) vytvára `ansible.cfg`, pinned collection manifest, static inventory s logical a immutable asset identity, expected-vs-resolved fleet manifest, `group_vars`, role defaults, Jinja template, application-level `validate`, handler, rolling `serial` playbook, drain/restart/readiness/rejoin transition, per-host loaded-generation oracle, load-balancer verification a druhý `changed=0` run. Obsahuje aj GitLab validation/check/apply jobs a partial-fleet recovery.

Tieto walkthroughy sú referenčným štandardom pre code-oriented learning. Samostatný HCL alebo YAML snippet je užitočný iba vtedy, keď je jasné, do ktorého súboru patrí, aké inputs používa, aký graph alebo target set z neho vznikne, akú mutation vykoná a akým independent read-backom sa overí výsledok.
"""
section_07 = insert_before(section_07, "## Connected learning scenarios", section_07_practical)
section_07 = section_07.replace(
    "1. všetkých 19 authoritative kapitol používa connected Keycloak-style prose a dominantný lifecycle;",
    "1. všetkých 21 authoritative kapitol vrátane Terraform a Ansible end-to-end walkthroughov používa connected Keycloak-style prose, dominantný lifecycle a primeraný executable surface;",
)
section_07 = re.sub(
    r"## Aktuálny stav revalidácie\n.*\Z",
    """## Aktuálny stav revalidácie

| Blok | Kapitoly | Stav |
|---|---:|---|
| `IAC-PAY-75` — Terraform authority, graph a state binding | 5/5 | Complete |
| `IAC-PAY-76` — backend, modules a address/lifecycle migration | 3/3 | Complete |
| `IAC-PAY-77` — drift, testing a policy | 2/2 | Complete |
| `IAC-PAY-78` — Ansible execution, inventory a configuration | 5/5 | Complete |
| `IAC-PAY-79` — reusable content, secrets, idempotency a ownership | 4/4 | Complete |
| Terraform a Ansible end-to-end practical walkthroughs | 2/2 | Complete |

Celkový authoritative stav: **21/21 · Ready for user review**. Pôvodný 19-kapitolový prose-first pass zostáva zachovaný a dva nové walkthroughy dopĺňajú súvislé code, command, output a runtime-verification flows. Tento stav neznamená automatické používateľské schválenie, Accepted, Verified ani Stable.
""",
    section_07,
    flags=re.DOTALL,
)
SECTION_07.write_text(section_07, encoding="utf-8", newline="\n")

ledger = LEDGER.read_text(encoding="utf-8")


def update_ledger_row(text: str, prefix: str, old_count: str, new_count: str, note: str) -> str:
    pattern = rf"^\| {re.escape(prefix)} \|.*$"
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        raise RuntimeError(f"Ledger row not found: {prefix}")
    row = match.group(0)
    row = row.replace(old_count, new_count, 1)
    row = re.sub(r"\| 2026-07-\d{2} \|", "| 2026-07-31 |", row, count=1)
    if note not in row:
        if not row.endswith(" |"):
            raise RuntimeError(f"Unexpected ledger row ending: {prefix}")
        row = row[:-2] + " " + note + " |"
    return text[: match.start()] + row + text[match.end() :]


ledger = update_ledger_row(
    ledger,
    "`06-gitlab` — GitLab",
    "10/10 strict revalidation",
    "11/11 prose-first practical revalidation",
    "Doplnená bola samostatná end-to-end pipeline kapitola s kompletným `.gitlab-ci.yml`, Docker/registry digest hand-offom, JUnit a dotenv reports, scannerom, Kubernetes staging/production deployom, live-image read-backom a Service smoke testom; README a navigation teraz evidujú 11 authoritative kapitol.",
)
ledger = update_ledger_row(
    ledger,
    "`07-infrastructure-as-code` — Infrastructure as Code and Configuration Management",
    "19/19 strict revalidation",
    "21/21 prose-first practical revalidation",
    "Doplnené boli dva samostatné executable walkthroughy: kompletný Terraform module/backend/test/plan/policy/apply/remote-read-back flow a kompletný Ansible inventory/role/template/handler/rolling-fleet/second-run flow; README a navigation teraz evidujú 21 authoritative kapitol.",
)
LEDGER.write_text(ledger, encoding="utf-8", newline="\n")
