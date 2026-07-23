# DevOps Lifecycle

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [SDLC](sdlc.md), [DevOps](devops.md)
- Súvisiace témy: CI/CD, testing, observability, incident management, DORA metrics

Metadata opisuje miesto kapitoly v učebnej ceste. DevOps lifecycle nie je názov jednej pipeline, ale model celého toku zmeny vrátane rozhodnutí pred commitom a učenia po nasadení.

## 1. Definícia

DevOps lifecycle je nepretržitý tok, ktorým zmena prechádza od identifikácie potreby cez implementáciu, overenie, release a deployment až po prevádzku, pozorovanie a ďalšie rozhodnutie. Prepája product, engineering a operations aktivity do jedného value streamu.

Lifecycle nemá definitívny koniec. Produkčné signály, incidenty, používateľský feedback a zmeny business prostredia vytvárajú nové vstupy do plánovania a môžu zmeniť pôvodnú požiadavku, testy alebo architecture.

## 2. Problém, ktorý lifecycle rieši

Samotný commit alebo dokončená backlog položka ešte nevytvára používateľskú hodnotu. Zmena musí byť správne pochopená, bezpečne transformovaná na artifact, nasadená, prevádzkovaná a overená na reálnom outcome-e.

Keď jednotlivé kroky vlastnia izolované tímy, zmena čaká vo frontoch a stráca kontext. Lifecycle model umožňuje zmerať celý tok, určiť ownership a identifikovať, kde vzniká waiting, rework, risk alebo oneskorený feedback.

Každá časť lifecycle-u znižuje iný typ neistoty:

- **Plan — neistota o probléme a hodnote**: tím určuje, čo má zmena dosiahnuť, pre koho a podľa akého dôkazu sa vyhodnotí úspech.
- **Code — neistota o realizovateľnosti**: návrh sa premieňa na verzovaný software, configuration, infrastructure a tests.
- **Build — neistota o reprodukovateľnom výstupe**: source inputs sa transformujú na jednoznačne identifikovaný artifact.
- **Test — neistota o správnosti a regresii**: automatizované a manuálne evidence preverujú contract a významné failure paths.
- **Release — neistota o pripravenosti verzie**: organizácia rozhoduje, či konkrétny artifact spĺňa risk a compatibility požiadavky.
- **Deploy — neistota o zmene prostredia**: artifact a configuration sa aplikujú v správnom poradí a s kontrolovaným failure behaviorom.
- **Operate — neistota o dlhodobom runtime stave**: služba sa škáluje, patchuje, zálohuje, chráni a obnovuje.
- **Monitor a learn — neistota o reálnom výsledku**: telemetry a feedback potvrdzujú alebo vyvracajú pôvodné predpoklady.

## 3. Mentálny model troch tokov

Klasický diagram zobrazuje smer zmeny k produkcii, ale lifecycle obsahuje tri súčasné toky. Ak jeden z nich chýba, systém môže dodávať rýchlo bez učenia alebo zbierať množstvo dát bez schopnosti reagovať.

```text
Plan → Code → Build → Test → Release → Deploy → Operate → Monitor
  ↑                                                        ↓
  └────────────────────── feedback ────────────────────────┘
```

- **Flow of work — presun hodnoty smerom k používateľovi**: source, artifact, configuration a rozhodnutia postupujú cez jednotlivé control points do runtime-u.
- **Flow of feedback — návrat evidence k tvorcom zmeny**: chyby kompilácie, tests, canary signals, incidents a user behavior ovplyvňujú ďalší krok.
- **Flow of learning — úprava samotného systému práce**: opakované zistenia menia architecture, platform capabilities, policies, test strategy a ownership.

Feedback bez learningu vedie k opakovaným incidentom. Learning bez flowu zostáva v postmortem dokumentoch, ktoré nemenia delivery systém.

## 4. Plan

Plan definuje problém, požadovaný outcome, priority, constraints a spôsob merania úspechu. Nejde iba o vytvorenie ticketu; plán musí poskytnúť dostatočný contract pre design, testing, rollout a produkčnú validáciu.

Dobrý plan vysvetlí používateľa alebo systém, ktorý zmenu potrebuje, a pomenuje najväčšie riziká a dependencies. Neznáme sa nemajú zakryť presným dátumom, ale premeniť na experiment, spike alebo menší inkrement.

