# Python for automation

Keď automatizácia potrebuje schema validation, typed state, viac krokov, retries a testovateľnú domain logiku, Python je vhodnejší než rastúci shell script. Atlas `atlasctl` nevolá API naslepo. Najprv načíta desired config a observed state, vytvorí fingerprintovaný plan, pri apply overí stale-plan preconditions, vykoná atomic write a následne samostatne overí outcome.

## CLI boundary

```python
from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="atlasctl")
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan")
    plan.add_argument("--config", required=True)
    plan.add_argument("--state", required=True)

    apply_cmd = sub.add_parser("apply")
    apply_cmd.add_argument("--config", required=True)
    apply_cmd.add_argument("--state", required=True)
    apply_cmd.add_argument("--plan", required=True)

    verify = sub.add_parser("verify")
    verify.add_argument("--config", required=True)
    verify.add_argument("--state", required=True)
    return parser
```

Parser rieši syntax a required arguments. Domain validation patrí do samostatných functions, aby sa dala testovať bez process exit-u.

## Typed immutable model

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class OrdersConfig:
    service: str
    environment: str
    release: str
    max_order_amount: int
    currency: str
```

Frozen dataclass obmedzí náhodnú mutation po validation. Parser explicitne mapuje external keys a odmieta unknown alebo missing fields podľa contractu. Type hints nie sú runtime validation; treba vykonať checks.

## Canonical fingerprint

```python
import hashlib
import json


def fingerprint(value: object) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
```

Canonicalization musí byť definovaná. Hash raw YAML textu by sa zmenil pri komentári alebo whitespace, hoci domain state zostal rovnaký. Naopak semantic fingerprint môže zámerne ignorovať presentation differences.

## Plan subject

Plan obsahuje:

```json
{
  "schemaVersion": 1,
  "desiredFingerprint": "...",
  "observedFingerprint": "...",
  "changes": {
    "maxOrderAmount": {"from": 4000, "to": 5000}
  }
}
```

Apply musí znovu načítať config aj state a porovnať oba fingerprints. Ak sa medzi planom a apply zmenil ktorýkoľvek vstup, plan je stale a mutation sa odmietne. To je optimistická concurrency control hranica.

## Atomic local write

```python
import os
import tempfile
from pathlib import Path


def atomic_write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, sort_keys=True, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)
```

Atomic rename chráni pred partial file contentom na rovnakom filesysteme. Nezaručuje distribuovanú transakciu s ďalším systémom. Directory fsync alebo platform-specific durability môže byť potrebná pri silnejšom crash contracte.

## Lock a concurrency

Linux local tool môže použiť `fcntl.flock`. Cross-platform implementácia potrebuje inú library alebo OS abstraction. Lock acquisition má timeout a jasný owner diagnostic.

Lock sa drží cez observation recheck, mutation a local verification. Ak sa observed state číta pred lockom a apply ho už nekontroluje, dva procesy môžu použiť stale plans.

## HTTP clients, timeout a retry

Production automation musí uviesť connect aj read/total timeout. Infinite default timeout môže zablokovať pipeline. Retry sa používa iba na transient classes a bezpečné operations.

```python
# pseudocode contract
for attempt in retry_policy:
    try:
        return call(timeout=deadline.remaining())
    except RetryableError:
        retry_policy.sleep(attempt, deadline)
```

Deadline sa prenáša cez všetky pokusy. Retry count bez total budgetu môže prekročiť job SLA. Mutating request potrebuje idempotency key alebo operation status lookup, aby unknown outcome nevytvoril duplicate side effect.

## Structured logging

Logs majú stable event name a fields:

```python
logger.info(
    "apply_verified",
    extra={
        "environment": config.environment,
        "desired_fingerprint": desired_fp,
        "changed": changed,
    },
)
```

Secret values sa redigujú pred logging boundary. Stack trace patrí k unexpected erroru; expected invalid input má jasnú message a exit code bez zbytočného tracebacku.

## Exit codes a exceptions

Domain exceptions možno mapovať:

```text
2 invalid input
3 precondition alebo stale plan
4 mutation failure
5 verification failure
```

Top-level `main()` zachytí očakávané errors, zapíše diagnostic na stderr a vráti code. Neočakávaná exception môže ponechať traceback a odlišný internal-error code. `sys.exit(main())` je jediný process boundary.

## Testovateľnosť

Filesystem, clock, HTTP client a environment access sa injectujú alebo izolujú. Unit test vytvorí temporary directory a testuje:

```text
valid plan
stale desired config
stale observed state
atomic apply
second no-op apply
invalid schema
verification drift
```

Test nemá volať production endpoint ani závisieť od user home configuration.

## Graceful cancellation

Long-running automation reaguje na SIGINT/SIGTERM. Pri lokálnej atomic mutation možno cancellation prijať pred apply alebo po completed write a verify. Pri external operation môže outcome zostať unknown; tool má uložiť operation ID a inštrukciu na status reconciliation.

„Rollback“ nie je automatický univerzálny krok. Ak downstream side effect prebehol, slepé inverse volanie môže zhoršiť stav. Recovery sa riadi domain contractom.

## Incident: retry vytvorí dvojitý rollout

Python client odosiela mutating POST, connection timeoutne po tom, čo server request prijme. Generic retry odošle druhý request bez idempotency key. Server vytvorí dva rollout records.

Oprava používa stable operation key, status endpoint a deadline-aware retry iba pred známym acceptance boundary. Tests simulujú timeout po commit-e a overia jeden effective rollout. Transport exception sa už neinterpretuje ako „nič sa nestalo“.

## Zhrnutie

Python umožňuje oddeliť CLI, parsing, domain model, planning, mutation a verification. Bezpečný tool používa canonical fingerprints, stale-plan protection, atomic writes, bounded retries, stable exit codes a injected dependencies. Úspešné API volanie nie je finálny verdict; outcome sa overuje samostatným read-backom.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: PowerShell fundamentals](powershell-fundamentals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: YAML, JSON a regular expressions →](yaml-json-regular-expressions.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
