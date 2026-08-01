# Routing a default gateway

<!-- CONCEPT-FIRST:START -->
## Čo je routing a default gateway

Routing je rozhodovanie, ktorým egress interface-om a cez aký next hop sa odošle IP packet. Host aj router používajú routing table a vyberajú najšpecifickejšiu zodpovedajúcu route, teda longest-prefix match. Default route `0.0.0.0/0` alebo `::/0` je iba najmenej špecifický fallback.

Route môže byť connected, statická, naučená dynamickým protokolom alebo vložená platformovým control plane-om. Výsledné forwarding rozhodnutie zahŕňa destination prefix, next hop, interface, metric a často source-address selection. Policy routing môže navyše vyberať inú table podľa source, fwmark alebo ďalších fields.

Neutrálny príklad:

```text
203.0.113.0/24 via 192.0.2.1
203.0.113.40/32 via 192.0.2.2
default via 192.0.2.254
```

Packet na `203.0.113.40` použije `/32`, nie default a ani `/24`, pretože `/32` je najšpecifickejšia. Metric rozhoduje až medzi porovnateľnými candidates; neprebije dlhší prefix.

Default gateway musí byť sama dosiahnuteľná na lokálnom linku alebo cez explicitný recursive next-hop mechanizmus. Existencia route nepreukazuje neighbor resolution ani to, že ďalší router pozná pokračovanie cesty.

End-to-end komunikácia potrebuje forward aj return path. Asymetria nemusí byť automaticky chybná, ale stateful firewall alebo NAT môže vyžadovať, aby oba directions prešli rovnakým state ownerom.

TTL pri IPv4 a hop limit pri IPv6 sa znižuje na každom routeri. Traceroute využíva expiráciu tejto hodnoty, no jeho výstup nie je úplná topologická pravda: zariadenia môžu ICMP rate-limitovať, tunely skrývať hops a load balancing meniť pozorovanú cestu.

Routing control plane a forwarding data plane sú odlišné states. Prijatá BGP route alebo zelená routing session nepreukazuje, že konkrétny packet je skutočne forwardovaný požadovanou cestou. Najpresnejší lokálny read-back je route lookup pre konkrétny destination a source.
<!-- CONCEPT-FIRST:END -->

## Atlas scenár a praktické použitie

Klient pozná destination IP `203.0.113.40`, ale musí rozhodnúť, kam packet odoslať ako ďalší hop. Routing je proces výberu egress interface, next hopu a source address podľa aktuálnych rules, route tables a packet metadata. Default gateway je iba najširšia fallback route; nie je automaticky prvým ani jediným rozhodnutím.

## Route lookup pre konkrétny packet

Linux route decision možno pozorovať:

```bash
ip route get 203.0.113.40 from 10.24.8.37
```

Výstup môže obsahovať destination, gateway, interface, source address a cache-related metadata. Tento command je silnejší než obyčajné čítanie `ip route`, pretože vykoná lookup pre konkrétny destination a voliteľný source.

Zjednodušený výber používa longest-prefix match. Ak existujú routes:

```text
203.0.113.0/24 via 10.24.8.2
203.0.113.40/32 via 10.24.8.3
0.0.0.0/0 via 10.24.8.1
```

packet na `203.0.113.40` použije `/32`, pretože je najšpecifickejšia. Metric rozhoduje medzi porovnateľnými candidates; neprebije špecifickejší prefix len preto, že má nižšie číslo.

## Connected a default route

Connected route vzniká z adresy priradenej interface-u. Pre `10.24.8.37/24` kernel vie, že `10.24.8.0/24` je dostupný priamo cez daný link. Destination mimo známych špecifických prefixov môže použiť:

```text
default via 10.24.8.1 dev eth0
```

Gateway musí byť dosiahnuteľný na linku alebo cez explicitný mechanizmus. Samotná existencia default route nepreukazuje neighbor resolution ani to, že gateway pozná ďalšiu cestu.

## Source address selection

Host s viacerými adresami alebo interfaces musí vybrať source address. Toto rozhodnutie ovplyvňuje return path, firewall policy, TLS client identity, load-balancer affinity aj logs.

