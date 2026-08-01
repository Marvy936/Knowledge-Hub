# Praktický CI/CD projekt od source change po overený production release

Táto kapitola skladá princípy celej sekcie do jedného vykonateľného release flowu. Nepoužíva cloud ani Kubernetes, aby bolo viditeľné samotné CI/CD jadro: presný integration candidate, čistý build, build-once artifact, complete evidence, promotion toho istého digestu, oddelený deployment a traffic transition, business verification a recovery bez neovereného rebuildu.

Výsledkom bude malá HTTP aplikácia `payments-api`, lokálny immutable artifact store a dva environmenty reprezentované samostatnými runtime adresármi. Release sa nebude považovať za úspešný po skopírovaní súborov. Musí prejsť cez exact subject manifest, test evidence, staging acceptance, production canary, atomický traffic switch a druhú business operáciu.

```text
source commit a candidate tree
→ clean build workspace
→ unit a contract evidence
→ immutable tar artifact + SHA-256
→ release manifest
→ staging deployment generation
→ staging business acceptance
→ production candidate deployment
→ canary request
→ atomic active-generation switch
→ production business verification
→ evidence closure alebo recovery
```

## Projekt a jeho identity

Vytvor pracovný adresár:

```bash
mkdir -p atlas-cicd/{src,tests,scripts,artifacts,environments,release-evidence}
cd atlas-cicd
git init
```

Repository bude mať túto štruktúru:

```text
atlas-cicd/
├── src/
│   └── payments_api.py
├── tests/
│   └── test_payments_api.py
├── scripts/
│   ├── build.sh
│   ├── verify-artifact.sh
│   ├── deploy.sh
│   ├── verify-environment.sh
│   └── promote-production.sh
├── artifacts/
├── environments/
│   ├── staging/
│   └── production/
└── release-evidence/
```

Release subject nebude iba Git SHA. Manifest zachová source commit, source tree, build-script digest, artifact digest a expected evidence inventory. Commit identifikuje history subject; tree identifikuje source snapshot. Build script je samostatný input, pretože z rovnakého source tree-u môže vytvoriť iný artifact.

## Malá aplikácia a testovateľný business contract

`src/payments_api.py`:

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def authorize(operation_id: str, amount: int, ledger: Path) -> dict[str, object]:
    if amount <= 0 or amount > 10_000:
        raise ValueError("amount must be between 1 and 10000")

    ledger.parent.mkdir(parents=True, exist_ok=True)
    existing: dict[str, dict[str, object]] = {}
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            item = json.loads(line)
            existing[str(item["operationId"])] = item

    if operation_id in existing:
        return existing[operation_id]

    result = {
        "operationId": operation_id,
        "authorizationId": "auth-" + hashlib.sha256(operation_id.encode()).hexdigest()[:10],
        "amount": amount,
        "status": "authorized",
    }
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result, sort_keys=True) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--operation-id", required=True)
    parser.add_argument("--amount", type=int, required=True)
    args = parser.parse_args()
    print(json.dumps(authorize(args.operation_id, args.amount, args.ledger), sort_keys=True))


if __name__ == "__main__":
    main()
```

`tests/test_payments_api.py`:

```python
from pathlib import Path

import pytest

from src.payments_api import authorize


def test_authorize_is_idempotent(tmp_path: Path) -> None:
    ledger = tmp_path / "payments.jsonl"
    first = authorize("op-1001", 500, ledger)
    second = authorize("op-1001", 500, ledger)
    assert first == second
    assert len(ledger.read_text(encoding="utf-8").splitlines()) == 1


