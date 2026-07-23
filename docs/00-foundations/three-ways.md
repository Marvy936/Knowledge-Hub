# Three Ways of DevOps

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [DevOps](devops.md), [DevOps Lifecycle](devops-lifecycle.md), [CALMS](calms.md)
- Súvisiace témy: systems thinking, feedback loops, continuous learning, CI/CD, observability, incident management

Metadata zaraďuje Three Ways za základný DevOps a CALMS model. Princípy neopisujú tri projektové fázy ani tri tímy; ide o súčasne fungujúce vlastnosti jedného delivery a operations systému.

## 1. Definícia

Three Ways of DevOps sú tri systémové princípy opisujúce tok práce, návrat spätnej väzby a dlhodobé učenie. Pomáhajú vysvetliť, prečo moderný toolchain sám osebe nezaručuje rýchle ani bezpečné delivery.

Tri princípy sa navzájom podmieňujú:

- **The First Way — Flow**: optimalizuje pohyb práce a hodnoty od potreby cez engineering systém k používateľovi.
- **The Second Way — Feedback**: vracia dôkazy o kvalite a runtime výsledku k ľuďom a mechanizmom schopným zmenu opraviť.
- **The Third Way — Continual Learning and Experimentation**: premieňa experimenty, incidents a near misses na trvalú zmenu tests, architecture, platformy alebo pracovných pravidiel.

Flow bez feedbacku iba zrýchľuje presun chýb. Feedback bez learningu opravuje jednotlivé prejavy, ale ponecháva podmienky na ich opakovanie.

## 2. Problém, ktorý Three Ways riešia

Organizácia môže mať silných špecialistov, cloud platformu a automatizované pipelines a napriek tomu dodávať pomaly. Práca môže čakať medzi tímami, feedback prichádza po strate contextu a incidenty sa uzatvárajú obnovením služby bez odstránenia systémovej slabiny.

Three Ways presúvajú pozornosť z utilization jednotlivých ľudí na správanie celého systému. Pýtajú sa, ako rýchlo sa dokončená hodnota pohybuje, ako skoro sa odhalí odchýlka a či zistenie zmení budúcu schopnosť systému.

Typické symptómy ukazujú na odlišnú Way:

- **Dlhé fronty a veľké release-y — slabý Flow**: práca je rozpracovaná, ale neprechádza plynulo cez bottleneck k používateľovi.
- **Chyby objavené neskoro — slabý Feedback**: kontrola je ďaleko od vzniku chyby alebo výsledok nedostane človek schopný konať.
- **Opakované incidenty — slabé Learning**: tím obnovuje aktuálny stav, ale nepridáva guardrail, test, ownership ani architecture zmenu.

## 3. Spoločný mentálny model

Three Ways možno zobraziť ako tri smery pohybu v jednom value streame. Work a artifacty idú smerom k produkcii, evidence sa vracia opačne a learning mení samotné cesty, pravidlá a capabilities systému.

```text
FIRST WAY — FLOW
Potreba → Development → Build/Test → Delivery → Operations → Používateľ

SECOND WAY — FEEDBACK
Používateľ/Production → Telemetry/Incident → Delivery → Development → Planning

THIRD WAY — LEARNING
Experiment alebo failure → Evidence → Analýza → Systémová zmena → Nový štandard
```

Nejde o jednorazový kruh. V každom okamihu môže pipeline poskytovať feedback, production incident zastaviť flow a learning experiment upraviť budúci deployment model.

# The First Way — Flow

## 4. Definícia Flow

First Way optimalizuje plynulý pohyb práce od business potreby po overenú používateľskú hodnotu. Cieľom nie je maximalizovať počet otvorených úloh alebo stopercentnú vyťaženosť každého oddelenia, ale skracovať end-to-end lead time bez zhoršenia quality a reliability.

Flow skúma active work aj waiting. Rýchly build neposkytuje veľkú hodnotu, ak release čaká tri dni na environment alebo mesačné change window.

