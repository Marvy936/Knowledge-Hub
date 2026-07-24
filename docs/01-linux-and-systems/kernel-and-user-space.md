# Kernel a user space

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: DevOps Foundations
- Súvisiace témy: procesy, system calls, permissions, namespaces, containers, virtual memory

## 1. Čo oddeľuje kernel space od user space

Linux oddeľuje privilegovaný **kernel space** od obmedzeného **user space**. Kernel vlastní mechanizmy, ktoré musia byť spoločné a dôveryhodné pre celý systém: plánovanie CPU, správu virtuálnej pamäte, prístup k zariadeniam, filesystémom, sieti, procesom a bezpečnostným kontrolám.

Program v user space nemôže priamo prepísať page tables, naprogramovať disk controller ani čítať pamäť iného procesu. Keď takúto službu potrebuje, požiada kernel cez definované rozhranie, najčastejšie pomocou system callu.

```text
user-space program
→ library alebo runtime
→ system call boundary
→ kernel subsystem
→ driver alebo hardware
→ výsledok a errno späť procesu
```

Hranica nie je iba organizačné rozdelenie kódu. Je vynútená procesorom, memory protection a kernelovým access-control modelom.

## 2. Prečo privilege boundary existuje

Ak by každý proces mohol vykonávať privilegované operácie, chyba jednej aplikácie by mohla poškodiť celý systém. Nesprávny pointer by mohol prepísať kernelovú pamäť, chybný program by mohol zmeniť route table alebo prečítať secrets iného používateľa bez kontroly.

Kernel preto centralizuje operácie, ktoré ovplyvňujú spoločný stav systému. Pred vykonaním requestu validuje pointery, veľkosti bufferov, identity, permissions, capabilities, namespaces, mount flags a podľa konfigurácie aj SELinux, AppArmor alebo seccomp pravidlá.

Výsledkom je obmedzený blast radius. Pád bežného procesu zvyčajne ukončí daný proces, zatiaľ čo chyba v kernelovom subsystéme alebo driveri môže poškodiť všetky procesy a celý host.

## 3. Vrstvy Linux systému

Použiteľný Linux systém pozostáva z viacerých vrstiev, ktoré sa pri diagnostike nesmú zamieňať.

```text
Aplikácie, shell, daemons a runtimes
→ libc a ďalšie knižnice
→ system call ABI
→ kernel subsystems
→ device drivers
→ hardware alebo virtualizované zariadenia
```

- **Aplikácia alebo runtime** — implementuje business alebo systémovú logiku a rozhoduje, aké kernelové služby potrebuje. Java JVM, Python interpreter aj shell stále bežia ako user-space procesy.
- **Knižnica** — poskytuje pohodlnejšie API, buffering, alokáciu a portability. Jedna knižničná funkcia môže vykonať nula, jeden alebo viac system callov.
- **System call ABI** — definuje číslo operácie, registre, argumenty a návratovú hodnotu pri prechode do kernelu. Je to stabilnejšia hranica než interné kernelové funkcie.
- **Kernel subsystem** — spracuje request v príslušnej oblasti, napríklad VFS, networking, scheduler alebo virtual memory.
- **Driver** — prekladá všeobecný kernelový request na operácie konkrétneho zariadenia alebo virtuálneho hardware.

Pri probléme je dôležité určiť, v ktorej vrstve vznikol dôkaz. Chyba knižnice, kernelom vrátené `EACCES` a hardware I/O error nie sú rovnaký typ zlyhania.

## 4. CPU privilege levels

Procesory poskytujú režimy s rozdielnymi oprávneniami. Na architektúre x86-64 Linux typicky vykonáva kernel v ring 0 a user-space kód v ring 3; na iných architektúrach existuje ekvivalentné rozdelenie privilegovaných execution levels.

User-space inštrukcie nemôžu priamo vykonať vybrané privilegované operácie. Pokus o nepovolenú inštrukciu alebo prístup k neplatnej adrese vyvolá exception, ktorú prevezme kernel.

Kontrolovaný vstup do kernelu nastáva najmä tromi cestami:

