# Vector stores a indexing

Vector store ukladá embeddings a súvisiace identities/metadata tak, aby aplikácia vedela vykonať similarity search alebo širší retrieval workflow. Index je konkrétna dátová štruktúra a generácia, ktorá zrýchľuje search. Tieto pojmy sa často zamieňajú s celou RAG databázou, ale retrieval correctness závisí aj od embedding compatibility, distance metric, metadata filtering, index type, build parameters, update lifecycle a exact-versus-approximate behavior.

Vector similarity nie je semantic truth. Najbližší vektor je iba najbližší podľa konkrétneho embedding modelu, normalizácie, metric a index/search configuration. Approximate Nearest Neighbor, skrátene ANN, môže vedome vymeniť čas, memory alebo scale za recall. Preto úspešný query a vysoké similarity score nepreukazujú, že bol nájdený authoritative evidence.

V incidente `GENAI-SUPPORT-04` tím migroval embedding model po častiach. Nové chunks boli embedované modelom `embed-multilingual-3`, staré zostali z modelu `embed-multilingual-2`; oba typy vektorov mali rovnaký rozmer, takže database insert prešiel. HNSW index ich uložil bez chyby, ale distances medzi dvoma nekompatibilnými vector spaces nemali definovaný význam. Retrieval quality klesla bez infraštruktúrneho alarmu.

## 1. Exact index subject

Index generation musí byť rozbaliteľná:

```yaml
vector_index:
  index_generation: support-policy-hnsw-2026-08-04.1
  corpus_generation: support-policy-2026-08-04.1
  embedding_model: embed-multilingual-3-2026-06-10
  embedding_dimension: 1536
  normalization: l2
  distance_metric: inner_product
  index_type: hnsw
  build_parameters:
    m: 24
    ef_construction: 160
  search_defaults:
    ef_search: 96
  metadata_schema: knowledge-metadata-v8
  tenant_partitioning: tenant-hash-v3
  record_count: 1842203
  created_at: 2026-08-04T04:42:11Z
```

Alias `support-policy-current` je operational pointer. Nie je dostatočná identity pre eval, rollback ani incident reconstruction.

## 2. Embedding compatibility

Vektory možno porovnávať iba v kompatibilnom vector space. Compatibility zahŕňa model snapshot, output dimension, preprocessing, input prefix/instruction, pooling a normalization.

```text
same dimension
≠ same vector space
≠ compatible distance semantics
```

Dva embedding modely môžu produkovať 1536-dimensional vectors, ale ich axes a distributions sa líšia. Partial in-place migration bez explicitného multi-index routing alebo full re-embedding je forbidden, pokiaľ provider negarantuje kompatibilitu.

## 3. Distance a similarity metrics

Bežné metrics:

```text
cosine similarity
inner product / dot product
Euclidean distance L2
```

Cosine porovnáva direction po zohľadnení norms. Inner product zohľadňuje direction aj magnitude, ak vectors nie sú normalizované. Pre unit-normalized vectors sú rankingy cosine a inner-product úzko prepojené. L2 meria vzdialenosť v priestore.

Vector database operator alebo index musí zodpovedať embedding contractu. Index vytvorený pre L2 a query interpretovaná ako cosine môže vracať iný ranking. Score direction sa tiež líši: pri similarity je vyššie často lepšie, pri distance nižšie.

## 4. Exact nearest-neighbor search

Exact search porovná query vector so všetkými candidate vectors alebo používa štruktúru, ktorá garantuje exact result pre daný metric. Je dôležitý ako correctness baseline.

```text
query vector
→ distance ku každému permitted vectoru
→ exact top-k
```

Exact search môže byť dostatočný pre menšie datasety alebo nízky query volume. Pri scale je drahší na latency a compute, ale poskytuje referenciu pre meranie ANN recall.

## 5. Approximate nearest-neighbor search

ANN index obmedzí search space a môže vynechať skutočných nearest neighbors. Cieľom je výhodnejší speed–recall–memory trade-off.

```text
ANN top-k
≈ exact top-k
```

Approximation sa musí merať na vlastnom corpus/query distribution. „Používame HNSW“ nehovorí nič o recall bez parameters, filters a data distribution.

## 6. HNSW

Hierarchical Navigable Small World vytvára viacvrstvový proximity graph. Search prechádza graphom od hrubých vrstiev k detailným candidates.

Typické parameters:

```yaml
hnsw:
  m: 24
  ef_construction: 160
  ef_search: 96
```

Vyššie `m` zvyšuje connections, memory a build cost. Vyššie `ef_construction` môže zlepšiť index quality za cenu build time. Vyššie `ef_search` zvyčajne zvyšuje recall a query cost. Konkrétne defaulty sú implementation-specific a nie sú universal recommendation.

