from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMP_PATHS = [
    ".github/workflows/section-17-block-29-30.yml",
    "scripts/section_17_block_29_30.py",
    ".github/workflows/section-17-block-29-30-closeout.yml",
    "scripts/section_17_block_29_30_closeout.py",
    ".github/workflows/section-17-block-29-30-closeout2.yml",
    "scripts/section_17_block_29_30_closeout2.py",
    ".github/workflows/section-17-final-verify.yml",
    "scripts/section_17_final_verify.py",
    ".github/workflows/section-17-final-cleanup.yml",
    "scripts/section_17_cleanup.py",
]

for relative in TEMP_PATHS:
    path = ROOT / relative
    if path.exists():
        path.unlink()
        print(f"removed {relative}")
