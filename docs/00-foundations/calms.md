# CALMS Framework

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [DevOps](devops.md), [DevOps Lifecycle](devops-lifecycle.md)
- Súvisiace témy: culture, automation, Lean, measurement, sharing, DORA metrics

Metadata zaraďuje CALMS za všeobecný DevOps operating model. Rámec sa používa na diagnostiku schopností a ich vzájomných väzieb, nie ako univerzálna certifikačná stupnica.

## 1. Definícia

CALMS je diagnostický rámec, ktorý skúma DevOps schopnosť organizácie cez päť oblastí: Culture, Automation, Lean, Measurement a Sharing. Každá oblasť opisuje inú podmienku potrebnú na bezpečný a rýchly tok zmien.

Skratka nepredstavuje päť nezávislých projektov. Hodnota vzniká ich kombináciou: automation potrebuje dôveru a jasný ownership, Lean potrebuje measurement na identifikáciu bottlenecku a sharing premieňa lokálne zistenie na opakovateľnú schopnosť celej organizácie.

- **Culture — spôsob spolupráce a rozhodovania**: určuje, či tímy zdieľajú outcome, hovoria otvorene o riziku a učia sa zo zlyhaní.
- **Automation — konzistentné vykonávanie pochopeného procesu**: znižuje manuálnu variabilitu, feedback latency a závislosť od individuálnej pamäte.
- **Lean — optimalizácia end-to-end flowu**: zmenšuje batch sizes, waiting, handoffs, rework a nadmernú rozpracovanosť.
- **Measurement — evidence pre rozhodnutie**: spája delivery flow, reliability a business outcome a ukazuje, či zmena systému priniesla výsledok.
- **Sharing — distribúcia znalostí a spätnej väzby**: zabraňuje tomu, aby kritický context zostal v jednom tíme, dokumente bez ownera alebo hlave jedného človeka.

## 2. Problém, ktorý CALMS rieši

DevOps transformácia sa často redukuje na nákup technológií alebo vytvorenie centralizovaného pipeline tímu. Toolchain sa zmení, ale konfliktné ciele, manuálne approvals a nejasný production ownership zostanú rovnaké.

CALMS núti posudzovať celý socio-technický systém. Ak deployment zostáva mesačnou rizikovou udalosťou, nestačí sa pýtať, ktorý orchestrator chýba; treba skúmať veľkosť batchu, trust medzi tímami, kvalitu feedbacku, rozhodovacie metriky a dostupnosť prevádzkových znalostí.

Typické symptómy ukazujú na kombináciu oblastí:

- **Moderná platforma, ale dlhý lead time** — Automation existuje, no Lean flow môže zostať blokovaný approvals, frontami a veľkými batchmi.
- **Tímy spolupracujú, ale robia veľa ručných chýb** — Culture je relatívne zdravá, no chýba Automation a štandardizovaný execution contract.
- **Veľa dashboardov bez zlepšenia** — Measurement produkuje čísla, ale Culture a governance ich nepoužívajú na experiment alebo rozhodnutie.
- **Opakované incidenty s rovnakou príčinou** — feedback vzniká, ale Sharing a institutional learning ho nepremenili na test, guardrail alebo architecture zmenu.

## 3. Mentálny model závislostí

CALMS je vhodné predstaviť si ako päť spojených control surfaces. Zlyhanie jednej oblasti znižuje účinnosť ostatných, preto výsledok nemožno vypočítať jednoduchým súčtom jednotlivých bodov.

```text
Culture
  vytvára dôveru, ownership a bezpečný feedback
       ↓
Lean ───────────────→ určuje, ktorý flow problém má zmysel riešiť
       ↓                                  ↓
Automation ─────────→ vykonáva zjednodušený proces konzistentne
       ↓                                  ↓
Measurement ←─────── sleduje flow, reliability a outcome
       ↓
Sharing
  distribuuje evidence, rozhodnutia a naučené mechanizmy späť do systému
```

Napríklad automation môže skrátiť technický deployment z hodiny na desať minút. Ak release stále čaká tri dni na nejasné manuálne schválenie, Lean a Measurement ukážu, že hlavný bottleneck zostal mimo automatizovaného kroku.

## 4. Culture

Culture opisuje správanie, motivácie a decision patterns, ktoré vznikajú medzi ľuďmi a tímami. Nie je to neurčitá požiadavka „lepšie komunikovať“, ale súbor podmienok ovplyvňujúcich, či sa risk zviditeľní, či je outcome spoločný a či sa po chybe zmení systém.

