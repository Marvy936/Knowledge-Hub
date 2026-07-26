# Firewally

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [Routing a default gateway](routing-and-default-gateway.md), [Ports a sockets](ports-and-sockets.md), [NAT](nat.md)
- Súvisiace témy: security groups, network ACLs, proxies, load balancers, Kubernetes NetworkPolicy, WAF

## 1. Problém, ktorý firewall rieši

Atlas publikuje Orders API cez endpoint `203.0.113.5:443`. NAT môže packet preložiť na interný reverse proxy `10.20.2.10:8443`, ale samotný preklad neodpovedá na bezpečnostnú otázku:

```text
Smie tento konkrétny traffic pokračovať?
```

Firewall je policy enforcement point. Pozoruje packet, flow alebo aplikačný request, porovná ho s efektívnou politikou a vydá verdict, napríklad `accept`, `drop` alebo `reject`.

Pre jeden inbound request môže cesta vyzerať takto:

```text
Internet klient
→ cloud edge policy
→ subnet ACL
→ NAT/DNAT
→ host FORWARD policy
→ reverse-proxy listener
→ proxy/WAF policy
→ application authorization
```

Povolenie na jednej vrstve neznamená povolenie na ďalšej. Firewall zároveň neotvára socket, nevytvára route a neopravuje nefunkčnú aplikáciu.

## 2. Dominantný mentálny model

Každé firewall rozhodnutie možno analyzovať rovnakým lifecycle-om:

```text
packet alebo request
→ observation point a smer
→ fields a identity viditeľné v tomto bode
→ optional state lookup
→ rule selection a precedence
→ verdict
→ ďalší enforcement point alebo destination
```

Pri incidente treba zodpovedať šesť otázok:

1. Ktorý enforcement point packet skutočne videl?
2. V akom smere a hooku sa nachádzal?
3. Aké source/destination fields mal pred alebo po NAT-e?
4. Aký connection alebo aplikačný state bol priradený?
5. Ktoré pravidlo a poradie rozhodlo?
6. Aký verdict vznikol a kam packet pokračoval?

Neurčité tvrdenie „firewall je otvorený“ neodpovedá ani na jednu z nich.

## 3. Carried scenario: klient pristupuje k Atlas Orders

Klient `198.51.100.25` otvára TCP connection na verejný endpoint:

```text
198.51.100.25:51000 → 203.0.113.5:443
```

DNAT ho preloží na reverse proxy:

```text
198.51.100.25:51000 → 10.20.2.10:8443
```

Na Linux gateway môže flow prejsť:

```text
ingress wan0
→ PREROUTING a DNAT
→ route k 10.20.2.10
→ FORWARD firewall
→ egress inside0
```

Firewall vo FORWARD path-e môže vidieť už preloženú destination. Pravidlo napísané pre public IP v nesprávnom hooku preto nemusí matchovať.

Po doručení reverse proxy vznikne nový upstream flow. Ten môže mať inú source IP, port, TLS session a ďalší firewall path. Jeden používateľský request tak môže obsahovať viac samostatných policy decisions.

## 4. Observation point a smer

Linux rozlišuje tri hlavné packet paths:

```text
remote → local process
PREROUTING → routing → INPUT

local process → remote
OUTPUT → routing → POSTROUTING

remote → routed cez host → remote
PREROUTING → routing → FORWARD → POSTROUTING
```

Dôsledky:

- `INPUT` pravidlo neovplyvní packet routovaný do kontajnera cez `FORWARD`.
- Hostový firewall nemusí vidieť packet zahodený cloud security groupou.
- Packet v inom network namespace môže používať iný ruleset alebo dataplane.
- WAF nemôže rozhodovať pred úspešným TCP a zvyčajne TLS setupom.
- eBPF alebo virtual switch policy môže rozhodnúť mimo chainu, ktorý administrátor kontroluje cez tradičný nftables výpis.

Observation point musí byť pomenovaný konkrétne: cloud attachment, interface, namespace, hook, chain, proxy listener alebo aplikačný middleware.

