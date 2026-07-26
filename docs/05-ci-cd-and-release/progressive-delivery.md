# Progressive delivery

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Progressive delivery je riadený release systém, ktorý po malých krokoch zosúlaďuje deployment, traffic, audience, feature behavior a data-migration state s produkčnou evidence. Nie je to synonymum pre pomalý rollout ani jedna deployment technika. Je to reconciliation loop nad viacerými control planes.

```text
versionovaný rollout contract
→ pozorovaný multi-axis runtime state
→ jeden bounded transition
→ technical + functional + business evidence
→ promote / pause / abort / inconclusive / invalid
→ recovery alebo ďalší transition
→ delayed validation
→ odstránenie dočasného state-u a closure
```

Hodnota nevzniká samotným znižovaním percenta trafficu. Vzniká tým, že každý transition má známy subject, preconditions, observation points, decision policy a recovery path.

## 1. Nosný model: rollout controller ako reconciler

Controller porovnáva desired a observed state:

```text
desired rollout state
versus
observed artifact + config + traffic + audience + flags + data phase + evidence
```

Potom vypočíta najmenšiu bezpečnú zmenu, vykoná ju a znovu pozoruje systém.

```text
observe
→ classify divergence
→ validate preconditions
→ acquire generation lock
→ apply one transition
→ verify effective state
→ collect outcome evidence
→ record verdict
→ reconcile again
```

Tento model je dôležitý, pretože control-plane zápis nie je automaticky effective runtime state. Route môže byť publikovaná, ale staré connections ostanú. Flag revision môže existovať, ale worker používa stale snapshot. Migration phase môže byť deklarovaná ako `dual-write`, hoci časť fleet stále zapisuje iba old representation.

## 2. Osi promotion sú oddelené, ale musia mať spoločnú identity

Progressive delivery riadi najmenej tieto osi:

```text
artifact       ktorý immutable digest beží
environment    v ktorom targete beží
traffic        koľko requestov smeruje na new generation
audience       ktoré rings, tenants alebo clients sú eligible
feature        ktorý runtime behavior je aktívny
data           ktorá read/write representation je autoritatívna
acceptance     či je release podporovaný a pripravený na cleanup
```

Každá os môže byť v inom stave. To je legitímne iba vtedy, ak je kombinácia zámerná a auditovateľná.

Napríklad:

```text
artifact M3 deployed = 100 % fleet
traffic to M3 = 25 %
risk-decision flag = 10 % eligible tenants
database phase = dual-write, read-old
audience = ring 1
release acceptance = pending
```

Agregovaná veta „release je na 25 %“ by bola nepresná. Nie je jasné, či 25 % označuje traffic, audience, feature exposure alebo data writes.

## 3. Nosný scenár: Atlas Orders release 3.12.0

Atlas pripravuje release `3.12.0`, ktorý presúva risk-decision výpočet na nový service a zároveň migruje uložený výsledok z `orders.risk_status` do `risk_decisions` table.

Rollout subject `R120` obsahuje:

```text
release manifest M3
Orders API digest D_api3
Risk worker digest D_worker3
rendered config C21
flag revision F31
ring membership revision H15
database migration phase S_expand
analysis policy P12
metrics query bundle Q18
```

Plánovaný lifecycle:

```text
1. deploy M3 s feature off a schema expanded
2. shadow traffic do Risk v3 bez authoritative writes
3. ring 0: feature on, read-old + dual-write
4. ring 1: 5 % eligible tenants
5. ring 1: 25 % po sample a invariant evidence
6. read-new with fallback-old
7. rings 2 a 3
8. 100 % feature exposure
9. delayed settlement/reconciliation validation
10. stop old writes, close rollback window
11. contract old schema a remove flag branches
12. release accepted and closed
```

Každý krok mení iba jasne určené osi. Controller nesmie súčasne rozšíriť audience, prepnúť read source a odstrániť rollback path, pretože pri failure by nebolo možné určiť mechanizmus ani bezpečnú recovery vrstvu.

## 4. Rollout contract definuje rozhodovací systém

`R120` obsahuje:

- immutable release, config, flag, membership a migration identities;
- desired state každej promotion osi;
- presný povolený transition graph;
- preconditions pre každý transition;
- minimálnu vzorku, duration a failure-latency horizon;
- technical, functional, business, security a data invariants;
- policy pre missing alebo delayed telemetry;
- maximum blast radius;
- recovery hierarchy a rollback eligibility;
- ownerov, approvals, expiry a pause timeout;
- final intended state a cleanup obligations.

Contract nie je iba konfigurácia controlleru. Je to auditovateľný argument:

```text
prečo smel release vstúpiť do kroku
→ čo sa reálne zmenilo
→ aká evidence vznikla
→ prečo bol zvolený verdict
→ aký state zostal po rozhodnutí
```

Zmena digestu, configu, flag payloadu, cohort policy alebo metrics query vytvára nový subject alebo invaliduje časť evidence.

## 5. Preconditions chránia transition, nie všeobecnú predstavu o zdraví

Pred aktiváciou ring 1 Atlas overí:

```text
M3 + C21 + F31 sú immutable a nasadené
→ schema S_expand podporuje old aj new readers/writers
→ shadow diff je complete pre required workload classes
→ ring membership H15 je konzistentná naprieč API a workermi
→ version/ring/flag/data-phase telemetry je dostupná
→ stable baseline nemá aktívny incident
→ previous compatible state a recovery package sú dostupné
→ controller drží generation lock
```

Každá precondition chráni konkrétnu failure boundary. Baseline health umožňuje atribúciu. Membership consistency chráni cross-service journey. Compatibility matrix chráni rollback. Telemetry completeness chráni decision oracle.

Precondition typu „dashboard je zelený“ je príliš neurčitá, pretože nehovorí, ktorý observation point alebo transition chráni.

## 6. Jeden transition musí mať authoritatívny effective-state check

Pri zmene flag exposure z 5 % na 25 % controller:

```text
1. overí expected current revision F31-step-5
2. publikuje F31-step-25 cez compare-and-swap
3. čaká na distribution acknowledgement
4. meria effective evaluations per revision a variant
5. overí skutočnú eligible cohortu a exposure events
6. až potom začne observation window
```

Čas publikovania configu nie je začiatok experimentu. Observation window začína, keď je effective state dostatočne rozšírený a merateľný.

Rovnaký princíp platí pre routing, deployments a migration flags. Controller nemá predpokladať úspech na základe control-plane response; musí pozorovať data plane.

## 7. Evidence je viazaná na subject a rozhodovaciu otázku

Atlas skladá päť vrstiev evidence.

### Technical

- request errors a p95/p99 latency;
- Risk dependency retries a saturation;
- queue lag, DB wait a resource pressure;
- restarts, probe failures a propagation lag.

### Functional

- order completion;
- jeden authoritative risk decision na order;
- idempotent retry;
- authorization a tenant isolation;
- old/new representation equivalence.

### Business

- accepted-order a manual-review distribution;
- abandonment a support signal;
- delayed settlement completion.

### Security a data invariants

- žiadny cross-tenant access;
- žiadne duplicate side effects;
- dual-write mismatch pod hard limitom;
- nové values čitateľné aktívnymi consumers.

### Evidence health

- query execution status;
- ingestion latency;
- expected sample inventory;
- cohort comparability;
- complete release dimensions.

Evidence bez subject identity môže patriť inému digestu, configu, ring-u alebo data phase. Evidence bez freshness pravidla môže opisovať predchádzajúci krok.

## 8. Verdict taxonomy oddeľuje release failure od evidence failure

Atlas používa:

- `PROMOTE` — required evidence je úplná a policy splnená;
- `PAUSE` — current scope zostáva bezpečný, ale treba čas alebo triage;
- `ABORT` — guardrail alebo invariant bol porušený;
- `INCONCLUSIVE` — evidence je nedostatočná, oneskorená alebo neporovnateľná;
- `INVALID` — skúmaný subject alebo setup nezodpovedal contractu;
- `RECOVER` — treba vykonať konkrétnu containment/recovery vetvu.

Query timeout nie je application failure. Chýbajúca business metric nie je business success. Neplatná cohort membership nie je neutrálna neistota; invaliduje atribúciu.

## 9. Risk class určuje tvar rollout-u

Atlas klasifikuje `R120` ako high-risk, pretože kombinuje:

- nový network dependency;
- mutable database transition;
- background workers;
- delayed business outcome;
- external accounting side effects;
- partial rollback limitations.

Preto používa malé rings, samostatný data read switch, manuálny checkpoint pred ukončením rollback windowu a dlhú delayed validation.

Low-risk statická UI copy zmena by nepotrebovala rovnaký počet krokov. Progressive delivery nie je univerzálny ceremoniál; risk a reversibility určujú required evidence, automation a approvals.

## 10. Worked failure: traffic, feature a data phase sa rozišli

Controller zvýšil route weight M3 z 25 % na 50 %. Feature platforma však zostala na 10 % exposure a migration controller už prepol `read-new` pre ring 1.

