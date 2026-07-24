# Filesystem hierarchy, inodes a links

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Kernel a user space](kernel-and-user-space.md), [Procesy, thready, PID a signals](processes-threads-pid-signals.md)
- Súvisiace témy: permissions, storage, mounts, containers, backups, file descriptors

## 1. Filesystem nie je iba strom názvov

Linux prezentuje súbory, adresáre, zariadenia a viacero virtuálnych kernelových rozhraní cez jeden pathname strom začínajúci v `/`. Tento strom však nie je jeden fyzický disk. Je to zložený namespace, do ktorého sa na rôznych mount pointoch pripájajú lokálne filesystémy, network filesystems, pseudo-filesystems, bind mounts a kontajnerové vrstvy.

```text
pathname
→ lookup jednotlivých komponentov
→ mount namespace a mount point
→ directory entry
→ inode
→ open file description
→ filesystem implementation alebo kernel object
```

Pathname teda nie je samotný súbor. Je to požiadavka na vyhľadanie objektu v konkrétnom mount namespace procesu. Rovnaká cesta môže v inom kontajneri alebo mount namespace ukazovať na iný objekt.

## 2. Jeden koreň, viac filesystemov

Každý proces vidí koreňovú cestu `/`, ale objekty pod ňou môžu pochádzať z rôznych zdrojov. Root filesystem poskytuje počiatočný strom a ďalšie filesystémy sa pripájajú na konkrétne adresáre.

```text
/
├── etc        → root filesystem
├── home       → samostatný disk alebo volume
├── proc       → procfs generovaný kernelom
├── sys        → sysfs pohľad na kernel objects
├── run        → tmpfs runtime state
├── var/lib    → samostatný persistent filesystem
└── mnt/data   → network alebo block filesystem
```

Keď sa filesystem pripojí na `/var/lib`, pôvodný obsah adresára pod mount pointom sa nevymaže. Je prekrytý novým mountom a z bežného pathname lookupu zostáva neviditeľný, kým sa mount neodpojí alebo sa k pôvodnému stromu nepristúpi iným namespace mechanizmom.

## 3. Filesystem Hierarchy Standard ako prevádzkový kontrakt

Filesystem Hierarchy Standard a distribučné konvencie dávajú adresárom očakávanú úlohu. Nie je to iba estetické triedenie. Umiestnenie určuje, čo má byť zálohované, čo môže byť read-only, čo sa môže po reštarte stratiť a ktorú časť má spravovať package manager alebo aplikácia.

- **`/etc` — host-specific konfigurácia.** Súbory tu typicky opisujú požadované alebo lokálne nastavenie systému. Nemajú obsahovať veľké runtime dáta; pri obnove hosta sú často súčasťou konfiguračného alebo backup kontraktu.
- **`/usr` — distribuovaný software a read-mostly dáta.** Binárky, knižnice a zdieľané resources spravuje najmä package manager alebo image build. Ručná úprava súboru pod `/usr` môže byť pri ďalšom upgrade prepísaná.
- **`/var` — dáta, ktoré sa počas prevádzky menia.** Logy, spooly, cache, databázy a aplikačný state môžu mať odlišnú retention, quota a backup politiku. Plný `/var` môže zastaviť logging, package management aj databázu, hoci root filesystem inde má voľné miesto.
- **`/run` — runtime state aktuálneho bootu.** PID files, Unix sockets a krátkodobé state sú často na `tmpfs`, takže po reštarte zmiznú. Služba nemá považovať súbor v `/run` za durable databázu.
- **`/tmp` — dočasné zdieľané dáta.** Čistenie a lifetime závisia od distribúcie a systemd-tmpfiles politiky. Bezpečná aplikácia musí počítať s race conditions, sticky bitom a možnosťou odstránenia starých položiek.
- **`/home` a `/root` — používateľský state.** `/root` je samostatný domovský adresár administrátora, aby nebol závislý od dostupnosti bežného `/home` mountu.
- **`/dev`, `/proc` a `/sys` — kernelové rozhrania.** Tieto cesty nepredstavujú bežné persistentné súbory. Obsah vzniká dynamicky podľa zariadení, procesov a kernelového stavu.

Moderné distribúcie môžu používať merged `/usr`, kde sú `/bin`, `/sbin` alebo `/lib` symlinky do `/usr`. Pri diagnostike preto treba pozorovať reálny layout cez `readlink`, `findmnt` a package metadata, nie predpokladať historické fyzické rozdelenie.

## 4. Pathname lookup

Pri otvorení `/var/log/app.log` kernel neskočí priamo na jeden globálny záznam. VFS vykonáva lookup po komponentoch cesty a pri každom kroku rešpektuje mounty, symlinky, permissions a namespace procesu.

