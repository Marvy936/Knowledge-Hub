#!/usr/bin/env python3
import json, subprocess, sys
from datetime import datetime, timedelta
from pathlib import Path

FILES=["flow-contract.json","baseline-events.json","improvement-events.json","dashboard.json","improvement-plan.json","feedback-evidence.json","second-operation.json"]
OUT=["flow-report.json","flow-evidence-ledger.json"]
BASE={name:Path(name).read_text() for name in FILES}

def load(path): return json.loads(Path(path).read_text())
def write(path,obj): Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
def parse(ts): return datetime.fromisoformat(ts.replace("Z","+00:00"))
def iso(dt): return dt.isoformat().replace("+00:00","Z")
def restore():
    for name,text in BASE.items(): Path(name).write_text(text)
    for name in OUT: Path(name).unlink(missing_ok=True)
def run(): return subprocess.run([sys.executable,"./flow_gate.py"],text=True,capture_output=True)
def reject(label):
    result=run()
    assert result.returncode!=0,label+" unexpectedly passed"
    assert not Path("flow-evidence-ledger.json").exists(),label+" wrote ledger"

def healthy():
    imp=load("improvement-events.json")
    for ch in imp["changes"]:
        ev=ch["events"]
        approval=parse(ev["approval_requested"])
        granted=approval+timedelta(minutes=60)
        deploy_start=granted+timedelta(minutes=15)
        deploy_end=deploy_start+timedelta(minutes=10)
        verified=deploy_end+timedelta(minutes=10)
        ev["approval_granted"]=iso(granted)
        ev["deploy_start"]=iso(deploy_start)
        ev["deploy_end"]=iso(deploy_end)
        ev["production_verified"]=iso(verified)
        ev.pop("failure_detected",None)
        ev.pop("capability_restored",None)
        ch["result"]="success"
    write("improvement-events.json",imp)
    plan=load("improvement-plan.json")
    plan["hypothesis_id"]="hyp-approval-queue"
    plan["observed_bottleneck"]="approval_queue"
    plan["change"]="replace fixed approval window with bounded risk-based approval SLA"
    plan["target_metrics"]=["lead_time_minutes","approval_wait_minutes","change_failure_rate"]
    plan["owner"]="checkout-service-team"
    plan["standard_work_updated"]=True
    write("improvement-plan.json",plan)
    feedback=load("feedback-evidence.json")
    feedback.update({
      "signal":"approval queue dominates end-to-end change lead time",
      "owner":"checkout-service-team",
      "observation":"raw value-stream events show approval wait dominates process time",
      "decision":"run bounded approval-SLA experiment for standard production changes",
      "corrective_action":"apply risk-based approval SLA and preserve verification/recovery gates",
      "re_observed":True,
      "outcome_changed":True,
      "learning_recorded":True
    })
    write("feedback-evidence.json",feedback)
    second=load("second-operation.json")
    second.update({
      "same_event_contract":True,
      "same_population_definition":True,
      "recompute_required":True,
      "manual_metric_override":False,
      "replayed_from_raw_events":True
    })
    write("second-operation.json",second)

restore(); reject("canonical local-optimization incident")
print("PASS faster build plus green dashboard cannot prove delivery improvement")
restore(); healthy()
c=load("flow-contract.json"); c["authority"]["rollout_authorized"]=True; write("flow-contract.json",c)
reject("tampered authority")
print("PASS exact flow contract and authority boundary are enforced")
restore(); healthy()
imp=load("improvement-events.json"); imp["population"]["change_class"]="emergency-hotfix"; write("improvement-events.json",imp)
reject("population substitution")
print("PASS baseline and improvement populations must be comparable")
restore(); healthy()
imp=load("improvement-events.json"); imp["changes"][0]["artifact_digest"]="checkout:latest"; write("improvement-events.json",imp)
reject("mutable lifecycle identity")
print("PASS SDLC change chain requires immutable artifact identity")
restore(); healthy()
plan=load("improvement-plan.json"); plan["observed_bottleneck"]="build"; plan["target_metrics"]=["build_duration_minutes"]; write("improvement-plan.json",plan)
reject("local optimization")
print("PASS systems thinking rejects local build optimization when approval queue dominates")
restore(); healthy()
feedback=load("feedback-evidence.json"); feedback["re_observed"]=False; feedback["outcome_changed"]=False; write("feedback-evidence.json",feedback)
reject("open feedback loop")
print("PASS feedback requires observation, action and re-observation")
restore(); healthy()
second=load("second-operation.json"); second["manual_metric_override"]=True; second["replayed_from_raw_events"]=False; write("second-operation.json",second)
reject("manual metric override")
print("PASS second operation must recompute from raw events")
restore(); healthy()
result=run(); assert result.returncode==0,result.stdout+result.stderr
report=load("flow-report.json")
assert report["flow_verified"] and report["dora_recomputed"] and report["feedback_loop_verified"]
assert not report["dashboard_claim_used_as_authority"]
assert not report["rollout_authorized"] and not report["promotion_authorized"]
rb=Path("flow-report.json").read_bytes(); lb=Path("flow-evidence-ledger.json").read_bytes()
result=run(); assert result.returncode==0,result.stdout+result.stderr
assert Path("flow-report.json").read_bytes()==rb and Path("flow-evidence-ledger.json").read_bytes()==lb
print("PASS healthy flow evidence is byte-idempotent")
Path("flow-evidence-ledger.json").write_text('{"conflict":true}\n')
before=Path("flow-evidence-ledger.json").read_bytes()
result=run(); assert result.returncode!=0
assert Path("flow-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable flow evidence is preserved")
restore(); print("VALIDATION PASSED")
