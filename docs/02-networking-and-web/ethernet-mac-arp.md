# Ethernet, MAC a ARP

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [OSI a TCP/IP model](osi-and-tcp-ip-model.md), [Linux networking](../01-linux-and-systems/linux-networking.md)
- Súvisiace témy: switching, VLAN, IPv4, routing, NDP, packet capture, high availability

## 1. Definícia

Ethernet je skupina linkových technológií na prenos **frames** v lokálnom L2 segmente. MAC adresa je linkový identifikátor používaný pri doručení frame-u v danom broadcast domaine. ARP mapuje IPv4 adresu lokálneho next hopu na MAC adresu potrebnú pre Ethernet frame.

Tieto mechanizmy riešia iba jeden lokálny hop. Ethernet switch nerozhoduje, kadiaľ má IP packet prejsť cez Internet. ARP nehľadá MAC adresu vzdialeného servera za routerom. Ich úlohou je dostať frame k najbližšiemu L2 endpointu, ktorý má packet ďalej spracovať.

## 2. Lokálny-hop mentálny model

Pred odoslaním IPv4 packetu host najprv vykoná routing decision. Výsledkom je výber egress interface, source IP a next-hop IP. Až potom potrebuje linková vrstva určiť destination MAC.

```text
Aplikácia vytvorí dáta
  ↓
IP stack vytvorí packet
  ↓
Routing table vyberie interface a next hop
  ↓
ARP/neighbor cache poskytne next-hop MAC
  ↓
Ethernet vytvorí frame
  ↓
Switch forwarduje podľa destination MAC
```

Ak je destination IP v lokálnom prefixe, next hopom je typicky samotný destination host. Ak je mimo lokálneho prefixu, next hopom je gateway. V oboch prípadoch Ethernet rieši iba doručenie k tomuto lokálnemu next hopu.

## 3. Ethernet frame

Zjednodušený Ethernet frame obsahuje:

```text
Preamble a start delimiter
Destination MAC
Source MAC
Voliteľný 802.1Q VLAN tag
EtherType alebo length
Payload
Frame Check Sequence
```

Destination MAC určuje, komu má byť frame v lokálnom segmente doručený. Source MAC umožňuje switchu naučiť sa, cez ktorý port je source dostupný. EtherType identifikuje vyšší protokol, napríklad IPv4, IPv6 alebo ARP.

Frame Check Sequence slúži na detekciu poškodenia frame-u na linke. Chybný frame sa typicky zahodí bez toho, aby Ethernet sám vykonal retransmission. Obnovu môže zabezpečiť vyššia vrstva, napríklad TCP, alebo ju nemusí zabezpečiť nikto.

## 4. MTU a veľkosť frame-u

Ethernet interface má Maximum Transmission Unit, ktorá typicky určuje maximálnu veľkosť L3 payloadu bez potreby fragmentácie alebo iného spracovania. Bežná hodnota Ethernet MTU je 1500 bytes, ale VLAN, tunnels, overlays alebo jumbo frames môžu meniť efektívny limit.

MTU nie je to isté ako celková veľkosť Ethernet frame-u. Frame obsahuje aj linkové headers a trailer. Pri tunelovaní sa k pôvodnému packetu pridávajú ďalšie headers, preto musí byť underlay MTU dostatočná alebo musí fungovať path MTU discovery.

Chybný MTU model môže vytvoriť stav, v ktorom malé packets fungujú, ale väčšie prenosy timeoutujú. Tento failure sa môže mylne pripisovať aplikácii alebo TLS, hoci vzniká na linkovej alebo network vrstve.

## 5. MAC adresy

Bežná Ethernet MAC adresa má 48 bitov a zapisuje sa napríklad:

```text
00:11:22:33:44:55
```

MAC adresa nie je spoľahlivá globálna identita zariadenia. Môže byť softvérovo zmenená, generovaná hypervisorom alebo runtime-om, zdieľaná vo failover modeli alebo abstrahovaná cloudovou sieťou.

