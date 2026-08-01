# Chaos testing

Chaos testing je riadený experiment, ktorý overuje správanie a recovery systému pri konkrétnom failure mode. Nie je to náhodné rozbíjanie infraštruktúry. Experiment začína hypotézou o steady state a presným fault modelom.

Experiment contract obsahuje:

```text
subject a environment
steady-state hypothesis
fault a injection point
blast radius
observation window
abort criteria
recovery expectation
business reconciliation
owner a communication
```

Steady state je merateľný normálny outcome, napríklad successful request rate, queue delay alebo completed orders. Hypotéza predpovedá, čo sa stane počas faultu a ako rýchlo sa systém zotaví.

Fault môže byť process crash, network latency/loss, dependency error, resource exhaustion, clock skew alebo data inconsistency. Injection point musí zodpovedať reálnemu threat modelu. Zastavenie jedného stateless procesu neoverí region failure ani corrupted message.

Neutrálny príklad: systém má dve instances a tvrdí, že výpadok jednej nespôsobí user-visible outage. Experiment najprv potvrdí steady state, potom ukončí jednu instance, sleduje errors, load redistribution a recovery a napokon overí, že backlog a business state sú konzistentné.

Safety state machine môže byť:

```text
precheck
→ arm
→ inject
→ observe
→ abort alebo continue
→ remove fault
→ wait for recovery
→ reconcile
→ close experiment
```

Abort criterion musí byť automaticky pozorovateľný a rýchlejší než neprijateľný impact. Manual observation bez jasného threshold-u nie je dostatočný control.

Experiment nekončí odstránením faultu. Treba overiť backlog drain, duplicate alebo lost operations, resource release a návrat všetkých SLO/business metrics. Recovery time a data outcome sú často dôležitejšie než okamžitá dostupnosť.

Výsledok chaos testu má viesť k trvalej zmene: retry budget, circuit breaker, capacity, runbook, alert, architecture alebo nový regression test. Opakovanie rovnakého experimentu bez remediation closure má nízku hodnotu.

## 1. Cieľ kapitoly

Nosný model kapitoly je resilience-experiment lifecycle:

```text
historický alebo modelovaný failure mode
→ steady-state contract
→ mechanizmus, ktorý má resilience zabezpečiť
→ experiment validity a safety preconditions
→ fault model, target a blast radius
→ live technical/business evidence
→ abort alebo dokončenie
→ fault removal, backlog/reconciliation a recovery deadline
→ trvalá zmena designu, controlu alebo runbooku
→ opakovaný experiment
```

Cieľom nie je dokázať, že systém „je odolný“. Každý experiment poskytuje úzko ohraničený dôkaz pre konkrétny fault, topology, workload, artifact a čas.

## 2. Nosný scenár: Atlas Orders 3.9.2

Atlas Orders spracúva objednávku cez:

```text
client
→ edge a orders-api
→ PostgreSQL transaction/outbox
→ broker
→ payment worker
→ external payment provider
→ OrderConfirmed event
→ confirmation a audit
```

Tím tvrdí, že systém zvládne payment-provider brownout:

```text
provider odpovedá 8 až 20 sekúnd alebo timeoutuje
→ requesty majú bounded deadline
→ retries používajú budget, backoff a idempotency key
→ worker pool a DB connections sa nevyčerpajú
→ nevznikne duplicate authorization
→ objednávky prejdú do explicitného pending/degraded state
→ po obnove sa backlog vyprázdni do 10 minút
```

Toto tvrdenie je experimentovateľná hypotéza. Bežný happy-path E2E test ani vypnutie jedného Podu ju nepreukazuje.

## 3. Steady state je používateľský výsledok

Steady state nie je počet bežiacich replík. Atlas ho definuje cez outcomes:

- CreateOrder acceptance rate zostane nad dohodnutou hranicou;
- používateľ dostane explicitný pending alebo retry-safe výsledok;
- nevznikne žiadna duplicate payment authorization;
- queue oldest-message age zostane bounded;
- authorization a tenant isolation zostanú zachované;
- error-budget burn neprekročí abort threshold;
- po obnove provideru sa backlog vyprázdni do 10 minút;
- všetky objednávky skončia v terminal alebo auditovateľnom recovery state.

