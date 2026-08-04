# RAG evaluation a retrieval diagnostics

RAG evaluation musí oddeliť kvalitu source a ingestion vrstvy, retrievalu, context assembly, generation, citations a business outcome-u. Jedno answer score nedokáže určiť, či správna odpoveď vznikla z relevantného evidence alebo náhodne z parametric knowledge. Rovnako nesprávna odpoveď nehovorí, či zlyhal retriever, assembler, generator alebo validator.

V incidente `GENAI-SUPPORT-05` tím používal synthetic questions generované z rovnakých chunks, ktoré boli neskôr indexované. Eval obsahoval iba answerable cases a grader hodnotil podobnosť final textu s reference answer. Candidate systém dosiahol vysoké skóre, hoci lexical rewrite strácal policy identifiers, reranker preferoval staré dokumenty a citations ukazovali na nesprávne spans. Dataset nemal retrieval judgments, unanswerable queries, conflict cases ani temporal split, preto meral schopnosť zopakovať známy text, nie produkčný evidence path.

## 1. Eval subject a generation

Eval run je reprodukovateľný iba ak identifikuje dataset, labels, split, corpus a index generation, retrieval policy, assembler, prompt, generator, grader a scoring code.

```yaml
rag_eval_run:
  suite: support-rag-eval-2026-08-04
  dataset_digest: sha256:4a21...
  judgment_generation: legal-review-v6
  split: temporal-holdout-2026-q3
  corpus_generation: support-policy-2026-08-04.2
  index_generation: support-hybrid-2026-08-04.2
  retrieval_policy: hybrid-rrf-rerank-v8
  assembler: support-context-v9
  prompt: support-grounded-v20
  generator: support-pro-2026-07-28
  citation_validator: claim-source-v6
  grader_bundle: rag-graders-v10
  scoring_code: git:9af32c1
```

Zmena grader promptu alebo relevance judgments vytvára inú eval generation. Výsledky z dvoch behov nemožno porovnávať iba podľa rovnakého suite name.

## 2. Evaluation contract

Eval začína rozhodnutím, aký user a business outcome systém podporuje a čo je forbidden. Pre policy assistant nestačí merať prirodzene znejúcu odpoveď. Contract zahŕňa správnu policy version, authorization, evidence support, no-answer pri chýbajúcom evidence a bezpečnú eskaláciu pri konflikte.

```yaml
success_contract:
  correct_policy_version: required
  unauthorized_retrieval_rate: 0
  factual_claims_cited: required
  citation_support: required
  unanswerable_abstention: required
  conflicting_evidence_escalation: required
  business_resolution: measured
```

Metrika bez decision rule nie je gate. Tím musí určiť minimum per segment, forbidden rates a confidence interval alebo sample-size boundary.

## 3. Dataset unit

Eval item potrebuje viac než question a reference answer. Obsahuje query context, authenticated scope, relevant a forbidden sources, expected evidence facets, answerability, reference claims a business action.

```json
{
  "case_id": "policy-rf-eu-042-017",
  "query": "Platí RF-EU-042 po manuálnom schválení?",
  "request_time": "2026-08-04T07:30:00Z",
  "principal": {"tenant": "eu-support", "groups": ["support-eu"]},
  "answerable": true,
  "relevant_sources": [
    "policy/refunds/eu/v7#4.2",
    "policy/refunds/eu/v7#effective-date"
  ],
  "hard_negatives": [
    "policy/refunds/eu/v6#4.2",
    "policy/refunds/uk/v7#4.2"
  ],
  "forbidden_sources": ["policy/refunds/vip-internal/v3"],
  "required_facets": ["standard_rule", "manual_approval_exception"],
  "reference_claims": [
    {"claim": "Manual approval activates the exception", "source": "policy/refunds/eu/v7#4.2"}
  ]
}
```

Táto unit umožňuje retrieval, context, answer, citation a security scoring nad tým istým case.

## 4. Dataset construction

Dataset kombinuje production-derived cases, expert-authored cases, incident regressions a controlled synthetic augmentation. Production queries zlepšujú distribution fidelity, ale môžu obsahovať privacy, selective labels a feedback loops. Expert cases pokrývajú critical boundaries, no nemusia reprezentovať frekvenciu. Synthetic generation zvyšuje coverage, ale môže kopírovať wording dokumentu a urobiť retrieval neprirodzene jednoduchým.

Každý case má provenance a generation method. Synthetic query sa reviduje tak, aby neobsahovala answer alebo exact chunk phrase, ak production users takto nehovoria. Incident cases sa uchovávajú ako permanent regression set, no neprepisujú celý benchmark na zopár známych failures.

## 5. Splits a leakage

