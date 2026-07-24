# OSI a TCP/IP model

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [Linux networking](../01-linux-and-systems/linux-networking.md)
- Súvisiace témy: Ethernet, IP, TCP, UDP, DNS, HTTP, TLS, routing, troubleshooting

## 1. Definícia

OSI a TCP/IP sú **vrstvené modely sieťovej komunikácie**. Rozdeľujú prenos dát na zodpovednosti s relatívne stabilnými rozhraniami: lokálny prenos po linke, routovanie medzi sieťami, transport medzi procesmi a význam dát pre aplikáciu.

Model nie je packet, konkrétny protokol ani presný popis implementácie kernelu. Je to analytická mapa, ktorá pomáha určiť:

- ktorý mechanizmus rieši konkrétnu časť komunikácie,
- ktoré metadata sa v danej vrstve pridávajú,
- ktoré zariadenia alebo procesy ich interpretujú,
- kde možno komunikáciu pozorovať,
- a na ktorej hranici mohol vzniknúť failure.

## 2. Prečo vrstvenie existuje

Bez vrstvenia by každá aplikácia musela implementovať fyzický prenos, framing, adresovanie, routing, spoľahlivosť, šifrovanie aj aplikačnú syntax ako jeden nerozdeliteľný systém. Zmena sieťového média alebo transportného protokolu by potom vyžadovala prepis celej aplikácie.

Vrstvenie vytvára kontrakty. Aplikácia môže poslať byte stream cez TCP bez znalosti Ethernet MAC adries. Router môže preposlať IP packet bez znalosti HTTP metódy. Ethernet switch môže forwardovať frame bez znalosti cieľového TCP portu.

Toto oddelenie nie je absolútne. Firewally, load balancery, proxy servery a observability nástroje môžu analyzovať viac vrstiev naraz. Stále však pomáha pomenovať, **ktoré informácie konkrétna funkcia potrebuje na rozhodnutie**.

## 3. OSI model

OSI model používa sedem konceptuálnych vrstiev:

| Vrstva | Názov | Hlavná zodpovednosť | Typické príklady |
|---:|---|---|---|
| 7 | Application | Význam requestov a aplikačné operácie | HTTP, DNS, SMTP, SSH |
| 6 | Presentation | Reprezentácia, encoding, serializácia, kompresia a kryptografická transformácia | JSON, ASN.1, TLS record representation |
| 5 | Session | Riadenie dialógu, session state a obnovenie komunikácie | aplikačné sessions, RPC conversation state |
| 4 | Transport | Komunikácia medzi procesmi, ports, reliability, ordering a congestion control | TCP, UDP, QUIC transport functions |
| 3 | Network | Logické adresovanie a prechod cez routované siete | IPv4, IPv6, ICMP, routing |
| 2 | Data Link | Prenos frames v lokálnom linkovom scope | Ethernet, Wi-Fi, VLAN, MAC forwarding |
| 1 | Physical | Prenos bitov cez konkrétne médium | elektrický, optický alebo rádiový signál |

OSI model je vhodný na precízne pomenovanie zodpovedností. Reálny internetový stack však nezachováva všetky hranice ako samostatné implementačné moduly. Presentation a session funkcie sú napríklad často súčasťou aplikačných knižníc alebo TLS stacku.

Preto sa OSI nemá používať ako dogma typu „každá technológia patrí presne do jednej vrstvy“. Je to referenčný rámec na analýzu kontraktov a failure boundaries.

## 4. TCP/IP model

TCP/IP model zodpovedá praktickému internetovému stacku a zvyčajne používa štyri vrstvy:

| TCP/IP vrstva | Približné OSI vrstvy | Zodpovednosť | Príklady |
|---|---:|---|---|
| Application | 5–7 | Aplikačný protokol, formát dát, identity a session logika | HTTP, DNS, SSH, SMTP, TLS nad TCP |
| Transport | 4 | End-to-end komunikácia medzi procesmi | TCP, UDP, QUIC |
| Internet | 3 | Adresovanie a routing medzi sieťami | IPv4, IPv6, ICMP |
| Link | 1–2 | Prenos v jednom lokálnom linkovom segmente | Ethernet, Wi-Fi, VLAN, ARP/NDP kontext |

