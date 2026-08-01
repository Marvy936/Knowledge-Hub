# Pipeline as Code

Pipeline as Code spravuje delivery workflow ako versionovaný privilegovaný software systém. YAML alebo DSL uložené v repository sú iba source intent. Skutočný runtime behavior vznikne až po spracovaní includes, reusable workflows, inheritance, parameters, defaults, conditions, matrix expansion, permission policy a runner selection. Review jedného source file-u preto nepreukazuje, čo platforma naozaj spustí.

Pipeline code má vysokú autoritu. Môže čítať source, spúšťať untrusted commands, vydávať workload identity, publikovať artifacts, meniť environmenty a mazať resources. Jeho lifecycle potrebuje rovnakú disciplínu ako application code: ownership, tests, immutable dependencies, staged rollout, observability, rollback a incident response.

## 1. Dominantný source-to-execution model

```text
versionované pipeline source fragments
→ include/reusable dependency resolution
→ typed inputs, secrets a variable binding
→ inheritance, merge a condition evaluation
→ resolved workflow configuration
→ policy nad effective graphom a permissions
→ pipeline execution a artifacts
→ runtime evidence a deployment side effects
→ pipeline-change acceptance
→ rollback, deprecation a dependency upgrade
```

Chyba môže vzniknúť ešte pred job execution. Mutable include sa môže zmeniť, default input môže získať inú hodnotu, child workflow môže pridať privilege a expression môže vyradiť security job. Source diff musí preto viesť k resolved-graph diffu.

## 2. Exact pipeline-definition subject

Atlas Payments eviduje pipeline generation:

```yaml
pipelineDefinitionSubject:
  repository: atlas/payments
  rootWorkflow:
    path: .github/workflows/release.yml
    sha: 18ab442
  dependencies:
    - repository: atlas/platform-ci
      path: .github/workflows/build.yml
      sha: 4d10f77
    - repository: atlas/platform-ci
      path: .github/actions/publish/action.yml
      sha: b11f20a
  inputSchemaSha: c21de91
  policyBundleSha: 66cf902
  runnerPolicySha: a11ce92
  resolvedGraphDigest: sha256:dag1000
  expectedPermissionSets:
    build:
      contents: read
      id-token: write
      packages: write
    deploy:
      contents: read
      id-token: write
```

Mutable references ako `@main` alebo `@v4` môžu byť convenient locator, ale nie immutable execution identity. Ak provider podporuje verified publisher a protected major tag, risk je nižší, no exact reproducibility stále vyžaduje resolved commit SHA v evidence.

## 3. Source syntax versus resolved configuration

Pipeline source môže vyzerať bezpečne:

```yaml
jobs:
  release:
    uses: atlas/platform-ci/.github/workflows/release.yml@main
    with:
      environment: production
```

Runtime behavior však závisí od current `main`, defaults a nested actions. Dôveryhodný model pinne dependency:

```yaml
jobs:
  release:
    uses: atlas/platform-ci/.github/workflows/release.yml@4d10f77f4cd2c1a7e35a52c734b40403f1109de7
    with:
      environment: production
```

Pinned SHA preukazuje source identity dependency. Nepreukazuje, že nested Docker images, package installs alebo scripts sú tiež pinned. Dependency inventory musí pokračovať cez celý execution graph.

## 4. Typed inputs a configuration contract

Untyped strings vytvárajú nejednoznačné behavior. Input `deploy: "false"` môže byť v niektorom expression jazyku truthy. Environment name môže byť použitý v path alebo role name bez allowlistu. Reusable workflow má definovať schema, defaults a invariants.

```yaml
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      canary-percent:
        required: false
        type: number
        default: 2
      deploy:
        required: true
        type: boolean
```

Source typing znižuje chyby, ale platform-specific coercion a expression semantics sa musia testovať. Domain validation stále potrebuje allowlist:

```bash
case "$ENVIRONMENT" in
  staging|production) ;;
  *) echo "unsupported environment: $ENVIRONMENT" >&2; exit 2 ;;
esac

python - <<'PY'
import os
p = float(os.environ['CANARY_PERCENT'])
if not 0 <= p <= 10:
    raise SystemExit('canary percent outside approved bound')
PY
```

