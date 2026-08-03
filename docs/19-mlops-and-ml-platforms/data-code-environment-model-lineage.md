# Data, code, environment a model lineage

Lineage odpovedá na otázku, z čoho presne vznikol konkrétny výstup a ktoré downstream objekty týmto výstupom boli ovplyvnené. V ML systéme nestačí vedieť, že model patrí projektu `payment-risk`. Potrebujeme vedieť, ktorý dataset snapshot, feature definitions, source commit, configuration, container image, dependencies, pipeline run a training operation vytvorili konkrétne bytes modelu, a ktoré deploymenty, predictions, actions a outcomes ich následne použili.

Incident `MLOPS-PAY-90` pokračuje. Atlas mal experiment run s vysokým validation score a model artifact s digestom. Pri audite však nebolo možné určiť, či run čítal dataset `2026-07-31` alebo mutable path `latest`, pretože tracking record obsahoval iba textový parameter. Container image bol označený tagom `risk-trainer:2.6`, no tag sa medzičasom presunul. Feature pipeline emitovala OpenLineage udalosti, ale model training job neuviedol presné input dataset facets. Tím teda mal veľa metadata, ale nemal uzavretý provenance graph.

## 1. Lineage ako graf príčin, nie zoznam tagov

Lineage je directed graph. Nodes predstavujú datasety, jobs, runs, code revisions, environments, artifacts, deployments alebo business operations. Edges vyjadrujú konkrétny vzťah, napríklad `consumed`, `produced`, `derived_from`, `packaged_with`, `loaded_by` alebo `acted_on`. Každý node potrebuje stabilnú identity a každá edge potrebuje event alebo manifest, ktorý vysvetľuje, kedy a pri akej operácii vznikla.

```text
raw dataset snapshot
        └─consumed_by→ feature-materialization run
                            └─produced→ curated feature snapshot
Git commit + config + image digest
        └─executed_as→ training run
curated feature snapshot + label snapshot
        └─consumed_by→ training run
training run
        └─produced→ model artifact digest
model artifact + serving image + policy
        └─loaded_by→ deployment generation
prediction request
        └─used→ loaded model + feature values
        └─caused→ queue action
        └─joined_to→ mature business outcome
```

Graf musí byť traversable v oboch smeroch. Backward lineage vysvetľuje pôvod artifactu: „z čoho vznikol model?“. Forward lineage ukazuje blast radius: „ktoré models, deployments alebo reports použili chybný dataset?“. Audit, incident response a deletion request potrebujú obe otázky.

Tag ako `dataset=v3` nie je lineage, ak `v3` nie je globálne rozlíšiteľný immutable subject. Rovnako run URL nie je provenance, ak artifact store už neobsahuje bytes alebo environment tag ukazuje iba package name bez digestu.

## 2. Exact identity každej lineage vrstvy

Data identity môže byť content digest, immutable object version, table snapshot ID, transaction/version timestamp alebo manifest digest. Code identity je commit SHA alebo signed source archive digest. Configuration identity musí zachytiť resolved values po precedence a interpolation, nie iba default súbor. Environment identity je image digest, lockfile digest, hardware/runtime class a dôležité driver/library versions. Model identity je digest finálnych bytes spolu s formatom a interface contractom.

Training run je operation identity, nie model identity. Jeden run môže vytvoriť viac checkpoints a exportov; dva runs môžu teoreticky vytvoriť identické bytes. Preto sa nesmie `run_id` zamieňať za `model_digest`. Podobne experiment je organizačný container pre runs, nie lineage edge ani promotion decision.

Praktický lineage manifest môže mať explicitné namespaced identifiers:

