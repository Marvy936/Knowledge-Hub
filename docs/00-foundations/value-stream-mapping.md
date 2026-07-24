# Value Stream Mapping

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Systems Thinking](systems-thinking.md), [Feedback Loops](feedback-loops.md)
- Súvisiace témy: lead time, flow efficiency, constraints, DORA metrics, continuous improvement

## 1. Čo je value stream

**Value stream** je celý socio-technický tok potrebný na premenu požiadavky, problému alebo incidentu na overený výsledok pre používateľa. Zahŕňa nielen aktívnu technickú prácu, ale aj fronty, rozhodnutia, odovzdávky, schválenia, rework a spätnú väzbu.

**Value Stream Mapping (VSM)** je technika, ktorá tento tok zviditeľňuje pomocou konkrétnych udalostí a časov. Jej cieľom nie je vytvoriť estetický procesný diagram, ale identifikovať, kde sa práca zdržiava, vracia späť alebo stráca kontext.

## 2. Prečo lokálne metriky nestačia

Jednotlivé tímy prirodzene sledujú vlastnú časť práce. Vývoj môže optimalizovať implementačný čas, QA počet vykonaných testov a prevádzka dĺžku samotného deploymentu, hoci väčšinu end-to-end času zmena strávi čakaním medzi nimi.

VSM preto používa systémovú hranicu od jasne definovaného vstupu po používateľský výsledok. Lokálne zrýchlenie má hodnotu iba vtedy, keď znižuje celkový lead time, rework, riziko alebo používateľský dopad.

## 3. Základný model toku

```text
požiadavka alebo incident
→ rozhodnutie a prioritizácia
→ implementácia
→ review a integrácia
→ build a test
→ release a deployment
→ produkčné overenie
→ používateľský výsledok
```

Tok nie je vždy lineárny. Neúspešný test, nejasná požiadavka alebo produkčný problém môžu vrátiť prácu do skoršej fázy; tieto spätné slučky treba mapovať rovnako dôsledne ako hlavný forward flow.

## 4. Pracovná položka a scope mapy

Mapa musí sledovať konkrétny typ pracovnej položky, pretože feature, bezpečnostná oprava a incident majú odlišný tok. Mapa „celého IT“ zmieša príliš veľa variantov a neumožní spoľahlivo určiť constraint.

Použiteľný scope napríklad znie: „bežná aplikačná zmena od merge do `main` po overenie v produkcii“. Začiatok a koniec musia byť merateľné udalosti, nie neurčité stavy ako „vývoj začal“ alebo „projekt bol hotový“.

## 5. Process time, wait time a lead time

**Process time** je čas, počas ktorého niekto alebo niečo na položke aktívne pracuje. **Wait time** je čas, keď položka čaká vo fronte, na rozhodnutie, prostredie, kapacitu alebo inú závislosť.

```text
lead time = process time + wait time + rework time
```

Ak má zmena deväť hodín aktívnej práce a desaťdňový lead time, dominantný problém pravdepodobne nie je rýchlosť písania kódu. Treba hľadať fronty, handoffs, scheduling delays a opakované návraty práce.

## 6. Flow efficiency

Flow efficiency vyjadruje podiel aktívneho času na celkovom lead time.

```text
flow efficiency = process time / lead time × 100 %
```

Nízka hodnota neznamená automaticky zlý tím; môže odhaľovať regulačné čakanie, externú závislosť alebo batch scheduling. Metrika je užitočná vtedy, keď vedie k otázke, prečo práca čaká a či dané čakanie skutočne znižuje riziko.

## 7. Queue a work in progress

Queue je zásoba práce čakajúcej pred konkrétnym krokom. Rastie, keď arrival rate dlhodobo prevyšuje processing capacity alebo keď je spracovanie výrazne variabilné.

Work in progress (WIP) zahŕňa všetky začaté, ale nedokončené položky. Vysoký WIP predlžuje lead time, zvyšuje multitasking a spôsobuje, že zmena zastará skôr, než sa dostane do produkcie.

## 8. Handoff a strata kontextu

Handoff je odovzdanie pracovnej položky medzi ľuďmi, tímami alebo systémami. Každé odovzdanie môže vytvoriť nový front, odlišnú prioritu a potrebu znovu vysvetliť pôvodný zámer.

