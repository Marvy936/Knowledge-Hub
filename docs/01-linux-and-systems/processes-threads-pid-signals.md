# Procesy, thready, PID a signals

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Kernel a user space](kernel-and-user-space.md)
- Súvisiace témy: scheduling, memory, systemd, containers, observability

## 1. Proces

Proces je bežiaca inštancia programu spolu s execution contextom a kernelom spravovaným stavom. Zahŕňa najmä:

- virtuálny adresný priestor,
- otvorené file descriptors,
- credentials a capabilities,
- current working directory,
- environment,
- signal dispositions,
- jeden alebo viac threadov.

Program na disku je pasívny súbor. Proces je aktívne vykonávanie tohto programu.

## 2. PID a hierarchia procesov

Kernel prideľuje procesu process ID — PID. Proces má aj parent PID — PPID.

```bash
ps -eo pid,ppid,user,stat,comm,args --forest
```

Procesy vytvárajú hierarchiu. Na modernom Linuxe býva PID 1 init systém, typicky `systemd`. PID 1 má špeciálnu zodpovednosť za adoptovanie orphan procesov a reaping zombie procesov.

PID nie je globálne večne jedinečný. Po ukončení procesu môže byť neskôr znovu použitý. Preto samotný PID bez času alebo ďalšieho kontextu nie je stabilná identita.

## 3. Vznik procesu: fork/clone a exec

Typický Unix model:

```text
existujúci proces
    │
    ├── fork/clone → nový execution context
    │
    └── execve     → nahradenie programu v procese
```

`fork()` logicky vytvorí potomka. Moderný kernel využíva copy-on-write, takže fyzická pamäť sa nekopíruje okamžite celá.

`execve()` nevytvorí nový PID. Nahradí program, adresný priestor a väčšinu runtime state existujúceho procesu novým executable.

Shell pri spustení príkazu typicky vytvorí child process a v ňom vykoná `execve()`.

## 4. Thread

Thread je samostatne schedulovateľný tok vykonávania v rámci procesu. Thready toho istého procesu typicky zdieľajú:

- adresný priestor,
- heap,
- otvorené file descriptors,
- väčšinu process-wide state.

Každý thread má vlastný:

- stack,
- registers,
- instruction pointer,
- scheduling state,
- thread ID.

Zdieľaná pamäť robí komunikáciu rýchlou, ale vytvára race conditions. Synchronizácia používa mutexy, semafory, atomické operácie alebo futexy.

## 5. Process states

Stĺpec `STAT` v `ps` môže obsahovať napríklad:

| Stav | Význam |
|---|---|
| `R` | running alebo runnable |
| `S` | interruptible sleep |
| `D` | uninterruptible sleep, často čakanie na I/O |
| `T` | stopped alebo traced |
| `Z` | zombie |

Proces v stave `R` nemusí práve bežať na CPU; môže čakať v run queue.

`D` nie je automaticky deadlock. Znamená, že thread čaká v kernelovej operácii, ktorú nemožno bezpečne prerušiť. Dlhodobý vysoký počet `D` procesov často ukazuje na storage alebo network filesystem problém.

## 6. Zombie a orphan

Zombie už nevykonáva kód. Ukončil sa, ale parent ešte neprevzal exit status cez `wait()`.

Zombie spotrebúva minimálny kernelový záznam, nie bežnú aplikačnú pamäť. Veľké množstvo zombie procesov však môže vyčerpať PID space a indikuje chybný parent process.

Orphan je živý proces, ktorému skončil parent. Kernel ho priradí vhodnému reaperu, typicky PID 1 alebo subreaperu.

## 7. Exit status

Proces pri ukončení poskytne číselný exit status. Konvencia:

- `0` — úspech,
- nenulová hodnota — chyba alebo špecifický výsledok.

```bash
command
printf '%s\n' "$?"
```

Shell uchováva status iba posledného foreground pipeline alebo príkazu. Preto ho treba prečítať skôr, než sa spustí ďalší príkaz.

