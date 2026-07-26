# NAT

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [Routing a default gateway](routing-and-default-gateway.md), [Ports a sockets](ports-and-sockets.md), [TCP a UDP](tcp-and-udp.md)
- Súvisiace témy: firewalls, load balancing, conntrack, container networking, cloud gateways, IPv6

## 1. Problém, ktorý NAT rieši

Predstavme si firmu Atlas. Interná aplikácia Orders beží na adrese `10.20.1.15` a pri spracovaní objednávky volá externú platobnú službu `198.51.100.20:443`. Privátna adresa `10.20.1.15` sa vo verejnom Internete neroutuje, preto odpoveď nemôže byť doručená priamo späť na tento endpoint.

Atlas má egress gateway s verejnou adresou `203.0.113.5`. Gateway môže pri odchode prepísať source endpoint:

```text
pôvodný flow
10.20.1.15:45000 → 198.51.100.20:443

flow viditeľný na Internete
203.0.113.5:62001 → 198.51.100.20:443
```

Tento preklad je NAT — Network Address Translation. NAT zmení adresu alebo port v packet headeri a pri stateful modeli si zapamätá vzťah medzi pôvodným a preloženým flowom.

NAT však nerieši celý request path. Funkčný flow potrebuje:

```text
route na translation point
→ translation rule a voľnú mapping kapacitu
→ firewall allow
→ route k cieľu
→ odpoveď cez rovnaký state owner
→ reverse translation
→ doručenie pôvodnému socketu
```

Routing rozhoduje, kam packet ide. NAT rozhoduje, aké endpoint fields bude mať. Firewall rozhoduje, či smie pokračovať. Aplikácia rozhoduje, čo packet znamená.

## 2. Dominantný mentálny model

Stateful NAT treba chápať ako lifecycle jedného flowu:

```text
original tuple
→ prvý packet a rule lookup
→ výber translated tuple
→ uloženie obojsmerného mappingu
→ ďalšie packets používajú mapping
→ return packet nájde reverse mapping
→ timeout alebo close odstráni state
```

Pre TCP flow Atlas Orders môže mapping vyzerať takto:

```text
original direction
10.20.1.15:45000 → 198.51.100.20:443

translated direction
203.0.113.5:62001 → 198.51.100.20:443

reply on public side
198.51.100.20:443 → 203.0.113.5:62001

reverse-translated reply
198.51.100.20:443 → 10.20.1.15:45000
```

Mapping musí jednoznačne rozlišovať protocol, source a destination endpointy a smer. Samotná verejná IP nestačí, pretože ju môže súčasne používať veľa klientov.

## 3. Prvý packet je rozhodujúci

Pri prvom packete nového flowu translation point typicky:

1. prijme packet v konkrétnom interface, namespace a hooku,
2. vykoná conntrack lookup,
3. klasifikuje packet ako nový flow,
4. vyhodnotí NAT policy,
5. vyberie preloženú adresu a prípadne port,
6. vytvorí obojsmerný mapping,
7. aplikuje firewall a routing rozhodnutie,
8. odošle packet ďalej.

Ďalšie packets sa už priraďujú k existujúcemu state. NAT pravidlo sa nemusí pre každý packet rozhodovať od začiatku.

Dôležitý dôsledok:

```text
zmena NAT pravidla
≠
okamžitá zmena existujúcich connections
```

Staré flows môžu pokračovať podľa starého mappingu, kým conntrack entry nezanikne. Pri overovaní zmeny treba vytvoriť nový flow, nie iba opätovne použiť existujúcu pooled connection.

## 4. SNAT a outbound cesta Atlas Orders

Source NAT mení source endpoint. Orders pošle nový TCP flow na platobný server:

```text
Orders socket
10.20.1.15:45000
    ↓ default route
egress gateway inside interface
    ↓ conntrack NEW
    ↓ SNAT/PAT
egress gateway outside interface
203.0.113.5:62001
    ↓ Internet
payment API
198.51.100.20:443
```

Aby tento tok fungoval, musia sedieť všetky hranice:

- Orders má route na gateway.
- Gateway má povolený IP forwarding.
- Packet zodpovedá SNAT policy.
- Gateway má voľný preložený port a conntrack entry.
- FORWARD policy povoľuje nový outbound flow.
- Verejná strana má route k platobnej službe.
- Odpoveď sa vracia na `203.0.113.5`.
- Gateway stále vlastní mapping a vie vykonať reverse translation.

Ak packet odíde so source `10.20.1.15`, externá služba spravidla nemá route späť. NAT teda nevytvára cestu sám; upravuje identitu flowu tak, aby return routing mohol fungovať.

## 5. PAT a kapacita jednej verejnej adresy

Port Address Translation umožní zdieľať jednu verejnú IP:

```text
10.20.1.15:45000 → 203.0.113.5:62001
10.20.1.16:45000 → 203.0.113.5:62002
10.20.1.17:52000 → 203.0.113.5:62003
```

Verejná IP však neposkytuje nekonečnú kapacitu. Každý aktívny mapping potrebuje jednoznačný translated tuple a state.

Typický capacity incident:

```text
existujúce connections fungujú
→ nové connections začnú timeoutovať
→ failure rate rastie s concurrency
→ po poklese loadu sa situácia dočasne zlepší
```

Možné mechanizmy sú:

- source-port exhaustion,
- conntrack table exhaustion,
- veľa krátkych connections bez pooling-u,
- retry storm,
- veľa idle long-lived flows,
- dlhé UDP timeouts,
- malý pool verejných source adries,
- provider-specific per-destination limit.

Náprava sa musí opierať o meranie. Zväčšiť conntrack table nepomôže, ak limitom je portový priestor. Skrátiť timeouty môže uvoľniť state, ale zároveň rozbiť legitímne idle connections.

## 6. DNAT a publikovanie služby

Destination NAT mení destination endpoint. Atlas publikuje edge endpoint `203.0.113.5:443`, ktorý sa prekladá na interný reverse proxy `10.20.2.10:8443`:

```text
client
    ↓ destination 203.0.113.5:443
translation point
    ↓ DNAT
reverse proxy
10.20.2.10:8443
```

DNAT sa musí vykonať pred finálnym route lookupom k backendu, pretože po preklade sa zmenil cieľ packetu.

Return path:

```text
reverse proxy 10.20.2.10:8443
    ↓ response toward client
translation point
    ↓ reverse DNAT
source becomes 203.0.113.5:443
    ↓
client
```

Samotné DNAT pravidlo službu nesprístupní. Potrebné sú aj:

- packet doručený na externú adresu,
- IP forwarding,
- FORWARD allow,
- route k `10.20.2.10`,
- listener na porte `8443`,
- backendová route späť cez translation point,
- zachovaný conntrack state,
- správny TLS a aplikačný protokol.

Ak backend odpovie inou cestou, klient môže dostať packet z neočakávanej source adresy alebo ho stateful policy zahodí.

## 7. Return path je súčasť NAT correctness

Stateful NAT vlastní obojsmerný mapping. Oba smery flowu preto musia prejsť bodom, ktorý tento mapping pozná.

```text
forward
client → NAT A → backend

chybný return
backend → router B → client
```

Ak return obíde NAT A:

- reverse translation sa nevykoná,
- client tuple nebude sedieť,
- conntrack state na NAT A uvidí iba polovicu flowu,
- stateful firewall môže odpoveď vyhodnotiť ako neplatnú,
- packet captures na rôznych miestach budú vyzerať protichodne.

Asymetriu môžu vytvoriť multiple defaults, policy routing, ECMP, chybná backend gateway, cloud route table alebo failover na druhý NAT node bez state synchronizácie.

## 8. Conntrack state nie je socket ani aplikácia

Translation point používa conntrack na priradenie packetov k flowu. Bežné klasifikácie sú `NEW`, `ESTABLISHED`, `RELATED` a `INVALID`.

Treba odlíšiť tri stavy:

```text
endpoint socket state
≠
middlebox conntrack/NAT state
≠
application business state
```

Conntrack `ESTABLISHED` môže iba znamenať, že middlebox videl obojsmerný transportný traffic. Neznamená úspešný TLS handshake, autorizovanú platbu ani zdravý backend.

Naopak, socket môže zostať otvorený, hoci NAT mapping po inactivity timeoute zanikol. Ďalší packet potom narazí na chýbajúci middlebox state.

Pozorovanie v Linuxe:

```bash
sudo conntrack -L
sudo conntrack -S
sysctl net.netfilter.nf_conntrack_count
sysctl net.netfilter.nf_conntrack_max
journalctl -k -b
```

## 9. TCP a UDP majú odlišný state lifecycle

TCP poskytuje handshake, FIN, RST a sequence state. NAT preto môže flow presnejšie sledovať a používať timeouty podľa lifecycle fázy.

UDP nemá handshake ani close. Translation point vytvorí pseudo-state po datagrame a odstráni ho po nečinnosti:

```text
UDP request
→ mapping vznikne
→ response použije reverse mapping
→ idle timeout
→ mapping zanikne
→ neskorá response môže byť zahodená
```

UDP keepalive udržiava NAT mapping, ale nedokazuje aplikačný health. Pri WebRTC, VoIP alebo hernom trafficu musí aplikácia počítať so zmenou externého portu, timeoutmi a potrebou STUN/TURN/ICE alebo explicitného mappingu.

## 10. Hairpin NAT: interný klient používa verejnú identitu