Jej význam je lokálny. Router pri preposlaní IP packetu vytvorí nový linkový frame s MAC adresami platnými pre ďalší segment. Pôvodná source MAC klienta sa preto cez routované hops neprenáša.

## 6. Unicast, multicast a broadcast

**Unicast frame** je adresovaný jednému destination MAC endpointu. Switch ho pri známom destination forwarduje na konkrétny port.

**Broadcast frame** používa destination:

```text
ff:ff:ff:ff:ff:ff
```

Switch ho floodne na relevantné ports v rámci VLAN okrem ingress portu. ARP request je typický broadcast.

**Multicast frame** je určený skupine receiverov. Praktické forwarding správanie môže byť ovplyvnené multicast snoopingom a ďalšou switch policy. Bez správneho state môže byť multicast floodovaný podobne ako broadcast.

Broadcast a multicast majú väčší fan-out než unicast. Veľký broadcast domain preto zvyšuje množstvo práce, ktorú musia spracovať všetky pripojené endpointy.

## 7. Ako sa switch učí MAC table

L2 switch sa učí zo **source MAC** prichádzajúcich frames:

```text
frame prišiel na port 3
source MAC = AA:AA:AA:AA:AA:AA
→ MAC AA... je momentálne dostupná cez port 3 vo VLAN 20
```

Tento záznam sa uloží do forwarding database, často nazývanej MAC table alebo CAM table. Záznam je viazaný minimálne na MAC, VLAN a port a po čase bez trafficu zostarne.

Switch sa teda neučí z destination MAC ani z IP adresy. Source learning mu umožňuje vytvoriť spätnú cestu pre budúce frames.

Ak sa endpoint presunie na iný port, nové source frames majú tabuľku aktualizovať. Rýchle striedanie rovnakej MAC medzi portmi sa označuje ako MAC flapping a môže signalizovať loop, chybné teaming/bonding nastavenie alebo duplikovanú virtuálnu identitu.

## 8. Forwarding decision

Po prijatí frame-u switch typicky vykoná:

1. určenie ingress portu a VLAN kontextu,
2. source MAC learning,
3. lookup destination MAC vo forwarding table,
4. výber egress správania,
5. aplikáciu port/VLAN/security policy,
6. odoslanie alebo zahodenie frame-u.

Možné výsledky:

- **known unicast** — frame ide na známy egress port,
- **unknown unicast** — destination MAC nie je v table a frame sa floodne v rámci VLAN,
- **broadcast** — frame sa floodne v broadcast domaine,
- **multicast** — forwarduje sa podľa multicast state alebo sa floodne,
- **same-port destination** — switch frame nepošle späť na rovnaký port,
- **policy drop** — frame zablokuje VLAN, port-security alebo iná kontrola.

Unknown-unicast flooding je normálne prechodné správanie, kým sa switch destination MAC nenaučí. Trvalé vysoké flooding môže znamenať krátke aging intervaly, asymetrický traffic, MAC table pressure alebo neštandardnú topológiu.

## 9. Collision domain a broadcast domain

Historické Ethernet hubs zdieľali jedno médium a collision domain. Endpointy používali CSMA/CD a mohli sa navzájom rušiť.

Moderný switched full-duplex Ethernet má typicky samostatný collision domain na každom switch porte. Collision counters dnes skôr signalizujú duplex mismatch, chybný link alebo starší/shared-media segment než normálne fungovanie siete.

Broadcast domain je scope, v ktorom sa šíria broadcast frames. Typicky zodpovedá jednej VLAN. Router alebo L3 boundary broadcasty medzi subnetmi štandardne neforwarduje.

Veľký broadcast domain zväčšuje:

- ARP a discovery traffic,
- blast radius broadcast stormu,
- počet endpointov spracúvajúcich každý broadcast,
- rozsah duplicate-IP a spoofing problémov,
- náročnosť izolácie failure-u.

## 10. VLAN ako logický L2 segment

