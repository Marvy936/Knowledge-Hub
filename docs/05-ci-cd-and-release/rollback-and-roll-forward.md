# Rollback a roll-forward

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Rollback a roll-forward sú recovery stratégie nad distribuovaným state-om. Rollback sa vracia k poslednému kompatibilnému runtime subjectu; roll-forward vytvára nový opravený subject, ktorý rešpektuje state už vytvorený chybným release-om.

```text
user impact detected
→ contain ďalšie mutations/exposure
→ zostav state-delta inventory
→ identifikuj last compatible state
→ vyhodnoť recovery eligibility
→ rollback / roll-forward / compensation / restore
→ vykonaj jednu autoritatívnu recovery state machine
→ over technical + data + business outcome
→ sleduj delayed effects
→ uzavri incident a obnov recovery capability
```

Recovery nie je synonymum pre redeployment. Artifact možno vrátiť za minúty, no databáza, events, clients alebo external side effects môžu zostať v novom state-e.

## 1. Nosný model: state delta určuje recovery path

Pri incidente najprv rozdeľ state na vrstvy:

```text
immutable artifact
runtime config a feature flags
routing a exposure
infrastructure desired/effective state
database schema a data
queues, events a checkpoints
cache a sessions
external side effects
distributed clients a integrations
```

Potom pri každej vrstve urči:

```text
before state
→ change introduced by release
→ current effective state
→ reversibility
→ compatibility s candidate recovery targetom
```

Rollback jednej vrstvy neopravuje automaticky ostatné. Traffic rollback nezruší už publikovaný event. Artifact rollback nezmení schema. Point-in-time restore môže vrátiť databázu, ale nie partner payment alebo email.

## 2. Nosný scenár: Atlas Orders release 3.12.0

Atlas rollout `R120` aktivoval Risk v3 pre 25 % ring 1. New worker zapisuje `risk_decisions`, publikuje event `RiskDecisionRecorded.v2` a pri `MANUAL_REVIEW` odosiela partner notification.

Po promotion sa objavia duplicate notifications a niektoré orders ostávajú v `REVIEW_PENDING`.

Current inventory:

```text
API: M3 na 100 % fleet, feature F31 na 25 % ring 1
workers: 70 % D_worker3, 30 % D_worker2
schema: S_expand, dual-write active
queue: v1 aj v2 events, backlog 18 000
external notifications: časť už odoslaná
clients: old aj new API consumers
previous manifest: M_prev dostupný
```

Naivný príkaz „rollback na previous“ je nedostatočný. Old worker nerozumie všetkým v2 events a partner notifications už nemožno odvolať binary rollbackom.

## 3. Containment predchádza rozhodnutiu o finálnej recovery

Atlas najprv zníži damage rate:

```text
pause rollout
→ feature F31 off pre nové orders
→ stop Risk v3 producers
→ pause notification adapter
→ zachovaj queue a database evidence
→ ponechaj healthy read-only paths
```

Containment nie je finálne recovery. Jeho cieľom je zastaviť nové nežiaduce mutations a vytvoriť stabilný decision horizon.

Slepý restart alebo okamžitý rollback môže:

- stratiť in-flight evidence;
- znovu doručiť unacked messages;
- aktivovať old consumer nad nekompatibilným backlogom;
- zväčšiť external side effects;
- skryť prvý divergence point.

## 4. Recovery subject je last compatible state, nie iba previous release

`M_prev` je candidate iba vtedy, ak:

```text
artifact a config bytes sú immutable a dostupné
+ old code číta current schema a data
+ old consumers tolerujú current events
+ clients a external contracts ostávajú kompatibilné
+ security posture je prijateľná
+ recovery workflow a validation sú funkčné
```

Predchádzajúca verzia môže byť:

- už nekompatibilná s novými enum values;
- závislá od odstráneného secretu alebo endpointu;
- zraniteľná;
- bez capacity alebo credentials;
- nikdy produkčne overená v aktuálnom environment state-e.

Last compatible state je teda konkrétny runtime subject s evidence, nie tag `previous`.

## 5. Recovery package vzniká pred rolloutom

Atlas release package obsahuje:

```text
current manifest M3
previous compatible manifest M_prev
config a flag snapshots
schema/event/client compatibility matrix
known irreversible transitions
containment commands
artifact/config/routing rollback workflows
roll-forward build a migration owners
data repair, replay a compensation procedures
technical, functional a business validation queries
```

Package nepredpisuje vždy rollback. Umožňuje rýchlo zistiť, ktoré vetvy sú stále eligible.

## 6. Eligibility graph spája recovery action s current state-om

Pre Atlas incident:

### Traffic alebo feature rollback

Eligible. Zastaví nové Risk v3 exposures, ale nerieši backlog ani notifications.

### Artifact rollback API

Čiastočne eligible. API M_prev toleruje S_expand, ale môže zobrazovať iba old representation.

### Worker rollback

Neeligible, kým queue obsahuje `RiskDecisionRecorded.v2`, ktoré D_worker2 nepozná.

### Data rollback

Nežiaduci. Point-in-time restore by odstránil legitímne orders vytvorené po release.

### Roll-forward

Eligible. Tolerantný worker patch môže spracovať v1 aj v2, deduplikovať notifications a dokončiť reconciliation.

### Compensation

Nutná pre notifications a accounting records, ktoré už vznikli duplicitne.

Recovery rozhodnutie je preto kompozícia:

```text
feature containment
+ roll-forward worker patch
+ queue replay s deduplication
+ selective data reconciliation
+ partner compensation
```

Nie jeden globálny `undo`.

## 7. Rollback preferuj iba pri malom a kompatibilnom state delta

Rollback má silnú výhodu, keď:

- known-good target je pripravený a warm;
- release zmenil iba application behavior alebo routing;
- nové writes/events ostávajú old-compatible;
- návrat neotvorí security problém;
- rollback je rýchlejší než bezpečný fix;
- validation pôvodného outcome-u je pripravená.

Príklad: green API vracia `403` pre chybný audience config, ale ešte nevykonalo nové writes. Routing a config rollback môže byť úplná recovery.

## 8. Roll-forward preferuj pri posunutom alebo nevratnom state-e

Roll-forward je typicky bezpečnejší, keď:

- schema alebo data už zmenili význam;
- stream obsahuje nový event contract;
- external side effects vznikli;
- new clients používajú nový protocol;
- old release obsahuje vulnerability;
- minimal fix je menší než návrat viacerých vrstiev;
- backward migration by stratila dáta alebo prekročila RTO.

Incident urgency nemení požiadavku na immutable fix subject, targeted gates a audit. Mení iba rozsah dôkazu na najkritickejšie failure boundaries.

## 9. Roll-forward lifecycle

Atlas vytvorí `M3.1`:

```text
contain current impact
→ identifikuj minimálny tolerant-reader a dedup fix
→ build immutable D_worker3_1
→ contract fixtures pre v1/v2 events
→ replay a idempotency tests
→ deploy do isolated consumer group
→ spracuj bounded sample backlogu
→ over duplicate a completion invariants
→ promote worker fleet
→ replay remaining backlog
→ reconcile data a external side effects
```

Fix sa najprv overí na presnej failure boundary, nie iba všeobecným test suite passom.

## 10. Compensation je nová business operácia

Duplicate partner notification alebo payment sa nedá „rollbacknúť“ ako file.

Compensation potrebuje:

```text
affected-entity inventory
→ authoritative duplicate classification
→ idempotent compensation key
→ partner/customer communication
→ retry a reconciliation
→ audit a final business invariant
```

Compensating transaction môže sama zlyhať, byť duplicitná alebo vytvoriť ďalší finančný či právny dopad. Preto má vlastného ownera, approvals a observation.

## 11. Restore má collateral state cost

Point-in-time restore na `14:05` môže odstrániť poškodené writes od `14:06`, ale aj všetky legitímne orders po tomto čase.

Restore decision preto hodnotí:

- RPO a RTO;
- rozsah legitímnych writes po recovery point-e;
- external-system divergence;
- event replay capability;
- encryption keys a backup integrity;
- restore target a routing cutover;
- reconciliation po návrate.

Často je bezpečnejšie restore-nuť do nového targetu, selektívne extrahovať správny state a potom vykonať controlled repair.

