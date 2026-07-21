# Docker networks a port publishing

Docker networking implementuje konkrétne runtime modely nad Linux network namespaces, virtual Ethernet interfaces, bridge-mi, routingom, firewallom a NAT-om. Docker network object určuje, ktoré containers zdieľajú connectivity a service-discovery boundary. **Port publishing** je samostatná operácia, ktorá sprístupní container port cez host address a port.

## 1. Network driver model

Docker Engine poskytuje network drivers, ktoré implementujú odlišné connectivity semantics.

Bežné drivers:

- `bridge` — single-host container network,
- `host` — container zdieľa host network namespace,
- `none` — bez bežnej external connectivity,
- `overlay` — multi-host network v podporovanom orchestration modeli,
- `macvlan` — container dostane L2 identity na parent networku,
- `ipvlan` — L2/L3 model zdieľajúci parent interface podľa režimu.

Driver je súčasťou network contractu. Rovnaký container image môže mať výrazne odlišné behavior podľa drivera.

## 2. Default bridge vs. user-defined bridge

Docker vytvára default `bridge` network. Pre application stack je spravidla vhodnejšia user-defined bridge network:

```bash
docker network create example-net

docker run -d --name db --network example-net postgres:17
docker run -d --name app --network example-net example:1
```

User-defined bridge poskytuje:

- explicitnú lifecycle identity,
- built-in DNS resolution medzi containers,
- jednoduchšie network isolation,
- configurable subnet/gateway/options,
- možnosť pripájať/odpájať containers.

Default bridge často vedie k implicitnejšej a menej čitateľnej konfigurácii.

## 3. Container DNS

Na user-defined networke môže container typicky resolve-nuť iný container podľa mena alebo network aliasu.

```bash
docker run --name db --network example-net postgres:17
```

Application sa pripája na:

```text
db:5432
```

Nie na host-published port.

Service discovery potrebuje stabilnú logical identity. Container IP je runtime detail a môže sa po replacement-e zmeniť.

## 4. Network aliases

```bash
docker network connect --alias database example-net db
```

Alias poskytuje ďalšie DNS meno v konkrétnej network boundary.

Riziká:

- collision aliasov,
- viac odpovedí pri replicas,
- stale application connection pools,
- nejasný ownership mena.

Alias nie je globálny DNS record; patrí ku konkrétnej Docker network.

## 5. Container port

Container port je port, na ktorom process počúva vo svojom network namespace.

```text
application → 0.0.0.0:8080 vo vnútri containeru
```

Process musí počúvať na vhodnej adrese. Ak počúva iba na `127.0.0.1` v container namespace, traffic prichádzajúci cez container interface ho nemusí dosiahnuť.

`EXPOSE 8080` v Dockerfile iba dokumentuje port metadata. Nevykonáva publishing.

## 6. Port publishing

```bash
docker run -p 8080:80 nginx
```

Zápis znamená:

```text
HOST_PORT:CONTAINER_PORT
8080      → 80
```

Traffic na host port `8080` je forwarded na container port `80`.

Toto je rovnaký princíp ako pri:

```bash
docker run --rm -p 8080:80 marvy936/knowledge-site:latest
```

Aplikácia je dostupná na hoste cez port `8080`, zatiaľ čo web server v containeri počúva na porte `80`.

## 7. Bind address

```bash
docker run -p 127.0.0.1:8080:80 nginx
```

Publikuje iba na host loopback.

```bash
docker run -p 0.0.0.0:8080:80 nginx
```

Publikuje na všetkých IPv4 interfaces.

Pri skrátenom zápise bez host IP Docker typicky bindne publikovaný port na všetky host interfaces podľa daemon/network configuration.

Pre local-only službu explicitne používaj loopback address. Firewall zostáva ďalšou vrstvou, nie náhradou správneho bind scope-u.

## 8. Náhodný host port

```bash
docker run -p 80 nginx
```

Docker môže vybrať ephemeral host port.

Zistenie mappingu:

```bash
docker port <container>
docker ps
```

Tento model je vhodný pre test isolation, ale caller potrebuje discovery mechanizmus.

## 9. `-P` a `EXPOSE`

```bash
docker run -P image
```

`-P` publikuje všetky exposed ports na náhodné host ports.

Riziko:

- nejasná exposure,
- neočakávané otvorenie management portu,
- zlá auditovateľnosť.

