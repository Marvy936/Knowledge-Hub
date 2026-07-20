# Network troubleshooting

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: všetky predchádzajúce kapitoly sekcie
- Súvisiace témy: observability, incident response, packet capture, distributed systems

## 1. Cieľ

Network troubleshooting je systematické zužovanie failure scope od používateľského symptómu po konkrétnu vrstvu, component a mechanizmus zlyhania.

Cieľom nie je náhodne skúšať príkazy, ale vytvárať a testovať hypotézy s čo najnižším rizikom zmeny systému.

## 2. Základný princíp

```text
symptóm
  ↓
scope
  ↓
vrstva
  ↓
hypotéza
  ↓
dôkaz
  ↓
náprava
  ↓
overenie používateľského výsledku
```

Pred každým zásahom si polož:

- Čo presne nefunguje?
- Komu a odkedy?
- Je problém trvalý alebo prerušovaný?
- Čo sa zmenilo?
- Ktorý zdravý porovnávací prípad existuje?

## 3. Scope

Rozdeľ incident podľa:

- jedného klienta vs. všetkých klientov,
- jednej IP family,
- subnetu, zóny alebo regiónu,
- jedného backendu,
- konkrétneho hostname/pathu,
- jednej verzie aplikácie,
- nových vs. existujúcich connections,
- interného vs. externého prístupu.

Scope často odhalí failure domain skôr než hlboký packet analysis.

## 4. End-to-end path

Pre typický HTTPS request:

```text
client application
→ local resolver/cache
→ recursive DNS
→ destination IP
→ local route/source address
→ neighbor/gateway
→ host/network firewall
→ NAT/middleboxes
→ load balancer/proxy
→ TLS handshake
→ HTTP routing
→ backend listener
→ application/dependency
→ response return path
```

Každý krok má iné autoritatívne dôkazy.

## 5. Vrstevná diagnostika

### Application

- request/response semantics,
- status codes,
- authentication/authorization,
- business result,
- application logs a traces.

### TLS

- SNI,
- certificate chain,
- hostname,
- protocol/cipher,
- ALPN,
- trust store.

### Transport

- listening socket,
- handshake,
- TCP states,
- resets,
- retransmissions,
- port exhaustion.

### Network

- IP address,
- route,
- source selection,
- MTU,
- forward/return path.

### Link

- interface/carrier,
- VLAN,
- ARP/NDP,
- switch port.

Vrstvy používaj ako mapu, nie ako rigidný checklist. Začni tam, kde je najlacnejší diskriminačný test.

## 6. Minimálna klientská diagnostika

```bash
getent ahosts api.example.com
resolvectl query api.example.com
ip route get <destination-ip>
ss -tan
curl -v --connect-timeout 5 https://api.example.com/path
openssl s_client -connect api.example.com:443 -servername api.example.com
```

Zaznamenaj:

- resolved IPs a family,
- zvolený source address a interface,
- connection timing,
- TLS certificate/SNI/ALPN,
- HTTP status a headers,
- presný čas testu.

## 7. Server-side diagnostika

```bash
ip -br addr
ip route
ss -lntup
systemctl status <service>
journalctl -u <service> --since '10 min ago'
sudo nft list ruleset -a
sudo tcpdump -ni any host <client-ip> and port <port>
```

Over:

- proces existuje,
- počúva na správnej adrese a porte,
- je v správnom namespace,
- firewall rule sa zhoduje,
- request prichádza,
- response odchádza,
- aplikácia request zaznamená.

## 8. DNS troubleshooting

Postup:

1. over search domain a presný query name,
2. porovnaj A a AAAA,
3. testuj cez system resolver (`getent`),
4. testuj recursive resolver (`dig`),
5. skontroluj TTL a negative cache,
6. over authoritative data,
7. porovnaj interný a externý view,
8. over DNSSEC, ak sa validuje,
9. koreluj destination IP s infraštruktúrou.

Rozlíš:

```text
DNS query zlyhala
DNS vrátil nesprávnu odpoveď
DNS je správny, ale destination nefunguje
```

## 9. Routing troubleshooting

```bash
ip route get <destination>
ip rule
ip route show table all
tracepath <destination>
```

Kontroluj:

- longest-prefix match,
- policy routing,
- source address selection,
- default gateway,
- VRF/namespace,
- forward aj return path,
- asymmetric routing a stateful devices.

Traceroute ukazuje reakciu na probes, nie úplnú pravdu o aplikačnom flow.

