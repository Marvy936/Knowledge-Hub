# DHCP

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [IPv4, IPv6 a subnetting](ipv4-ipv6-subnetting.md), [Ethernet, MAC a ARP](ethernet-mac-arp.md), [DNS](dns.md)
- Súvisiace témy: routing, VLANs, PXE, cloud networking, IP address management

## 1. Čo DHCP poskytuje

Dynamic Host Configuration Protocol poskytuje klientovi sieťové konfiguračné údaje s časovo obmedzenou platnosťou. DHCPv4 môže prideliť IPv4 adresu, prefix masku, default gateway, DNS resolvery, search domains, routes a ďalšie options.

DHCP nevytvára link, neroutuje packets a negarantuje dostupnosť gateway ani DNS. Distribuuje desired configuration, ktorú klientsky network manager aplikuje do interface, routing table a resolver state.

```text
DHCP lease/options
  ↓
client network manager
  ├── IP address
  ├── connected/default routes
  ├── DNS resolver configuration
  └── ďalšie platformové nastavenia
```

## 2. Prečo sa používajú leases

Adresa nie je klientovi pridelená navždy. Lease umožňuje serveru znovu použiť address space, reagovať na zmenu topológie a centrálne meniť konfiguráciu.

Časovo obmedzený model rieši:

- Mobility — klient môže prejsť do iného subnetu a dostať inú konfiguráciu.
- Churn — krátkodobé zariadenia nezablokujú adresu natrvalo.
- Policy change — po obnove môže klient dostať novú gateway, DNS alebo routes.
- Capacity management — server eviduje aktívne a expirované pridelenia.
- Conflict reduction — centrálna lease database koordinuje dynamický pool.

## 3. DHCPv4 používa UDP a broadcast bootstrap

Klient na začiatku nemusí mať použiteľnú IPv4 adresu ani poznať server. Preto DHCPv4 používa UDP porty `68` na klientovi a `67` na serveri a prvé správy môžu byť broadcast.

```text
source      0.0.0.0:68
destination 255.255.255.255:67
```

Broadcast rieši bootstrap v lokálnom L2 segmente. Router ho bežne neforwarduje do iného subnetu, preto centralizovaný server potrebuje relay.

## 4. DORA je skratka pre základnú výmenu

DHCPv4 bootstrap sa často označuje DORA. Táto skratka tu znamená Discover, Offer, Request, Acknowledge a nesúvisí s DevOps DORA metrikami.

```text
Client                                Server
DHCPDISCOVER                     ─────►
                                ◄───── DHCPOFFER
DHCPREQUEST                      ─────►
                                ◄───── DHCPACK
```

DORA opisuje najbežnejší initial allocation flow. Renewal, reboot a decline používajú ďalšie varianty a správy.

## 5. DHCPDISCOVER

Klient v INIT stave hľadá server. Správa obsahuje transaction ID, client identity, parameter request list a prípadne informácie o triede alebo predchádzajúcej adrese.

Discover môže vidieť viac serverov. Každý môže podľa scope, policy a dostupnej capacity vytvoriť vlastnú ponuku.

Absencia Discover v packet capture ukazuje klientsky alebo linkový problém. Discover bez Offer presúva podozrenie na relay, server, scope alebo security policy.

## 6. DHCPOFFER

Offer obsahuje navrhovanú adresu a konfiguračné options. Je to ponuka, nie finálne vlastníctvo adresy.

Server typicky rezervuje adresu na krátky čas, aby ju počas výberu neponúkol inému klientovi. Implementácia musí zvládnuť neakceptované a expirované offers bez dlhodobého úniku pool capacity.

Klient môže dostať viac offers a vybrať jednu podľa svojej implementácie a policy.

## 7. DHCPREQUEST má viac významov

DHCPREQUEST sa používa v rôznych lifecycle stavoch. Jeho fields a broadcast/unicast forma hovoria serverom, čo klient robí.

