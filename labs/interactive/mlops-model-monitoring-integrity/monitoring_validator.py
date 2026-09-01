#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path


def run(expect_success):
    proc = subprocess.run(['python3', 'monitoring_gate.py'], capture_output=True, text=True)
    if (proc.returncode == 0) != expect_success:
        raise AssertionError(f'unexpected gate result rc={proc.returncode}\n{proc.stdout}\n{proc.stderr}')
    return proc


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
Path('monitoring-window.json').write_text(json.dumps(window, indent=2, sort_keys=True) + '\n')

drift = json.loads(Path('drift-evidence.json').read_text())
drift.update({
    'actual_exposure_denominator': 1000,
    'actual_exposure_denominator_present': True,
    'current_prediction_events': 995,
    'retraining_requested': False,
    'segment_breakdown_present': True,
})
Path('drift-evidence.json').write_text(json.dumps(drift, indent=2, sort_keys=True) + '\n')

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
Path('second-window.json').write_text(json.dumps(second, indent=2, sort_keys=True) + '\n')

Path('monitoring-report.json').unlink(missing_ok=True)
Path('monitoring-evidence-ledger.json').unlink(missing_ok=True)
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

Path('monitoring-evidence-ledger.json').write_text('{"conflict":true}\n')
proc = subprocess.run(['python3', 'monitoring_gate.py'], capture_output=True, text=True)
assert proc.returncode != 0
assert Path('monitoring-evidence-ledger.json').read_text() == '{"conflict":true}\n'
print('PASS conflicting durable monitoring state is preserved')
print('VALIDATION PASSED')
