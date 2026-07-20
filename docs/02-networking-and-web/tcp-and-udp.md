# TCP a UDP

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [OSI a TCP/IP model](osi-and-tcp-ip-model.md), [Routing a default gateway](routing-and-default-gateway.md)
- Súvisiace témy: ports, sockets, DNS, HTTP, QUIC, load balancing, firewalls

## 1. Definícia

TCP a UDP sú transportné protokoly používané nad IP.

- TCP poskytuje connection-oriented byte stream s reliability, ordering, flow control a congestion control.
- UDP poskytuje connectionless datagram service s minimálnym transportným stavom a bez zabudovanej garancie doručenia alebo poradia.

Ani jeden protokol sám neurčuje význam aplikačných dát.

## 2. Transport endpoint

Transportný endpoint sa typicky identifikuje kombináciou:

```text
IP address + protocol + port
```

TCP connection je jednoznačne identifikovaná 4-tuple:

```text
source IP
source port
destination IP
destination port
```

V praxi sa zohľadňuje aj transport protocol a network namespace.

Preto môže jeden server port 443 obsluhovať tisíce connections z rôznych source endpoints.

## 3. Porty

Port je 16-bit číslo v rozsahu 0–65535.

Konvenčné skupiny:

- well-known ports,
- registered ports,
- dynamic/ephemeral ports.

Tieto rozsahy sú organizačné konvencie, nie bezpečnostná policy.

Aplikácia môže používať HTTP na neštandardnom porte a ľubovoľný iný protokol na porte 443.

## 4. TCP byte stream

TCP neposkytuje message boundaries.

Ak aplikácia vykoná:

```text
write("ABC")
write("DEF")
```

receiver môže čítať:

```text
"ABCDEF"
```

alebo viac menších chunks podľa buffering-u a network conditions.

Aplikačný protokol musí definovať framing, napríklad:

- length prefix,
- delimiter,
- fixed-size record,
- self-describing serialization.

## 5. TCP handshake

Klasický three-way handshake:

```text
Client                     Server
  | ------ SYN -----------> |
  | <---- SYN-ACK ---------- |
  | ------ ACK -----------> |
  |       ESTABLISHED        |
```

Účel:

- synchronizovať initial sequence numbers,
- potvrdiť obojsmernú reachability,
- dohodnúť options, napríklad MSS, window scaling, SACK a timestamps.

Handshake úspech ešte nedokazuje, že application request bude úspešný.

## 6. Sequence numbers a acknowledgments

TCP čísluje bytes v stream-e.

Receiver potvrdzuje, ktorý ďalší byte očakáva. Sender podľa acknowledgments vie:

- ktoré dáta boli potvrdené,
- ktoré môže odstrániť z retransmission queue,
- ktoré musí po timeout alebo duplicate ACK signále retransmitovať.

TCP reliability znamená, že protokol sa pokúša doručiť ordered byte stream alebo connection ukončí chybou. Neznamená nekonečné retries ani business-level exactly-once spracovanie.

## 7. Retransmissions

Packet môže byť stratený pre:

- congestion,
- link errors,
- firewall/policy drop,
- route changes,
- receiver overload,
- queue overflow.

TCP používa:

- retransmission timeout,
- duplicate ACK heuristiky,
- selective acknowledgments,
- moderné loss-detection algoritmy podľa implementácie.

Pozorovanie:

```bash
ss -ti
nstat | grep -i retrans
tcpdump -ni any tcp
```

Retransmission je symptóm straty alebo oneskorenia, nie automaticky dôkaz chyby konkrétneho linku.

## 8. Flow control

Receiver advertises receive window podľa dostupného bufferu.

```text
sender rate
  ≤ receiver advertised capacity
```

Ak receiver nestíha čítať, window sa môže zmenšiť až na zero window. Sender potom periodicky overuje, či sa window znovu otvorilo.

Flow control chráni receiver. Nie je to to isté ako congestion control, ktorý chráni network path.

## 9. Congestion control

TCP odhaduje dostupnú kapacitu pathu a upravuje množstvo dát in flight.

