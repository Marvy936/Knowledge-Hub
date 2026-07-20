# Cron and systemd Timers

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Shell, Bash, pipes, redirection a exit codes](shell-bash-pipes-redirection-exit-codes.md), [Environment variables](environment-variables.md), [systemd, services a daemons](systemd-services-daemons.md)
- Súvisiace témy: automation, batch processing, idempotency, locking, observability

## 1. Definícia

Cron a systemd timers plánujú spustenie úloh podľa času alebo kalendárneho pravidla.

- cron spúšťa command podľa crontab expression,
- systemd timer aktivuje inú unit, najčastejšie `.service`.

Oba mechanizmy riešia scheduling, ale odlišujú sa v modeli konfigurácie, missed-run semantics, dependency managemente, observability a resource controls.

## 2. Cron model

Cron daemon načíta crontabs a v zodpovedajúcom čase spustí command v neinteraktívnom prostredí.

```text
crontab rule
  ↓ time match
cron daemon
  ↓ fork/exec shell command
process
  ↓ stdout/stderr podľa konfigurácie
```

User crontab:

```bash
crontab -e
crontab -l
```

System crontab môže byť v:

```text
/etc/crontab
/etc/cron.d/
/etc/cron.daily/
/etc/cron.hourly/
```

Presná implementácia a directories sa líšia podľa distribúcie.

## 3. Cron syntax

Klasická päťpolová syntax:

```text
minute hour day-of-month month day-of-week command
```

Príklady:

```cron
# Každých 5 minút
*/5 * * * * /usr/local/bin/check.sh

# Denne o 02:30
30 2 * * * /usr/local/bin/backup.sh

# Pondelok až piatok o 08:00
0 8 * * 1-5 /usr/local/bin/report.sh
```

Special strings môžu zahŕňať:

```cron
@reboot /usr/local/bin/startup-task.sh
@daily /usr/local/bin/daily-task.sh
```

Podpora závisí od cron implementation.

## 4. Day-of-month a day-of-week pasca

V mnohých cron implementations, keď sú day-of-month aj day-of-week obmedzené, job sa spustí pri zhode jedného z nich, nie nutne oboch.

Pravidlo:

```cron
0 0 1 * 1 command
```

nemusí znamenať iba „prvý deň mesiaca, ak je pondelok“. Môže znamenať „prvý deň každého mesiaca alebo každý pondelok“.

Pri kritických schedule pravidlách treba overiť konkrétnu implementáciu a radšej použiť explicitnú logiku alebo systemd calendar expression.

## 5. Cron environment

Cron nebeží v rovnakom prostredí ako interaktívny shell.

Typické rozdiely:

- minimálny `PATH`,
- iný working directory,
- nenačítaný `.bashrc`,
- chýbajúce environment variables,
- iný shell, často `/bin/sh`,
- žiadny TTY,
- odlišný locale.

Bezpečný pattern:

```cron
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

30 2 * * * /usr/local/bin/backup.sh >>/var/log/backup.log 2>&1
```

V scripts používaj absolútne paths tam, kde ambiguity predstavuje riziko.

## 6. Output a failure visibility

Historicky cron posiela stdout/stderr mailom lokálnemu používateľovi, ak je mail subsystem nakonfigurovaný. Na mnohých hostoch však výstup ostane nepozorovaný.

Nebezpečný pattern:

```cron
* * * * * command >/dev/null 2>&1
```

Úplne odstráni diagnostické dôkazy.

Lepší model:

- logovať do journald alebo kontrolovaného logu,
- kontrolovať exit status,
- emitovať metriku alebo heartbeat,
- alertovať pri zlyhaní alebo chýbajúcom úspechu,
- evidovať duration a processed-item count.

## 7. Overlap a concurrency

Ak job trvá dlhšie než interval, môže vzniknúť viac súbežných behov.

```text
Run 1: ───────────────
Run 2:      ───────────────
Run 3:           ───────────────
```

To môže spôsobiť:

- duplicitné spracovanie,
- race conditions,
- lock contention,
- preťaženie dependency,
- poškodenie shared state.

Jednoduchý host-local lock:

```cron
*/5 * * * * flock -n /run/check.lock /usr/local/bin/check.sh
```

`flock -n` skončí, ak lock už drží iný proces. Lock scope musí zodpovedať failure modelu. Host-local lock nezabráni súbehu na dvoch serveroch.

## 8. Idempotencia a retry

Scheduled job sa môže spustiť opakovane, oneskorene alebo po čiastočnom zlyhaní.

Dobrý job:

- má explicitný input scope,
- zapisuje progress alebo checkpoint,
- opakovanie je bezpečné,
- rozlišuje transient a permanent failures,
- používa bounded retries a backoff,
- neduplikuje side effects.

Cron sám neposkytuje robustný distributed workflow engine. Pri komplexných dependencies, retries a fan-out je vhodnejší špecializovaný scheduler alebo queue.

## 9. systemd timer model

Timer unit aktivuje service unit.

```text
example.timer
  ↓ trigger
example.service
  ↓ ExecStart
application process
```

`/etc/systemd/system/example.service`:

```ini
[Unit]
Description=Daily example job

[Service]
Type=oneshot
User=example
ExecStart=/usr/local/bin/example-job
```

`/etc/systemd/system/example.timer`:

```ini
[Unit]
Description=Run example job daily

[Timer]
OnCalendar=*-*-* 02:30:00
Persistent=true
RandomizedDelaySec=10m

[Install]
WantedBy=timers.target
```