- **System call** — proces zámerne požiada kernel o operáciu, napríklad otvorenie súboru alebo vytvorenie socketu.
- **Hardware interrupt** — zariadenie alebo timer upozorní CPU na udalosť, napríklad dokončenie diskového I/O alebo potrebu scheduler ticku.
- **Exception alebo fault** — CPU zistí stav vyžadujúci kernel, napríklad page fault, delenie nulou alebo neplatnú inštrukciu.

Kernel uloží potrebný execution context, spracuje udalosť a následne môže vrátiť pôvodný proces, naplánovať iný proces alebo ukončiť chybnú operáciu signalom.

## 5. System call nie je bežné volanie funkcie

Bežné volanie funkcie zostáva v rovnakom privilege leveli a používa pravidlá daného programovacieho ABI. System call aktivuje špeciálnu CPU inštrukciu, zmení execution mode a odovzdá kontrolu kernelovému entry pointu.

Kernel nesmie dôverovať argumentom z user space. Pointer môže ukazovať na neplatnú pamäť, buffer sa môže zmeniť počas operácie a číslo file descriptoru nemusí patriť volajúcemu procesu. Preto kernel argumenty validuje a dáta bezpečne kopíruje medzi user a kernel adresným priestorom.

Typické oblasti system callov:

| Oblasť | Príklady | Čo kernel reálne riadi |
|---|---|---|
| Procesy | `clone`, `execve`, `wait4`, `exit` | lifecycle taskov, address space, credentials a návratové stavy |
| Súbory | `openat`, `read`, `write`, `close`, `statx` | pathname lookup, permissions, file offsets a VFS objekty |
| Pamäť | `mmap`, `munmap`, `mprotect`, `brk` | virtuálne mapovania, protection flags a backing storage |
| Sieť | `socket`, `bind`, `connect`, `accept4` | socket state, routing, porty a protocol stack |
| Synchronizácia | `futex`, `epoll_wait`, `poll` | čakanie, wake-up a koordináciu medzi taskmi |
| Čas | `clock_gettime`, `timerfd_create`, `nanosleep` | clocks, timers a blokovanie tasku |

Návratová hodnota často rozlišuje úspech od chyby a knižnica nastaví `errno`. `errno` nie je ľubovoľná aplikačná správa; reprezentuje konkrétnu triedu zlyhania na rozhraní s kernelom.

## 6. Knižničná funkcia, runtime a syscall

Programy zvyčajne nevolajú system calls priamo. Používajú libc, jazykový runtime alebo framework, ktorý vytvorí vhodný request a spracuje návratovú hodnotu.

`printf()` napríklad typicky zapisuje do user-space bufferu a `write()` môže zavolať až pri flushi. `malloc()` môže uspokojiť malú alokáciu z už prideleného heapu bez nového system callu; pri potrebe ďalšej pamäte môže použiť `brk()` alebo `mmap()`.

To je dôležité pri profilovaní. Veľký počet volaní aplikačnej funkcie nemusí znamenať rovnaký počet prechodov do kernelu a naopak jeden framework call môže vykonať mnoho syscallov.

## 7. Scheduling a execution context

Kernel scheduler rozhoduje, ktorý runnable task dostane CPU. Proces nie je „spustený stále“; strieda obdobia vykonávania, čakania na I/O, spánku, preemption a opätovného naplánovania.

Pri context switchi kernel uloží execution state jedného tasku a obnoví stav ďalšieho. Context switch má cenu, pretože mení CPU registre, scheduler state a nepriamo môže zhoršiť cache a TLB locality.

Prechod user/kernel a context switch nie sú synonymá. System call môže byť spracovaný a vrátiť sa do rovnakého procesu bez prepnutia na iný task, zatiaľ čo scheduler môže prepnúť medzi procesmi po timer interrupte alebo pri blokovaní na I/O.

## 8. Virtual memory a address space

Každý proces pracuje s vlastným virtuálnym adresným priestorom. Virtuálna adresa nie je priamo fyzická RAM adresa; MMU ju podľa page tables prekladá na fyzickú page, file-backed mapping alebo stav, ktorý vyvolá page fault.

Virtual memory poskytuje viacero mechanizmov:

