# Storage, Mounts and Filesystems

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Filesystem hierarchy, inodes a links](filesystem-hierarchy-inodes-links.md), [Users, groups, permissions, sudo a PAM](users-groups-permissions-sudo-pam.md)
- Súvisiace témy: block devices, LVM, RAID, persistence, backups, container storage

## 1. Definícia

Linux storage stack prevádza fyzické alebo virtuálne zariadenie na block device, voliteľné vrstvy transformácie a nakoniec filesystem pripojený do jedného adresárového stromu.

Mentálny model:

```text
Disk / virtual disk
  ↓
Block device
  ↓
Partition / RAID / encryption / LVM
  ↓
Filesystem
  ↓
Mount
  ↓
Path v jednotnom VFS strome
```

Adresár ako `/data` sám osebe nie je disk. Je to mount point, na ktorý môže, ale nemusí byť pripojený filesystem.

## 2. Block devices

Block device poskytuje náhodný prístup k blokom dát. Typické názvy:

```text
/dev/sda
/dev/sda1
/dev/nvme0n1
/dev/nvme0n1p1
/dev/vda
/dev/mapper/vg0-data
```

Inventár:

```bash
lsblk
lsblk -f
blkid
```

- `lsblk` ukáže topológiu block devices,
- `lsblk -f` doplní filesystem type, UUID a mountpoint,
- `blkid` číta filesystem a partition identifiers.

Názov `/dev/sdb` nemusí byť stabilný medzi rebootmi. Pre persistent konfiguráciu sa používajú UUID, labels alebo stabilné device paths.

## 3. Partition table

Partition table rozdeľuje disk na logické regions.

Bežné modely:

- GPT,
- MBR/DOS.

Nástroje:

```bash
sudo fdisk -l
sudo parted -l
```

GPT podporuje moderné veľké disky a viac partitions. Zmena partition table je riziková operácia; nesprávny offset alebo resize môže zneprístupniť dáta.

## 4. Filesystem

Filesystem organizuje blocks na súbory, directories, metadata a allocation structures.

Časté filesystems:

| Filesystem | Typické použitie |
|---|---|
| ext4 | všeobecný Linux filesystem |
| XFS | veľké filesystems a enterprise workloads |
| Btrfs | snapshots, checksums a advanced volume features |
| tmpfs | dáta v pamäti/swap, životnosť do unmount/rebootu |
| vfat | interoperabilita a EFI system partition |

Vytvorenie filesystemu zmaže alebo prepíše existujúce filesystem metadata:

```bash
sudo mkfs.ext4 /dev/vdb1
sudo mkfs.xfs /dev/vdb1
```

Pred `mkfs` treba nezávisle overiť device, veľkosť, topológiu a absenciu potrebných dát.

## 5. VFS a mount

Virtual Filesystem Switch poskytuje spoločné rozhranie nad rôznymi filesystem implementations.

Mount pripojí root konkrétneho filesystemu na directory v existujúcom namespace:

```bash
sudo mount /dev/vdb1 /data
```

Po mountnutí pôvodný obsah directory `/data` nezmizne z disku, ale je prekrytý novým mountom. Po unmountnutí sa znovu zobrazí.

Kontrola:

```bash
findmnt
findmnt /data
mount
cat /proc/self/mountinfo
```

`findmnt` je praktickejší než parsovanie human-readable výstupu `mount`.

## 6. `/etc/fstab`

`/etc/fstab` deklaruje filesystems, ktoré sa majú mountovať pri boote alebo na požiadanie.

Príklad:

```fstab
UUID=1a2b-3c4d  /data  ext4  defaults,noatime  0  2
```

Polia:

```text
source  target  type  options  dump  fsck-order
```

Po úprave:

```bash
sudo mount -a
findmnt /data
```

`mount -a` je dôležitá validácia pred rebootom. Chybný fstab môže predĺžiť boot, prepnúť systém do emergency mode alebo nechať službu bez potrebného storage.

Bezpečnejší source je často UUID:

```bash
blkid /dev/vdb1
```

## 7. Mount options

Časté options:

- `ro` / `rw`,
- `noexec`,
- `nosuid`,
- `nodev`,
- `noatime`,
- `nofail`,
- `_netdev`,
- filesystem-specific options.

Príklad hardeningu data mountu:

```fstab
UUID=... /srv/uploads ext4 defaults,nodev,nosuid,noexec 0 2
```

Trade-off: `noexec` nezabráni interpreteru explicitne prečítať script, napríklad `bash /srv/uploads/file.sh`. Je to defense-in-depth, nie absolútna execution boundary.

## 8. Capacity: `df` vs. `du`

```bash
df -h
df -i
du -sh /var/*
```

- `df` číta filesystem allocation state,
- `du` prechádza viditeľné directory entries a sčítava blocks súborov.

Rozdiel môže vzniknúť pri deleted-open file:

```text
process drží otvorený file descriptor
  ↓
file bol unlinknutý
  ↓
path už nevidno cez du
  ↓
blocks sa uvoľnia až po close
```

