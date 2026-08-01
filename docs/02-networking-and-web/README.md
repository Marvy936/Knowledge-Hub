# Networking and Web Fundamentals

Táto sekcia vysvetľuje sieť ako jednu súvislú cestu requestu, nie ako zbierku izolovaných protokolov. Celým výkladom prechádza klient z pobočky Atlas, ktorý odosiela `POST /v1/orders` na `https://api.atlas.example`. Request musí získať adresu cez DNS, nájsť lokálny next hop, prejsť routovanou sieťou, firewallom a NAT-om, vytvoriť transportné spojenie, overiť TLS identitu, prejsť load balancerom a reverse proxy a napokon vytvoriť objednávku `ord-8421`.

Spoločný scenár používa dokumentačné adresy, aby sa nedali zameniť za reálnu produkčnú konfiguráciu:

```text
klient:              10.24.8.37
lokálny gateway:     10.24.8.1
recursive DNS:       10.24.0.53
API IPv4 VIP:        203.0.113.40
API IPv6 VIP:        2001:db8:100::40
reverse proxy:       10.50.0.10
orders-api backendy: 10.60.1.21:8080 a 10.60.1.22:8080
hostname:             api.atlas.example
request ID:           req-7f31
```

Cieľom nie je memorovať sedem OSI vrstiev alebo zoznam portov. Čitateľ má vedieť určiť, ktorý packet, flow, connection, TLS session alebo HTTP request práve sleduje, kde je jeho authoritative observation point a čo daný dôkaz ešte nepreukazuje. DNS odpoveď nepreukazuje route, úspešný TCP handshake nepreukazuje TLS identitu, HTTP `200` nepreukazuje správny business outcome a zelený backend health check nepreukazuje, že request prešiel rovnakou cestou ako používateľ.

## Authoritative poradie kapitol

1. [OSI a TCP/IP model](osi-and-tcp-ip-model.md)
2. [Ethernet, MAC a ARP](ethernet-mac-arp.md)
3. [IPv4, IPv6 a subnetting](ipv4-ipv6-subnetting.md)
4. [Routing a default gateway](routing-and-default-gateway.md)
5. [TCP a UDP](tcp-and-udp.md)
6. [Porty a sockety](ports-and-sockets.md)
7. [DNS](dns.md)
8. [DHCP](dhcp.md)
9. [NAT](nat.md)
10. [Firewally](firewalls.md)
11. [Proxy a reverse proxy](proxy-and-reverse-proxy.md)
12. [Load balancing](load-balancing.md)
13. [HTTP](http.md)
14. [HTTPS, TLS, certifikáty a PKI](https-tls-certificates-pki.md)
15. [REST API a WebSockety](rest-apis-and-websockets.md)
16. [Praktický sieťový projekt od namespace po HTTPS request](networking-practical-walkthrough.md)
17. [Network troubleshooting](network-troubleshooting.md)

Poradie sleduje reálnu cestu komunikácie. Najprv sa vytvorí analytická mapa vrstiev a lokálny Ethernet hop. Potom sa vyrieši adresovanie a route, transport a socket state, name resolution a dynamická konfigurácia hosta. NAT a firewall ukážu, ako middlebox mení alebo povoľuje flow. Proxy, load balancer, HTTP a TLS vysvetlia aplikačnú cestu a trust boundaries. REST a WebSocket kapitola uzavrie aplikačný kontrakt a dlhodobý channel. Praktický walkthrough všetky vrstvy zostaví a troubleshooting ich použije pri jednom preserve-first incidente.

## Výkladový štandard

Každá koncepčná kapitola najprv samostatne vysvetlí, čo protokol alebo mechanizmus je, aký problém rieši, ktoré identity a vrstvy stavu vlastní a ako funguje bez väzby na Atlas topológiu. Nasleduje jednoduchý neutrálny príklad a jasná hranica toho, čo daný dôkaz potvrdzuje. Až potom kapitola prejde k sekcii `Atlas scenár a praktické použitie`, kde sa model aplikuje na spoločný request, doplnia sa CLI, packet fields, konfigurácia, incident a recovery. Scenár je teda aplikáciou už vysvetleného modelu, nie jeho náhradou.

