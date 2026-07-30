# Incident management

Incident management je koordinovaný control system na obmedzenie user a business impactu, obnovenie bezpečnej služby a zachovanie dôkazov potrebných na učenie a nápravu. Nie je synonymom debuggingu ani chatom, v ktorom veľa ľudí súčasne skúša zmeny. Incident vzniká vtedy, keď observed alebo pravdepodobný impact prekročí bežný operational workflow a vyžaduje explicitnú command štruktúru, prioritizáciu a bounded authority.

Technická diagnóza je iba jedna časť response. Tím musí súčasne riadiť blast radius, rozhodovať pod neistotou, koordinovať zmeny, komunikovať potvrdený stav a overiť, že pôvodný business outcome bol skutočne obnovený. Zelený endpoint alebo dočasný pokles error rate-u tento end-to-end verdict neposkytuje.

## 1. Dominantný impact-to-recovery lifecycle

Incident lifecycle začína user-impact signalom a končí až stabilným, overeným outcome-om a vlastnenou follow-up prácou. Declaration mení normal troubleshooting na koordinovaný režim; command roles oddeľujú rozhodovanie, technické vykonávanie, communication a longer-horizon planning.

```text
signal, user report alebo imminent risk
→ exact incident subject a impact hypothesis
→ declaration a severity transition
→ IC, Operations, Communications a Planning ownership
→ authoritative incident state a evidence preservation
→ stabilization a blast-radius control
→ competing hypotheses a bounded changes
→ technical, business a forbidden-outcome verification
→ handoff, recurrence watch a communication closure
→ incident closure a owned corrective work
```

Rýchlosť bez koordinácie môže zhoršiť incident. Naopak command process bez user-impact feedbacku sa môže zmeniť na administratívny overhead. Každý transition preto potrebuje objective, owner a observation, ktorá ukáže, či impact klesá.

## 2. Exact incident subject

Názov „payments outage“ nestačí. Exact subject zachováva affected capability, cohort a Region, start/detection/declaration times, release a configuration generations, affected operations a data, SLO/error-budget impact, suspected paths, active mitigations a current command ownership.

```text
incident: SRE-PAY-53
capability: settlement completion
Region: prod-eu1
cohort: end-of-month campaign merchants
start: 10:02 UTC
detected: 10:07 UTC
declared: 10:31 UTC
impact: completion latency > 10 min, rising backlog
release: settlement-api 8.1.0
capacity generation: CAP-PAY-53-A
current commander: IC-1
```

Subject sa aktualizuje, keď sa objaví nový affected cohort alebo data risk, ale history zostáva zachovaná. Bez tejto identity môžu rôzne tímy riešiť odlišný scope pod jedným incident ID alebo aplikovať mitigation na nesprávnu release generation.

## 3. Declaration a severity ako control transition

Declaration je okamih, keď organizácia prizná, že normal ownership a tooling nestačia. Spúšťa command roles, communication cadence, change logging, vendor paths a priority nad bežnou prácou. Má nastať pri critical journey SLO burne, rastúcom impacte, data/security risku, multi-team koordinácii, nejasnom blast radiuse alebo potrebe urgentného externého communication.

Severity opisuje user/business impact a response urgency, nie iba počet errors. Zohľadňuje criticality capability, affected cohorts, duration a growth rate, workaround, data integrity, regulatory alebo security risk, recovery complexity a neistotu scope-u.

| Severity | Impact contract | Response contract |
|---|---|---|
| SEV-1 | rozsiahly critical outage, data-integrity risk alebo nekontrolovaný rast | okamžitá command štruktúra, executive/customer communication a continuous response |
| SEV-2 | významná degradácia critical journey alebo bounded high-impact cohort | okamžitý technical response, explicitný owner a pravidelné updates |
| SEV-3 | obmedzený stabilný impact s workaroundom | urgentná owned remediation v pracovnom režime |
| SEV-4 | nízky impact bez urgentného user risku | normal queue a review |

Severity možno zvýšiť aj pri nezmenenom error count-e, ak rastie uncertainty alebo data risk. Zníženie vyžaduje evidence, nie optimizmus.

## 4. Command roles a decision authority

Incident Commander drží objective, priority, role assignments, decision cadence, escalation a closure. Nemusí byť najhlbší subject-matter expert; ak je jediný expert zároveň IC, stráca kapacitu na technické myslenie aj coordination.

Operations lead koordinuje hypotheses, technical actions a effective-state observations. Communications lead prekladá potvrdený stav na predvídateľné interné a externé updates a chráni responders pred opakovanými status otázkami. Planning alebo logistics lead sleduje staffing, vendor access, temporary overrides, handoff, longer-horizon recovery a follow-up commitments.

