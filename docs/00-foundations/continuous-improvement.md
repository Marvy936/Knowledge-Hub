# Continuous Improvement

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Feedback Loops](feedback-loops.md), [Systems Thinking](systems-thinking.md)
- Súvisiace témy: retrospectives, postmortems, DORA metrics, toil, technical debt, value stream mapping

Metadata zaraďuje continuous improvement za feedback a systems thinking. Zlepšovanie nie je samostatná aktivita mimo delivery; je to riadený spôsob, ako meniť technický aj organizačný systém na základe evidence.

## 1. Definícia

Continuous improvement je opakovaný proces pozorovania systému, formulovania hypotézy, vykonania kontrolovanej zmeny a overenia jej výsledku. Cieľom je zlepšovať flow, reliability, security, operability alebo používateľský outcome a zároveň sa učiť o mechanizmoch systému.

Zmena sama osebe nie je zlepšenie. Za zlepšenie ju možno označiť až vtedy, keď evidence ukáže očakávaný pozitívny výsledok bez neprijateľného presunu costu alebo risku do inej časti systému.

## 2. Problém, ktorý continuous improvement rieši

Proces a architecture, ktoré dnes fungujú, sa časom menia pod vplyvom rastu, nových dependencies, trafficu, organization a security požiadaviek. Dočasný workaround sa môže stať kritickým production pathom a malý manuálny krok narásť na každodenný toil.

Bez improvement capability sa systém zhoršuje postupne a incidentne. Tím rieši symptómy, pridáva exceptions a spotrebúva rastúcu časť kapacity na údržbu existujúceho behavioru.

Zhoršovanie má konkrétne zdroje:

- **Rastúca complexity — viac states a interactions**: každá nová integration alebo feature zväčšuje test, observability a change surface.
- **Nové dependencies — ďalšie failure a lifecycle boundaries**: provider, library alebo shared service môže zaviesť upgrade a availability risk.
- **Väčší tím alebo organization — viac communication paths**: nejasné interfaces a decision rights vytvárajú handoffs a duplicated solutions.
- **Vyšší traffic — odhalenie nonlinear limits**: queues, locks a quotas, ktoré pri malom load-e neboli viditeľné, sa stanú bottleneckom.
- **Technical debt — rastúci interest**: rýchle dočasné rozhodnutie môže zvyšovať cost každej budúcej zmeny.
- **Security a compliance change — posun threat a control požiadaviek**: starý trust model nemusí pokrývať nové data alebo regulatory boundaries.
- **Accumulated toil — manuálna práca rastúca so scale**: operátori spotrebujú kapacitu na opakovanie namiesto odstránenia príčiny.

## 3. Mentálny model experimentálnej slučky

Continuous improvement je uzavretý feedback loop s explicitnou hypotézou. Každý cyklus má vytvoriť evidence o systéme, aj keď experiment nepotvrdí pôvodné očakávanie.

```text
pozorovanie a baseline
→ výber problému alebo constraintu
→ hypotéza o cause-and-effect
→ malá bezpečná zmena
→ meranie výsledku
→ ponechať, upraviť alebo rollback
→ štandardizovať learning
→ ďalší cyklus
```

Neúspešná hypotéza nie je neúspešné učenie. Ak experiment bezpečne ukáže, že queue time nespôsobuje nedostatok runnerov, tím odstránil jednu falošnú príčinu a môže skúmať scheduling alebo long-running jobs.

## 4. Improvement object a system boundary

Pred zmenou treba určiť, čo sa zlepšuje a aký širší outcome môže zásah ovplyvniť. Optimalizácia pipeline duration môže zvýšiť infrastructure cost alebo vynechať tests a zhoršiť change failure rate.

Improvement object môže byť:

- **Technical component — konkrétny runtime alebo pipeline krok**: napríklad build cache, database index alebo autoscaling policy.
- **Value stream — end-to-end flow zmeny**: waiting, approvals, WIP a rework môžu byť významnejšie než component performance.
- **Operational capability — diagnosis, deployment alebo recovery**: improvement môže skrátiť MTTR bez zmeny samotnej business funkcie.
- **Team interface — handoff a decision rights**: self-service alebo jasný ownership môže odstrániť frontu, ktorú technická automation nevidí.
- **User outcome — reliability alebo product behavior**: zmena musí byť validovaná na boundary, pre ktorú systém existuje.

