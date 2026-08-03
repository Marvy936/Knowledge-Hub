# CI pre ML code, data a pipelines

Continuous Integration pre ML nemá v každom pull requeste znovu vytrénovať produkčný model. Jej úlohou je vytvoriť dôveryhodného integračného kandidáta: overiť source code, data a feature contracts, compiled pipeline, component images, training a inference interfaces, package integrity, security a lineage tak, aby zmena mohla bezpečne vstúpiť do drahšieho evaluation a delivery procesu.

Klasická software CI často predpokladá, že repository obsahuje väčšinu správania aplikácie. ML systém má významné správanie aj v datasetoch, fitted artifacts, feature pipelines, notebookoch, runtime images a external stores. Zelené unit testy preto nestačia. Naopak, spustenie full trainingu nad produkčnými dátami pri každom commite je pomalé, drahé, môže vytvárať data-access riziko a stále nemusí testovať správnu deployment generation.

V incidente `MLOPS-PAY-92` Atlas CI overila lint, type checks a tri unit testy training code. Pipeline compiler sa nespustil, takže review nevidelo, že generated component stále používa starý image tag. Tiny training smoke použil synthetic dáta bez missing values, zatiaľ čo produkčný dataset contract povoľoval nullable merchant category. Model package sa síce vytvoril, ale neprešiel fresh-environment inference testom. CI označila commit za green a downstream workflow spustil drahý distributed training, ktorý zlyhal až po hodine.

## 1. Dominantný ML CI lifecycle

ML CI začína change subjectom a končí immutable candidate evidence bundle. Každý gate má vlastný účel a nesmie tvrdiť viac, než preukázal.

```text
pull request a exact changed surfaces
→ source/static checks
→ data a feature contract checks
→ component a pipeline compilation
→ deterministic tiny training/inference smoke
→ package a artifact validation
→ security, permissions a supply-chain checks
→ immutable CI evidence bundle
→ eligibility pre full training alebo promotion workflow
```

CI verdict nepreukazuje production model quality. Preukazuje, že candidate je technicky a zmluvne pripravený na ďalšiu fázu. Full evaluation, promotion a rollout zostávajú oddelené gates.

## 2. Exact CI subject

„PR #412 je zelené“ nestačí. Exact CI subject zahŕňa repository commit, workflow generation, actions a reusable workflows, runner image, resolved dependencies, test data fixtures, compiled IR digest, component images, permissions a output artifacts.

```yaml
ci_subject: MLOPS-PAY-CI-2026-08-03-412
repository_commit: 36042cccbf9c0786e833955c090d848993117754
workflow_path: .github/workflows/ml-ci.yml
workflow_commit: 36042cccbf9c0786e833955c090d848993117754
runner_image: ubuntu-24.04
python_lock_digest: sha256:1aa3...9910
fixture_manifest: sha256:72bd...0f11
compiled_pipeline_digest: sha256:672a...a103
component_images:
  validate: registry.example/ml/validate@sha256:1c4e...bb01
  train: registry.example/ml/train@sha256:5f7a...91d2
permissions:
  contents: read
  packages: write
  id-token: write
forbidden:
  - production_dataset_write
  - registry_alias_mutation
  - production_deployment_mutation
```

Workflow file je code a patrí do subjectu. Ak reusable workflow používa mutable branch, CI semantics sa môžu zmeniť bez zmeny application repository. Externé actions majú byť pinované na reviewed commit SHA alebo inú dôveryhodnú immutable generation.

## 3. Change classification a test selection

Nie každá zmena potrebuje rovnaké testy, ale selection musí byť deterministická a auditovateľná. Zmena training algorithm vyžaduje unit, tiny training, checkpoint a package tests. Zmena feature definition vyžaduje point-in-time a online/offline parity fixtures. Zmena pipeline componentu vyžaduje compilation a container-contract test. Zmena workflowu vyžaduje permissions a generated plan review.

