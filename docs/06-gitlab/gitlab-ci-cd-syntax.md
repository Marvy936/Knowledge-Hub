# GitLab CI/CD syntax

GitLab CI/CD pipeline sa primárne deklaruje v súbore `.gitlab-ci.yml`. YAML syntax však nie je iba zoznam shell príkazov. Definuje pipeline creation policy, jobs, dependencies, execution context, artifacts, environments, permissions a reusable configuration.

Cieľom tejto kapitoly je rozumieť modelu konfigurácie tak, aby pipeline bola deterministická, bezpečná, diagnostikovateľná a udržiavateľná.

## 1. Pipeline configuration lifecycle

Pri vytvorení pipeline GitLab:

1. načíta root CI configuration,
2. vyrieši `include` dependencies,
3. expanduje reusable konfiguráciu,
4. vyhodnotí `workflow:rules`,
5. vytvorí alebo nevytvorí pipeline,
6. vyhodnotí job-level `rules`,
7. zostaví job graph,
8. validuje dependencies a syntax,
9. odošle eligible jobs runnerom.

Pipeline používa konfiguráciu vyriešenú pri svojom vytvorení. Neskoršia zmena included template nemení už existujúci pipeline run.

## 2. Globálne a job-level keywords

Globálne keywords ovplyvňujú celý pipeline, napríklad:

- `workflow`,
- `stages`,
- `default`,
- `variables`,
- `include`.

Job je top-level mapping, ktorý typicky obsahuje:

- `stage`,
- `script`,
- `rules`,
- `needs`,
- `image`,
- `services`,
- `variables`,
- `artifacts`,
- `cache`,
- `environment`,
- `resource_group`,
- `timeout`,
- `retry`.

Názov jobu je súčasťou pipeline contractu. Používa sa v `needs`, artifact dependencies, API, UI a downstream integráciách.

## 3. Minimálna pipeline

```yaml
stages:
  - test
  - build

lint:
  stage: test
  image: python:3.13-slim
  script:
    - pip install ruff
    - ruff check .

build:
  stage: build
  script:
    - ./scripts/build.sh
```

Jobs v rovnakej stage môžu bežať paralelne. Bez `needs` ďalšia stage štandardne čaká na úspešné dokončenie predchádzajúcej.

## 4. `workflow:rules`

`workflow:rules` rozhoduje, či pipeline vôbec vznikne.

```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - when: never
```

Používaj ho na explicitné povolenie pipeline contexts a prevenciu duplicate branch a merge-request pipelines.

Typická chyba:

```yaml
workflow:
  rules:
    - if: $CI_COMMIT_BRANCH
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

Feature branch môže spĺňať obe podmienky a vytvoriť dva pipelines pre rovnakú zmenu.

## 5. Job-level `rules`

`rules` sa vyhodnocujú zhora nadol. Prvý matching rule rozhoduje job inclusion a jeho atribúty.

```yaml
deploy_prod:
  script: ./deploy.sh production
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: manual
    - when: never
```

Rule môže používať:

- `if`,
- `changes`,
- `exists`,
- `when`,
- `allow_failure`,
- `variables`,
- `needs`,
- `interruptible`.

Pipeline creation time nemá k dispozícii hodnoty vznikajúce až počas job execution.

## 6. `rules:changes`

Path-based selection môže zrýchliť monorepo pipeline:

```yaml
service_a_tests:
  rules:
    - changes:
        - services/service-a/**/*
        - shared/**/*
  script: ./test-service-a.sh
```

Riziká:

- neúplný dependency graph,
- generated files,
- shared tooling mimo sledovaných paths,
- odlišné správanie podľa pipeline source,
- false skip pri zmene build image alebo template.

Path rules sú optimalizácia. Nesmú nahradiť správne modelovanie dependencies.

## 7. Stages a DAG cez `needs`

Stage model je jednoduchý, ale môže vytvárať zbytočné barriers. `needs` definuje explicitný DAG.

```yaml
lint:
  stage: test
  needs: []
  script: ./lint.sh

build_api:
  stage: build
  script: ./build-api.sh
  artifacts:
    paths: [dist/api/]

api_tests:
  stage: test
  needs:
    - job: build_api
      artifacts: true
  script: ./test-api.sh
