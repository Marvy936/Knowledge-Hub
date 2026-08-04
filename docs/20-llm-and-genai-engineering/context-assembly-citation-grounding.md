# Context assembly a citation grounding

Context assembly premieňa ranked evidence candidates na konkrétny model input. Nie je to mechanické spojenie top-k textov. Assembler rozhoduje, ktoré passages sa zmestia do token budgetu, v akom poradí sa zobrazia, ako sa zachová authority a provenance, ako sa riešia duplicates a konflikty a ktoré citation labels sa priradia jednotlivým spans. Chyba v tejto vrstve môže znehodnotiť správny retrieval ešte pred generation.

V incidente `GENAI-SUPPORT-05` retrieval našiel správnu policy aj jej exception clause. Assembler však pri token-budget truncation ponechal hlavné pravidlo a odrezal vetu „neplatí pre žiadosti po manuálnom schválení“. Deduplication zároveň zlúčila starú a novú verziu dokumentu a citation labels sa po preusporiadaní neprepočítali. Model vytvoril fluent odpoveď s citáciou `S2`, no label ukazoval na iný chunk než text, ktorý odpoveď podporoval. Retrieval recall bol správny, ale context a citation integrity zlyhali.

## 1. Assembly subject

Exact assembly subject zahŕňa vstupný candidate set, authority a access verdict, deduplication mapping, token budget, packing policy, ordering, compression, citation-label generation, prompt release a generator context profile.

```yaml
context_assembly:
  request_id: rag-req-8421
  candidate_set_digest: sha256:8d10...
  assembler_generation: support-context-v9
  generator_tokenizer: provider-tokenizer-2026-07
  maximum_context_tokens: 18000
  reserved_output_tokens: 1800
  instruction_tokens: 2200
  history_tokens: 1600
  evidence_budget_tokens: 12400
  ordering_policy: authority-then-query-coverage-v4
  dedup_policy: canonical-source-version-v5
  compression_policy: extractive-only-v3
  citation_schema: claim-source-v6
```

Budget sa počíta tokenizerom a serialization formátom skutočného generatora. Character count ani embedding tokenizer nie sú spoľahlivá náhrada.

## 2. Input candidate contract

Assembler nesmie prijímať iba text a score. Každá evidence unit potrebuje identity, source version, authority, effective dates, access decision, content digest, structural path, retrieval provenance a citation offsets.

```yaml
context_candidate:
  chunk_id: policy/refunds/eu/v7#4.2@71bd
  source_id: policy/refunds/eu
  source_version: 7
  authority: approved-policy
  effective_from: 2026-07-01T00:00:00Z
  effective_to: null
  authorized: true
  content_digest: sha256:71bd...
  structural_path: [Refunds, Exceptions, Manual approval]
  retrieval_provenance:
    sparse_rank: 2
    dense_rank: 11
    reranked_rank: 1
  source_span:
    page: 12
    start: 842
    end: 1127
```

Text bez source identity nemožno bezpečne citovať, invalidovať po update ani diagnostikovať po incidente.

## 3. Trust a instruction boundary

Retrieved content je data, nie application instruction. Interný dokument môže obsahovať prompt injection, obsolete procedure alebo text určený pre človeka. Assembler preto serializuje evidence pod explicitným data contractom a system/developer instructions určujú, že commands v evidence sa nevykonávajú.

```text
trusted application instructions
→ untrusted user goal
→ authorized retrieved evidence as data
→ model answer contract
```

Delimiters, XML tags alebo JSON fields zlepšujú parsing a provenance, ale nevytvárajú bezpečnostný sandbox. Enforcement pre tools, authorization a output validation ostáva v aplikácii.

## 4. Token-budget accounting

Context window sa delí medzi instructions, conversation history, tool state, evidence a output reserve. Prekročenie limitu môže viesť k request erroru, implicitnému truncation alebo application-side orezaniu. Každý variant má odlišnú failure semantics.

```text
total input =
instructions
+ examples
+ history
+ query
+ tool state
+ evidence
+ serialization overhead
```

Output reserve je súčasť budgetu. Ak aplikácia naplní celý context inputom, model nemusí mať priestor na požadovaný structured output alebo citations. Token estimate sa validuje po finálnom renderi, nie iba nad raw passage textom.

## 5. Packing ako constrained optimization

