# Ethernet, MAC a ARP

Klient `10.24.8.37` chce odoslať packet na verejnú API adresu `203.0.113.40`. Destination nie je v lokálnom prefixe, takže kernel vyberie gateway `10.24.8.1`. Pred odoslaním IP packetu však potrebuje linkovú adresu gatewaya. Ethernet a ARP riešia práve tento prvý lokálny hop.

Ethernet neposkytuje end-to-end routing. Doručuje frames v jednej broadcast doméne alebo VLAN. Router frame prijme, odstráni ho a pre ďalší link vytvorí nový. Preto sa pri každom routovanom hope menia linkové adresy, aj keď IP packet pokračuje k rovnakému cieľu.

## Frame na klientskom linku

Frame pre Atlas request obsahuje približne:

```text
destination MAC: MAC gatewaya 10.24.8.1
source MAC:      MAC klienta
EtherType:       IPv4 alebo IPv6
payload:         IP packet
FCS:             linková kontrola integrity
```

Destination MAC nie je MAC servera `api.atlas.example`. Server je mimo lokálnej broadcast domény a klient pozná iba next hop. To je častá chyba pri čítaní capture: linková destination opisuje nasledujúce zariadenie, IP destination opisuje routovaný cieľ.

```bash
ip link show dev eth0
ip addr show dev eth0
ip route get 203.0.113.40
ip neigh show dev eth0
```

`ip route get` určí route a source address. `ip neigh` ukáže neighbor state pre next hop. Ani jeden príkaz nepreukazuje, že frame skutočne odišiel alebo že switch ho doručil; na to treba interface counters alebo capture.

## Ako switch forwarduje

Switch sa učí source MAC adresy z prijatých frames a priraďuje ich k portu a VLAN. Keď pozná destination MAC, pošle frame iba na príslušný port. Unknown unicast a broadcast typicky flooduje v rámci VLAN, nie cez routované siete.

VLAN tag oddeľuje logické broadcast domény na spoločnej fyzickej infraštruktúre. Access port obvykle prenáša jednu VLAN bez tagu smerom ku koncovému hostu. Trunk prenáša viac VLAN s 802.1Q tagom. Native VLAN a rozdielna trunk konfigurácia môžu vytvoriť problém, pri ktorom link svieti, ale hosty sú v inej broadcast doméne.

Switch forwarding table je dynamický state s ageingom. Po presune VM alebo failoveri sa rovnaká MAC môže objaviť na inom porte. Krátkodobé stale learning alebo security policy na porte môže zablokovať frames, hoci IP konfigurácia je správna.

## ARP ako neighbor resolution

Pre IPv4 klient pošle ARP request ako broadcast:

```text
Who has 10.24.8.1?
Tell 10.24.8.37.
```

Gateway odpovie unicastom so svojou MAC. Klient výsledok uloží do neighbor cache a môže vytvoriť Ethernet frame. ARP neoveruje vlastníctvo IP cryptograficky; dôveruje odpovedi v lokálnej doméne. Preto existujú ARP spoofing a poisoning attacks a ochrany ako dynamic ARP inspection alebo statické bindings v citlivých segmentoch.

```bash
ip neigh get 10.24.8.1 dev eth0
sudo arping -I eth0 10.24.8.1
sudo tcpdump -eni eth0 'arp or host 203.0.113.40'
```

`arping` overuje lokálnu neighbor reachability. Neoveruje, že gateway má route ďalej. ARP môže byť zdravé a end-to-end request stále zlyhá na ďalšom routeri, firewalle alebo aplikácii.

## Neighbor state nie je iba prítomný alebo neprítomný

Linux používa neighbor states ako `REACHABLE`, `STALE`, `DELAY`, `PROBE`, `FAILED` a `INCOMPLETE`. `STALE` neznamená chybu; znamená, že entry nebola nedávno potvrdená a pri ďalšom použití sa môže overiť. `INCOMPLETE` znamená, že resolution prebieha. `FAILED` signalizuje, že pokusy nepriniesli použiteľnú odpoveď.

Ak sa gateway MAC zmení po HA failoveri, gratuitous ARP môže aktualizovať cache hostov a switchov. Ak je oznámenie blokované alebo sa stratí, časť klientov môže dočasne posielať frames na starú MAC. Reset celej siete je hrubá mitigation; presnejšie je potvrdiť neighbor a switch-table state na postihnutom segmente.

## IPv6 používa NDP

IPv6 nepoužíva ARP. Neighbor Discovery Protocol prenáša Neighbor Solicitation a Neighbor Advertisement cez ICMPv6 a multicast. NDP zároveň podporuje router discovery, prefix information a duplicate-address detection. Blokovanie ICMPv6 preto neodstráni iba „ping“; môže rozbiť základnú IPv6 funkciu.

Pri dual-stack incidente treba kontrolovať obe rodiny:

```bash
ip -4 neigh
ip -6 neigh
ping -c 2 10.24.8.1
ping -6 -c 2 fe80::1%eth0
```

Link-local IPv6 adresa je viazaná na interface scope, preto príkaz obsahuje `%eth0`. Rovnaká link-local adresa môže existovať na viacerých rozhraniach.

## Incident: gateway odpovedá iba niektorým klientom

Po výmene redundantného firewallu zlyháva komunikácia približne polovici pobočky. Route tables sú rovnaké a gateway IP odpovedá z niektorých hostov. Competing hypotheses zahŕňajú VLAN mismatch, stale neighbor cache, switch port security a asymetrický HA state.

Postihnutý host má neighbor entry s pôvodnou MAC v stave `REACHABLE`, pretože aplikačný traffic ju neustále používa. Zdravý host už pozná novú virtual MAC. Capture ukáže frames odchádzajúce na starú MAC bez odpovede. Autoritatívna oprava je korektné gratuitous ARP/HA failover správanie a switch learning, nie periodické manuálne mazanie cache na klientoch.

Po oprave sa overí nový neighbor mapping, obojsmerný packet flow a pôvodný HTTPS request. Samotný `arping` nestačí, pretože business path môže mať ďalší problém.

## Zhrnutie

Ethernet rieši lokálny hop, nie celý internetový path. MAC adresa pomenúva linkový endpoint v broadcast doméne, ARP alebo NDP prekladá next-hop IP na linkovú identitu a switch forwarduje podľa VLAN a learned state-u. Pri diagnostike treba odlíšiť zdravú neighbor resolution od funkčnej route a aplikácie.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: OSI a TCP/IP model](osi-and-tcp-ip-model.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: IPv4, IPv6 a subnetting →](ipv4-ipv6-subnetting.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
