# Reusable a parallel pipelines

Reusable pipelines znižujú duplicitu a zavádzajú konzistentné delivery capabilities. Paralelizácia skracuje feedback a deployment lead time. Obe techniky však musia mať explicitné contracts, isolation a ownership; inak iba presunú komplexitu do skrytých templates, race conditions a nečitateľných dependency graphov.

## 1. Úrovne reuse

Reuse môže existovať na viacerých úrovniach:

- shell/Python/PowerShell script,
- containerized tool,
- reusable job,
- reusable workflow alebo template,
- child pipeline,
- organization-level platform capability.

Preferuj najnižšiu úroveň, ktorá poskytuje stabilný contract bez zbytočného coupling-u na konkrétnu CI platformu.

## 2. Reusable script

Script je vhodný pre logiku, ktorú možno spustiť lokálne aj v CI:

```bash
./scripts/verify.sh
./scripts/build.sh
./scripts/deploy.py --environment staging
```

Výhody:

- jednoduché unit/component testovanie,
- menší vendor lock-in,
- rovnaké správanie lokálne a v CI,
- jasný CLI contract.

Pipeline YAML zostáva orchestration vrstvou.

## 3. Reusable job

Reusable job typicky definuje:

- runtime image,
- commands,
- variables,
- artifacts,
- reports,
- retry/timeout,
- runner requirements.

Je vhodný pre štandardné capabilities ako:

- language build,
- container scan,
- artifact publication,
- deployment smoke,
- IaC validation.

## 4. Reusable workflow alebo template

Template môže skladať viac jobs a gates:

```text
standard service pipeline
├─> lint
├─> unit
├─> build image
├─> scan
├─> publish
└─> deployment workflow
```

Template je interný produkt. Potrebuje API contract, versioning, testovanie, dokumentáciu a support model.

## 5. Template contract

Explicitne definuj:

- required a optional inputs,
- input types a defaults,
- secrets/identity requirements,
- outputs,
- artifacts,
- permissions,
- supported environments,
- failure semantics,
- compatibility policy.

Skryté závislosti na repository layout-e alebo názve branch komplikujú adopciu.

## 6. Versioning reusable components

Možnosti:

- immutable commit SHA,
- versioned tag chránený proti prepísaniu,
- semantic version,
- organization-managed release channel.

Floating `main` poskytuje okamžité updates, ale môže rozbiť consumers bez ich zmeny. Version pinning umožňuje kontrolovanú migráciu.

## 7. Backward compatibility

Template zmena je breaking, keď:

- odstráni input,
- zmení default,
- zmení artifact name/path,
- sprísni permissions requirement,
- zmení failure behavior,
- zmení runner/runtime,
- zmení output contract.

Používaj deprecation warning, migration guide a support window.

## 8. Centralizácia vs. autonómia

Príliš málo reuse vedie ku copy-paste driftu. Príliš veľa centralizácie vedie k:

- globálnemu blast radiusu,
- pomalým zmenám,
- univerzálnemu template pre rozdielne workloads,
- skrytému platform coupling-u.

Dobrá platforma poskytuje paved road s escape hatchom a explicitnou exception policy.

## 9. Parallel execution

Jobs bez dependency môžu bežať paralelne:

```text
lint ─────────────┐
unit ─────────────┼─> package
SAST ─────────────┤
license-check ────┘
```

Celková pipeline duration je určená critical pathom, nie súčtom všetkých job durations.

## 10. Fan-out a fan-in

### Fan-out

Jeden input sa spracuje paralelne:

```text
artifact
├─> linux tests
├─> windows tests
├─> arm64 tests
└─> security scan
```

### Fan-in

Downstream job čaká na viac upstream výsledkov:

```text
linux + windows + arm64 + security
→ release candidate
```

Fan-in musí presne definovať required a optional dependencies.

## 11. Matrix pipeline

Matrix generuje jobs z kombinácie dimensions:

```yaml
matrix:
  os: [linux, windows]
  runtime: [3.11, 3.12]
```

Výsledok:

```text
linux / 3.11
linux / 3.12
windows / 3.11
windows / 3.12
```

