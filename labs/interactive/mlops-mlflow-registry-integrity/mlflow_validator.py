#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
FILES=["mlflow-contract.json","dataset-manifest.json","evaluation-evidence.json","tracking-evidence.json","registry-evidence.json","deployment-evidence.json","second-operation.json"]
OUT=["mlflow-report.json","mlflow-evidence-ledger.json"]
BASE={n:Path(n).read_text() for n in FILES}
def load(p): return json.loads(Path(p).read_text())
def write(p,o): Path(p).write_text(json.dumps(o,indent=2)+"\n")
def restore():
    for n,t in BASE.items(): Path(n).write_text(t)
    for n in OUT: Path(n).unlink(missing_ok=True)
def run(): return subprocess.run([sys.executable,"./mlflow_gate.py"],text=True,capture_output=True)
def reject(label):
    r=run(); assert r.returncode!=0,label
    assert not Path("mlflow-evidence-ledger.json").exists(),label+" ledger"
def healthy():
    ds=load("dataset-manifest.json")
    tr=load("tracking-evidence.json"); tr["dataset_input"]["source"]=ds["snapshot_uri"]; tr["dataset_input"]["manifest_digest"]=ds["manifest_digest"]; write("tracking-evidence.json",tr)
    rg=load("registry-evidence.json"); rg["mutation"]["read_before_retry_performed"]=True; rg["mutation"]["retry_submitted"]=False; write("registry-evidence.json",rg)
    dep=load("deployment-evidence.json"); c=load("mlflow-contract.json")
    dep["registry_resolution_mode"]="immutable_version_once"; dep["resolved_registry_version"]="185"; dep["resolved_model_digest"]=c["logged_model"]["model_digest"]
    for r in dep["replicas"]: r["loaded_registry_version"]="185"; r["loaded_model_digest"]=c["logged_model"]["model_digest"]
    dep["synthetic_inference"]["exact_version_verified"]=True; dep["synthetic_inference"]["exact_model_digest_verified"]=True; write("deployment-evidence.json",dep)
    s=load("second-operation.json"); s["read_before_retry_performed"]=True; s["existing_version_reused"]=True; s["duplicate_version_created"]=None; s["fresh_load_version"]="185"; write("second-operation.json",s)
restore(); reject("canonical mutable MLflow path"); print("PASS green run + champion alias cannot hide mutable dataset and mixed deployment")
restore(); c=load("mlflow-contract.json"); c["authority"]["rollout_authorized"]=True; write("mlflow-contract.json",c); reject("tampered contract"); print("PASS tampered MLflow authority contract is blocked")
restore(); rg=load("registry-evidence.json"); rg["version"]["source_model_digest"]="sha256:tampered"; write("registry-evidence.json",rg); reject("registry substitution"); print("PASS Registry version source substitution is blocked")
restore(); healthy(); r=run(); assert r.returncode==0,r.stdout+r.stderr
rep=load("mlflow-report.json"); assert rep["mlflow_integrity_verified"] and not rep["rollout_authorized"] and not rep["promotion_authorized"] and not rep["retraining_authorized"]
rb=Path("mlflow-report.json").read_bytes(); lb=Path("mlflow-evidence-ledger.json").read_bytes(); r=run(); assert r.returncode==0,r.stdout+r.stderr; assert Path("mlflow-report.json").read_bytes()==rb and Path("mlflow-evidence-ledger.json").read_bytes()==lb
print("PASS exact MLflow run/model/Registry/deployment chain is byte-idempotent")
Path("mlflow-evidence-ledger.json").write_text('{"conflict":true}\n'); before=Path("mlflow-evidence-ledger.json").read_bytes(); r=run(); assert r.returncode!=0; assert Path("mlflow-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable MLflow evidence is preserved")
restore(); print("VALIDATION PASSED")