## 5. PDCA ako control model

PDCA rozdeľuje improvement na Plan, Do, Check a Act. Hodnota modelu je v tom, že zabraňuje zámene implementácie nápadu za dokončené zlepšenie.

### Plan

Plan definuje problém, baseline, target condition, hypotézu a safety boundary. Tím musí vysvetliť, prečo očakáva konkrétny mechanismus a aký signal ho potvrdí alebo vyvráti.

Bez baseline a decision criteria sa úspech hodnotí pocitom. Bez abort condition môže experiment pokračovať aj po vzniku neprimeraného user impactu.

### Do

Do vykoná najmenšiu zmenu schopnú otestovať hypotézu. Scope môže byť jeden repository, pipeline, tenant alebo traffic cohort, aby sa znížil blast radius a interference s ďalšími iniciatívami.

Execution musí zachovať change identity a timestamps. Ak súčasne prebehne viac nekorelovaných zásahov, výsledok nemožno spoľahlivo pripísať testovanej hypotéze.

### Check

Check porovná observed result s baseline a targetom. Nehodnotí iba primary metric, ale aj guardrail metrics, ktoré odhalia presun costu alebo risku.

Zrýchlenie build-u je napríklad neúspešné, ak zvýši cache corruption, failure rate alebo infra spend nad prijateľnú boundary. Variabilita a sample size musia byť dostatočné na rozlíšenie trendu od náhody.

### Act

Act rozhodne, či sa zmena ponechá, upraví alebo vráti. Potvrdený experiment sa štandardizuje cez code, template, policy, documentation a ownership; vyvrátený experiment sa zaznamená ako learning a systém sa vráti do bezpečného state-u.

Act nie je koniec. Nový štandard vytvorí ďalšie pozorovanie a môže presunúť bottleneck do inej časti systému.

## 6. Kaizen a malé kroky

Kaizen zdôrazňuje priebežné malé zlepšenia vykonávané ľuďmi, ktorí systém reálne používajú. Malý experiment skracuje feedback, znižuje blast radius a uľahčuje určenie cause-and-effect.

Výhody majú konkrétny mechanizmus:

- **Jednoduchšie vyhodnotenie — menej súčasne menených premenných**: observed difference sa ľahšie priradí zásahu.
- **Menší blast radius — obmedzený user alebo system scope**: chybná hypotéza nespôsobí organization-wide incident.
- **Lepšia reverzibilita — lacnejší rollback**: systém možno rýchlo vrátiť na baseline bez rozsiahlej migration.
- **Častejšie learning cycles — viac evidence za rovnaké obdobie**: tím nemusí čakať na dokončenie veľkého transformation programu.
- **Skoré odhalenie assumptions — menší sunk cost**: chybný smer sa upraví pred investíciou do kompletnej platformy alebo redesignu.

Veľká architecture zmena môže byť potrebná, ale aj tá sa má rozdeliť na compatibility, migration a rollout kroky s vlastným evidence contractom.

## 7. Baseline

Baseline opisuje správanie systému pred zásahom. Musí zahŕňať dostatočne dlhý a reprezentatívny interval, aby prirodzená variabilita, traffic seasonality alebo jednorazový incident neboli zamieňané za improvement effect.

Pri pomalej CI pipeline môže baseline obsahovať:

- **Median duration — typický processing čas**: ukazuje bežnú skúsenosť, ale nie tail najpomalších behov.
- **p95 duration — tail latency pipeline**: odhaľuje zriedkavejšie dlhé runs, ktoré môžu dominovať developer experience.
- **Queue time — waiting pred spustením**: odlišuje nedostatok runner capacity od pomalých jobs.
- **Failure rate — podiel neúspešných runs**: zabraňuje zrýchleniu cez vynechanie dôležitých kontrol alebo rast instability.
- **Retry rate — opakované execution**: môže maskovať flaky tests a zvyšovať skutočný compute a lead time.
- **Cost per run — ekonomický guardrail**: ukazuje, či performance improvement nevznikol neprimeraným navýšením resources.

Bez baseline sa výsledok porovnáva s pamäťou alebo jedným vhodným príkladom. Také hodnotenie je náchylné na confirmation bias.

## 8. Target condition