Assembler vyberá evidence podľa relevance, authority, coverage, redundancy, token cost a required facets. Najvyššie reranker scores nemusia vytvoriť najlepší set: prvých päť chunks môže opakovať rovnakú vetu a nepokryť exception.

Jednoduchý packing objective možno vyjadriť:

```text
maximize:
relevance + authority + facet coverage + diversity

subject to:
token budget + authorization + validity + conflict policy
```

Greedy top-score packing je baseline. Produkčný policy môže najprv rezervovať miesto pre mandatory facets, potom dopĺňať ďalšie high-value passages. Pri multi-document answeri sa budget rozdeľuje podľa query planu, nie rovnomerne podľa dokumentov.

## 6. Evidence coverage

Query decomposition určuje required evidence facets. Pri refund policy to môže byť hlavné pravidlo, exception, effective date a escalation path. Assembly prejde iba vtedy, keď každý mandatory facet má platný passage alebo sa answer status nastaví na `insufficient_evidence`.

```yaml
coverage:
  policy_rule:
    status: covered
    source: S1
  exception_conditions:
    status: covered
    source: S2
  effective_date:
    status: covered
    source: S1
  escalation_path:
    status: missing
```

Chýbajúci facet sa nesmie nahradiť modelovou domnienkou. Aplikácia môže vrátiť čiastočnú odpoveď iba ak contract presne určuje, ktoré claims sú bezpečné.

## 7. Ordering

Poradie evidence ovplyvňuje model attention a konflikt resolution. Možnosti zahŕňajú relevance-first, authority-first, chronological, grouped-by-source alebo grouped-by-facet. Žiadne poradie nie je univerzálne.

Authority-first znižuje riziko, že draft prehluší approved policy. Chronological ordering pomáha pri incident timeline, ale najnovší document nemusí byť platný. Grouping podľa facet uľahčuje claim construction, no môže oddeliť passage od širšieho source contextu.

Ordering policy sa evaluačne testuje vrátane informácie na začiatku, v strede a na konci contextu. Zmena poradia je release change, pretože môže zmeniť generation behavior bez zmeny candidate setu.

## 8. Deduplication

Deduplication znižuje token waste, ale musí zachovať source-version semantics. Dva chunks s rovnakým obsahom z approved a draft dokumentu nie sú zameniteľné. Rovnako overlap z jedného dokumentu možno zlúčiť, iba ak sa zachová union source span a citation mapping.

```yaml
dedup_group:
  canonical_id: policy/refunds/eu/v7#4.2
  members:
    - chunk-17
    - chunk-18
  merged_span:
    start: 842
    end: 1281
  preserved_labels:
    - source_version
    - authority
    - effective_dates
```

Po merge alebo reorder sa labels regenerujú z canonical context listu. Ponechanie starého indexového čísla vedie k citation driftu.

## 9. Parent-child expansion

Retriever môže vybrať malý child chunk pre precision a assembler pridať parent section pre interpretáciu. Expansion musí používať rovnakú source generation, ACL a effective state.

```text
retrieved child
→ verify parent mapping generation
→ authorize parent
→ select bounded surrounding spans
→ preserve child highlight
```

Automatické pridanie celej parent stránky môže prekročiť budget alebo zaviesť unrelated instructions. Expansion sa viaže na maximum span a structural boundary.

## 10. Truncation

Naivné skrátenie `text[:N]` môže odrezať negáciu, exception, unit alebo záver tabuľky. Truncation sa vykonáva na semantic/structural boundaries a zaznamenáva sa, či bol passage complete.

```yaml
assembled_item:
  source: S2
  selected_tokens: 438
  original_tokens: 612
  truncation: tail_removed
  semantic_complete: false
```

Passage označený `semantic_complete: false` nemá podporovať claim, ktorý závisí od odstránenej časti. Pri critical evidence je vhodnejšie vyhodiť menej dôležitý passage než orezať rozhodujúcu podmienku.

## 11. Compression a summarization

Contextual compression odstráni nerelevantné vety alebo vytvorí summary. Extractive compression zachováva vybrané source spans; abstractive compression vytvára nový model-generated text. Druhá možnosť pridáva ďalšiu hallucination a provenance boundary.

```text
source passage
→ compression model/policy
→ compressed artifact
→ mapping na source spans
→ validation
```

