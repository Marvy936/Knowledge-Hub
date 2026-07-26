# Continuous Delivery

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

Continuous Delivery je schopnosť udržiavať každú akceptovanú zmenu v stave, v ktorom možno konkrétny immutable artifact bezpečne, opakovateľne a na požiadanie nasadiť do produkcie. Produkčný release nemusí byť automatický, ale technická cesta od integrovanej zmeny po promotable candidate je stále pripravená, pravidelne používaná a podložená auditovateľným dôkazom.

```text
zdravý main candidate
→ jeden immutable artifact
→ risk-specific evidence v relevantných environments
→ configuration a shared-state compatibility
→ promotable artifact state
→ vedomé release rozhodnutie
→ deployment, validation a recovery
```

Continuous Delivery nie je „máme pipeline“. Je to prevádzkový invariant: release nesmie vyžadovať stabilizačný projekt, ručné skladanie bytes ani improvizované technické kroky.

## 1. Cieľ kapitoly

Nosný model kapitoly je deployability lifecycle:

```text
CI-accepted artifact
→ artifact a evidence identity
→ environment-specific risk validation
→ versioned configuration a infrastructure state
→ shared-state compatibility
→ deployment state machine
→ promotion/approval decision
→ post-deploy oracle
→ rollback, roll-forward alebo feature disable
→ deployability debt späť do automation a designu
```

Rozdiel medzi Continuous Delivery a Continuous Deployment je posledné rozhodnutie. Delivery môže ponechať manuálny approval, ale ten rozhoduje nad pripraveným artifactom a complete evidence. Nesmie nahrádzať ručné nasadenie.

## 2. Nosný scenár: Atlas Orders 3.10.0

CI vytvorilo:

```text
candidate SHA C
→ orders-api image digest A
→ payment-worker image digest B
→ migration bundle M
→ SBOM, signatures a test evidence E
```

Release 3.10.0 pridáva event field `priority`, retry policy a PostgreSQL index. Atlas musí preukázať:

- A, B a M zostanú rovnaké medzi environments;
- staging zachová deployment, identity a shared-state boundaries;
- stará aj nová verzia rozumejú schema a eventom počas rollout-u;
- config a feature flags majú známu revision;
- deployment zvládne partial completion a retry;
- existuje bezpečná recovery cesta;
- approval vidí presný artifact, risk a evidence.

Deployability nie je vlastnosť samotného image digestu. Je to vlastnosť artifactu, konfigurácie, platformy, shared stateu, automation a recovery contractu spolu.

## 3. Deployability ako invariant

Atlas candidate je deployable iba keď:

- artifacty sú immutable a jednoznačne previazané na source;
- required evidence je complete, fresh a patrí rovnakým bytes;
- deployment automation je versionovaná, testovaná a partial-failure aware;
- environment configuration má source, schema, policy a rollback identity;
- database, events a caches podporujú mixed-version interval;
- post-deploy technical, functional a business oracles sú známe;
- recovery variant má explicitné preconditions;
- promotion policy a approvals sú auditovateľné.

„Build prešiel“ preukazuje iba prvú časť tohto invariantu.

## 4. Build once, promote many

Atlas používa:

```text
commit C
→ build A/B/M
→ verify A/B/M
→ deploy tie isté digests do integration a staging
→ promote tie isté digests do production
```

Rebuild pred produkciou by vytvoril nové bytes, aj keby používal rovnaký source commit. Base image, package mirror, compiler alebo timestamp sa mohli zmeniť.

Promotion record obsahuje:

- artifact digests a registry locations;
- source/candidate SHA a build run;
- SBOM, signatures a provenance;
- evidence bundle a policy version;
- environment deployment history;
- approvals a actor identity;
- known-good recovery references.

Promotion presúva artifact identity a evidence, nie iba textový version tag.

## 5. Artifact state machine

Atlas modeluje artifact stav:

```text
built
→ verified
→ deployed-to-integration
→ integration-validated
→ deployed-to-staging
→ operationally-validated
→ promotable
→ deployed-to-production
→ released
→ superseded alebo revoked
```

