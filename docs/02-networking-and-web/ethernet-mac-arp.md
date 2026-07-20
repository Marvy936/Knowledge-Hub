# Ethernet, MAC a ARP

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [OSI a TCP/IP model](osi-and-tcp-ip-model.md), [Linux networking](../01-linux-and-systems/linux-networking.md)
- Súvisiace témy: switching, VLAN, IPv4, routing, NDP, packet capture

## 1. Definícia

Ethernet je skupina link-layer technológií používaných na prenos frames v lokálnom sieťovom segmente. MAC address je link-layer identifikátor interface. ARP mapuje IPv4 next-hop adresu na MAC adresu v lokálnom linku.

Tieto mechanizmy riešia lokálny hop. Nerobia globálny Internet routing.

## 2. Ethernet frame

Zjednodušená štruktúra:

```text
Destination MAC
Source MAC
EtherType alebo length
Payload
Frame Check Sequence
```

EtherType označuje vyšší protokol, napríklad:

- IPv4,
- IPv6,
- ARP,
- VLAN-tagged frame.

Frame Check Sequence slúži na detekciu poškodenia na linke. Frame s chybným FCS sa typicky zahodí a vyššia vrstva môže zlyhanie kompenzovať retransmission mechanizmom.

## 3. MAC address

Bežná MAC adresa má 48 bitov:

```text
00:11:22:33:44:55
```

Nie je spoľahlivou globálnou identitou zariadenia:

- môže byť softvérovo zmenená,
- virtual interfaces dostávajú generované adresy,
- cloud a virtualizácia abstrahujú fyzický hardware,
- MAC je relevantná iba v danom L2 domain,
- router ju nepresúva end-to-end.

### Unicast, multicast a broadcast

- unicast: jeden destination interface,
- multicast: skupina receivers,
- broadcast: všetky nodes v broadcast domain.

Ethernet broadcast address:

```text
ff:ff:ff:ff:ff:ff
```

## 4. Switch forwarding

Ethernet switch sa učí source MAC addresses z prichádzajúcich frames.

```text
frame arrives on port 3
source MAC = AA:AA:AA:AA:AA:AA
→ switch learns MAC AA... is reachable via port 3
```

Forwarding decision:

- destination MAC v table → pošli na konkrétny port,
- neznámy unicast → flood v rámci VLAN,
- broadcast/multicast podľa policy → flood alebo špecializované spracovanie,
- destination na rovnakom ingress porte → neforwarduj späť.

MAC table entries starnú. Pri presune endpointu sa switch musí preučiť.

## 5. Collision domain a broadcast domain

Moderný switched full-duplex Ethernet oddeľuje collision domain na každý port. Historické hubs zdieľali médium a používali CSMA/CD.

Broadcast domain typicky zodpovedá VLAN alebo jednému L2 segmentu. Router broadcast domain oddeľuje.

Veľký broadcast domain zvyšuje:

- ARP/broadcast traffic,
- blast radius L2 problémov,
- riziko loops,
- náročnosť troubleshooting-u.

## 6. VLAN

VLAN logicky oddeľuje L2 broadcast domains na rovnakej switch infraštruktúre.

802.1Q tag obsahuje VLAN identifikáciu a priority fields.

```text
access port
  → frames endpointu typicky bez tagu

trunk port
  → prenáša frames viacerých VLAN s tagmi
```

Pojmy access/trunk sú implementačné konvencie switchov. Native VLAN a untagged traffic musia byť nakonfigurované konzistentne na oboch stranách.

VLAN nie je automaticky bezpečnostná hranica bez správnej switch, routing a firewall policy.

## 7. ARP účel

Host má IPv4 packet pre next-hop IP, ale Ethernet frame potrebuje destination MAC.

```text
Routing decision
  → next hop 192.0.2.1 cez eth0
  → aká MAC patrí 192.0.2.1?
  → ARP
```

ARP request je broadcast:

```text
Who has 192.0.2.1? Tell 192.0.2.10
```

Owner IP odpovie unicast ARP reply so svojou MAC adresou.

Výsledok sa uloží do neighbor cache.

## 8. ARP iba pre lokálny next hop

Ak destination IP leží mimo lokálneho prefixu, host nehľadá MAC remote servera. Hľadá MAC default gateway alebo iného next hopu.

```text
Destination: 203.0.113.20
Route: via 192.0.2.1
ARP target: 192.0.2.1
```

Toto je kľúčové rozlíšenie medzi L2 a L3.

## 9. Neighbor cache

Linux:

```bash
ip neigh
ip neigh show dev eth0
```

Typické stavy:

- `INCOMPLETE` — resolution prebieha,
- `REACHABLE` — nedávno potvrdený neighbor,
- `STALE` — entry existuje, ale reachability sa musí pri použití overiť,
- `DELAY` a `PROBE` — aktívne overovanie,
- `FAILED` — resolution zlyhala,
- `PERMANENT` — statická entry.

Stav `STALE` nie je automaticky chyba. Je súčasťou Neighbor Unreachability Detection modelu.

## 10. Gratuitous ARP

Gratuitous ARP oznamuje alebo overuje vlastnú IPv4-to-MAC väzbu bez predchádzajúceho requestu.

Použitie:

- failover virtual IP,
- aktualizácia neighbor caches po presune služby,
- duplicate address detection v niektorých implementáciách,
- oznamovanie MAC zmeny.