Plan typicky vytvára tieto prepojené výstupy:

- **Change intent — presný dôvod zmeny**: vysvetľuje problém a zabraňuje tomu, aby implementácia optimalizovala iba technickú úlohu bez business outcome-u.
- **Acceptance criteria — pozorovateľný úspech**: určujú správanie, ktoré musí preukázať test alebo produkčný signal.
- **Non-functional requirements — prevádzkové hranice**: definujú reliability, security, latency, data a recovery požiadavky, ktoré ovplyvnia architecture.
- **Risk a rollout hypothesis — kontrola expozície**: pomenúva najnebezpečnejšie failure modes a spôsob, ako ich odhaliť pri malom blast radiuse.

Slabé plánovanie vedie k efektívnej implementácii nesprávnej veci. Príliš detailný plan bez feedbacku zase vytvára drahé záväzky založené na neoverených predpokladoch.

## 5. Code

Vo fáze Code vzniká verzovaná zmena application kódu, infrastructure, configuration, tests alebo dokumentácie. Source control uchováva nielen výsledné bytes, ale aj históriu rozhodnutí, review a väzbu na požiadavku.

Zmena má zostať malá a zrozumiteľná. Veľký commit kombinuje viac príčin a sťažuje review, test selection, rollback aj incident diagnosis.

Praktiky v tejto fáze majú konkrétnu úlohu:

- **Krátko žijúca vetva alebo trunk-based integrácia** — obmedzuje divergence od spoločného source-u a skracuje čas od vzniku konfliktu po jeho odhalenie.
- **Code review — kontrola change intentu a systémového dopadu**: reviewer overuje nielen syntax, ale aj assumptions, failure behavior, test coverage a operability.
- **Lokálne testy a linting — najrýchlejší feedback**: odhaľujú lacné chyby pred spustením vzdialenej pipeline a šetria shared compute aj čas ostatných ľudí.
- **Versioning configuration a infrastructure** — zachováva audit a reprodukovateľnosť všetkého, čo mení runtime, nie iba application source-u.

## 6. Build

Build transformuje deklarované source inputs na spustiteľný alebo distribuovateľný artifact. Môže kompilovať kód, získavať dependencies, generovať súbory, vytvárať package alebo container image a pripájať metadata o pôvode.

Dôveryhodný build je reprodukovateľný a izolovaný od náhodného stavu developer laptopu. Rovnaký revision a rovnaké deklarované dependencies majú vytvoriť ekvivalentný výstup alebo aspoň jednoznačne vysvetliteľný rozdiel.

Artifact types majú odlišný deployment contract:

- **Binary alebo JAR — application runtime artifact**: obsahuje skompilovaný program, ktorý stále potrebuje kompatibilný OS, runtime a configuration.
- **Container image — filesystem a process contract**: balí application dependencies a startup metadata, ale nie external state, secrets ani orchestrator policy.
- **Helm chart — Kubernetes release template**: balí templates a defaults; výsledný runtime závisí od chart version, values a cluster capabilities.
- **Terraform module package — reusable infrastructure definition**: poskytuje versioned interface, no skutočnú zmenu určuje provider version, variables, state a target APIs.
- **Static web bundle — client artifact**: môže byť nemenný, ale CDN caching a backend compatibility ovplyvňujú reálny rollout.

Build success nepreukazuje runtime correctness. Potvrdzuje iba to, že deklarovaný transformačný proces vytvoril artifact.

## 7. Artifact identity a provenance

Artifact musí mať stabilnú identitu, napríklad package version a content digest. Mutable tag typu `latest` nestačí na audit, pretože rovnaký názov môže neskôr ukazovať na iné bytes.

Provenance prepája artifact so source revisionom, build workflowom a použitými vstupmi. Pri incidente umožňuje zistiť, čo presne bolo nasadené, a pri promotion zabraňuje zámene testovaného výstupu za neskorší rebuild.

## 8. Test

Testovanie poskytuje evidence, že zmena spĺňa contract a že významné existujúce správanie zostalo zachované. Každý test pokrýva určitú boundary a môže zlyhať aj falošne uspieť, ak používa nereprezentatívne mocks, data alebo environment.

Test strategy kombinuje rýchlosť a realistickosť:

- **Unit test — izolovaná logika**: poskytuje rýchly feedback a presnú lokalizáciu chyby, ale nepreukazuje kompatibilitu s reálnou dependency.
- **Integration test — spolupráca komponentov**: overuje protocol, schema, authentication a state transitions na konkrétnej boundary.
- **Contract test — kompatibilita producer/consumer rozhrania**: odhaľuje breaking API alebo event zmenu bez potreby plného end-to-end prostredia.
- **Security scanning — známe supply-chain a code risks**: identifikuje vulnerability alebo policy violation, ale potrebuje triage a runtime context.
- **Infrastructure validation — syntax, plan a policy evidence**: ukazuje zamýšľanú zmenu resources, no nepreukazuje dostupnosť cloud capacity ani správne runtime správanie.
- **Performance a resilience test — správanie pod záťažou alebo faultom**: skúma saturation a recovery, ale výsledok platí iba pre testovaný workload a environment.
- **Smoke test — minimálna post-deployment funkčnosť**: rýchlo odhaľuje zásadný startup alebo routing failure, no nie kompletnú business correctness.

Testy nezaručujú absenciu chýb. Znižujú neistotu a musia byť doplnené progressive delivery a produkčným feedbackom.

## 9. Release

Release je rozhodnutie, že konkrétny artifact je pripravený na určené použitie. Môže zahŕňať version assignment, approval, signature, release notes, compatibility evidence a označenie artifactu ako promotable.

Release je logický a governance stav, nie nutne runtime zmena. Artifact môže byť vydaný ako kandidát, ale deployment sa môže uskutočniť neskôr alebo iba pre vybraného zákazníka.

Release contract má vysvetliť:

- **čo bolo schválené** — presný digest, chart version alebo package identity;
- **na základe akých dôkazov** — tests, scans, review, migration a risk evidence;
- **pre aký scope** — environment, Region, tenant alebo feature cohort;
- **s akými obmedzeniami** — known issues, compatibility a required configuration;
- **kto môže rozhodnutie zmeniť** — release owner, rollback authority a exception process.

## 10. Deploy

Deployment mení runtime alebo infrastructure state tak, aby prostredie používalo požadovanú verziu. Operácia zahŕňa viac než kopírovanie artifactu: musí riešiť configuration, identities, migrations, ordering, health a failure recovery.

Deployment je úspešný technicky vtedy, keď orchestration dokončí požadované kroky. Business úspech sa potvrdzuje až validáciou služby na používateľskom alebo SLO outcome-e.

Bezpečný deployment vysvetľuje:

- **ordering — poradie závislých zmien**: napríklad backward-compatible schema sa aplikuje pred code verziou, ktorá ju používa;
- **availability — správanie počas výmeny replicas**: minimum healthy capacity a draining chránia existujúci traffic;
- **configuration identity — presné runtime nastavenia**: deployment musí vedieť, ktoré values a secrets boli použité, nie iba artifact version;
- **verification — dôkaz po každom kritickom kroku**: readiness, smoke a synthetic test odlišujú vytvorený resource od fungujúcej služby;
- **rollback alebo roll-forward — cesta po failure**: strategy musí rešpektovať data compatibility a nesmie predpokladať, že všetko možno jednoducho vrátiť.

## 11. Rollout a exposure control

Rollout určuje, ako sa nasadená verzia sprístupňuje trafficu alebo používateľom. Rolling update, canary, blue-green a feature flag kontrolujú odlišné vrstvy a nemožno ich považovať za zameniteľné názvy.

Canary rollout znižuje blast radius iba vtedy, keď malý cohort reprezentuje hlavný workload a telemetry rozlišuje canary od baseline. Bez abort conditions a automatického alebo jasného manuálneho rozhodnutia je postupné nasadenie iba pomalší deployment.

## 12. Operate

Operate zahŕňa každodennú správu služby po release-i. Tím udržiava availability, capacity, security, data protection, dependency compatibility a schopnosť obnovy počas celého života systému.

Operations capabilities riešia odlišné failure classes:

- **Capacity management — dostatok resources pre demand a failover**: sleduje saturation, quotas, growth a provisioning latency.
- **Patching a dependency lifecycle — kontrola zastarávania a vulnerabilities**: plánuje upgrade, compatibility test a rollback skôr než skončí support window.
- **Certificate a secret lifecycle — zachovanie identity a trustu**: rotation musí prebehnúť pred expiráciou a bez prerušenia komunikácie.
- **Backup a restore — ochrana authoritative state-u**: backup success sa dopĺňa pravidelnou obnovou a application validation.
- **Incident response — obmedzenie dopadu a obnova služby**: on-call potrebuje telemetry, authority, runbook a bezpečné remediation mechanizmy.
- **Cost a resource hygiene — udržateľnosť služby**: nepoužívané resources, nebounded telemetry a zlá elasticity môžu meniť ekonomický contract produktu.

Prevádzka nie je fáza po dokončení vývoja. Každý incident, upgrade alebo capacity problém vytvára ďalšiu software a platform prácu.

## 13. Monitor, observe a validate

Monitoring sleduje vopred definované signály a conditions. Observability poskytuje širšie telemetry a context potrebný na skúmanie neznámych failure modes a prechod od symptómu ku konkrétnej request alebo dependency path.

Produkčná validácia musí kombinovať technické aj business signály:

- **Latency — čas na relevantnej user boundary**: ukazuje výkon, ale musí oddeľovať úspešné, neúspešné a queued operations.
- **Traffic — množstvo demandu**: poskytuje denominator a odlišuje reálny pokles používania od telemetry failure-u.
- **Errors — porušenie contractu**: zahŕňa timeout, invalid result alebo nedokončený async workflow, nie iba HTTP 5xx.
- **Saturation — čakanie a blízkosť limitu**: odhaľuje capacity risk skôr, než vznikne rozsiahly user impact.
- **Availability a SLO — podiel úspešných valid operations**: spája technický signal s reliability cieľom.
- **Business outcome — skutočná hodnota zmeny**: napríklad dokončené objednávky alebo spracované dokumenty potvrdzujú, že technicky zdravá služba robí správnu vec.

Telemetry uzatvára feedback loop iba vtedy, keď má ownera, decision threshold a cestu späť do backlogu alebo rollout controlu.

## 14. Fázy nie sú organizačné silá

Diagram lifecycle-u nehovorí, že každú fázu musí vlastniť iné oddelenie. Špecialisti môžu vykonávať rôznu prácu, ale value stream potrebuje spoločný outcome, spoločné metriky a jasné interfaces.

Chybný handoff model vyzerá takto:

```text
Product naplánuje
→ Development napíše
→ QA schváli
→ DevOps nasadí
→ Operations nesie incident
```

V tomto modeli sa feedback vracia cez tickety a každý tím optimalizuje svoju frontu. Cross-functional ownership neznamená, že každý ovláda všetko; znamená, že product a service tím zostáva zapojený do production výsledku a platform alebo security tím poskytuje self-service capabilities a expertízu.

## 15. Lifecycle nie je waterfall

Lineárny diagram je orientačný model dependency, nie povinné časové poradie všetkej práce. Tests, observability, security a deployment strategy sa navrhujú súbežne s application zmenou.

Prekrytie aktivít skracuje spätnú väzbu:

- **Threat modeling počas planningu** — mení design predtým, než vznikne zraniteľná implementation.
- **Test design spolu s contractom** — odhaľuje neoveriteľnú alebo nejasnú požiadavku ešte pred code review.
- **Observability spolu s feature** — zabezpečí, že rollout bude mať signal potrebný na rozhodnutie.
- **Deployment rehearsal pred release-om** — overí migrations, permissions a rollback skôr než production window.
- **Production experiment ako discovery input** — reálny feedback môže zmeniť ďalší product plán namiesto iba potvrdenia technickej stability.

## 16. Gates a feedback loops

Gate je decision point, ktorý na základe evidence povolí, zastaví alebo obmedzí pokračovanie zmeny. Feedback loop prenesie informáciu späť k miestu, kde možno príčinu opraviť alebo zmeniť predpoklad.

```text
failed integration test
→ gate zastaví promotion
→ report ukáže nekompatibilný contract
→ developer opraví source alebo test expectation
→ nový revision prejde lifecycle-om
```

Gate bez kvalitného feedbacku iba blokuje. Ak výsledkom je neurčité „policy failed“ bez pravidla, resource-u a remediation, ľudia hľadajú obchádzku namiesto opravy.

