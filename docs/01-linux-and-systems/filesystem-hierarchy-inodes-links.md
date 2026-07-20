# Filesystem hierarchy, inodes a links

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Kernel a user space](kernel-and-user-space.md)
- Súvisiace témy: permissions, storage, mounts, containers, backups

## 1. Filesystem ako menný priestor

Linux prezentuje filesystémy ako jeden strom začínajúci v `/`. Samostatné block devices, network filesystems, pseudo-filesystems a bind mounts sa pripájajú do konkrétnych mount points v tomto strome.

```text
/
├── etc
├── home
├── proc
├── sys
├── run
├── tmp
├── usr
└── var
```

Pathname nie je samotný súbor. Je to cesta cez directory entries, ktorou kernel nájde objekt filesystému.

## 2. Filesystem Hierarchy Standard

Bežný význam hlavných adresárov:

| Cesta | Typický obsah |
|---|---|
| `/etc` | systémová konfigurácia |
| `/home` | domovské adresáre používateľov |
| `/root` | domovský adresár používateľa root |
| `/usr` | väčšina programov, knižníc a read-only dát |
| `/var` | meniace sa dáta, logy, cache, queues, databázy |
| `/run` | runtime state od bootu, PID files a sockets |
| `/tmp` | dočasné dáta s rôznou politikou čistenia |
| `/opt` | voliteľný alebo vendor software |
| `/srv` | dáta poskytované službami |
| `/dev` | device nodes spravované kernelom a udev |
| `/proc` | procesný a kernelový pseudo-filesystem |
| `/sys` | sysfs pohľad na devices, drivers a kernel objects |
| `/boot` | bootloader, kernel a initramfs |

Konkrétna distribúcia môže používať symlinks alebo zlúčený `/usr`, preto treba overovať reálny layout namiesto slepého predpokladu.

## 3. Inode

Inode je filesystémový objekt s metadata. Typicky obsahuje:

- file type,
- owner UID a group GID,
- mode bits,
- timestamps,
- file size,
- link count,
- odkazy na dátové bloky alebo extents,
- extended attributes.

Inode neobsahuje bežný filename. Názov sa nachádza v directory entry, ktorá mapuje meno na inode number.

```text
adresár
└── "app.log" ──→ inode 12345 ──→ dátové bloky
```

Preto môže mať jeden inode viac názvov — hard links.

## 4. Directory

Directory je špeciálny typ súboru obsahujúci mapovanie names na inode references. Pri vyhodnotení cesty:

```text
/var/log/app.log
```

kernel postupne:

1. začne v root directory,
2. nájde entry `var`,
3. v ňom nájde `log`,
4. v ňom nájde `app.log`,
5. overí search permission na každom adresári,
6. overí požadovanú operáciu na cieľovom objekte.

Execute bit na adresári znamená možnosť prechádzať cez directory a vyhľadávať entries; neznamená „spustiť adresár“.

## 5. Hard link

Hard link je ďalšia directory entry smerujúca na ten istý inode.

```bash
ln source.txt second-name.txt
ls -li source.txt second-name.txt
```

Vlastnosti:

- oba názvy sú rovnocenné,
- zmena obsahu je viditeľná cez oba názvy,
- inode sa odstráni až keď link count klesne na nulu a žiadny proces ho nemá otvorený,
- bežne nemožno vytvoriť hard link cez hranicu filesystému,
- hard links na directories sú obmedzené, aby sa chránila stromová štruktúra.

Vymazanie jedného mena nevymaže dáta, pokiaľ existuje ďalší hard link alebo otvorený file descriptor.

## 6. Symbolic link

Symbolic link je samostatný inode, ktorého obsahom je cieľová pathname.

```bash
ln -s /opt/app/releases/42 /opt/app/current
readlink /opt/app/current
readlink -f /opt/app/current
```

Vlastnosti:

- môže smerovať cez filesystémy,
- môže smerovať na directory,
- môže byť relatívny alebo absolútny,
- môže zostať dangling, keď cieľ neexistuje.

Relatívny symlink sa vyhodnocuje voči adresáru, v ktorom sa symlink nachádza, nie voči current working directory procesu.

