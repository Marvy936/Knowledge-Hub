# Blue-green deployment

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Blue-green deployment pripraví novú application generation v oddelenom produkčne relevantnom targete a potom zmení autoritatívny routing pointer. Application runtime je oddelený, no databáza, queues, caches, sessions a external side effects často zostávajú spoločné.

```text
blue active
→ green provisioned s immutable release subjectom
→ green overený cez produkčne relevantný path
→ cutover transaction blue → green
→ blue drain + green observation
→ accept / routing rollback / roll-forward
→ old target retention alebo retirement
```

Hlavná výhoda je silná pre-cutover validácia a potenciálne rýchly návrat routingu. Hlavné obmedzenie je, že routing rollback nevracia mutable state.

## 1. Nosný model: dva targety a jeden autoritatívny pointer

Blue-green má tri identity:

```text
blue target state
+ green target state
+ routing revision určujúca active target
```

Každý target má vlastný:

- artifact digest;
- rendered config a secret references;
- application capacity;
- runtime a network identity;
- readiness a telemetry dimensions;
- worker/scheduler activation state.

Routing pointer určuje, kam idú nové requests alebo connections. Nehovorí však, ktorá farba stále spracúva staré connections, queues alebo background work.

Z toho vyplýva hlavný trade-off:

```text
pre-cutover isolation + rýchly routing switch
za cenu dvojitej capacity, shared-state koordinácie a ostrého cutover blast radiusu
```

## 2. Nosný scenár: Atlas Orders 3.11.0

Atlas prevádzkuje Orders API v blue targete s release manifestom `M_prev`. Green target pripravuje manifest `M2`:

```text
green API digest D_api
worker digest D_worker
rendered config C17
expanded database schema S_expand
feature risk-decision = off
routing candidate revision R42
```

Plán:

```text
blue = 100 % active
→ green provisioned bez customer trafficu
→ green synthetics cez production ingress, TLS a auth
→ green warm-up a capacity verification
→ internal cohort na green
→ cutover CAS: expected active blue, new active green
→ green 100 % nových requests
→ blue connection drain
→ observation window
→ blue warm standby počas recovery windowu
```

Workers zostanú počas pre-cutover fázy aktívne iba v blue. Green worker preberie ownership samostatným fenced transitionom po application cutover-e.

## 3. Green evidence musí patriť finálnemu runtime subjectu

Pre-cutover verification je platná iba vtedy, keď testuje rovnaký subject, ktorý bude po switchi aktívny:

```text
M2
+ C17
+ production secret references
+ production ingress/TLS/auth path
+ S_expand
+ planned traffic and worker policy
```

Ak sa pri cutover-e zmení config, feature flag, secret alebo route behavior, vznikol nový subject. Predchádzajúci green test ho nepreukazuje.

Atlas preto zachová content-derived rendered-config digest a pre/post routing snapshot. Interný test cez pod IP, ktorý obíde ingress, TLS alebo authorization proxy, je iba component evidence, nie dôkaz finálneho production pathu.

## 4. Behavioral equivalence je risk-specific, nie vizuálna podobnosť

Green nemusí byť fyzicky identický s blue, ale musí zachovať vlastnosti relevantné pre release risk:

- rovnaký protocol a identity path;
- porovnateľné resource limits a topology;
- rovnaké policy a deployment templates;
- production dependencies a quotas;
- kompatibilný database/event/cache/session contract;
- rovnaké observability semantics;
- dostatočnú kapacitu pre plánovaný cutover.

Green s jednou malou instance môže prejsť smoke, ale nepreukazuje schopnosť niesť plnú produkčnú záťaž. Green v inom network path-e nemusí odhaliť mTLS alebo authorization failure.

## 5. Cutover je chránená transakcia

Atlas neprepíše routing bez precondition:

```text
expected routing revision = R41
expected active target = blue
new routing revision = R42
new active target = green
release subject = M2 + C17
```

