# Container networking

Container networking je packet lifecycle medzi application socketom v network namespace, host dataplane-om a remote peerom. Nefunguje ako jedna abstraktná „Docker sieť“: každý packet prechádza konkrétnymi interfaces, routes, firewall/NAT states, service-discovery records a return pathom.

Dominantný model:

```text
application endpoint intent
→ socket bind a network-namespace identity
→ container address, route a neighbor state
→ veth/bridge alebo alternate dataplane
→ host forwarding, firewall a NAT
→ physical/overlay path
→ remote listener a policy
→ reverse path a conntrack
→ application protocol/readiness verification
```

Troubleshooting musí nájsť prvý observation point, na ktorom očakávaný flow prestal existovať alebo zmenil identity.

## 1. Atlas flow subject

Atlas Payments container `pay-07` poskytuje HTTPS API a volá database:

```text
image/platform digest: MAMD313
container runtime ID: CT-PAY-07
network namespace inode: NS-4401
container interface: eth0
container IP: 172.22.0.17/24
default gateway: 172.22.0.1
host veth: veth8ab1
bridge: br-atlas
published endpoint: 10.20.4.12:443 → 172.22.0.17:8443
application bind: 0.0.0.0:8443
database name: payments-db.internal
resolved endpoint: 10.40.8.21:5432
flow ID: TCP 172.22.0.17:51844 → 10.40.8.21:5432
```

Flow subject musí zachytiť:

- source namespace/interface/address/port;
- destination name/address/port/protocol;
- route a gateway;
- veth/bridge/dataplane identity;
- NAT/conntrack tuple;
- firewall/policy generation;
- DNS answer a freshness;
- timestamp a node identity.

## 2. Socket bind je prvá hranica

Application môže počúvať na:

```text
127.0.0.1:8443
172.22.0.17:8443
0.0.0.0:8443
[::]:8443
```

`127.0.0.1` patrí aktuálnemu namespace-u. Ak process počúva iba na container loopback, packet prichádzajúci cez `eth0` nemá matching listener.

Observation:

```bash
ss -lntup
```

Port metadata v image alebo deployment spec nepreukazuje listener. `EXPOSE 8443` nevytvára socket, firewall rule ani host publication.

## 3. Network namespace identity

Network namespace izoluje pohľad na:

- interfaces;
- addresses;
- routes;
- neighbor cache;
- sockets a ports;
- loopback;
- časť firewall/network state podľa implementácie.

Runtime namespace nemusí byť pomenovaný v `ip netns`. Identifikuj ho cez process:

```bash
readlink /proc/<pid>/ns/net
nsenter -t <pid> -n ip addr
nsenter -t <pid> -n ip route
nsenter -t <pid> -n ss -lntup
```

Container name alebo IP nie sú dostatočná dlhodobá identity. Po replacement-e sa namespace inode, veth a IP môžu zmeniť.

## 4. Interface, address a route

Packet odchádza iba ak namespace obsahuje:

```text
UP interface
+ valid source address
+ matching route
+ reachable next hop
```

Typický bridge model:

```text
container eth0
↔ veth pair
host veth
↔ Linux bridge
↔ host route/firewall/NAT
↔ uplink
```

Observation:

```bash
ip -br link
ip -br addr
ip route get 10.40.8.21
ip neigh
```

`ip route get` ukazuje effective source, interface a next hop pre konkrétny destination, nie iba statický zoznam routes.

## 5. Veth a bridge transition

Veth pair prenáša frame medzi namespace-mi. Host-side veth môže byť:

- pripojený k Linux bridge-u;
- routovaný priamo;
- spravovaný CNI/eBPF/overlay dataplane-om;
- odpojený alebo v nesprávnom bridge/networke.

Bridge rieši L2 forwarding. Nezaručuje L3 route, host forwarding, firewall acceptance ani remote return path.

Observation points:

```bash
ip -d link show
bridge link
bridge fdb show
```

Packet capture na container `eth0`, host veth, bridge a uplinku umožní určiť, medzi ktorými dvoma bodmi packet zmizol.

## 6. Port publishing

Port publishing vytvára host-side exposure contract:

```text
host bind address + host port + protocol
→ forwarding/NAT/proxy
→ container address + container port
```

Príklad:

