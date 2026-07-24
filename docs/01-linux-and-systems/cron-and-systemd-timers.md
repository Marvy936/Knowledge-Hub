# Cron a systemd timers

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Shell, Bash, pipes, redirection a exit codes](shell-bash-pipes-redirection-exit-codes.md), [Environment variables](environment-variables.md), [systemd, services a daemons](systemd-services-daemons.md)
- Súvisiace témy: automation, batch processing, idempotency, locking, observability, retries

## 1. Čo scheduling skutočne rieši

Cron a systemd timers rozhodujú, **kedy má vzniknúť pokus o vykonanie práce**. Samotný scheduler však negarantuje, že práca úspešne skončí, že sa nevykoná dvakrát ani že jej výsledok zostane správny.

Kompletný scheduled-job model preto obsahuje viac vrstiev:

```text
schedule
  ↓
trigger
  ↓
execution identity a environment
  ↓
application logic
  ↓
lock / idempotency / retry
  ↓
exit status a durable outcome
  ↓
logs, metrics a alert
```

Cron spúšťa command priamo podľa crontab pravidla. Systemd timer aktivuje inú unit, najčastejšie `.service`, a scheduling od execution lifecycle explicitne oddeľuje.

## 2. Požiadavky na spoľahlivý scheduled job

Pred výberom schedulera treba definovať prevádzkový kontrakt úlohy. Bez neho sa nedá rozhodnúť, či je zmeškaný, duplicitný alebo oneskorený run bezpečný.

- **Časová podmienka** — určuje, či ide o wall-clock čas, interval od posledného behu alebo udalosť po boote.
- **Execution identity** — určuje používateľa, skupiny, working directory, environment a oprávnenia procesu.
- **Input scope** — určuje, ktoré obdobie alebo položky má konkrétny run spracovať, aby retry nespracoval neurčitý pohyblivý rozsah.
- **Concurrency policy** — určuje, či sa behy môžu prekrývať, majú sa serializovať alebo má nový run starý nahradiť.
- **Missed-run policy** — určuje, či sa práca po downtime dobehne, preskočí alebo zlúči do jedného recovery runu.
- **Retry policy** — rozlišuje transient chybu od permanentnej a obmedzuje počet pokusov aj ich frekvenciu.
- **Success evidence** — definuje, čo je dôkazom úspechu: exit status, checkpoint, vytvorený artifact, spracovaný offset alebo potvrdený remote outcome.
- **Observability** — zachováva začiatok, koniec, duration, run ID, výsledok a dôvod zlyhania, aby tichý nebeh nevyzeral ako úspech.

Scheduler je iba prvá časť tohto kontraktu. Najčastejšie incidenty vznikajú v okolí scheduleru: skrytý environment, súbeh, nepozorovaný exit status alebo nebezpečný catch-up po výpadku.

## 3. Cron execution model

Cron daemon načíta crontab pravidlá a pri zhode času vytvorí proces s definovanou identitou. Command typicky vykoná cez shell, ale konkrétny shell, environment, mail handling a podporované rozšírenia závisia od implementácie.

```text
crontab entry
  ↓ time match
cron daemon
  ↓ set UID/GID + minimal environment
shell -c 'command'
  ↓
job process tree
  ↓
exit status + stdout/stderr
```

Používateľský crontab spravuje úlohy konkrétneho účtu:

```bash
crontab -e
crontab -l
```

Systémové úlohy môžu byť definované v `/etc/crontab`, `/etc/cron.d/` alebo distribučných periodic directories. Systémový formát často obsahuje navyše pole používateľa, preto nie je bezpečné kopírovať riadok medzi user crontabom a `/etc/cron.d/` bez kontroly syntaxe.

## 4. Cron syntax a calendar semantics

Klasická syntax obsahuje päť časových polí a command:

```text
minute hour day-of-month month day-of-week command
```

```cron
*/5 * * * * /usr/local/bin/check.sh
30 2 * * * /usr/local/bin/backup.sh
0 8 * * 1-5 /usr/local/bin/report.sh
```

