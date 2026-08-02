# Artificial intelligence, machine learning, deep learning a generative AI

Artificial intelligence, machine learning, deep learning a generative AI nie sú štyri mená pre tú istú vec. Označujú rôzne scope-y systému, rôzne mechanizmy vytvárania správania a rozdielne dôkazné hranice. Keď tím povie „nasadili sme AI“, bez ďalšieho spresnenia nie je jasné, či hovorí o pravidlovom decision engine, fitted klasifikačnom modeli, neurónovej sieti, generátore textu alebo o celej aplikácii, ktorá okolo modelu vykonáva retrieval, policy checks, tool calls a business mutations.

Pre DevOps, platform a operations rolu je táto hranica zásadná. Model môže byť numericky validný, ale systém môže stále používať nesprávny dataset, starý feature pipeline, neautorizovaný tool, chybný threshold alebo neoverený generated output. Naopak, deterministický workflow môže spĺňať business cieľ bezpečnejšie a lacnejšie než zložitejší ML alebo agentický komponent. Táto kapitola preto sleduje jeden dominantný lifecycle od business problému až po produkčný outcome a v každom kroku pomenúva presný subject, authority a evidence.

Atlas Payments používa spoločný incident `ML-PAY-83`. Tím mal znížiť čas manuálneho preverovania podozrivých merchant operácií. Projekt bol prezentovaný ako „AI fraud detector“, hoci v skutočnosti kombinoval supervised classifier, pravidlový threshold, generatívne vysvetlenie a support queue. Nejasné pomenovanie umožnilo, aby sa úspech jednej časti zamieňal za správnosť celého systému.

## 1. Dominantný AI-system lifecycle

AI systém začína cieľom a rozhodovacou hranicou, nie výberom modelu. Najprv sa určí, ktorý user alebo business outcome sa má zmeniť, akú operáciu systém podporuje, čo smie iba odporučiť a čo smie vykonať. Až potom sa rozhoduje, či je vhodný deterministický algoritmus, klasické machine learning, deep learning alebo generative AI.

```text
business problém a intended outcome
→ exact decision alebo content subject
→ data a observation contract
→ deterministic pravidlo alebo learning objective
→ training/configuration generation
→ model alebo policy artifact
→ inference/generation request
→ application policy a human/tool boundary
→ business action
→ production evidence, recovery a second-operation test
```

Model je iba jeden komponent tohto reťazca. Dataset pipeline, feature transform, prompt, retrieval index, threshold, API wrapper, identity, authorization, queue a human review môžu zmeniť výsledok aj bez zmeny model weights. Produkčný verdict preto musí pomenovať celý relevantný system generation, nie iba model family alebo marketingový názov.

## 2. Exact AI-system subject

Tvrdenie „model v2 je v produkcii“ nestačí. Exact subject musí rozlíšiť use case, decision unit, population, data snapshot, feature schema, learning objective, algorithm a hyperparameters, fitted artifact digest, inference runtime, post-processing, threshold, policy, deployment cohort a ownera business actionu.

```yaml
subject: ML-PAY-RISK-2026-08-v1
business_operation: prioritize_manual_review
observation_unit: merchant_operation_id
population: card-not-present EUR payments
prediction_time: authorization_received_at
training_snapshot: s3://ml-curated/risk/2026-07-15/manifest.json
feature_schema: risk-features-v4
label_contract: confirmed_loss_within_30d-v2
estimator: histogram-gradient-boosting
artifact_digest: sha256:7c1d...91ab
output: calibrated_loss_probability
threshold_policy: review-capacity-2500-per-day-v3
explanation_component: genai-summary-v1
business_owner: risk-operations
forbidden: model output directly blocks settlement
```

Takýto manifest oddeľuje learned artifact od system policy. Rovnaké probabilities s novým thresholdom môžu zmeniť počet kontrolovaných operácií. Rovnaký model s novým feature pipeline môže dostať iné vstupy. Rovnaký generátor s novým promptom môže vytvoriť odlišné vysvetlenia. Bez týchto generácií sa incident nedá reprodukovať ani bezpečne rollbackovať.