```text
50 % requests beží na M3
→ iba časť z nich aktivuje Risk v3
→ ring 1 číta new table
→ ostatné requests stále zapisujú prevažne old representation
→ fallback read rastie
→ business metric sa agreguje iba podľa artifact digestu
→ M3 vyzerá nekonzistentne a rollout sa pause-ne
```

### Príčina

Tri control planes nemali jeden transition record ani atomic desired-state contract. Dashboard dimenzoval artifact, ale nie flag variant a data phase. Tím teda nevedel, ktoré requesty skutočne použili nový behavior.

### Dôsledok

Samotný traffic rollback by nevrátil read source. Samotný flag disable by ponechal ring na new table s rastúcim fallbackom. Recovery musela najprv zastaviť promotion, stabilizovať write path, vrátiť read source na old a až potom znížiť traffic.

### Trvalá náprava

```text
spoločný rollout ID a axis inventory
→ prerequisite graph: read-new requires dual-write coverage
→ transition journal s expected/observed state
→ telemetry dimensions artifact + flag revision + ring + data phase
→ invariant: žiadny ďalší transition pri axis divergence
```

## 11. Worked failure: controller crashol po route update-e

Pri promotion z 5 % na 25 % routing API úspešne aplikovalo revision `T25`, ale response sa stratila. Controller nestihol zapísať completed transition a po reštarte načítal lokálny state `T5`.

Naivný controller by opakoval príkaz alebo rovno prešiel na ďalší krok. Atlas reconciler namiesto toho:

```text
načíta observed routing revision
→ nájde T25 active
→ overí, že transition subject a generation sedia
→ reconciliuje journal ako completed-with-unknown-response
→ spustí effective-state verification
→ nezačne ďalší krok bez evidence T25
```

### Failure boundary

Control-plane timeout vytvoril unknown outcome, nie potvrdené zlyhanie. Blind retry bez idempotency key alebo compare-and-swap mohol vytvoriť 50 % exposure alebo prepísať novší manuálny containment.

### Trvalá náprava

- idempotency key per transition;
- desired/observed reconciliation po každom restart-e;
- generation lock a fencing;
- append-only transition journal;
- data plane ostáva v poslednom potvrdenom bezpečnom state-e;
- promotion timer sa neobnoví, kým effective state a evidence nie sú známe.

## 12. Kauzálny diagnostický walkthrough

Symptom: po promotion ring 1 z 5 % na 25 % klesne order completion, server error rate ostáva stabilná a fallback reads rastú.

### Krok 1 — stabilizuj rollout subject a actual state

```text
rollout R120
artifact M3 / config C21
route T25
flag F31-step-25
ring policy H15
migration desired = read-new
effective worker distribution = unknown
```

Posledná položka je zásadná: desired data phase nie je dôkaz, že všetci writers používajú rovnaký effective state.

### Krok 2 — vytvor konkurenčné hypotézy

```text
H1: Risk v3 code vracia nesprávne decisions
H2: read-new path číta neúplné dáta pre stale workers
H3: ring 1 má ťažší workload než control
H4: global database incident zhoršuje oba variants
H5: completion telemetry je delayed alebo nesprávne dimenzovaná
```

### Krok 3 — vyber observation points

- dual-write coverage a worker config revision testujú H2;
- risk-decision diff na paired orders testuje H1;
- tenant/order complexity distribution testuje H3;
- stable a canary DB wait v rovnakom regióne testuje H4;
- raw completion events, ingestion lag a query revision testujú H5.

Atlas zistí:

```text
API fleet je na F31-step-25
30 % workerov stále používa F31-step-5
fallback reads korelujú s outputs týchto workerov
stable DB latency je normálna
paired decision values sú správne, keď oba writes existujú
telemetry je complete
```

H2 vysvetľuje symptom. Nejde o čistú code regression ani globálny DB incident.

### Krok 4 — contain-ni príčinný state

Controller pause-ne ďalšiu promotion, vráti ring 1 na `read-old`, ponechá dual-write, zablokuje worker rollout bez latest revision a počká na complete distribution. Binary artifact rollback by nebol potrebný a mohol by skomplikovať migration state.

### Krok 5 — over pôvodný outcome

Recovery je potvrdená až keď:

```text
fallback reads klesnú k nule
dual-write coverage je complete
order completion sa vráti k control baseline
data equivalence invariant prejde
worker revision inventory je úplný
```

### Krok 6 — vráť learning do skoršej vrstvy

Finding sa zmení na phase prerequisite, worker-distribution gate, cross-axis telemetry a fault test controllera pri partial config propagation.

