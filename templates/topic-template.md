# Názov témy

## Metadata

- Status: Not Started
- Level: L0
- Domain:
- Prerequisites:
- Related topics:
- Last reviewed:

## 1. Definícia

Presná definícia v jednej alebo dvoch vetách.

## 2. Problém, ktorý rieši

Prečo koncept alebo technológia existuje a čo by bolo bez nej komplikované.

## 3. Mentálny model

Jednoduchý, ale technicky správny spôsob, ako si tému predstaviť. Analógia nesmie nahradiť reálny mechanizmus.

## 4. Ako to funguje

Mechanizmus krok po kroku. Uveď, kto iniciuje operáciu, kde sa ukladá stav a ktoré komponenty komunikujú.

## 5. Komponenty

| Komponent | Zodpovednosť |
|---|---|
|  |  |

## 6. Životný cyklus

Čo sa deje od vytvorenia alebo spustenia po ukončenie či odstránenie.

## 7. Minimálny príklad

Najmenší funkčný príklad, ktorý izoluje základný mechanizmus.

## 8. Realistický príklad

Príklad bližší produkčnému použitiu vrátane relevantných bezpečnostných, prevádzkových a kapacitných nastavení.

## 9. Chybný príklad

Zámerne chybná konfigurácia alebo scenár. Uveď očakávaný symptóm.

## 10. Vysvetlenie príkladov

Vysvetli význam podstatných polí, príkazov a rozhodnutí. Pri príkazoch uveď, čo čítajú alebo menia.

## 11. Interné fungovanie

Detailnejší pohľad na protokoly, procesy, stav, riadiace slučky a závislosti.

## 12. Bezpečnosť

Identity, oprávnenia, šifrovanie, hranice dôvery, secrets a hlavné riziká.

## 13. Produkčný kontext

Čo sa v produkcii rieši inak než v deme. Zahrň dostupnosť, škálovanie, upgrade, rollback a náklady, ak sú relevantné.

## 14. Pozorovanie systému

| Zdroj | Čo ukazuje | Čo v ňom hľadať |
|---|---|---|
| Status |  |  |
| Events |  |  |
| Logs |  |  |
| Metrics |  |  |
| Traces |  |  |

## 15. Časté problémy

Pri každom probléme použi štruktúru:

- Symptóm
- Pravdepodobná príčina
- Diagnostika
- Mechanizmus zlyhania
- Náprava
- Overenie

## 16. Časté omyly

Nesprávne alebo neúplné mentálne modely a presnejšie vysvetlenie.

## 17. Súvisiace témy

Relatívne odkazy na predpoklady, závislosti a nadväzujúce kapitoly.

## 18. Praktický lab

Odkaz na príslušný dokument v `labs/`.

## 19. Kontrolné otázky

1. Definičná otázka.
2. Mechanistická otázka.
3. Porovnávacia otázka.
4. Troubleshooting scenár.
5. Návrhová otázka s trade-offmi.

## 20. Zhrnutie

Najdôležitejšie informácie na rýchle zopakovanie.

## Zdroje

Primárne zdroje: oficiálna dokumentácia, štandardy, RFC alebo pôvodné technické materiály.

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