Diagnostika:

```bash
sudo lsof +L1
```

Filesystem môže byť plný aj pri voľných data blocks, ak sa vyčerpajú inodes:

```bash
df -i
```

## 9. Journaling a crash consistency

Journaling filesystem zapisuje metadata alebo dáta cez journal tak, aby po crashi vedel obnoviť konzistentnú štruktúru.

Journaling nie je backup. Chráni primárne konzistenciu filesystemu, nie proti:

- omylom zmazaným dátam,
- ransomware,
- aplikačnej korupcii,
- strate celého zariadenia.

## 10. Filesystem check a repair

Ext filesystems:

```bash
sudo fsck -f /dev/vdb1
```

XFS:

```bash
sudo xfs_repair /dev/vdb1
```

Filesystem repair sa typicky vykonáva na unmounted filesysteme. Spustenie nesprávneho repair nástroja na mounted alebo aktívnom storage môže poškodenie zhoršiť.

Pred repair:

1. zisti scope dopadu,
2. zastav writers,
3. vytvor snapshot alebo image, ak je to možné,
4. over hardware/block layer chyby,
5. použi filesystem-specific postup.

## 11. LVM

Logical Volume Manager vkladá abstrakciu medzi physical devices a filesystems.

```text
Physical Volume (PV)
  ↓
Volume Group (VG)
  ↓
Logical Volume (LV)
  ↓
Filesystem
```

Inventár:

```bash
pvs
vgs
lvs
```

LVM umožňuje flexibilné rozšírenie, snapshots a skladanie capacity. Filesystem však treba po zväčšení LV často rozšíriť samostatne.

Príklad ext4:

```bash
sudo lvextend -L +10G /dev/vg0/data
sudo resize2fs /dev/vg0/data
```

Príklad XFS:

```bash
sudo lvextend -L +10G /dev/vg0/data
sudo xfs_growfs /data
```

XFS sa zväčšuje cez mounted target; ext4 môže podľa scenára používať device. Shrink support sa medzi filesystems líši a je rizikovejší než grow.

## 12. Swap

Swap je block alebo file-backed priestor, kam kernel môže presúvať memory pages.

```bash
swapon --show
free -h
cat /proc/swaps
```

Swap nie je náhrada RAM. Môže poskytnúť buffer pri tlaku na pamäť, ale intenzívne swapovanie môže spôsobiť vysokú latency a thrashing.

## 13. Network filesystems

NFS, SMB a ďalšie remote filesystems pridávajú závislosť na sieti a vzdialenej službe.

Riziká:

- boot ordering,
- hangs pri network partition,
- odlišná locking semantics,
- identity mapping,
- cache consistency,
- latency.

Vo fstab sa môže použiť `_netdev`, `nofail` alebo systemd automount podľa požadovaného failure modelu. „Mount sa podaril“ neznamená, že storage je zdravý pod reálnou záťažou.

## 14. Diagnostický postup

Aplikácia hlási `No space left on device`:

```bash
df -h
df -i
findmnt /path
sudo du -xhd1 /path | sort -h
sudo lsof +L1
journalctl -k -b
lsblk -f
```

Otázky:

1. Ktorý filesystem path reálne používa?
2. Sú vyčerpané blocks alebo inodes?
3. Nie sú veľké files prekryté mountom?
4. Nedrží proces deleted-open files?
5. Nie je filesystem read-only po I/O chybe?
6. Nerastú logy, cache alebo temporary data?

## 15. Časté omyly

### „Directory `/data` je samostatný disk“

Iba ak je naň pripojený samostatný filesystem.

### „`du` a `df` musia ukazovať rovnaké číslo“

Nie. Merajú rozdielne vrstvy a deleted-open files vytvárajú typický rozdiel.

### „LVM snapshot je backup“

Nie. Zvyčajne zdieľa failure domain s pôvodnými dátami a má obmedzenú životnosť/capacity.

### „Journaling chráni pred stratou dát“

Primárne pomáha s crash consistency, nie s každým typom straty.

### „Mount option `noexec` úplne zabráni spusteniu kódu“

Nie. Je to obmedzenie pri priamom exec z mountu, nie univerzálny zákaz interpretácie obsahu.

## 16. Kontrolné otázky

1. Aký je rozdiel medzi block device, filesystemom a mountom?
2. Prečo je UUID stabilnejší než `/dev/sdb1`?
3. Čo sa stane s pôvodným obsahom mount pointu po mountnutí?
4. Prečo sa `df` a `du` môžu výrazne líšiť?
5. Ako môže filesystem zlyhať pri voľných gigabajtoch?
6. Prečo journaling nie je backup?
7. Ktoré dve vrstvy treba rozšíriť pri LVM + filesystem scenári?
8. Prečo je network filesystem odlišný failure domain?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: journald a logging](journald-and-logging.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Memory a CPU fundamentals →](cpu-and-memory-fundamentals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
