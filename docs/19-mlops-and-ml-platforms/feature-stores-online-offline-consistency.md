# Feature stores a online/offline consistency

Feature store je platformová vrstva pre definovanie, objavovanie, získavanie a podľa architektúry aj materializáciu modelových features. Jeho hlavná hodnota nie je „databáza pre features“, ale jednotný contract medzi historical training retrieval a low-latency online retrieval. Feature store sám nezaručuje, že offline a online values sú identické, čerstvé alebo business-correct; poskytuje object model a retrieval paths, ktoré treba verziovať, monitorovať a testovať.

Incident `MLOPS-PAY-91` pokračuje. Atlas nasadil model version 18 s feature service `risk-features-v6`. Historical training dataset používal point-in-time join z warehouse, ale production online store obsahoval posledné materializované values. Materialization job meškal dve hodiny, stream push zapisoval niektoré entities s event time nahradeným processing time a serving pri miss-e dosadzoval nulu. Model package, Registry aj deployment boli správne; online feature vector patril inej effective generation než training evidence.

## 1. Dominantný feature lifecycle

Feature lifecycle začína semantic definition a končí request-correlated value evidence. Definícia, batch transform, historical retrieval, materialization, online write, online read a model consumption sú samostatné transitions.

```text
business event a entity identity
→ feature semantic a timestamp contract
→ source data a transformation generation
→ feature view / feature service definition
→ historical point-in-time retrieval pre training
→ batch materialization alebo stream push
→ online-store state pre entity
→ low-latency retrieval pri requeste
→ model input vector
→ freshness, parity a business outcome evidence
```

Rovnaký názov feature v offline table a online store nepreukazuje rovnakú hodnotu. Consistency potrebuje common definition, event-time semantics, transformation behavior, schema, entity join key, TTL, materialization watermark a request read-back.

## 2. Exact feature subject

Feature subject musí uviesť logical name, entity, type, semantic definition, source, event timestamp, transformation a ownership. Feature view zoskupuje related time-series features. Feature service alebo ekvivalent viaže exact feature set k model use caseu.

```yaml
feature_service: payment-risk-features-v6
model_interface: risk-inference-v6
entity:
  name: payment_operation
  join_key: payment_operation_id
features:
  - reference: merchant_velocity:amount_sum_7d
    type: float64
    unit: EUR
    entity: merchant
    event_timestamp: transaction_authorized_at
    availability_timestamp: warehouse_ingested_at
    ttl: 48h
    transformation_commit: 91af22c
    source: warehouse://risk/merchant_velocity
  - reference: merchant_profile:merchant_age_days
    type: int64
    entity: merchant
    event_timestamp: profile_effective_at
    transformation_commit: 883b1f0
owner: risk-feature-platform
```

Unit, event time a availability time sú súčasť semantics. `amount_sum_7d` vypočítaná podľa authorization time nie je tá istá feature ako suma podľa settlement time. Zmena window inclusion, timezone alebo deduplication vytvára novú generation aj pri rovnakom názve a type.

## 3. Feast object model

Feast modeluje entities, data sources, feature views, fields/features, feature services a Registry. Feature view je logical group time-series feature data viazaná na data source a voliteľne entity. V offline settings sa používa pre historical retrieval; v online settings určuje stateful collection, ktorá sa číta cez online retrieval.

Feature service zoskupuje features pre model alebo use case. Feast FAQ odporúča, aby každá model version zodpovedala odlišnému feature service a aby feature views používané feature service zostali immutable, kým je service aktívna. Tento pattern chráni model-interface lineage.

Feast Registry drží definitions aplikované z version-controlled feature repository. `feast apply` publikuje definitions a môže pripraviť online infrastructure. Registry definition je control-plane state; nepreukazuje, že materialization naplnila online values alebo že source table obsahuje expected rows.

## 4. Offline store

Offline store je storage/compute interface pre historical time-series feature values. Používa sa na tvorbu training datasetov a ako source pre materialization do online store. Feast často neprodukuje batch features; transformations vykonáva warehouse, Spark, SQL alebo iný upstream engine a Feast nad nimi vykoná retrieval.

Historical retrieval potrebuje entity dataframe s entity keys a event timestamps. Point-in-time join pre každú observation vyberie feature value, ktorá bola platná a dostupná v relevantnom čase, nie najnovšiu current value.

```python
training_df = store.get_historical_features(
    entity_df=entity_dataframe,
    features=[
        "merchant_velocity:amount_sum_7d",
        "merchant_profile:merchant_age_days",
    ],
).to_df()
```

Successful query preukazuje, že offline retrieval vrátil data. Nepreukazuje správny observation unit, label maturity ani absence leakage, ak entity dataframe alebo source timestamps sú chybné.

## 5. Point-in-time correctness

Point-in-time correctness zabraňuje future leakage. Pre observation s prediction time `t` sa nesmie vybrať feature event po `t`. V praxi treba zohľadniť aj availability: event mohol nastať pred `t`, ale pipeline ho spracovala až po prediction. Strict reproduction production knowledge používa availability timestamp alebo source-specific ingestion boundary.

