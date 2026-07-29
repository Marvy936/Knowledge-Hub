# Blameless postmortems

Blameless postmortem je reviewovaný a zdieľaný záznam incidentu, ktorý zachytáva **impact, časovú os, response, príčinné mechanizmy, úspešné aj neúspešné kontroly a overiteľné follow-up actions** bez osobného obviňovania ľudí, ktorí konali s informáciami a nástrojmi dostupnými v danom čase.

Blameless neznamená bez zodpovednosti, bez presnosti ani bez nepríjemných zistení. Znamená, že accountability sa viaže na opravu systémov, procesov a rozhodovacích podmienok, nie na zjednodušený príbeh o vinníkovi.

```text
postmortem trigger a exact incident subject
→ evidence-preserving draft
→ factual impact a timeline
→ causal analysis a response evaluation
→ what went well / poorly / where we got lucky
→ corrective-action portfolio
→ independent review a publication
→ action tracking a mechanism closure
→ cross-incident learning a recurrence validation
```

## 1. Prečo postmortem existuje

Incident response obnovuje službu. Postmortem mení incident na organizačné learning evidence.

Bez formalizovaného reviewu sa často stane:

```text
incident skončí
→ temporary mitigation zostane
→ assumptions sa zabudnú
→ action items nemajú ownera
→ rovnaký failure path sa vráti
→ budúci responder začína od nuly
```

Postmortem má tri hlavné outcomes:

1. reprodukovateľné porozumenie incidentu;
2. konkrétne zníženie pravdepodobnosti alebo impactu recurrence;
3. prenos knowledge mimo ľudí, ktorí boli priamo pri incidente.

## 2. Exact postmortem subject

Postmortem musí byť viazaný na immutable incident generation:

- incident ID;
- service a business capability;
- impact start/end;
- affected users, tenants, Regions alebo operations;
- severity a declaration generation;
- relevant releases/configurations/policies;
- incident commander a response roles;
- evidence cutoff;
- document owner a reviewers;
- publication state.

Príklad:

```text
postmortem: PM-SRE-PAY-54-v1
incident: SRE-PAY-54
capability: settlement reconciliation
impact: 91 stale/unknown merchant settlements
technical cohort: 7 842 active rows incorrectly archived
window: 02:14–06:03 UTC
review status: draft → reviewed → published
```

Editovanie published postmortemu má vytvoriť novú revision alebo auditovanú opravu, nie potichu prepísať historical record.

## 3. Kedy postmortem vytvoriť

Criteria majú byť definované pred incidentom. Typické triggers:

- user-visible outage alebo degradation nad threshold;
- data loss, corruption alebo confidentiality impact;
- error-budget consumption nad policy hranicu;
- SEV-1/SEV-2 declaration;
- manual failover, rollback alebo destructive intervention;
- recovery time nad objective;
- monitoring alebo escalation failure;
- near miss s vysokým potential impactom;
- recurrence predchádzajúceho mechanismu;
- stakeholder request.

Každý minor alert nepotrebuje plný dokument. Menšie events môžu používať lightweight review. Kritérium však nesmie závisieť od toho, či incident vyzerá pre tím nepríjemne.

## 4. Blamelessness ako analysis contract

Blameless writing predpokladá:

```text
ľudia mali dobrý úmysel
+ konali podľa vtedy dostupných informácií
+ používali povolené nástroje a procesy
→ analyzujeme, prečo environment podporil chybný outcome
```

Namiesto:

```text
operator neopatrne spustil compactor
```

použi:

```text
release workflow povolil production activation,
pretože config schema akceptovala missing scope,
canary vrátila zero affected rows
a gate overoval job exit namiesto business invariantu
```

Taký opis je presnejší aj actionable.

## 5. Blameless neznamená anonymný

Mená alebo role môžu byť potrebné pre:

- incident handoff;
- audit;
- action ownership;
- timeline reconstruction;
- recognition dobrej response práce.

Zakázaný nie je identity context, ale osobné hodnotenie bez mechanistickej hodnoty. V širšie zdieľanej verzii možno identity minimalizovať podľa privacy a security policy.

## 6. Accountability bez blame

Healthy accountability znamená:

- incident owner zabezpečí completion dokumentu;
- action owners doručia alebo explicitne eskalujú blockers;
- leadership poskytne priority a capacity;
- reviewers odmietnu plytké causal claims;
- accepted residual risk má ownera a expiry;
- intentional policy violations sa riešia samostatným vhodným procesom.

