# Toil

Toil je operational work priamo súvisiaci s prevádzkou služby, ktorý má tendenciu byť manuálny, opakovaný, automatizovateľný, reaktívny, bez trvalej hodnoty a rastie aspoň lineárne so scale alebo complexity systému. Nie každá nepríjemná úloha je toil a nie každá manuálna úloha má byť okamžite automatizovaná.

SRE cieľom nie je odstrániť ľudí zo všetkých rozhodnutí. Cieľom je odstrániť opakovanú ľudskú prácu tam, kde software, redesign, self-service alebo zmena procesu dokáže vytvoriť bezpečnejší a škálovateľnejší outcome.

```text
demand source a operational trigger
→ exact human workflow a touch points
→ frequency, duration, queueing a risk evidence
→ toil classification
→ root demand alebo failure mechanism
→ eliminate, redesign, automate, delegate alebo accept
→ guarded implementation
→ residual human work a exception path
→ recurrence, load a reliability validation
```

## 1. Exact toil subject

Tvrdenie `máme veľa toil-u` je neakčné. Toil subject musí uviesť:

- service a operational capability;
- trigger alebo demand source;
- actor a skill level;
- exact workflow steps;
- frequency a arrival pattern;
- human touch time;
- elapsed wait time;
- interruption a context-switch cost;
- error a incident risk;
- scale driver;
- current automation;
- ownera;
- measurement window.

Príklad:

```text
service: atlas-settlement-api
workflow: manual outbox backlog recovery
trigger: backlog age > 20 min
actors: primary on-call + database operator
frequency: 11× za 28 dní
median touch time: 38 min
p95 elapsed time: 94 min
scale driver: broker partitions a settlement volume
risk: unsafe SQL, duplicate replay, lost intent
```

Bez workflow identity sa čas z rôznych činností zleje do jedného percenta a tím nevie rozhodnúť, čo treba odstrániť.

## 2. Charakteristiky toil-u

Toil sa nachádza na spektre. Čím viac vlastností práca spĺňa, tým silnejší je kandidát na redukciu.

### Manuálna

Človek musí vykonať konkrétne kroky. Aj manuálne spustenie existujúceho scriptu je stále human touch time.

### Opakovaná

Rovnaký alebo veľmi podobný workflow sa vracia. Prvý novel incident zvyčajne nie je toil; jedenásty incident s rovnakým runbookom pravdepodobne áno.

### Automatizovateľná

Machine môže vykonať rozhodnutie a kroky s rovnakou alebo vyššou bezpečnosťou, prípadne možno potrebu workflowu navrhnúť preč.

### Taktická a reaktívna

Práca vzniká ako interrupt alebo odpoveď na aktuálny stav, nie ako plánované trvalé zlepšenie.

### Bez enduring value

Po dokončení je služba približne v rovnakom structural state-e a rovnaká práca sa pravdepodobne vráti.

### Rastúca so scale

Počet zásahov rastie s trafficom, tenantmi, clusters, releases, resources alebo complexity.

Nie je potrebné, aby workflow spĺňal všetkých šesť vlastností. Classification má byť evidence-based, nie binárny label použitý na odmietnutie práce.

## 3. Toil, engineering, overhead a grungy work

### Toil

Opakované operational udržiavanie current service state-u bez trvalého zlepšenia.

### Engineering work

Vytvára durable capability, znižuje budúci demand, zlepšuje reliability alebo umožňuje sublinear scale. Môže byť technicky nepríjemné a manuálne, ale má enduring value.

### Overhead

Práca nesúvisiaca priamo s prevádzkou konkrétnej služby, napríklad organizačné meetings, hiring administration alebo všeobecný reporting. Overhead môže byť nadmerný, ale nie je automaticky toil.

### Grungy work

Neatraktívna alebo namáhavá práca. Ak jednorazovo odstráni root cause alebo vytvorí trvalé zlepšenie, nie je toil.

Príklad:

```text
každý týždeň ručne opravovať 200 alert routes
→ toil

jednorazovo migrovať alert ownership do versionovaného service catalogu
→ grungy engineering s enduring value
```

## 4. On-call nie je celé toil

On-call shift obsahuje viac typov práce:

- novel incident diagnosis;
- opakované known-issue response;
- urgent decision s neautomatizovateľným judgmentom;
- routine execution runbooku;
- communication a coordination;
- post-incident evidence collection.

Novel diagnosis môže byť engineering learning. Opakované spúšťanie rovnakého recovery scriptu je toil. Samotný label `on-call` preto nestačí; treba klasifikovať konkrétne workflows a touch time.

## 5. Toil demand model

Toil má source. Môže vzniknúť z:

- unreliable service behavior;
- chýbajúcej self-service capability;
- unsafe alebo príliš častej release procedúry;
- manuálnej access approval;
- configuration driftu;
- alert noise;
- neúplného inventory;
- capacity shortage;
- legacy interface;
- policy alebo compliance workflowu;
- nejasného ownershipu;
- product behavioru, ktorý presúva prácu na operations.

```text
system alebo process condition
→ operational demand
→ queue alebo interrupt
→ human decision/action
→ temporary state restoration
→ condition zostáva
→ ďalší demand
```

Automatizácia posledného human kroku nemusí odstrániť demand. Môže iba zrýchliť nebezpečný loop.

## 6. Meranie toil-u

Užitočný inventory kombinuje viac dimensions:

- počet occurrences;
- human touch time;
- elapsed lead time;
- počet interruptions;
- number of actors;
- required privilege;
- error rate;
- incident contribution;
- after-hours podiel;
- growth rate;
- opportunity cost;
- customer wait time.

Príklad:

| Workflow | Occurrences / 28 dní | Touch time | Total human time | Risk |
|---|---:|---:|---:|---|
| Outbox backlog recovery | 11 | 38 min | 418 min | lost/duplicate settlement |
| Merchant certificate renewal | 7 | 22 min | 154 min | authentication outage |
| False-positive queue alert triage | 64 | 6 min | 384 min | alert fatigue |

Samotné percento času môže skryť critical workflow s nízkou frekvenciou a vysokým blast radiusom. Toil prioritization preto potrebuje volume aj risk.

## 7. Toil budget

Niektoré tímy používajú upper bound na podiel času venovaného operational worku alebo toil-u. Google SRE opisuje 50 % limit operational práce ako vlastný organizačný model; nie je to univerzálna norma pre každý tím.

Lokálny toil budget má definovať:

- čo sa meria;
- za aké obdobie;
- či zahŕňa on-call, tickets a releases;
- team-level a individual distribution;
- výnimky počas major incidentov;
- action pri prekročení;
- ochranu engineering capacity.

Cieľ nie je optimalizovať timesheet. Cieľ je zabrániť reinforcing loopu:

```text
viac incidents a manual work
→ menej engineering času
→ menej root-cause fixes
→ ešte viac incidents a manual work
```

## 8. Prioritization

Najvyššiu prioritu nemá vždy workflow s najväčším počtom hodín. Praktický model hodnotí:

```text
annualized human cost
+ interruption cost
+ reliability/security risk
+ customer wait
+ growth rate
+ tractability
- implementation a maintenance cost
```

Silní kandidáti:

- vysoká frekvencia a jasný deterministic workflow;
- vysoký privilege alebo destructive risk;
- lineárny rast s trafficom;
- častý after-hours interrupt;
- workflow, ktorý spotrebúva error budget;
- runbook pripomínajúci pseudocode;
- opakovaná customer request vhodná pre self-service.

## 9. Elimination strategies

### Engineer demand preč

Oprav root cause tak, aby workflow nevznikal. Toto je často najlepšie riešenie.

### Redesign service contract

Zaveď backpressure, idempotency, bounded queue, safer state machine alebo immutable operation.

### Full automation

