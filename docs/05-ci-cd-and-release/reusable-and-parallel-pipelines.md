# Reusable a parallel pipelines

Reusable pipeline je versionovaný provider–consumer contract, nie skopírovaný YAML fragment. Provider publikuje workflow capability s definovanými inputs, outputs, permissions, failure semantics a compatibility policy. Consumer vyberie konkrétnu provider generation a dodá domain inputs. CI platforma z týchto dvoch strán vytvorí resolved execution graph.

Paralelizácia potom rozdelí jeden exact candidate alebo artifact subject na viac jobs a znovu ich spojí do complete verdictu. Rýchlosť vzniká iba vtedy, keď fan-out units sú nezávislé, capacity je dostupná a fan-in vie rozlíšiť chýbajúci, canceled, duplicated alebo stale result. Viac jobs bez identity contractu môže zrýchliť false green.

## 1. Dominantný provider-to-fan-in model

```text
consumer intent a exact candidate
→ pinned reusable-workflow provider generation
→ typed inputs, outputs a permission contract
→ resolved graph a expected execution inventory
→ fan-out nad immutable subjectom
→ isolated parallel jobs
→ subject-bound reports a artifacts
→ identity-aware complete fan-in
→ consumer verdict a provider compatibility feedback
```

Provider zodpovedá za reusable contract a bezpečné defaults. Consumer zodpovedá za správne inputs, risk context a interpretáciu outputu. Platforma zodpovedá za scheduling a execution semantics. Tieto responsibilities sa nemajú skrývať za jedným `uses:` riadkom.

## 2. Exact reusable-workflow subject

```yaml
reusablePipelineSubject:
  consumer:
    repository: atlas/payments
    workflowSha: 18ab442
    candidateSha: d94e1c6
  provider:
    repository: atlas/platform-ci
    workflowPath: .github/workflows/test-artifact.yml
    workflowSha: 4d10f77
    contractVersion: 3.2.0
  inputs:
    artifactDigest: sha256:pay1000api
    platforms:
      - linux-amd64
      - linux-arm64
    shardsPerPlatform: 2
  expectedOutputs:
    - evidenceManifestDigest
    - overallVerdict
  expectedExecutions:
    - linux-amd64/0
    - linux-amd64/1
    - linux-arm64/0
    - linux-arm64/1
```

Provider tag alebo major alias môže byť convenient adoption channel, no decision record má zachovať resolved commit SHA. Contract version opisuje interface semantics; workflow SHA identifikuje exact implementation.

## 3. Contract inputs, outputs a failure semantics

Reusable workflow má definovať nielen input names, ale aj meaning a invariants. `artifact` môže znamenať tag, digest alebo local path; bez exact contractu consumers používajú odlišné identity. Output `passed=true` bez evidence reference je príliš slabý.

```yaml
on:
  workflow_call:
    inputs:
      artifact-digest:
        required: true
        type: string
      shard-count:
        required: true
        type: number
    outputs:
      evidence-manifest-digest:
        value: ${{ jobs.verdict.outputs.evidence-manifest-digest }}
      verdict:
        value: ${{ jobs.verdict.outputs.verdict }}
```

Source syntax preukazuje deklarovaný interface. Nepreukazuje domain validation, že input je skutočný digest ani že output vznikne pri partial failure. Provider musí dokumentovať states ako `PASS`, `FAIL`, `INCOMPLETE`, `INFRA_FAILURE` a `CANCELED`.

Input validation:

```bash
case "$ARTIFACT_DIGEST" in
  sha256:[0-9a-f][0-9a-f]*) ;;
  *) echo 'artifact-digest must be a sha256 reference' >&2; exit 2 ;;
esac

test "$SHARD_COUNT" -ge 1
test "$SHARD_COUNT" -le 32
```

Pattern check preukazuje formát, nie existenciu artifactu alebo trust registry. Provider má resolve-núť digest v allowed registry a overiť signature/provenance podľa contractu.

## 4. Provider compatibility a versioning

Reusable workflow má vlastné public API. Breaking changes zahŕňajú odstránený input, zmenu defaultu, nový required permission, inú output schema, nové runner requirements alebo zmenu failure semantics. Provider potrebuje deprecation window a consumer inventory.

```text
provider candidate
→ contract tests
→ internal canary consumers
→ compatibility diff
→ versioned publication
→ opt-in adoption
→ observed consumer outcomes
→ old generation support a retirement
```

Mutable `@main` obchádza lifecycle. Protected major tag môže smerovať na compatible updates, ale consumer musí mať rollback na previous resolved SHA a monitorovať actual adoption.

## 5. Parallel fan-out design

Work sa delí podľa explicitnej dimension: platforma, test shard, region alebo package. Delenie má zachovať jeden immutable subject a deterministic partitioning.

```python
# deterministic test sharding by stable test ID
import hashlib
import os

shard = int(os.environ["SHARD_INDEX"])
count = int(os.environ["SHARD_COUNT"])

def assigned(test_id: str) -> bool:
    value = int(hashlib.sha256(test_id.encode()).hexdigest(), 16)
    return value % count == shard
```