Často sa používa aj päťvrstvový model, ktorý oddeľuje physical a data-link vrstvu. Počet vrstiev nie je hlavný cieľ. Dôležité je vedieť, ktorý kontrakt sa práve testuje.

Napríklad „sieť nefunguje“ môže znamenať chýbajúci link, nesprávnu VLAN, zlyhaný ARP, chybnú route, blokovaný TCP handshake, neplatný certifikát alebo HTTP chybu. Každý z týchto problémov patrí do inej diagnostickej vetvy.

## 5. Encapsulation

Pri odosielaní dát nižšia vrstva prijme výstup vyššej vrstvy ako payload a pridá svoje metadata. Tento proces sa nazýva **encapsulation**.

```text
HTTP request
  ↓ TCP pridá source/destination port, sequence state a flags
TCP segment
  ↓ IP pridá source/destination IP, TTL/hop limit a protocol identifier
IP packet
  ↓ Ethernet pridá source/destination MAC a frame metadata
Ethernet frame
  ↓ fyzická vrstva zakóduje frame do signálu
bits / symbols / signal
```

Na prijímacej strane prebieha **decapsulation**. Driver prijme frame, linková vrstva overí jeho základnú integritu a cieľ, IP vrstva spracuje network header, transportná vrstva nájde socket a aplikácia interpretuje aplikačné bytes.

Každá vrstva teda vidí iný objekt a iný scope. Ethernet switch forwarduje frame. Router routuje packet. TCP stack spravuje connection state. HTTP server interpretuje request method, headers a body.

## 6. Protocol Data Units

Názvy prenášaných jednotiek pomáhajú presne určiť vrstvu:

- **message alebo application data** — aplikačný význam, napríklad HTTP request,
- **TCP segment** — časť TCP byte streamu s TCP headerom,
- **UDP datagram** — jedna transportná správa s UDP headerom,
- **IP packet** — routovateľná jednotka internetovej vrstvy,
- **Ethernet frame** — linková jednotka platná v konkrétnom L2 segmente,
- **bits alebo symbols** — fyzická reprezentácia na médiu.

V bežnej reči sa slovo „packet“ používa všeobecne. Pri diagnostike však presná terminológia zabraňuje chybným záverom. Packet capture na Ethernet interface môže obsahovať Ethernet frame, IP packet aj TCP segment ako vnorené vrstvy jedného záznamu.

## 7. Header, payload a trailer

Každá vrstva pridáva metadata potrebné pre svoju zodpovednosť. Vyššia vrstva sa pre nižšiu vrstvu stáva payloadom:

```text
Ethernet payload = IP packet
IP payload       = TCP segment alebo UDP datagram
TCP payload      = application bytes
```

Ethernet frame môže mať aj trailer, napríklad frame check sequence na detekciu linkovej chyby. IP header obsahuje informácie potrebné pre routing. TCP header obsahuje porty, sequence numbers, flags a flow-control state.

Router typicky nepotrebuje interpretovať aplikačný payload, aby vykonal longest-prefix route lookup. Stateful firewall však môže čítať transportné metadata a reverse proxy môže ukončiť TLS a analyzovať HTTP. To ukazuje, že zariadenie sa nemá klasifikovať iba marketingovým názvom, ale podľa informácií, ktoré pri rozhodovaní používa.

## 8. Adresovanie a identity podľa vrstvy

Rôzne identifikátory riešia rozdielne scope a nemožno ich navzájom zamieňať:

| Identifikátor | Scope | Čo identifikuje |
|---|---|---|
| MAC address | lokálny L2 segment | linkový interface alebo virtuálny endpoint v konkrétnom broadcast domaine |
| IP address | routovaný L3 priestor | network endpoint alebo interface podľa routing kontextu |
| Port | transportný namespace hosta | aplikačný endpoint v rámci IP/protokolu |
| DNS name | naming vrstva | meno mapované resolverom na jeden alebo viac cieľov |
| URL | aplikačný resource identifier | scheme, authority, path a ďalšie časti requestu |

Úplný TCP flow sa bežne rozlišuje pomocou päťprvku:

```text
source IP, source port, destination IP, destination port, protocol
```

Samotný port `443` neidentifikuje službu. Rovnaký port môže existovať na tisícoch IP adries a jeden listening socket môže obsluhovať viac virtuálnych hostov cez TLS SNI alebo HTTP `Host` header.

## 9. Linkový scope a routovaný scope

Ethernet frame je platný iba v konkrétnom linkovom segmente. Router frame prijme, odstráni pôvodný linkový header, rozhodne o ďalšom hop-e podľa IP packetu a vytvorí nový frame pre nasledujúci link.

```text
Host A → Router 1
L2: MAC-A → MAC-R1
L3: IP-A  → IP-B

Router 1 → Router 2
L2: MAC-R1-out → MAC-R2-in
L3: IP-A       → IP-B
```

Zdrojová a cieľová IP typicky zostávajú end-to-end rovnaké, kým ich nezmení NAT alebo iný packet transformation mechanizmus. MAC adresy sa menia na každom routovanom linku, pretože riešia iba doručenie k lokálnemu next hopu.

Táto hranica vysvetľuje častú chybu: host pri komunikácii s internetovým serverom nehľadá MAC adresu vzdialeného servera. Hľadá MAC adresu svojho lokálneho next hopu, typicky default gateway.

## 10. Hop-by-hop a end-to-end mechanizmy

**Hop-by-hop mechanizmus** sa aplikuje medzi susednými uzlami alebo na každom routeri. Patrí sem linkový framing, neighbor resolution, queueing na interface a znižovanie TTL alebo hop limitu.

**End-to-end mechanizmus** vytvára logický kontrakt medzi pôvodnými endpointmi. TCP connection, aplikačný request alebo TLS session sú typicky end-to-end voči endpointu, ktorý daný protokol ukončuje.

Middlebox môže end-to-end vzťah rozdeliť. Reverse proxy môže ukončiť klientsky TLS a vytvoriť nový TLS alebo plaintext connection k backendu. Load balancer môže mať samostatné TCP spojenie na každej strane. Z pohľadu klienta je proxy cieľovým transportným a kryptografickým endpointom, aj keď business request pokračuje ďalej.

## 11. Data plane, control plane a management plane

**Data plane** spracúva konkrétne frames, packets alebo requests podľa už existujúceho stavu. Vykonáva forwarding, filtering, NAT, queueing, load-balancing decision alebo packet encapsulation.

**Control plane** vytvára a distribuuje stav, ktorý data plane používa. Routing protocols napĺňajú routing information base, ARP/NDP vytvára neighbor state, load-balancer controller publikuje backend membership a DNS control plane mení records.

**Management plane** poskytuje administratívne rozhranie pre konfiguráciu a pozorovanie zariadenia alebo systému. Patrí sem CLI, API, configuration database, identity a audit prístupov.

Tieto roviny môžu zlyhať nezávisle:

- data plane môže stále forwardovať podľa starej route, hoci control plane je nedostupný,
- control plane môže distribuovať chybnú policy do inak zdravého data plane,
- management API môže byť nedostupné, hoci produkčný traffic pokračuje,
- preťažený data plane môže dropovať packets, hoci konfigurácia je správna.

## 12. Protocol, implementation, service a endpoint

**Protocol** je súbor pravidiel komunikácie, napríklad HTTP alebo DNS. **Implementation** je konkrétny software, ktorý protokol implementuje, napríklad NGINX alebo BIND. **Service** je schopnosť poskytovaná používateľovi alebo inému systému. **Endpoint** je konkrétny adresovateľný bod, cez ktorý je služba dostupná.

Tieto pojmy sa nesmú zamieňať. Proces môže počúvať na porte, ale nemusí odpovedať korektným protokolom. Viac implementácií môže poskytovať rovnakú službu. Jeden endpoint môže smerovať cez proxy na viac backendov. Jeden backend môže poskytovať viac virtuálnych služieb.

Pri troubleshooting-u treba preto overiť postupne:

```text
existuje endpoint?
→ prijíma transportné spojenie?
→ prebehne TLS alebo iný session handshake?
→ rozumie očakávanému aplikačnému protokolu?
→ poskytuje správnu business operáciu?
```