def test_invalid_amount_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        authorize("op-invalid", 10_001, tmp_path / "payments.jsonl")
```

Test oracle nie je „Python skončil s nulou“. Prvý test kontroluje business invariant: retry rovnakej operation identity nesmie vytvoriť druhú authorization. Druhý kontroluje forbidden path. Tento invariant sa neskôr overí aj po deploymente, pretože unit test sám nepreukazuje packaging a runtime generation.

## Build vytvára immutable artifact a subject manifest

`scripts/build.sh`:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root"

[[ -z $(git status --porcelain) ]] || {
  echo 'working tree must be clean' >&2
  exit 2
}

source_commit=$(git rev-parse HEAD)
source_tree=$(git rev-parse HEAD^{tree})
build_script_sha=$(sha256sum scripts/build.sh | awk '{print $1}')
build_dir=$(mktemp -d)
trap 'rm -rf -- "$build_dir"' EXIT

python3 -m compileall -q src
pytest -q --junitxml="$build_dir/unit.xml"

mkdir -p "$build_dir/package/src"
cp src/payments_api.py "$build_dir/package/src/"
printf '%s\n' "$source_commit" > "$build_dir/package/SOURCE_COMMIT"
printf '%s\n' "$source_tree" > "$build_dir/package/SOURCE_TREE"

tar --sort=name --mtime='UTC 1970-01-01' \
  --owner=0 --group=0 --numeric-owner \
  -C "$build_dir/package" -czf "$build_dir/payments-api.tgz" .

artifact_sha=$(sha256sum "$build_dir/payments-api.tgz" | awk '{print $1}')
artifact_path="artifacts/sha256-$artifact_sha.tgz"
cp "$build_dir/payments-api.tgz" "$artifact_path"
cp "$build_dir/unit.xml" "release-evidence/unit-$artifact_sha.xml"

python3 - "$source_commit" "$source_tree" "$build_script_sha" "$artifact_sha" "$artifact_path" <<'PY'
import json, sys
commit, tree, build_script, artifact, path = sys.argv[1:]
manifest = {
    "sourceCommit": commit,
    "sourceTree": tree,
    "buildScriptSha256": build_script,
    "artifactSha256": artifact,
    "artifactPath": path,
    "expectedEvidence": ["unit", "artifact-integrity", "staging-business", "production-business"],
}
open(f"release-evidence/release-{artifact}.json", "w", encoding="utf-8").write(
    json.dumps(manifest, indent=2, sort_keys=True) + "\n"
)
PY

printf 'artifact=%s\ndigest=sha256:%s\n' "$artifact_path" "$artifact_sha"
```

`tar --sort`, stabilný timestamp a numeric ownership odstraňujú bežné nondeterministic metadata. To ešte nezaručuje bit-for-bit reproducibility na každej tar/gzip implementácii, ale explicitne zmenšuje implicitný input surface. Artifact sa pomenúva digestom; version tag môže existovať ako ďalší index, no promotion musí používať digest.

Build odmieta dirty working tree, pretože inak by source commit neidentifikoval skutočné bytes. Testy sa vykonajú pred packagingom a JUnit report je viazaný na artifact digest. Dôležité je, že staging ani production už artifact nerebuildnú.

## Integrity read-back

`scripts/verify-artifact.sh`:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

