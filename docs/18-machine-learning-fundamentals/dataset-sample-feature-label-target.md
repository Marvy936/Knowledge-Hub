# Dataset, sample, feature, label a target

Machine learning model nevidí „zákazníkov“, „platby“ ani „fraud“ tak, ako ich chápe business. Vidí konkrétnu reprezentáciu observations v datasete. Ak tím nesprávne určí, čo je jeden sample, kedy boli features známe alebo čo label skutočne znamená, môže vytvoriť numericky úspešný model pre nesprávny problém. Dataset contract je preto súčasťou business correctness, nie iba prípravný CSV súbor pred trainingom.

Táto kapitola pokračuje incidentom `ML-PAY-83`. Atlas Payments chcel prioritizovať merchant operations pre manuálny review. Pôvodný dataset však používal payment attempts ako samples, hoci jedna business operation mohla mať viac retries. Feature `final_settlement_status` vznikala až po prediction time a label `needs_review` reprezentoval historickú routing policy, nie potvrdenú stratu. Model sa tak učil z nesprávnej observation unit, budúcich informácií a nejednoznačného targetu.

## 1. Dominantný data-to-learning lifecycle

Dataset nie je ľubovoľná tabuľka s rows a columns. Je to versionovaný výber observations z definovanej population, vytvorený podľa extraction time, inclusion/exclusion rules, entity a time identity, feature computation a label policy. Training correctness začína tým, že každá row predstavuje to, čo tvrdí dataset manifest.

```text
business decision a prediction time
→ population a observation unit
→ source systems a authority
→ entity/time join contract
→ samples a features dostupné v cutoff-e
→ label observation window a source
→ dataset snapshot a schema
→ split assignment
→ training/evaluation
→ production feature parity a outcome evidence
```

Každý krok môže zmeniť meaning dát bez zmeny column names. Recomputed table po oprave source records nie je tá istá dataset generation. Rovnaký SQL query nad mutable source bez snapshotu nemusí byť reprodukovateľný. Dataset musí mať immutable manifest alebo ekvivalentnú lineage, ktorá umožní vysvetliť, z čoho presne vznikol model artifact.

## 2. Dataset ako versionovaný population snapshot

Dataset je organizovaný súbor samples a associated metadata určený pre konkrétny learning alebo evaluation purpose. Jeho identity zahŕňa nielen file path, ale aj source snapshots, extraction query/code, schema, filters, deduplication, feature definitions, label policy, observation windows a integrity checks.

```yaml
subject: DATASET-ML-PAY-83-v2
purpose: train review-priority model
population:
  product: card-not-present
  currency: EUR
  operation_created: 2025-01-01..2026-06-30
observation_unit: merchant_operation_id
prediction_time: authorization_received_at
feature_cutoff: event_time <= prediction_time
label:
  name: confirmed_loss_within_30d
  source: reconciled_loss_ledger
  mature_after: 30d
sources:
  operations_snapshot: iceberg://payments/operations@snapshot-8841
  merchant_snapshot: iceberg://risk/merchant@snapshot-4410
extraction_code: git:9a73d19
schema: risk-training-v4
row_count: 18423917
manifest_digest: sha256:2a83...bc11
```

Path `training/latest.parquet` nie je stabilná identity. Aj immutable object môže mať neznámy pôvod. Manifest musí umožniť read-back population a lineage bez opakovania mutable query proti dnešným tables.

## 3. Population, unit of analysis a sample

Population je množina entities alebo events, na ktoré sa majú závery vzťahovať. Sample je jedna observation z tejto population reprezentovaná v datasete. Unit of analysis určuje, čo presne row znamená: customer, merchant, operation, attempt, session, device, document, time window alebo query-item pair.

Pri Atlas use case je decision subject merchant operation. Payment attempt je technický pokus vykonať tú istú operation. Ak sa attempts použijú ako nezávislé samples, high-retry operations dostanú väčšiu váhu a identické entity môžu skončiť v rôznych splits.

