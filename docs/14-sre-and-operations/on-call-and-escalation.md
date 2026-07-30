# On-call a escalation

On-call je časovo ohraničená zodpovednosť prevziať urgentný production signal, posúdiť jeho impact a bezpečne konať alebo eskalovať. Nie je to neobmedzená dostupnosť každého engineera ani mechanizmus, ktorým služba absorbuje všetku neplánovanú prácu. Escalation je riadený prechod k ďalšej osobe, role, tímu alebo authority, keď current responder nemá čas, skill, access, kapacitu alebo rozhodovacie oprávnenie potrebné na ochranu služby.

Základným omylom je zameniť doručenie alebo acknowledgement page-u za effective response. Kliknutie v notification systéme dokazuje iba interaction s alertom. Nedokazuje, že responder pochopil subject, má správny access, prevzal ownership, začal vhodnú mitigation alebo vie incident včas deklarovať.

## 1. Dominantný support-to-qualified-response lifecycle

On-call systém začína service support objective-om a končí sustainable rotation, ktorá dokáže opakovane vytvoriť qualified response. Routing, schedule, delivery, acknowledgement, ownership, escalation a incident declaration sú samostatné boundaries a každá potrebuje vlastný dôkaz.

```text
service support objective
→ exact on-call support contract
→ page eligibility a routing
→ rotation, schedule a competency generation
→ notification delivery
→ human acknowledgement
→ qualified ownership a impact assessment
→ time, skill, authority, load alebo severity escalation
→ incident declaration a coordinated response
→ recovery, handoff a follow-up
→ page-quality, fatigue a sustainability review
```

On-call je prijateľný iba vtedy, keď urgentný user-impact signal dostane pripravený responder, ktorý vie bezpečne konať alebo rýchlo eskalovať, a keď dlhodobý load nepoškodzuje ľudí ani reliability.

## 2. Exact on-call support contract

„Payments majú 24/7 on-call“ nehovorí, čo sa podporuje ani aký response je sľúbený. Exact contract obsahuje supported capability, hours a time zones, page eligibility, primary/secondary roles, acknowledgement a qualified-response targets, required skills a access, incident-declaration authority, vendor/dependency paths, handoff rules a sustainability limits.

```text
contract: OC-PAY-54
service: Atlas settlement completion
coverage: 24/7
primary: triage, containment alebo incident declaration
secondary: backup, parallel diagnosis a overload protection
service owner: architecture a high-risk authority
provider P1: activation do 10 min pri provider-wide impacte
security/data escalation: immediate
qualified-response target: 5 min po page-i
```

Bez explicitného contractu sa support opiera o sociálnu pamäť a hidden key people. Zmena schedule, service ownershipu, provider kontaktu alebo declaration policy vytvára novú support generation, ktorú treba otestovať.

## 3. Page eligibility a actionable signal

Page má prerušiť človeka iba vtedy, keď je urgentný, relevantný pre podporovanú službu, dostatočne spoľahlivý, actionable pre receiving role a časovo citlivý. Capacity trend, known low-impact defect alebo report bez potreby okamžitej action patrí do ticketu či review, nie do nočného page-u.

Dobrý page prenáša impact alebo imminent risk, exact service/cohort/Region, threshold, dôvod urgency, safe first observation, forbidden action, runbook alebo playbook a escalation path. Page bez contextu núti respondera najprv rekonštruovať subject, čím predlžuje qualified response.

Page quality sa nehodnotí iba false-positive rate-om. Dôležité sú actionable, duplicate a grouping rates, pages per shift, after-hours interruption, runbook coverage, time to qualified response, repeated families a podiel pages, ktoré mali byť ticketom.

## 4. Delivery, acknowledgement a qualified ownership

Notification chain má viac krokov:

```text
alert fired
→ routing decision
→ provider delivery attempt
→ device/channel delivery
→ human acknowledgement
→ responder prevzal exact subject
→ impact a urgency assessed
→ safe action alebo escalation začala
```

Každý krok má inú failure semantics. Page môže byť nesprávne routed, delivery provider môže zlyhať, device môže byť nedostupné alebo človek môže kliknúť bez reálnej kapacity konať. Preto sa samostatne meria routing latency, delivery success, acknowledgement time, time to qualified ownership, declaration latency, effective mitigation time a escalation latency.

Acknowledgement nesmie automaticky zastaviť všetky escalation paths. No-ack escalation rieši nedostupnosť človeka; progress alebo severity escalation rieši situáciu, keď človek odpovedal, ale impact rastie alebo nevznikla qualified action.

## 5. Rotation, competency a readiness

