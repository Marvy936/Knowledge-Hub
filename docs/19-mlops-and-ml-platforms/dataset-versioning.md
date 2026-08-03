# Dataset versioning

Dataset versioning znamená, že tím vie jednoznačne pomenovať, obnoviť a porovnať presnú populáciu dát použitú pre training, validation, test, backfill alebo production replay. Nie je to iba uloženie súboru s dátumom v názve. Version musí zachytiť obsah alebo authoritative snapshot, schema a semantic contract, extraction boundary, partitions, labels, point-in-time pravidlá a retention. Bez toho rovnaký code commit nemusí nikdy znovu dostať rovnaké observations.

Incident `MLOPS-PAY-90` ukázal typickú chybu. Training pipeline čítala `s3://ml-curated/risk/latest/`. Tento prefix obsahoval Parquet objekty z aktuálneho snapshotu, no počas dlhého training runu data pipeline prepísala manifest a pridala ďalšiu partition. Run preto spotreboval dataset, ktorý nikdy neexistoval ako schválená logická verzia. Experiment tracker evidoval path, ale nie object list ani digest. Model sa nedal reprodukovať a nebolo možné spoľahlivo určiť, či zmena metrics vznikla code zmenou alebo data membershipom.

## 1. Exact dataset subject

Dataset subject musí odlíšiť názov datasetu od jeho verzie. Názov `payment_risk_training` označuje logickú kolekciu a contract. Version označuje konkrétnu immutable generation tejto kolekcie. Pri file-based datasete môže byť version manifest digest. Pri warehouse table môže byť transaction snapshot alebo time-travel version. Pri streamoch môže byť rozsah topic partitions a offsets. Pri third-party source môže byť export artifact s checksumom a acquisition metadata.

```yaml
dataset_name: payment_risk_training
dataset_version: risk-train-2026-07-31-v2
manifest_digest: sha256:9bd7...e802
created_at: 2026-08-01T02:14:09Z
observation_unit: payment_operation_id
population_contract: cnp-eur-v5
event_time_range:
  start: 2025-01-01T00:00:00Z
  end: 2026-06-30T23:59:59Z
label_contract: confirmed-loss-30d-v3
label_maturity_cutoff: 2026-07-31T23:59:59Z
schema_version: risk-training-schema-v8
feature_view: payment-risk-features-v6
split_policy: merchant-group-time-v3
objects_manifest: s3://ml-manifests/risk/risk-train-2026-07-31-v2.json
row_count: 18422319
owner: risk-data-platform
retention_until: 2028-08-01
```

Manifest oddeľuje human-readable version od content identity. Version name môže niesť význam, ale digest zabraňuje tichej zmene. Row count je kontrolný signal, nie identity; dva datasety môžu mať rovnaký počet rows a odlišný obsah.

## 2. Čo všetko tvorí verziu datasetu

Dataset version nie sú iba data bytes. Pre reprodukciu treba vedieť, ktoré source objects alebo table versions boli zahrnuté, aký schema contract platil, ako sa deduplikovalo, ktoré entity boli excluded, kedy boli labels považované za mature a ako sa vytvorili splits. Zmena jednej z týchto vrstiev môže vytvoriť novú semantic version aj vtedy, keď raw source zostal rovnaký.

Physical version identifikuje konkrétne bytes alebo storage snapshot. Logical version identifikuje dataset po aplikovaní population a transformation contractu. Evaluation version navyše zahŕňa split membership a leakage boundary. V praxi môže jeden raw snapshot vytvoriť viac logical datasetov pre rôzne use cases.

```text
raw source snapshot R17
→ extraction/filter contract P5
→ point-in-time feature transform F6
→ label contract L3
→ split membership S3
→ training dataset version D22
```

Ak sa opraví label policy, vznikne nová dataset version, aj keď source events zostali rovnaké. Ak sa iba presunie object do iného bucketu bez zmeny obsahu a manifest zachová checksum, physical location sa zmení, no content version môže zostať rovnaká. Governance musí explicitne určiť, ktorá zmena invaliduje version identity.

## 3. Snapshot oproti mutable view

Mutable table alebo prefix je discovery surface, nie training authority. View `risk_features_latest` je užitočná pre exploráciu, ale training run musí resolve-nuť immutable snapshot pred začiatkom execution. Snapshot musí zostať stabilný počas celého runu, vrátane retries a distributed workers.

Pri object storage sa často vytvorí manifest so sorted listom object URI, object version ID, size a checksum. Digest sa počíta z canonical manifestu. Pri data lake formátoch môže authority poskytovať snapshot ID alebo transaction log version. Pri warehouse time travel sa zaznamená exact snapshot timestamp/version spolu s query a engine semantics.

```json
{
  "dataset": "payment_risk_training",
  "objects": [
    {
      "uri": "s3://ml-curated/risk/date=2026-06-29/part-00001.parquet",
      "version_id": "3Lg...P1",
      "size": 92844113,
      "sha256": "2f40...c911"
    },
    {
      "uri": "s3://ml-curated/risk/date=2026-06-30/part-00001.parquet",
      "version_id": "BB8...q7",
      "size": 94133702,
      "sha256": "b11e...8a09"
    }
  ]
}
```

