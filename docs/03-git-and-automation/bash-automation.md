# Bash automation

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Git and Automation Basics
- Predpoklady: [Shell, Bash, pipes, redirection a exit codes](../01-linux-and-systems/shell-bash-pipes-redirection-exit-codes.md), [Processes, threads, PID a signals](../01-linux-and-systems/processes-threads-pid-signals.md)
- Súvisiace témy: idempotencia, process orchestration, file locking, CI entrypoints, structured data

## 1. Definícia

Bash je interaktívny shell aj programovací jazyk vhodný najmä na skladanie existujúcich procesov, prácu so súbormi a orchestration systémových nástrojov.

Je silný, keď väčšinu doménovej práce už vykonávajú spoľahlivé CLI programy:

```text
validate input
→ zavolať nástroje
→ prepojiť streams
→ vyhodnotiť exit status
→ vykonať malý počet kontrolovaných mutations
→ overiť výsledok
```

Bash nie je bezpečný automaticky. Interaktívny one-liner sa nestane produkčným skriptom iba uložením do `.sh` súboru. Produkčný skript potrebuje explicitný kontrakt vstupov, výstupov, exit codes, side effects, concurrency, retry, cleanup a observability.

## 2. Kedy je Bash vhodný

Silné prípady:

- bootstrap a provisioning wrappers,
- deployment a CI job entrypoints,
- filesystem a process orchestration,
- diagnostické utility,
- krátke admin workflows,
- spájanie `git`, `curl`, `jq`, `kubectl`, `aws`, `sed`, `awk` a podobných nástrojov,
- malé transformácie s jasne definovaným textovým alebo structured-data vstupom.

Slabé prípady:

- zložitý dátový model,
- rozsiahle JSON/YAML transformácie bez špecializovaného parsera,
- robustný HTTP klient s komplexným retry a auth lifecycle,
- dlhodobá daemon služba,
- veľká paralelná pipeline s komplikovaným schedulingom,
- multiplatformová aplikácia s výrazne rozdielnymi systémami,
- doménová logika vyžadujúca typy, knižnice a unit-test izoláciu.

Praktický signál na prechod k Pythonu alebo inému jazyku:

```text
väčšina riadkov už neriadi procesy,
ale parsuje dáta, simuluje typy a implementuje vlastný framework
```

## 3. Execution model

Shell najprv interpretuje source text a až potom spúšťa výsledný príkaz.

Zjednodušený model:

```text
source text
→ lexical parsing a syntax
→ brace/tilde/parameter/command/arithmetic expansion
→ word splitting
→ pathname expansion (globbing)
→ redirections
→ command lookup
→ process alebo builtin execution
→ exit status
```

Presné poradie má výnimky podľa syntaktického kontextu, ale hlavná diagnostická myšlienka je:

> argument, ktorý program dostane, nemusí byť rovnaký text, ktorý vidíš v skripte.

Príklad:

```bash
target='report *.txt'
printf '%s\n' $target
```

Nequoted expansion môže vytvoriť viac arguments a expandovať glob ešte pred spustením `printf`.

Over skutočné arguments bezpečným debugom:

```bash
printf 'arg=<%q>\n' "$@" >&2
```

`%q` je Bash-specific reprezentácia vhodná na diagnostiku, nie portable serialization formát.

## 4. Shebang a interpreter contract

```bash
#!/usr/bin/env bash
```

`env` vyhľadá `bash` cez aktuálny `PATH`.

Výhoda:

- funguje aj tam, kde Bash nie je v `/bin/bash`.

Riziko:

- interpreter závisí od environmentu a `PATH`,
- privileged alebo vysoko kontrolovaný skript môže spustiť neočakávaný binary.

Alternatíva pre známe prostredie:

```bash
#!/bin/bash
```

Skript spustený takto:

```bash
sh script.sh
```

ignoruje Bash shebang a používa `sh`. Ak používa arrays, `[[ ]]`, process substitution alebo `mapfile`, musí byť spustený Bashom.

Over version:

```bash
if ((BASH_VERSINFO[0] < 5)); then
  printf 'Bash 5 or newer is required\n' >&2
  exit 2
fi
```

Version check je súčasť dependency contractu, nie workaround po incidente.

## 5. Script lifecycle

Produkčný automation flow má byť čitateľný ako fázy:

```text
parse
→ validate
→ observe current state
→ calculate plan
→ optionally display dry-run
→ acquire lock
→ apply bounded mutations
→ verify postconditions
→ release resources
→ return stable exit status
```

Tento model oddeľuje:

- chybný vstup,
- nesplnenú precondition,
- plán bez zmien,
- úspešnú mutation,
- partial failure,
- verify failure,
- interruption.

Skript, ktorý hneď počas parsovania mení systém, sa ťažšie testuje a bezpečne prerušuje.

## 6. Exit-status contract

Unix command vracia integer status. Konvencia:

