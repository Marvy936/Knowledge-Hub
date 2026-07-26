# Bash automation

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Shell, Bash, pipes, redirection a exit codes](../01-linux-and-systems/shell-bash-pipes-redirection-exit-codes.md), [Processes, threads, PID a signals](../01-linux-and-systems/processes-threads-pid-signals.md)
- Súvisiace témy: idempotencia, process orchestration, file locking, CI entrypoints, structured data

## 1. Cieľ kapitoly

Bash je vhodný na automatizáciu vtedy, keď doménovú prácu vykonávajú existujúce programy a shell ich spája do kontrolovaného procesu.

Dobrý Bash skript nie je uložený one-liner. Je to malý orchestration program s explicitným lifecycle-om:

```text
input
→ validation
→ current-state observation
→ plan
→ bounded mutation
→ postcondition verification
→ cleanup a stable exit status
```

Tento model je nosnou témou celej kapitoly. Quoting, arrays, pipelines, traps, locking, retry aj logging sú mechanizmy, ktoré chránia konkrétnu fázu lifecycle-u.

## 2. Nosný scenár: Atlas config deployer

Tím Atlas prevádzkuje službu `orders-api`. Potrebuje CI entrypoint, ktorý:

1. prijme environment a cestu k šablóne,
2. vyrenderuje konfiguráciu,
3. overí syntax,
4. porovná desired content s aktuálnym súborom,
5. pri zmene vykoná atomické nahradenie,
6. reloadne službu,
7. overí readiness endpoint,
8. pri chybe zachová dôkaz a vráti stabilný exit code.

Rozhranie:

```bash
./deploy-config.sh \
  --environment prod \
  --template ./config/orders.conf.tpl \
  --target /etc/atlas/orders.conf \
  --dry-run
```

Skript môže byť spustený:

- lokálne administrátorom,
- v CI,
- cez systemd unit,
- bez TTY,
- s minimálnym environmentom,
- opakovane alebo súbežne.

Preto nemožno spoliehať na interaktívny shell state, aktuálny directory ani manuálnu interpretáciu outputu.

## 3. Kedy Bash použiť a kedy prestať

Bash je silný, keď workflow pozostáva najmä z:

```text
filesystem operations
+ process execution
+ stream composition
+ malý počet state transitions
```

Atlas skript používa `envsubst`, validator, `cmp`, `install`, `systemctl` a `curl`. Shell riadi poradie a interpretuje ich výsledky.

Bash je slabá voľba, keď väčšina programu:

- implementuje komplikovaný dátový model,
- ručne parsuje JSON alebo YAML,
- potrebuje rozsiahle retry a API state machines,
- riadi veľa paralelných závislostí,
- potrebuje typované reusable API a izolované unit tests.

Praktická hranica:

```text
Ak shell prevažne spúšťa programy, Bash je prirodzený.
Ak prevažne simuluje aplikačný runtime, zvoľ Python alebo iný jazyk.
```

## 4. Interpreter je dependency contract

Skript začína explicitným interpreterom:

```bash
#!/usr/bin/env bash
```

`env` nájde `bash` cez `PATH`. To zvyšuje prenosnosť, ale znamená, že interpreter závisí od execution environmentu.

V kontrolovanom image môže byť vhodnejšie:

```bash
#!/bin/bash
```

Spustenie:

```bash
sh deploy-config.sh
```

ignoruje Bash shebang a použije `sh`. Ak skript používa arrays, `[[ ]]`, `mapfile`, process substitution alebo `BASH_SOURCE`, musí byť spustený Bashom.

Version contract:

```bash
if ((BASH_VERSINFO[0] < 5)); then
  printf 'Bash 5 or newer is required\n' >&2
  exit 2
fi
```

## 5. Shell najprv vytvorí argument vector

Pred spustením programu Bash vykoná parsing a expansions:

```text
source text
→ parameter/command/arithmetic expansion
→ word splitting
→ pathname expansion
→ redirections
→ command execution
```

Pre Atlas je zásadné, že program nemusí dostať rovnaký text, aký vizuálne vidíme v skripte.

Nebezpečné:

```bash
target='orders config.conf'
rm $target
```

Nequoted expansion môže vytvoriť viac argumentov a vykonať globbing.

Bezpečný default:

```bash
rm -- "$target"
printf 'target=<%q>\n' "$target" >&2
```

