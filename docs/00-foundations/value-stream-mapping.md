# Value Stream Mapping

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Systems Thinking](systems-thinking.md), [Feedback Loops](feedback-loops.md)
- Súvisiace témy: lead time, flow efficiency, constraints, DORA metrics, continuous improvement

## 1. Definícia

**Value stream** je celý tok práce potrebný na premenu požiadavky alebo problému na výsledok poskytujúci hodnotu používateľovi. **Value Stream Mapping (VSM)** je technika, ktorá tento tok vizualizuje vrátane práce, čakania, odovzdávok, chýb a spätnej väzby.

Cieľom nie je vytvoriť pekný diagram. Cieľom je odhaliť, kde sa hodnota zdržiava, vracia späť alebo sa stráca.

## 2. Problém, ktorý rieši

Tímy často vidia iba svoju časť procesu:

- vývoj sleduje čas implementácie,
- QA sleduje testovanie,
- security sleduje schválenie,
- operations sleduje deployment.

Lokálne môže byť každý tím efektívny, ale zmena môže väčšinu času čakať medzi tímami. VSM optimalizuje end-to-end tok namiesto lokálnej vyťaženosti.

## 3. Mentálny model

```text
Požiadavka
   ↓
Analýza → vývoj → review → CI → test → approval → deployment → používateľ
           ↑                         ↓
           └────── rework / chyba ───┘
```

Pri každom kroku sledujeme:

- process time — čas aktívnej práce,
- wait time — čas čakania,
- queue — množstvo rozpracovanej práce,
- handoff — odovzdanie medzi ľuďmi alebo systémami,
- rework — návrat práce späť,
- feedback time — ako rýchlo sa dozvieme výsledok.

## 4. Lead time a process time

Príklad:

```text
Celkový lead time: 10 dní
Aktívna práca:      9 hodín
```

Rozdiel tvorí čakanie, plánovanie, fronty a odovzdávky. Zrýchlenie 30-minútového build jobu o 20 % nemusí mať význam, ak merge request čaká dva dni na review.

Zjednodušená flow efficiency:

```text
Flow efficiency = aktívny process time / celkový lead time × 100 %
```

Nízka flow efficiency často znamená, že hlavným problémom nie je rýchlosť vykonania práce, ale fronty a koordinácia.

## 5. Dva dôležité software value streams

Pri softvéri treba mapovať minimálne:

### Delivery value stream

Normálny tok feature alebo opravy od commitu po úspešné nasadenie.

### Recovery value stream

Tok od zistenia produkčného problému po obnovenie služby alebo odstránenie dopadu.

Tím môže mať rýchly feature delivery, ale veľmi pomalý recovery proces. Oba toky používajú podobné mechanizmy — diagnostiku, zmenu, test, deployment a overenie.

## 6. Ako vytvoriť current-state map

### 1. Urči scope

Vyber konkrétny produkt, službu a typ zmeny. Mapa „celého IT“ bude príliš všeobecná.

### 2. Urči začiatok a koniec

Napríklad:

```text
Začiatok: commit na main
Koniec: zmena overená v produkcii
```

### 3. Zapoj ľudí z celého toku

Vývoj, QA, security, platforma, operations a produkt môžu vidieť odlišné časti reality.

### 4. Mapuj skutočný proces

Nie proces z dokumentácie, ale to, čo sa reálne deje vrátane ručných obchádzok.

### 5. Zaznamenaj časy a fronty

Pri každom kroku uveď process time, wait time, failure/rework rate a spôsob odovzdania.

### 6. Nájdite constraint

Zameraj sa na najväčšie systémové obmedzenie, nie na najľahšie automatizovateľný krok.

## 7. Príklad current-state mapy

| Krok | Process time | Wait time | Rework |
|---|---:|---:|---:|
| Implementácia | 6 h | 1 deň | 10 % |
| Code review | 45 min | 2 dni | 20 % |
| CI | 35 min | 0 | 15 % retry |
| Security approval | 20 min | 3 dni | 5 % |
| Deployment | 30 min | 1 deň | 10 % |

Najdlhší vykonávaný krok je implementácia, ale najväčší delay vytvárajú approval a review queues. Optimalizácia build cache sama nevyrieši hlavný constraint.

## 8. Handoffs

Každé odovzdanie zvyšuje riziko:

- straty kontextu,
- nejasnej zodpovednosti,
- čakania vo fronte,
- rozdielnej priority,
- chybného prekladu požiadavky.

Handoff nie je automaticky zlý. Špecializované kontroly môžu byť potrebné. Treba však skúmať, či sa dajú nahradiť self-service rozhraním, automatickou policy alebo skoršou spoluprácou.

## 9. Batch size a work in progress

Veľké dávky zvyšujú:

- čas do feedbacku,
- počet naraz menených premenných,
- riziko konfliktov,
- cenu review,
- rozsah rollbacku.

Príliš veľa rozpracovanej práce vytvára fronty. Obmedzenie WIP pomáha dokončovať začaté položky namiesto otvárania ďalších.

## 10. Rework

Rework je práca, ktorá sa musí zopakovať alebo opraviť, pretože predchádzajúci výstup nebol použiteľný.

Príčiny:

- nejasné požiadavky,
- neskoré bezpečnostné kontroly,
- nekonzistentné prostredia,
- flaky tests,
- chýbajúce kontrakty medzi službami,
- príliš veľké zmeny.

Rework môže vyzerať ako vysoká aktivita, ale nezvyšuje dodanú hodnotu.

## 11. Future-state map

Future-state mapa nemá predstavovať ideálny svet bez obmedzení. Má opisovať konkrétny dosiahnuteľný ďalší stav.

Príklad:

```text
Security požiadavky ako policy-as-code v CI
  ↓
automatické schválenie nízkorizikových zmien
  ↓
manuálny review iba pre definované výnimky
```

Výsledok treba overiť metrikami, nie iba pocitom.

## 12. Vzťah k DORA metrikám

VSM vysvetľuje mechanizmy za výslednými metrikami:

- change lead time ukazuje rýchlosť toku,
- deployment frequency ukazuje schopnosť dokončovať malé dávky,
- change fail rate odhaľuje nestabilitu,
- failed deployment recovery time meria recovery value stream,
- deployment rework rate ukazuje podiel neplánovaných opravných deploymentov.

DORA metrika ukáže, **že** je problém. Value stream mapa pomáha zistiť, **kde a prečo** vzniká.

## 13. Anti-patterny

### Mapovanie oficiálneho procesu

Tím zakreslí proces zo smernice a ignoruje ručné kroky, Slack správy a obchádzky.

### Príliš široký scope

Mapa obsahuje celú organizáciu a nedá sa z nej vybrať konkrétny experiment.

### Optimalizácia lokálneho kroku

Jeden tím zrýchli svoju prácu, ale iba rýchlejšie plní nasledujúcu frontu.

### VSM bez následnej zmeny

Workshop vytvorí diagram, ale nevznikne owner, hypotéza, experiment ani termín kontroly výsledku.

### Použitie na hodnotenie ľudí

Účelom je zlepšiť systém. Ak sa časy použijú na trestanie jednotlivcov, údaje prestanú byť dôveryhodné.

## 14. Praktický mini-lab

Vyber poslednú bežnú produkčnú zmenu a zapíš:

1. čas commitu,
2. čas začiatku a konca review,
3. čas behu a čakania CI,
4. approval časy,
5. deployment čas,
6. čas overenia v produkcii,
7. všetky návraty a retry.

Potom vypočítaj:

```text
lead time
aktívny process time
wait time
počet handoffs
počet rework cyklov
```

Vyber jedno najväčšie obmedzenie a navrhni malý experiment na jeho zníženie.

## 15. Kontrolné otázky

1. Prečo je vyťaženosť jednotlivých tímov slabý ukazovateľ toku hodnoty?
2. Aký je rozdiel medzi process time a lead time?
3. Prečo treba mapovať aj recovery value stream?
4. Ako veľký batch size ovplyvňuje feedback a riziko?
5. Prečo automatizácia najkratšieho kroku nemusí zlepšiť celý systém?
6. Ako sa VSM dopĺňa s DORA metrikami?

## 16. Zhrnutie

Value Stream Mapping zviditeľňuje celý tok práce, najmä čakanie, fronty, handoffs a rework. Je to nástroj systems thinking: optimalizuje výsledok celého delivery systému, nie iba lokálnu rýchlosť jedného tímu alebo nástroja.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Toil a technical debt](toil-and-technical-debt.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: DORA metrics →](dora-metrics.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
