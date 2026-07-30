# Service catalog

Service catalog je riadený model software a platform ecosystemu, ktorý spája stable entity identity, vlastníctvo, lifecycle, rozhrania, dependencies, runtime koreláciu a operational context. Nie je to iba vyhľadávacia stránka nad repositories. Ak catalog metadata riadia self-service, incident routing, tenant profile, policy alebo decommission, consumer musí rozlíšiť authoritative source, spracovanú projection a effective runtime state.

Najnebezpečnejší catalog nie je prázdny. Je to presvedčivá last-good projection so stale ownerom, tenant boundary alebo data classification, ktorú automatizácia považuje za fresh authority. Privileged consumer preto potrebuje explicitný freshness verdict a source-generation precondition, nie iba úspešný catalog lookup.

```text
real software/platform/organizational object
→ stable entity identity a authority map per field
→ source descriptor alebo provider snapshot
→ ingestion so source revision a observation time
→ schema, policy a processors
→ stitched catalog generation
→ discovery alebo automation consumption
→ Git/runtime/identity correlation
→ freshness, conflict a orphan verdict
→ lifecycle transition alebo removal
→ second source change a downstream validation
```

## 1. Catalog, registry, inventory a runtime truth

Inventory odpovedá, čo bolo objavené alebo evidované. Registry poskytuje authoritative registration a lookup pre určitý object type. Service catalog vytvára user-facing software graph pre ownership, discovery a lifecycle. Jeden backend môže plniť viac rolí, ale každé field potrebuje provenance a freshness.

Catalog môže zobrazovať repository descriptor, owner z identity systemu, on-call z incident toolu a deployment z cluster inventory. Stitching týchto údajov nevytvára jednu spoločnú freshness. Owner môže byť current, runtime relation stará päť minút a security score deň. Jedna zelená entity page nie je freshness oracle.

Git descriptor opisuje desired metadata. Cloud alebo cluster inventory pozoruje runtime objects. Catalog projection tieto sources sprístupňuje. Critical automation nesmie zameniť annotation `production` za dôkaz effective deploymentu ani last-good entity za úspešne spracovaný latest revision.

## 2. Exact entity subject

Názov `settlement-export-api` nestačí. Subject obsahuje catalog instance, `apiVersion/kind/namespace/name`, stable business/service ID, source authority a location, resolved source revision alebo provider cursor, processor/policy generation, stitched entity generation, observation time a freshness class.

```text
catalog instance atlas-prod
+ component:payments/settlement-export-api
+ service ID svc-771
+ descriptor revision 9ba771e
+ processor schema v17
+ stitched generation catalog-g119
+ observed-at/freshness
```

Owner transfer alebo tenant reclassification je metadata generation aj bez rename entity. Repository move môže zanechať starú location. Rename môže vyžadovať identity migration a relation rewrite. Catalog musí explicitne modelovať alias, migration, orphan a tombstone, inak vzniknú duplicate entities a dangling policy references.

## 3. Authority map per field

Catalog nie je automaticky authority pre všetky fields. Entity identity a repository môžu byť riadené reviewed descriptorom. Team membership identity providerom. Data classification governance registry. Runtime deployment inventory controllerom. On-call rota incident-management systemom. Catalog je projection hub a musí zachovať source coordinate.

Pre critical field sa definuje writer, source generation, validation, merge/conflict policy, stale budget a consumer eligibility. Last-write-wins medzi Git descriptorom, org providerom a manual editom nie je reconciliation.

```text
owner
→ authoritative org/team registry alebo reviewed ownership contract

tenant profile
→ tenant registry generation

data classification
→ governance authority

runtime artifact
→ deployment inventory a loaded generation
```

Automation smie použiť field iba vtedy, keď source a processor generation sú compatible, latest input bol spracovaný, freshness je v limite a conflict/error state je terminally understood.

## 4. Ingestion, processing a last-good semantics

Git location alebo entity provider dodá raw entity. Processing validuje schema, aplikuje policies a processors, emituje relations/statuses a stitchuje final entity. Processor môže resolve-nuť owner reference alebo pridať external metadata; každý extension point je trust boundary a musí byť versionovaný a testovaný.

Last-good projection je užitočná pre degraded discovery. Krátky source outage nemusí vymazať catalog page. Je však nebezpečná pre fresh automation. Entity response musí sprístupniť latest source coordinate, processing errors, displayed stitched generation a field freshness.

```text
latest source revision 9ba771e
→ processing failed na schema v16
→ visible last-good catalog-g118
→ discovery: allowed with stale warning
→ tenant provisioning decision: blocked
```

Availability UI a eligibility pre privileged action sú dva odlišné contracts. Self-service plan potrebuje compare-and-swap nad exact catalog generation a revalidation tesne pred authoritative mutation.

## 5. Entity model, relations a ownership

Catalog model má byť dostatočne malý na konzistentnú semantics a dostatočne presný pre jobs. Component reprezentuje vlastnený software unit, API contract boundary, Resource data/infrastructure dependency, System functional grouping, Domain business area a Group organizational principal. Každý Kubernetes Deployment nemusí byť samostatný Component; runtime objects môžu byť observed relations k service identity.

Relation je directional claim s type, target a provenance. `ownedBy` nie je runtime authorization, `dependsOn` nie je potvrdený traffic path a `providesApi` neznamená production availability. Blast-radius alebo decommission používa catalog graph ako hypothesis a koreluje ho s telemetry, access logs a data owners.

Owner je operational contract, nie display string. Potrebuje resolvable Group, decision scope a escalation. Org rename, merge alebo deletion má vytvoriť current relation alebo explicitný orphan-owner state. Incident routing podľa stale ownera môže predĺžiť breach aj pri funkčnom runtime.

