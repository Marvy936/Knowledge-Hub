# Bash automation

Atlas potrebuje jednoduchý wrapper, ktorý overí repository stav, vytvorí automation plan, vykoná apply a zachová diagnostické outputs. Bash je vhodný, keď orchestration zostáva prevažne nad command-line tools a dátový model je malý. Je však nemilosrdný k nequotovaným hodnotám, pipeline exit statusom a nejasnej cleanup hranici.

## Skript ako kontrakt

Bezpečný skript najprv definuje inputs, outputs, side effects a exit codes. Príklad interface-u:

```text
release.sh --config PATH --state PATH [--dry-run]

stdout: machine-readable final JSON
stderr: progress a diagnostics
0: desired state verified
2: invalid input
3: precondition alebo stale plan
4: apply failure
5: verification failure
```

Keď stdout obsahuje progress aj JSON, ďalšia automatizácia ho nevie spoľahlivo parsovať. Streams sú súčasť API contractu.

## Strict mode s pochopením hraníc

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
```

`-e` ukončí shell pri niektorých neúspešných simple commands, ale má kontextové výnimky v podmienkach, pipelines a subshells. Nie je náhradou explicitného error handlingu. `-u` odhalí unset variables, no optional values musia používať `${value:-}`. `pipefail` zabezpečí, že pipeline nezakryje failure skoršieho commandu.

```bash
if ! output=$(command-that-may-fail 2>&1); then
  printf 'command failed: %s\n' "$output" >&2
  exit 4
fi
```

Explicitná branch je čitateľnejšia než spoliehanie sa na jemné `errexit` pravidlá.

## Quoting a arrays

Premenná môže obsahovať spaces, glob znaky alebo newline. Bezpečný default je quote:

```bash
python3 "$tool" --config "$config_path"
```

Command arguments sa skladajú arrayom:

```bash
args=(plan --config "$config_path" --state "$state_path")
((dry_run)) && args+=(--dry-run)
python3 "$tool" "${args[@]}"
```

String `cmd="python3 ..."; $cmd` je chybný parser model. Shell znovu rozdelí words a môže expandovať globy. `eval` pridáva ďalšiu parse vrstvu a injection risk.

## Argument parser

```bash
while (($#)); do
  case $1 in
    --config)
      (($# >= 2)) || { echo 'missing value for --config' >&2; exit 2; }
      config_path=$2
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    --)
      shift
      break
      ;;
    *)
      printf 'unknown argument: %s\n' "$1" >&2
      exit 2
      ;;
  esac
done
```

Parser musí odmietnuť unknown options a chýbajúce values. Tiché ignorovanie typo-u môže zmeniť production behavior.

## Temporary files a trap

```bash
tmp_dir=$(mktemp -d)
cleanup() {
  rc=$?
  rm -rf -- "$tmp_dir"
  exit "$rc"
}
trap cleanup EXIT INT TERM
```

Trap zachová pôvodný exit code a odstráni iba resource, ktoré skript vytvoril. Cleanup nemá mazať shared path podľa nevalidovaného inputu.

Pri secrets treba používať restrictive permissions a nevypisovať obsah do trace. `set -x` v credential path-e je častý leak.

## Locking

Dva apply runs nad rovnakým state file-om môžu prepísať novší výsledok. Na Linuxe:

```bash
exec 9>"$state_path.lock"
if ! flock -n 9; then
  echo 'another apply is running' >&2
  exit 3
fi
```

Lock identity musí zodpovedať mutation subjectu. Globálny lock znižuje concurrency; príliš úzky lock nechráni shared state. File lock na lokálnom filesystéme nie je automaticky distribuovaný lock.

## Plan, apply a verify

Bash wrapper nemá znovu implementovať business parser, ak Python tool už poskytuje typed contract:

```bash
plan_file="$tmp_dir/plan.json"
python3 tools/atlasctl.py plan \
  --config "$config_path" \
  --state "$state_path" \
  >"$plan_file"

if ((dry_run)); then
  cat "$plan_file"
  exit 0
fi

python3 tools/atlasctl.py apply \
  --config "$config_path" \
  --state "$state_path" \
  --plan "$plan_file"

python3 tools/atlasctl.py verify \
  --config "$config_path" \
  --state "$state_path"
```

Plan file je immutable subject iba v rámci svojich fingerprints a observation time. Apply musí overiť, že config aj observed state sa od planu nezmenili.

## Native command exit a pipelines

```bash
if ! git diff --quiet; then
  echo 'working tree is dirty' >&2
  exit 3
fi
```

Nie každý non-zero exit znamená rovnakú vec. `grep` používa 1 pre no match a 2 pre error. `git diff --quiet` používa 1 pre rozdiel. Skript musí interpretovať command-specific contract, nie všetko označiť za „crash“.

Pipeline:

```bash
result=$(producer | jq -e '.status == "verified"')
```

s `pipefail` zlyhá pri producer aj jq failure. Bez neho môže posledný úspešný command zakryť skorší problém.

## Signals a child processes

Ak wrapper spúšťa long-running child, signal delivery a cleanup treba navrhnúť. `exec` nahradí shell process childom:

```bash
exec python3 tools/atlasctl.py apply ...
```

To je vhodné, keď shell už nepotrebuje cleanup. Ak cleanup potrebuje, musí child PID sledovať a signals forwardovať.

## Incident: pipeline je zelená napriek zlyhanému validatoru

Skript používa:

```bash
validate-config | tee validation.log
```

Bez `pipefail` vráti pipeline exit status `tee`, ktorý uspel. Apply pokračuje s neplatným configom. Root cause nie je CI runner, ale shell pipeline semantics.

Oprava zapne `pipefail`, pridá explicitný validator result a regression test s failing producerom. Verification kontroluje, že apply sa pri invalid input vôbec nespustil.

## Zhrnutie

Bash je silný orchestration jazyk, keď má úzky dátový model a jasný process contract. Bezpečný skript používa quoted arrays, explicitný parser, command-specific exit semantics, trap cleanup, lock, oddelené streams a plan/apply/verify hranice. Strict mode pomáha, ale nenahrádza mechanistické pochopenie shellu.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Monorepo vs. multirepo](monorepo-vs-multirepo.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: PowerShell fundamentals →](powershell-fundamentals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
