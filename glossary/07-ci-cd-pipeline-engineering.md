# CI/CD pipeline engineering glossary entries

## Allowed failure

Pipeline stav, pri ktorom zlyhanie jobu zostane viditeľné, ale neblokuje definovaný downstream alebo celkový pipeline result. Musí mať explicitný dôvod a ownership. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Approval — CI/CD

Explicitné rozhodnutie oprávnenej identity, ktoré povoľuje merge, promotion, deployment alebo release na základe definovaného rizika a dostupnej evidence. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Approval freshness

Platnosť approvalu viazaná na nezmenený subject, evidence, target environment, rollout strategy a časové okno; zmena ktorejkoľvek dependency môže approval invalidovať. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Artifact — CI/CD

Versionovaný a identifikovateľný výstup pipeline určený na ďalšie overenie, distribúciu alebo deployment. Na rozdiel od cache môže byť súčasťou correctness a release evidence. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Artifact digest

Content-derived immutable identifikátor artifactu, napríklad SHA-256 digest container image, používaný na presnú väzbu medzi buildom, evidence, promotion a deploymentom. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Artifact promotion

Riadené použitie alebo presun toho istého immutable artifactu v ďalšom environment-e bez jeho rebuildu. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Authoritative run

Pipeline run určený policy ako jediný zdroj required verdictu alebo release artifactu pre konkrétny candidate a workflow revision. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Behavioral equivalence — environment

Miera, do akej nižší environment zachováva produkčne relevantné protokoly, konfiguráciu, topology, limits a security behavior aj bez úplnej veľkostnej parity. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Blocking gate

Quality gate, ktorého neúspech zastaví merge, promotion alebo deployment. Má sa používať pre spoľahlivý signál spojený s neprijateľným rizikom. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Build once, promote many

Delivery princíp, pri ktorom sa source zostaví raz do immutable artifactu a rovnaký digest sa overuje a promotionuje cez všetky environments. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Cache — CI/CD

Odstrániteľná optimalizácia pipeline na znovupoužitie dependencies alebo intermediate build dát. Pipeline musí zostať korektná aj pri cache miss alebo eviction. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Cache key

Identifikátor cache odvodený zo všetkých významných vstupov, napríklad OS, architecture, toolchain version, lockfile hash a build configuration. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Cache poisoning

Stav, keď nedôveryhodný alebo chybný pipeline uloží cache, ktorú neskôr použije dôveryhodnejší workflow, čím môže ovplyvniť build alebo spustiť škodlivý obsah. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Child pipeline

Samostatný pipeline run vytvorený parent pipelineom pre component, matrix časť alebo dynamicky generovaný workflow, s explicitnými input/output a failure-propagation pravidlami. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Cleanup transition

Povinný pipeline alebo job transition, ktorý po success, failure, timeout alebo cancellation uvoľní locks, credentials a temporary resources a zachová dostupné evidence. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Critical path — pipeline

Najdlhšia dependency cesta od triggeru po požadovaný výsledok pipeline. Určuje minimálnu možnú duration pri danom grafe bez ohľadu na súčet všetkých job durations. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## DAG — CI/CD

Directed Acyclic Graph vyjadrujúci explicitné dependencies medzi jobs vrátane ordering-u, artifact flowu a failure propagation. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Decision packet

Kompaktný auditovateľný balík pre approvera obsahujúci subject, risk, evidence, findings, target, rollout, recovery a expiry kontext potrebný na vedomé rozhodnutie. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Deployment lock

Mechanizmus serializujúci alebo koordinujúci mutations jedného environmentu, aby sa paralelné deploymenty navzájom neprepísali alebo nevytvorili nekonzistentný stav. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Deployment record

Auditovateľný záznam spájajúci environment, artifact digest, configuration revision, pipeline run, identity, čas a výsledok konkrétneho deploymentu vrátane partial a failed attempts. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Environment drift

Rozdiel medzi deklarovaným desired state environmentu a jeho skutočným runtime stavom, napríklad po manuálnej config alebo infrastructure zmene. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Evidence freshness

Pravidlá určujúce, či test result, scan, review alebo approval stále patrí k aktuálnemu commitu, artifactu, policy a environment state. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Evidence manifest

