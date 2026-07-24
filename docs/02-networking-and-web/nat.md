# NAT

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [Routing a default gateway](routing-and-default-gateway.md), [Ports a sockets](ports-and-sockets.md), [TCP a UDP](tcp-and-udp.md)
- Súvisiace témy: firewalls, load balancing, conntrack, container networking, cloud gateways, IPv6

## 1. Definícia

Network Address Translation — NAT — je mechanizmus, ktorý pri prechode packetu cez translation point zmení jednu alebo viac hodnôt v network alebo transport headeri. Najčastejšie mení source alebo destination IP adresu a pri PAT aj transportný port.

NAT nie je samostatný routing protokol ani bezpečnostná politika. Aby preložený flow fungoval, musia byť súčasne splnené najmenej tieto podmienky:

- route — packet sa musí dostať na translation point a odtiaľ k výslednému cieľu,
- translation rule — packet musí zodpovedať pravidlu alebo existujúcemu state mappingu,
- firewall policy — príslušný INPUT, OUTPUT alebo FORWARD path musí traffic povoliť,
- state capacity — zariadenie musí mať miesto na conntrack/NAT state,
- return path — odpoveď sa musí vrátiť cez bod, ktorý pozná mapping,
- application semantics — preloženie nesmie rozbiť protokol, identity alebo payload assumptions.

Preto platí:

```text
route exists
≠
NAT mapping exists
≠
firewall allows flow
≠
application is healthy
```

## 2. Prečo NAT existuje

NAT sa používa najmä z prevádzkových a adresných dôvodov.

### Zdieľanie verejnej IPv4 adresy

Mnoho interných klientov môže používať jednu alebo niekoľko verejných source adries. Jednotlivé flows sa rozlíšia preloženými source portmi.

### Publikovanie internej služby

Externá adresa alebo port sa môže preložiť na interný backend. Ide o destination NAT alebo port forwarding.

### Prekrytie adresných priestorov

Pri spojení dvoch sietí s rovnakými RFC1918 prefixmi možno translation použiť ako adaptačnú vrstvu. Takéto riešenie však pridáva state, znižuje transparentnosť a komplikuje audit.

### Stabilný externý endpoint

Interná topológia alebo backend sa môže meniť, zatiaľ čo klient používa stabilnú virtuálnu adresu. Túto úlohu môže plniť NAT, load balancer alebo proxy podľa požadovanej vrstvy.

### Adresná kompatibilita

Prechodové mechanizmy ako NAT64 umožňujú komunikáciu medzi IPv6-only klientom a IPv4 serverom.

NAT nie je základná požiadavka IP routingu. Router môže forwardovať packets bez akejkoľvek zmeny source alebo destination adresy.

## 3. Tuple a translation mapping

Flow sa pri NATe neidentifikuje iba jednou adresou. Stavový translator pracuje s kombináciou protokolu, adries a portov.

Pôvodný TCP flow:

```text
protocol:    TCP
source:      10.0.1.10:45000
destination: 198.51.100.20:443
```

Po source translation:

```text
protocol:    TCP
source:      203.0.113.5:62001
destination: 198.51.100.20:443
```

Translation zariadenie si musí zapamätať obojsmerný vzťah:

```text
original tuple
10.0.1.10:45000 → 198.51.100.20:443

translated tuple
203.0.113.5:62001 → 198.51.100.20:443
```

Pri odpovedi na `203.0.113.5:62001` zariadenie vyhľadá mapping a obnoví destination `10.0.1.10:45000`.

Mapping typicky obsahuje:

- transportný protokol,
- pôvodný a preložený source endpoint,
- pôvodný a preložený destination endpoint,
- connection alebo pseudo-connection state,
- čas poslednej aktivity,
- timeout class,
- interface, zone alebo policy context,
- pomocné protokolové informácie podľa implementácie.

## 4. SNAT, DNAT, PAT a statické mapovanie

### SNAT — Source NAT

SNAT mení source adresu a prípadne source port. Používa sa typicky pre outbound flow z privátnej siete.

