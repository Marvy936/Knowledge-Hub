#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

FILES=["ownership-contract.json","ownership-evidence.json","toil-debt-evidence.json","improvement-evidence.json","second-operation.json"]
OUT=["ownership-report.json","ownership-evidence-ledger.json"]
BASE={n:Path(n).read_text() for n in FILES}
GATE=Path("ownership_gate.py").read_text()

def load(p): return json.loads(Path(p).read_text())
def write(p,o): Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
def restore():
    for n,t in BASE.items(): Path(n).write_text(t)
    for n in OUT: Path(n).unlink(missing_ok=True)
    Path("ownership_gate.py").write_text(GATE)
def run(): return subprocess.run([sys.executable,"./ownership_gate.py"],text=True,capture_output=True)
def reject(label):
    r=run()
    assert r.returncode!=0,label+" unexpectedly passed\n"+r.stdout+r.stderr
    assert not Path("ownership-evidence-ledger.json").exists(),label+" wrote ledger"

def healthy():
    c=load("ownership-contract.json")
    o=load("ownership-evidence.json")
    o["primary_incident_owner"]=c["ownership"]["primary_incident_owner"]
    o["decision_rights"]=c["ownership"]["required_decision_rights"]
    o["direct_runtime_evidence"]=True
    o["platform_ticket_required_for_mitigation"]=False
    o["trained_responders"]=4
    o["runbook_validated_by_non_author"]=True
    write("ownership-evidence.json",o)

    t=load("toil-debt-evidence.json")
    t["intervention"]={"mechanism":"connection-lifecycle-fix","symptom_automation":False}
    t["debt"]={
      "debt_id":c["debt"]["debt_id"],
      "owner":"payments-team",
      "risk":"Recurring connection leak causes payment pages, manual restarts and reliability degradation.",
      "interest_metric":"manual-hours-and-recurring-pages-per-week",
      "review_date":"2026-11-01",
      "exit_condition":"28-day effectiveness review meets toil/page/reliability targets",
      "status":"closed-after-effectiveness-review"
    }
    write("toil-debt-evidence.json",t)

    i=load("improvement-evidence.json")
    i["baseline"]={"window_days":28,"manual_hours_per_week":10.0,"recurring_pages_per_week":12,"payment_success_rate":0.992}
    i["hypothesis"]="The connection leak causes recurring pages and manual restarts; fixing connection lifecycle will remove that mechanism without degrading payment success."
    i["guardrails_defined"]=True
    i["action"]={"owner":"payments-team","deadline":"2026-10-04","mechanism":"connection-lifecycle-fix"}
    i["evaluation"]={"window_days":28,"manual_hours_per_week":0.5,"recurring_pages_per_week":1,"payment_success_rate":0.9995}
    i["standardization"]=c["improvement"]["required_standardization"]
    i["effectiveness_review"]=True
    write("improvement-evidence.json",i)

    s=load("second-operation.json")
    s["same_subject"]=True
    s["evidence_mutations"]=0
    s["report_byte_identical"]=True
    write("second-operation.json",s)

restore(); reject("canonical reduced-clicks incident")
print("PASS reduced clicks do not prove ownership or continuous improvement")

restore(); healthy(); o=load("ownership-evidence.json"); o["primary_incident_owner"]="operations"; write("ownership-evidence.json",o); reject("handoff ownership")
print("PASS service outcome cannot be handed off to central operations")

restore(); healthy(); o=load("ownership-evidence.json"); o["decision_rights"]=["view-dashboard"]; write("ownership-evidence.json",o); reject("ownership without authority")
print("PASS ownership requires bounded decision rights")

restore(); healthy(); o=load("ownership-evidence.json"); o["trained_responders"]=1; o["runbook_validated_by_non_author"]=False; write("ownership-evidence.json",o); reject("hero ownership")
print("PASS hero-only recovery does not satisfy collective ownership")

restore(); healthy(); t=load("toil-debt-evidence.json"); t["intervention"]={"mechanism":"cron-restart","symptom_automation":True}; write("toil-debt-evidence.json",t); reject("symptom automation")
print("PASS automating a recurring symptom is not a systemic improvement")

restore(); healthy(); t=load("toil-debt-evidence.json"); t["debt"]["owner"]=None; write("toil-debt-evidence.json",t); reject("incomplete debt lifecycle")
print("PASS technical debt requires owner/risk/interest/review/exit lifecycle")

restore(); healthy(); i=load("improvement-evidence.json"); i["evaluation"]["window_days"]=1; write("improvement-evidence.json",i); reject("short effectiveness window")
print("PASS improvement requires the contracted effectiveness window")

restore(); healthy(); i=load("improvement-evidence.json"); i["standardization"]=["runbook"]; write("improvement-evidence.json",i); reject("unstandardized learning")
print("PASS proven learning must be institutionalized")

restore(); healthy(); r=run(); assert r.returncode==0,r.stdout+r.stderr
rep=load("ownership-report.json")
assert rep["ownership_verified"] and rep["improvement_verified"] and rep["third_way_verified"]
assert rep["improvement_evidence_only"] and rep["task_done_is_not_outcome"]
rb=Path("ownership-report.json").read_bytes(); lb=Path("ownership-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode==0,r.stdout+r.stderr
assert Path("ownership-report.json").read_bytes()==rb and Path("ownership-evidence-ledger.json").read_bytes()==lb
print("PASS healthy ownership/improvement evidence is byte-idempotent")

Path("ownership-evidence-ledger.json").write_text('{"conflict":true}\n')
before=Path("ownership-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode!=0
assert Path("ownership-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable ownership evidence is preserved")

restore(); print("VALIDATION PASSED")