## 3. Artificial intelligence ako najširší system scope

Artificial intelligence je najširší pojem v tejto štvorici. Prakticky označuje engineered system, ktorý pre definované objectives vytvára predictions, recommendations, decisions alebo content ovplyvňujúce reálne či virtuálne prostredie. Taký systém môže používať learned model, explicitné pravidlá, search/planning alebo kombináciu viacerých mechanizmov.

AI system teda nie je automaticky neurónová sieť a už vôbec nie iba model file. Payment review application môže kombinovať:

- deterministic eligibility rules, ktoré odmietnu nekompletný request;
- supervised classifier, ktorý odhadne probability budúcej straty;
- ranking policy, ktorá zoradí prípady podľa expected value kontroly;
- generatívny model, ktorý pripraví analyst summary;
- human reviewer, ktorý má autoritu rozhodnúť o ďalšom kroku;
- audit a reconciliation, ktoré preukážu skutočný business outcome.

Dôsledok je dôležitý: model evaluation preukazuje vlastnosť modelu na definovanom datasete. Nepreukazuje automaticky správnosť identity, authorization, queue semantics, human processu ani finálnej business operácie. AI-system acceptance musí pokryť celý path.

## 4. Machine learning ako učenie správania z dát

Machine learning je podmnožina AI, v ktorej sa časť správania neprogramuje ako úplný zoznam pravidiel. Training algorithm upravuje parameters modelu tak, aby na training observations minimalizoval objective alebo inak zachytil štruktúru dát. Výsledkom trainingu je fitted model artifact, ktorý sa následne používa na inference nad novými observations.

```text
training data X a prípadne learning signal y/reward
→ algorithm + objective + hyperparameters
→ fitted parameters
→ model artifact
→ inference nad novým X
→ prediction, score alebo representation
```

Machine learning nie je „systém sa učí sám v produkcii“ v neurčitom zmysle. Väčšina produkčných modelov má explicitný training job, immutable input snapshots, code/environment generation a promotion gate. Online alebo continual learning je samostatný design s ešte prísnejšou kontrolou feedbacku, poisoning, rollbacku a reproducibility.

Fitted model zachytáva štatistické patterns v training population. Nezískava business truth nezávisle od dát. Ak label meria analyst decision namiesto potvrdenej straty, model sa učí napodobňovať historické rozhodovanie analytikov. Ak training data obsahuje iba prípady, ktoré sa historicky dostali na review, model nemusí reprezentovať celú production population.

## 5. Deep learning ako parametrický model s viacvrstvovými neurónovými sieťami

Deep learning je podmnožina machine learning založená na neurónových sieťach s viacerými learnable transformáciami. Vrstvy postupne vytvárajú representations, ktoré môžu zachytiť komplexné relations v obraze, zvuku, texte, časových radoch alebo veľkých tabulárnych dátach. „Deep“ opisuje architektúru a composition vrstiev, nie automaticky vyššiu kvalitu alebo všeobecnú inteligenciu.

```text
raw alebo transformed input
→ layer 1 representation
→ layer 2 representation
→ ...
→ output head
→ loss
→ gradient-based parameter update
```

Deep model môže znížiť potrebu ručne navrhnutých features pri niektorých modalities, ale presúva complexity do dataset scale, architecture, optimization, compute, reproducibility a serving. Väčší model môže mať vyššiu capacity, no aj vyššiu latency, memory footprint, energy/cost, attack surface a náročnejšiu explainability.

Pri tabulárnom payment-risk probléme nemusí deep network prekonať kvalitný tree ensemble. Výber musí vychádzať z reprodukovateľného porovnania na správnom split-e a production constraints. Produktové tvrdenie „používame deep learning“ nie je evidence, že systém generalizuje lepšie.

## 6. Generative AI ako tvorba odvodeného contentu

