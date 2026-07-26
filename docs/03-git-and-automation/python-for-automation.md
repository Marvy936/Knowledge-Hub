# Python for automation

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Bash automation](bash-automation.md), [PowerShell fundamentals](powershell-fundamentals.md), [Idempotencia](../00-foundations/idempotency.md)
- Súvisiace témy: CLI contract, domain model, adapters, plan/apply/verify, retries, packaging, testing

## 1. Cieľ kapitoly

Python je vhodný pre automatizáciu, keď workflow už nie je iba krátke skladanie existujúcich príkazov, ale potrebuje vlastný dátový model, viac externých hraníc, dlhodobú údržbu a samostatné testovanie.

Produkčný Python nástroj má stále rovnaký základný lifecycle ako dobrý Bash alebo PowerShell automation program:

```text
process invocation
→ validovaný config
→ current state
→ desired state
→ deterministický plan
→ bounded mutations
→ postcondition verification
→ structured result a exit code
```

Python neprináša idempotenciu, bezpečné retries ani prenositeľnosť automaticky. Prináša lepšie prostriedky na to, aby boli tieto kontrakty explicitné a testovateľné.

## 2. Nosný scenár: Atlas release reconciler

Atlas prevádzkuje službu `orders-api`. CI potrebuje nástroj:

```bash
atlas-release reconcile \
  --environment prod \
  --service orders-api \
  --version 3.8.1
```

Nástroj má:

1. načítať a validovať vstupy,
2. zistiť aktuálnu verziu služby,
3. vypočítať požadovanú zmenu,
4. v režime `--dry-run` iba zobraziť plan,
5. publikovať immutable release manifest,
6. požiadať deployment API o rollout,
7. čakať na potvrdenú readiness,
8. vrátiť jeden strojovo čitateľný výsledok.

Nosný tok:

```text
CLI/config
→ AtlasConfig
→ DeploymentState
→ tuple[Change, ...]
→ deployment adapter
→ nový observed state
→ verified AutomationResult
```

Všetky ďalšie mechanizmy v kapitole chránia jednu z týchto hraníc.

## 3. Kedy už workflow patrí do Pythonu

Bash zostáva vhodný, keď väčšinu práce vykonáva niekoľko stabilných CLI nástrojov a shell iba riadi ich poradie. PowerShell je prirodzený pri object-oriented administrácii a Microsoft ekosystéme.

Python začína dávať väčší zmysel, keď workflow potrebuje viacero z týchto vlastností:

- vlastné doménové typy a invarianty,
- HTTP, filesystem a subprocess adapters,
- komplexnejší error a recovery model,
- paralelné alebo asynchrónne I/O,
- reusable package namiesto jedného skriptu,
- unit, contract a integration tests,
- stabilné CLI alebo library API,
- packaging, versioning a provenance.

Praktický signál:

```text
shell script už prevažne modeluje dáta a failure state
namiesto toho, aby iba skladal procesy
```

## 4. Runtime a artifact sú súčasť kontraktu

Deklaruj podporovanú verziu Pythonu:

```toml
[project]
name = "atlas-release"
version = "0.1.0"
requires-python = ">=3.12,<3.14"
dependencies = [
  "httpx>=0.27,<1",
]

[project.scripts]
atlas-release = "atlas_release.cli:main"
```

Rozlišuj:

```text
declared dependency ranges
→ resolver
→ konkrétny locked graph
→ nainštalovaný runtime
→ vytvorený wheel/container artifact
```

Virtual environment izoluje Python packages, nie celý operačný systém, trust store, externé executable súbory ani sieť. Produkčný workflow preto nesmie byť závislý od náhodného system `python`, current working directory alebo mutable package state runnera.

Odporúčaný layout:

```text
atlas-release/
├── pyproject.toml
├── src/atlas_release/
│   ├── cli.py
│   ├── domain.py
│   ├── planning.py
│   ├── service.py
│   └── adapters/
│       ├── deployment_api.py
│       ├── manifest_store.py
│       └── subprocess.py
└── tests/
    ├── unit/
    └── integration/
```

