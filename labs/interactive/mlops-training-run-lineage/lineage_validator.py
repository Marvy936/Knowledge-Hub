#!/usr/bin/env python3
import copy, hashlib, json, random, subprocess, tempfile
from pathlib import Path

LAB_ROOT=Path(__file__).resolve().parent
WORKSPACE=Path('/workspace')
PROTECTED={
  'training-lineage-contract.json':LAB_ROOT/'training-lineage-contract.json.template',
  'approved-training-request.json':LAB_ROOT/'approved-training-request.json.template',
  'training-run.json':LAB_ROOT/'training-run.json.template',
  'trainer-config.json':LAB_ROOT/'trainer-config.json.template',
  'model.bin':LAB_ROOT/'model.bin.template',
}

def fail(msg): raise AssertionError(msg)
def load(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_json(path,obj): Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def jbytes(obj): return (json.dumps(obj,indent=2,sort_keys=True)+'\n').encode()

def invoke(contract,request,run,config,model,candidate,expect_success):
    candidate=Path(candidate)
    before=candidate.read_bytes() if candidate.exists() else None
    p=subprocess.run([
      'python3',str(WORKSPACE/'lineage_gate.py'),
      '--contract',str(contract),'--request',str(request),'--run',str(run),
      '--config',str(config),'--model',str(model),'--candidate',str(candidate)
    ],capture_output=True,text=True)
    if expect_success:
        if p.returncode:
            fail('lineage gate failed: '+(p.stderr.strip() or p.stdout.strip()))
        try: out=json.loads(p.stdout)
        except Exception as e: fail('bad JSON output: '+str(e))
        return out
    if p.returncode==0: fail('invalid lineage evidence was accepted')
    after=candidate.read_bytes() if candidate.exists() else None
    if after!=before: fail('rejected evidence mutated candidate state')
    try: return json.loads(p.stdout)
    except Exception: return {'decision':'rejected'}

def expected_candidate(contract,request,run,config,model):
    c=load(contract); r=load(run); ex=c['execution']; op=c['output_policy']; model_sha='sha256:'+sha(model)
    cid='candidate-'+hashlib.sha256((c['training_subject_id']+'|'+r['run_id']+'|'+model_sha).encode()).hexdigest()[:16]
    return {
      'candidate_id':cid,
      'candidate_state':op['candidate_state'],
      'training_subject_id':c['training_subject_id'],
      'request_id':c['request_id'],
      'operation_id':c['operation_id'],
      'run_id':r['run_id'],
      'model_family':c['model_family'],
      'baseline_release':c['baseline_release'],
      'dataset_generation_id':c['dataset_generation_id'],
      'training_data_manifest_sha256':c['training_data_manifest_sha256'],
      'label_contract':c['label_contract'],
      'source_revision':ex['source_revision'],
      'trainer_image_digest':ex['trainer_image_digest'],
      'dependency_lock_sha256':ex['dependency_lock_sha256'],
      'trainer_config_id':ex['trainer_config_id'],
      'trainer_config_sha256':ex['trainer_config_sha256'],
      'random_seed':ex['random_seed'],
      'model_artifact_sha256':model_sha,
      'contract_sha256':'sha256:'+sha(contract),
      'approved_request_sha256':'sha256:'+sha(request),
      'training_run_sha256':'sha256:'+sha(run),
      'lineage_verified':True,
      'evaluation_required':True,
      'promotion_mode':op['promotion_mode'],
      'promotion_authorized':False,
    }

def temp_json(tmp,name,obj):
    p=tmp/name; write_json(p,obj); return p

def main():
    for name,template in PROTECTED.items():
        p=WORKSPACE/name
        if not p.exists() or p.read_bytes()!=template.read_bytes(): fail('protected input modified: '+name)

    contract=WORKSPACE/'training-lineage-contract.json'; request=WORKSPACE/'approved-training-request.json'
    run=WORKSPACE/'training-run.json'; config=WORKSPACE/'trainer-config.json'; model=WORKSPACE/'model.bin'
    candidate=WORKSPACE/'candidate-manifest.json'; candidate.unlink(missing_ok=True)
    canonical=invoke(contract,request,run,config,model,candidate,False)
    if canonical.get('decision')!='rejected': fail('canonical mismatched run was not rejected')
    if canonical.get('reasons')!=['source_revision_mismatch','trainer_image_digest_mismatch']:
        fail('canonical rejection reasons mismatch: '+json.dumps(canonical,sort_keys=True))
    if candidate.exists(): fail('canonical rejection created candidate')

    base_run=load(run); c=load(contract); ex=c['execution']; base_req=load(request); rng=random.Random(280816)
    healthy=copy.deepcopy(base_run); healthy['source_revision']=ex['source_revision']; healthy['trainer_image_digest']=ex['trainer_image_digest']

    with tempfile.TemporaryDirectory(prefix='kh-lineage-') as td:
        tmp=Path(td)
        healthy_run=temp_json(tmp,'healthy-run.json',healthy); cand=tmp/'candidate.json'
        first=invoke(contract,request,healthy_run,config,model,cand,True)
        if first.get('decision')!='candidate_ready_for_evaluation': fail('healthy run did not create evaluation candidate')
        expected=expected_candidate(contract,request,healthy_run,config,model)
        if load(cand)!=expected: fail('candidate manifest does not bind exact lineage')
        if load(cand)['promotion_authorized'] is not False or load(cand)['evaluation_required'] is not True:
            fail('candidate crossed evaluation/promotion boundary')
        before=cand.read_bytes(); first_stdout=first
        second=invoke(contract,request,healthy_run,config,model,cand,True)
        if second!=first_stdout or cand.read_bytes()!=before: fail('exact replay is not byte-for-byte idempotent')

        conflict=tmp/'conflict.json'; conflict.write_text('{"foreign":"state"}\n'); cb=conflict.read_bytes()
        out=invoke(contract,request,healthy_run,config,model,conflict,False)
        if 'candidate_state_conflict' not in out.get('reasons',[]): fail('candidate state conflict was not rejected')
        if conflict.read_bytes()!=cb: fail('candidate state conflict was overwritten')

        invalid_runs=[]
        def vr(name,field,value):
            x=copy.deepcopy(healthy)
            if isinstance(field,tuple): x[field[0]][field[1]]=value
            else: x[field]=value
            invalid_runs.append((name,x))
        vr('subject','training_subject_id','FOREIGN-SUBJECT')
        vr('request-id','request_id','foreign-request')
        vr('operation','operation_id','foreign-operation')
        vr('dataset','dataset_generation_id','pay-train-2026-08-g41')
        vr('manifest','training_data_manifest_sha256','sha256:'+'1'*64)
        vr('label','label_contract','instant-review-v1')
        vr('request-digest','approved_request_sha256','sha256:'+'2'*64)
        vr('source','source_revision','2'*40)
        vr('image','trainer_image_digest','sha256:'+'3'*64)
        vr('lock','dependency_lock_sha256','sha256:'+'4'*64)
        vr('config-id','trainer_config_id','payment-risk-xgb-v11')
        vr('config-sha','trainer_config_sha256','sha256:'+'5'*64)
        vr('seed','random_seed',999)
        vr('entrypoint','entrypoint',['python3','train.py'])
        vr('status','status','failed')
        vr('artifact-type',('output','artifact_type'),'pickle-model')
        vr('artifact-file',('output','artifact_filename'),'other.bin')
        vr('artifact-digest',('output','artifact_sha256'),'sha256:'+'6'*64)
        for name,obj in invalid_runs:
            invoke(contract,request,temp_json(tmp,name+'.json',obj),config,model,tmp/(name+'-candidate.json'),False)

        bad_req=copy.deepcopy(base_req); bad_req['promotion_authorized']=True
        invoke(contract,temp_json(tmp,'bad-request.json',bad_req),healthy_run,config,model,tmp/'bad-request-candidate.json',False)
        bad_req2=copy.deepcopy(base_req); bad_req2['promotion_mode']='auto-promote'
        invoke(contract,temp_json(tmp,'bad-mode-request.json',bad_req2),healthy_run,config,model,tmp/'bad-mode-candidate.json',False)

        bad_cfg=load(config); bad_cfg['metric']='logloss'; bad_cfg_path=temp_json(tmp,'bad-config.json',bad_cfg)
        invoke(contract,request,healthy_run,bad_cfg_path,model,tmp/'bad-config-candidate.json',False)
        bad_model=tmp/'bad-model.bin'; bad_model.write_bytes(Path(model).read_bytes()+b'TAMPERED\n')
        invoke(contract,request,healthy_run,config,bad_model,tmp/'bad-model-candidate.json',False)

        for i in range(8):
            x=copy.deepcopy(healthy); x['run_id']=f'train-pay-generated-{i:02d}'
            x['started_at']=f'2026-08-16T14:{i:02d}:00Z'; x['completed_at']=f'2026-08-16T14:{i:02d}:30Z'
            items=list(x.items()); rng.shuffle(items); x=dict(items)
            rp=temp_json(tmp,f'generated-{i}.json',x); cp=tmp/f'generated-{i}-candidate.json'
            out=invoke(contract,request,rp,config,model,cp,True)
            if out.get('decision')!='candidate_ready_for_evaluation': fail('generated valid run failed')
            if load(cp)!=expected_candidate(contract,request,rp,config,model): fail('generated candidate lineage mismatch')

    for name,template in PROTECTED.items():
        if (WORKSPACE/name).read_bytes()!=template.read_bytes(): fail('protected input changed: '+name)
    if (WORKSPACE/'promotion-request.json').exists(): fail('forbidden promotion request created')
    print('PASS: training lineage gate binds the approved retraining subject to exact dataset/code/image/dependency/config execution and exact artifact bytes before candidate registration, while preserving the evaluation and promotion boundary')

if __name__=='__main__':
    try: main()
    except AssertionError as e:
        print('FAIL: '+str(e)); raise SystemExit(1)
