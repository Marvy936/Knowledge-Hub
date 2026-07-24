# Network troubleshooting

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: všetky predchádzajúce kapitoly sekcie
- Súvisiace témy: observability, incident response, packet capture, distributed systems

## 1. Cieľ

Network troubleshooting je systematické zužovanie failure scope od používateľského symptómu po konkrétny flow, observation point, vrstvu a mechanizmus zlyhania.

Cieľom nie je náhodne spúšťať príkazy. Každý krok má:

1. testovať konkrétnu hypotézu;
2. rozlišovať aspoň dva možné failure modes;
3. používať autoritatívny observation point;
4. minimalizovať zmenu systému;
5. zachovať dôkazy;
6. viesť k overiteľnej náprave.

## 2. Základný metodický model

```text
používateľský symptóm
  ↓
scope a čas
  ↓
flow identity
  ↓
end-to-end path
  ↓
hypotéza
  ↓
diskriminačný dôkaz
  ↓
root cause mechanizmus
  ↓
najmenšia bezpečná náprava
  ↓
overenie používateľského výsledku
```

Troubleshooting sa nesmie skončiť vetou „sieť nefungovala“. Musí vysvetliť, ktorý packet, request alebo state zlyhal, kde a prečo.

## 3. Začni používateľským symptómom

Namiesto:

```text
API je pomalé
```

definuj:

```text
Klienti z pobočky A od 10:14 nedokončia HTTPS POST
na api.example.com/payments do 10 sekúnd.
GET health endpoint funguje. Klienti z internetu nie sú postihnutí.
```

Zaznamenaj:

- presný hostname, IP alebo URL;
- protocol a port;
- method alebo aplikačnú operáciu;
- source identity a location;
- čas vrátane timezone;
- očakávaný výsledok;
- skutočný error alebo timeout;
- frequency a duration;
- či problém ovplyvňuje nové aj existujúce connections;
- čo sa zmenilo tesne pred incidentom.

Bez presného symptómu nemožno vybrať správny observation point.

## 4. Scope ako prvý silný filter

Rozdeľ incident podľa nezávislých dimenzií:

- jeden client verzus všetci;
- jeden subnet, VLAN, Availability Zone alebo región;
- interný verzus externý prístup;
- IPv4 verzus IPv6;
- jeden resolver alebo DNS view;
- jedna destination IP;
- jeden load-balancer backend;
- jedna application version;
- jedna route/path;
- nový flow verzus reused connection;
- malé payloady verzus veľké;
- jedna identity alebo tenant;
- konkrétny časový pattern.

Scope často priamo ukáže failure domain. Ak každý štvrtý request zlyhá, hypotéza „jeden zo štyroch backendov“ je silnejšia než všeobecné „Internet je nestabilný“.

## 5. Flow identity

Pred capture alebo firewall analýzou identifikuj flow:

```text
protocol
source IP
source port
original destination IP
original destination port
translated tuple, ak existuje NAT
hostname/SNI/HTTP authority
request ID
čas
network namespace/VRF
```

TCP flow sa typicky identifikuje päťprvkom. Proxy vytvára nový flow, takže client → proxy a proxy → upstream majú odlišné tuples a lifecycle.

Pri NAT existuje original aj translated tuple. Pri HTTP/2 môže jedna TCP connection obsahovať viac request streams. Pri WebSocket môže jeden HTTP handshake viesť k dlhodobému message channelu.

## 6. End-to-end HTTPS path

```text
client application
  ↓ local application cache
OS/NSS stub resolver
  ↓ recursive DNS/cache
DNS answer a address-family selection
  ↓ local socket/connect
routing rule a source-address selection
  ↓ ARP/NDP k next hopu
local firewall / endpoint policy
  ↓ network path, ACL, NAT, tunnels
edge load balancer
  ↓ TLS SNI/ALPN/certificate
reverse proxy alebo gateway
  ↓ route, pool, retry, timeout
backend listener
  ↓ application processing
backend dependencies
  ↓ response cez všetky vrstvy späť
client interpretation a business result
```

