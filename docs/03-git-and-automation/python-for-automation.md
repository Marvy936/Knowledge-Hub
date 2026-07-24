# Python for automation

Python je všeobecný programovací jazyk vhodný pre automatizáciu, ktorá potrebuje stabilný dátový model, testovateľnosť, rozsiahle knižnice alebo dlhodobú údržbu. Oproti shell skriptu pridáva jasnejšie typové a modulové hranice, robustnejší error model a jednoduchšie testovanie. Stále však automaticky nezaručuje prenositeľnosť, idempotenciu ani bezpečnosť.

## 1. Mentálny model

Produkčný automatizačný nástroj je vhodné chápať ako riadený lifecycle:

```text
process invocation
  ↓
parse a validate inputs
  ↓
load configuration and credentials
  ↓
discover current state
  ↓
build deterministic plan
  ↓
apply bounded mutations
  ↓
verify postconditions
  ↓
emit structured result and exit code
  ↓
cleanup resources
```

Najdôležitejšie hranice sú:

- **input boundary** — CLI, environment, súbory a vzdialené API vstupy sa musia validovať,
- **planning boundary** — nástroj má vedieť vysvetliť, čo zamýšľa zmeniť,
- **mutation boundary** — side effects majú byť explicitné, ohraničené a opakovateľné,
- **verification boundary** — úspešný return z API ešte nemusí znamenať dosiahnutý desired state,
- **process boundary** — stdout, stderr a exit codes tvoria kontrakt voči shellu, CI alebo scheduleru.

## 2. Kedy je Python vhodný

Python je silná voľba pre:

- HTTP a cloud API klientov,
- spracovanie JSON, YAML, CSV, XML a databázových výsledkov,
- validačné a transformačné pipeline,
- cross-platform CLI nástroje,
- inventory, reporting a compliance kontroly,
- release a deployment orchestration,
- paralelné alebo asynchrónne I/O,
- automatizáciu s vlastnými doménovými objektmi,
- nástroje, ktoré potrebujú unit a integration tests.

Bash býva jednoduchší, keď väčšinu práce vykonáva niekoľko existujúcich CLI príkazov. PowerShell býva prirodzenejší pri práci s Windows a Microsoft management object modelom. Python má zmysel vtedy, keď komplexita dát a failure modelu už prevyšuje výhodu krátkeho shell skriptu.

## 3. Interpreter, runtime a launcher

Automatizácia musí deklarovať podporovaný Python runtime:

```toml
[project]
requires-python = ">=3.12,<3.14"
```

Aktívny interpreter over:

```bash
python --version
python -c "import sys; print(sys.executable); print(sys.version)"
```

Na Unix systémoch môže byť vhodný shebang:

```python
#!/usr/bin/env python3
```

`env` vyhľadá interpreter cez `PATH`. To je flexibilné, ale výsledok závisí od prostredia. Pre produkčné spustenie je spoľahlivejší package entry point, explicitný virtual environment alebo hermetický runtime image než náhodný systémový `python`.

## 4. Virtual environment

Virtual environment izoluje Python interpreter-visible packages:

```bash
python -m venv .venv
```

Aktivácia nie je technickou podmienkou. Príkaz možno spustiť explicitne:

```bash
.venv/bin/python -m inventory_tool
```

Na Windows:

```powershell
.\.venv\Scripts\python.exe -m inventory_tool
```

Virtual environment neizoluje:

- operačný systém,
- externé executable súbory,
- sieť,
- používateľské oprávnenia,
- globálne environment variables,
- systémové trust stores.

Preto „funguje vo venv“ nie je dôkaz hermetického alebo prenositeľného runtime.

## 5. Dependency contract

Treba odlíšiť tri vrstvy:

```text
declared requirements
  ↓ resolver
locked concrete dependency graph
  ↓ installation
runtime environment
```

Príklad deklarácie:

```toml
[project]
name = "inventory-tool"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
  "httpx>=0.27,<1",
  "pydantic>=2.8,<3",
]
```

