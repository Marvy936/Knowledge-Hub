# Continuous Integration

Continuous Integration je mechanizmus, ktorým tím často skladá malé source changes do jednej spoločnej línie a pre každý potenciálny výsledok merge-u vytvára nový, reprodukovateľný a auditovateľný integračný verdict. CI preto nie je synonymum pre „server spustil testy“. Základnou jednotkou je exact integration candidate: konkrétny source revision, konkrétny target revision, konkrétna workflow generation a všetky build inputs, z ktorých vznikol overovaný tree a artifact.

Najčastejší omyl vzniká vtedy, keď sa zelený branch pipeline považuje za dôkaz budúceho merge-u. Branch mohla byť testovaná proti staršiemu `main`, iný pull request medzitým zmenil dependency graph a reusable workflow alebo build image sa mohli posunúť. Platný CI verdict musí preto patriť presnému candidate-u, nie iba názvu branch-e alebo pull requestu.

## 1. Dominantný candidate-to-verdict model

CI sa má čítať ako reťaz identity, execution a evidence boundaries. Najprv sa určí tree, ktorý by sa skutočne integroval. Potom sa v čistom a deklarovanom prostredí vyriešia dependencies, vytvorí build, spustí complete verification inventory a publikuje immutable artifact. Až fan-in nad všetkými required výsledkami môže vydať merge verdict.

```text
source change a current target
→ exact synthetic merge candidate
→ trusted checkout a pinned inputs
→ resolved build/test execution graph
→ compile, test, contract a policy evidence
→ immutable artifact a provenance
→ complete candidate-bound verdict
→ merge alebo oprava
→ healthy mainline
→ escaped defect späť do dependency/test/policy modelu
```

Každý krok má inú failure semantics. Checkout môže byť neúplný, build môže používať stale cache, test shard môže chýbať a artifact môže byť po testoch rebuildnutý. „Pipeline succeeded“ je dôveryhodné iba vtedy, keď systém preukáže identitu a úplnosť celého chainu.

## 2. Exact integration subject

Názov PR ani source SHA samostatne nestačia. CI record má zachovať minimálne:

```yaml
integrationSubject:
  repository: atlas/payments
  sourceRef: refs/pull/481/head
  sourceSha: 8e21b8d
  targetRef: refs/heads/main
  targetSha: 53d92af
  candidateSha: d94e1c6
  workflowPath: .github/workflows/ci.yml
  workflowSha: 18ab442
  reusableWorkflowShas:
    - atlas/platform-ci@4d10f77
  buildImageDigest: sha256:build420
  dependencyLockDigest: sha256:lock192
  expectedEvidence:
    - compile
    - unit-0
    - unit-1
    - integration-postgres
    - event-contract
    - sast
    - artifact-policy
```

`candidateSha` je výsledný merge state, nie iba source branch. `workflowSha` a reusable workflow revisions sú súčasťou subjectu, pretože zmena execution policy môže zmeniť verdict bez zmeny application source. Expected evidence inventory bráni tomu, aby chýbajúci shard alebo scanner zmizol z fan-inu a ticho vytvoril green status.

## 3. Praktické vytvorenie merge candidate-u

Jednoduchý lokálny model možno reprodukovať v disposable clone. Pipeline checkout-ne target revision a vytvorí presne merge, ktorý chce overovať:

```bash
git fetch --no-tags origin "$TARGET_SHA" "$SOURCE_SHA"
git checkout --detach "$TARGET_SHA"
git merge --no-ff --no-edit "$SOURCE_SHA"

candidate_sha="$(git rev-parse HEAD)"
candidate_tree="$(git rev-parse HEAD^{tree})"
printf 'candidate_sha=%s\ncandidate_tree=%s\n' "$candidate_sha" "$candidate_tree"
```

Výstup preukazuje, ktorý commit a tree vznikli v tejto clone. Nepreukazuje, že target sa od začiatku jobu neposunul ani že branch protection prijme práve tento candidate. Merge queue alebo server-side merge-result pipeline musí preto pred merge-om znovu potvrdiť target SHA a invalidovať starší verdict.

Na konci jobu je vhodné uložiť subject ako machine-readable artifact:

```bash
jq -n \
  --arg source "$SOURCE_SHA" \
  --arg target "$TARGET_SHA" \
  --arg candidate "$candidate_sha" \
  --arg workflow "$WORKFLOW_SHA" \
  '{sourceSha:$source,targetSha:$target,candidateSha:$candidate,workflowSha:$workflow}' \
  > integration-subject.json
```

Validný JSON ešte nepreukazuje pravdivosť hodnôt. Pipeline musí získavať SHA z trusted event contextu a lokálne overiť, že checkout HEAD zodpovedá deklarovanému candidate-u.

## 4. Mainline ako spoločný contract

`main` je najnovší akceptovaný integračný stav. Nemusí byť automaticky vystavený používateľom, ale musí zostať dôveryhodným vstupom pre ďalší build, delivery a release. Dlhodobo broken main ničí význam required checks: ďalšie branches sa testujú proti známemu chybnému targetu a každé zlyhanie má viac možných príčin.

