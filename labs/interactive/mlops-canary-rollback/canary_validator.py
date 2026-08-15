#!/usr/bin/env python3
import copy
import hashlib
import json
import math
import random
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent
WORKSPACE = Path("/workspace")
PROTECTED = {
    "rollout-contract.json": LAB_ROOT / "rollout-contract.json.template",
    "known-good-release.json": LAB_ROOT / "known-good-release.json.template",
    "exposure-window.json": LAB_ROOT / "exposure-window.json.template",
}
INITIAL_STATE = LAB_ROOT / "routing-state.json.template"

def fail(message):
    raise AssertionError(message)

def load(path):
    return json.loads(Path(path).read_text())

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def parse_ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def p95(values):
    ordered = sorted(float(v) for v in values)
    if not ordered:
        fail("validator candidate latency population unexpectedly empty")
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]

def rounded(value):
    return round(float(value), 6)

def expected(contract_path, known_good_path, exposure_path, state_before):
    contract = load(contract_path)
    known_good = load(known_good_path)
    exposure = load(exposure_path)
    start = parse_ts(contract["window"]["start"])
    end = parse_ts(contract["window"]["end"])
    eligible = [
        r for r in exposure["records"]
        if r.get("eligible") is True and start <= parse_ts(r["event_time"]) < end
    ]
    assignments = {}
    for row in eligible:
        assignments.setdefault(row[contract["assignment_unit"]], row["assigned_release"])
    candidate = [r for r in eligible if r["actual_release"] == contract["candidate_release"]]
    control = [r for r in eligible if r["actual_release"] == contract["control_release"]]
    candidate_units = {r[contract["assignment_unit"]] for r in candidate}
    eligible_units = set(assignments)
    actual_unit_exposure = len(candidate_units) / len(eligible_units)
    candidate_error_rate = sum(bool(r["error"]) for r in candidate) / len(candidate) if candidate else 0.0
    candidate_fallback_rate = sum(bool(r["feature_fallback"]) for r in candidate) / len(candidate) if candidate else 0.0
    candidate_p95_latency = p95([r["latency_ms"] for r in candidate]) if candidate else 0.0
    candidate_review_rate = sum(r["action"] == "manual_review" for r in candidate) / len(candidate) if candidate else 0.0
    control_review_rate = sum(r["action"] == "manual_review" for r in control) / len(control)
    review_rate_delta = abs(candidate_review_rate - control_review_rate)

    breached = []
    g = contract["guardrails"]
    if candidate_error_rate > g["candidate_error_rate_max"]:
        breached.append("candidate_error_rate")
    if candidate_fallback_rate > g["candidate_fallback_rate_max"]:
        breached.append("candidate_fallback_rate")
    if candidate_p95_latency > g["candidate_p95_latency_ms_max"]:
        breached.append("candidate_p95_latency_ms")
    if review_rate_delta > g["review_rate_delta_max"]:
        breached.append("review_rate_delta")

    enough_evidence = (
        len(candidate) >= contract["current_step"]["minimum_candidate_requests"]
        and len(candidate_units) >= contract["current_step"]["minimum_candidate_units"]
    )
    if actual_unit_exposure > contract["current_step"]["maximum_actual_unit_exposure"]:
        decision, reason = "rollback", "actual_exposure_exceeded"
        target_exposure = 0.0
        generation = contract["rollback"]["state_generation"]
    elif breached:
        decision, reason = "rollback", "guardrail_breach"
        target_exposure = 0.0
        generation = contract["rollback"]["state_generation"]
    elif not enough_evidence:
        decision, reason = "hold", "minimum_evidence_not_met"
        target_exposure = state_before.get("candidate_exposure", contract["current_step"]["configured_candidate_exposure"])
        generation = state_before.get("routing_generation", contract["routing_generation"])
    else:
        decision, reason = "ramp", "step_accepted"
        target_exposure = contract["next_step"]["candidate_exposure"]
        generation = contract["next_step"]["state_generation"]

    result = {
        "contract_id": contract["contract_id"],
        "contract_sha256": sha256(contract_path),
        "rollout_subject_id": contract["rollout_subject_id"],
        "known_good_release": {
            "release_id": known_good["release_id"],
            "sha256": contract["known_good_release_sha256"],
        },
        "exposure": {
            "window_id": exposure["window_id"],
            "window_complete": True,
            "eligible_requests": len(eligible),
            "eligible_units": len(eligible_units),
            "candidate_requests": len(candidate),
            "candidate_units": len(candidate_units),
            "actual_candidate_unit_exposure": rounded(actual_unit_exposure),
            "assignment_unit": contract["assignment_unit"],
        },
        "guardrails": {
            "candidate_error_rate": rounded(candidate_error_rate),
            "candidate_fallback_rate": rounded(candidate_fallback_rate),
            "candidate_p95_latency_ms": rounded(candidate_p95_latency),
            "candidate_review_rate": rounded(candidate_review_rate),
            "control_review_rate": rounded(control_review_rate),
            "review_rate_delta": rounded(review_rate_delta),
            "breached": breached,
        },
        "decision": decision,
        "reason": reason,
        "target_release": contract["control_release"],
        "target_candidate_exposure": rounded(target_exposure),
        "state_generation": generation,
    }
    state = {
        "active_release": contract["control_release"],
        "candidate_exposure": rounded(target_exposure),
        "candidate_release": contract["candidate_release"],
        "last_decision": result,
        "rollout_subject_id": contract["rollout_subject_id"],
        "routing_generation": generation,
        "status": {"rollback":"rolled_back", "hold":"canary_active", "ramp":"ramped"}[decision],
    }
    return result, state