```text
10.20.4.12:443/TCP
→ 172.22.0.17:8443/TCP
```

Rozlišuj:

- host bind `127.0.0.1`, konkrétnu IP alebo `0.0.0.0`;
- TCP a UDP;
- host firewall/security group;
- IPv4 a IPv6 publication;
- application listener address;
- source-IP preservation.

Publish na `0.0.0.0` môže vytvoriť širšiu exposure boundary než reverse proxy alebo operator očakával.

## 7. Host networking

Host network mode odstráni bežnú network-namespace boundary:

```text
container process
→ host interfaces, routes, sockets a port namespace
```

Dôsledky:

- port collision s hostom alebo iným host-network workloadom;
- širšia traffic visibility;
- priamy host firewall contract;
- `localhost` je host loopback;
- `CAP_NET_ADMIN` má výrazne väčší blast radius.

Použi ho iba pri explicitnom performance/tooling/lifecycle dôvode, nie ako univerzálnu opravu connectivity.

## 8. Outbound NAT a conntrack

Private container subnet často používa source NAT:

```text
original tuple:
172.22.0.17:51844 → 10.40.8.21:5432

translated tuple:
10.20.4.12:43122 → 10.40.8.21:5432
```

Conntrack uchováva mapping a protocol state pre reverse packet.

Failure boundaries:

- table exhaustion;
- NAT source-port exhaustion;
- stale entries;
- asymmetric return path;
- firewall verdict pred/po translation;
- short timeout voči application keepalive modelu.

External server môže vidieť node IP, nie container IP. Authorization založená na source IP preto musí rozumieť translation pathu.

## 9. Firewall a policy order

Verdict môže vzniknúť na viacerých boundaries:

```text
container namespace policy
→ bridge/forward chain
→ engine-managed chains
→ host firewall
→ cloud security control
→ remote host/service policy
```

Ručné pravidlo v jednej chain-e nedokazuje effective policy. Container engine môže vytvárať alebo meniť iptables/nftables state.

Zaznamenaj:

- packet direction;
- pre-NAT a post-NAT tuple;
- interface pair;
- chain/hook priority;
- policy generation;
- counter/log verdict.

IPv4 allow a IPv6 default-allow môžu vytvoriť policy bypass.

## 10. DNS resolution subject

DNS query v containeri má vlastný lifecycle:

```text
application resolver behavior
→ /etc/resolv.conf a search/ndots
→ embedded/host/enterprise resolver
→ authoritative/cache answer
→ selected A/AAAA endpoint
→ connection attempt
```

DNS subject obsahuje:

- queried name;
- effective search expansion;
- resolver IP;
- record type;
- answer a TTL;
- cache generation;
- selected address;
- timestamp.

DNS success neznamená service readiness. Service discovery navyše potrebuje endpoint eligibility, stale removal a stable identity.

## 11. Service discovery a endpoint lifecycle

Dynamický workload nemá používať jednu ephemeral container IP ako dlhodobý contract.

Service lifecycle:

```text
container created
→ readiness verified
→ endpoint published
→ traffic eligible
→ draining
→ endpoint removed
→ container deleted
```

Failure môže nastať, keď DNS alebo registry obsahuje:

- endpoint pred readiness;
- terminated IP;
- IP recyklovanú inému workloadu;
- unhealthy endpoint;
- subset z nesprávneho environmentu.

Name-to-IP mapping je iba jedna časť service discovery.

## 12. East-west, north-south a egress

Rozlišuj flow classes:

- **north-south ingress** — externý klient → workload;
- **north-south egress** — workload → externý systém;
- **east-west** — workload → interný service;
- **control-plane** — runtime/orchestrator/registry/secret API;
- **infrastructure** — DNS, time, metadata, telemetry.

Každá class potrebuje explicitný source, destination, protocol, identity a policy owner.

Default-allow east-west zväčšuje lateral-movement blast radius. Egress allowlist musí riešiť DNS/CDN volatility, nie iba statické IP.

## 13. Cloud metadata exposure

Container s node egressom môže dosiahnuť cloud metadata endpoint. Application compromise sa potom môže zmeniť na credential theft.

Controls:

- workload identity namiesto node credentialu;
- metadata endpoint policy/hop limits podľa platformy;
- network deny alebo proxy boundary;
- short-lived scoped credentials;
- audit token issuance/use.

