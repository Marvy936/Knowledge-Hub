# ML lifecycle a rozdiel medzi DevOps a MLOps

MLOps nie je DevOps s pridaným slovom „model“. DevOps rieši bezpečný a opakovateľný tok zmeny softvéru od source code cez build, test, release a runtime prevádzku. ML systém má rovnaký softvérový tok, ale jeho správanie navyše závisí od dát, feature definícií, labelov, tréningového prostredia, model artifactu, rozhodovacej policy a oneskoreného produkčného feedbacku. Zmena produkčného výsledku preto môže vzniknúť aj bez jediného nového commitu aplikácie.

Atlas Payments používa v tejto sekcii incident `MLOPS-PAY-90`. Risk tím vyhlásil nový model za úspešne nasadený, pretože CI pipeline bola zelená, training job skončil stavom `Succeeded` a model server vrátil HTTP 200. O dva dni neskôr sa počet manuálne skontrolovaných operácií znížil o tretinu a recovered loss klesol. Model weights boli správne, ale training job použil nový dataset snapshot, experiment nemal zaznamenaný image digest, deployment načítal starší feature contract a queue zostala na novej kapacitnej policy. Každý jednotlivý subsystém vyzeral zdravo; chybný bol composite generation celého ML produktu.

## 1. Dominantný ML lifecycle

ML lifecycle začína business rozhodnutím, nie notebookom ani tréningovým frameworkom. Tím musí najprv určiť, ktorý outcome chce ovplyvniť, aká observation unit sa hodnotí, kto vlastní finálny side effect a aký dôkaz bude znamenať prijateľné zlepšenie. Až potom vzniká dataset, experiment a model.

```text
business objective a decision contract
→ observation, label a feature contract
→ dataset snapshot a quality evidence
→ code, configuration a environment generation
→ training run a experiment record
→ model artifact a evaluation evidence
→ validation a promotion decision
→ deployment a serving generation
→ prediction, policy a business action
→ delayed ground truth a production outcome
→ monitoring, recovery a controlled retraining
```

Tento reťazec obsahuje viac samostatných autorít. Git je autorita pre deklarovaný code a configuration intent. Dataset registry alebo manifest je autorita pre presnú populáciu vstupných dát. Experiment tracker eviduje vykonané runy. Artifact store drží bytes modelu a ďalších výstupov. Model Registry eviduje kandidáta a promotion rozhodnutie. Serving platforma ukazuje načítaný runtime artifact. Business databáza a mature labels dokazujú finálny outcome. Žiadna z týchto vrstiev sama nepreukazuje celý lifecycle.

## 2. Čo DevOps už rieši správne

MLOps nestavia mimo DevOps. Preberá jeho základné mechanizmy: version control, code review, immutable build artifacts, automatizované testovanie, CI, environment promotion, observability, least privilege, rollback, incident response a ownership. Ak organizácia nevie spoľahlivo identifikovať container image alebo prevádzkovú konfiguráciu, ML platforma tento problém nevyrieši; iba pridá ďalšie mutable inputs.

DevOps pipeline môže napríklad vytvoriť image `risk-trainer@sha256:31ab...`, podpísať ho, overiť dependency graph a nasadiť ho do Kubernetes. Tým je preukázané, ktorý executable environment bol publikovaný. Nie je však ešte preukázané, ktorý dataset tento image čítal, aké features boli dostupné v event time, aký seed a hyperparameters použil, ktorý model artifact vytvoril ani či model zlepšil business outcome.

MLOps preto rozširuje, nie nahrádza, DevOps chain. Každá známa softvérová kontrola zostáva potrebná, ale jej subject sa musí rozšíriť z „verzia aplikácie“ na presnú zostavu code, data, environment, model a policy generácií.

## 3. Čo pridáva MLOps

MLOps pridáva štyri hlavné druhy variability. Prvým sú mutable data: rovnaký code spustený zajtra môže dostať inú populáciu, opravené labels alebo nové partitions. Druhým je štatistický training: výsledok môže závisieť od splitu, seedov, nondeterministic kernels a optimalizačnej trajektórie. Tretím je oddelenie offline a online sveta: feature dostupná pri tréningu nemusí byť dostupná alebo identicky vypočítaná pri serving-u. Štvrtým je delayed feedback: pravdivý business outcome môže dozrieť až po dňoch alebo mesiacoch.

