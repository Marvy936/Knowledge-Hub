# IPv4, IPv6 a subnetting

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [OSI a TCP/IP model](osi-and-tcp-ip-model.md), [Ethernet, MAC a ARP](ethernet-mac-arp.md)
- Súvisiace témy: routing, NAT, DNS, NDP, SLAAC, DHCPv6, cloud networking

## 1. Definícia

IP poskytuje logické adresovanie a doručenie packetov medzi sieťami. IP adresa neidentifikuje fyzické zariadenie navždy; je súčasťou routovacieho kontextu a môže patriť interface-u, virtuálnemu endpointu, load balanceru alebo loopbacku.

**Prefix** určuje, ktoré úvodné bity adresy reprezentujú spoločný network priestor. **Subnetting** rozdeľuje väčší prefix na menšie prefixes podľa topológie, failure domainov, routingu, kapacity a bezpečnostnej politiky.

Dobrý address plan nie je iba matematicky platný. Musí zostať routovateľný, sumarizovateľný, neprekrývajúci sa, dostatočne veľký pre rast a zrozumiteľný pre prevádzku.

## 2. Adresa, prefix a route

Zápis:

```text
192.0.2.10/24
```

obsahuje dve odlišné informácie:

- `192.0.2.10` — konkrétnu IPv4 adresu,
- `/24` — počet úvodných bitov tvoriacich prefix.

Prefix neurčuje iba rozsah „susedov“. Kernel z neho typicky vytvorí connected route a podľa nej rozhoduje, ktoré destinations považuje za on-link.

```text
adresa + prefix
  ↓
connected network
  ↓
rozhodnutie: destination je lokálna alebo potrebuje gateway?
```

Chybný prefix preto nespôsobí iba nesprávny výpočet subnetu. Môže zmeniť ARP/NDP správanie, selected route a return path.

## 3. IPv4 binárny model

IPv4 má 32 bitov rozdelených do štyroch oktetov:

```text
192.0.2.10
```

Binárne:

```text
11000000.00000000.00000010.00001010
```

Pri `/24` je prvých 24 bitov prefix a posledných 8 bitov host časť:

```text
11000000.00000000.00000010 | 00001010
network bits                 | host bits
```

Network address vznikne vynulovaním host bitov. Posledná adresa klasického broadcast subnetu vznikne nastavením host bitov na `1`.

## 4. Maska a CIDR

Prefix `/24` zodpovedá maske:

```text
255.255.255.0
```

Binárna maska musí mať súvislú sekvenciu jednotiek a potom núl:

```text
11111111.11111111.11111111.00000000
```

CIDR zápis je všeobecnejší než historické classful siete. Adresa začínajúca `10.` nemusí mať automaticky `/8`; konkrétny interface alebo route môže používať ľubovoľný platný prefix.

Pri diagnostike je preto nesprávne odvodiť subnet iba z prvého oktetu. Autoritatívny je nakonfigurovaný prefix a routing table.

## 5. Network, broadcast a použiteľné adresy

Pre klasický IPv4 subnet:

```text
192.0.2.0/24
```

platí:

```text
network:   192.0.2.0
hosts:     192.0.2.1 – 192.0.2.254
broadcast: 192.0.2.255
```

Počet adries je:

```text
2^(32 - prefix length)
```

Klasický počet použiteľných host adries je:

```text
2^(32 - prefix length) - 2
```

Odčítanie dvoch reprezentuje network a broadcast address. Tento vzorec však nie je univerzálny pre každý scenár.

## 6. Výnimky `/31` a `/32`

`/31` obsahuje dve adresy. Na point-to-point linku sa môžu obe použiť ako endpointy, pretože link nepotrebuje klasický broadcast model.

```text
192.0.2.10/31
192.0.2.11/31
```

`/32` reprezentuje jednu adresu. Používa sa napríklad ako host route, loopback identity, virtual IP alebo route announcement.

Cloud platformy môžu rezervovať ďalšie adresy na začiatku alebo konci subnetu. Preto tabuľka „počet adries mínus dva“ nemusí zodpovedať reálne dostupnej kapacite providera.

## 7. Block size a výpočet subnetu

Pri `/26` zostáva 6 host bitov:

```text
32 - 26 = 6
2^6 = 64 adries
```

V jednom `/24` vzniknú štyri `/26` subnety:

```text
192.0.2.0/26
192.0.2.64/26
192.0.2.128/26
192.0.2.192/26
```

