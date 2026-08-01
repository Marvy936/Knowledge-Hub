# NAT

Atlas klient používa private adresu `10.24.8.37`, ale verejný edge a internet túto adresu neroutujú ako globálnu identitu. NAT môže pri prechode middleboxom zmeniť source alebo destination IP a port. Nejde o routing ani o firewall policy, hoci všetky tri mechanizmy často existujú na rovnakom zariadení.

Pri diagnostike treba vždy pracovať s dvoma tuples:

```text
original tuple
→ translation a conntrack state
→ translated tuple
```

Bez nich sa log z jednej strany NAT-u nedá spoľahlivo korelovať s capture na druhej strane.

## SNAT a PAT

Source NAT mení source address odchádzajúceho packetu. Port address translation zároveň môže meniť source port, aby mnoho interných flows zdieľalo jednu verejnú IP.

```text
pred NAT:
10.24.8.37:53144 → 203.0.113.40:443

po SNAT/PAT:
198.51.100.20:61002 → 203.0.113.40:443
```

Return packet sa podľa conntrack state-u preloží späť na interný tuple. Server vidí verejnú NAT adresu, nie pôvodný client IP, pokiaľ aplikačná proxy nepridá dôveryhodné metadata.

## DNAT a publikovanie služby

Destination NAT mení destination a používa sa pri publikovaní interného listenera:

```text
client:
198.51.100.31:54000 → 203.0.113.40:443

po DNAT:
198.51.100.31:54000 → 10.50.0.10:443
```

DNAT nevytvorí listener. Ak na `10.50.0.10:443` nič nepočúva, client dostane reset alebo timeout podľa ďalšej policy. Rovnako neotvára firewall automaticky; packet môže byť preložený a následne zahodený v inom hooku.

## Conntrack a obojsmerný state

Stateful NAT potrebuje mapovanie pre oba directions. Linux ho možno pozorovať:

```bash
sudo conntrack -L -p tcp | grep 203.0.113.40
sudo nft list ruleset
```

Conntrack entry môže existovať aj po zániku application procesu, kým timeout nevyprší. Zmena NAT rule preto nemusí okamžite ovplyvniť existujúce connections. Nové a staré flows môžu súčasne používať odlišný translation state.

Pri HA middleboxoch treba synchronizovať state alebo akceptovať, že failover ukončí existujúce connections. Zelená konfigurácia na standby node nepreukazuje, že pozná active tuples.

## Port exhaustion

Jedna verejná IP má obmedzený transportný tuple priestor pre konkrétny destination. Pri veľkom počte krátkych connections alebo dlhých flows môže NAT vyčerpať dostupné source ports.

Symptóm sa často javí ako náhodný outbound timeout. Interné hosty majú voľné ephemeral ports a server je zdravý, ale NAT pool nevie vytvoriť ďalšie unikátne mapping.

Evidence zahŕňa translation counters, allocation failures, destination concentration a connection churn. Oprava môže rozšíriť address pool, zlepšiť connection pooling alebo odstrániť zbytočné retries. Skrátenie timeoutov bez pochopenia trafficu môže poškodiť legitímne long-lived connections.

## Hairpin NAT

Interný client môže používať verejný hostname, ktorý smeruje na VIP pre tú istú internú službu. Hairpin NAT umožní, aby flow vstúpil cez DNAT a vrátil sa do rovnakej internej siete so správnym source translation.

Bez hairpin podpory môže služba fungovať externe, ale z internej siete nie. Split-horizon DNS môže tento path obísť, no vytvára dve answers a ďalší lifecycle. Rozhodnutie má byť explicitné a testované z oboch cohorts.

## NAT a aplikačná identita

NAT zachováva packet forwarding, nie user identity. Backend vidí translated source. Ak security alebo rate limit potrebuje pôvodného klienta, reverse proxy môže pridať `Forwarded` alebo `X-Forwarded-For`, ale iba po odstránení nedôveryhodných client-supplied hodnôt a s jasným trusted-proxy chainom.

Transport source IP nie je vždy používateľ. Môže reprezentovať office NAT, mobile carrier, service mesh proxy alebo cloud egress gateway. Authorization založená iba na source IP má preto obmedzenú dôkaznú hodnotu.

## Incident: iba časť outbound requests timeoutuje

Po raste trafficu začnú Atlas workers náhodne zlyhávať pri volaní partner API. Server partnera je zdravý a interné sockets nie sú vyčerpané. NAT gateway metrics ukážu port-allocation failures pre jednu destination IP.

Competing hypotheses zahŕňali DNS imbalance, partner rate limit, local ephemeral exhaustion a NAT pool. Correlation s translated tuple allocation potvrdí NAT. Containment zníži retry amplification a rozdelí traffic na ďalšiu egress IP. Trvalá oprava pridá connection reuse a capacity alert podľa destination concentration.

## Zhrnutie

NAT mení packet identity a drží translation state. Diagnostika musí poznať original aj translated tuple, direction, rule hook a conntrack lifecycle. NAT nie je firewall ani user identity a jeho zelený rule set nepreukazuje dostupnú port capacity.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: DHCP](dhcp.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Firewally →](firewalls.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
