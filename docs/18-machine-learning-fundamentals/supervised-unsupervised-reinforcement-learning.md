# Supervised, unsupervised a reinforcement learning

Supervised, unsupervised a reinforcement learning sa nelíšia iba algorithmom. Líšia sa tým, aký learning signal je dostupný, čo model alebo policy optimalizuje, ako sa vytvára evidence a aké failure modes vznikajú medzi historical data a reálnym prostredím. Rovnaké payment events môžu podporiť supervised predikciu lossu, unsupervised hľadanie nezvyčajných patterns alebo reinforcement-learning policy pre sekvenčné rozhodovanie, ale tieto tri úlohy neodpovedajú na tú istú otázku.

V incidente `ML-PAY-83` Atlas potreboval prioritizovať operations pre obmedzenú manuálnu kapacitu. Supervised model mal labels z potvrdených outcomes, unsupervised analysis pomáhala objaviť nové traffic cohorts a reinforcement learning bolo navrhnuté ako „automatické optimalizovanie review policy“. Bez rozlíšenia learning signalov tím takmer zamieňal anomaly score za fraud probability a historický feedback za bezpečný reward pre autonómne actions.

## 1. Dominantný learning-signal lifecycle

Learning approach sa vyberá podľa relationship medzi observations, dostupným feedbackom a intended actionom. Najprv sa určí, čo je sample alebo environment state, aký signal vzniká a kedy, ktoré outputs sa majú generalizovať na nové cases a či systém môže bezpečne experimentovať.

```text
business objective a decision boundary
→ observation/state subject
→ dostupný learning signal
→ supervised / unsupervised / reinforcement formulation
→ objective, algorithm a training generation
→ fitted model alebo policy artifact
→ offline evaluation
→ shadow/simulation/controlled deployment
→ production outcome a delayed feedback
→ recovery a second-decision validation
```

Výber approachu nie je branding. Ak existuje historical label, neznamená to, že je správny alebo unbiased. Ak labels neexistujú, cluster nemusí reprezentovať business class. Ak existuje reward, nemusí zachytiť všetky costs a constraints. Learning signal je contract, nie iba parameter training API.

## 2. Supervised learning: učiť mapping z inputs na known targets

Supervised learning používa samples s input features `X` a observed targets alebo labels `y`. Training algorithm hľadá model, ktorý sa naučí relationship medzi vstupom a targetom a generalizuje na unseen samples z relevantnej population.

```text
(X_train, y_train)
→ supervised objective
→ fitted parameters
→ model f(X)
→ prediction pre nový sample
```

Typické supervised tasks sú classification, regression a learning to rank s explicitným relevance alebo preference signalom. Supervision neznamená, že človek ručne označil každú row; label môže pochádzať z ledgeru, sensoru, experimentu alebo delayed business outcome-u. Stále však musí byť jasné, čo signal meria a kde vzniká.

Jednoduchý estimator contract v scikit-learn štýle:

```python
from sklearn.ensemble import HistGradientBoostingClassifier

model = HistGradientBoostingClassifier(random_state=17)
model.fit(X_train, y_train)
probability = model.predict_proba(X_eval)[:, 1]
```

`fit` vytvorí fitted state z konkrétnych `X_train` a `y_train`. Úspešné dokončenie nepreukazuje generalization, calibration ani production value. Tie sa overujú na nezávislom evaluation sete a neskôr na reálnom decision path-e.

## 3. Supervised target a selection bias

Supervised model sa učí target tak, ako je pozorovaný v datasete. Ak label vzniká iba pre vybranú subset population, chýbajúce outcomes nemusia byť random. Atlas poznal potvrdenú fraud alebo loss častejšie pri operations, ktoré už historická policy poslala na review. Neoverené operations neboli automaticky safe; iba nemali rovnaký measurement process.

```text
all operations
├── reviewed → richer final labels
└── not reviewed → delayed, incomplete alebo no label
```

