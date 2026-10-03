#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

FILES=[
    "evaluation-contract.json",
    "release-manifest.json",
    "trace-query-manifest.json",
    "classic-evaluation.json",
    "trace-evidence.json",
    "deployment-evidence.json",
    "second-operation.json",
]
OUT=["mlflow-eval-report.json","mlflow-eval-evidence-ledger.json"]
BASE={name:Path(name).read_text() for name in FILES}

def load(p):
    return json.loads(Path(p).read_text())

def write(p,o):
    Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")

def restore():
    for name,text in BASE.items():
        Path(name).write_text(text)
    for name in OUT:
        Path(name).unlink(missing_ok=True)

def run():
    return subprocess.run([sys.executable,"./mlflow_eval_gate.py"],text=True,capture_output=True)

def reject(label):
    r=run()
    assert r.returncode!=0,label+"\n"+r.stdout+r.stderr
    assert not Path("mlflow-eval-evidence-ledger.json").exists(),label+" unexpectedly created ledger"

def healthy():
    classic=load("classic-evaluation.json")
    for row in classic["segments"]:
        if row["segment"]=="channel=mobile":
            row["f1_score"]=0.83
            row["log_loss"]=0.41
    write("classic-evaluation.json",classic)

    traces=load("trace-evidence.json")
    traces["selection_filter"]="all_eligible_requests"
    traces["exported_traces"]=970
    traces["dropped_traces"]=30
    traces["result_classes"]={
        "model_success":900,
        "fallback":50,
        "error":20,
        "deadline_miss":30
    }
    traces["scores"]["correctness_coverage"]=0.97
    write("trace-evidence.json",traces)

    release=load("release-manifest.json")
    deploy=load("deployment-evidence.json")
    for r in deploy["production_target"]["replicas"]:
        r["loaded_release_id"]=release["release_id"]
        r["loaded_model_digest"]=release["model_digest"]
        r["loaded_image_digest"]=release["image_digest"]
        r["runtime_generation"]=release["runtime_generation"]
    deploy["production_target"]["synthetic_request"]["release_identity_verified"]=True
    deploy["production_target"]["synthetic_request"]["model_digest_verified"]=True
    write("deployment-evidence.json",deploy)

    second=load("second-operation.json")
    second["classic_replay_byte_equal"]=True
    second["trace_snapshot_reused"]=True
    second["deployment_noop"]=True
    second["manual_cache_warmup_used"]=False
    second["manual_target_edit_used"]=False
    write("second-operation.json",second)

restore()
reject("canonical collapsed quality verdict")
print("PASS aggregate metrics + sampled traces + local serve cannot establish production integrity")

restore()
c=load("evaluation-contract.json")
c["authority"]["rollout_authorized"]=True
write("evaluation-contract.json",c)
reject("tampered authority contract")
print("PASS authority-contract tampering is blocked")

restore()
classic=load("classic-evaluation.json")
classic["segments"]=[r for r in classic["segments"] if r["segment"]!="channel=mobile"]
write("classic-evaluation.json",classic)
reject("missing required segment")
print("PASS aggregate pass cannot hide missing required segment")

restore()
traces=load("trace-evidence.json")
traces["selection_filter"]="status = 'OK'"
traces["exported_traces"]=990
traces["dropped_traces"]=10
traces["result_classes"]={"model_success":990,"fallback":5,"error":3,"deadline_miss":2}
write("trace-evidence.json",traces)
reject("biased trace population")
print("PASS high trace coverage cannot hide selective successful-request sampling")

restore()
healthy()
deploy=load("deployment-evidence.json")
deploy["production_target"]["replicas"][1]["loaded_image_digest"]="sha256:other"
write("deployment-evidence.json",deploy)
reject("mixed production target")
print("PASS local serve success cannot hide mixed production runtime identity")

restore()
healthy()
r=run()
assert r.returncode==0,r.stdout+r.stderr
report=load("mlflow-eval-report.json")
assert report["mlflow_evaluation_integrity_verified"] is True
assert report["classic_evaluation_verified"] is True
assert report["trace_evidence_verified"] is True
assert report["production_deployment_verified"] is True
assert report["second_operation_verified"] is True
assert report["rollout_authorized"] is False
assert report["promotion_authorized"] is False
assert report["retraining_authorized"] is False
rb=Path("mlflow-eval-report.json").read_bytes()
lb=Path("mlflow-eval-evidence-ledger.json").read_bytes()
r=run()
assert r.returncode==0,r.stdout+r.stderr
assert Path("mlflow-eval-report.json").read_bytes()==rb
assert Path("mlflow-eval-evidence-ledger.json").read_bytes()==lb
print("PASS healthy MLflow evaluation/tracing/deployment evidence is byte-idempotent")

Path("mlflow-eval-evidence-ledger.json").write_text('{"conflict":true}\n')
before=Path("mlflow-eval-evidence-ledger.json").read_bytes()
r=run()
assert r.returncode!=0
assert Path("mlflow-eval-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable evidence is preserved")

restore()
print("VALIDATION PASSED")
