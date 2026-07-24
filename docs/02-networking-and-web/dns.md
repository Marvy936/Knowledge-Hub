# DNS

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [Ports a sockets](ports-and-sockets.md), [IPv4, IPv6 a subnetting](ipv4-ipv6-subnetting.md), [TCP a UDP](tcp-and-udp.md)
- Súvisiace témy: DHCP, HTTP, TLS, service discovery, load balancing, caching

## 1. DNS nie je iba preklad mena na IP

Domain Name System je distribuovaný hierarchický databázový a query systém. Mapuje mená na resource records, deleguje správu častí namespace a poskytuje dáta pre service discovery, email routing, certificate policy, reverse lookup a ďalšie mechanizmy.

Jedno meno môže mať viac record types, viac hodnôt a odlišné odpovede podľa resolvera, lokality, času alebo policy. Výsledná IP adresa je iba jeden možný výstup resolution procesu.

## 2. Meno, label a fully qualified name

DNS meno sa skladá z labels oddelených bodkami:

```text
api.prod.example.com.
```

Hierarchia sa číta sprava:

```text
.                    root
com.                 top-level domain
example.com.         delegated zone
prod.example.com.    subdomain
api.prod.example.com. konkrétne meno
```

Koncová bodka označuje absolute fully qualified domain name. Bez nej môže resolver meno považovať za relatívne a dopĺňať search suffixes.

## 3. Namespace a zone nie sú to isté

DNS namespace je celý strom mien. Zone je administratívne spravovaný výsek tohto stromu, pre ktorý authoritative server poskytuje dáta.

Zone môže obsahovať subdomains bez toho, aby boli samostatnými zones. Nová zone vzniká až delegáciou cez NS records v parent zone.

```text
example.com zone
├── www.example.com
├── api.example.com
└── prod.example.com delegation
        ↓
    samostatná prod.example.com zone
```

## 4. Hlavné komponenty resolution pathu

- Application resolver API — aplikácia volá napríklad `getaddrinfo()` alebo používa vlastnú DNS knižnicu.
- Stub resolver — lokálna knižnica alebo daemon zostaví query a pošle ju nakonfigurovanému resolveru.
- Recursive resolver — hľadá finálnu odpoveď, používa cache a podľa potreby vykonáva iterative queries.
- Authoritative server — poskytuje dáta pre zone, za ktorú nesie autoritu.
- Registry hierarchy — root a TLD zones delegujú nižšie časti namespace.

Tieto role môžu bežať v samostatných procesoch alebo sa kombinovať v jednej službe, no ich zodpovednosti zostávajú odlišné.

## 5. Bežný resolution lifecycle

Pri query na `api.example.com` môže tok vyzerať takto:

```text
application
  ↓ getaddrinfo()
local stub / NSS
  ↓ query
recursive resolver
  ├── cache hit → odpoveď
  └── cache miss
        ↓ root referral
        ↓ .com referral
        ↓ example.com authoritative answer
        ↓ cache
application dostane výsledok
```

Cache môže existovať v aplikácii, runtime, OS daemon-e, recursive resolveri aj upstream forwarderi. „Vyčistil som DNS cache“ preto nie je úplná veta bez uvedenia konkrétnej vrstvy.

## 6. Recursive a iterative query

Recursive query žiada server, aby vrátil finálnu odpoveď alebo finálnu chybu. Klientský stub typicky posiela recursive query lokálnemu alebo organizačnému resolveru.

Iterative query môže vrátiť referral na server bližšie k autoritatívnej odpovedi. Recursive resolver používa iterative queries voči hierarchii, keď odpoveď nemá v cache.

```bash
dig api.example.com
dig +trace api.example.com
```

`dig +trace` ukáže iteratívnu hierarchiu, ale neprehráva presne cache, forwarding, split-DNS ani validation policy lokálneho resolvera.

## 7. Referral a delegation

Parent zone deleguje child zone cez NS records. Referral hovorí resolveru, ktoré authoritative servery majú byť kontaktované ďalej.

```dns
prod.example.com.  IN NS ns1.prod.example.com.
prod.example.com.  IN NS ns2.provider.net.
```

Delegation data existujú v parent zone, zatiaľ čo authoritative NS records child zone existujú aj v child zone. Nekonzistencia medzi nimi môže spôsobovať čiastočné alebo cache-dependent zlyhania.

