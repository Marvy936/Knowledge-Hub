# Feedback Loops

Feedback loop je mechanizmus, ktorý z pozorovaného výsledku vytvorí korekciu budúceho správania. Potrebuje sensor alebo observation point, interpretáciu voči očakávaniu, ownera rozhodnutia a actuator, ktorý vie zmeniť systém. Samotný dashboard alebo notifikácia ešte feedback loop nevytvára.

```text
zmena alebo disturbance
→ pozorovanie
→ porovnanie s cieľom alebo invariantom
→ rozhodnutie
→ korekčná akcia
→ nové pozorovanie
```

Kvalitu loopu určujú najmä latency, signal fidelity, scope a authority. Rýchly, ale nesprávny test môže poskytovať škodlivý feedback. Presný incident report doručený o tri mesiace neskôr už nemusí ovplyvniť pôvodné rozhodnutie. Alert bez ownera vytvára noise, zatiaľ čo automatický controller bez safety limits môže zosilniť chybný signál.

Balancing loop smeruje systém k cieľu, napríklad autoscaler pridávajúci kapacitu pri raste queue age. Reinforcing loop sám seba zosilňuje, napríklad timeouty vyvolávajúce retries, ktoré ešte viac preťažia dependency. Diagnostika preto musí rozlíšiť, aký typ loopu pozorujeme a kde možno bezpečne zmeniť jeho gain, delay alebo boundary.

## 1. Definícia

Feedback loop je uzavretý mechanizmus, v ktorom sa informácia o výsledku akcie vracia k človeku alebo automatizovanému controlleru a ovplyvní ďalší krok. Informácia sama osebe nestačí; musí existovať porovnanie s cieľom, rozhodnutie a pozorovanie účinku korekcie.

V DevOps feedback loops vznikajú pri editovaní kódu, code review, CI, deployment-e, production monitoring-u, incidente aj retrospektíve. Ich kvalita určuje, ako rýchlo a presne sa systém dokáže priblížiť k požadovanému outcome-u.

## 2. Problém, ktorý feedback rieši

Bez feedbacku nevieme, či akcia priniesla očakávaný výsledok alebo vytvorila novú odchýlku. Tím môže nasadiť zmenu, dokončiť ticket a pritom nevedieť, či používatelia dostávajú správny výsledok alebo či sa iba presunul failure do ďalšej dependency.

Oneskorený feedback zvyšuje correction cost. Čím viac ďalšieho code-u, decisions a rolloutov vznikne na chybnom predpoklade, tým zložitejšie je problém izolovať a bezpečne opraviť.

```text
akcia alebo zmena
→ systém reaguje
→ výsledok sa zmeria
→ porovná sa s cieľom alebo baseline
→ vykoná sa korekcia
→ zmeria sa nový stav
```

Ak posledný krok chýba, tím nevie, či remediation skutočne fungovala. Loop zostáva otvorený aj vtedy, keď existuje alert a ticket.

## 3. Anatomia feedback loopu

Použiteľný feedback loop obsahuje viac častí, ktoré musia mať presný contract. Slabosť ktorejkoľvek časti môže vytvoriť nečinnosť, prehnanú reakciu alebo falošný pocit kontroly.

- **Target alebo desired state — očakávaný výsledok**: môže byť passing contract test, SLO, počet replicas alebo business conversion boundary.
- **Action alebo disturbance — zmena ovplyvňujúca systém**: deployment, traffic spike, configuration change alebo component failure vytvorí novú situáciu.
- **Observation — measurement skutočného stavu**: test result, metric, log, trace alebo user feedback poskytne dostupné evidence.
- **Comparison — vyhodnotenie odchýlky**: controller alebo človek rozhodne, či je rozdiel relevantný, v tolerancii alebo vyžaduje zásah.
- **Correction — úprava ďalšieho správania**: rollback, scale-out, code fix, zmena policy alebo nový backlog item má zmenšiť odchýlku.
- **Verification — potvrdenie účinku korekcie**: rovnaký alebo doplnkový signal ukáže, či sa systém skutočne vrátil do požadovaného stavu.

## 4. Príklad reconciliation loopu

Kubernetes controller používa desired a observed state na opakovanú korekciu. Desired state `replicas = 3` je uložený v API, controller pozoruje iba dve dostupné replicas a vytvorí ďalší Pod.

