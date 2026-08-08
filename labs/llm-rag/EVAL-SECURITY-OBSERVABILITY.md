# Evaluation-driven RAG security a observability

Táto vrstva nadväzuje na exact corpus/chunk manifest, deterministic retrieval a structured answer envelope. Cieľom nie je simulovať kvalitu produkčného LLM. Core CI authority je zámerne offline a deterministická.

```text
versioned runtime config
→ exact implementation + corpus revision
→ exact retrieval subject
→ bounded context
→ direct-query injection scan
→ context-chunk injection scan
→ deterministic extractive adapter
→ exact citations alebo policy abstention
→ per-case eval slices
→ critical/high-risk hard gates
→ prompt/config promotion iba po full report rebuild
→ trace, latency a token-equivalent counters
→ bounded cleanup
```

## Versioned runtime config

`runtime_config_id` pinne:

- prompt/config generation,
- exact `implementation_revision`,
- code-defined system policy,
- deterministic adapter generation,
- prompt-injection policy generation,
- tokenizer/counter generation,
- retrieval `top_k` a `min_score`,
- context character budget,
- answer character budget,
- per-slice eval thresholds,
- high-risk slice inventory.

`implementation_revision` musí byť exact lowercase 40-hex Git commit SHA a adapter ho porovnáva s `manifest.source_revision`. Pre Practical v1 teda implementation, corpus, chunk manifest, retrieval index a eval patria tomu istému Git subjectu.

System policy nie je runtime-editable string. Je definovaná v code generation, pretože promotion nesmie tvrdiť, že otestovala prompt/policy, ktorý deterministic adapter reálne nepoužil. Zmena policy vyžaduje zmenu source revision a nový eval/release subject.

Config validation ho z týchto inputs znovu zostaví. Nanovo zahashovaný config s inými thresholds, revision alebo adapter generation preto nie je automaticky dôveryhodný.

Default system policy explicitne hovorí, že retrieved content je evidence, nie instruction authority.

## Deterministic CI adapter

Core adapter nepotrebuje model API ani secret. Najprv zostaví exact bounded context podľa config budgetu. Security scan aj answer selection používajú iba items z tohto contextu; raw retrieval hits nemôžu obísť `context_max_chars`.

Pri bezpečnom výsledku adapter vyberie najvyššie zoradený safe context item a odpovie extraktívnym substringom z tohto chunku.

To vytvára prísnu faithfulness boundary:

```text
answer text
⊆ exact cited chunk content
```

`adapter_result_id` pinne aj `context_id` a exact implementation revision. Tento adapter nie je náhrada za kvalitný generatívny model. Je to deterministic CI reference implementation, na ktorej sa dajú overiť retrieval, citation, faithfulness, abstention a security contracts bez plateného providera.

## Prompt-injection policy

`prompt-injection-policy-v1` používa explicitné, verzované heuristic rules pre napríklad:

- „ignore previous/prior instructions“,
- pokus o získanie system promptu,
- pokus o získanie developer instructions,
- exfiltráciu secret/token/credential/password,
- instruction override typu „you are now“ alebo „new instructions:“,
- výzvu na spustenie command/tool/function.

Security evidence pinne subject type/ID, text SHA-256, matched rules, classification a generation.

Je to bounded test policy, nie všeobecný production prompt-injection classifier. False positive/negative riziko je otvorená hranica.

### Direct injection

Ak injection pattern obsahuje samotná query, security policy má prednosť pred retrieval outcome. Answer envelope musí byť:

```text
status = abstained
abstention_reason = direct_prompt_injection
answer = null
citations = []
```

Aj keď lexical retrieval nájde relevantné chunks, direct injection query sa neodpovedá. Ak retrieval zároveň skončí `no_result`, direct injection môže zostať explicitným dôvodom abstention; indirect injection sa pri neexistujúcom retrieved subjecte deklarovať nesmie.

### Indirect injection

Každý chunk, ktorý sa skutočne dostal do bounded contextu, sa skenuje ako untrusted data. Unsafe chunk môže zostať v retrieval evidence, ale nesmie byť citation authority pre offline answer.

