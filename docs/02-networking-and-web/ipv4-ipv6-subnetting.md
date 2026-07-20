# IPv4, IPv6 a subnetting

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [OSI a TCP/IP model](osi-and-tcp-ip-model.md), [Ethernet, MAC a ARP](ethernet-mac-arp.md)
- Súvisiace témy: routing, NAT, DNS, IPv6 NDP, cloud networking

## 1. Definícia

IP poskytuje logické adresovanie a packet delivery medzi sieťami. Prefix určuje, ktorá časť adresy identifikuje sieť a ktorá adresný priestor v tejto sieti.

Subnetting rozdeľuje väčší address prefix na menšie prefixes podľa topológie, routingu, kapacity a bezpečnostných hraníc.

## 2. IPv4 adresa a prefix

IPv4 adresa má 32 bitov a zapisuje sa ako štyri decimal octets:

```text
192.0.2.10
```

CIDR prefix:

```text
192.0.2.10/24
```

`/24` znamená, že prvých 24 bitov tvorí network prefix a zostávajúcich 8 bitov host časť.

Maska:

```text
255.255.255.0
```

CIDR je presnejší a všeobecnejší zápis než historické classful siete.

## 3. Network, host a broadcast address

Pre `192.0.2.0/24`:

```text
network:   192.0.2.0
hosts:     192.0.2.1 – 192.0.2.254
broadcast: 192.0.2.255
```

Klasický počet použiteľných IPv4 host addresses:

```text
2^(32-prefix) - 2
```

Výnimky:

- `/31` sa používa na point-to-point links bez klasického network/broadcast odpočítania,
- `/32` reprezentuje jednu IPv4 adresu alebo host route,
- cloud platforma môže rezervovať ďalšie adresy v subnet-e.

## 4. Binárny základ subnettingu

Adresa:

```text
192.0.2.10
```

Binárne:

```text
11000000.00000000.00000010.00001010
```

Pri `/26`:

```text
network bits: 26
host bits:     6
addresses:     2^6 = 64
```

Možné `/26` subnety v pôvodnom `/24`:

```text
192.0.2.0/26
192.0.2.64/26
192.0.2.128/26
192.0.2.192/26
```

Block size v poslednom relevantnom octete je 64.

## 5. Rýchly výpočet IPv4 prefixov

| Prefix | Adries | Typicky použiteľných hostov |
|---:|---:|---:|
| /24 | 256 | 254 |
| /25 | 128 | 126 |
| /26 | 64 | 62 |
| /27 | 32 | 30 |
| /28 | 16 | 14 |
| /29 | 8 | 6 |
| /30 | 4 | 2 |
| /31 | 2 | point-to-point |
| /32 | 1 | host route |

Pri cloudových subnets nepoužívaj tabuľku bez overenia provider reservations.

## 6. Zistenie subnetu adresy

Adresa `192.0.2.77/26`:

- block size: 64,
- intervaly: 0, 64, 128, 192,
- 77 patrí do 64–127.

Výsledok:

```text
network:   192.0.2.64/26
broadcast: 192.0.2.127
hosts:     192.0.2.65–126
```

Nástroje:

```bash
ipcalc 192.0.2.77/26
python3 - <<'PY'
import ipaddress
n = ipaddress.ip_interface('192.0.2.77/26')
print(n.network)
print(n.network.broadcast_address)
PY
```

## 7. Overlapping subnets

Prefixes sa prekrývajú, ak časť address space patrí do oboch.

```text
10.0.0.0/16
10.0.10.0/24
```

Druhý je vnorený v prvom. To je normálne v routing table, kde vyhráva longest-prefix match.

Problém vzniká, keď dve organizačne odlišné siete používajú prekrývajúce sa private addresses a majú sa prepojiť cez VPN, peering alebo merger.

Dôsledky:

- nejednoznačný routing,
- komplikovaný NAT,
- nemožné priame reachability,
- zložité DNS a identity mapovanie.

Address planning je architektonická disciplína, nie iba lokálna konfigurácia.

## 8. Private, public a špeciálne IPv4 ranges

Private IPv4 ranges:

```text
10.0.0.0/8
172.16.0.0/12
192.168.0.0/16
```

Ďalšie dôležité ranges:

- loopback `127.0.0.0/8`,
- link-local `169.254.0.0/16`,
- multicast `224.0.0.0/4`,
- documentation `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`,
- limited broadcast `255.255.255.255`.

Private adresa nie je automaticky bezpečná. Znamená iba, že nie je globálne routovaná vo verejnom Internet address plane.

## 9. IPv4 packet header

Kľúčové fields:

- version,
- header length,
- total length,
- identification a fragmentation fields,
- TTL,
- protocol,
- header checksum,
- source a destination address.

TTL sa znižuje na každom router hop-e. Pri nule router packet zahodí a typicky odošle ICMP Time Exceeded.

TTL bráni nekonečnému cirkulovaniu packetov pri routing loop-e.

## 10. Fragmentácia a Path MTU

IPv4 router môže packet fragmentovať, ak je väčší než outgoing MTU a DF flag to nezakazuje.

Moderné aplikácie sa typicky spoliehajú na Path MTU Discovery a snažia sa fragmentácii vyhnúť.

Problém:

```text
DF set
packet príliš veľký
ICMP Fragmentation Needed blokované
→ Path MTU black hole
```

Symptóm: malé requests fungujú, veľké prenosy timeoutujú.

## 11. IPv6 základ

IPv6 adresa má 128 bitov a zapisuje sa hexadecimal groups:

```text
2001:db8:1234:5678:abcd:ef01:2345:6789
```

Skrátenie:

- leading zeros v skupine možno vynechať,
- jednu súvislú sekvenciu nulových skupín možno nahradiť `::`.

Príklad:

```text
2001:db8:0:0:0:0:0:1
→ 2001:db8::1
```

`::` možno v jednej adrese použiť iba raz, aby bol zápis jednoznačný.

## 12. IPv6 prefixy

Bežný LAN subnet je `/64`.

```text
2001:db8:1234:5678::/64
```

To ponecháva 64-bit interface identifier space.

IPv6 subnetting sa nemá navrhovať iba podľa počtu hostov. Veľký address space umožňuje hierarchické, sumarizovateľné a stabilné prefix allocation.

Príklad rozdelenia `/48` na `/64`:

```text
organization: 2001:db8:1234::/48
subnet ID:    16 bitov
→ 65 536 možných /64 subnetov
```

## 13. Typy IPv6 adries

### Global unicast

Globálne routovateľné adresy, typicky z `2000::/3`.

### Link-local

```text
fe80::/10
```

Každý IPv6-enabled interface má typicky link-local adresu. Používa sa pre neighbor discovery a lokálnu komunikáciu.

Pri link-local destination je často potrebný zone/interface identifikátor:

```bash
ping -6 fe80::1%eth0
```

### Unique local

```text
fc00::/7
```

Prakticky sa používa `fd00::/8` s náhodne generovaným global ID. Nie je to presný ekvivalent RFC1918 private IPv4 a nemá sa používať ako ospravedlnenie pre slabú security policy.

### Multicast

```text
ff00::/8
```

IPv6 nepoužíva broadcast; veľa lokálnych funkcií používa multicast.

### Loopback a unspecified

```text
::1/128
::/128
```

## 14. IPv6 header

IPv6 base header je jednoduchší než IPv4 a má fixnú veľkosť.

Kľúčové fields:

- version,
- traffic class,
- flow label,
- payload length,
- next header,
- hop limit,
- source a destination.

Voliteľné informácie používajú extension headers.

Routery IPv6 packet typicky nefragmentujú. Fragmentáciu vykonáva source endpoint pomocou Fragment extension header podľa Path MTU Discovery.

## 15. NDP namiesto ARP

IPv6 používa Neighbor Discovery Protocol nad ICMPv6.

Funkcie:

- neighbor address resolution,
- router discovery,
- prefix discovery,
- duplicate address detection,
- neighbor reachability detection,
- redirect messages.

Blokovanie ICMPv6 plošne môže rozbiť základné IPv6 fungovanie. ICMPv6 je integrálna súčasť protocol stacku, nie iba ping.

## 16. SLAAC a DHCPv6

### SLAAC

Host vytvorí adresu z prefixu oznámeného Router Advertisement a interface identifier mechanizmu.

### DHCPv6

Môže prideľovať adresy alebo ďalšie configuration data.

### Router Advertisement flags

Oznamujú, či host použije SLAAC, DHCPv6 alebo kombináciu.

Default gateway v IPv6 sa host typicky učí z Router Advertisements, nie z DHCPv6 default-route option.

## 17. Privacy addresses

Stabilný interface identifier môže uľahčiť sledovanie zariadenia naprieč sieťami. IPv6 privacy extensions vytvárajú dočasné source addresses pre outbound connections.

Host môže mať súčasne:

- link-local address,
- stable global address,
- temporary global addresses,
- multiple deprecated addresses.

Preto `ip addr` môže zobraziť viac IPv6 adries na jednom interface a source-address selection je samostatný mechanizmus.

## 18. Dual stack

Dual-stack host používa IPv4 aj IPv6.

