# Linux namespaces

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Kernel a user space](kernel-and-user-space.md), [Procesy, thready, PID a signals](processes-threads-pid-signals.md), [Linux networking](linux-networking.md)
- Súvisiace témy: containers, cgroups, capabilities, mounts, process isolation, user namespaces

## 1. Definícia

Linux namespace je kernelový objekt, ktorý oddeľuje **pohľad procesu na konkrétnu kategóriu systémového stavu**. Procesy môžu používať rovnaký kernel a rovnaký hardware, ale vidieť odlišné PID čísla, mount tree, network stack, hostname alebo UID/GID mapovanie.

Namespace nevytvára nový operačný systém ani nový kernel. Vytvára oddelenú skupinu identifikátorov, objektov alebo pravidiel v rámci jedného kernelu.

```text
jeden Linux kernel
  ├── proces A → PID ns A, mount ns A, net ns A, user ns A
  └── proces B → PID ns B, mount ns B, net ns B, user ns B
```

Izolácia procesu je výsledkom **kombinácie** namespace členstiev. Dva procesy môžu zdieľať network namespace, ale mať rozdielny mount namespace, alebo naopak.

## 2. Čo namespaces riešia a čo nie

Bez namespaces by všetky procesy videli jeden globálny process tree, jednu mount table a jeden network stack. To by znemožnilo, aby viac workloadov bezpečne používalo rovnaké názvy, porty alebo PID čísla bez vzájomného konfliktu.

Namespaces poskytujú najmä:

- **Oddelenú identitu objektov** — PID `1`, hostname `app` alebo port `8080` môže existovať nezávisle v rôznych namespaces.
- **Obmedzený pohľad** — proces nemusí vidieť hostové procesy, mounty alebo interfaces, aj keď kernel ich spravuje.
- **Samostatné konfiguračné tabuľky** — network namespace má vlastné routes, firewall state a sockets; mount namespace má vlastnú mount topology.
- **Základ kontajnerov** — runtime kombinuje viac namespaceov, aby proces dostal izolovaný systémový pohľad.

Namespaces samy neposkytujú resource limity, syscall filtering ani úplnú bezpečnostnú hranicu proti kernel exploitom. Tie riešia ďalšie mechanizmy, napríklad cgroups, capabilities, seccomp a SELinux/AppArmor.

## 3. Namespace set procesu

Každý thread patrí v danom okamihu do jedného namespace objektu každého podporovaného typu. Process-wide pohľad vzniká preto, že thready jedného procesu zvyčajne zdieľajú rovnaký namespace set, hoci kernelové API umožňuje pri niektorých typoch jemnejšie správanie.

```bash
ls -l /proc/self/ns
```

Príklad:

```text
mnt  -> mnt:[4026531841]
pid  -> pid:[4026531836]
net  -> net:[4026531840]
user -> user:[4026531837]
```

Číslo v hranatých zátvorkách identifikuje konkrétny namespace objekt. Ak dva procesy majú pri danom type rovnaký identifikátor, zdieľajú rovnaký namespace objekt tohto typu.

## 4. Hlavné typy namespaces

| Typ | Izolovaný stav | Praktický dôsledok |
|---|---|---|
| PID | PID numbering a process hierarchy | rovnaký proces môže mať host PID a odlišný container PID |
| Mount | mount table a propagation | bind mount môže byť viditeľný iba v jednom kontejnere |
| Network | interfaces, routes, sockets, ports, conntrack a firewall | viac workloadov môže nezávisle počúvať na rovnakom porte |
| UTS | hostname a NIS domain name | proces môže vidieť vlastný hostname |
| IPC | System V IPC a POSIX message queues | workloady nezdieľajú IPC identifikátory implicitne |
| User | UID/GID mapping a capability scope | namespace root nemusí byť host root |
| Cgroup | pohľad na cgroup hierarchy | proces môže vidieť svoju subtree ako root |
| Time | offsety niektorých clocks | izolované testovanie boot/monotonic času |

Izolovaný pohľad neznamená vždy izolovanú fyzickú resource. Napríklad dva network namespaces používajú ten istý NIC hardware cez virtuálne interfaces a hostový routing alebo bridge.

## 5. Vytvorenie a pripojenie namespaceov

Základné kernelové operácie sú `clone()`, `unshare()` a `setns()`. Každá rieši inú časť lifecycle.