Každé pole opisuje množinu povolených hodnôt, nie interval od posledného úspešného behu. Pravidlo `*/5 * * * *` preto vyhodnocuje wall-clock minúty deliteľné piatimi; nezaručuje päťminútový odstup od dokončenia predchádzajúceho runu.

### Day-of-month a day-of-week

V mnohých cron implementáciách sa pri súčasnom obmedzení `day-of-month` a `day-of-week` použije logika OR. Pravidlo:

```cron
0 0 1 * 1 command
```

môže znamenať prvý deň mesiaca **alebo** každý pondelok, nie iba prvý deň mesiaca, ktorý je pondelok. Kritické pravidlo treba overiť proti manuálu konkrétnej implementácie alebo podmienku presunúť do explicitného validačného kódu.

### Špeciálne aliasy

Aliasy ako `@reboot`, `@hourly` alebo `@daily` zlepšujú čitateľnosť, ale ich presná podpora je implementačne závislá. `@reboot` znamená spustenie po štarte cron daemonu, nie nevyhnutne po dosiahnutí plnej aplikačnej pripravenosti hosta.

## 5. Čas, timezone a DST

Cron je wall-clock scheduler. Jeho správanie preto ovplyvňuje timezone hosta, zmena systémového času a prechod na letný alebo zimný čas.

Pri posune hodín dopredu nemusí lokálny čas, napríklad `02:30`, v daný deň vôbec existovať. Pri posune späť sa rovnaký lokálny čas môže vyskytnúť dvakrát a niektoré implementácie môžu job spustiť dvakrát alebo použiť vlastnú kompenzačnú logiku.

Pre kritický job treba explicitne rozhodnúť:

- **UTC schedule** — znižuje sezónnu nejednoznačnosť, ale nemusí zodpovedať lokálnemu business času.
- **Lokálny business čas** — musí mať definované správanie počas DST prechodu a zmeny timezone.
- **Interval od posledného behu** — nie je to isté ako wall-clock cron pravidlo a vhodnejší môže byť monotonic timer alebo workflow scheduler.

Aplikácia má do logu zapisovať timestamp aj timezone alebo používať UTC. Samotný text „job bežal o 02:30“ nestačí na koreláciu počas opakovaného lokálneho času.

## 6. Cron environment a execution identity

Cron nezdedí interaktívny shell environment používateľa. Bežný rozdiel medzi manuálnym a plánovaným spustením preto nie je v aplikácii, ale v inom `PATH`, working directory, shelli, locale alebo dostupných credentials.

Typické vlastnosti cron procesu:

- **Minimálny `PATH`** — príkaz dostupný v interaktívnom shelli nemusí byť nájdený alebo sa môže vybrať iný executable.
- **Neurčený working directory** — relatívne cesty môžu smerovať mimo očakávaného adresára a meniť miesto zápisu.
- **Iný shell** — command môže bežať cez `/bin/sh`, hoci skript bol testovaný iba v Bashi.
- **Žiadny TTY** — nástroj čakajúci na interaktívny prompt alebo terminal capability môže visieť alebo zlyhať.
- **Iné locale** — parsovanie human-readable outputu sa môže meniť podľa `LANG` a `LC_*`.
- **Iné credential sources** — SSH agent, cloud login alebo desktop keyring dostupný v session nemusí existovať v cron kontexte.

Robustný crontab nastavuje minimum explicitne:

```cron
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
MAILTO=ops@example.invalid

30 2 * * * /usr/local/bin/backup-job
```

Ešte lepšie je presunúť komplexnú logiku do verziovaného executable alebo skriptu. Crontab potom zostáva deklaráciou času a identity namiesto nečitateľného shell programu v jednom riadku.

## 7. Output, exit status a tiché zlyhanie