Path filter je optimalizácia, nie proof. Shared library, base image alebo schema dependency môže ovplyvniť viac surfaces než ukazuje changed path. CI má preto vytvoriť resolved dependency impact, nie iba `git diff --name-only`.

```text
changed file
→ owned component alebo contract
→ reverse dependencies
→ required test suites
→ skipped suite + explicit dôvod
```

Skips musia byť súčasťou evidence bundle. Neviditeľne nebežiaci test je horší než červený test, pretože green verdict vytvára falošnú istotu.

## 4. Source a static checks

Lint, formatting, type checking a unit tests zostávajú základom. Pri ML code majú testovať aj shape, dtype, missing-value behavior, ordering, threshold semantics a deterministic transformations. Notebook nie je výnimka: production logic má byť extrahovaná do testovateľných modulov a notebook execution má mať pinned environment.

```bash
ruff check src tests pipelines
mypy src pipelines
pytest -q tests/unit tests/contracts
python -m compileall src pipelines
```

Static check nepreukazuje runtime dependency compatibility. Import smoke v clean environment zachytí chýbajúci package, ale nepreukazuje training correctness. Každý výsledok sa interpretuje v správnej hranici.

## 5. Data contract CI

CI nemá kopírovať produkčné dáta bez governance. Používa malé anonymizované alebo syntetické fixtures, ktoré reprezentujú schema, edge cases a failure modes. Contract checks overujú required columns, logical types, ranges, nullability, uniqueness, event-time constraints, label maturity a forbidden future fields.

```python
def test_payment_feature_contract(sample_frame):
    assert list(sample_frame.columns) == EXPECTED_ORDER
    assert sample_frame["amount_eur"].ge(0).all()
    assert sample_frame["merchant_id"].notna().all()
    assert sample_frame["event_time"].le(sample_frame["prediction_time"]).all()
```

Happy-path fixture nestačí. CI má obsahovať missing values, unknown categories, duplicate entity-time rows, late events, empty partitions a timezone boundary. Contract test stále nepreukazuje, že live source dodáva správnu distribúciu; to patrí do integration a production monitoring vrstvy.

Dataset version alebo query plan môže byť príliš veľký pre PR job. Vtedy CI overí schema a query compilation nad representative fixture a full data validation spustí ako oddelený, identity-bound gate pred trainingom.

## 6. Feature logic a parity fixtures

Feature transformácie potrebujú golden fixtures s inputom, event time, expected value a explanation. Golden value nemá byť ručne prepísané číslo bez provenance. Fixture generation má byť reviewed a versionovaná.

```yaml
case_id: merchant_velocity_late_event
entity: merchant-42
prediction_time: 2026-08-03T10:00:00Z
events:
  - event_time: 2026-08-03T09:30:00Z
    amount_eur: 20
  - event_time: 2026-08-03T10:05:00Z
    amount_eur: 900
expected:
  tx_count_1h: 1
  amount_sum_1h: 20
```

Rovnaká fixture sa má vykonať cez offline transformáciu aj online implementation. Equality môže byť exact alebo tolerance-based podľa typu. Parity test pre niekoľko fixtures nepreukazuje population-wide consistency, ale zachytí semantic drift v ordering, units, null handling a point-in-time boundary.

## 7. Pipeline compilation a graph checks

Pipeline source sa v CI skompiluje do IR. Generated graph sa validuje proti policy: pinned images, explicit resources, service accounts, cache policy, artifact outputs a absence production credentials. Diff compiled IR je review artifact.

```bash
python -m pipelines.compile --output dist/risk-training.yaml
python scripts/validate_pipeline_ir.py dist/risk-training.yaml
sha256sum dist/risk-training.yaml > dist/risk-training.sha256
```

Test má zlyhať, ak source zmena neočakávane mení graph alebo ak generated IR nie je synchronizovaný. Compiler success nepreukazuje, že backend run prejde admission alebo scheduling; server-side dry run alebo ephemeral namespace integration pridáva ďalší dôkaz.

## 8. Component container contract

