# DevOps

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Software Development Life Cycle](sdlc.md)
- Súvisiace témy: CALMS, Three Ways, CI/CD, testing, SRE, platform engineering

## 1. Definícia

DevOps je súbor kultúrnych princípov, organizačných praktík a technických mechanizmov, ktoré spájajú vývoj a prevádzku s cieľom dodávať zmeny rýchlo, bezpečne, opakovateľne a s krátkou spätnou väzbou.

DevOps nie je jeden nástroj, produkt ani pracovná pozícia. Organizácia môže používať Docker, Kubernetes a CI pipeline a napriek tomu fungovať spôsobom, ktorý je v rozpore s DevOps princípmi.

## 2. Problém, ktorý rieši

Tradičné oddelenie vývoja a prevádzky vytvára rozdielne lokálne ciele:

- vývoj chce dodávať nové zmeny,
- prevádzka chce minimalizovať zmeny a chrániť stabilitu.

Ak tímy komunikujú najmä cez odovzdávky a tickety, vznikajú dlhé čakacie doby, nejasná zodpovednosť, manuálne kroky a konflikty. DevOps sa snaží optimalizovať celý tok hodnoty namiesto jednotlivých oddelení.

## 3. Mentálny model

DevOps možno chápať ako uzavretú regulačnú slučku:

```text
Plánovanie
  ↓
Vývoj
  ↓
Build a test
  ↓
Release a deployment
  ↓
Prevádzka
  ↓
Monitoring a spätná väzba
  └──────────────────→ späť do plánovania
```

Rýchlosť nie je výsledkom preskočenia kontrol. Vzniká tým, že kontroly sú automatizované, konzistentné a poskytujú spätnú väzbu skôr.

## 4. DevOps ako kultúra, praktiky a technológie

### Kultúra

Kultúrna vrstva zahŕňa zdieľanú zodpovednosť, spoluprácu, transparentnosť, učenie zo zlyhaní a optimalizáciu celého systému.

### Praktiky

Medzi typické praktiky patria:

- malé a časté zmeny,
- trunk-based development alebo krátko žijúce vetvy,
- automatizované testovanie,
- Continuous Integration a Continuous Delivery,
- Infrastructure as Code,
- observability,
- postmortems,
- priebežné zlepšovanie.

### Technológie

Git, GitLab, Terraform, Ansible, Docker, Kubernetes, Prometheus a AWS sú nástroje, ktoré môžu DevOps praktiky podporovať. Samy osebe však organizačné bariéry ani zlý ownership nevyriešia.

## 5. Hlavné princípy

### Shared ownership

Tím nezodpovedá iba za odovzdanie kódu, ale za správanie služby počas celého životného cyklu. Zodpovednosť nemusí znamenať, že každý vykonáva všetky úlohy. Znamená, že hranice rolí neoddeľujú tím od výsledku.

### Systems thinking

Lokálna optimalizácia môže zhoršiť celý systém. Napríklad zrýchlenie build jobu nemá veľkú hodnotu, ak zmena čaká dva dni na manuálne schválenie alebo týždeň na pridelenie prostredia.

### Short feedback loops

Čím skôr tím zistí problém, tým lacnejšie ho vie opraviť. Preto sa kontroly presúvajú bližšie k vzniku zmeny a produkčná spätná väzba sa vracia späť k vývoju.

### Automation

Automatizácia odstraňuje opakovateľnú manuálnu prácu, znižuje variabilitu a vytvára auditovateľný proces. Nemá automatizovať nepochopený alebo chybný proces bez jeho predchádzajúceho zjednodušenia.

### Small batch sizes

Menšie zmeny sa jednoduchšie kontrolujú, testujú, nasadzujú a vracajú späť. Znižujú počet premenných pri diagnostike a skracujú čas medzi vznikom a overením zmeny.

### Continuous improvement

Proces sa nepovažuje za definitívne dokončený. Tím sleduje úzke miesta, incidenty, čakacie doby a manuálny toil a priebežne upravuje systém práce.

