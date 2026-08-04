# Retrieval, hybrid search a reranking

Retrieval pipeline rozhoduje, ktoré evidence units sa vôbec dostanú do ďalších stages RAG systému. Vector search je iba jeden candidate-generation mechanism. Produkčný retrieval zvyčajne kombinuje lexical, dense a structured signály, mandatory authorization filters, deduplication, reranking a explicitný sufficient-evidence verdict. Každý stage má vlastnú generation, score semantics, latency a failure boundary.

V incidente `GENAI-SUPPORT-05` zákazník uviedol presný identifikátor policy `RF-EU-042`. Query-rewrite model ho preformuloval na všeobecné „late refund exception“. Dense retriever našiel semanticky podobné dokumenty, lexical retriever našiel presný identifikátor, ale fusion policy zvýhodnila dense list. Click-trained reranker následne posunul na prvé miesto staršiu, populárnejšiu policy. Search request bol technicky úspešný, no authoritative dokument v candidate sete prehral kvôli zlej kombinácii rewrite, fusion a reranking signálov.

## 1. Retrieval subject

Retrieval request musí byť identifikovateľný od raw query po finálne zoradený evidence set. Jeden top-k list bez stage provenance nestačí, pretože neukazuje, či dokument pochádzal z lexical, dense alebo structured vetvy a kde sa jeho rank zmenil.

```yaml
retrieval_request:
  request_id: rag-req-8421
  raw_query: "Ako sa uplatňuje RF-EU-042?"
  query_generation: support-query-v6
  corpus_generation: policy-corpus-2026-08-04.2
  dense_index: policy-embed3-hnsw-2026-08-04.2
  sparse_index: policy-bm25-2026-08-04.2
  structured_source: policy-registry-v11
  authorization_filter: principal-tenant-policy-v5
  dense_candidates: 80
  sparse_candidates: 80
  fusion_policy: rrf-v4
  reranker: support-crossencoder-v7
  final_candidates: 12
```

Raw query, rewritten queries, filters, candidate budgets, fusion a reranker generation sú súčasť exact subjectu. Zmena jedného z nich vytvára inú retrieval execution generation, aj keď corpus zostane rovnaký.

## 2. Query understanding a rewrite

Query normalization môže odstrániť encoding artefacts, rozpoznať jazyk alebo zjednotiť whitespace. Query rewrite ide ďalej: môže rozvinúť skratku, vytvoriť synonyms, doplniť kontext z konverzácie alebo rozdeliť multi-hop otázku na viac subqueries. Taká transformácia je model-generated artifact, nie používateľská authority.

Presné identifikátory, čísla objednávok, policy codes, mená produktov a quoted phrases sa musia zachovať alebo poslať samostatnou lexical vetvou. Rewrite, ktorý zmení `RF-EU-042` na všeobecný opis, môže zlepšiť semantic recall, ale poškodiť exact-match recall.

```yaml
query_plan:
  raw: "RF-EU-042 late refund"
  lexical_queries:
    - '"RF-EU-042"'
    - 'RF-EU-042 refund'
  dense_queries:
    - "late refund exception in EU policy"
  structured_lookup:
    policy_id: RF-EU-042
```

Query plan sa validuje proti authorization scope. Model nesmie z konverzácie odvodiť širší tenant, region alebo document class, než povoľuje authenticated principal.

## 3. Sparse a lexical retrieval

Lexical retrieval pracuje s term frequency, document frequency, field boosts a tokenization. Je silný pri exact identifiers, rare terms, product names, error codes a quoted text. Jeho slabinou je vocabulary mismatch: používateľ môže pomenovať rovnaký koncept inými slovami než dokument.

BM25 alebo obdobný ranking používa term matching s normalizáciou podľa dĺžky dokumentu. Konkrétne score nie je portable medzi indexmi ani priamo porovnateľné s cosine similarity. Fielded search môže zvýhodniť `policy_id`, title alebo headings oproti body textu.

```json
{
  "query": {
    "bool": {
      "filter": [
        {"term": {"tenant_id": "eu-support"}},
        {"range": {"effective_from": {"lte": "2026-08-04T07:30:00Z"}}}
      ],
      "should": [
        {"term": {"policy_id": {"value": "RF-EU-042", "boost": 8}}},
        {"match": {"title": {"query": "late refund", "boost": 3}}},
        {"match": {"body": "late refund exception"}}
      ],
      "minimum_should_match": 1
    }
  }
}
```

