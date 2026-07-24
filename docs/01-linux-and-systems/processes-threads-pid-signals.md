# Procesy, thready, PID a signals

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Kernel a user space](kernel-and-user-space.md)
- Súvisiace témy: scheduling, memory, systemd, containers, observability, cgroups

## 1. Program, proces a thread

Program je pasívny executable alebo script uložený na filesystéme. Proces je živý kernelový objekt, ktorý vykonáva program a má vlastný runtime context, identity, resources a lifecycle.

Thread je samostatne schedulovateľný execution flow v rámci procesu. Linux scheduler v skutočnosti plánuje jednotlivé tasky; viac threadov jedného procesu preto môže súčasne bežať na viacerých CPU.

```text
program na disku
→ process image a kernel task
→ jeden alebo viac threadov
→ scheduler ich prideľuje CPU
```

Rozlíšenie je dôležité pri diagnostike. Jeden executable môže mať stovky procesov, jeden proces môže mať stovky threadov a vysoké CPU môže vytvárať iba jeden konkrétny thread.

## 2. Čo tvorí process context

Proces nie je iba PID a názov príkazu. Kernel a user-space runtime spolu udržiavajú viacero typov stavu.

- **Virtual address space** — obsahuje executable mappings, shared libraries, heap, stacks a ďalšie memory regions. Po `execve()` sa väčšina address space nahradí.
- **File-descriptor table** — mapuje malé čísla na otvorené files, sockets, pipes, devices a ďalšie kernelové objekty. Descriptors možno dediť alebo zdieľať.
- **Credentials** — real, effective a saved UID/GID, supplementary groups, capabilities a security labels ovplyvňujú access-control rozhodnutia.
- **Filesystem context** — current working directory, root directory, umask a mount namespace určujú, ako proces interpretuje pathname.
- **Environment a arguments** — vznikajú pri spustení programu a bežne sa dedia do child procesov. Kernel ich nevníma ako globálnu systémovú konfiguráciu.
- **Signal state** — zahŕňa signal dispositions, masks, pending signals a alternate signal stack podľa procesu a threadu.
- **Resource associations** — cgroups, namespaces, scheduler policy, limits a accounting určujú pohľad na systém a dostupné resources.

Nie všetky položky majú rovnaký ownership. Niektoré sú process-wide, iné patria konkrétnemu threadu a ďalšie sú zdieľané podľa flags použitých pri `clone()`.

## 3. PID, TID a process identity

PID je číselný identifikátor task groupu, ktorý používateľ bežne chápe ako proces. Každý thread má vlastný thread ID; hlavný thread má TID rovný PID procesu.

PID je jedinečný iba v konkrétnom PID namespace a iba počas životnosti tasku. Po ukončení ho kernel môže neskôr prideliť inému procesu, preto dlhodobá automatizácia nesmie považovať samotné číslo PID za stabilnú identitu.

Bezpečnejší context zahŕňa PID spolu so start time, executable identity, cgroup, pidfd alebo service-manager ownershipom. Moderné pidfd rozhrania umožňujú odkazovať na konkrétny process object bez race condition spôsobenej opätovným použitím PID.

```bash
ps -eo pid,ppid,lstart,user,stat,comm,args --forest
```

Tento výpis ukazuje hierarchy a start time, ale stále ide o okamžitú snapshot. Medzi získaním PID a následnou operáciou sa proces môže ukončiť alebo zmeniť.

## 4. Parent, child a procesový strom

Proces môže vytvoriť child proces. Kernel eviduje parent-child vzťah, pretože parent typicky potrebuje získať exit status potomka a shell alebo service manager potrebuje riadiť celú skupinu práce.

PPID je PID aktuálneho parenta v danom PID namespace. Parent sa môže zmeniť, ak pôvodný rodič skončí a living child adoptuje PID 1 alebo určený subreaper.

Procesový strom je užitočný, ale nevysvetľuje všetok ownership. Daemon môže double-forknúť, procesy môžu komunikovať bez parent-child vzťahu a systemd riadi služby najmä cez cgroups, nie iba cez jedného potomka.

## 5. Vznik procesu: clone alebo fork

Tradičný Unix model používa `fork()`, ktorý vytvorí child s logickou kópiou process contextu. Linux implementuje podobné mechanizmy cez `clone()` alebo novšie varianty, ktoré umožňujú presne určiť, ktoré resources sa majú zdieľať.