```text
merchant operation op-741
├── attempt a1: timeout
├── attempt a2: issuer unavailable
└── attempt a3: accepted

správna sample identity pre review decision:
op-741

nesprávne nezávislé samples:
a1, a2, a3
```

Sample identity musí byť stable a deduplication policy musí rešpektovať business semantics. Odstrániť byte-identical rows nestačí, ak tri rows reprezentujú ten istý decision subject s mierne odlišným timestampom.

## 4. Observation time a prediction time

Prediction time je okamih, v ktorom má produkčný systém vytvoriť output. Feature môže vstúpiť do modelu iba vtedy, ak bola v tomto okamihu dostupná cez production-equivalent path. Event time, ingestion time, processing time a database update time sa nesmú zamieňať.

```text
operation created                 10:00:00
merchant profile known            10:00:01
authorization response             10:00:02  ← prediction time
settlement final status            +2 days
chargeback confirmed               +21 days
```

`final_settlement_status` môže byť validný label precursor alebo post-outcome diagnostic field, ale nie feature pre prediction o 10:00:02. To, že historical table obsahuje column na jednej row, neznamená, že hodnota bola dostupná pri rozhodnutí.

Point-in-time correct join musí vybrať najnovšiu feature value známu najneskôr v cutoff-e:

```sql
SELECT o.merchant_operation_id,
       f.risk_band,
       f.country_velocity_1h
FROM operations AS o
LEFT JOIN merchant_features AS f
  ON f.merchant_id = o.merchant_id
 AND f.effective_at <= o.authorization_received_at
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY o.merchant_operation_id
  ORDER BY f.effective_at DESC
) = 1;
```

Query je ilustrácia semantics. Reálna correctness vyžaduje aj immutable source snapshots, timezone, late-arriving events, corrections a tie-breaking contract.

## 5. Feature ako model input s production contractom

Feature je merateľná alebo odvodená property sample-u použitá ako model input. Feature nie je iba column name. Jej contract zahŕňa data type, unit, allowed range, category vocabulary, missingness semantics, computation window, source authority, freshness, transformation a online/offline implementation.

```yaml
feature: merchant_decline_rate_1h
entity: merchant_id
window: event_time in (prediction_time - 1h, prediction_time]
numerator: declined_authorization_attempts
denominator: all_authorization_attempts
late_event_policy: exclude after 5m watermark
missing: no eligible attempts -> null, not 0
unit: ratio
online_source: feature-service/risk-v4
offline_source: batch-job risk_features_v4
```

Hodnota `0` a missing value nemusia znamenať to isté. Nula môže znamenať nulovú decline rate z desiatich attempts; missing môže znamenať, že merchant nemal žiadnu history alebo feature job zlyhal. Tiché `fillna(0)` môže spojiť business state s pipeline failure.

Feature names bez semantics nevytvárajú compatibility. Ak `amount` zmení unit z euros na cents, schema môže zostať integer, ale model behavior sa dramaticky zmení. Unit a transformation generation musia byť súčasťou contractu.

## 6. Feature vector a design matrix `X`

V klasickom supervised ML sa samples často reprezentujú ako matrix `X` tvaru `(n_samples, n_features)`: rows sú samples a columns features. Toto je implementation representation, nie business identity. Mapping medzi row indexom a stable sample keyom musí zostať zachovaný mimo samotného numeric arrayu.

```python
sample_keys = ["op-741", "op-742", "op-743"]
X = [
    [12500, 0.12, 3],
    [  990, 0.01, 0],
    [80400, 0.42, 7],
]
```

Bez feature order a schema generation je array neinterpretovateľný. Model očakávajúci `[amount_minor, decline_rate_1h, device_count_24h]` nesmie dostať rovnaké tri numbers v inom poradí.

Sparse, text, image alebo graph inputs môžu mať inú representation, ale rovnaké otázky zostávajú: čo je sample, aké fields boli dostupné, ako sa transformovali a či production path vytvára ekvivalentný input.

## 7. Label ako observed learning signal

