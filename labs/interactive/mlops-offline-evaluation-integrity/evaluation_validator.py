#!/usr/bin/env python3
import hashlib, json, shutil, subprocess, sys, tempfile
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent
WORKSPACE = Path('/workspace')
FILES = {
    'evaluation-contract.json': 'evaluation-contract.json.template',
    'candidate-manifest.json': 'candidate-manifest.json.template',
    'candidate-model.bin': 'candidate-model.bin.template',
    'baseline-model.bin': 'baseline-model.bin.template',
    'evaluation-dataset-manifest.json': 'evaluation-dataset-manifest.json.template',
    'evaluation-dataset.json': 'evaluation-dataset.json.template',
    'training-membership.json': 'training-membership.json.template',
    'evaluation-run.json': 'evaluation-run.json.template',
}


def fail(msg):
    print('FAIL: ' + msg, file=sys.stderr)
    raise SystemExit(1)


def sha(path):
    return 'sha256:' + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def save(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def metric(model, rows, threshold):
    tp = fp = fn = tn = 0
    for row in rows:
        score = float(model['bias']) + sum(float(model['weights'][k]) * float(row['features'][k]) for k in model['weights'])
        pred = 1 if score >= threshold else 0
        label = int(row['label'])
        if pred == 1 and label == 1: tp += 1
        elif pred == 1 and label == 0: fp += 1
        elif pred == 0 and label == 1: fn += 1
        else: tn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn, 'precision': round(precision, 6), 'recall': round(recall, 6), 'f1': round(f1, 6)}


def bundle(model, rows, segments, threshold):
    return {'overall': metric(model, rows, threshold), 'segments': {s: metric(model, [r for r in rows if r['segment'] == s], threshold) for s in segments}}


def copy_case(dst):
    dst.mkdir(parents=True, exist_ok=True)
    for name, template in FILES.items():
        shutil.copyfile(LAB_ROOT / template, dst / name)


def reconcile(case):
    candidate = load(case / 'candidate-manifest.json')
    cand_model = load(case / 'candidate-model.bin')
    base_model = load(case / 'baseline-model.bin')
    dataset = load(case / 'evaluation-dataset.json')
    membership = load(case / 'training-membership.json')
    manifest = load(case / 'evaluation-dataset-manifest.json')
    contract = load(case / 'evaluation-contract.json')
    run = load(case / 'evaluation-run.json')

    candidate['model_artifact_sha256'] = sha(case / 'candidate-model.bin')
    save(case / 'candidate-manifest.json', candidate)

    manifest['dataset_sha256'] = sha(case / 'evaluation-dataset.json')
    manifest['training_membership_sha256'] = sha(case / 'training-membership.json')
    manifest['row_count'] = len(dataset['rows'])
    save(case / 'evaluation-dataset-manifest.json', manifest)

    contract['candidate_manifest_sha256'] = sha(case / 'candidate-manifest.json')
    contract['baseline_model_sha256'] = sha(case / 'baseline-model.bin')
    contract['evaluation_dataset']['manifest_sha256'] = sha(case / 'evaluation-dataset-manifest.json')
    contract['evaluation_dataset']['training_membership_sha256'] = sha(case / 'training-membership.json')
    save(case / 'evaluation-contract.json', contract)

    threshold = float(contract['execution']['decision_threshold'])
    segments = contract['evaluation_dataset']['required_segments']
    rows = dataset['rows']
    run.update({
        'status': 'succeeded',
        'evaluation_subject_id': contract['evaluation_subject_id'],
        'evaluation_contract_sha256': sha(case / 'evaluation-contract.json'),
        'candidate_id': contract['candidate_id'],
        'candidate_manifest_sha256': sha(case / 'candidate-manifest.json'),
        'candidate_model_sha256': sha(case / 'candidate-model.bin'),
        'baseline_release': contract['baseline_release'],
        'baseline_model_sha256': sha(case / 'baseline-model.bin'),
        'evaluation_dataset_id': contract['evaluation_dataset']['dataset_id'],
        'evaluation_dataset_manifest_sha256': sha(case / 'evaluation-dataset-manifest.json'),
        'evaluation_dataset_sha256': sha(case / 'evaluation-dataset.json'),
        'training_membership_sha256': sha(case / 'training-membership.json'),
        'evaluator_generation': contract['execution']['evaluator_generation'],
        'evaluator_image_digest': contract['execution']['evaluator_image_digest'],
        'metric_contract': contract['execution']['metric_contract'],
        'decision_threshold': contract['execution']['decision_threshold'],
        'reported_metrics': {
            'candidate': bundle(cand_model, rows, segments, threshold),
            'baseline': bundle(base_model, rows, segments, threshold),
        },
        'quality_passed': True,
    })
    save(case / 'evaluation-run.json', run)


