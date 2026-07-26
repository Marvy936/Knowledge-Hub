# Rolling update

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Rolling update postupne vymieňa starú fleet za novú. Dostupnosť zachováva tým, že po určitý čas existujú obe generácie súčasne. Táto výhoda zároveň vytvára hlavnú failure boundary: old a new code, data contracts, queues, caches a sessions musia bezpečne koexistovať.

```text
old fleet healthy
→ vytvor new batch
→ over functional readiness a capacity
→ priraď časť trafficu/worku
→ porovnaj old/new evidence
→ drain a odstráň old batch
→ opakuj
→ full new fleet
→ delayed observation
```

Rolling update preto nie je „zero-downtime deployment mode“. Je to kontrolovaná výmena capacity pod mixed-version compatibility contractom.

## 1. Nosný model: capacity exchange s dočasným overlapom

V každom okamihu platí:

```text
desired service capacity
= old available
+ new available
- unavailable alebo pending capacity
```

Controller opakovane vykonáva päť rozhodnutí:

```text
1. koľko new capacity smie vytvoriť
2. kedy je new capacity funkčne ready
3. koľko trafficu alebo worku jej priradiť
4. či evidence povoľuje pokračovanie
5. koľko old capacity možno bezpečne drainovať
```

Ak chýba compatibility, rollout môže poškodiť shared state. Ak chýba capacity headroom, rollout môže vytvoriť outage. Ak chýba version-level evidence, controller iba pomalšie rozšíri chybu na celú fleet.

## 2. Nosný scenár: Atlas Orders API 3.11.0

Atlas nasadzuje release manifest `M2` do fleet desiatich Orders API instances v troch availability zones.

```text
old artifact = D_old
new artifact = D_new
rendered config = C17
database phase = expanded schema S_expand
rollout policy = maxSurge 2, maxUnavailable 1
batch ordering = najviac jedna instance per zone
```

Plánovaný rollout:

```text
10 old / 0 new
→ 10 old / 2 new starting
→ 10 old / 2 new ready
→ observation batch 1
→ drain 2 old
→ 8 old / 2 new
→ ďalší batch
...
→ 0 old / 10 new
→ post-rollout watch
```

New API pridáva optional `riskDecision`, ale počas overlapu musí:

- stále čítať rows vytvorené old API;
- zapisovať format čitateľný old workerom;
- emitovať iba event contract tolerovaný old consumers;
- používať cache a session format kompatibilný s oboma generáciami;
- zachovať idempotency semantics.

## 3. `maxSurge` a `maxUnavailable` sú absolútne capacity rozhodnutia

`maxSurge=2` povoľuje dočasne dvanásť instances. `maxUnavailable=1` povoľuje jednu nedostupnú instance voči desired countu.

Tieto hodnoty sa nesmú hodnotiť iba ako percentá. Pri malej fleet môže zaokrúhlenie zmeniť význam:

```text
2 replicas
maxUnavailable = 50 %
→ platforma môže odstaviť 1
→ strata 50 % capacity
```

Atlas pred rolloutom prepočíta:

```text
available throughput old fleet
- peak utilization
- failure reserve jednej ďalšej instance
+ reálne schedulovateľný surge throughput
```

Surge existuje iba vtedy, keď sú dostupné aj downstream zdroje:

- CPU, memory a zone capacity;
- load-balancer targets a IPs;
- database connections;
- broker partitions alebo consumer slots;
- external API quotas;
- licenses a storage throughput.

Dvanásť ready pods nie je dôkaz dvanásťnásobnej použiteľnej capacity, ak všetky zdieľajú rovnaký vyčerpaný DB pool.

## 4. Mixed-version compatibility je vstupná precondition

Atlas pred prvým batchom overí kombinácie, ktoré počas rollout-u skutočne vzniknú:

```text
old API + old worker + expanded schema
new API + old worker + expanded schema
old API + new worker + expanded schema
new API + new worker + expanded schema
```

Compatibility zahŕňa:

- syntax aj behavior API;
- database reads a writes;
- event schema, ordering a unknown values;
- queue retry a idempotency;
- cache key význam a serialization;
- session formát;
- config a feature flags;
- old/new client správanie.

