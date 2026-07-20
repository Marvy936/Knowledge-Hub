# DORA Metrics

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Value Stream Mapping](value-stream-mapping.md), [Continuous Improvement](continuous-improvement.md)
- Súvisiace témy: CI/CD, deployment strategies, SRE, observability, flow metrics
- Model: aktuálny päťmetrikový model DORA

## 1. Definícia

DORA software delivery performance metrics merajú schopnosť tímu dodávať softvérové zmeny rýchlo a bezpečne. Aktuálny model používa päť metrík rozdelených na **throughput** a **instability**.

```text
Throughput
├── Change lead time
├── Deployment frequency
└── Failed deployment recovery time

Instability
├── Change fail rate
└── Deployment rework rate
```

Historicky sa bežne používal pojem „Four Keys“. DORA model sa vyvinul na päť metrík pridaním deployment rework rate a spresnením recovery metriky.

## 2. Prečo tieto metriky existujú

Samotný počet pipeline jobov, Kubernetes clusterov alebo automatizačných skriptov nehovorí, či delivery systém funguje dobre. DORA metriky sledujú výsledky toku:

- ako dlho zmena prechádza systémom,
- ako často tím dokáže nasadiť,
- ako často deployment spôsobí problém,
- ako rýchlo sa tím zotaví zo zlyhaného deploymentu,
- koľko deploymentov tvorí neplánovaný rework.

Metriky sa majú používať spolu. Jedna metrika izolovane môže viesť k nesprávnemu správaniu.

## 3. Change lead time

**Change lead time** je čas od commitu zmeny do version control po jej úspešné nasadenie do produkcie.

```text
Change lead time = production deployment time - commit time
```

Zahŕňa napríklad:

- čakanie na review,
- CI build a testy,
- čakanie vo fronte runnerov,
- approval,
- packaging,
- deployment,
- prípadné rework cykly pred úspešným nasadením.

### Čo odhaľuje

Dlhý lead time môže znamenať:

- veľké batch sizes,
- dlhé review queues,
- pomalé alebo flaky testy,
- manuálne approvals,
- nedostatok prostredí,
- závislosť od iného tímu,
- komplikovaný release proces.

### Pozor na definíciu začiatku

Produktový lead time od nápadu po používateľa je širšia metrika. DORA change lead time začína commitom, preto primárne meria software delivery časť value streamu.

## 4. Deployment frequency

**Deployment frequency** vyjadruje, ako často tím nasadzuje zmeny do produkcie alebo ich sprístupňuje používateľom.

Môže sa merať ako:

```text
počet deploymentov za deň / týždeň / mesiac
```

alebo ako priemerný čas medzi deploymentmi.

### Čo odhaľuje

Vyššia deployment frequency často súvisí so schopnosťou:

- pracovať v menších dávkach,
- automatizovať delivery,
- oddeliť deployment od release pomocou feature flags,
- rýchlo doručiť opravu,
- znížiť riziko jednotlivého deploymentu.

### Čo sa počíta ako deployment

Tím musí mať konzistentnú definíciu. Samostatný restart bez zmeny artifactu alebo automatický rescheduling Podu typicky nie je nový software deployment. Definícia má reprezentovať zmenu releasovanú do produkčného systému.

## 5. Failed deployment recovery time

**Failed deployment recovery time** je čas potrebný na obnovenie služby po produkčnej zmene, ktorá spôsobila degradáciu alebo výpadok a vyžaduje nápravu.

```text
Recovery time = service restored time - failed deployment impact time
```

Náprava môže byť:

- rollback,
- roll-forward,
- hotfix,
- patch,
- deaktivácia feature flagu,
- oprava konfigurácie.

### Prečo nejde o všeobecné MTTR

Táto metrika sa sústreďuje na zlyhanie spôsobené deploymentom. Výpadok elektriny, externého providera alebo fyzického zariadenia môže patriť do širšieho incident managementu, ale nemá sa automaticky miešať s výkonom software delivery procesu.

### Čo odhaľuje

Dlhý recovery time môže znamenať:

- slabú observability,
- nejasný ownership,
- chýbajúci rollback,
- veľké alebo nekompatibilné zmeny,
- pomalý emergency change proces,
- chýbajúce runbooky,
- nemožnosť reprodukovať artifact.

## 6. Change fail rate

**Change fail rate** je podiel produkčných deploymentov, ktoré spôsobia degradáciu a vyžadujú bezprostrednú nápravu.

```text
Change fail rate = failed deployments / all deployments × 100 %
```

Príklad:

```text
100 deploymentov
8 vyžadovalo rollback, hotfix alebo inú okamžitú nápravu
Change fail rate = 8 %
```

### Čo odhaľuje

Vysoká hodnota môže poukazovať na:

- slabé testy,
- veľké batch sizes,
- nekonzistentné prostredia,
- chýbajúce canary overenie,
- nebezpečné databázové migrácie,
- manuálny a neštandardný deployment,
- nedostatočné release readiness kritériá.

### Dôležitý denominator

Počet incidentov bez počtu deploymentov je zavádzajúci. Tím so štyrmi zlyhaniami pri 1 000 deploymentoch má iný profil než tím so štyrmi zlyhaniami pri ôsmich deploymentoch.

## 7. Deployment rework rate

**Deployment rework rate** je podiel deploymentov, ktoré neboli plánovanou hodnotovou zmenou, ale neplánovanou opravou používateľsky viditeľnej chyby.

```text
Deployment rework rate = unplanned corrective deployments / all deployments × 100 %
```

Táto metrika zviditeľňuje kapacitu spotrebovanú opravovaním predchádzajúcej práce.

