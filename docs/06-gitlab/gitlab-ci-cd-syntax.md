# GitLab CI/CD syntax

GitLab pipeline nie je priame vykonanie jedného `.gitlab-ci.yml`. GitLab najprv načíta root configuration, resolve-ne includes alebo CI/CD components, aplikuje merge a inheritance semantics, vyhodnotí `workflow:rules`, job `rules`, variables a matrix/parallel expansion, validuje DAG a až potom vytvorí jobs pre runners. Source YAML je intent; authoritative execution subject je resolved pipeline graph pre konkrétny event, source/target SHA a GitLab version/configuration.

Nejasnosť vzniká, keď UI ukáže „pipeline skipped“, duplicate branch+MR pipelines alebo missing security job a tím hľadá chybu iba v job script-e. Job možno nikdy nevznikol pre rules, include sa resolve-ol na inú revision alebo `extends` zmenil effective fields. Diagnosis preto začína compiler lifecycle-om.

## 1. Dominantný source-to-job model

```text
pipeline source a event context
→ root `.gitlab-ci.yml`
→ include/component resolution
→ YAML merge, defaults, extends a references
→ workflow:rules pipeline-creation verdict
→ job rules and variable evaluation
→ stages/needs/parallel expansion
→ resolved DAG and job contracts
→ runner scheduling and execution
→ artifacts/reports/deployments and final verdict
```

Pipeline môže byť validná a nevzniknúť. Pipeline môže vzniknúť bez expected jobu. Job môže existovať, ale byť manual, delayed, allowed-to-fail alebo blocked. Každý state má odlišný meaning.

## 2. Exact pipeline configuration subject

```yaml
pipelineConfigSubject:
  projectId: 481
  pipelineId: 771184
  sourceSha: 8e21b8d
  targetSha: 53d92af
  candidateSha: d94e1c6
  source: merge_request_event
  rootConfigSha: ci-root-18ab442
  includes:
    - project: atlas/platform-ci
      file: /components/build.yml
      ref: 4d10f77
    - component: gitlab.atlas.example/platform/security@2.4.1
      resolvedSha: 7c118e0
  variableContextDigest: sha256:variables184
  resolvedConfigDigest: sha256:gitlab-dag771184
  expectedJobs:
    - validate
    - build
    - test-amd64
    - test-arm64
    - security-gate
    - verdict
```

Pipeline ID bez config/candidate identity nie je reusable evidence. Retry môže používať rovnakú configuration alebo current source podľa operation semantics; record musí rozlíšiť job retry, pipeline retry a new pipeline.

## 3. Includes a immutable dependencies

Includes môžu byť local, project, remote, template alebo component-based podľa GitLab capabilities. Mutable branch ref alebo remote URL znamená, že rovnaký application commit môže vytvoriť iný graph.

```yaml
include:
  - project: atlas/platform-ci
    ref: 4d10f77f4cd2c1a7e35a52c734b40403f1109de7
    file: /components/build.yml
```

Pinned ref preukazuje Git source revision include-u. Nepreukazuje nested includes, container images alebo downloaded tools. Resolved dependency inventory pokračuje transitively.

Remote include má network a integrity boundary. If supported integrity/checksum contract treba používať; inak trusted project include alebo versioned component poskytuje silnejší governance model.

## 4. `workflow:rules` a pipeline creation

`workflow:rules` rozhoduje, či pipeline vôbec vznikne. Job `rules` rozhodujú, či job patrí do created pipeline. Nesprávna kombinácia môže vytvoriť duplicate push a merge-request pipelines.

```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - if: '$CI_COMMIT_TAG'
    - when: never
```

YAML vyjadruje intended events. Nepreukazuje variable values, parent/child pipeline context alebo current GitLab expression semantics. CI Lint simulation a real test events overujú behavior.

## 5. Job `rules`

Rules sa vyhodnocujú v poradí a first matching rule určuje attributes. Broad final rule môže pridať job do unintended pipelines.

