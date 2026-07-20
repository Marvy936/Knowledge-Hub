# Three Ways of DevOps

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [DevOps](devops.md), [DevOps Lifecycle](devops-lifecycle.md), [CALMS](calms.md)
- Súvisiace témy: systems thinking, feedback loops, continuous learning, CI/CD, observability, incident management

## 1. Definícia

Three Ways of DevOps sú tri systémové princípy, ktoré opisujú, ako má organizácia navrhovať tok práce, spätnú väzbu a učenie:

1. **The First Way — Flow**
2. **The Second Way — Feedback**
3. **The Third Way — Continual Learning and Experimentation**

Nejde o tri chronologické fázy projektu. Sú to tri súčasne fungujúce vlastnosti delivery systému.

## 2. Problém, ktorý riešia

Organizácia môže mať kvalitných odborníkov aj moderné nástroje a napriek tomu dodávať pomaly a rizikovo, ak:

- práca čaká medzi tímami,
- spätná väzba prichádza neskoro,
- chyby sa opakujú,
- ľudia optimalizujú iba svoju časť systému,
- experimentovanie je príliš nebezpečné,
- incidenty nevytvárajú trvalé zlepšenie.

Three Ways presúvajú pozornosť z izolovaných úloh na správanie celého systému.

## 3. Základný mentálny model

```text
First Way
Tok práce zľava doprava
Business → Development → Delivery → Operations → Customer

Second Way
Spätná väzba sprava doľava
Customer / Production → Operations → Development → Planning

Third Way
Opakované učenie naprieč celým systémom
Experiment → Pozorovanie → Poučenie → Zmena systému
```

Bez First Way sa práca nepohybuje plynulo. Bez Second Way sa systém nevie rýchlo korigovať. Bez Third Way sa rovnaké chyby a obmedzenia opakujú.

# The First Way — Flow

## 4. Definícia Flow

First Way sa sústreďuje na rýchly, predvídateľný a bezpečný tok práce od požiadavky k používateľskej hodnote.

Cieľom nie je maximalizovať lokálnu vyťaženosť každého človeka alebo tímu. Cieľom je maximalizovať plynulosť celého value streamu.

## 5. Hlavné mechanizmy Flow

### Vizualizácia práce

Práca musí byť viditeľná. Neviditeľné fronty, neformálne požiadavky a skryté závislosti nemožno efektívne riadiť.

### Limitovanie work in progress

Príliš veľa rozpracovanej práce vytvára:

- multitasking,
- dlhšie čakacie doby,
- viac konfliktov priorít,
- pomalšie dokončovanie,
- zastarané rozpracované zmeny.

### Small batch sizes

Menšie zmeny skracujú čas do spätnej väzby a znižujú blast radius.

### Odstraňovanie úzkych miest

Throughput systému je obmedzený jeho najužším miestom. Zrýchlenie neobmedzujúcej časti systému môže iba zväčšiť front pred bottleneckom.

### Znižovanie handoffov

Každé odovzdanie zvyšuje riziko straty kontextu a čakacej doby.

### Built-in quality

Kvalita sa nevkladá až na konci samostatnou kontrolou. Kontroly sú súčasťou toku od začiatku.

### Automatizácia opakovateľných krokov

Automatizácia znižuje variabilitu a skracuje processing time, ak je proces najprv pochopený a zjednodušený.

## 6. Príklad First Way

Pôvodný proces:

```text
Developer dokončí zmenu
  ↓
2 dni čaká na review
  ↓
1 deň čaká na testovacie prostredie
  ↓
QA testuje veľký balík zmien
  ↓
Release čaká na mesačné okno
```

Zlepšený proces:

```text
Malá zmena
  ↓
Automatické lokálne a CI kontroly
  ↓
Krátko žijúca vetva a rýchle review
  ↓
On-demand test environment
  ↓
Automatizované smoke testy
  ↓
Priebežná promotion do produkcie
```

Hlavné zlepšenie nemusí pochádzať z rýchlejšieho kompilátora. Vzniká odstránením čakania, frontov a veľkých batchov.

## 7. Anti-patterny First Way

### Maximálna lokálna vyťaženosť

Každý tím má vlastný backlog a je permanentne vyťažený na 100 %. Nová práca potom čaká, pretože systém nemá rezervnú kapacitu na variabilitu, incidenty ani urgentné požiadavky.

### Veľké release batchy

Zmeny sa akumulujú, pretože deployment je drahý a rizikový. Veľké batchy následne robia deployment ešte drahším a rizikovejším.

### Throw over the wall

Vývoj odovzdá zmenu ďalšiemu tímu bez spoločného kontextu a ownershipu.

### Automatizovaný bottleneck

Neefektívny proces sa automatizuje bez odstránenia zbytočných schválení a handoffov.

# The Second Way — Feedback

## 8. Definícia Feedback

Second Way vytvára rýchle a kvalitné spätné väzby z neskorších častí systému smerom k skorším častiam.

