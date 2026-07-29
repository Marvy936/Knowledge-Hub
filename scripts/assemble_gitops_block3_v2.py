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

expected_part_hashes = [
    "905e56f0a1f7a0b930a56c5fd3ea45905b14fac13643a77461d97034f80bb0c7",
    "767d6d8e869e232634af81605a5611563b46b34ea92e810559799f47a7e33a44",
    "47df757e0576ffa8631ed78090df52818083e49751f40885266a930fe228ea62",
    "b6ae349e2bbc7451ac7dcf52e1a1bd2dfd0cc371e77b6beb52b9dfae8a04b3d3",
    "4ba01a2d5cf41e353060fc2d7315edec7f940eaccef6cf4e1c85b0bd3215a302",
    "8e681364bd9126f955c0e796a04574dfab0f24edd501df4fa55d399cefc3f2f7",
    "9a7889d22d08dfa5f148a0dffa712864b9f8003b5da51322f48f5017647b312f",
    "d3d87b086625fbaf92a27c488508ce216286fa290f4a97cf7ed96baaeae78cb4",
    "beaa7a4f98b72fb270053ddc5e9780629d1c4bfce99f3da52ef973fcb17d31d0",
    "e68bd3d432c4b5575ca2fcccc740e822e4f223cccf7a487ee3da17306fd1dc8b",
    "a2efb467ed066266c0a28258a925392a3bcb537734b22ec851c9e9465b5147a6",
    "205a7363b11358801d41f7befac099238a3c8630d399365165ef6650bcdae693",
    "bd8fdf129b8470399e4b9124c15e2271cb0c6e139ba2032df96b4415e06bdf46",
    "59b60a9c27b07f0b5b794dbe727d6d02f6df4e97d5cd8aabbeb7c2b7f62aa070",
    "1eaf8e74140f4a6c9930f7eb5fe42d8bbc45cc062bffd64c526c48a16daa94ae",
    "2075095a9ad28e58ff9c3b43a2956bbcf5562bb6baba1303cb73b055831d3099",
    "2e3cf2e9515b64e0503cc17a3450dfe0d853d36241361a24a93d06a00da068f0",
    "b7b39ec1521622663bc0d026033c2c29bef4427d936a29af8f2b43d9e5e6b530",
    "bf395f834894f87da6df4fe70101d43319902340bfa1863822dc484868338b01",
    "8142459684402b404abe94353d4b4466d34b3e905dccb2747bae1f3ab3d21bde",
    "9f19a88929558633a799647753f7338b2dceb94a798a0b14b07d6d3bbeed2e7d",
    "67709acc1ebdfbbb9a5a1c28a12f629afa25168dd482ecb029d61887d2c93f79",
    "61fd0992d4fdaef7c393a005e9152d007b16aff1c6e58e00e906f212f4f0fcfb",
    "4342b9413e1b9f60225a1c65192a3e70228d6d40a1df6a4da19f0cfbe14a2270",
    "525c5746a7840d512f9593a2acf1a382ea310e7fdac40993228b45d70231fb4d",
]

mismatches = []
for part, expected in zip(parts, expected_part_hashes):
    raw = part.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        mismatches.append(
            f"{part.name}: length={len(raw)} expected={expected} actual={actual}"
        )
if mismatches:
    raise SystemExit("GitOps block 3 fragment integrity failure:\n" + "\n".join(mismatches))

payload = "".join(p.read_text(encoding="ascii") for p in parts)
expected_length = 60540
expected_sha256 = "9b90316b6c21fd36f1508bd61fc429f70fdd39a2712937a5a0750152688ff400"
actual_sha256 = hashlib.sha256(payload.encode("ascii")).hexdigest()
if len(payload) != expected_length or actual_sha256 != expected_sha256:
    raise SystemExit(
        "GitOps block 3 payload integrity failure after verified fragments: "
        f"length={len(payload)} sha256={actual_sha256}"
    )

for old in SCRIPTS.glob(".gitops_block3_payload_*.txt"):
    old.unlink()
(SCRIPTS / ".gitops_block3_payload_00.txt").write_text(
    payload, encoding="ascii", newline="\n"
)
print(f"Assembled verified GitOps block 3 payload: {len(payload)} bytes {actual_sha256}")
