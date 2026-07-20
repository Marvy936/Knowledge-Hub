# Feedback Loops

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Systems Thinking](systems-thinking.md), [DevOps lifecycle](devops-lifecycle.md)
- Súvisiace témy: observability, CI/CD, shift-left, shift-right, SRE, continuous improvement

## 1. Definícia

Feedback loop je mechanizmus, ktorým sa informácia o výsledku činnosti vracia späť k človeku alebo systému, ktorý na základe nej upraví ďalšie správanie.

V DevOps je cieľom vytvárať rýchle, presné a akčné spätné väzby počas celého životného cyklu zmeny.

## 2. Prečo feedback loops existujú

Bez spätnej väzby nevieme, či systém smeruje k požadovanému stavu.

```text
Zmena
  ↓
Systém reaguje
  ↓
Pozorovanie výsledku
  ↓
Porovnanie s očakávaním
  ↓
Korekcia ďalšieho kroku
```

Čím dlhšie trvá, kým sa dozvieme o chybe, tým viac ďalšej práce môže vzniknúť na nesprávnom predpoklade.

## 3. Mentálny model regulačnej slučky

Feedback loop obsahuje štyri základné časti:

1. požadovaný stav alebo cieľ,
2. vykonaná zmena,
3. meranie skutočného výsledku,
4. korekčný zásah.

Príklad Kubernetes controllera:

```text
Desired state: replicas = 3
Observed state: replicas = 2
Controller zistí rozdiel
Controller vytvorí ďalší Pod
Observed state sa priblíži desired state
```

Rovnaký princíp sa dá použiť na delivery proces, incident response aj učenie tímu.

## 4. Negatívna a pozitívna spätná väzba

### Negative feedback

Negatívna spätná väzba znižuje odchýlku od cieľa a stabilizuje systém.

Príklad:

```text
Error rate prekročí limit
→ alert
→ rollback
→ error rate klesne
```

### Positive feedback

Pozitívna spätná väzba zosilňuje aktuálny trend.

Príklad negatívnej špirály:

```text
Viac incidentov
→ viac manuálnych hotfixov
→ menej času na odstránenie technického dlhu
→ ešte viac incidentov
```

Pozitívna spätná väzba nemusí byť „dobrá“. Znamená iba, že zosilňuje zmenu.

## 5. Vlastnosti kvalitnej spätnej väzby

### Rýchlosť

Informácia musí prísť dostatočne skoro, aby ovplyvnila rozhodnutie.

### Presnosť

Signál musí správne reprezentovať stav systému. Falošný alert alebo flaky test znižuje dôveru.

### Kontext

Informácia musí ukázať, čo sa zmenilo, kde sa problém prejavil a aký je dopad.

### Akčnosť

Príjemca musí vedieť, aké ďalšie rozhodnutie alebo diagnostický krok z feedbacku vyplýva.

### Správny adresát

Feedback má dostať tím alebo automatizovaný mechanizmus, ktorý vie stav ovplyvniť.

## 6. Latencia feedbacku

Feedback latency je čas medzi vznikom udalosti a okamihom, keď sa o nej dozvieme a môžeme reagovať.

```text
Syntax error v YAML:
editor validation       → sekundy
pre-commit hook         → desiatky sekúnd
CI pipeline             → minúty
staging deployment      → desiatky minút
produkčný incident      → hodiny alebo dni
```

Rovnaká chyba má inú cenu podľa toho, v ktorej slučke sa odhalí.

## 7. Feedback loops v SDLC

### Lokálny development loop

```text
Edit → lint → test → výsledok
```

Má byť veľmi rýchly, pretože sa opakuje často.

### Code review loop

```text
Commit → review → pripomienka → úprava
```

Kvalita závisí od času review, jasnosti zmien a dostupnosti reviewerov.

### CI loop

```text
Push → build → test → scan → výsledok
```

Má overovať zmenu konzistentne a bez závislosti od lokálneho prostredia autora.

### Deployment loop

```text
Release → rollout → health check → pokračovanie alebo rollback
```

### Production loop

```text
Prevádzka → telemetry → alert / analýza → náprava → nová zmena
```

## 8. Shift-left a shift-right

Shift-left skracuje feedback tým, že kontroly presúva bližšie k vzniku zmeny:

- linting,
- statická analýza,
- unit testy,
- policy checks,
- security scanning.

Shift-right získava feedback z reálneho správania systému:

- monitoring,
- traces,
- syntetické testy,
- canary analýza,
- real user monitoring,
- chaos experiments.

Obidva prístupy sú potrebné. Predprodukčné testy nedokážu úplne simulovať produkčné prostredie a produkčné pozorovanie nemá nahradiť základnú validáciu.

## 9. Signal a noise

Feedback loop zlyháva, ak obsahuje priveľa šumu.