## 17. Lead time, processing time a wait time

Lead time meria end-to-end čas zmeny od definovaného začiatku po požadovaný výsledok. Skladá sa z active processingu, čakania, reworku a opakovaných cyklov.

```text
lead time = processing time + wait time + rework time
```

V mnohých organizáciách je samotné písanie kódu menšia časť celku. Najväčšie fronty vznikajú pri review, environment provisioning, manuálnych approvals, coordinated testovaní a release windows.

Typické waits treba vysvetľovať mechanizmom:

- **Čakanie na review — nedostatok reviewer capacity alebo príliš veľký change**: ďalšie paralelné rozpracovanie zvýši WIP a problém ešte zhorší.
- **Čakanie na environment — ticketový provisioning alebo zdieľané nestabilné prostredie**: self-service ephemeral environment môže odstrániť frontu, ale potrebuje cost a data guardrails.
- **Manuálne schválenie — governance bez automatizovaného evidence**: approval môže byť opodstatnený pri vysokom risku, ale nemá opakovať kontroly, ktoré už systém vykonal.
- **Front na testovanie — neskorá alebo centralizovaná quality ownership**: testability a automation sa musia presunúť do tímu a skorších fáz.
- **Deployment okno — strach z failure alebo shared dependency**: menšie batch sizes, progressive delivery a compatibility môžu znížiť potrebu koordinovanej udalosti.

## 18. Shift-left a shift-right

Shift-left presúva určité kontroly bližšie k vzniku zmeny, aby chyba vznikla aj bola odhalená v kratšom intervale. Neznamená, že vývojár sám preberá všetky security a operations povinnosti; platforma a expertíza majú poskytnúť použiteľné skoré mechanizmy.

Shift-right pokračuje vo validácii v runtime, pretože production traffic, scale a dependencies nemožno úplne simulovať. Obe stratégie sa dopĺňajú.

- **Threat modeling pri design-e — skorá kontrola trust boundaries**: môže zmeniť architecture ešte pred implementáciou.
- **Linting a unit tests pred commitom — okamžitý code feedback**: zachytia lacné chyby bez čakania na shared pipeline.
- **Policy checks v CI — opakovateľné governance evidence**: blokujú známy nepovolený configuration pred deploymentom.
- **Canary analysis po nasadení — runtime porovnanie verzií**: odhalí regresiu na reálnom trafficu pri malom blast radiuse.
- **Real user monitoring — user-experience evidence**: zachytí geografické, browser alebo network podmienky, ktoré synthetic test nemusí pokryť.
- **Chaos alebo fault experiments — overenie recovery assumptions**: testujú správanie pri zlyhaní, ale potrebujú hypotézu a kontrolovaný scope.

## 19. Automation lifecycle-u

Automation má znižovať variabilitu a feedback latency, nie zakrývať nejasné rozhodnutie. Pred automatizáciou sa definuje source of truth, input contract, success, failure, retry a rollback behavior.

Vyspelá automation poskytuje:

- **konzistentné vykonanie — rovnaký proces pre rovnaké vstupy**;
- **auditovateľnosť — väzbu medzi actorom, revisionom, artifactom a zmenou runtime-u**;
- **rýchly feedback — presný error a remediation pri najbližšom relevantnom kroku**;
- **bezpečné opakovanie — idempotency alebo explicitnú compensation po partial failure**;
- **kontrolu blast radiusu — environment, tenant alebo percentage scope a abort condition**.

Ak proces obsahuje zbytočný handoff alebo neurčitý approval, automatizácia jeho formulára nevyrieši príčinu čakania.

## 20. Build once, promote the same artifact

Princíp znamená, že build vytvorí artifact raz a ten istý digest sa presúva cez test, staging a production. Environment-specific hodnoty sa dodávajú cez configuration a secret contract, nie novou kompiláciou.

Tým sa zachováva platnosť test evidence: bytes overené v stagingu sú bytes nasadené do produkcie. Rebuild pre každé prostredie môže načítať inú dependency, base image alebo timestamp-generated obsah a vytvoriť nepozorovanú odchýlku.

## 21. End-to-end príklad

API má dostať nový voliteľný parameter bez porušenia starších clients. Plan preto definuje backward compatibility a signal, ktorý ukáže adoption a errors.

