# Python for automation

Python je všeobecný programovací jazyk vhodný pre automatizáciu, ktorá prerástla možnosti shell skriptu alebo potrebuje stabilný dátový model, robustné knižnice, testovateľnosť a prenositeľnosť. Je silný pri práci s API, súbormi, paralelnými úlohami, validáciou dát a orchestration workflowov.

## 1. Kedy použiť Python

Python je vhodný najmä pre:

- HTTP/API klientov,
- spracovanie JSON, YAML, CSV a XML,
- zložitejšie validačné a transformačné pipeline,
- cross-platform CLI nástroje,
- inventory a reporting,
- release a deployment orchestration,
- cloud SDK integrácie,
- paralelné alebo asynchrónne I/O,
- automatizáciu, ktorá má byť dlhodobo testovaná a udržiavaná.

Pre krátke skladanie existujúcich CLI nástrojov môže byť Bash jednoduchší. Pre tesnú integráciu s Windows management stackom môže byť prirodzenejší PowerShell.

## 2. Interpreter a virtual environment

Over verziu:

```bash
python --version
```

Vytvor izolované prostredie:

```bash
python -m venv .venv
```

Aktivácia na Linux/macOS:

```bash
source .venv/bin/activate
```

Aktivácia v PowerShelli:

```powershell
.\.venv\Scripts\Activate.ps1
```

Virtual environment izoluje interpreter-visible dependencies, nie celý operačný systém.

## 3. Reprodukovateľné dependencies

Jednoduchý projekt môže používať `pyproject.toml`:

```toml
[project]
name = "inventory-tool"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "httpx>=0.27,<1",
  "pydantic>=2.8,<3"
]
```

Rozlišuj:

- deklarovaný version range,
- presne vyriešený lockfile,
- runtime environment,
- transitive dependencies.

Samotný `requirements.txt` bez stratégie pinningu a aktualizácie nemusí zaručiť reprodukovateľnosť.

## 4. Project layout

```text
inventory-tool/
├── pyproject.toml
├── src/
│   └── inventory_tool/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       └── api.py
├── tests/
└── README.md
```

`src` layout znižuje riziko, že tests importujú lokálny adresár namiesto nainštalovaného package.

## 5. Entry point

```python
from __future__ import annotations

import sys


def main() -> int:
    try:
        run()
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

`main()` vracia process exit code. `SystemExit` ho odovzdá shellu alebo CI runneru.

## 6. Type hints

```python
from collections.abc import Iterable


def normalize_names(values: Iterable[str]) -> list[str]:
    return sorted({value.strip().lower() for value in values if value.strip()})
```

Type hints nie sú runtime enforcement samy osebe. Pomáhajú static analyzers, IDE a review procesu.

Použiteľné nástroje:

```bash
mypy src
pyright
```

## 7. Dataclasses

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Service:
    name: str
    environment: str
    port: int
```

`frozen=True` obmedzuje mutation a `slots=True` znižuje dynamické attributes. Dataclass nie je automaticky input validator.

## 8. Command-line interface

Štandardná knižnica:

```python
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", choices=["dev", "test", "prod"], required=True)
    parser.add_argument("--dry-run", action="store_true")
    return parser
```

CLI kontrakt má definovať:

- required arguments,
- defaults,
- allowed values,
- exit codes,
- stdout/stderr semantics,
- machine-readable output mode.

## 9. Paths

Používaj `pathlib`:

```python
from pathlib import Path

config_path = Path("config") / "app.json"
content = config_path.read_text(encoding="utf-8")
```

`Path` znižuje platform-specific string manipulation, ale nemení permissions, symlink ani filesystem semantics.

## 10. Atomic file update

```python
from pathlib import Path
import os
import tempfile


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
    ) as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
        temp_path = Path(handle.name)

    temp_path.replace(path)
```

`replace()` je typicky atomický iba v rámci jedného filesystemu. Ak je dôležitá durability po power loss, treba riešiť aj fsync adresára a konkrétne filesystem semantics.

## 11. JSON

```python
import json
from pathlib import Path


data = json.loads(Path("input.json").read_text(encoding="utf-8"))
output = json.dumps(data, indent=2, sort_keys=True)
```

Nezamieňaj:

- absent key,
- key s hodnotou `null`,
- empty string,
- empty list,
- `0` alebo `false`.

## 12. HTTP requests

Príklad s `httpx`:

```python
import httpx


def fetch_service(url: str, token: str) -> dict[str, object]:
    headers = {"Authorization": f"Bearer {token}"}
    timeout = httpx.Timeout(10.0, connect=3.0)

    with httpx.Client(timeout=timeout, headers=headers) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.json()
```

Definuj samostatne:

- connect timeout,
- read timeout,
- write timeout,
- pool timeout,
- retry policy,
- idempotency,
- rate limiting,
- TLS verification.