## 5. Stateless a stateful rozhodovanie

### Stateless model

Stateless firewall hodnotí každý packet samostatne podľa aktuálnych fields:

```text
source/destination IP
+ protocol
+ source/destination port
+ interface
+ flags alebo ICMP type
→ verdict
```

Pre TCP request treba explicitne myslieť na oba smery:

```text
client ephemeral → server 443
server 443 → client ephemeral
```

Tento model nepotrebuje per-flow table, ale politika musí presne pokryť return traffic.

### Stateful model

Stateful firewall používa conntrack:

```text
prvý packet
→ NEW
→ explicitné allow pravidlo
→ obojsmerný state
→ ďalšie packets ESTABLISHED
```

Bežná politika:

```text
allow established,related
allow new TCP 443 from approved sources
drop ostatné new flows
```

Stateful model zjednodušuje return policy, ale pridáva state capacity a timeout lifecycle.

## 6. Conntrack nie je aplikačný stav

Rozlišuj:

```text
TCP socket state na endpointe
≠
conntrack state na firewalle
≠
TLS alebo HTTP state
≠
business authorization
```

`ct state established` znamená, že packet patrí k rozpoznanému flowu. Neznamená, že:

- TLS certifikát je platný,
- HTTP route existuje,
- používateľ je autorizovaný,
- backend dependency funguje,
- response je správna.

Conntrack entry môže navyše prežiť aplikačný close alebo naopak expirovať skôr než endpoint zistí, že middlebox state zmizol.

## 7. Verdict mení failure semantics

### Accept

Packet pokračuje do ďalšieho hooku alebo enforcement pointu. Nie je to dôkaz finálneho doručenia.

### Drop

Packet sa ticho zahodí:

```text
client SYN
→ firewall drop
→ žiadna odpoveď
→ retransmission
→ connect timeout
```

Drop predlžuje failure detection a môže vytvoriť retry load.

### Reject

Firewall vráti explicitnú chybu, napríklad TCP RST alebo ICMP unreachable. Klient zlyhá rýchlejšie.

### Log a counter

Logovanie alebo counter poskytujú evidence, ale samy nemusia byť terminating verdict. Rule môže packet zaznamenať a pokračovať ďalej.

Rozdiel medzi timeoutom a okamžitým `connection refused` preto nesie informáciu o mechanizme, nie iba o používateľskom texte chyby.

## 8. Rule selection a precedence

Efektívny výsledok závisí od poradia a control flow rulesetu.

Pri first-match modeli:

```text
1. drop TCP 443 from any
2. allow TCP 443 from 198.51.100.0/24
```

je druhé pravidlo nedosiahnuteľné.

Nftables navyše rozlišuje:

- table family,
- base chain hook,
- chain priority,
- base policy,
- jump, goto a return,
- sets a maps,
- rules vložené inými managermi.

Source configuration nie je automaticky efektívny ruleset. Docker, Kubernetes, firewalld, VPN agent alebo security produkt môžu pridať vlastné chains a priority.

## 9. Default deny ako prevádzkový kontrakt

Default deny znamená:

```text
neznámy flow
→ zakázaný

známy legitímny flow
→ explicitne povolený
```

Je to silný model iba vtedy, keď Atlas pozná svoje dependencies:

- inbound klientov a management sources,
- DNS, NTP a certificate endpoints,
- payment API a telemetry egress,
- IPv4 aj IPv6 flows,
- health checks,
- package a artifact repositories,
- recovery a out-of-band access.

Default deny bez inventory a observability vedie počas incidentu k širokým `allow any` výnimkám, ktoré zrušia pôvodný bezpečnostný cieľ.

## 10. Konkrétny nftables model pre Atlas

Základ hostového inbound rulesetu:

```nft
table inet atlas_filter {
    set admin_sources {
        type ipv4_addr
        flags interval
        elements = { 198.51.100.0/24 }
    }

    chain input {
        type filter hook input priority filter;
        policy drop;

        iifname "lo" accept
        ct state invalid drop
        ct state established,related accept

        ip protocol icmp accept
        ip6 nexthdr ipv6-icmp accept

        tcp dport 22 ip saddr @admin_sources counter accept
        counter drop
    }

    chain forward {
        type filter hook forward priority filter;
        policy drop;

        ct state invalid drop
        ct state established,related accept

        iifname "wan0" oifname "inside0" \
            ip daddr 10.20.2.10 tcp dport 8443 \
            ct state new counter accept

        counter drop
    }
}
```

Tento príklad ukazuje dve odlišné otázky:

- management SSH končí na samotnej gateway a používa `INPUT`,
- publikovaný Orders traffic je forwardovaný po DNAT-e a používa `FORWARD` s internou destination.

Produkčný ruleset musí mať explicitný owner, persistent deployment, rollback a test pre legitímne aj zakázané flows.

## 11. NAT a firewall sú oddelené rozhodnutia

Pre Atlas endpoint:

```text
DNAT match
→ destination sa zmení na 10.20.2.10:8443
→ FORWARD firewall môže allow alebo drop
```

Možné kombinácie:

| Translation | Firewall | Výsledok |
|---|---|---|
| nie | allow | packet pokračuje bez požadovaného prekladu alebo skončí inde |
| áno | drop | klient timeoutuje napriek správnemu DNAT-u |
| áno | reject | klient dostane explicitnú chybu |
| áno | allow | flow pokračuje, no backend môže stále zlyhať |

NAT vysvetľuje tuple. Firewall vysvetľuje verdict. Routing vysvetľuje next hop.

## 12. Worked failure: po default-deny rolloute fungujú iba staré connections

Atlas nasadí nový ruleset. Monitoring ukáže:

```text
existujúce HTTPS sessions pokračujú
→ nové client connections timeoutujú
→ reverse proxy a backend sú zdravé
→ rollback okamžite obnoví nové flows
```

### Hypotéza

Ruleset povoľuje `ESTABLISHED`, ale chýba alebo nematchuje pravidlo pre nový DNAT flow vo FORWARD chain.

### Predikcie

- existujúce conntrack entries pokračujú,
- nový SYN príde na WAN,
- DNAT counter môže rásť,
- allow counter vo FORWARD chain nerastie,
- drop counter rastie,
- backend nový SYN nevidí.

### Overenie

```bash
sudo nft list ruleset -a
sudo conntrack -L
sudo tcpdump -ni wan0 'tcp port 443'
sudo tcpdump -ni inside0 'host 10.20.2.10 and tcp port 8443'
```

Mechanický záver:

```text
SYN na wan0
+ žiadny SYN na inside0
+ rast drop countera vo FORWARD
→ firewall decision medzi DNAT a backend route
```

Oprava nie je „otvoriť port 443 všade“. Oprava je pridať úzke pravidlo pre translated destination, správny interface direction a `ct state new`, potom overiť novú connection.

## 13. Worked failure: hostový ruleset povoľuje, ale packet neprichádza

Atlas administrátor vidí hostové allow pravidlo, no reverse proxy nevidí žiadny traffic.

Postup:

1. Over DNS a destination endpoint klienta.
2. Zachyť packet na klientskom alebo upstream routeri.
3. Skontroluj subnet ACL.
4. Skontroluj cloud security group alebo virtual NIC policy.
5. Až potom interpretuj hostový nftables ruleset.

```text
route exists
→ network ACL allows
→ security group drops
→ host tcpdump nič nevidí
```

Absencia packetu na hoste nie je dôkaz hostového firewall dropu. Posúva root cause na skorší observation point.

## 14. Conntrack exhaustion

Stateful firewall môže prestať prijímať nové flows, hoci existujúce pokračujú.

Typický chain:

```text
retry storm alebo scan
→ rast NEW flows
→ conntrack table sa zaplní
→ nové entries nemožno vytvoriť
→ nové connections timeoutujú
→ klienti viac retryujú
→ pressure sa posilní
```

