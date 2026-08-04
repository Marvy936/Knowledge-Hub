# Chunking, metadata a document processing

Document processing premieňa zdrojový artifact na retrieval-ready units. Chunking nie je iba rozrezanie textu na rovnaký počet znakov. Je to rozhodnutie, aká evidence unit sa bude indexovať, akú semantic a structural integritu si zachová, aké metadata a access controls zdedí a ako sa neskôr namapuje späť na authoritative source.

Zlý chunking môže stratiť nadpis, tabuľkový header, footnote, exception condition alebo effective date. Príliš veľké chunks znižujú retrieval precision a plytvajú context budgetom. Príliš malé chunks rozdelia claim a jeho podmienky. Overlap môže zlepšiť continuity, ale vytvoriť duplicate evidence a skresliť ranking.

V incidente `GENAI-SUPPORT-04` parser extrahoval refund policy z PDF po riadkoch. Tabuľkový stĺpec „výnimka“ sa pripojil k nesprávnej policy category a page footer sa stal súčasťou každého chunku. Vector search vracal obsahovo podobný chunk, ale jeho text už nereprezentoval pôvodný dokument. Root cause nebol embedding model; poškodenie vzniklo pred embedding generation.

## 1. Processing subject a generation

Každý derived document a chunk musí byť spätne dohľadateľný:

```yaml
document_processing:
  source_id: policy/refunds/eu/2026-07
  source_version: 7
  source_digest: sha256:91ca...
  source_format: pdf
  parser: layout-parser-v9
  ocr: disabled
  normalizer: text-normalizer-v6
  chunker: policy-semantic-v6
  metadata_schema: knowledge-metadata-v8
  processing_run: ingest-2026-08-04T04:20:11Z
```

Mutable názov parsera bez version/digest oslabuje reprodukovateľnosť rovnako ako mutable model alias.

## 2. Source acquisition

Processing začína acquisition contractom. Systém eviduje odkiaľ artifact pochádza, kto ho vlastní, či je approved, kedy nadobúda platnosť a aký je jeho content digest.

```text
authoritative source
→ immutable fetched artifact
→ checksum a metadata snapshot
→ parsing
```

Web page alebo API response sa uloží s retrieval timestampom, canonical URL/resource ID a relevantnými headers/version fields. Pri mutable source sa musí dať preukázať, ktorú podobu pipeline spracovala.

## 3. Parsing a layout recovery

Parser rekonštruuje logical structure z formátu. Pri HTML môže použiť DOM headings, lists a tables. Pri PDF musí riešiť reading order, columns, repeated headers/footers, page breaks, text boxes a scanned pages. Pri office documents potrebuje sections, tables, comments a hidden content policy.

```text
bytes
→ pages/elements
→ reading order
→ semantic blocks
→ normalized document tree
```

Plain-text extraction je vhodný baseline, nie universal truth. Dva parsers môžu z rovnakého PDF vytvoriť odlišný text. Parser quality sa testuje na reprezentatívnych layouts, nie iba na jednom sample.

## 4. OCR boundary

OCR sa používa pri scanned images alebo image-based text. OCR output je inference artifact s confidence a language profile. Nesmie sa zamieňať za source truth.

```yaml
ocr_span:
  page: 12
  bbox: [101, 220, 887, 420]
  text: "Refund exception applies after 30 days"
  confidence: 0.91
  engine: ocr-engine-v5
  language: en
```

Low-confidence spans môžu byť označené, vylúčené alebo smerované na review podľa risku. OCR chyba v čísle alebo negácii môže mať vysoký business dopad aj pri vysokej priemernej confidence.

## 5. Normalization

Normalization zjednocuje encoding, whitespace, Unicode, line breaks a boilerplate. Musí byť loss-aware. Odstránenie interpunkcie, case alebo table separators môže poškodiť identifiers a semantics.

```text
raw parsed block
→ Unicode normalization
→ controlled whitespace cleanup
→ boilerplate detection
→ structural annotation
```

Original span sa zachová alebo sa udržiava offset mapping, aby citation a debugging vedeli ukázať source representation.

## 6. Chunk identity