Koncepty:

- congestion window,
- slow start,
- congestion avoidance,
- loss alebo ECN signal,
- pacing,
- RTT estimation.

Konkrétny algoritmus môže byť napríklad CUBIC alebo BBR podľa systému.

```bash
sysctl net.ipv4.tcp_congestion_control
sysctl net.ipv4.tcp_available_congestion_control
```

Zmena algoritmu bez merania a workload kontextu nie je univerzálna optimalizácia.

## 10. MSS, MTU a segmentation

Maximum Segment Size určuje maximálny TCP payload segmentu, ktorý endpoint deklaruje pri handshake.

Typicky sa odvodzuje z interface/path MTU mínus IP a TCP headers.

Mechanizmy ako TCP Segmentation Offload môžu spôsobiť, že packet capture na hoste ukáže väčšie logical segments než frames na fyzickom linku.

MTU black hole môže spôsobiť, že handshake a malé dáta fungujú, ale väčšie prenosy sa zastavia.

## 11. TCP states

Dôležité stavy:

- `LISTEN`,
- `SYN-SENT`,
- `SYN-RECV`,
- `ESTABLISHED`,
- `FIN-WAIT-1`,
- `FIN-WAIT-2`,
- `CLOSE-WAIT`,
- `LAST-ACK`,
- `TIME-WAIT`,
- `CLOSED`.

```bash
ss -tan
ss -s
```

### `CLOSE-WAIT`

Remote peer ukončil svoju stranu, ale lokálna aplikácia ešte nezavrela socket. Veľký trvalý počet často ukazuje application cleanup problém.

### `TIME-WAIT`

Endpoint, ktorý aktívne ukončil connection, dočasne drží state, aby staré segments neovplyvnili novú connection s rovnakým tuple.

Veľa `TIME-WAIT` nie je automaticky incident; treba posúdiť ephemeral port pressure, connection reuse a workload.

## 12. Graceful a abortive close

### FIN

Oznamuje, že endpoint už nebude posielať ďalšie bytes, ale môže ešte prijímať.

TCP umožňuje half-close.

### RST

Connection sa ukončí okamžite a receiver dostane reset signal. RST môže vzniknúť, keď:

- nič nepočúva na porte,
- application abortne socket,
- firewall aktívne rejectne,
- packet patrí neexistujúcej connection.

RST je odlišný od tichého dropu, ktorý vedie skôr k timeoutu.

## 13. Listen backlog

Server vytvorí listening socket a kernel drží queues pre incoming connection state.

Pri preťažení môže dôjsť k:

- SYN queue pressure,
- accept queue overflow,
- dropped connections,
- retransmitted SYNs,
- rastu handshake latency.

Pozorovanie:

```bash
ss -lnt
nstat | grep -E 'Listen|SYN'
```

Application musí dostatočne rýchlo volať `accept()` a mať primeranú concurrency a backlog configuration.

## 14. Ephemeral ports

Klient typicky používa dočasný source port.

```bash
sysctl net.ipv4.ip_local_port_range
```

Ephemeral port exhaustion môže nastať pri:

- veľkom počte outbound connections,
- dlhom `TIME-WAIT`,
- malom source IP/port priestore,
- connection leak,
- NAT gateway port pressure,
- chýbajúcom connection pooling-u.

Možné riešenia závisia od root cause:

- reuse/pooling,
- viac source IPs,
- kratšie application lifetime tam, kde je bezpečné,
- zníženie leakov,
- horizontálne rozdelenie egressu.

Náhodné sysctl tuning bez pochopenia state lifecycle môže vytvoriť correctness riziká.

## 15. Keepalive

TCP keepalive je voliteľný kernel mechanizmus na detekciu dlho neaktívnej a nefunkčnej connection.

Nie je to isté ako application heartbeat.

Application heartbeat môže overovať:

- protocol responsiveness,
- business session,
- dependency health.

TCP keepalive overuje iba transportnú liveness podľa svojich časov a probe pravidiel.

## 16. Nagle, delayed ACK a malé writes