def make_valid(case):
    copy_case(case)
    data = load(case / 'evaluation-dataset.json')
    data['rows'][1]['merchant_id'] = 'eval-m-002'
    data['rows'][5]['feature_availability']['velocity_24h'] = '2026-05-11T14:58:00Z'
    save(case / 'evaluation-dataset.json', data)
    reconcile(case)


def invoke(script, case):
    report = case / 'evaluation-report.json'
    cmd = [sys.executable, str(script),
        '--contract', str(case / 'evaluation-contract.json'),
        '--candidate', str(case / 'candidate-manifest.json'),
        '--candidate-model', str(case / 'candidate-model.bin'),
        '--baseline-model', str(case / 'baseline-model.bin'),
        '--dataset-manifest', str(case / 'evaluation-dataset-manifest.json'),
        '--dataset', str(case / 'evaluation-dataset.json'),
        '--training-membership', str(case / 'training-membership.json'),
        '--run', str(case / 'evaluation-run.json'),
        '--report', str(report)]
    return subprocess.run(cmd, text=True, capture_output=True), report


def assert_reject(script, case, label):
    before = (case / 'evaluation-report.json').read_bytes() if (case / 'evaluation-report.json').exists() else None
    cp, report = invoke(script, case)
    if cp.returncode == 0:
        fail(label + ' was accepted')
    after = report.read_bytes() if report.exists() else None
    if before != after:
        fail(label + ' changed evaluation report state')
    if (case / 'promotion-request.json').exists():
        fail(label + ' created promotion-request.json')
    return cp