Healthy-main contract obsahuje reprodukovateľný build, complete required evidence, immutable artifact identity a ownera pre okamžitú recovery. Keď authoritative main pipeline zlyhá, tím má zastaviť ďalšie rizikové merges, identifikovať first bad integration a zvoliť revert alebo minimálny roll-forward. Oprava nekončí zeleným rerunom; control, ktorý defect prepustil, sa musí zmeniť.

## 5. Small batches a merge queue

Malé changes znižujú počet assumptions a uľahčujú review, diagnosis aj recovery. Veľká capability sa môže skladať cez backward-compatible schema, branch by abstraction a feature flag, ale hidden code stále patrí do build, security a compatibility contractu.

Merge queue rieši stale-green race medzi paralelnými PRs:

```text
approved change
→ queue position
→ candidate proti aktuálnemu predecessorovi
→ complete required evidence
→ atomic merge
→ invalidácia nasledujúcich candidate-ov pri zmene predecessor state-u
```

Queue nepreukazuje správnosť test oracle-u. Ak event compatibility test nepokrýva historické payloads, candidate môže byť správne identifikovaný a stále chybne akceptovaný.

## 6. Reprodukovateľný build a explicitné inputs

Source nie je jediný build input. Artifact bytes ovplyvňujú lockfiles, compiler alebo SDK, build image, architecture, flags, locale, timezone, generated-code tools, base image a network-fetched dependencies. Každý mutable input oslabuje schopnosť vysvetliť, prečo dva buildy rovnakého source vytvorili iné výsledky.

Atlas používa digest-pinned build image a cold workspace. Build manifest zachováva všetky relevantné generations:

```bash
git rev-parse HEAD > build-candidate.txt
docker image inspect "$BUILD_IMAGE" --format '{{index .RepoDigests 0}}' > build-image.txt
sha256sum package-lock.json > dependency-lock.txt
uname -m > build-architecture.txt
```

Tieto výstupy preukazujú observed inputs jedného runnera. Nepreukazujú, že remote registry tag nebol resolve-nutý skôr na iný digest ani že package manager nepoužil undeclared mirror. Trusted build má preto používať digest references, lockfiles a obmedzený network policy.

## 7. Build once a immutable artifact

Dôveryhodný model je:

```text
candidate C
→ build immutable artifact A
→ test a policy nad A
→ publish A s provenance
→ promotion používa presne A
```

Rebuild po testoch vytvorí nový supply-chain event. Aj pri rovnakom candidate SHA sa mohol zmeniť base image, compiler alebo dependency mirror. Artifact-dependent checks majú preto čítať output z autoritatívneho build jobu.

Príklad multi-platform publication:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --provenance=true \
  --sbom=true \
  --tag "registry.atlas.example/payments:${candidate_sha}" \
  --push .

published_digest="$(crane digest "registry.atlas.example/payments:${candidate_sha}")"
printf 'published_digest=%s\n' "$published_digest"
```

Digest preukazuje content identity publikovaného image indexu. Nepreukazuje, že oba platform manifests prešli testami, že provenance používa trusted builder ani že production neskôr spustí ten istý platform digest. Evidence manifest musí uviesť index aj per-platform subjects.

## 8. Complete evidence a verdict classes

Fan-in nesmie interpretovať absenciu ako pass. Atlas generuje expected manifest a porovná ho so skutočnými reports:

```bash
jq -e '
  (.expected | sort) as $expected |
  (.received | sort) as $received |
  $expected == $received
' evidence-manifest.json
```

Exit code `0` preukazuje iba rovnosť dvoch zoznamov v manifeste. Nepreukazuje validitu samotných reports. Každý report potrebuje schema, producer identity, candidate subject a výsledok oracle-u.

CI verdict rozlišuje:

- **PASS** — všetky required controls sa vykonali nad správnym subjectom a splnili oracle;
- **CHANGE_FAILURE** — candidate porušil compile, test, contract alebo policy;
- **INCOMPLETE** — chýba required job, report, shard alebo artifact;
- **TOOL_OR_INFRA_FAILURE** — control sa nedal dôveryhodne vykonať;
- **CANCELED_OR_SUPERSEDED** — výsledok už nereprezentuje aktuálny candidate.

Retry je legitímny iba pre klasifikovaný transient failure. First-attempt evidence sa zachová. Fail-then-pass nie je čistý first-pass verdict a patrí do flaky alebo infrastructure reliability metrík.

## 9. Runner a credential trust boundaries

PR code je untrusted input. Môže meniť scripts, čítať filesystem, skúšať metadata endpoints alebo zapisovať do cache. Preto Atlas oddeľuje:

```text
untrusted verification
→ ephemeral runner, žiadne production secrets, read-only source

trusted artifact build
→ reviewed workflow, candidate namespace, short-lived publication identity

signing a attestation
→ samostatná identity, read immutable digest