## 10. Transport troubleshooting

TCP:

```bash
ss -tan state syn-sent
ss -tan state established
ss -tan state time-wait
ss -tan state close-wait
```

Interpretácia packet capture:

- SYN bez odpovede: drop, route, remote host alebo return path,
- SYN → RST: nič nepočúva alebo active reject,
- handshake → immediate reset: application/proxy protocol failure,
- retransmissions: loss, congestion alebo receiver behavior,
- zero window: receiver backpressure.

UDP vyžaduje aplikačný request/response kontext; absencia odpovede je nejednoznačná.

## 11. TLS troubleshooting

```bash
openssl s_client -connect host:443 -servername host -showcerts
curl -vk https://host/
```

`-k` používaj iba na diagnostické rozlíšenie trust failure od ostatných vrstiev, nie ako produkčnú nápravu.

Kontroluj:

- presented chain,
- SAN,
- validity,
- issuer trust,
- SNI,
- ALPN,
- protocol/cipher,
- client certificate pri mTLS.

## 12. HTTP a proxy troubleshooting

```bash
curl -v https://host/path
curl -H 'Host: expected.example' http://<ip>/path
curl --resolve expected.example:443:<ip> https://expected.example/path
```

`--resolve` umožní testovať konkrétnu IP pri zachovaní SNI a Host.

Kontroluj:

- redirect chain,
- proxy-generated vs. origin status,
- Host/path routing,
- forwarding headers,
- body size limits,
- buffering,
- connect/upstream/idle timeout,
- retries,
- cache.

## 13. Packet capture

```bash
sudo tcpdump -ni any host 198.51.100.25 and port 443
sudo tcpdump -ni eth0 -s 0 -w incident.pcap
```

Pred capture definuj otázku:

- Prichádza SYN?
- Odchádza SYN-ACK?
- Kde vzniká RST?
- Sú retransmissions?
- Aký MTU/fragmentation behavior vidím?
- Odpovedá DNS server?

Capture na nesprávnom interface alebo namespace môže vytvoriť falošný záver.

## 14. Observation points

Pri proxy chain-e:

```text
client capture/log
edge load balancer log
reverse proxy access/error log
service mesh proxy log
backend application log/trace
server capture
```

Hľadaj spoločný request ID, source identity, timestamp a upstream target.

Bez časovej synchronizácie sa korelácia výrazne komplikuje.

## 15. MTU a PMTUD

Typický symptóm:

- malé requests fungujú,
- TLS handshake alebo veľké responses timeoutujú,
- VPN/overlay cesta je postihnutá.

Nástroje:

```bash
tracepath destination
ping -M do -s <size> destination
ip link show
```

Neblokuj bez rozmyslu ICMP Fragmentation Needed alebo ICMPv6 Packet Too Big; sú súčasťou Path MTU Discovery.

## 16. Firewall a NAT troubleshooting

Kontroluj postupne:

1. route pred NAT,
2. translation rule,
3. conntrack entry,
4. filter rule a counter,
5. translated packet na egress,
6. return packet,
7. reverse translation,
8. doručenie socketu.

```bash
sudo nft list ruleset -a
sudo conntrack -L
sudo tcpdump -ni any host <address>
```

NAT a firewall sú odlišné rozhodnutia, aj keď ich implementuje rovnaký framework.

## 17. Load balancer troubleshooting

Ak zlyháva iba časť requests:

- identifikuj backend podľa logu/headera,
- porovnaj health-check a reálny endpoint,
- skontroluj weights a affinity,
- over draining,
- porovnaj zóny,
- odlíš nové a reused connections,
- skontroluj retry amplification.

Pravidelný pattern, napríklad každý štvrtý request, často ukazuje jeden chybný backend.

## 18. Intermittent failures

Potrebujú časovú sériu a automatizovaný probe:

```bash
while true; do
  date -Is
  curl -sS -o /dev/null -w '%{remote_ip} %{http_code} %{time_connect} %{time_starttransfer}\n' https://example.com/
  sleep 1
done
```

Zaznamenaj destination IP, latency fázy, status a čas. Neobmedzený probe môže incident zhoršiť; používaj primeranú frekvenciu.

## 19. Healthy comparison

Porovnaj chybný prípad so zdravým:

- iný klient v rovnakom subnete,
- rovnaký klient k inému endpointu,
- iný backend,
- IPv4 vs. IPv6,
- cez proxy vs. priamo,
- pred a po zmene,
- rovnaký request s konkrétnou destination IP.