Target condition opisuje konkrétny požadovaný state v blízkom horizonte. Nie je to vzdialená vízia typu „pipeline má byť rýchla“, ale merateľná hranica spojená s behaviorom a constraints.

Príklad targetu môže byť: „Median queue time pod dve minúty, p95 pod päť minút a runner utilization pod 80 % pri zachovaní failure rate.“ Tento target umožňuje rozhodnúť, či sa systém priblížil k cieľu bez vytvorenia nového saturation risku.

Target sa má viazať na user alebo operator outcome. Technická hodnota, ktorú nikto nepociťuje a ktorá nemení rozhodnutie, nemusí byť vhodnou prioritou.

## 9. Hypotéza

Hypotéza spája zásah, mechanismus a očakávaný merateľný výsledok. Formulácia „pridáme viac runnerov, aby bola pipeline lepšia“ nehovorí, ktorý problem sa rieši ani čo vyvráti predpoklad.

Presnejší model:

```text
Ak zvýšime runner capacity z 3 na 6,
median queue time klesne pod 2 minúty,
pretože baseline ukazuje dlhú frontu pri vysokej runner utilization,
pričom build duration a failure rate zostanú bez zhoršenia.
```

Hypotéza je vyvrátiteľná. Ak queue time neklesne, bottleneck môže byť scheduler, job affinity alebo dlhý serial step a tím nemá pokračovať v pridávaní compute bez nového modelu.

## 10. Experiment design

Experiment musí izolovať hypotézu a kontrolovať risk. Pred vykonaním sa definujú scope, duration, metrics, guardrails, abort, rollback a owner.

- **Scope — kde sa zmena aplikuje**: jedna pipeline alebo repository znižuje interference a blast radius.
- **Duration — ako dlho sa zbiera evidence**: interval musí pokryť reprezentatívny workload a nie iba jeden priaznivý run.
- **Primary metric — čo potvrdzuje target**: napríklad median a p95 queue time priamo testujú capacity hypotézu.
- **Guardrail metrics — čo sa nesmie neprijateľne zhoršiť**: failure rate, cost alebo resource saturation chránia širší outcome.
- **Abort condition — kedy experiment okamžite skončí**: data corruption, výrazný user impact alebo cost spike majú vopred definovanú hranicu.
- **Rollback — ako sa obnoví baseline**: zmena musí byť technicky a organizačne reverzibilná v požadovanom čase.

## 11. Improvement Kata

Improvement Kata je rutina pre postup cez neistotu. Nevyžaduje kompletný dlhodobý implementation plan; udržiava smer a vyberá ďalší malý experiment na základe aktuálneho evidence.

Štyri otázky tvoria decision sequence:

1. **Aký je smer alebo cieľový stav?** — definuje outcome, aby lokálne experimenty nesmerovali proti širšej potrebe.
2. **Aký je aktuálny stav?** — vytvára baseline a odhaľuje rozdiel medzi dojmom a evidence.
3. **Aké prekážky bránia cieľu?** — formuluje hypotheses o constraints namiesto okamžitého zoznamu solutions.
4. **Aký je ďalší malý experiment?** — testuje najbližšiu neistotu s obmedzeným riskom a krátkym feedbackom.

Kata bráni tomu, aby transformation roadmapa predstierala znalosť všetkých budúcich krokov. Nasledujúci krok sa mení podľa výsledku predchádzajúceho experimentu.

## 12. Retrospective

Retrospective pravidelne skúma spôsob práce tímu, nie iba výsledok jednej technickej udalosti. Má identifikovať repeated waiting, communication, planning alebo quality patterns a vybrať malý počet zlepšení, ktoré tím reálne dokončí.

Kvalitná retrospective používa konkrétne evidence:

- **Pozorovanie — čo sa opakovane stalo**: napríklad review queue prekročila jeden deň pri polovici zmien.
- **Mechanism hypothesis — prečo behavior vzniká**: veľké pull requests a nejasný reviewer ownership môžu byť causes, nie „ľudia sú pomalí“.
- **Prioritizované opatrenie — jeden zvládnuteľný experiment**: WIP limit alebo reviewer rotation sa testuje pred rozsiahlym process redesignom.
- **Owner a deadline — zodpovednosť za vykonanie**: bez nich action prehrá s urgentným product backlogom.
- **Verification — spôsob merania účinku**: ďalšia retrospective porovná review latency a rework s baseline.

