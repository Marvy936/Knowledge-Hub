# Ring deployment

## Metadata

- Status: Learning
- Level: L2
- Domain: CI/CD and Release Engineering

## 1. Definícia

Ring deployment rozdeľuje release do stabilných, vopred definovaných production cohorts. Každý ring má vlastný risk profil, membership, support model, observation contract a promotion podmienky.

```text
ring 0 internal
→ ring 1 early adopters
→ ring 2 limited production
→ ring 3 broad production
→ ring 4 critical/regulatory population
```

Ring nie je iba percento trafficu ani názov environmentu. Je to dlhšie žijúca release boundary, ktorá umožňuje kontrolovať, kto používa ktorú verziu.

## 2. Ring verzus canary

Canary často používa dočasný traffic weight alebo malú náhodnú vzorku. Ring používa stabilnú a organizačne významnú skupinu:

- interní používatelia,
- pilotní zákazníci,
- región,
- device update channel,
- tenant tier,
- compliance segment.

V rámci jedného ring-u možno vykonať canary. Ring určuje cohort; canary určuje postupnú expozíciu v jej vnútri.

## 3. Mental model: release inventory naprieč cohortami

V jednom okamihu môže systém obsahovať viac aktívnych release stavov:

```text
ring 0 → version N
ring 1 → version N
ring 2 → version N-1
ring 3 → version N-1
```

To vytvára version skew a support matrix. Bez inventory nie je jasné, kto používa čo, ktoré contracts musia zostať kompatibilné a kam smerovať recovery.

## 4. Ring identity a membership contract

Každý ring potrebuje:

- stable ring ID,
- membership rule version,
- member inventory alebo deterministické pravidlo,
- artifact/config identity,
- entry a exit criteria,
- maximum exposure,
- support a escalation ownera,
- rollout status.

Membership zmena je produkčná policy change a musí byť auditovaná.

## 5. Návrh poradia

Poradie má zvyšovať dôkaz a rozširovať blast radius podľa rizika. Posudzuj:

- business criticality,
- workload a data distribution,
- integration complexity,
- support coverage,
- recovery schopnosť,
- regulation a residency,
- device/client downgrade možnosti,
- shared dependency topology.

Najväčší alebo najkritickejší zákazník nemá byť prvým produkčným dôkazom iba preto, že generuje veľa trafficu.

## 6. Stable membership

Membership musí byť:

- deterministický,
- konzistentný naprieč services,
- odolný proti náhodnému reshuffle,
- dostupný pre telemetry,
- versionovaný,
- privacy-safe.

Pri user-level assignment používaj stabilný subject key. Pri tenant ring-u musí celý cross-service workflow rešpektovať rovnaký ring.

## 7. Ring state machine

Pre každý ring:

```text
not eligible
→ admitted
→ artifact deployed
→ exposure enabled
→ observing
→ accepted / paused / aborted / inconclusive
→ retained alebo advanced
```

Celý release:

```text
ring 0 accepted
→ ring 1
→ ring 2
→ ...
→ final ring
→ skew reduction
→ old version retirement
```

## 8. Entry contract

Pred vstupom do ring-u over:

- predchádzajúci ring verdict,
- evidence freshness,
- immutable artifact a config,
- compatibility s ringmi na staršej verzii,
- support a on-call readiness,
- ring-specific integrations,
- capacity a quotas,
- communication,
- recovery eligibility.

## 9. Observation contract

Pre každý ring definuj:

- minimálnu vzorku,
- minimálnu a maximálnu duration,
- technické a business guardrails,
- ring-specific workflows,
- delayed outcomes,
- promotion/abort/inconclusive policy,
- approval podľa risku.

Fixná krátka duration pre všetky ringy ignoruje rare workflows a business cycles.

## 10. Ring 0 a interné používanie

Ring 0 môže obsahovať:

- development a operations tímy,
- synthetic identities,
- interné workflows,
- test tenants.

Je užitočný na rýchlu diagnostiku, ale nereprezentuje externé permissions, data scale ani používateľské správanie. Nemá byť jediným dôkazom.

## 11. Early-adopter ring

Potrebuje:

- informed opt-in alebo zmluvný model,
- support channel,
- known-issues komunikáciu,
- opt-out/recovery,
- jasný SLA,
- privacy a compliance kontrolu.

Early adopters nie sú nevedomí testeri kritickej zmeny.

## 12. Tenant rings