Block size v poslednom relevantnom oktete je 64. Adresa `192.0.2.77/26` patrí do intervalu `64–127`:

```text
network:   192.0.2.64
broadcast: 192.0.2.127
hosts:     192.0.2.65–126
```

Rýchly postup:

1. urči počet host bitov,
2. vypočítaj počet adries v bloku,
3. nájdi násobok block size, ktorý je menší alebo rovný adrese,
4. tento násobok je začiatok subnetu,
5. koniec bloku je začiatok ďalšieho subnetu mínus jedna.

## 8. Bežné IPv4 prefixes

| Prefix | Celkový počet adries | Klasicky použiteľných hostov |
|---:|---:|---:|
| `/24` | 256 | 254 |
| `/25` | 128 | 126 |
| `/26` | 64 | 62 |
| `/27` | 32 | 30 |
| `/28` | 16 | 14 |
| `/29` | 8 | 6 |
| `/30` | 4 | 2 |
| `/31` | 2 | point-to-point model |
| `/32` | 1 | jedna adresa/route |

Tabuľka je pomôcka, nie náhrada za pochopenie bitov. Pri prefixoch mimo hranice oktetu je potrebné vedieť určiť network bits a block size, nie iba memorovať najčastejšie hodnoty.

## 9. Network membership a asymetria

Dva hosty nemusia súhlasiť, či sú navzájom on-link, ak majú rozdielne prefixy.

Príklad:

```text
Host A: 192.0.2.10/24
Host B: 192.0.2.200/25
```

Host A považuje celý `192.0.2.0/24` za lokálny. Host B považuje za lokálny iba `192.0.2.128/25`. Výsledkom môže byť asymetrický neighbor a gateway behavior.

Pri probléme „hosty v rovnakej sieti sa nevidia“ nestačí porovnať prvé tri oktety. Treba vypočítať network membership z pohľadu oboch endpointov.

## 10. Overlapping prefixes

Prefixes sa prekrývajú, keď aspoň časť address space patrí do oboch:

```text
10.0.0.0/16
10.0.10.0/24
```

V jednej routing table je vnorenie normálne. Longest-prefix match zabezpečí, že `/24` je špecifickejší než `/16`.

Problém vzniká, keď organizačne oddelené siete používajú rovnaký alebo prekrývajúci sa private space a neskôr sa majú prepojiť cez VPN, peering alebo merger.

Dôsledky:

- destination môže byť lokálna aj vzdialená podľa rozdielneho kontextu,
- priame routing rozhodnutie je nejednoznačné,
- NAT musí prekladať aj interné identity,
- DNS mená nemusia zodpovedať rovnakej IP z oboch strán,
- security logy a allowlists sú ťažšie interpretovateľné.

Address planning preto musí zohľadniť budúce prepojenia, nie iba dnešnú lokálnu potrebu.

## 11. Private a špeciálne IPv4 ranges

RFC1918 private ranges:

```text
10.0.0.0/8
172.16.0.0/12
192.168.0.0/16
```

Nie sú určené na globálne routovanie vo verejnom Internet address plane. To však neznamená, že sú bezpečné. Private adresa môže byť dostupná cez VPN, peering, compromised host alebo chybný routing.

Ďalšie dôležité ranges:

- `127.0.0.0/8` — loopback,
- `169.254.0.0/16` — IPv4 link-local,
- `224.0.0.0/4` — multicast,
- `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` — dokumentačné rozsahy,
- `255.255.255.255` — limited broadcast.

Pri návrhu a dokumentácii je vhodné používať dokumentačné ranges namiesto skutočných produkčných adries.

## 12. IPv4 header a forwarding

Kľúčové IPv4 header fields:

- version a header length,
- total length,
- identification a fragmentation flags/offset,
- TTL,
- protocol,
- header checksum,
- source a destination address.

Router vykoná route lookup podľa destination IP, zníži TTL a prepočíta IPv4 header checksum. Keď TTL dosiahne nulu, packet zahodí a typicky odošle ICMP Time Exceeded.

TTL zabraňuje nekonečnému cirkulovaniu packetov pri routing loop-e. `traceroute` a podobné nástroje využívajú kontrolované TTL/hop-limit hodnoty na odhalenie jednotlivých hopov.

## 13. IPv4 fragmentácia a Path MTU Discovery

Ak je IPv4 packet väčší než egress MTU, router ho môže fragmentovať, ak nie je nastavený `Don't Fragment` flag. Fragmenty sa skladajú až na destination endpoint-e.

