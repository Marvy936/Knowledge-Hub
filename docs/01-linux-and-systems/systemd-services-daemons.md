# systemd, services a daemons

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Procesy, thready, PID a signals](processes-threads-pid-signals.md), [Environment variables](environment-variables.md)
- Súvisiace témy: journald, boot, cgroups, timers, service reliability

## 1. Daemon, service a service manager

Daemon je dlhšie bežiaci proces poskytujúci systémovú alebo aplikačnú schopnosť. Service je širší prevádzkový objekt: zahŕňa procesy, konfiguráciu, dependencies, identity, resource policy, startup a shutdown pravidlá aj spôsob pozorovania výsledku.

`systemd` je init systém a service manager, ktorý na mnohých distribúciách beží ako PID 1. Nevlastní iba príkaz „spusti proces“; zostavuje dependency graph, vytvára execution context, sleduje procesy cez cgroups a rozhoduje, ako sa služba aktivuje, zastaví alebo zotaví po zlyhaní.

```text
unit definition
   ↓ load + merge + dependency graph
activation request
   ↓ execution context + cgroup
service processes
   ↓ status, signals, logs, restart policy
runtime outcome
```

## 2. Unit je desired configuration aj runtime state

Unit je objekt spravovaný systemd. Unit file opisuje zámer, ale manager zároveň vedie runtime state, dependency jobs, timestamps, exit result a cgroup priradenú danej unit.

Typ unit určuje suffix:

- **`.service` — správa procesu alebo skupiny procesov.** Definuje executable, user identity, environment, readiness, restart a shutdown lifecycle.
- **`.socket` — vlastní listening socket.** Môže aktivovať službu až pri prvom spojení a odovzdať jej už otvorený file descriptor.
- **`.target` — synchronizačný bod v dependency grafe.** Zoskupuje units podľa prevádzkového stavu, nie podľa spoločného procesu.
- **`.timer` — časová aktivácia inej unit.** Zachováva scheduling policy oddelene od samotnej vykonávanej práce.
- **`.mount` a `.automount` — modelujú mounty ako dependencies.** Umožňujú ordering a on-demand aktiváciu cez rovnaký job engine.
- **`.path` — aktivácia na základe filesystem udalosti.** Je vhodná iba tam, kde path event zodpovedá spoľahlivému trigger contractu.
- **`.slice` a `.scope` — organizujú cgroups.** Slice definuje hierarchiu resource policy, scope reprezentuje externe vytvorenú skupinu procesov.

Service unit preto nie je totožná s main PID. Jedna unit môže počas lifecycle vytvoriť viac procesov a systemd ju riadi ako cgroup a stavový objekt.

## 3. Odkiaľ systemd načíta unit definíciu

Manager prehľadáva viac vrstiev konfigurácie. Typické poradie priorít je lokálna administrátorská konfigurácia v `/etc`, runtime konfigurácia v `/run` a vendor definícia v `/usr/lib` alebo `/lib`.

```text
/etc/systemd/system      lokálne units a overrides
/run/systemd/system      dočasná runtime konfigurácia
/usr/lib/systemd/system  vendor units
/lib/systemd/system      alternatívny vendor path
```

Vendor unit sa nemá upravovať priamo, pretože package upgrade ju môže nahradiť. Administrátor používa drop-in, čím zachová upstream definíciu a explicitne prepíše iba potrebné properties.

```bash
sudo systemctl edit example.service
systemctl cat example.service
```

`systemctl cat` je dôležitejší než otvorenie jedného predpokladaného súboru. Zobrazí základnú unit aj drop-ins v poradí, z ktorého systemd skladá effective configuration.

## 4. Merge semantics a resetovanie list properties

Drop-in nemusí vždy iba „pridať ďalšiu hodnotu“. Scalar properties typicky nahradia starú hodnotu, zatiaľ čo niektoré list properties sa skladajú a pred novou definíciou ich treba explicitne resetovať prázdnym assignmentom.

```ini
[Service]
ExecStart=
ExecStart=/opt/example/bin/server --listen=:8080
```

