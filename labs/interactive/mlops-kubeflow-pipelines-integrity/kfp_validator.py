#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

FILES=["kfp-contract.json","run-evidence.json","cache-evidence.json","artifact-evidence.json","mutation-evidence.json","second-operation.json"]
OUT=["kfp-report.json","kfp-evidence-ledger.json"]
BASE={n:Path(n).read_text() for n in FILES}

def load(p): return json.loads(Path(p).read_text())
def write(p,o): Path(p).write_text(json.dumps(o,indent=2)+"\n")
def restore():
    for n,t in BASE.items(): Path(n).write_text(t)
    for n in OUT: Path(n).unlink(missing_ok=True)
def run_gate(): return subprocess.run([sys.executable,"./kfp_gate.py"],text=True,capture_output=True)
def reject(label):
    r=run_gate()
    assert r.returncode!=0,label+" unexpectedly passed"
    assert not Path("kfp-evidence-ledger.json").exists(),label+" wrote ledger"
def healthy():
    c=load("kfp-contract.json")
    r=load("run-evidence.json")
    r["compiled_ir_digest"]=c["compiled_ir_digest"]
    for t in r["tasks"]:
        t["accepted_attempt"]=1
        t["attempts"]=[1]
    write("run-evidence.json",r)

    x=load("cache-evidence.json")
    x["preprocess"]["external_lookup_generation"]=c["external"]["lookup_generation"]
    x["preprocess"]["hidden_dependency_complete"]=True
    write("cache-evidence.json",x)

    m=load("mutation-evidence.json")
    m["read_before_retry_performed"]=True
    m["retry_submitted"]=False
    m["duplicate_version_created"]=None
    write("mutation-evidence.json",m)

    s=load("second-operation.json")
    s["same_compiled_ir"]=True
    s["mutation_read_before_retry"]=True
    s["mutation_noop_reconciled"]=True
    s["new_registry_version_created"]=None
    write("second-operation.json",s)

restore(); reject("canonical green KFP run")
print("PASS green KFP run cannot hide IR/cache/mutation integrity failures")

restore(); c=load("kfp-contract.json"); c["authority"]["promotion_authorized"]=True; write("kfp-contract.json",c); reject("tampered authority contract")
print("PASS authority contract tampering is blocked")

restore(); healthy(); x=load("cache-evidence.json"); x["preprocess"]["external_lookup_generation"]="merchant-risk-table-latest"; write("cache-evidence.json",x); reject("mutable hidden lookup")
print("PASS mutable hidden cache dependency is blocked")

restore(); healthy(); r=load("run-evidence.json"); r["tasks"][3]["attempts"]=[1,2]; r["tasks"][3]["accepted_attempt"]=2; write("run-evidence.json",r); reject("ambiguous register attempt")
print("PASS duplicate mutation attempt evidence is blocked")

restore(); healthy(); a=load("artifact-evidence.json"); a["model"]["digest"]="sha256:tampered"; write("artifact-evidence.json",a); reject("artifact substitution")
print("PASS artifact substitution is blocked")

restore(); healthy(); r=run_gate(); assert r.returncode==0,r.stdout+r.stderr
rep=load("kfp-report.json")
assert rep["kfp_integrity_verified"] and not rep["rollout_authorized"] and not rep["promotion_authorized"] and not rep["retraining_authorized"]
rb=Path("kfp-report.json").read_bytes(); lb=Path("kfp-evidence-ledger.json").read_bytes()
r=run_gate(); assert r.returncode==0,r.stdout+r.stderr
assert Path("kfp-report.json").read_bytes()==rb and Path("kfp-evidence-ledger.json").read_bytes()==lb
print("PASS healthy immutable KFP subject is byte-idempotent")

Path("kfp-evidence-ledger.json").write_text('{"conflict":true}\n')
before=Path("kfp-evidence-ledger.json").read_bytes()
r=run_gate(); assert r.returncode!=0
assert Path("kfp-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable KFP evidence is preserved")

restore(); print("VALIDATION PASSED")