## 12. Worked failure: artifact rollback zhoršil queue incident

Pri staršom incidente Atlas automaticky rollbackol worker na D_worker2 po náraste error rate.

```text
new worker emitne v2 events
→ queue obsahuje 12 000 v2 messages
→ automation nasadí old worker
→ old deserializer v2 odmietne
→ retries a dead-letter rastú
→ backlog blokuje aj kompatibilné v1 work
→ completion rate klesne viac než pred rollbackom
```

### Príčina

Automatic rollback poznal application version, ale nie event backlog contract. Eligibility kontrola overovala dostupnosť previous artifactu, nie schopnosť previous consumeru spracovať current stream.

### Dôsledok

Rollback zmenšil application novelty, no zväčšil operational damage. Recovery vyžadovala zastaviť old consumer, nasadiť tolerantný roll-forward patch a oddeliť poison messages.

### Trvalá náprava

```text
event-version inventory v recovery package
→ backlog compatibility gate
→ producer-first containment
→ tolerant consumer fixture
→ automatic rollback povolený iba pri state-compatible targete
```

## 13. Worked failure: noisy dependency spustila recovery oscillation

Automatický controller sledoval p99 latency. Regionálny database incident zasiahol blue aj green, ale threshold nebol version-specific.

```text
p99 prekročí limit
→ route green → blue
→ cache a pools sa znovu zahrievajú
→ p99 ostáva vysoká
→ health sa krátko zlepší
→ controller promotionuje späť na green
→ ďalší threshold breach
→ repeated route flips
```

### Príčina

Signal neodlišoval release effect od shared dependency incidentu. Chýbala hysteresis, cooldown, single recovery lock a maximum transition count.

### Dôsledok

Oscillation pridala cache churn, connection bursts a nejasný active state k pôvodnému DB incidentu.

### Trvalá náprava

- stable/new concurrent comparison;
- dependency-health dimension;
- consecutive windows a minimum duration;
- cooldown a maximum automatic transitions;
- po opakovanom failure manuálny checkpoint;
- data plane ostáva v poslednom potvrdenom safe state-e.

## 14. Kauzálny diagnostický walkthrough

Symptom: po feature disable prestali vznikať nové Risk v3 requests, ale duplicate notifications pokračujú.

### Krok 1 — potvrď containment a current subject

```text
rollout R120 paused
F31 off effective na API fleet
Risk v3 producer rate = 0
worker inventory = D_worker2 + D_worker3
queue backlog obsahuje v1/v2
a notification adapter stále spracúva queued commands
```

Feature disable fungoval na request path-e. Symptom preto vzniká za touto boundary.

### Krok 2 — formuluj konkurenčné hypotézy

```text
H1: časť API fleet stále používa stale flag
H2: queued commands vznikli pred disable a teraz sa drainujú
H3: worker retry vytvára nové duplicate commands
H4: partner redeliveruje už prijaté notifications
H5: dashboard dedup alebo event-time query zobrazuje staré dáta ako nové
```

### Krok 3 — vyber observation points

- effective flag evaluations a producer timestamp testujú H1;
- command creation time vs send time testuje H2;
- logical order ID, attempt a worker digest testujú H3;
- partner idempotency/audit ID testuje H4;
- raw ingestion/event-time lag testuje H5.

Atlas zistí:

```text
žiadne commands nevznikli po flag disable
starý backlog sa drainuje
časť orders má dve commands s rôznymi worker attempt IDs
partner každú prijal raz
telemetry latency je normálna
```

H2 a H3 sú podporené. H1, H4 a H5 nie.

### Krok 4 — contain-ni správnu vrstvu

API rollback by nič nezmenil. Atlas pause-ne notification adapter, zastaví mixed worker fleet a nasadí tolerantný dedup worker. Potom klasifikuje backlog pred replayom.

### Krok 5 — vyber recovery podľa state-u

Pretože v2 events a new rows už existujú, worker artifact rollback je neeligible. Roll-forward + reconciliation je bezpečnejší.

### Krok 6 — over pôvodný outcome

Recovery je complete až keď:

```text
notification command creation = 1 per logical decision
partner sends = 1 per idempotency key
queue backlog klesá bez poison retries
orders opúšťajú REVIEW_PENDING
data a accounting reconciliation prejde
```

### Krok 7 — vráť learning

Finding sa mení na queued-side-effect containment v runbooku, event compatibility gate a recovery test s mixed backlogom.

## 15. Recovery validation je outcome-based

Po technickom transitione Atlas overí:

### Runtime

- current artifact/config/flag/routing inventory;
- error, latency a saturation;
- jeden active recovery generation owner.

### Data a events

- schema a representation invariants;
- backlog, dead-letter a replay stav;
- duplicate alebo missing records;
- replicas, CDC a analytics.

### Business a external systems

- order completion;
- partner notification a accounting reconciliation;
- customer/support impact;
- compensation completion.

Zelený deployment job je iba execution evidence, nie dôkaz recovery.

## 16. Delayed verification a rollback window

Po immediate recovery sleduj:

- settlement a scheduled reconciliation;
- late retries a dead-letter replay;
- cache/session warming;
- replication a downstream exports;
- client/integration behavior;
- security a support signals.

Rollback window ostáva otvorené iba kým previous subject zostáva compatible. Keď contract migration, clients alebo events túto podmienku ukončia, release record explicitne zmení primárnu recovery stratégiu na roll-forward, compensation alebo restore.

## 17. Diagnostický runbook

1. Contain-ni nové exposure, writes alebo side effects.
2. Zachovaj timeline a zostav actual state-delta inventory.
3. Urči last compatible state, nie iba previous artifact.
4. Vyhodnoť recovery eligibility pre každú zmenenú vrstvu.
5. Formuluj konkurenčné hypotézy pre pokračujúci symptom.
6. Použi observation points na oddelenie active code, backlogu, external redelivery a telemetry chyby.
7. Vyber jednu autoritatívnu recovery state machine.
8. Zabraň súbežným rollback/roll-forward transitions a oscillation.
9. Over runtime, data, event, business a external-system outcomes.
10. Sleduj delayed effects a zmeň incident na recovery test alebo compatibility control.

## 18. Referenčné pravidlá

- Containment predchádza finálnemu recovery rozhodnutiu.
- Recovery začína state-delta inventory, nie redeployment príkazom.
- Previous release nie je automaticky last compatible state.
- Artifact availability nie je rollback eligibility.
- Traffic, config, artifact, data a client rollback sú odlišné vrstvy.
- Roll-forward je preferovaný pri posunutom shared state-e alebo external side effects.
- Compensation je nová auditovaná business operácia.
- Automatic rollback potrebuje version-specific signal, compatible target, hysteresis a lock.
- Recovery sa končí technical, data a business outcome verification.
- Rollback window je aktívne udržiavaný compatibility contract.

## 19. Časté omyly

### „Vždy rollbackni čo najrýchlejšie“

Nekompatibilný stream alebo schema môže incident zhoršiť.

### „Vždy roll-forwardni“

Pri malom reversible delta môže zbytočne predĺžiť user impact.

### „Feature off vyrieši všetko“

Queued work a external side effects môžu pokračovať.

### „Previous tag je known good“

Target potrebuje immutable identity, evidence a current-state compatibility.

### „Restore je bezplatné undo“

Môže odstrániť legitímne writes a zväčšiť external divergence.

## 20. Zhrnutie

Atlas recovery lifecycle je:

```text
contain damage growth
→ map immutable a mutable state delta
→ identify last compatible runtime subject
→ evaluate per-layer eligibility
→ choose rollback, roll-forward, compensation alebo restore
→ execute one fenced recovery transition
→ verify runtime + data + events + business
→ observe delayed effects
→ restore recovery window and learning controls
```

Rollback a roll-forward nie sú ideologické preferencie. Sú to výsledky kompatibilitného rozhodnutia nad current state-om. Dôveryhodná recovery capability vie nielen spustiť staré alebo nové bytes, ale dokázať, že zvolený state znovu poskytuje správny používateľský a business outcome.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Progressive delivery](progressive-delivery.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Databázová kompatibilita počas deploymentu →](database-compatibility-during-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->