## 13. Kde patria TLS a QUIC

Niektoré technológie prekračujú jednoduché hranice vrstiev.

TLS poskytuje kryptografickú ochranu, integritu a peer authentication. Pri HTTPS typicky beží nad TCP a pod HTTP, ale jeho session a presentation funkcie zodpovedajú viacerým OSI konceptom. TLS terminujúci proxy sa stáva bezpečnostným endpointom, aj keď aplikačný request pokračuje ďalej.

QUIC beží nad UDP, ale implementuje reliable streams, ordering, congestion control, connection migration a integrovaný TLS handshake. Funkčne teda pokrýva časť transportnej aj session/security zodpovednosti. HTTP/3 následne používa QUIC namiesto TCP.

Vrstvený model je mapa zodpovedností, nie pravidlo, že každý protokol musí patriť do jednej bunky tabuľky.

## 14. Observation points

Každý nástroj pozoruje komunikáciu na konkrétnej vrstve a v konkrétnom namespace alebo procese:

| Nástroj | Primárny observation point |
|---|---|
| `ip link`, `ethtool` | interface a link state |
| `ip addr`, `ip route`, `ip neigh` | lokálny L3 a neighbor state |
| `ss` | socket a transport state konkrétneho network namespace |
| `tcpdump` | packets viditeľné na vybranom interface/hooku |
| `dig`, `getent` | DNS alebo NSS resolution path |
| `openssl s_client` | TLS handshake a certificate presentation |
| `curl` | resolver, transport, TLS a HTTP klientsky pohľad |
| aplikačné logy a traces | aplikačný request, dependency calls a business outcome |

Negatívny výsledok jedného observation pointu nehovorí automaticky, kde je root cause. `curl` timeout môže vzniknúť pred HTTP vrstvou. Hostový `ss` nemusí vidieť socket v inom namespace. `tcpdump` na nesprávnom interface nemusí zachytiť relevantný flow.

## 15. Diagnostika HTTPS requestu po vrstvách

Pri HTTPS timeout-e je vhodné najprv definovať konkrétny endpoint, source context a očakávaný výsledok. Potom možno testovať jednotlivé hranice:

```text
Naming:     vyriešilo sa správne meno a address family?
Link/L3:    existuje interface, source IP a route?
Neighbor:   je dostupný lokálny next hop?
Transport:  prebehol TCP handshake alebo QUIC exchange?
Security:   prebehol TLS handshake, SNI a certificate validation?
HTTP:       bol request odoslaný a prišla response?
Application: spracoval backend request v očakávanom čase?
```

Príklad nástrojov:

```bash
getent ahosts example.com
ip route get <resolved-ip>
ip neigh show
ss -tan dst <resolved-ip>:443
sudo tcpdump -ni any host <resolved-ip> and port 443
openssl s_client -connect example.com:443 -servername example.com
curl --verbose --connect-timeout 5 https://example.com/
```

Každý krok má testovať konkrétnu hypotézu. Nie je efektívne zbierať všetky možné výstupy bez otázky, ktorú majú potvrdiť alebo vyvrátiť.

## 16. Bottom-up, top-down a divide-and-conquer

**Bottom-up diagnostika** začína linkom a pokračuje smerom k aplikácii. Je vhodná, keď neexistuje základná konektivita alebo nie je známy prvý funkčný bod.

**Top-down diagnostika** začína používateľským requestom a identifikuje, v ktorej fáze zlyhal. Je efektívna pri kvalitných logoch, distributed traces a jasných erroroch klienta.

**Divide-and-conquer** začne na strednej vrstve, napríklad packet capture alebo TCP connect testom. Ak handshake neprebehne, pokračuje smerom nadol. Ak prebehne, pokračuje k TLS a aplikácii.

Metóda sa má vybrať podľa dostupných dôkazov. Mechanické „vždy začni od L1“ môže byť rovnako neefektívne ako okamžité obvinenie aplikácie.

## 17. Failure boundaries a timeout budget

Každá vrstva môže mať vlastný timeout, retry a failure semantics. DNS resolver môže čakať na nameserver, TCP môže retransmitovať SYN, TLS môže zlyhať na validácii chainu a HTTP klient môže mať celkový request timeout.

