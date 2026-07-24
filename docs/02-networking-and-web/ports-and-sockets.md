# Ports a sockets

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [TCP a UDP](tcp-and-udp.md), [Linux networking](../01-linux-and-systems/linux-networking.md)
- Súvisiace témy: DNS, firewalls, NAT, load balancing, HTTP, connection pooling

## 1. Port nie je služba

Port je 16-bitový transportný identifikátor. Socket je kernelový komunikačný objekt, ktorý má protocol family, transport protocol, lokálny endpoint, stav, queues a file-descriptor väzbu na proces.

Služba je reálne dostupná až vtedy, keď celý reťazec funguje:

```text
process
  ↓ socket()
kernel socket
  ↓ bind/listen alebo connect
lokálny endpoint
  ↓ route, firewall, NAT, load balancer
remote endpoint
  ↓ application protocol
užitočná odpoveď
```

Samotné číslo portu preto nehovorí, či niečo počúva, či je endpoint routovateľný alebo či aplikácia funguje.

## 2. Socket ako kernel objekt a file descriptor

Proces vytvorí socket systémovým volaním `socket()`. Kernel vytvorí objekt a procesu vráti file descriptor, cez ktorý aplikácia volá `bind()`, `connect()`, `listen()`, `accept()`, `send()`, `recv()` a `close()`.

```text
process FD 7
    ↓
open socket object
    ├── protocol: TCP
    ├── local endpoint
    ├── remote endpoint
    ├── state
    ├── send queue
    └── receive queue
```

File descriptor možno zdediť cez `fork()`, odovzdať cez Unix socket alebo zdieľať medzi threadmi. „Ktorý proces vlastní port“ preto môže znamenať proces, ktorý listener vytvoril, proces, ktorý ho zdedil, alebo workery, ktoré obsluhujú accepted sockets.

## 3. Endpoint a flow identity

Lokálny transportný endpoint tvorí minimálne:

```text
network namespace + protocol + local IP + local port
```

Konkrétny TCP flow pridáva remote IP a remote port. Preto jeden listener na `192.0.2.10:443` môže obsluhovať veľa súčasných connections; každá má iný remote endpoint.

TCP a UDP majú oddelený port space. TCP listener na porte `53` nekoliduje automaticky s UDP listenerom na porte `53`.

## 4. Rozsahy portov

Porty sú číslované `0–65535`. Rozdelenie na well-known, registered a dynamic ranges je konvencia pre interoperabilitu, nie enforcement pravidlo.

- Well-known range — tradičné systémové služby používajú nízke porty; Linux typicky vyžaduje UID 0 alebo `CAP_NET_BIND_SERVICE` pre bind pod `1024`.
- Registered range — aplikácie a produkty si rezervujú bežné čísla, ale port stále nedokazuje protokol.
- Ephemeral range — kernel z neho vyberá dočasné source porty pre outbound flows.

```bash
cat /proc/sys/net/ipv4/ip_local_port_range
```

Operačný systém môže používať iný ephemeral rozsah než organizačné IANA členenie.

## 5. TCP server lifecycle

Typický TCP server prejde týmito krokmi:

```text
socket()
  ↓ vytvorí endpoint objekt
bind()
  ↓ priradí local address a port
listen()
  ↓ zmení socket na listener
accept()
  ↓ vytvorí nový connected socket
read()/write()
  ↓ spracuje konkrétny flow
close()
```

Listening socket zostáva otvorený pre nové connections. Každé úspešné `accept()` vráti samostatný file descriptor pre konkrétneho klienta.

To je dôležité pri diagnostike: listener môže byť zdravý, ale accepted sockets, workers alebo application queues môžu byť preťažené.

## 6. TCP client lifecycle

Klient vytvorí socket a zavolá `connect()`. Ak neurobí explicitný `bind()`, kernel vyberie source address podľa routingu a source-address selection a pridelí ephemeral port.

```text
socket()
  ↓
route + source address selection
  ↓
ephemeral port allocation
  ↓
TCP handshake
  ↓
connected socket
```

`connect()` preto môže zlyhať ešte pred odoslaním SYN, napríklad pre chýbajúcu route, vyčerpaný port space alebo lokálnu policy.

## 7. UDP socket lifecycle

UDP server zvyčajne vykoná `socket()` a `bind()` a potom používa `recvfrom()` a `sendto()`. Neexistuje TCP-like handshake ani accepted socket pre každý peer.