Retrospective bez kontroly predchádzajúcich actions je otvorený feedback loop. Tím opakovane pomenúva rovnaké problémy bez zmeny systému.

## 13. Post-incident review

Post-incident review analyzuje významný failure pomocou timeline, technical evidence a decision contextu. Cieľom je pochopiť, ako viacero conditions a safeguards vytvorilo výsledný dopad.

Blameless prístup neznamená absenciu accountability. Odmieta však vysvetlenie „človek urobil chybu“ ako root cause a skúma, prečo bola akcia možná, prečo sa neodhalila skôr a prečo recovery trvala daný čas.

Výstup má viesť k systémovým zmenám:

- **Preventive action — zníženie pravdepodobnosti**: test, safer default alebo permission boundary blokuje známu failure path.
- **Detective action — skorší signal**: monitoring alebo audit znižuje time-to-detection.
- **Mitigating action — menší blast radius**: isolation, canary alebo rate limit obmedzí dopad, aj keď failure vznikne.
- **Recovery action — rýchlejšia a bezpečnejšia obnova**: runbook, automation alebo backup test znižuje correction time a uncertainty.

## 14. Toil

Toil je manuálna, opakovaná, automatizovateľná práca, ktorá neprináša trvalé zlepšenie a typicky rastie so scale služby. Nie každá operations práca je toil; komplexná jednorazová migration alebo design recovery plánu môže vytvárať dlhodobú hodnotu.

Typické toil examples treba chápať cez mechanizmus:

- **Ručné reštarty — opakovaná mitigation bez permanent fixu**: obnovujú process, ale neodstraňujú memory leak alebo saturation cause.
- **Opakované prideľovanie accessu — manuálny identity lifecycle**: rastie s počtom ľudí a vytvára waiting, inconsistency a audit risk.
- **Manuálne deployment kroky — execution závislé od pamäte**: variabilita a partial failures vyžadujú hero knowledge.
- **Ručné čistenie diskov — capacity problem bez retention controlu**: odstráni aktuálny symptom a zachová rastúci data flow.
- **Kopírovanie údajov medzi systémami — chýbajúca integration alebo source of truth**: vytvára stale a conflicting records.

Improvement nemá toil iba zrýchliť. Najprv zistí jeho cause a rozhodne, či ho odstráni, zníži demand, automatizuje alebo zmení architecture.

## 15. Toil budget a opportunity cost

Toil spotrebúva kapacitu, ktorá potom chýba na reliability a product improvements. Ak rastie lineárne s trafficom alebo počtom accounts, služba môže dosiahnuť bod, keď všetka engineering práca udržiava aktuálny stav.

Toil budget zviditeľňuje tento trend a vytvára decision threshold. Keď manuálna operations práca prekročí dohodnutý podiel, tím prioritizuje automation alebo redesign namiesto ďalšieho scale-u rovnakého procesu.

Budget nie je ospravedlnenie ignorovať malý toil. Má pomáhať posúdiť opportunity cost a riziko, že dočasný workaround sa stane trvalým operating modelom.

## 16. Technical debt

Technical debt je budúci cost alebo risk vytvorený dnešným rozhodnutím. Môže byť vedomý a ekonomicky racionálny, ak organizácia rozumie interestu, ownerovi a podmienke splatenia.

Debt sa stáva nebezpečný, keď je neviditeľný alebo bez lifecycle-u:

- **Neevidovaný debt — budúce tímy nepoznajú constraint**: prekvapí pri zmene, incidente alebo upgrade-e.
- **Debt bez ownera — nikto nemá decision authority ani priority**: interest rastie, ale každá product požiadavka ho opäť odloží.
- **Nemeraný interest — cost sa javí ako bežná práca**: dlhšie tests, incidents a manual steps nie sú spätne spojené s pôvodným rozhodnutím.
- **Dočasné riešenie bez exit condition — permanentná výnimka**: workaround zostane aj po zániku pôvodného termínu alebo constraintu.

Debt register bez väzby na risk a flow sa môže zmeniť na nekonečný wishlist. Prioritizuje sa podľa evidence o incidente, lead time, security a opportunity costu.

## 17. Prioritizácia zlepšení

