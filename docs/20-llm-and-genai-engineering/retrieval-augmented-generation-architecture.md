# Retrieval-Augmented Generation architecture

Retrieval-Augmented Generation, skrátene RAG, je application architecture, v ktorej model nedostáva iba používateľský prompt a svoje parametric knowledge, ale aj externe vyhľadaný kontext. Cieľom nie je „dať modelu databázu“, ale vytvoriť riadený evidence path od authoritative source cez ingestion, index, retrieval a context assembly až po grounded odpoveď a citation verification.

RAG môže zlepšiť aktuálnosť, domain coverage a provenance, ale automaticky neodstraňuje hallucinations. Retrieval môže vrátiť irelevantný, zastaraný alebo neoprávnený dokument. Generator môže správny evidence ignorovať, nesprávne ho interpretovať alebo vytvoriť tvrdenie, ktoré v kontexte nie je. Preto sa retrieval success, context faithfulness a business correctness hodnotia oddelene.

V incidente `GENAI-SUPPORT-04` support assistant začal citovať starú refund policy. Aplikačný dashboard ukazoval úspešné vector queries a nízku latency, preto tím označil retrieval za zdravý. Neskôr sa zistilo, že corpus alias smeroval na index obsahujúci novú aj starú policy generáciu, metadata filter nepoužíval `effective_to` a generator dostal oba protichodné chunks. Úspešný search request nepreukázal správny evidence set.

## 1. Business a evidence contract

RAG sa navrhuje od user outcome a authority boundary:

```text
user question
→ required authoritative domain
→ access-controlled corpus
→ retrieved evidence
→ grounded answer alebo explicit insufficient-evidence result
```

Príklad support contractu:

```yaml
rag_contract:
  workload: refund-policy-answer
  authoritative_sources:
    - policy-registry
  allowed_tenants: request-tenant-only
  freshness_requirement: effective-at-request-time
  citations_required: true
  unsupported_claim_policy: refuse-or-escalate
  maximum_evidence_age: governed-by-policy-validity
```

Corpus nie je authoritative iba preto, že je indexovaný. Authority vzniká zo source ownership, schváleného publication lifecycle a effective-date semantics.

## 2. End-to-end RAG lifecycle

Produkčný RAG lifecycle vyzerá takto:

```text
source registration
→ extraction a normalization
→ document/chunk identity
→ metadata a ACL enrichment
→ embedding generation
→ index build alebo mutation
→ query understanding
→ retrieval
→ filtering a reranking
→ context assembly
→ generation
→ citation/evidence validation
→ business outcome a feedback
```

Každá šípka môže meniť výsledok. Preto sa „RAG version“ nerozumie ako jediný vector-store alias, ale ako zostava identifikovaných generácií.

## 3. Exact RAG subject

RAG request je composite subject. Rovnaká user otázka môže dostať iný evidence set po zmene parsera, embedding modelu, index generation, filters alebo rerankera, aj keď generator model a prompt zostanú rovnaké. Incident a eval preto musia vedieť rekonštruovať každú resolved generation, nie iba finálnu odpoveď.

Manifest slúži aj ako boundary pre cache, rollout a rollback. Ak dva requesty nemajú rovnaký corpus/index/retrieval/context subject, nemožno ich považovať za čistý model A/B test. Request trace preto potrebuje rozbaliteľný manifest:

```yaml
rag_request:
  corpus_generation: support-policy-2026-08-04.1
  parser_generation: unstructured-layout-v9
  chunker_generation: policy-semantic-v6
  embedding_model: embed-multilingual-3-2026-06-10
  index_generation: support-policy-hnsw-2026-08-04.1
  query_rewrite: support-query-v5
  retrieval_policy: hybrid-rrf-v7
  metadata_filter: tenant-effective-language-v4
  reranker: rerank-crossencoder-v3
  context_assembler: grounded-context-v8
  prompt_release: support-grounded-v19
  generator_model: support-pro-2026-07-28
```

Bez tohto manifestu sa nedá rozlíšiť zmena source, parsera, embeddingov, index parametrov, query rewrite alebo generatora.

## 4. Parametric a non-parametric knowledge

Model parameters obsahujú naučené patterns a knowledge z tréningu. RAG pridáva non-parametric memory: explicitne uložené dokumenty alebo records, ktoré možno aktualizovať bez retrainingu modelu.

To neznamená, že external context má automaticky vyššiu epistemickú váhu. Aplikácia musí modelu explicitne určiť, ktoré zdroje sú authoritative, ako riešiť konflikt a kedy odpoveď nevytvoriť.

```text
model prior
+ retrieved evidence
+ instruction contract
→ generated answer
```