- **Process isolation** — rovnaká virtuálna adresa v dvoch procesoch môže smerovať na odlišnú fyzickú pamäť, takže procesy si navzájom nevidia obsah bez explicitného zdieľania.
- **Memory protection** — page môže byť read-only, executable alebo neprístupná. CPU pri porušení flags vyvolá fault namiesto tichého prepísania cudzieho stavu.
- **Demand paging** — mapovanie môže existovať skôr než fyzická page. Kernel ju pridelí alebo načíta až pri prvom prístupe.
- **Copy-on-write** — po `fork()` môžu parent a child zdieľať pages, kým jeden z nich nezačne zapisovať. Až potom kernel vytvorí súkromnú kópiu.
- **File mappings a shared memory** — súbor alebo anonymous memory možno mapovať do address space a zdieľať medzi procesmi podľa zvolených flags.

Segmentation fault znamená, že proces vykonal neprípustný memory access a kernel mu doručil signal, typicky `SIGSEGV`. Samotná správa ešte neurčuje, či príčinou bol null pointer, use-after-free, stack overflow alebo nepovolený access do mapovanej oblasti.

## 9. Page fault nie je automaticky chyba

Page fault je exception, pri ktorej CPU nevie okamžite dokončiť memory access podľa aktuálnych page tables. Mnoho page faultov je očakávaných a kernel ich vyrieši bez ukončenia procesu.

- **Minor fault** — požadovaná page je už v pamäti alebo sa dá namapovať bez diskového I/O. Môže ísť napríklad o copy-on-write page.
- **Major fault** — kernel musí načítať dáta zo storage, čo môže výrazne zvýšiť latency.
- **Invalid fault** — mapping alebo permissions request nepovoľujú. Kernel zvyčajne doručí `SIGSEGV` alebo `SIGBUS`.

Pri troubleshooting preto nestačí vidieť vysoký počet page faultov. Treba rozlíšiť ich typ, latency a súvislosť s memory pressure alebo file I/O.

## 10. VFS, filesystems a file descriptors

Aplikácia pri `openat()` nežiada konkrétny ext4 driver priamo. Request prechádza cez Virtual File System, ktorý poskytuje spoločný model pre pathname, inode, file object, permissions a operácie rôznych filesystémov.

Po úspešnom otvorení kernel vytvorí alebo zdieľa open-file description a procesu vráti malé číslo — file descriptor. Descriptor je index v tabuľke procesu, nie názov súboru ani globálny identifikátor.

Pri `read(fd, ...)` kernel používa descriptor na nájdenie file objectu, offsetu a operácií príslušného filesystemu alebo socketu. Rovnaký abstraktný model preto funguje pre regular files, pipes, sockets, devices aj pseudo-filesystems ako `/proc`.

## 11. Devices a kernel drivers

Device driver beží v kernel context-e a implementuje komunikáciu s konkrétnym zariadením alebo virtuálnym device modelom. Driver môže obsluhovať interrupts, DMA, queues a error recovery, pričom zvyšku kernelu poskytuje štandardizované rozhranie.

Chyba drivera má vysoký dopad, pretože driver má kernelové oprávnenia. Môže spôsobiť kernel panic, memory corruption, deadlock alebo stratu I/O na celom hoste.

Device files v `/dev` nie sú samotné zariadenia. Sú to filesystem objekty, cez ktoré proces otvorí kernelové device rozhranie; permissions a cgroup device policy môžu obmedziť, kto ich smie používať.

## 12. Kernel modules

Kernel module je načítateľná časť kernelového kódu. Umožňuje pridať driver, filesystem alebo inú funkcionalitu bez zostavenia všetkého priamo do hlavného kernel image.

Modul stále beží v kernel space a musí presne zodpovedať kernelovým rozhraniam a bezpečnostným požiadavkám. Podpisovanie modulov a Secure Boot môžu obmedziť načítanie nedôveryhodného kódu.

Užitočné pozorovania:

```bash
uname -a
lsmod
modinfo <module>
dmesg --level=err,warn
```

- `uname -a` ukazuje bežiacu kernel release a základné systémové údaje. Nepotvrdzuje však, že všetky user-space balíky zodpovedajú rovnakej verzii distribúcie.
- `lsmod` zobrazuje aktuálne načítané moduly a referencie. Modul môže byť použitý nepriamo iným modulom alebo zariadením.
- `modinfo` číta metadata modulu, napríklad aliasy, parametre a podpis. Nehovorí, že modul je práve načítaný.
- `dmesg` číta kernel ring buffer, kde sa objavujú boot, driver, OOM a ďalšie kernelové udalosti. Prístup môže byť bezpečnostnou politikou obmedzený.