VLAN oddeľuje viac broadcast domains na spoločnej switch infraštruktúre. Rovnaká fyzická linka môže niesť frames viacerých VLAN, ale switch ich udržiava v oddelených forwarding kontextoch.

802.1Q tag nesie VLAN identifier a priority-related fields. Frame endpointu na access porte býva typicky untagged; switch ho interne priradí k access VLAN. Trunk port prenáša viac VLAN a frames sú typicky tagged.

```text
endpoint ── untagged ── access port [VLAN 20]
                         switch
switch ── tagged VLAN 20/30/40 ── trunk ── switch/router
```

Native alebo untagged VLAN na trunku musí byť konzistentná na oboch stranách. Mismatch môže presúvať untagged traffic do iného broadcast domainu, než administrátor očakáva.

VLAN je L2 segmentácia, nie kompletná security policy. Inter-VLAN routing, trunk configuration, switch ACL, firewall a identity controls určujú, či VLAN hranica poskytuje požadovanú izoláciu.

## 11. VLAN a subnet nie sú to isté

VLAN je linkový broadcast domain. Subnet je IP prefix. Často sa navrhujú v pomere 1:1, pretože to zjednodušuje routing, DHCP a troubleshooting, ale nejde o technickú identitu.

Jeden L2 segment môže obsahovať viac IP prefixov. Jeden IP prefix môže byť pri neštandardnom dizajne rozšírený cez viac L2 technológií. Takéto návrhy zvyšujú komplexitu neighbor resolution, failoveru a failure domainov.

Pri diagnostike preto treba overiť obidve vrstvy:

```text
Som v správnej VLAN/broadcast domaine?
A zároveň:
Mám správnu IP adresu, prefix a route?
```

## 12. ARP účel a workflow

Ethernet frame potrebuje destination MAC, ale routing decision poskytuje next-hop IP. ARP túto medzeru preklenie pre IPv4.

```text
IP packet má ísť cez eth0 na next hop 192.0.2.1
  ↓
neighbor cache nemá použiteľnú entry
  ↓
ARP request: Who has 192.0.2.1? Tell 192.0.2.10
  ↓ broadcast
owner 192.0.2.1 odpovie svojou MAC
  ↓ unicast ARP reply
kernel uloží IP → MAC mapping
  ↓
queued IP packet sa zabalí do Ethernet frame-u
```

ARP neoveruje vlastníctvo IP kryptograficky. Host spravidla dôveruje linkovým správam podľa kernelovej neighbor policy a aktuálneho state.

## 13. ARP iba pre next hop

Ak destination patrí do lokálneho on-link prefixu, ARP targetom je destination IP. Ak destination leží mimo lokálneho prefixu, routing table vyberie gateway a ARP targetom je gateway.

```text
Destination IP: 203.0.113.20
Selected route: via 192.0.2.1 dev eth0
ARP target:     192.0.2.1
Ethernet dst:   MAC gateway
IP dst:         203.0.113.20
```

Toto je zásadné rozlíšenie. Nesprávne široký prefix môže spôsobiť, že host považuje vzdialenú IP za on-link a márne ARPuje priamo namiesto použitia gateway.

## 14. Neighbor cache a jej stavy

Linux spravuje ARP mappings v neighbor table:

```bash
ip neigh show
ip neigh show dev eth0
```

Dôležité stavy:

- `INCOMPLETE` — resolution prebieha, ale mapping ešte nie je známy,
- `REACHABLE` — reachability bola nedávno potvrdená,
- `STALE` — mapping existuje, ale pri ďalšom použití môže byť potrebné overenie,
- `DELAY` — kernel krátko čaká na potvrdenie vyššou vrstvou pred aktívnym probingom,
- `PROBE` — odosielajú sa aktívne probes,
- `FAILED` — resolution alebo reachability overenie zlyhalo,
- `PERMANENT` — statická entry bez bežného aging lifecycle.

`STALE` nie je failure. Je to normálny cache stav. Dôležitý je prechod pri reálnom trafficu a to, či entry končí ako `REACHABLE` alebo `FAILED`.