Bez resetu môže override zlyhať alebo vytvoriť iný effective contract, než administrátor očakáva. Pri každej zmene preto treba overiť výsledok cez `systemctl cat`, `systemctl show` a `systemd-analyze verify`.

## 5. Základná štruktúra service unit

```ini
[Unit]
Description=Example API
Wants=network-online.target
After=network-online.target

[Service]
Type=notify
User=example
Group=example
WorkingDirectory=/opt/example
EnvironmentFile=-/etc/example/example.env
ExecStart=/opt/example/bin/server --listen=:8080
Restart=on-failure
RestartSec=5s
TimeoutStartSec=60s
TimeoutStopSec=30s

[Install]
WantedBy=multi-user.target
```

`[Unit]` opisuje vzťahy k ostatným units a ordering jobs. `[Service]` definuje execution a runtime lifecycle procesu. `[Install]` neurčuje aktuálny stav; opisuje, aké dependency links sa vytvoria pri `enable`.

Toto rozdelenie zabraňuje miešaniu troch odlišných otázok: čo služba potrebuje, ako má bežať a pri akých budúcich aktiváciách sa má zaradiť do grafu.

## 6. Dependency a ordering sú dve rôzne osi

`Wants=` alebo `Requires=` určuje requirement dependency. `After=` alebo `Before=` určuje ordering, teda poradie jobs pri štarte a zastavení.

```ini
Wants=network-online.target
After=network-online.target
```

`After=` samo o sebe druhú unit nespustí. `Wants=` ju pridá do transakcie, ale slabé zlyhanie nemusí zastaviť pôvodnú unit. `Requires=` vytvára silnejšiu väzbu, no stále negarantuje, že vzdialená databáza alebo API je funkčné počas celej životnosti služby.

Service manager rieši lokálny dependency graph. Aplikácia stále potrebuje timeout, retry, circuit breaker alebo degraded mode pre runtime dependencies, ktoré môžu zlyhať po úspešnom boote.

## 7. Targets nie sú health checks

Target ako `network-online.target` je synchronizačný bod, ktorého význam závisí od konkrétneho network managera a wait-online služby. Neznamená „DNS funguje, route je správna a databáza odpovedá“.

Target môže pomôcť pri boot orderingu, ale application readiness musí vychádzať z vlastného initialization contractu. Service, ktorá potrebuje vzdialený endpoint, má vedieť rozlíšiť dočasnú nedostupnosť od neobnoviteľnej konfigurácie a nemá sa spoliehať iba na boot target.

## 8. Service types určujú okamih považovaný za štart

### `Type=simple`

Proces z `ExecStart=` je main process a systemd považuje start job za úspešný hneď po jeho vytvorení. To je vhodné iba vtedy, keď vznik procesu dostatočne reprezentuje pripravenosť alebo keď dependencies nepotrebujú čakať na skutočnú readiness.

### `Type=exec`

Systemd čaká, kým sa úspešne vykoná `execve()`. Zachytí teda chyby ako neexistujúci executable alebo permission denial, ale stále nečaká na aplikačnú inicializáciu, bind socketu ani načítanie dát.

### `Type=notify`

Aplikácia explicitne odošle readiness správu cez `sd_notify`. Start job sa dokončí až po oznámení, takže dependent units môžu čakať na reálny initialization milestone namiesto samotného PID.

### `Type=forking`

Používa sa pre legacy daemons, ktoré sa samy daemonizujú a parent proces po forku skončí. Systemd potom musí identifikovať nový main process, často cez PID file, čo je krehkejšie než foreground model.

### `Type=oneshot`

Predstavuje konečnú úlohu, ktorej úspech je daný exit statusom. `RemainAfterExit=yes` môže zachovať unit ako active po skončení commandu, ale neznamená, že nejaký proces stále beží.

Výber type je readiness contract. Nesprávny type môže spôsobiť, že systemd označí službu ako active skôr, než je použiteľná, alebo čaká na udalosť, ktorú aplikácia nikdy neposkytne.

