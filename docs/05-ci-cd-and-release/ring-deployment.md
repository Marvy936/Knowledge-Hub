# Ring deployment

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Ring deployment riadi release cez stabilné production cohorts s odlišným risk profilom, workloadom, support modelom a recovery schopnosťou. Ring nie je iba percento trafficu ani environment name. Je to dlhšie žijúca release boundary, ktorá udržiava explicitnú informáciu o tom, kto používa ktorú release identity.

```text
immutable release subject
→ versionované ring membership a inventory
→ ring-specific entry contract
→ deployment a exposure
→ ring-specific observation
→ promote / pause / abort / inconclusive
→ ďalší ring alebo partial recovery
→ skew reduction a cleanup
```

Hlavná cena ring rollout-u je version skew: viac produkčných cohort používa rôzne verzie nad spoločnými API, databázou, eventmi, caches a clients.

## 1. Nosný model: release inventory naprieč stabilnými cohortami

V jednom okamihu môže Atlas vyzerať takto:

```text
ring 0 internal         → M2
ring 1 pilot tenants    → M2
ring 2 general small    → M_prev
ring 3 large tenants    → M_prev
ring 4 regulated        → M_prev
```

Release inventory musí pre každý ring spájať:

```text
ring ID a membership revision
+ member/workload inventory
+ release manifest a rendered config
+ exposure state
+ support owner
+ observation verdict
+ recovery eligibility
```

Bez inventory nemožno odpovedať:

- kto je zasiahnutý incidentom;
- ktoré contracts musia zostať kompatibilné;
- či je partial rollback bezpečný;
- ktoré support a communication pravidlá platia;
- ako dlho môže version skew pokračovať.

## 2. Nosný scenár: Atlas Orders 3.11.0 naprieč tenant rings

Atlas rozdeľuje tenants:

```text
ring 0
→ interné a synthetic tenants

ring 1
→ dobrovoľní pilotní zákazníci s priamym support channelom

ring 2
→ small a medium tenants s bežnými integráciami

ring 3
→ large tenants s vysokým order volume a custom webhooks

ring 4
→ regulované tenants s dlhším approval a audit cycle
```

Všetky ringy dostávajú rovnaký immutable release manifest `M2`. Rozdiely v config alebo flags sú explicitné a versionované, nie skryté per-ring rebuildy.

Release 3.11.0 mení riskDecision flow. Ring poradie má získať postupne širší dôkaz:

```text
functional correctness
→ external integration behavior
→ workload scale
→ regulated workflow a audit evidence
```

## 3. Membership je produkčná policy

Ring membership musí byť stabilný a auditovateľný:

```text
membership revision H12
subject tenant T42
→ ring 3
```

Rule môže používať tenant tier, opt-in, region, compliance class alebo device channel. Musí však byť:

- deterministická;
- konzistentná naprieč API, workers a clients;
- privacy-safe;
- dostupná v telemetry;
- chránená revision compare-and-swap;
- vysvetliteľná supportu.

Membership change mení blast radius a experiment population. Preto je to production change s auditom, ownerom a invalidation semantics pre predchádzajúcu evidence.

## 4. Ring poradie vychádza z failure risks

Atlas nepoužíva jednoduché „od najmenšieho po najväčší“. Každý ring testuje inú neistotu:

```text
ring 0
→ rýchla diagnostika, ale nereprezentatívne identity a data scale

ring 1
→ reálni users a integrations pri silnom support kontakte

ring 2
→ broad behavior a region mix

ring 3
→ high-scale queues, DB pools, custom webhooks a large-tenant workflows

ring 4
→ regulatory evidence, long outcome latency a change-window constraints
```

Najkritickejší zákazník nie je dobrý prvý dôkaz len preto, že generuje veľa trafficu. Naopak ring 0 nemôže byť jediný dôkaz, pretože obchádza externé identity, client skew a produkčný data mix.

## 5. Entry contract chráni prechod do širšieho risku

Pred ringom 3 Atlas overí:

```text
predchádzajúce ring verdicts complete a fresh
+ M2 a config identity nezmenené
+ ring 3 membership H12 stabilná
+ large-tenant capacity a webhook quotas pripravené
+ old/new contracts kompatibilné s rings na M_prev
+ support a communication pripravené
+ partial recovery eligible
```

Ak ring 3 používa inú config revision než ring 2, výsledok ring 2 sa neprenáša automaticky. Nový deployment subject potrebuje vlastnú evidence.

## 6. Observation contract je ring-specific

Každý ring má spoločné release guardrails, ale aj vlastné outcomes.

Pre ring 3:

```text
technical
→ DB wait, queue age, webhook retry, requests per tenant

functional
→ CreateOrder completion, idempotency, custom webhook delivery

business
→ large-tenant abandonment, reconciliation completion, support signal

sample
→ minimum number large-tenant orders a integration variants

duration
→ dostatočná pre async webhook a reconciliation latency
```

Fixná hodinová observation pre všetky ringy by mohla byť dostatočná pre HTTP errors, ale nie pre večerný batch alebo mesačný regulated workflow.

## 7. Version skew je explicitný compatibility contract

Počas rollout-u musí M2 koexistovať s `M_prev`:

- API clients v rôznych rings;
- old/new event producers a consumers;
- shared database schema;
- cache a session formats;
- authentication claims;
- worker a scheduler generations;
- feature flags a config.

Atlas určí maximálny podporovaný skew:

```text
M2 vs M_prev podporované do deadline D
M2 nesmie emitovať contract, ktorý M_prev consumer odmietne
schema contract phase sa nezačne pred uzavretím rollback windowu
```

Permanentný partial rollout nie je stabilný cieľ. Je to rastúci support, security a compatibility debt.

## 8. Shared state môže prekročiť hranicu ring-u

Ring 1 môže vytvoriť row alebo event, ktorý neskôr spracuje ring 3 na starej verzii. Regionálny ring môže zapisovať do globálnej databázy. Obmedzená membership teda nemusí znamenať obmedzený state blast radius.

Atlas používa:

```text
expand-contract schema
forward-tolerant consumers
versioned cache keys
cross-ring workflow telemetry
fencing pre global workers
irreversible mutations až po relevantnom rollout milestone
```

Partial rollback jedného ring-u je bezpečný iba ak staršia verzia rozumie state-u vytvorenému novšími ringmi.

## 9. Support a communication sú súčasť runtime operability

Support musí z privacy-safe lookupu zistiť:

```text
tenant T42
→ ring 3
→ manifest M2
→ config C17
→ membership H12
→ current rollout state observing
```

Každý ring má ownera, known-issues channel, audience-specific release notes, opt-out alebo recovery model a escalation path.

Ak používateľ hlási chybu a support nevie určiť jeho ring/version, incidentná segmentácia stráca prvý observation point.

## 10. Worked failure: API a worker používali odlišnú membership revision

Atlas API načítalo membership `H12`, ale worker fleet mala stale `H11`. Tenant T42 bol v API ring 3, no worker ho stále považoval za ring 2.

```text
API M2 prijme order a zapíše nový risk state
→ worker M_prev podľa H11 spracuje rovnaký tenant
→ old worker nepozná nový state transition
→ event sa retryuje
→ queue lag rastie iba pre časť tenantov
→ dashboard podľa API ring ID ukazuje neúplný obraz
```

### Príčina

Ring membership sa považovala za routing detail, nie za cross-service production contract. Telemetry niesla ring podľa lokálneho evaluatoru bez membership revision.

### Dôsledok

Incident nebol čistý „ring 3 release failure“. Bol to inconsistent cohort boundary naprieč API a workerom.

### Trvalá náprava

```text
membership revision v každom evente a trace
→ atomic publish alebo compatible transition H11 → H12
→ worker precondition na supported membership revision
→ cross-service membership consistency synthetic
→ inventory reconciliation
```

## 11. Worked failure: počet tenants skryl dominantný workload

Ring 3 obsahoval iba 3 % tenantov, ale jeden large tenant generoval 28 % order volume.

```text
membership count vyzerá malý
→ promotion sa označí ako bounded exposure
→ large tenant spustí paralelný import
→ DB pool, webhook quotas a queue partitions sa saturujú
→ shared dependencies degradujú aj pre staršie rings
```

### Príčina

Blast radius sa odhadoval počtom členov, nie workloadom, shared dependencies a business dopadom.

### Náprava

Atlas pridal workload-weighted inventory, per-tenant capacity budget, dominant-member check a samostatný pre-ring canary pre najväčšieho tenanta.

## 12. Kauzálny diagnostický walkthrough

Symptom: po vstupe do ring 3 rastie queue lag iba pre niektoré tenants a časť ich API requests je zdravá.

### Krok 1 — stabilizuj release inventory

```text
ring 3 manifest M2
config C17
membership H12
worker membership observed H11/H12 mixed
rollout generation R31
```

### Krok 2 — formuluj konkurenčné hypotézy

```text
H1: M2 code regression zasahuje celý ring 3
H2: workload skew preťažuje shared queue
H3: API a workers nesú konzistentne odlišné ring membership
H4: ring-specific config alebo integration spôsobuje failure
H5: globálny broker incident náhodou koreluje s promotion
```

### Krok 3 — vyber observation points

