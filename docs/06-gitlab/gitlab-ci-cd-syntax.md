# GitLab CI/CD syntax

GitLab CI/CD pipeline sa typicky deklaruje v `.gitlab-ci.yml`, ale výsledný pipeline nie je priamym vykonaním jedného YAML súboru. GitLab najprv načíta a zlúči includes, vyhodnotí pipeline-creation policy, vytvorí job graph, priradí execution context a až potom odošle jobs runnerom.

```text
source configuration
→ include resolution
→ merge/render
→ workflow decision
→ job selection
→ DAG validation
→ runner scheduling
→ job execution
→ artifacts/reports/environments
```

CI konfigurácia je privilegovaný program. Môže čítať secrets, publikovať artifacts, meniť registry a nasadzovať runtime. Preto potrebuje rovnakú disciplínu ako produkčný kód: versioning, review, testing, pinning, least privilege a audit resolved configuration.

Konkrétne keywords a semantics sa môžu meniť podľa GitLab verzie. Pri implementácii over aktuálnu CI/CD YAML reference konkrétnej inštancie.

## 1. Mental model: configuration compiler

GitLab možno chápať ako compiler a orchestrátor:

```text
input:
- root CI file
- included files/components
- repository/ref context
- pipeline source
- pre-pipeline a pipeline variables
- project/group policy

compile:
- parse
- include resolution
- configuration merge
- workflow rules
- job rules
- DAG validation

output:
- immutable pipeline instance
- resolved job definitions
- dependencies
- permissions/context
```

Pipeline používa configuration snapshot vyriešený pri vytvorení runu. Neskoršia zmena externého template nemení už vytvorený pipeline, ale môže zmeniť nový retry alebo ďalší run podľa konkrétneho mechanizmu. Preto treba ukladať resolved configuration identity.

## 2. Configuration identity

Na reprodukciu pipeline nestačí source commit aplikácie. Potrebuješ poznať:

- root `.gitlab-ci.yml` revision,
- všetky included project/ref/file identities,
- CI/CD component versions,
- remote include content alebo checksum podľa možností,
- project/group variables a policy version,
- pipeline source a ref context,
- runner/executor image versions,
- generated child configuration,
- inputs a manual variables.

Praktický record:

```text
pipeline ID
+ source SHA
+ pipeline source
+ resolved config digest
+ include/component identities
+ policy version
+ runner image/executor identity
```

Floating include z `main` znamená, že pipeline behavior sa môže zmeniť bez diffu v consumer projekte.

## 3. Pipeline configuration lifecycle

Typický lifecycle:

1. GitLab určí pipeline event a ref context.
2. Načíta root konfiguráciu.
3. Vyhodnotí a načíta applicable includes.
4. Zlúči configuration fragments podľa GitLab semantics.
5. Validuje top-level syntax a references.
6. Vyhodnotí `workflow:rules` a rozhodne, či pipeline vznikne.
7. Vyhodnotí job-level `rules`.
8. Vytvorí job inventory a DAG.
9. Overí `needs`, stages a ďalšie references.
10. Uloží pipeline snapshot.
11. Eligible jobs čakajú na runner scheduling.
12. Jobs vytvoria artifacts, reports, caches, deployments alebo downstream pipelines.

Chyba môže vzniknúť v každej fáze. „YAML je validný“ potvrdzuje iba prvú časť lifecycle.

## 4. Top-level a job-level konfigurácia

Top-level keywords môžu definovať:

- `workflow`,
- `stages`,
- `default`,
- globálne `variables`,
- `include`,
- ďalšie platformové nastavenia podľa verzie.

Job je top-level mapping, ktorý typicky obsahuje:

- `stage`,
- `script` alebo trigger semantics,
- `rules`,
- `needs`,
- `image` a `services`,
- variables,
- artifacts, reports a cache,
- environment,
- resource serialization,
- timeout, retry a interruptibility,
- tags a runner požiadavky,
- identity alebo token-related options podľa feature setu.

Názov jobu je contract. Používa sa v DAG references, API, UI, artifact transfere a downstream automation. Premenovanie môže byť breaking zmena aj bez zmeny job scriptu.

## 5. Minimálna pipeline

