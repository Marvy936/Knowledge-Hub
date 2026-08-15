#!/usr/bin/env python3
import hashlib
import json
import math
import os
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path("/workspace")
LAB_ROOT = Path(os.environ["LAB_ROOT"])
CONTRACT_PATH = ROOT / "feature_contract.json"
OFFLINE_SCRIPT = ROOT / "offline_transform.py"
SERVING_SCRIPT = ROOT / "serving_transform.py"


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text())


def run_transform(script: Path, record):
    try:
        completed = subprocess.run(
            ["python3", str(script)],
            input=json.dumps(record),
            text=True,
            capture_output=True,
            cwd=ROOT,
            timeout=5,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return 124, None, "transform timed out"

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        return completed.returncode, None, detail

    try:
        return 0, json.loads(completed.stdout), ""
    except json.JSONDecodeError:
        return 3, None, "transform did not emit one valid JSON object"


def expected_vector(record, contract):
    amount_rule = contract["rules"]["amount_eur"]
    velocity_rule = contract["rules"]["merchant_velocity_eur_7d"]
    border_rule = contract["rules"]["cross_border"]

    amount = round(
        record["amount_minor"] / amount_rule["minor_units_per_major"],
        amount_rule["round_digits"],
    )
    velocity = round(
        record["merchant_velocity_minor_7d"] / velocity_rule["minor_units_per_major"],
        velocity_rule["round_digits"],
    )
    customer = record["customer_country"].strip().upper()
    merchant = record["merchant_country"].strip().upper()
    if not customer or not merchant:
        border = border_rule["unknown_value"]
    else:
        border = int(customer != merchant)
    return [amount, velocity, border]


def vectors_equal(actual, expected):
    if not isinstance(actual, list) or len(actual) != len(expected):
        return False
    for index, (left, right) in enumerate(zip(actual, expected)):
        if index == 2:
            if isinstance(left, bool) or type(left) is not int or left != right:
                return False
        else:
            if isinstance(left, bool) or not isinstance(left, (int, float)):
                return False
            if not math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-9):
                return False
    return True


def valid_metadata(output, operation_id, contract, contract_digest):
    return (
        isinstance(output, dict)
        and output.get("operation_id") == operation_id
        and output.get("contract_id") == contract["contract_id"]
        and output.get("contract_sha256") == contract_digest
        and output.get("schema_id") == contract["schema_id"]
        and output.get("feature_order") == contract["feature_order"]
    )


def print_result(ok, message):
    marker = "PASS" if ok else "FAIL"
    print(f"[{marker}] {message}")