## 6. DevOps lifecycle

Často sa používa nekonečný cyklus:

```text
Plan → Code → Build → Test → Release → Deploy → Operate → Monitor
  ↑                                                        ↓
  └────────────────────── feedback ────────────────────────┘
```

Tento model je užitočný ako orientácia, ale nemá sa chápať ako pevná organizačná štruktúra. V modernom delivery procese mnoho krokov prebieha paralelne a opakovane.

## 7. DevOps engineer

DevOps engineer je pracovná rola, ktorá implementuje alebo prevádzkuje časť DevOps schopností. Typicky pracuje s automatizáciou, CI/CD, cloudom, kontajnermi, observability, bezpečnosťou a reliability.

Dôležité rozlíšenie:

```text
DevOps
  = spôsob fungovania organizácie a delivery systému

DevOps engineer
  = konkrétna technická rola v tomto systéme
```

Ak všetka prevádzková zodpovednosť zostane izolovaná v „DevOps tíme“, môže sa iba premenovať pôvodné silo Ops bez skutočnej zmeny modelu.

## 8. T-shaped profil

T-shaped engineer má široký prehľad naprieč systémom a hlbokú expertízu v jednej alebo niekoľkých oblastiach.

```text
Šírka:
SDLC, Git, Linux, networking, security, cloud, CI/CD,
containers, Kubernetes, monitoring, databases

Hĺbka:
napríklad Kubernetes platforma a cloud automation
```

Šírka umožňuje chápať závislosti a komunikovať s ostatnými disciplínami. Hĺbka umožňuje riešiť komplexné problémy a robiť kvalifikované technické rozhodnutia.

## 9. Príklad DevOps toku

Vývojár zmení API aplikácie:

```text
Commit do Gitu
  ↓
Pre-commit a statická kontrola
  ↓
CI: build, unit a integration tests
  ↓
Vytvorenie verziovaného image
  ↓
Security a dependency scan
  ↓
Deployment do testovacieho prostredia
  ↓
Smoke a end-to-end testy
  ↓
Canary rollout do produkcie
  ↓
Sledovanie error rate, latency a business metrík
  ↓
Automatické alebo manuálne rozhodnutie pokračovať / rollback
```

DevOps hodnota nie je v tom, že pipeline existuje. Hodnota je v tom, že vytvára konzistentný, rýchly a merateľný tok spätnej väzby.

## 10. DevOps a CI/CD

CI/CD je významná technická implementácia DevOps princípov, ale nie je ich celým obsahom.

CI/CD rieši najmä integráciu, overenie, packaging a delivery zmien. DevOps navyše rieši organizáciu tímov, ownership, observability, incidenty, bezpečnosť, reliability a priebežné zlepšovanie.

## 11. DevOps a Agile

Agile sa primárne sústreďuje na spôsob vývoja a iteratívne dodávanie hodnoty. DevOps rozširuje tento tok cez build, deployment a prevádzku.

Agile bez DevOps môže produkovať funkcie rýchlo, ale nasadzovať ich pomaly. DevOps bez produktového a používateľského feedbacku môže efektívne dodávať zmeny s nízkou hodnotou.

## 12. DevOps a SRE

SRE je konkrétnejší engineering prístup k prevádzke spoľahlivých systémov. Používa napríklad SLI, SLO, error budgets, riadenie toil-u a automatizáciu.

DevOps poskytuje širšie princípy spolupráce a toku. SRE poskytuje presnejšie mechanizmy na riadenie reliability. Tieto prístupy sa dopĺňajú.

## 13. Meranie výsledkov

DevOps úspech sa nemeria počtom nástrojov ani pipeline jobov. Dôležité sú výsledky systému.

Medzi kľúčové DORA metriky patria:

- deployment frequency,
- lead time for changes,
- change failure rate,
- time to restore service.