Cron môže poslať stdout a stderr lokálnym mailom, ale iba ak mail subsystem funguje a niekto výstup reálne sleduje. Presmerovanie všetkého do `/dev/null` odstraňuje dôkaz, že job zlyhal, neštartoval alebo zostal visieť.

Nebezpečný vzor:

```cron
* * * * * command >/dev/null 2>&1
```

Spoľahlivejší job zachováva minimálne:

- **Run ID a plánovaný interval** — umožnia rozlíšiť retry od nového logického behu.
- **Start a finish event** — absencia finish eventu odhalí stuck alebo zabitý proces.
- **Exit status a failure class** — odlišia aplikačnú chybu, timeout, signal a validačné odmietnutie vstupu.
- **Duration a workload count** — odhalia postupné spomaľovanie alebo run, ktorý úspešne nespracoval nič.
- **Last-success signal** — umožní alertovať aj vtedy, keď scheduler job vôbec nespustil.

Exit status `0` je iba kontrakt procesu. Pri side effecte treba overiť aj durable outcome, napríklad checkpoint v databáze, checksum backupu alebo potvrdenie remote API.

## 8. Prekrývanie behov a locking

Cron nespomaľuje plán len preto, že predchádzajúci run stále beží. Keď duration presiahne interval, vzniknú dva alebo viac súbežných procesov.

```text
run A: ───────────────────
run B:      ───────────────────
run C:           ───────────────────
```

Súbeh môže viesť k duplicitnému spracovaniu, súťaženiu o lock, preťaženiu dependency alebo poškodeniu zdieľaného súboru. Pred zákazom súbehu však treba určiť, či paralelizácia nie je zámerná a či lock reprezentuje správny business scope.

Host-local serializácia:

```cron
*/5 * * * * flock -n /run/check.lock /usr/local/bin/check.sh
```

`flock -n` nevytvorí front; nový pokus skončí, ak lock drží iný proces. To je správne iba vtedy, keď preskočený run netreba neskôr spracovať.

Lock má mať tieto vlastnosti:

- **Lifecycle via file descriptor** — kernel lock sa uvoľní po skončení procesu aj pri páde, na rozdiel od primitívneho stale lock file.
- **Jednoznačný scope** — jeden lock pre celý job môže zbytočne blokovať nezávislé zákaznícke alebo dátové partitiony.
- **Zodpovedajúci failure domain** — host-local lock nechráni pred súbehom na druhom hoste; distributed job potrebuje shared claim, lease alebo queue semantics.
- **Pozorovateľný konflikt** — preskočenie pre lock má byť metrika alebo log, nie tichý úspech.

## 9. Idempotencia, checkpoint a retry

Scheduled job môže byť spustený dvakrát, po timeoute alebo po čiastočnom side effecte. Bez stabilnej identity logickej práce scheduler nevie rozlíšiť nový interval od opakovania rovnakého intervalu.

Praktický model:

```text
logical_run_id = job_name + input_window
claim logical_run_id atomicky
spracuj explicitný input_window
ulož checkpoint alebo result
označ completed
retry používa rovnaký logical_run_id
```

Dobrý job:

- **Spracúva explicitný interval** — napríklad `[2026-07-24T00:00Z, 2026-07-25T00:00Z)`, nie neurčité „všetko nové teraz“.
- **Používa atomický claim** — dva schedulery nemôžu súčasne prevziať rovnaký logical run.
- **Checkpointuje progres** — dlhý run nemusí po zlyhaní začínať od nuly ani opakovať hotové side effects.
- **Rozlišuje transient failure** — network timeout môže dostať bounded retry s backoffom, zatiaľ čo invalidný vstup vyžaduje opravu.
- **Deduplikuje externé side effects** — e-mail, platba alebo publikovanie eventu potrebuje stabilný operation ID.
- **Má deadline** — retry starého runu nesmie neobmedzene konkurovať aktuálnej práci.

Cron ani systemd timer nie sú distributed workflow engines. Fan-out, dependency graph, durable queues a komplexné recovery stavy patria do nástroja, ktorý tieto vlastnosti explicitne poskytuje.