Odrážky zostávajú iba pri krátkom inventári fields, stavov alebo acceptance podmienok. Hlavný výklad nesú súvislé odseky. Incidenty používajú presnú flow identity, čas, direction a observation points; nekončia neurčitým záverom „bol problém v sieti“.

Sekcia dôsledne rozlišuje tieto identity:

```text
hostname a DNS answer
≠ IP packet a route
≠ transportný flow
≠ socket a process
≠ TLS peer identity
≠ HTTP request
≠ business operácia
```

Proxy alebo NAT môže medzi dvoma bodmi vytvoriť nové flow identities. HTTP/2 môže niesť viac request streams v jednom TCP spojení. Retry môže vytvoriť viac HTTP requestov pre jednu používateľskú operáciu. Pri diagnostike sa preto vždy viaže dôkaz na presný objekt a čas.

## Praktický walkthrough

Praktická kapitola vytvorí laboratórium na jednom Linux hoste:

```text
client namespace
→ client LAN bridge
→ edge router a firewall namespace
→ DNAT na TLS listener
→ HAProxy reverse proxy a load balancer
→ app network
→ dva Python orders-api backendy
```

Samostatný DNS namespace bude odpovedať na `api.atlas.test`. Lokálna CA podpíše serverový certifikát a klient vykoná HTTPS `POST`. Verification script skontroluje DNS, route, ARP, TCP/TLS, round-robin backends a business response. Potom sa reprodukuje backend, ktorého health zostáva zelený pri zlyhanom business path-e, a firewall allow pravidlo napísané pre nesprávnu pre-NAT identitu. Packet capture a nftables trace ukážu prvý chýbajúci transition.

Lab vyžaduje Linux s oprávnením `root` a nástroje `iproute2`, `nftables`, `dnsmasq`, `haproxy`, `openssl`, `curl`, `tcpdump`, `jq` a `python3`. Repository workflow overuje dokumentáciu a konzistenciu príkazov, ale lab nespúšťa proti kernelu. Skutočné `Verified` vyžaduje vykonanie positive aj failure paths na podporovanom Linux hoste.

## Čo má čitateľ po sekcii vedieť

Čitateľ má vedieť sledovať request od application callu po business výsledok a v každom kroku pomenovať source, destination, protocol, direction a state. Má rozumieť tomu, prečo sa MAC adresa mení po routovanom hope, ako longest-prefix match a source selection vytvoria route, prečo TCP reliability nie je aplikačná exactly-once garancia a prečo UDP neznamená „bez stavu“ v celej infraštruktúre.

Má vedieť odlíšiť stub resolver, recursive cache a authoritative server; vysvetliť TTL, negative caching a split-horizon DNS; sledovať DHCP lease a jeho options; diagnostikovať original a translated NAT tuple; čítať stateful firewall decision na správnom hooku a direction.

Na aplikačnej vrstve má vedieť rozlíšiť forward proxy, reverse proxy, L4 a L7 load balancing, TLS termination a re-encryption. Má rozumieť HTTP method semantics, caching, conditional requests, idempotency keys, API compatibility, WebSocket reconnectu a backpressure.

Pri incidente má začať presným používateľským symptómom, zachovať volatile evidence, rozložiť path na testovateľné transitions a vybrať observation point s najvyššou diskriminačnou hodnotou. Oprava sa uzatvára až overením pôvodného requestu, zakázaného flowu a business side effectu.

## Stav

Všetkých sedemnásť kapitol je po rewritingu pripravených na používateľskú kontrolu. Stav `Ready for user review` neznamená, že boli commands vykonané v každej platforme alebo že používateľ obsah akceptoval. Praktický lab a platformovo špecifické správanie zostávajú oddelenou runtime validation hranicou.