Tento príklad ilustruje separation medzi mandatory filters a relevance clauses. Tenant a effective-date filter nesmie byť iba optional scoring signal.

## 4. Dense retrieval

Dense retrieval embeduje query a dokumenty do kompatibilného vector space a používa similarity alebo distance. Je vhodný pre paraphrases, semantic proximity a multilingual matching, ale môže prehliadnuť význam presného symbolu alebo negácie.

Query embedding profile musí byť kompatibilný s corpus embeddings. Niektoré embedding modely používajú odlišný prefix alebo instruction pre query a document. Ak pipeline zabudne query prefix, dimension môže sedieť, no distribution a relevance sa zmenia.

Dense top-k je candidate set, nie evidence verdict. Pri veľkom k sa zvyšuje recall a downstream cost; pri malom k môže relevantný dokument vypadnúť skôr, než ho reranker uvidí.

## 5. Structured retrieval

Niektoré otázky majú presný authoritative lookup path cez SQL, API, graph alebo registry. Policy ID, account state, effective-date rule alebo product compatibility sa nemusia riešiť approximate searchom.

```sql
SELECT policy_id, version, status, effective_from, effective_to, source_uri
FROM policy_registry
WHERE policy_id = :policy_id
  AND effective_from <= :request_time
  AND (effective_to IS NULL OR effective_to > :request_time)
  AND status = 'approved';
```

Structured result môže slúžiť ako filter, anchor candidate alebo samostatný evidence source. Ak authoritative registry vráti presnú platnú verziu, semantic retriever ju nemá prehlasovať populárnejším draftom.

## 6. Hybrid retrieval

Hybrid retrieval kombinuje candidate lists z viacerých retrieverov. Cieľom je získať semantic recall dense vetvy a exact-term recall sparse alebo structured vetvy. Kombinácia však potrebuje explicitnú fusion policy.

Raw scores sa zvyčajne nedajú priamo sčítať, pretože majú odlišné distributions a direction. Score normalization môže používať min-max, z-score alebo learned calibration, ale je citlivá na query distribution a outliers. Rank-based fusion obchádza časť problému tým, že kombinuje poradie namiesto raw scores.

Reciprocal Rank Fusion, RRF, možno zapísať:

```text
RRF(d) = Σ 1 / (k + rank_r(d))
```

Konštanta `k` tlmí rozdiel medzi vysokými rankmi a každý retriever môže mať vlastnú váhu. Fusion zvýši rank dokumentu, ktorý sa objaví vo viacerých listoch, no môže potlačiť presný structured hit, ak je iba v jednej vetve. Preto authoritative anchors môžu mať osobitné pravidlo.

Praktický deterministic RRF helper:

```python
from collections import defaultdict
from collections.abc import Iterable


def reciprocal_rank_fusion(
    ranked_lists: Iterable[list[str]],
    *,
    k: int = 60,
) -> list[tuple[str, float]]:
    scores: dict[str, float] = defaultdict(float)
    for ranked in ranked_lists:
        for rank, document_id in enumerate(ranked, start=1):
            scores[document_id] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))
```

Tento helper rieši iba rank fusion. Neimplementuje ACL, authority, freshness, deduplication ani sufficient-evidence decision.

## 7. Candidate budgets

Každá vetva potrebuje candidate budget. Dense retriever môže vrátiť 100 kandidátov, lexical 50 a structured lookup 5. Fusion a reranker potom spracujú union. Príliš nízky budget znižuje recall; príliš vysoký zvyšuje latency a reranker cost.

Budget sa nevolí iba globálne. Exact-ID query môže potrebovať malú structured a lexical vetvu, zatiaľ čo broad conceptual query potrebuje širší dense pool. Multi-hop otázka môže vytvoriť viac subqueries a samostatný budget pre každý hop.

Candidate-budget telemetry zahŕňa requested count, returned count, filtered count, deduplicated count a reranked count. Ak filter po ANN searchi odstráni väčšinu výsledkov, pipeline musí vedieť rozšíriť search breadth alebo použiť pre-filtering/partitioning.

## 8. Mandatory filtering a authorization

Authorization filter je correctness a security boundary. Nesmie byť optional boost a nesmie sa aplikovať až po tom, čo unauthorized text vstúpil do rerankera, promptu alebo debug logu.

```text
authenticated principal
→ resolved tenant a groups
→ permitted corpus partitions/filters
→ candidate generation
→ ranking
```

