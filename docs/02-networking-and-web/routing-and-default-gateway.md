# Routing a default gateway

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [IPv4, IPv6 a subnetting](ipv4-ipv6-subnetting.md), [Ethernet, MAC a ARP](ethernet-mac-arp.md)
- Súvisiace témy: policy routing, dynamic routing, ECMP, NAT, firewally, cloud route tables

## 1. Definícia

Routing je proces výberu cesty pre IP packet podľa destination adresy a ďalších policy vstupov. Výsledkom routing decision nie je dôkaz dostupnosti cieľa; je to lokálne rozhodnutie, ktoré určí egress interface, next hop, source address a ďalšie forwarding parametre.

Default gateway je next hop použitý vtedy, keď pre destination neexistuje špecifickejšia route v aktuálnom routing-policy kontexte.

```text
packet destination
  ↓
policy rules vyberú routing table
  ↓
longest-prefix match vyberie route
  ↓
route určí egress interface, next hop a source hint
  ↓
neighbor resolution doručí frame k next hopu
  ↓
ďalší router rozhoduje znova
```

## 2. Route ako rozhodovací objekt

Route typicky obsahuje:

- destination prefix,
- route type,
- next hop alebo priamy egress interface,
- metric alebo preference,
- source-address hint,
- protocol alebo origin,
- scope,
- routing table,
- voliteľné multipath, MTU alebo policy attributes.

Linux inventár:

```bash
ip -4 route
ip -6 route
ip rule show
ip route show table all
```

Príklad:

```text
default via 192.0.2.1 dev eth0 metric 100
192.0.2.0/24 dev eth0 proto kernel scope link src 192.0.2.10
10.20.0.0/16 via 192.0.2.254 dev eth0 metric 50
```

Route neobsahuje stav celej end-to-end služby. Nehovorí, či gateway odpovedá na ARP/NDP, či firewall traffic povolí, či existuje return path ani či aplikácia počúva.

## 3. Routing verzus forwarding

**Routing** je výpočet alebo výber cesty. **Forwarding** je spracovanie konkrétneho packetu podľa už existujúceho routing a policy state.

Control plane môže routes vytvoriť statickou konfiguráciou, dynamickým protokolom, cloud controllerom alebo orchestration systémom. Data plane potom vykonáva lookup a packet pošle, lokálne doručí alebo zahodí.

```text
control plane: nauč sa, kadiaľ je prefix dostupný
forwarding plane: pre tento konkrétny packet použi vybranú route
```

Chybná route je control-plane problém. Drop na interface queue alebo firewall hooku je data-plane problém. Pri incidente treba tieto roviny oddeliť.

## 4. Connected route

Keď interface dostane IP adresu s prefixom, kernel typicky vytvorí connected route:

```text
interface: eth0
address:   192.0.2.10/24
route:     192.0.2.0/24 dev eth0 scope link src 192.0.2.10
```

Destination v connected prefixe sa považuje za on-link. Host sa pokúsi získať MAC adresu destination priamo cez ARP alebo NDP.

Ak je prefix omylom príliš široký, host môže vzdialenú IP považovať za lokálnu a márne ju ARPovať namiesto odoslania packetu gateway. Chybný prefix je preto zároveň routing aj neighbor-resolution problém.

## 5. Local route

Linux udržiava osobitnú `local` table pre adresy patriace hostu, broadcasty a ďalšie lokálne destinations:

```bash
ip route show table local
```

Ak destination zodpovedá lokálnej adrese, packet sa neposiela na fyzický link iba preto, že existuje interface s touto adresou. Kernel ho môže doručiť lokálnemu socketu cez local input path.

To vysvetľuje, prečo route typu `local` má iné správanie než connected unicast route. Pri policy routingu alebo virtual IP troubleshootingu treba kontrolovať aj local table, nie iba `main`.

## 6. Longest-prefix match

Ak destination zodpovedá viacerým routes, vyhrá najšpecifickejší prefix:

```text
10.0.0.0/8      via gateway A
10.10.0.0/16    via gateway B
10.10.20.0/24   via gateway C
```

Destination `10.10.20.5` použije `/24` cez gateway C.