```yaml
stages:
  - verify
  - build

lint:
  stage: verify
  image: python:3.13-slim
  script:
    - pip install --require-hashes -r requirements-lint.txt
    - ruff check .

build:
  stage: build
  script:
    - ./scripts/build.sh
  artifacts:
    paths:
      - dist/
```

Bez explicitného `needs` jobs v rovnakej stage môžu bežať paralelne a ďalšia stage štandardne čaká na predchádzajúcu stage. Toto je jednoduchý barrier model, nie optimalizovaný dependency graph.

## 6. `workflow:rules`: vznik pipeline

`workflow:rules` rozhoduje, či pipeline instance vôbec vznikne.

```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - when: never
```

Použi explicitný allowlist pipeline contexts. Typické sources môžu zahŕňať push, merge request, schedule, web/manual, API, trigger, parent pipeline alebo ďalšie platformové contexts.

Bezpečný návrh odpovedá:

- ktoré events majú vytvoriť pipeline,
- či branch a MR pipeline majú odlišný účel,
- či tag pipeline môže publikovať release,
- ktoré manual/API inputs sú autorizované,
- ako sa zabránia duplicate runs.

## 7. Duplicate pipelines

Duplicate pipeline vznikne, keď jeden push spĺňa branch aj merge-request creation policy.

Riziká:

- dvojnásobné CI náklady,
- rozdielne verdicts nad rovnakou zmenou,
- dva artifacty s nejasnou autoritou,
- duplicitné external side effects,
- nejasné required status checks.

Príčina býva často kombinácia broad `workflow` a job rules. Vytvor truth table:

| Pipeline source | Branch | Open MR | Má pipeline vzniknúť? | Účel |
|---|---|---:|---:|---|
| push feature branch | áno | nie | podľa policy | branch feedback |
| push feature branch | áno | áno | zvyčajne MR pipeline | integration review |
| push default branch | áno | N/A | áno | post-merge/build |
| tag | tag | N/A | podľa release policy | publication/release |
| schedule | ref | N/A | explicitne | periodic checks |

Testuj rules proti všetkým podporovaným sources, nie iba jednému príkladu.

## 8. Job-level `rules`

Job `rules` sa vyhodnocujú zhora nadol; prvý matching rule určí inclusion a relevantné atribúty.

```yaml
deploy_production:
  script: ./deploy.sh production
  environment:
    name: production
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
    - when: never
```

Rule môže podľa syntaxe používať podmienky ako `if`, `changes`, `exists`, `when`, `allow_failure`, variables alebo job-specific overrides.

Kritické pravidlo: pipeline-creation evaluation nemôže používať output, ktorý vznikne až počas job execution. Ak rozhodnutie potrebuje runtime discovery, vytvor child pipeline alebo explicitný plan artifact namiesto predstierania, že job output existuje pri compile time.

## 9. Rule truth tables

Komplexné rules dokumentuj tabuľkou:

| Source | Ref type | Changed paths | Protected? | Job |
|---|---|---|---:|---|
| MR | branch | application | nie | verify |
| MR | branch | deploy manifests | nie | verify + policy check |
| push | default | ľubovoľné | áno | build/publish |
| tag | protected tag | release | áno | release |
| schedule | default | N/A | áno | full regression |

Takáto tabuľka odhalí:

- chýbajúci fallback,
- job dostupný v nebezpečnom context-e,
- duplicate inclusion,
- manual deploy v unprotected ref-e,
- required job, ktorý sa pri určitom source nevytvorí.

## 10. `rules:changes` a selection risk

Path-based selection môže zrýchliť monorepo pipeline:

```yaml
service_a_tests:
  rules:
    - changes:
        - services/service-a/**/*
        - shared/**/*
        - ci/images/python/**/*
  script:
    - ./test-service-a.sh
```

Riziká:

- neúplný dependency graph,
- shared library alebo build tool mimo patternu,
- zmena included template bez source path zmeny,
- generated source,
- base-comparison rozdiel medzi pipeline sources,
- rename alebo delete edge case,
- false skip pri zmene runtime image.

`rules:changes` je selection optimization, nie dôkaz nezávislosti. Potrebuje periodický full run a monitoring selection misses.

## 11. `rules:exists`

`exists` môže zapnúť job podľa repository layoutu, napríklad iba pre projekt s Dockerfile alebo Terraform konfiguráciou.