Tieto rozdiely menia release model. Pri bežnej službe je často možné povedať, že commit `abc123` vytvoril image digest `sha256:...` a ten beží v deployment-e. Pri ML produkte musí release record navyše uviesť dataset snapshot, feature schema, label contract, training run, model digest, evaluation set, threshold alebo ranking policy, serving runtime a exposure cohort.

MLOps zároveň pridáva continuous training. CT neznamená, že model sa má automaticky pretrénovať pri každom novom dátovom súbore. Znamená kontrolovaný mechanizmus, ktorý vie zistiť dôvod retrainingu, vytvoriť nový candidate, porovnať ho s incumbentom a zastaviť promotion, ak nie je splnený data, model, system alebo business gate.

## 4. Exact ML product subject

Tvrdenie „model v7 je v produkcii“ je neúplné. Exact subject musí byť dostatočný na reprodukciu, audit a rollback. Praktický manifest môže vyzerať takto:

```yaml
ml_product: payment-risk-prioritization
release_id: mlpay-2026-08-03.1
business_operation: prioritize_manual_review
observation_unit: payment_operation_id
population_contract: cnp-eur-v5
label_contract: confirmed-loss-30d-v3
dataset_manifest: s3://ml-data/risk/snapshots/2026-07-31/manifest.json
dataset_digest: sha256:9bd7...e802
feature_view: payment-risk-features-v6
feature_code_commit: 2e48b91
training_code_commit: 77a51d0
trainer_image: registry.example/risk-trainer@sha256:31ab...91fe
run_id: 6f7b8fa3b5ad4aaead859f1a5d771301
model_artifact: s3://ml-artifacts/6f7b.../model/model.pkl
model_digest: sha256:b8ae...7d22
evaluation_snapshot: risk-holdout-2026q2-v2
threshold_policy: review-capacity-2500-v4
serving_image: registry.example/risk-serving@sha256:80cd...7810
deployment: risk-api-prod-eu1
exposure: 10-percent-shadow
owner: risk-ml-platform
business_owner: risk-operations
```

Manifest nie je duplicita nástrojov. Je to join key medzi nimi. `run_id` ukáže experiment metadata, `model_digest` overí bytes, deployment ukáže loaded generation a business operation určí downstream evidence. Ak niektorá väzba chýba, tím nevie bezpečne odpovedať na otázku „čo presne sme nasadili?“.

## 5. Viacero navzájom previazaných lifecycle-ov

ML produkt má najmenej data lifecycle, model lifecycle, software lifecycle a business-decision lifecycle. Data lifecycle sleduje ingest, validáciu, point-in-time transformácie, snapshot a retention. Model lifecycle sleduje training, evaluation, candidate, registration, promotion a retirement. Software lifecycle sleduje source, build, image, deployment a runtime. Business lifecycle sleduje prediction, policy decision, human alebo automatický action a neskorší outcome.

Tieto lifecycle-y sa nesmú zlúčiť do jedného statusu. `Training Succeeded` znamená, že definovaný job dokončil execution path. `Model approved` znamená, že promotion autorita akceptovala konkrétny candidate podľa dostupných gates. `Deployment Available` znamená, že serving platforma má požadovaný počet ready replík. Až request-correlated trace preukazuje, že konkrétna prediction použila správne features a model. Až business evidence ukazuje, že action prebehol a outcome sa zlepšil.

V incidente `MLOPS-PAY-90` dashboard ukazoval zelené tri prvé stavy, ale chýbal join medzi prediction requestom, queue actionom a mature labelom. Tím preto nevidel, že nové scores boli správne, no stará feature generation a nová capacity policy zmenili population aj počet vykonaných kontrol.

## 6. Development, validation a production nie sú iba tri clustre

Environment boundary v MLOps nepredstavuje iba názov Kubernetes namespace. Development experiment môže používať sample dataset, notebook dependencies a dočasný tracking store. Validation potrebuje immutable evaluation snapshot, controlled secrets a runtime podobný produkcii. Production serving potrebuje live feature dependencies, explicitnú policy, SLO a audit. Training production modelu môže prebiehať v oddelenom training environment-e, ale musí používať schválené data a artifact boundaries.

Prechod medzi prostrediami preto neznamená skopírovať model file. Promotion musí zachovať artifact identity a zmeniť iba environment-specific references alebo deployment policy. Ak sa model pri promotion znovu exportuje, konvertuje alebo kompiluje, vzniká nový artifact generation, ktorý potrebuje vlastnú validáciu. Rovnaké platí pre feature transformations a preprocessing graph.

## 7. CI, CD a CT v ML systéme

