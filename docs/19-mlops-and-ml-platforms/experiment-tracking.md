# Experiment tracking

Experiment tracking je systém evidencie vykonaných ML pokusov. Spája run identity s parameters, metrics, dataset references, code a environment generation, output artifacts a statusom execution. Jeho cieľom nie je vytvoriť pekný leaderboard. Musí umožniť porovnať kandidátov, reprodukovať relevantný run, vysvetliť promotion decision a odlíšiť model-level zmenu od zmeny dát, evaluation alebo runtime policy.

Incident `MLOPS-PAY-90` pokračuje. Atlas mal stovky MLflow runs a dashboard zoradený podľa validation ROC-AUC. Najvyšší run bol označený tagom `best=true` a jeho model sa dostal do Registry. Run však nemal immutable dataset digest, logoval iba poslednú hodnotu threshold-dependent metric, environment bol zachytený neúplne a test set sa používal opakovane pri výbere kandidáta. Experiment tracker správne uložil to, čo mu klient poslal; neúplný tracking contract však vytvoril falošnú istotu.

## 1. Experiment, run a model nie sú jedna vec

Experiment je logický container pre súvisiace runs, napríklad `payment-risk-classification`. Run je jedno konkrétne execution training alebo evaluation kódu. Logged model je model artifact a jeho metadata vytvorená počas runu. Registered model a model version patria do neskoršieho lifecycle-u promotion a governance.

```text
Experiment: payment-risk-classification
├── Run A: baseline logistic regression
│   └── Logged model artifact A
├── Run B: gradient boosting trial 41
│   └── Logged model artifact B
└── Run C: final refit candidate
    └── Logged model artifact C
        └── Registry version payment-risk/17
```

Run success neznamená, že model je vhodný. Znamená, že tracking client alebo orchestrátor uzavrel execution stavom, ktorý považuje za úspešný. Model artifact môže chýbať, upload môže byť partial alebo evaluation môže byť chybná. Registry version zase nemá byť odvodená iba z názvu experimentu alebo najvyššej metric.

## 2. Exact experiment run subject

Run musí mať globally unique ID a explicitný purpose. Hyperparameter trial, cross-validation fold, final refit, calibration, export a offline evaluation sú rozdielne operations. Ak sa všetky logujú ako rovnocenné runs v jednom leaderboards, tím môže porovnávať neporovnateľné estimands.

```yaml
run_id: 6f7b8fa3b5ad4aaead859f1a5d771301
experiment: payment-risk-classification
run_type: final-refit-candidate
parent_run_id: 3a80a77e2f0b45d6a3b2667e054fb13d
purpose: train candidate after nested-CV selection
code_commit: 77a51d0
dataset_digest: sha256:9bd7...e802
split_generation: merchant-group-time-v3
training_image: registry.example/risk-trainer@sha256:31ab...91fe
resolved_config_digest: sha256:1a6d...de11
seed_set: [11, 29, 47]
model_family: histogram-gradient-boosting
metric_contract: risk-eval-v6
owner: risk-data-science
```

Run type a purpose vysvetľujú, prečo execution existuje. Parent-child relationship môže zoskupiť HPO study, folds alebo distributed subruns, no child run zostáva samostatná operation identity. Re-run po failure potrebuje nový run ID a relation `retry_of`; nemá prepísať pôvodný historical record.

## 3. Parameters, tags a immutable references

Parameters opisujú inputs alebo choices runu, napríklad learning rate, max depth, feature set a split rule. Tags pridávajú organizačný alebo lifecycle context. Ani jedno nemá byť použité ako náhrada immutable artifactu. Parameter `dataset=2026-07` je užitočný pre filter, ale authoritative reference musí obsahovať digest alebo snapshot ID.

Parameters majú byť logované v resolved podobe. Ak config používa inheritance, environment variables alebo Hydra composition, tracker má zachytiť final effective configuration. Secret values sa nelogujú; uloží sa secret reference alebo redacted marker. Mutable tag `best=true` nie je promotion authority, pretože viac runs môže mať rovnaký tag a používateľ ho môže zmeniť bez nového evaluation.

