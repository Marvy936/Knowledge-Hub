#!/usr/bin/env python3
import hashlib, json, math, shutil, subprocess, tempfile
from pathlib import Path

LAB_ROOT=Path(__file__).resolve().parent
WORK=Path('/workspace')
INPUTS={
 'contract':'inference-contract.json','request':'request.json','features':'feature-snapshot.json','model':'model.json',
 'policy':'policy.json','trace':'runtime-trace.json'
}
TEMPLATES={k:LAB_ROOT/(v+'.template') for k,v in INPUTS.items()}
CANON_REASONS=['fallback_action_not_allowed','fallback_reason_reporting_mismatch','fallback_reporting_mismatch','loaded_model_digest_mismatch']
PASS='PASS: online inference gate binds exact request identity to loaded release/model/runtime, point-in-time feature bytes, policy/fallback execution and idempotent action evidence while preserving promotion and retraining authority boundaries'

def fail(msg):
    print('FAIL:',msg); raise SystemExit(1)

def load(p): return json.loads(Path(p).read_text())
def dump(p,o): Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
def sha(p): return 'sha256:'+hashlib.sha256(Path(p).read_bytes()).hexdigest()
def healthy_trace(base, model_sha, score, action):
    t=json.loads(json.dumps(base)); t['loaded_model_sha256']=model_sha; t['actual_feature_fallback']=False; t['actual_fallback_reason']=None
    t['response']['actual_model_sha256']=model_sha; t['response']['score']=score; t['response']['action']=action; t['response']['feature_fallback']=False; t['response']['fallback_reason']=None
    return t

def calc(model,features,policy):
    z=float(model['bias'])+sum(float(w)*float(features['values'][k]) for k,w in model['coefficients'].items())
    s=round(1/(1+math.exp(-z)),6)
    if s>=policy['thresholds']['decline_at_or_above']: a=policy['actions']['decline']
    elif s>=policy['thresholds']['manual_review_at_or_above']: a=policy['actions']['review']
    else: a=policy['actions']['below_review']
    return s,a

def seed(td):
    td=Path(td)
    for k,name in INPUTS.items(): shutil.copy2(TEMPLATES[k], td/name)
    return td

def run(td):
    td=Path(td); gate=WORK/'inference_gate.py'
    cmd=['python3',str(gate),'--contract',str(td/INPUTS['contract']),'--request',str(td/INPUTS['request']),'--features',str(td/INPUTS['features']), '--model',str(td/INPUTS['model']),'--policy',str(td/INPUTS['policy']),'--trace',str(td/INPUTS['trace']),'--evidence',str(td/'inference-evidence.json'),'--action-ledger',str(td/'action-ledger.json')]
    return subprocess.run(cmd,text=True,capture_output=True)

def decision(cp):
    try: return json.loads(cp.stdout.strip().splitlines()[-1])
    except Exception: return None

def assert_reject(td, expected=None):
    cp=run(td)
    if cp.returncode==0: fail('invalid scenario was accepted')
    d=decision(cp)
    if not d or d.get('decision')!='rejected': fail('invalid scenario did not return a structured rejection')
    if expected and expected not in d.get('reasons',[]): fail(f'missing rejection reason {expected}: {d}')
    if (Path(td)/'inference-evidence.json').exists() or (Path(td)/'action-ledger.json').exists(): fail('rejected scenario created side effects')
    return d

def mutation_case(name, mutate, expected):
    with tempfile.TemporaryDirectory(prefix='kh-inf-') as x:
        td=seed(x); c=load(td/'inference-contract.json'); m=load(td/'model.json'); f=load(td/'feature-snapshot.json'); p=load(td/'policy.json'); t=load(td/'runtime-trace.json'); s,a=calc(m,f,p)
        t=healthy_trace(t,c['model']['sha256'],s,a); dump(td/'runtime-trace.json',t)
        mutate(td)
        assert_reject(td,expected)