```text
Plan
  contract, compatibility a success metric
→ Code
  API, documentation, telemetry a tests
→ Build
  immutable image s digestom
→ Test
  unit, contract, integration, security a migration evidence
→ Release
  schválený digest a rollout policy
→ Deploy
  canary instance s rovnakou configuration schema
→ Operate
  capacity, logs, dependency a rollback readiness
→ Monitor
  error ratio, p95 latency, parameter adoption a old-client success
→ Learn
  pokračovať, zastaviť, upraviť contract alebo odstrániť feature
```

Každá fáza znižuje inú neistotu a vytvára evidence pre ďalšie rozhodnutie. Ak contract test chýba, canary môže ukázať failures až po vystavení reálnych clients; ak telemetry nerozlišuje novú operáciu, rollout nemá spoľahlivý decision signal.

## 22. Produkčný lifecycle contract

Vyspelý lifecycle má konzistentné interfaces medzi source, artifact, release a runtime. Nejde o povinný zoznam produktov, ale o capabilities, ktoré musia spolupracovať.

- **Versioning pravidlá — jednoznačná identita source-u a release-u**: umožňujú audit, dependency compatibility a presný rollback target.
- **Immutable artifacts — stabilný obsah počas promotion**: zabraňujú zámene testovaných a nasadených bytes.
- **Environment promotion bez rebuildu — zachovanie test evidence**: oddelí application artifact od environment configuration.
- **Automatizované quality gates — opakovateľné rozhodnutia podľa risku**: znižujú manuálne čakanie, ale musia poskytovať vysvetliteľný failure.
- **Spravované secrets — krátkodobé a scope-nuté runtime credentials**: zabraňujú tomu, aby environment values boli zabudované v artifacte alebo logoch.
- **Audit trail — trace source-to-runtime**: spája commit, build, approval, deployment actor a production version.
- **Progressive delivery — obmedzený exposure a meranie**: umožňuje zastaviť chybnú zmenu pred plným blast radiusom.
- **Observability naviazaná na release — porovnateľný runtime evidence**: version a deployment metadata umožňujú odlíšiť regresiu od všeobecného incidentu.
- **Rollback a incident postupy — pripravená recovery cesta**: tím pozná authority, data compatibility a validation po návrate alebo roll-forwarde.

## 23. Anti-patterny

### Lineárny handoff model

Každá fáza patrí inému tímu a zmena sa odovzdáva cez frontu bez spoločného ownershipu. Context sa stráca a chyba sa vracia cez rovnaký pomalý reťazec.

### Deployment ako koniec procesu

Pipeline označí job ako úspešný a backlog položka sa uzavrie bez production validation. Tím potom nevie, či sa feature používa, či zhoršila reliability alebo či vôbec rieši pôvodný problém.

### Monitoring bez spätnej väzby

Dashboardy a alerts existujú, ale zistenia nemenia tests, backlog ani architecture. Telemetry sa stáva nákladným archívom namiesto riadiaceho vstupu.

### Veľké batch releases

Mnoho nezávislých zmien sa kombinuje do jednej udalosti. Blast radius, coordination a počet možných príčin rastú a rollback môže odstrániť aj zdravé capabilities.

### Environment-specific rebuild

Každé prostredie dostane iné bytes, takže staging evidence sa nevzťahuje na production artifact. Rozdiel môže vzniknúť aj bez source zmeny cez mutable dependency alebo base image.

## 24. Troubleshooting lifecycle-u

Pri audite nehodnoť iba trvanie pipeline. Zmeraj cestu change requestu, source revisionu, artifactu, approvalu, deploymentu a produkčného feedbacku.

Typické symptómy treba mapovať na konkrétny flow problem:

- **Veľa práce je „takmer hotovej“ — vysoký WIP a handoff queues**: obmedz nové začiatky a dokonči review, test alebo deployment bottleneck.
- **Pipeline je zelená, incidenty rastú — gates nekorelujú s production riskom**: porovnaj test coverage, failure classes a release verification s reálnymi incidentmi.
- **Release čaká na jeden tím — centralizovaný decision alebo environment interface**: zaveď self-service, delegated ownership alebo risk-based automation namiesto presunu ďalších ticketov.
- **Canary nevie rozhodnúť — chýba baseline, version metadata alebo business signal**: instrumentation musí byť súčasťou feature a rollout plánu.
- **Rollback zlyháva — data alebo configuration nie sú backward-compatible**: lifecycle musí uprednostniť expand/contract, roll-forward a testovanú recovery cestu.

