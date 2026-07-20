# DNS

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [Ports a sockets](ports-and-sockets.md), [IPv4, IPv6 a subnetting](ipv4-ipv6-subnetting.md), [TCP a UDP](tcp-and-udp.md)
- Súvisiace témy: DHCP, HTTP, TLS, service discovery, load balancing, caching

## 1. Definícia

Domain Name System je distribuovaný hierarchický systém, ktorý mapuje mená na resource records a poskytuje ďalšie informácie potrebné na smerovanie služieb, autentifikáciu domén a delegáciu správy namespace.

DNS nie je iba „preklad názvu na IP“. Jedno meno môže mať viac typov záznamov, viac odpovedí a správanie závislé od resolvera, cache, lokality, času a policy.

## 2. Hierarchický model

Príklad mena:

```text
api.prod.example.com.
```

Hierarchia sa číta sprava:

```text
.                root
com.             top-level domain
example.com.     delegated zone
prod.example.com.
api.prod.example.com.
```

Koncová bodka označuje fully qualified domain name. Bez nej môže resolver pridať search suffix.

## 3. Hlavné komponenty

### Stub resolver

Knižnica alebo lokálna služba používaná aplikáciou. Typicky odovzdá query recursive resolveru.

### Recursive resolver

Prijme požiadavku klienta, používa cache a podľa potreby vykoná iteratívne queries cez DNS hierarchiu.

### Authoritative server

Poskytuje autoritatívne dáta pre konkrétnu zone. Nemusí vykonávať recursion.

### Zone

Administratívne spravovaná časť DNS namespace obsahujúca resource records a delegácie.

## 4. Resolution flow

Pri query na `api.example.com` môže resolver postupovať:

```text
client stub resolver
  ↓
recursive resolver cache miss
  ↓
root server: kto spravuje .com?
  ↓
.com server: kto spravuje example.com?
  ↓
authoritative server: aký je record api.example.com?
  ↓
recursive resolver cache
  ↓
client
```

V praxi cache často eliminuje väčšinu krokov.

## 5. Resource records

Bežné typy:

- `A`: IPv4 adresa,
- `AAAA`: IPv6 adresa,
- `CNAME`: alias na iné canonical meno,
- `MX`: mail exchanger,
- `NS`: authoritative nameserver pre zone,
- `SOA`: základné zone metadata,
- `TXT`: textové dáta, často policy alebo verification,
- `SRV`: service location vrátane portu a priority,
- `PTR`: reverse lookup,
- `CAA`: ktoré certificate authorities môžu vydávať certifikáty.

Príklad:

```dns
api.example.com. 300 IN A 192.0.2.20
api.example.com. 300 IN AAAA 2001:db8::20
```

## 6. CNAME a aliasing

`CNAME` hovorí, že meno je alias iného mena:

```dns
www.example.com. 300 IN CNAME frontend.example.net.
```

Resolver následne potrebuje získať address records canonical mena.

Dôležité obmedzenia:

- CNAME node typicky nemá zároveň iné bežné records,
- zone apex historicky nemôže byť klasický CNAME, preto provideri používajú ALIAS/ANAME flattening ako proprietárnu alebo implementačnú funkciu,
- dlhé CNAME chains zvyšujú latency a failure surface.

## 7. TTL a caching

TTL určuje, ako dlho môže resolver cacheovať record.

```text
TTL 300 = cache najviac 5 minút
```

Trade-off:

- vysoké TTL znižuje query load a latency,
- nízke TTL urýchľuje zmenu, ale zvyšuje závislosť od authoritative infraštruktúry.

Zníženie TTL tesne pri incidente nevymaže existujúce cache entries. Zmenu TTL treba vykonať vopred a počkať na pôvodný TTL.

## 8. Negative caching

Aj neexistujúca odpoveď, napríklad `NXDOMAIN`, môže byť cacheovaná. Dĺžku ovplyvňujú SOA metadata a resolver policy.

Preto novo vytvorený record nemusí okamžite fungovať klientovi, ktorý predtým dostal negatívnu odpoveď.

## 9. Recursive vs. iterative query

Recursive query žiada server o finálnu odpoveď alebo chybu.

Iterative query môže vrátiť referral na ďalší server.

Nástroje:

```bash
dig api.example.com
dig +trace api.example.com
dig @1.1.1.1 api.example.com
```

`+trace` vykonáva iteratívnu cestu od rootu a nemusí presne simulovať lokálny recursive resolver, jeho cache ani split-horizon policy.

## 10. UDP, TCP a transport

DNS tradične používa UDP port 53 pre väčšinu queries. TCP sa používa napríklad pri:

- truncated odpovedi,
- zone transfers,
- väčších odpovediach,
- explicitnej policy.

EDNS rozširuje možnosti DNS cez UDP, vrátane väčšej veľkosti odpovede.

Firewall povoľujúci iba UDP/53 môže spôsobovať selektívne zlyhania pri fallbacku na TCP.

Šifrované varianty zahŕňajú DNS over TLS a DNS over HTTPS. Menia transport a pozorovateľnosť, nie základný DNS namespace model.

## 11. DNSSEC

DNSSEC pridáva kryptografické podpisy, ktoré umožňujú overiť autenticitu a integritu DNS dát cez chain of trust.

DNSSEC neposkytuje dôvernosť query ani automaticky nešifruje DNS traffic.

Typické records:

- `DNSKEY`,
- `DS`,
- `RRSIG`,
- `NSEC` alebo `NSEC3`.

Chybná rotácia keys alebo DS delegation môže spôsobiť `SERVFAIL` u validating resolverov, hoci authoritative server vracia dáta.

