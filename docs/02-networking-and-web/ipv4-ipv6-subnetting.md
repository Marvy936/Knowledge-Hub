# IPv4, IPv6 a subnetting

Po vyriešení lokálneho next hopu potrebuje Atlas klient správne IP adresy a prefixy. IP vrstva pomenúva routované endpoints a umožňuje, aby packet prešiel cez viac sietí. Prefix neurčuje iba „masku“; definuje, ktoré destinations sú priamo pripojené, ako sa agregujú routes a aký blast radius má broadcast alebo policy domain.

Dokumentačný scenár používa IPv4 `203.0.113.40` a IPv6 `2001:db8:100::40`. Obe adresy môžu patriť rovnakému hostname, ale vytvárajú nezávislé routes, neighbor state, firewall rules a failure modes.

## IPv4 adresa a prefix

Adresa `10.24.8.37/24` znamená, že prvých 24 bitov tvorí network prefix a zvyšok hostovú časť. Prefix `10.24.8.0/24` pokrýva adresy `10.24.8.0` až `10.24.8.255`. Tradične je prvá adresa network identifier a posledná directed broadcast; hosty typicky používajú adresy medzi nimi.

Kernel rozhoduje, či je destination on-link, podľa prefixu, nie podľa podobnosti textu. `10.24.9.10` nie je v `10.24.8.0/24`, hoci sa líši iba jedným oktetom, a packet preto smeruje cez route.

```bash
ip -4 addr show
ipcalc 10.24.8.37/24
ip route get 10.24.8.99
ip route get 10.24.9.10
```

Prvý `route get` typicky vyberie lokálny link, druhý gateway. Výstup je rozhodnutie konkrétneho kernelu s aktuálnymi rules a routes; nie je všeobecným tvrdením o celej sieti.

## Subnetting ako návrh hraníc

Prefix size určuje počet adries, ale subnetting nie je iba aritmetika. Prefixy ovplyvňujú sumarizáciu rout, fault domain, DHCP scope, security policy a rast.

Atlas môže prideliť:

```text
10.24.8.0/24   branch-a clients
10.24.9.0/24   branch-a voice
10.24.10.0/24  branch-a infrastructure
```

Nadradený prefix `10.24.8.0/22` pokrýva `10.24.8.0` až `10.24.11.255` a môže byť sumarizovaný do core routingu. Sumarizácia znižuje počet rout, ale musí zodpovedať reálnej reachability. Ak jedna časť agregátu nie je dostupná cez rovnaký next hop, summary môže vytvoriť black hole.

Pri návrhu treba ponechať priestor na rast a vyhnúť sa prekrývaniu s cloud, VPN a partner networks. Overlap nevadí iba „na papieri“; znemožňuje jednoznačný route selection a často vedie k NAT workaroundom.

## IPv6 nie je väčší IPv4

IPv6 používa 128-bit addresses a bežne `/64` subnety pre host networks. Nemá broadcast; používa multicast a NDP. Router advertisement môže oznámiť prefix, default router a ďalšie flags. Host môže vytvoriť adresu cez SLAAC, DHCPv6 alebo statickú konfiguráciu.

```bash
ip -6 addr show
ip -6 route
ip -6 route get 2001:db8:100::40
```

Link-local `fe80::/10` adresa existuje nezávisle od globálnej reachability a používa sa pri neighbor a router discovery. Global unicast address bez default route alebo funkčného NDP neposkytuje end-to-end connectivity.

IPv6 extension headers, ICMPv6 a Path MTU Discovery sú súčasťou funkčného protokolu. Bezhlavé blokovanie ICMPv6 môže rozbiť neighbor discovery alebo prenos väčších packetov.

## Dual-stack selection

DNS môže vrátiť `A` aj `AAAA`. Klientský runtime potom vyberá address family a môže spúšťať pokusy paralelne alebo s krátkym oneskorením. Používateľ preto môže vidieť fungujúcu službu cez IPv4, hoci IPv6 path je pokazený, alebo naopak.

```bash
getent ahosts api.atlas.example
curl -4 --verbose https://api.atlas.example/
curl -6 --verbose https://api.atlas.example/
```

`curl -4` a `curl -6` sú diskriminačné testy. Bežný `curl` môže fallbacknúť a skryť jednu chybnú family. Zdravý browser výsledok preto nie je dôkazom, že obe address families fungujú.

## Prefix length a host assumptions

IPv4 host môže mať viac adries a routes; „local subnet“ nie je absolútna vlastnosť IP adresy. Rovnaké dve adresy môžu byť on-link pri `/16` a routované pri `/24`. Nesprávna maska vytvára asymetrické správanie: host sa pokúsi ARP-ovať destination, ktorú ostatní posielajú cez router.

```text
správne: 10.24.8.37/24 → 10.24.9.10 cez gateway
chybne:  10.24.8.37/16 → ARP pre 10.24.9.10 na lokálnom linku
```

Server môže byť dostupný z iných sietí, ale chybný host ho nikdy nepošle gatewayu. Route inspection na serveri tento client-local problém neodhalí.

## Incident: nový AAAA záznam

Atlas pridá IPv6 VIP `2001:db8:100::40` do DNS. Monitoring z datacentra je zelený, ale časť pobočiek hlási dlhý prvý request. IPv4 je funkčné, IPv6 route z pobočiek chýba. Klienti najprv skúšajú AAAA a až po timeout-e použijú A.

Competing hypotheses zahŕňajú DNS latency, TLS rozdiel, broken IPv6 route a firewall. `dig` potvrdí oba records, ale nie reachability. `curl -6` zlyhá pred TCP handshakeom, `ip -6 route get` ukáže chýbajúcu route a packet capture neukáže použiteľný return path.

Containment môže dočasne odstrániť AAAA iba vtedy, keď je jasný TTL a cache dopad. Autoritatívna oprava doplní IPv6 routing, firewall a monitoring z reprezentatívnych pobočiek. Po oprave sa overia obe families a bežný klientský selection behavior.

## Zhrnutie

IP adresa bez prefixu, route a address-family kontextu je neúplná. Subnetting určuje on-link hranice, sumarizáciu a policy domains. IPv4 a IPv6 sú samostatné dataplanes a dual-stack klient môže skryť chybu fallbackom. Diagnostika preto testuje konkrétnu family, source address a route.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Ethernet, MAC a ARP](ethernet-mac-arp.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Routing a default gateway →](routing-and-default-gateway.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
