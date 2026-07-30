#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]

readme = root / "docs/14-sre-and-operations/README.md"
text = readme.read_text(encoding="utf-8")
old = "Aktuálny authoritative stav sekcie je **15/15 · Ready for user review**. Všetky authoritative kapitoly, navigation väzby, glossary, audit artifacts a section-level consistency gate prešli."
new = "Aktuálny authoritative stav sekcie je **15/15 · Ready for user review**. Všetkých 15 kapitol bolo po pôvodnom authoring passe kompletne znovu spracovaných v štyroch prose-first strict blokoch; každá kapitola má nulové critical, high a medium learning-depth findings. Authoritative ordering, connected incidents, navigation, glossary a section-level consistency zostávajú zachované."
if text.count(old) != 1:
    raise SystemExit("README status sentence not found exactly once")
readme.write_text(text.replace(old, new), encoding="utf-8")

ledger = root / "DOCUMENTATION-REVIEW-STATUS.md"
lines = ledger.read_text(encoding="utf-8").splitlines()
prefix = "| `14-sre-and-operations` — SRE and Operations |"
indexes = [i for i, line in enumerate(lines) if line.startswith(prefix)]
if len(indexes) != 1:
    raise SystemExit(f"Expected one SRE ledger row, found {len(indexes)}")
replacement = "| `14-sre-and-operations` — SRE and Operations | 15/15 prose-first strict revalidation | Ready for user review | 2026-07-30 | Všetkých 15 authoritative kapitol bolo kompletne znovu spracovaných v štyroch strict blokoch podľa nového Keycloak-style prose-first gate-u. Prvý blok spája `SRE-PAY-52` cez `business capability → exact reliability subject → user-centered SLI/SLO → error-budget governance → operational demand/toil → safe recovery`; broker backlog a unsafe cleanup odstránili `4 182` nepublikovaných commands, spotrebovali `83.64 %` completion budgetu a vytvorili `418 minút` privileged toil-u. Druhý blok spája `SRE-PAY-53` cez `forecast/SLO → logical demand a amplification → effective capacity/overload contract → incident declaration/command → qualified on-call ownership/escalation → state-classified runbook`; zachováva demand `2 800` unique settlements/s, safe capacity `1 850/s`, 24-minútové declaration delay, reset `62 418` lease-ov a `143` sent-unknown operations. Tretí blok spája `SRE-PAY-54` cez evidence-backed RCA, causal graph, blameless learning a mechanism closure s protected consistency groupom, clean-point restore, provider reconciliation a actual RPO/RTO; missing tenant scope broad-archived `186 420` rows, poškodil `7 842` active records a recovery trvala `3 h 48 min 53 s`. Záverečný blok spája `SRE-PAY-55` cez versionovaný DR recovery graph, writer fencing, provider/KMS/broker/DNS recovery, falsifikovateľný chaos experiment a evidence-classified operational readiness; pôvodná safe recovery trvala `2 h 19 min`, narrow `CH-PAY-41` bola odmietnutá ako regional evidence a repeat `CH-PAY-55-2` po remediation prešiel s business recovery `31 min 42 s`, recovered-point gapom 48 sekúnd a nulovými lost/duplicate intents. Všetky kapitoly používajú explicitné subject/generation/evidence boundaries, positive/recovery/failure/forbidden acceptance paths, second-operation alebo alternate-scenario validation a nulové critical/high/medium audit findings. README ordering 15/15, obojsmerný navigation chain `13-security-and-identity/zero-trust.md ↔ Reliability` cez celú sekciu po `Operational readiness ↔ 15-databases-and-distributed-systems/relational-vs-non-relational-databases.md`, glossary fragments `14a`–`14d` a current Google SRE, NIST a Principles of Chaos Engineering sources boli zachované. Sekcia je pripravená na používateľskú kontrolu, nie automaticky používateľsky schválená, Accepted, Verified ani Stable. |"
lines[indexes[0]] = replacement
ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("SRE prose-first revalidation closeout applied")
