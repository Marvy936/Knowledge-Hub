# Continuous Deployment

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Continuous Deployment je delivery model, v ktorom každá zmena, ktorá prejde automatizovanými kontrolami a policy, pokračuje bez manuálneho release approvalu do produkcie.

```text
commit
→ CI
→ validation
→ production deployment
→ production verification
```

Continuous Deployment nie je synonymum pre rýchle alebo nebezpečné nasadzovanie. Vyžaduje vysokú úroveň automatizácie, observability, testovateľnosti, rollback/roll-forward pripravenosti a riadenia blast radiusu.

## 2. Vzťah k Continuous Integration a Delivery

Continuous Deployment stojí na predchádzajúcich schopnostiach:

```text
Continuous Integration
→ zmeny sa často a dôveryhodne integrujú

Continuous Delivery
→ každý úspešný artifact je pripravený na produkciu

Continuous Deployment
→ produkčná promotion je automatická
```

Bez kvalitného CI a Continuous Delivery sa automatické deploymenty iba zrýchlene menia na automatické incidenty.

## 3. Automatické rozhodnutie

Manuálny approval je nahradený policy a evidence.

Automatické rozhodnutie môže vyhodnocovať:

- blocking test results,
- security a compliance policy,
- artifact provenance,
- environment health,
- change risk classification,
- maintenance rules,
- SLO/error-budget stav,
- canary analysis.

Policy musí byť explicitná, versionovaná a auditovateľná.

## 4. Predpoklady

Praktické predpoklady:

- trunk alebo často integrovaná mainline,
- malé zmeny,
- immutable artifacts,
- stabilná pipeline,
- nízky flaky rate,
- automatizované environment provisioning,
- backward-compatible changes,
- kvalitná observability,
- post-deploy validation,
- rýchly rollback alebo roll-forward,
- jasné ownership a on-call reakcia.

Continuous Deployment nie je iba prepnutie jedného pipeline flagu.

## 5. Deployment vs. release

Automatický deployment nemusí znamenať okamžité sprístupnenie celej funkcionality všetkým používateľom.

Deployment a release možno oddeliť cez:

- feature flags,
- dark launch,
- canary,
- tenant alebo region allowlist,
- staged configuration,
- ring deployment.

Kód môže byť v produkcii, ale exposure sa riadi samostatne.

## 6. Progressive exposure

Bezpečnejší model:

```text
artifact deployed
→ internal ring
→ 1 % trafficu
→ 10 %
→ 50 %
→ 100 %
```

Každý krok má:

- minimálnu observation window,
- success criteria,
- abort criteria,
- automatickú alebo manuálnu recovery policy.

Automatický rollout bez kvalitného signálu iba oneskorene šíri chybu.

## 7. Canary analysis

Canary analysis porovnáva novú verziu s baseline alebo kontrolnou skupinou.

Signály:

- error-rate delta,
- p95/p99 latency,
- saturation,
- restart rate,
- dependency failures,
- business conversion/completion,
- log anomaly,
- support signal.

Používaj relatívne porovnanie v rovnakom čase, nie iba statický absolútny threshold.

## 8. Automatický rollback

Automatický rollback je vhodný, keď:

- failure je rýchlo detegovateľný,
- predchádzajúca verzia je kompatibilná so stavom,
- rollback operácia je overená,
- signal má nízky false-positive rate.

Nie je vhodný ako slepá univerzálna reakcia pri:

- nevratnej databázovej migrácii,
- zmene event schema,
- external side effects,
- poškodení dát,
- nejasnom alebo oneskorenom signáli.

V týchto prípadoch môže byť bezpečnejší roll-forward alebo feature disable.

## 9. Feature flags

Feature flags podporujú:

- oddelenie deploymentu a release,
- malé exposure cohorts,
- rýchle vypnutie funkcionality,
- experimenty,
- postupnú migráciu.

Potrebujú lifecycle:

- owner,
- default behavior,
- failure mode flag služby,
- removal date,
- audit zmien,
- testovanie oboch relevantných stavov.

Stale flags vytvárajú trvalú komplexitu.

## 10. Databázová kompatibilita

Continuous Deployment vyžaduje, aby viac aplikačných verzií mohlo krátkodobo fungovať so spoločným stavom.

Používaj:

- expand-contract,
- dual read/write podľa potreby,
- online migrations,
- backward-compatible event schemas,
- postupné backfill,
- explicitnú deprecation policy.

Destruktívne zmeny musia byť oddelené od prvého deploymentu novej verzie.

## 11. Queue a event-driven systémy

Pri event-driven systémoch overuj:

- starých aj nových consumers,
- schema compatibility,
- duplicate a out-of-order events,
- replay,
- poison-message behavior,
- backlog pri rollbacku,
- idempotency.

Automatický deployment consumerov bez compatibility policy môže poškodiť dlhodobo uložené messages.

## 12. Risk-based deployment policy

Nie každá zmena musí mať rovnaký rollout.