Interné metrics ako leader election alebo počet ready pods sú diagnostické signály. Nemôžu nahradiť business correctness a recovery oracle.

## 4. Vyvrátiteľná hypotéza

Dobrá hypotéza má tvar:

```text
Ak nastane fault X,
systém zachová outcome Y v limite Z,
pretože mechanizmus M funguje,
a po odstránení faultu sa zotaví do času R.
```

Atlas hypotéza:

> Ak payment provider zvýši response time na 8–20 sekúnd pri 20 % requestov počas piatich minút, orders-api a worker zachovajú bounded queues, celková failure rate zostane pod guardrailom, nevznikne duplicate authorization a backlog sa po odstránení faultu vyprázdni do desiatich minút vďaka end-to-end deadlines, retry budgetu, idempotency a admission controlu.

Tvrdenie „systém by mal zvládnuť timeout“ neposkytuje presný oracle ani rozhodnutie.

## 5. Experiment contract

Pred spustením Atlas eviduje:

- **risk a ownera** — ktorú resilience vlastnosť experiment chráni;
- **artifact a topology** — digest, config, replicas, DB/broker/provider route;
- **workload** — arrival model, operation mix, tenant a dataset;
- **steady-state metrics** — primary outcomes a guardrails;
- **fault model** — typ, intensity, direction, duration a correlation;
- **target identity** — presný process, route, dependency alebo cohort;
- **preconditions** — zdravý baseline, observability a recovery capacity;
- **blast radius** — maximálny prípustný dopad;
- **abort criteria** — automatické a manuálne thresholds;
- **kill switch** — fault removal nezávislé od fault domainu;
- **recovery contract** — čo znamená úplné zotavenie;
- **evidence** — timeline, metrics, traces, logs a experiment events;
- **communication** — observers, on-call a incident channel;
- **remediation closure** — issue, owner, deadline a repeat criteria.

Experiment bez tohto contractu je neauditovateľný zásah.

## 6. Validita experimentu

Výsledok nie je iba pass alebo fail:

```text
HYPOTHESIS_CONFIRMED
→ fault bol platne aplikovaný a steady state/recovery ostali v limite

HYPOTHESIS_REFUTED
→ platný experiment porušil outcome alebo recovery contract

INCONCLUSIVE
→ fault prebehol, ale sample alebo signal nestačí

INVALID
→ target, baseline, workload, instrumentation alebo fault nezodpovedali contractu

ABORTED_FOR_SAFETY
→ guardrail zastavil experiment; evidence stále ukazuje safety limit
```

Invalid alebo inconclusive experiment nie je dôkaz resilience. Rovnako automatický abort nie je „zlyhanie chaos nástroja“; môže byť správnym výsledkom safety systému.

## 7. Baseline a preconditions

Pred faultom Atlas overí:

```text
správny artifact/config
→ stabilný traffic a SLI baseline
→ zdravé DB, broker a provider connections
→ dostatočná spare capacity
→ funkčné dashboards, alerts a traces
→ dostupný kill switch a recovery path
→ žiadny súbežný incident alebo risk change
→ správny target preview
```

Ak backlog rastie ešte pred experimentom, nie je možné pripísať výsledok faultu. Baseline potrebuje interval, nie jednu okamžitú zelenú hodnotu.

## 8. Fault model

Fault má reprezentovať realistické failure semantics. Atlas rozlišuje:

- **outage** — okamžité connection refused alebo unavailable;
- **brownout** — vysoká alebo variabilná latency, partial responses a timeouts;
- **intermittency** — premenlivý failure iba časti requestov;
- **stale/corrupt response** — odpoveď existuje, ale porušuje contract;
- **resource pressure** — CPU, memory, disk, connections alebo quotas;
- **network partition** — asymetrická alebo smerovo obmedzená strata komunikácie;
- **identity failure** — credential expiry, revocation alebo denied permission;
- **process/node/zone loss** — strata execution capacity;
- **human/control-plane failure** — chybný deploy, runbook alebo delayed response.

