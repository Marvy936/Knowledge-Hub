# Pipeline, stage, job a runner

CI/CD platforma premieňa versionovanú workflow definíciu a event context na konkrétny runtime execution graph. Pipeline, stage, job, step, runner a executor nie sú synonymá. Každá vrstva rieši inú časť ordering-u, izolácie, trustu, capacity, failure semantics a evidence. Keď sa tieto boundaries zlejú do jednej predstavy „pipeline beží“, vznikajú skryté dependencies, chýbajúce reports, nebezpečné credentials a false-green fan-in.

Workflow file je iba source intent. Platforma ho najprv parsuje, vyhodnotí conditions, rozbalí reusable workflows a matrix, priradí permissions a vytvorí jobs. Scheduler potom vyberie runner, executor pripraví process alebo container context a steps vykonajú commands. Authoritative verdict preto závisí od resolved graphu a runtime contexts, nie iba od YAML uloženého v repository.

## 1. Dominantný definition-to-verdict model

```text
trusted event a workflow revision
→ parse, include a reusable-workflow resolution
→ condition, matrix a policy expansion
→ resolved pipeline DAG
→ job contracts a permissions
→ runner scheduling a executor creation
→ step execution a explicitný data flow
→ reports, artifacts a per-job outcomes
→ complete fan-in verdict
→ cleanup, cancellation a retained evidence
```

Každý transition môže zlyhať inak. Neplatný YAML zastaví parse. Condition môže legitímne vynechať job alebo ho omylom vyradiť z required evidence. Runner provisioning môže zlyhať pred prvým stepom. Job môže skončiť success, ale nepublikovať report. Final job môže byť green, pretože používa `always()` a ignoruje failed dependency výsledok.

## 2. Exact pipeline execution subject

Pipeline instance potrebuje viac než run ID:

```yaml
pipelineSubject:
  repository: atlas/payments
  event:
    type: pull_request
    deliveryId: evt-4fd821
    actor: contributor-17
    trustClass: untrusted-fork
  sourceSha: 8e21b8d
  targetSha: 53d92af
  candidateSha: d94e1c6
  workflow:
    path: .github/workflows/ci.yml
    sha: 18ab442
    resolvedReusableWorkflows:
      - atlas/platform-ci/.github/workflows/build.yml@4d10f77
  graph:
    graphDigest: sha256:dag1000
    expectedJobs:
      - validate
      - build
      - test-linux-amd64-0
      - test-linux-amd64-1
      - test-linux-arm64-0
      - artifact-policy
      - verdict
  runnerPolicySha: a11ce92
```

Event trust class je súčasťou subjectu, pretože rovnaký workflow môže dostať odlišné permissions pri pushi, internom PR alebo forku. Resolved reusable revisions musia byť immutable; mutable ref znamená, že source workflow SHA samostatne neurčuje execution graph.

## 3. Pipeline, stage, job a step

**Pipeline** je jedna inštancia resolved workflowu pre konkrétny event a subject. Obsahuje graph, shared context, status a retained outputs.

**Stage** je ordering alebo policy grouping. Niektoré platformy ho majú ako explicitný objekt, iné ho realizujú dependencies. Stage `deploy` neznamená, že všetky predchádzajúce jobs poskytli complete evidence; to musí definovať graph a verdict contract.

**Job** je schedulovateľná execution unit s vlastným runner contextom, timeoutom, permissions, inputs, outputs a outcome-om. Filesystem a environment medzi jobs nie sú implicitne spoločné, pokiaľ platforma nepoužíva persistent workspace alebo explicitný executor model.

**Step** je command alebo action vykonaný v jobe. Steps zdieľajú job workspace a credentials podľa platformy. Step-level success nepreukazuje job-level acceptance, ak cleanup, report publication alebo post-action zlyhá.

## 4. Runner a executor

Runner je agent alebo service, ktorý prijíma job a poskytuje execution capacity. Executor je konkrétny spôsob spustenia: shell process, container, VM, Kubernetes Pod alebo iný izolovaný context. Jeden runner môže podporovať viac executorov; názov labelu `docker` nehovorí, či job má host Docker socket, privileged container alebo čistú ephemeral VM.

Runtime subject runnera môže obsahovať:

```bash
printf 'runner_host=%s\n' "$(hostname)"
printf 'kernel=%s\n' "$(uname -srmo)"
printf 'identity=%s\n' "$(id)"
printf 'workspace=%s\n' "$PWD"
printf 'cgroup=%s\n' "$(cat /proc/self/cgroup | sha256sum | cut -d' ' -f1)"
mount | sed -n '1,20p'
```

Output pomáha rozlíšiť host, kernel, identity, cgroup a mount context. Nepreukazuje úplnú izoláciu, absence residual processes ani network reachability. Runner policy má explicitne definovať persistence, privileged interfaces, egress a credential delivery.

## 5. Resolved DAG, nie vizuálne poradie

Jobs majú dependencies podľa dát a decision flowu. Stage-style lineárny model môže zbytočne blokovať nezávislé práce; príliš voľný DAG môže naopak spustiť policy pred vytvorením artifactu.

Príklad konkrétneho workflowu:

```yaml
name: candidate-ci
on:
  pull_request:

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/validate-source.sh

  build:
    needs: validate
    runs-on: trusted-build
    permissions:
      contents: read
      id-token: write
      packages: write
    outputs:
      artifact-digest: ${{ steps.publish.outputs.digest }}
    steps:
      - uses: actions/checkout@v4
      - id: publish
        run: ./scripts/build-and-publish.sh

  test:
    needs: build
    strategy:
      fail-fast: false
      matrix:
        shard: [0, 1]
        platform: [linux-amd64, linux-arm64]
    runs-on: test-${{ matrix.platform }}
    steps:
      - run: ./scripts/test-artifact.sh '${{ needs.build.outputs.artifact-digest }}' '${{ matrix.platform }}' '${{ matrix.shard }}'

  verdict:
    if: always()
    needs: [validate, build, test]
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/aggregate-verdict.sh '${{ toJSON(needs) }}'
```

YAML ukazuje intended graph a permission scopes. Nepreukazuje resolved action revisions, platform-generated jobs ani correctness `aggregate-verdict.sh`. Final job s `if: always()` sa spustí aj po failure; script musí explicitne odmietnuť failed, canceled alebo missing dependency.

## 6. Matrix a expected execution inventory

Matrix rozbalí jeden job template na viac execution units. Complete verdict potrebuje expected tuple inventory, nie iba počet úspešných jobs.

```json
{
  "expected": [
    {"platform":"linux-amd64","shard":0},
    {"platform":"linux-amd64","shard":1},
    {"platform":"linux-arm64","shard":0},
    {"platform":"linux-arm64","shard":1}
  ],
  "received": [
    {"platform":"linux-amd64","shard":0},
    {"platform":"linux-amd64","shard":1},
    {"platform":"linux-arm64","shard":0}
  ]
}
```

Fan-in check:

```bash
jq -e '
  def norm: sort_by(.platform, .shard);
  (.expected | norm) == (.received | norm)
' matrix-manifest.json
```

Non-zero exit preukazuje, že tuple sets sa nezhodujú. Nepreukazuje, prečo shard chýba ani či received reports patria správnemu artifactu. Každý report potrebuje candidate, artifact digest, platform a shard identity.

## 7. Explicitný data flow medzi jobs

Jobs si nesmú implicitne odovzdávať stav cez shared workspace. Dôveryhodné transitions používajú outputs, artifacts alebo content-addressed storage.

```text
build job
→ immutable artifact digest
→ test jobs čítajú digest
→ reports obsahujú digest
→ policy job overí ten istý digest
→ verdict agreguje subject-bound evidence
```

Cache je výkonová optimalizácia, nie job output. Ak test potrebuje build result, má používať artifact alebo digest, nie cache key, ktorého obsah môže byť evicted, overwritten alebo poisoned.

Pri upload-e sa overuje checksum:

```bash
sha256sum test-report.json > test-report.json.sha256
```

Checksum dokáže detegovať zmenu bytes po vytvorení. Nepreukazuje, že report vytvoril trusted job alebo že jeho verdict je pravdivý. Provenance zahŕňa producer identity a pipeline subject.

## 8. Job permissions a credential delivery

Najmenšie oprávnenie sa aplikuje per job. Validate job nepotrebuje publication identity. Build môže publikovať iba do candidate namespace-u. Deployment job nesmie vykonávať untrusted PR source.

Short-lived federation znižuje static secret exposure, ale token je stále capability. Audience, subject claims, repository/ref/environment conditions a lifetime určujú blast radius. `id-token: write` v každom jobe je broad trust, aj keď žiadny static secret neexistuje.