Taká selective labeling môže model naučiť existing policy a jej blind spots. Potrebné môže byť random audit sample, delayed reconciliation, external ground truth alebo explicitné modeling assumptions. Accuracy na labels vytvorených starou policy nepreukazuje zlepšenie oproti tej istej policy.

## 4. Supervised generalization a out-of-distribution boundary

Supervised evidence platí pre population a data-generation assumptions evaluation setu. Model môže fungovať na historical trafficu a zlyhať pri novom merchant segment, novej payment method, campaign trafficu alebo changed attacker behavior.

Generalization sa preto nehodnotí iba random holdoutom. Split má rešpektovať entity, time, groups a deployment scenario. Production monitoring musí sledovať input coverage, score/output behavior, delayed outcomes a business impact.

```text
training distribution P_train(X, y)
→ fitted relationship
→ deployment distribution P_prod(X, y)
→ equivalent, shifted alebo unknown regime
```

Model nemá zabudovaný dôkaz, že nový sample patrí do známej regime. Application potrebuje range/schema checks, cohort monitoring, uncertainty alebo fallback policy.

## 5. Unsupervised learning: hľadať structure bez target labelu

Unsupervised learning pracuje s observations bez explicitného targetu `y`. Algorithm hľadá structure podľa svojho objective: groups, components, low-dimensional representation, density alebo unusual observations. Výsledok je závislý od feature representation, scale, distance/similarity, hyperparameters a algorithm assumptions.

```text
X bez authoritative targetu
→ unsupervised objective
→ clusters / components / density / anomaly score
→ human alebo downstream interpretation
```

Príklad clusteringu:

```python
from sklearn.cluster import KMeans
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

clusterer = make_pipeline(
    StandardScaler(),
    KMeans(n_clusters=6, random_state=17, n_init="auto"),
)
cluster_ids = clusterer.fit_predict(X)
```

Cluster ID `3` nemá inherentný business meaning. Číslo je arbitrary identifier výslednej partition. Tím musí cluster charakterizovať cez source features, stability a external evidence; nesmie ho premenovať na „fraud ring“ iba preto, že vyzerá neobvykle.

## 6. Clustering, dimensionality reduction a anomaly detection nie sú to isté

Unsupervised learning obsahuje viac families úloh. Clustering partitionuje alebo hierarchicky organizuje observations podľa similarity. Dimensionality reduction vytvára compact representation zachovávajúcu vybrané structure. Density alebo anomaly methods odhadujú, ktoré points sú unusual podľa training reference.

```text
clustering: ktoré samples sú si podobné?
dimensionality reduction: ako reprezentovať variation v menšom priestore?
anomaly detection: ktoré samples sú neobvyklé voči reference?
```

Unusual neznamená harmful. Nový veľký merchant môže byť anomaly, ale legitímny. Naopak, coordinated fraud môže napodobniť dense normálny traffic. Anomaly score je evidence o statistical rarity podľa konkrétnej representation, nie authoritative fraud label.

## 7. Unsupervised objective vytvára vlastný notion of similarity

Algorithm neobjaví „prirodzené pravé skupiny“ bez assumptions. K-means minimalizuje within-cluster squared distances a preferuje približne convex, podobne rozmerné groups v zvolenom feature space. DBSCAN používa density neighborhoods. Hierarchical methods používajú distance a linkage. Zmena scalingu alebo metric môže zmeniť clusters aj pri rovnakých raw data.

```text
raw amount EUR:          12, 90000
country category code:    1, 2

bez scalingu:
amount dominuje Euclidean distance
```

Preto musí unsupervised subject obsahovať feature generation, preprocessing, metric, algorithm, parameters a random seed. „Cluster 4“ bez tejto generation nemá stabilnú identity medzi rerunmi.

## 8. Unsupervised evaluation a external usefulness

Bez target labels nemožno jednoducho počítať predictive accuracy. Internal metrics hodnotia compactness, separation alebo objective value, ale nemusia korelovať s business usefulness. Stability pri resampling alebo time windows ukazuje robustness, nie automaticky správny interpretation.

