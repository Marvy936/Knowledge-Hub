#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
FILES=["troubleshooting-contract.json","incident-manifest.json","evidence-bundle.json","state-ladder.json","hypotheses.json","containment-recovery.json","second-operation.json"]
OUT=["troubleshooting-report.json","troubleshooting-evidence-ledger.json"]
BASE={n:Path(n).read_text() for n in FILES}
def load(p): return json.loads(Path(p).read_text())
def write(p,o): Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
def restore():
    for n,t in BASE.items(): Path(n).write_text(t)
    for n in OUT: Path(n).unlink(missing_ok=True)
def run(): return subprocess.run([sys.executable,"./troubleshooting_gate.py"],text=True,capture_output=True)
def reject(label):
    r=run(); assert r.returncode!=0,label+" unexpectedly passed"
    assert not Path("troubleshooting-evidence-ledger.json").exists(),label+" wrote ledger"
def healthy():
    c=load("troubleshooting-contract.json")
    i=load("incident-manifest.json"); i["change_freeze"]=True; i["mutations_after_detection"]=[]; i["exact_ids"]["feature_generation"]=c["incident_observed"]["loaded_feature_generation"]; write("incident-manifest.json",i)
    e=load("evidence-bundle.json"); e["preserved_before_mutation"]=True; e["clock_context_recorded"]=True
    e["feature_materialization"]={"present":True,"digest":"sha256:feature-materialization-r51"}; e["logs_traces"]={"present":True,"digest":"sha256:logs-traces-r51"}; e["external_side_effects"]={"present":True,"digest":"sha256:side-effects-r51"}
    e["monitor_query"]["denominator_recorded"]=True; e["monitor_query"]["sampling_recorded"]=True; write("evidence-bundle.json",e)
    l=load("state-ladder.json"); l["declared_first_divergence"]="loaded"; write("state-ladder.json",l)
    h=load("hypotheses.json"); h["root_cause_hypothesis_id"]="stale-feature-materialization"; h["one_variable_tests"]=True
    for x in h["items"]:
        if x["id"] in ("mixed-serving-runtime","stale-feature-materialization","feedback-join-loss"): x["result"]="confirmed"
        elif x["id"]=="concept-drift": x["result"]="unknown"
    write("hypotheses.json",h)
    r=load("containment-recovery.json")
    r["containment"]={"change_freeze":True,"traffic_increase_stopped":True,"unsafe_retraining_disabled":True,"operation_ids_recorded":True}
    r["recovery"]={"known_good_release":c["known_good"]["release_id"],"loaded_fingerprint_parity":True,"feature_generation":c["known_good"]["feature_generation"],"runtime_image":c["known_good"]["runtime_image"],"actual_traffic_verified":True,"false_positive_rate_recovered":True,"p99_recovered":True,"side_effects_reconciled":True,"duplicate_model_packages":0}
    r["corrective_action"]={"generation":c["corrective_control"]["generation"],"mechanism_fixed":True,"acceptance_test_passed":True}; write("containment-recovery.json",r)
    s=load("second-operation.json"); s["same_subject"]=True; s["read_before_retry"]=True; s["duplicate_side_effects"]=0; s["evidence_preserved_before_mutation"]=True; s["corrective_control_generation"]=c["corrective_control"]["generation"]; s["corrective_control_held"]=True; s["loaded_fingerprint_parity"]=True; s["business_outcome_verified"]=True; write("second-operation.json",s)

restore(); reject("canonical restart-is-green incident"); print("PASS green-after-restart cannot substitute for preserved evidence and root cause")
restore(); c=load("troubleshooting-contract.json"); c["authority"]["rollout_authorized"]=True; write("troubleshooting-contract.json",c); reject("tampered authority"); print("PASS troubleshooting evidence cannot grant rollout authority")
restore(); healthy(); e=load("evidence-bundle.json"); e["preserved_before_mutation"]=False; write("evidence-bundle.json",e); reject("unpreserved evidence"); print("PASS mutations before evidence preservation are blocked")
restore(); healthy(); l=load("state-ladder.json"); l["declared_first_divergence"]="outcome"; write("state-ladder.json",l); reject("wrong first divergence"); print("PASS unsupported first-divergence declaration is blocked")
restore(); healthy(); h=load("hypotheses.json"); h["root_cause_hypothesis_id"]="concept-drift"; write("hypotheses.json",h); reject("unsupported concept drift root cause"); print("PASS root cause must match tested competing hypotheses")
restore(); healthy(); r=load("containment-recovery.json"); r["recovery"]["loaded_fingerprint_parity"]=False; write("containment-recovery.json",r); reject("partial recovery"); print("PASS recovery requires complete loaded-state convergence")
restore(); healthy(); s=load("second-operation.json"); s["read_before_retry"]=False; write("second-operation.json",s); reject("blind retry"); print("PASS second operation requires read-before-retry")
restore(); healthy(); r=run(); assert r.returncode==0,r.stdout+r.stderr
rep=load("troubleshooting-report.json"); assert rep["troubleshooting_verified"] and not rep["rollout_authorized"] and not rep["promotion_authorized"] and not rep["retraining_authorized"]
rb=Path("troubleshooting-report.json").read_bytes(); lb=Path("troubleshooting-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode==0,r.stdout+r.stderr
assert Path("troubleshooting-report.json").read_bytes()==rb and Path("troubleshooting-evidence-ledger.json").read_bytes()==lb
print("PASS healthy troubleshooting evidence is byte-idempotent")
Path("troubleshooting-evidence-ledger.json").write_text('{"conflict":true}\n'); before=Path("troubleshooting-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode!=0; assert Path("troubleshooting-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable troubleshooting evidence is preserved")
restore(); print("VALIDATION PASSED")