Fragmentácia zvyšuje overhead a failure risk. Strata jedného fragmentu môže znehodnotiť celý pôvodný packet. Preto sa moderné stacks snažia používať Path MTU Discovery a posielať packets vhodnej veľkosti.

Typický PMTU black hole:

```text
packet je väčší než ďalší link MTU
DF je nastavené
router packet zahodí
ICMP Fragmentation Needed je blokované
source sa nedozvie menšiu MTU
→ väčšie prenosy timeoutujú
```

Malé requests môžu fungovať, zatiaľ čo TLS handshake s väčšími records alebo prenos dát zlyhá. ICMP preto nemožno bezhlavo blokovať.

## 14. IPv6 adresný model

IPv6 má 128 bitov a zapisuje sa v ôsmich hexadecimal skupinách:

```text
2001:0db8:1234:5678:abcd:ef01:2345:6789
```

Leading zeros v skupine možno vynechať:

```text
2001:db8:1234:5678:abcd:ef01:2345:6789
```

Jednu súvislú sekvenciu nulových skupín možno skrátiť ako `::`:

```text
2001:db8:0:0:0:0:0:1
→ 2001:db8::1
```

`::` možno použiť iba raz, aby bolo možné jednoznačne dopočítať chýbajúce skupiny.

## 15. IPv6 prefixy a `/64`

Bežný IPv6 LAN subnet používa `/64`:

```text
2001:db8:1234:5678::/64
```

Prvých 64 bitov tvorí subnet prefix a zvyšných 64 bitov interface identifier pri bežnom modelovaní endpoint subnetu.

IPv6 subnetting sa nemá dimenzovať iba podľa počtu hostov. Hlavným cieľom je hierarchická alokácia, jednoduchá sumarizácia a stabilný návrh.

Príklad organizácie s `/48`:

```text
organization prefix: 2001:db8:1234::/48
subnet identifier:   16 bitov
endpoint subnet:     /64
```

To poskytuje 65 536 možných `/64` subnetov. Veľkosť `/64` nie je plytvanie v rovnakom zmysle ako pri IPv4; je súčasťou štandardného IPv6 addressing modelu a podporuje SLAAC a ďalšie mechanizmy.

## 16. Typy a scopes IPv6 adries

### Global unicast

Globálne routovateľné IPv6 adresy sú typicky z priestoru `2000::/3`. Ich reálna reachability stále závisí od routing a firewall policy.

### Link-local

```text
fe80::/10
```

Link-local adresa existuje v scope jedného linku. Používa sa pre NDP, Router Advertisements a lokálnu komunikáciu. Rovnaká link-local adresa môže existovať na viacerých interfaces, preto je často potrebný zone identifier:

```bash
ping -6 fe80::1%eth0
```

### Unique local

```text
fc00::/7
```

Prakticky sa bežne generujú locally assigned prefixes z `fd00::/8`. ULA nie je presný ekvivalent RFC1918 z pohľadu návrhu ani automatická bezpečnostná hranica.

### Multicast

```text
ff00::/8
```

IPv6 nemá broadcast. Viaceré lokálne funkcie používajú scoped multicast.

### Loopback a unspecified

```text
::1/128
::/128
```

Unspecified address sa používa ako „žiadna konkrétna adresa“ v určitých lifecycle fázach, nie ako routovateľný endpoint.

## 17. IPv6 header a extension headers

IPv6 base header má fixnú veľkosť a obsahuje:

- version,
- traffic class,
- flow label,
- payload length,
- next header,
- hop limit,
- source a destination address.

Voliteľné informácie sú v extension headers. Ich spracovanie môže ovplyvniť firewally, middleboxes a packet capture interpretáciu.

IPv6 routery bežne nefragmentujú transit packets. Ak je packet príliš veľký, router odošle ICMPv6 Packet Too Big a source upraví veľkosť. Fragmentáciu môže vykonať source endpoint pomocou Fragment extension header.

Preto je ICMPv6 nevyhnutný pre funkčný Path MTU Discovery.

## 18. NDP namiesto ARP

IPv6 používa Neighbor Discovery Protocol nad ICMPv6. NDP pokrýva širší rozsah funkcií než IPv4 ARP:

- neighbor address resolution,
- router discovery,
- prefix discovery,
- Duplicate Address Detection,
- Neighbor Unreachability Detection,
- redirects,
- komunikáciu Router Solicitation a Router Advertisement.