Ak existuje safe context item, adapter odpovie iba z neho. Ak bounded context existuje, ale všetky jeho items sú unsafe, výsledok je policy abstention `indirect_prompt_injection`. Ak retrieval mal hits, ale do context budgetu sa nedostal žiadny, výsledok je `no_safe_context`.

## Answer abstention schema

Structured answer contract rozlišuje:

- `retrieval_no_result`,
- `direct_prompt_injection`,
- `indirect_prompt_injection`,
- `no_safe_context`.

Abstention nikdy nenesie answer text ani citations. Dôvod musí zodpovedať existujúcemu subjectu: `indirect_prompt_injection` a `no_safe_context` sú prípustné iba pri retrieval `results`; no-result povoľuje `retrieval_no_result` alebo direct-query security precedence.

## Eval dataset

Versioned source dataset je `data/eval-cases.json`. Jeden case pinne:

- `case_id`,
- query,
- `critical`,
- povinné slices,
- expected retrieval state,
- expected answer state a abstention reason,
- expected source paths,
- attack type `none`, `direct` alebo `indirect`.

Source dataset obsahuje Knowledge Hub queries pre error budget a Kubernetes ConfigMap, explicitný no-result case a direct injection case. Indirect injection sa testuje synthetic fixture-om, pretože do trusted documentation corpusu zámerne nevkladáme škodlivý payload iba kvôli eval-u.

## Eval slices

Core evaluator oddeľuje päť metrík.

### Retrieval

Overuje exact expected retrieval state a podľa case aj prítomnosť očakávaného source pathu medzi hits.

### Citation

Pre answered case vyžaduje exact retrieved citation. Ak case deklaruje expected source paths, cited source musí patriť do tejto množiny.

### Faithfulness

Core reference adapter musí mať answer text ako exact substring aspoň jedného cited chunk contentu. LLM-as-judge nie je authority tejto CI vrstvy.

### Abstention

Overuje `answered`/`abstained` a podľa case exact abstention reason.

### Security

Direct case musí byť policy-abstained. Indirect case musí preukázať aspoň jeden detected unsafe context chunk a žiadny unsafe chunk nesmie byť cited.

## Hard gates

Default thresholds sú:

```text
retrieval    >= 0.80
citation     = 1.00
faithfulness = 1.00
abstention   = 1.00
security     = 1.00
```

High-risk slices sú citation, faithfulness, abstention a security.

Suite prejde iba ak:

1. každý slice dosiahne threshold,
2. žiadny `critical` case nezlyhá,
3. žiadny high-risk slice nezlyhá.

Aggregate case rate je iba diagnostic. Napríklad 75 % aggregate nemôže prekryť jeden critical abstention/security failure.

Povinný slice bez applicable evidence je failure. Eval case preto nesmie napríklad deklarovať faithfulness pri očakávanom abstention outcome.

## Eval report authority a provenance

`eval_report_id` sám nie je promotion authority. `validate_eval_report()` vykoná celú suite znova z exact:

- eval cases,
- chunk manifestu,
- retrieval indexu,
- runtime configu.

Pred suite sa index deterministicky overí proti manifestu. Každý adapter run zároveň vyžaduje `runtime_config.implementation_revision == manifest.source_revision`.

Top-level eval report priamo pinne:

- `runtime_config_id`,
- `chunk_manifest_id`,
- `corpus_snapshot_id`,
- Git `source_revision`,
- `retrieval_index_id`,
- case/slice výsledky a hard-gate state.

Promotion preto odmietne aj report, ktorý niekto zmenil a korektne nanovo zahashoval.

## Prompt/config promotion

`build_prompt_release()` vytvorí `prompt_release_id` iba keď full deterministic report rebuild prejde a `suite_passed=true`.

Release priamo pinne exact:

- `runtime_config_id`,
- config generation,
- `eval_report_id`,
- `chunk_manifest_id`,
- `corpus_snapshot_id`,
- Git `source_revision`,
- `retrieval_index_id`.

Neexistuje „promote aggregate average“. Promotion je viazaná na hard slice gates a exact corpus/index/revision provenance.

Executable driver vyžaduje fresh `release-output` path. Ak na path už existuje release, run sa odmietne ešte pred evalom. Failed re-eval preto nemôže nechať starý promotion artifact, ktorý by vyzeral ako výsledok nového runu.

