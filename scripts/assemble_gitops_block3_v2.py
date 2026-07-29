#!/usr/bin/env python3
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
parts = sorted(SCRIPTS.glob(".gitops_block3_v2_*.txt"))
expected_names = [f".gitops_block3_v2_{i:03d}.txt" for i in range(25)]
actual_names = [p.name for p in parts]
if actual_names != expected_names:
    raise SystemExit(f"Unexpected GitOps block 3 v2 fragments: {actual_names}")

payload = "".join(p.read_text(encoding="ascii") for p in parts)
expected_length = 60540
expected_sha256 = "9b90316b6c21fd36f1508bd61fc429f70fdd39a2712937a5a0750152688ff400"
actual_sha256 = hashlib.sha256(payload.encode("ascii")).hexdigest()
if len(payload) != expected_length or actual_sha256 != expected_sha256:
    raise SystemExit(
        "GitOps block 3 payload integrity failure: "
        f"length={len(payload)} sha256={actual_sha256}"
    )

for old in SCRIPTS.glob(".gitops_block3_payload_*.txt"):
    old.unlink()
(SCRIPTS / ".gitops_block3_payload_00.txt").write_text(
    payload, encoding="ascii", newline="\n"
)
print(f"Assembled verified GitOps block 3 payload: {len(payload)} bytes {actual_sha256}")
