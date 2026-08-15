#!/usr/bin/env python3
import copy
import hashlib
import json
import random
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent
WORKSPACE = Path("/workspace")
PROTECTED = {
    "drift_contract.json": LAB_ROOT / "drift_contract.json.template",
    "reference-window.json": LAB_ROOT / "reference-window.json.template",
    "current-window.json": LAB_ROOT / "current-window.json.template",
}


def fail(message):
    raise AssertionError(message)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def parse_ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def mean(values):
    if not values:
        fail("validator metric population unexpectedly empty")
    return sum(values) / len(values)


def expected(contract_path, reference_path, current_path):
    contract = load(contract_path)
    reference = load(reference_path)
    current = load(current_path)
    start = parse_ts(contract["current_window"]["start"])
    end = parse_ts(contract["current_window"]["end"])

    ref_eligible = [r for r in reference["records"] if r.get("eligible") is True]
    cur_eligible = [
        r for r in current["records"]
        if r.get("eligible") is True and start <= parse_ts(r["event_time"]) < end
    ]
    ref_scored = [r for r in ref_eligible if r.get("serving_status") == "scored" and r.get("score") is not None]
    cur_scored = [r for r in cur_eligible if r.get("serving_status") == "scored" and r.get("score") is not None]
    cur_fallback = [r for r in cur_eligible if r.get("serving_status") == "fallback"]

    feature = contract["metrics"]["data_feature"]
    ref_mean = mean([float(r[feature]) for r in ref_eligible])
    cur_mean = mean([float(r[feature]) for r in cur_eligible])
    data_shift = abs(cur_mean - ref_mean) / abs(ref_mean)
    pred_shift = abs(mean([float(r["score"]) for r in cur_scored]) - mean([float(r["score"]) for r in ref_scored]))
    fallback_rate = len(cur_fallback) / len(cur_eligible)
    data_alert = data_shift >= contract["metrics"]["data_alert_threshold"]
    pred_alert = pred_shift >= contract["metrics"]["prediction_alert_threshold"]
    fallback_alert = fallback_rate >= contract["metrics"]["fallback_rate_alert_threshold"]
    if fallback_alert:
        action = "investigate_serving_fallback"
    elif data_alert:
        action = "investigate_data_drift"
    elif pred_alert:
        action = "investigate_prediction_drift"
    else:
        action = "stable"

    return {
        "contract_id": contract["contract_id"],
        "contract_sha256": sha256(contract_path),
        "reference": {
            "dataset_id": reference["dataset_id"],
            "sha256": contract["reference_sha256"],
            "release_id": reference["release_id"],
            "eligible_count": len(ref_eligible),
            "scored_count": len(ref_scored),
        },
        "current": {
            "window_id": current["window_id"],
            "release_id": current["release_id"],
            "eligible_count": len(cur_eligible),
            "scored_count": len(cur_scored),
            "fallback_count": len(cur_fallback),
            "fallback_rate": round(fallback_rate, 6),
        },
        "population_basis": "eligible_event_time",
        "window_basis": "event_time",
        "window_complete": True,
        "feature_generation": contract["feature_generation"],
        "threshold_policy": contract["threshold_policy"],
        "data_drift": {
            "metric": contract["metrics"]["data_metric"],
            "value": round(data_shift, 6),
            "alert": data_alert,
        },
        "prediction_drift": {
            "metric": contract["metrics"]["prediction_metric"],
            "value": round(pred_shift, 6),
            "alert": pred_alert,
        },
        "concept_drift": {"status": "not_evaluable", "reason": "mature_labels_unavailable"},
        "recommended_action": action,
        "retraining_triggered": False,
    }


def run_monitor(reference_path, current_path, expect_success=True):
    marker = WORKSPACE / "retrain-request.json"
    marker.unlink(missing_ok=True)
    proc = subprocess.run(
        [
            "python3", str(WORKSPACE / "drift_monitor.py"),
            "--contract", str(WORKSPACE / "drift_contract.json"),
            "--reference", str(reference_path),
            "--current", str(current_path),
        ],
        text=True,
        capture_output=True,
    )
    if marker.exists():
        fail("monitor created forbidden retraining side effect")
    if expect_success:
        if proc.returncode != 0:
            fail(f"monitor failed unexpectedly: {proc.stderr.strip()}")
        try:
            value = json.loads(proc.stdout)
        except Exception as exc:
            fail(f"monitor did not emit one JSON result: {exc}: {proc.stdout!r}")
        return value
    if proc.returncode == 0:
        fail(f"monitor accepted invalid evidence: {proc.stdout.strip()}")
    return None


def write_variant(tmp, name, obj):
    path = tmp / name
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    return path


def assert_case(reference_path, current_path):
    actual = run_monitor(reference_path, current_path)
    wanted = expected(WORKSPACE / "drift_contract.json", reference_path, current_path)
    if actual != wanted:
        fail("behavior mismatch\nEXPECTED: " + json.dumps(wanted, sort_keys=True) + "\nACTUAL:   " + json.dumps(actual, sort_keys=True))
    return actual