Riziká:

- file existuje, ale nie je authoritative,
- layout sa zmení bez aktualizácie rules,
- include project a consumer project majú odlišný evaluation context,
- malicious branch pridá marker file a aktivuje privileged job.

Privileged capability neautorizuj iba existenciou súboru v nedôveryhodnom branchi.

## 12. Stages verzus DAG

Stages vytvárajú globálne barriers:

```text
stage verify dokončí všetky jobs
→ stage build
→ stage deploy
```

`needs` definuje explicitný DAG:

```text
lint ───────────────┐
build_api → api_test ├→ package/release gate
build_ui  → ui_test ─┘
```

DAG skracuje critical path, ale vyžaduje presný model dependencies.

Každá edge môže reprezentovať:

- control dependency,
- artifact/data dependency,
- evidence dependency,
- policy dependency.

Nesprávny DAG môže spustiť publication pred dokončením security reportu alebo deployment pred agregáciou všetkých shardov.

## 13. `needs`

Príklad:

```yaml
build_api:
  stage: build
  script: ./build-api.sh
  artifacts:
    paths:
      - dist/api/

api_tests:
  stage: verify
  needs:
    - job: build_api
      artifacts: true
  script: ./test-api.sh dist/api/
```

Kontroluj:

- upstream job sa vždy vytvorí,
- optional dependency je skutočne optional,
- artifact identity je jednoznačná,
- parallel jobs neprepisujú rovnaký path/name,
- downstream job vie rozpoznať chýbajúci artifact,
- failure propagation zodpovedá gate policy.

## 14. Optional `needs` hazard

Ak upstream job podmienene nevznikne, pevný `needs` môže spôsobiť pipeline-creation error. Optional dependency môže creation umožniť, ale zároveň môže skryť chýbajúcu povinnú evidence.

Pre každú optional edge definuj:

```text
prečo upstream nemusí existovať
+ ako downstream zistí tento stav
+ či môže bezpečne pokračovať
+ aký auditný signal ostane
```

`optional` nemá byť univerzálna oprava nesúladných rules.

## 15. Artifact transfer

Artifact flow má byť explicitný:

```text
build job
→ immutable candidate artifact
→ verification jobs
→ aggregation/gate
→ publication/promotion
```

Rozlišuj:

- job artifact,
- report artifact,
- cache,
- published release/package/container artifact.

`needs:artifacts` viaže DAG a transfer. Starší `dependencies` model obmedzuje downloads z predchádzajúcich stages. Nekombinuj oba modely bez presného dôvodu.

Consumer má overiť checksum, manifest alebo inú identity, ak artifact vstupuje do release rozhodnutia.

## 16. `default`

`default` znižuje duplicitu:

```yaml
default:
  image: alpine:3.22
  interruptible: true
  retry:
    max: 1
    when:
      - runner_system_failure
```

Defaults sú súčasťou effective job behavioru. Môžu nebezpečne zmeniť privileged job:

- deployment sa stane `interruptible`,
- retry zopakuje non-idempotentnú mutation,
- všeobecný image nemá potrebnú trust/provenance,
- shared `before_script` stiahne mutable code.

Citlivé jobs majú explicitne override-nuť kritické vlastnosti a review má používať resolved configuration.

## 17. Runtime images a services

```yaml
integration_tests:
  image: python:3.13-slim
  services:
    - name: postgres:17
      alias: db
  script:
    - pytest -m integration
```

Image a service tag je dependency. Pre dôveryhodný workflow:

- používaj kontrolované versions alebo digesty,
- dokumentuj architecture/platform variants,
- minimalizuj privileged mode,
- over image provenance a vulnerability policy,
- neukladaj secrets do image layers,
- definuj readiness namiesto fixného sleepu.

Mutable image môže zmeniť pipeline behavior bez repository diffu.

## 18. Hidden jobs a `extends`

Hidden job sa priamo nespúšťa a môže slúžiť ako template:

```yaml
.python_test:
  image: python:3.13-slim
  before_script:
    - pip install --require-hashes -r requirements-dev.txt

unit_tests:
  extends: .python_test
  script:
    - pytest tests/unit
```

