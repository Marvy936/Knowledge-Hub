# Rollback a roll-forward

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Rollback obnovuje predchádzajúci kompatibilný application, configuration, traffic alebo infrastructure state. Roll-forward vytvára a nasadzuje nový opravený stav bez návratu na predchádzajúcu verziu.

```text
failure detected
→ contain exposure
→ classify changed state
→ evaluate recovery eligibility
→ rollback / roll-forward / compensate / restore
→ validate recovery
→ close incident and improve controls
```

Recovery nie je synonymum pre redeployment. Zmena mohla zasiahnuť binaries, config, databázu, events, clients, external systems a business state.

## 2. Mental model: vrstvy mutable a immutable state

Rozlišuj:

- immutable application artifact,
- mutable runtime config a flags,
- routing/exposure state,
- infrastructure desired/effective state,
- database schema a dáta,
- queues/events,
- caches/sessions,
- external side effects,
- distributed clients.

Rollback jednej vrstvy nemusí obnoviť ostatné. Artifact rollback nie je data rollback; traffic rollback nie je compensation.

## 3. Recovery lifecycle

```text
detect
→ contain
→ preserve evidence
→ identify last compatible state
→ choose recovery path
→ execute
→ verify technical state
→ verify data/business outcome
→ monitor delayed effects
→ close
```

Containment môže byť rýchlejší než samotná oprava: zastaviť writes, znížiť traffic, vypnúť feature alebo pause-nuť consumers.

## 4. Recovery subject a current-state record

Pred rozhodnutím zisti:

- current a previous artifact digests,
- config/flag revisions,
- deployment/exposure state,
- schema a migration phase,
- events a backlog,
- clients/rings,
- side effects od začiatku release,
- active incidents/dependency state,
- last known good evidence.

Bez aktuálneho state inventory je recovery iba odhad.

## 5. Typy rollbacku

### Traffic rollback

Presunie requests na stable target alebo zníži canary exposure. Rýchly, ale nemení data state.

### Feature/config rollback

Obnoví predchádzajúcu behavior/config revision. Bezpečný iba ak kód a state podporujú oba varianty.

### Artifact rollback

Nasadí previous immutable digest. Vyžaduje runtime a state compatibility.

### Infrastructure rollback

Vráti desired infrastructure revision. Provider side effects alebo deleted state nemusia byť automaticky obnoviteľné.

### Data rollback

Backward migration, point-in-time restore alebo selective repair. Najrizikovejší pre RPO, consistency a collateral data loss.

### Client rollback

Často pomalý alebo nemožný pre distribuované mobile/desktop/firmware clients.

## 6. Last known good verzus previous

Predchádzajúci release nie je automaticky known good. Potrebuje:

- immutable identity,
- health a business evidence,
- známu security pozíciu,
- kompatibilitu s aktuálnou schema/data/config,
- dostupný artifact a dependencies,
- podporovaný operational model.

Tag `previous` je iba pointer a môže byť nejednoznačný.

## 7. Recovery package

Pre každý release priprav:

```text
current release manifest
previous compatible release manifest
config/flag snapshots
schema compatibility matrix
known irreversible changes
traffic/feature containment actions
rollback workflow
roll-forward owner/path
data restore/compensation references
validation queries and synthetics
```

Package vzniká pred rolloutom, nie až počas incidentu.

## 8. Recovery eligibility

Rollback je eligible iba ak:

- target artifact/config je dostupný,
- aktuálny state je ním čitateľný a zapisovateľný,
- external contracts a clients sú compatible,
- security risk sa návratom nezhorší neprijateľne,
- recovery operácia je otestovaná,
- očakávaný čas spĺňa incident potreby.

Eligibility sa môže meniť počas rollout-u. Nové enum values alebo writes môžu uzavrieť artifact rollback window.

## 9. Rozhodovací model

Rollback preferuj, keď:

- known compatible state je okamžite dostupný,
- mutation scope je malý alebo nulový,
- rollback je rýchlejší než bezpečný fix,
- stará verzia neobsahuje závažný security problém.

Roll-forward preferuj, keď:

- state je nevratne posunutý,
- starý code nerozumie novým dátam/events,
- external side effects už vznikli,
- fix je malý a rýchlo overiteľný,
- rollback by znovu otvoril vulnerability,
- clients už používajú nový contract.

## 10. Containment first

Možnosti:

- pause promotion,
- odstrániť canary traffic,
- vypnúť feature,
- prepnúť read-only,
- zastaviť consumers/producers,
- rate limit/load shed,
- odpojiť problematickú dependency,
- zablokovať ďalšie data mutations.

Containment znižuje rastúci damage budget a dáva čas na presnejšie rozhodnutie.

## 11. Configuration a flag recovery

Najrýchlejší zásah môže byť zmena behavioru bez artifact rollbacku. Over:

- propagation lag,
- code path coverage,
- stale clients/instances,
- config schema compatibility,
- atomic multi-setting transition,
- side effects, ktoré už vznikli.

Flag disable nemusí zrušiť queued alebo už rozbehnutú prácu.

## 12. Database a schema constraints

Old application musí tolerovať:

- nové columns/tables,
- nové enum/state values,
- nové serialization formáty,
- migration phase,
- aktuálne writer semantics.

Destruktívny contract krok alebo nekompatibilný write môže zrušiť rollback. Preto compatibility window musí byť súčasťou release planu.

## 13. Data recovery options

- forward-fix migration,
- backward migration,
- point-in-time restore,
- restore do nového targetu a cutover,
- selective repair,
- compensating transaction,
- event replay/rebuild,
- reconciliation zo source of truth.

Posudzuj:

- RPO,
- RTO,
- collateral data loss,
- consistency,
- external system divergence,
- audit/compliance,
- recovery test freshness.

## 14. Backward migration limitations

Existencia `down` scriptu neznamená bezpečnosť. Môže:

- dropnúť nové dáta,
- zlyhať na nových hodnotách,
- blokovať produkciu,
- nevrátiť semantic state,
- poškodiť events/consumers.

Forward-only schema model s compatibility a restore môže byť bezpečnejší.

## 15. External side effects a compensation

Rollback neodvolá:

- platbu,
- email/SMS,
- partner mutation,
- published event,
- issued token/certificate,
- customer decision,
- inventory reservation.

Compensating action je nová business operácia s vlastným auditom, failure modes a idempotency. Nie je to technické „undo“.

## 16. Queues a event streams

Pri recovery analyzuj:

- producers a consumers versions,
- schema compatibility,
- backlog vzniknutý novou verziou,
- poison messages,
- changed partitioning,
- acknowledgements/checkpoints,
- duplicates a replay,
- side effects po consume.

Starý consumer môže byť neeligible, ak stream už obsahuje nový contract.

## 17. Cache a sessions

Rollback môže zlyhať pre:

- nový cache serialization,
- changed key semantics,
- sessions vytvorené novou verziou,
- stale feature state,
- global invalidation.

Použi versioned namespaces, tolerant readers alebo controlled cache purge. Purge sám môže spôsobiť thundering herd.

## 18. Client-server skew

Server rollback musí podporovať clients, ktoré už poznajú nové behavior alebo schema. Rieš:

- backward-compatible endpointy,
- capability negotiation,
- minimum/maximum supported versions,
- feature disable,
- tolerant clients,
- staged release.

Client fleet sa často nedá rollbacknúť naraz.

## 19. Strategy-specific recovery

### Rolling

Rollback je ďalší batch rollout; exposure sa znižuje postupne a môže byť pomalý.

### Blue-green

Routing switch môže byť rýchly, ale old target a shared state musia zostať compatible.

### Canary

Najprv odstráň exposure; potom rozhodni o artifact/data recovery.

### Recreate

Rollback predlžuje outage a vyžaduje znovu shutdown/start sequence.

### Ring

Partial ring rollback môže zvýšiť version skew a zlyhať na shared state.

## 20. Automatic rollback

Je vhodný iba keď:

- signal je version-specific a nízko-noise,
- guardrail je významný,
- target je known compatible,
- action je bounded a otestovaná,
- existuje cooldown/hysteresis,
- missing telemetry nie je zamenená za failure alebo success,
- audit a human escalation sú dostupné.

Noisy dependency alert môže spustiť škodlivé oscillation.

## 21. Oscillation protection

Použi:

- minimum observation duration,
- consecutive threshold windows,
- hysteresis,
- cooldown,
- single active recovery lock,
- manual checkpoint po opakovanom failure,
- limit počtu automatických transitions.

## 22. Rollback window

Počas rollback window zachovaj:

- previous artifacts a config,
- schema/event compatibility,
- old target alebo provisioning capability,
- feature paths,
- support/runbook,
- validation evidence.

Po jeho skončení explicitne označ, že primárna recovery stratégia je roll-forward, compensation alebo restore.

## 23. Roll-forward workflow

```text
contain
→ identify minimal fix
→ build immutable artifact/migration
→ run risk-focused gates
→ deploy to smallest scope
→ validate
→ expand
→ repair remaining state
```

Incident urgency nezrušuje identity, review, test a audit. Zmenšuje scope na najkritickejšie kontroly.

## 24. Partial deployment a mixed state

Recovery musí vedieť pracovať s:

- časťou fleet na new,
- časťou na old,
- migration partial,
- config propagation partial,
- queued work z oboch versions.

Pred ďalším krokom vytvor actual-state inventory. Slepo opakovaný pipeline job môže situáciu zhoršiť.

## 25. Recovery validation

Po technickom zásahu over:

- version/exposure inventory,
- request success a latency,
- business completion,
- data invariants,
- backlog a event processing,
- external side effects/compensation,
- clients a integrations,
- alerts a error-budget trend.