## 13. Kernel log a user-space log nie sú to isté

Kernel zapisuje udalosti do vlastného ring bufferu. User-space daemons a aplikácie môžu zapisovať do journald, syslog socketu, súborov alebo externého telemetry backendu.

Journald často ingestuje aj kernel messages, takže rovnaká udalosť môže byť dostupná cez `dmesg` aj `journalctl -k`. Rozdiel je v storage, metadata, retention a access policy, nie nevyhnutne v pôvode samotnej správy.

Pri boot alebo driver incidente treba vedieť, či dôkaz vznikol v kernel space, v initramfs alebo až v user-space službe. Nesprávne zvolený log source môže skryť najskoršiu príčinu zlyhania.

## 14. Bezpečnostné rozhodnutie pri system calle

Kernel pri requeste nekontroluje iba tradičné Unix mode bits. Finálne rozhodnutie môže prechádzať viacerými vrstvami podľa typu operácie.

```text
process credentials a namespaces
→ discretionary access control a ACL
→ Linux capabilities
→ mount a filesystem flags
→ seccomp filter
→ SELinux alebo AppArmor policy
→ service-specific kernel checks
→ allow alebo errno
```

- **Credentials a namespaces** určujú, aké UID/GID a resource view kernel pre proces používa. Root v user namespace nemusí mať rovnakú moc ako host root.
- **DAC a ACL** vyhodnocujú owner, group, mode bits a rozšírené access-control entries na pathname a inode objektoch.
- **Capabilities** rozdeľujú časť tradičných root práv na menšie privilege units, napríklad bind na nízky port alebo network administration.
- **Seccomp** môže blokovať konkrétne system calls alebo ich argumenty bez ohľadu na filesystem permissions.
- **SELinux/AppArmor** pridávajú mandatory policy, ktorá môže request zamietnuť aj vtedy, keď ho DAC povoľuje.

Preto `Permission denied` neznamená automaticky zlé mode bits. Treba určiť, ktorá vrstva request zamietla.

## 15. User space nie je jedna úroveň dôvery

Všetky bežné procesy síce bežia mimo kernel space, ale nemajú rovnaké oprávnenia ani rovnaký pohľad na systém. Kernel medzi nimi vytvára ďalšie boundaries.

- **Proces a address space** — každý proces má samostatnú memory map a file-descriptor table, pokiaľ explicitne nezdieľa vybrané objekty.
- **Unix identity** — effective UID, GID a supplementary groups ovplyvňujú DAC rozhodnutia a vlastníctvo vytvorených objektov.
- **Capabilities** — proces môže dostať konkrétnu privilegovanú schopnosť bez plného root scope-u.
- **Namespaces** — proces môže vidieť iné PIDy, mounty, interfaces, hostname alebo UID mapovanie než host.
- **cgroups** — riadia resource accounting a limits, ale samy osebe nevytvárajú bezpečnostnú izoláciu pohľadu.
- **LSM a seccomp** — obmedzujú povolené objekty a system-call surface podľa policy.

Root proces v user space stále nie je kernel. Má však veľmi široké práva na volanie kernelových rozhraní, takže compromise root procesu zostáva závažný.

## 16. Kontajner a kernel boundary

Bežný Linux kontajner nemá vlastný kernel. Kontajnerové procesy používajú kernel hosta a izolovaný pohľad získavajú cez namespaces, cgroups, capabilities, LSM a filesystem layers.

To má dve dôležité implikácie. Kernel vulnerability môže prekročiť kontajnerovú boundary a konfigurácia host kernelu určuje dostupné features aj všetkým kontajnerom. Zároveň proces v kontajneri môže vidieť inú PID, network alebo mount topológiu než administrátor na hoste, hoci obe perspektívy opisujú rovnaké kernelové objekty.

Virtuálny stroj naopak typicky spúšťa vlastný guest kernel nad virtualizovaným hardware rozhraním. Kontajner a VM preto poskytujú odlišnú isolation boundary a odlišný patch lifecycle.

## 17. Pozorovanie system-call boundary cez strace

`strace` používa tracing mechanizmy kernelu na zachytenie system callov, výsledkov a signalov procesu. Je vhodný vtedy, keď aplikácia hlási všeobecnú chybu, ale potrebujeme poznať presnú kernelovú operáciu.