`src` layout pomáha testovať nainštalovaný package contract namiesto náhodného importu z repository rootu.

## 5. Input boundary: jeden validovaný config objekt

Konfigurácia môže mať precedence:

```text
CLI
> environment variables
> config file
> application defaults
```

Po načítaní ju normalizuj do jedného immutable objektu:

```python
from dataclasses import dataclass
from urllib.parse import urlparse


class UsageError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class AtlasConfig:
    environment: str
    service: str
    version: str
    api_url: str
    timeout_seconds: float
    dry_run: bool


def validate_config(config: AtlasConfig) -> None:
    if config.environment not in {"dev", "test", "prod"}:
        raise UsageError("unsupported environment")
    if not config.service or "/" in config.service:
        raise UsageError("invalid service name")
    if not config.version:
        raise UsageError("version is required")
    parsed = urlparse(config.api_url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise UsageError("deployment API must use an HTTPS URL")
    if not 1 <= config.timeout_seconds <= 300:
        raise UsageError("timeout is outside the allowed range")
```

Type hints nie sú runtime validácia. `str` neznamená automaticky platný hostname, version alebo service identity.

Rozlišuj aj:

- absent hodnotu,
- explicitné `None`,
- prázdny string,
- `0`,
- `False`,
- prázdnu kolekciu.

Pravdivostná skratka nesmie prepísať explicitnú doménovú hodnotu.

## 6. Current a desired state sú doménové objekty

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DeploymentState:
    service: str
    environment: str
    version: str | None
    ready: bool
    resource_version: str


@dataclass(frozen=True, slots=True)
class DesiredState:
    service: str
    environment: str
    version: str
    ready: bool = True
```

Current state je pozorovanie konkrétneho okamihu, nie trvalá pravda. `resource_version` alebo ETag umožní zistiť, že sa stav medzi plan a apply zmenil.

Desired state má byť odvodený iba z validovaného configu a policy. Nemá čítať mutable globálne environment variables uprostred workflowu.

## 7. Plan je samostatný auditovateľný výsledok

```python
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Change:
    target: str
    action: str
    before: str | None
    after: str
    expected_resource_version: str


def build_plan(
    current: DeploymentState,
    desired: DesiredState,
) -> tuple[Change, ...]:
    if current.version == desired.version and current.ready:
        return ()

    return (
        Change(
            target=f"{desired.environment}/{desired.service}",
            action="UPDATE_VERSION",
            before=current.version,
            after=desired.version,
            expected_resource_version=current.resource_version,
        ),
    )
```

Plan má byť:

- deterministický pre rovnaké vstupy,
- bez side effects,
- explicitný o create/update/delete operáciách,
- serializovateľný alebo ľahko auditovateľný,
- schopný zachytiť preconditions,
- redigovaný pri citlivých hodnotách.

`--dry-run` musí vykonať parsing, discovery, normalizáciu a planning. Vynechá iba mutation a reálne verification po apply.

## 8. Adapters izolujú externé side effects

Doménová logika nemá priamo volať HTTP, subprocess ani filesystem.

```python
from typing import Protocol


class DeploymentAdapter(Protocol):
    def get_state(self, environment: str, service: str) -> DeploymentState: ...

    def apply(self, change: Change, *, operation_id: str) -> None: ...
```

Výhoda nie je iba „čistejší kód“. Adapter boundary určuje:

- timeout a retry policy,
- authentication a authorization,
- response validation,
- idempotency key,
- error translation,
- logging a request identity,
- test seam.

Mockuj externú hranicu, nie každú internú funkciu.

## 9. HTTP adapter musí klasifikovať výsledok

Jeden HTTP call môže skončiť ako:

```text
DNS/connect/TLS failure
HTTP error response
valid HTTP response s neplatným payloadom
valid payload s odmietnutou business operáciou
accepted mutation bez potvrdenej postcondition
```

Príklad klienta:

```python
import httpx


def build_client(token: str) -> httpx.Client:
    return httpx.Client(
        headers={"Authorization": f"Bearer {token}"},
        timeout=httpx.Timeout(connect=3, read=10, write=10, pool=2),
        limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        follow_redirects=False,
    )
