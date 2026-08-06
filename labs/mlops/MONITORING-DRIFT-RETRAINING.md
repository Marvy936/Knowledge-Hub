# Monitoring, drift a approval-gated retraining

Táto vrstva vytvára deterministic monitoring a decision contracts nad serving evidence. Neimplementuje production telemetry backend ani samotný retraining job. Jej cieľom je zabrániť trom častým chybám:

1. chýbajúce dáta sú interpretované ako zdravý stav,
2. operational failure je nesprávne interpretovaný ako data drift,
3. drift signal automaticky spustí training bez exact approval subjectu.

```text
baseline events
→ aggregate baseline profile
→ deployment monitoring window
→ drift comparison
→ stable / no-data / insufficient / operational-failure / drift-detected
→ canonical retraining proposal
→ exact human approval
→ budúci controlled retraining operation
```

## Event contract

Jeden monitoring event obsahuje:

- exact feature record,
- `success`,
- observed `latency_ms`,
- prediction a probability pri úspechu,
- `null` prediction/probability pri failure.

Feature record používa rovnakých osem vstupov ako Machine Learning a serving contract:

- päť numeric features,
- `contract_type`,
- `region`,
- `auto_pay`.

Event corpus je dôveryhodný vstup do aggregate buildera. Baseline ani monitoring window neukladajú raw recordy. Ukladajú iba counts, feature distributions, latency, error rate a prediction aggregates. Source event log môže mať vlastný retention a access policy mimo tohto labu.

## Baseline profile

Baseline musí obsahovať aspoň jeden úspešný event a nesmie obsahovať failed outcomes. Profile obsahuje:

- profile name a generation,
- total/success/failure counts,
- error rate a explicitný `no_data`,
- latency minimum, average, p95 a maximum,
- positive prediction rate a average probability,
- numeric quantile boundaries, proportions, mean, minimum a maximum,
- categorical categories, proportions a `other_proportion`,
- canonical `baseline_profile_id`.

Numeric boundaries sa vytvoria iba z baseline-u. Monitoring window používa tie isté boundaries; nesmie si vytvoriť nové bins, pretože tým by sa zmenil porovnávací subject.

## Monitoring window

Window je viazané na:

- exact `baseline_profile_id`,
- exact `deployment_id`.

Window môže obsahovať úspešné aj neúspešné events. Ak neobsahuje žiadny event, `no_data=true`, latency je `null` a prediction aggregates sú `null`. Tento stav je explicitne otvorený; nie je healthy.

Window ukladá canonical `monitoring_window_id`. Zmena countu, error rate-u, distribution alebo deployment subjectu bez nového ID je tampering a validácia ju odmietne.

## Drift metriky

Numeric features používajú Population Stability Index nad baseline bins:

```text
PSI = Σ (actual - expected) × ln((actual + ε) / (expected + ε))
```

Categorical features používajú total variation distance nad baseline categories a samostatným `other` bucketom.

Prediction layer porovnáva absolute delta positive prediction rate. Operational layer používa observed error rate.

Thresholdy sú explicitné vstupy drift reportu:

- numeric PSI,
- categorical TVD,
- prediction-rate delta,
- maximum error rate,
- minimum successful events.

## Status precedence

Drift report má presne jeden stav:

| Stav | Význam |
|---|---|
| `no_data` | Window nemá events. |
| `insufficient_evidence` | Úspešných events je menej než minimum. |
| `operational_failure` | Error rate prekročil operational threshold. |
| `drift_detected` | Evidence volume je dostatočný a drift signal prekročil threshold. |
| `stable` | Evidence je dostatočný a žiadny gate nebol prekročený. |

Precedence je zámerná. Vysoký error rate nie je automaticky training signal. Najprv treba vyriešiť serving, dependency, network alebo telemetry failure.

Drift report obsahuje exact baseline/window/deployment IDs, thresholds, per-feature PSI/TVD, exceeded feature names, prediction delta, observed error rate a canonical `drift_report_id`.

## Reproducible drift injection

`inject_drift` má dva režimy:

- `control` — exact copy bez zmeny,
- `shift` — deterministic zmena spend, support tickets, login activity, contract a autopay distribution.

Control dataset musí zostať `stable`. Shift dataset musí vytvoriť reproducible drift signals pri rovnakých thresholds. Injection je testovací mechanizmus; nepredstavuje production data generator.

## Retraining proposal

Proposal sa vytvorí iba z canonical-valid drift reportu.

- `drift_detected` → `approval_required`,
- každý iný status → `blocked`.

Proposal pinne:

- exact `drift_report_id`,
- exact `deployment_id`,
- current model SHA-256,
- policy generation,
- canonical `retraining_proposal_id`.

Upravený drift status s pôvodným report ID sa odmietne. Operational failure, no-data, insufficient evidence a stable window nemôžu byť schválené na retraining.

## Human approval

Approval vyžaduje:

- canonical proposal,
- exact expected proposal ID,
- approvera,
- approval generation.

Výstup pinne proposal, drift report, deployment, model SHA, policy generation a authorized action `start_controlled_retraining`. Canonical `retraining_approval_id` sa zmení pri každej zmene subjectu alebo approval generation.

Approval neštartuje training. Je to authorization artifact pre budúci executor. Executor musí ešte overiť:

- approval ID a payload,
- že current deployment/model stále zodpovedá proposal subjectu,
- operation ID a read-before-retry state,
- exact training dataset generation,
- výsledný candidate/version read-back.

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
  --expected-proposal-id <exact-proposal-id> \
  --approver ml-platform-owner \
  --approval-generation approval-2026-08-06 \
  --output labs/mlops/.runtime/retraining-approval.json
```

Nesprávny proposal ID, upravený proposal alebo blocked action skončia refusal bez approval outputu.

## Testovaná hranica

Exact-source tests pokrývajú:

- stable control window,
- reproducible shifted window,
- no-data,
- insufficient evidence,
- operational failure oddelený od driftu,
- proposal blocked pre nedriftové stavy,
- exact approval pre drift,
- stale proposal refusal,
- tampered drift-report refusal,
- tampered proposal refusal,
- baseline/window tampering,
- executable monitoring a approval lifecycle.

## Neoverená hranica

Tento blok nepreukazuje:

- production telemetry collection,
- online feature store alebo streaming aggregation,
- reálny drift počas času,
- label/concept drift,
- alert delivery,
- schválenie cez externý identity/approval systém,
- samotný retraining execution,
- nový candidate, Registry version alebo serving promotion,
- business outcome.

Practical v1 monitoring, drift a controlled retraining checkbox zostáva otvorený do live evidence a schváleného end-to-end retraining runu.
