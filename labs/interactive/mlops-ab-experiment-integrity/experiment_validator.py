#!/usr/bin/env python3
import copy
import hashlib
import json
import math
import random
import tempfile
import importlib.util
from datetime import datetime
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent
WORKSPACE = Path('/workspace')
PROTECTED = {
    'experiment-contract.json': LAB_ROOT / 'experiment-contract.json.template',
    'experiment-evidence.json': LAB_ROOT / 'experiment-evidence.json.template',
}
INITIAL_STATE = LAB_ROOT / 'experiment-state.json.template'
FORBIDDEN_PROMOTION = WORKSPACE / 'promotion-request.json'


def fail(message):
    raise AssertionError(message)


def load(path):
    return json.loads(Path(path).read_text())


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_ts(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def rounded(value):
    return round(float(value), 6)


def srm_stats(candidate_units, control_units, expected_candidate_share):
    total = candidate_units + control_units
    ec = total * expected_candidate_share
    e0 = total * (1.0 - expected_candidate_share)
    chi2 = ((candidate_units - ec) ** 2) / ec + ((control_units - e0) ** 2) / e0
    p = math.erfc(math.sqrt(chi2 / 2.0))
    return rounded(chi2), rounded(p)


def prop_p(cs, cn, ks, kn):
    if cn <= 0 or kn <= 0:
        return None
    cr = cs / cn
    kr = ks / kn
    pooled = (cs + ks) / (cn + kn)
    var = pooled * (1.0 - pooled) * (1.0 / cn + 1.0 / kn)
    if var <= 0:
        return 1.0 if cr == kr else 0.0
    z = (cr - kr) / math.sqrt(var)
    return rounded(math.erfc(abs(z) / math.sqrt(2.0)))


def expected(contract_path, evidence_path):
    contract = load(contract_path)
    evidence = load(evidence_path)
    start = parse_ts(contract['window']['start'])
    end = parse_ts(contract['window']['end'])
    rows = [r for r in evidence['records'] if r['eligible'] is True and start <= parse_ts(r['event_time']) < end]

    unit_rows = {}
    release_mismatch = set()
    for row in rows:
        unit = row[contract['assignment_unit']]
        unit_rows.setdefault(unit, []).append(row)
        if row['actual_release'] != row['assigned_release']:
            release_mismatch.add(unit)

    contaminated = sorted(unit for unit, rs in unit_rows.items() if len({r['assigned_release'] for r in rs}) > 1)
    first = {unit: rs[0] for unit, rs in unit_rows.items()}
    candidate_units = sum(r['assigned_release'] == contract['candidate_release'] for r in first.values())
    control_units = sum(r['assigned_release'] == contract['control_release'] for r in first.values())
    total_units = candidate_units + control_units
    chi2, srm_p = srm_stats(candidate_units, control_units, contract['expected_allocation']['candidate'])

    invalidity = []
    if contaminated:
        invalidity.append('assignment_contamination')
    if release_mismatch:
        invalidity.append('release_delivery_mismatch')
    srm = contract['sample_ratio_mismatch']
    if total_units >= srm['minimum_total_units'] and srm_p < srm['alpha']:
        invalidity.append('sample_ratio_mismatch')

    consumed = sum(r['manual_review_slot_consumed'] for r in rows)
    shared = contract['shared_resource']
    util = consumed / shared['capacity_slots']
    if shared['outcome_can_be_affected'] and util > shared['maximum_utilization_for_independence']:
        invalidity.append('shared_capacity_interference')

    observations = list(first.values())
    cand = [r for r in observations if r['assigned_release'] == contract['candidate_release'] and r['outcome_status'] == 'mature']
    ctrl = [r for r in observations if r['assigned_release'] == contract['control_release'] and r['outcome_status'] == 'mature']
    cs = sum(r['converted'] for r in cand)
    ks = sum(r['converted'] for r in ctrl)
    cr = cs / len(cand) if cand else 0.0
    kr = ks / len(ctrl) if ctrl else 0.0
    lift = cr - kr
    p = prop_p(cs, len(cand), ks, len(ctrl))

    readiness = []
    policy = contract['analysis_policy']
    if evidence['analysis_stage'] != policy['winner_authority_stage']:
        readiness.append('interim_analysis_only')
    if parse_ts(evidence['outcome_watermark']) < parse_ts(contract['window']['required_outcome_watermark']) or any(r['outcome_status'] != 'mature' for r in observations):
        readiness.append('outcome_maturity_incomplete')
    if len(cand) < policy['minimum_mature_outcomes_per_variant'] or len(ctrl) < policy['minimum_mature_outcomes_per_variant']:
        readiness.append('minimum_mature_outcomes_not_met')

    if invalidity:
        decision = 'invalidate'
    elif readiness:
        decision = 'continue'
    else:
        decision = 'winner_candidate' if p is not None and p < policy['alpha'] and lift >= policy['minimum_absolute_lift'] else 'no_winner'

    return {
        'contract_id': contract['contract_id'],
        'contract_sha256': sha256(contract_path),
        'experiment_subject_id': contract['experiment_subject_id'],
        'evidence_sha256': sha256(evidence_path),
        'assignment': {
            'assignment_unit': contract['assignment_unit'],
            'eligible_units': total_units,
            'candidate_units': candidate_units,
            'control_units': control_units,
            'contaminated_units': contaminated,
            'release_delivery_mismatch_units': sorted(release_mismatch),
            'srm_chi_square': chi2,
            'srm_p_value': srm_p,
        },
        'shared_resource': {
            'resource_id': shared['resource_id'],
            'capacity_slots': shared['capacity_slots'],
            'consumed_slots': consumed,
            'utilization': rounded(util),
        },
        'outcomes': {
            'primary_metric': policy['primary_metric'],
            'candidate_mature_units': len(cand),
            'control_mature_units': len(ctrl),
            'candidate_rate': rounded(cr),
            'control_rate': rounded(kr),
            'absolute_lift': rounded(lift),
            'two_sided_p_value': p,
        },
        'invalidity_reasons': invalidity,
        'readiness_reasons': readiness,
        'decision': decision,
        'causal_claim_supported': decision in {'winner_candidate', 'no_winner'},
        'winner_claim_supported': decision == 'winner_candidate',
        'promotion_authorized': False,
    }


def wanted_state(result):
    return {
        'experiment_subject_id': result['experiment_subject_id'],
        'status': {'invalidate':'invalidated', 'continue':'running', 'winner_candidate':'completed', 'no_winner':'completed'}[result['decision']],
        'last_analysis': result,
    }


def write_variant(tmp, name, value):
    path = tmp / name
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    return path


def fresh_state(tmp, name):
    p = tmp / name
    p.write_bytes(INITIAL_STATE.read_bytes())
    return p


def load_learner():
    path = WORKSPACE / 'experiment_analyzer.py'
    spec = importlib.util.spec_from_file_location('kh_experiment_learner', path)
    if spec is None or spec.loader is None:
        fail('cannot load learner analyzer')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, 'analyze', None)):
        fail('learner must expose analyze(contract_path, evidence_path, state_path)')
    return module