UDP `connect()` je lokálna socketová operácia:

- nastaví default remote endpoint,
- umožní používať `send()` a `recv()`,
- filtruje datagramy podľa peer identity,
- môže zlepšiť priradenie ICMP chýb ku konkrétnemu socketu.

Nevytvára tým zdieľaný transportný connection state s remote hostom.

## 8. Bind address rozhoduje o exposure

Proces binduje socket na lokálnu adresu, nie na všeobecný názov služby.

| Bind | Význam |
|---|---|
| `127.0.0.1:8080` | iba IPv4 loopback v danom namespace |
| `0.0.0.0:8080` | wildcard pre všetky vhodné lokálne IPv4 adresy |
| `192.0.2.10:8080` | iba konkrétna lokálna IPv4 adresa |
| `[::1]:8080` | iba IPv6 loopback |
| `[::]:8080` | IPv6 wildcard; IPv4 správanie závisí od `IPV6_V6ONLY` |

Loopback listener nemožno sprístupniť remote klientovi iba otvorením firewallu, pretože packet nemá zodpovedajúci non-loopback socket endpoint.

Wildcard bind neznamená „počúvaj na ľubovoľnej vzdialenej IP“. Znamená všetky vhodné lokálne adresy v danom namespace.

## 9. IPv4 a IPv6 wildcard interakcia

IPv6 listener na `[::]:port` môže podľa OS, sysctl a socket option prijímať aj IPv4-mapped flows. Iná aplikácia môže vyžadovať samostatný IPv4 socket.

```bash
sysctl net.ipv6.bindv6only
ss -lntp
```

Pri `Address already in use` treba overiť aj dual-stack wildcard konflikt. Výpis iba jedného address family nemusí ukázať celý bind model.

## 10. Bind na neexistujúcu adresu

Bind na konkrétnu IP typicky vyžaduje, aby bola adresa lokálne nakonfigurovaná. Existujú špeciálne transparent alebo freebind mechanizmy pre proxy a routing scenáre, ale bežná aplikácia sa na ne nemá spoliehať bez explicitného návrhu.

Ak služba štartuje skôr než sa adresa objaví, môže bind zlyhať. Service manager dependency, retry policy alebo wildcard bind musia zodpovedať reálnemu address lifecycle.

## 11. Listening socket nie je accepted socket

Listener reprezentuje service endpoint. Accepted socket reprezentuje jeden konkrétny TCP flow.

```text
listener 0.0.0.0:443
├── 192.0.2.10:443 ↔ 198.51.100.20:51000
├── 192.0.2.10:443 ↔ 198.51.100.21:51001
└── 192.0.2.10:443 ↔ 203.0.113.8:42000
```

Listener a accepted sockets môžu mať odlišné owners po pre-fork, socket activation alebo descriptor passing modeli. Pri incidente treba pozorovať oba druhy objektov.

## 12. SYN queue a accept queue

TCP listener má dve odlišné kapacitné fázy:

- SYN queue — handshakes ešte nie sú dokončené.
- Accept queue — handshake je hotový, ale aplikácia connection ešte neprevzala.

`listen(fd, backlog)` vyjadruje požadovanú queue kapacitu, ktorú kernel obmedzí svojou policy.

```bash
sysctl net.core.somaxconn
sysctl net.ipv4.tcp_max_syn_backlog
ss -lnt
nstat | grep -E 'Listen|SYN'
```

Plná SYN queue sa prejavuje handshake retries alebo dropmi. Plná accept queue často znamená, že application accept loop alebo worker pool nestíha.

## 13. Send a receive queues

Connected socket má buffer pre odosielané a prijaté dáta. `ss` zobrazuje queue hodnoty, ktoré treba interpretovať spolu s protokolom a stavom.

- Rastúci send queue — peer alebo network path nepotvrdzuje dáta dostatočne rýchlo.
- Rastúci receive queue — dáta dorazili do kernelu, ale aplikácia ich nečíta.
- UDP receive drops — datagramy môžu doraziť na host, no pretečie socket buffer.

Queue je observation point medzi aplikáciou a transportom. Pomáha rozlíšiť application backpressure od path lossu.

## 14. `SO_REUSEADDR`

`SO_REUSEADDR` mení pravidlá bind konfliktu. Často umožňuje serveru znovu bindnúť lokálny endpoint po reštarte, aj keď existujú connections v lifecycle stavoch.

