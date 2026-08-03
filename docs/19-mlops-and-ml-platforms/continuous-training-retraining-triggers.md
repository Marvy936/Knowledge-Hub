# Continuous Training a retraining triggers

Continuous Training je riadený proces, ktorý vytvára nový model candidate, keď nastane explicitná potreba a sú splnené data, label, capacity a governance podmienky. Nie je to synonymum pre cron job, ktorý pravidelne volá training script. Periodický trigger môže spustiť pipeline, ale nevysvetľuje, či existujú nové mature labels, či sa zmenila population, či je incident observation pravdivá alebo či ďalší training run prinesie inú informáciu.

CT vlastní rozhodnutie „má vzniknúť nový candidate“. Continuous Delivery vlastní neskorší presun validated candidate do runtime. Tieto authority sa nesmú zlúčiť do jedného automatického pathu, v ktorom drift alert priamo prepisuje production model.

Incident `MLOPS-PAY-93` začína tým, že Atlas Payments dostal alert na pokles modelového recallu. Alert používal iba prípady, ktoré už analytici dokončili, takže denominator bol selektívny a labels ešte neboli mature. Dva nezávislé automaty spustili retraining: denný cron a drift webhook. Obe pipeline použili rovnaký dataset watermark, pretože ingestion meškala, ale vytvorili dve Registry versions. Novší run skončil neskôr a prepisoval alias starším candidate-om. Tím minul GPU capacity bez toho, aby získal nový informačný stav.

## 1. Dominantný Continuous Training lifecycle

CT lifecycle začína trigger evidence a končí candidate modelom, nie deploymentom.

```text
trigger signal
→ signal validation a deduplication
→ data/label readiness
→ retraining policy a approval boundary
→ immutable training subject
→ training a evaluation
→ candidate registration
→ validation/promotion workflow
→ explicit hold, reject alebo delivery eligibility
```

Každá fáza môže rozhodnúť, že training sa nespustí. „No-op“ je validný outcome, ak od posledného accepted training subjectu nepribudli nové mature labels alebo trigger neprešiel confidence a persistence gate-om.

## 2. Exact retraining subject

Retraining request musí pomenovať dôvod, source signal, logical data interval, label cutoff, baseline model a deduplication key.

```yaml
retraining_subject: MLOPS-PAY-CT-2026-08-03-017
trigger_type: performance_degradation
trigger_evidence_digest: sha256:41aa...90bd
trigger_window:
  start: 2026-07-20T00:00:00Z
  end_exclusive: 2026-08-03T00:00:00Z
minimum_persistence_windows: 3
training_data_manifest: sha256:72bd...0f11
label_contract: confirmed_loss_within_30d-v2
label_cutoff: 2026-09-02T00:00:00Z
baseline_release: MLOPS-PAY-RISK-PROD-2026-07-r29
deduplication_key: risk-v2:2026-08-03:sha256-72bd
promotion_mode: validation-required
```

Ak dva triggers vytvoria rovnaký deduplication key, druhý request sa pripojí k existujúcej operation alebo skončí ako no-op. Vytvorenie ďalšieho run ID nie je samo o sebe bezpečná deduplikácia.

## 3. Typy triggerov a ich dôkazná hranica

Periodický trigger je vhodný, keď dáta a labels prirodzene pribúdajú v predvídateľnom intervale. Kubeflow Pipelines recurring run môže používať interval alebo cron trigger a limitovať concurrent runs. Scheduler však iba vytvára nové pipeline runs; nepreukazuje data readiness ani potrebu retrainingu.

Data-volume trigger reaguje na dostatočný počet nových eligible observations alebo mature labels. Performance trigger reaguje na zhoršenie outcome metricu. Drift trigger reaguje na zmenu dát, predictions alebo learned relationship. Business trigger môže byť zmena produktu, policy, ceny alebo regulácie. Manuálny trigger zostáva dôležitý pri incidente alebo planned refreshi.

Každý trigger potrebuje vlastný falsifier. Drift bez performance zhoršenia nemusí vyžadovať retraining. Performance zhoršenie môže pochádzať z feature outage alebo policy change. Nové dáta môžu byť iba duplicates. Trigger je hypothesis, nie root-cause verdict.

