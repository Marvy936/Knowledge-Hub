# Environment variables

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Shell, Bash, pipes, redirection a exit codes](shell-bash-pipes-redirection-exit-codes.md)
- Súvisiace témy: process creation, systemd, containers, CI/CD, secrets

## 1. Definícia

Environment je množina stringových `name=value` párov pripojená k procesu. Pri vytvorení child procesu sa environment typicky skopíruje z parent procesu a pri `execve()` sa odovzdá novému programu.

Environment variable nie je globálna systémová premenná. Je súčasťou process contextu.

## 2. Dedenie

```text
login manager alebo service manager
        │
        ▼
parent process environment
        │ fork/exec alebo spawn
        ▼
child process environment
```

Child zdedí snapshot environmentu v okamihu vytvorenia. Neskoršia zmena v parent procese už existujúci child automaticky nezmení.

Child proces tiež nemôže bežným spôsobom zmeniť environment parent procesu. Preto skript spustený ako samostatný proces nemôže nastaviť variable v shelli, ktorý ho spustil.

## 3. Shell variable vs. environment variable

Bash môže mať shell variable, ktorá ešte nie je exportovaná:

```bash
name=example
```

Je dostupná v aktuálnom shelli, ale child ju nemusí zdediť.

```bash
export name
# alebo
export name=example
```

`export` označí variable na zahrnutie do environmentu child procesov.

Overenie:

```bash
name=local
bash -c 'printf "%s\n" "${name-unset}"'

export name
bash -c 'printf "%s\n" "$name"'
```

## 4. Jednorazové nastavenie pre command

```bash
LOG_LEVEL=debug APP_PORT=8080 ./app
```

Tieto assignments sa aplikujú na environment konkrétneho commandu bez trvalej zmeny parent shell environmentu.

To je vhodné na izolované testovanie alebo spustenie procesu s konkrétnou konfiguráciou.

## 5. Zobrazenie environmentu

```bash
env
printenv
printenv PATH
export -p
```

Pre konkrétny proces:

```bash
tr '\0' '\n' < /proc/<pid>/environ
```

Environment v `/proc` je NUL-separated. Čítanie môže byť obmedzené permissions a bezpečnostnými nastaveniami.

## 6. Odstránenie a čistý environment

```bash
unset VARIABLE
env -u VARIABLE command
env -i PATH=/usr/bin:/bin command
```

`env -i` spustí command s prázdnym environmentom okrem explicitne zadaných hodnôt. Je užitočný pri diagnostike závislosti na skrytej konfigurácii.

Pozor: úplne prázdny environment môže zmeniť locale, PATH, home directory lookup alebo správanie knižníc.

## 7. PATH