Random split na úrovni chunks môže umiestniť takmer identické passages z jedného dokumentu do train aj test setu. Pri retrieval a fine-tuning evale sa preto používajú source-level, version-level, tenant-level alebo temporal splits podľa intended generalization.

```text
training documents: policy versions <= 2026-06
validation: selected 2026-07 versions
test: unseen 2026-08 versions a incident cases
```

Temporal split overuje behavior pri novom knowledge. Source-family split overuje prenos na nové templates alebo domains. Pri multilingual workload sa language segment nesmie stratiť v aggregate average.

## 6. Relevance judgments

Retrieval ground truth môže byť binary, graded alebo facet-based. Binary label určuje relevant/irrelevant. Graded judgment rozlišuje napríklad authoritative direct answer, supporting context, partially relevant a irrelevant. Facet-based judgment určuje, ktorú časť otázky document pokrýva.

```yaml
judgment:
  document: policy/refunds/eu/v7#4.2
  relevance_grade: 3
  facets: [manual_approval_exception]
  authority_valid: true
  effective_valid: true
  annotator: legal-expert-12
  adjudicated: true
```

High semantic similarity nemôže nahradiť authority a validity judgment. Starý dokument môže dostať vysokú topical relevance, ale nulovú usable-evidence relevance.

## 7. Retrieval metrics

Recall@k meria, koľko relevantných evidence units sa objavilo v top-k. Precision@k meria podiel relevantných jednotiek medzi vrátenými. Hit rate odpovedá, či sa našiel aspoň jeden relevantný source. MRR zvýhodňuje prvý relevantný result. nDCG pracuje s graded relevance a penalizuje horšie poradie.

```text
recall@k = relevant retrieved at k / all relevant
precision@k = relevant retrieved at k / k
reciprocal rank = 1 / rank first relevant
```

Pri multi-facet otázkach hit rate môže byť zavádzajúci: jeden relevantný document nestačí, ak chýba exception. Preto sa meria facet recall a evidence-set completeness.

Praktický deterministic výpočet základných metrík:

```python
from collections.abc import Sequence


def recall_at_k(
    retrieved: Sequence[str],
    relevant: set[str],
    k: int,
) -> float:
    if not relevant:
        raise ValueError("relevant set must not be empty")
    found = set(retrieved[:k]) & relevant
    return len(found) / len(relevant)


def reciprocal_rank(
    retrieved: Sequence[str],
    relevant: set[str],
) -> float:
    for rank, document_id in enumerate(retrieved, start=1):
        if document_id in relevant:
            return 1.0 / rank
    return 0.0
```

Kód nehodnotí graded relevance, authority ani duplicates. Produkčný scorer musí používať canonical identity a judgment semantics suite.

## 8. Stage-wise retrieval diagnostics

Finálny rank sa rozkladá podľa stages. Pre každý expected source sa zaznamená, či bol v sparse, dense a structured listoch, ako ho fusion preusporiadala, či prežil filters, dedup a reranking a či bol vybraný assemblerom.

```yaml
expected_source_trace:
  source: policy/refunds/eu/v7#4.2
  sparse_rank: 1
  dense_rank: 24
  structured_rank: 1
  fused_rank: 3
  after_filter: 3
  reranked_rank: 2
  assembled: false
  drop_reason: token_budget
```

Tento record ukazuje, že retriever source našiel a failure vznikol až pri assembly. Bez stage trace by tím zbytočne menil embeddings.

## 9. Context metrics

Context precision hodnotí, koľko vloženého contextu je relevantné alebo podporuje answer. Context recall hodnotí, či context obsahuje všetky required evidence. Duplication rate meria redundantné spans, authority-valid rate podiel platných sources a token efficiency podiel budgetu použitý na required facets.

Automatický context grader môže označiť relevantné passages, ale kalibruje sa proti expert judgments. Grader môže považovať zastaraný dokument za relevantný, ak nedostane effective-date metadata.

Context metric sa počíta po finálnom assembly, nie nad reranked top-k. Iba assembled text mal generator k dispozícii.

## 10. Answer correctness

Answer correctness porovnáva generated claims s reference facts alebo expert verdictom. Exact string match je vhodný pre bounded extraction, no nie pre voľnú formuláciu. Semantic similarity môže akceptovať fluent paraphrase, ale aj prehliadnuť negáciu alebo nesprávne číslo.

Pre policy answers je robustnejší structured claim comparison:

```yaml
expected:
  standard_deadline_days: 30
  manual_approval_exception: true
actual:
  standard_deadline_days: 30
  manual_approval_exception: false
```

Jedna chybná boolean exception môže mať väčší business impact než vysoká lexical similarity zvyšku odpovede.

## 11. Faithfulness a groundedness

