# Shell, Bash, pipes, redirection a exit codes

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Procesy, thready, PID a signals](processes-threads-pid-signals.md), [Filesystem hierarchy, inodes a links](filesystem-hierarchy-inodes-links.md)
- Súvisiace témy: automation, CI/CD, environment variables, file descriptors, process substitution

## 1. Shell je jazykový runtime a process orchestrator

Shell nie je iba miesto, kam sa píšu príkazy. Je to interpreter príkazového jazyka, ktorý parsuje syntax, vykonáva expansions, nastavuje file descriptors, rozhoduje medzi builtin a externým programom, vytvára procesy, čaká na ich výsledok a skladá control flow podľa exit statusov.

```text
text shell programu
→ parsing a syntaktická štruktúra
→ expansions
→ redirections
→ builtin alebo fork/exec
→ waiting a signal handling
→ exit status
→ ďalší control-flow krok
```

Terminal emulator, shell a spustený command sú tri odlišné vrstvy. Terminal poskytuje pseudo-terminal a používateľské I/O, shell interpretuje jazyk a command je builtin, funkcia alebo externý executable.

## 2. Bash, POSIX shell a prenositeľnosť

Bash je konkrétny shell s vlastnými rozšíreniami. Skript s arrays, `[[ ... ]]`, process substitution `<(...)`, here-string `<<<`, `&>` alebo `shopt` nie je automaticky kompatibilný s POSIX `sh`.

Shebang určuje interpreter pri priamom spustení:

```bash
#!/usr/bin/env bash
```

`#!/bin/sh` na rôznych systémoch môže smerovať na `dash`, Bash v POSIX mode alebo iný shell. CI skript preto musí explicitne deklarovať runtime, ktorý jeho syntax vyžaduje. Spustenie `sh script.sh` navyše ignoruje Bash shebang a vynúti `sh` parser.

## 3. Od textu k vykonaniu

Shell najprv vytvorí syntaktickú štruktúru. Operátory ako `|`, `&&`, `||`, `;`, `>`, `(` a `{` majú význam ešte pred expansion premenných.

Zjednodušené poradie:

```text
lexing a parsing
→ brace/tilde/parameter/command/arithmetic expansion
→ word splitting
→ pathname expansion
→ quote removal
→ redirections
→ command lookup a execution
```

Presné poradie sa líši podľa typu slova a shell kontextu, ale dôležitý princíp je stabilný: veľká časť chýb vznikne pred spustením cieľového programu. Program môže dostať iný počet argumentov, iné filenames alebo prázdny vstup, než autor skriptu očakával.

## 4. Slovo, argument a quoting

Shell parser pracuje so slovami. Po expansions sa jedno syntaktické slovo môže zmeniť na nula, jeden alebo viac argumentov.

```bash
value='one two *.log'
printf '<%s>\n' $value
```

Nequoteovaná expansion podlieha word splittingu a pathname expansion. Výsledok môže byť `one`, `two` a zoznam všetkých `.log` súborov v current directory. Toto nie je estetický detail, ale zmena API kontraktu volaného programu.

Dvojité úvodzovky zachovajú výsledok parameter alebo command substitution ako jeden argument:

```bash
printf '<%s>\n' "$value"
```

Jednoduché úvodzovky vypnú expansions úplne:

```bash
printf '%s\n' '$HOME $(hostname) *'
```

Praktický default je quoteovať parameter expansions. Nequoteovaný splitting alebo globbing má byť explicitný a zdokumentovaný zámer.

## 5. Positional parameters, `$@` a arrays

`"$@"` expanduje každý positional parameter ako samostatný argument a zachová prázdne hodnoty aj medzery.

```bash
for arg in "$@"; do
  printf 'argument: <%s>\n' "$arg"
done
```

`$*`, `"$*"` a nequoteované `$@` majú odlišnú semantics. `"$*"` zlepí všetky parameters do jedného argumentu podľa prvého znaku `IFS`; nequoteované formy znovu podliehajú splittingu a globbingu.

Bash arrays sú správny spôsob, ako skladať command a zachovať hranice argumentov:

```bash
cmd=(curl --fail --silent)
cmd+=(--header "Authorization: Bearer $token")
cmd+=("$url")
"${cmd[@]}"
```

String nie je bezpečná náhrada argument vectoru. `cmd="curl --header ..."; $cmd` znovu aktivuje shell parsing a poškodí quoting.

## 6. Parameter expansion a defaulty

