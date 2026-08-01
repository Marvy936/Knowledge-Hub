# Bash automation

Bash je shell a programovací jazyk orientovaný na spúšťanie procesov, prepájanie streams a prácu s Unixovým prostredím. Je vhodný pre menšie orchestration tasks, ktoré skladajú existujúce CLI nástroje. Nie je automaticky bezpečný iba preto, že skript má málo riadkov.

Shell vykonáva viac fáz expanzie: parameter expansion, command substitution, word splitting, pathname expansion a redirections. Quoting určuje, ktoré fázy sa aplikujú. Premenná nepredstavuje typed string argument; po nequoted expanzii môže vzniknúť nula, jeden alebo mnoho arguments.

```bash
file='report final.txt'
rm -- "$file"
```

Úvodzovky zachovajú jeden argument. `--` ukončí parsing options a chráni pathname začínajúci pomlčkou.

Exit status je základný control signal. Nula znamená úspech podľa command contractu, nenulová hodnota failure alebo špecifický outcome. `set -e` nie je úplný exception model a má kontextové výnimky. Bezpečný skript explicitne kontroluje kritické commands, pipeline status a native output.

Robustný automation lifecycle:

```text
parse inputs
→ validate
→ observe current state
→ calculate plan
→ acquire lock
→ apply bounded mutation
→ verify effective state
→ cleanup
→ emit stable result
```

Idempotencia znamená, že opakované vykonanie nad už požadovaným stavom nevytvorí ďalšiu zmenu. Nie každý príkaz musí byť sám idempotentný, ale celý workflow musí observe-nuť stav a rozhodnúť, či je mutation potrebná.

Temporary files sa vytvárajú cez bezpečný mechanizmus ako `mktemp`, cleanup sa viaže na `trap` a writes sa podľa potreby dokončujú atomic rename-om. Lock musí mať jasný scope a stale-owner contract. Log nesmie miešať machine-readable stdout s diagnostickým stderr, ak ho používa ďalší program.

Bash je slabší pri komplexnom dátovom modeli, concurrency, HTTP clients a veľkej testovateľnej doménovej logike. Vtedy je vhodnejšie presunúť jadro do Pythonu alebo iného jazyka a shell ponechať ako tenký entrypoint.

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

## Mechanický rozbor kľúčových Bash vzorov

Táto časť rozoberá ukážky tak, ako ich interpretuje shell. Pri Bash bezpečnosti je často dôležitejší presný evaluation order než samotný počet riadkov.

### Čo robí `set -Eeuo pipefail`

```bash
set -Eeuo pipefail
```

- `-e` po vybranom neúspešnom simple command-e ukončí shell. Neplatí rovnako v `if`, `while`, ľavej strane `&&/||`, negácii `!` a rôznych subshell/pipeline kontextoch. Preto nie je exception mechanizmom.
- `-E` dedí `ERR` trap do functions, command substitutions a subshells, kde by sa inak nemusel spustiť. Nemá vplyv na `EXIT` trap.
- `-u` spôsobí chybu pri expanzii unset premennej. Optional hodnotu preto čítaj napríklad `${timeout_seconds:-30}`; `${value-}` a `${value:-}` sa líšia pri empty stringu.
- `pipefail` nastaví status pipeline na pravý najneskorší nenulový status, namiesto statusu posledného commandu. Stále treba vedieť, ktorý command zlyhal; array `${PIPESTATUS[@]}` treba zachytiť okamžite po pipeline.

Explicitný error branch:

```bash
if ! output=$(command-that-may-fail 2>&1); then
  rc=$?
  printf 'command failed rc=%s: %s\n' "$rc" "$output" >&2
  exit 4
fi
```

Tento zápis má jednu pascu: po `!` je `$?` status negovaného compound commandu, teda pri vstupe do branchu môže byť 0. Ak potrebuješ pôvodný status, nepouži `!` takto:

```bash
set +e
output=$(command-that-may-fail 2>&1)
rc=$?
set -e
if ((rc != 0)); then
  printf 'command failed rc=%s: %s\n' "$rc" "$output" >&2
  exit 4
fi
```

Ešte čitateľnejšie je dať command do `if`, keď stačí success/failure a nepotrebuješ pôvodný rc. Command-specific statusy ako grep 1 alebo git diff 1 však vyžadujú explicitnú klasifikáciu.

### Arrays zachovávajú argument boundaries

