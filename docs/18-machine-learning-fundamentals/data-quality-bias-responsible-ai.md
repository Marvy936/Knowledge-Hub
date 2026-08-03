# Data quality, bias a responsible AI

Data quality v machine learning nie je všeobecná vlastnosť tabuľky. Dataset môže byť syntakticky validný, úplný a bez duplicates, no nevhodný pre konkrétny target, population, deployment time alebo decision. Bias nie je iba jeden numerický fairness gap; môže vzniknúť v tom, kto sa do datasetu dostane, ako sa meria reality, kto dostane label, ktoré outcomes sa považujú za úspech, ako model transformuje prediction na action a ako action spätne mení budúce dáta. Responsible AI preto prepája data/model engineering, risk ownership, human oversight, security, privacy, transparency, monitoring a recovery.

Incident `ML-PAY-88` sa v Atlas Payments rozšíril z calibration a explainability do governance. Training dataset obsahoval iba cases, ktoré predchádzajúca fraud policy poslala na investigation. „Negative“ labels boli často iba absencia potvrdeného fraudu, nie potvrdený legitimate outcome. Campaign traffic z nových merchants mal krátku label maturity a vysoký missing-feature rate. Aggregate performance vyzerala prijateľne, ale model zvyšoval manual review pre jednu geography a znižoval approval rate pre low-history merchants. Tím reportoval parity iba na accepted predictions, protected attributes odstránil z features a považoval tým fairness za vyriešenú. Kapitola preto sleduje quality a bias od population a measurementu až po action, impact a governance evidence.

## 1. Dominantný responsible-ML lifecycle

Responsible AI lifecycle začína intended use a affected parties. Dataset a labels sa hodnotia voči tomuto use case-u, nie iba proti schema. Model a policy sa následne testujú na utility, harms, subgroup coverage a human/system interactions. Risk acceptance má ownera a monitorovanie pokračuje po deployment-e.

```text
intended use, non-use a affected parties
→ exact population, data sources a collection process
→ measurement, label a sampling contract
→ quality, representativeness, privacy a security validation
→ model/evaluation/policy generation
→ utility, subgroup, harm a human-oversight evidence
→ accountable risk decision a documented limitations
→ deployment, monitoring, incident response a appeal/correction
→ second-window a impact acceptance
```

Tento chain rozlišuje model metric od system impactu. Model môže mať equalized offline rates a downstream workflow môže stále vytvárať unequal delays alebo denial. Responsible verdict preto zahŕňa celý socio-technical decision path.

## 2. Exact responsible-AI subject

Risk alebo fairness report musí identifikovať use case, model, policy, population, groups, outcomes, time horizon a authority. Bez toho sa metric stáva prenosným sloganom bez scope-u.

```yaml
responsible_ai_subject: ML-PAY-RAI-2026-08-v4
use_case:
  intended: prioritize_payment_operations_for_human_fraud_review
  forbidden:
    - automatic_criminal_accusation
    - customer_identity_inference
    - use_outside_eu_card_not_present_scope
stakeholders:
  affected: [customers, merchants, reviewers]
  owners: [risk_product, ml_platform, compliance]
model:
  digest: sha256:1f92...b0c4
  calibration_digest: sha256:8a17...71e3
policy:
  generation: ML-PAY-QUEUE-2026-08-v7
population:
  manifest: eu-cnp-mature-2026w28-w30-v4
  label_maturity_days: 21
groups:
  analysis_only: [country, merchant_age_band, customer_age_band]
outcomes:
  model: [precision, recall, calibration]
  workflow: [review_rate, delay, approval_rate, recovered_loss]
  harm: [false_block, missed_fraud, appeal_overturn]
```

Sensitive attributes môžu byť zakázané ako prediction inputs a zároveň potrebné pre controlled evaluation. Access, legal basis, retention a aggregation constraints sú samostatná governance vrstva.

## 3. Data quality ako fitness for purpose

Quality dimensions sa interpretujú voči intended use:

- validity — hodnota spĺňa schema, domain a temporal rules;
- completeness — povinné fields alebo records nechýbajú pre relevantnú population;
- accuracy — measurement zodpovedá intended real-world quantity;
- consistency — rovnaký concept má kompatibilné semantics naprieč sources/time;
- uniqueness — duplicate observations alebo entity aliases sú identifikované;
- timeliness — data boli dostupné pri prediction time a nie až po outcome;
- representativeness — sample pokrýva deployment population a critical cohorts;
- lineage — source, transformation, ownership a mutation sa dajú auditovať.

Stopercentná completeness môže byť zlá, ak missing values boli nepresne imputované a pôvodný missingness signal sa stratil. Syntaktická accuracy timestampu nepreukazuje správny event time. Quality gate preto kombinuje automated constraints s domain validation a outcome-based evidence.

## 4. Population, sampling frame a coverage

Intended population je množina entities/events, pre ktoré sa má systém používať. Sampling frame je praktický mechanizmus, z ktorého dataset získava records. Coverage error vzniká, keď frame systematicky vynecháva alebo duplikuje časti population.

```text
intended population
→ observable platform events
→ eligible records
→ successfully joined features
→ labeled mature cases
→ training/evaluation sample
```

Každý prechod má counts a subgroup rates. Model trained iba na successfully investigated cases nepozná unreviewed outcomes. Random split z takého sample-u je representative iba pre selective frame, nie pre všetky payments.

Sampling weights môžu korigovať known selection probabilities, ale nevytvoria informáciu o úplne nepozorovaných groups. Data acquisition alebo exploration je často potrebná.

## 5. Measurement bias

Measurement bias vzniká, keď observed feature alebo label systematicky meria concept odlišne medzi groups, times alebo sources. Fraud report rate môže závisieť od awareness a investigation intensity, nie iba od actual fraud. Device-risk signal môže mať odlišnú accuracy podľa platformy.

```text
latent concept
→ measurement process
→ recorded variable
→ preprocessing
→ model feature/label
```

Zlyhanie môže byť differential: rovnaký real-world state vedie k odlišnej recorded value podľa group. Technical sensor accuracy, language coverage, manual review guidelines a source-system outages patria do model risk.

Validácia porovnáva measurement s alternate authority alebo audit sample, nie iba missing rate. Ak ground truth neexistuje, uncertainty a limitations sa explicitne dokumentujú.

## 6. Label quality a target validity

Label je operational definition targetu, nie čistá pravda. Dôležité dimensions:

- source authority a adjudication process;
- maturity delay a censoring;
- inter-annotator agreement a guideline version;
- positive/negative/unknown semantics;
- label leakage z post-outcome data;
- differential error medzi cohorts;
- feedback zo starej model policy.

```yaml
label_contract:
  positive: confirmed_recoverable_loss_within_21d
  negative: mature_no_loss_after_21d
  unknown: unresolved_or_unobserved
  adjudication: chargeback_plus_manual_confirmation_v4
  guideline_version: fraud-ops-2026-06
```

Unknown nesmie byť automaticky mapované na negative. Pri delayed outcomes sa evaluation cutoff nastaví tak, aby labels dozreli. Noisy label model môže optimalizovať consistency s chybným processom namiesto intended business conceptu.

## 7. Historical a societal bias

Historical data odrážajú predchádzajúce decisions, access, enforcement a inequalities. Predikovať historical approval alebo investigation outcome môže reprodukovať policy, ktorú organizácia chce zmeniť.

```text
past policy
→ who received opportunity/review
→ observed outcomes
→ training labels
→ model learns past policy
→ future policy reinforcement
```

High predictive accuracy voči historical labelu nie je automaticky normative acceptance. Intended target sa musí oddeliť od proxy typu „reviewer chose to escalate“. Responsible AI vyžaduje domain, legal a stakeholder decision o tom, čo sa má optimalizovať.

## 8. Representation bias a subgroup support

Representation bias vzniká, keď dataset nedostatočne pokrýva relevantné groups alebo situations. Aggregate sample count nestačí; support sa hodnotí v intersections a operational conditions.

```text
country × merchant_age × traffic_source × device_platform
```