Bash podporuje viac foriem práce s unset a prázdnymi hodnotami:

```bash
${var:-default}   # default ak unset alebo empty
${var-default}    # default iba ak unset
${var:?message}   # zlyhá ak unset alebo empty
${var:=default}   # nastaví default
```

Rozdiel medzi unset a empty je dôležitý pri konfigurácii. Prázdny secret, prázdna destination path alebo prázdny environment selector nemusia byť platná hodnota a nemajú automaticky dostať benign default.

```bash
: "${DEPLOY_ENV:?DEPLOY_ENV must be set}"
```

Táto validácia zlyhá skoro, pred vykonaním destructive alebo network operácie.

## 7. Globbing a pathname expansion

Vzory `*`, `?` a `[...]` expanduje shell podľa files v current directory ešte pred `execve()`. Program typicky nedostane znak `*`, ale konkrétny zoznam pathnames.

Ak pattern nič nenájde, Bash ho defaultne ponechá literálny. `nullglob` ho môže odstrániť a `failglob` môže vyvolať chybu:

```bash
shopt -s nullglob
files=(/var/log/app/*.log)
```

Skript musí vedieť, či „žiadny match“ znamená prázdny zoznam, chybu alebo literal pattern. Inak môže napríklad odoslať string `*.log` externému API alebo pracovať s nesprávnym súborom.

## 8. Command lookup

Pri jednoduchom command name Bash typicky kontroluje funkcie, builtins, hash cache a `PATH`. Presné poradie môže ovplyvniť alias alebo reserved word už počas parsing fázy.

```bash
type -a printf
type -a test
command -V grep
hash -t ls
```

`cd` musí byť builtin, pretože child process nemôže zmeniť current working directory parent shellu. `export`, `umask`, `read` a shell option commands rovnako menia stav aktuálneho shellu.

Bezpečný skript nemá predpokladať dôveryhodný `PATH` pri privilegovanom execution. Používa kontrolované environment, absolútne paths tam, kde je to vhodné, a nevkladá writable directories pred system paths.

## 9. File descriptors a štandardné streams

Proces typicky zdedí file descriptors 0, 1 a 2:

- **FD 0 — stdin.** Zdroj vstupu; môže byť terminal, file, pipe, socket alebo `/dev/null`.
- **FD 1 — stdout.** Normálny dátový výstup určený na ďalšie spracovanie alebo zobrazenie.
- **FD 2 — stderr.** Diagnostický kanál, ktorý môže zostať viditeľný aj keď stdout ide do pipeline.

File descriptor je číslo v process descriptor table. Redirection zmení, na aký open file description descriptor ukazuje, ešte pred spustením commandu.

## 10. Redirection ako descriptor operácia

```bash
command >output.txt
command >>output.txt
command 2>error.txt
command </input.txt
```

`>` otvorí alebo vytvorí cieľ s truncate semantics. `>>` otvorí s append semantics. Skutočné permissions, umask, symlink behavior, mount state a errors rieši kernelový `openat()`.

Descriptor duplication je ľavo-pravá sekvencia:

```bash
command >all.txt 2>&1
```

Najprv FD 1 začne ukazovať na `all.txt`. Potom FD 2 dostane kópiu aktuálneho FD 1, takže oba smerujú do súboru.

```bash
command 2>&1 >all.txt
```

FD 2 sa najprv pripojí na pôvodný stdout, napríklad terminal. Až potom sa FD 1 presmeruje do súboru. Stderr preto zostane na terminali.

Bash `&>all.txt` je skratka pre stdout aj stderr, ale nie je POSIX syntax.

## 11. Vlastné file descriptors

Shell môže otvoriť ďalší descriptor a používať ho opakovane:

```bash
exec 3>>audit.log
printf 'start %s\n' "$(date -Is)" >&3
critical_command
printf 'status=%d\n' "$?" >&3
exec 3>&-
```

`exec` bez commandu mení descriptors aktuálneho shellu. To je užitočné, ale globálna redirection môže nečakane ovplyvniť všetky ďalšie commands. Skript má descriptor lifecycle explicitne uzavrieť a zabrániť inheritance do child procesov, ak ho nepotrebujú.

## 12. Pipe je kernelový byte stream

```bash
producer | consumer
```

Shell vytvorí pipe, pripojí write end na stdout producenta a read end na stdin konzumenta. Commands typicky bežia súčasne v samostatných procesoch alebo subshell contexts.