Nagle algorithm môže agregovať malé writes, aby znížil počet segments. Delayed ACK môže krátko odkladať acknowledgment.

V určitých request/response patterns môže interakcia zvýšiť latency. Aplikácia môže použiť `TCP_NODELAY`, ale plošné vypnutie bez merania zvyšuje packet overhead.

Rozhodnutie závisí od message size, latency cieľa a traffic patternu.

## 17. UDP datagram model

UDP zachováva message boundaries.

```text
send datagram A
send datagram B
```

Receiver dostane samostatné datagrams, ak boli doručené.

UDP neposkytuje zabudované:

- connection handshake,
- retransmission,
- ordering,
- flow control,
- congestion control,
- duplicate suppression.

Aplikácia alebo vyšší protokol musí implementovať to, čo potrebuje.

## 18. UDP header

UDP header obsahuje:

- source port,
- destination port,
- length,
- checksum.

Je výrazne jednoduchší než TCP header.

Nízky protocol overhead však neznamená automaticky nižšiu aplikačnú latency. Aplikácia môže potrebovať vlastné timers, retries, security a congestion behavior.

## 19. Connected UDP socket

UDP socket môže byť v API „connected“ na konkrétny peer.

To neznamená TCP-like handshake. Kernel iba:

- nastaví default destination,
- filtruje incoming datagrams podľa peer,
- môže doručovať niektoré asynchronous errors socketu.

`ss -uan` môže zobrazovať UDP socket state odlišne od jednoduchého unbound listenera.

## 20. UDP loss, duplication a reordering

Aplikácia musí počítať s tým, že datagram:

- nepríde,
- príde viackrát,
- príde mimo poradia,
- príde poškodený a bude zahodený,
- je väčší než receiver buffer,
- fragmentuje sa a stratí celý message pri strate fragmentu.

Preto napríklad DNS používa transaction IDs a retries; streaming protokoly používajú sequence numbers a loss handling.

## 21. UDP a MTU

Veľký UDP datagram môže byť IP-fragmentovaný. Strata jedného fragmentu znehodnotí celý datagram.

Preferované stratégie:

- držať datagrams pod bezpečným path MTU,
- používať application fragmentation s vlastnou recovery logikou,
- Path MTU discovery,
- prepnúť na transport s vhodným segmentation/reliability modelom.

DNS over UDP používa EDNS a pri truncation môže fallbacknúť na TCP podľa klienta/protokolu.

## 22. ICMP errors a UDP

Keď UDP destination port neexistuje, host môže poslať ICMP Port Unreachable.

Firewall môže ICMP blokovať, takže sender dostane iba timeout.

Connected UDP socket môže dostať error pri ďalšej operácii, ale správanie závisí od OS a timing-u.

Absencia UDP response nehovorí, či sa stratil request, response alebo application odpoveď nevznikla.

## 23. Multicast a broadcast

UDP sa často používa s multicastom alebo IPv4 broadcastom.

Použitie:

- service discovery,
- routing/control protocols,
- telemetry,
- media distribution.

Multicast vyžaduje group membership a network support. Nie je automaticky routovaný medzi segmentmi.

## 24. QUIC nad UDP

QUIC používa UDP ako substrate a implementuje:

- reliable streams,
- congestion control,
- loss recovery,
- encryption cez TLS 1.3 integráciu,
- connection migration,
- stream multiplexing bez TCP head-of-line blocking medzi streams.

Tvrdenie „UDP je nespoľahlivý, preto QUIC je nespoľahlivý“ je nesprávne. Reliability môže implementovať vyššia vrstva.

## 25. TCP vs. UDP výber

| Požiadavka | TCP | UDP / protokol nad UDP |
|---|---|---|
| ordered reliable byte stream | natívne | musí implementovať vyššia vrstva |
| message boundaries | nie | áno |
| connection setup | handshake | bez UDP handshake |
| multicast/broadcast | nie | možné |
| kernel congestion control | áno | musí riešiť vyšší protokol |
| partial loss tolerance | stream čaká na chýbajúce bytes | aplikácia môže zvoliť vlastné správanie |

