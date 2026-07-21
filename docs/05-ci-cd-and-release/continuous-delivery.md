# Continuous Delivery

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Continuous Delivery je schopnosť udržiavať softvér v stave, v ktorom možno dôveryhodný artifact bezpečne a opakovateľne nasadiť do produkcie na požiadanie.

Deployment do produkcie nemusí byť automatický. Rozhodnutie o release môže zostať manuálne, ale technická cesta od source po deployable artifact a overený deployment proces je automatizovaná a pravidelne používaná.

```text
commit
→ CI
→ immutable artifact
→ automatizované validácie
→ deployable candidate
→ rozhodnutie o produkčnom release
```

## 2. Continuous Delivery vs. Continuous Deployment

### Continuous Delivery

Každá úspešná zmena je pripravená na produkčný deployment. Produkčný krok môže vyžadovať vedomé rozhodnutie alebo approval.

### Continuous Deployment

Každá zmena, ktorá prejde automatickými kontrolami, sa automaticky nasadí do produkcie.

Rozdiel je primárne v poslednom rozhodovacom kroku, nie v kvalite build a test procesu.

## 3. Deployable state

Systém je v deployable state, keď:

- existuje immutable artifact,
- artifact je jednoznačne prepojený so source commitom,
- potrebné testy a policies prešli,
- deployment automation je versionovaná,
- konfigurácia a secrets sú dostupné bezpečným spôsobom,
- databázové zmeny sú kompatibilné,
- rollback alebo roll-forward je pripravený,
- observability a post-deploy validation sú definované.

„Build prešiel“ sám osebe nestačí.

## 4. Deployment pipeline

Deployment pipeline rozširuje CI o ďalšie dôkazy a promotion:

```text
source
→ build
→ unit/static checks
→ integration/contract tests
→ package
→ security/compliance checks
→ environment deployment
→ acceptance/performance validation
→ production-ready candidate
```

Pipeline má sprístupniť stav artifactu, nie skrývať ho za manuálne neauditované kroky.

## 5. Artifact promotion

Artifact sa má medzi prostrediami promovať, nie rebuildovať.

```text
artifact digest A
→ test
→ staging
→ production
```

Promotion metadata môže obsahovať:

- artifact digest,
- source commit,
- build ID,
- test evidence,
- approvals,
- environment history,
- deployment timestamp.

## 6. Environment promotion

Tradičný model:

```text
dev → test → staging → production
```

Každé prostredie má overovať inú triedu rizika. Viac prostredí bez jasného účelu iba predlžuje lead time.

Promotion má byť založená na dôkaze:

- artifact identity,
- passing gates,
- compatibility,
- environment policy,
- release decision.

## 7. Configuration separation

Artifact má byť pokiaľ možno rovnaký vo všetkých prostrediach. Rozdiely patria do external configuration:

- environment variables,
- configuration service,
- secret manager,
- deployment manifest,
- feature flags.

Riziko nadmernej environment-specific konfigurácie je, že staging prestane reprezentovať produkciu.

## 8. Infrastructure a environment provisioning

Continuous Delivery potrebuje reprodukovateľné prostredia.

Mechanizmy:

- Infrastructure as Code,
- declarative configuration,
- immutable images,
- ephemeral environments,
- policy validation,
- environment drift detection.

Manuálne vytvorený staging s neznámou históriou je slabý validačný bod.

## 9. Deployment automation

Deployment musí byť:

- versionovaný,
- opakovateľný,
- idempotentný alebo bezpečne retryable,
- pozorovateľný,
- auditovateľný,
- schopný detegovať partial failure,
- schopný pokračovať alebo sa bezpečne zastaviť.

Script, ktorý predpokladá ideálny stav a neoveruje výsledok, nie je spoľahlivá deployment automation.

## 10. Approvals

Approval má byť rozhodnutie nad dostupným evidence, nie manuálne vykonanie technických krokov.

Dobré approval rozhranie ukazuje:

- čo sa nasadzuje,
- aké zmeny obsahuje,
- ktoré kontroly prešli,
- aký je risk classification,
- aký je rollback plan,
- aký je deployment window a owner.

Approval bez kontextu je iba checkbox.

## 11. Compliance a separation of duties

Continuous Delivery môže podporovať compliance cez:

- signed artifacts,
- immutable audit log,
- protected environments,
- role-based approvals,
- policy as code,
- evidence retention,
- least-privilege deployment identity.

Separation of duties nemusí znamenať manuálne kopírovanie artifactu. Môže byť implementované ako nezávislé schválenie automatizovanej promotion.