```text
0       úspech
1       všeobecné zlyhanie alebo false podľa príkazu
2       usage/syntax error v mnohých CLI
126     command existuje, ale nemožno ho vykonať
127     command not found
128+N   často termination signal N
```

Nie každý nenulový status znamená rovnakú kategóriu chyby.

Príklad `grep`:

```text
0 match nájdený
1 match nenájdený
2 runtime alebo input error
```

Správne:

```bash
if grep -Fxq -- "$needle" "$file"; then
  found=true
else
  status=$?
  if ((status == 1)); then
    found=false
  else
    printf 'grep failed with status %d\n' "$status" >&2
    exit "$status"
  fi
fi
```

Automatizácia musí interpretovať exit status podľa contractu konkrétneho nástroja.

## 7. Strict mode a jeho limity

Častý základ:

```bash
set -Eeuo pipefail
```

Význam:

- `-e` — shell sa v mnohých nehandled failure kontextoch ukončí,
- `-E` — `ERR` trap sa dedí do functions, command substitutions a subshells podľa Bash pravidiel,
- `-u` — čítanie nenastavenej premennej je chyba,
- `pipefail` — pipeline status je status pravého najneskoršieho zlyhaného commandu, inak nula.

### `set -e` nie je exception system

Jeho správanie závisí od syntaktického kontextu. Failure nemusí ukončiť shell napríklad v podmienkach `if`, po `!`, v časti `&&`/`||` listu alebo v pipeline podľa konfigurácie.

Nejasné:

```bash
set -e
some_command
```

Lepšie pre očakávanú chybu:

```bash
if ! output=$(some_command); then
  printf 'some_command failed\n' >&2
  exit 1
fi
```

Ale pozor: pri `!` je `$?` po podmienke status negovaného výsledku. Ak potrebuješ pôvodný status:

```bash
set +e
output=$(some_command)
status=$?
set -e

if ((status != 0)); then
  printf 'some_command failed: %d\n' "$status" >&2
  exit "$status"
fi
```

Často je čitateľnejšia explicitná helper function než dynamické prepínanie `-e`.

### `set -u`

Použi default alebo required expansion:

```bash
region=${REGION:-eu-central-1}
: "${TOKEN:?TOKEN must be set}"
```

Rozlišuj:

- unset variable,
- nastavená prázdna hodnota,
- explicitný default.

### `pipefail`

Bez `pipefail`:

```bash
producer | consumer
```

môže vrátiť nulu, ak `consumer` uspel, hoci `producer` zlyhal.

S `pipefail` sa failure zviditeľní, ale stále treba vedieť, ktorý člen zlyhal:

```bash
set +e
producer | transform | consumer
statuses=("${PIPESTATUS[@]}")
set -e
printf 'statuses=%s\n' "${statuses[*]}" >&2
```

`PIPESTATUS` treba zachytiť okamžite; ďalší príkaz ho zmení.

## 8. Quoting ako dátový kontrakt

Bezpečný default:

```bash
printf '%s\n' "$value"
cp -- "$source" "$destination"
rm -- "$target"
```

Double quotes zachovajú jednu expanded hodnotu ako jeden argument, s osobitným správaním pre `"$@"` a arrays.

### Single quotes

```bash
printf '%s\n' '$HOME'
```

Obsah sa neexpanduje.

### Double quotes

```bash
printf '%s\n' "$HOME"
```

Parameter a command substitutions sa expandujú, ale word splitting a pathname expansion sa na výsledok bežne nevykonajú.

### Unquoted expansion

Použi iba vtedy, keď zámerne potrebuješ konkrétne shell splitting/globbing semantics a sú zdokumentované. V produkčnom skripte je to zriedkavé.

## 9. Argument list nie je string

Nesprávne:

```bash
options='--header Authorization: Bearer token'
curl $options "$url"
```

String nemá spoľahlivú hranicu arguments.

Správne:

```bash
options=(
  --fail-with-body
  --header "Authorization: Bearer $token"
  --connect-timeout 5
)

curl "${options[@]}" -- "$url"
```

Array zachová presnú argument boundaries.

## 10. Arrays

Indexed array:

```bash
services=(api worker scheduler)
services+=(notifications)

for service in "${services[@]}"; do
  printf '%s\n' "$service"
done
```

Rozdiel:

```text
"${array[@]}"  každý element je samostatný argument
"${array[*]}"  všetky elementy sa spoja podľa prvého znaku IFS
```

Associative array:

```bash
declare -A ports=(
  [api]=8080
  [metrics]=9090
)

printf '%s\n' "${ports[api]}"
```

Bash arrays neobsahujú NUL byte a nie sú portable do POSIX `sh`.

## 11. Positional arguments a `"$@"`

Forwardovanie všetkých arguments:

```bash
run_tool() {
  tool --fixed-option "$@"
}
```

Použi `"$@"`, nie `$*` ani unquoted `$@`.

