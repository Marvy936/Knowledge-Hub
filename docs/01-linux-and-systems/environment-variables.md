# Environment variables

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Shell, Bash, pipes, redirection a exit codes](shell-bash-pipes-redirection-exit-codes.md)
- Súvisiace témy: process creation, systemd, containers, CI/CD, secrets

## 1. Čo environment skutočne je

Environment je množina stringových párov `name=value`, ktorú kernel odovzdá novému programu pri `execve()`. Nie je to globálna databáza konfigurácie servera; každý proces má vlastný snapshot environmentu uložený v jeho process context.

Premenná preto existuje iba v konkrétnom procese a v potomkoch, ktorým ju proces explicitne alebo implicitne odovzdá. Dve služby na rovnakom hoste môžu mať rovnaký názov premennej s úplne odlišnou hodnotou bez konfliktu.

```text
source konfigurácie
      ↓
parent process environment
      ↓ fork/spawn + execve
child process environment snapshot
      ↓
aplikácia vytvorí svoju effective configuration
```

## 2. Dedenie je kopírovanie snapshotu

Child proces pri vytvorení typicky dostane kópiu environmentu parent procesu. Po vytvorení sú tieto environmenty nezávislé: neskorší `export` v parent shelli nemení už bežiaci child a child nedokáže bežným spôsobom prepísať environment parent procesu.

To vysvetľuje, prečo skript spustený ako `./setup.sh` nemôže trvalo nastaviť premennú v aktuálnom shelli. Ak má meniť stav aktuálneho shellu, musí sa načítať cez `source` alebo `.`; vtedy sa jeho príkazy vykonajú priamo v existujúcom shell procese namiesto nového child procesu.

```bash
./set-env.sh       # samostatný proces, parent sa nezmení
source set-env.sh  # vykonanie v aktuálnom shelli
```

## 3. Shell variable a exportovaná environment variable

Bash môže držať internú shell variable, ktorá zatiaľ nie je súčasťou environmentu budúcich child procesov. Príkaz `export` označí túto hodnotu na odovzdanie pri ďalšom spustení programu.

```bash
name=local
bash -c 'printf "%s\n" "${name-unset}"'  # unset

export name
bash -c 'printf "%s\n" "$name"'          # local
```

Rozdiel je dôležitý pri debugovaní skriptov a služieb. Hodnota môže byť viditeľná v interaktívnom shelli, ale program ju nedostane, pretože nebola exportovaná alebo ho nespustil očakávaný parent proces.

## 4. Jednorazový environment pre jeden command

Assignment umiestnený pred príkazom vytvorí hodnotu iba pre environment daného commandu. Parent shell si pôvodnú hodnotu ponechá, takže tento model je vhodný na izolované testovanie alebo krátkodobé override bez trvalého zásahu do session.

```bash
LOG_LEVEL=debug APP_PORT=8080 ./app
```

Shell najprv pripraví environment pre command a až potom spustí builtin alebo externý program. Pri shell builtinoch sa presné správanie môže líšiť podľa kontextu, preto sa pri produkčnej automatizácii oplatí používať explicitný subshell alebo `env`.

```bash
env LOG_LEVEL=debug APP_PORT=8080 ./app
```

## 5. Ako environment pozorovať

`env`, `printenv` a `export -p` ukazujú environment alebo exportované shell variables aktuálneho procesu. Pri diagnostike služby je však rozhodujúci environment reálne bežiaceho procesu, nie environment administrátorovho shellu.

```bash
tr '\0' '\n' < /proc/<pid>/environ
```

`/proc/<pid>/environ` používa NUL separators, preto obyčajný `cat` nevytvorí čitateľný výstup. Prístup môže byť obmedzený UID, `hidepid`, ptrace policy alebo inými bezpečnostnými nastaveniami, pretože environment môže obsahovať citlivé údaje.

## 6. Čistý environment ako diagnostický nástroj

`env -i` spustí program bez zdedeného environmentu okrem explicitne zadaných hodnôt. Tým sa dá odhaliť skrytá závislosť na `PATH`, locale, proxy premennej, `HOME` alebo premenných načítaných z interaktívneho profilu.

```bash
env -i PATH=/usr/bin:/bin HOME=/tmp ./app
```

Úplne prázdny environment nemusí byť realistický produkčný stav. Knižnice a programy môžu očakávať základné hodnoty ako `PATH`, `HOME`, `LANG` alebo `TMPDIR`, preto treba testovací environment zostaviť zámerne a dokumentovať, ktoré hodnoty sú kontraktom aplikácie.

## 7. PATH je lookup policy, nie iba textový zoznam

