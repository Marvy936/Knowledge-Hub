# Knowledge Hub LLM/RAG runtime evidence

> **Evidence status: Pending**

Tento dokument je authoritative runtime-evidence contract pre celý offline/deterministic Practical v1 RAG flagship. Source implementácia už pokrýva exact Git corpus, deterministic Markdown chunking, lexical index/retrieval, explicitný `no_result`, exact citations, bounded grounded answer/abstention, eval/security release gates, tracing a cleanup. `Pending` znamená, že repository ešte nemá successful authoritative clean-checkout run pre exact merged implementation subject.

GitHub Actions dispatch je momentálne otvorený repository-level blocker v issue #151. Source/test completeness preto nie je `Runtime verified`.

## Required execution subject

Každý successful record musí pinovať:

- exact 40-character Git SHA,
- Python version,
- installed package/dependency resolution,
- implementation revision použitú runtime configom,
- include roots a corpus scope,
- workflow/run alebo equivalent execution ID,
- disposable runtime/output paths,
- cleanup/read-back result,
- explicit proof boundary.

Core CI nesmie pre tento offline gate vyžadovať platený model provider ani externý API key.

## 1. Exact Git corpus evidence

Required chain:

```text
exact Git subject
→ include roots
→ tracked Markdown corpus
→ per-file byte read-back
→ corpus snapshot
→ snapshot ID
```

Evidence musí obsahovať:

- source revision,
- file count,
- per-file relative path, byte size a SHA-256,
- canonical snapshot ID,
- successful byte read-back proti exact checkoutu,
- refusal branch pre changed bytes, symlinked source alebo invalid/tampered snapshot.

Branch name, abbreviated SHA alebo mutable checkout state nie je authoritative corpus identity.

## 2. Deterministic chunking evidence

Required evidence:

- exact corpus snapshot ID,
- chunking generation/config,
- deterministic heading/code-fence boundaries,
- chunk count,
- per-chunk content/source identity,
- canonical chunk manifest ID,
- full deterministic rebuild equality.

Failure matrix musí odhaliť minimálne:

- chunk content tampering,
- source digest mismatch,
- manifest patriaci inému snapshotu,
- rehashed manifest s vynechaným/pridaným chunkom,
- non-canonical chunk ordering/metadata.

## 3. Index and retrieval evidence

Practical v1 offline core používa deterministic lexical index/retrieval; generative/embedding provider nie je hard requirement.

Required chain:

```text
chunk manifest
→ deterministic index
→ index ID
→ canonical query
→ scored retrieval result
→ retrieval_result_id
```

Gate musí preukázať:

- index subject viazaný na exact manifest/corpus,
- deterministic rebuild indexu,
- canonical query/result identity,
- bounded `top_k` a score threshold z runtime configu,
- aspoň jeden positive query s retrieved chunks,
- exact ordered retrieved chunk IDs/scores,
- explicitný `no_result` query path,
- refusal stale/mismatched index alebo corpus subjectu.

`no_result` je validný explicitný stav; nesmie sa premeniť na fabricated answer.

## 4. Bounded context and exact citation evidence

Positive retrieval musí vytvoriť bounded grounded context iba z retrieved chunks.

Required evidence:

- context bound/config,
- exact chunk IDs zahrnuté do contextu,
- source path/section metadata podľa contractu,
- context identity,
- žiadny unretrieved chunk v answer authority,
- exact citations viazané na existujúce retrieved chunk IDs.

Citation, ktorá smeruje na iný corpus/index/chunk subject, je failure aj vtedy, ak text odpovede vyzerá správne.

## 5. Structured answer and abstention evidence

Offline reference adapter musí preukázať dva explicitné outcomes:

### Answered

```text
retrieval result
→ bounded context
→ structured answered envelope
→ exact citations
→ answer_id
```

Answered result vyžaduje non-empty grounded answer, exact citations a žiadny abstention reason.

### Abstained

```text
no_result alebo security refusal
→ structured abstained envelope
→ explicit abstention_reason
→ no fabricated citations
→ answer_id
```

Abstention je successful safe behavior pre príslušný test slice, nie systémová chyba.

## 6. Evaluation and release evidence

Hard eval musí byť viazaný na exact:

```text
implementation revision
+ corpus snapshot
+ chunk/index subject
+ runtime config
+ eval case set
→ eval report
→ prompt/config release
```

Required slices musia samostatne vyhodnotiť minimálne:

- retrieval relevance/expected retrieval,
- exact citation validity,
- answer faithfulness ku bounded contextu,
- expected abstention/no-result behavior,
- direct prompt-injection refusal,
- retrieved-context/indirect prompt-injection refusal.

Critical/high-risk security failure musí blokovať release. Aggregate green score nesmie prekryť failed injection slice.

Evidence musí obsahovať eval report ID, per-slice outcomes, failed-count, release ID a exact provenance na corpus/index/config/implementation subject.

## 7. Prompt-injection security evidence

Runtime gate musí explicitne odlíšiť dve authority hranice:

### Direct injection

Malicious instruction v user query nesmie prepísať code-defined system/runtime policy ani získať authority mimo bounded RAG contractu.

### Retrieved-content injection

Malicious instruction uložená v retrieved corpus texte je untrusted data. Expected behavior je security refusal/abstention podľa source policy; retrieved text sa nesmie reinterpretovať ako system/tool instruction.

Gate musí zaznamenať exact security classification/reason a potvrdiť, že refusal nevytvorila fabricated answer/citations.

## 8. Tracing and operational evidence

Každý executed query path musí mať bounded trace evidence viazanú na exact runtime subjects.

Required evidence:

- trace ID,
- runtime config/release identity,
- retrieval result ID,
- answer ID,
- latency evidence,
- token-equivalent/bounded-context counters podľa source contractu,
- explicitný status pre answered/no-result/security abstention.

Trace nesmie obsahovať credential/API key, raw private corpus mimo deklarovaného evidence scope alebo mutable unbounded debug dump.

## 9. Determinism and rebuild evidence

V rovnakom exact source/corpus/config subjecte musí repeated execution pre deterministic core preukázať stabilitu identity tam, kde contract neobsahuje meranú latency ako mutable field.

Minimálne:

- corpus snapshot rebuild parity,
- chunk manifest parity,
- index parity,
- canonical retrieval result parity pre rovnaký query/config,
- answer/citation identity parity podľa adapter contractu,
- eval/release rebuild validity.

## Required forbidden evidence

Runtime musí odmietnuť alebo odhaliť:

- abbreviated/mutable Git subject,
- changed bytes po snapshot vytvorení,
- symlinked corpus source,
- tampered snapshot/chunk/index IDs,
- missing/reordered chunk so znovu vypočítaným neautorizovaným manifestom,
- index z iného corpus subjectu,
- citation na unretrieved/nonexistent chunk,
- fabricated answer pri `no_result`,
- answer bez required citations,
- direct alebo indirect injection accepted ako authority,
- runtime-editable system policy mimo release provenance,
- eval/report/release subject mismatch,
- trace/result ID tampering,
- runtime artifacts ponechané v checkout-e po cleanup-e.

## Cleanup evidence

Cleanup sa musí vykonať po positive aj failure flowe podľa použitého runnera.

Musí odstrániť/read-backnúť non-existence:

- generated corpus snapshot/chunk/index files,
- query/context/answer/trace outputs,
- eval report a prompt-release runtime copies,
- temporary config/output directories,
- virtual environment alebo runner-temp state, ak je súčasťou exact gate-u,
- všetok disposable `.runtime` RAG state.

Tracked worktree musí po cleanup-e sedieť s exact source subjectom a nesmú pribudnúť nové runtime artifacts.

## Evidence record

Finálny successful RAG record musí uviesť minimálne:

- exact Git SHA,
- workflow/run/job ID,
- Python/package resolution,
- corpus snapshot ID + counts,
- chunk manifest ID + counts,
- index ID,
- positive retrieval result ID,
- explicit no-result evidence,
- answered result + exact citation IDs,
- abstention result/reason,
- direct/indirect injection slice outcomes,
- eval report ID,
- prompt/config release ID,
- trace IDs/operational counters,
- cleanup/read-back,
- proof boundary.

## Proof boundary

Úspešný Practical v1 RAG gate preukáže exact Git-bound deterministic offline lifecycle od corpus bytes cez chunk/index/retrieval a exact citations po structured answer/abstention, security eval, tracing a cleanup.

Nepreukáže automaticky:

- semantic embedding/retrieval quality,
- external vector database durability,
- generative LLM factuality mimo deterministic adapter contractu,
- paid/provider API availability,
- multi-tenant authorization,
- production latency/SLO,
- production business usefulness.

Voliteľný local alebo external LLM adapter môže byť post-v1 alebo doplnkový runtime layer; offline core evidence od neho nesmie závisieť.

Kým exact clean-checkout record neexistuje, stav zostáva `Pending`.