```text
desired replicas = 3
observed available replicas = 2
→ controller vypočíta rozdiel
→ vytvorí nový Pod
→ scheduler a kubelet vykonajú prácu
→ controller znovu pozoruje stav
```

Controller nevie garantovať okamžité splnenie. Scheduling môže zlyhať pre nedostatok capacity alebo image pull, preto loop potrebuje retries, events, conditions a explicitné failure evidence.

## 5. Human a automated loops

Automated loop reaguje podľa machine-readable policy a môže vykonávať korekciu často a konzistentne. Autoscaler, deployment controller alebo circuit breaker preto potrebuje presné thresholds, stabilization a bezpečné limits.

Human loop dokáže interpretovať širší context a neznámu situáciu, ale má vyššiu latency a variabilitu. Incident responder môže rozhodnúť, že technically healthy replica obsahuje poškodené dáta a automatický failover by situáciu zhoršil.

Produkčný systém často kombinuje oba modely. Automation rieši bežnú cestu a vopred modelované failures, zatiaľ čo človek preberá ambiguous state alebo vysoký business risk.

## 6. Negative feedback

Negative feedback znižuje odchýlku a stabilizuje systém. Názov neznamená nepriaznivú informáciu; opisuje smer reakcie proti pôvodnej zmene.

```text
error rate prekročí rollout boundary
→ canary controller zastaví exposure
→ traffic sa vráti na stable version
→ error rate klesne
```

Loop je stabilný iba vtedy, keď signal koreluje s canary zmenou a rollback je kompatibilný s data state-om. Falošný alert môže blokovať zdravú verziu a príliš pomalá reakcia môže vystaviť väčšinu používateľov.

## 7. Positive feedback

Positive feedback zosilňuje aktuálny trend. Môže byť žiaduci, napríklad adoption užitočnej platformy, alebo deštruktívny, napríklad retry storm.

```text
viac timeoutov
→ viac client retries
→ vyšší downstream load
→ ešte viac timeoutov
```

Pri zosilňujúcom loop-e nestačí opraviť jeden symptom. Potrebné sú limits, backoff, load shedding alebo isolation, ktoré prerušia mechanizmus amplification.

## 8. Feedback latency

Feedback latency je čas od vzniku udalosti po okamih, keď relevantný actor dostane použiteľný signal a môže konať. Zahŕňa collection, processing, routing aj waiting na rozhodnutie.

Rovnaký YAML syntax error môže byť odhalený v rôznych loops:

- **Editor validation — sekundy**: autor má plný mental context a oprava je lacná.
- **Pre-commit hook — desiatky sekúnd**: chyba ešte neopustila lokálny workflow, ale kontrola je konzistentnejšia.
- **CI pipeline — minúty**: shared environment poskytne dôveryhodnejšie evidence, no autor už môže pracovať na ďalšej zmene.
- **Staging deployment — desiatky minút až hodiny**: odhalí integration alebo runtime problém po vytvorení artifactu a environment state-u.
- **Production incident — hodiny alebo dni**: chyba už môže ovplyvniť používateľov, data a ďalšie releases.

Najskorší možný loop nie je vždy autoritatívny. Production-only behavior stále potrebuje shift-right signal, ale známe syntax alebo policy chyby nemajú čakať na runtime.

## 9. Vlastnosti kvalitného feedbacku

Kvalita je viacrozmerná. Optimalizácia iba jednej vlastnosti môže zhoršiť celý loop, napríklad ultrarýchly test s vysokou flaky rate.

- **Timeliness — signal príde pred nevratným alebo drahým rozhodnutím**: feedback po plnom rollout-e už nemôže obmedziť pôvodný blast radius.
- **Accuracy — signal reprezentuje skutočný stav**: false positives vytvárajú noise a false negatives falošnú dôveru.
- **Context — evidence vysvetľuje scope a súvislosti**: version, environment, operation a recent change umožnia začať diagnosis na správnej boundary.
- **Actionability — existuje ďalší bezpečný krok**: owner vie zmenu zastaviť, rollbacknúť, eskalovať alebo vytvoriť presný fix.
- **Correct recipient — signal dostane actor s authority**: report odoslaný do nečítaného channelu nie je funkčný feedback.
- **Verifiability — loop potvrdí výsledok zásahu**: po remediation sa zmeria recovery a nevychádza sa iba zo statusu commandu.
- **Cost proportionality — získanie evidence je primerané risku**: drahý full-scale test pri každom typo môže flow poškodiť viac, než znižuje neistotu.