## 4. Data a label readiness

Training sa nesmie spustiť iba preto, že source partition existuje. Readiness contract kontroluje completeness, schema, event-time watermark, label maturity, duplicate handling, cohort coverage a leakage boundary.

```text
source objects present
≠ ingestion complete
≠ late events uzavreté
≠ labels mature
≠ split generation validná
≠ retraining dataset vhodný
```

Pri 30-dňovom fraud labeli nemá run 3. augusta používať operácie z 2. augusta ako definitívne negatives. Môže ich zahrnúť ako unlabeled population pre monitoring, ale supervised training cutoff musí rešpektovať maturity contract.

Readiness manifest obsahuje expected a actual partition counts, late-arrival tolerance a data-quality verdict. Ak ingestion mešká, recurring run sa odloží alebo skončí ako blocked, nie ako successful training nad starým snapshotom.

## 5. Watermark a logical interval

Processing time hovorí, kedy platforma dáta spracovala. Event time hovorí, kedy business event nastal. CT pipeline potrebuje logical interval a watermark, ktorý určuje, do akého event time sú data považované za dostatočne complete.

```yaml
logical_interval:
  start: 2026-06-01T00:00:00Z
  end_exclusive: 2026-08-01T00:00:00Z
source_watermark: 2026-08-01T00:00:00Z
allowed_lateness: 48h
label_watermark: 2026-07-01T00:00:00Z
```

Backfill vytvára nový dataset generation, ak prišli relevantné late events. Nemá potichu prepísať snapshot použitý starším modelom. CT policy rozhodne, či correction generation vyžaduje retraining podľa affected population a impactu.

## 6. Trigger validation a persistence

Jednorazový spike môže byť measurement noise. Trigger policy preto používa minimum sample, confidence, consecutive windows, telemetry completeness a suppression interval. Missing data nesmie byť interpretovaná ako zlepšenie ani zhoršenie bez explicitnej policy.

```python
should_trigger = (
    evidence.complete
    and evidence.mature_labels >= 5_000
    and evidence.recall_drop >= 0.04
    and evidence.consecutive_failed_windows >= 3
    and not active_retraining_for(evidence.deduplication_key)
)
```

Toto je iba decision surface. Reálna policy potrebuje segment guardrails, baseline generation a audit. Threshold sa versionuje, pretože jeho zmena mení frekvenciu a náklady CT.

## 7. Overlap a concurrency control

Recurring runs môžu prekrývať execution, ak training trvá dlhšie než schedule. Platforma môže limitovať maximum concurrent runs, ale to nerieši semantic overlap dvoch rôznych trigger sources.

CT coordinator drží lease alebo operation ledger podľa model family a data generation. Nový request porovná active subject. Ak prináša rovnaké dáta a policy, pripojí sa k existujúcemu runu. Ak prináša novšiu generation, môže počkať, zrušiť starší low-value run alebo vytvoriť explicitný superseding subject.

Cancellation nie je okamžitá. GPU workers, checkpoint uploads a Registry writes môžu pokračovať. Cancel path musí prečítať finálny outcome a označiť artifacts ako superseded alebo quarantined.

## 8. Retraining policy a cost

CT rozhoduje aj o ekonomike. Full retraining, warm start, incremental update a threshold-only change majú odlišný cost a risk. Nie každý symptom vyžaduje nové weights.

Ak sa zmenila queue capacity, môže stačiť policy update. Ak online features sú stale, treba obnoviť materialization. Ak sa zmenil label definition, training je potrebný, ale staré a nové metrics nie sú priamo porovnateľné. Ak pribudlo málo dát, retraining môže vytvoriť variance bez reálneho zlepšenia.

Policy zaznamenáva expected benefit, compute budget, carbon/cost limit a maximum frequency. Prekročenie budgetu vyžaduje approval alebo degraded strategy, nie tiché vypnutie validation.

## 9. Training trigger oproti promotion triggeru

Successful retraining vytvorí candidate a evaluation bundle. Nemá automaticky posunúť production alias. Promotion gate porovná candidate s baseline, segment constraints, calibration, latency, package a governance evidence.