def write_variant(tmp, name, value):
    path = tmp / name
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    return path

def fresh_state(tmp, name):
    path = tmp / name
    path.write_bytes(INITIAL_STATE.read_bytes())
    return path

def run_decider(exposure_path, state_path, expect_success=True):
    before = Path(state_path).read_bytes()
    proc = subprocess.run(
        [
            "python3", str(WORKSPACE / "canary_decider.py"),
            "--contract", str(WORKSPACE / "rollout-contract.json"),
            "--known-good", str(WORKSPACE / "known-good-release.json"),
            "--exposure", str(exposure_path),
            "--state", str(state_path),
        ],
        text=True, capture_output=True,
    )
    if expect_success:
        if proc.returncode != 0:
            fail(f"decider failed unexpectedly: {proc.stderr.strip()}")
        try:
            return json.loads(proc.stdout), before
        except Exception as exc:
            fail(f"decider did not emit one JSON object: {exc}: {proc.stdout!r}")
    if proc.returncode == 0:
        fail(f"decider accepted invalid rollout evidence: {proc.stdout.strip()}")
    if Path(state_path).read_bytes() != before:
        fail("invalid evidence mutated routing state")
    return None, before

def assert_case(exposure_path, state_path):
    state_before = load(state_path)
    wanted_result, wanted_state = expected(
        WORKSPACE / "rollout-contract.json",
        WORKSPACE / "known-good-release.json",
        exposure_path,
        state_before,
    )
    actual, _ = run_decider(exposure_path, state_path)
    if actual != wanted_result:
        fail("decision mismatch\nEXPECTED: " + json.dumps(wanted_result, sort_keys=True) + "\nACTUAL:   " + json.dumps(actual, sort_keys=True))
    if load(state_path) != wanted_state:
        fail("routing-state side effect does not match the exact canary decision")
    return actual