Prefix specificity sa porovnáva pred metric. Route `/24` s vyššou metric typicky stále vyhrá nad `/16`, pretože opisuje menší a presnejší address range.

Mentálny model:

```text
najprv policy context
→ potom najdlhší zhodný prefix
→ potom preference/metric medzi rovnako špecifickými kandidátmi
→ potom multipath selection, ak zostáva viac rovnocenných ciest
```

## 7. Default route

IPv4 default:

```text
0.0.0.0/0
```

IPv6 default:

```text
::/0
```

Prefix length nula znamená, že route sa zhoduje s každou adresou. Zároveň je najmenej špecifická, preto ju prekryje každá presnejšia route.

Default gateway teda nedostáva „všetok traffic“. Lokálne destinations, connected prefixes, host routes, VPN routes a policy-selected routes môžu mať prednosť.

Konkrétne rozhodnutie:

```bash
ip route get 203.0.113.20
ip -6 route get 2001:db8::20
```

`ip route get` je praktickejší než samotný výpis table, pretože ukáže resolved route, selected source, interface a gateway pre konkrétny flow context.

## 8. Next-hop reachability

Gateway musí byť z pohľadu vybranej route linkovo dosiahnuteľná alebo musí existovať explicitný mechanizmus, ktorý umožní recursive resolution.

```text
default via 192.0.2.1 dev eth0
```

Host musí vedieť doručiť Ethernet frame k `192.0.2.1` cez `eth0`. Typicky to znamená, že next hop patrí do connected prefixu interface-u a ARP/NDP uspeje.

Existencia route nedokazuje:

- že interface má carrier,
- že host je v správnej VLAN,
- že neighbor odpovie,
- že gateway routuje ďalej,
- že firewall traffic povolí,
- že destination pozná return path.

Routing table je plán. Neighbor table a packet capture ukazujú, či sa plán vykonal na lokálnom hop-e.

## 9. Recursive next-hop resolution

Niektoré routing systémy dovolia route, ktorej next hop sa sám musí vyriešiť cez inú route.

```text
10.20.0.0/16 via 192.0.2.254
192.0.2.254 je reachable cez connected 192.0.2.0/24
```

Routing engine najprv určí next-hop IP a potom nájde spôsob, ako sa k next hopu dostať. Konkrétne pravidlá závisia od platformy a route flags.

Ak next-hop resolution zlyhá, route môže zostať nakonfigurovaná, ale nemusí byť aktívna alebo použiteľná. Pri dynamickom routingu je dôležité rozlišovať route v control-plane databáze od route nainštalovanej vo forwarding table.

## 10. Source-address selection

Host s viacerými adresami musí vybrať source IP pre outbound packet. Výber ovplyvňuje:

- route `src` alebo `prefsrc` hint,
- destination scope,
- prefix similarity,
- IPv6 source-selection pravidlá,
- policy routing,
- socket bind aplikácie,
- interface a address state.

```bash
ip route get 198.51.100.10
ip -6 route get 2001:db8::10
```

Výstup môže obsahovať:

```text
src 192.0.2.10
```

Nesprávna source address môže spôsobiť chýbajúci return path, firewall deny, odpoveď na iný interface alebo nesprávnu identitu služby. Routing sa preto nemá analyzovať iba podľa destination.

## 11. Forward path a return path

End-to-end komunikácia potrebuje route v oboch smeroch:

```text
client → server
server → client
```

Forward route môže byť správna, ale odpoveď sa nemusí vrátiť. Každá strana a každý transit segment potrebuje route k source prefixu alebo mechanizmus, ktorý ho prekladá.

Pri incidente „request odchádza, odpoveď neprichádza“ treba samostatne zrekonštruovať:

1. forward path,
2. destination processing,
3. return route,
4. stateful firewall alebo NAT state,
5. source-address selection odpovede.

Packet capture iba na source hoste často nedokáže určiť, kde sa return packet stratil.

## 12. Asymmetric routing

Asymmetric routing znamená, že forward a return traffic idú rozdielnymi paths:

```text
client → firewall A → server
server → firewall B → client
```

IP routing to môže podporovať. Problém vzniká, keď middlebox udržiava per-flow state a vidí iba jednu polovicu komunikácie.