```

Client vlastní connection pool a má sa zatvoriť cez context manager. Odpoveď treba validovať pred prekladom na `DeploymentState`.

Neloguj token, celý authorization header ani citlivý payload.

## 10. Subprocess je samostatný process contract

Argumenty odovzdávaj ako vector:

```python
import subprocess


def validate_manifest(path: str) -> None:
    subprocess.run(
        ["atlas-manifest-validator", "--", path],
        check=True,
        timeout=15,
        cwd=None,
        text=True,
        encoding="utf-8",
        capture_output=True,
    )
```

`shell=True` pridáva ďalšie parsing kolo a command-injection boundary. Použi ho iba pri vedomej potrebe shell syntaxe.

Pri dlhom procese treba riešiť streaming, pipe buffers, process group, graceful termination a child cleanup. `subprocess.run()` je vhodný iba pre ohraničený synchronný call.

## 11. Mutation má byť bounded a idempotentná

Apply používa precondition z planu:

```python
class StalePlanError(RuntimeError):
    pass


def apply_change(
    change: Change,
    adapter: DeploymentAdapter,
    *,
    operation_id: str,
) -> None:
    adapter.apply(change, operation_id=operation_id)
```

Deployment API má napríklad odmietnuť update, ak `expected_resource_version` už nie je aktuálna. Tým sa zabráni použitiu stale planu po paralelnej zmene.

Idempotencia potrebuje:

- stabilnú resource identity,
- normovaný current state,
- jednoznačný desired state,
- idempotency key alebo compare-and-swap pri nejasnom výsledku,
- no-change path,
- bezpečné opakovanie po partial failure.

Idempotencia nie je iba absencia exception pri druhom spustení. Druhé spustenie musí skončiť v rovnakom výslednom stave bez nových vedľajších účinkov.

## 12. Verification je nové pozorovanie

Úspešná odpoveď z mutation API ešte nedokazuje používateľský výsledok.

```python
class PostconditionError(RuntimeError):
    pass


def verify_postconditions(
    desired: DesiredState,
    actual: DeploymentState,
) -> None:
    if actual.version != desired.version:
        raise PostconditionError(
            f"expected version {desired.version}, observed {actual.version}"
        )
    if desired.ready and not actual.ready:
        raise PostconditionError("deployment is not ready")
```

Verification používa nový read z autoritatívneho observation pointu. Nemá iba znovu prečítať lokálny plan alebo request body.

## 13. Failure taxonomy riadi recovery

Rozlišuj minimálne:

- **usage/configuration error** — používateľ môže opraviť vstup,
- **precondition failure** — current state už nezodpovedá planu,
- **transient dependency failure** — retry môže byť bezpečný,
- **permanent dependency failure** — retry bez zmeny vstupu nepomôže,
- **postcondition failure** — mutation bola prijatá, výsledok nie je potvrdený,
- **internal invariant violation** — bug alebo neznámy stav,
- **interruption** — operátor alebo scheduler požiadal o ukončenie.

Výnimku zachyť tam, kde vieš pridať kontext, vykonať recovery alebo ju mapovať na verejný výsledok. Exception chain zachovaj:

```python
try:
    state = adapter.get_state(environment, service)
except httpx.TimeoutException as exc:
    raise RemoteStateError("timed out while reading deployment state") from exc
