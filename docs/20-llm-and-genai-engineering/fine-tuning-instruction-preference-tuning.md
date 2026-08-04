# Fine-tuning, instruction tuning a preference tuning

Fine-tuning mení model parameters alebo pripojené trainable adapters tak, aby model stabilnejšie vykonával konkrétnu úlohu, formát alebo behavior. Nie je to náhrada za retrieval, authorization, current source-of-truth ani deterministic business logic. Ak sa problém nachádza v nesprávnom candidate sete, chýbajúcej exception clause alebo zlom tool precondition, fine-tuning môže iba naučiť model presvedčivejšie opakovať nesprávny vzorec.

V incidente `GENAI-SUPPORT-05` tím reagoval na zlé RAG odpovede supervised fine-tuningom nad historickými „úspešnými“ support transcripts. Dataset obsahoval staré policy versions, odpovede bez citations a cases označené ako úspešné iba preto, že ticket bol zatvorený. Fine-tuned model začal pri chýbajúcom evidence generovať rozhodné odpovede zo zapamätaných patterns. Retrieval chyba zostala a model navyše znížil abstention rate. Root cause bol nesprávny use case a slabý data contract, nie nedostatočný počet epochs.

## 1. Training subject

Fine-tuned release musí byť rozbaliteľná na base model, tokenizer/chat template, training method, dataset generations, preprocessing, hyperparameters, code/environment, output artifact a eval suite.

```yaml
fine_tuned_release:
  release: support-sft-v4
  base_model: support-base-2026-07-28
  tokenizer_profile: provider-managed-2026-07
  method: supervised
  training_dataset: support-demonstrations-2026-08-04
  validation_dataset: support-demonstrations-val-2026-08-04
  preprocessing: chat-normalizer-v6
  hyperparameters:
    epochs: 2
    batch_size: auto
    learning_rate_multiplier: 0.5
  training_job: ftjob-8421
  output_model: support-sft-2026-08-04-01
  eval_suite: support-behavior-gate-2026-08-04
```

Mutable output alias bez job, dataset a base-model identity nie je reprodukovateľný model release.

## 2. Kedy fine-tuning dáva zmysel

Fine-tuning je vhodný, keď prompt a examples už ukazujú požadované správanie, ale model ho vykonáva príliš nestabilne alebo draho. Typické use cases sú bounded classification, extraction do stabilného formátu, domain style, tool selection patterns, response structure a opakovaný instruction-following behavior.

Pri často sa meniacich facts, policy versions a tenant-specific records je vhodnejší retrieval alebo tool lookup. Fine-tuning ukladá patterns do model parameters; aktualizácia jedného faktu vyžaduje nový dataset, training a release, pričom zabudnutie starej verzie nie je garantované.

```text
current knowledge → retrieval/tool
stable behavior pattern → prompt/examples alebo fine-tuning
hard business constraint → deterministic validation/authorization
```

Rozhodnutie sa robí podľa failure stage, update frequency, risku a evalov, nie podľa dojmu, že „model potrebuje vedieť viac“.

## 3. Adaptation hierarchy

Pred trainingom sa overí lacnejšia a kontrolovateľnejšia vrstva:

```text
clear instruction
→ examples a structured output
→ retrieval/tool correction
→ deterministic validator
→ fine-tuning candidate
```

Táto postupnosť nie je absolútna, ale zabraňuje používaniu trainingu na maskovanie application bugov. Ak prompt nemá jednoznačný target alebo dataset nemá konzistentné labels, fine-tuning iba zosilní nejasnosť.

## 4. Supervised fine-tuning

Supervised fine-tuning, SFT, používa input-output demonstrations. Model sa učí zvyšovať pravdepodobnosť target response pri danom inpute. Instruction tuning je širší SFT pattern nad rozmanitými tasks formulovanými ako instructions a responses, aby model lepšie generalizoval instruction following.

