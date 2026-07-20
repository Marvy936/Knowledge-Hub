# Routing a default gateway

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [IPv4, IPv6 a subnetting](ipv4-ipv6-subnetting.md), [Ethernet, MAC a ARP](ethernet-mac-arp.md)
- Súvisiace témy: policy routing, dynamic routing, NAT, firewalls, cloud route tables

## 1. Definícia

Routing je proces výberu cesty, ktorou sa IP packet odošle k destination prefixu. Router alebo host porovná destination IP s routing table a vyberie najvhodnejšiu route.

Default gateway je next hop použitý vtedy, keď neexistuje presnejšia route pre destination.

## 2. Routing table

Route typicky obsahuje:

- destination prefix,
- next hop/gateway,
- outgoing interface,
- metric alebo preference,
- source address hint,
- protocol/origin,
- scope a type,
- prípadne ďalšie policy attributes.

Linux:

```bash
ip route
ip -6 route
```

Príklad:

```text
default via 192.0.2.1 dev eth0
192.0.2.0/24 dev eth0 proto kernel scope link src 192.0.2.10
10.20.0.0/16 via 192.0.2.254 dev eth0 metric 50
```

## 3. Connected route

Keď interface dostane adresu s prefixom, kernel typicky vytvorí connected route.

```text
IP:    192.0.2.10/24
Route: 192.0.2.0/24 dev eth0 scope link
```

Destination v tomto prefixe sa považuje za on-link. Host sa pokúsi získať MAC adresu destination priamo cez ARP, nie cez default gateway.

Chybný prefix môže preto zmeniť L2/L3 rozhodnutie.

## 4. Longest-prefix match

Ak sa zhoduje viac routes, vyhráva najšpecifickejší prefix.

```text
10.0.0.0/8      via gateway A
10.10.0.0/16    via gateway B
10.10.20.0/24   via gateway C
```

Destination `10.10.20.5` použije `/24` route cez gateway C.

Metric sa typicky porovnáva až medzi routes s rovnakou prefix specificity a v rámci príslušného routing modelu.

## 5. Default route

IPv4:

```text
0.0.0.0/0
```

IPv6:

```text
::/0
```

Default route sa zhoduje s každou adresou, ale je najmenej špecifická.

```bash
ip route get 203.0.113.20
ip -6 route get 2001:db8::20
```

`ip route get` je užitočnejší než samotný výpis table, pretože ukáže konkrétny resolved decision vrátane interface, gateway a source address.

## 6. Next hop musí byť dosiahnuteľný

Gateway musí byť typicky on-link alebo dosiahnuteľná cez ďalší explicitný mechanizmus.

```text
default via 192.0.2.1 dev eth0
```

Host musí vedieť doručiť frame k `192.0.2.1` cez eth0.

Existencia route nedokazuje:

- ARP/NDP úspech,
- funkčný link,
- dostupnosť gateway,
- správny return path,
- firewall povolenie.

## 7. Packet forwarding na routeri

Host sa stane IP routerom, keď:

- má viac relevantných interfaces alebo paths,
- kernel forwarding je povolený,
- routing table pozná destination,
- firewall forwarding policy traffic povoľuje,
- return path existuje.

Linux:

```bash
sysctl net.ipv4.ip_forward
sysctl net.ipv6.conf.all.forwarding
```

Forwarding nie je NAT. Router môže routovať bez translation.

## 8. TTL a hop limit

IPv4 TTL a IPv6 hop limit sa na každom router hop-e znižujú.

Pri dosiahnutí nuly router packet zahodí a typicky odošle ICMP Time Exceeded.

To umožňuje nástroje:

```bash
traceroute example.com
tracepath example.com
```

Routing loop sa prejaví opakujúcimi sa hops alebo vypršaním TTL, ale firewally a asymetrické paths môžu výsledok komplikovať.

## 9. Route types v Linuxe

Okrem unicast route existujú typy ako:

- `local` — destination patrí lokálnemu hostu,
- `broadcast`,
- `unreachable`,
- `blackhole`,
- `prohibit`,
- `throw`.

Príklad blackhole route:

```bash
ip route add blackhole 203.0.113.0/24
```