## 8. Glue records

Ak nameserver delegovanej zone leží priamo pod touto zone, resolver by bez jeho adresy potreboval vyriešiť meno cez zone, ku ktorej sa ešte len snaží dostať.

```text
zone: example.com
NS:   ns1.example.com
```

Parent preto môže pridať glue A/AAAA record pre nameserver. Glue je bootstrap informácia, nie všeobecný náhradný authoritative record.

Chybný alebo zastaraný glue môže spôsobiť, že cold resolution zlyhá, hoci niektoré resolvery ešte fungujú z cache.

## 9. Resource record model

DNS odpoveď obsahuje resource record sets. Record set tvoria records rovnakého mena, typu a class.

- `A` — IPv4 address.
- `AAAA` — IPv6 address.
- `CNAME` — alias na canonical meno.
- `NS` — authoritative nameserver pre zone alebo delegation.
- `SOA` — zone metadata, serial, timers a negative-caching údaje.
- `MX` — mail exchanger s preference hodnotou.
- `TXT` — textové policy alebo verification dáta.
- `SRV` — service location vrátane priority, weight a portu.
- `PTR` — reverse mapping.
- `CAA` — policy pre certificate authorities.
- `HTTPS` alebo `SVCB` — service binding parametre podľa podporovaného ekosystému.

Record type je súčasť query. `A` a `AAAA` queries môžu mať odlišný výsledok alebo failure mode.

## 10. Answer, authority a additional sections

DNS message môže obsahovať viac sekcií:

- Answer — priama odpoveď na query.
- Authority — informácie o authoritative zone alebo referral.
- Additional — pomocné records, napríklad addresses nameserverov.

Resolver nesmie automaticky považovať každý additional record za rovnako dôveryhodný ako authoritative answer. Bailiwick a validation pravidlá obmedzujú, čo možno bezpečne cacheovať.

## 11. `A` a `AAAA` odpovede

Meno môže mať jednu alebo viac IPv4 a IPv6 adries:

```dns
api.example.com. 300 IN A    192.0.2.20
api.example.com. 300 IN A    192.0.2.21
api.example.com. 300 IN AAAA 2001:db8::20
```

Resolver spravidla vráti celý dostupný record set. Aplikácia potom používa vlastný address-family a connection-selection algoritmus.

Funkčný `A` record nekompenzuje nefunkčný `AAAA` record, ak klient preferuje IPv6.

## 12. CNAME resolution

CNAME označuje, že meno je alias iného mena:

```dns
www.example.com. 300 IN CNAME frontend.example.net.
```

Resolver musí pokračovať a získať potrebný record canonical mena. Odpoveď môže obsahovať CNAME aj finálny A/AAAA record, ak ich server alebo cache pozná.

Dôležité dôsledky:

- CNAME chain pridáva ďalšie resolution kroky a failure points.
- CNAME node typicky nemá súčasne iné bežné records.
- Klasický zone apex nemožno jednoducho nahradiť CNAME, preto provideri ponúkajú flattening alebo proprietárne ALIAS/ANAME mechanizmy.
- CNAME nemení HTTP URL ani neposiela redirect browseru.

## 13. MX a SRV nie sú obyčajné adresy

MX record smeruje mail delivery na hostname a používa preference. Klient musí následne vyriešiť A/AAAA records zvoleného exchangeru.

SRV record obsahuje service, protocol, priority, weight, port a target:

```dns
_sip._tcp.example.com. 300 IN SRV 10 20 5060 sip1.example.com.
```

Priority určuje preferenciu skupiny, weight rozdelenie v rámci rovnakej priority. Aplikácia musí SRV výslovne podporovať; bežný HTTP klient ho automaticky nepoužije.

## 14. TTL a cache lifetime

TTL určuje maximálny čas, počas ktorého môže resolver cacheovať record set bez novej authoritative query.

```text
TTL 300 → maximálne približne 5 minút cache lifetime
```

TTL je súčasť odpovede a v cache postupne klesá. Rôzne resolvery môžu mať policy pre minimálny alebo maximálny TTL, preto reálne správanie nemusí byť identické.

Trade-off:

- Vyšší TTL — menej queries, nižšia dependency load a lepšia odolnosť voči krátkemu authoritative výpadku.
- Nižší TTL — rýchlejšia budúca zmena, ale vyššia query záťaž a väčšia závislosť od resolver pathu.