Nezapínaj retries bez rozlíšenia idempotentných a ne-idempotentných operácií.

## 13. Exceptions

```python
class ConfigurationError(ValueError):
    pass


def load_port(raw: str) -> int:
    try:
        port = int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"invalid port: {raw!r}") from exc

    if not 1 <= port <= 65535:
        raise ConfigurationError(f"port out of range: {port}")
    return port
```

Zachovaj exception chaining cez `raise ... from exc`, aby root cause nezmizla.

Nezachytávaj všeobecné `Exception` hlboko bez recovery stratégie.

## 14. Logging

```python
import logging

logger = logging.getLogger(__name__)


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s level=%(levelname)s logger=%(name)s message=%(message)s",
    )
```

Loguj:

- operation identity,
- target,
- duration,
- result,
- retry count,
- correlation ID.

Neloguj secrets, celé tokens alebo sensitive payloady.

## 15. Configuration

Konfigurácia môže pochádzať z:

- CLI arguments,
- environment variables,
- config files,
- secret managera,
- service discovery.

Definuj precedence explicitne:

```text
CLI > environment > config file > defaults
```

Neskladaj konfiguráciu implicitne z desiatok globálnych reads počas runtime.

## 16. Environment variables

```python
import os

api_url = os.environ.get("API_URL", "https://api.example.com")
token = os.environ["API_TOKEN"]
```

`os.environ[...]` zlyhá pri chýbajúcej required hodnote. `.get()` je vhodné pre optional hodnoty s vedomým defaultom.

Environment nie je secret manager a môže byť viditeľný v process alebo diagnostic kontexte.

## 17. Subprocesses

```python
import subprocess


def git_head() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()
```

Používaj argument list, nie shell string.

Nebezpečné:

```python
subprocess.run(f"tool {user_input}", shell=True)
```

`check=True` zmení non-zero exit status na exception. Pri veľkom outpute zváž streaming namiesto `capture_output=True`.

## 18. Temporary files

```python
from tempfile import TemporaryDirectory
from pathlib import Path

with TemporaryDirectory() as directory:
    workdir = Path(directory)
    # temporary workflow
```

Context manager zabezpečuje cleanup pri bežnom aj exception flow. Pri potrebe incidentnej analýzy môže byť vhodné temp artifacts po chybe zachovať kontrolovaným režimom.

## 19. Context managers

```python
from contextlib import contextmanager
from collections.abc import Iterator


@contextmanager
def operation(name: str) -> Iterator[None]:
    logger.info("operation started", extra={"operation": name})
    try:
        yield
    except Exception:
        logger.exception("operation failed", extra={"operation": name})
        raise
    else:
        logger.info("operation completed", extra={"operation": name})
```

Context manager je vhodný pre lifecycle resources: files, locks, sessions, transactions a temporary state.

## 20. Idempotencia

```python
def ensure_directory(path: Path) -> bool:
    if path.is_dir():
        return False
    path.mkdir(parents=True, exist_ok=True)
    return True
```

Dobrá automation funkcia často vracia, či stav zmenila.

Rozlišuj:

- plan,
- apply,
- verify,
- rollback alebo compensation.

## 21. Retry

Retry má byť ohraničený a pozorovateľný:

```python
import random
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def retry(operation: Callable[[], T], attempts: int = 4) -> T:
    delay = 0.5
    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except TimeoutError:
            if attempt == attempts:
                raise
            time.sleep(delay + random.uniform(0, delay * 0.2))
            delay *= 2
    raise AssertionError("unreachable")
```

Retry iba transient errors. Definuj maximum attempts, deadline, backoff, jitter a idempotency.

## 22. Concurrency

### Threads

Vhodné najmä pre blocking I/O:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(fetch_item, item_ids))
```

### Processes

Vhodné pre CPU-bound workload, ale s serialization overheadom a oddelenou memory.

### Asyncio

Vhodné pre veľké množstvo concurrent I/O, ak knižnice podporujú async model.

Concurrency limit je súčasť failure control. Neobmedzené paralelné API requests môžu spôsobiť rate limit alebo incident.

## 23. Signals a shutdown

```python
import signal
import threading

stop_event = threading.Event()


def request_stop(signum: int, frame: object) -> None:
    stop_event.set()

signal.signal(signal.SIGTERM, request_stop)
signal.signal(signal.SIGINT, request_stop)
```

Graceful shutdown má:

- zastaviť prijímanie novej práce,
- dokončiť alebo bezpečne prerušiť rozpracovanú prácu,
- uvoľniť locks a sessions,
- flushnúť logy,
- vrátiť správny exit code.

## 24. File locking

Štandardná knižnica neposkytuje jednotný high-level cross-platform file lock. Použi platform-specific mechanizmus alebo overenú knižnicu a definuj failure semantics.

Lock nie je distribuovaný coordination mechanizmus medzi hostmi.

## 25. Testing s pytest

```python
from pathlib import Path


