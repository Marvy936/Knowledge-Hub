# Continuous Delivery

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Continuous Delivery je schopnosť udržiavať každú akceptovanú zmenu v stave, v ktorom možno dôveryhodný immutable artifact bezpečne, opakovateľne a na požiadanie nasadiť do produkcie. Produkčný release nemusí byť automatický, ale technická cesta od source po produkčne pripraveného kandidáta je automatizovaná, pravidelne používaná a podložená evidence.

```text
integrovaná zmena
→ reprodukovateľný build
→ immutable artifact
→ vrstvené verification a validation
→ promotion evidence
→ deployable candidate
→ vedomé release rozhodnutie
```

Continuous Delivery nie je stav „pipeline existuje“. Je to prevádzková vlastnosť systému: release nie je výnimočný projekt, ale štandardná, nacvičená a auditovateľná operácia.

## 2. Continuous Integration, Delivery a Deployment

Tieto schopnosti na seba nadväzujú:

```text
Continuous Integration
→ zmeny sa často integrujú a mainline ostáva dôveryhodná

Continuous Delivery
→ každý akceptovaný artifact je možné bezpečne nasadiť na požiadanie

Continuous Deployment
→ produkčná promotion po úspešných kontrolách prebieha automaticky
```

Rozdiel medzi Delivery a Deployment nie je v kvalite buildov alebo testov. Rozdiel je v poslednom release rozhodnutí. Continuous Delivery môže mať manuálny approval, ale approval rozhoduje nad pripraveným artifactom a evidence; nesmie nahrádzať ručne vykonávané technické kroky.

## 3. Mental model: deployability ako invariant

Deployability je invariant, nie udalosť tesne pred releaseom.

Systém je deployable, keď:

- **Artifact existuje —** je immutable, identifikovaný digestom a spojený so source commitom;
- **Evidence je kompletné —** required checks prešli a nechýbajú reporty, shards ani policy výsledky;
- **Deployment automation je dôveryhodná —** je versionovaná, testovaná a bezpečne retryable;
- **Konfigurácia je pripravená —** environment-specific values a secrets majú známy source a validáciu;
- **Shared state je kompatibilný —** databáza, events, caches a clients podporujú súbeh verzií;
- **Recovery je definovaná —** rollback, roll-forward, feature disable alebo traffic shift majú jasné podmienky;
- **Observability je pripravená —** release a version identity sú viditeľné a post-deploy oracle je známy;
- **Promotion policy je splnená —** risk, approvals a environment rules sú auditovateľné.

„Build prešiel“ dokazuje iba časť deployability.

## 4. Deployment pipeline

Deployment pipeline rozširuje CI evidence až po produkčne pripravený stav:

```text
source candidate
→ build a package
→ unit/static/security checks
→ integration a contract verification
→ artifact publication
→ deployment do validačného prostredia
→ acceptance/performance/operability dôkaz
→ promotion decision
→ produkčný candidate
```

Pipeline nie je iba sekvencia prostredí. Je to reťaz rozhodovacích bodov, ktoré pridávajú nový dôkaz o tom istom artifacte.

Každý krok má definovať:

- vstupný artifact digest,
- prostredie a konfiguráciu,
- kontrolované riziko,
- oracle a success criteria,
- evidence output,
- failure a retry semantics,
- ownera a exception policy.

## 5. Build once, promote many

Základný princíp:

```text
commit C
→ build artifact digest A
→ verify A
→ deploy A do test/staging
→ promote A do produkcie
```

Rebuild pred produkciou vytvorí artifact B. Aj keď pochádza z rovnakého source commit-u, môže používať iný base image, dependency mirror, compiler, timestamp alebo network-fetched vstup. Produkcia by potom nedostala bytes, ktoré prešli predchádzajúcou validáciou.

Promotion musí presúvať identitu a dôkaz artifactu, nie iba názov verzie.

Promotion record typicky obsahuje:

- artifact digest a registry location,
- source commit a build run,
- SBOM a provenance,
- výsledky required checks,
- environment deployment history,
- approvals a policy version,
- timestamp a actor identity,
- rollback/roll-forward reference.

## 6. Artifact state machine

Artifact môže prechádzať explicitnými stavmi:

```text
built
→ verified
→ deployed-to-test
→ validated
→ approved/promotable
→ deployed-to-production
→ released
→ superseded alebo revoked
```

Stav nemá byť iba tag, ktorý možno ľubovoľne prepísať. Musí byť odvodený z evidence a policy.

Dôležité pravidlá:

- revoked artifact sa nesmie znovu promovať bez novej policy výnimky;
- chýbajúci alebo expirovaný dôkaz invaliduje promotability;
- zmena artifact bytes vytvára novú identitu a nový verification lifecycle;
- promotion medzi registries musí overiť digest a podpis;
- environment deployment nesmie nepozorovane mutovať artifact.

