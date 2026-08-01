# DNS

<!-- CONCEPT-FIRST:START -->
## Čo je DNS

DNS je distribuovaný, hierarchický a cacheovaný naming systém. Preklad hostname na IP adresu je iba jedna jeho funkcia. DNS publikuje records, deleguje zóny a umožňuje resolverom dočasne uchovávať odpovede podľa TTL.

Aplikácia typicky volá stub resolver operačného systému. Ten používa configured recursive resolver. Recursive resolver môže výsledok nájsť v cache alebo postupne získať referrals od root, TLD a authoritative serverov. Authoritative server publikuje data pre konkrétnu zónu; nevykonáva bežne rekurziu za klienta.

Dôležité records:

```text
A      hostname → IPv4
AAAA   hostname → IPv6
CNAME  alias → canonical name
NS     delegácia zóny
MX     mail exchange
TXT    textové policy alebo verification data
SOA    základné metadata zóny
```

TTL neurčuje, kedy sa zmena „globálne aktivuje“. Určuje, ako dlho môže konkrétna cache používať starú odpoveď. Aplikačný runtime môže mať navyše vlastnú cache a existujúce TCP connections môžu pokračovať aj po zmene DNS.

Negative odpovede, napríklad `NXDOMAIN`, sa môžu tiež cacheovať. Vytvorenie chýbajúceho recordu preto nemusí okamžite opraviť clients, ktoré ešte držia negatívny result.

Split-horizon DNS vracia odlišné answers podľa resolvera alebo source siete. Môže byť zámerné, ale vytvára viac naming states, routes a certificate assumptions.

Neutrálny príklad:

```text
app.example CNAME edge.example
edge.example A     198.51.100.20
edge.example AAAA  2001:db8::20
```

Klient musí vyriešiť alias chain a následne vybrať address family. Bežný request môže fallbacknúť z nefunkčného IPv6 na IPv4 a skryť chybu.

`dig` overuje DNS query voči konkrétnemu serveru. `getent` alebo aplikačný test môže používať celý OS naming path vrátane hosts file a NSS. Rovnaký hostname preto treba testovať cez rovnaký resolver path ako reálna aplikácia.
<!-- CONCEPT-FIRST:END -->

## Atlas scenár a praktické použitie

Atlas klient nezačína IP adresou. Aplikácia pozná `api.atlas.example` a resolver musí vrátiť použiteľný address set. DNS je distribuovaná databáza s delegáciou, cachingom a časovou platnosťou. Zelený `dig` output dokazuje odpoveď konkrétneho servera; nepreukazuje, že aplikácia použila rovnaký resolver, cache, search path alebo address family.

## Od aplikácie k authoritative zóne

Typická cesta:

```text
application/runtime
→ OS stub resolver
→ configured recursive resolver
→ root a TLD referrals
→ authoritative server pre atlas.example
→ cache a odpoveď klientovi
```

Recursive resolver vykoná potrebné queries, validuje policy a výsledok cacheuje podľa TTL. Aplikácia môže mať vlastnú DNS cache a JVM, browser alebo proxy môžu držať answer dlhšie alebo kratšie než OS.

```bash
cat /etc/resolv.conf
resolvectl status
getent ahosts api.atlas.example
dig api.atlas.example A
dig api.atlas.example AAAA
```

`getent` typicky používa systémový name-service path vrátane NSS. `dig` sa pýta DNS priamo a môže obísť hosts file alebo aplikačný behavior. Pri incidente sa používajú oba, ale neinterpretujú sa ako rovnaký dôkaz.

## Records a alias chain

`A` mapuje meno na IPv4, `AAAA` na IPv6. `CNAME` vytvorí alias k ďalšiemu menu, `MX` opisuje mail exchange, `TXT` nesie textové policy alebo verification údaje, `NS` deleguje zónu a `SOA` obsahuje základné zónové metadata.

API môže používať:

```text
api.atlas.example CNAME edge.atlas.example
edge.atlas.example A     203.0.113.40
edge.atlas.example AAAA  2001:db8:100::40
```