```yaml
lineage_event_id: 01J4A5X2M8Y2R7TQ9M1N5P6K3B
event_time: 2026-08-03T08:14:51Z
job:
  namespace: kubeflow://prod-eu1/risk
  name: train-payment-risk
run:
  id: 6f7b8fa3b5ad4aaead859f1a5d771301
inputs:
  - namespace: s3://ml-curated-eu1
    name: risk/features/2026-07-31
    version: sha256:9bd7...e802
  - namespace: s3://ml-labels-eu1
    name: confirmed-loss/2026-07-31
    version: sha256:3c28...992a
code:
  repository: git@example/risk-model.git
  commit: 77a51d0
configuration_digest: sha256:1a6d...de11
environment:
  image: registry.example/risk-trainer@sha256:31ab...91fe
  python_lock_digest: sha256:8f00...9c21
outputs:
  - namespace: s3://ml-artifacts-eu1
    name: runs/6f7b.../model/model.pkl
    version: sha256:b8ae...7d22
```

Namespacing zabraňuje kolízii názvov. Version musí reprezentovať immutable generation alebo presne definovaný snapshot. Ak source system immutable version neposkytuje, pipeline musí vytvoriť vlastný manifest so zoznamom objektov, partitions, checksums a extraction boundary.

## 3. Data lineage

Data lineage sleduje raw sources, ingestion, filters, joins, transformations, labels, splits a materializations. Pre ML je zvlášť dôležitý event-time a point-in-time boundary. Dataset môže obsahovať správne columns, ale lineage musí ukázať, či hodnota feature bola dostupná v prediction time. Bez toho graf opisuje fyzický pohyb dát, no nepreukazuje absence leakage.

Dataset node nesmie byť iba názov table `risk_features`. Potrebuje snapshot alebo partition set, schema generation, extraction query/code a row-population contract. Pri mutable warehouse table môže training manifest zaznamenať transaction snapshot, time-travel version alebo exported file set. Query text sám nestačí, pretože rovnaký query nad mutable table v inom čase vráti iné rows.

Label lineage musí odlíšiť event, ktorý sa má predikovať, od procesu, ktorý vytvoril observed label. Confirmed loss môže vzniknúť z chargebacku, investigation workflowu a maturity window. Ak sa zmení adjudication policy, rovnaký raw event môže dostať iný label. Model lineage preto potrebuje label-contract version, nie iba názov target column.

## 4. Code a configuration lineage

Git commit identifikuje versionovaný source tree, ale training behavior môže meniť runtime parameter, secret-provided endpoint, feature flag alebo notebook state. Lineage musí zachytiť resolved configuration, ktorá vstúpila do runu. Najbezpečnejší pattern je vytvoriť canonical, secret-redacted config artifact a jeho digest.

```bash
python render_config.py \
  --base config/train.yaml \
  --environment prod-eu1 \
  --output resolved-config.json

sha256sum resolved-config.json
```

Digest sa loguje do runu a samotný redacted file sa uloží ako artifact. Secrets sa nemajú zapisovať do experiment trackeru; namiesto value sa eviduje secret reference, version alebo credential generation, ak to threat model povoľuje. Cieľom je reprodukcia behavioru bez exfiltrácie credentials.

Notebook lineage je náročnejšia, pretože execution order a in-memory mutations nemusia zodpovedať cell orderu. Notebook použitý na authoritative training musí byť exportovaný alebo spustený clean-kernel orchestráciou, pričom run zachytí executed notebook artifact. „Notebook uložený v Git-e“ nepreukazuje, že práve tento state vytvoril model.

## 5. Environment lineage

Environment zahŕňa package graph, OS libraries, Python runtime, framework, CUDA/cuDNN, drivers, architecture a relevantné hardware characteristics. Container image digest je silný základ, ale nezachytí host driver alebo accelerator firmware. Pri CPU scikit-learn modeli môže byť image digest a lockfile dostatočný pre praktickú reprodukciu. Pri distributed GPU trainingu treba navyše topology, world size, precision mode a communication-library generation.

Mutable image tag je pointer, nie environment identity. Ak run loguje `risk-trainer:2.6`, read-back musí resolve-nuť digest v čase štartu a uložiť ho. Neskoršie `docker pull` rovnakého tagu nemusí dostať rovnaký image.

```bash
image_ref='registry.example/risk-trainer:2.6'
resolved_digest=$(crane digest "$image_ref")
printf '%s\n' "$resolved_digest"
```

Command output preukazuje registry resolution v danom okamihu. Nepreukazuje, že scheduler skutočne spustil tento digest. Runtime evidence musí prísť z Pod `status.containerStatuses[].imageID`, node runtime alebo podpísanej execution attestation.

