#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

FILES=["resource-contract.json","symptom-evidence.json","scope-evidence.json","cpu-evidence.json","memory-evidence.json","repair-evidence.json","second-operation.json"]
OUT=["resource-report.json","resource-evidence-ledger.json"]
BASE={n:Path(n).read_text() for n in FILES}
GATE=Path("resource_gate.py").read_text()

def load(p): return json.loads(Path(p).read_text())
def write(p,o): Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
def restore():
    for n,t in BASE.items(): Path(n).write_text(t)
    for n in OUT: Path(n).unlink(missing_ok=True)
    Path("resource_gate.py").write_text(GATE)
def run(): return subprocess.run([sys.executable,"./resource_gate.py"],text=True,capture_output=True)
def reject(label):
    r=run()
    assert r.returncode!=0,label+" unexpectedly passed\n"+r.stdout+r.stderr
    assert not Path("resource-evidence-ledger.json").exists(),label+" wrote ledger"

def healthy():
    c=load("resource-contract.json")
    s=load("scope-evidence.json")
    s.update({"host":c["scope"]["host"],"cgroup":c["scope"]["cgroup"],"pid":c["scope"]["pid"],"scope_used_for_diagnosis":"cgroup-process"})
    write("scope-evidence.json",s)

    cpu=load("cpu-evidence.json")
    cpu.update({"host_cpu_utilization":38.0,"cgroup_cpu_max":c["scope"]["cpu_max_before"],"diagnosed_root_cause":c["acceptance"]["root_cause"]})
    write("cpu-evidence.json",cpu)

    mem=load("memory-evidence.json")
    mem["diagnosed_pressure"]="none"
    write("memory-evidence.json",mem)

    rep=load("repair-evidence.json")
    rep.update({
      "change_scope":"cgroup","cpu_max_after":c["scope"]["cpu_max_after"],
      "p99_ms_after":320,"error_rate_after":0.004,
      "throughput_per_second_before":405,"throughput_per_second_after":438,
      "cpu_throttle_ratio_after":0.01,"cpu_psi_some_avg10_after":1.1,
      "memory_current_after":671088640,"memory_psi_some_avg10_after":0.2,
      "major_faults_per_second_after":0.1,"oom_kill_after":0,"adjacent_mutations":[]
    })
    write("repair-evidence.json",rep)

    second=load("second-operation.json")
    second.update({"same_subject":True,"evidence_mutations":0,"report_byte_identical":True})
    write("second-operation.json",second)

restore(); reject("canonical host-snapshot diagnosis")
print("PASS host CPU and low MemFree alone cannot authorize a repair")

restore(); healthy(); s=load("scope-evidence.json"); s["scope_used_for_diagnosis"]="host"; write("scope-evidence.json",s); reject("host-only scope")
print("PASS diagnosis must bind host to cgroup and process scope")

restore(); healthy(); cpu=load("cpu-evidence.json"); cpu["cgroup_cpu_max"]="max 100000"; write("cpu-evidence.json",cpu); reject("unbounded pre-repair CPU")
print("PASS effective workload CPU quota must be observed")

restore(); healthy(); cpu=load("cpu-evidence.json"); cpu["nr_throttled_delta"]=0; cpu["throttled_usec_delta"]=0; write("cpu-evidence.json",cpu); reject("no CPU throttling")
print("PASS CPU root cause requires throttling evidence")

restore(); healthy(); mem=load("memory-evidence.json"); mem["diagnosed_pressure"]="host_low_free_memory"; write("memory-evidence.json",mem); reject("false memory root cause")
print("PASS low MemFree cannot override healthy MemAvailable and cgroup memory evidence")

restore(); healthy(); mem=load("memory-evidence.json"); mem["cgroup_memory_current"]=mem["cgroup_memory_high"]; write("memory-evidence.json",mem); reject("memory headroom exhausted")
print("PASS memory headroom must remain healthy")

restore(); healthy(); rep=load("repair-evidence.json"); rep["cpu_max_after"]="max 100000"; write("repair-evidence.json",rep); reject("unbounded repair")
print("PASS repair cannot disable the workload CPU boundary")

restore(); healthy(); rep=load("repair-evidence.json"); rep["p99_ms_after"]=700; write("repair-evidence.json",rep); reject("latency not recovered")
print("PASS repair must recover the user-visible p99 outcome")

restore(); healthy(); rep=load("repair-evidence.json"); rep["adjacent_mutations"]=["disable_cgroup_limits"]; write("repair-evidence.json",rep); reject("adjacent broad mutation")
print("PASS adjacent broad resource mutations are forbidden")

restore(); healthy(); second=load("second-operation.json"); second["evidence_mutations"]=1; write("second-operation.json",second); reject("mutating replay")
print("PASS repeated diagnosis must not mutate evidence")

restore(); healthy(); r=run(); assert r.returncode==0,r.stdout+r.stderr
rep=load("resource-report.json")
assert rep["resource_issue_verified"] and rep["cpu_saturation_verified"] and rep["memory_pressure_refuted"]
assert rep["repair_verified"] and rep["user_outcome_verified"] and rep["adjacent_safety_verified"]
rb=Path("resource-report.json").read_bytes(); lb=Path("resource-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode==0,r.stdout+r.stderr
assert Path("resource-report.json").read_bytes()==rb and Path("resource-evidence-ledger.json").read_bytes()==lb
print("PASS healthy resource diagnosis is byte-idempotent")

Path("resource-evidence-ledger.json").write_text('{"conflict":true}\n')
before=Path("resource-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode!=0
assert Path("resource-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable resource evidence is preserved")

restore(); print("VALIDATION PASSED")
