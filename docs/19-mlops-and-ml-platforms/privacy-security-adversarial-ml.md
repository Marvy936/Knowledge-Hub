# Privacy, security a adversarial ML

Bezpečnosť ML systému zahŕňa tradičné aplikačné, dátové a infraštruktúrne riziká aj útoky, ktoré cielia na učenie, modelové správanie alebo informáciu zakódovanú v modeli. Privacy nie je iba šifrovanie datasetu. Určuje, ktoré údaje smú vstúpiť do tréningu, čo môže byť odvodené z modelu alebo telemetry a kto môže vykonať inference, export, explanation alebo retraining.

V incidente `MLOPS-PAY-96` získal interný analytický účet prístup k prediction endpointu a detailným explanation logs. Účet nemohol čítať training table, ale mohol posielať veľké množstvo adaptívnych queries. Súčasne sa do retraining snapshotu dostali feedback records bez provenance a monitoring ukladal takmer surové features. Incident preto nemal jednu príčinu. Spájal nadmernú inference autoritu, privacy leakage cez outputy a logging, chýbajúcu abuse detekciu a poisoning boundary v feedback pipeline.

## 1. Security a privacy subject

Threat model musí viazať presný systém, model a lifecycle generation. Všeobecné tvrdenie „model je za API gateway“ nevysvetľuje, kto ovláda training inputs, kto pozná model architektúru, aké outputy endpoint vracia ani aké side effects môže prediction vyvolať.

```yaml
security_subject:
  system_id: fraud-decision-platform
  release_id: fraud-serving-2026-08-03.4
  model_digest: sha256:31d7...
  intended_use: transaction-risk-prioritization-v6
assets:
  - training_data
  - feature_definitions
  - model_artifact
  - inference_outputs
  - explanations
  - feedback_labels
  - deployment_credentials
attack_surfaces:
  - data_ingestion
  - training_pipeline
  - artifact_store
  - registry
  - inference_api
  - monitoring_and_feedback
privacy_population:
  data_subjects: customers-and-merchants
  retention_policy: fraud-privacy-v8
```

Subject musí zahŕňať aj environment, action policy a telemetry scope. Rovnaký model v internom batch scoringu a v externom low-latency API má odlišný attacker capability a privacy exposure.

## 2. Threat actors, capability a lifecycle stage

Adversár môže byť externý caller, compromised service account, malicious data supplier, insider, dependency maintainer alebo tenant zdieľajúci platformu. Capability zahŕňa knowledge o modeli, možnosť meniť training data, počet a adaptívnosť queries, prístup k gradients alebo artifacts a kontrolu nad deploymentom.

NIST adversarial-ML taxonómia rozlišuje útoky podľa lifecycle stage, cieľa, capability a knowledge. Pre predictive ML sú dôležité najmä evasion, poisoning a privacy attacks. Tento rámec je terminologická a risk-management pomôcka; nie je dôkazom, že konkrétny control útok odstránil.

Threat model preto zaznamená:

```text
actor
→ access path
→ knowledge
→ mutable subject
→ intended security/privacy impact
→ detection evidence
→ prevention/containment controls
```

Neznámy alebo čiastočný attacker knowledge sa nesmie zjednodušiť na „black box“. Query volume, output precision a feedback access môžu dať prakticky silnejšiu capability než znalosť architektúry.

## 3. Data minimization, purpose a retention

Najbezpečnejší citlivý údaj je ten, ktorý systém nepotrebuje. Dataset contract preto odlišuje required features, optional research fields, prohibited attributes a derived proxies. Každé pole má purpose, ownera, lawful/approved basis podľa organizačného contextu, retention a access class.

Raw identifiers sa často nahrádzajú stable pseudonymous join key, no pseudonymizácia nie je anonymizácia. Kombinácia časových, lokálnych a behaviorálnych features môže znovu identifikovať osobu. Privacy review preto hodnotí celý feature set a linkability, nie iba prítomnosť mena.

Training snapshot, experiment artifact, trace a debug export môžu mať rozdielnu retention. Automatický copy do notebooku alebo lokálneho cache môže obísť centrálnu policy. DLP, object-store policy, encryption, audit a deletion workflow musia pokrývať derived datasets aj artifacts.