## 10. Systemd timer model

Systemd oddeľuje plán od vykonania. `.timer` unit určuje trigger a `.service` unit určuje identity, environment, command, sandbox, resource limits a výsledný stav.

```text
example.timer
  ↓ activation event
example.service
  ↓ cgroup + execution policy
job process tree
  ↓
service result + journal
```

Service unit:

```ini
[Unit]
Description=Daily example job

[Service]
Type=oneshot
User=example
Group=example
WorkingDirectory=/var/lib/example
ExecStart=/usr/local/bin/example-job
```

Timer unit:

```ini
[Unit]
Description=Schedule daily example job

[Timer]
OnCalendar=*-*-* 02:30:00
Persistent=true
RandomizedDelaySec=10m
Unit=example.service

[Install]
WantedBy=timers.target
```

Aktivácia:

```bash
sudo systemd-analyze verify /etc/systemd/system/example.service /etc/systemd/system/example.timer
sudo systemctl daemon-reload
sudo systemctl enable --now example.timer
```

Timer môže byť `active (waiting)`, hoci posledná aktivovaná service skončila chybou. Prevádzkový monitoring preto musí sledovať schedule state aj execution result.

## 11. Calendar timers

`OnCalendar=` používa wall-clock calendar expression. Výraz treba validovať, pretože ľudská interpretácia dátumu alebo rozsahu sa môže líšiť od normalizovaného systemd pravidla.

```bash
systemd-analyze calendar 'daily'
systemd-analyze calendar 'Mon..Fri 08:00'
systemd-analyze calendar '*-*-01 00:00:00'
```

Výstup ukáže normalizovanú formu a najbližšie triggers. Pri timezone-sensitive úlohe treba overiť timezone managera, prípadnú direktívu `Timezone=` podporovanú danou verziou a správanie počas DST.

Calendar trigger znamená, že service sa má aktivovať v danom čase. Neznamená, že sa job spustí presne na sekundu pri preťaženom hoste ani že sa aktivácia vykoná, ak je service už active.

## 12. Monotonic timers

Monotonic timers merajú interval voči udalosti v runtime lifecycle, nie voči kalendárnemu času. Nie sú ovplyvnené manuálnym posunom wall clock rovnakým spôsobom ako `OnCalendar=`.

```ini
[Timer]
OnBootSec=10m
OnUnitActiveSec=1h
OnUnitInactiveSec=15m
```

- **`OnBootSec=`** — aktivuje unit po uplynutí času od bootu; vhodné pre oneskorený housekeeping po štarte.
- **`OnUnitActiveSec=`** — počíta od poslednej aktivácie unit, preto interval nezávisí od dĺžky dokončenia rovnakým spôsobom ako calendar schedule.
- **`OnUnitInactiveSec=`** — počíta od momentu, keď unit prestala byť active, a je vhodný pre odstup po dokončení.

Výber závisí od významu práce. „Každý deň o polnoci“ je calendar semantics, zatiaľ čo „pätnásť minút po skončení predchádzajúceho behu“ je inactive-relative semantics.

## 13. Missed runs a `Persistent=true`

Bežný cron zmeškaný wall-clock okamih typicky nedobehne. Systemd calendar timer s `Persistent=true` si uloží posledný trigger timestamp a po opätovnom štarte môže aktivovať zmeškaný run.

```ini
Persistent=true
```

Catch-up nie je automaticky správny. Po trojdňovom outage môže existovať viac logických období, ale timer typicky aktivuje service, nie tri samostatné business runy s automaticky odvodenými intervalmi.

Aplikácia preto potrebuje vlastnú missed-run politiku:

- **Skip** — staré obdobia už nemajú hodnotu a spracuje sa iba aktuálny stav.
- **Coalesce** — jeden recovery run spracuje celý backlog v explicitnom rozsahu.
- **Replay each interval** — workflow vytvorí samostatnú identitu pre každé zmeškané obdobie.
- **Require approval** — starý side effect môže byť nebezpečný a catch-up čaká na operátora.

