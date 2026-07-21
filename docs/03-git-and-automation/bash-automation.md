# Bash automation

Bash je shell aj programovací jazyk určený najmä na skladanie procesov, prácu so súbormi a orchestration systémových nástrojov. Je silný tam, kde už väčšinu práce vykonávajú existujúce CLI programy. Nie je však bezpečné považovať interaktívny one-liner za produkčný skript bez explicitnej práce s quotingom, exit statusmi, vstupmi a vedľajšími účinkami.

## 1. Kedy je Bash vhodný

Bash je vhodný najmä pre:

- spájanie CLI nástrojov do krátkeho workflow,
- bootstrap a deployment skripty,
- filesystem a process orchestration,
- CI job entrypointy,
- diagnostické a administratívne utility,
- textové transformácie s jasne ohraničeným vstupom.

Bash prestáva byť vhodný, keď skript potrebuje zložitý dátový model, rozsiahle paralelné spracovanie, robustnú HTTP integráciu, komplikované error types alebo dlhodobú maintainability naprieč platformami. Vtedy je často vhodnejší Python alebo špecializovaný nástroj.

## 2. Execution model

Shell najprv vykoná parsing a expansion a až potom spustí príkaz.

Zjednodušený tok:

```text
source text
→ tokenization a parsing
→ parameter/command/arithmetic expansion
→ word splitting
→ pathname expansion
→ redirections
→ command execution
→ exit status
```

Poradie je dôležité. Mnohé chyby nevznikajú v programe, ale ešte pred jeho spustením pri shell expansion.

## 3. Shebang a interpreter

```bash
#!/usr/bin/env bash
```

Shebang určuje interpreter pri priamom spustení súboru. `env` hľadá `bash` cez `PATH`, čo zvyšuje prenositeľnosť, ale zároveň znamená, že výsledok závisí od environmentu.

Pri skriptoch vyžadujúcich konkrétnu verziu treba verziu explicitne overiť:

```bash
if (( BASH_VERSINFO[0] < 5 )); then
  printf 'Bash 5 or newer is required\n' >&2
  exit 2
fi
```

## 4. Strict mode nie je magické riešenie

Často používaný základ:

```bash
set -Eeuo pipefail
```

Význam:

- `-e`: shell sa v mnohých kontextoch ukončí pri nenulovom statuse,
- `-E`: `ERR` trap sa dedí do funkcií a subshell kontextov,
- `-u`: použitie nenastavenej premennej je chyba,
- `pipefail`: pipeline vráti nenulový status, ak zlyhá ktorýkoľvek jej člen.

`set -e` má výnimky a kontextové správanie. Nesmie nahradiť explicitnú kontrolu očakávaných chýb.

```bash
if ! output=$(some_command); then
  printf 'some_command failed\n' >&2
  exit 1
fi
```

## 5. Quoting

Najbezpečnejší default je citovať parameter expansions:

```bash
rm -- "$target"
printf '%s\n' "$value"
cp -- "$source" "$destination"
```

Bez quoting-u:

```bash
for file in $files; do
  ...
done
```

môže shell vykonať word splitting a glob expansion.

Správny model pre kolekciu paths je array:

```bash
files=("report one.txt" "*.log" "--strange-name")
for file in "${files[@]}"; do
  printf '%s\n' "$file"
done
```

## 6. Arrays

Indexed array:

```bash
services=(api worker scheduler)
services+=(notifications)
printf '%s\n' "${services[@]}"
```

Associative array:

```bash
declare -A ports=(
  [api]=8080
  [metrics]=9090
)

printf '%s\n' "${ports[api]}"
```

Arrays sú vhodnejšie než serializovanie zoznamu do space-separated stringu.

## 7. Funkcie a lokálne premenné

```bash
log() {
  local level=$1
  shift
  printf '%s [%s] %s\n' "$(date -Is)" "$level" "$*" >&2
}
```

Používaj `local`, aby funkcia nemenila globálnu premennú neúmyselne.

Funkcia vracia exit status, nie komplexnú hodnotu. Dáta typicky vracia cez stdout alebo nastaví premennú odovzdanú nepriamo, ale stdout kontrakt musí byť čistý.

## 8. Argument parsing

Jednoduchý parser:

```bash
usage() {
  printf 'Usage: %s --environment NAME [--dry-run]\n' "$0"
}

environment=
dry_run=false

while (($#)); do
  case $1 in
    --environment)
      (($# >= 2)) || { usage >&2; exit 2; }
      environment=$2
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
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

[[ -n $environment ]] || { usage >&2; exit 2; }
```

