# CALMS Framework

CALMS je diagnostický rámec pre päť navzájom závislých schopností: Culture, Automation, Lean, Measurement a Sharing. Nie je to maturity checklist, v ktorom organizácia samostatne „splní“ päť položiek. Každá dimenzia mení správanie ostatných a slabá hranica v jednej oblasti môže znehodnotiť zvyšok systému.

Automation napríklad zrýchli deployment, ale bez culture bezpečného priznania chyby sa incidenty skryjú. Measurement vytvorí veľa dashboardov, ale bez Lean práce s WIP a bottleneckmi sa metriky nepremenia na rozhodnutie. Sharing rozšíri runbooky, no bez ownershipu a reálnych rehearsals zostanú neaktuálnou dokumentáciou.

CALMS sa preto používa nad konkrétnym value streamom. Najprv sa určí user alebo business outcome, následne sa sleduje tok práce, rozhodnutia, automation boundaries, dostupné evidence a spôsob učenia. Výsledkom nie je skóre samo osebe, ale hypotéza o tom, ktorý systémový constraint bráni bezpečnejšiemu a rýchlejšiemu flowu.

## 1. CALMS nie je zoznam piatich nezávislých iniciatív

CALMS je diagnostický rámec pozostávajúci z oblastí Culture, Automation, Lean, Measurement a Sharing. Každá oblasť skúma inú podmienku delivery systému, ale výsledok vzniká až ich interakciou.

```text
Culture
  určuje ownership, dôveru a decision rights
        ↓
Lean
  odhaľuje, ktorý problém vo flowe je skutočný bottleneck
        ↓
Automation
  vykonáva zjednodušený proces konzistentne
        ↓
Measurement
  overuje, či sa flow, reliability a outcome zlepšili
        ↓
Sharing
  premieňa lokálne zistenie na opakovateľnú schopnosť
        └────────────────────────────────────────────↺
```

Automation bez Lean môže iba zrýchliť zbytočný proces. Measurement bez Culture môže motivovať tímy manipulovať čísla. Sharing bez ownershipu vytvorí množstvo neaktuálnych dokumentov. CALMS preto nie je checklist, v ktorom organizácia „splní“ každé písmeno oddelene.

## 2. Priebežný scenár: mesačný štvorhodinový deployment

Predstav si tím, ktorý nasadzuje objednávkovú službu raz mesačne. Release obsahuje desiatky zmien, samotný deployment trvá približne štyri hodiny a často vyžaduje ručný zásah dvoch administrátorov. Product tím po odovzdaní balíka nemá prístup k produkčnej telemetry a pri incidente čaká na Ops tím.

Na prvý pohľad môže riešenie vyzerať jednoducho: „potrebujeme lepšiu pipeline“. CALMS však rozloží symptom na viac navzájom previazaných hypotheses:

```text
zriedkavý a rizikový deployment
├── konflikt ownershipu a motivácií
├── ručný, neštandardizovaný execution path
├── veľké batch sizes a dlhé fronty
├── metriky bez end-to-end rozhodovacieho kontextu
└── kritické znalosti uzamknuté v dvoch ľuďoch
```

Ak sa opraví iba jeden branch, ostatné môžu výsledok zablokovať. Pipeline môže vykonať kroky automaticky, ale release stále čaká tri dni na approval, product tím stále nevidí produkčný výsledok a pri partial failure nikto okrem pôvodného administrátora nevie obnoviť systém.

## 3. Culture: kto vlastní výsledok a môže konať

Culture v CALMS neznamená neurčitú požiadavku na lepšiu komunikáciu. Opisuje reálne decision rights, motivácie a správanie pod tlakom. V scenári development vlastní feature throughput, Ops tím vlastní deployment a incidenty a security tím schvaľuje release tesne pred produkčným oknom.

Každý tím môže konať racionálne podľa vlastného cieľa:

- development odovzdá čo najviac zmien do mesačného balíka;
- Ops obmedzuje frekvenciu deploymentov, pretože nesie recovery risk;
- security pridáva manuálny gate, pretože skoršie evidence nie sú dôveryhodné;
- product považuje prácu za dokončenú po odovzdaní do release fronty.

Výsledkom nie je zlyhanie jedného človeka. Je ním operating model, v ktorom je change throughput oddelený od production outcome-u.

Zdravší model potrebuje spoločný service outcome. Product a engineering tím zostáva zapojený do rollout-u, telemetry aj incident follow-upu. Ops a platform špecialisti poskytujú runtime expertízu, self-service mechanizmy a guardrails, nie finálnu odkladaciu plochu pre všetko produkčné riziko.

## 4. Psychological safety má technický dôsledok

Psychological safety je schopnosť oznámiť neistotu, near miss alebo chybu bez automatického poníženia a trestu. Nie je to iba HR téma. Určuje kvalitu vstupných dát delivery systému.

Ak administrátor vie, že priznanie ručného workaroundu povedie k obvineniu, workaround zostane nezdokumentovaný. Pipeline design potom vychádza z neúplného modelu a automatizuje iba ideálnu cestu. Pri ďalšom incidente chýba evidence o skutočnom failure mode.

Blameless prístup neznamená absenciu zodpovednosti. Znamená, že analýza nekončí pri človeku, ktorý vykonal poslednú akciu. Skúma, prečo systém dovolil neoverený krok, prečo chýbal guardrail a prečo bola improvizácia v danom kontexte racionálna.

## 5. Culture audit v priebežnom scenári

Pri mesačnom deploymente treba zistiť konkrétne decision boundaries:

1. Kto môže release zastaviť a podľa akých signálov?
2. Kto rozhoduje o rollbacku alebo roll-forwarde?
3. Kto vlastní službu po skončení deployment okna?
4. Má product tím prístup k runtime telemetry a incidentným zisteniam?
5. Je security zapojená do designu controls alebo iba do finálneho approvalu?
6. Dostane tím čas na odstránenie toil-u, alebo sa heroický zásah považuje za normálnu prevádzku?

Ak odpoveď na každú otázku smeruje k inému izolovanému tímu, Culture vytvára handoffy, ktoré žiadny deployment nástroj sám neodstráni.

## 6. Lean: najprv nájdi hlavné obmedzenie flowu

Lean skúma celý value stream od potreby po produkčný feedback. Jeho cieľom nie je maximalizovať utilization každého človeka, ale znížiť waiting, rework, batch size a množstvo nedokončenej práce.

V scenári môže aktívna technická práca vyzerať takto:

```text
build                 12 minút
automatizované testy  25 minút
ručný deployment       4 hodiny
```

End-to-end lead time však môže byť tri týždne, pretože zmeny čakajú na spoločný release branch, test environment, security approval a mesačné okno. Zrýchlenie buildu o šesť minút je lokálne zlepšenie, nie odstránenie bottlenecku.

Lean preto rozdeľuje čas na active work, waiting a rework:

```text
lead time = active processing + waiting + rework
```

Ak najväčšiu časť tvorí čakanie na koordinovaný release, prvým experimentom nemá byť nový build cache produkt, ale zmenšenie batchu, odstránenie nejasného handoffu alebo vytvorenie bezpečnejšej častej delivery cesty.

## 7. Batch size vytvára spätnú väzbu so strachom z deploymentu

Veľký mesačný release obsahuje mnoho nezávislých zmien. To zvyšuje test scope, počet dependencies, pravdepodobnosť konfliktu a počet možných príčin pri incidente. Recovery je ťažšia, pretože rollback jedného balíka odstráni aj zdravé capabilities.

Vzniká posilňujúca slučka:

```text
zriedkavý deployment
→ veľký batch
→ vysoký risk a dlhá diagnostika
→ strach z ďalšieho deploymentu
→ ešte zriedkavejší deployment
```