Nie všetky problémy majú rovnaký systémový dopad. Najhlasnejší stakeholder alebo najľahšie technické riešenie nemusia predstavovať aktuálny constraint.

Kritériá musia vysvetľovať, čo ovplyvňujú:

- **User impact — závažnosť a rozsah outcome-u**: prioritu zvyšuje strata kritickej capability, integrity alebo trustu.
- **Frequency — ako často sa problem opakuje**: malý incident denne môže mať väčší cumulative cost než veľká zriedkavá nepríjemnosť.
- **Toil time — spotrebovaná engineering kapacita**: ukazuje opportunity cost opakovanej manuálnej práce.
- **Security risk — threat a exposure**: vysoká exploitability alebo privilege boundary môže vyžadovať prioritu aj bez minulého incidentu.
- **Reliability risk — pravdepodobnosť a blast radius failure-u**: near miss môže odhaliť významný latentný problém.
- **Blocking effect — obmedzenie ďalšieho flowu**: bottleneck, ktorý brzdí mnoho tímov, má multiplier effect.
- **Change cost — effort a coordination**: ovplyvňuje veľkosť experimentu, nie automaticky jeho hodnotu.
- **Reversibility — schopnosť bezpečne testovať**: reverzibilné opatrenie možno overiť skôr a s menším riskom.

## 18. Selecting the constraint

Systems thinking odporúča zlepšovať aktuálny constraint, nie každý viditeľný problém naraz. Zásah mimo bottlenecku môže vytvoriť viac upstream outputu a zväčšiť queue.

Výber používa flow a runtime evidence. Ak väčšina lead time vzniká v environment queue, optimalizácia code formattingu neprinesie významný end-to-end effect, hoci je jednoduchá a lokálne merateľná.

Constraint po zlepšení treba znovu určiť. Continuous improvement je séria presunov obmedzenia, nie jednorazové „odstránenie všetkých bottleneckov“.

## 19. Praktický experiment: nestabilné deploymenty

Baseline ukazuje, že 20 % deploymentov potrebuje manuálny zásah, rollback trvá priemerne 35 minút a veľká časť failures súvisí s chýbajúcou configuration. Tím formuluje hypotézu, že schema validation a render test znížia túto triedu failure-ov aspoň o polovicu.

Experiment je rozdelený takto:

1. **Klasifikovať posledný mesiac failures** — overí, či configuration je skutočne dominantná a vytvorí baseline podľa failure class.
2. **Pridať schema validation pre najčastejšiu chybu** — testuje malú konkrétnu boundary namiesto všeobecného „zlepšenia pipeline“.
3. **Nasadiť kontrolu do jednej pipeline** — obmedzí blast radius a umožní porovnanie s podobným neovplyvneným flowom.
4. **Merať štyri týždne** — zachytí dostatok deploymentov a prirodzenú variabilitu.
5. **Porovnať configuration failure, total failure, lead time a bypasses** — overí primary effect aj guardrails.

Ak failures neklesnú, validácia môže testovať nesprávnu schema boundary alebo chýbajúca configuration vzniká až pri secret delivery. Výsledok vedie k novej hypotéze, nie automaticky k pridaniu ďalšieho validatora.

## 20. Measurement a guardrails

Improvement metric má reprezentovať target condition a byť citlivá na očakávaný mechanismus. Súčasne treba sledovať guardrails, aby sa lokálne zlepšenie nezaplatilo horším global outcome-om.

Podľa typu zásahu možno použiť:

- **Lead time — end-to-end flow zmeny**: odhaľuje waiting aj processing, ale potrebuje stabilný start a end event.
- **Deployment frequency — capability často meniť produkciu**: bez change size a failure contextu môže byť vanity metric.
- **Change failure rate — delivery quality**: vyžaduje presnú klasifikáciu rollback, hotfixu a degraded release-u.
- **Recovery time — diagnosability a remediation capability**: má rozlišovať detection, decision a technical restoration.
- **Queue time — konkrétny waiting bottleneck**: priamo testuje capacity alebo scheduling experiment.
- **Test flakiness — trust feedbacku**: meria nondeterministic failures oddelene od reálnych regressions.
- **Manual intervention count — toil a automation gaps**: potrebuje severity a time spent, nie iba počet kliknutí.
- **User SLI — global reliability guardrail**: potvrdzuje, že delivery alebo cost improvement nepoškodil používateľský outcome.

