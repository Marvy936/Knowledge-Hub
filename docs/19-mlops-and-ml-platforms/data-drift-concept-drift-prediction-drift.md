# Data drift, concept drift a prediction drift

Drift označuje zmenu štatistického alebo rozhodovacieho vzťahu medzi referenčnou a aktuálnou populáciou. Nie je to jeden jav ani automatický dôkaz, že model zlyhal. Data drift môže zmeniť distribúciu vstupov bez zhoršenia performance, concept drift môže zhoršiť performance bez výraznej zmeny marginálnych vstupov a prediction drift môže vzniknúť aj po zmene threshold alebo policy bez zmeny modelu.

V incidente `MLOPS-PAY-94` alert hlásil výrazný prediction drift a automaticky vytvoril retraining request. Reference bola mesačná training population, current window obsahovalo iba requesty, ktoré neprešli fallbackom, a candidate mal iný review-capacity threshold. Zmena score distribution preto kombinovala traffic mix, selective observation a policy change. Keď sa population zrekonštruovala podľa actual eligible requests, prvá divergencia bola GPU timeout a fallback, nie concept drift. Kapitola preto používa drift ako hypothesis evidence, nie ako automatický promotion alebo retraining trigger.

## 1. Formálne rozdiely medzi driftmi

Nech \(X\) označuje features, \(Y\) ground truth a \(\hat{Y}\) prediction. Data alebo covariate drift opisuje zmenu \(P(X)\). Label alebo target drift opisuje zmenu \(P(Y)\). Prediction drift opisuje zmenu \(P(\hat{Y})\). Concept drift opisuje zmenu vzťahu \(P(Y \mid X)\).

Tieto distribúcie sa môžu meniť nezávisle. Marketingová kampaň môže zmeniť \(P(X)\), no model zostane presný. Útočník môže zmeniť správanie tak, že rovnaké features majú iný risk, teda zmení sa \(P(Y \mid X)\). Threshold change môže zmeniť action a prediction class distribution bez zmeny score modelu. Preto alert musí pomenovať, čo presne porovnáva.

```text
data drift        P_ref(X)      vs P_cur(X)
target drift      P_ref(Y)      vs P_cur(Y)
prediction drift  P_ref(Ŷ)      vs P_cur(Ŷ)
concept drift     P_ref(Y|X)    vs P_cur(Y|X)
```

Concept drift sa nedá priamo potvrdiť bez labels alebo ďalších silných predpokladov. Performance estimation bez labels je modelový odhad s vlastnou uncertainty a nesmie sa prezentovať ako realized performance.

## 2. Exact drift subject

Drift run je reprodukovateľný iba ak viaže reference a current population, feature/transform generation, release exposure, segment, method, threshold a multiplicity policy. Samotný názov feature alebo dátum dashboardu nestačí.

```yaml
drift_run_id: fraud-drift-2026-08-03T10
reference:
  dataset: production-stable-2026-W27
  release_id: fraud-serving-2026-07-01.2
  interval: 2026-06-29/2026-07-06
current:
  release_id: fraud-serving-2026-08-03.4
  interval: 2026-08-03T09:00/2026-08-03T10:00
population:
  eligibility: all_fraud_requests_v7
  include_fallback: true
  segment: merchant_online_eu
features:
  generation: fraud-request-v11
method:
  numeric: wasserstein
  categorical: jensen_shannon
  multiple_testing: benjamini_hochberg
policy:
  minimum_rows: 5000
  alert_if_share_drifted_gt: 0.2
```

Reference selection je authority decision. Training reference odpovedá, či production pripomína training data. Stable-production reference odpovedá, či sa traffic zmenil od posledného zdravého obdobia. Seasonally matched reference odpovedá, či zmena presahuje očakávanú seasonality. Jeden universal reference neexistuje.

Current window používa event time a explicitný completeness watermark. Processing-time window môže porovnávať oneskorené alebo neúplné dáta a vytvoriť false drift.

## 3. Population a exposure correctness