Naming convention musí byť stabilná. Ak jeden tím loguje `learning_rate`, druhý `lr` a tretí `optimizer.lr`, cross-run query je nepresná. Platforma môže poskytnúť schema a helper library, ktorá validuje required fields pred ukončením runu.

## 4. Metrics ako časové a kontextové observations

Metric nie je iba key-value. Má step, timestamp, dataset context, evaluation population a direction. Training loss po epochách je time series. Validation ROC-AUC je aggregate nad konkrétnym splitom. Latency môže byť distribution, nie jedna priemerná hodnota. Fairness alebo business metric potrebuje cohort a denominator.

```python
import mlflow

with mlflow.start_run() as run:
    mlflow.log_params({
        "max_depth": 8,
        "learning_rate": 0.05,
        "dataset_digest": "sha256:9bd7...e802",
        "split_generation": "merchant-group-time-v3",
    })

    for epoch, loss in enumerate([0.61, 0.54, 0.49]):
        mlflow.log_metric("train.loss", loss, step=epoch)

    mlflow.log_metric("validation.roc_auc", 0.892)
    mlflow.log_metric("validation.average_precision", 0.314)
```

Tento example ukazuje API surface, nie complete evaluation. Dataset digest je zatiaľ iba parameter; robustný run ho má zároveň logovať ako structured dataset input alebo artifact manifest a platforma musí reference overiť. Metric names samy nevysvetľujú threshold, sample weighting ani confidence interval.

Metrics treba chápať ako evidence statements. `validation.roc_auc=0.892` znamená výsledok konkrétneho evaluation code nad konkrétnou population. Ak sa zmení scorer implementation, filtering alebo label snapshot, rovnaký názov už nemusí byť porovnateľný. Metric contract version preto patrí do run metadata.

## 5. Dataset inputs v tracking-u

MLflow podporuje tracking dataset inputs prostredníctvom dataset metadata a API ako `mlflow.log_input()`. Taký record je užitočný na spájanie runu s datasetom, ale kvalita identity závisí od toho, aký digest, source a context klient poskytne. Path na mutable table nestačí.

Experiment tracker nemá byť jediným dataset Registry. Má uložiť reference na authoritative dataset manifest a prípadne summary profile. Raw citlivé data sa do trackeru nekopírujú len preto, aby bol run „self-contained“. Access control, retention a privacy boundary zostávajú súčasťou platform designu.

Training, validation a test inputs musia byť rozlíšené contextom. Run, ktorý loguje iba jeden všeobecný `dataset`, neumožňuje určiť, či metric patrí validation alebo test population. Pri final refit-e môže training input zahŕňať train+validation, no independent test zostáva oddelený evaluation run alebo context.

## 6. Artifacts, checkpoints a evidence bundle

Run artifacts zahŕňajú model weights, plots, confusion matrices, feature schemas, resolved config, environment lock, validation report a logs. Backend store typicky drží run metadata; artifact store drží väčšie files. Tieto dve vrstvy môžu zlyhať nezávisle.

Run môže byť označený `FINISHED`, ale artifact upload ešte nemusí byť durable, ak aplikácia ukončila context skôr alebo network zlyhala. Promotion pipeline musí read-backom overiť required artifact paths, digests a loadability. Screenshot chartu nie je náhrada machine-readable metrics a raw evaluation outputs.

Checkpoints sú intermediate model states. Každý checkpoint potrebuje step a artifact identity. „Best checkpoint“ musí uviesť selection metric a evaluation snapshot. Final exported model môže byť odlišný od checkpointu, preto sa jeho digest loguje po exporte a parity teste.

## 7. Autologging a jeho dôkazná hranica

MLflow autologging dokáže automaticky zachytiť framework-specific parameters, metrics, models a ďalšie metadata. Znižuje friction a je vhodné ako baseline. Nemôže však samo poznať business observation unit, label maturity, dataset snapshot authority, promotion purpose ani downstream policy.

Autologging môže navyše meniť coverage medzi framework versions. Platform contract preto nesmie predpokladať, že „autologging zachytí všetko“. Required metadata sa validujú explicitne. Pri upgrade MLflow alebo integration library sa spraví compatibility test a porovná sa, ktoré fields a artifacts sú emitované.

