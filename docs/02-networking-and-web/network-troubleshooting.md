# Network troubleshooting

Network troubleshooting je proces lokalizácie prvého chýbajúceho alebo nesprávneho transitionu na komunikačnej ceste. Nezačína zoznamom príkazov, ale presným symptómom, subject identity, časom a scope-om.

Jedna používateľská operácia môže zahŕňať viac identít:

```text
hostname a DNS answer
→ IP address a route
→ packet a transportný tuple
→ socket a process
→ TLS session a peer identity
→ HTTP request a proxy attempt
→ backend operation a business outcome
```

Každý observation point vidí iba časť cesty. Client capture nevie automaticky povedať, čo prijal backend. Proxy log nemusí dokazovať, že client dostal response. Absencia logu nie je dôkaz, kým nie je overená log coverage.

Základný workflow:

```text
presný symptom
→ timeline a recent changes
→ scope zdravých a chybných cohorts
→ flow/request/business identity
→ preservation volatile evidence
→ path a enforcement inventory
→ competing hypotheses
→ diskriminačný test
→ minimálne containment
→ oprava authoritative state-u
→ positive, negative a business verification
```

„Ping funguje“ dokazuje iba určitý ICMP path. „Port je otvorený“ môže dokazovať TCP handshake, nie TLS alebo HTTP. Zelený health endpoint môže používať inú route, payload, dependency alebo backend cohort než reálny request.

Competing hypotheses majú predpovedať odlišné dôkazy. Pri timeoute väčších payloadov môžu byť kandidátmi application size limit, proxy buffering, congestion, packet loss alebo PMTU black hole. Porovnanie malého a veľkého requestu, captures pred a za tunnelom a ICMP feedback má vyššiu diskriminačnú hodnotu než opakovaný restart služby.

Preserve-first znamená zachovať pcap, counters, conntrack, route, ruleset, logs a generation identity pred zásahom, ktorý volatile state zničí. Containment má mať úzky scope a rollback.

Incident sa uzatvára až pôvodným user journey a business outcome-om, nie iba zeleným technickým probe. Zároveň sa overuje zakázaný flow a susedné cohorts, aby oprava nevytvorila security alebo availability regresiu.

Network troubleshooting nezačína príkazom. Začína presným používateľským symptómom, flow identity a časom. Vrstvy z predchádzajúcich kapitol poskytujú mapu, no incident sa rieši hľadaním prvého chýbajúceho transitionu, nie mechanickým vykonaním rovnakého checklistu pri každom probléme.

Nosný incident tejto kapitoly:

> Od 10:14 klienti z pobočky A dokončia `GET /healthz`, ale `POST /v1/orders` s payloadom väčším než približne 1 300 bytes timeoutuje po desiatich sekundách. Klienti z datacentra a malej testovacej pobočky problém nemajú. Zmena začala po migrácii WAN tunela. API môže request spracovať, preto každý test používa nový `Idempotency-Key`.

Toto tvrdenie už oddeľuje location, operation, payload size, čas a change correlation. „Sieť je pomalá“ by neposkytla žiadnu diskriminačnú vetvu.

## 1. Zachovaj presný subject

Pre jeden reprodukčný request sa zaznamená:

```text
client:          10.24.8.37
hostname:        api.atlas.example
DNS answer:      203.0.113.40
protocol:        TCP/TLS/HTTP
client port:     53144
destination:     203.0.113.40:443
method/path:     POST /v1/orders
request ID:      req-7f31
idempotency key: incident-20260801-001
payload size:    4096 bytes
time:            2026-08-01T10:14:32+02:00
```

Bez tejto identity sa client capture, firewall log, proxy access log a backend audit nedajú spojiť. Source port a tuple sa pri retry zmenia, preto aplikačné IDs zostávajú potrebné aj po transportnom korelovaní.

## 2. Najprv chráň business outcome

POST môže mať unknown outcome. Pred opakovaním treba vedieť, či API podporuje idempotency alebo query podľa operation identity. Testovací request používa nový key a nepracuje s reálnou platbou.

```bash
payload=$(python3 - <<'PY'
import json
print(json.dumps({
    "customerId": "diagnostic",
    "currency": "EUR",
    "note": "x" * 4096
}))
PY
)

curl --verbose --trace-time \
  --connect-timeout 3 \
  --max-time 10 \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: incident-20260801-001' \
  -H 'X-Request-ID: req-7f31' \
  --data "$payload" \
  https://api.atlas.example/v1/orders
```