Abstractive summary sa nesmie citovať ako verbatim source. Musí mať vlastnú generation identity a claim-support validation proti originálu. Pre high-risk policy odpovede je často bezpečnejší extractive selection.

## 12. Conflict detection

Ak context obsahuje protichodné authoritative claims, assembler nemá konflikt skryť výberom vyššieho score. Najprv sa aplikujú source precedence, approval state a effective-date rules. Nevyriešený konflikt sa odovzdá generatoru ako explicitný stav alebo sa request eskaluje.

```yaml
conflict:
  claim_key: refund_deadline_days
  sources:
    - id: S1
      value: 30
      effective_from: 2026-07-01
    - id: S4
      value: 45
      effective_from: 2026-06-01
  resolution: S1_supersedes_S4
  rule: latest-approved-effective
```

Relevance score nepatrí medzi authority precedence rules.

## 13. Citation labels

Citation label je stable reference na assembled evidence item, nie na pôvodný retrieval rank. Labels sa priraďujú po filtering, deduplication, ordering a compression, pretože až vtedy vznikne finálny context.

```yaml
citation_source:
  label: S2
  chunk_id: policy/refunds/eu/v7#4.2@71bd
  content_digest: sha256:71bd...
  displayed_span: "Manual approval exception applies ..."
  source_uri: policy://refunds/eu/v7#4.2
```

Label musí byť unique v requeste a response validator ho mapuje na rovnaký digest. URL bez digest/version môže po update ukazovať na iný obsah než ten, ktorý model videl.

## 14. Claim-level grounding

Grounding sa hodnotí na úrovni claims. Odpoveď môže mať správnu citáciu pri jednej vete a unsupported tvrdenie pri druhej. Claim extractor alebo structured response schema preto oddeľuje assertions.

```json
{
  "status": "grounded",
  "claims": [
    {
      "text": "Štandardná lehota je 30 dní.",
      "citations": ["S1"]
    },
    {
      "text": "Pri manuálnom schválení sa uplatní výnimka.",
      "citations": ["S2"]
    }
  ]
}
```

Validator kontroluje existenciu labelu, authorization, source validity a semantic support. Validný pointer ešte neznamená, že passage claim skutočne podporuje.

## 15. Citation precision a recall

Citation precision sa pýta, či uvedené citations podporujú claims. Citation recall sa pýta, či všetky claims, ktoré citation potrebujú, nejakú platnú citáciu majú. Obe metriky sú potrebné.

Model môže zvýšiť recall tým, že cituje všetko ku každej vete, ale precision klesne. Môže mať vysokú precision pri jednej citácii a zároveň pridať mnoho uncited claims. Eval preto používa claim-source judgments, nie iba počet labels.

## 16. Programmatic integrity validator

Deterministic validator vie overiť label mapping a základný response contract. Semantic support potrebuje ďalší grader alebo expert judgment.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Source:
    label: str
    content_digest: str
    authorized: bool
    effective: bool


def validate_citation_integrity(
    claims: list[dict[str, object]],
    sources: dict[str, Source],
) -> list[str]:
    errors: list[str] = []
    for claim_index, claim in enumerate(claims):
        citations = claim.get("citations", [])
        if not isinstance(citations, list) or not citations:
            errors.append(f"claim[{claim_index}] has no citations")
            continue
        for label in citations:
            if not isinstance(label, str) or label not in sources:
                errors.append(f"claim[{claim_index}] unknown citation {label!r}")
                continue
            source = sources[label]
            if not source.authorized or not source.effective:
                errors.append(f"claim[{claim_index}] invalid source {label}")
    return errors