V production preferuj explicitné mappings.

## 10. Publishing nie je potrebný pre container-to-container traffic

Containers v rovnakej network sa pripájajú priamo na container port:

```text
app → db:5432
```

Host publishing:

```text
host/external client → host:15432 → db:5432
```

Application container nemá používať host-published database port, ak existuje priama internal network cesta. Zbytočne by prechádzal NAT/host boundary a vytváral coupling.

## 11. Bridge datapath

Zjednodušený user-defined bridge model:

```text
container process
  ↓ container interface
veth pair
  ↓
Linux bridge
  ↓
host routing/firewall/NAT
  ↓
external network
```

Port publishing pridáva forwarding/NAT alebo proxy behavior podľa platformy a konfigurácie.

Pri troubleshooting sleduj celý packet path, nie iba container IP.

## 12. Firewall a NAT

Docker Engine na Linuxe spravuje pravidlá pre:

- bridge isolation,
- outbound masquerading,
- published ports,
- forwarding medzi interfaces.

Host firewall tooling a Docker-managed rules môžu interagovať neočakávane.

Potrebné je rozumieť:

- input vs. forward path,
- pre-routing a destination NAT,
- source NAT/masquerade,
- Docker-specific chains alebo nftables backendu,
- host policy aplikovanej pred/po Docker rules.

Nevkladaj firewall pravidlá naslepo bez overenia skutočného backendu a packet pathu.

## 13. Direct routing

Niektoré topológie môžu routovať priamo na container addresses bez NAT-u, ak host a upstream network poznajú route a Docker configuration to povoľuje.

Výhody:

- zachovanie source address,
- menej NAT state-u,
- jednoduchší east-west routing v kontrolovanej sieti.

Riziká:

- širšia exposure container subnetu,
- route propagation,
- firewall policy complexity,
- IP lifecycle coupling.

Direct routing nie je automaticky bezpečnejší ani jednoduchší.

## 14. Host network mode

```bash
docker run --network host example:1
```

Container zdieľa host network namespace.

Dôsledky:

- bez samostatnej container IP,
- process binduje priamo host ports,
- port collision s host services,
- menšia network isolation,
- `-p` mapping stráca bežný význam.

Používaj iba pri opodstatnenom performance alebo network requirement-e a s vedomým security modelom.

## 15. `none` network

```bash
docker run --network none example:1
```

Container má minimálny network namespace, typicky iba loopback.

Vhodné pre:

- offline batch processing,
- artifact conversion,
- security-sensitive workload bez network dependency,
- test, ktorý overuje absence egressu.

Stále môže komunikovať cez mounted sockets, shared filesystem alebo host devices, ak sú sprístupnené.

## 16. Macvlan a ipvlan

### Macvlan

Container môže mať vlastnú MAC identity na physical networku.

### Ipvlan

Viac endpoints môže zdieľať parent MAC a používať samostatné IP podľa režimu.

Trade-offy:

- upstream switch/port policy,
- host-to-container connectivity caveats,
- DHCP/IPAM ownership,
- observability,
- L2 scale,
- cloud network restrictions.

Tieto drivers nepoužívaj iba preto, aby container „vyzeral ako VM“.

## 17. IPv4 a IPv6

Docker network môže mať IPv4, IPv6 alebo dual-stack configuration podľa Engine a host podpory.

Over:

- subnet a gateway,
- daemon IPv6 settings,
- host routes,
- DNS records,
- application listen addresses,
- firewall rules pre obe families,
- published-port behavior.

`0.0.0.0` je IPv4 unspecified address; `::` je IPv6 unspecified address. Dual-stack behavior závisí od application socket options a platformy.

## 18. MTU

Container packet môže prechádzať:

- veth,
- bridge,
- host uplink,
- VPN,
- overlay/tunnel,
- cloud network.

Nesprávna MTU môže spôsobiť:

- fungujúci ping, ale zlyhanie veľkých requests,
- TLS handshake timeout,
- partial downloads,
- retransmissions,
- problémy iba cez VPN/overlay.

Diagnostika:

```bash
ip link
ip route
ping -M do -s <size> <target>
tracepath <target>
```

## 19. Conntrack a ephemeral ports

NAT a stateful firewall používajú connection tracking. Pri vysokom počte flows môžu zlyhať:

- conntrack table,
- ephemeral source ports,
- NAT mappings,
- timeout policy.

