from pathlib import Path

path = Path(__file__).resolve().with_name("section_17_block_25_28.py")
text = path.read_text(encoding="utf-8")
old = '"pitr", "realm export", "persisted sessions", "all nodes", "override", "bootstrap-admin", "kc-pay-77"'
new = '"pitr", "realm export", "persisted sessions", "všetky nodes", "override", "bootstrap-admin", "kc-pay-77"'
if new not in text:
    if text.count(old) != 1:
        raise RuntimeError("Expected exactly one backup semantic-gate token sequence")
    text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8", newline="\n")
print("Corrected the backup all-nodes semantic gate token.")