```json
{"messages":[
  {"role":"developer","content":"Classify the support request. Return JSON."},
  {"role":"user","content":"My approved refund has not arrived."},
  {"role":"assistant","content":"{\"intent\":\"refund_status\",\"escalate\":false}"}
]}
```

Target musí predstavovať želané production behavior. Historický assistant output nie je automaticky label; môže obsahovať workaround, outdated policy alebo skrytú human correction.

## 5. Instruction tuning

Instruction-tuning dataset obsahuje rôzne formulations, tasks, constraints a response styles. Cieľom nie je memorovať konkrétne wording, ale naučiť mapping medzi instruction a desired behavior.

Coverage zahŕňa positive, negative, ambiguous a refusal cases. Ak dataset obsahuje iba úspešné answerable prompts, model sa naučí odpovedať aj tam, kde má abstainovať. Pri structured workload sa examples líšia obsahom, ale zachovávajú schema contract.

```yaml
instruction_segments:
  - direct_classification
  - ambiguous_request
  - missing_required_field
  - unauthorized_action
  - insufficient_evidence
  - conflicting_policy
  - multilingual
```

Segment weights a sampling policy sú súčasť training generation.

## 6. Preference data

Preference tuning používa pairs alebo rankings odpovedí. Každý example obsahuje prompt, preferred response a rejected response, prípadne strength alebo rubric metadata.

```json
{
  "input": {
    "messages": [
      {"role": "user", "content": "Can you approve this refund without evidence?"}
    ]
  },
  "preferred_output": [
    {"role": "assistant", "content": "I cannot approve it without the required evidence."}
  ],
  "non_preferred_output": [
    {"role": "assistant", "content": "Yes, I have approved the refund."}
  ],
  "rubric": "authorization-and-evidence"
}
```

Pair vyjadruje relatívnu preferenciu v konkrétnom contextu. Neurčuje automaticky absolútnu correctness. Obe odpovede môžu byť zlé alebo preference môže odrážať style namiesto factual quality.

## 7. RLHF lifecycle

Reinforcement learning from human feedback typicky začína supervised modelom, pokračuje preference collection a reward-model trainingom a následne optimalizuje policy model proti reward signálu s obmedzením odchýlky od reference modelu.

```text
base model
→ supervised demonstrations
→ preference comparisons
→ reward model
→ policy optimization
→ evaluation a rollout
```

Reward model aproximuje labels a môže byť gamed. Vysoká reward score nie je business acceptance. Training pipeline potrebuje holdout preferences, reward calibration, safety evals a kontrolu reward hackingu.

## 8. Direct Preference Optimization

Direct Preference Optimization, DPO, optimalizuje policy priamo z preferred/rejected pairs bez samostatného reward-model-plus-RL loopu. Zjednodušuje pipeline, ale neznižuje požiadavky na quality a representativeness preference dát.

DPO parameter `beta` alebo ekvivalent riadi trade-off medzi preferenciou a odchýlkou od reference policy. Príliš agresívny update môže zhoršiť general capabilities alebo prehnane zosilniť annotation bias.

```yaml
preference_training:
  method: dpo
  base_model: support-sft-v3
  dataset: support-preferences-v5
  beta: 0.1
  epochs: 1
  heldout_preferences: support-preferences-test-v5
```

Konkrétne hyperparameter hodnoty sú experiment subject, nie univerzálny default.

## 9. Reinforcement fine-tuning a graders

Niektoré platformy umožňujú fine-tuning proti programmatic alebo model graderu. Je to vhodné pri úlohách s robustným verifiable rewardom, napríklad exact structured transformation alebo unit-test outcome. Slabý grader však vytvorí priamy optimization target pre exploit.

```text
prompt
→ candidate output
→ grader
→ reward
→ parameter update
```

Grader sa pred trainingom validuje na adversarial cases. Ak reward meria iba presence citation labelu, model sa môže naučiť pridávať labels bez validného supportu.

## 10. Data authority

Training data má ownera, source, rights, classification, consent/retention policy a label authority. Production transcript nie je voľný training corpus. Môže obsahovať personal data, secrets, copyrighted content alebo customer-specific instructions.