artifact=${1:?usage: verify-artifact.sh ARTIFACT}
expected=${artifact##*/sha256-}
expected=${expected%.tgz}
actual=$(sha256sum "$artifact" | awk '{print $1}')

[[ "$actual" == "$expected" ]] || {
  printf 'digest mismatch: expected=%s actual=%s\n' "$expected" "$actual" >&2
  exit 3
}

tmp=$(mktemp -d)
trap 'rm -rf -- "$tmp"' EXIT
tar -xzf "$artifact" -C "$tmp"
python3 -m py_compile "$tmp/src/payments_api.py"
printf 'verified sha256:%s\n' "$actual"
```

Digest equality dokazuje, že bytes zodpovedajú názvu artifactu. `py_compile` dokazuje, že packaged Python file je syntakticky načítateľný. Ani jedno nepreukazuje business behavior; na to zostávajú test a environment acceptance.

## Deployment vytvára novú environment generation

`scripts/deploy.sh`:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

environment=${1:?usage: deploy.sh ENV ARTIFACT}
artifact=${2:?usage: deploy.sh ENV ARTIFACT}
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)

"$root/scripts/verify-artifact.sh" "$artifact"
digest=${artifact##*/sha256-}
digest=${digest%.tgz}
env_dir="$root/environments/$environment"
generation="$env_dir/releases/$digest"

mkdir -p "$generation"
tar -xzf "$artifact" -C "$generation"
printf 'sha256:%s\n' "$digest" > "$generation/ARTIFACT_DIGEST"

# Candidate publication is separate from traffic activation.
ln -sfn "releases/$digest" "$env_dir/candidate"
printf 'candidate=%s digest=sha256:%s\n' "$generation" "$digest"
```

Deployment je idempotentný voči digestu: opakované rozbalenie rovnakých bytes vytvorí rovnakú generation identity. `candidate` ešte nie je active traffic. Toto oddelenie umožní canary a acceptance pred cutoverom.

## Environment verification

`scripts/verify-environment.sh`:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

environment=${1:?usage: verify-environment.sh ENV LINK OPERATION_ID}
link=${2:?usage: verify-environment.sh ENV LINK OPERATION_ID}
operation_id=${3:?usage: verify-environment.sh ENV LINK OPERATION_ID}
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
env_dir="$root/environments/$environment"
runtime=$(readlink -f "$env_dir/$link")
ledger="$env_dir/data/payments.jsonl"

[[ -f "$runtime/ARTIFACT_DIGEST" ]] || { echo 'missing artifact identity' >&2; exit 5; }
first=$(python3 "$runtime/src/payments_api.py" --ledger "$ledger" --operation-id "$operation_id" --amount 500)
second=$(python3 "$runtime/src/payments_api.py" --ledger "$ledger" --operation-id "$operation_id" --amount 500)

[[ "$first" == "$second" ]] || { echo 'idempotency verification failed' >&2; exit 5; }
printf '%s\n' "$first"
printf 'runtime=%s artifact=%s\n' "$runtime" "$(cat "$runtime/ARTIFACT_DIGEST")"
```

Verifier číta symlink, ktorý reprezentuje serving generation, a vykoná dve rovnaké business operations. Druhý request je dôležitý: prvý môže uspieť a retry vytvoriť duplicate. Ledger je environment-owned persistent state a nepatrí do release directory, preto prežije generation switch.

## Staging acceptance a promotion evidence

Po prvom commite:

```bash
chmod +x scripts/*.sh
git add .
git commit -m 'add payments release project'

build_output=$(scripts/build.sh)
printf '%s\n' "$build_output"
artifact=$(awk -F= '/^artifact=/{print $2}' <<<"$build_output")

scripts/deploy.sh staging "$artifact"
ln -sfn "$(readlink environments/staging/candidate)" environments/staging/active
scripts/verify-environment.sh staging active staging-op-1001
```

Promotion proposal musí identifikovať artifact a staging evidence, nie iba branch alebo version label:

```bash
digest=${artifact##*/sha256-}; digest=${digest%.tgz}
cat >"release-evidence/promotion-$digest.json" <<EOF
{
  "artifactSha256": "$digest",
  "stagingGeneration": "$(readlink environments/staging/active)",
  "stagingOperation": "staging-op-1001",
  "decision": "approved-for-production"
}
EOF
```

V reálnom systéme by approval niesla identity, policy generation, čas a signature/audit event. Lokálny súbor demonštruje subject binding. Ak sa artifact zmení, staré approval evidence sa nesmie použiť.

## Production canary a atomický switch

`scripts/promote-production.sh`:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

artifact=${1:?usage: promote-production.sh ARTIFACT}
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
digest=${artifact##*/sha256-}; digest=${digest%.tgz}
approval="$root/release-evidence/promotion-$digest.json"

[[ -f "$approval" ]] || { echo 'missing digest-bound approval' >&2; exit 3; }
grep -q 'approved-for-production' "$approval" || { echo 'approval is not valid' >&2; exit 3; }

"$root/scripts/deploy.sh" production "$artifact"
"$root/scripts/verify-environment.sh" production candidate "canary-$digest"

previous=''
[[ -L "$root/environments/production/active" ]] && previous=$(readlink "$root/environments/production/active")
ln -sfn "$(readlink "$root/environments/production/candidate")" "$root/environments/production/active"

if ! "$root/scripts/verify-environment.sh" production active "prod-$digest"; then
  if [[ -n "$previous" ]]; then
    ln -sfn "$previous" "$root/environments/production/active"
  fi
  echo 'production verification failed; active generation restored' >&2
  exit 5
fi

printf 'production active=%s\n' "$(readlink "$root/environments/production/active")"
```

