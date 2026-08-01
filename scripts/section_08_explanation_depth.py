from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

for script in (
    ROOT / "scripts" / "section_08_depth_build.py",
    ROOT / "scripts" / "section_08_depth_practical.py",
):
    code = compile(script.read_text(encoding="utf-8"), str(script), "exec")
    exec(code, {"__name__": "__main__", "__file__": str(script)})

print("Section 08 explanation-depth pass completed.")
# Explicit retrigger after workflow registration.