def main():
    for workspace_name, template_path in PROTECTED.items():
        workspace_path = WORKSPACE / workspace_name
        if not workspace_path.exists():
            fail(f"missing protected rollout evidence: {workspace_name}")
        if workspace_path.read_bytes() != template_path.read_bytes():
            fail(f"protected rollout evidence was modified: {workspace_name}")

    contract = load(WORKSPACE / "rollout-contract.json")
    if sha256(WORKSPACE / "known-good-release.json") != contract["known_good_release_sha256"]:
        fail("known-good release bytes no longer match the pinned digest")
    if not (WORKSPACE / "canary_decider.py").exists():
        fail("missing learner decider: /workspace/canary_decider.py")
    if not (WORKSPACE / "routing-state.json").exists():
        fail("missing routing state: /workspace/routing-state.json")

    canonical_exposure = WORKSPACE / "exposure-window.json"
    canonical = assert_case(canonical_exposure, WORKSPACE / "routing-state.json")
    state_after = (WORKSPACE / "routing-state.json").read_bytes()
    repeated, _ = run_decider(canonical_exposure, WORKSPACE / "routing-state.json")
    if repeated != canonical:
        fail("same exact rollout subject produced a different repeated decision")
    if (WORKSPACE / "routing-state.json").read_bytes() != state_after:
        fail("repeating the exact rollback subject changed routing state bytes")

    base = load(canonical_exposure)
    rng = random.Random(250815)
    with tempfile.TemporaryDirectory(prefix="kh-canary-") as tmpdir:
        tmp = Path(tmpdir)

        # Healthy candidate: enough evidence, candidate-only guardrails accepted -> ramp.
        healthy = copy.deepcopy(base)
        candidate_rows = [r for r in healthy["records"] if r["assigned_release"] == contract["candidate_release"]]
        for row in candidate_rows:
            row["error"] = False
            row["feature_fallback"] = False
            row["latency_ms"] = 140
            row["action"] = "allow"
        candidate_rows[0]["action"] = "manual_review"
        assert_case(write_variant(tmp, "healthy.json", healthy), fresh_state(tmp, "healthy-state.json"))

        # Underpowered candidate: stable and healthy, but not enough candidate units/requests -> hold.
        underpowered = copy.deepcopy(healthy)
        for row in underpowered["records"]:
            if row["merchant_id"] == "merchant-03":
                row["eligible"] = False
        assert_case(write_variant(tmp, "underpowered.json", underpowered), fresh_state(tmp, "underpowered-state.json"))

        # Actual unique-unit exposure above the contract maximum -> rollback even if metrics are healthy.
        overexposed = copy.deepcopy(healthy)
        for row in overexposed["records"]:
            if row["merchant_id"] == "merchant-04":
                row["assigned_release"] = contract["candidate_release"]
                row["actual_release"] = contract["candidate_release"]
                row["latency_ms"] = 140
                row["action"] = "allow"
        assert_case(write_variant(tmp, "overexposed.json", overexposed), fresh_state(tmp, "overexposed-state.json"))

        # Out-of-window and ineligible records must not change the rollout subject.
        noise = copy.deepcopy(healthy)
        noise["records"].append({
            "request_id":"noise-outside", "event_time":"2026-08-15T11:59:00Z",
            "merchant_id":"merchant-noise", "eligible":True,
            "eligibility_policy":contract["eligibility_policy"],
            "assigned_release":contract["candidate_release"], "actual_release":contract["candidate_release"],
            "routing_generation":contract["routing_generation"], "error":True,
            "feature_fallback":True, "latency_ms":9999, "action":"manual_review",
        })
        noise["records"].append({
            "request_id":"noise-ineligible", "event_time":"2026-08-15T12:30:00Z",
            "merchant_id":"merchant-noise-2", "eligible":False,
            "eligibility_policy":contract["eligibility_policy"],
            "assigned_release":contract["candidate_release"], "actual_release":contract["candidate_release"],
            "routing_generation":contract["routing_generation"], "error":True,
            "feature_fallback":True, "latency_ms":9999, "action":"manual_review",
        })
        assert_case(write_variant(tmp, "noise.json", noise), fresh_state(tmp, "noise-state.json"))

        # Generated variants exercise ordering and candidate-only guardrail combinations.
        for case_idx in range(10):
            variant = copy.deepcopy(healthy)
            rng.shuffle(variant["records"])
            candidate = [r for r in variant["records"] if r["assigned_release"] == contract["candidate_release"]]
            if case_idx % 4 == 0:
                candidate[0]["error"] = True
            elif case_idx % 4 == 1:
                candidate[0]["feature_fallback"] = True
            elif case_idx % 4 == 2:
                candidate[-1]["latency_ms"] = 260
            else:
                for row in candidate:
                    row["action"] = "manual_review"
            assert_case(write_variant(tmp, f"generated-{case_idx:02d}.json", variant), fresh_state(tmp, f"generated-state-{case_idx:02d}.json"))

        # Invalid evidence must fail closed and preserve routing bytes.
        invalids = []

        incomplete = copy.deepcopy(base)
        incomplete["completeness_watermark"] = "2026-08-15T12:59:59Z"
        invalids.append(("incomplete.json", incomplete))

        wrong_subject = copy.deepcopy(base)
        wrong_subject["rollout_subject_id"] = "MLOPS-PAY-ROLLOUT-UNKNOWN"
        invalids.append(("wrong-subject.json", wrong_subject))

        wrong_router = copy.deepcopy(base)
        wrong_router["records"][0]["routing_generation"] = "risk-rollout-router-v7"
        invalids.append(("wrong-router.json", wrong_router))

        mixed_assignment = copy.deepcopy(base)
        mixed_assignment["records"][1]["assigned_release"] = contract["control_release"]
        mixed_assignment["records"][1]["actual_release"] = contract["control_release"]
        invalids.append(("mixed-assignment.json", mixed_assignment))

        mixed_revision = copy.deepcopy(base)
        mixed_revision["records"][0]["actual_release"] = contract["control_release"]
        invalids.append(("mixed-revision.json", mixed_revision))

        missing_field = copy.deepcopy(base)
        del missing_field["records"][0]["merchant_id"]
        invalids.append(("missing-field.json", missing_field))

        for name, value in invalids:
            exposure_path = write_variant(tmp, name, value)
            state_path = fresh_state(tmp, "state-" + name)
            run_decider(exposure_path, state_path, expect_success=False)

    for workspace_name, template_path in PROTECTED.items():
        if (WORKSPACE / workspace_name).read_bytes() != template_path.read_bytes():
            fail(f"protected rollout evidence changed during validation: {workspace_name}")

    print("PASS: canary decision binds exact rollout evidence, measures actual stable-unit exposure, evaluates candidate-only guardrails, and performs deterministic rollback/ramp/hold state transitions")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
