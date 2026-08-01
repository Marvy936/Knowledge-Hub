# Praktický Git a automation projekt od prázdneho adresára po overený apply

Táto kapitola spojí celý section model do jedného vykonateľného projektu. Najprv vytvoríme bare remote a seed repository, potom dve samostatné clones pre Alice a Boba. Obe clones vytvoria platné, ale navzájom konfliktné changes. Prejdeme rejected push, fetch, rebase conflict, semantic resolution, annotated tag a reflog recovery. Až potom repository doplníme o Python automation tool, Bash wrapper, PowerShell wrapper a tests.

Lab používa iba lokálny filesystem. Git transport je file-based, takže nepotrebuje účet ani network. Python a Bash časti sú executable na Linuxe. PowerShell časť vyžaduje PowerShell 7 a v tomto documentation workflowe sa nespúšťa.

## 1. Pracovný adresár a identity

Vytvor izolovaný adresár:

```bash
mkdir -p atlas-git-automation-lab
cd atlas-git-automation-lab
```

Nastav identities iba pre lab repositories, nie globálne. Budeme ich nastavovať po clone.

Výsledný layout bude:

```text
atlas-git-automation-lab/
├── origin.git/          # bare remote
├── seed/                # bootstrap repository
├── alice/               # prvá clone
└── bob/                 # druhá clone
```

## 2. Bare remote a seed repository

```bash
git init --bare origin.git

git init seed
cd seed
git config user.name 'Atlas Bootstrap'
git config user.email 'bootstrap@atlas.example'
git switch -c main

mkdir -p config schemas tools scripts state tests
```

Vytvor `config/orders.yaml`. Súbor má príponu YAML, ale používa JSON syntax, ktorá je kompatibilným YAML 1.2 subsetom. Praktický tool ho preto dokáže načítať štandardnou Python `json` knižnicou bez externých dependencies.

```yaml
{
  "service": "orders-api",
  "environment": "dev",
  "release": "4.2.0",
  "maxOrderAmount": 5000,
  "currency": "EUR"
}
```

Vytvor `schemas/orders.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["service", "environment", "release", "maxOrderAmount", "currency"],
  "properties": {
    "service": {"const": "orders-api"},
    "environment": {"enum": ["dev", "staging", "production"]},
    "release": {"type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$"},
    "maxOrderAmount": {"type": "integer", "minimum": 1, "maximum": 1000000},
    "currency": {"enum": ["EUR", "USD", "GBP"]}
  }
}
```

Schema je dokumentačný contract. Zero-dependency lab ju nepoužíva cez externú `jsonschema` library; Python tool implementuje rovnaké required/type/range checks priamo. V production riešení sa parser a schema validator pinujú ako dependencies a testuje sa ich verzia.

Pridaj `.gitignore`:

```gitignore
__pycache__/
*.pyc
state/*.json
state/*.lock
.tmp/
```

Prvý commit:

```bash
git add config schemas .gitignore
git diff --cached
git commit -m 'bootstrap Atlas Orders delivery repository'
git remote add origin ../origin.git
git push -u origin main
git --git-dir=../origin.git symbolic-ref HEAD refs/heads/main
cd ..
```

Read-back:

```bash
git --git-dir=origin.git show-ref
git --git-dir=origin.git log --oneline --decorate --all
```

Bare repository nemá working tree. Jeho authoritative viditeľný state sú objects a refs.

## 3. Dve samostatné clones

```bash
git clone origin.git alice
git clone origin.git bob
git -C alice config user.name 'Alice'
git -C alice config user.email 'alice@atlas.example'
git -C bob config user.name 'Bob'
git -C bob config user.email 'bob@atlas.example'
```

Over:

```bash
git -C alice branch -vv
git -C bob branch -vv
git -C alice rev-parse HEAD
git -C bob rev-parse HEAD
```

Obe local `main` a oba `origin/main` začínajú na rovnakom commite. Od tejto chvíle sa však repositories vyvíjajú nezávisle.

## 4. Alice vytvorí feature branch a object evidence

```bash
cd alice
git switch -c feature/ord-8421
```

Zmeň `maxOrderAmount` z `5000` na `6000` a release na `4.2.1`:

```bash
python3 - <<'PY2'
import json
from pathlib import Path
path = Path('config/orders.yaml')
value = json.loads(path.read_text(encoding='utf-8'))
value['release'] = '4.2.1'
value['maxOrderAmount'] = 6000
path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
PY2
```

Pred stagingom sleduj vrstvy:

```bash
git status --short
git diff
```

Vytvor blob priamo a potom stage-ni file:

```bash
blob=$(git hash-object -w config/orders.yaml)
printf 'blob=%s\n' "$blob"
git cat-file -t "$blob"
git cat-file -p "$blob"

git add config/orders.yaml
git diff --cached
git ls-files --stage config/orders.yaml
```

Commit:

```bash
git commit -m 'ORD-8421 raise development order limit'
```

Preskúmaj graph:

```bash
git cat-file -p HEAD
git show --stat --decorate HEAD
git rev-parse HEAD^{tree}
```

Zatiaľ branch nepushuj.

## 5. Bob paralelne zmení rovnaký contract

V druhom termináli alebo po návrate do parent directory:

```bash
cd ../bob
git switch -c feature/ord-8450
```

Bob mení rovnaký limit na 7000, ale release field ponechá na `4.2.0`:

```bash
python3 - <<'PY2'
import json
from pathlib import Path
path = Path('config/orders.yaml')
value = json.loads(path.read_text(encoding='utf-8'))
value['maxOrderAmount'] = 7000
path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
PY2

git add config/orders.yaml
git commit -m 'ORD-8450 align order limit with risk policy'
```

Bob integruje change do `main` a pushne ho:

```bash
git switch main
git merge --ff-only feature/ord-8450
git push origin main
```

Remote `main` teraz obsahuje Bobov commit. Alice local remote-tracking ref to ešte nevie.

## 6. Alice dostane non-fast-forward a najprv pozoruje

```bash
cd ../alice
git switch main
git merge --ff-only feature/ord-8421
```

Alice sa pokúsi pushnúť:

```bash
git push origin main
```

Push musí byť odmietnutý ako non-fast-forward. Namiesto force pushu:

```bash
git fetch origin
git log --oneline --graph --decorate --all
git log --left-right --oneline main...origin/main
```

Teraz je divergence explicitná. Local `main` obsahuje Alice commit, `origin/main` Bob commit.

## 7. Rebase a conflict inputs

Vytvor safety ref:

```bash
git branch backup/alice-before-rebase
```

Spusť:

```bash
git rebase origin/main
```

Rebase sa zastaví na `config/orders.yaml`. Pozri tri stages:

```bash
git status
git ls-files -u
git show :1:config/orders.yaml
git show :2:config/orders.yaml
git show :3:config/orders.yaml
```

Pri rebase nepoužívaj `ours/theirs` mechanicky. Bobov main a replayovaný Alice commit majú odlišné business intenty. Tím rozhodne, že risk policy 7000 je maximum, no Alice zmena má pridať explicitný `release` bump. Výsledný file bude:

```json
{
  "service": "orders-api",
  "environment": "dev",
  "release": "4.2.1",
  "maxOrderAmount": 7000,
  "currency": "EUR"
}
```

Zapíš ho a pokračuj:

```bash
cat > config/orders.yaml <<'JSON'
{
  "service": "orders-api",
  "environment": "dev",
  "release": "4.2.1",
  "maxOrderAmount": 7000,
  "currency": "EUR"
}
JSON

git add config/orders.yaml
GIT_EDITOR=true git rebase --continue
```

Rebase vytvoril nový Alice commit. Porovnaj sériu:

```bash
git range-diff backup/alice-before-rebase~1..backup/alice-before-rebase \
               origin/main..main
```

Final diff môže byť prázdny alebo obsahovať iba intent, ktorý po resolution zostal. To je dôležitý review výsledok: Alice pôvodná hodnota 6000 nebola slepo zachovaná.

Push je teraz fast-forward:

```bash
git push origin main
```

## 8. Annotated release tag

```bash
git tag -a v4.2.1 -m 'Atlas Orders 4.2.1'
git show v4.2.1
git push origin v4.2.1
```

Over remote:

```bash
git ls-remote --heads --tags origin
```

Tag nemeníme. Ďalšia oprava dostane novú verziu.

## 9. Accidental reset a reflog recovery

Na local `main` vytvor safety marker:
```bash
before_reset=$(git rev-parse HEAD)
printf 'before_reset=%s\n' "$before_reset"
```

Simuluj omyl:

```bash
git reset --hard HEAD~1
```

Remote sa nemení. Reflog:

```bash
git reflog -5
```

Najprv zachovaj stratený tip:

```bash
git branch recovery/from-reflog "$before_reset"
```

Potom vráť main bez force pushu:

```bash
git reset --hard origin/main
```