Malé batch sizes túto slučku prerušujú. Zmena sa jednoduchšie reviewuje, testuje, nasadzuje a priraďuje produkčnému signálu. Malý diff však nie je automaticky malý risk; IAM policy alebo database migration môže mať veľký blast radius aj pri niekoľkých riadkoch. Lean hodnotí batch podľa systémového dopadu, nie iba počtu commitov.

## 8. WIP limits chránia dokončovanie práce

Keď release čaká, tímy často otvoria ďalšie úlohy, aby „neboli nevyužité“. Tým rastie work in progress, context switching a počet zmien, ktoré sa navzájom predbiehajú alebo zastarávajú.

WIP limit núti organizáciu pomôcť bottlenecku. Namiesto ďalšieho feature branchu môže developer dokončiť review, opraviť flaky integration test alebo pomôcť odstrániť manuálny deployment krok.

Stopercentná utilization odstraňuje rezervu na review, incidenty a variabilitu. Systém s plne vyťaženými ľuďmi a frontami pred každou špecializovanou rolou môže mať vysokú lokálnu aktivitu a nízky end-to-end throughput.

## 9. Automation: štandardizovaný proces, nie elektronický checklist

Automation premieňa pochopený proces na verzované, konzistentné a auditovateľné vykonanie. Má znižovať variabilitu, feedback latency a závislosť od individuálnej pamäte.

Správne poradie je:

```text
pozorovať reálny proces
→ odstrániť zbytočné kroky
→ definovať vstupy, výstupy a failure semantics
→ štandardizovať bežnú cestu
→ automatizovať
→ merať outcome a udržiavať automation
```

Ak sa existujúci štvorhodinový postup iba prepíše do pipeline, môžu v ňom zostať duplicitné approvals, environment-specific rebuildy a kroky bez jasného ownera. Organizácia získa rýchlejšie klikanie cez zlý proces.

## 10. Automation contract v priebežnom scenári

Pred automatizáciou deploymentu treba pomenovať jeho contract:

- **Vstup — konkrétny immutable artifact a verzovaná konfigurácia**: pipeline nesmie implicitne zostavovať iný obsah podľa prostredia.
- **Preconditions — kompatibilná schema, dostupná kapacita a platné credentials**: chybný stav sa má zistiť pred mutation boundary.
- **Plan — vysvetliteľné poradie zmien a očakávaný scope**: operátor musí vedieť, čo systém zamýšľa vykonať.
- **Apply — ohraničené a auditované mutations**: každý krok má actor identity, timeout a failure result.
- **Verify — technické aj používateľské postconditions**: vytvorený resource nie je to isté ako zdravá objednávková cesta.
- **Recovery — rollback, roll-forward alebo compensation**: partial failure nesmie zostať závislý od pamäte jedného administrátora.

Automation, ktorá pozná iba happy path, môže znížiť duration pri úspechu a súčasne zväčšiť blast radius pri zlyhaní.

## 11. Idempotencia a partial failure

Deployment sa skladá z viacerých externých operácií. Ak sa po treťom kroku preruší network connection, runner nemusí vedieť, či vzdialená platforma operáciu dokončila.

Bezpečný retry preto vyžaduje discovery current state-u a stabilnú resource identity. Opakované spustenie nemá slepo vytvárať druhú databázovú migráciu alebo druhý load-balancer target. Tam, kde operácia nie je idempotentná, automation potrebuje explicitnú compensation alebo resume point.

```text
unknown result
→ znovu načítať current state
→ porovnať s desired state
→ pokračovať, kompenzovať alebo eskalovať
```

„Spusť pipeline znova“ nie je všeobecný recovery model.

## 12. Measurement: číslo musí meniť rozhodnutie

Measurement poskytuje evidence o flowe, reliability a výsledku. Dashboard sám o sebe nie je capability. Metrika potrebuje presnú definíciu, ownera, threshold alebo rozhodnutie, ktoré ovplyvňuje.