```text
pred prekladom:
10.0.1.10:45000 → 198.51.100.20:443

po preklade:
203.0.113.5:62001 → 198.51.100.20:443
```

Remote server vidí source `203.0.113.5:62001`, nie interný endpoint.

### DNAT — Destination NAT

DNAT mení destination adresu alebo port. Používa sa pri publikovaní internej služby.

```text
pred prekladom:
client → 203.0.113.5:443

po preklade:
client → 10.0.1.20:8443
```

Backend môže stále vidieť pôvodnú source adresu klienta, ak sa zároveň neaplikuje SNAT.

### PAT — Port Address Translation

PAT umožňuje viacerým interným flows zdieľať rovnakú externú IP. Rozlíšenie zabezpečí kombinácia preloženého source portu a ostatných tuple fields.

```text
10.0.1.10:50000 → 203.0.113.5:61001
10.0.1.11:50000 → 203.0.113.5:61002
```

Termíny PAT, NAT overload alebo NAPT sa v praxi často používajú pre tento model.

### Statický one-to-one NAT

Jedna adresa sa stabilne mapuje na inú adresu. Aj pri statickom mapovaní môže zariadenie stále používať conntrack pre firewall state alebo protokolový lifecycle.

## 5. Prvý packet a ďalšie packets

Pri stateful NAT je prvý packet flowu odlišný od nasledujúcich packetov.

### Prvý packet

1. Packet vstúpi do príslušného network namespace a netfilter hooku.
2. Conntrack sa pokúsi flow klasifikovať alebo vytvoriť nový entry.
3. Routing a NAT pravidlá určia preklad.
4. Zvolí sa preložená adresa a prípadne port.
5. Vytvorí sa obojsmerný mapping.
6. Packet pokračuje cez firewall a forwarding path.

### Ďalšie packets

1. Conntrack ich priradí k existujúcemu flowu.
2. Translation sa aplikuje podľa uloženého mappingu.
3. Pravidlo NAT table sa nemusí znovu vyhodnocovať rovnakým spôsobom ako pri prvom packete.
4. Stav a timeout sa aktualizujú podľa protokolu a aktivity.

Dôsledok: po zmene NAT pravidla môžu existujúce connections pokračovať podľa starého state mappingu, kým state nezanikne alebo sa explicitne neodstráni.

## 6. Outbound SNAT lifecycle

Príklad klienta v privátnej sieti:

```text
client 10.0.1.10:45000
    ↓ route na default gateway
NAT gateway
    ↓ conntrack new flow
    ↓ SNAT/PAT
203.0.113.5:62001
    ↓ internet routing
server 198.51.100.20:443
```

Return packet:

```text
server 198.51.100.20:443
    ↓ destination 203.0.113.5:62001
NAT gateway
    ↓ conntrack lookup
    ↓ reverse translation
client 10.0.1.10:45000
```

Outbound NAT vyžaduje:

- route klienta na gateway,
- IP forwarding na gateway,
- SNAT alebo masquerade policy,
- povolený forward traffic,
- route gateway k internetu,
- route remote strany späť k verejnej NAT adrese,
- dostatočný source-port a conntrack priestor.

Ak packet odíde bez preloženej source adresy, remote strana typicky nevie routovať odpoveď na privátnu adresu.

## 7. Inbound DNAT lifecycle

Publikovaná služba:

```text
client
    ↓ 203.0.113.5:443
translation point
    ↓ DNAT
10.0.1.20:8443
    ↓
backend listener
```

DNAT mení destination pred finálnym forwarding rozhodnutím, aby kernel route vybral podľa interného targetu.

Backend response musí prejsť späť cez translation point:

```text
backend 10.0.1.20:8443
    ↓ reply to client
translation point
    ↓ reverse DNAT
source becomes 203.0.113.5:443
    ↓
client
```

Ak backend odpovie mimo translation pointu, klient môže dostať packet z neočakávanej internej adresy alebo sa odpoveď vôbec nedoručí. Preto sa pri DNAT scenári kontroluje:

- backend default route,
- policy routing,
- asymmetric paths,
- stateful firewall symmetry,
- prípadný dodatočný SNAT.

## 8. NAT hook ordering v Linuxe

