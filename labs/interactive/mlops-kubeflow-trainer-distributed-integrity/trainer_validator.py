#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

FILES=["trainer-contract.json","trainjob-evidence.json","topology-evidence.json","partition-evidence.json","checkpoint-evidence.json","resume-evidence.json","second-operation.json"]
OUT=["trainer-report.json","trainer-evidence-ledger.json"]; BASE={n:Path(n).read_text() for n in FILES}
def load(p): return json.loads(Path(p).read_text())
def write(p,o): Path(p).write_text(json.dumps(o,indent=2)+"\n")
def restore():
    for n,t in BASE.items(): Path(n).write_text(t)
    for n in OUT: Path(n).unlink(missing_ok=True)
def run(): return subprocess.run([sys.executable,"./trainer_gate.py"],text=True,capture_output=True)
def reject(label):
    r=run(); assert r.returncode!=0,label
    assert not Path("trainer-evidence-ledger.json").exists(),label+" ledger"
def healthy():
    c=load("trainer-contract.json")
    j=load("trainjob-evidence.json"); j["resolved_runtime_generation"]=c["runtime"]["generation"]; j["resolved_runtime_manifest_digest"]=c["runtime"]["resolved_manifest_digest"]; write("trainjob-evidence.json",j)
    p=load("partition-evidence.json"); p["workers"]=[{"rank":0,"start":0,"end":2999},{"rank":1,"start":3000,"end":5999},{"rank":2,"start":6000,"end":8999},{"rank":3,"start":9000,"end":11999}]; write("partition-evidence.json",p)
    ck=load("checkpoint-evidence.json"); ck["state_present"]=["model","optimizer","scheduler","sampler","rng"]; ck["runtime_generation"]=c["runtime"]["generation"]; ck["fresh_restore_test"]=True; ck["restored_next_step"]=True; write("checkpoint-evidence.json",ck)
    r=load("resume-evidence.json"); r["resume_world_size"]=r["source_world_size"]; r["optimizer_restored"]=True; r["scheduler_restored"]=True; r["sampler_cursor_restored"]=True; r["rng_restored"]=True; r["processed_sample_parity"]=True; write("resume-evidence.json",r)
    s=load("second-operation.json"); s["same_subject"]=True; s["duplicate_samples"]=0; s["duplicate_model_artifact"]=False; s["processed_sample_count"]=c["dataset"]["sample_count"]; s["manual_runtime_patch"]=False; write("second-operation.json",s)

restore(); reject("canonical Succeeded Trainer incident"); print("PASS Succeeded TrainJob cannot hide Runtime/partition/checkpoint/resume failures")
restore(); c=load("trainer-contract.json"); c["authority"]["promotion_authorized"]=True; write("trainer-contract.json",c); reject("tampered authority"); print("PASS contract authority tampering is blocked")
restore(); healthy(); j=load("trainjob-evidence.json"); j["resolved_runtime_generation"]="19"; write("trainjob-evidence.json",j); reject("Runtime substitution"); print("PASS resolved Runtime substitution is blocked")
restore(); healthy(); p=load("partition-evidence.json"); p["workers"][1]["start"]=2500; write("partition-evidence.json",p); reject("overlapping shards"); print("PASS overlapping distributed shards are blocked")
restore(); healthy(); ck=load("checkpoint-evidence.json"); ck["state_present"]=["model"]; write("checkpoint-evidence.json",ck); reject("weights-only checkpoint"); print("PASS weights-only checkpoint is blocked")
restore(); healthy(); r=load("resume-evidence.json"); r["resume_world_size"]=2; write("resume-evidence.json",r); reject("undeclared world-size change"); print("PASS undeclared topology change on resume is blocked")
restore(); healthy(); r=run(); assert r.returncode==0,r.stdout+r.stderr
rep=load("trainer-report.json"); assert rep["trainer_integrity_verified"] and not rep["rollout_authorized"] and not rep["promotion_authorized"] and not rep["retraining_authorized"]
rb=Path("trainer-report.json").read_bytes(); lb=Path("trainer-evidence-ledger.json").read_bytes(); r=run(); assert r.returncode==0,r.stdout+r.stderr
assert Path("trainer-report.json").read_bytes()==rb and Path("trainer-evidence-ledger.json").read_bytes()==lb
print("PASS healthy Trainer subject is byte-idempotent")
Path("trainer-evidence-ledger.json").write_text('{"conflict":true}\n'); before=Path("trainer-evidence-ledger.json").read_bytes(); r=run(); assert r.returncode!=0; assert Path("trainer-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable Trainer evidence is preserved")
restore(); print("VALIDATION PASSED")