V scenári sa pôvodne sleduje iba to, či deployment job skončil zelenou. Táto metrika nevysvetľuje:

- prečo release čakal tri týždne;
- koľko manuálnych zásahov bolo potrebných;
- či nasadenie poškodilo objednávkovú cestu;
- ako dlho trvala obnova po chybe;
- či sa veľkosť batchu zmenšuje.

Measurement musí preto spájať tri vrstvy:

```text
flow
lead time, wait time, WIP, batch size

reliability
change failures, user errors, recovery time

outcome
úspešné objednávky, latency a používateľský výsledok
```

Jedna vrstva bez ostatných môže viesť k nesprávnej optimalizácii.

## 13. DORA metrics ako prepojený systém

Deployment frequency, lead time for changes, change failure rate a recovery time sa interpretujú spolu. Každá metrika ukazuje inú časť delivery capability.

V scenári sa po zmenšení batchu môže deployment frequency zvýšiť. To je pozitívne iba vtedy, ak change failure rate nerastie a recovery zostáva rýchla. Nulové incidenty dosiahnuté zákazom deploymentov nie sú zdravá reliability stratégia.

Metriky musia mať stabilný scope a denominator. „Počet deploymentov“ bez určenia produkčného prostredia, úspechu a change identity sa dá interpretovať alebo manipulovať rôznymi spôsobmi.

## 14. Goodhartov problém

Keď sa metrika stane individuálnym cieľom, ľudia optimalizujú číslo namiesto systému. Ak vedenie odmeňuje počet deploymentov, tímy môžu umelo rozdeliť jednu zmenu na viac technických udalostí bez skrátenia feedbacku alebo zníženia risku.

Ak sa change failure rate používa na trest, tím môže incident preklasifikovať na „support issue“ alebo hotfix neevidovať ako remediation. Measurement bez zdravej Culture znižuje pravdivosť vlastných dát.

Bezpečnejší model používa balanced metrics, trend, context a tímovú diskusiu nad systémovým výsledkom, nie individuálny rebríček.

## 15. Sharing: knowledge ako udržiavané rozhranie

Sharing premieňa lokálnu znalosť na nájditeľnú, dôveryhodnú a použiteľnú capability. Neznamená viac meetingov ani uloženie každého incidentu do náhodného dokumentu.

V pôvodnom scenári poznajú deployment dvaja administrátori. Ich vedomosť zahŕňa poradie krokov, výnimky, recovery aj informáciu, ktoré warnings možno ignorovať. Ak pipeline vznikne bez zachytenia tejto tacit knowledge, automatizuje iba viditeľnú časť procesu.

Užitočné knowledge artifacts majú rôzne úlohy:

- runbook vysvetľuje známu failure situáciu, dôkazy, bezpečný zásah a postcondition;
- architecture decision record zachováva dôvod a trade-offs rozhodnutia;
- service catalog ukazuje ownera, dependencies, SLO a escalation path;
- post-incident review spája evidence s konkrétnou zmenou testu, guardrailu alebo architecture;
- code review zachováva change context pri source revision-e.

Každý artifact potrebuje ownera a aktualizačný trigger. Dokumentácia bez lifecycle-u sa po niekoľkých neúspešných použitiach stane nedôveryhodná.

## 16. Sharing sa overuje použitím

Knowledge nie je zdieľaná iba preto, že je uložená. Druhý človek musí vedieť informáciu nájsť, pochopiť a použiť pri reálnej úlohe.

V scenári možno vykonať game day: iný engineer nasadí testovaciu verziu, zámerne vyvolá partial failure a podľa runbooku obnoví službu. Výsledok ukáže, ktoré kroky sú nejasné, ktoré credentials chýbajú a kde pipeline neposkytuje dostatočnú observability.

Takéto overenie súčasne zlepšuje Sharing, Automation aj Culture. Knowledge prestáva byť osobným vlastníctvom a tím získava dôveru v spoločný recovery model.

