# Firewally

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [Routing a default gateway](routing-and-default-gateway.md), [Ports a sockets](ports-and-sockets.md), [NAT](nat.md)
- Súvisiace témy: security groups, network ACLs, proxies, load balancers, Kubernetes NetworkPolicy, WAF

## 1. Definícia

Firewall je policy enforcement point, ktorý nad packetom, flowom alebo aplikačným requestom vykoná rozhodnutie podľa definovanej politiky.

Verdict môže byť napríklad:

- accept — traffic smie pokračovať,
- drop — traffic sa ticho zahodí,
- reject — traffic sa odmietne explicitnou chybou,
- log — udalosť sa zaznamená,
- rate-limit — traffic sa obmedzí,
- mark — packet dostane metadata pre ďalšie rozhodovanie,
- redirect — traffic sa odošle na iný lokálny alebo vzdialený endpoint.

Firewall nie je jeden konkrétny produkt ani jedna sieťová vrstva. Enforcement môže existovať:

- v host kernel-i,
- na routeri alebo appliance,
- vo virtual switchi alebo hypervisore,
- v cloud security group alebo network ACL,
- v container dataplane,
- v Kubernetes CNI,
- v service meshi,
- v reverse proxy alebo WAF,
- priamo v aplikácii.

Preto otázka „je firewall otvorený?“ je nepresná. Treba určiť:

```text
ktorý enforcement point
+ ktorý smer
+ ktoré fields
+ ktorý state
+ ktoré poradie policy
+ ktorý výsledný verdict
```

## 2. Policy-decision lifecycle

Zjednodušený model:

```text
packet alebo request
    ↓
observation point
    ↓
normalizácia a state lookup
    ↓
rule selection v definovanom poradí
    ↓
match alebo no match
    ↓
verdict
    ↓
ďalší enforcement point alebo destination
```

Každá vrstva odpovedá na inú otázku:

- routing — kam packet smeruje,
- NAT — aké adresy alebo porty packet používa,
- firewall — či packet smie pokračovať,
- proxy — či sa vytvorí nové upstream spojenie a kam,
- application authorization — či konkrétna operácia smie prebehnúť.

Povolenie na jednej vrstve nie je dôkazom povolenia na ďalšej.

## 3. Observation point a direction

Firewall vidí iba traffic, ktorý cez neho skutočne prechádza.

Na Linux hoste sú dôležité hlavné pathy:

```text
remote → local process
PREROUTING → routing → INPUT

local process → remote
OUTPUT → routing → POSTROUTING

remote → routed through host → remote
PREROUTING → routing → FORWARD → POSTROUTING
```

Dôsledky:

- INPUT rule neovplyvní forwardovaný container traffic, ak packet ide cez FORWARD,
- OUTPUT rule neovplyvní packet, ktorý vytvoril iný namespace alebo eBPF dataplane mimo očakávaného hooku,
- host firewall nemusí vidieť traffic medzi dvoma workloads v rovnakom virtual switchi,
- cloud firewall môže packet zahodiť skôr, než sa dostane na host,
- WAF začne rozhodovať až po úspešnom TCP a často TLS spojení.

Pri diagnostike musí byť observation point pomenovaný fyzicky aj logicky: interface, namespace, hook, chain, cloud attachment alebo proxy listener.

## 4. Stateless firewall

Stateless firewall hodnotí každý packet samostatne podľa aktuálnych header fields a lokálnej policy.

Typické match fields:

- source a destination IP,
- transportný protokol,
- source a destination port,
- interface,
- TCP flags,
- ICMP type/code,
- DSCP alebo mark,
- fragment metadata.

Výhody:

- nepotrebuje per-flow state,
- správanie je jednoduchšie pri veľkom objeme trafficu,
- oba smery sú explicitne viditeľné v policy,
- failure jedného state table neblokuje všetky nové flows.

Nevýhody:

- return traffic treba povoliť samostatne,
- ephemeral ports komplikujú policy,
- packet bez širšieho kontextu môže vyzerať legitímne,
- TCP flags samy neposkytujú spoľahlivý aplikačný lifecycle.

Stateless filter musí myslieť na oba smery:

```text
client ephemeral port → server 443
server 443 → client ephemeral port
```

## 5. Stateful firewall

Stateful firewall používa connection tracking. Prvý packet vytvorí alebo začne state entry; ďalšie packets sa vyhodnocujú aj podľa vzťahu k existujúcemu flowu.

