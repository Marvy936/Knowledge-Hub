# Incident management

Incident management je koordinovaný proces na obmedzenie user a business impactu, obnovenie bezpečnej služby a zachovanie dostatočných dôkazov na následné učenie. Nie je to synonymum pre debugging ani chat, v ktorom veľa ľudí súčasne skúša zmeny.

Incident začína vtedy, keď observed alebo pravdepodobný impact prekročí bežný operational workflow a vyžaduje explicitnú koordináciu, prioritizáciu a bounded authority.

## 1. Dominantný lifecycle

```text
signal alebo user report
→ exact incident subject a declaration criteria
→ severity, scope a impact hypothesis
→ command roles a communication channels
→ evidence-preserving stabilization
→ competing hypotheses a bounded mitigations
→ effective-state a business recovery verification
→ handoff a recurrence watch
→ incident closure
→ post-incident learning a action ownership
```

Incident je uzavretý až po obnovení pôvodného business outcome-u, stabilizácii relevantných cohorts a zachytení follow-up práce. Zelený dashboard alebo pokles error rate-u nestačí.

## 2. Exact incident subject

Incident subject má obsahovať:

```text
business capability a affected user outcome
+ start/detection/declaration times
+ tenant/Region/cohort
+ release/configuration/topology generations
+ affected operations a data
+ SLO/error-budget impact
+ suspected control/data/dependency paths
+ active mitigations
+ current authority a role ownership
```

Príklad:

```text
incident: SRE-PAY-53
capability: settlement completion
Region: prod-eu1
affected cohort: end-of-month campaign merchants
start: 10:02 UTC
detected: 10:07 UTC
declared: 10:31 UTC
impact: completion latency > 10 min, rising backlog
release: settlement-api 8.1.0
capacity generation: CAP-PAY-53-A
```

Bez presného subjectu môžu tímy riešiť odlišné incidents pod jedným názvom alebo aplikovať mitigation na nesprávny cohort.

## 3. Incident declaration

Vyhlásenie incidentu je control transition, nie administratívna formalita.

Typické declaration triggers:

- critical user journey porušuje alebo pravdepodobne poruší SLO;
- error budget sa spaľuje nad definovanou rýchlosťou;
- impact rastie rýchlejšie než normal troubleshooting dokáže reagovať;
- viac tímov alebo failure domains potrebuje koordináciu;
- existuje data integrity, security alebo safety risk;
- diagnosis je neistá, no containment má deadline;
- public alebo contractual communication je potrebná;
- bežný owner alebo runbook nemá dostatočnú authority.

Deklarovať neskoro znamená ponechať coordination problem v neformálnom režime.

## 4. Severity

Severity vyjadruje impact a požadovanú response urgency. Nemá byť odvodená iba od počtu errors.

Zohľadni:

- criticality business capability;
- affected users, tenants a Regions;
- data loss alebo incorrect side effects;
- duration a growth rate;
- workaround availability;
- contractual, security alebo regulatory impact;
- recovery complexity;
- blast-radius uncertainty.

Príklad lokálneho modelu:

| Severity | Charakteristika | Response |
|---|---|---|
| SEV-1 | rozsiahly critical outage, data integrity alebo nekontrolovaný rast impactu | okamžitá command štruktúra a executive/customer communication |
| SEV-2 | významná degradácia critical journey alebo ohraničený high-impact cohort | okamžitý technical response a pravidelné updates |
| SEV-3 | obmedzený impact s workaroundom a stabilným scope-om | owned urgent remediation |
| SEV-4 | nízky impact alebo operational defect bez urgentného user rizika | normal queue |

Tabuľka je organizačný contract, nie univerzálny štandard.

## 5. Command roles

Počas komplexného incidentu treba oddeliť koordináciu od vykonávania.

### Incident Commander — IC

- drží incident objective a priority;
- prideľuje roles a owners;
- schvaľuje alebo zastavuje riskantné mitigations;
- udržiava shared state a decision cadence;
- rozhoduje o escalation, handoff a closure.

IC nemusí byť najhlbší subject-matter expert.

### Operations lead

- koordinuje technickú diagnostiku a zmeny;
- udržiava hypothesis/action/evidence chain;
- zaisťuje, že súčasné zásahy nekolidujú;
- reportuje effective outcome IC.

### Communications lead

- publikuje interné a externé updates;
- oddeľuje confirmed facts od hypotheses;
- udržiava stakeholder cadence;
- chráni responders pred opakovanými status otázkami.

### Planning alebo logistics lead

- sleduje follow-up úlohy, handoff a staffing;
- rieši access, vendor support a dlhší recovery horizon;
- zaznamenáva divergence od normal state-u.

Pri menšom incidente môže jedna osoba držať viac roles. Responsibilities však musia zostať explicitné.

## 6. Incident state document

Jeden authoritative state document alebo channel má obsahovať:

```text
incident ID, severity a commander
current user/business impact
scope a exclusions
known timeline
active hypotheses
recent evidence
current mitigations a owners
forbidden alebo paused changes
next decision checkpoint
communication status
recovery a closure criteria
```

Chat history nie je spoľahlivý incident state. Dôležité decisions musia byť stručne materializované.

## 7. Stabilization pred root cause

Počas impactu je priorita:

```text
zastaviť rast blast radiusu
→ zachovať kritické dôkazy
→ obnoviť bezpečný bounded service outcome
→ až potom optimalizovať alebo kompletne vysvetliť root cause
```

Príklady stabilization:

- zastaviť rollout;
- obmedziť admission;
- izolovať affected cohort;
- vypnúť noncritical feature;
- znížiť retry amplification;
- failover na known-good path;
- zablokovať destructive automation;
- chrániť data a audit evidence;
- aktivovať degraded mode.

Mitigation nie je automaticky remediation. Môže iba znížiť impact.

## 8. Hypothesis-driven response

Každá technická akcia má mať:

```text
hypothesis
+ observation, ktorá ju podporuje
+ bounded action
+ očakávaný signal
+ abort criterion
+ rollback alebo compensation
+ owner a timestamp
```

Príklad:

```text
hypothesis: provider retries saturujú DB pool
observation: retry multiplier 4.6×, DB acquire p99 1.4 s
action: znížiť provider concurrency a vypnúť immediate retries
expected: DB acquire p99 < 200 ms, queue drain rate rastie
abort: completion rate klesne pod 1 500/s
owner: Ops-2
```

„Skúsme pridať workery“ bez hypothesis a expected observation je nekoordinačná zmena.

## 9. Change control počas incidentu

Incident neznamená nulové change governance. Znamená rýchlejší, explicitný a auditovateľný contract.

Každá zmena potrebuje:

- exact subject a scope;
- initiator a approver podľa severity;
- current generation;
- expected effect;
- rollback/compensation;
- observation window;
- recorded result.

Parallel untracked changes ničia causal evidence a môžu vytvoriť oscillation.

## 10. Communication

Dobrý update odpovedá:

```text
čo je potvrdené
čo je impact
čo robíme teraz
aké riziká zostávajú
kedy bude ďalší update
```

Externý update nesmie prezentovať hypothesis ako root cause. Interný technický detail má zostať dostatočný na coordinated action, nie zahltiť všetkých raw telemetry.

Communication cadence má byť predvídateľná a oddelená od technického response loopu.

## 11. Recovery criteria

Recovery nie je iba návrat jednej metric pod threshold.

Pre settlement incident:

- new unique intents majú accepted alebo explicitne rejected outcome;
- completion latency je v SLO;
- queue age klesá a drain rate je stabilná;
- DB/provider saturation sú v guardraile;
- duplicate alebo lost settlements nevznikajú;
- affected historical cohort je reconciled;
- temporary overrides sú inventoried;
- on-call a support channels už nevidia rast impactu;
- second operation a adjacent cohort prejdú.

Ak backlog ešte rastie, incident nie je recovered len preto, že API error rate klesla.

## 12. Worked incident `SRE-PAY-53`

O `10:07 UTC` page `SettlementCompletionFastBurn` upozornila na rastúci completion burn rate. Primary on-call však incident nevyhlásil. Predpokladal bežný provider transient a pokračoval v normal troubleshooting.

Nasledujúcich 24 minút:

1. application engineer zvýšil worker replicas zo 120 na 240;
2. database engineer zvýšil connection pool limit;
3. support lead požiadal o replay starších settlements;
4. provider owner zmenil retry interval;
5. nikto nedržal shared incident state ani approved action sequence.

Výsledok:

- DB connection pressure vzrástol;
- retries sa zosilnili;
- queue age pokračovala v raste;
- dve mitigations si navzájom menili observation;
- support komunikoval, že problém je „takmer vyriešený“, hoci completion SLO sa zhoršovalo.

Incident bol formálne vyhlásený o `10:31 UTC` ako `SEV-1` po prekročení 15-minútovej queue age a potvrdení viacerých merchant impacts.

Trigger zostal traffic spike a provider slowdown. Primary capacity root cause je opísaný v predchádzajúcej kapitole.

Incident-management failure bol **oneskorený declaration a chýbajúca command štruktúra, ktorá dovolila nekorelované parallel mitigations počas rastúceho impactu**.

## 13. Stabilization a recovery

Po declaration:

```text
IC assigned
→ change freeze mimo approved incident actions
→ Ops, Comms a Planning roles
→ admission limit 1 700 unique intents/s
→ immediate retries disabled
→ worker concurrency bounded podľa DB/provider
→ noncritical batch traffic paused
→ provider escalation
→ queue cohort inventory
→ controlled drain a reconciliation
```