Intersectional slices rýchlo znižujú sample size. Report preto kombinuje predeclared mandatory groups, minimum support, uncertainty a „insufficient evidence“ stav. Vynechať sparse group z reportu je forbidden; rovnako zavádzajúce je vydávať highly uncertain point estimate za presný verdict.

Oversampling existujúcich minority rows nezväčší real-world diversity. Missing subtypes potrebujú collection alebo targeted validation.

## 9. Proxy features

Protected alebo sensitive attribute môže byť neprítomný, no model ho môže inferovať z geography, name, language, device, behavior alebo correlated socioeconomic signals. Proxy nie je definovaná iba correlation coefficientom; relevantná je model reliance a effect na action.

```text
remove direct attribute
≠ remove encoded information
≠ prove equal outcomes
```

Proxy investigation kombinuje lineage, domain review, feature importance/ablation, predictability of sensitive attribute, subgroup performance a policy impact. Nie každá correlated feature je automaticky zakázaná; legitímnosť závisí od use case-u a governing requirements. Decision musí byť dokumentovaný, nie vyriešený jedným technickým thresholdom.

## 10. Fairness metric subject

Fairness metric identifikuje groups, favorable/unfavorable outcome, denominator, threshold/policy, population a time. Rovnaký názov môže mať odlišný meaning podľa toho, či sa počíta nad model predictions, policy actions alebo realized outcomes.

```yaml
fairness_metric:
  name: false_positive_rate_gap
  group_attribute: merchant_age_band
  reference_group: established_merchant
  evaluated_action: manual_review_admission
  population: policy_eligible_mature_operations
  threshold_policy: ML-PAY-QUEUE-2026-08-v7
  window: 2026w28-w30
```

Groups nesmú byť inferred nezdokumentovaným modelom, ak to mení membership uncertainty. Small denominators a missing group values sa reportujú.

## 11. Demographic parity a selection rates

Demographic parity-like criterion porovnáva positive/selected action rates medzi groups bez conditioningu na label.

```text
selection_rate_g = selected_g / eligible_g
```

Je relevantný pri access alebo opportunity otázkach, ale môže konfliktovať s utility alebo label-conditioned metrics, ak base rates a measurement process sa líšia. Equal selection rate nepreukazuje equal error rates ani equal benefit. Zároveň rozdiel selection rates je dôležitý impact signal aj vtedy, keď model performance metrics vyzerajú podobne.

Analysis musí rozlíšiť model predicted positive a final reviewed/approved action. Capacity queue alebo human override môže parity výrazne zmeniť.

## 12. Equal opportunity a equalized odds

Equal opportunity-like criterion porovnáva true-positive rates/recall medzi groups. Equalized odds-like analysis zohľadňuje true-positive aj false-positive rates.

```text
TPR_g = TP_g / actual_positive_g
FPR_g = FP_g / actual_negative_g
```

Tieto metrics závisia od label validity a maturity. Ak investigation intensity ovplyvňuje, ktoré positives sa potvrdia, observed TPR nie je čistý system performance. Threshold adjustment per group môže zlepšiť metric, ale prináša policy, legal, operational a calibration trade-offs.

Nie je možné všeobecne maximalizovať všetky fairness criteria, calibration a utility naraz pri odlišných base rates. Trade-off je governance decision, nie dôvod vybrať najvýhodnejší metric post-hoc.

## 13. Predictive parity a calibration by group

Predictive parity porovnáva precision/positive predictive value medzi groups. Group calibration skúma, či rovnaká predicted probability zodpovedá podobnej observed frequency v každej group.

```text
for group g and score bin b:
mean_probability_g,b ≈ observed_frequency_g,b
```

Aggregate calibration môže prekryť group miscalibration. Sparse high-risk bins potrebujú uncertainty. Equal precision môže vzniknúť pri odlišnom recall a action burden. Report preto neizoluje jeden criterion od full error/cost matrix.

## 14. Individual, counterfactual a causal fairness boundaries

