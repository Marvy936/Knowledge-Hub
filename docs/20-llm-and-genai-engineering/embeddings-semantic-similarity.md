# Embeddings a semantic similarity

Embedding je vektorová reprezentácia objektu, napríklad textu, obrázka, audio segmentu, produktu alebo entity. Embedding model mapuje input do priestoru, v ktorom geometrická blízkosť podľa zvolenej metriky aproximuje relationship naučenú training objective. Semantic similarity je jedna možná interpretácia tohto relationshipu, nie univerzálna vlastnosť každého embeddingu. Blízke vektory nepreukazujú pravdivosť, identity, authorization ani rovnaký business intent.

V incidente `GENAI-SUPPORT-01` assistant vyhľadával runbooky podľa cosine similarity. Query „reset zákazníckeho hesla“ bola blízko dokumentu o resetovaní service-account credentialov, pretože oba texty zdieľali security a reset language. Retrieval threshold bol prevzatý z anglického benchmarku, dokumenty boli indexované staršou embedding generation a query encoder dostal iný instruction prefix. Vector store vrátil presvedčivo podobný, ale autoritatívne nesprávny dokument. Root cause bolo zamieňanie geometric similarity za task relevance a identity.

## 1. Čo embedding reprezentuje

Model vytvára dense vector s pevnou dimension. Význam jednotlivých súradníc spravidla nie je ľudsky interpretovateľný. Informácia je distribuovaná v celom priestore a vzniká training objective, dátami, poolingom a normalization.

```text
input
→ tokenizer/preprocessing
→ embedding model
→ pooling alebo selected representation
→ optional normalization
→ vector
```

Rovnaký text s iným modelom, prompt prefixom, poolingom alebo normalization je iný embedding subject. Vectors z nekompatibilných spaces sa nesmú porovnávať ani miešať v jednom indexe bez explicitnej transformácie a parity evidence.

## 2. Word, token, sentence a document embeddings

Token embeddings sú interné vectors vocabulary items pred contextual mixingom. Contextual token representations závisia od celej sequence. Sentence/document embedding komprimuje variable-length input do jedného alebo viacerých vectors vhodných pre retrieval, clustering alebo classification.

Naivný average token hidden states nemusí vytvárať kvalitný semantic space. Sentence-BERT ukázal training architecture určenú pre sentence-level similarity, kde vectors možno efektívne porovnávať cosine similarity. Embedding model sa preto vyberá podľa tasku, nie podľa toho, že základný Transformer vie produkovať hidden states.

## 3. Exact embedding subject

Index a query musia zdieľať complete contract:

```yaml
embedding_subject:
  model_id: org/embed-model-v7
  model_revision: 4f22c1a
  tokenizer_revision: 2b9910
  dimension: 1024
  pooling: mean
  normalization: l2
  query_prefix: "query: "
  document_prefix: "passage: "
  preprocessing_generation: support-doc-v5
  distance_metric: cosine
```

Asymmetric retrieval models môžu očakávať odlišné query a document instructions. Vynechanie prefixu nemení API shape, ale mení vector semantics. Index metadata musí niesť generation; model update vyžaduje nový index alebo plne riadenú migration.

## 4. Cosine similarity

Cosine similarity meria uhol medzi vektormi:

```text
cos(a, b) = (a · b) / (||a|| ||b||)
```

Pri L2-normalized vectors sa dot product rovná cosine similarity. Euclidean distance medzi normalized vectors je monotónne previazaná s cosine, ale index configuration musí stále zodpovedať training/retrieval contractu.

Hodnota `0.82` nemá univerzálny význam. Distribution scores závisí od modelu, domainu, query length, language a corpusu. Threshold sa kalibruje na labeled relevance datasete a často sa používa ranking top-k plus reranking, nie absolútny semantic truth test.

## 5. Similarity, relevance a identity

Similarity znamená blízkosť podľa embedding objective. Relevance znamená, že document pomáha vyriešiť konkrétny task. Identity znamená, že ide o ten istý authoritative object. Tieto pojmy sa nesmú zamieňať.

Dva incidenty môžu byť podobné, ale patriť do iného environmentu. Dve policies môžu používať rovnaký jazyk, ale jedna je deprecated. Duplicate detection môže vyžadovať exact hashes a metadata, nie embedding similarity.

Retrieval preto kombinuje vector score s filters pre tenant, product, version, validity interval, access policy a document type.

## 6. Praktické encoding a similarity

Sentence Transformers interface môže vytvoriť normalized embeddings a vypočítať similarity:

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer(
    "org/support-embedding-model",
    revision="exact-revision",
)

texts = [
    "Reset používateľského hesla v zákazníckom portáli.",
    "Rotácia service-account credentialov.",
]

vectors = model.encode(
    texts,
    normalize_embeddings=True,
)