Brownout môže byť nebezpečnejší než úplný outage, pretože drží connections a workers, spúšťa retries a vytvára unknown outcomes.

## 9. Target identity a blast radius

Pred aktiváciou faultu Atlas zobrazí target preview:

```text
cluster/account/region
→ namespace a workload UID
→ route alebo dependency endpoint
→ matched replicas a cohort
→ excluded resources
→ expected traffic share
```

Selector `app=orders` môže omylom zasiahnuť API aj worker alebo viac environmentov. Scope expansion mimo allowlistu blokuje experiment.

Blast radius je najmenší rozsah, ktorý stále testuje hypotézu. Môže byť obmedzený na:

- jeden interný tenant;
- jednu worker cohortu;
- 5 % syntetického alebo production trafficu;
- jednu availability zone;
- read-only alebo compensatable workflow;
- päťminútové fault window;
- maximálnu latency a error intensity.

Blast radius zahŕňa downstream amplification. Fault na provider route môže cez retries zvýšiť load v orders-api, DB aj brokeri.

## 10. Safety state machine

Bezpečný experiment prechádza stavmi:

```text
planned
→ prechecks
→ armed
→ fault active
→ observing
→ fault removed
→ recovery observing
→ completed / aborted / invalid
→ cleanup verified
```

Každý stav má timeout a povolené transitions. Experiment nesmie prejsť do `fault active`, ak baseline, target preview alebo observability precheck zlyhá.

Safety controls zahŕňajú:

- allowlist/denylist scope;
- intensity a duration limit;
- live guardrail evaluation;
- independent kill switch;
- automatické fault removal;
- emergency traffic shift alebo feature disable;
- zákaz súbehu s incidentom alebo migráciou;
- cleanup verification;
- audit každého state transition.

## 11. Observation points a kompozitný oracle

Atlas koreluje:

```text
client arrival a response
→ edge retries a timeouts
→ orders-api concurrency a queue
→ DB pool waits a transaction state
→ outbox/broker age
→ worker attempts a deadlines
→ provider request/authorization identity
→ final order state
→ user confirmation a audit
```

Primary oracle sleduje business correctness. Guardrails sledujú širší systém: error budget, resource saturation, cross-tenant safety, duplicate side effects a dopad na unrelated journeys.

Ak fault injection tool hlási „latency applied“, ale traces neukazujú zasiahnutú route, experiment je invalidný.

## 12. Deadlines, retries a unknown outcome

Timeout v jednej vrstve nie je automaticky zrušenie operácie v ďalšej vrstve:

```text
worker odošle payment authorization
→ provider operáciu commitne
→ response sa stratí alebo príde po deadline
→ worker vidí timeout
→ retry môže vytvoriť duplicate side effect
```

Resilience contract preto potrebuje:

- end-to-end deadline propagation;
- klasifikáciu retryable a non-retryable failures;
- bounded attempts a retry budget;
- exponential backoff a jitter;
- idempotency identity zachovanú cez všetky vrstvy;
- reconciliation pre unknown outcome;
- ochranu pred retry amplificationom na client/proxy/service vrstve.

Chaos test overuje celý mechanizmus, nie iba to, že circuit breaker zmenil stav.

## 13. Graceful degradation a admission control

Pri provider brownoute Atlas nemusí garantovať okamžitý terminal success. Môže zachovať prijateľný degraded contract:

```text
nová objednávka
→ prijatá iba ak existuje queue a DB budget
→ stav PAYMENT_PENDING
→ používateľ dostane explicitný status a correlation ID
→ background reconciliation pokračuje po obnove
```

Admission control, bounded queues a load shedding chránia core state. Neobmedzené prijímanie práce môže dočasne zlepšiť acceptance rate, ale vytvorí neobnoviteľný backlog a dlhší incident.

## 14. Recovery je samostatná fáza dôkazu

Odstránenie faultu nie je koniec experimentu. Atlas sleduje:

- návrat latency a error rate;
- vyprázdnenie queue a oldest-message age;
- skončenie retry stormu;
- uvoľnenie DB connections a workers;
- reconciliation unknown outcomes;
- absence duplicate authorization;
- terminal order states;
- cache a replica convergence;
- odstránenie temporary degraded mode;
- splnenie recovery deadline.

Systém môže po fault-e vyzerať healthy, ale backlog drain môže znovu saturovať DB alebo provider. Recovery phase potrebuje vlastný oracle a abort criteria.

## 15. Worked failure: brownout vytvoril retry amplification a duplicity

Atlas aplikoval 12-sekundovú provider latency na 20 % payment requestov. Každá vrstva mala vlastný retry:

```text
client retry 2×
× edge retry 2×
× worker retry 3×
→ rovnaká business operácia mala viac súbežných attempts
→ provider commitol prvú authorization
→ oneskorené responses boli považované za timeout
→ ďalšie attempts použili nové idempotency keys
→ vznikli duplicate payment authorizations
→ DB pool a worker queue sa saturovali
```

### Root cause

Timeout a retry policies boli navrhnuté lokálne. Neexistoval end-to-end retry budget ani business idempotency identity propagovaná cez client, API, event a provider request.

### Náprava

- jedna order/payment idempotency identity prechádza celým workflowom;
- edge nere-tryuje non-idempotent write bez explicitného contractu;
- worker má bounded attempts, deadline a jitter;
- provider timeout spúšťa reconciliation, nie slepý nový charge;
- queue a DB admission limits chránia core dependencies;
- metrics sledujú attempts per business operation;
- regression portfolio obsahuje unit state machine, provider simulator, component retry test a periodický chaos experiment.

## 16. Worked failure: fault skončil, systém sa nezotavil

Druhý experiment zastavil payment workerov na päť minút. Po ich obnovení API health a worker readiness zezeleneli:

```text
fault removed
→ workers ready
→ experiment označený ako complete
→ backlog sa začal drainovať maximálnou concurrency
→ DB pool sa saturoval
→ CreateOrder latency vzrástla
→ staré jobs prekročili business expiry
→ používatelia dostali neskoré alebo chybné confirmations
```

### Root cause

Experiment oracle končil pri návrate procesov. Nemeral controlled backlog drain, expired-work policy, reconciliation ani recovery deadline.

### Náprava

- recovery phase má samostatný state a metrics;
- worker concurrency sa po obnove rampuje;
- expired jobs majú explicitnú cancel/reconcile semantiku;
- oldest-message age a terminal-state completeness sú blocking criteria;
- experiment končí až po stabilnom baseline window;
- recovery behavior sa pridá do capacity a operational acceptance testov.

## 17. Experiment v stagingu verzus produkcii

Staging je vhodný na:

- overenie fault mechanismu a tooling-u;
- safety state machine;
- runbook rehearsal;
- známe topology a dependency failures;
- vysoký alebo destructive fault bez user impactu.

Produkcia poskytuje unikátnu hodnotu pri:

- reálnom traffic mixe a tenant skew;
- effective identity, quotas a routing;
- emergentnom behavior-e shared dependencies;
- skutočnej on-call a alerting path;
- veľkom dlhodobom state.

Produkčný experiment používa menší blast radius, prísnejšie guardrails a vyššiu maturity. Nie každý risk potrebuje produkčný chaos.

## 18. Game days a sociotechnická resilience

Resilience závisí aj od ľudí a procesov. Game day môže overiť:

```text
fault alebo incident signal
→ alert routing
→ on-call triage
→ diagnosis cez telemetry
→ runbook action
→ communication a escalation
→ containment
→ recovery a handoff
```

Cieľom nie je hodnotiť jednotlivca. Experiment testuje systém práce: permissions, documentation, tool access, ownership, decision authority a communication latency.

## 19. Maturity ladder

Atlas zvyšuje riziko experimentov postupne:

```text
design/tabletop
→ deterministic component fault test
→ isolated environment
→ staging game day
→ internal production tenant
→ small production cohort
→ scheduled recurring experiment
```

