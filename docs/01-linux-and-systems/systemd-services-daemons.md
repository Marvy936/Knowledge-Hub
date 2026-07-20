# systemd, services a daemons

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Procesy, thready, PID a signals](processes-threads-pid-signals.md), [Environment variables](environment-variables.md)
- Súvisiace témy: journald, boot, cgroups, timers, service reliability

## 1. Daemon a service manager

Daemon je dlhšie bežiaci proces poskytujúci systémovú alebo aplikačnú službu. `systemd` je init systém a service manager, ktorý na mnohých distribúciách beží ako PID 1.

Jeho úlohy zahŕňajú:

- vytvorenie userspace počas bootu,
- spúšťanie a zastavovanie units,
- dependency ordering,
- sledovanie procesov cez cgroups,
- aktiváciu cez sockets, paths alebo timers,
- riadenie restart policy a timeouts,
- integráciu s journald.

## 2. Unit

Unit je objekt spravovaný systemd. Typ určuje suffix:

| Typ | Úloha |
|---|---|
| `.service` | proces alebo daemon |
| `.socket` | socket activation |
| `.target` | logická synchronizačná skupina |
| `.timer` | časová aktivácia |
| `.mount` | mount point |
| `.automount` | on-demand mount |
| `.path` | aktivácia zmenou cesty |
| `.slice` | hierarchia resource managementu |
| `.scope` | externe vytvorená skupina procesov |

Service unit nie je samotný proces. Je to desired configuration a runtime state, ktorými systemd riadi jednu alebo viac process groups.

## 3. Unit file locations a precedence

Typické cesty:

```text
/etc/systemd/system     lokálne administratorské units a overrides
/run/systemd/system     runtime units
/usr/lib/systemd/system vendor units na mnohých distribúciách
/lib/systemd/system     vendor path na iných distribúciách
```

Lokálna konfigurácia v `/etc` má vyššiu prioritu než vendor unit. Vendor súbor sa nemá upravovať priamo, pretože package upgrade ho môže prepísať.

Použi drop-in:

```bash
sudo systemctl edit example.service
```

Výsledok býva napríklad:

```text
/etc/systemd/system/example.service.d/override.conf
```

## 4. Základná service unit

```ini
[Unit]
Description=Example API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=example
Group=example
WorkingDirectory=/opt/example
EnvironmentFile=-/etc/example/example.env
ExecStart=/opt/example/bin/server --listen=:8080
Restart=on-failure
RestartSec=5s
TimeoutStopSec=30s

[Install]
WantedBy=multi-user.target
```

### `[Unit]`

Popisuje dependencies a ordering.

### `[Service]`

Definuje proces, identity, environment, lifecycle a reliability policy.

### `[Install]`

Určuje, ako sa unit zapojí pri `enable`. Táto sekcia sama o sebe nespúšťa službu.

## 5. Dependency vs. ordering

```ini
Wants=network-online.target
After=network-online.target
```

`Wants=` vytvára slabú requirement dependency. `After=` určuje iba poradie štartu alebo zastavenia; neznamená, že druhá unit bude automaticky spustená.

Toto rozlíšenie je zásadné:

```text
requirement dependency ≠ ordering dependency
```

`Requires=` je silnejšie než `Wants=`, ale ani ono automaticky neznamená, že aplikácia má funkčnú vzdialenú sieťovú službu. Aplikácia musí zvládať retry, timeout a neskoršie výpadky.

## 6. Service types

### `Type=simple`

Proces z `ExecStart` je main process. Systemd považuje službu za spustenú po vytvorení procesu.

### `Type=exec`

Podobné ako `simple`, ale štart sa považuje za úspešný až po úspešnom `execve()`.

### `Type=notify`

Aplikácia oznámi pripravenosť cez `sd_notify`. Je vhodné, keď proces potrebuje inicializovať dependencies pred prijímaním trafficu.

### `Type=forking`

Pre staršie daemons, ktoré sa samy backgroundujú. Moderná service má typicky zostať vo foregrounde a nechať lifecycle na systemd.

### `Type=oneshot`

Krátka úloha, často s `RemainAfterExit=yes`, ak má unit reprezentovať stav aj po skončení commandu.

## 7. ExecStart nie je shell command line

Systemd štandardne nespúšťa `ExecStart=` cez shell. Shell metacharacters ako pipe, redirect alebo `&&` sa neinterpretujú.

Chybné očakávanie:

```ini
ExecStart=/usr/bin/program > /var/log/program.log
```

`>` sa môže odovzdať ako obyčajný argument.

Ak je shell naozaj potrebný:

```ini
ExecStart=/bin/bash -c 'program | other-program'
```

To však pridáva quoting, error handling a injection riziká. Lepšie je používať natívne systemd možnosti ako `StandardOutput=journal`, wrapper script s testami alebo priamo aplikáciu.

## 8. Štart, enable a preset

```bash
systemctl start example.service
systemctl stop example.service
systemctl restart example.service
systemctl reload example.service
systemctl enable example.service
systemctl disable example.service
```

- `start` mení runtime state teraz,
- `enable` vytvára väzby pre budúce aktivácie, typicky pri boote,
- `enable --now` vykoná oboje,
- `reload` funguje iba ak unit definuje reload mechanizmus alebo ho aplikácia podporuje.

Enabled neznamená running a running neznamená enabled.

## 9. daemon-reload

Po zmene unit files alebo drop-ins:

```bash
sudo systemctl daemon-reload
```

