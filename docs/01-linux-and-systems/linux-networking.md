# Linux Networking

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Kernel a user space](kernel-and-user-space.md), [Procesy, thready, PID a signals](processes-threads-pid-signals.md)
- Súvisiace témy: TCP/IP, DNS, routing, firewalls, network namespaces, containers

## 1. Definícia

Linux networking je súbor kernelových dátových štruktúr, protocol implementations a user-space nástrojov, ktoré riadia interfaces, addresses, routes, neighbor discovery, sockets, packet filtering a transport dát.

Aplikácia typicky neodosiela packet priamo na interface. Vytvorí socket a kernel vykoná routing, neighbor resolution, segmentation, filtering a odovzdanie driveru.

## 2. Packet path

Zjednodušený outbound tok:

```text
Application
  ↓ socket syscall
TCP/UDP layer
  ↓
Routing decision
  ↓
Netfilter / policy
  ↓
Neighbor resolution
  ↓
Network interface driver
  ↓
Network
```

Inbound tok ide opačne a kernel podľa destination address, portu a socket state rozhodne, ktorému socketu dáta doručí.

## 3. Interfaces

Inventár:

```bash
ip link
ip -br link
ip addr
ip -br addr
```

Interface môže byť:

- fyzický NIC,
- loopback,
- bridge,
- VLAN,
- bond,
- veth pair,
- tunnel,
- virtual interface cloud platformy.

Stavy treba odlišovať:

- administratively up/down,
- carrier/link state,
- pridelená IP adresa,
- routability.

Interface `UP` bez carrieru alebo route nemusí mať konektivitu.

## 4. IP addresses a prefixes

```bash
ip addr show dev eth0
```

Príklad:

```text
192.0.2.10/24
```

Prefix `/24` určuje network mask. Kernel z neho odvodí connected route pre lokálnu sieť.

Viac IP adries môže byť priradených jednému interface. IPv6 bežne používa link-local adresu aj globálne addresses.

Loopback:

```text
127.0.0.1/8
::1/128
```

Loopback komunikácia neprechádza fyzickou sieťou, ale stále používa socket a protocol stack.

## 5. Routing table

```bash
ip route
ip -6 route
ip route get 198.51.100.20
```

Route obsahuje destination prefix, next hop, interface, metric a prípadne source policy.

Príklad:

```text
default via 192.0.2.1 dev eth0
192.0.2.0/24 dev eth0 proto kernel scope link src 192.0.2.10
```

Kernel vyberá najšpecifickejší prefix. Default route sa použije, keď neexistuje presnejšia route.

`ip route get` je veľmi užitočný, pretože ukáže konkrétne routing rozhodnutie vrátane zvoleného source address.

## 6. Neighbor discovery: ARP a NDP

Pri komunikácii v lokálnom L2 segmente potrebuje host mapovať next-hop IP na link-layer address.

```bash
ip neigh
```

IPv4 používa ARP; IPv6 Neighbor Discovery Protocol.

Neighbor states ako `REACHABLE`, `STALE`, `DELAY`, `FAILED` pomáhajú diagnostikovať lokálne L2 problémy.

Ak route existuje, ale neighbor resolution zlyhá, packet sa nemusí dostať ani k gateway.

## 7. Sockets a ports

Socket reprezentuje communication endpoint.

```bash
ss -lntup
ss -tan
ss -s
```

Časté flags:

- `-l` listening,
- `-n` bez name resolution,
- `-t` TCP,
- `-u` UDP,
- `-p` process,
- `-a` všetky sockets.

Listening socket:

```text
Local address 0.0.0.0:8080
```

znamená bind na všetky IPv4 local addresses. `127.0.0.1:8080` je dostupné iba lokálne. `[::]:8080` je IPv6 wildcard a dual-stack správanie závisí od socket option a sysctl.

## 8. TCP state

Časté stavy:

- `LISTEN`,
- `SYN-SENT`,
- `SYN-RECV`,
- `ESTAB`,
- `FIN-WAIT-1/2`,
- `CLOSE-WAIT`,
- `TIME-WAIT`.

Veľa `CLOSE-WAIT` často znamená, že peer spojenie ukončil, ale lokálna aplikácia nezavrela socket. Veľa `TIME-WAIT` nie je automaticky chyba; chráni TCP sequence space po aktívnom close.

## 9. DNS resolution

Aplikácia môže používať resolver podľa `/etc/nsswitch.conf`, `/etc/resolv.conf`, systemd-resolved alebo lokálneho caching resolvera.

Diagnostika:

```bash
getent hosts example.com
resolvectl query example.com
dig example.com
cat /etc/resolv.conf
```

`getent` testuje Name Service Switch cestu podobnú bežnej aplikácii. `dig` testuje DNS priamo a môže obísť niektoré NSS sources, napríklad `/etc/hosts`.

Rozlíš:

```text
DNS name resolution
  ≠
network reachability
  ≠
application availability
```

## 10. Network configuration managers

Interfaces môže konfigurovať:

- NetworkManager,
- systemd-networkd,
- netplan ako generačná vrstva,
- distribution-specific scripts,
- cloud-init,
- orchestration platforma.

Aktuálny runtime stav zobrazuje `ip`, ale persistent desired state môže byť uložený inde. Ručná zmena cez `ip addr add` často neprežije reboot a môže byť prepísaná managerom.