## 10. Signal, noise a trust

Signal je informácia relevantná pre rozhodnutie, zatiaľ čo noise spotrebúva pozornosť bez dostatočnej väzby na outcome. Ratio závisí od contextu; jeden warning môže byť kritický pri security boundary a bezvýznamný pri očakávanom transientnom retry.

Feedback trust sa buduje konzistentným behaviorom. Flaky test, stovky neakčných alerts alebo pipeline zlyhávajúca pre nestabilný runner naučia ľudí výsledok ignorovať alebo automaticky retryovať bez diagnosis.

Typické noise sources majú odlišnú nápravu:

- **Flaky test — nondeterministic setup alebo timing**: quarantine bez ownera iba skryje risk; treba odstrániť race, shared state alebo environment variability.
- **Alert storm — príliš jemná identity a grouping**: page per Pod nahradí symptom jednej služby stovkami notifications.
- **Dashboard bez threshold-u — data bez decision contractu**: viewer nevie, kedy je zmena významná alebo kto má reagovať.
- **Logs bez correlation identity — neprepojiteľné events**: diagnosis vyžaduje manuálne časové odhady a stráca causal path.
- **Infrastructure-induced CI failures — feedback o platforme namiesto code-u**: pipeline musí rozlíšiť test failure od runner, network alebo registry incidentu.

## 11. Measurement completeness

Feedback vychádza iba z pozorovateľnej časti reality. Absencia erroru môže znamenať zdravie, nulový traffic alebo nefunkčnú telemetry pipeline.

Každý signal potrebuje completeness contract: ktoré operations zahŕňa, aké sampling sa používa, čo sa stane pri no-data a ktorá boundary je autoritatívna. Bez neho controller alebo človek môže reagovať na neúplný obraz.

Napríklad nulový payment error rate je dobrá správa iba vtedy, ak payment attempts skutočne prichádzajú a numerator aj denominator sa merajú na rovnakej business boundary.

## 12. Gain a sila reakcie

Gain opisuje veľkosť korekcie voči nameranej odchýlke. Príliš slabá reakcia ponechá systém mimo cieľa, zatiaľ čo príliš silná môže vytvoriť overshoot a oscillation.

Autoscaler, ktorý pri veľkom backlogu pridá jedného pomalého workera, nemusí dohnať arrival rate. Autoscaler, ktorý po krátkom spike-u pridá stovky instances a následne ich okamžite odoberie, zvyšuje cost, cold starts a nestabilitu.

Sila reakcie sa riadi thresholds, step size, rate limits a maximum capacity. Tieto controls musia zohľadňovať provisioning latency a reálny bottleneck, inak controller koriguje stale state.

## 13. Delay, sampling a oscillation

Delay medzi action a observed effectom komplikuje control. Ak sa nová kapacita warmuje päť minút, autoscaler nesmie počas tohto času opakovane vyhodnotiť nezmenenú metric ako potrebu ďalšieho rovnakého scale-outu bez limitu.

Sampling interval ovplyvňuje, ktoré zmeny sú viditeľné. Príliš riedky scrape prehliadne krátke saturation spikes a príliš časté noisy samples môžu vyvolať reakciu na bežnú variabilitu.

Stabilization window, cooldown, moving average a multi-window evaluation znižujú oscillation. Ich cena je vyššia detection alebo correction latency, preto sa nastavujú podľa dynamiky workloadu.

## 14. Hysteresis a deadband

Hysteresis používa odlišnú hranicu pre zapnutie a vypnutie reakcie. Napríklad scale-out začne pri queue age nad desať minút, ale scale-in až po poklese pod dve minúty počas stabilného okna.

Deadband je tolerančné pásmo, v ktorom controller nereaguje na malú odchýlku. Oba mechanizmy zabraňujú flappingu pri hodnotách oscilujúcich tesne okolo jedného threshold-u.

Príliš široký deadband však môže maskovať reálnu degradáciu. Boundary sa preto overuje na historickom aj failure workload-e.

## 15. Local development loop

Lokálny loop je najčastejšie opakovaná spätná väzba autora. Edit, lint, compile a unit tests majú byť dostatočne rýchle, aby človek neotváral ďalšiu prácu počas čakania.

```text
edit
→ format a static validation
→ focused test
→ presný failure alebo success
→ ďalšia úprava
```

