#!/usr/bin/env python3
import json, shutil, subprocess, sys, tempfile
from pathlib import Path

LAB_ROOT=Path(__file__).resolve().parent
WORKSPACE=Path('/workspace')
PROTECTED=['delivery-contract.json','release-manifest.json','release-approval.json','deployment-spec.json','controller-state.json','fleet-readback.json','current-runtime.json']

def fail(message):
    print('FAIL: '+message,file=sys.stderr); raise SystemExit(1)
def load(path): return json.loads(Path(path).read_text())
def dump(path,value): Path(path).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def run_case(root):
    report=root/'delivery-report.json'; traffic=root/'traffic-change-request.json'
    cmd=['python3',str(WORKSPACE/'deliver.py'),'--contract',str(root/'delivery-contract.json'),'--release',str(root/'release-manifest.json'),
         '--approval',str(root/'release-approval.json'),'--deployment',str(root/'deployment-spec.json'),'--controller',str(root/'controller-state.json'),
         '--fleet',str(root/'fleet-readback.json'),'--current',str(root/'current-runtime.json'),'--report',str(report)]
    return subprocess.run(cmd,text=True,capture_output=True),report,traffic
def make_case():
    root=Path(tempfile.mkdtemp(prefix='kh-delivery-'))
    for name in PROTECTED: shutil.copy2(WORKSPACE/name,root/name)
    return root
def exact_instance(instance_id,release):
    return {'instance_id':instance_id,'release_subject':release['release_subject'],'model_package_digest':release['model_package_digest'],
            'serving_image':release['serving_image'],'feature_contract':release['feature_contract'],'feature_registry_digest':release['feature_registry_digest'],
            'preprocessing_digest':release['preprocessing_digest'],'policy_id':release['policy_id'],'policy_digest':release['policy_digest'],
            'inference_protocol':release['inference_protocol'],'ready':True,'request_trace_count':7}
def make_valid(root,order=None):
    release=load(root/'release-manifest.json'); fleet=load(root/'fleet-readback.json'); ids=[x['instance_id'] for x in fleet['instances']]
    fleet['instances']=[exact_instance(i,release) for i in ids]
    if order is not None: fleet['instances']=[fleet['instances'][i] for i in order]
    dump(root/'fleet-readback.json',fleet)
def expect_blocked(mutator,reason):
    root=make_case()
    try:
        mutator(root); p,report,traffic=run_case(root)
        if p.returncode!=0: fail(f'{reason}: expected zero exit, got {p.returncode}: {p.stdout} {p.stderr}')
        if not report.exists(): fail(f'{reason}: blocked report missing')
        value=load(report)
        if value.get('decision')!='blocked' or value.get('reason')!=reason: fail(f'{reason}: unexpected report {value}')
        if value.get('delivery_verified') is not False or value.get('rollout_authorized') is not False: fail(f'{reason}: blocked report grants authority')
        if traffic.exists(): fail(f'{reason}: traffic request created')
    finally: shutil.rmtree(root,ignore_errors=True)
def expect_invalid(mutator,label):
    root=make_case()
    try:
        mutator(root); p,report,traffic=run_case(root)
        if p.returncode==0: fail(f'{label}: invalid evidence returned zero')
        if report.exists(): fail(f'{label}: invalid evidence created a report')
        if traffic.exists(): fail(f'{label}: invalid evidence created a traffic request')
    finally: shutil.rmtree(root,ignore_errors=True)

for name in PROTECTED:
    src=LAB_ROOT/(name+'.template'); dst=WORKSPACE/name
    if not src.exists() or not dst.exists() or src.read_bytes()!=dst.read_bytes(): fail(f'protected canonical input changed: {name}')
(WORKSPACE/'delivery-report.json').unlink(missing_ok=True); (WORKSPACE/'traffic-change-request.json').unlink(missing_ok=True)
p,report,traffic=run_case(WORKSPACE)
if p.returncode!=0: fail(f'canonical mixed-fleet case should block with zero exit: {p.stdout} {p.stderr}')
canonical=load(report) if report.exists() else fail('canonical blocked report missing')
if canonical.get('decision')!='blocked' or canonical.get('reason')!='fleet_fingerprint_mismatch': fail(f'canonical mixed-fleet incident not detected: {canonical}')
if canonical.get('delivery_verified') is not False or canonical.get('rollout_authorized') is not False: fail('canonical block grants authority')
if traffic.exists(): fail('canonical repair created traffic-change-request.json')
root=make_case()
try:
    make_valid(root); p,report,traffic=run_case(root)
    if p.returncode!=0: fail(f'valid exact delivery failed: {p.stdout} {p.stderr}')
    value=load(report)
    if value.get('decision')!='verified' or value.get('reason')!='exact_release_loaded_everywhere': fail(f'valid delivery not verified: {value}')
    if value.get('delivery_verified') is not True or value.get('rollout_authorized') is not False: fail('valid delivery authority boundary wrong')
    if value.get('promotion_authorized') is not True or len(value.get('verified_instance_ids',[]))!=3: fail('verified report incomplete')
    if traffic.exists(): fail('valid delivery created traffic-change-request.json')
    first=report.read_bytes(); p2,report2,traffic2=run_case(root)
    if p2.returncode!=0 or report2.read_bytes()!=first: fail('exact replay is not byte-idempotent')
    if traffic2.exists(): fail('replay created traffic-change-request.json')