Úspešný validation step preukazuje hodnoty v jednom jobe. Nepreukazuje, že downstream reusable workflow nepoužije iný default alebo shadow variable s vyššou precedence.

## 5. Variable a secret precedence

Pipeline hodnoty môžu pochádzať z repository, organization, environment, workflow inputs, job environmentu, secret store-u a runtime outputs. Rovnaký názov vo viacerých scopes môže vytvoriť hidden override.

```text
platform defaults
→ organization variables
→ repository variables
→ environment variables/secrets
→ workflow inputs
→ job/step environment
→ runtime output
```

Presná precedence je platform-specific a musí byť overená z official docs aj praktickým testom. Critical values nemajú byť identifikované iba názvom. Release record má uložiť non-secret resolved values a references/versions secretov bez expozície samotných secretov.

## 6. Resolved graph a permission inspection

Pipeline review potrebuje machine-readable resolved model. Ak platforma neposkytuje kompletný export, repository môže vytvoriť vlastný compiler alebo test harness pre allowed subset.

Source lint:

```bash
actionlint .github/workflows/*.yml
```

Lint preukazuje syntaktické a časť semantic issues podľa tool version. Nepreukazuje runtime permissions, remote include content ani behavior shell scripts.

Repository môže exportovať graph contract:

```json
{
  "jobs": {
    "build": {
      "needs": ["validate"],
      "runnerClass": "trusted-build",
      "permissions": ["contents:read", "id-token:write", "packages:write"]
    },
    "deploy": {
      "needs": ["gate"],
      "runnerClass": "protected-deploy",
      "permissions": ["contents:read", "id-token:write"]
    }
  }
}
```

Policy check:

```bash
opa eval --data policy/pipeline.rego --input resolved-graph.json 'data.pipeline.deny'
```

Empty deny set preukazuje súlad s loaded policy a provided graph. Nepreukazuje, že export obsahuje všetky hidden platform behaviors alebo že runtime scheduler presadí runner class. Runtime evidence sa porovná s graph contractom.

## 7. Pipeline dependency a supply-chain boundary

Reusable workflow, action, container image, package installer a downloaded binary sú code dependencies. Každá môže zmeniť execution alebo exfiltrovať credentials.

Dôveryhodná dependency policy zahŕňa:

- immutable source revision;
- trusted repository a ownership;
- reviewed update process;
- checksum alebo signature pre binaries;
- digest-pinned container images;
- network allowlist a minimal install surface;
- transitive dependency inventory;
- deprecation a emergency revocation.

Command ako `curl URL | sh` spája network retrieval a privileged execution bez integrity boundary. Lepší model download-ne versioned artifact, overí checksum/signature a až potom vykoná.

```bash
curl --fail --location --output tool.tar.gz "$TOOL_URL"
echo "$TOOL_SHA256  tool.tar.gz" | sha256sum --check -
tar -xzf tool.tar.gz
```

Checksum match preukazuje expected bytes. Nepreukazuje, že expected checksum pochádza z trusted release authority.

## 8. Trust separation v jednom workflowe

Pipeline file môže obsahovať untrusted verification aj protected deployment, ale jobs musia mať oddelené execution a credential boundaries. Output z untrusted jobu sa nesmie interpretovať ako command alebo path bez validation.

```text
untrusted PR job
→ produces bounded report/artifact
→ trusted verifier checks schema, digest a policy
→ protected release job consumes immutable subject
```

`pull_request_target`-style event, ktorý používa target workflow s privileged secrets, je bezpečný iba vtedy, keď nevykoná untrusted PR code. Checkout PR SHA a následný shell execution ruší boundary.

## 9. Pipeline tests

Pipeline change potrebuje vrstvené tests:

```text
syntax/lint
→ schema a type tests
→ resolved graph snapshot/diff
→ policy tests nad permissions/runners/deploy paths
→ component tests scripts/actions
→ sandbox execution
→ failure injection
→ staged adoption
```

