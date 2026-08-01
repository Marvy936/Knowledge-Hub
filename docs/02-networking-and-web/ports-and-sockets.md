# Porty a sockety

<!-- CONCEPT-FIRST:START -->
## Čo sú porty a sockety

Port je 16-bitové číslo v transportnom protokole, ktoré pomáha kernelu doručiť traffic správnej aplikácii. Samotný port neidentifikuje službu globálne. Jeho význam závisí od protocolu, local address, network namespace a socket state-u.

Socket je kernelový komunikačný objekt dostupný procesu cez file descriptor alebo ekvivalent runtime handle. TCP server najprv vytvorí listening socket. Po prijatí spojenia vznikne nový connected socket s vlastným remote endpointom, buffers a transportným state-om.

```text
listener:
TCP 0.0.0.0:8080 LISTEN

accepted connection:
192.0.2.20:8080 ↔ 198.51.100.40:53144 ESTABLISHED
```

Jeden listener teda môže obslúžiť mnoho connections na rovnakom local porte. Unikátnosť TCP flowu typicky určuje source address, source port, destination address, destination port a protocol.

Bind address mení reachability. `127.0.0.1:8080` je dostupné iba cez loopback daného namespace. `0.0.0.0:8080` je IPv4 wildcard pre lokálne adresy. `[::]:8080` je IPv6 wildcard a dual-stack behavior závisí od platformy.

Client dostáva ephemeral source port z lokálneho range. Pri vysokom connection churn-e alebo NAT koncentrácii môže vzniknúť port exhaustion. Connection pooling a multiplexing znižujú počet nových tuples.

Listen backlog a accept queue oddeľujú transportný handshake od rýchlosti, akou aplikácia prijíma connections. Otvorený listener ešte neznamená, že process stíha `accept()`, má voľné file descriptors alebo obsluhuje requests.

Neutrálny incident: lokálny health check na `127.0.0.1:8080` prejde, ale remote client dostane connection refused. Process je bindnutý iba na loopback. Dôkaz o procese a porte je pravdivý, ale pre inú address scope než používa klient.
<!-- CONCEPT-FIRST:END -->

## Atlas scenár a praktické použitie

IP adresa určí host alebo interface, port pomôže kernelu doručiť transportný traffic správnemu socketu. Port však nie je služba a socket nie je iba číslo. Význam vzniká kombináciou protocolu, local address, local port, remote address, remote portu, network namespace a process state-u.

## Listener a prijaté spojenie

Reverse proxy Atlas počúva na porte `443`. Listener môže vyzerať:

```text
TCP 10.50.0.10:443 LISTEN
```

Po prijatí klienta vznikne nový connected socket:

```text
10.50.0.10:443 ↔ 10.24.8.37:53144 ESTABLISHED
```

Listener zostáva pripravený prijímať ďalšie spojenia. Connected socket má vlastné sequence, buffer a timeout state. Preto jeden port môže obsluhovať tisíce súbežných clients.

```bash
ss -lntp
ss -ntp '( sport = :443 or dport = :443 )'
lsof -nP -iTCP:443
```

Process informácie môžu vyžadovať vyššie oprávnenia. Výstup sa viaže na namespace, v ktorom command beží.

## Bind address rozhoduje o reachability

Aplikácia bindnutá na `127.0.0.1:8080` je dostupná iba cez loopback daného namespace. `0.0.0.0:8080` typicky znamená všetky aktuálne IPv4 local addresses; `[::]:8080` IPv6 wildcard a podľa platformového nastavenia môže alebo nemusí prijímať aj IPv4-mapped connections.

```bash
ss -lnt
curl http://127.0.0.1:8080/healthz
curl http://10.60.1.21:8080/healthz
```

Prvý request môže prejsť a druhý zlyhať, hoci process aj port existujú. Health check vykonaný cez loopback preto nepreukazuje Service alebo remote path.

## Port namespace a konflikty

Port je pridelený v rámci protocolu, local address a network namespace. Dve aplikácie môžu počúvať na rovnakom porte, ak používajú odlišné addresses alebo namespaces. Naopak dva procesy sa môžu biť o `0.0.0.0:8080`, pretože wildcard zahŕňa konkrétnu adresu.

`SO_REUSEPORT` alebo load-balancing mechanizmy môžu dovoliť viacerým sockets zdieľať listener podľa definovaných pravidiel. Netreba z toho automaticky usudzovať, že každý proces dostane rovnaký traffic alebo že reload je bezstratový.

## Ephemeral ports

Klient pri outbound spojení dostane dočasný source port z lokálneho range:

```bash
sysctl net.ipv4.ip_local_port_range
ss -tan state time-wait | wc -l
```

Tuple musí byť dostatočne jedinečný. Pri veľkom connection churn-e, úzkom NAT address pool-e alebo spojeniach k rovnakému destination môže vzniknúť port exhaustion. Symptómom sú connect failures alebo čakajúce requests, hoci server má kapacitu.

Connection pooling a HTTP/2 multiplexing znižujú churn. Agresívne rozširovanie port range alebo reuse bez pochopenia tuple a TIME_WAIT môže skryť nesprávny client lifecycle.

## Listen a accept queues

TCP SYN backlog drží rozpracované handshakes; accept queue drží dokončené spojenia čakajúce na `accept()`. Ak aplikácia neprijíma dostatočne rýchlo, klient môže vidieť timeout alebo reset aj pri otvorenom porte.

```bash
ss -lnt
nstat -az | grep -E 'ListenOverflows|ListenDrops'
```

Queue limit je iba jedna časť. Treba zistiť, či process plánuje accept loop, či nemá file-descriptor limit alebo či worker pool nie je blokovaný downstream dependency.

## File descriptor a socket lifecycle

Socket je kernelový objekt dostupný procesu cez file descriptor. Descriptor sa dedí podľa `fork/exec` flags, uzatvára pri process exit-e a podlieha limitom.

```bash
ulimit -n
PID=$(pgrep -n orders-api)
cat "/proc/$PID/limits"
ls -l "/proc/$PID/fd"
```

Ak process vyčerpá descriptors, nemusí vedieť prijať nový socket, otvoriť log ani načítať configuration. Error `EMFILE` je process-local limit; `ENFILE` signalizuje širší systémový limit.

## Incident: health check je zelený, klient dostáva connection refused

Nová verzia `orders-api` počúva iba na `127.0.0.1:8080`. Lokálny health check v tom istom namespace prechádza, ale reverse proxy sa pripája na `10.60.1.21:8080` a dostáva reset.

`ps` a local `curl` vyzerajú zdravo. `ss -lntp` odhalí effective bind address. Oprava mení application config na `0.0.0.0:8080` alebo konkrétnu service address, potom overí listener, remote connect a HTTP outcome. Pridá sa remote-path readiness test, aby sa loopback dôkaz nezamieňal za sieťovú dostupnosť.

## Zhrnutie

Port je iba časť transportnej identity. Listener, connected socket, bind address, namespace, queues, file descriptors a ephemeral range určujú reálne správanie. Diagnostika vždy číta socket z rovnakého namespace a pathu, aký používa klient alebo proxy.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: TCP a UDP](tcp-and-udp.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: DNS →](dns.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