## 12. Split-horizon DNS

Rovnaké meno môže mať inú odpoveď podľa resolvera alebo siete:

```text
api.example.com → 10.0.0.20     interný resolver
api.example.com → 203.0.113.20  verejný resolver
```

Použitie:

- interné a externé endpointy,
- private cloud zones,
- geografické alebo policy-based odpovede.

Riziká:

- nejednotný troubleshooting,
- VPN a resolver ordering problémy,
- cache pollution,
- certifikát alebo routing mismatch.

## 13. Search domains a `ndots`

Resolver môže pri krátkom mene skúšať search suffixes.

Príklad:

```text
search prod.example.com svc.cluster.local
```

Query `db` môže viesť na:

```text
db.prod.example.com
db.svc.cluster.local
```

Nastavenie `ndots` ovplyvňuje, kedy sa meno najprv skúša ako relatívne a kedy ako absolute.

V kontajnerových platformách môže nevhodný `ndots` generovať veľa zbytočných queries a zvyšovať latency.

## 14. Linux resolver path

Bežná aplikácia môže používať NSS cestu:

```bash
getent ahosts api.example.com
```

Konfigurácie:

```text
/etc/nsswitch.conf
/etc/resolv.conf
/etc/hosts
```

Systém môže používať `systemd-resolved`, NetworkManager, lokálny caching resolver alebo container-specific DNS proxy.

Diagnostika:

```bash
resolvectl status
resolvectl query api.example.com
cat /etc/resolv.conf
getent hosts api.example.com
dig api.example.com
```

`dig` nemusí kopírovať rovnakú resolution path ako aplikácia. Môže obísť `/etc/hosts`, NSS moduly alebo application cache.

## 15. Load balancing cez DNS

Jedno meno môže vracať viac adries:

```dns
api.example.com. 60 IN A 192.0.2.10
api.example.com. 60 IN A 192.0.2.11
```

DNS však nevidí stav každého existujúceho spojenia a klienti môžu odpovede cacheovať odlišne.

DNS-based steering sa používa pre:

- geo routing,
- weighted odpovede,
- failover,
- multi-region entry points.

Nie je náhradou za connection-aware load balancer tam, kde potrebujeme per-request health a routing.

## 16. Reverse DNS

IPv4 reverse lookup používa `in-addr.arpa`, IPv6 `ip6.arpa`.

```bash
dig -x 192.0.2.20
```

PTR record neurčuje forward mapping automaticky. Forward a reverse records môžu byť spravované oddelene.

Reverse DNS je relevantné napríklad pre mail reputation, audit a niektoré access policy.

## 17. Delegation a glue records

Parent zone deleguje child zone cez NS records.

Ak nameserver child zone leží priamo v delegovanej zone, parent môže potrebovať glue address records, aby nevznikla kruhová závislosť.

Chybná delegácia môže fungovať z niektorých caches a zlyhávať pri cold resolution.

## 18. Typické response codes

- `NOERROR`: query bola spracovaná; odpoveď môže byť aj prázdna,
- `NXDOMAIN`: meno neexistuje,
- `SERVFAIL`: server nedokázal odpoveď zostaviť alebo validovať,
- `REFUSED`: server query odmietol,
- `FORMERR`: neplatná query.

`NOERROR` bez A/AAAA nie je to isté ako `NXDOMAIN`.

## 19. Diagnostický postup

Aplikácia nevie vyriešiť `api.example.com`:

```bash
getent ahosts api.example.com
resolvectl query api.example.com
dig api.example.com A
dig api.example.com AAAA
dig api.example.com CNAME
dig +trace api.example.com
```

Postup:

1. reprodukuj problém rovnakou cestou ako aplikácia,
2. zisti použitý resolver,
3. odlíš timeout, `NXDOMAIN`, `SERVFAIL` a prázdnu odpoveď,
4. over search suffix a absolute meno,
5. skontroluj cache a TTL,
6. over delegation a authoritative odpoveď,
7. skontroluj UDP aj TCP port 53,
8. over DNSSEC validáciu,
9. porovnaj interný a verejný resolver,
10. po resolution pokračuj routingom a aplikačnou diagnostikou.

## 20. Časté omyly

### „DNS funguje, lebo `ping` našiel IP“

To dokazuje iba určitú resolution path a ICMP test, nie dostupnosť cieľovej služby.

### „`dig` a aplikácia vždy používajú rovnaký resolver“

Nie. Aplikácia môže používať NSS, vlastnú cache alebo iný runtime resolver.

### „Nízky TTL znamená okamžitú zmenu“

Nie pre cache entries vytvorené pred znížením TTL.

### „DNSSEC šifruje DNS“

Nie. Overuje autenticitu a integritu dát.

### „CNAME presmeruje HTTP request“

Nie. DNS alias iba ovplyvní resolution; HTTP redirect je aplikačná odpoveď.

## 21. Kontrolné otázky

1. Aký je rozdiel medzi recursive a authoritative serverom?
2. Čo presne riadi TTL?
3. Prečo môže byť `NXDOMAIN` cacheovaný?
4. Aký je rozdiel medzi CNAME a HTTP redirectom?
5. Prečo DNS potrebuje aj TCP?
6. Čo DNSSEC chráni a čo nechráni?
7. Prečo `dig` nemusí reprodukovať správanie aplikácie?
8. Ako split-horizon DNS komplikuje troubleshooting?
9. Aký je rozdiel medzi `NOERROR` bez odpovede a `NXDOMAIN`?
10. Prečo DNS load balancing nie je connection-aware load balancing?