Zjednodušený netfilter path pre forwardovaný packet:

```text
ingress interface
    ↓
PREROUTING
    ├── conntrack classification
    └── typický DNAT
    ↓
routing decision
    ↓
FORWARD
    ↓
POSTROUTING
    └── typický SNAT/MASQUERADE
    ↓
egress interface
```

Lokálne generovaný packet používa aj `OUTPUT` hook:

```text
local process
    ↓
OUTPUT
    ↓
routing / policy
    ↓
POSTROUTING
```

Lokálne doručovaný packet smeruje po routing decision do `INPUT`.

Presné priority chains a poradie pravidiel závisia od nftables rulesetu a implementácie. Pri diagnostike je dôležité vedieť:

- v ktorom hooku sa preklad aplikuje,
- či ide o local alebo forwarded traffic,
- či packet mení route po DNAT,
- či firewall matchuje original alebo translated fields v danom bode,
- či ďalší namespace alebo virtual dataplane vykonáva ďalšiu translation.

## 9. Conntrack a NAT state

Linux netfilter používa conntrack na evidenciu flows. Conntrack state nie je totožný s aplikačným stavom ani presnou TCP state machine, ale poskytuje kernelu dostatok informácií na stateful filtering a reverse translation.

Pozorovanie:

```bash
sudo conntrack -L
sudo conntrack -S
sysctl net.netfilter.nf_conntrack_count
sysctl net.netfilter.nf_conntrack_max
```

Typické conntrack klasifikácie:

- `NEW` — flow ešte nemá potvrdenú obojsmernú komunikáciu alebo začína,
- `ESTABLISHED` — packet patrí k rozpoznanému obojsmernému flowu,
- `RELATED` — nový flow súvisí s existujúcim flowom podľa helpera alebo protokolu,
- `INVALID` — packet nemožno korektne priradiť k state modelu.

Pri vyčerpaní conntrack table môžu nové flows zlyhávať, hoci:

- listener beží,
- route existuje,
- CPU nie je vyťažené,
- aplikácia nemá vysokú latency,
- existujúce connections pokračujú.

Kernel log môže obsahovať informáciu o plnej table alebo droppoch.

## 10. TCP state a timeouty

TCP poskytuje handshake, sequence state a explicitné FIN/RST udalosti. Conntrack preto môže rozlišovať viac lifecycle fáz a používať odlišné timeouty.

Mapping musí prežiť dostatočne dlho na legitímnu komunikáciu, ale nie nekonečne. Príliš krátky timeout môže rozbiť idle alebo long-lived connections. Príliš dlhý timeout zadržiava state a porty po zaniknutých flowoch.

Dôležité rozlíšenie:

```text
TCP socket state v endpointe
≠
conntrack state v middleboxe
```

Endpoint môže považovať connection za otvorenú, zatiaľ čo NAT mapping po nečinnosti už expiroval. Ďalší packet potom nemusí dostať očakávanú odpoveď.

## 11. UDP state a timeouty

UDP nemá handshake ani FIN. NAT zariadenie preto vytvorí pseudo-state z pozorovaných datagramov a zruší ho po inactivity timeoute.

```text
client UDP datagram
    ↓ vytvorí mapping
server response
    ↓ mapping umožní reverse translation
idle interval
    ↓ mapping expiruje
late response
    ↓ môže byť zahodená
```

UDP aplikácie musia počítať s tým, že:

- mapping môže zaniknúť bez upozornenia,
- keepalive traffic udržiava middlebox state, nie nutne application health,
- timeouty sa líšia medzi zariadeniami,
- rovnaký interný endpoint môže dostať iný externý port po obnovení mappingu,
- inbound reachability závisí od konkrétneho NAT behavioru.

## 12. MASQUERADE verzus explicitný SNAT

### MASQUERADE

Masquerade použije aktuálnu adresu egress interface. Je vhodný, keď sa verejná adresa mení, napríklad pri dynamickom pripojení.

```nft
chain postrouting {
    type nat hook postrouting priority srcnat;
    oifname "wan0" ip saddr 10.0.0.0/8 masquerade
}
```