Faithfulness sa pýta, či claims vyplývajú z poskytnutého contextu. Nehodnotí automaticky, či context je authoritative alebo pravdivý. Model môže byť dokonale faithful k starému dokumentu a stále odpovedať nesprávne pre current policy.

Preto sa rozlišuje:

```text
context faithfulness
source authority/validity
answer correctness
```

Grader dostane claim, cited passage a metadata. Bez source version a effective dates vie hodnotiť textový support, nie business truth.

## 12. Citation metrics

Citation integrity overuje, že labels existujú a mapujú na context digest. Citation precision hodnotí podporu cited claims. Citation recall hodnotí, či claims, ktoré potrebujú evidence, majú platné citations. Citation completeness môže byť required gate pre factual answer.

```yaml
citation_result:
  integrity: pass
  precision: 0.92
  recall: 0.81
  unsupported_claims: 2
  invalid_source_claims: 0
```

Vysoká precision pri nízkom recall znamená, že uvedené citations sú dobré, ale časť tvrdení ostala bez evidence.

## 13. No-answer a conflict evaluation

Eval musí obsahovať unanswerable, unauthorized a conflicting cases. Systém sa hodnotí podľa správneho statusu, nie podľa toho, či vždy vytvorí text.

```text
answerable + sufficient evidence → grounded answer
unanswerable → insufficient_evidence
unauthorized → unauthorized_scope
conflicting current authority → conflict/escalation
retrieval outage → retrieval_failure
```

Abstention rate sama osebe nie je kvalita. Príliš časté odmietanie znižuje usefulness; príliš nízke vytvára unsupported answers. Potrebná je confusion matrix per segment.

## 14. Security evaluation

Security cases testujú cross-tenant retrieval, revoked documents, indirect prompt injection, malicious metadata a cache isolation. Metric `unauthorized_retrieval_rate` musí byť nulová v testovaných boundaries a evidence IDs sa nesmú objaviť ani v hidden trace dostupnom neautorizovanému operatorovi.

Prompt-injection eval rozlišuje retrieval event a model behavior. Ak malicious document vstúpil do contextu, retrieval/ingestion control zlyhal aj vtedy, keď generator instruction ignoroval. Ak document bol oprávnene relevantný, ale jeho command zmenil tool behavior, zlyhala trust/tool boundary.

## 15. LLM-as-a-judge

Model grader škáluje evaluation voľného textu, no je ďalší model s bias, prompt sensitivity a version drift. Môže preferovať verbose odpovede, zdieľať chyby candidate modelu alebo zle chápať domain exceptions.

Grader sa kalibruje na expert-labeled sample. Meria sa agreement, confusion per label a stability pri prompt/model zmene. High-risk gates kombinujú deterministic checks, expert judgments a model grader; jeden judge score nie je authority.

```yaml
grader_release:
  model: judge-pro-2026-07-15
  prompt: rag-faithfulness-v12
  rubric: legal-support-v6
  calibration_set: rag-judge-calibration-2026-08
  expert_agreement: 0.86
```

Grader output a rationale sa ukladajú ako derived evidence, nie ground truth.

## 16. Human evaluation

Expert review je potrebný pri nuanced authority, policy conflict a business impact. Rubric rozdeľuje correctness, completeness, evidence support, tone a action safety. Annotators dostanú rovnaké source generation a blinded candidate identity.

Inter-annotator disagreement nie je noise na automatické odstránenie. Môže odhaliť nejasnú policy alebo rubric. Adjudication result a reason sa versionujú. Ak experts nevedia dosiahnuť consensus, model nemá dostať falošne presný target.

## 17. Counterfactual a ablation tests

Ablation izoluje contributions jednotlivých stages:

```text
dense only
sparse only
hybrid without reranker
hybrid with reranker
baseline assembler
candidate assembler
```

Counterfactual test odstráni required passage a overí, či systém správne abstainuje. Vloženie relevantného, ale neplatného dokumentu testuje authority. Zmena order testuje position sensitivity. Tieto experimenty pomáhajú odlíšiť causal improvement od korelácie.

## 18. Offline, shadow a online evaluation

Offline eval je reprodukovateľný a lacný, ale nemusí zachytiť live traffic, latency, user interactions a delayed outcomes. Shadow traffic používa production queries bez user-visible candidate answer a nesmie vykonávať write tools. Online canary meria reálny journey a business outcome.

```text
offline regression gate
→ shadow retrieval a generation
→ bounded canary
→ user/business outcome
→ promotion alebo rollback
```

Click-through rate nie je automaticky correctness. Online metrics zahŕňajú resolution, corrections, escalation, complaint a policy violation.

## 19. Statistical interpretation