Version range vyjadruje kompatibilný kontrakt, nie presné reprodukovateľné prostredie. Lockfile alebo hash-pinned constraints zachytávajú konkrétne vyriešené verzie vrátane transitívnych dependencies.

Produkčný dependency proces má definovať:

- kto aktualizuje lockfile,
- ako sa testujú nové transitívne verzie,
- či sa vyžadujú package hashes,
- z ktorých indexov sa môže inštalovať,
- ako sa rieši dependency confusion,
- aký vulnerability a license audit je povinný,
- ako sa reprodukuje historický build.

## 6. Project layout a import model

Odporúčaný layout:

```text
inventory-tool/
├── pyproject.toml
├── README.md
├── src/
│   └── inventory_tool/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── domain.py
│       ├── planning.py
│       ├── apply.py
│       └── adapters/
│           ├── http.py
│           └── subprocess.py
└── tests/
    ├── unit/
    └── integration/
```

`src` layout znižuje riziko, že tests omylom importujú package priamo z repository rootu namiesto nainštalovaného artifactu.

Rozdelenie vrstiev zlepšuje testovateľnosť:

- `domain` — čisté dátové typy a pravidlá bez I/O,
- `planning` — porovnanie current a desired state,
- `adapters` — filesystem, API, subprocess a secret-provider hranice,
- `cli` — parsing, logging, exit-code mapping a user-facing output.

## 7. Package entry point

V `pyproject.toml`:

```toml
[project.scripts]
inventory-tool = "inventory_tool.cli:main"
```

Entry point odstráni závislosť od current working directory a manuálneho `python path/to/script.py`.

Top-level boundary:

```python
from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)


def main() -> int:
    try:
        args = parse_args()
        configure_logging(args.verbose)
        run(args)
    except KeyboardInterrupt:
        logger.warning("interrupted")
        return 130
    except UsageError as exc:
        logger.error("invalid input: %s", exc)
        return 2
    except ExpectedOperationalError as exc:
        logger.error("operation failed: %s", exc)
        return 1
    except Exception:
        logger.exception("unexpected automation failure")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

`main()` mapuje interný error model na stabilné process exit codes. Hlboké funkcie nemajú svojvoľne volať `sys.exit()`, pretože by komplikovali reuse a testovanie.

## 8. CLI ako verejný kontrakt

Príklad s `argparse`:

```python
import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="inventory-tool")
    parser.add_argument(
        "--environment",
        choices=("dev", "test", "prod"),
        required=True,
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", choices=("human", "json"), default="human")
    parser.add_argument("--verbose", action="store_true")
    return parser
```

CLI kontrakt musí definovať:

- required a optional argumenty,
- defaults a precedence,
- validované ranges a enumerácie,
- behavior pri opakovaní argumentu,
- stdin použitie,
- human-readable a machine-readable output,
- exit codes,
- deprecation pravidlá.

Zmena názvu argumentu, defaultu alebo exit code môže byť breaking change pre pipeline rovnako ako zmena API.

## 9. Configuration precedence

Konfigurácia môže pochádzať z viacerých zdrojov:

```text
explicit CLI
  > environment variables
  > configuration file
  > application defaults
```

Precedence musí byť deterministická a zdokumentovaná. Nástroj má po načítaní vytvoriť jeden validovaný immutable config objekt, namiesto opakovaného čítania globálneho environmentu počas spracovania.

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Config:
    environment: str
    api_url: str
    timeout_seconds: float
    dry_run: bool
    state_file: Path
```

Config objekt má obsahovať normované hodnoty. Parsovanie stringu na URL, číslo alebo path patrí na input boundary.

## 10. Environment variables a secrets

```python
import os

api_url = os.environ.get("API_URL", "https://api.example.com")
token = os.environ["API_TOKEN"]
```

`os.environ[...]` je vhodné pre povinnú hodnotu, pretože pri chýbaní zlyhá. `.get()` je vhodné iba pre vedomý optional default.

Environment variable nie je plnohodnotný secret manager. Môže sa objaviť v:

- crash reporte,
- debug dump-e,
- child process environment-e,
- CI diagnostike,
- `/proc` alebo platform-specific inspection,
- nechránenom process snapshot-e.

Preferuj workload identity, krátkodobé credentials a secret-provider adapter. Secret nikdy nevkladaj do URL, log message, exception textu ani argument listu externého procesu, ak existuje bezpečnejší kanál.

## 11. Dátový model a validácia

Type hints zlepšujú statickú kontrolu, ale samy nevalidujú runtime vstup:

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Service:
    name: str
    environment: str
    port: int
```

Runtime validation musí overiť aj invarianty:

```python
class ConfigurationError(ValueError):
    pass


def parse_port(raw: str) -> int:
    try:
        port = int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"invalid port: {raw!r}") from exc

    if not 1 <= port <= 65535:
        raise ConfigurationError(f"port out of range: {port}")
    return port
