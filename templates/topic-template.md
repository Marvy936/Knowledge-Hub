# Názov témy

> Táto šablóna je učebná, nie iba štrukturálna. Jedna veta nasledovaná zoznamom sa nepovažuje za dokončené vysvetlenie konceptu. Každá hlavná sekcia má v súvislom texte vysvetliť význam, mechanizmus a dôsledok; odrážky slúžia až ako zhrnutie alebo referencia. Významová odrážka nesmie byť iba holý názov: musí priamo vysvetliť úlohu položky v aktuálnom kontexte alebo musí byť jej význam jednoznačne vysvetlený v bezprostrednom texte.

## Metadata

- Status: Not Started
- Level: L0
- Domain:
- Prerequisites:
- Related topics:
- Last reviewed:

Metadata je referenčná výnimka. Hodnoty môžu zostať stručné, pretože nejde o konceptuálny výklad.

## 1. Definícia

Presne definuj tému a odlíš ju od najbližších príbuzných pojmov. Nepouži iba jednu tautologickú vetu. Čitateľ má po tejto sekcii vedieť povedať, čo koncept zahŕňa, čo nezahŕňa a na akej systémovej vrstve existuje.

Ak sa v definícii objaví nový odborný termín, krátko ho vysvetli priamo tu alebo odkáž na skoršiu autoritatívnu kapitolu a pridaj lokálne pripomenutie jeho významu.

## 2. Problém, ktorý rieši

Vysvetli, prečo koncept alebo technológia existuje a čo by bolo bez nej komplikované, rizikové alebo neškálovateľné. Popíš príčinu a následok, nie iba zoznam benefitov.

Pridaj aspoň jeden konkrétny scenár: aký systémový problém vznikne bez tohto mechanizmu a ako ho daný koncept zmení.

## 3. Mentálny model

Uveď jednoduchý, ale technicky správny spôsob, ako si tému predstaviť. Analógia môže pomôcť, ale nesmie nahradiť reálny mechanizmus.

Mentálny model doplň o pomenovanie aktérov, stavu, vstupov, výstupov a trust alebo failure boundaries. Ak použiješ diagram alebo zoznam, vysvetli ho v odseku pred alebo za ním.

## 4. Ako to funguje

Popíš mechanizmus krok po kroku v súvislom texte. Uveď, kto iniciuje operáciu, aké vstupy systém prijíma, kde sa mení stav, podľa čoho sa rozhoduje a čo predstavuje úspešný výsledok. Samostatne vysvetli, čo sa stane pri chýbajúcom, stale alebo neplatnom vstupe.

Nasledujúci zoznam je iba kontrola pokrytia; v hotovej kapitole musí mať každý bod konkrétny význam v texte:

- iniciátor — kto začína operáciu a aký outcome očakáva;
- vstupy a dôkazy — čo komponent prijíma a ktorému zdroju dôveruje;
- komunikácia — ktoré komponenty spolu hovoria a akým smerom tečú dáta alebo control;
- stav — kde sa ukladá, mení alebo verziuje authoritative state;
- rozhodnutie — ktoré pravidlá, algoritmus alebo policy určia výsledok;
- úspech — aký pozorovateľný stav potvrdzuje správne dokončenie;
- neplatný vstup — ako systém odmietne, obmedzí alebo bezpečne degraduje operáciu.

Samotné pomenovanie komponentov alebo signálov nestačí. Ak položka zavádza nový pojem, použi formu `pojem — vysvetlenie jeho úlohy` alebo celý vysvetľovací odsek.

## 5. Komponenty a pojmy

Pred tabuľkou vysvetli, čo komponenty spoločne tvoria a ako medzi nimi prechádza control alebo data flow. Čitateľ musí rozumieť vzťahu medzi položkami, nie iba ich samostatným definíciám.

| Komponent alebo pojem | Čo presne znamená | Zodpovednosť v mechanizme | Hranica alebo typické zlyhanie |
|---|---|---|---|
|  |  |  |  |

Nový termín nesmie prvýkrát zostať iba ako názov riadku. Jeho definícia má byť zrozumiteľná bez externého vyhľadávania.

## 6. Životný cyklus

Vysvetli, čo sa deje od vytvorenia, registrácie alebo spustenia po obnovu, rotáciu, ukončenie či odstránenie. Uveď vlastníka stavu a transition podmienky.