```

`api_tests` nemusí čakať na nesúvisiace jobs. Sleduj však:

- missing optional job,
- artifact overwrite,
- príliš hustý graph,
- nejasnú failure propagation,
- dependency na job vylúčený cez `rules`.

Pre podmienené upstream jobs používaj explicitný optional dependency model podľa podporovanej syntaxe.

## 8. `dependencies` vs. `needs:artifacts`

`dependencies` obmedzuje artifact download z jobs v predchádzajúcich stages.

`needs:artifacts` súčasne definuje DAG dependency a artifact transfer.

Nekombinuj ich bez presného dôvodu. Pri DAG pipeline preferuj jasný `needs` graph.

## 9. `default`

Spoločné defaults znižujú duplicitu:

```yaml
default:
  image: alpine:3.22
  interruptible: true
  retry:
    max: 1
    when:
      - runner_system_failure
```

Defaults nesmú skrývať kritické behavior. Deployment job môže potrebovať:

```yaml
deploy_prod:
  interruptible: false
```

Zrušenie mutation jobu v nesprávnom okamihu môže nechať environment v neznámom stave.

## 10. Images a services

Pri container executoroch job môže definovať runtime image a sidecar services:

```yaml
integration_tests:
  image: python:3.13-slim
  services:
    - name: postgres:17
      alias: db
  variables:
    POSTGRES_PASSWORD: test-only
  script:
    - pytest -m integration
```

Pinuj image aspoň na kontrolovanú version a pre high-assurance workflow na digest. Mutable tag mení execution environment bez zmeny repository history.

## 11. Hidden jobs a `extends`

Job začínajúci bodkou nie je spustený priamo:

```yaml
.python_test:
  image: python:3.13-slim
  before_script:
    - pip install -r requirements-dev.txt

unit_tests:
  extends: .python_test
  script: pytest tests/unit
```

`extends` je GitLab configuration merge, nie YAML inheritance v programátorskom zmysle. Over resolved configuration, najmä pri arrays a nested mappings.

## 12. YAML anchors a `!reference`

YAML anchors riešia lokálnu syntaktickú duplicitu. GitLab-specific reference mechanizmy môžu prenášať vybrané configuration fragments.

Nevýhody nadmerného skladania:

- výsledok nie je čitateľný bez renderovania,
- merge semantics sú neintuitívne,
- chyba sa šíri do mnohých jobs,
- lokálny override môže odstrániť očakávanú hodnotu.

Pre cross-project reuse preferuj versionovaný component alebo include contract.

## 13. `include`

Konfiguráciu možno rozdeliť cez:

- local file,
- project file,
- remote file,
- template,
- component.

```yaml
include:
  - local: /ci/test.yml
  - project: platform/ci-components
    ref: v2.4.1
    file: /components/security.yml
```

Remote alebo cross-project include je code execution dependency. Pinuj immutable alebo kontrolovanú verziu, validuj ownership a chráň update process.

Branch ako `main` v include znamená mutable pipeline dependency.

## 14. CI/CD components

Component má byť versionovaný reusable contract s:

- explicitnými inputs,
- definovanými jobs a outputs,
- permissions dokumentáciou,
- compatibility policy,
- testovacím fixture projectom,
- release notes.

Consumer musí vedieť, ktorú component version používa. Globálne neversionované zmeny majú veľký blast radius.

## 15. Predefined variables

GitLab poskytuje predefined variables pre project, commit, pipeline, job, registry a environment context.

Príklady:

- `CI_PROJECT_PATH`,
- `CI_COMMIT_SHA`,
- `CI_COMMIT_REF_SLUG`,
- `CI_PIPELINE_SOURCE`,
- `CI_JOB_ID`,
- `CI_REGISTRY_IMAGE`,
- `CI_ENVIRONMENT_NAME`.

Over availability phase. Nie každá variable existuje pri pipeline creation a nie každá pri každom pipeline source.

## 16. `before_script` a `after_script`

`before_script` pripravuje job runtime. `after_script` je vhodný na diagnostiku a cleanup, ale jeho execution a failure semantics treba overiť pre konkrétnu situáciu.

Cleanup kritického external resource nemá byť založený iba na best-effort shell príkaze. Použi idempotentný cleanup workflow a TTL/lifecycle policy.

## 17. Retry a allow-failure

Retry je vhodný pre jasne transientné infrastructure failures, nie pre neurčité test failures.

```yaml
retry:
  max: 2
  when:
    - runner_system_failure
    - stuck_or_timeout_failure