- **`clone()`** — vytvorí nový task a môže ho priamo umiestniť do nových namespaces.
- **`unshare()`** — odpojí calling process alebo thread od vybraného zdieľaného kontextu a vytvorí nový namespace.
- **`setns()`** — pripojí calling thread k existujúcemu namespace objektu reprezentovanému file descriptorom.

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

Zmena hostname ovplyvní iba procesy v novom UTS namespace. Host a procesy v inom UTS namespace zostanú nezmenené.

## 6. Namespace nesting

Niektoré namespace typy, najmä PID a user namespaces, podporujú hierarchiu. Proces v nadradenom namespace môže vidieť objekty v descendant namespace, ale proces v descendant namespace nemusí vidieť nadradený svet.

```text
host PID namespace
  └── container PID namespace
       └── nested PID namespace
```

Nesting nie je iba vizuálne usporiadanie. Ovplyvňuje, ktoré PID číslo proces vidí, kde platia capabilities a aké mapovania UID/GID možno vytvoriť.

Pri diagnostike preto nestačí otázka „je proces v namespace?“. Treba vedieť, v ktorom konkrétnom objekte je, aký má parent namespace a z ktorého kontextu ho pozorujeme.

## 7. PID namespace

PID namespace izoluje numbering procesov a ich hierarchický pohľad. Jeden kernelový task môže byť z hosta viditeľný ako PID `12000`, ale vo vnútri kontajnera ako PID `1`.

```text
host view:       PID 12000
container view:  PID 1
```

Kernel udržiava PID identitu pre každú relevantnú úroveň namespace hierarchy. NSpid možno pozorovať cez:

```bash
cat /proc/<pid>/status | grep '^NSpid'
```

Proces v child PID namespace nevidí procesy existujúce iba v parent namespace. Hostový administrátor však typicky vidí descendant procesy a môže ich diagnostikovať podľa host PID.

## 8. PID 1 semantics v namespace

Prvý proces v PID namespace dostane PID `1` a má špeciálnu úlohu. Adoptuje orphaned descendants a musí ich reapovať, aby nezostávali zombie entries.

PID 1 má aj odlišné signal semantics. Niektoré signály, pre ktoré nemá handler, nemusia mať rovnaký defaultný efekt ako pri bežnom procese, pretože neúmyselné ukončenie namespace initu by zničilo celý namespace process tree.

Ak PID 1 v PID namespace skončí, kernel ukončí zostávajúce procesy v tomto namespace. Kontajner runtime preto považuje lifecycle PID 1 za lifecycle kontajnera.

Aplikácia spustená priamo ako PID 1 musí:

- reapovať child procesy,
- preposielať alebo spracovať shutdown signals,
- nenechať shell wrapper zadržať `SIGTERM`,
- ukončiť celý child tree pred runtime timeoutom.

Minimalistický init alebo runtime voľba typu `--init` rieši reaping a signal forwarding pre aplikácie, ktoré nie sú navrhnuté ako namespace init.

## 9. Mount namespace

Mount namespace izoluje mount table procesu. Dva procesy môžu mať rovnaký pathname `/data`, ale pod ním vidieť iný filesystem alebo bind mount.

```bash
sudo unshare --mount --fork /bin/bash
mount --bind /tmp /mnt
findmnt /mnt
```

Mount namespace nekopíruje obsah filesystému. Vytvára samostatný pohľad na väzby medzi mount objektmi a mount points.

Pri vytvorení namespace sa počiatočná mount topology typicky odvodená od parenta stane východiskom. Neskoršie zmeny sa môžu alebo nemusia propagovať podľa propagation policy.

## 10. Mount propagation

Propagation určuje, či sa nová mount udalosť prenesie medzi prepojenými mount trees. Je kritická pri kontajnerových runtimeoch, volume pluginoch a nested mountoch.

- **Shared** — mount a unmount udalosti sa propagujú medzi členmi rovnakej peer group.
- **Slave** — mount prijíma udalosti z mastera, ale svoje zmeny neposiela späť.
- **Private** — udalosti sa medzi stromami nešíria ani jedným smerom.
- **Unbindable** — správa sa ako private a navyše ho nemožno bind-mountnúť do iného miesta.