Ak lifecycle obsahuje viac stavov, popíš aj neúspešné alebo čiastočné prechody a spôsob recovery.

## 7. Minimálny príklad

Uveď najmenší funkčný príklad, ktorý izoluje základný mechanizmus. Pred príkladom vysvetli, čo má demonštrovať; po príklade vysvetli cause-and-effect medzi vstupom, interným spracovaním a výsledkom.

## 8. Realistický príklad

Pridaj produkčne bližší scenár vrátane relevantných bezpečnostných, prevádzkových, kapacitných a lifecycle nastavení.

Vysvetli rozhodnutia: prečo boli zvolené konkrétne boundaries, identity, timeouty, retry pravidlá, failure defaults alebo rollout model.

## 9. Chybný príklad

Uveď zámerne chybnú konfiguráciu alebo scenár. Vysvetli, čo je chybné, aký symptóm sa objaví, prečo systém zlyhá práve týmto spôsobom a aký dôkaz odlíši túto príčinu od podobných problémov.

Ak použiješ odrážky, každý bod musí obsahovať vysvetlenie, napríklad `symptóm — čo používateľ alebo operátor pozoruje`, nie iba slovo `Symptóm`.

## 10. Vysvetlenie príkladov

Vysvetli význam všetkých podstatných polí, príkazov, objektov a rozhodnutí. Pri príkazoch uveď, čo čítajú alebo menia; pri konfigurácii uveď, kto ju konzumuje a kedy sa prejaví.

Nevysvetlené názvy fields alebo flags sa nepovažujú za učebný výklad.

## 11. Interné fungovanie

Rozšír mechanizmus o protokoly, procesy, dátové štruktúry, stav, riadiace slučky a dependencies. Ukáž, čo je control plane a data plane, kde je authoritative state a aký consistency model sa používa, ak je to relevantné.

Táto sekcia má vysvetliť správanie „pod kapotou“, nie zopakovať zoznam komponentov.

## 12. Bezpečnosť

Vysvetli identity, oprávnenia, šifrovanie, hranice dôvery, secrets a hlavné riziká. Každý uvedený control musí mať vysvetlené, ktorému threatu čelí, na akej boundary sa presadzuje, aký dôkaz používa, čo nezaručuje a čo sa stane pri jeho zlyhaní alebo obídení.

Namiesto holého zoznamu používaj napríklad:

- authorization policy — obmedzuje, ktoré actions môže principal vykonať nad konkrétnym resource-om;
- encryption at rest — chráni uložené bytes pred čítaním mimo autorizovaného storage a key pathu, ale nechráni dáta po legitímnom dešifrovaní aplikáciou;
- audit log — zachytáva actor, action, target a outcome, aby bolo možné spätne overiť použitie oprávnenia.

Po zozname vysvetli, ako sa controls skladajú a kde zostáva residual risk.

## 13. Produkčný kontext

Vysvetli, čo sa v produkcii rieši inak než v deme. Zahrň availability, scaling, upgrades, rollback, state compatibility, ownership a náklady, ak sú relevantné.

Uveď aspoň jeden trade-off. Produkčný návrh nemá byť iba zoznam „best practices“ bez podmienok, za ktorých sú vhodné.

## 14. Pozorovanie systému

Pred tabuľkou popíš, ako sa prejaví zdravý tok a kde vzniká evidence pri zlyhaní.

| Zdroj | Čo ukazuje | Ktorá vrstva ho produkuje | Čo v ňom hľadať |
|---|---|---|---|
| Status |  |  |  |
| Events |  |  |  |
| Logs |  |  |  |
| Metrics |  |  |  |
| Traces |  |  |  |

Vysvetli limity signálov. Absencia logu, metriky alebo eventu nemusí znamenať absenciu problému.

## 15. Časté problémy

Pred jednotlivými prípadmi vysvetli troubleshooting model: od používateľského symptómu cez failure-domain narrowing po dôkaz a overenú nápravu.

Každý problém musí vysvetliť symptóm, pravdepodobnú príčinu, diagnostiku, mechanizmus zlyhania, nápravu a overenie. Tieto názvy nemajú zostať ako samostatné holé odrážky; použite podnadpisy, tabuľku s vysvetľovacími stĺpcami alebo formu `položka — konkrétny obsah`.

Zoznam príkazov bez vysvetlenia, prečo odlišujú jednotlivé hypotézy, nestačí.