## 11. Netfilter a firewall

Linux packet filtering typicky používa netfilter framework cez nftables alebo legacy iptables frontend.

```bash
sudo nft list ruleset
sudo iptables -S
```

Treba vedieť, ktorý stack host reálne používa. Iptables command môže byť frontend nad nft backendom.

Firewall decision môže závisieť od:

- direction a hook,
- source/destination,
- protocol a port,
- connection tracking state,
- interface,
- mark,
- namespace.

„Port je otvorený“ môže znamenať iba listening socket; firewall alebo upstream security policy ho stále môže blokovať.

## 12. Packet capture

```bash
sudo tcpdump -ni any host 198.51.100.20
sudo tcpdump -ni eth0 port 443
sudo tcpdump -ni any 'tcp[tcpflags] & tcp-syn != 0'
```

Packet capture odpovedá, či packet prešiel konkrétnym observation pointom.

Interpretácia TCP handshake:

```text
SYN od klienta
SYN-ACK od servera
ACK od klienta
```

- SYN odchádza, odpoveď neprichádza: route, firewall, remote service alebo return path,
- SYN prichádza, server posiela RST: nič nepočúva alebo explicit reject,
- handshake prebehne, aplikácia timeoutuje: problém vyššej vrstvy.

Capture môže byť ovplyvnený offloadingom, namespaces a šifrovaním. Miesto capture je kritické.

## 13. ICMP a `ping`

```bash
ping -c 4 192.0.2.1
```

Ping testuje ICMP echo, nie dostupnosť konkrétnej TCP služby. ICMP môže byť filtrované aj pri funkčnej aplikácii.

Užitočné nástroje:

```bash
tracepath example.com
traceroute example.com
mtr example.com
```

Trasa je smerovo a časovo závislá. Chýbajúca odpoveď jedného hopu nemusí znamenať packet loss pre forward traffic; router môže iba neodpovedať na probe.

## 14. MTU

Maximum Transmission Unit určuje maximálnu veľkosť L3 packetu na linke bez fragmentácie.

```bash
ip link show dev eth0
tracepath example.com
```

MTU mismatch alebo blokované ICMP Packet Too Big môže spôsobiť, že malé requests fungujú a veľké prenosy timeoutujú.

Typické pri:

- VPN,
- tunnels,
- overlays,
- cloud networking,
- containers.

## 15. Forwarding a NAT

IP forwarding umožní hostu routovať packets medzi interfaces.

```bash
sysctl net.ipv4.ip_forward
```

NAT mení addresses alebo ports, typicky cez netfilter.

Dôležité:

- forwarding route nestačí bez povoleného kernel forwarding,
- firewall forward chain môže traffic blokovať,
- return path musí byť routovateľná,
- connection tracking drží state NAT mappingu.

## 16. Network namespaces

Každý network namespace má vlastné:

- interfaces,
- addresses,
- routes,
- neighbor table,
- sockets,
- firewall state.

Preto `ss` alebo `ip route` na hoste nemusí ukázať stav kontajnera.

```bash
ip netns list
ip netns exec <name> ip addr
```

Podrobne bude namespace mechanizmus rozpracovaný v samostatnej kapitole.

## 17. Diagnostický postup

Aplikácia sa nevie pripojiť na `db.example:5432`:

```bash
getent hosts db.example
ip route get <resolved-ip>
ip neigh
ss -tan dst <resolved-ip>:5432
nc -vz db.example 5432
sudo tcpdump -ni any host <resolved-ip> and port 5432
```

Postup po vrstvách:

1. name resolution,
2. zvolená IP a address family,
3. route a source address,
4. local firewall,
5. packet odchod,
6. remote response a return path,
7. TCP handshake,
8. TLS/application protocol.

## 18. Časté omyly

### „Keď ping funguje, aplikácia funguje“

Nie. Ping netestuje port, TLS ani application protocol.

### „Keď socket počúva, je dostupný zo siete“

Nie. Môže byť bindnutý iba na loopback alebo blokovaný firewallom.

### „`dig` dokazuje, že aplikácia vyrieši rovnaké meno rovnako“

Nie vždy. Aplikácia môže používať NSS, cache, search domains alebo iný resolver path.

### „Default route sa použije vždy“

Nie. Presnejšia route alebo policy routing má prednosť.

### „Tcpdump na hoste vidí všetko“

Nie nevyhnutne. Traffic môže byť v inom namespace, na inom interface alebo spracovaný offloadom.

## 19. Kontrolné otázky

1. Aký je rozdiel medzi interface up, carrier a routability?
2. Ako kernel vyberá route?
3. Načo slúži ARP/NDP po routing decision?
4. Aký je rozdiel medzi listening na `127.0.0.1` a `0.0.0.0`?
5. Čo typicky znamená veľa `CLOSE-WAIT` sockets?
6. Prečo `getent hosts` a `dig` nemusia dať rovnaký diagnostický význam?
7. Ako tcpdump pomáha lokalizovať vrstvu zlyhania?
8. Prečo malé packets môžu fungovať pri MTU probléme, ale veľké nie?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Memory a CPU fundamentals](cpu-and-memory-fundamentals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: SSH →](ssh.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