Canonicalization musí definovať ordering, encoding a fields zahrnuté do digestu. Inak dva nástroje môžu vypočítať iný hash nad rovnakým logical setom.

## 4. DVC pointer model

DVC je Git-oriented pattern pre versioning datasetov a model files. `dvc add` vytvorí alebo aktualizuje malý `.dvc` metadata file a obsah uloží do DVC cache. Metadata file sa versionuje v Git-e, zatiaľ čo veľké bytes sa synchronizujú do configured remote storage cez `dvc push` a obnovujú cez `dvc pull` alebo `dvc checkout`.

```bash
dvc init
dvc remote add -d storage s3://ml-dvc-prod/risk
dvc add data/training.parquet
git add .dvc/config data/training.parquet.dvc data/.gitignore
git commit -m "Track risk training snapshot"
dvc push
```

Git commit viaže code a DVC pointer metadata. DVC remote drží content-addressed objects. Checkout staršieho Git commitu a `dvc checkout` obnoví corresponding dataset, ak object stále existuje v cache alebo remote. To je mechanizmus; nepreukazuje semantic correctness datasetu ani správnosť label maturity.

DVC je vhodné pre project-oriented file datasets a model artifacts. Pri data lakes, veľmi veľkom počte objektov alebo warehouse-native snapshots môže byť vhodnejší table-format alebo storage-native versioning. Nástroj sa vyberá podľa authority a scale, nie podľa marketingovej analógie „Git pre dáta“.

## 5. Git LFS a jeho hranica

Git LFS nahrádza veľký file v Git repository pointer fileom, ktorý obsahuje object ID a size, zatiaľ čo bytes sú uložené v LFS storage. Je užitočný pre veľké binary assets, ale sám nerieši dataset semantics, partitions, schema, labels ani point-in-time joins.

Pointer môže vyzerať takto:

```text
version https://git-lfs.github.com/spec/v1
oid sha256:4cac19622fc3ada9c0fdeadb33f88f367b541f38b89102a3f1261ac81fd5bcb5
size 84977953
```

OID identifikuje file bytes. Ak dataset tvorí tisíce objects, jeden LFS pointer na archive znižuje diffability a môže komplikovať partial access. Ak sa používateľovi LFS object nestiahne, workspace obsahuje iba pointer text; pipeline musí túto situáciu detegovať, inak môže omylom spracovať pointer ako data file.

## 6. Schema, contract a compatibility

Schema version musí zahŕňať names, types, nullability a constraints, ale production fitness vyžaduje aj semantic contract. Column `country_code` môže zostať string, no zmeniť source alebo normalization. Feature `merchant_age_days` môže zmeniť event-time reference. Taká zmena je semantic breaking change aj bez schema diffu.

Dataset validation sa preto delí na structural, statistical a semantic evidence. Structural checks overujú schema a required fields. Statistical checks sledujú distributions, missingness, uniqueness alebo class balance. Semantic checks overujú business invariants, time ordering, entity membership a label maturity. Threshold breach môže dataset zablokovať alebo vyžiadať approval podľa use case.

```yaml
checks:
  - name: operation_id_unique
    type: uniqueness
    column: payment_operation_id
    expectation: 1.0
  - name: no_future_features
    type: temporal_relation
    expression: feature_event_time <= prediction_time
    expectation: true
  - name: mature_labels_only
    type: temporal_relation
    expression: label_observed_at <= label_maturity_cutoff
    expectation: true
  - name: supported_currency
    type: allowed_values
    column: currency
    values: [EUR]
```

Validation report je evidence pre konkrétny dataset digest. Ak sa bytes zmenia, starý report sa nesmie recyklovať.

## 7. Split membership ako versionovaný artifact

Training, validation a test split nie je len parameter `random_state=42`. Membership musí byť reprodukovateľná a viazaná na entity/group/time boundary. Pri rolling datasetoch môže nová population meniť split membership aj s rovnakým seedom. Preto sa pre critical evaluation uloží mapping observation alebo group ID na split, prípadne deterministic rule a exact input snapshot.

```text
payment_operation_id,merchant_id,split
op-1001,m-77,train
op-1002,m-80,validation
op-1003,m-92,test
```

Test snapshot musí zostať chránený pred repeated feedbackom. Dataset Registry môže evidovať, ktoré runs ho spotrebovali. Samotné versioning bytes nezabráni tomu, aby tím test set používal ako validation; governance a experiment lineage musia doplniť access a usage evidence.

## 8. Labels a dozrievanie pravdy

Labels často prichádzajú oneskorene a môžu sa spätne meniť. Dataset version musí určiť maturity cutoff a correction policy. Ak chargeback môže vzniknúť do 30 dní, operácie z posledných dní nemajú mature negative label. Označiť ich ako negatívne by vytvorilo censoring bias.