External evaluation môže použiť neskôr dostupné outcomes, expert review alebo downstream experiment. Atlas použil clusters ako exploration tool: analytici preskúmali cohorts a navrhli nové interpretable features. Cluster assignment sám priamo neblokoval payments.

```text
cluster output
→ profile a stability analysis
→ sampled expert inspection
→ hypothesis
→ independent supervised alebo business validation
```

Tým zostáva unsupervised result evidence generatorom pre ďalšie skúmanie, nie neovereným decision authority.

## 9. Reinforcement learning: policy sa učí zo sekvenčnej interakcie

Reinforcement learning rieši sekvenčné decision problems. Agent pozoruje state alebo observation, vyberie action, environment prejde do ďalšieho state-u a poskytne reward. Cieľom je naučiť policy maximalizujúcu expected cumulative reward, často s discountom a dlhodobými consequences.

```text
state s_t
→ policy vyberie action a_t
→ environment transition
→ reward r_(t+1) + next state s_(t+1)
→ update value/policy
→ ďalší krok
```

RL subject nemožno zredukovať na samotný model file. Environment vlastní transition dynamics, policy vlastní výber action a reward function určuje, ktorý observed consequence sa optimalizuje. State je analytický predpoklad decision problemu, zatiaľ čo observation je konkrétna informácia dostupná agentovi; ich zámena môže vytvoriť policy, ktorá pri trainingu videla informáciu nedostupnú v produkcii.

Základné subjects tvoria jeden transition contract:

- environment — systém alebo svet, ktorý prijme action a vytvorí next state aj observed consequences;
- state — informácia, ktorá je v zvolenom modelovaní potrebná pre predikciu future rewards;
- observation — to, čo agent skutočne dostane na vstupe; pri partial observability nemusí určovať complete state;
- action — explicitne povolená voľba, ktorú policy môže navrhnúť alebo vykonať v danom state;
- reward — scalar feedback priradený transitionu, ktorý reprezentuje iba zakódovanú časť objective-u;
- return — kumulovaný budúci reward, podľa ktorého sa porovnávajú krátkodobé a dlhodobé consequences;
- policy — versionovaný mapping zo state-u alebo observation na action alebo action distribution;
- episode — bounded trajectory od definovaného začiatku po termination, ak má problem takú prirodzenú hranicu.

Tieto položky musia byť versionované spolu, pretože zmena action setu, rewardu alebo observation schema mení meaning policy aj pri rovnakých weights. RL nie je „supervised learning, ktorý sa často retrainuje“. Label pre correct action nemusí byť priamo dostupný; agent hodnotí consequences actions cez reward a transition dynamics, pričom authorization a safety constraints zostávajú mimo reward optimization.

## 10. Exploration, exploitation a bezpečnostná hranica

RL agent čelí trade-offu medzi exploitation známych dobrých actions a exploration, ktorá získava information o alternatívach. V simulácii môže byť exploration lacná. V payments, healthcare alebo production operations môže náhodná action spôsobiť neprijateľný side effect.

```text
explore:
vyskúšaj menej známu action → získaj evidence → možno utrp cost

exploit:
použi current best policy → nižší immediate uncertainty → možno prehliadni lepšiu policy
```

Safety constraints nesmú byť iba záporná reward po škode. Niektoré actions musia byť technicky zakázané policy enforcementom, approvalom alebo sandboxom. Reward design nie je authorization control.

Atlas preto nesmel nechať online RL agent autonómne meniť block/review policy na live trafficu. Najprv bolo potrebné simulovať capacity decisions, použiť offline policy evaluation, shadow mode a hard constraints. Aj potom by business owner, nie reward scalar, vlastnil risk tolerance.

## 11. Reward specification a Goodhart boundary

Reward je optimalizačný signal, nie úplný opis business value. Agent môže nájsť spôsob, ako maximalizovať measured reward a poškodiť nezahrnutý outcome. Ak Atlas odmení iba počet completed reviews, policy môže posielať jednoduché low-value prípady a ignorovať complex high-loss operations.

