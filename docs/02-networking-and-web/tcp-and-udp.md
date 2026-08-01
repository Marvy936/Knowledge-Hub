# TCP a UDP

Po route lookupu musí Atlas klient preniesť bytes k API. Transportná vrstva pridáva porty a komunikačné semantics. TCP vytvára obojsmerné spojenie s poradím, retransmission a flow control. UDP prenáša samostatné datagramy bez transportnej garancie doručenia alebo poradia. Ani jeden protokol však neposkytuje aplikačnú exactly-once garanciu.

## TCP spojenie je stav na oboch stranách

Klient otvorí spojenie z dočasného source portu na serverový port `443`:

```text
10.24.8.37:53144 → 203.0.113.40:443
```

Zjednodušený handshake:

```text
client  → server  SYN, seq=x
server  → client  SYN-ACK, seq=y, ack=x+1
client  → server  ACK, ack=y+1
```

Handshake potvrdí obojsmernú transportnú reachability a vytvorí sequence state. Nepotvrdí, že TLS handshake alebo HTTP request uspeje. Firewall môže povoliť SYN a následne blokovať väčšie packets; server môže mať otvorený listener, ale aplikácia nemusí byť pripravená.

```bash
ss -tn state syn-sent
ss -tn state established
tcpdump -ni any 'host 203.0.113.40 and tcp port 443'
```

`ss` číta socket state v danom network namespace. Capture zobrazuje packets na vybranom interface. Ak aplikácia beží v kontajneri alebo inom namespace, hostový pohľad nemusí obsahovať správny socket.

## Byte stream a segmentácia

TCP prenáša usporiadaný byte stream. Zachová poradie bytes, nie hranice aplikačných messages. Server môže dostať jeden `read()` s časťou HTTP requestu alebo s viacerými messages podľa bufferingu.

Sequence numbers identifikujú pozíciu v stream-e. Receiver potvrdzuje prijaté bytes a používa receive window na flow control. Sender prispôsobuje množstvo dát aj podľa congestion controlu, ktorý reaguje na loss, RTT a dostupnú kapacitu pathu.

Retransmission je transportná oprava stratených segmentov. Z pohľadu aplikácie môže zvýšiť latency bez explicitnej chyby. Pri packet loss preto sleduj retransmissions, RTT a window state, nie iba konečný HTTP status.

```bash
ss -ti dst 203.0.113.40
nstat -az | grep -E 'TcpRetransSegs|TcpExtTCPTimeouts'
```

Counters sú kumulatívne a často host-wide. Musia sa porovnať v časovom a scope kontexte s konkrétnym flowom.

## Flow control a congestion control

Flow control chráni receiver. Ak aplikácia nečíta socket dostatočne rýchlo, receive window sa zmenší a sender spomalí. Congestion control chráni network path; odhaduje dostupnú kapacitu a upravuje congestion window.

Tieto mechanizmy sa môžu navonok podobať. Zero-window signal ukazuje receiver pressure, retransmissions a klesajúca congestion window skôr path loss. Backend CPU alebo garbage collection môže spôsobiť pomalé čítanie a transportný stall bez sieťovej chyby.

## Ukončenie a TIME_WAIT

Bežné ukončenie používa FIN/ACK výmenu. Reset `RST` spojenie ukončí bez graceful drainu a často znamená, že socket neexistuje, proces spojenie odmietol alebo middlebox poslal reset.

Endpoint, ktorý aktívne uzatvára spojenie, typicky vstúpi do `TIME_WAIT`. Tento stav chráni nové spojenia pred oneskorenými segmentmi starého flowu a umožňuje zopakovať finálny ACK. Veľké množstvo `TIME_WAIT` nie je automaticky problém; treba ho korelovať s port range, connection churn a reuse modelom.

## UDP datagram

UDP message zachová hranicu datagramu:

```text
source port
destination port
length
checksum
payload
```

Protokol nevytvára handshake ani nepotvrdzuje doručenie. Aplikácia musí riešiť timeout, retry, duplicate a ordering podľa potreby. DNS často používa UDP pre bežné queries, no pri truncation alebo iných podmienkach môže prejsť na TCP.

„UDP je bez spojenia“ neznamená, že infraštruktúra nemá state. Firewall a NAT môžu vytvárať časovo obmedzený pseudo-connection state podľa tuple. Load balancer môže používať affinity a QUIC nad UDP udržiava vlastné cryptographic a stream state.

## TCP reliability nie je business exactly-once

Klient môže odoslať celý `POST /v1/orders`, server ho spracuje a response sa stratí. TCP klient nakoniec vidí timeout, ale objednávka môže existovať. Opakovanie requestu vytvorí duplicate, ak API nepoužíva idempotency key alebo deduplication.

```text
transport outcome: response nebola doručená klientovi
business outcome: objednávka mohla byť commitnutá
```

Po unknown outcome sa najprv zisťuje business state pomocou stabilnej operation identity. Transport retry bez aplikačného contractu nie je bezpečný.

## Incident: SYN handshake funguje, ale throughput padá

Po WAN zmene Atlas vidí normálny connect time, no veľké responses sú veľmi pomalé. Capture ukazuje rastúce retransmissions a selective acknowledgements. Backend CPU a receive window sú zdravé. Loss sa objavuje iba na jednom tunnel path-e pri väčších bursts.

Mitigation zníži traffic na zdravú route; root cause odstráni chybný queue alebo MTU configuration. Po oprave sa overí nielen handshake, ale aj throughput, retransmission rate a pôvodný user journey.

## Zhrnutie

TCP poskytuje usporiadaný byte stream s retransmission, flow a congestion controlom. UDP prenáša datagramy s minimálnymi transportnými semantics. Obe riešenia potrebujú aplikačný timeout, retry a duplicate contract. Zelený handshake je iba jeden transition na ceste k business výsledku.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Routing a default gateway](routing-and-default-gateway.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Porty a sockety →](ports-and-sockets.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