Deterministic mapping preukazuje, že rovnaký test ID a shard count vedú k rovnakému shardu. Nepreukazuje complete discovery testov ani balanced duration. Provider má uložiť discovered test inventory a per-shard assignment.

## 6. Expected inventory a complete fan-in

Fan-in porovná expected tuples s received evidence. Nesmie používať „všetky jobs, ktoré existujú v API“ ako expected set, pretože condition bug môže job nevytvoriť.

```json
{
  "subjectDigest": "sha256:pay1000api",
  "expected": [
    "linux-amd64/0",
    "linux-amd64/1",
    "linux-arm64/0",
    "linux-arm64/1"
  ],
  "received": [
    {"id":"linux-amd64/0","result":"PASS","subjectDigest":"sha256:pay1000api"},
    {"id":"linux-amd64/1","result":"PASS","subjectDigest":"sha256:pay1000api"},
    {"id":"linux-arm64/0","result":"PASS","subjectDigest":"sha256:pay1000api"}
  ]
}
```

```bash
jq -e '
  (.expected | sort) as $e |
  ([.received[].id] | sort) as $r |
  $e == $r and
  all(.received[]; .result == "PASS" and .subjectDigest == $.subjectDigest)
' fan-in.json
```

Exit `0` preukazuje complete ID set, pass results a subject equality podľa JSON. Nepreukazuje authenticity reports ani correctness test oracle-u. Reports majú integrity/provenance a raw references.

## 7. Parallelism versus concurrency a capacity

Parallel graph neznamená, že jobs bežia súčasne. Runner quotas, environment locks, package registry limits alebo database test capacity môžu vytvoriť queue. Príliš veľa shards zvýši setup, artifact download a fan-in overhead.

Relevantné metrics:

```text
queue duration
+ critical-path duration
+ shard duration distribution
+ setup/download overhead
+ runner utilization a saturation
+ cancellation waste
+ fan-in wait
```

Optimalizuje sa time to useful verdict, nie maximálny počet boxes v UI. Test sharding má vyvažovať observed duration a pritom zachovať deterministic assignment a history.

## 8. Shared dependencies a isolation

Parallel jobs môžu používať shared database, test tenant alebo external sandbox. Bez isolation vzniká cross-shard interference. Každá execution unit má stable namespace odvodený od candidate a shard identity.

```bash
safe_id="$(printf '%s-%s-%s' "$CANDIDATE_SHA" "$PLATFORM" "$SHARD_INDEX" | sha256sum | cut -c1-16)"
printf 'test_namespace=ci-%s\n' "$safe_id"
```

Hash vytvára bounded locator. Nepreukazuje, že provisioning system zabráni collision alebo že cleanup odstráni resources. Ownership labels a independent sweeper sú stále potrebné.

## 9. Cancellation, fail-fast a evidence

`fail-fast: true` môže skrátiť feedback, ale canceled shards už neposkytnú complete failure inventory. Pre release gate môže byť správne zastaviť drahé jobs po first deterministic failure; pre flaky diagnosis alebo compatibility matrix môže byť vhodnejšie dokončiť všetky.

Policy má rozlíšiť:

```text
first blocking failure
→ merge verdict môže byť DENY

remaining canceled shards
→ evidence inventory je intentionally incomplete
→ nesmie sa reuse-núť pre inú otázku
```

Superseded candidate cancellation má zachovať first-failure reports a označiť run `SUPERSEDED`, nie `PASS` ani `FAIL` pre current candidate.

## 10. Reusable security boundary

Provider workflow môže dostať secrets od consumer-a alebo používať OIDC capability. Contract má explicitne uviesť required permissions a nesmie automaticky dediť všetky consumer secrets. Untrusted inputs sa nesmú interpolovať do shell, path, runner labelu alebo environment name bez validation.

```text
consumer grants minimum capability
→ provider validates inputs
→ privileged job nepoužíva untrusted source-controlled executable
→ outputs sú bounded data, nie commands
```

Provider update je supply-chain change. Compromise platform-ci repository môže zasiahnuť všetkých consumers, preto sú potrebné branch protection, signed reviews, pinning a staged adoption.

## Ako fungujú fan-out, shardy a fan-in

Parallel pipeline rozdelí prácu na viac jobs alebo matrix combinations. **Fan-out** vytvorí shards; **fan-in** zhromaždí ich outputs a rozhodne o complete výsledku.

```text
candidate
→ linux/windows/macos alebo test shard 1..N
→ per-shard result a artifact
→ fan-in completeness check
→ aggregate verdict
```

Zelený agregátor nie je dôveryhodný, ak nevie, koľko shards sa očakávalo. Potrebuje **shard manifest** obsahujúci exact inventory, napríklad platform, dependency version a test partition.

Matrix expression môže vytvoriť nula jobs pri chybnom filtri. Pipeline potom vyzerá green, hoci required platform sa nevykonala. Fan-in preto porovná expected a observed shard IDs.

Fail-fast zruší ostatné jobs po prvom failure. Šetrí čas, ale môže znížiť diagnostic evidence. Pri compatibility matrix môže byť vhodné nechať všetky shards dobehnúť a uložiť kompletný failure obraz.