Rizikom je combinatorial explosion. Testuj iba kombinácie odôvodnené support matrixom a riskom.

## 12. Selective matrix

Nie všetky kombinácie majú rovnakú hodnotu. Môžeš definovať:

- full matrix nightly,
- representative matrix per merge request,
- targeted matrix podľa changed componentu,
- mandatory oldest/newest supported version.

Selection policy musí byť transparentná a nesmie vynechať kritickú compatibility boundary.

## 13. DAG dependencies

Explicitný DAG umožní jobu začať hneď po jeho skutočných dependencies.

Napríklad documentation deploy nemusí čakať na performance tests, ak tieto workflows nemajú spoločný artifact alebo gate.

Nesprávny DAG môže spustiť downstream pred dostupnosťou required artifactu alebo evidence.

## 14. Parallel test sharding

Veľký test suite možno rozdeliť:

- staticky podľa súborov,
- podľa historical duration,
- hashom test ID,
- dynamickým schedulerom.

Dobrý shard model:

- vyvažuje duration,
- zachováva deterministický assignment alebo traceability,
- agreguje reports,
- zachytí missing/duplicate tests,
- podporuje retry iba failed shardu bez maskovania first failure.

## 15. Race conditions

Paralelné jobs môžu kolidovať cez:

- rovnaký environment,
- database schema,
- object-storage path,
- mutable artifact tag,
- shared cache,
- static port,
- external test account,
- deployment lock.

Používaj unique run IDs, isolated resources, immutable names a explicitné locks.

## 16. Artifact flow

Jobs si nemajú odovzdávať dáta cez náhodný shared filesystem. Použi explicitný flow:

```text
build job
→ artifact digest
→ parallel verification jobs
→ promotion job
```

Každý consumer má overiť očakávanú identity a integrity artifactu.

## 17. Cache pri paralelizácii

Viac jobs môže súčasne zapisovať rovnaký cache key. Dôsledky:

- last writer wins,
- čiastočný obsah,
- veľké duplicitné uploady,
- cross-architecture contamination.

Možnosti:

- read-only shared base cache,
- per-job exact cache,
- jeden designated writer,
- atomic cache publication,
- architecture/toolchain-scoped keys.

## 18. Concurrency limits

Paralelizácia je limitovaná:

- runner capacity,
- organization quota,
- external API rate limits,
- database connections,
- registry throughput,
- test-environment capacity.

Neobmedzený fan-out môže zvýšiť queue time a spomaliť všetky pipelines.

## 19. Resource-aware scheduling

Jobs môžu vyžadovať odlišné resources:

- CPU-heavy compilation,
- memory-heavy tests,
- I/O-heavy package restore,
- GPU,
- private network.

Scheduler a runner pools majú odrážať workload class. Jeden univerzálny pool vytvára noisy-neighbor a capacity planning problémy.

## 20. Fail-fast

Fail-fast zastaví zostávajúce matrix jobs po prvom failure.

Výhody:

- šetrí capacity,
- rýchlejšie signalizuje failure.

Nevýhody:

- stratí informáciu o ďalších nekompatibilných kombináciách,
- komplikuje diagnostiku release matrixu.

Použi podľa účelu: merge feedback môže fail-fast, nightly compatibility run môže dokončiť celú matrix.

## 21. Continue-on-error

Optional job môže pokračovať po failure, napríklad experimentálna platforma. Result však musí zostať viditeľný.

`continue-on-error` potrebuje:

- explicitný dôvod,
- ownera,
- expiry alebo maturity plán,
- oddelenie od required support matrixu.

## 22. Child pipeline

Parent pipeline môže vytvoriť child pipelines podľa components alebo deployment targets.

Výhody:

- menší graph per component,
- samostatné ownership a reports,
- dynamické monorepo workflows.

Riziká:

- zložitá observability,
- nejasná cancellation propagation,
- artifacts medzi parent/child,
- permission escalation,
- veľký počet pipeline objects.

## 23. Multi-project pipeline

Jeden project môže spustiť pipeline v inom repository, napríklad application release spustí environment-config update.

Potrebné sú:

- explicitný authentication model,
- immutable input identity,
- versioned contract,
- idempotency,
- cycle prevention,
- cross-project traceability.

Trigger token bez obmedzeného scope-u je security risk.

## 24. Reusable deployment workflow

Deployment template má akceptovať najmä:

- artifact digest,
- target environment,
- config revision,
- rollout policy,
- change metadata.

Nemá implicitne buildovať source alebo vyberať `latest` artifact. Deployment contract začína immutable release inputom.

## 25. Aggregácia výsledkov

Parallel jobs produkujú:

- JUnit reports,
- coverage fragments,
- scan findings,
- artifacts,
- logs.

Aggregation job musí:

- rozpoznať chýbajúci shard,
- deduplikovať results,
- zachovať source job identity,
- správne rozhodnúť overall status,
- publikovať diagnostický summary.

Zelený aggregation result pri chýbajúcom sharde je false success.

## 26. Pipeline performance

Sleduj:

- critical path duration,
- total compute time,
- queue time,
- fan-out width,
- shard imbalance,
- cache hit rate,
- artifact transfer time,
- canceled compute,
- runner utilization.

Optimalizácia critical pathu môže zvýšiť total compute. Treba vyvážiť developer feedback a náklady.

## 27. Observability reusable components

Template owner potrebuje vedieť:

- koľko projects používa jednotlivé versions,
- failure rate podľa version,
- adoption novej release,
- deprecated consumers,
- performance trend,
- najčastejšie override/escape patterns.

Bez usage telemetry sa central template vyvíja naslepo.

## 28. Testing reusable template

Použi representative fixture repositories:

- jednoduchá služba,
- monorepo,
- Windows/Linux workload,
- protected deployment,
- optional feature combinations.

Testuj:

- rendered config,
- input validation,
- artifacts/outputs,
- permissions,
- failure paths,
- backward compatibility.

## 29. Troubleshooting

### Parallel jobs používajú rozdielny artifact

Skontroluj, či každý job rebuildoval source alebo použil mutable tag. Fan-out musí začínať jedným immutable artifactom.

### Matrix pipeline vytvorila stovky jobs

Over Cartesian product dimensions, excludes/includes a support policy. Použi representative combinations.

### Child pipeline nepropaguje failure

Skontroluj trigger strategy, dependency semantics a whether parent čaká na child completion.

### Shared template update rozbil staré projects

Chýbalo version pinning alebo backward compatibility. Rollbackni template release a migruj consumers po verziách.

### Shards majú veľmi rozdielny čas

Použi historical duration balancing a sleduj outlier tests.

## 30. Časté omyly

### „Reuse znamená skopírovať YAML anchor“

Lokálna deduplikácia nie je versionovaný reusable contract naprieč projects.

### „Najviac paralelných jobs znamená najrýchlejšiu pipeline“

Capacity, queueing, external limits a transfer overhead môžu výsledok zhoršiť.

### „Central template má okamžite opraviť všetky repositories“

Neversionovaný globálny update má veľký blast radius.

### „Optional matrix failure možno ignorovať navždy“

Optional support potrebuje explicitný lifecycle a ownership.

## 31. Kontrolné otázky

1. Aké úrovne reuse poznáš?
2. Čo má obsahovať reusable template contract?
3. Prečo version pinning znižuje globálny blast radius?
4. Aký je rozdiel medzi fan-out a fan-in?
5. Ako vzniká matrix combinatorial explosion?
6. Ako rozdeliť veľký test suite na vyvážené shards?
7. Aké shared-state race conditions vznikajú pri paralelných jobs?
8. Kedy použiť fail-fast a kedy dokončiť celú matrix?
9. Aké riziká majú child a multi-project pipelines?
10. Ktoré metriky odlišujú skrátenie critical pathu od rastu celkových nákladov?

## Glossary impact

Relevantné pojmy: reusable pipeline, reusable job, workflow template, template contract, fan-out, fan-in, matrix pipeline, test sharding, shard imbalance, child pipeline, multi-project pipeline, fail-fast, continue-on-error, critical path a pipeline concurrency.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Pipeline as Code](pipeline-as-code.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Artifact versioning →](artifact-versioning.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