- Selecting — klient broadcastom oznámi, ktorú offer a server identifier vybral; ostatné servery môžu svoje offers uvoľniť.
- Init-reboot — klient po reštarte žiada potvrdenie predtým používanej adresy bez úplného Discover flow.
- Renewing — klient unicastom žiada pôvodný server o predĺženie aktívnej lease.
- Rebinding — klient broadcastom hľadá ľubovoľný server, ktorý lease predĺži.

Pri capture nestačí vidieť názov správy; treba interpretovať client state, requested IP, server identifier a destination.

## 8. DHCPACK a DHCPNAK

DHCPACK potvrdí lease a poskytne finálne options. Klient až potom aplikuje adresu podľa svojej implementácie a môže vykonať conflict detection.

DHCPNAK hovorí, že requested address alebo configuration nie je platná, napríklad preto, že klient sa presunul do iného subnetu alebo lease už nemožno obnoviť. Klient má neplatný stav zahodiť a vrátiť sa k initial discovery.

NAK storm môže znamenať chybný relay, overlapping scopes, nejednotné HA servery alebo klienta používajúceho starú cached lease v novom segmente.

## 9. Ďalšie DHCPv4 správy

- DHCPDECLINE — klient oznámi, že ponúknutá adresa vyzerá byť už používaná.
- DHCPRELEASE — klient dobrovoľne vráti lease serveru; nie každý shutdown ho spoľahlivo odošle.
- DHCPINFORM — klient už má adresu, ale žiada ďalšie options.

Server nemôže capacity plán postaviť na predpoklade, že každý klient pošle RELEASE. Lease expiration zostáva základný reclamation mechanizmus.

## 10. Lease state machine

Zjednodušený klientsky lifecycle:

```text
INIT
  ↓ Discover/Offer
SELECTING
  ↓ Request
REQUESTING
  ↓ ACK
BOUND
  ↓ T1
RENEWING
  ↓ T2
REBINDING
  ↓ expiration
INIT
```

Každý stav má inú komunikačnú stratégiu a failure semantics. Klient s platnou lease nemusí opakovať broadcast bootstrap pri každom renewal.

## 11. T1 renewal

Pri T1 sa klient pokúsi obnoviť lease u pôvodného servera, typicky unicastom. Stále môže používať pridelenú adresu a bežnú konektivitu.

Ak je server nedostupný, klient lease okamžite nestratí. Pokračuje v používaní adresy a opakuje renewal podľa timer policy až do T2.

Failure iba počas renewal môže byť skrytý dlhý čas. Preto treba monitorovať server dostupnosť aj lease renewal success, nie iba initial DORA.

## 12. T2 rebinding

Pri T2 klient predpokladá, že pôvodný server nemusí byť dostupný, a broadcastom osloví ľubovoľný vhodný server.

Rebinding vyžaduje, aby HA alebo náhradný server poznal lease state alebo vedel bezpečne rozhodnúť o predĺžení. Nekoordinované servery môžu vytvoriť conflicts alebo NAK behavior.

## 13. Expiration

Po expirácie klient už nemá právo adresu používať. Mal by ju odstrániť z interface, zrušiť závislé routes a vrátiť sa do initial state.

Aplikácie môžu mať otvorené connections viazané na expirovanú adresu. Lease loss preto nie je iba konfiguračný event; môže prerušiť existujúce sessions a zmeniť DNS source identity.

## 14. Lease time ako capacity a resilience trade-off

Krátka lease:

- rýchlejšie reclaimuje adresy,
- rýchlejšie distribuuje policy zmenu,
- zvyšuje renewal traffic a závislosť od servera.

Dlhá lease:

- znižuje control-plane traffic,
- umožní klientom dlhšie fungovať pri DHCP výpadku,
- spomaľuje reclaim a zmenu configuration.

Lease duration má zodpovedať churnu, veľkosti poolu a požadovanej odolnosti.

## 15. Options tvoria konfiguračný kontrakt

DHCP options nie sú iba doplnky. Niektoré priamo menia packet path alebo name resolution.