## 7. Environment promotion

Tradičný model `dev → test → staging → production` je užitočný iba vtedy, keď má každé prostredie jasný účel.

Príklady účelu:

- **ephemeral integration environment —** wiring, reálne dependencies a contract behavior;
- **staging —** deployment topology, identity, ingress, migrations a operational acceptance;
- **performance environment —** kontrolovaný workload a capacity evidence;
- **production canary —** reálny traffic, quotas a business validation.

Viac prostredí bez rozdielneho oracle iba predlžuje lead time. Prostredie nemá byť „level“, ktorým artifact prejde z tradície. Má poskytovať konkrétnu fidelity pre konkrétny risk.

Promotion decision sa viaže na:

- artifact identity,
- úplnosť a čerstvosť evidence,
- target environment health,
- shared-state compatibility,
- release risk classification,
- policy a approvals.

## 8. Environment parity a fidelity

Staging nemusí mať rovnakú kapacitu ako produkcia, ale musí zachovať vlastnosti relevantné pre testovaný risk.

Kontroluj najmä:

- rovnaký deployment mechanism,
- rovnaký artifact format,
- kompatibilné database/broker versions,
- podobnú identity a authorization cestu,
- TLS, proxy a routing vrstvy,
- platform mutations a admission policies,
- feature-flag defaults,
- realistickú data shape a topology.

Parity nie je cieľ sama osebe. Cieľom je vedieť, ktoré assumptions staging dokazuje a ktoré ostávajú až pre produkčný rollout.

## 9. Configuration separation

Artifact má byť environment-agnostic tam, kde je to praktické. Rozdiely patria do external configuration:

- deployment manifests,
- environment variables,
- configuration service,
- secret manager,
- feature flags,
- runtime policy.

Configuration je však tiež release input. Musí mať:

- source a version,
- schema a policy validation,
- environment scope,
- ownership,
- audit zmien,
- rollback alebo previous-known-good state,
- bezpečné secret references.

„Rovnaký artifact“ nestačí, ak produkcia používa neauditovanú konfiguráciu odlišnú od stagingu.

## 10. Infrastructure a environment provisioning

Continuous Delivery potrebuje reprodukovateľné a obnoviteľné prostredia.

Mechanizmy:

- Infrastructure as Code,
- declarative platform configuration,
- immutable images,
- policy as code,
- ephemeral environments,
- drift detection,
- environment reconciliation.

Ručne udržiavaný staging s neznámou históriou je slabý validačný bod. Ak deployment uspeje iba preto, že niekto manuálne opravil server, pipeline nepreukázala deployability.

Environment provisioning lifecycle:

```text
declarative source
→ validate a plan
→ provision/reconcile
→ runtime verification
→ deploy artifact
→ cleanup alebo drift monitoring
```

## 11. Deployment automation ako stavový stroj

Deployment nie je jeden príkaz. Je to stavový prechod s partial-failure rizikom.

Príklad:

```text
planned
→ artifact verified
→ prechecks
→ change applied
→ rollout waiting
→ post-deploy validation
→ completed / paused / failed
→ rollback alebo roll-forward
```

Spoľahlivá automation je:

- idempotentná alebo bezpečne retryable,
- schopná zistiť aktuálny stav,
- tolerantná k partial completion,
- časovo ohraničená,
- pozorovateľná,
- auditovateľná,
- schopná zastaviť sa bez ďalšieho poškodenia,
- schopná overiť postconditions.

Retry nesmie slepo zopakovať nevratnú mutation. Pred opakovaním musí automation rozlíšiť „operácia neprebehla“ od „prebehla, ale response sa stratila“.

## 12. Approvals ako risk decision

Approval má byť vedomé rozhodnutie nad evidence, nie manuálne spúšťanie skriptov.

Schvaľovateľ potrebuje vidieť:

- presný artifact digest,
- source diff alebo release content,
- výsledky gates a ich čerstvosť,
- risk classification,
- database/IAM/network changes,
- target environment a rollout strategy,
- rollback/roll-forward plán,
- aktuálny SLO/error-budget stav,
- ownera a deployment window.

Approval bez kontextu je checkbox. Approval po vykonaní ručných technických krokov je oneskorená a slabo reprodukovateľná kontrola.

## 13. Separation of duties

Separation of duties oddeľuje právomoc vytvoriť zmenu od právomoci schváliť alebo vykonať citlivú promotion.

Nemusí znamenať manuálne kopírovanie artifactov. Môže byť implementovaná cez:

- protected environments,
- role-based approvals,
- samostatnú deployment identity,
- signed artifacts a provenance,
- policy as code,
- immutable audit log,
- break-glass workflow,
- environment-scoped credentials.

Deployment job má dostať iba práva potrebné pre konkrétny environment a časovo obmedzenú operáciu.