Evidence:

```bash
sudo conntrack -S
sysctl net.netfilter.nf_conntrack_count
sysctl net.netfilter.nf_conntrack_max
journalctl -k -b
```

Zvýšenie limitu je bezpečné iba po kontrole memory capacity a príčiny flow growth. Primárnym fixom môže byť rate limit, retry control, connection pooling alebo blokovanie útoku.

## 15. ICMP je súčasť funkčného IP stacku

Plošné blokovanie ICMP môže rozbiť:

- explicitné destination-unreachable errors,
- traceroute a TTL feedback,
- Path MTU Discovery,
- IPv6 Neighbor Discovery,
- Router Advertisements,
- Duplicate Address Detection.

Atlas môže mať stav, kde malé HTTPS requests fungujú, ale veľké responses timeoutujú, pretože firewall blokuje ICMP Packet Too Big.

Správny prístup je povoliť potrebné typy, blokovať nelegitímne kombinácie a rate-limitovať abuse-sensitive traffic — nie zahodiť celý protokol.

## 16. Safe rollout firewall policy

Zmena remote firewallu môže odstrihnúť správcu aj produkčný traffic. Bezpečný lifecycle:

```text
inventory a hypothesis
→ export effective state
→ recovery path
→ syntaktická validácia
→ atomický apply
→ nový-flow test
→ negatívny test
→ persistence test
→ monitoring a rollback
```

Praktický postup:

1. Potvrď out-of-band console.
2. Zachovaj aktuálny ruleset.
3. Definuj management source a return path.
4. Pridaj explicitný management allow pred default deny.
5. Použi atomické načítanie.
6. Nezatváraj pôvodnú session.
7. Otvor novú paralelnú session.
8. Vytvor nový produkčný flow.
9. Otestuj aj traffic, ktorý má zostať zakázaný.
10. Over reload alebo reboot behavior.

Test existujúcej connection nestačí, pretože ju môže držať starý conntrack state.

## 17. Policy lifecycle

Firewall rule je prevádzkový kontrakt a má mať:

- ownera,
- konkrétny účel,
- source a destination scope,
- protocol a smer,
- test,
- deployment history,
- counter alebo log identity,
- expiration alebo revalidation,
- rollback,
- odstránenie po zániku dependency.

Dočasné pravidlo bez expiration sa stáva trvalým attack surface. Comment má vysvetliť dôvod, nie iba zopakovať port.

## 18. Referenčné enforcement vrstvy

Tieto platformy používajú rovnaký policy-decision lifecycle, ale líšia sa observation pointom a state modelom.

### Cloud security group

Typicky je stateful a viazaná na virtual NIC alebo workload. Packet zahodený tu sa nemusí dostať do guest OS.

### Network ACL

Často je subnet-level a stateless. Musí explicitne povoľovať forward aj return smer vrátane ephemeral portov.

### firewalld

Pracuje so zones a rozlišuje runtime a permanent state. Pravidlo v nesprávnej zone alebo iba v permanent konfigurácii nemusí byť aktívne.

### Kubernetes NetworkPolicy

Desired object vynucuje CNI plugin. Bez podporovaného dataplane môže policy existovať bez efektu. Treba skontrolovať selected Pods, ingress/egress smer, DNS egress a preklad cez Services.

### L7 firewall a WAF

Rozhoduje podľa Host, path, method, headers, body alebo identity. Začína až po nižšom network a často TLS path-e. Nemôže nahradiť L3/L4 segmentation ani aplikačnú authorization logiku.

## 19. Observability

Dobrý firewall evidence model kombinuje:

- rule counters,
- explicitné rule identifiers,
- rate-limited deny logs,
- flow logs,
- conntrack metrics,
- cielený packet capture,
- config/deployment timeline.

Log má obsahovať čas, source, destination, protocol, direction, interface alebo zone, state, verdict a rule identity.

Absencia logu neznamená absenciu firewall decisionu. Rule nemusí logovať, logging môže byť rate-limited alebo packet zlyhal na inom enforcement pointe.