## 13. Recovery hierarchy vychádza zo zmeneného state-u

Atlas používa od najmenej invazívnej akcie:

```text
stop promotion
→ reduce audience/traffic
→ disable feature alebo vráť read source
→ route na stable target
→ rollback config/artifact
→ roll-forward fix
→ compensate side effects
→ repair alebo restore data
```

Správna akcia sa neurčuje názvom stratégie, ale current state inventory. Ak nové writes zostali old-compatible, flag disable môže stačiť. Ak new worker emitoval nekompatibilné events, traffic rollback API neodstráni poison backlog.

## 14. Pause je riadený state, nie odložené rozhodnutie

Pause record obsahuje:

- current actual state každej osi;
- dôvod a chýbajúcu evidence;
- ownera;
- maximum pause duration;
- povolené mutations počas pause;
- freshness preconditions pre resume;
- expiry action, napríklad abort alebo návrat na stable.

Po hodinách sa môže zmeniť baseline, dependency health, ring membership alebo rollback eligibility. Resume preto nie je pokračovanie starého timeru; je to nový reconciliation a precondition pass.

## 15. Full exposure nie je closure

Po 100 % feature exposure Atlas stále overuje:

- queue a settlement lag;
- reconciliation výsledok;
- memory a connection behavior;
- late client versions;
- support a business-cycle signals;
- data migration invariants.

Release sa uzavrie až keď:

```text
final artifact/config/feature/data state je explicitný
old generation a dočasné routes sú retired
flag evaluation a obsolete path sú odstránené
migration rollback window je ukončené vedomým rozhodnutím
contract cleanup je hotový
release record a findings sú archivované
```

`100 % on` bez cleanupu vytvára permanentný skew a control-plane debt.

## 16. Diagnostický runbook

1. Urči rollout ID, contract revision a immutable subject.
2. Zostav observed inventory artifactu, routingu, audience, flags a data phase.
3. Porovnaj desired a effective state každej osi.
4. Over generation lock, transition journal a posledný confirmed transition.
5. Validuj evidence completeness, freshness, query execution a cohort comparability.
6. Formuluj code, axis-divergence, workload, dependency a telemetry hypotézy.
7. Vyber observation points, ktoré ich rozlíšia.
8. Contain-ni mechanizmus na najnižšej bezpečnej vrstve.
9. Over technical, functional, business a data outcome.
10. Uzavri cleanup a premeň finding na precondition, policy alebo controller test.

## 17. Referenčné pravidlá

- Progressive delivery je reconciliation loop, nie timer.
- Deployment, traffic, audience, feature, data a acceptance sú samostatné osi.
- Všetky osi potrebujú spoločný rollout subject a actual-state inventory.
- Control-plane success sa overuje v effective data plane.
- Jeden transition má meniť ohraničený state a mať vlastnú evidence.
- Missing telemetry je `INCONCLUSIVE`, subject mismatch je `INVALID`.
- Risk a reversibility určujú kroky, approvals a observation horizon.
- Unknown transition outcome sa reconciliuje, nie slepo opakuje.
- Recovery vrstva sa vyberá podľa mutable state-u a side effects.
- Full exposure bez delayed validation a cleanup nie je closure.

## 18. Časté omyly

### „Progressive delivery je pomalý rolling update“

Bez subjectu, evidence a decision policy ide iba o pomalšie šírenie.

### „25 % rollout presne opisuje state“

Nie je jasné, či ide o traffic, audience, feature alebo data writes.

### „Controller dostal HTTP 200, transition je hotový“

Treba potvrdiť effective routing, distribution a exposure.

### „Missing metric znamená nulový problém“

Nefunkčný oracle nesmie povoliť promotion.

### „100 % exposure znamená dokončenie“

Old paths, flags, migration fallback a support skew môžu zostať.

## 19. Zhrnutie

Atlas progressive-delivery lifecycle je:

```text
immutable rollout contract
→ observed multi-axis state
→ precondition a generation lock
→ jeden bounded transition
→ effective-state verification
→ subject-bound technical/functional/business/data evidence
→ explicitný verdict
→ recovery alebo ďalší reconciliation krok
→ delayed validation
→ debt-free closure
```

Progressive delivery je dôveryhodné iba vtedy, keď controller rozumie skutočnému distribuovanému state-u, nie iba vlastným príkazom. Jeho cieľom nie je maximalizovať počet rollout krokov, ale minimalizovať exposure pred detekciou a zachovať vysvetliteľnú recovery cestu pri každom transitione.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Feature flags](feature-flags.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Rollback a roll-forward →](rollback-and-roll-forward.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