deployment
→ environment-scoped identity bez spúšťania PR source
```

Container executor nie je automatická hard security boundary. Privileged mounts, shared host kernel, persistent workspace, Docker socket a broad egress môžu spojiť untrusted job s ďalšími runs. Runner sa klasifikuje podľa identity, persistence, networku a oprávnení, nie iba podľa executor labelu.

## 10. Connected incident `REL-PAY-66`

Atlas Payments pripravoval release `payments 10.0`. PR A menil `SettlementCreated` schema a generated client. PR B menil serializer dependency. Oba pipelines boli zelené proti `main=M1`. PR B sa mergol a vytvoril `M2`; PR A sa následne mergol bez merge-result revalidácie.

Persistent runner navyše obsahoval generated client zo staršieho jobu. Test jobs pracovali s warm workspace, ale release build prebehol v inom jobe a image po testoch rebuildol. Výsledok bol:

```text
A/M1 evidence
+ B/M1 evidence
→ B merged ako M2
→ A merged bez candidate A+M2 testu
→ warm generated client maskoval missing build edge
→ release artifact vznikol z cold rebuild-u
→ artifact bytes nemali rovnaký evidence subject
```

`main` sa tváril zeleno, no payment worker nedokázal čítať nový enum representation. 8 412 settlement events ostalo v retry backlogu a 73 operations prešlo do manual reconciliation.

Root cause nebol jeden zlý test. Authority chain bol neúplný: branch status nahradil candidate verdict, workspace bol hidden build input a tested output nebol publikovaný artifact.

## 11. Recovery a acceptance

Containment najprv zastaví merges a consumers nového eventu, zachová candidate/workflow/cache/runner evidence a identifikuje exact artifacts. Recovery potom vytvorí jeden nový candidate nad current main, explicitne regeneruje client, vykoná historical event replay, publikuje build-once artifact a obnoví backlog s idempotentným consumerom.

CI blok je prijatý iba vtedy, keď:

```text
current target + source vytvoria evidovaný candidate
+ cold build vytvorí jeden immutable artifact
+ expected a received evidence inventory sú rovnaké
+ reports patria candidate-u a artifactu
+ untrusted job nevie čítať/publikovať trusted credentials
+ merge pri zmene targetu invaliduje starý verdict
+ clean runner a warm runner vytvoria rovnaký contract outcome
+ second PR combination prejde
+ forbidden stale-candidate merge je odmietnutý
```

Green pipeline bez týchto väzieb je iba execution status.

## 12. Troubleshooting flow

Pri CI incidente postupuj od identity, nie od náhodného rerunu:

```text
merge alebo build symptom
→ source/target/candidate/workflow identity
→ checkout tree a declared inputs
→ runner, workspace a cache generation
→ resolved DAG a expected evidence
→ artifact subject a provenance
→ report validity a fan-in verdict
→ merge/mainline state
```

Competing hypotheses môžu byť stale target, wrong checkout, missing generated edge, poisoned cache, architecture drift, chýbajúci shard, analyzer crash, rebuild po testoch alebo flaky oracle. Každá hypotéza má diskriminačný observation point. Rerun bez zachovania first attemptu môže zničiť práve evidence potrebné na rozlíšenie.

## 13. Anti-patterny

### Branch green ako merge proof

Branch výsledok proti starému targetu nepreukazuje budúci integrated tree.

### Cache ako hidden source of truth

Cache miss má znížiť výkon, nie zmeniť correctness. Ak cold build zlyhá, dependency graph je neúplný.

### Rebuild pred publication

Nový build nie je artifact, ktorý prešiel testami, aj keď používa rovnaký source SHA.

### Privileged persistent runner pre PRs

Shared workspace, credentials a host access umožňujú cross-run contamination a supply-chain compromise.

### Rerun-until-green

Opakovanie bez failure classification mení intermittency na false confidence.

## 14. Kontrolné otázky

1. Prečo source SHA nie je úplný integration subject?
2. Aký rozdiel je medzi source, target a candidate SHA?
3. Kedy sa predchádzajúci CI verdict invaliduje?
4. Čo rieši merge queue a čo nerieši?
5. Ktoré build inputs musia byť explicitné?
6. Prečo build-once podporuje dôveryhodnú promotion?
7. Ako sa odlišuje missing evidence od passu?
8. Čo preukazuje image index digest a čo nepreukazuje?
9. Prečo container runner nemusí byť bezpečný pre untrusted PR?
10. Čo bolo authority root cause incidentu `REL-PAY-66`?
11. Ako sa overí forbidden stale-candidate path?
12. Akú zmenu control modelu musí vyvolať escaped defect?

## Glossary impact

Relevantné pojmy: integration candidate, source SHA, target SHA, candidate SHA, workflow generation, expected evidence inventory, merge-result pipeline, merge queue, cold build, hidden build input, build-once, immutable artifact, candidate-bound report, incomplete verdict, superseded run, runner trust boundary a healthy-main contract.

## Primárne zdroje

- [Git documentation — git merge](https://git-scm.com/docs/git-merge)
- [GitHub Docs — About merge queues](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue)
- [GitHub Docs — Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [SLSA specification](https://slsa.dev/spec/)
- [OCI Image Specification](https://github.com/opencontainers/image-spec)
- [Docker Docs — Build attestations](https://docs.docker.com/build/metadata/attestations/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Chaos testing](../04-testing-and-quality/chaos-testing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Continuous Delivery →](continuous-delivery.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
