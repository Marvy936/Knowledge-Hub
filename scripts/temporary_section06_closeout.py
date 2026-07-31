from __future__ import annotations

import re
from pathlib import Path

README = Path("docs/06-gitlab/README.md")
LEDGER = Path("DOCUMENTATION-REVIEW-STATUS.md")

readme = README.read_text(encoding="utf-8")
old_status = """## Aktuálny stav revalidácie

| Blok | Kapitoly | Stav |
|---|---:|---|
| `GL-PAY-72` — access, merge a protected boundaries | 0/3 | In progress |
| `GL-PAY-73` — CI graph, runner a secret capabilities | 0/3 | Not started |
| `GL-PAY-74` — artifacts, registry, deployments a security closure | 0/4 | Not started |

Celkový authoritative stav: **0/10 · In progress**.
"""
new_status = """## Aktuálny stav revalidácie

| Blok | Kapitoly | Stav |
|---|---:|---|
| `GL-PAY-72` — access, merge a protected boundaries | 3/3 | Complete |
| `GL-PAY-73` — CI graph, runner a secret capabilities | 3/3 | Complete |
| `GL-PAY-74` — artifacts, registry, deployments a security closure | 4/4 | Complete |

Celkový authoritative stav: **10/10 · Ready for user review**. Tento stav znamená dokončený repository review a strict/practical gate; neznamená automatické používateľské schválenie, Accepted, Verified ani Stable.
"""
if old_status not in readme:
    raise SystemExit("Section 06 README status block was not found")
readme = readme.replace(old_status, new_status, 1)
README.write_text(readme, encoding="utf-8", newline="\n")

ledger = LEDGER.read_text(encoding="utf-8")
row = (
    "| `06-gitlab` — GitLab | 10/10 Keycloak-style prose-first practical revalidation | Ready for user review | 2026-07-31 | "
    "Všetkých 10 authoritative kapitol bolo kompletne znovu spracovaných v troch connected blokoch `GL-PAY-72` až `GL-PAY-74`. "
    "Sekcia teraz používa súvislý GitLab chain od exact group/project namespace subjectu cez direct, inherited, shared a token effective access, immutable MR decision, protected source/runtime boundaries, resolved CI graph, runner/executor trust a short-lived secret capability po artifact/report/cache authority, multi-platform registry digest, deployment/runtime correlation a security-remediation closure. "
    "`GL-PAY-72` odhaľuje project transfer, hidden inherited/shared access, stale approval po force-pushi a environment-name/direct-credential bypass. `GL-PAY-73` spája mutable include, duplicate pipeline graph, protected persistent runner, shared cache a broad OIDC/static-secret capability. `GL-PAY-74` spája incomplete report inventory, mutable registry graph, GitOps false deployment success, secret dismissal bez provider revocation a source fix bez deployed-digest replacementu. "
    "Kapitoly obsahujú konkrétne GitLab REST API, `.gitlab-ci.yml`, runner/executor, ID-token/Vault, artifact/cache, OCI registry, Kubernetes runtime a security-report walkthroughy; každý významný output vysvetľuje proof boundary. "
    "Recovery overuje effective access revocation, forbidden merge/deploy paths, cold runner/cache path, durable artifact identity, runtime digest a second operation. README, ordering, navigation a ledger sú synchronizované; finálny clean workflow je acceptance gate. Sekcia je pripravená na používateľskú kontrolu, nie automaticky používateľsky schválená, Accepted, Verified ani Stable. |"
)
pattern = r"^\| `06-gitlab` — GitLab \|.*$"
if not re.search(pattern, ledger, flags=re.MULTILINE):
    raise SystemExit("Section 06 ledger row was not found")
ledger = re.sub(pattern, row, ledger, count=1, flags=re.MULTILINE)
LEDGER.write_text(ledger, encoding="utf-8", newline="\n")