Každý stupeň potrebuje evidence, že tooling, guardrails a recovery z predchádzajúceho stupňa fungujú. Automatizácia nezrelého experimentu iba opakuje nebezpečný zásah rýchlejšie.

## 20. Evidence a report

Experiment report obsahuje:

- hypotézu a rozhodovací význam;
- artifact, config, topology a workload provenance;
- baseline interval;
- target preview a skutočne zasiahnuté resources;
- fault timeline a intensity;
- guardrail a abort events;
- technical, functional a business outcomes;
- recovery timeline;
- invalid/inconclusive limitations;
- root cause a remediation actions;
- regression controls a repeat plan.

Graf bez timeline faultu a rollout/config identity má slabú diagnostickú hodnotu.

## 21. Remediation a experiment closure

Chaos experiment je úspešný ako learning mechanism aj vtedy, keď vyvráti hypotézu. Zlyhá organizačne, ak findings nezmenia systém.

```text
finding
→ owner a impact
→ design/code/config/runbook fix
→ skorší regression control
→ aktualizovaný steady-state alebo abort contract
→ retest konkrétneho failure
→ opakovaný chaos experiment
→ closure s evidence
```

Permanentné „known issue“ bez ownera a termínu mení experiment na opakované meranie známeho rizika.

## 22. Diagnostický postup

Pri chaos failure:

1. Potvrď experiment state, artifact, config, workload a target identity.
2. Over, či fault bol skutočne aplikovaný podľa contractu.
3. Potvrď zdravý baseline a complete observability.
4. Nájdite prvý observation point, kde sa steady state odlíšil.
5. Rozlíš direct fault impact od retry, queue alebo dependency amplification.
6. Skontroluj business correctness, nie iba process availability.
7. Vyhodnoť guardrail a abort behavior.
8. Po fault removal sleduj backlog, reconciliation a delayed side effects.
9. Klasifikuj verdict ako refuted, invalid, inconclusive alebo safety abort.
10. Oprav autoritatívny mechanismus a pridaj skorší regression control.
11. Opakuj experiment až po splnení remediation preconditions.

## 23. Referenčné pravidlá

- Chaos experiment začína konkrétnym failure riskom a hypotézou.
- Steady state vyjadruje používateľský alebo business outcome.
- Fault model obsahuje mode, direction, intensity, duration a correlation.
- Target preview a allowlist chránia scope.
- Blast radius zahŕňa downstream amplification.
- Experiment má explicitnú safety state machine a kill switch.
- Invalid alebo inconclusive run nie je potvrdená resilience.
- Timeout testuje unknown outcome, idempotency a retry budget.
- Process recovery nie je system recovery.
- Backlog drain a reconciliation patria do experimentu.
- Produkčný chaos vyžaduje vyššiu maturity a menší blast radius.
- Finding sa uzatvára až fixom, regression controlom a retestom.

## 24. Časté omyly

### „Chaos testing znamená náhodne vypínať veci“

Náhodný zásah bez hypotézy, oracle a safety contractu neposkytuje dôveryhodný learning.

### „Pods zostali ready, hypotéza prešla“

Business correctness, latency, duplicate side effects alebo recovery môžu byť porušené.

### „Fault tool hlási success“

To dokazuje iba command execution. Treba potvrdiť skutočný target a dopad cez nezávislé observation points.

### „Po odstránení faultu je experiment hotový“

Backlog, retries, stale state a reconciliation môžu pokračovať dlho po fault-e.

### „Staging chaos dokazuje produkčnú resilience“

Iba pre boundaries, ktoré staging zachováva. Traffic, quotas, identity a state môžu byť odlišné.

### „Viac chaosu znamená vyššiu odolnosť“

Bez remediation a regresných controls sa iba opakovane vytvára rovnaký incident.

## Doplnenie výkladu: hypothesis, steady state a fault injection

Chaos testing je riadený experiment nad odolnosťou systému. Nejde o náhodné vypínanie komponentov. Experiment začína **hypotézou**: konkrétnym tvrdením o observable business alebo service outcome-e počas definovaného zlyhania.

Príklad:

```text
Hypotéza:
Ak jedna z troch API replík zanikne,
úspešnosť idempotentných objednávok zostane >= 99.9 %
a p95 completion latency zostane < 800 ms.
```

**Steady state** je merateľný normálny stav pred experimentom. Môže obsahovať success rate, queue depth, reconciliation lag alebo business invariant. Nie je to všeobecná veta „systém je zdravý“. Pred fault injection sa overí, že steady-state podmienky platia; inak experiment nevie odlíšiť existujúci problém od vyvolaného efektu.

**Fault injection** je kontrolovaná mutation, napríklad ukončenie procesu, latency, packet loss, dependency error alebo resource pressure. Fault musí mať exact target identity a trvanie. `kill random pod` bez zaznamenania Pod UID, Node, generation a ownera vytvára slabý experiment.

Experiment flow:

```text
hypotéza a risk
→ exact target a blast radius
→ steady-state baseline
→ observability a abort oracle
→ fault injection
→ system response a user/business outcome
→ fault removal
→ recovery a backlog reconciliation
→ lessons a permanent control
```

Abort condition chráni systém. Napríklad experiment sa zastaví pri error rate > 2 %, queue > 10 000 alebo strate redundantnej druhej AZ. Automation musí mať nezávislú cestu na zastavenie faultu; nemá závisieť iba od systému, ktorý práve poškodzuje.

Príkaz ako:

```bash
kubectl delete pod payments-api-abc123 -n payments
```

preukazuje prijatie delete requestu pre konkrétny object. Nepreukazuje, že Pod naozaj zanikol, že controller vytvoril náhradu alebo že traffic zostal úspešný. Read-back potrebuje Deployment/ReplicaSet/Pod convergence, EndpointSlice a business synthetic result.

Chaos experiment prejde iba vtedy, keď sa potvrdí hypotéza a systém sa po odstránení faultu vráti do akceptovaného stavu. Ak používateľské requests uspeli, ale backlog zostal nekonečne rásť, experiment odhalil latentný failure. Recovery a druhá operácia sú rovnako dôležité ako správanie počas faultu.

## 25. Zhrnutie

Dôveryhodný Atlas chaos experiment je:

```text
failure mode
→ steady-state a recovery hypotéza
→ artifact/topology/workload provenance
→ baseline a safety prechecks
→ scoped realistic fault
→ live technical + business oracle
→ abort/complete/invalid verdict
→ fault removal
→ backlog, reconciliation a recovery proof
→ remediation, skorší control a opakovaný experiment
```

Chaos testing uzatvára sekciu Testing and Software Quality tým, že overuje, či navrhnuté controls fungujú aj pri narušení a či sa výsledok experimentu zmení na trvalý delivery dôkaz. Nasledujúca sekcia CI/CD and Release Engineering tieto evidence contracts umiestni do pipelines, artifact promotionu, rolloutov a recovery rozhodnutí.

## 26. Kontrolné otázky

1. Čím sa chaos experiment líši od bežného failure testu?
2. Prečo steady state nemá byť definovaný iba cez ready instances?
3. Aký tvar má vyvrátiteľná resilience hypotéza?
4. Čo musí obsahovať experiment contract?
5. Ako sa líši invalid, inconclusive a aborted experiment?
6. Prečo je provider brownout nebezpečnejší než okamžitý outage?
7. Ako target preview a blast radius chránia experiment?
8. Prečo lokálne retries vytvorili Atlas amplification?
9. Čo znamená unknown payment outcome?
10. Prečo návrat workerov neznamenal úplnú recovery?
11. Kedy má chaos experiment prejsť do produkcie?
12. Ako sa finding uzatvára cez remediation a skorší regression control?

## Glossary impact

Relevantné pojmy: chaos testing, chaos engineering, resilience experiment, steady-state hypothesis, fault model, fault injection, experiment validity, blast radius, safety state machine, kill switch, brownout, retry amplification, graceful degradation, recovery observation, reconciliation, game day a sociotechnická resilience.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Shift-right](shift-right.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Continuous Integration →](../05-ci-cd-and-release/continuous-integration.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