Každý pipeline component je deployment unit. CI vytvorí image, spustí ho s contract fixture, overí exit codes, output paths, manifest a non-root/security settings. Mutable tag sa môže publikovať ako convenience, ale candidate identity je digest.

```bash
docker buildx build \
  --platform linux/amd64 \
  --tag registry.example/ml/train:pr-412 \
  --provenance=true \
  --sbom=true \
  --push .

docker buildx imagetools inspect registry.example/ml/train:pr-412
```

Po push-i sa digest zapíše do evidence bundle a compiled pipeline sa renderuje s digestom. Tag samotný sa nesmie preniesť do promotion manifestu.

## 9. Tiny training smoke

Tiny training overí executable path od fixture datasetu cez preprocessing, model fit, checkpoint a package. Dataset je malý a počet steps bounded. Cieľom nie je kvalita, ale interface a state transition.

```bash
python -m training.run \
  --config tests/config/tiny-train.yaml \
  --dataset tests/fixtures/tiny.manifest.json \
  --max-steps 3 \
  --output /tmp/candidate
```

Acceptance kontroluje finite loss, expected step count, complete checkpoint keys, model signature a fresh-process load. Fixný expected metric môže byť krehký naprieč hardware alebo library generations; vhodnejšie je overiť invariants a tolerance, pričom environment zostáva pinovaný.

Distributed smoke s dvoma local processes overí initialization a sampler partitioning. Full multi-node performance a convergence patria mimo PR CI.

## 10. Inference a package compatibility

Candidate package sa načíta v čistom environment-e, nie v workspace po trainingu. Test používa declared signature, representative requests a forbidden schemas. Tým zachytí undeclared local files, transitive dependencies, path assumptions a serialization failures.

```bash
python -m venv /tmp/fresh-env
/tmp/fresh-env/bin/pip install -r dist/model/requirements.lock
/tmp/fresh-env/bin/python tests/package/load_and_predict.py dist/model
```

Ak production používa container, CI spustí image a pošle protocol-level request. HTTP 200 nestačí; response schema, model digest header, request correlation a expected prediction invariants musia sedieť.

## 11. Evaluation boundary v CI

CI môže spustiť malý deterministic regression dataset a porovnať candidate s baseline. Tento gate chráni pred zjavnou regresiou, ale nie je production promotion verdict. Dataset môže byť príliš malý, historický alebo bez mature labels.

Metric threshold musí mať dataset a evaluator identity. `accuracy >= 0.90` bez cohortov a guardrails je slabý gate. Better contract uvádza primary metric, segment constraints, forbidden degradation a uncertainty alebo sample-size minimum.

Full model evaluation môže byť downstream workflow, ktorý sa spustí po green CI a používa immutable candidate bundle. Výsledok sa pripojí k rovnakému lineage chainu, nie k mutable branch name.

## 12. Workflow artifacts a evidence bundle

GitHub Actions artifacts sú vhodné na prenesenie compiled IR, reports a test logs medzi jobs alebo na krátkodobé review. Nie sú automaticky production artifact store. Majú retention a workflow-run identity a môžu byť odstránené.

Finálny CI bundle obsahuje manifest s checksumami:

```json
{
  "repository_commit": "36042ccc...",
  "workflow_run_id": 30807589337,
  "compiled_pipeline": "sha256:672a...a103",
  "images": {
    "train": "sha256:5f7a...91d2"
  },
  "fixture_manifest": "sha256:72bd...0f11",
  "reports": {
    "unit": "sha256:11aa...",
    "contracts": "sha256:22bb...",
    "tiny_training": "sha256:33cc..."
  }
}
```

Bundle sa podpíše alebo attesuje podľa supply-chain modelu a uloží do durable store, ak je promotion input. Download z CI cache alebo lokálny workspace nie je authoritative read-back.

## 13. Secrets, identity a permissions

PR CI nemá potrebovať production credentials. Build môže používať short-lived OIDC identity pre push do candidate registry path. Data tests používajú sanitized fixtures. Promotion credentials patria do oddeleného environmentu s approval a protected branch/tag policy.

