from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECTION = ROOT / "docs" / "17-keycloak-and-identity-platform"
README = (SECTION / "README.md").read_text(encoding="utf-8")
LEDGER = (ROOT / "DOCUMENTATION-REVIEW-STATUS.md").read_text(encoding="utf-8")
AUDIT = (ROOT / "DOCUMENTATION-AUDIT.md").read_text(encoding="utf-8")

if "Aktuálny authoritative stav sekcie je **30/30 · Ready for user review**" not in README:
    raise RuntimeError("Section 17 README is not at 30/30 Ready for user review")

if "| `17-keycloak-and-identity-platform` — Keycloak and Identity Platform | 30/30 authoritative drafting and section closeout | Ready for user review |" not in LEDGER:
    raise RuntimeError("Central review ledger is not at Section 17 30/30 Ready for user review")

if "### `docs/17-keycloak-and-identity-platform/" in AUDIT:
    raise RuntimeError("Section 17 still appears in the critical/high learning-depth review queue")

ordered_links = []
for line in README.splitlines():
    stripped = line.strip()
    if not stripped or not stripped[0].isdigit() or ". [" not in stripped or "](" not in stripped:
        continue
    prefix, rest = stripped.split(". [", 1)
    if not prefix.isdigit():
        continue
    number = int(prefix)
    if 1 <= number <= 30:
        target = rest.rsplit("](", 1)[1].rstrip(")")
        ordered_links.append((number, target))

if [number for number, _ in ordered_links] != list(range(1, 31)):
    raise RuntimeError(f"Expected authoritative ordering 1..30, got {[n for n, _ in ordered_links]}")

missing = [target for _, target in ordered_links if not (SECTION / target).exists()]
if missing:
    raise RuntimeError(f"README links to missing authoritative chapters: {missing}")

for number, target in ordered_links:
    text = (SECTION / target).read_text(encoding="utf-8")
    if len(text.split()) < 850:
        raise RuntimeError(f"Chapter {number} {target} is unexpectedly short")
    if text.count("```") < 4:
        raise RuntimeError(f"Chapter {number} {target} lacks executable/model surface")
    if "<!-- KNOWLEDGE-NAVIGATION:START -->" not in text:
        raise RuntimeError(f"Chapter {number} {target} lacks generated navigation")

print("Section 17 final verification passed: 30/30, ledger ready, all chapters present, no critical/high queue entry.")