Group metrics hodnotia aggregates. Individual fairness chce podobné zaobchádzanie s relevantne podobnými individuals, ale definícia similarity je normatívna a domain-dependent. Counterfactual fairness-like claims vyžadujú causal model toho, ako sensitive attribute a descendants vznikajú.

Jednoduchá zmena protected field pri fixných ostatných features často vytvorí impossible counterfactual. Model prediction invariance na tomto synthetic edit-e nie je complete fairness proof. Causal claims potrebujú explicitný graph, assumptions a validation beyond standard feature attribution.

V fundamentals dokumentácii sa tieto concepts používajú na určenie hranice: observational subgroup metrics nepreukazujú counterfactual fairness.

## 15. Quality gates pred model fitom

Data contract obsahuje machine-checkable constraints a expected distributions. Gate rozlišuje hard invalidity od warning/drift.

```yaml
quality_gates:
  schema:
    operation_id_unique: required
    event_time_not_future: required
  coverage:
    feature_join_success_min: 0.995
    campaign_traffic_min_rows: 5000
  label:
    unknown_not_coerced_to_negative: required
    maturity_days_min: 21
  drift:
    country_distribution_psi_max: 0.20
```

Distribution threshold ako PSI nie je universal quality truth. Potrebuje baseline, binning a business interpretation. Stable distribution môže obsahovať persistent bias; drift môže byť legitimate product growth. Gate spúšťa investigation, nie automatickú causal diagnosis.

## 16. Datasheets, model cards a system documentation

Documentation artifacts zachytávajú intended use, collection process, composition, preprocessing, labels, metrics, limitations, ethical considerations a maintenance. Dataset datasheet a model card nie sú marketing summary; musia odkazovať na immutable manifests a evidence.

```text
dataset card/datasheet
→ source, population, collection, labels, quality, limitations
model card
→ model lineage, intended use, metrics, subgroup evidence, limitations
system card/runbook
→ policy, human workflow, monitoring, incidents, appeals
```

Document generated pri release sa stáva stale, ak population, threshold alebo workflow sa zmení. Ownership a refresh trigger sú súčasťou governance.

## 17. NIST AI RMF ako risk-management rámec

NIST AI Risk Management Framework organizuje prácu do funkcií Govern, Map, Measure a Manage. Nie je to model metric ani automatická certifikácia. Pomáha prepojiť context, ownership, measurement a treatment rizík naprieč lifecycle-om.

```text
GOVERN → policies, roles, accountability a culture
MAP    → context, stakeholders, intended use a harms
MEASURE→ tests, metrics, uncertainty a evidence
MANAGE → prioritization, treatment, monitoring a response
```

Aktuálny official AI RMF 1.0 je dobrovoľný framework a NIST ho priebežne rozvíja/reviduje. Organizácia musí mapovať framework na svoje právne, sektorové a interné povinnosti. Checklist completion bez evidence nie je risk acceptance.

## 18. Human oversight a automation bias

Human-in-the-loop neznamená automaticky bezpečný systém. Reviewer môže slepo prijímať model output, byť preťažený queue, nemať relevantné context alebo nemať authority rozhodnutie zmeniť.

```yaml
human_oversight:
  role: fraud_reviewer
  model_output_visible: probability_and_reason_codes
  override_allowed: true
  required_evidence: transaction_and_account_context
  queue_capacity_per_day: 2500
  escalation_path: senior_risk_officer
```

Oversight sa testuje cez reviewer accuracy, disagreement, time, override outcomes, cohort burden a usability. Hidden model confidence môže znížiť automation bias, ale zároveň odstrániť useful uncertainty signal; design sa validuje experimentálne.

Human review môže vytvoriť nové bias cez inconsistent guidelines. Guideline version a reviewer effects patria do label/decision evidence.

## 19. Appeals, correction a contestability

Affected party alebo internal user potrebuje mechanizmus na opravu chybných data, contest action a získanie review podľa use case-u. Appeal outcome je monitoring signal, nie iba support ticket.

```text
model/policy action
→ notice a reason
→ appeal/correction request
→ independent review
→ action reversal or confirmation
→ data/model/policy feedback with safeguards
```