finally: shutil.rmtree(root,ignore_errors=True)
for order in ([2,0,1],[1,2,0]):
    root=make_case()
    try:
        make_valid(root,order); p,report,traffic=run_case(root)
        if p.returncode!=0 or load(report).get('decision')!='verified': fail('shuffled complete fleet did not verify')
        if traffic.exists(): fail('shuffled fleet created traffic-change-request.json')
    finally: shutil.rmtree(root,ignore_errors=True)
expect_blocked(lambda r: dump(r/'current-runtime.json',{**load(r/'current-runtime.json'),'release_subject':'MLOPS-PAY-RISK-PROD-2026-08-emergency-r30'}),'current_release_changed')
expect_blocked(lambda r: dump(r/'controller-state.json',{**load(r/'controller-state.json'),'ready':False}),'controller_not_ready')
expect_blocked(lambda r: dump(r/'controller-state.json',{**load(r/'controller-state.json'),'reconciled_generation':30}),'controller_generation_not_reconciled')
def incomplete(r):
    f=load(r/'fleet-readback.json'); f['instances']=f['instances'][:2]; dump(r/'fleet-readback.json',f)
expect_blocked(incomplete,'fleet_readback_incomplete')
def not_ready(r):
    make_valid(r); f=load(r/'fleet-readback.json'); f['instances'][0]['ready']=False; dump(r/'fleet-readback.json',f)
expect_blocked(not_ready,'fleet_instance_not_ready')
def unexercised(r):
    make_valid(r); f=load(r/'fleet-readback.json'); f['instances'][0]['request_trace_count']=0; dump(r/'fleet-readback.json',f)
expect_blocked(unexercised,'fleet_readback_unexercised')
expect_invalid(lambda r: dump(r/'release-approval.json',{**load(r/'release-approval.json'),'release_manifest_sha256':'sha256:'+'0'*64}),'approval release digest mismatch')
expect_invalid(lambda r: dump(r/'deployment-spec.json',{**load(r/'deployment-spec.json'),'serving_image':'registry.example/ml/risk-server:latest'}),'mutable serving image')
expect_invalid(lambda r: dump(r/'deployment-spec.json',{**load(r/'deployment-spec.json'),'feature_contract':'payment-risk-features-v5'}),'deployment feature mismatch')
expect_invalid(lambda r: dump(r/'controller-state.json',{**load(r/'controller-state.json'),'observed_spec_sha256':'sha256:'+'f'*64}),'controller spec digest mismatch')
expect_invalid(lambda r: dump(r/'release-manifest.json',{**load(r/'release-manifest.json'),'environment':'staging'}),'foreign release environment')
expect_invalid(lambda r: dump(r/'release-manifest.json',{**load(r/'release-manifest.json'),'promotion_authorized':False}),'unpromoted release')
def duplicate(r):
    make_valid(r); f=load(r/'fleet-readback.json'); f['instances'][1]['instance_id']=f['instances'][0]['instance_id']; dump(r/'fleet-readback.json',f)
expect_invalid(duplicate,'duplicate fleet instance')
root=make_case()
try:
    make_valid(root); p,report,traffic=run_case(root)
    if p.returncode!=0: fail('could not establish valid report for conflict test')
    report.write_text('{"decision":"foreign-state"}\n'); before=report.read_bytes(); p2,_,traffic2=run_case(root)
    if p2.returncode==0 or report.read_bytes()!=before: fail('conflicting existing report was overwritten')
    if traffic2.exists(): fail('conflict path created traffic-change-request.json')
finally: shutil.rmtree(root,ignore_errors=True)
for name in PROTECTED:
    if (LAB_ROOT/(name+'.template')).read_bytes()!=(WORKSPACE/name).read_bytes(): fail(f'validator mutated protected canonical input: {name}')
print('PASS: delivery gate binds the promoted release to exact immutable deployment rendering, controller reconciliation and complete fleet fingerprints, while never converting delivery verification into rollout authority')