Pri menšom incidente môže jedna osoba držať viac roles, ale responsibilities nesmú zmiznúť. Každé high-risk rozhodnutie musí mať identifikovanú authority: IC môže schváliť scoped mitigation, no data restore, security containment alebo contractual customer action môže vyžadovať ďalšieho ownera.

## 5. Authoritative incident state

Chat je komunikačný stream, nie spoľahlivý current state. Incident potrebuje jeden stručný materializovaný dokument alebo channel topic obsahujúci incident ID, severity, commander-a, impact, scope/exclusions, timeline, active hypotheses, recent evidence, mitigations a owners, paused changes, next checkpoint, communication status a recovery criteria.

```text
current truth
+ unresolved uncertainty
+ active action/owner/expected signal
+ decision history
+ next checkpoint
```

State document sa aktualizuje po významnom observation alebo decision transitione. Nemá kopírovať všetku telemetry; má umožniť novému responderovi pochopiť, čo je potvrdené, čo sa skúša a ktoré zmeny nesmú kolidovať.

## 6. Stabilization pred úplným root cause

Počas rastúceho impactu je priorita zastaviť blast radius, zachovať evidence a obnoviť bounded service. Úplné vysvetlenie môže prísť neskôr. Legitímne stabilizačné kroky zahŕňajú zastavenie rollout-u, admission limit, izoláciu cohortu, vypnutie noncritical feature, retry reduction, failover na known-good path, fencing destructive automation alebo activation degraded mode-u.

Mitigation nie je remediation. Môže znížiť impact bez odstránenia root mechanismu. Preto sa zaznamenáva ako temporary state s ownerom, expiry a recovery implication. Napríklad admission limit chráni DB/provider path, ale vytvára odmietnuté operations, ktoré musia zostať vo user-impact evidence.

Evidence preservation má prednosť pred broad cleanupom. Pred mutation sa zachovajú exact queries, actor, configuration, release, affected operation manifests a relevantné logs/ledgers. Incident response nesmie zničiť informáciu potrebnú na odlíšenie lost, pending, completed a unknown outcomes.

## 7. Hypothesis-driven a bounded changes

Každá technická akcia potrebuje hypothesis, supporting observation, exact scope, expected signal, abort criterion, rollback alebo compensation, ownera a timestamp.

```text
hypothesis: provider retries saturujú DB pool
observation: retry multiplier 4.6×, DB acquire p99 1.4 s
action: znížiť provider concurrency a vypnúť immediate retries
expected: DB acquire p99 < 200 ms a queue drain rastie
abort: completion rate klesne pod 1 500/s
owner: Ops-2
```

Incident mode neruší change governance; iba ju zrýchľuje a zviditeľňuje. Parallel untracked changes ničia causal evidence a môžu vytvoriť oscillation. Operations lead preto vedie action log a IC rozhoduje o konfliktných alebo blast-radius meniacich zásahoch.

Unknown outcome sa nesmie riešiť blind retryom. Ak provider request mohol uspieť, recovery potrebuje idempotency, ledger reconciliation alebo compensation, nie opakovanie podľa timeoutu.

## 8. Communication ako samostatný control loop

Dobrý update oddeľuje potvrdené facts od hypotheses a uvádza impact, current action, zostávajúce riziká a čas ďalšieho update-u. Externý communication nemá tvrdiť root cause, kým nie je overený; interný update nemá zahltiť stakeholderov raw telemetry bez rozhodovacieho významu.

Predvídateľná cadence znižuje interruption responders a zabraňuje protichodným správam. Communications lead tiež zachováva correction lineage: ak sa scope zmení, predchádzajúci update sa nevymaže, ale explicitne opraví.

## 9. Connected incident `SRE-PAY-53`

O `10:07 UTC` page `SettlementCompletionFastBurn` signalizovala rastúci completion burn rate. Primary on-call incident nevyhlásil, pretože predpokladal bežný provider transient. Nasledujúcich 24 minút application engineer zvýšil workers zo 120 na 240, database engineer zvýšil pool, support požiadal replay starších settlements a provider owner zmenil retry interval. Nikto nedržal shared state ani approved action sequence.

DB pressure a retries vzrástli, queue age pokračovala v raste a mitigations si navzájom menili observations. Support komunikoval „takmer vyriešené“, hoci completion SLO sa zhoršovalo. Incident bol deklarovaný až o `10:31 UTC` ako `SEV-1` po prekročení 15-minútovej queue age a potvrdení merchant impactu.

Traffic spike a provider slowdown zostali triggerom; capacity defect bol technický root mechanismus. Incident-management failure bola oneskorená declaration a chýbajúca command štruktúra, ktorá dovolila nekorelované parallel changes počas rastúceho impactu.

## 10. Stabilization, recovery a handoff