- Subnet mask/prefix — určuje, ktoré destinations klient považuje za on-link.
- Router option — pridáva default gateway.
- DNS servers — určuje recursive resolver path.
- Domain search — ovplyvňuje relative-name expansion.
- Classless static routes — pridáva presnejšie routes a môže meniť default-route správanie.
- MTU — ovplyvňuje packet size a Path MTU behavior.
- NTP servers — ovplyvňujú čas a nepriamo TLS, logs a authentication.
- PXE options — určujú boot server a boot artifact location.

Klient nemusí podporovať každú option a network manager môže policy prepísať.

## 16. Poradie route options je dôležité

Ak server poskytuje classless static routes, klient môže podľa štandardu alebo implementácie ignorovať tradičný router option a zostaviť routing table z classless route option.

Nesprávna option preto môže vytvoriť stav:

```text
IP adresa existuje
DNS funguje
časť destinations je reachable
Internet alebo private subnet nie je reachable
```

Diagnostika musí porovnať lease options s výslednou `ip route`, nie iba potvrdiť pridelenú adresu.

## 17. Scope, subnet a pool

Scope predstavuje configuration policy pre konkrétny subnet alebo relay context. Pool je množina dynamicky prideľovaných adries v tomto scope.

```text
scope: 192.0.2.0/24
├── options: gateway 192.0.2.1, DNS 192.0.2.53
├── exclusions: 192.0.2.1–192.0.2.49
└── dynamic pool: 192.0.2.50–192.0.2.220
```

Exclusions chránia adresy používané staticky alebo inou infraštruktúrou. Pool sa nemá prekrývať s nekoordino­vaným statickým rozsahom.

## 18. Reservation

Reservation mapuje klientsku identitu na stabilnú adresu, ale stále používa DHCP lifecycle a options.

Identita môže byť:

- MAC address — bežná, ale nie vždy autoritatívna pri virtualizácii alebo relayi.
- Client identifier — klient môže posielať hodnotu odlišnú od MAC.
- Relay metadata — policy môže brať do úvahy circuit alebo remote ID.
- Vendor/user class — umožňuje rozdielne options podľa typu zariadenia.

Reservation a manuálne statická IP nie sú to isté. Reservation zostáva viditeľná v centrálnej lease a policy databáze.

## 19. Klientská identita a klonovanie

VM alebo image clone môže zdediť machine-id, DHCP client identifier alebo cached lease. Aj pri novej MAC môže server klienta považovať za pôvodné zariadenie, alebo naopak.

Pri klonovaní kontroluj:

- virtual NIC MAC,
- DHCP client identifier,
- machine-id,
- cloud-init datasource state,
- cached lease files,
- persistent network profile.

Duplicitná identita môže spôsobiť striedanie jednej lease medzi dvoma hostmi.

## 20. DHCP relay

Relay prijme klientsky broadcast v subnet-e a pošle ho serveru unicastom. Do správy vloží informáciu o segmente, aby server vybral správny scope.

```text
client broadcast v VLAN 120
  ↓
gateway / relay
  ├── giaddr alebo link information
  └── optional relay-agent metadata
  ↓ unicast
central DHCP server
```

Serverova route späť k relayi a relayova delivery klientovi sú samostatné časti pathu.

## 21. `giaddr` a relay-agent information

V DHCPv4 relay typicky nastaví gateway IP address field `giaddr`. Server podľa neho určí subnet a destination návratovej odpovede.

Option 82 môže niesť circuit ID, remote ID alebo ďalšie access-layer údaje. Používa sa pre policy, subscriber identity alebo security validation.

Chybná relay metadata môže spôsobiť:

- výber nesprávneho scope,
- žiadnu matching policy,
- nesprávnu reservation,
- drop serverom pre nedôveryhodnú relay informáciu.

## 22. Relay a routing musia fungovať obojsmerne

Discover môže doraziť serveru, ale Offer sa nemusí vrátiť klientovi. Treba overiť:

- route servera k relay address,
- firewall pre UDP/67 a relay traffic,
- relay source interface a VRF,
- správny egress VLAN na klienta,
- broadcast/unicast flag klienta,
- server policy pre relay address.

