# Monitoring, drift a approval-gated retraining

Táto vrstva vytvára deterministic monitoring a decision contracts nad serving evidence. Neimplementuje production telemetry backend ani samotný retraining job. Zabraňuje trom chybným skratkám:

1. chýbajúce dáta sa nesmú interpretovať ako zdravý stav,
2. operational failure sa nesmie interpretovať ako data drift,
3. drift signal nesmie automaticky spustiť training bez exact approval subjectu.

```text
baseline events
→ aggregate baseline profile
→ deployment monitoring window
→ semantically validated drift report
→ stable / no-data / insufficient / operational-failure / drift-detected
→ canonical retraining proposal
→ proposal + exact drift report + human approval
→ budúci controlled retraining operation
```

## Event a privacy boundary

Jeden vstupný event obsahuje exact feature record, `success`, observed `latency_ms` a pri úspechu prediction s probability. Failed event musí mať prediction a probability nastavené na `null`.

Baseline ani monitoring window neukladajú raw recordy. Ukladajú len counts, feature distributions, latency, error rate a prediction aggregates. Source event log môže mať vlastný retention, redaction a access policy mimo tohto labu.

## Baseline profile

Baseline vyžaduje aspoň jeden úspešný event a nesmie obsahovať failed outcome. Obsahuje:

- profile name a generation,
- total/success/failure counts,
- error rate a explicitný `no_data`,
- latency minimum, average, p95 a maximum,
- positive prediction rate a priemernú probability,
- numeric quantile boundaries, proportions, mean, minimum a maximum,
- categorical categories, proportions a `other_proportion`,
- canonical `baseline_profile_id`.

Numeric boundaries vzniknú iba z baseline-u. Monitoring window používa tie isté boundaries. Vytvorenie nových bins vo window by zmenilo porovnávací subject a znehodnotilo PSI.

## Monitoring window

Window je viazané na exact `baseline_profile_id` a `deployment_id`. Môže obsahovať úspešné aj neúspešné events.

Ak nemá žiadny event:

- `no_data=true`,
- latency hodnoty sú `null`,
- prediction aggregates sú `null`,
- feature distributions majú nulové proportions.

Tento stav je otvorený, nie healthy.

## Semantic validation

Canonical SHA-256 sám o sebe dokazuje iba nemennosť payloadu. Nedokazuje, že payload dáva zmysel. Preto validátory pred rozhodnutím kontrolujú aj:

- exact top-level a nested keys,
- event-count rovnice,
- `error_rate = failed / total`,
- konzistenciu `no_data`,
- latency a prediction nullability,
- feature profile keys,
- count každej feature distribution voči `successful_events`,
- strictly increasing numeric boundaries,
- počet histogram bins,
- súčet numeric proportions,
- categorical categories, proportions a `other` bucket,
- canonical ID až po sémantickej validácii.

Nanovo zahashovaný, ale sémanticky neplatný profile alebo window sa preto odmietne.

## Drift metriky

Numeric features používajú Population Stability Index nad baseline bins:

```text
PSI = Σ (actual - expected) × ln((actual + ε) / (expected + ε))
```

Categorical features používajú total variation distance nad baseline categories a samostatným `other` bucketom. Prediction layer porovnáva absolute delta positive prediction rate. Operational layer používa observed error rate.

Thresholdy sú explicitné súčasti reportu:

- numeric PSI,
- categorical TVD,
- prediction-rate delta,
- maximum error rate,
- minimum successful events.

## Drift report a status precedence

Report obsahuje exact baseline, window a deployment IDs, per-feature scores, thresholdy, exceeded feature lists a observed:

- total events,
- successful events,
- failed events,
- `no_data`,
- error rate.

Tieto observed polia umožňujú validátoru deterministicky prepočítať status:

| Stav | Podmienka |
|---|---|
| `no_data` | Window nemá events. |
| `insufficient_evidence` | Successful events sú pod minimom. |
| `operational_failure` | Error rate prekročil operational threshold. |
| `drift_detected` | Evidence volume je dostatočný a drift gate bol prekročený. |
| `stable` | Evidence je dostatočný a žiadny gate nebol prekročený. |

Validátor znovu vypočíta exceeded lists a status. Preto nestačí zmeniť `status` na `drift_detected` a vytvoriť nový hash.