Recovery nie je complete pri zelenom deployment jobe.

## 26. Delayed recovery verification

Sleduj neskoré následky:

- settlement/reconciliation,
- backlogs,
- cache warming,
- replication,
- batch jobs,
- user support,
- security effects.

## 27. Recovery testing

Pravidelne testuj:

- traffic/config/artifact rollback,
- feature disable,
- partial-rollout recovery,
- schema compatibility,
- restore/PITR,
- event replay,
- credentials a permissions,
- rollback pod loadom,
- old target readiness,
- compensation workflow.

Runbook bez vykonania je hypotéza.

## 28. Evidence a audit

Uchovaj:

- detection a containment timeline,
- current/target state identities,
- eligibility decision,
- commands/workflows a actor,
- data/side-effect assessment,
- recovery transitions,
- validation results,
- final incident state,
- follow-up controls.

## 29. Metriky capability

- containment time,
- recovery decision time,
- rollback/roll-forward success rate,
- failed automated rollback rate,
- oscillation incidents,
- rollback-ineligible releases,
- restore test freshness,
- recovery validation duration,
- data loss/repair scope,
- repeat incident rate.

## 30. Typické anti-patterny

### Vždy rollback

Ignoruje nekompatibilný state a side effects.

### Vždy roll-forward

Predlžuje incident pri dostupnom safe targete.

### Previous = known good

Predchádzajúca verzia môže byť nekompatibilná alebo insecure.

### Mutable rollback tag

Target bytes sú nejednoznačné.

### Artifact rollback = full recovery

Config, data, events a clients zostávajú zmenené.

### Destruktívny contract pred koncom window

Recovery možnosť zmizne priskoro.

### Automatic rollback bez hysteresis

Vzniká oscillation.

### Recovery sa netestuje

Prvý test prebieha počas incidentu.

## 31. Diagnostický postup

1. Contain-ni ďalší dopad.
2. Zachovaj evidence a current-state inventory.
3. Urči, ktoré vrstvy sa zmenili.
4. Identifikuj last compatible, nie iba previous release.
5. Posúď rollback eligibility a security.
6. Porovnaj recovery times a risks.
7. Vykonaj jednu autoritatívnu recovery state machine.
8. Over technical, data a business výsledok.
9. Sleduj delayed effects.
10. Premeň incident na test, compatibility alebo rollout zlepšenie.

## 32. Rozhodovací rámec

1. Aký user impact treba okamžite contain-nuť?
2. Ktoré immutable a mutable vrstvy sa zmenili?
3. Aký je last compatible state?
4. Aké external side effects vznikli?
5. Je rollback target bezpečný a dostupný?
6. Aký je RTO/RPO každej možnosti?
7. Je fix-forward rýchlejší a menej rizikový?
8. Potrebujeme compensation alebo restore?
9. Ako sa zabráni oscillation?
10. Aký user/business signal ukončí recovery?

## 33. Kontrolný checklist

- current a target identities sú známe,
- containment actions existujú,
- recovery package je pripravený,
- rollback eligibility zahŕňa DB/events/clients/security,
- previous artifact/config sú dostupné,
- side effects majú compensation plan,
- restore/PITR je overený,
- automatic rollback má hysteresis a lock,
- partial-state recovery je idempotentná,
- validation zahŕňa data/business outcomes,
- delayed verification pokračuje,
- audit a learning actions sa uzavrú.

## 34. Kontrolné otázky

1. Prečo recovery nie je iba redeployment?
2. Aké typy rollbacku treba odlišovať?
3. Aký je rozdiel medzi previous a last compatible state?
4. Čo tvorí rollback eligibility?
5. Prečo `down` migration nemusí byť bezpečná?
6. Ako external side effects menia recovery?
7. Prečo client skew komplikuje server rollback?
8. Kedy je automatic rollback vhodný?
9. Ako hysteresis chráni pred oscillation?
10. Aké signály dokazujú úplné recovery?

## Summary

Rollback a roll-forward sú alternatívne recovery stratégie nad viacerými vrstvami systému. Správne rozhodnutie začína containmentom a actual-state inventory, nie automatickým redeploymentom. Rollback je možný iba do posledného kompatibilného stavu; artifact availability sama nestačí, ak sa zmenili databázy, events, caches, clients alebo external side effects. Roll-forward je často bezpečnejší pri nevratnom state. Recovery sa končí až po technickej, dátovej a business validácii a monitorovaní oneskorených následkov.

## Glossary impact

Relevantné pojmy: rollback, roll-forward, containment, rollback eligibility, last compatible state, recovery package, traffic rollback, artifact rollback, data recovery, compensating action, rollback window, automatic rollback, hysteresis, recovery oscillation a recovery validation.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Progressive delivery](progressive-delivery.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Databázová kompatibilita počas deploymentu →](database-compatibility-during-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->