Control plane použije compare-and-swap. Ak medzičasom niekto zmenil route alebo začal iný deployment, transition zlyhá namiesto prepísania novšieho state-u.

Cutover record obsahuje:

- old a new target identity;
- routing mechanism a revision;
- actor/workload identity;
- čas začiatku a potvrdenia propagation;
- traffic weights;
- worker/scheduler ownership;
- rollback relation.

Idempotentné opakovanie musí rozpoznať, či R42 už platí, či sa cutover nevykonal alebo či existuje konfliktujúci state.

## 6. Routing propagation nie je okamžitý globálny stav

Po zmene pointera môžu requests stále smerovať na blue kvôli:

- load-balancer propagation;
- persistent HTTP connections;
- WebSockets a streams;
- session affinity;
- service discovery cache;
- DNS TTL a resolver cache;
- regionálnemu traffic manageru.

Preto Atlas odlišuje:

```text
new-request cutover
→ blue dostáva minimum nových connections

connection drain complete
→ blue už nemá critical active work
```

Cutover success sa nepotvrdzuje iba stavom control-plane objektu. Overuje sa skutočným requests-per-color a connection inventory.

## 7. Shared database určuje rollback window

Atlas používa jednu databázu. Pred cutoverom vykoná expand migration, ktorú číta blue aj green.

```text
expand schema
→ green deploy
→ cutover
→ green writes zostávajú blue-readable
→ observation a rollback window
→ blue retirement
→ backfill/contract až neskôr
```

Ak green začne zapisovať nekompatibilný format, návrat route na blue môže obnoviť traffic, ale blue nebude vedieť čítať nové rows. Routing rollback je bezpečný iba dovtedy, kým shared-state contract zostáva kompatibilný.

Oddelené blue/green databázy nie sú automaticky jednoduchšie. Vyžadujú write synchronization, consistency point, replication lag, sequence coordination a failback. To je data migration systém, nie iba application deployment strategy.

## 8. Workers a schedulers potrebujú samostatný ownership transition

Dve API farby môžu byť read-compatible, no dva active schedulers môžu vykonať rovnakú mutáciu dvakrát.

Atlas používa:

```text
blue worker active generation W41
green worker ready but fenced
→ application cutover R42
→ worker ownership CAS W41 → W42
→ blue worker drain
→ green worker active
```

Ownership sa nevkladá do mutable application configu, ktorý obe farby môžu načítať nejednoznačne. Používa sa external lease/fencing generation.

Ak worker transition zlyhá, application traffic môže zostať na green, no background capability ostane paused. Release record musí tento partial state zobraziť namiesto jedného všeobecného `deployed` statusu.

## 9. Pre-cutover validation postupuje po observation boundaries

Atlas overuje green v poradí:

```text
artifact/config identity
→ startup a dependency connectivity
→ production ingress/TLS/auth
→ critical read/write synthetic
→ old/new schema compatibility
→ warm-up a capacity
→ telemetry podľa color/digest
→ rollback target blue stále healthy
```

Poradie nie je náhodné. Nemá význam analyzovať business synthetic, ak request ešte nedosiahne green pre routing alebo auth chybu. Nemá význam označiť green za rollback-safe, ak blue už driftoval alebo stratil credentials.

Verdict je `ready`, `not ready` alebo `inconclusive`. Chýbajúca color telemetry je `inconclusive`, pretože po cutover-e by nebolo možné pripísať failure správnej farbe.

## 10. Warm-up a capacity patria pred ostrý switch

Green potrebuje pred cutoverom:

- JIT alebo rules-engine initialization;
- cache prewarming;
- connection pools;
- discovery propagation;
- autoscaler stabilization;
- capacity test voči shared quotas.

Warm-up requests musia byť side-effect safe. Atlas používa izolované synthetic identities a bounded replay bez skutočných customer mutations.

