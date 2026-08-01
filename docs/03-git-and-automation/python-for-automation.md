# Python for automation

Python je všeobecný programovací jazyk vhodný pre automatizáciu, keď workflow potrebuje bohatší dátový model, HTTP alebo cloud SDK, concurrency, testovateľnosť a presné error handling. Výhodou nie je iba čitateľnejšia syntax; dôležité je, že domain logiku možno oddeliť od I/O a testovať ako čisté funkcie.

Dobrá automatizačná aplikácia oddeľuje vrstvy:

```text
CLI parsing
→ configuration loading
→ domain validation
→ observation adapter
→ planning
→ mutation adapter
→ verification
→ result serialization
```

Configuration sa načíta raz a prevedie na typed alebo aspoň validovaný immutable domain model. Functions nemajú potichu čítať environment variables z rôznych miest, pretože vznikajú skryté inputs a nepredvídateľné tests.

Plan má presne pomenovať subject a expected current state. Pri apply sa current state znovu observe-ne a porovná s plan precondition. Tým sa odhalí stale plan alebo concurrent writer. Mutation result sa nesmie automaticky zameniť za effective-state verification.

Retries patria iba na operations s jasným timeout a idempotency contractom. Network timeout môže mať unknown outcome: server mutation dokončil, ale client response nedostal. Blind retry môže vytvoriť duplicate. Používa sa idempotency key, operation lookup alebo reconciliation.

Exceptions sa zachytávajú na hranici, ktorá ich vie preložiť na stabilný result alebo vykonať recovery. `except Exception: pass` ničí evidence. CLI má definovať exit codes a písať machine-readable result na stdout, diagnostics na stderr.

Atomic local write typicky vytvorí temporary file v rovnakom filesystéme, flushne a podľa durability požiadavky fsyncne data, potom použije `os.replace`. Pri remote systéme atomicitu určuje jeho API, conditional update alebo transaction model.

Packaging a dependencies sú súčasťou reproducibility. Skript, ktorý „funguje na mojom Pythone“, nemá stabilný runtime contract. Pinning, virtual environment alebo packaged executable musí byť spojený s testovanou interpreter a dependency verziou.

Keď automatizácia potrebuje schema validation, typed state, viac krokov, retries a testovateľnú domain logiku, Python je vhodnejší než rastúci shell script. Atlas `atlasctl` nevolá API naslepo. Najprv načíta desired config a observed state, vytvorí fingerprintovaný plan, pri apply overí stale-plan preconditions, vykoná atomic write a následne samostatne overí outcome.

## CLI boundary

CLI boundary prevádza process argument vector na syntakticky rozpoznaný command model a určuje, ktoré chyby patria callerovi. `argparse` môže potvrdiť prítomnosť options a vybrať subcommand, ale path ešte nie je canonical subject a string hodnota ešte nie je validný domain limit. Parser output sa preto odovzdá samostatnej resolution a validation vrstve namiesto priamej mutation.

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

Typed domain model oddeľuje external representation od state-u, nad ktorým planning a verification skutočne rozhodujú. Loader musí najprv odmietnuť unknown fields, konvertovať hodnoty a overiť invariants; až potom vytvorí model. `frozen=True` chráni pred bežnou neskoršou assignment mutation, ale nenahrádza runtime validation ani deep immutability nested structures.

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

Fingerprint má identifikovať presne definovaný semantic subject, nie náhodnú textovú presentation. Automation najprv zostaví canonical representation so stabilným field setom, orderingom, encodingom a number semantics a až potom hashne výsledné bytes. Rovnaký digest dokazuje zhodu podľa tohto canonicalization contractu; nedokazuje pravdivosť inputu ani runtime aplikovanie state-u.

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

Atomic local write oddeľuje prípravu nového obsahu od okamihu, keď sa stane viditeľným pod production pathname. Temporary file sa vytvorí na rovnakom filesysteme, úplne zapíše a flushne; `os.replace` potom jednou pathname transition nahradí target. Tento model bráni readers vidieť partial serialization, ale jeho crash durability, ownership, mode a následné runtime načítanie zostávajú samostatnými contracts.

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

## Mechanický rozbor Python automation ukážok

Nasledujúce rozbory spájajú skrátené ukážky s reálnym Python execution modelom. Pri každom vzore sledujú vznik objektu alebo file descriptoru, ownership a exception boundary, presnú mutation a read-back, ktorý výsledok potvrdzuje. Zároveň pomenúvajú to, čo lokálne úspešné volanie nepreukazuje pri concurrent writerovi, power loss, remote API alebo novej tool generation.

### Parser vytvára syntaktický model, nie validný domain object

```python
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="atlasctl")
    sub = parser.add_subparsers(dest="command", required=True)
```

Function vytvorí nový parser pri každom volaní, čo zjednodušuje tests. `dest="command"` uloží zvolený subcommand do namespace a `required=True` odmietne prázdne CLI. `parse_args()` pri chybe štandardne vypíše diagnostic a vyvolá `SystemExit(2)`. Preto domain unit testy nemajú byť schované priamo v parser actions; parser testuje syntax, domain functions hodnoty.

Path argument ako `str` ešte nie je canonical path ani existujúci file. Po parse sa vykoná explicitný resolve, allowed-root check a read pod lockom podľa risku.