`PATH` je usporiadaný zoznam adresárov oddelených dvojbodkou. Shell pri príkaze bez `/` prehľadáva tieto adresáre zľava doprava a spustí prvý zodpovedajúci executable, ktorý nájde.

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
type -a python
command -v kubectl
```

Poradie preto priamo ovplyvňuje, ktorý program sa vykoná. Zapisovateľný adresár pred systémovými cestami umožňuje command hijacking, prázdna položka môže reprezentovať current working directory a služba pod systemd môže mať iný `PATH` než interaktívny shell.

V kritickej automatizácii je bezpečnejšie definovať minimálny explicitný `PATH` alebo používať absolútne cesty k bezpečnostne citlivým programom. Tým sa lookup stáva súčasťou zdokumentovaného execution contractu namiesto závislosti na neznámom profile používateľa.

## 8. HOME, USER a LOGNAME nie sú autoritatívna identita

Premenné `HOME`, `USER` a `LOGNAME` sú user-space konvencie. Proces ich môže dostať nesprávne, zastarané alebo úmyselne podvrhnuté, preto sa nemajú používať ako jediný vstup bezpečnostného rozhodnutia.

Autoritatívnu process identity poskytujú kernel credentials:

```bash
id
id -u
id -g
getent passwd "$(id -u)"
```

Aplikácia môže používať `HOME` na nájdenie konfiguračného adresára, ale oprávnenie na chránenú operáciu musí posudzovať podľa dôveryhodnej identity a vlastného authorization modelu.

## 9. Locale mení sémantiku textového spracovania

`LANG`, `LC_ALL` a jednotlivé `LC_*` kategórie určujú encoding, collation, klasifikáciu znakov, formát čísiel a dátumov aj jazyk diagnostických správ. Rovnaký príkaz preto môže na dvoch systémoch zoradiť text alebo vytvoriť výstup odlišne.

```bash
LC_ALL=C sort file
LC_ALL=C command
```

Skript, ktorý parsuje lokalizovaný human-readable output, je krehký. Spoľahlivejšie je použiť štruktúrovaný alebo machine-readable formát a locale fixovať iba tam, kde je textový kontrakt nevyhnutný.

## 10. Environment ako runtime configuration interface

Environment je vhodný na menšie scalar hodnoty, ktoré aplikácia načíta pri štarte: názov prostredia, log level, hostname závislosti alebo feature toggle. Výhodou je jednoduché odovzdanie cez process manager, kontajnerový runtime alebo CI systém bez potreby meniť image.

```text
APP_ENV=production
LOG_LEVEL=info
DATABASE_HOST=db.internal
```

Nie je vhodný pre veľké štruktúrované dokumenty, veľmi často meniace sa hodnoty alebo konfiguráciu vyžadujúcu atómový reload. Environment je snapshot pri štarte; ak aplikácia nemá vlastný reload mechanizmus, zmena source hodnoty sa prejaví až po vytvorení nového procesu.

## 11. Precedence musí byť explicitný kontrakt

Aplikácia často skladá konfiguráciu z viacerých zdrojov. Musí preto presne definovať poradie, napríklad:

```text
defaults
  < config file
  < environment
  < command-line flags