Presná semantika sa líši medzi OS a protokolmi. Option neznamená „dovoľ ľubovoľným procesom používať rovnaký port“ a nenahrádza kontrolu ownershipu, graceful restartu ani socket activation.

## 15. `SO_REUSEPORT`

`SO_REUSEPORT` umožňuje viacerým kompatibilným sockets bindnúť rovnaký endpoint. Kernel môže incoming flows rozdeliť medzi listeners, často hashom podľa flow identity.

Použitie:

- viac worker procesov bez jedného centrálneho acceptora,
- distribúcia UDP datagramov medzi workers,
- graceful rollout s paralelnými listeners podľa aplikačného modelu.

Riziká:

- nerovnomerné flow sizes,
- nejasný ownership endpointu,
- rozdielne konfigurácie workerov,
- zložitejšia observability a rollout koordinácia.

## 16. Systemd socket activation

Systemd môže listener vytvoriť skôr než samotnú service a file descriptor jej odovzdať. Port potom môže počúvať, hoci application process ešte nebeží alebo sa práve reštartuje.

```text
systemd .socket unit
  ↓ vlastní listener
incoming connection
  ↓ aktivuje service
service zdedí socket FD
```

Pri diagnostike treba skontrolovať `.socket` aj `.service` unit. Ownership portu nemusí byť z výpisu procesu intuitívny.

## 17. Ephemeral port allocation

Outbound connection potrebuje unikátny local tuple. Kernel vyberie ephemeral port tak, aby nekolidoval s existujúcim flow v rovnakom namespace a protocol space.

Vyčerpanie môže spôsobiť:

- veľa súčasných flows k rovnakému destination,
- connection churn a veľa `TIME-WAIT`,
- malý ephemeral range,
- explicitné bindovanie source portov,
- NAT/PAT port pressure,
- connection leak alebo chýbajúci pooling.

```bash
cat /proc/sys/net/ipv4/ip_local_port_range
ss -s
ss -tan state time-wait | wc -l
```

Port exhaustion sa môže prejaviť ako `Cannot assign requested address`, connect failure alebo NAT timeout. Nie je to automaticky server-side problém.

## 18. Reserved a explicitne používané porty

Linux môže vyhradiť časti ephemeral range pre aplikácie, ktoré potrebujú stabilný port. Aplikácia môže tiež explicitne bindnúť source address a port.

Taký návrh zmenšuje dostupný tuple priestor a môže vytvoriť kolízie pri scale-out alebo failover scenároch. Port allocation policy musí byť súčasťou capacity modelu, nie skrytý detail.

## 19. File-descriptor limits

Každý socket používa file descriptor. Aj keď je port space dostatočný, proces môže naraziť na per-process alebo service limit.

```bash
cat /proc/<PID>/limits
ls /proc/<PID>/fd | wc -l
systemctl show example.service -p LimitNOFILE
sysctl fs.file-max
```

Zvýšenie limitu bez opravy socket leak iba oddiali incident. Treba rozlíšiť legitímny connection growth od descriptorov, ktoré aplikácia zabudla zavrieť.

## 20. Unix domain sockets

Unix domain socket používa lokálny kernel IPC path namiesto IP routingu. Môže byť pomenovaný filesystem pathname alebo existovať v abstract namespace.

```text
/run/example/api.sock
```

Výhody:

- lokálny scope — traffic neopúšťa host ani network namespace model IP stacku,
- filesystem DAC — pathname ownership a mode môžu riadiť prístup,
- descriptor passing — procesy si môžu odovzdávať otvorené file descriptors,
- jednoduchá integrácia — reverse proxy môže komunikovať s lokálnym backendom bez TCP portu.

Riziká:

- parent directory permissions,
- stale pathname po nekorektnom páde,
- mount namespace rozdiely,
- SELinux/AppArmor policy,
- nesprávne cleanup a startup race.

```bash
ss -xap
lsof -U
```

## 21. Socket pathname a socket objekt nie sú to isté

Pri pathname Unix sockete je directory entry iba meno vedúce ku kernel endpointu. Odstránenie pathname môže zabrániť novým klientom pripojiť sa, ale existujúce connected sockets môžu ďalej fungovať.

Podobne vytvorenie bežného súboru s rovnakým názvom nevytvorí socket. Diagnostika musí rozlišovať filesystem object type a živý listener.