```bash
strace -f -tt -o trace.log -- command arg1
```

- `-f` sleduje aj vytvorené child procesy alebo thready, takže nestratíš request vykonaný mimo pôvodného PID.
- `-tt` pridá časové údaje a pomáha nájsť dlhé blokovanie alebo timeout sekvenciu.
- `-o` oddelí trace od normálneho stdout/stderr programu a uľahčí ďalšiu analýzu.

Príklad:

```text
openat(AT_FDCWD, "/etc/app.conf", O_RDONLY) = -1 ENOENT
```

Tento riadok hovorí, že proces požiadal kernel o pathname lookup a kernel objekt nenašiel. Nehovorí, prečo aplikácia zvolila danú cestu ani či mala vytvoriť fallback; to už patrí do aplikačnej logiky.

## 18. Cena a limity tracingu

Tracing mení timing a môže vytvoriť veľké množstvo dát. Pri latency-sensitive alebo vysoko paralelnom procese preto sleduj iba potrebný scope, obmedz konkrétne syscalls alebo použi výkonnejšie mechanizmy ako eBPF podľa rizika a cieľa.

`strace` tiež neukazuje všetku internú prácu kernelu. Vidí boundary request a výsledok, ale nie vždy scheduler decisions, network packet path, filesystem cache behavior alebo driver internals.

Pri diagnostike ho preto kombinuj s `journalctl`, `/proc`, `ss`, `perf`, pressure stall information a service-specific telemetry namiesto predstavy, že jeden nástroj vysvetlí celý systém.

## 19. End-to-end príklad: čítanie súboru

Príkaz `cat /etc/hostname` vyzerá jednoducho, ale prechádza viacerými vrstvami.

```text
shell vytvorí proces
→ dynamic loader a libc pripravia program
→ cat zavolá openat()
→ kernel vykoná pathname lookup cez VFS
→ DAC/ACL/LSM overia prístup
→ filesystem nájde inode a file data
→ read() prenesie bytes do user bufferu
→ write() ich odošle na stdout descriptor
```

Dáta môžu byť už v page cache, takže disk sa vôbec nemusí čítať. Ak nie sú, filesystem a block layer vytvoria I/O request, driver ho odošle zariadeniu a proces môže počas čakania prejsť do sleep state-u.

Tento model pomáha pri troubleshooting. `ENOENT`, `EACCES`, dlhý disk wait a blokovanie na pipe sú odlišné body toho istého toku a vyžadujú odlišné dôkazy.

## 20. Troubleshooting: Permission denied pri otvorení súboru

Pri chybe `Permission denied` nezačínaj zmenou oprávnení. Najprv identifikuj request, identity a vrstvu, ktorá ho zamietla.

```text
aplikácia a presný pathname
→ syscall a errno
→ effective UID/GID/capabilities
→ parent-directory traversal
→ inode mode bits a ACL
→ mount flags a read-only state
→ SELinux/AppArmor audit
→ namespace a container context
```

- **Syscall a pathname** — `strace` potvrdí, či zlyhal `openat`, `connect`, `execve` alebo iná operácia. Rovnaký text chyby môže mať odlišný kernelový request.
- **Effective credentials** — over proces cez `/proc/<pid>/status`, `ps` alebo service manager. Interaktívny shell a daemon môžu bežať pod inou identitou.
- **Directory traversal** — proces potrebuje execute permission na každom parent adresári. Správne permissions cieľového súboru nestačia, ak nevie prejsť cestou.
- **ACL a LSM** — `getfacl`, audit log a SELinux/AppArmor nástroje odhalia policy, ktorú obyčajný `ls -l` nezobrazuje.
- **Mount a namespace** — cesta môže byť read-only, `noexec`, prekrytá bind mountom alebo odlišná v kontajneri.

`chmod 777` maskuje mechanizmus a rozširuje access scope bez dôkazu, že problém bol v mode bits. Kvalitná náprava mení iba vrstvu, ktorá request skutočne blokovala.

## 21. Troubleshooting: vysoký system CPU

Vysoký system CPU znamená, že CPU trávi významný čas vykonávaním kernelového kódu v mene procesov alebo interrupt handlingu. Samotná hodnota však neurčuje príčinu.