```text
/
→ nájdi entry var
→ over search permission na /
→ vstúp do inode adresára var
→ nájdi entry log
→ prípadne prekroč mount point
→ nájdi entry app.log
→ over operáciu na cieľovom inode
```

Execute bit na adresári znamená **search/traversal permission**. Používateľ môže poznať presný názov súboru a mať read permission na súbore, ale bez `x` na niektorom parent adresári sa k nemu nedostane. Read bit na adresári naopak povoľuje čítať zoznam mien; s `x` bez `r` možno pristúpiť k známemu menu, ale nie pohodlne listovať obsah.

`namei -l /var/log/app.log` je preto pri permission probléme často užitočnejší než samotné `ls -l app.log`: ukáže každý komponent cesty, vlastníka a mode bits.

## 5. Dentry a inode

Directory entry, často označovaná ako dentry, spája meno v konkrétnom adresári s inode objektom. Inode reprezentuje filesystémový objekt a nesie jeho metadata, nie bežný filename.

```text
adresár inode 200
├── "app.log"  → inode 12345
└── "latest"   → inode 12345

inode 12345
├── type: regular file
├── owner UID/GID
├── mode, ACL a xattrs
├── size a timestamps
├── link count: 2
└── extents alebo block mapping
```

Inode number je identifikátor iba v rámci konkrétneho filesystému. Dvojica `device/filesystem identity + inode number` je presnejšia než samotné číslo inode. Po odstránení objektu môže byť inode number neskôr znovu použitý, preto nie je večnou globálnou identitou.

## 6. Čo inode obsahuje a čo nie

Inode typicky uchováva typ objektu, UID, GID, mode bits, ACL alebo extended attributes, timestamps, size, link count a mapovanie na dátové extents. Konkrétna implementácia sa líši podľa ext4, XFS, Btrfs alebo iného filesystému, ale mentálny model zostáva podobný.

Filename sa nachádza v parent directory entry. Preto rename v rámci rovnakého filesystému často nemení inode ani dátové bloky; zmení sa mapovanie mena. Presun cez hranicu filesystemu však typicky vyžaduje kopírovanie nového objektu a odstránenie pôvodného, pretože inode nemôže patriť dvom filesystémom.

## 7. Otvorenie súboru a file descriptor

Keď proces úspešne vykoná `openat()`, kernel vytvorí alebo použije open file description a procesu vráti malé číslo file descriptoru. File descriptor nie je pathname ani inode. Je to per-process referencia na otvorený objekt a jeho runtime stav, napríklad current offset a open flags.

```text
proces fd 3
→ open file description
   ├── current offset
   ├── O_APPEND / O_RDONLY / ďalšie flags
   └── inode 12345
```

Po otvorení môže byť pathname premenovaný alebo odstránený a file descriptor stále ukazuje na pôvodný inode. To vysvetľuje, prečo proces môže pokračovať v čítaní alebo zapisovaní do súboru, ktorý už nie je viditeľný pod pôvodným menom.

## 8. Hard link

Hard link je ďalšia directory entry smerujúca na ten istý inode. Neexistuje primárne meno a sekundárny alias; všetky hard links sú z pohľadu inode rovnocenné názvy.

```bash
ln source.txt second-name.txt
ls -li source.txt second-name.txt
stat source.txt
```

- **Obsah je spoločný, pretože inode je spoločný.** Zápis cez jeden názov mení dáta viditeľné cez druhý názov.
- **Link count sleduje počet directory entries.** `unlink()` jedného mena zníži count, ale objekt nezanikne, kým existuje ďalší hard link alebo otvorená referencia.
- **Hard link bežne neprekročí filesystem boundary.** Directory entry môže odkazovať iba na inode patriaci tomu istému filesystému; druhý mount má vlastný inode namespace.
- **Hard links na adresáre sú obmedzené.** Voľné vytváranie cyklov by narušilo stromový model, rekurzívne nástroje a garbage-collection predpoklady filesystému.

Hard link nie je vhodný ako všeobecný deployment pointer medzi release adresármi na rôznych volumes. Na tento účel sa častejšie používa symlink alebo atomický rename.

## 9. Symbolic link

Symbolic link je samostatný inode, ktorého obsahom je textová cieľová pathname. Pri lookup-e kernel alebo aplikácia načíta tento text a pokračuje v rozlišovaní cesty.

```bash
ln -s /opt/app/releases/42 /opt/app/current
readlink /opt/app/current
readlink -f /opt/app/current
```