Capture iba na klientskom interface nemusí odhaliť, či server odpoveď vytvoril.

## 23. Pool exhaustion

Pool je vyčerpaný, keď server nemá adresu, ktorú môže bezpečne ponúknuť novému klientovi.

Príčiny:

- reálny počet klientov prekročil návrh,
- leases sú príliš dlhé pre daný churn,
- abandoned/conflict addresses zostávajú blokované,
- reservations spotrebovali veľkú časť poolu,
- rogue alebo test clients generujú množstvo identities,
- staré lease state sa nereplikuje alebo neupratuje.

Capacity sa má sledovať ako počet voľných, aktívnych, offered, declined a expirovaných leases, nie iba veľkosť prefixu.

## 24. Address conflict

Dva hosty používajúce rovnakú IPv4 adresu vytvárajú ARP instability, prerušované connections a nepredvídateľný return path.

Časté príčiny:

- statická adresa leží v dynamic poole,
- dva nekoordino­vané servery prideľujú rovnaký priestor,
- stale lease database,
- snapshot alebo clone obnovil starú identity,
- chybná reservation,
- rogue server,
- manuálna konfigurácia ignoruje IPAM.

## 25. Conflict detection a DHCPDECLINE

Klient môže pred použitím adresy vyslať ARP probe. Ak zistí odpoveď, pošle DHCPDECLINE a adresu nepoužije.

Server môže sám pingovať alebo ARPovať pred offer, ale táto kontrola má race conditions a nemusí vidieť spiace alebo filtrované zariadenie.

Conflict detection je defense-in-depth. Základná ochrana je neprekrývajúci sa IPAM a jeden koordinovaný allocation authority.

## 26. Rogue DHCP server

Neautorizovaný server môže odpovedať rýchlejšie než legitímny a poslať klientom útočníkovu gateway, DNS alebo routes.

Dôsledky:

- man-in-the-middle,
- name-resolution manipulation,
- denial of service,
- traffic redirection mimo bezpečnostných controls.

Switchové DHCP snooping označuje trusted ports pre server responses a blokuje offers/ACK z untrusted access portov. Binding database môže podporiť Dynamic ARP Inspection a IP Source Guard.

## 27. DHCP snooping trust model

Trusted port neznamená „bezpečný endpoint“. Znamená port, cez ktorý sú povolené server-side DHCP správy, typicky uplink k relayu alebo legitímnemu serveru.

Nesprávne označenie access portu ako trusted umožní rogue server. Nesprávne označenie legitímneho uplinku ako untrusted zablokuje všetky Offers.

Snooping policy musí zodpovedať L2 topológii, trunks, relays a HA server pathom.

## 28. DHCP server HA

Produkčný DHCP potrebuje spoločný lease-state alebo koordinovaný allocation model. Jednoduché spustenie dvoch serverov nad rovnakým poolom bez koordinácie môže prideliť rovnakú adresu dvom klientom.

HA modely môžu používať:

- failover protocol alebo lease replication,
- rozdelené address ranges,
- active/standby službu,
- platformový distributed control plane.

Treba testovať nielen initial allocation, ale renewal počas partition, failover a návrat pôvodného servera.

## 29. Split-scope trade-off

Rozdelenie poolu medzi dva nezávislé servery znižuje konflikt, ale každý server má iba časť capacity. Pri výpadku jedného servera klienti môžu získať adresu iba zo zostávajúceho rozsahu.

Tento model nerieši plnú synchronizáciu reservations, active leases a renewal semantics. Je jednoduchší, ale má slabší failure model než koordinované HA.

## 30. DHCP a Dynamic DNS

DHCP server alebo klient môže aktualizovať DNS records pri pridelení a uvoľnení lease.

```text
lease allocation
  ↓
forward A/AAAA update
  ↓
reverse PTR update
```

Riziká:

- stale records po expirácii,
- race medzi klientom a serverom,
- nesprávne ownership update credentials,
- krátke leases vytvárajú vysoký DNS update churn,
- forward a reverse zone sa aktualizujú rozdielne.