`Persistent=true` rieši zaznamenanie zmeškaného timer triggeru, nie business-level replay semantics.

## 14. Randomized delay, jitter a fleet safety

Ak tisíce hostov spustia backup alebo repository refresh v rovnakej sekunde, vznikne thundering herd. Náhodné oneskorenie rozloží load na dependency, sieť aj storage.

```ini
RandomizedDelaySec=30m
```

Jitter mení čas konkrétneho pokusu v povolenom intervale. Nemá však nahradiť kapacitný limit, concurrency control ani backpressure na centrálnej službe.

`AccuracySec=` umožňuje manageru zoskupiť wakeups a znižovať overhead. Systemd timer ani cron nie sú real-time schedulery; exact-time požiadavka musí tolerovať scheduling delay, boot, pressure a service activation latency.

## 15. Systemd service lifecycle pre job

Timer iba aktivuje service. Všetky prevádzkové vlastnosti jobu patria primárne do `.service` unit.

```ini
[Service]
Type=oneshot
User=backup
Group=backup
WorkingDirectory=/var/lib/backup
EnvironmentFile=-/etc/backup/job.env
ExecStart=/usr/local/bin/backup-job
TimeoutStartSec=2h
Nice=10
IOSchedulingClass=best-effort
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/var/lib/backup /var/log/backup
```

Dôležité aspekty:

- **`Type=oneshot`** — systemd čaká na ukončenie commandu a jeho status použije ako výsledok unit.
- **Timeout** — zabráni permanentne visiacemu jobu, ale aplikácia musí korektne reagovať na `SIGTERM` a zachovať checkpoint.
- **Cgroup ownership** — child procesy zostávajú v unit cgroup, takže timeout a stop môžu ukončiť celý process tree.
- **Sandbox** — obmedzí write paths, privilege escalation a viditeľnosť častí systému.
- **Resource controls** — CPU, memory, I/O a task limity znižujú blast radius, ale príliš nízke hodnoty môžu vytvoriť nové zlyhanie.

`Restart=on-failure` pri timer jobe treba používať opatrne. Interný restart service môže vytvoriť ďalšie pokusy mimo calendar identity a skomplikovať deduplikáciu; často je vhodnejšie, aby bounded retry riadila aplikácia alebo workflow s explicitným run ID.

## 16. Dependencies a remote readiness

Systemd môže zoradiť job voči lokálnym units, mountom alebo network targetom. Ordering však nie je health check vzdialenej databázy ani garancia funkčného DNS, TLS alebo credentials.

```ini
[Unit]
RequiresMountsFor=/var/lib/backup
Wants=network-online.target
After=network-online.target
```

`RequiresMountsFor=` pomôže aktivovať mount dependencies pre konkrétnu cestu. `network-online.target` vyjadruje lokálnu predstavu network managera o pripravenosti, nie dostupnosť konkrétneho remote endpointu.

Aplikácia stále potrebuje:

- timeout pre connect a request,
- bounded retry s backoffom,
- rozlíšenie authentication, validation a transient network failure,
- kontrolu, že remote side effect neprebehol pred timeoutom,
- jasný exit status pre service manager.

## 17. User timers

Systemd podporuje aj user units. Tie riadi per-user manager a ich lifecycle závisí od login session alebo lingering konfigurácie.

```bash
systemctl --user enable --now example.timer
loginctl show-user "$USER" -p Linger
```

User timer nie je automaticky vhodný pre serverový kritický job. Treba overiť, či user manager beží bez aktívneho loginu, kde sú uložené units, aký environment manager používa a kto vlastní prevádzkovú zodpovednosť.

System service timer je zvyčajne jasnejší pre host-level prevádzkovú úlohu. User timer je vhodný tam, kde práca patrí používateľskému session alebo nevyžaduje systémovú identitu.

## 18. Observability a success monitoring