```yaml
security_gate:
  stage: verify
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
      changes:
        - src/**/*
        - deploy/**/*
        - .gitlab-ci.yml
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - when: never
```

`changes` optimalizuje execution, no expected security coverage nesmie zmiznúť pri rename, generated source alebo diff-base edge case. High-risk gate môže byť always required a internally skip non-applicable analyzers s explicitným evidence verdictom.

## 6. Defaults, hidden jobs a `extends`

Hidden job/template centralizuje contract. `extends` používa GitLab-specific reverse deep merge semantics; arrays sa nemusia merge-núť podľa intuitive expectation. Multiple inheritance zvyšuje difficulty.

```yaml
.default_job:
  image: registry.atlas.example/ci/base@sha256:build420
  interruptible: true
  retry:
    max: 1
    when: [runner_system_failure]

build:
  extends: .default_job
  script:
    - ./scripts/build.sh
```

Resolved config treba reviewovať, nie predpokladať, že template field zostal. `retry` má klasifikovať infrastructure failure; assertion failure nemá byť rerun-until-green.

## 7. Stages versus `needs`

Stages vytvárajú broad ordering. `needs` vytvára DAG a explicitný artifact/data dependency. Job s `needs: []` môže začať okamžite. DAG má zodpovedať real dependency graphu, nie len performance optimization.

```yaml
stages: [validate, build, test, release]

build:
  stage: build

unit_tests:
  stage: test
  needs:
    - job: build
      artifacts: true

release:
  stage: release
  needs:
    - job: unit_tests
      artifacts: true
```

Graph preukazuje intended ordering. Nepreukazuje, že artifact subject je správny alebo expected parallel jobs sú complete. Fan-in script/policy musí kontrolovať identity a results.

## 8. Parallel a matrix jobs

`parallel` alebo matrix expansion vytvára viac jobs. Expected tuple inventory sa generuje pred runtime. Missing job pre condition bug nesmie zmiznúť z gate-u.

```yaml
integration:
  parallel:
    matrix:
      - PLATFORM: [linux-amd64, linux-arm64]
        SHARD: [0, 1]
```

Actual job names/API inventory sa porovnajú s expected four tuples. Green three jobs nie sú complete evidence.

## 9. Variables a precedence

Variables môžu pochádzať z instance/group/project, pipeline inputs, trigger, schedule, job, dotenv report alebo environment scope. Precedence je product-specific a security-critical. Same key v multiple scopes vytvára hidden override.

Resolved non-secret variable inventory a secret references sa evidujú. Sensitive values sa nevypisujú. Runtime job môže potvrdiť generation/reference, nie secret.

## 10. CI Lint a resolved configuration

GitLab CI Lint/API dokáže validovať config a podľa features zahrnúť merged YAML alebo simulation. Practical call sa viaže na current instance API:

```bash
curl --fail --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  --form "content=<.gitlab-ci.yml" \
  "$GITLAB_URL/api/v4/ci/lint" | jq .
```

Valid response preukazuje parser/lint verdict pre supplied content a server generation. Nepreukazuje remote include immutability, exact pipeline event variables ani runtime runner/credential behavior. Full pipeline simulation alebo test project dopĺňa evidence.

## 11. Parent-child a multi-project pipelines

Downstream pipeline má vlastný project, ref, permissions a artifact boundary. Trigger success môže znamenať downstream pipeline created, nie completed or accepted. Strategy/needs semantics musia explicitne prenášať verdict a exact downstream SHA.

CI job token allowlist a cross-project artifact access sú security boundaries. Broad token scope môže zmeniť pipeline graph na lateral-movement path.

## 12. Connected incident `GL-PAY-73`

Atlas root config používal `include: project ... ref: main`. `workflow:rules` vytváral push aj MR pipeline. Security job mal `changes: src/**`, no MR menil only `.gitlab-ci.yml` a remote include, takže job nevznikol. Mutable include meanwhile added protected runner tag a OIDC ID token.