Rozdiel dvoch aggregate scores môže byť sample noise. Report obsahuje count, segment distribution, confidence interval alebo bootstrap estimate a paired differences na rovnakých cases. Critical forbidden failures sa neagregujú do priemeru.

```yaml
segment_result:
  segment: policy-exception
  cases: 184
  baseline_recall_at_10: 0.91
  candidate_recall_at_10: 0.94
  paired_improvement_cases: 19
  paired_regression_cases: 8
  forbidden_failures: 1
```

Candidate s lepším average recall, ale jedným cross-tenant leakom, gate neprejde.

## 20. Regression corpus

Každý potvrdený incident vytvára regression cases na first-divergence stage a end-to-end journey. `GENAI-SUPPORT-05` preto pridá exact-ID rewrite case, stale-policy hard negative, truncated exception a citation-remap case.

Regression set sa nesmie stať jediným benchmarkom. Overfitting na známe cases môže zlepšiť gate bez generalizácie. Suite kombinuje stable core, rotating holdout a fresh production sample.

## 21. Diagnostic workflow

Pri regressione sa nezačína fine-tuningom. Najprv sa porovnajú exact manifests a stage outputs:

```text
source a labels
→ ingestion/chunks
→ sparse/dense/structured candidates
→ filters/fusion/reranking
→ assembled context
→ claims/citations
→ validators
→ business outcome
```

Prvý rozdiel medzi baseline a candidate určuje hypothesis. Ak relevantný source chýba v dense listoch, skúma sa embedding/query/index. Ak je v reranked top-k, ale nie v contextu, skúma sa assembler. Ak context je správny a claim unsupported, skúma sa generator/prompt/validator.

## 22. Automated eval pipeline

CI môže validovať schema, spustiť bounded dataset a publikovať per-stage artifacts. Production-scale eval býva samostatný workflow s pinned environment a cost limits.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class EvalVerdict:
    recall_at_10: float
    citation_precision: float
    unauthorized_retrievals: int
    forbidden_failures: int


def passes_gate(verdict: EvalVerdict) -> bool:
    return (
        verdict.recall_at_10 >= 0.90
        and verdict.citation_precision >= 0.95
        and verdict.unauthorized_retrievals == 0
        and verdict.forbidden_failures == 0
    )
```

Thresholdy sú workload-specific. Kód nevypovedá o správnosti vstupných labels ani reprezentatívnosti datasetu.

## 23. Observability a result registry

Eval registry ukladá suite a run identity, manifests, artifacts, aggregate a segment metrics, failed cases, grader releases, cost a verdict. Dashboard umožní drill-down z metric regression na exact case a stage trace.

Result bez dataset digestu a candidate release sa nesmie použiť na promotion. Retention policy zachová minimálne promotion evidence a incident regressions. Sensitive query text môže byť redacted, ale case identity a derived digests musia zostať auditovateľné.

## 24. Failure hypotheses

Pri príliš dobrom score sa skúma leakage, duplicate cases, synthetic wording overlap, judge bias, missing negatives alebo evaluation na rovnakom corpus snapshot-e ako training data. Pri nestabilnom score sa skúma stochastic generation, grader drift, non-pinned index, sampling a small segments.

Pri offline-online gap sa skúma traffic distribution, conversational history, latency/timeouts, cache, user behavior a delayed labels. „Eval nefunguje“ nie je root cause; musí sa určiť, ktorá assumption medzi datasetom, scorerom a live outcome neplatí.

## 25. Containment a recovery

Containment pri nespoľahlivom evale zastaví promotion, zachová candidate artifacts a vráti gate na poslednú calibrated suite. Nemá zmysel znižovať threshold iba preto, aby release prešiel.

Recovery opraví labels, scorer alebo dataset split, znovu prepočíta baseline aj candidate rovnakou generation a preskúma zmenu verdictu. Second-operation test pridá fresh holdout alebo incident case, ktorý nebol použitý pri oprave.

## 26. Acceptance

Pozitívna acceptance vyžaduje versioned representative dataset, source/facet judgments, answerable aj unanswerable cases, per-stage retrieval/context/generation/citation/security metrics, calibrated graders, segment gates, paired comparison a online outcome plan.

Recovery acceptance vyžaduje identifikovanú evaluation chybu alebo system first divergence, opravené labels/scorer/manifests, rerun baseline a candidate, fresh holdout a potvrdenie, že forbidden failure rate ostáva nulová.

Forbidden acceptance je answer-only semantic score ako dôkaz RAG kvality, synthetic questions z indexovaných chunks bez leakage kontroly, LLM judge bez expert calibration, aggregate average zakrývajúci security failure alebo promotion podľa jedného benchmarku bez stage diagnostics.