Nový label snapshot môže opravovať historical records. Tím musí rozhodnúť, či oprava vytvára novú dataset version, patch manifest alebo úplný rebuild. Historical model evaluation musí zostať viazaná na pôvodný label evidence, ale re-evaluation môže použiť novšiu truth generation a jasne označiť, že porovnáva iný estimand.

## 9. Storage, cache a garbage collection

Content-addressed storage znižuje duplicity, ale garbage collection môže zničiť reprodukciu. Object sa nesmie odstrániť len preto, že nie je referenced aktuálnou Git branchou. Môže ho potrebovať registered model, audit retention, active incident alebo rollback candidate. Reachability graph musí zahrnúť model registry, release manifests, legal hold a pending experiments.

Cache je performance layer, nie authority. Local worker cache môže obsahovať správne bytes aj po tom, čo remote object chýba, čím zakryje broken reproducibility. Acceptance preto zahŕňa fresh-environment pull z authoritative remote. Naopak, remote object existencia nepreukazuje, že training worker použil túto version; runtime lineage musí zaznamenať actual read.

## 10. Dataset diff a change review

Pri code reviewe vidíme line diff. Pri dataset reviewe potrebujeme membership, schema, distribution, label a segment diff. Review musí vysvetliť, prečo version vznikla a aké model behavior sa môže zmeniť.

```text
old: risk-train-2026-06-30-v1
new: risk-train-2026-07-31-v2
rows: +812,441 / -19,203
new time window: 2026-06-01..2026-06-30
label maturity: 30d → 45d
merchant groups added: 1,204
positive prevalence: 0.83% → 0.71%
schema: no structural change
semantic change: chargeback appeal reversal applied
```

Aggregate diff môže zakryť cohort-specific zmenu. Critical datasets potrebujú segment breakdown a source-level explanation. Approval je decision nad evidence, nie len formálny status.

## 11. Failure walkthrough incidentu MLOPS-PAY-90

Tím najprv skontroloval Git commit a DVC-like pointer record, no training config ukazoval na mutable prefix. Object access logs odhalili, že workers prečítali 412 objects z manifestu A a 19 objects pridaných po update na manifest B. Dataset digest uložený v experiment tracker-i patril iba manifestu A.

Prvá containment action zastavila ďalšiu promotion a zakázala writerovi meniť `latest` počas aktívneho runu. Tím zachoval cache a access logs, vytvoril reconstructed object manifest a označil pôvodný run ako `lineage-incomplete`. Následne vytvoril immutable snapshot B2, prebehol validation a spustil nový training run z fresh workera.

Nový run mal nižší validation score než pôvodný mixed snapshot, čo potvrdilo, že data membership ovplyvnila výsledok. Root cause nebola chyba storage služby, ale absent snapshot-resolution boundary a nepravdivý experiment parameter.

## 12. Recovery a acceptance

Pozitívny test vytvorí dataset version, uloží manifest, pushne bytes do authoritative remote a obnoví ich vo fresh environment-e. Hash a row/schema evidence sa musia zhodovať. Forbidden test odmietne `latest`, unversioned table alebo object bez checksum/version ID v authoritative training. Partial-failure test simuluje, že pointer commit existuje, ale remote object chýba; pipeline musí zlyhať pred trainingom. Second-version test vytvorí novú version a overí, že stará zostáva obnoviteľná.

Príklad pre DVC-style read-back:

```bash
git checkout <dataset-commit>
dvc pull

dvc status --cloud
sha256sum data/training.parquet
python validate_dataset.py \
  --manifest manifests/risk-train-2026-07-31-v2.json \
  --data data/training.parquet
```

`dvc status --cloud` a checksum dokazujú synchronization a bytes. Validation dokazuje definované checks. Ani jeden príkaz sám nepreukazuje, že dataset reprezentuje budúcu production population alebo že labels sú business-correct; tieto tvrdenia patria evaluation a outcome vrstvám.

## 13. Kontrolné otázky

1. Aký je rozdiel medzi human-readable dataset version a content digestom?
2. Prečo mutable warehouse view alebo object prefix nie je training authority?
3. Ktoré zmeny vytvoria novú semantic dataset version bez schema change?
4. Prečo cache môže zakryť broken remote reproducibility?
5. Aké evidence odlíšia chybu model code od zmeny dataset membershipu?

## 14. Primárne zdroje

- [DVC Get Started](https://dvc.org/doc/start)
- [DVC `add` command](https://dvc.org/doc/command-reference/add)
- [DVC `push` command](https://dvc.org/doc/command-reference/push)
- [GitHub documentation — Git Large File Storage](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage)

Dataset versioning je základ provenance, nie úplný MLOps systém. Musí sa spojiť s experiment runom, model artifactom, deploymentom a production outcome-om, inak vie tím obnoviť dáta, ale nevie dokázať, čo z nich vzniklo.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Data, code, environment a model lineage](data-code-environment-model-lineage.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Experiment tracking →](experiment-tracking.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