`--` oddeľuje options od positional arguments, ak ho daný program podporuje. Chráni aj path začínajúcu znakom `-`.

## 6. Argument list nie je command string

Zlé skladanie:

```bash
options="--template $template --target $target"
render_tool $options
```

String neuchová spoľahlivé hranice argumentov.

Použi array:

```bash
render_args=(
  --environment "$environment"
  --template "$template"
  --target "$rendered_file"
)

render_tool "${render_args[@]}"
```

Rozdiel:

```text
"${array[@]}"  každý element zostane samostatný argument
"${array[*]}"  elementy sa spoja do jedného stringu
```

Nevytváraj command z nedôveryhodného vstupu cez `eval`. `eval` spustí ďalšie kolo shell parsing-u a vytvorí command-injection boundary.

## 7. Parse a validate pred prvou mutation

Atlas parser rozlišuje usage chybu od runtime failure:

```bash
usage() {
  printf 'Usage: %s --environment NAME --template PATH --target PATH [--dry-run]\n' \
    "${0##*/}"
}

environment=
template=
target=
dry_run=false

while (($#)); do
  case $1 in
    --environment)
      (($# >= 2)) || { usage >&2; exit 2; }
      environment=$2
      shift 2
      ;;
    --template)
      (($# >= 2)) || { usage >&2; exit 2; }
      template=$2
      shift 2
      ;;
    --target)
      (($# >= 2)) || { usage >&2; exit 2; }
      target=$2
      shift 2
      ;;
    --dry-run)
      dry_run=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done
```

Semantic validation:

```bash
case $environment in
  dev|stage|prod) ;;
  *)
    printf 'Invalid environment: %s\n' "$environment" >&2
    exit 2
    ;;
esac

[[ -f $template && -r $template ]] || {
  printf 'Template is not a readable regular file: %s\n' "$template" >&2
  exit 2
}
```

Validation má byť allowlist-oriented. Pri security-sensitive paths samotné `test` checks neodstránia TOCTOU race; treba použiť bezpečný file-descriptor alebo API model.

## 8. Execution environment musí byť explicitný

Skript, ktorý funguje interaktívne, môže zlyhať v CI alebo systemd pre odlišný:

- interpreter,
- `PATH`,
- working directory,
- user a groups,
- umask,
- locale a timezone,
- mounted filesystem,
- credential context.

Atlas deklaruje stabilný `PATH` iba preto, že image má známe umiestnenie nástrojov:

```bash
readonly PATH='/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
umask 077
```

Required variables:

```bash
: "${ATLAS_CONFIG_SOURCE:?ATLAS_CONFIG_SOURCE must be set}"
```

Neloguju sa celé environmenty. Vypisujú sa iba allowlisted ne-secret hodnoty.

Path relatívna k scriptu:

```bash
script_dir=$(
  cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1
  pwd -P
)
```

Toto je vedomé rozhodnutie. Niektoré inputs majú byť relatívne ku caller working directory, iné k umiestneniu scriptu.

## 9. Exit status je typovaný výsledok, nie iba nula alebo chyba

Unix process vracia integer status. Bežný contract:

```text
0    úspech alebo no-change
2    usage/input error
70   interná chyba podľa zvoleného contractu
75   dočasný/concurrency failure podľa zvoleného contractu
126  nemožno vykonať command
127  command not found
```

Konkrétny tool môže mať vlastné semantics. `grep` napríklad používa:

```text
0  match
1  bez matchu
2  runtime chyba
```

Preto sa očakávaný `1` nesmie automaticky interpretovať ako incident:

```bash
if grep -Fxq -- "$desired" "$target"; then
  changed=false
else
  status=$?
  if ((status == 1)); then
    changed=true
  else
    printf 'grep failed: %d\n' "$status" >&2
    exit "$status"
  fi
fi
```

## 10. Strict mode je ochranná sieť, nie exception system

Bežný základ:

```bash
set -Eeuo pipefail
```

- `-e` ukončí shell v mnohých neošetrených failure contexts,
- `-E` rozšíri `ERR` trap do ďalších contexts,
- `-u` odhalí čítanie nenastavenej premennej,
- `pipefail` sprístupní failure v skoršej časti pipeline.

`set -e` má syntaktické výnimky v `if`, `!`, `&&`, `||` a ďalších contexts. Očakávanú chybu spracuj explicitne:

```bash
if output=$(query_tool --json); then
  :
else
  status=$?
  printf 'query failed: %d\n' "$status" >&2
  exit "$status"
fi
```

Pipeline diagnostika:

```bash
set +e
producer | transform | consumer
statuses=("${PIPESTATUS[@]}")
set -e
```

`PIPESTATUS` treba zachytiť okamžite. Ďalší command ho prepíše.

## 11. Streams musia mať stabilný contract

Produkčný CLI má oddeliť:

```text
stdout  primárne dáta alebo machine-readable result
stderr  logs, warnings a diagnostics
status  výsledná failure category
```

Log helper:

```bash
log() {
  local level=$1
  shift
  printf '%s level=%s operation=%s phase=%s message=%q\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "$level" \
    "$operation_id" \
    "$phase" \
    "$*" >&2
}
```

JSON sa neskladá ručne:

```bash
jq -n \
  --arg environment "$environment" \
  --argjson changed "$changed" \
  '{environment: $environment, changed: $changed}'
```

`set -x` môže vypísať expanded secrets. Nie je bezpečný default pre CI logging.

## 12. Observe a plan bez side effects

Atlas najprv vyrenderuje desired file do bezpečného temporary directory:

```bash
tmp_dir=$(mktemp -d) || exit 1
rendered_file=$tmp_dir/orders.conf

ATLAS_ENV=$environment envsubst \
  <"$template" \
  >"$rendered_file"

orders-config-validator -- "$rendered_file"
```

Potom určí plán:

```bash
if [[ -e $target ]] && cmp -s -- "$rendered_file" "$target"; then
  action=NO_CHANGE
else
  action=UPDATE
fi
```

Dry-run prechádza rovnakým parsingom, validation a planningom:

```bash
printf 'action=%s target=%q environment=%q\n' \
  "$action" "$target" "$environment"

if [[ $dry_run == true ]]; then
  exit 0
fi
```

Dry-run, ktorý iba preskočí posledný mutation command, nie je dôveryhodný. Musí vypočítať reálny plán a priznať neistoty dostupné až počas apply.

## 13. Lock chráni mutation boundary

Dve súbežné spustenia môžu obe pozorovať starý stav a následne si prepisovať výsledok.

Advisory lock:

```bash
exec 9>/run/lock/atlas-orders-config.lock
if ! flock -n 9; then
  printf 'Another deployment is running\n' >&2
  exit 75
fi
```

Existencia lock file nie je lock. Súbor môže zostať po páde procesu. `flock` viaže lock na otvorený file description a uvoľní sa po zatvorení descriptoru.

Limity:

- chráni iba cooperating processes,
- network filesystem môže mať odlišné semantics,
- distributed workflow potrebuje distributed coordination alebo idempotent conflict model,
- príliš široký lock znižuje throughput.

## 14. Apply má byť bounded a idempotentný

Ak nie je zmena:

```bash
if [[ $action == NO_CHANGE ]]; then
  changed=false
else
  changed=true
fi
```

Atomické file replacement:

```bash
target_dir=${target%/*}
staged_file=$(mktemp --tmpdir="$target_dir" '.orders.conf.tmp.XXXXXX')

install -m 0640 -o root -g atlas -- "$rendered_file" "$staged_file"
orders-config-validator -- "$staged_file"
mv -fT -- "$staged_file" "$target"
staged_file=
```

Dôležité mechanizmy:

1. temporary file vznikne na rovnakom filesysteme,
2. syntax a permissions sa overia pred aktiváciou,
3. rename sprístupní celý nový file naraz,
4. opakované spustenie s rovnakým desired content skončí ako `NO_CHANGE`.

`mv` medzi filesystems môže byť copy plus delete a neposkytuje rovnakú atomicitu.

Idempotencia neznamená iba „druhý run nezlyhá“. Znamená:

```text
rovnaký desired input
→ rovnaký konečný state
→ bez akumulácie vedľajších účinkov
```

## 15. Verify je samostatná fáza

Úspešný `mv` ani `systemctl reload` ešte nedokazuje používateľský výsledok.

```bash
systemctl reload orders-api
systemctl is-active --quiet orders-api

curl \
  --fail \
  --silent \
  --show-error \
  --connect-timeout 2 \
  --max-time 5 \
  -- http://127.0.0.1:8080/ready \
  >/dev/null
```