## 12. Release vs. deployment

Deployment je technické umiestnenie verzie do prostredia.

Release je sprístupnenie funkcionality používateľom.

Možno ich oddeliť cez:

- feature flags,
- dark launch,
- tenant allowlist,
- canary exposure,
- configuration switch.

Toto oddelenie znižuje tlak na deployment ako jediný okamih rozhodnutia.

## 13. Database delivery

Databázové zmeny musia podporovať súbežnú existenciu starej a novej aplikácie.

Preferuj expand-contract:

```text
1. pridať backward-compatible schema
2. nasadiť aplikáciu používajúcu nový model
3. migrovať dáta
4. overiť používanie
5. odstrániť starú schema až neskôr
```

Destruktívna migrácia a application deployment v jednom nevratnom kroku výrazne znižujú deployability.

## 14. Rollback a roll-forward

Rollback nemusí byť vždy bezpečný, najmä pri:

- databázových migráciách,
- external side effects,
- event schema zmenách,
- cache alebo state transformácii.

Preto pipeline potrebuje:

- rollback podmienky,
- roll-forward hotfix cestu,
- compatibility plan,
- data recovery postup,
- post-deploy validation.

## 15. Post-deploy validation

Deployment success nie je dôkaz funkčnej služby.

Po deploymente over:

- readiness a health,
- critical smoke workflow,
- error rate a latency,
- dependency behavior,
- business result,
- version identity,
- migration status.

Validation má mať časový limit a jasný failure handling.

## 16. Release cadence

Continuous Delivery nevyžaduje release každého commitu. Umožňuje však release vtedy, keď ho business potrebuje.

Release cadence môže byť:

- on demand,
- denne,
- týždenne,
- podľa release trainu,
- podľa regulovaného okna.

Dôležité je, že technická pripravenosť nie je viazaná na dlhú stabilizačnú fázu.

## 17. Trunk-based development

Continuous Delivery dobre funguje s:

- krátkodobými branches,
- častou integráciou,
- feature flags,
- backward-compatible changes,
- automatizovanými gates.

Dlhodobé release branches zvyšujú divergence a náklady na backporty.

## 18. Pipeline as Code

Pipeline definícia má byť:

- versionovaná,
- reviewovaná,
- testovateľná,
- reusable,
- prepojená s aplikačnou zmenou.

Riziká:

- privilegovaný pipeline code z nedôveryhodného PR,
- copy-paste drift,
- nepinované external actions,
- nejasná kompatibilita reusable templates.

## 19. DORA a Continuous Delivery

Continuous Delivery podporuje:

- kratší change lead time,
- vyššiu deployment frequency,
- menší batch size,
- rýchlejšiu recovery,
- nižšie riziko jednotlivého release.

Metriky však treba sledovať spolu. Vyššia frekvencia bez stability nie je úspech.

## 20. Anti-patterny

### Manuálny deploy runbook ako hlavný proces

Postup je pomalý, variabilný a slabo auditovateľný.

### Rebuild pred produkciou

Produkčný artifact nebol ten, ktorý prešiel testami.

### Staging ako ručne udržiavaný „pet“

Environment drift znižuje hodnotu validácie.

### Approval bez evidence

Schvaľovateľ nevie posúdiť riziko.

### Rollback ako univerzálna odpoveď

Stateful a databázové zmeny môžu rollback znemožniť.

### Dlhá code freeze fáza

Skrýva nedostatok automatizácie a deployability.

## 21. Metriky

Sleduj napríklad:

- percent času, keď main je deployable,
- lead time od commit-u po deployable candidate,
- deployment preparation time,
- manuálne kroky na deployment,
- approval waiting time,
- environment drift,
- promotion failure rate,
- rollback/roll-forward time,
- deployment frequency,
- change fail rate.

## 22. Kontrolné otázky

1. Čo je Continuous Delivery?
2. Aký je rozdiel oproti Continuous Deployment?
3. Čo znamená deployable state?
4. Prečo sa artifact promuje a nerebuilduje?
5. Aký je rozdiel medzi deploymentom a releaseom?
6. Ako má fungovať approval?
7. Prečo je expand-contract dôležitý?
8. Kedy rollback nemusí byť bezpečný?
9. Čo musí overiť post-deploy validation?
10. Ako Continuous Delivery súvisí s DORA metrikami?

## Glossary impact

Relevantné pojmy: Continuous Delivery, deployable state, deployment pipeline, artifact promotion, environment promotion, protected environment, separation of duties, release train a expand-contract.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Continuous Integration](continuous-integration.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Continuous Deployment →](continuous-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