Typické symptómy:

- SYN príde cez jednu cestu a SYN-ACK odíde cez inú,
- stateful firewall B nepozná pôvodný SYN,
- NAT mapping existuje iba na jednej appliance,
- packet capture na jednej ceste ukazuje polovicu flow-u,
- failover zmení path existujúceho spojenia.

Asymetria nie je automaticky chybná, ale musí byť kompatibilná s firewallom, NAT-om, load balancerom a observability modelom.

## 13. Reverse path filtering

Linux `rp_filter` môže kontrolovať, či source adresa inbound packetu zodpovedá očakávanej reverse route.

```bash
sysctl net.ipv4.conf.all.rp_filter
sysctl net.ipv4.conf.eth0.rp_filter
```

Strict model môže zahodiť packet, ak najlepšia reverse route k source nevedie cez ingress interface. To znižuje spoofing risk, ale môže blokovať legitímny multihomed alebo asymmetric traffic.

Loose model overuje všeobecnú routovateľnosť source adresy menej striktne. Presný režim a jeho vhodnosť závisia od topológie.

Vypnutie `rp_filter` bez dôkazu môže odstrániť symptom, ale zároveň oslabiť anti-spoofing ochranu. Najprv treba potvrdiť konkrétny asymmetric path.

## 14. Viac default routes

Host môže mať viac default routes:

```text
default via 192.0.2.1 dev eth0 metric 100
default via 198.51.100.1 dev eth1 metric 200
```

Nižšia metric je medzi rovnako špecifickými routes typicky preferovaná. To však nie je plnohodnotný service-health failover.

Interface môže zostať `UP`, gateway môže odpovedať na ARP a route môže zostať aktívna, hoci vzdialený upstream je nefunkčný. Robustný failover preto môže potrebovať:

- trackovanie vzdialenejšieho health signálu,
- odstránenie alebo zmenu route pri failure,
- dynamic routing,
- policy routing podľa source,
- koordináciu existujúceho connection state,
- DNS alebo application-level failover.

Samotná metric rieši preference, nie úplnú detekciu path health.

## 15. Metrics, preference a route origin

Pri výbere route sa často miešajú rozdielne pojmy:

- **prefix specificity** — veľkosť zhodného prefixu,
- **route preference alebo administrative distance** — dôvera k zdroju route,
- **protocol metric** — cena cesty v rámci routing protokolu,
- **kernel metric** — lokálna preference konkrétnych routes,
- **ECMP equality** — podmienka pre multipath kandidátov.

Konkrétne poradie závisí od platformy. Nie je správne používať univerzálne pravidlo „najnižšia metric vždy vyhrá“ bez určenia prefixu, table a route source.

## 16. Linux routing policy database

Linux môže použiť viac routing tables. `ip rule` určuje, v akom poradí a za akých podmienok sa tables vyhodnocujú.

```bash
ip rule show
ip route show table local
ip route show table main
ip route show table all
```

Typické tables:

- `local` — lokálne addresses a broadcast destinations,
- `main` — bežné connected, static a dynamic routes,
- `default` — fallback table podľa konfigurácie,
- custom tables — source-based alebo service-specific routing.

Bežný `ip route` zobrazuje najmä `main`. Pri policy-routing incidente preto môže vyzerať správne, aj keď packet používa inú table.

## 17. Policy routing

Klasický route lookup používa primárne destination. Policy routing môže pred výberom table zohľadniť:

- source prefix,
- ingress interface,
- firewall mark,
- TOS/DSCP,
- lokálne UID range,
- ďalšie platformové selectors.

Príklad konceptu:

```text
from 10.0.10.0/24 lookup table 100
```

Workflow:

```text
packet fields
  ↓
ip rule priority order
  ↓
vybraná routing table
  ↓
longest-prefix match v tejto table
```

Simulácia konkrétneho source:

```bash
ip route get 203.0.113.10 from 192.0.2.10
```

Pri marked trafficu môže byť potrebné zahrnúť mark a ingress context. Diagnostika bez rovnakých selectorov nemusí reprodukovať reálne rozhodnutie.

## 18. Route types

Linux podporuje viac route types než bežný unicast:

- `local` — destination patrí hostu,
- `broadcast` — lokálny broadcast,
- `unreachable` — explicitná nedostupnosť,
- `prohibit` — administratívne zakázaná cesta,
- `blackhole` — tiché zahodenie,
- `throw` — ukončenie lookupu v table a pokračovanie podľa rules.

Príklad:

```bash
ip route add blackhole 203.0.113.0/24
```

Blackhole route môže byť zámerný security alebo aggregation mechanizmus. Z pohľadu klienta však môže vyzerať ako obyčajný timeout. Preto treba rozlíšiť chýbajúcu route, explicitný reject a tiché zahodenie.

## 19. Packet forwarding na Linuxe

Host routuje transit packets iba ak sú splnené viaceré podmienky:

- packet nie je lokálne terminovaný,
- kernel forwarding je povolený,
- existuje route k destination,
- forwarding policy traffic povolí,
- next hop je reachable,
- return path existuje.

```bash
sysctl net.ipv4.ip_forward
sysctl net.ipv6.conf.all.forwarding
```

Forwarding nie je NAT. Router môže preposielať packet bez zmeny source alebo destination adresy. NAT je samostatná transformácia aplikovaná podľa policy.

Cloud alebo hypervisor môže mať ďalšiu source/destination check vrstvu, ktorá blokuje appliance forwarding aj pri správnej Linux konfigurácii.

## 20. TTL, hop limit a traceroute

IPv4 TTL a IPv6 hop limit sa na každom routeri znižujú. Pri nule router packet zahodí a typicky odošle ICMP Time Exceeded.

Traceroute posiela probes s postupne rastúcou TTL/hop-limit hodnotou a z odpovedí odhaduje jednotlivé hops.

```bash
tracepath example.com
traceroute example.com
```

Výstup nie je dokonalá mapa každej aplikačnej cesty. ECMP môže vybrať rôzne paths podľa flow hash, niektoré routery neodpovedajú na probes a return path ICMP odpovedí môže byť iná než forward path.

Opakujúce sa hops alebo vypršanie TTL môže signalizovať routing loop, ale treba ho potvrdiť v control-plane a packet evidence.

## 21. Static routing

Static route vytvára administrátor alebo automation:

```bash
ip route add 10.20.0.0/16 via 192.0.2.254
```

Výhody:

- jednoduchý mentálny model,
- predvídateľné správanie,
- žiadna routing-protocol komunikácia,
- vhodné pre malé alebo stabilné topológie.

Nevýhody:

- manuálna správa a drift,
- slabá reakcia na topology failure,
- rastúci počet konfigurácií,
- riziko nekonzistentného return pathu,
- potreba osobitného health/failover mechanizmu.

Static route má byť spravovaná ako desired state, nie ako jednorazový príkaz bez dokumentovaného ownershipu.

## 22. Dynamic routing

Dynamic routing protocol vymieňa reachability informácie a vypočítava paths. Príklady:

- OSPF alebo IS-IS v interných sieťach,
- BGP medzi autonomous systems aj v datacentroch a cloude.

Dynamic routing poskytuje konvergenciu pri topology changes, ale zvyšuje control-plane komplexitu. Chybný prefix advertisement, route leak alebo zlá policy sa môže rozšíriť rýchlejšie než manuálna chyba.

Bezpečný návrh potrebuje:

- explicitné import/export policy,
- prefix filters,
- maximum-prefix limity,
- authentication tam, kde je relevantná,
- route ownership,
- monitoring adjacencies a route changes,
- rollback plán.

Dynamické neznamená automaticky správne alebo odolné.

## 23. ECMP

Equal-Cost Multi-Path umožňuje používať viac rovnocenných next hops:

```text
10.20.0.0/16
  nexthop via 192.0.2.1
  nexthop via 192.0.2.2
```

Traffic sa zvyčajne rozdeľuje per-flow hashom, nie náhodne packet po packete. Tým sa znižuje reordering v jednom flow-e.

Trade-offs:

- veľké flows môžu vytvoriť nerovnomerné využitie,
- pri failure sa flow hash mapping zmení,
- stateful middleboxes musia byť v path-e konzistentne,
- asymetria môže byť prirodzená,
- packet captures treba robiť na viacerých paths,
- hash fields a seed ovplyvňujú rozdelenie.