Ak celkový request trvá 30 sekúnd, treba zistiť, kde sa čas spotreboval:

```text
DNS lookup       5 s
TCP connect     10 s
TLS handshake    0.2 s
HTTP backend    14.8 s
```

Bez tejto dekompozície môže byť „HTTP timeout“ nesprávne interpretovaný ako pomalá aplikácia, hoci polovicu času spotreboval transportný retry.

Retry na viacerých vrstvách sa môže násobiť. Klient, proxy a backend SDK môžu každý opakovať pokus, čím jeden používateľský request vytvorí veľké množstvo downstream práce. Vrstvenie preto pomáha nielen diagnostike, ale aj návrhu konzistentného timeout a retry budgetu.

## 18. Anti-patterny

### Model ako memorovanie siedmich názvov

Poznať poradie OSI vrstiev bez schopnosti sledovať konkrétny request neposkytuje praktickú diagnostickú hodnotu. Dôležité je rozumieť zodpovednostiam, metadata a observation points.

### Root cause podľa názvu symptómu

`HTTP timeout` neznamená automaticky L7 problém. Môže ho spôsobiť DNS delay, packet loss, SYN retry, MTU black hole, TLS failure alebo backend queueing.

### Zariadenie priradené jednej vrstve navždy

Moderný switch môže routovať, firewall môže analyzovať TLS metadata a load balancer môže fungovať na L4 aj L7. Rozhodujú konkrétne funkcie a headers, ktoré používa.

### Predpoklad end-to-end spojenia cez proxy

Keď proxy terminujú transport alebo TLS, klient a backend nemusia zdieľať jednu connection ani jeden security context. Diagnostika musí skúmať obe strany proxy oddelene.

## 19. Praktický mini-lab

Spusť HTTPS request a zachyť jednotlivé vrstvy:

```bash
getent ahosts example.com
ip route get <IP>
ip neigh show
sudo tcpdump -ni any host <IP> and port 443
curl --verbose https://example.com/
```

Pri capture identifikuj:

1. linkový source a destination pre lokálny hop,
2. end-to-end source a destination IP,
3. TCP source a destination ports,
4. SYN, SYN-ACK a ACK,
5. TLS ClientHello a ServerHello, ak nie sú skryté konkrétnou capture podmienkou,
6. moment, po ktorom začne aplikačná výmena.

Potom odpovedz, ktoré polia by sa zmenili po prechode routerom, ktoré po NAT-e a ktoré po TLS termination proxy.

## 20. Kontrolné otázky

1. Prečo je vrstvený model analytická mapa a nie presný obraz implementácie?
2. Aký je rozdiel medzi Ethernet frame, IP packetom a TCP segmentom?
3. Prečo sa MAC adresy menia na routovaných hopoch, ale IP adresy typicky nie?
4. Aký je rozdiel medzi hop-by-hop a end-to-end mechanizmom?
5. Ako sa líši data plane, control plane a management plane?
6. Prečo port neidentifikuje službu bez ďalšieho kontextu?
7. Kde funkčne patria TLS a QUIC a prečo ich nemožno zaradiť úplne mechanicky?
8. Čo je observation point a prečo môže viesť nesprávne miesto pozorovania k chybnému záveru?
9. Ako rozložíš HTTPS timeout na DNS, transport, TLS a application fázu?
10. Kedy je vhodná bottom-up, top-down alebo divide-and-conquer diagnostika?

## 21. Zhrnutie

OSI a TCP/IP modely rozdeľujú komunikáciu na zodpovednosti, metadata a failure boundaries. Ich praktická hodnota nie je v memorovaní názvov vrstiev, ale v schopnosti sledovať konkrétny request cez encapsulation, lokálny link, routing, transport, security a aplikačný protokol. Správne použitý vrstvený model určuje, ktorý kontrakt testujeme, kde ho pozorujeme a aký dôkaz potrebujeme pred ďalším zásahom.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Performance a troubleshooting](../01-linux-and-systems/performance-and-troubleshooting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ethernet, MAC a ARP →](ethernet-mac-arp.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
