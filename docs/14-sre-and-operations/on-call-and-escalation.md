# On-call a escalation

On-call je časovo ohraničená zodpovednosť reagovať na urgentné production udalosti s primeranou rýchlosťou, kompetenciou a authority. Nie je to neobmedzená dostupnosť každého engineera ani mechanizmus na absorbovanie všetkej neplánovanej práce.

Escalation je riadený prechod k ďalšej osobe, role, tímu alebo authority, keď current responder nemá čas, informácie, access, kapacitu alebo rozhodovacie oprávnenie potrebné na ochranu služby.

## 1. Dominantný lifecycle

```text
service support objective
→ exact on-call support contract
→ page eligibility a routing
→ rotation, coverage a competency
→ schedule generation a handoff
→ notification delivery a acknowledgement
→ first response a impact assessment
→ technical/organizational escalation
→ incident declaration a coordinated response
→ recovery a follow-up ownership
→ load, fatigue a page-quality review
→ sustainable rotation validation
```

On-call systém je prijateľný až keď správny urgentný signal dostane pripravený responder, ktorý vie bezpečne konať alebo rýchlo eskalovať, a keď dlhodobý load nepoškodzuje ľudí ani reliability.

## 2. Exact on-call support contract

Support contract musí pomenovať:

```text
supported service a business capability
+ hours/time zones a coverage model
+ page eligibility a urgency
+ primary/secondary/escalation roles
+ response a acknowledgement targets
+ required skills, tools a access
+ incident-declaration authority
+ vendor a cross-team dependencies
+ handoff a follow-up rules
+ load a sustainability limits
```

Príklad:

```text
service: Atlas settlement completion
coverage: 24/7
primary: immediate triage a containment
secondary: parallel diagnosis, handoff alebo primary replacement
service owner: architecture a risk authority
provider escalation: P1 channel do 10 min pri provider-wide impacte
security escalation: okamžite pri integrity/credential suspicion
```

Bez support contractu sa „zavolaj niekomu“ stane implicitnou sociálnou závislosťou.

## 3. Page eligibility

Page má prerušiť človeka iba keď je signal:

- urgentný;
- relevantný pre podporovanú službu;
- dostatočne spoľahlivý;
- actionable pre receiving role;
- viazaný na user/business impact alebo imminent risk;
- časovo citlivý tak, že čakanie na normal queue zvyšuje škodu.

Dobrý page contract obsahuje:

```text
čo je impact alebo risk
→ exact service/cohort/Region
→ current signal a threshold
→ prečo je urgentný
→ safe first observation alebo action
→ čo nerobiť
→ runbook/playbook
→ escalation path
```

Informational alert, dlhodobý capacity trend alebo známy low-impact defect typicky patrí do ticketu, nie do nočného page-u.

## 4. Notification delivery nie je response

Treba oddeliť:

```text
alert fired
→ routing decision
→ provider delivery attempt
→ device/channel delivery
→ human acknowledgement
→ responder prevzal ownership
→ impact assessed
→ action alebo escalation začala
```

`Acknowledged` môže znamenať iba kliknutie. Nepotvrdzuje správny scope, competency, access ani začiatok mitigation.

Meraj samostatne:

- time to page creation;
- routing latency;
- delivery success;
- acknowledgement time;
- time to qualified response;
- time to incident declaration;
- time to effective mitigation;
- escalation latency.

## 5. Rotation design

Rotation má zabezpečiť coverage bez vytvorenia chronickej únavy alebo key-person dependency.

Zohľadni:

- počet ľudí a časových pásiem;
- primary/secondary model;
- shift length a frequency;
- nočné a víkendové zaťaženie;
- holiday coverage;
- skill distribution;
- new-hire shadowing;
- handoff overlap;
- planned leave a illness;
- recovery time po náročnom incidente;
- lokálne pracovné a compensation pravidlá.

Konkrétny počet ľudí alebo maximálny počet pages je organizačný design parameter, nie univerzálny zákon. Malá rotation však nemôže dlhodobo poskytovať kvalitné 24/7 coverage bez trade-offu v health, project work alebo response quality.

## 6. Primary, secondary a specialist roles

### Primary on-call

- prijíma prvý page;
- potvrdí subject a impact;
- vykoná safe first response;
- deklaruje incident alebo eskaluje;
- udržiava ownership, kým ho explicitne neodovzdá.

### Secondary on-call

- prevezme ďalšie alerts alebo tickets;
- poskytne paralelnú diagnostiku;
- nahradí primary pri nedostupnosti alebo overload-e;
- môže prevziať IC alebo Operations rolu;
- chráni primary pred multitaskingom.

### Specialist alebo service owner