Credential read-back nesmie vypísať token. Overuje sa identity endpoint alebo cloud caller identity s redaction:

```bash
aws sts get-caller-identity --output json | jq '{Account,Arn}'
```

Output preukazuje current AWS principal pre konkrétny request. Nepreukazuje jeho effective permissions ani absence session policy. Authorization sa testuje bounded operation alebo policy simulation podľa rizika.

## 9. Failure, timeout, cancellation a retry

Job outcome musí odlíšiť application failure od execution failure. Timeout môže zanechať external side effect. Cancellation môže prerušiť upload alebo cleanup. Retry na inom runneri môže zmeniť architecture alebo workspace state.

```text
NOT_STARTED
→ SCHEDULED
→ RUNNING
→ SUCCEEDED / CHANGE_FAILED / INFRA_FAILED / TIMED_OUT / CANCELED
→ OUTPUT_PUBLISHED alebo OUTPUT_INCOMPLETE
→ CLEANUP_CONFIRMED alebo RESIDUAL_STATE_UNKNOWN
```

Retry policy sa viaže na class. Runner provisioning failure možno zopakovať. Test assertion failure sa nemá ticho rerunovať do zelena. Deployment timeout najprv potrebuje read-back, pretože mutation mohla prebehnúť.

Cancellation propagácia má zastaviť superseded work, no evidence prvého failure sa zachová. Aggressive cancel-in-progress môže odrezať report upload a vytvoriť neviditeľný flaky pattern.

## 10. Cleanup a persistent state

Ephemeral runner znižuje residual risk, ale cleanup stále zahŕňa external resources: test namespace, cloud account resources, temporary credentials, locks a reservation records. `finally` alebo post steps nemajú garantovaný beh pri host failure.

Cleanup sa preto modeluje ako reconciler nad inventory:

```text
pipeline creates resource with run/candidate labels
→ cleanup request
→ independent sweeper observes expired resources
→ ownership a TTL validation
→ delete
→ absence read-back
```

Job success bez potvrdenia critical cleanup-u môže byť `SUCCEEDED_WITH_RESIDUAL_RISK`, nie čistý pass.

## Doplnenie výkladu: pipeline graph, job isolation a runner

**Pipeline** je jedna konkrétna execution instance vytvorená z versionovanej definície a eventu. **Stage** je logická skupina alebo ordering barrier. **Job** je jednotka execution s vlastnými commands, environmentom a výsledkom. **Runner** je agent, ktorý job prijme a spustí cez executor, napríklad shell, container alebo VM.

Tieto pojmy opisujú odlišné vrstvy:

```text
pipeline definition
→ resolved job graph
→ scheduler rozhodne readiness
→ runner vyberie job
→ executor vytvorí execution environment
→ commands vrátia exit statuses a artifacts
```

Stage-based pipeline často čaká, kým všetky jobs v predchádzajúcom stage skončia. DAG pipeline môže cez dependencies spustiť job skôr. Poradie v YAML preto nemusí byť reálne execution poradie.

Job success typicky vznikne z process exit statusu. Ak shell pipeline zakryje failure skoršieho commandu, CI systém vidí nulu a označí job green. Runner nevie, že business validation zlyhala.

Runner identity je trust boundary. Persistent shell runner môže zachovať workspace, credentials alebo cache medzi jobs. Ephemeral container znižuje residue, ale host daemon, mounted socket alebo privileged mode môžu stále poskytovať širokú authority.

Pri pending jobe kontroluj:

```text
job tags a protected status
→ dostupní runners
→ runner online/paused state
→ executor capacity
→ project/group eligibility
```

Successful job preukazuje execution na konkrétnom runneri a návratový stav commands. Nepreukazuje čistotu workspace, kompletnosť outputs ani dôveryhodnosť runner hosta bez ďalšej evidence.

## 11. Connected incident `REL-PAY-66`

Atlas používal persistent self-hosted runner pre validate, build aj deploy. Workflow zobrazoval stages `test → build → deploy`, ale build job nemal explicitnú dependency na generated-client step. Warm workspace obsahoval starý output, takže test prešiel. Matrix pre arm64 mala štyri shards, no condition po chybe v expression vytvorila iba tri; verdict job používal `always()` a kontroloval iba, že aspoň jeden `test` result bol success.