### Explicitný SNAT

Explicitný SNAT určí stabilnú source adresu alebo pool adries.

```nft
chain postrouting {
    type nat hook postrouting priority srcnat;
    oifname "wan0" ip saddr 10.0.0.0/8 snat to 203.0.113.5
}
```

Pri stabilnej infraštruktúre je explicitný SNAT predvídateľnejší. Masquerade je praktický pri dynamickej adrese, ale môže mať odlišný lifecycle pri zmene alebo strate interface adresy.

## 13. Port allocation a NAT exhaustion

PAT potrebuje pre každý súbežný mapping unikátnu externú kombináciu endpoint fields. Jedna verejná source IP preto neposkytuje nekonečnú kapacitu.

Dostupnosť portov ovplyvňuje:

- transportný protokol,
- rezervované a používané porty,
- mapping behavior zariadenia,
- destination endpoint,
- timeouty,
- počet public IP adries,
- per-client alebo per-destination limity.

Typický incident:

```text
existujúce connections fungujú
nové outbound connections timeoutujú
problém rastie s concurrency
po znížení loadu sa dočasne stratí
```

Možné príčiny:

- chýbajúci connection pooling,
- extrémne krátke application connections,
- retry storm,
- veľa long-lived idle flows,
- UDP mappings s dlhým timeoutom,
- malý pool public adries,
- conntrack table exhaustion,
- platformový per-destination limit.

Náprava má vychádzať z merania. Zväčšenie timeoutu môže zhoršiť state pressure; jeho skrátenie môže rozbiť legitímne idle flows.

## 14. Hairpin NAT

Hairpin NAT nastane, keď interný klient používa externú adresu služby, ktorá sa prekladá späť do rovnakej internej siete.

```text
client 10.0.1.30
    ↓ destination 203.0.113.5:443
NAT gateway
    ↓ DNAT
backend 10.0.1.20:8443
```

Ak backend vidí source `10.0.1.30`, môže odpovedať klientovi priamo, mimo gateway. Klient však otvoril connection na `203.0.113.5`, takže takáto odpoveď môže porušiť očakávaný tuple.

Hairpin implementácia preto často aplikuje aj SNAT:

```text
client source 10.0.1.30
    ↓ SNAT na gateway address
backend odpovie gateway
    ↓ reverse translation
client dostane odpoveď z očakávanej public identity
```

Alternatívou je split-horizon DNS, kde interný resolver vráti internú adresu. To odstraňuje hairpin path, ale vytvára dve DNS views, ktoré treba prevádzkovať konzistentne.

## 15. Port forwarding

Konceptuálny nftables DNAT:

```nft
chain prerouting {
    type nat hook prerouting priority dstnat;
    iifname "wan0" tcp dport 443 dnat to 10.0.1.20:8443
}
```

Samotný DNAT nezaručuje dostupnosť. Potrebné sú aj:

- IP forwarding,
- FORWARD allow policy,
- listener na `10.0.1.20:8443`,
- funkčný backend route,
- reverse translation path,
- správne MTU a transport state,
- logovanie a monitoring,
- obmedzenie source rozsahu podľa security policy.

Pri publikovaní služby sa musí určiť, či backend potrebuje pôvodnú client IP. Ak sa source preloží, aplikácia ju môže dostať iba cez dôveryhodný proxy protokol alebo aplikačný header — ak je na ceste príslušný proxy, nie obyčajný L3/L4 NAT.

## 16. NAT a firewall

NAT a firewall sú odlišné funkcie:

```text
NAT
= prepíš adresu alebo port

Firewall
= povoľ alebo zamietni traffic
```

DNAT rule môže vytvoriť route k backendu, ale forward firewall môže packet zahodiť. Naopak firewall môže traffic povoliť bez akejkoľvek translation.

Stateful firewall a NAT často používajú rovnaký conntrack state, preto sa ich diagnostika prelína. Koncepčne ich však treba oddeliť:

- translation vysvetľuje, aké endpoint fields packet má,
- filter vysvetľuje, či packet smie pokračovať,
- routing vysvetľuje, kam packet smeruje,
- application vysvetľuje, čo sa po doručení stane.