```text
event_time <= prediction_time
a zároveň
availability_time <= prediction_time
```

TTL obmedzuje, ako ďaleko späť možno hľadať. Ak posledná value je staršia než TTL, retrieval vráti missing. Offline a online path musia mať kompatibilnú missing/fallback semantics. Offline forward-fill bez rovnakého online behavioru vytvára skew.

Entity join je ďalší leakage boundary. Nesprávny join key môže spojiť retry, account alebo merchant records do jednej entity. Point-in-time algorithm nemôže opraviť chybnú entity identity.

## 6. Online store

Online store slúži low-latency retrieval. Feast online store typicky drží pre entity key iba najnovšiu feature value, nie celú history. Values sa dostávajú do online store batch materialization alebo stream/push pathom.

```python
online = store.get_online_features(
    features=[
        "merchant_velocity:amount_sum_7d",
        "merchant_profile:merchant_age_days",
    ],
    entity_rows=[{"merchant_id": "m-771"}],
).to_dict()
```

Online response musí obsahovať alebo byť korelovateľný s feature timestamps, service/definition generation a retrieval status. Value bez freshness metadata môže byť syntakticky správna a stale. Low latency nie je correctness.

Online store je derived serving state. Autorita pre historical rebuild môže zostať offline source a transformation code. Ak online store stratí data, recovery materializuje alebo replay-ne stream podľa RPO/RTO, no musí zabrániť older eventu prepísať newer value.

## 7. Materialization

Materialization načíta feature values z offline sources do online store pre definovaný časový interval. Feast poskytuje commands ako `feast materialize` a `materialize-incremental`. Scheduler musí vlastniť watermark, retry a overlap semantics.

```bash
feast materialize \
  2026-08-03T00:00:00 \
  2026-08-03T12:00:00

feast materialize-incremental \
  2026-08-03T13:00:00
```

Command success nepreukazuje complete entity coverage. Job môže spracovať partial partitions, late data alebo wrong project/Registry. Acceptance porovná expected source population, online write counts, per-feature watermark a sampled values.

Materialization s processing/current timestamps môže zničiť event-time ordering. Feast podporuje aj `--disable-event-timestamp`, ale použitie mení semantics a musí byť explicitné; pre historical/online parity môže byť nevhodné.

## 8. Stream a push paths

Fresh features môžu prichádzať zo streamu alebo Push API. Push source môže zapisovať do online, offline alebo oboch stores podľa configuration. Dual write bez common operation identity môže divergovovať pri partial failure: online write prejde, offline append zlyhá, alebo opačne.

Robustný pattern používa durable event log ako replay authority, event ID, entity key, event time a transformation generation. Consumer writes sú idempotentné a older event nesmie prepísať newer value. Late-arriving event môže patriť historical store, ale online latest selection musí rešpektovať event time a policy.

Stream transformation a batch transformation musia implementovať rovnakú semantic function alebo mať parity test. Copy-paste SQL a Python implementation často driftujú. Shared definition znižuje riziko, no engine-specific numeric/time behavior stále treba testovať.

## 9. Druhy offline/online consistency

Consistency nie je jedna boolean vlastnosť. Treba oddeliť:

```text
definition consistency:
rovnaký feature contract a generation

schema consistency:
rovnaký type, null a shape contract

transformation consistency:
rovnaká semantic funkcia

value parity:
rovnaký entity + event boundary dá rovnakú value

freshness consistency:
online value spĺňa required age/watermark

availability consistency:
feature použitá offline bola dostupná v production time

serving consistency:
model dostal intended feature set, order a fallback
```

Systém môže mať schema parity a hodnotový skew. Môže mať rovnaké values na sample, ale online freshness mimo SLO. Aggregate parity rate môže zakryť skew v jednom high-risk cohort-e.

## 10. Feature definition versioning a promotion

Feature repository je version-controlled source pre definitions. `feast apply` načíta project definitions a aktualizuje Registry/infrastructure. Git commit identifikuje declared definitions, ale effective serving generation potrebuje Registry read-back a materialization/online evidence.

Breaking change sa nemá robiť in-place pre feature view používanú production modelom. Vznikne `v7` feature view/service, backfill, parity evaluation a controlled model/pipeline migration. Starú generation možno odstrániť až po retirement všetkých modelov a rollback window.

Feature service je vhodný release contract: model Registry version eviduje exact feature service name/generation. Deployment odmietne model, ak serving platform nevie resolve-nuť compatible service.

## 11. Freshness, TTL a missing values

Freshness SLO určuje maximálny age alebo watermark lag. TTL v retrieval určuje použiteľnosť historical/online value, ale nie automaticky alert threshold. Feature môže byť technically within TTL a business-neprijateľne stale.

Missing value má dôvod: entity neexistuje, value expired, materialization mešká, online store timeout, schema mismatch alebo access denial. Zlúčiť všetko na `0` ničí diagnózu a môže vytvoriť bias. Response alebo side telemetry musí zachovať status a fallback reason.

