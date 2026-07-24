# Feature flags

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Feature flag je versionovaný runtime control, ktorý oddeľuje nasadenie kódu od aktivácie konkrétneho behavioru. Aplikácia obsahuje viac ciest a evaluation rozhodne, ktorú cestu daný request, používateľ, tenant alebo workload použije.

```text
code deployed
→ flag context evaluated
→ variant selected
→ behavior executed
→ exposure observed
→ state expanded/reduced
→ obsolete path and flag removed
```

Flag je produkčný control-plane mechanizmus. Nie je náhradou authorization, secret managera, version controlu ani trvalej konfigurácie bez ownershipu.

## 2. Typy flagov

- **Release flag —** dočasne oddeľuje deploy a release.
- **Experiment flag —** stabilne priraďuje control/treatment variants.
- **Operational flag —** mení prevádzkový behavior alebo slúži ako kill switch.
- **Migration flag —** riadi read/write, dependency alebo data migration fázu.
- **Entitlement flag —** dlhodobý business contract podľa plánu alebo licencie.
- **Permission-like control —** môže ovplyvniť UI alebo capability discovery, ale nesmie nahradiť server-side authorization.

Každý typ potrebuje iný lifecycle, default a approval model.

## 3. Mental model: versionovaný distribuovaný control plane

Flag platforma typicky obsahuje:

```text
authoring/control plane
→ config version
→ distribution
→ SDK/cache
→ evaluation
→ behavior/exposure
→ telemetry
```

Control plane môže byť nedostupný, distribution môže meškať a jednotlivé instances môžu krátko vyhodnocovať rozdielnu verziu. Návrh preto musí explicitne riešiť consistency a failure semantics.

## 4. Flag contract

Pre každý flag definuj:

- key a type,
- ownera,
- účel a risk,
- allowed environments,
- variants a payload schema,
- targeting inputs,
- code default,
- remote default,
- failure behavior,
- creation a expiry date,
- final intended state,
- cleanup issue,
- approval policy,
- telemetry a success criteria.

Flag bez contractu je anonymná mutable production config.

## 5. Flag identity a configuration version

Runtime rozhodnutie má byť spätne vysvetliteľné cez:

- flag key,
- flag config version/revision,
- evaluated variant,
- matched rule,
- subject/context identity,
- application version,
- environment,
- evaluation timestamp,
- cache/source age.

Samotná hodnota `true` nestačí na incidentnú rekonštrukciu.

## 6. Evaluation context

Context môže obsahovať:

- stable user/tenant/device ID,
- region,
- plan alebo entitlement,
- client/application version,
- environment,
- capability,
- request attributes.

Minimalizuj citlivé attributes. Evaluation rules nemajú potrebovať údaje, ktoré flag platforma nemusí spracúvať.

## 7. Deterministická percentage assignment

```text
bucket = hash(flag_key + flag_version + subject_id + salt) mod N
```

Požiadavky:

- konzistentný result naprieč instances,
- stabilný subject počas workflowu,
- kontrolovaný reshuffle pri zmene salt/version,
- predvídateľná expanzia percenta,
- explicitný anonymous identity lifecycle,
- auditovateľné rule precedence.

## 8. Rule precedence

Definuj poradie napríklad:

```text
emergency override
→ explicit subject/tenant rule
→ prerequisite flags
→ segment rule
→ percentage rollout
→ environment remote default
→ code default
```

Nejasná precedence vytvára odlišné výsledky medzi SDK alebo services. Resolved evaluation reason má byť dostupný v debug telemetry.

## 9. Server-side verzus client-side

### Server-side

- pravidlá a citlivý context zostávajú na serveri,
- jednoduchšie server-side enforcement,
- dependency na SDK/cache alebo service.

### Client-side

- vhodné pre UI behavior,
- config môže byť verejne viditeľná,
- offline a stale clients predlžujú propagation,
- používateľ môže local state manipulovať.

Client-side flag nikdy nie je authorization boundary. Server musí oprávnenie overiť nezávisle.

## 10. Local verzus remote evaluation

- **Local evaluation —** SDK stiahne versionovanú config a rozhoduje bez network callu per request. Rýchle, ale môže byť stale.
- **Remote evaluation —** central service vyhodnotí request. Konzistentnejšie rules, ale pridáva latency a dependency.

Hybridný model používa streaming/polling config a local evaluation. Definuj maximum staleness a startup behavior.

## 11. Failure defaults

Pre každý flag rozhodni:

- pri chýbajúcej config,
- pri timeout-e,
- pri stale cache,
- pri invalid payload,
- pri neznámom variante,
- pri startup bez snapshotu,
- pri rozdielnej SDK schema verzii.

`Fail open` a `fail closed` závisia od risku. Operational kill switch môže potrebovať lokálny bezpečný snapshot; entitlement alebo security behavior musí používať konzervatívny default.

