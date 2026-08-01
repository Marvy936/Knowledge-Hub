# DHCP

Atlas notebook sa pripojí do pobočkovej siete a potrebuje viac než IP adresu. Musí získať prefix, default gateway, DNS resolvery, lease lifetime a prípadné routes alebo ďalšie options. DHCP je lifecycle prenájmu konfigurácie, nie jednorazové pridelenie čísla.

## DORA lifecycle

Pri novom IPv4 klientovi sa často používa:

```text
DHCPDISCOVER
→ DHCPOFFER
→ DHCPREQUEST
→ DHCPACK
```

Klient ešte nemá stabilnú IP, preto počiatočné messages používajú broadcast a identifikátory clienta. Server ponúkne address a options, klient vyberie offer a server lease potvrdí.

Packet capture:

```bash
sudo tcpdump -ni eth0 -vvv 'udp port 67 or udp port 68'
```

Capture potvrdí messages na danom segmente. Ak je server v inej sieti, relay agent ich prepošle unicastom a doplní informáciu o source scope-e.

## Lease, renew a rebind

Lease má časovú platnosť. Klient sa pokúša obnoviť ju skôr, než expiruje. V T1 fáze typicky komunikuje s pôvodným serverom; pri T2 rebind fáze hľadá dostupný server širšie. Ak lease expiruje bez obnovy, klient už adresu nemá bezpečne používať.

Dlhý lease stabilizuje konfiguráciu a znižuje load, no spomaľuje zmenu gateway alebo DNS options. Krátky lease urýchli zmenu, ale zvýši dependency na DHCP infraštruktúru a môže zväčšiť outage pri server failure.

```bash
networkctl status
nmcli device show
journalctl -u NetworkManager --since -30min
```

Konkrétne commands závisia od network managera. Treba čítať effective interface state aj lease metadata, nie iba konfiguračný súbor.

## Options sú súčasťou connectivity

DHCP môže odovzdať:

```text
IP address a prefix
default gateway
DNS servers a search domains
lease time
NTP alebo boot options
classless static routes
```

Host môže dostať platnú IP a pingovať lokálny gateway, ale nemať správny DNS alebo route k podnikovej sieti. „DHCP funguje“ preto nie je binárny záver; treba overiť všetky options potrebné pre daný workload.

## Relay a subnet identity

Router alebo relay prijme client broadcast a pošle request serveru. Server vyberie scope podľa relay informácie. Chybný relay address alebo policy môže prideliť lease z nesprávneho subnetu.

Pri redundantných relays môže jeden path dopĺňať odlišné metadata. Symptóm sa potom objaví iba pri časti renewals alebo po failoveri. Server logs, relay capture a client lease sa musia korelovať jedným transaction ID a časom.

## Conflict a duplicate address

Serverova databáza nie je jediný source pravdy. Staticky nakonfigurovaný host, stale lease alebo rogue server môže spôsobiť duplicate IP. Klient môže pred použitím adresy vykonať conflict detection, no nie všetky races sa zachytia.

Duplicate address sa prejavuje premenlivým ARP mappingom, connection resets alebo trafficom doručeným nesprávnemu hostu. Oprava rieši authoritative address management, reservations a rogue source, nie iba manuálne pridelenie ďalšej adresy.

## DHCPv6 a SLAAC

IPv6 host môže získať prefix a default router z Router Advertisements a ďalšie údaje cez SLAAC alebo DHCPv6. DHCPv6 typicky neurčuje default gateway rovnakým spôsobom ako IPv4 DHCP; túto informáciu poskytuje router discovery.

Managed a other-configuration flags v RA naznačujú, či sa má použiť DHCPv6 pre address alebo ďalšie options. Reálne správanie závisí od OS a policy. Pri IPv6 incidente treba kontrolovať RA, NDP, DHCPv6 a DNS configuration ako súvisiace, ale odlišné state machines.

## Security hranice

Rogue DHCP server môže ponúknuť útočníkov gateway alebo DNS. Switch protections ako DHCP snooping viažu trusted server ports a vytvárajú bindings použiteľné pre ďalšie controls. Tieto mechanizmy musia poznať relays, trunks a failover topology; nesprávna policy môže zablokovať legitímny ACK.

## Incident: host má IP, ale interné API nejde

Po migrácii DHCP Atlas notebook dostane `10.24.8.37/24` a gateway `10.24.8.1`. Internet funguje, no `api.atlas.example` sa nepreloží. Nový scope neobsahuje interný DNS `10.24.0.53`; posiela verejný resolver.

`ip addr` a `ping gateway` sú zelené. `resolvectl status` ukáže effective DNS z lease a capture potvrdí, že queries idú nesprávnemu serveru. Oprava zmení DHCP option, vynúti controlled renew a overí DNS aj HTTPS. Monitoring začne kontrolovať kompletný lease contract, nie iba address allocation.

## Zhrnutie

DHCP prenajíma celý host network contract. Address, prefix, gateway, DNS, routes a lifetime musia zodpovedať subnetu a workloadu. Diagnose sleduje transaction od clienta cez relay po server a následne overuje effective host configuration.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: DNS](dns.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: NAT →](nat.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