Blamelessness nie je výhovorka pre neuzatvorené action items.

## 7. Povinná štruktúra

Kvalitný postmortem obsahuje minimálne:

1. metadata a status;
2. executive summary;
3. user/business impact;
4. detection a response summary;
5. overenú timeline;
6. trigger a causal analysis;
7. contributing factors;
8. what went well;
9. what went poorly;
10. where we got lucky;
11. recovery a reconciliation;
12. corrective actions;
13. residual risk;
14. lessons a similar-system scope;
15. review a publication evidence.

Template pomáha konzistentnosti, ale nesmie nahradiť myslenie.

## 8. Executive summary

Summary má v niekoľkých vetách vysvetliť:

```text
čo sa stalo
+ komu a ako to ublížilo
+ ako dlho
+ hlavný failure mechanismus
+ ako bola služba obnovená
+ aké najdôležitejšie actions nasledujú
```

Nesmie tvrdiť definitívnu root cause, kým analysis nie je dokončená.

Príklad:

```text
Release 7.25.0 aktivoval settlement compactor, ktorý interpretoval
chýbajúci tenant scope ako wildcard a archivoval aj active rows.
Provider callbacks potom stratili correlation path; 91 merchant settlements
bolo dočasne stale alebo unknown. Job bol zastavený, affected cohort bol
obnovený z isolated point-in-time restore a reconciliovaný s provider ledgerom.
Follow-up odstraňuje wildcard semantics, zavádza bounded affected manifest
a testuje coordinated restore consistency group.
```

## 9. Impact

Impact musí byť user-centered a numericky podložený:

- počet affected users/operations;
- duration;
- failed, degraded, delayed a unknown outcomes;
- financial, legal, security alebo support impact;
- data integrity/loss classification;
- SLO/error-budget impact;
- affected cohorts;
- confidence a measurement limitations.

`Database bola corrupted` nie je impact statement. Je to technický stav.

## 10. Detection a response

Zaznamenaj oddelene:

```text
time to detect
→ time to acknowledge
→ time to declare
→ time to contain
→ time to technical recovery
→ time to business reconciliation
→ time to full closure
```

Pri `SRE-PAY-54` bola database healthy a job skončil successful. Incident odhalila až callback-correlation correctness a merchant-state discrepancy. To je monitoring lesson, nie iba timeline detail.

## 11. Factual timeline

Timeline používa overené state transitions. Každá položka má:

- timestamp a timezone;
- actor alebo system subject;
- action/transition;
- evidence source;
- outcome;
- confidence.

Nevkladaj do timeline retrospectívne hodnotenie:

```text
02:10 — team urobil zlú konfiguráciu
```

Lepšie:

```text
02:10 — workload načítal config generation 54 bez tenant_scope;
config read-back potvrdzuje absent field
```

## 12. What went well

Táto sekcia nie je dekorácia. Identifikuje controls, ktoré treba zachovať alebo rozšíriť:

- business correctness SLI odhalila silent failure;
- incident commander zastavil ďalšie destructive jobs;
- WAL a audit zachovali exact affected IDs;
- provider podporoval idempotency key lookup;
- isolated restore zabránil broad production rewind;
- support identifikoval affected merchants;
- responders eskalovali uncertainty namiesto unsafe replayu.

Silné response behavior sa má explicitne uznať.

## 13. What went poorly

Opisuje system/process gaps:

- destructive config bola fail-open;
- canary nemala positive eligible population;
- job success oracle bol exit code;
- broad DB role a chýbajúci max scope zväčšili blast radius;
- restore decryption grant nebol current;
- consistency-group manifest chýbal;
- business recovery bola pomalšia než deklarovaný RTO.

Vyhni sa formulácii `team nevedel`, ak možno presne pomenovať chýbajúci signal, tool alebo contract.

## 14. Where we got lucky

Luck analysis odhaľuje latentný risk:

- idempotency keys zabránili potvrdeným duplicate provider settlements;
- compactor neodstránil immutable provider reference pre všetky rows;
- WAL retention ešte obsahovala clean point;
- incident nastal mimo najvyššieho traffic peak-u;
- decryption key nebola compromised;
- provider ledger bol dostupný pre reconciliation.

Luck sa nesmie zameniť za control. Každé kritické `mali sme šťastie` potrebuje risk decision alebo action.

## 15. Causal section

Postmortem používa výsledok RCA, ale neprepisuje ho na dramatický lineárny príbeh.

Rozlišuj:

- trigger;
- technical root cause;
- systemic root cause;
- escape/detection causes;
- amplification factors;
- recovery-delay causes;
- residual unknowns.

Causal tvrdenia odkazujú na evidence a counterfactual reasoning. `Root cause: operator error` je review failure.

## 16. Action items

Action items majú odstraňovať alebo obmedzovať mechanisms:

| ID | Mechanismus | Action | Owner | Priority | Due | Verification |
|---|---|---|---|---|---|---|
| ARCH-219 | missing scope → wildcard | mandatory scope + fail-closed runtime | Settlement Platform | P0 | 2026-08-05 | missing/empty/wrong scope rejected |
| SAFE-87 | unbounded batch | affected manifest + max 500 rows | Data Platform | P0 | 2026-08-07 | broad batch abort test |
| OBS-311 | silent archive corruption | transition/correlation SLI | Observability | P1 | 2026-08-12 | controlled failure pages |
| REC-144 | slow restore access | decryption/access canary | Resilience | P1 | 2026-08-10 | isolated restore drill |
| REC-145 | incomplete consistency group | DB/outbox/broker/provider manifest | Payments SRE | P0 | 2026-08-14 | end-to-end reconciliation drill |

Action item musí mať verification, nie iba status `Done`.

## 17. Action classes

Vyvážené portfolio obsahuje:

### Prevent

Odstráni failure path alebo invalid state.

### Detect

Skráti čas do spoľahlivého signal-u.

### Contain

Zmenší blast radius alebo rate.

### Recover

Skráti a spresní obnovu.

### Learn

Rozšíri knowledge, testy alebo similar-system audit.

Iba prevent actions môžu byť neúmerne drahé; iba detect actions nechávajú incident opakovať. Portfolio má byť risk-based.

## 18. Priority a action-item SLO

Postmortem action priority má vychádzať z:

- potential impact;
- recurrence likelihood;
- current exposure;
- control effectiveness;
- implementation lead time;
- dependencies;
- error-budget policy;
- compliance alebo security urgency.

Organizácia môže definovať action-item SLO, napríklad P0 mitigation do dní a mechanism closure do týždňov. Čísla musia byť lokálnou policy, nie univerzálnym pravidlom.

## 19. Review gate

Nezávislý review overuje:

- impact completeness;
- timeline evidence;
- causal depth;
- blameless factual language;
- what-went-well/poorly/luck coverage;
- action mapping na mechanisms;
- owners, priority a due dates;
- privacy/security redaction;
- similar-system scope;
- publication audience.

Unreviewed postmortem nie je organizational knowledge.

## 20. Publication a sharing

Zdieľanie má byť čo najširšie v rámci bezpečnostných a privacy hraníc:

- owning team;
- dependent teams;
- platform/security/data owners;
- leadership podľa impactu;
- searchable incident repository;
- training alebo game-day library.

Secrets, customer PII, exploit details alebo citlivé vendor údaje musia byť redacted alebo oddelené do restricted annexu.

## 21. Action tracking

Postmortem zostáva živý cez action lifecycle:

```text
accepted action
→ planned
→ implemented
→ deployed/effective
→ verified
→ mechanism closed alebo residual risk accepted
```

Ticket closed po merge-i nie je production effectiveness. Verification môže vyžadovať:

- negative test;
- canary;
- restore drill;
- wrong-subject rejection;
- second incident/operation simulation;
- telemetry read-back;
- recurrence-free observation window.

## 22. Recurrence review

Pri podobnom incidente sa pýtaj:

- bol to rovnaký mechanismus alebo iba podobný symptom?
- boli previous actions dokončené?
- boli effective v správnom scope-e?
- vznikol alternate path?
- bola action príliš lokálna?
- prečo similar-system search nenašiel túto variantu?
- prečo recurrence watch skončil priskoro?

Recurring incident nie je dôvod na blame; je dôkaz, že learning/control loop nebol uzavretý.

## 23. Cross-incident trend analysis

Structured metadata umožňuje agregovať:

- opakované trigger classes;
- common root/escape causes;
- detection gaps;
- affected dependencies;
- recovery delays;
- stale runbooks;
- overdue action items;
- toil a on-call amplification;
- similar technology/control failures.

Trend analysis môže odhaliť, že desať lokálnych incidents má jednu platform root cause.

## 24. Worked postmortem `PM-SRE-PAY-54-v1`

### Impact

