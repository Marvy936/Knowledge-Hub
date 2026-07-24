# Linux networking

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Linux and Systems
- Predpoklady: [Kernel a user space](kernel-and-user-space.md), [Procesy, thready, PID a signals](processes-threads-pid-signals.md)
- Súvisiace témy: TCP/IP, DNS, routing, firewalls, network namespaces, containers

## 1. Mentálny model

Linux networking je kombinácia kernelového protocol stacku, interfaces, routing tables, neighbor caches, sockets, filtering rules a user-space konfigurácie. Aplikácia typicky nevytvára packet priamo; vytvorí socket a kernel rozhodne, ako sa dáta preložia na packet a ktorou cestou odídu.

```text
Name
  ↓ resolver
Destination IP
  ↓ routing + source selection
Next hop
  ↓ ARP/NDP
Link-layer destination
  ↓ netfilter / qdisc / driver
Network
  ↓
Remote host → transport socket → application protocol
```

Diagnostika preto musí postupovať po vrstvách. Úspešný DNS lookup nepreukazuje routing, úspešný TCP handshake nepreukazuje TLS a otvorený listening socket nepreukazuje dostupnosť zo vzdialenej siete.

## 2. Network namespace

Každý network namespace má vlastné interfaces, addresses, routing tables, neighbor cache, sockets, conntrack a firewall state. Host, kontajner a Pod preto môžu vidieť úplne odlišnú sieťovú realitu.

```bash
ip netns list
ip netns exec <name> ip addr
nsenter -t <PID> -n ip route
```

Pred interpretáciou výstupu `ip`, `ss`, `nft` alebo `tcpdump` treba overiť správny namespace. Capture na host interface nemusí vidieť packet pred alebo po NAT-e v inom namespace.

## 3. Interfaces

Interface je kernelový network endpoint. Môže reprezentovať fyzický NIC, loopback, bridge, bond, VLAN, veth pair, tunnel alebo cloudový virtual NIC.

```bash
ip -br link
ip -br addr
ip -s link show dev eth0
ethtool eth0
```

Stav interface treba rozlišovať:

- **Administrative state** — `UP` znamená, že kernel môže interface používať; nepreukazuje fyzické spojenie.
- **Carrier state** — signalizuje link na L1/L2 vrstve, ale stále nepreukazuje IP konfiguráciu.
- **Address state** — interface môže mať adresu, no chýbať route alebo neighbor reachability.
- **Operational reachability** — až reálny packet path potvrdí, že traffic prejde tam aj späť.

Interface môže byť `UP`, ale bez carrieru, vhodnej route alebo remote return path zostáva aplikácia nedostupná.

## 4. IP addresses a prefixes

IP adresa identifikuje L3 endpoint v konkrétnom namespace. Prefix určuje, ktoré addresses kernel považuje za priamo pripojenú sieť.

```text
192.0.2.10/24
```

Pri `/24` vznikne connected route pre `192.0.2.0/24`. Destination v tomto prefixe sa pošle priamo cez neighbor resolution; destination mimo prefixu typicky potrebuje gateway alebo inú route.

```bash
ip addr show dev eth0
ip -6 addr show dev eth0
```

Jeden interface môže mať viac IPv4 aj IPv6 adries. Source address selection potom závisí od route, scope, policy a protocol rules; nie vždy sa použije adresa, ktorú operátor intuitívne očakáva.

## 5. Loopback a wildcard bind

Loopback `127.0.0.0/8` a `::1` zostáva v lokálnom host stacku. Služba bindnutá na `127.0.0.1:8080` preto nie je dostupná cez externý interface.

Wildcard bind `0.0.0.0:8080` znamená prijímanie na všetkých vhodných lokálnych IPv4 addresses. `[::]:8080` je IPv6 wildcard; či zároveň prijíma IPv4-mapped connections, závisí od socket option a systému.

```bash
ss -lntp
```

Pri probléme „port je otvorený, ale zvonka nefunguje“ treba najprv overiť bind address. Listening iba na loopback je aplikačná konfigurácia, nie firewall problém.

## 6. Routing decision