Meníš iba jednu premennú naraz.

## 20. Change timeline

Koreluj incident s:

- deploymentom,
- DNS zmenou,
- certificate rotation,
- firewall policy,
- route advertisement,
- autoscalingom,
- proxy config reloadom,
- OS/kernel update,
- cloud/network maintenance.

„Nič sa nemenilo“ je hypotéza, nie dôkaz.

## 21. Bezpečné experimenty

Preferuj read-only observation. Pri aktívnom teste definuj:

- očakávaný výsledok,
- blast radius,
- rollback,
- časové okno,
- success/failure signal.

Nebezpečné náhodné zásahy:

- vypnúť firewall,
- vymazať conntrack table,
- reštartovať všetky proxy,
- flushnúť DNS cache bez zachovania dôkazov,
- meniť MTU na produkcii bez hypotézy.

## 22. Typické failure patterns

### Timeout

Drop, chýbajúca route, return path, upstream stall alebo príliš dlhá queue.

### Connection refused

RST z hosta/firewallu; nič nepočúva alebo explicit reject.

### Name resolution failure

Resolver, search domain, DNS server, record alebo validation.

### Certificate failure

Chain, hostname, expiry, trust store, clock alebo SNI.

### `502/503/504`

Proxy-upstream protocol/connectivity, no healthy backend/overload alebo upstream timeout.

### Existujúce connections fungujú, nové nie

Port/conntrack exhaustion, listener backlog, firewall pre new state, certificate rotation alebo balancer health.

### Jeden región alebo subnet

Route, ACL, DNS view, NAT gateway, MTU alebo zone-specific backend.

## 23. Root cause vs. trigger

Trigger môže byť deployment. Root cause môže byť:

- chýbajúci timeout,
- neobmedzený retry,
- nedostatočná capacity,
- nesprávny health check,
- single failure domain,
- manuálny certificate lifecycle,
- chýbajúca observability.

Postmortem nemá skončiť pri „zlá konfigurácia“. Má vysvetliť, prečo systém chybu dovolil, nezachytil a nezvládol.

## 24. Overenie nápravy

Po zmene over:

- pôvodný používateľský scenár,
- všetky postihnuté IP families/zóny,
- error rate a latency,
- nové aj existujúce connections,
- logs a health checks,
- neprítomnosť vedľajších dopadov,
- stabilitu počas primeraného intervalu.

„Príkaz prešiel“ nie je dôkaz obnovy služby.

## 25. Diagnostický checklist

### Identity a čas

- presný hostname, IP, port, protocol,
- client identity a location,
- timestamp a timezone.

### DNS

- system resolver,
- recursive response,
- authoritative record,
- TTL/cache/view.

### Network

- source/destination,
- route a policy,
- neighbor/gateway,
- MTU,
- forward/return path.

### Transport

- listener,
- handshake,
- states,
- loss/retransmissions,
- port/queue capacity.

### Security

- firewall/ACL/security group,
- NAT/conntrack,
- TLS identity/trust,
- authentication/authorization.

### Application

- proxy route,
- status/body,
- dependency,
- request ID/trace,
- business result.

## 26. Časté omyly

### „Ping funguje, sieť je v poriadku“

Ping netestuje DNS, TCP port, TLS ani aplikáciu.

### „Traceroute ukázal problém na hop-e 5“

Router môže iba neodpovedať na probe a forwardovať traffic správne.

### „Tcpdump nič nevidí, packet neexistuje“

Môžeš byť na nesprávnom interface, namespace alebo observation point-e.

### „Reštart vyriešil root cause“

Obnovil stav, ale mohol odstrániť dôkazy.

### „HTTP 200 znamená, že incident skončil“

Treba overiť správny business výsledok, latency a všetky failure domains.

## 27. Kontrolné otázky

1. Ako definuješ scope incidentu?
2. Aké sú hlavné kroky HTTPS request pathu?
3. Aký je rozdiel medzi DNS, route, transport a HTTP failure?
4. Ako packet capture rozlíši drop od rejectu?
5. Prečo traceroute nie je dôkaz presného application pathu?
6. Ako diagnostikuješ malé requesty fungujúce a veľké zlyhávajúce?
7. Prečo existujúce connections môžu fungovať a nové nie?
8. Ako používaš healthy comparison?
9. Aký je rozdiel medzi triggerom a root cause?
10. Ako overíš nápravu z pohľadu používateľa?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: REST APIs a WebSockets](rest-apis-and-websockets.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