## 15. Neighbor reachability verzus ARP mapping

Samotná existencia IP-to-MAC mappingu ešte nedokazuje, že endpoint je funkčný. MAC môže byť stará, endpoint môže byť vypnutý, switch path môže byť chybná alebo host môže packets zahadzovať.

Neighbor state sa preto snaží reprezentovať aj reachability, nielen statické mapovanie. Vyššia vrstva môže kernelu nepriamo potvrdiť, že komunikácia funguje, alebo kernel vykoná aktívne probing.

Pri troubleshooting-u treba rozlišovať:

```text
mapping existuje
≠ frame sa dostal k endpointu
≠ endpoint spracoval packet
≠ aplikácia odpovedala
```

## 16. Gratuitous ARP a failover

Gratuitous ARP oznamuje vlastnú IPv4-to-MAC väzbu bez predchádzajúceho requestu. Používa sa pri presune virtual IP, aktualizácii neighbor caches a niektorých duplicate-address detection postupoch.

Pri HA failover-e môže nový node prevziať IP, ale okolité zariadenia ešte používajú starú MAC:

```text
VIP pred failoverom → MAC node A
VIP po failoveri    → MAC node B
neighbor caches     → stále MAC node A
```

Nový node preto odošle gratuitous ARP, aby oznámil novú väzbu. Úspech závisí od toho, či switches, hosty a cloud/virtualization anti-spoofing policy zmenu akceptujú.

V niektorých cloud sieťach klasický L2 failover nefunguje podľa fyzického Ethernet modelu. Provider control plane môže vyžadovať presun secondary IP alebo zmenu route namiesto gratuitous ARP.

## 17. Duplicate IP

Duplicate IP vznikne, keď viac endpointov tvrdí, že vlastní rovnakú IPv4 adresu. Výsledok môže byť prerušovaný, pretože neighbor cache rôznych klientov môže obsahovať rozdielne MAC adresy a ARP replies môžu prichádzať od viacerých hostov.

Typické symptómy:

- spojenia náhodne smerujú na iný endpoint,
- neighbor entry sa často mení,
- switch vidí traffic z rôznych MAC,
- klienti majú rozdielne výsledky,
- failover pôsobí nestabilne.

Diagnostika:

```bash
ip neigh show <IP>
sudo arping -D -I eth0 <IP>
sudo tcpdump -eni eth0 arp
```

Treba hľadať viac odpovedí na jeden ARP request a korelovať source MAC s inventárom, hypervisorom alebo switch portom.

## 18. Proxy ARP

Pri proxy ARP router alebo host odpovie na ARP request za IP, ktorá fyzicky nepatrí jeho lokálnemu interface-u, a následne packets routuje ďalej.

Tento mechanizmus môže umožniť komunikáciu bez zmeny konfigurácie endpointu, ale skrýva L3 hranicu. Host si myslí, že destination je lokálne dostupná, hoci traffic prechádza routerom.

Proxy ARP komplikuje troubleshooting, subnet design a failure analysis. Má sa používať len v návrhoch, kde je jeho účel explicitný a zdokumentovaný.

## 19. ARP spoofing a poisoning

ARP nemá vstavanú silnú autentifikáciu. Endpoint v rovnakom L2 segmente môže poslať falošnú ARP informáciu a pokúsiť sa zmeniť neighbor cache obete.

Možné následky:

- man-in-the-middle,
- gateway impersonation,
- traffic interception,
- denial of service,
- presmerovanie na škodlivý endpoint.

Mitigácie sú vrstvené:

- menšie a jasne segmentované VLANs,
- DHCP snooping a Dynamic ARP Inspection tam, kde ich switch podporuje,
- port security a anti-spoofing policy,
- monitoring neočakávaných IP/MAC zmien,
- šifrovanie a peer authentication vo vyšších vrstvách,
- minimalizácia dôvery v samotnú sieťovú cestu.

TLS certificate validation alebo SSH host-key verification môžu chrániť identitu vyššej vrstvy aj pri kompromitovanom L2 path-e.