Verification má kontrolovať správnu postcondition:

- cieľový content alebo digest,
- parser validity,
- service state,
- readiness semantics,
- očakávanú config generation/version,
- neprítomnosť neočakávaného driftu.

Ak apply uspel a verify zlyhal, ide o partial failure. Skript ho nesmie označiť za úspech iba preto, že mutation command vrátil nulu.

## 16. Cleanup musí zachovať primárny výsledok

```bash
cleanup() {
  local status=$?

  if [[ -n ${staged_file:-} && -e $staged_file ]]; then
    rm -f -- "$staged_file" || true
  fi

  if [[ -n ${tmp_dir:-} && -d $tmp_dir ]]; then
    rm -rf -- "$tmp_dir" || true
  fi

  return "$status"
}

trap cleanup EXIT
```

Cleanup má byť jednoduchý a idempotentný. Nesmie prepísať pôvodný exit status vlastným sekundárnym failure.

`EXIT` trap sa nespustí po `SIGKILL` alebo hard crashi. Temporary-file naming a startup cleanup preto musia zniesť pozostatky starého runu.

## 17. Signals a child process lifecycle

Scheduler alebo container runtime môže poslať `SIGTERM`. Skript má zastaviť začínanie novej práce a forwardovať signal dlhému child procesu.

```bash
child_pid=

on_term() {
  if [[ -n ${child_pid:-} ]]; then
    kill -TERM "$child_pid" 2>/dev/null || true
  fi
}

trap on_term TERM INT

long_running_validator &
child_pid=$!
wait "$child_pid"
status=$?
child_pid=
exit "$status"
```

Pre čistý wrapper entrypoint môže byť správne:

```bash
exec orders-api --config "$target"
```

`exec` nahradí shell proces aplikáciou. Signals a exit status potom prechádzajú priamo, ale shell už po úspešnom `exec` nevykoná ďalší cleanup.

## 18. Retry iba pri známej neistote

Retry potrebuje:

```text
retryable failure class
+ per-attempt timeout
+ bounded attempts
+ backoff a jitter
+ total time budget
+ idempotent operation alebo idempotency key
```

Jednoduchý wrapper:

```bash
retry() {
  local max_attempts=$1
  shift

  local attempt status
  for ((attempt = 1; attempt <= max_attempts; attempt++)); do
    if "$@"; then
      return 0
    fi

    status=$?
    ((attempt == max_attempts)) && return "$status"
    sleep "$attempt"
  done
}
```

Tento wrapper ešte nevie, ktoré statuses sú retryable. Produkčný caller musí klasifikovať failure.

Neopakuj slepo ne-idempotentný `POST` po timeout-e. Server mohol operáciu vykonať, hoci odpoveď neprišla.

## 19. Práca s filenames a structured data

Textový riadok nie je univerzálny filename format. Filename môže obsahovať newline, ale nie NUL.

```bash
while IFS= read -r -d '' file; do
  process_file "$file"
done < <(find . -type f -print0)
```

Pri čítaní bežného textu:

```bash
while IFS= read -r line || [[ -n $line ]]; do
  process_line "$line"
done < "$file"
```

JSON parsuj `jq`, YAML YAML parserom a human-formatted CLI tabuľku nepovažuj za stabilný machine contract.

```bash
version=$(jq -er '.version' -- "$manifest")
```

Treba odlíšiť missing property, `null`, parser error a validnú prázdnu hodnotu podľa konkrétneho schema contractu.

## 20. Worked failure: pipeline je zelená, config sa nenasadil

Pôvodná CI implementácia:

```bash
render_config | tee "$target"
systemctl reload orders-api
```

Incident:

- `render_config` zlyhal po vytvorení partial outputu,
- `tee` úspešne zapísal neúplný file a vrátil `0`,
- pipeline bez `pipefail` bola vyhodnotená ako úspešná,
- reload command sa vykonal,
- služba zostala aktívna so starým in-memory configom,
- CI označilo deployment za green.

Mechanistická diagnostika:

```text
source command failure
→ pipeline status prevzatý z tee
→ partial mutation cieľového file
→ reload bez parser validation
→ chýbajúca readiness/config-version verification
→ false success
```

Náprava:

1. renderovať do temporary file,
2. zachytiť producer status,
3. validovať celý file,
4. porovnať current a desired state,
5. atomicky nahradiť target,
6. reloadnúť,
7. overiť readiness a config generation.