## Reproducible drift injection

`inject_drift` podporuje:

- `control` — exact copy bez zmeny,
- `shift` — deterministic zmenu spend, support tickets, login activity, contract a autopay distribution.

Control corpus musí zostať `stable`. Shift corpus musí pri rovnakých thresholdoch vytvoriť reprodukovateľný drift signal. Injection je testovací mechanizmus, nie production data generator.

## Retraining proposal

Proposal vznikne iba z canonical a semantically valid drift reportu.

- `drift_detected` → `approval_required`,
- každý iný status → `blocked`.

Proposal pinne:

- exact `drift_report_id`,
- `drift_status`,
- exact `deployment_id`,
- current model SHA-256,
- policy generation,
- canonical `retraining_proposal_id`.

Action a reason sa musia zhodovať s drift statusom. Nanovo zahashovaný proposal s vlastným action mappingom sa odmietne.

## Human approval

Approval vyžaduje súčasne:

- canonical proposal,
- exact canonical drift report,
- exact expected proposal ID,
- approvera,
- approval generation.

Approval path znovu overí, že proposal patrí danému reportu, má rovnaký drift status a deployment a bol z reportu deterministicky odvodený. Výstup pinne `drift_detected` a authorized action `start_controlled_retraining`.

Approval neštartuje training. Je to authorization artifact pre budúci executor. Executor musí ešte overiť current deployment/model, operation ID, read-before-retry state, exact training dataset generation a výsledný candidate/Registry read-back.

## Executable monitoring driver

```bash
python labs/mlops/scripts/run_monitoring_drift.py \
  --baseline-events-jsonl labs/mlops/.runtime/baseline-events.jsonl \
  --window-events-jsonl labs/mlops/.runtime/window-events.jsonl \
  --profile-name churn-baseline \
  --generation generation-1 \
  --deployment-id <deployment-id> \
  --model-sha256 <model-sha256> \
  --policy-generation retraining-policy-v1 \
  --minimum-successful-events 100 \
  --numeric-psi-threshold 0.20 \
  --categorical-tvd-threshold 0.15 \
  --prediction-rate-delta-threshold 0.10 \
  --maximum-error-rate 0.05 \
  --baseline-output labs/mlops/.runtime/baseline.json \
  --window-output labs/mlops/.runtime/window.json \
  --drift-output labs/mlops/.runtime/drift.json \
  --proposal-output labs/mlops/.runtime/retraining-proposal.json
```

Exit codes:

- `0` — stable,
- `2` — invalid input alebo contract,
- `3` — no-data alebo insufficient evidence,
- `4` — operational failure,
- `5` — drift detected; explicit approval je potrebný.

## Separate approval driver

```bash
python labs/mlops/scripts/approve_retraining.py \
  --proposal labs/mlops/.runtime/retraining-proposal.json \
  --drift-report labs/mlops/.runtime/drift.json \
  --expected-proposal-id <exact-proposal-id> \
  --approver ml-platform-owner \
  --approval-generation approval-2026-08-06 \
  --output labs/mlops/.runtime/retraining-approval.json
```

Nesprávny proposal ID, iný drift report, upravený payload alebo blocked action skončia refusal bez approval outputu.

## Overená source hranica

Izolovaná exact-source rekonštrukcia monitoring, drift a approval vrstvy prešla:

- Python `compileall`,
- **12/12 pytest cases**.

Testy pokrývajú stable control, reproducible shift, no-data, insufficient evidence, operational failure, exact approval, stale approval, canonical tampering, semantically invalid rehashed report/profile, forged proposal viazaný na iný report a executable driver lifecycle.

Predchádzajúci live-canary blok na `main` prešiel vlastnou 42-testovou source reconstruction. Celý repository runtime suite však nie je uzavretý, pretože GitHub Actions dispatch zostáva blokovaný issue #151.

## Neoverená hranica

Tento blok nepreukazuje production telemetry collection, reálny časový drift, label/concept drift, alert delivery, externý identity/approval systém, samotný retraining execution, nový candidate alebo Registry version ani business outcome.

Practical v1 monitoring, drift a controlled retraining checkbox zostáva otvorený do live evidence a schváleného end-to-end retraining runu.
