from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Run both idempotent section passes from the current branch head.
runpy.run_path(str(ROOT / "scripts" / "section_07_terraform_depth.py"), run_name="__main__")
runpy.run_path(str(ROOT / "scripts" / "section_07_ansible_depth.py"), run_name="__main__")

print("Combined Section 07 explanation-depth pass applied.")