DDNS lifecycle musí byť koordinovaný s lease state a bezpečne autentizovaný.

## 31. DHCPv6 je samostatný protokol

DHCPv6 používa UDP port `546` na klientovi a `547` na serveri. Správy, identity a relay model sa líšia od DHCPv4.

Základný stateful flow:

```text
SOLICIT
  ↓
ADVERTISE
  ↓
REQUEST
  ↓
REPLY
```

Rapid Commit môže pri podpore oboch strán skrátiť výmenu.

## 32. DUID a IAID

DHCPv6 klient sa identifikuje pomocou DUID a pre jednotlivé interfaces alebo identity associations používa IAID.

- DUID — stabilnejšia identita klienta, nemusí byť totožná s MAC.
- IAID — rozlišuje identity association v rámci klienta.
- IA_NA — non-temporary address assignment.
- IA_PD — prefix delegation, napríklad router dostane prefix pre downstream siete.

Klonovanie DUID môže spôsobiť podobné problémy ako duplicitný DHCPv4 client identifier.

## 33. Stateful a stateless DHCPv6

Stateful DHCPv6 prideľuje IPv6 adresu a vedie lease state. Stateless DHCPv6 neposkytuje adresu; klient ju získa cez SLAAC a DHCPv6 dodá napríklad DNS options.

```text
SLAAC address + DHCPv6 DNS
```

Klientská podpora sa líši. Nie všetky operačné systémy reagujú na RA flags identicky, preto návrh musí vychádzať z reálnych klientov.

## 34. Router Advertisement zostáva kľúčový

IPv6 default router sa host typicky učí z Router Advertisement, nie z DHCPv6 default-gateway option.

RA poskytuje:

- on-link prefixes,
- default-router lifetime,
- SLAAC prefix information,
- M/O flags pre DHCPv6 guidance,
- ďalšie neighbor-discovery údaje.

Funkčný DHCPv6 server nekompenzuje chýbajúce alebo blokované RA. Klient môže mať IPv6 adresu, ale žiadnu default route.

## 35. RA M a O flags

Managed flag typicky naznačuje použitie stateful DHCPv6 pre adresy. Other Configuration flag naznačuje DHCPv6 pre ďalšie options.

Tieto flags sú guidance, nie absolútny univerzálny behavior contract všetkých klientov. Network design musí testovať Linux, Windows, mobile a embedded implementácie podľa cieľového prostredia.

## 36. Prefix delegation

DHCPv6 Prefix Delegation prideľuje klientskemu routeru celý prefix, nie jednu adresu. Router ho následne rozdelí alebo inzeruje do downstream segmentov.

```text
ISP/server → delegates 2001:db8:1000::/56
customer router
  ├── LAN1 /64
  ├── LAN2 /64
  └── guest /64
```

Renumbering a lease expiration prefixu ovplyvnia všetky downstream addresses a routes. Klientsky router musí správne spravovať preferred a valid lifetimes.

## 37. Cloud a virtualizované prostredie

Cloud provider môže DHCP implementovať ako virtuálnu control-plane službu. Broadcast nemusí fyzicky prechádzať klasickou L2 sieťou a server address môže byť platformovo špecifická.

DHCP options môžu pochádzať z virtual network configuration, subnet option setu alebo metadata služby. Ručná zmena klienta môže byť pri reštarte prepísaná cloud-init alebo network agentom.

## 38. PXE a network boot

DHCP môže poskytnúť bootstrap informácie:

- next server,
- boot filename alebo URL,
- architecture/client-class specific options,
- proxyDHCP údaje podľa prostredia.

```text
DHCP adresa a boot metadata
  ↓
TFTP/HTTP fetch bootloadera
  ↓
bootloader načíta kernel alebo installer
```

DHCP neprenáša samotný boot image. Iba nasmeruje klienta na ďalší protokol a artifact.

## 39. Klientsky zdroj pravdy v Linuxe

Konfiguráciu môže spravovať NetworkManager, systemd-networkd, dhclient, cloud-init alebo iný agent. Lease file path nie je univerzálny.

