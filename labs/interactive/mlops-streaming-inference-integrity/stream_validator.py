#!/usr/bin/env python3
import hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUTS = ["stream-contract.json", "events.json", "runtime-trace.json", "model.json", "policy.json"]
OUTPUTS = ["prediction-ledger.json", "action-ledger.json", "stream-checkpoint.json", "stream-report.json"]
PASS = "PASS: streaming inference gate binds topic/partition/offset and event-time evidence to the exact loaded release, survives rebalance replay with idempotent prediction/action ledgers, and advances the checkpoint only after durable unique business effects without granting promotion or retraining authority"


def sha_bytes(data): return hashlib.sha256(data).hexdigest()
def load(path): return json.loads(Path(path).read_text())
def write(path, obj): Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")

def prepare():
    td = Path(tempfile.mkdtemp(prefix="kh-stream-validator-"))
    for name in INPUTS:
        src = ROOT / name
        if not src.exists():
            src = ROOT / (name + ".template")
        shutil.copy2(src, td / name)
    shutil.copy2(ROOT / "stream_gate.py", td / "stream_gate.py")
    return td

def run(td):
    return subprocess.run([sys.executable, "stream_gate.py"], cwd=td, text=True, capture_output=True)

def mutate_json(td, name, fn, repin_events=False):
    p = td / name
    data = load(p); fn(data); write(p, data)
    if repin_events:
        c = load(td / "stream-contract.json")
        c["events_sha256"] = "sha256:" + hashlib.sha256((td / "events.json").read_bytes()).hexdigest()
        write(td / "stream-contract.json", c)

def expect_reject(label, mutator, reason, repin_events=False):
    td = prepare()
    try:
        mutator(td, repin_events)
        before = {o: (td / o).read_bytes() if (td / o).exists() else None for o in OUTPUTS}
        r = run(td)
        if r.returncode == 0 or reason not in (r.stdout + r.stderr):
            raise AssertionError(f"{label}: expected rejection reason {reason}; rc={r.returncode}; out={r.stdout}; err={r.stderr}")
        after = {o: (td / o).read_bytes() if (td / o).exists() else None for o in OUTPUTS}
        if before != after:
            raise AssertionError(f"{label}: rejection mutated output state")
    finally:
        shutil.rmtree(td)