Rozlišuj usage error od runtime failure. Status `2` sa často používa pre chybný vstup.

## 9. Temporary files a cleanup

Nepoužívaj predvídateľné názvy v `/tmp`.

```bash
tmp_dir=$(mktemp -d)
cleanup() {
  rm -rf -- "$tmp_dir"
}
trap cleanup EXIT
```

Pri cleanup-e používaj hodnoty zachytené bezpečne a nevykonávaj `rm -rf` nad neoverenou alebo prázdnou premennou.

## 10. Traps a signal handling

```bash
on_error() {
  local status=$?
  local line=$1
  printf 'Failure at line %s, status %s\n' "$line" "$status" >&2
  exit "$status"
}

trap 'on_error "$LINENO"' ERR
trap 'printf "Interrupted\n" >&2; exit 130' INT TERM
```

Trap nemá robiť zložitú recovery operáciu bez idempotency. Pri `SIGTERM` má skript ideálne zastaviť prijímanie novej práce, ukončiť children a zachovať konzistentný stav.

## 11. Pipelines a subshells

```bash
producer | transform | consumer
```

Časti pipeline často bežia v subshell procesoch. Premenná zmenená v pipeline nemusí byť po pipeline dostupná.

Problematické:

```bash
count=0
printf '%s\n' a b c | while read -r item; do
  ((count++))
done
printf '%s\n' "$count"
```

Bezpečnejší variant s process substitution:

```bash
count=0
while IFS= read -r item; do
  ((count++))
done < <(printf '%s\n' a b c)
```

## 12. Čítanie súborov

```bash
while IFS= read -r line || [[ -n $line ]]; do
  printf '%s\n' "$line"
done < "$file"
```

`IFS=` zachová leading/trailing whitespace a `-r` zabráni interpretácii backslashov. Dodatočná podmienka spracuje posledný riadok bez newline.

Pre paths používaj NUL-delimited streams:

```bash
find . -type f -print0 |
while IFS= read -r -d '' file; do
  printf '%s\n' "$file"
done
```

## 13. Command substitution

```bash
version=$(tool version)
```

Command substitution odstráni trailing newlines. Nie je vhodná na binárne dáta ani na presné zachovanie NUL bytes.

Capture status explicitne:

```bash
if ! result=$(tool query --json); then
  printf 'query failed\n' >&2
  exit 1
fi
```

## 14. Idempotencia

Automatizačný skript má smerovať ku desired state, nie iba slepo opakovať mutations.

Slabé:

```bash
echo 'export APP_ENV=prod' >> ~/.profile
```

Lepšie:

```bash
line='export APP_ENV=prod'
grep -Fxq "$line" ~/.profile || printf '%s\n' "$line" >> ~/.profile
```

Ešte lepšie je spravovať celý deklaratívny fragment alebo použiť nástroj, ktorý vlastní danú konfiguráciu.

## 15. Atomicita a bezpečný zápis

Pri generovaní konfigurácie:

```bash
tmp=$(mktemp "${target}.tmp.XXXXXX")
generate_config > "$tmp"
validate_config "$tmp"
chmod --reference="$target" "$tmp" 2>/dev/null || true
mv -f -- "$tmp" "$target"
```

`mv` v rámci jedného filesystemu je typicky atomický rename. Validácia má prebehnúť pred nahradením aktívneho súboru.

## 16. Concurrency a locking

```bash
exec 9>/run/lock/my-job.lock
if ! flock -n 9; then
  printf 'Another instance is running\n' >&2
  exit 0
fi
```

Lock chráni iba účastníkov používajúcich rovnaký locking protokol. Musí byť definované, či paralelné spustenie čaká, zlyhá alebo sa považuje za no-op.

## 17. Logging

Loguj na stderr, dáta určené na ďalšie spracovanie na stdout.

```bash
log_info() {
  printf '%s level=info message=%q\n' "$(date -Is)" "$*" >&2
}
```

Nevypisuj secrets, tokens alebo celé environmenty. Pri CI používaj maskovanie a minimalizuj debug output.

## 18. External commands a dependencies

```bash
require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    printf 'Missing required command: %s\n' "$1" >&2
    exit 127
  }
}

require_command jq
require_command curl
```

Over aj kompatibilitu verzií a rozdiely GNU/BSD nástrojov. Skript fungujúci na Linuxe nemusí fungovať na macOS alebo BusyBox prostredí.