Generative AI používa modely, ktoré zachytávajú štruktúru a characteristics input/training data a generujú odvodený syntetický content, napríklad text, obraz, audio, video alebo code. Generative model typicky nevracia iba jednu class alebo numeric estimate; vytvára sekvenciu alebo inú zložitú output štruktúru podľa input contextu a sampling/decoding policy.

```text
model generation
+ system/developer instructions
+ user input
+ retrieved context
+ tool results
+ decoding parameters
→ generated content
→ validation, policy a consumer action
```

Generated text nie je databázový fact ani automaticky vysvetlenie interného rozhodovania iného modelu. Ak LLM dostane risk features a vytvorí vetu „operácia je podozrivá pre nezvyčajnú krajinu“, táto veta môže byť presvedčivá aj vtedy, keď classifier v skutočnosti rozhodujúco reagoval na iné features alebo keď country feature nebola dostupná. Faithful explanation vyžaduje samostatný contract a evaluation.

Generative AI môže byť užitočná pre summarization, draftovanie, extraction, conversational interface alebo synthetic-data experiments. Pri každom use case však treba určiť, či output ide človeku na kontrolu, do ďalšieho deterministic parsera alebo priamo do tool/action pathu. Čím bližšie je output k side effectu, tým silnejšie musia byť schema validation, authorization, grounding, approval a rollback boundaries.

## 7. Vzťah medzi pojmami

Vzťah sa dá zhrnúť ako vnorenie, nie ako lineárna evolúcia, v ktorej novší pojem ruší starší.

```text
Artificial intelligence systems
├── deterministic/search/planning-based systems
└── machine learning systems
    ├── classical/statistical ML models
    └── deep learning models
        ├── discriminative deep models
        └── generative deep models
```

Nie každý AI systém používa ML. Nie každý ML model je deep learning. Nie každý deep model je generatívny. Generative AI zároveň nie je jeden algorithm; zahŕňa families modelov a modalities s odlišným trainingom, inference a risk profilom.

V production architecture môže jeden systém používať viac vetiev naraz. Atlas classifier je klasické supervised ML, generatívny summary component je deep generative model a queue policy zostáva deterministická. Zlyhanie summary komponentu preto nemá automaticky zneplatniť classifier score, ale musí aktivovať explicitný fallback. Naopak, zlyhanie feature pipeline môže zneplatniť classifier a nesmie sa zakryť pekne vyzerajúcim summary.

## 8. Training, inference a application decision

Training vytvára model parameters z historických alebo simulovaných dát. Inference používa frozen alebo explicitne versionovaný model na nový input. Application decision kombinuje model output s policy, capacity, authorization a business stateom. Tieto tri operácie majú odlišnú identity aj failure semantics.

```text
training operation:
(dataset snapshot, code, environment, seed, objective)
→ model artifact

inference operation:
(model artifact, feature vector, runtime)
→ score/content

business operation:
(score/content, threshold, policy, human/tool authority)
→ review/block/allow/notify
```

Úspešný HTTP response z model servera preukazuje iba to, že endpoint vrátil output pre request. Nepreukazuje správnu feature generation, kalibráciu, threshold policy ani business side effect. Rovnako successful training job nepreukazuje generalization; môže iba potvrdiť, že optimizer dokončil nad zadanými vstupmi.

## 9. Deterministické a probabilistické komponenty

Deterministický komponent pri rovnakom explicitnom inpute a generation očakáva rovnaký output. Probabilistický model môže produkovať score odhadujúci uncertainty alebo pri generovaní používať sampling. Aj deterministicky nastavená inference neurčitého modelu však zostáva štatistická vo vzťahu k svetu: rovnaký output neznamená, že je factually správny.

Atlas musí oddeliť dva typy variability:

- execution variability — rovnaký request môže kvôli sampling, nondeterministic kernels alebo concurrency dostať iný raw output;
- epistemic/aleatoric uncertainty — model nemá dostatočné knowledge alebo je samotný jav nepredvídateľný, aj keď execution je bitovo reprodukovateľná.

Retries preto nie sú univerzálna oprava. Retry generatívneho requestu môže vytvoriť iný text bez odstránenia root cause. Retry business actionu po timeout-e môže duplikovať side effect. Operation identity a idempotency zostávajú potrebné aj pri AI systémoch.