Chunk ID nesmie byť iba row auto-increment, ak sa má podporovať diff, update a deletion. Stabilná identity môže vychádzať zo source ID, structural path a content digest.

```yaml
chunk:
  chunk_id: policy/refunds/eu/2026-07#4.2@sha256:71bd...
  source_id: policy/refunds/eu/2026-07
  structural_path: ["Refunds", "EU", "Exceptions", "Late request"]
  ordinal: 17
  content_digest: sha256:71bd...
```

Pri zmene contentu vznikne nová generation alebo digest. Stable structural locator pomáha mapovať changed/unchanged chunks, ale nesmie zakryť semantic zmenu.

## 7. Chunking strategies

### Fixed-size chunking

Text sa delí podľa character alebo token budgetu s voliteľným overlapom. Je jednoduchý a predvídateľný, ale ignoruje document structure.

### Recursive separator chunking

Pipeline skúša odseky, vety a menšie separators, kým sa zmestí do limitu. Zachováva viac prirodzenej štruktúry, ale stále môže rozdeliť logical condition.

### Structure-aware chunking

Používa headings, sections, list items, table rows, code symbols alebo page elements. Je vhodné pre policy, manuals, code a structured documents.

### Semantic chunking

Hranice sa určujú podľa topic/embedding change alebo model-generated segmentation. Môže lepšie zachovať themes, ale pridáva model generation, cost a reproducibility concerns.

### Parent-child chunking

Malý child chunk slúži na retrieval precision, väčší parent na context. Mapping musí byť versioned a access-consistent.

Žiadna stratégia nie je univerzálna. Selection sa viaže na query types a evidence granularity.

## 8. Token budget a overlap

Chunk size sa meria tokenizerom relevantným pre embedding alebo generator pipeline, nie iba znakmi. Overlap pomáha pri boundary continuity:

```yaml
chunk_policy:
  target_tokens: 420
  maximum_tokens: 560
  overlap_tokens: 60
  preserve_headings: true
  preserve_table_rows: true
```

Overlap zvyšuje storage, indexing cost a duplicate candidates. Retrieval alebo context assembler musí deduplikovať highly overlapping passages. Vysoký overlap nesmie nahrádzať structure-aware segmentation.

## 9. Context preservation

Chunk potrebuje dostatok local contextu. Heading lineage, document title alebo section summary sa môže pripojiť ako metadata alebo controlled prefix.

```text
Document: EU Refund Policy
Section: Exceptions > Late request
Content: ...
```

Prefix vstupuje do embeddingu iba ak je to zámer. Ak metadata text zmení embedding semantics, musí byť súčasť chunker/embedding generation. Display context a embedding context nemusia byť identické, ale oba sa evidujú.

## 10. Tables

Tabuľky vyžadujú zachovanie headers, row/column relations, merged cells, units a footnotes. Naivná serializácia po cells môže vytvoriť nepravdivé pairs.

Možné representations:

```text
row-oriented textual records
structured JSON records
whole-table summary + row chunks
HTML/Markdown with header repetition
```

Pre lookup otázky je často vhodný row-level record s inherited headers. Pre comparative questions môže byť potrebný širší table context. Parser testuje round-trip sample proti vizuálnemu originálu.

## 11. Lists, code a conversations

Ordered procedure sa nemá deliť tak, aby chýbali prerequisites. Code chunking rešpektuje modules, classes, functions a imports. Chat alebo tickets zachovávajú speaker, timestamp, thread a resolution state.

```yaml
conversation_chunk:
  thread_id: ticket-8421
  messages: [31, 32, 33, 34]
  participants: [customer, agent]
  resolution_state: approved-refund
  contains_internal_note: false
```

Internal note a customer-visible text môžu mať odlišné access a usage policies.

## 12. Metadata schema

Metadata nie sú dekorácia. Riadi filtering, authorization, freshness, citations, deletion a evaluation.

```yaml
metadata:
  source_id: policy/refunds/eu/2026-07
  source_type: approved-policy
  owner: legal-operations
  tenant_scope: global-eu
  language: en
  effective_from: 2026-07-01T00:00:00Z
  effective_to: null
  classification: internal
  acl_groups: [support-eu]
  parser_generation: layout-parser-v9
  chunker_generation: policy-semantic-v6
```

