#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

FILES=["sagemaker-contract.json","pipeline-evidence.json","registry-evidence.json","endpoint-evidence.json","monitor-evidence.json","parity-evidence.json","second-operation.json"]
OUT=["sagemaker-report.json","sagemaker-evidence-ledger.json"]
BASE={n:Path(n).read_text() for n in FILES}
def load(p): return json.loads(Path(p).read_text())
def write(p,o): Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
def restore():
    for n,t in BASE.items(): Path(n).write_text(t)
    for n in OUT: Path(n).unlink(missing_ok=True)
def run(): return subprocess.run([sys.executable,"./sagemaker_gate.py"],text=True,capture_output=True)
def reject(label):
    r=run()
    assert r.returncode!=0,label+" unexpectedly passed"
    assert not Path("sagemaker-evidence-ledger.json").exists(),label+" wrote ledger"
def healthy():
    c=load("sagemaker-contract.json")
    p=load("pipeline-evidence.json")
    p["processing_input"]={"s3_uri":c["data"]["s3_uri"],"s3_version_id":c["data"]["s3_version_id"],"dataset_digest":c["data"]["dataset_digest"]}
    p["processing_image"]=c["images"]["processing_image"]; p["training_image"]=c["images"]["training_image"]; write("pipeline-evidence.json",p)
    r=load("registry-evidence.json"); r["inference_image"]=c["images"]["inference_image"]; write("registry-evidence.json",r)
    e=load("endpoint-evidence.json")
    e["endpoint_config_arn"]=c["serving"]["endpoint_config_arn"]; e["model_arn"]=c["serving"]["model_arn"]
    e["loaded_model_package_arn"]=c["registry"]["model_package_arn"]; e["loaded_model_digest"]=c["release"]["model_artifact_digest"]
    e["synthetic_request"]["release_id"]=c["release"]["release_id"]; e["synthetic_request"]["model_digest"]=c["release"]["model_artifact_digest"]; write("endpoint-evidence.json",e)
    m=load("monitor-evidence.json"); m["baseline_feature_generation"]=c["monitoring"]["baseline_feature_generation"]; m["baseline_dataset_digest"]=c["monitoring"]["baseline_dataset_digest"]; write("monitor-evidence.json",m)
    x=load("parity-evidence.json"); x["aws_loaded_model_digest"]=c["release"]["model_artifact_digest"]; x["same_model_bytes"]=True; x["same_acceptance_subject"]=True; write("parity-evidence.json",x)
    s=load("second-operation.json"); s["model_package_read_before_retry"]=True; s["duplicate_model_package_created"]=None; s["endpoint_read_before_retry"]=True; s["duplicate_endpoint_update_submitted"]=False; s["loaded_state_reconciled"]=True; write("second-operation.json",s)

restore(); reject("canonical cloud-migration incident"); print("PASS Succeeded/Approved/InService cannot hide immutable cloud mapping failures")
restore(); c=load("sagemaker-contract.json"); c["authority"]["rollout_authorized"]=True; write("sagemaker-contract.json",c); reject("tampered authority"); print("PASS lifecycle authority tampering is blocked")
restore(); healthy(); p=load("pipeline-evidence.json"); p["processing_input"]["s3_uri"]="s3://fraud-ml-prod/datasets/fraud/latest/"; p["processing_input"]["s3_version_id"]=None; write("pipeline-evidence.json",p); reject("mutable S3 input"); print("PASS mutable S3 processing input is blocked")
restore(); healthy(); p=load("pipeline-evidence.json"); p["training_image"]="123456789012.dkr.ecr.eu-central-1.amazonaws.com/fraud-training:latest"; write("pipeline-evidence.json",p); reject("tagged training image"); print("PASS mutable ECR training image is blocked")
restore(); healthy(); e=load("endpoint-evidence.json"); e["loaded_model_package_arn"]="arn:aws:sagemaker:eu-central-1:123456789012:model-package/fraud-prod/183"; write("endpoint-evidence.json",e); reject("stale loaded package"); print("PASS stale production Model Package is blocked")
restore(); healthy(); m=load("monitor-evidence.json"); m["baseline_feature_generation"]="fraud-features-v15"; write("monitor-evidence.json",m); reject("baseline mismatch"); print("PASS Model Monitor baseline generation mismatch is blocked")
restore(); healthy(); s=load("second-operation.json"); s["model_package_read_before_retry"]=False; write("second-operation.json",s); reject("blind retry"); print("PASS unknown-outcome Model Package retry without read-back is blocked")
restore(); healthy(); r=run(); assert r.returncode==0,r.stdout+r.stderr
rep=load("sagemaker-report.json")
assert rep["sagemaker_mapping_verified"] and not rep["rollout_authorized"] and not rep["promotion_authorized"] and not rep["retraining_authorized"]
rb=Path("sagemaker-report.json").read_bytes(); lb=Path("sagemaker-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode==0,r.stdout+r.stderr
assert Path("sagemaker-report.json").read_bytes()==rb and Path("sagemaker-evidence-ledger.json").read_bytes()==lb
print("PASS healthy SageMaker mapping is byte-idempotent")
Path("sagemaker-evidence-ledger.json").write_text('{"conflict":true}\n')
before=Path("sagemaker-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode!=0
assert Path("sagemaker-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable SageMaker evidence is preserved")
restore(); print("VALIDATION PASSED")
