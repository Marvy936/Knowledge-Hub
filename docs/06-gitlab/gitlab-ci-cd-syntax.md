# GitLab CI/CD syntax

GitLab CI/CD pipeline nie je priame vykonanie jedného YAML súboru. GitLab najprv zostaví effective configuration, rozhodne, či pipeline vznikne, vyberie jobs, validuje dependency graph, priradí execution context a až potom odošle jobs runnerom.

```text
pipeline event a repository context
→ root configuration
→ include/component resolution
→ merge a inheritance semantics
→ workflow decision
→ job-rule selection
→ expected job inventory a DAG
→ runner scheduling
→ execution
→ artifacts, reports, deployments a downstream state
```

Nosný model je configuration compiler. Root `.gitlab-ci.yml` je iba jeden vstup. Dôveryhodnosť pipeline závisí od resolved configuration identity a od toho, či skutočný job graph zodpovedá expected evidence a trust modelu.

Konkrétne keywords a semantics sa menia podľa GitLab verzie. Pri implementácii treba overiť YAML reference a CI Lint/simulation správanie konkrétnej inštancie.

## 1. Priebežný scenár: Atlas Payments pipeline

Atlas project `payments/api` používa:

```yaml
include:
  - component: gitlab.example.com/atlas/platform/verify@2.4.1
  - project: atlas/platform/deploy
    ref: 3.2.0
    file: /templates/deploy.yml
```

Pipeline má vytvoriť:

```text
MR context
→ lint + unit + contract + security
→ merged-result evidence

default branch
→ build immutable artifact
→ verify artifact
→ publish
→ deploy staging

tag/release context
→ promotion/deploy production podľa policy
```

Expected job inventory pre MR:

```text
lint
unit[1..4]
contract
security_sast
security_dependency
aggregate_evidence
```

Tri incidenty ukážu, prečo YAML syntax nestačí:

1. push s otvoreným MR vytvorí branch aj MR pipeline;
2. `rules:changes` vynechá security job pri zmene shared include-u a `optional needs` dovolí zelený gate;
3. floating include zmení deployment default na retry/interruptible bez diffu v consumer projekte.

## 2. Configuration subject

Reprodukcia pipeline potrebuje viac než application source SHA:

```text
pipeline source a ref context
root CI revision
resolved include/component identities
resolved configuration digest
policy a variable context
runner image/executor identity
generated child config digest
manual/API inputs
```

Praktický subject:

```text
pipeline ID
+ source/candidate SHA
+ pipeline source
+ resolved config digest
+ include/component versions
+ expected job inventory
+ runner/executor class
```

Mutable include alebo image môže zmeniť behavior bez local repository diffu.

## 3. Compile-time a runtime sú rozdielne fázy

### Pre-pipeline a pipeline creation

GitLab rozhoduje:

- ktoré includes sú applicable;
- či pipeline vznikne cez `workflow:rules`;
- ktoré jobs vzniknú cez job `rules`;
- aký DAG je validný.

### Job runtime

Runner vykoná script a vytvorí outputs.

Runtime-generated dotenv, file alebo script output nemôže spätne rozhodnúť, či pôvodný job mal vzniknúť. Ak selection potrebuje runtime discovery, použi explicitný plan artifact a generated child pipeline.

## 4. `workflow:rules` definuje pipeline creation policy

```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - if: '$CI_COMMIT_TAG'
    - when: never
```

Creation policy odpovedá:

- ktoré events podporujeme;
- aký účel má branch, MR, default-branch, tag, schedule a API pipeline;
- ktoré contexts smú publikovať alebo deployovať;
- ako sa zabráni duplicates.

Truth table je lepšia než čítanie izolovaných `if` výrazov:

| Source | Ref | Open MR | Pipeline? | Účel |
|---|---|---:|---:|---|
| push feature | branch | nie | podľa policy | skorý feedback |
| push feature | branch | áno | MR pipeline | review/integration |
| push main | protected branch | N/A | áno | build/publish |
| tag | protected tag | N/A | podľa release policy | release |
| schedule | explicit ref | N/A | explicitne | periodic checks |

## 5. Duplicate pipeline je policy ambiguity

Broad workflow a job rules môžu pri jednom pushi vytvoriť branch aj MR pipeline.

Dôsledky:

- dvojnásobný cost;
- rozdielne verdicts;
- dva artifacts bez jasnej autority;
- duplicitné side effects;
- nejasný required status.

Náprava nie je náhodne pridať `when: never` do jednotlivých jobs. Najprv sa centralizuje pipeline-creation truth table a až potom job applicability.