def main():
    protected = {}
    for name in INPUTS:
        p = ROOT / name
        protected[name] = p.read_bytes()

    td = prepare()
    try:
        r = run(td)
        if r.returncode != 0:
            raise AssertionError(f"canonical run failed: {r.stdout} {r.stderr}")
        report = load(td / "stream-report.json")
        preds = load(td / "prediction-ledger.json")
        actions = load(td / "action-ledger.json")
        checkpoint = load(td / "stream-checkpoint.json")
        assert report == {
            "broker_exactly_once_claimed": False,
            "business_action_idempotency_verified": True,
            "checkpoint_commit_verified": True,
            "committed_offset_exclusive": 918204,
            "decision": "accepted",
            "processed_deliveries": 4,
            "promotion_authorized": False,
            "replay_deliveries": 1,
            "retraining_authorized": False,
            "stream_subject_id": "MLOPS-PAY-INF-STREAM-2026-08-r42",
            "unique_events": 3,
        }
        assert [p["score"] for p in preds] == [0.571506, 0.763145, 0.903958]
        assert [a["action"] for a in actions] == ["manual_review", "manual_review", "decline"]
        assert len({a["operation_id"] for a in actions}) == 3
        assert checkpoint["committed_offset_exclusive"] == 918204
        assert checkpoint["durable_predictions"] == checkpoint["durable_actions"] == 3
        before = {o: (td / o).read_bytes() for o in OUTPUTS}
        r2 = run(td)
        assert r2.returncode == 0
        after = {o: (td / o).read_bytes() for o in OUTPUTS}
        assert before == after, "exact replay must be byte-idempotent"
        assert not (td / "promotion-request.json").exists()
        assert not (td / "retraining-request.json").exists()
    finally:
        shutil.rmtree(td)

    def trace_mut(field, value):
        def m(td, _): mutate_json(td, "runtime-trace.json", lambda d: d.__setitem__(field, value))
        return m

    expect_reject("stale model", trace_mut("loaded_model_digest", "sha256:" + "a"*64), "loaded_model_digest_mismatch")
    expect_reject("wrong runtime", trace_mut("loaded_runtime_image_digest", "sha256:" + "b"*64), "loaded_runtime_image_digest_mismatch")
    expect_reject("wrong release", trace_mut("loaded_release_subject", "MLOPS-PAY-RISK-PROD-2026-08-r41"), "loaded_release_mismatch")
    expect_reject("wrong feature contract", trace_mut("loaded_feature_contract_id", "payment-risk-features-v5"), "loaded_feature_contract_mismatch")
    expect_reject("wrong policy", trace_mut("loaded_policy_digest", "sha256:" + "c"*64), "loaded_policy_digest_mismatch")
    expect_reject("wrong schema", trace_mut("loaded_schema_id", "risk-event-v4"), "loaded_schema_mismatch")

    def generation_regression(td, _):
        mutate_json(td, "runtime-trace.json", lambda d: d["deliveries"][-1].__setitem__("generation", 43))
    expect_reject("generation regression", generation_regression, "generation_regression")

    def missing_offset(td, _):
        mutate_json(td, "runtime-trace.json", lambda d: d.__setitem__("deliveries", [x for x in d["deliveries"] if x["offset"] != 918203]))
    expect_reject("missing offset", missing_offset, "delivery_range_incomplete")

    def replay_before_checkpoint(td, _):
        def f(d): d["deliveries"].insert(3, {"generation": 45, "offset": 918201, "processed_at": "2026-08-18T10:01:31Z", "reason": "bad_replay"})
        mutate_json(td, "runtime-trace.json", f)
    expect_reject("replay before checkpoint", replay_before_checkpoint, "rebalance_replay_before_checkpoint")

    def future_feature(td, _):
        mutate_json(td, "events.json", lambda d: d["events"][2].__setitem__("feature_available_at", "2026-08-18T09:58:31Z"), repin_events=True)
    expect_reject("future feature", future_feature, "feature_time_travel")

    def too_late(td, _):
        def f(d):
            d["events"][2]["event_time"] = "2026-08-18T09:50:00Z"
            d["events"][2]["feature_available_at"] = "2026-08-18T09:49:58Z"
        mutate_json(td, "events.json", f, repin_events=True)
    expect_reject("too late", too_late, "event_beyond_allowed_lateness")

    def source_schema(td, _):
        mutate_json(td, "events.json", lambda d: d["events"][1].__setitem__("schema_id", "risk-event-v4"), repin_events=True)
    expect_reject("source schema", source_schema, "event_schema_mismatch")

    def promotion_authority(td, _):
        mutate_json(td, "stream-contract.json", lambda d: d.__setitem__("promotion_authorized", True))
    expect_reject("promotion authority", promotion_authority, "promotion_authority_violation")

    # Tampered exact bytes are rejected by the pinned digest.
    def tampered_model(td, _):
        p=td/"model.json"; p.write_text(p.read_text()+" ")
    expect_reject("tampered model bytes", tampered_model, "model_digest_mismatch")

    # Existing conflicting action state must never be overwritten.
    td = prepare()
    try:
        assert run(td).returncode == 0
        actions = load(td / "action-ledger.json")
        actions[1]["action"] = "approve"
        write(td / "action-ledger.json", actions)
        conflict_bytes = (td / "action-ledger.json").read_bytes()
        r = run(td)
        assert r.returncode != 0 and "action_ledger_conflict" in r.stdout
        assert (td / "action-ledger.json").read_bytes() == conflict_bytes
    finally:
        shutil.rmtree(td)

    for name, before in protected.items():
        if (ROOT / name).read_bytes() != before:
            raise AssertionError(f"protected input mutated: {name}")

    print(PASS)

if __name__ == "__main__":
    main()