Výber nie je iba „rýchlosť vs. spoľahlivosť“. Rozhoduje aplikačný semantics a failure model.

## 26. Sockets v Linuxe

```bash
ss -lntup
ss -tan
ss -uan
ss -ti
lsof -i
```

Dôležité:

- network namespace,
- bind address,
- port,
- socket state,
- owning process,
- queue sizes,
- TCP internal info.

Listening na `127.0.0.1:8080` nie je dostupné z remote hosta. Listening na `0.0.0.0:8080` pokrýva všetky IPv4 local addresses, ale firewall môže traffic stále blokovať.

## 27. Packet capture

TCP handshake:

```bash
sudo tcpdump -ni any 'tcp port 443'
```

UDP flow:

```bash
sudo tcpdump -ni any 'udp port 53'
```

Interpretácia TCP:

- SYN bez odpovede → drop, path alebo server reachability,
- RST → aktívne odmietnutie alebo no listener,
- handshake + immediate FIN/RST → application/protocol policy,
- retransmissions → loss alebo severe delay,
- zero window → receiver pressure.

Interpretácia UDP vyžaduje aplikačný protokol, pretože transport nemá connection state.

## 28. Troubleshooting scenár: TCP timeout

```bash
getent hosts example.com
ip route get <IP>
ss -tan dst <IP>:443
nc -vz example.com 443
tcpdump -ni any host <IP> and tcp port 443
```

Rozlíš:

- DNS failure,
- route/ARP failure,
- SYN drop,
- RST,
- handshake success,
- TLS/application timeout.

## 29. Troubleshooting scenár: veľa `CLOSE-WAIT`

1. Identifikuj owning process.
2. Over, či remote peers posielajú FIN.
3. Skontroluj application socket lifecycle.
4. Pozri thread dumps alebo goroutines/tasks.
5. Sleduj file descriptor growth.
6. Oprav application cleanup; neznižuj stav iba sysctl tuningom.

`CLOSE-WAIT` state čaká na lokálnu aplikáciu, nie na sieť.

## 30. Troubleshooting scenár: UDP request bez odpovede

1. Zachyť request na senderi.
2. Over route a firewall.
3. Zachyť request na receiveri.
4. Over listening socket a bind address.
5. Zachyť response.
6. Over return path.
7. Skontroluj ICMP errors.
8. Over application transaction ID a timeout/retry logiku.

## 31. Časté omyly

### „TCP garantuje, že business operácia prebehne presne raz“

Nie. Connection môže zlyhať po server-side spracovaní, ale pred doručením response. Aplikácia potrebuje idempotency a deduplication.

### „UDP je vždy rýchlejší“

Nie. Vyšší protokol môže implementovať komplexné reliability a security mechanizmy.

### „TIME-WAIT je memory leak“

Je normálny TCP lifecycle state. Problémom môže byť až jeho dopad na port alebo state capacity.

### „TCP connection je identifikovaná iba destination portom“

Používa source/destination addresses a ports.

### „Keď handshake funguje, aplikácia je zdravá“

Handshake overuje transportnú cestu, nie aplikačné spracovanie.

### „UDP nemá žiadny stav“

Samotný protokol nemá TCP connection state, ale kernel socket, conntrack, NAT a aplikácia môžu stav udržiavať.

## 32. Kontrolné otázky

1. Aký je rozdiel medzi TCP byte streamom a UDP datagramom?
2. Čo identifikuje TCP connection?
3. Načo slúži three-way handshake?
4. Aký je rozdiel medzi flow control a congestion control?
5. Čo znamenajú `CLOSE-WAIT` a `TIME-WAIT`?
6. Ako vzniká ephemeral port exhaustion?
7. Prečo UDP aplikácia potrebuje vlastnú retry alebo ordering logiku?
8. Ako MTU ovplyvňuje TCP aj UDP?
9. Prečo QUIC môže byť reliable, hoci beží nad UDP?
10. Ako packet capture rozlíši timeout od aktívneho odmietnutia?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Routing a default gateway](routing-and-default-gateway.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ports a sockets →](ports-and-sockets.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