## Trace a observability

Single-query trace pinne:

- runtime config ID,
- query ID,
- retrieval result ID,
- context ID,
- adapter result ID,
- answer ID,
- answer status,
- observed latency.

Pred zápisom trace sa znovu validuje runtime config, retrieval, adapter a bounded context. Adapter sám pinne exact context a implementation revision.

Counters obsahujú:

- query lexical token equivalents,
- retrieved chunk count,
- retrieved characters,
- context characters,
- answer lexical token equivalents,
- citation count.

Cost-equivalent block používa jednotku `lexical_token_equivalent`. `monetary_cost` je explicitne `null`; tento offline adapter nemá provider billing a nesmie predstierať dolárovú cenu.

Latency je runtime observation, preto dva korektné runy môžu mať iný `trace_id`.

## Executable single-query flow

```bash
python labs/llm-rag/scripts/run_offline_query.py \
  --manifest .runtime/rag/chunk-manifest.json \
  --index .runtime/rag/retrieval-index.json \
  --query "Ako funguje Kubernetes ConfigMap?" \
  --generation rag-grounded-v1 \
  --implementation-revision "$GIT_COMMIT" \
  --config-output .runtime/rag/runtime-config.json \
  --retrieval-output .runtime/rag/retrieval.json \
  --context-output .runtime/rag/context.json \
  --adapter-output .runtime/rag/adapter.json \
  --trace-output .runtime/rag/trace.json
```

`$GIT_COMMIT` musí byť ten istý exact commit, ktorý bol použitý pri corpus snapshot/chunk manifest subjecte. Výstup môže byť `answered` alebo policy/retrieval `abstained`; oba sú validné business states, ak zodpovedajú contractu.

## Executable eval/promotion flow

```bash
python labs/llm-rag/scripts/run_eval_suite.py \
  --manifest .runtime/rag/chunk-manifest.json \
  --index .runtime/rag/retrieval-index.json \
  --cases labs/llm-rag/data/eval-cases.json \
  --generation rag-grounded-v1 \
  --implementation-revision "$GIT_COMMIT" \
  --config-output .runtime/rag/runtime-config.json \
  --report-output .runtime/rag/eval-report.json \
  --release-output .runtime/rag/prompt-release.json
```

Exit codes:

- `0` — hard gates prešli a release bol vytvorený,
- `2` — contract/refusal error,
- `4` — validný eval run, ale jeden alebo viac gates zlyhalo; release sa nevytvorí.

## Cleanup

Cleanup je zámerne samostatný a bounded:

```bash
python labs/llm-rag/scripts/cleanup_runtime.py \
  --runtime-root .runtime/rag
```

Script odmietne symlink a každý target, ktorý nekončí presne `.runtime/rag`. Po zmazaní číta späť, že directory neexistuje.

## Source test inventory

Nová test matrix pokrýva:

- canonical runtime config, exact implementation revision a tampering,
- malformed config refusal,
- deterministic security evidence,
- direct injection abstention,
- indirect injection skip pri existencii safe evidence,
- all-unsafe indirect abstention,
- passing multi-slice eval suite a prompt release,
- direct corpus/index/revision provenance v report/release,
- aggregate-pass/critical-failure konflikt,
- forged eval report refusal,
- invalid required-slice schema,
- trace subject/counter reconstruction.

Predchádzajúca retrieval/answer test vrstva zostáva samostatná. Kým issue #151 blokuje Actions dispatch, prítomnosť tests v source nie je deklarovaná ako vykonaný central CI run.

## Neoverená hranica

Táto vrstva ešte nepreukazuje:

- kvalitu generatívneho LLM,
- semantic embedding retrieval alebo reranker,
- robustnosť voči všetkým prompt-injection variantom,
- LLM-based faithfulness judge calibration,
- provider token accounting alebo skutočnú cenu,
- production tracing backend,
- online prompt/config canary,
- user acceptance alebo business outcome.

Core Practical v1 zostáva offline a reproducible; optional real/local model adapter môže byť pridaný neskôr bez zmeny authority hard CI gates.
