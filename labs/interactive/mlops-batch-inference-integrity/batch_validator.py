#!/usr/bin/env python3
import hashlib
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path.cwd()
PROTECTED = ["batch-contract.json", "input-manifest.json", "runtime-trace.json", "model.json", "policy.json"]
GENERATED = ["output-manifest.json", "action-ledger.json", "batch-ledger.json", "batch-report.json"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def digest(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def clean(root):
    for name in GENERATED:
        (root / name).unlink(missing_ok=True)
    shutil.rmtree(root / "output", ignore_errors=True)


def execute(root):
    return subprocess.run(
        ["python3", "batch_gate.py"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=20,
    )


def assert_no_authority_files(root):
    assert not (root / "promotion-request.json").exists(), "batch gate must not create promotion authority"
    assert not (root / "retraining-request.json").exists(), "batch gate must not create retraining authority"


def assert_blocked(root, expected_reason):
    report = read_json(root / "batch-report.json")
    assert report["decision"] == "blocked"
    assert report["batch_verified"] is False
    assert report["promotion_authorized"] is False
    assert report["retraining_authorized"] is False
    assert expected_reason in report["reasons"], (expected_reason, report["reasons"])
    assert not (root / "output-manifest.json").exists(), "blocked evidence published canonical output manifest"
    assert not (root / "action-ledger.json").exists(), "blocked evidence mutated business actions"
    assert not (root / "batch-ledger.json").exists(), "blocked evidence committed batch ledger"
    assert not (root / "output").exists(), "blocked evidence published output parts"
    assert_no_authority_files(root)


def current_fixtures_to(dst):
    for name in PROTECTED:
        shutil.copy2(ROOT / name, dst / name)
    shutil.copy2(ROOT / "batch_gate.py", dst / "batch_gate.py")


def refresh_manifest_digest(root):
    contract = read_json(root / "batch-contract.json")
    contract["expected_input_manifest_digest"] = digest(root / "input-manifest.json")
    write_json(root / "batch-contract.json", contract)


def make_valid(root):
    manifest = read_json(root / "input-manifest.json")
    manifest["selection_basis"] = "event_time"
    manifest["rows"] = [r for r in manifest["rows"] if r["observation_id"] != "payment-8204"]
    manifest["row_count"] = len(manifest["rows"])
    write_json(root / "input-manifest.json", manifest)

    trace = read_json(root / "runtime-trace.json")
    trace["selection_basis"] = "event_time"
    trace["query_cutoff"] = "2026-08-22T00:00:00Z"
    for shard in trace["shards"]:
        shard["row_ids"] = [x for x in shard["row_ids"] if x != "payment-8204"]
    write_json(root / "runtime-trace.json", trace)
    refresh_manifest_digest(root)


def collect_generated(root):
    values = {}
    for name in GENERATED:
        if (root / name).exists():
            values[name] = (root / name).read_bytes()
    if (root / "output").exists():
        for path in sorted((root / "output").glob("*")):
            values[str(path.relative_to(root))] = path.read_bytes()
    return values


def recompute(model, policy, features):
    logit = model["intercept"] + sum(model["weights"][k] * features[k] for k in model["weights"])
    value = 1.0 / (1.0 + math.exp(-logit))
    if value < policy["thresholds"]["approve_below"]:
        action = "approve"
    elif value < policy["thresholds"]["manual_review_below"]:
        action = "manual_review"
    else:
        action = "decline"
    return round(value, 6), action


def assert_accepted(root):
    contract = read_json(root / "batch-contract.json")
    manifest = read_json(root / "input-manifest.json")
    model = read_json(root / "model.json")
    policy = read_json(root / "policy.json")
    report = read_json(root / "batch-report.json")
    out = read_json(root / "output-manifest.json")
    actions = read_json(root / "action-ledger.json")
    ledger = read_json(root / "batch-ledger.json")

    assert report["decision"] == "accepted"
    assert report["batch_verified"] is True
    assert report["promotion_authorized"] is False
    assert report["retraining_authorized"] is False
    assert out["complete"] is True
    assert out["row_count"] == 3
    assert out["unique_observations"] == 3
    assert len(out["parts"]) == 2
    assert len(actions) == 3
    assert len({a["business_operation_id"] for a in actions}) == 3
    assert ledger["status"] == "durable"
    assert ledger["row_count"] == 3 and ledger["action_count"] == 3
    assert ledger["output_manifest_digest"] == "sha256:" + hashlib.sha256((root / "output-manifest.json").read_bytes()).hexdigest()
    assert report["output_manifest_digest"] == ledger["output_manifest_digest"]

    rows = {r["observation_id"]: r for r in manifest["rows"]}
    predictions = []
    for part in out["parts"]:
        path = root / part["path"]
        data = path.read_bytes()
        assert part["sha256"] == "sha256:" + hashlib.sha256(data).hexdigest()
        parsed = [json.loads(line) for line in data.decode().splitlines() if line]
        assert part["rows"] == len(parsed)
        predictions.extend(parsed)
    assert len(predictions) == 3
    assert {p["observation_id"] for p in predictions} == set(rows)
    assert len({p["prediction_id"] for p in predictions}) == 3

    action_by_prediction = {a["prediction_id"]: a for a in actions}
    for p in predictions:
        row = rows[p["observation_id"]]
        value, expected_action = recompute(model, policy, row["features"])
        raw = "|".join([contract["release_subject"], contract["batch_operation_id"], row["observation_id"]]).encode()
        expected_prediction_id = "sha256:" + hashlib.sha256(raw).hexdigest()
        assert p["prediction_id"] == expected_prediction_id
        assert p["score"] == value
        assert p["action"] == expected_action
        assert p["model_digest"] == contract["model_digest"]
        assert p["feature_contract_id"] == contract["feature_contract_id"]
        assert p["policy_digest"] == contract["policy_digest"]
        assert action_by_prediction[p["prediction_id"]]["business_operation_id"] == row["business_operation_id"]
        assert action_by_prediction[p["prediction_id"]]["action"] == expected_action
    assert_no_authority_files(root)


def case(name, mutate, expected_reason):
    with tempfile.TemporaryDirectory(prefix="kh-batch-") as tmp:
        root = Path(tmp)
        current_fixtures_to(root)
        make_valid(root)
        mutate(root)
        clean(root)
        result = execute(root)
        assert result.returncode == 0, f"{name}: gate exit {result.returncode}: {result.stdout}"
        assert_blocked(root, expected_reason)


def _mutate_json(path, callback):
    value = read_json(path)
    callback(value)
    write_json(path, value)


def main():
    protected_before = {name: sha(ROOT / name) for name in PROTECTED}
    clean(ROOT)

    result = execute(ROOT)
    assert result.returncode == 0, result.stdout
    report = read_json(ROOT / "batch-report.json")
    expected = {
        "selection_basis_mismatch",
        "manifest_selection_basis_mismatch",
        "input_row_count_mismatch",
        "unique_observation_count_mismatch",
        "observation_outside_logical_interval:payment-8204",
    }
    assert expected.issubset(set(report["reasons"])), report["reasons"]
    assert_blocked(ROOT, "selection_basis_mismatch")
    assert {name: sha(ROOT / name) for name in PROTECTED} == protected_before, "gate mutated protected canonical evidence"
    print("PASS canonical processing-time leakage is blocked before publication")

    with tempfile.TemporaryDirectory(prefix="kh-batch-valid-") as tmp:
        root = Path(tmp)
        current_fixtures_to(root)
        make_valid(root)
        result = execute(root)
        assert result.returncode == 0, result.stdout
        assert_accepted(root)
        first = collect_generated(root)
        result2 = execute(root)
        assert result2.returncode == 0, result2.stdout
        assert_accepted(root)
        assert collect_generated(root) == first, "second execution changed durable output bytes"
        print("PASS complete 3-row / 2-shard subject publishes once and replays byte-idempotently")

    case("loaded model", lambda r: _mutate_json(r / "runtime-trace.json", lambda x: x.__setitem__("loaded_model_digest", "sha256:" + "0" * 64)), "loaded_model_digest_mismatch")
    case("runtime image", lambda r: _mutate_json(r / "runtime-trace.json", lambda x: x.__setitem__("loaded_runtime_image_digest", "sha256:" + "1" * 64)), "loaded_runtime_image_digest_mismatch")
    case("feature contract", lambda r: _mutate_json(r / "runtime-trace.json", lambda x: x.__setitem__("loaded_feature_contract_id", "payment-risk-features-v5")), "loaded_feature_contract_id_mismatch")
    case("input schema", lambda r: _mutate_json(r / "runtime-trace.json", lambda x: x.__setitem__("loaded_input_schema_id", "risk-batch-row-v5")), "loaded_input_schema_id_mismatch")
    case("job failed", lambda r: _mutate_json(r / "runtime-trace.json", lambda x: x.__setitem__("job_status", "failed")), "job_not_succeeded")

    def model_tamper(root):
        model = read_json(root / "model.json")
        model["weights"]["amount_norm"] = 9.9
        write_json(root / "model.json", model)
    case("model bytes", model_tamper, "model_digest_mismatch")

    def policy_tamper(root):
        policy = read_json(root / "policy.json")
        policy["thresholds"]["approve_below"] = 0.9
        write_json(root / "policy.json", policy)
    case("policy bytes", policy_tamper, "policy_digest_mismatch")

    def feature_future(root):
        manifest = read_json(root / "input-manifest.json")
        manifest["rows"][1]["feature_available_at"] = "2026-08-21T14:30:01Z"
        write_json(root / "input-manifest.json", manifest)
        refresh_manifest_digest(root)
    case("feature time travel", feature_future, "feature_time_travel:payment-8202")

    def interval_tamper(root):
        manifest = read_json(root / "input-manifest.json")
        manifest["logical_interval"]["start"] = "2026-08-20T00:00:00Z"
        write_json(root / "input-manifest.json", manifest)
        refresh_manifest_digest(root)
    case("logical interval", interval_tamper, "logical_interval_mismatch")

    def missing_shard(root):
        trace = read_json(root / "runtime-trace.json")
        trace["shards"] = [x for x in trace["shards"] if x["shard_id"] == 0]
        write_json(root / "runtime-trace.json", trace)
    case("missing shard", missing_shard, "incomplete_successful_shards")

    def duplicate_cross_shard(root):
        trace = read_json(root / "runtime-trace.json")
        trace["shards"][1]["row_ids"].append("payment-8202")
        write_json(root / "runtime-trace.json", trace)
    case("duplicate shard row", duplicate_cross_shard, "duplicate_row_across_shards")

    def duplicate_observation(root):
        manifest = read_json(root / "input-manifest.json")
        manifest["rows"][2]["observation_id"] = "payment-8202"
        write_json(root / "input-manifest.json", manifest)
        trace = read_json(root / "runtime-trace.json")
        trace["shards"][1]["row_ids"] = ["payment-8202"]
        write_json(root / "runtime-trace.json", trace)
        refresh_manifest_digest(root)
    case("duplicate observation", duplicate_observation, "duplicate_observation_id:payment-8202")

    def wrong_publication(root):
        contract = read_json(root / "batch-contract.json")
        contract["publication_mode"] = "publish_prefix_on_first_shard"
        write_json(root / "batch-contract.json", contract)
    case("publication mode", wrong_publication, "unsupported_publication_mode")

    with tempfile.TemporaryDirectory(prefix="kh-batch-retry-") as tmp:
        root = Path(tmp)
        current_fixtures_to(root)
        make_valid(root)
        trace = read_json(root / "runtime-trace.json")
        original = next(x for x in trace["shards"] if x["shard_id"] == 1)
        original["attempt"] = 2
        trace["shards"].insert(1, {"shard_id": 1, "attempt": 1, "status": "failed", "row_ids": []})
        write_json(root / "runtime-trace.json", trace)
        result = execute(root)
        assert result.returncode == 0, result.stdout
        assert_accepted(root)
        print("PASS failed shard attempt followed by one successful attempt is reconciled")

    with tempfile.TemporaryDirectory(prefix="kh-batch-conflict-") as tmp:
        root = Path(tmp)
        current_fixtures_to(root)
        make_valid(root)
        (root / "action-ledger.json").write_text('[{"foreign":"state"}]\n')
        before = (root / "action-ledger.json").read_bytes()
        result = execute(root)
        assert result.returncode != 0
        assert "conflicting_existing_state:action-ledger.json" in result.stdout
        assert (root / "action-ledger.json").read_bytes() == before
        assert not (root / "output-manifest.json").exists()
        assert not (root / "batch-ledger.json").exists()
        assert not (root / "output").exists()
        print("PASS conflicting durable action state is preserved and blocks publication")

    assert {name: sha(ROOT / name) for name in PROTECTED} == protected_before, "validator or gate mutated canonical protected evidence"
    clean(ROOT)
    print("VALIDATION PASSED")


if __name__ == "__main__":
    main()
