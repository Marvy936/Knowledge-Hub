# CALMS Framework

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [DevOps](devops.md), [DevOps Lifecycle](devops-lifecycle.md)
- Súvisiace témy: culture, automation, Lean, measurement, sharing, DORA metrics

## 1. Definícia

CALMS je rámec na posúdenie DevOps schopností organizácie cez päť vzájomne závislých oblastí:

- **Culture**,
- **Automation**,
- **Lean**,
- **Measurement**,
- **Sharing**.

Rámec pomáha zabrániť tomu, aby sa DevOps redukoval iba na nástroje alebo CI/CD pipeline.

## 2. Problém, ktorý rieši

DevOps transformácie často zlyhávajú, pretože organizácia optimalizuje iba jednu vrstvu. Napríklad zavedie Kubernetes, nový CI systém a Infrastructure as Code, ale ponechá:

- konfliktné ciele tímov,
- manuálne schvaľovacie fronty,
- slabý ownership,
- málo produkčnej spätnej väzby,
- kultúru obviňovania.

CALMS poskytuje jednoduchý kontrolný model: technická automatizácia musí byť podporená kultúrou, štíhlym tokom, meraním a zdieľaním poznatkov.

## 3. Mentálny model

```text
Culture
   ├── umožňuje dôveru a ownership
Automation
   ├── robí proces opakovateľný a rýchly
Lean
   ├── optimalizuje tok a znižuje odpad
Measurement
   ├── ukazuje správanie a výsledky systému
Sharing
   └── distribuuje poznatky a spätnú väzbu
```

Tieto oblasti sa nesčítavajú ako nezávislé body. Slabá oblasť môže obmedziť celý systém.

## 4. Culture

### Čo znamená Culture

Culture je spôsob, akým ľudia spolupracujú, rozhodujú, reagujú na chyby a chápu zodpovednosť.

DevOps kultúra typicky podporuje:

- shared ownership,
- psychologické bezpečie,
- transparentnosť,
- spoluprácu naprieč rolami,
- učenie z incidentov,
- lokálnu autonómiu v jasných guardrails,
- orientáciu na výsledok namiesto aktivity.

### Prečo je kritická

Automatizácia nemení motivácie tímov. Ak je vývoj hodnotený podľa počtu funkcií a prevádzka podľa počtu zmien, ktorým zabránila, konflikt zostane aj po zavedení modernej platformy.

### Príklad zdravej kultúry

Po incidente tím nehľadá osobu, ktorá „urobila chybu“. Skúma:

- aké podmienky umožnili chybe prejsť,
- prečo systém neposkytol skoršiu spätnú väzbu,
- aké guardrails alebo automatizácia chýbali,
- ako znížiť pravdepodobnosť opakovania.

### Anti-pattern

„You build it, you run it“ sa zavedie ako príkaz bez observability, dokumentácie, on-call podpory a času na reliability prácu. Výsledkom nie je ownership, ale presun stresu.

## 5. Automation

### Čo znamená Automation

Automation premieňa opakovateľnú činnosť na konzistentný, auditovateľný a reprodukovateľný proces.

Typické oblasti:

- build a test,
- provisioning infraštruktúry,
- configuration management,
- deployment,
- policy enforcement,
- security scanning,
- backup,
- incident enrichment,
- environment creation.

### Hodnota automatizácie

Automatizácia znižuje:

- manuálnu variabilitu,
- počet handoffov,
- čas spätnej väzby,
- závislosť od individuálnej pamäte,
- neauditovateľné zásahy.

### Dôležitá hranica

Nie všetko sa má automatizovať okamžite.

Rozumné poradie:

```text
Pochopiť proces
  ↓
Odstrániť zbytočné kroky
  ↓
Štandardizovať
  ↓
Automatizovať
  ↓
Merať výsledok
```

Automatizácia zlého procesu iba zrýchli jeho zlé výsledky.

### Príklad

Namiesto ručného vytvárania VM cez cloud konzolu sa infraštruktúra deklaruje v Terraform konfigurácii. Zmena prejde review, planom, policy kontrolou a auditovateľným apply krokom.

## 6. Lean

### Čo znamená Lean

Lean sa sústreďuje na plynulý tok hodnoty, malé dávky práce, obmedzenie rozpracovanosti a odstránenie odpadu.

V DevOps kontexte sa sleduje najmä:

- wait time,
- handoffy,
- work in progress,
- veľkosť zmien,
- opakovaná manuálna práca,
- úzke miesta,
- rework.

