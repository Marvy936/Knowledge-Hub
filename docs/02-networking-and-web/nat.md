# NAT

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [Routing a default gateway](routing-and-default-gateway.md), [Ports a sockets](ports-and-sockets.md), [TCP a UDP](tcp-and-udp.md)
- Súvisiace témy: firewalls, load balancing, container networking, cloud gateways, IPv6

## 1. Definícia

Network Address Translation mení source alebo destination IP adresu a často aj transportný port pri prechode packetu cez translation point.

NAT nevytvára route ani service availability. Packet musí mať platnú cestu, zodpovedajúce translation pravidlo, povolenie vo firewalle a funkčný return path.

## 2. Prečo NAT existuje

Najčastejšie dôvody:

- zdieľanie jednej verejnej IPv4 adresy viacerými internými hostmi,
- publikovanie internej služby cez externú adresu alebo port,
- prepojenie sietí s overlapping addressing,
- zachovanie alebo skrytie interného adresného plánu,
- implementácia niektorých load-balancing a service-routing modelov.

NAT sa stal bežný najmä pre nedostatok IPv4 adries. Nie je základnou požiadavkou IP routingu.

## 3. Základné typy

### SNAT — Source NAT

Mení source adresu odchádzajúceho packetu.

```text
10.0.1.10:45000
  ↓ SNAT
203.0.113.5:62001
```

Použitie: outbound internet access privátnych hostov.

### DNAT — Destination NAT

Mení destination adresu alebo port prichádzajúceho packetu.

```text
203.0.113.5:443
  ↓ DNAT
10.0.1.20:8443
```

Použitie: port forwarding alebo publikovanie internej služby.

### PAT — Port Address Translation

Viac interných flows zdieľa jednu externú adresu a rozlišuje sa preloženými portmi. Často sa neformálne nazýva NAT overload.

### Static one-to-one NAT

Stabilné mapovanie jednej adresy na inú adresu.

## 4. Stateful translation

Bežný NAT je stavový. Translation zariadenie vedie mapping flowu:

```text
inside local:   10.0.1.10:45000
inside global:  203.0.113.5:62001
outside:        198.51.100.20:443
protocol:       TCP
state/timeout:  established, 5 min...
```

Return packet sa musí vrátiť cez zariadenie, ktoré mapping pozná. Asymmetric routing môže spôsobiť, že odpoveď príde inou cestou a translation zlyhá.

## 5. Packet flow pri outbound SNAT

```text
client 10.0.1.10:45000
  ↓ default gateway
NAT gateway
  ↓ route decision + SNAT
internet source 203.0.113.5:62001
  ↓
server 198.51.100.20:443
```

Return flow:

```text
server 198.51.100.20:443
  ↓ destination 203.0.113.5:62001
NAT gateway mapping lookup
  ↓ reverse translation
client 10.0.1.10:45000
```

## 6. Packet flow pri DNAT

```text
client
  ↓ destination 203.0.113.5:443
NAT device
  ↓ DNAT to 10.0.1.20:8443
backend
```

Backend musí mať return route tak, aby odpoveď prešla cez rovnaký translation point alebo musí existovať ďalší SNAT mechanizmus.

Inak môže backend odpovedať priamo klientovi zo svojej internej adresy, ktorú klient neočakáva alebo nevie routovať.

## 7. Conntrack

Linux netfilter používa connection tracking na evidenciu flow state a NAT mappings.

Pozorovanie:

```bash
sudo conntrack -L
sysctl net.netfilter.nf_conntrack_count
sysctl net.netfilter.nf_conntrack_max
```

Pri vyčerpaní conntrack table môžu nové spojenia zlyhávať, hoci CPU, memory a listener vyzerajú zdravo.

Typické príčiny:

- veľký počet krátkych spojení,
- retry storm,
- UDP flows s dlhými timeoutmi,
- útok alebo scan,
- poddimenzovaný table limit.

## 8. NAT a TCP/UDP

Pri TCP translation zariadenie sleduje flow state a lifecycle.

Pri UDP neexistuje handshake ani explicitný close, preto NAT mapping zaniká podľa inactivity timeoutu. Neskorá odpoveď môže prísť po expirácii mappingu a byť zahodená.

Aplikácie používajú keepalive, refresh alebo protocol-specific traversal mechanizmy, ak potrebujú mapping udržať.

## 9. Hairpin NAT

Interný klient pristupuje na verejnú adresu služby, ktorá sa prekladá späť do rovnakej internej siete.

```text
10.0.1.30
  ↓ 203.0.113.5:443
NAT gateway
  ↓ 10.0.1.20:8443
backend
```

Aby return path zostal symetrický, môže byť potrebný aj SNAT. Bez hairpin podpory môže služba fungovať zvonka, ale nie z internej siete cez verejné meno.

Alternatívou je split-horizon DNS s internou adresou.

## 10. NAT a checksums

Zmena IP adresy alebo portu mení fields zahrnuté v IP alebo transportnom checksum. NAT implementácia musí checksum korektne prepočítať alebo využiť offload mechanizmy.

Packet capture môže ukazovať zdánlivo neplatné checksums na odchádzajúcom hoste kvôli checksum offloadu; nie vždy ide o reálnu chybu na wire.

## 11. Linux netfilter hooks

Zjednodušený model:

```text
incoming packet
  ↓ PREROUTING — typické DNAT
routing decision
  ↓ INPUT alebo FORWARD
  ↓ POSTROUTING — typické SNAT/MASQUERADE
outgoing interface
```

Lokálne generovaný traffic používa aj `OUTPUT` hook.

Moderná konfigurácia používa nftables; legacy prostredie môže používať iptables frontend.