## 15. Prečo zníženie TTL nefunguje spätne

Cache entry vytvorená pred znížením TTL si nesie pôvodný zostávajúci lifetime. Zmena authoritative TTL ju nevymaže z cudzích cache.

Bezpečný migration pattern:

1. Zníž TTL dostatočne vopred.
2. Počkaj aspoň pôvodný TTL a podľa prostredia aj ďalší buffer.
3. Zmeň record data.
4. Sleduj obe staré aj nové destinations počas prechodu.
5. Po stabilizácii TTL znovu zvýš.

## 16. Negative caching

Resolver môže cacheovať aj dôkaz neexistencie. `NXDOMAIN` alebo odpoveď bez požadovaného typu môže mať negative TTL odvodený zo SOA metadata a resolver policy.

Dôsledok:

```text
klient sa opýta príliš skoro
→ dostane NXDOMAIN
→ resolver cacheuje negatívnu odpoveď
→ record sa vytvorí
→ klient stále vidí NXDOMAIN do expirácie cache
```

Pri diagnostike nového recordu treba kontrolovať aj negative cache, nie iba positive TTL.

## 17. `NXDOMAIN` verzus NODATA

`NXDOMAIN` znamená, že queried name neexistuje. NODATA je bežne `NOERROR` odpoveď bez recordu požadovaného typu; meno môže existovať, ale napríklad nemá AAAA record.

```text
NXDOMAIN: api.example.com neexistuje
NODATA:   api.example.com existuje, ale nemá AAAA
```

Tento rozdiel ovplyvňuje caching, fallback a diagnostiku dual-stack problémov.

## 18. Response codes

- `NOERROR` — server query syntakticky a logicky spracoval; answer section môže byť prázdna.
- `NXDOMAIN` — queried name neexistuje podľa authoritative odpovede.
- `SERVFAIL` — server nedokázal odpoveď zostaviť alebo validovať; príčinou môže byť timeout, lame delegation alebo DNSSEC failure.
- `REFUSED` — server query podľa policy odmietol.
- `FORMERR` — message je neplatná alebo nepodporovaná.
- `NOTIMP` — server nepodporuje požadovanú operáciu.

Response code je klasifikácia resolvera, nie vždy priama root cause.

## 19. UDP transport

Väčšina klasických DNS queries používa UDP port `53`. Klient odošle query s transaction ID a čaká na odpoveď od resolvera.

UDP výhody:

- bez TCP handshakeu,
- malý per-query transportný overhead,
- jednoduchý request/response model.

UDP riziká:

- loss a retries,
- fragmentácia veľkých odpovedí,
- spoofing bez ďalších ochranných mechanizmov,
- socket-buffer alebo firewall drops.

Resolver musí mať timeout a retry policy a správne párovať response s query.

## 20. TCP transport

DNS používa TCP pri zone transfers, explicitnej policy alebo keď UDP odpoveď nestačí. TC flag v UDP response signalizuje truncation a klient môže query zopakovať cez TCP.

```bash
dig +tcp api.example.com
```

Firewall povoľujúci iba UDP/53 môže preto spôsobovať selektívne zlyhania: malé odpovede fungujú, väčšie alebo DNSSEC odpovede timeoutujú.

## 21. EDNS a veľkosť UDP odpovede

EDNS umožňuje klientovi oznámiť väčšiu prijateľnú UDP payload size a používať rozšírené flags. Väčšia odpoveď však zvyšuje riziko IP fragmentácie alebo dropu middleboxom.

Moderný resolver môže používať konzervatívnejšiu UDP veľkosť a prejsť na TCP. Diagnostika musí porovnať bežnú query, `+tcp`, veľkosť odpovede a packet capture.

## 22. DNS over TLS a DNS over HTTPS

DoT prenáša DNS v TLS spojení, typicky na samostatnom porte. DoH používa HTTPS transport a môže zdieľať bežnú webovú infraštruktúru.

Tieto mechanizmy poskytujú dôvernosť a integritu transportu medzi klientom a zvoleným resolverom. Nezaručujú správnosť authoritative dát a nemenia základný DNS namespace model.

Prevádzkovo menia:

- observation points,
- firewall a proxy policy,
- resolver selection,
- enterprise split-DNS integráciu,
- incidentné packet captures.