```

Validácia má rozlíšiť:

- neplatný typ alebo syntax,
- chýbajúcu povinnú hodnotu,
- semanticky neplatnú kombináciu,
- conflict medzi dvoma zdrojmi configu,
- hodnotu, ktorá je syntakticky platná, ale zakázaná policy.

## 12. `$null` ekvivalenty a pravdivostné skratky

Pri JSON a config dátach nezamieňaj:

- absent key,
- explicitné `null` / Python `None`,
- prázdny string,
- prázdny list alebo dictionary,
- číslo `0`,
- boolean `False`.

Nebezpečné:

```python
if not config.get("retries"):
    retries = 3
```

Tým sa explicitná hodnota `0` zamení za chýbajúcu hodnotu. Presnejšie:

```python
if "retries" not in config:
    retries = 3
else:
    retries = int(config["retries"])
```

## 13. Paths a filesystem boundary

Používaj `pathlib`:

```python
from pathlib import Path

config_path = Path("config") / "app.json"
content = config_path.read_text(encoding="utf-8")
```

Stále treba riešiť:

- relatívnu path voči current working directory,
- symlinky a ich dereference,
- case sensitivity,
- permissions a ownership,
- race medzi check a use,
- path traversal,
- Windows reserved names a path length,
- network filesystem semantics.

Pri user-supplied relative path over, že resolved cieľ zostáva pod povoleným rootom:

```python
root = allowed_root.resolve()
target = (root / user_path).resolve()
if target != root and root not in target.parents:
    raise ConfigurationError("path escapes allowed root")
```

Takáto kontrola stále musí zohľadniť symlink races a oprávnenia threat modelu.

## 14. Atomic file update

Bezpečný update má typicky fázy:

```text
generate temporary content
→ flush and optionally fsync
→ validate temporary file
→ preserve required metadata
→ atomic replace in same filesystem
→ verify active file
```

Príklad:

```python
from pathlib import Path
import os
import tempfile


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            delete=False,
        ) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            temp_path = Path(handle.name)

        validate_generated_file(temp_path)
        os.replace(temp_path, path)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
```

`os.replace()` je atomický rename iba v rámci podporovaného filesystem modelu. Durability po power loss môže vyžadovať fsync parent adresára. Atomicita jedného súboru navyše neznamená transakciu viacerých súborov.

## 15. Subprocess boundary

Používaj argument vector, nie shell string:

```python
import subprocess