Po odobratí argumentu:

```bash
command=$1
shift
run_subcommand "$command" "$@"
```

Pred čítaním `$1` over počet arguments, najmä pri `set -u`.

## 12. Argument parsing

Jednoduchý long-option parser:

```bash
usage() {
  printf 'Usage: %s --environment NAME [--dry-run]\n' "${0##*/}"
}

environment=
dry_run=false

while (($#)); do
  case $1 in
    --environment)
      (($# >= 2)) || {
        printf 'Missing value for --environment\n' >&2
        usage >&2
        exit 2
      }
      environment=$2
      shift 2
      ;;
    --environment=*)
      environment=${1#*=}
      shift
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
    -*)
      printf 'Unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
    *)
      break
      ;;
  esac
done

[[ -n $environment ]] || {
  printf 'Environment is required\n' >&2
  exit 2
}
```

Parser má oddeliť:

- usage errors,
- semantic validation,
- runtime preconditions.

Nikdy nespoliehaj, že prvý ne-option argument nemôže začínať `-`; podporuj `--`.

## 13. Input validation

Validácia má byť allowlist-oriented.

```bash
case $environment in
  dev|stage|prod) ;;
  *)
    printf 'Invalid environment: %s\n' "$environment" >&2
    exit 2
    ;;
esac
```

Path validation musí rozlíšiť:

- existenciu,
- file type,
- ownership,
- permissions,
- symlink policy,
- canonical location,
- race medzi checkom a použitím.

Príklad:

```bash
[[ -f $config ]] || die "Config is not a regular file: $config"
[[ -r $config ]] || die "Config is not readable: $config"
```

Pre security-sensitive path operácie samotné predbežné checks nemusia odstrániť TOCTOU race. Preferuj API alebo file-descriptor model, ktorý vykoná bezpečnú operáciu priamo.

## 14. Functions a scope

```bash
log() {
  local level=$1
  shift
  printf '%s level=%s message=%q\n' \
    "$(date -Is)" "$level" "$*" >&2
}
```

Používaj `local`:

```bash
calculate_plan() {
  local input=$1
  local result
  result=$(tool -- "$input") || return
  printf '%s\n' "$result"
}
```

Function vracia integer status cez `return`, nie ľubovoľnú hodnotu.

Dátový output posielaj na stdout. Logy na stderr. Ak function mieša oboje, command substitution môže zachytiť logy ako dáta.

## 15. Stdout, stderr a structured output

Stabilný CLI contract:

```text
stdout  machine-readable result alebo primárny output
stderr  logs, warnings, diagnostics
status  success/failure category
```

Text pre človeka:

```bash
printf 'Deployment completed\n'
```

JSON pre automation:

```bash
jq -n \
  --arg environment "$environment" \
  --arg status success \
  '{environment: $environment, status: $status}'
```

Nevytváraj JSON ručným string concatenation, ak hodnoty môžu obsahovať quotes, newline alebo backslash.

## 16. Command lookup a dependencies

```bash
require_command() {
  local name=$1
  command -v "$name" >/dev/null 2>&1 || {
    printf 'Missing required command: %s\n' "$name" >&2
    exit 127
  }
}
```

Over aj:

- version,
- required feature flags,
- GNU/BSD/BusyBox variant,
- configuration a plugins,
- authentication context.

Príklad version probe má byť založený na stabilnom machine-readable outpute, nie lokalizovanom human texte, ak nástroj taký output poskytuje.

## 17. Command execution a status capture

Jednoduché:

```bash
if output=$(tool query --json); then
  process "$output"
else
  status=$?
  printf 'Query failed: %d\n' "$status" >&2
  exit "$status"
fi
```

Pozor na assignments:

```bash
local output=$(tool)
```

Status môže byť status `local`, nie spoľahlivo command substitution v zamýšľanom význame.

Bezpečnejšie:

```bash
local output
output=$(tool)
```

## 18. Command substitution

```bash
version=$(tool version)
```

Vlastnosti:

- trailing newline sa odstránia,
- NUL byte nemožno zachovať v Bash variable,
- veľký output sa načíta do memory,
- command substitution beží v subshell environment-e,
- `set -e` inheritance má historické a konfiguračné nuansy.

Nie je vhodná na streaming ani binary payload.

## 19. Čítanie textových riadkov

```bash
while IFS= read -r line || [[ -n $line ]]; do
  printf '%s\n' "$line"
done < "$file"
```

- `IFS=` zachová leading a trailing whitespace,
- `-r` nevykoná backslash escape processing,
- doplnková podmienka spracuje posledný riadok bez newline.

Textový riadok nie je vhodný univerzálny formát pre filenames.

## 20. NUL-delimited paths

Filename môže obsahovať whitespace aj newline, ale nie NUL.

Bezpečný pattern:

```bash
while IFS= read -r -d '' file; do
  printf 'file=<%q>\n' "$file"
done < <(find . -type f -print0)
```