Fyzická pamäť sa pri `fork()` nekopíruje okamžite celá. Parent a child zdieľajú pages označené copy-on-write a samostatná kópia vznikne až pri zápise.

Child dedí napríklad file descriptors, current directory, environment a signal dispositions podľa pravidiel príslušného API. Dedenie neznamená vždy nezávislú kópiu: dva descriptory môžu smerovať na rovnaký open-file description a zdieľať file offset.

## 6. execve nahrádza program, nie proces identity

`execve()` načíta nový executable do existujúceho procesu. PID zostáva rovnaký, ale address space, program code, stack a veľká časť runtime state sa nahradia.

Niektoré attributes prežijú, napríklad vybrané credentials a file descriptors bez `close-on-exec`. Iné sa resetujú alebo prepočítajú podľa executable permissions, set-user-ID bits, capabilities a security policy.

```text
shell child po fork()
→ upraví redirection a descriptors
→ execve("/usr/bin/command", argv, envp)
→ rovnaký PID vykonáva nový program
```

Ak `execve()` uspeje, pôvodný program sa už nevráti. Návrat z `execve()` znamená failure a `errno` vysvetľuje napríklad chýbajúci executable, permission problem alebo invalid format.

## 7. Shell pipeline ako process topology

Pipeline nie je jedna aplikácia. Shell typicky vytvorí pipes, spustí viac child procesov, upraví ich descriptors a následne čaká na ich dokončenie.

```text
producer stdout
→ kernel pipe buffer
→ consumer stdin
```

Ak consumer nečíta dostatočne rýchlo, producer môže blokovať na plnom pipe buffri. Ak consumer skončí, ďalší zápis môže vyvolať `SIGPIPE` alebo `EPIPE`.

Pri diagnostike preto treba sledovať všetky členy pipeline a exit status semantics shellu. Bez `pipefail` môže výsledný status reprezentovať iba posledný príkaz, hoci skorší stage zlyhal.

## 8. Thread a zdieľaný process state

Thready jedného procesu typicky zdieľajú address space, heap, file-descriptor table a process-wide credentials. Vďaka tomu komunikujú cez pamäť bez serializácie medzi procesmi.

Každý thread má vlastný stack, register state, instruction pointer, scheduler state, TID a signal mask. Thread-local storage poskytuje dáta viditeľné iba konkrétnemu threadu, hoci technicky ležia v spoločnom address space.

Zdieľaná pamäť vytvára concurrency risk. Dva thready môžu súčasne čítať a meniť rovnaký object, čo vedie k race condition, lost update, use-after-free alebo nekonzistentnému invariant-u.

## 9. Synchronizácia threadov

Mutex, semaphore, condition variable, read-write lock a atomic operation riešia rozdielne koordinácie. Ich použitie musí chrániť konkrétny invariant, nie iba „pridať lock“ okolo náhodného kódu.

Mnohé user-space locks používajú rýchlu atomickú operáciu bez syscallu, pokiaľ lock nie je contended. Pri contention môžu použiť `futex()`, ktorý umožní thread uspať a neskôr prebudiť cez kernel.

Nesprávna synchronizácia môže vytvoriť deadlock, livelock, starvation alebo priority inversion. Vysoký počet threadov sám o sebe nezaručuje throughput; môže zvýšiť scheduling, stack-memory a lock contention overhead.

## 10. Scheduler states

Kernel task môže byť runnable, executing alebo čakať na udalosť. `ps` zobrazuje zjednodušené state codes, ktoré treba interpretovať v kontexte.

| Stav | Mechanizmus | Diagnostický význam |
|---|---|---|
| `R` | Task práve beží alebo čaká v run queue. | Veľa `R` taskov spolu s CPU saturation môže znamenať CPU contention, ale jeden `R` task je normálny. |
| `S` | Interruptible sleep; task čaká na event, timer, pipe, socket alebo lock a môže reagovať na signal. | Je to bežný stav idle daemonov a neznamená problém bez latency alebo queue dôkazu. |
| `D` | Uninterruptible sleep v kernelovej operácii, často počas I/O alebo niektorých filesystem paths. | Dlhodobé alebo rastúce `D` tasky môžu indikovať storage, NFS, device alebo kernel-lock problém. |
| `T` | Task je zastavený job-control signalom alebo debuggerom. | Over `SIGSTOP`, `SIGTSTP`, ptrace alebo administratívny zásah. |
| `Z` | Task skončil, ale parent ešte neprevzal exit status. | Zombie nevykonáva prácu, no veľké množstvo signalizuje chybné child-reaping správanie. |