Zdravá DevOps culture má viac prepojených vlastností:

- **Shared ownership — spoločná zodpovednosť za service outcome**: development, platform a operations neprenášajú production problém cez hranicu role bez ďalšieho záujmu o výsledok.
- **Psychological safety — možnosť oznámiť neistotu a chybu bez ponižovania**: ľudia eskalujú near miss alebo nebezpečný workaround skôr, než sa z neho stane incident.
- **Transparency — viditeľné rozhodnutia, fronty a riziká**: tím dokáže vysvetliť, prečo sa zmena zastavila a kto vlastní ďalší krok.
- **Cross-functional collaboration — expertíza dostupná v správnom čase**: security, database alebo operations poznatok vstupuje do designu, nie až do neskorého approval gate-u.
- **Learning response to failure — analýza systémových podmienok**: post-incident review hľadá chýbajúce controls, zlé defaults a nepresné feedback loops namiesto jednoduchého označenia vinníka.
- **Autonomy within guardrails — lokálne rozhodnutie v jasnej boundary**: tímy nemusia čakať na centralizovaný ticket pri každej bežnej zmene, ale poznajú policy, budget a escalation path.
- **Outcome orientation — hodnotenie výsledku namiesto objemu aktivity**: počet commitov alebo ticketov nie je náhradou za flow, reliability a používateľskú hodnotu.

Culture sa prejavuje v rozhodnutiach pod tlakom. Organizácia môže deklarovať blameless prístup, ale ak incident review ovplyvňuje odmenu jednotlivca a nefinancuje remediation, ľudia sa naučia risk skrývať.

## 5. Culture failure modes

Konfliktné incentives sú častou príčinou slabého DevOps modelu. Ak development získava uznanie za feature throughput a operations za blokovanie zmien, každý tím racionálne optimalizuje metriku, ktorá poškodzuje spoločný flow.

Ďalšie culture failures majú konkrétne dôsledky:

- **Hero culture — oceňovanie opakovaných manuálnych záchran**: organizácia investuje do jednotlivca schopného hasiť incident namiesto odstránenia príčiny potreby zásahu.
- **Blame culture — trestanie nositeľa zlej správy**: incidenty a near misses sa hlásia neskoro a evidence je neúplné.
- **Ownership without capability — povinnosť bez nástrojov a času**: príkaz „you build it, you run it“ bez telemetry, runbookov a reliability kapacity iba presunie stres.
- **Central approval dependency — dôvera nahradená frontou**: každý tím čaká na malú skupinu administrátorov, ktorá nemá context ani kapacitu na včasné rozhodnutia.

## 6. Automation

Automation premieňa opakovateľný a pochopený proces na versioned, konzistentné a auditovateľné vykonanie. Jej cieľom nie je odstrániť človeka za každú cenu, ale presunúť jeho pozornosť z mechanického opakovania na návrh, exception handling a zlepšovanie systému.

Automation je účinná v rôznych častiach lifecycle-u:

- **Build a test automation — rovnaké kontroly pre každý revision**: znižuje rozdiel medzi lokálnym prostredím a shared evidence a poskytuje feedback pred merge alebo release-om.
- **Infrastructure provisioning — deklaratívne a opakovateľné prostredia**: nahrádza console clicks versionovaným change planom a umožňuje recovery alebo review.
- **Configuration management — kontrola desired state-u a driftu**: distribuuje nastavenia podľa definovaného contractu a odhaľuje neautorizované odchýlky.
- **Deployment automation — riadený ordering, verification a rollback**: znižuje manuálnu variabilitu pri zmene runtime-u a zachováva audit trail.
- **Policy enforcement — konzistentné organization guardrails**: kontroluje známe pravidlá pri source, build, admission alebo runtime boundary namiesto občasnej manuálnej kontroly.
- **Security scanning — opakované hľadanie známych risks**: poskytuje triage input, ale nenahrádza threat modeling ani posúdenie exploitability.
- **Backup a recovery automation — pravidelné vytváranie a testovanie recovery points**: znižuje manuálne oneskorenie, no potrebuje application validation a izoláciu credentials.
- **Incident enrichment — context pri prvom page-i**: pripája recent deployments, ownership, dependency a runbook, aby responder nezačínal z prázdneho alertu.
- **Environment creation — self-service v guardrails**: odstraňuje ticketovú frontu, pričom policy, quotas a cleanup chránia cost a security.