Pipe nemá riadky, JSON objekty ani record schema. Prenáša ordered byte stream. Line buffering, delimitery a parsing sú kontraktom producenta a konzumenta.

Keď sa buffer naplní, write môže blokovať. Tento backpressure spomaľuje producenta podľa kapacity konzumenta. Ak konzument skončí a producent ďalej zapisuje, producent môže dostať `SIGPIPE` alebo `EPIPE`.

## 13. Buffering v pipeline

Program môže meniť buffering podľa toho, či stdout smeruje na terminal alebo pipe. Interaktívne line-buffered správanie sa po pripojení do pipeline môže zmeniť na block buffering, takže output prichádza vo veľkých dávkach.

```text
program → terminal: output po riadkoch
program → pipe: output až po naplnení bufferu
```

Tento jav môže vyzerať ako „pipeline zamrzla“, hoci producent iba neflushuje user-space buffer. Nástroje ako `stdbuf` môžu pri niektorých programoch zmeniť buffering, ale nie sú univerzálnou opravou; aplikácia môže používať vlastný runtime alebo explicitný buffering.

## 14. Pipeline exit status

Bez `pipefail` Bash reportuje status posledného commandu pipeline:

```bash
false | true
echo "$?"   # 0
```

To môže maskovať zlyhanie buildu pred úspešným `tee`:

```bash
build | tee build.log
```

`set -o pipefail` nastaví status pipeline na nenulový status najpravšieho zlyhaného commandu, alebo 0 ak všetky uspeli. Bash array `${PIPESTATUS[@]}` zachytáva statuses jednotlivých členov poslednej foreground pipeline.

```bash
set -o pipefail
build | tee build.log
statuses=("${PIPESTATUS[@]}")
printf 'build=%s tee=%s\n' "${statuses[0]}" "${statuses[1]}"
```

Treba statuses uložiť okamžite. Ďalší command prepíše `$?` aj `PIPESTATUS`.

## 15. Control operators

Shell používa status 0 ako success a nenulový status ako failure alebo iný non-success outcome podľa programu.

```bash
command && next_on_success
command || recovery_on_failure
command1 ; command2
```

- **`&&` — pravá strana sa vykoná iba po statuse 0.** Vhodné pre sekvenciu, kde ďalší krok závisí od úspechu predchádzajúceho.
- **`||` — pravá strana sa vykoná po nenulovom statuse.** Nemá automaticky znamenať „neočakávaná chyba“; napríklad `grep -q` používa status 1 pre „nenašiel match“.
- **`;` — ďalší command sa vykoná bez ohľadu na status.** Predchádzajúca chyba môže byť následne prekrytá statusom ďalšieho úspešného commandu.

`if` testuje command status, nie text `true` alebo `false`:

```bash
if grep -q '^enabled=true$' config; then
  printf 'enabled\n'
else
  printf 'disabled or unreadable\n'
fi
```

Tento príklad stále mieša status 1 „no match“ a status 2 „error“. Robustný skript ich môže rozlíšiť explicitne.

## 16. Exit status kontrakt

Status 0 typicky znamená úspech, ale význam nenulových hodnôt určuje program. `grep` rozlišuje no-match a error, `diff` rozlišuje rozdiel a failure, `test` používa 1 pre false condition.

```bash
grep -q pattern file
status=$?
case $status in
  0) printf 'match\n' ;;
  1) printf 'no match\n' ;;
  *) printf 'grep failed: %d\n' "$status" >&2; exit "$status" ;;
esac
```

Shell často reprezentuje ukončenie signalom ako `128 + signal number`, ale je to shellová konvencia. Pri incident analýze treba overiť signal, core dump a service-manager result, nie iba interpretovať číslo bez kontextu.

## 17. `set -e` a jeho hranice

`set -e` ukončí shell pri niektorých neošetrených failures, ale jeho behavior závisí od syntaktického kontextu. Commands testované v `if`, `while`, `until`, časti `&&/||`, negácii alebo niektorých subshell/function kontextoch môžu byť z errexit pravidla vyňaté.

```bash
set -e
false && echo never
printf 'script continues here\n'
```

`set -e` preto nie je exception system. Nedetekuje logickú chybu, nesprávne prázdny output ani command, ktorý vráti 0 napriek neplatnému business výsledku.

Bezpečnejší model explicitne označí kritické boundaries:

```bash
if ! artifact=$(build_artifact); then
  printf 'build failed\n' >&2
  exit 1
fi

[[ -s $artifact ]] || {
  printf 'artifact missing or empty: %s\n' "$artifact" >&2
  exit 1
}
```