HNSW často poskytuje dobrý speed-recall trade-off, ale delete/update, memory footprint, filtering a rebuild behavior sa líšia podľa produktu.

## 7. IVF a quantization

Inverted File Index, IVF, rozdelí vector space do clusters/lists. Query najprv nájde nearest centroids a prehľadá iba vybrané lists.

```yaml
ivf:
  lists: 2048
  probes: 32
```

Viac lists zmenšuje candidate partitions, ale vyžaduje vhodný training/build. Viac probes zvyšuje recall a latency. Index vytvorený na malej alebo nereprezentatívnej vzorke môže mať slabé partitioning.

Product Quantization, scalar quantization alebo binary quantization znižujú memory a bandwidth za cenu information loss. Často sa kombinuje approximate candidate generation s re-rankingom podľa presnejších vectors.

## 8. Flat index ako baseline

Flat L2 alebo inner-product index vykonáva brute-force exact search. Je vhodný ako eval baseline a pri menších datasets. Faiss napríklad oddeľuje exact `IndexFlatL2`/`IndexFlatIP` od approximate index families.

Produkčný acceptance test periodicky porovná ANN results proti exact baseline na sample queries:

```text
recall@k =
počet relevantných exact neighbors prítomných v ANN top-k
/
počet relevantných exact neighbors v baseline
```

Ground-truth relevance dataset je ešte dôležitejší než exact vector neighbors, pretože embedding metric nemusí dokonale reprezentovať user relevance.

## 9. Metadata filtering

Vector similarity sa kombinuje s filters pre tenant, language, document type, effective date, classification alebo ACL.

```sql
SELECT chunk_id, source_id, embedding <=> :query AS distance
FROM knowledge_chunks
WHERE tenant_id = :tenant
  AND effective_from <= :request_time
  AND (effective_to IS NULL OR effective_to > :request_time)
ORDER BY embedding <=> :query
LIMIT 20;
```

Database syntax a operator sú implementation-specific. Security point je poradie a guarantee: unauthorized vectors sa nesmú dostať do returned candidate set ani downstream promptu.

Pri ANN indexoch môže filtering prebiehať pred searchom, počas searchu alebo po candidate generation. Post-filtering môže vrátiť menej než `k` results a znížiť recall. Riešením môže byť partitioning, pre-filtered index, iterative scan alebo širší candidate budget.

## 10. Multi-tenant architecture

Možnosti zahŕňajú:

```text
samostatný index per tenant
shared index s mandatory tenant filterom
partitioned collections/namespaces
hybrid podľa tenant size a risku
```

Samostatný index zjednodušuje isolation, ale zvyšuje operational count. Shared index zlepšuje utilization, ale vyžaduje silné authorization/filtering a cache keys. Namespace label bez enforcement nie je security boundary.

## 11. Index build lifecycle

Immutable alebo blue-green build je často bezpečnejší než nekontrolovaná in-place mutation:

```text
corpus generation
→ embeddings
→ candidate index build
→ integrity checks
→ exact/ANN eval
→ metadata/ACL tests
→ alias promotion
→ old generation retention
```

Candidate index sa nepovýši iba preto, že `record_count` sedí. Kontroluje sa dimension, model generation, duplicates, missing records, deleted residue, index trained state, sample queries a recall/latency.

## 12. Incremental mutation

Streaming alebo incremental indexing znižuje freshness lag, ale komplikuje consistency. Pipeline potrebuje idempotent upsert identity, deletion/tombstone handling a reconciliation.

```yaml
vector_record:
  vector_id: chunk:policy/refunds/eu/2026-07#4.2@71bd
  chunk_generation: sha256:71bd...
  embedding_generation: embed-multilingual-3-2026-06-10
  index_generation: mutable-stream-support-v8
```

Retry po unknown outcome nesmie vytvoriť duplicate vector. Reconciliation porovná source-of-truth chunk registry a active index records.

## 13. Re-embedding migration

Pri zmene embedding modelu sa vytvorí nová index generation:

```text
old corpus chunks
→ new embedding model
→ candidate index B
→ query embedding route B
→ paired retrieval eval A/B
→ controlled promotion
```

Query vector a corpus vectors musia používať kompatibilný model/profile. Dual-read môže porovnať old a new index. Dual-write môže podporiť migration, ale nesmie miešať vectors v jednom logical indexe bez explicitného compatible designu.

## 14. Index consistency a read-after-write

Niektoré systems poskytujú eventual consistency. Upsert success nemusí znamenať okamžitú search visibility. Application contract potrebuje vedieť, či vyžaduje read-after-write a ako sa overuje.

