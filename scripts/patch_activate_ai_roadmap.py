from pathlib import Path

path = Path(__file__).with_name("activate_ai_roadmap.py")
text = path.read_text(encoding="utf-8")
old = '("MLOps and ML Platforms", None),'
new = '("MLOps and ML Platforms", "LLM and GenAI Engineering"),'
if old in text:
    text = text.replace(old, new, 1)
elif new not in text:
    raise RuntimeError("MLOps extraction boundary anchor not found")
path.write_text(text, encoding="utf-8", newline="\n")
print("Corrected MLOps extraction boundary for the activation run.")