## 5. Čo systémom skutočne tečie

Flow nie je iba presun ticketu cez stĺpce. Systémom tečú rozhodnutia, source changes, artifacts, configuration, approvals a evidence, pričom každá zmena formy môže vytvoriť frontu alebo stratu identity.

Dôležité flow units sú:

- **Change request — dôvod a požadovaný outcome**: bez jasného intentu môže downstream tím správne vykonať technicky nesprávnu zmenu.
- **Source revision — verzovaná implementácia rozhodnutia**: musí zachovať väzbu na review, tests a požiadavku.
- **Artifact — nemenný build output**: promotion rovnakého digestu zachováva platnosť evidence medzi prostrediami.
- **Configuration a infrastructure state — runtime kontext**: zmena artifactu bez správnej configuration nemusí vytvoriť očakávaný outcome.
- **Operational evidence — dôkaz pripravenosti a výsledku**: test, scan, health alebo SLO signal rozhoduje, či flow pokračuje.

## 6. Vizualizácia práce

Práca musí byť viditeľná vrátane waitingu, dependencies a blocked state-u. Ticket označený ako „in progress“ môže v skutočnosti tri dni čakať na review, pričom tento čas sa v lokálnej metrike vývojára stratí.

Vizualizácia má zachytiť aj neplánovanú prácu a incidents. Ak urgentné zásahy prebiehajú mimo boardu, plánovaný throughput vyzerá stabilne, ale reálna kapacita a WIP zostávajú skryté.

## 7. Work in progress a queueing

Work in progress (WIP) je množstvo začatej, ale nedokončenej práce. Vysoký WIP zvyšuje počet context switches, vek otvorených zmien a waiting pred každým obmedzeným reviewerom, environmentom alebo deployment windowom.

WIP limit neznamená, že ľudia majú zostať nečinní. Núti tím pomôcť dokončiť bottleneck, zlepšiť test alebo odstrániť blocked dependency namiesto zakladania ďalšej práce, ktorá iba zväčší frontu.

## 8. Small batch sizes

Malý batch skracuje čas medzi rozhodnutím a feedbackom a znižuje počet súčasne menených premenných. Pri software change sa jednoduchšie reviewuje a pri rollout-e vytvára menší blast radius.

Výhody vznikajú konkrétnym mechanizmom:

- **Menší review scope — lepšie pochopenie change intentu**: reviewer dokáže posúdiť assumptions a failure paths bez kombinácie viacerých nezávislých zmien.
- **Užšie testovanie — rýchlejšia lokalizácia regresie**: affected surface je jasnejší, hoci kritická zmena môže stále vyžadovať široké integration tests.
- **Bezpečnejší progressive rollout — čitateľnejší signal**: pri canary failure je menej pravdepodobných príčin a rollback odstráni menší rozsah hodnoty.
- **Skorší product feedback — menší sunk cost**: používateľská reakcia môže zmeniť smer pred implementáciou veľkého balíka.

## 9. Bottleneck a constraint

Throughput celého value streamu obmedzuje jeho aktuálny najužší krok. Zrýchlenie práce pred bottleneckom zväčší queue a multitasking, zatiaľ čo zrýchlenie kroku za bottleneckom zostane nevyužité.

Bottleneck môže byť technický alebo organizačný: flaky integration suite, jeden database reviewer, ručné security approval alebo zriedkavé release window. Po jeho odstránení sa obmedzenie presunie, preto sa flow zlepšuje iteratívne.

## 10. Handoffs a strata contextu

Handoff prenáša prácu a zodpovednosť medzi ľuďmi alebo tímami. Každý handoff pridáva waiting a potrebu znovu vytvoriť context, najmä ak interface tvorí neurčitý ticket namiesto presného contractu a self-service capability.

Znižovanie handoffov neznamená odstránenie špecialistov. Expertíza môže vstúpiť cez reusable policy, paved road, consultation alebo embedded collaboration bez toho, aby každá zmena čakala v centralizovanej fronte.