## 8. Local oproti remote tracking architektúre

Default local MLflow setup môže zapisovať do adresára `mlruns`. Je vhodný pre individuálny experiment, ale team workflow potrebuje shared tracking server, backend store a artifact store. Metadata a artifacts majú rozdielne durability, throughput a access-control requirements.

Remote setup typicky obsahuje client API, Tracking Server, SQL backend store a object artifact store. Pri proxied artifact mode klient uploaduje cez server; pri direct mode potrebuje credentials k object storage. Zmena artifact routing po vytvorení experimentov môže nechať staré runs na pôvodnej location, preto migration vyžaduje explicitný inventory a read-back.

```text
training client
├─REST→ MLflow Tracking Server
│        └─metadata→ PostgreSQL backend
└─artifact upload→ server proxy alebo object store
                         └─S3/Blob artifact bytes
```

HTTP 200 z metadata requestu nepreukazuje durable artifact. Object existence nepreukazuje, že backend record naň ukazuje. Backup a restore musia pokryť obe vrstvy konzistentne alebo mať reconciliation mechanizmus.

## 9. Experiment organization a queryability

Experimenty sa organizujú podľa stable use case alebo tasku, nie podľa osoby či dátumu. Runs sa filtrujú tags a parameters. Parent-child runs sú vhodné pre folds alebo trials, ale hierarchy nesmie zakryť independent operations.

Príliš široký experiment s tisíckami neporovnateľných runs vytvára selection bias a neprehľadnosť. Príliš veľa experimentov zas rozbíja cross-run comparison. Platforma preto definuje naming, lifecycle state a archival policy. Search query musí vedieť vybrať runs s rovnakým dataset, split, metric contract a model interface.

```python
runs = mlflow.search_runs(
    experiment_names=["payment-risk-classification"],
    filter_string=(
        "params.dataset_digest = 'sha256:9bd7...e802' and "
        "params.split_generation = 'merchant-group-time-v3' and "
        "tags.run_type = 'hpo-trial'"
    ),
    order_by=["metrics.validation.average_precision DESC"],
)
```

Ordering podľa jednej metric je exploratory view. Promotion selection musí použiť complete gate a independent evidence, nie priamo prvý row query výsledku.

## 10. Reproducibility cez tracking record

Tracking record je reprodukčný index, nie kompletný reproducible environment. Na rerun treba dostupný code commit, dataset snapshot, config artifact, environment image, secrets/dependencies a execution topology. Tracker spája references a uloží outcomes. Ak remote objects boli garbage-collected alebo mutable tags sa presunuli, historical run ostane viditeľný, ale nereprodukovateľný.

Reproduction má dve úrovne. Execution reproduction overuje, že job sa dá znovu spustiť. Result reproduction porovná metrics alebo artifact v definovanej tolerance. Bitwise identity nemusí byť realistická pri nondeterministic GPU trainingu, ale expected stability range a multi-seed evidence musia byť explicitné.

## 11. Experiment comparison a multiple testing

Čím viac trials tím skúša a čím častejšie sleduje rovnaký validation set, tým vyššie je riziko, že vyberie náhodne dobrý candidate. Tracker uľahčuje experimentovanie, ale nezabraňuje overfittingu na validation evidence. HPO study musí evidovať search space, sampler, pruner, budget a počet observations. Final verdict potrebuje independent test alebo nested evaluation podľa rizika.

Runs s rôznym datasetom, splitom alebo metric implementation sa nemajú porovnávať iba preto, že UI zobrazuje rovnaký column name. Experiment comparison musí najprv overiť compatibility dimensions a až potom metrics.

## 12. Failure semantics a unknown outcomes

Tracking call môže timeout-nuť po tom, čo server mutation prijal. Blind retry môže vytvoriť duplicate child run alebo zmeniť tags. Client má používať known run ID a idempotent logging pattern, kde to API umožňuje. Po chybe sa najprv číta authoritative run state a artifact list.

