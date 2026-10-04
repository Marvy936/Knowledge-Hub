#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

FILES=["access-contract.json","network-evidence.json","ssh-evidence.json","authz-evidence.json","mac-evidence.json","verification-evidence.json","second-operation.json"]
OUT=["access-report.json","access-evidence-ledger.json"]
BASE={n:Path(n).read_text() for n in FILES}
GATE=Path("access_gate.py").read_text()

def load(p): return json.loads(Path(p).read_text())
def write(p,o): Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
def restore():
    for n,t in BASE.items(): Path(n).write_text(t)
    for n in OUT: Path(n).unlink(missing_ok=True)
    Path("access_gate.py").write_text(GATE)
def run(): return subprocess.run([sys.executable,"./access_gate.py"],text=True,capture_output=True)
def reject(label):
    r=run(); assert r.returncode!=0,label+" unexpectedly passed\n"+r.stdout+r.stderr
    assert not Path("access-evidence-ledger.json").exists(),label+" wrote ledger"
def healthy():
    c=load("access-contract.json")
    n=load("network-evidence.json")
    n.update({"namespace":c["network"]["namespace"],"resolved_name":c["network"]["destination_name"],"resolved_ip":c["network"]["destination_ip"],"source_ip":c["network"]["source_ip"],"route_via":c["network"]["route_via"],"output_interface":c["network"]["output_interface"],"destination_port":c["network"]["destination_port"],"listener":c["network"]["listener"],"return_path_verified":True}); write("network-evidence.json",n)
    s=load("ssh-evidence.json")
    s.update({"host":c["ssh"]["host"],"user":c["ssh"]["user"],"authentication":c["ssh"]["authentication"],"observed_host_key_fingerprint":c["ssh"]["host_key_fingerprint"],"strict_host_key_checking":True,"agent_forwarding":False,"tcp_forwarding":False,"pty":False,"authorized_key_restricted":True}); write("ssh-evidence.json",s)
    a=load("authz-evidence.json"); a.update({"groups":c["authorization"]["required_groups"],"pam_account_allowed":True,"sudo_commands":c["authorization"]["sudo_commands"],"forbidden_sudo_allowed":False}); write("authz-evidence.json",a)
    m=load("mac-evidence.json"); m.update({"framework":c["mac"]["framework"],"mode":c["mac"]["mode"],"process_domain":c["mac"]["process_domain"],"config_path":c["mac"]["config_path"],"config_type":c["mac"]["config_type"],"policy_generation":c["mac"]["policy_generation"],"expected_type_mapping_persistent":True,"denial_preserved":True,"temporary_chcon_only":False}); write("mac-evidence.json",m)
    v=load("verification-evidence.json"); v["allowed_flow"]=c["verification"]["allowed_flow"]; v["allowed_flow_succeeded"]=True; v["forbidden_results"]={x:False for x in c["verification"]["forbidden_flows"]}; write("verification-evidence.json",v)
    z=load("second-operation.json"); z.update({"same_subject":True,"mutations":0,"report_byte_identical":True}); write("second-operation.json",z)

restore(); reject("canonical reachability-is-trust incident")
print("PASS reachability and SSH login alone cannot prove a safe access path")
restore(); healthy(); n=load("network-evidence.json"); n["route_via"]="10.20.10.254"; write("network-evidence.json",n); reject("wrong route")
print("PASS exact route/source/interface tuple is required")
restore(); healthy(); s=load("ssh-evidence.json"); s["strict_host_key_checking"]=False; write("ssh-evidence.json",s); reject("disabled host trust")
print("PASS strict SSH host identity verification is required")
restore(); healthy(); s=load("ssh-evidence.json"); s["agent_forwarding"]=True; write("ssh-evidence.json",s); reject("agent forwarding")
print("PASS unnecessary SSH forwarding capability is blocked")
restore(); healthy(); a=load("authz-evidence.json"); a["sudo_commands"]=["ALL"]; a["forbidden_sudo_allowed"]=True; write("authz-evidence.json",a); reject("broad sudo")
print("PASS sudo scope must remain command-bounded")
restore(); healthy(); m=load("mac-evidence.json"); m["mode"]="permissive"; write("mac-evidence.json",m); reject("permissive SELinux")
print("PASS MAC enforcement cannot be disabled as remediation")
restore(); healthy(); m=load("mac-evidence.json"); m["expected_type_mapping_persistent"]=False; m["temporary_chcon_only"]=True; write("mac-evidence.json",m); reject("temporary label fix")
print("PASS persistent MAC labeling is required")
restore(); healthy(); v=load("verification-evidence.json"); v["forbidden_results"]["arbitrary-root-shell"]=True; write("verification-evidence.json",v); reject("adjacent privilege")
print("PASS allowed flow must coexist with denied adjacent privilege")
restore(); healthy(); r=run(); assert r.returncode==0,r.stdout+r.stderr
rep=load("access-report.json"); assert rep["security_verified"] and rep["network_path_verified"] and rep["ssh_trust_verified"] and rep["authorization_verified"] and rep["mac_verified"]
rb=Path("access-report.json").read_bytes(); lb=Path("access-evidence-ledger.json").read_bytes(); r=run(); assert r.returncode==0; assert Path("access-report.json").read_bytes()==rb and Path("access-evidence-ledger.json").read_bytes()==lb
print("PASS healthy access evidence is byte-idempotent")
Path("access-evidence-ledger.json").write_text('{"conflict":true}\n'); before=Path("access-evidence-ledger.json").read_bytes(); r=run(); assert r.returncode!=0; assert Path("access-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable access evidence is preserved")
restore(); print("VALIDATION PASSED")
