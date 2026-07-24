# TCP a UDP

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [OSI a TCP/IP model](osi-and-tcp-ip-model.md), [Routing a default gateway](routing-and-default-gateway.md)
- Súvisiace témy: ports, sockets, DNS, HTTP, QUIC, load balancing, firewalls

## 1. Čo transportná vrstva rieši

TCP a UDP prenášajú aplikačné dáta medzi transportnými endpointmi nad IP. IP rozhoduje, kam packet smeruje, zatiaľ čo transportná vrstva rozlišuje konkrétne aplikácie na hoste, definuje formu prenášaných dát a podľa protokolu pridáva stav, recovery alebo riadenie toku.

TCP poskytuje obojsmerný, usporiadaný a spoľahlivý byte stream. UDP prenáša samostatné datagramy bez zabudovaného handshakeu, retransmission, ordering alebo flow-control modelu. Ani jeden protokol však neurčuje význam payloadu; ten definuje aplikačný protokol.

```text
application semantics
        ↓
TCP byte stream alebo UDP datagrams
        ↓
IP packets
        ↓
route, link a fyzický prenos
```

## 2. Endpoint, flow a connection identity

Transportný endpoint nie je iba port. Je to kombinácia network namespace, transportného protokolu, lokálnej IP adresy a lokálneho portu. Remote peer pridáva vzdialenú IP a port.

TCP connection sa typicky identifikuje 5-tuple:

```text
protocol
source IP
source port
destination IP
destination port
```

Network namespace je ďalšia hranica, pretože dva namespaces môžu mať rovnaké IP adresy aj porty bez konfliktu. Jeden serverový port môže súčasne obsluhovať tisíce connections, pretože jednotlivé accepted sockets majú odlišné remote endpoints.

## 3. Porty a ich význam

Port je 16-bitové číslo v rozsahu `0–65535`. Well-known, registered a dynamic ranges sú organizačné konvencie, nie dôkaz protokolu ani bezpečnostná politika.

- Well-known port — štandardne sa používa pre všeobecne známe služby, ale aplikácia na ňom môže hovoriť iným protokolom.
- Registered port — býva priradený produktu alebo aplikačnému protokolu, no stále nejde o enforcement mechanizmus.
- Ephemeral port — operačný systém ho typicky vyberie ako dočasný source port outbound connection.

Port `443` preto neznamená automaticky HTTPS a otvorený port neznamená, že je služba autorizovaná alebo zdravá.

## 4. TCP je byte stream, nie správy

TCP zachováva poradie bytes, ale nezachováva hranice jednotlivých `write()` volaní. Sender môže vykonať dve malé writes a receiver ich môže prečítať spolu, po častiach alebo v inom chunk rozdelení.

```text
sender:   write("ABC") + write("DEF")
receiver: read("AB") + read("CDEF")
```

Aplikačný protokol preto potrebuje framing:

- Length prefix — správa nesie svoju veľkosť, takže receiver vie, koľko bytes ešte čaká.
- Delimiter — koniec správy označuje špeciálna sekvencia, ktorú musí protokol bezpečne escapovať.
- Fixed-size record — každá správa má rovnakú dĺžku, čo zjednodušuje parsing, ale môže plytvať miestom.
- Self-describing format — parser určí hranicu zo syntaxe formátu, stále však musí správne pracovať s neúplným inputom.

Predpoklad „jedno `send` = jedno `recv`“ je chyba aplikačného protokolu.

## 5. Vytvorenie TCP connection

Klient typicky vykoná `connect()`, kernel vyberie source address a ephemeral port, vytvorí connection state a odošle SYN. Server má listening socket, SYN queue a následne accept queue pre dokončené handshakes čakajúce na `accept()`.

```text
Client                                      Server
SYN, seq=x                           ───────►
                                     ◄─────── SYN-ACK, seq=y, ack=x+1
ACK, ack=y+1                         ───────►
ESTABLISHED                                  ESTABLISHED
```

Handshake plní viac úloh:

- Sequence synchronization — obe strany si zvolia initial sequence space, podľa ktorého číslujú bytes.
- Bidirectional path validation — klient aj server musia vedieť doručiť aspoň handshake packets opačným smerom.
- Option negotiation — endpointy si oznámia MSS, window scaling, SACK, timestamps a ďalšie podporované vlastnosti.
- State allocation — kernel vytvorí stav potrebný na retransmission, ordering, windows a close lifecycle.

Úspešný handshake dokazuje funkčný transportný začiatok. Nedokazuje TLS úspech, aplikačnú autorizáciu ani správne spracovanie requestu.

## 6. Sequence numbers, ACK a ordered delivery

TCP čísluje bytes, nie packets. Receiver ACK hodnotou oznamuje ďalší byte, ktorý očakáva; tým kumulatívne potvrdzuje všetky predchádzajúce súvislé bytes.

Sender drží nepotvrdené dáta v retransmission queue. Keď dostane ACK, môže potvrdenú časť uvoľniť. Ak chýba časť streamu, receiver novšie bytes dočasne podrží, ale aplikácii ich neodovzdá pred chýbajúcim miestom.

Tento mechanizmus vytvára head-of-line blocking v rámci jedného TCP streamu: strata jedného segmentu pozastaví delivery neskorších bytes, hoci fyzicky už dorazili.

## 7. Loss detection a retransmission

TCP nerozoznáva fyzickú príčinu straty. Pozoruje len ACK pattern, čas a prípadné explicitné congestion signály.

- Retransmission timeout — sender po odhadovanom časovom limite zopakuje nepotvrdené dáta.
- Duplicate ACK — opakované ACK rovnakej hodnoty signalizujú dieru v sequence space.
- SACK — receiver oznámi aj neskoršie bloky, ktoré už má, takže sender nemusí opakovať celý rozsah.
- RACK a moderné loss detection — implementácia môže loss odvodzovať z časovania novšie doručených segmentov.

Loss môže vzniknúť pre queue overflow, link error, firewall drop, congestion, route change, receiver overload alebo chybný middlebox. Retransmission counter je dôkaz transportného recovery, nie automaticky dôkaz konkrétneho zlého linku.

```bash
ss -ti
nstat | grep -i retrans
tcpdump -ni any 'tcp and host <IP>'
```

## 8. RTT a retransmission timeout

TCP priebežne odhaduje round-trip time a jeho variabilitu. Retransmission timeout musí byť dosť dlhý, aby nereagoval na každé krátke oneskorenie, ale dosť krátky, aby recovery netrvala neprimerane dlho.

Vysoký RTT znižuje rýchlosť feedback loopu. Loss na high-latency path preto často bolí viac než rovnaké percento lossu v lokálnej sieti. Pri diagnostike treba pozerať RTT, jeho distribúciu, retransmissions a množstvo dát in flight spolu.

## 9. Flow control chráni receiver

Receiver má obmedzený socket buffer a aplikácia z neho musí čítať. Advertised receive window oznamuje senderovi, koľko ďalších bytes môže poslať bez pretečenia receiver bufferu.

```text
network doručuje bytes
        ↓
receive socket buffer
        ↓ read()
application
```

Ak aplikácia číta pomaly, receive window sa zmenšuje. Pri zero window sender zastaví bežné posielanie a periodicky používa probes, aby zistil, či sa priestor znovu otvoril.

Zero-window stav preto často ukazuje receiver-side pressure alebo blocked application thread. Nie je to rovnaký mechanizmus ako congestion control.

## 10. Congestion control chráni sieťovú cestu

Congestion control obmedzuje množstvo nepotvrdených dát v sieti. Sender používa congestion window, RTT, loss, ECN a pacing na odhad bezpečného sending rate.

- Slow start — sender na začiatku rýchlo zväčšuje množstvo dát in flight, kým nenájde približnú kapacitu alebo congestion signál.
- Congestion avoidance — rast je opatrnejší a snaží sa stabilizovať okolo dostupnej kapacity.
- Loss response — algoritmus typicky zníži sending rate, pretože loss môže znamenať preplnené queues.
- ECN — sieť môže označiť congestion bez zahodenia packetu, ak to celý path podporuje.
- Pacing — sender rozkladá packets v čase, aby nevytváral zbytočné bursty.

Flow control odpovedá „koľko ešte zvládne receiver“. Congestion control odpovedá „koľko unesie cesta bez škodlivého queueingu a lossu“.