Po declaration bol pridelený IC, zmeny mimo approved incident actions sa zastavili a vznikli Ops, Comms a Planning roles. Admission sa obmedzila na `1 700 unique intents/s`, immediate retries sa vypli, worker concurrency sa viazala na DB/provider capacity, noncritical batch traffic sa pozastavil a affected queue sa inventarizovala pred controlled drainom.

Do 18 minút kleslo DB acquire p99 pod `180 ms`. Queue prestala rásť o `10:54 UTC` a do SLO sa vrátila o `11:42 UTC`. Historical cohort sa reconcilioval samostatne; incident zostal otvorený do second-peak testu.

Pri dlhom response handoff prenáša exact subject, effective state, unresolved risks, actions a outcomes, active hypotheses, temporary overrides, thresholds, stakeholder commitments a explicitný transfer command roles. Nový responder nemá rekonštruovať incident z tisícov chat messages.

## 11. Incident acceptance a closure contract

Positive response path musí preukázať včasnú declaration, správnu severity, explicitné roles a current state. Mitigation path musí znížiť user impact bez poškodenia evidence alebo data integrity. Recovery path musí obnoviť original business outcome, reconciliovať historical cohort a potvrdiť adjacent operation aj second-peak stability.

Forbidden paths musia byť kontrolovane odmietnuté: untracked parallel changes, broad destructive cleanup, communication hypothesis ako fact, green API pri rastúcom backloge, closure s aktívnym hidden overrideom alebo handoff bez command ownershipu.

```text
positive:
signal → declaration → command → bounded mitigation

recovery:
impact stabilný → SLO outcome → reconciliation → recurrence watch

forbidden:
ack bez incident ownershipu
parallel unlogged mutations
root-cause čakanie počas rastúceho impactu
metric recovery bez business recovery
temporary mitigation bez ownera/expiry
```

Closure neznamená, že všetka remediation je dokončená. Znamená, že impact je odstránený alebo explicitne akceptovaný, recovery criteria a recurrence watch prešli, evidence a timeline sú zachované, temporary states majú ownera a follow-up actions majú priority a closure evidence.

## 12. Troubleshooting response failure-u

Ak impact pokračuje napriek veľkej aktivite, najprv over, či incident bol deklarovaný, kto drží objective a aký je exact scope. Potom skontroluj current state, active changes, hypotheses, expected observations a recovery criteria.

```text
impact pokračuje
→ declaration/severity/IC
→ exact subject a authoritative state
→ active changes a owners
→ hypothesis/evidence/expected signal
→ conflicting mitigations
→ user-centered impact oracle
→ containment vs remediation
→ recovery criteria a adjacent cohort
```

Veľa responders a commands neznamená effective response. Dôležité je, či coordinated actions znižujú business impact a zachovávajú recovery options.

## 13. Anti-patterny

Incident anti-patterny zamieňajú technical expertise alebo activity za coordination a verified recovery. Výsledkom je pomalší response a horšia causal evidence aj napriek vysokému počtu zapojených ľudí.

- **Najseniornejší engineer je automaticky IC —** expert potom stráca kapacitu na deep diagnosis a súčasne nemusí efektívne koordinovať roles a communication.
- **Najprv nájdime root cause —** impact rastie, kým tím čaká na kompletné vysvetlenie. Stabilization môže prebehnúť s explicitnou neistotou.
- **Všetci skúšajú zmeny —** parallel actions menia observations a môžu sa zosilniť. Každá mutation potrebuje hypothesis, ownera a log.
- **Chat je incident state —** critical decisions a current truth sa stratia, čo poškodí handoff a stakeholder alignment.
- **Zelený endpoint znamená recovered —** backlog, incorrect outcomes alebo historical data damage môžu pokračovať.
- **Incident končí po mitigation —** temporary override sa stane permanentným hidden riskom bez recovery a recurrence closure.

## 14. Kontrolné otázky

1. Čo tvorí exact incident subject?
2. Kedy normal troubleshooting prechádza na incident režim?
3. Ako severity vyjadruje impact a uncertainty?
4. Prečo IC nemusí byť najhlbší expert?
5. Čo musí obsahovať authoritative incident state?
6. Ako sa stabilization líši od remediation?
7. Čo potrebuje bounded incident change?
8. Prečo parallel mitigations poškodili `SRE-PAY-53`?
9. Ako communication oddeľuje facts a hypotheses?
10. Čo musí preniesť handoff?
11. Ako sa technical recovery líši od business recovery?
12. Ktoré positive, recovery a forbidden paths patria do acceptance?

## Glossary impact

Relevantné pojmy: incident subject, declaration transition, severity contract, Incident Commander, Operations/Communications/Planning lead, authoritative incident state, stabilization, bounded incident change, command continuity, recovery criteria, recurrence watch a incident acceptance contract.

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