## 22. Network namespaces

IP socket patrí do konkrétneho network namespace. Namespace má vlastné addresses, routes, port space, firewall a socket inventory.

```bash
readlink /proc/<PID>/ns/net
readlink /proc/self/ns/net
sudo nsenter -t <PID> -n ss -lntup
```

Hostové `ss` nemusí ukázať kontajnerový listener. Port `8080` môže byť bez konfliktu použitý v mnohých namespaces.

## 23. Container port a publikovaný host port

Aplikácia v kontajneri môže počúvať na `0.0.0.0:8080` iba vo svojom namespace. Remote klient sa k nej dostane až cez routing, proxy alebo publikovanie host portu.

```text
client → host:18080
          ↓ DNAT/proxy
        container-IP:8080
          ↓
        application socket
```

Treba oddeliť:

- application port,
- container namespace port,
- host published port,
- load-balancer frontend port,
- backend target port.

Chyba na ktorejkoľvek mapping vrstve môže vyzerať ako „aplikácia nepočúva“.

## 24. Kubernetes socket kontext

Kontajnery v rovnakom Pode typicky zdieľajú network namespace. Preto nemôžu dva procesy bindnúť rovnaký incompatible endpoint bez reuse mechanizmu.

Kubernetes Service port nie je socket na Pode. Je to virtuálny service endpoint, ktorý dataplane prekladá alebo routuje na target port Podu.

```text
Service port → targetPort → Pod IP:container listener
```

Pri diagnostike treba overiť každý endpoint a jeho namespace zvlášť.

## 25. Firewall a bind sú odlišné kontroly

Bind určuje, či kernel má lokálny endpoint pre destination adresu a port. Firewall určuje, či packet môže prejsť policy.

Možné kombinácie:

| Listener | Firewall | Typický výsledok |
|---|---|---|
| nie | allow | host môže poslať RST alebo ICMP unreachable |
| áno | drop | klient typicky timeoutuje |
| áno | reject | klient dostane rýchlu explicitnú chybu |
| áno | allow | transport môže pokračovať, aplikácia stále môže zlyhať |

## 26. NAT a load balancer nemenia backend listener contract

DNAT alebo load balancer môžu zmeniť destination IP a port pred doručením backendu. Backend musí počúvať na výslednom lokálnom endpoint-e a jeho return path musí byť kompatibilný s prekladom alebo proxy modelom.

„Frontend port je otvorený“ preto neznamená, že backend port existuje, health check používa správny protokol alebo response prejde späť.

## 27. Bezpečnostný model socket exposure

Listening socket zväčšuje attack surface, ale bezpečnosť nevyrieši samotné číslo portu.

- Minimal bind scope — služba má počúvať iba na adresách, kde je potrebná.
- Network policy — firewall alebo security group má obmedziť source a protocol.
- Application authentication — povolený packet nie je autorizovaný používateľ.
- Encryption — citlivý protokol potrebuje ochranu proti odpočúvaniu a MITM.
- Least privilege — proces nemá bežať s väčšími právami, než listener vyžaduje.
- Connection limits — rate limiting, queues a worker bounds chránia pred exhaustion.
- Inventory — neočakávané listeners treba detegovať a vysvetliť.

## 28. Pozorovanie socketov v Linuxe

```bash
ss -lntup
ss -tan
ss -uan
ss -xap
ss -s
lsof -nP -i
fuser -v 8080/tcp
```

Pri výstupe kontroluj:

- protocol a address family,
- bind address a port,
- network namespace,
- listener alebo connected state,
- send/receive queue,
- process a file descriptor,
- cgroup/service ownership,
- dual-stack wildcard správanie.

## 29. `Connection refused`

Refused znamená aktívnu chybu, nie všeobecný timeout. Typické príčiny:

- destination host poslal TCP RST, pretože nič nepočúva,
- firewall alebo proxy explicitne rejectli connection,
- aplikácia počúva na inej adrese alebo porte,
- NAT/load-balancer target smeruje na nesprávny endpoint.

Packet capture vie potvrdiť RST alebo ICMP unreachable a jeho source.

## 30. Timeout

Timeout znamená absenciu očakávaného progresu do deadline. Môže vzniknúť pred listenerom aj po ňom:

- DNS alebo route zlyhanie,
- ARP/NDP failure,
- firewall drop,
- chýbajúci return path,
- plná SYN/accept queue,
- TLS alebo application timeout,
- packet loss a retransmission,
- nesprávna IPv4/IPv6 family.