Fork PR predstavuje vyššie riziko. Workflow, ktorý má secrets alebo write token, nesmie automaticky vykonať untrusted code. `pull_request_target` a ekvivalentné privileged triggers vyžadujú veľmi opatrnú boundary, pretože checkout útočníkovho code s write credentials vytvára supply-chain compromise.

Každý job dostane minimálne permissions. Broad default token zvyšuje blast radius aj pri nevinnom dependency compromise.

## 14. Matrix a compatibility testing

Matrix overuje podporované combinations, nie všetky teoretické verzie. Training library, Python, CPU/GPU runtime, model format a inference server môžu mať compatibility surface. Matrix má explicitný support policy a failures nesmú byť potichu `continue-on-error`, ak kombinácia zostáva supported.

```yaml
strategy:
  matrix:
    python: ["3.11", "3.12"]
    mode: [cpu-smoke, package-load]
```

GPU matrix býva drahá a môže bežať nightly alebo pred release. Jej výsledok musí byť viazaný na candidate digest; nočný test branch headu sa nemá spätne považovať za proof pre iný artifact.

## 15. Flakiness a nondeterminism

Retry červeného testu môže rozlíšiť transient infrastructure issue, ale nesmie zmeniť flaky test na green verdict bez evidence. CI zaznamená všetky attempts a označí flake. Nondeterministic ML test potrebuje tolerances, fixed fixtures a seed inventory, nie neobmedzený retry.

Performance test v shared runneri má noise. V PR CI je vhodný coarse regression alebo resource invariant, nie jemný latency SLO. Dedicated performance environment patrí do neskoršieho gate-u.

## 16. Competing failure hypotheses

Keď CI zlyhá, first divergence môže byť source defect, fixture/contract drift, dependency resolution, compiler change, container build, runner environment, external service alebo permissions. Rovnaký symptom `tiny training failed` môže znamenať NaN v loss, chýbajúcu shared library, nedostupný artifact alebo OOM.

Logs sa čítajú spolu s exact runner, image a input identity. Re-run na inom runneri bez preservation môže zakryť root cause. Ak dependency registry krátko zlyhala, cache môže spôsobiť, že druhý attempt prejde s iným resolved graphom. Lockfile a download checksums chránia atribúciu.

## 17. Recovery a second-operation test

Containment zablokuje downstream full training a zachová CI artifacts. Recovery opraví jednu identifikovanú vrstvu a vytvorí nový commit alebo workflow generation. Starý green verdict sa nerecykluje pre nový candidate.

Second-operation test spustí workflow znovu nad rovnakým commitom a fixture manifestom. Výsledné compiled IR a image digests majú byť rovnaké, pokiaľ build contract deklaruje reproducibility. Ak sa líšia, evidence vysvetlí nondeterministic input, napríklad base image alebo timestamp.

Forbidden tests overia, že CI nemôže meniť Registry production alias, deployovať do production alebo čítať raw production labels. Positive test vytvorí complete evidence bundle. Adjacent test zmení schema fixture a potvrdí, že správny contract gate zlyhá.

## 18. Acceptance contract

ML CI je prijatá, keď každý relevantný change surface spúšťa vysvetlený test set, skipped suites sú viditeľné, outputs majú immutable identities a green verdict nevlastní production promotion. Workflow sa dá reprodukovať z reviewed inputs a jeho credentials sú bounded.

Taká CI skracuje feedback bez predstierania, že lacný smoke nahrádza drahú evaluation. Je mostom medzi repository change a trusted training candidate, nie posledným slovom o modeli.

## Primárne zdroje

- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [GitHub Actions — Workflow artifacts](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts)
- [GitHub Actions — Reusing workflow configurations](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations)
- [Kubeflow Pipelines — Pipeline concepts](https://www.kubeflow.org/docs/components/pipelines/concepts/pipeline/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Training pipelines a distributed training](training-pipelines-distributed-training.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Continuous Delivery pre modely →](continuous-delivery-for-models.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