Tým systemd manager znovu načíta unit definitions. Nereštartuje automaticky bežiacu službu a nie je to reload aplikačnej konfigurácie.

Typický tok:

```bash
sudo systemd-analyze verify /etc/systemd/system/example.service
sudo systemctl daemon-reload
sudo systemctl restart example.service
sudo systemctl status example.service
```

## 10. Procesy a cgroups

Systemd sleduje všetky procesy služby v jej cgroup, nie iba PID uložený v PID file.

```bash
systemctl status example.service
systemd-cgls
systemctl show example.service -p ControlGroup -p MainPID
```

To umožňuje konzistentnejšie zastaviť child procesy a aplikovať resource controls.

Nastavenia môžu zahŕňať:

```ini
MemoryMax=1G
CPUQuota=200%
TasksMax=512
```

Resource limit sa má nastaviť podľa pozorovaného workloadu a failure mode, nie náhodnou nízkou hodnotou.

## 11. Restart policy

```ini
Restart=on-failure
RestartSec=5s
StartLimitIntervalSec=60s
StartLimitBurst=5
```

Restart môže zlepšiť recovery pri transient failure, ale môže aj maskovať crash loop.

Dôležité otázky:

- Je operácia po reštarte bezpečná a idempotentná?
- Nespôsobí proces ďalšie poškodenie?
- Je medzi pokusmi backoff?
- Existuje alert na opakované restarty?
- Zachovajú sa diagnostické údaje?

`Restart=always` nie je automaticky správna reliability stratégia.

## 12. Graceful shutdown

Pri stop systemd typicky pošle nakonfigurovaný signal, počká `TimeoutStopSec` a potom môže použiť `SIGKILL`.

Relevantné options:

```ini
KillSignal=SIGTERM
TimeoutStopSec=30s
KillMode=control-group
```

Aplikácia má na `SIGTERM`:

1. prestať prijímať novú prácu,
2. dokončiť alebo bezpečne prerušiť in-flight operácie,
3. flushnúť stav,
4. ukončiť child procesy,
5. skončiť pred timeoutom.

## 13. Security hardening

Príklady:

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

Hardening treba zavádzať iteratívne a testovať. Príliš široké výnimky rušia ochranu; príliš úzke nastavenie môže blokovať legitímne system calls alebo paths.

Pomocný audit:

```bash
systemd-analyze security example.service
```

Výsledné skóre nie je dôkaz bezpečnosti. Je to zoznam hardening opportunities.

## 14. Logs a status

```bash
systemctl status example.service
journalctl -u example.service
journalctl -u example.service -b
journalctl -u example.service --since '10 minutes ago'
```

`systemctl status` zobrazuje iba výber posledných logov. Pre úplnejšiu analýzu použi `journalctl`.

Ďalšie užitočné príkazy:

```bash
systemctl cat example.service
systemctl show example.service
systemctl list-dependencies example.service
systemd-analyze critical-chain
systemd-analyze blame
```

`systemctl cat` zobrazí vendor unit aj drop-ins v poradí. Je autoritatívnejší než otvorenie jedného predpokladaného súboru.

## 15. Failed state

Keď process skončí chybou alebo štart prekročí limit, unit môže byť `failed`.

```bash
systemctl --failed
systemctl reset-failed example.service
```

`reset-failed` vymaže failed state a rate-limit counters; neopravuje root cause.

## 16. Socket activation

`.socket` unit môže držať listening socket a spustiť `.service` až pri spojení. File descriptor sa odovzdá službe.

Výhody:

- on-demand activation,
- paralelizácia bootu,
- zachovanie listening endpointu počas niektorých restart scenárov.

Aplikácia však musí podporovať socket activation alebo musí existovať vhodný wrapper.

## 17. Časté omyly

### „After=network.target znamená, že databáza je dostupná“

Nie. Určuje ordering voči lokálnemu targetu, nie health vzdialenej dependency.

### „enable službu okamžite spustí“

Nie bez `--now`.

### „daemon-reload reštartuje daemon“

Nie. Reloadne unit definitions v systemd manageri.

### „systemd potrebuje, aby daemon forkol do backgroundu“

Nie. Moderný model preferuje foreground process, ktorý systemd priamo sleduje.

### „Restart=always vyrieši nestabilitu“

Môže vytvoriť crash loop a tlak na dependencies. Recovery policy musí mať observability a limity.

## 18. Troubleshooting scenár

Služba funguje pri ručnom spustení, ale systemd ju opakovane reštartuje.

1. Pozri `systemctl status` a `journalctl -u`.
2. Zobraz efektívnu unit cez `systemctl cat`.
3. Porovnaj User, Group, WorkingDirectory, Environment a PATH.
4. Over `ExecStart` absolútnu cestu a arguments.
5. Skontroluj permissions, mount namespace a hardening options.
6. Over exit status a signal v `systemctl show`.
7. Dočasne vypni iba konkrétnu podozrivú ochranu, nie celý hardening.
8. Po oprave resetni failed state a over stabilitu bez crash loopu.

## 19. Kontrolné otázky

1. Aký je rozdiel medzi unit a procesom?
2. Prečo `After=` nie je requirement dependency?
3. Aký je rozdiel medzi `start`, `enable` a `daemon-reload`?
4. Prečo je foreground daemon vhodnejší pre systemd než self-daemonizing proces?
5. Ako cgroup pomáha systemd spravovať všetky child procesy služby?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Environment variables](environment-variables.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Package management →](package-management.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
