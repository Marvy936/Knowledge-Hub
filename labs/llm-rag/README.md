# Knowledge Hub LLM/RAG flagship

Tento package je praktický flagship pre sekciu 20. Implementované sú authoritative corpus identity, deterministic Markdown chunking, offline lexical retrieval, explicitný `no_result`, exact citations, structured answer/abstention, versioned runtime config, deterministic extractive CI adapter, evaluation-driven promotion, prompt-injection policy gates a bounded trace/cost-equivalent evidence.

Core cesta zostáva offline a bez API keya. Generatívny alebo lokálny model môže byť neskôr pridaný ako voliteľný adapter, ale nemení authority deterministických CI gates.

## Aktuálny lifecycle

```text
exact Git commit
→ immutable corpus snapshot
→ deterministic Markdown chunks
→ exact chunk manifest
→ deterministic lexical index
→ canonical query identity
→ BM25-v1 retrieval
→ results / no_result
→ direct-query a retrieved-chunk security scan
→ safe-context selection
→ deterministic extractive answer alebo exact abstention
→ exact citations
→ per-slice evaluation
→ critical/high-risk hard gates
→ runtime-config promotion
→ trace + latency + token-equivalent counters
→ bounded cleanup
```

Podrobné contracts:

- [`RETRIEVAL-GROUNDED-ANSWER.md`](RETRIEVAL-GROUNDED-ANSWER.md)
- [`EVAL-SECURITY-OBSERVABILITY.md`](EVAL-SECURITY-OBSERVABILITY.md)
- runtime evidence: [`RUNTIME-EVIDENCE.md`](RUNTIME-EVIDENCE.md)

## Corpus a chunk identity

Snapshot nepoužíva mtime, absolute workspace path ani wall-clock timestamp. Rovnaké bytes, relatívne cesty, include roots a source revision vytvoria rovnaký `corpus_snapshot_id` aj v inom checkout adresári.

Chunk identity zahŕňa source path, source SHA-256, heading path, ordinal, content SHA-256 a character count. `chunk_manifest_id` fingerprintuje celý ordered manifest vrátane chunk textu a chunking configuration.

Snapshot a chunk manifest sa nevalidujú iba hashom. Source bytes sa čítajú späť a chunk manifest sa deterministicky rebuildne z exact snapshot subjectu.

## Retrieval a citations

Retrieval index pinne exact `chunk_manifest_id`, source revision, tokenizer generation a lexical statistics. Query pinne index, normalized tokens a retrieval parametre. Result validator retrieval vykoná znova; rehashed result s odstráneným alebo modifikovaným hitom neprejde.

Core retrieval používa:

```text
algorithm = bm25-v1
tokenizer = unicode-word-v1
k1 = 1.2
b = 0.75
```

Každý hit nesie exact:

- `chunk_id`,
- `source_path`,
- source file SHA-256,
- heading path,
- content SHA-256,
- canonical citation ID.

Ak žiadny chunk neprekročí score gate, stav je explicitný `no_result`.

## Versioned runtime config

`runtime_config_id` pinne prompt/config generation, system policy, adapter/security/token-counter generations, retrieval parametre, context/answer budget a eval thresholds.

Default system policy považuje retrieved text výhradne za evidence. Retrieved text nemá instruction authority.

Config sa validuje deterministic rebuildom. Zmena thresholdov, generation alebo policy vytvorí iný subject.

## Deterministic offline adapter

Reference adapter je zámerne extraktívny. Pri bezpečnom retrieval výsledku odpovie substringom z exact cited chunku. To umožňuje deterministic faithfulness gate bez LLM judge-a.

Ak query obsahuje direct prompt-injection pattern, výsledok je `direct_prompt_injection` abstention. Retrieved chunks sa skenujú oddelene. Unsafe chunk sa nesmie stať citation authority; ak neexistuje safe evidence, výsledok je `indirect_prompt_injection` abstention.

Security scanner je explicitný heuristic policy `prompt-injection-policy-v1`, nie všeobecný production classifier.

## Structured answer states

Povolené sú answered alebo explicitne abstained výsledky.

Retrieval abstention:

```text
status = abstained
answer = null
abstention_reason = retrieval_no_result
citations = []
```

Security abstention môže používať:

- `direct_prompt_injection`,
- `indirect_prompt_injection`,
- `no_safe_context`.

Policy abstention nikdy nenesie answer text ani citations.

## Evaluation-driven promotion

Versioned dataset `data/eval-cases.json` obsahuje retrieval, citation, faithfulness, abstention a direct-security cases. Indirect injection sa testuje synthetic fixture-om, aby sa škodlivý prompt nemusel commitovať do trusted documentation corpusu.

Default gates:

```text
retrieval    >= 0.80
citation     = 1.00
faithfulness = 1.00
abstention   = 1.00
security     = 1.00
```

Citation, faithfulness, abstention a security sú high-risk slices.

