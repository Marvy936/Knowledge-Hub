# Knowledge Hub RAG clean-checkout runtime gate

Tento gate skladá existujúce LLM/RAG Practical v1 CLIs do jedného exact-revision lifecycle. Nevytvára nový retriever, nový answer adapter ani druhú eval implementáciu.

Authoritative driver:

```text
labs/llm-rag/scripts/run_clean_checkout_runtime.py
```

Dedicated hosted workflow:

```text
.github/workflows/rag-clean-checkout-runtime.yml
```

## Lifecycle

Gate používa presne existujúce vrstvy:

```text
exact Git revision
→ build_corpus.py
→ build_index.py
→ build_runtime_config.py
→ positive query
→ explicit no-result query
→ run_evaluation.py
→ build_prompt_release.py
→ cleanup_runtime.py
```

Všetky runtime artifacts vznikajú pod:

```text
.runtime/llm-rag
```

Canonical evidence JSON je mimo disposable runtime rootu.

## Exact corpus subject

`build_corpus.py` dostane exact 40-character Git SHA. Driver potom vyžaduje:

- `manifest.source_revision == checked-out HEAD`,
- canonical `snapshot_id`,
- minimálne jeden canonical `chunk_id`,
- exact Git checkout bez tracked modifikácií pred runtime.

Pozitívny query sa nehardcoduje podľa konkrétnej dnešnej kapitoly. Odvodí sa z reálneho freshly built chunku, takže content edit nemení runtime harness na stale fixture.

## Index a runtime config

Index musí obsahovať canonical `index_id` a exact corpus `snapshot_id`.

Runtime config musí obsahovať canonical `runtime_config_id` a pinovať exact implementation revision.

Tieto identity sú samostatné:

```text
corpus snapshot
≠ retrieval index
≠ runtime/config generation
```

## Positive retrieval

Derived query musí skončiť:

```text
status=answered
```

Driver vyžaduje:

- non-empty answer,
- canonical `answer_id`,
- canonical `trace_id`,
- minimálne jednu citation,
- každý cited `chunk_id` musí patriť do exact freshly built corpus manifestu.

Citation text alebo path bez exact chunk identity nestačí.

## Explicit no-result/abstention

Druhý query je zámerne nonsensical subject, ktorý v Knowledge Hub corpuse nemá existovať.

Výsledok musí byť explicitne:

```text
no_result
```

alebo bounded:

```text
abstained
```

Gate nesmie reinterpretovať chýbajúci retrieval result ako answered response.

No-result path stále musí mať trace identity podľa authoritative query contractu.

## Hard evaluation

`run_evaluation.py` používa repository eval dataset a exact:

- corpus manifest,
- index,
- runtime config.

Runtime evidence vyžaduje:

```text
all_passed=true
failed_count=0
```

A musí explicitne obsahovať oba bezpečnostné slices:

```text
direct_prompt_injection
retrieved_context_prompt_injection
```

Aggregate score preto nemôže zakryť zlyhanie hard security slice-u.

## Prompt/config release

`build_prompt_release.py` môže vzniknúť až po úspešnom eval reporte.

Release musí pinovať exact upstream identities:

```text
snapshot_id
index_id
runtime_config_id
report_id
```

Implementation revision je transitívne immutable cez exact runtime-config subject. Runtime evidence nemá znovu resolvovať branch name alebo mutable config alias.

## Artifact evidence

Driver pre každý intermediate JSON zaznamenáva:

- SHA-256,
- byte size.

Canonical lifecycle evidence navyše pinne:

- Git SHA,
- snapshot ID,
- chunk count,
- index ID,
- runtime-config ID,
- positive answer ID a trace ID,
- exact cited chunk IDs,
- no-result status a trace ID,
- eval report ID,
- required injection slices,
- prompt release ID,
- cleanup result,
- canonical evidence ID.

## Cleanup

`cleanup_runtime.py` sa volá z `finally` boundary, nie iba po happy path.

Po cleanup-e musí platiť:

```text
.runtime/llm-rag neexistuje
```

Dedicated workflow to overí ešte raz pred artifact uploadom a má samostatný `always()` emergency cleanup pre runtime root a virtual environment.

Zelený query/eval bez cleanup read-backu nie je completed Practical v1 runtime evidence.

## Proof boundary

Successful exact-revision run preukáže bounded offline Practical v1 lifecycle:

```text
Git corpus bytes
→ deterministic chunk/index identities
→ deterministic lexical retrieval
→ grounded bounded answer + exact citations
→ explicit no-result
→ hard eval/security slices
→ prompt/config release provenance
→ trace identities
→ cleanup
```

Nepreukáže:

- semantic embedding provider,
- vector database,
- reranker model provider,
- generative external LLM,
- paid API,
- GPU serving,
- production latency/SLO,
- production data boundary,
- user acceptance.

Practical v1 core adapter je zámerne deterministic a credential-free. Voliteľný semantic/generative adapter je post-v1 alebo samostatný provider-specific evidence layer.

Kým `.github/workflows/rag-clean-checkout-runtime.yml` nevytvorí successful authoritative run, tento gate je `Implemented`, nie `Runtime verified`.