## 20. L2 loops a Spanning Tree

Ethernet frame nemá všeobecný hop limit porovnateľný s IP TTL. Ak redundantné links vytvoria aktívnu L2 slučku, broadcast alebo unknown-unicast frame môže cirkulovať a množiť sa.

Následkom môže byť:

- broadcast storm,
- vysoké CPU switchov,
- MAC flapping,
- vyčerpanie link capacity,
- rozsiahly packet loss,
- nestabilita celej VLAN.

Spanning Tree Protocol vytvára loop-free aktívnu topológiu tým, že niektoré redundantné paths blokuje. Pri failure môže odblokovať náhradnú path podľa svojej konvergencie a policy.

STP nie je náhrada za správny dizajn. Nesprávna root bridge voľba, vypnuté ochrany alebo edge port pripojený k ďalšiemu switchu môžu vytvoriť významný failure domain.

## 21. Port security a anti-spoofing

Switch alebo virtual network môže obmedziť, ktoré MAC adresy sú povolené na konkrétnom porte. Takáto politika chráni pred nečakanými endpointmi, ale môže zablokovať legitímny failover, nested virtualization alebo container networking.

Pri zavádzaní port security treba poznať:

- očakávaný počet MAC na porte,
- virtual machine a container behavior,
- bonding/teaming failover,
- virtual IP model,
- reakciu pri violation,
- recovery a audit postup.

Bez tohto kontextu môže bezpečnostná kontrola vytvoriť výpadok, ktorý vyzerá ako chýbajúca ARP reply alebo jednostranný packet loss.

## 22. Linux diagnostické observation points

Základný stav:

```bash
ip -br link
ip -s link show dev eth0
ip addr show dev eth0
ip neigh show dev eth0
ethtool eth0
ethtool -S eth0
```

Tieto nástroje pozorujú odlišné vrstvy:

- `ip link` — administratívny stav, carrier, MTU a link flags,
- `ip -s link` — RX/TX counters, errors a drops,
- `ip addr` — L3 addresses a prefixes,
- `ip neigh` — neighbor mappings a reachability state,
- `ethtool` — driver/link properties,
- `ethtool -S` — device-specific counters.

Vo virtualizácii môže guest vidieť iba virtuálny interface. Fyzické link errors, switch forwarding a provider anti-spoofing state potom vyžadujú ďalší observation point mimo guest OS.

## 23. Packet capture Ethernetu a ARP

ARP capture:

```bash
sudo tcpdump -eni eth0 arp
```

Linkový header pri IP trafficu:

```bash
sudo tcpdump -eni eth0 host 192.0.2.1
```

`-e` zobrazí Ethernet header a `-n` vypne name resolution. Pri analýze sleduj:

1. či ARP request odchádza na správnom interface,
2. či cieľová IP v requeste zodpovedá selected next hopu,
3. či prichádza reply,
4. či odpovedá jedna alebo viac MAC adries,
5. či source MAC zodpovedá očakávanému endpointu,
6. či po resolution odchádzajú IP frames na získanú MAC,
7. či capture prebieha v správnom network namespace a VLAN kontexte.

Packet capture na hoste nemusí vidieť traffic v inom namespace alebo traffic spracovaný mimo pozorovaného interface-u.

## 24. Troubleshooting: route existuje, gateway je nedostupná

Začni routing decision:

```bash
ip route get 198.51.100.10
```

Potom over lokálny hop:

```bash
ip link show dev eth0
ip addr show dev eth0
ip neigh show 192.0.2.1
sudo arping -I eth0 192.0.2.1
sudo tcpdump -eni eth0 arp
```

Hypotézy:

- interface nemá carrier alebo je administratívne down,
- host je v nesprávnej VLAN,
- source IP/prefix je chybný,
- gateway nie je v skutočnosti on-link,
- ARP request neodchádza z očakávaného namespace,
- reply blokuje switch alebo virtual network policy,
- gateway je offline,
- existuje duplicate IP,
- MTU alebo link errors spôsobujú ďalší failure po úspešnom ARP.

