# Shell, Bash, pipes, redirection a exit codes

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Procesy, thready, PID a signals](processes-threads-pid-signals.md), [Filesystem hierarchy, inodes a links](filesystem-hierarchy-inodes-links.md)
- Súvisiace témy: automation, CI/CD, environment variables, process substitution

## 1. Shell

Shell je program, ktorý číta príkazový jazyk, vykonáva expansions, nastavuje redirections, vytvára procesy a vyhodnocuje exit statuses. Terminál a shell nie sú to isté:

- terminal emulator poskytuje vstupno-výstupné rozhranie,
- shell interpretuje príkazy,
- command je program alebo shell builtin.

Bash je jeden konkrétny shell. Skript s Bash syntaxou nie je automaticky kompatibilný s POSIX `sh`.

## 2. Ako shell spracuje príkaz

Zjednodušený tok:

```text
text príkazu
  ↓
parsing a quoting
  ↓
parameter/command/arithmetic expansion
  ↓
word splitting a pathname expansion
  ↓
redirections
  ↓
builtin alebo fork + exec
  ↓
exit status
```

Poradie je dôležité. Mnohé chyby nevznikajú v programe, ale ešte pred jeho spustením pri shell expansion.

## 3. Quoting

### Bez úvodzoviek

```bash
printf '%s\n' $value
```

Shell vykoná word splitting a glob expansion. Hodnota s medzerami alebo `*` sa môže zmeniť na viac argumentov.

### Dvojité úvodzovky

```bash
printf '%s\n' "$value"
```

Parameter a command expansion fungujú, ale výsledok sa zachová ako jeden argument.

### Jednoduché úvodzovky

```bash
printf '%s\n' '$HOME'
```

Obsah je literálny; parameter expansion sa nevykoná.

Praktické pravidlo: parameter expansions sa majú štandardne quoteovať, pokiaľ zámerne nepotrebuješ splitting alebo globbing.

## 4. Argumenty a `$@`

```bash
for arg in "$@"; do
  printf 'argument: %s\n' "$arg"
done
```

`"$@"` zachová každý pôvodný positional parameter ako samostatný argument. `$*` a nequoteované `$@` majú iné správanie a často poškodia hranice argumentov.

## 5. Standard streams

Proces typicky začína s tromi file descriptors:

| FD | Názov | Typický smer |
|---|---|---|
| `0` | stdin | vstup |
| `1` | stdout | normálny výstup |
| `2` | stderr | diagnostický výstup |

Program môže otvoriť ďalšie descriptors. Shell redirection mení, na čo descriptor ukazuje ešte pred spustením commandu.

## 6. Redirection

```bash
command >output.txt       # stdout prepíše súbor
command >>output.txt      # stdout pripojí na koniec
command 2>error.txt       # stderr
command >all.txt 2>&1     # stdout a následne stderr na rovnaký cieľ
command </input.txt       # stdin zo súboru
```

Poradie redirections je významové:

```bash
command >all.txt 2>&1
```

najprv presmeruje stdout do súboru a potom stderr na aktuálny stdout.

```bash
command 2>&1 >all.txt
```

najprv presmeruje stderr na pôvodný stdout a až potom stdout do súboru. Výsledok je odlišný.

Bash podporuje skrátenú formu:

```bash
command &>all.txt
```

Táto syntax nie je POSIX `sh`.

## 7. Pipe

```bash
producer | consumer
```

Shell vytvorí kernel pipe, pripojí stdout producenta na write end a stdin konzumenta na read end. Oba procesy môžu bežať súčasne.

Pipe prenáša byte stream, nie riadky ani štruktúrované objekty. To, že nástroje často pracujú po riadkoch, je ich vlastnosť, nie vlastnosť pipe.

Backpressure vznikne, keď pipe buffer zaplní pomalý consumer. Producer potom blokuje pri zápise.

## 8. Exit status pipeline

Bez ďalších nastavení Bash typicky vráti exit status posledného commandu pipeline:

```bash
false | true
echo "$?"   # 0
```

To môže maskovať zlyhanie skoršieho kroku.

```bash
set -o pipefail
false | true
echo "$?"   # nenulový status
```

`pipefail` spôsobí, že pipeline zlyhá, ak zlyhá niektorý jej relevantný command.

Bash array `${PIPESTATUS[@]}` obsahuje statuses jednotlivých členov poslednej foreground pipeline.

## 9. Exit codes a control operators

```bash
command && next_on_success
command || recovery_on_failure
command1 ; command2
```

- `&&` vykoná pravú stranu pri statuse 0,
- `||` pri nenulovom statuse,
- `;` vykoná ďalší command bez ohľadu na status.

