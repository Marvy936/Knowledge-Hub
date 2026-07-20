# Firewalls

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [Routing a default gateway](routing-and-default-gateway.md), [Ports a sockets](ports-and-sockets.md), [NAT](nat.md)
- Súvisiace témy: security groups, network ACLs, proxies, load balancers, Kubernetes NetworkPolicy

## 1. Definícia

Firewall je policy enforcement point, ktorý povoľuje, zamieta alebo inak spracúva network traffic podľa pravidiel nad packet metadata, connection state, identity alebo aplikačným kontextom.

Firewall nie je jeden konkrétny produkt ani jedna vrstva. Môže existovať na hoste, routeri, cloud subnet boundary, load balanceri, hypervisore, kontajnerovej platforme alebo priamo v aplikácii.

## 2. Základný mentálny model

```text
packet alebo flow
  ↓
observation point
  ↓
policy match v definovanom poradí
  ↓
allow / drop / reject / log / rate-limit / redirect
```

Výsledok závisí od toho, či packet vôbec prejde cez konkrétny firewall hook alebo zariadenie.

## 3. Stateless vs. stateful firewall

### Stateless

Každý packet sa hodnotí samostatne podľa header fields.

Výhody:

- jednoduchší model,
- nižšie state nároky,
- vhodné pre niektoré vysokovýkonné alebo hraničné filtre.

Nevýhody:

- policy musí explicitne riešiť oba smery,
- slabší kontext o lifecycle spojenia.

### Stateful

Firewall používa connection tracking a rozlišuje stavy flowu.

Typické kategórie:

- `NEW`,
- `ESTABLISHED`,
- `RELATED`,
- `INVALID`.

Stateful rule môže povoliť odpovede na outbound spojenie bez širokého inbound pravidla.

## 4. Allow, drop a reject

### Allow

Packet pokračuje ďalším spracovaním alebo je doručený.

### Drop

Packet sa zahodí bez explicitnej odpovede. Klient typicky čaká na timeout.

### Reject

Firewall odošle chybu, napríklad TCP RST alebo ICMP unreachable. Klient dostane rýchlejšiu negatívnu odpoveď.

Trade-off:

- drop znižuje informáciu pre scanner, ale predlžuje diagnostiku,
- reject zlepšuje fail-fast správanie, ale explicitne potvrdí existenciu enforcement pointu.

## 5. Default policy

Dva základné modely:

```text
default allow + explicit deny
```

alebo:

```text
default deny + explicit allow
```

Pre security boundary je preferovaný least-privilege model `default deny`, ale vyžaduje inventár legitímnych flows a bezpečný rollout.

## 6. Rule matching a poradie

Firewall engine môže používať first-match, priority alebo chain-based model.

Pri first-match policy:

```text
1. allow trusted subnet to 443
2. deny all to 443
3. allow all established
```

poradie zásadne mení výsledok.

Pravidlá musia byť:

- jednoznačné,
- minimálne široké,
- zdokumentované ownerom a účelom,
- časovo obmedzené pri výnimkách,
- testované z relevantného source segmentu.

## 7. Packet direction a hooks

Na Linux hoste treba rozlíšiť:

- `INPUT`: traffic určený lokálnemu hostu,
- `OUTPUT`: lokálne generovaný traffic,
- `FORWARD`: traffic routovaný cez host,
- NAT hooks ako `PREROUTING` a `POSTROUTING`.

Povolenie INPUT neznamená povolenie FORWARD. To je častá chyba pri routeri, VPN gateway alebo container hoste.

## 8. Linux netfilter a nftables

Netfilter je kernel framework. Moderný userspace interface je nftables.

Inventár:

```bash
sudo nft list ruleset
sudo nft list tables
sudo nft list ruleset -a
```

Konceptuálny ruleset:

```nft
table inet filter {
    chain input {
        type filter hook input priority filter;
        policy drop;

        iifname "lo" accept
        ct state established,related accept
        tcp dport 22 ip saddr 198.51.100.0/24 accept
        tcp dport 443 accept
    }
}
```