Ak by commit nebol na remote, recovery branch by zostala jediným stabilným refom. Reflog nie je dlhodobý backup, preto sa recovery ref vytvára okamžite.

## 10. Automation tool

V repository `alice` vytvor ďalšie files. Najprv vytvor adresáre:

```bash
mkdir -p tools scripts state tests
```

Python tool je zámerne Linux-oriented v lock implementation, pretože používa `fcntl`. PowerShell wrapper môže volať ten istý tool na WSL/Linux path-e; pre natívny Windows state lock by production verzia potrebovala cross-platform locking abstraction.

`tools/atlasctl.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

EXIT_INVALID_INPUT = 2
EXIT_PRECONDITION = 3
EXIT_APPLY_FAILURE = 4
EXIT_VERIFY_FAILURE = 5


class AtlasError(Exception):
    exit_code = 1


class InvalidInput(AtlasError):
    exit_code = EXIT_INVALID_INPUT


class PreconditionFailed(AtlasError):
    exit_code = EXIT_PRECONDITION


class ApplyFailed(AtlasError):
    exit_code = EXIT_APPLY_FAILURE


class VerifyFailed(AtlasError):
    exit_code = EXIT_VERIFY_FAILURE


@dataclass(frozen=True)
class OrdersConfig:
    service: str
    environment: str
    release: str
    maxOrderAmount: int
    currency: str


EXPECTED_KEYS = {
    "service",
    "environment",
    "release",
    "maxOrderAmount",
    "currency",
}


def load_json_compatible_yaml(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise InvalidInput(f"file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InvalidInput(
            f"{path} must use the JSON-compatible YAML subset: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise InvalidInput(f"{path} must contain an object")
    return value


def validate_config(value: dict[str, Any]) -> OrdersConfig:
    keys = set(value)
    if keys != EXPECTED_KEYS:
        missing = sorted(EXPECTED_KEYS - keys)
        unknown = sorted(keys - EXPECTED_KEYS)
        raise InvalidInput(f"invalid keys; missing={missing}, unknown={unknown}")
    if value["service"] != "orders-api":
        raise InvalidInput("service must be orders-api")
    if value["environment"] not in {"dev", "staging", "production"}:
        raise InvalidInput("environment is not supported")
    if not isinstance(value["maxOrderAmount"], int) or isinstance(
        value["maxOrderAmount"], bool
    ):
        raise InvalidInput("maxOrderAmount must be an integer")
    if not 1 <= value["maxOrderAmount"] <= 1_000_000:
        raise InvalidInput("maxOrderAmount is outside the allowed range")
    if value["currency"] not in {"EUR", "USD", "GBP"}:
        raise InvalidInput("currency is not supported")
    if not isinstance(value["release"], str) or not re.fullmatch(
        r"[0-9]+\.[0-9]+\.[0-9]+", value["release"]
    ):
        raise InvalidInput("release must use MAJOR.MINOR.PATCH")
    return OrdersConfig(**value)


def canonical(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def load_config(path: Path) -> OrdersConfig:
    return validate_config(load_json_compatible_yaml(path))


def load_state(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return load_json_compatible_yaml(path)


def state_fingerprint(state: dict[str, Any] | None) -> str | None:
    return None if state is None else fingerprint(state)


def build_plan(config: OrdersConfig, state: dict[str, Any] | None) -> dict[str, Any]:
    desired = asdict(config)
    changes: dict[str, dict[str, Any]] = {}
    for key, desired_value in desired.items():
        current_value = None if state is None else state.get(key)
        if current_value != desired_value:
            changes[key] = {"from": current_value, "to": desired_value}
    return {
        "schemaVersion": 1,
        "desiredFingerprint": fingerprint(desired),
        "observedFingerprint": state_fingerprint(state),
        "changed": bool(changes),
        "changes": changes,
        "desired": desired,
    }


def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, sort_keys=True, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    except OSError as exc:
        raise ApplyFailed(f"unable to write {path}: {exc}") from exc
    finally:
        temp_path.unlink(missing_ok=True)


def read_plan(path: Path) -> dict[str, Any]:
    value = load_json_compatible_yaml(path)
    if value.get("schemaVersion") != 1:
        raise InvalidInput("unsupported plan schemaVersion")
    required = {
        "desiredFingerprint",
        "observedFingerprint",
        "changed",
        "changes",
        "desired",
    }
    if not required.issubset(value):
        raise InvalidInput("plan is missing required fields")
    return value

def command_plan(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config))
    state = load_state(Path(args.state))
    print(json.dumps(build_plan(config, state), sort_keys=True, indent=2))
    return 0


def command_apply(args: argparse.Namespace) -> int:
    config_path = Path(args.config)
    state_path = Path(args.state)
    plan = read_plan(Path(args.plan))

    lock_path = state_path.with_suffix(state_path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock_handle:
        try:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise PreconditionFailed("another apply is already running") from exc

        config = load_config(config_path)
        state = load_state(state_path)
        desired = asdict(config)

        if fingerprint(desired) != plan["desiredFingerprint"]:
            raise PreconditionFailed("desired configuration changed after plan")
        if state_fingerprint(state) != plan["observedFingerprint"]:
            raise PreconditionFailed("observed state changed after plan")

        changed = state != desired
        if changed:
            atomic_write_json(state_path, desired)

        result = {
            "status": "applied",
            "changed": changed,
            "desiredFingerprint": fingerprint(desired),
            "statePath": str(state_path),
        }
        print(json.dumps(result, sort_keys=True))
    return 0


def command_verify(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config))
    desired = asdict(config)
    state_path = Path(args.state)
    state = load_state(state_path)
    if state != desired:
        raise VerifyFailed(
            f"state does not match desired configuration: {state_path}"
        )
    print(
        json.dumps(
            {
                "status": "verified",
                "changed": False,
                "desiredFingerprint": fingerprint(desired),
                "statePath": str(state_path),
            },
            sort_keys=True,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="atlasctl")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "verify"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--config", required=True)
        cmd.add_argument("--state", required=True)
    apply_cmd = sub.add_parser("apply")
    apply_cmd.add_argument("--config", required=True)
    apply_cmd.add_argument("--state", required=True)
    apply_cmd.add_argument("--plan", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            return command_plan(args)
        if args.command == "apply":
            return command_apply(args)
        if args.command == "verify":
            return command_verify(args)
        raise AssertionError(f"unhandled command: {args.command}")
    except AtlasError as exc:
        print(str(exc), file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
```