```bash
findmnt -o TARGET,SOURCE,FSTYPE,PROPAGATION
```

Nesprávna policy môže vytvoriť dve opačné chyby. Runtime mount sa nemusí objaviť v kontajneri, alebo sa naopak mount z kontajnerového kontextu môže propagovať do hostovej topology.

Propagation je vlastnosť mount objektu, nie všeobecný prepínač celého namespace. Pri diagnostike treba pozrieť konkrétny path a jeho parent propagation chain.

## 11. Root filesystem a `pivot_root`

Kontajner potrebuje okrem mount namespace aj vlastný root filesystem view. Runtime pripraví root tree a následne zmení root procesu pomocou mechanizmu ako `pivot_root()` alebo kontrolovaného `chroot()` v kombinácii s mount izoláciou.

`chroot` sám osebe nie je bezpečnostný sandbox. Privilegovaný proces môže mať možnosti úniku, ak chýbajú mount namespace, capability reduction a ďalšie kontroly.

Izolovaný root preto typicky vzniká ako kombinácia:

```text
mount namespace
+ prepared root filesystem
+ pivot_root/chroot
+ read-only a masked paths
+ capabilities/seccomp/LSM
```

Path viditeľný v kontajneri nemusí mať jednoduchý hostový ekvivalent. Overlay layers, bind mounts a volume plugins môžu vytvoriť viacvrstvový backing path.

## 12. Network namespace

Network namespace vlastní samostatný network stack state. Má vlastné interfaces, adresy, routes, neighbor cache, sockets, port space, netfilter rules a connection tracking tabuľky.

Nový network namespace typicky obsahuje iba loopback interface, ktorý môže byť administratívne down:

```bash
sudo ip netns add demo
sudo ip netns exec demo ip link set lo up
sudo ip netns exec demo ip -br addr
```

Socket počúvajúci na `0.0.0.0:8080` v jednom network namespace nekoliduje s rovnakým portom v inom namespace. Oba však stále potrebujú cestu k fyzickej alebo virtuálnej sieti.

## 13. Veth pair, bridge a packet path

Veth pair je dvojica virtuálnych ethernetových interfaces. Frame vložený na jednom konci sa objaví na druhom konci, podobne ako cez virtuálny kábel.

```bash
sudo ip link add veth-host type veth peer name veth-demo
sudo ip link set veth-demo netns demo
```

Typický kontajnerový path:

```text
container process
  ↓ socket
container net namespace
  ↓ veth-container
veth-host
  ↓ bridge / host routing / firewall / NAT
physical or overlay network
```

Každý observation point ukazuje inú časť packetu. Hostový `tcpdump -i any` nemusí automaticky nahradiť capture vo vnútri namespace, najmä pri NAT, bridge hooks, offloadoch alebo overlay encapsulation.

## 14. Network namespace a DNS

Network namespace izoluje kernelový network stack, ale resolver configuration je prevažne filesystémová user-space konfigurácia. Súbor `/etc/resolv.conf` preto závisí od mount/root filesystem view, nie iba od network namespace.

Kontajner môže mať správnu route, ale nesprávny resolver súbor. Naopak, môže vyriešiť meno cez lokálny cache daemon, ku ktorému však z jeho network namespace neexistuje route alebo socket.

Pri diagnostike treba oddeliť:

- resolver configuration v mount namespace,
- network path k DNS serveru v network namespace,
- NSS policy aplikácie,
- prípadný sidecar alebo local DNS proxy.

## 15. User namespace

User namespace izoluje mapovanie UID/GID a capability scope. Proces môže mať UID `0` vo svojom user namespace, ale mapovať sa na neprivilegovaný host UID, napríklad `100000`.

```text
namespace UID 0
  ↕ uid_map
host UID 100000
```

Mapovania:

```bash
cat /proc/<pid>/uid_map
cat /proc/<pid>/gid_map
```

Capabilities procesu platia voči objektom, nad ktorými má príslušný user namespace autoritu. Root v child user namespace preto nie je automaticky host root.

User namespace je základ rootless kontajnerov, ale prináša prevádzkové dôsledky:

- bind-mounted súbor môže mať v host view neočakávané číselné ownership,
- subordinate UID/GID ranges musia byť pridelené a spravované,
- nie všetky filesystems a operation podporujú rovnaké ID-mapping semantics,
- device a kernel-global operácie zostávajú obmedzené,
- security policy musí rozumieť namespace mapovaniu.