def run_analyzer(evidence_path, state_path, expect_success=True):
    before = Path(state_path).read_bytes()
    FORBIDDEN_PROMOTION.unlink(missing_ok=True)
    learner = load_learner()
    try:
        result = learner.analyze(
            str(WORKSPACE / 'experiment-contract.json'),
            str(evidence_path),
            str(state_path),
        )
    except Exception as exc:
        if expect_success:
            fail(f'analyzer failed unexpectedly: {exc}')
        if Path(state_path).read_bytes() != before:
            fail('rejected evidence mutated experiment state')
        if FORBIDDEN_PROMOTION.exists():
            fail('rejected evidence created a promotion side effect')
        return None, before
    if expect_success:
        if not isinstance(result, dict):
            fail('analyze() must return one result object')
        if FORBIDDEN_PROMOTION.exists():
            fail('experiment analysis created forbidden promotion-request.json')
        return result, before
    fail(f'analyzer accepted malformed/foreign evidence: {json.dumps(result, sort_keys=True)}')

def assert_case(evidence_path, state_path, expected_decision=None):
    wanted = expected(WORKSPACE / 'experiment-contract.json', evidence_path)
    if expected_decision and wanted['decision'] != expected_decision:
        fail(f'validator fixture expected {expected_decision}, computed {wanted["decision"]}')
    actual, _ = run_analyzer(evidence_path, state_path)
    if actual != wanted:
        fail('analysis mismatch\nEXPECTED: ' + json.dumps(wanted, sort_keys=True) + '\nACTUAL:   ' + json.dumps(actual, sort_keys=True))
    if load(state_path) != wanted_state(wanted):
        fail('experiment-state side effect does not match exact analysis result')
    return actual


def make_balanced_final(base, candidate_success=10, control_success=4):
    v = copy.deepcopy(base)
    v['analysis_stage'] = 'final'
    v['outcome_watermark'] = '2026-08-15T16:00:00Z'
    # Keep merchant 1-12 as candidate and 13-24 as control; remove contamination row.
    v['records'] = [r for r in v['records'] if r['request_id'] != 'req-025']
    for i, row in enumerate(v['records'], start=1):
        cand = i <= 12
        rel = 'risk-serving-r42' if cand else 'risk-serving-r39'
        row['assigned_release'] = rel
        row['actual_release'] = rel
        row['outcome_status'] = 'mature'
        success_index = i if cand else i - 12
        row['converted'] = success_index <= (candidate_success if cand else control_success)
        row['manual_review_slot_consumed'] = i in {1, 13, 14, 15}
    return v


