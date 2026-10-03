#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

FILES=["architecture-contract.json","release-manifest.json","authority-map.json","system-evidence.json","event-evidence.json","recovery-evidence.json","second-operation.json"]
OUT=["architecture-report.json","architecture-evidence-ledger.json"]
BASE={name:Path(name).read_text() for name in FILES}

def load(path): return json.loads(Path(path).read_text())
def write(path,obj): Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
def restore():
    for name,text in BASE.items(): Path(name).write_text(text)
    for name in OUT: Path(name).unlink(missing_ok=True)
def run(): return subprocess.run([sys.executable,"./architecture_gate.py"],text=True,capture_output=True)
def reject(label):
    result=run()
    assert result.returncode!=0,label+" unexpectedly passed"
    assert not Path("architecture-evidence-ledger.json").exists(),label+" wrote ledger"

def healthy():
    c=load("architecture-contract.json")
    release=load("release-manifest.json")
    write("authority-map.json",c["authority"])
    systems=load("system-evidence.json")
    systems["registry"]["version"]=c["systems"]["registry_version"]
    systems["feature_store"]["materialized_generation"]=release["feature_generation"]
    systems["kserve"]["feature_generation"]=release["feature_generation"]
    systems["sagemaker"]["runtime_image_digest"]=release["runtime_image_digest"]
    systems["observability"]["correlation_key"]="release_id"
    systems["observability"]["actual_exposure_release_ids"]=[c["release_id"]]
    write("system-evidence.json",systems)
    event=load("event-evidence.json")
    event["deduplicated"]=True
    event["read_before_retry"]=True
    event["duplicate_mutation_submitted"]=False
    write("event-evidence.json",event)
    recovery=load("recovery-evidence.json")
    recovery["sagemaker_loaded_release_id"]=c["recovery"]["known_good_release_id"]
    recovery["sagemaker_runtime_image_digest"]=c["recovery"]["known_good_runtime_image_digest"]
    recovery["all_loaded_parity"]=True
    recovery["actual_traffic_converged"]=True
    recovery["failover_runtime_generation_changed"]=True
    write("recovery-evidence.json",recovery)
    second=load("second-operation.json")
    second["same_subject"]=True
    second["pure_operation_outputs_reproducible"]=True
    second["mutation_noop_or_reconciled"]=True
    second["read_before_retry"]=True
    second["duplicate_mutations"]=0
    second["loaded_fingerprint_parity"]=True
    second["manual_pointer_edit"]=False
    write("second-operation.json",second)

restore(); reject("canonical platform architecture incident")
print("PASS green subsystems cannot hide cross-system authority/lineage divergence")
restore(); healthy(); a=load("authority-map.json"); a["dashboard_is_authoritative"]=True; write("authority-map.json",a); reject("dashboard authority")
print("PASS central dashboard cannot become architectural authority")
restore(); healthy(); s=load("system-evidence.json"); s["kserve"]["feature_generation"]="fraud-features-v15"; write("system-evidence.json",s); reject("stale feature generation")
print("PASS stale KServe feature generation is blocked")
restore(); healthy(); s=load("system-evidence.json"); s["sagemaker"]["runtime_image_digest"]="sha256:old-fallback-image"; write("system-evidence.json",s); reject("fallback runtime divergence")
print("PASS cloud fallback runtime divergence is blocked")
restore(); healthy(); e=load("event-evidence.json"); e["read_before_retry"]=False; write("event-evidence.json",e); reject("blind event retry")
print("PASS unknown-outcome event mutation requires read-before-retry")
restore(); healthy(); r=load("recovery-evidence.json"); r["actual_traffic_converged"]=False; write("recovery-evidence.json",r); reject("partial recovery")
print("PASS control-pointer rollback without composite traffic convergence is blocked")
restore(); healthy(); result=run(); assert result.returncode==0,result.stdout+result.stderr
report=load("architecture-report.json")
assert report["architecture_integrity_verified"] and not report["rollout_authorized"] and not report["promotion_authorized"] and not report["retraining_authorized"]
rb=Path("architecture-report.json").read_bytes(); lb=Path("architecture-evidence-ledger.json").read_bytes()
result=run(); assert result.returncode==0,result.stdout+result.stderr
assert Path("architecture-report.json").read_bytes()==rb and Path("architecture-evidence-ledger.json").read_bytes()==lb
print("PASS healthy architecture evidence is byte-idempotent")
Path("architecture-evidence-ledger.json").write_text('{"conflict":true}\n')
before=Path("architecture-evidence-ledger.json").read_bytes()
result=run(); assert result.returncode!=0
assert Path("architecture-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable architecture evidence is preserved")
restore(); print("VALIDATION PASSED")