## 6. Job `rules` a first-match semantics

```yaml
deploy_production:
  script: ./deploy.sh production
  environment:
    name: production
  rules:
    - if: '$CI_COMMIT_TAG'
      when: manual
    - when: never
```

Job rules sa vyhodnocujú v poradí. Prvý match určí inclusion a relevantné atribúty.

Pre každý critical job dokumentuj:

```text
pipeline source
ref/protected context
changed paths alebo repository state
required variables dostupné v tejto fáze
first matching rule
resulting when/allow_failure/needs/variables
```

## 7. `changes` a `exists` sú selection heuristiky

`rules:changes` môže zrýchliť monorepo pipeline, ale path patterns nie sú dependency graph.

False skip môže vzniknúť pri:

- shared library;
- build image alebo toolchain zmene;
- included template zmene;
- generated source;
- rename/delete;
- odlišnom comparison base podľa pipeline source-u.

`rules:exists` dokazuje existenciu súboru, nie authorization. Untrusted branch môže pridať marker file a aktivovať job, preto privileged capability nesmie závisieť iba od `exists`.

Selection policy potrebuje konzervatívny fallback a periodický full run.

## 8. Resolved configuration je review subject

Includes, hidden jobs, `extends`, defaults a overrides vytvoria effective job, ktorý nemusí byť zrejmý z root YAML.

```text
base component
+ include merge
+ hidden parent jobs
+ default
+ consumer overrides
+ rule-specific overrides
→ resolved job
```

Review critical jobs nad resolved configuration kontroluje:

- final script a image;
- variables a permissions;
- retry, interruptibility a timeout;
- artifacts a reports;
- environment a resource group;
- runner tags;
- dependencies.

## 9. Includes a components sú executable supply-chain dependencies

Include môže pridať alebo zmeniť:

- jobs a scripts;
- defaults;
- variables;
- images/services;
- publication/deployment behavior;
- trust boundaries.

Pre každý include/component definuj:

```text
owner a source trust
immutable version alebo controlled release line
input/output contract
required permissions a variables
GitLab compatibility
fixture tests
update a rollback policy
resolved-content audit
```

`ref: main` je floating dependency. Consumer behavior sa môže zmeniť bez lokálneho diffu.

## 10. Stages a `needs` DAG

Stages vytvárajú barriers:

```text
verify complete
→ build
→ deploy
```

`needs` vytvára explicitný graph:

```text
build_api → unit shards ─┐
contract ────────────────┼→ aggregate_evidence → publish
security ────────────────┘
```

Každá edge môže byť:

- control dependency;
- artifact/data dependency;
- evidence dependency;
- policy dependency.

Optimalizácia critical pathu nesmie odstrániť required evidence ordering.

## 11. Expected job inventory a optional dependency

Ak upstream job podmienene nevznikne, fixed `needs` môže spôsobiť creation error. `optional: true` môže pipeline vytvoriť, ale nesmie skryť required evidence.

Pre optional edge definuj:

```text
prečo upstream nemusí existovať
→ aký supported context ho vynecháva
→ ako downstream rozpozná absent/not-applicable
→ či verdict môže pokračovať
→ aký auditný signal ostane
```

Fan-in gate porovná actual results s expected inventory. Zelená agregácia bez očakávaného security jobu je incomplete, nie pass.

## 12. Artifact a evidence flow

```text
build immutable candidate
→ verification jobs používajú rovnaký digest
→ reports/shards sa agregujú
→ gate overí completeness
→ publish/promote bez rebuildu
```

Rozlišuj:

- job artifact;
- report artifact;
- cache;
- published package/container/release artifact.

Consumer overuje manifest alebo digest. Parallel shards používajú unique names a identity.

## 13. Defaults, inheritance a mutation semantics

Shared `default` môže nebezpečne zmeniť privileged job:

- deployment sa stane `interruptible`;
- retry zopakuje non-idempotentnú mutation;
- generic image zmení trust/provenance;
- inherited `before_script` stiahne mutable code.

Sensitive jobs explicitne override-nu kritické vlastnosti.

`extends` používa GitLab merge semantics, nie klasickú objektovú inheritance. Obmedz depth a testuj final resolved job.

## 14. Retry, interruption a cleanup

Retry je vhodný pre klasifikovaný transient failure. Nie pre:

- deterministic test failure;
- security finding;
- non-idempotent deployment;
- migration s unknown partial outcome.

`interruptible` je vhodný pre superseded read-only jobs. Mutation job potrebuje explicitný cancellation, reconciliation a resume contract.