## 7. Automation lifecycle a hranice

Rozumné poradie začína pochopením problému. Ak tím automatizuje proces s piatimi zbytočnými approvals, výsledkom je rýchlejšie odosielanie formulárov, nie kratší flow.

```text
pozorovať a zmerať proces
→ odstrániť kroky bez hodnoty
→ definovať vstupy, výstupy a failure semantics
→ štandardizovať bežnú cestu
→ automatizovať
→ merať outcome a udržiavať automation
```

Automation musí riešiť partial failure, retries, permissions a rollback. Script, ktorý funguje iba pri ideálnom stave a pri chybe vyžaduje zásah pôvodného autora, presúva toil namiesto jeho odstránenia.

## 8. Lean

Lean optimalizuje plynulý tok hodnoty cez celý value stream. Neznamená „robiť viac s menším počtom ľudí“; znižuje waiting, nadmernú rozpracovanosť, handoffs, rework a prácu, ktorá nevytvára požadovaný outcome.

Flow problémy sa prejavujú rôznymi merateľnými javmi:

- **Wait time — čas, keď práca nepokračuje**: review alebo environment queue môže tvoriť väčšinu lead time-u, aj keď active processing je rýchly.
- **Handoff — presun ownershipu a contextu**: každé odovzdanie pridáva frontu, potrebu vysvetlenia a riziko, že ďalší tím optimalizuje iný cieľ.
- **Work in progress — množstvo nedokončenej práce**: vysoký WIP zvyšuje multitasking a čas, počas ktorého sa požiadavka alebo branch môže stať zastaranou.
- **Batch size — množstvo zmien viazaných na jedno rozhodnutie**: veľký release zväčšuje blast radius, test scope a počet možných príčin incidentu.
- **Rework — opakovaná oprava už vykonanej práce**: často signalizuje neskorý feedback, nejasný contract alebo nekonzistentné prostredie.
- **Bottleneck — krok obmedzujúci throughput celku**: zrýchlenie inej časti iba zväčší front pred obmedzením.

## 9. Small batch sizes a WIP limits

Malé batch sizes skracujú interval medzi vznikom zmeny a jej overením. Pri code change znižujú review complexity a pri deployment-e zmenšujú blast radius a počet premenných počas diagnosis.

Jednotlivé výhody majú konkrétny dôvod:

- **Jednoduchší review — menší cognitive scope**: reviewer dokáže pochopiť change intent a failure paths bez kombinácie viacerých tém.
- **Rýchlejšie testovanie — užší affected surface**: test selection a diagnosis sa viažu na menší počet komponentov, hoci kritická zmena stále môže vyžadovať široké testy.
- **Bezpečnejší rollout — menší počet súčasných rizík**: canary signal sa ľahšie priradí konkrétnej zmene.
- **Rýchlejší rollback alebo roll-forward — menšia kompatibilitná medzera**: návrat neodstráni veľký balík zdravých funkcií spolu s jednou chybnou.

WIP limit obmedzuje počet rozpracovaných položiek, aby tím dokončoval bottleneck namiesto zakladania ďalšej práce. Stopercentná utilization každého človeka odstraňuje rezervu na variabilitu, review a incidenty a zvyšuje celkový waiting time.

## 10. Value stream a bottleneck

Value stream je celý tok od potreby po používateľskú hodnotu a produkčný feedback. Zahŕňa active work, waiting, approvals, technical systems aj organizačné decision points.

Predstav si build trvajúci osem minút a release čakajúci tri dni na manuálne schválenie. Zrýchlenie build cache o dve minúty je lokálne zlepšenie, ale odstránenie nejasnej approval fronty môže skrátiť lead time o dni.

Bottleneck sa po optimalizácii môže presunúť. Lean preto nie je jednorazové mapovanie procesu, ale opakované meranie a zlepšovanie aktuálneho obmedzenia.

## 11. Measurement

Measurement poskytuje evidence o správaní delivery systému, prevádzkovanej služby a business výsledku. Metrika má podporiť konkrétne rozhodnutie; bez ownera, threshold-u alebo experimentu je dashboard iba pasívny report.

Rozličné metric families odpovedajú na odlišné otázky:

- **Flow metrics — kde a ako dlho sa pohybuje práca**: lead time, cycle time, throughput, wait time a WIP odhaľujú fronty a bottlenecks v delivery systéme.
- **Delivery metrics — ako často a bezpečne sa mení produkcia**: deployment frequency, lead time for changes, change failure rate a recovery time spájajú throughput so stability outcome-om.
- **Reliability metrics — čo zažíva používateľ v runtime**: availability, latency, errors, SLI, SLO a incident frequency merajú service contract a jeho porušenia.
- **Outcome metrics — či zmena priniesla hodnotu**: adoption, conversion, task completion alebo satisfaction odlišujú technicky zdravú feature od užitočného produktu.

Metriky musia mať presnú definíciu scope-u a denominatora. „Počet deploymentov“ bez určenia environmentu, úspechu a change identity možno interpretovať viacerými spôsobmi a ľahko manipulovať.

## 12. Goodhartov problém a metric safety

Keď sa metrika stane individuálnym cieľom alebo odmenou, ľudia optimalizujú číslo namiesto systému. Cieľ „viac deploymentov“ môže viesť k umelému deleniu zmien a počet uzavretých ticketov k zakladaniu menších, no stále nehodnotných položiek.

Bezpečné measurement používa balanced metrics, trend a context. DORA ukazovatele sa posudzujú spoločne, pretože vysoká frequency bez change quality alebo rýchly lead time bez reliability nie je zdravý delivery outcome.

Measurement bez zdravej Culture môže znižovať pravdivosť dát. Ak číslo slúži na trest, tímy menia klasifikáciu incidentu alebo skrývajú manual work namiesto odstránenia príčiny.

## 13. Sharing

Sharing premieňa individuálnu znalosť na dostupné a udržiavané informačné rozhranie. Neznamená viac meetingov ani hromadné kopírovanie dokumentov; informácia musí byť nájditeľná, dôveryhodná, aktuálna a prepojená s prácou, ktorú podporuje.

Mechanizmy zdieľania slúžia rôznym potrebám:

- **Code review — distribúcia change contextu**: viac ľudí rozumie designu a zároveň sa decisions zachovajú pri source zmene.
- **Runbook — vykonávacie knowledge pri known failure**: opisuje význam alertu, dôkazy, bezpečné remediation a validation, nie iba zoznam príkazov.
- **Architecture Decision Record — zachovanie dôvodu rozhodnutia**: budúci tím vie, ktoré constraints a trade-offs viedli k súčasnému návrhu.
- **Post-incident review — prenos runtime learningu**: prepája incident evidence s konkrétnou zmenou tests, guardrails, architecture alebo ownershipu.
- **Service catalog — nájditeľnosť ownera a dependencies**: umožňuje rýchlo určiť, kto službu vlastní, čo spotrebúva a aký má operational contract.
- **Community of practice — zdieľanie expertízy naprieč tímami**: vytvára reusable patterns bez centralizácie všetkých rozhodnutí do jedného delivery bottlenecku.
- **Pairing a interné školenie — prenos tacit knowledge**: pomáhajú pri činnostiach, ktoré samotný dokument nedokáže úplne zachytiť.

## 14. Knowledge lifecycle

Dokumentácia bez ownera a lifecycle-u sa rýchlo stane nedôveryhodná. Ak incident responder opakovane nájde neaktuálny runbook, prestane veriť aj správnym dokumentom.

Knowledge má vznikať spolu so zmenou a byť overované používaním. Runbook sa testuje počas game day alebo incidentu, architecture record sa aktualizuje pri zmene decisionu a service catalog sa synchronizuje s account alebo repository lifecycle-om.

Sharing znižuje bus factor iba vtedy, keď druhý človek dokáže informáciu skutočne použiť. Uloženie videa bez indexu, textového contractu a ownera je archív, nie operational capability.

## 15. Vzájomné zlyhania CALMS oblastí

Oblasti sa navzájom obmedzujú a rovnaký symptom môže mať viac príčin. Diagnostika preto nemá priradiť problém iba jednému písmenu bez overenia dependencies.

- **Automation bez Culture — centralizované nové silo**: malý platform tím vlastní všetky pipelines a ostatné tímy čakajú na zmenu namiesto self-service a shared ownershipu.
- **Culture bez Automation — dobrá spolupráca s vysokou variabilitou**: ľudia si pomáhajú, ale manuálne deploymenty a recovery závisia od pamäte a vytvárajú opakované chyby.
- **Automation bez Lean — zrýchlenie odpadu**: komplikovaný approval a handoff proces sa vykonáva elektronicky, no end-to-end waiting zostane.
- **Measurement bez Culture — trestajúce čísla**: tímy optimalizujú klasifikáciu a reporting, pretože metriky sa používajú proti nim.
- **Lean bez Measurement — zlepšenie podľa dojmu**: tím nevie, či odstránil hlavný bottleneck alebo iba presunul frontu.
- **Sharing bez štandardov — množstvo nedôveryhodných informácií**: duplicity a neaktuálne návody zvyšujú čas hľadania namiesto jeho zníženia.