Training process môže spadnúť po vytvorení modelu, ale pred uzavretím runu. Taký run má status `FAILED` alebo `KILLED`, no artifacts môžu existovať. Nemajú sa automaticky promovovať, pretože completion a evaluation evidence sú neúplné. Recovery môže zachovať artifacts pre forensics alebo pokračovať z checkpointu ako nový related run.

## 13. Failure walkthrough incidentu MLOPS-PAY-90

Audit začal query nad top runs. Najvyšší candidate mal `validation.roc_auc=0.917`, no dataset parameter ukazoval mutable path a `metric_contract` chýbal. Run artifacts obsahovali model a plot, ale nie resolved config ani split membership. Environment file zachytil Python packages, no nie training image digest.

Tím zreprodukoval evaluation nad approved snapshotom a dostal ROC-AUC `0.889`. Rozdiel nevznikol model corruption; pôvodný run použil mixed dataset a repeated test feedback. Tag `best=true` bol manuálne nastavený ešte pred independent evaluation.

Containment zablokoval registry promotion pre runs bez required tracking schema. Pôvodný run zostal immutable a dostal annotation `incomplete-lineage`; metadata sa neprepísali tak, aby spätne predstierali úplnosť. Nový run použil immutable dataset, exact image digest a separate final evaluation. Jeho metric bola nižšia, ale evidence bolo authoritative.

## 14. Tracking contract a promotion gate

Platforma môže pred uzavretím candidate runu validovať required metadata a artifacts:

```python
required_params = {
    "code_commit",
    "dataset_digest",
    "split_generation",
    "resolved_config_digest",
    "training_image_digest",
    "metric_contract",
}

required_artifacts = {
    "resolved-config.json",
    "dataset-manifest.json",
    "evaluation/metrics.json",
    "evaluation/slices.parquet",
    "model/MLmodel",
}
```

Validation musí kontrolovať nielen názvy, ale aj resolve-nuteľnosť references, artifact checksums a model load smoke test. Run sa môže úspešne ukončiť ako experiment, ale nebude promotable candidate. Tým sa execution status oddeľuje od release eligibility.

## 15. Recovery a acceptance

Pozitívny test vytvorí run, zaloguje required inputs, metrics a artifacts, ukončí ho a z fresh clienta read-backom overí backend metadata aj artifact bytes. Forbidden test odmietne candidate s mutable dataset reference, missing metric contract alebo neapproved experiment. Unknown-outcome test preruší network počas logging-u a overí read-before-retry behavior. Second-run test zopakuje rovnaký intent s novým run ID a porovná lineage aj result tolerance.

```python
run = mlflow.get_run(run_id)
assert run.data.params["dataset_digest"].startswith("sha256:")

artifacts = {
    item.path
    for item in mlflow.artifacts.list_artifacts(run_id=run_id)
}
assert "resolved-config.json" in artifacts
assert "evaluation" in {path.split("/", 1)[0] for path in artifacts}
```

Tento read-back dokazuje, že tracker eviduje parameters a artifact paths. Neoveruje automaticky object checksum, model behavior ani business outcome; promotion pipeline musí pokračovať hlbším validation chainom.

## 16. Kontrolné otázky

1. Aký je rozdiel medzi experimentom, runom, logged modelom a Registry version?
2. Prečo najvyššia metric v UI nie je automaticky promotion verdict?
3. Čo autologging nevie odvodiť bez domain-specific instrumentation?
4. Ako sa líši backend store od artifact store a ako môžu divergovovať?
5. Ako sa má správať client pri timeout-e po tracking mutation?

## 17. Primárne zdroje

- [MLflow Tracking](https://mlflow.org/docs/latest/tracking/)
- [MLflow Tracking APIs](https://mlflow.org/docs/latest/ml/tracking/tracking-api)
- [MLflow artifact stores](https://mlflow.org/docs/latest/self-hosting/architecture/artifact-store/)
- [Remote experiment tracking with MLflow](https://mlflow.org/docs/latest/ml/tracking/tutorials/remote-server)

Experiment tracker je evidence service, nie oracle kvality. Jeho hodnota závisí od immutable identities, konzistentného tracking contractu a väzby na dataset, artifact, promotion, deployment a production outcome.