`169.254.x.x` je network path a identity boundary, nie nevinná link-local adresa.

## 14. IPv4, IPv6 a dual stack

Dual-stack flow môže vybrať inú family než operator testoval.

Over:

```text
A/AAAA answer
→ application address selection
→ namespace route
→ firewall/NAT parity
→ remote listener
→ return path
```

Application môže počúvať na IPv6 `::`, ale nie na IPv4 podľa socket/kernel settings. Test `curl localhost` nemusí reprezentovať external family.

## 15. MTU a PMTU

Každá encapsulation layer znižuje payload MTU:

```text
container interface
→ bridge/veth
→ overlay/VPN/tunnel
→ host uplink
→ remote path
```

Malý ping môže prejsť, zatiaľ čo TLS handshake, upload alebo database response zlyhá.

Observation:

```bash
ip link show
tracepath <destination>
ping -M do -s <size> <destination>
tcpdump
```

Blokované ICMP „packet too big“ môže rozbiť Path MTU Discovery a vytvoriť black-hole behavior.

## 16. Rootless networking

Rootless runtime môže používať user-space stack alebo helper process namiesto bežného privileged host dataplane-u.

To mení:

- source IP visibility;
- throughput/latency;
- port binding;
- MTU;
- IPv6 support;
- packet capture observation points;
- failure ownership medzi processom a helperom.

Rootless connectivity sa nemá diagnostikovať automaticky rovnakým packet pathom ako rootful bridge.

## 17. Worked failure: application počúva iba na loopback

Atlas API v containeri hlási healthy pri internom `curl 127.0.0.1:8443`, ale host publication timeoutuje.

```text
host packet je DNATovaný na 172.22.0.17:8443
→ packet príde cez eth0
→ process počúva iba na 127.0.0.1
→ žiadny matching listener na eth0 address
```

Oprava je explicitný application bind contract, nie host networking alebo privileged mode.

## 18. Worked failure: port bol publikovaný na všetkých interfaces

Deployment mal byť dostupný iba cez local reverse proxy, no runtime použil `0.0.0.0:8443`.

```text
host publication vytvorí external listener
→ cloud firewall port povoľuje
→ klient obíde reverse proxy authentication/TLS policy
```

Security review musí porovnávať effective host bind a packet path, nie iba `EXPOSE` alebo application config.

## 19. Worked failure: DNS držalo terminated endpoint

Container `pay-04` bol odstránený a IP `172.22.0.14` bola pridelená debug workloadu. Stale service record stále smeroval traffic na túto IP.

```text
service name resolveuje syntakticky správne
→ IP identity bola recyklovaná
→ klient kontaktuje nesprávny workload
```

Service records potrebujú stable workload identity, readiness generation a removal/TTL contract.

## 20. Worked failure: malé requests fungovali, veľké timeoutovali

Overlay MTU bola 1450, container interface 1500 a firewall blokoval potrebný ICMP feedback.

```text
small packets pass
→ large packet requires fragmentation/PMTU correction
→ ICMP feedback je dropped
→ TCP retransmits až do timeoutu
```

Recovery zahŕňa zosúladenie MTU alebo povolenie potrebného PMTU feedbacku, potom end-to-end large-payload test.

## 21. Worked failure: conntrack exhaustion

Atlas worker vytváral tisíce krátkych outbound connections bez pooling-u. Node conntrack table sa naplnila.

```text
existing flows continue
→ new SYN packets sú dropped
→ iba časť requests timeoutuje
→ application a remote service vyzerajú healthy
```

Observation musí spojiť node conntrack usage, drop counters, flow churn a application connection model.

## 22. Causal troubleshooting walkthrough: host dosiahne API, externý klient nie

`curl 172.22.0.17:8443` z node-u funguje. `curl https://api.example` zvonku timeoutuje.

### 1. Zafixuj flow subject

Zaznamenaj:

- external client source a DNS answer;
- load balancer/public IP a port;
- node IP a published bind;
- pre/post-NAT tuples;
- container namespace/IP/listener;
- bridge/veth identities;
- firewall/cloud-policy generations;
- captures/counters a return path.

### 2. Súťažiace hypotézy