```text
MR pipeline + duplicate push pipeline
→ security job absent in MR
→ mutable include resolved new privileged graph
→ push pipeline na protected runneri
→ production credential acquisition
```

Merge gate sledoval „latest successful pipeline“ a vybral push pipeline nad source branch, nie merged-results candidate. Root cause bol unresolved pipeline source/graph/evidence subject.

## 13. Containment, recovery a acceptance

Containment pause-ne pipelines/runners, preserve-ne config snapshots, includes, variables, job API and issued identities. Recovery pinne includes, fixne `workflow:rules`, generates expected job inventory a requires merged-results pipeline for MR.

CI syntax model je prijatý iba vtedy, keď:

```text
root and transitive config generations sú exact
+ workflow creation rules have no duplicate/bypass paths
+ job rules preserve expected evidence
+ extends/defaults result is reviewable
+ stages/needs match data dependencies
+ matrix expected inventory is explicit
+ variable precedence is known
+ downstream pipeline verdict is subject-bound
+ forbidden untrusted-to-protected job graph is tested
+ second MR/push/tag scenarios produce intended graphs
```

## 14. Troubleshooting flow

```text
pipeline source/event
→ root config and includes
→ workflow:rules
→ job rules/changes
→ extends/default/variables
→ stages/needs/matrix
→ resolved jobs and permissions
→ runner scheduling and outputs
```

Competing hypotheses môžu byť duplicate event, mutable include, condition order, changes diff-base, variable shadowing, extends merge, DAG error, child-pipeline behavior alebo stale successful pipeline selection.

## 15. Anti-patterny

### `.gitlab-ci.yml` diff ako whole graph review

Includes, defaults, variables a platform evaluation tvoria effective config.

### Broad final `when: always`

Môže vytvoriť duplicate pipelines alebo unexpected jobs.

### Security job iba podľa narrow `changes`

Pipeline/security config changes môžu control vypnúť.

### Mutable include

Rovnaký application SHA môže vykonať iný privileged graph.

### Latest successful pipeline bez subject checku

Môže patriť push, branch alebo stale candidate-u.

## 16. Kontrolné otázky

1. Aký je rozdiel medzi source YAML a resolved graphom?
2. Čo tvorí exact pipeline config subject?
3. Prečo mutable include oslabuje reproducibility?
4. Čo rozhoduje `workflow:rules` a čo job `rules`?
5. Ako vznikajú duplicate pipelines?
6. Čo treba vedieť o `extends` merge semantics?
7. Ako `needs` mení graph a artifact transfer?
8. Prečo matrix potrebuje expected inventory?
9. Čo preukazuje CI Lint a čo nie?
10. Ako downstream pipeline mení trust boundary?
11. Čo sa pokazilo v `GL-PAY-73`?
12. Ako sa testuje forbidden protected-runner graph?

## Glossary impact

Relevantné pojmy: GitLab pipeline source, root configuration, include resolution, CI/CD component, workflow rules, job rules, resolved configuration, hidden job, extends, stage, needs DAG, parallel matrix, child pipeline, multi-project pipeline, CI Lint a expected job inventory.

## Primárne zdroje

- [GitLab CI/CD YAML syntax reference](https://docs.gitlab.com/ci/yaml/)
- [GitLab Docs — Pipeline architectures](https://docs.gitlab.com/ci/pipelines/pipeline_architectures/)
- [GitLab Docs — Job rules](https://docs.gitlab.com/ci/jobs/job_rules/)
- [GitLab API — CI Lint](https://docs.gitlab.com/api/lint/)
- [GitLab Docs — CI/CD components](https://docs.gitlab.com/ci/components/)
- [GitLab Docs — Downstream pipelines](https://docs.gitlab.com/ci/pipelines/downstream_pipelines/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Protected branches a environments](protected-branches-and-environments.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Runners a executors →](runners-and-executors.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
