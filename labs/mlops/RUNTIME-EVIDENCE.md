# MLOps flagship runtime evidence

> **Evidence status: Pending**

Tento dokument je authoritative runtime evidence summary pre praktický MLOps lifecycle. Stav `Pending` znamená, že source, contracts a tests sú pripravené, ale repository zatiaľ nemá úspešný authoritative post-merge GitHub run viazaný na aktuálny validation subject. Dokument sa nesmie interpretovať ako `Runtime verified`.

## Evidence layers

MLOps flagship má dve odlišné vrstvy:

```text
foundation evidence
→ dataset snapshot, candidate, release, compare-before-promote a stale refusal

registry evidence
→ MLflow server, database metadata, artifact upload/read-back,
  registered version, alias read-back, exact-version load a restart verification
```

Zelený výsledok jednej vrstvy automaticky nepreukazuje ďalšiu. Registry evidence tiež nepreukazuje serving, canary, rollback, drift alebo retraining.

## Authoritative execution subject

Repository obsahuje dva oddelené runtime paths:

- `.github/workflows/mlops-lab.yml` používa Linux X64 self-hosted runner pre foundation a Registry checks,
- `.github/workflows/mlops-registry-hosted.yml` používa GitHub-hosted `ubuntu-latest` pre nezávislý Registry, artifact a restart round-trip.

Oba pull-request paths používajú trusted workflow z base vetvy, exact subject SHA, branch z rovnakého repozitára, `contents: read` a checkout bez persisted Git credentials. Disposable virtual environment a runtime state sú uložené pod `runner.temp`.

Každý push-only status publisher vykonáva samostatný no-checkout job s jedinou write permission `statuses: write`. Feature-branch kód preto nedostáva write token. Hosted workflow bol bootstrapnutý na `main`; tento dokumentačný merge je samostatný `labs/mlops/**` trigger, pri ktorom workflow už existuje v parent revision. Evidence zostáva `Pending`, kým connector-readable statusy nepotvrdia výsledok exact merge commit-u.

## Required foundation evidence

Gate musí preukázať:

- dataset snapshot a SHA-256,
- accepted candidate a canonical candidate ID,
- release manifest a canonical release ID,
- alias-state read-back,
- source revision viazanú na exact execution subject,
- refusal druhého promotionu s neaktuálnym `expected-current`,
- absenciu `stale-release.json`,
- cleanup virtual environmentu a runtime directory.

Unit suite musí odmietnuť tampered candidate, neakceptovanú evaluation, invalid alias-state schema, workspace-dependent identity a nesprávny compare-before-promote subject.

## Required Registry evidence

Registry gate musí vykonať celý tento chain:

```text
trusted deterministic model.joblib
→ candidate digest verification pred deserializáciou
→ loopback MLflow Tracking Server
→ SQLite metadata backend
→ oddelený proxied filesystem artifact destination
→ run params, metrics, tags a candidate evidence
→ logged model a registered model version
→ model-version tags a alias mutation
→ API read-back runu, version a aliasu
→ source/model.joblib download cez tracking server
→ SHA-256 porovnanie
→ exact models:/<name>/<version> load
→ prediction parity
→ MLflow server restart
→ opakovaná exact-version verification
```

Authoritative evidence musí obsahovať:

- exact merge commit,
- workflow run alebo connector-readable status target,
- Python a MLflow version,
- experiment ID, run ID a logged model ID,
- registered model name a exact numeric version,
- exact immutable Registry URI,
- alias a version, na ktorú sa alias pri rune resolvoval,
- candidate ID a source revision tags prečítané späť z runu aj model version,
- pôvodný a stiahnutý model SHA-256,
- registry evidence ID,
- source a Registry prediction parity,
- dôkaz, že SQLite database a artifact files existovali pred cleanupom,
- dôkaz opakovanej verifikácie po reštarte servera,
- cleanup read-back.

## Required forbidden evidence

Runtime musí odmietnuť alebo odhaliť:

- source model bytes, ktoré nesedia s candidate digestom,
- Registry evidence s alias URI namiesto exact numeric version URI,
- model version s nesprávnym source runom,
- chýbajúci alebo nesprávny candidate/source/model tag,
- artifact download s odlišným SHA-256,
- alias ukazujúci na inú version než zaznamenaný subject,
- prediction mismatch medzi source artifactom a exact Registry version,
- neplatný alebo dodatočne upravený registry evidence payload.

Mutable alias `models:/<name>@<alias>` je control-plane reference. Runtime evidence a budúci deployment subject musia pinovať `models:/<name>/<version>` a model digest.

## Cleanup evidence

Cleanup step sa vykonáva s `always()` a musí ukončiť lokálny MLflow server, odstrániť:

- SQLite database,
- artifact destination,
- downloaded artifacts,
- generated Machine Learning dataset a model,
- manifests a registry evidence,
- virtual environment,
- všetok disposable runtime state.

Evidence je uzavreté až po explicitnom read-backu, že runtime a virtual-environment paths neexistujú.

## Proof boundary

Úspešný registry run preukáže database-backed lokálny Registry, oddelený artifact store, API lineage read-back, exact model version, artifact byte integrity, prediction parity a persistenciu po reštarte servera v rovnakom resolved runtime.

Nepreukáže:

- fresh dependency reconstruction na inom operačnom systéme,
- containerized serving alebo image digest,
- canary traffic a rollback,
- production metrics alebo no-data handling,
- drift a controlled retraining,
- vzdialený artifact object store,
- multi-user authentication a authorization,
- HA, backup/restore alebo disaster recovery,
- production readiness alebo business outcome.