Snapshot resolved graphu nie je jediný oracle; legitimate dependency update môže graph zmeniť. Review musí vysvetliť význam diffu.

Príklad property test môže overiť, že žiadny fork event nevytvorí job s production role:

```rego
package pipeline

deny contains msg if {
  input.event.trustClass == "untrusted-fork"
  some job
  job := input.jobs[_]
  job.environment == "production"
  msg := sprintf("fork event reaches production job %s", [job.name])
}
```

Policy testuje model, nie runtime. Acceptance potrebuje aj sandbox forbidden-path test.

## 10. Pipeline change rollout

Zmena shared reusable workflowu môže ovplyvniť stovky repositories. Major tag update bez consumer inventory vytvára fleet-wide blast radius. Pipeline platform product používa release channels alebo rings:

```text
workflow candidate SHA
→ contract tests
→ internal canary repositories
→ low-risk consumer ring
→ broader adoption
→ default ref update
→ old generation support window
→ retirement
```

Consumers majú možnosť pinning-u a rollbacku. Platform sleduje resolved adoption, nie iba source search. Repository môže referencovať wrapper, ktorý ďalej volá starú generation.

## 11. Runtime read-back a audit

Po execution sa porovná intended graph s actual jobs, runner identities a permissions. Pipeline record zachová:

```text
trigger subject
+ root/dependency SHAs
+ resolved graph digest
+ actual job inventory
+ runner/executor identities
+ issued workload identities
+ artifact/report subjects
+ gate decisions
+ environment mutations
```

Cloud audit log môže potvrdiť, ktorá federated role vykonala deployment. Nepreukazuje, že role získala správny workflow subject, ak trust policy neobsahuje relevantné claims alebo logs ich nezachovávajú.

## Ako sa source pipeline zmení na resolved execution graph

Pipeline as Code ukladá orchestration contract do versionovaného source-u, ale runner nevykonáva iba jeden YAML file. Systém spracuje includes, templates, reusable workflows, variables, conditions a matrix expansion a vytvorí resolved execution graph. Tento resolved graph je skutočný plán jobov, dependencies, images, permissions a rules pre konkrétny run.

Mutable include alebo action ref môže zmeniť graph bez zmeny aplikačného commit-u. Preto sa externé templates a actions pinujú na immutable revision a ich identity patria do release evidence. Review lokálneho YAML nepreukazuje, čo platforma po expanzii vykoná; pipeline compiler alebo platform API má vedieť zobraziť resolved formu.

Validation prebieha na viacerých vrstvách. Syntax check potvrdí, že YAML sa dá parse-nuť. Schema alebo platform lint overí podporované keys. Policy kontroluje permissions, untrusted triggers a secret exposure. Dry-run alebo graph inspection overí dependencies a conditions. Až reálny run potvrdí runner, network a tool behavior.

Pipeline code je súčasťou trusted build inputs. Pull request, ktorý mení workflow, môže meniť spôsob testovania aj publication. Untrusted change nemá dostať release credentials skôr, než trusted revision workflowu znovu overí candidate. Oddelenie source change a privileged execution je kľúčová supply-chain hranica.

Pri troubleshootingu sa porovná source pipeline revision, resolved graph, runtime job metadata a artifacts. Zelený run podľa inej template generation nemôže byť automaticky použitý ako evidence pre nový graph.

## 12. Connected incident `REL-PAY-67`

Atlas root workflow používal reusable release workflow cez `@main`. Review diff v application repository menil iba `canary-percent: 2`. Po approval platform tím zmenil reusable workflow: pridal prefix cache restore, rozšíril `id-token: write` na workflow level a deployment condition z `refs/heads/main` na expression, ktorá bola true aj pre protected tag vytvorený fork-driven automation.

```text
reviewed root workflow SHA
+ mutable reusable ref
→ resolved graph drift po review
→ broader OIDC capability
→ poisoned cache restore
→ protected artifact publication
→ production deployment
```