Počet tenantov nie je podiel trafficu. Jeden tenant môže dominovať:

- requestom,
- dátam,
- custom integrations,
- queue volume,
- support impactu.

Ring capacity a risk meraj podľa workloadu a business dopadu, nie iba countu členov.

## 13. Regionálne ringy

Zohľadni:

- data residency,
- latency a traffic pattern,
- region-specific dependencies,
- failover topology,
- support timezone,
- shared global control plane,
- shared database alebo event stream.

Regionálny ring neobmedzí blast radius, ak zmena mutuje globálny shared state.

## 14. Device a client rings

Client rollout používa channels ako:

```text
internal → beta → preview → stable → LTS
```

Rieš:

- update eligibility,
- podpis a download integrity,
- offline clients,
- auto-update cadence,
- minimum server compatibility,
- downgrade možnosti,
- version telemetry,
- support/EOL.

Server môže rollbacknúť za minúty; klient môže zostať starý mesiace.

## 15. Ring-specific configuration

Zámerné rozdiely sú možné, ale musia byť explicitné. Zachovaj:

- artifact digest,
- rendered config revision,
- flags,
- membership policy,
- environment/dependency differences,
- deployment timestamp.

Ak neskorší ring používa inú config, dôkaz z predchádzajúceho ring-u sa musí prehodnotiť.

## 16. Version skew contract

Dlhý rollout vyžaduje kompatibilitu:

- API a clients,
- event producers/consumers,
- DB schema,
- cache/session formatov,
- auth claims,
- background workers,
- feature flags.

Definuj maximálne podporovaný skew a deadline na dokončenie rollout-u. Nekonečný partial rollout je release debt.

## 17. Shared mutable state

Neskorší ring na starej verzii môže čítať state vytvorený novším ringom. Preto:

- používať expand-contract,
- udržiavať forward-tolerant consumers,
- versionovať cache keys,
- oddeliť irreversible mutations,
- merať cross-ring workflows,
- posúdiť rollback eligibility každého ring-u.

## 18. Ring promotion

Promotion je decision nad evidence, nie iba zmena membership percentage. Výsledky:

- promote next ring,
- extend observation,
- pause,
- abort current ring,
- rollback affected rings,
- roll-forward fix,
- inconclusive.

Evidence sa viaže na release/ring/config identities.

## 19. Partial rollback

Rollback jedného ring-u môže byť nebezpečný, ak:

- novšia verzia zmenila shared state,
- cross-ring workflow posiela nové events,
- clients komunikujú medzi ringmi,
- schema contract sa už posunul.

Recovery môže vyžadovať flag disable alebo fix-forward vo všetkých dotknutých ringoch.

## 20. Ring concurrency

Nepovoľ neauditované paralelné verzie toho istého release v jednom ring-u. Použi ring lock a generation state.

Viac releaseov môže byť v rôznych ringoch iba s explicitnou compatibility a inventory policy.

## 21. Support a communication

Každý ring potrebuje:

- ownera,
- support readiness,
- audience-specific release notes,
- known-issues channel,
- escalation,
- status a release identity,
- rollback/disable komunikáciu.

Support musí vedieť zistiť ring a verziu konkrétneho používateľa bez citlivého alebo neauditovaného lookupu.

## 22. Observability

Telemetry dimensions:

- ring ID,
- artifact/release version,
- membership policy version,
- deployment wave,
- config revision,
- region/tenant/client channel.

Porovnávanie ringov musí zohľadniť odlišný workload. Ring 0 nie je automaticky control pre final ring.

## 23. Delayed validation

Neskoršie ringy môžu obsahovať:

- rare operations,
- mesačné cycles,
- regulované workflows,
- high-scale data,
- offline clients.

Promotion contract musí rešpektovať ich outcome latency. Po final ring-u pokračuje support a telemetry validation.

## 24. Emergency release

Emergency môže ringy skrátiť alebo preskočiť, ale musí zachovať:

- immutable artifact,
- minimálne safety gates,
- explicitný risk acceptance,
- bounded first exposure,
- observability,
- recovery plan,
- audit trail,
- follow-up návrat k štandardnému modelu.

## 25. Ring retirement a cleanup

Po full rollout-e:

- odstráň staré membership výnimky,
- zjednoť config/flags,
- ukonči old support state,
- aktualizuj inventory,
- odstráň obsolete code paths,
- archivuj release evidence.

Ring framework môže zostať, release-specific cohort state nie.