Risk classification môže zohľadniť:

- zmenený komponent,
- business criticality,
- database alebo IAM zmenu,
- blast radius,
- test coverage,
- novelty,
- incident history,
- rollback complexity.

Príklad:

```text
nízke riziko
→ automatický rýchly rollout

stredné riziko
→ dlhší canary

vysoké riziko
→ chránený environment alebo explicitné approval
```

Organizácia môže používať Continuous Deployment pre časť zmien a Continuous Delivery pre iné.

## 13. Error budgets

Error-budget stav môže ovplyvniť automatizovanú policy.

```text
budget healthy
→ štandardný rollout

budget sa rýchlo míňa
→ spomalenie, menší canary alebo freeze
```

Freeze má byť založený na používateľskom reliability signále, nie na všeobecnom strachu zo zmien.

## 14. Observability požiadavky

Automatický deployment potrebuje okamžité a dôveryhodné signály:

- version labels,
- deployment markers,
- request tracing,
- user-facing SLIs,
- technical saturation metrics,
- business KPIs,
- logs s correlation IDs,
- synthetic checks.

Bez možnosti odlíšiť starú a novú verziu nie je canary analýza spoľahlivá.

## 15. Deployment event a audit trail

Zachovaj:

- artifact digest,
- source commit,
- pipeline run,
- policy version,
- deployment identity,
- target environment,
- rollout steps,
- metrics decision,
- rollback/roll-forward event.

Audit trail má vysvetliť, prečo bola promotion povolená alebo zastavená.

## 16. Failure detection window

Niektoré failures sa prejavia okamžite, iné neskôr.

Príklady oneskorených problémov:

- memory leak,
- queue backlog,
- cache churn,
- batch job,
- certificate refresh,
- data corruption,
- business settlement.

Krátka canary window nemusí zachytiť dlhodobý failure. Potrebná je kombinácia rollout gates a kontinuálneho monitoring-u.

## 17. Deployment frequency a batch size

Continuous Deployment typicky znižuje batch size a zvyšuje deployment frequency.

Menší batch:

- znižuje blast radius,
- uľahčuje root-cause izoláciu,
- zrýchľuje feedback,
- zjednodušuje revert.

Veľa deploymentov samo osebe nie je úspech, ak rastie change fail rate alebo používateľský dopad.

## 18. Human-in-the-loop

Automatizácia neodstraňuje ľudí zo systému.

Ľudia stále:

- navrhujú policy,
- definujú thresholds,
- reagujú na nejednoznačné failures,
- rozhodujú pri vysokom riziku,
- analyzujú incidenty,
- zlepšujú pipeline.

Cieľom je odstrániť rutinné mechanické approvals, nie zodpovednosť.

## 19. Anti-patterny

### Deploy všetkého priamo na 100 %

Nie je kontrolovaný blast radius.

### Automatický rollback na každý alert

Noise môže spôsobiť deployment oscillation.

### Feature flags bez cleanupu

Komplexita rastie pri každom release.

### Rovnaká policy pre všetky zmeny

Ignoruje rozdielne riziko a recovery možnosti.

### Deployment success = release success

Chýba produkčná a business validácia.

### Automatizácia bez on-call pripravenosti

Failure sa šíri bez schopnosti rýchlej reakcie.

## 20. Metriky

Sleduj napríklad:

- deployment frequency,
- change lead time,
- change fail rate,
- failed deployment recovery time,
- canary abort rate,
- automatic rollback rate,
- false rollback rate,
- mean exposure before detection,
- rollout duration,
- stale feature flags,
- percent deploymentov s version-level telemetry.

## 21. Rozhodovací rámec

1. Je artifact dôveryhodný a immutable?
2. Sú blocking gates stabilné a nízko-noise?
3. Aký je risk classification zmeny?
4. Aký rollout strategy a blast radius použijeme?
5. Aké metrics sú promotion a abort criteria?
6. Je rollback kompatibilný so stavom?
7. Máme bezpečný roll-forward alebo feature disable?
8. Ako dlho treba pozorovať canary?
9. Kto reaguje na nejednoznačný failure?
10. Ako sa deployment evidence auditne?

## 22. Kontrolné otázky

1. Čo je Continuous Deployment?
2. Aký je jeho vzťah k CI a Continuous Delivery?
3. Prečo automatický deployment nemusí znamenať okamžitý release?
4. Ako funguje progressive exposure?
5. Čo musí obsahovať canary analysis?
6. Kedy je automatický rollback nebezpečný?
7. Prečo je databázová kompatibilita kritická?
8. Ako risk classification mení rollout policy?
9. Ako error budget ovplyvňuje deploymenty?
10. Aké metriky ukazujú kvalitu Continuous Deployment procesu?

## Glossary impact

Relevantné pojmy: Continuous Deployment, automated promotion, progressive exposure, canary analysis, automatic rollback, risk-based deployment, deployment marker, rollout window a release automation.