Label je observed value priradená sample-u, ktorú supervised learning používa ako learning signal. Môže to byť class, numeric value, relevance grade alebo iný structured output. Label nie je automaticky objective truth. Je výsledkom measurement procesu s vlastným source, timingom, ambiguity, noise a coverage.

Atlas pôvodne používal `needs_review`, ktoré vzniklo rozhodnutím historickej queue policy. Taký label odpovedá na otázku „čo bolo historicky routované“, nie „ktorá operation spôsobila potvrdenú stratu“. Model môže presne replikovať staré rozhodnutia aj s ich omissions a bias.

```text
proxy label:
needs_review = historical analyst queue membership

business target evidence:
confirmed_loss_within_30d = reconciled loss ledger outcome
```

Niekedy je proxy nevyhnutná, pretože final outcome prichádza neskoro alebo je drahý. Potom musí byť proxy status explicitný a evaluation musí skúmať jej relationship k business outcome-u. Premenovanie proxy columnu na `fraud` nevylepší measurement.

## 8. Target ako quantity alebo outcome, ktorý sa model učí predikovať

Pojmy label a target sa často používajú zameniteľne, ale užitočná operational hranica je táto: target opisuje intended quantity alebo outcome tasku; label je konkrétna observed value v datasete. Target môže byť „pravdepodobnosť potvrdenej straty do 30 dní“, label pre mature sample je `0` alebo `1` podľa reconciled ledgeru.

```yaml
target_concept: confirmed loss within 30 days
target_type: binary outcome
label_value:
  positive: reconciled_loss_minor > 0 within 30d
  negative: mature 30d window and no reconciled loss
  unknown: window not mature or reconciliation incomplete
```

Unknown nie je automaticky negative. Ak recent operations ešte nemali čas vytvoriť chargeback, priradenie `0` vytvorí censoring bias. Label maturity a exclusion alebo survival-aware semantics musia byť explicitné.

Target definition tiež určuje actionability. Predikovať „loss niekedy v budúcnosti“ je menej použiteľné než definovaný horizon a recoverable action window.

## 9. Label window, maturity a delayed ground truth

Mnohé labels vznikajú po prediction time. Dataset builder musí definovať observation window a moment, keď je sample mature. Recent samples bez ukončeného window-u majú unknown outcome, aj keď source table zatiaľ neobsahuje positive event.

```text
prediction_time t0
→ label observation window [t0, t0 + 30d]
→ reconciliation delay +3d
→ label mature at t0 + 33d
```

Delayed labels ovplyvňujú training freshness a production monitoring. Najnovší traffic mix môže byť dostupný bez final ground truth; mature evaluation reprezentuje staršiu population. Dashboard musí odlíšiť immediate proxy signals od final labels.

Corrections a reversals tiež menia label generation. Chargeback môže byť neskôr overturned. Dataset snapshot musí uviesť as-of time a reconciliation policy, aby rovnaká operation nemala nezdokumentovane iný label pri každom rerune.

## 10. Entity joins, one-to-many relationships a duplication

Dataset často vzniká joinom viacerých sources. One-to-many join môže nepozorovane duplikovať samples a meniť weights. Ak operation joinne tri device events a dve support annotations, cross product vytvorí šesť rows.

```text
1 operation
× 3 device rows
× 2 analyst annotations
= 6 dataset rows
```

Správne riešenie závisí od semantics: agregovať events do point-in-time features, vybrať authoritative annotation, vytvoriť nested representation alebo zmeniť observation unit. `SELECT DISTINCT` môže skryť duplication bez vysvetlenia, ktorú informáciu zahodil.

Integrity checks majú overiť cardinality proti manifestu:

```sql
SELECT
  COUNT(*) AS rows,
  COUNT(DISTINCT merchant_operation_id) AS operations
FROM training_dataset;
```

Rovnosť nemusí byť vždy požadovaná, ale očakávaný ratio musí byť vysvetlený a testovaný.

## 11. Dataset schema a semantic validation

