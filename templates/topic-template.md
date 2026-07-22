# Názov témy

> Táto šablóna je učebná, nie iba štrukturálna. Jedna veta nasledovaná zoznamom sa nepovažuje za dokončené vysvetlenie konceptu. Každá hlavná sekcia má v súvislom texte vysvetliť význam, mechanizmus a dôsledok; odrážky slúžia až ako zhrnutie alebo referencia.

## Metadata

- Status: Not Started
- Level: L0
- Domain:
- Prerequisites:
- Related topics:
- Last reviewed:

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

Popíš mechanizmus krok po kroku v súvislom texte. Uveď:

- kto iniciuje operáciu a prečo;
- aké vstupy alebo dôkazy systém prijíma;
- ktoré komponenty komunikujú a akým smerom;
- kde sa ukladá alebo mení stav;
- podľa čoho sa vykonáva rozhodnutie;
- aký je úspešný výsledok;
- čo sa stane pri chýbajúcom, stale alebo neplatnom vstupe.

Každý bod zo zoznamu musí mať vysvetlenie v texte. Samotné pomenovanie komponentov alebo signálov nestačí.

## 5. Komponenty a pojmy

Pred tabuľkou vysvetli, čo komponenty spoločne tvoria a ako medzi nimi prechádza control alebo data flow.

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

Uveď zámerne chybnú konfiguráciu alebo scenár. Popíš:

- čo je chybné;
- aký symptóm sa objaví;
- prečo systém zlyhá práve týmto spôsobom;
- aký dôkaz odlíši túto príčinu od podobných problémov.

## 10. Vysvetlenie príkladov

Vysvetli význam všetkých podstatných polí, príkazov, objektov a rozhodnutí. Pri príkazoch uveď, čo čítajú alebo menia; pri konfigurácii uveď, kto ju konzumuje a kedy sa prejaví.

Nevysvetlené názvy fields alebo flags sa nepovažujú za učebný výklad.

## 11. Interné fungovanie

Rozšír mechanizmus o protokoly, procesy, dátové štruktúry, stav, riadiace slučky a dependencies. Ukáž, čo je control plane a data plane, kde je authoritative state a aký consistency model sa používa, ak je to relevantné.

Táto sekcia má vysvetliť správanie „pod kapotou“, nie zopakovať zoznam komponentov.

## 12. Bezpečnosť

Vysvetli identity, oprávnenia, šifrovanie, hranice dôvery, secrets a hlavné riziká. Pri každom controle uveď:

- ktorému threatu čelí;
- na akej boundary sa presadzuje;
- aký dôkaz alebo signal používa;
- čo control nezaručuje;
- čo sa stane pri jeho zlyhaní alebo obídení.

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

Pri každom probléme použi štruktúru:

- Symptóm
- Pravdepodobná príčina
- Diagnostika
- Mechanizmus zlyhania
- Náprava
- Overenie

Zoznam príkazov bez vysvetlenia, prečo odlišujú jednotlivé hypotézy, nestačí.

## 16. Časté omyly

Popíš nesprávne alebo neúplné mentálne modely. Pri každom omyle vysvetli:

1. prečo pôsobí intuitívne;
2. v čom je technicky nepresný;
3. aký presnejší model ho nahrádza;
4. aké praktické zlyhanie z omylu vzniká.

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

Otázky nemajú testovať iba rozpoznanie názvov alebo memorovanie zoznamu.

## 20. Zhrnutie

Zhrň najdôležitejšie informácie na rýchle zopakovanie. Zhrnutie môže byť stručné, pretože plný mechanizmus už musí byť vysvetlený vyššie.

## Glossary impact

Pred dokončením kapitoly skontroluj `GLOSSARY.md`:

- pridaj nové opakovane použiteľné technické pojmy;
- existujúce heslá spresni, ak kapitola priniesla presnejší mechanizmus;
- každé heslo podľa možnosti prepoj na autoritatívnu kapitolu;
- nepridávaj jednorazové názvy príkazov alebo polí bez širšieho významu;
- ak kapitola glossary nemení, explicitne to potvrď pri review.

Glossary sa má aktualizovať v rovnakom pracovnom bloku ako článok, nie odložene v samostatnom neurčitom backloge.

## Zdroje

Použi primárne zdroje: oficiálnu dokumentáciu, štandardy, RFC alebo pôvodné technické materiály. Zdroj má podporovať konkrétny mechanizmus alebo tvrdenie; zoznam odkazov nenahrádza syntézu a vysvetlenie.

## Kontrola učebnej hĺbky

Pred dokončením spusti:

```bash
python scripts/audit_learning_depth.py
```

Skontroluj najmä nálezy:

- `outline-instead-of-explanation`;
- `list-first-introduction`;
- `thin-concept-section`;
- `term-before-explanation`.

Heuristický audit nie je náhradou ľudského review. Autor musí overiť, že každá dôležitá sekcia odpovedá na otázky **čo**, **prečo**, **ako**, **príklad** a **kde to zlyháva**.

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