Aktivácia:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now example.timer
```

## 10. Calendar expressions

```bash
systemd-analyze calendar 'daily'
systemd-analyze calendar 'Mon..Fri 08:00'
systemd-analyze calendar '*-*-* 02:30:00'
```

Tento príkaz ukáže normalizované pravidlo a najbližšie triggers. Je vhodný na validáciu pred nasadením.

Príklady:

```ini
OnCalendar=hourly
OnCalendar=Mon..Fri 08:00
OnCalendar=*-*-01 00:00
```

## 11. Monotonic timers

Systemd podporuje aj pravidlá relatívne k udalosti:

```ini
OnBootSec=10m
OnUnitActiveSec=1h
OnUnitInactiveSec=15m
```

- `OnBootSec` od bootu,
- `OnUnitActiveSec` od poslednej aktivácie,
- `OnUnitInactiveSec` od času, keď unit prestala byť active.

Monotonic timers sa správajú inak než wall-clock calendar schedules a nie sú závislé od timezone rovnakým spôsobom.

## 12. `Persistent=true`

Ak host pri plánovanom čase nebežal, persistent timer môže po štarte vykonať missed run.

```ini
Persistent=true
```

To je zásadný rozdiel oproti bežnému cron modelu, ktorý zmeškaný čas typicky nedobehne.

Riziko: po dlhom outage môže job spracovať veľký backlog alebo spustiť nevhodnú starú operáciu. Job musí vedieť interpretovať missed-run semantics.

## 13. Randomized delay a fleet safety

Keď tisíce hostov spustia job presne o 02:00, vznikne thundering herd.

```ini
RandomizedDelaySec=30m
```

rozloží runs v intervale.

Pri stabilnom rozložení môže byť relevantné aj fixed random delay správanie podľa dostupnej systemd verzie. Vždy over konkrétnu verziu hosta.

## 14. Accuracy

Systemd môže zoskupiť timers pre energetickú a scheduling efektivitu.

```ini
AccuracySec=1m
```

Timer nie je real-time scheduler. Ak job vyžaduje presnosť na milisekundy, cron ani bežný systemd timer nie sú vhodné.

## 15. Observability systemd timers

```bash
systemctl list-timers --all
systemctl status example.timer
systemctl status example.service
journalctl -u example.timer
journalctl -u example.service
systemctl show example.timer
```

Timer môže byť `active (waiting)`, zatiaľ čo posledný service run zlyhal. Preto treba kontrolovať timer aj service unit.

Exit status oneshot služby zostáva dostupný v systemd state a journal.

## 16. Dependencies a hardening

Service unit môže mať:

```ini
[Unit]
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
User=backup
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/var/lib/backup
```

`network-online.target` stále nie je dôkaz dostupnosti vzdialeného API alebo databázy. Aplikácia potrebuje timeout, retry a správnu failure classification.

## 17. Cron vs. systemd timer

| Vlastnosť | Cron | systemd timer |
|---|---|---|
| Konfigurácia | crontab line | `.timer` + `.service` |
| Logs | závisí od redirect/mail | journald a unit state |
| Missed runs | typicky nie | `Persistent=true` |
| Dependencies | minimálne | systemd dependency model |
| Resource controls | externé | service sandboxing/cgroups |
| Random delay | implementation-specific | `RandomizedDelaySec` |
| User jobs | jednoduché | user systemd units možné |
| Portabilita | široká | systemd systems |

Cron je vhodný pre jednoduché lokálne jobs. Systemd timer je prirodzený tam, kde je systemd autoritatívny service manager a potrebujeme lifecycle, logs, hardening alebo dependencies.

## 18. Troubleshooting cron

Job funguje ručne, ale nie z cronu:

1. skontroluj syntax a user crontab,
2. over cron daemon,
3. nastav explicitný PATH a shell,
4. použi absolútne paths,
5. presmeruj stdout/stderr do dočasného logu,
6. over working directory a permissions,
7. skontroluj timezone,
8. over SELinux/PAM policy,
9. spusti command v minimálnom environment-e.

Príklad simulácie:

```bash
env -i PATH=/usr/bin:/bin HOME="$HOME" /bin/sh -c '/usr/local/bin/job.sh'
```

## 19. Troubleshooting systemd timer

```bash
systemctl list-timers --all
systemctl status example.timer
systemctl status example.service
journalctl -u example.service -b
systemd-analyze calendar '<expression>'
systemctl cat example.timer
systemctl cat example.service
```

Kontroluj:

- timer enabled/active,
- next trigger,
- service exit status,
- effective unit a drop-ins,
- time synchronization a timezone,
- condition/assert directives,
- user, paths a environment,
- overlap s predchádzajúcim runom.

## 20. Časté omyly

### „Cron načíta môj `.bashrc`“

Nie automaticky. Beží v minimálnom neinteraktívnom prostredí.

### „Keď timer je active, job bol úspešný“

Nie. Timer môže čakať na ďalší trigger a posledná service execution mohla zlyhať.

### „Každých päť minút znamená, že nikdy nevznikne overlap“

Nie, ak run trvá dlhšie než interval.

### „Persistent timer bezpečne dobehne všetko“

Spustí missed activation podľa semantics, ale aplikácia musí bezpečne zvládnuť backlog a starý kontext.

### „Scheduled job nepotrebuje monitoring“

Potrebuje minimálne success/failure, duration, freshness a business outcome signal.

## 21. Kontrolné otázky

1. Prečo cron job nemusí fungovať rovnako ako ručný command?
2. Aké riziko vzniká pri overlap runs?
3. Kedy host-local `flock` nestačí?
4. Čo znamená `Persistent=true`?
5. Prečo timer status nestačí na overenie úspechu jobu?
6. Ako `RandomizedDelaySec` chráni fleet a dependencies?
7. Kedy je vhodnejší systemd timer než cron?
8. Kedy už treba workflow scheduler namiesto oboch?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: SSH](ssh.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Namespaces →](namespaces.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