Stav je okamžitá hodnota konkrétneho threadu. Proces s mnohými threadmi môže mať súčasne jeden thread v `R`, viacero v `S` a ďalší v `D`.

## 11. Running nie je to isté ako používa CPU

`R` zahŕňa executing aj runnable tasks. Runnable task je pripravený, ale môže čakať v run queue, kým scheduler uvoľní CPU.

Preto vysoký load average alebo veľa `R` taskov neznamená, že každý task spotrebúva celý CPU. Treba skúmať run-queue latency, per-thread CPU time, CPU count a scheduler pressure.

Pri multithreaded procese môže celkový CPU prekročiť 100 % podľa konvencie nástroja, pretože 100 % často reprezentuje jeden logický CPU. Hodnota 400 % môže znamenať približne štyri plne využité CPU.

## 12. Interruptible a uninterruptible sleep

Interruptible sleep umožňuje thread prebudiť udalosťou alebo vybraným signalom. Typickým príkladom je čakanie na socket data, timer alebo condition variable.

Uninterruptible sleep chráni kernelovú operáciu, ktorú nemožno bezpečne prerušiť v ľubovoľnom bode. `SIGKILL` je pending, ale task sa ukončí až po návrate z neinterruptible pathu.

Preto proces v dlhodobom `D` stave nemusí okamžite reagovať ani na `kill -9`. Root cause môže byť nedostupný block device, hung NFS server, driver timeout alebo kernel synchronization problem.

## 13. Exit a exit status

Proces pri normálnom ukončení poskytne exit status. Shell a parent používajú status na rozhodovanie, ale význam nenulových hodnôt definuje konkrétny program alebo konvencia.

```bash
command
status=$?
printf 'status=%s\n' "$status"
```

Status treba uložiť okamžite, pretože ďalší príkaz prepíše `$?`. Pri pipeline treba poznať shell semantics, `PIPESTATUS` alebo `set -o pipefail` podľa požadovaného contractu.

Ak proces ukončí signal, kernel parentovi reportuje signal termination. Shell často zobrazí hodnotu `128 + signal number`, ale ide o shellovú reprezentáciu a nie univerzálny aplikačný exit code.

## 14. wait a reaping child procesu

Keď child skončí, kernel musí dočasne uchovať jeho PID, exit status a resource-usage údaje, aby ich parent mohol prevziať cez `wait()`, `waitpid()` alebo príbuzné API.

Po úspešnom wait kernel process record uvoľní. Ak parent nečaká, child zostane zombie.

Robustný parent musí spracovať viac child exits, race medzi signalom a wait a prípad, keď sa child ukončí skôr, než parent začne čakať. `SIGCHLD` je notification, ale samotné prevzatie statusu vykonáva wait-family syscall.

## 15. Zombie proces

Zombie už nevykonáva inštrukcie, nedrží bežný address space a nespotrebúva CPU. Zostáva iba malý kernelový záznam potrebný pre parenta.

Jeden krátkodobý zombie môže byť normálny počas race medzi child exit a parent wait. Trvalý alebo rastúci počet zombie znamená, že parent nereapuje children alebo je sám zaseknutý.

Zombie nemožno „zabiť“, pretože už skončil. Náprava smeruje na parent process: opraviť reaping logiku, reštartovať parent kontrolovaným spôsobom alebo nechať child adoptovať funkčným reaperom.

## 16. Orphan a subreaper

Orphan je živý proces, ktorému skončil pôvodný parent. Kernel ho priradí PID 1 v danom namespace alebo processu označenému ako subreaper.

Subreaper je dôležitý pre service managers a container init procesy. Umožňuje, aby grandchildren po ukončení intermediate parenta zostali pod kontrolou správcu, ktorý ich neskôr reapne.

V kontajneri môže aplikácia bežať ako PID 1 daného PID namespace. Ak nevykonáva signal forwarding a child reaping, container môže mať problémy so shutdownom a zombie procesmi aj napriek tomu, že na hoste existuje systemd.