CI pre ML overuje viac než syntax a unit testy. Kontroluje schema contracts, point-in-time joins, deterministic transforms, data-test fixtures, training code, environment lock, model interface a reprodukovateľnosť malého smoke runu. Nemôže však v každom pull requeste preukázať finálnu model quality na plnom datasete, ak je tréning drahý alebo labels dozrievajú pomaly.

Continuous Delivery vytvára promotable candidate a overuje, že model sa dá bezpečne zabaliť, načítať, interrogovať a nasadiť. Deployment môže zostať manuálne schválený alebo automatický podľa rizika. Continuous Training spúšťa nový training lifecycle na základe času, nových labelov, driftu, opravy chyby alebo explicitného rozhodnutia. CT nesmie obísť independent test ani promotion policy len preto, že trigger bol automatický.

```text
code/data change
→ CI validation
→ training candidate
→ offline evaluation
→ registration
→ promotion gate
→ shadow alebo canary
→ production evidence
→ approve, rollback alebo retrain
```

Každá šípka potrebuje operation identity. Retry training jobu vytvára nový run, aj keď používa rovnaký intent. Retry promotion po timeout-e musí najprv read-backom zistiť, či registry mutation už prebehla. Retry business actionu musí používať idempotency key, pretože model score nie je operation identity.

## 8. Control plane, execution plane a evidence plane

MLOps platforma má control plane, ktorý eviduje experiments, registry records, pipeline definitions, approvals a desired deployments. Execution plane vykonáva data processing, training a inference. Evidence plane zbiera immutable manifests, metrics, logs, traces, artifacts a business outcomes. Tieto roviny môžu divergovovať.

Registry alias môže ukazovať na candidate model, no serving Pod stále môže mať v pamäti predchádzajúci digest. Pipeline UI môže hlásiť úspech, no artifact upload mohol skončiť partial alebo na lokálnom disku workera. Deployment desired state môže obsahovať správny model URI, ale init container mohol použiť stale cache. Autoritatívny verdict preto potrebuje configured, resolved, loaded a exercised state.

```text
configured: registry alias alebo deployment manifest
resolved: presný model URI a digest po resolution
loaded: runtime potvrdil načítaný digest
exercised: request trace použil tento digest
outcome: downstream action a mature label patria k tomu istému requestu
```

## 9. Promotion nie je kopírovanie súboru

Promotion je rozhodnutie, že konkrétny immutable candidate spĺňa definované gates pre ďalšiu exposure úroveň. Môže zmeniť registry alias, release manifest alebo deployment reference, ale nesmie potichu zmeniť bytes modelu. Promotion record musí obsahovať approvera alebo policy, evidence snapshot, exceptions, target environment a rollback subject.

Model môže mať lepšie ROC-AUC a zároveň horší calibration, latency alebo subgroup harm. Preto gate nie je jedno číslo. Obsahuje data validity, model metrics, system compatibility, security, resource limits, operational readiness a business guardrails. Neskoršie kapitoly rozoberú registry a promotion detailne; tu je dôležité, že „best run“ nie je automaticky release candidate.

## 10. Failure walkthrough incidentu MLOPS-PAY-90

Prvý symptom bol pokles review completion, nie chyba model servera. Tím najprv predpokladal, že model sa zhoršil, a pripravil retraining. Evidence-preserving postup však začal exact release manifestom a request IDs z affected aj healthy obdobia.

Dataset digest a model digest sa zhodovali s approved runom. Offline replay nad immutable request sample vrátil rovnaké scores, čím oslabil hypotézu poškodených weights. Online trace ukázal zvýšený fallback pre feature `merchant_velocity_7d`; serving deployment používal starší feature-view reference. Aj po simulovanom opravení feature parity však predicted queue size nevysvetľoval celý pokles. Druhý divergence vznikol v policy layeri: capacity policy `v4` znižovala denný limit počas špičky a bola nasadená nezávisle od modelu.

Root cause preto nebol jeden chybný model. Bol to neúplný release subject a chýbajúci join medzi model promotion, feature generation a queue policy. Retraining by vytvoril nový model, ale neodstránil ani jednu z týchto príčin a ešte by zničil attribution.

## 11. Containment, recovery a rollback

Containment musí znížiť harm bez zničenia dôkazov. Atlas najprv zastavil ďalšie zvyšovanie exposure, zachoval request traces a zamrazil automatické retraining triggery. Následne v shadow režime obnovil intended feature view a prepočítal predicted queue. Queue policy bola rollbacknutá na známu generation samostatne, aby bolo možné odmerať efekt každej zmeny.