```

## 14. Retry potrebuje dôkaz, nie optimizmus

Retry je vhodný iba ak:

1. chyba je transientná,
2. operácia je idempotentná alebo má idempotency key,
3. existuje per-attempt timeout,
4. existuje celkový deadline,
5. retry má bounded attempts, backoff a jitter,
6. server response ako `Retry-After` sa rešpektuje,
7. každý attempt je pozorovateľný.

Timeout mutation je nejasný výsledok:

```text
request mohol byť spracovaný
ale response sa ku klientovi nevrátila
```

Pred zopakovaním najprv vyhľadaj operation ID alebo znovu prečítaj remote state.

Vnorené retries v klientovi, proxy a službe môžu počas incidentu vytvoriť retry storm.

## 15. Partial failure potrebuje operation state

Atlas workflow má viac krokov:

```text
publish manifest
→ request rollout
→ verify readiness
```

Ak verification zlyhá, manifest aj rollout request už môžu existovať. Automatické „vráť všetko späť“ nemusí byť bezpečné.

Definuj:

- ktoré kroky sú atomické,
- ktorý partial state môže zostať,
- či existuje rollback,
- či treba kompenzačnú operáciu,
- ako sa workflow obnoví po reštarte,
- kde je uložené operation ID a phase.

Rollback obnovuje predchádzajúci stav. Compensation vytvára novú operáciu, ktorá znižuje dopad už vykonaného side effectu.

## 16. Concurrency je correctness policy

Pred threads, processes alebo `asyncio` definuj:

- maximálnu concurrency,
- per-target limit,
- ordering výsledkov,
- rate-limit budget,
- cancellation,
- partial-success policy,
- koordináciu shared state.

Neobmedzené vytváranie tasks presunie frontu do memory:

```text
producer rýchlejší než workers
→ pending tasks rastú
→ memory a latency rastú
→ timeout cascade
```

Použi bounded queue, semaphore alebo batchovanie. Lokálny lock nechráni viac hostov; distribuovaný workflow potrebuje lease, compare-and-swap alebo inú koordináciu s fencing semantics.

## 17. Resource ownership a graceful shutdown

Vrstva, ktorá vytvorí resource, ho má aj zavrieť:

```python
with build_client(token) as client:
    adapter = HttpDeploymentAdapter(client, api_url)
    result = reconcile(config, adapter)
```

To platí pre:

- HTTP clients,
- files a temporary directories,
- locks,
- subprocesses,
- executors,
- database transactions,
- tracing spans.

Pri `SIGINT` alebo `SIGTERM` nástroj prestane prijímať novú prácu, dokončí alebo bezpečne preruší aktuálny krok, uloží operation state, zatvorí resources a vráti konzistentný exit code.

## 18. Process boundary: výsledok, logy a exit codes

Knižničná vrstva vracia objekty alebo vyhadzuje doménové errors. Top-level CLI mapuje výsledok na stdout, stderr a exit code.

```python
from dataclasses import asdict, dataclass
import json
import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AutomationResult:
    environment: str
    service: str
    changed: bool
    verified: bool
    version: str
    operation_id: str


def emit_json(result: AutomationResult) -> None:
    print(json.dumps(asdict(result), sort_keys=True))
```

Odporúčaný contract:

```text
stdout  structured result alebo požadované dáta
stderr  logs a diagnostics
status  stabilná kategória process výsledku
```

Hlboké funkcie nemajú volať `sys.exit()`.

## 19. Worked failure: timeout vytvoril dvojitý rollout

Pôvodný klient:

```python
for _ in range(3):
    try:
        client.post("/rollouts", json=payload, timeout=5)
        break
    except httpx.TimeoutException:
        continue