Možné mechanizmy zahŕňajú veľký počet system callov, packet processing, context switching, filesystem alebo block-layer prácu, lock contention a driver aktivitu. Diagnostika má korelovať `top` alebo `pidstat` s `strace -c`, `perf`, interrupt counters a workload throughputom.

Ak sa system CPU zvýšil spolu s dramatickým rastom krátkych network connections, optimalizácia aplikačného algoritmu nemusí pomôcť. Príčinou môže byť connection churn, firewall traversal alebo príliš malé I/O batches.

## 22. Časté omyly

### Kernel je celý operačný systém

Kernel je privilegované jadro, ale funkčný Linux systém potrebuje init, knižnice, utilities, shell, package management a ďalší user-space software. Distribúcia môže meniť väčšinu user-space vrstvy bez zásadnej zmeny kernelového modelu.

### System call je obyčajná funkcia

Syntax môže vyzerať podobne, ale system call prekračuje privilege boundary a kernel musí všetky vstupy považovať za nedôveryhodné. Cena a failure semantics sa preto od bežného function callu líšia.

### Každý page fault znamená nedostatok RAM

Minor page faults sú bežnou súčasťou demand paging a copy-on-write. Až kombinácia major faults, I/O latency, reclaimu a memory pressure poskytuje dôkaz o probléme.

### Root proces je kernel

Root je user-space identity s rozsiahlymi právami na kernelové API. Stále však podlieha CPU mode boundary a podľa konfigurácie aj namespaces, capabilities, seccomp a LSM policy.

### Kontajner má vlastný kernel

Štandardný kontajner zdieľa host kernel. Odlišný hostname, PID 1 alebo network interface sú namespace views, nie dôkaz samostatného kernelu.

## 23. Praktické overenie

Na testovacom Linux systéme vykonaj nasledujúci tok a pri každom kroku vysvetli, ktorú vrstvu pozoruješ.

```bash
uname -r
cat /proc/self/status
strace -e trace=openat,read,write,close cat /etc/hostname
cat /proc/self/maps | head
journalctl -k -b --no-pager | tail
```

`uname` číta identitu bežiaceho kernelu, `/proc` vystavuje kernelový pohľad na proces a jeho mappings, `strace` sleduje boundary requesty a `journalctl -k` zobrazuje kernel-originated udalosti aktuálneho bootu. Lab nemá byť iba spustenie príkazov; výsledkom má byť vysvetlenie, ako sa jednotlivé dôkazy prepájajú.

## 24. Kontrolné otázky

1. Prečo CPU privilege levels obmedzujú dopad chyby bežnej aplikácie?
2. Aký je rozdiel medzi system callom, interruptom a exception?
3. Prečo `printf()` nemusí pri každom volaní vykonať `write()`?
4. Aký je rozdiel medzi prechodom do kernelu a context switchom?
5. Prečo je minor page fault často normálny a major fault môže byť drahý?
6. Čo reprezentuje file descriptor a prečo nie je totožný s pathname?
7. Prečo chyba kernel modulu môže ovplyvniť celý host?
8. Ktoré vrstvy môžu zamietnuť otvorenie súboru aj pri správnych mode bits?
9. Prečo kontajner zdieľa kernel hosta, hoci vidí iné PIDy a mounty?
10. Aké hranice má `strace` a kedy potrebuješ ďalší nástroj?
11. Ako by si rozlíšil aplikačný error od kernelom vráteného `errno`?
12. Prečo vysoký system CPU neznamená automaticky chybu kernelu?

## 25. Zhrnutie

Kernel space je privilegovaná vrstva, ktorá arbitruje spoločné resources a presadzuje systémové boundaries. User-space procesy používajú knižnice a system calls, pričom kernel validuje request podľa identity, pamäte, namespace, filesystem a bezpečnostnej policy.

Pri diagnostike treba sledovať celý tok od aplikačného zámeru cez syscall a kernel subsystem až po device alebo runtime výsledok. Príkaz má hodnotu iba vtedy, keď je jasné, ktorú vrstvu pozoruje a akú hypotézu jeho výstup overuje.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: DevOps anti-patterns](../00-foundations/devops-anti-patterns.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Procesy, thready, PID a signals →](processes-threads-pid-signals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