Tool oddeľuje:

```text
parse a domain validation
→ canonical desired fingerprint
→ observed state fingerprint
→ plan
→ lock
→ precondition recheck
→ atomic write
→ independent verify
```

Plan obsahuje desired aj observed fingerprint. Apply odmietne stale config aj state.

## 11. Bash wrapper

Vytvor `scripts/release.sh`:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
CONFIG="$ROOT/config/orders.yaml"
STATE="$ROOT/state/dev.json"
DRY_RUN=0

while (($#)); do
  case $1 in
    --config)
      (($# >= 2)) || { echo 'missing value for --config' >&2; exit 2; }
      CONFIG=$2
      shift 2
      ;;
    --state)
      (($# >= 2)) || { echo 'missing value for --state' >&2; exit 2; }
      STATE=$2
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    *)
      printf 'unknown argument: %s\n' "$1" >&2
      exit 2
      ;;
  esac
done

if ! git -C "$ROOT" diff --quiet || ! git -C "$ROOT" diff --cached --quiet; then
  echo 'repository has tracked changes; commit or stash them first' >&2
  exit 3
fi

TMP_DIR=$(mktemp -d)
cleanup() {
  rc=$?
  rm -rf -- "$TMP_DIR"
  exit "$rc"
}
trap cleanup EXIT INT TERM

PLAN="$TMP_DIR/plan.json"
python3 "$ROOT/tools/atlasctl.py" plan \
  --config "$CONFIG" \
  --state "$STATE" >"$PLAN"

if ((DRY_RUN)); then
  cat "$PLAN"
  exit 0
fi

python3 "$ROOT/tools/atlasctl.py" apply \
  --config "$CONFIG" \
  --state "$STATE" \
  --plan "$PLAN" >&2

python3 "$ROOT/tools/atlasctl.py" verify \
  --config "$CONFIG" \
  --state "$STATE"
```

Nastav executable bit:

```bash
chmod +x tools/atlasctl.py scripts/release.sh
```

Wrapper odmietne tracked dirty tree. Untracked runtime state je povolený, pretože `state/dev.json` sa v tomto lab-e commitovať nebude. V reálnom systéme by runtime state typicky žil mimo source repository úplne.

## 12. PowerShell wrapper

Vytvor `scripts/Release-Orders.ps1`:

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'Medium')]
param(
    [string]$ConfigPath = (Join-Path $PSScriptRoot '..\config\orders.yaml'),
    [string]$StatePath = (Join-Path $PSScriptRoot '..\state\dev.json')
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Tool = Join-Path $Root 'tools\atlasctl.py'
$Plan = Join-Path ([System.IO.Path]::GetTempPath()) ("atlas-plan-{0}.json" -f [guid]::NewGuid())

try {
    & git -C $Root diff --quiet
    if ($LASTEXITCODE -eq 1) { throw 'Repository has unstaged tracked changes.' }
    if ($LASTEXITCODE -ne 0) { throw "git diff failed: $LASTEXITCODE" }

    & git -C $Root diff --cached --quiet
    if ($LASTEXITCODE -eq 1) { throw 'Repository has staged changes.' }
    if ($LASTEXITCODE -ne 0) { throw "git diff --cached failed: $LASTEXITCODE" }

    & python $Tool plan --config $ConfigPath --state $StatePath |
        Set-Content -LiteralPath $Plan -Encoding utf8NoBOM
    if ($LASTEXITCODE -ne 0) { throw "plan failed: $LASTEXITCODE" }
    if ($PSCmdlet.ShouldProcess($StatePath, 'Apply Atlas Orders configuration')) {
        & python $Tool apply --config $ConfigPath --state $StatePath --plan $Plan
        if ($LASTEXITCODE -ne 0) { throw "apply failed: $LASTEXITCODE" }

        $verified = & python $Tool verify --config $ConfigPath --state $StatePath
        if ($LASTEXITCODE -ne 0) { throw "verify failed: $LASTEXITCODE" }
        $verified | ConvertFrom-Json
    }
    else {
        Get-Content -LiteralPath $Plan -Raw | ConvertFrom-Json
    }
}
finally {
    Remove-Item -LiteralPath $Plan -Force -ErrorAction SilentlyContinue
}
```

Wrapper používa object output, `ShouldProcess`, `LiteralPath` a okamžitú kontrolu `$LASTEXITCODE`. `-WhatIf` vytvorí plan, ale nevykoná apply.

## 13. Tests

Vytvor `tests/test_atlasctl.py`:

```python
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "tools" / "atlasctl.py"
spec = importlib.util.spec_from_file_location("atlasctl", MODULE_PATH)
assert spec and spec.loader
atlasctl = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = atlasctl
spec.loader.exec_module(atlasctl)


class AtlasCtlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.config = self.root / "orders.yaml"
        self.state = self.root / "state.json"
        self.plan = self.root / "plan.json"
        self.write_config(5000)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_config(self, amount: int) -> None:
        self.config.write_text(
            json.dumps(
                {
                    "service": "orders-api",
                    "environment": "dev",
                    "release": "4.2.0",
                    "maxOrderAmount": amount,
                    "currency": "EUR",
                }
            ),
            encoding="utf-8",
        )

    def make_plan(self) -> None:
        config = atlasctl.load_config(self.config)
        state = atlasctl.load_state(self.state)
        self.plan.write_text(
            json.dumps(atlasctl.build_plan(config, state)), encoding="utf-8"
        )

    def test_apply_and_second_noop(self) -> None:
        self.make_plan()
        args = type("Args", (), {
            "config": str(self.config),
            "state": str(self.state),
            "plan": str(self.plan),
        })()
        self.assertEqual(atlasctl.command_apply(args), 0)
        self.make_plan()
        self.assertEqual(atlasctl.command_apply(args), 0)
        self.assertEqual(
            json.loads(self.state.read_text(encoding="utf-8"))["maxOrderAmount"],
            5000,
        )

    def test_stale_desired_plan_is_rejected(self) -> None:
        self.make_plan()
        self.write_config(6000)
        args = type("Args", (), {
            "config": str(self.config),
            "state": str(self.state),
            "plan": str(self.plan),
        })()
        with self.assertRaises(atlasctl.PreconditionFailed):
            atlasctl.command_apply(args)

    def test_unknown_key_is_rejected(self) -> None:
        value = json.loads(self.config.read_text(encoding="utf-8"))
        value["unexpected"] = True
        self.config.write_text(json.dumps(value), encoding="utf-8")
        with self.assertRaises(atlasctl.InvalidInput):
            atlasctl.load_config(self.config)


if __name__ == "__main__":
    unittest.main()
```

Spusť:

```bash
python3 -m py_compile tools/atlasctl.py tests/test_atlasctl.py
bash -n scripts/release.sh
python3 -m unittest discover -s tests -v
```

Tests pokrývajú prvý apply, druhý no-op apply, stale desired plan a unknown key. Production suite by doplnila stale observed state, lock contention, write failure, signal a permission paths.

## 14. Commit automation change

```bash
git add tools scripts tests schemas config .gitignore
git diff --cached --check
git diff --cached
git commit -m 'add fingerprinted plan apply verify automation'
git push origin main
```

Over exact subject:

```bash
git status --short
git rev-parse HEAD
git rev-parse origin/main
git diff --exit-code origin/main..HEAD
```

## 15. Dry-run a prvý apply

Working tree musí byť clean:

```bash
./scripts/release.sh --dry-run
```

Plan ukáže `changed: true`, pretože `state/dev.json` ešte neexistuje.

Apply:

```bash
./scripts/release.sh
```

Stdout obsahuje finálny verify JSON. Apply progress ide na stderr. Read-back:

```bash
cat state/dev.json
python3 tools/atlasctl.py verify \
  --config config/orders.yaml \
  --state state/dev.json
```

## 16. Druhý no-op run

```bash
./scripts/release.sh --dry-run
./scripts/release.sh
```

Plan má `changed: false` a apply nevykoná write. Idempotencia sa neposudzuje iba podľa exit code-u; plan a state fingerprint musia zostať rovnaké.

## 17. Stale-plan failure

Vytvor plan:

```bash
python3 tools/atlasctl.py plan \
  --config config/orders.yaml \
  --state state/dev.json > /tmp/atlas-plan.json
```

Potom zmeň desired config bez vytvorenia nového planu:

```bash
python3 - <<'PY2'
import json
from pathlib import Path
path = Path('config/orders.yaml')
value = json.loads(path.read_text(encoding='utf-8'))
value['maxOrderAmount'] = 7500
path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
PY2
```

Apply starého planu:

```bash
set +e
python3 tools/atlasctl.py apply \
  --config config/orders.yaml \
  --state state/dev.json \
  --plan /tmp/atlas-plan.json
rc=$?
set -e
printf 'exit=%s\n' "$rc"
test "$rc" -eq 3
```

State sa nesmie zmeniť:

```bash
cat state/dev.json
```

Obnov working tree:

```bash
git restore config/orders.yaml
rm -f /tmp/atlas-plan.json
```

Stale-plan protection zabraňuje apply-u subjectu, ktorý už nebol reviewovaný v plan outpute.
## 18. Dirty-tree gate

Zmeň tracked file bez commitu:

```bash
printf '\n' >> config/orders.yaml
```

Wrapper musí odmietnuť execution:

```bash
set +e
./scripts/release.sh --dry-run
rc=$?
set -e
printf 'exit=%s\n' "$rc"
test "$rc" -eq 3
git restore config/orders.yaml
```

Tento gate viaže automation na clean source subject. Neoveruje remote freshness; produkčný release wrapper by navyše fetchol remote a porovnal exact protected ref alebo CI-provided commit.

## 19. PowerShell read-back

Na hoste s PowerShell 7:

```powershell
./scripts/Release-Orders.ps1 -WhatIf
./scripts/Release-Orders.ps1
```

Prvý command vráti plan object bez mutation. Druhý vráti verified object. Ak `python` command nie je dostupný pod týmto názvom, wrapper má explicitne dostať interpreter path; nemá ticho použiť inú runtime verziu.

## 20. Final acceptance a cleanup

Final evidence:

```bash
git status --short
git log --oneline --graph --decorate --all --max-count=20
git show-ref --heads --tags
git fsck --full
python3 -m unittest discover -s tests -v
./scripts/release.sh --dry-run
python3 tools/atlasctl.py verify \
  --config config/orders.yaml \
  --state state/dev.json
```

Acceptance znamená:

```text
remote main je fast-forward integrovaný
tag v4.2.1 ukazuje na schválený commit
conflict resolution zachovala risk policy aj release intent
reflog recovery vytvorila stabilný recovery ref
Python tests prešli
Bash syntax prešla
plan/apply/verify pracujú nad fingerprintami
stale plan je odmietnutý s exit 3
second apply je no-op
runtime state zodpovedá desired configu
```

Po skončení možno celý lab odstrániť z parent directory:

```bash
cd ..
rm -rf atlas-git-automation-lab
```

Git a automation flow v tejto kapitole nepreukazuje hosting branch protection, signed commits, distributed lock, remote API idempotency ani Windows-native lock semantics. Tie potrebujú samostatné platformové testy.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: YAML, JSON a regular expressions](yaml-json-regular-expressions.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Verification vs. validation →](../04-testing-and-quality/verification-vs-validation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