```yaml
bad_reward:
  +1 per completed review

missing_costs:
  captured loss
  customer friction
  analyst time
  false block harm
  delayed outcomes
  queue fairness
```

Multi-objective problem nemožno bezpečne zredukovať na scalar bez explicitných trade-offov a constraints. Reward hacking alebo specification gaming môže byť správna optimalizácia nesprávneho objective-u.

## 12. Online, offline a simulated reinforcement learning

Online RL zbiera transitions počas interakcie s environmentom. Offline RL sa učí z historical logged trajectories. Simulated RL používa model alebo simulator environmentu. Každý variant má inú evidence boundary.

Historical log obsahuje actions starej behavior policy. Neobsahuje reliable outcomes pre actions, ktoré sa takmer nikdy nevykonali. Offline policy môže extrapolovať mimo support data a vyzerať výhodne podľa nepresného modelu. Simulator môže vynechať adversarial behavior, delayed effects alebo human adaptation.

```text
logged trajectory:
(state, action_old, reward, next_state)

counterfactual otázka:
čo by sa stalo pri action_new?

log sám odpoveď neobsahuje
```

Deployment RL policy vyžaduje policy version, environment generation, state schema, action constraints, reward definition, behavior-policy lineage a evaluation method. „Agent sa zlepšil“ bez týchto subjects nie je auditovateľné tvrdenie.

## 13. Semi-supervised a self-supervised learning ako susedné režimy

Reálne systémy často nekopírujú čisté tri categories. Semi-supervised learning kombinuje menší labeled set s väčším unlabeled setom. Self-supervised learning vytvára training signal zo samotnej štruktúry dát, napríklad predikciou masked alebo next elementu. Pretraining sa potom môže fine-tune-nuť na supervised task.

Tieto prístupy nemenia dataset a evaluation contract. Pseudo-label alebo pretext objective nie je automaticky business target. Pretrained representation môže preniesť capabilities aj biases z inej population. Fine-tuning score musí byť viazané na downstream task a deployment evidence.

## 14. Výber learning režimu podľa otázky

Výber začína tým, akú odpoveď systém potrebuje a aký feedback je skutočne dostupný.

```text
poznáme target pre historical samples?
→ supervised learning

nepoznáme target, hľadáme structure alebo anomalies?
→ unsupervised learning

actions menia future state a dlhodobý reward?
→ reinforcement learning

explicitné stabilné pravidlo stačí?
→ deterministic system, nie learning za každú cenu
```

Táto mapa je počiatočná, nie automatická. Supervised label môže byť biased. Unsupervised output môže byť nepoužiteľný. RL environment môže byť nebezpečný alebo neidentifikovateľný. Najjednoduchší validný formulation s jasnou evidence boundary je preferovaný.

## 15. Worked incident `ML-PAY-83`: learning-mode confusion

Po zistení dataset leakage navrhol Atlas tím tri „opravy“:

1. supervised classifier retrainovať na potvrdenom loss labeli;
2. anomaly detector použiť bez labels a anomaly score nazvať riskom;
3. RL agent nechať automaticky meniť daily review threshold podľa captured lossu.

Prvá cesta zodpovedala dostupnému decision problemu, ak sa vyriešila selection bias a delayed labels. Druhá bola vhodná na discovery nových cohorts, nie ako replacement probability. Tretia mala sekvenčný character, ale live exploration a delayed/noisy reward vytvárali neprijateľný risk.

Tím vytvoril oddelené subjects:

```yaml
supervised:
  target: confirmed_loss_within_30d
  output: calibrated probability
  action: input do bounded ranking policy

unsupervised:
  objective: discover stable unusual cohorts
  output: cluster/anomaly evidence
  action: sampled analyst investigation

reinforcement_candidate:
  state: queue + capacity + cohort outcomes
  action: bounded allocation suggestion
  environment: offline simulator first
  forbidden: direct live block/review mutation
```

