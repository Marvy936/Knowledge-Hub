# Storage, mounty a filesystems

Storage path v Linuxe skladá viac nezávislých vrstiev. Application zapisuje cez VFS do mounted filesystemu; ten môže ležať na partition, device mapper targete, LVM logical volume, encrypted mappingu, RAID-e alebo virtual block device. Každá vrstva má vlastnú identity, capacity, failure a persistence semantics.

```text
application file operation
→ pathname a mount namespace
→ filesystem a page cache
→ block layer a queues
→ mapper/LVM/RAID/encryption
→ physical alebo virtual device
→ durable media acknowledgement
```

`df` meria filesystem allocation, `du` prechádza reachable pathnames a `lsblk` zobrazuje block topology; preto môžu ukazovať rozdielne hodnoty bez chyby. Mount point môže byť prekrytý ďalším mountom, deleted-open file môže držať space a úspešný `write()` môže znamenať iba prijatie do page cache. Prevádzkové overenie potrebuje rozlíšiť visibility, capacity, I/O completion, flush/durability, filesystem consistency a schopnosť obnovy.

## 1. Mentálny model storage stacku

Linux storage nie je jedna vrstva. Cesta od fyzického alebo virtuálneho disku k súboru prechádza cez viacero objektov, pričom každá vrstva má vlastný stav, identitu a failure modes.

```text
Disk alebo cloud volume
  ↓
Block device
  ↓
Partition / RAID / dm-crypt / LVM
  ↓
Filesystem
  ↓
Mount v konkrétnom mount namespace
  ↓
Path cez VFS
  ↓
Súbor, directory alebo iný filesystem object
```

Adresár `/data` preto nie je disk. Je to iba pathname, na ktorú môže byť pripojený samostatný filesystem; bez mountu je to obyčajný adresár na parent filesysteme.

## 2. Block device

Block device poskytuje adresovateľný priestor rozdelený na bloky. Kernel nad ním vykonáva čítanie a zápis bez toho, aby samotné zariadenie poznalo pojmy súbor, adresár alebo oprávnenie.

Typické názvy zahŕňajú `/dev/sda`, `/dev/nvme0n1`, `/dev/vda` alebo `/dev/mapper/vg0-data`. Meno v `/dev` však nemusí byť stabilná dlhodobá identita, preto sa persistentná konfigurácia opiera skôr o UUID, filesystem label alebo stabilnú device path.

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,UUID,MOUNTPOINTS
blkid
udevadm info --query=property --name=/dev/sda
```

- `lsblk` — zobrazuje topológiu block vrstiev, takže vie odhaliť partition, LVM aj mapper relationships.
- `blkid` — číta identifikátory filesystemov a partitions, ktoré možno použiť vo `fstab`.
- `udevadm info` — ukazuje device properties a stabilnejšie identifikátory vytvorené udevom.

## 3. Partition table

Partition table rozdeľuje address space disku na logické oblasti. GPT je moderný model s redundantnými metadátami a podporou veľkých diskov; MBR je starší model s výraznejšími limitmi.

Partition nie je filesystem. Je to len vyhradený blokový rozsah, na ktorý možno neskôr umiestniť filesystem, LVM physical volume, swap alebo inú transformačnú vrstvu.

```bash
fdisk -l
parted -l
lsblk -o NAME,START,SIZE,TYPE
```

Zmena začiatku partition alebo nesprávne zmenšenie môže zneprístupniť dáta aj vtedy, keď filesystem metadata zostanú fyzicky na disku. Pred zápisom partition table treba overiť device identity, aktuálne mounty, zálohu a presný resize workflow.

## 4. Transformačné vrstvy

Medzi fyzickým diskom a filesystemom môže byť viac vrstiev. RAID kombinuje zariadenia kvôli dostupnosti alebo výkonu, dm-crypt poskytuje block encryption a LVM vytvára flexibilné logické volumes.

Každá ďalšia vrstva pridáva schopnosť, ale aj ďalší stav, ktorý treba diagnostikovať. Ak napríklad filesystem vidí I/O error, príčina môže ležať vo filesysteme, logical volume, RAID sete, cloud volume alebo fyzickom zariadení.

```text
/dev/sdb + /dev/sdc
        ↓ md RAID
/dev/md0
        ↓ LUKS
/dev/mapper/secure
        ↓ LVM PV → VG → LV
/dev/mapper/vg0-data
        ↓ ext4