## 18. `set -u`, `pipefail` a `ERR` trap

`set -u` zlyhá pri niektorých references na unset variable. Pomáha odhaliť preklepy, ale skript musí vedome pracovať s voliteľnými premennými cez `${var-}` alebo `${var:-default}`.

`pipefail` zabraňuje maskovaniu skoršieho pipeline failure, ale môže zmeniť behavior pipelines, kde producent zámerne dostane `SIGPIPE`, napríklad `yes | head -n 1`. Každá pipeline má vlastný success contract.

`trap '...' ERR` môže centralizovať diagnostics, ale dedenie do functions, command substitutions a subshells je zložité. `set -E` rozširuje inheritance, no stále nenahrádza explicitný handling.

```bash
set -Eeuo pipefail
trap 'printf "failed at line %d: %s\n" "$LINENO" "$BASH_COMMAND" >&2' ERR
```

Trace alebo trap output môže obsahovať secrets. Produkčný skript musí sanitizovať citlivé values a vedieť, ktoré commands vypnúť z `xtrace`.

## 19. Functions a návratový status

Shell function vracia status posledného vykonaného commandu, pokiaľ nepoužije explicitný `return`.

```bash
check_config() {
  grep -q '^enabled=true$' "$1"
}
```

Pridanie diagnostického `printf` na koniec function môže neúmyselne zmeniť status na 0. Robustná function uloží status a vráti ho vedome.

```bash
check_config() {
  local file=$1
  if grep -q '^enabled=true$' "$file"; then
    return 0
  fi
  local status=$?
  printf 'config check failed for %s: %d\n' "$file" "$status" >&2
  return "$status"
}
```

## 20. Subshell a grouping

Parentheses vytvoria subshell environment:

```bash
( cd /tmp && run_job )
printf 'cwd is still %s\n' "$PWD"
```

Zmeny directory, variables, traps a shell options v subshelli neovplyvnia parent shell. Kernel môže implementovať execution cez fork-like process model alebo optimalizáciu, ale language semantics zostávajú izolované.

Curly braces vykonajú group v aktuálnom shelli:

```bash
{ command1; command2; } >combined.log
```

Zmeny premenných zostanú zachované. Syntax vyžaduje separator pred `}`.

Pipeline members v Bash typicky bežia v subshell contexts. Preto tento pattern často stratí zmenu premennej:

```bash
count=0
printf '%s\n' a b | while read -r _; do
  ((count++))
done
printf '%s\n' "$count"   # často 0
```

Bezpečnejšie je input redirection alebo process substitution:

```bash
count=0
while read -r _; do
  ((count++))
done < <(printf '%s\n' a b)
```

## 21. Command substitution

```bash
value=$(command)
```

Command substitution zachytí stdout a odstráni trailing newline characters. Stderr zostane na pôvodnom FD 2, ak ho skript explicitne nepresmeruje.

Binary data s NUL bytes nemožno bezpečne uložiť do Bash stringu. Veľký output sa materializuje v pamäti shellu a môže byť neefektívny. Pre streams je vhodnejšia pipe, temporary file alebo explicitný descriptor.

Status assignmentu s command substitution môže byť status substitution commandu:

```bash
output=$(critical_command)
status=$?
```

Ak však declaration builtin kombinuje assignment, behavior môže byť prekvapivý. Bezpečný skript oddeľuje `local` declaration od command substitution, aby zachoval status.

## 22. Here-document a here-string

Here-document poskytne multi-line stdin:

```bash
cat <<'EOF'
$HOME zostane literálny
$(hostname) sa nevykoná
EOF
```

Quoteovaný delimiter vypne parameter, command a arithmetic expansions v tele. Nequoteovaný delimiter ich povolí, čo môže byť zámer alebo injection risk.

Here-string je Bash feature:

```bash
read -r line <<<"$value"
```

Pridáva newline a nie je vhodný pre arbitrárne binary data. Pri citlivých secrets treba zvážiť, či sa neobjavia v process memory, debug trace alebo temporary implementation detailoch.

## 23. Process substitution

```bash
diff <(generate_expected) <(generate_actual)
```

Bash poskytne path reprezentujúcu pipe alebo `/dev/fd` endpoint. Je to užitočné pre programy, ktoré očakávajú filenames, ale neznamená seekable regular file. Program vyžadujúci random access alebo opakované otvorenie môže zlyhať.