## 16. Subordinate UID/GID ranges

Rootless runtime potrebuje rozsah hostových UID/GID, ktoré môže mapovať do kontajnerového namespace. Tieto rozsahy bývajú evidované v `/etc/subuid` a `/etc/subgid`.

```text
alice:100000:65536
```

Takýto záznam umožňuje používateľovi `alice` mapovať namespace identity na vyhradený hostový rozsah. Zlé alebo prekrývajúce sa ranges môžu viesť ku konfliktom ownershipu a narušeniu izolácie medzi používateľmi.

Mapovanie neznamená, že proces môže svojvoľne používať všetky host UID. Kernel validuje, ktoré rozsahy môže neprivilegovaný proces zapísať do namespace mapy.

## 17. UTS namespace

UTS namespace izoluje hostname a NIS domain name. Je vhodný na to, aby workload dostal vlastnú host identity bez zmeny hostového mena.

Hostname nie je silná bezpečnostná identita. Aplikácia ho môže používať pre logy alebo service discovery, ale autentizácia má stáť na kryptografických credentials a dôveryhodnom inventory.

Zmena hostname v UTS namespace nemení DNS records ani network routes. Je to lokálna hodnota kernelového pohľadu.

## 18. IPC namespace

IPC namespace izoluje System V IPC objekty a POSIX message queues. Procesy v rôznych IPC namespaces preto implicitne nezdieľajú message queues, semaphore sets ani shared-memory identifiers tejto kategórie.

Nie všetka inter-process communication patrí do IPC namespace. Unix sockets v filesysteme závisia aj od mount namespace a permissions; network sockets patria do network namespace; zdieľaný bind mount môže znovu vytvoriť komunikačný kanál medzi workloadmi.

Izolácia jednej IPC vrstvy preto neznamená úplné odstránenie všetkých komunikačných ciest.

## 19. Cgroup namespace

Cgroup namespace mení, ako proces vidí svoju pozíciu v cgroup hierarchy. Proces môže v `/proc/self/cgroup` vidieť svoju cgroup ako root, hoci host má nad ňou širší strom.

Tento namespace nemení samotné resource limity. Limity a accounting spravuje cgroup controller hierarchy; namespace iba virtualizuje pohľad na path.

Cgroup namespace znižuje únik hostovej topológie a pomáha kontajnerom interpretovať vlastný cgroup kontext. Diagnostika na hoste však musí používať hostový pohľad, ak potrebuje vidieť parent limits a sibling workloads.

## 20. Time namespace

Time namespace umožňuje offsety pre vybrané clocks, najmä monotonic a boot-time pohľady. Je užitočný pri testovaní suspend/uptime správania alebo pri izolovaných lifecycle modeloch.

Nejde o univerzálnu možnosť nastaviť ľubovoľný wall clock pre každý kontajner. Realtime clock a časová synchronizácia majú širšie systémové a bezpečnostné dôsledky.

Aplikácia má pri korelácii incidentov rozlišovať wall-clock timestamp, monotonic duration a namespace-specific offset.

## 21. Namespace lifecycle

Namespace objekt existuje, kým naň zostáva referencia. Referenciou môže byť proces, otvorený file descriptor alebo bind mount na namespace link z `/proc/<pid>/ns/`.

```text
process membership
or open namespace FD
or bind-mounted namespace handle
  ↓
namespace remains alive
```

Keď posledná referencia zanikne, kernel môže namespace objekt odstrániť. Preto dočasný namespace vytvorený cez `unshare` typicky zanikne po skončení posledného procesu.

Named network namespaces spravované cez `ip netns` používajú persistovaný handle, aby namespace prežil aj bez bežiaceho procesu. Samotný názov je user-space referencia na kernelový objekt.

## 22. Vstup do existujúceho namespace

Namespace links v `/proc/<pid>/ns/` možno otvoriť a použiť s `setns()`. Nástroj `nsenter` tento mechanizmus zjednodušuje.

```bash
sudo nsenter -t <pid> --mount --uts --ipc --net --pid -- /bin/bash
```

`nsenter` nespája existujúci shell spätne do target namespace. Spustí nový proces s vybranými namespace membership.