Schema-additive zmena nemusí byť behaviorálne kompatibilná. Nový producer môže napríklad pridať enum hodnotu, ktorú old consumer nedokáže spracovať.

Ak sa bezpečné overlap okno nedá vytvoriť, rolling update nie je vhodná stratégia bez predchádzajúcej expand alebo compatibility fázy.

## 5. Functional readiness chráni traffic boundary

Nová instance prechádza:

```text
scheduled
→ image pulled
→ process started
→ startup complete
→ dependencies connected
→ functional synthetic passed
→ minimum-ready window
→ traffic eligible
```

Rozlišuj:

- startup probe: proces ešte inicializuje;
- liveness: proces je unrecoverably stuck;
- readiness: instance dokáže bezpečne obslúžiť relevantný request.

Atlas readiness pre Orders nevykoná iba `/health`. Vytvorí kontrolný read/write request s izolovanou identitou, overí authorization, database path a idempotentný retry. Potom čaká minimum-ready duration, aby odhalil warm-up alebo pool instability.

Slabá readiness vloží chybnú new capacity do trafficu. Príliš prísna readiness viazaná na globálne degraded dependency môže vyradiť old aj new fleet naraz. Readiness musí hodnotiť schopnosť instance obslúžiť traffic, nie predstierať úplnú health analýzu celého sveta.

## 6. Traffic weight sa neodvodzuje iba z počtu instances

Pri `8 old / 2 new` nemusí new generation dostať presne 20 % requests. Rozdelenie menia:

- persistent connections;
- session affinity;
- zone-aware routing;
- rozdielna response latency;
- connection pool reuse;
- request hashing;
- long-lived streams.

Version-level telemetry preto zaznamenáva skutočné requests, sessions a work items podľa artifact digestu. Observation gate porovnáva normalizované outcomes, nie iba replica counts.

## 7. Old batch sa odstraňuje až po drain boundary

Bezpečné odstránenie:

```text
old instance marked not ready
→ routing propagation
→ stop new work intake
→ drain active requests/connections
→ checkpoint alebo requeue queue work
→ release locks
→ terminate
```

Ak platforma ukončí pod skôr než load balancer prestane posielať requests, používateľ dostane reset. Ak worker ackne položku pred side effectom a potom sa ukončí, work sa stratí. Ak ju neackne po side effecte, retry môže vytvoriť duplicitu.

Termination grace period preto vychádza z reálneho request a work lifecycle-u, nie z univerzálnych tridsiatich sekúnd.

## 8. Observation gate medzi batchmi je rozhodovací mechanizmus

Po každom batchi Atlas skladá evidence:

```text
subject = D_new + C17 + batch ID + current old/new counts

technical
→ error rate, p95/p99, restarts, saturation, dependency retries

functional
→ CreateOrder completion, idempotency, authorization, event completion

business
→ accepted-order rate, rejection distribution, support signal
```

Verdict je:

- `continue` — evidence complete a thresholds splnené;
- `pause` — treba dlhšie okno alebo triage;
- `abort` — rollout nesmie rozšíriť exposure;
- `rollback` — previous generation je state-compatible;
- `roll-forward` — návrat je nebezpečnejší než oprava;
- `inconclusive` — chýba porovnateľná alebo úplná evidence.

Missing telemetry nie je povolenie pokračovať.

## 9. Topology-aware ordering chráni failure domains

Atlas nevymení naraz celú zónu. Každý batch rozloží new instances tak, aby náhodný zone failure neodstránil spolu s rolloutom väčšinu capacity.

```text
batch 1 → jedna new instance v zone A a B
batch 2 → jedna new instance v zone C a A
```

Controller rešpektuje anti-affinity, disruption budgets a current node health. Rollout, autoscaler a plánovaná node maintenance nesmú nezávisle predpokladať tú istú rezervu.

## 10. Autoscaler a rollout musia mať explicitný ownership

Autoscaler môže počas rollout-u:

- zvýšiť desired count pre cold-start latency;
- spotrebovať surge quota;
- scale-downovať old alebo new generation;
- meniť requests per instance;
- skresliť version-level porovnanie.

Atlas preto zaznamenáva desired count a autoscaler decision pri každom batchi. Observation používa request-normalized metrics a rollout controller vie rozlíšiť plánovanú capacity exchange od autoscaling mutation.

## 11. Worked failure: new producer rozbil stále aktívny old worker

New API začalo emitovať event stav `PENDING_REVIEW`. Schema registry zmenu označil ako additive, ale old worker používal exhaustívny enum switch.

```text
2 new API instances prijmú časť orders
→ emitujú PENDING_REVIEW
→ 8 old workers načítajú event
→ deserialization alebo switch zlyhá
→ message sa retryuje
→ poison queue a lag rastú
→ API request metrics zostávajú prevažne zelené
```

### Príčina

Rollout overoval new API s new workerom, nie reálne mixed combinations. Tím zamieňal syntaktickú schema compatibility za behaviorálnu consumer compatibility.

### Dôsledok

Binary rollback API nezmazal poison messages. Recovery vyžadovala pause, zastavenie nového event variantu feature flagom, tolerantný old-worker patch a replay po oprave.

### Trvalá náprava

```text
old-consumer/new-producer contract fixture
→ explicitná enum openness policy
→ event variant feature gate
→ poison-message guardrail per producer digest
→ expand producer až po tolerant-reader rollout-e
```

## 12. Worked failure: readiness pass vytvoril capacity dip

New Orders process označil readiness za true hneď po otvorení portu. Pri prvom produkčnom loade však lazy-inicializoval rules engine a otvoril veľký DB pool.

```text
new pod ready
→ controller okamžite drainuje old pod
→ new pod dostane traffic
→ cold initialization zvýši latency
→ clients retryujú
→ DB connection pressure rastie
→ ďalšie new pods sa tiež označia ready
→ rollout znižuje effective throughput batch za batchom
```

Replica count vyzeral správne, ale použiteľná capacity klesala.

### Príčina

Readiness neobsahovala critical path ani minimum-ready window. `maxUnavailable` počítal ready objects, nie reálny throughput. Observation gate nemal requests-per-instance a retry-amplification signál.

### Recovery

Atlas pause-nul rollout, prestal odstraňovať old pods, znížil traffic weight new generation, predhrial rules engine a pools a obnovil pokračovanie až po stabilnej functional readiness.

## 13. Kauzálny diagnostický walkthrough

Symptom: po druhom batchi rastie p99 a error rate, ale celkový počet `Ready` pods neklesol.

### Krok 1 — zafixuj rollout identity a state

```text
rollout generation R17
old digest D_old = 6 instances
new digest D_new = 4 instances
config C17
batch 2 observing
maxSurge 2 / maxUnavailable 1
```

Bez tejto identity by dashboard mohol miešať predchádzajúci batch, autoscaler alebo inú config revision.

### Krok 2 — formuluj odlišné mechanizmy

```text
H1: code regression na každom new requeste
H2: new capacity je cold alebo poddimenzovaná
H3: globálna DB degradácia zasahuje obe generácie
H4: routing stále posiela traffic drainovaným old pods
```

### Krok 3 — použi diskriminačné observation points

- error a latency podľa digestu rozlišujú H1/H2 od H3;
- requests a CPU/DB connections per instance rozlišujú H1 od H2;
- old-target request count po `not ready` testuje H4;
- DB telemetry ostatných služieb testuje globálnu H3.

Výsledok:

```text
old latency normálna
new latency vysoká iba prvé minúty
new requests per instance 2.3× old
new DB pools otvárajú connection burst
old drain routing je korektný
```

H2 vysvetľuje symptom. Nejde o univerzálnu code chybu ani globálny DB incident.

### Krok 4 — zastav príčinný transition

Pause zabráni ďalšiemu odstraňovaniu old capacity. Zníženie new traffic weightu a warm-up stabilizujú new pods. Slepý rollback by spustil ďalší rolling transition a zbytočne zväčšil churn.