Každý krok má vlastný state a môže generovať podobný používateľský timeout.

## 7. Observation point musí zodpovedať otázke

Príklady:

- „Akú IP vybrala aplikácia?“ — application/runtime resolver log alebo `getent`, nie iba verejný `dig`.
- „Akú route vybral kernel?“ — `ip route get` s konkrétnym source/mark/namespace.
- „Prišiel SYN na server?“ — packet capture na správnom server interface/namespace.
- „Ktoré firewall pravidlo sa zhodlo?“ — ruleset counters/trace na enforcement point-e.
- „Ktorý backend vybral LB?“ — LB access log alebo response debug metadata.
- „Kde vznikol 504?“ — proxy/gateway log s request ID.
- „Spracoval server payment?“ — business database/event audit, nie iba client timeout.

Jeden observation point nikdy nie je automaticky autoritatívny pre celý distributed path.

## 8. Hypotéza a diskriminačný test

Dobrá hypotéza je falzifikovateľná:

```text
Hypotéza:
Klient preferuje chybnú IPv6 AAAA adresu.

Predikcia:
curl -6 zlyhá, curl -4 uspeje;
packet capture ukáže IPv6 SYN bez odpovede;
DNS vráti obe families.
```

Slabá hypotéza:

```text
Asi firewall.
```

Pred každým testom si napíš:

- čo očakávam, ak je hypotéza pravdivá;
- čo očakávam, ak je nepravdivá;
- ktorý výsledok zvolí ďalšiu vetvu;
- či test mení systém;
- aký má blast radius.

## 9. Bottom-up, top-down a divide-and-conquer

### Bottom-up

Začni linkom a pokračuj nahor. Vhodné, keď host nemá základnú konektivitu alebo scope nie je jasný.

```text
interface → neighbor → route → transport → TLS → HTTP
```

### Top-down

Začni presným user requestom a postupne izoluj failure phase. Vhodné pri dobrej application observability.

```text
business result → HTTP → TLS → transport → network
```

### Divide-and-conquer

Testuj strednú vrstvu s vysokou diskriminačnou hodnotou. Napríklad zisti, či prebehol TCP handshake:

- ak nie, pokračuj nižšie;
- ak áno, pokračuj TLS/HTTP.

Neexistuje povinnosť vždy začať Layer 1. Začni testom s najvyššou informačnou hodnotou a najnižším rizikom.

## 10. Minimálny klientský snapshot

```bash
getent ahosts api.example.com
resolvectl query api.example.com
ip route get <destination-ip>
ss -tan
curl -v --connect-timeout 5 https://api.example.com/path
openssl s_client -connect api.example.com:443 -servername api.example.com
```

Zachyť:

- exact command a environment;
- timestamp;
- DNS answers a TTL, ak relevantné;
- selected IP family;
- source IP a interface;
- connect time;
- TLS SNI, certificate a ALPN;
- remote IP z reálnej connection;
- HTTP status, headers a redirect chain;
- request ID;
- error text bez odstránenia podstatného detailu.

Snapshot má byť reprodukovateľný. „Mne to nejde“ nie je diagnostický artefakt.

## 11. Minimálny server snapshot

```bash
ip -br addr
ip rule
ip route show table all
ss -lntup
systemctl status <service>
journalctl -u <service> --since '10 minutes ago'
sudo nft list ruleset -a
sudo tcpdump -ni any host <client-ip> and port <port>
```

Over:

- proces a unit lifecycle;
- listener address, port a protocol;
- network namespace;
- route späť ku klientovi;
- firewall counters;
- príchod request packetov;
- odchod responses;
- application access/error log;
- cgroup pressure, ak služba nestíha;
- proxy/backend connection, ak server nie je origin.

## 12. DNS troubleshooting lifecycle

