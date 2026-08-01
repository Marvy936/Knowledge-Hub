# Container networking

Container networking nie je jedna abstraktná „Docker sieť“. Je to konkrétny packet path medzi socketom aplikácie, network namespace-om containeru, hostiteľským dataplane-om a vzdialeným peerom. Keď request zlyhá, musíme zistiť, na ktorej vrstve sa paket prestal správať podľa očakávania: aplikácia nemusí počúvať, route môže chýbať, firewall môže packet zahodiť, NAT alebo conntrack state môže byť vyčerpaný, DNS môže vrátiť nesprávnu adresu a return path môže ísť inou cestou.

Budeme sledovať `payments-api`, ktorá počúva na porte `8080`. V lokálnom Docker prostredí komunikuje s verifier containerom cez user-defined bridge network a zároveň publikuje port `127.0.0.1:18080` na host. Z application pohľadu ide o jeden HTTP server. Z network pohľadu sú to dve odlišné cesty.

## 1. Process najprv vytvorí socket

Sieť nezačína Docker bridge-om. Začína tým, že process vytvorí socket a bindne ho na adresu a port.

```text
payments-api process
→ socket(AF_INET alebo AF_INET6)
→ bind address a port
→ listen queue
```

Ak aplikácia počúva na `127.0.0.1:8080`, prijíma iba traffic smerujúci na loopback konkrétneho network namespace-u. Ak počúva na `0.0.0.0:8080`, prijíma IPv4 traffic na všetkých vhodných interfaces daného namespace-u. Pri IPv6 treba samostatne overiť bind na `::` a kernelové dual-stack správanie.

Listener možno vo vhodnom debug image-i zobraziť:

```bash
ss -lntp
```

Distroless production image nemusí obsahovať `ss`. Vtedy sa používa application telemetry, host namespace inspection alebo controlled debug container, nie ručná inštalácia balíkov do running production containeru.

## 2. Network namespace vytvorí samostatný network view

Bežný bridge container dostane vlastný network namespace. Vo vnútri vidí loopback a virtuálne rozhranie, často pomenované `eth0`.

```bash
docker run --rm --name net-demo alpine:3.22 \
  ip address
```

Výstup sa líši od hostiteľského `ip address`, pretože procesy sa pozerajú na iné network namespaces. Container môže mať adresu napríklad `172.20.0.3/16`, zatiaľ čo host má fyzické alebo virtual interfaces v úplne iných subnets.

Network namespace má aj vlastnú routing table:

```bash
docker run --rm --network atlas-backend alpine:3.22 \
  ip route
```

Typicky obsahuje connected route pre Docker subnet a default route cez bridge gateway.

## 3. Veth pair spája container s hostom

Virtual Ethernet pair funguje ako dve prepojené koncovky. Jedna sa presunie do container network namespace-u a stane sa `eth0`. Druhá zostane na hoste a pripojí sa k bridge-u.

```text
container eth0
↔ veth pair
↔ host-side veth
↔ Docker bridge
```

Packet od `payments-api` odíde cez container `eth0`, objaví sa na host-side veth a bridge rozhodne, kam ho poslať. Pri komunikácii medzi dvoma containers na rovnakom bridge-i môže traffic zostať na host dataplane bez external NAT.

Hostiteľský PID containeru umožňuje pozrieť jeho network namespace:

```bash
pid="$(docker inspect payments-api --format '{{.State.Pid}}')"
nsenter -t "$pid" -n ip address
nsenter -t "$pid" -n ip route
```

`nsenter` vyžaduje host authority. Je vhodný pre kontrolovaný troubleshooting na node, nie ako bežná application operácia.

## 4. Default bridge a user-defined bridge

Docker Engine vytvára default bridge network. Containers na ňom môžu komunikovať podľa IP a legacy link mechanizmov, ale user-defined bridge poskytuje lepšiu project isolation a embedded DNS pre mená containers alebo aliases.

Vytvorenie vlastnej siete:

```bash
docker network create atlas-backend
```

Spustenie API:

```bash
docker run -d --rm \
  --name payments-api \
  --network atlas-backend \
  atlas/payments-api:1.0.0
```

Verifier v rovnakej sieti môže použiť meno:

```bash
docker run --rm \
  --network atlas-backend \
  curlimages/curl:8.10.1 \
  curl -fsS http://payments-api:8080/readyz
```

Meno `payments-api` sa resolve-ne cez Docker embedded DNS pre danú user-defined network. To nepreukazuje host port publishing ani dostupnosť z iného Docker hosta.

## 5. Container IP nie je stabilná service identity

Container IP patrí konkrétnej runtime generation. Po recreate môže dostať inú adresu. Automation, ktorá uloží IP do config file-u, vytvára coupling na ephemeral object.

Stabilnejší model používa service name alebo external load balancer:

```text
payments-api service name
→ aktuálne container endpointy
→ replacement bez zmeny consumer configu
```

V Docker Compose je service name automaticky DNS name v project network. Pri scale-out môže DNS vrátiť viac addresses podľa Compose a Engine modelu, ale Compose sám neposkytuje plnohodnotný load balancer pre všetky použitia. Client musí zvládnuť connection failures a endpoint changes.

