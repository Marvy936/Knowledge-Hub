# Knowledge Hub LLM/RAG flagship

Tento package je praktický flagship pre sekciu 20. Prvá implementovaná vrstva rieši iba authoritative corpus identity a deterministic Markdown chunking. Retrieval, reranking, answer generation, evals, injection defense a observability sú samostatné nasledujúce vrstvy.

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
```

Snapshot nepoužíva mtime, absolute workspace path ani wall-clock timestamp. Rovnaké bytes, relatívne cesty, include roots a source revision preto vytvoria rovnaký `corpus_snapshot_id` aj v inom checkout adresári.

Chunk identity zahŕňa source path, source SHA-256, heading path, ordinal, content SHA-256 a character count. `chunk_manifest_id` fingerprintuje celý ordered manifest vrátane chunk textu a chunking configuration.

## Trust boundary

Corpus source je v tomto bloku lokálny trusted Git checkout. Vstup musí mať exact lowercase 40-hex commit SHA. Default corpus root je `docs/`; ďalšie roots musia byť explicitne relatívne k repository rootu.

Zakázané sú:

- symlinked Markdown subjects,
- include root mimo repository rootu,
- non-Markdown corpus subject,
- ne-UTF-8 Markdown,
- snapshot s changed size alebo digestom,
- chunk manifest patriaci inému snapshotu alebo revision,
- chunk source digest odlišný od snapshotu,
- canonical tampering s corpus/chunk IDs,
- rehashed manifest s vynechaným alebo zmeneným chunkom; final validation deterministicky rebuildne celý manifest z exact source bytes.

Hash sám nie je authority. Snapshot a chunk manifest sa pred ďalšou vrstvou validujú semanticky a proti source bytes.

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
```

Runtime output patrí do disposable `.runtime` alebo runner temp priestoru a nesmie sa commitovať.

## Parser a chunking semantics

Markdown headings vytvárajú ordered heading path. Heading syntax vo fenced code blocku sa neinterpretuje ako section boundary. Fenced blocks sa pri paragraph splittingu nerozbijú na blank lines.

Default chunk limits sú:

- `max_chars = 1800`,
- `min_chars = 240`.

Blok väčší než maximum sa delí deterministicky najprv na newline boundary, potom whitespace boundary a až potom hard character boundary. Malý posledný chunk sa spojí s predchádzajúcim iba vtedy, keď výsledok neprekročí maximum.

Tieto hodnoty sú zatiaľ parser generation `v1` implicitne reprezentovaná package version/schema. Budúci retrieval/index contract musí chunking configuration niesť ako immutable input a nesmie ticho re-chunkovať corpus.

## Evidence boundary

Táto vrstva môže po úspešnom rune preukázať:

- exact documentation corpus viazaný na Git commit,
- per-file byte identity a read-back,
- workspace-independent snapshot identity,
- deterministic section/chunk identity,
- code-fence-aware parsing,
- tamper a source-drift refusal,
- completeness read-back cez deterministic rebuild.

Nepreukazuje:

- semantic alebo lexical retrieval kvalitu,
- embedding model/version alebo vector index,
- reranking,
- grounded answer generation,
- citation correctness,
- structured answer schema,
- prompt injection resistance,
- eval-driven promotion,
- model/token/cost telemetry,
- production search alebo business outcome.

## Ďalší blok

Nasledujúca vrstva pridá deterministic offline index a retrieval contract s explicitným `no_result`, exact chunk citations a query/result identity. Externý API key nebude potrebný pre core CI path.