## 4. Privacy attacks a model leakage

Membership inference sa pýta, či konkrétny záznam pravdepodobne patril do training data. Model inversion alebo reconstruction sa snaží odvodiť citlivé vlastnosti alebo reprezentatívne inputs. Model extraction sa snaží aproximovať model alebo jeho decision boundary z queries. Tieto kategórie sa môžu prekrývať a riziko závisí od output detailu, overfittingu, query accessu a auxiliary knowledge.

Mitigácie sa vrstvia. Data minimization a regularization znižujú memorization risk. Differential privacy môže poskytnúť formálny privacy budget pre konkrétny training mechanismus, ale utility, accounting a composition musia byť explicitné. Output rounding, obmedzenie explanation detailu, authentication, rate limits a abuse detection znižujú query capability, no samy neposkytujú matematický privacy dôkaz.

Privacy test report musí uviesť model generation, dataset population, attacker assumptions, query budget, baseline a uncertainty. Jedna nízka attack accuracy bez realistickej baseline alebo s obmedzenejším attackerom než produkčný caller nie je acceptance.

## 5. Evasion a robust input boundary

Evasion útok mení inference input tak, aby model vytvoril nežiaduci output. Pri tabular fraud systéme môže ísť o manipuláciu business fields v povolených rozsahoch; pri obraze o malé alebo fyzicky realizovateľné zmeny; pri textovom systéme o obchádzanie classifiera. Security otázka nie je len „dokáže model rozpoznať adversarial example“, ale či celý systém vie odmietnuť invalid subject a bezpečne spracovať uncertainty.

Input boundary obsahuje schema, units, range, cross-field invariants, provenance a rate/behavior controls. Model nesmie byť prvou a jedinou validačnou vrstvou. Out-of-distribution alebo low-confidence input môže vyvolať abstention, fallback alebo human review podľa risk policy.

Robustness test používa domain-valid transformations a threat model. Náhodný noise test nie je náhradou za motivated adversary. Zároveň adversarial benchmark nesmie potichu meniť label semantics alebo vytvárať nerealizovateľné inputs.

## 6. Poisoning, backdoor a feedback integrity

Poisoning mení training data, labels alebo pipeline tak, aby poškodil dostupnosť, všeobecnú performance alebo vybraný target. Backdoor vytvára správanie aktivované triggerom, ktorý môže byť v bežnom aggregate evaluation takmer neviditeľný. Feedback-driven systémy sú obzvlášť citlivé, pretože production action ovplyvňuje, ktoré labels vzniknú.

Ingestion contract preto viaže source identity, schema, event time, producer version, signatures/checksums, deduplication a quality/quarantine verdict. High-impact label source môže vyžadovať dual control alebo audit sample. Human correction sa nezapisuje priamo do authoritative training setu bez provenance a validation.

```text
raw feedback
→ authenticated producer
→ immutable landing
→ schema a semantic validation
→ duplicate/conflict analysis
→ quarantine alebo accepted snapshot
→ training dataset version
```

Poisoning detection nemôže byť iba outlier removal. Útočník môže vytvoriť valid-looking, segmentovo cielené records. Potrebné sú source-level rate a distribution controls, label disagreement, influence/segment analysis a known-clean holdout.

## 7. Model, artifact a serialization security

Model artifact je executable-adjacent input. Pickle a podobné formáty môžu pri deserializácii vykonať code. Artifact sa preto načítava iba z trusted store po digest a signature verification, v izolovanom runtime a s minimálnymi credentials. „Je to iba model file“ nie je security boundary.

Package manifest viaže model bytes, code paths, dependencies, signature, SBOM/provenance a expected loader. Runtime nesmie automaticky sťahovať arbitrary code podľa metadata z neovereného artifactu. Conversion medzi formátmi potrebuje parity test, pretože bezpečnejší runtime formát môže zmeniť numerické správanie.

Registry authorization oddeľuje create version, set alias, delete a read artifact. Caller, ktorý môže iba čítať metadata, nemá automaticky dostať raw model bytes alebo training examples.

## 8. Inference API, abuse a output policy

Endpoint používa strong identity, least privilege, tenant isolation, bounded request size, timeout, rate/quota a anomaly detection. Rate limit sa viaže na actor a operation class, nie iba IP adresu. Bulk batch export a interactive inference majú odlišné permissions.

