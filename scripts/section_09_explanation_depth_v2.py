from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

for script in (
    ROOT / "scripts" / "section_09_depth_core.py",
    ROOT / "scripts" / "section_09_depth_platform.py",
    ROOT / "scripts" / "section_09_depth_practical.py",
    ROOT / "scripts" / "section_09_finalize.py",
):
    code = compile(script.read_text(encoding="utf-8"), str(script), "exec")
    exec(code, {"__name__": "__main__", "__file__": str(script)})

print("Section 09 preserve-first explanation-depth pass completed and finalized.")