## 23. Stub resolver a NSS v Linuxe

Bežná aplikácia nemusí posielať DNS query priamo. `getaddrinfo()` môže používať Name Service Switch, ktorý kombinuje `/etc/hosts`, DNS, mDNS alebo directory service.

```text
/etc/nsswitch.conf
/etc/hosts
/etc/resolv.conf
```

```bash
getent ahosts api.example.com
getent hosts api.example.com
```

`getent` lepšie reprodukuje systémovú NSS cestu než samotný `dig`.

## 24. `/etc/resolv.conf` nemusí byť zdroj pravdy

`/etc/resolv.conf` môže byť generovaný symlink na systemd-resolved stub, NetworkManager konfiguráciu, DHCP údaje alebo container runtime DNS proxy.

```bash
ls -l /etc/resolv.conf
cat /etc/resolv.conf
resolvectl status
```

Súbor môže ukazovať `127.0.0.53`, zatiaľ čo skutočné upstream resolvery a per-interface domains sú uložené v resolved stave. Treba identifikovať manager, ktorý konfiguráciu vlastní.

## 25. Search domains a relative names

Resolver môže ku krátkemu menu pripojiť search suffixes:

```text
search prod.example.com svc.cluster.local
```

Query `db` môže vygenerovať viac kandidátov. Poradie ovplyvňuje `ndots`, resolver implementácia a absolute trailing dot.

```text
db
→ db.prod.example.com
→ db.svc.cluster.local
→ prípadne db.
```

Veľa search candidates zvyšuje latency, query volume a riziko, že krátke meno vyrieši neočakávaná zone.

## 26. `ndots` a Kubernetes

`ndots` určuje, koľko bodiek musí meno obsahovať, aby sa najprv skúšalo ako absolute candidate. Kubernetes často používa viac search suffixes a vyššie `ndots`, čo môže pre externé meno bez trailing dot generovať viac neúspešných interných queries.

Pri DNS latency v Pode treba skontrolovať:

```bash
cat /etc/resolv.conf
getent ahosts example.com
```

Aplikačný runtime môže navyše implementovať vlastnú cache a query strategy.

## 27. Split-horizon DNS

Rovnaké meno môže mať odlišné odpovede podľa resolver view:

```text
interný resolver: api.example.com → 10.0.0.20
verejný resolver: api.example.com → 203.0.113.20
```

Použitie:

- private endpoints,
- interné service names,
- region alebo geography steering,
- odlišné security boundaries.

Riziká:

- VPN klient používa nesprávny resolver,
- cache prežije prechod medzi sieťami,
- interná IP unikne do verejnej odpovede,
- certificate alebo routing policy nezodpovedá konkrétnemu view,
- troubleshooting tím testuje iný resolver než aplikácia.

## 28. Resolver forwarding

Organizačný resolver nemusí vykonávať recursion priamo. Môže queries forwardovať inému resolveru podľa zone alebo policy.

```text
client
→ local resolver
→ conditional forwarder pre corp.example
→ private authoritative DNS
```

Conditional forwarding je častý pri VPN, hybrid cloud a Active Directory prostrediach. Zlyhanie jedného forward targetu môže ovplyvniť iba konkrétnu zone.

## 29. Authoritative server a zone serial

SOA record obsahuje primary server, administrative contact, serial a refresh/retry/expire údaje pre secondary synchronization.

```dns
example.com. IN SOA ns1.example.com. hostmaster.example.com. (
  2026072401 ; serial
  3600       ; refresh
  600        ; retry
  1209600    ; expire
  300        ; negative caching
)
```

Ak secondary nevidí vyšší serial, nemusí načítať nové dáta. Chybná zone deployment pipeline môže preto vytvoriť nejednotné authoritative odpovede.

## 30. Lame delegation

Lame delegation nastane, keď parent odkazuje na nameserver, ktorý nie je autoritatívny pre delegovanú zone alebo ju nevie správne obslúžiť.

Symptómy:

- niektoré resolvery fungujú z cache,
- cold queries timeoutujú,
- odpovede závisia od vybraného NS,
- `SERVFAIL` sa objavuje prerušovane.

Treba testovať každý authoritative server priamo.

## 31. DNSSEC chain of trust

DNSSEC podpisuje record sets a umožňuje validating resolveru overiť autenticitu a integritu dát.