`extends` používa GitLab merge semantics, nie klasickú objektovú inheritance. Arrays, mappings a null/override behavior môžu byť neintuitívne.

Ochrany:

- obmedz depth inheritance,
- dokumentuj contract template-u,
- používaj resolved-config preview,
- testuj override edge cases,
- neukrývaj secrets alebo permissions v hlbokých parents.

## 19. YAML anchors a `!reference`

YAML anchors redukujú lokálnu syntaktickú duplicitu. GitLab-specific references môžu prenášať vybrané fragments.

Nie sú náhradou versionovaného reusable componentu. Pri nadmernom skladaní vzniká:

- nečitateľný effective job,
- nejasná merge precedence,
- accidental removal array hodnoty,
- široký blast radius lokálnej zmeny,
- nemožnosť používať a versionovať contract naprieč projektmi.

## 20. `include` ako supply-chain dependency

Includes môžu byť local, project, remote, template alebo component podľa GitLab capabilities.

```yaml
include:
  - local: /ci/test.yml
  - project: platform/ci-components
    ref: v2.4.1
    file: /components/security.yml
```

Každý include môže pridať jobs, scripts, variables, images, permissions a deployment behavior. Posudzuj ho ako executable dependency.

Pre include definuj:

- ownera a source trust,
- immutable alebo controlled version,
- compatibility policy,
- update automation a review,
- availability/fetch failure behavior,
- audit resolved contentu,
- deprecation a rollback.

`ref: main` je floating dependency s organizačným blast radiusom.

## 21. Include merge a precedence

Keď root a included configuration definujú rovnaké names alebo keys, výsledok závisí od GitLab merge semantics a poradia.

Riziká:

- consumer neúmyselne prepíše security job,
- include zmení defaults všetkým jobs,
- lokálny job s rovnakým názvom nahradí časť template contractu,
- variables majú inú precedence než author očakáva,
- viac includes definuje konfliktujúce fragments.

Pre citlivé components testuj:

```text
base component
+ supported consumer overrides
+ forbidden overrides
→ expected resolved job
```

Policy má kontrolovať resolved graph, nie iba root YAML.

## 22. CI/CD components

Component je versionovaný reusable contract. Mal by definovať:

- typed alebo dokumentované inputs,
- jobs a output artifacts/reports,
- required permissions a variables,
- runner/executor požiadavky,
- failure semantics,
- supported GitLab versions/context,
- compatibility a deprecation policy,
- fixture projects a test suite,
- release notes.

Consumer musí vedieť, ktorú component version použil. Central component release rolloutuj cez canary consumers a usage telemetry, nie okamžitým floating update-om.

## 23. Variables a evaluation phases

GitLab variables existujú v rôznych phases a scopes. Nie každá je dostupná pri include, workflow, job-rule a runtime evaluation.

Rozlišuj:

- pre-pipeline context,
- pipeline-creation context,
- job-only/runtime context.

Návrh rules musí používať iba variables dostupné v danej fáze. Runtime-generated dotenv alebo script output nemôže spätne rozhodnúť, či pôvodný job mal vzniknúť.

Predefined variables ako project path, commit SHA, pipeline source, job ID alebo environment metadata interpretuj podľa konkrétneho pipeline source-u.

## 24. Variable precedence a effective value

Rovnaký variable key môže byť definovaný na viacerých úrovniach. Effective value závisí od GitLab precedence rules, scope-u, protected statusu a job override-u.

Audituj:

```text
variable key
→ všetky definitions
→ level/source
→ environment scope
→ protected visibility
→ pipeline/ref context
→ job override
→ effective runtime value
```

Nejasná precedence môže spôsobiť deployment do nesprávneho accountu alebo použitie production endpointu v review app.

## 25. `before_script`, `script` a `after_script`

`before_script` pripravuje runtime, `script` vykonáva hlavný contract a `after_script` môže zbierať diagnostiku alebo cleanup podľa platformových semantics.

Cleanup kritického external resource nestavaj iba na best-effort `after_script`. Job môže byť hard-killed, runner stratený alebo token expirovaný.

Použi:

- idempotentný explicitný cleanup job,
- `when: always` podľa potreby,
- TTL/lifecycle controller,
- resource owner tags,
- periodický orphan cleanup,
- audit partial failures.