Cleanup critical external resource nestavaj iba na best-effort `after_script`. Použi idempotentný cleanup job, TTL controller a orphan reconciliation.

## 15. Child a generated pipelines

Generated config je compiler output.

Contract obsahuje:

- immutable input identity;
- generator version;
- generated config digest;
- schema/policy validation;
- job-count a size limits;
- expected component inventory;
- parent-child status propagation;
- artifacts/reports transfer;
- token scope a cancellation semantics.

Parent, ktorý skončí zeleno pred required child pipeline, vytvára false success.

## 16. Runner scheduling je súčasť effective security contextu

Eligible runner závisí od:

```text
project/group/instance runner scope
protected runner status
tags a untagged policy
executor isolation
host state a privileged capabilities
concurrency/resource limits
```

CI syntax môže neúmyselne presunúť privileged job na menej dôveryhodný runner. Runner identity patrí do pipeline provenance.

## 17. Worked failure: duplicate branch a MR pipelines

Push do branchu s otvoreným MR spĺňal broad branch rule aj MR rule.

```text
push event
→ branch pipeline vytvorí artifact B1
→ MR pipeline vytvorí artifact M1
→ oba spustia integration side effect
→ status checks ukazujú rozdielne jobs
```

### Príčina

Pipeline creation policy bola rozdelená medzi job rules bez jednej workflow truth table.

### Náprava

- explicitný `workflow:rules` allowlist;
- MR pipeline ako autoritatívny review context pri open MR;
- default-branch build oddelený od branch feedbacku;
- side-effect jobs iba v trusted context-e;
- test creation matrixu v CI Lint/simulation.

## 18. Worked failure: missing security job vytvoril false green

Security component sa mal spustiť pri zmene source alebo shared CI image. Consumer `rules:changes` neobsahoval path `ci/images/base/**`.

```text
base image sa zmení
→ security job nevznikne
→ aggregate job má optional needs
→ fan-in spracuje iba existujúce reports
→ pipeline pass
→ vulnerable image sa publikuje
```

### Príčina

Selection optimization bola považovaná za dôkaz applicability a gate nemal expected job inventory.

### Trvalá náprava

```text
conservative dependency patterns
→ explicitný expected security inventory
→ absent/not-applicable report
→ optional edge iba pre skutočne optional context
→ periodic full pipeline
→ selection-miss regression fixture
```

## 19. Worked failure: floating include zmenil deploy behavior

Consumer pinoval application SHA, ale deployment include používal `ref: main`. Platform tím pridal global default:

```yaml
default:
  interruptible: true
  retry: 1
```

Nový production job zdedil retry a interruption bez diffu v consumer repository.

### Dôsledok

Canceled job zanechal partial rollout; retry začal ďalšiu mutation s nejasným current state-om.

### Náprava

- immutable component version;
- sensitive-job explicit overrides;
- resolved-config digest v release recorde;
- provider compatibility release a canary consumers;
- mutation workflow s reconciliation namiesto generic retry.

## 20. Kauzálny diagnostický walkthrough

Symptom: pipeline je zelená, ale release gate nemá SAST report a napriek tomu publikoval artifact.

### Krok 1 — stabilizuj configuration subject

```text
source SHA S18
pipeline source = merge_request_event
root CI revision R6
resolved config digest C44
security component 2.4.1
expected inventory E9
```

### Krok 2 — konkurenčné hypotézy

```text
H1: security job nevznikol kvôli workflow/job rules
H2: include/component sa nenačítal alebo bol prepísaný
H3: job vznikol, ale report artifact chýbal
H4: child pipeline status/report sa nepropagoval
H5: aggregator považoval missing job za optional
H6: report existuje, ale artifact selection stiahla nesprávny shard/attempt
```

### Krok 3 — observation points

- resolved job inventory a rule trace testujú H1;
- include identities a merge output testujú H2;
- actual job/attempt artifacts testujú H3/H6;
- parent-child graph testuje H4;
- expected-versus-actual manifest a gate logic testujú H5.

Atlas zistí, že security job nevznikol pre `rules:changes` a aggregator mal optional edge bez expected inventory. H1/H5 sú potvrdené.

### Krok 4 — containment

- zablokovať publication/promóciu artifactu;
- označiť verdict `incomplete`, nie pass;
- spustiť full security pipeline nad rovnakým artifact subjectom;
- auditovať už publikované alebo nasadené outputs.

### Krok 5 — verify outcome