Dvojitá application capacity môže stále preťažiť shared DB alebo broker. Blue-green capacity model preto zahŕňa `blue + green` connections, consumers, targets a monitoring cardinality.

## 11. Worked failure: green sa testoval cez skratku, cutover rozbil authorization

Green smoke používal internú service adresu a service account s administrátorským scope-om.

```text
internal green smoke prejde
→ production route sa prepne na green
→ request ide cez ingress a mTLS identity proxy
→ green config očakáva starý audience claim
→ bežní users dostávajú 403
→ process a interný health zostávajú zelené
```

### Príčina

Pre-cutover evidence obchádzala finálny network a authorization path. Green bol funkčný ako interný component, nie ako production runtime subject.

### Recovery

Atlas vykonal routing rollback na blue, pretože green ešte nevytvoril nekompatibilné writes. Potom opravil audience config, vytvoril nový rendered-config digest a zopakoval synthetic cez production ingress s reprezentatívnou user identity.

### Trvalá náprava

```text
production-path synthetic
→ positive aj negative authorization fixtures
→ config digest súčasť cutover subjectu
→ approval invalidation pri config zmene
→ color-specific auth telemetry
```

## 12. Worked failure: oba schedulery vytvorili duplicate side effects

Pri cutover-e pipeline prepla application route, ale worker activation bol obyčajný boolean v confige. Blue načítal starú hodnotu z cache a green novú hodnotu.

```text
blue scheduler zostane active
green scheduler sa aktivuje
→ obaja vyberú rovnaký reconciliation batch
→ external notification a accounting update sa vykonajú dvakrát
→ routing rollback na blue nezruší už vykonané side effects
```

### Príčina

Tím považoval farbu za úplný system ownership. V skutočnosti routing pointer riadil iba HTTP traffic; scheduler nemal external fencing ani single-owner invariant.

### Dôsledok

Application rollback nestačil. Atlas musel zastaviť oba schedulery, zvoliť jedného ownera, reconciliovať duplicate účtovné entries a kompenzovať notifications.

### Trvalá náprava

- worker ownership dostal samostatný CAS/fencing transition;
- side effects používajú idempotency key;
- release record zobrazuje application a worker state oddelene;
- pre-cutover test simuluje blue/green scheduler overlap;
- rollback plan obsahuje reconciliation, nie iba route switch.

## 13. Kauzálny diagnostický walkthrough

Symptom: po cutover-e rastie duplicate-order invariant, ale HTTP error rate ostáva normálna.

### Krok 1 — identifikuj skutočný active state

```text
routing revision R42 → green
blue requests klesajú, ale nie sú nulové
worker generation W41 aj W42 hlásia active
release subject M2 + C17
```

Tento obraz okamžite ukazuje, že application routing a worker ownership nie sú jedna os.

### Krok 2 — formuluj konkurenčné hypotézy

```text
H1: green API vytvára duplicity pri retry
H2: blue a green schedulers vykonávajú rovnakú prácu
H3: client cohort posiela duplicate requests
H4: regionálny broker redeliveruje správy
```

### Krok 3 — vyber observation points

- idempotency key a request trace per color testujú H1/H3;
- scheduler lease generation a batch ownership testujú H2;
- broker delivery attempt a partition telemetry testujú H4;
- duplicate side-effect timestamps voči scheduler runs ukazujú prvý divergence point.

Atlas zistí, že každý duplicate pair má dve scheduler run identities a rovnaký batch ID, zatiaľ čo API request vznikol iba raz. H2 je podporená, H1 a H3 nie.

### Krok 4 — zastav mutation boundary

Najprv sa zastavia schedulery a vydá nová fencing generation. Routing rollback bez zastavenia workerov by nezastavil duplicate side effects.

### Krok 5 — rozhodni recovery podľa state-u

