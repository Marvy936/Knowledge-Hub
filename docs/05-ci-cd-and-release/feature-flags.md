# Feature flags

Feature flag oddeľuje deployment kódu od release capability. Runtime rozhodnutie určuje, kto alebo čo používa konkrétnu vetvu správania bez potreby nového buildu alebo deploymentu.

## 1. Základný model

```text
deploy code with old and new path
→ evaluate flag for request/context
→ execute selected behavior
→ observe outcome
→ expand or reduce exposure
→ remove obsolete path and flag
```

Flag je dočasný control-plane mechanizmus. Nie je náhradou za version control, konfiguráciu bez lifecycle ani trvalý permission systém.

## 2. Typy feature flags

### Release flag

Dočasne skrýva nedokončenú alebo ešte neuvoľnenú capability.

### Experiment flag

Rozdeľuje používateľov do control/treatment variantov a musí zachovať experimentálnu konzistenciu.

### Operational flag

Umožňuje vypnúť drahú alebo rizikovú runtime funkciu počas incidentu.

### Permission alebo entitlement flag

Riadi dostupnosť podľa plánu, role alebo zmluvy. Ide skôr o dlhodobý business control než dočasný release flag.

### Migration flag

Riadi prechod medzi implementáciami, dátovými cestami alebo dependencies.

Každý typ potrebuje iný ownership, expiry a audit model.

## 3. Flag evaluation

Evaluation môže používať:

- boolean value,
- percent rollout,
- stable subject ID,
- tenant,
- region,
- application version,
- device capability,
- environment,
- custom attributes.

Rozhodnutie musí byť deterministické pre workflow, kde zmena variantu počas session vytvára nekonzistenciu.

## 4. Server-side vs. client-side

### Server-side

Flag sa vyhodnocuje na serveri. Lepšie chráni pravidlá a secrets, ale pridáva dependency na flag service alebo lokálnu cache.

### Client-side

Klient dostane flag configuration alebo výsledok. Vhodné pre UI behavior, ale pravidlá a neaktívny kód môžu byť viditeľné. Client-side flag nikdy nesmie byť jedinou authorization kontrolou.

## 5. Control plane a data plane

Flag platforma typicky obsahuje:

- authoring API/UI,
- policy a approvals,
- versionovaný flag state,
- distribution stream,
- SDK alebo evaluation engine,
- local cache,
- audit log,
- telemetry.

Data plane musí mať definované správanie pri nedostupnosti control plane.

## 6. Default a failure behavior

Pre každý flag definuj:

- code default,
- remote default,
- behavior pri timeout-e,
- behavior pri stale cache,
- fail-open/fail-closed rozhodnutie,
- maximum staleness,
- startup behavior.

Kritický kill switch nesmie závisieť od jedinej nedostupnej služby bez lokálnej fallback policy.

## 7. Stable percentage rollout

Použi stabilný hashing:

```text
bucket = hash(flag_key + subject_id + salt) mod 10000
```

Požiadavky:

- rozšírenie z 5 % na 20 % zachová pôvodných 5 %, ak je to žiaduce,
- rovnaký subject má rovnaký výsledok naprieč instances,
- salt/version zmeny sú kontrolované,
- anonymous identity má explicitný lifecycle.

## 8. Flag dependencies

Flagy môžu mať závislosti:

```text
new-checkout-ui requires new-checkout-api
```

Skryté kombinácie spôsobujú neotestovaný stavový priestor. Preferuj:

- minimálny počet závislostí,
- explicitné prerequisites,
- validáciu neplatných kombinácií,
- matrix testy relevantných variantov,
- spoločný release plan.

## 9. Flag debt

Každý flag zvyšuje:

- počet code paths,
- test matrix,
- observability cardinality,
- incident complexity,
- cognitive load,
- riziko stale configu.

Release flag má mať už pri vytvorení:

- ownera,
- creation date,
- expiry/removal date,
- success criteria,
- cleanup issue,
- default final state.

## 10. Cleanup lifecycle

```text
create
→ deploy both paths
→ limited exposure
→ full release
→ observe
→ make final behavior default
→ remove evaluation
→ remove old path
→ delete flag metadata
```

Samotné nastavenie na 100 % nie je dokončenie lifecycle.

## 11. Kill switch

Operational flag môže rýchlo obmedziť dopad bez rollbacku. Musí byť:

- rýchlo dostupný,
- auditovaný,
- chránený RBAC a approvals podľa rizika,
- testovaný pred incidentom,
- zdokumentovaný v runbooku,
- naviazaný na observability.

Kill switch, ktorý nikto nikdy nevyskúšal, nie je spoľahlivý recovery mechanizmus.

## 12. Security

Riziká:

- client-side bypass,
- neoprávnená zmena produkčného flagu,
- targeting podľa citlivých údajov,
- secrets v flag values,
- neauditované emergency zmeny,
- flag service supply-chain compromise.

Použi least privilege, protected environments, short-lived identity, approvals, encryption, audit log a signed/versioned configuration podľa kritickosti.

## 13. Privacy

Targeting attributes môžu byť osobné alebo citlivé. Minimalizuj:

- údaje posielané flag platforme,
- retention evaluation logs,
- persistent cross-device identifiers,
- segmenty s diskriminačným dopadom.

Experiment a targeting pravidlá musia rešpektovať privacy a compliance policy.

## 14. Testing

Testuj:

- oba hlavné code paths,
- default behavior bez flag služby,
- stale a invalid config,
- percentage boundaries,
- targeting rules,
- dependencies,
- permission boundaries,
- cleanup migration,
- kill-switch activation.

Nie je realistické testovať všetky kombinácie desiatok flagov; redukuj stavový priestor a používaj risk-based pairwise alebo targeted testing.

## 15. Observability

Telemetry potrebuje:

- flag key a version,
- evaluated variant,
- reason/rule,
- application version,
- environment,
- exposure event pre experimenty,
- zmenu flag state ako deployment marker.

Nekontrolovaná kombinácia flag labels môže spôsobiť vysokú metric cardinality. Používaj agregáciu a sampling podľa potreby.

## 16. Configuration consistency

V distribuovanom systéme sa flag update neprejaví všade naraz. Sleduj:

- propagation lag,
- SDK cache version,
- stale instances,
- ordering zmien,
- reconnect behavior,
- offline clients.

Pri nekompatibilnej zmene nemožno predpokladať okamžitý globálny switch.

## 17. Databázové a API migrácie

Flag môže riadiť:

- read-old/read-new,
- dual write,
- shadow read,
- new API client,
- migration worker,
- cleanup fázu.

Flag však nevyrieši chýbajúcu backward compatibility. Počas overlapu musia staré aj nové komponenty rozumieť shared state.

## 18. Troubleshooting

### Používateľ vidí varianty striedavo

Over stable identity, hashing salt, cache, session a evaluation na viacerých services.

### Flag zmena sa neprejavila všade

Skontroluj distribution stream, SDK version, polling interval, stale cache a offline clients.

### Incident pokračuje po vypnutí flagu

Nie všetky code paths flag vyhodnocujú, side effects už vznikli alebo je config stale. Aktivuj ďalší recovery plán.

### Po odstránení starého pathu rollback zlyhá

Starší artifact očakáva flag alebo nekompatibilný state. Cleanup musí rešpektovať rollback window.

## 19. Anti-patterny

### Feature flag ako authorization

Client alebo používateľ môže flag obísť; authorization musí byť vynútená nezávisle.

### Flag bez ownera a expiry

Mení sa na permanentný nezdokumentovaný branch.

### Secrets vo flag values

Flag platforma nie je automaticky secret manager.

### Desiatky vnorených flagov

Stavový priestor a diagnostika sa stávajú neudržateľné.

### Emergency zmeny bez audit trailu

Rýchlosť nesmie odstrániť rekonštruovateľnosť rozhodnutia.

## 20. Kontrolné otázky

1. Aké typy feature flags poznáš?
2. Aký je rozdiel medzi server-side a client-side evaluation?
3. Prečo feature flag nie je authorization mechanizmus?
4. Ako navrhnúť failure default pri nedostupnosti platformy?
5. Ako funguje stabilný percentage rollout?
6. Čo vytvára flag debt?
7. Ako vyzerá úplný cleanup lifecycle?
8. Čo musí spĺňať kill switch?
9. Ako flagy ovplyvňujú test matrix a observability?
10. Prečo flag nevyrieši nekompatibilnú databázovú zmenu?

## Glossary impact

Relevantné pojmy: feature flag, release flag, experiment flag, operational flag, kill switch, flag evaluation, targeting rule, stable bucketing, flag dependency, flag debt, flag cleanup, propagation lag a stale flag state.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Ring deployment](ring-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Progressive delivery →](progressive-delivery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