```bash
args=(plan --config "$config_path" --state "$state_path")
((dry_run)) && args+=(--dry-run)
python3 "$tool" "${args[@]}"
```

Pri assignment-e array elementy vzniknú už po quoting pravidlách. `"${args[@]}"` expanduje každý element ako jeden samostatný argument. Naproti tomu `${args[*]}` v quotes vytvorí jeden string spojený prvým znakom `IFS`; bez quotes znovu zapne word splitting a globbing.

Over si argumenty bez ich vykonania:

```bash
printf 'arg=<%q>\n' python3 "$tool" "${args[@]}"
```

`%q` vytvorí shell-escaped diagnostický zápis. Nie je to command na následné `eval`; slúži na audit boundaries.

### Argument parser krok po kroku

```bash
while (($#)); do
  case $1 in
    --config)
      (($# >= 2)) || { printf 'missing value for --config\n' >&2; exit 2; }
      config_path=$2
      shift 2
      ;;
```

`$#` je počet zostávajúcich positional parameters. `case $1` je bezpečný bez quotes v tejto syntaktickej pozícii, pretože `case` nevykonáva word splitting ako obyčajný command argument. Po kontrole minimálne dvoch arguments sa `$2` uloží a `shift 2` odstráni option aj value. Ak user zadá `--config --dry-run`, jednoduchý parser prijme `--dry-run` ako value; robustnejší contract môže odmietnuť value začínajúcu `-` alebo podporovať `--config=PATH`.

`--` ukončuje option parsing. Zostávajúce values možno interpretovať ako positional arguments. Ak ich script nepodporuje, po loop-e skontroluj `(($# == 0))`.

### Temporary directory a trap — pôvodná ukážka

```bash
tmp_dir=$(mktemp -d)
cleanup() {
  rc=$?
  rm -rf -- "$tmp_dir"
  exit "$rc"
}
trap cleanup EXIT INT TERM
```

Riadok `tmp_dir=$(mktemp -d)` spustí external command a zachytí jeho stdout bez trailing newlines. `mktemp -d` atomicky vytvorí unikátny directory podľa platformovej šablóny; je bezpečnejší než zostavenie `/tmp/my-script-$$`, ktoré môže byť predvídateľné alebo preexistovať. Pri `set -e` failure command substitution typicky ukončí assignment command, ale explicitný check je čitateľnejší.

V `cleanup` sa `rc=$?` musí vykonať ako prvý command. `$?` obsahuje status commandu alebo signalu, ktorý aktivoval trap. Keby najprv prebehol `printf` alebo `rm`, pôvodný status by sa prepísal.

`rm -rf -- "$tmp_dir"` používa quotes, aby path ostal jeden argument, a `--`, aby path začínajúci `-` nebol option. Samotné `-rf` je stále nebezpečné, ak `tmp_dir` môže byť empty, `/` alebo user-controlled shared path. V ukážke je hodnota vytvorená skriptom a nemení sa.

`trap cleanup EXIT INT TERM` registruje rovnakú function pre normal exit aj signals. Tu vzniká subtlety: handler pre `INT` alebo `TERM` zavolá `exit`, čo následne aktivuje aj `EXIT` trap. Cleanup preto môže prebehnúť dvakrát. `rm -rf` je v tomto prípade idempotentný, ale iný cleanup, napríklad revoke lease alebo upload evidence, nemusí byť.

Robustnejší vzor:

```bash
umask 077
tmp_dir=''
cleanup_running=0

cleanup() {
  rc=$?
  ((cleanup_running == 0)) || return "$rc"
  cleanup_running=1
  trap - EXIT INT TERM

  if [[ -n $tmp_dir && -d $tmp_dir && $tmp_dir == "${TMPDIR:-/tmp}"/* ]]; then
    rm -rf -- "$tmp_dir"
  fi
  exit "$rc"
}

trap cleanup EXIT INT TERM

tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/atlas-release.XXXXXXXX") || {
  printf 'unable to create temporary directory\n' >&2
  exit 4
}
```

`umask 077` spôsobí, že novo vytvorené files/directories budú defaultne dostupné iba ownerovi, pokiaľ command explicitne nenastaví širší mode. Prázdna initial value umožní bezpečný cleanup aj vtedy, keď failure nastane pred `mktemp`. Guard zabráni reentrancy a `trap -` odstráni handlers pred `exit`. Prefix check je defense-in-depth; ešte silnejšie je neumožniť žiadnu mutation premennej po create.