Ak evidence chýba, model môže doplniť plausible text zo svojich parametrov. Preto grounded workload potrebuje insufficient-evidence behavior a post-generation validation.

## 5. Corpus architecture

Corpus môže byť zostavený z files, database records, tickets, web pages, code, logs alebo API snapshots. Každý source má ownera, classification, publication state, retention a deletion semantics.

```yaml
source_record:
  source_id: policy/refunds/eu/2026-07
  owner: legal-operations
  authority: approved-policy
  tenant_scope: global-eu
  effective_from: 2026-07-01T00:00:00Z
  effective_to: null
  classification: internal
  source_digest: sha256:91ca...
  ingestion_state: indexed
```

Copy uložená v object storage nie je automaticky current authority. Ingestion musí zachovať link na source identity a mutation event.

## 6. Query path

Query path môže obsahovať normalization, language detection, intent classification, decomposition, expansion alebo hypothetical-document generation. Každá transformácia mení retrieval subject.

```text
raw user query
→ trust-safe normalization
→ scope a tenant resolution
→ retrieval query alebo queries
→ vector/lexical search
→ candidate evidence set
```

Query rewrite je model-generated artifact, nie používateľský fakt. Loguje sa, validuje a nesmie meniť authorization scope. Model nesmie rozšíriť tenant filter preto, že „potrebuje viac informácií“.

## 7. Retrieval families

Dense retrieval používa embeddings a vector similarity. Sparse alebo lexical retrieval používa token/term matching, napríklad BM25. Hybrid retrieval kombinuje oba signály. Structured retrieval môže používať SQL, graph alebo API filters.

```text
dense: semantic proximity
sparse: exact terms a rare identifiers
structured: exact fields a constraints
hybrid: kombinácia a fusion
```

Dense retrieval môže nájsť parafrázu, ale zlyhať na presnom policy ID. Lexical search môže nájsť ID, ale minúť synonymá. Hybrid nie je automaticky lepší; fusion weights a candidate budgets sa musia evaluovať.

## 8. Candidate generation, filtering a reranking

Retrieval sa často skladá z viacerých stages:

```text
broad candidate search
→ mandatory ACL/metadata filter
→ deduplication
→ reranking
→ evidence diversity/coverage
→ top-k context candidates
```

ACL filter je security control, nie relevance optimization. Musí byť aplikovaný tak, aby unauthorized candidate neunikol do promptu ani logu. Post-filtering po ANN search môže znížiť počet výsledkov; systém musí vedieť zvýšiť search breadth alebo použiť partitioning/pre-filtering.

Reranker prehodnocuje relevance query-document pair. Jeho score nie je correctness ani authority. Starý policy document môže byť veľmi relevantný, ale neplatný.

## 9. Context assembly

Context assembly rozhoduje, ktoré passages sa dostanú do model inputu, v akom poradí, s akými labels a token budgetom.

```yaml
context_item:
  chunk_id: policy-refund-eu-2026-07#section-4.2
  source_id: policy/refunds/eu/2026-07
  authority: approved-policy
  effective_at: 2026-08-04T04:53:00Z
  retrieval_score: 0.82
  rerank_score: 0.91
  citation_label: S1
  content_digest: sha256:71bd...
```

Delimiters a labels pomáhajú serialization, ale nie sú security sandbox. Retrieved text sa klasifikuje ako untrusted data, aj keď pochádza z interného dokumentu; môže obsahovať prompt injection alebo neaktuálne inštrukcie.

## 10. Grounding a citations

Citation je mapping medzi answer claim a source evidence. URL alebo chunk ID pripojené k odpovedi samy osebe nepreukazujú support.

```text
claim
→ cited context span
→ source identity
→ authority a validity
→ semantic entailment alebo support verdict
```

Aplikácia môže vyžadovať inline citation labels a potom overiť, že každé factual claim má platný source reference. Automatický entailment grader je pomocný signál; high-risk cases môžu vyžadovať deterministic validators alebo human review.

## 11. No-answer a conflict behavior

RAG systém potrebuje explicitné stavy:

```yaml
answer_status:
  - grounded
  - insufficient_evidence
  - conflicting_evidence
  - unauthorized_scope
  - retrieval_failure
  - generation_failure
```

Ak dva authoritative documents konfliktujú, generator nemá „vybrať pravdepodobnejší“. Musí použiť effective-date/precedence rules alebo eskalovať conflict. Ak retrieval nič nenájde, fluent answer zo všeobecnej znalosti môže byť forbidden.

## 12. Freshness, updates a deletion

RAG umožňuje knowledge updates bez model retrainingu, ale iba ak ingestion a index lifecycle správne propagujú zmenu.

```text
source mutation
→ event alebo scan detection
→ extraction/chunk diff
→ embedding/index mutation
→ alias promotion
→ retrieval verification
```