def main():
    for name, template in PROTECTED.items():
        p = WORKSPACE / name
        if not p.exists():
            fail(f'missing protected experiment evidence: {name}')
        if p.read_bytes() != template.read_bytes():
            fail(f'protected experiment evidence was modified: {name}')
    if not (WORKSPACE / 'experiment-state.json').exists():
        fail('missing experiment state')
    if not (WORKSPACE / 'experiment_analyzer.py').exists():
        fail('missing learner analyzer')

    canonical = assert_case(WORKSPACE / 'experiment-evidence.json', WORKSPACE / 'experiment-state.json', 'invalidate')
    required_invalid = {'assignment_contamination', 'sample_ratio_mismatch', 'shared_capacity_interference'}
    if not required_invalid.issubset(set(canonical['invalidity_reasons'])):
        fail('canonical incident did not expose all required causal-integrity failures')
    if canonical['causal_claim_supported'] or canonical['winner_claim_supported'] or canonical['promotion_authorized']:
        fail('invalid canonical experiment still claimed causal/promotion authority')

    after = (WORKSPACE / 'experiment-state.json').read_bytes()
    repeated, _ = run_analyzer(WORKSPACE / 'experiment-evidence.json', WORKSPACE / 'experiment-state.json')
    if repeated != canonical:
        fail('repeated exact experiment subject produced another result')
    if (WORKSPACE / 'experiment-state.json').read_bytes() != after:
        fail('repeating exact analysis changed experiment-state bytes')

    contract = load(WORKSPACE / 'experiment-contract.json')
    base = load(WORKSPACE / 'experiment-evidence.json')
    rng = random.Random(260816)
    with tempfile.TemporaryDirectory(prefix='kh-ab-integrity-') as td:
        tmp = Path(td)

        winner = make_balanced_final(base, 10, 4)
        winner_result = assert_case(write_variant(tmp, 'winner.json', winner), fresh_state(tmp, 'winner-state.json'), 'winner_candidate')
        if not winner_result['winner_claim_supported'] or winner_result['promotion_authorized']:
            fail('valid winner semantics do not separate experiment evidence from promotion authority')

        no_winner = make_balanced_final(base, 7, 6)
        assert_case(write_variant(tmp, 'no-winner.json', no_winner), fresh_state(tmp, 'no-winner-state.json'), 'no_winner')

        interim = make_balanced_final(base, 10, 4)
        interim['analysis_stage'] = 'interim'
        assert_case(write_variant(tmp, 'interim.json', interim), fresh_state(tmp, 'interim-state.json'), 'continue')

        immature = make_balanced_final(base, 10, 4)
        immature['outcome_watermark'] = '2026-08-15T15:30:00Z'
        for row in immature['records'][-2:]:
            row['outcome_status'] = 'pending'
            row['converted'] = None
        assert_case(write_variant(tmp, 'immature.json', immature), fresh_state(tmp, 'immature-state.json'), 'continue')

        underpowered = make_balanced_final(base, 4, 2)
        for row in underpowered['records']:
            if int(row['merchant_id'].split('-')[1]) > 10:
                row['eligible'] = False
        # Make exactly five candidate and five control eligible.
        for i, row in enumerate(underpowered['records'], start=1):
            row['eligible'] = i <= 5 or 13 <= i <= 17
        assert_case(write_variant(tmp, 'underpowered.json', underpowered), fresh_state(tmp, 'underpowered-state.json'), 'continue')

        srm_only = make_balanced_final(base, 15, 3)
        for i, row in enumerate(srm_only['records'], start=1):
            rel = 'risk-serving-r42' if i <= 18 else 'risk-serving-r39'
            row['assigned_release'] = rel
            row['actual_release'] = rel
            row['converted'] = (i <= 15) if i <= 18 else (i - 18 <= 3)
            row['manual_review_slot_consumed'] = i in {1, 19, 20}
        assert_case(write_variant(tmp, 'srm-only.json', srm_only), fresh_state(tmp, 'srm-only-state.json'), 'invalidate')

        contamination = make_balanced_final(base, 10, 4)
        extra = copy.deepcopy(contamination['records'][0])
        extra['request_id'] = 'cross-variant'
        extra['event_time'] = '2026-08-15T14:59:00Z'
        extra['assigned_release'] = contract['control_release']
        extra['actual_release'] = contract['control_release']
        extra['converted'] = False
        extra['manual_review_slot_consumed'] = False
        contamination['records'].append(extra)
        assert_case(write_variant(tmp, 'contamination.json', contamination), fresh_state(tmp, 'contamination-state.json'), 'invalidate')

        delivery = make_balanced_final(base, 10, 4)
        delivery['records'][0]['actual_release'] = contract['control_release']
        assert_case(write_variant(tmp, 'delivery-mismatch.json', delivery), fresh_state(tmp, 'delivery-state.json'), 'invalidate')

        interference = make_balanced_final(base, 10, 4)
        for i, row in enumerate(interference['records']):
            row['manual_review_slot_consumed'] = i < 9
        assert_case(write_variant(tmp, 'interference.json', interference), fresh_state(tmp, 'interference-state.json'), 'invalidate')

        noise = make_balanced_final(base, 10, 4)
        noise['records'].append({
            'request_id':'outside-noise','event_time':'2026-08-15T13:59:00Z','merchant_id':'merchant-noise-a','eligible':True,
            'eligibility_policy':contract['eligibility_policy'],'assignment_policy':contract['assignment_policy'],
            'assigned_release':contract['candidate_release'],'actual_release':contract['control_release'],
            'outcome_status':'mature','converted':False,'manual_review_slot_consumed':True,
        })
        noise['records'].append({
            'request_id':'ineligible-noise','event_time':'2026-08-15T14:30:00Z','merchant_id':'merchant-noise-b','eligible':False,
            'eligibility_policy':'wrong-policy-is-ignored-because-ineligible','assignment_policy':'wrong-assignment-is-ignored',
            'assigned_release':'unknown','actual_release':'unknown','outcome_status':'pending','converted':None,'manual_review_slot_consumed':True,
        })
        assert_case(write_variant(tmp, 'noise.json', noise), fresh_state(tmp, 'noise-state.json'), 'winner_candidate')

        # Generated order/outcome cases prove request order is irrelevant and threshold logic is not hard-coded.
        for idx in range(4):
            v = make_balanced_final(base, 10, 4)
            rng.shuffle(v['records'])
            if idx % 3 == 0:
                # Valid winner remains a winner under reordering.
                decision = 'winner_candidate'
            elif idx % 3 == 1:
                # Remove lift without changing experiment validity.
                cand_rows = [r for r in v['records'] if r['assigned_release'] == contract['candidate_release']]
                ctrl_rows = [r for r in v['records'] if r['assigned_release'] == contract['control_release']]
                for j, row in enumerate(cand_rows): row['converted'] = j < 7
                for j, row in enumerate(ctrl_rows): row['converted'] = j < 6
                decision = 'no_winner'
            else:
                # High capacity utilization invalidates even statistically strong outcomes.
                for j, row in enumerate(v['records']): row['manual_review_slot_consumed'] = j < 9
                decision = 'invalidate'
            assert_case(write_variant(tmp, f'generated-{idx:02d}.json', v), fresh_state(tmp, f'generated-state-{idx:02d}.json'), decision)

        malformed = []
        wrong_subject = copy.deepcopy(base); wrong_subject['experiment_subject_id'] = 'UNKNOWN'; malformed.append(('wrong-subject.json', wrong_subject))
        incomplete = copy.deepcopy(base); incomplete['completeness_watermark'] = '2026-08-15T14:59:59Z'; malformed.append(('incomplete.json', incomplete))
        wrong_resource = copy.deepcopy(base); wrong_resource['shared_resource_id'] = 'other-pool'; malformed.append(('wrong-resource.json', wrong_resource))
        wrong_policy = copy.deepcopy(base); wrong_policy['records'][0]['assignment_policy'] = 'request-random-v1'; malformed.append(('wrong-policy.json', wrong_policy))
        unknown_release = copy.deepcopy(base); unknown_release['records'][0]['assigned_release'] = 'risk-serving-r999'; malformed.append(('unknown-release.json', unknown_release))
        missing = copy.deepcopy(base); del missing['records'][0]['merchant_id']; malformed.append(('missing-field.json', missing))
        for name, value in malformed:
            run_analyzer(write_variant(tmp, name, value), fresh_state(tmp, 'state-' + name), expect_success=False)

    for name, template in PROTECTED.items():
        if (WORKSPACE / name).read_bytes() != template.read_bytes():
            fail(f'protected experiment evidence changed during validation: {name}')

    print('PASS: experiment analysis binds exact subject evidence, proves stable-unit randomization/SRM/interference integrity, waits for fixed-horizon mature outcomes, and never turns an A/B winner into promotion authority')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f'FAIL: {exc}')
        raise SystemExit(1)