## 17. PID 1 má špeciálne správanie

PID 1 je prvý userspace proces daného PID namespace. Okrem adoptovania orphanov má špecifické signal semantics a typicky koordinuje boot, služby a shutdown systému alebo kontajnera.

Na hoste túto rolu často plní systemd. Systemd však nespravuje služby iba cez parent-child tree; pripája procesy do service cgroups a dokáže ukončiť všetky tasky patriace službe.

V kontajneri jednoduchý application process ako PID 1 nemusí mať implementovaný init behavior. Preto sa niekedy používa minimal init wrapper, ktorý forwarduje signaly a reapuje children.

## 18. Signal ako asynchrónna udalosť

Signal je kernelom doručená asynchrónna udalosť pre proces alebo thread. Štandardné signaly prenášajú najmä typ udalosti; real-time signaly navyše podporujú queueing a obmedzený accompanying value.

Signal môže vzniknúť z terminalu, iného procesu, kernel exception, timeru, child state change alebo administratívneho nástroja. Permission na odoslanie signalov závisí od credentials a namespace contextu.

Doručenie nie je totožné s okamžitým vykonaním handlera. Signal môže byť blocked, pending alebo smerovaný konkrétnemu threadu podľa masky a typu udalosti.

## 19. Signal disposition, mask a pending state

Pre väčšinu signalov môže proces nastaviť default action, ignore alebo custom handler. Disposition je prevažne process-wide, zatiaľ čo signal mask je per-thread.

Blocked signal sa nedoručí handleru okamžite; zostane pending, kým ho thread neodblokuje alebo proces neskončí. Štandardné signaly sa bežne nequeueujú ako samostatné opakované položky, takže viac rovnakých udalostí môže splynúť do jedného pending signalu.

Signal handler musí byť navrhnutý opatrne. Väčšina knižničných funkcií nie je async-signal-safe, preto komplexná práca v handleri môže deadlocknúť alebo poškodiť runtime state.

## 20. Dôležité signaly a ich skutočný význam

| Signal | Default alebo typický mechanizmus | Prevádzkový kontext |
|---|---|---|
| `SIGHUP` | Historicky strata controlling terminalu; mnohé daemons ho používajú na reload. | Reload nie je kernelová garancia. Aplikácia musí tento contract explicitne implementovať. |
| `SIGINT` | Interaktívne prerušenie, typicky z `Ctrl+C`. | Program ho môže zachytiť a vykonať cleanup alebo ho interpretovať odlišne od service shutdownu. |
| `SIGTERM` | Defaultne ukončenie, ale dá sa zachytiť alebo ignorovať. | Je štandardnou žiadosťou o graceful termination a má byť prvým krokom pri riadenom stop. |
| `SIGKILL` | Kernel okamžite ukončí task bez user-space handlera. | Nemožno ho blokovať ani zachytiť; cleanup, flush a business compensation sa nevykonajú. |
| `SIGSTOP` | Kernel task zastaví bez možnosti handlera. | Používa sa na job control alebo administratívne zmrazenie, ale môže držať locks a resources. |
| `SIGCONT` | Pokračovanie zastaveného tasku. | Môže súčasne prebudiť task a doručiť handler, ak je definovaný. |
| `SIGCHLD` | Informácia o zmene stavu child procesu. | Parent musí následne použiť wait-family API a reapnúť všetky relevantné children. |
| `SIGSEGV` | Invalid memory access zistený CPU/kernelom. | Handler môže vytvoriť crash evidence, ale pokračovanie programu býva nebezpečné. |
| `SIGPIPE` | Zápis do pipe alebo socketu bez readera. | Defaultne proces ukončí; aplikácia ho často ignoruje a spracuje `EPIPE`. |

Čísla signalov sa môžu medzi architektúrami líšiť. V scripts a dokumentácii je bezpečnejšie používať symbolické názvy.

## 21. Process-directed a thread-directed signal

Niektoré signaly smerujú procesu ako celku a kernel vyberie vhodný thread, ktorý ich môže prijať. Iné vznikajú konkrétnemu threadu, napríklad synchronous fault po invalid memory access.