## 26. Retry

Retry je vhodný pre klasifikovaný transient failure, napríklad runner-system alebo transportný problém.

Nevhodný retry:

- deterministic test failure,
- compile error,
- security finding,
- non-idempotentný deployment,
- migration po neznámom partial completion.

Každý retry má zachovať first-attempt evidence a attempt identity. Zelený druhý pokus nesmie vymazať flaky alebo infra signal.

## 27. `allow_failure`

`allow_failure` mení gate semantics. Použi ho iba s explicitným účelom:

- experimentálny alebo advisory check,
- nepodporovaná optional matrix kombinácia,
- nový analyzer počas kalibrácie.

Potrebuje:

- ownera,
- viditeľný warning/finding,
- maturity alebo removal plan,
- oddelenie od required evidence,
- monitoring dlhodobých failures.

Permanentný security job s `allow_failure` bez review lifecycle je dekorácia.

## 28. Timeout a interruptibility

Definuj viac vrstiev:

- queue timeout podľa platformy,
- job timeout,
- command/dependency timeout,
- graceful shutdown,
- cleanup timeout,
- external operation deadline.

`interruptible` je bezpečný pre superseded read-only jobs, keď cancellation nezanechá external state.

Nie je automaticky bezpečný pre:

- deployment,
- database migration,
- artifact publication,
- package signing,
- destructive cleanup.

Mutation job potrebuje explicitnú cancellation a resume semantics.

## 29. Resource serialization

Jobs mutujúce rovnaký environment alebo shared resource koordinuj cez `resource_group` alebo ekvivalentný lock model.

```yaml
deploy_production:
  resource_group: production
  script:
    - ./deploy.sh
```

Serialization rieši súbeh GitLab jobs, ale nie:

- external actors mimo GitLabu,
- idempotency,
- stale/outdated deployment,
- lock recovery,
- partial mutation.

Deployment workflow má po získaní locku znovu overiť, že candidate je stále eligible.

## 30. Parallel a matrix jobs

Parallelization môže vytvoriť viac jobs alebo shards. Každý shard potrebuje:

- jednoznačnú identity,
- expected inventory,
- unique artifact/report names,
- deterministický alebo auditovateľný assignment,
- aggregation completeness,
- retry attempt visibility.

Fan-in job musí zlyhať alebo vrátiť incomplete, ak shard nevznikol, bol canceled alebo nepublikoval report.

## 31. Child pipelines

Parent môže spustiť child pipeline s static alebo generated configuration.

Contract musí definovať:

- input identity,
- configuration artifact a digest,
- parent-child status propagation,
- artifact/report transfer,
- token a permission scope,
- cancellation behavior,
- retry a idempotency,
- audit väzbu.

Parent, ktorý skončí zeleno pred required child pipeline, vytvára false success.

## 32. Dynamic pipeline generation

Generator je compiler. Musí byť:

- deterministic pre rovnaké vstupy,
- chránený pred injection cez filenames alebo metadata,
- obmedzený size/job-count limits,
- schema a policy validovaný,
- versionovaný a testovaný,
- schopný publikovať generated config ako evidence,
- fail-closed pri nekompletnom graph-e.

Generated graph má mať expected inventory, aby chýbajúci component pipeline neostal neviditeľný.

## 33. Multi-project pipeline

Cross-project trigger potrebuje:

- explicitný producer/consumer contract,
- immutable input identity,
- scoped authentication,
- branch/ref allowlist,
- cycle prevention,
- status propagation,
- environment/release traceability.

Trigger token s veľkým scope-om a user-supplied target project/ref je capability-escalation riziko.

## 34. Runner scheduling context

Job definition môže obsahovať tags alebo ďalšie požiadavky, ktoré určia eligible runners. Effective execution trust závisí od:

- project/group/instance runner scope,
- protected-runner settings,
- tags a whether untagged jobs sú povolené,
- executor isolation,
- runner host state,
- concurrency a resource limits.

CI syntax môže neúmyselne presunúť job na menej dôveryhodný runner. Runner selection je súčasť security reviewu.

## 35. Security boundaries

Chráň:

- `.gitlab-ci.yml`,
- include/component repositories,
- generated pipeline scripts,
- runner tags a privileged modes,
- protected variables a job tokens,
- registry publication,
- environment declarations,
- deployment scripts a resource groups.