## 9. ExecStart nie je shell command line

Systemd štandardne parsuje `ExecStart=` vlastnou syntaxou a nespúšťa ho cez interaktívny shell. Operátory `|`, `>`, `&&` alebo globbing preto nemajú shellový význam.

```ini
ExecStart=/usr/bin/program > /var/log/program.log
```

Tu sa `>` môže stať obyčajným argumentom. Výstup sa má smerovať cez `StandardOutput=journal`, explicitný file descriptor model alebo cez testovaný wrapper script.

```ini
ExecStart=/bin/bash -c 'program | other-program'
```

Shell wrapper je legitímny iba vtedy, keď je pipeline skutočnou súčasťou service contractu. Prináša však quoting, pipeline status, signal propagation a injection riziká, ktoré treba explicitne navrhnúť.

## 10. Runtime activation, enable a preset

`start` vytvorí runtime job teraz. `enable` vytvorí dependency links pre budúce aktivácie, zvyčajne voči targetu uvedenému v `[Install]`.

```bash
systemctl start example.service
systemctl enable example.service
systemctl enable --now example.service
```

Enabled neznamená running a running neznamená enabled. Služba môže byť aktívna po manuálnom štarte bez boot väzby, alebo enabled, no momentálne failed či stopped.

`preset` aplikuje distribučnú alebo organizačnú policy, ktoré units majú byť defaultne enabled. Nie je to synonymum pre enable všetkého; je to mechanizmus na konzistentné zavedenie policy pri inštalácii systému.

## 11. daemon-reload, reload a restart riešia iné vrstvy

`systemctl daemon-reload` prikáže manageru znovu načítať unit definitions. Nezmení execution context už bežiaceho procesu a nereštartuje službu.

`systemctl reload` volá aplikáciou podporovaný reload mechanizmus, často cez `ExecReload=` alebo signal. `restart` ukončí starý proces a vytvorí nový podľa aktuálnej effective unit.

```text
zmena unit file     → daemon-reload
zmena runtime config s podporou reloadu → reload
zmena environmentu alebo executable contractu → restart
```

Správny postup závisí od toho, ktorá vrstva sa zmenila. Mechanické používanie `daemon-reload && restart` môže byť bezpečné, ale nepreukazuje pochopenie lifecycle ani minimalizáciu dopadu.

## 12. Cgroup je skutočná hranica služby

Systemd vytvorí pre service unit cgroup a priradí do nej main process aj jeho potomkov. Vďaka tomu nemusí hádať ownership iba podľa PID file alebo mena programu.

```bash
systemctl show example.service -p MainPID -p ControlGroup
systemd-cgls
```

Cgroup umožňuje konzistentný shutdown celej process tree a resource controls ako `MemoryMax=`, `CPUQuota=` alebo `TasksMax=`. Limity však musia vychádzať z workloadu a failure modelu; náhodne nízka hodnota môže vytvoriť OOM kills, throttling alebo fork failures bez zlepšenia spoľahlivosti.

## 13. MainPID a child procesy

`MainPID` reprezentuje proces, ktorého exit často určuje service result, ale nie je jediným procesom služby. Worker pool, helper alebo shell pipeline môžu vytvoriť ďalšie tasks v rovnakej cgroup.

Pri diagnostike preto nestačí sledovať jeden PID cez `ps`. Treba pozrieť cgroup, process tree a `KillMode`, pretože shutdown policy môže signalizovať iba main process alebo celú control group.

## 14. Readiness, liveness a active state

Unit `active` znamená, že systemd lifecycle podľa zvoleného `Type=` dosiahol aktívny stav. Neznamená automaticky, že aplikácia obsluhuje požiadavky správne, všetky dependencies sú healthy alebo business operation funguje.

Readiness má byť explicitný aplikačný kontrakt. `Type=notify`, socket bind, health endpoint a syntetická kontrola merajú rôzne vrstvy; ich kombinácia musí zodpovedať tomu, čo dependent service alebo load balancer potrebuje vedieť.

## 15. Restart policy je control loop