Lokálny loop nemá predstierať úplné production evidence. Jeho úlohou je lacno odstraňovať chyby v boundaries, ktoré dokáže dôveryhodne simulovať.

## 16. Code review loop

Code review vracia feedback o change intent-e, architecture, readability, tests a operational risku. Latency loopu ovplyvňuje veľkosť change-u, reviewer capacity a jasnosť ownershipu.

Review comment typu „toto sa mi nepáči“ má nízku actionability. Kvalitný feedback pomenuje affected contract, risk alebo alternatívu a rozlišuje required fix od návrhu na zlepšenie.

Automated formatting a known policy checks majú prebehnúť pred human review. Reviewer potom používa pozornosť na context a trade-offs, ktoré automation nevie spoľahlivo posúdiť.

## 17. CI loop

CI vytvára shared, opakovateľný feedback nad konkrétnym source revisionom. Build, tests a scans majú presne ukázať, ktorý input a rule vytvorili výsledok.

Pipeline latency treba posudzovať podľa poradia rozhodnutí. Rýchle high-value checks sa spúšťajú skoro a nezávislé jobs paralelne, zatiaľ čo drahé broad tests môžu nasledovať po základnej validácii alebo v scheduled path-e podľa risku.

CI zlyhanie musí rozlišovať:

- **Code alebo test failure — zmena porušila contract**: autor potrebuje konkrétny assertion, file alebo affected component.
- **Policy failure — zmena porušila guardrail**: report má ukázať pravidlo, resource a povolenú remediation alebo exception path.
- **Infrastructure failure — execution environment nebol dostupný**: retry môže byť vhodný, ale výsledok sa nesmie zamieňať za quality failure source-u.
- **Flaky alebo unknown failure — feedback nie je dôveryhodný**: potrebuje ownera a odstránenie nondeterminismu, nie permanentné slepé retry.

## 18. Deployment a rollout loop

Deployment loop porovnáva požadovanú release verziu s runtime state-om a overuje, či nový artifact dokáže bezpečne obsluhovať traffic. Readiness samotná nestačí; application alebo business smoke test musí overiť relevantný outcome.

Progressive rollout vytvára krátky loop medzi exposure a telemetry:

```text
release malému cohortu
→ porovnanie canary a baseline
→ decision threshold
→ pokračovať, pozastaviť alebo rollback
→ znovu zmerať outcome
```

Ak telemetry nerozlišuje version alebo cohort, canary nemá autoritatívny feedback. Ak rollback nie je data-compatible, correction action môže vytvoriť ďalší failure.

## 19. Production operations loop

Production loop začína user alebo system behaviorom a končí zmenou runtime-u alebo source-u. Monitoring deteguje known conditions, observability podporuje investigation a incident process koordinuje risk a authority.

```text
user impact alebo system signal
→ detection
→ triage a hypothesis
→ mitigation
→ validation recovery
→ permanent fix alebo improvement
```

Mitigation a permanent fix sú odlišné. Reštart môže obnoviť službu, ale loop učenia zostáva otvorený, kým sa neodstráni memory leak, nepridá test alebo nezmení capacity model.

## 20. Organizational learning loop

Retrospective a post-incident review vytvárajú feedback o procese a architecture. Loop sa uzatvára až implementáciou action a overením, že zmenila behavior alebo risk.

```text
incident evidence
→ systemic analysis
→ prioritized action s ownerom
→ implementation
→ test alebo runtime verification
→ update standardu a knowledge
```

Postmortem document bez ownera, deadline-u a effectiveness review je iba uložená informácia. Nevytvára korekciu systému.

## 21. Shift-left

Shift-left umiestňuje kontrolu bližšie k vzniku relevantnej zmeny. Cieľom je znížiť feedback latency a correction cost, nie preniesť všetku expertízu a zodpovednosť na developera.

Mechanizmy majú vysvetlenú boundary:

- **Linting — syntax a source conventions pri editovaní**: odhaľuje lacné chyby pred commitom, ale nepozná runtime dependencies.
- **Static analysis — known code patterns bez execution**: môže zachytiť vulnerability alebo bug class, no potrebuje triage false positives.
- **Unit tests — isolated behavior pred integráciou**: poskytujú rýchly feedback, ale mocks nemusia reprezentovať skutočný service contract.
- **Policy checks — machine-readable guardrails pri source alebo plan-e**: blokujú nepovolenú configuration pred vytvorením blast radiusu.
- **Security scanning — known dependency a artifact findings**: znižuje čas do discovery, ale nepreukazuje exploitability ani kompletný threat model.

