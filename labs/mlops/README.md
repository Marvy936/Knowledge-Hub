# MLOps flagship project — foundation

Tento blok zakladá praktický lifecycle sekcie 19. Neimplementuje ešte celý serving, canary, drift a retraining chain. Najprv vytvára deterministic evidence a promotion contract, bez ktorého by MLflow run, Registry version alebo alias zostali iba mutable control-plane metadata.

```text
source dataset
→ immutable dataset snapshot manifest
→ evaluation bundle
→ accepted candidate manifest
→ compare-before-promote decision
→ immutable release manifest
→ mutable local alias read-back
```

## Hranica prvého bloku

Implementované sú:

- SHA-256 identita datasetu a model artifactu,
- canonical JSON fingerprints,
- strict schema validation pre dataset, evaluation, candidate a alias state,
- candidate manifest viazaný na dataset, model bytes, source revision a policy generation,
- workspace-independent candidate identity bez lokálneho filesystem pathu,
- refusal pri neakceptovanom candidate,
- compare-before-promote kontrola očakávanej predchádzajúcej verzie,
- atomic write alias state-u,
- immutable release manifest pre downstream serving,
- tests pre determinism, tampering, workspace portability a stale promotion.

Zatiaľ nie sú implementované ani deklarované ako overené:

- MLflow Tracking Server a database-backed Model Registry,
- upload model bytes do artifact store,
- Registry version a alias mutation,
- container image build a digest pinning,
- canary traffic,
- production metrics, drift signal a controlled retraining.

Tieto vrstvy budú nadväzovať na release manifest vytvorený týmto blokom.

## Inštalácia

Z koreňa repozitára:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "labs/mlops[dev]"
pytest labs/mlops/tests -q
```

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e "labs/mlops[dev]"
pytest labs/mlops/tests -q
```

## Dataset snapshot

Ako vstup možno použiť deterministický CSV dataset z `labs/machine-learning` alebo iný lokálny testovací súbor.

```bash
python -m mlops_lab snapshot \
  --dataset labs/machine-learning/.runtime/data/customers.csv \
  --output labs/mlops/.runtime/dataset-manifest.json \
  --dataset-name churn-training \
  --generation churn-data-2026-08-06
```

Výstup obsahuje exact path subject, byte size, SHA-256, dataset name a generation. Manifest nedokazuje data quality ani representativeness; dokazuje iba identitu konkrétnych bytes. Lokálna cesta ostáva diagnostickým údajom dataset snapshotu, ale neprenáša sa do candidate identity.

## Candidate manifest

Evaluation bundle je explicitný JSON contract:

```json
{
  "accepted": true,
  "metrics": {
    "f1": 0.63,
    "recall": 0.57
  },
  "policy_generation": "churn-promotion-v1"
}
```

Candidate sa vytvorí iba z existujúceho dataset manifestu, model artifactu a evaluation bundle:

```bash
python -m mlops_lab candidate \
  --dataset-manifest labs/mlops/.runtime/dataset-manifest.json \
  --model labs/machine-learning/.runtime/artifact/model.joblib \
  --evaluation labs/mlops/data/sample-evaluation.json \
  --source-revision local-dev \
  --output labs/mlops/.runtime/candidate.json
```

Candidate identity je SHA-256 canonical payloadu. Mutable timestamp, lokálna cesta ani názov model file nie sú súčasťou identity. Rovnaké dataset a model bytes, evaluation bundle a source revision preto vytvoria rovnaký candidate ID aj v inom workspace. Kandidát stále nie je dôkazom, že model možno bezpečne načítať alebo že je vhodný pre produkciu; tieto gates patria do nasledujúcich vrstiev.

## Promotion a release manifest

Promotion používa compare-before-promote semantics. Prvý promotion očakáva, že alias ešte neexistuje:

```bash
python -m mlops_lab promote \
  --candidate labs/mlops/.runtime/candidate.json \
  --alias-state labs/mlops/.runtime/registry-aliases.json \
  --alias champion \
  --expected-current none \
  --release-output labs/mlops/.runtime/release.json
```

Ďalší promotion musí uviesť presnú candidate identity, ktorú očakáva ako aktuálnu:

```bash
python -m mlops_lab promote \
  --candidate labs/mlops/.runtime/next-candidate.json \
  --alias-state labs/mlops/.runtime/registry-aliases.json \
  --alias champion \
  --expected-current <previous-candidate-id> \
  --release-output labs/mlops/.runtime/next-release.json
```

Ak alias medzitým zmenil iný actor, command zlyhá bez mutation. Release manifest pinne candidate ID, dataset digest, model digest, evaluation digest, source revision a policy generation. Downstream deployment má používať release manifest, nie znovu resolvovať mutable alias pri štarte každej repliky.

## Acceptance hranica

Zelené tests preukazujú lokálny deterministic promotion contract. Nepreukazujú MLflow server, Registry permissions, artifact upload, model loadability, serving image, canary outcome, production drift ani business impact.

## Cleanup

```bash
rm -rf labs/mlops/.runtime
```

PowerShell:

```powershell
Remove-Item -Recurse -Force labs/mlops/.runtime
```

Cleanup je dokončený až po read-backu, že `.runtime` neexistuje.