## 16. Časté omyly

Popíš nesprávne alebo neúplné mentálne modely. Pri každom omyle vysvetli, prečo pôsobí intuitívne, v čom je technicky nepresný, aký presnejší model ho nahrádza a aké praktické zlyhanie z omylu vzniká.

## 17. Súvisiace témy

Uveď relatívne odkazy na predpoklady, dependencies a nadväzujúce kapitoly. Pri každom dôležitom odkaze jednou vetou vysvetli, akú väzbu má na aktuálnu tému.

Cross-link nenahrádza lokálne vysvetlenie pojmu. Čitateľ má rozumieť jeho významu v tejto kapitole ešte pred otvorením odkazu.

## 18. Praktický lab

Odkaz na príslušný dokument v `labs/`. Uveď, ktorú časť mechanizmu má lab preukázať a aký dôkaz úspechu má používateľ pozorovať.

## 19. Kontrolné otázky

1. Definičná otázka, ktorá vyžaduje odlíšenie od susedného pojmu.
2. Mechanistická otázka o actors, state alebo data flow.
3. Porovnávacia otázka s podmienkami a trade-offmi.
4. Troubleshooting scenár vyžadujúci hypotézu a dôkaz.
5. Návrhová otázka s boundary, failure a recovery požiadavkami.

Otázky nemajú testovať iba rozpoznanie názvov alebo memorovanie zoznamu. Táto sekcia je referenčná výnimka a nemusí vysvetľovať každú otázku ako koncept.

## 20. Zhrnutie

Zhrň najdôležitejšie informácie na rýchle zopakovanie. Zhrnutie môže byť stručné, pretože plný mechanizmus už musí byť vysvetlený vyššie.

## Glossary impact

Pred dokončením kapitoly skontroluj `GLOSSARY.md`:

- nový pojem — pridaj iba opakovane použiteľný technický termín a vysvetli jeho stabilný význam;
- existujúce heslo — spresni ho, ak kapitola priniesla presnejší mechanizmus;
- autoritatívny odkaz — prepoj heslo na kapitolu, ktorá pojem vysvetľuje do hĺbky;
- jednorazový názov — nepridávaj command alebo field bez širšieho významu;
- bez zmeny — pri review explicitne potvrď, že kapitola glossary nemení.

Glossary sa má aktualizovať v rovnakom pracovnom bloku ako článok, nie odložene v samostatnom neurčitom backloge.

## Zdroje

Použi primárne zdroje: oficiálnu dokumentáciu, štandardy, RFC alebo pôvodné technické materiály. Zdroj má podporovať konkrétny mechanizmus alebo tvrdenie; zoznam odkazov nenahrádza syntézu a vysvetlenie.

## Kontrola učebnej hĺbky

Pred dokončením spusti:

```bash
python scripts/audit_learning_depth.py
```

Skontroluj najmä nálezy:

- `single-sentence-concept` — konceptuálna sekcia má iba jednu obsahovú vetu;
- `outline-instead-of-explanation` — zoznam nahrádza samotný výklad;
- `list-first-introduction` — sekcia začína zoznamom bez mentálneho modelu;
- `bare-bullet-items` — odrážky iba pomenúvajú položky bez kontextového vysvetlenia;
- `thin-concept-section` — súvislý výklad je príliš krátky;
- `term-before-explanation` — nový pojem sa objavil skôr, než bol vysvetlený.

Heuristický audit nie je náhradou ľudského review. Autor musí overiť, že každá dôležitá sekcia odpovedá na otázky **čo**, **prečo**, **ako**, **príklad** a **kde to zlyháva** a že každá významová odrážka objasňuje svoju úlohu v aktuálnom kontexte.

## Navigačný kontrakt

Učebný článok musí byť uvedený ako očíslovaný Markdown odkaz v sekčnom `README.md`. Poradie v tomto indexe je jediným zdrojom poradia článkov.

Footer `Predchádzajúca / Obsah sekcie / Nasledujúca` sa nepíše ručne. Generuje ho:

```bash
python scripts/update_navigation.py --write
```

CI overuje synchronizáciu príkazom:

```bash
python scripts/update_navigation.py --check
```

Generovaná časť je označená komentármi `KNOWLEDGE-NAVIGATION:START` a `KNOWLEDGE-NAVIGATION:END`. Obsah medzi nimi sa nemá ručne upravovať.