PID namespace má zvláštnosť: vstup ovplyvní PID namespace budúcich child procesov, preto nástroj typicky vytvorí nový command. Pri diagnostike treba porovnať `/proc/self/ns/*` v novom procese, nie predpokladať úspech podľa promptu.

## 23. Namespaces a kontajner runtime

Kontajner runtime typicky vykoná koordinovaný lifecycle:

1. **Pripraví root filesystem** — image layers, writable layer a volumes vytvoria budúci mount view.
2. **Vytvorí alebo pripojí namespaces** — podľa konfigurácie môže niektoré zdieľať s hostom alebo iným kontajnerom.
3. **Nastaví network path** — veth, bridge, routes, firewall/NAT alebo CNI plugin.
4. **Aplikuje UID/GID mapping** — pri rootless alebo user-namespaced modeli.
5. **Pripojí cgroup a security policy** — resource limits, capabilities, seccomp a LSM labels.
6. **Spustí namespace PID 1** — jeho exit sa stane lifecycle eventom kontajnera.
7. **Udržiava handles a metadata** — potrebné pre `exec`, logs, inspect, pause a cleanup.

Kontajner preto nie je iba proces spustený s jedným `unshare`. Je to koordinovaný súbor kernelových objektov a user-space lifecycle state.

## 24. Namespace sharing v Kubernetes Pode

Kontajnery v jednom Kubernetes Pode typicky zdieľajú network namespace. Používajú rovnakú Pod IP a rovnaký port space, preto dva kontajnery v Pode nemôžu nezávisle bindnúť rovnakú adresu a port.

Mount namespace je typicky samostatný pre každý kontajner, hoci volumes môžu zdieľať rovnaký backing storage. PID namespace môže byť oddelený alebo zdieľaný podľa Pod konfigurácie.

Toto vysvetľuje viacero praktických javov:

- sidecar komunikuje s aplikáciou cez `localhost`,
- všetky kontajnery zdieľajú Pod network policy identity,
- filesystem path v jednom kontajneri nemusí existovať v druhom bez volume mountu,
- process inventory závisí od PID namespace sharing nastavenia.

## 25. Namespaces nie sú kompletný sandbox

Namespace obmedzuje viditeľnosť a menný priestor, nie všetky možné operácie. Procesy stále volajú ten istý hostový kernel a zdieľajú jeho attack surface.

Kompletná kontajnerová hranica typicky skladá:

```text
namespaces          izolovaný pohľad
cgroups             accounting a resource control
capabilities        obmedzenie root právomocí
seccomp              syscall allow/deny policy
SELinux/AppArmor     mandatory access control
read-only mounts     zmenšenie writable surface
runtime policy       device, privilege a lifecycle rules
```

Izoláciu môžu oslabiť:

- `--privileged` alebo široké capabilities,
- host PID/network namespace sharing,
- writable host filesystem bind mounts,
- host device passthrough,
- neobmedzený Docker/container runtime socket,
- kernel vulnerability,
- nebezpečné proc/sysfs mounty.

„Je to v kontajneri“ preto nie je dôkaz least privilege.

## 26. Diagnostika namespace membership

Základný inventár:

```bash
lsns
lsns -p <pid>
ls -l /proc/<pid>/ns
readlink /proc/<pid>/ns/net
readlink /proc/self/ns/net
```

Pri porovnaní dvoch procesov treba kontrolovať každý relevantný typ. Rovnaký network namespace nevylučuje rozdielny mount alebo user namespace.

Užitočný diagnostický vzor:

```bash
sudo nsenter -t <pid> -n ip -br addr
sudo nsenter -t <pid> -n ip route
sudo nsenter -t <pid> -n ss -lntup
sudo nsenter -t <pid> -m findmnt
sudo nsenter -t <pid> -p -m ps -ef
```

Príkaz má byť spustený v namespace, ktorý vlastní skúmaný stav. Hostový `ss`, `mount` alebo `ps` môže byť správny pre host, ale nesprávny observation point pre kontajner.

## 27. Troubleshooting: port existuje v kontajneri, nie na hoste

Aplikácia tvrdí, že počúva na porte `8080`, ale hostový `ss -lntp` ju nezobrazuje.