- **Môže prekročiť filesystem boundary.** Obsahuje pathname, nie priamu inode referenciu.
- **Môže smerovať na súbor aj adresár.** Cieľ nemusí existovať v čase vytvorenia, preto môže vzniknúť dangling symlink.
- **Relatívny cieľ sa vyhodnocuje voči adresáru symlinku.** Nevyhodnocuje sa voči current working directory procesu, ktorý link používa.
- **Lookup má limit počtu nasledovaných symlinkov.** Cyklus `a → b → a` skončí chybou typu `ELOOP`, nie nekonečným kernelovým lookupom.

Pri bezpečnostne citlivých operáciách sú symlink races dôležitý failure mode. Privilegovaný program nemá nekriticky kontrolovať cestu a následne ju otvoriť spôsobom, ktorý dovolí útočníkovi medzi krokmi vymeniť symlink; používa sa bezpečný `openat`-style lookup, directory file descriptor a vhodné flags.

## 10. Rename, unlink a lifetime objektu

`rm` typicky nevykonáva fyzické prepísanie dát. Zavolá `unlink`, ktorý odstráni jednu directory entry a zníži link count inode. Kernel uvoľní inode a jeho bloky až keď link count dosiahne nulu **a zároveň** neexistuje otvorená kernelová referencia.

```text
meno odstránené
+ link count = 0
+ proces stále drží fd
= dáta zostávajú alokované a zapisovateľné
```

Rename v rámci jedného filesystému môže byť atomická namespace operácia: pozorovateľ uvidí staré alebo nové meno, nie polovičný obsah. Táto vlastnosť sa používa pri bezpečnom nahrádzaní konfiguračných súborov: aplikácia zapíše nový dočasný súbor, flushne ho a vykoná rename na cieľovú cestu. Durability po power loss však môže vyžadovať aj `fsync` súboru a parent adresára; atomická viditeľnosť nie je totožná s trvalým zápisom na médium.

## 11. Otvorený, ale vymazaný súbor

Keď logrotate alebo administrátor odstráni veľký log, proces môže stále zapisovať cez starý file descriptor. `du` prechádza viditeľné directory entries a súbor nenájde, zatiaľ čo `df` sleduje alokované bloky a stále ich počíta.

```bash
lsof +L1
ls -l /proc/<pid>/fd
```

Riešením je prinútiť proces korektne reopenúť log, napríklad cez podporovaný signal, alebo službu kontrolovane reštartovať. Vytvorenie nového prázdneho súboru pod rovnakým menom vytvorí iný inode a neuvoľní bloky starého otvoreného objektu.

## 12. Inode exhaustion a block exhaustion

Filesystem môže odmietnuť nový súbor z viacerých odlišných dôvodov. Voľné gigabajty neznamenajú automaticky dostupnú schopnosť vytvárať nové objekty.

- **Block exhaustion — nie sú voľné dátové bloky.** `df -h` ukáže vysoké využitie; príčinou môžu byť veľké súbory, snapshots, reserved blocks alebo deleted-open files.
- **Inode exhaustion — nie sú voľné inode objekty.** `df -i` môže byť na 100 %, hoci dátové bloky zostávajú voľné. Typickou príčinou sú milióny malých cache, mail queue alebo session súborov.
- **Quota exhaustion — limit prekročil konkrétny user, group alebo project.** Celý filesystem môže mať voľnú kapacitu, ale zapisujúca identita dostane `EDQUOT` alebo používateľsky podobný symptóm.
- **Read-only alebo error state — filesystem bol remountnutý `ro`.** Kernel môže po chybách chrániť konzistenciu zákazom ďalších zápisov; čistenie priestoru samo problém nevyrieši.

Diagnostika musí vždy overiť presný target mount cez `findmnt -T`, pretože `/var/lib/app` môže byť na inom filesystéme než `/var` alebo `/`.

## 13. Mounty a mount namespace

Mount spája filesystem root alebo inú subtree view s mount pointom. Kernel pathname lookup pri dosiahnutí mount pointu prejde do pripojeného stromu.

```bash
findmnt
findmnt -T /var/lib/app/data.db
mountpoint /var/lib/app
cat /proc/self/mountinfo
```

Procesy môžu mať odlišné mount namespaces. Kontajner môže vidieť bind-mounted `/config`, zatiaľ čo host proces pod rovnakou textovou cestou vidí iný strom. Pri troubleshootingu preto treba spustiť `findmnt` alebo `nsenter` v správnom namespace, nie automaticky veriť host pohľadu.