Delete musí odstrániť nielen source object, ale aj derived chunks, vectors, caches a replicas podľa retention policy. Tombstone bez query filtering môže stále vracať deleted content.

## 13. Multi-tenant a authorization boundary

Tenant, user a document ACL sa riešia pred alebo počas retrievalu authoritative identity layerom. Model-generated tenant ID sa nepoužíva ako authority.

```text
authenticated principal
→ tenant/resource authorization
→ permitted corpus partitions a filters
→ retrieval
```

Shared vector store môže byť bezpečný iba pri správnom partitioning/filtering a testoch. Neúspešný unauthorized query musí overiť, že content nebol retrieved, logged ani cached.

## 14. Caching

RAG môže cacheovať query rewrites, embeddings, retrieval results alebo final answers. Cache key musí zahŕňať relevantné generácie a authorization scope.

```text
cache key =
normalized query
+ tenant/access scope
+ corpus/index generation
+ retrieval policy
+ prompt/model release
```

Cache bez corpus generation môže po policy update servovať starý evidence set. Shared cache bez tenant scope môže spôsobiť data leak.

## 15. Evaluation model

RAG evaluation sa rozkladá:

| Vrstva | Príklady metrík |
|---|---|
| Ingestion | extraction coverage, metadata correctness, stale/deleted residue |
| Retrieval | recall@k, precision@k, MRR, nDCG, evidence coverage |
| Context | authority validity, duplication, conflict, token efficiency |
| Generation | faithfulness, answer correctness, citation support, refusal |
| Outcome | resolution rate, escalation, user correction, compliance |

High answer score nemôže zakryť unauthorized retrieval. High retrieval recall nemôže zakryť generator hallucination. Eval dataset musí obsahovať unanswerable, conflicting, outdated, multilingual a access-control cases.

## 16. Observability

Trace zachytáva raw query digest, transformed queries, corpus/index generation, filters, candidate IDs/scores, reranked set, final context items, prompt/model release, citations, validators, latency a outcome. Sensitive content sa nemusí logovať verbatim; identities a digests musia zostať auditovateľné.

Latency sa rozkladá na rewrite, embedding, search, rerank, context assembly, generation a validation. Aggregate p95 bez stage breakdownu neposkytuje recovery direction.

## 17. Failure hypotheses a troubleshooting

Pri nesprávnej odpovedi sa testujú competing hypotheses:

```text
source nie je authoritative alebo current
parser stratil obsah
chunking rozdelil evidence
metadata/ACL sú chybné
embedding/query mismatch
ANN index znížil recall
filter odstránil candidates
reranker preferoval zlý dokument
assembler orezal evidence
generator evidence ignoroval
citation validator zlyhal
```

Najprv sa identifikuje prvý stage, kde expected evidence zmizlo alebo sa zmenilo. Re-running iba final prompt nevie diagnostikovať ingestion a retrieval.

## 18. Containment a recovery

Containment znižuje business a security dopad skôr, než je potvrdený root cause. Môže vypnúť affected corpus alias, prepnúť na known-good index generation, obmedziť workload na read-only lookup alebo vynútiť escalation pri insufficient evidence. Voľba containmentu sa viaže na prvý podozrivý stage; plošné vypnutie generatora nepomôže, ak unauthorized dokument už uniká v retrieval výsledkoch.

Recovery obnovuje celý evidence path, nie iba jeden component. Known-good index sa najprv read-backne, potom sa replayom overí source authority, ingestion, exact a ANN retrieval, filters, reranking, context a generation. Až po bounded canary a druhej odlišnej query sa potvrdzuje, že oprava nie je iba sample-specific.

Recovery postup:

```text
freeze exact failing trace
→ verify source authority
→ replay ingestion
→ compare exact a ANN retrieval
→ validate filters/reranker/context
→ replay generation
→ bounded canary
→ second-query acceptance
```

## 19. Acceptance

Pozitívna acceptance vyžaduje versioned corpus/index/pipeline manifest, authoritative source lifecycle, access-controlled retrieval, representative retrieval a generation evals, claim-level evidence model, no-answer behavior, observability a business outcome metrics.

Recovery acceptance vyžaduje identifikáciu stage-level root cause, obnovu known-good generation, replay affected a control queries, deletion/freshness verification a druhú operáciu po oprave.

Forbidden acceptance je tvrdenie, že vector query success znamená správny retrieval, že citácia znamená grounded claim, že RAG eliminuje hallucinations alebo že index alias bez corpus a embedding identity je reprodukovateľný release.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Model version pinning a compatibility](model-version-pinning-compatibility.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Chunking, metadata a document processing →](chunking-metadata-document-processing.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