## 6. Port publishing vytvára host path

Dockerfile `EXPOSE 8080` iba deklaruje metadata. Host listener alebo NAT rule vznikne až pri runtime publication:

```bash
docker run -d --rm \
  --name payments-api \
  --publish 127.0.0.1:18080:8080 \
  atlas/payments-api:1.0.0
```

Táto syntax znamená:

```text
host address 127.0.0.1, port 18080
→ Docker port publishing dataplane
→ container address, port 8080
```

Binding na `127.0.0.1` obmedzí host listener na loopback. Binding na `0.0.0.0` alebo vynechanie host IP môže sprístupniť port na všetkých vhodných host interfaces podľa platformy a firewallu.

Observed mapping:

```bash
docker port payments-api
docker inspect payments-api \
  --format '{{json .NetworkSettings.Ports}}' | jq .
```

Mapping ešte nepreukazuje, že aplikácia na container porte počúva alebo že host firewall traffic povoľuje.

## 7. Prečo loopback bind rozbije publikovaný port

Predstavme si, že `payments-api` používa:

```text
LISTEN_ADDRESS=127.0.0.1:8080
```

Local healthcheck vo vnútri containeru volá `http://127.0.0.1:8080/readyz` a prejde. Host request však prichádza cez container `eth0`, nie cez jeho loopback.

```text
host 127.0.0.1:18080
→ DNAT alebo proxy path
→ container eth0 address:8080
→ žiadny listener na eth0 address
→ connection failure
```

Fix je zmeniť application bind na `:8080` alebo `0.0.0.0:8080`, ak má byť služba dostupná cez container interface. Pridanie ďalšieho Docker publish pravidla neodstráni chýbajúci listener.

## 8. Egress a masquerading

Keď bridge container komunikuje s externým endpointom, source private container address často nie je routovateľná mimo hosta. Docker host preto môže vykonať source NAT alebo masquerading.

```text
container 172.20.0.3
→ bridge
→ host routing a NAT
→ host external address
→ remote database alebo API
```

Remote peer vidí host alebo NAT address, nie priamo container address. Return traffic sa priradí k connection state-u a preloží späť.

Pri egress probléme kontroluj container route, host forwarding, firewall, NAT, proxy environment, DNS a remote allowlist. Ak remote service povoľuje iba konkrétne source IP, scale alebo presun workloadu na iný host môže zmeniť pozorovanú egress identity.

## 9. DNS má viac vrstiev

Container môže používať Docker embedded DNS pre service names a host-configured upstream resolvers pre externé domains. Query flow môže vyzerať:

```text
application resolver
→ /etc/resolv.conf v containere
→ Docker embedded DNS
→ host alebo configured upstream resolver
→ authoritative DNS
```

Pozri runtime konfiguráciu:

```bash
docker exec payments-api cat /etc/resolv.conf
```

Dočasný debug test:

```bash
docker run --rm --network atlas-backend alpine:3.22 \
  nslookup database.example.internal
```

DNS success nepreukazuje TCP reachability. DNS failure môže byť spôsobený chýbajúcim search domainom, nesprávnym project networkom, upstream outage, packet size/fragmentation problémom alebo rozdielnym IPv4/IPv6 výsledkom.

## 10. MTU a fragmentácia

Container interface a bridge musia používať MTU kompatibilnú s underlying network pathom. Overlay, VPN alebo cloud encapsulation môže znížiť dostupnú payload veľkosť. Ak Docker bridge používa príliš vysokú MTU, malé requesty prejdú a väčšie TLS alebo API responses môžu visieť.

Symptómy často vyzerajú zvláštne:

```text
TCP connect prejde
malý HTTP response prejde
väčší response alebo TLS handshake sa zastaví
```

Diagnostika používa packet capture, `tracepath`, vhodne nastavený `ping` s DF flagom a kontrolu interface MTU. Automatické znižovanie application timeoutov nie je oprava packet-size boundary.

## 11. Conntrack a port exhaustion

NAT a stateful firewall používajú connection tracking. Host s veľkým počtom krátkych spojení môže vyčerpať conntrack table alebo ephemeral ports. Containers potom hlásia sporadické timeouts, hoci target service je zdravá.

Pri takom incidente koreluj:

```text
application connection rate
host conntrack utilisation
TIME_WAIT a ephemeral port inventory
NAT gateway alebo firewall limits
retry amplification
```

Blind retry môže situáciu zhoršiť tým, že vytvorí ešte viac connections. Trvalá oprava môže zahŕňať connection pooling, keep-alive, bounded retries, kapacitnú zmenu alebo rozdelenie egress pathu.

## 12. Host network mode

Pri host network mode container nezíska samostatný network namespace rovnakým spôsobom; process používa host network stack.

```bash
docker run --rm --network host IMAGE
```

Port `8080` potom patrí host port space. Dva workloads na rovnakom hoste nemôžu jednoducho bindnúť rovnakú adresu a port. Port publishing flags nemajú rovnaký význam ako pri bridge mode.