Alebo:

```bash
mapfile -d '' files < <(find . -type f -print0)
for file in "${files[@]}"; do
  process_file "$file"
done
```

Over podporu `mapfile -d` v požadovanej Bash version.

## 21. Pipelines a subshells

Pipeline:

```bash
producer | transform | consumer
```

Jednotlivé commands typicky bežia v samostatných processes/subshell contexts. Assignment v pipeline loop nemusí zostať v parent shelli.

Problematické:

```bash
count=0
printf '%s\n' a b c | while IFS= read -r item; do
  ((count += 1))
done
printf '%s\n' "$count"
```

Bezpečnejší variant:

```bash
count=0
while IFS= read -r item; do
  ((count += 1))
done < <(printf '%s\n' a b c)
printf '%s\n' "$count"
```

Process substitution vytvára vlastný process pre producer, ale loop zostáva v aktuálnom shell kontexte.

## 22. Redirections

```bash
command >output.log 2>error.log
command >>combined.log 2>&1
```

Poradie je významné:

```bash
command >file 2>&1
```

obidva streams smerujú do `file`.

```bash
command 2>&1 >file
```

stderr sa najprv duplikuje na pôvodný stdout a stdout sa potom presmeruje do `file`.

Pre vlastný file descriptor:

```bash
exec 3>audit.log
printf 'event=started\n' >&3
```

File descriptor musí byť uzavretý alebo sa zavrie pri exit-e procesu:

```bash
exec 3>&-
```

## 23. Temporary files

Nikdy nepoužívaj predvídateľné temp meno:

```bash
/tmp/my-script.tmp
```

Použi:

```bash
tmp_dir=$(mktemp -d) || {
  printf 'Unable to create temporary directory\n' >&2
  exit 1
}
```

Cleanup:

```bash
cleanup() {
  local status=$?
  if [[ -n ${tmp_dir:-} && -d $tmp_dir ]]; then
    rm -rf -- "$tmp_dir"
  fi
  return "$status"
}

trap cleanup EXIT
```

Pri privileged skripte over:

- bezpečný parent directory,
- restrictive umask,
- symlink policy,
- ownership.

```bash
umask 077
```

Cleanup nesmie prepisovať pôvodný exit status neúmyselne.

## 24. Traps

Bash trap reaguje na shell events alebo signals.

```bash
on_error() {
  local status=$1
  local line=$2
  local command=$3
  printf 'status=%d line=%d command=%q\n' \
    "$status" "$line" "$command" >&2
}

trap 'status=$?; on_error "$status" "$LINENO" "$BASH_COMMAND"; exit "$status"' ERR
```

Nuansy:

- trap source string sa interpretuje pri triggeri,
- `$?` treba zachytiť pred ďalším command-o-m,
- `ERR` sa nespustí vo všetkých kontextoch, podobne ako `errexit`,
- recursion v error handleri môže zakryť pôvodnú chybu,
- `EXIT` sa spustí pri normálnom aj chybovom ukončení shellu, nie pri `SIGKILL`.

Trap má byť jednoduchý a idempotentný.

## 25. Signal handling a graceful termination

```bash
terminate=false

on_term() {
  terminate=true
}

trap on_term INT TERM
```

Dlhší loop:

```bash
for item in "${items[@]}"; do
  if [[ $terminate == true ]]; then
    printf 'Termination requested; stopping before next item\n' >&2
    exit 143
  fi
  process_item "$item"
done
```

Pri child processoch treba signal forwardovať:

```bash
child_pid=

on_term() {
  if [[ -n ${child_pid:-} ]]; then
    kill -TERM "$child_pid" 2>/dev/null || true
  fi
}

trap on_term INT TERM

long_running_command &
child_pid=$!
wait "$child_pid"
status=$?
child_pid=
exit "$status"
```

Wrapper ako PID 1 v kontajneri má navyše riešiť signal forwarding a zombie reaping; často je vhodný init wrapper alebo `exec`.

## 26. `exec` a process replacement

```bash
exec application --config "$config"
```

`exec` nahradí shell proces cieľovým programom:

- program dostane pôvodné signals priamo,
- shell už nevykoná ďalší cleanup po úspešnom `exec`,
- exit status procesu sa stane statusom wrapperu.

Použitie je vhodné pre container entrypoint po dokončení prípravných krokov.

## 27. Background jobs a `wait`

```bash
run_a &
pid_a=$!
run_b &
pid_b=$!
```

Každý child treba `wait`-núť a vyhodnotiť:

```bash
status=0

if ! wait "$pid_a"; then
  status=1
fi

if ! wait "$pid_b"; then
  status=1
fi

exit "$status"
```

Pri fail-fast parallel execution treba:

- zastaviť ostatných children,
- čakať na ich ukončenie,
- zachovať primárny failure reason,
- cleanupnúť partial outputs.

