# Linux Namespaces

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Kernel a user space](kernel-and-user-space.md), [Procesy, thready, PID a signals](processes-threads-pid-signals.md), [Linux networking](linux-networking.md)
- Súvisiace témy: containers, cgroups, capabilities, mounts, process isolation

## 1. Definícia

Linux namespace je kernel mechanizmus, ktorý procesu poskytne izolovaný pohľad na vybranú kategóriu systémových resources.

Procesy v rôznych namespaces môžu používať rovnaké identifikátory alebo názvy, ale odkazovať na rozdielny kernel stav. Namespace preto nevytvára nový kernel; vytvára oddelený pohľad v rámci toho istého kernelu.

## 2. Problém, ktorý rieši

Bez namespaces by všetky procesy hosta zdieľali jeden globálny pohľad na:

- process IDs,
- mount tree,
- network interfaces a routes,
- hostname,
- IPC objekty,
- user/group IDs,
- cgroup membership view,
- časové offsets.

To komplikuje izoláciu workloadov. Namespaces umožňujú, aby proces videl iba časť systémového stavu, ktorú potrebuje.

## 3. Mentálny model

```text
Jeden Linux kernel
├── namespace set A
│   ├── PID view A
│   ├── mount tree A
│   └── network stack A
└── namespace set B
    ├── PID view B
    ├── mount tree B
    └── network stack B
```

Proces patrí súčasne do jedného namespace každého podporovaného typu. Jeho izolácia je kombináciou týchto členstiev.

## 4. Hlavné typy namespaces

| Namespace | Izolovaný pohľad |
|---|---|
| PID | process ID tree a init proces |
| mount | mount points a mount propagation |
| network | interfaces, addresses, routes, sockets, firewall state |
| UTS | hostname a domain name |
| IPC | System V IPC a POSIX message queues |
| user | UID/GID mapping a capability scope |
| cgroup | pohľad na cgroup hierarchy |
| time | boot a monotonic clock offsets |

Aktuálnu podporu kernelu možno pozorovať cez namespace links procesov.

```bash
ls -l /proc/self/ns
```

Príklad:

```text
mnt -> mnt:[4026531841]
pid -> pid:[4026531836]
net -> net:[4026531840]
```

Číslo identifikuje namespace objekt v kerneli. Dva procesy s rovnakým identifikátorom daného typu zdieľajú ten istý namespace.

## 5. Vytvorenie a pripojenie

Základné system calls:

- `clone()` môže vytvoriť proces zároveň v nových namespaces,
- `unshare()` odpojí calling process od zdieľaného namespace a vytvorí nový,
- `setns()` pripojí proces alebo thread k existujúcemu namespace.

User-space nástroje:

```bash
unshare --help
nsenter --help
lsns
```

Príklad izolovaného UTS namespace:

```bash
sudo unshare --uts --fork /bin/bash
hostname isolated-host
hostname
```

Hostname sa zmení iba v novom UTS namespace. Host mimo neho si ponechá pôvodnú hodnotu.

## 6. PID namespace

PID namespace izoluje process ID numbering a process tree.

```text
Host PID namespace
└── process PID 12000
    └── container PID namespace
        └── ten istý proces viditeľný ako PID 1
```

Proces môže mať rozdielny PID v každej nadradenej úrovni PID namespaces.

```bash
cat /proc/self/status | grep NSpid
```

Prvý proces v PID namespace má PID 1 a špeciálne povinnosti:

- reaping orphaned child procesov,
- spracovanie signalov,
- lifecycle namespace.

Ak PID 1 skončí, kernel ukončí zostávajúce procesy v danom PID namespace.

### Častý problém PID 1 v kontajneri

Aplikácia spustená priamo ako PID 1 nemusí správne reapovať zombie procesy alebo očakávať odlišné signal semantics.

Preto sa niekedy používa minimalistický init proces alebo runtime option typu `--init`.

## 7. Mount namespace

Mount namespace izoluje mount table.

```bash
sudo unshare --mount --fork /bin/bash
mount --bind /tmp /mnt
findmnt /mnt
```

Bind mount vykonaný v izolovanom mount namespace nemusí byť viditeľný na hoste.

Dôležitá je mount propagation:

- `shared` — mount udalosti sa môžu propagovať medzi peers,
- `slave` — prijíma udalosti z mastera, neposiela ich späť,
- `private` — udalosti sa nepropagujú,
- `unbindable` — private a nemožno ho bind-mountnúť.

```bash
findmnt -o TARGET,PROPAGATION
```

Nesprávna propagation policy môže spôsobiť, že mount vytvorený runtimeom nie je viditeľný tam, kde sa očakáva, alebo naopak unikne do nadradeného namespace.

## 8. Network namespace

Network namespace má vlastné:

- interfaces,
- IP addresses,
- routes,
- neighbor table,
- sockets,
- port space,
- netfilter state.

Vytvorenie:

```bash
sudo ip netns add demo
sudo ip netns exec demo ip link
```

Nový network namespace má typicky iba loopback interface v stave down.

```bash
sudo ip netns exec demo ip link set lo up
```

Prepojenie s hostom cez veth pair:

```bash
sudo ip link add veth-host type veth peer name veth-demo
sudo ip link set veth-demo netns demo
sudo ip addr add 192.0.2.1/24 dev veth-host
sudo ip link set veth-host up
sudo ip netns exec demo ip addr add 192.0.2.2/24 dev veth-demo
sudo ip netns exec demo ip link set veth-demo up
```

Veth pair funguje ako virtuálny ethernetový kábel: packet zapísaný na jednom konci sa objaví na druhom.

## 9. User namespace

