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

Ďalšie plánované kapitoly: ports a sockets, DNS, DHCP, NAT, firewally, proxy a reverse proxy, load balancing, HTTP, HTTPS/TLS/PKI, REST APIs, WebSockets a end-to-end network troubleshooting.

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
- diagnostikovať transportný timeout pomocou routes, sockets a packet capture.

## Stav

| Téma | Status | Úroveň |
|---|---|---|
| OSI a TCP/IP model | Learning | L2 |
| Ethernet, MAC a ARP | Learning | L2 |
| IPv4, IPv6 a subnetting | Learning | L2 |
| Routing a default gateway | Learning | L2 |
| TCP a UDP | Learning | L2 |