## 11. Bandwidth-delay product

Množstvo dát, ktoré treba mať in flight na plné využitie cesty, približne zodpovedá bandwidth × RTT. High-bandwidth a high-latency path preto potrebuje väčšie windows a buffers než lokálna sieť.

Príliš malé okno obmedzí throughput aj bez packet lossu. Príliš veľké nekontrolované queues môžu naopak vytvoriť bufferbloat a vysokú latency. Tuning musí vychádzať z merania pathu a workloadu, nie z univerzálnych sysctl receptov.

## 12. MSS, MTU a segmentation

MSS je maximálny TCP payload segmentu oznámený peerovi. Typicky sa odvodí z lokálneho MTU po odpočítaní IP a TCP headerov.

Sender môže aplikácii prijať veľký buffer a neskôr ho rozdeliť na segmenty. Offloading mechanizmy môžu segmentation presunúť z CPU protocol stacku do NIC, preto hostový packet capture môže zobrazovať väčšie logical packets než fyzická sieť.

MTU black hole sa často prejaví takto:

```text
handshake funguje
malý request funguje
väčší response sa zastaví
retransmissions bez progresu
```

Príčinou môže byť zablokovaný ICMP Packet Too Big/Fragmentation Needed alebo nesprávne tunelové MTU.

## 13. Listening socket a dve serverové queues

Serverový listening socket nie je totožný s accepted connection. Kernel počas prijímania connections typicky pracuje s dvoma logickými queue oblasťami:

- SYN queue — obsahuje handshakes, ktoré ešte nie sú dokončené.
- Accept queue — obsahuje dokončené connections, ktoré aplikácia ešte neprevzala cez `accept()`.

Preťaženie môže vzniknúť, keď SYN rate prekročí ochranné mechanizmy, aplikácia volá `accept()` príliš pomaly alebo worker model nevie nové connections spracovať.

```bash
ss -lnt
ss -s
nstat | grep -E 'Listen|SYN'
```

Backlog parameter aplikácie, kernel limity a reálna rýchlosť accept loopu tvoria jeden systém. Zvýšenie jediného limitu nemusí odstrániť bottleneck.

## 14. TCP state machine

TCP connection neprechádza iba stavmi `open` a `closed`. Kernel musí koordinovať obojsmerné ukončenie a chrániť sequence space.

- `LISTEN` — socket čaká na nové handshakes.
- `SYN-SENT` — klient odoslal SYN a čaká na odpoveď.
- `SYN-RECV` — server prijal SYN a čaká na posledný ACK.
- `ESTABLISHED` — obe strany môžu prenášať bytes.
- `FIN-WAIT-1/2` — lokálna strana aktívne ukončuje sending direction.
- `CLOSE-WAIT` — remote peer poslal FIN, ale lokálna aplikácia ešte socket nezavrela.
- `LAST-ACK` — lokálna strana pošle vlastný FIN a čaká na potvrdenie.
- `TIME-WAIT` — aktívny closer dočasne chráni starý tuple a oneskorené segmenty.

```bash
ss -tan
ss -tan state close-wait
ss -tan state time-wait
```

## 15. `CLOSE-WAIT` a application cleanup

`CLOSE-WAIT` znamená, že peer už ukončil svoj sending direction a kernel túto udalosť doručil lokálnej aplikácii. Stav sa skončí až vtedy, keď aplikácia zavrie socket.

Trvalý rast `CLOSE-WAIT` preto často ukazuje zabudnutý `close()`, blocked worker, neukončený request context alebo chybný connection pool. Kernel tuning nevyrieši application lifecycle leak.

## 16. `TIME-WAIT` a bezpečné opätovné použitie tuple

`TIME-WAIT` drží endpoint, ktorý aktívne ukončil connection. Chráni novú connection s rovnakým tuple pred oneskorenými segmentmi starej connection a umožňuje retransmit posledného ACK pri strate.

Veľký počet `TIME-WAIT` môže byť normálny pri veľkom počte krátkych connections. Incident vzniká až pri merateľnom dopade, napríklad ephemeral port exhaustion, conntrack pressure alebo nadmernom connection setup overhead-e.