Samotné pridanie `set -o pipefail` by zviditeľnilo failure, ale nevyriešilo partial file mutation. Problém bol v lifecycle dizajne, nie iba v jednej shell option.

## 21. Worked failure: funguje lokálne, nie v CI

Lokálne skript našiel `orders-config-validator`; v CI hlásil `command not found`.

Pozorovania:

```bash
printf 'bash=%q\n' "$BASH_VERSION" >&2
printf 'uid=%s gid=%s\n' "$(id -u)" "$(id -g)" >&2
printf 'pwd=%q\n' "$PWD" >&2
printf 'path=%q\n' "$PATH" >&2
command -V orders-config-validator >&2 || true
```

Príčina:

```text
interaktívny shell startup files
→ lokálne rozšírený PATH
→ validator dostupný

CI non-interactive shell
→ minimálny PATH
→ command resolution failure 127
```

Náprava je deklarovať dependency v image alebo job-e, overiť version a používať kontrolovaný `PATH`. Kopírovanie celého lokálneho environmentu do CI by iba skrylo contract.

## 22. Produkčný skeleton Atlas skriptu

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

readonly SCRIPT_NAME=${0##*/}
readonly PATH='/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
umask 077

operation_id=${OPERATION_ID:-"$(date -u +%Y%m%dT%H%M%SZ)-$$"}
phase=bootstrap
environment=
template=
target=
dry_run=false
tmp_dir=
staged_file=

log() {
  local level=$1
  shift
  printf '%s level=%s operation=%s phase=%s script=%s message=%q\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "$level" "$operation_id" "$phase" "$SCRIPT_NAME" "$*" >&2
}

die() {
  local status=$1
  shift
  log error "$*"
  exit "$status"
}

cleanup() {
  local status=$?
  [[ -z ${staged_file:-} || ! -e $staged_file ]] || rm -f -- "$staged_file" || true
  [[ -z ${tmp_dir:-} || ! -d $tmp_dir ]] || rm -rf -- "$tmp_dir" || true
  return "$status"
}

trap cleanup EXIT
trap 'status=$?; log error "status=$status line=$LINENO command=$BASH_COMMAND"; exit "$status"' ERR

parse_args() {
  while (($#)); do
    case $1 in
      --environment) environment=${2:?}; shift 2 ;;
      --template) template=${2:?}; shift 2 ;;
      --target) target=${2:?}; shift 2 ;;
      --dry-run) dry_run=true; shift ;;
      *) die 2 "unknown argument: $1" ;;
    esac
  done
}

validate_inputs() {
  case $environment in dev|stage|prod) ;; *) die 2 'invalid environment' ;; esac
  [[ -f $template && -r $template ]] || die 2 'template is not readable'
  command -v envsubst >/dev/null || die 127 'envsubst is required'
  command -v orders-config-validator >/dev/null || die 127 'validator is required'
  command -v flock >/dev/null || die 127 'flock is required'
}