## 12. Distribution a consistency

Sleduj:

- config publish revision,
- propagation lag,
- percent instances na latest revision,
- stale SDK caches,
- offline clients,
- out-of-order updates,
- reconnect behavior,
- invalid config rejection.

Pri incompatible flag payload schema používaj version negotiation a backward-compatible config rollout.

## 13. Atomic multi-flag changes

Viac flagov môže tvoriť jeden invariant. Samostatné postupné update-y môžu krátko vytvoriť neplatnú kombináciu.

Možnosti:

- transakčná config revision,
- release manifest s viacerými flags,
- prerequisite rules,
- application-side invariant validation,
- dvojfázový compatible transition.

## 14. Flag dependencies

```text
new-ui requires new-api
```

Závislosti musia byť explicitné a acyklické. Validuj:

- prerequisite availability,
- fallback pri mismatchi,
- test matrix relevantných combinations,
- cleanup order,
- cross-service consistency.

Hlboké dependency trees vytvárajú nečitateľný stavový priestor.

## 15. Release lifecycle

```text
create contract
→ deploy both paths with safe default
→ validate flag-off
→ limited flag-on exposure
→ expand
→ accept final behavior
→ make final code default
→ remove evaluation
→ remove obsolete path
→ delete metadata after rollback window
```

`100 % on` nie je dokončenie. Old path a evaluation zostávajú technickým dlhom.

## 16. Cleanup a rollback window

Old path neodstraňuj okamžite, ak rollback staršieho artifactu ešte očakáva flag alebo old data semantics. Cleanup musí koordinovať:

- supported artifact versions,
- database migration phase,
- client skew,
- event compatibility,
- rollback window.

Po uzavretí odstráň code branch, tests, config, dashboards a ownership metadata.

## 17. Operational kill switch

Kill switch musí byť:

- nízko-latentný,
- dostupný mimo failure domainu feature,
- least-privilege a auditovaný,
- otestovaný game dayom alebo controlled exercise,
- dokumentovaný v runbooku,
- viazaný na konkrétny failure behavior,
- schopný fungovať pri degraded control plane podľa návrhu.

Vypnutie flagu nemusí kompenzovať už vykonané side effects.

## 18. Migration flags

Použitia:

- read-old/read-new,
- shadow read,
- dual write,
- new dependency client,
- backfill worker,
- verification mode,
- contract cleanup.

Flag koordinuje fázy, ale nevytvára compatibility sám. Old/new readers a writers musia rozumieť shared state počas overlapu.

## 19. Experiment flags

Experiment flag potrebuje navyše:

- experiment version,
- stable assignment,
- exposure event,
- control/treatment payload,
- eligibility,
- metric a retention contract,
- experiment end a cleanup.

Zmena treatment payloadu bez experiment version invaliduje interpretáciu.

## 20. Entitlements a permissions

Entitlement môže byť dlhodobý a auditovaný business state. Stále však oddeľuj:

- capability discovery/UI,
- licensing/entitlement decision,
- security authorization.

Flag platforma môže informovať behavior, ale resource access musí vynútiť autoritatívny server-side policy systém.

## 21. Security

Riziká:

- neoprávnená production flag zmena,
- client manipulation,
- secrets v values,
- supply-chain compromise SDK/platformy,
- targeting podľa citlivých dát,
- neauditovaný break-glass,
- flag injection cez user-controlled attributes.

Ochrany:

- scoped RBAC,
- protected environments,
- approvals podľa risku,
- short-lived workload identity,
- signed/versioned config,
- audit a alerting,
- zákaz secrets v payloads.

## 22. Privacy a fairness

Targeting rules môžu vytvárať profilovanie alebo diskriminačný dopad. Minimalizuj attributes, definuj retention evaluation logs, rešpektuj consent/opt-out a audituj segment changes.

## 23. Testing

Testuj:

- code default bez platformy,
- remote default,
- oba hlavné paths,
- rule precedence,
- percentage boundaries,
- stale/invalid config,
- SDK version mismatch,
- dependency combinations,
- server/client consistency,
- kill switch,
- migration cleanup,
- authorization nezávisle od flagu.

Všetky kombinácie desiatok flags nie sú realistické. Znižuj počet flags a používaj risk-based pairwise/targeted tests.

## 24. Observability

Zaznamenávaj primerane:

- flag key a config version,
- variant,
- evaluation reason,
- application version,
- environment/ring,
- propagation lag,
- flag state-change marker,
- exposure event pre experiment.

Nedávaj unconstrained flag dimensions do každej metric label set; používaj logs/traces, sampling alebo curated dimensions.

## 25. Flag inventory a debt

Inventory má obsahovať:

- ownera,
- type,
- creation/expiry,
- active environments,
- rollout state,
- dependencies,
- code references,
- cleanup ticket,
- last evaluation/change.

