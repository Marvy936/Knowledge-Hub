from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "DOCUMENTATION-REVIEW-STATUS.md"
FUTURE = ROOT / "FUTURE-IDENTITY-AI-ROADMAP.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise RuntimeError(f"Missing {label} anchor")


ledger = LEDGER.read_text(encoding="utf-8")
ledger = replace_once(
    ledger,
    "Tento súbor je ručne udržiavaný ledger section-level reviewov. Eviduje, ktoré hlavné sekcie boli kapitolu po kapitole preverené podľa aktuálneho learning-depth a authoring štandardu a sú pripravené na používateľskú kontrolu.",
    "Tento súbor je ručne udržiavaný ledger section-level reviewov. Eviduje, ktoré hlavné sekcie boli kapitolu po kapitole preverené podľa aktuálneho learning-depth a authoring štandardu a aký je ich aktuálny review state.",
    "ledger introduction",
)
ledger = replace_once(
    ledger,
    "Používateľ 2. augusta 2026 schválil aktuálny dokumentačný rozsah sekcií 00–17. Stav `User reviewed` vyjadruje prijatie dokumentácie, nie automatické vykonanie labov, runtime verifikáciu ani úroveň zvládnutia v `REVIEW.md`.",
    "Používateľ 2. augusta 2026 schválil aktuálny dokumentačný rozsah sekcií 00–17. Stav `User reviewed` vyjadruje prijatie dokumentácie, nie automatické vykonanie labov, runtime verifikáciu ani úroveň zvládnutia v `REVIEW.md`. Stavový stĺpec je autoritatívny; výrazy `Ready for user review` alebo `nie Accepted` v historických poznámkach opisujú predošlý dokumentačný gate a po tomto schválení už neurčujú aktuálny stav sekcie.",
    "authoritative approval note",
)
for number in range(18):
    prefix = f"| `{number:02d}-"
    row = next((line for line in ledger.splitlines() if line.startswith(prefix)), None)
    if row is None or "| User reviewed |" not in row:
        raise RuntimeError(f"Section {number:02d} is not User reviewed")
for number, expected in ((18, "0/26"), (19, "0/34"), (20, "0/37"), (21, "0/62")):
    prefix = f"| `{number:02d}-"
    row = next((line for line in ledger.splitlines() if line.startswith(prefix)), None)
    if row is None or expected not in row or "| In progress |" not in row:
        raise RuntimeError(f"Section {number:02d} activation row is invalid")
LEDGER.write_text(ledger.rstrip() + "\n", encoding="utf-8", newline="\n")

future = FUTURE.read_text(encoding="utf-8")
future = replace_once(future, "Navrhované poradie:", "Aktívne poradie:", "active ordering")
if future.count("Predbežný priečinok:") != 4 and "Predbežný priečinok:" in future:
    raise RuntimeError("Unexpected number of preliminary directory labels")
future = future.replace("Predbežný priečinok:", "Aktívny priečinok:")
for path in (
    "docs/18-machine-learning-fundamentals/",
    "docs/19-mlops-and-ml-platforms/",
    "docs/20-llm-and-genai-engineering/",
    "docs/21-ai-agents-and-intelligent-automation/",
):
    if path not in future:
        raise RuntimeError(f"Missing active AI section path: {path}")
FUTURE.write_text(future.rstrip() + "\n", encoding="utf-8", newline="\n")

print("Finalized user-review authority and active AI directory status.")