Interný klient `10.20.1.30` pristupuje k Atlas službe cez verejné meno, ktoré sa preloží na `203.0.113.5:443`:

```text
10.20.1.30
→ 203.0.113.5:443
→ DNAT
→ 10.20.2.10:8443
```

Backend môže mať priamu route k klientovi a odpovedať mimo gateway. Klient však otvoril connection voči verejnému endpointu, takže direct response z internej adresy poruší očakávaný tuple.

Hairpin model preto často pridá SNAT:

```text
client source
→ SNAT na gateway address
→ backend odpovie gateway
→ reverse SNAT a DNAT
→ klient vidí verejnú service identity
```

Alternatívou je split-horizon DNS, ktoré internému klientovi vráti interný endpoint. To odstráni hairpin translation, ale pridá dve DNS views a nový consistency lifecycle.

## 11. Linux hook model

Zjednodušený path forwardovaného packetu:

```text
ingress
→ PREROUTING / typický DNAT
→ routing decision podľa aktuálneho destination
→ FORWARD filtering
→ POSTROUTING / typický SNAT
→ egress
```

Lokálne generovaný packet používa `OUTPUT` a `POSTROUTING`. Lokálne doručovaný packet skončí po routingu v `INPUT`.

Pri diagnostike treba vedieť:

- či je traffic local alebo forwarded,
- v ktorom namespace vznikol,
- ktorý hook vidí original a ktorý translated fields,
- či DNAT zmenil ďalšie routing rozhodnutie,
- či container, cloud alebo eBPF dataplane vykonáva ďalšiu translation.

Príklad explicitného SNAT v nftables:

```nft
chain postrouting {
    type nat hook postrouting priority srcnat;
    oifname "wan0" ip saddr 10.20.0.0/16 snat to 203.0.113.5
}
```

Príklad DNAT:

```nft
chain prerouting {
    type nat hook prerouting priority dstnat;
    iifname "wan0" tcp dport 443 dnat to 10.20.2.10:8443
}
```

Konfigurácia iba opisuje translation. Samostatná filter policy musí flow povoliť.

## 12. Worked failure: nové platby timeoutujú, existujúce fungujú

Atlas zaznamená tento incident:

```text
08:00 traffic rastie
08:08 nové payment connections začnú timeoutovať
08:10 existujúce pooled connections stále fungujú
08:12 CPU a backend latency sú normálne
08:15 zníženie trafficu dočasne obnoví službu
```

### Hypotéza

Egress NAT vyčerpal source-port alebo conntrack kapacitu pre nové flows.

### Predikcie

- packet z Orders dorazí na inside interface,
- nový packet nemusí odísť s translated tuple,
- `nf_conntrack_count` sa blíži limitu alebo port-allocation errors rastú,
- existujúce entries stále prenášajú traffic,
- connection pooling znižuje failure rate.

### Overenie

```bash
ip route get 198.51.100.20
sudo tcpdump -ni inside0 host 10.20.1.15
sudo tcpdump -ni wan0 host 198.51.100.20
sudo conntrack -S
sysctl net.netfilter.nf_conntrack_count
sysctl net.netfilter.nf_conntrack_max
```

Rozhodovací tok:

```text
packet nepríde na gateway
→ route, L2 alebo upstream policy

packet príde, ale neodíde
→ forwarding, filter, NAT match alebo state allocation

packet odíde preložený, reply nepríde
→ remote path, remote policy alebo return routing

reply príde, ale klient ho nedostane
→ reverse mapping, filter alebo inside route
```

### Náprava

Atlas najprv zastaví retry amplification, obnoví connection pooling a pridá ďalšiu public source IP. Až následne upraví conntrack sizing podľa nameranej concurrency a timeout distribúcie.

Tým sa odlišuje mitigation od root-cause fixu: reštart gateway by state dočasne uvoľnil, ale zároveň by zrušil existujúce connections a neopravil connection churn.

## 13. Worked failure: publikovaný endpoint timeoutuje

Externý klient používa `203.0.113.5:443`, no reverse proxy request nevidí.

Postupuj cez štyri observation points:

1. **Original flow** — prichádza packet na public interface?
2. **Translated flow** — zmenila sa destination na `10.20.2.10:8443`?
3. **Conntrack mapping** — existuje original/reply tuple?
4. **Return flow** — odpovedá backend cez rovnaký state owner?

```bash
sudo nft list ruleset
sudo conntrack -L
ip route get 10.20.2.10
sudo tcpdump -ni wan0 'tcp port 443'
sudo tcpdump -ni inside0 'host 10.20.2.10 and tcp port 8443'
```

Výsledky majú mechanický význam:

- Packet na WAN, ale bez DNAT countera: rule alebo hook mismatch.
- DNAT nastane, ale packet nejde na inside interface: route alebo FORWARD policy.
- Packet dorazí backendu a príde RST: nesprávny listener/protocol.
- Backend odpovie priamo inou gateway: asymmetric return path.
- Transport funguje, ale TLS zlyhá: NAT vrstva je už preukázateľne funkčná.

## 14. HA: presun adresy nestačí

NAT gateway má per-flow state. Pri failover-e na druhý node nestačí presunúť verejnú IP.

Bez state synchronization:

- nový node nepozná reverse mappings,
- existujúce TCP flows sa prerušia,
- UDP pseudo-state zanikne,
- klientské retries vytvoria load burst.

Návrh musí explicitne určiť, či chráni iba nové connections alebo aj existujúce flows. Možnosti zahŕňajú active/passive state replication, deterministické active/active rozdelenie alebo vedomé akceptovanie connection lossu s bezpečným retry modelom vyššej vrstvy.

## 15. Referenčné rozšírenia

Nasledujúce varianty sú dôležité, ale nemenia základný lifecycle `original tuple → mapping → reverse translation`.

### MASQUERADE verzus explicitný SNAT

- `masquerade` používa aktuálnu adresu egress interface a hodí sa pre dynamickú adresu,
- explicitný `snat to` je predvídateľnejší pri stabilnej infraštruktúre.

### Cloud NAT

Managed služba stále potrebuje route z privátneho subnetu, state a port capacity. Má provider-specific limity pre flows, throughput, idle timeouty, public IP pool a failure domain.

### Container a Kubernetes dataplane

Publikovaný port alebo Service môže používať DNAT, proxy, IPVS alebo eBPF translation. Treba odlíšiť application listener, Pod IP, node port, Service virtual IP a external load balancer.

### NAT64 a DNS64

DNS64 môže syntetizovať IPv6 destination z IPv4 recordu a NAT64 preloží IPv6 flow na IPv4. Literal IPv4 adresy, DNSSEC assumptions alebo adresy v payload-e môžu tento model rozbiť.

### NAT traversal

STUN zisťuje externý endpoint, TURN reléuje traffic a ICE testuje dostupné candidates. Tieto mechanizmy riešia inbound reachability a variabilné NAT behavior, nie všeobecný routing.

## 16. Časté omyly

### „NAT je firewall“

NAT mení endpoint fields. Firewall vykonáva allow alebo deny rozhodnutie.

### „DNAT automaticky otvorí službu“

Stále treba route, FORWARD allow, listener, aplikačný protokol a return path.

### „Route znamená, že translation funguje“

Route neoveruje NAT rule match, state allocation ani reverse mapping.

### „Privátna adresa je bezpečnostná hranica“

Private endpoint môže byť dostupný cez VPN, peering, proxy, compromised host alebo chybný forwarding.

### „IPv6 potrebuje NAT kvôli bezpečnosti“

IPv6 inbound policy sa rieši firewallom a identitou. Preklad nie je náhrada access controlu.

### „Veľká conntrack table vyrieši každý capacity incident“

Limitom môže byť portový priestor, public IP pool, per-destination quota alebo retry-generated load.

## 17. Kontrolné otázky

1. Aký problém rieši SNAT v scenári Atlas Orders?
2. Čo obsahuje obojsmerný NAT mapping?
3. Prečo sa pravidlo rozhoduje najmä pri prvom packete?
4. Prečo po zmene pravidla treba testovať nový flow?
5. Ako PAT umožní zdieľať jednu verejnú IP?
6. Ako rozlíšiš conntrack exhaustion od source-port exhaustion?
7. Prečo DNAT vyžaduje správny backend return path?
8. Aký je rozdiel medzi socket state, conntrack state a aplikačným stavom?
9. Prečo UDP mapping expiruje bez FIN udalosti?
10. Prečo hairpin NAT často potrebuje aj SNAT?
11. Ktoré Linux hooks typicky vykonávajú DNAT a SNAT?
12. Aké štyri observation points potrebuje NAT troubleshooting?
13. Prečo presun virtuálnej IP nestačí na transparentný NAT failover?
14. Čo NAT64 mení a akú úlohu má DNS64?

## 18. Zhrnutie

NAT je stateful transformácia endpoint identity. Prvý packet vytvorí mapping medzi original a translated tuple, ďalšie packets ho používajú a return traffic musí prejsť bodom, ktorý vie vykonať reverse translation. NAT funguje iba spolu s routingom, firewallom, state capacity a správnym return pathom.

Praktická diagnostika preto nesleduje iba pravidlo. Porovná original packet, translated packet, conntrack mapping a return packet. Až z tejto štvorice možno určiť, či flow zlyhal pred prekladom, pri state allocation, po preklade alebo pri reverse ceste.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: DHCP](dhcp.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Firewally →](firewalls.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