Produkčný ruleset musí riešiť IPv4 aj IPv6, management access, ICMP, loopback, logging a recovery path.

## 9. iptables compatibility

Príkaz `iptables` môže používať legacy backend alebo nft backend.

Kontrola závisí od distribúcie, napríklad:

```bash
iptables --version
update-alternatives --display iptables
```

Nemiešaj nevedomky viac manažment vrstiev, napríklad raw nftables, firewalld a ručné iptables rules. Jedna vrstva môže pravidlá prepísať alebo vložiť do inej priority.

## 10. firewalld a zones

Firewalld poskytuje vyššiu abstrakciu nad netfilterom.

Základné pozorovanie:

```bash
firewall-cmd --get-active-zones
firewall-cmd --list-all
firewall-cmd --list-all-zones
```

Zone reprezentuje trust profil priradený interface alebo source. Runtime a permanent configuration sú odlišné:

```bash
firewall-cmd --add-service=https
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

Runtime zmena bez permanent zápisu neprežije reload; permanent zmena bez reloadu nemusí byť okamžite aktívna.

## 11. Connection tracking

Stateful firewall používa conntrack table.

```bash
sudo conntrack -L
sysctl net.netfilter.nf_conntrack_count
sysctl net.netfilter.nf_conntrack_max
```

Vyčerpanie table môže zahadzovať nové flows. Príčinou môže byť traffic burst, scan, retry storm alebo nevhodné timeouty.

`ESTABLISHED` vo firewall kontexte nemusí presne znamenať TCP state `ESTAB`; conntrack používa vlastný model validného obojsmerného flowu.

## 12. ICMP a IPv6

Bezhlavé blokovanie ICMP môže poškodiť:

- Path MTU Discovery,
- error reporting,
- troubleshooting,
- IPv6 Neighbor Discovery a Router Advertisements.

IPv6 je od ICMPv6 funkčne závislejší než IPv4 od ICMP echo.

Bezpečná policy nemá znamenať `deny all ICMP`. Treba povoliť potrebné typy a rate-limitovať abuse-sensitive traffic.

## 13. Cloud security groups

Security group je typicky stateful policy priradená virtual NIC, instance alebo workloadu.

Vlastnosti sa líšia podľa cloudu, ale často:

- pravidlá sú allow-only,
- implicitný deny platí pre nezhodný traffic,
- return traffic je povolený stavovo,
- policy sa vyhodnocuje na virtualizovanej network vrstve.

Security group nie je host firewall. Obe vrstvy môžu platiť súčasne.

## 14. Network ACLs

Cloud network ACL býva subnet-level a často stateless.

To znamená potrebu pravidiel pre oba smery vrátane ephemeral ports.

Pri troubleshootingu treba odlíšiť:

```text
route table
→ network ACL
→ security group
→ host firewall
→ process bind/listener
```

Každá vrstva môže traffic zastaviť.

## 15. Distributed firewalling

V moderných platformách môže policy platiť pri každom workload interface namiesto jedného centrálneho boxu.

Príklady:

- hypervisor virtual switch,
- Kubernetes CNI policy,
- service mesh L7 authorization,
- cloud security groups.

Výhody:

- policy bližšie k workloadu,
- menší lateral movement,
- škálovanie bez central choke pointu.

Riziká:

- rozptýlená observability,
- viac policy engines,
- nejasné poradie enforcementu,
- rozdiel medzi deklarovanou a efektívnou policy.

## 16. L3/L4 vs. L7 firewall

### L3/L4

Rozhoduje podľa:

- source/destination address,
- protocol,
- port,
- connection state.

### L7

Rozumie aplikačnému protokolu, napríklad HTTP host, path, method alebo identity tokenu.

L7 firewall alebo WAF môže blokovať request aj po úspešnom TCP a TLS spojení.

Preto „port 443 je povolený“ neznamená, že konkrétny HTTP request bude prijatý.

## 17. Egress filtering

Outbound policy je dôležitá pre:

- obmedzenie data exfiltration,
- kontrolu command-and-control trafficu,
- povolenie iba potrebných dependencies,
- vynútenie proxy alebo inspection path,
- stabilnejší inventory komunikácie.

Egress default deny je náročný, pretože aplikácie používajú dynamické SaaS endpoints, DNS, package repositories a certificate services. Vyžaduje ownership a observability.

## 18. Logging

Logovanie každého packetu môže zahltiť CPU, storage a SIEM.

Dobrý model:

- logovať denied flows s rate limitom,
- agregovať counters,
- evidovať rule identifier,
- korelovať source, destination, interface a timestamp,
- chrániť logy pred citlivými payloadmi,
- používať flow logs tam, kde packet logs nie sú vhodné.

Nftables counters:

```nft
tcp dport 443 counter accept
```

Handle a counters pomáhajú overiť, či sa packet zhoduje s očakávaným pravidlom.

## 19. Bezpečný rollout

Pri zmene remote host firewallu hrozí strata administratívneho prístupu.

Bezpečný postup:

1. potvrdiť out-of-band alebo console recovery,
2. identifikovať management source addresses,
3. pridať allow pravidlo pred default deny,
4. použiť časovaný rollback alebo testovaciu session,
5. overiť novú paralelnú session,
6. až potom odstrániť staré pravidlá,
7. uložiť persistent configuration.

## 20. Diagnostický postup

Klient sa nevie pripojiť na server:

```bash
ss -lntp
ip route get <client-ip>
sudo nft list ruleset -a
sudo conntrack -L
sudo tcpdump -ni any host <client-ip> and port <port>
```

Postup:

1. klient používa správnu destination IP a port,
2. packet opustí klienta,
3. route a upstream ACL ho doručia,
4. packet príde na server interface,
5. zhoduje sa s firewall chain a rule,
6. proces počúva na správnej adrese,
7. odpoveď má povolený return path,
8. L7 policy neblokuje request po transportnom spojení.

## 21. Typické symptómy

### Timeout

Často drop policy, chýbajúca route alebo return path.

### Okamžité `connection refused`

Nič nepočúva alebo firewall posiela reject/RST.

### Funguje z jedného subnetu, nie z druhého

Source-based rule, route, ACL alebo asymmetric path.

### Existujúce spojenia fungujú, nové nie

Conntrack exhaustion, listen queue, rate limit alebo nová policy aplikovaná iba na nové flows.

### IPv4 funguje, IPv6 nie

Chýbajúce IPv6 rules, ICMPv6 blokovanie alebo listener iba na IPv4.

## 22. Časté omyly

### „Firewall otvorí port“

Firewall iba povoľuje traffic. Port musí byť bindnutý procesom.

### „NAT je firewall“

Nie. Translation a policy enforcement sú odlišné funkcie.

### „Stateful firewall nepotrebuje outbound pravidlá“

Záleží od platformy a smeru iniciácie. Nové outbound flows stále potrebujú policy.

### „ICMP treba vždy blokovať“

Nie. Niektoré ICMP/ICMPv6 správy sú nevyhnutné pre správne fungovanie siete.

### „Keď je security group správna, sieť musí fungovať“

Nie. Stále existujú routes, ACLs, host firewall, bind address a aplikácia.

## 23. Kontrolné otázky

1. Aký je rozdiel medzi stateless a stateful firewallom?
2. Aký je rozdiel medzi drop a reject?
3. Prečo je rule order dôležitý?
4. Aký je rozdiel medzi INPUT a FORWARD chain?
5. Prečo môže conntrack exhaustion blokovať nové spojenia?
6. Prečo nie je bezpečné blokovať všetok ICMPv6?
7. Ako sa líši security group od network ACL?
8. Aký je rozdiel medzi L4 firewallom a WAF?
9. Ako bezpečne nasadiť default-deny policy na remote server?
10. Prečo firewall allow nie je dôkaz aplikačného health?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: NAT](nat.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