1. **Zisti host PID aplikácie** — runtime inspect alebo cgroup tree poskytne target proces.
2. **Porovnaj network namespace IDs** — odlišné IDs vysvetlia rozdielny socket inventory.
3. **Spusti `ss` v target namespace** — potvrď bind address a listening state.
4. **Skontroluj veth a routes** — listening socket ešte nevytvára hostovú alebo externú reachability.
5. **Skontroluj publish/NAT/forwarding policy** — port môže byť interný iba pre namespace alebo Pod.
6. **Capture na správnych bodoch** — kontajner interface, host veth, bridge a external NIC môžu ukázať, kde packet zmizol.

```bash
sudo nsenter -t <pid> -n ss -lntp
sudo nsenter -t <pid> -n ip route
```

## 28. Troubleshooting: ownership bind mountu nesedí

Kontajner vidí súbor ako UID `1000`, zatiaľ čo host ho zobrazuje ako UID `101000`.

1. **Over user namespace ID** — porovnaj `/proc/<pid>/ns/user` s hostom.
2. **Prečítaj `uid_map` a `gid_map`** — zisti presný preklad identity.
3. **Over mount backing path** — bind mount môže obchádzať image ownership model.
4. **Over idmapped mount alebo runtime mapping support** — filesystem a runtime musia podporovať použitý model.
5. **Nemeň ownership naslepo z hosta** — môžeš poškodiť mapovanie pre iný workload alebo hostového používateľa.

Číselné UID/GID treba vždy interpretovať v konkrétnom user namespace kontexte.

## 29. Časté omyly

### „Kontajner má vlastný kernel“

Bežný Linux kontajner používa hostový kernel. Namespaces oddeľujú vybrané pohľady a objekty, ale syscall implementácia a kernel vulnerability surface zostávajú spoločné.

### „PID 1 v kontajneri je host PID 1“

Nie. Rovnaký task môže mať PID `1` v child namespace a iné PID v host namespace. Host PID 1 zostáva init systému hosta.

### „Nový network namespace automaticky má internet“

Nový namespace má izolovaný stack, ale potrebuje interface, address, route, neighbor path, forwarding a prípadne NAT/firewall policy.

### „Root v user namespace je root na hoste“

Capabilities sú viazané na user namespace scope a UID je mapované na host identity. Nebezpečné bind mounts, devices alebo kernel chyby však môžu hranicu oslabiť.

### „Mount namespace znamená oddelené dáta“

Oddeľuje mount topology, nie automaticky backing storage. Dva namespace views môžu bind-mountovať rovnaký inode alebo volume.

### „Hostový diagnostický príkaz vidí celý kontajnerový stav“

Host vidí hostový namespace pohľad. Socket, route, mount alebo PID informácia môže byť relevantná iba po vstupe do target namespace.

## 30. Kontrolné otázky

1. Čo presne namespace izoluje a prečo nevytvára nový kernel?
2. Prečo je izolácia procesu kombináciou viacerých namespace typov?
3. Ako môže mať jeden task rozdielny PID na hoste a v kontajneri?
4. Aké povinnosti má PID 1 v PID namespace?
5. Prečo mount namespace neznamená automaticky samostatné dáta?
6. Ako mount propagation ovplyvňuje viditeľnosť nested mountov?
7. Čo vlastní network namespace a čo doň nepatrí?
8. Ako veth pair prepája dva network namespaces?
9. Prečo root v user namespace nemusí byť host root?
10. Akú úlohu majú subordinate UID/GID ranges?
11. Čo udržiava namespace objekt živý po skončení pôvodného procesu?
12. Prečo namespaces bez cgroups, capabilities a LSM netvoria kompletný sandbox?

## 31. Zhrnutie

Linux namespaces rozdeľujú pohľad procesov na vybrané kernelové resources. PID, mount, network, user a ďalšie namespaces umožňujú izolované identity, topology a konfiguračné tabuľky bez spustenia samostatného kernelu.

Praktická izolácia vzniká až kombináciou namespace membership, cgroup limits, capability reduction, syscall policy, mandatory access control a bezpečných mount/device pravidiel. Pri diagnostike musí byť každý príkaz spustený v namespace, ktorý vlastní skúmaný stav; inak môže byť pozorovanie správne, ale pre nesprávny systémový pohľad.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Cron a systemd timers](cron-and-systemd-timers.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: cgroups →](cgroups.md)
<!-- KNOWLEDGE-NAVIGATION:END -->