## 22. Shift-right

Shift-right pokračuje vo validácii po nasadení, pretože reálny traffic, scale a dependencies nemožno úplne simulovať. Produkcia nie je náhradou základného testovania; je ďalšou autoritatívnou boundary pre určité assumptions.

- **Metrics a traces — runtime performance a causal paths**: ukazujú reálny behavior, ale závisia od instrumentation a sampling contractu.
- **Synthetic tests — pravidelný user-path probe**: zachytia availability aj pri nízkom trafficu, no nemusia reprezentovať všetkých používateľov.
- **Canary analysis — porovnanie novej a stabilnej verzie**: obmedzuje exposure, ak cohort a baseline zostávajú porovnateľné.
- **Real user monitoring — skutočná client experience**: odhaľuje geography, browser a network variabilitu, ale potrebuje privacy a sampling governance.
- **Chaos experiments — overenie resilience hypothesis**: poskytujú evidence o failure behavior, ak majú steady state, abort a recovery.

## 23. Leading indicators

Leading indicator signalizuje vznikajúci risk skôr, než sa prejaví konečný user alebo business dopad. Môže umožniť preventívnu akciu, ale často je menej priamo naviazaný na outcome a vyžaduje context.

Príklady vysvetľujú, čo predpovedajú:

- **Rast queue age — processing nestíha business deadline**: môže predchádzať timeoutom alebo nedoručeným výsledkom.
- **Rast latency pri stabilnom trafficu — približovanie k saturation alebo dependency slowdown**: signalizuje znižujúci sa headroom.
- **Pokles cache hit rate — vyšší load na origin alebo database**: môže viesť k neskoršej latency a cost degradácii.
- **Rast failed deployments — slabnúca delivery quality**: môže predchádzať production incidentom alebo zväčšovaniu release batchov.

Leading signal nemá byť page iba preto, že sa mení. Potrebuje validovanú väzbu na risk a konkrétnu action.

## 24. Lagging indicators

Lagging indicator opisuje dopad, ktorý už nastal. Je bližšie user outcome-u, ale môže prísť príliš neskoro na prevenciu.

- **SLA alebo SLO breach — reliability contract bol porušený**: poskytuje jasný outcome, no remediation už rieši existujúci dopad.
- **Customer complaint — používateľ pozoroval problém**: môže odhaliť semantic failure, ktorý technická telemetry nezachytila, ale signal je oneskorený a neúplný.
- **Outage — služba nedokáže poskytovať kritický outcome**: je autoritatívny dopad, nie skorý capacity signal.
- **Data loss — integrity alebo durability failure sa materializoval**: vyžaduje recovery a často business notification, preto je prevencia cez leading controls kritická.

Zdravý model kombinuje leading a lagging signals. Leading chráni pred známym riskom a lagging overuje, či ochrana skutočne koreluje s user outcome-om.

## 25. Praktický príklad pomalej CI spätnej väzby

Pipeline trvá 55 minút a developer počas čakania otvorí ďalšiu zmenu. Pri failure už nemá plný mental context a WIP rastie.

Rozklad ukáže:

```text
lint:               2 min
unit tests:          6 min
image build:        12 min
integration tests:  30 min
security scan:       5 min
```

Zlepšenia musia vysvetliť mechanismus a zachovať dôveryhodnosť:

- **Paralelizovať nezávislé jobs — skrátiť critical path**: unit tests, build a scan sa môžu prekrývať iba vtedy, ak nepotrebujú výsledok predchádzajúceho kroku.
- **Cache a incremental build — odstrániť opakovanú transformáciu nezmenených vstupov**: cache key musí obsahovať dependencies, inak vytvorí stale alebo nesprávny artifact.
- **Fast commit pipeline a deeper scheduled path — rozdeliť rozhodnutia podľa latency a risku**: merge gate používa rýchle high-value evidence a broad tests stále pravidelne chránia širší scope.
- **Affected-component test selection — zmenšiť test scope podľa dependency graphu**: nepresný graph môže vynechať relevantný consumer, preto potrebuje validation.
- **Odstrániť flaky tests — zvýšiť trust namiesto slepého retry**: nondeterminism sa meria a opravuje pri source, environment alebo timing boundary.

Cieľom nie je najkratšia pipeline za každú cenu. Cieľom je najskorší dôveryhodný signal pre aktuálne rozhodnutie.