`PATH` je colon-separated zoznam adresárov, v ktorých shell a niektoré programy hľadajú executable.

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
type -a python
command -v kubectl
```

Riziká:

- relatívna alebo prázdna PATH položka môže znamenať current directory,
- zapisovateľný adresár pred systémovými cestami umožňuje command hijacking,
- service manager môže mať odlišný PATH než interaktívny shell,
- `sudo` môže používať `secure_path`.

V automatizácii je často lepšie používať explicitný PATH alebo absolútne cesty ku kritickým programom.

## 8. HOME, USER a current identity

Environment variables ako `HOME`, `USER` alebo `LOGNAME` sú konvencie a user-space dáta. Nemusia autoritatívne zodpovedať effective UID procesu.

Autoritatívnejšie overenie identity:

```bash
id
id -u
getent passwd "$(id -u)"
```

Bezpečnostné rozhodnutie sa nemá robiť iba podľa hodnoty `$USER`.

## 9. Locale

Premenné `LANG`, `LC_ALL` a `LC_*` ovplyvňujú:

- encoding,
- collation a sort order,
- formát dátumu a čísiel,
- klasifikáciu znakov,
- text chybových hlásení.

To môže poškodiť skripty, ktoré parsujú ľudský výstup.

```bash
LC_ALL=C sort file
LC_ALL=C command
```

Pre strojové spracovanie je lepšie používať štruktúrovaný output alebo stabilné locale, nie parsovať lokalizovaný text.

## 10. Konfigurácia cez environment

Environment je vhodný pre malé runtime values:

```bash
APP_ENV=production
LOG_LEVEL=info
DATABASE_HOST=db.internal
```

Nie je ideálny pre:

- veľké štruktúrované konfigurácie,
- často meniace sa hodnoty,
- dáta vyžadujúce atomické reloadovanie,
- secrets s prísnym exposure modelom.

Aplikácia musí mať definovaný precedence model, napríklad:

```text
defaults < config file < environment < command-line flags
```

Bez tohto kontraktu sa ťažko určuje, odkiaľ výsledná hodnota pochádza.

## 11. Environment files

Shell file a environment file nie sú automaticky rovnaký formát.

Shell môže podporovať expansions a command substitutions:

```bash
VALUE="$(command)"
```

`EnvironmentFile=` v systemd má vlastnú syntax a nemá sa automaticky interpretovať ako Bash script.

Rovnako Docker Compose `.env`, Kubernetes EnvFrom a CI variable stores používajú odlišné parsing a escaping pravidlá. Formát treba čítať podľa konkrétneho consumeru.

## 12. Environment v systemd

Služba nededí bežný interaktívny shell environment používateľa.

Unit môže používať:

```ini
[Service]
Environment="LOG_LEVEL=info"
EnvironmentFile=-/etc/example/example.env
```

Po zmene unit konfigurácie:

```bash
sudo systemctl daemon-reload
sudo systemctl restart example.service
```

Runtime environment procesu:

```bash
systemctl show example.service -p Environment
systemctl show example.service -p EnvironmentFiles
```

Zobrazenie metadata nemusí ukázať hodnoty načítané a transformované samotnou aplikáciou; pri diagnostike treba pozrieť aj `/proc/<pid>/environ` a aplikačný config dump, ak existuje.

## 13. Environment v kontajneroch

Kontajnerový proces dostane environment pri vytvorení kontajnera. Zmena Kubernetes ConfigMap alebo Secret automaticky nezmení environment už bežiaceho procesu.

Na aplikovanie zmeny je typicky potrebné vytvoriť nový Pod alebo použiť iný reload mechanizmus.

Environment nie je oddelený secret vault. Hodnoty môžu byť viditeľné:

- v process metadata,
- crash dumps,
- debug endpoints,
- deployment manifests,
- audit alebo CI logoch.

## 14. Secrets

Secrets v environment variables sú bežné, ale majú trade-offs:

- jednoduché injection,
- široké dedenie do child procesov,
- riziko logovania,
- nemožnosť jemného access lifecycle po štarte,
- zložitejšia rotácia bez reštartu.

Alternatívy zahŕňajú file-mounted secrets s permissions, Unix sockets, workload identity alebo dynamické credential APIs.

Nikdy nevypisuj celý environment do verejných alebo dlhodobo uchovávaných logov bez redakcie.

## 15. Expansion a default values v Bash

```bash
printf '%s\n' "${NAME:-default}"   # default pri unset alebo empty
printf '%s\n' "${NAME-default}"    # default iba pri unset
: "${REQUIRED:?REQUIRED must be set}"
```

Rozdiel medzi unset a empty je významný. Aplikácia má explicitne definovať, či prázdna hodnota znamená validnú konfiguráciu, default alebo chybu.

## 16. Diagnostika

Aplikácia funguje v interaktívnom shelli, ale zlyhá pod systemd:

1. Porovnaj executable, user, working directory a arguments.
2. Porovnaj PATH a relevantné environment values.
3. Over permissions a mount namespace služby.
4. Pozri `systemctl cat`, `systemctl show` a `/proc/<pid>/environ`.
5. Spusti aplikáciu s čistým environmentom a explicitnými hodnotami.
6. Nepokúšaj sa riešiť problém načítaním celého `.bashrc` do služby; tým vzniká skrytá a nestabilná závislosť.

## 17. Časté omyly

### „Environment variable je globálna pre celý server“

Nie. Každý proces má vlastný environment a child dostáva kópiu pri vytvorení.

### „Zmena exportu ovplyvní už bežiacu službu“

Nie. Existujúci proces má svoj pôvodný snapshot.

### „`.env` je univerzálny štandard“

Nie. Rôzne nástroje používajú rozdielnu syntax, quoting a expansion pravidlá.

### „Environment je bezpečné miesto pre secret, lebo nie je v súbore“

Nie automaticky. Environment môže byť dostupný cez procesné rozhrania a logy.

## 18. Kontrolné otázky

1. Prečo child process nedokáže zmeniť environment parent procesu?
2. Aký je rozdiel medzi shell variable a exportovanou variable?
3. Prečo môže mať systemd service iný PATH než používateľský shell?
4. Ako locale ovplyvňuje automatizačné skripty?
5. Prečo zmena Kubernetes ConfigMap nezmení environment existujúceho Podu?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Shell, Bash, pipes, redirection a exit codes](shell-bash-pipes-redirection-exit-codes.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: systemd, services a daemons →](systemd-services-daemons.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