## 12. MASQUERADE vs. explicit SNAT

`MASQUERADE` dynamicky používa adresu outbound interface. Je vhodný pre linky s meniacou sa adresou.

Explicitný SNAT používa definovanú source adresu a býva vhodnejší pri stabilnom adresovaní.

Konceptuálny nftables príklad:

```nft
chain postrouting {
    type nat hook postrouting priority srcnat;
    oifname "eth0" ip saddr 10.0.0.0/8 masquerade
}
```

Konfigurácia musí byť prispôsobená konkrétnej distribúcii, rulesetu a forwarding policy.

## 13. Port forwarding

Konceptuálny DNAT:

```nft
chain prerouting {
    type nat hook prerouting priority dstnat;
    tcp dport 443 dnat to 10.0.1.20:8443
}
```

Samotný DNAT nestačí. Treba overiť:

- IP forwarding,
- FORWARD chain policy,
- backend route,
- listener na target porte,
- health a return traffic,
- security policy.

## 14. Container networking

Pri publikovaní container portu môže host vytvoriť DNAT alebo proxy path:

```text
host:8080
  ↓ NAT/proxy
container-IP:80
```

Treba rozlišovať:

- container listener,
- bridge network,
- host port,
- host firewall,
- orchestrator service abstraction.

NAT môže skryť pôvodnú source IP, čo ovplyvní audit, rate limiting a aplikačnú policy.

## 15. Cloud NAT

Cloud NAT gateway typicky poskytuje outbound internet access privátnym subnetom bez inbound publikovania hostov.

Treba sledovať:

- počet dostupných source ports,
- počet public IP adries,
- per-destination limits,
- connection count,
- idle timeouty,
- availability-zone architektúru,
- náklady na spracované dáta.

NAT gateway nie je automaticky firewall ani inbound load balancer.

## 16. NAT exhaustion

Jedna verejná IP poskytuje konečný počet source-port mappings pre konkrétny protocol a destination model.

Symptómy:

- nové outbound spojenia timeoutujú,
- existujúce spojenia fungujú,
- problém sa objaví iba pri vysokej concurrency,
- niektoré destinations zlyhávajú viac než iné.

Možné nápravy:

- connection pooling a keep-alive,
- zníženie retry stormu,
- viac public source adries,
- rozloženie gateways,
- priama private connectivity,
- IPv6 bez NAT44.

## 17. NAT traversal

Inbound spojenie na klienta za NAT je problematické, pretože mapping typicky vzniká outbound trafficom.

Mechanizmy:

- static port forwarding,
- UPnP/NAT-PMP/PCP,
- STUN na zistenie external mappingu,
- TURN relay,
- ICE kombinujúci kandidátov.

Používa sa pri VoIP, WebRTC, P2P a gaming komunikácii.

## 18. NAT a IPv6

IPv6 bol navrhnutý s dostatočným adresným priestorom na end-to-end addressing. Firewall a policy zostávajú potrebné, ale NAT66 nie je štandardnou náhradou za security.

IPv6 privacy addressing alebo prefix delegation riešia iné problémy než NAT44.

Prechodové mechanizmy môžu zahŕňať NAT64/DNS64, kde IPv6-only klient komunikuje s IPv4 serverom cez preklad.

## 19. Security trade-offs

NAT môže neúmyselne obmedziť unsolicited inbound traffic, ale nie je plnohodnotná security policy.

Riziká:

- široký port forwarding,
- skrytá source identity,
- nedostatočný logging mappings,
- vyčerpanie state table,
- chybné pravidlo s veľkým blast radius,
- obchádzanie segmentácie hairpin cestou.

Explicitný stateful firewall musí definovať, čo je povolené.

## 20. Diagnostický postup

Outbound spojenie z privátneho hosta zlyháva:

```bash
ip route get <destination>
ss -tan
sudo nft list ruleset
sudo conntrack -L
sudo tcpdump -ni <inside-iface> host <client-ip>
sudo tcpdump -ni <outside-iface> host <destination-ip>
```

Postup:

1. klient má správnu route na NAT gateway,
2. packet príde na inside interface,
3. forwarding je povolený,
4. NAT pravidlo sa zhoduje,
5. packet odchádza s preloženou source adresou,
6. reply sa vracia na translation point,
7. conntrack mapping existuje,
8. reverse translation doručí packet klientovi.

## 21. Časté omyly

### „NAT a firewall sú to isté“

Nie. NAT mení adresy; firewall rozhoduje, či traffic povolí.

### „DNAT automaticky sprístupní službu“

Nie bez forward policy, listenera a funkčného return pathu.

### „Privátna IP znamená bezpečnú službu“

Nie. Môže byť dostupná cez VPN, peering, compromised host alebo chybné forwarding pravidlo.

### „NAT vždy skryje internú topológiu“

Nie úplne. Aplikačné payloady, DNS, timing a ďalšie metadata ju môžu odhaliť.

### „IPv6 potrebuje NAT kvôli bezpečnosti“

Nie. Bezpečnosť zabezpečuje firewall a access policy.

## 22. Kontrolné otázky

1. Aký je rozdiel medzi SNAT a DNAT?
2. Prečo NAT potrebuje stav?
3. Prečo asymmetric routing rozbíja stateful translation?
4. Aký je rozdiel medzi MASQUERADE a explicitným SNAT?
5. Prečo DNAT pravidlo samo nestačí na publikovanie služby?
6. Ako vzniká NAT port exhaustion?
7. Čo je hairpin NAT a kedy je potrebný?
8. Ako conntrack súvisí s NAT?
9. Prečo NAT nie je firewall?
10. Aký problém rieši NAT64/DNS64?