Explicitný zoznam required a optional evidence položiek pre konkrétny gate subject vrátane subject identity, tool statusu, completion, timestamps, integrity a exception references. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Expected result inventory

Pred vykonaním fan-out-u deklarovaná množina required a optional result identities pre konkrétny immutable subject. Fan-in ju porovnáva s prijatými výsledkami, aby odhalil chýbajúci, duplicitný, stale alebo nevytvorený job či shard. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Execution contract — job

Deklarované runtime, inputs, permissions, resources, timeout, retries, outputs, success criteria a cleanup semantics jedného samostatne plánovaného jobu. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Executor — CI/CD

Mechanizmus použitý runnerom na vykonanie jobu, napríklad host shell, container, virtual machine alebo Kubernetes pod. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Fail closed — gate policy

Policy, pri ktorej chýbajúca alebo nedostupná evidence spôsobí blokovanie operácie. Používa sa pri kontrolách, ktorých obídenie predstavuje neprijateľné riziko. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Fail open — gate policy

Policy, pri ktorej nedostupná kontrola neblokuje operáciu, ale vytvorí viditeľný degraded signal. Je vhodná iba tam, kde riziko nedostupnosti gate prevyšuje riziko pokračovania. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Fan-in — pipeline

Bod pipeline grafu, v ktorom downstream job čaká na výsledky viacerých upstream jobs alebo shards a overuje ich úplnosť. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Fan-out — pipeline

Rozdelenie jedného vstupu, artifactu alebo test suite do viacerých paralelných jobs. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Fencing token

Monotónna alebo unikátna lease identity overovaná pred každou environment mutation, ktorá zabráni starému deployment ownerovi pokračovať po strate alebo expirácii locku. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Gate decision contract

Model rozhodnutia spájajúci immutable subject, expected evidence manifest, applicability, freshness, versioned policy a rozhodovaciu authority do explicitného viacstavového verdictu. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Gate subject

Presná immutable alebo versionovaná entita hodnotená gate-om, napríklad candidate SHA, release manifest digest, rendered configuration, environment revision alebo rollout cohort. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Generated graph completeness

Dôkaz, že dynamický pipeline generator analyzoval deklarovaný scope, zachoval required gates, vytvoril všetkých potrebných producers/consumers a explicitne uviedol preskočené components. Pozri [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md).

## Identity-aware fan-in

Agregácia, ktorá pred verdictom overí expected inventory aj zhodu subjectu, variantu, shardu, child runu a attempt identity každého výsledku. Zelené prijaté reporty nestačia, ak výsledný set nie je úplný a porovnateľný. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Incomplete verdict

Výsledok signalizujúci, že autoritatívne rozhodnutie nemožno urobiť, pretože chýba required job, shard, report, artifact alebo tool execution status. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Job — CI/CD

Najmenšia samostatne plánovaná execution unit pipeline s vlastným runtime, inputs, permissions, commands, timeoutom, resultom a outputs. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Job attempt

Jedno konkrétne vykonanie jobu vrátane runnera, časov, logs a verdictu; retry vytvára nový attempt a nesmie prepísať evidence predchádzajúceho pokusu. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Matrix pipeline

Pipeline model generujúci viac jobs z kombinácie dimensions ako OS, architecture, runtime version alebo deployment target. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Permission graph

Resolved tok authority medzi pipeline jobs, runners, artifacts, secrets, registries, cloud roles a environments používaný na review effective blast radiusu. Pozri [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md).

## Pipeline — CI/CD

Runtime inštancia versionovaného delivery workflowu vytvorená konkrétnym triggerom a viazaná na candidate, event context, variables, jobs, permissions, artifacts a results. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Pipeline as Code

Správa delivery workflowu ako versionovaného, reviewovateľného, testovateľného a policy-validovaného privilegovaného programu. Pozri [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md).

## Pipeline instance

Konkrétny runtime run po vyhodnotení workflow definície, trigger payloadu, candidate identity, conditions, matrix, permissions a environment policy. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Promotion evidence

Súbor výsledkov a metadata viazaných na konkrétny artifact alebo release manifest digest, ktoré odôvodňujú jeho postup do ďalšieho environmentu. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Promotion subject

