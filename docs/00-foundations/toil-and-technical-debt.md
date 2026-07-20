# Toil and Technical Debt

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Automation Mindset](automation-mindset.md), [Continuous Improvement](continuous-improvement.md)
- Súvisiace témy: SRE, automation, incident management, platform engineering, prioritization

## 1. Definícia

**Toil** je opakovaná prevádzková práca, ktorá je prevažne manuálna, automatizovateľná, reaktívna a rastie približne úmerne s veľkosťou systému alebo počtom zákazníkov.

**Technical debt** je budúci náklad vytvorený technickým rozhodnutím, skratkou, zanedbanou údržbou alebo rastúcou komplexitou, ktorá sťažuje ďalšie zmeny a prevádzku.

Tieto pojmy sa prekrývajú, ale nie sú rovnaké.

## 2. Mentálny model

```text
Toil
  = práca, ktorú musíme stále opakovať

Technical debt
  = vlastnosť systému, ktorá robí budúcu prácu drahšou
```

Príklad:

```text
Technical debt: deployment nemá automatizovaný rollback.
Toil: operátor pri každom zlyhaní ručne vykonáva 15 rollback krokov.
```

Dlh môže toil vytvárať. Toil zároveň odoberá kapacitu potrebnú na odstránenie dlhu.

## 3. Typické vlastnosti toil-u

Práca má charakter toil-u, ak spĺňa viacero z týchto znakov:

- je manuálna,
- opakuje sa,
- dá sa automatizovať,
- je reaktívna namiesto strategickej,
- neprináša trvalé zlepšenie systému,
- rastie lineárne s počtom resources, ticketov alebo zákazníkov,
- vyžaduje ľudský zásah iba preto, že systém nemá vhodné rozhranie alebo automatizáciu.

Nie každá manuálna práca je toil. Jednorazová architektonická analýza alebo vyšetrovanie nového incidentu môže mať vysokú hodnotu a nemusí byť automatizovateľné.

## 4. Príklady toil-u

- ručné vytváranie rovnakých používateľských účtov,
- opakované obnovovanie expirovaných certifikátov,
- manuálny deployment podľa checklistu,
- pravidelné čistenie diskov bez odstránenia príčiny rastu,
- kopírovanie údajov medzi ticketovacími systémami,
- ručné reštartovanie služby po známej chybe,
- opakované pridávanie rovnakých firewall pravidiel,
- manuálne škálovanie podľa predvídateľnej metriky.

## 5. Príklady práce, ktorá nie je automaticky toil

- prvé vyšetrovanie neznámeho incidentu,
- návrh disaster recovery stratégie,
- bezpečnostné threat modeling stretnutie,
- refactoring zložitého modulu,
- jednorazová migrácia s vysokým rizikom,
- komunikácia so zákazníkom počas závažného incidentu.

Rozhodujúca nie je nepríjemnosť práce, ale jej opakovateľnosť, škálovanie a možnosť vytvoriť trvalejší mechanizmus.

## 6. Technical debt

Technical debt môže vzniknúť vedome aj nevedome.

### Vedome prijatý dlh

Tím zvolí jednoduchšie riešenie, aby splnil časovo kritický cieľ, a explicitne eviduje následnú nápravu.

### Nevedomý dlh

Tím neskôr zistí, že pôvodný návrh nezvláda nový rozsah, bezpečnostné požiadavky alebo prevádzkový model.

### Zanedbaný dlh

Dočasná skratka sa stane trvalou, nemá ownera ani termín a ďalšie zmeny ju obchádzajú ďalšími skratkami.

## 7. Typy technického dlhu

- architektonický dlh,
- nekvalitné alebo duplicitné implementácie,
- chýbajúce testy,
- zastarané dependencies,
- nepodporované platformy,
- manuálne deployment procesy,
- nedostatočná observability,
- chýbajúce runbooky,
- nejasný ownership,
- nekonzistentná Infrastructure as Code,
- bezpečnostné výnimky bez expirácie.

Dlh nie je iba v aplikačnom kóde. Môže byť v infraštruktúre, procesoch, dokumentácii aj organizačných hraniciach.

## 8. Spätná väzba medzi toil-om a dlhom

```text
Technical debt
      ↓
vytvára manuálne zásahy a incidenty
      ↓
     toil
      ↓
znižuje čas na engineering zlepšenia
      ↓
dlh sa ďalej zväčšuje
```

