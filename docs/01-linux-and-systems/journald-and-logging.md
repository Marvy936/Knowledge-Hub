# journald and Logging

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [systemd, services a daemons](systemd-services-daemons.md), [Filesystem hierarchy, inodes a links](filesystem-hierarchy-inodes-links.md)
- Súvisiace témy: observability, log rotation, incident response, centralized logging

## 1. Definícia

Logging je zaznamenávanie udalostí systému a aplikácií. `systemd-journald` je system service, ktorá prijíma, obohacuje, indexuje a ukladá log records z viacerých zdrojov.

Journald neukladá iba textové riadky. Každý record môže obsahovať štruktúrované fields, napríklad:

- timestamp,
- unit,
- PID, UID a GID,
- executable,
- boot ID,
- priority,
- transport,
- message.

## 2. Zdroje logov

Journald prijíma záznamy najmä z:

```text
stdout/stderr systemd services
kernel ring buffer
syslog socket
native journal API
 audit a ďalšie integrácie
```

Systemd service nemusí zapisovať do vlastného súboru. Ak zapisuje na stdout/stderr, systemd output pripojí k unit a journald ho uloží s relevantnými metadátami.

## 3. Mentálny model

```text
Application / kernel
        ↓
Log record + metadata
        ↓
systemd-journald
  ├── rate limiting
  ├── enrichment
  ├── indexing
  ├── volatile/persistent storage
  └── optional forwarding
        ↓
journalctl / collector / SIEM
```

Journald je lokálny event store. Nie je automaticky dlhodobý centralizovaný log management.

## 4. Čítanie logov

Základné príkazy:

```bash
journalctl
journalctl -b
journalctl -b -1
journalctl -u ssh.service
journalctl -u example.service --since '30 minutes ago'
journalctl -p warning
journalctl -f
```

- `-b` filtruje aktuálny boot,
- `-b -1` predchádzajúci boot,
- `-u` konkrétnu unit,
- `-p` priority,
- `-f` sleduje nové records.

Časový interval:

```bash
journalctl --since '2026-07-20 10:00:00' --until '2026-07-20 11:00:00'
```

## 5. Structured fields

Výstup s fields:

```bash
journalctl -u example.service -o verbose
```

Časté fields:

```text
_MESSAGE=
_SYSTEMD_UNIT=
_PID=
_UID=
_COMM=
_EXE=
_BOOT_ID=
PRIORITY=
_TRANSPORT=
```

Filtrovanie podľa field:

```bash
journalctl _PID=1234
journalctl _COMM=sshd
journalctl _SYSTEMD_UNIT=nginx.service
```

Viac hodnôt rovnakého field-u sa typicky správa ako OR; rôzne fields sa kombinujú ako AND. Pri zložitejšom filtri treba výsledok explicitne overiť.

## 6. Priority

Syslog priority levels:

| Číslo | Názov |
|---|---|
| 0 | emerg |
| 1 | alert |
| 2 | crit |
| 3 | err |
| 4 | warning |
| 5 | notice |
| 6 | info |
| 7 | debug |

Príklad:

```bash
journalctl -p err..alert
```

Priority je iba klasifikácia emitera. Zle instrumentovaná aplikácia môže kritickú chybu zapísať ako `info` alebo bežnú udalosť ako `error`.

## 7. Volatile a persistent storage

Typické umiestnenia:

```text
/run/log/journal/   volatile, zmizne po reboote
/var/log/journal/   persistent
```

Správanie riadi `Storage=` v `journald.conf`:

```ini
[Journal]
Storage=auto
```

Bežné hodnoty:

- `volatile`,
- `persistent`,
- `auto`,
- `none`.

Pri `auto` môže existencia `/var/log/journal` rozhodnúť, či sa používa persistent storage.

Po zmene konfigurácie:

```bash
sudo systemctl restart systemd-journald
```

Restart journald treba robiť opatrne; niektoré descriptors a forwarding paths môžu mať distribučne špecifické správanie.

## 8. Disk usage a retention

```bash
journalctl --disk-usage
sudo journalctl --vacuum-time=14d
sudo journalctl --vacuum-size=1G
```

Relevantné nastavenia:

```ini
SystemMaxUse=
SystemKeepFree=
SystemMaxFileSize=
MaxRetentionSec=
RuntimeMaxUse=
```

Retention je kompromis medzi diagnostickou hodnotou a disk capacity. Príliš krátka retencia odstráni dôkazy pred incident review; nekontrolovaná retencia môže zaplniť filesystem.

## 9. Rate limiting