```yaml
training_record_provenance:
  record_id: demo-1842
  source: reviewed-support-case
  source_time: 2026-07-14
  label_owner: support-quality
  policy_generation: refund-policy-v7
  privacy_classification: internal-pseudonymized
  usage_right: model-training-approved
  review_status: adjudicated
```

Redaction sa vykonáva pred uploadom alebo trainingom a testuje sa, že identifiers nemožno rekonštruovať z derived datasetu.

## 11. Label generation

Labels môžu písať experts, trained annotators, deterministic systems alebo teacher models. Každý source má inú authority a bias. Teacher-generated response sa nepovažuje za truth bez validation.

Rubric musí vysvetliť correctness, completeness, evidence, style a refusal. Ak annotators preferujú dlhšie odpovede, model môže nadmerne verbose output interpretovať ako quality. Pairwise disagreement a adjudication sa uchovávajú ako signal.

```yaml
label_quality:
  annotators_per_case: 2
  expert_adjudication: required_on_disagreement
  agreement_metric: reported
  teacher_model_used: true
  teacher_output_reviewed: true
```

## 12. Dataset cleaning a deduplication

Near-duplicate demonstrations môžu preťažiť jeden pattern a vytvoriť leakage medzi train a eval. Dedup sa vykonáva na prompt, response aj source-case identity. Rovnako sa odstránia contradictory labels alebo sa explicitne segmentujú podľa policy generation.

Data cleaning nesmie bez záznamu vyhodiť rare failure cases. Outliers môžu byť critical exceptions, nie noise. Každý filter má version a report countov pred/po transformácii.

## 13. Temporal validity

Dataset s mutable business knowledge potrebuje effective-time semantics. Odpoveď správna v júni môže byť nesprávna v auguste. Fine-tuning na mixe policy generations bez time/context fieldov učí model konflikt.

Pre stable behavior možno policy-specific content nahradiť abstrahovaným patternom:

```text
Namiesto: "Refund deadline is 30 days"
Uč: "Use only the current retrieved policy and cite the applicable exception"
```

Current facts zostanú v RAG. Model sa učí behavior: evidence-first, conflict handling a abstention.

## 14. Preprocessing a chat template

Raw records sa serializujú tokenizerom a chat template base modelu. Role mapping, special tokens, truncation, maximum sequence length a loss masking menia training subject.

Ak sa loss počíta aj nad user textom alebo hidden metadata, model sa môže učiť neželané copying. Long examples môžu byť orezané tak, že target stratí prerequisite. Preprocessing reportuje truncated examples a token distributions.

```yaml
preprocessing_report:
  records_input: 12400
  records_output: 11982
  duplicates_removed: 271
  invalid_schema: 43
  truncated_inputs: 96
  truncated_targets: 0
  maximum_tokens: 8192
```

## 15. Full fine-tuning a parameter-efficient methods

Full fine-tuning aktualizuje veľkú časť alebo všetky model parameters. Parameter-efficient fine-tuning, napríklad adapters alebo LoRA, trénuje menší počet parameters a zachová base artifact oddelene.

PEFT znižuje training memory a storage, ale stále vytvára behavior release viazaný na presný base model a adapter. Adapter z jedného snapshotu nemusí byť compatible s iným base modelom, aj keď family name ostáva rovnaký.

```yaml
adapter_release:
  base_model_digest: sha256:aa91...
  method: lora
  adapter_digest: sha256:8f10...
  target_modules: [q_proj, v_proj]
  rank: 16
  alpha: 32
```

Serving musí read-backnúť base aj adapter identity.

## 16. Hyperparameters

Epochs, learning rate, batch size, sequence length, optimizer, warmup, weight decay a preference-specific coefficients ovplyvňujú výsledok. Viac epochs nie je automaticky lepšie. Malý dataset sa môže rýchlo overfitnúť alebo zhoršiť general behavior.