Stav je odvodený z evidence a policy. Mutable tag `approved` bez väzby na digest nie je state machine.

Pravidlá:

- zmena bytes vytvára nový lifecycle;
- chýbajúci alebo expirovaný evidence ruší promotability;
- revoked artifact sa nepromuje bez explicitnej výnimky;
- kopírovanie medzi registries overuje digest a signature;
- environment nesmie artifact pri deployment-e nepozorovane mutovať.

## 6. Každé environment má risk-specific účel

Atlas environments nie sú rituálne levely:

```text
ephemeral integration
→ wiring, real PostgreSQL/broker a contract behavior

staging
→ deployment topology, ingress, IAM, migration a operational acceptance

performance environment
→ representative workload a capacity assumptions

production canary
→ real traffic mix, quotas, tenant skew a business outcome
```

Ak dve environments poskytujú rovnaký oracle a fidelity, druhé iba predlžuje lead time.

Parity znamená zachovať vlastnosti relevantné pre riziko: deployment mechanism, artifact format, DB/broker versions, identity path, TLS/routing, platform mutations a data shape. Neznamená slepo kopírovať celú produkčnú kapacitu.

## 7. Configuration a infrastructure provenance

Rovnaký artifact môže mať odlišný behavior kvôli:

- Helm values alebo manifests;
- environment variables;
- secret references;
- feature flags;
- IAM a network policy;
- platform defaults a admission mutations.

Configuration preto patrí do release identity:

```text
artifact digest
+ config revision
+ secret-reference version
+ infrastructure plan/state
+ feature-flag snapshot
→ effective deployment candidate
```

Atlas validuje schema a policy nad source aj rendered outputom, uchováva previous-known-good config a overuje effective runtime state po apply.

Ručne opravovaný staging s neznámou históriou nemôže dôveryhodne potvrdiť deployability.

## 8. Deployment ako stavový stroj

Deployment nie je jeden shell príkaz:

```text
planned
→ artifact/config verified
→ environment prechecks
→ migration phase
→ workload mutation
→ rollout observing
→ post-deploy validation
→ completed / paused / failed
→ rollback / roll-forward / feature disable
→ cleanup a recovery verification
```

Automation musí:

- poznať current a desired state;
- byť idempotentná alebo reconciliation-based;
- rozlíšiť „mutation neprebehla“ od „prebehla, response sa stratila“;
- zvládnuť partial completion;
- používať timeouty a environment locks;
- zachovať logs, events a deployment record;
- overiť postconditions.

Slepý retry nevratnej migrácie alebo traffic cutoveru môže poškodiť stav viac než pôvodný timeout.

## 9. Promotion evidence

Každý promotion gate pridáva dôkaz o rovnakom artifacte:

```text
CI evidence
+ integration contracts
+ staging deployment/identity/migration evidence
+ performance alebo security evidence podľa risku
+ target environment health
+ recovery readiness
→ promotable decision
```

Evidence musí mať:

- artifact/config identity;
- execution environment;
- test/plan/policy version;
- timestamp a freshness;
- complete report manifest;
- ownera a exception semantics.

Rerun po dlhom čakaní môže byť potrebný, ak sa zmenil target environment, policy, dependency advisory alebo evidence expiry.

## 10. Approval ako risk decision

Approval v Continuous Delivery nie je technické vykonanie deploymentu. Schvaľovateľ vidí:

- presné digests a release content;
- required evidence a jeho čerstvosť;
- database, IAM, network a config changes;
- risk classification;
- rollout a cohort strategy;
- rollback/roll-forward/flag-off preconditions;
- SLO a incident stav;
- target environment a window.

Approval bez tohto kontextu je checkbox. Separation of duties sa implementuje protected environmentom, samostatnou deployment identity, policy a audit trailom, nie manuálnym kopírovaním artifactov.

## 11. Deployment verzus release

Deployment technicky umiestni artifact do environmentu. Release sprístupní behavior používateľom alebo business procesu.

Atlas ich môže oddeliť:

```text
artifact deployed
→ feature flag off alebo 0 % traffic
→ startup, wiring a synthetics
→ internal tenant
→ broader exposure
```