Ak client timeoutuje, backend business store sa skontroluje podľa idempotency key. Absencia client response neznamená absenciu commitu.

## 3. Vytvor časovú os a scope

Zmena WAN tunela o 10:10 je relevantná, ale nie je automaticky root cause. Timeline:

```text
10:10 nový tunnel generation aktivovaný pre pobočku A
10:14 prvý large-POST timeout
10:15 GET a malé POST stále fungujú
10:18 synthetics z datacentra zelené
10:22 proxy error rate bez výrazného nárastu
```

Scope ukazuje, že hostname, API release a backend fleet sú spoločné zdravým aj chybným klientom. Rozdiel je source location a payload size. Tým sa znižuje pravdepodobnosť všeobecného backend outage-u a rastie význam path MTU, tunnel policy, branch firewallu alebo client-specific proxy.

## 4. Rozlož path na transitions

Pre incident sa vytvorí mapa:

```text
application vytvorí payload
→ stub resolver vráti address
→ kernel vyberie route a source
→ ARP/NDP vyrieši gateway
→ packet vstúpi do WAN tunela
→ firewall/NAT povolí a preloží flow
→ TCP handshake
→ TLS handshake
→ HTTP headers
→ request body
→ edge proxy
→ backend
→ durable business result
→ response späť klientovi
```

Zdravý `GET /healthz` dokazuje DNS, route, handshake a malý HTTP round trip pre daný čas. Nedokazuje prenos veľkého request body. Prvý chýbajúci transition je preto po úspešnom TLS, pri prenose väčších data segments.

## 5. Competing hypotheses

Namiesto okamžitého záveru „MTU“ sa zachovajú možnosti, ktoré predpovedajú navzájom odlišné observation results:

1. **Client alebo lokálny proxy limituje request body.** Predikciou je lokálne odmietnutie alebo rýchly `4xx`, často bez odoslania celého body na WAN. Client log alebo lokálny proxy log má obsahovať konkrétny limit; packet capture nemá ukazovať opakované retransmissions rovnakého sequence range-u.
2. **Edge proxy bufferuje request a prekročí vlastný timeout.** Client môže upload dokončiť a edge môže prijať headers alebo celé body, ale upstream attempt vznikne neskoro alebo vôbec. Rozhodujú proxy timing fields, buffer counters a rozdiel medzi client-side a upstream-side capture.
3. **Backend číta body pomaly alebo čaká na dependency.** Edge už request priradil backendu, backend log pozná request ID a transport môže ukázať zmenšujúce sa receive window alebo application stall. Táto hypotéza predpovedá backend evidence, ktoré pri path failure chýba.
4. **Packet loss alebo congestion sa prejavuje pri dlhšom prenose.** Failure nemusí mať stabilný size threshold; mení sa s časom, loadom a route. Captures môžu ukázať loss aj pri menších flows, rast RTT alebo congestion-window recovery namiesto stále rovnakého chýbajúceho segmentu.
5. **Path MTU sa po novom tunnel-e znížil a ICMP feedback je blokovaný.** Predikciou je opakovateľný threshold, retransmission rovnakých väčších sequence ranges, absencia requestu za chybným hopom a chýbajúca ICMP `fragmentation needed` alebo ICMPv6 `Packet Too Big` správa.
6. **Security zariadenie zahadzuje konkrétny TLS record alebo payload pattern.** Failure sa viaže na stabilný record alebo content signature, nie iba na veľkosť packetu. Dôkazom sú policy/drop counters, trace na zariadení alebo controlled test s rovnakou veľkosťou a odlišným payloadom.

Hypotéza je užitočná iba vtedy, keď možno pomenovať observation point, očakávaný dôkaz a výsledok, ktorý ju oslabí. Controlled pair malého a veľkého requestu rozlíši size threshold; captures pred a za tunnelom lokalizujú prvý chýbajúci hop; proxy a backend logs oddelia network path od application processingu. Takýto test má vyššiu diskriminačnú hodnotu než séria restartov, ktorá naraz zmení transportný, aplikačný aj volatile evidence state.

## 6. Porovnaj malý a veľký request

Vykonaj controlled pair s rovnakým endpointom a odlišnou veľkosťou:

```bash
for size in 100 1000 1300 1400 4000; do
  body=$(python3 - "$size" <<'PY'
import json, sys
size = int(sys.argv[1])
print(json.dumps({"note": "x" * size}))
PY
)
  printf 'size=%s ' "$size"
  curl --silent --show-error \
    --connect-timeout 2 --max-time 5 \
    -o /dev/null -w 'code=%{http_code} total=%{time_total}\n' \
    -H 'Content-Type: application/json' \
    -H "Idempotency-Key: mtu-$size-$(date +%s%N)" \
    --data "$body" \
    https://api.atlas.example/v1/orders || true
done
```

Jasný threshold okolo packet size podporuje MTU alebo fragmentation hypothesis. Náhodná väzba na čas alebo backend by skôr ukazovala capacity, LB cohort alebo intermittent loss. `|| true` v ukážke zámerne zabraňuje ukončeniu loopu po prvom neúspešnom `curl`; zároveň však maskuje výsledný shell exit status. Úspech sa preto nesmie odvodzovať z toho, že loop dobehol. Pre každý size sa číta HTTP code, total time, stderr a podľa potreby samostatne zachytený `curl` return code.

Test stále mení application state, preto používa diagnostický tenant a stable deduplication. Bez bezpečného endpointu sa veľkostný test vykoná proti echo alebo upload canary mimo produkčnej business operácie. Rovnaký payload sa neopakuje s náhodne menenou business identitou bez kontroly backend store-u, pretože timeout môže mať unknown outcome.

## 7. Client observation

Pred capture sa uloží route, interface MTU a socket state:

```bash
date --iso-8601=seconds
getent ahosts api.atlas.example
ip route get 203.0.113.40
ip link show
tracepath 203.0.113.40
ss -ti dst 203.0.113.40
```

Tieto commands nemajú spoločnú success semantics. `getent` ukazuje address set cez OS name-service path, `ip route get` vykoná lokálny lookup pre aktuálny namespace a `tracepath` iba odhaduje path a PMTU podľa prijatého feedbacku. `ss -ti` číta existujúci socket a jeho transportný state; prázdny výstup môže znamenať, že flow už zanikol alebo sa command spustil v inom namespace. Exit status nula preto nie je spoločným oracle-om. Každý output sa uloží s časom a interpretuje iba pre vrstvu, ktorú pozoruje.

Potom capture:

```bash
sudo tcpdump -ni any \
  -s 0 -w client-req-7f31.pcap \
  'host 203.0.113.40 and tcp port 443'
```

Vo Wireshark alebo `tshark` sa hľadajú retransmissions, duplicate ACKs, MSS, segment sizes a čas po handshake. Pre TLS payload nie je viditeľný HTTP obsah, ale transportný behavior zostáva pozorovateľný.

Client capture ukáže:

```text
TCP handshake OK
TLS handshake OK
malé encrypted records ACKované
segment s väčším payloadom odoslaný
rovnaký sequence range opakovane retransmitovaný
žiadny ACK pre chýbajúce bytes
```

To oslabuje proxy size-limit hypotézu, pretože request ešte pravdepodobne nedosiahol edge.

## 8. Porovnaj captures na oboch stranách tunela

Capture iba na clientovi nevie určiť, kde packet zmizol. Na branch edge a central edge sa použije rovnaký čas, tuple a request ID:

```bash
sudo tcpdump -ni <tunnel-or-wan-interface> \
  -s 0 -w branch-edge-req-7f31.pcap \
  'host 203.0.113.40 and tcp port 443'
```

```bash
sudo tcpdump -ni <central-ingress-interface> \
  -s 0 -w central-edge-req-7f31.pcap \
  'host <translated-client-ip> and tcp port 443'
```

Ak branch ingress vidí veľký packet, ale tunnel egress alebo central ingress nie, failure domain je tunnel encapsulation, MTU alebo policy pred central edge. Ak central edge packet vidí, pokračuje sa proxy a backend observationom.

Capture môže používať offload a zobrazovať zdanlivo väčšie segments pred reálnym rozdelením. Pri potrebe sa kontrolujú GRO/GSO/TSO effects a capture point. Jedno „oversized“ packet zobrazenie na hoste nie je automaticky wire size.

## 9. Path MTU Discovery

IPv4 sender typicky používa Path MTU Discovery s DF behaviorom. Router alebo tunnel endpoint, ktorý nevie packet forwardovať bez prekročenia MTU, má vrátiť ICMP Destination Unreachable, fragmentation needed. IPv6 router packet nefragmentuje a používa ICMPv6 Packet Too Big.

Ak firewall tento feedback zahodí:

```text
sender odosiela príliš veľký packet
→ path ho nevie preniesť
→ ICMP feedback sa stratí
→ sender sa nedozvie nižšie PMTU
→ retransmituje rovnakú veľkosť
→ connection „zamrzne“ po určitom objeme dát
```

`tracepath` môže odhadnúť PMTU, no nie každý path alebo policy poskytne úplný výsledok. Diskriminačný test môže dočasne znížiť interface alebo route MTU na jednom diagnostickom hoste:

```bash
sudo ip route replace 203.0.113.40 via 10.24.8.1 mtu 1280
```

Ak veľký POST po znížení MTU prejde, hypothesis je silná. Je to mitigation experiment, nie finálna oprava; musí byť scope-nutý a po teste odstránený.

## 10. Effective tunnel a firewall state

Zmena znížila tunnel effective MTU z 1500 na 1380 bytes kvôli encapsulation overheadu. Branch interface však stále inzeruje 1500 a firewall blokuje potrebné ICMP feedback messages.

Kontroluje sa:

```bash
ip -d link show <tunnel-interface>
ip route show table all
nft -a list ruleset
nft monitor trace
```

Na vendor zariadení sa hľadajú ekvivalentné effective MTU, MSS clamp, drop counters a ICMP policy. Management config musí byť porovnaný s runtime dataplane generation.

MSS clamping môže zmierniť TCP SYN-negotiated segment size, ale nerieši všetok non-TCP traffic a nemá nahradiť správny PMTU/ICMP design. Oprava má byť zvolená podľa tunnel a platformového contractu.

## 11. Proxy a backend evidence

Proxy access log pre `req-7f31` chýba. To je negatívny dôkaz iba vtedy, keď je potvrdená log coverage a request ID by bol zaznamenaný po prijatí headers. Proxy listener metrics ukazujú TCP spojenie, ale žiadny complete HTTP request.

Backend log a audit takisto request nevidia. Tento evidence chain odlišuje path failure od pomalého business processingu. Absencia z central logs bez coverage kontroly by však nebola dôkazom; collector mohol mať vlastný problém.

## 12. Containment

Najrýchlejšia bezpečná mitigation môže byť:

```text
scope-nutý route MTU alebo TCP MSS clamp pre pobočku A
→ obnova veľkých requests
→ zachovanie ostatných cohorts
→ monitorovanie retransmissions a business completion
```

Containment sa aplikuje na presný tunnel generation a prefix, nie globálne na všetky sites. Zároveň sa zachovajú pcap, ruleset, tunnel config, counters a change metadata pred ďalšími zásahmi.

Rollback WAN zmeny je možný iba ak je stále kompatibilný s routing a security state-om. „Vráť všetko späť“ bez inventory môže vytvoriť ďalšiu asymetriu.

## 13. Autoritatívna oprava

Maximum Transmission Unit (MTU) je najväčší IP packet, ktorý konkrétny link alebo tunnel interface prenesie bez ďalšieho rozdelenia. Path MTU (PMTU) je najnižšia takáto hranica na celej ceste. ICMP pri IPv4 a ICMPv6 pri IPv6 prenášajú spätnú väzbu, že packet je pre ďalší hop príliš veľký. TCP Maximum Segment Size (MSS) je iná hodnota: počas handshake-u obmedzuje TCP payload v jednom segmente a nepokrýva UDP ani všetky neskoršie zmeny pathu.

Trvalá oprava preto zladí viac states, nie iba jeden command:

1. **Tunnel a underlay majú správny configured aj effective MTU.** Source-of-truth hodnota zohľadní encapsulation overhead a runtime read-back na active aj standby generation potvrdí, že ju data plane skutočne používa.
2. **Routers a firewally povoľujú potrebný PMTU feedback.** Policy explicitne povoľuje príslušné ICMP `fragmentation needed` a ICMPv6 `Packet Too Big` messages v správnom directione; counters a capture dokazujú, že feedback prechádza, nie iba že allow rule existuje.
3. **TCP MSS clamping sa používa iba ako schválený doplnkový mechanizmus.** Je scope-nutý na správne interface-y a TCP handshakes, má zdokumentovanú hodnotu a neprezentuje sa ako oprava UDP, ICMP alebo všeobecného MTU contractu.
4. **Ad-hoc containment sa premietne do autoritatívnej konfigurácie a rollout lifecycle-u.** Candidate prejde review, nasadí sa na všetky požadované generations a po replacement-e alebo failoveri sa znova overí. Ručný `ip route ... mtu` na jednom edge môže obnoviť službu, ale bez tejto transformácie ponechá drift a problém sa vráti.