Niektoré vector engines vykonávajú post-filtering po ANN candidate generation. Aj keď unauthorized result nie je vrátený aplikácii, treba overiť, či nebol spracovaný externým rerankerom alebo uložený v trace. Security acceptance zahŕňa negative query, pri ktorej sa zakázaný document ID neobjaví v žiadnom downstream artefakte.

## 9. Deduplication a canonical identity

Overlap, duplicate sources, mirrored web pages a parent-child expansion môžu vytvoriť viac takmer rovnakých candidates. Bez deduplication môžu obsadiť celý top-k a vytlačiť evidence diversity.

Deduplication môže používať canonical source ID, content digest, parent document a high-overlap relation. Nesmie však zlúčiť dve policy versions iba preto, že sú textovo podobné. Version, effective dates a authority state sú súčasť identity.

```yaml
dedup_key:
  canonical_source_id: policy/refunds/eu
  source_version: 7
  chunk_digest: sha256:71bd...
```

Po deduplication sa musí zachovať mapping z pôvodných rankov a score provenance na canonical candidate. Inak sa citation labels a diagnostics môžu posunúť.

## 10. Reranking

Reranker prehodnocuje menší candidate set s bohatším query-document interaction modelom. Cross-encoder spracuje query a document spoločne, preto môže lepšie rozlíšiť jemné podmienky než bi-encoder similarity. Je však drahší, lebo inference prebieha pre každý pair.

Reranker score je relevance estimate, nie authority, validity ani factual entailment. Starý policy dokument môže odpovedať na otázku presnejšie než nový, ale stále je neplatný. Mandatory metadata a authority gates preto ostávajú mimo alebo pred rerankerom.

Pointwise reranker skóruje každý pair samostatne. Pairwise model porovnáva dva candidates. Listwise model pracuje s celým listom. Každý variant má iné latency, context a reproducibility trade-offs.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    document_id: str
    text: str
    authority: str
    effective: bool
    authorized: bool


def eligible(candidate: Candidate) -> bool:
    return (
        candidate.authorized
        and candidate.effective
        and candidate.authority == "approved-policy"
    )


# Model scoring sa vykoná iba nad eligible candidates.
eligible_candidates = [item for item in candidates if eligible(item)]
rerank_pairs = [(query, item.text) for item in eligible_candidates]
scores = cross_encoder.predict(rerank_pairs)
ranked = sorted(
    zip(eligible_candidates, scores, strict=True),
    key=lambda item: float(item[1]),
    reverse=True,
)
```

Aplikačný kód stále musí validovať vstupy, limitovať text a zaznamenať reranker generation.

## 11. Reranker training data a bias

Reranker trénovaný na clicks môže zdediť position bias, popularity bias a feedback loops. Dokument zobrazený na prvom mieste dostáva viac klikov, preto sa javí relevantnejší a model ho posúva ešte vyššie. Click nemusí znamenať vyriešený problém; používateľ mohol kliknúť na nesprávny výsledok a vrátiť sa.

Training dataset potrebuje explicitné positives, hard negatives a segment coverage. Hard negative je dokument, ktorý je veľmi podobný query, ale nie je správny evidence. Pre policy retrieval sú kritické staré verzie, susedné regióny a podobné exceptions.

```json
{
  "query": "RF-EU-042 late refund",
  "positive": "policy/refunds/eu/v7#exception-4.2",
  "hard_negatives": [
    "policy/refunds/eu/v6#exception-4.2",
    "policy/refunds/uk/v7#exception-4.2",
    "policy/refunds/eu/v7#standard-rule"
  ],
  "judgment_source": "legal-review-2026-08"
}
```

Training a evaluation queries sa oddeľujú podľa source/version/time, aby sa predišlo leakage.

## 12. Diversity a coverage

Top-k môže potrebovať viac než maximálnu individual relevance. Multi-part otázka vyžaduje evidence pre každú subclaim. Maximal Marginal Relevance alebo custom diversity policy môže penalizovať redundantné candidates, ale nesmie odstrániť dve odlišné authoritative clauses len pre vysokú textovú podobnosť.

Coverage policy sa môže viazať na query plan:

```yaml
required_facets:
  - policy_rule
  - exception_conditions
  - effective_date
  - escalation_path