- `186 420` rows broad-archived;
- `7 842` rows nebolo terminal;
- `613` provider callbacks potrebovalo secondary correlation;
- `91` merchant-visible settlements bolo stale/unknown;
- potvrdené duplicate settlements: `0`;
- business recovery trvala `3 h 49 min`;
- deklarovaný RTO `45 min` bol prekročený.

### What went well

- business correctness SLI detegovala silent failure;
- incident command zastavil destructive jobs;
- WAL/audit poskytli affected manifest;
- isolated restore prebehol bez production rewind;
- provider idempotency lookup umožnil reconciliation;
- responders odmietli broad replay pri unknown outcome.

### What went poorly

- missing scope bol wildcard;
- zero-row canary vytvorila false confidence;
- broad role a unbounded batch zväčšili impact;
- restore identity nemala current decryption grant;
- consistency-group a post-point manifest sa skladali počas incidentu;
- declared RPO/RTO neboli odvodené od tested end-to-end recovery pathu.

### Where we got lucky

- WAL clean point bol stále retained;
- provider ledger bol dostupný;
- immutable external reference zostala pre väčšinu rows;
- traffic bol pod campaign peakom;
- corruption nezasiahla credential ani audit stores.

### Learning verdict

Incident nevznikol preto, že jedna osoba `zle nastavila parameter`. Vznikol preto, že destructive workflow považoval missing scope za validný broad intent a celý delivery/recovery systém túto interpretáciu neodmietol.

## 25. Postmortem acceptance verdict

Postmortem je prijatý, keď:

- spĺňa pre-defined trigger criteria;
- exact incident/document generation je identifikovaná;
- impact je user/business-centered a kvantifikovaný;
- timeline je evidence-backed;
- language je factual a blameless;
- response effectiveness je vyhodnotená;
- what went well, poorly a luck sú explicitné;
- causal section je dostatočne hlboká;
- actions mapujú na failure mechanisms;
- owners, priorities, due dates a verification existujú;
- independent review prešiel;
- document je publikovaný správnemu audience;
- action tracking vedie až k effective-state verification;
- similar-system a recurrence review sú naplánované;
- sensitive data je správne chránené.

## 26. Anti-patterny

### Postmortem ako trest

Ľudia skrývajú uncertainty a incidents, čím rastie systémový risk.

### Blameless = bez konkrétnosti

Vynechanie actions, actors a failures znemožní učenie.

### Šablóna vyplnená po pamäti

Bez preserved evidence vznikne presvedčivý, ale nepresný príbeh.

### Root cause: human error

Organizácia nevie, ktorý executable control má zmeniť.

### Action: buďte opatrnejší

Nie je scoped, owned ani verifiable.

### Všetko P0

Priority stratia význam a kritické actions sa utopia.

### Dokument publikovaný, actions zabudnuté

Pre usera je postmortem bez účinnej zmeny nerozoznateľný od žiadneho postmortemu.

### Luck ignorovaná

Latentný high-impact path zostane otvorený.

## 27. Kontrolné otázky

1. Čo robí postmortem blameless, ale accountable?
2. Aké objektívne triggers majú vyžadovať postmortem?
3. Čo tvorí exact postmortem subject?
4. Ako sa executive summary líši od causal analysis?
5. Prečo musí byť impact user-centered?
6. Ako zapísať timeline bez retrospectívneho blame?
7. Prečo sú `what went well` a `where we got lucky` dôležité?
8. Aké action classes tvorí vyvážené portfolio?
9. Prečo merge alebo closed ticket nie je mechanism closure?
10. Ako independent review zvyšuje kvalitu?
11. Ako recurrence review odlíši rovnaký mechanismus od podobného symptómu?
12. Čo musí overiť postmortem acceptance verdict?

## Glossary impact

Relevantné pojmy: postmortem subject, blameless analysis contract, system accountability, postmortem trigger, factual timeline, what went well, what went poorly, where we got lucky, action-item SLO, mechanism closure, recurrence review, cross-incident trend analysis a postmortem acceptance verdict.

## Primárne zdroje

- [Google SRE — Postmortem Culture: Learning from Failure](https://sre.google/sre-book/postmortem-culture/)
- [Google SRE Workbook — Postmortem Culture: Learning from Failure](https://sre.google/workbook/postmortem-culture/)
- [Google SRE — Incident Management Guide](https://sre.google/resources/practices-and-processes/incident-management-guide/)
- [NIST SP 800-61 Rev. 3 — Incident Response Recommendations and Considerations](https://csrc.nist.gov/pubs/sp/800/61/r3/final)