Do 18 minút sa DB acquire p99 vrátilo pod `180 ms`. Queue age prestala rásť o `10:54 UTC`; do SLO sa vrátila o `11:42 UTC`. Historical affected cohort bol reconciled samostatne a incident zostal otvorený, kým second-peak test nepotvrdil stabilitu.

## 14. Handoff

Pri dlhom incidente handoff musí obsahovať:

- current incident subject a severity;
- effective state a unresolved risks;
- executed actions a outcomes;
- active hypotheses;
- temporary overrides;
- upcoming thresholds a decision times;
- stakeholder commitments;
- explicit transfer of IC a operational roles.

Nový responder nesmie rekonštruovať incident iba z tisícov chat messages.

## 15. Closure

Incident možno uzavrieť, keď:

- impact je odstránený alebo explicitne akceptovaný;
- recovery criteria prešli;
- temporary mitigations majú ownera a expiry;
- evidence a timeline sú zachované;
- affected data/business state je reconciled;
- support a customer communication je uzavretá;
- post-incident review má ownera a termín;
- urgent corrective actions sú filed a prioritized;
- recurrence watch prešiel definovaným intervalom.

Closure nie je deklarácia, že všetka remediation je hotová.

## 16. Incident-management acceptance verdict

Response je prijatá, keď:

- declaration criteria a severity boli správne použité;
- incident subject a impact boli explicitné;
- IC, Ops, Comms a Planning responsibilities boli jasné;
- state document zachytával current truth;
- evidence bola zachovaná pred destructive changes;
- mitigations mali hypothesis, scope, owner a abort criterion;
- parallel changes boli koordinované;
- original business outcome bol obnovený;
- forbidden outcomes, napríklad duplicate settlement, boli overené;
- adjacent cohort a second operation prešli;
- handoff zachoval command continuity;
- follow-up actions majú ownera, priority a closure evidence.

## 17. Troubleshooting response failure

```text
impact pokračuje napriek aktivite
→ bol incident deklarovaný?
→ kto je IC a aký je objective?
→ aký je current incident subject/scope?
→ existuje authoritative state document?
→ ktoré changes sú aktívne a kto ich vlastní?
→ aké hypotheses a expected observations existujú?
→ ktoré mitigations kolidujú?
→ je impact metric user-centered?
→ čo je containment a čo remediation?
→ aké recovery criteria ešte neprešli?
```

Veľa responders a veľa commands neznamená effective response.

## 18. Earlier controls

- explicitné declaration a severity criteria;
- incident roles a backups;
- static alebo dependency-independent coordination channel;
- incident state template;
- change/action log;
- user-centered impact dashboards;
- evidence preservation checklist;
- communication templates;
- vendor escalation contracts;
- regular incident drills;
- handoff checklist;
- closure a recurrence criteria.

## 19. Anti-patterny

### Najseniornejší engineer je automaticky IC

Deep technical expert potom nemôže súčasne koordinovať celý response.

### Najprv nájdime root cause

Impact rastie, kým tím čaká na kompletné vysvetlenie.

### Všetci skúšajú zmeny

Parallel actions zničia causal evidence a môžu sa navzájom zosilniť.

### Chat je incident state

Critical decisions sa stratia a handoff zlyhá.

### Zelený endpoint znamená recovered

Historical backlog, incorrect outcomes alebo data damage môžu pokračovať.

### Incident končí po mitigation

Temporary override sa stane permanentným hidden riskom.

## 20. Kontrolné otázky

1. Čo tvorí exact incident subject?
2. Kedy normal troubleshooting musí prejsť na incident režim?
3. Ako severity súvisí s impactom a urgency?
4. Aké responsibilities majú IC, Ops, Comms a Planning?
5. Prečo IC nemusí byť najhlbší expert?
6. Čo obsahuje incident state document?
7. Ako stabilization súvisí s root-cause analysis?
8. Čo potrebuje bounded incident change?
9. Prečo parallel mitigations poškodili `SRE-PAY-53`?
10. Čo musí obsahovať handoff?
11. Ako sa recovery criteria líšia od jednej green metric?
12. Čo musí overiť incident-management acceptance verdict?

## Glossary impact

Relevantné pojmy: incident subject, incident declaration, severity contract, Incident Commander, Operations lead, Communications lead, Planning lead, incident state document, stabilization, bounded incident change, recovery criteria, command continuity, incident closure a incident-management acceptance verdict.

## Primárne zdroje

- [Google SRE — Managing Incidents](https://sre.google/sre-book/managing-incidents/)
- [Google SRE Workbook — Incident Response](https://sre.google/workbook/incident-response/)
- [Google SRE — Emergency Response](https://sre.google/sre-book/emergency-response/)
- [NIST SP 800-61 Revision 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Capacity planning](capacity-planning.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: On-call a escalation →](on-call-and-escalation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