main() {
  parse_args "$@"

  phase=validate
  validate_inputs

  phase=observe
  tmp_dir=$(mktemp -d) || die 1 'cannot create temporary directory'
  rendered_file=$tmp_dir/orders.conf
  ATLAS_ENV=$environment envsubst <"$template" >"$rendered_file"
  orders-config-validator -- "$rendered_file"

  if [[ -e $target ]] && cmp -s -- "$rendered_file" "$target"; then
    action=NO_CHANGE
  else
    action=UPDATE
  fi

  phase=plan
  printf 'action=%s target=%q environment=%q\n' "$action" "$target" "$environment"
  [[ $dry_run == false ]] || return 0
  [[ $action == UPDATE ]] || return 0

  phase=lock
  exec 9>/run/lock/atlas-orders-config.lock
  flock -n 9 || die 75 'another deployment is running'

  phase=apply
  target_dir=${target%/*}
  staged_file=$(mktemp --tmpdir="$target_dir" '.orders.conf.tmp.XXXXXX')
  install -m 0640 -o root -g atlas -- "$rendered_file" "$staged_file"
  orders-config-validator -- "$staged_file"
  mv -fT -- "$staged_file" "$target"
  staged_file=
  systemctl reload orders-api

  phase=verify
  systemctl is-active --quiet orders-api
  curl --fail --silent --show-error --connect-timeout 2 --max-time 5 \
    -- http://127.0.0.1:8080/ready >/dev/null

  phase=complete
  log info 'configuration deployed and verified'
}

main "$@"
```

Skeleton ukazuje poradie a boundaries. Reálny skript ešte potrebuje konkrétny rollback alebo compensation model, service-specific readiness a presnú exit-code policy.

## 23. Testing podľa lifecycle-u

Testy nemajú kontrolovať iba happy path syntax.

### Input a argument boundaries

- chýbajúci option value,
- neplatný environment,
- paths so spaces, newline a leading `-`,
- odlišný caller working directory,
- chýbajúci alebo nesprávny interpreter.

### Planning

- target neexistuje,
- content je identický,
- desired content sa líši,
- dry-run nevykoná mutation,
- validator odmietne output pred apply.

### Apply a concurrency

- druhé spustenie je no-op,
- súbežný run rešpektuje lock policy,
- rename a permissions sú správne,
- partial mutation failure zachová evidence.

### Verify a recovery

- reload zlyhá,
- service je active, ale readiness zlyhá,
- cleanup zachová primárny status,
- SIGTERM zastaví child proces,
- retry nezdvojí side effect.

Nástroje môžu zahŕňať ShellCheck, shfmt, Bats a containerized integration tests. ShellCheck odhaľuje patterns, nie business correctness.

## 24. Referenčné pravidlá

- Parameter expansions quote-ni, pokiaľ zámerne nepotrebuješ splitting alebo globbing.
- Command arguments ukladaj do arrays, nie do jedného stringu.
- Používaj `--` alebo inú option-injection ochranu podľa contractu nástroja.
- Dátový output posielaj na stdout, logs na stderr.
- External status interpretuj podľa konkrétneho tool contractu.
- Temporary files vytváraj bezpečne a cleanup rob idempotentne.
- Mutation oddeľ od planningu a verification.
- Retry musí byť bounded a bezpečný voči duplicitnému side effectu.
- Secrets neposielaj do command line, trace outputu ani globálnych logs.
- Pre zložité dátové a concurrency workflows zvoľ silnejší runtime.

## 25. Časté omyly

### „`set -e` vyrieši error handling“

Nevyrieši syntaktické výnimky ani doménový význam exit statuses.

### „Quoting je iba štýl“

Quoting určuje argument boundaries, a teda dáta odovzdané programu.

### „Dry-run znamená preskočiť posledný command“

Dôveryhodný dry-run vykoná validation, observation a planning bez mutations.

### „Command vrátil nulu, automatizácia uspela“

Úspech musí potvrdiť postcondition a používateľský outcome.

### „Lock file znamená, že proces beží“

Existencia súboru nie je synchronization primitive.

### „Retry vždy zvyšuje spoľahlivosť“

Pri nejasnom výsledku môže duplikovať mutation alebo zosilniť overload.

### „Bash je rovnaký na každom Unix systéme“

Líšia sa Bash versions, GNU/BSD/BusyBox tools, filesystems aj process environment.

## 26. Kontrolné otázky

1. Aký lifecycle má produkčný Bash automation skript?
2. Prečo program nemusí dostať rovnaké arguments, aké vidíš v source texte?
3. Prečo sa options ukladajú do array a nie do stringu?
4. Čo `set -e` chráni a kde sú jeho limity?
5. Ako rozlíšiš stdout, stderr a exit-status contract?
6. Prečo musí dry-run vypočítať skutočný plán?
7. Ako atomické file replacement znižuje partial-state window?
8. Čo musí overiť postcondition fáza po úspešnom command-e?
9. Prečo existencia lock file nie je lock?
10. Aké podmienky musí spĺňať bezpečný retry?
11. Ako zachová cleanup pôvodný exit status?
12. Ktoré signály ukazujú, že workflow už nepatrí do Bashu?

## Glossary impact

Relevantné pojmy: shell expansion, word splitting, pathname expansion, quoting, argument vector, strict mode, exit status, pipeline, `PIPESTATUS`, dry-run, current state, desired state, idempotencia, atomic rename, advisory lock, trap, signal forwarding, retry budget, postcondition verification, command injection, option injection.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Monorepo vs. multirepo](monorepo-vs-multirepo.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: PowerShell fundamentals →](powershell-fundamentals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