Signal-specific exit code možno zachovať samostatnými handlers, napríklad 130 pre INT a 143 pre TERM. `$?` v signal trap-e nemusí vždy reprezentovať shell convention, ktorú chce CLI publikovať.

Pri secrets:

```bash
set +x
secret_file="$tmp_dir/credential"
install -m 600 /dev/null "$secret_file"
# write secret without echoing it
```

`set +x` vypne xtrace pred secret-bearing commands. Treba ho vypnúť skôr, než sa secret objaví v expanded argumente. Temporary cleanup neodstraňuje secret, ktorý už unikol do process listu, CI trace alebo child environmentu.

### File lock a descriptor 9

```bash
exec 9>"$state_path.lock"
if ! flock -n 9; then
  printf 'another apply is running\n' >&2
  exit 3
fi
```

`exec` bez commandu aplikuje redirection na current shell. Shell otvorí lock file na write a priradí ho file descriptoru 9. Descriptor zostane otvorený do close alebo process exit-u. `flock -n 9` skúsi non-blocking exclusive lock viazaný na open file description.

Path file-u nie je samotný lock. Ochranu drží kernel lock na otvorenom descriptore. Zmazanie lock file-u iným processom môže vytvoriť nový inode a druhý nezávislý lock, preto cleanup nemá lock pathname mazať počas aktívnych writerov.

Explicitné close:

```bash
flock -u 9
exec 9>&-
```

Väčšinou sa lock drží cez observe recheck, mutation a verify a uvoľní sa pri exit-e. `flock` semantics na NFS alebo non-Linux platforme sa môžu líšiť; distribuovaný state potrebuje backend-native coordination.

### Plan, apply a verify a exit propagation

```bash
plan_file="$tmp_dir/plan.json"
python3 tools/atlasctl.py plan ... >"$plan_file"
```

Redirection file otvorí ešte pred spustením Pythonu. Ak command zlyhá, môže zostať prázdny alebo partial file. Apply ho preto nesmie používať iba preto, že path existuje. Python plan command musí zapisovať validný complete JSON a exit status 0 až po úspechu; wrapper môže navyše validovať `jq -e`.

```bash
if ! jq -e '.schemaVersion == 1 and .desiredFingerprint' "$plan_file" >/dev/null; then
  printf 'plan output is incomplete\n' >&2
  exit 3
fi
```

Pri dry-run `cat "$plan_file"` publikuje plán na stdout. Progress predtým musí ísť na stderr, inak stdout prestane byť jeden JSON document.

Apply success nepreukazuje verify. Wrapper musí zachytiť native exit code a verify spustiť samostatne. Ak apply vráti 3 pre stale plan, wrapper ho nemá premapovať na generic 4 bez zachovania classu.

### Pipeline status a `PIPESTATUS`

```bash
validate-config | tee validation.log
status=("${PIPESTATUS[@]}")
```

`PIPESTATUS` je array statusov poslednej foreground pipeline. Musí sa skopírovať okamžite; aj `printf` ho prepíše. S dvoma commands je `status[0]` validator a `status[1]` tee. `pipefail` nastaví `$?`, ale array ukáže presného vinníka.

```bash
if ((status[0] != 0)); then
  printf 'validator failed rc=%s\n' "${status[0]}" >&2
  exit 2
fi
if ((status[1] != 0)); then
  printf 'unable to persist validation log rc=%s\n' "${status[1]}" >&2
  exit 4
fi
```

Tieto failures majú odlišný význam: invalid config verzus evidence-storage failure.

### Signals a child process

Ak shell už nepotrebuje cleanup, `exec child ...` nahradí shell rovnakým PID a orchestrator signal ide priamo childovi. Ak cleanup potrebuje, spusti child na pozadí, ulož PID, forwarduj signals a `wait`-ni:

```bash
child_pid=''
forward_term() {
  [[ -n $child_pid ]] && kill -TERM "$child_pid" 2>/dev/null || true
}
trap forward_term TERM INT

python3 tools/atlasctl.py apply ... &
child_pid=$!
set +e
wait "$child_pid"
rc=$?
set -e
child_pid=''
exit "$rc"
```

Tento zjednodušený vzor stále nerieši process group a grandchildren. Pre komplexné supervision je vhodný runtime alebo programovací jazyk s explicitným subprocess modelom.

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