## 26. Failure taxonomy

- membership inconsistency,
- ring-specific config drift,
- workload representativeness failure,
- compatibility/skew failure,
- support readiness failure,
- telemetry ambiguity,
- partial rollback incompatibility,
- rollout stall,
- emergency bypass debt.

## 27. Metriky stratégie

- time per ring,
- promotion/abort rate,
- ring-specific change fail rate,
- maximum version skew age,
- membership drift incidents,
- percentage population with unknown version/ring,
- partial rollout duration,
- rollback eligibility failures,
- support contacts per ring,
- final-ring escaped defects.

## 28. Typické anti-patterny

### Ring je iba environment name

Ring reprezentuje production cohort, nie dev/stage/prod.

### Každý ring dostane iný build

Nie je zachovaná artifact identity.

### Membership sa mení bez versioningu

Výsledky a incident scope sa nedajú rekonštruovať.

### Percento tenantov = percento trafficu

Ignoruje workload skew.

### Najkritickejší zákazník prvý

Blast radius rastie bez predchádzajúceho dôkazu.

### Rollout ostane mesiace v polovici

Compatibility, support a security debt rastú.

### Partial rollback bez shared-state analýzy

Staršia verzia nemusí tolerovať nový state.

## 29. Diagnostický postup

1. Over ring membership policy a konkrétny subject.
2. Zisti artifact/config identity v každom ring-u.
3. Skontroluj version skew a rollout generation.
4. Porovnaj workload a integrations medzi zdravým a chybným ringom.
5. Over telemetry dimensions a sample sufficiency.
6. Skontroluj shared state a cross-ring events.
7. Posúď partial rollback eligibility.
8. Pri rollout stall-e urč blokujúce entry/exit criteria.
9. Po recovery aktualizuj inventory a support state.
10. Uzavri release-specific cleanup.

## 30. Rozhodovací rámec

1. Aké failure risks odlišujú jednotlivé ringy?
2. Ako je membership stabilný a auditovateľný?
3. Aký workload a business impact každý ring reprezentuje?
4. Aký je maximálny podporovaný version skew?
5. Ktoré shared-state contracts musia zostať kompatibilné?
6. Aká observation duration zodpovedá ring outcomes?
7. Ako sa posudzuje promotion a inconclusive stav?
8. Je partial rollback bezpečný?
9. Ako support zistí ring a verziu?
10. Aký deadline zabráni permanentnému partial rollout-u?

## 31. Kontrolný checklist

- ring IDs a membership sú versionované,
- release inventory je úplný,
- rovnaký immutable artifact sa promuje,
- config rozdiely sú explicitné,
- entry/exit criteria sú evidence-based,
- workload reprezentatívnosť je známa,
- version skew limit existuje,
- DB/events/cache/sessions sú compatible,
- telemetry obsahuje ring/version,
- support a komunikácia sú pripravené,
- partial rollback eligibility je overená,
- rollout má deadline a cleanup.

## 32. Kontrolné otázky

1. Čo odlišuje ring deployment od canary weightu?
2. Prečo ring vyžaduje release inventory?
3. Ako membership inconsistency poškodí workflow aj evidence?
4. Prečo počet tenantov nevyjadruje blast radius?
5. Ako regionálne ringy súvisia s globálnym shared state?
6. Prečo client rings vytvárajú dlhší version skew?
7. Čo musí obsahovať promotion contract?
8. Kedy partial rollback nie je bezpečný?
9. Ako sa meria a obmedzuje rollout stall?
10. Čo treba odstrániť po full promotion?

## Summary

Ring deployment riadi release cez stabilné production cohorts s rastúcim rizikom, reprezentatívnosťou alebo kritickosťou. Vyžaduje versionované membership pravidlá, úplný release inventory, ring-specific observation contracts a jasný maximálny version skew. Najväčšou technickou výzvou je dlhšie obdobie viacerých verzií nad spoločnou databázou, eventmi, cache a clients. Promotion aj partial rollback musia byť založené na evidence a shared-state compatibility; po dokončení treba odstrániť release-specific cohort a flag debt.

## Glossary impact

Relevantné pojmy: ring deployment, deployment ring, rollout wave, ring membership, release inventory, version skew, ring entry criteria, ring exit criteria, early-adopter ring, client channel, partial rollback a rollout stall.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Shadow deployment](shadow-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Feature flags →](feature-flags.md)
<!-- KNOWLEDGE-NAVIGATION:END -->