## 14. Deployment verzus release

- **Deployment —** technické umiestnenie artifactu do prostredia.
- **Release —** sprístupnenie behavioru používateľom alebo business procesu.

Oddelenie umožňujú:

- feature flags,
- dark launch,
- tenant/ring allowlists,
- canary traffic,
- configuration activation,
- API version routing.

Výhoda: deployment možno overiť pred širokou expozíciou. Riziko: feature flags a skryté paths vytvárajú ďalší state space a potrebujú lifecycle, telemetry a cleanup.

## 15. Databázová a shared-state kompatibilita

Continuous Delivery je limitovaná stavom, ktorý zdieľajú viaceré verzie.

Počas rolling alebo canary deploymentu môžu súčasne existovať:

- stará a nová application verzia,
- starí a noví consumers,
- nové schema s ešte nemigrovanými dátami,
- staré events v queue,
- caches so starým serialization formátom.

Preferuj expand-contract:

```text
1. pridať backward-compatible schema alebo field
2. nasadiť readers/writers tolerantné k obom modelom
3. vykonať backfill alebo dual-write podľa potreby
4. overiť adopciu a data integrity
5. odstrániť starý kontrakt v samostatnej neskoršej zmene
```

Destruktívna migrácia spojená s prvým deploymentom znižuje rollback aj rollout safety.

## 16. Rollback, roll-forward a feature disable

Rollback nie je univerzálne bezpečný. Môže zlyhať po:

- nevratnej schema migrácii,
- event publication,
- external financial side effecte,
- cache alebo serialization zmene,
- data backfille,
- credential alebo IAM rotácii.

Recovery policy má vybrať medzi:

- rollbackom artifactu,
- roll-forward hotfixom,
- vypnutím feature flagu,
- traffic shiftom,
- write freeze alebo read-only režimom,
- data reconciliation alebo restore.

Každá cesta potrebuje preconditions a post-recovery validation.

## 17. Post-deploy verification a validation

Orchestrator success neznamená zdravú službu.

Po deploymente over:

- správny artifact digest a config version,
- readiness, routing a capacity,
- kritický synthetic/smoke journey,
- error rate, latency a saturation,
- dependency behavior,
- migration a reconciliation stav,
- business completion alebo invariant,
- log/trace anomalies.

Výsledky:

- **success —** postconditions sú splnené;
- **pause/inconclusive —** chýba dostatok dát alebo telemetry;
- **failed —** guardrail je porušený;
- **tool/observability failure —** validation sa nedala vykonať a nesmie byť pass.

## 18. Release cadence

Continuous Delivery nevyžaduje release každého commitu. Umožňuje release vtedy, keď je potrebný, bez dlhej stabilizačnej fázy.

Cadence môže byť:

- on demand,
- denne alebo viackrát denne,
- release train,
- regulované okno,
- koordinovaný multi-product release.

Dôležité je, že čakanie je business alebo policy rozhodnutie, nie technická neschopnosť pripraviť artifact.

Dlhé čakanie môže starnúť evidence a zvyšovať divergence konfigurácie alebo dependencies. Promotion policy preto môže vyžadovať revalidation.

## 19. Pipeline as Code a template trust

Deployment pipeline musí byť versionovaná, reviewovaná a testovateľná.

Riziká:

- privilegovaný pipeline code z nedôveryhodného PR,
- nepinované external actions alebo images,
- reusable template zmena ovplyvňujúca veľa repositories,
- copy-paste drift,
- skrytá zmena environment permissions,
- nekompatibilná template verzia.

Reusable templates potrebujú semantic versioning, changelog, compatibility policy a kontrolovaný rollout.

## 20. Failure taxonomy

Promotion môže zlyhať z rôznych príčin:

- artifact alebo evidence failure,
- environment provisioning failure,
- deployment mutation failure,
- rollout timeout,
- post-deploy validation failure,
- approval timeout alebo policy denial,
- observability/tool failure,
- cleanup alebo rollback failure.

Každá trieda potrebuje inú reakciu. Opakovať deployment pri policy denial alebo data corruption nie je rovnaké ako retry pri krátkom registry timeout-e.

## 21. Metriky Continuous Delivery

Sleduj schopnosť byť bezpečne deployable:

- percent času, keď mainline má promotable artifact,
- lead time od commit-u po deployable candidate,
- evidence a approval wait time,
- deployment preparation time,
- počet manuálnych technických krokov,
- environment provisioning a drift failure rate,
- promotion failure rate podľa triedy,
- post-deploy validation failure rate,
- rollback/roll-forward time a úspešnosť,
- change fail rate,
- deployment frequency,
- stale candidate a revalidation rate.

Vyššia deployment frequency bez nižšieho risku a rýchlej recovery nie je sama osebe úspech.

## 22. Diagnostický postup