## 11. Built-in quality

Built-in quality znamená, že správnosť, security a operability sa kontrolujú počas vzniku zmeny, nie iba na konci samostatnou kontrolnou skupinou. Skorší feedback znižuje množstvo ďalšej práce postavenej na chybnom predpoklade.

Mechanizmy majú odlišnú boundary:

- **Static analysis — chyby viditeľné zo source-u**: odhaľuje syntax, types alebo známe patterns bez spustenia celého systému.
- **Automated tests — overenie behavior contractu**: kontrolujú izolovanú logiku a integrations podľa reprezentatívnosti test environmentu.
- **Policy as code — opakovateľné guardrails**: blokuje známu nepovolenú configuration pri source, plan alebo admission boundary.
- **Progressive delivery — runtime quality control**: vystaví zmenu malému scope-u a porovná reálny outcome s baseline.

Quality gate bez vysvetliteľného feedbacku iba vytvára frontu. Kontrola musí ukázať porušené pravidlo, affected object a spôsob nápravy.

## 12. Automation a flow

Automation skracuje processing time a variabilitu iba pri stabilnom, zjednodušenom procese. Automatizovaný ticketový handoff alebo desať redundantných approvals zostávajú waste, aj keď sa formulár presúva okamžite.

Flow automation potrebuje versioned inputs, idempotentné kroky, explicitný timeout, failure handling a audit. Inak zlyhanie pipeline vytvorí ďalšiu manuálnu frontu závislú od jej pôvodného autora.

## 13. First Way príklad

Pôvodný proces má krátku implementáciu, ale dlhé waiting periods:

```text
zmena dokončená
→ 2 dni review queue
→ 1 deň environment ticket
→ veľký spoločný QA batch
→ mesačné release window
→ production feedback po strate contextu
```

Zlepšený proces zmenšuje batch a odstraňuje waiting:

```text
malá zmena
→ lokálne a CI evidence
→ rýchle review s WIP limitom
→ self-service test environment
→ automated integration a smoke tests
→ canary promotion rovnakého artifactu
→ okamžitý production feedback
```

Najväčšie zlepšenie nevzniklo rýchlejším compilerom. Vzniklo zmenou queue, handoff a release modelu.

## 14. First Way failure modes

### Maximálna lokálna utilization

Každý tím je permanentne vyťažený a nemá rezervu na review, incident alebo variabilitu. Nová práca potom čaká a end-to-end lead time rastie napriek vysokej lokálnej produktivite.

### Veľké release batchy

Zmeny sa akumulujú, pretože deployment je drahý a rizikový. Veľký batch následne zvyšuje coordination a failure risk, čím posilňuje pôvodný dôvod nasadzovať zriedka.

### Throw over the wall

Development označí svoju úlohu za hotovú po odovzdaní ďalšiemu tímu. Production context a následky zmeny sa nevracajú k ľuďom, ktorí ovplyvňujú design.

### Automatizovaný bottleneck

Organizácia automatizuje execution, ale zachová centralizovaný approval alebo nejasné decision rights. Processing sa zrýchli, no queue pred rozhodnutím zostane.

# The Second Way — Feedback

## 15. Definícia Feedback

Second Way vytvára rýchle, presné a akčné spätné väzby z neskorších častí systému smerom k skorším. Cieľom je zistiť odchýlku čo najbližšie k jej vzniku a dostať evidence k actorovi schopnému zmeniť source, policy alebo rollout.

Feedback nie je množstvo dát. Signal, ktorému nikto neverí alebo ktorý nemá ownera a remediation path, zvyšuje noise a môže spomaliť rozhodovanie.

## 16. Feedback latency a cost of correction

Čím neskôr sa chyba odhalí, tým viac ďalšej práce už môže závisieť od chybného state-u. Syntax error v editore stojí sekundy, nekompatibilné API odhalené po týždni vyžaduje koordináciu viacerých tímov a production data corruption môže potrebovať recovery a business reconciliation.