## 14. Verification po oprave

Overenie sa viaže na pôvodný symptóm a používa viac nezávislých acceptance paths. Positive path je povolená používateľská operácia, ktorú mala oprava obnoviť. Negative path je flow, ktorý musí zostať zakázaný. Adjacent cohort je susedná skupina hostov, address family alebo tunnel generation, ktorá nebola pôvodne chybná, ale mohla byť opravou nechtiac ovplyvnená.

### Positive application path

Z pôvodne chybnej pobočky musí prejsť malý `GET`, teda read-only HTTP request, aj veľký `POST`, teda mutating request s request body. POST používa novú operation identity a idempotency key. Backend store potvrdí presne jeden durable outcome, zatiaľ čo client response sa overí samostatne; tým sa nezamieňa úspešný commit za úspešné doručenie odpovede.

### Transport recovery

Packet capture už nesmie ukazovať opakované retransmissions rovnakého TCP sequence range-u a latency aj throughput musia zostať v definovanom limite. Controlled oversized probe zároveň vyvolá očakávaný ICMP alebo ICMPv6 PMTU feedback na správnych observation points, prípadne zvýši presne určené counters. Samotná absencia timeoutu bez tohto transportného read-backu by nevysvetlila, prečo oprava funguje.

### Proxy, backend a client correlation

Rovnaký request ID sa musí objaviť na edge proxy aj na backend-e a odpoveď sa musí vrátiť pôvodnému clientovi. Request ID je korelačná identita konkrétneho pokusu, nie automaticky durable business operation. Samotný backend log preto nie je postačujúci: môže dokazovať prijatie alebo spracovanie requestu, ale nie client completion.

### Negative security path

Zakázaný inbound flow a priame obídenie reverse proxy zostávajú blocked. Firewall policy po zmene povoľuje iba PMTU feedback a presne definovaný service path; nesmie vytvoriť všeobecnú ICMP alebo application reachability. Negative test sa vykoná z reprezentatívneho nedôveryhodného source-u a jeho očakávané odmietnutie sa odlíši od náhodného timeoutu.

### Adjacent cohorts

Zdravé pobočky, obe používané address families a reprezentatívne tunnel generations nesmú mať regresiu. Tento test odhalí opravu viazanú iba na jeden host, jednu cache alebo active edge. Porovnáva sa rovnaký operation contract a rovnaké observation boundaries, nie iba všeobecný ping.

### Second operation a recovery generation

Po skončení prvého requestu sa vykoná druhý veľký POST s novým idempotency keyom, aby sa preukázalo, že systém nefungoval iba vďaka stale connection alebo jednorazovému cache state-u. Následne sa vykoná controlled failover alebo replacement edge-u a rovnaký positive aj negative contract sa zopakuje bez ručného runtime patchu. Tým sa dokazuje, že oprava prežila novú configuration a process generation.

Large-payload synthetic sa pridá do branch capability canary. Monitoring sleduje PMTU-related drops, retransmissions, ICMP feedback a tunnel generation coverage, aby sa rovnaká odchýlka zistila skôr než používateľským timeoutom.

## 15. Všeobecný preserve-first workflow

Rovnaký spôsob práce platí aj pre iné incidenty:

```text
presný user symptom
→ scope, čas a recent changes
→ hostname/address/flow/request/business identity
→ volatile evidence pred restartom
→ path a enforcement inventory
→ prvý chýbajúci transition
→ competing hypotheses
→ diskriminačný test
→ najmenšia bezpečná containment
→ oprava authoritative state-u
→ positive, negative a business verification
→ adjacent cohort a second-change closure
```

Commands sa vyberajú podľa otázky. `ping` nie je univerzálny network test, `telnet port` nepreukazuje TLS/HTTP a packet capture z nesprávneho namespace môže byť presný pre nesprávny flow.

## Zhrnutie

Sieťový incident sa uzatvára kauzálnym reťazcom od používateľského outcome-u k prvému chýbajúcemu transitionu. V Atlas incidente DNS, route, TCP a TLS fungovali, ale väčší packet sa stratil po zmene tunnel MTU a blokovanom ICMP feedbacku. Oprava nebola „reštartovať proxy“, ale zosúladiť effective MTU, firewall policy a runtime evidence a potom overiť jeden business outcome aj zakázané flows.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Praktický sieťový projekt od namespace po HTTPS request](networking-practical-walkthrough.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Git object model →](../03-git-and-automation/git-object-model.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