## 17. Ako sa oblasti navzájom blokujú

Rovnaký symptom nemožno automaticky priradiť jednému písmenu.

### Automation bez Culture

Centralizovaný pipeline tím vlastní všetky zmeny a product tímy čakajú na ticket. Execution je automatizovaný, ale ownership a lead time zostávajú rozdelené.

### Culture bez Automation

Ľudia spolupracujú a ochotne pomáhajú, no deployment stále závisí od manuálneho poradia a pamäte. Dobrá vôľa neodstráni variabilitu ani recovery risk.

### Automation bez Lean

Pipeline elektronicky vykonáva päť approvals a environment-specific rebuild. Duration jedného kroku klesla, ale hlavná fronta zostala.

### Measurement bez Culture

Metriky sa používajú na hodnotenie jednotlivcov, takže incident classification a reporting prestávajú byť dôveryhodné.

### Lean bez Measurement

Tím odstráni viditeľný krok, ale nemeria end-to-end lead time ani failure rate. Bottleneck sa môže iba presunúť do inej fronty.

### Sharing bez ownershipu

Vznikajú wiki stránky, videá a runbooky bez ownera. Viac zdrojov zvyšuje čas hľadania a nikto nevie, ktorý je autoritatívny.

## 18. End-to-end CALMS zásah

Pre mesačný deployment môže postupná náprava vyzerať takto:

```text
Culture
spoločný service ownership a rollback authority
        ↓
Lean
zmerať wait time a rozdeliť mesačný batch
        ↓
Automation
versioned build-once pipeline s plan/apply/verify/recovery
        ↓
Measurement
lead time, change failure, recovery a order outcome
        ↓
Sharing
testovaný runbook, service catalog a post-incident actions
```

Poradie nie je univerzálne. Organizácia môže začať malým experimentom v oblasti, ktorá odblokuje ostatné. Dôležité je merať systémový outcome a nevyhlásiť úspech po nainštalovaní nástroja.

## 19. Praktický CALMS audit

Pri audite jednej služby zbieraj evidence, nie iba názory.

### Culture

Zaznamenaj service ownera, production authority, on-call model, spôsob incident review a konfliktné tímové ciele. Over, či človek môže bezpečne zastaviť rollout a či tím dostáva kapacitu na remediation.

### Automation

Rekonštruuj reálny execution path vrátane manuálnych krokov, credentials, partial failures a recovery. Porovnaj dokumentovaný a skutočný postup.

### Lean

Zmeraj active time, waiting, rework, WIP a batch size od change intentu po production feedback. Označ jeden aktuálny bottleneck a jeho ownera.

### Measurement

Pre každú metriku zapíš definíciu, scope, denominator, ownera a rozhodnutie, ktoré mení. Odstráň vanity metrics bez action contractu.

### Sharing

Urči authoritative source pre runbook, architecture decisions, service ownership a incident learning. Over jeho použiteľnosť druhým človekom alebo game dayom.

## 20. Diagnostické symptómy

### Moderný toolchain, ale dlhý lead time

Automation pravdepodobne zrýchlila iba active processing. Zmeraj approval, review, environment a release waiting a over, či platforma poskytuje skutočný self-service contract.

### Deployment je rýchlejší, ale incidenty častejšie

Skontroluj batch risk, test evidence, rollout control a production validation. Automation možno zrýchlila exposure bez zodpovedajúceho feedbacku.

### Veľa dashboardov, no žiadne zlepšenie

Over, ktoré rozhodnutie každá metrika mení, kto ju vlastní a či sa zistenia premieňajú na experiment alebo backlog.

### Rovnaké incidenty sa opakujú

Feedback vzniká, ale Sharing a learning loop zrejme nevytvorili regression test, guardrail, platform capability alebo ownership zmenu.

### Tímy obchádzajú platformu