- poskytuje deep component knowledge;
- schvaľuje high-risk domain decisions;
- rieši architecture, vendor alebo data-recovery hranice;
- nemá byť neformálne jedinou osobou, ktorá systém dokáže obnoviť.

## 7. Handoff

Shift handoff má byť explicitný state transition.

Obsah:

```text
active incidents a severity
open pages/tickets a deadlines
current service health a risk
temporary overrides
recent changes a rollouts
capacity alebo provider constraints
pending customer/vendor commitments
next expected events
who owns each follow-up
```

Handoff `nič zvláštne` bez prečítania active incidents a change calendaru nie je dôkazom continuity.

## 8. Escalation dimensions

Escalation nie je iba časovač po neacknowledged page-i.

### Time escalation

Responder sa neozval alebo nezačal qualified response v contract time.

### Skill escalation

Incident prekračuje responderove knowledge alebo diagnostic confidence.

### Authority escalation

Potrebné rozhodnutie má business, security, financial alebo destructive impact mimo current role.

### Capacity escalation

Responder má priveľa simultánnych incidents alebo tasks.

### Severity escalation

Impact alebo uncertainty sa zväčšili a vyžadujú incident command, communication alebo leadership support.

### Dependency escalation

Root alebo mitigation boundary leží v inom tíme, vendorovi alebo providerovi.

### Safety escalation

Existuje data integrity, security, legal alebo human safety risk.

Page acknowledgement nesmie zrušiť escalation, keď sa impact neznižuje.

## 9. Access a readiness

On-call responder musí mať pred shiftom overené:

- identity a MFA;
- JIT alebo break-glass process;
- read access k production telemetry a auditom;
- bounded remediation permissions;
- incident communication channels;
- vendor support contacts;
- current runbooks a dashboards;
- workstation a network readiness;
- ability deklarovať incident.

Access sa nemá prvýkrát testovať počas SEV-1.

## 10. Page quality

Page quality metrics:

- actionable rate;
- false-positive rate;
- duplicate rate;
- pages per shift a per incident;
- pages mimo pracovných hodín;
- percentage pages s relevantným runbookom;
- percentage pages vedúcich k incident declaration;
- time to qualified response;
- repeated page families;
- pages spôsobené monitoring failure-om;
- page-to-ticket downgrade rate.

Page count bez severity, duration a cognitive complexity je neúplný.

## 11. On-call health a sustainability

Chronický on-call overload vedie k:

```text
sleep disruption a context switching
→ pomalšia diagnóza
→ risky shortcuts
→ viac incidentov a pages
→ menej engineering času
→ menej reliability improvement
→ ďalší overload
```

Sleduj:

- nočné prerušenia a recovery time;
- simultánne incidents;
- shift swap a absence patterns;
- self-reported fatigue;
- post-incident rest;
- project-work displacement;
- attrition a rotation participation;
- knowledge concentration;
- psychological safety pri escalation.

Responder nemá byť penalizovaný za skorú pomoc alebo incident declaration.

## 12. Worked incident `SRE-PAY-53`

Settlement rotation mala štyroch engineers a poskytovala 24/7 coverage. Počas šiestich hodín pred campaign peakom primary prijal 11 pages:

```text
6 duplicate alebo symptom alerts
3 nonurgent capacity warnings
1 provider heartbeat false positive
1 SettlementCompletionFastBurn page
```

O `10:07 UTC` critical burn-rate page dorazila primary responderovi. Ten ju acknowledged o dve minúty, preto notification platforma zastavila no-ack escalation.

Skutočný stav:

- primary riešil súčasne dva support requests a predchádzajúci broker alert;
- capacity warning pages nemali jasný distinction ticket vs page;
- secondary schedule override skončil o hodinu skôr pre timezone configuration drift;
- provider P1 contact nebol v current runbooku;
- escalation policy reagovala iba na absence acknowledgementu, nie na absence mitigation alebo rast severity;
- responder predpokladal transient a nevyhlásil incident.

On-call root failure bol **support contract, ktorý zamieňal acknowledgement za qualified ownership a nemal load-, severity- ani progress-based escalation**.

Causal amplifiers:

- malá rotation a vysoký duplicate page load;
- stale secondary schedule;
- chýbajúci pre-shift access/contact check;
- kultúrny pressure „najprv vyrieš, potom deklaruj“;
- runbook bez explicitného incident triggeru.

Capacity defect bol technický root incidentu; on-call design predĺžil detection-to-command interval.

## 13. Containment on-call failure-u

Po declaration IC vykonal:

1. aktiváciu backup secondary mimo stale schedule;
2. presun support tickets na nonincident ownera;
3. grouping/silence duplicate symptom alerts pod incident ID;
4. explicitné provider a DB specialist escalation;
5. handoff primary z IC/coordination práce na bounded technical task;
6. pravidelný welfare a fatigue check;
7. zabezpečenie replacement coverage pre nasledujúci shift.