Routing table mapuje destination prefix na next hop, output interface, metric a ďalšie attributes. Kernel vyberá najšpecifickejší matching prefix; default route sa použije až keď neexistuje presnejšia route.

```bash
ip route
ip -6 route
ip route get 198.51.100.20
```

`ip route get` ukáže konkrétne rozhodnutie vrátane source address, gateway a interface. Je presnejší než všeobecný pohľad na tabuľku, pretože zohľadní destination aj policy.

Route môže byť:

- **Connected** — destination je priamo na lokálnom linku a potrebuje ARP/NDP.
- **Via gateway** — packet sa pošle next-hop routeru, nie priamo cieľovému hostu.
- **Blackhole/unreachable/prohibit** — kernel zámerne packet zahodí alebo vráti chybu.
- **Policy route** — výber tabuľky závisí aj od source, marku alebo iného pravidla.

## 7. Policy routing

Linux môže používať viac routing tables. `ip rule` rozhoduje, ktorú tabuľku použiť podľa source address, fwmarku, interface alebo priority pravidla.

```bash
ip rule
ip route show table all
ip route get 198.51.100.20 from 192.0.2.10
```

Default route v hlavnej tabuľke preto nemusí byť výslednou cestou. Multi-homed host, VPN alebo container platforma často používa policy routing a asymetrické očakávania môžu viesť k nesprávnemu return pathu.

## 8. Neighbor resolution

Po routing decision potrebuje host link-layer address next hopu. IPv4 používa ARP, IPv6 Neighbor Discovery.

```bash
ip neigh show
arping -I eth0 192.0.2.1
```

Neighbor entry prechádza stavmi ako `REACHABLE`, `STALE`, `DELAY`, `PROBE` alebo `FAILED`. `STALE` nie je automaticky chyba; znamená, že reachability nebola nedávno potvrdená a pri ďalšom použití sa môže znovu overiť.

Ak route existuje, ale neighbor resolution zlyhá, packet sa nedostane ani ku gateway. Typickými príčinami sú zlý VLAN segment, chýbajúci carrier, duplicate IP, bridge policy alebo nedostupný next hop.

## 9. Sockets

Socket je kernelový communication endpoint. Aplikácia cez syscalls vytvorí socket, bindne local address, začne listenovať alebo iniciuje spojenie.

```bash
ss -lntup
ss -tanp
ss -s
```

Listening socket má local address a port. Established TCP connection je identifikovaná kombináciou protocolu, source address/port a destination address/port v príslušnom namespace.

Port nie je globálne vlastnený iba číslom. `127.0.0.1:8080`, `192.0.2.10:8080` a IPv6 socket môžu mať odlišné bind a reachability semantics.

## 10. TCP handshake

TCP connection začína trojcestným handshakeom:

```text
Client → SYN
Server → SYN-ACK
Client → ACK
```

- `SYN-SENT` — klient odoslal SYN a čaká na odpoveď.
- `SYN-RECV` — server prijal SYN a čaká na finálne ACK.
- `ESTABLISHED` — transportné spojenie je vytvorené; aplikácia však ešte nemusí byť pripravená.

Ak klient posiela SYN a nič sa nevracia, problém môže byť v route, firewalli, remote hoste alebo return path. Ak prichádza RST, cieľ je dosiahnuteľný, ale nič nepočúva alebo policy spojenie aktívne odmieta.

## 11. TCP close states

TCP ukončenie je obojsmerný proces. `CLOSE-WAIT` znamená, že peer ukončil svoju stranu a lokálna aplikácia ešte nezavrela socket; veľké množstvo často ukazuje leak file descriptors alebo chybný connection lifecycle.

`TIME-WAIT` vzniká na strane aktívneho close a chráni pred oneskorenými segmentmi zo starého spojenia. Jeho prítomnosť je normálna; problémom sa stáva až v kombinácii s vyčerpaním ephemeral ports alebo nevhodným connection churnom.

```bash
ss -tan state close-wait
ss -tan state time-wait
```

## 12. UDP

UDP je connectionless transport. Kernel nevyžaduje handshake a úspešný `sendto()` typicky iba potvrdí lokálne prijatie dát do stacku, nie doručenie remote aplikácii.