def git_head(repository: str) -> str:
    completed = subprocess.run(
        ["git", "-C", repository, "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=10,
    )
    return completed.stdout.rstrip("\n")
```

Dôležité parametre:

- `check=True` — non-zero exit status sa zmení na `CalledProcessError`,
- `timeout` — zabráni neobmedzenému visu,
- `cwd` — explicitný working directory,
- `env` — explicitné inherited alebo sanitized environment,
- `capture_output` — vhodné iba pre ohraničený output,
- `text` a `encoding` — definovaný decoding contract.

`shell=True` je potrebné iba vtedy, keď vedome potrebuješ syntax shellu. Pri user-controlled inpute vytvára command-injection boundary.

## 16. Subprocess lifecycle a streaming

Pri dlhom procese je potrebné riešiť:

- priebežné čítanie stdout/stderr,
- riziko zaplnenia pipe bufferov,
- timeout a termination escalation,
- process group a child procesy,
- signal forwarding,
- zachovanie diagnostického outputu,
- rozdiel medzi graceful terminate a forced kill.

`subprocess.run()` je vhodný pre krátky synchronný proces. Pre streaming alebo koordinované ukončenie použi `Popen` alebo async subprocess API s explicitným lifecycle modelom.

## 17. HTTP klient ako stateful resource

Príklad s `httpx`:

```python
import httpx


def build_client(token: str) -> httpx.Client:
    timeout = httpx.Timeout(
        connect=3.0,
        read=10.0,
        write=10.0,
        pool=2.0,
    )
    limits = httpx.Limits(max_connections=20, max_keepalive_connections=10)
    return httpx.Client(
        headers={"Authorization": f"Bearer {token}"},
        timeout=timeout,
        limits=limits,
        follow_redirects=False,
    )
```

Client objekt vlastní connection pool, TLS sessions a sockets. Neotváraj nový client pre každý request bez dôvodu.

HTTP adapter musí definovať:

- base URL a allowed destinations,
- DNS/TLS verification policy,
- connect/read/write/pool timeouty,
- redirect policy,
- status-code mapping,
- response-size limit,
- pagination,
- rate-limit handling,
- idempotency a retry policy,
- credential refresh.

## 18. HTTP failure semantics

Rozlíš:

```text
DNS/connect/TLS failure
HTTP response with error status
valid HTTP response with invalid payload
valid payload with failed business postcondition
```

Tieto chyby majú odlišnú retry a diagnostickú politiku. `response.raise_for_status()` overí HTTP status, ale nie schema ani business výsledok.

```python
def fetch_service(client: httpx.Client, url: str) -> Service:
    response = client.get(url)
    response.raise_for_status()
    payload = response.json()
    return parse_service(payload)
```

`parse_service()` musí validovať payload. Nástroj nesmie považovať ľubovoľný JSON za dôveryhodný doménový objekt.

## 19. Exception model

Výnimku zachyť tam, kde vieš aspoň jedno z nasledovného:

- pridať užitočný kontext,
- vykonať bezpečnú recovery,
- preložiť low-level error na doménový error,
- mapovať chybu na boundary output alebo exit code.

```python
class RemoteStateError(RuntimeError):
    pass


def load_remote_state(client: httpx.Client, url: str) -> dict[str, object]:
    try:
        response = client.get(url)
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException as exc:
        raise RemoteStateError(f"timeout while reading {url}") from exc
```

`raise ... from exc` zachová exception chain. Nezachytávaj všeobecné `Exception` hlboko iba preto, aby sa pokračovalo s neúplným stavom.

## 20. Expected a unexpected failures

Doménové chyby majú byť rozlíšiteľné:

- **usage/configuration error** — používateľ môže opraviť vstup,
- **precondition failure** — current state nedovoľuje operáciu,
- **transient dependency failure** — operácia môže byť bezpečne zopakovaná,
- **permanent dependency response** — retry bez zmeny vstupu nepomôže,
- **postcondition failure** — mutation prebehla, ale desired state nebol potvrdený,
- **internal invariant violation** — bug alebo nepredpokladaný stav.

Toto rozdelenie ovplyvňuje exit code, retry, alerting aj runbook.

## 21. Logging a structured result

Knižnica nemá globálne konfigurovať root logger. Logging sa konfiguruje na process boundary.

```python
import logging


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format=(
            "%(asctime)s level=%(levelname)s logger=%(name)s "
            "message=%(message)s"
        ),
    )