Silence bola scoped podľa incidentu, service a time windowu. Nebola globálnym vypnutím monitoringu.

## 14. Authoritative redesign

Nový on-call contract `OC-PAY-54` zaviedol:

```text
user-impact page eligibility
→ primary + active secondary coverage
→ acknowledgement + qualified-response timers
→ severity/progress escalation
→ direct incident-declaration authority
→ verified provider/security/data paths
→ shift handoff artifact
→ page-quality review a follow-up ownership
```

Konkrétne:

- capacity trend alerts prešli na ticket/report;
- duplicate symptom alerts sa groupujú podľa incident subjectu;
- critical burn-rate page eskaluje pri absent mitigation progress aj po acknowledgement;
- schedule a timezone sa validujú canary notificationou;
- pre-shift checklist testuje access a contacts;
- po náročnom SEV-1 nasleduje replacement a recovery interval;
- repeated pages automaticky vytvoria reliability/toil review item.

## 15. On-call acceptance verdict

On-call model je prijatý, keď:

- support scope, hours a severity sú explicitné;
- page eligibility je user-impacting, urgentná a actionable;
- schedule má primary, secondary a tested escalation;
- notification delivery a qualified response sú oddelené;
- responder má skills, access a current documentation;
- acknowledgement nezastaví severity/progress escalation;
- handoff zachová active state a commitments;
- duplicate a nonurgent alerts nezahlcujú rotation;
- incident declaration je psychologicky a procedurálne bezpečná;
- load a fatigue sú merané a vedú k redesignu;
- second shift a schedule-failure canary prejdú;
- original page vytvorí správny response bez hidden key person dependency.

## 16. Troubleshooting on-call failure

```text
page existoval, response bol pomalý
→ alert fired a routing decision
→ schedule generation/timezone/override
→ delivery channel/device
→ acknowledgement vs qualified response
→ responder load a concurrent work
→ access a documentation readiness
→ escalation timer a conditions
→ incident-declaration authority/culture
→ handoff a secondary availability
→ effective mitigation time
```

`Ack in 2 min` nie je dobrý outcome, ak incident command vznikne o 24 minút neskôr.

## 17. Earlier controls

- service support contract;
- page eligibility review;
- primary/secondary coverage;
- schedule a timezone canary;
- pre-shift access checklist;
- severity/progress escalation;
- runbook freshness;
- incident declaration training;
- page grouping a deduplication;
- shift handoff template;
- on-call load dashboard;
- post-incident recovery policy.

## 18. Anti-patterny

### Každý alert je page

Nonurgent alebo nonactionable signals poškodzujú attention pre critical incidents.

### Acknowledged znamená handled

Human kliknutie nepotvrdzuje diagnosis, authority ani mitigation.

### Primary musí všetko vyriešiť sám

Oddiali escalation a vytvára key-person risk.

### Heroická rotation

Malý tím dlhodobo absorbuje 24/7 load bez engineering capacity a health controls.

### Escalation je zlyhanie jednotlivca

Responder sa bojí požiadať o pomoc a impact rastie.

### Globálne silence počas incidentu

Odstráni aj nové independent failure signals.

## 19. Kontrolné otázky

1. Čo tvorí exact on-call support contract?
2. Ktoré vlastnosti musí mať page?
3. Ako sa delivery, acknowledgement a qualified response líšia?
4. Aké responsibilities majú primary a secondary?
5. Čo má obsahovať shift handoff?
6. Aké dimensions môže mať escalation?
7. Prečo ack nemá vždy zastaviť escalation?
8. Ako sa testuje schedule a access readiness?
9. Ktoré metrics opisujú page quality?
10. Ako on-call overload vytvára reliability feedback loop?
11. Prečo `SRE-PAY-53` neeskaloval napriek rýchlemu acku?
12. Čo musí overiť on-call acceptance verdict?

## Glossary impact

Relevantné pojmy: on-call support contract, page eligibility, notification-delivery chain, qualified response, primary on-call, secondary on-call, shift handoff, time/skill/authority/capacity/severity escalation, schedule canary, page quality, on-call sustainability a on-call acceptance verdict.

## Primárne zdroje

- [Google SRE — Being On-Call](https://sre.google/sre-book/being-on-call/)
- [Google SRE Workbook — On-Call](https://sre.google/workbook/on-call/)
- [Google SRE — Dealing with Interrupts](https://sre.google/sre-book/dealing-with-interrupts/)
- [Google SRE — Service Best Practices](https://sre.google/sre-book/service-best-practices/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Incident management](incident-management.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Runbooks a playbooks →](runbooks-and-playbooks.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
