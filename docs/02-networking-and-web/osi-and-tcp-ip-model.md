# OSI a TCP/IP model

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [Linux networking](../01-linux-and-systems/linux-networking.md)
- Súvisiace témy: Ethernet, IP, TCP, UDP, DNS, HTTP, TLS, troubleshooting

## 1. Definícia

OSI a TCP/IP sú vrstvené modely sieťovej komunikácie. Pomáhajú rozdeliť komplexný prenos dát na menšie zodpovednosti a rozhrania.

Model nie je packet ani konkrétny software stack. Je to spôsob, ako pomenovať vrstvy, encapsulation a hranice zodpovednosti.

## 2. Problém, ktorý riešia

Bez vrstvenia by každá aplikácia musela rozumieť fyzickému prenosu, adresovaniu, routingu, spoľahlivosti aj aplikačnému protokolu ako jednému celku.

Vrstvenie umožňuje:

- meniť jednu technológiu bez úplného prepisu ostatných vrstiev,
- štandardizovať rozhrania,
- oddeliť lokálny prenos od end-to-end komunikácie,
- diagnostikovať problém podľa vrstvy,
- opätovne používať transport a network mechanizmy medzi aplikáciami.

## 3. OSI model

Sedem vrstiev:

| Vrstva | Názov | Typická zodpovednosť |
|---:|---|---|
| 7 | Application | aplikačné protokoly a význam dát |
| 6 | Presentation | encoding, serialization, compression, encryption representation |
| 5 | Session | riadenie session a dialógu |
| 4 | Transport | end-to-end transport, ports, reliability |
| 3 | Network | logické adresovanie a routing |
| 2 | Data Link | lokálny link, frames, MAC addressing |
| 1 | Physical | signál, médium, bity |

OSI model je presný konceptuálny referenčný rámec, ale reálny Internet stack sa často opisuje TCP/IP modelom.

## 4. TCP/IP model

Bežné štvorvrstvové členenie:

| TCP/IP vrstva | Približné OSI vrstvy | Príklady |
|---|---|---|
| Application | 5–7 | HTTP, DNS, SSH, SMTP |
| Transport | 4 | TCP, UDP, QUIC transport functions |
| Internet | 3 | IPv4, IPv6, ICMP |
| Link | 1–2 | Ethernet, Wi-Fi, ARP/NDP context |

Niekedy sa používa päťvrstvový model, ktorý oddeľuje physical a data-link vrstvu.

Dôležité nie je memorovať počet vrstiev, ale vedieť, ktorú zodpovednosť konkrétny mechanizmus rieši.

## 5. Encapsulation

Pri odoslaní dát každá vrstva pridá svoje metadata.

```text
HTTP message
  ↓ TCP header
TCP segment
  ↓ IP header
IP packet
  ↓ Ethernet header + trailer
Ethernet frame
  ↓ physical encoding
bits/signals
```

Na prijímajúcej strane prebieha decapsulation opačne.

Jednotky sa často pomenúvajú:

- application data/message,
- TCP segment,
- UDP datagram,
- IP packet,
- Ethernet frame,
- bits.

Terminológia sa v praxi mieša, ale pri diagnostike je užitočné pomenovať správnu vrstvu.

## 6. Headers a payload

Každá vrstva typicky vníma vyššiu vrstvu ako payload.

```text
Ethernet frame payload = IP packet
IP packet payload       = TCP segment
TCP segment payload     = application bytes
```

Router spravidla nepotrebuje rozumieť HTTP payloadu, aby routoval IP packet. Firewall alebo proxy však môže analyzovať vyššie vrstvy podľa svojej funkcie.

## 7. Adresovanie podľa vrstvy

Rôzne identifikátory riešia rozdielne scope:

| Identifikátor | Vrstva/scope | Príklad |
|---|---|---|
| MAC address | lokálny L2 link | `00:11:22:33:44:55` |
| IP address | routovaný network endpoint | `192.0.2.10` |
| Port | transport endpoint v hoste | `443` |
| DNS name | aplikačný naming | `api.example.com` |
| URL | identifikácia resource/protokolu | `https://api.example.com/v1` |

MAC adresa neidentifikuje server globálne cez Internet. Port bez IP adresy nie je úplný remote endpoint.

## 8. L2 a L3 hranica

Ethernet frame sa prenáša v lokálnom linkovom segmente. IP packet môže prechádzať viacerými routovanými hops.

Pri každom router hop sa môže zmeniť L2 header:

```text
Host A
Ethernet: MAC A → MAC gateway 1
IP:       IP A  → IP B

Router
Ethernet: MAC router 2 → MAC next hop
IP:       IP A         → IP B
```

End-to-end IP adresy typicky zostávajú rovnaké, pokiaľ ich nemení NAT. Link-layer adresy sa menia podľa lokálneho segmentu.

## 9. End-to-end vs. hop-by-hop

### Hop-by-hop

Mechanizmus sa uplatňuje medzi susednými nodes alebo na každom hop-e:

- Ethernet frame,
- neighbor resolution,
- TTL/hop limit decrement,
- queueing na interface.

### End-to-end

Mechanizmus spája pôvodný source a destination endpoint:

- TCP connection,
- application request,
- TLS session typicky medzi klientom a terminujúcim serverom/proxy.

Middleboxes môžu end-to-end model rozdeliť, napríklad TLS termination proxy alebo load balancer.

## 10. Data plane a control plane

### Data plane

Spracúva konkrétne packets alebo frames podľa existujúceho stavu:

- forwarding,
- filtering,
- queueing,
- encapsulation.

### Control plane

Vytvára stav, podľa ktorého data plane rozhoduje:

- routing protocols,
- ARP/NDP neighbor discovery,
- configuration management,
- DNS records,
- orchestration policies.

Pri incidente môže byť data plane zdravý, ale control plane distribuoval chybnú route alebo policy.

## 11. Protokol, služba a implementácia

Tieto pojmy treba odlišovať:

- protokol: pravidlá komunikácie, napríklad HTTP,
- služba: schopnosť poskytovaná používateľovi, napríklad web API,
- implementácia: konkrétny server alebo client software,
- port: transport identifier, nie samotná služba.

Dva programy môžu implementovať rovnaký protokol. Jeden port môže obsluhovať odlišné virtuálne služby podľa TLS SNI alebo HTTP Host headeru.

## 12. Kde patria TLS a QUIC

Nie všetky technológie sa zmestia do jednej vrstvy bez zvyšku.

### TLS

Poskytuje encryption, integrity a peer authentication nad transportom alebo ako súčasť vyššieho transportného stacku. V OSI analógii sa často spája s presentation/session vrstvami, ale prakticky je medzi application protokolom a transportom.

### QUIC

Beží nad UDP, ale implementuje reliability, congestion control, multiplexing a security integráciu, ktoré tradične spájame s transportnou vrstvou a TLS.

Vrstvený model je mapa, nie fyzikálny zákon.

## 13. Troubleshooting podľa vrstiev

Príklad: HTTPS request timeoutuje.

```text
L1/L2: link up? errors? VLAN?
L3: IP, route, source address, return path?
L4: TCP handshake alebo UDP/QUIC flow?
TLS: certificate, SNI, cipher, handshake?
L7: HTTP status, headers, application latency?
```

Príkazy:

```bash
ip link
ip addr
ip route get <IP>
ip neigh
ss -tan
tcpdump -ni any host <IP>
curl -v https://example.com/
openssl s_client -connect example.com:443 -servername example.com
```

Každý nástroj pozoruje inú vrstvu. `curl` failure nemusí znamenať HTTP problém; môže zlyhať DNS, TCP alebo TLS pred odoslaním HTTP requestu.

## 14. Bottom-up a top-down diagnostika

### Bottom-up

Začína od linku a postupuje nahor. Je vhodná, keď nie je jasné, či funguje základná konektivita.

### Top-down

Začína používateľským requestom a znižuje vrstvu podľa konkrétneho failure pointu. Je efektívna pri dobrej observability.

### Divide and conquer

Začne v strede, napríklad overením TCP handshake. Podľa výsledku pokračuje nad alebo pod transportnú vrstvu.

Najlepší postup závisí od dostupných dôkazov.

## 15. Anti-pattern: „Je to L7 problém“ bez dôkazu

Aplikačný timeout môže byť spôsobený:

- packet loss a retransmissions,
- MTU black hole,
- DNS delay,
- SYN backlog,
- TLS handshake,
- backend queueing,
- samotnou aplikáciou.

Názov symptómu neurčuje vrstvu root cause.

## 16. Časté omyly

### „OSI model presne opisuje implementáciu Internetu“

Nie. Je konceptuálny model. Reálne stacks spájajú alebo prekračujú vrstvy.

### „Switch je vždy L2 a load balancer vždy L4“

Produkty môžu implementovať viac vrstiev. Rozhodujú funkcie, nie marketingový názov.

### „MAC adresa putuje cez celý Internet“

Nie. Je relevantná v lokálnom linkovom scope a mení sa na routovaných hops.

### „Port 443 znamená HTTPS“

Je to konvencia. Port neoveruje aplikačný protokol.

### „Keď ping funguje, všetky vrstvy fungujú“

Ping testuje určitý ICMP flow, nie TCP, TLS ani aplikáciu.

## 17. Kontrolné otázky

1. Načo slúži vrstvený model?
2. Ako sa mapuje OSI na TCP/IP model?
3. Čo je encapsulation?
4. Aký je rozdiel medzi frame, packet a segment?
5. Prečo sa L2 header mení na routovaných hops?
6. Aký je rozdiel medzi data plane a control plane?
7. Prečo TLS a QUIC nemožno vždy zaradiť do jednej jednoduchej vrstvy?
8. Ako by si diagnostikoval HTTPS timeout po vrstvách?