Reusable workflow je versionovaný contract s inputs, outputs, secrets a permissions. Caller musí pinovať verziu a chápať defaults. Zmena template môže zmeniť runner image alebo gate behavior pre mnoho repositories naraz.

Outputs z parallel jobs potrebujú unikátne names a checksums. Ak všetky shards uploadnú `report.xml`, posledný môže prepísať ostatné. Aggregate report bez jedného shardu je `INCOMPLETE`, nie legitímne nižšie coverage.

## 11. Connected incident `REL-PAY-68`

Atlas shared workflow `test-artifact.yml@v3` rozbalil matrix podľa platforms a shard count. Provider release `v3.2.1` zmenil expression: arm64 shard `1` sa nevytvoril pri `fail-fast=false`, pretože podmienka používala index ako boolean. Expected inventory sa generovalo z actual matrix jobs, takže fan-in zostal green.

Zároveň provider premenoval output `evidence-digest` na `evidence-manifest-digest`, ale consumer používal fallback empty string a release job zobral latest artifact podľa tagu. Výsledok:

```text
mutable major provider ref
→ resolved contract drift
→ missing arm64 shard
→ dynamic expected inventory
→ empty output fallback
→ mutable artifact lookup
→ release manifest s nesprávnym platform graphom
```

Production amd64 fungovala. Arm64 nodes stiahli manifest s binary, ktorá nemala potrebný native module. 14 Pods vstúpilo do crash loopu.

Root cause bol provider–consumer contract a incomplete fan-in, nie iba jedna matrix expression.

## 12. Recovery a acceptance verdict

Containment pinne previous provider SHA, zastaví promotion a inventarizuje affected consumers/artifacts. Recovery fixne provider, pridá static expected inventory, output schema validation a platform-specific artifact tests. Consumer pinne exact provider SHA a release manifest uvádza per-platform digests.

Reusable/parallel contract je prijatý iba vtedy, keď:

```text
provider generation a contract version sú explicitné
+ inputs/outputs/permissions majú schema a semantics
+ expected fan-out vzniká pred runtime expansion
+ každý result patrí rovnakému immutable subjectu
+ fan-in odmieta missing, duplicate, canceled a infra results
+ shared dependencies sú isolated
+ provider rollout je staged a reversible
+ untrusted input nemôže zmeniť runner/deploy capability
+ missing platform shard je forbidden
+ second consumer prejde compatibility testom
```

## 13. Troubleshooting flow

Pri reusable workflow incidente sleduj:

```text
consumer source a inputs
→ resolved provider SHA a contract version
→ defaults/permissions
→ resolved matrix a expected inventory
→ runner scheduling a isolation
→ per-unit subject/report
→ fan-in logic a outputs
→ consumer interpretation
→ release artifact graph
```

Competing hypotheses môžu byť provider drift, input coercion, output rename, matrix condition, missing runner capacity, shared-test interference, canceled shard, stale artifact lookup alebo consumer fallback. Provider log bez consumer resolved inputs je neúplný dôkaz.

## 14. Anti-patterny

### Reusable workflow ako copy-paste reduction iba

Bez contractu centralizácia iba centralizuje blast radius.

### Expected inventory z actual jobs

Job, ktorý condition bug nevytvorí, sa nikdy neobjaví ako missing.

### Empty output fallback na latest artifact

Missing identity sa nesmie nahradiť mutable locatorom.

### Maximálny počet shards

Setup a queue overhead môžu critical path predĺžiť a zvýšiť failure surface.

### Consumer bez rollbacku provider generation

Shared workflow update potom nemá bounded recovery.

## 15. Kontrolné otázky

1. Čo tvorí provider–consumer contract reusable pipeline?
2. Prečo contract version a workflow SHA nie sú to isté?
3. Ako deterministic sharding pomáha a čo negarantuje?
4. Odkiaľ má vzniknúť expected execution inventory?
5. Čo musí fan-in overiť okrem job statusu?
6. Prečo viac shards nemusí byť rýchlejších?
7. Ako sa izolujú shared test dependencies?
8. Kedy je fail-fast vhodný a aký evidence stráca?
9. Ako provider update mení supply-chain boundary?
10. Čo sa pokazilo v `REL-PAY-68`?
11. Prečo empty output fallback zhoršil incident?
12. Ako sa testuje second-consumer compatibility?

## Glossary impact

Relevantné pojmy: reusable workflow contract, provider generation, consumer generation, contract version, resolved provider SHA, typed input, output schema, expected execution inventory, deterministic sharding, matrix tuple, identity-aware fan-in, shared dependency isolation, fail-fast evidence a provider rollout ring.

## Primárne zdroje

- [GitHub Actions — Reusing workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [GitHub Actions — Matrix strategy](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs)
- [GitLab Docs — CI/CD components](https://docs.gitlab.com/ci/components/)
- [GitLab Docs — Directed acyclic graph](https://docs.gitlab.com/ci/directed_acyclic_graph/)
- [SLSA specification](https://slsa.dev/spec/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Pipeline as Code](pipeline-as-code.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Artifact versioning →](artifact-versioning.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