mount /data
```

## 5. Filesystem

Filesystem premieňa blokový priestor na menný priestor súborov, directories a metadata. Spravuje allocation, inodes, extents, free-space structures, timestamps a consistency metadata.

- `ext4` — všeobecný Linux filesystem s journalingom a širokou podporou.
- `XFS` — škáluje dobre pre veľké filesystems a paralelné workloady, ale nepodporuje shrink.
- `Btrfs` — poskytuje checksums, snapshots a volume features, no vyžaduje znalosť jeho vlastného operating modelu.
- `tmpfs` — ukladá dáta do pamäte a prípadne swapu; jeho obsah neprežije unmount alebo reboot.

```bash
mkfs.ext4 /dev/vdb1
mkfs.xfs /dev/vdb1
```

`mkfs` vytvára nové filesystem metadata a môže prepísať existujúci layout. Pred jeho použitím treba nezávisle overiť zariadenie, veľkosť, mount state a absenciu potrebných dát; samotné meno device nie je dostatočná kontrola.

## 6. VFS a mount

VFS poskytuje jednotné syscall rozhranie nad rôznymi filesystem implementations. Aplikácia používa `open`, `read`, `write` a ďalšie operácie bez toho, aby musela vedieť, či cieľ leží na ext4, XFS, NFS alebo tmpfs.

Mount pripojí root jedného filesystemu na directory v konkrétnom mount namespace. Pôvodný obsah mount pointu sa nevymaže, ale počas mountu je prekrytý a znovu sa objaví po unmountnutí.

```bash
mount /dev/vdb1 /data
findmnt -T /data/example.txt
cat /proc/self/mountinfo
```

`findmnt -T` je dôležitý pri diagnostike, pretože odpovedá na otázku, ktorý filesystem konkrétny pathname skutočne používa. Pohľad na mounts môže byť odlišný medzi hostom, kontajnerom a samostatným mount namespace.

## 7. Persistentné mounty a `/etc/fstab`

`/etc/fstab` deklaruje, ktoré filesystems sa majú mountovať pri boote alebo na požiadanie. Nie je to iba zoznam príkazov; je to vstup pre mount tooling a systemd-generated mount units.

```fstab
UUID=1a2b-3c4d  /data  ext4  defaults,noatime  0  2
```

Polia určujú source, target, filesystem type, options, historický dump flag a poradie filesystem checku. UUID je vhodnejší než `/dev/sdb1`, pretože kernelové názvy sa môžu po zmene topológie alebo reboote zmeniť.

```bash
findmnt --verify
mount -a
findmnt /data
```

`mount -a` alebo `findmnt --verify` treba spustiť pred rebootom. Chybný `fstab` môže spôsobiť emergency mode, dlhé timeouty alebo štart aplikácie nad prázdnym parent adresárom namiesto očakávaného storage.

## 8. Mount options ako policy

Mount options menia správanie a bezpečnostné hranice filesystemu. Ich význam treba posudzovať spolu s workloadom, pretože rovnaká option môže byť vhodná pre uploads a nevhodná pre aplikačné binaries.

- `ro` — kernel odmietne zápisy cez daný mount; nechráni však proti zmene lower layer mimo tohto mountu.
- `noexec` — blokuje priame `execve` z mountu, ale interpreter môže stále explicitne čítať script ako dáta.
- `nosuid` — ignoruje setuid/setgid privilege transition na tomto mount point-e.
- `nodev` — zabráni používaniu device nodes z filesystemu, čo znižuje attack surface.
- `nofail` a `_netdev` — menia boot dependency a failure model, najmä pri optional alebo network storage.

```fstab
UUID=... /srv/uploads ext4 defaults,nodev,nosuid,noexec 0 2
```

Tieto options sú defense-in-depth, nie náhrada za DAC, ACL, capabilities, SELinux/AppArmor alebo aplikačnú autorizáciu.

## 9. Capacity model: bloky, inodes, quota a reserved space

`No space left on device` neznamená vždy vyčerpané gigabajty. Filesystem môže vyčerpať dátové bloky, inodes, user/project quota alebo priestor dostupný neprivilegovaným procesom.

```bash
df -hT /path
df -i /path
quota -s
xfs_quota -x -c report /mount  # ak sa používa XFS project/user quota
```

`df` číta allocation state filesystemu. `du` prechádza viditeľné directory entries, preto sa čísla môžu líšiť pri deleted-open files, bind mountoch, snapshots alebo neprístupných directories.

```bash
lsof +L1
du -xhd1 /var | sort -h
```

Deleted-open file už nemá pathname, ale jeho bloky zostávajú alokované, kým posledný file descriptor nezanikne. Vytvorenie nového súboru s rovnakým menom starý inode neuvoľní.

## 10. Page cache, writeback a durability

Bežný `write()` často najprv zmení page cache a označí stránky ako dirty. Kernel ich zapíše na storage neskôr podľa writeback policy, takže úspešný syscall nemusí znamenať, že dáta sú fyzicky durable.

Aplikácie vyžadujúce durability používajú `fsync`, `fdatasync` alebo databázové WAL mechanizmy. Aj potom závisí výsledok od storage stacku, cache politiky a správneho správania zariadenia pri flush operáciách.

```bash
sync
cat /proc/meminfo | grep -E 'Dirty|Writeback'
```

`sync` môže pomôcť pred plánovaným odpojením, ale nie je náhradou za aplikačný consistency protocol. Databázová konzistencia musí byť navrhnutá na úrovni databázy, nie iba filesystemu.

## 11. Journaling a crash consistency

Journaling zaznamenáva vybrané zmeny pred ich aplikovaním do hlavných filesystem structures. Po páde systém replayne journal a obnoví konzistentnú metadata štruktúru bez plného skenovania.

Journaling však nie je backup ani automatická ochrana aplikačných dát. Nevráti omylom zmazaný súbor, neodstráni ransomware a nemusí zachovať logickú konzistenciu dát, ak aplikácia používa nesprávne poradie zápisov.

## 12. Filesystem check a repair

Repair nástroj mení filesystem metadata, preto sa má používať až po identifikácii failure domainu a zastavení writers. Oprava aktívneho alebo nesprávne identifikovaného filesystemu môže poškodenie zväčšiť.

```bash
fsck -f /dev/vdb1       # ext family, typicky unmounted
xfs_repair /dev/vdb1    # XFS, typicky unmounted
```

Bezpečný postup zahŕňa:

1. **Identifikáciu správneho device** — over topológiu cez `lsblk`, `findmnt` a UUID, aby repair nebežal nad nesprávnym volume.
2. **Zastavenie zápisov** — unmount alebo recovery mode zabráni súbežnej zmene metadata počas opravy.
3. **Zachovanie evidence** — snapshot alebo block image umožní opakovať analýzu, ak repair zlyhá.
4. **Kontrolu lower layers** — kernel I/O errors, RAID degradation alebo cloud volume problém treba riešiť skôr než samotný filesystem.
5. **Filesystem-specific workflow** — ext4 a XFS majú rozdielne nástroje, možnosti aj recovery semantics.

## 13. LVM

LVM oddeľuje fyzickú kapacitu od logických volumes. Physical volumes tvoria volume group a z jej extents sa prideľujú logical volumes.

```text
PV1 + PV2
   ↓