NAT nie je bezpečnostná hranica sám osebe. Neúmyselne môže obmedziť unsolicited inbound flows, ale explicitná access policy musí byť definovaná firewallom alebo vyššou vrstvou.

## 17. Asymetria a return path

Stateful translation vyžaduje, aby oba smery flowu prešli zariadením, ktoré pozná mapping.

```text
forward path:
client → NAT A → server

return path:
server → router B → client
```

Ak odpoveď obíde NAT A:

- reverse translation sa nevykoná,
- source alebo destination tuple nebude sedieť,
- stateful firewall môže packet zahodiť,
- capture na NAT A ukáže iba outbound polovicu flowu.

Asymetriu môžu spôsobiť:

- multiple default routes,
- ECMP,
- policy routing,
- nesprávna backend gateway,
- cloud route tables,
- HA failover bez state synchronization,
- anycast alebo multi-region routing,
- container overlay a host routing kombinácia.

## 18. HA a state synchronization

Ak je NAT gateway redundantná, nestačí iba presunúť virtuálnu IP. Aktívne mappings sú lokálny stav.

Pri failover-e bez synchronizácie:

- existujúce TCP connections môžu byť resetnuté alebo timeoutovať,
- UDP mappings sa stratia,
- nový node nevie vykonať reverse translation,
- aplikačné retries môžu vytvoriť burst.

Možné modely:

- active/passive so state replication,
- active/active s deterministickým flow hashingom,
- stateless alebo algorithmic translation pre vhodný use case,
- akceptovanie connection lossu a retry na vyššej vrstve.

HA návrh musí explicitne určiť, či chráni iba novú konektivitu alebo aj existujúce flows.

## 19. NAT traversal

Klient za stateful NAT typicky nemá stabilný inbound mapping, kým ho nevytvorí outbound traffic alebo explicitné pravidlo.

Používané mechanizmy:

- static port forwarding — administrátor vytvorí stabilný inbound mapping,
- UPnP, NAT-PMP alebo PCP — klient žiada gateway o mapping,
- STUN — klient zistí, aký externý endpoint mu NAT pridelil,
- TURN — traffic sa reléuje cez verejne dostupný server,
- ICE — kombinuje host, server-reflexive a relay candidates a testuje reachability.

Používa sa pri WebRTC, VoIP, P2P a hrách. Úspech závisí od NAT mapping a filtering behavioru, firewallu, timeoutov a dostupnosti relay infraštruktúry.

## 20. NAT a aplikačné protokoly

Protokol, ktorý v payloade prenáša vlastné IP adresy alebo porty, môže po NATe zlyhať. Translation zariadenie mení headers, nie automaticky aplikačné dáta.

Historicky sa používali protocol helpers alebo application-level gateways. Tie však:

- zvyšujú parser attack surface,
- musia rozumieť protokolu,
- zlyhávajú pri šifrovanom payloade,
- komplikujú state a troubleshooting.

Moderný návrh preferuje protokoly, ktoré sú NAT-aware na aplikačnej vrstve, používajú explicitné relays alebo neprenášajú routovacie endpointy v neautentizovaných payloads.

## 21. NAT v kontajneroch a Kubernetes

Pri publikovaní container portu môže dataplane vykonať DNAT, SNAT, proxying alebo eBPF service translation.

```text
client
    ↓ host/node IP:8080
service or host translation
    ↓ container/Pod IP:80
application socket
```

Treba oddeliť:

- application listener,
- Pod alebo container network namespace,
- Pod IP,
- container port metadata,
- node port alebo published host port,
- Service virtual IP,
- external load balancer,
- ingress alebo reverse proxy.

Source IP sa môže zachovať alebo stratiť podľa dataplane a traffic policy. To ovplyvňuje:

- audit logy,
- rate limiting,
- network policy,
- geolocation,
- client identity,
- session affinity.

Hostový nftables ruleset nemusí byť jediným zdrojom pravdy, ak platforma používa IPVS, eBPF alebo managed virtual networking.

## 22. Cloud NAT