Multithreaded aplikácie často blokujú vybrané signaly vo worker threadov a vytvoria jeden dedicated signal thread, ktorý ich spracúva cez `sigwait()`. Tento model znižuje riziko vykonávania komplikovanej logiky v asynchronous handleri.

Pri debugging treba preto pozerať per-thread masks a stacks. To, že process má handler, neznamená, že každý thread môže signal práve prijať.

## 22. Graceful shutdown ako lifecycle

Graceful shutdown nie je iba zachytenie `SIGTERM`. Proces musí zastaviť príjem novej práce, dokončiť alebo bezpečne odovzdať in-flight operations, flushnúť alebo commitnúť stav a uzavrieť dependencies v správnom poradí.

```text
SIGTERM alebo service stop
→ mark not-ready a prestaň prijímať novú prácu
→ drain connections alebo queue leases
→ dokonči alebo checkpointni operations
→ flush logs a state
→ ukonči child processes
→ exit s interpretovateľným statusom
```

Shutdown timeout musí zohľadniť najdlhšiu legitímnu operation. Príliš krátky timeout mení každý stop na `SIGKILL`; príliš dlhý môže blokovať rollout alebo recovery.

## 23. Prečo SIGKILL nie je bežný restart mechanizmus

`SIGKILL` dá kernelu príkaz task ukončiť bez návratu do user space. Proces nemôže odstrániť temporary state, release-nuť application locks, dokončiť transakciu ani oznámiť peerom ukončenie.

Kernel síce zavrie file descriptors a uvoľní process memory, ale externé side effects môžu zostať neúplné. Databáza môže vykonať rollback podľa vlastných transakčných pravidiel, no vzdialený systém, message lease alebo partial file protocol nemusí byť automaticky konzistentný.

`SIGKILL` je posledná eskalácia po získaní diagnostických dôkazov a po vyčerpaní primeraného graceful timeoutu.

## 24. Process groups, sessions a terminal job control

Process group zoskupuje procesy pre job control a group signal delivery. Pipeline v interactive shelli typicky tvorí jednu foreground process group.

Session združuje process groups a môže vlastniť controlling terminal. Terminal generuje signaly ako `SIGINT`, `SIGTSTP` alebo `SIGHUP` podľa foreground group a terminal lifecycle.

Daemonization historicky oddeľovala proces od terminalu cez fork, `setsid()` a ďalšie kroky. Pri systemd službách je často vhodnejšie zostať v foreground a nechať service manager spravovať lifecycle, logs a cgroup.

## 25. systemd a cgroup ownership procesu

Pri systemd službe je main PID iba jedna časť modelu. Všetky tasky služby sa nachádzajú v service cgroup a systemd ich môže pozorovať a ukončovať podľa `KillMode`, timeoutov a restart policy.

```bash
systemctl status example.service
systemctl show example.service -p MainPID -p ControlGroup -p KillMode
systemd-cgls
```

Ak daemon double-forkne alebo vytvorí workers, sledovanie iba main PID môže vynechať ďalšie procesy. Cgroup poskytuje stabilnejšiu boundary pre accounting a lifecycle celej služby.

`systemctl stop` používa definovaný service contract. Môže vykonať `ExecStop`, odoslať signal, čakať na timeout a následne eskalovať podľa unit konfigurácie.

## 26. /proc ako kernelový process view

`/proc` je pseudo-filesystem generovaný kernelom. Adresár `/proc/<pid>` reprezentuje aktuálny pohľad na konkrétny process task group.

```bash
cat /proc/<pid>/status
tr '\0' ' ' < /proc/<pid>/cmdline
readlink /proc/<pid>/exe
ls -l /proc/<pid>/fd
cat /proc/<pid>/limits
cat /proc/<pid>/cgroup
cat /proc/<pid>/wchan
```

- **`status`** — sumarizuje identity, memory counters, capabilities, signal masks, thread count a namespace-related údaje. Hodnoty sú snapshot a môžu sa okamžite zmeniť.
- **`cmdline`** — obsahuje argumenty z process startup memory. Proces môže vlastný argv zmeniť a secrets v arguments sú bezpečnostný problém.
- **`exe`** — symlink na executable mapping. Súbor mohol byť po štarte zmazaný alebo nahradený, zatiaľ čo proces stále používa pôvodný inode.
- **`fd`** — ukazuje otvorené descriptors. Potvrdzuje sockets, deleted files a pipes, ktoré proces stále drží.
- **`wchan`** — naznačuje kernel function, v ktorej sleeping task čaká. Je to clue, nie kompletná root cause analýza.