```ini
Restart=on-failure
RestartSec=5s
StartLimitIntervalSec=60s
StartLimitBurst=5
```

Restart policy transformuje exit result na nový activation attempt. Môže obnoviť službu po transient failure, ale bez limitov a observability vytvorí crash loop, zaťaží dependencies a prepíše diagnostický kontext.

Pri návrhu treba vysvetliť:

- **ktoré výsledky sú retryable;** konfiguračná chyba sa reštartom neopraví, kým dočasná strata dependency môže,
- **či je startup idempotentný;** opakovanie nesmie duplikovať migráciu, job alebo side effect,
- **aký backoff chráni systém;** okamžitý retry môže zhoršiť výpadok spoločnej dependency,
- **ako sa crash loop deteguje;** počet restartov a failed jobs musí byť monitorovaný,
- **aké evidence zostanú;** core dump, journal a exit metadata musia prežiť ďalší pokus.

`Restart=always` nie je reliability stratégia samo osebe. Je to len jedna časť control loopu, ktorý potrebuje klasifikáciu chýb, limity a escalation.

## 16. Start limits a failed state

Keď počet neúspešných štartov prekročí limit, systemd zastaví ďalšie automatické pokusy a unit môže zostať `failed`. Tento stav chráni host a dependencies pred nekonečným retry, no vyžaduje ľudskú alebo automatizovanú nápravu root cause.

```bash
systemctl --failed
systemctl show example.service -p Result -p ExecMainStatus -p ExecMainCode -p NRestarts
systemctl reset-failed example.service
```

`reset-failed` vymaže recorded failure a rate-limit counters. Neopravuje konfiguráciu, executable ani dependency; má sa použiť až po pochopení a odstránení príčiny.

## 17. Graceful shutdown je časovo ohraničený protokol

Pri stop jobe systemd odošle nakonfigurovaný signal, čaká na ukončenie a po `TimeoutStopSec=` môže eskalovať na `SIGKILL`. `KillMode=control-group` zabezpečí, že shutdown zahŕňa celú cgroup služby, nie iba main PID.

```ini
KillSignal=SIGTERM
TimeoutStopSec=30s
KillMode=control-group
```

Aplikácia musí po `SIGTERM` prestať prijímať novú prácu, dokončiť alebo bezpečne prerušiť in-flight operácie, flushnúť potrebný stav a ukončiť child procesy. Timeout musí byť dlhší než reálny drain contract, ale nie nekonečný; inak deployment alebo shutdown hosta môže zostať blokovaný.

## 18. ExecStartPre, ExecStartPost a lifecycle hooks

Lifecycle hooks môžu validovať prerequisites alebo vykonať doplnkový krok, ale nesmú skrývať nekontrolovaný provisioning v štarte každej služby. Každý hook má vlastný exit status a môže zmeniť výsledok activation jobu.

`ExecStartPost=` neznamená automaticky „po úplnej readiness aplikácie“; spustí sa podľa service type a systemd lifecycle. Ak je potrebné čakať na business readiness, má to byť súčasť explicitného notify alebo health contractu.

## 19. Security hardening mení execution boundary

```ini
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/example
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_BIND_SERVICE
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
```

Každá property mení konkrétnu attack alebo access boundary. `ProtectSystem=strict` robí veľkú časť filesystemu read-only, `PrivateTmp` vytvára oddelený `/tmp` view a capability sets zužujú privilege, ktoré proces môže získať.

Hardening sa má zavádzať iteratívne s testom startupu, normálnej prevádzky, reloadu a shutdownu. Široké výnimky môžu ochranu anulovať a príliš úzke policy môžu blokovať legitímny path alebo syscall, preto treba denial diagnostikovať po konkrétnej vrstve.

```bash
systemd-analyze security example.service
```

Skóre je heuristic checklist, nie dôkaz bezpečnosti. Threat model a effective runtime permissions zostávajú autoritatívnejšie než jedno číslo.

## 20. Socket activation mení ownership listening endpointu