Managed cloud NAT typicky poskytuje outbound connectivity privátnym subnetom bez inbound publikovania workloadov.

Prevádzkové limity môžu zahŕňať:

- source-port kapacitu na public IP,
- per-destination mapping limit,
- počet súbežných flows,
- idle timeouty,
- throughput a packets per second,
- zonálny failure domain,
- počet priradených public IP adries,
- cenu za spracované dáta.

Cloud NAT nie je automaticky firewall ani load balancer. Route table musí smerovať outbound traffic na NAT target a security controls musia traffic samostatne povoliť.

Pri zonálnom dizajne treba zvážiť, či cross-zone routing zvyšuje náklady, latency alebo failure coupling.

## 23. NAT64 a DNS64

NAT64 umožňuje IPv6-only klientovi komunikovať s IPv4 serverom.

Zjednodušený tok:

```text
IPv6-only client
    ↓ query A/AAAA
DNS64
    ↓ syntetizuje AAAA z IPv4 A recordu
client sends IPv6 packet to NAT64 prefix
    ↓
NAT64 translates IPv6 ↔ IPv4
    ↓
IPv4 server
```

DNS64 syntetizácia nie je vždy možná alebo vhodná, napríklad pri aplikácii používajúcej literal IPv4 adresu, vlastné DNSSEC validation assumptions alebo protokol prenášajúci adresy v payloade.

NAT66 existuje v niektorých prostrediach, ale IPv6 security nemá byť založená na preklade. Segmentáciu a inbound policy rieši firewall, nie absencia globálnej adresy.

## 24. Checksums a offload

Zmena IP adresy alebo portu mení hodnoty zahrnuté v IP alebo transportnom checksume. NAT implementácia musí checksum korektne upraviť.

Pri packet capture na hoste môže checksum vyzerať neplatne, pretože:

- kernel ešte neodovzdal finálny výpočet NIC offloadu,
- capture prebehla pred alebo po inom dataplane kroku,
- packet je logical large segment pred segmentation offloadom.

Preto chybný checksum v host capture nie je automaticky dôkaz poškodeného packetu na wire. Porovnaj capture na vhodnom observation pointe alebo dočasne zohľadni offload stav.

## 25. Observability

Pri NAT incidente treba pozorovať najmenej štyri pohľady:

### Original flow

Aké source/destination fields vytvoril klient?

### Translated flow

S akými fields packet odchádza z translation pointu?

### Conntrack mapping

Existuje state a aký má lifecycle?

### Return flow

Prichádza odpoveď na preložený endpoint a vykoná sa reverse translation?

Nástroje:

```bash
sudo nft list ruleset
sudo conntrack -L
sudo conntrack -S
ss -tan
ip route get <destination>
sudo tcpdump -ni <inside-iface> host <client-or-backend>
sudo tcpdump -ni <outside-iface> host <remote-endpoint>
journalctl -k -b
```

Pri nftables je užitočné používať counters a kontrolované tracing mechanizmy. Pri vysokej prevádzke môže kompletný conntrack dump alebo široký packet capture vytvoriť veľký overhead a citlivé dáta.

## 26. Diagnostický postup: outbound flow

Klient z privátnej siete sa nevie pripojiť na externý endpoint.

1. Over klientský destination a source selection:

```bash
ip route get <destination>
```

2. Zachyť original packet na inside interface translation pointu.
3. Over IP forwarding a FORWARD policy.
4. Over, že packet zodpovedá NAT pravidlu.
5. Zachyť egress packet a skontroluj preloženú source adresu a port.
6. Over conntrack entry a timeout/state.
7. Over, či odpoveď prichádza na public endpoint.
8. Skontroluj reverse translation a doručenie klientovi.
9. Pri vysokom load-e skontroluj conntrack a source-port capacity.
10. Po obnovení transportu over aplikačný výsledok, nie iba SYN handshake.

Klasifikácia dôkazov:

```text
packet nepríde na NAT
→ klientská route, L2 alebo upstream firewall

packet príde, ale neodíde
→ forwarding, filter, NAT match alebo route

packet odíde nepreložený
→ NAT rule/hook mismatch

packet odíde preložený, reply nepríde
→ remote path, remote policy alebo return routing

reply príde, ale klient ho nedostane
→ conntrack/reverse translation/filter/inside route
```

