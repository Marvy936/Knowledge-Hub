# MLOps training lineage contract

Tento contract odstraňuje statický sample evaluation bundle z authoritative Registry pathu. Candidate evaluation musí byť odvodená z exact `manifest.json`, ktorý vytvoril Machine Learning flagship training run.

```text
exact dataset bytes
→ ML training
→ model.joblib + manifest.json
→ manifest dataset/model/source/gate verification
→ generated evaluation bundle
→ candidate identity
→ MLflow run a registered version
```

## Povinné väzby

Command `evaluation-from-training` overuje:

- `artifact_type` je trusted local scikit-learn pipeline,
- `model_file` zodpovedá skutočnému model pathu,
- dataset SHA-256 z manifestu zodpovedá aktuálnym dataset bytes,
- model SHA-256 z manifestu zodpovedá aktuálnym model bytes,
- training `source_revision` zodpovedá exact execution subjectu,
- threshold gate má stav `recall_gate_satisfied`,
- selected model nie je dummy baseline,
- test F1 a recall spĺňajú prahy zaznamenané v tom istom manifeste,
- manifest vyžaduje, aby selected F1 prekonal dummy baseline,
- decision threshold je v rozsahu 0–1,
- resolved Python, NumPy, pandas, scikit-learn a joblib versions sú prítomné.

Ak ktorákoľvek väzba nesedí, evaluation bundle nevznikne. MLOps candidate preto nemôže deklarovať acceptance iba na základe ručne napísaného JSON súboru.

## Command

```bash
python -m mlops_lab evaluation-from-training \
  --training-manifest labs/machine-learning/.runtime/artifact/manifest.json \
  --dataset labs/machine-learning/.runtime/data/customers.csv \
  --model labs/machine-learning/.runtime/artifact/model.joblib \
  --source-revision <exact-subject-sha> \
  --policy-generation ml-training-manifest-v1 \
  --output labs/mlops/.runtime/evaluation.json
```

Výstup zachováva existujúci evaluation contract:

```json
{
  "accepted": true,
  "metrics": {
    "accuracy": 0.68,
    "decision_threshold": 0.72,
    "f1": 0.63,
    "precision": 0.70,
    "recall": 0.57,
    "roc_auc": 0.74
  },
  "policy_generation": "ml-training-manifest-v1"
}
```

Čísla v príklade nie sú authoritative runtime evidence. Skutočné hodnoty sa generujú z exact training manifestu.

## Failure boundary

Contract odmietne najmä:

- dataset zmenený po trainingu,
- model zmenený po packagingu,
- training manifest z iného commitu,
- neprejdený threshold alebo metric gate,
- dummy model ako selected candidate,
- chýbajúce runtime versions,
- neplatný decision threshold.

## Dôkazová hranica

Úspešné vytvorenie evaluation bundle preukazuje konzistenciu medzi training manifestom, dataset bytes, model bytes, source revision a zaznamenanými acceptance gates.

Samo osebe ešte nepreukazuje, že training manifest bol zapísaný a prečítaný späť cez MLflow API alebo artifact store. Tento posledný krok zostáva otvorený pre úplné uzavretie Practical v1 lineage gate-u.