Untrusted fork/MR pipeline nemá automaticky dostať:

- protected secrets,
- privileged persistent runner,
- package/registry write token,
- production cloud identity,
- parent-project write capability.

Trusted deploy workflow má používať artifact vytvorený a overený v predchádzajúcej boundary, nie znovu spúšťať arbitrary source script s production credentials.

## 36. CI Lint a resolved configuration

Validation má viac vrstiev:

1. YAML parse.
2. GitLab schema/keyword validation.
3. Include resolution.
4. Resolved configuration inspection.
5. Workflow/job-rule truth-table tests.
6. DAG a job inventory validation.
7. Permission/runner/environment policy checks.
8. Component fixture pipeline.
9. Sandbox integration run.

Resolved config je dôležitejšia než jednotlivé fragments, pretože ukazuje effective jobs, defaults, scripts a dependencies.

## 37. Pipeline verdict a incomplete states

Rozlišuj:

- configuration invalid,
- pipeline not created by policy,
- pipeline created with expected jobs,
- expected job missing,
- job failed,
- job infrastructure error,
- child/downstream incomplete,
- reports/artifacts incomplete,
- pipeline passed.

`Pipeline not created` môže byť správny výsledok pre nepodporovaný event alebo závažná policy chyba pre release tag. Kontext musí byť explicitný.

## 38. Troubleshooting

### Pipeline nevznikla

Over event source, `workflow:rules`, variable availability phase, include resolution a syntax/config errors.

### Job chýba

Vyhodnoť job rules zhora nadol, first-match outcome, `changes/exists` context a resolved configuration.

### Duplicate pipelines

Vytvor truth table pre push s/bez open MR. Zjednoť creation policy vo `workflow:rules` a oddeľ účel branch/MR pipeline.

### Pipeline creation error pri `needs`

Upstream job nevznikol alebo jeho meno sa po include merge zmenilo. Zosúlaď rules; optional edge používaj iba pri skutočne optional evidence.

### Job stiahol nesprávny artifact

Over DAG edge, artifact name/path, parallel shard identity, dependencies a to, či upstream job rebuildoval rovnaký subject.

### Include sa zmenil bez zmeny consumer repository

Použitý bol mutable ref alebo remote content. Pinuj version/commit a ukladaj resolved-config identity.

### Deploy job sa objavil v MR pipeline

Job rules alebo inherited template povoľujú nebezpečný context. Skontroluj resolved job, pipeline source, protected ref a environment authorization.

### Parent je zelený, child zlyhal

Trigger/status strategy nepropaguje required child result. Oprav contract a gate až po child completion.

### Pipeline používa nesprávnu variable hodnotu

Zostav precedence mapu vrátane group/project/job scope-u, protected statusu a environment matchu.

## 39. Typické anti-patterny

### YAML parse = pipeline validation

Neoveruje includes, rules, DAG, permissions ani runtime behavior.

### Floating include z `main`

Consumer pipeline sa môže zmeniť bez lokálneho diffu.

### Rovnaké rules copy-paste v každom jobe

Vznikajú nekonzistentné contexts a duplicate behavior. Centralizuj creation policy a používaj zrozumiteľné contracts.

### `optional: true` na všetkých `needs`

Pipeline sa vytvorí aj bez povinnej evidence.

### Hlboké `extends` inheritance

Reviewer nevie zistiť effective script, permissions ani artifacts bez komplikovaného renderovania.

### `allow_failure` ako oprava červeného pipeline

Maskuje risk namiesto opravy signálu alebo zmeny advisory policy.

### Retry všetkých failures

Maskuje deterministic a flaky chyby a môže zopakovať side effects.

### Privileged deployment script priamo z MR branchu

Untrusted source získava production identity.

### Dynamic generator bez limits a evidence

Môže vytvoriť injection, job explosion alebo ticho vynechať komponent.

### Parent pipeline nečaká required child

Zelený parent je false success.

## 40. Praktický rozhodovací rámec