## 27. Diagnostický postup: publikovaná služba

Externý klient sa nevie pripojiť na DNAT endpoint.

1. Over, že packet prichádza na external address a správny interface.
2. Over DNAT counter a translated destination.
3. Skontroluj routing decision k backendu.
4. Over FORWARD policy a backend listener.
5. Zachyť packet pri backende.
6. Over backend source-address view.
7. Skontroluj backend return route.
8. Zachyť response na backend aj external strane translation pointu.
9. Over reverse DNAT a source identity odpovede.
10. Skontroluj hairpin path osobitne, ak interní klienti používajú public endpoint.

`Connection refused` môže znamenať RST od externého translation pointu, backendu alebo firewall reject. Timeout typicky znamená drop alebo chýbajúcu odpoveď, ale observation point musí určiť, kde sa flow zastavil.

## 28. Bezpečnostné trade-offy

NAT môže znížiť priame vystavenie interných adries, ale neposkytuje úplnú bezpečnostnú politiku.

Riziká:

- široké DNAT pravidlo publikuje nechcenú službu,
- source translation skrýva pôvod klienta pred backendom,
- chýbajúce mapping logy znemožnia atribúciu,
- state exhaustion vytvorí denial of service,
- hairpin path obíde očakávanú segmentáciu,
- helper spracúva nedôveryhodný aplikačný payload,
- overlapping translation komplikuje identity a audit,
- automatické port mapping protokoly zväčšia attack surface.

Least-privilege návrh má obmedziť source, destination, protocol, port, direction a životnosť pravidla. Translation policy má byť versionovaná, testovaná a pozorovateľná rovnako ako firewall policy.

## 29. Časté omyly

### „NAT a firewall sú to isté“

Nie. NAT mení endpoint fields; firewall rozhoduje, či packet môže pokračovať.

### „DNAT automaticky sprístupní službu“

Nie. Potrebuje forwarding, firewall allow, backend listener a funkčný return path.

### „Existujúca route znamená, že NAT funguje“

Nie. Route neurčuje translation match, state capacity ani reverse mapping.

### „NAT vždy skryje internú topológiu“

Nie. DNS, aplikačné payloady, headers, timing a ďalšie metadata ju môžu odhaliť.

### „Privátna IP je automaticky bezpečná“

Nie. Môže byť dostupná cez VPN, peering, compromised host, proxy alebo nesprávne forwarding pravidlo.

### „Veľká conntrack table vyrieši NAT exhaustion“

Nie vždy. Bottleneck môže byť source-port priestor, per-destination limit, retry storm alebo platformová quota.

### „IPv6 potrebuje NAT kvôli bezpečnosti“

Nie. Security policy poskytuje firewall a access-control vrstva.

## 30. Kontrolné otázky

1. Aký je rozdiel medzi routingom, NATom a firewallom?
2. Čo obsahuje stateful NAT mapping?
3. Prečo sa NAT pravidlo typicky rozhoduje pri prvom packete flowu?
4. Ako funguje reverse translation pri SNAT a DNAT?
5. Prečo asymmetric return path rozbije stateful NAT?
6. Aký je rozdiel medzi MASQUERADE a explicitným SNAT?
7. Ako vzniká source-port alebo conntrack exhaustion?
8. Prečo UDP mapping potrebuje inactivity timeout?
9. Čo je hairpin NAT a prečo môže vyžadovať SNAT?
10. Prečo DNAT pravidlo samo nestačí na publikovanie služby?
11. Ako sa líši endpoint socket state od conntrack state?
12. Čo musí HA NAT riešiť pri failover-e existujúcich connections?
13. Aký problém riešia STUN, TURN a ICE?
14. Ako NAT64 a DNS64 umožnia IPv6-only klientovi dosiahnuť IPv4 server?
15. Ktoré observation points potrebuješ pri diagnostike translation flowu?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: DHCP](dhcp.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Firewally →](firewalls.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