Rýchlosť však nesmie znižovať dôveryhodnosť. Flaky test poskytuje feedback skoro, ale jeho false positives naučia ľudí výsledok ignorovať.

## 17. Technický feedback

Technické feedback loops pokrývajú odlišné vrstvy a majú odlišnú presnosť:

- **Compiler alebo type checker — okamžitá language correctness**: odhaľuje neplatné constructs, ale nevie posúdiť business behavior.
- **Linting a static analysis — source patterns a policy**: upozorňuje na style, bugs alebo known security patterns bez runtime contextu.
- **Unit tests — izolovaná behavioral evidence**: poskytujú rýchlu lokalizáciu, no mocks môžu skryť reálnu integration semantics.
- **Integration a contract tests — boundary compatibility**: odhaľujú protocol, schema a authentication mismatch medzi komponentmi.
- **Security a policy checks — známe risk boundaries**: blokujú vulnerability alebo nepovolenú configuration, ale potrebujú triage a exception lifecycle.
- **Deployment verification — runtime activation**: readiness, smoke a synthetic checks odlišujú vytvorený resource od funkčnej služby.

## 18. Produkčný feedback

Production poskytuje evidence o reálnom trafficu, scale, dependencies a používateľskom správaní. Nemá nahradiť skoré tests, ale overuje assumptions, ktoré pre-production prostredie nedokáže úplne reprodukovať.

- **Metrics — agregovaný rozsah a trend**: ukazujú rate, errors, latency a saturation, ale strácajú detail jednotlivého requestu.
- **Logs — detail udalosti a decisionu**: vysvetľujú error code alebo state transition, no môžu byť sampled, neúplné alebo obsahovať citlivé data.
- **Traces — causal request path**: ukazujú dependency a latency breakdown, ale iba pre vytvorené a sampled spans.
- **SLO a error budget — user-oriented reliability feedback**: spájajú technical signal s prijateľným service outcome-om a release policy.
- **Support a user feedback — kvalitatívny product evidence**: odhaľuje nečakaný workflow alebo usability problém, ktorý infra metrics neukážu.
- **Business outcomes — potvrdenie hodnoty**: conversion, completed tasks alebo processed orders ukazujú, či zdravá technológia rieši správny problém.

## 19. Observability a context

Observability umožňuje skúmať správanie systému pomocou korelovaných signals a contextu. Tím nemusí vopred poznať každú failure otázku, ale musí mať stabilnú service identity, version metadata, trace context a structured events.

Observability nie je magická vlastnosť backendu. Ak application nezaznamená business outcome alebo propagation preruší trace, storage systém nedokáže chýbajúci context spätne vytvoriť.

## 20. Stop-the-line mentality

Stop-the-line znamená, že závažný known defect zastaví ďalšie zvyšovanie exposure alebo produkciu ďalšej chybnej práce. Pochádza z myšlienky, že krátke zastavenie je lacnejšie než pokračovanie a hromadenie reworku.

V software systéme môže CI blokovať merge, canary controller zastaviť rollout alebo incident commander pozastaviť deployments. Mechanizmus potrebuje jasné severity a recovery criteria; ak každá drobná warning zastaví flow, ľudia kontrolu obídu.

## 21. Feedback musí dosiahnuť správne miesto

Production alert uzavretý iba v operations tíme neovplyvní source ani design. Feedback loop sa uzatvorí až vtedy, keď poznatok dostane tím schopný upraviť code, tests, platformu alebo product requirement.

Ownership metadata, service catalog a traceability release-u skracujú routing feedbacku. Bez nich responder najprv hľadá autora alebo repository a correction cost rastie.

## 22. Kvalita feedbacku

Dôveryhodný feedback má viac vlastností, ktoré sa musia posudzovať spolu:

- **Rýchly — prichádza pred stratou contextu a veľkým downstream dopadom**.
- **Relevantný — koreluje s change intentom alebo user outcome-om namiesto náhodnej aktivity**.
- **Dôveryhodný — má nízky false-positive a false-negative rate a známy completeness contract**.
- **Konkrétny — ukazuje affected component, pravidlo, hodnotu alebo request path**.
- **Akčný — dostáva ho owner s authority a bezpečnou remediation cestou**.
- **Overiteľný — po náprave možno rovnakým signalom potvrdiť recovery**.

Veľa nekvalitných signálov môže byť horších než menší počet presných signálov. Alert fatigue a ignorované flaky tests prerušujú Second Way aj v technicky bohato instrumentovanom systéme.

## 23. Second Way príklad

Rýchly feedback zachováva context autora:

```text
commit s breaking API zmenou
→ contract test zlyhá do 5 minút
→ report ukáže konkrétneho consumera a field
→ autor upraví backward-compatible contract
→ nový revision prejde testom pred merge
```

Neskorý model odhalí rovnakú chybu až po integračnom release-i. Medzitým sa zmení viac components, pôvodný autor pracuje na inej téme a oprava potrebuje coordinated rollback alebo rework viacerých tímov.

## 24. Second Way failure modes

### Late feedback

Kontrola prebieha až pri veľkom integračnom teste alebo production deployment-e. Correction cost rastie, pretože source context je starý a na zmenu už nadviazali ďalšie práce.

### Feedback bez contextu

Pipeline oznámi iba `job failed` alebo alert iba `high CPU`. Človek musí rekonštruovať scope, zmenu a dependency, takže technicky rýchly signal vedie k pomalej akcii.

### Monitoring iba pre Operations

Developers nevidia runtime behavior svojej služby a architecture decisions sa neopierajú o production evidence. Operations tím sa stáva manuálnym prekladateľom všetkého feedbacku.

### Alerting na každý symptóm

Veľké množstvo neakčných notifications znižuje dôveru a responder nevie rozlíšiť user-impact incident od bežnej variability.

### Potlačenie zlých správ

Ak je reakciou na risk obviňovanie, ľudia eskalujú neskoro alebo evidence upravia. Culture tým priamo poškodzuje technický feedback loop.

# The Third Way — Continual Learning and Experimentation

## 25. Definícia continual learning

Third Way vytvára podmienky na bezpečné experimentovanie, pravdivú analýzu zlyhaní a zabudovanie poznatkov späť do systému. Cieľom nie je tolerovať nedbanlivosť ani eliminovať všetky failures, ale znižovať neistotu a opakovanie rovnakých systémových chýb.

Learning sa preukazuje zmenou capability. Manuálne obnovenie služby rieši aktuálny state; nový test, automated renewal alebo isolation boundary mení pravdepodobnosť a dopad budúceho incidentu.

## 26. Experiment contract

Experiment je riadená zmena vykonaná s cieľom overiť hypotézu. Bez hypotézy a merateľného outcome-u je iba neštandardnou production zmenou označenou bezpečnejším slovom.

Bezpečný experiment definuje:

- **Hypotézu — očakávaný cause-and-effect vzťah**: napríklad „zlyhanie jednej worker zóny nezvýši oldest-message age nad SLO“.
- **Baseline — dôkaz normálneho stavu**: bez steady-state merania nemožno posúdiť, čo experiment zmenil.
- **Blast radius — scope vystavený riziku**: tenant, traffic percentage, Region alebo non-production environment obmedzí možnú škodu.
- **Observation signals — metrics a events pre rozhodnutie**: určujú, či hypotéza platí a či vzniká nečakaný dopad.
- **Abort condition — hranica okamžitého zastavenia**: chráni používateľa a zabraňuje pokračovaniu experimentu pri neprimeranom riziku.
- **Rollback alebo recovery plan — návrat do bezpečného state-u**: musí byť pripravený a otestovaný skôr než sa fault alebo zmena aktivuje.

## 27. Blameless post-incident learning

Blameless review skúma, prečo bolo rozhodnutie alebo akcia v danom context-e možné a často racionálne. Nezastaví sa pri vete „operator zadal zlý príkaz“, ale skúma permissions, UI, review, defaults, time pressure a recovery capabilities.