```

Assembler dostane evidence set až po overení, že mandatory facets majú kandidáta alebo sa výsledok označí `insufficient_evidence`.

## 13. Multi-hop retrieval

Niektoré otázky nemožno vyriešiť jedným searchom. Najprv sa nájde policy, potom linked product class alebo customer eligibility. Multi-hop pipeline musí evidovať dependency medzi subqueries a nesmie používať model-generated intermediate claim ako authoritative filter bez validácie.

```text
question
→ retrieve policy by ID
→ extract referenced eligibility table ID
→ structured lookup eligibility table
→ join evidence
```

Každý hop má samostatný candidate set a failure state. Ak prvý hop vráti nesprávny document, druhý môže byť konzistentný, ale celý answer nesprávny.

## 14. Thresholds a sufficient-evidence verdict

Top-k search takmer vždy môže vrátiť niečo. Systém preto potrebuje sufficient-evidence policy, ktorá kombinuje retrieval signals, authority, coverage a validation.

Global similarity threshold nie je portable medzi models, languages a corpus generations. Kalibrácia sa robí na labeled queries a segmentoch. Threshold môže byť iba jeden signál vedľa exact-ID match, reranker margin, evidence coverage a conflict detection.

```yaml
evidence_verdict:
  status: sufficient
  required_facets_covered: true
  authoritative_candidates: 3
  conflicting_candidates: 0
  top_rerank_score: 0.91
  score_margin: 0.18
  calibrated_segment: policy-id-en
```

Model-generated confidence bez calibration nie je replacement za retrieval verdict.

## 15. Latency a cost

Retrieval latency sa rozkladá na query planning, embeddings, sparse search, dense search, structured lookup, filtering, fusion, reranking a deduplication. Parallel branches môžu znížiť wall-clock latency, no výsledok sa nesmie finalizovať skôr, než prídu mandatory branches.

Reranking cost rastie s počtom pairs a text length. Candidate text sa môže skrátiť na relevantný window, ale truncation policy musí zachovať podmienky a provenance. Cache reranker score je bezpečná iba pri rovnakých query, document digest, reranker generation a authorization scope.

## 16. Observability

Trace zachytáva raw a rewritten queries, filters, per-retriever candidates a scores, fusion contribution, removed unauthorized candidates, dedup mapping, reranker input digest, final rank, threshold verdict a latency per stage.

```yaml
candidate_trace:
  document_id: policy/refunds/eu/v7#4.2
  dense_rank: 14
  sparse_rank: 1
  structured_rank: 1
  fused_rank: 2
  reranked_rank: 1
  authorized: true
  effective: true
  final_selected: true
```

Aggregate `search_success_rate` nepreukazuje retrieval quality. Potrebné sú labeled recall, rank metrics, zero-result rate, insufficient-evidence rate, filter-drop rate a final outcome link.

## 17. Failure hypotheses a diagnostics

Pri retrieval miss sa porovná raw query a rewrite, exact structured lookup, lexical candidates, dense candidates, filters, fusion, dedup a reranking. Prvý stage, kde expected document zmizol alebo stratil rank, určuje recovery direction.

```text
expected source nebol indexovaný
query rewrite stratil identifier
lexical analyzer rozdelil token
query/corpus embeddings nie sú compatible
ANN recall je nízky
filter odstránil validný candidate
fusion potlačil authoritative branch
reranker preferoval popularity bias
threshold odmietol dostatočné evidence
```

Re-running iba generatora neoveruje žiadnu z týchto hypotéz.

## 18. Containment a recovery

Containment môže vypnúť query rewrite pre exact-ID segment, zvýšiť lexical/structured weight, bypassnúť affected reranker alebo prepnúť na known-good retrieval policy. Pri možnom authorization probléme sa affected route vypne úplne, nie iba zníži rank.

Recovery zachová failing query a všetky candidate lists. Potom sa replayuje baseline a candidate policy na labeled queries, porovná first divergence, vykoná bounded canary a overí second query z iného segmentu. Reranker fix sa neprijíma iba na pôvodnom sample.

## 19. Acceptance

Pozitívna acceptance vyžaduje versioned query plan, sparse/dense/structured candidates, mandatory authorization filters, explicit fusion, calibrated reranker, representative hard negatives, exact stage traces, sufficient-evidence behavior a retrieval aj business metrics.

Recovery acceptance vyžaduje identifikovaný first-divergence stage, known-good policy alebo cielenú opravu, paired replay, negative authorization test, multi-segment canary a druhú odlišnú query po promotion.

Forbidden acceptance je úspešný search request ako dôkaz relevance, raw score fusion bez calibration, click data ako ground truth bez bias correction, reranker score ako authority alebo top-k bez explicitného no-answer verdictu.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Vector stores a indexing](vector-stores-indexing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Context assembly a citation grounding →](context-assembly-citation-grounding.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