ECMP poskytuje paralelné cesty, ale nie automaticky rovnomernú aplikačnú záťaž.

## 24. Route summarization

Súvislé prefixes možno publikovať ako väčší aggregate. Sumarizácia znižuje počet routes a stabilizuje control plane.

```text
10.20.0.0/24
10.20.1.0/24
10.20.2.0/24
10.20.3.0/24
→ 10.20.0.0/22
```

Aggregate môže priťahovať traffic aj pre subprefix, ktorý momentálne neexistuje. Preto sumarizujúci router často inštaluje discard route pre aggregate a presnejšie routes pre dostupné subnets.

Bez tohto mechanizmu môže fallback route vytvoriť loop. Príliš široká sumarizácia môže blackholovať traffic ďaleko od reálneho failure-u.

## 25. Cloud route tables

Cloud platformy implementujú virtual routing. Route target môže byť:

- local virtual network,
- Internet gateway,
- NAT gateway,
- virtual appliance,
- peering alebo transit gateway,
- VPN alebo direct-connect attachment,
- service endpoint.

Pri cloud troubleshootingu treba overiť:

1. ktorá route table je asociovaná so source subnetom,
2. longest-prefix match pre destination,
3. stav a ownership targetu,
4. security groups a network ACLs,
5. source/destination check pre appliance,
6. return route na druhej strane,
7. propagated routes a precedence,
8. provider-specific system routes.

Cloud route table nie je firewall. Route umožňuje alebo vyberá path; access policy je samostatná vrstva.

## 26. Kubernetes a container routing

Pod traffic môže používať direct routes, overlays, tunnels, eBPF dataplane alebo kombináciu host routing a translation rules.

```text
Pod socket
  ↓
Pod network namespace route
  ↓
veth alebo runtime dataplane
  ↓
node route / tunnel / eBPF forwarding
  ↓
remote node alebo endpoint
```

Hostový `ip route` môže byť iba jedna časť rozhodovacieho modelu. CNI môže používať policy rules, BPF maps, encapsulation alebo network namespaces.

Pri troubleshooting-u identifikuj:

- source namespace,
- Pod a node addresses,
- CNI implementation,
- service translation,
- host route,
- underlay return path,
- NetworkPolicy alebo firewall hooks.

## 27. Diagnostika route decision

Základný postup:

```bash
ip addr
ip rule show
ip route show table all
ip route get <destination>
ip neigh
```

Pre konkrétny source:

```bash
ip route get <destination> from <source>
```

Otázky:

1. Je destination lokálna, connected alebo remote?
2. Ktoré rule vybralo table?
3. Ktorý prefix vyhral longest-prefix match?
4. Aký source address bol vybraný?
5. Je next hop linkovo reachable?
6. Je route typu unicast, blackhole alebo unreachable?
7. Existuje return route?
8. Nezasahuje firewall, NAT, `rp_filter` alebo cloud policy?

## 28. Chybové signály

`Network is unreachable` typicky znamená, že lokálny routing lookup nenašiel použiteľnú route.

`Host is unreachable` môže pochádzať z lokálneho neighbor failure-u alebo ICMP odpovede z iného zariadenia.

ICMP `Destination Unreachable` je explicitný signál od hosta alebo routera. Jeho code určuje presnejšiu triedu failure-u.

Timeout znamená, že klient nedostal očakávanú odpoveď v limite. Neurčuje, či packet neodišiel, bol zahodený po ceste, destination neodpovedala alebo return packet zlyhal.

Chybová správa sa má korelovať s packet capture a route state, nie interpretovať izolovane.

## 29. Troubleshooting: destination je nedostupná

```bash
ip route get <destination>
ip neigh
ping -c 1 <next-hop>
tracepath <destination>
sudo tcpdump -ni any host <destination>
```

Rozhodovací strom:

```text
route lookup zlyhá
→ lokálna route/policy chyba

route existuje, neighbor zlyhá
→ link/VLAN/ARP/NDP/next-hop problém

packet odchádza, ICMP unreachable príde
→ explicitný downstream routing alebo policy failure

packet odchádza, nič sa nevráti
→ forward drop, destination failure, return-path alebo stateful middlebox
```

