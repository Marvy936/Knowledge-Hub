from __future__ import annotations

import re
from pathlib import Path

README = Path("docs/05-ci-cd-and-release/README.md")
LEDGER = Path("DOCUMENTATION-REVIEW-STATUS.md")

readme = README.read_text(encoding="utf-8")
readme = readme.replace(
    "Sekcia sa po staršom strict passe znovu spracúva podľa rovnakého prose-first a practical-example štandardu ako Keycloak a novšie authoritative kapitoly. Silný existujúci obsah sa zachová tam, kde už vysvetľuje mechanizmus, no každá kapitola musí mať explicitný subject/generation model, reálne príkazy alebo konfiguráciu, vysvetlené read-back hranice, connected incident, authoritative recovery a allowed aj forbidden validation path.",
    "Sekcia bola po staršom strict passe kompletne znovu spracovaná podľa rovnakého prose-first a practical-example štandardu ako Keycloak a novšie authoritative kapitoly. Všetkých 23 kapitol teraz používa explicitný subject/generation model, reálne príkazy alebo konfiguráciu, vysvetlené read-back hranice, connected incident, authoritative recovery a allowed, forbidden aj second-operation validation path.",
)

old_status = """## Aktuálny stav revalidácie

| Blok | Kapitoly | Stav |
|---|---:|---|
| `REL-PAY-66` — integration, delivery, deployment a pipeline runtime | 0/4 | In progress |
| `REL-PAY-67` — triggers, artifacts, environments, gates a Pipeline as Code | 0/4 | Not started |
| `REL-PAY-68` — reusable pipelines, versions a release management | 0/4 | Not started |
| `REL-PAY-69` — deployment strategies | 0/4 | Not started |
| `REL-PAY-70` — experiments a runtime exposure controls | 0/4 | Not started |
| `REL-PAY-71` — progressive delivery, recovery a data compatibility | 0/3 | Not started |

Celkový authoritative stav: **0/23 · In progress**.
"""
new_status = """## Aktuálny stav revalidácie

| Blok | Kapitoly | Stav |
|---|---:|---|
| `REL-PAY-66` — integration, delivery, deployment a pipeline runtime | 4/4 | Complete |
| `REL-PAY-67` — triggers, artifacts, environments, gates a Pipeline as Code | 4/4 | Complete |
| `REL-PAY-68` — reusable pipelines, versions a release management | 4/4 | Complete |
| `REL-PAY-69` — deployment strategies | 4/4 | Complete |
| `REL-PAY-70` — experiments a runtime exposure controls | 4/4 | Complete |
| `REL-PAY-71` — progressive delivery, recovery a data compatibility | 3/3 | Complete |

Celkový authoritative stav: **23/23 · Ready for user review**. Tento stav znamená dokončený repository review a úspešný strict/practical gate; neznamená automatické používateľské schválenie, Accepted, Verified ani Stable.
"""
if old_status not in readme:
    raise SystemExit("Section 05 README status block was not found")
readme = readme.replace(old_status, new_status, 1)
README.write_text(readme, encoding="utf-8", newline="\n")

ledger = LEDGER.read_text(encoding="utf-8")
row = (
    "| `05-ci-cd-and-release` — CI/CD and Release Engineering | 23/23 Keycloak-style prose-first practical revalidation | Ready for user review | 2026-07-31 | "
    "Všetkých 23 authoritative kapitol bolo kompletne znovu spracovaných v šiestich connected blokoch `REL-PAY-66` až `REL-PAY-71`. "
    "Sekcia používa jednotný chain od exact source/target/integration candidate-u cez trusted resolved pipeline graph, build-once immutable artifact, complete evidence, release manifest a environment generation po deployment, traffic/feature/audience/data exposure, business acceptance a per-layer recovery. "
    "`REL-PAY-66` uzatvára stale-green candidate, hidden runner/workspace input, rebuilt artifact a nejednoznačný automatic production verdict. `REL-PAY-67` spája event trust, shared-cache poisoning, environment generation, subject-bound gate/approval a resolved Pipeline-as-Code graph. "
    "`REL-PAY-68` spája reusable provider-consumer contract, complete matrix fan-in, multi-platform OCI artifact graph, evidence-backed SemVer compatibility a immutable release lifecycle. `REL-PAY-69` oddeľuje recreate exclusive-slot fencing, rolling capacity/mixed-version safety, blue-green cutover a stable canary evidence. "
    "`REL-PAY-70` rozlišuje causal A/B assignment, hard-isolated shadow execution, historical ring membership a configured-versus-loaded feature-flag generation. `REL-PAY-71` uzatvára multi-axis progressive delivery, state-delta recovery a version-safe expand–migrate–contract database protocol. "
    "Každá kapitola obsahuje exact subject/generation/evidence boundaries, reálne Git, Docker/OCI, GitHub Actions, Kubernetes, Helm, OPA/Rego, PromQL, SQL alebo API walkthroughy a vysvetlenie, čo output preukazuje a nepreukazuje. "
    "Recovery overuje original, forbidden, adjacent-cohort a second-operation outcomes. README, authoritative ordering a navigation sú synchronizované; finálny clean documentation workflow je acceptance gate. Sekcia je pripravená na používateľskú kontrolu, nie automaticky používateľsky schválená, Accepted, Verified ani Stable. |"
)
pattern = r"^\| `05-ci-cd-and-release` — CI/CD and Release Engineering \|.*$"
if not re.search(pattern, ledger, flags=re.MULTILINE):
    raise SystemExit("Section 05 ledger row was not found")
ledger = re.sub(pattern, row, ledger, count=1, flags=re.MULTILINE)
LEDGER.write_text(ledger, encoding="utf-8", newline="\n")