Tým sa odstránilo nebezpečné tvrdenie, že všetky tri outputs sú „risk score“.

## 16. Evidence-preserving containment a recovery

Počas incidentu tím zachoval training dataset manifests, labels, unsupervised preprocessing/metric, policy proposals, historical queue actions a delayed outcomes. Anomaly-driven auto-routing a RL experiment flags boli vypnuté. Posledná deterministic capacity policy zostala authority.

Recovery oddelila pipelines a evals. Supervised model dostal time/group holdout a top-capacity business metric. Unsupervised cohorts dostali stability a expert-sample review. RL proposal zostal simulation-only s hard action constraints a counterfactual uncertainty reportom.

```text
one shared data foundation
├── supervised artifact + predictive evaluation
├── unsupervised artifact + structural/stability evaluation
└── RL candidate policy + simulator/offline evaluation

žiadny output nezdieľa automaticky business meaning
```

## 17. Acceptance contract podľa learning mode

Supervised positive path musí preukázať target contract, split isolation, generalization a downstream action outcome. Forbidden je používať incomplete proxy ako truth alebo score mimo validated population bez fallbacku.

Unsupervised positive path musí preukázať exact representation, objective, stable artifact a independent interpretation process. Forbidden je premenovať cluster/anomaly na business class bez external validation.

RL positive path musí preukázať environment, state/action/reward generations, constraints, behavior-policy coverage, offline/simulation evidence a bounded rollout. Forbidden je live exploration cez citlivé side effects, reward ako jediný safety control alebo autonomous action mimo authorization.

```text
supervised second test:
nový mature cohort → expected predictive/business behavior

unsupervised second test:
rerun/resample → vysvetlená stability alebo drift

RL second test:
new episode/scenario → constraints držia aj pri reward pressure

universal forbidden:
training objective sa vydáva za business acceptance
```

## Kontrolné otázky

1. Čo je learning signal v supervised, unsupervised a reinforcement learning?
2. Prečo supervised label nemusí byť objective truth?
3. Ako selection bias vzniká, keď labels existujú iba pre reviewed cases?
4. Čo presne preukazuje supervised holdout score?
5. Prečo cluster ID nemá inherentný business meaning?
6. Ako feature scaling a metric menia unsupervised result?
7. Prečo anomaly score nie je fraud probability?
8. Aký je rozdiel medzi RL state a observation?
9. Čo je policy, reward a return?
10. Prečo reward nemôže nahradiť authorization a safety constraints?
11. Čo chýba v historical logu pre unseen actions?
12. Ako sa semi-supervised a self-supervised learning líšia od business targetu?
13. Prečo boli tri návrhy v `ML-PAY-83` oddelené do rôznych subjects?
14. Aké evidence a forbidden paths sú špecifické pre každý learning mode?
15. Kedy je vhodnejší deterministic workflow?

## Glossary impact

Relevantné pojmy: supervised learning, unsupervised learning, reinforcement learning, learning signal, target, generalization, selection bias, supervised estimator, clustering, dimensionality reduction, anomaly detection, similarity metric, environment, state, observation, action, reward, return, policy, episode, exploration, exploitation, reward specification, behavior policy, offline RL, simulator, semi-supervised learning, self-supervised learning a learning-mode acceptance contract.

## Primárne zdroje

- [scikit-learn — Supervised learning](https://scikit-learn.org/stable/supervised_learning.html)
- [scikit-learn — Unsupervised learning](https://scikit-learn.org/stable/unsupervised_learning.html)
- [scikit-learn — Clustering](https://scikit-learn.org/stable/modules/clustering.html)
- [Sutton and Barto — Reinforcement Learning: An Introduction, Second Edition](https://incompleteideas.net/book/the-book-2nd.html)
- [NIST AI 100-2e2025 — Adversarial Machine Learning](https://csrc.nist.gov/pubs/ai/100/2/e2025/final)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Dataset, sample, feature, label a target](dataset-sample-feature-label-target.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Regression, classification, ranking a clustering →](regression-classification-ranking-clustering.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
