# You Build It, You Run It

## Metadata

- Status: Learning
- Úroveň: L2 — rozumiem mechanizmu
- Doména: DevOps Foundations
- Predpoklady: [Ownership Mindset](ownership-mindset.md), [Feedback Loops](feedback-loops.md)
- Súvisiace témy: on-call, SRE, service ownership, observability, platform engineering

## 1. Definícia

You build it, you run it je prevádzkový princíp, podľa ktorého tím, ktorý službu navrhuje a vyvíja, nesie významnú zodpovednosť aj za jej produkčné správanie, spoľahlivosť a obnovu po zlyhaní.

Cieľom nie je odstrániť všetky špecializované prevádzkové roly. Cieľom je zabrániť tomu, aby vývoj odovzdal dôsledky svojich rozhodnutí úplne oddelenému tímu.

## 2. Problém tradičného handoff modelu

```text
Development vytvorí aplikáciu
  ↓
Operations ju prevezme
  ↓
Incidenty rieši Operations
  ↓
Development dostáva oneskorenú alebo neúplnú spätnú väzbu
```

Tento model môže viesť k tomu, že:

- prevádzkovateľnosť sa rieši až po dokončení vývoja,
- logy a metriky nie sú navrhnuté podľa potrieb služby,
- vývoj nevidí cenu svojich architektonických rozhodnutí,
- Operations sa stane úzkym miestom,
- incidenty sa presúvajú cez viacero tímov.

## 3. Mentálny model

```text
Design → Build → Deploy → Operate → Learn
   ↑                                  ↓
   └────────────── feedback ──────────┘
```

Prevádzka nie je posledná fáza, ktorou zodpovednosť končí. Je zdrojom informácií pre ďalší návrh.

## 4. Čo „run it“ zahŕňa

Podľa prostredia môže zahŕňať:

- definovanie SLI a SLO,
- návrh logov, metrík a traces,
- alerting,
- on-call alebo podporu on-call,
- incident triage,
- rollback a mitigation,
- capacity planning,
- patching aplikačných závislostí,
- backup a restore požiadavky,
- postmortems,
- reliability roadmapu.

Presný rozsah musí byť explicitný. Slogan sám o sebe nevytvára funkčný operating model.

## 5. Nie je to „každý robí všetko“

Špecializované tímy zostávajú potrebné:

- platform engineering,
- cloud infrastructure,
- security,
- database engineering,
- networking,
- SRE.

Rozdiel je v rozhraní spolupráce.

```text
Platform tím vlastní platform capability.
Aplikačný tím vlastní správanie služby na platforme.
SRE môže poskytovať reliability mechanizmy a koučing.
Security definuje guardrails a pomáha riešiť riziká.
```

Aplikačný tím nemusí spravovať fyzický cluster, ale nemôže ignorovať resource requests, probes, rollout správanie alebo aplikačné SLO.

## 6. Predpoklady úspešného modelu

### Observability

Tím musí vidieť stav služby a vedieť prepojiť používateľský symptóm s technickou príčinou.

### Bezpečný deployment

Musí existovať automatizovaný rollout, rollback alebo roll-forward mechanizmus.

### Runbooky

Opakované failure modes musia mať zdokumentovanú diagnostiku a mitigáciu.

### Prístup a oprávnenia

Tím musí mať bezpečný prístup k potrebným systémom a telemetry.

### Kapacita

Roadmapa musí obsahovať reliability, security a operational work. Prevádzka nemôže byť neviditeľná práca navyše.

### Platform support

Self-service platforma znižuje množstvo infraštruktúrnych detailov, ktoré musí každý aplikačný tím riešiť samostatne.

## 7. On-call

On-call je mechanizmus dostupnosti zodpovednej osoby alebo tímu mimo bežného pracovného toku.

Zdravý on-call model potrebuje:

- akčné alerty,
- primeranú rotáciu,
- dokumentovanú eskaláciu,
- prístup k systémom,
- kompenzáciu a ochranu pracovnej kapacity,
- pravidelné vyhodnotenie opakovaných incidentov,
- limit na množstvo nočných zásahov.

On-call bez investície do reliability iba distribuuje bolesť systému medzi ľudí.

## 8. Alert ownership

Alert má smerovať na tím, ktorý:

1. rozumie signálu,
2. má právomoc reagovať,
3. má runbook alebo diagnostický kontext,
4. dokáže vykonať mitigation,
5. vie zabezpečiť dlhodobú nápravu.

Alert „CPU high“ smerovaný na vývojára bez kontextu nie je service ownership. Je to presun diagnostického toil-u.

## 9. Praktický príklad

Aplikácia pravidelne zlyháva po nasadení kvôli nekompatibilnej databázovej migrácii.

### Oddelený model