def main():
    gate=WORK/'inference_gate.py'
    if not gate.exists(): fail('/workspace/inference_gate.py is missing; run reset')
    protected={k:TEMPLATES[k].read_bytes() for k in TEMPLATES}
    with tempfile.TemporaryDirectory(prefix='kh-inf-canon-') as x:
        td=seed(x); d=assert_reject(td)
        if d.get('reasons')!=CANON_REASONS: fail(f'canonical rejection reasons differ: {d.get("reasons")}')
    with tempfile.TemporaryDirectory(prefix='kh-inf-ok-') as x:
        td=seed(x); c=load(td/'inference-contract.json'); m=load(td/'model.json'); f=load(td/'feature-snapshot.json'); p=load(td/'policy.json'); t=load(td/'runtime-trace.json'); s,a=calc(m,f,p)
        t=healthy_trace(t,c['model']['sha256'],s,a); dump(td/'runtime-trace.json',t)
        cp=run(td)
        if cp.returncode!=0: fail('healthy execution was rejected: '+cp.stdout+cp.stderr)
        ev=load(td/'inference-evidence.json'); led=load(td/'action-ledger.json')
        checks={
          'verified':ev.get('inference_verified') is True,'model':ev.get('model_sha256')==c['model']['sha256'],
          'feature hash':ev.get('feature_snapshot_sha256')==sha(td/'feature-snapshot.json'),'policy hash':ev.get('policy_sha256')==sha(td/'policy.json'),
          'score':ev.get('score')==s,'action':ev.get('action')==a,'promotion boundary':ev.get('promotion_authorized') is False,
          'retraining boundary':ev.get('retraining_authorized') is False,'ledger action':led.get('action')==a,
          'idempotency':led.get('idempotency_key')=='action:'+load(td/'request.json')['operation_id']+':'+p['policy_id']
        }
        for k,v in checks.items():
            if not v: fail('healthy evidence check failed: '+k)
        out1=cp.stdout; eb=(td/'inference-evidence.json').read_bytes(); lb=(td/'action-ledger.json').read_bytes()
        cp2=run(td)
        if cp2.returncode!=0 or cp2.stdout!=out1 or (td/'inference-evidence.json').read_bytes()!=eb or (td/'action-ledger.json').read_bytes()!=lb: fail('exact replay is not byte-idempotent')
        if (td/'promotion-request.json').exists() or (td/'retraining-request.json').exists(): fail('healthy inference created forbidden authority artifacts')
    with tempfile.TemporaryDirectory(prefix='kh-inf-conflict-') as x:
        td=seed(x); c=load(td/'inference-contract.json'); m=load(td/'model.json'); f=load(td/'feature-snapshot.json'); p=load(td/'policy.json'); t=load(td/'runtime-trace.json'); s,a=calc(m,f,p)
        dump(td/'runtime-trace.json',healthy_trace(t,c['model']['sha256'],s,a)); bad=b'{"foreign":true}\n'; (td/'inference-evidence.json').write_bytes(bad)
        cp=run(td); d=decision(cp)
        if cp.returncode==0 or d.get('reasons')!=['prediction_state_conflict'] or (td/'inference-evidence.json').read_bytes()!=bad: fail('prediction conflict was not preserved')
        if (td/'action-ledger.json').exists(): fail('prediction conflict created an action side effect')
    with tempfile.TemporaryDirectory(prefix='kh-inf-action-conflict-') as x:
        td=seed(x); c=load(td/'inference-contract.json'); m=load(td/'model.json'); f=load(td/'feature-snapshot.json'); p=load(td/'policy.json'); t=load(td/'runtime-trace.json'); s,a=calc(m,f,p)
        dump(td/'runtime-trace.json',healthy_trace(t,c['model']['sha256'],s,a)); bad=b'{"foreign":true}\n'; (td/'action-ledger.json').write_bytes(bad)
        cp=run(td); d=decision(cp)
        if cp.returncode==0 or d.get('reasons')!=['action_state_conflict'] or (td/'action-ledger.json').read_bytes()!=bad: fail('action conflict was not preserved')
        if (td/'inference-evidence.json').exists(): fail('action conflict created prediction side effect')
    mutation_case('foreign operation', lambda td: (lambda o:(o.__setitem__('operation_id','foreign-op'),dump(td/'runtime-trace.json',o)))(load(td/'runtime-trace.json')), 'runtime_operation_mismatch')
    mutation_case('wrong requested release', lambda td: (lambda o:(o.__setitem__('release_subject','MLOPS-FOREIGN'),dump(td/'request.json',o)))(load(td/'request.json')), 'requested_release_mismatch')
    mutation_case('wrong caller', lambda td: (lambda o:(o.__setitem__('authenticated_caller','unknown-client'),dump(td/'request.json',o)))(load(td/'request.json')), 'caller_not_allowed')
    mutation_case('future feature', lambda td: (lambda o:(o.__setitem__('as_of','2026-08-16T12:00:01Z'),dump(td/'feature-snapshot.json',o), (lambda t:(t.__setitem__('feature_snapshot_sha256',sha(td/'feature-snapshot.json')),dump(td/'runtime-trace.json',t)))(load(td/'runtime-trace.json'))))(load(td/'feature-snapshot.json')), 'feature_snapshot_from_future')
    mutation_case('stale feature', lambda td: (lambda o:(o.__setitem__('as_of','2026-08-16T11:50:00Z'),dump(td/'feature-snapshot.json',o), (lambda t:(t.__setitem__('feature_snapshot_sha256',sha(td/'feature-snapshot.json')),dump(td/'runtime-trace.json',t)))(load(td/'runtime-trace.json'))))(load(td/'feature-snapshot.json')), 'feature_snapshot_stale')
    mutation_case('serving image', lambda td: (lambda o:(o.__setitem__('serving_image_digest','sha256:'+'2'*64),dump(td/'runtime-trace.json',o)))(load(td/'runtime-trace.json')), 'serving_image_digest_mismatch')
    mutation_case('loaded model', lambda td: (lambda o:(o.__setitem__('loaded_model_sha256','sha256:'+'3'*64),o['response'].__setitem__('actual_model_sha256','sha256:'+'3'*64),dump(td/'runtime-trace.json',o)))(load(td/'runtime-trace.json')), 'loaded_model_digest_mismatch')
    mutation_case('protocol', lambda td: (lambda o:(o.__setitem__('protocol','custom-v1'),dump(td/'runtime-trace.json',o)))(load(td/'runtime-trace.json')), 'protocol_mismatch')
    mutation_case('deadline', lambda td: (lambda o:(o.__setitem__('completed_at','2026-08-16T12:00:04Z'),dump(td/'runtime-trace.json',o)))(load(td/'runtime-trace.json')), 'deadline_exceeded')
    mutation_case('score', lambda td: (lambda o:(o['response'].__setitem__('score',0.1),dump(td/'runtime-trace.json',o)))(load(td/'runtime-trace.json')), 'score_mismatch')
    mutation_case('action', lambda td: (lambda o:(o['response'].__setitem__('action','approve'),dump(td/'runtime-trace.json',o)))(load(td/'runtime-trace.json')), 'action_mismatch')
    mutation_case('idempotency key', lambda td: (lambda o:(o.__setitem__('action_idempotency_key','unstable-key'),dump(td/'runtime-trace.json',o)))(load(td/'runtime-trace.json')), 'action_idempotency_key_mismatch')
    mutation_case('tampered model bytes', lambda td: (lambda o:(o.__setitem__('bias',9.0),dump(td/'model.json',o)))(load(td/'model.json')), 'model_bytes_mismatch')
    mutation_case('tampered policy bytes', lambda td: (lambda o:(o['thresholds'].__setitem__('manual_review_at_or_above',0.1),dump(td/'policy.json',o)))(load(td/'policy.json')), 'policy_bytes_mismatch')
    with tempfile.TemporaryDirectory(prefix='kh-inf-fallback-') as x:
        td=seed(x); c=load(td/'inference-contract.json'); t=load(td/'runtime-trace.json')
        t['loaded_model_sha256']=c['model']['sha256']; t['response']['actual_model_sha256']=c['model']['sha256']; t['response']['feature_fallback']=True; t['response']['fallback_reason']='online_store_timeout'; t['response']['action']='manual_review'
        dump(td/'runtime-trace.json',t); cp=run(td)
        if cp.returncode!=0: fail('truthful allowed fallback was rejected: '+cp.stdout+cp.stderr)
        ev=load(td/'inference-evidence.json')
        if ev.get('feature_fallback') is not True or ev.get('action')!='manual_review': fail('fallback evidence did not preserve fail-closed action')
    for i in range(6):
        with tempfile.TemporaryDirectory(prefix='kh-inf-gen-') as x:
            td=seed(x); c=load(td/'inference-contract.json'); r=load(td/'request.json'); f=load(td/'feature-snapshot.json'); p=load(td/'policy.json'); m=load(td/'model.json'); t=load(td/'runtime-trace.json')
            op=f'payment-op-gen-{i:02d}-risk-r42'; r['operation_id']=op; r['entity_id']=f'merchant-gen-{i:02d}'; f['operation_id']=op; f['snapshot_id']=f'feat-gen-{i:02d}'; dump(td/'request.json',r); dump(td/'feature-snapshot.json',f)
            s,a=calc(m,f,p); t=healthy_trace(t,c['model']['sha256'],s,a); t['operation_id']=op; t['feature_snapshot_id']=f['snapshot_id']; t['feature_snapshot_sha256']=sha(td/'feature-snapshot.json'); t['action_idempotency_key']='action:'+op+':'+p['policy_id']; t['response']['operation_id']=op; dump(td/'runtime-trace.json',t)
            cp=run(td)
            if cp.returncode!=0: fail(f'generated valid execution {i} was rejected: '+cp.stdout+cp.stderr)
    for k,b in protected.items():
        if TEMPLATES[k].read_bytes()!=b: fail('protected canonical template changed during validation: '+k)
    print(PASS)

if __name__=='__main__': main()