```

Tento kód neoveruje entailment. Jeho dôkazná hranica je structural integrity, authorization a validity flags.

## 17. Prompt serialization

Context format musí byť explicitný a stable. Každý source môže obsahovať label, title, authority, effective dates a text. Fields určené pre model sa oddeľujú od interných metadata, ktoré model nepotrebuje.

```text
<SOURCE id="S2" authority="approved-policy" effective="2026-07-01">
Title: EU Refund Policy — Manual approval exception
Content: ...
</SOURCE>
```

Escaping zabráni rozbitiu serialization, ale text `</SOURCE>` v dokumente stále predstavuje untrusted content. Parser nesmie dôverovať model-generated reprodukcii source blocks; authoritative mapping zostáva server-side.

## 18. History a conversational context

Conversation history môže obsahovať staré model claims, ktoré nie sú evidence. Assembler ich nesmie miešať do source listu. Pri follow-up otázke sa z history vytvorí query context alebo resolved entities, ale authoritative claims sa znovu opierajú o current retrieval.

History truncation potrebuje state summary s provenance. Model-generated summary rozhovoru nie je dôkaz, že používateľ naozaj poskytol konkrétny fakt, pokiaľ sa nedá mapovať na pôvodnú message identity.

## 19. Streaming a commit boundary

Pri streaming odpovedi sa text môže zobraziť skôr, než sú citations a semantic validation kompletné. High-risk UI preto rozlišuje provisional stream a committed answer.

```text
stream tokens
→ parse complete structured response
→ validate citations a claims
→ commit user-visible answer
```

Ak sa streaming zobrazuje okamžite, UI musí vedieť stiahnuť alebo označiť nevalidnú odpoveď. Logovanie finish reason a incomplete state je súčasť acceptance.

## 20. Caching

Assembled-context cache key zahŕňa query plan, principal/tenant scope, candidate-set digest, assembler generation, source digests a token profile. Cache bez source generation môže po policy update vrátiť staré evidence.

Final-answer cache navyše zahŕňa prompt a generator release. Cache hit neobchádza authorization revalidation, ak sa principal alebo document ACL mohli zmeniť.

## 21. Observability

Trace zachytáva candidate input, removed items a dôvod, dedup groups, token estimates, selected spans, truncation flags, ordering, labels, conflict decisions, final prompt digest, generated claims a citation-validation results.

```yaml
assembly_trace:
  input_candidates: 18
  authorized_candidates: 15
  deduplicated_candidates: 11
  selected_sources: 6
  evidence_tokens: 8932
  missing_facets: []
  conflicts_resolved: 1
  truncated_sources: 1
  citation_integrity_errors: 0
```

Aggregate token usage bez selected source IDs nepomáha určiť, prečo model nedostal expected evidence.

## 22. Failure hypotheses a diagnostics

Pri unsupported claim sa skúma, či expected passage vstúpil do assemblera, nebol odstránený filtrom alebo dedupom, zmestil sa do budgetu, nebol semanticky neúplne orezaný, dostal správny label a model ho použil.

```text
candidate chýbal už po retrieveli
assembler vyhodil mandatory facet
wrong source version prežila dedup
truncation odstránil exception
compression zmenila význam
ordering zvýhodnil konflikt
citation label sa posunul
model vytvoril uncited claim
validator neodmietol unsupported answer
```

First divergence sa hľadá medzi candidate setom, assembled contextom a response claims, nie iba v final texte.

## 23. Containment a recovery

Containment môže zvýšiť reserved evidence budget, vypnúť abstractive compression, vynútiť one-source-per-version dedup, zablokovať answers s incomplete mandatory facetom alebo prepnúť na known-good assembler generation. Pri citation-integrity chybe sa answer nesmie publikovať, aj keď text pôsobí správne.

Recovery replayuje failing candidate set cez baseline a candidate assembler, porovná selected spans a labels, vykoná claim-level validation a bounded canary. Second-operation test použije inú query s konfliktom alebo boundary truncation, aby sa overila všeobecnosť opravy.

## 24. Acceptance

Pozitívna acceptance vyžaduje exact assembly manifest, tokenizer-aware budget, authority a coverage gates, version-aware deduplication, semantic-safe truncation, explicit conflict policy, stable citation mapping, claim-level grounding validation, no-answer behavior a stage observability.

Recovery acceptance vyžaduje rekonštrukciu candidate a context generations, identifikovaný first divergence, replay baseline/candidate, citation integrity a semantic support check, negative unauthorized-source test a druhú odlišnú query po promotion.

Forbidden acceptance je vloženie top-k textu ako hotový context bez authority a budget modelu, citation URL ako dôkaz supportu, abstractive summary ako source truth, truncation bez completeness flagu alebo odpoveď publikovaná pred validáciou citations.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Retrieval, hybrid search a reranking](retrieval-hybrid-search-reranking.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: RAG evaluation a retrieval diagnostics →](rag-evaluation-retrieval-diagnostics.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