Prístup môže obmedziť UID, ptrace policy, `hidepid`, namespace alebo LSM configuration.

## 27. Open deleted files

Proces môže držať otvorený file descriptor aj po odstránení pathname. Filesystem uvoľní inode a blocks až po zatvorení poslednej referencie.

To vysvetľuje situáciu, keď `du` nevidí veľký log file, ale `df` stále ukazuje plný filesystem. `lsof +L1` môže nájsť deleted files, ktoré proces stále drží.

Správna náprava môže byť reopen logu, graceful restart alebo oprava log rotation contractu. Ručné ukončenie procesu bez pochopenia role môže získať miesto, ale zároveň spôsobiť outage.

## 28. Diagnostické nástroje a čo dokazujú

```bash
ps -eo pid,ppid,tid,stat,psr,pcpu,comm,args --forest
pgrep -a <name>
pstree -ap
ps -L -p <pid>
top -H -p <pid>
lsof -p <pid>
strace -ff -p <pid>
```

- `ps` poskytuje snapshot metadata a CPU accounting, ale krátke tasks môže medzi snapshotmi minúť.
- `pgrep` vyhľadáva process metadata priamo a je spoľahlivejší než `ps | grep`, no názov procesu nemusí byť stabilná service identity.
- `ps -L` a `top -H` odhalia per-thread správanie, napríklad jeden spinning worker v inak idle procese.
- `lsof` mapuje descriptors na files a sockets. Na veľkom systéme môže byť drahý a output treba scope-nuť.
- `strace -ff` ukáže syscalls všetkých threadov alebo children, ale mení timing a nemusí odhaliť user-space lock contention bez syscallov.

Nástroj vyberaj podľa hypotézy, nie podľa zvyku.

## 29. Troubleshooting: služba nereaguje na stop

Keď `systemctl stop` čaká až do timeoutu, najprv zisti, či aplikácia signal prijala a kde trávi shutdown čas.

```text
unit a ControlGroup
→ MainPID a všetky cgroup tasks
→ signal delivery a masks
→ thread states a stacks
→ in-flight I/O, locks alebo child wait
→ timeout a KillMode
→ až potom eskalácia
```

- Over `systemctl status` a `systemctl show`, aby si poznal MainPID, ControlGroup, timeout a stop contract.
- Skontroluj `journalctl -u` pred a po `SIGTERM`, či aplikácia zaznamenala začiatok shutdownu.
- Prezri per-thread states; `D` môže znamenať kernel I/O wait, `S` môže byť čakanie na child alebo condition variable a `R` môže byť busy loop.
- Použi application stack dump, debugger alebo `strace`, ak je to bezpečné a primerané incidentu.
- Zisti, či proces čaká na child, remote dependency, queue lease, filesystem flush alebo lock, ktorý už nikto neuvoľní.

`SIGKILL` použi až po zachytení dôkazov alebo keď používateľský dopad vyžaduje okamžitú mitigáciu. Následne musí vzniknúť remediation pre chybný shutdown lifecycle.

## 30. Troubleshooting: rast zombie procesov

Najprv identifikuj PPID zombie taskov a parent application.

```bash
ps -eo pid,ppid,stat,comm,args | awk '$3 ~ /^Z/'
```

Ak majú zombie spoločného parenta, problém je typicky v jeho wait logic, blocked event loop alebo nesprávnej signal handling implementácii. Reštart parenta môže zombie odstrániť cez adoption a reaping, ale je iba mitigácia.

Pri kontajneri over, kto je PID 1 a či forwarduje signaly a reapuje descendants. Aplikácia navrhnutá ako worker nemusí automaticky plniť init responsibilities.

## 31. Troubleshooting: vysoké CPU jedného procesu

Najprv rozlíš process-wide a per-thread spotrebu. `top -H`, `ps -L` alebo profiler môžu ukázať, či CPU používa jeden thread alebo celý worker pool.

Spinning user-space loop môže mať málo syscallov, zatiaľ čo system-call storm ukáže veľa krátkych kernel transitions. Lock contention môže vytvoriť futex waits a scheduling overhead bez zodpovedajúceho business throughputu.