Metriky treba vyhodnocovať spoločne. Vysoká deployment frequency bez kontroly zlyhaní nie je úspech; extrémna stabilita dosiahnutá nulovým nasadzovaním tiež nie.

## 14. Anti-patterns

### DevOps ako premenovaný Ops tím

Vývoj odovzdá aplikáciu samostatnému DevOps tímu, ktorý vykoná build, deployment a prevádzku. Zodpovednosť a úzke miesta zostávajú oddelené.

### Tool-first transformation

Organizácia kúpi nástroje bez zmeny procesu, ownershipu a spätnej väzby. Výsledkom je automatizovaný neefektívny proces.

### Automatizácia všetkého bez priority

Automatizovať sa má opakovateľná, stabilná a hodnotná činnosť. Jednorazová alebo nepochopená práca môže mať vyššiu cenu automatizácie než manuálneho vykonania.

### „You build it, you run it“ bez podpory

Preniesť on-call na vývojárov bez observability, školenia, runbookov a kapacity iba presunie stres. Ownership musí byť podporený platformou a procesmi.

### Pipeline ako cieľ

Pipeline je mechanizmus. Cieľom je spoľahlivé dodanie hodnoty. Komplexná pipeline môže sama vytvárať dlhý lead time a vysoké náklady na údržbu.

## 15. Časté omyly

### „DevOps znamená developer, ktorý robí aj administráciu“

Nie. Ide o systém spolupráce a delivery, nie iba o rozšírenie zoznamu povinností jednej osoby.

### „DevOps odstráni všetky špecializované roly“

Nie. Špecializácia zostáva potrebná. Mení sa spôsob spolupráce, rozhrania a zodpovednosť za výsledok.

### „Viac automatizácie vždy znamená lepší DevOps“

Nie. Automatizácia zlého procesu môže zrýchliť produkciu chýb alebo vytvoriť neprehľadnú platformu.

### „Rýchlosť a stabilita sú protiklady“

Pri veľkých, manuálnych a zriedkavých zmenách často áno. Pri malých zmenách, automatizovaných kontrolách a rýchlom recovery sa môžu zlepšovať súčasne.

## 16. Produkčný kontext

Funkčný DevOps model potrebuje viac než nástroje:

- jasný ownership služieb,
- štandardizovaný a auditovateľný delivery proces,
- bezpečné defaulty,
- self-service platformové schopnosti,
- observability navrhnutú spolu so službou,
- riadenie incidentov a učenie z nich,
- meranie toku a reliability,
- čas vyhradený na odstránenie toil-u a technického dlhu.

## 17. Kontrolné otázky

1. Prečo DevOps nie je synonymum pre CI/CD alebo Kubernetes?
2. Aký konflikt cieľov vzniká medzi tradične oddeleným Dev a Ops?
3. Ako small batch sizes znižujú deployment a troubleshooting riziko?
4. Prečo lokálna optimalizácia jedného tímu nemusí zlepšiť celý delivery systém?
5. Aký je rozdiel medzi DevOps a rolou DevOps engineer?
6. Prečo tool-first transformácia často zlyhá?
7. Ako sa DevOps, Agile a SRE navzájom dopĺňajú?
8. Prečo treba DORA metriky hodnotiť spoločne?
9. Kedy automatizácia nemusí byť správnym prvým krokom?

## 18. Zhrnutie

- DevOps spája kultúru, procesy a technické mechanizmy.
- Cieľom je optimalizovať celý tok hodnoty a spätnú väzbu.
- Nástroje DevOps podporujú, ale nevytvárajú ho automaticky.
- Shared ownership neznamená zrušenie špecializácie.
- Malé zmeny, automatizované kontroly a observability umožňujú zvyšovať rýchlosť aj stabilitu.
- Úspech sa meria výsledkami delivery a reliability, nie počtom používaných nástrojov.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Software Development Life Cycle](sdlc.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: DevOps lifecycle →](devops-lifecycle.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