## 6. Model lineage

Model lineage začína candidate artifactom, ale zahŕňa aj preprocessing, signature, dependencies a export/conversion kroky. Scikit-learn pipeline uložená ako jeden artifact môže obsahovať transformer aj estimator. Pri ONNX alebo TensorRT conversion vzniká nový model artifact, ktorý je derived from training checkpoint, no nie je bitovo identický a môže mať numerické odchýlky.

```text
training checkpoint digest A
→ export job run E
→ ONNX artifact digest B
→ optimization job run O
→ TensorRT engine digest C
```

Serving musí referencovať digest C; evaluation iba nad A nie je plný production proof. Conversion job potrebuje vlastný code/environment lineage a parity test medzi source a target artifactom. Registry version môže ukazovať na C a metadata zachovať relation `derived_from=A`.

Model signature a input schema patria do lineage, pretože rovnaké weights s iným feature orderom vytvoria iné behavior. Artifact digest síce identifikuje bytes, no operational compatibility vyžaduje aj explicitný interface contract.

## 7. Runtime a business lineage

Training provenance končí model artifactom, ale production lineage musí pokračovať. Deployment generation spája model digest, serving image digest, feature-view generation, policy a environment. Každá prediction loguje minimálne request ID, event time, model digest alebo deployment generation, feature-set reference, output a policy decision reference podľa privacy pravidiel.

Business action potrebuje vlastnú idempotent operation identity. Prediction `req-9182` môže viesť k queue itemu `review-7711`; mature label môže prísť o 30 dní. Join medzi týmito IDs umožní odmerať outcome konkrétneho model release-u. Bez neho monitoring ostáva pri technických metrics a nevie preukázať, či model pomohol.

Privacy a retention môžu zakazovať dlhodobé uloženie raw features. Lineage potom používa pseudonymized IDs, schema/dataset references, hashes alebo controlled evidence store. Lineage nie je licencia kopírovať citlivé dáta do každého nástroja.

## 8. OpenLineage object model a jeho hranica

OpenLineage modeluje najmä `Job`, `Run` a `Dataset`. Job je definovaná práca, Run je konkrétne vykonanie a Dataset je vstupná alebo výstupná kolekcia. Runtime events umožňujú skladať graph naprieč orchestrátormi a data platformami. Tento model je vhodný pre data a pipeline lineage, ale organizácia musí doplniť ML-specific facets alebo väzby na experiment run, model artifact, registry a deployment.

Job `train-payment-risk` nie je konkrétny model. Run event môže ukázať, že job spotreboval dva datasety a vytvoril output dataset alebo model artifact. Promotion a loaded runtime state však stále potrebujú ďalšie authority. OpenLineage event sám nepreukazuje, že referenced object ešte existuje alebo že event emitter bol dôveryhodný.

Lineage eventy preto musia mať authentication, schema validation, replay/deduplication a retention. Duplicated `COMPLETE` event nesmie vytvoriť dva logické runs. Missing event sa nesmie interpretovať ako dôkaz, že job neprebehol; je to observation gap.

## 9. Lineage collection patterns

Implicitná instrumentation číta metadata z orchestrátora, query engine alebo frameworku. Je lacná na adopciu, no môže vynechať business IDs alebo custom transforms. Explicitná instrumentation zapisuje domain-specific input/output references priamo v kóde. Je presnejšia, ale závisí od disciplíny tímu. Najlepší platform pattern kombinuje oboje: automaticky zachytí common execution context a vyžaduje explicitný contract pre kritické subjects.

Build-time lineage môže byť uložená ako manifest pri artifacte. Runtime lineage sa emituje ako event. Periodická reconciliation kontroluje, či graph references stále existujú a či model Registry, object store a deployment inventory sú konzistentné.

## 10. Dôkazná hierarchia lineage

Deklarovaný config hovorí, čo job mal použiť. Resolved manifest hovorí, aké references boli vyriešené pred execution. Runtime event hovorí, čo emitter tvrdí, že použil. Object-store checksum a runtime imageID poskytujú nezávislejší read-back. Reproduction alebo replay ukazuje, či inputs a environment vedú k očakávanému outputu. Business trace uzatvára downstream consequence.