Cieľom je zistiť odchýlku čo najbližšie k jej vzniku a umožniť rýchlu korekciu.

## 9. Hlavné mechanizmy Feedback

### Rýchla technická spätná väzba

- compiler errors,
- linting,
- unit tests,
- integration tests,
- policy checks,
- security scans,
- deployment verification.

### Produkčná spätná väzba

- metrics,
- logs,
- traces,
- user feedback,
- support tickets,
- SLO violations,
- business outcomes.

### Observability

Tím musí vedieť položiť nové otázky o správaní systému bez potreby vopred pripraviť samostatnú metriku pre každú možnú poruchu.

### Stop-the-line mentality

Keď kontrola odhalí závažný problém, tok sa zastaví a problém sa rieši namiesto pokračovania s vedomou chybou.

### Shared operational feedback

Vývojári musia vidieť, ako sa ich zmeny správajú v produkcii. Prevádzkové poznatky sa nesmú uzavrieť v oddelenom Ops tíme.

## 10. Príklad Second Way

```text
Commit
  ↓
CI odhalí nekompatibilnú API zmenu do 5 minút
  ↓
Autor dostane presný test failure
  ↓
Zmena sa opraví pred merge
```

Alternatívny slabý proces:

```text
API zmena sa zlúči
  ↓
O týždeň sa nasadí do integračného prostredia
  ↓
Iný tím nájde chybu
  ↓
Pôvodný autor už pracuje na inej téme
```

Technická chyba je rovnaká, ale cena opravy je výrazne vyššia pre stratu kontextu, koordináciu a rework.

## 11. Kvalita spätnej väzby

Spätná väzba musí byť:

- rýchla,
- relevantná,
- dôveryhodná,
- konkrétna,
- dostupná osobe schopnej konať.

Flaky test, ktorý náhodne zlyháva, vytvára šum. Alert bez ownershipu a kontextu vytvára alert fatigue. Veľa nekvalitných signálov môže byť horších než menší počet presných signálov.

## 12. Anti-patterny Second Way

### Late feedback

Chyba sa objaví až počas veľkého integračného testu alebo produkčného deploymentu.

### Feedback bez kontextu

Pipeline oznámi iba „job failed“ bez logu, príčiny alebo odkazu na nápravu.

### Monitoring iba pre Operations

Vývojári nevidia produkčné metriky a nepoznajú následky svojich zmien.

### Alerting na každý symptóm

Veľké množstvo neakčných alertov znižuje dôveru v celý alerting systém.

### Potlačenie zlých správ

Ľudia sa boja eskalovať riziko alebo incident, pretože reakciou je obviňovanie.

# The Third Way — Continual Learning and Experimentation

## 13. Definícia continual learning

Third Way vytvára kultúru a technické podmienky na priebežné experimentovanie, učenie zo zlyhaní a zabudovanie poznatkov späť do systému.

Cieľom nie je eliminovať všetky chyby. Cieľom je robiť bezpečné experimenty, rýchlo sa učiť a zabrániť opakovaniu rovnakých systémových zlyhaní.

## 14. Hlavné mechanizmy Third Way

### Blameless postmortems

Postmortem analyzuje systémové podmienky, rozhodnutia a chýbajúce ochrany. Neznamená absenciu zodpovednosti; znamená odmietnutie zjednodušujúceho záveru „chybu spôsobil človek“.

### Controlled experimentation

Experiment má:

- hypotézu,
- obmedzený blast radius,
- merateľný výsledok,
- stop podmienku,
- rollback plán.

### Chaos engineering

Systém sa kontrolovane vystavuje zlyhaniam, aby sa overili predpoklady o jeho odolnosti.

### Practice and simulation

Game days, incident drills a restore testy vytvárajú skúsenosť pred skutočnou krízou.

### Knowledge institutionalization

Poučenie sa musí premietnuť do:

- testu,
- automatizácie,
- guardrailu,
- runbooku,
- architektonickej zmeny,
- školenia,
- monitoringu.

Inak zostane iba poznámkou, ktorú systém časom zabudne.

## 15. Príklad Third Way

Incident vznikne po expirácii certifikátu.

Slabá reakcia:

```text
Certifikát sa manuálne obnoví
  ↓
Incident sa uzavrie
```

Systémové učenie:

```text
Obnova služby
  ↓
Postmortem
  ↓
Automatizovaný renewal
  ↓
Alert pred expiráciou
  ↓
Runbook a ownership certifikátu
  ↓
Test renewal procesu
```

Rozdiel je v tom, že druhý prístup mení schopnosť systému, nie iba aktuálny stav.

## 16. Psychologické bezpečie

Učenie vyžaduje, aby ľudia mohli otvorene hovoriť o:

- neistote,
- chybných predpokladoch,
- near misses,
- technickom dlhu,
- nebezpečných workaroundoch.

Ak organizácia trestá nositeľa zlej správy, problémy sa skryjú a feedback loop sa preruší.