Rotation musí vytvoriť coverage bez chronickej únavy a key-person dependency. Zohľadňuje počet ľudí a time zones, primary/secondary model, shift length, nočné a víkendové zaťaženie, holidays, skill distribution, shadowing, overlap, planned leave, post-incident recovery a lokálne pracovné pravidlá.

Primary preberá prvý signal, potvrdí subject a impact, vykoná safe first response a drží ownership do explicitného handoffu. Secondary chráni primary pred multitaskingom, preberá ďalšie alerts, poskytuje parallel diagnosis alebo replacement a môže prevziať command rolu. Specialist alebo service owner poskytuje deep knowledge a high-risk authority, ale nemá byť jedinou osobou schopnou obnoviť službu.

Pred shiftom sa testuje identity/MFA, JIT alebo break-glass path, telemetry a audit access, bounded remediation permissions, communication channels, vendor contacts, current docs, workstation/network a declaration authority. Access sa prvýkrát netestuje počas SEV-1.

## 6. Escalation dimensions

Escalation nie je iba timer po neacknowledged page-i. **Time escalation** reaguje na absent acknowledgement alebo qualified response. **Skill escalation** aktivuje deep expertise pri nízkej diagnostic confidence. **Authority escalation** rieši destructive, financial, security alebo customer decision mimo current role. **Load escalation** pridáva respondera pri simultánnych incidents. **Severity escalation** aktivuje incident command pri rastúcom impacte. **Dependency escalation** privádza iný tím alebo vendora a **safety escalation** chráni data integrity, security, legal alebo human safety.

Tieto dimensions sa môžu aktivovať súčasne. Acknowledged page nezruší progress escalation, ak completion burn pokračuje. Primary tiež nemusí čakať na timeout, ak vie, že potrebuje specialistu alebo nemá required authority. Escalation je správne používanie support systému, nie osobné zlyhanie.

## 7. Handoff a continuity

Shift handoff je explicitný transfer operational state-u a ownershipu. Obsahuje active incidents a severity, open pages/tickets, current service health, temporary overrides, recent changes, capacity/provider constraints, pending commitments, expected events a ownera každého follow-upu.

```text
outgoing responder state
→ shared handoff artifact
→ incoming responder read-back
→ explicit ownership acceptance
→ previous responder released
```

Handoff „nič zvláštne“ bez kontroly incidents, overrides a change calendaru nie je continuity proof. Pri aktívnom incidente sa command role prenáša samostatne od bežnej on-call shift responsibility.

## 8. Sustainability a human reliability

Chronický on-call overload vytvára reinforcing loop:

```text
sleep disruption a context switching
→ pomalšia diagnosis a risky shortcuts
→ viac incidents a pages
→ menej engineering času
→ menej reliability improvement
→ ďalší overload
```

Sustainability sa sleduje cez nočné prerušenia, simultaneous incidents, shift swaps, recovery time, self-reported fatigue, project-work displacement, attrition, knowledge concentration a psychological safety pri escalation. Jedno jednoduché maximum pages nie je univerzálny zákon; page severity, duration a cognitive load sa líšia.

Responder nemá byť penalizovaný za skorú escalation alebo declaration. Po náročnom incidente potrebuje replacement coverage a recovery interval, inak organizácia prenáša reliability risk do ďalšieho shiftu.

## 9. Connected incident `SRE-PAY-53`

Settlement rotation mala štyroch engineers a poskytovala 24/7 coverage. Počas šiestich hodín pred campaign peakom primary dostal 11 pages: šesť duplicate alebo symptom alerts, tri nonurgent capacity warnings, jeden provider heartbeat false positive a jeden `SettlementCompletionFastBurn` page.

Critical page dorazila o `10:07 UTC` a responder ju acknowledged o dve minúty. Notification platforma preto zastavila no-ack escalation. Responder však súčasne riešil dva support requests a starší broker alert. Secondary schedule override skončil o hodinu skôr pre timezone drift, current runbook nemal provider P1 kontakt a escalation policy nereagovala na absent mitigation progress ani rast severity.

On-call root failure bol support contract, ktorý zamieňal acknowledgement za qualified ownership a nemal load-, severity- ani progress-based escalation. Malá rotation, duplicate page load, stale secondary schedule, chýbajúci readiness check a kultúra „najprv vyrieš, potom deklaruj“ predĺžili detection-to-command interval.

## 10. Containment a authoritative redesign