`ip route` dokazuje iba existenciu lokálneho routing state. Nedokazuje úspešnú L2 reachability next hopu.

## 25. Troubleshooting: failover VIP nefunguje

Pri presune virtual IP:

1. over, že nový node IP skutočne vlastní,
2. over správny source interface a VLAN,
3. zachyť gratuitous ARP na novom node,
4. skontroluj neighbor cache klienta alebo gateway,
5. skontroluj switch MAC table a MAC move,
6. zachyť ingress traffic na starom aj novom node,
7. over cloud/hypervisor anti-spoofing policy,
8. over, či aplikácia na novom node počúva a je pripravená.

Tento postup oddeľuje L2 aktualizáciu od aplikačnej readiness. Úspešná zmena ARP mappingu ešte neznamená, že nová služba prijíma traffic.

## 26. Anti-patterny

### ARP cache sa pri každom probléme bezhlavo vymaže

Vymazanie neighbor entry môže dočasne zmeniť symptóm, ale odstráni diagnostický dôkaz. Najprv treba zaznamenať mapping, state, čas a packet capture.

### Statická ARP entry ako univerzálna oprava

Statická entry môže obísť dynamický failure, ale vytvára skrytý desired state a komplikuje failover. Je vhodná iba v kontrolovanom návrhu.

### VLAN sa považuje za úplnú bezpečnostnú hranicu

Bez správneho trunkingu, inter-VLAN firewallu, switch policy a endpoint controls môže byť izolácia neúplná.

### MAC adresa sa používa ako dôveryhodná identita používateľa alebo zariadenia

MAC možno spoofnúť a jej scope je lokálny. Autentifikácia má používať silnejšie identity a kryptografické mechanizmy.

## 27. Praktický mini-lab

Na testovacom Linux hoste:

```bash
ip route get <remote-ip>
ip neigh show
sudo tcpdump -eni <iface> arp
ping -c 1 <gateway-ip>
ip neigh show <gateway-ip>
```

Zaznamenaj:

- selected egress interface,
- selected next-hop IP,
- ARP request source IP/MAC,
- ARP reply source IP/MAC,
- neighbor state pred a po trafficu,
- Ethernet destination MAC následného IP frame-u.

Potom zopakuj test pre destination v rovnakom subnete a destination mimo subnetu. Porovnaj, ktorú IP host ARPuje v každom prípade.

## 28. Kontrolné otázky

1. Aký je rozdiel medzi Ethernet frame-om a IP packetom?
2. Z ktorého poľa sa switch učí MAC table?
3. Čo sa stane pri unknown-unicast destination?
4. Aký je rozdiel medzi collision domain a broadcast domain?
5. Ako access a trunk port pracujú s VLAN tagom?
6. Prečo VLAN a subnet nie sú technicky totožné?
7. Prečo host pri remote destination ARPuje gateway?
8. Čo znamenajú neighbor states `INCOMPLETE`, `STALE`, `PROBE` a `FAILED`?
9. Ako gratuitous ARP pomáha pri virtual-IP failover-e?
10. Ako rozpoznáš duplicate IP z packet capture?
11. Prečo je L2 loop nebezpečný aj bez vysokej aplikačnej záťaže?
12. Ktoré vyššie vrstvy chránia identitu komunikácie pri ARP spoofingu?

## 29. Zhrnutie

Ethernet doručuje frames v jednom lokálnom L2 segmente. Switch sa učí source MAC adresy, forwarduje known unicast a flooduje broadcast alebo unknown unicast v rámci VLAN. Routing určí next-hop IP a ARP ho preloží na destination MAC. Praktická diagnostika preto musí oddeliť route selection, VLAN kontext, link state, neighbor resolution, switch forwarding a pripravenosť vyššej vrstvy.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OSI a TCP/IP model](osi-and-tcp-ip-model.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: IPv4, IPv6 a subnetting →](ipv4-ipv6-subnetting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
