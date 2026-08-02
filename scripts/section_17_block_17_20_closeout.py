from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "17-keycloak-and-identity-platform"

replacements = {
    SECTION / "events-audit-metrics-observability.md": (
        "## 12. Acceptance matrix\n\nPositive:",
        "## 12. Acceptance matrix\n\nAcceptance musí overiť celý evidence chain, nie iba existenciu jedného eventu alebo zelenej metriky. Positive path dokazuje complete intended journey, recovery path dokazuje signalizovanú stratu a obnovenú durable delivery a forbidden path dokazuje, že observability surface ani ambiguous target nemožno zneužiť. Každý test sa viaže na rovnaký deployment, node population, realm, client a operation identity.\n\nPositive:",
    ),
    SECTION / "themes-email-templates-localization.md": (
        "## 1. Dominantný render-to-operation lifecycle\n\n```text",
        "## 1. Dominantný render-to-operation lifecycle\n\nTheme lifecycle začína ešte pred renderom: release vyberie artifact a parent generation, realm zvolí theme a request určí journey aj locale. Rendered HTML alebo email je iba medzistav; authoritative výsledok vznikne až po browser/email interaction, Keycloak transaction validation a user/session mutation. Diagram preto spája supply-chain, server render, client behavior a identity outcome do jednej testovateľnej cesty.\n\n```text",
    ),
}

for path, (old, new) in replacements.items():
    text = path.read_text(encoding="utf-8")
    if new in text:
        continue
    if text.count(old) != 1:
        raise RuntimeError(f"Expected exactly one closeout marker in {path}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")

print("Applied focused Section 17 block 17-20 audit closeout.")