def main():
    script = WORKSPACE / 'evaluate.py'
    if not script.exists():
        fail('/workspace/evaluate.py is missing')

    protected_before = {}
    for name, template in FILES.items():
        wp = WORKSPACE / name
        tp = LAB_ROOT / template
        if not wp.exists(): fail(name + ' is missing')
        protected_before[name] = wp.read_bytes()
        if wp.read_bytes() != tp.read_bytes():
            fail(name + ' differs from protected canonical evidence')

    with tempfile.TemporaryDirectory(prefix='kh-eval-') as td:
        base = Path(td)

        canonical = base / 'canonical'
        copy_case(canonical)
        cp = assert_reject(script, canonical, 'canonical contaminated holdout')
        if 'group_overlap_with_training' not in cp.stdout or 'feature_available_after_prediction' not in cp.stdout:
            fail('canonical rejection did not expose both contamination mechanisms')

        valid = base / 'valid'
        make_valid(valid)
        cp, report = invoke(script, valid)
        if cp.returncode != 0 or not report.exists():
            fail('valid independent evaluation did not produce a report')
        first = report.read_bytes()
        result = json.loads(first)
        if result.get('decision') != 'evaluation_passed': fail('valid evaluation did not pass quality')
        if result.get('promotion_authorized') is not False: fail('evaluation report granted promotion authority')
        if result.get('independent_holdout_verified') is not True or result.get('leakage_checks_passed') is not True:
            fail('valid evaluation did not record integrity checks')
        if result.get('candidate_model_sha256') != sha(valid / 'candidate-model.bin'): fail('report candidate digest mismatch')
        if result.get('evaluation_dataset_sha256') != sha(valid / 'evaluation-dataset.json'): fail('report dataset digest mismatch')
        if (valid / 'promotion-request.json').exists(): fail('valid evaluation created promotion-request.json')
        cp2, _ = invoke(script, valid)
        if cp2.returncode != 0 or report.read_bytes() != first:
            fail('exact replay is not byte-for-byte idempotent')

        conflict = base / 'conflict'
        make_valid(conflict)
        cp, report = invoke(script, conflict)
        if cp.returncode != 0: fail('conflict setup did not pass')
        report.write_text('{"foreign":"state"}\n')
        before = report.read_bytes()
        cp = assert_reject(script, conflict, 'conflicting existing report')
        if report.read_bytes() != before or 'evaluation_report_state_conflict' not in cp.stdout:
            fail('conflicting report was not preserved')

        quality = base / 'quality-fail'
        make_valid(quality)
        c = load(quality / 'evaluation-contract.json')
        c['decision_policy']['minimum_f1_improvement'] = 0.9
        save(quality / 'evaluation-contract.json', c)
        reconcile(quality)
        cp, report = invoke(script, quality)
        if cp.returncode != 0 or load(report).get('decision') != 'failed_quality':
            fail('valid but weak quality case was not recorded as failed_quality')
        if load(report).get('promotion_authorized') is not False: fail('failed quality granted promotion authority')

        candidate_auth = base / 'candidate-auth'
        make_valid(candidate_auth)
        x = load(candidate_auth / 'candidate-manifest.json'); x['promotion_authorized'] = True; save(candidate_auth / 'candidate-manifest.json', x)
        assert_reject(script, candidate_auth, 'candidate with promotion authority')

        model_tamper = base / 'model-tamper'
        make_valid(model_tamper)
        x = load(model_tamper / 'candidate-model.bin'); x['bias'] = -0.2; save(model_tamper / 'candidate-model.bin', x)
        assert_reject(script, model_tamper, 'tampered candidate model bytes')

        baseline_tamper = base / 'baseline-tamper'
        make_valid(baseline_tamper)
        x = load(baseline_tamper / 'baseline-model.bin'); x['bias'] = -0.2; save(baseline_tamper / 'baseline-model.bin', x)
        assert_reject(script, baseline_tamper, 'tampered baseline model bytes')

        failed_run = base / 'failed-run'
        make_valid(failed_run)
        x = load(failed_run / 'evaluation-run.json'); x['status'] = 'failed'; save(failed_run / 'evaluation-run.json', x)
        assert_reject(script, failed_run, 'failed evaluator run')

        evaluator = base / 'evaluator'
        make_valid(evaluator)
        x = load(evaluator / 'evaluation-run.json'); x['evaluator_generation'] = 'risk-evaluator-v6'; save(evaluator / 'evaluation-run.json', x)
        assert_reject(script, evaluator, 'wrong evaluator generation')

        forged = base / 'forged-metrics'
        make_valid(forged)
        x = load(forged / 'evaluation-run.json'); x['reported_metrics']['candidate']['overall']['f1'] = 0.999999; save(forged / 'evaluation-run.json', x)
        cp = assert_reject(script, forged, 'forged reported metrics')
        if 'reported_metrics_mismatch' not in cp.stdout: fail('forged metrics reason missing')

        semantic_tests = []
        group = base / 'group-overlap'; make_valid(group); d = load(group/'evaluation-dataset.json'); d['rows'][0]['merchant_id']='m-train-001'; save(group/'evaluation-dataset.json',d); reconcile(group); semantic_tests.append((group,'group overlap'))
        future = base / 'future-feature'; make_valid(future); d=load(future/'evaluation-dataset.json'); d['rows'][0]['feature_availability']['amount_norm']='2026-05-02T10:00:05Z'; save(future/'evaluation-dataset.json',d); reconcile(future); semantic_tests.append((future,'future feature'))
        dup = base / 'duplicate'; make_valid(dup); d=load(dup/'evaluation-dataset.json'); d['rows'][1]['operation_id']=d['rows'][0]['operation_id']; save(dup/'evaluation-dataset.json',d); reconcile(dup); semantic_tests.append((dup,'duplicate operation'))
        immature = base / 'immature'; make_valid(immature); d=load(immature/'evaluation-dataset.json'); d['rows'][0]['label_mature_at']='2026-07-02T00:00:00Z'; save(immature/'evaluation-dataset.json',d); reconcile(immature); semantic_tests.append((immature,'immature label'))
        stale = base / 'stale-watermark'; make_valid(stale); m=load(stale/'evaluation-dataset-manifest.json'); m['label_watermark']='2026-06-30T23:59:59Z'; save(stale/'evaluation-dataset-manifest.json',m); reconcile(stale); semantic_tests.append((stale,'stale label watermark'))
        purpose = base / 'purpose'; make_valid(purpose); m=load(purpose/'evaluation-dataset-manifest.json'); m['purpose']='validation'; save(purpose/'evaluation-dataset-manifest.json',m); reconcile(purpose); semantic_tests.append((purpose,'non-independent purpose'))
        split = base / 'split'; make_valid(split); m=load(split/'evaluation-dataset-manifest.json'); m['split_generation']='random-row-v1'; save(split/'evaluation-dataset-manifest.json',m); reconcile(split); semantic_tests.append((split,'wrong split generation'))
        segment = base / 'segment'; make_valid(segment); d=load(segment/'evaluation-dataset.json');
        for row in d['rows']:
            if row['segment']=='new_merchant': row['segment']='established_merchant'
        save(segment/'evaluation-dataset.json',d); reconcile(segment); semantic_tests.append((segment,'missing required segment'))
        for case, label in semantic_tests:
            assert_reject(script, case, label)

        for i in range(6):
            generated = base / ('generated-' + str(i))
            make_valid(generated)
            d = load(generated / 'evaluation-dataset.json')
            d['rows'] = d['rows'][i:] + d['rows'][:i]
            for n, row in enumerate(d['rows']):
                row['merchant_id'] = f'generated-{i}-merchant-{n}'
            save(generated / 'evaluation-dataset.json', d)
            reconcile(generated)
            cp, report = invoke(script, generated)
            if cp.returncode != 0 or load(report).get('decision') != 'evaluation_passed':
                fail('generated valid evaluation was rejected')

    for name, before in protected_before.items():
        if (WORKSPACE / name).read_bytes() != before:
            fail(name + ' changed during validation')
    if (WORKSPACE / 'promotion-request.json').exists():
        fail('promotion-request.json exists in workspace')

    print('PASS: offline evaluation binds the exact lineage-verified candidate to an immutable independent holdout, proves split/label/feature-time integrity, recomputes metrics from actual bytes, and never turns evaluation success into promotion authority')


if __name__ == '__main__':
    main()