def main():
    protected = [
        (ROOT / "feature_contract.json", LAB_ROOT / "feature_contract.json.template"),
        (ROOT / "feature_runtime.py", LAB_ROOT / "feature_runtime.py.template"),
        (ROOT / "offline_transform.py", LAB_ROOT / "offline_transform.py.template"),
        (ROOT / "matched-requests.json", LAB_ROOT / "matched-requests.json.template"),
    ]
    fixture_integrity = all(
        current.exists() and template.exists() and sha256(current) == sha256(template)
        for current, template in protected
    )
    print_result(fixture_integrity, "Canonical contract, offline path and incident evidence are unchanged")
    if not fixture_integrity:
        print("\nLAB NOT COMPLETE")
        print("Restore the protected fixtures with 'reset'; repair only serving_transform.py.")
        return 1

    contract = load_json(CONTRACT_PATH)
    contract_digest = sha256(CONTRACT_PATH)
    matched = load_json(ROOT / "matched-requests.json")

    rng = random.Random(2307)
    countries = ["SK", " sk ", "CZ", "cz", "DE", " de ", "AT", "", " PL "]
    generated = []
    for index in range(24):
        generated.append(
            {
                "operation_id": f"generated-{index:02d}",
                "amount_minor": rng.randint(0, 5_000_000),
                "merchant_velocity_minor_7d": rng.randint(0, 250_000_000),
                "customer_country": rng.choice(countries),
                "merchant_country": rng.choice(countries),
            }
        )

    valid_records = matched + generated
    baseline_ok = True
    baseline_errors = []
    for record in valid_records:
        rc, output, detail = run_transform(OFFLINE_SCRIPT, record)
        expected = expected_vector(record, contract)
        if (
            rc != 0
            or not valid_metadata(output, record["operation_id"], contract, contract_digest)
            or not vectors_equal(output.get("vector") if isinstance(output, dict) else None, expected)
        ):
            baseline_ok = False
            baseline_errors.append(f"{record['operation_id']}: {detail or 'offline result diverged from contract'}")
            if len(baseline_errors) >= 3:
                break
    print_result(baseline_ok, "Offline training path matches the canonical feature contract")
    if not baseline_ok:
        for detail in baseline_errors:
            print("  ", detail)
        print("\nLAB NOT COMPLETE")
        print("The protected offline baseline is invalid; use 'reset'.")
        return 1

    identity_ok = True
    schema_ok = True
    value_ok = True
    serving_errors = []
    for record in valid_records:
        rc, output, detail = run_transform(SERVING_SCRIPT, record)
        if rc != 0 or not isinstance(output, dict):
            identity_ok = False
            schema_ok = False
            value_ok = False
            serving_errors.append(f"{record['operation_id']}: {detail or 'serving transform failed'}")
            if len(serving_errors) >= 4:
                break
            continue

        if not (
            output.get("operation_id") == record["operation_id"]
            and output.get("contract_id") == contract["contract_id"]
            and output.get("contract_sha256") == contract_digest
        ):
            identity_ok = False
            if len(serving_errors) < 4:
                serving_errors.append(f"{record['operation_id']}: serving is not bound to the exact contract bytes")

        if not (
            output.get("schema_id") == contract["schema_id"]
            and output.get("feature_order") == contract["feature_order"]
        ):
            schema_ok = False
            if len(serving_errors) < 4:
                serving_errors.append(f"{record['operation_id']}: schema/order mismatch")

        expected = expected_vector(record, contract)
        if not vectors_equal(output.get("vector"), expected):
            value_ok = False
            if len(serving_errors) < 4:
                serving_errors.append(
                    f"{record['operation_id']}: serving vector {output.get('vector')} != training vector {expected}"
                )

    print_result(identity_ok, "Serving reports the exact feature contract ID and SHA-256")
    print_result(schema_ok, "Serving preserves the training schema and feature order")
    print_result(value_ok, "Matched and generated serving vectors equal the offline training representation")

    invalid_records = [
        {
            "operation_id": "invalid-string-amount",
            "amount_minor": "12345",
            "merchant_velocity_minor_7d": 100,
            "customer_country": "SK",
            "merchant_country": "SK",
        },
        {
            "operation_id": "invalid-missing-velocity",
            "amount_minor": 12345,
            "customer_country": "SK",
            "merchant_country": "SK",
        },
        {
            "operation_id": "invalid-bool-amount",
            "amount_minor": True,
            "merchant_velocity_minor_7d": 100,
            "customer_country": "SK",
            "merchant_country": "SK",
        },
        {
            "operation_id": "invalid-negative-velocity",
            "amount_minor": 12345,
            "merchant_velocity_minor_7d": -1,
            "customer_country": "SK",
            "merchant_country": "SK",
        },
        {
            "operation_id": "",
            "amount_minor": 12345,
            "merchant_velocity_minor_7d": 100,
            "customer_country": "SK",
            "merchant_country": "SK",
        },
        {
            "operation_id": "invalid-country-type",
            "amount_minor": 12345,
            "merchant_velocity_minor_7d": 100,
            "customer_country": 703,
            "merchant_country": "SK",
        },
    ]

    invalid_ok = True
    for record in invalid_records:
        offline_rc, _, _ = run_transform(OFFLINE_SCRIPT, record)
        serving_rc, _, _ = run_transform(SERVING_SCRIPT, record)
        if offline_rc == 0:
            print("[FAIL] Offline baseline unexpectedly accepted malformed input")
            return 1
        if serving_rc == 0:
            invalid_ok = False
            if len(serving_errors) < 4:
                serving_errors.append(f"{record.get('operation_id')!r}: serving silently accepted malformed input")
    print_result(invalid_ok, "Serving rejects the same malformed input classes as training")

    complete = identity_ok and schema_ok and value_ok and invalid_ok
    if complete:
        print("\nLAB COMPLETED")
        return 0

    if serving_errors:
        print("\nFirst observed divergences:")
        for detail in serving_errors[:4]:
            print("  -", detail)
    print("\nLAB NOT COMPLETE")
    print("Repair serving_transform.py so it consumes the exact feature contract and reproduces training semantics.")
    print("Use 'hint' for progressive guidance.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