Fallback policy je súčasť model system release. Môže použiť safe default, offline cache, simpler model alebo human review. Retry online readu nesmie neobmedzene zvyšovať latency ani meniť request outcome po side effectu.

## 12. Online store capacity a availability

Feature read je v critical request path. Latency budget zahŕňa network, serialization, multi-entity lookup a hot-key behavior. Online store potrebuje capacity, partitioning, replication, timeout, load shedding a tenant isolation.

Batch request na stovky features môže prekročiť payload alebo timeout. Feature service má minimalizovať required set. Precomputed features znižujú latency, ale zvyšujú freshness/materialization dependency. On-demand transformations zvyšujú flexibility, no pridávajú compute a consistency boundary.

Online store outage nie je automaticky model outage, ak existuje bounded fallback. Fallback sa musí monitorovať ako separate cohort; inak model quality metrics miešajú normal a degraded path.

## 13. Monitoring a parity testing

Monitoring sleduje materialization watermark, source-to-online lag, write errors, retrieval latency, miss/expired/fallback rates, schema errors a sampled offline-online parity. Parity sample potrebuje exact entity, event time, feature generation a comparison tolerance.

```text
entity=m-771
prediction_time=2026-08-03T11:44:00Z
feature=merchant_velocity:amount_sum_7d
offline_value=1920.50
online_value=0.00
online_event_time=2026-08-03T08:00:00Z
retrieval_status=defaulted_after_expiry
```

Tento record ukazuje, že problém nie je floating-point tolerance, ale expired value a fallback. Aggregate model drift by bol downstream symptom.

Parity evaluation musí používať production-like requests a cohorts. Random entity sample môže minúť new merchants, high-volume keys alebo late-data sources.

## 14. Failure walkthrough incidentu MLOPS-PAY-91

Atlas začal porovnaním model digestu a feature service reference; obe boli správne. Prediction traces však ukázali nárast `defaulted_after_expiry` pre `amount_sum_7d`. Online store obsahoval values staré dve hodiny, hoci freshness SLO bolo 20 minút.

Materialization scheduler hlásil success, ale watermark state sa posunul na job start time pred dokončením writes. Retry preto preskočil missing interval. Stream push navyše používal processing time pri jednej source, takže late events prepisovali ordering nekompatibilne s offline event-time transformom.

Containment zastavil promotion a presunul affected requests do conservative review fallbacku. Tím zachoval online snapshots a event log offsets. Watermark sa vrátil na posledný complete interval, prebehla idempotentná re-materialization a stream writer začal posielať explicitný event time.

## 15. Recovery a acceptance

Component recovery overí Registry definition, materialization completeness, online timestamps a parity sample. Journey recovery vykoná historical retrieval aj online retrieval pre rovnaký controlled entity/event scenario a potom prediction cez actual model server. Business recovery sleduje fallback cohort, review completion a mature loss outcome.

Positive test prejde apply, historical retrieval, materialization a online read. Forbidden test odmietne breaking in-place feature change, missing timestamp alebo unversioned service. Late-event test overí ordering. Partial-write test simuluje offline/online divergence a replay. Stale test očakáva explicitný expired status, nie silent zero. Second-materialization test zopakuje overlap interval bez duplicate alebo older-value overwrite.

```bash
feast apply
feast materialize-incremental 2026-08-03T13:00:00

python verify_feature_parity.py \
  --feature-service payment-risk-features-v6 \
  --entities tests/entities.parquet \
  --prediction-time-column prediction_time \
  --max-online-age 20m
```

`feast apply` preukazuje úspešné spracovanie definition change. Materialization command preukazuje job execution. Parity verifier musí čítať source, online values, timestamps a statuses. Ani tieto kroky samy nepreukazujú model alebo business outcome.

## 16. Kontrolné otázky

1. Prečo feature definition nie je online feature value?
2. Aký je rozdiel medzi event time a availability time pri historical retrieval?
3. Ktoré rôzne dimensions tvoria offline/online consistency?
4. Prečo online store latest-value model komplikuje recovery late events?
5. Aké evidence odlíšia model drift od stale-feature fallbacku?

## 17. Primárne zdroje

- [Feast architecture overview](https://docs.feast.dev/getting-started/architecture/overview)
- [Feast components overview](https://docs.feast.dev/getting-started/components/overview)
- [Feast feature views](https://docs.feast.dev/getting-started/concepts/feature-view)
- [Feast online store](https://docs.feast.dev/getting-started/components/online-store)
- [Feast quickstart](https://docs.feast.dev/getting-started)

Feature store znižuje duplication a skew iba vtedy, keď definitions, timestamps, materialization, online state, model interface a request evidence zostávajú v jednom versionovanom lifecycle.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Model Registry, versions, stages a aliases](model-registry-versions-stages-aliases.md) · [↑ Obsah sekcie](README.md) · [↑ Learning Roadmap](../../ROADMAP.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
