# DHCP

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: Networking and Web Fundamentals
- Predpoklady: [IPv4, IPv6 a subnetting](ipv4-ipv6-subnetting.md), [Ethernet, MAC a ARP](ethernet-mac-arp.md), [DNS](dns.md)
- Súvisiace témy: routing, VLANs, PXE, cloud networking, IP address management

## 1. Definícia

Dynamic Host Configuration Protocol automaticky poskytuje hostom sieťové parametre, napríklad IP adresu, prefix masku, default gateway, DNS servery a lease duration.

DHCP neroutuje traffic ani nevytvára konektivitu. Distribuuje konfiguráciu, ktorú klient následne použije pri lokálnom rozhodovaní.

## 2. Problém, ktorý rieši

Bez centrálnej adresnej konfigurácie musí každý host poznať a manuálne udržiavať:

- unikátnu IP adresu,
- subnet mask alebo prefix,
- gateway,
- DNS resolvery,
- ďalšie environment-specific options.

Pri väčšej sieti vznikajú konflikty, neaktuálne záznamy a nekonzistentné nastavenia.

## 3. DHCPv4 model DORA

Základná sekvencia sa často označuje DORA:

```text
DHCPDISCOVER
  ↓
DHCPOFFER
  ↓
DHCPREQUEST
  ↓
DHCPACK
```

### DHCPDISCOVER

Klient bez platnej adresy hľadá dostupný server. Typicky používa broadcast, source `0.0.0.0:68` a destination `255.255.255.255:67`.

### DHCPOFFER

Server ponúkne adresu a options.

### DHCPREQUEST

Klient vyberie ponuku a explicitne požiada o konkrétnu lease.

### DHCPACK

Server lease potvrdí. Alternatívne môže vrátiť `DHCPNAK`, ak požiadavka nie je platná.

## 4. Lease lifecycle

Lease nie je trvalé vlastníctvo adresy.

Typický lifecycle:

```text
BOUND
  ↓ T1
RENEWING
  ↓ T2
REBINDING
  ↓ expiration
INIT
```

- T1: klient sa pokúša obnoviť lease u pôvodného servera, často unicastom,
- T2: klient skúša ľubovoľný dostupný server,
- expiration: bez úspešnej obnovy musí adresu prestať používať.

T1 a T2 sa často odvodzujú z lease duration, ale server ich môže poskytnúť explicitne.

## 5. DHCP options

Bežné options:

- subnet mask alebo prefix information,
- router/default gateway,
- DNS servers,
- domain search,
- lease time,
- NTP servers,
- MTU,
- classless static routes,
- boot server a boot filename pre PXE.

Klient nemusí podporovať všetky options a lokálna policy môže niektoré ignorovať.

## 6. Scope, pool a reservation

### Scope alebo subnet

Definuje sieť, pre ktorú server poskytuje konfiguráciu.

### Dynamic pool

Rozsah adries prideľovaných klientom.

### Reservation

Stabilné mapovanie identity klienta na konkrétnu adresu. Identita môže používať MAC, client identifier alebo platform-specific atribút.

Reservation nie je rovnaká ako manuálne nastavená statická IP. Stále ide o DHCP-managed konfiguráciu.

## 7. Broadcast boundary a DHCP relay

Router štandardne neforwarduje L2 broadcast medzi subnetmi. DHCP server preto nemusí byť v každom VLAN segmente; používa sa DHCP relay.

```text
client broadcast
  ↓
VLAN gateway / relay agent
  ↓ unicast
central DHCP server
  ↓
relay
  ↓
client
```

Relay pridá informáciu o klientskom segmente, napríklad `giaddr` alebo relay-agent options, aby server vybral správny scope.

Chybný relay môže spôsobiť:

- žiadnu ponuku,
- ponuku z nesprávneho subnetu,
- nesprávnu gateway,
- nesprávnu policy podľa relay metadata.

## 8. Adresný konflikt

Dve zariadenia používajúce rovnakú IP môžu spôsobovať prerušovanú konektivitu a ARP instability.

Príčiny:

- statická IP vo vnútri DHCP poolu,
- dva nekoordino­vané DHCP servery,
- stale lease database,
- obnovenie snapshotu VM s rovnakou identitou,
- chybná reservation,
- rogue DHCP server.

Niektorí klienti alebo servery vykonávajú conflict detection cez ARP probe, ale nemožno sa na to spoliehať ako na jedinú ochranu.

## 9. Rogue DHCP server

Neautorizovaný DHCP server môže rozdávať nesprávnu gateway alebo DNS a presmerovať traffic.

Ochranné mechanizmy na switchi môžu zahŕňať DHCP snooping:

- trusted uplink ports,
- blokovanie server responses na untrusted ports,
- binding database,
- integrácia s Dynamic ARP Inspection alebo source guard.

Tieto funkcie závisia od konkrétnej sieťovej platformy.

## 10. DHCPv6

DHCPv6 používa odlišný protokol a správy než DHCPv4.

IPv6 host môže získať adresu a konfiguráciu kombináciou:

- SLAAC,
- stateful DHCPv6,
- stateless DHCPv6,
- Router Advertisements.