```

Loguj najmä:

- operation a correlation ID,
- target a environment,
- plan summary,
- duration,
- retry attempt,
- result category,
- relevant remote request ID.

Machine-readable výsledok patrí na stdout; diagnostika na stderr. Nevypisuj tokeny, authorization headers, celé environmenty ani citlivé payloady.

## 22. Plan, apply a verify

Doménový workflow oddeľ od I/O:

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Change:
    target: str
    action: str
    before: object
    after: object


def build_plan(current: State, desired: State) -> tuple[Change, ...]:
    ...


def apply_plan(plan: tuple[Change, ...], adapter: Adapter) -> None:
    ...


def verify_postconditions(desired: State, adapter: Adapter) -> None:
    ...
```

`dry-run` má vykonať parsing, discovery, validation a plánovanie. Má vynechať mutation, nie celý program pred mutation boundary.

Plán má byť:

- deterministický pre rovnaké vstupy,
- serializovateľný alebo auditovateľný,
- explicitný o create/update/delete operáciách,
- schopný ukázať neznáme alebo citlivé hodnoty redigovane,
- validovaný pred aplikovaním.

## 23. Idempotencia

Idempotentná automatizácia porovnáva current a desired state:

```python
def ensure_directory(path: Path) -> bool:
    if path.is_dir():
        return False
    if path.exists():
        raise PreconditionError(f"path exists but is not a directory: {path}")
    path.mkdir(parents=True)
    return True
```

Návratová hodnota rozlišuje no-op od mutation.

Idempotencia vyžaduje:

- stabilnú identitu resource,
- normovaný current state,
- deterministic desired state,
- bezpečné opakovanie po partial failure,
- explicitnú handling politiku pre externe zmenený stav,
- overenie, že operation naozaj dosiahla postcondition.

## 24. Atomicita, rollback a compensation

Viackrokový externý workflow zvyčajne nie je transakčný:

```text
create resource A
update resource B
publish manifest C
```

Ak krok C zlyhá, rollback nemusí byť možný alebo bezpečný. Workflow má definovať:

- ktoré kroky sú atomické,
- ktorý partial state môže zostať,
- či je možný rollback,
- či sa používa compensation,
- ako sa operácia obnoví po reštarte,
- kde sa eviduje operation state.

„Pri exception vráť všetko späť“ nie je realistická stratégia bez podpory transakcie alebo explicitných kompenzačných operácií.

## 25. Retry policy

Retry je bezpečný iba pri transientnej chybe a opakovateľnej operácii.

```python
import random
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def retry(
    operation: Callable[[], T],
    *,
    attempts: int,
    initial_delay: float,
) -> T:
    delay = initial_delay
    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except TransientError:
            if attempt == attempts:
                raise
            time.sleep(delay + random.uniform(0, delay * 0.2))
            delay *= 2
    raise AssertionError("unreachable")
```

Produkčný retry potrebuje:

- bounded attempts alebo deadline,
- exponential backoff a jitter,
- per-attempt timeout,
- celkový time budget,
- observability,
- idempotency key pri nejasnom výsledku,
- rešpektovanie `Retry-After`,
- stop condition pri permanentnej chybe.

Násobenie retries v klientovi, proxy a ďalšej službe môže počas incidentu vytvoriť retry storm.

## 26. Timeouts a deadlines

Každé externé I/O má mať timeout. Timeout jednotlivého pokusu však nestačí. Potrebný je aj celkový deadline workflowu:

```text
total deadline
  ├── discovery budget
  ├── apply attempts
  ├── verification budget
  └── cleanup reserve
```

Bez celkového budgetu môžu vnorené retries predĺžiť job z minút na hodiny.

Timeout je nejasný výsledok: vzdialená operácia mohla prebehnúť, hoci klient odpoveď nedostal. Pred retry treba podľa operation semantics overiť remote state.

## 27. Concurrency model

### Threads