Training metrics ako loss ukazujú optimization, nie application correctness. Validation loss môže klesať, zatiaľ čo refusal, tool use alebo factuality regressujú. Hyperparameter selection sa viaže na task eval a safety gates.

## 17. Train/validation/test split

Split sa robí podľa intended generalization unit. Random message split môže preniesť rovnakého customer case, template alebo policy passage do train aj testu. Vhodnejší môže byť case-level, source-level alebo temporal split.

Preference pairs z rovnakého prompt family sa držia v jednom splite. Test set zostáva mimo prompt iteration aj hyperparameter tuning. Incident regressions môžu byť permanentný gate, ale potrebný je aj fresh holdout.

## 18. Baseline

Candidate sa porovnáva s base modelom plus najlepším rozumným prompt/RAG configuration. Slabý baseline vytvára falošný training gain.

```text
base model + current prompt/RAG
versus
fine-tuned model + compatible prompt/RAG
```

Fine-tuned model môže potrebovať jednoduchší prompt, ale comparison musí zachovať rovnaký business contract. Cost a latency sa merajú spolu s quality; kratší prompt môže byť legitímny benefit.

## 19. Evaluation

Eval pokrýva target behavior aj adjacent capabilities. SFT na classification môže zlepšiť accuracy a zároveň zhoršiť multilingual alebo refusal behavior. Preference tuning môže zlepšiť human style preference, ale znížiť concise structured output.

```yaml
eval_segments:
  - target_task
  - unseen_templates
  - policy_updates
  - insufficient_evidence
  - unauthorized_actions
  - multilingual
  - adversarial_instructions
  - long_context
  - tool_schema
```

Per-segment forbidden failures blokujú promotion aj pri lepšom average score.

## 20. Memorization a privacy testing

Fine-tuned model sa testuje na canary strings, personal identifiers a prompt extraction. Exact training-example replay a membership inference risk sa posudzujú podľa sensitivity a platform controls.

Dataset minimalization znižuje riziko. Nie je potrebné trénovať na full transcript, ak target je iba classification label. Secrets a access tokens nesmú vstúpiť do training pipeline ani logs.

## 21. Catastrophic forgetting a regressions

Fine-tuning môže zhoršiť capabilities mimo target domain alebo prehnane fixovať response style. Mieru zmeny ovplyvňuje dataset size, diversity, learning rate a method.

Regression suite zahŕňa base-model capabilities relevantné pre application. Pri adapteroch možno rollbacknúť adapter, no ak sa súčasne zmenil prompt alebo RAG release, návrat iba na base model nie je celý rollback.

## 22. Knowledge injection versus behavior tuning

Fine-tuning môže zvýšiť pravdepodobnosť reprodukcie domain facts, ale neposkytuje explicitnú freshness, source provenance ani delete semantics. Nie je vhodný ako jediný knowledge store pre mutable policies.

```text
behavior: "odpovedz iba z current evidence" → fine-tuning candidate
fact: "policy RF-EU-042 v7 platí od 1. júla" → RAG/source registry
```

Ak source musí byť odstránený alebo opravený, retrieval index sa dá cielene aktualizovať. Odstránenie memorized factu z weights je podstatne ťažšie overiť.

## 23. Fine-tuning a RAG

Tieto techniky sa môžu dopĺňať. Fine-tuned model sa učí query decomposition, evidence-first answer format, citations a abstention; RAG poskytuje current facts. Training dataset však musí používať synthetic alebo versioned evidence blocks, aby model nepreferoval zapamätaný answer pred contextom.

Counterfactual eval vloží nový alebo protichodný evidence a overí, či model nasleduje authorized current source. Ak fine-tuned model odpovedá podľa training memory napriek contextu, release neprejde.

## 24. Tool a schema tuning

SFT môže zlepšiť výber toolu a argument format, ale model proposal stále nie je authorization. Training examples nesmú obsahovať falošný pattern, že assistant text znamená vykonaný side effect.