Appeals nie sú automatically clean labels; ľudia s vyšším access alebo awareness apelujú častejšie. Report obsahuje appeal rate, resolution time a overturn rate po groups, ale interpretuje selection bias.

## 20. Privacy a data minimization

Viac features môže zlepšiť predictive metric a zároveň zvýšiť privacy, security a misuse risk. Data minimization sa nepreukazuje iba feature importance. Potrebné je purpose, access, retention a necessity assessment.

Sensitive evaluation attributes môžu byť uložené oddelene s restricted access. Training extracts sa pseudonymizujú, ale join keys a rare combinations môžu stále umožniť re-identification. Privacy-enhancing techniques majú utility a complexity trade-offs a potrebujú vlastné acceptance.

## 21. Security, misuse a abuse cases

Responsible AI zahŕňa adversarial a misuse risks. Model môže byť zneužitý na profiling mimo intended scope, explanations môžu odhaliť decision boundaries a feedback APIs môžu umožniť gaming.

```text
legitimate intended user
malicious external user
privileged insider
compromised pipeline/tool
unintended downstream reuse
```

Threat model určuje access control, logging, rate limits, output granularity, red-team tests a incident response. Security finding môže zmeniť responsible-use decision aj pri stabilných fairness metrics.

## 22. Worked incident `ML-PAY-88`

Atlas training population bola shaped starou review policy. Unreviewed operations dostávali default negative po 21 dňoch, hoci mnohé nemali authoritative outcome. New merchants mali vyšší missing-history rate a častejšie boli routed na review. Model sa učil pattern „nový merchant → investigation-confirmed risk“, ktorý bol čiastočne artefactom selection.

Tím odstránil direct geography field z modelu, ale traffic routing, currency a merchant-history features zostali strong proxies. Fairness report počítal FPR iba na operations, ktoré dostali mature labels; accepted/unreviewed population chýbala. Human queue mala fixed capacity a campaign operations prichádzali neskôr počas dňa, takže boli disproporčne dropped alebo delayed.

```text
legacy policy selects labels
→ selective negative definition
→ proxy-rich model
→ capacity queue changes action
→ report excludes unobserved outcomes
→ apparent fairness, unequal workflow impact
```

Root cause bol system-level lineage failure. Dataset, label, model, queue, human workflow a impact denominators neboli hodnotené ako jeden decision system.

## 23. Competing failure hypotheses

Responsible-AI incident sa nesmie redukovať na „model bias“. Diagnostika rekonštruuje population funnel, measurement/label process, model predictions, policy actions, human decisions a realized outcomes.

- coverage bias — relevantná population alebo subgroup chýba už v source/sampling frame;
- measurement bias — feature/label accuracy sa líši medzi groups alebo sources;
- label maturity/censoring — unknown alebo unresolved outcomes sú mapované na negative;
- historical-policy bias — label reprezentuje starú decision policy namiesto intended outcome;
- proxy reliance — direct attribute je odstránený, ale correlated descendants riadia model;
- subgroup underfit — aggregate model nemá dostatok supportu alebo capacity pre critical group;
- calibration/threshold disparity — rovnaký score alebo probability vedie k odlišným error/action rates;
- queue/workflow disparity — model predictions sú podobné, ale capacity, timing alebo reviewer behavior mení impact;
- selective-label feedback — iba acted-on cases získajú ground truth a future training sa zužuje;
- metric-definition masking — report používa favorable denominator alebo jednu fairness criterion post-hoc;
- documentation/ownership failure — known limitation nemá ownera, treatment alebo refresh trigger;
- misuse/security failure — model alebo explanation sa používa mimo intended scope alebo umožňuje abuse.

Ak disparity existuje už v feature-join coverage, model retraining ju nemusí odstrániť. Ak predictions sú parity-like, ale final actions sa líšia po queue, root cause je policy/workflow. Ak gap zmizne iba po odstránení unknown outcomes, denominator contract je chybný.

## 24. Evidence-preserving containment a recovery

Containment môže obmedziť scope, vypnúť automated action, zvýšiť human review alebo vrátiť approved policy. Zachová source records, population funnel, labels vrátane unknown, predictions, group memberships, actions, overrides a appeal outcomes.