Bežné conntrack kategórie:

- `NEW` — nový alebo ešte nepotvrdený flow,
- `ESTABLISHED` — packet patrí k rozpoznanému obojsmernému flowu,
- `RELATED` — nový flow súvisí s existujúcim podľa protokolu alebo helpera,
- `INVALID` — packet nemožno korektne zaradiť.

Typická inbound policy:

```text
allow established,related
allow new TCP 443 from required sources
drop everything else
```

Stateful firewall umožní odpoveď na povolený outbound flow bez širokého všeobecného inbound pravidla. Stále však platí, že nový outbound flow musí prejsť outbound alebo forward policy.

## 6. Conntrack nie je aplikačný health

Conntrack state neznamená, že aplikácia je zdravá.

```text
ct state established
```

môže znamenať iba to, že kernel videl obojsmerný transportný flow. Nehovorí, že:

- TLS handshake uspel,
- HTTP request bol autorizovaný,
- databáza odpovedala,
- application worker nie je zaseknutý,
- response obsahuje správne dáta.

Zároveň conntrack state nie je totožný s TCP socket state v endpointe. Middlebox môže flow stále považovať za platný, hoci aplikácia už socket zavrela, alebo mapping môže expirovať skôr než endpoint zistí failure.

## 7. Conntrack capacity a failure mode

Stateful firewall potrebuje pamäť a čas na každý flow.

Pozorovanie:

```bash
sudo conntrack -L
sudo conntrack -S
sysctl net.netfilter.nf_conntrack_count
sysctl net.netfilter.nf_conntrack_max
journalctl -k -b
```

Pri vyčerpaní state table typicky:

- existujúce flows pokračujú,
- nové flows timeoutujú alebo sa zahadzujú,
- listener a route vyzerajú zdravo,
- problém rastie s concurrency alebo scanom,
- kernel môže logovať table full drops.

Príčiny:

- retry storm,
- veľa krátkych connections,
- UDP pseudo-state s dlhým timeoutom,
- attack alebo scan,
- connection leak,
- neprimeraný limit,
- zlá state distribúcia v HA modeli.

Zvýšenie limitu bez odstránenia retry stormu iba oddiali ďalší incident.

## 8. Allow, drop a reject

### Accept

Packet pokračuje do ďalšieho hooku, enforcement pointu alebo destination. Accept v jednej chain nemusí znamenať konečné doručenie, ak nasleduje ďalšia policy vrstva.

### Drop

Packet sa zahodí bez explicitnej odpovede. Klient typicky čaká do timeoutu a retransmituje.

Výhoda je menšie množstvo informácie pre scanner. Nevýhoda je dlhšia failure detection, väčší retry load a zložitejšia diagnostika.

### Reject

Firewall odošle aktívnu chybu, napríklad:

- TCP RST,
- ICMP destination unreachable,
- ICMP administratively prohibited.

Reject poskytne fail-fast správanie. Nie je automaticky menej bezpečný; rozhodnutie závisí od threat modelu a prevádzkovej potreby.

### Log

Logovanie nie je verdict, pokiaľ rule následne explicitne neprijme alebo nezahodí packet. Log rule môže iba zaznamenať a pokračovať v chain.

## 9. Default policy

Dva základné modely:

```text
default allow
+ explicit deny
```

alebo:

```text
default deny
+ explicit allow
```

Default deny je vhodný pre security boundary, pretože neznámy flow je zakázaný. Vyžaduje však:

- inventár legitímnych flows,
- ownership každej výnimky,
- správne return traffic pravidlá,
- IPv4 aj IPv6 policy,
- DNS, NTP, package repositories a certificate endpoints,
- management recovery path,
- bezpečný rollout a rollback.

Default deny bez observability vedie k náhodnému povoľovaniu širokých rozsahov pri každom incidente.

## 10. Rule ordering a precedence

Firewall engine môže používať:

- first-match semantics,
- priority-based chains,
- kombináciu jumpov a returnov,
- explicitný terminating alebo non-terminating verdict,
- platformovú agregáciu pravidiel.

Pri first-match modeli:

```text
1. allow 198.51.100.0/24 → TCP 443
2. drop all → TCP 443
3. allow established
```

je tretie pravidlo pre niektoré packets nedosiahnuteľné. Rovnaké pravidlá v inom poradí môžu dať iný výsledok.

Pri nftables treba chápať aj:

- table family,
- chain hook,
- chain priority,
- base chain policy,
- jump/goto semantics,
- sets a maps,
- pravidlá vložené iným managerom.

Jedna textová konfigurácia nemusí byť jediným zdrojom efektívnej policy.

## 11. Match scope

Dobré pravidlo explicitne určuje relevantný scope:

```text
source identity alebo prefix
+ destination identity alebo prefix
+ protocol
+ destination port
+ direction
+ interface alebo zone
+ connection state
+ časová alebo prevádzková podmienka
```

Príliš široké pravidlá:

```text
allow any any
allow 0.0.0.0/0 to all ports
allow whole corporate network to management plane
```

zväčšujú blast radius a skrývajú skutočné dependencies.

Príliš úzke pravidlá bez lifecycle managementu zasa zlyhávajú pri zmene adries, scale-out-e alebo failover-e. Policy preto potrebuje stabilnú identity vrstvu alebo automatizované generovanie z inventory.

## 12. nftables model

Netfilter je kernel framework; nftables je moderný userspace model na tvorbu pravidiel.

Inventár:

```bash
sudo nft list ruleset
sudo nft list ruleset -a
sudo nft list tables
```

Príklad základnej `inet` table:

```nft
table inet filter {
    set admin_sources {
        type ipv4_addr
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
        tcp dport 443 counter accept

        counter drop
    }
}
```

Produkčný ruleset musí riešiť:

- IPv4 aj IPv6,
- loopback,
- management access,
- potrebné ICMP/ICMPv6,
- fragmenty,
- invalid state,
- rate limiting a logging,
- persistent load,
- rollback,
- ownership iného firewall managera.

## 13. Sets, maps a dynamická policy

Nftables sets umožňujú spravovať veľa adries alebo portov efektívnejšie než opakované rules.

```nft
set trusted_backends {
    type ipv4_addr
    flags interval
    elements = { 10.20.0.0/16, 10.30.0.0/16 }
}
```

Maps môžu priamo mapovať key na verdict alebo value. Dynamická aktualizácia setu je často bezpečnejšia než prepis celého rulesetu.

Riziká:

- stale inventory,
- neatomická externá automatizácia,
- neočakávaná expirácia dynamického prvku,
- rozdiel medzi desired a effective state,
- chýbajúci audit pôvodu zmeny.

## 14. iptables compatibility a viac managerov

Príkaz `iptables` môže používať legacy backend alebo nft backend.

```bash
iptables --version
update-alternatives --display iptables
```

Na jednom hoste môžu pravidlá spravovať:

- raw nftables konfigurácia,
- firewalld,
- Docker alebo container runtime,
- Kubernetes komponent,
- VPN software,
- cloud agent,
- bezpečnostný produkt.

Ak viac managerov mení rovnaký dataplane bez jasného ownershipu:

- pravidlá sa môžu prepísať,
- priority sa môžu meniť,
- reload môže odstrániť runtime rules,
- diagnostika jedného config súboru nebude autoritatívna.

Efektívny ruleset je dôležitejší než predpokladaný zdroj konfigurácie.

## 15. firewalld a zones

Firewalld poskytuje abstrakciu zones, services a runtime/permanent konfigurácie.

Zone reprezentuje trust profil priradený interface alebo source.

```bash
firewall-cmd --get-active-zones
firewall-cmd --list-all
firewall-cmd --list-all-zones
```

Rozdiel stavov:

```text
runtime configuration
= aktívna teraz

permanent configuration
= načíta sa pri reload/reštarte
```

Príklad:

```bash
firewall-cmd --add-service=https
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

Runtime zmena bez permanent zápisu sa stratí. Permanent zmena bez reloadu nemusí byť aktívna.

Pri zones treba overiť, či interface alebo source patrí do očakávanej zone. Pravidlo v správnej zone nepomôže packetu spracovanému inou zone.

## 16. ICMP a ICMPv6

Plošné blokovanie ICMP nie je bezpečná univerzálna politika.

ICMP poskytuje:

- destination unreachable,
- time exceeded,
- fragmentation needed alebo packet too big,
- parameter problem,
- redirect v špecifických scenároch,
- diagnostický echo traffic.

ICMPv6 navyše zabezpečuje základné IPv6 funkcie:

- Neighbor Solicitation a Advertisement,
- Router Solicitation a Advertisement,
- Duplicate Address Detection,
- Path MTU Discovery,
- multicast listener signaling.

Blokovanie potrebných typov môže spôsobiť:

- MTU black holes,
- nefunkčný IPv6 neighbor discovery,
- chýbajúcu default route,
- pomalé timeouty namiesto explicitných chýb.

Správny model je povoliť potrebné typy, blokovať nelegitímne a rate-limitovať abuse-sensitive traffic.

## 17. Fragmenty a firewall policy

Nie každý fragment obsahuje transportný header. Neskorší IPv4 fragment nemusí mať TCP/UDP porty, podľa ktorých pravidlo bežne matchuje.

Stateful reassembly alebo fragment tracking môže pomôcť, ale pridáva resource pressure a attack surface.

Pri IPv6 môžu extension headers a fragment header komplikovať parsing a policy. Plošné blokovanie všetkých extension headers môže rozbiť legitímny traffic; plošné povolenie bez limitov môže byť rizikové.

Firewall musí mať explicitnú fragment policy, nie náhodné správanie odvodené z rule orderu.

## 18. Cloud security groups

Security group je typicky stateful policy priradená virtual NIC, instance alebo workload identity.

Bežný model:

- allow rules,
- implicit deny pre nezhodný traffic,
- stateful return traffic,
- policy vyhodnotená vo virtualizovanej network vrstve.

Security group nie je host firewall. Obe vrstvy môžu platiť súčasne.

Príklad failure path:

```text
internet route exists
→ subnet ACL allows
→ security group denies
→ packet nikdy nepríde na host
```

Hostový `tcpdump` preto nemusí vidieť packet, ktorý cloud firewall zahodil skôr.

## 19. Network ACLs

Cloud network ACL býva subnet-level a často stateless.

Stateless model vyžaduje pravidlá pre oba smery vrátane ephemeral portov:

```text
client ephemeral → server 443
server 443 → client ephemeral
```

ACL môže mať numbered rule order, explicitné deny a platformové limity. Pri troubleshooting-u treba poznať konkrétnu cloud implementáciu, nie všeobecný predpoklad.

Vrstvy:

```text
route table
→ network ACL
→ security group
→ host firewall
→ namespace/CNI policy
→ listener
→ L7 authorization
```

## 20. Distributed firewalling

Moderné platformy aplikujú policy priamo pri workload interface.

Príklady:

- hypervisor vNIC policy,
- Kubernetes CNI NetworkPolicy,
- eBPF dataplane,
- service mesh authorization,
- cloud workload identity firewall.

Výhody:

- menší lateral movement,
- enforcement blízko workloadu,
- škálovanie bez jedného centrálneho boxu,
- policy podľa identity workloadu.

Riziká:

- viac policy engines,
- rozptýlené logy,
- nejasný precedence model,
- rozdiel medzi deklarovanou a efektívnou policy,
- policy lag pri rýchlom scale-out-e,
- odlišné IPv4/IPv6 pokrytie.

Pri incidente treba identifikovať všetky enforcement points, nie iba „hlavný firewall“.

## 21. Kubernetes NetworkPolicy

Kubernetes NetworkPolicy deklaruje povolené ingress a egress flows pre vybrané Pods. Reálny enforcement poskytuje CNI plugin.

Dôležité dôsledky:

- bez podporujúceho CNI môže objekt existovať bez efektu,
- policy je namespaced, ale source/destination identity môže prechádzať namespace hranice,
- default deny vzniká až po policy, ktorá Pod vyberie v danom smere,
- service translation môže zmeniť observation point,
- hostNetwork Pods a node traffic môžu mať odlišný model,
- DNS egress treba povoliť explicitne pri egress default deny.

`kubectl get networkpolicy` ukazuje desired objects, nie nevyhnutne efektívny dataplane stav.

## 22. L3/L4 firewall verzus L7 firewall a WAF

### L3/L4 firewall

Rozhoduje najmä podľa:

- IP adresy,
- protokolu,
- portu,
- interface,
- connection state.

Nevie automaticky určiť, či HTTP request na povolenom porte obsahuje SQL injection alebo neautorizovanú cestu.

### L7 firewall alebo WAF

Rozumie aplikačnému protokolu a môže rozhodovať podľa:

- HTTP host a path,
- method,
- headers,
- request body,
- identity tokenu,
- rate a behavioru,
- signatúry útoku.

L7 enforcement nastáva až po úspešnom nižšom network path-e. Pri TLS termination mimo WAF nemusí WAF vidieť plaintext. Pri passthrough modeli L7 inspection nie je možná bez terminácie.

## 23. Egress filtering

Outbound policy obmedzuje, kam workload smie komunikovať.

Použitie:

- obmedzenie data exfiltration,
- blokovanie command-and-control trafficu,
- vynútenie egress proxy,
- povolenie iba potrebných dependencies,
- zníženie lateral movement,
- stabilný dependency inventory.

Egress default deny je prevádzkovo náročný, pretože aplikácie potrebujú:

- DNS,
- NTP,
- certificate validation endpoints,
- package repositories,
- cloud metadata alebo APIs,
- dynamické SaaS addresses,
- telemetry collectors.

IP allowlist pre SaaS endpoint môže byť nestabilný. Niekedy je vhodnejší proxy alebo identity-aware egress kontrola.

## 24. Source identity a spoofing

Firewall rule používajúca source IP predpokladá, že source identity je dôveryhodná.

Anti-spoofing vrstvy môžu zahŕňať:

- ingress filtering,
- reverse path validation,
- cloud source/destination checks,
- switch source guard,
- authenticated tunnels,
- workload identity v service meshi.

Ak útočník môže source IP spoofovať v rovnakom enforcement scope, IP allowlist nemusí poskytovať očakávanú identitu.

Proxy a NAT navyše môžu zmeniť source address. Backend potom vidí proxy alebo gateway, nie pôvodného klienta. Dôvera v `X-Forwarded-For` bez overenia trusted proxy pathu je nebezpečná.

## 25. Logging, counters a flow logs

Logovanie každého packetu môže preťažiť CPU, disk a SIEM.

Dobrý model používa kombináciu:

- rule counters,
- rate-limited deny logs,
- flow logs,
- conntrack metrics,
- sampled packet capture,
- explicitný rule identifier,
- koreláciu s deploymentom a časom.

Nftables counter:

```nft
tcp dport 443 counter accept
```

Log má obsahovať aspoň:

- timestamp,
- source a destination,
- protocol a port,
- interface alebo zone,
- action,
- rule identity,
- state,
- sampling/rate-limit kontext.

Absencia logu neznamená, že firewall packet nevidel. Rule nemusí logovať, log môže byť rate-limited alebo packet mohol zlyhať na inom enforcement pointe.

## 26. Rate limiting a DoS ochrana

Firewall môže limitovať:

- nové connections,
- ICMP probes,
- packets per second,
- source-specific bursts,
- invalid traffic,
- log rate.

Rate limit musí rozlišovať legitímny burst od útoku. Príliš nízky limit môže zablokovať:

- autoscaling,
- reconnect storm po outage,
- health checks,
- veľa klientov za jedným NAT endpointom.

Firewall nie je plnohodnotná DDoS ochrana, ak bottleneck vzniká pred ním na linke alebo provider edge.

## 27. Bezpečný rollout

Zmena remote firewallu môže odstrihnúť management access.

Bezpečný postup:

1. Potvrď out-of-band console alebo recovery mechanizmus.
2. Exportuj aktuálny efektívny ruleset.
3. Identifikuj management source a return path.
4. Pridaj explicitný management allow pred default deny.
5. Validuj syntax mimo aktívneho rulesetu.
6. Použi atomické načítanie alebo transakciu.
7. Nastav časovaný rollback, ak platforma umožňuje.
8. Nezatváraj existujúcu session.
9. Otvor novú paralelnú session a over ju.
10. Otestuj legitímne aj zakázané flows z relevantných segmentov.
11. Ulož persistent configuration.
12. Over stav po reload/reboot scenári.

Zmena, ktorá funguje iba pre existujúcu conntrack session, nie je úspešne overená. Treba otestovať nový flow.

## 28. Policy lifecycle

Firewall rule má mať lifecycle podobný aplikačnému kódu:

- owner,
- business alebo technický účel,
- source požiadavky,
- test,
- review,
- deployment,
- observability,
- expiration alebo revalidation,
- rollback,
- odstránenie po zániku dependency.

Dočasné pravidlo bez expirácie sa stáva trvalým attack surface. Comment v rulesete má vysvetliť dôvod, nie iba zopakovať port.

## 29. Diagnostický postup

Klient sa nevie pripojiť na server.

### Krok 1: potvrď endpoint

```bash
getent ahosts <name>
ss -lntp
```

Over destination IP, port, protocol a listener bind.

### Krok 2: potvrď route

```bash
ip route get <server-ip>
ip route get <client-ip>
```

Over forward aj return path.

### Krok 3: zachyť packet na každom relevantnom bode

```bash
sudo tcpdump -ni any host <peer-ip> and port <port>
```

Urči posledný bod, kde packet existuje.

### Krok 4: over efektívnu policy

```bash
sudo nft list ruleset -a
sudo conntrack -L
```

Sleduj chain, counter, state a rule handle.

### Krok 5: odlíš failure typ

```text
žiadny packet na serveri
→ upstream route, ACL, SG alebo path