```text
security job vzniká v relevantnom context-e
expected inventory je complete
fan-in odmietne missing report
gate patrí rovnakému source/artifact subjectu
publication čaká na complete evidence
```

### Krok 6 — skorší control

Finding sa zmení na rule truth-table fixture, resolved-config snapshot test a invariant `expected required job cannot be silently absent`.

## 21. Validation lifecycle

```text
YAML parse
→ GitLab keyword/schema validation
→ include resolution
→ resolved configuration inspection
→ workflow/job truth-table simulation
→ expected job inventory a DAG validation
→ permission/runner/environment policy
→ component fixture pipeline
→ sandbox execution
```

`YAML valid` dokazuje iba syntax. CI Lint a pipeline simulation môžu odhaliť zložitejšie `rules` a `needs` chyby, no runtime trust, external side effects a business evidence potrebujú ďalšie tests.

## 22. Diagnostický runbook

1. Urči pipeline source, ref/candidate SHA a resolved config digest.
2. Over root a všetky include/component identities.
3. Vyhodnoť `workflow:rules` creation truth table.
4. Trace-ni first-match job rules a variable phase.
5. Porovnaj expected a actual job inventory.
6. Validuj DAG, optional edges a child/downstream propagation.
7. Over artifact/report identity a attempts.
8. Skontroluj final runner, variables, environment a mutation semantics.
9. Oprav compile-time contract, nie iba symptom v jednom run-e.
10. Zopakuj rovnaký supported context a over complete verdict.

## 23. Referenčné pravidlá

- Root YAML nie je effective pipeline.
- Resolved configuration je review a provenance subject.
- `workflow:rules` riadi pipeline creation; job rules riadia job inclusion.
- Runtime output nemôže spätne meniť compile-time selection.
- `changes/exists` sú heuristiky, nie authorization ani dependency proof.
- Includes a components sú executable dependencies.
- DAG edge môže niesť control, artifact alebo evidence dependency.
- Optional edge nesmie maskovať required evidence.
- Expected job inventory odlišuje pass od incomplete.
- Retry a interruptibility menia mutation semantics.
- Generated config je compiler output s vlastnou provenance.
- Runner selection je security boundary.

## 24. Časté omyly

### „YAML prešiel lintom, pipeline je správna“

Neoveruje full resolved graph, applicability ani runtime trust.

### „Job chýba, asi nebol potrebný“

Treba porovnať actual graph s expected inventory.

### „`optional: true` opraví creation error“

Môže premeniť required evidence na tiché missing.

### „Include z mainu je vždy aktuálny“

Je mutable a mení consumer behavior bez local diffu.

### „Retry pomôže deploymentu“

Pri unknown partial outcome môže zopakovať mutation.

## 25. Zhrnutie

Dôveryhodný GitLab CI lifecycle je:

```text
versionovaný source a executable dependencies
→ deterministický resolved config
→ explicitná creation/selection truth table
→ complete expected DAG
→ trusted runner context
→ immutable artifact a evidence flow
→ outcome-aware mutation semantics
→ auditovateľný pipeline verdict
```

CI syntax sa učí ako configuration-to-execution protocol, nie ako zoznam YAML keywords. Troubleshooting postupuje od pipeline subjectu a resolved graphu k selection, evidence a runtime observation points; zelený status bez expected evidence je false success.

## Kontrolné otázky

1. Prečo root `.gitlab-ci.yml` nie je effective pipeline?
2. Čo tvorí resolved configuration identity?
3. Ako sa líšia `workflow:rules` a job rules?
4. Prečo vznikajú duplicate pipelines?
5. Prečo `rules:changes` nie je dependency proof?
6. Aké dependencies môže niesť `needs` edge?
7. Prečo optional edge potrebuje explicitný contract?
8. Ako expected inventory odhalí false green?
9. Prečo include patrí do supply-chain modelu?
10. Ako retry, interruptibility a runner selection menia trust/failure semantics?

## Oficiálna dokumentácia

- [CI/CD YAML syntax reference](https://docs.gitlab.com/ci/yaml/)
- [Workflow rules](https://docs.gitlab.com/ci/yaml/workflow/)
- [Job rules](https://docs.gitlab.com/ci/jobs/job_rules/)
- [Includes](https://docs.gitlab.com/ci/yaml/includes/)
- [CI/CD components](https://docs.gitlab.com/ci/components/)
- [Validate CI/CD configuration](https://docs.gitlab.com/ci/yaml/lint/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Protected branches a environments](protected-branches-and-environments.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Runners a executors →](runners-and-executors.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