## 26. Návrh feedback loopu

Návrh začína rozhodnutím, nie metricou. Až potom sa vyberie signal, latency, actor a bezpečná korekcia.

1. **Aké rozhodnutie má loop podporiť?** — napríklad povoliť rollout, pridať capacity alebo eskalovať incident.
2. **Aký target alebo contract sa porovnáva?** — SLO, test expectation alebo desired state musí mať stabilnú semantics.
3. **Ktorý signal reprezentuje observed state?** — treba poznať boundary, sampling, freshness a no-data behavior.
4. **Aká feedback latency je ešte použiteľná?** — signal musí prísť pred decision deadline-om alebo nevratným dopadom.
5. **Kto alebo čo reaguje?** — actor potrebuje access, authority a ownership.
6. **Aká korekcia je bezpečná a primeraná?** — reaction gain, limits a recovery chránia pred overcorrection.
7. **Ako sa obmedzí noise a oscillation?** — grouping, thresholds, hysteresis a stabilization musia zodpovedať dynamike systému.
8. **Ako sa overí účinok?** — po action sa zmeria nový outcome a loop sa explicitne uzavrie.

## 27. Anti-patterny

### Feedback bez ownera

Report alebo alert existuje, ale nikto nemá povinnosť ani authority reagovať. Informácia sa uloží bez zmeny správania.

### Feedback príliš neskoro

Architecture risk sa odhalí pri release review po mesiacoch implementation. Oprava vyžaduje redesign a coordinated rework namiesto malej zmeny pri planningu.

### Feedback bez contextu

Alert `CPU high` neuvádza service, duration, saturation, user impact ani recent change. Responder musí najprv zistiť, či signal vôbec súvisí s incidentom.

### Metrika ako cieľ

Tím optimalizuje test coverage alebo deployment count bez sledovania failure a outcome-u. Číslo rastie, no feedback o kvalite systému sa zhoršuje.

### Neuzavreté nápravné opatrenia

Retrospective identifikuje problém, ale action nemá ownera, termín ani verification. Loop končí poznámkou namiesto korekcie.

### Automatický loop bez limits

Controller reaguje na chybný alebo stale signal a vykonáva rozsiahle zmeny bez maximum, cooldownu alebo abort condition. Automation potom zosilňuje pôvodnú poruchu.

## 28. Kontrolné otázky

1. Ktoré časti musí obsahovať uzavretý feedback loop?
2. Prečo signal bez korekcie a verification nie je kompletný loop?
3. Aký je rozdiel medzi negative a positive feedbackom?
4. Ako feedback latency ovplyvňuje correction cost?
5. Prečo rýchly flaky test môže byť horší než pomalší dôveryhodný test?
6. Čo znamená gain a ako vytvára overshoot alebo oscillation?
7. Ako hysteresis a deadband stabilizujú controller?
8. Aký je rozdiel medzi local, CI, rollout a production loopom?
9. Prečo shift-left a shift-right nie sú konkurenčné stratégie?
10. Ako leading a lagging indicators spolu chránia user outcome?
11. Aký completeness contract potrebuje no-data alebo sampled signal?
12. Ako navrhneš feedback loop od rozhodnutia po overenie účinku?

## 29. Zhrnutie

Feedback loop spája target, action, observation, comparison, correction a verification. Jeho hodnota závisí od latency, accuracy, contextu, actionability, správneho recipienta a známeho completeness contractu.

DevOps používa viac vnorených loops od editora po production a organizational learning. Zdravý systém presúva známe kontroly do skorších boundaries, pokračuje runtime validáciou, obmedzuje noise a nastavuje reaction gain tak, aby korekcia stabilizovala systém namiesto vytvárania oscillation alebo amplification.

## Glossary impact

Relevantné pojmy: feedback loop, target state, observed state, correction, verification, negative feedback, positive feedback, feedback latency, signal, noise, gain, delay, hysteresis, deadband, oscillation, actionability, completeness contract, leading indicator a lagging indicator.

## Primárne zdroje

- [MIT OpenCourseWare — System Dynamics](https://ocw.mit.edu/courses/15-871-introduction-to-system-dynamics-fall-2013/)
- [Google Cloud — DevOps capabilities](https://cloud.google.com/architecture/devops)
- [Google SRE — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Systems thinking](systems-thinking.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Continuous improvement →](continuous-improvement.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
