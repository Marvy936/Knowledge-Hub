#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

FILES=["system-contract.json","system-evidence.json","feedback-evidence.json","second-operation.json"]
OUT=["system-report.json","system-evidence-ledger.json"]
BASE={n:Path(n).read_text() for n in FILES}
GATE=Path("system_gate.py").read_text()

def load(p): return json.loads(Path(p).read_text())
def write(p,o): Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
def restore():
    for n,t in BASE.items(): Path(n).write_text(t)
    for n in OUT: Path(n).unlink(missing_ok=True)
    Path("system_gate.py").write_text(GATE)
def run(): return subprocess.run([sys.executable,"./system_gate.py"],text=True,capture_output=True)
def reject(label):
    r=run()
    assert r.returncode!=0,label+" unexpectedly passed"
    assert not Path("system-evidence-ledger.json").exists(),label+" wrote ledger"
def healthy():
    c=load("system-contract.json")
    s=load("system-evidence.json")
    s["boundary_id"]=c["system"]["boundary_id"]
    s["flow"]=c["system"]["flow"]
    s["constraint_claim"]=c["system"]["constraint"]
    write("system-evidence.json",s)

    f=load("feedback-evidence.json")
    f["observation"]={"complete":True,"outcome_count":10000,"request_count":10000,"source":"production-trace-and-queue"}
    f["comparison"]={"global_outcome_checked":True,"target_checked":True}
    f["loop"]={"edges":c["system"]["reinforcing_loop"],"type_claim":"reinforcing"}
    f["decision"]={"authority_scope":c["system"]["boundary_id"],"owner":"checkout-oncall"}
    f["correction"]={"action":"bound-retries-backoff-load-shed","api_scale_change":False,"exponential_backoff":True,"load_shed":True,"retry_limit":1}
    f["delay"]={"accounted":True,"propagation_delay_seconds":120,"verification_after_seconds":180}
    f["verification"]={"boundary_id":c["system"]["boundary_id"],"checkout_success_rate":0.997,"downstream_timeout_rate":0.006,"effective_downstream_demand_rps":68,"queue_age_seconds":18}
    write("feedback-evidence.json",f)

    second=load("second-operation.json")
    second["same_subject"]=True
    second["evidence_mutations"]=0
    second["report_byte_identical"]=True
    write("second-operation.json",second)

restore(); reject("canonical local-optimization incident")
print("PASS local green state cannot substitute for end-to-end system recovery")

restore(); healthy(); s=load("system-evidence.json"); s["boundary_id"]="checkout-api-only"; s["flow"]=["client","checkout-api"]; write("system-evidence.json",s); reject("narrow boundary")
print("PASS too-narrow system boundary is blocked")

restore(); healthy(); s=load("system-evidence.json"); s["constraint_claim"]="checkout-api"; write("system-evidence.json",s); reject("local constraint")
print("PASS local component metric cannot replace the actual system constraint")

restore(); healthy(); f=load("feedback-evidence.json"); f["loop"]["type_claim"]="balancing"; write("feedback-evidence.json",f); reject("wrong loop type")
print("PASS retry amplification must be recognized as a reinforcing loop")

restore(); healthy(); f=load("feedback-evidence.json"); f["observation"]["complete"]=False; write("feedback-evidence.json",f); reject("incomplete feedback")
print("PASS incomplete observation cannot close a feedback loop")

restore(); healthy(); f=load("feedback-evidence.json"); f["correction"]["retry_limit"]=3; f["correction"]["exponential_backoff"]=False; write("feedback-evidence.json",f); reject("unbounded retry correction")
print("PASS systemic correction must bound retry amplification")

restore(); healthy(); f=load("feedback-evidence.json"); f["delay"]["verification_after_seconds"]=30; write("feedback-evidence.json",f); reject("premature verification")
print("PASS correction verification must account for propagation delay")

restore(); healthy(); f=load("feedback-evidence.json"); f["verification"]["boundary_id"]="checkout-api-only"; write("feedback-evidence.json",f); reject("local-only verification")
print("PASS correction must be verified on the same global outcome boundary")

restore(); healthy(); r=run(); assert r.returncode==0,r.stdout+r.stderr
rep=load("system-report.json")
assert rep["system_integrity_verified"] is True
assert rep["optimization_authorized"] is False
assert rep["constraint"]=="payment-worker"
assert rep["loop_type"]=="reinforcing"
assert rep["global_recovered"] is True
rb=Path("system-report.json").read_bytes(); lb=Path("system-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode==0,r.stdout+r.stderr
assert Path("system-report.json").read_bytes()==rb and Path("system-evidence-ledger.json").read_bytes()==lb
print("PASS healthy system feedback evidence is byte-idempotent")

Path("system-evidence-ledger.json").write_text('{"conflict":true}\n')
before=Path("system-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode!=0
assert Path("system-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable system evidence is preserved")

restore(); print("VALIDATION PASSED")