### Krok 1: reprodukuj rovnakú resolution path

Aplikácia môže používať NSS, vlastný runtime resolver, sidecar alebo cache. `dig` testuje DNS protocol, nie nevyhnutne aplikačnú path.

```bash
getent ahosts api.example.com
resolvectl query api.example.com
dig api.example.com A
dig api.example.com AAAA
```

### Krok 2: klasifikuj výsledok

- timeout — resolver alebo network path neodpovedá;
- `NXDOMAIN` — meno neexistuje podľa daného view;
- NODATA — meno existuje, ale nie daný record type;
- `SERVFAIL` — recursion, authority alebo DNSSEC validation zlyhala;
- nesprávna IP — data alebo split-view problém;
- správna IP, connection zlyhá — pokračuj routingom.

### Krok 3: porovnaj vrstvy

- local hosts/NSS;
- stub/cache;
- configured recursive resolver;
- iný resolver iba ako comparison;
- authoritative server;
- interný verzus externý view.

### Krok 4: cache a čas

Skontroluj TTL, negative caching, application cache a to, či zmena DNS prebehla pred alebo po vytvorení cache entry.

### Krok 5: transport a validation

Over UDP aj TCP port 53, EDNS, fragmentation/MTU a DNSSEC chain.

## 13. Address-family selection

Dual-stack klient môže zlyhávať iba cez jednu family.

```bash
curl -4 -v https://api.example.com/
curl -6 -v https://api.example.com/
ip -4 route get <ipv4>
ip -6 route get <ipv6>
```

Over:

- A a AAAA;
- IPv6 default route;
- firewall rules pre obe families;
- listener bind;
- ICMPv6/PMTUD;
- source-address selection;
- Happy Eyeballs behavior;
- rozdielne backendy za IPv4/IPv6 endpointom.

„IPv4 funguje“ neznamená, že služba funguje pre clienta, ktorý vybral IPv6.

## 14. Routing a source selection

```bash
ip rule show
ip route show table all
ip route get <destination>
ip route get <destination> from <source>
```

Kontroluj:

- longest-prefix match;
- policy rules a priority;
- routing table;
- source-address selection;
- next hop a interface;
- namespace alebo VRF;
- packet mark;
- connected route;
- default route;
- explicit blackhole/unreachable route;
- reverse path.

Routing table je decision state, nie dôkaz doručenia. Next hop môže byť nedostupný a return path môže byť odlišný.

## 15. Neighbor a L2 troubleshooting

```bash
ip -br link
ip -s link show dev <iface>
ip neigh show dev <iface>
sudo arping -I <iface> <ipv4-next-hop>
sudo tcpdump -eni <iface> 'arp or icmp6'
```

Otázky:

- je interface administratívne up;
- má carrier;
- je správny VLAN context;
- odchádza ARP/NDP request;
- prichádza reply;
- odpovedá správna MAC;
- neexistuje duplicate IP;
- neflappuje MAC medzi ports;
- nie sú RX/TX errors alebo drops;
- nie je endpoint v inom network namespace.

Route k gateway neznamená úspešnú neighbor resolution.

## 16. Forward a return path

Každá obojsmerná komunikácia potrebuje dve route decisions:

```text
client → server
server → client
```

Forward path môže fungovať, ale response môže:

- ísť cez inú stateful firewall;
- obísť NAT mapping;
- použiť nesprávny source IP;
- naraziť na chýbajúcu route;
- byť zahodená reverse-path filteringom;
- vstúpiť do iného tunnelu/VRF.

Pri asymmetric incidentoch rob capture na oboch stranách a na relevantných middleboxes. Absencia response u clienta nevysvetľuje, či ju server nevytvoril alebo sa stratila späť.

## 17. TCP handshake klasifikácia

### SYN bez odpovede

Možnosti:

- client packet neopustil host;
- route/neighbor failure;
- firewall drop;
- remote path outage;
- server packet neprijal;
- SYN-ACK sa stratil na return path;
- backlog/SYN protection.