Drift analysis musí používať správnu population. Ak current dataset obsahuje iba úspešné model invocations, ale reference všetky eligible requests, fallback a schema rejection zmenia population ešte pred štatistickým testom. Ide o selection bias, nie nutne drift v user trafficu.

Population chain:

```text
eligible requests
→ assigned release
→ actually routed
→ features resolved
→ model invoked
→ prediction emitted
→ action taken
→ label observed
```

Každý drift typ potrebuje iný cutoff. Input data drift môže používať eligible requesty po schema normalization. Prediction drift používa úspešne scored requesty a samostatne reportuje fallback share. Concept/performance analysis používa label-mature joined population a coverage.

Pri A/B alebo canary sa varianty porovnávajú na stable assignment population. Porovnanie candidate score distribution s controlom po odlišných fallback alebo latency filters je biased.

## 4. Data drift methods a interpretácia

Numerické features možno porovnávať pomocou Kolmogorov-Smirnov testu, Wasserstein distance, Jensen-Shannon divergence po discretizácii alebo Population Stability Index. Kategorické features možno porovnávať chi-square testom, total variation alebo Jensen-Shannon divergence. Žiadna metóda nie je univerzálna; voľba závisí od sample size, support, missingness a praktickej významnosti.

P-value odpovedá, či je rozdiel nepravdepodobný pri null hypothesis, nie či je prevádzkovo dôležitý. Pri veľkom sample bude významná aj malá zmena. Preto sa kombinuje effect size, minimum sample a domain threshold.

PSI sa často interpretuje pevnými hranicami, ale tie nie sú prirodzeným zákonom. Výsledok závisí od binning a reference. Method a bins musia byť versioned.

Missingness, category novelty a range violations sa sledujú samostatne. Zmena z 0 na 5 % missing môže byť kritickejšia než mierny shift distribúcie nepoškodenej feature.

## 5. Multiple testing a segment explosion

Pri stovkách features a segmentov vzniknú false positives aj bez reálnej zmeny. Ak sa pre každú feature vykoná nezávislý test s alpha 0.05, očakáva sa množstvo náhodných alertov. Monitoring policy preto používa correction, hierarchický gate alebo požiadavku na podiel drifted features.

Segmenty sú potrebné, pretože aggregate môže skrývať lokálny drift. Zároveň príliš jemné segmenty znižujú sample size a zvyšujú noise. Segment definition musí byť stabilná a business relevantná, napríklad region × channel, nie dynamicky generovaný customer ID.

Drift report by mal uvádzať confidence/effect, sample counts, missingness, coverage a top contributing segments. Jedno červené číslo bez population evidence nie je actionable.

## 6. Prediction drift a policy changes

Prediction drift možno sledovať bez labels. Zahŕňa score distribution, predicted class rate, confidence, abstention a action rate. Treba však oddeliť raw model score od thresholded prediction a downstream action.

```text
raw score
→ calibration
→ threshold
→ policy constraints
→ capacity suppression
→ final action
```

Zmena threshold alebo review capacity môže zmeniť action distribution bez zmeny raw score. Fallback model môže mať inú score scale. Monitoring preto reportuje release, fallback class, threshold generation a policy generation.

Prediction drift je early-warning signal. Môže indikovať input drift, feature bug, population change alebo concept change. Nemôže sám určiť príčinu ani performance direction.

## 7. Concept drift a delayed labels

Concept drift vyžaduje zmenu mapovania medzi inputs a outcomes. Pri dostupných mature labels sa porovnáva conditional performance podľa feature regionov, segmentov alebo času. Možno sledovať residual distribution, calibration a subgroup error.

Delayed labels vytvárajú right censoring. Recent window má menej labels a často odlišný mix prípadov. Concept drift report preto používa maturity cutoff a label coverage. Porovnáva len windows, ktoré dosiahli kompatibilnú maturity, alebo používa survival/weighting model s explicitnými predpokladmi.