## 17. Graceful close, half-close a reset

FIN uzatvára iba jeden smer streamu. Endpoint môže oznámiť, že už nebude posielať ďalšie bytes, ale stále môže prijímať dáta z opačnej strany.

RST connection okamžite zruší. Môže znamenať:

- No listener — destination host nemá socket pre daný port.
- Active reject — firewall alebo proxy connection explicitne odmietli.
- Application abort — proces zavrel socket spôsobom, ktorý zahodil neodoslané alebo neprečítané dáta.
- Unknown connection — packet nezodpovedá existujúcemu kernel state.

Tichý drop vedie typicky k timeoutu a retries. RST dáva rýchlu explicitnú chybu.

## 18. TCP timeouty nie sú jedna hodnota

Connection lifecycle používa viac časových hraníc:

- Connect timeout — ako dlho klient čaká na vytvorenie transportnej connection.
- Retransmission timers — ako TCP obnovuje stratené segmenty.
- Idle timeout — ako dlho aplikácia, proxy alebo middlebox drží neaktívny flow.
- Read/write deadline — ako dlho aplikácia čaká na progres konkrétnej operácie.
- Keepalive timers — ako kernel testuje dlho neaktívnu transportnú liveness.

Aplikačný timeout kratší než transport recovery môže connection ukončiť skôr, než TCP vyčerpá vlastné retries. Pri incidente treba identifikovať, ktorá vrstva timeout vyhlásila.

## 19. Keepalive a application heartbeat

TCP keepalive posiela probes na dlho neaktívnej connection a overuje, či transportný peer ešte reaguje. Default intervaly bývajú pre mnohé aplikácie veľmi dlhé.

Application heartbeat je súčasť protokolu a môže overiť viac:

- Peer process odpovedá — nielen kernel hosta.
- Protocol loop funguje — správa prešla parserom a event loopom.
- Session je platná — aplikácia môže odhaliť expirovanú autentizáciu.
- Dependency stav je použiteľný — heartbeat môže niesť aplikačné metadata.

Tieto mechanizmy sa dopĺňajú, ale nie sú zameniteľné.

## 20. Nagle, delayed ACK a malé správy

Nagle algorithm môže zadržať malé writes, kým sa nepotvrdia predchádzajúce dáta alebo sa nazbiera väčší segment. Delayed ACK môže krátko odložiť potvrdenie, aby ho spojil s odpoveďou alebo ďalším ACK.

V určitých request/response patterns sa tieto mechanizmy môžu nepriaznivo kombinovať. `TCP_NODELAY` môže znížiť latency malých interaktívnych správ, ale zvyšuje počet packets a overhead. Rozhodnutie musí vychádzať z message size, traffic patternu a meranej latency.

## 21. Ephemeral ports a outbound capacity

Klient potrebuje pre každú súčasnú TCP connection unikátny local tuple. Ak sa veľa connections smerom k rovnakému destination vytvára z jednej source IP, ephemeral port space sa môže stať kapacitným limitom.

```bash
sysctl net.ipv4.ip_local_port_range
ss -s
```

Príčiny pressure:

- Connection churn — aplikácia stále vytvára nové connections namiesto pooling-u.
- Dlhé `TIME-WAIT` — staré tuples ešte nemožno bezpečne znova použiť.
- Connection leak — sockets zostávajú otvorené bez užitočnej práce.
- NAT/PAT — viac klientov zdieľa jeden prekladový source IP a port space.
- Malý source-address pool — egress používa príliš málo zdrojových IP adries.

Správna náprava môže byť pooling, viac source IPs, menší churn, oprava leakov alebo rozdelenie egressu. Náhodné skracovanie TCP lifecycle timers môže poškodiť correctness.

## 22. UDP datagram semantics

UDP zachováva hranice správ. Jeden `sendto()` vytvorí jeden datagram a receiver dostane celý datagram alebo žiadny; ak je receive buffer príliš malý, zvyšok môže byť zahodený podľa API semantics.

UDP neposkytuje natívne:

- Handshake — sender nemusí vedieť, či receiver existuje.
- Delivery guarantee — datagram sa môže stratiť bez transportnej recovery.
- Ordering — neskorší datagram môže prísť skôr.
- Duplicate suppression — rovnaká správa môže doraziť viackrát.
- Flow control — sender nevie, či application receive queue stíha.
- Congestion control — jednoduché UDP API samo nereguluje sending rate podľa path pressure.

Vyšší protokol musí implementovať presne tie vlastnosti, ktoré jeho failure model potrebuje.

## 23. UDP header a checksum

UDP header obsahuje source port, destination port, length a checksum. Malý header znižuje protocol overhead, ale neodstraňuje aplikačnú potrebu pre retries, deduplication, security alebo congestion behavior.

Checksum odhaľuje poškodenie počas prenosu. Zlyhaný datagram sa zahodí; UDP neposiela automatický retransmission request.

## 24. „Connected“ UDP socket

UDP socket môže aplikácia pripojiť ku konkrétnemu peerovi cez `connect()`. Nevzniká tým handshake ani zdieľaný transportný connection state ako pri TCP.

Kernel však získa praktické informácie:

- Default destination — aplikácia môže používať `send()` namiesto `sendto()`.
- Peer filtering — socket prijíma iba datagramy z vybraného remote endpointu.
- Route/source selection — kernel môže skôr vyriešiť lokálny path.
- Asynchronous errors — niektoré ICMP chyby možno priradiť konkrétnemu socketu.

## 25. UDP failure ambiguity

Keď UDP klient nedostane odpoveď, samotný transport nevie rozlíšiť:

```text
request sa stratil
receiver ho zahodil
aplikácia ho nespracovala
response sa stratila
response prišla po timeout-e
```

Preto aplikačný protokol používa transaction IDs, sequence numbers, deadlines, retry policy a deduplication. Retry bez idempotency môže zopakovať side effect rovnako ako pri TCP aplikačnom timeout-e.

## 26. UDP buffers a drops

Kernel drží send a receive queues aj pre UDP. Pri vysokom trafficu môže receiver buffer pretekať skôr, než aplikácia datagramy prečíta.

```bash
ss -uan
nstat
netstat -su
```

Dôležité je rozlíšiť packet loss na linke od lokálneho socket-buffer dropu. Packet capture pred socket delivery môže ukazovať, že datagram dorazil na host, hoci aplikácia ho už nedostala.

## 27. UDP, fragmentácia a Path MTU

Veľký UDP datagram môže byť fragmentovaný na IP vrstve. Strata jedného fragmentu znehodnotí celý datagram a fragmenty často horšie prechádzajú firewallmi alebo middleboxes.

Bezpečnejší protokolový návrh:

- Obmedzí veľkosť datagramu — tak, aby sa zmestil do očakávaného path MTU.
- Použije aplikačné chunking — každý chunk má identitu, ordering a recovery pravidlá.
- Implementuje PMTUD — vrátane správneho spracovania ICMP signálov.
- Zvolí iný transport — keď aplikácia potrebuje stream segmentation a spoľahlivú delivery.

DNS používa EDNS na väčšie UDP odpovede a pri truncation môže prejsť na TCP.

## 28. ICMP chyby pri UDP

Ak destination host nemá listener na UDP porte, môže poslať ICMP Port Unreachable. Firewall môže túto odpoveď zahodiť alebo ticho zahodiť samotný request, takže klient vidí iba timeout.

Asynchronous error nemusí byť aplikácii doručený okamžite a správanie závisí od socket API a operačného systému. Absencia ICMP chyby preto nedokazuje, že receiver request prijal.

## 29. Broadcast a multicast

UDP sa často používa tam, kde má jedna správa osloviť viac receivers.

- IPv4 broadcast — datagram sa doručuje v broadcast domain a router ho bežne neforwarduje.
- IP multicast — receivers sa prihlasujú do skupiny a sieť musí podporovať príslušný forwarding model.
- Service discovery — lokálne protokoly používajú multicast alebo broadcast na nájdenie peers bez centrálneho registry.
- Telemetry a media — jeden stream môže sieť distribuovať viacerým receivers efektívnejšie než samostatné unicasty.

Multicast nie je automaticky dostupný cez routované, cloudové alebo overlay siete. Potrebuje explicitnú sieťovú podporu a observability.