Tool dataset zahŕňa refusal, missing arguments, read-before-write, unknown outcome a no-tool cases. Schema conformance sa overuje deterministic validatorom aj po fine-tuningu.

## 25. Training pipeline

Controlled lifecycle:

```text
use-case a baseline
→ data contract a governance
→ dataset build
→ preprocessing report
→ training candidate
→ offline eval
→ safety/privacy eval
→ shadow
→ bounded canary
→ outcome observation
→ promotion alebo rollback
```

Training job success iba dokazuje, že platforma vytvorila artifact. Neurčuje, či artifact zlepšil workload alebo je bezpečný.

## 26. Registry a lineage

Model registry ukladá base model, training job, datasets, code/environment, hyperparameters, checkpoints, metrics, eval verdict, owner, lifecycle a deployment aliases.

```yaml
registry_entry:
  model_release: support-sft-v4
  lineage:
    base_model: support-base-2026-07-28
    training_job: ftjob-8421
    dataset: support-demonstrations-2026-08-04
    code: git:91ae230
  status: candidate
  eval_verdict: passed-offline
  production_state: not-promoted
```

`completed` training status sa nesmie zameniť s production promotion.

## 27. Deployment a compatibility

Fine-tuned model môže podporovať odlišný context, structured-output alebo tool feature set podľa provider/platformy. Application compatibility sa znovu testuje. Prompt a decoding configuration sa pinujú spolu s modelom.

Canary assignment je stabilný podľa tenant/user/case. Shadow traffic nesmie vykonávať write tools. Outcome delay sa rešpektuje pred promotion; okamžitý schema pass nepreukazuje ticket resolution.

## 28. Observability

Runtime trace loguje model release, base/adapter identity ak dostupná, prompt, RAG generation, route, usage, latency, validation, refusal, tool proposal a business outcome. Metrics sa porovnávajú s baseline per segment.

Training observability zahŕňa data counts, token distributions, loss, checkpoints, gradient/optimization health a cost. Tieto metrics diagnostikujú training, ale production verdict pochádza z eval a journey telemetry.

## 29. Failure hypotheses

Pri candidate regressione sa skúma dataset bias, stale labels, leakage, preprocessing/truncation, wrong chat template, aggressive hyperparameters, overfitting, preference inconsistency, grader exploit, base-model mismatch a serving compatibility.

Pri nezmenenom outcome sa overí, či bottleneck vôbec leží v model behavior. Ak retrieval stále nevracia current policy, fine-tuning nemá čo opraviť. First-divergence analysis sa vykoná pred ďalším training runom.

## 30. Containment a recovery

Containment vypne candidate route, vráti known-good full release a zachová failing requests a model/dataset manifests. Pri privacy alebo memorization incidente sa zastaví serving aj ďalšie používanie training artefacts podľa incident policy.

Recovery môže opraviť dataset a znovu trénovať, znížiť update magnitude, zmeniť method alebo opustiť fine-tuning v prospech prompt/RAG fixu. Každý nový candidate prejde baseline replay, fresh holdout, safety/privacy a bounded canary. Druhá operácia testuje odlišný segment, nie iba pôvodný incident prompt.

## 31. Acceptance

Pozitívna acceptance vyžaduje správny use-case boundary, authoritative a governed data, reproducible training subject, leakage-safe split, strong baseline, target aj adjacent evals, privacy/safety gates, full release lineage, controlled rollout a business outcome measurement.

Recovery acceptance vyžaduje identifikovaný failure stage, known-good rollback, zachované training a runtime evidence, opravený dataset/method alebo application-layer fix, fresh holdout a druhý odlišný production journey.

Forbidden acceptance je fine-tuning ako náhrada current knowledge alebo authorization, closed tickets ako implicitný ground truth, training loss ako production verdict, provider job completion ako promotion, preference pair ako absolútna truth alebo ďalší training run bez first-divergence diagnosis.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: RAG evaluation a retrieval diagnostics](rag-evaluation-retrieval-diagnostics.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