Pri socket activation vlastní listening socket `.socket` unit. Service sa môže spustiť až pri prvej udalosti a dostane už otvorený file descriptor namiesto vlastného `bind()` lifecycle.

Tento model umožňuje on-demand activation, paralelizovať boot a v niektorých prípadoch zachovať endpoint počas restartu služby. Aplikácia však musí podporovať preberanie file descriptoru a musí mať jasné správanie pri backlogu, viacerých sockets a zlyhaní activation jobu.

## 21. Status a journal sú dve rozdielne evidence vrstvy

`systemctl status` kombinuje high-level unit state, main PID, result a malý výrez logov. Je vhodný na orientáciu, ale nie na úplnú časovú analýzu.

```bash
journalctl -u example.service -b
journalctl -u example.service --since '10 minutes ago'
systemctl show example.service
```

`systemctl show` poskytuje machine-readable properties ako `Result`, `ExecMainStatus`, `ActiveEnterTimestamp` alebo `NRestarts`. `journalctl` poskytuje event stream, z ktorého možno rekonštruovať startup, signals, restart attempts a aplikačné logy.

## 22. Diagnostika služby, ktorá funguje manuálne, ale nie pod systemd

Rozdiel je takmer vždy v execution context alebo lifecycle contracte. Postup:

1. **Získaj effective unit.** Použi `systemctl cat` a `systemctl show`, aby si videl vendor file, drop-ins, user, environment, hardening a výsledný executable.
2. **Identifikuj presný failure result.** Over `Result`, `ExecMainCode`, `ExecMainStatus` a journal od začiatku konkrétneho activation attemptu.
3. **Porovnaj execution context.** Skontroluj `User`, `Group`, `WorkingDirectory`, `PATH`, environment, mounts, capabilities a address-family restrictions.
4. **Over readiness contract.** Zisti, či je zvolený service type kompatibilný s tým, ako aplikácia signalizuje pripravenosť alebo daemonizuje.
5. **Pozri celú cgroup.** Worker alebo helper môže zlyhať, aj keď main PID krátko existoval.
6. **Izoluj jednu policy vrstvu.** Dočasne zmeň iba konkrétnu podozrivú hardening property a výsledok porovnaj; nevypínaj všetku ochranu naraz.
7. **Oprav root cause pred resetom stavu.** Až potom použi `reset-failed` a over, že služba zostáva stabilná bez crash loopu.

## 23. Časté omyly

### „After=network.target znamená, že databáza je dostupná“

Nie. `After=` určuje iba ordering lokálnych units. Vzdialená dependency potrebuje runtime timeout, retry a health model v aplikácii.

### „Enable službu okamžite spustí“

Nie bez `--now`. Enable mení budúce dependency links, zatiaľ čo start mení runtime state teraz.

### „daemon-reload reštartuje daemon“

Nie. Znovu načíta unit definitions v manageri. Bežiaci proces si ponechá starý execution context, kým sa reloadne alebo reštartuje príslušným mechanizmom.

### „systemd potrebuje self-daemonizing proces“

Nie. Foreground process je zvyčajne jednoduchší na supervision, signal delivery a exit tracking. Forking model je kompatibilita pre legacy daemons.

### „Restart=always vyrieši nestabilitu“

Nie. Môže iba opakovať rovnakú chybu, vytvoriť pressure na dependency a skryť incident. Restart policy potrebuje error classification, backoff, limits a alerting.

## 24. Kontrolné otázky

1. Prečo service unit nie je totožná s main PID?
2. Ako sa líši requirement dependency od ordering dependency?
3. Čo presne garantujú `Type=exec` a `Type=notify`?
4. Prečo `daemon-reload` nezmení environment už bežiacej služby?
5. Ako cgroup umožňuje systemd spravovať child procesy a resource limits?
6. Kedy môže restart policy zhoršiť incident?
7. Prečo `active` unit nemusí znamenať business-ready aplikáciu?
8. Ako socket activation mení ownership listening socketu?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Environment variables](environment-variables.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Package management →](package-management.md)
<!-- KNOWLEDGE-NAVIGATION:END -->