Metriky:

- stale/expired flags,
- median flag age,
- flags without owner,
- cleanup lead time,
- evaluation/config incidents,
- kill-switch test freshness.

## 26. Change workflow

Flag change je production change. Potrebuje:

- subject/environment,
- old/new resolved state,
- risk classification,
- approval podľa policy,
- scheduled alebo emergency reason,
- expected metrics,
- rollback value,
- audit timestamp a actor.

## 27. Concurrent config changes

Súbežné edits môžu stratiť update. Použi revision compare-and-swap, transakčný publish a change diff.

Emergency override musí byť časovo obmedzený a po incidente premenený na riadny config alebo odstránený.

## 28. Failure taxonomy

- control-plane outage,
- distribution lag,
- stale cache,
- invalid config,
- SDK compatibility failure,
- inconsistent identity/assignment,
- dependency-cycle alebo invalid combination,
- unauthorized change,
- cleanup/rollback incompatibility,
- side effects pokračujúce po disable.

## 29. Diagnostický postup

1. Over application version a flag key.
2. Zisti resolved config revision na konkrétnej instance/clientovi.
3. Skontroluj context, matched rule a precedence.
4. Porovnaj expected a actual assignment.
5. Over propagation a SDK cache age.
6. Skontroluj prerequisite flags a payload schema.
7. Pri incidente potvrď, že všetky code paths flag vyhodnocujú.
8. Over, či side effects už nevznikli.
9. Posúď compatibility staršieho artifactu pred rollbackom.
10. Aktualizuj inventory a cleanup action.

## 30. Typické anti-patterny

### Feature flag ako authorization

Client alebo request môže evaluation obísť.

### Flag bez ownera a expiry

Mení sa na permanentný branch.

### Secrets vo flag payloads

Flag store nie je secret manager.

### Remote default bez code fallbacku

Startup alebo outage platformy znefunkční aplikáciu.

### Desiatky vnorených flags

Stavový priestor je neudržateľný.

### `100 % on` sa považuje za cleanup

Old path a evaluation zostávajú.

### Immediate removal pred rollback window

Starší artifact alebo client stratí očakávaný control.

### Emergency change bez expiry

Dočasný override sa stane neviditeľným defaultom.

## 31. Rozhodovací rámec

1. Aký typ flagu a lifecycle potrebujeme?
2. Aký subject/context je minimálne potrebný?
3. Aký je code a remote default?
4. Čo sa stane pri outage, stale alebo invalid config?
5. Ako je assignment stabilný?
6. Aká rule precedence platí?
7. Potrebujeme atomic multi-flag transition?
8. Aké security/privacy constraints platia?
9. Ako sa meria exposure a success?
10. Kedy sa final behavior stane code defaultom?
11. Kedy končí rollback window?
12. Ako sa vynúti cleanup?

## 32. Kontrolný checklist

- flag má type, ownera a expiry,
- key, variants a payload schema sú versionované,
- code default je bezpečný,
- outage/staleness behavior je explicitný,
- assignment a precedence sú deterministické,
- client-side flag nie je authorization,
- distribution lag je pozorovateľný,
- dependencies a invalid combinations sú validované,
- security/privacy policy je aplikovaná,
- kill switch je otestovaný,
- telemetry používa config version,
- rollback window a cleanup order sú známe,
- stale flag inventory je meraný.

## 33. Kontrolné otázky

1. Prečo je feature flag produkčný control plane?
2. Aký je rozdiel medzi release, experiment, operational a entitlement flagom?
3. Ako sa určuje effective flag result?
4. Aké failure defaults treba definovať?
5. Prečo distribution nie je okamžite konzistentná?
6. Kedy treba atomic multi-flag update?
7. Prečo flag nenahrádza authorization?
8. Ako migration flag súvisí s compatibility?
9. Prečo `100 % on` nie je koniec lifecycle?
10. Ako cleanup súvisí s rollback window a client skew?

## Summary

Feature flag oddeľuje deployment od runtime behavioru, ale zároveň vytvára distribuovaný a privilegovaný control plane. Dôveryhodný flag potrebuje versionovaný contract, deterministickú evaluation a precedence, bezpečné code/remote defaults, definované správanie pri outage a staleness, auditované changes a telemetry s config revision. Release, experiment, operational, migration a entitlement flags majú rozdielne lifecycles. Hodnota sa uzatvára až odstránením obsolete pathu a metadata po skončení compatibility a rollback window.

## Glossary impact

Relevantné pojmy: feature flag, flag contract, flag configuration revision, local evaluation, remote evaluation, targeting rule, stable bucketing, rule precedence, flag dependency, atomic flag update, operational kill switch, flag debt, stale flag, propagation lag a flag cleanup.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Ring deployment](ring-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Progressive delivery →](progressive-delivery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->