Schema validation kontroluje types, nullability, ranges, categories a shape. Semantic validation kontroluje invariants, time ordering, uniqueness, source coverage, distribution a business relationships. Obe vrstvy sú potrebné.

```python
assert dataset["merchant_operation_id"].is_unique
assert (dataset["feature_event_time"] <= dataset["prediction_time"]).all()
assert dataset["label"].isin([0, 1]).all()
assert dataset.loc[dataset["label_mature"], "label"].notna().all()
```

Také checks preukazujú konkrétne invariants nad loaded snapshotom. Nepreukazujú, že source event bol pravdivý, target zodpovedá business cieľu alebo production feature service používa rovnakú transformáciu.

Distribution checks môžu zachytiť náhle changes, ale threshold musí byť viazaný na population a seasonality. Zmena môže byť bug, incident alebo legitímna business kampaň. Automatické odmietnutie bez diagnosis nie je vždy správne; tiché pokračovanie tiež nie.

## 12. Provenance, consent, privacy a access boundary

Dataset môže byť technicky použiteľný a zároveň nevhodný z hľadiska purpose, privacy, policy alebo rights. Provenance musí uviesť, odkiaľ data pochádzajú, na aký účel boli získané, kto ich smie používať, retention, deletion a citlivé fields.

Feature availability nie je oprávnenie ju použiť. Protected alebo proxy attributes môžu vytvoriť discrimination risk. Raw identifiers môžu byť potrebné pre grouping a leakage prevention, ale nemusia vstupovať do modelu. Dataset access, training access a serving access sú odlišné capabilities.

```text
source authority
→ approved purpose
→ minimization a transformation
→ training access
→ artifact leakage assessment
→ serving exposure
→ retention/deletion propagation
```

Deletion request môže vyžadovať odstránenie source recordu, future datasets a caches; či vyžaduje retraining alebo model unlearning, závisí od policy a risk assessmentu. Nemožno to uzavrieť iba delete-om jedného parquet file-u.

## 13. Dataset read-back a reproducibility

Reproducibility vyžaduje viac než uložený file. Treba vedieť overiť manifest digest, source snapshots, extraction code, environment, row/sample counts, schema hash, label distribution, time range a split assignment.

```json
{
  "dataset_id": "DATASET-ML-PAY-83-v2",
  "manifest_sha256": "2a83...bc11",
  "n_rows": 18423917,
  "n_samples": 18423917,
  "n_features": 47,
  "positive_rate": 0.0038,
  "prediction_time_max": "2026-05-28T23:59:59Z",
  "label_mature_through": "2026-06-30T23:59:59Z"
}
```

Read-back musí byť vytvorený z artifactu, ktorý training job skutočne načítal. Catalog entry alebo pipeline parameter preukazuje requested dataset, nie automaticky loaded bytes.

## 14. Worked incident `ML-PAY-83`: data root cause

Pôvodný Atlas dataset mal `42,7 milióna` payment-attempt rows, ale iba `18,4 milióna` merchant operations. Random row split umiestnil retry attempts tej istej operation do train aj test. Model tak rozpoznával takmer identické histories a test score nadhodnotil generalization na nové operations.

Feature `final_settlement_status` bola pripojená cez current-state table bez point-in-time predicate. Pri historical extraction už poznala outcome, ktorý v prediction time neexistoval. Label `needs_review` vznikal z queue membership a recent unresolved operations boli ticho označené ako negative.

Po kampani vzrástol retry rate. Dataset representation dávala high-retry operations viac rows a model ich častejšie posielal na review. Queue-level deduplication neexistovala, takže analytici dostali viac prípadov tej istej business operation.

Evidence ukázal štyri odlišné defects:

```text
sample defect: attempt namiesto operation
join defect: current-state feature bez cutoff-u
label defect: historical routing proxy
maturity defect: unresolved recent outcomes ako negative
```

Zmena algorithmu by tieto chyby nevyriešila. Najprv bolo potrebné obnoviť dataset contract.

## 15. Containment a recovery