## 25. Praktické pozorovanie existujúceho procesu

Value-stream audit má vytvoriť merateľný model, nie iba pekný diagram. Pri každom kroku zaznamenaj ownera, vstup, výstup, active time, wait time, failure rate a feedback destination.

Otázky vedú k odhaleniu konkrétnej medzery:

1. Kde zmena vzniká a kedy sa začína merať lead time?
2. V ktorých frontoch čaká a kto riadi ich kapacitu?
3. Ktoré manuálne kroky pridávajú rozhodnutie a ktoré iba prepisujú údaje?
4. Ktoré kontroly odhaľujú chybu až po veľkom množstve ďalšej práce?
5. Kde vzniká artifact a či sa jeho obsah medzi prostrediami mení?
6. Aký dôkaz potvrdzuje deployment a aký potvrdzuje user outcome?
7. Kam sa produkčné zistenia zapisujú a kto vlastní následnú zmenu?
8. Kto rozhoduje o službe po nasadení a počas incidentu?

## 26. Časté omyly

### Lifecycle je názov CI pipeline

Pipeline automatizuje časť build, test a deployment toku. Lifecycle zahŕňa aj discovery, ownership, production operation, incidenty, user feedback a zmenu samotného systému práce.

### Monitor je posledný krok

Monitorovanie vytvára vstup do ďalšieho rozhodnutia. Ak telemetry nemení rollout, backlog alebo architecture, regulačná slučka zostala otvorená.

### Každá fáza musí byť pipeline stage

Fázy sú konceptuálne responsibilities a evidence boundaries. Konkrétna pipeline môže niektoré kroky kombinovať alebo vykonávať paralelne podľa architecture a risku.

### Čím viac gates, tým bezpečnejší proces

Gate znižuje risk iba vtedy, keď používa relevantné evidence a poskytuje rýchly feedback. Redundantné alebo nepresné gates predlžujú lead time a motivujú ľudí hľadať obchádzky.

## 27. Kontrolné otázky

1. Prečo DevOps lifecycle nekončí deploymentom?
2. Aké tri toky predstavujú work, feedback a learning?
3. Aký je rozdiel medzi buildom, release-om, deploymentom a rolloutom?
4. Prečo rovnaký artifact treba promovať medzi prostrediami bez rebuildu?
5. Ktorý typ neistoty znižuje každá hlavná fáza lifecycle-u?
6. Ako sa líši gate od feedback loopu?
7. Prečo fázy nemajú byť mapované na izolované tímy?
8. Ktoré časti lead time-u typicky vznikajú čakaním?
9. Ako sa shift-left a shift-right dopĺňajú pri tej istej zmene?
10. Aké evidence potrebuje canary rollout na dôveryhodné rozhodnutie?
11. Prečo zelená pipeline nemusí znamenať zdravý delivery lifecycle?
12. Ako by si auditoval existujúci value stream bez optimalizácie nesprávneho kroku?

## 28. Zhrnutie

DevOps lifecycle pokrýva celý tok od potreby po produkčné učenie. Plan, Code, Build, Test, Release, Deploy, Operate a Monitor sú responsibilities a evidence boundaries, nie povinné organizačné silá alebo názvy pipeline stages.

Zmena smeruje k používateľovi, feedback sa vracia k tvorcom a learning mení celý systém. Zdravý lifecycle zmenšuje batch sizes, podporuje promotion rovnakého artifactu, kontroluje exposure a meria end-to-end lead time aj production outcome.

## Glossary impact

Relevantné pojmy: DevOps lifecycle, flow of work, flow of feedback, flow of learning, change intent, artifact identity, provenance, release, deployment, rollout, gate, feedback loop, lead time, processing time, wait time, shift-left, shift-right a artifact promotion.

## Primárne zdroje

- [Google Cloud — DevOps capabilities](https://cloud.google.com/architecture/devops)
- [DORA — Research program](https://dora.dev/)
- [NIST Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: DevOps](devops.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: CALMS framework →](calms.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