Software detectuje condition, rozhodne a vykoná action bez human touch, s guardrails a evidence.

### Partial automation

Software pripraví evidence, plan alebo candidate action; človek schváli iba risk-relevantný krok.

### Self-service

Consumer vykoná bezpečne scoped operation bez ticketu a privileged operatora.

### Standardization

Zníženie heterogenity umožní jeden tooling path namiesto množstva special cases.

### Delegation alebo process change

Niektoré work nie je technicky potrebné vykonávať centralizovaným SRE tímom. Presun musí zachovať capability, safety a ownership.

### Explicit acceptance

Ak reduction cost prevyšuje benefit, toil možno časovo prijať s ownerom, budgetom a review triggerom.

## 10. Automation risk

Automation zväčšuje execution speed aj blast radius. Pred automatizáciou treba modelovať:

- input authority a freshness;
- preconditions;
- idempotency;
- maximum scope;
- rate limits;
- concurrency;
- dry-run alebo plan;
- approval boundary;
- partial failure;
- unknown outcome;
- rollback alebo compensation;
- audit;
- kill switch;
- forbidden actions.

```text
manual unsafe workflow
→ fully automatic unsafe workflow
```

nie je toil elimination. Je to rýchlejší incident mechanismus.

## 11. Runbook ako automation candidate

Detailný runbook môže byť executable design input:

```text
trigger
→ required evidence
→ branch conditions
→ actions
→ validation
→ escalation
```

Pred prepisom do code treba odstrániť nejasné pokyny ako:

- `ak to vyzerá zle`;
- `vyber staré rows`;
- `reštartuj podľa potreby`;
- `skontroluj, či je všetko OK`.

Tieto vety skrývajú chýbajúci contract. Automatizácia potrebuje explicitné thresholds, identities a outcome oracles.

## 12. Connected failure `SRE-PAY-52`

Outbox backlog recovery bola opakovaná toil cesta:

```text
page
→ on-call otvorí dashboard a SQL console
→ identifikuje rows staršie než 30 minút
→ manuálne scale-ne workers
→ spustí cleanup SQL
→ reštartuje publisher
→ sleduje queue
→ ručne odpovedá merchant supportu
```

Za predchádzajúcich 28 dní sa workflow vykonal `11×`. Median touch time bol `38 minút`, spolu `418 minút` privileged human worku. Runbook neodstraňoval broker partition, backlog contract ani unsafe retention. Každé vykonanie vrátilo systém do dočasne použiteľného stavu a pripravilo podmienky na ďalšie opakovanie.

Dňa 29. júla cleanup odstránil `4 182` nepublikovaných commands. Toil teda nebol iba productivity cost. Bol causal amplifier reliability a durability incidentu.

## 13. Root demand a redesign

Nový design odstránil manual cleanup ako normal operation:

```text
broker publish latency rastie
→ publisher backlog-age SLI a queue watermark
→ API postupne znižuje admission alebo vracia explicitný retryable response
→ unpublished rows nikdy nepodliehajú time-only deletion
→ retention vyžaduje published/terminal state
→ autoscaling používa bounded queue signal
→ reconciler porovnáva payment, outbox, broker a provider ledger
→ operator zasahuje iba pri novel alebo forbidden state
```

Self-service recovery tool umožňuje vybrať exact intent IDs, vytvoriť dry-run classification a vykonať idempotentný replay iba po policy decisione. Neumožňuje broad age-based delete.

## 14. Human-in-the-loop boundary

Niektoré rozhodnutia zostali ľudské:

- schválenie replayu `sent-unknown` cohortu s finančným impactom;
- výber business compensation pre poškodeného merchanta;
- rozhodnutie o degraded mode počas provider incidentu;
- incident command a external communication.

Automation pripraví evidence a bounded options. Človek zostáva pri neautomatizovateľnom risk judgment-e, nie pri kopírovaní IDs a spúšťaní rovnakých SQL commands.

## 15. Toil reduction acceptance verdict

Reduction je prijatá, keď:

- pôvodný workflow, trigger, volume a touch time sú zmerané;
- root demand je pomenovaný;
- nový mechanismus znižuje occurrences alebo human touch;
- allowed operation zostáva dostupná;
- automation má bounded scope, idempotency a audit;
- partial failure a unknown outcome majú recovery;
- privileged destructive path bol odstránený alebo výrazne zúžený;
- residual exceptions majú runbook a ownera;
- reliability, security a customer wait sa nezhoršili;
- toil sa nepresunul na iný tím alebo usera bez merania;
- druhý broker incident nevyžaduje pôvodný manual workflow;
- 28-day follow-up potvrdí trvalé zníženie demandu.

## 16. Troubleshooting reduction failure

```text
očakávaný toil reduction sa neprejavil
→ exact workflow a measurement window
→ demand arrival rate
→ automation adoption a eligibility
→ manual fallback reasons
→ exception cohorts
→ automation errors/unknown outcomes
→ hidden downstream work
→ shifted toil na iný tím
→ reliability a user impact
→ redesign alebo policy correction
```

Ak počet tickets klesol, ale consumers teraz opakovane skúšajú broken self-service flow, toil sa iba skryl z team queue.

## 17. Earlier controls

- toil taxonomy a workflow IDs;
- periodic time sampling;
- on-call interrupt classification;
- runbook occurrence counters;
- privileged-operation audit;
- error-budget consumer mapping;
- quarterly toil review;
- protected engineering capacity;
- self-service product ownership;
- automation threat model;
- toil-reduction success metrics;
- deprecation date manuálneho pathu.

## 18. Anti-patterny

### Všetko manuálne je toil

Novel investigation a risk judgment môžu mať enduring value.

### Automatizuj existujúce kroky bez redesignu

Chybný workflow sa vykoná rýchlejšie a vo väčšom scope-e.

### Počet tickets je jediná metric

Skryje interrupts, chat requests, user retries a prácu presunutú inde.

### SRE tím absorbuje všetky operations

Chýbajúci product ownership a self-service sa normalizujú ako permanentná queue.

### Toil hero

Jedna osoba je odmeňovaná za rýchle opakované zásahy namiesto odstránenia demandu a zdieľania knowledge.

### 50 % ako univerzálny zákon

Organizačný model sa kopíruje bez definície, čo sa meria a aké sú lokálne constraints.

### Automation bez ownera

Script sa stane novým legacy service-om, ktorý vytvára ďalší toil.

## 19. Kontrolné otázky

1. Čo je toil a ktoré vlastnosti ho charakterizujú?
2. Ako sa toil líši od overheadu a grungy engineering worku?
3. Prečo celý on-call shift nie je automaticky toil?
4. Čo tvorí exact toil subject?
5. Ako merať volume, touch time a risk?
6. Čo je toil reinforcing loop?
7. Kedy je lepší redesign než automation?
8. Aké guardrails potrebuje toil automation?
9. Prečo runbook obsahuje skrytý decision contract?
10. Ako odhaliť toil presunutý na iný tím alebo usera?
11. Ako manual cleanup amplifikoval `SRE-PAY-52`?
12. Čo musí overiť toil-reduction acceptance verdict?

## Glossary impact

Relevantné pojmy: toil subject, toil characteristic, operational demand, human touch time, interruption cost, toil budget, toil reinforcing loop, root-demand elimination, toil automation, self-service reduction, residual toil, toil shift, engineering capacity a toil-reduction acceptance verdict.

## Primárne zdroje

- [Google SRE — Eliminating Toil](https://sre.google/sre-book/eliminating-toil/)
- [Google SRE Workbook — Eliminating Toil](https://sre.google/workbook/eliminating-toil/)
- [Google SRE — Introduction](https://sre.google/sre-book/introduction/)
- [Google SRE Workbook — How SRE Relates to DevOps](https://sre.google/workbook/how-sre-relates/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Error budgets](error-budgets.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