```text
freeze expansion or harmful action
→ preserve end-to-end decision evidence
→ validate population, measurement and label contracts
→ recompute utility, subgroup and impact metrics
→ test model, policy and workflow hypotheses
→ acquire/correct data, retrain or redesign policy
→ independent review and risk acceptance
→ monitored staged rollout
```

Recovery musí smerovať na root cause. Reweighting modelu nevyrieši inaccessible appeal process. Threshold adjustment nevyrieši chybný label. Odstránenie proxy feature nevyrieši correlated information ani capacity disparity. Treatment plan má ownera, due date, residual risk a rollback trigger.

## 25. Acceptance contract

Positive acceptance identifikuje intended/non-use, affected parties, data/label quality, population funnel, model/policy lineage, subgroup support, utility, fairness/harm metrics, human workflow, privacy/security a accountable owner. Trade-offs a residual risks sú explicitné.

Recovery acceptance preukazuje correction na independent data a end-to-end action/impact layer, nie iba lepší offline model score. Forbidden paths zahŕňajú unknown→negative coercion, vynechanie sparse groups, fairness claim po odstránení direct attribute, metric shopping, evaluation iba na acted-on cases, human-in-loop bez capacity/override evidence, stale model card a deployment mimo intended scope.

Second-window test používa novšie mature outcomes a zachová rovnaký population/metric contract. Second-operation test reprodukuje population funnel, group membership, predictions, policy actions a report. Impact acceptance sleduje realized delays, false blocks, missed harms, appeals a overrides po staged rollout.

```yaml
acceptance:
  intended_use_and_owners: passed
  population_measurement_label_quality: passed
  subgroup_support_and_uncertainty: passed
  utility_fairness_and_harm_portfolio: passed
  human_privacy_security_controls: passed
  documented_residual_risk: accepted
  second_window_and_impact: passed
```

## Kontrolné otázky

1. Prečo data quality znamená fitness for purpose, nie iba valid schema?
2. Aký je rozdiel medzi intended population a sampling frame?
3. Ako measurement bias vzniká aj pri complete fields?
4. Prečo unknown label nesmie byť automaticky negative?
5. Ako historical policy formuje budúce labels?
6. Prečo oversampling nenahrádza chýbajúcu subgroup diversity?
7. Prečo odstránenie protected attribute nepreukazuje fairness?
8. Čo musí identifikovať fairness metric subject?
9. Ako demographic parity, equal opportunity, equalized odds a predictive parity odpovedajú na odlišné otázky?
10. Prečo observational group metrics nepreukazujú counterfactual fairness?
11. Ako datasheet, model card a system documentation spolu súvisia?
12. Čo znamenajú NIST AI RMF funkcie Govern, Map, Measure a Manage?
13. Prečo human-in-the-loop nemusí odstrániť risk?
14. Ako appeals vytvárajú evidence aj selection bias?
15. Čo pokazilo responsible-AI lifecycle v `ML-PAY-88`?
16. Aké positive, recovery, forbidden, second-window a impact testy uzatvárajú responsible-AI contract?

## Glossary impact

Relevantné pojmy: fitness for purpose, data quality, validity, completeness, accuracy, consistency, uniqueness, timeliness, representativeness, sampling frame, coverage error, measurement bias, label bias, historical bias, representation bias, proxy feature, subgroup support, demographic parity, selection rate, equal opportunity, equalized odds, predictive parity, group calibration, individual fairness, counterfactual fairness, datasheet, model card, system card, responsible AI, NIST AI RMF, Govern, Map, Measure, Manage, human oversight, automation bias, contestability, data minimization, misuse risk, residual risk a responsible-AI acceptance contract.

## Primárne zdroje

- [NIST — AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [NIST — AI RMF 1.0](https://doi.org/10.6028/NIST.AI.100-1)
- [NIST — Generative AI Profile](https://doi.org/10.6028/NIST.AI.600-1)
- [Datasheets for Datasets](https://arxiv.org/abs/1803.09010)
- [Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993)
