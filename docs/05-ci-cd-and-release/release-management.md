# Release management

Release management riadi cestu od pripraveného, overeného artifactu k používateľsky alebo obchodne dostupnej zmene. Spája versioning, planning, approvals, deployment, communication, observability, recovery a lifecycle podporovaných verzií.

Release nie je synonymum pre build ani deployment.

## 1. Build, deployment a release

Rozlišuj:

```text
build
→ vytvorenie artifactu

deployment
→ umiestnenie artifactu do environmentu

release
→ sprístupnenie capability používateľom alebo business procesu
```

Feature flag umožňuje deployment bez okamžitého release. Mobilná aplikácia môže byť release-nutá cez store až po tom, ako bol backend dávno nasadený.

## 2. Release unit

Release unit je presne definovaný súbor zmien a runtime identities, napríklad:

- jeden application artifact,
- viac koordinovaných services,
- application + migrations,
- infrastructure/config bundle,
- mobile client + API compatibility window,
- environment manifest s viacerými digestmi.

Bez explicitnej release unit nie je jasné, čo sa schvaľuje, komunikuje ani rollbackuje.

## 3. Release record

Auditovateľný release record má obsahovať:

- release ID a version,
- artifact digests,
- source commits,
- configuration/infrastructure revisions,
- database migrations,
- pipeline runs,
- test a scan evidence,
- approvals alebo policy decisions,
- target environments,
- rollout strategy,
- feature-flag plan,
- ownera a on-call kontakty,
- release a rollback výsledok.

## 4. Release cadence

Možné modely:

### On-demand

Release nastane po splnení podmienok. Podporuje malé batches a rýchly feedback.

### Fixed cadence

Release windows napríklad denne, týždenne alebo mesačne. Môžu zjednodušiť koordináciu, ale veľké batchovanie zvyšuje riziko.

### Train model

Zmeny pripravené do cutoffu nastúpia na konkrétny release train; ostatné čakajú na ďalší.

### Continuous release

Malé zmeny sú release-nuté priebežne cez automatizovaný a progressive flow.

Cadence musí zodpovedať recovery capability, regulácii a organizačnému kontextu.

## 5. Release readiness

Readiness nie je checklist bez kontextu. Má byť risk-based a evidence-driven.

Typické oblasti:

- artifact identity a provenance,
- functional a non-functional tests,
- security findings,
- compatibility,
- migrations,
- observability,
- capacity,
- rollout a abort criteria,
- rollback/roll-forward,
- support readiness,
- documentation a communication.

## 6. Release candidate

Release candidate je immutable artifact považovaný za potenciálny final release.

Bezpečný model:

```text
build candidate digest
→ test candidate
→ promotion candidate
→ final release alias na ten istý digest
```

Rebuild po schválení ruší dôkaz, že final artifact prešiel kontrolami.

## 7. Release branch

Release branch môže stabilizovať konkrétnu release line:

```text
release/2.8
```

Použitie:

- final stabilization,
- backport fixes,
- dlhodobá podpora,
- oddelený release cadence.

Riziká:

- divergence od mainline,
- duplicitné fixy,
- merge/cherry-pick chyby,
- dlhé code freeze,
- nejasný source of truth.

Release branch má mať explicitný lifecycle a ownership.

## 8. Code freeze

Code freeze obmedzuje zmeny pred release. Môže znížiť change rate, ale často maskuje slabú automatizáciu a recovery.

Lepšie mechanizmy:

- malé batches,
- branch protection,
- merge queue,
- risk classification,
- progressive delivery,
- feature flags,
- robustné rollback/roll-forward.

Freeze môže byť legitímny pri regulačnej alebo kritickej udalosti, ale nemá byť permanentný operating model.

## 9. Release approvals

Approval má potvrdiť konkrétne rozhodnutie, nie mechanicky zopakovať zelený pipeline stav.

Dobrý approval pozná:

- presný artifact digest,
- zmenu od poslednej verzie,
- risk classification,
- evidence,
- rollout plan,
- recovery plan,
- platnosť rozhodnutia.

Nový commit, rebuild alebo zmena konfigurácie môže approval invalidovať.

## 10. Segregation of duties

V regulovanom prostredí môže byť potrebné oddeliť:

- autora zmeny,
- reviewerov,
- build identity,
- release approvera,
- deployment identity,
- auditora.

Automatizácia môže vynucovať separation of duties bez ručného kopírovania ticketov.

## 11. Change request a release evidence

Ticket alebo change request má odkazovať na strojovo overiteľný release record, nie ručne opisovať údaje, ktoré už existujú v pipeline.

Preferovaný model:

```text
change intent
+ risk classification
+ immutable release identity
+ generated evidence
+ decision record
```

## 12. Release notes

Release notes sú určené konkrétnemu publiku:

- používatelia,
- administrátori,
- integrátori,
- support,
- security alebo compliance.

Obsah môže zahŕňať:

- nové capabilities,
- opravy,
- breaking changes,
- deprecations,
- migration kroky,
- known issues,
- security informácie,
- rollback limitations.

Commit log bez kurácie nie je automaticky dobrý release note.

## 13. Changelog

Changelog je dlhodobý chronologický záznam významných zmien. Release notes sú komunikácia konkrétneho release.

Changelog fragmenty môžu znížiť konflikty v monorepe:

```text
changes/1842.feature.md
changes/1847.fix.md
```

Release automation ich agreguje a označí vydanou verziou.

## 14. Release manifest

Pri viacerých komponentoch manifest mapuje release na immutable identities:

```yaml
release: 2026.07.21.1
components:
  api: sha256:aaa
  worker: sha256:bbb
  frontend: sha256:ccc
config_revision: 8d2a11f
infrastructure_revision: 719ab3c
```

Manifest podporuje reprodukciu environmentu, audit aj koordinovaný rollback.

## 15. Dependency a compatibility management

Release plán musí zohľadniť:

- producer/consumer compatibility,
- API a event schemas,
- client upgrade lag,
- database schema,
- infrastructure dependencies,
- third-party services,
- minimum/maximum supported versions.

Koordinovaný „big bang“ release je často signálom nedostatočnej backward compatibility.

## 16. Database release

Databázové zmeny majú samostatný lifecycle:

```text
expand schema
→ deploy compatible application
→ migrate/backfill data
→ observe
→ remove old usage
→ contract schema
```

Release record musí uviesť applied migrations a rollback limitations.

## 17. Release window

Release window môže byť založené na:

- support coverage,
- traffic profile,
- dependency availability,
- business kalendári,
- compliance pravidlách,
- maintenance constraints.

„Nenasadzovať v piatok“ nie je univerzálne pravidlo. Rozhodujú detection a recovery capability.

## 18. Communication plan

Definuj:

- kto musí byť informovaný,
- pred akou zmenou,
- akým kanálom,
- čo je maintenance alebo degradation expectation,
- kde je live status,
- kto komunikuje rollback alebo incident.

Komunikácia má používať release ID a používateľský dopad, nie iba interný commit SHA.

## 19. Rollout plan

Release plan má explicitne uvádzať:

- target population,
- rollout kroky,
- observation windows,
- promotion criteria,
- abort criteria,
- maximum blast radius,
- feature-flag transitions,
- rollback/roll-forward postup.

## 20. Hypercare

Hypercare je dočasne zvýšená pozornosť po významnom release:

- owner dostupnosť,
- zvýšené dashboardy/alerts,
- support triage,
- business KPI sledovanie,
- rýchly decision path.

Nemá nahrádzať permanentnú observability ani on-call model.

## 21. Release rollback a roll-forward

Rollback obnovuje staršiu application verziu. Roll-forward nasadí opravu alebo dokončí migráciu.

Rozhodnutie závisí od:

- databázovej kompatibility,
- external side effects,
- queue/event state,
- cache formátu,
- client versions,
- času na opravu,
- exposure a impactu.

Release management musí recovery testovať, nie iba dokumentovať.

## 22. Supported versions

Definuj support policy:

- latest only,
- current + previous,
- LTS lines,
- security-only support,
- end-of-life dátum.

Policy ovplyvňuje backporting, test matrix, dependency updates a incident response.

## 23. Emergency release

Emergency alebo hotfix flow má byť rýchlejší, nie nekontrolovaný.

Minimálne zachovaj:

- code review podľa rizika,
- immutable artifact,
- kritické tests,
- security controls,
- deployment record,
- explicitný owner,
- post-release follow-up.

Break-glass použitie musí byť auditované a následne vyhodnotené.

## 24. Release metrics

Sleduj:

- release frequency,
- lead time,
- deployment frequency,
- change fail rate,
- failed deployment recovery time,
- rollback/abort rate,
- release delay po readiness,
- approval wait time,
- defect escape rate,
- stale release candidates,
- unsupported version population.

Metriky majú zlepšovať systém, nie odmeňovať objem releaseov bez hodnoty.

## 25. Anti-patterny

### Release = manuálny checklist v tickete

Evidence je zastaraná a neoveriteľná.

### Final artifact sa po schválení rebuildne

Approval patrí iným bytes.

### Veľký mesačný release bundle

Zvyšuje blast radius a komplikuje root-cause analýzu.

### Approval bez rizikového kontextu

Je iba ceremoniálny gate.

### Rollback plán „vrátime predchádzajúcu verziu“

Ignoruje dáta, events a side effects.

### Release notes sú celý Git log

Používateľ nevie identifikovať dopad.

## 26. Troubleshooting

### Nie je jasné, čo je v produkcii

Zaveď deployment record a environment manifest s digestmi a config revisions.

### Release candidate sa líši od final artifactu

Odstráň rebuild pri promotion a publikuj immutable digest.

### Approval čaká dni

Analyzuj chýbajúcu evidence, nejasný ownership, batch size a zbytočné univerzálne approval pravidlá.

### Rollback zlyhal

Over state compatibility, migrácie, queue backlog, cache schema a dostupnosť starého artifactu.

### Release branch sa výrazne odchýlila

Skráť lifecycle, automatizuj backports, pravidelne syncuj mainline a zníž množstvo paralelných release lines.

## 27. Kontrolné otázky

1. Aký je rozdiel medzi buildom, deploymentom a release?
2. Čo tvorí release unit?
3. Čo má obsahovať release record?
4. Prečo sa schválený release candidate nemá rebuildovať?
5. Aké riziká má release branch?
6. Kedy má approval reálnu hodnotu?
7. Na čo slúži release manifest?
8. Ako expand-contract podporuje release databázovej zmeny?
9. Kedy preferovať rollback a kedy roll-forward?
10. Aké controls musí zachovať emergency release?

## Glossary impact

Relevantné pojmy: release management, release unit, release record, release cadence, release train, release candidate, release branch, code freeze, release manifest, changelog, release notes, hypercare, emergency release, hotfix a supported version policy.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Semantic Versioning](semantic-versioning.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Recreate deployment →](recreate-deployment.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
