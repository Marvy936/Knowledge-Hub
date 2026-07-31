from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "docs/08-container-fundamentals-and-docker/README.md"
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label}, found {count}")
    return text.replace(old, new, 1)


readme = README.read_text(encoding="utf-8")

readme = replace_once(
    readme,
    "18. [Praktický Docker release od source zmeny po overený runtime](docker-practical-walkthrough.md)",
    "18. [Praktický Docker projekt od prázdneho adresára po overený Compose runtime](docker-practical-walkthrough.md)",
    "authoritative walkthrough title",
)

old_description = """Kapitola [Praktický Docker release od source zmeny po overený runtime](docker-practical-walkthrough.md) používa existujúcu službu `payments-api` ako jeden súvislý release scenár. Neodbieha do implementácie aplikácie; sústreďuje sa na Docker mechanizmus od build contextu a multi-stage graphu cez explicitný test target, image config/layers/digest, registry publication, constrained container create/start, PID 1, volume a network identity až po Compose reconciliation, multi-platform read-back a business verification.

Text je prepracovaný v rovnakom prose-first rytme ako Keycloak a CI/CD: najprv vysvetlí dominantný source-to-runtime model, potom presný release subject, konkrétne Dockerfile a Compose rozhodnutia, dôkazové hranice jednotlivých príkazov a connected incident `CTR-PAY-81`. Incident spája rozdielnych builderov, mutable tag, neúplný platform scan, plytký health oracle a nekompatibilný volume ownership do jedného diagnostického a recovery flowu.
"""

new_description = """Kapitola [Praktický Docker projekt od prázdneho adresára po overený Compose runtime](docker-practical-walkthrough.md) ide rovnakým detailným walkthrough štýlom ako praktická Helm kapitola. Od prázdneho adresára vytvorí minimálnu Go HTTP aplikáciu, unit a forbidden-path test, `.dockerignore`, celý multi-stage Dockerfile, samostatný BuildKit test target, lokálny runtime image, network, named volume a hardenovaný non-root container. Každý súbor a každý významný príkaz je vložený priamo do výkladu a bezprostredne vysvetlený: čo je jeho vstup, čo zmení, aký output očakávame a čo zelený výsledok ešte nedokazuje.

Druhá polovica kapitoly skladá celý `compose.yaml`, najprv kontroluje resolved model cez `docker compose config`, potom overuje container-local health, Compose DNS, host-published port a volume-backed business write/read. Nasleduje recreate a druhý nezmenený run, configuration-driven replacement, zámerne chybný bind na container loopback, volume-permission failure, evidence-preserving diagnostika, recovery, multi-platform publication, image-index read-back, digest-pinned consumption a bezpečný cleanup. Aplikačný kód bol lokálne formátovaný a overený cez `go test`; Docker a registry commands zostávajú dokumentačne auditované príklady, kým sa nespustia proti reálnemu Engine-u a registry.
"""

readme = replace_once(
    readme,
    old_description,
    new_description,
    "walkthrough description",
)

README.write_text(readme, encoding="utf-8")

ledger_lines = LEDGER.read_text(encoding="utf-8").splitlines()
prefix = "| `08-container-fundamentals-and-docker` — Container Fundamentals and Docker |"
replacement = (
    "| `08-container-fundamentals-and-docker` — Container Fundamentals and Docker "
    "| 19/19 prose-first + practical walkthrough revalidation | Ready for user review "
    "| 2026-07-31 | Pôvodných 18 authoritative kapitol zostáva strict revalidovaných. "
    "Praktická kapitola `docker-practical-walkthrough.md` bola kompletne prepísaná od nuly "
    "podľa detailného Helm walkthrough vzoru. Vytvára reálny Go project, unit a forbidden-path "
    "testy, `.dockerignore`, celý multi-stage Dockerfile, samostatný BuildKit test target, image "
    "inspect/export, ručný `docker create/start/inspect` lifecycle, non-root read-only runtime, "
    "named-volume persistence a celý Compose model. Walkthrough vysvetľuje každý súbor a command "
    "bezprostredne pri kóde, oddeľuje local health, Compose DNS, host port a business write/read, "
    "overuje recreate, druhý nezmenený run a configuration replacement a obsahuje reprodukovateľný "
    "broken-bind aj volume-permission failure s diagnostikou a recovery. Záver pokrýva multi-platform "
    "publication, index/platform digest read-back, digest-pinned consumption a cleanup. Go source "
    "prešiel lokálnym `gofmt` a `go test`; repository workflow validuje documentation depth a "
    "navigation, nie reálny Docker Engine alebo registry. Sekcia je pripravená na používateľskú "
    "kontrolu, nie automaticky používateľsky schválená, Accepted, Verified ani Stable. |"
)

matches = [index for index, line in enumerate(ledger_lines) if line.startswith(prefix)]
if len(matches) != 1:
    raise RuntimeError(f"Expected one Section 08 ledger row, found {len(matches)}")

ledger_lines[matches[0]] = replacement
LEDGER.write_text("\n".join(ledger_lines) + "\n", encoding="utf-8")