UDP diagnostika preto potrebuje packet capture alebo application-level response. Listening UDP socket nemusí vytvoriť viditeľný connection state podobný TCP.

```bash
ss -lunp
nc -u -v <host> <port>
```

ICMP errors sa môžu vrátiť neskôr alebo byť filtrované. Absencia chyby nie je dôkaz úspešného doručenia.

## 13. DNS a NSS

Bežná aplikácia často používa `getaddrinfo()`, ktoré rešpektuje Name Service Switch. Výsledok môže pochádzať z `/etc/hosts`, DNS, mDNS, SSSD alebo iného zdroja podľa `/etc/nsswitch.conf`.

```bash
getent ahosts example.com
resolvectl query example.com
dig example.com
cat /etc/nsswitch.conf
cat /etc/resolv.conf
```

`dig` testuje DNS protocol priamo, ale nemusí reprodukovať aplikačný lookup. `getent` je vhodnejší na overenie NSS pathu, ktorý používa väčšina libc aplikácií.

Resolver behavior ovplyvňujú search domains, `ndots`, cache, address-family preference a timeout/retry policy. Rovnaké meno preto môže viesť k inému výsledku medzi kontajnerom, hostom a systemd službou.

## 14. DNS nie je reachability

Name resolution iba preloží meno na jednu alebo viac adries. Ďalšie vrstvy môžu zlyhať nezávisle:

```text
name → IP
IP → route
route → next hop
next hop → remote host
remote host → port
port → TLS/application
```

Ak meno vracia IPv6 aj IPv4, aplikácia môže skúsiť inú family než manuálny test. Pri diagnostike treba zaznamenať konkrétnu vybranú adresu a testovať rovnaký destination tuple.

## 15. Persistent network configuration

`ip addr add` alebo `ip route add` mení runtime state. Persistent desired state môže spravovať NetworkManager, systemd-networkd, netplan, cloud-init alebo orchestration platforma.

```bash
networkctl status
nmcli device show
systemctl status NetworkManager systemd-networkd
```

Ručná runtime zmena môže po reboote zmiznúť alebo ju manager okamžite prepíše. Pred opravou treba identifikovať source of truth a upraviť ho, nie iba aktuálny kernel state.

## 16. Netfilter hooks

Netfilter umožňuje filtrovanie, NAT, marking a connection tracking v rôznych bodoch packet pathu. nftables je moderné rozhranie; `iptables` môže byť legacy backend alebo compatibility frontend nad nftables.

```bash
nft list ruleset
iptables -S
iptables -t nat -S
```

Direction určuje relevantný hook:

- **INPUT** — packet je určený lokálnemu hostu.
- **OUTPUT** — packet vytvorila lokálna aplikácia.
- **FORWARD** — host packet routuje medzi interfaces.
- **PREROUTING/POSTROUTING** — používajú sa okrem iného pri DNAT/SNAT a marking.

Listening socket môže byť správny, no INPUT policy packet zahodí. Pri routovaní kontajnerového trafficu môže byť problém vo FORWARD chaine, nie v lokálnom INPUT-e.

## 17. Connection tracking

Conntrack sleduje flow state a umožňuje stateful firewall a NAT. Entry spája originálny a reply tuple, preto return traffic môže byť povolený ako súčasť existujúceho spojenia.

```bash
conntrack -L
nft list ruleset
sysctl net.netfilter.nf_conntrack_count
sysctl net.netfilter.nf_conntrack_max
```

Vyčerpanie conntrack table môže spôsobiť stratu nových spojení aj pri voľnom CPU a funkčnom listening sockete. NAT mapping je tiež závislý od conntrack state; jeho strata môže prerušiť existujúce flows.

## 18. NAT

NAT mení source alebo destination address/port. SNAT/MASQUERADE sa často používa pri outbound trafficu z private siete, DNAT pri publikovaní služby na inom endpoint-e.

```text
Client 10.0.0.10:40000
  ↓ SNAT
Gateway 198.51.100.5:52000
  ↓
Remote server
```