def test_atomic_write(tmp_path: Path) -> None:
    target = tmp_path / "config.txt"
    atomic_write(target, "value\n")
    assert target.read_text(encoding="utf-8") == "value\n"
```

Testuj:

- invalid input,
- network timeout,
- retry exhaustion,
- partial write,
- repeated execution,
- interruption,
- missing dependency,
- platform differences,
- dry-run,
- logging redaction.

## 26. Mocking

Mockuj boundary, nie implementačné detaily.

Príklady boundaries:

- HTTP transport,
- filesystem adapter,
- clock,
- random source,
- subprocess runner,
- secret provider.

Príliš veľa mocks môže vytvoriť testy, ktoré dokazujú iba vlastné predpoklady.

## 27. Static analysis a formatting

```bash
ruff check .
ruff format --check .
mypy src
pytest
```

Rozumný quality gate môže obsahovať:

- lint,
- formatting,
- type checking,
- unit tests,
- dependency audit,
- package build.

## 28. Packaging CLI

`pyproject.toml`:

```toml
[project.scripts]
inventory-tool = "inventory_tool.cli:main"
```

Po inštalácii package vznikne executable entry point. To je stabilnejšie než spoliehanie sa na current working directory a `python script.py`.

## 29. Security

Riziká:

- unsafe deserialization,
- command injection cez `shell=True`,
- path traversal,
- SSRF pri neoverených URLs,
- TLS verification disable,
- secrets v logs,
- dependency confusion alebo typosquatting,
- neobmedzené file permissions,
- nekontrolovaný archive extraction.

Pri archive extraction over, že výsledná path zostáva v cieľovom adresári.

## 30. Produkčný skeleton

```python
from __future__ import annotations

import argparse
import logging
import sys

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment", required=True, choices=["dev", "test", "prod"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def run(environment: str, dry_run: bool) -> None:
    plan = build_plan(environment)
    validate_plan(plan)

    if dry_run:
        print(render_plan(plan))
        return

    apply_plan(plan)
    verify_postconditions(plan)


def main() -> int:
    args = parse_args()
    configure_logging(args.verbose)

    try:
        run(args.environment, args.dry_run)
    except KeyboardInterrupt:
        logger.warning("interrupted")
        return 130
    except ConfigurationError as exc:
        logger.error("configuration error: %s", exc)
        return 2
    except Exception:
        logger.exception("automation failed")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

## 31. Troubleshooting

### Funguje lokálne, ale nie v CI

Skontroluj:

- Python version,
- dependency lock,
- working directory,
- environment variables,
- filesystem permissions,
- locale a timezone,
- network egress,
- certificate trust store.

### Importuje sa nesprávny modul

```bash
python -c "import package; print(package.__file__)"
python -m pip show package
```

Over aktívny interpreter a virtual environment.

### Skript visí

Kontroluj:

- chýbajúce timeouts,
- deadlock,
- blocking I/O v async loop-e,
- neukončené thread/process pools,
- subprocess pipe buffer,
- DNS alebo TLS timeout.

### Pamäť rastie

Sleduj:

- unbounded collections,
- celý súbor načítaný do memory,
- cache bez eviction,
- retained references,
- príliš veľký captured subprocess output.

## 32. Časté omyly

### „Python skript je automaticky cross-platform“

Nie. External commands, paths, signals, permissions a encoding sa líšia.

### „Retry vyrieši každé zlyhanie“

Nie. Permanent error iba predĺži failure a môže znásobiť side effects.

### „Type hints validujú runtime vstup“

Nie bez explicitnej validácie alebo validačnej knižnice.

### „Exception treba zachytiť čo najskôr“

Nie. Zachyť ju tam, kde vieš pridať kontext, vykonať recovery alebo mapovať error na boundary contract.

## 33. Kontrolné otázky

1. Kedy je Python vhodnejší než Bash alebo PowerShell?
2. Aký je rozdiel medzi deklarovaným dependency range a lockfile?
3. Prečo je `src` layout užitočný?
4. Ako navrhneš stabilný CLI contract a exit codes?
5. Prečo používať argument list v `subprocess.run()`?
6. Aké podmienky musí spĺňať bezpečný retry?
7. Kedy použiť threads, processes alebo asyncio?
8. Ako navrhneš graceful shutdown?
9. Aký je rozdiel medzi mockovaním boundary a implementačných detailov?
10. Ako overíš idempotenciu automation workflowu?

## Glossary impact

Relevantné pojmy: virtual environment, dependency lock, package, entry point, type hint, dataclass, context manager, exception chaining, atomic write, retry budget, exponential backoff, jitter, thread pool, process pool, asyncio, graceful shutdown, boundary mock a path traversal.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: PowerShell fundamentals](powershell-fundamentals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: YAML, JSON a regular expressions →](yaml-json-regular-expressions.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
