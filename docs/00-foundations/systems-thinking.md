# Systems Thinking

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [DevOps](devops.md), [Three Ways of DevOps](three-ways.md)
- Súvisiace témy: feedback loops, value stream mapping, bottlenecks, observability, SRE

## 1. Definícia

Systems thinking je spôsob uvažovania, pri ktorom systém neposudzujeme ako izolované komponenty, ale ako sieť vzájomne závislých častí, tokov, obmedzení a spätných väzieb.

V DevOps kontexte znamená sledovať celý tok zmeny od nápadu až po produkčný výsledok a optimalizovať výsledok systému, nie iba výkon jedného tímu alebo jedného nástroja.

## 2. Problém, ktorý rieši

Komplexné technické systémy často zlyhávajú na rozhraniach medzi komponentmi a tímami. Každá časť môže lokálne vyzerať efektívne, ale celkový výsledok môže byť pomalý alebo nespoľahlivý.

Príklad:

```text
Development dokončí zmenu za 2 hodiny.
Security review čaká 2 dni.
Provisioning prostredia trvá 3 dni.
Deployment čaká na týždenné okno.
```

Optimalizovať čas kompilácie z 10 na 7 minút má v takom systéme zanedbateľný vplyv. Dominantným problémom sú čakacie doby a organizačné handoffy.

## 3. Mentálny model

Systém možno chápať ako tok práce cez viacero závislých stupňov:

```text
Požiadavka
  ↓
Analýza
  ↓
Implementácia
  ↓
Build a test
  ↓
Security a compliance
  ↓
Release a deployment
  ↓
Prevádzka
  ↓
Používateľský výsledok
```

Výstup jedného stupňa je vstupom ďalšieho. Kapacita celého systému je obmedzená jeho najužším miestom, nie priemerným výkonom všetkých častí.

## 4. Systém, komponent a hranica

Pred analýzou treba určiť hranicu systému.

Napríklad pri probléme „deployment je pomalý“ môže byť hranica príliš úzka:

```text
Pipeline job → Kubernetes API
```

Reálna hranica môže zahŕňať:

```text
Commit
→ code review
→ CI queue
→ build
→ test environment
→ approval
→ artifact promotion
→ deployment
→ readiness
→ produkčné overenie
```

Ak zvolíme príliš úzku hranicu, optimalizujeme iba viditeľný fragment a prehliadneme dominantný zdroj oneskorenia.

## 5. Lokálna a globálna optimalizácia

### Lokálna optimalizácia

Jedna časť systému zlepší vlastnú metriku bez ohľadu na celkový tok.

Príklady:

- vývoj zvýši počet rozpracovaných úloh,
- QA vytvorí veľkú dávku regresných testov až na konci releasu,
- bezpečnostný tím zvýši počet manuálnych kontrol,
- platformový tím štandardizuje proces, ale vytvorí dlhý ticket queue.

### Globálna optimalizácia

Zmena sa hodnotí podľa výsledku celého systému:

- lead time,
- spoľahlivosť,
- kvalita,
- obnoviteľnosť,
- používateľská hodnota,
- množstvo manuálneho toil-u.

Lokálna efektivita má význam iba vtedy, keď zlepšuje alebo aspoň nepoškodzuje globálny výsledok.

## 6. Bottleneck

Bottleneck je časť systému, ktorá obmedzuje jeho priepustnosť.

```text
Kapacita:
Development: 20 zmien/deň
CI:          15 zmien/deň
QA:           5 zmien/deň
Deployment:  10 zmien/deň
```

Celý tok je prakticky obmedzený QA kapacitou približne na 5 zmien denne. Zvýšenie CI kapacity z 15 na 30 problém nevyrieši; môže iba zväčšiť front pred QA.

Práca nahromadená pred bottleneckom predlžuje lead time a zvyšuje rozpracovanosť.

## 7. Fronty a čakacie doby

V delivery systémoch býva väčšina lead time často čakanie, nie aktívna práca.

Typické fronty:

- merge request čakajúci na review,
- pipeline čakajúca na runner,
- deployment čakajúci na approval,
- ticket čakajúci na infra tím,
- incident čakajúci na správneho vlastníka.

Front vzniká, keď príchod práce dlhodobo prekračuje schopnosť systému túto prácu spracovať alebo keď je spracovanie nepravidelné.

## 8. Batch size

Veľké dávky znižujú frekvenciu odovzdávok, ale zvyšujú riziko, variabilitu a cenu diagnostiky.

```text
Veľký release:
50 zmien → zložité testovanie → ťažký rollback → nejasná príčina chyby

Malé zmeny:
1–5 zmien → rýchla spätná väzba → jednoduchšia izolácia problému
```

Menší batch size znižuje množstvo súčasne menených premenných a podporuje plynulejší tok.

## 9. Závislosti a coupling