NAT nerieši routing automaticky. Host potrebuje správnu route, povolený forwarding, firewall policy a funkčný return path.

Pri packet capture treba vedieť, či observation point leží pred alebo po translation. Rovnaké spojenie môže mať na rôznych interfaces odlišný tuple.

## 19. IP forwarding

Host routuje packet medzi interfaces iba ak je forwarding povolený a routing/firewall policy ho dovoľuje.

```bash
sysctl net.ipv4.ip_forward
sysctl net.ipv6.conf.all.forwarding
```

Zapnutie sysctl samo osebe nestačí. FORWARD chain môže packet zahodiť a remote sieť musí mať route späť alebo sa musí použiť NAT.

Asymetrický routing môže naraziť na reverse-path filtering alebo stateful firewall expectations. Forward path a return path treba overovať oddelene.

## 20. MTU a Path MTU Discovery

MTU určuje maximálnu veľkosť L3 packetu na konkrétnom linku. Tunnely a overlays pridávajú headers, takže effective payload MTU je menšie než na underlying interface.

```bash
ip link show dev eth0
tracepath example.com
ping -M do -s 1472 <IPv4-destination>
```

Path MTU Discovery závisí od ICMP správ ako Fragmentation Needed alebo Packet Too Big. Ak sú filtrované, malé requests môžu fungovať, zatiaľ čo väčšie TLS records alebo file transfers zamrznú.

MTU problém je častý pri VPN, VXLAN, cloud tunnels a kontajnerových overlay networks. Riešenie musí byť konzistentné pozdĺž celej path, nie iba na jednom interface.

## 21. Packet capture

`tcpdump` ukazuje packets prechádzajúce konkrétnym observation pointom. Jeho hodnota závisí od správneho namespace, interface, direction a času.

```bash
tcpdump -ni any host 198.51.100.20 and port 443
tcpdump -ni eth0 'tcp[tcpflags] & tcp-syn != 0'
```

Capture odpovedá na presné otázky:

- SYN neodchádza — problém je pred output pathom, napríklad DNS, route alebo local policy.
- SYN odchádza, nič sa nevracia — remote path, firewall alebo return route.
- SYN prichádza a host posiela RST — socket nepočúva na danom tuple alebo policy rejectuje spojenie.
- Handshake prebehne, no aplikácia timeoutuje — problém je vyššie, napríklad TLS alebo application protocol.

Offloading môže spôsobiť, že capture ukazuje zdanlivo veľké alebo neštandardne checksumované packets. To nemusí znamenať chybu na wire.

## 22. ICMP, ping a path tools

`ping` testuje ICMP echo. Neoveruje TCP port, TLS certifikát ani application response.

```bash
ping -c 4 192.0.2.1
tracepath example.com
traceroute example.com
mtr example.com
```

Router môže neodpovedať na traceroute probe, ale forwardovať bežný traffic. Jeden chýbajúci hop preto nie je automaticky dôkaz packet lossu.

ICMP neslúži iba na diagnostiku. Prenáša aj dôležité control messages pre unreachable destinations a Path MTU Discovery; jeho plošné blokovanie môže poškodiť funkčnosť siete.

## 23. Firewall nie je jediná policy vrstva

Packet môže blokovať lokálny nftables ruleset, cloud security group, network ACL, Kubernetes NetworkPolicy, service mesh alebo remote host firewall. Každá vrstva vidí iný tuple a iný bod packet pathu.

Diagnostika musí explicitne určiť:

- source a destination address po prípadnom NAT-e,
- protocol a port,
- direction,
- namespace a interface,
- connection state,
- policy ownera každej vrstvy.

Neurčité tvrdenie „firewall je otvorený“ nestačí bez uvedenia konkrétnej vrstvy a flow.

## 24. Socket backlog a connection pressure

Listening socket má backlog pre pending connections. Pri preťažení môže SYN queue alebo accept queue dosiahnuť limit a klienti uvidia timeouty alebo retransmissions.

```bash
ss -lnt
ss -s
netstat -s | grep -i listen
sysctl net.core.somaxconn
sysctl net.ipv4.tcp_max_syn_backlog
```