Pri HA failover-e môže pomalá alebo blokovaná aktualizácia ARP cache spôsobiť, že traffic pokračuje na starý node.

## 11. Proxy ARP

Router alebo host odpovie na ARP request za inú IP adresu a následne traffic routuje.

Proxy ARP môže prepojiť segmenty bez zmeny host konfigurácie, ale skrýva L3 hranicu a komplikuje troubleshooting. Používa sa iba v špecifických designs.

## 12. ARP spoofing a bezpečnosť

ARP nemá silnú autentifikáciu. Útočník v rovnakom L2 domain môže posielať falošné ARP replies a presmerovať traffic.

Riziká:

- man-in-the-middle,
- denial of service,
- traffic interception,
- gateway impersonation.

Mitigácie podľa prostredia:

- switch port security,
- DHCP snooping + Dynamic ARP Inspection,
- menšie VLANs,
- encryption vyšších vrstiev,
- statické entries iba pri veľmi kontrolovaných scenároch,
- monitoring nečakaných MAC/IP zmien.

TLS alebo SSH host-key verification chráni vyššiu vrstvu aj v prípade kompromitovaného L2 pathu.

## 13. L2 loops a Spanning Tree

Ethernet frame nemá všeobecný hop limit ako IP TTL. Fyzická alebo logická L2 loop môže vytvoriť broadcast storm a MAC table instability.

Spanning Tree Protocol blokuje redundantné paths tak, aby aktívna L2 topológia zostala bez slučiek, pričom redundancia môže byť použitá po failure.

Symptómy loopu:

- vysoký broadcast traffic,
- switch CPU load,
- MAC flapping,
- packet loss,
- rozsiahla nestabilita VLAN.

## 14. Linux interface a neighbor diagnostika

```bash
ip -br link
ip -s link show dev eth0
ip addr show dev eth0
ip neigh show dev eth0
ethtool eth0
ethtool -S eth0
```

Sleduj:

- administratívny stav,
- carrier,
- speed/duplex,
- RX/TX errors a drops,
- MTU,
- neighbor states,
- driver counters.

Vo virtualizácii nemusí `ethtool` zobrazovať fyzický link rovnakým spôsobom ako na bare metal hoste.

## 15. Packet capture

ARP capture:

```bash
sudo tcpdump -eni eth0 arp
```

Ethernet headers pri IP traffiku:

```bash
sudo tcpdump -eni eth0 host 192.0.2.1
```

`-e` zobrazí link-layer header. `-n` vypne name resolution.

Otázky:

- odchádza ARP request?
- prichádza reply?
- reply obsahuje očakávanú MAC?
- neodpovedá viac zariadení na jednu IP?
- mení sa source MAC neočakávane?

## 16. Troubleshooting scenár: route existuje, gateway je nedostupná

```bash
ip route get 198.51.100.10
ip neigh show 192.0.2.1
ping -c 1 192.0.2.1
sudo arping -I eth0 192.0.2.1
sudo tcpdump -eni eth0 arp
```

Možné príčiny:

- nesprávna VLAN,
- link down,
- gateway offline,
- duplicate IP,
- switch port policy,
- ARP filtering,
- interface v inom network namespace,
- chybná IP/prefix konfigurácia.

`ip route` potvrdzuje routing state, nie úspešnú L2 reachability next hopu.

## 17. Troubleshooting scenár: IP failover nefunguje okamžite

Po presune virtual IP na nový node:

1. over, že nový node IP skutočne vlastní,
2. odošli gratuitous ARP,
3. sleduj neighbor cache klienta/gateway,
4. over switch MAC table,
5. zachyť traffic na starom aj novom node,
6. skontroluj anti-spoofing policy vo virtualizácii alebo cloude.

Cloud networking nemusí používať klasické L2 správanie dostupné používateľovi. Provider môže virtual IP presun riadiť control plane mechanizmom.

## 18. Časté omyly

### „Switch posiela frame podľa IP adresy“

Bežný L2 switch forwarduje podľa destination MAC. L3 switch môže zároveň routovať IP, ale ide o inú funkciu.

### „ARP nájde MAC remote servera“

ARP rieši iba lokálny next hop.

### „MAC adresa je nezmeniteľná hardware identita“

Môže byť generovaná, spoofnutá alebo virtualizovaná.

### „VLAN je to isté ako subnet“

VLAN je L2 broadcast domain, subnet je L3 prefix. Často sa mapujú 1:1, ale nie je to technická nutnosť.

### „STALE neighbor entry znamená výpadok“

Nie. Je to normálny cache state.

## 19. Kontrolné otázky

1. Aké polia potrebuje Ethernet frame na forwarding?
2. Ako sa switch učí MAC table?
3. Aký je rozdiel medzi collision a broadcast domain?
4. Načo slúži VLAN tag?
5. Prečo host ARPuje gateway namiesto remote servera?
6. Čo znamenajú neighbor states `INCOMPLETE`, `STALE` a `FAILED`?
7. Načo slúži gratuitous ARP?
8. Prečo môže L2 loop spôsobiť rozsiahly výpadok?
9. Ako by si diagnostikoval chýbajúcu ARP reply?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OSI a TCP/IP model](osi-and-tcp-ip-model.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: IPv4, IPv6 a subnetting →](ipv4-ipv6-subnetting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
