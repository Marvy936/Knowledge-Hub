#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

FILES=["automation-contract.json","request-evidence.json","operation-evidence.json","observed-state.json","effective-state.json","recovery-evidence.json","second-operation.json"]
OUT=["automation-report.json","automation-evidence-ledger.json"]
BASE={name:Path(name).read_text() for name in FILES}
GATE=Path("automation_gate.py").read_text()

def load(path): return json.loads(Path(path).read_text())
def write(path,obj): Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
def restore():
    for name,text in BASE.items(): Path(name).write_text(text)
    for name in OUT: Path(name).unlink(missing_ok=True)
    Path("automation_gate.py").write_text(GATE)
def run(): return subprocess.run([sys.executable,"./automation_gate.py"],text=True,capture_output=True)
def reject(label):
    result=run()
    assert result.returncode!=0,label+" unexpectedly passed"
    assert not Path("automation-evidence-ledger.json").exists(),label+" wrote ledger"

def healthy():
    c=load("automation-contract.json")
    op=load("operation-evidence.json")
    op["mode"]="reconcile"
    op["read_before_retry"]=True
    op["authoritative_read_before_retry"]=True
    op["created_resource_ids"]=[c["desired"]["resource_id"]]
    op["reconcile_plan_generated"]=True
    write("operation-evidence.json",op)

    observed=load("observed-state.json")
    r=observed["resources"][0]
    r["resource_id"]=c["desired"]["resource_id"]
    r["environment_key"]=c["desired"]["environment_key"]
    r["owner"]=c["desired"]["owner"]
    r["expiry"]=c["desired"]["expiry"]
    r["network_profile"]=c["desired"]["network_profile"]
    r["artifact_reference"]="registry.example/app@"+c["desired"]["artifact_digest"]
    r["artifact_digest"]=c["desired"]["artifact_digest"]
    r["artifact_mutable"]=False
    r["application_health"]=c["desired"]["application_health"]
    r["manual_override"]=False
    observed["resources"]=[r]
    write("observed-state.json",observed)

    effective=load("effective-state.json")
    effective["resource_id"]=c["desired"]["resource_id"]
    write("effective-state.json",effective)

    recovery=load("recovery-evidence.json")
    recovery["disposition"]="reconcile_existing"
    recovery["final_resource_id"]=c["desired"]["resource_id"]
    recovery["identity_preserved"]=True
    recovery["duplicate_resource_created"]=False
    recovery["partial_state_reconciled"]=True
    write("recovery-evidence.json",recovery)

    second=load("second-operation.json")
    second["same_subject"]=True
    second["read_before_retry"]=True
    second["mutation_count"]=0
    second["inventory_generation_after"]=second["inventory_generation_before"]
    second["resource_count"]=1
    second["duplicate_resources"]=0
    second["effective_readback_repeated"]=True
    write("second-operation.json",second)

restore()
reject("canonical imperative retry incident")
print("PASS green exit/smoke cannot hide duplicate imperative retry")

restore()
healthy()
op=load("operation-evidence.json"); op["read_before_retry"]=False; write("operation-evidence.json",op)
reject("unknown-outcome blind retry")
print("PASS timeout_unknown requires authoritative read-before-retry")

restore()
healthy()
o=load("observed-state.json"); dup=dict(o["resources"][0]); dup["resource_id"]="duplicate"; o["resources"].append(dup); write("observed-state.json",o)
reject("duplicate desired resource")
print("PASS duplicate resources violate stable desired identity")

restore()
healthy()
o=load("observed-state.json"); o["resources"][0]["artifact_mutable"]=True; o["resources"][0]["artifact_reference"]="registry.example/app:latest"; write("observed-state.json",o)
reject("mutable artifact")
print("PASS mutable artifact reference is blocked")

restore()
healthy()
e=load("effective-state.json"); e["loaded_artifact_digest"]="sha256:stale"; write("effective-state.json",e)
reject("stale effective runtime")
print("PASS configured desired state cannot replace effective read-back")

restore()
healthy()
s=load("second-operation.json"); s["mutation_count"]=1; s["inventory_generation_after"]=45; write("second-operation.json",s)
reject("non-idempotent second operation")
print("PASS identical second operation must be a no-op")

restore()
healthy()
o=load("observed-state.json"); o["resources"][0]["manual_override"]=True; write("observed-state.json",o)
reject("manual conflict overwrite")
print("PASS conflicting manual state is rejected rather than silently overwritten")

restore()
healthy()
result=run(); assert result.returncode==0,result.stdout+result.stderr
rb=Path("automation-report.json").read_bytes(); lb=Path("automation-evidence-ledger.json").read_bytes()
result=run(); assert result.returncode==0,result.stdout+result.stderr
assert Path("automation-report.json").read_bytes()==rb and Path("automation-evidence-ledger.json").read_bytes()==lb
print("PASS healthy declarative reconciliation is byte-idempotent")

Path("automation-evidence-ledger.json").write_text('{"conflict":true}\n')
before=Path("automation-evidence-ledger.json").read_bytes()
result=run(); assert result.returncode!=0
assert Path("automation-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable automation evidence is preserved")

restore()
print("VALIDATION PASSED")