Volume Group
   ↓
Logical Volume
   ↓
Filesystem
```

```bash
pvs
vgs
lvs -a -o +devices
```

Rozšírenie LV automaticky nemusí rozšíriť filesystem. Pri ext4 sa často používa `resize2fs`, pri XFS `xfs_growfs` nad mounted targetom.

```bash
lvextend -L +10G /dev/vg0/data
resize2fs /dev/vg0/data
# alebo
xfs_growfs /data
```

Shrink je podstatne rizikovejší a nie každý filesystem ho podporuje. Pred zmenšením treba najprv bezpečne zmenšiť filesystem, potom block layer; opačné poradie môže odrezať živé dáta.

## 14. Snapshots

LVM alebo storage snapshot zachytí point-in-time block view, často pomocou copy-on-write. Snapshot je užitočný pre krátkodobú recovery alebo konzistentné čítanie, ale zvyčajne zdieľa failure domain s pôvodnými dátami.

Snapshot bez aplikačnej koordinácie môže obsahovať crash-consistent, nie application-consistent stav. Databáza môže vyžadovať flush, freeze alebo natívny backup protocol pred vytvorením snapshotu.

Snapshot tiež potrebuje kapacitu na changed blocks. Pri jej vyčerpaní sa môže stať neplatným, preto musí byť monitorovaný a časovo obmedzený.

## 15. Swap

Swap rozširuje priestor pre anonymné memory pages mimo RAM. Kernel ho môže použiť na uvoľnenie fyzickej pamäte pre aktívnejšie stránky alebo page cache.

```bash
swapon --show
free -h
cat /proc/swaps
vmstat 1
```

Swap nie je náhrada RAM. Neustále swap-in/swap-out operácie vytvárajú vysokú latency a môžu viesť k thrashingu, pri ktorom systém trávi viac času presunom stránok než vykonávaním užitočnej práce.

## 16. Network filesystems

NFS, SMB a ďalšie remote filesystems rozširujú storage path o sieť, vzdialený server, identity mapping a distribuované cache/locking semantics. Pathname lookup alebo zápis preto môže blokovať na network partition alebo preťaženom serveri.

- Boot ordering — mount môže čakať na sieť alebo remote endpoint, preto treba explicitný failure model.
- Locking — advisory locks a recovery po výpadku sa môžu správať inak než na lokálnom filesysteme.
- Identity mapping — UID/GID alebo doménová identita musí byť konzistentná na oboch stranách.
- Cache consistency — klient nemusí okamžite vidieť zmenu vykonanú iným klientom podľa protokolu a mount options.

`_netdev`, `nofail` alebo automount menia startup správanie, ale nepreukazujú zdravie storage. Funkčný mount treba testovať reálnym read/write workloadom a pozorovať latency aj error rate.

## 17. Bind mounts, namespaces a kontajnery

Bind mount pripojí existujúcu directory view na inú pathname bez vytvorenia nového filesystemu. Kontajnery ho používajú na sprístupnenie host directories alebo volumes v inom mount namespace.

```bash
mount --bind /srv/data /opt/app/data
findmnt -T /opt/app/data
```

Rovnaký inode môže byť viditeľný cez viac ciest. Pri diagnostike preto treba skúmať mount ID, namespace a source, nie iba pathname z vnútra kontajnera.

OverlayFS skladá lower read-only layers s upper writable layer. Mazanie môže byť reprezentované whiteout objektom a apparent disk usage sa môže líšiť od jednoduchého pohľadu aplikácie.

## 18. Bezpečný unmount

Unmount zlyhá ako `busy`, ak namespace stále obsahuje open files, current working directories alebo ďalšie dependent mounts. Nútené odpojenie môže poškodiť aktívne operácie alebo ponechať aplikáciu v nejasnom stave.

```bash
findmnt -R /data
fuser -vm /data
lsof +f -- /data
```

Pred unmountom treba zastaviť writers, opustiť current directories, flushnúť aplikačný stav a overiť nested mounts. Lazy unmount iba odpojí pathname z namespace a dokončí cleanup neskôr; nie je univerzálnym riešením storage incidentu.

## 19. Diagnostika `No space left on device`

Postup má prechádzať vrstvami bez náhodného mazania dát:

1. **Urči efektívny mount** — `findmnt -T /path` potvrdí, ktorý filesystem aplikácia používa.
2. **Skontroluj bloky a inodes** — `df -h` a `df -i` odlíšia dva odlišné typy vyčerpania.
3. **Skontroluj quota a reserved space** — používateľ môže mať limit aj pri voľnom globálnom priestore.
4. **Porovnaj `du` a `df`** — veľký rozdiel ukazuje na deleted-open files, hidden mount content alebo snapshots.
5. **Skontroluj read-only remount** — kernel môže po I/O chybe prepnúť filesystem na read-only.
6. **Skontroluj lower layers** — `journalctl -k`, `dmesg`, RAID/LVM/cloud metrics môžu ukázať skutočný storage failure.
7. **Odstráň príčinu rastu** — rotácia logov, retention, cache policy alebo aplikačná chyba sú dlhodobá náprava; náhodné mazanie iba obnoví krátkodobú kapacitu.

## 20. Anti-patterny

### Device identifikovaný iba menom

Automatizácia predpokladá, že `/dev/sdb` je vždy dátový disk. Po zmene topológie môže rovnaké meno patriť inému zariadeniu, preto treba používať UUID, labels a nezávislé safety checks.

### Mount bez validácie

Služba zapisuje do `/data`, hoci mount zlyhal, a dáta skončia na root filesysteme. Správny model zahŕňa dependency na mount unit, kontrolu `findmnt` a failure, ak required storage nie je dostupný.

### Snapshot považovaný za backup

Snapshot zdieľa storage account, credentials alebo fyzický failure domain s primárnymi dátami. Backup potrebuje oddelenie, retention, restore test a ochranu pred rovnakou chybou alebo kompromitáciou.

### Repair pred diagnostikou

`fsck` alebo `xfs_repair` sa spustí okamžite bez snapshotu a bez kontroly hardware chýb. Tým sa môže stratiť evidence a logická korupcia sa môže premeniť na nezvratnú zmenu metadata.

## 21. Kontrolné otázky

1. Aký je rozdiel medzi block device, filesystemom, mountom a pathname?
2. Prečo UUID poskytuje stabilnejšiu identitu než `/dev/sdb1`?
3. Prečo sa `df` a `du` môžu výrazne líšiť?
4. Ako sa líši vyčerpanie blocks, inodes a quota?
5. Prečo úspešný `write()` nemusí znamenať durable zápis?
6. Čo chráni journaling a čo nechráni?
7. Prečo LVM resize a filesystem resize predstavujú dve samostatné operácie?
8. Prečo snapshot bez aplikačnej koordinácie nemusí byť application-consistent?
9. Aké nové failure modes pridáva network filesystem?
10. Ako by si diagnostikoval `No space left on device` bez náhodného mazania dát?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: journald a logging](journald-and-logging.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CPU a memory fundamentals →](cpu-and-memory-fundamentals.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