### Krok 5 — over outcome

Pokračovanie je povolené až keď:

```text
new minimum-ready window prejde pod loadom
requests per instance sú porovnateľné
DB connection headroom je zdravý
retry rate sa vráti k baseline
business completion ostáva zdravá
```

### Krok 6 — vráť learning do modelu

Failure sa zmení na warm-up synthetic, minimum-ready duration, per-version capacity gate a test rollout-u pri autoscaler scale-up udalosti.

## 14. Rolling rollback je ďalší rollout

Rollback neprepne pointer okamžite. Musí znovu vytvárať previous generation a postupne odstraňovať chybnú.

```text
mixed old/new bad state
→ pause forward rollout
→ potvrď rollback eligibility
→ vytvor previous generation
→ functional readiness
→ batch-by-batch replacement
→ observation
```

Ak new generation už zmenila schema, cache, sessions alebo events nekompatibilne, previous version nemusí byť eligible. Vtedy Atlas preferuje feature disable, worker containment alebo roll-forward fix.

Platformové `undo` pozná desired object revision. Nevie automaticky dokázať data compatibility.

## 15. Diagnostický runbook

1. Urči rollout generation, batch a old/new/pending/unavailable counts.
2. Potvrď artifact, config, migration a policy identity každej generácie.
3. Prepočítaj `maxSurge` a `maxUnavailable` na absolútnu použiteľnú capacity.
4. Rozlíš scheduling, startup, readiness, routing a runtime failure.
5. Porovnaj skutočné requests/work per digest, nie iba replica count.
6. Over mixed-version DB, event, cache, session a worker compatibility.
7. Pri termination probléme skontroluj routing propagation a active work.
8. Pri pause znovu over freshness a environment state pred resume.
9. Rozhodni rollback alebo roll-forward podľa mutable-state compatibility.
10. Po recovery over business a data invariants a pridaj skorší control.

## 16. Referenčné pravidlá

- Rolling update vymieňa capacity a zámerne vytvára mixed-version obdobie.
- `maxSurge` a `maxUnavailable` sa hodnotia absolútne aj voči downstream headroomu.
- Funkčná readiness predchádza trafficu a odstráneniu old capacity.
- Replica count nie je automaticky throughput.
- Old/new contracts musia pokrývať DB, events, cache, sessions a workers.
- Observation gate potrebuje version-level technical, functional a business evidence.
- Topology-aware ordering nesmie spotrebovať celú failure-domain rezervu.
- Missing evidence vedie k `inconclusive`, nie k pokračovaniu.
- Rolling rollback je ďalší rollout.
- Diagnostika odlišuje code effect, capacity effect, global dependency a routing failure.

## 17. Časté omyly

### „Rolling update znamená zero downtime“

Dostupnosť závisí od kompatibility, functional readiness a reálnej rezervy.

### „Ready pods znamenajú zachovanú capacity“

Cold alebo pomalšia new generation môže mať výrazne nižší throughput.

### „Additive event schema je kompatibilná“

Old consumer môže mať closed enum alebo iný behaviorálny predpoklad.

### „Rollback je okamžitý“

Je to ďalší batch rollout a môže byť data-nekompatibilný.

### „Percentuálne hodnoty fungujú rovnako pri každej fleet“

Rounding pri dvoch alebo troch replikách môže vytvoriť veľký absolútny outage.

## 18. Zhrnutie

Atlas rolling lifecycle je:

```text
immutable old/new generations
→ mixed-version compatibility evidence
→ capacity a topology preconditions
→ new batch scheduling
→ functional readiness + minimum-ready window
→ version-aware traffic observation
→ old batch drain
→ continue/pause/abort/recover
→ full new fleet + delayed watch
```

Rolling update bezpečne znižuje blast radius iba vtedy, keď controller nevymieňa počty objektov, ale dôveryhodnú použiteľnú capacity. Jeho hlavnou cenou je dočasný systém dvoch generácií, ktorého contracts a mutable state musia byť navrhnuté ešte pred prvým batchom.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Recreate deployment](recreate-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Blue-green deployment →](blue-green-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