### SYN → RST

Aktívne odmietnutie:

- nič nepočúva;
- listener je na inej adrese;
- firewall reject;
- proxy/LB nemá route/target;
- packet patrí neexistujúcemu flowu.

### Handshake uspeje

Transportná cesta existuje. Pokračuj TLS alebo application protocol. Handshake neoveruje business health.

### Opakované SYN/SYN-ACK

Jedna strana nedostáva nasledujúci packet. Skontroluj asymetriu, firewall state a capture na oboch smeroch.

## 18. TCP state a pressure

```bash
ss -tan
ss -ti
ss -s
nstat
```

Dôležité patterns:

- veľa `SYN-SENT` — connect attempts nedokončujú handshake;
- veľa `SYN-RECV` — incomplete handshake/backlog pressure;
- veľa `CLOSE-WAIT` — lokálna aplikácia nezatvára po peer FIN;
- veľa `TIME-WAIT` — vysoký connection churn; posúď port capacity;
- retransmissions — loss, congestion alebo severe delay;
- zero window — receiver/application nestíha čítať;
- listen queue overflow — proces počúva, ale nestíha accept.

Nemeň TCP sysctls pred potvrdením konkrétneho capacity bottlenecku.

## 19. UDP troubleshooting

UDP nemá transportný handshake. Absencia response môže znamenať:

- request sa stratil;
- server nepočúva;
- firewall ho zahodil;
- application ho odmietla bez odpovede;
- response sa stratila;
- NAT mapping expiroval;
- datagram fragmentácia zlyhala;
- receiver buffer overflow;
- protocol transaction ID nesedel.

Potrebný postup:

1. zachyť request na senderi;
2. zachyť request na receiveri;
3. over socket/bind;
4. over application logs;
5. zachyť response;
6. over return path;
7. skontroluj ICMP errors;
8. analyzuj aplikačný timeout/retry model.

## 20. Firewall troubleshooting

Firewall analýza musí určiť:

- ktorý enforcement point;
- packet direction;
- hook/chain;
- original alebo translated tuple;
- conntrack state;
- matching rule;
- verdict;
- counter/log evidence.

```bash
sudo nft list ruleset -a
sudo conntrack -L
sudo tcpdump -ni any host <address> and port <port>
```

Dôležité:

- INPUT nie je FORWARD;
- security group nie je host firewall;
- stateless ACL potrebuje return rules;
- established conntrack state nie je to isté ako TCP `ESTABLISHED`;
- policy zmena môže ovplyvniť iba nové flows;
- IPv4 a IPv6 rules môžu byť odlišné;
- drop vedie k timeoutu, reject k rýchlej chybe.

Nevypínaj firewall ako prvý test. Použi counters, tracing, dočasné úzke pravidlo alebo controlled source.

## 21. NAT troubleshooting

Sleduj celý translation lifecycle:

```text
inside original packet
  ↓ rule match
translated egress packet
  ↓ remote response
return packet k translation pointu
  ↓ conntrack lookup
reverse translation
  ↓ inside delivery
```

Over:

1. client route na NAT gateway;
2. packet na inside interface;
3. forwarding;
4. NAT rule match;
5. translated source/destination;
6. conntrack entry;
7. egress packet;
8. remote response;
9. symmetric return cez správny NAT node;
10. reverse translation;
11. port/table capacity.

Existujúce mappings môžu fungovať, kým nové zlyhávajú pre source-port alebo conntrack exhaustion.

## 22. MTU a Path MTU Discovery

Silný pattern:

```text
small request works
large request stalls
```

alebo:

- TCP handshake funguje;
- malé TLS/HTTP messages fungujú;
- veľký certificate chain, upload alebo response timeoutuje;
- problém existuje iba cez VPN/overlay.

Nástroje:

```bash
tracepath <destination>
ip link show
ping -M do -s <size> <destination>
```