```

Incident:

```text
prvý POST vytvoril rollout R-101
→ response sa stratila
→ klient po 5 sekundách retryol
→ druhý POST vytvoril rollout R-102
→ dva rollouty súťažili o rovnaký target
```

Príčina nebola „HTTP je nespoľahlivé“. Mutation nemala stabilnú operation identity ani deduplication contract.

Náprava:

1. klient vytvorí `operation_id`,
2. pošle ho ako idempotency key,
3. timeout klasifikuje ako unknown outcome,
4. pred retry vyhľadá operation status,
5. server rovnaký key neduplikuje,
6. verification sleduje konkrétny rollout.

Mechanizmus:

```text
bounded retry
+ stable operation identity
+ state lookup
+ postcondition verification
```

## 20. Worked failure: lokálne funguje, CI importuje iný package

Lokálne vývojár spustil:

```bash
python src/atlas_release/cli.py
```

CI nainštalovalo starší wheel z cache a spustilo entry point. Testy pritom importovali package priamo z repository rootu.

Výsledok:

```text
tests green nad source tree
→ artifact obsahuje inú dependency alebo chýbajúci file
→ nainštalovaný CLI zlyhá až v release jobe
```

Diagnostika:

```bash
python -c "import atlas_release; print(atlas_release.__file__)"
python -m pip show atlas-release
python -m pip list
```

Náprava:

- `src` layout,
- build wheelu v CI,
- install wheelu do čistého prostredia,
- smoke test package entry pointu,
- lock a cache key viazaný na dependency inputs,
- version/provenance v structured result-e.

## 21. Testing kopíruje lifecycle boundaries

Test layers:

- **unit** — input validation, desired state, plan a invariants,
- **adapter contract** — HTTP, subprocess a filesystem semantics,
- **integration** — reálne adapters proti sandboxu alebo realistickému fake-u,
- **end-to-end** — nainštalovaný artifact a používateľský CLI scenár.

Povinné scenáre:

- no-change run,
- idempotent second run,
- dry-run bez mutation,
- stale plan rejection,
- timeout s unknown outcome,
- retry exhaustion,
- partial apply,
- verify failure,
- interruption,
- concurrent invocation,
- log redaction,
- package install a entry-point smoke test.

Static gates môžu obsahovať:

```bash
ruff check .
ruff format --check .
mypy src
pytest
python -m build
```

Lint a type checker neoverujú externé API semantics, races ani idempotenciu.

## 22. Packaging a supply-chain boundary

Source checkout nie je deployment artifact. Produkčný artifact má byť:

- identifikovateľný verziou a digestom,
- dohľadateľný na source commit,
- vytvorený z kontrolovaného dependency graphu,
- otestovaný po inštalácii,
- publikovaný oddelenou identity s minimálnym scope.

Riziká:

- dependency confusion a typosquatting,
- mutable index alebo cache,
- neoverený wheel/sdist,
- build-time code execution,
- príliš široké publish credentials,
- odlišný artifact oproti testovanému source tree.

Controls majú podporovať konkrétny provenance chain, nie iba generický zoznam scannerov.

## 23. Produkčný skeleton

```python
from __future__ import annotations

import argparse
import logging
import uuid

logger = logging.getLogger(__name__)