Blameless neznamená absenciu standards alebo accountability. Owner stále musí vykonať remediation, ale organizácia získava pravdivejšie evidence a opravuje systém namiesto iba výmeny človeka.

## 28. Chaos engineering, game days a drills

Chaos engineering kontrolovane vkladá fault, aby overil resilience hypotézu. Nie je to náhodné vypínanie production komponentov; potrebuje steady state, experiment scope, abort a recovery.

Game days a incident drills precvičujú technické aj ľudské paths. Restore test overí backup a keys, failover exercise authority a routing a tabletop odhalí nejasnú communication alebo dependency ešte pred skutočnou krízou.

## 29. Psychological safety

Learning vyžaduje, aby ľudia mohli hovoriť o uncertainty, near misses, technical debt a nebezpečných workaroundoch. Ak nositeľ zlej správy riskuje trest alebo zosmiešnenie, problémy sa stanú neviditeľné až do rozsiahleho incidentu.

Psychological safety nie je zníženie technických štandardov. Umožňuje skôr zistiť porušenie štandardu, presne opísať context a prijať evidence-based nápravu.

Význam jednotlivých tém je praktický:

- **Uncertainty — priznanie neúplného modelu**: umožní navrhnúť experiment alebo konzervatívny rollout pred predstieraním istoty.
- **Near miss — failure, ktorý ešte nespôsobil dopad**: poskytuje lacný learning signal pred skutočnou škodou.
- **Technical debt — vedomé budúce riziko a cost**: musí mať ownera a rozhodnutie, nie iba neurčitú sťažnosť.
- **Unsafe workaround — obídenie guardrailu pre okamžitý cieľ**: jeho zviditeľnenie umožní opraviť platform interface alebo proces, ktorý ľudí k obchádzke viedol.

## 30. Institutionalization of knowledge

Poznatok musí byť uložený v mechanizme, ktorý ovplyvní budúce správanie. Postmortem dokument bez ownera a termínu sa časom stratí a rovnaký incident sa zopakuje.

Learning sa môže premietnuť do viacerých vrstiev:

- **Test — automatický dôkaz pred rovnakou regresiou**: reprodukuje failure condition pri ďalšej relevantnej zmene.
- **Automation — odstránenie opakovanej manuálnej chyby**: napríklad certificate renewal zníži závislosť od kalendára jedného človeka.
- **Guardrail — obmedzenie nebezpečnej akcie pri správnej boundary**: policy alebo safer default blokuje known failure bez centralizovaného ručného approvalu.
- **Runbook — zlepšenie diagnosis a recovery**: zachová evidence path, bezpečné kroky a validation pre known incident.
- **Architecture change — odstránenie spoločného failure domainu**: rieši root systemic weakness namiesto iba symptómu.
- **Training a simulation — prenos tacit response knowledge**: pripraví viac ľudí na rozhodnutie, ktoré nemožno úplne automatizovať.
- **Monitoring alebo SLO — skoršie zviditeľnenie odchýlky**: vytvorí signal pred tým, než rovnaký failure dosiahne pôvodný dopad.

## 31. Third Way príklad

Certifikát expiruje a služba stratí TLS connectivity. Slabá reakcia obnoví certifikát manuálne a incident uzavrie; aktuálny state je opravený, ale systémová schopnosť zostáva rovnaká.

Systémové učenie zmení celý lifecycle:

```text
obnova služby
→ timeline a post-incident analýza
→ explicitný owner certificate lifecycle-u
→ automated renewal a bezpečné distribution
→ expiry a renewal-failure alerts
→ runbook a break-glass postup
→ pravidelný test renewal a failover paths
```

Každý krok odstraňuje inú podmienku incidentu: ownership gap, manuálnu závislosť, neskorý feedback alebo neotestovaný recovery proces.

## 32. Third Way failure modes

### Postmortem ako formalita