Základná kontrola systemd timeru:

```bash
systemctl list-timers --all
systemctl status example.timer
systemctl status example.service
systemctl show example.timer -p LastTriggerUSec -p NextElapseUSecRealtime
systemctl show example.service -p Result -p ExecMainStatus -p ExecMainCode
journalctl -u example.timer -u example.service -b
```

Timer state odpovedá, či scheduler čaká a kedy triggeroval. Service state odpovedá, či posledný execution pokus skončil úspešne, signalom, timeoutom alebo resource failure.

Monitoring má používať viac než stav `active`:

- **Last successful logical run** — odhalí, že timer triggeruje, ale aplikácia opakovane zlyháva.
- **Expected next run** — odhalí disabled alebo nesprávne načítaný schedule.
- **Duration trend** — odhalí blížiaci sa overlap alebo rast backlogu.
- **Processed scope** — odhalí úspešný proces, ktorý spracoval nesprávne obdobie.
- **Skipped/locked runs** — odhalí chronické prekrývanie alebo stuck job.

Heartbeat založený iba na štarte je slabý. Autoritatívny heartbeat má vzniknúť až po potvrdení durable outcome.

## 19. Cron verzus systemd timer

| Vlastnosť | Cron | Systemd timer |
|---|---|---|
| Scheduling objekt | crontab entry | `.timer` unit |
| Execution policy | command v cron kontexte | samostatná `.service` unit |
| Missed calendar run | typicky sa preskočí | voliteľný catch-up cez `Persistent=true` |
| Logs a status | mail/redirection/external monitoring | journald a unit result |
| Dependency graph | minimálny | systemd ordering a requirements |
| Sandboxing a limits | externý wrapper | natívna service policy a cgroups |
| Fleet jitter | závisí od implementácie alebo skriptu | `RandomizedDelaySec=` |
| Portabilita | široká medzi Unix systémami | systémy so systemd |

Cron je vhodný pre jednoduchý lokálny schedule, ak tím explicitne doplní environment, locking, logs a monitoring. Systemd timer je prirodzený na systemd hoste, keď job potrebuje service identity, cgroup supervision, sandbox, persistent trigger alebo jednotnú diagnostiku.

Ani jeden mechanizmus nenahrádza distributed workflow engine. Rozhodnutie má vychádzať z failure semantics, nie z počtu riadkov konfigurácie.

## 20. Troubleshooting: job funguje ručne, ale nie z cronu

Postup musí reprodukovať cron kontext namiesto náhodného pridávania exportov do `.bashrc`.

1. **Over načítaný crontab a používateľa** — user crontab a `/etc/cron.d/` používajú odlišný formát a identity pravidlá.
2. **Over cron daemon a jeho logy** — najprv potvrď, že trigger vôbec nastal.
3. **Zachovaj stdout, stderr a exit status** — bez nich nemožno odlíšiť nespustenie od aplikačného zlyhania.
4. **Nastav explicitný `PATH`, shell a working directory** — odstrániš závislosť na interaktívnej session.
5. **Reprodukuj minimálny environment** — napríklad cez `env -i`, ale pridaj iba hodnoty, ktoré kontrakt vyžaduje.
6. **Over permissions a credentials** — vrátane home, mountov, SELinux/AppArmor a remote keys.
7. **Over timezone a calendar match** — najmä pri DST a rozdielnej systémovej timezone.
8. **Skontroluj overlap a lock result** — job mohol byť správne triggerovaný, ale okamžite preskočený.

```bash
env -i \
  PATH=/usr/bin:/bin \
  HOME=/var/lib/example \
  LANG=C.UTF-8 \
  /bin/bash -c 'cd /var/lib/example && /usr/local/bin/example-job'
```

## 21. Troubleshooting: timer čaká, ale job nevytvára výsledok

Systemd timer a service treba diagnostikovať ako dva samostatné objekty.