Otázky:

- aké MTU má každý segment/tunnel;
- prichádza ICMP Fragmentation Needed alebo Packet Too Big;
- neblokuje ho firewall;
- funguje MSS clamping;
- capture je pred alebo po offloade;
- ide o IPv4 fragmentáciu alebo IPv6 source PMTUD.

Zníženie MTU môže potvrdiť hypotézu, ale permanentný fix má opraviť path alebo PMTUD policy.

## 23. TLS troubleshooting

```bash
openssl s_client \
  -connect api.example.com:443 \
  -servername api.example.com \
  -showcerts

curl -v https://api.example.com/
```

Kontroluj:

- destination IP;
- SNI;
- selected TLS version;
- cipher/group/signature;
- presented chain;
- SAN;
- validity a čas;
- client trust store;
- EKU/constraints;
- revocation policy;
- ALPN;
- client certificate pri mTLS.

`curl -k` môže ako kontrolovaný experiment ukázať, že jediným blockerom je trust validation. Nie je to náprava a nesmie sa preniesť do production configu.

## 24. HTTP a proxy troubleshooting

```bash
curl -v https://api.example.com/path
curl --resolve api.example.com:443:<ip> -v https://api.example.com/path
curl --http1.1 -v https://api.example.com/path
curl --http2 -v https://api.example.com/path
```

`--resolve` zachová hostname pre SNI a HTTP authority, ale použije konkrétnu IP. Je vhodný na odlíšenie DNS steeringu od endpoint behavior.

Over:

- method, host, path a query;
- redirect chain;
- protocol version;
- proxy route;
- forwarding headers;
- body limits/framing;
- downstream a upstream timeout;
- retry;
- cache hit/miss;
- status source;
- request ID;
- origin business result.

Test originu priamo je iba comparison. Môže obísť authentication, WAF, rewrite alebo client identity, preto nepreukazuje, že proxy path je chybná bez ďalších dôkazov.

## 25. `502`, `503` a `504`

### `502 Bad Gateway`

Proxy nedostala platnú upstream response. Hľadaj connection reset, protocol mismatch, malformed response, TLS failure k upstreamu alebo chybný target.

### `503 Service Unavailable`

Môže znamenať žiadny healthy backend, overload, maintenance, circuit breaker alebo explicitný load shedding.

### `504 Gateway Timeout`

Proxy nedostala upstream výsledok v budgete. Upstream mohol pokračovať a operáciu dokončiť po client timeout-e.

Status mapovanie je implementation-specific. Koreluj proxy error reason, upstream timings a backend logs.

## 26. Load balancer troubleshooting

Ak zlyháva časť requests:

1. zisti selected frontend IP a backend;
2. rozdeľ výsledky podľa backendu/zóny/version;
3. porovnaj health-check request s reálnym requestom;
4. over weights a selection algorithm;
5. skontroluj affinity alebo connection reuse;
6. odlíš per-connection a per-request balancing;
7. over draining/slow start;
8. sleduj outlier ejection;
9. porovnaj backend capacity;
10. skontroluj retry amplification.

Pattern „každý tretí request“ nemusí byť presne round robin; pri persistent connections môže jedna connection držať chybný backend dlhšie.

## 27. Long-lived connections

WebSocket, SSE, streaming alebo database connections majú odlišný failure model než krátke requests.

Kontroluj:

- idle timeout na každom middleboxe;
- heartbeat;
- maximum connection lifetime;
- token expiry;
- NAT timeout;
- server draining;
- reconnect policy;
- per-client buffer;
- half-open detection;
- state recovery po reconnecte.

Pravidelné odpojenie po presne rovnakom intervale silno ukazuje timeout alebo lease/lifetime policy.

## 28. Packet capture ako experiment

```bash
sudo tcpdump -ni any host 198.51.100.25 and port 443
sudo tcpdump -ni eth0 -s 0 -w incident.pcap
```