Symptómy:

- nové spojenia padajú,
- existujúce fungujú,
- problém rastie s concurrency,
- restart dočasne pomôže.

Sleduj host kernel metrics, nie iba container logs.

## 20. DNS troubleshooting

Pri zlyhaní DNS over:

```bash
docker network inspect example-net
docker exec <container> cat /etc/resolv.conf
docker exec <container> getent hosts db
```

Rozlišuj:

- Docker embedded DNS,
- upstream DNS,
- search domains,
- container alias,
- application DNS cache,
- stale persistent connections,
- split-horizon alebo VPN DNS.

Používanie pevnej container IP obchádza discovery a zvyšuje coupling.

## 21. Compose networks

```yaml
services:
  app:
    image: example:1
    networks:
      - frontend
      - backend
    ports:
      - "127.0.0.1:8080:8080"

  db:
    image: postgres:17
    networks:
      - backend

networks:
  frontend:
  backend:
    internal: true
```

`db` nie je v `frontend` network. `backend` môže byť označený ako internal podľa požadovaného egress modelu.

Network segmentation má nasledovať communication graph, nie iba convenience.

## 22. Security

Controls:

- explicitné user-defined networks,
- minimálny počet pripojených networks,
- loopback-only publishing pre local services,
- firewall a network policy,
- žiadny host network bez potreby,
- TLS/mTLS na application vrstve,
- krátkodobé workload identities,
- egress control a DNS observability.

Container network isolation nie je automaticky tenant-grade boundary.

## 23. Anti-patterny

### Všetky služby v jednej default network

Zväčšuje lateral movement a nejasný communication graph.

### Application používa `localhost` pre inú službu

`localhost` označuje rovnaký network namespace, nie susedný container.

### Publikovanie databázy na `0.0.0.0`

Zbytočne ju vystaví všetkým host interfaces.

### Používanie container IP ako stabilnej identity

IP sa môže po replacement-e zmeniť.

### `EXPOSE` považovaný za publishing

Nevytvára host mapping.

### Host network ako oprava každého connectivity problému

Odstráni isolation bez pochopenia príčiny.

### Firewall kontrolovaný iba cez host `INPUT`

Published traffic môže prechádzať forwarding/NAT pathom.

## 24. Troubleshooting

### Port je publikovaný, ale connection zlyhá

Over:

- process počúva,
- správny container port,
- bind address vo vnútri containeru,
- host bind address,
- firewall/NAT,
- application health.

### Funguje na hoste, ale nie z iného stroja

Over host bind `127.0.0.1` vs. `0.0.0.0`, host firewall, route a upstream security group.

### Container nevie resolve-nuť service name

Over, či sú oba containers v rovnakej user-defined network a či alias existuje.

### `address already in use`

Host port už vlastní iný process/container alebo application v host-network mode.

### Fungujú malé requests, veľké timeoutujú

Over MTU, fragmentation/PMTUD, VPN/overlay a firewall ICMP handling.

### Náhodné connection failures pri load-e

Over conntrack, ephemeral ports, backlog, DNS cache a resource limits.

## 25. Kontrolné otázky

1. Aký je rozdiel medzi Docker network a port publishingom?
2. Prečo je user-defined bridge vhodnejší než default bridge?
3. Prečo má application používať service name namiesto container IP?
4. Čo znamená `-p 8080:80`?
5. Ako obmedzíš published port iba na localhost?
6. Prečo containers v rovnakej network nepotrebujú host-published port?
7. Čo sa mení pri host network mode?
8. Ako Docker networking súvisí s firewallom a NAT-om?
9. Ako sa prejavuje MTU problém?
10. Ktoré host resources môžu limitovať veľký počet spojení?

## Glossary impact

Relevantné pojmy: Docker network, network driver, default bridge, user-defined bridge, Docker embedded DNS, network alias, Docker port publishing, host bind address, random host port, direct routing, Docker host network, Docker none network, macvlan, ipvlan a Docker internal network.

## Oficiálna dokumentácia

- [Docker networking overview](https://docs.docker.com/engine/network/)
- [Port publishing and mapping](https://docs.docker.com/engine/network/port-publishing/)
- [Bridge network driver](https://docs.docker.com/engine/network/drivers/bridge/)
- [Docker container run](https://docs.docker.com/reference/cli/docker/container/run/)