Problém nemusí byť iba Culture. Paved road môže mať vysokú latency, nepodporovaný use case alebo nejasný exception proces. Zmeraj developer experience a porovnaj oficiálnu a neoficiálnu cestu.

## 21. Časté omyly

### CALMS je maturity score

Rámec možno použiť na porovnanie observations v čase, ale jedno celkové číslo môže zakryť kritickú slabinu. Organizácia s výbornou automation a nulovým production feedbackom nemá „priemerne dobrý“ DevOps model.

### Culture sa nedá technicky ovplyvniť

Decision rights, ownership, platform interfaces, alert routing, review proces a metriky menia správanie ľudí. Culture nie je oddelená od architecture a governance.

### Automation je najobjektívnejší a preto najdôležitejší pilier

Automation je viditeľná, ale vykonáva iba proces a rozhodnutia, ktoré jej organizácia poskytne. Bez Lean a Culture môže škálovať chybný model.

### Lean znamená znižovanie počtu ľudí

Lean odstraňuje waste, waiting a rework vo value streame. Rezerva na review, incidenty a učenie môže throughput zvyšovať, nie znižovať.

### Measurement znamená viac metrík

Cieľom je lepšie rozhodnutie. Množstvo nejasných dashboardov môže zvýšiť cognitive load a znížiť dôveru v telemetry.

### Sharing znamená vytvoriť dokument

Knowledge je zdieľaná až vtedy, keď je nájditeľná, aktuálna a druhý človek ju vie použiť bez neformálnej závislosti na pôvodnom autorovi.

## 22. Kontrolné otázky

1. Prečo CALMS nemožno hodnotiť ako päť nezávislých checklistov?
2. Ako Culture ovplyvňuje kvalitu technických evidence?
3. Prečo môže plná utilization zhoršiť end-to-end flow?
4. Ako veľký batch posilňuje strach zo zmeny?
5. Prečo sa má proces pred automatizáciou zjednodušiť?
6. Ktoré failure semantics musí mať deployment automation?
7. Ako sa flow metrics líšia od reliability a outcome metrics?
8. Ako Goodhartov zákon poškodí incident alebo deployment reporting?
9. Kedy sa dokument stáva operational capability?
10. Ako by si overil, že critical knowledge nie je viazaná na jedného človeka?
11. Prečo automation bez Lean môže skrátiť job a nezmeniť lead time?
12. Ako Measurement bez Culture znižuje pravdivosť dát?
13. Ktoré CALMS oblasti by si preveril pri opakovaných incidentoch s rovnakou príčinou?
14. Ako by si navrhol prvý malý experiment pre mesačný rizikový deployment?

## 23. Zhrnutie

CALMS je diagnostický model socio-technického delivery systému. Culture určuje ownership a pravdivosť feedbacku, Lean odhaľuje hlavné obmedzenie flowu, Automation vykonáva pochopený proces konzistentne, Measurement overuje systémový výsledok a Sharing premieňa lokálne poznanie na udržiavanú capability.

V praxi sa oblasti nedajú opravovať izolovane. Nová pipeline nezlepší delivery, ak release zostáva veľký, tímy majú konfliktné ciele, metriky nemenia rozhodnutia a recovery poznajú iba dvaja ľudia. CALMS pomáha zvoliť experiment podľa skutočného bottlenecku a následne overiť, či sa zlepšil end-to-end outcome.

## Glossary impact

Relevantné pojmy: CALMS, Culture, Automation, Lean, Measurement, Sharing, psychological safety, shared ownership, batch size, WIP limit, bottleneck, value stream, Goodhartov zákon, operational knowledge, game day a bus factor.

## Primárne zdroje

- [DORA — Research program](https://dora.dev/)
- [Google Cloud — DevOps capabilities](https://cloud.google.com/architecture/devops)
- [The DevOps Handbook — IT Revolution](https://itrevolution.com/product/the-devops-handbook-second-edition/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: DevOps lifecycle](devops-lifecycle.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Three Ways of DevOps →](three-ways.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