Pred capture definuj otázku:

- odchádza DNS query;
- prichádza reply;
- odchádza SYN;
- prichádza SYN-ACK alebo RST;
- kde vzniká retransmission;
- aký tuple existuje pred/po NAT;
- prichádza ICMP error;
- odchádza server response;
- kde sa flow zastaví.

Capture scope:

- správny interface;
- správny network namespace;
- pre/post tunnel;
- inside/outside NAT;
- client aj server;
- dostatočný snap length;
- časová synchronizácia.

Packet capture môže obsahovať citlivé dáta. Minimalizuj filter, access a retention.

## 29. Offloading a capture artefakty

Host capture môže ukazovať:

- veľké logical segments pre TSO/GSO;
- checksum ako neplatný pred hardware offloadom;
- spojené receive buffers pri GRO;
- packet na virtual interface, nie fyzickom wire;
- duplicate-looking observation na `any` alebo bridge/veth paths.

Neinterpretuj hostový pcap ako presnú wire reprezentáciu bez znalosti observation pointu a offloadov.

## 30. Časová korelácia

Distributed flow môže mať logs na:

```text
client
DNS resolver
edge load balancer
WAF
reverse proxy
service mesh
backend
identity provider
dependency
```

Korelácia potrebuje:

- synchronizované clocks;
- timestamp s timezone;
- request/trace ID;
- client identity;
- upstream target;
- selected backend;
- status source;
- duration fázy.

Clock skew môže vytvoriť falošný záver, že response vznikla pred requestom alebo že timeout nastal na nesprávnej vrstve.

## 31. Intermittent failures

Jednorazový manuálny test nemusí zachytiť problém. Použi bounded probe s identitou každého pokusu:

```bash
for i in $(seq 1 60); do
  date -Is
  curl -sS -o /dev/null \
    -w 'ip=%{remote_ip} code=%{http_code} connect=%{time_connect} ttfb=%{time_starttransfer} total=%{time_total}\n' \
    https://example.com/
  sleep 1
done
```

Zaznamenaj:

- remote IP;
- protocol version;
- backend/request ID, ak bezpečne dostupný;
- connect/TLS/TTFB/total latency;
- status/error;
- time.

Probe nesmie incident zosilniť. Frekvencia a concurrency musia byť nižšie než production impact.

## 32. Healthy comparison

Vyber zdravý prípad, ktorý sa líši jednou dimenziou:

- rovnaký client, iný endpoint;
- iný client v rovnakom subnete;
- rovnaký request cez IPv4 a IPv6;
- rovnaký hostname s konkrétnou IP;
- proxy path verzus origin comparison;
- zdravý a chybný backend;
- pred a po config zmene;
- nový a reused connection;
- malý a veľký payload.

Ak zmeníš naraz DNS, source, protocol aj payload, úspešný test nevysvetlí, ktorá zmena bola rozhodujúca.

## 33. Change timeline

Koreluj incident s:

- deploymentom;
- DNS recordom alebo TTL;
- certificate/CA rotation;
- firewall/ACL/security group policy;
- route advertisementom;
- NAT/LB scalingom;
- proxy config reloadom;
- autoscaling/scale-in;
- tunnel/VPN zmenou;
- OS/kernel updateom;
- dependency incidentom;
- cloud maintenance;
- identity policy.

„Nič sa nemenilo“ je hypotéza. Desired state, runtime state a provider control plane sa mohli zmeniť mimo application deploymentu.

## 34. Bezpečný aktívny experiment

Pred zásahom definuj:

```text
hypotéza
predikcia
presná zmena
scope
trvanie
blast radius
rollback
success signal
failure signal
```

Príklad:

```text
Hypotéza: IPv6 path je chybná.
Experiment: jeden testovací client použije curl -4 a curl -6.
Blast radius: iba testovací request.
Dôkaz: -4 success, -6 SYN timeout.
```