```bash
ip addr
ip route
resolvectl status
nmcli device show
networkctl status
journalctl -u NetworkManager -u systemd-networkd
```

Autoritatívne je spojenie:

```text
manager configuration
+ manager logs
+ packet capture
+ aplikovaný kernel/resolver state
```

## 40. Packet capture DHCPv4

```bash
sudo tcpdump -eni <iface> -vvv 'udp port 67 or udp port 68'
```

Capture má ukázať:

- client MAC a client identifier,
- transaction ID,
- Discover/Offer/Request/ACK poradie,
- requested IP a server identifier,
- relay address alebo Option 82,
- offered prefix, gateway, DNS a lease timers,
- viac odpovedajúcich serverov.

`-e` je užitočné, pretože zobrazuje L2 source a destination pri broadcast bootstrap-e.

## 41. Packet capture DHCPv6

```bash
sudo tcpdump -ni <iface> -vvv 'udp port 546 or udp port 547'
```

Pri DHCPv6 sleduj:

- SOLICIT/ADVERTISE/REQUEST/REPLY,
- DUID a IAID,
- IA_NA alebo IA_PD,
- lifetimes,
- relay-forward/relay-reply,
- súčasné Router Advertisements a NDP.

Samotný DHCPv6 capture nestačí na vysvetlenie default route; treba zachytiť aj ICMPv6 RA.

## 42. Diagnostický postup: klient nedostane IPv4 adresu

1. Link — interface je up, má carrier a správnu VLAN?
2. Client manager — spúšťa DHCP a používa správny profile?
3. Discover — odchádza z očakávaného interface a namespace?
4. Relay — prijíma broadcast a forwarduje ho správnemu serveru?
5. Server — existuje matching scope, voľná adresa a policy pre identity?
6. Offer — server ju vytvoril a vrátila sa cez relay?
7. Request/ACK — klient vybral server a server lease potvrdil?
8. Conflict detection — klient adresu neodmietol?
9. Apply — network manager pridal address, routes a DNS?
10. Post-configuration — gateway, DNS a route sú reálne funkčné?

## 43. Diagnostický postup: adresa funguje iba do T1/T2

1. Zisti lease duration, T1 a T2 z klientského state alebo capture.
2. Zachyť unicast DHCPREQUEST pri renewal.
3. Over route a firewall klienta k pôvodnému serveru.
4. Skontroluj server logs a lease database.
5. Sleduj prechod na broadcast rebinding.
6. Over HA server coordination.
7. Skontroluj, či klient dostane ACK/NAK a správne ho aplikuje.

Initial DORA môže byť zdravé, zatiaľ čo unicast renewal path je blokovaný.

## 44. Diagnostický postup: klient má IP, ale nie konektivitu

Porovnaj received options s kernel state:

```bash
ip addr
ip route
resolvectl status
```

Skontroluj:

- správny prefix a on-link rozhodovanie,
- default gateway a classless routes,
- gateway ARP/NDP reachability,
- DNS resolvery a search domains,
- MTU,
- address conflict,
- policy prepísanú lokálnou statickou konfiguráciou.

DHCP môže byť príčinou aj po úspešnom pridelení adresy.

## 45. Diagnostický postup: niektorí klienti dostávajú inú konfiguráciu

1. Porovnaj client identifiers, vendor/user class a relay metadata.
2. Skontroluj overlapping scopes a reservations.
3. Zachyť všetky Offers a identifikuj rogue server.
4. Over HA server configuration a replication.
5. Porovnaj VLAN/relay path klientov.
6. Skontroluj policy podľa Option 82 alebo circuit ID.
7. Over cached lease a init-reboot behavior.

## 46. Typické symptómy

### IPv4 link-local `169.254.0.0/16`

Klient mohol prejsť na link-local fallback, pretože nezískal DHCP lease. Treba potvrdiť klientsky manager a packet exchange; samotná adresa nie je univerzálny dôkaz.

### Pool exhausted