Používa sa na explicitné zahodenie alebo na routing-policy designs. Je dôležité rozlíšiť zámerný blackhole od chýbajúcej route.

## 10. Source address selection

Host s viacerými adresami musí vybrať source IP.

Výber ovplyvňuje:

- route `src` hint,
- address scope,
- IPv6 source selection rules,
- policy routing,
- socket bind aplikácie.

```bash
ip route get 198.51.100.10
```

Výstup môže obsahovať:

```text
src 192.0.2.10
```

Nesprávny source address môže spôsobiť chýbajúci return path, firewall deny alebo nesprávnu identitu služby.

## 11. Multiple default routes

Host môže mať viac default routes s rôznymi metrics.

```text
default via 192.0.2.1 dev eth0 metric 100
default via 198.51.100.1 dev eth1 metric 200
```

Nižšia metric je typicky preferovaná. Samotná route však nemusí automaticky reagovať na vzdialenú service health. Link môže byť up, ale upstream Internet path nefunkčný.

Robustný failover môže potrebovať:

- route tracking,
- dynamic routing,
- health-check automation,
- policy routing,
- connection-state consideration.

## 12. Asymmetric routing

Outbound a inbound traffic môžu ísť rozdielnymi paths.

```text
client → firewall A → server
server → firewall B → client
```

IP routing to môže dovoliť, ale stateful firewalls, NAT alebo load balancers môžu očakávať symetrický flow.

Symptómy:

- SYN prichádza, SYN-ACK odchádza inou cestou,
- connection timeout,
- firewall state missing,
- packet capture na jednej ceste ukazuje iba polovicu flow.

## 13. Reverse path filtering

Linux `rp_filter` overuje, či source address prichádzajúceho packetu zodpovedá očakávanej reverse route.

```bash
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.eth0.rp_filter
```

Strict mode môže zahadzovať legitímny asymmetric traffic. V multihomed, policy-routing alebo overlay environments treba policy navrhnúť vedome.

Vypnutie bez analýzy môže oslabiť anti-spoofing ochranu.

## 14. Policy routing

Bežný routing rozhoduje najmä podľa destination. Policy routing môže zohľadniť:

- source prefix,
- packet mark,
- ingress interface,
- TOS/DSCP,
- user/group pri lokálnom traffiku,
- ďalšie selectors.

Linux:

```bash
ip rule
ip route show table all
```

Príklad konceptu:

```text
from 10.0.10.0/24 lookup table 100
```

Policy rule vyberie routing table; v nej sa potom opäť vykoná longest-prefix match.

## 15. Routing tables a rules

Linux má viac tables, napríklad:

- `local`,
- `main`,
- `default`,
- custom tables.

```bash
ip rule show
ip route show table local
ip route show table main
```

Bežný `ip route` zobrazuje najmä main table. Pri policy-routing incidente nemusí byť dostatočný.

`ip route get` s doplneným source môže simulovať konkrétny flow:

```bash
ip route get 203.0.113.10 from 192.0.2.10
```

## 16. Static a dynamic routing

### Static route

Konfiguruje administrátor alebo automation.

Výhody:

- jednoduchá,
- predvídateľná,
- nízka protocol complexity.

Nevýhody:

- manuálna správa,
- slabá reakcia na topology changes,
- rastúca komplexita vo veľkej sieti.

### Dynamic routing

Routing protocol vymieňa reachability informácie a vypočítava paths.

Príklady:

- OSPF/IS-IS v interných sieťach,
- BGP medzi autonomous systems aj vo veľkých datacenters/cloud designs.

Dynamic neznamená automaticky správne. Chybný route advertisement sa môže rozšíriť veľmi rýchlo.

## 17. Administrative distance a metrics

Rôzne platformy používajú preference na výber medzi routes z rôznych zdrojov. Potom protokol používa vlastnú metric na výber paths.

Konkrétne názvy a poradie závisia od router platformy. Linux route table používa svoje fields a prioritu rules.

Nemiešaj:

- prefix specificity,
- route source preference,
- protocol metric,
- ECMP selection.

## 18. ECMP

Equal-Cost Multi-Path umožňuje viac rovnocenných next hops.