Každý výsledok vedie do inej diagnostickej vetvy.

## 30. Troubleshooting: request odchádza, odpoveď neprichádza

1. Zaznamenaj selected source a route cez `ip route get`.
2. Zachyť outbound packet na source hoste.
3. Over, či packet dorazí na ďalší router, firewall alebo destination.
4. Na destination over lokálne doručenie a odpoveď.
5. Vypočítaj return route k selected source.
6. Skontroluj NAT a conntrack state.
7. Skontroluj asymmetric path a `rp_filter`.
8. Skontroluj policy rules a marks v oboch smeroch.
9. Over, či odpoveď neodchádza s inou source adresou.

Forward a return path treba dokumentovať ako dve samostatné sekvencie. „Route tam existuje“ nestačí.

## 31. Anti-patterny

### Default gateway sa mení bez výpočtu konkrétneho flow-u

Zmena môže opraviť jeden destination a rozbiť connected, VPN alebo management traffic. Najprv treba overiť longest-prefix a policy context.

### Metric sa používa ako univerzálny failover

Metric nepozná vzdialenú service health ani existujúci connection state.

### Static route sa pridá ručne a nezapíše do desired state

Po reboote alebo reconciliation sa stratí a incident sa zopakuje.

### `rp_filter` sa vypne globálne pri prvom asymetrickom symptóme

Tým sa môže oslabiť anti-spoofing bez potvrdenia root cause.

### Traceroute sa považuje za presnú mapu aplikačného flow-u

ECMP, ICMP filtering a odlišný return path môžu zobrazovať inú cestu než konkrétne TCP spojenie.

## 32. Praktický mini-lab

Vytvor alebo analyzuj routing table:

```text
10.0.0.0/8 via 192.0.2.1 metric 100
10.10.0.0/16 via 192.0.2.2 metric 200
10.10.20.0/24 via 192.0.2.3 metric 300
default via 192.0.2.254 metric 10
```

Urči route pre:

- `10.10.20.5`,
- `10.10.30.5`,
- `10.20.1.5`,
- `203.0.113.10`.

Potom vysvetli, prečo metric 10 na default route neprebije presnejšie prefixes.

Na Linux hoste porovnaj:

```bash
ip route
ip rule
ip route show table all
ip route get <destination>
ip route get <destination> from <alternate-source>
```

Zaznamenaj, či source zmení vybranú table, gateway alebo interface.

## 33. Kontrolné otázky

1. Aký je rozdiel medzi routing a forwarding?
2. Čo presne obsahuje route?
3. Ako connected route ovplyvní ARP/NDP správanie?
4. Ako funguje longest-prefix match?
5. Prečo metric neprebije špecifickejší prefix?
6. Kedy sa použije default route?
7. Prečo next hop musí byť linkovo reachable?
8. Aký je rozdiel medzi forward a return pathom?
9. Kedy je asymmetric routing problém?
10. Ako `rp_filter` interaguje s multihomingom?
11. Ako policy rules vyberajú routing table?
12. Aký je rozdiel medzi blackhole, unreachable a chýbajúcou route?
13. Prečo viac default routes neposkytuje automaticky spoľahlivý failover?
14. Ako ECMP rozdeľuje flows a aké má riziká?
15. Prečo summary route potrebuje premyslenú discard/failure policy?
16. Prečo cloud route table nie je firewall?
17. Ako by si diagnostikoval packet, ktorý odchádza, ale odpoveď sa nevracia?

## 34. Zhrnutie

Routing je lokálne rozhodovanie o ceste packetu. Policy rules vyberú routing table, longest-prefix match vyberie route a route určí next hop, interface a source context. Úspešný lookup však nedokazuje reachability. End-to-end komunikácia potrebuje funkčný local hop, forwarding policy, destination processing a return path. Praktický troubleshooting preto vždy rekonštruuje konkrétny flow v oboch smeroch a rozlišuje control-plane state od reálneho packet movementu.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: IPv4, IPv6 a subnetting](ipv4-ipv6-subnetting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: TCP a UDP →](tcp-and-udp.md)
<!-- KNOWLEDGE-NAVIGATION:END -->