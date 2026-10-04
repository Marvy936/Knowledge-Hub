#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

FILES=["isolation-contract.json","isolation-evidence.json","cgroup-evidence.json","capability-evidence.json","operation-evidence.json","second-operation.json"]
OUT=["isolation-report.json","isolation-evidence-ledger.json"]
BASE={n:Path(n).read_text() for n in FILES}
GATE=Path("isolation_gate.py").read_text()

def load(p): return json.loads(Path(p).read_text())
def write(p,o): Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
def restore():
    for n,t in BASE.items(): Path(n).write_text(t)
    for n in OUT: Path(n).unlink(missing_ok=True)
    Path("isolation_gate.py").write_text(GATE)
def run(): return subprocess.run([sys.executable,"./isolation_gate.py"],text=True,capture_output=True)
def reject(label):
    r=run()
    assert r.returncode!=0,label+" unexpectedly passed\n"+r.stdout+r.stderr
    assert not Path("isolation-evidence-ledger.json").exists(),label+" wrote ledger"

def healthy():
    c=load("isolation-contract.json")
    i=load("isolation-evidence.json")
    i["inside_pid"]=c["namespaces"]["pid_inside"]
    i["uid_mapping"]={"inside_uid":c["namespaces"]["user_uid_inside"],"host_uid":c["namespaces"]["user_uid_host"]}
    i["namespaces"]["workload"]={
      "pid":"pid:[4026533101]","mnt":"mnt:[4026533102]","net":"net:[4026533103]",
      "uts":"uts:[4026533104]","ipc":"ipc:[4026533105]","user":"user:[4026533106]"
    }
    write("isolation-evidence.json",i)

    g=load("cgroup-evidence.json")
    g.update({"version":2,"path":c["cgroup"]["path"],"cpu_max":c["cgroup"]["cpu_max"],
              "memory_max":c["cgroup"]["memory_max"],"memory_current":268435456,
              "pids_max":c["cgroup"]["pids_max"],"pids_current":37,"memory_events":{"oom":0}})
    write("cgroup-evidence.json",g)

    caps=load("capability-evidence.json")
    caps.update({"effective":["CAP_NET_BIND_SERVICE"],"permitted":["CAP_NET_BIND_SERVICE"],
                 "bounding":["CAP_NET_BIND_SERVICE"],"ambient":[],"no_new_privs":True})
    write("capability-evidence.json",caps)

    ops=load("operation-evidence.json")
    ops["allowed"]["bind_port_443"]["result"]="success"
    for name in ops["forbidden"]: ops["forbidden"][name]["result"]="denied"
    write("operation-evidence.json",ops)

    s=load("second-operation.json")
    s.update({"same_subject":True,"evidence_mutations":0,"report_byte_identical":True})
    write("second-operation.json",s)

restore(); reject("canonical label-only isolation incident")
print("PASS container label and namespace-root UID cannot prove isolation")

restore(); healthy(); i=load("isolation-evidence.json"); i["namespaces"]["workload"]["net"]=i["namespaces"]["host"]["net"]; write("isolation-evidence.json",i); reject("shared net namespace")
print("PASS required namespace cannot be shared with host")

restore(); healthy(); i=load("isolation-evidence.json"); i["uid_mapping"]["host_uid"]=0; write("isolation-evidence.json",i); reject("host root mapping")
print("PASS namespace root must map to non-root host identity")

restore(); healthy(); g=load("cgroup-evidence.json"); g["memory_max"]="max"; write("cgroup-evidence.json",g); reject("unbounded memory")
print("PASS effective cgroup memory limit is required")

restore(); healthy(); g=load("cgroup-evidence.json"); g["pids_current"]=128; write("cgroup-evidence.json",g); reject("pids saturation")
print("PASS resource acceptance checks effective usage against pids limit")

restore(); healthy(); caps=load("capability-evidence.json"); caps["effective"].append("CAP_SYS_ADMIN"); caps["bounding"].append("CAP_SYS_ADMIN"); write("capability-evidence.json",caps); reject("broad capability")
print("PASS broad effective/bounding capability is blocked")

restore(); healthy(); caps=load("capability-evidence.json"); caps["no_new_privs"]=False; write("capability-evidence.json",caps); reject("new privilege allowed")
print("PASS no_new_privs boundary is required")

restore(); healthy(); ops=load("operation-evidence.json"); ops["forbidden"]["ptrace_host_process"]["result"]="success"; write("operation-evidence.json",ops); reject("host ptrace")
print("PASS forbidden adjacent privileged operation must be denied")

restore(); healthy(); s=load("second-operation.json"); s["evidence_mutations"]=1; write("second-operation.json",s); reject("mutating replay")
print("PASS repeated isolation assessment must not mutate evidence")

restore(); healthy(); r=run(); assert r.returncode==0,r.stdout+r.stderr
rep=load("isolation-report.json")
assert rep["isolation_verified"] and rep["namespace_boundary_verified"] and rep["cgroup_boundary_verified"] and rep["least_privilege_verified"]
assert rep["shared_kernel"] is True and rep["container_label_is_evidence_only"] is True
rb=Path("isolation-report.json").read_bytes(); lb=Path("isolation-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode==0,r.stdout+r.stderr
assert Path("isolation-report.json").read_bytes()==rb and Path("isolation-evidence-ledger.json").read_bytes()==lb
print("PASS healthy isolation evidence is byte-idempotent")

Path("isolation-evidence-ledger.json").write_text('{"conflict":true}\n')
before=Path("isolation-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode!=0
assert Path("isolation-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable isolation evidence is preserved")

restore(); print("VALIDATION PASSED")
