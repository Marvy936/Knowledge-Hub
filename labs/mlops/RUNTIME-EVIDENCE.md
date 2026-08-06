# MLOps flagship foundation runtime evidence

> **Evidence status: Pending**

Tento dokument bude immutable evidence summary pre prvý praktický MLOps blok. Stav `Pending` znamená, že source a tests sú pripravené, ale repository zatiaľ nemá úspešný authoritative GitHub runtime run viazaný na aktuálny pull-request subject. Tento dokument sa nesmie interpretovať ako `Runtime verified`.

## Intended execution subject

Authoritative gate je permanentný workflow `.github/workflows/mlops-lab.yml` uložený na `main`. Pull request vykonáva iba kód z rovnakého repozitára na Linux X64 self-hosted runneri, s `contents: read`, bez persisted Git credentials a v izolovanom virtual environmente pod `runner.temp`.

Po úspešnom rune sa sem zapíše:

- exact pull-request merge subject a feature revision,
- workflow run a job ID,
- runner a Python/runtime dependency versions,
- počet a výsledok contract tests,
- dataset, candidate a release identity,
- stale-promotion refusal,
- cleanup read-back,
- merge a post-merge validation boundary.

## Required positive evidence

Gate musí vytvoriť dataset snapshot, accepted candidate, release manifest a alias-state read-back. Candidate identity musí byť workspace-independent a release identity musí pinovať dataset, model, evaluation, policy generation a source revision.

## Required forbidden evidence

Druhý promotion s neaktuálnym `expected-current` musí zlyhať. Nesmie vzniknúť `stale-release.json` ani sa zmeniť úspešne zapísaný alias state.

Unit suite musí zároveň odmietnuť tampered candidate, neakceptovanú evaluation, invalid alias-state schema a nesprávny compare-before-promote subject.

## Cleanup evidence

Cleanup step sa vykonáva s `always()` a musí odstrániť runtime directory aj virtual environment. Evidence je uzavreté až po explicitnom read-backu, že oba paths neexistujú.

## Proof boundary

Úspešný foundation run preukáže iba deterministic local evidence a promotion contract. Nepreukáže živý MLflow Tracking Server, database-backed Registry, artifact store, model loadability, containerized serving, canary traffic, rollback, drift, retraining, production security ani business outcome.
