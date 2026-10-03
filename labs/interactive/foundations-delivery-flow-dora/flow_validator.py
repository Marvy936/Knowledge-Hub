#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

FILES=["flow-contract.json","change-events.json","metric-claims.json","value-stream.json","second-operation.json"]
OUT=["flow-report.json","flow-evidence-ledger.json"]
BASE={n:Path(n).read_text() for n in FILES}
GATE=Path("flow_gate.py").read_text()

def load(p): return json.loads(Path(p).read_text())
def write(p,o): Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
def restore():
    for n,t in BASE.items(): Path(n).write_text(t)
    for n in OUT: Path(n).unlink(missing_ok=True)
    Path("flow_gate.py").write_text(GATE)
def run(): return subprocess.run([sys.executable,"./flow_gate.py"],text=True,capture_output=True)
def reject(label):
    r=run()
    assert r.returncode!=0,label+" unexpectedly passed"
    assert not Path("flow-evidence-ledger.json").exists(),label+" wrote ledger"
def healthy():
    claims=load("metric-claims.json")
    claims.update({
      "deployment_frequency_per_day":8/7,
      "lead_time_for_changes_hours":2.5,
      "change_failure_rate_pct":25.0,
      "time_to_restore_hours":1.25,
      "denominator":"production_deployments",
      "measurement_source":"production-change-event-log"
    })
    write("metric-claims.json",claims)
    flow=load("value-stream.json")
    flow["claimed_bottleneck"]="review"
    flow["claimed_process_efficiency_pct"]=100.0*14.0/53.0
    write("value-stream.json",flow)
    second=load("second-operation.json")
    second["same_subject"]=True
    second["evidence_mutations"]=0
    second["report_byte_identical"]=True
    write("second-operation.json",second)

restore(); reject("canonical dashboard-proxy incident")
print("PASS dashboard proxies cannot substitute for production DORA evidence")

restore(); healthy(); c=load("metric-claims.json"); c["denominator"]="ci_jobs"; write("metric-claims.json",c); reject("CI denominator")
print("PASS deployment frequency/change failure metrics require production-deployment denominator")

restore(); healthy(); e=load("change-events.json"); e["changes"].append(dict(e["changes"][0])); write("change-events.json",e); reject("duplicate change")
print("PASS duplicate change identity is blocked")

restore(); healthy(); c=load("metric-claims.json"); c["lead_time_for_changes_hours"]=0.3; write("metric-claims.json",c); reject("pipeline-end lead time")
print("PASS lead time must end at production exposure, not pipeline completion")

restore(); healthy(); c=load("metric-claims.json"); c["change_failure_rate_pct"]=0.0; write("metric-claims.json",c); reject("excluded failures")
print("PASS rollback/incident outcomes remain in change-failure denominator")

restore(); healthy(); c=load("metric-claims.json"); c["time_to_restore_hours"]=0.291667; write("metric-claims.json",c); reject("service-green restore proxy")
print("PASS restore time must reach business recovery, not merely service green")

restore(); healthy(); f=load("value-stream.json"); f["claimed_bottleneck"]="implementation"; write("value-stream.json",f); reject("active-work bottleneck proxy")
print("PASS value-stream bottleneck follows wait time rather than longest active work")

restore(); healthy(); s=load("second-operation.json"); s["evidence_mutations"]=1; write("second-operation.json",s); reject("mutating replay")
print("PASS repeated measurement must be a no-mutation identical-subject operation")

restore(); healthy(); r=run(); assert r.returncode==0,r.stdout+r.stderr
rep=load("flow-report.json")
assert rep["flow_verified"] and rep["optimization_authorized"] is False
assert rep["metrics"]["deployment_frequency_per_day"]==round(8/7,6)
assert rep["metrics"]["lead_time_for_changes_hours"]==2.5
assert rep["metrics"]["change_failure_rate_pct"]==25.0
assert rep["metrics"]["time_to_restore_hours"]==1.25
assert rep["value_stream"]["bottleneck"]=="review"
rb=Path("flow-report.json").read_bytes(); lb=Path("flow-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode==0,r.stdout+r.stderr
assert Path("flow-report.json").read_bytes()==rb and Path("flow-evidence-ledger.json").read_bytes()==lb
print("PASS healthy flow/DORA measurement is byte-idempotent")

Path("flow-evidence-ledger.json").write_text('{"conflict":true}\n')
before=Path("flow-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode!=0
assert Path("flow-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable flow evidence is preserved")

restore(); print("VALIDATION PASSED")