Nebezpečné náhodné zásahy:

- vypnúť firewall;
- flushnúť conntrack;
- reštartovať celý proxy fleet;
- vymazať DNS cache bez snapshotu;
- zmeniť MTU na všetkých nodes;
- zvýšiť všetky timeouty;
- vypnúť certificate verification.

Takéto zásahy môžu skryť root cause, odstrániť evidence alebo vytvoriť nový incident.

## 35. Root cause, contributing factors a trigger

### Trigger

Udalosť, ktorá incident aktivovala, napríklad deployment alebo traffic spike.

### Root cause mechanism

Konkrétny technický mechanizmus, bez ktorého by incident nevznikol, napríklad:

- backend po deploymente nebol ready, ale health check kontroloval iba port;
- return route obchádzala stateful firewall;
- certificate renewal nevykonal reload;
- unbounded retries preťažili dependency;
- MTU tunnelu bolo menšie a ICMP bolo blokované.

### Contributing factors

- chýbajúci canary;
- slabá observability;
- manual lifecycle;
- single failure domain;
- príliš dlhý timeout;
- chýbajúci load shedding;
- nejasné ownership.

Postmortem nemá skončiť pri „human error“ alebo „bad config“. Má vysvetliť, prečo control, test alebo recovery mechanizmus chybu nezachytil.

## 36. Mitigation verzus permanentná náprava

Mitigation obnoví službu:

- rollback route;
- odstránenie unhealthy backendu;
- dočasné zníženie trafficu;
- pridanie capacity;
- obnova starého certificate;
- failover.

Permanentná náprava zmení systémový mechanizmus:

- správny readiness check;
- automated certificate deployment verification;
- retry budget;
- route validation;
- MTU/ICMP policy;
- idempotency;
- HA state sync;
- observability a alerting.

Mitigation je legitímna počas incidentu, ale nesmie byť omylom označená za root-cause fix.

## 37. Overenie nápravy

Po zmene over:

1. pôvodný používateľský scenár;
2. všetky postihnuté source groups;
3. IPv4 aj IPv6, ak relevantné;
4. všetky regions/zones/backends;
5. nové aj existujúce connections;
6. malý aj pôvodne chybný veľký payload;
7. error rate a latency percentily;
8. queue, conntrack, port a capacity metrics;
9. absence novej regresie;
10. stabilitu počas primeraného intervalu;
11. business state pri operáciách retryovaných počas incidentu.

„curl vrátil 200 raz“ nie je dôkaz obnovy fleet-wide služby.

## 38. Typické symptom-to-hypothesis mapovanie

### Timeout pred connection

Hypotézy: DNS timeout, route, ARP/NDP, firewall drop, return path, SYN backlog.

### Okamžité `connection refused`

Hypotézy: no listener, wrong bind, firewall reject, LB bez targetu.

### Connection funguje, TLS zlyhá

Hypotézy: SNI, certificate chain, hostname, trust store, protocol/cipher, mTLS.

### TLS funguje, HTTP `502`

Hypotézy: proxy → upstream connect/reset, protocol mismatch, invalid upstream response.

### `503`

Hypotézy: no eligible backend, overload, circuit breaker, maintenance.

### `504`

Hypotézy: upstream timeout, queue, dependency stall, timeout-budget mismatch.

### Existujúce connections fungujú, nové nie

Hypotézy: listener/backlog, conntrack/port exhaustion, new-flow firewall policy, certificate rotation, LB health.

### Malé funguje, veľké nie

Hypotézy: MTU/PMTUD, body limit, proxy buffering, flow control, compression, timeout.

### Jeden región alebo subnet

Hypotézy: route/ACL, DNS view, NAT gateway, MTU, zone backend, provider failure domain.

### Pravidelný disconnect

Hypotézy: idle timeout, token expiry, lease/lifetime, heartbeat mismatch.

## 39. Praktický incident checklist

### Identity a čas