score = float(np.dot(vectors[0], vectors[1]))
print(score)
```

Kód je interface example. Production path pinne package/model revisions, batch parameters, device/precision a preprocessing. Score bez corpus a relevance labels nie je acceptance verdict.

## 7. Pooling a truncation

Sentence embedding môže používať CLS-like token, mean pooling, weighted pooling alebo model-specific strategy. Pooling je súčasť weights/training contractu. Zmena pooling bez retrainingu môže zničiť geometry.

Embedding input má context limit. Long document sa môže ticho truncate-nuť, takže vector reprezentuje iba začiatok. Document processing musí chunkovať alebo používať long-document strategy a logovať retained offsets.

## 8. Normalization a metric compatibility

Niektoré models sú trénované pre cosine/dot product s normalized vectors, iné využívajú magnitude. Index nesmie automaticky normalizovať bez contractu. Query normalization a document normalization musia byť konzistentné.

Ak vector DB používa `inner_product`, ale application interpretuje score ako cosine pri nenormalizovaných vectors, ranking sa môže meniť podľa normy namiesto direction. Migration test porovná exact neighbors a relevance, nie iba úspešný insert.

## 9. Indexing a approximate search

Exact nearest-neighbor search je drahý pri veľkom corpuse. ANN indexy používajú approximations a tuning trade-offs medzi recall, latency, memory a build time. HNSW, IVF alebo vendor-specific index sú retrieval runtime generation.

Embedding quality a ANN recall sú samostatné. Relevantný document môže mať dobrý vector score, ale index ho nevráti pre nízky search budget. Evaluation preto meria candidate recall pred rerankingom aj end-to-end answer outcome.

## 10. Batch a serving consistency

Offline indexing a online query encoding musia používať rovnaké model/tokenizer/preprocessing generation. Quantization, precision alebo runtime engine môžu mierne meniť vectors; parity threshold sa stanoví empiricky.

Index build manifest eviduje document IDs, content digests, metadata filters, embedding generation, vector count, dimension, metric a ANN config. Query trace nesie index generation a returned IDs/scores.

## 11. Multilingual a domain behavior

Multilingual model môže mapovať languages do spoločného priestoru, ale coverage a score distributions nemusia byť rovnaké. Domain abbreviations, logs, code, medical/legal terms alebo Slovak inflection môžu vyžadovať domain eval alebo adaptation.

English threshold prenesený na slovenský corpus je hypothesis, nie policy. Eval dataset musí obsahovať languages, negative near-matches a access/version constraints z reálneho use caseu.

## 12. Embedding drift a reindexing

Model update mení vector space. Staré document vectors a nové query vectors sa spravidla nesmú kombinovať, aj keď dimension zostane rovnaká. Blue/green index migration vytvorí novú generation, backfillne vectors, porovná recall/latency a atomicky presunie query routing.

Document update bez re-embeddingu vytvára stale index. Delete/retention musí odstrániť vector aj metadata/cached copies podľa policy.

## 13. Security a privacy

Embeddings môžu uchovávať informácie o inpute a nie sú automaticky anonymné. Access control sa vykonáva pred alebo počas retrievalu; post-filter po načítaní unauthorized textu môže stále leaknúť cez logs alebo model context.

Attacker môže manipulovať content tak, aby zvýšil similarity, alebo vložiť documents do corpusu. Ingestion potrebuje provenance, authorization a content validation. Vector search nie je security boundary.

## 14. Evaluation

Embedding evaluation používa labeled pairs/triplets, retrieval queries s relevant document sets, hard negatives a production-like filters. Metrics môžu zahŕňať recall@k, MRR, nDCG, classification quality, latency a index cost.

Offline similarity benchmark nestačí pre RAG. End-to-end eval kontroluje, či retrieved context bol authoritative, cited a použitý správne. High recall s nesprávnym top-1 môže stále viesť k chybnému answer.

## 15. Failure hypotheses

Wrong retrieval môže byť embedding model, prefix, truncation, stale index, metadata filter, ANN recall, corpus quality alebo reranker. Zero results môže byť threshold, access filter, language mismatch alebo query encoding failure.

Troubleshooting porovná exact query vector generation, index manifest, candidate list pred filters/rerankingom a labeled relevance. Reindex bez preservation starého generation znemožní reprodukciu.

## 16. Recovery a acceptance

Containment môže zvýšiť human verification, obmedziť corpus na authoritative sources, znížiť auto-action scope alebo route-nuť na keyword/hybrid fallback. Recovery obnoví known-good embedding/index generation a replayne relevance dataset vrátane hard negatives.

Pozitívna acceptance vyžaduje pinned embedding subject, metric compatibility, calibrated retrieval evaluation, metadata authorization, index manifest a end-to-end grounding. Forbidden acceptance je vysoký cosine score, pekná 2D visualization alebo úspešný vector DB query ako proof relevance či truth.

Second-operation test znovu zakóduje golden inputs a overí vector parity a neighbors. Potom vykoná blue/green reindex s novou generation a preukáže, že routing, rollback a delete semantics sú deterministické.
