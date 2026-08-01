# OSI a TCP/IP model

OSI a TCP/IP modely sú analytické rámce, ktoré rozdeľujú sieťovú komunikáciu na vrstvy s odlišnými zodpovednosťami. Neopisujú presnú implementáciu každého operačného systému ani zariadenia. Ich účelom je oddeliť typy identít, protokolov a failure boundaries, aby bolo jasné, čo konkrétny dôkaz potvrdzuje.

OSI model tradične rozlišuje sedem vrstiev: physical, data link, network, transport, session, presentation a application. TCP/IP model ich zoskupuje praktickejšie na linkovú, internetovú, transportnú a aplikačnú vrstvu. Moderné protokoly sa nemusia dokonale zmestiť do jednej priehradky. TLS napríklad pracuje nad transportom a pod HTTP, zatiaľ čo QUIC spája transportné a cryptographic funkcie nad UDP.

Encapsulation znamená, že vyššia vrstva odovzdá svoj payload nižšej vrstve, ktorá pridá vlastnú hlavičku alebo obálku:

```text
aplikačná message
→ transportný segment alebo datagram
→ IP packet
→ linkový frame
→ fyzický signál
```

Na prijímacej strane sa obálky spracujú opačným smerom. Hranice messages sa pritom nemusia zhodovať: jeden aplikačný request môže byť rozdelený do viacerých TCP segmentov a jeden TCP segment môže obsahovať časti viacerých aplikačných zápisov.

Model je najpraktickejší pri troubleshootingu. Úspešný link nepreukazuje route, úspešný TCP handshake nepreukazuje TLS identity a HTTP response nepreukazuje správny business side effect. Každá vrstva má vlastné observation points a vlastný subject.

Neutrálny príklad:

```text
browser vytvorí HTTP GET
→ TLS ho zašifruje
→ TCP prenesie byte stream
→ IP vyberie routovaný destination
→ Ethernet doručí packet k lokálnemu next hopu
```

Router typicky odstráni pôvodný Ethernet frame a vytvorí nový pre ďalší link, zatiaľ čo IP destination zostáva rovnaká, ak ju nemení NAT. Proxy môže ukončiť jedno TCP/TLS spojenie a vytvoriť druhé, takže „end-to-end“ treba vždy presne definovať.

Klient Atlas odošle `POST /v1/orders` na `https://api.atlas.example`. Používateľ vidí jednu operáciu, ale systém ju realizuje cez viac kontraktov. DNS preloží meno na adresu, kernel vyberie route, lokálny link doručí frame k next hopu, transport vytvorí spojenie, TLS overí peer identity a HTTP prenesie aplikačný request. Vrstvený model je mapa týchto zodpovedností a observation points.

Nie je to presný obrázok implementácie. Moderný kernel, QUIC, proxy alebo smartNIC môže spájať viac funkcií a jeden komponent môže pracovať na viacerých vrstvách. Model je užitočný vtedy, keď pomôže odpovedať: *ktorý kontrakt zlyhal, kde ho možno pozorovať a čo tento dôkaz ešte nedokazuje?*

## Jeden request, viac obálok

Aplikácia vytvorí HTTP message. TLS ju chráni v recordoch, transport ju prenesie ako TCP byte stream, IP ju rozdelí do packetov a lokálny link vloží packet do Ethernet frame-u.

```text
HTTP request
└── TLS records
    └── TCP segments
        └── IP packets
            └── Ethernet frames
```

Na príjme sa proces obráti. Ethernet interface prijme frame, kernel spracuje IP a TCP state, TLS knižnica overí a dešifruje records a HTTP server zrekonštruuje request. Aplikácia nedostáva „packet“; dostáva stream bytes alebo aplikačnú message podľa svojho runtime-u.

Encapsulation neznamená, že jedna aplikačná message vždy zodpovedá jednému transportnému segmentu. Jeden HTTP request môže byť rozdelený do mnohých segmentov a naopak jeden segment môže niesť časti viacerých vyšších messages. Packet capture preto treba interpretovať podľa protokolu, nie podľa vizuálnej hranice jedného riadku v nástroji.

## OSI a TCP/IP ako dve analytické mapy

OSI model rozlišuje sedem logických vrstiev. TCP/IP model ich zoskupuje praktickejšie do linkovej, internetovej, transportnej a aplikačnej oblasti. Pri diagnostike nie je dôležité hádať, či TLS patrí „presne“ do vrstvy 5, 6 alebo 7. Dôležité je, že má vlastný handshake, identity, cryptographic state a failure evidence odlišné od TCP a HTTP.

Pre Atlas request možno zodpovednosti čítať takto:

```text
application: HTTP semantics, API contract, business result
security/session: TLS handshake, peer identity, encryption
transport: TCP connection, ordering, retransmission, flow control
internet: IPv4/IPv6 address, route, TTL/hop limit
link: Ethernet frame, VLAN, neighbor resolution, next hop
physical: signal, interface, medium a link state
```