Toto znižuje blast radius, ale vytvára ďalší state space. Feature flags, routing a cohorts potrebujú ownera, provenance, telemetry, failure default a cleanup deadline.

## 12. Shared-state compatibility

Počas rolling alebo canary obdobia súčasne existujú:

- stará a nová application verzia;
- starí a noví event consumers;
- nová schema s neúplným backfillom;
- staré messages v broker retention;
- cache entries so starším formatom.

Atlas používa expand-contract:

```text
1. pridať backward-compatible schema/event field
2. nasadiť tolerant readers a compatible writers
3. vykonať bounded backfill alebo reconciliation
4. overiť adopciu a integrity
5. odstrániť starý contract v samostatnom release
```

Destructive cleanup v rovnakom deployment-e ako prvé použitie nového contractu ruší bezpečný rollback.

## 13. Recovery decision

Rollback nie je univerzálne bezpečný. Atlas vyberá medzi:

- artifact rollbackom;
- roll-forward hotfixom;
- feature disable;
- traffic shiftom;
- write freeze/read-only režimom;
- reconciliation alebo restore.

Rozhodnutie zohľadňuje application, config, database, event a external-side-effect compatibility.

```text
starý artifact kompatibilný s current state
→ rollback môže byť bezpečný

schema/data/external side effect nevratný
→ roll-forward, containment alebo reconciliation
```

Každá cesta má prechecks a post-recovery oracle.

## 14. Post-deploy verification a validation

Orchestrator success znamená iba, že požadované API mutations skončili. Atlas následne overí:

- nasadené digests a config revision;
- readiness, routing a capacity;
- public synthetic order journey;
- event a worker completion;
- migration/backfill/reconciliation state;
- error rate, latency, saturation a queues;
- tenant, idempotency a audit invariants;
- business completion.

Výsledok môže byť `success`, `pause/inconclusive`, `failed` alebo `tool/observability failure`. Chýbajúca telemetry nie je pass.

## 15. Worked failure: produkcia dostala iný artifact

Atlas staging validoval image `orders-api@sha256:A`. Release script však pred produkciou znovu buildol tag `3.10.0`:

```text
staging A green
→ mutable base image sa medzi buildmi zmenil
→ production build vytvoril digest B
→ B obsahoval novšiu TLS knižnicu s odlišným defaultom
→ payment callback handshake zlyhal
→ evidence patrilo A, nie B
```

### Root cause

Pipeline promovala version label, nie immutable bytes. Rebuild sa nesprávne považoval za identickú operáciu.

### Náprava

- build once, promote same digest;
- registry policy zakáže mutable production reference;
- promotion record overí digest a signature;
- environment config je externalized;
- post-deploy verification číta effective image digest;
- každý nový digest začína nový verification lifecycle.

## 16. Worked failure: deployment timeout vytvoril unknown state

Staging deployment API timeoutoval po aplikovaní migration jobu, ale pred uložením pipeline statusu:

```text
migration batch commitnutý
→ response sa stratila
→ deployment job označený infra failure
→ automatický retry spustil batch znova
→ ne-idempotentný backfill vytvoril duplicate audit rows
```

### Root cause

Automation používala command/retry model bez current-state observation, checkpointu a reconciliation. Timeout sa interpretoval ako „nič sa nestalo“.

### Náprava

- deployment má explicitnú state machine;
- migration používa idempotency key a checkpoint;
- retry najprv pozoruje current state;
- partial completion je samostatný verdict;
- recovery overuje data integrity, nie iba job exit code;
- rovnaký failure sa testuje fault injectionom v stagingu.

## 17. Deployability metrics

Atlas sleduje schopnosť byť bezpečne nasaditeľný:

- percent času s promotable artifactom na main;
- commit-to-promotable lead time;
- evidence a approval wait;
- manual technical step count;
- environment provisioning/drift failure rate;
- promotion failure podľa triedy;
- post-deploy validation failure rate;
- stale candidate a revalidation rate;
- rollback/roll-forward time a success;
- change fail rate.

Deployment frequency bez stabilnej recovery a nízkeho dopadu nie je dostatočný úspech.

## 18. Diagnostický postup