Dokument vznikne, ale actions nemajú ownera, deadline ani overenie effectiveness. Organizácia archivuje opis incidentu bez zmeny systému.

### Hero culture

Jednotlivec opakovane zachraňuje službu cez nezdokumentované manuálne zásahy. Odmena hero behavioru odstraňuje motiváciu vytvoriť automation, runbook a shared capability.

### Experiment bez guardrails

Zmena nemá hypotézu, baseline ani abort condition. Neúspech potom neposkytuje jasný learning a dopad nie je kontrolovaný.

### Zero-failure culture

Každé zlyhanie sa interpretuje ako individuálne zlyhanie. Tímy spomaľujú zmeny, skrývajú near misses a prestávajú vykonávať experimenty potrebné na overenie resilience.

### Opakovaný incident bez systémovej zmeny

Služba sa zakaždým obnoví rovnakým postupom, ale test, platforma ani architecture sa nemenia. Toil a risk zostávajú súčasťou normálneho operating modelu.

## 33. Vzájomná závislosť Three Ways

Všetky tri Ways musia fungovať súčasne. Slabá kombinácia vytvára predvídateľný anti-pattern.

```text
Flow bez Feedback
→ chyby a nesprávne predpoklady sa rýchlo dostanú do produkcie

Feedback bez Flow
→ problém je známy, ale oprava čaká v pomalom delivery systéme

Flow a Feedback bez Learning
→ systém reaguje na každú udalosť, ale rovnaké slabiny sa opakujú

Learning bez Flow a Feedback
→ experimenty nemajú rýchly evidence path ani schopnosť dostať zlepšenie do praxe
```

Vyspelý systém preto neoptimalizuje iba deployment speed alebo počet postmortems. Meria tok, feedback latency a mieru dokončenia systémových improvement actions.

## 34. End-to-end audit podľa Three Ways

Audit má spájať otázku s dôkazom a možným systémovým obmedzením.

### First Way — Flow

- **Aký je end-to-end lead time?** — ukáže, či sa lokálne rýchle kroky strácajú v dlhom waitingu.
- **Kde práca čaká najdlhšie?** — identifikuje queue, approval alebo environment bottleneck.
- **Aká je veľkosť typickej zmeny?** — odhaľuje feedback interval a blast radius release-u.
- **Koľko handoffov change prejde?** — ukazuje stratu contextu a organizačné fronty.
- **Ktorý constraint obmedzuje throughput?** — zabraňuje optimalizácii neobmedzujúceho kroku.

### Second Way — Feedback

- **Ako rýchlo autor zistí chybu?** — meria feedback latency od vzniku po action ownera.
- **Sú tests a alerts dôveryhodné?** — odhaľuje flaky alebo noisy signals, ktoré ľudia ignorujú.
- **Vidí tím production behavior svojej služby?** — preveruje shared operational feedback a version correlation.
- **Má signal context a remediation path?** — odlišuje akčný feedback od neurčitého noise.
- **Vracia sa user feedback do planningu?** — uzatvára product, nie iba technical loop.

### Third Way — Learning

- **Menia incidents systém alebo iba aktuálny state?** — rozlišuje recovery od institutional learningu.
- **Testujú sa recovery a failure assumptions?** — overuje, či architecture diagram zodpovedá reálnemu správaniu.
- **Existujú game days a bezpečné experiments?** — ukazuje schopnosť učiť sa pred kritickým incidentom.
- **Môžu ľudia hlásiť near misses?** — preveruje psychological safety a kvalitu evidence.
- **Majú improvement actions ownera a validation?** — odhaľuje postmortems bez vykonanej zmeny.

## 35. Nástroje ako implementácia princípu

Nástroj nie je samotná Way. Rovnaký produkt môže flow podporiť alebo poškodiť podľa konfigurácie, ownershipu a feedback contractu.