Handoff nie je automaticky zlý, pretože špecializovaná kontrola môže byť potrebná. Treba však vysvetliť, aké riziko kontrola pokrýva, aké evidence potrebuje a či ju možno presunúť skôr, automatizovať alebo sprístupniť ako self-service capability.

## 9. Rework

Rework je opakovaná práca potrebná preto, že predchádzajúci výstup nebol použiteľný. Môže ísť o opravu nejasnej požiadavky, opakované testovanie flaky scenára, prerobenie deploymentu alebo hotfix po neúspešnom release.

Rework sa nesmie zamieňať s hodnotovou iteráciou. Iterácia zámerne skúma neistotu; rework vzniká najmä vtedy, keď systém poskytol neskorú alebo nekvalitnú spätnú väzbu.

## 10. Delivery a recovery value stream

**Delivery value stream** sleduje normálnu zmenu od vzniku po bezpečné sprístupnenie používateľovi. Ukazuje, ako organizácia premieňa plánovanú prácu na produkčnú hodnotu.

**Recovery value stream** sleduje tok od detekcie problému po obnovenie služby a overenie používateľského výsledku. Rýchly delivery proces bez efektívnej diagnostiky, rozhodovania a mitigácie môže mať stále veľmi slabú prevádzkovú odolnosť.

## 11. Zber skutočných udalostí

Current-state mapa má vychádzať zo skutočných udalostí: commitov, review timestamps, pipeline behov, deploymentov, approval records a incidentných záznamov. Workshopová pamäť ľudí je dôležitá na vysvetlenie kontextu, ale samotná často podceňuje čakanie a neformálne obchádzky.

Pri každom kroku zaznamenaj vstupnú udalosť, výstupnú udalosť, process time, wait time, počet položiek vo fronte, failure alebo rework rate a ownera rozhodnutia. Tým sa diagram mení na analyzovateľný model.

## 12. Current-state mapa

Current-state mapa opisuje proces tak, ako reálne funguje dnes. Musí obsahovať ručné zásahy, Slack schválenia, dočasné skripty aj rozdiel medzi deklarovaným a skutočným postupom.

```text
merge
→ 18 h čakanie na review
→ 35 min CI
→ 6 h čakanie na test environment
→ 45 min acceptance test
→ 2 dni approval queue
→ 12 min deployment
→ 20 min produkčné overenie
```

V tomto príklade samotný deployment nie je bottleneck. Najväčšiu časť lead time tvoria fronty pred review, prostredím a schválením.

## 13. Constraint

Constraint je prvok, ktorý momentálne najviac obmedzuje throughput alebo recovery schopnosť celého toku. Zrýchlenie iného kroku môže iba rýchlejšie napĺňať front pred constraintom.

Constraint nemusí byť technická kapacita. Môže ním byť availability reviewera, policy vyžadujúca manuálny podpis, chýbajúce test environmenty alebo nejasné rozhodovacie právo.

## 14. Batch size

Batch size určuje, koľko zmien sa spracúva a odovzdáva naraz. Veľké batchy znižujú frekvenciu handoffov, ale zväčšujú množstvo súčasne menených premenných, čas do feedbacku a rozsah možného rollbacku.

Menšie dávky zjednodušujú review, testovanie a diagnostiku. Neznamenajú umelé rozdelenie práce na bezvýznamné deploye; každý batch musí zostať koherentný, overiteľný a bezpečne nasaditeľný.

## 15. Information flow

Material flow opisuje pohyb pracovnej položky, zatiaľ čo information flow opisuje pohyb požiadaviek, rozhodnutí a spätnej väzby. Slabý informačný tok môže spôsobiť rework aj v procese s rýchlou technickou automatizáciou.

Pri mapovaní preto sleduj, kto pozná akceptačné kritériá, kde vzniká bezpečnostný feedback a ako sa produkčné poznatky vracajú k autorovi zmeny. Dashboard bez ownera alebo approval bez kontextu je informačný bottleneck.

## 16. Future-state mapa

Future-state mapa opisuje konkrétny nasledujúci stav, nie ideálnu organizáciu bez frontov a rizík. Má ukázať, ktorý constraint sa mení, akým mechanizmom a aké nové failure modes môže zmena vytvoriť.