### Small batch sizes

Malé zmeny sa jednoduchšie:

- reviewujú,
- testujú,
- nasadzujú,
- diagnostikujú,
- vracajú späť.

Veľká zmena kombinuje mnoho premenných a zväčšuje blast radius.

### Limitovanie WIP

Ak tím začne viac práce, než dokáže dokončiť, rastie multitasking a čakacia doba. Vyššia lokálna vyťaženosť nemusí znamenať vyšší systémový throughput.

### Value stream

Value stream je celý tok od požiadavky po hodnotu v produkcii. Lean optimalizuje celý tok, nie iba jednu technickú fázu.

### Príklad

Build trvá 8 minút, ale release čaká 3 dni na manuálne schválenie. Optimalizácia build cache o 2 minúty má menší systémový efekt než odstránenie alebo automatizovanie schvaľovacieho úzkeho miesta.

## 7. Measurement

### Čo znamená Measurement

Measurement poskytuje dôkazy o správaní delivery systému aj prevádzkovanej služby.

Meranie má odpovedať na otázky:

- Dodávame rýchlejšie?
- Zlyhávajú zmeny častejšie?
- Obnovujeme službu rýchlo?
- Prináša zmena používateľskú hodnotu?
- Kde sa práca najdlhšie zdržiava?
- Je služba spoľahlivá z pohľadu používateľa?

### Typy metrík

#### Flow metrics

- lead time,
- cycle time,
- throughput,
- wait time,
- work in progress.

#### Delivery metrics

- deployment frequency,
- lead time for changes,
- change failure rate,
- time to restore service.

#### Reliability metrics

- availability,
- latency,
- error rate,
- SLI a SLO,
- incident frequency.

#### Outcome metrics

- adopcia funkcie,
- conversion rate,
- task completion,
- používateľská spokojnosť.

### Goodhartov problém

Keď sa metrika stane cieľom bez kontextu, ľudia môžu optimalizovať číslo namiesto systému.

Príklad: cieľ „zvýšiť počet deploymentov“ môže viesť k umelému rozdeľovaniu zmien bez zlepšenia hodnoty alebo reliability.

### Meranie bez akcie

Dashboard nie je zlepšenie. Metrika má viesť k rozhodnutiu, experimentu alebo zmene procesu.

## 8. Sharing

### Čo znamená Sharing

Sharing je systematické zdieľanie vedomostí, spätnej väzby, rozhodnutí a prevádzkových skúseností.

Mechanizmy zahŕňajú:

- code review,
- dokumentáciu,
- runbooks,
- architecture decision records,
- demos,
- communities of practice,
- postmortems,
- pairing,
- interné školenia,
- service catalogs.

### Prečo je dôležité

Ak kritické znalosti existujú iba v hlave jedného človeka, systém má vysoký bus factor a slabú schopnosť škálovať.

Sharing znižuje:

- opakované riešenie rovnakých problémov,
- závislosť od jednotlivcov,
- nekonzistentné lokálne riešenia,
- čas onboardingu.

### Príklad

Po incidente tím vytvorí postmortem, aktualizuje runbook, pridá alert a upraví test. Poznatok sa tým mení z individuálnej skúsenosti na systémovú schopnosť.

## 9. Ako sa oblasti ovplyvňujú

### Automation bez Culture

Vzniká centralizovaný tím, ktorý vlastní všetky pipeline a stáva sa novým úzkym miestom.

### Culture bez Automation

Tímy dobre spolupracujú, ale manuálne procesy sú pomalé a náchylné na chyby.

### Automation bez Lean

Automatizuje sa veľký, komplikovaný proces s množstvom zbytočných krokov.

### Measurement bez Culture

Metriky sa používajú na hodnotenie a trestanie jednotlivcov. Ľudia ich začnú skrývať alebo manipulovať.

### Sharing bez štandardov

Veľa dokumentácie vzniká nekonzistentne, bez ownershipu a údržby. Informácie sú dostupné, ale nedôveryhodné.

## 10. Príklad CALMS auditu

Scenár: tím nasadzuje raz mesačne, deployment trvá štyri hodiny a často vyžaduje manuálny zásah.

