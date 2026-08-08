# Knowledge Hub LLM/RAG flagship

Tento package je praktický flagship pre sekciu 20. Implementované sú authoritative corpus identity, deterministic Markdown chunking, offline lexical retrieval, explicitný `no_result`, exact chunk citations a structured answer/abstention envelope. Model generation, evals, injection defense a observability sú samostatné nasledujúce vrstvy.

## Aktuálny lifecycle

```text
exact Git commit
→ explicitné corpus roots
→ path-sorted Markdown discovery
→ per-file byte SHA-256
→ immutable corpus snapshot ID
→ snapshot byte read-back
→ heading-aware deterministic parsing
→ fenced-code-safe block splitting
→ bounded chunk packing
→ per-chunk source/content identity
→ immutable chunk manifest ID
→ deterministic rebuild verification
→ deterministic lexical index
→ canonical query identity
→ BM25-v1 retrieval
→ results / no_result
→ exact chunk citations
→ bounded grounded context
→ structured answer alebo exact abstention
```

Snapshot nepoužíva mtime, absolute workspace path ani wall-clock timestamp. Rovnaké bytes, relatívne cesty, include roots a source revision preto vytvoria rovnaký `corpus_snapshot_id` aj v inom checkout adresári.

Chunk identity zahŕňa source path, source SHA-256, heading path, ordinal, content SHA-256 a character count. `chunk_manifest_id` fingerprintuje celý ordered manifest vrátane chunk textu a chunking configuration.

Retrieval index pinne exact `chunk_manifest_id`, source revision, tokenizer generation a lexical statistics. Query pinne index, normalized tokens a retrieval parametre. Result validator retrieval deterministicky vykoná znova; rehashed result s odstráneným alebo zmeneným hitom neprejde.

Podrobný retrieval/answer contract je v [`RETRIEVAL-GROUNDED-ANSWER.md`](RETRIEVAL-GROUNDED-ANSWER.md).

## Trust boundary

Corpus source je lokálny trusted Git checkout. Vstup musí mať exact lowercase 40-hex commit SHA. Default corpus root je `docs/`; ďalšie roots musia byť explicitne relatívne k repository rootu.

Zakázané sú:

- symlinked Markdown subjects,
- include root mimo repository rootu,
- non-Markdown corpus subject,
- ne-UTF-8 Markdown,
- snapshot s changed size alebo digestom,
- chunk manifest patriaci inému snapshotu alebo revision,
- chunk source digest odlišný od snapshotu,
- canonical tampering s corpus/chunk IDs,
- rehashed manifest s vynechaným alebo zmeneným chunkom,
- rehashed retrieval result, ktorý sa nezhoduje s deterministic query/index rebuildom,
- answer citation, ktorá nebola exact retrieved hitom,
- answer pri `no_result` namiesto mandatory abstention.

Hash sám nie je authority. Snapshot, chunk manifest, retrieval index a retrieval result sa validujú semanticky alebo deterministic rebuildom.

## CLI

Z editable installu package:

```bash
python -m knowledge_hub_rag snapshot \
  --repo-root . \
  --source-revision "$GIT_COMMIT" \
  --output .runtime/rag/corpus-snapshot.json

python -m knowledge_hub_rag verify-snapshot \
  --repo-root . \
  --snapshot .runtime/rag/corpus-snapshot.json

python -m knowledge_hub_rag chunk \
  --repo-root . \
  --snapshot .runtime/rag/corpus-snapshot.json \
  --output .runtime/rag/chunk-manifest.json

python -m knowledge_hub_rag validate-chunks \
  --repo-root . \
  --snapshot .runtime/rag/corpus-snapshot.json \
  --manifest .runtime/rag/chunk-manifest.json

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

Structured answer od budúceho deterministic/local/real model adaptera sa zapisuje cez `answer`. Command pred zápisom znova validuje retrieval proti exact indexu a manifestu.

Runtime output patrí do disposable `.runtime` alebo runner temp priestoru a nesmie sa commitovať.

## Parser a chunking semantics

Markdown headings vytvárajú ordered heading path. Heading syntax vo fenced code blocku sa neinterpretuje ako section boundary. Fenced blocks sa pri paragraph splittingu nerozbijú na blank lines.

Default chunk limits sú:

- `max_chars = 1800`,
- `min_chars = 240`.

Blok väčší než maximum sa delí deterministicky najprv na newline boundary, potom whitespace boundary a až potom hard character boundary. Malý posledný chunk sa spojí s predchádzajúcim iba vtedy, keď výsledok neprekročí maximum.

## Retrieval a citation semantics

Core retrieval používa deterministic `bm25-v1`, `unicode-word-v1` tokenizer, default `k1=1.2` a `b=0.75`. Stop-word list, stemming ani hidden locale config sa nepoužívajú.

Každý hit nesie exact:

- `chunk_id`,
- `source_path`,
- source file SHA-256,
- heading path,
- content SHA-256,
- canonical citation ID.

Ak žiadny chunk neprekročí score gate, result je `no_result`. Tento stav sa nesmie interpretovať ako odpoveď ani healthy evidence.

Structured answer envelope vyžaduje aspoň jednu exact retrieved citation. Pri `no_result` povoľuje iba `abstained`, `answer=null`, `retrieval_no_result` a prázdne citations.

Tento schema/citation contract ešte nedokazuje faithfulness textu; to bude samostatný eval gate.

## Evidence boundary

Implementované vrstvy môžu po úspešnom rune preukázať:

- exact documentation corpus viazaný na Git commit,
- per-file byte identity a read-back,
- workspace-independent snapshot identity,
- deterministic section/chunk identity,
- code-fence-aware parsing,
- tamper a source-drift refusal,
- completeness read-back cez deterministic rebuild,
- deterministic offline index identity,
- query/result identity,
- relevant lexical retrieval a explicitný no-result state,
- exact source/chunk citation binding,
- structured answered/abstained schema.

Zatiaľ nepreukazujú:

- semantic embedding retrieval alebo learned reranking,
- faithfulness answer textu,
- hallucination rate,
- prompt/config promotion,
- prompt injection resistance,
- model execution,
- token/cost telemetry,
- end-to-end runtime CI evidence,
- production search alebo business outcome.

## Ďalší blok

Nasledujúca vrstva pridá versioned prompt/config, deterministic model adapter, eval dataset a hard gates pre retrieval, citation, faithfulness a abstention slices. Potom nasledujú direct/indirect prompt-injection testy a trace/latency/token-equivalent observability.