```text
root trust anchor
  ↓ DS/DNSKEY
TLD
  ↓ DS/DNSKEY
child zone
  ↓ RRSIG over record set
validated answer
```

Dôležité records:

- `DNSKEY` — verejné signing keys zone.
- `DS` — digest child key uložený v parent zone.
- `RRSIG` — podpis record setu.
- `NSEC/NSEC3` — kryptografický dôkaz neexistencie.

DNSSEC nešifruje query a neskrýva meno pred observerom.

## 32. DNSSEC failure semantics

Ak podpis, key alebo DS chain nesedí, validating resolver odpoveď odmietne a klient typicky vidí `SERVFAIL`. Non-validating test priamo na authoritative serveri môže pritom ukazovať správne-looking records.

Časté príčiny:

- DS v parent zone nezodpovedá aktívnemu child key,
- podpis expiroval,
- clock skew,
- key rotation nebola dokončená,
- veľká response zlyhá cez UDP/TCP path.

Pri diagnostike treba rozlíšiť authoritative data od validation výsledku.

## 33. Reverse DNS

IPv4 reverse zones používajú `in-addr.arpa`, IPv6 `ip6.arpa`. PTR record mapuje adresu na meno.

```bash
dig -x 192.0.2.20
```

Forward a reverse mapping sú nezávislé. PTR nemusí smerovať späť na meno, ktorého A record obsahuje danú IP, pokiaľ to prevádzková policy nevyžaduje.

Reverse DNS sa používa pri mail reputácii, audite, log enrichment a niektorých access policies. Nemá byť jediným autorizačným dôkazom.

## 34. DNS-based traffic steering

DNS môže vracať viac adries alebo meniť odpoveď podľa health, geography alebo weight policy.

```dns
api.example.com. 60 IN A 192.0.2.10
api.example.com. 60 IN A 192.0.2.11
```

Limity:

- klient môže record cacheovať dlhšie než očakávaš,
- existujúce connections DNS zmena nepresunie,
- resolver locality nemusí zodpovedať client locality,
- failover je viazaný na TTL a client behavior,
- DNS nevidí per-request backend queue.

DNS steering sa často kombinuje s regionálnym L4/L7 load balancerom.

## 35. Application DNS cache

Runtime alebo connection pool môže cacheovať resolution dlhšie, kratšie alebo vôbec nerešpektovať TTL rovnakým spôsobom ako OS resolver.

Príklady prevádzkových dôsledkov:

- aplikácia používa starú backend IP aj po DNS zmene,
- nový connection pool obnoví meno, staré pooled connections zostanú,
- JVM, browser alebo proxy majú vlastnú cache policy,
- proces reštart vyrieši symptóm, ale skryje chybnú cache konfiguráciu.

Pri incidente treba poznať resolver implementáciu konkrétnej aplikácie.

## 36. Diagnostické nástroje a ich observation point

```bash
getent ahosts api.example.com
resolvectl query api.example.com
dig api.example.com A
dig api.example.com AAAA
dig @<resolver> api.example.com
dig +tcp api.example.com
dig +trace api.example.com
```

- `getent` — testuje NSS path podobný bežnej aplikácii.
- `resolvectl` — ukazuje systemd-resolved routing a cache context.
- `dig` — posiela DNS query zvolenému resolveru, ale obchádza časť NSS.
- `dig @server` — izoluje konkrétny recursive alebo authoritative server.
- `+tcp` — testuje transport fallback.
- `+trace` — sleduje delegačnú hierarchiu bez lokálnej recursive cache.

## 37. Diagnostický postup: aplikácia nevyrieši meno

1. Reprodukuj rovnakou API cestou ako aplikácia, napríklad `getent` alebo runtime-specific testom.
2. Zisti network namespace, `/etc/resolv.conf`, NSS a aktívny resolver manager.
3. Zaznamenaj presný výsledok: timeout, `NXDOMAIN`, NODATA, `SERVFAIL` alebo `REFUSED`.
4. Over absolute meno a search-domain expansion.
5. Porovnaj A a AAAA queries.
6. Query pošli priamo nakonfigurovanému recursive resolveru.
7. Skontroluj TTL, positive a negative cache.
8. Otestuj authoritative servers a delegation.
9. Porovnaj UDP a TCP transport.
10. Over DNSSEC validation a čas.
11. Porovnaj interný, VPN a verejný resolver view.
12. Po úspešnom resolution pokračuj route, port, TLS a application vrstvou.

