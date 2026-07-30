# Toil

Toil je operational work priamo viazaný na udržiavanie služby, ktorý je prevažne manuálny, opakovaný, automatizovateľný, reaktívny, bez trvalej hodnoty a rastie so scale alebo complexity. Nie každá manuálna alebo nepríjemná úloha je toil. Novel incident diagnosis môže vytvoriť nové engineering knowledge a jednorazová náročná migrácia môže odstrániť budúci demand. Rozhodujúci je workflow, jeho opakovanie a to, či po vykonaní zostáva production mechanismus nezmenený.

Cieľom nie je automatizovať každé ľudské rozhodnutie. Cieľom je odstrániť operational demand alebo ho previesť na bezpečný, škálovateľný a auditovateľný mechanismus. Automatizácia unsafe workflowu môže zrýchliť incident rovnako ako jeho opravu.

## 1. Dominantný demand-to-elimination model

Toil treba analyzovať ako feedback loop. Production alebo process condition vytvorí demand, demand vstúpi do queue alebo preruší on-call, človek dočasne obnoví state a pôvodná condition zostane. Bez zásahu sa loop opakuje a spotrebúva engineering capacity.

```text
production/process condition
→ operational demand a trigger
→ exact human workflow a privileges
→ queue, interruption a touch time
→ temporary state restoration
→ condition zostáva
→ recurrence a scale growth
→ eliminate/redesign/automate/self-service/accept decision
→ guarded implementation
→ residual human path
→ recurrence, risk a capacity validation
```

Najlepšie riešenie často neleží v poslednom manuálnom kroku. Ak broker outage stále vytvára unbounded backlog, automatické spustenie cleanup SQL neodstráni demand; iba odstráni človeka z nebezpečného loopu.

## 2. Exact toil subject

„Máme veľa toil-u“ neposkytuje action. Exact subject zachováva service, capability, trigger, actor, workflow steps, frequency, human touch time, elapsed wait, interruptions, required privilege, error risk, scale driver, current automation, ownera a measurement window.

```text
subject: TOIL-PAY-52-outbox-recovery
service: atlas-settlement-api
trigger: unpublished outbox age > 20 min
actors: primary on-call + database operator
frequency: 11× / 28 dní
median touch: 38 min
p95 elapsed: 94 min
privilege: production SQL write + deployment scale
scale driver: broker failures × settlement volume
risk: lost intent, duplicate replay, support delay
```

Workflow identity je dôležitejšia než všeobecné timesheet percento. Dve aktivity môžu mať rovnaký touch time, ale jedna je low-risk certificate inventory a druhá privileged data mutation s customer impactom.

## 3. Classification: toil, engineering a overhead

Práca je silným toil kandidátom, keď kombinuje viac vlastností: opakuje sa, vyžaduje rovnaké manuálne kroky, reaguje na aktuálny stav, môže byť mechanizovaná, po dokončení nevytvára enduring improvement a jej množstvo rastie s trafficom, tenants alebo fleet size.

Engineering work vytvára durable capability alebo znižuje budúci demand. Môže byť manuálne a neatraktívne. Jednorazová migrácia alert ownershipu do versionovaného catalogu je grungy engineering; ručná oprava rovnakých routes každý týždeň je toil.

Overhead je administratívna práca, ktorá nie je priamo viazaná na prevádzku konkrétnej služby. Môže byť nadmerná, ale potrebuje iný improvement mechanismus. On-call ako celok tiež nie je toil: novel diagnosis, risk judgment a incident command sa odlišujú od opakovaného runbook executionu.

## 4. Demand source a reinforcing loop

Toil má upstream source. Môže ho vytvárať unreliable service, alert noise, chýbajúci self-service, unsafe release, manual access approval, configuration drift, capacity shortage, neúplný inventory alebo product behavior presúvajúci prácu na operations.

```text
viac incidents a manual interventions
→ menej času na engineering
→ menej root-cause a platform improvements
→ viac latentných defects
→ ešte viac incidents a interventions
```

Toil budget má chrániť engineering capacity pred týmto reinforcing loopom. Google SRE používa vlastný organizačný cieľ, aby operational work dlhodobo neprekročil približne polovicu času; nie je to univerzálna norma, ktorú treba kopírovať bez local staffing a service contextu.

## 5. Measurement: volume, time a risk

Toil inventory kombinuje occurrences, human touch time, elapsed lead time, interruptions, počet actors, privilege, error rate, after-hours share, customer wait, growth rate a opportunity cost.

```text
Workflow                    Occ/28d   Touch   Total   Primary risk
Outbox backlog recovery     11        38m     418m    lost/duplicate intent
Certificate renewal         7         22m     154m    auth outage
False queue alert triage    64        6m      384m    alert fatigue
```