```text
write accepted
≠ indexed
≠ searchable na každej replica
≠ active alias generation
```

Ingestion pipeline môže mať stages `persisted`, `embedded`, `indexed`, `searchable`, `promoted`. Business freshness SLA sa viaže na posledný relevantný stage.

## 15. Score calibration a thresholds

Similarity threshold nie je portable medzi modelmi, metrics ani datasets. Score distributions sa menia pri re-embeddingu a corpus drift.

Threshold sa kalibruje na labeled queries a segmentoch. Jeden global threshold môže zlyhať medzi languages alebo document types. Top-k bez minimum support môže vždy vrátiť niečo, aj keď je všetko nerelevantné.

```text
retrieve candidates
→ threshold/quality signals
→ sufficient-evidence verdict
→ context alebo no-answer
```

## 16. Hybrid retrieval a fusion

Vector store môže byť jedna časť hybrid systému. Lexical engine nájde identifiers a exact terms, vector index semantic matches. Candidate lists sa kombinujú napríklad rank fusion alebo learned scoringom.

Fusion policy je versioned:

```yaml
hybrid_policy:
  dense_candidates: 80
  sparse_candidates: 80
  fusion: reciprocal-rank-v3
  rerank_top_n: 40
  final_context_n: 8
```

Raw scores z dvoch engines nemusia byť priamo porovnateľné. Naivné sčítanie bez calibration môže preferovať jeden engine.

## 17. Sharding, replicas a capacity

Veľký corpus môže byť shardovaný podľa tenant, hash, language alebo semantic partition. Routing musí hľadať vo všetkých relevantných shards alebo mať preukázaný partition-selection mechanism.

Replicas zvyšujú availability a read throughput, ale môžu mať index-generation lag. Trace loguje shard/replica a generation. Capacity planning sleduje vector count, dimensions, memory/index bytes, query rate, build time a compaction/vacuum cost.

## 18. Backup a recovery

Backup vector indexu bez source chunks, metadata a embedding generation nemusí byť použiteľný. V niektorých architectures je index rebuildable derived artifact; authoritative backup sú source artifacts, chunk registry a pipeline manifests. Rebuild time potom vstupuje do RTO.

```text
restore source/chunks
→ regenerate alebo restore embeddings
→ rebuild index
→ verify recall/ACL
→ promote alias
```

Snapshot restore sa testuje vrátane query compatibility a deletion state.

## 19. Observability

Index metrics:

```yaml
metrics:
  - query_latency_p50_p95_p99
  - candidate_count
  - filter_drop_rate
  - exact_vs_ann_recall
  - zero_result_rate
  - score_distribution
  - index_size_bytes
  - build_duration
  - indexing_lag
  - deleted_residue
  - replica_generation_lag
```

Trace obsahuje query embedding generation, index generation, metric, search parameters, filters, returned IDs/distances a rerank/context decisions. Vector values sa nemusia logovať verbatim.

## 20. Failure hypotheses a troubleshooting

Pri retrieval regresii sa skúma:

```text
query/corpus embedding incompatibility
wrong dimension alebo preprocessing
wrong metric/operator
ANN parameters a recall
index training/build quality
metadata filter behavior
shard routing
stale alias alebo replica
partial upsert/delete
score threshold drift
```

Prvý diagnostický experiment často porovná exact search a ANN nad rovnakými vectors a filters. Ak exact search tiež zlyhá, problém je skôr embedding, data alebo relevance contract než ANN structure. Ak exact uspeje a ANN nie, skúmajú sa index/search parameters a filtering.

## 21. Containment a recovery

Containment môže prepnúť na exact search pre kritický menší corpus, zvýšiť ANN search breadth, vrátiť known-good index alias alebo vypnúť affected tenant/language route.

Recovery:

```text
freeze failing query a exact manifests
→ validate embedding compatibility
→ compare exact a ANN
→ rebuild candidate index
→ run recall/latency/ACL gates
→ promote
→ second-query a deletion test
```

## 22. Acceptance

Pozitívna acceptance vyžaduje exact embedding/index subject, compatible vector space, správny metric, exact baseline, measured ANN recall, mandatory authorization filtering, versioned build/mutation lifecycle, re-embedding strategy, observability, backup/rebuild test a retrieval outcome metrics.

Recovery acceptance vyžaduje identifikáciu či zlyhal data, embedding, exact similarity, ANN, filter alebo routing stage; obnovenie known-good generation; paired queries a second-operation/delete verification.

Forbidden acceptance je úspešný insert ako dôkaz compatibility, rovnaký dimension ako dôkaz rovnakého vector space, vysoký similarity score ako correctness, HNSW/IVF default bez recall evaluation alebo alias promotion iba podľa record countu.