Bash sám neposkytuje plnohodnotný task scheduler. Pri komplikovanej paralelizácii zváž iný nástroj.

## 28. Idempotencia

Idempotentný skript smeruje current state k desired state.

Slabé:

```bash
printf '%s\n' 'export APP_ENV=prod' >> ~/.profile
```

Každé spustenie pridá ďalší riadok.

Lepšie:

```bash
line='export APP_ENV=prod'
touch ~/.profile
grep -Fxq -- "$line" ~/.profile || printf '%s\n' "$line" >> ~/.profile
```

Ešte lepšie:

- vlastniť celý managed fragment,
- porovnať desired a current content,
- nahradiť ho atomicky,
- overiť parserom alebo aplikáciou.

Idempotencia nie je iba „príkaz nezlyhá druhýkrát“. Výsledný stav musí byť rovnaký a nesmie akumulovať vedľajšie účinky.

## 29. Plan, apply a verify

```bash
current=$(read_current_state)
desired=$(calculate_desired_state)
plan=$(calculate_plan "$current" "$desired")
```

Dry-run:

```bash
if [[ $dry_run == true ]]; then
  print_plan "$plan"
  exit 0
fi
```

Apply:

```bash
apply_plan "$plan"
```

Verify:

```bash
verify_state "$desired"
```

Dry-run musí:

- parsovať a validovať vstupy,
- overiť preconditions,
- vypočítať presný plán,
- nevolať mutation APIs,
- jasne označiť neistoty, ktoré možno zistiť až pri apply.

## 30. Atomic file update

Bezpečný model:

```bash
target=/etc/myapp/config.yaml
target_dir=${target%/*}

tmp=$(mktemp --tmpdir="$target_dir" '.config.yaml.tmp.XXXXXX')
cleanup_file=$tmp

generate_config >"$tmp"
validate_config "$tmp"
chmod 0640 "$tmp"
chown root:myapp "$tmp"
mv -fT -- "$tmp" "$target"
cleanup_file=
```

Dôležité:

- temporary file je na rovnakom filesysteme ako target,
- validácia prebehne pred rename,
- permissions a ownership sú nastavené pred aktiváciou,
- rename je atomický pre observers v rámci podporovaných filesystem semantics,
- directory durability môže pri crash-consistency požiadavkách vyžadovať fsync model mimo jednoduchého Bash skriptu.

`mv` cez filesystems je copy+delete a nie je rovnaká atomic operácia.

## 31. Backup a rollback

Pred mutation definuj recovery:

```bash
backup=$(mktemp --tmpdir="$target_dir" '.config.backup.XXXXXX')
cp --preserve=mode,ownership,timestamps -- "$target" "$backup"
```

Rollback má byť:

- testovateľný,
- idempotentný,
- obmedzený na vlastnené state,
- spustený iba pri jasnej failure kategórii.

Nie každá partial mutation je bezpečne automaticky revertovateľná. Pri databázach, remote APIs alebo externých side effects môže byť vhodnejšia kompenzačná operácia než „undo“.

## 32. Locking a concurrency

Advisory file lock:

```bash
exec 9>/run/lock/my-job.lock
if ! flock -n 9; then
  printf 'Another instance is running\n' >&2
  exit 0
fi
```

Definuj policy:

- wait,
- fail,
- no-op,
- replace stale owner.

Lock file existencia sama nie je spoľahlivý lock. Process môže zomrieť a súbor zostať.

`flock` lock sa viaže na open file description a uvoľní sa pri zatvorení descriptoru/process exit-e.

Limity:

- advisory lock chráni iba cooperating processes,
- network filesystem semantics sa môžu líšiť,
- distributed jobs potrebujú distributed coordination alebo idempotentný conflict model,
- lock granularity ovplyvňuje throughput.

## 33. Retry policy

Retry má byť explicitný a bounded.

```bash
retry() {
  local max_attempts=$1
  local delay=$2
  shift 2

  local attempt status
  for ((attempt = 1; attempt <= max_attempts; attempt++)); do
    if "$@"; then
      return 0
    fi
    status=$?

    if ((attempt == max_attempts)); then
      return "$status"
    fi

    sleep "$delay"
  done
}
```

Produkčný retry má navyše riešiť:

- ktoré statuses sú retryable,
- per-attempt timeout,
- exponential backoff,
- jitter,
- total time budget,
- idempotency mutation,
- server `Retry-After`,
- logging attemptov.

Neopakuj slepo ne-idempotentnú operáciu po timeout-e, ak nevieš, či bola vykonaná.

## 34. Timeouts

Externý command bez timeoutu môže blokovať job donekonečna.

GNU example:

```bash
timeout --signal=TERM --kill-after=5s 30s command args...
```

Portability sa líši. `timeout` nemusí byť dostupný na BSD/macOS bez coreutils.

HTTP nástroju nastav jeho vlastné timeouty:

```bash
curl \
  --connect-timeout 5 \
  --max-time 30 \
  --retry 3 \
  --retry-all-errors \
  --retry-delay 1 \
  --fail-with-body \
  -- "$url"
```

Retry flags musia zodpovedať idempotency a konkrétnej curl version.

## 35. Logging

Log má odpovedať:

- čo skript robil,
- s akým logical operation ID,
- nad akým targetom,
- v ktorej fáze,
- s akým výsledkom a trvaním.

```bash
log() {
  local level=$1
  shift
  printf '%s level=%s script=%s pid=%d message=%q\n' \
    "$(date -Is)" "$level" "${0##*/}" "$$" "$*" >&2
}
```

Nevypisuj:

- tokens,
- passwords,
- celé environmenty,
- private keys,
- sensitive request bodies.

`set -x` môže leaknúť secrets cez expanded commands. V CI ho používaj kontrolovane a dočasne.

## 36. Observability a operation identity

Pre opakovateľný job:

```bash
operation_id=${OPERATION_ID:-"$(date -u +%Y%m%dT%H%M%SZ)-$$"}
```

Loguj phases:

```text
phase=validate
phase=plan
phase=apply
phase=verify
phase=cleanup
```

Metriky alebo summary môžu obsahovať:

- duration,
- changed/no-change,
- attempt count,
- processed item count,
- failure category,
- rollback status.

Skript môže byť malý, ale prevádzkovo stále potrebuje dôkaz úspechu.

## 37. Security: command injection

Nikdy nepoužívaj neoverený vstup cez `eval`:

```bash
eval "$user_input"
```

Ani quoting okolo `eval` neodstráni druhé kolo shell parsing-u.

Bezpečnejšie:

- mapovať povolenú operáciu cez `case`,
- arguments ukladať v array,
- používať parser konkrétneho dátového formátu,
- nikdy nevytvárať shell source z user inputu.

## 38. Option injection

Filename:

```text
--preserve-root
```

môže byť interpretovaný ako option.

Použi:

```bash
rm -- "$file"
cp -- "$source" "$destination"
```

Nie každý command podporuje `--`; over contract konkrétneho nástroja. Alternatívou môže byť absolute alebo `./`-prefixed path.

## 39. PATH hijacking

Privileged skript nemá slepo dôverovať caller `PATH`.

```bash
readonly PATH='/usr/sbin:/usr/bin:/sbin:/bin'
export PATH
```

Ale hard-coded PATH musí zodpovedať platforme.

Ďalšie riziká:

- shell functions alebo aliases pri sourced execution,
- environment variables ovplyvňujúce tools,
- dynamic loader variables,
- writable command directories.

Pre privileged automation preferuj minimálne oprávnenia a spúšťanie konkrétnych operations cez kontrolovaný interface, nie celý shell ako root.

## 40. Secrets

Secret v command argumente môže byť viditeľný cez process listing alebo job metadata.

Preferuj podľa tool supportu:

- stdin,
- protected file descriptor,
- temporary file s `umask 077`,
- environment iba ak threat model a platforma to umožňujú,
- workload identity namiesto dlhodobého static secretu.

Cleanup secret file musí prebehnúť aj pri error-e, ale secure deletion na moderných filesystems a SSD nie je garantovaná jednoduchým overwrite.

## 41. Sourcing verzus execution

Execution:

```bash
./script.sh
```

vytvorí nový process.

Sourcing:

```bash
source script.sh
```

vykoná code v aktuálnom shelli a môže meniť:

- variables,
- functions,
- working directory,
- shell options,
- traps.

Library file má byť navrhnutý na sourcing. Executable script má chrániť entrypoint:

```bash
main() {
  :
}

if [[ ${BASH_SOURCE[0]} == "$0" ]]; then
  main "$@"
fi
```

## 42. Working directory a script location

Cron, CI a systemd môžu spustiť skript z iného directory.

Nejasné:

```bash
cat config/defaults.yaml
```

Script directory:

```bash
script_dir=$(
  cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1
  pwd -P
)
```

Symlink-aware resolution je zložitejšia a musí byť vedomou policy. Niekedy má path zostať relatívna k caller working directory; inokedy k script file.

## 43. Environment contract

Skript má dokumentovať required variables:

```bash
: "${API_URL:?API_URL must be set}"
: "${TOKEN:?TOKEN must be set}"
```

Neloguj celý `env`. Pri diagnostike vypíš iba allowlisted ne-secret hodnoty.

Rozdiely medzi interaktívnym shellom, CI, cron a systemd:

- iný `PATH`,
- iný working directory,
- žiadny TTY,
- minimálny environment,
- iný user/group,
- iný umask,
- iné locale a timezone,
- iný shell.

## 44. Locale, timezone a determinism

Textové nástroje môžu závisieť od locale.

```bash
export LC_ALL=C
```

môže stabilizovať sorting a parsing, ale mení Unicode a human-language semantics. Použi iba tam, kde je byte-oriented contract správny.