- exact request;
- source/client location;
- protocol/hostname/IP/port;
- timestamp/timezone;
- request ID.

### DNS

- application/system resolver;
- A/AAAA;
- cache/TTL;
- internal/external view;
- authoritative data;
- DNSSEC/transport.

### Network

- source address;
- route/policy table;
- next hop a neighbor;
- namespace/VRF;
- MTU;
- forward a return path.

### Transport

- listener/bind;
- SYN/SYN-ACK/RST;
- TCP states;
- retransmissions;
- queue/port capacity;
- UDP request/response evidence.

### Enforcement a translation

- firewall hook/rule/counter;
- ACL/security group;
- original/translated tuple;
- conntrack state;
- NAT capacity.

### TLS

- SNI;
- chain/SAN/time/trust;
- TLS version/cipher;
- ALPN;
- mTLS.

### Proxy/LB

- selected frontend/backend;
- route/weight/health;
- retries/timeouts;
- draining;
- status source.

### Application

- request log/trace;
- authn/authz;
- dependency;
- business side effect;
- user-visible result.

## 40. Časté omyly

### „Ping funguje, sieť je v poriadku“

Ping testuje konkrétny ICMP flow. Netestuje DNS, TCP/UDP port, TLS, proxy route ani application behavior.

### „Traceroute ukázal chybný hop“

Router môže neodpovedať na probes a pritom forwardovať application traffic. Forward a return paths môžu byť rozdielne a ECMP môže zvoliť inú cestu.

### „Tcpdump nič nevidí, packet neexistuje“

Capture môže byť na nesprávnom interface, namespace, VRF alebo strane tunnelu. Offloading môže meniť pozorovaný tvar.

### „Firewall rule vyzerá správne“

Musíš dokázať, že packet prešiel konkrétnym hookom a zhodil sa s konkrétnym pravidlom v effective rulesete.

### „Reštart vyriešil root cause“

Reštart mohol uvoľniť queue, porty alebo stale state, ale zároveň odstrániť evidence. Je mitigation, kým nie je mechanizmus vysvetlený.

### „HTTP 200 znamená, že incident skončil“

Over body, latency, business state, všetky failure domains a dostatočný interval.

## 41. Kontrolné otázky

1. Ako vytvoríš presnú definíciu používateľského symptómu?
2. Ktoré scope dimenzie najrýchlejšie odhalia failure domain?
3. Čo musí obsahovať identity jedného network flowu?
4. Ako vyberieš autoritatívny observation point pre konkrétnu otázku?
5. Čo je diskriminačný test a ako falzifikuje hypotézu?
6. Aký je rozdiel medzi bottom-up, top-down a divide-and-conquer postupom?
7. Prečo `dig` nemusí reprodukovať DNS správanie aplikácie?
8. Ako rozlíšiš forward-path a return-path failure?
9. Čo packet capture ukáže pri drop-e a čo pri reject-e?
10. Prečo môže TCP handshake uspieť a aplikácia stále zlyhať?
11. Ako diagnostikuješ UDP request bez response?
12. Prečo existujúce NAT/TCP connections môžu fungovať a nové nie?
13. Ako rozlíšiš TLS SNI, HTTP authority a destination IP?
14. Prečo malé requesty môžu fungovať a veľké zlyhávať?
15. Ako odlíšiš `502`, `503` a `504` podľa failure fázy?
16. Prečo packet capture na hoste nemusí zodpovedať wire packetom?
17. Ako healthy comparison izoluje jednu premennú?
18. Aký je rozdiel medzi triggerom, root cause a contributing factorom?
19. Aký je rozdiel medzi mitigation a permanentnou nápravou?
20. Ako overíš obnovu z pohľadu používateľa a všetkých failure domains?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: REST APIs a WebSockets](rest-apis-and-websockets.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Git object model →](../03-git-and-automation/git-object-model.md)
<!-- KNOWLEDGE-NAVIGATION:END -->