1. **Zobraz efektívnu unit konfiguráciu** — `systemctl cat example.timer` a `systemctl cat example.service` odhalia drop-ins aj override precedence.
2. **Validuj calendar výraz** — `systemd-analyze calendar` ukáže normalizované pravidlo a ďalšie triggers.
3. **Over načítanie a enablement** — timer môže existovať, ale nebyť enabled alebo môže byť masked.
4. **Skontroluj `LastTriggerUSec` a service result** — trigger mohol prebehnúť, ale service zlyhala.
5. **Čítaj journal pre obe units** — timer log vysvetľuje aktiváciu, service log execution failure.
6. **Over service identity a sandbox** — working directory, environment, write paths a capabilities sa líšia od manuálneho shellu.
7. **Over input scope a checkpoint** — úspešný exit status nemusí znamenať správny business outcome.
8. **Over catch-up policy** — `Persistent=true` mohol po boote spustiť starú prácu s neočakávaným rozsahom.

## 22. Časté omyly

### „Cron každých päť minút znamená päť minút po dokončení“

Nie. Cron vyhodnocuje wall-clock polia; dlhý job sa môže prekrývať s ďalším triggerom. Interval po dokončení treba modelovať iným mechanizmom alebo explicitným orchestration state.

### „Keď nie je log, job bol úspešný“

Absencia logu môže znamenať, že trigger nenastal, command sa nenašiel, output bol zahodený alebo logging zlyhal. Success potrebuje pozitívny durable signal.

### „`flock` vyrieši distributed concurrency“

Bežný lock nad lokálnym filesystemom chráni iba zodpovedajúci host a namespace. Viac hostov potrebuje spoločný atomický claim alebo distributed lease.

### „`Persistent=true` prehrá každý zmeškaný interval“

Timer môže aktivovať service po downtime, ale nevytvorí automaticky samostatné business runy pre každý zmeškaný interval. Replay logiku musí definovať aplikácia alebo workflow.

### „Timer je active, takže job funguje“

`active (waiting)` opisuje scheduler. Posledná service activation mohla skončiť chybou, timeoutom alebo nesprávnym výsledkom.

### „`network-online.target` znamená dostupnú databázu“

Target vyjadruje lokálny network readiness model. Remote DNS, route, firewall, TLS, authentication a aplikácia môžu stále zlyhať.

## 23. Kontrolné otázky

1. Prečo scheduler negarantuje úspešný outcome jobu?
2. Aký je rozdiel medzi wall-clock cron pravidlom a intervalom od dokončenia?
3. Prečo môže DST vytvoriť zmeškaný alebo duplicitný run?
4. Aké rozdiely medzi interaktívnym shellom a cron environmentom najčastejšie spôsobujú incident?
5. Prečo host-local `flock` nestačí pre job spúšťaný na viacerých serveroch?
6. Čo musí obsahovať stabilná identita logického scheduled runu?
7. Aký je rozdiel medzi `OnCalendar=`, `OnUnitActiveSec=` a `OnUnitInactiveSec=`?
8. Čo presne rieši `Persistent=true` a čo nerieši?
9. Prečo treba monitorovať timer aj aktivovanú service?
10. Ktorý dôkaz je silnejší než samotný exit status `0`?

## 24. Zhrnutie

Cron a systemd timers vytvárajú časový trigger, nie úplný reliability model. Spoľahlivý scheduled job potrebuje explicitnú identitu, environment, input scope, concurrency a missed-run policy, idempotentný execution path, bounded retries a pozitívny dôkaz výsledku.

Cron je jednoduchý a prenosný, ale veľa lifecycle vlastností musí doplniť job alebo externá platforma. Systemd timer oddeľuje schedule od service execution a poskytuje lepšiu integráciu s unit stavom, journald, cgroups, dependencies a sandboxom, no business-level checkpoint, replay a deduplikáciu musí stále riešiť aplikácia.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: SSH](ssh.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Namespaces →](namespaces.md)
<!-- KNOWLEDGE-NAVIGATION:END -->