## 20. Diagnostický postup pre jeden flow

Klient sa nevie pripojiť na Atlas Orders:

```text
1. potvrď presný endpoint a address family
2. potvrď listener alebo frontend target
3. rekonštruuj forward a return route
4. zachyť packet na každom relevantnom boundary
5. nájdi posledný observation point, kde existuje
6. over effective policy a counter
7. odlíš drop, reject a no-listener RST
8. skontroluj conntrack state a capacity
9. po zmene vytvor nový flow
10. pokračuj TLS/proxy/application diagnostikou
```

Interpretácia:

```text
packet nedorazí na host
→ upstream route, ACL, SG alebo virtual dataplane

packet dorazí, allow counter nerastie
→ nesprávny chain, family, translated fields alebo precedence

packet dorazí backendu, príde RST
→ listener alebo explicitný reject

TCP handshake funguje, HTTP zlyhá
→ firewall L3/L4 path je preukázateľne funkčný
```

## 21. Časté omyly

### „Firewall otvorí port“

Firewall povoľuje packet. Socket musí byť bindnutý a aplikácia musí odpovedať.

### „Allow na jednom firewalle znamená end-to-end allow“

Ďalšia ACL, SG, host policy, CNI, proxy alebo aplikácia môže request odmietnuť.

### „NAT je firewall“

Translation mení tuple; firewall vydáva verdict.

### „Stateful policy nepotrebuje outbound pravidlá“

Nový outbound flow musí byť najprv povolený. Až jeho return traffic môže použiť established state.

### „ICMP treba celý zablokovať“

Tým sa môžu rozbiť PMTUD a základné IPv6 mechanizmy.

### „Hostový tcpdump vidí každý firewall drop“

Packet môže zaniknúť pred hostom alebo v inom namespace a dataplane.

### „Default deny možno zapnúť a výnimky doplniť neskôr“

Bez inventory, recovery a new-flow testu ide o nebezpečný experiment.

## 22. Kontrolné otázky

1. Čo firewall rozhoduje a čo nerobí?
2. Ktorých šesť údajov potrebuješ na vysvetlenie verdictu?
3. Aký je rozdiel medzi INPUT, OUTPUT a FORWARD pathom?
4. Prečo môže firewall po DNAT-e vidieť internú destination?
5. Aký je rozdiel medzi stateless a stateful policy?
6. Prečo `ct state established` nedokazuje zdravú aplikáciu?
7. Ako sa líši drop od rejectu z pohľadu klienta a retry loadu?
8. Prečo rule order mení výsledok?
9. Čo musí default-deny model poznať pred rolloutom?
10. Prečo existujúce connections môžu fungovať po chybnom nasadení?
11. Ako rozpoznáš conntrack exhaustion?
12. Prečo hostový allow rule nevylučuje cloud firewall drop?
13. Prečo treba povoliť vybrané ICMP a ICMPv6 typy?
14. Ako bezpečne overíš firewall zmenu na remote hoste?
15. Aký je rozdiel medzi security groupou, network ACL a NetworkPolicy?
16. Kedy sa troubleshooting presúva z firewallu na TLS alebo aplikáciu?

## 23. Zhrnutie

Firewall je policy decision v konkrétnom observation pointe. Výsledok závisí od direction, fields viditeľných pred alebo po translation, state, rule precedence a verdictu. Povolenie packetu neznamená existenciu listenera ani úspešnú aplikačnú operáciu.

Praktický troubleshooting sleduje jeden flow cez všetky enforcement points, hľadá posledné miesto, kde packet existuje, a spája packet capture s effective rulesetom, counterom a conntrack state. Oprava mení iba pravidlo alebo boundary, ktoré bolo preukázateľne príčinou — nie celý systém širokým `allow any` pravidlom.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: NAT](nat.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Proxy a reverse proxy →](proxy-and-reverse-proxy.md)
<!-- KNOWLEDGE-NAVIGATION:END -->