## 38. Diagnostický postup: odpoveď sa líši medzi klientmi

1. Zisti, ktorý resolver používa každý klient.
2. Porovnaj source network, VPN a split-horizon view.
3. Zaznamenaj record set a zostávajúci TTL.
4. Skontroluj application a browser cache.
5. Query authoritative servery priamo.
6. Over geo/weighted/load-balancing policy.
7. Skontroluj, či rozdiel nevzniká medzi A a AAAA selection.
8. Over, či všetky authoritative servers majú rovnakú zone verziu.

## 39. Diagnostický postup: iba niektoré DNS odpovede timeoutujú

```bash
dig small.example A
dig large.example TXT
dig +dnssec large.example
dig +tcp large.example
```

Ak malé UDP queries fungujú a väčšie zlyhávajú:

- over EDNS payload a fragmentation,
- skontroluj firewall pre TCP/53,
- pozri Path MTU a ICMP policy,
- zachyť query aj response,
- over middlebox, ktorý zahadzuje fragmenty alebo EDNS.

## 40. Bezpečnostné hranice

DNS odpoveď ovplyvňuje, kam sa klient pripojí, ale sama nemusí autentizovať cieľ.

- TLS certificate validation — overuje server identity aj pri manipulovanom DNS path-e.
- SSH host keys — chránia remote host identity nezávisle od mena.
- DNSSEC — overuje DNS data chain, nie aplikačný endpoint po connection.
- Resolver transport encryption — chráni query medzi klientom a resolverom.
- Access control — authoritative a recursive služby musia obmedziť recursion, zone transfer a administrative API.

Open recursive resolver môže byť zneužitý na amplification attack a predstavuje prevádzkové riziko.

## 41. Časté omyly

### „`dig` dokazuje, ako meno vyrieši aplikácia“

`dig` môže obísť NSS, `/etc/hosts`, lokálny daemon, search logic alebo application cache. Je to jeden observation point.

### „Nízky TTL znamená okamžitú zmenu“

Existujúce cache entries si držia predchádzajúci TTL. Migration treba pripraviť vopred.

### „CNAME presmeruje browser“

CNAME mení DNS alias resolution. HTTP redirect je samostatná aplikačná odpoveď.

### „DNSSEC šifruje DNS traffic“

DNSSEC poskytuje autenticitu a integritu DNS dát. Dôvernosť transportu rieši DoT, DoH alebo iná zabezpečená cesta.

### „`NOERROR` znamená, že A record existuje“

`NOERROR` môže mať prázdnu answer section. Meno môže existovať bez požadovaného record type.

### „Keď DNS vráti IP, služba funguje“

Resolution iba vyberie target. Route, port, TLS, autentizácia a aplikácia môžu zlyhať neskôr.

### „DNS failover presunie existujúce connections“

DNS ovplyvní až nové resolution alebo connection pokusy. Existujúce flows zostanú na starom endpoint-e.

## 42. Kontrolné otázky

1. Aký je rozdiel medzi DNS namespace a zone?
2. Ako sa líši stub, recursive a authoritative resolver role?
3. Čo je referral a načo slúži glue record?
4. Aký je rozdiel medzi recordom a record setom?
5. Prečo CNAME chain zvyšuje failure surface?
6. Čo presne riadi TTL a prečo jeho zníženie neplatí spätne?
7. Aký je rozdiel medzi `NXDOMAIN` a NODATA?
8. Prečo DNS potrebuje UDP aj TCP?
9. Ako EDNS a MTU ovplyvňujú veľké odpovede?
10. Prečo `dig` nemusí reprodukovať správanie aplikácie?
11. Ako search domains a `ndots` zvyšujú latency?
12. Ako split-horizon DNS komplikuje troubleshooting?
13. Čo DNSSEC chráni a čo nechráni?
14. Prečo môže validating resolver vrátiť `SERVFAIL`, hoci authoritative server vracia records?
15. Aké limity má DNS-based load balancing?
16. Ako by si diagnostikoval odpovede, ktoré sa líšia medzi dvoma klientmi?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Ports a sockets](ports-and-sockets.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: DHCP →](dhcp.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