```text
10.20.0.0/16
  nexthop via 192.0.2.1
  nexthop via 192.0.2.2
```

Traffic sa typicky rozdeľuje hashom podľa flow fields, nie packet-by-packet náhodne.

Riziká:

- nerovnomerné flow sizes,
- zmena hash mappingu pri failure,
- stateful middleboxes,
- asymmetry,
- observability na viacerých paths.

## 19. Route summarization

Viac prefixes možno inzerovať ako väčší aggregate.

```text
10.20.0.0/24
10.20.1.0/24
...
→ 10.20.0.0/16 podľa allocation
```

Výhody:

- menšie routing tables,
- stabilnejší control plane,
- skrytie detailnej topológie.

Riziko: aggregate môže pri chýbajúcej konkrétnej route priťahovať traffic do black hole. Preto sa často používa discard route pre summary a konzistentné allocation.

## 20. Cloud route tables

Cloud platformy implementujú virtual routing.

Route target môže byť:

- Internet gateway,
- NAT gateway,
- virtual appliance,
- peering/transit gateway,
- VPN attachment,
- local virtual network.

Dôležité:

- route table nie je automaticky firewall,
- subnet association určuje, ktorá table sa používa,
- platform môže rezervovať system routes,
- source/destination checks môžu blokovať appliance forwarding,
- return route musí existovať na všetkých relevantných stranách.

## 21. Kubernetes a container routing

Pod traffic môže používať:

- direct routes,
- overlays/tunnels,
- eBPF dataplane,
- host routing a policy rules,
- service translation.

Troubleshooting musí identifikovať namespace a dataplane implementation.

```text
Pod route
→ node veth
→ CNI dataplane
→ host route/tunnel
→ remote node/endpoint
```

Host `ip route` môže byť iba časťou rozhodovacieho modelu.

## 22. Troubleshooting scenár: destination unreachable

```bash
ip addr
ip rule
ip route show table all
ip route get <destination>
ip neigh
ping -c 1 <gateway>
tracepath <destination>
tcpdump -ni any host <destination>
```

Klasifikuj:

- `Network is unreachable` — lokálne chýba route,
- ARP/NDP failure — next hop nie je link-layer reachable,
- ICMP unreachable — vzdialený router/host explicitne odmietol,
- timeout — packet alebo odpoveď sa stratila bez explicitnej chyby.

## 23. Troubleshooting scenár: request odchádza, odpoveď neprichádza

1. Over source address cez `ip route get`.
2. Zachyť outbound packet.
3. Zachyť traffic na destination alebo next appliance, ak je prístup.
4. Over return routing k source.
5. Skontroluj stateful firewall/NAT symmetry.
6. Over `rp_filter`.
7. Skontroluj policy rules a marks.

Return path je samostatný routing problém; forward route sama nestačí.

## 24. Časté omyly

### „Default gateway dostane všetok traffic“

Nie. Presnejšie connected alebo static routes majú prednosť.

### „Nižšia metric vždy vyhrá“

Najprv rozhoduje prefix specificity a routing-policy kontext.

### „Route existuje, teda destination je dostupná“

Route je iba rozhodovací stav. Link, next hop, firewall a return path môžu zlyhať.

### „Forwarding a NAT sú to isté“

Nie. Forwarding routuje packet; NAT mení addresses alebo ports.

### „Asymmetric routing je vždy chyba“

IP ho povoľuje, ale môže byť nekompatibilný so stateful middleboxes.

### „Traceroute ukazuje presnú cestu každého application packetu“

ECMP, filtering a return-path differences môžu výsledok meniť.

## 25. Kontrolné otázky

1. Ako funguje longest-prefix match?
2. Kedy sa použije default route?
3. Prečo next hop musí byť on-link reachable?
4. Aký je rozdiel medzi routing a forwarding?
5. Prečo route nedokazuje end-to-end dostupnosť?
6. Ako source-address selection ovplyvňuje return path?
7. Čo rieši policy routing?
8. Prečo môže `rp_filter` blokovať asymmetric flow?
9. Aké trade-offy má ECMP?
10. Ako by si diagnostikoval packet, ktorý odchádza, ale odpoveď neprichádza?