`if` testuje exit status commandu:

```bash
if grep -q '^enabled=true$' config; then
  echo enabled
else
  echo disabled
fi
```

Netestuje text `true/false`; testuje status vykonaného commandu.

## 10. `set -euo pipefail`

Často používaný strict mode:

```bash
set -Eeuo pipefail
```

- `-e` — ukončenie pri niektorých neošetrených zlyhaniach,
- `-u` — chyba pri použití unset variable,
- `-o pipefail` — zohľadnenie zlyhania v pipeline,
- `-E` — dedenie `ERR` trapu v ďalších kontextoch.

`set -e` má kontextové výnimky pri `if`, `while`, `&&`, `||`, negácii a ďalších konštrukciách. Nie je náhradou za explicitný error handling a testovanie skriptu.

Bezpečnejší vzor:

```bash
if ! result=$(critical_command); then
  printf 'critical_command failed\n' >&2
  exit 1
fi
```

## 11. Subshell a grouping

```bash
( cd /tmp && command )
```

Zátvorky spustia zoznam v subshell environment. Zmena directory alebo variable neovplyvní parent shell.

```bash
{ command1; command2; }
```

Curly braces vykonajú commands v aktuálnom shelli; syntax vyžaduje oddeľovač pred `}`.

Pipeline members často bežia v subshelloch, preto variable zmenená v `while` loop napojenom cez pipe nemusí zostať zachovaná.

## 12. Command substitution

```bash
value=$(command)
```

Zachytí stdout commandu a odstráni trailing newlines. Stderr zostáva samostatný, pokiaľ ho nepresmeruješ.

Command substitution nie je vhodný na arbitrárne binary data a môže spotrebovať veľa pamäte pri veľkom výstupe.

## 13. Here-document a here-string

```bash
cat <<'EOF'
$HOME zostane literálny
EOF
```

Quoteovaný delimiter vypne expansions v tele.

```bash
read -r line <<<"$value"
```

Here-string je Bash feature a pridáva newline.

## 14. Builtins a external commands

```bash
type cd
type printf
type ls
command -V grep
```

`cd` musí byť builtin, pretože external child process nemôže zmeniť current working directory parent shellu.

Niektoré názvy existujú ako builtin aj external executable. Správanie alebo podporované options sa môžu líšiť.

## 15. Bezpečnosť

### Command injection

Nikdy neskladaj shell command z nedôveryhodného vstupu a nespúšťaj ho cez `eval`.

Chybné:

```bash
eval "rm -- $user_input"
```

Lepšie je používať argument arrays:

```bash
files=("$path1" "$path2")
rm -- "${files[@]}"
```

### Option injection

Filename začínajúci `-` môže byť interpretovaný ako option. Použi `--`:

```bash
rm -- "$filename"
```

### Temporary files

Nepoužívaj predvídateľné mená v `/tmp`. Použi `mktemp` a cleanup trap.

## 16. Diagnostika skriptov

```bash
bash -n script.sh          # syntax check
bash -x script.sh          # execution trace
shellcheck script.sh       # statická analýza
printf '%q\n' "$value"    # shell-escaped reprezentácia
```

Pri trace dávaj pozor na secrets; `set -x` môže zapísať tokeny alebo heslá do logov CI.

## 17. Časté omyly

### „Pipe posiela súbory“

Pipe posiela byte stream medzi file descriptors procesov.

### „`set -e` zachytí každú chybu“

Nie. Správanie závisí od syntaktického kontextu a neošetruje logické chyby ani nečakaný úspech.

### „Nequoteovaná variable je iba estetický problém“

Nie. Mení počet argumentov a môže spustiť glob expansion.

### „stderr je vždy chyba“

Niektoré programy zapisujú progress alebo diagnostiku na stderr aj pri úspechu. Autoritatívny výsledok je definovaný kontraktom programu a exit statusom.

## 18. Troubleshooting scenár

CI job hlási úspech, hoci prvý command pipeline zlyhal:

```bash
build | tee build.log
```

1. Reprodukuj status pipeline.
2. Zapni `set -o pipefail`.
3. Skontroluj `${PIPESTATUS[@]}`.
4. Uisti sa, že wrapper alebo CI runner neprepisuje status ďalším commandom.
5. Pridaj explicitné overenie očakávaného artifactu.

## 19. Kontrolné otázky

1. Aký je rozdiel medzi terminal emulatorom a shellom?
2. Prečo `"$@"` zachová argumenty lepšie než `$*`?
3. Prečo sa líšia `>file 2>&1` a `2>&1 >file`?
4. Čo presne prenáša pipe a ako vzniká backpressure?
5. Prečo `set -euo pipefail` nie je úplný error-handling model?