Aplikácia môže dostať A aj AAAA record a vybrať protokol podľa resolver a connection algorithm-u, napríklad Happy Eyeballs.

Dôležitý dôsledok:

```text
IPv4 funguje
≠
služba funguje pre klienta, ktorý preferuje IPv6
```

Diagnostikuj obe families samostatne:

```bash
curl -4 https://example.com/
curl -6 https://example.com/
ip -4 route
ip -6 route
```

## 19. IPv4-mapped IPv6 addresses

Aplikácia alebo log môže zobraziť IPv4 clienta ako:

```text
::ffff:192.0.2.10
```

Ide o IPv4-mapped IPv6 representation v API alebo socket kontexte, nie automaticky o end-to-end IPv6 traffic.

Dual-stack socket behavior závisí od OS, `IPV6_V6ONLY` option a aplikácie.

## 20. Subnet design princípy

Dobrý address plan zohľadňuje:

- počet a rast endpoints,
- Availability Zones alebo failure domains,
- routing summarization,
- security boundaries,
- on-prem/cloud connectivity,
- Kubernetes Pod/Service CIDRs,
- mergers a peering,
- IPv6 allocation,
- rezervy bez extrémneho plytvania.

Nesnaž sa využiť každý address bit. Address space má podporovať prevádzkovateľnú topológiu.

## 21. VLSM a sumarizácia

Variable Length Subnet Masking umožňuje rozdeliť address space na rôzne veľké prefixes.

```text
10.0.0.0/16
├── 10.0.0.0/20 production
├── 10.0.16.0/22 staging
└── 10.0.20.0/24 management
```

Route summarization znižuje počet routes:

```text
10.0.0.0/16
```

môže reprezentovať viac vnútorných subnetov, ak topológia a policy dovoľujú spoločné announcement.

Neopatrná sumarizácia môže vytvoriť black hole pre neexistujúce alebo nesprávne smerované subprefixes.

## 22. Linux diagnostika adries

```bash
ip -4 addr
ip -6 addr
ip -4 route
ip -6 route
ip route get 198.51.100.10
ip -6 route get 2001:db8::10
```

Kontroluj:

- prefix length,
- scope,
- tentative/deprecated flags,
- source address selection,
- duplicate address detection,
- connected routes,
- policy routing.

## 23. Troubleshooting scenár: hosty v rovnakom subnet-e sa nevidia

1. Over IP a prefix na oboch hostoch.
2. Vypočítaj, či sa navzájom považujú za on-link.
3. Skontroluj ARP/NDP.
4. Over VLAN a link stav.
5. Skontroluj firewall.
6. Zachyť neighbor discovery traffic.

Chybný prefix môže spôsobiť asymetriu:

- host A považuje B za lokálny,
- host B posiela odpoveď cez gateway.

## 24. Troubleshooting scenár: IPv6 preferencia spôsobuje timeout

```bash
getent ahosts example.com
curl -4 -v https://example.com/
curl -6 -v https://example.com/
ip -6 route get <IPv6>
ping -6 <gateway-or-target>
tcpdump -ni any ip6
```

Možné príčiny:

- AAAA record existuje, ale server alebo route nie,
- chýba IPv6 default route,
- firewall blokuje ICMPv6 alebo TCP,
- return path chýba,
- application počúva iba na IPv4,
- MTU/PMTUD problém.

## 25. Časté omyly

### „/24 znamená 24 hostov“

Nie. Znamená 24 network bits.

### „Private IP znamená bezpečná IP“

Nie. Security závisí od routing a access policy.

### „IPv6 nemá subnetting“

Má rozsiahly hierarchický prefix model; bežný endpoint subnet je `/64`.

### „IPv6 nepotrebuje ICMP“

ICMPv6 je kritický pre NDP a Path MTU Discovery.

### „Dual stack znamená, že obe families fungujú rovnako“

Každá má vlastné addresses, routes, firewall rules a failure modes.

### „NAT je podmienka používania IPv4“

Nie. NAT je samostatný translation mechanizmus, často používaný pre address conservation alebo policy.

## 26. Kontrolné otázky

1. Čo znamená CIDR prefix length?
2. Ako vypočítaš network a broadcast pre IPv4 `/26`?
3. Prečo `/31` funguje na point-to-point linku?
4. Aké problémy spôsobujú overlapping private networks?
5. Načo slúži IPv4 TTL a IPv6 hop limit?
6. Prečo je `/64` bežný IPv6 LAN prefix?
7. Akú úlohu má NDP?
8. Aký je rozdiel medzi SLAAC a DHCPv6?
9. Prečo môže dual-stack aplikácia zlyhávať iba cez IPv6?
10. Ako address planning podporuje route summarization?