Noví klienti nedostávajú Offer, zatiaľ čo existujúce leases fungujú. Sleduj free capacity, lease duration, abandoned addresses a identity churn.

### Nesprávny subnet

Relay alebo server vybral chybný scope, prípadne odpovedal rogue server. Výsledkom môže byť nefunkčný on-link a default-route model.

### Funguje po reštarte, neskôr vypadne

Initial allocation funguje, ale renewal alebo rebinding path zlyháva. Zameraj sa na T1/T2 traffic a server state.

### DHCPv6 adresa bez Internetu

Klient dostal address lease, ale chýba Router Advertisement/default route alebo je blokovaný ICMPv6.

## 47. Bezpečný prevádzkový model

- IPAM authority — dynamické, reserved a statické ranges sa nesmú prekrývať bez koordinácie.
- HA — servery musia zdieľať alebo bezpečne rozdeliť lease state.
- Access-layer protection — snooping a relay trust majú blokovať rogue responses.
- Capacity monitoring — sleduj pool utilization a lease-state kategórie.
- Change validation — option zmena sa testuje na route, DNS a renewal lifecycle.
- Audit — reservations, policy classes a relay metadata majú mať vlastníka a históriu.
- Recovery — tím musí vedieť obnoviť lease database bez duplicitného allocation.

## 48. Časté omyly

### „DHCP vytvára default gateway“

DHCP klientovi iba oznámi adresu gateway. Samotný router, route a L2 reachability musia existovať nezávisle.

### „Reservation je statická IP“

Reservation je centrálne DHCP-managed stabilné pridelenie, ktoré stále používa lease a options lifecycle.

### „Broadcast automaticky prejde routerom“

DHCPv4 bootstrap broadcast zostáva v L2 domain, pokiaľ relay alebo platforma nevykoná špeciálne forwardovanie.

### „Keď klient dostal IP, DHCP funguje správne“

Prefix, routes, DNS, MTU, renewal timers alebo classless options môžu byť nesprávne.

### „Dva DHCP servery automaticky znamenajú HA“

Bez koordinácie lease state môžu prideľovať konfliktné adresy alebo rozdielne options.

### „DHCPv6 poskytne celý IPv6 network setup“

Default router a veľká časť on-link/SLAAC informácií prichádzajú z Router Advertisements.

### „DHCP RELEASE vždy okamžite uvoľní adresu“

Klient nemusí RELEASE poslať alebo správa nemusí doraziť. Server sa musí spoliehať aj na lease expiration.

## 49. Kontrolné otázky

1. Čo DHCP konfiguruje a čo nerobí?
2. Prečo DHCPv4 pri bootstrap-e používa broadcast?
3. Čo znamená DORA v DHCP kontexte?
4. Ako sa líšia selecting, init-reboot, renewing a rebinding DHCPREQUEST?
5. Aký je rozdiel medzi T1, T2 a lease expiration?
6. Prečo krátka lease zvyšuje control-plane záťaž?
7. Ako classless route option môže zmeniť výslednú routing table?
8. Aký je rozdiel medzi scope, pool, exclusion a reservation?
9. Prečo reservation nemusí byť viazaná iba na MAC?
10. Ako relay vyberá správny scope a načo slúži Option 82?
11. Ako vzniká pool exhaustion aj pri zdanlivo veľkom subnet-e?
12. Prečo ARP conflict detection nie je úplná ochrana?
13. Ako DHCP snooping blokuje rogue server?
14. Prečo dva nezávislé servery nad rovnakým poolom nie sú HA?
15. Ako DHCPv6 DUID a IAID súvisia s klientskou identitou?
16. Aký je rozdiel medzi stateful a stateless DHCPv6?
17. Prečo DHCPv6 adresa nedokazuje existenciu default route?
18. Ako packet capture odlíši klientsky, relay a server-side failure?
19. Prečo PXE používa DHCP iba na bootstrap metadata?
20. Ako by si diagnostikoval lease, ktorá zlyhá až pri renewal?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: DNS](dns.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: NAT →](nat.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