Canary sa vykoná nad `candidate`, teda nad exact unpacked artifact pred aktiváciou. `ln -sfn` je lokálny model atomického route switchu; existujúci process alebo request model v skutočnej platforme môže mať vlastné drain a connection semantics. Po switchi sa test zopakuje cez `active`, pretože candidate success nepreukazuje serving path.

## Failure walkthrough: rebuild po schválení

Zámerne vytvor druhý tar z rovnakého source-u s odlišným timestampom alebo dodatočným file-om a pokús sa použiť staré approval evidence. Nový digest nemá `promotion-<digest>.json`, takže production gate zlyhá pred mutation.

```bash
cp "$artifact" /tmp/original.tgz
mkdir -p /tmp/rebuild && tar -xzf "$artifact" -C /tmp/rebuild
date > /tmp/rebuild/BUILD_TIME
tar -C /tmp/rebuild -czf artifacts/rebuilt.tgz .
scripts/promote-production.sh artifacts/rebuilt.tgz
```

Prvý možný failure je už integrity naming: `rebuilt.tgz` nemá digest-bound názov. Aj keby sa premenoval podľa nového SHA, approval pre pôvodný digest sa neprenesie. To je podstata build-once-promote-many.

## Failure walkthrough: unknown deployment outcome

Predstav si, že command po `ln -sfn` stratí response alebo job runner zanikne. Výsledok nie je bezpečné klasifikovať ako „nič sa nestalo“. Recovery najprv read-backne:

```bash
readlink environments/production/active
readlink environments/production/candidate
cat "$(readlink -f environments/production/active)/ARTIFACT_DIGEST"
tail -n 5 environments/production/data/payments.jsonl
```

Až potom rozhodne, či pokračovať vo verification, obnoviť predošlý link alebo vykonať nový release transition. Blind retry promotion scriptu môže byť bezpečný iba preto, že deploy a business operation používajú stabilné digest/operation identities; bez nich by mohol vytvoriť duplicate side effects.

## Cleanup a acceptance

```bash
rm -rf environments artifacts release-evidence
```

V reálnom systéme sa artifacts a evidence nemažú týmto spôsobom; cleanup je určený iba lokálnemu labu. Acceptance walkthroughu vyžaduje:

```text
source commit a tree sú zaznamenané
build odmietne dirty workspace
unit a forbidden test prejdú
artifact má digest-bound identity
staging a production používajú tie isté bytes
approval je viazaná na digest
candidate sa overí pred traffic switchom
active generation sa read-backne
business retry nevytvorí duplicate
unknown outcome sa rieši observation-first
neoverený rebuild sa nedá promovovať
```

Walkthrough tým spája CI, delivery, deployment, promotion, progressive exposure a recovery do jedného vykonateľného modelu. Nezávisí od konkrétneho CI produktu; GitLab, GitHub Actions alebo Jenkins majú implementovať rovnaké subject a evidence boundaries.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Databázová kompatibilita počas deploymentu](database-compatibility-during-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Projects, groups a permissions →](../06-gitlab/projects-groups-permissions.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