Systémová analýza sleduje nielen komponenty, ale aj ich väzby.

Silný coupling môže znamenať, že:

- release jednej služby vyžaduje release ďalších služieb,
- databázová zmena blokuje viacero aplikácií,
- centrálna pipeline zmena ovplyvní desiatky tímov,
- zlyhanie identity provideru znefunkční veľkú časť platformy.

Čím viac skrytých závislostí systém obsahuje, tým ťažšie sa predvída správanie zmien.

## 10. Delay a nepriame dôsledky

Dôsledok rozhodnutia nemusí byť okamžitý.

Príklad:

```text
Zrýchlenie delivery bez investície do testov
  ↓
krátkodobo vyššia deployment frequency
  ↓
postupný rast regresií
  ↓
viac incidentov a manuálnych hotfixov
  ↓
nižšia kapacita na ďalší vývoj
```

Oneskorené efekty vedú k nesprávnym záverom, ak meriame iba krátke obdobie.

## 11. Praktický príklad: pomalý deployment

### Symptóm

Tím uvádza, že produkčný deployment trvá priemerne štyri dni od merge.

### Úzka interpretácia

„Kubernetes rollout je pomalý.“

### Systémové pozorovanie

```text
Merge → CI queue:             20 min
Build a test:                 25 min
Čakanie na test environment:  9 h
Acceptance test:              40 min
Čakanie na approval:          2 dni
Deployment:                   8 min
Produkčné overenie:           15 min
```

Samotný Kubernetes deployment nie je bottleneck. Najväčšiu časť lead time tvorí dostupnosť prostredia a approval proces.

### Vhodná náprava

- self-service ephemeral environments,
- automatizované risk-based approvals,
- jasná politika, ktoré zmeny vyžadujú manuálny zásah,
- meranie času čakania oddelene od času spracovania.

## 12. Value stream

Value stream je celý sled aktivít potrebných na dodanie hodnoty používateľovi.

Pri mapovaní sledujeme:

- aktívny processing time,
- waiting time,
- rework,
- handoffy,
- počet rozpracovaných položiek,
- frekvenciu zlyhaní,
- tok informácií a spätnej väzby.

Cieľom nie je vytvoriť pekný diagram. Cieľom je identifikovať obmedzenia a zbytočné oneskorenia.

## 13. Typické systémové otázky

Pri probléme sa pýtame:

1. Aký výsledok má celý systém produkovať?
2. Kde začína a končí analyzovaný tok?
3. Kde práca čaká?
4. Ktorý krok obmedzuje priepustnosť?
5. Kde vzniká rework?
6. Aké závislosti nie sú explicitné?
7. Ktoré metriky podporujú lokálnu optimalizáciu?
8. Aké oneskorené dôsledky môže mať navrhovaná zmena?

## 14. Anti-patterny

### Optimalizácia viditeľného nástroja

Tím rieši výkon pipeline, pretože je ľahko merateľný, hoci väčšina času sa stráca mimo pipeline.

### Presun problému

Automatizácia zrýchli odovzdanie práce ďalšiemu tímu, ale nevyrieši jeho kapacitný limit. Front sa iba presunie.

### Viac rozpracovanej práce ako riešenie

Začatie ďalších úloh zvyšuje work in progress, no nezvyšuje počet dokončených zmien.

### Izolované tímové KPI

Tímy optimalizujú počet ticketov, deploymentov alebo kontrol bez väzby na výsledok služby.

## 15. Produkčný kontext

Systems thinking sa uplatňuje pri:

- návrhu CI/CD procesu,
- organizácii tímov a ownershipu,
- incident response,
- capacity planningu,
- platform engineeringu,
- bezpečnostných kontrolách,
- migráciách a modernizácii systémov.

Technická zmena je kvalitná iba vtedy, keď rešpektuje správanie širšieho systému.

## 16. Kontrolné otázky

1. Prečo zvýšenie kapacity kroku, ktorý nie je bottleneck, nemusí zrýchliť celý tok?
2. Aký je rozdiel medzi processing time a waiting time?
3. Ako môže lokálne úspešné KPI poškodiť globálny výsledok?
4. Prečo veľké batch sizes komplikujú diagnostiku?
5. Ako by si určil hranice systému pri probléme s pomalým releasom?
6. Uveď príklad oneskoreného negatívneho dôsledku technického rozhodnutia.

## 17. Zhrnutie

- Systém je viac než súčet jeho komponentov.
- Celkový tok obmedzuje bottleneck a čakacie doby.
- Lokálna optimalizácia môže zhoršiť globálny výsledok.
- Treba sledovať závislosti, fronty, batch sizes a oneskorené dôsledky.
- DevOps optimalizuje celý value stream od zmeny po používateľský výsledok.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Three Ways of DevOps](three-ways.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Feedback loops →](feedback-loops.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