Host networking môže znížiť niektoré translation vrstvy, ale oslabuje network isolation a zvyšuje coupling na host. Má byť vedomé architektonické rozhodnutie, nie univerzálna oprava network problému.

## 13. IPv4 a IPv6

Dual-stack prostredie pridáva ďalšie rozhodnutia. DNS môže vrátiť A aj AAAA record. Aplikácia môže bindnúť iba IPv4 alebo iba IPv6. Host a Docker network môžu mať rozdielnu IPv6 podporu.

Pri incidente zaznamenaj exact address family:

```bash
getent ahosts database.example.internal
curl -4 -v https://database.example.internal
curl -6 -v https://database.example.internal
```

Úspech cez IPv4 nepreukazuje IPv6 a opačne. „Connection refused“ na jednej family môže vzniknúť, aj keď hostname a port fungujú cez druhú.

## 14. Packet capture podľa vrstvy

Packet capture je najužitočnejší, keď presne vieš, na ktorom interface alebo namespace ho robíš.

```bash
# host bridge alebo physical interface
tcpdump -ni any port 8080
```

Pre container namespace možno použiť `nsenter` s host PID alebo debug tooling pripojený do rovnakého network namespace-u. Porovnaním captures možno určiť, či request prišiel na host, či bol preložený, či vstúpil do container namespace-u a či sa vrátil response.

Capture bez časovej korelácie a exact 5-tuple môže byť hlučný. Zachovaj source/destination address, ports, protocol, timestamp a container generation.

## 15. Incident: iba veľké payment responses zlyhávali

Po presune worker VM do VPN-connected subnetu začali malé health requesty fungovať, ale payment export s väčším TLS response timeoutoval. DNS, TCP connect a prvé TLS packets prešli.

Failure chain bol:

```text
container MTU 1500
→ VPN path efektívne podporuje menší payload
→ ICMP fragmentation-needed sa stráca
→ malé packets prejdú
→ väčšie TLS records sa opakovane retransmitujú
→ application timeout
```

Tím najprv podozrieval database a certificate. Packet capture však ukázal opakované retransmissions rovnakého segmentu. Oprava zosúladila Docker network MTU s underlying pathom a obnovila ICMP handling. Acceptance test zahŕňal malé aj veľké responses.

## 16. Incident: Compose service name fungoval, host port nie

Verifier service v rovnakej Compose network úspešne volala `http://payments-api:8080/readyz`, ale developer nedokázal otvoriť `http://localhost:18080`.

`docker compose config` ukázal správny publish model. `docker inspect` ukázal mapping na `127.0.0.1:18080`. Logs však uvádzali `listening on 127.0.0.1:8080` vo vnútri containeru.

Service-name test fungoval iba preto, že verifier bol omylom spustený s `network_mode: service:api`, takže zdieľal rovnaký network namespace a loopback. Neoveroval samostatnú service DNS cestu. Oprava odstránila shared network namespace, nastavila bind na `:8080` a pridala tri oddelené testy: local health, service DNS a host-published port.

## 17. Systematický network troubleshooting

Pri symptóme „container sa nevie pripojiť“ postupuj podľa packet pathu:

```text
application socket a bind/connect parameters
→ DNS result a address family
→ container interfaces a routes
→ Docker network membership
→ host bridge, forwarding a firewall
→ NAT/conntrack
→ physical alebo overlay path
→ remote listener a policy
→ return route
```

Praktické príkazy:

```bash
docker inspect CONTAINER
docker network inspect NETWORK
docker port CONTAINER
docker logs --timestamps CONTAINER
```

V debug kontexte:

```bash
ip address
ip route
ss -lntp
getent hosts NAME
curl -v URL
```

Najprv zachovaj evidence a exact container ID. Recreate môže zmeniť IP, veth, network namespace a conntrack state a tým odstrániť dôkaz pôvodnej chyby.

## Čo si z kapitoly odniesť

Container networking je reálny packet lifecycle. Aplikácia musí počúvať na správnej adrese, namespace musí mať interface a route, Docker network musí spájať správne endpoints a host dataplane musí packet povoliť, prípadne preložiť. DNS, port publishing a service discovery sú samostatné vrstvy.

Container IP je runtime identity, nie stabilný service contract. `EXPOSE` nepublikuje port. Zelený local healthcheck nepreukazuje service DNS ani host port. Pri troubleshooting-u sleduj request aj return path a rozlišuj bind address, DNS, route, firewall, NAT, conntrack, MTU a address family.

## Primárne zdroje

- [Docker networking overview](https://docs.docker.com/engine/network/)
- [Bridge network driver](https://docs.docker.com/engine/network/drivers/bridge/)
- [Port publishing](https://docs.docker.com/engine/network/port-publishing/)
- [Host network driver](https://docs.docker.com/engine/network/drivers/host/)
- [IPv6 with Docker](https://docs.docker.com/engine/daemon/ipv6/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Registries](registries.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Container storage →](container-storage.md)
<!-- KNOWLEDGE-NAVIGATION:END -->