Bind mount nepridáva novú kópiu dát; pripája existujúcu subtree na ďalšiu cestu. OverlayFS skladá lower read-only vrstvy s upper writable vrstvou, takže delete môže byť reprezentovaný whiteout objektom namiesto odstránenia lower súboru.

## 14. Mount flags a ich hranice

Mount flags menia povolené operácie pre celý mount alebo jeho view. Sú defense-in-depth mechanizmom, nie kompletným access-control modelom.

- **`ro` — blokuje bežné zápisy cez daný mount.** Neznamená, že underlying storage nemožno zmeniť cez inú read-write view alebo privilegovaný mechanizmus.
- **`noexec` — zakazuje priame spustenie binárky z mountu.** Interpreter môže stále prečítať script ako dáta, preto flag sám nezabraňuje každému vykonaniu škodlivého obsahu.
- **`nosuid` — ignoruje setuid a setgid účinok.** Znižuje riziko privilege escalation z nedôveryhodného volume, ale capabilities, interpreters a iné cesty treba riešiť samostatne.
- **`nodev` — neaktivuje device-node semantics.** Bežný súbor s device major/minor údajmi sa cez tento mount nepoužije na prístup k zariadeniu.
- **`relatime`, `noatime` — riadia access-time writes.** Znižujú write amplification, ale môžu ovplyvniť aplikácie, ktoré na presnom `atime` závisia.

Pri security troubleshootingu treba overiť aj mount flags. Správne mode bits na executable súbore nepomôžu, ak jeho mount používa `noexec`.

## 15. Pseudo-filesystems a device nodes

Nie každý inode vedie k dátovým blokom na disku. VFS poskytuje jednotné rozhranie aj kernelovým a device objektom.

- **`procfs` pod `/proc` — runtime pohľad na procesy a kernel settings.** Čítanie súboru môže dynamicky generovať obsah a zápis do niektorých `sysctl` entries mení kernelový stav.
- **`sysfs` pod `/sys` — objektový model devices, drivers a subsystems.** Nie je určený ako stabilná databáza pre ľubovoľné aplikačné dáta.
- **`devtmpfs` a udev pod `/dev` — device nodes.** Node obsahuje major/minor identitu, cez ktorú kernel vyberie driver; samotný node nie je obsah zariadenia.
- **`tmpfs` — pamäťou podporovaný filesystem.** Dáta spotrebúvajú memory accounting a môžu používať swap; po unmount/reboot typicky zaniknú.
- **`overlayfs` — zložený view vrstiev.** Kontajnerový writable layer nie je vhodný pre durable state, ktorý musí prežiť replacement containeru.

Pathname preto neodhaľuje storage alebo durability model. Pred backupom, performance analýzou alebo capacity zásahom treba zistiť filesystem type, source a mount options.

## 16. Timestamps a ich interpretácia

Linux inode typicky sleduje viac timestampov. Ich význam sa často zamieňa.

- **`mtime` — čas poslednej zmeny obsahu súboru.** Zmena ownera alebo permissions ho nemusí upraviť.
- **`ctime` — čas poslednej zmeny inode metadata.** Nie je to všeobecný creation time; mení sa napríklad pri `chmod`, `chown`, link alebo zmene obsahu.
- **`atime` — čas prístupu k dátam.** Mount policy môže aktualizáciu odložiť alebo vypnúť.
- **Birth/creation time — dostupnosť závisí od filesystému a nástroja.** Nemožno predpokladať, že každý Linux filesystem ho spoľahlivo poskytuje.

Pri forenznej analýze alebo backup incremental logike treba poznať konkrétny filesystem a mount policy. Jeden timestamp bez kontextu nie je dôkazom celej histórie objektu.

## 17. Diagnostické nástroje a otázka, ktorú odpovedajú

```bash
stat /path/to/object
ls -li /path/to/object
namei -l /path/to/object
findmnt -T /path/to/object
df -hT /path
df -i /path
du -xhd1 /var
lsof +L1
file /path/to/object
readlink -f /path/to/object
```

- **`stat` — aký inode objekt a metadata kernel/filesystem reportuje?** Ukáže size, inode number, links, mode, owner a timestamps.
- **`namei -l` — na ktorom pathname komponente zlyháva traversal?** Je vhodný pri `EACCES`, nesprávnom symlinku alebo neočakávanom parent ownershipu.
- **`findmnt -T` — ktorý mount a options skutočne obsluhujú cieľ?** Chráni pred diagnostikou nesprávneho filesystemu.
- **`df` — koľko blokov a inode objektov eviduje filesystem?** Nehovorí, ktorý viditeľný adresár ich spotreboval.
- **`du` — koľko blokov spotrebujú viditeľné directory entries v prechádzanom strome?** Nevidí deleted-open files a bez `-x` môže prejsť ďalšie mounty.
- **`lsof +L1` — ktoré procesy držia objekty bez directory linku?** Spája procesný a filesystem lifetime model.

