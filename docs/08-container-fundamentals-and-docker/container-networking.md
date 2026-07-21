# Container networking

Container networking prepája process v network namespace s hostom, ostatnými containers a externými sieťami. Runtime môže vytvoriť samostatný namespace, virtual interfaces, bridge, routes, DNS configuration, NAT a firewall rules, ale konkrétny packet path závisí od zvoleného drivera, host networking stacku a orchestrátora.

## 1. Network namespace ako základ

Container s vlastným network namespace má vlastné:

- interfaces,
- IP adresy,
- routing table,
- neighbor cache,
- sockets a port namespace,
- loopback interface,
- časť firewall/network state podľa implementácie.

`127.0.0.1` alebo `localhost` označuje aktuálny namespace. Dva containers so samostatnými network namespaces nemajú spoločný loopback.

## 2. Veth pair

Bežný Linux container model používa virtual Ethernet pair:

```text
container namespace                host namespace

eth0  <==========================>  vethXYZ
```

Packet zapísaný na jeden koniec sa objaví na druhom. Host-side endpoint sa môže pripojiť k bridge, route table alebo špecializovanej dataplane vrstve.

Diagnostika:

```bash
ip link
ip netns list
ip -d link show
```

Runtime nemusí svoje namespaces pomenovať cez `ip netns`, preto sa často pracuje s process namespace cez `/proc/<pid>/ns/net` a `nsenter`.

## 3. Linux bridge model

Bridge funguje ako software L2 switch. Viac host-side veth interfaces môže byť pripojených k jednému bridge:

```text
container A eth0 ─ vethA ┐
                          ├─ bridge ─ host routing/NAT ─ external network
container B eth0 ─ vethB ┘
```

Bridge učí MAC addresses a forwarduje frames. L3 reachability potom závisí od IP subnetu, routes, forwarding a firewall/NAT pravidiel.

## 4. Default route

Container typicky dostane:

- IP adresu z runtime-managed subnetu,
- route do lokálneho subnetu,
- default gateway na bridge alebo host-side router.

Kontrola:

```bash
ip addr
ip route
ip neigh
```

Chýbajúci default route, nesprávny subnet alebo stale neighbor entry sa môže prejaviť ako všeobecný timeout.

## 5. NAT a masquerading

Private container subnety často používajú source NAT/masquerading pre outbound traffic:

```text
container source IP
→ host NAT
→ host/external source IP
```

NAT rieši address translation, nie application-level service discovery ani bezpečnostnú autorizáciu.

Dôsledky:

- external server môže vidieť host IP namiesto container IP,
- connection tracking spotrebúva state,
- port exhaustion môže obmedziť počet outbound connections,
- original source identity môže byť skrytá,
- packet capture treba robiť na viacerých interfaces.

## 6. Port publishing

Container process môže počúvať na port 8080 vo svojom namespace. Bez route alebo publish pravidla to neznamená, že je port dostupný na hoste.

Port publishing vytvorí host-side listener alebo NAT/forwarding rule:

```text
host 0.0.0.0:8080
→ containerIP:8080
```

Rozlišuj:

- container port,
- host published port,
- bind address,
- protocol TCP/UDP,
- firewall exposure.

Publikovanie na `127.0.0.1` má inú exposure boundary než `0.0.0.0`.

## 7. `EXPOSE` nie je firewall rule

Image metadata `EXPOSE` dokumentuje očakávaný listening port/protocol. Samo osebe nemusí:

- publikovať port,
- otvoriť host firewall,
- vytvoriť load balancer,
- garantovať, že application počúva.

Runtime networking configuration je samostatná vrstva.

## 8. Bind address aplikácie

Application môže počúvať:

- na `127.0.0.1` v container namespace,
- na konkrétnej container IP,
- na `0.0.0.0`,
- na IPv6 `::` podľa socket behavioru.

Ak application počúva iba na container loopback, port publish na container interface nemusí fungovať.

Kontrola:

```bash
ss -lntup
```

## 9. Host networking

Pri host network mode container zdieľa host network namespace.

Výhody:

- menej virtual networking vrstiev,
- priame host interfaces a ports,
- vhodné pre špecifické performance alebo network tooling prípady.

Riziká:

- port collisions,
- slabšia isolation,
- širšia visibility host trafficu,
- neplatí bežný container IP model,
- väčší blast radius pri `CAP_NET_ADMIN` alebo packet capture permissions.

## 10. None/isolated networking

Container môže bežať bez externého network interface, typicky iba s loopbackom. Je to vhodné pre offline batch alebo security-sensitive workloads, ktoré nepotrebujú network.

Application dependency na DNS, metadata service, licensing alebo telemetry sa v takomto režime prejaví explicitne a môže odhaliť skryté egress požiadavky.

## 11. DNS v containeri

Runtime typicky pripraví `/etc/resolv.conf`, `/etc/hosts` a hostname metadata. DNS môže smerovať:

- priamo na host resolver,
- na embedded runtime DNS,
- na orchestrator DNS service,
- na enterprise resolver.

Riziká:

- search domain rozširuje dotazy,
- `ndots` môže meniť poradie lookupov,
- stale service records,
- split DNS,
- DNS timeouty vyzerajú ako application latency,
- container restart môže zmeniť IP, ale service name zostáva stabilný.

## 12. Service discovery

Pri dynamických containers nepoužívaj ich krátkodobú IP ako dlhodobý application contract. Preferuj:

- runtime-managed DNS names,
- service abstraction,
- load balancer,
- registry/discovery systém,
- orchestrator service.

Service discovery musí riešiť readiness, stale endpoints a retry behavior, nielen name-to-IP mapping.

## 13. IPv4 a IPv6

Container networking môže používať IPv4, IPv6 alebo dual stack. Over:

- address allocation,
- routes,
- DNS A/AAAA behavior,
- firewall parity,
- NAT66/NAT64 alebo routed model,
- application listen addresses,
- MTU a path behavior.

„IPv6 enabled“ na hoste neznamená, že runtime network alebo application má správne IPv6 routes a policy.

## 14. MTU

Virtual encapsulation, VPN alebo overlay network môže znížiť efektívnu MTU. Nesúlad môže spôsobiť:

- fragmentáciu,
- dropped large packets,
- TLS handshake alebo upload failures,
- fungujúci ping s malým packetom, ale nefunkčné application requests.

Diagnostika:

```bash
ip link show
tracepath destination
ping -M do -s SIZE destination
```

Over MTU na container interface, bridge/veth, host uplinku a overlay/tunnel vrstve.

## 15. Conntrack

Stateful NAT a firewall používajú connection tracking. Pri vysokom connection churn môže nastať:

- conntrack table exhaustion,
- dropped new connections,
- vysoká CPU contention,
- dlhé timeouty stale entries.

Sleduj table usage, protocol states, NAT port range a application keepalive/pooling behavior.

## 16. Firewall rules

Container engine môže meniť host firewall cez iptables/nftables integration. Security model musí rozumieť:

- chain ordering,
- forwarding policy,
- published ports,
- host firewall manageru,
- direct-routing pravidlám,
- IPv4/IPv6 parity.

Ručné pravidlo môže byť prepísané alebo obídené engine-managed chainom. Overuj reálny packet path, nie iba očakávanú konfiguráciu.

## 17. East-west a north-south traffic

- **east-west** — traffic medzi workloads alebo internými services,
- **north-south** — traffic medzi workloadom a externým klientom/službou.

Policy sa môže líšiť:

- service-to-service allowlist,
- ingress exposure,
- egress restriction,
- metadata endpoint protection,
- DNS a time services,
- observability collectors.

Default allow east-west model zvyšuje lateral-movement risk.

## 18. Egress control

Outbound access nie je automaticky bezpečný. Container môže kontaktovať:

- internet,
- cloud metadata service,
- internal databases,
- control-plane APIs,
- registry alebo secret manager.

Egress policy má definovať destination, protocol, identity a DNS behavior. IP allowlist bez kontroly DNS/CDN volatility môže byť krehký.

## 19. Rootless networking

Rootless containers nemôžu vždy vytvárať rovnaké host networking primitives ako privileged daemon. Môžu používať user-space networking, slirp-style stack alebo helper processes.

Trade-offy:

- lepšia host privilege boundary,
- odlišný performance profil,
- port binding limitations,
- odlišná source IP visibility,
- MTU a protocol caveats.

## 20. Packet path troubleshooting

Postupuj po vrstvách:

1. application počúva na očakávanom address/porte,
2. container interface je UP,
3. IP a route sú správne,
4. neighbor/gateway funguje,
5. bridge/veth je pripojený,
6. host forwarding je aktívny,
7. firewall/NAT pravidlá zodpovedajú,
8. external route a return path fungujú,
9. DNS resolveuje správne,
10. application protocol/TLS je validný.

Užitočné nástroje:

```bash
ss
ip
nsenter
ping
tracepath
dig
curl
tcpdump
conntrack
nft
iptables
```

## 21. Troubleshooting scenáre

### Container dosiahne IP, ale nie hostname

Network route funguje, problém je DNS config, resolver reachability, search domain alebo application resolver behavior.

### Port funguje z hosta, nie zvonku

Over publish bind address, host firewall, external security group, route a return path.

### Connection funguje pre malé requesty, veľké timeoutujú

Over MTU, PMTU discovery, tunnel overhead a firewall blocking ICMP potrebný pre path discovery.

### Container nevie volať host service

`localhost` je container loopback. Použi explicitnú host route/address alebo podporovaný host-gateway model.

### Po reštarte sa zmenila IP

Container IP je runtime identity. Použi service discovery a názov, nie uloženú IP.

## 22. Kontrolné otázky

1. Čo izoluje network namespace?
2. Ako funguje veth pair a bridge?
3. Prečo `localhost` nie je host?
4. Čo robí port publishing?
5. Prečo `EXPOSE` neotvára port?
6. Aké riziká má host network mode?
7. Ako DNS a service discovery súvisia, ale nie sú totožné?
8. Ako MTU spôsobí partial connectivity?
9. Čo je conntrack exhaustion?
10. Ako postupovať pri packet-path diagnostike?

## Glossary impact

Relevantné pojmy: container network namespace, veth pair, Linux bridge, container subnet, port publishing, container port, host port, host network mode, embedded DNS, container service discovery, east-west traffic, north-south traffic, egress policy, conntrack, rootless networking a container MTU.

## Oficiálna dokumentácia

- [Docker networking overview](https://docs.docker.com/engine/network/)
- [Linux network namespaces](https://man7.org/linux/man-pages/man7/network_namespaces.7.html)
- [Linux bridge](https://docs.kernel.org/networking/bridge.html)