Príklady:

- stovky neakčných alertov,
- flaky testy,
- dashboardy bez prahu alebo kontextu,
- logy bez correlation ID,
- pipeline chyby spôsobené nestabilnou infraštruktúrou.

Keď ľudia opakovane dostávajú falošné signály, začnú ich ignorovať. Dôvera je vlastnosť feedback systému.

## 10. Gain a prehnaná reakcia

V regulačných systémoch gain vyjadruje silu reakcie na odchýlku.

Príliš slabá reakcia:

```text
Služba je preťažená
→ autoscaling pridá príliš málo kapacity
→ problém pretrváva
```

Príliš silná reakcia:

```text
Krátky spike
→ autoscaling prudko zväčší kapacitu
→ spike skončí
→ kapacita prudko klesne
→ systém osciluje
```

Preto sa používajú thresholds, stabilization windows, cooldowny a trendové vyhodnocovanie.

## 11. Praktický príklad: pomalá CI spätná väzba

### Stav

Pipeline trvá 55 minút a vývojár dostáva výsledok až po ďalšom rozpracovaní úloh.

### Dôsledky

- strata mentálneho kontextu,
- viac súčasne rozpracovaných zmien,
- väčší počet konfliktov,
- pomalšie opravy,
- obchádzanie testov.

### Analýza

```text
Lint:              2 min
Unit tests:         6 min
Build image:       12 min
Integration tests: 30 min
Security scan:      5 min
```

### Možné zlepšenie

- spustiť nezávislé joby paralelne,
- použiť cache a incremental build,
- rozdeliť rýchlu commit pipeline a hlbšiu scheduled pipeline,
- spúšťať relevantné testy podľa zmenených komponentov,
- odstrániť flaky testy namiesto ich slepého retry.

Cieľom nie je iba kratšia pipeline, ale skorší dôveryhodný signál.

## 12. Feedback v incident response

Počas incidentu existuje viac slučiek:

```text
Telemetry → detekcia → triage → zásah → nové meranie
```

Po incidente nasleduje organizačná slučka:

```text
Incident → postmortem → nápravné opatrenie → implementácia → overenie účinku
```

Postmortem bez sledovania nápravných opatrení nevytvára uzavretú slučku. Je iba dokumentom.

## 13. Leading a lagging indicators

### Leading indicator

Signalizuje vznikajúce riziko skôr, než sa prejaví výsledný dopad.

Príklady:

- rast queue depth,
- rast latency,
- pokles cache hit rate,
- rast počtu neúspešných deployov.

### Lagging indicator

Opisuje dôsledok, ktorý už nastal.

Príklady:

- SLA breach,
- zákaznícke sťažnosti,
- výpadok,
- strata dát.

Kvalitný systém kombinuje oba typy.

## 14. Anti-patterny

### Feedback bez vlastníka

Report existuje, ale nikto nie je zodpovedný za reakciu.

### Feedback príliš neskoro

Security review až pred produkčným releasom odhalí architektonický problém, ktorý vznikol mesiace predtým.

### Feedback bez kontextu

Alert „CPU high“ neuvádza službu, trend, dopad ani runbook.

### Metrika ako cieľ

Tím optimalizuje počet deploymentov alebo test coverage bez sledovania skutočnej kvality a hodnoty.

### Neuzavreté nápravné opatrenia

Retrospektíva identifikuje problém, ale nevznikne vlastník, termín ani overenie výsledku.

## 15. Návrh feedback loopu

Pri návrhu sa pýtame:

1. Aké rozhodnutie má feedback podporiť?
2. Ktorý signál reprezentuje požadovaný stav?
3. Aká latencia je ešte použiteľná?
4. Kto alebo čo reaguje?
5. Aká reakcia je bezpečná?
6. Ako obmedzíme noise a oscilácie?
7. Ako overíme, že nápravná akcia mala účinok?

## 16. Kontrolné otázky

1. Prečo rýchly, ale nespoľahlivý feedback nemusí byť hodnotný?
2. Aký je rozdiel medzi negative a positive feedback?
3. Ako súvisia flaky testy s dôverou v CI?
4. Prečo production monitoring nenahrádza shift-left kontroly?
5. Čo je feedback latency a prečo ovplyvňuje cenu chyby?
6. Uveď príklad neuzavretej spätnej slučky.

## 17. Zhrnutie

- Feedback loop vracia informáciu o výsledku späť k rozhodovaniu.
- Kvalitný feedback je rýchly, presný, kontextový a akčný.
- Shift-left aj shift-right skracujú rôzne typy spätnej väzby.
- Noise, oneskorenie a nejasný ownership slučku oslabujú.
- Slučka je uzavretá až vtedy, keď sa vykoná korekcia a overí sa jej účinok.