## 30. QUIC nad UDP

QUIC používa UDP ako prenosový substrate, ale nad ním implementuje vlastný connection a recovery model:

- Reliable streams — loss recovery a ordering sa riešia v QUIC vrstve.
- Per-stream multiplexing — strata v jednom streame neblokuje delivery nezávislého streamu rovnakým spôsobom ako TCP byte stream.
- Congestion control — protokol reguluje sending rate podľa path feedbacku.
- TLS 1.3 integration — kryptografický handshake je súčasťou connection setupu.
- Connection migration — identita connection nie je viazaná iba na nemenný IP/port tuple.

Tvrdenie „QUIC je nespoľahlivý, lebo používa UDP“ zamieňa vlastnosti substrate s vlastnosťami celého protokolu.

## 31. TCP verzus UDP nie je „spoľahlivosť verzus rýchlosť“

Voľba transportu vychádza z aplikačného kontraktu.

| Otázka | TCP | UDP alebo protokol nad UDP |
|---|---|---|
| Potrebuje aplikácia ordered byte stream? | Poskytuje ho natívne. | Vyššia vrstva ho musí navrhnúť. |
| Potrebuje zachovať message boundaries? | Aplikácia musí pridať framing. | Datagram boundaries sú zachované. |
| Je čiastočná strata prijateľná? | Stream čaká na chýbajúce bytes. | Aplikácia môže stratenú správu ignorovať alebo obnoviť selektívne. |
| Potrebuje multicast? | TCP ho neposkytuje. | UDP môže používať multicast alebo broadcast. |
| Kto riadi congestion? | Kernel TCP stack. | Vyšší protokol alebo aplikácia. |
| Kto definuje retry a deduplication? | TCP obnovuje bytes, nie business operácie. | Aplikácia rieši transport aj business semantics podľa návrhu. |

## 32. Transport, TLS a aplikačné retries

TCP môže doručiť request serveru, server ho môže spracovať a connection môže zlyhať pred doručením response. Klient potom nevie, či operácia prebehla.

```text
request doručený
server vykonal side effect
response sa stratila
client timeout
client retry
```

Transportná reliability preto neposkytuje business-level exactly-once. API potrebuje idempotency key, deduplication, transaction status alebo bezpečný reconciliation model.

## 33. Pozorovanie TCP a UDP v Linuxe

```bash
ss -lntup
ss -tan
ss -uan
ss -ti
ss -s
lsof -i
```

Pri každom výstupe over:

- Namespace — hostový socket inventory nemusí obsahovať kontajnerový namespace.
- Bind address — loopback listener nie je dostupný zvonku.
- Protocol — TCP a UDP port space sú oddelené.
- State — listening socket, established connection a UDP endpoint majú iný význam.
- Queue — vysoké send/receive queue môže ukazovať backpressure.
- Owner — proces, ktorý socket vytvoril, nemusí byť totožný s procesom, ktorý ho neskôr zdedil alebo obsluhuje.

## 34. Packet capture ako transportný dôkaz

```bash
sudo tcpdump -ni any 'tcp port 443'
sudo tcpdump -ni any 'udp port 53'
```

TCP capture umožní rozlíšiť:

- SYN bez odpovede — packet alebo return path sa stráca, prípadne server neodpovedá.
- RST — aktívne odmietnutie alebo chýbajúci listener.
- Úspešný handshake — L4 setup funguje, ďalšia chyba je v TLS, aplikácii alebo neskoršom transporte.
- Retransmissions — sender nedostáva očakávané ACK.
- Zero window — receiver nemá buffer capacity alebo aplikácia nečíta.
- FIN/RST po prvých bytes — protokolová alebo aplikačná policy connection ukončila.

Pri UDP capture treba poznať aplikačný request/response formát a transaction identity. UDP samo neposkytuje handshake state.

## 35. Diagnostický postup: TCP connect timeout

```bash
getent ahosts example.com
ip route get <resolved-ip>
ss -tan dst <resolved-ip>:443
nc -vz example.com 443
tcpdump -ni any 'host <resolved-ip> and tcp port 443'
```

Postupuj podľa dôkazu:

1. Resolver — over, ktorú IP family a adresu klient reálne používa.
2. Route — potvrď interface, gateway a source address.
3. SYN — zisti, či odchádza z očakávaného namespace a interface.
4. SYN-ACK alebo RST — rozlíš tichý drop od explicitného odmietnutia.
5. Return path — ak server odpovedá, over, kam odpoveď smeruje.
6. Handshake completion — skontroluj, či posledný ACK dorazí serveru.
7. Vyššia vrstva — po úspešnom handshake pokračuj TLS a aplikačnou diagnostikou.

## 36. Diagnostický postup: veľa `CLOSE-WAIT`

1. Identifikuj proces a konkrétne sockets cez `ss -tanp` alebo `lsof`.
2. Packet capture potvrď, že remote peers posielajú FIN.
3. Skontroluj thread, goroutine alebo event-loop stack, ktorý má socket zavrieť.
4. Sleduj počet file descriptors a connection-pool state v čase.
5. Over timeout a cancellation paths aplikácie.
6. Oprav cleanup logiku a následne over, že počet `CLOSE-WAIT` nekumulatívne klesá.

`CLOSE-WAIT` čaká na lokálnu aplikáciu, nie na sieťový timeout.

## 37. Diagnostický postup: UDP request bez odpovede

1. Zachyť odoslaný datagram na klientovi a over destination, source port a transaction ID.
2. Over route, firewall, NAT a MTU na forward path.
3. Zachyť request na receiveri v správnom network namespace.
4. Over UDP listener, bind address a receive-buffer drops.
5. Skontroluj aplikačné logy, parser a request identity.
6. Zachyť response na receiveri.
7. Over return route, NAT state a firewall.
8. Skontroluj ICMP errors a klientsky timeout/retry model.

Bez capture na oboch stranách sa „UDP timeout“ nedá spoľahlivo priradiť requestu, response ani aplikácii.

## 38. Časté omyly

### „TCP garantuje presne jedno spracovanie“

TCP garantuje ordered byte delivery alebo chybu connection. Negarantuje, že business operácia neprebehne dvakrát po aplikačnom retry.

### „UDP je vždy rýchlejší“

UDP má menší základný transportný mechanizmus, ale vyšší protokol môže pridať handshake, encryption, recovery a congestion control. Výsledná latency závisí od celého stacku.

### „Veľa `TIME-WAIT` je memory leak“

`TIME-WAIT` je normálny correctness state. Hodnotí sa jeho dopad na port, conntrack a memory capacity, nie samotná existencia.

### „Handshake znamená zdravú službu“

Handshake potvrdzuje vytvorenie TCP transportu. Aplikácia môže byť preťažená, odmietnuť protokol alebo zlyhať počas TLS.

### „UDP nemá žiadny stav“

UDP protokol nemá TCP state machine, ale socket queues, conntrack, NAT a aplikácia môžu udržiavať významný stav.

### „Packet capture ukazuje presne to, čo vidí fyzický link“

Offloading, namespaces, tunnels a capture point môžu meniť zobrazené segmenty a headers. Observation point musí byť súčasťou interpretácie.

## 39. Kontrolné otázky

1. Prečo TCP nezachováva hranice aplikačných správ?
2. Ktoré hodnoty identifikujú TCP connection?
3. Čo sa dohodne alebo inicializuje počas three-way handshakeu?
4. Ako sa líši flow control od congestion control?
5. Prečo jedna strata blokuje delivery neskorších bytes v rovnakom TCP streame?
6. Aký je rozdiel medzi SYN queue a accept queue?
7. Čo presne signalizujú `CLOSE-WAIT` a `TIME-WAIT`?
8. Ako vzniká ephemeral port exhaustion?
9. Prečo UDP timeout neodhaľuje, kde sa správa stratila?
10. Prečo veľký UDP datagram predstavuje prevádzkové riziko?
11. Ako môže byť QUIC reliable, hoci používa UDP?
12. Prečo TCP reliability neposkytuje business-level exactly-once?
13. Ako packet capture rozlíši tichý drop od aktívneho odmietnutia?

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Routing a default gateway](routing-and-default-gateway.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ports a sockets →](ports-and-sockets.md)
<!-- KNOWLEDGE-NAVIGATION:END -->