Journald môže obmedziť počet správ v intervale, aby log storm nevyčerpal CPU alebo disk.

```ini
RateLimitIntervalSec=30s
RateLimitBurst=10000
```

Pri prekročení limitu sa records zahodia a journald zapíše informáciu o suppressnutí.

Dôsledok: absencia jednotlivých logov nemusí znamenať, že udalosť nenastala. Pri incidente skontroluj, či neprebehol rate limiting.

## 10. Kernel logs

```bash
journalctl -k
journalctl -k -b
```

Alternatívne:

```bash
dmesg -T
```

Kernel ring buffer a journal nie sú úplne rovnaký pohľad. `dmesg` číta kernel buffer; journald môže kernel records uchovať spolu s boot metadata a persistent storage.

Kernel logy sú kľúčové pri:

- OOM killer,
- filesystem errors,
- device resets,
- network driver problémoch,
- security denials,
- hardware faults.

## 11. Output formats

```bash
journalctl -o short-iso
journalctl -o json
journalctl -o json-pretty
journalctl -o cat
```

- `short-iso` je vhodný pre ľudské čítanie s presným časom,
- `json` pre automatizované spracovanie,
- `cat` zobrazí iba message bez metadata.

Pri parsovaní preferuj structured output pred regexom nad human-readable textom.

## 12. journald, syslog a log files

Journald môže koexistovať s rsyslog alebo syslog-ng.

```text
Application
  ↓
journald
  ├── journal storage
  └── forwarding → rsyslog → text files / remote collector
```

Nie každá distribúcia používa rovnaké forwarding defaults. Autoritatívne je efektívne nastavenie hosta, nie všeobecný predpoklad.

Log rotation nástroj `logrotate` spravuje typicky textové log files. Journald má vlastnú segmentáciu a retention mechanizmy; jeho binary journal files sa nemajú rotovať ručne cez logrotate.

## 13. Čas a korelácia

Presná diagnostika potrebuje synchronizovaný čas.

```bash
timedatectl
```

Pri korelácii medzi hostmi sleduj:

- timezone,
- UTC vs. local time,
- clock drift,
- NTP stav,
- boot ID,
- monotonic timestamp.

Wall-clock time sa môže upraviť. Monotonic time rastie od bootu a je vhodná na poradie udalostí v rámci jedného bootu.

## 14. Diagnostický postup

Služba zlyhala po deploymente:

```bash
systemctl status example.service
journalctl -u example.service -b --since '15 minutes ago'
journalctl -u example.service -o verbose
systemctl show example.service -p ExecMainStatus -p Result
journalctl -k -b --since '15 minutes ago'
```

Postup:

1. urč čas a boot,
2. filtruj unit,
3. nájdi prvú chybu, nie iba posledný následok,
4. skontroluj exit status a signal,
5. rozšír pohľad na kernel a dependencies,
6. over, či logy neboli rate-limited,
7. koreluj so zmenami a deploymentom.

## 15. Bezpečnosť a citlivé údaje

Logy môžu obsahovať:

- access tokens,
- session IDs,
- osobné údaje,
- request bodies,
- interné hostnames,
- file paths,
- stack traces.

Aplikácia nemá logovať secrets. Access k journalu musí rešpektovať least privilege; členstvo v skupine s prístupom k systémovým logom môže odhaliť citlivé prevádzkové údaje.

## 16. Časté omyly

### „journalctl bez parametrov ukazuje iba aktuálny boot“

Nie vždy. Pri persistent journal môže zahŕňať viac bootov.

### „Keď v logu nič nie je, udalosť nenastala“

Log mohol byť rate-limited, filtrovaný, stratený pred zápisom alebo aplikácia nebola správne instrumentovaná.

### „systemctl status obsahuje celý log“

Nie. Zobrazuje iba obmedzený výrez.

### „journald nahrádza centralizované logovanie“

Nie. Rieši lokálny zber a query; retention, korelácia a vyhľadávanie naprieč fleetom vyžadujú ďalšiu vrstvu.

## 17. Kontrolné otázky

1. Čím sa journal record líši od obyčajného textového riadku?
2. Aký je rozdiel medzi volatile a persistent journalom?
3. Prečo môže journald zahodiť správy?
4. Aký je rozdiel medzi `journalctl -k` a `dmesg`?
5. Prečo `systemctl status` nestačí na úplnú diagnostiku?
6. Ako sa journald líši od logrotate?
7. Prečo je synchronizovaný čas kritický pri incidentoch?
8. Ktoré citlivé údaje nesmú byť v logoch?
