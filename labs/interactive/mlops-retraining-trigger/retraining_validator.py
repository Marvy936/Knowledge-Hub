#!/usr/bin/env python3
import copy, hashlib, json, random, subprocess, tempfile
from pathlib import Path
LAB_ROOT=Path(__file__).resolve().parent; WORKSPACE=Path('/workspace')
PROTECTED={'retraining-contract.json':LAB_ROOT/'retraining-contract.json.template','trigger-evidence.json':LAB_ROOT/'trigger-evidence.json.template','readiness-evidence.json':LAB_ROOT/'readiness-evidence.json.template'}
INITIAL_LEDGER=LAB_ROOT/'operations-ledger.json.template'
def fail(m): raise AssertionError(m)
def load(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_json(p,o): Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
def expected(cp,tp,rp,ledger):
 c,t,r=load(cp),load(tp),load(rp); base={'baseline_release':c['baseline_release'],'contract_id':c['contract_id'],'contract_sha256':sha(cp),'model_family':c['model_family'],'promotion_authorized':False,'retraining_subject_id':c['retraining_subject_id'],'trigger_evidence_sha256':sha(tp),'readiness_evidence_sha256':sha(rp)}
 p=c['trigger_policy']; n=p['minimum_consecutive_failed_windows']; s=t['windows'][-n:] if len(t['windows'])>=n else t['windows']; complete=len(s)>=n and all(x['complete'] for x in s); mature=complete and all(x['mature_labels']>=p['minimum_mature_labels_per_window'] for x in s); failed=mature and all((x['baseline_recall']-x['observed_recall'])>=p['recall_drop_min'] for x in s)
 if not complete:return {**base,'decision':'blocked','reason':'trigger_evidence_incomplete'},ledger,None
 if not mature:return {**base,'decision':'blocked','reason':'mature_label_count_insufficient'},ledger,None
 if not failed:return {**base,'decision':'no_op','reason':'persistence_not_met'},ledger,None
 q=c['readiness_policy']
 if r['source_watermark']<q['source_watermark_required']:return {**base,'decision':'blocked','reason':'source_watermark_incomplete'},ledger,None
 if r['label_watermark']<c['label_cutoff']:return {**base,'decision':'blocked','reason':'label_watermark_not_mature'},ledger,None
 if r['eligible_rows']<q['minimum_eligible_rows']:return {**base,'decision':'blocked','reason':'training_population_too_small'},ledger,None
 if r['duplicate_rows']>q['maximum_duplicate_rows']:return {**base,'decision':'blocked','reason':'duplicate_rows_present'},ledger,None
 dedup=f"{c['model_family']}:{r['dataset_generation_id']}:{c['label_contract']}"; opid='ct-op-'+hashlib.sha256((c['retraining_subject_id']+'|'+dedup).encode()).hexdigest()[:12]
 result={**base,'decision':'start_training','reason':'persistent_degradation_and_ready_data','deduplication_key':dedup,'operation_id':opid,'dataset_generation_id':r['dataset_generation_id'],'training_data_manifest_sha256':sha(rp)}
 for op in ledger['operations']:
  if op.get('deduplication_key')==dedup:
   if op.get('retraining_subject_id')==c['retraining_subject_id'] and op.get('operation_id')==opid:return result,ledger,None
   return {**base,'decision':'reuse_existing','reason':'semantic_duplicate_training_subject','deduplication_key':dedup,'operation_id':op.get('operation_id')},ledger,None
 la=copy.deepcopy(ledger); la['operations'].append({'deduplication_key':dedup,'operation_id':opid,'retraining_subject_id':c['retraining_subject_id'],'status':'requested','training_data_generation':r['dataset_generation_id']})
 req={'baseline_release':c['baseline_release'],'dataset_generation_id':r['dataset_generation_id'],'deduplication_key':dedup,'label_contract':c['label_contract'],'label_cutoff':c['label_cutoff'],'logical_interval':c['logical_interval'],'model_family':c['model_family'],'operation_id':opid,'promotion_authorized':False,'promotion_mode':'validation-required','readiness_evidence_sha256':sha(rp),'retraining_subject_id':c['retraining_subject_id'],'training_data_manifest_sha256':sha(rp),'trigger_evidence_sha256':sha(tp)}
 return result,la,req
def run(t,r,l,q,success=True):
 lb=Path(l).read_bytes(); rb=Path(q).read_bytes() if Path(q).exists() else None; p=subprocess.run(['python3',str(WORKSPACE/'retraining_coordinator.py'),'--contract',str(WORKSPACE/'retraining-contract.json'),'--trigger',str(t),'--readiness',str(r),'--ledger',str(l),'--request',str(q)],capture_output=True,text=True)
 if success:
  if p.returncode: fail('coordinator failed: '+p.stderr.strip())
  try:return json.loads(p.stdout)
  except Exception as e:fail(f'bad JSON output: {e}')
 if not p.returncode:fail('invalid evidence accepted')
 if Path(l).read_bytes()!=lb:fail('invalid evidence mutated ledger')
 if (Path(q).read_bytes() if Path(q).exists() else None)!=rb:fail('invalid evidence mutated request')
def case(t,r,l,q):
 before=load(l); wanted,wl,wq=expected(WORKSPACE/'retraining-contract.json',t,r,before); actual=run(t,r,l,q)
 if actual!=wanted:fail('decision mismatch\nEXPECTED '+json.dumps(wanted,sort_keys=True)+'\nACTUAL '+json.dumps(actual,sort_keys=True))
 if load(l)!=wl:fail('ledger mismatch')
 if wq is None:
  if Path(q).exists():fail('non-start created request')
 else:
  if not Path(q).exists() or load(q)!=wq:fail('training request mismatch')
 return actual
def tj(tmp,n,o):p=tmp/n;write_json(p,o);return p
def fl(tmp,n):p=tmp/n;p.write_bytes(INITIAL_LEDGER.read_bytes());return p
def main():
 for n,t in PROTECTED.items():
  if not (WORKSPACE/n).exists() or (WORKSPACE/n).read_bytes()!=t.read_bytes():fail('protected evidence modified: '+n)
 req=WORKSPACE/'training-request.json';req.unlink(missing_ok=True); c=case(WORKSPACE/'trigger-evidence.json',WORKSPACE/'readiness-evidence.json',WORKSPACE/'operations-ledger.json',req)
 if c['decision']!='blocked' or c['reason']!='label_watermark_not_mature':fail('canonical readiness block mismatch')
 bt=load(WORKSPACE/'trigger-evidence.json');br=load(WORKSPACE/'readiness-evidence.json');rng=random.Random(270816)
 with tempfile.TemporaryDirectory(prefix='kh-ct-') as td:
  tmp=Path(td);ready=copy.deepcopy(br);ready['label_watermark']='2026-08-15T00:00:00Z'; vt=tj(tmp,'valid-trigger.json',bt);vr=tj(tmp,'valid-ready.json',ready);l=fl(tmp,'valid-ledger.json');q=tmp/'valid-request.json';first=case(vt,vr,l,q)
  if first['decision']!='start_training':fail('valid trigger did not start'); lb=l.read_bytes();qb=q.read_bytes();second=run(vt,vr,l,q)
  if second!=first or l.read_bytes()!=lb or q.read_bytes()!=qb:fail('exact replay not idempotent')
  if load(q)['promotion_authorized'] is not False:fail('request bypassed promotion boundary')
  dl=fl(tmp,'dup-ledger.json');d=load(dl);dedup=f"payment-risk:{ready['dataset_generation_id']}:confirmed_loss_within_30d-v2";d['operations'].append({'deduplication_key':dedup,'operation_id':'ct-op-existing','status':'running','training_data_generation':ready['dataset_generation_id'],'retraining_subject_id':'OTHER-SUBJECT'});write_json(dl,d);dq=tmp/'dup-request.json'
  if case(vt,vr,dl,dq)['decision']!='reuse_existing':fail('duplicate not reused')
  variants=[];x=copy.deepcopy(bt);x['windows'][-1]['complete']=False;variants.append(('incomplete',x,ready,'blocked'));x=copy.deepcopy(bt);x['windows'][-1]['mature_labels']=3;variants.append(('lowlabels',x,ready,'blocked'));x=copy.deepcopy(bt);x['windows'][0]['observed_recall']=0.90;variants.append(('transient',x,ready,'no_op'));x=copy.deepcopy(ready);x['source_watermark']='2026-07-31T23:00:00Z';variants.append(('source',bt,x,'blocked'));x=copy.deepcopy(ready);x['eligible_rows']=8;variants.append(('small',bt,x,'blocked'));x=copy.deepcopy(ready);x['duplicate_rows']=2;variants.append(('duplicates',bt,x,'blocked'))
  for n,tv,rv,dn in variants:
   if case(tj(tmp,n+'-t.json',tv),tj(tmp,n+'-r.json',rv),fl(tmp,n+'-l.json'),tmp/(n+'-q.json'))['decision']!=dn:fail(n+' wrong decision')
  for i in range(8):
   tv=copy.deepcopy(bt);rng.shuffle(tv['windows']);rv=copy.deepcopy(ready);rv['dataset_generation_id']=f'pay-train-2026-08-g{30+i}'
   if case(tj(tmp,f'g{i}t.json',tv),tj(tmp,f'g{i}r.json',rv),fl(tmp,f'g{i}l.json'),tmp/f'g{i}q.json')['decision']!='start_training':fail('generated ready case failed')
  invalid=[];x=copy.deepcopy(bt);x['retraining_subject_id']='FOREIGN';invalid.append((x,ready));x=copy.deepcopy(bt);x['trigger_policy_id']='performance-persistent-v3';invalid.append((x,ready));x=copy.deepcopy(ready);x['schema_id']='payment-risk-training-v7';invalid.append((bt,x));x=copy.deepcopy(ready);x['feature_generation']='payment-risk-features-v5';invalid.append((bt,x));x=copy.deepcopy(ready);x['label_contract']='instant-review-v1';invalid.append((bt,x));x=copy.deepcopy(ready);x['logical_interval']['end_exclusive']='2026-08-02T00:00:00Z';invalid.append((bt,x))
  for i,(tv,rv) in enumerate(invalid):run(tj(tmp,f'i{i}t.json',tv),tj(tmp,f'i{i}r.json',rv),fl(tmp,f'i{i}l.json'),tmp/f'i{i}q.json',False)
 for n,t in PROTECTED.items():
  if (WORKSPACE/n).read_bytes()!=t.read_bytes():fail('protected evidence changed: '+n)
 if (WORKSPACE/'promotion-request.json').exists():fail('forbidden promotion request created')
 print('PASS: retraining coordinator binds exact trigger/readiness evidence, requires persistent mature information, deduplicates semantic training subjects, and never converts training authority into promotion authority')
if __name__=='__main__':
 try:main()
 except AssertionError as e:print('FAIL: '+str(e));raise SystemExit(1)