Príkladom je presun opakovaných security pravidiel do policy-as-code, automatické schválenie nízkorizikových zmien a manuálny review iba pre explicitné výnimky. Hodnota tejto zmeny sa musí potvrdiť kratším wait time bez rastu change failure rate.

## 17. Experiment a overenie

Každé VSM zlepšenie má mať baseline, hypotézu, ownera, časové okno a success criteria. Bez nich sa workshop môže skončiť zoznamom želaní, pri ktorom nie je možné určiť, či sa systém skutočne zlepšil.

```text
hypotéza:
ak zavedeme review rotation a WIP limit,
median review wait klesne z 18 h pod 4 h
bez rastu escaped defect rate
```

Po experimente treba znovu zmerať celý tok. Lokálne zlepšenie, ktoré presunie front do ďalšej fázy, nie je end-to-end úspech.

## 18. Vzťah k DORA metrikám

DORA metriky ukazujú výsledok delivery systému, napríklad change lead time alebo change fail rate. Value stream mapa rozkladá výsledok na konkrétne kroky, fronty a feedback loops, aby bolo možné nájsť mechanizmus problému.

Dlhý change lead time teda nie je priamo diagnóza. VSM môže odhaliť, že väčšinu času tvorí review queue, environment provisioning alebo rework po neskorých contract testoch.

## 19. Praktický mini-lab

Vyber jednu nedávnu bežnú produkčnú zmenu a zostav jej časovú os od dohodnutého začiatku po overený používateľský výsledok. Pri každom kroku odlíš aktívnu prácu od čakania a označ každý návrat práce späť.

Následne vypočítaj lead time, process time, wait time, flow efficiency, počet handoffs a počet rework cyklov. Vyber iba jeden dominantný constraint a navrhni malý reverzibilný experiment, ktorý má zmeniť jeho merateľné správanie.

## 20. Troubleshooting mapy

Ak mapa ukazuje nereálne vysokú flow efficiency, skontroluj, či neboli vynechané queue a approval timestamps. Ak sa ľudia nezhodnú na procese, sleduj konkrétnu pracovnú položku namiesto snahy vytvoriť jeden univerzálny diagram.

Ak sa po zmene lead time nezlepší, over, či sa constraint nepresunul do ďalšej fázy alebo či arrival rate nevzrástol. VSM je opakovaný diagnostický cyklus, nie jednorazový workshop.

## 21. Anti-patterny

### Mapovanie oficiálneho procesu

Diagram zo smernice často neobsahuje ručné workaroundy, neformálne schválenia ani retry. Takáto mapa reprezentuje želaný proces a nemôže spoľahlivo vysvetliť skutočný lead time.

### Príliš široký scope

Mapa celej organizácie zmieša rôzne typy práce a vlastníkov. Výsledkom je všeobecný zoznam problémov bez konkrétneho constraintu a experimentu.

### Lokálna optimalizácia

Zrýchlenie krátkeho build kroku môže byť technicky správne, ale systémovo zanedbateľné, ak zmena ďalej čaká dni na review. Priorita sa má odvíjať od end-to-end výsledku.

### Použitie na hodnotenie ľudí

VSM skúma systém, nie produktivitu jednotlivca. Ak sa časy použijú na trestanie, ľudia začnú skrývať čakanie, rework a neformálne kroky, čím mapa stratí dôveryhodnosť.

## 22. Kontrolné otázky

1. Prečo process time a lead time opisujú odlišné vlastnosti toku?
2. Ako queue a WIP ovplyvňujú čas dokončenia položky?
3. Prečo handoff môže vytvoriť delay aj bez aktívnej práce?
4. Ako odlíšiš hodnotovú iteráciu od reworku?
5. Prečo treba mapovať delivery aj recovery value stream?
6. Ako sa constraint líši od najpomalšieho jednotlivého jobu?
7. Prečo future-state mapa potrebuje merateľnú hypotézu?
8. Ako sa VSM dopĺňa s DORA metrikami?

## 23. Zhrnutie

Value Stream Mapping zviditeľňuje end-to-end pohyb práce, informácií a spätnej väzby. Jeho hlavnou hodnotou je rozlíšenie process time od wait time, identifikácia constraintu a návrh merateľného experimentu, ktorý zlepšuje celý systém namiesto jednej lokálnej metriky.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Toil a technical debt](toil-and-technical-debt.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: DORA metrics →](dora-metrics.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
