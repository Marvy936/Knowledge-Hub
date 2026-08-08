# Retrieval, citations a structured grounded-answer contract

Táto vrstva nadväzuje na exact corpus snapshot a deterministic chunk manifest. Core path zostáva úplne offline: nevytvára embeddings, nevolá LLM provider a nepotrebuje API key.

```text
exact chunk manifest
→ deterministic lexical index
→ canonical query identity
→ BM25-v1 retrieval
→ results / no_result
→ exact chunk citations
→ bounded grounded context
→ structured answer alebo exact abstention
```

## Retrieval index authority

Index je odvodený iba z authoritative chunk manifestu. Pinne:

- `chunk_manifest_id`,
- `corpus_snapshot_id`,
- exact Git `source_revision`,
- tokenizer generation `unicode-word-v1`,
- počet dokumentov a priemernú token length,
- per-term document frequency,
- per-chunk term frequencies,
- exact chunk/source/content identities.

`retrieval_index_id` je canonical SHA-256 celého index payloadu. Hash však nie je jediný proof boundary. `validate_retrieval_index()` celý index deterministicky znovu zostaví z chunk manifestu a vyžaduje exact equality. Rehashed index s vynechaným dokumentom, zmeneným DF alebo inou metadata preto neprejde.

Tokenizácia používa Unicode NFKC normalization, `casefold()` a explicitnú `unicode-word-v1` generation. Stop-word list, stemming ani skrytý locale-dependent tokenizer sa nepoužívajú.

## Query identity

Každá query pinne:

- pôvodný query string,
- normalizovaný token string,
- ordered query tokens,
- exact `retrieval_index_id`,
- `top_k`,
- `min_score`.

Z toho vznikne `query_id`. Zmena indexu alebo retrieval parametrov preto vytvorí nový query subject aj pri rovnakom textovom dopyte.

## BM25-v1 retrieval

Offline retriever používa bounded BM25 variant s explicitnými parametrami:

```text
k1 = 1.2
b  = 0.75
```

Výsledky sú zoradené podľa:

1. score zostupne,
2. `chunk_id` vzostupne ako deterministic tie-breaker.

Do resultu sa dostanú iba dokumenty s pozitívnym score, ktoré dosiahli `min_score`. Ak neprejde žiadny dokument, stav je explicitne:

```json
{
  "status": "no_result",
  "hit_count": 0,
  "hits": []
}
```

`no_result` sa nesmie premeniť na guessed answer.

## Citation identity

Jeden retrieval hit nesie exact citation object:

- `chunk_id`,
- `source_path`,
- source file SHA-256,
- heading path,
- chunk content SHA-256,
- canonical `citation_id`.

Citation nie je iba display path. Je viazaná na konkrétnu verziu source bytes a konkrétny chunk subject.

Retrieval result zároveň nesie chunk content pre bounded context assembly. `retrieval_result_id` fingerprintuje query, index subject, retrieval config, hit ordering, citations aj returned content.

## Semantic result validation

`validate_retrieval_result()` neverí iba `retrieval_result_id`. Z resultu zoberie query/config, vykoná retrieval znova nad exact indexom a chunk manifestom a vyžaduje exact equality.

To odmieta napríklad tento útok:

```text
valid result
→ odstránenie top hitu
→ prepočet retrieval_result_id
→ validator vykoná query znovu
→ exact result sa nezhoduje
→ refusal
```

## Bounded grounded context

`build_grounded_context()` pridáva retrieved chunks v rank order iba pokiaľ sa zmestia do explicitného `max_chars` budgetu.

Stavy sú:

- `context` — aspoň jeden retrieved chunk sa zmestil,
- `insufficient_context` — retrieval mal výsledky, ale žiadny sa nezmestil do budgetu,
- `no_result` — retrieval nemal žiadny výsledok.

Context nepridáva externé fakty ani neprepisuje citation metadata.

## Structured answer envelope

Core package ešte negeneruje natural-language answer. Prijme text od budúceho deterministic/local/real model adaptera a vytvorí iba validated envelope.

Pre answered variant musí platiť:

- retrieval status je `results`,
- answer text je neprázdny,
- existuje aspoň jedna citation,
- každá citation je exact retrieved citation,
- citation chunk IDs sú unique,
- `prompt_generation` je explicitná.

Výstup pinne:

- `retrieval_result_id`,
- `query_id`,
- prompt generation,
- answer/abstention stav,
- exact citations,
- canonical `answer_id`.

Answer CLI pred vytvorením envelope znovu validuje retrieval proti exact indexu a chunk manifestu. Samostatný falšovaný `retrieval.json` teda nie je authority.

## Mandatory abstention

Ak retrieval skončil `no_result`, povolený je iba:

```text
status = abstained
answer = null
abstention_reason = retrieval_no_result
citations = []
```

Answer text alebo citation pri `no_result` je contract violation.

## CLI

Po vytvorení corpus snapshotu a chunk manifestu:

```bash
python -m knowledge_hub_rag index \
  --manifest .runtime/rag/chunk-manifest.json \
  --output .runtime/rag/retrieval-index.json
```

Retrieval:

```bash
python -m knowledge_hub_rag retrieve \
  --manifest .runtime/rag/chunk-manifest.json \
  --index .runtime/rag/retrieval-index.json \
  --query "Ako funguje Kubernetes Service?" \
  --top-k 5 \
  --min-score 0.01 \
  --output .runtime/rag/retrieval.json \
  --context-output .runtime/rag/context.json
```

Structured answer od externého adaptera:

```bash
python -m knowledge_hub_rag answer \
  --manifest .runtime/rag/chunk-manifest.json \
  --index .runtime/rag/retrieval-index.json \
  --retrieval .runtime/rag/retrieval.json \
  --answer-text-file .runtime/rag/model-answer.txt \
  --cite-chunk-id <exact-retrieved-chunk-id> \
  --prompt-generation grounded-answer-v1 \
  --output .runtime/rag/answer.json
```

Pri `no_result` sa `--answer-text-file` ani `--cite-chunk-id` neposielajú; command zapíše abstention envelope.

## Testovaná source hranica

Izolovaný contract reconstruction pokrýva:

- deterministic index ID a full rebuild validation,
- relevant lexical ranking,
- explicitný `no_result`,
- deterministic query/result identity,
- rehashed dropped-hit refusal,
- bounded context a exact citation preservation,
- refusal citation, ktorá nebola retrieved,
- mandatory no-result abstention,
- refusal rehashed answer s modifikovanou citation metadata.

## Neoverená hranica

Táto vrstva ešte nepreukazuje:

- semantic embedding retrieval,
- learned alebo cross-encoder reranking,
- faithfulness answer textu voči citations,
- hallucination rate,
- prompt template promotion,
- direct alebo indirect prompt-injection resistance,
- model execution,
- token/cost telemetry,
- end-to-end runtime CI evidence.

Tieto body patria do nasledujúcej eval/security/observability vrstvy. `Runtime verified` zostáva otvorený aj kvôli issue #151.
