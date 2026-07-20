# Networking and Web Fundamentals

Táto sekcia rozširuje Linux packet-path základ na všeobecné sieťové modely, adresovanie, routing, transportné a aplikačné protokoly. Cieľom je vedieť sledovať request od lokálneho socketu cez link, routované siete, middleboxes, TLS a aplikačný server.

## Predpoklady

Odporúča sa najprv dokončiť [Linux and Systems](../01-linux-and-systems/README.md), najmä Linux networking, namespaces, cgroups a performance troubleshooting.

## Odporúčané poradie

1. [OSI a TCP/IP model](osi-and-tcp-ip-model.md)
2. [Ethernet, MAC a ARP](ethernet-mac-arp.md)
3. [IPv4, IPv6 a subnetting](ipv4-ipv6-subnetting.md)
4. [Routing a default gateway](routing-and-default-gateway.md)
5. [TCP a UDP](tcp-and-udp.md)
6. [Ports a sockets](ports-and-sockets.md)
7. [DNS](dns.md)
8. [DHCP](dhcp.md)
9. [NAT](nat.md)
10. [Firewally](firewalls.md)

Ďalšie plánované kapitoly: proxy a reverse proxy, load balancing, HTTP, HTTPS/TLS/certificates/PKI, REST APIs, WebSockets a end-to-end network troubleshooting.

## Cieľ zvládnutia

Po dokončení sekcie má byť možné:

- používať OSI/TCP-IP model ako diagnostickú mapu bez mechanického zjednodušovania,
- vysvetliť Ethernet frame forwarding, VLAN broadcast domains a ARP neighbor resolution,
- počítať IPv4 prefixes a navrhovať sumarizovateľný address plan,
- rozlíšiť IPv4 a IPv6 addressing, NDP, SLAAC a dual-stack failure modes,
- interpretovať routing table, longest-prefix match, default route a policy routing,
- analyzovať forward a return path vrátane asymetrie,
- vysvetliť TCP handshake, reliability, flow a congestion control,
- rozlíšiť TCP byte stream od UDP datagram semantics,
- rozlíšiť port, listening socket, accepted socket a konkrétny network flow,
- diagnostikovať bind address, ephemeral port exhaustion, listen queues a namespace-local sockets,
- sledovať DNS resolution od stub resolvera cez recursive cache po authoritative zone,
- interpretovať TTL, negative caching, split-horizon DNS, DNSSEC a transport cez UDP/TCP,
- analyzovať DHCP lease lifecycle, relay, options, address conflicts a DHCPv6/SLAAC interakciu,
- sledovať SNAT, DNAT, PAT a conntrack state vrátane return pathu a port exhaustion,
- rozlíšiť NAT od firewall policy,
- navrhnúť stateful alebo stateless firewall rules s least privilege a bezpečným rolloutom,
- diagnostikovať transportný timeout pomocou routes, sockets, firewall counters a packet capture.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| OSI a TCP/IP model | Learning | L2 |
| Ethernet, MAC a ARP | Learning | L2 |
| IPv4, IPv6 a subnetting | Learning | L2 |
| Routing a default gateway | Learning | L2 |
| TCP a UDP | Learning | L2 |
| Ports a sockets | Learning | L2 |
| DNS | Learning | L2 |
| DHCP | Learning | L2 |
| NAT | Learning | L2 |
| Firewally | Learning | L2 |