### Frozen dataclass

```python
@dataclass(frozen=True)
class OrdersConfig:
    service: str
    environment: str
    release: str
    max_order_amount: int
    currency: str
```

Dataclass vygeneruje `__init__`, equality a representation. `frozen=True` blokuje bežné assignmenty na fields po vytvorení, ale nerobí deep immutability, ak field obsahuje mutable list/dict. Type annotations nekontrolujú runtime input; `OrdersConfig(max_order_amount="five")` sa bez vlastnej validation vytvorí.

Bezpečný loader najprv parse-ne external data, odmietne unknown keys, explicitne skonvertuje typy a overí invariants. Až potom vytvorí dataclass. Equality je užitočná pre plan/no-op tests.

### Canonical fingerprint krok po kroku

```python
encoded = json.dumps(
    value,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
).encode("utf-8")
return hashlib.sha256(encoded).hexdigest()
```

`sort_keys=True` stabilizuje object key order. Compact separators odstránia presentation whitespace. `ensure_ascii=False` zachová Unicode characters a následné UTF-8 encoding je explicitné. SHA-256 potom identifikuje presné canonical bytes.

Toto nie je univerzálny JSON canonicalization štandard. Floats, Decimals, negative zero, Unicode normalization a custom objects potrebujú presný contract. Pre money používaj integer minor units alebo decimal string. Fingerprint má obsahovať iba state, ktorého zmena má invalidovať plan.

Pri apply porovnaj tri identities:

```text
plan.desiredFingerprint == freshly loaded desired
plan.observedFingerprint == freshly observed current state
plan.tool/schema generation == current implementation contract
```

Chýbajúca tretia väzba umožní starému planu prejsť po zmene planning semantics.

### Atomic write detailne

```python
fd, temp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
temp = Path(temp_name)
```

`mkstemp` atomicky vytvorí file a vráti otvorený OS descriptor aj pathname. Je bezpečnejší než `NamedTemporaryFile` v niektorých Windows replace scenároch a než predvídateľné meno. Directory je rovnaký ako target, aby `os.replace` neprekročil filesystem boundary.

```python
with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
```

`fdopen` prenesie ownership descriptoru file objectu; context manager ho zavrie. Ak exception nastane pred `fdopen`, treba descriptor explicitne zavrieť — production helper môže mať ešte širší try/finally než skrátená ukážka.

`flush()` presunie Python userspace buffer do OS. `os.fsync()` žiada persistenciu file data/metadata podľa filesystem contractu. `os.replace(temp, path)` atomicky zmení directory entry z pohľadu readers na podporovanom filesysteme a prepíše existujúci target.

Pre crash durability po rename môže byť potrebný fsync parent directory. Atomic visibility neznamená durable commit po power loss. ACL/owner/mode nového file-u tiež nemusia automaticky kopírovať target; nastav ich pred replace alebo použi platformový contract.

`finally: temp.unlink(missing_ok=True)` odstráni leftover temp file. Po úspešnom replace temp pathname už neexistuje, takže je to no-op. Cleanup exception nemá prekryť primary mutation error bez diagnostic policy.

### Exceptions na správnej vrstve

```python
try:
    config = load_config(path)
except json.JSONDecodeError as error:
    raise InvalidConfiguration(f"invalid JSON at line {error.lineno}") from error
```

Lower adapter preloží parser-specific exception na domain error a zachová cause cez `from error`. Top-level `main` mapuje `InvalidConfiguration` na exit 2 a píše bounded diagnostic na stderr. Neočakávanú exception neprehltí; traceback je evidence pre tool defect.

```python
def main() -> int:
    try:
        return run_command(...)
    except InvalidConfiguration as error:
        print(str(error), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
```

Functions pod `main` nemajú volať `sys.exit`, pretože by komplikovali unit tests a cleanup.

### Retry a unknown outcome

Retry loop musí používať absolute deadline:

```python
deadline = time.monotonic() + 30.0
for attempt in range(1, 4):
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise DeadlineExceeded()
    try:
        return client.create_rollout(
            operation_id=operation_id,
            timeout=min(5.0, remaining),
        )
    except RetryableTransportError:
        if attempt == 3:
            raise
        time.sleep(min(2 ** (attempt - 1), max(0.0, deadline - time.monotonic())))
```

`time.monotonic()` nie je ovplyvnený wall-clock adjustmentom. Stabilný `operation_id` je rovnaký cez všetky pokusy. Transport exception po send/commit boundary nevie povedať, či server mutation vykonal; client má najprv query-nuť operation status alebo rely-nuť na server deduplication.

Retry iba na status/error classes označené ako transient. Validation, authorization a precondition failure sa retryom spravidla neopraví a môže zbytočne zaťažovať dependency.

### Dependency injection v teste

Namiesto globálneho `requests`/clock/filesystemu:

```python
def apply_plan(plan: Plan, client: RolloutClient, clock: Clock) -> Result:
    ...
```

Test dodá fake client, ktorý zaznamená calls a simuluje timeout po commite. Fake musí implementovať rovnaký behavior contract, nie iba vracať pohodlný success. Integration test s reálnym sandbox API potom kontroluje adapter a serialization boundary.

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