Čas:

```bash
date -u +%Y-%m-%dT%H:%M:%SZ
```

Pre timestampy v machine outpute používaj explicitnú timezone.

## 45. Portability

Rozlišuj:

- Bash script,
- POSIX `sh` script,
- GNU userland,
- BSD/macOS userland,
- BusyBox/Alpine.

Príklady rozdielov:

- `sed -i`,
- `date` parsing,
- `readlink -f`,
- `mktemp` syntax,
- `stat` format,
- `xargs` options.

Portable contract má byť testovaný na podporovaných platforms. „Fungovalo na Ubuntu“ nie je portability dôkaz.

## 46. Structured data

JSON:

```bash
value=$(jq -er '.config.value' -- "$file")
```

- `-e` dá meaningful status podľa výsledku,
- `-r` vráti raw string,
- stále treba odlíšiť `null`, missing field a parser error podľa contractu.

YAML parsuj YAML parserom, nie `grep`/`sed`, ak syntax môže obsahovať nested structures, anchors, quoting alebo multiline values.

Tabuľkový human output CLI nie je stabilný parser contract. Preferuj `--json`, `--output json` alebo explicitné fields.

## 47. Dry-run

Dry-run nemá byť:

```bash
if ! $dry_run; then
  final_mutation
fi
```

Musí prejsť rovnakým:

- parsingom,
- validation,
- state observation,
- planningom,
- permission/precondition checks, ak sú read-only.

Output má presne uviesť:

```text
CREATE file X
UPDATE service Y from version A to B
DELETE stale entry Z
NO CHANGE resource Q
```

Ak server rozhoduje dynamicky až pri apply, dry-run musí neistotu priznať.

## 48. Verification

Úspešný command status nie je automaticky úspešný používateľský výsledok.

Po mutation over:

- desired file content,
- parser validity,
- service reload status,
- health endpoint,
- expected resource version,
- neprítomnosť neočakávaného driftu.

Príklad:

```bash
systemctl reload myapp
systemctl is-active --quiet myapp
curl --fail --silent --show-error --max-time 5 \
  http://127.0.0.1:8080/health >/dev/null
```

Health check musí reprezentovať správnu readiness semantics.

## 49. Testing

Testuj minimálne:

- happy path,
- invalid arguments,
- missing dependency,
- empty input,
- paths s spaces, tabs a newline,
- filenames začínajúce `-`,
- repeated run,
- no-change run,
- partial mutation failure,
- verify failure,
- signal interruption,
- concurrent invocation,
- timeout,
- retryable a non-retryable errors,
- cleanup po failure.

Nástroje:

- ShellCheck,
- shfmt,
- Bats,
- containerized integration tests,
- test harness v Pythone alebo inom jazyku.

ShellCheck odhaľuje patterns, nie business correctness.

## 50. Produkčný skeleton

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

readonly SCRIPT_NAME=${0##*/}
readonly PATH='/usr/sbin:/usr/bin:/sbin:/bin'
export PATH

umask 077

dry_run=false
lock_fd=9
tmp_dir=

log() {
  local level=$1
  shift
  printf '%s level=%s script=%s pid=%d message=%q\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "$level" \
    "$SCRIPT_NAME" \
    "$$" \
    "$*" >&2
}

die() {
  local status=$1
  shift
  log error "$*"
  exit "$status"
}

cleanup() {
  local status=$?
  if [[ -n ${tmp_dir:-} && -d $tmp_dir ]]; then
    rm -rf -- "$tmp_dir"
  fi
  return "$status"
}

on_error() {
  local status=$1
  local line=$2
  local command=$3
  log error "status=$status line=$line command=$command"
}

trap cleanup EXIT
trap 'status=$?; on_error "$status" "$LINENO" "$BASH_COMMAND"; exit "$status"' ERR
trap 'log warn "termination requested"; exit 143' TERM
trap 'log warn "interrupted"; exit 130' INT

parse_args() {
  while (($#)); do
    case $1 in
      --dry-run)
        dry_run=true
        shift
        ;;
      -h|--help)
        printf 'Usage: %s [--dry-run]\n' "$SCRIPT_NAME"
        exit 0
        ;;
      *)
        die 2 "unknown argument: $1"
        ;;
    esac
  done
}

validate() {
  command -v flock >/dev/null 2>&1 || die 127 'flock is required'
}

acquire_lock() {
  exec {lock_fd}>/run/lock/my-job.lock
  flock -n "$lock_fd" || die 75 'another instance is running'
}

main() {
  parse_args "$@"
  validate

  tmp_dir=$(mktemp -d) || die 1 'unable to create temporary directory'

  # current=$(observe_state)
  # plan=$(calculate_plan "$current")
  # print_plan "$plan"
  # [[ $dry_run == true ]] && return 0

  acquire_lock

  # apply_plan "$plan"
  # verify_postconditions

  log info 'completed successfully'
}