Recovery sa uzavrela v troch vrstvách. Component recovery potvrdila feature parity a loaded model digest. Journey recovery prešla reprezentatívne requesty od point-in-time features cez prediction a queue assignment. Business recovery sledovala dokončené reviews a mature confirmed-loss outcome. Druhá operácia na novom cohort-e overila, že systém nepoužil stale cache a že retraining trigger zostal správne blokovaný.

Rollback modelu by bol správny iba vtedy, keby evidence ukázala model-level divergence alebo neprijateľný outcome viazaný na konkrétny artifact. V tomto incidente by model rollback mohol náhodne zmeniť queue mix, ale nebol by kauzálnou opravou.

## 12. Acceptance model

Pozitívna acceptance musí preukázať presný chain od release manifestu po business outcome. Forbidden acceptance overuje, že neapproved dataset, neznámy artifact digest alebo incompatible feature schema sa nedostane do promotion. Adjacent acceptance kontroluje, že oprava jedného modelu nepoškodila iný tenant, cohort alebo shared capacity. Second-operation acceptance opakuje lifecycle s novým runom alebo requestom a odhaľuje stale state, cache a non-idempotent mutations.

Minimálny production verdict preto obsahuje:

- exact composite release subject — manifest určuje code, data, environment, model, feature, policy a deployment generation a každú immutable reference možno nezávisle resolve-nuť;
- offline evidence — metrics a reports sú viazané na presný dataset, split a evaluation contract, takže screenshot dashboardu nemôže nahradiť reprodukovateľný result;
- loaded a exercised generation — runtime read-back a request trace potvrdzujú model, feature a policy generation, ktoré skutočne obslúžili konkrétne requests;
- rollout evidence — population, fallbacks, latency a action-completion denominators ukazujú, či exposure a downstream workflow zodpovedali schválenému experimentu;
- business evidence — mature outcome je priradený k release-u alebo je dočasný proxy explicitne označený s maturity a uncertainty hranicou;
- recovery evidence — rollback subject, owner, component/journey/business recovery a second-operation výsledok dokazujú, že systém sa nevrátil iba do zdanlivo zeleného stavu.

Tieto body sumarizujú už vysvetlený lifecycle. Samotné vyplnenie checklistu bez korelovateľných IDs nepredstavuje dôkaz.

## 13. Praktický minimálny release record

Jednoduchý repository-native record môže spájať Git a externé autority bez kopírovania veľkých artifactov do repozitára:

```json
{
  "release_id": "mlpay-2026-08-03.1",
  "code_commit": "77a51d0",
  "dataset_digest": "sha256:9bd7...e802",
  "training_image_digest": "sha256:31ab...91fe",
  "experiment_run_id": "6f7b8fa3b5ad4aaead859f1a5d771301",
  "model_digest": "sha256:b8ae...7d22",
  "feature_view": "payment-risk-features-v6",
  "threshold_policy": "review-capacity-2500-v4",
  "deployment_generation": "risk-api-prod-eu1-184",
  "evidence_bundle": "s3://ml-evidence/mlpay-2026-08-03.1/"
}
```

CI môže overiť schema, formát digestov, existenciu references a zakázať mutable tags ako `latest`. Promotion controller následne zapisuje observed deployment generation a rollout result do oddeleného append-only evidence recordu. Git history tak zostáva authority pre intended release, nie falošným skladom runtime truth.

## 14. Kontrolné otázky

1. Ktoré zmeny môžu zmeniť ML production outcome bez zmeny application commitu?
2. Prečo úspešný training job nepreukazuje model quality ani business outcome?
3. Aký je rozdiel medzi registry subjectom, loaded runtime subjectom a exercised request subjectom?
4. Prečo je continuous training samostatný controlled lifecycle a nie automatický deployment?
5. Ktoré evidence by v incidente `MLOPS-PAY-90` podporili model-level root cause a ktoré ho falsifikovali?

## 15. Primárne zdroje

- [MLflow Tracking concepts](https://mlflow.org/docs/latest/tracking/)
- [OpenLineage object model](https://openlineage.io/docs/spec/object-model/)
- [DVC Get Started — versioning data and models](https://dvc.org/doc/start)

Dokumentácia nástrojov vysvetľuje ich object model a API. Production MLOps contract však musí navyše definovať, ako sa tieto objekty spájajú s identity, promotion, serving a business outcome vrstvou konkrétnej organizácie.