Tím zmrazil dataset manifest, extraction SQL/code, source snapshot IDs a row-level sample keys. Zastavil training z mutable `latest` tables a porovnal operation counts, retry multiplicity, feature timestamps a label maturity.

Nový builder agregoval attempts do operation-level features, používal point-in-time joins, oddelil proxy `historical_review` od targetu `confirmed_loss_within_30d` a recent immature operations označil ako unknown. Split assignment sa viazal na stable operation key a time boundary, nie na náhodnú row.

```text
raw events
→ operation identity resolution
→ point-in-time feature aggregation
→ mature label join
→ schema/invariant checks
→ immutable dataset snapshot
→ grouped/time split
```

Recovery nebola uzavretá vytvorením nového parquetu. Tím porovnal offline feature computation s production feature service na shadow requests a preukázal rovnaké values alebo vysvetlené tolerances.

## 16. Dataset acceptance contract

Positive acceptance musí potvrdiť, že každý sample reprezentuje intended unit, features sú dostupné v prediction time, labels majú správny source a mature window, schema a semantic invariants prešli a loaded snapshot zodpovedá manifestu.

Recovery acceptance musí preukázať rebuild z pinned sources a code s rovnakým manifestom alebo explicitne novou generation. Oprava source data nesmie ticho zmeniť existujúci dataset ID.

Forbidden paths musia zlyhať:

```text
positive:
stable operation key
→ point-in-time features
→ mature authoritative label
→ immutable manifest

forbidden:
future field joins training row
same operation crosses split cez retry attempts
unknown outcome becomes negative
one-to-many join mení sample weight bez contractu
feature unit/order sa zmení bez schema generation
mutable latest path sa vydáva za reproducible snapshot
```

Second-build test musí spustiť builder nad rovnakými immutable inputs a potvrdiť rovnaké sample inventory, schema a digest alebo zdokumentovaný nondeterminism. Second-production test musí porovnať offline a online features pre nové operations, nie iba training rows.

## Kontrolné otázky

1. Čím sa population líši od datasetu a sample-u?
2. Prečo musí sample identity vychádzať z business decision subjectu?
3. Ako retry attempts vytvorili leakage medzi train a test?
4. Čo určuje prediction time a feature cutoff?
5. Prečo current-state join môže používať budúcu informáciu?
6. Aké properties tvoria feature contract okrem názvu columnu?
7. Prečo missing value nie je automaticky nula?
8. Ako sa label líši od business truth?
9. Aký je užitočný rozdiel medzi target conceptom a observed labelom?
10. Prečo recent sample bez eventu nemusí byť negative?
11. Ako one-to-many join mení sample weights?
12. Čo preukazuje schema validation a čo nepreukazuje?
13. Ktoré provenance a access boundaries patria do datasetu?
14. Aký read-back je potrebný pre reprodukovateľný training?
15. Ktoré positive, rebuild, forbidden a second-build testy uzatvárajú dataset contract?

## Glossary impact

Relevantné pojmy: dataset generation, population, sample, observation unit, unit of analysis, sample key, prediction time, event time, ingestion time, feature cutoff, feature contract, design matrix `X`, label, target, proxy label, label window, label maturity, unknown outcome, point-in-time join, dataset manifest, semantic validation, data provenance, offline/online feature parity a dataset acceptance contract.

## Primárne zdroje

- [scikit-learn — Getting Started: samples matrix `X` a target `y`](https://scikit-learn.org/stable/getting_started.html)
- [scikit-learn — Dataset loading utilities](https://scikit-learn.org/stable/datasets.html)
- [scikit-learn — Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html)
- [NIST AI Risk Management Framework 1.0](https://airc.nist.gov/airmf-resources/airmf/)
- [NIST AI 100-2e2025 — Adversarial Machine Learning](https://csrc.nist.gov/pubs/ai/100/2/e2025/final)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Artificial intelligence, machine learning, deep learning a generative AI](artificial-intelligence-machine-learning-deep-learning-generative-ai.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Supervised, unsupervised a reinforcement learning →](supervised-unsupervised-reinforcement-learning.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