## 16. End-to-end CALMS audit

Predstav si tím, ktorý nasadzuje raz mesačne, deployment trvá štyri hodiny a často potrebuje manuálny zásah. CALMS audit rozkladá symptom na overiteľné hypotheses.

| Oblasť | Pozorovanie | Čo mechanizmus znamená | Ďalší dôkaz |
|---|---|---|---|
| Culture | Deployment vlastní izolovaný Ops tím | Product tím nemá production feedback ani authority zmeniť delivery path | Kto rozhoduje o rollbacku a kto vlastní incident follow-up? |
| Automation | Kroky sa vykonávajú podľa checklistu | Execution závisí od poradia a pamäte operátora a partial failure sa rieši improvizovane | Koľko krokov je stabilných, opakovateľných a vhodných na versioned automation? |
| Lean | Mesačný batch obsahuje mnoho zmien | Veľký scope zväčšuje test, coordination a diagnosis a spätne posilňuje strach z deploymentu | Aký je wait time, WIP a veľkosť typického release-u? |
| Measurement | Sleduje sa iba status deployment jobu | Tím nevie, kde vzniká lead time ani či zmena poškodila user outcome | Poznáme flow, change failure, recovery a business metrics? |
| Sharing | Postup poznajú dvaja administrátori | Recovery a execution majú human single point of failure | Existuje verzovaný, testovaný runbook a dostupný backup owner? |

Audit nevytvára automaticky solution backlog podľa názvov nástrojov. Najprv identifikuje obmedzenie a až potom navrhne experiment, napríklad zmenšenie batchu a automatizáciu jedného stabilného deployment pathu.

## 17. Praktické auditné otázky

Otázky majú odhaliť konkrétnu boundary alebo chýbajúci dôkaz, nie iba vyvolať diskusiu.

### Culture

- **Kto vlastní service outcome po deployment-e?** — odhalí, či ownership končí handoffom alebo zahŕňa runtime a learning.
- **Ako tím reaguje na chybu alebo near miss?** — ukáže, či sa risk zviditeľňuje alebo skrýva pre blame a incentives.
- **Sú lokálne ciele kompatibilné?** — porovná feature throughput, change approvals, security a reliability expectations.
- **Môže človek zastaviť nebezpečný rollout?** — overí psychologickú aj formálnu authority konať pri riziku.

### Automation

- **Ktoré manuálne kroky sú stabilné a opakované?** — identifikuje automation kandidátov namiesto jednorazových výnimiek.
- **Je automation versioned, testovaná a reviewovaná?** — odlišuje engineering capability od osobného scriptu.
- **Čo sa stane po partial failure alebo retry?** — overuje idempotency, compensation a recovery semantics.
- **Existuje audit trail source-to-runtime?** — ukáže, či možno priradiť zmenu k actorovi, artifactu a výsledku.

### Lean

- **Kde práca čaká a prečo?** — oddeľuje active work od queue, approval a dependency delay.
- **Aký veľký je typický batch?** — ukazuje blast radius a feedback interval.
- **Koľko položiek je rozpracovaných?** — odhaľuje multitasking a skrytý inventory práce.
- **Ktorý krok obmedzuje throughput celku?** — zabraňuje optimalizácii neobmedzujúcej lokálnej aktivity.

### Measurement

- **Meriame activity, flow, reliability alebo outcome?** — odlíši počet vykonaných krokov od výsledku pre používateľa.
- **Ktoré rozhodnutie metrika mení?** — odhaľuje dashboards bez action contractu.
- **Aký je numerator, denominator a scope?** — preverí, či má číslo stabilnú a porovnateľnú semantics.
- **Ako možno metriku manipulovať?** — identifikuje Goodhart risk a potrebu balanced metrics.

### Sharing

