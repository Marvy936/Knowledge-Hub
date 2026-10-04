#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

FILES=["execution-contract.json","cron-evidence.json","package-evidence.json","filesystem-evidence.json","execution-evidence.json","shell-evidence.json","outcome-evidence.json","second-operation.json"]
OUT=["execution-report.json","execution-evidence-ledger.json"]
BASE={n:Path(n).read_text() for n in FILES}
GATE=Path("execution_gate.py").read_text()

def load(p): return json.loads(Path(p).read_text())
def write(p,o): Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
def restore():
    for n,t in BASE.items(): Path(n).write_text(t)
    for n in OUT: Path(n).unlink(missing_ok=True)
    Path("execution_gate.py").write_text(GATE)
def run(): return subprocess.run([sys.executable,"./execution_gate.py"],text=True,capture_output=True)
def reject(label):
    r=run()
    assert r.returncode!=0,label+" unexpectedly passed\n"+r.stdout+r.stderr
    assert not Path("execution-evidence-ledger.json").exists(),label+" wrote ledger"

def healthy():
    c=load("execution-contract.json")
    cron=load("cron-evidence.json")
    cron.update(c["cron"]); cron["observed_runtime"]="cron"; cron["triggered"]=True
    write("cron-evidence.json",cron)

    pkg=load("package-evidence.json")
    pkg.update(c["package"]); pkg.update({"metadata_fresh":True,"signature_verified":True,"dependency_transaction_complete":True,"local_database_consistent":True,"loaded_version":c["package"]["installed_version"]})
    write("package-evidence.json",pkg)

    fs=load("filesystem-evidence.json")
    fs.update(c["filesystem"]); fs.update({"launcher_type":"symlink","package_owns_target":True,"mount":"/usr"})
    write("filesystem-evidence.json",fs)

    exe=load("execution-evidence.json")
    exe.update({"job_pid":c["execution"]["job_pid"],"job_parent":"cron","exec_pid_before":c["execution"]["exec_pid"],"exec_pid_after":c["execution"]["exec_pid"],"exec_start_time_ticks_before":c["execution"]["exec_start_time_ticks"],"exec_start_time_ticks_after":c["execution"]["exec_start_time_ticks"]})
    exe["environment"]={"APP_ENV":c["execution"]["app_env"],"PATH":c["cron"]["path"]}
    exe["syscall"]={"name":"execve","path":c["package"]["payload_path"],"result":0,"errno":None}
    write("execution-evidence.json",exe)

    sh=load("shell-evidence.json")
    sh.update(c["shell"]); sh.update({"interpreter":c["cron"]["shell"],"report_argument_count":3,"quoted_argument_count":3,"atomic_output":True})
    write("shell-evidence.json",sh)

    out=load("outcome-evidence.json")
    out.update(c["outcome"]); out["durable"]=True
    write("outcome-evidence.json",out)

    second=load("second-operation.json")
    second.update(c["second_operation"])
    write("second-operation.json",second)

restore(); reject("interactive-shell package check")
print("PASS cron trigger plus installed package is not runtime success")

restore(); healthy(); cron=load("cron-evidence.json"); cron["path"]="/usr/local/bin:/usr/bin:/bin"; write("cron-evidence.json",cron); reject("interactive PATH")
print("PASS scheduler environment must be exact")

restore(); healthy(); pkg=load("package-evidence.json"); pkg["signature_verified"]=False; write("package-evidence.json",pkg); reject("unsigned package evidence")
print("PASS package transaction requires repository trust")

restore(); healthy(); pkg=load("package-evidence.json"); pkg["loaded_version"]="2.3.9-1"; write("package-evidence.json",pkg); reject("stale loaded binary")
print("PASS installed version is not loaded-version proof")

restore(); healthy(); fs=load("filesystem-evidence.json"); fs["resolved_target"]="/usr/local/bin/report-cli-2.3"; fs["package_owns_target"]=False; write("filesystem-evidence.json",fs); reject("stale symlink")
print("PASS pathname must resolve to exact package-owned object")

restore(); healthy(); exe=load("execution-evidence.json"); exe["exec_pid_after"]=39999; write("execution-evidence.json",exe); reject("exec changed PID")
print("PASS execve replaces program without changing process identity")

restore(); healthy(); exe=load("execution-evidence.json"); exe["syscall"]["result"]=-1; exe["syscall"]["errno"]="ENOENT"; write("execution-evidence.json",exe); reject("execve ENOENT")
print("PASS kernel syscall result must be checked")

restore(); healthy(); sh=load("shell-evidence.json"); sh["report_exit"]=1; sh["logger_exit"]=0; sh["job_exit"]=0; write("shell-evidence.json",sh); reject("masked pipeline failure")
print("PASS logging success cannot mask producer failure")

restore(); healthy(); sh=load("shell-evidence.json"); sh["quoted_argument_count"]=2; write("shell-evidence.json",sh); reject("word splitting")
print("PASS shell quoting must preserve the argument vector")

restore(); healthy(); out=load("outcome-evidence.json"); out["durable"]=False; write("outcome-evidence.json",out); reject("non-durable outcome")
print("PASS scheduler success requires durable business outcome")

restore(); healthy(); second=load("second-operation.json"); second["duplicate_reports"]=1; write("second-operation.json",second); reject("duplicate replay")
print("PASS repeated cron operation must remain duplicate-free")

restore(); healthy(); r=run(); assert r.returncode==0,r.stdout+r.stderr
rep=load("execution-report.json")
for key in ("cron_runtime_verified","environment_verified","package_transaction_verified","filesystem_identity_verified","process_exec_verified","kernel_transition_verified","shell_semantics_verified","durable_outcome_verified","replay_verified"):
    assert rep[key] is True,key
rb=Path("execution-report.json").read_bytes(); lb=Path("execution-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode==0,r.stdout+r.stderr
assert Path("execution-report.json").read_bytes()==rb and Path("execution-evidence-ledger.json").read_bytes()==lb
print("PASS healthy scheduled execution is byte-idempotent")

Path("execution-evidence-ledger.json").write_text('{"conflict":true}\n')
before=Path("execution-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode!=0
assert Path("execution-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable execution evidence is preserved")

restore(); print("VALIDATION PASSED")
