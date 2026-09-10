#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

FILES = [
    "supply-chain-contract.json",
    "release-manifest.json",
    "source.json",
    "dataset.json",
    "dependency-lock.json",
    "build-provenance.json",
    "artifacts.json",
    "runtime-evidence.json",
    "second-operation.json",
]
OUTPUTS = ["supply-chain-report.json", "supply-chain-evidence-ledger.json"]
BASELINE = {name: Path(name).read_text() for name in FILES}

def load(path):
    return json.loads(Path(path).read_text())

def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2) + "\n")

def restore():
    for name, text in BASELINE.items():
        Path(name).write_text(text)
    for name in OUTPUTS:
        Path(name).unlink(missing_ok=True)

def run_gate():
    return subprocess.run([sys.executable, "./supply_chain_gate.py"], text=True, capture_output=True)

def expect_rejected(label):
    result = run_gate()
    assert result.returncode != 0, f"{label}: gate unexpectedly accepted"
    assert not Path("supply-chain-evidence-ledger.json").exists(), f"{label}: durable ledger must not be created"
    if Path("supply-chain-report.json").exists():
        assert load("supply-chain-report.json").get("supply_chain_verified") is False, f"{label}: rejection report verified chain"

def make_healthy():
    lock = load("dependency-lock.json")
    lock["transitive_dependencies_pinned"] = True
    lock["hash_checking_mode"] = True
    lock["only_binary"] = True
    write_json("dependency-lock.json", lock)

    import hashlib
    dep_digest = "sha256:" + hashlib.sha256(Path("dependency-lock.json").read_bytes()).hexdigest()

    build = load("build-provenance.json")
    build["builder_isolated"] = True
    build["ephemeral_runner"] = True
    build["dependency_lock_digest"] = dep_digest
    build["base_image_reference"] = "python:3.12-slim@sha256:de17f0e5a1c0aa5f711571eb2ae3c0970045c89aba6a10a1983207809c538760"
    build["base_image_digest"] = "sha256:de17f0e5a1c0aa5f711571eb2ae3c0970045c89aba6a10a1983207809c538760"
    build["network_policy"] = "audited_proxy_only"
    build["provenance_generated_by_platform"] = True
    write_json("build-provenance.json", build)

    artifacts = load("artifacts.json")
    artifacts["model"]["storage_uri"] = "s3://ml-models/fraud/releases/r45/model@sha256:8f337b6096eca4d33c905e54336e102893ed911b3447cf1c93becc38dd7a7ba6"
    artifacts["model"]["immutable_uri"] = True
    artifacts["image"]["certificate_identity"] = "https://github.com/example/fraud/.github/workflows/model-build.yml@refs/heads/main"
    write_json("artifacts.json", artifacts)

    release = load("release-manifest.json")
    runtime = load("runtime-evidence.json")
    for field in (
        "provenance_verified",
        "builder_identity_verified",
        "release_manifest_verified",
        "remote_model_digest_verified",
    ):
        runtime["admission"][field] = True
    runtime["loaded"]["model_digest"] = release["model_digest"]
    runtime["synthetic_inference"]["release_matches_manifest"] = True
    write_json("runtime-evidence.json", runtime)

    second = load("second-operation.json")
    second["same_dependency_lock_digest"] = True
    second["same_base_image_digest"] = True
    second["trusted_builder_used"] = True
    second["platform_provenance_verified"] = True
    second["model_subject_bound"] = True
    second["admission_verified_composite"] = True
    second["loaded_model_matches_release"] = True
    second["mutable_package_index_dependency"] = False
    second["long_lived_secret_required"] = False
    second["manual_digest_edit_required"] = False
    second["old_subjects_quarantined"] = True
    write_json("second-operation.json", second)

restore()
expect_rejected("canonical signed-image-only incident")
print("PASS signed image + HTTP success without composite chain of custody is blocked")

restore()
contract = load("supply-chain-contract.json")
contract["authority"]["promotion_authorized"] = True
write_json("supply-chain-contract.json", contract)
expect_rejected("tampered supply-chain authority")
print("PASS tampered supply-chain authority contract is blocked")

restore()
make_healthy()
build = load("build-provenance.json")
build["provenance_subjects"]["model_digest"] = "sha256:bad0000000000000000000000000000000000000000000000000000000000000"
write_json("build-provenance.json", build)
expect_rejected("provenance subject substitution")
print("PASS provenance bound to different model bytes is blocked")

restore()
make_healthy()
result = run_gate()
assert result.returncode == 0, result.stdout + result.stderr
report = load("supply-chain-report.json")
for field in (
    "supply_chain_verified",
    "source_data_dependency_verified",
    "builder_provenance_verified",
    "artifact_binding_verified",
    "admission_runtime_verified",
    "second_operation_verified",
):
    assert report[field] is True, field
assert report["rollout_authorized"] is False
assert report["promotion_authorized"] is False
assert report["retraining_authorized"] is False
report_bytes = Path("supply-chain-report.json").read_bytes()
ledger_bytes = Path("supply-chain-evidence-ledger.json").read_bytes()

replay = run_gate()
assert replay.returncode == 0, replay.stdout + replay.stderr
assert Path("supply-chain-report.json").read_bytes() == report_bytes
assert Path("supply-chain-evidence-ledger.json").read_bytes() == ledger_bytes
print("PASS pinned inputs + trusted provenance + composite admission are byte-idempotent")

Path("supply-chain-evidence-ledger.json").write_text('{"conflict":true}\n')
before = Path("supply-chain-evidence-ledger.json").read_bytes()
conflict = run_gate()
assert conflict.returncode != 0, "conflicting durable supply-chain state unexpectedly overwritten"
assert Path("supply-chain-evidence-ledger.json").read_bytes() == before
print("PASS conflicting durable supply-chain evidence is preserved")

restore()
print("VALIDATION PASSED")