def main():
    for workspace_name, template_path in PROTECTED.items():
        workspace_path = WORKSPACE / workspace_name
        if not workspace_path.exists():
            fail(f"missing protected evidence: {workspace_name}")
        if workspace_path.read_bytes() != template_path.read_bytes():
            fail(f"protected evidence was modified: {workspace_name}")

    contract = load(WORKSPACE / "drift_contract.json")
    if sha256(WORKSPACE / "reference-window.json") != contract["reference_sha256"]:
        fail("canonical reference bytes no longer match the pinned digest")
    if not (WORKSPACE / "drift_monitor.py").exists():
        fail("missing learner monitor: /workspace/drift_monitor.py")

    reference_path = WORKSPACE / "reference-window.json"
    current_path = WORKSPACE / "current-window.json"
    canonical = assert_case(reference_path, current_path)
    if run_monitor(reference_path, current_path) != canonical:
        fail("same drift subject was not deterministic on repeated evaluation")

    reference = load(reference_path)
    base = load(current_path)
    rng = random.Random(240815)

    with tempfile.TemporaryDirectory(prefix="kh-drift-") as tmpdir:
        tmp = Path(tmpdir)

        # Targeted: healthy serving, true input drift, and isolated prediction drift.
        healthy = copy.deepcopy(base)
        for i, row in enumerate(healthy["records"]):
            row["serving_status"] = "scored"
            row["score"] = reference["records"][i]["score"]
        assert_case(reference_path, write_variant(tmp, "healthy.json", healthy))

        data_only = copy.deepcopy(healthy)
        for row in data_only["records"]:
            row["amount_eur"] = round(float(row["amount_eur"]) * 1.30, 3)
        assert_case(reference_path, write_variant(tmp, "data-only.json", data_only))

        prediction_only = copy.deepcopy(healthy)
        for row in prediction_only["records"]:
            row["score"] = round(float(row["score"]) + 0.05, 6)
        assert_case(reference_path, write_variant(tmp, "prediction-only.json", prediction_only))

        # Deterministic generated cases exercise record ordering, processing-time delay,
        # ineligible noise, amount drift and fallback mixtures. Event-time population is authority.
        for case_idx in range(12):
            variant = copy.deepcopy(base)
            rng.shuffle(variant["records"])
            for row in variant["records"]:
                if rng.random() < 0.35:
                    row["ingest_time"] = "2026-08-15T12:30:00Z"
                if rng.random() < 0.25:
                    row["amount_eur"] = round(float(row["amount_eur"]) * rng.choice([0.90, 1.00, 1.10, 1.35]), 3)
                if rng.random() < 0.20:
                    if row["serving_status"] == "fallback":
                        row["serving_status"] = "scored"
                        row["score"] = round(float(row["amount_eur"]) / 1000, 6)
                    else:
                        row["serving_status"] = "fallback"
                        row["score"] = None
            variant["records"].append({
                "request_id": f"noise-{case_idx}",
                "event_time": "2026-08-15T10:30:00Z",
                "ingest_time": "2026-08-15T10:31:00Z",
                "eligible": False,
                "amount_eur": 999999,
                "serving_status": "fallback",
                "score": None,
            })
            # Keep at least one scored row for the prediction metric.
            if not any(r.get("eligible") is True and r.get("serving_status") == "scored" for r in variant["records"]):
                row = next(r for r in variant["records"] if r.get("eligible") is True)
                row["serving_status"] = "scored"
                row["score"] = round(float(row["amount_eur"]) / 1000, 6)
            assert_case(reference_path, write_variant(tmp, f"generated-{case_idx:02d}.json", variant))

        # Out-of-window eligible noise must not change the event-time subject.
        outside = copy.deepcopy(base)
        outside["records"].append({
            "request_id":"outside-window", "event_time":"2026-08-15T11:30:00Z",
            "ingest_time":"2026-08-15T11:31:00Z", "eligible":True,
            "amount_eur":999999, "serving_status":"scored", "score":0.999,
        })
        assert_case(reference_path, write_variant(tmp, "outside.json", outside))

        # Invalid evidence must stop before a drift verdict.
        incomplete = copy.deepcopy(base)
        incomplete["completeness_watermark"] = "2026-08-15T10:59:59Z"
        run_monitor(reference_path, write_variant(tmp, "incomplete.json", incomplete), expect_success=False)

        wrong_release = copy.deepcopy(base)
        wrong_release["release_id"] = "risk-serving-UNKNOWN"
        run_monitor(reference_path, write_variant(tmp, "wrong-release.json", wrong_release), expect_success=False)

        wrong_feature = copy.deepcopy(base)
        wrong_feature["feature_generation"] = "payment-risk-features-v5"
        run_monitor(reference_path, write_variant(tmp, "wrong-feature.json", wrong_feature), expect_success=False)

        wrong_policy = copy.deepcopy(base)
        wrong_policy["threshold_policy"] = "review-capacity-legacy"
        run_monitor(reference_path, write_variant(tmp, "wrong-policy.json", wrong_policy), expect_success=False)

    print("PASS: drift monitor binds exact evidence, uses complete event-time populations, separates fallback/prediction/data signals, and refuses unsupported concept-drift or retraining claims")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