Tento cyklus môže prevádzkový tím uzamknúť v reaktívnom režime.

## 9. Automatizácia toil-u

Automatizácia je vhodná, keď:

- proces je dostatočne stabilný,
- opakuje sa často,
- riziko ľudskej chyby je významné,
- výsledok je merateľný,
- existuje jasný owner,
- cena automatizácie je nižšia než dlhodobá cena manuálnej práce.

Najprv treba proces pochopiť a zjednodušiť. Automatizácia zlej procedúry môže iba zrýchliť produkciu chýb.

## 10. Odstránenie príčiny vs. automatizácia symptómu

Príklad:

```text
Symptóm: disk sa každý týždeň zaplní.
Rýchla automatizácia: cron maže staré logy.
Root cause riešenie: správna log rotation, retention policy,
centralizované logovanie a alert pred vyčerpaním kapacity.
```

Cron môže byť dočasná ochrana, ale nemusí odstrániť technický dlh.

## 11. Meranie toil-u

Toil možno sledovať napríklad ako:

- hodiny manuálnej opakovanej práce za obdobie,
- počet opakujúcich sa ticketov,
- počet manuálnych krokov na deployment,
- počet stránkovaní spôsobených známou príčinou,
- čas strávený rutinnou údržbou oproti engineering práci,
- rast operačnej práce pri raste zákazníkov.

Meranie má slúžiť na priorizáciu zlepšení, nie na hodnotenie jednotlivcov.

## 12. Evidencia technického dlhu

Dobrý záznam dlhu obsahuje:

- konkrétny problém,
- aktuálny dopad,
- riziko ďalšieho odkladu,
- systémy a tímy, ktorých sa týka,
- navrhovanú nápravu,
- približnú cenu,
- ownera,
- spúšťač alebo termín prehodnotenia.

Položka „refactor platform“ bez dopadu a scope sa ťažko prioritizuje.

## 13. Prioritizácia

Dlh možno posudzovať podľa:

```text
Priorita ≈ frekvencia problému × dopad × rastúce riziko
           ───────────────────────────────────────────
                     cena nápravy
```

Nie je to presný matematický model. Núti však oddeliť hlasné, ale zriedkavé problémy od tichých problémov, ktoré denne spotrebúvajú kapacitu.

## 14. Príklad z CI/CD

Stav:

- pipeline trvá 70 minút,
- testy sú flaky,
- vývojári retryujú joby,
- deployment musí niekto manuálne potvrdiť a doplniť parametre.

Technical debt:

- zlá test isolation,
- neefektívny build graph,
- chýbajúce deterministické prostredie,
- manuálne release rozhranie.

Toil:

- sledovanie pipeline,
- opakované retry,
- ručné vyhľadávanie správnych parametrov,
- manuálna koordinácia deploymentu.

## 15. Anti-patterny

### Hero culture

Skúsený človek opakovane manuálne zachraňuje systém. Organizácia oceňuje zásah, ale neinvestuje do odstránenia príčiny.

### Automatizácia bez ownershipu

Skript odstráni časť toil-u, ale nikto ho netestuje, neaktualizuje ani nesleduje jeho zlyhania.

### Nekonečný backlog dlhu

Dlh sa eviduje, ale nikdy nevstupuje do plánovania a nemá jasné kritériá priority.

### Premenovanie toil-u na „operational excellence“

Rutinná manuálna práca sa normalizuje ako povinnosť namiesto toho, aby sa spochybnila jej potreba.

## 16. Kontrolné otázky

1. Prečo nie je každá manuálna práca toil?
2. Ako môže technical debt vytvárať toil?
3. Prečo môže automatizácia symptómu ponechať root cause nedotknutú?
4. Ktoré údaje by si zbieral pri meraní toil-u?
5. Ako sa líši vedome prijatý dlh od zanedbaného dlhu?
6. Prečo hero culture dlhodobo znižuje reliability?

## 17. Zhrnutie

Toil je opakovaná operačná spotreba ľudskej kapacity. Technical debt je vlastnosť systému, ktorá zvyšuje cenu budúcich zmien a prevádzky. DevOps a SRE sa nesnažia odstrániť všetku manuálnu prácu, ale systematicky znižovať prácu, ktorá neprináša trvalé zlepšenie.