Vhodné pre blocking I/O, ak použité knižnice a zdieľané objekty sú thread-safe.

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(fetch_item, item_ids))
```

### Processes

Vhodné pre CPU-bound prácu. Každý proces má samostatnú memory a objekty sa musia serializovať. Startup a IPC overhead môžu prevýšiť prínos pri malých úlohách.

### `asyncio`

Vhodné pre veľa concurrent I/O operácií s async-compatible knižnicami. Blocking call v event loop-e môže zastaviť všetky tasks.

Výber modelu je sekundárny. Najprv definuj:

- maximálnu concurrency,
- ordering výsledkov,
- per-target limit,
- rate-limit budget,
- cancellation,
- partial failure policy,
- zdieľaný state a synchronizáciu.

## 28. Backpressure a bounded work

Neobmedzené vytváranie tasks presunie frontu do memory:

```text
producer > workers
→ pending tasks grow
→ memory and latency grow
→ timeout cascade
```

Použi bounded queue, semaphore alebo batchovanie. Concurrency limit je súčasť correctness a failure control, nie iba performance tuning.

## 29. Cancellation a graceful shutdown

Pri `SIGINT` alebo `SIGTERM` má nástroj:

1. prestať prijímať novú prácu,
2. označiť cancellation intent,
3. bezpečne dokončiť alebo prerušiť rozpracované operácie,
4. ukončiť child procesy a sessions,
5. uvoľniť locks,
6. flushnúť logy a operation state,
7. vrátiť konzistentný exit code.

```python
import signal
import threading

stop_event = threading.Event()


def request_stop(signum: int, frame: object) -> None:
    stop_event.set()


signal.signal(signal.SIGTERM, request_stop)
signal.signal(signal.SIGINT, request_stop)
```

Signal handler má robiť minimum práce. Komplexný cleanup patrí do normálneho control flowu.

## 30. Context managers a resource ownership

Context manager vyjadruje vlastníctvo lifecycle resource:

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

Použitie:

- files a temporary directories,
- HTTP clients,
- databázové transakcie,
- locks,
- tracing spans,
- temporary credentials,
- process pools.

Resource má zatvárať vrstva, ktorá ho vytvorila a vlastní.

## 31. Locking a koordinácia

Python štandardná knižnica neposkytuje jednotný high-level cross-platform file lock. Platform-specific alebo externá knižnica musí definovať:

- advisory verzus mandatory behavior,
- wait, fail-fast alebo skip policy,
- stale lock recovery,
- lock ownership a metadata,
- filesystem compatibility.

Lokálny file lock nekoordinuje viac hostov. Distribuovaný workflow potrebuje databázový lock, lease, compare-and-swap alebo iný coordination mechanismus s timeoutom a fencing semantics.

## 32. Testing architecture

Testovateľný design oddeľuje čistú doménovú logiku od adapters.

Test layers:

- **unit tests** — parsing, validation, diff a plan logic,
- **adapter tests** — HTTP, filesystem a subprocess contract,
- **integration tests** — skutočná kombinácia viacerých komponentov,
- **end-to-end test** — nainštalovaný CLI artifact a používateľský scenár.

Príklad:

```python
from pathlib import Path


def test_atomic_write(tmp_path: Path) -> None:
    target = tmp_path / "config.txt"
    atomic_write(target, "value\n")
    assert target.read_text(encoding="utf-8") == "value\n"
```

Testuj aj:

- invalid a boundary input,
- prázdne kolekcie,
- timeout a retry exhaustion,
- partial mutation,
- opakované spustenie,
- concurrent invocation,
- interruption,
- unavailable dependency,
- permission failure,
- dry-run bez mutations,
- log redaction,
- cross-platform path a encoding behavior.

## 33. Mocking a test seams

Mockuj externú hranicu, nie interný algoritmus:

- HTTP transport,
- filesystem adapter,
- clock,
- random/jitter source,
- subprocess runner,
- secret provider,
- identity provider.

Ak test mockuje každú internú funkciu, môže dokazovať iba vlastnú implementáciu. Pre kritické adapters používaj contract alebo integration tests proti realistickému fake/serveru.

Dependency injection nemusí znamenať framework. Často stačí odovzdať callable alebo adapter objekt funkcii.

## 34. Static analysis a quality gates

Príklad lokálneho gate:

```bash
ruff check .
ruff format --check .
mypy src
pytest
python -m build
```

Podľa threat modelu doplň:

- dependency vulnerability audit,
- secret scanning,
- license policy,
- package metadata validation,
- wheel installation smoke test,
- supported-Python-version matrix.

Lint a type checker neoveria externé API semantics, race conditions ani idempotenciu.

## 35. Packaging a distribution

Artifact má byť reprodukovateľný a identifikovateľný:

```bash
python -m build
```

Distribučné možnosti:

- wheel v internom package registry,
- standalone application environment,
- container image,
- zipapp alebo iný self-contained model,
- OS package.

Nepovažuj source checkout za deployment artifact. Package version, Git commit, dependency lock a build provenance majú byť dohľadateľné.

Pri spustení možno logovať neškodnú version identitu:

```python
from importlib.metadata import version