```text
Development nasadí zmenu.
Operations vidí chyby a rollbackne aplikáciu.
Database tím analyzuje locky.
Development dostane ticket na ďalší deň.
```

### You build it, you run it model

```text
Aplikačný tím definuje backward-compatible migration stratégiu.
Pipeline testuje migráciu na reprezentatívnej schéme.
Deployment používa staged rollout.
Tím sleduje error rate a databázovú latency.
Pri zhoršení vykoná pripravený rollback alebo roll-forward.
Postmortem upraví migration pattern a testy.
```

Rozdiel nie je iba v tom, kto drží pager. Rozdiel je v tom, že prevádzkové riziko ovplyvňuje návrh ešte pred deploymentom.

## 10. Shared responsibility model

V praxi môže existovať viac úrovní zodpovednosti:

| Oblasť | Aplikačný tím | Platform/SRE tím |
|---|---|---|
| Business logika | vlastní | nepokrýva |
| Aplikačné SLO | vlastní | pomáha definovať |
| Aplikačné alerty | vlastní | poskytuje platformu |
| Cluster control plane | konzument | vlastní |
| Deployment mechanizmus | používa a konfiguruje | poskytuje |
| Incident aplikácie | vedie | podporuje |
| Incident platformy | spolupracuje | vedie |

Tento model je presnejší než neurčité tvrdenie, že „všetci vlastnia všetko“.

## 11. Operational readiness

Pred produkčným spustením by služba mala mať minimálne:

- definovaný owner,
- health a readiness mechanizmy,
- dashboard,
- alerty viazané na používateľský dopad,
- rollback alebo mitigation plán,
- runbook pre kritické failure modes,
- capacity predpoklady,
- backup a restore požiadavky,
- dependency mapu,
- bezpečnostnú a lifecycle zodpovednosť.

Operational readiness review kontroluje, či je služba pripravená nielen na deployment, ale aj na zlyhanie.

## 12. Vzťah k SRE

SRE môže tento princíp implementovať viacerými modelmi:

- aplikačný tím je primárne on-call a SRE poskytuje konzultácie,
- SRE zdieľa on-call po splnení readiness kritérií,
- SRE dočasne podporuje kritickú službu a postupne odovzdáva ownership,
- platforma automatizuje spoločné reliability schopnosti.

SRE nemá byť permanentný tím, na ktorý sa odovzdá každá problematická služba bez splnenia prevádzkových požiadaviek.

## 13. Riziká nesprávnej implementácie

### Pager bez podpory

Vývojári dostanú on-call bez dashboardov, runbookov, prístupov a školenia.

### Prevádzka ako druhá práca

Tím má plnú feature roadmapu a všetka reliability práca sa očakáva navyše.

### Zrušenie špecialistov

Organizácia odstráni Ops/SRE expertízu s argumentom, že vývojári si všetko spravia sami.

### Alerting podľa infra metrík

Tím je budený pri každom technickom odchýlení bez používateľského dopadu.

### Nejasný escalation path

Aplikačný tím je formálne owner, ale pri probléme platformy nevie, koho kontaktovať.

## 14. Kedy model upraviť

Nie každé prostredie potrebuje rovnakú mieru priameho on-call ownershipu.

Faktory:

- kritickosť služby,
- veľkosť tímu,
- regulačné požiadavky,
- globálna prevádzka,
- zrelosť platformy,
- frekvencia incidentov,
- dostupnosť špecialistov.

Princíp možno zachovať aj pri centralizovanom NOC alebo Operations tíme, ak aplikačný tím stále vlastní diagnostiku, nápravu a spätnú väzbu do návrhu.

## 15. Signály zdravého modelu

- tím pozná produkčné SLI,
- alerty sú akčné a majú vlastníka,
- rollback je rýchly a nacvičený,
- incidenty menia testy a architektúru,
- reliability práca je súčasťou plánovania,
- platforma poskytuje self-service mechanizmy,
- počet manuálnych zásahov dlhodobo klesá.

## 16. Kontrolné otázky

1. Aký problém rieši princíp you build it, you run it?
2. Prečo samotné pridelenie pagera nevytvára ownership?
3. Ktoré platformové schopnosti podporujú aplikačný tím?
4. Ako sa rozdeľuje zodpovednosť pri aplikačnom a platformovom incidente?
5. Čo má obsahovať operational readiness?
6. Ako tento model skracuje feedback loop medzi návrhom a prevádzkou?

## 17. Zhrnutie

- Tím má cítiť produkčné dôsledky svojich rozhodnutí.
- Run it zahŕňa observability, incidenty, reliability a obnovu, nie iba pager.
- Špecializované platformové a SRE tímy zostávajú dôležité.
- Zodpovednosť musí byť podporená autonómiou, kapacitou a nástrojmi.
- Cieľom je uzavrieť spätnú väzbu medzi vývojom a prevádzkou.