| Oblasť | Pozorovanie | Otázka |
|---|---|---|
| Culture | Deployment vlastní izolovaný Ops tím | Má produktový tím ownership výsledku? |
| Automation | Kroky sa vykonávajú podľa manuálneho checklistu | Ktoré opakovateľné kroky možno bezpečne automatizovať? |
| Lean | Veľké mesačné batch releases | Možno zmenšiť dávky a skrátiť fronty? |
| Measurement | Sleduje sa iba úspech alebo zlyhanie deploymentu | Poznáme lead time, failure rate a recovery time? |
| Sharing | Postupy poznajú dvaja administrátori | Existuje verzovaný runbook a zdieľaná dokumentácia? |

CALMS nepredpisuje jeden nástroj. Pomáha identifikovať, v ktorej systémovej oblasti chýba schopnosť.

## 11. Praktické otázky pre každú oblasť

### Culture

- Kto vlastní výsledok služby?
- Ako tím reaguje na zlyhanie?
- Sú ciele tímov kompatibilné?
- Môžu ľudia bezpečne upozorniť na riziko?

### Automation

- Ktoré kroky sú opakovateľné a manuálne?
- Je automatizácia verzovaná a testovaná?
- Je možné proces bezpečne opakovať?
- Existuje audit trail?

### Lean

- Kde práca čaká?
- Aká je veľkosť batchu?
- Koľko práce je rozpracovanej?
- Ktorý krok obmedzuje celý tok?

### Measurement

- Meriame aktivitu alebo výsledok?
- Máme delivery aj reliability metriky?
- Vedie metrika ku konkrétnemu rozhodnutiu?
- Dá sa metrika jednoducho manipulovať?

### Sharing

- Kde sú uložené rozhodnutia a prevádzkové znalosti?
- Kto dokumentáciu vlastní?
- Aktualizuje sa dokumentácia spolu so zmenou?
- Vie nový člen tímu nájsť potrebné informácie bez neformálnej eskalácie?

## 12. Anti-patterny

### Tooling-first CALMS

Automation sa považuje za hlavný alebo jediný pilier a ostatné oblasti zostanú ignorované.

### Vanity metrics

Merajú sa ľahko dostupné čísla, ktoré nepomáhajú rozhodovať, napríklad počet pipeline jobov alebo počet commitov na osobu.

### Knowledge dumping

Sharing sa chápe ako vytvorenie veľkého množstva dokumentov bez jasnej štruktúry, relevance a ownershipu.

### Permanentná transformácia bez výsledku

Organizácia vykonáva workshopy a reorganizácie, ale nemeria zlepšenie toku, kvality ani používateľských výsledkov.

## 13. Časté omyly

### „CALMS je maturity score“

CALMS možno použiť pri posudzovaní vyspelosti, ale nie je to presný univerzálny bodovací systém. Kontext produktu, rizika a organizácie je rozhodujúci.

### „Automation je najtechnickejšia a preto najdôležitejšia časť“

Nie. Automatizácia bez kultúry a správneho toku môže iba stabilizovať zlé silá.

### „Sharing znamená viac meetingov“

Nie. Zdieľanie má vytvárať dostupné a opakovateľné informačné rozhrania. Často ide o kvalitnejšiu dokumentáciu a asynchrónne mechanizmy.

### „Lean znamená robiť viac s menším počtom ľudí“

Nie. Lean znamená znižovať odpad a optimalizovať tok hodnoty, nie maximalizovať vyťaženosť ľudí.

## 14. Kontrolné otázky

1. Čo znamená skratka CALMS?
2. Prečo Automation sama osebe nevytvára DevOps model?
3. Ako small batch sizes znižujú riziko?
4. Aký je rozdiel medzi flow metric a outcome metric?
5. Prečo môže Measurement bez zdravej Culture zhoršiť systém?
6. Uveď príklad automatizácie zlého procesu.
7. Ako Sharing znižuje bus factor?
8. Ktorú oblasť CALMS by si skúmal pri trojdňovom čakaní na schválenie a prečo?
9. Prečo vysoká vyťaženosť každého tímu nemusí znamenať vysoký throughput systému?

## 15. Zhrnutie

- CALMS pokrýva Culture, Automation, Lean, Measurement a Sharing.
- DevOps schopnosť vzniká kombináciou organizačných aj technických mechanizmov.
- Culture určuje ownership, dôveru a reakciu na zlyhania.
- Automation robí proces konzistentný, reprodukovateľný a auditovateľný.
- Lean optimalizuje celý tok, malé dávky a obmedzenie rozpracovanosti.
- Measurement má podporovať rozhodovanie, nie iba produkovať dashboardy.
- Sharing premieňa individuálne skúsenosti na systémové znalosti.
- Slabosť jedného piliera môže obmedziť hodnotu ostatných.