Selective labels sú vážnejšie: outcome sa pozoruje iba po určitej action. Napríklad manuálne review vytvorí rýchly fraud label, automaticky schválená transakcia môže zostať neoverená. Realized performance na pozorovaných labels potom nereprezentuje všetky predictions. Experiment, audit sample alebo inverse propensity weighting môže pomôcť, ale assumption a uncertainty musia byť zdokumentované.

## 8. Drift, performance a causality

Data drift nie je synonymum performance degradation. Performance degradation môže vzniknúť aj bez driftu, napríklad po label definition change, leakage odstránení alebo concept change v malej rozhodujúcej oblasti. Preto sa drift koreluje s realized alebo estimated performance, service health a business outcome.

Causal poradie pri incidente:

```text
GPU queue increase
→ timeout a fallback
→ changed scored population
→ prediction distribution shift
→ review action shift
→ delayed label mix shift
```

Ak tím začne na konci a retrainuje model, príčina zostane. First-divergence analysis musí zahrnúť infra, feature, model, policy a outcome timeline.

Drift alert môže otvoriť investigation alebo spustiť shadow retraining candidate, ale nesmie automaticky obísť validation, promotion a delivery gates. Continuous Training trigger musí overiť data completeness, label maturity a competing hypotheses.

## 9. Practical computation contract

Jednoduchý drift job najprv validuje schema a population counts, potom vypočíta metrics a uloží report s manifestom. Pseudokód:

```python
def run_drift(reference, current, contract):
    validate_schema(reference, contract.schema)
    validate_schema(current, contract.schema)
    validate_population(reference, current, contract.population)

    results = []
    for feature in contract.features:
        ref = reference[feature].dropna()
        cur = current[feature].dropna()
        results.append(
            compare_distribution(
                feature=feature,
                reference=ref,
                current=cur,
                method=contract.method_for(feature),
            )
        )

    corrected = apply_multiple_testing(results, contract.multiple_testing)
    return build_report(
        subject=contract.subject,
        sample_counts=count_rows(reference, current),
        missingness=missingness(reference, current),
        results=corrected,
    )
```

Produkčný job musí pinovať code/image digest, dataset URIs a checksums. Report artifact obsahuje raw counts a method parameters, aby dashboard nebol jedinou authority.

Evidently alebo iný framework môže vypočítať drift metrics, ale platforma stále vlastní population, reference, threshold a action policy. Tool default nie je business contract.

## 10. Failure hypotheses a recovery

Drift spike môže byť reálny traffic shift, schema/units bug, transform version mismatch, incomplete window, fallback selection, logging duplication, seasonality alebo release/policy change. Hypotézy sa testujú podľa najskoršej divergencie: counts a completeness, schema, feature generation, release exposure, service result classes, potom distributions.

Containment závisí od príčiny. Pri feature bug sa vypne alebo rollbackne feature generation. Pri fallback selection sa obnoví serving capacity. Pri reálnom drift-e sa môže vytvoriť candidate dataset a retraining run, ale produkčný model sa nemení bez validation a rollout-u.

Recovery sa neuzatvára zhasnutím alertu. Reference/current windows sa prepočítajú s opravenou population, service a business metrics sa stabilizujú a nasledujúce kompletné window potvrdí výsledok.

## 11. Acceptance boundaries

Pozitívna acceptance vyžaduje versioned drift subject, complete event-time windows, explicitnú population, sample counts, effect size, multiplicity handling a oddelenie data, prediction, target a concept claims. Recovery acceptance vyžaduje odstránenie first divergence a prepočet reportu bez manuálneho filtrovania.

Forbidden acceptance je automatický retrain alebo rollback iba na základe jedného drift score, p-value bez effect size, porovnanie nekompatibilných populations alebo concept-drift claim bez labels/predpokladov. Rovnako zakázané je ignorovať fallback a missing telemetry.

Second-operation test spracuje ďalšie kompletné window rovnakým contractom. Ak sa report nedá reprodukovať, reference sa potichu posunula alebo population query závisí od processing-time race, drift monitoring nie je authoritative. Stabilný systém musí vysvetliť rovnaký verdict z uložených manifests a artifacts.