Najväčší počet hodín nemusí mať najvyššiu prioritu. Low-frequency workflow s production write accessom a možnosťou zmazať potvrdené operations môže byť kritickejší než stovky bezpečných read-only tickets. Prioritization preto kombinuje annualized cost, interruption, user/reliability risk, growth a tractability.

Measurement nesmie byť surveillance nad jednotlivcami. Cieľom je identifikovať system demand, nerovnomernú distribúciu a investment opportunity, nie odmeňovať človeka, ktorý vykazuje viac incident hodín.

## 6. Elimination strategy order

Riešenie sa vyberá podľa toho, kde možno bezpečne prerušiť demand loop. Najvyššiu hodnotu má odstránenie upstream condition; automatizácia posledného kroku je vhodná až vtedy, keď demand zostáva legitímny a decision možno formalizovať bez skrytia uncertainty.

Poradie zároveň vyjadruje trade-off medzi trvalým znížením práce a nákladom na redesign. Tím môže zvoliť partial automation alebo bounded acceptance, ale musí explicitne uviesť, prečo root-demand elimination zatiaľ nie je primerané a aký residual toil zostáva.

1. **Eliminate root demand** — oprav failure mechanismus, aby trigger nevznikal.
2. **Redesign service contract** — pridaj backpressure, idempotency, bounded state machine alebo safer ownership.
3. **Full automation** — software bezpečne pozoruje, rozhodne, vykoná a overí outcome.
4. **Partial automation** — software pripraví evidence a plan, človek schváli iba risk-relevantný transition.
5. **Self-service** — consumer vykoná scoped operation bez central ticketu.
6. **Standardize alebo delegate** — odstráň special cases a presuň authority k správnemu ownerovi.
7. **Bounded acceptance** — ak cost prevyšuje benefit, zachovaj ownera, budget a review trigger.

Automatizovať treba až po vysvetlení authority, preconditions a failure semantics. Runbook s vetami „vyber staré rows“ alebo „reštartuj podľa potreby“ nemá dostatočný contract na bezpečnú automatizáciu.

## 7. Automation safety contract

Automation zväčšuje execution speed a blast radius. Potrebuje authoritative input, freshness, exact subject, maximum scope, idempotency, concurrency limit, dry-run alebo plan, approval boundary, unknown-outcome behavior, compensation, audit a kill switch.

```text
observe exact subject
→ validate generation a preconditions
→ calculate bounded plan
→ optional risk approval
→ idempotent apply
→ read-back effective state
→ business outcome validation
→ stop/compensate/escalate
```

Automatický cleanup, ktorý zmaže všetky rows staršie než threshold, nie je toil reduction. Je to unsupervised destructive control bez business oracle. Bezpečná automation má radšej zastaviť a eskalovať ambiguous cohort než optimalizovať throughput za cenu data lossu.

## 8. Connected incident `SRE-PAY-52`

Outbox backlog recovery sa za 28 dní vykonala `11×`. On-call otvoril dashboard a SQL console, vybral rows staršie než 30 minút, zvýšil workers, spustil cleanup a reštartoval publisher. Median touch time bol `38 minút`, spolu `418 minút` privileged worku.

Runbook neodstraňoval broker partition, unbounded backlog ani unsafe retention contract. Každé vykonanie dočasne znížilo queue a pripravilo ďalšie opakovanie. Dňa 29. júla cleanup query zmazala `4 182` unpublished commands a vytvorila data-loss incident.

Toil nebol iba staffing problém. Bol causal amplifier:

```text
opakovaný incident demand
→ normalizovaný privileged runbook
→ pressure na rýchle queue reduction
→ ambiguous age-based cleanup
→ chýbajúca plan a business oracle
→ destructive execution
```

Automatizovať pôvodnú query by incident urýchlilo. Správny redesign musel zmeniť service a recovery contract.

## 9. Redesign outbox recovery

Nový model zaviedol bounded backlog admission, immutable retention invariant a reconciler:

```text
broker slowdown
→ backlog-age a provider-capacity signal
→ automatic bounded backpressure
→ unpublished rows nikdy nemaže retention
→ publisher používa leases a idempotent attempts
→ reconciler porovná payment/outbox/broker/provider
→ classified recovery plan
→ human approval iba pre unknown high-risk cohort
→ execution s operation-level audit
```

Routine healthy cohorts sa obnovujú automaticky. Unknown provider outcomes ostávajú fenced, kým reconciliation neurčí, či replay vytvorí duplicate. On-call už nemusí písať SQL; dostáva exact incident subject, plan, estimated impact a safe action choices.