```text
CT trigger accepted
→ candidate 141 created
→ validation failed on high-value cohort
→ candidate retained for diagnosis
→ production release unchanged
```

Taký outcome je správny. CT availability sa nemeria percentom candidates nasadených do produkcie. Môže sa merať časom od validného triggeru po dôveryhodný candidate alebo reject verdict.

## 10. Feedback loops a selective labels

Model ovplyvňuje, ktoré prípady dostanú action a následne label. Ak sa do trainingu dostávajú iba reviewed cases, CT môže zosilňovať historickú selection bias. Trigger metric aj retraining dataset potrebujú exposure a action propensity.

Exploration cohort, random audit sample alebo causal correction môže zlepšiť observability, ale má business cost. CT dokumentácia musí uviesť, ktoré labels chýbajú a čo inference o unobserved population predpokladá.

Automatické retraining z vlastných predictions bez independent ground truth vytvára self-training loop. To je samostatný design s confidence a poisoning controls, nie default CT.

## 11. Poisoning a security boundary

Trigger endpoint, dataset ingestion a labels sú attack surfaces. Útočník môže vytvoriť drift, zaplaviť retraining requests alebo manipulovať labels. CT service account má iba potrebné read/write paths a trigger event je autentizovaný, autorizovaný a auditovaný.

Data quarantine a anomaly checks predchádzajú trainingu. Emergency disable switch zastaví nové runs bez mazania evidence. Model family a tenant isolation zabraňujú tomu, aby trigger jedného subjectu spotreboval všetku shared GPU capacity.

## 12. Evidence hierarchy

Configured evidence je recurring-run alebo event policy. Resolved evidence je exact trigger evaluation a immutable training subject. Loaded evidence je pipeline run a training workload. Candidate evidence je package, metrics a validation bundle. Production evidence vzniká až po samostatnom delivery.

```bash
# Recurring-run alebo run metadata
kfp recurring-run get --recurring-run-id "$JOB_ID"
kfp run get --run-id "$RUN_ID"

# Data readiness
python scripts/verify_readiness.py "$DATASET_MANIFEST"

# Active operation ledger
curl -sS "$CT_API/operations/$DEDUP_KEY"
```

Scheduler UI nepreukazuje data readiness. Training run success nepreukazuje promotion eligibility. Registry version nepreukazuje deployment.

## 13. Competing failure hypotheses

Keď CT spúšťa príliš často alebo vytvára slabé candidates, hypotheses zahŕňajú measurement error, incomplete labels, duplicate triggers, stale watermark, feature outage, policy change, genuine concept shift a training regression. First divergence sa hľadá pred trainingom: source telemetry, label maturity, dedup ledger a data snapshot.

Ak candidate nepriniesol nové správanie, porovná sa dataset delta, optimizer steps a artifact digest. Dva runs nad rovnakými inputs môžu byť užitočný stability test, ale nesmú byť zamieňané za dva nezávislé retraining opportunities.

## 14. Recovery a acceptance

Containment vypne alebo pozastaví triggers, nastaví concurrency na nulu a zachová active runs. Recovery opraví signal query, watermark alebo dedup policy a vytvorí novú generation. Staré candidates zostanú označené ako superseded alebo invalid, nie vymazané bez lineage.

Pozitívny test vytvorí jeden run pre validný persistent trigger a complete data. Forbidden test odmietne immature labels, duplicate key a trigger bez evidence digestu. Recovery test simuluje timeout po run creation a overí read-before-retry. Second-operation test znovu doručí ten istý event a očakáva no-op alebo reference na pôvodný run.

CT je prijatá, keď nový candidate vzniká iba z nového a dôveryhodného informačného stavu, overlapping triggers sú deterministicky riešené a žiadny training outcome neobchádza validation a delivery gates.

## Primárne zdroje

- [Kubeflow Pipelines — Run and recurring run](https://www.kubeflow.org/docs/components/pipelines/concepts/run/)
- [Kubeflow Pipelines — Run trigger](https://www.kubeflow.org/docs/components/pipelines/concepts/run-trigger/)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Continuous Delivery pre modely](continuous-delivery-for-models.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Model validation a promotion gates →](model-validation-promotion-gates.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