Pri neúspešnej promotion:

1. Potvrď source, artifact digests, config a policy revision.
2. Over complete a fresh evidence bundle.
3. Urči, ktoré environment risk boundary zlyhalo.
4. Porovnaj desired config s effective runtime stateom.
5. Klasifikuj artifact, provisioning, deployment, validation, approval alebo tool failure.
6. Skontroluj mixed-version database/event/cache compatibility.
7. Zachovaj deployment events, manifests, traces a migration checkpoints.
8. Rozlíš bezpečný retry od unknown mutation outcome.
9. Vyber rollback, roll-forward, feature disable alebo containment podľa state compatibility.
10. Over post-recovery technical aj data/business invariants.
11. Pridaj skorší control, policy alebo automation fix.

## 19. Referenčné pravidlá

- Continuous Delivery je trvalá deployability, nie existencia pipeline.
- Buildni raz a promuj rovnaké immutable bytes.
- Artifact state vychádza z evidence, nie z mutable tagu.
- Každé environment musí poskytovať unikátny risk-specific oracle.
- Configuration a infrastructure revisions patria do release identity.
- Deployment je partial-failure-aware state machine.
- Approval rozhoduje nad evidence, nie nad ručnými technickými krokmi.
- Deployment a release možno oddeliť, ale exposure state potrebuje lifecycle.
- Shared state vyžaduje mixed-version compatibility.
- Rollback sa volí podľa current state, nie automaticky.
- Post-deploy validation zahŕňa business a data invariants.
- Tool alebo observability failure nie je success.

## 20. Časté omyly

### „Rovnaký version tag znamená rovnaký artifact“

Mutable tag alebo rebuild môže ukazovať na iné bytes.

### „Viac environments znamená vyššiu istotu“

Iba ak každé zachová inú relevantnú boundary a oracle.

### „Manuálny approval robí deployment bezpečným“

Approval bez presného artifactu, evidence a recovery kontextu je slabá kontrola.

### „Orchestrator hlási success“

To nepreukazuje routing, business completion ani data integrity.

### „Rollback je vždy najrýchlejšia cesta“

Current schema, events alebo external side effects môžu byť so starou verziou nekompatibilné.

### „Deployment timeout stačí retry-nuť“

Najprv treba zistiť, či mutation prebehla a aký state zostal.

## 21. Zhrnutie

Dôveryhodná Continuous Delivery pre Atlas je:

```text
CI-accepted immutable artifact
→ risk-specific environment evidence
→ versioned config/infrastructure
→ mixed-version shared-state compatibility
→ promotable state
→ evidence-based release decision
→ deployment state machine
→ post-deploy validation
→ compatible recovery
→ deployability learning späť do platformy
```

Continuous Delivery odstraňuje technickú neistotu z release rozhodnutia. Business alebo policy môže rozhodnúť kedy releasovať; systém už musí vedieť bezpečne vykonať ako.

## 22. Kontrolné otázky

1. Prečo je deployability invariant a nie pre-release udalosť?
2. Aký je rozdiel medzi Continuous Delivery a Continuous Deployment?
3. Čo znamená build once, promote many?
4. Prečo mutable tag nie je artifact state?
5. Aký risk-specific účel majú Atlas environments?
6. Prečo configuration patrí do release identity?
7. Ako deployment state machine rieši partial completion?
8. Čo má obsahovať evidence-based approval?
9. Aký je rozdiel medzi deploymentom a releaseom?
10. Ako expand-contract podporuje mixed-version obdobie?
11. Prečo production rebuild zneplatnil staging evidence?
12. Ako sa rieši timeout s unknown migration outcome?
13. Kedy zvoliť rollback, roll-forward alebo feature disable?
14. Čo musí overiť post-deploy oracle?

## Glossary impact

Relevantné pojmy: Continuous Delivery, deployability invariant, promotable artifact, build once promote many, artifact state machine, promotion evidence, environment fidelity, configuration provenance, deployment state machine, partial completion, separation of duties, release decision, expand-contract a post-deploy validation.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Continuous Integration](continuous-integration.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Continuous Deployment →](continuous-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->