Deploy job zdedil long-lived production kubeconfig a checkoutol PR branch kvôli helper scriptu. Výsledný chain bol:

```text
untrusted source
→ persistent privileged runner
→ hidden generated output
→ incomplete matrix
→ false-green fan-in
→ rebuilt artifact
→ production credential v rovnakom context-e
```

Release bol technicky spustený, ale arm64 image obsahoval chýbajúci module a jedna production node cohorta vstúpila do crash loopu. Shared runner zároveň zachoval registry credential v Docker configu pre ďalší job.

Root cause nebol iba missing shard. Pipeline design zlieval graph, data, trust a runtime boundaries.

## 12. Redesign a acceptance verdict

Atlas rozdelil pools na untrusted ephemeral verification, trusted build, isolated signing a protected deployment. Build vytvára jeden immutable artifact. Matrix manifest sa generuje pred expansion a každý report nesie tuple aj digest. Verdict odmieta missing/canceled/infra states. Deployment používa reviewed immutable helper image, nie PR checkout, a získava short-lived environment identity.

Pipeline runtime je prijatý iba vtedy, keď:

```text
workflow a resolved includes sú immutable
+ expected DAG/matrix je evidovaný
+ jobs majú explicitné inputs, outputs a permissions
+ runner/executor trust class zodpovedá eventu
+ build/test/policy používajú rovnaký artifact subject
+ fan-in odmieta missing a infra failures
+ cancellation zachová first-failure evidence
+ cleanup má nezávislý reconciliation path
+ untrusted job nevie získať publication/deploy capability
+ cold second run vytvorí rovnaký contract outcome
```

## 13. Troubleshooting flow

Pri pipeline incidente sleduj:

```text
event a workflow revision
→ resolved includes, conditions a matrix
→ DAG a job permissions
→ runner scheduling a executor context
→ workspace/cache/artifact data flow
→ per-job outcomes a outputs
→ fan-in logic
→ external mutations a cleanup
```

Competing hypotheses môžu byť parser/include drift, condition skip, matrix omission, runner label mismatch, stale workspace, artifact upload failure, permission escalation, cancellation race alebo broken aggregator. Vizuálny pipeline graph môže byť neúplný; authoritative data je resolved job inventory a runtime logs.

## 14. Anti-patterny

### Stages ako dôkaz správneho ordering-u

Stage názvy samy nepreukazujú data dependency ani complete evidence.

### Shared filesystem medzi jobs

Implicitný workspace vytvára hidden inputs, race conditions a cross-run contamination.

### Final job s `always()` bez explicitného fan-inu

Taký job môže byť zelený aj pri failed alebo missing dependencies.

### Jeden runner pool pre všetky trust classes

PR, signing a production deployment nemajú zdieľať persistence, credentials ani network access.

### Retry jobu bez identity invariants

Nový runner alebo artifact môže zmeniť subject a rerun už nie je rovnaký experiment.

## 15. Kontrolné otázky

1. Aký je rozdiel medzi workflow source a resolved pipeline graphom?
2. Čo odlišuje pipeline, stage, job a step?
3. Aký je rozdiel medzi runnerom a executorom?
4. Prečo matrix potrebuje expected tuple inventory?
5. Prečo cache nie je vhodný job output?
6. Čo musí final verdict kontrolovať pri `always()`?
7. Ako event trust class mení permissions?
8. Čo preukazuje `get-caller-identity` a čo nie?
9. Ako timeout mení retry semantics?
10. Prečo cleanup potrebuje independent reconciliation?
11. Aké boundaries sa zliali v `REL-PAY-66`?
12. Ako sa overí forbidden untrusted-to-deploy path?

## Glossary impact

Relevantné pojmy: pipeline instance, resolved execution graph, stage, job contract, step, runner, executor, event trust class, matrix tuple, expected job inventory, explicit artifact flow, fan-in verdict, residual runner state, short-lived job identity, cancellation propagation a cleanup reconciler.

## Primárne zdroje

- [GitHub Actions — Workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub Actions — Security hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [GitLab CI/CD pipelines](https://docs.gitlab.com/ci/pipelines/)
- [GitLab Runner executors](https://docs.gitlab.com/runner/executors/)
- [SLSA specification](https://slsa.dev/spec/)
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Continuous Deployment](continuous-deployment.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Trigger, artifact a cache →](trigger-artifact-cache.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