| Princíp | Mechanizmus | Čo nástroj podporuje | Limit |
|---|---|---|---|
| Flow | Version control a CI | malé integrácie, reproducible build a automated evidence | dlhé approvals a veľké branches môžu flow stále blokovať |
| Flow | Infrastructure as Code | self-service, review a opakovateľné environmenty | pomalý central apply tím môže zostať bottleneckom |
| Feedback | Automated tests | skoré odhalenie behavior alebo compatibility chyby | flaky alebo nereprezentatívny test vytvára falošnú dôveru |
| Feedback | Prometheus, Grafana, OpenTelemetry | runtime signals, correlation a canary evidence | chýbajúcu instrumentation a ownership backend nedoplní |
| Learning | Issue tracker a documentation | ownership postmortem actions a zachovanie rozhodnutí | dokument bez deadline-u a verification nemení systém |
| Learning | Feature flags a rollout controllers | controlled experiment a obmedzený exposure | flag bez lifecycle-u vytvára permanentnú complexity |

## 36. Časté omyly

### First Way znamená iba zrýchliť deployment

Flow pokrýva celý value stream od potreby po používateľský outcome. Rýchly deployment nevyrieši dvojdňový review queue ani nejasnú požiadavku.

### Second Way znamená viac dashboardov

Feedback musí byť relevantný, dôveryhodný a akčný. Dashboard bez decision ownera alebo contextu môže zvyšovať množstvo dát bez skrátenia correction time-u.

### Third Way ospravedlňuje chyby

Continual learning neodstraňuje standards ani accountability. Vytvára presnejšiu analýzu a zodpovednosť za systémovú remediation namiesto zjednodušeného obvinenia jednotlivca.

### Three Ways sa implementujú raz a potom sú hotové

Flow bottleneck, feedback needs a risk sa menia spolu s produktom a organizáciou. Three Ways sú trvalé vlastnosti a predmet continuous improvement.

## 37. Kontrolné otázky

1. Čo konkrétne tečie value streamom okrem ticketu?
2. Prečo stopercentná utilization všetkých tímov môže zvýšiť lead time?
3. Ako small batch size znižuje correction cost a blast radius?
4. Ako odlíšiš bottleneck od iba pomalého, ale neobmedzujúceho kroku?
5. Aké vlastnosti musí mať kvalitný feedback?
6. Prečo flaky test poškodzuje Second Way aj pri rýchlom vykonaní?
7. Aký rozdiel je medzi production telemetry a uzavretým feedback loopom?
8. Čo musí obsahovať bezpečný experiment?
9. Prečo blameless postmortem neznamená absenciu zodpovednosti?
10. Ako sa incident knowledge premieňa na trvalú capability?
11. Čo sa stane pri Flow bez Feedbacku a pri Feedbacku bez Flowu?
12. Ako by si auditoval všetky Three Ways na jednej konkrétnej službe?

## 38. Zhrnutie

First Way optimalizuje plynulý end-to-end tok práce a znižuje WIP, waiting, handoffs a batch size. Second Way vracia dôveryhodný a akčný feedback k miestu vzniku zmeny a prepája skoré tests s production evidence.

Third Way premieňa experiments, incidents a near misses na testy, automation, guardrails, runbooks a architecture zmeny. Vyspelý DevOps systém potrebuje všetky tri princípy naraz: schopnosť zlepšenie rýchlo doručiť, overiť jeho výsledok a zachovať získané learning v systéme.

## Glossary impact

Relevantné pojmy: Three Ways, First Way, Flow, Second Way, Feedback, Third Way, continual learning, WIP, batch size, bottleneck, built-in quality, stop-the-line, feedback latency, experiment hypothesis, blast radius, blameless postmortem, chaos engineering, game day, psychological safety, near miss a institutional learning.

## Primárne zdroje

- [IT Revolution — The DevOps Handbook](https://itrevolution.com/product/the-devops-handbook-second-edition/)
- [Google Cloud — DevOps capabilities](https://cloud.google.com/architecture/devops)
- [Google SRE — Postmortem Culture](https://sre.google/sre-book/postmortem-culture/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CALMS framework](calms.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Systems thinking →](systems-thinking.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