Po declaration IC aktivoval backup secondary mimo stale schedule, presunul support tickets na nonincident ownera, grouped duplicate alerts pod incident ID, explicitne eskaloval DB/provider specialists, pridelil primary bounded technical task a zabezpečil replacement pre nasledujúci shift. Alert silence bolo scoped na exact incident, service a čas; nezablokovalo independent failure signals.

Nový contract `OC-PAY-54` používa:

```text
user-impact page eligibility
→ active primary + secondary
→ delivery a acknowledgement evidence
→ qualified-response timer
→ severity/progress/load escalation
→ direct incident-declaration authority
→ verified provider/security/data paths
→ explicit handoff
→ page-quality a sustainability review
```

Capacity trends prešli na tickets, duplicate symptoms sa groupujú, critical burn page eskaluje aj po ACK pri absent progress, schedule/timezone sa testujú canary notificationou a pre-shift checklist overuje access a contacts. Repeated page family automaticky vytvára reliability/toil work item.

## 11. On-call acceptance contract

Positive path musí preukázať, že user-impact page je správne routed, doručený, acknowledged a prejde do qualified ownershipu v target time. No-ack path musí aktivovať secondary. Ack-without-progress path musí napriek kliknutiu eskalovať podľa severity alebo burn rate. Schedule-failure path musí odhaliť timezone/override drift a nájsť backup respondera.

Recovery path musí potvrdiť incident declaration, safe response, handoff a replacement po fatigue. Forbidden paths zahŕňajú nonurgent nočný page, ACK ako jediný success signal, unavailable specialist ako hidden single point, global silence a pokračovanie primary respondera bez replacementu po severe incident-e.

```text
positive:
urgent page → qualified owner → safe action

escalation:
no ACK alebo no progress → secondary/specialist/IC

continuity:
shift handoff → read-back → explicit ownership

forbidden:
nonactionable page
ACK bez ownershipu
stale schedule bez canary
escalation culture penalty
fatigue bez replacementu
```

Verdict musí prejsť na druhom shift-e a pri simulovanom primary/secondary failure-i, nie iba počas office hours s dostupným service ownerom.

## 12. Troubleshooting on-call failure-u

Ak page existoval, ale response bol pomalý, sleduj celý chain: alert generation, routing, schedule generation, delivery, ACK, qualified ownership, responder load, access, escalation conditions, declaration authority a handoff.

```text
slow response
→ page eligibility a alert subject
→ route/schedule/timezone/override
→ delivery a device
→ ACK vs qualified response
→ concurrent load a readiness
→ time/skill/authority/severity escalation
→ incident declaration
→ effective mitigation time
```

`Ack in 2 min` nie je dobrý outcome, ak incident command vznikne o 24 minút neskôr.

## 13. Anti-patterny

Tieto anti-patterny optimalizujú notification alebo heroickú dostupnosť, ale nezaručujú qualified a sustainable response.

- **Každý alert je page —** nonurgent alebo nonactionable signals spotrebujú attention potrebnú pre critical incidents. Routing musí rozlišovať page, ticket a report.
- **Acknowledged znamená handled —** kliknutie nepotvrdzuje subject understanding, authority ani mitigation progress.
- **Primary musí všetko vyriešiť sám —** odďaľuje escalation, zvyšuje multitasking a vytvára key-person risk.
- **Heroická rotation —** malý tím absorbuje 24/7 load za cenu zdravia a engineering capacity, čo zvyšuje budúci page demand.
- **Escalation je zlyhanie jednotlivca —** responders skrývajú uncertainty a impact rastie. Escalation má byť štandardný control transition.
- **Globálne silence počas incidentu —** odstráni independent failure signals; silence musí byť scoped a expirovateľné.

## 14. Kontrolné otázky

1. Čo tvorí exact on-call support contract?
2. Ktoré signals patria do page-u a ktoré do ticketu?
3. Ako sa delivery, acknowledgement a qualified ownership líšia?
4. Aké responsibilities majú primary, secondary a specialist?
5. Čo testuje pre-shift readiness?
6. Aké dimensions má escalation?
7. Prečo ACK nemá vždy zastaviť escalation?
8. Čo musí obsahovať handoff?
9. Ako overload rotation vytvára reliability loop?
10. Prečo `SRE-PAY-53` neeskaloval napriek rýchlemu ACK?
11. Ktoré positive, escalation, continuity a forbidden paths patria do acceptance?
12. Prečo sa testuje druhý shift a schedule failure?

## Glossary impact

Relevantné pojmy: on-call support contract, page eligibility, delivery chain, acknowledgement, qualified ownership, primary/secondary on-call, multi-dimensional escalation, schedule canary, handoff continuity, page quality, on-call sustainability a on-call acceptance contract.

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