```

Bez stabilného precedence modelu nie je možné vysvetliť, prečo výsledná hodnota platí. Dobrá aplikácia vie pri štarte alebo cez diagnostický endpoint ukázať effective configuration a zdroj každej hodnoty, pričom secrets musia zostať redigované.

## 12. Environment file nie je univerzálny formát

Súbor s riadkami `NAME=value` môže vyzerať rovnako v Bash, systemd, Docker Compose, Kubernetes alebo CI systéme, no každý consumer má vlastné pravidlá pre quoting, escaping, comments a expansion. Súbor sa preto musí písať podľa parsera, ktorý ho bude načítavať.

`EnvironmentFile=` v systemd nie je Bash script a nevykoná command substitution. Docker Compose `.env` má inú úlohu než `environment:` vo výslednom kontajneri a Kubernetes `envFrom` pracuje s objektmi ConfigMap alebo Secret, nie so shellovým parserom.

## 13. Environment v systemd

System service nededí bežný interaktívny shell environment používateľa. Jej parentom je service manager, ktorý zostaví environment z unit properties, manager environmentu a explicitných `EnvironmentFile=` zdrojov.

```ini
[Service]
Environment="LOG_LEVEL=info"
EnvironmentFile=-/etc/example/example.env
```

Po zmene unit definície treba načítať nové metadata a vytvoriť nový service proces:

```bash
sudo systemctl daemon-reload
sudo systemctl restart example.service
```

`daemon-reload` iba znovu načíta unit files; nemení environment už bežiaceho procesu. Pri diagnostike treba porovnať `systemctl cat`, `systemctl show`, PID služby a `/proc/<pid>/environ`, pretože definovaný intent a skutočný runtime snapshot nemusia byť totožné.

## 14. Environment v kontajneroch a Kubernetes

Kontajnerový runtime vytvorí environment pre hlavný proces pri štarte kontajnera. Zmena ConfigMap, Secret alebo deployment konfigurácie automaticky neprepíše environment už bežiaceho procesu.

Nová hodnota sa prejaví až po vytvorení nového kontajnera alebo cez samostatný aplikačný reload mechanizmus. Preto rollout stratégie často používajú checksum konfigurácie v Pod template, aby zmena source objektu vyvolala novú ReplicaSet a nové Pody.

Environment zároveň nie je izolovaný secret vault. Hodnoty sa môžu objaviť v deployment metadata, `/proc`, crash dumpoch, debug výstupe alebo CI logoch podľa oprávnení a použitých nástrojov.

## 15. Secrets v environmente

Secret v environment variable sa jednoducho injektuje a aplikácia ho ľahko načíta. Cena za túto jednoduchosť je široké dedenie do child procesov, slabšia rotácia bez reštartu a riziko neúmyselného výpisu pri debugovaní.

Bezpečnejší model môže používať file-mounted secret s úzkymi permissions, workload identity, lokálny agent cez Unix socket alebo dynamické krátko žijúce credentials. Voľba závisí od threat modelu, potreby rotácie a toho, či aplikácia vie credential obnoviť počas behu.

Celý environment sa nemá vypisovať do logu bez allowlistu alebo redakcie. Incident response príkaz `env` môže okamžite zmeniť konfiguračný problém na credential exposure.

## 16. Unset, empty a default value sú rozdielne stavy

Bash rozlišuje premennú, ktorá nie je definovaná, od premennej definovanej ako prázdny string. Aplikácia musí určiť, či empty znamená platnú hodnotu, použitie defaultu alebo chybu konfigurácie.

```bash
printf '%s\n' "${NAME:-default}"  # default pri unset alebo empty
printf '%s\n' "${NAME-default}"   # default iba pri unset
: "${REQUIRED:?REQUIRED must be set and non-empty}"
```

Nejasná interpretácia je častý zdroj rozdielov medzi lokálnym shellom, CI a produkčným runtime. Validácia povinných hodnôt má prebehnúť pri štarte a zlyhať s konkrétnou, bezpečne redigovanou správou.

## 17. Diagnostika rozdielu medzi shellom a službou

Keď aplikácia funguje manuálne, ale zlyhá pod systemd alebo v kontajneri, problém zvyčajne nie je „systemd nepodporuje aplikáciu“. Ide o rozdiel v effective execution context: executable, arguments, UID/GID, working directory, PATH, environment, mounts alebo permissions.

Postup:

1. **Identifikuj reálny proces a executable.** Over PID, `/proc/<pid>/exe`, command line a service unit, aby si nediagnostikoval inú binárku alebo wrapper.
2. **Porovnaj runtime environment.** Získaj relevantné hodnoty z `/proc/<pid>/environ` a porovnaj ich s interaktívnym shellom bez vypisovania secretov.
3. **Over precedence a config sources.** Skontroluj, či aplikácia neprepisuje environment config fileom, command-line flagom alebo interným defaultom.
4. **Reprodukuj minimálny context.** Spusti program cez `env -i` s explicitným `PATH`, `HOME`, locale a povinnými hodnotami.
5. **Nenačítavaj slepo `.bashrc`.** Interaktívny profil obsahuje aliasy, shell-specific syntax a používateľské hodnoty, ktoré zo služby vytvárajú nestabilnú skrytú závislosť.

## 18. Časté omyly

### „Environment variable je globálna pre celý server“

Nie. Každý proces má vlastnú kópiu environmentu a nové hodnoty sa šíria iba do novo vytvorených potomkov. Centrálna konfigurácia môže generovať environment pre viac procesov, ale runtime hodnoty zostávajú process-local.

### „Zmena exportu ovplyvní už bežiacu službu“

Nie. Už bežiaca služba má snapshot z času štartu. Treba ju reloadnúť mechanizmom aplikácie alebo vytvoriť nový proces, pričom samotný `daemon-reload` nestačí.

### „`.env` je univerzálny štandard“

Nie. Rôzni consumermi používajú odlišnú syntax a expansion semantics. Súbor správny pre Bash nemusí byť správny pre systemd ani Docker Compose.

### „Environment je bezpečný pre secret, lebo nie je v súbore“

Nie automaticky. Environment môže byť dostupný cez process metadata, diagnostiku a logy. Bezpečnosť určuje celý exposure a rotation model, nie iba absencia konfiguračného súboru.

## 19. Kontrolné otázky

1. Prečo neskorší `export` v parent shelli nezmení už bežiaci child proces?
2. Aký je rozdiel medzi shell variable, exportovanou variable a one-command assignmentom?
3. Prečo môže systemd service spustiť inú binárku než interaktívny shell pri rovnakom názve commandu?
4. Ako locale mení správanie textovej automatizácie?
5. Prečo zmena Kubernetes ConfigMap nezmení environment existujúceho Podu?
6. Ako by si diagnostikoval, z ktorého source vznikla effective hodnota konfigurácie?
7. Aké trade-offs má uloženie dynamicky rotovaného secretu v environmente?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Shell, Bash, pipes, redirection a exit codes](shell-bash-pipes-redirection-exit-codes.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: systemd, services a daemons →](systemd-services-daemons.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