Pri neúspešnej promotion:

1. identifikuj artifact digest, source commit a policy version;
2. over úplnosť a čerstvosť evidence;
3. rozlíš artifact, environment, deployment, validation a tool failure;
4. porovnaj target config a secrets references s očakávaným stavom;
5. skontroluj shared-state compatibility a migration phase;
6. zachovaj rollout events, logs, manifests a trace IDs;
7. rozhodni medzi retry, pause, rollback, roll-forward a feature disable;
8. over cleanup a environment health;
9. vykonaj post-recovery smoke a data-integrity kontrolu;
10. pridaj skoršiu kontrolu alebo policy, ktorá failure nabudúce zachytí.

## 23. Typické anti-patterny

### Rebuild pred produkciou

Produkčný artifact nie je ten, ktorý prešiel validáciou.

### Prostredia ako rituálne levely

Každé pridáva čas, ale nie nový risk-specific dôkaz.

### Manuálny deploy runbook ako hlavný proces

Operácia je variabilná, pomalá a slabo auditovateľná.

### Approval bez evidence

Schvaľovateľ nevie, čo presne schvaľuje ani aké riziko ostáva.

### Staging ako ručne udržiavaný pet

Environment drift znižuje dôveryhodnosť výsledku.

### Rollback ako automatická odpoveď

Shared-state alebo external side effects môžu návrat starej verzie zhoršiť.

### Rovnaký artifact, neauditovaná konfigurácia

Produkčný behavior sa môže zásadne líšiť napriek identickým bytes.

### Dlhá code freeze stabilizácia

Skrýva nedostatok častej integrácie, automation a deployability.

## 24. Praktický rozhodovací rámec

1. Čo presne znamená deployable state pre tento systém?
2. Je artifact immutable a jednoznačne identifikovaný?
3. Promujeme rovnaké bytes alebo rebuildujeme?
4. Aké riziko a oracle má každý environment?
5. Je konfigurácia versionovaná a auditovateľná?
6. Je deployment idempotentný a partial-failure aware?
7. Aké evidence potrebuje approval?
8. Ako je implementovaná separation of duties?
9. Sú databáza, events a caches kompatibilné so súbehom verzií?
10. Ktorá recovery cesta je bezpečná pre konkrétnu zmenu?
11. Čo overuje post-deploy validation?
12. Kedy evidence expiruje a vyžaduje revalidation?

## 25. Kontrolný checklist

- mainline produkuje immutable artifact;
- artifact digest sa nemení medzi prostrediami;
- provenance a required evidence sú dostupné;
- každé prostredie má explicitný validačný účel;
- config a secrets references sú versionované a scoped;
- provisioning je deklaratívny a drift je viditeľný;
- deployment workflow rozlišuje partial failure;
- approvals zobrazujú risk a recovery kontext;
- deployment identity má least privilege;
- database a event changes používajú compatibility lifecycle;
- rollback/roll-forward/flag-off sú otestované;
- post-deploy verification a validation majú failure policy;
- tool alebo telemetry failure nie sú pass;
- promotion a release audit trail je úplný.

## 26. Kontrolné otázky

1. Čo znamená Continuous Delivery ako schopnosť?
2. Aký je rozdiel medzi Delivery a Deployment?
3. Prečo je deployability invariant?
4. Čo znamená build once, promote many?
5. Aké stavy môže mať artifact?
6. Prečo prostredie potrebuje explicitný risk-specific účel?
7. Ako configuration ovplyvňuje dôveryhodnosť rovnakého artifactu?
8. Prečo deployment automation potrebuje stavový model?
9. Čo má obsahovať kvalitný approval?
10. Ako sa separation of duties implementuje bez manuálneho kopírovania?
11. Prečo deployment a release nie sú to isté?
12. Ako expand-contract podporuje deployability?
13. Kedy rollback nemusí byť bezpečný?
14. Aké výsledky má rozlišovať post-deploy validation?
15. Ktoré metriky ukazujú, že systém je skutočne continuously deliverable?

## Summary

Continuous Delivery udržiava zmeny v trvalo deployable stave. Dôveryhodný proces buildne artifact raz, promuje rovnaký digest, vrství evidence podľa konkrétnych rizík, oddeľuje konfiguráciu a release od deploymentu a používa versionovanú automation s explicitnými partial-failure a recovery semantics. Manuálny approval môže zostať, ale rozhoduje nad pripraveným artifactom a auditovateľným dôkazom; nemá nahrádzať automatizovaný deployment proces.

## Glossary impact

Relevantné pojmy: Continuous Delivery, deployable state, deployment pipeline, artifact promotion, artifact state machine, environment promotion, configuration provenance, protected environment, separation of duties, release decision, expand-contract, post-deploy validation a promotable artifact.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Continuous Integration](continuous-integration.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Continuous Deployment →](continuous-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->