packet príde, bez odpovede
→ host firewall, listener, queue alebo application

RST/reject
→ explicitné odmietnutie alebo no listener

timeout
→ drop alebo chýbajúci return path

handshake funguje, request zlyhá
→ TLS, proxy, WAF alebo application policy
```

### Krok 6: over nový flow

Po zmene policy otestuj novú connection, nie iba existujúcu stateful session.

## 30. Typické symptómy

### Timeout

Často znamená silent drop, chýbajúcu route alebo return path. Observation point musí určiť, kde traffic zmizol.

### Okamžité `connection refused`

Remote endpoint poslal RST, lokálny kernel vie, že nič nepočúva, alebo firewall použil reject.

### Funguje z jedného subnetu, nie z druhého

Možná source-based policy, odlišná route, ACL, zone, security group alebo asymmetric path.

### Existujúce connections fungujú, nové nie

Možná conntrack exhaustion, listen queue pressure, rate limit, source-port exhaustion alebo policy aplikovaná iba na nové flows.

### IPv4 funguje, IPv6 nie

Možný chýbajúci IPv6 ruleset, listener iba na IPv4, blokované ICMPv6 alebo odlišná cloud policy.

### Host firewall ukazuje allow, packet neprichádza

Traffic mohol zablokovať cloud ACL, security group, hypervisor, CNI alebo upstream appliance.

### Counter na očakávanom pravidle nerastie

Packet môže ísť iným hookom, chain, family, namespace, interface alebo ruleset managerom.

## 31. Časté omyly

### „Firewall otvorí port“

Firewall iba povoľuje traffic. Port musí byť bindnutý socketom a aplikácia musí odpovedať.

### „NAT je firewall“

Nie. Translation a policy enforcement sú odlišné funkcie.

### „Stateful firewall nepotrebuje outbound policy“

Nové outbound flows stále potrebujú povolenie podľa platformového modelu.

### „ICMP treba vždy blokovať“

Nie. Potrebné ICMP a ICMPv6 správy sú súčasťou funkčného IP stacku.

### „Security group je celý firewall model“

Nie. Môžu existovať ACL, host firewall, CNI policy, proxy a aplikačná autorizácia.

### „Allow rule dokazuje aplikačný health“

Nie. Dokazuje iba policy verdict v jednom enforcement pointe.

### „Packet capture na hoste vidí každý drop“

Nie. Packet mohol byť zahodený pred hostom alebo v inom namespace/dataplane.

### „Default deny stačí zapnúť a potom dopĺňať výnimky“

Bez inventory, recovery a observability je to prevádzkový hazard.

## 32. Kontrolné otázky

1. Aký je rozdiel medzi routingom, NATom a firewallom?
2. Prečo je observation point súčasťou významu firewall policy?
3. Aký je rozdiel medzi stateless a stateful filteringom?
4. Čo znamenajú conntrack stavy `NEW`, `ESTABLISHED`, `RELATED` a `INVALID`?
5. Aký je rozdiel medzi drop a reject?
6. Prečo môže rule order zmeniť výsledok?
7. Aký je rozdiel medzi INPUT, OUTPUT a FORWARD pathom?
8. Prečo `ct state established` nie je dôkaz aplikačného health?
9. Ako conntrack exhaustion ovplyvní nové a existujúce flows?
10. Prečo nemožno blokovať všetok ICMPv6?
11. Ako sa líši security group od stateless network ACL?
12. Prečo môže hostový `tcpdump` nevidieť cloud firewall drop?
13. Aký je rozdiel medzi L4 firewallom a WAF?
14. Čo musí egress default deny zohľadniť?
15. Ako bezpečne nasadiť default-deny policy na remote host?
16. Prečo treba po zmene overiť nový flow?
17. Aké údaje má obsahovať firewall log alebo flow log?
18. Ako zistíš, že packet išiel iným chain alebo namespaceom?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: NAT](nat.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Proxy a reverse proxy →](proxy-and-reverse-proxy.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