tool_version = version("inventory-tool")
```

## 36. Supply-chain security

Riziká dependency a build procesu:

- typosquatting a dependency confusion,
- kompromitovaný maintainer alebo package,
- neočakávaný build-time code execution,
- mutable package index alebo cache,
- neoverené wheels/sdists,
- secrets dostupné build procesu,
- publish credential s príliš širokým scope.

Controls:

- schválené indexy,
- lockfile a hashes,
- izolovaný build,
- minimálne build credentials,
- signed/provenance metadata podľa platformy,
- review dependency updates,
- oddelený build a publish krok.

## 37. Aplikačná bezpečnosť

Typické automation riziká:

- command injection cez `shell=True`,
- path traversal a symlink race,
- SSRF cez neoverenú URL,
- vypnutá TLS verification,
- unsafe deserialization,
- nekontrolované archive extraction,
- secrets v logoch alebo exceptions,
- world-readable output files,
- široké cloud credentials,
- neobmedzené deletion alebo wildcard targets.

Pri archive extraction over každú výslednú path. Pri delete operácii validuj root, target identity, scope a dry-run plán. „Je to interný nástroj“ nie je bezpečnostná hranica.

## 38. Produkčný skeleton

```python
from __future__ import annotations

import argparse
import logging

logger = logging.getLogger(__name__)


def run(args: argparse.Namespace) -> Result:
    config = load_and_validate_config(args)

    with build_adapters(config) as adapters:
        current = discover_current_state(config, adapters)
        desired = build_desired_state(config)
        plan = build_plan(current, desired)
        validate_plan(plan, config)

        if config.dry_run:
            return Result.from_plan(plan)

        apply_plan(plan, adapters)
        verified = discover_current_state(config, adapters)
        verify_postconditions(verified, desired)
        return Result.success(plan)


def main() -> int:
    args = build_parser().parse_args()
    configure_logging(args.verbose)

    try:
        result = run(args)
    except KeyboardInterrupt:
        logger.warning("interrupted")
        return 130
    except UsageError as exc:
        logger.error("invalid input: %s", exc)
        return 2
    except ExpectedOperationalError as exc:
        logger.error("operation failed: %s", exc)
        return 1
    except Exception:
        logger.exception("unexpected failure")
        return 1

    emit_result(result, output_format=args.output)
    return 0