„Timeout“ bez observation pointu nie je root cause.

## 31. `Address already in use`

Bind konflikt môže spôsobovať:

- existujúci listener na rovnakom endpoint-e,
- wildcard listener, ktorý pokrýva konkrétnu adresu,
- IPv6 dual-stack socket, ktorý koliduje s IPv4 bindom,
- reuse options nastavené iba na jednej strane,
- Unix socket pathname po starom procese,
- iný proces alebo unit aktivovaný skôr.

```bash
ss -lntup 'sport = :8080'
lsof -nP -iTCP:8080
systemctl list-sockets
```

## 32. Funguje cez localhost, ale nie zo siete

Najprv over bind:

```bash
ss -lntp 'sport = :8080'
```

Ak listener používa `127.0.0.1`, remote packet sa k nemu nemôže priradiť. Ak používa wildcard alebo interface address, pokračuj route, firewall, port publishing a return-path kontrolou.

## 33. Diagnostický postup: klient sa nepripojí na `8080`

```bash
ss -lntp 'sport = :8080'
ip addr
ip route get <client-ip>
nft list ruleset
tcpdump -ni any 'tcp port 8080'
```

1. Listener — existuje v správnom network namespace?
2. Bind — pokrýva destination IP, ktorú klient používa?
3. Owner — beží očakávaný proces a service?
4. Queue — nie je listener aktívny, ale preťažený?
5. Exposure — je container alebo load-balancer port správne mapovaný?
6. Firewall — ide o allow, drop alebo reject?
7. Packet path — prichádza SYN a odchádza SYN-ACK/RST?
8. Return path — smeruje odpoveď späť ku klientovi?
9. Application layer — po handshake odpovedá správny protokol?

## 34. Diagnostický postup: socket existuje, ale aplikácia nereaguje

1. Over send a receive queues cez `ss -tinp`.
2. Skontroluj thread alebo event-loop state procesu.
3. Over file-descriptor a worker limits.
4. Zachyť, či request bytes dorazili a či response bytes odchádzajú.
5. Skontroluj dependency latency a application logs.
6. Rozlíš listener health od accepted-connection processing.

Listener môže byť v `LISTEN`, aj keď všetky workers sú deadlocked alebo vyčerpané.

## 35. Časté omyly

### „Otvorený port znamená zdravú aplikáciu“

Listener dokazuje iba lokálny transport endpoint. Neoveruje TLS, autentifikáciu, dependencies ani business response.

### „Jeden port môže obsluhovať iba jednu connection“

Jeden listener obsluhuje veľa flows, ktoré sa rozlišujú source a destination tuple.

### „`0.0.0.0` je adresa, na ktorú sa pripája klient“

Je to wildcard bind reprezentácia. Klient používa konkrétnu destination adresu hosta.

### „Hostové `ss` vidí všetky sockets“

Socket inventory je namespace-local. Kontajner alebo Pod môže mať samostatný network namespace.

### „Firewall otvorí loopback listener do siete“

Firewall nemení bind address. Aplikácia musí mať socket na non-loopback local endpoint-e.

### „Zvýšenie backlogu vyrieši preťažený server“

Väčšia queue môže iba oddialiť drop. Ak accept loop alebo workers nestíhajú, treba opraviť processing capacity a backpressure.

## 36. Kontrolné otázky

1. Aký je rozdiel medzi portom, socketom a službou?
2. Ako file descriptor súvisí so socket objektom?
3. Čím sa líši listening socket od accepted socketu?
4. Ako wildcard bind ovplyvňuje network exposure?
5. Prečo môže IPv6 wildcard kolidovať s IPv4 listenerom?
6. Aký je rozdiel medzi SYN queue a accept queue?
7. Čo signalizuje rast receive queue?
8. Kedy sa používa `SO_REUSEPORT` a aké má riziká?
9. Ako vzniká ephemeral port exhaustion?
10. Prečo môže proces naraziť na file-descriptor limit skôr než na port limit?
11. Ako sa Unix socket líši od TCP socketu?
12. Prečo hostový port a container port nie sú ten istý endpoint?
13. Ako packet capture rozlíši refused od timeoutu?
14. Prečo listener nie je dôkaz aplikačného health?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: TCP a UDP](tcp-and-udp.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: DNS →](dns.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