## 21. Statistical a observational caution

Observed improvement nemusí byť spôsobený zásahom. Traffic mohol klesnúť, iný tím zmeniť dependency alebo incidentne pomalý baseline interval sa prirodzene vrátiť k priemeru.

Preto experiment zaznamenáva concurrent changes, používa dostatočný interval a podľa možnosti control alebo phased rollout. Pri vysokom risku môže byť potrebná formálnejšia experimentálna analýza; pri menšom operational change postačí transparentný before/after model s guardrails.

Nie každé rozhodnutie potrebuje štatistickú signifikanciu. Potrebuje však čestný opis neistoty a nesmie tvrdiť cause-and-effect iba z jednej korelácie.

## 22. Standardization

Potvrdené zlepšenie sa musí stať normálnou súčasťou systému. Inak závisí od pamäte pôvodného tímu a po organization alebo tool zmene zmizne.

Standardization používa viac vrstiev:

- **Code alebo automation — vykonávací mechanismus**: odstráni potrebu spoliehať sa na manuálne pripomenutie.
- **Automated test — regression evidence**: zachová očakávaný behavior pri budúcej zmene.
- **Template alebo platform capability — reusable paved road**: distribuuje improvement ďalším tímom bez kopírovania.
- **Policy a safer default — organization guardrail**: chráni known high-risk boundary, pričom exception má lifecycle.
- **Runbook a documentation — operational context**: vysvetľuje význam, diagnosis a recovery, ktoré nemožno plne automatizovať.
- **Ownership a service catalog — udržanie capability**: určuje, kto sleduje drift, metrics a ďalšie zmeny.

## 23. Follow-up a effectiveness review

Action sa nepovažuje za dokončenú iba po merge-i. Effectiveness review po primeranom čase overí, či sa primary metric zlepšila, guardrails zostali zdravé a ľudia nový mechanismus skutočne používajú.

Policy môže byť technicky nasadená, ale teams ju obchádzajú cez manual path. Platform feature môže existovať, ale mať takú latency alebo UX, že pôvodná ticket queue zostane.

Review môže viesť k úprave alebo odstráneniu improvementu. Continuous improvement zahŕňa aj zrušenie controls a automation, ktoré už neprinášajú hodnotu.

## 24. Improvement portfolio a WIP

Priveľa paralelných initiatives znižuje schopnosť určiť cause-and-effect a spotrebúva owner attention. Každý projekt má meetings, migration, communication a maintenance cost aj vtedy, keď nie je dokončený.

Improvement WIP limit chráni completion a learning. Organizácia vyberie niekoľko najvýznamnejších constraints, dokončí experiment a standardization a až potom otvorí ďalšiu veľkú iniciatívu.

Portfolio má zahŕňať product, reliability, security, toil aj debt improvements. Ak všetku kapacitu spotrebujú features, latentný risk a manual cost rastú až do incidentného vynútenia práce.

## 25. Continuous improvement v incident response

Incident vytvára immediate mitigation loop a dlhší learning loop. Prvý obnovuje službu, druhý mení pravdepodobnosť, detection alebo blast radius budúceho failure-u.

```text
incident
→ containment a recovery
→ evidence preservation
→ systemic analysis
→ prioritized improvement
→ implementation
→ fault alebo regression test
→ effectiveness review
```

Ak permanent action nie je financovaná, incident response sa stáva opakovaným toilom. Ak sa každé zistenie označí za najvyššiu prioritu, backlog sa zaplní a žiadna zmena sa nedokončí.

## 26. Continuous improvement v platform engineeringu

Platform je interný produkt a potrebuje vlastný feedback loop. Adoption, time-to-first-deploy, support tickets, bypass rate a developer interviews ukazujú, či paved road znižuje cognitive load alebo vytvára nové obmedzenia.

Platform team nemá merať iba počet vytvorených templates. Dôležitý je downstream outcome: kratší environment waiting, menej security exceptions, stabilnejšie deployments a nižší toil product tímov.

Improvement experiment môže zmeniť API, documentation, default alebo support model. Centralizovanie ďalšej capability nie je automaticky zlepšenie, ak zvyšuje organization-wide coupling.

## 27. Continuous improvement v security