## 10. Kedy nepoužiť machine learning alebo generative AI

ML má zmysel, keď existuje opakovaný decision/content problem, dostatočný data alebo feedback signal, merateľný objective, prijateľná error asymmetry a možnosť monitorovať zmenu population. Ak je pravidlo stabilné, explicitné a auditovateľné, deterministic implementation býva lepšia.

Generative AI nie je vhodná ako náhrada presného parsera, schema validatora, access-control decisionu alebo účtovného výpočtu, pokiaľ sa jej output neuzatvorí do deterministického contractu a nezávislého enforcementu. Model môže navrhnúť policy text; nemá byť sám jediným policy enforcement pointom.

```text
stabilné explicitné pravidlo
→ implementuj a testuj deterministicky

pattern z veľkého množstva príkladov
→ zváž ML + offline/online evaluation

nový content alebo open-ended transformation
→ zváž generative AI + grounding/validation

citlivý side effect
→ oddel model recommendation od authoritative approval/enforcement
```

Technologická novinka nie je business requirement. Acceptance musí porovnať baseline vrátane jednoduchého rule-based riešenia, prevádzkových nákladov a failure behavior.

## 11. Worked incident `ML-PAY-83`

Atlas vytvoril `risk-assist-v1` pre manuálne preverovanie merchant operácií. Dashboard prezentoval „AI accuracy 96,8 %“. V skutočnosti číslo patrilo binary classifieru na náhodne rozdelených rows z payment-attempt table. Jeden merchant operation mohol mať viac retries, takže attempts tej istej operácie skončili v training aj test sete.

Feature pipeline navyše používala `final_settlement_status`, ktorý vznikal až po decision time. Label `needs_review` pochádzal z historického analyst queue, nie z potvrdenej straty. Model sa teda učil historickú routing policy s future leakage, nie budúci risk. Generatívny komponent vytváral natural-language summary a analytici jeho presvedčivý text považovali za faithful explanation classifieru.

Produkčný cieľ bol pritom kapacitný: zoradiť najhodnotnejších `2 500` prípadov denne. Tím však optimalizoval classification accuracy pri default thresholde. Keď sa traffic mix zmenil počas kampane, classifier označil veľa lacných retries ako positive, queue sa zaplnila duplicitnými operations a precision v top capacity window klesla. Support videl pekné summaries a zelený model endpoint, preto incident najprv pripísal analyst throughputu.

Root cause nebola iba „zlá accuracy“. Systém nemal exact subject a rozlíšenie komponentov:

```text
marketing label: AI fraud detector
actual components:
  leaked supervised classifier
  attempt-level observation unit
  threshold policy unrelated to daily capacity
  unfaithful generative summary
  queue without operation-level deduplication
```

Každá časť mohla vyzerať funkčne, ale end-to-end business path bol nesprávny.

## 12. Evidence-preserving containment a recovery

Tím najprv zastavil automatické queue promotion z modelu, no zachoval inference requests, feature vectors, model digest, threshold generation, generated summaries a queue decisions. Review sa dočasne vrátil k poslednej schválenej deterministic ruleset generation a operation-level deduplication.

Recovery vytvorila nový subject:

```text
observation unit: merchant_operation_id
prediction cutoff: authorization_received_at
label: confirmed_loss_within_30d
split: time-based + operation-group isolation
primary objective: expected captured loss in top 2500/day
classifier output: calibrated probability
ranking score: probability * recoverable_amount
GenAI summary: optional analyst aid, never decision evidence
```

Model artifact, feature pipeline, threshold/ranking policy a summary prompt sa versionovali nezávisle. Analyst UI začalo zobrazovať source facts a model score oddelene od generated narrative. Fallback pri summary outage ponechal structured evidence, ale nie vymyslený text. Promotion vyžadovala replay nad frozen holdoutom, shadow traffic a business acceptance na exact daily capacity.

## 13. Acceptance contract

