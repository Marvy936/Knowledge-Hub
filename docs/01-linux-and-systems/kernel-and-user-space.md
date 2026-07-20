# Kernel a user space

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: DevOps Foundations
- Súvisiace témy: procesy, system calls, permissions, namespaces, containers

## 1. Definícia

Linux oddeľuje privilegovaný **kernel space** od obmedzeného **user space**. Kernel riadi CPU, pamäť, zariadenia, procesy, filesystémy a sieť; používateľské programy požiadajú kernel o službu cez presne definované rozhranie system calls.

## 2. Prečo hranica existuje

Keby každý program mohol priamo meniť page tables, čítať ľubovoľnú fyzickú pamäť alebo ovládať disk, chyba jednej aplikácie by mohla poškodiť celý systém. Privilege boundary obmedzuje dopad zlyhania a umožňuje kernelu centrálne presadzovať izoláciu, scheduling a access control.

## 3. Mentálny model

```text
User space
├── shell
├── systemd a daemons
├── aplikácie
└── knižnice, napr. glibc
        │
        │ system call boundary
        ▼
Kernel space
├── scheduler
├── virtual memory
├── VFS a filesystems
├── network stack
└── device drivers
        │
        ▼
Hardware
```

Aplikácia typicky nekomunikuje s hardvérom priamo. Napríklad `cat file.txt` zavolá knižničné funkcie, tie použijú system calls ako `openat`, `read` a `write`, kernel overí oprávnenia a prenesie dáta.

## 4. CPU privilege levels

Procesor podporuje režimy s rozdielnymi oprávneniami. Na bežných architektúrach Linux vykonáva kernel v privilegovanom režime a aplikácie v neprivilegovanom režime.

Prechod do kernelu nastáva riadeným spôsobom:

- system call,
- hardware interrupt,
- exception alebo fault.

Po spracovaní kernel obnoví kontext procesu a vráti vykonávanie do user space.

## 5. System calls

System call je vstupný bod do kernelu. Medzi základné patria:

| Oblasť | Príklady |
|---|---|
| Procesy | `clone`, `execve`, `wait4`, `exit` |
| Súbory | `openat`, `read`, `write`, `close`, `stat` |
| Pamäť | `mmap`, `munmap`, `brk` |
| Sieť | `socket`, `bind`, `connect`, `accept` |
| Čas a čakanie | `clock_gettime`, `nanosleep`, `futex` |

Knižničná funkcia a system call nie sú automaticky to isté. Napríklad `printf()` je funkcia štandardnej C knižnice; bufferuje dáta a až neskôr môže zavolať `write()`.

## 6. Virtual memory

Každý proces vidí vlastný virtuálny adresný priestor. Kernel a MMU mapujú virtuálne adresy na fyzickú pamäť alebo iné backing storage.

To umožňuje:

- izoláciu procesov,
- zdieľané knižnice,
- memory-mapped files,
- copy-on-write,
- paging a riadenie memory pressure.

Segmentation fault typicky znamená, že proces pristúpil k virtuálnej adrese, pre ktorú nemá platné mapovanie alebo oprávnenie.

## 7. Kernel modules a drivers

Časť kernelovej funkcionality môže byť načítaná ako modul. Modul stále beží v kernel space; chyba v ňom preto môže poškodiť celý systém.

Užitočné príkazy:

```bash
uname -a
lsmod
modinfo <module>
dmesg --level=err,warn
```

`dmesg` číta kernel ring buffer. Prístup môže byť obmedzený bezpečnostnou politikou systému.

## 8. Pozorovanie hranice

```bash
strace -f -o trace.log -- command arg1
```

`strace` sleduje system calls a signals procesu. Pomáha odpovedať napríklad:

- ktorý súbor sa program pokúsil otvoriť,
- aké oprávnenie zlyhalo,
- na ktorom socket connect čaká,
- ktorý syscall vrátil konkrétny `errno`.

Príklad:

```text
openat(AT_FDCWD, "/etc/app.conf", O_RDONLY) = -1 ENOENT
```

Toto neznamená „aplikácia je pokazená“. Presne to znamená, že kernel pre dané pathname nenašiel objekt a vrátil `ENOENT`.

## 9. User space nie je jedna úroveň dôvery

Aj v user space existujú ďalšie hranice:

- samostatné procesy a virtuálne adresné priestory,
- Unix users a groups,
- Linux capabilities,
- namespaces a cgroups,
- seccomp,
- SELinux alebo AppArmor,
- kontajnerové a virtuálne prostredia.

Root proces v user space má rozsiahle oprávnenia, ale stále používa kernelové rozhrania. Nie je totožný s kernelom.

## 10. Časté omyly

### „Kernel je operačný systém a všetko ostatné je aplikácia“

Kernel je jadro operačného systému, ale použiteľný Linux systém zahŕňa aj init systém, knižnice, shell, utilities a ďalší user-space software.

### „System call je obyčajné volanie funkcie“

Z pohľadu programu môže vyzerať podobne, ale zahŕňa kontrolovaný prechod privilege boundary a validáciu vstupov kernelom.

### „Kontajner má vlastný kernel“

Bežný Linux kontajner zdieľa kernel hosta. Izoláciu vytvárajú najmä namespaces, cgroups, capabilities a ďalšie kernelové mechanizmy.

## 11. Troubleshooting scenár

Aplikácia hlási `Permission denied` pri otvorení súboru.

Postup uvažovania:

1. Použi `strace` a identifikuj syscall a pathname.
2. Over UID/GID procesu.
3. Skontroluj directory traversal permissions na každom parent adresári.
4. Skontroluj mode bits, ACL, mount flags a LSM policy.
5. Až potom men oprávnenia.

Chybou je začať príkazom `chmod 777`; tým sa maskuje mechanizmus a zväčšuje bezpečnostný problém.

## 12. Kontrolné otázky

1. Prečo aplikácia nemôže priamo meniť page tables?
2. Aký je rozdiel medzi knižničnou funkciou a system callom?
3. Čo sa deje pri prechode z user space do kernel space?
4. Prečo môže byť chyba kernel modulu závažnejšia než chyba bežného procesu?
5. Ako `strace` pomáha odlíšiť aplikačný problém od kernelom vráteného erroru?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: DevOps anti-patterns](../00-foundations/devops-anti-patterns.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Procesy, thready, PID a signals →](processes-threads-pid-signals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