Pretože customer HTTP behavior green je zdravý, Atlas ponechá application route na green. Reconciliuje duplicate accounting records, aktivuje iba W42 a overí idempotency invariant. Binary rollback by nepriniesol hodnotu a mohol by pridať ďalšiu zmenu.

### Krok 6 — over outcome a vráť learning

Recovery je potvrdená nulovým rastom duplicate invariantu, jedným active lease ownerom a úspešnou reconciliation. Finding sa mení na external fencing control a mixed-color scheduler test.

## 14. Routing rollback eligibility sa priebežne mení

Blue je rollback candidate iba ak:

```text
blue artifact/config stále dôveryhodné
+ blue runtime je ready a warm
+ schema/data/events sú blue-compatible
+ secrets a dependencies platia
+ worker ownership možno bezpečne vrátiť
+ green side effects sú kompatibilné alebo kompenzovateľné
```

Old target sa preto počas retention pravidelne health-checkuje. Target ponechaný bez trafficu môže stratiť credentials, network access alebo capacity a vytvoriť falošný pocit recovery.

Po contract migration alebo nekompatibilnom backfille sa blue explicitne označí ako rollback-ineligible a recovery sa prepne na roll-forward model.

## 15. Diagnostický runbook

1. Urči routing revision, active target a skutočné traffic weights.
2. Potvrď artifact/config identity oboch farieb a finálny release subject.
3. Over routing propagation, persistent connections a requests per color.
4. Porovnaj color-specific technical, functional a business evidence.
5. Skontroluj shared DB, event, cache a session compatibility.
6. Over samostatný worker/scheduler ownership a fencing generation.
7. Nájdite prvý observation point, kde sa green od blue odlíšil.
8. Rozlíš routing failure, green runtime failure, shared-state failure a external incident.
9. Posúď routing rollback eligibility vrátane nových writes a side effects.
10. Po recovery over business/data invariants a aktualizuj pre-cutover control.

## 16. Referenčné pravidlá

- Blue-green riadi dva targety a jeden autoritatívny routing pointer.
- Application isolation neznamená izoláciu databázy, queues ani side effects.
- Green evidence musí patriť finálnemu artifact/config/path subjectu.
- Cutover je CAS-chránená, idempotentná a auditovaná transakcia.
- Control-plane route success sa overuje skutočným trafficom per color.
- Connection drain pokračuje po switchi nových requests.
- Workers a schedulers potrebujú samostatný ownership transition.
- Routing rollback nie je data rollback.
- Old target zostáva recovery candidate iba pri priebežnej health a compatibility evidence.
- Diagnostika odlišuje routing, runtime, shared state a ownership boundaries.

## 17. Časté omyly

### „Green je overený, lebo health endpoint prešiel“

Health cez internú skratku nemusí testovať production ingress, identity ani customer journey.

### „Switch route je okamžitý“

Persistent connections, DNS a propagation vytvárajú dočasný dual-active request stav.

### „Dve farby znamenajú dve oddelené databázy“

Najčastejšie zostáva shared mutable state spoločný.

### „Rollback je iba vrátenie pointera“

Green writes alebo external side effects môžu spraviť blue nekompatibilným.

### „Oba schedulery môžu krátko bežať“

Bez fencing a idempotency môže krátky overlap vytvoriť trvalé duplicity.

## 18. Zhrnutie

Atlas blue-green lifecycle je:

```text
immutable blue a green identities
→ green validation cez finálny production path
→ warm-up a shared-capacity evidence
→ CAS routing cutover
→ samostatný worker ownership transition
→ color-specific observation a connection drain
→ accept alebo recovery podľa shared-state compatibility
→ health-checked standby a riadené retirement
```

Blue-green poskytuje hodnotu vďaka oddelenému runtime targetu a rýchlemu routing controlu. Bez explicitného shared-state, worker ownership a rollback contractu však dve farby iba presunú nejasnosť z application fleet do dát a side effects.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Rolling update](rolling-update.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Canary deployment →](canary-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