Positive path musí preukázať, že správna operation population vstupuje do správneho component generationu, model output je interpretovaný podľa svojho contractu a business policy vytvorí intended action. Evidence musí spojiť request, feature snapshot, model digest, output, threshold/ranking policy, human/tool action a outcome.

Recovery path musí umožniť vypnúť alebo rollbackovať jednu vrstvu bez nejasného návratu celého „AI“. Ak generatívne summary zlyhá, classifier a structured evidence môžu pokračovať iba vtedy, ak summary nie je required decision input. Ak feature schema nesedí, classifier musí fail-closed alebo použiť explicitne schválený fallback, nie ticho doplniť nuly.

Forbidden paths musia byť testované:

```text
positive:
exact operation → valid features → pinned model → score
→ approved queue policy → analyst decision → outcome evidence

recovery:
summary provider unavailable
→ structured evidence remains
→ no fabricated explanation

forbidden:
future field enters prediction features
attempt retries become independent business subjects
generated text becomes authorization or fraud fact
model endpoint 200 is treated as business acceptance
unversioned threshold changes production decisions
```

Second-operation test musí použiť novú merchant operation s rovnakými relevantnými characteristics a potvrdiť, že systém nevytvára duplicate queue entries, nededí stale generation a zachováva audit lineage.

## 14. Praktický component manifest

Nasledujúci Python-like príklad nie je training lab; ukazuje, že systémový manifest má oddeliť learned a deterministic generations.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class RiskSystemGeneration:
    feature_schema: str
    model_digest: str
    ranking_policy: str
    summary_prompt: str
    decision_owner: str

GENERATION = RiskSystemGeneration(
    feature_schema="risk-features-v4",
    model_digest="sha256:7c1d...91ab",
    ranking_policy="top-2500-expected-loss-v3",
    summary_prompt="analyst-summary-v1",
    decision_owner="risk-operations",
)
```

Deployment evidence musí read-backnúť loaded values z reálneho runtime-u. Git manifest alebo registry tag preukazuje intended state, nie automaticky loaded model digest, active threshold ani serving cohort.

## Kontrolné otázky

1. Prečo AI system nie je synonymum modelu?
2. Ktoré AI systémy nemusia používať machine learning?
3. Čo presne vzniká počas trainingu a čo počas inference?
4. Prečo deep learning automaticky neznamená lepší model?
5. Čím sa generative AI output líši od classification score-u?
6. Prečo generated summary nie je automaticky faithful explanation?
7. Ktoré generations treba pripnúť pre reprodukovateľný incident?
8. Kedy je deterministic workflow vhodnejší než ML?
9. Čo preukazuje successful model endpoint a čo nepreukazuje?
10. Ako nejasný pojem „AI fraud detector“ zakryl root cause `ML-PAY-83`?
11. Ktoré vrstvy sa musia dať rollbackovať nezávisle?
12. Aké positive, recovery, forbidden a second-operation testy uzatvárajú systém?

## Glossary impact

Relevantné pojmy: artificial intelligence system, machine learning, deep learning, generative AI, deterministic component, probabilistic component, training, inference, fitted model artifact, model generation, system generation, learning objective, application decision, generated content, faithful explanation, execution variability, uncertainty, model endpoint a AI-system acceptance contract.

## Primárne zdroje

- [NIST AI Risk Management Framework 1.0](https://airc.nist.gov/airmf-resources/airmf/)
- [NIST AI 600-1 — Generative Artificial Intelligence Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence)
- [NIST AI 100-3 — The Language of Trustworthy AI](https://www.nist.gov/publications/language-trustworthy-ai-depth-glossary-terms)
- [NIST AI 100-2e2025 — Adversarial Machine Learning](https://csrc.nist.gov/pubs/ai/100/2/e2025/final)
- [scikit-learn — Getting Started](https://scikit-learn.org/stable/getting_started.html)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Keycloak troubleshooting](../17-keycloak-and-identity-platform/keycloak-troubleshooting.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Dataset, sample, feature, label a target →](dataset-sample-feature-label-target.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