- **Kde sa nachádza authoritative knowledge?** — odlíši udržiavaný source od viacerých konfliktných kópií.
- **Kto informáciu vlastní a kedy sa overila?** — odhaľuje orphaned dokumentáciu.
- **Aktualizuje sa knowledge spolu so zmenou?** — preverí, či docs a runbooks driftujú od runtime-u.
- **Dokáže nový člen vykonať úlohu bez neformálnej eskalácie?** — testuje skutočný bus factor a použiteľnosť rozhrania.

## 18. Anti-patterny

### Tooling-first CALMS

Automation sa považuje za jediný technicky vážny pilier. Organizácia potom investuje do platformy, ale neodstráni conflicting incentives, waiting ani neprístupný production feedback.

### Vanity metrics

Meriavajú sa ľahko dostupné čísla, napríklad počet commitov alebo pipeline jobs na osobu. Tieto čísla možno zvýšiť bez zlepšenia flow, reliability alebo používateľskej hodnoty.

### Knowledge dumping

Sharing sa zamieňa za vytvorenie veľkého množstva dokumentov. Bez informačnej architecture, ownera, review dátumu a prepojenia na workflow sa zvyšuje search cost a klesá dôvera.

### Permanentná transformácia bez outcome-u

Organizácia vykonáva workshopy, reorganizácie a tool migrations, ale nemá baseline ani cieľový flow alebo reliability outcome. Transformácia sa stane aktivitou, ktorá nemôže byť označená za úspešnú ani ukončená.

## 19. Časté omyly

### CALMS je univerzálne maturity score

CALMS môže organizovať assessment, ale neexistuje jedno správne číslo pre všetky produkty. Kritický regulovaný systém a malý interný tool potrebujú odlišné controls, automation aj measurement depth.

### Automation je najdôležitejšia časť, pretože je technická

Automation iba vykonáva zvolený proces. Bez zdravej Culture a Lean môže stabilizovať silo alebo zrýchliť kroky, ktoré by sa mali odstrániť.

### Sharing znamená viac meetingov

Sharing vytvára dostupné informačné interfaces a spätnú väzbu. Asynchrónny ADR, testovaný runbook alebo service catalog môže byť hodnotnejší než opakovaný meeting bez zachovaného rozhodnutia.

### Lean znamená maximalizovať vyťaženosť a znížiť headcount

Lean optimalizuje flow a odstraňuje waste. Systém bez rezervnej kapacity má dlhé queues a nevie reagovať na variabilitu, incident ani review potrebu.

## 20. Kontrolné otázky

1. Prečo CALMS nie je päť nezávislých transformačných projektov?
2. Ako Culture ovplyvňuje pravdivosť Measurement dát?
3. Prečo sa proces pred automatizáciou najprv zjednodušuje?
4. Ako WIP limit znižuje waiting time a multitasking?
5. Aký je rozdiel medzi flow, delivery, reliability a outcome metrics?
6. Prečo môže vysoká deployment frequency bez ďalších metrík zavádzať?
7. Ako Sharing premieňa incident z individuálnej skúsenosti na systémovú schopnosť?
8. Čo vznikne pri Automation bez Lean a pri Lean bez Measurement?
9. Ktoré CALMS oblasti by si skúmal pri trojdňovom approval waitingu a prečo?
10. Ako navrhneš CALMS experiment s merateľným outcome-om namiesto neurčitej transformácie?

## 21. Zhrnutie

CALMS skúma DevOps schopnosť cez Culture, Automation, Lean, Measurement a Sharing. Oblasti sa navzájom podmieňujú a slabá boundary môže obmedziť hodnotu celého delivery systému.

Culture vytvára podmienky na pravdivý feedback a ownership, Lean určuje, čo treba zlepšiť, Automation vykonáva stabilný proces, Measurement overuje výsledok a Sharing zachováva learning. Rámec je najužitočnejší ako diagnostika a návrh malého experimentu, nie ako rebríček nástrojov alebo jediné maturity číslo.

## Glossary impact

Relevantné pojmy: CALMS, Culture, Automation, Lean, Measurement, Sharing, psychological safety, WIP limit, batch size, value stream, bottleneck, Goodhartov zákon, bus factor a knowledge lifecycle.

## Primárne zdroje

- [DORA — Research program](https://dora.dev/)
- [Google Cloud — DevOps capabilities](https://cloud.google.com/architecture/devops)
- [The Lean Enterprise Institute — What is Lean Thinking?](https://www.lean.org/explore-lean/what-is-lean-thinking/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: DevOps lifecycle](devops-lifecycle.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Three Ways of DevOps →](three-ways.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