User namespace izoluje mapovanie UID/GID a capability scope.

Proces môže byť UID 0 vo svojom user namespace, ale mať neprivilegované UID na hoste.

```text
namespace UID 0
    ↕ mapping
host UID 1000
```

Mapovania sú viditeľné v:

```bash
cat /proc/self/uid_map
cat /proc/self/gid_map
```

User namespaces sú základom rootless containers. „Root v kontajneri“ však automaticky neznamená plný host root; oprávnenia sú viazané na user namespace a ďalšie security boundaries.

User namespace zároveň komplikuje:

- ownership bind-mounted súborov,
- device access,
- subordinate UID/GID ranges,
- filesystem podporu ID mappingu,
- interoperability so security politikami.

## 10. UTS, IPC, cgroup a time namespaces

### UTS

Izoluje hostname a NIS domain name.

### IPC

Izoluje System V IPC identifiers a POSIX message queues. Procesy v oddelených IPC namespaces nezdieľajú tieto objekty implicitne.

### cgroup namespace

Mení pohľad procesu na jeho pozíciu v cgroup hierarchy. Proces môže vidieť svoju cgroup ako root, hoci host má širšiu hierarchiu.

### time namespace

Umožňuje offsets pre určité clocks. Je užitočný pri testovaní a izolovaných environments, ale neizoluje bežný wall-clock čas ľubovoľným spôsobom.

## 11. Namespace membership procesu

```bash
ls -l /proc/<PID>/ns
lsns -p <PID>
```

Porovnanie dvoch procesov:

```bash
readlink /proc/<PID1>/ns/net
readlink /proc/<PID2>/ns/net
```

Ak identifiers nesedia, príkazy ako `ip`, `ss`, `mount` alebo `ps` spustené v jednom kontexte nemusia ukázať stav druhého.

Vstup do namespaces existujúceho procesu:

```bash
sudo nsenter -t <PID> --mount --uts --ipc --net --pid
```

`nsenter` nemení proces spätne; spustí nový command pripojený k vybraným namespaces target procesu.

## 12. Namespaces nie sú kompletný sandbox

Namespaces izolujú pohľad na resources, ale samy osebe neriešia:

- resource limits,
- syscall filtering,
- mandatory access control,
- kernel vulnerabilities,
- secrets,
- host filesystem bind mounts,
- privileged device access.

Kontajnerová izolácia typicky kombinuje:

```text
namespaces
+ cgroups
+ capabilities
+ seccomp
+ SELinux/AppArmor
+ read-only filesystems
+ runtime policy
```

Procesy stále zdieľajú jeden kernel. Kernel exploit môže prekročiť namespace boundary.

## 13. Namespace lifecycle

Namespace existuje, kým:

- v ňom existuje proces,
- alebo naň existuje otvorený file descriptor či bind mount namespace linku.

Persistovanie namespace objektu:

```bash
sudo touch /run/netns/example
sudo mount --bind /proc/<PID>/ns/net /run/netns/example
```

Nástroje ako `ip netns` spravujú podobný mechanizmus pre network namespaces.

## 14. Produkčný kontext

Kontajner runtime typicky:

1. pripraví root filesystem,
2. vytvorí alebo pripojí namespaces,
3. nastaví mounts a network,
4. aplikuje cgroups, capabilities a security policy,
5. spustí process,
6. udržiava metadata potrebné na `exec`, logs a lifecycle.

Kubernetes Pod zdieľa vybrané namespaces medzi containers v Pode, najmä network namespace. Preto containers v jednom Pode používajú rovnaké IP a port space.

## 15. Troubleshooting scenár

Proces údajne počúva na porte 8080, ale na hoste ho `ss -lntp` neukáže.

Postup:

```bash
readlink /proc/<PID>/ns/net
readlink /proc/self/ns/net
sudo nsenter -t <PID> -n ss -lntp
sudo nsenter -t <PID> -n ip addr
sudo nsenter -t <PID> -n ip route
```

Ak proces beží v inom network namespace, hostový socket inventory nie je autoritatívny pre jeho namespace.

Ďalší scenár: súbor je viditeľný v kontajneri, ale nie na hoste na očakávanom path. Porovnaj mount namespaces a efektívne mount tables cez `findmnt` spustený s `nsenter`.

## 16. Časté omyly

### „Container je virtuálny stroj“

Nie. Kontajnerové procesy používajú host kernel, ale majú kombináciu izolovaných namespace pohľadov a ďalších kontrol.

### „PID 1 v kontajneri je host PID 1“

Nie. Je PID 1 iba v danom PID namespace a na hoste má iný PID.

### „Root v user namespace je host root“

Nie automaticky. Privileges sú viazané na user namespace a host mapping.

### „Network namespace má iba inú IP“

Má vlastný celý network stack view vrátane routes, sockets a firewall state.

### „Namespace zaručuje bezpečnosť“

Je iba jedna vrstva izolácie. Potrebuje doplnenie resource, syscall a access-control mechanizmami.

## 17. Kontrolné otázky

1. Čo presne namespace izoluje a čo neizoluje?
2. Prečo môže mať jeden proces viac PID hodnôt?
3. Aké povinnosti má PID 1 v PID namespace?
4. Ako veth pair prepája dva network namespaces?
5. Prečo je mount propagation dôležitá?
6. Ako user namespace umožňuje rootless containers?
7. Prečo `ss` na hoste nemusí ukázať sockets kontajnera?
8. Ktoré ďalšie security mechanizmy musia namespaces dopĺňať?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Cron a systemd timers](cron-and-systemd-timers.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Linux Control Groups — cgroups →](cgroups.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