1. Public DNS smeruje na zlý endpoint.
2. Load balancer/backend registration alebo health je nesprávny.
3. Host port nie je publikovaný.
4. Publication binduje iba `127.0.0.1` alebo inú node IP.
5. Host/cloud firewall blokuje ingress.
6. DNAT pravidlo smeruje na stale container IP.
7. Application listener alebo readiness sa zmenil medzi testami.
8. Return path je asymetrický.
9. IPv6 klient používa AAAA path bez parity.
10. MTU/TLS spôsobuje partial failure, nie L3 timeout.

### 3. Diskriminačné observation points

- authoritative DNS A/AAAA a client selection;
- LB listener/backend/health evidence;
- `ss` v host a container namespace;
- effective NAT/firewall rules a counters;
- packet captures na uplinku, host bind, bridge/veth a container eth0;
- conntrack original/reply tuples;
- container IP/runtime generation;
- remote/client TCP a TLS evidence.

### 4. Containment

Neotváraj všetky ports ani nevypínaj firewall. Zachovaj effective rules/counters a failed flow capture. Ak existuje bypass exposure, dočasne ho uzavri.

### 5. Recovery

- DNS/LB gap → oprav endpoint subject a verify health;
- bind mismatch → publish na intended node address;
- stale DNAT → reconcile runtime network state;
- firewall denial → pridaj narrow source/destination/protocol rule;
- return-path issue → oprav routing/NAT symmetry;
- IPv6 gap → zosúlaď dual-stack policy alebo odstráň nefunkčný record;
- MTU → oprav interface/tunnel MTU a PMTU behavior.

### 6. Over pôvodný outcome

Z externého reprezentatívneho clienta over DNS, TCP, TLS a business request. Potvrď container readiness, expected source identity, return flow a absence neplánovaného direct exposure.

### 7. Posuň control skôr

Pridaj effective-flow manifest, external synthetic test, IPv4/IPv6 parity gate, stale-endpoint test a packet-path observability s runtime generation.

## 23. Referenčné pravidlá

- Network troubleshooting začína application socketom a flow identity.
- `localhost` patrí aktuálnemu namespace-u.
- `EXPOSE` nie je listener, publication ani firewall rule.
- Bridge L2 forwarding nezaručuje L3 alebo policy reachability.
- Port publication má host bind, protocol a exposure boundary.
- NAT mení visible source identity a potrebuje reverse conntrack state.
- Effective firewall verdict závisí od hook/chain orderu a tuple view.
- DNS answer nie je service readiness.
- Ephemeral IP nie je dlhodobá workload identity.
- Dual stack potrebuje policy a listener parity.
- Malý ping nepreukazuje správnu MTU pre application flow.
- Existing connections môžu fungovať pri conntrack exhaustion nových flows.
- Rootless a rootful dataplane majú odlišné observation points.
- Host networking je boundary change, nie diagnostický shortcut.

## 24. Kontrolné otázky

1. Čo tvorí container flow subject?
2. Prečo listener na loopbacku nemusí fungovať cez veth?
3. Aké transitions spája veth a bridge?
4. Čo presne vytvorí port publishing?
5. Ako sa líši original a translated conntrack tuple?
6. Prečo DNS success nie je service-discovery success?
7. Ako stale endpoint a IP reuse vytvoria identity failure?
8. Prečo dual-stack failure môže byť selektívny?
9. Ako MTU a PMTU vytvoria partial connectivity?
10. Ktoré observation points lokalizujú external-ingress timeout?

## Glossary impact

Relevantné pojmy: container flow subject, network namespace identity, socket-bind boundary, veth transition, bridge dataplane, port-publication subject, pre-NAT tuple, post-NAT tuple, effective firewall verdict, DNS resolution subject, service endpoint generation, stale endpoint identity, metadata-service exposure, dual-stack parity, PMTU black hole, conntrack capacity boundary a rootless dataplane subject.

## Oficiálna dokumentácia

- [Docker networking overview](https://docs.docker.com/engine/network/)
- [Linux network namespaces](https://man7.org/linux/man-pages/man7/network_namespaces.7.html)
- [Linux bridge](https://docs.kernel.org/networking/bridge.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Registries](registries.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Container storage →](container-storage.md)
<!-- KNOWLEDGE-NAVIGATION:END -->