Process substitution beží asynchrónne a jeho failure sa nemusí automaticky premietnuť do statusu hlavného commandu. Pri kritických workflows treba statuses a outputs validovať explicitne.

## 24. `read`, IFS a bezpečné spracovanie textu

```bash
while IFS= read -r line; do
  printf '%s\n' "$line"
done < input.txt
```

`IFS=` zabráni orezaniu leading/trailing whitespace a `-r` vypne interpretáciu backslash escape. Textový line model stále nedokáže reprezentovať filename s newline bezpečne.

Pre filenames používaj NUL-delimited rozhrania:

```bash
find /data -type f -print0 |
while IFS= read -r -d '' file; do
  process_file "$file"
done
```

Ešte bezpečnejšie je tam, kde je to možné, použiť `find ... -exec ... {} +`, čím sa vyhne manuálnemu parsovaniu textu.

## 25. Command injection

Shell injection vzniká, keď nedôveryhodný vstup dostane možnosť stať sa shell syntaxou namiesto jedného argumentu.

Nebezpečné:

```bash
eval "rm -- $user_input"
sh -c "process $user_input"
```

Útočník môže vložiť separators, substitutions alebo redirections. Quoting po zložení stringu problém spoľahlivo nerieši, pretože shell musí string znovu parse-nuť.

Bezpečnejšie je odovzdať argument vector:

```bash
rm -- "$user_input"
```

Ak je `sh -c` nevyhnutné, nedôveryhodné hodnoty sa majú odovzdať ako positional parameters, nie interpolovať do script stringu.

## 26. Option injection a filenames

Filename začínajúci `-` môže program interpretovať ako option:

```bash
rm -- "$filename"
grep -- "$pattern" "$file"
```

`--` ukončuje options iba v programoch, ktoré túto konvenciu podporujú. Alternatívou pre local filename je prefix `./`.

Quoting chráni hranicu argumentu, ale nezabraňuje option interpretation. `"-rf"` je stále jeden argument `-rf` a program ho môže chápať ako option.

## 27. Temporary files a cleanup

Predvídateľný `/tmp/app.$$` môže byť zneužitý symlink race alebo kolíziou. Použi `mktemp`, nastav restrictive umask a cleanup trap.

```bash
umask 077
tmpdir=$(mktemp -d)
cleanup() {
  rm -rf -- "$tmpdir"
}
trap cleanup EXIT HUP INT TERM
```

Cleanup musí byť idempotentný a bezpečný pri prázdnej alebo neočakávanej variable. Destructive command nikdy nemá pracovať s nevalidovaným empty pathom.

## 28. Signals a traps

`trap` nastaví shell reaction na signals alebo pseudo-events ako `EXIT`, `ERR`, `DEBUG` a `RETURN`.

```bash
terminate=false
trap 'terminate=true' TERM INT

while ! "$terminate"; do
  run_one_iteration
done
```

Signal handler v shelli sa vykonáva medzi commands podľa interpreter semantics, nie ako arbitrary asynchronous C handler v ľubovoľnom instruction pointe. Ak shell čaká na foreground child, timing trapu závisí od signalu a waiting behavior.

Cleanup trap má zachovať pôvodný status:

```bash
cleanup() {
  status=$?
  rm -rf -- "$tmpdir"
  exit "$status"
}
trap cleanup EXIT
```

Inak úspešný cleanup command môže prekryť pôvodné zlyhanie.

## 29. Logging a secrets

`set -x` vypíše expanded commands. V CI môže odhaliť tokeny, passwordy, signed URLs alebo command-line secrets.

```bash
set +x
fetch_secret
set -x
```

Ani dočasné vypnutie xtrace nemusí chrániť secret, ak ho ďalší command vypíše v argumentoch alebo error outpute. Preferuj file descriptor, stdin alebo secret-aware tool integration pred command-line argumentom, ktorý môže byť viditeľný v process listings alebo audite.

## 30. Diagnostika skriptu

```bash
bash -n script.sh
bash -x script.sh
shellcheck script.sh
printf '%q\n' "$value"
type -a command_name
```

- **`bash -n` — syntaktická validácia.** Nevykoná runtime expansions, takže neodhalí unset variable, missing file ani command failure.
- **`bash -x` — execution trace po expansions.** Pomáha vidieť skutočné arguments, ale môže leaknúť secrets.
- **ShellCheck — statická analýza typických shell chýb.** Je to feedback tool, nie formálny dôkaz correctness.
- **`printf %q` — shell-escaped reprezentácia jednej hodnoty.** Pomáha odlíšiť medzery, newlines a prázdne strings pri diagnostike.
- **`PS4` — xtrace prefix.** Môže doplniť source file, line a function, ale nesmie obsahovať citlivé dynamic values.