```bash
ip route get 203.0.113.40
ip route get 203.0.113.40 from 10.24.9.37
```

Aplikácia môže explicitne bindnúť source IP. Policy routing môže podľa source, fwmark alebo ďalších fields použiť inú table. Preto príkaz vykonaný bez rovnakého source a namespace nemusí reprodukovať aplikačný flow.

## Policy routing

Linux spracúva `ip rule` podľa priority a vyberá route table. Bežná konfigurácia môže oddeľovať management a application traffic:

```bash
ip rule show
ip route show table main
ip route show table 100
```

Napríklad packets zo source `10.24.9.0/24` môžu používať VPN gateway, zatiaľ čo ostatné idú cez internet edge. Po zmene source addressu sa teda zmení celý path, hoci destination zostane rovnaký.

Policy routing je častý zdroj „funguje z shellu, nefunguje zo služby“. Služba môže bežať v inom network namespace, používať inú source IP alebo dostávať fwmark od cgroup/eBPF policy.

## Forward a return path

TCP spojenie potrebuje obojsmernú reachability. Forward packet môže ísť cez firewall A a response cez firewall B. Asymetria nemusí byť sama osebe chybná, ale stateful firewall alebo NAT očakáva, že oba directions uvidia rovnaký state.

```text
client → router A → firewall A → server
server → firewall B → router B → client
```

Ak firewall B nepozná connection, response môže zahodiť. Client potom vidí SYN retransmissions, hoci server SYN prijal a odoslal SYN-ACK. Capture na oboch ends je diskriminačnejší než opakované testovanie iba z klienta.

## TTL, hop limit a traceroute

IPv4 TTL a IPv6 hop limit sa znižuje na každom routeri. Pri dosiahnutí nuly router packet zahodí a typicky vráti ICMP Time Exceeded. `traceroute` alebo `tracepath` túto vlastnosť používa na odhad pathu.

```bash
tracepath 203.0.113.40
traceroute -T -p 443 203.0.113.40
```

Path output nie je úplná mapa. Router môže ICMP rate-limitovať, load balancing môže meniť hops a MPLS/tunnels môžu skryť časť infraštruktúry. Chýbajúca odpoveď jedného hopu neznamená, že router neforwarduje.

## Dynamický routing a convergence

V enterprise sieti routes často pochádzajú z OSPF, IS-IS, BGP alebo cloud control plane-u. Control plane vyhodnocuje susedov, policies a advertisements a zapisuje best path do forwarding state-u. Management UI môže ukázať prijatú route, kým data plane ju ešte nepoužíva alebo ju hardware table nemá.

Pri failoveri existuje convergence interval. Časť packetov môže smerovať na starý next hop, nové connections môžu používať nový path a stateful middleboxes môžu mať nekompatibilný state. Acceptance preto obsahuje reálny flow a nie iba stav routing session.

## Incident: iba jeden application host nemá API

Dva hosty v rovnakej pobočke používajú rovnaký DNS answer. Jeden funguje, druhý timeoutuje. Interface a gateway sú `UP`, ARP je zdravé. Zlý host má po VPN klientovi zostávajúcu `/32` route na `203.0.113.40` cez neexistujúci tunnel interface.

```bash
ip route get 203.0.113.40
ip rule show
ip route show table all
```

`route get` okamžite odlíši local route decision od upstream outage-u. Oprava odstráni stale VPN route a upraví lifecycle klienta tak, aby po disconnecte reconcilioval state. Po zmene sa overí source address, next hop, TCP/TLS a pôvodný POST request.

## Zhrnutie

Routing vyberá path pre konkrétny packet podľa najšpecifickejšej route, policy rules, source a namespace. Default route je fallback, nie univerzálne vysvetlenie. End-to-end diagnostika musí kontrolovať forward aj return path a odlíšiť control-plane informáciu od effective forwarding state-u.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: IPv4, IPv6 a subnetting](ipv4-ipv6-subnetting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: TCP a UDP →](tcp-and-udp.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