Zvýšenie backlogu môže zmierniť burst, ale nevyrieši pomalý `accept()`, vyčerpaný worker pool alebo downstream dependency. Queue je symptom rozdielu medzi arrival rate a service rate.

## 25. Ephemeral ports

Outbound TCP connection potrebuje lokálny ephemeral port. Pri veľkom connection churne alebo NAT koncentrácii sa môže rozsah vyčerpať.

```bash
sysctl net.ipv4.ip_local_port_range
ss -tan state time-wait | wc -l
```

Vyčerpanie sa môže prejaviť chybami pri connecte, hoci remote service je zdravá. Root cause môže byť chýbajúci connection pooling, príliš krátke connections alebo NAT mapping pressure.

## 26. Diagnostika spojenia na databázu

Aplikácia sa nevie pripojiť na `db.example:5432`. Postup má zachovať rovnaký destination a namespace ako aplikácia:

1. **Over resolver path** — `getent ahosts db.example` ukáže addresses dostupné cez NSS.
2. **Zaznamenaj vybranú family a IP** — aplikácia môže preferovať IPv6, zatiaľ čo manuálny test používa IPv4.
3. **Over routing decision** — `ip route get <IP>` ukáže source, gateway a interface.
4. **Over neighbor state** — pri connected route skontroluj `ip neigh` pre next hop.
5. **Over local socket attempt** — `ss -tanp` ukáže `SYN-SENT`, established alebo chýbajúci pokus.
6. **Over local policy** — nftables/iptables OUTPUT alebo container policy môže traffic blokovať.
7. **Capture packet** — potvrď SYN, odpoveď a return path cez `tcpdump` v správnom namespace.
8. **Over TCP port** — `nc -vz` alebo `timeout bash -c '</dev/tcp/host/port'` testuje transport, nie aplikáciu.
9. **Over TLS/protocol** — po handshaku skontroluj certifikát, authentication a databázový protocol.
10. **Koreluj s remote logs** — absencia requestu na serveri potvrdzuje problém pred application layerom.

## 27. Anti-patterny

### Ping použitý ako dôkaz zdravia služby

ICMP echo funguje, no TCP port je zatvorený alebo TLS handshake zlyháva. Test musí zodpovedať protokolu a endpointu, ktorý používa aplikácia.

### Ručná route bez zmeny source of truth

Operátor pridá runtime route cez `ip route add`, ale NetworkManager alebo reboot ju odstráni. Trvalá oprava musí byť zapísaná v správnom configuration manageri.

### Capture v nesprávnom namespace

Na hoste nie je vidieť packet a tím usúdi, že aplikácia nič neposiela. Kontajner však používa iný network namespace a packet prechádza veth alebo overlay pathom mimo zvoleného observation pointu.

### MTU riešené iba znížením jednej strany

Jeden interface dostane menšie MTU, ale tunnel alebo peer zostane nekonzistentný. Výsledkom môžu byť asymetrické alebo workload-specific problémy; treba modelovať celý path MTU.

## 28. Kontrolné otázky

1. Aký je rozdiel medzi administrative state, carrier a routability?
2. Ako kernel vyberá route a kedy vstupuje do hry policy routing?
3. Prečo po route decision ešte treba ARP alebo NDP?
4. Aký je rozdiel medzi bindom na loopback, konkrétnu adresu a wildcard?
5. Čo znamenajú `SYN-SENT`, `CLOSE-WAIT` a `TIME-WAIT`?
6. Prečo `dig` nemusí reprodukovať lookup bežnej aplikácie?
7. Ako sa líšia INPUT, OUTPUT a FORWARD packet paths?
8. Načo slúži conntrack a čo sa stane pri jeho vyčerpaní?
9. Prečo NAT vyžaduje aj routing a return path?
10. Ako sa prejavuje MTU black hole?
11. Prečo `tcpdump -i any` nemusí vidieť všetok relevantný traffic?
12. Ako by si odlíšil DNS, route, firewall, TCP, TLS a application failure?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Memory a CPU fundamentals](cpu-and-memory-fundamentals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: SSH →](ssh.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