## 6. Freshness a critical automation gate

Každý field alebo relation má freshness class podľa risku. Documentation summary môže tolerovať deň. Production tenant owner alebo data classification nemusí tolerovať unspracovaný latest descriptor vôbec.

Critical automation gate overuje:

```text
requested entity ID
→ latest source/provider generation
→ processing success pre required schema
→ stitched generation obsahujúca current critical fields
→ no unresolved conflict/orphan
→ freshness within policy
→ expected base generation CAS
→ plan alebo mutation
```

Catalog UI musí odlíšiť `Fresh`, `StaleLastGood`, `ProcessingError`, `Conflicted`, `Orphaned` a `UnknownSource`. Consumer nemá inferovať freshness z HTTP 200 alebo existence entity.

Cache a search index môžu byť ďalšou stale layer. Automation má čítať authoritative catalog API alebo versioned projection, nie full-text search document bez generation identity.

## 7. Catalog ako projection, nie privileged decision engine

Catalog môže agregovať scorecards, docs, APIs a runtime links, ale tenant, access alebo policy decisions majú zostať v appropriate authority. Catalog field môže byť input, ak provenance/freshness gate prešiel. Nemá sám vydávať broad credential len preto, že `spec.owner` obsahuje team name.

Portal a catalog status sa často stávajú ľudským source of truth. Preto musia ukázať processing error a actual operation/runtime state, nie historický template success. Catalog registration po scaffolding tasku nedokazuje usable service. Entity lifecycle `production` má mať definované consequences a evidence, nie byť free-text label.

Scorecard je derived assessment. Jeho green status potrebuje expected check inventory, check generations, not-applicable rules a source freshness. Missing check nesmie byť automaticky pass.

## 8. Lifecycle, deprecation a removal

Lifecycle taxonomy má byť spojená so supportom, change policy a retirement. `experimental`, `production`, `deprecated`, `retired` alebo `detached` musia mať owner, required controls a consumer communication.

Decommission flow používa graph, ale overuje runtime a data dependencies. Najprv sa označí intent, zastaví new consumers, identifikuje actual traffic/data, drain-ne service, revoke-ne identities/secrets, odstráni desired state a až potom tombstone-ne catalog entity. Hard delete entity pred resource cleanup odstráni navigáciu a incident evidence.

Orphaned entity môže znamenať removed source location alebo ownership gap. Potrebuje remediation/retention, nie okamžité zmazanie bez kontroly real resource graphu.

## 9. Connected incident `GITOPS-PAY-64`

Repository transfer pre `settlement-export-api` zmenil ownera, tenant boundary a data classification na `vega-regulated` a `restricted`. Descriptor revision `9ba771e` však neprešla starou processor schema generation. Catalog ponechal last-good projection:

```text
visible generation: catalog-g118
owner: orion-payments
tenant: shared-internal
classification: internal
profile: standard
latest source: 9ba771e processing error
```

LaunchPad kontroloval iba existenciu entity. Neoveril source revision, processing error ani critical-field freshness a vytvoril namespace podľa stale `standard` profilu. Incident page tiež routovala alert na starého ownera, čo predĺžilo triage o `26 minút`.

Catalog last-good behavior bol správny pre availability discovery. Root cause bol consumer, ktorý ho použil ako fresh authority bez generation/CAS gate-u. Počas následného tenant breachu bolo v foreign provider context-e dostupných `2 184` settlement records a `312` bolo exportovaných do Vega workspace.

## 10. Authoritative redesign a acceptance paths

Redesign používa stable tenant ID `tenant-vega-71`, compatible processor schema a stitched generation `catalog-g119`. LaunchPad plan pinne expected catalog generation a pred mutation revaliduje latest source processing. Critical fields nesmú pochádzať zo stale last-good entity.

Positive path spracuje owner/tenant/classification transition a všetci consumers čítajú `g119`. Degraded-discovery path zobrazí `g118` s explicitným stale/error statusom, no privileged action sa zablokuje. Recovery path po processor upgrade reprocess-ne entity a reroutuje incident. Removal path zachová tombstone a resource cleanup. Forbidden path odmietne HTTP-200 freshness, free-text owner, stale tenant profile, scorecard missing-as-pass a catalog-only runtime proof.

## 11. Troubleshooting a anti-patterny

Pri wrong ownerovi alebo tenant profile sa kontroluje canonical entity ID, source location/revision, processor/policy version, processing error, stitched generation, field provenance, cache/search generation, consumer expected base, runtime relation a downstream decision log. Prvá stale alebo conflict boundary určuje repair.

Anti-patterny sú: `catalog je authority pre všetko`, `entity exists = metadata fresh`, `last-good = latest`, `owner string = authorization`, `production label = runtime proof`, `catalog graph = complete dependency graph` a `zmaž orphan a problém zmizne`.

## Glossary impact

Relevantné pojmy: catalog entity subject, source revision, processor generation, stitched entity generation, field authority map, last-good projection, critical-field freshness gate, processing-error state, catalog CAS, orphan owner, runtime correlation a catalog acceptance verdict.

## Primárne zdroje

- [Backstage — Software Catalog](https://backstage.io/docs/features/software-catalog/)
- [Backstage — The Life of an Entity](https://backstage.io/docs/features/software-catalog/life-of-an-entity/)
- [Backstage — Creating the Catalog Graph](https://backstage.io/docs/features/software-catalog/creating-the-catalog-graph/)
- [Backstage — External integrations](https://backstage.io/docs/features/software-catalog/external-integrations/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Developer experience](developer-experience.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Guardrails →](guardrails.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