Suite prejde iba keď každý slice dosiahne threshold, žiadny critical case nezlyhá a žiadny high-risk slice nezlyhá. Aggregate case rate je diagnostika, nie promotion authority.

`eval_report_id` sám nestačí. Pred promotion sa report celý znovu vykoná z exact cases, manifestu, indexu a runtime configu. Až potom môže vzniknúť `prompt_release_id`.

## Observability

Single-query trace pinne config, query, retrieval, context, adapter a answer IDs plus observed latency.

Counters obsahujú query/retrieved/answer lexical token equivalents, retrieved chunk count, retrieved/context chars a citation count. `monetary_cost` je `null`, pretože offline adapter nemá provider billing a nesmie predstierať finančnú cenu.

Trace pred zápisom znovu validuje config, retrieval, adapter a context.

## CLI pre corpus a retrieval

```bash
python -m knowledge_hub_rag snapshot \
  --repo-root . \
  --source-revision "$GIT_COMMIT" \
  --output .runtime/rag/corpus-snapshot.json

python -m knowledge_hub_rag chunk \
  --repo-root . \
  --snapshot .runtime/rag/corpus-snapshot.json \
  --output .runtime/rag/chunk-manifest.json

python -m knowledge_hub_rag index \
  --manifest .runtime/rag/chunk-manifest.json \
  --output .runtime/rag/retrieval-index.json

python -m knowledge_hub_rag retrieve \
  --manifest .runtime/rag/chunk-manifest.json \
  --index .runtime/rag/retrieval-index.json \
  --query "Ako funguje Kubernetes Service?" \
  --output .runtime/rag/retrieval.json \
  --context-output .runtime/rag/context.json
```

## Offline query evidence

```bash
python labs/llm-rag/scripts/run_offline_query.py \
  --manifest .runtime/rag/chunk-manifest.json \
  --index .runtime/rag/retrieval-index.json \
  --query "Ako funguje Kubernetes ConfigMap?" \
  --generation rag-grounded-v1 \
  --config-output .runtime/rag/runtime-config.json \
  --retrieval-output .runtime/rag/retrieval.json \
  --context-output .runtime/rag/context.json \
  --adapter-output .runtime/rag/adapter.json \
  --trace-output .runtime/rag/trace.json
```

## Eval a promotion

```bash
python labs/llm-rag/scripts/run_eval_suite.py \
  --manifest .runtime/rag/chunk-manifest.json \
  --index .runtime/rag/retrieval-index.json \
  --cases labs/llm-rag/data/eval-cases.json \
  --generation rag-grounded-v1 \
  --config-output .runtime/rag/runtime-config.json \
  --report-output .runtime/rag/eval-report.json \
  --release-output .runtime/rag/prompt-release.json
```

Eval driver vracia `4`, ak run je contract-validný, ale hard gate zlyhal. Release vtedy nevznikne.

## Cleanup

```bash
python labs/llm-rag/scripts/cleanup_runtime.py --runtime-root .runtime/rag
```

Cleanup driver smie odstrániť iba target končiaci `.runtime/rag`, odmieta symlink a číta späť, že directory neexistuje.

## Trust boundary

Zakázané alebo odmietané sú najmä:

- symlinked corpus subjects,
- include root mimo repository rootu,
- non-Markdown alebo non-UTF-8 corpus,
- changed snapshot bytes,
- rehashed alebo incomplete chunk manifest,
- rehashed retrieval result odlišný od deterministic query rebuild-u,
- citation, ktorá nebola exact retrieved hitom,
- answer bez citation pri answered stave,
- guessed answer pri `no_result`,
- direct injection answer,
- citation unsafe retrieved chunku,
- eval promotion podľa aggregate priemeru pri critical/high-risk failure,
- forged eval report bez deterministic rebuild-u,
- trace nad iným context/adapter subjectom,
- broad alebo symlinked cleanup target.

## Source test inventory a runtime boundary

Corpus/chunk layer, retrieval/answer layer a eval/security/observability layer majú samostatné source tests. Nová eval/security test matrix obsahuje 10 test functions pre config, security, direct/indirect injection, all-unsafe abstention, hard eval gates, forged report refusal, invalid slice schema a trace evidence.

Kým issue #151 blokuje GitHub Actions dispatch, tieto source tests sa neprezentujú ako central runtime verification. `RUNTIME-EVIDENCE.md` zostáva `Pending`.

Táto vrstva stále nepreukazuje:

- kvalitu generatívneho LLM,
- semantic embeddings alebo learned reranker,
- robustnosť voči všetkým injection variantom,
- production tracing backend,
- provider billing,
- online prompt canary,
- user acceptance alebo business outcome.

## Ďalší blok

LLM/RAG source lifecycle pre Practical v1 je po tejto vrstve funkčne uzavretý na offline deterministic úrovni. Ďalší major track je Keycloak-secured AI API; LLM/RAG runtime closeout zostáva paralelne blokovaný issue #151.