```

Skeleton zámerne oddeľuje config, discovery, plan, mutation, verification a presentation.

## 39. Diagnostický postup

Keď nástroj funguje lokálne, ale nie v CI:

1. zaznamenaj presný Python executable a version,
2. porovnaj nainštalovaný dependency graph a lockfile,
3. over package install a import path,
4. skontroluj current working directory,
5. porovnaj environment, locale a timezone,
6. over filesystem usera a permissions,
7. skontroluj network egress, proxy a trust store,
8. over externé executable a ich verzie,
9. porovnaj machine-readable logs a exit code,
10. reprodukuj z rovnakého artifactu v čistom prostredí.

Import diagnostika:

```bash
python -c "import package; print(package.__file__)"
python -m pip show package
python -m pip list
```

## 40. Typické failure patterns

### Skript visí

Možné príčiny:

- chýbajúci network alebo subprocess timeout,
- deadlock alebo čakajúci lock,
- blocking call v async event loop-e,
- child process so zaplneným pipe bufferom,
- neukončený executor,
- retry bez celkového deadline.

### Pamäť rastie

Kontroluj:

- unbounded queue alebo task list,
- celý veľký súbor načítaný do memory,
- neobmedzený subprocess output capture,
- cache bez eviction,
- retained references,
- výsledky zhromaždené naraz namiesto streamingu.

### Operácia sa vykonala dvakrát

Skontroluj:

- retry po nejasnom timeout-e,
- scheduler duplicate delivery,
- chýbajúci idempotency key,
- race medzi dvoma instances,
- plan založený na stale current state.

### `dry-run` je zelený, apply zlyhá

Príčinou môže byť:

- dry-run neoveril permissions alebo externé preconditions,
- stav sa medzi plan a apply zmenil,
- mutation používa inú code path,
- secret alebo credential sa načítava až pri apply,
- plan nezachytil hidden dependency.

## 41. Prevádzkový checklist

Pred nasadením automatizačného nástroja over:

- podporovaný Python runtime je deklarovaný,
- dependency graph je reprodukovateľný,
- package entry point funguje z čistého prostredia,
- CLI a exit codes sú stabilné,
- config precedence je explicitná,
- secrets sa nelogujú,
- každé externé I/O má timeout,
- retries sú bounded a idempotentné,
- concurrency je limitovaná,
- mutations majú dry-run a verification,
- partial failure má recovery alebo compensation postup,
- shutdown uvoľní resources,
- artifact má version a provenance,
- unit, integration a smoke tests pokrývajú kritické scenáre.

## 42. Časté omyly

### „Python skript je automaticky cross-platform“

Nie. Externé príkazy, signals, permissions, filesystem, encoding a trust stores sa líšia.

### „Type hints validujú runtime vstup“

Nie. Bez explicitnej validácie sú iba statickým kontraktom.

### „Retry vyrieši každé zlyhanie“

Permanentnú chybu iba predĺži a pri mutation môže znásobiť side effects.

### „Exception treba zachytiť čo najskôr“

Nie. Zachyť ju na vrstve, ktorá vie pridať kontext, vykonať recovery alebo ju mapovať na verejný kontrakt.

### „Úspešný API status znamená úspešnú automatizáciu“

Nie. Treba validovať payload a overiť výsledný desired state.

### „Virtual environment je hermetický deployment“

Nie. Izoluje Python packages, nie celý runtime a operačný systém.

## 43. Kontrolné otázky

1. Kedy je Python vhodnejší než Bash alebo PowerShell?
2. Aký je rozdiel medzi deklarovaným dependency range, lockfile a runtime environmentom?
3. Prečo je `src` layout užitočný?
4. Aké hranice má stabilný CLI a process contract?
5. Prečo sa konfigurácia má načítať do jedného validovaného objektu?
6. Aké failure kategórie musí rozlišovať HTTP adapter?
7. Prečo timeout vytvára nejasný výsledok mutation?
8. Aké podmienky musí spĺňať bezpečný retry?
9. Ako sa líšia threads, processes a `asyncio`?
10. Prečo je bounded concurrency súčasť correctness?
11. Čo oddeľuje plan, apply a verify?
12. Kedy je potrebná compensation namiesto rollbacku?
13. Ako navrhneš graceful shutdown?
14. Prečo sa má mockovať externá boundary a nie každá interná funkcia?
15. Ako overíš reprodukovateľnosť a provenance Python artifactu?

## Glossary impact

Relevantné pojmy: virtual environment, dependency resolver, lockfile, package entry point, CLI contract, configuration precedence, type hint, runtime validation, adapter, atomic write, exception chaining, timeout budget, idempotency key, retry budget, backoff, jitter, thread pool, process pool, `asyncio`, backpressure, graceful shutdown, compensation, boundary mock, package provenance a dependency confusion.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: PowerShell fundamentals](powershell-fundamentals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: YAML, JSON a regular expressions →](yaml-json-regular-expressions.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
