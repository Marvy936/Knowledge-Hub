#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

FILES=["linux-backup-contract.json","filesystem-evidence.json","service-evidence.json","journal-evidence.json","backup-outcome.json","second-operation.json"]
OUT=["linux-backup-report.json","linux-backup-evidence-ledger.json"]
BASE={n:Path(n).read_text() for n in FILES}
GATE=Path("linux_backup_gate.py").read_text()

def load(p): return json.loads(Path(p).read_text())
def write(p,o): Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
def restore():
    for n,t in BASE.items(): Path(n).write_text(t)
    for n in OUT: Path(n).unlink(missing_ok=True)
    Path("linux_backup_gate.py").write_text(GATE)
def run(): return subprocess.run([sys.executable,"./linux_backup_gate.py"],text=True,capture_output=True)
def reject(label):
    r=run()
    assert r.returncode!=0,label+" unexpectedly passed\n"+r.stdout+r.stderr
    assert not Path("linux-backup-evidence-ledger.json").exists(),label+" wrote ledger"
def healthy():
    c=load("linux-backup-contract.json")
    fs=load("filesystem-evidence.json")
    fs.update({"mount_source":c["filesystem"]["mount_source"],"fs_type":c["filesystem"]["fs_type"],"mount_options":["rw","relatime"],"writable":True,"deleted_open":[],"df_used_pct":41,"du_visible_used_pct":40})
    fs["target"]={"path":c["filesystem"]["target_path"],"exists":True,"inode":7711}
    fs["symlink"]={"path":"/var/lib/backup/current","target":"snapshot-2026-10-03.tar","dangling":False}
    fs["hardlink"]={"path":"/var/lib/backup/latest.tar","inode":7711,"link_count":2,"same_inode_as_target":True}
    write("filesystem-evidence.json",fs)

    svc=load("service-evidence.json")
    svc.update({"unit":c["service"]["unit"],"unit_type":c["service"]["type"],"user":c["service"]["user"],"result":c["service"]["result"],"exec_main_status":c["service"]["exec_main_status"],"cgroup_cleanup_complete":True})
    write("service-evidence.json",svc)

    j=load("journal-evidence.json")
    j["query_unit"]=c["logging"]["journal_unit"]
    j["entries"]=[
      {"message":"starting backup run backup:2026-10-03","priority":6,"run_id":c["logging"]["run_id"],"unit":c["logging"]["journal_unit"]},
      {"message":c["logging"]["completion_event"],"priority":6,"run_id":c["logging"]["run_id"],"unit":c["logging"]["journal_unit"]}
    ]
    write("journal-evidence.json",j)

    o=load("backup-outcome.json")
    o["artifact"]={"path":c["filesystem"]["target_path"],"exists":True,"sha256":c["outcome"]["artifact_sha256"],"manifest_entries":c["outcome"]["manifest_entries"]}
    o["remote_verified"]=True
    o["run_id"]=c["logging"]["run_id"]
    write("backup-outcome.json",o)

    s=load("second-operation.json")
    s.update({"same_run_id":True,"duplicate_artifacts":0,"report_byte_identical":True})
    write("second-operation.json",s)

restore(); reject("canonical timer-is-green incident")
print("PASS active timer cannot substitute for successful service and backup outcome")

restore(); healthy(); fs=load("filesystem-evidence.json"); fs["mount_source"]="/dev/mapper/vg-root"; fs["fs_type"]="ext4"; write("filesystem-evidence.json",fs); reject("wrong mount")
print("PASS target pathname must resolve to the exact storage mount")

restore(); healthy(); fs=load("filesystem-evidence.json"); fs["deleted_open"]=[{"pid":4242,"process":"compressor","inode":9021,"path":"/var/lib/backup/tmp/archive.partial (deleted)","bytes":8589934592}]; write("filesystem-evidence.json",fs); reject("deleted-open inode")
print("PASS deleted-open inode consumption is detected despite pathname deletion")

restore(); healthy(); fs=load("filesystem-evidence.json"); fs["symlink"]["dangling"]=True; fs["symlink"]["target"]="snapshot-latest.tar"; write("filesystem-evidence.json",fs); reject("dangling symlink")
print("PASS dangling current symlink is blocked")

restore(); healthy(); fs=load("filesystem-evidence.json"); fs["hardlink"]["inode"]=7712; fs["hardlink"]["same_inode_as_target"]=False; write("filesystem-evidence.json",fs); reject("hard-link mismatch")
print("PASS hard-link evidence must refer to the same inode")

restore(); healthy(); svc=load("service-evidence.json"); svc["result"]="exit-code"; svc["exec_main_status"]=1; write("service-evidence.json",svc); reject("failed service")
print("PASS timer activation is separated from service execution result")

restore(); healthy(); j=load("journal-evidence.json"); j["query_unit"]="backup.timer"; write("journal-evidence.json",j); reject("wrong journal scope")
print("PASS journal evidence must be scoped to the executing service")

restore(); healthy(); o=load("backup-outcome.json"); o["remote_verified"]=False; write("backup-outcome.json",o); reject("unverified backup")
print("PASS exit zero cannot replace durable remote backup verification")

restore(); healthy(); s=load("second-operation.json"); s["duplicate_artifacts"]=1; write("second-operation.json",s); reject("duplicate replay")
print("PASS identical logical run cannot create a duplicate artifact")

restore(); healthy(); r=run(); assert r.returncode==0,r.stdout+r.stderr
rep=load("linux-backup-report.json")
assert rep["backup_verified"] and rep["timer_active_is_evidence_only"] and rep["service_exit_zero_is_evidence_only"]
rb=Path("linux-backup-report.json").read_bytes(); lb=Path("linux-backup-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode==0,r.stdout+r.stderr
assert Path("linux-backup-report.json").read_bytes()==rb and Path("linux-backup-evidence-ledger.json").read_bytes()==lb
print("PASS healthy Linux backup evidence is byte-idempotent")

Path("linux-backup-evidence-ledger.json").write_text('{"conflict":true}\n')
before=Path("linux-backup-evidence-ledger.json").read_bytes()
r=run(); assert r.returncode!=0
assert Path("linux-backup-evidence-ledger.json").read_bytes()==before
print("PASS conflicting durable Linux backup evidence is preserved")

restore(); print("VALIDATION PASSED")