Output policy určuje score precision, explanation, confidence, model/version metadata a error detail. Debug stack trace, feature contribution alebo exact threshold môže zvýšiť extraction alebo evasion capability. Prevádzka však stále potrebuje request-correlated internal evidence; riešením je rozdeliť external response a protected audit trace.

Abuse detection sleduje query similarity, boundary probing, unusual coverage population, high reject rate a credential sharing. Alert musí viesť k throttlingu, token revocation alebo investigation, nie automaticky k zablokovaniu legitímneho high-volume batch klienta bez contextu.

## 9. Secrets, network a workload isolation

Training a serving workload dostáva iba credentials potrebné pre konkrétny subject a čas. Secret sa nepíše do run params, model tags, traces ani Docker layer. Workload identity a short-lived token sú preferované pred shared static key.

Network policy oddeľuje training, artifact, registry, feature a serving paths. Egress z model runtime sa obmedzí, ak ho model nepotrebuje. Multi-tenant GPU alebo node sharing musí rešpektovať memory/fault isolation a side-channel risk; time-slicing nie je security izolácia.

Admin UI, tracking server a object store potrebujú TLS, authentication, authorization, audit a backup. ML-specific controls nenahrádzajú patching, vulnerability management a incident response tradičného software stacku.

## 10. Privacy-safe telemetry a incident evidence

Monitoring musí zachovať evidence bez neobmedzeného zberu citlivých inputs. Contract určuje redaction, hashing, aggregation, sampling, access a retention. Hash nízko-entropického údaja nemusí chrániť privacy, pretože sa dá slovníkovo obnoviť.

Trace môže uložiť schema verdict, feature generation a protected pointer namiesto raw payloadu. Security incident môže vyžadovať legal hold; ten musí byť explicitný, časovo ohraničený a auditovaný, nie permanentná výnimka z deletion policy.

Telemetry pipeline sama je attack surface. Poisoned metrics, disabled logging alebo selective trace sampling môžu skryť útok. Sleduje sa coverage, freshness a integrity monitoring evidence.

## 11. Security testing a red teaming

Security testing kombinuje code/dependency scanning, access-control tests, artifact verification, malformed inputs, rate/abuse scenarios, poisoning simulations, evasion/robustness tests, privacy assessment a recovery drill. Test subject a attacker capability sú versioned.

Red team nepreukazuje úplnú bezpečnosť. Hľadá concrete failure paths pod dohodnutým scope. Findings sa viažu na ownera, severity, containment, remediation a retest. Absencia findings pri úzkom query budgete nie je dôkaz, že model nie je extractable alebo privacy-safe.

Produkčný canary používa bounded blast radius a nesmie testovať nevratné útoky na skutočných data subjects bez schválenej policy. Bezpečnostný experiment má vlastný approval a cleanup.

## 12. Failure hypotheses, recovery a acceptance

Pri podozrení na leakage sa skúma source dataset access, artifact download, endpoint queries, output detail, explanations a telemetry exports. Pri apparent poisoning sa skúma producer identity, label definition, snapshot lineage, pipeline code a business policy. Pri evasion spike sa oddeľuje reálny traffic shift, feature bug a motivated probing.

Containment môže zrušiť credentials, obmedziť output, freeze retraining, quarantine data, presmerovať traffic na safe fallback alebo odpojiť compromised artifact. Pred rotáciou a deletion sa zachytí audit evidence podľa incident a privacy policy.

Pozitívna acceptance vyžaduje explicitný threat model, least privilege, privacy/data contract, artifact verification, abuse monitoring, adversarial/robustness tests a incident runbook. Recovery acceptance vyžaduje odstránenie kompromitovanej generácie, credential rotation, data/artifact lineage review, downstream reconciliation a ďalší clean operation. Forbidden acceptance je „endpoint je interný“, encryption-at-rest bez access control alebo adversarial accuracy bez attacker assumptions.

Second-operation test zopakuje inference, retraining snapshot alebo artifact load po containment-e. Ak starý token, cache alebo mutable alias stále umožní prístup ku kompromitovanej generácii, recovery nie je uzavretá.