Psychologické bezpečie neznamená, že neexistujú štandardy alebo zodpovednosť. Znamená, že organizácia hľadá pravdivé informácie potrebné na zlepšenie systému.

## 17. Anti-patterny Third Way

### Postmortem ako formalita

Dokument vznikne, ale nápravné akcie nemajú ownera, termín ani prioritu.

### Hero culture

Organizácia oceňuje jednotlivcov, ktorí opakovane zachraňujú systém manuálnymi zásahmi, namiesto odstránenia príčiny potreby zásahov.

### Experiment bez guardrails

Zmena sa označí za experiment, ale nemá hypotézu, meranie ani kontrolovaný blast radius.

### Zero-failure culture

Každé zlyhanie je považované za neprijateľné. Výsledkom je skrývanie problémov, pomalé zmeny a slabá schopnosť učenia.

### Opakovaný incident bez systémovej zmeny

Tím obnoví službu, ale nezmení testy, automatizáciu ani architektúru.

## 18. Vzťah medzi Three Ways

Three Ways sa navzájom podmieňujú:

```text
Flow bez Feedback
  → chyby sa pohybujú rýchlo smerom k produkcii

Feedback bez Flow
  → problém sa zistí, ale oprava čaká v pomalom systéme

Flow a Feedback bez Learning
  → systém sa koriguje, ale dlhodobo sa nezlepšuje
```

Vyspelý delivery systém potrebuje všetky tri.

## 19. Praktický audit systému

### First Way

- Aký je lead time od commitu po produkciu?
- Kde práca najdlhšie čaká?
- Aká je veľkosť typickej zmeny?
- Ktorý tím alebo proces je bottleneck?
- Koľko handoffov zmena prejde?

### Second Way

- Ako rýchlo autor zistí chybu?
- Sú testy dôveryhodné?
- Vidí tím produkčné správanie svojej služby?
- Sú alerty akčné a majú ownera?
- Vracia sa používateľská spätná väzba do backlogu?

### Third Way

- Menia incidenty systém alebo iba aktuálny stav?
- Testujú sa backupy a restore procesy?
- Existujú game days alebo incident drills?
- Môžu ľudia bezpečne hlásiť near miss?
- Majú postmortem akcie ownera a termín?

## 20. Príklad mapovania na nástroje

Nástroje nie sú samotné Three Ways, ale môžu ich podporovať:

| Princíp | Mechanizmus | Príklad nástroja |
|---|---|---|
| Flow | version control a pipeline | Git, GitLab CI |
| Flow | reproducible infrastructure | Terraform, Ansible |
| Feedback | automated tests | test framework, CI runner |
| Feedback | production telemetry | Prometheus, Grafana, OpenTelemetry |
| Learning | postmortem workflow | issue tracker, documentation |
| Learning | controlled rollout | Kubernetes, Argo Rollouts, feature flags |

Moderný nástroj nezaručuje správny princíp. Pipeline môže mať dlhé manuálne fronty a monitoring môže byť bez akčnej spätnej väzby.

## 21. Časté omyly

### „First Way znamená iba zrýchliť deployment“

Nie. Ide o celý value stream od požiadavky k hodnote, vrátane čakacích dôb a handoffov.

### „Second Way znamená viac dashboardov“

Nie. Spätná väzba musí viesť k rýchlej a správnej akcii.

### „Third Way ospravedlňuje chyby“

Nie. Umožňuje ich pravdivo analyzovať a systematicky znižovať ich opakovanie.

### „Three Ways sa implementujú postupne a potom sú hotové“

Nie. Sú to trvalé vlastnosti systému a predmet priebežného zlepšovania.

## 22. Kontrolné otázky

1. Čo optimalizuje First Way?
2. Prečo 100 % vyťaženosť všetkých tímov môže spomaliť celý systém?
3. Aké vlastnosti má kvalitná spätná väzba?
4. Prečo flaky test poškodzuje Second Way?
5. Ako sa líši obnova služby od systémového učenia?
6. Čo musí obsahovať bezpečný experiment?
7. Prečo blameless postmortem neznamená absenciu zodpovednosti?
8. Uveď príklad Flow bez Feedback a jeho následok.
9. Ako môže observability podporiť Second Way?
10. Ako postmortem podporuje Third Way iba vtedy, keď sa zistenia implementujú?

## 23. Zhrnutie

- First Way optimalizuje plynulý tok práce zľava doprava.
- Second Way vytvára rýchlu a kvalitnú spätnú väzbu sprava doľava.
- Third Way premieňa experimenty a zlyhania na trvalé systémové učenie.
- Lokálna vyťaženosť nie je to isté ako throughput celého systému.
- Feedback má hodnotu iba vtedy, keď je rýchly, dôveryhodný a akčný.
- Incident je príležitosť zmeniť schopnosť systému, nie iba obnoviť aktuálnu službu.
- Všetky tri princípy musia fungovať súčasne.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: CALMS framework](calms.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Systems thinking →](systems-thinking.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