## 19. ShellCheck a formatovanie

```bash
shellcheck script.sh
shfmt -d script.sh
```

ShellCheck odhaľuje napríklad:

- chýbajúci quoting,
- nebezpečné word splitting,
- nefunkčné assignments v subshelloch,
- nepoužité premenné,
- problematické globy.

Lint nenahrádza runtime testy.

## 20. Testovanie

Pre shell skripty možno použiť Bats alebo test harness v inom jazyku.

Testuj:

- happy path,
- chýbajúce argumenty,
- dependency failure,
- paths s medzerami a newline,
- opakované spustenie,
- interruption,
- partial failure,
- concurrent invocation,
- dry-run režim.

## 21. Bezpečnosť

Nikdy nevyhodnocuj neoverený vstup cez `eval`.

Nebezpečné:

```bash
eval "$user_input"
```

Ďalšie riziká:

- command injection cez nesprávny quoting,
- option injection pri argumente začínajúcom `-`,
- PATH hijacking,
- unsafe temporary files,
- secrets v process arguments alebo logoch,
- wildcard expansion nad útočníkom kontrolovaným adresárom.

Používaj `--` na ukončenie options, absolútne paths v privileged skriptoch a minimálne oprávnenia.

## 22. Produkčný skeleton

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

readonly SCRIPT_NAME=${0##*/}
dry_run=false

log() {
  local level=$1
  shift
  printf '%s level=%s script=%s message=%q\n' \
    "$(date -Is)" "$level" "$SCRIPT_NAME" "$*" >&2
}

die() {
  log error "$*"
  exit 1
}

cleanup() {
  :
}
trap cleanup EXIT
trap 'die "failed at line $LINENO"' ERR

main() {
  # parse arguments
  # validate preconditions
  # calculate desired changes
  # apply atomically
  # verify postconditions
  log info 'completed successfully'
}

main "$@"
```

Skeleton nie je hotová architektúra. Každý skript musí definovať kontrakt vstupov, výstupov, retry, rollback a observability.

## 23. Troubleshooting

### Skript funguje interaktívne, ale nie v CI alebo cron

Kontroluj:

```bash
printf 'PATH=%s\n' "$PATH"
id
pwd
env | sort
```

Typické príčiny:

- iný shell,
- minimálny `PATH`,
- iný working directory,
- chýbajúci TTY,
- iný user alebo permissions,
- nenastavené environment variables,
- rozdielne verzie CLI.

### Pipeline skryla chybu

Zapni `pipefail` a kontroluj `PIPESTATUS`:

```bash
producer | consumer
statuses=("${PIPESTATUS[@]}")
printf '%s\n' "${statuses[*]}"
```

### Argument s medzerou sa rozdelil

Skontroluj quoting a používaj arrays namiesto stringov reprezentujúcich argument list.

## 24. Časté omyly

### „`set -e` vyrieši error handling“

Nevyrieši. Má kontextové výnimky a nevysvetľuje, ktoré chyby sú očakávané.

### „Bash je vhodný na všetku automatizáciu“

Nie. Je optimálny najmä ako glue language nad existujúcimi procesmi.

### „Text je vždy bezpečný dátový formát“

Nie. Paths môžu obsahovať whitespace aj newline a command output môže byť lokalizovaný alebo nestabilný.

### „Dry-run je iba vypnutie posledného príkazu“

Dry-run musí stále validovať vstupy a vypočítať presný plán zmien bez vedľajších účinkov.

## 25. Kontrolné otázky

1. V akom poradí Bash vykonáva expansion a execution?
2. Prečo má byť väčšina parameter expansions v double quotes?
3. Aký je rozdiel medzi stringom a array pri argumentoch?
4. Čo presne mení `pipefail`?
5. Prečo `set -e` nestačí ako error handling stratégia?
6. Ako bezpečne spracuješ filenames s whitespace a newline?
7. Ako zabezpečíš idempotenciu a atomický zápis konfigurácie?
8. Ako rozlíšiš stdout data contract a stderr logging?
9. Prečo je `eval` rizikový?
10. Kedy je vhodnejšie prejsť z Bashu na Python?

## Glossary impact

Relevantné pojmy: shell expansion, word splitting, globbing, exit status, pipeline, `pipefail`, subshell, trap, idempotent script, atomic rename, file lock, command injection, option injection a NUL-delimited stream.