NDP používa multicast namiesto broadcastu. Plošné blokovanie ICMPv6 môže rozbiť address configuration, default gateway discovery, neighbor resolution a PMTUD.

Pri IPv6 failure treba preto kontrolovať ICMPv6 policy rovnako vážne ako TCP alebo UDP rules.

## 19. Duplicate Address Detection

Pred plným použitím novej IPv6 adresy host typicky vykoná Duplicate Address Detection. Adresa môže byť počas procesu označená ako `tentative`.

Ak sa zistí konflikt, adresa sa nemá normálne použiť. Linux môže zobraziť flags cez:

```bash
ip -6 addr show
```

Pri diagnostike sleduj stavy ako:

- `tentative`,
- `dadfailed`,
- `deprecated`,
- `temporary`,
- `dynamic`.

Samotná prítomnosť adresy v konfigurácii teda nemusí znamenať, že je pripravená na source selection a komunikáciu.

## 20. Router Advertisements a SLAAC

Router Advertisement oznamuje hostom informácie o IPv6 linku, napríklad prefixes, default-router lifetime a configuration flags.

Pri SLAAC host vytvorí adresu z oznámeného prefixu a lokálneho interface-identifier mechanizmu. Súčasne sa z Router Advertisement učí default gateway.

```text
router odošle RA
  ↓
host zistí prefix a router lifetime
  ↓
vytvorí adresu
  ↓
vykoná DAD
  ↓
adresa sa stane použiteľnou
```

RA nie je iba „IPv6 DHCP odpoveď“. Je základným control-plane mechanizmom IPv6 linku.

## 21. DHCPv6

DHCPv6 môže prideľovať adresy alebo poskytovať ďalšie configuration data. Môže fungovať stateful alebo stateless podľa návrhu a Router Advertisement flags.

Dôležitý rozdiel oproti IPv4 DHCP: default gateway sa v bežnom IPv6 modeli učí z Router Advertisements, nie z DHCPv6 default-route option.

Možné kombinácie:

- SLAAC pre adresu a RA pre gateway,
- SLAAC plus stateless DHCPv6 pre doplnkové údaje,
- stateful DHCPv6 pre adresu plus RA pre gateway,
- statické adresovanie plus RA alebo statická route.

Prevádzka musí vedieť, ktorý model je autoritatívny. Inak môže byť host adresovaný, ale bez správneho DNS alebo default route state.

## 22. Privacy a stable addresses

Host môže mať na jednom interface viac IPv6 adries:

- link-local,
- stable global,
- temporary privacy address,
- deprecated staršiu adresu,
- ULA,
- viac prefixov počas renumberingu.

Privacy extensions vytvárajú dočasné source addresses, aby stabilný interface identifier neumožňoval jednoduché sledovanie klienta naprieč sieťami.

Serverové služby zvyčajne potrebujú stabilný listening a DNS model. Klientsky outbound traffic môže preferovať temporary source address. Preto „ktorú adresu vidím v `ip addr`“ a „ktorú source address kernel vyberie“ nie sú rovnaká otázka.

## 23. Source-address selection

Keď interface obsahuje viac adries, kernel vyberá source address podľa destination scope, prefix match, address state, policy a route.

Overenie konkrétneho rozhodnutia:

```bash
ip route get 198.51.100.10
ip -6 route get 2001:db8::10
```

Výstup môže ukázať selected source. Chybná source address môže spôsobiť:

- neexistujúci return path,
- firewall drop,
- nesprávnu DNS identity,
- asymetriu medzi interfaces,
- použitie deprecated alebo neočakávanej family.

Pri multi-homed hostoch a policy routingu je source selection zásadná časť troubleshooting-u.

## 24. Dual stack

Dual-stack host používa IPv4 aj IPv6 ako samostatné sieťové stacks. Každá family má vlastné:

- addresses,
- routes,
- neighbor state,
- firewall rules,
- DNS records,
- PMTU behavior,
- failure modes.

Resolver môže vrátiť A aj AAAA record. Klientsky algorithm, napríklad Happy Eyeballs, skúša families tak, aby nefunkčná IPv6 path nespôsobila dlhý používateľský timeout.

Dôležitý dôsledok:

```text
IPv4 funguje
≠
služba funguje pre klienta, ktorý preferuje IPv6
```

Testuj obe families explicitne:

```bash
curl -4 -v https://example.com/
curl -6 -v https://example.com/
ip -4 route
ip -6 route
```

## 25. IPv4-mapped IPv6 adresy

Aplikácia môže zobraziť IPv4 klienta ako:

```text
::ffff:192.0.2.10
```

Ide o IPv4-mapped IPv6 representation používanú niektorými socket APIs. Sama osebe nedokazuje, že traffic prešiel end-to-end cez IPv6.

Dual-stack listening behavior závisí od `IPV6_V6ONLY`, operačného systému a aplikácie. Socket na `[::]:443` môže alebo nemusí prijímať aj IPv4-mapped connections.

Pri diagnostike preto overuj reálnu address family flow-u cez `ss`, packet capture a aplikačné metadata.

## 26. Address planning

Dobrý IPv4/IPv6 address plan zohľadňuje:

- organizačné a environment boundaries,
- regions a Availability Zones,
- failure domains,
- routing summarization,
- firewall a security zones,
- on-premises, cloud, VPN a peering,
- Kubernetes Pod a Service CIDRs,
- future mergers a partner connectivity,
- growth a rezervy,
- IPv6 prefix delegation a renumbering.

Cieľom nie je maximalizovať percentuálne využitie každého subnetu. Príliš tesné alokácie zvyšujú počet budúcich migrácií a fragmentujú routing table.

Adresný priestor má podporovať topológiu. Ak možno z prefixu rozpoznať region, environment alebo failure domain bez vytvorenia rigidnej schémy, troubleshooting a route summarization sú jednoduchšie.

## 27. VLSM

Variable Length Subnet Masking umožňuje použiť rôzne prefix lengths podľa potreby:

```text
10.0.0.0/16
├── 10.0.0.0/20   production
├── 10.0.16.0/22  staging
├── 10.0.20.0/24  management
└── 10.0.21.0/27  point services
```

VLSM zvyšuje efektivitu, ale nesmie rozbiť sumarizáciu. Náhodne roztrúsené malé subnety môžu vytvoriť veľké množstvo špecifických routes a komplikovať policy.

Alokácie sa majú robiť od väčších blokov po menšie a s explicitnou rezervou pre rast.

## 28. Route summarization

Súvislé a správne zarovnané prefixes možno agregovať do jedného summary route.

Napríklad štyri `/24`:

```text
10.0.0.0/24
10.0.1.0/24
10.0.2.0/24
10.0.3.0/24
```

možno agregovať ako:

```text
10.0.0.0/22
```

Sumarizácia znižuje počet routes a izoluje interné zmeny. Má však aj failure semantics: summary môže smerovať traffic pre nealokovaný alebo nedostupný subprefix k agregujúcemu routeru.

Preto agregujúci bod často potrebuje discard/null route pre summary a presnejšie routes pre reálne dostupné subnets. Inak môže vzniknúť routing loop alebo nepredvídateľný fallback.

## 29. Renumbering a address lifecycle

IP adresy sa časom menia. Cloud migrácia, provider zmena, merger alebo IPv6 prefix delegation môžu vyžadovať renumbering.

Bezpečný lifecycle obsahuje:

1. pridanie nového prefixu popri starom,
2. aktualizáciu routes, firewallov a DNS,
3. overenie source-address selection,
4. zníženie DNS TTL pred cutoverom,
5. presun trafficu,
6. obdobie dual addressing,
7. označenie starej IPv6 adresy ako deprecated,
8. odstránenie starého prefixu až po overení dependencies.

Adresy zakódované priamo v aplikáciách, certifikátoch, allowlistoch alebo databázach zvyšujú cenu renumberingu.

## 30. Linux diagnostika

Základný inventár:

```bash
ip -4 addr
ip -6 addr
ip -4 route
ip -6 route
ip neigh
ip -6 neigh
```

Konkrétne route a source decision:

```bash
ip route get 198.51.100.10
ip -6 route get 2001:db8::10
```

Pri adrese kontroluj:

- prefix length,
- scope,
- dynamic/static pôvod,
- `tentative`, `dadfailed` alebo `deprecated` state,
- selected source,
- connected route,
- policy routing table,
- namespace, v ktorom sa príkaz vykonáva.

## 31. Troubleshooting: hosty sa považujú za susedov rozdielne

Postup:

1. zaznamenaj IP a prefix na oboch hostoch,
2. vypočítaj network range z pohľadu každého hosta,
3. over route selection na destination,
4. skontroluj ARP/NDP target,
5. over VLAN a link state,
6. zachyť neighbor discovery a packets,
7. skontroluj return path a firewall.

Chybný prefix môže vytvoriť stav:

```text
Host A → destination považuje za on-link a ARPuje priamo
Host B → source považuje za remote a odpovedá cez gateway
```

Výsledkom môže byť asymetria alebo úplný failure podľa router a firewall policy.

## 32. Troubleshooting: IPv6 preferencia spôsobuje timeout

Začni resolverom:

```bash
getent ahosts example.com
```

Porovnaj families:

```bash
curl -4 -v https://example.com/
curl -6 -v https://example.com/
```

Potom over IPv6 path:

```bash
ip -6 route get <IPv6>
ip -6 neigh
ping -6 <gateway-or-target>
sudo tcpdump -ni any ip6
```

Možné príčiny:

- AAAA record existuje, ale server alebo route nie,
- chýba IPv6 default route z RA,
- adresa zostala `tentative` alebo DAD zlyhal,
- firewall blokuje ICMPv6 alebo TCP,
- return path nepozná prefix,
- aplikácia počúva iba na IPv4,
- PMTUD zlyháva pre blokované Packet Too Big,
- DNS alebo load balancer vracia nefunkčný IPv6 endpoint.

## 33. Anti-patterny

### Prefix sa odhaduje podľa zvyku

Predpoklad `/24`, pretože adresa „vyzerá ako interná sieť“, môže zmeniť on-link decision a vytvoriť ARP failure.

### Subnet sa dimenzuje iba podľa dnešného počtu hostov

Ignorovanie rastu, provider reservations, HA a orchestrácie vedie k drahému renumberingu.

### Private adresa sa považuje za security control

Private space nezastupuje firewall, identity ani encryption.

### IPv6 sa vypne namiesto opravy

Vypnutie môže skryť chybnú RA, DNS, firewall alebo PMTU policy a vytvoriť nekonzistentné prostredie. Dual-stack failure sa má diagnostikovať po families.

### Summary route sa publikuje bez failure policy

Agregácia bez správneho discard route a ownershipu môže blackholovať alebo loopovať neexistujúce subprefixes.

## 34. Praktický mini-lab

### IPv4

Pre adresu `192.0.2.173/27` vypočítaj:

- network address,
- broadcast address,
- prvú a poslednú klasicky použiteľnú adresu,
- počet adries,
- susedný predchádzajúci a nasledujúci `/27` subnet.

Over výsledok:

```bash
ipcalc 192.0.2.173/27
```

### IPv6

Pre prefix:

```text
2001:db8:1234::/48
```

navrhni štyri `/64` subnety pre production, staging, management a test. Zvoľ subnet identifiers tak, aby zostal priestor na rast a aby prefixes boli čitateľné.

Potom vysvetli, ktoré adresy sa host naučí z RA, ktoré môže dostať cez DHCPv6 a odkiaľ získa default gateway.

## 35. Kontrolné otázky

1. Čo presne znamená CIDR prefix length?
2. Ako adresa a prefix ovplyvnia connected route a ARP target?
3. Ako vypočítaš network a broadcast pre IPv4 `/27`?
4. Prečo `/31` funguje na point-to-point linku?
5. Aké problémy spôsobujú overlapping private networks?
6. Ako TTL a hop limit chránia pred routing loopom?
7. Ako vzniká Path MTU black hole?
8. Prečo je `/64` štandardný IPv6 endpoint subnet?
9. Aký je rozdiel medzi link-local, ULA a global-unicast IPv6 adresou?
10. Ktoré funkcie poskytuje NDP?
11. Aký je rozdiel medzi SLAAC, stateless DHCPv6 a stateful DHCPv6?
12. Odkiaľ sa IPv6 host učí default gateway?
13. Prečo môže mať interface viac IPv6 adries a ako sa vyberá source?
14. Prečo IPv4 success nevylučuje dual-stack incident?
15. Ako VLSM a summarization ovplyvňujú prevádzkovateľnosť siete?

## 36. Zhrnutie

IPv4 a IPv6 používajú prefixy na vyjadrenie routovateľného address space. Subnetting nie je iba výpočet počtu hostov; určuje on-link správanie, neighbor resolution, routing hierarchy, failure domains a budúcu prepojiteľnosť. IPv6 pridáva rozsiahly 128-bit priestor, NDP, Router Advertisements, SLAAC a samostatný dual-stack lifecycle. Správna diagnostika preto vždy kontroluje konkrétnu family, prefix, source address, route, neighbor state a return path.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Ethernet, MAC a ARP](ethernet-mac-arp.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Routing a default gateway →](routing-and-default-gateway.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