Kompletný deployment tuple hodnotený pred promotion, typicky release manifest, rendered configuration, infrastructure revision, target environment a relevantný shared-state snapshot. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Provider–consumer contract — CI/CD

Versionovaný behaviorálny contract medzi providerom reusable capability a consumerom. Definuje input/output schema, resolved graph semantics, permissions, artifact a evidence identity, failure propagation, compatibility, support a migration lifecycle. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Protected environment

Environment s platformovo vynucovanými pravidlami pre refs, identities, approvals, secrets, deployment windows, artifact eligibility alebo concurrency. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Quality gate

Automatizovaný alebo kombinovaný rozhodovací bod, ktorý vyhodnotí versionovanú policy nad konkrétnou evidence a povolí, zablokuje alebo eskaluje ďalší krok delivery. Pozri [Quality gates a approvals](docs/05-ci-cd-and-release/quality-gates-and-approvals.md).

## Release manifest

Immutable manifest spájajúci digests viacerých component artifacts, migration bundle, config schema a evidence references do jednej release identity. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Rendered configuration digest

Content-derived identity výslednej environment configuration po templates, overlays, defaults a non-secret inputs, používaná na väzbu promotion, approval a deployment recordu. Pozri [Environment a promotion](docs/05-ci-cd-and-release/environment-and-promotion.md).

## Resolved config digest

Immutable digest effective pipeline konfigurácie po spracovaní includes, templates, inheritance, inputs, generated graphu a policy revisions. Pozri [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md).

## Resolved pipeline configuration

Výsledná pipeline definícia po spracovaní includes, templates, inheritance, parameters, rules a generated configu; predstavuje konfiguráciu, ktorú platforma skutočne vykoná. Pozri [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md).

## Reusable pipeline

Versionovaný pipeline component alebo workflow s explicitným input, output, permissions a failure contractom určený na použitie vo viacerých projects. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Runner — CI/CD

Agent alebo execution capacity, ktorá prijme job od CI control plane a vykoná ho prostredníctvom zvoleného executora. Runner je zároveň capacity a security boundary. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Runner pool

Oddelená skupina runners s definovanými capabilities, trust levelom, network accessom a scaling policy. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Service readiness — pipeline

Stav, keď testovacia dependency nielen beží ako proces, ale dokáže spracovať relevantnú operáciu v deklarovanom deadline. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Stage — CI/CD

Logická skupina jobs alebo broad ordering barrier v pipeline. Stage nie je samostatná execution unit a pri presnom DAG modeli nemusí určovať všetky dependencies. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Synthetic merge commit

Dočasný commit reprezentujúci výsledok zlúčenia source branch so súčasným target branch, používaný na testovanie budúceho mainline stavu. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).

## Template contract — CI/CD

Versionované pravidlá reusable template definujúce inputs, defaults, outputs, artifacts, permissions, supported scenarios, failure semantics a compatibility policy. Pozri [Pipeline as Code](docs/05-ci-cd-and-release/pipeline-as-code.md).

## Test sharding

Rozdelenie test suite medzi paralelné jobs podľa súborov, test IDs alebo historical duration s následnou validáciou úplnosti a agregáciou reportov. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Trigger — CI/CD

Udalosť alebo explicitný pokyn, ktorý vytvorí pipeline run a určí jeho commit, event payload, actor identity, variables a permission context. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Trigger contract

Resolved runtime contract vytvorený triggerom, ktorý spája event identity, actor, candidate a workflow revision, typed inputs, permissions, secret scope a concurrency policy. Pozri [Trigger, artifact a cache](docs/05-ci-cd-and-release/trigger-artifact-cache.md).

## Workflow template

Versionovaný reusable opis viacerých jobs, dependencies a policy hooks poskytujúci štandardnú delivery capability pre viaceré projects. Pozri [Reusable a parallel pipelines](docs/05-ci-cd-and-release/reusable-and-parallel-pipelines.md).

## Workspace lifecycle

Životný cyklus job workspace-u od čistého vytvorenia cez checkout a execution po upload explicitných outputs, credential revoke a odstránenie temporary state. Pozri [Pipeline, stage, job a runner](docs/05-ci-cd-and-release/pipeline-stage-job-runner.md).