Dôležité je, že default gateway sa v IPv6 typicky získava z Router Advertisement, nie z DHCPv6 option rovnakým spôsobom ako pri DHCPv4.

## 11. SLAAC vs. DHCPv6

### SLAAC

Host vytvorí adresu podľa advertised prefixu a lokálneho interface identifier mechanizmu.

### Stateful DHCPv6

Server prideľuje address lease a vedie stav.

### Stateless DHCPv6

Adresa vznikne cez SLAAC, DHCPv6 poskytne ďalšie options, napríklad DNS.

RA flags a klientská implementácia ovplyvňujú, ktorý model sa použije.

## 12. Linux klienti a pozorovanie

Runtime stav:

```bash
ip addr
ip route
resolvectl status
```

NetworkManager:

```bash
nmcli device show
nmcli connection show
```

systemd-networkd:

```bash
networkctl status
journalctl -u systemd-networkd
```

Lease files a log paths sa líšia podľa klienta a distribúcie. Autoritatívny stav treba hľadať v skutočne používanom network manageri.

## 13. Packet capture

DHCPv4:

```bash
sudo tcpdump -ni eth0 'port 67 or port 68'
```

DHCPv6:

```bash
sudo tcpdump -ni eth0 'port 546 or port 547'
```

Capture pomáha odpovedať:

- odišiel DISCOVER/SOLICIT,
- prišla OFFER/ADVERTISE,
- cez ktorý interface,
- aké options server poslal,
- odpovedal rogue server,
- funguje relay cesta.

## 14. Cloud a virtualizované siete

Cloud platforma môže implementovať DHCP ako virtuálnu službu mimo bežného broadcast modelu. Klient stále vidí lease semantics, ale packet path a server identity môžu byť platform-specific.

Pri VM klonovaní treba kontrolovať:

- MAC a virtual NIC identity,
- machine-id alebo client identifier,
- cloud-init network config,
- persistent udev naming,
- cached lease.

## 15. PXE boot

DHCP môže poskytnúť bootstrapping informácie:

- next-server,
- boot filename,
- architecture-specific options.

Typický tok:

```text
DHCP address/config
  ↓
boot server location
  ↓
TFTP alebo HTTP boot artifact
  ↓
installer / provisioning environment
```

DHCP iba sprostredkuje počiatočné údaje; samotný boot image sa prenáša iným protokolom.

## 16. Diagnostický postup

Host nedostal adresu:

```bash
ip link
ip addr
journalctl -b | grep -i dhcp
sudo tcpdump -ni <iface> 'port 67 or port 68'
```

Postup:

1. je interface administratívne up a má carrier,
2. používa sa správny VLAN/access port,
3. odchádza DISCOVER,
4. prichádza OFFER,
5. existuje relay a správny scope,
6. nie je pool vyčerpaný,
7. server vidí správny client identifier,
8. klient prijal ACK a aplikoval adresu,
9. vznikla route a DNS config,
10. nie je adresa v konflikte.

## 17. Typické symptómy

### Adresa `169.254.0.0/16`

IPv4 link-local fallback môže znamenať, že DHCP konfigurácia nebola získaná. Nie je to univerzálny dôkaz, ale silný signál.

### Adresa existuje, ale nefunguje internet

DHCP mohol poslať nesprávnu gateway, prefix alebo DNS. Tiež môže zlyhávať routing mimo DHCP.

### Lease funguje po reštarte, potom vypadne

Môže zlyhávať renewal cesta, relay alebo firewall pre unicast renewal.

### Niektorí klienti dostanú nesprávny subnet

Skontroluj relay information, overlapping scopes a rogue server.

### Pool exhausted

Server nemá voľnú lease pre nového klienta, hoci staré alebo neaktívne zariadenia stále držia adresy.

## 18. Časté omyly

### „DHCP prideľuje gateway ako sieťové zariadenie“

Nie. Poskytne klientovi informáciu, ktorú adresu má používať ako gateway.

### „Reservation a statická IP sú to isté“

Nie. Reservation je centrálne DHCP-managed mapovanie.

### „DHCP broadcast prejde routerom“

Nie bez relay alebo platform-specific mechanizmu.

### „DHCPv6 vždy poskytuje default gateway“

Nie. Gateway sa typicky učí z Router Advertisements.

### „Keď host dostal IP, DHCP už nemôže byť problém“

Môže byť nesprávny prefix, DNS, gateway, lease renewal alebo classless route.

## 19. Kontrolné otázky

1. Čo predstavuje DORA sekvencia v DHCPv4?
2. Aký je rozdiel medzi T1 a T2?
3. Prečo je potrebný DHCP relay?
4. Aký je rozdiel medzi scope, pool a reservation?
5. Ako vzniká IP conflict pri kombinácii statických a dynamických adries?
6. Čo robí DHCP snooping?
7. Aký je vzťah SLAAC, DHCPv6 a Router Advertisements?
8. Prečo IP adresa sama nedokazuje správnu DHCP konfiguráciu?
9. Ako packet capture odlíši client, relay a server problém?
10. Prečo PXE nepoužíva DHCP na prenos samotného boot image?