Žiadna jednotlivá vrstva nie je absolútna. Signed manifest môže byť správny, ale job mohol čítať mutable path mimo manifestu. Runtime event môže byť neúplný. Digest preukazuje bytes, nie semantic fitness. Preto sa critical promotion opiera o viac korelovaných authority layers.

## 11. Failure walkthrough incidentu MLOPS-PAY-90

Tím začal od model digestu a experiment runu. Artifact existoval, no run parameter `dataset_path=s3://ml-curated/risk/latest/` bol mutable. Object-store access logs ukázali, že job prečítal objects z dvoch snapshotov, pretože symlink-like manifest sa počas runu aktualizoval. Training image tag sa navyše resolve-ol na nový digest po security rebuild-e.

OpenLineage graph ukazoval feature materialization job a output dataset, ale training job neposlal input version. Prvá divergence preto vznikla už medzi intended dataset manifestom a actual object reads. Model metrics boli reprodukovateľné iba v pôvodnom ephemeral cache, nie z published references.

Containment zastavil promotion kandidáta a garbage collection related cache. Tím vytvoril forensic manifest z object access logs, Pod imageID, resolved config artifactu a experiment metadata. Následne znovu spustil training s immutable dataset manifestom a image digestom. Nový run vytvoril odlišný model digest, čím potvrdil, že pôvodný candidate nemal uzavretú provenance.

## 12. Recovery a acceptance

Recovery neznamená doplniť chýbajúce tagy spätne odhadom. Historical record musí jasne označiť reconstructed evidence a uncertainty. Autoritatívny nový run musí používať immutable inputs, emitovať complete lineage a vytvoriť model artifact, ktorý prejde parity a promotion gates.

Pozitívny test prejde backward traversal z production prediction po model, run, code, environment a datasety. Forward test začne známym chybným dataset snapshotom a nájde všetky derived models a deployments. Forbidden test odmietne mutable dataset path alebo image tag bez resolved digestu. Second-run test zopakuje training z rovnakých references a porovná artifact alebo definovanú tolerance, pričom nový run ID zostane odlišný.

Praktická policy môže vyžadovať minimálne lineage fields:

```rego
package ml.lineage

deny[msg] {
  input.stage == "promote"
  not input.dataset_digest
  msg := "promotion requires immutable dataset digest"
}

deny[msg] {
  input.stage == "promote"
  not startswith(input.training_image, "registry.example/")
  msg := "training image must use approved registry"
}

deny[msg] {
  input.stage == "promote"
  not contains(input.training_image, "@sha256:")
  msg := "training image must be pinned by digest"
}
```

Policy kontroluje prítomnosť a formát evidence. Neoveruje sama existenciu objektu ani pravdivosť lineage eventu; enforcement pipeline musí references resolve-nuť a read-backom potvrdiť.

## 13. Kontrolné otázky

1. Aký je rozdiel medzi experiment run ID a model artifact digestom?
2. Prečo query text nad mutable table nie je dostatočná dataset identity?
3. Ktoré environment properties nie sú zachytené samotným container image digestom?
4. Ako sa líši backward lineage od forward lineage pri incidente?
5. Prečo OpenLineage event nie je automaticky úplný production provenance proof?

## 14. Primárne zdroje

- [OpenLineage object model](https://openlineage.io/docs/spec/object-model/)
- [MLflow Tracking concepts](https://mlflow.org/docs/latest/tracking/)
- [DVC Get Started](https://dvc.org/doc/start)
- [Git Large File Storage pointer model](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage)

Lineage platforma má zmysel iba vtedy, keď identifiers a edges zodpovedajú skutočným authority boundaries. Veľký graf vytvorený z mutable názvov môže vyzerať kompletne, ale pri reprodukcii alebo incidente sa rozpadne.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: ML lifecycle a rozdiel medzi DevOps a MLOps](ml-lifecycle-devops-vs-mlops.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Dataset versioning →](dataset-versioning.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