```

`allow_failure` nesmie premeniť neznámy security alebo correctness failure na zelený pipeline bez viditeľnej policy.

## 18. Timeouts a interruptibility

Definuj:

- job timeout,
- command-level timeout,
- graceful cleanup,
- cancellation semantics,
- či job môže byť `interruptible`.

Starý read-only test job možno zrušiť po novom pushi. Produkčný deployment alebo migration nemusí byť bezpečne prerušiteľná.

## 19. Resource serialization

Jobs mutujúce rovnaký environment alebo shared resource musia byť koordinované.

```yaml
deploy_prod:
  resource_group: production
  script: ./deploy.sh
```

Resource serialization obmedzuje concurrent execution, ale nevyrieši idempotenciu ani external actors mimo GitLabu.

## 20. Dynamic a child pipelines

Dynamic child pipeline môže generovať configuration podľa repository obsahu.

Riziká:

- generated configuration injection,
- neobmedzený počet jobs,
- nejasná parent-child failure propagation,
- artifact identity medzi pipelines,
- permissions a token scope.

Generátor musí byť testovaný ako compiler: deterministic input, validovaný output a size limits.

## 21. CI Lint a merged configuration

Pred merge overuj:

- YAML syntax,
- includes,
- resolved configuration,
- rules behavior pre viac pipeline sources,
- DAG validity,
- permissions,
- artifact dependencies.

Samotná syntaktická validita nedokazuje správne execution semantics.

## 22. Bezpečnostné hranice

Pipeline configuration je executable code. Chráň:

- `.gitlab-ci.yml`,
- included templates,
- runner selection,
- protected variables,
- job tokens,
- deployment environments,
- registry credentials.

Merge-request pipeline z nedôveryhodného forku nesmie automaticky dostať production secrets alebo privileged runner.

## 23. Troubleshooting

### Pipeline nevznikla

Over `workflow:rules`, pipeline source, variable availability a syntax validation.

### Job chýba

Over poradie job-level `rules`, `changes`, `exists` a prvý matching rule.

### Duplicate pipelines

Over súbeh branch a merge-request conditions vo `workflow:rules`.

### Pipeline creation error pri `needs`

Upstream job mohol byť vylúčený cez `rules`. Zosúlaď inclusion conditions alebo optional dependency.

### Job stiahol nesprávne artifacts

Over `needs:artifacts`, `dependencies`, parallel jobs a unique artifact names.

### Included template sa zmenil bez zmeny projektu

Consumer používal mutable ref. Pinuj release tag alebo commit SHA.

## 24. Kontrolné otázky

1. Aký je rozdiel medzi `workflow:rules` a job-level `rules`?
2. Kedy stages vytvárajú zbytočný barrier?
3. Ako `needs` mení artifact download behavior?
4. Prečo included template predstavuje supply-chain dependency?
5. Aký je rozdiel medzi YAML anchorom a reusable CI componentom?
6. Prečo môže vzniknúť duplicate pipeline?
7. Kedy je job bezpečne `interruptible`?
8. Ako koordinovať dva deployment jobs pre rovnaký environment?
9. Prečo pipeline syntax validation nestačí?
10. Aké secrets smie dostať merge-request pipeline z forku?

## Glossary impact

Relevantné pojmy: GitLab pipeline configuration, `workflow:rules`, job rules, CI/CD component, resolved configuration, hidden job, `needs` DAG, predefined variable, resource group a dynamic child pipeline.

## Oficiálna dokumentácia

- [CI/CD YAML syntax reference](https://docs.gitlab.com/ci/yaml/)
- [CI/CD components](https://docs.gitlab.com/ci/components/)
- [Pipeline editor](https://docs.gitlab.com/ci/pipeline_editor/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Protected branches a environments](protected-branches-and-environments.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Runners a executors →](runners-and-executors.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