Residual human work zostáva pre novel failure, business exception a authority decision. To nie je zlyhanie automation. Cieľom je odstrániť deterministic repeat work a zachovať ľudský judgment tam, kde uncertainty skutočne mení risk.

## 10. Toil-reduction acceptance contract

Positive acceptance musí preukázať, že pôvodný trigger buď nevzniká, alebo sa spracuje bez opakovaného privileged touchu. Automation musí vytvoriť rovnaký alebo lepší business outcome, nie iba nižší ticket count. Meranie po nasadení porovná recurrence, touch time, customer wait, error budget a incident risk.

Forbidden paths musia zlyhať. Automation nesmie konať nad stale subjectom, prekročiť cohort limit, zmazať unpublished command, replayovať unknown provider operation ani skryť failure odstránením alertu. Kill switch a manual fallback musia fungovať bez návratu k ad-hoc SQL.

```text
positive:
known safe backlog → bounded plan → recovery → zero privileged touch

human judgment:
unknown provider state → fenced cohort → evidence + approval

forbidden:
stale plan apply
unbounded delete
duplicate external effect
alert suppression as toil reduction
manual fallback without audit
```

Druhý broker-failure test musí potvrdiť, že reduction pretrváva aj mimo pôvodného incidentu.

## 11. Troubleshooting toil programu

Ak toil neklesá po automation projekte, odlíš tri hypotézy: demand zostal, ale execution je rýchlejší; automation pokrýva iba časť cohortov; alebo measurement presunulo work do iného tímu či queue.

```text
expected reduction
→ exact workflow a demand source
→ before/after occurrence inventory
→ human touch a elapsed time
→ exception/fallback cohort
→ downstream alebo shifted work
→ reliability/business outcome
→ root mechanism verdict
```

Pokles on-call času pri raste customer wait alebo support tickets nie je úspech. Rovnako odstránený alert pri nezmenenom failure-u iba skryl demand.

## 12. Anti-patterny

Toil anti-patterny optimalizujú viditeľnosť alebo ownership práce bez odstránenia demandu a risku. Program preto hodnotí end-to-end occurrence, human touch, customer wait a reliability outcome, nie iba počet tickets jedného tímu.

- **Automatizuj každý manuálny krok —** Manual work môže obsahovať risk judgment. Najprv oddel deterministic execution od ambiguous decisionu a zachovaj fenced human path pre uncertainty.
- **Toil equals celé on-call —** Novel diagnosis a incident command nie sú rovnaké ako opakovaný runbook. Inventory musí klasifikovať konkrétne workflows, nie celú službu v rotačnom kalendári.
- **Počítaj iba hodiny —** Nízkoobjemový destructive workflow môže mať vyššiu prioritu než častá low-risk práca. Prioritization kombinuje volume, privilege, blast radius a growth.
- **Presuň ticket inému tímu —** Organizačný transfer nemení system demand ani customer wait. Úspech vyžaduje pokles end-to-end worku alebo jasný transfer authority a capability.
- **Odstráň alert —** Ak failure pokračuje, zníženie page countu nie je toil reduction. Alert možno zmeniť až spolu s detection contractom a dôkazom, že user risk neklesol iba z observability.

## 13. Kontrolné otázky

1. Čo tvorí exact toil subject?
2. Ktoré vlastnosti odlišujú toil od engineering worku?
3. Prečo on-call nie je automaticky celý toil?
4. Ako vzniká reinforcing loop medzi toilom a menším engineering časom?
5. Prečo prioritization potrebuje risk aj touch time?
6. Aké je poradie elimination strategies?
7. Kedy partial automation dáva väčší zmysel než full automation?
8. Čo musí obsahovať automation safety contract?
9. Prečo pôvodný runbook v `SRE-PAY-52` bol causal amplifier?
10. Ako overiť, že work nebol iba presunutý?
11. Ktoré forbidden paths musí toil-reduction test odmietnuť?
12. Prečo je potrebný second-trigger test?

## Glossary impact

Relevantné pojmy: toil subject, operational demand, human touch time, interruption cost, toil reinforcing loop, toil budget, elimination strategy, partial automation, automation safety contract, residual human path, shifted toil a toil-reduction acceptance contract.

## Primárne zdroje

- [Google SRE — Eliminating Toil](https://sre.google/sre-book/eliminating-toil/)
- [Google SRE Workbook — Eliminating Toil](https://sre.google/workbook/eliminating-toil/)
- [Google SRE — The Evolution of Automation at Google](https://sre.google/sre-book/automation-at-google/)
- [Google SRE — Dealing with Interrupts](https://sre.google/sre-book/dealing-with-interrupts/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Error budgets](error-budgets.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Capacity planning →](capacity-planning.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