## 18. End-to-end príklad: otvorenie konfigurácie

Proces spustí:

```c
openat(AT_FDCWD, "/etc/app/config.yaml", O_RDONLY)
```

Kernel najprv vyberie mount namespace procesu a root/cwd referenciu. VFS rozlíši `etc`, `app` a `config.yaml`, pri každom adresári overí traversal permission a sleduje prípadné mounty alebo symlinky. Na cieľovom inode vyhodnotí DAC, ACL, capabilities a LSM policy. Filesystem implementation načíta metadata alebo dáta cez page cache a pri úspechu proces dostane file descriptor.

`ENOENT`, `EACCES`, `ELOOP`, `ENOTDIR` a `EROFS` preto označujú odlišné fázy lookupu alebo operácie. Všeobecné tvrdenie „súbor nejde otvoriť“ treba rozložiť podľa presného syscallu, pathname a errno.

## 19. Troubleshooting: `No space left on device`

Aplikácia hlási `ENOSPC`, ale rýchly pohľad na `df -h /` ukazuje voľné miesto. Správny postup nezačína náhodným mazaním súborov.

1. **Identifikuj presnú cestu a mount.** `findmnt -T /var/lib/app/file` ukáže, či zápis smeruje na root filesystem, samostatný volume alebo tmpfs.
2. **Over block usage aj inode usage.** `df -hT` a `df -i` odlíšia veľké dáta od veľkého počtu malých objektov.
3. **Over quota a project limits.** Používateľ alebo aplikačný project môže mať vyčerpaný limit napriek voľnej globálnej kapacite.
4. **Porovnaj `df` a `du`.** Veľký rozdiel môže znamenať deleted-open files, snapshots, reserved blocks alebo neprístupné subtrees.
5. **Skontroluj `lsof +L1`.** Ak proces drží odstránený log, zabezpeč reopen alebo kontrolovaný restart a over, že bloky sa uvoľnili.
6. **Over kernel a filesystem errors.** `dmesg`, journal a mount flags môžu ukázať remount read-only alebo metadata corruption.
7. **Po náprave over aplikačný outcome.** Nestačí, že `df` kleslo; treba potvrdiť úspešný zápis, logging a prípadné recovery poškodeného workflowu.

## 20. Anti-patterny

### Diagnostika iba podľa pathname

Rovnaká cesta môže v inom mount namespace alebo po novom mountnutí ukazovať na iný objekt. Vždy treba overiť namespace, mount source a inode, nie iba text názvu.

### `chmod 777` pri každom `Permission denied`

Chyba môže vzniknúť na parent traversal, ACL, mount flags alebo SELinux/AppArmor vrstve. Globálne otvorenie mode bits môže nezmeniť root cause a zároveň zväčšiť attack surface.

### Mazanie logu bez koordinácie s writerom

`rm` odstráni meno, ale dlhodobý proces môže držať inode otvorený. Správny logging lifecycle potrebuje rotation, reopen signal alebo service integration a následnú verifikáciu diskového využitia.

### Durable state v kontajnerovom writable layeri

Overlay writable layer je viazaný na lifecycle konkrétneho containeru. Dáta, ktoré musia prežiť rescheduling alebo replacement, patria do explicitného persistent storage kontraktu.

## 21. Kontrolné otázky

1. Prečo pathname nie je samotný súbor a prečo môže rovnaká cesta v dvoch procesoch ukazovať inam?
2. Aký je rozdiel medzi directory entry, inode, open file description a file descriptorom?
3. Prečo hard link bežne nemožno vytvoriť cez hranicu filesystemu?
4. Ako sa vyhodnocuje relatívny symlink a aký problém predstavuje symlink race?
5. Prečo `df` môže ukazovať využité bloky, ktoré `du` nenájde?
6. Aký je rozdiel medzi block exhaustion, inode exhaustion a quota exhaustion?
7. Prečo atomický rename automaticky neznamená durability po strate napájania?
8. Ako mount namespace mení interpretáciu pathname pri kontajnerovom troubleshootingu?
9. Čo presne znamenajú `mtime`, `ctime` a `atime`?
10. Ako by si diagnostikoval `EACCES`, `ENOENT` a `EROFS` pri rovnakom `openat()` volaní?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Procesy, thready, PID a signals](processes-threads-pid-signals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Users, groups, permissions, sudo a PAM →](users-groups-permissions-sudo-pam.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
