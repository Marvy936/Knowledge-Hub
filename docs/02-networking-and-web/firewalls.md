# Firewally

Firewall je enforcement point, ktorý povoľuje alebo zahadzuje packets alebo flows podľa policy. Verdict nevzniká iba z čísla portu. Závisí od source, destination, protocolu, direction, interface-u, connection state-u, hooku a poradia pravidiel.

Stateless ACL hodnotí každý packet samostatne. Stateful firewall používa connection tracking a rozlišuje napríklad `new`, `established`, `related` a `invalid`. Bežná policy povolí vznik spojenia iba v jednom directione a return packets na základe established state-u.

Na Linux routeri routovaný packet typicky prejde:

```text
ingress
→ prerouting
→ route lookup
→ forward
→ postrouting
→ egress
```

Packet určený lokálnemu procesu ide cez input chain. Pravidlo v input chain-e preto nepovolí traffic, ktorý router iba forwarduje.

Default deny znamená, že neexistujúci explicitný allow skončí dropom. Bezpečnosť však závisí od presnosti allow contractu. Široké pravidlo `allow tcp/443` bez source, destination a direction môže otvoriť viac, než bolo zamýšľané.

Pravidlá sa spracúvajú podľa platformového modelu a priority. Skorší široký drop môže zatieniť neskorší allow; skorší široký allow môže zneplatniť neskorší drop. Counters a trace ukážu, ktoré pravidlo skutočne rozhodlo.

NAT môže zmeniť fields pred filter verdictom. Policy musí byť napísaná pre identitu, ktorú daný hook vidí. To je častý dôvod, prečo rule vyzerá správne, ale jeho counter zostáva nula.

Bezpečná zmena firewallu potrebuje syntax validation, management-path ochranu, timed rollback alebo out-of-band access a následné positive aj negative tests. Úspešný apply príkaz nepreukazuje, že požadovaný flow prejde ani že zakázaný flow zostal zablokovaný.

Firewall rozhoduje, či konkrétny packet alebo flow môže prejsť cez daný enforcement point. Rozhodnutie závisí od direction, hooku, viditeľných fields, connection state-u a poradia pravidiel. Neexistuje univerzálna veta „port 443 je povolený“ bez uvedenia source, destination, protocolu, interface-u a cesty.

## Packet prechádza konkrétnym hookom

Na Linux routeri môže packet prejsť cez `prerouting`, route decision, `forward` a `postrouting`. Packet určený lokálnemu procesu používa input path, packet vytvorený lokálnym procesom output path.

```text
routovaný client packet:
ingress
→ prerouting
→ route lookup
→ forward
→ postrouting
→ egress
```

Rule v `input` chain-e nepovolí forwardovaný traffic. Toto je častý dôvod, prečo konfigurácia vyzerá správne podľa portu, ale packet nikdy neprechádza daným chainom.

## Stateful policy

Stateful firewall používa conntrack classification ako `new`, `established`, `related` alebo `invalid`. Bežný model povolí nové spojenie len v jednom directione a návratové packets ako established.

```nft
ct state established,related accept
ip saddr 10.24.8.0/24 ip daddr 10.50.0.10 tcp dport 443 ct state new accept
counter drop
```

Toto pravidlo je iba ilustrácia. Effective ruleset potrebuje správnu table, family, hook, priority a default policy. `related` traffic má byť povolený iba vtedy, keď je potrebný a rozumie sa helper semantics.

## Default deny a explicitný contract

Default deny znižuje implicitnú reachability, ale bezpečnosť vzniká až z presného allow contractu. Pre Atlas request môže pravidlo definovať:

```text
source: branch client prefix alebo trusted edge
destination: API VIP alebo proxy address
protocol: TCP
destination port: 443
connection state: new,established
direction: client → edge
```

Backend network má odlišný contract: iba reverse proxy smie volať `orders-api:8080`. Client prefix nemá mať priamu route ani firewall allow na backend.

## Poradie a shadowing

Firewally typicky spracúvajú rules podľa priority a prvého rozhodujúceho verdictu. Široký drop pred úzkym allow ho môže zatieniť. Široký allow pred dropom môže policy obísť.

```bash
sudo nft -a list ruleset
sudo nft monitor trace
```

Handles a counters pomáhajú zistiť, ktoré pravidlo sa zhodlo. Trace je silný diagnostický nástroj, ale môže byť verbose a citlivý; používa sa s úzkym filterom a krátkym intervalom.

## Firewall a NAT order

NAT môže zmeniť fields pred filter decisionom. Rule môže vidieť original alebo translated destination podľa hooku a platformy. Preto dokumentácia musí uvádzať observation point.

Ak DNAT zmení `203.0.113.40:443` na `10.50.0.10:443`, forward rule po preklade môže pracovať s internou destination. Operátor hľadajúci iba verejnú IP v nesprávnom chain-e nenájde match.

## Bezpečný rollout policy

Firewall zmena môže odstrihnúť management alebo return traffic. Bezpečný postup používa out-of-band access, syntax check, transaction alebo timed rollback a reprezentatívny probe.

```bash
sudo nft -c -f candidate.nft
sudo nft -f candidate.nft
sudo nft list ruleset
```

Syntax success nepreukazuje semantics. Po apply treba testovať povolený flow, zakázaný flow a existujúce connections podľa rollout contractu.

Pri remote zmene je vhodný automatický rollback timer, ktorý sa zruší až po potvrdení management a service paths. Manuálne „neodpájaj SSH“ nie je dostatočná ochrana.

## Stateless ACL

Nie každý firewall drží connection state. Stateless ACL musí explicitne povoliť oba directions a pracuje s packet fields bez transportného lifecycle-u. Return client port je typicky ephemeral range, čo komplikuje policy.

Cloud security groups, network ACLs, host firewally a application policies môžu tvoriť viac vrstiev. Zelená jedna vrstva nepreukazuje ostatné. Pri incidente sa vytvorí enforcement inventory a path order.

## Incident: allow rule existuje, packet je stále dropped

Atlas pridá allow pre `203.0.113.40:443` do hostového `input` chainu edge routera. Request však používa DNAT a je forwardovaný k `10.50.0.10`. Counter na allow pravidle zostáva nula a forward chain má default drop.

`nft monitor trace` ukáže prerouting DNAT, route decision a drop vo forward chain-e. Oprava pridá úzky allow na translated destination a source, zachová established return a overí forbidden direct backend access. Root cause nie je „firewall cache“, ale nesprávny hook a packet identity.

## Zhrnutie

Firewall verdict patrí konkrétnemu packetu na konkrétnom enforcement pointe. Direction, hook, translation order, state a rule precedence rozhodujú viac než samotný port. Oprava je hotová až po positive, negative a management-path overení.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: NAT](nat.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Proxy a reverse proxy →](proxy-and-reverse-proxy.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