def run(args: argparse.Namespace) -> AutomationResult:
    config = load_and_validate_config(args)
    operation_id = str(uuid.uuid4())

    with build_adapters(config) as adapters:
        current = adapters.deployment.get_state(
            config.environment,
            config.service,
        )
        desired = build_desired_state(config)
        plan = build_plan(current, desired)
        validate_plan(plan)

        if config.dry_run:
            return AutomationResult(
                environment=config.environment,
                service=config.service,
                changed=bool(plan),
                verified=False,
                version=config.version,
                operation_id=operation_id,
            )

        for change in plan:
            adapters.deployment.apply(
                change,
                operation_id=operation_id,
            )

        actual = wait_for_state(
            adapters.deployment,
            desired,
            timeout_seconds=config.timeout_seconds,
        )
        verify_postconditions(desired, actual)

        return AutomationResult(
            environment=config.environment,
            service=config.service,
            changed=bool(plan),
            verified=True,
            version=config.version,
            operation_id=operation_id,
        )


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
        logger.exception("unexpected automation failure")
        return 1

    emit_result(result, output_format=args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Skeleton je čitateľný podľa lifecycle-u. Konkrétny nástroj ešte potrebuje presné adapters, timeout budget, retry classification, operation-state persistence a compensation policy.

## 24. Diagnostický postup

Keď nástroj funguje lokálne, ale nie v CI alebo scheduleri:

1. over presný executable a Python version,
2. over package path a nainštalovanú version,
3. porovnaj lockfile a runtime dependency graph,
4. skontroluj current working directory a filesystem identity,
5. porovnaj environment allowlist, locale a timezone,
6. over proxy, DNS, TLS trust store a egress,
7. over externé executable súbory a ich versions,
8. čítaj structured phase, operation ID a exit code,
9. reprodukuj rovnaký artifact v čistom prostredí,
10. lokalizuj failure na input, discovery, plan, apply alebo verify boundary.

Diagnostika nemá začínať všeobecným `except Exception: pass` ani okamžitým retryom.

## 25. Referenčné pravidlá

- Konfiguráciu načítaj raz do validovaného immutable objektu.
- Current state považuj za snapshot s freshness alebo version identity.
- Planning drž bez side effects.
- Mutation izoluj v adapters a obmedz preconditions.
- Dry-run má vytvoriť reálny plan.
- Každé externé I/O má timeout a celkový deadline.
- Retry vyžaduje klasifikovanú chybu a opakovateľnú operáciu.
- Timeout mutation považuj za unknown outcome.
- Verification vykonaj novým pozorovaním autoritatívneho state-u.
- Secrets neukladaj do URL, logs, exception textu ani subprocess arguments.
- Concurrency limituj podľa downstream capacity a correctness.
- Package artifact otestuj po inštalácii, nie iba source tree.

## 26. Časté omyly

### „Python skript je automaticky cross-platform“

Nie. Filesystem, signals, permissions, encoding, trust stores a externé tools sa líšia.

### „Type hints validujú vstup“

Nie. Runtime dáta potrebujú parsing a doménové invarianty.

### „Virtual environment je hermetický deployment“

Nie. Izoluje Python packages, nie celý runtime.

### „Úspešný API status znamená úspešnú automatizáciu“

Nie. Payload aj postcondition sa musia samostatne overiť.

### „Retry vyrieši timeout“

Timeout mutation môže znamenať úspech bez doručenej response. Slepy retry môže duplikovať side effect.

### „Exception treba zachytiť čo najskôr“

Zachyť ju až na vrstve, ktorá vie pridať kontext, vykonať recovery alebo ju preložiť na verejný contract.

### „Viac concurrency vždy zrýchli nástroj“

Môže vytvoriť rate-limit, memory, lock alebo timeout cascade.

## 27. Zhrnutie

Produkčný Python automation nástroj je state reconciler s explicitnými boundaries:

```text
validovaný input
→ typed current/desired state
→ auditovateľný plan
→ bounded adapters
→ idempotentná mutation
→ nové observation
→ verified result
```

Python má zmysel vtedy, keď tieto hranice už vyžadujú doménové typy, reusable adapters, test seams a package lifecycle. Jazyk a knižnice sú iba implementačné prostriedky; spoľahlivosť vzniká z presného state, failure a recovery modelu.

## 28. Kontrolné otázky

1. Kedy je Python vhodnejší než Bash alebo PowerShell?
2. Aký je rozdiel medzi dependency declaration, lockom, runtime a artifactom?
3. Prečo config treba načítať do jedného immutable objektu?
4. Prečo current state potrebuje freshness alebo resource version?
5. Aké vlastnosti má deterministický plan?
6. Prečo adapters tvoria failure a test boundaries?
7. Aké štyri odlišné failure vrstvy môže mať HTTP call?
8. Prečo timeout mutation vytvára unknown outcome?
9. Čo musí platiť pre bezpečný retry?
10. Ako compare-and-swap chráni pred stale planom?
11. Prečo verification musí vykonať nové observation?
12. Kedy treba compensation namiesto rollbacku?
13. Prečo bounded concurrency patrí do correctness modelu?
14. Ako odlíšiš library error od top-level process exit code?
15. Ako overíš, že testovaný artifact je skutočne nasadený artifact?

## Glossary impact

Relevantné pojmy: Python runtime, virtual environment, dependency resolver, lockfile, wheel, package entry point, CLI contract, configuration precedence, immutable config, domain model, adapter, current state, desired state, deterministic plan, compare-and-swap, resource version, idempotency key, unknown outcome, retry budget, deadline, bounded concurrency, backpressure, compensation, postcondition verification, package provenance a dependency confusion.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: PowerShell fundamentals](powershell-fundamentals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: YAML, JSON a regular expressions →](yaml-json-regular-expressions.md)
<!-- KNOWLEDGE-NAVIGATION:END -->