Application PR approval nevidelo zmenu effective graphu. Runtime logs ukázali expected root SHA, pretože reusable dependency SHA sa nezachovávala v release recorde.

Root cause nebol iba mutable ref. Pipeline source review sa zamieňal za resolved execution review a transitive dependency generation nebola súčasťou subjectu.

## 13. Recovery a acceptance verdict

Containment zablokuje mutable workflow ref, revokuje affected workload sessions, zastaví artifacts/promotions a zachová actual job/identity/cache records. Recovery pinne last-known-good reusable SHA, vytvorí resolved graph, spustí sandbox forbidden tests a cold rebuild affected candidates.

Pipeline as Code contract je prijatý iba vtedy, keď:

```text
root aj transitive workflow/action dependencies sú immutable
+ inputs majú type a domain validation
+ variable/secret precedence je známa
+ resolved graph a permissions sú reviewovateľné
+ policy testuje trusted/untrusted/deploy paths
+ runtime job/runner/identity inventory sa koreluje
+ shared workflow update používa staged rollout
+ rollback na previous workflow generation je testovaný
+ untrusted event nemôže dosiahnuť production capability
+ second consumer používa rovnaký contract bez hidden override
```

## 14. Troubleshooting flow

Pri pipeline behavior, ktorý nezodpovedá source diffu, sleduj:

```text
root workflow SHA
→ includes/reusable/action revisions
→ inputs, defaults a variable precedence
→ conditions/matrix/inheritance
→ resolved graph a permissions
→ runner/executor selection
→ runtime jobs a issued identities
→ artifacts, gates a deployments
```

Competing hypotheses zahŕňajú mutable dependency, default change, variable shadowing, expression coercion, matrix expansion, policy gap, runtime runner mismatch alebo stale platform cache. Fetch source file-u samostatne nestačí; treba exact resolved generations.

## 15. Anti-patterny

### „YAML je reviewnutý, pipeline je bezpečná“

Runtime behavior závisí od dependencies, inputs, policy a platform evaluation.

### Reusable workflow cez mutable branch

Review a execution môžu používať iný source.

### Workflow-level broad permissions

Každý job zdedí capability, aj keď ju potrebuje iba publication alebo deployment.

### String inputs bez domain validation

Type coercion, path injection alebo unsupported environment môže zmeniť control flow.

### Shared workflow big-bang update

Jedna chyba zasiahne všetkých consumers bez bounded evidence a rollbacku.

## 16. Kontrolné otázky

1. Prečo source YAML nie je complete pipeline behavior?
2. Čo tvorí exact pipeline-definition subject?
3. Prečo pinning root workflow nestačí bez transitive inventory?
4. Aký rozdiel je medzi type validation a domain validation?
5. Ako variable precedence vytvára hidden override?
6. Čo preukazuje lint a čo nepreukazuje?
7. Ako policy nad resolved graphom dopĺňa source review?
8. Prečo `curl | sh` oslabuje integrity boundary?
9. Ako sa oddeľuje untrusted output od trusted deployment?
10. Čo sa zmenilo bez application diffu v `REL-PAY-67`?
11. Ako sa rolloutuje shared pipeline change?
12. Ako sa testuje forbidden fork-to-production graph?

## Glossary impact

Relevantné pojmy: Pipeline as Code, pipeline-definition subject, resolved workflow graph, reusable workflow generation, transitive pipeline dependency, typed workflow input, variable precedence, hidden override, permission graph, pipeline policy, sandbox execution, pipeline rollout ring, runtime graph read-back a workflow generation rollback.

## Primárne zdroje

- [GitHub Actions — Reusing workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [GitHub Actions — Workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub Actions — Security hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [GitLab CI/CD YAML syntax reference](https://docs.gitlab.com/ci/yaml/)
- [Open Policy Agent documentation](https://www.openpolicyagent.org/docs/)
- [SLSA specification](https://slsa.dev/spec/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Quality gates a approvals](quality-gates-and-approvals.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Reusable a parallel pipelines →](reusable-and-parallel-pipelines.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