## 31. End-to-end príklad: build cez `tee`

Pipeline:

```bash
build_project | tee build.log
```

Shell vytvorí pipe, spustí build process a `tee`, prepojí build stdout na pipe write end a `tee` stdin na read end. `tee` zapisuje dáta do file aj svoj stdout. Ak build zlyhá, ale `tee` úspešne dopíše log, bez `pipefail` pipeline vráti 0.

Robustnejší variant:

```bash
set -o pipefail
if ! build_project 2>&1 | tee build.log; then
  statuses=("${PIPESTATUS[@]}")
  printf 'build pipeline failed: %s\n' "${statuses[*]}" >&2
  exit 1
fi

[[ -s build/output.tar ]] || {
  printf 'expected artifact missing\n' >&2
  exit 1
}
```

Samotný exit status stále nemusí dokazovať business úspech. Explicitná validácia artifactu uzatvára output contract.

## 32. Troubleshooting: CI hlási úspech po failure

1. **Identifikuj posledný command jobu.** CI runner často používa status posledného shell commandu; následný `echo` môže prekryť failure.
2. **Over pipeline semantics.** Zapni `pipefail` a okamžite zaznamenaj `PIPESTATUS`.
3. **Over wrapper shell.** Runner môže používať `sh -e`, Bash alebo generovaný script s vlastnými options.
4. **Over function status.** Diagnostický command na konci function môže vrátiť 0 namiesto pôvodného failure.
5. **Over subshell a command substitution.** Failure v background jobe alebo process substitution sa nemusí automaticky propagovať.
6. **Validuj výstup.** Skontroluj artifact, checksum, test report alebo deployment outcome, nie iba exit status wrappera.
7. **Pridaj regression test skriptu.** Spusti ho s failing fake commandmi a over, že job naozaj skončí nenulovo.

## 33. Anti-patterny

### Nequoteované premenné ako default

Menia argument boundaries, aktivujú globbing a robia behavior závislý od current directory. Výnimka musí byť explicitná a testovaná.

### `eval` ako univerzálny parser

Zmení dáta na shell program a otvára injection surface. Arrays, functions a explicitné parsovanie sú bezpečnejšie rozhrania.

### `set -euo pipefail` ako dôkaz robustness

Strict options odhalia časť chýb, ale majú kontextové výnimky a neriešia business invariants. Kritické operations potrebujú explicitný status a output validation.

### Parsovanie `ls`

`ls` output je prezentačný formát a filenames môžu obsahovať whitespace, newlines a escape sequences. Používaj glob arrays, `find -print0` alebo filesystem APIs.

### Secret v command line alebo xtrace

Argument môže byť viditeľný v logs, audit trail alebo process metadata. Secret transport má používať bezpečnejší channel a minimalizovať dobu exposure.

### Cleanup bez zachovania statusu

`trap 'rm ...' EXIT` môže pri zlom návrhu zmeniť výsledok skriptu alebo vykonať destructive command s prázdnou path. Cleanup má validovať state, byť idempotentný a zachovať pôvodný status.

## 34. Kontrolné otázky

1. Ktoré fázy prebehnú medzi textom príkazu a `execve()`?
2. Prečo quoting mení počet argumentov a nie iba vzhľad textu?
3. Aký je rozdiel medzi `"$@"`, `"$*"` a Bash array expansion?
4. Prečo sa `>file 2>&1` správa inak než `2>&1 >file`?
5. Čo presne prenáša pipe a ako vzniká backpressure alebo `SIGPIPE`?
6. Prečo status posledného člena pipeline môže maskovať failure producenta?
7. Aké sú hranice `set -e`, `set -u` a `pipefail`?
8. Prečo variable zmenená vo `while` loope za pipe nemusí zostať v parent shelli?
9. Aký je rozdiel medzi command substitution, process substitution a pipe?
10. Prečo quoting nezabráni option injection?
11. Ako cleanup trap zachová pôvodný exit status?
12. Ako by si otestoval, že CI shell wrapper správne propaguje build failure?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Users, groups, permissions, sudo a PAM](users-groups-permissions-sudo-pam.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Environment variables →](environment-variables.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