## 7. Otvorený, ale vymazaný súbor

Unix unlink odstráni directory entry. Ak proces stále drží file descriptor, inode a dáta zostávajú alokované.

Typický symptóm:

```text
`df` ukazuje plný filesystem,
`du` nedokáže nájsť zodpovedajúce súbory.
```

Diagnostika:

```bash
lsof +L1
```

Riešením je korektne nechať proces reopenúť súbor alebo ho reštartovať. Vytvorenie nového prázdneho súboru pod rovnakým názvom neuvoľní starý inode držaný procesom.

## 8. Inode exhaustion

Filesystem môže mať voľné dátové bloky, ale žiadne voľné inodes. Potom vytvorenie nového súboru zlyhá napriek voľnej kapacite.

```bash
df -h
df -i
```

Častou príčinou je extrémne veľa malých súborov, cache entries alebo nečistených spool directories.

## 9. Mounts

Mount pripojí filesystem alebo inú view na konkrétnu cestu.

```bash
findmnt
findmnt /var/lib/app
mountpoint /var/lib/app
```

Obsah pôvodného adresára pod mount pointom sa po mountnutí nestratí, ale je dočasne prekrytý novým mountom.

Dôležité mount flags:

- `ro` — read-only,
- `noexec` — obmedzenie execution z tohto mountu,
- `nosuid` — ignorovanie setuid/setgid bitov,
- `nodev` — ignorovanie device nodes,
- `noatime` alebo `relatime` — politika access timestamps.

Mount flags nie sú náhradou za všetky bezpečnostné vrstvy, ale zmenšujú attack surface.

## 10. Device, pseudo a virtual filesystems

Nie všetko pod stromom je uložené na disku:

- `/proc` generuje kernelové informácie dynamicky,
- `/sys` reprezentuje kernel objects,
- `/dev` obsahuje device nodes,
- `tmpfs` drží dáta v pamäti a swap backing,
- `overlayfs` skladá vrstvy, často pri kontajneroch.

Preto nemožno z pathname samotnej určiť storage backend.

## 11. Dôležité príkazy

```bash
stat file
ls -li file
namei -l /path/to/file
findmnt -T /path/to/file
df -hT /path
df -i /path
du -xhd1 /var
file /path/to/object
```

`namei -l` je obzvlášť užitočný pri permission problémoch, pretože zobrazí každý komponent cesty a jeho vlastníctvo a mode bits.

## 12. Časté omyly

### „Filename identifikuje súbor“

Filename identifikuje directory entry. Stabilnejším filesystémovým objektom je inode v rámci konkrétneho filesystému.

### „rm okamžite prepíše dáta“

`rm` typicky vykoná unlink. Uvoľnenie blokov závisí od link countu a otvorených descriptorov; bezpečné mazanie je samostatný problém.

### „Symlink obsahuje dáta cieľového súboru“

Nie. Obsahuje pathname k cieľu.

### „Voľné GB znamenajú, že možno vytvoriť súbor“

Nie nevyhnutne. Môžu byť vyčerpané inodes, quota alebo reserved blocks.

## 13. Troubleshooting scenár

Aplikácia hlási `No space left on device`, ale `df -h` ukazuje voľné miesto.

1. Over `df -i` kvôli inode exhaustion.
2. Over user/project quota.
3. Over cieľový mount cez `findmnt -T`.
4. Skontroluj, či cesta nie je na inom filesysteme než očakávaš.
5. Pozri deleted-open files cez `lsof +L1`.
6. Over reserved space a filesystem errors.

## 14. Kontrolné otázky

1. Kde je uložený filename a kde metadata súboru?
2. Prečo hard link nemožno bežne vytvoriť cez dva filesystémy?
3. Čo sa stane s dátami po `rm`, keď proces súbor stále drží otvorený?
4. Prečo môže byť filesystem plný pri voľných dátových blokoch?
5. Aký je rozdiel medzi hard linkom a symbolic linkom?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Procesy, thready, PID a signals](processes-threads-pid-signals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Users, groups, permissions, sudo a PAM →](users-groups-permissions-sudo-pam.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