Každá vrstva používa fields, ktoré nemusia byť viditeľné na inom observation pointe. Switch pracuje s MAC adresami a VLAN, router s IP prefixmi, TCP stack s tuple a sequence state-om, reverse proxy s SNI, authority, path a headers.

## Hop-by-hop a end-to-end identity

Ethernet frame platí iba na jednom lokálnom linku. Keď router prijme frame, odstráni linkovú obálku a vytvorí nový frame pre ďalší hop. MAC adresy sa teda menia, hoci source a destination IP typicky zostávajú rovnaké.

```text
client frame:
src MAC = client
dst MAC = gateway

router → next network:
src MAC = router egress
dst MAC = next hop
```

NAT môže zmeniť IP adresu alebo port, proxy vytvorí úplne nové transportné spojenie a TLS termination ukončí jeden cryptographic channel a prípadne vytvorí druhý. Preto „end-to-end“ treba vždy spresniť. Client-to-proxy TCP spojenie nie je backendové TCP spojenie a client TLS identity nemusí byť prenesená upstreamu bez explicitného mechanizmu.

## Data plane, control plane a management plane

Request cestuje data plane-om: forwarding tables, conntrack, proxy workers a backend sockets vykonávajú rozhodnutia pre konkrétny flow. Control plane vytvára stav, podľa ktorého data plane pracuje. Routing protocol môže naučiť route, DNS control plane publikuje záznam, load balancer controller mení backend inventory.

Management plane je cesta, ktorou operátor alebo automatizácia konfiguráciu mení. Zelený management API response ešte nepreukazuje, že data plane používa nový state. Po zmene firewall rule alebo route preto treba čítať effective ruleset a vykonať reálny flow.

## Observation point mení význam dôkazu

`curl` na klientovi ukáže DNS timing, connect, TLS a HTTP výsledok z pohľadu daného procesu. `tcpdump` na klientskom interface ukáže frames a packets, ktoré dosiahli tento interface. Capture na reverse proxy ukáže iný transportný flow. Backend access log ukáže request, ktorý proxy skutočne odoslala.

```bash
curl --verbose --trace-time https://api.atlas.example/v1/orders
sudo tcpdump -ni eth0 'host 203.0.113.40 and port 443'
```

Úspešný `SYN, SYN-ACK, ACK` potvrdzuje transportný handshake na pozorovanom path-e. Nepotvrdzuje platný certifikát, správny HTTP route ani vytvorenie objednávky. Backend log s `req-7f31` potvrdzuje, že request dosiahol daný proces, ale nie že databázový commit alebo event publication skončili správne.

## Timeout budget cez vrstvy

Používateľský timeout je súčet viacerých fáz:

```text
DNS lookup          40 ms
TCP connect         35 ms
TLS handshake       55 ms
proxy queue         10 ms
backend processing 180 ms
response transfer   20 ms
```

Pri incidente môže jedna fáza spotrebovať celý budget. DNS retry, SYN retransmission, TLS validation fetch alebo backend queue môžu navonok skončiť rovnakým hlásením „request timed out“. Preto treba merať jednotlivé transitions.

Retry na viacerých vrstvách sa môže násobiť. Klient vykoná dva pokusy, proxy tri a backend SDK ďalšie dva; jedna používateľská operácia môže vytvoriť dvanásť downstream attempts. Vrstvený model preto pomáha aj pri návrhu jednotného deadline a retry budgetu.

## Priebežný incident

Po zmene edge siete Atlas pozoruje, že malé `GET /healthz` fungujú, ale väčší `POST /v1/orders` z pobočky timeoutuje. DNS, TCP aj TLS handshake prejdú. Tento dôkaz posúva prvý chýbajúci transition za handshake, ale ešte nerozhoduje medzi HTTP bufferingom, PMTU black hole, proxy timeoutom a backendom.

Client capture ukáže opakované TCP retransmissions po prvých väčších segmentoch. Edge capture tieto segmenty nevidí a ICMP „fragmentation needed“ alebo IPv6 Packet Too Big sa nevracia. Root cause je path-MTU discovery failure, nie HTTP server. V troubleshooting kapitole sa tento incident rozvinie až po business outcome a recovery.

## Zhrnutie

OSI a TCP/IP model je praktický iba vtedy, keď sa viaže na konkrétny flow. Pomáha odlíšiť linkový frame, IP packet, transportné spojenie, TLS session, HTTP request a business operáciu. Každá identita má vlastné fields, state a observation points. Diagnostika postupuje po prvom chýbajúcom transitione, nie mechanicky od najnižšej vrstvy.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Performance a troubleshooting](../01-linux-and-systems/performance-and-troubleshooting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Ethernet, MAC a ARP →](ethernet-mac-arp.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