1. Ktoré pipeline sources podporujeme a prečo?
2. Aká truth table zabráni duplicate pipelines?
3. Ktoré variables sú dostupné v každej evaluation phase?
4. Ktoré includes/components sú executable dependencies a ako sú pinované?
5. Aká je resolved-config identity?
6. Ktoré defaults a inheritance menia privileged jobs?
7. Ktoré jobs sú required a ako sa overuje inventory?
8. Ktoré `needs` edges prenášajú artifacts alebo evidence?
9. Ako sa odlišuje optional job od missing required checku?
10. Aké artifacts/reports tvoria release evidence?
11. Ktoré jobs sú bezpečne retryable a interruptible?
12. Ako sa serializujú runtime mutations?
13. Ako parent/child a multi-project pipelines propagujú status a identity?
14. Ktoré runner/executor capabilities job vyžaduje?
15. Ako sa untrusted pipeline oddeľuje od production secrets a deploymentu?

## 41. Kontrolný checklist

- pipeline sources majú explicitný workflow allowlist;
- branch/MR/tag/schedule truth table je testovaná;
- includes a components sú versionované a vlastnené;
- resolved configuration je reviewovateľná;
- mutable images a remote scripts sú eliminované alebo kontrolované;
- rules používajú variables dostupné v správnej fáze;
- path selection má konzervatívny fallback/full run;
- required job inventory je explicitný;
- DAG edges zodpovedajú control, data a evidence dependencies;
- optional needs neukrývajú required evidence;
- artifact identity a transfer sú jednoznačné;
- retries sú iba pre transient classes;
- mutation jobs nie sú nebezpečne interruptible;
- resource mutations sú serializované a idempotentné;
- child/downstream status sa správne propaguje;
- generated config má limits, validation a provenance;
- runner selection a effective permissions sú auditované;
- untrusted contexts nemajú protected secrets ani deploy capability.

## 42. Kontrolné otázky

1. Prečo je GitLab CI konfigurácia podobná compiler inputu?
2. Čo tvorí resolved configuration identity?
3. Aký je rozdiel medzi `workflow:rules` a job-level `rules`?
4. Ako vznikajú duplicate pipelines?
5. Prečo treba pre rules vytvoriť truth table?
6. Aké riziko má `rules:changes`?
7. Kedy stage barrier zbytočne predlžuje critical path?
8. Aké typy dependencies môže reprezentovať `needs`?
9. Prečo je optional `needs` potenciálne nebezpečný?
10. Ako `default` alebo `extends` mení effective job?
11. Prečo je include supply-chain dependency?
12. Čo má obsahovať CI/CD component contract?
13. Prečo runtime job output nemožno použiť pri pipeline creation?
14. Kedy je retry alebo interruptibility nebezpečná?
15. Čo musí garantovať child-pipeline status propagation?
16. Prečo je generated pipeline configuration compiler output?
17. Ako runner selection ovplyvňuje trust boundary?
18. Prečo CI Lint syntax check nestačí?

## Summary

GitLab CI/CD syntax definuje configuration-to-execution lifecycle, nie iba shell príkazy. GitLab rieši includes, merge/render, workflow a job rules, DAG, runner scheduling a runtime evidence. Dôveryhodná pipeline potrebuje explicitné source truth tables, pinované executable dependencies, review resolved configuration, kompletný job inventory, presný artifact flow a jasnú status propagation pre child a multi-project pipelines. Retry, interruption, inheritance, variables a runner selection menia security aj failure semantics. Untrusted source verification musí zostať oddelené od privileged publication a deploymentu.

## Glossary impact

Relevantné pojmy: GitLab CI/CD configuration, configuration compiler, resolved configuration, configuration digest, `workflow:rules`, job rules, rule truth table, `rules:changes`, stages, `needs` DAG, optional dependency, hidden job, `extends`, include, CI/CD component, variable evaluation phase, resource group, child pipeline, dynamic pipeline, expected job inventory a pipeline trust boundary.

## Oficiálna dokumentácia

- [CI/CD YAML syntax reference](https://docs.gitlab.com/ci/yaml/)
- [CI/CD components](https://docs.gitlab.com/ci/components/)
- [Pipeline editor](https://docs.gitlab.com/ci/pipeline_editor/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Protected branches a environments](protected-branches-and-environments.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Runners a executors →](runners-and-executors.md)
<!-- KNOWLEDGE-NAVIGATION:END -->