Korelácia CPU s request rate, queue depth, latency a thread stacks je dôležitejšia než samotné percento. Vysoké CPU pri vysokom užitočnom throughput-e môže byť očakávané; vysoké CPU pri nulovom progress-e je iný failure mode.

## 32. Časté omyly

### Jeden proces používa iba jedno CPU

Proces môže obsahovať mnoho threadov a tie môžu bežať paralelne. Limituje ho počet runnable threadov, scheduler affinity, cgroup quota a workload parallelism, nie samotný PID.

### Fork okamžite skopíruje všetku RAM

Kernel používa copy-on-write a zdieľa pages, kým parent alebo child nezapisuje. Fork však stále môže byť drahý pre veľké page tables a následné copy-on-write faults.

### exec vytvorí nový proces

`execve()` nahrádza program v aktuálnom procese a PID zostáva. Nový proces vzniká samostatným create/clone krokom.

### Zombie stále beží

Zombie už nemá execution context schopný práce. Zostáva iba exit record, ktorý parent ešte neprevzal.

### kill znamená SIGKILL

`kill` je nástroj na posielanie signalov a bez explicitného signal argumentu typicky posiela `SIGTERM`. Názov príkazu neznamená okamžitú deštrukciu procesu.

### SIGKILL vyrieši každý stuck proces okamžite

Task v uninterruptible kernel sleep môže ukončenie odložiť, kým sa kernel operation nevráti. Ak je root cause hung device alebo NFS, problém môže pretrvať.

## 33. Praktický lab

Na testovacom systéme spusti shell pipeline a sleduj jej process topology, descriptors a states.

```bash
sleep 120 | cat >/dev/null &
job_pid=$!
ps -eo pid,ppid,pgid,sid,stat,comm,args --forest
pstree -ap $$
ls -l /proc/$job_pid/fd
kill -TERM "$job_pid"
wait "$job_pid"
printf 'status=%s\n' "$?"
```

Následne vytvor jednoduchý child process a over jeho zombie lifecycle iba v bezpečnom lab prostredí. Cieľom nie je memorovať `ps` flags, ale vysvetliť parent-child vzťah, process group, descriptors, signal a wait behavior.

## 34. Kontrolné otázky

1. Aký je rozdiel medzi executable programom, procesom a threadom?
2. Prečo PID nie je bezpečná dlhodobá identita bez ďalšieho contextu?
3. Ktoré resources môže child po `fork()` zdieľať s parentom?
4. Prečo `execve()` zachová PID, ale nahradí address space?
5. Ako pipeline vytvára viac procesov a kernelové pipes?
6. Ktoré časti stavu sú process-wide a ktoré per-thread?
7. Prečo stav `R` nemusí znamenať, že task práve používa CPU?
8. Prečo task v `D` stave nemusí reagovať okamžite ani na `SIGKILL`?
9. Čo kernel uchováva pri zombie procese a kto ho musí reapnúť?
10. Akú úlohu má PID 1 alebo subreaper?
11. Aký je rozdiel medzi signal disposition, mask a pending state?
12. Prečo `SIGTERM` umožňuje graceful shutdown a `SIGKILL` nie?
13. Prečo systemd používa cgroup boundary namiesto sledovania iba main PID?
14. Ako otvorený deleted file vysvetľuje rozdiel medzi `du` a `df`?
15. Aké dôkazy potrebuješ pred eskaláciou stuck služby na `SIGKILL`?

## 35. Zhrnutie

Proces je kernelom spravovaný runtime context, thread je samostatne schedulovateľný execution flow a PID je dočasný identifikátor v konkrétnom namespace. `fork` alebo `clone` vytvára nový task context, `execve` nahrádza program a `wait` uzatvára child lifecycle prevzatím exit statusu.

Signals poskytujú asynchrónny control a failure mechanism, ale ich účinok závisí od disposition, masky, threadu a aktuálneho kernel state-u. Kvalitná diagnostika spája process tree, cgroup, per-thread states, `/proc`, logs, syscalls a service-manager contract namiesto slepého posielania signalov náhodnému PID.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Kernel a user space](kernel-and-user-space.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Filesystem hierarchy, inodes a links →](filesystem-hierarchy-inodes-links.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