main "$@"
```

Skeleton je iba štruktúra. Konkrétny skript musí definovať:

- input schema,
- exact exit codes,
- mutation ownership,
- timeout a retry policy,
- lock scope,
- rollback/compensation,
- verification evidence.

## 51. Troubleshooting: funguje interaktívne, nie v CI/cron

Zachyť bezpečný kontext:

```bash
printf 'shell=%s\n' "$BASH_VERSION" >&2
printf 'uid=%s gid=%s\n' "$(id -u)" "$(id -g)" >&2
printf 'pwd=%q\n' "$PWD" >&2
printf 'path=%q\n' "$PATH" >&2
printf 'umask=%s\n' "$(umask)" >&2
```

Kontroluj:

- skutočný interpreter,
- environment allowlist,
- working directory,
- TTY dependency,
- file permissions,
- mounted paths,
- locale/timezone,
- CLI versions,
- authentication context.

## 52. Troubleshooting: pipeline skryla chybu

```bash
set -o pipefail
set +e
producer | transform | consumer
statuses=("${PIPESTATUS[@]}")
set -e
```

Potom identifikuj:

- ktorý process zlyhal,
- či downstream skončil skôr a producer dostal `SIGPIPE`,
- či partial output bol prijatý ako validný,
- či pipeline vytvorila partial mutation.

`SIGPIPE` nemusí znamenať incident, ak consumer zámerne skončil po získaní dostatočných dát. Contract musí byť explicitný.

## 53. Troubleshooting: cleanup zmenil status

Zlý cleanup command môže vrátiť iný status než pôvodné zlyhanie.

Správny pattern:

```bash
cleanup() {
  local status=$?
  rm -rf -- "$tmp_dir" || true
  exit "$status"
}
```

Pri `EXIT` trap-e je často vhodnejšie `return "$status"` alebo explicitný `exit` podľa call contextu; handler musí byť otestovaný, aby nevytvoril recursion.

## 54. Troubleshooting: repeated run poškodzuje state

1. Porovnaj current a desired state pred mutation.
2. Identifikuj append-only alebo create-only príkazy.
3. Over unique identifiers a deduplication.
4. Skontroluj retry po nejasnom timeout-e.
5. Pridaj no-change path.
6. Zaveď atomic replacement alebo compare-and-swap.
7. Testuj druhé a súbežné spustenie.
8. Over konečný state, nie iba exit status.

## 55. Časté omyly

### „`set -e` vyrieši error handling“

Nie. Má kontextové výnimky a nepozná doménový význam statusov.

### „Všetko treba quote-nuť“

Quoting je bezpečný default pre parameter expansion, ale shell syntax má kontexty, kde quotes menia zamýšľané správanie. Dôležité je rozumieť argument boundaries.

### „Textový riadok bezpečne reprezentuje filename“

Filename môže obsahovať newline. Použi NUL-delimited stream.

### „Lock file existencia znamená, že job beží“

Nie. Použi skutočný locking primitive a definovanú stale-owner policy.

### „Dry-run je iba preskočenie mutation“

Musí vypočítať a zobraziť reálny plán po validácii.

### „Command uspel, teda automation uspela“

Treba overiť postcondition a používateľský výsledok.

### „Retry vždy zvyšuje spoľahlivosť“

Môže duplikovať side effect alebo zosilniť overload.

### „Bash je prenosný medzi všetkými Unix systémami“

Bash version aj externé userland nástroje sa líšia.

## 56. Kontrolné otázky

1. Prečo program nemusí dostať rovnaké arguments, aké vizuálne vidíš v skripte?
2. Aký je rozdiel medzi `"${array[@]}"` a stringom obsahujúcim options?
3. Prečo `set -e` nie je exception handling systém?
4. Čo zmení `pipefail` a ako zistíš konkrétny zlyhaný člen pipeline?
5. Ako spracuješ filenames obsahujúce spaces aj newline?
6. Ako trap zachová pôvodný exit status?
7. Kedy má entrypoint použiť `exec`?
8. Ako navrhneš atomic file update a verify fázu?
9. Aké podmienky musí spĺňať bezpečný retry?
10. Ako rozlíšiš stdout data contract, stderr logging a exit-status contract?
11. Prečo `eval` a mutable command string vytvárajú injection riziko?
12. Ktoré signály ukazujú, že automatizácia už patrí do Pythonu alebo špecializovaného nástroja?

## Glossary impact

Relevantné pojmy: shell expansion, word splitting, pathname expansion, quoting, argument vector, exit status, `errexit`, `pipefail`, `PIPESTATUS`, subshell, process substitution, trap, signal forwarding, idempotent script, atomic rename, advisory lock, command injection, option injection, NUL-delimited stream, dry-run a postcondition verification.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Monorepo vs. multirepo](monorepo-vs-multirepo.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: PowerShell fundamentals →](powershell-fundamentals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->