Resolver musí prejsť alias chain a cacheuje jednotlivé records podľa ich TTL. Dlhý alebo chybný chain zvyšuje failure surface. CNAME tiež nemení TLS identity, ktorú klient očakáva; certifikát stále musí pokrývať hostname z URL.

## TTL a cache

TTL určuje, ako dlho môže resolver používať record bez nového authoritative query. Krátky TTL zrýchli prechod na nový target, ale zvýši query load a závislosť od resolver availability. Dlhý TTL znižuje load, ale predlžuje recovery po chybnej zmene.

Zmena DNS nie je okamžitý globálny switch:

```text
authoritative update
→ nové queries dostanú nový answer
→ existujúce recursive caches držia starý answer do expiry
→ application caches môžu mať vlastný lifecycle
→ existujúce TCP/TLS connections môžu pokračovať ďalej
```

Rollout a rollback preto musia rešpektovať TTL, connection lifetime a backend compatibility.

## Negative caching

Aj `NXDOMAIN` alebo negatívna odpoveď môže byť cacheovaná. Ak deployment publikuje hostname až po tom, čo clients dostali `NXDOMAIN`, opakované queries môžu určitý čas stále zlyhávať.

```bash
dig +noall +answer +authority missing.atlas.example
```

Pri recovery nestačí vytvoriť record a okamžite testovať iba z resolvera bez starej cache. Treba poznať negative TTL a overiť reprezentatívne resolver cohorts.

## Split-horizon a search domains

Interné a externé resolvery môžu pre rovnaké meno vracať odlišné answers. To môže byť zámerné, ale komplikuje diagnostiku a certificate, routing aj failover model.

Search domains a `ndots` môžu meniť, aké queries vzniknú pre krátke meno. Aplikácia volajúca `orders-api` môže skúšať viac suffixov pred absolútnym menom. Použitie FQDN s koncovou bodkou v diagnostickom nástroji môže obísť search behavior, ktorý reálna aplikácia používa.

## UDP, TCP a veľké odpovede

DNS typicky začína cez UDP. Ak response nevojde alebo je označená ako truncated, klient môže opakovať query cez TCP. EDNS umožňuje väčšie UDP payloady, no fragmentácia alebo middlebox policy môžu vytvoriť problém, pri ktorom malé answers fungujú a veľké DNSSEC answers timeoutujú.

```bash
dig api.atlas.example
dig +tcp api.atlas.example
```

Ak UDP zlyhá a TCP prejde, hypotézy zahŕňajú fragmentáciu, firewall alebo resolver implementation. Povolenie iba UDP/53 nie je úplný DNS transport contract.

## DNSSEC a trust

DNSSEC podpisuje DNS data a umožňuje validujúcemu resolveru overiť chain of trust. Nešifruje query ani neskrýva meno. Chybný podpis, expirovaná signature alebo broken delegation môže viesť k `SERVFAIL` z validujúceho resolvera, hoci nevalidujúci resolver vráti data.

Pri incidente treba zistiť, či resolver validuje a prečo odpoveď odmietol. Vypnutie validation je risk workaround, nie štandardná oprava.

## Incident: po rollbacku niektorí klienti stále používajú chybný VIP

Atlas publikuje nový `A` record s TTL 600 sekúnd. Po piatich minútach zistí chybu a vráti starý VIP. Časť resolverov však získala nový answer tesne pred rollbackom a drží ho ďalších desať minút. Existujúce connections navyše pokračujú k novému edge-u.

Autoritatívny record je už správny, no user cohort stále zlyháva. Diagnosis porovná authoritative answer, recursive cache TTL, application cache a connection reuse. Recovery ponechá oba VIP kompatibilné počas celého transition window a monitoruje answers z reprezentatívnych resolverov. Budúci rollout používa prechodné zníženie TTL s dostatočným predstihom.

## Zhrnutie

DNS je verzovaný a cacheovaný naming systém, nie okamžitá funkcia `meno → IP`. Aplikácia, stub, recursive cache a authoritative server sú odlišné observation points. TTL, negative caching, aliasy, split-horizon, transport a DNSSEC určujú, kedy je answer použiteľný a dôveryhodný.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Porty a sockety](ports-and-sockets.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: DHCP →](dhcp.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