Metadata values sa validujú proti schema. Free-form field names vedú k silent filter misses, napríklad `effectiveDate`, `effective_from` a `valid_since`.

## 13. Metadata authority a inheritance

Niektoré metadata pochádzajú zo source registry, iné z parsera a iné z model-generated classification. Musí byť jasná authority:

```yaml
metadata_provenance:
  owner: source-registry
  classification: security-catalog
  language: detector-v4
  section_title: layout-parser-v9
  topic_labels: classifier-v3
```

Model-generated topic label môže pomôcť retrievalu, ale nesmie určovať authorization. ACL a tenant scope sa dedia z authoritative source alebo explicitných resource rules.

## 14. Incremental updates

Pri update sa porovná source digest a document tree. Unchanged chunks možno reuse-núť iba ak sú kompatibilné parser/chunker/embedding generations.

```text
old source generation
+ new source generation
→ structural/content diff
→ delete obsolete chunks
→ preserve compatible chunks
→ embed changed chunks
→ build/mutate candidate index
```

Zmena chunker policy môže vyžadovať full reprocessing aj pri rovnakom source content. Zmena metadata schema môže vyžadovať backfill.

## 15. Deletion a tombstones

Delete lifecycle musí pokryť derived artifacts:

```text
source delete/revoke
→ chunk tombstones
→ vector/index deletion
→ cache invalidation
→ replica propagation
→ retrieval forbidden test
```

Soft-delete field bez mandatory retrieval filteru je nedostatočný. Audit testuje, že deleted content sa nevráti exact ani ANN searchom a nie je dostupný cez parent-child mapping.

## 16. Quality evaluation

Processing eval obsahuje:

```yaml
processing_metrics:
  - extraction_character_coverage
  - heading_hierarchy_accuracy
  - table_relation_accuracy
  - chunk_boundary_quality
  - metadata_schema_validity
  - acl_inheritance_accuracy
  - citation_offset_accuracy
  - stale_or_deleted_chunk_rate
```

End-to-end retrieval eval je stále potrebný. Parser môže mať vysokú text coverage, ale rozbiť critical table relation. Chunking môže vyzerať čitateľne, ale znížiť evidence recall.

Golden document set obsahuje simple text, multi-column PDF, scanned page, table, footnotes, multilingual content, long section, version update a deletion case.

## 17. Observability

Ingestion run loguje source count, changed/unchanged/deleted documents, parser errors, OCR pages, chunk counts a size distribution, metadata failures, embedding failures, index mutation a promotion status.

Sample-level debug umožní zobraziť:

```text
source page/span
→ parsed element
→ normalized text
→ chunk boundaries
→ metadata
→ vector/index identity
```

Sensitive content sa chráni, ale provenance a digests zostávajú dostupné ownerom incidentu.

## 18. Failure hypotheses a troubleshooting

Pri retrieval miss sa skúma, či source bol fetched, parser zachoval evidence, chunker ju nerozdelil, metadata filter ju nevylúčil, embedding bol vytvorený a chunk je v aktívnom indexe.

Pri nesprávnej citácii sa overí offset mapping a source version. Pri duplicated evidence sa skúma overlap, repeated headers, source duplicates a parent-child expansion.

Porovnávanie embeddings nemá zmysel, kým sa nepotvrdí, že text a metadata pred embeddingom sú správne.

## 19. Acceptance

Pozitívna acceptance vyžaduje immutable source snapshot alebo identitu, versioned parser/normalizer/chunker, stable chunk a source mapping, schema-valid metadata s provenance, ACL inheritance, update/delete lifecycle, representative golden documents a end-to-end retrieval evaluation.

Recovery acceptance vyžaduje replay failing source cez candidate pipeline, diff derived document tree a chunks, rebuild candidate index, retrieval/citation test a second-document operation.

Forbidden acceptance je počet vytvorených chunks ako dôkaz kvality, plain-text extraction ako univerzálne správny parsing, OCR confidence ako correctness, overlap ako náhrada semantic boundaries alebo soft delete bez retrieval verification.
