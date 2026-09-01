#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path


def run(expect_success):
    proc = subprocess.run(['python3', 'monitoring_gate.py'], capture_output=True, text=True)
    if (proc.returncode == 0) != expect_success:
        raise AssertionError(f'unexpected gate result rc={proc.returncode}\n{proc.stdout}\n{proc.stderr}')
    return proc


def write_json(name, payload):
    Path(name).write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')


def clear_outputs():
    Path('monitoring-report.json').unlink(missing_ok=True)
    Path('monitoring-evidence-ledger.json').unlink(missing_ok=True)


run(False)
report = json.loads(Path('monitoring-report.json').read_text())
assert report['accepted'] is False
assert report['monitoring_verified'] is False
assert report['retraining_authorized'] is False
assert report['rollout_authorized'] is False
assert not Path('monitoring-evidence-ledger.json').exists()
print('PASS green HTTP dashboard cannot hide fallback/deadline failure or authorize retraining')

window = json.loads(Path('monitoring-window.json').read_text())
window.update({
    'average_latency_ms': 68,
    'deadline_successes': 995,
    'model_invocations': 995,
    'p95_latency_ms': 120,
})
window['result_class_counts']['model_success'] = 995
window['result_class_counts']['fallback_timeout'] = 5
write_json('monitoring-window.json', window)

drift = json.loads(Path('drift-evidence.json').read_text())
drift.update({
    'actual_exposure_denominator': 1000,
    'actual_exposure_denominator_present': True,
    'current_prediction_events': 995,
    'retraining_requested': False,
    'segment_breakdown_present': True,
})
write_json('drift-evidence.json', drift)

second = json.loads(Path('second-window.json').read_text())
second.update({
    'deadline_successes': 997,
    'duplicate_events': 0,
    'materialized_at': '2026-08-03T09:30:20Z',
    'manual_backfill_required': False,
    'request_correlation_complete': True,
    'telemetry_events': 1000,
})
second['result_class_counts']['model_success'] = 997
second['result_class_counts']['fallback_timeout'] = 3
write_json('second-window.json', second)

clear_outputs()
run(True)
first = Path('monitoring-report.json').read_bytes() + Path('monitoring-evidence-ledger.json').read_bytes()
report = json.loads(Path('monitoring-report.json').read_text())
assert report['monitoring_verified'] is True
assert report['rollout_authorized'] is False
assert report['promotion_authorized'] is False
assert report['retraining_authorized'] is False
run(True)
second_bytes = Path('monitoring-report.json').read_bytes() + Path('monitoring-evidence-ledger.json').read_bytes()
assert first == second_bytes
print('PASS request-correlated monitoring evidence and second window are byte-idempotent')

release = json.loads(Path('release-manifest.json').read_text())
release['runtime_generation'] = 'kserve-v2-r17-tampered'
write_json('release-manifest.json', release)
clear_outputs()
run(False)
assert not Path('monitoring-evidence-ledger.json').exists()
release['runtime_generation'] = 'kserve-v2-r17'
write_json('release-manifest.json', release)
print('PASS release byte tampering is rejected')

drift['actual_exposure_denominator'] = None
drift['actual_exposure_denominator_present'] = False
drift['retraining_requested'] = True
write_json('drift-evidence.json', drift)
clear_outputs()
run(False)
assert not Path('monitoring-evidence-ledger.json').exists()
drift['actual_exposure_denominator'] = 1000
drift['actual_exposure_denominator_present'] = True
drift['retraining_requested'] = False
write_json('drift-evidence.json', drift)
print('PASS drift evidence cannot bypass exposure denominator or retraining authority boundary')

second['manual_backfill_required'] = True
write_json('second-window.json', second)
clear_outputs()
run(False)
assert not Path('monitoring-evidence-ledger.json').exists()
second['manual_backfill_required'] = False
write_json('second-window.json', second)
print('PASS second monitoring window must reproduce without manual backfill')

clear_outputs()
run(True)
Path('monitoring-evidence-ledger.json').write_text('{"conflict":true}\n')
proc = subprocess.run(['python3', 'monitoring_gate.py'], capture_output=True, text=True)
assert proc.returncode != 0
assert Path('monitoring-evidence-ledger.json').read_text() == '{"conflict":true}\n'
print('PASS conflicting durable monitoring state is preserved')
print('VALIDATION PASSED')