### Rozdiel oproti change fail rate

Change fail rate sa pýta, koľko deploymentov priamo spôsobilo degradáciu vyžadujúcu nápravu.

Deployment rework rate sa pýta, koľko vykonaných deploymentov bolo neplánovanou opravnou prácou.

Jeden failed deployment môže vyvolať viac opravných deploymentov. Metriky preto zachytávajú rozdielne aspekty instability.

## 8. Throughput a instability

DORA metriky nemajú vytvárať konflikt „rýchlosť verzus stabilita“.

```text
Throughput bez stability
→ veľa rýchlo dodaných problémov

Stability bez throughputu
→ stabilita dosiahnutá tým, že sa takmer nič nemení
```

Cieľom je schopnosť vykonávať malé, bezpečné a rýchlo overiteľné zmeny s efektívnym recovery.

## 9. Scope merania

Metriky sa majú primárne vyhodnocovať pre konkrétnu aplikáciu alebo službu v konkrétnom kontexte.

Nevhodné agregácie môžu skryť realitu:

```text
Tím A: 20 deploymentov denne
Tím B: 1 deployment za štvrťrok
Priemer organizácie: číslo, ktoré neopisuje ani jeden tím
```

Porovnanie medzi veľmi odlišnými systémami bez kontextu je slabšie než sledovanie trendu jednej služby v čase.

## 10. Zber údajov

Možné zdroje:

- Git commits a merge requests,
- CI/CD pipeline events,
- deployment platforma,
- incident management systém,
- feature flag platforma,
- observability a alerting,
- change management záznamy.

Potrebné je prepojiť identitu zmeny:

```text
commit → build artifact → deployment → incident / recovery
```

Bez spoločných identifikátorov vzniká nepresná manuálna korelácia.

## 11. Príklad dátového modelu

```text
deployment_id: deploy-2026-00482
service: payments-api
commit_sha: a12bc34
artifact: payments-api:2.18.4
started_at: 10:00
completed_at: 10:08
result: failed
user_impact_at: 10:05
restored_at: 10:22
remediation: rollback
planned_change: true
```

Z takýchto udalostí možno vypočítať delivery a recovery metriky konzistentnejšie než z ručne vedených tabuliek.

## 12. Metriky a príčina

DORA metriky sú výsledkové signály. Samy nevysvetlia root cause.

```text
Dlhý change lead time
  ↓
Value Stream Mapping
  ↓
zistenie: 70 % času tvorí čakanie na review
  ↓
experiment: review rotation a WIP limit
  ↓
nové meranie
```

Na hľadanie príčin treba doplnkové diagnostické metriky:

- review waiting time,
- pipeline duration,
- flaky test rate,
- queue time,
- batch size,
- approval wait time,
- rollback success rate.

## 13. Anti-gaming pravidlá

### Nepoužívaj DORA metriky na hodnotenie jednotlivcov

Software delivery je vlastnosť socio-technického systému. Individuálny target môže motivovať k rozdeľovaniu commitov, umelým deploymentom alebo skrývaniu zlyhaní.

### Neoptimalizuj jednu metriku izolovane

Deployment frequency možno umelo zvýšiť bez zlepšenia hodnoty. Change fail rate možno znížiť tým, že tím prestane nasadzovať.

### Nemeň definíciu pri každom zhoršení

Definície a zdroje dát musia byť stabilné, inak trend nie je porovnateľný.

### Nezamieňaj benchmark za cieľ

Kontext kritickej bankovej služby a interného experimentálneho nástroja je rozdielny. Cieľom je zlepšenie vlastného systému, nie slepé kopírovanie cudzieho čísla.

## 14. Reliability nie je totožná s delivery metrikami

DORA delivery metriky merajú tok a instability zmien. Prevádzková reliability potrebuje aj:

- SLI,
- SLO,
- error budgets,
- availability,
- latency,
- correctness,
- durability podľa typu služby.

Tím môže mať dobrý deployment proces a zároveň nevhodne navrhnutú alebo poddimenzovanú službu.

## 15. Praktický lab

Pre jednu službu a obdobie posledných 30 dní zozbieraj:

1. počet produkčných deploymentov,
2. commit a deployment timestamp každej zmeny,
3. deploymenty vyžadujúce okamžitú nápravu,
4. čas obnovenia po týchto deploymentoch,
5. neplánované opravné deploymenty.

Vypočítaj päť metrík a následne vyber jednu hypotézu, ktorá môže vysvetľovať najslabší výsledok. Hypotézu over pomocou detailnejšej flow alebo quality metriky.

## 16. Kontrolné otázky

1. Ktorých päť metrík používa aktuálny DORA delivery model?
2. Prečo je failed deployment recovery time presnejší než všeobecné MTTR pre hodnotenie delivery?
3. Aký je rozdiel medzi change fail rate a deployment rework rate?
4. Prečo počet incidentov bez počtu deploymentov nestačí?
5. Prečo sa DORA metriky nemajú používať na hodnotenie jednotlivca?
6. Ako Value Stream Mapping dopĺňa change lead time?
7. Prečo dobré DORA metriky automaticky negarantujú dobré SLO?

## 17. Zhrnutie

Aktuálny DORA model používa päť metrík: change lead time, deployment frequency, failed deployment recovery time, change fail rate a deployment rework rate. Spoločne vyjadrujú throughput a instability delivery systému. Ich hodnotou nie je leaderboard, ale merateľná spätná väzba pre priebežné zlepšovanie konkrétnej služby.

## 18. Zdroje

- DORA: Software delivery performance metrics
- DORA: History of software delivery metrics
- DORA Quick Check
- DORA: Value stream mapping for software delivery