Security improvement spája threat, control, operational friction a evidence. Pridanie approval gate-u môže znížiť jednu class risku a súčasne vytvoriť bypasses alebo veľkú queue.

Malý experiment môže zaviesť policy-as-code pre konkrétny high-confidence rule, merať blocked violations, false positives, exception lead time a developer remediation. Až potom sa control rozšíri na ďalší scope.

Control effectiveness sa posudzuje podľa zníženia exposure alebo detection time-u, nie iba podľa počtu vykonaných scans. Security metric bez behavior contextu môže podporovať compliance theatre.

## 28. Anti-patterny

### Improvement theatre

Vznikajú workshopy, maturity assessments a zoznamy opatrení, ale actions nemajú ownera ani evidence. Aktivita vytvára dojem transformácie bez zmeny system behavioru.

### Priveľa paralelných iniciatív

Tím mení pipeline, branching, test environment aj approval naraz. Výsledok nemožno priradiť konkrétnemu mechanismu a nedokončené migrations zvyšujú complexity.

### Zmena bez baseline

Úspech sa hodnotí podľa jedného rýchleho runu alebo subjektívneho dojmu. Prirodzená variabilita a seasonality sa zamieňajú za effect.

### Automatizácia symptómu

Tím automatizuje pravidelný restart memory-leaking service-u. Toil sa zníži, ale capacity a reliability risk zostáva a môže sa prejaviť pri inom workload-e.

### Trvalý emergency mode

Každý problem je urgentný a improvement work sa neustále prerušuje. Organizácia spotrebúva kapacitu na mitigation, čím posilňuje positive feedback medzi debtom, incidentmi a ďalším nedostatkom improvement času.

### Permanentný control bez review

Dočasný approval alebo exception sa nikdy neprehodnotí. Process accumulates steps, ktoré stratili pôvodný threat alebo business dôvod, ale stále zvyšujú lead time.

## 29. Kontrolné otázky

1. Aký je rozdiel medzi zmenou a preukázaným zlepšením?
2. Prečo improvement potrebuje system boundary a guardrail metrics?
3. Ako sa jednotlivé kroky PDCA navzájom podmieňujú?
4. Prečo malý experiment poskytuje kvalitnejší cause-and-effect feedback?
5. Čo musí obsahovať reprezentatívny baseline?
6. Ako sa target condition líši od neurčitého dlhodobého cieľa?
7. Ako napíšeš vyvrátiteľnú hypotézu s mechanismom?
8. Prečo retrospective bez follow-upu nie je uzavretý loop?
9. Čím sa toil líši od hodnotnej operations práce?
10. Ako sa meria interest technical debtu?
11. Prečo sa zlepšuje aktuálny constraint a nie najľahší problém?
12. Aké vrstvy standardizujú potvrdený improvement?
13. Čo overuje effectiveness review po dokončení implementation?
14. Ako improvement WIP limit zlepšuje learning?
15. Ako sa continuous improvement uplatňuje v platform a security kontexte?

## 30. Zhrnutie

Continuous improvement je experimentálny control loop založený na baseline, target condition, hypotéze, malej zmene, measurement a štandardizácii learningu. Zmena sa stáva zlepšením až po preukázaní outcome-u a kontrole širších guardrails.

Tím zlepšuje aktuálny constraint, obmedzuje paralelný WIP, odstraňuje toil a riadi technical debt podľa jeho interestu. Retrospectives a post-incident reviews majú hodnotu iba vtedy, keď actions dostanú ownera, prejdú implementation a ich účinok sa neskôr overí.

## Glossary impact

Relevantné pojmy: continuous improvement, PDCA, Kaizen, baseline, target condition, hypothesis, experiment, guardrail metric, abort condition, Improvement Kata, retrospective, post-incident review, toil, toil budget, technical debt, debt interest, standardization a effectiveness review.

## Primárne zdroje

- [The Lean Enterprise Institute — What is Lean Thinking?](https://www.lean.org/explore-lean/what-is-lean-thinking/)
- [Google SRE — Eliminating Toil](https://sre.google/sre-book/eliminating-toil/)
- [Google SRE — Postmortem Culture](https://sre.google/sre-book/postmortem-culture/)
- [DORA — Research program](https://dora.dev/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Feedback loops](feedback-loops.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: T-shaped, I-shaped a π-shaped engineer →](t-shaped-engineer.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
