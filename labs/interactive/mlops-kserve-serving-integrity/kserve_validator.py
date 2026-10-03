#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

FILES=["kserve-contract.json","inferenceservice-evidence.json","runtime-evidence.json","fleet-evidence.json","traffic-evidence.json","rollback-evidence.json","second-operation.json"]
OUT=["kserve-report.json","kserve-evidence-ledger.json"]
BASE={n:Path(n).read_text() for n in FILES}

def load(p): return json.loads(Path(p).read_text())
def write(p,o): Path(p).write_text(json.dumps(o,indent=2)+"\n")
def restore():
    for n,t in BASE.items(): Path(n).write_text(t)
    for n in OUT: Path(n).unlink(missing_ok=True)
def run(): return subprocess.run([sys.executable,"./kserve_gate.py"],text=True,capture_output=True)
def reject(label):
    r=run()
    assert r.returncode!=0,label+" unexpectedly passed"
    assert not Path("kserve-evidence-ledger.json").exists(),label+" wrote ledger"

def healthy():
    c=load("kserve-contract.json")
    i=load("inferenceservice-evidence.json")
    i["knative_annotations_present"]=False
    i["runtime_generation"]=c["release"]["runtime_generation"]
    i["model_uri"]=c["storage"]["model_uri"]
    i["storage_immutable"]=True
    i["storage_manifest_digest"]=c["storage"]["manifest_digest"]
    write("inferenceservice-evidence.json",i)

    r=load("runtime-evidence.json")
    r["generation"]=c["release"]["runtime_generation"]
    write("runtime-evidence.json",r)

    f=load("fleet-evidence.json")
    for p in f["replicas"]:
        p["warmup_complete"]=True
        p["release_id"]=c["release"]["release_id"]
        p["model_digest"]=c["release"]["model_digest"]
        p["runtime_generation"]=c["release"]["runtime_generation"]
    write("fleet-evidence.json",f)

    t=load("traffic-evidence.json")
    t["actual_exposure_reconciled"]=True
    t["configured_percent_used_as_denominator"]=False
    t["autoscaling_policy_generation"]=c["autoscaling"]["policy_generation"]
    t["autoscaling_metric"]=c["autoscaling"]["metric"]
    t["autoscaling_target"]=c["autoscaling"]["target"]
    write("traffic-evidence.json",t)

    rb=load("rollback-evidence.json")
    rb["endpoint_converged"]=True
    rb["candidate_endpoints_remaining"]=0
    rb["stale_connections"]=0
    rb["loaded_fingerprint_parity"]=True
    write("rollback-evidence.json",rb)

    s=load("second-operation.json")
    s["same_release_manifest"]=True
    s["reconciliation_noop"]=True
    s["fresh_synthetic_request"]=True
    s["loaded_fingerprint_parity"]=True
    s["manual_storage_edit"]=False
    write("second-operation.json",s)

restore(); reject("canonical Ready KServe incident")
print("PASS Ready/HTTP 200 cannot hide runtime, storage, fleet, routing and rollback failures")

restore(); c=load("kserve-contract.json"); c["authority"]["rollout_authorized"]=True; write("kserve-contract.json",c); reject("tampered authority")
print("PASS contract authority tampering is blocked")

restore(); healthy(); i=load("inferenceservice-evidence.json"); i["deployment_mode"]="Knative"; write("inferenceservice-evidence.json",i); reject("mode substitution")
print("PASS deployment-mode substitution is blocked")

restore(); healthy(); i=load("inferenceservice-evidence.json"); i["model_uri"]="s3://ml-models/fraud/latest/"; i["storage_immutable"]=False; write("inferenceservice-evidence.json",i); reject("mutable model storage")
print("PASS mutable model URI is blocked")

restore(); healthy(); f=load("fleet-evidence.json"); f["replicas"][1]["model_digest"]="sha256:old-model"; write("fleet-evidence.json",f); reject("mixed loaded fleet")
print("PASS mixed loaded model fingerprints are blocked")

restore(); healthy(); t=load("traffic-evidence.json"); t["configured_percent_used_as_denominator"]=True; write("traffic-evidence.json",t); reject("configured canary denominator")
print("PASS configured canary percent cannot replace actual exposure")

restore(); healthy(); rb=load("rollback-evidence.json"); rb["candidate_endpoints_remaining"]=1; write("rollback-evidence.json",rb); reject("stale rollback endpoint")
print("PASS stale candidate endpoint after rollback is blocked")

restore(); healthy(); r=run(); assert r.returncode==0,r.stdout+r.stderr
rep=load("kserve-report.json")
assert rep["kserve_integrity_verified"] and not rep["rollout_authorized"] and not rep["promotion_authorized"] and not rep["retraining_authorized"]
rb=Path("kserve-report.json").read_bytes(); lb=Path("kserve-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode==0,r.stdout+r.stderr
assert Path("kserve-report.json").read_bytes()==rb and Path("kserve-evidence-ledger.json").read_bytes()==lb
print("PASS healthy KServe subject is byte-idempotent")

Path("kserve-evidence-ledger.json").write_text('{"conflict":true}\n')
before=Path("kserve-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode!=0
assert Path("kserve-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable KServe evidence is preserved")

restore(); print("VALIDATION PASSED")
