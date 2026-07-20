# Ports and Sockets

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [TCP a UDP](tcp-and-udp.md), [Linux networking](../01-linux-and-systems/linux-networking.md)
- Súvisiace témy: DNS, firewalls, NAT, load balancing, HTTP, connection pooling

## 1. Definícia

Port je 16-bitový identifikátor transportného endpointu. Socket je kernelový objekt, cez ktorý proces komunikuje lokálne alebo po sieti.

Port sám o sebe nie je služba. Služba je dostupná až vtedy, keď proces vytvorí socket, priradí mu lokálnu adresu a port, začne počúvať alebo komunikovať a sieťová cesta tento traffic umožní.

## 2. Mentálny model

```text
Process
  ↓ socket()
Kernel socket
  ↓ bind(local IP, port)
Listening alebo connected endpoint
  ↓ routing, transport, firewall
Remote endpoint
```

Pre TCP spojenie je konkrétny tok identifikovaný typicky päťprvkom:

```text
protocol + source IP + source port + destination IP + destination port
```

Dve spojenia preto môžu používať rovnaký server port, ak majú odlišný source endpoint.

## 3. Rozsah portov

Porty majú rozsah `0–65535`.

Bežné kategórie:

- `0–1023`: system alebo well-known ports,
- `1024–49151`: registered ports,
- `49152–65535`: dynamický/private rozsah podľa IANA modelu.

Operačný systém môže používať vlastný ephemeral port range:

```bash
cat /proc/sys/net/ipv4/ip_local_port_range
```

Na Linuxe bind na port pod 1024 typicky vyžaduje root alebo capability `CAP_NET_BIND_SERVICE`.

## 4. Socket lifecycle

### TCP server

```text
socket()
  ↓
bind()
  ↓
listen()
  ↓
accept()
  ↓
read()/write()
  ↓
close()
```

Listening socket prijíma nové spojenia. `accept()` vytvorí samostatný connected socket pre konkrétneho klienta; listening socket zostáva aktívny pre ďalšie spojenia.

### TCP klient

```text
socket()
  ↓
voliteľný bind()
  ↓
connect()
  ↓
read()/write()
  ↓
close()
```

Ak klient explicitne neurčí source port, kernel vyberie ephemeral port.

### UDP

UDP nemá transportný handshake. Proces môže socket bindnúť a používať `sendto()/recvfrom()`. Volanie `connect()` na UDP sockete nevytvára TCP-like spojenie; nastaví default peer a umožní kernelu filtrovať prijímané datagramy.

## 5. Binding adresy

Príklady:

```text
127.0.0.1:8080
0.0.0.0:8080
192.0.2.10:8080
[::1]:8080
[::]:8080
```

Význam:

- `127.0.0.1`: dostupné iba cez IPv4 loopback,
- `0.0.0.0`: bind na všetky aktuálne IPv4 local addresses,
- konkrétna IP: iba na danom local address,
- `::1`: IPv6 loopback,
- `::`: IPv6 wildcard; dual-stack správanie závisí od `IPV6_V6ONLY` a systémovej konfigurácie.

Aplikácia počúvajúca na loopbacku nebude dostupná zvonka ani pri otvorenom firewalle.

## 6. Pozorovanie socketov

Autoritatívny moderný nástroj na Linuxe je `ss`:

```bash
ss -lntup
ss -tan
ss -uan
ss -s
```

Užitočné flags:

- `-l`: listening,
- `-n`: numerické adresy a porty,
- `-t`: TCP,
- `-u`: UDP,
- `-p`: process,
- `-a`: všetky sockety.

Príklady:

```bash
ss -lntp 'sport = :8080'
ss -tan state established
ss -tan state time-wait
```

Proces možno identifikovať aj cez:

```bash
lsof -nP -iTCP:8080 -sTCP:LISTEN
fuser -v 8080/tcp
```

## 7. TCP listen queues

TCP server má koncepty súvisiace s pending spojeniami:

- queue pre neúplné handshake,
- accept queue pre dokončené spojenia čakajúce na `accept()`.

Aplikácia môže volať:

```c
listen(fd, backlog)
```

Skutočné limity ovplyvňuje kernel a sysctl, napríklad:

```bash
sysctl net.core.somaxconn
sysctl net.ipv4.tcp_max_syn_backlog
```

Plná queue môže spôsobovať timeouty, retransmissions alebo odmietnuté spojenia aj vtedy, keď proces stále počúva.

## 8. `SO_REUSEADDR` a `SO_REUSEPORT`

`SO_REUSEADDR` a `SO_REUSEPORT` riešia odlišné prípady a ich presná semantika závisí od OS.

Typické použitie:

- rýchlejší restart servera po predchádzajúcom spojení,
- viac workerov počúvajúcich na rovnakom porte s `SO_REUSEPORT`,
- riadené rozdelenie incoming spojení kernelom.

Nie sú bezpečnou náhradou za správny lifecycle ani ospravedlnením pre nejasný ownership portu.

## 9. Ephemeral ports a vyčerpanie

Každé outbound TCP spojenie typicky používa ephemeral source port.

Pri veľkom počte spojení môže nastať:

- vyčerpanie lokálneho ephemeral range,
- veľa socketov v `TIME-WAIT`,
- collision s NAT mappings,
- limity file descriptorov,
- connection tracking pressure.

Diagnostika:

```bash
cat /proc/sys/net/ipv4/ip_local_port_range
ss -s
ss -tan state time-wait | wc -l
cat /proc/sys/fs/file-nr
ulimit -n
```

Riešenie nemá automaticky znamenať skrátenie TCP timeoutov. Najprv treba overiť connection reuse, pooling, keep-alive, retry storms a počet destination endpoints.

## 10. Unix domain sockets

Socket nemusí používať IP ani port. Unix domain socket komunikuje lokálne cez pathname alebo abstract namespace.

Príklad:

```text
/run/app/app.sock
```

Pozorovanie:

```bash
ss -lx
ss -xap
```

Výhody:

- lokálna komunikácia bez IP routing,
- filesystem permissions ako access control,
- nižší overhead v niektorých prípadoch.

Riziká:

- zlý ownership alebo mode,
- stale socket pathname po páde,
- neexistujúci parent directory,
- mount namespace rozdiely.

## 11. Network namespaces

Socket existuje v konkrétnom network namespace. Preto:

```bash
ss -lntp
```

na hoste nemusí ukázať socket kontajnera.

Kontrola:

```bash
readlink /proc/<PID>/ns/net
sudo nsenter -t <PID> -n ss -lntp
```

Port `8080` môže súčasne používať viac procesov v rozdielnych network namespaces bez konfliktu.

## 12. Port publishing a forwarding

Kontajner môže počúvať na `0.0.0.0:8080` vo vlastnom namespace, ale host port nemusí byť publikovaný.

Typický tok:

```text
client
  ↓ host:8080
host NAT/proxy rule
  ↓ container IP:8080
container socket
```

Treba rozlišovať:

- port aplikácie,
- port v container namespace,
- publikovaný host port,
- load balancer frontend port,
- backend target port.

## 13. Bezpečnosť

Otvorený listening socket zväčšuje attack surface.

Kontroly:

- bind iba na potrebné interfaces,
- firewall allowlist,
- autentifikácia a šifrovanie na aplikačnej vrstve,
- least privilege procesu,
- minimalizácia publikovaných portov,
- monitoring neočakávaných listeners,
- ochrana pred connection exhaustion.

Port scanning iba zisťuje odpoveď endpointu. Neurčuje automaticky verziu služby ani jej bezpečnosť.

## 14. Diagnostický postup

Aplikácia údajne počúva na porte `8080`, ale klient sa nepripojí:

```bash
ss -lntp 'sport = :8080'
ip addr
ip route get <client-ip>
sudo nft list ruleset
sudo tcpdump -ni any port 8080
```

Postup:

1. existuje proces a socket,
2. na akej adrese je bind,
3. v ktorom namespace je socket,
4. je port publikovaný alebo routovateľný,
5. blokuje traffic lokálny firewall,
6. prichádza SYN na správny interface,
7. odpovedá server SYN-ACK alebo RST,
8. prebehne application protocol po handshake.

## 15. Typické symptómy

### `Connection refused`

Typicky remote host odpovedal RST alebo lokálny kernel vie, že nič nepočúva. Môže ísť aj o explicitný firewall reject.

### Timeout

Môže znamenať packet drop, chýbajúcu route, firewall, nefunkčný return path alebo preťaženú queue.

### `Address already in use`

Iný socket už používa rovnakú kombináciu address/port alebo predchádzajúci lifecycle koliduje s bind policy.

### Funguje cez localhost, nie cez sieť

Častá príčina je bind iba na loopback.

### Funguje na hoste, nie v kontajneri

Proces môže byť v inom namespace, používať inú route, DNS alebo firewall state.

## 16. Časté omyly

### „Port je otvorený, takže aplikácia funguje“

Nie. Listening socket nedokazuje správny protocol response, autentifikáciu, dependency ani health.

### „Jeden port môže používať iba jedno spojenie“

Nie. Server port obsluhuje veľa spojení rozlíšených päťprvkom.

### „`0.0.0.0` je adresa vzdialeného servera“

Nie. Pri bind znamená všetky lokálne IPv4 adresy.

### „Veľa `TIME-WAIT` je automaticky chyba“

Nie. Je to súčasť TCP correctness. Problémom môže byť až kombinácia s port exhaustion alebo nevhodným connection lifecycle.

### „UDP socket nemôže byť connected“

Môže, ale bez TCP handshake a reliability semantics.

## 17. Kontrolné otázky

1. Aký je rozdiel medzi portom a socketom?
2. Čo identifikuje konkrétne TCP spojenie?
3. Prečo server potrebuje listening aj accepted sockets?
4. Aký je rozdiel medzi bindom na loopback a wildcard adresu?
5. Ako vzniká ephemeral port exhaustion?
6. Prečo hostové `ss` nemusí vidieť socket kontajnera?
7. Čo môže spôsobovať `connection refused` a čo timeout?
8. Prečo listening port nie je dôkaz aplikačného health?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: TCP a UDP](tcp-and-udp.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: DNS →](dns.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