Pri ukončení signalom shell často reportuje `128 + číslo signalu`, ale ide o shellovú konvenciu, nie univerzálny kernelový exit code.

## 8. Signals

Signal je asynchrónne oznámenie procesu alebo threadu. Nie je to payload-rich message queue; prenáša najmä typ udalosti.

Dôležité signály:

| Signal | Typický význam |
|---|---|
| `SIGHUP` | reload alebo strata terminálu |
| `SIGINT` | interaktívne prerušenie, typicky Ctrl+C |
| `SIGTERM` | žiadosť o korektné ukončenie |
| `SIGKILL` | okamžité ukončenie kernelom |
| `SIGSTOP` | okamžité zastavenie |
| `SIGCONT` | pokračovanie |
| `SIGCHLD` | zmena stavu child procesu |
| `SIGSEGV` | neplatný memory access |

`SIGKILL` a `SIGSTOP` nemožno zachytiť, ignorovať ani blokovať. Pri `SIGTERM` môže proces dokončiť requesty, flushnúť dáta a odstrániť dočasné resources.

## 9. Bezpečné ukončovanie

Odporúčaný postup:

```bash
kill -TERM <pid>
# počkaj a over stav
kill -KILL <pid>   # až keď korektné ukončenie zlyhá
```

`kill` neposiela automaticky `SIGKILL`; bez parametra posiela `SIGTERM`.

Pri službách je lepšie použiť správcu služby:

```bash
systemctl stop example.service
```

Ten pozná cgroup služby, timeouty a definovaný shutdown lifecycle.

## 10. /proc

`/proc` poskytuje kernelový pohľad na procesy:

```bash
cat /proc/<pid>/status
tr '\0' ' ' < /proc/<pid>/cmdline
ls -l /proc/<pid>/fd
cat /proc/<pid>/limits
cat /proc/<pid>/cgroup
```

Dôležité je rozlišovať:

- command line — argumenty pri spustení,
- executable — cieľ `/proc/<pid>/exe`,
- environment — `/proc/<pid>/environ`,
- open descriptors — `/proc/<pid>/fd`.

Čítanie môže byť obmedzené permissions alebo mount nastavením `hidepid`.

## 11. Diagnostické príkazy

```bash
ps aux
pgrep -a <name>
pidof <program>
top
pstree -p
lsof -p <pid>
strace -f -p <pid>
```

`pgrep` je bezpečnejší než `ps | grep`, pretože vyhľadáva process metadata a nezhoduje vlastný grep proces.

## 12. Časté omyly

### „Jeden proces používa jedno CPU“

Proces môže mať viac threadov a tie môžu bežať paralelne na viacerých CPU. Jednovláknový proces však v jednom okamihu vykonáva iba jeden thread.

### „SIGKILL je normálny spôsob reštartu“

Nie. Obchádza cleanup a môže zanechať nedokončené transakcie, lock files alebo nekonzistentný externý stav.

### „Zombie stále vykonáva prácu“

Nie. Je už ukončený; parent iba neprevzal jeho status.

## 13. Troubleshooting scenár

Služba nereaguje a `systemctl stop` čaká až do timeoutu.

1. Zisti main PID a cgroup služby.
2. Skontroluj process states a thready.
3. Pozri logy pred odoslaním `SIGTERM` a po ňom.
4. Použi `strace -p` alebo stack dump, ak je bezpečný.
5. Over, či proces čaká na I/O, lock alebo child process.
6. `SIGKILL` použi až po získaní diagnostických údajov.

## 14. Kontrolné otázky

1. Aký je rozdiel medzi programom, procesom a threadom?
2. Prečo `execve()` nemení PID?
3. Čo presne znamená zombie proces?
4. Prečo je dlhodobý stav `D` dôležitý diagnostický signál?
5. Aký je rozdiel medzi `SIGTERM` a `SIGKILL`?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Kernel a user space](kernel-and-user-space.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Filesystem hierarchy, inodes a links →](filesystem-hierarchy-inodes-links.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