- error/lag podľa artifact digestu a tenant testuje H1;
- work volume a partition saturation podľa tenant testujú H2;
- membership revision v API trace, evente a worker evaluation testuje H3;
- config/integration revision podľa tenant testuje H4;
- ostatné služby a rings na brokeri testujú H5.

Atlas nájde, že problematické events nesú API `H12`, ale worker loguje `H11`; broker mimo týchto partitionov je zdravý. H3 vysvetľuje selektívny failure.

### Krok 4 — containment podľa boundary

Promotion do ďalšieho ring-u sa zastaví. Nový risk transition sa flagom vypne pre affected tenants, worker membership sa zosúladí a poison events sa po tolerant-reader fixe replaynú.

Rollback API samotného by nevyriešil už emitované events ani stale worker policy.

### Krok 5 — over outcome

Recovery vyžaduje:

```text
jedna membership revision naprieč API/workermi
event retries a queue age klesajú
cross-ring functional invariant prejde
support inventory zobrazuje správny state
```

### Krok 6 — vráť learning

Incident sa mení na atomic membership rollout contract, membership revision propagation SLO a cross-service ring consistency gate.

## 13. Partial recovery je decision nad shared state-om

Možnosti:

- pause current ring;
- disable feature pre current ring;
- rollback affected ring;
- roll-forward fix iba v current ring;
- fix-forward vo všetkých rings, ak shared state prekročil hranicu;
- zastaviť global producer/worker;
- reconciliation alebo data repair.

Partial rollback nie je bezpečný, ak M2 už vytvorilo state alebo events, ktorým `M_prev` nerozumie. Recovery sa vyberá podľa failure domainu, nie podľa ring labelu.

## 14. Rollout deadline a cleanup obmedzujú skew debt

Po final ring-u Atlas:

```text
zjednotí manifest/config/flags
→ odstráni release-specific membership exceptions
→ ukončí old support state
→ uzavrie rollback window
→ odstráni obsolete code paths
→ archivuje ring evidence
```

Ak rollout ostane mesiace v polovici, pribúdajú test combinations, security fixes pre viac verzií, support ambiguity a nemožnosť contract cleanupu.

## 15. Diagnostický runbook

1. Potvrď ring membership policy, revision a konkrétny subject.
2. Zostav release inventory manifest/config/exposure pre všetky ringy.
3. Urči version skew, rollout generation a deadline.
4. Porovnaj workload, integrations a support context medzi healthy a failed ringom.
5. Over telemetry dimensions vrátane membership revision.
6. Skontroluj shared state, cross-ring events a global dependencies.
7. Formuluj code, workload, membership, config a dependency hypotézy.
8. Posúď partial rollback alebo feature-disable eligibility.
9. Po recovery reconciliuj inventory, queues a support state.
10. Uzavri rollout stall a release-specific cleanup actions.

## 16. Referenčné pravidlá

- Ring je stabilná production cohort, nie environment name.
- Membership je versionovaná production policy.
- Release inventory spája ring, subject, config, exposure a recovery state.
- Rovnaký immutable artifact sa promuje naprieč rings.
- Ring poradie zvyšuje konkrétnu fidelity, nie iba percento.
- Počet members nevyjadruje workload ani blast radius.
- Observation contract je ring-specific.
- Version skew má compatibility contract a deadline.
- Shared state môže prekročiť ring boundary.
- Partial rollback potrebuje cross-ring state analysis.
- Support musí vedieť určiť ring a release identity subjektu.

## 17. Časté omyly

### „Ring je dev, stage a prod“

Ringy sú production cohorts, nie environment lifecycle.

### „3 % tenantov je malý blast radius“

Jeden tenant môže dominovať workloadu alebo shared dependencies.

### „Membership stačí vyhodnotiť na ingress-e“

Celý cross-service workflow musí používať kompatibilnú ring identity.

### „Každý ring môže mať vlastný build“

Potom sa nepromuje jeden overený release subject.

### „Partial rollback ovplyvní iba jeden ring“

Shared database a events môžu preniesť nový state do ostatných rings.

## 18. Zhrnutie

Atlas ring lifecycle je:

```text
immutable release subject
→ stable membership a complete inventory
→ risk-specific entry contract
→ ring deployment/exposure
→ workload-aware observation
→ promote/pause/abort/inconclusive
→ cross-ring-compatible recovery
→ skew deadline a cleanup
```

Ring deployment poskytuje kontrolu nad tým, kto používa ktorú verziu, ale tým zároveň vytvára distribuovaný multi-version systém. Je bezpečný iba vtedy, keď membership, inventory, compatibility a support fungujú ako jedna release control plane, nie ako nezávislé zoznamy tenantov.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Shadow deployment](shadow-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Feature flags →](feature-flags.md)
<!-- KNOWLEDGE-NAVIGATION:END -->