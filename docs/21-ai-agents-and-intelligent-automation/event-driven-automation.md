# Event-driven automation

Event-driven automation oddeľuje producer od consumerov a umožňuje nízku latenciu, fan-out a nezávislé škálovanie. Bez presného event contractu však redelivery, ordering, schema evolution a replay vytvoria duplicate alebo chýbajúce business effects, ktoré žiadny broker status automaticky nevyrieši.

Incident `AGENT-AUTO-14` použil nejednoznačný event ID, chýbajúci subject a dva subscription paths. Redelivery spustila duplicitný build, prompt-like text v payload-e ovplyvnil AI remediation a absent consumer metrics boli nesprávne interpretované ako prázdna queue.

Nosný lifecycle je:

```text
business change alebo external signal
→ authenticated producer a canonical event envelope
→ broker persistence, routing a delivery
→ consumer inbox a schema validation
→ ordering, concurrency a idempotency decision
→ bounded side effect a provider acknowledgment
→ broker acknowledgment
→ projection a business read-back
→ replay, recovery a second-consumer acceptance
```

## 1. Event nie je command

Event oznamuje, že sa niečo stalo; command žiada, aby sa niečo vykonalo. `OrderCreated` je observation minulého faktu, zatiaľ čo `CreateShipment` nesie requested intent a authorization boundary.

Zamiešanie vedie k nejasnému retry a ownershipu. Consumer nesmie interpretovať informačný event ako implicitné povolenie na high-impact mutation bez policy a operation identity.

## 2. CloudEvents envelope

CloudEvents poskytuje štandardný envelope s atribútmi ako `specversion`, `id`, `source` a `type`; voliteľné `subject`, `time`, `dataschema` a content type zvyšujú routability a interpretáciu. Envelope oddeľuje event metadata od domain data.

Štandardizovaný tvar nezaručuje správnu business semantics. Producer musí definovať uniqueness scope, source authority, schema generation, tenant a privacy classification.

## 3. Event identity

Event `id` je stabilný identifikátor observation v rámci source. Broker delivery ID, HTTP request ID a business operation ID sú iné identities a nesmú sa zlievať.

Dedup store používa composite key podľa contractu, napríklad `source + id`. Ak producer opakovane vydá rovnakú business zmenu s novým event ID, consumer potrebuje aj domain version alebo operation key.

## 4. Source a subject

`source` identifikuje context, v ktorom event vznikol, a `subject` môže pomenovať konkrétnu entity. Multi-tenant platforma pridáva tenant identity v canonical attribute alebo podpísanom data contracte.

Topic name sám nie je trustworthy source. Gateway alebo broker musí autentizovať producera a zabrániť spoofingu event type-u a tenant scope.

## 5. Type a schema evolution

Event type vyjadruje stabilnú semantics, nie implementačný class name. Schema generation sa mení kompatibilne, s explicitným deprecation windowom a consumer contract tests.

Adding optional field býva jednoduchšie než zmena významu existujúceho field-u. Consumer musí odlíšiť unknown field od unsupported required generation a nesmie potichu defaultovať authority parameter.

## 6. Event time, ingestion time a processing time

Event time je čas domain udalosti, ingestion time čas prijatia brokerom a processing time čas consumer attemptu. Late a out-of-order eventy sú normálne v distribuovanom systéme.

Windowing, SLA a incident correlation používajú správny čas. UI sort podľa ingestion time nesmie dokazovať business poradie.

## 7. Delivery semantics

Najbežnejší praktický model je at-least-once delivery: event sa môže doručiť viackrát, kým broker nedostane acknowledgment. At-most-once môže event stratiť a exactly-once transport neznamená exactly-once business side effect cez externé API.

Consumer design preto predpokladá redelivery, crash po side effecte a pred acknowledgmentom a duplicitné subscription paths. Idempotency a reconciliation sú business controls, nie broker checkbox.

## 8. Acknowledgment boundary

Acknowledgment sa posiela až keď consumer bezpečne zaznamenal outcome alebo durable handoff. Ack po parsovaní, ale pred business commitom, môže stratiť operation; ack až po external call bez operation key môže pri crashi vytvoriť duplicate.

Transactional inbox alebo state transition viaže event receipt a local work item atomicky. External provider sa následne volá cez idempotent adapter a outcome sa read-backne.

## 9. Transactional outbox

Producer, ktorý zapisuje business state a publikuje event samostatne, riskuje dual-write inconsistency. Transactional outbox uloží domain zmenu a pending event v jednej databázovej transakcii a relay ho publikuje neskôr.

Outbox nezaručuje jediné doručenie; relay môže publikovať duplicitne. Stabilný event ID a consumer inbox zostávajú potrebné.

## 10. Inbox a deduplication

Inbox uchová `source`, `event_id`, payload digest, first-seen time, processing status a outcome reference. Rovnaký key s iným digestom je contract violation alebo spoofing, nie bežná redelivery.

Retention inboxu musí pokryť maximálne replay a broker retention window. Príliš skoré vymazanie znovu otvorí duplicate path.

## 11. Ordering a partitioning

Globálne poradie je drahé a často nepotrebné. Potrebné býva per-entity alebo per-aggregate ordering, ktoré broker dosahuje partition keyom a consumer serializáciou.

Aj pri per-key ordering môže retry starého eventu blokovať nové. Design určí, či použije strict ordering, version check, skip/quarantine alebo compensating path.

## 12. Concurrency control

Dvaja consumers môžu spracovať rovnakú entity paralelne cez rôzne topics alebo replay. Optimistic version, compare-and-swap, lease alebo single-writer partition chráni domain invariant.

Lock bez operation identity iba posunie duplicate. Consumer musí po získaní locku znovu overiť current business state.

## 13. Backpressure

Event rate môže prekročiť consumer alebo downstream capacity. Queue depth, oldest event age, processing latency, retries a provider quota spolu určujú health.

Autoscaling bez dependency budgetu môže zosilniť DB alebo API outage. Backpressure plan zahŕňa rate limit, priority, pause, shed, dead-letter a recovery ordering.

## 14. Dead-letter a quarantine

Permanentne invalid event, unsupported schema alebo poisoned payload sa necyklí donekonečna. Presunie sa do quarantine s reason, source, attempts, payload digest, classification a remediation ownerom.

Dead-letter queue nie je odpadkový kôš. Replay vyžaduje opravený consumer alebo data, approval pri citlivom side effecte a zachovanie pôvodnej identity.

## 15. Replay

Replay môže obnoviť projection, opraviť consumer bug alebo vytvoriť nový read model. Musí mať bounded range, pinned consumer generation, dry-run, rate limit a side-effect policy.

Analytics replay a command replay sú odlišné. Mutation consumers sú počas replay často vypnuté alebo používajú simulation mode, aby history nevytvorila nové externé operácie.

## 16. Event retention a compaction

Broker retention určuje, ako ďaleko možno replayovať raw events. Compacted log môže zachovať posledný state per key, ale nie úplnú históriu.

Compliance a recovery requirements sa nesmú odvodiť z default broker retention. Long-term archive používa immutable storage, checksums, encryption a access policy.

## 17. Polling, webhooks a event log

Webhook je push transport, nie automaticky durable event log. Polling môže byť správny pre provider bez event contractu alebo ako reconciliation safety net.

Robustný pattern často kombinuje webhook pre nízku latenciu a periodický poll/read-back pre missed events. Oba paths používajú rovnaký operation identity a dedup store.

## 18. Fan-out a consumer ownership

Jeden event môže spustiť billing, search indexing, notification a analytics. Každý consumer má vlastný offset, SLO, retry a failure domain.

Producer nesmie čakať na všetkých consumers ako na jednu distribuovanú transakciu. Kritické invariants sa riešia v domain transaction alebo explicitnej saga, nie implicitným fan-outom.

## 19. Event choreography a orchestration

Choreography necháva services reagovať na events bez centrálneho coordinatora; orchestration používa explicitný workflow, ktorý vydáva commands a čaká na outcomes. Choreography znižuje central coupling, ale môže skryť end-to-end state a cycles.

Komplexná business saga často potrebuje orchestrator a events ako observation a integration boundary. Jednoduché projections a notifications môžu zostať choreografické.

## 20. Security

Producer authentication, topic ACL, payload signing, encryption a schema validation chránia event plane. Consumer identity sa viaže na minimálne topics a downstream permissions.

Event data sa považujú za untrusted input aj keď prichádzajú z interného brokeru. Prompt injection, log forging a malicious fields nesmú meniť AI tool authority.

## 21. Privacy a data minimization

Event nesie iba fields potrebné pre consumers. PII, secrets a full documents sa nahrádzajú references, tokenized identifiers alebo purpose-limited claims.

Retention a right-to-delete sa riešia naprieč brokerom, archive, DLQ, projections a AI traces. Vymazanie iba primary recordu nestačí.

## 22. Observability a trace context

Event processing koreluje producer span, broker operation, consumer attempt a downstream mutation cez trace context a stable event/operation IDs. Metrics používajú bounded labels; event ID nepatrí do high-cardinality metric labelu.

Logs a traces zaznamenajú delivery attempt a outcome, nie raw sensitive payload. Missing trace pri sampling-u nie je dôkaz, že event nebol spracovaný.

## 23. Incident AGENT-AUTO-14

Producer použil rovnaké `id` pre celý batch a chýbal `subject`, takže dedup store zlúčil rôzne customer events a zároveň nevedel odhaliť redelivery jednej entity. Druhý subscription path spustil duplicitný CI build.

AI remediation spracovala log text z eventu ako trusted instruction a navrhla vypnúť test. Observability agent nevidel dropped consumer series a označil queue za prázdnu. Incident spojil event identity, prompt trust a no-data semantics.

## 24. Competing hypotheses

Rast queue age môže znamenať consumer outage, downstream throttling, poison event, partition hotspot, DB lock alebo nefunkčný metrics exporter. Duplicate business effect môže pochádzať z redelivery, producer duplicate, retry multiplication alebo manuálneho replayu.

Triage používa broker offsets, inbox, provider references a business ledger. Jedna dashboard series nestačí.

## 25. Containment

Containment môže pause-nuť affected consumer group, zakázať mutation adapter, izolovať partition alebo presmerovať eventy do quarantine. Producer sa zastaví iba ak pokračuje invalid emission a zastavenie nespôsobí väčšiu stratu.

Pred resetom offsetu sa zachová broker, inbox a consumer-generation evidence. Blind replay počas incidentu je zakázaný.

## 26. Recovery

Recovery opraví producer contract alebo consumer, pinne generation, overí dry-run nad bounded range a postupne replayne eventy podľa partition a business priority. Dedup a provider reconciliation chránia side effects.

Po dobehnutí sa porovná broker lag, inbox statuses, projection counts a business ledger. Technical zero lag bez business completeness nie je recovery.

## 27. Positive acceptance

Test publikuje valid event, redelivery, out-of-order version a late event. Consumer vykoná najviac jeden business effect, zachová všetky attempts a odmietne stale mutation.

Crash po provider acknowledgment a pred broker ackom vedie do reconciliation, nie duplicate callu. Replay vytvorí rovnakú projection a nulový nový mutation.

## 28. Forbidden acceptance

Event s rovnakým source/id a iným digestom sa nesmie spracovať ako bežná redelivery. Cross-tenant subject, unsupported schema a unsigned high-impact event sú blocked alebo quarantined.

No-data metric nesmie znamenať empty queue a DLQ replay nesmie obísť approval. Očakáva sa nulový unauthorized side effect.

## 29. Recovery acceptance

Po consumer bug fixe sa pinned replay obnoví z presného offsetu a zachová event identities. Business reconciliation potvrdí complete affected set.

Alternate test obnoví broker alebo inbox backup a overí, že consumer nezačne od začiatku bez dedup history. Druhý consumer group prejde rovnaký contract suite.

## 30. Practical event contract

Practical event record musí oddeliť event identity, entity subject, tenant, business operation a trace context. Consumer contract potom explicitne určuje dedup key, ordering key, retry owner a replay behavior.

Nasledujúci envelope je interoperable transportný tvar, nie authorization token. Consumer pred mutation znovu overí tenant, policy, current entity version a operation status.

```yaml
event:
  specversion: "1.0"
  id: "01JZ6X5M8R7Q4P3N2K1H0G9F8E"
  source: "urn:crm:tenant-42"
  type: "com.example.customer.onboarding.requested.v2"
  subject: "customer/cus-8042"
  time: "2026-08-05T14:10:00Z"
  datacontenttype: "application/json"
  dataschema: "https://schemas.example.com/onboarding-requested/v2"
  extensions:
    tenantid: "tenant-42"
    operationid: "onboard-tenant-42-cus-8042-v7"
    traceparent: "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
  data:
    customer_version: 7
    requested_plan: "enterprise"
consumer_contract:
  dedup_key: "source+id"
  ordering_key: "tenantid+subject"
  retry_owner: "broker-consumer"
  unknown_outcome: "provider-read-back"
  replay_mode: "mutation-disabled"
```

## 31. Primary sources

CloudEvents project a current 1.0.2-compatible specification baseline sú publikované na https://cloudevents.io/ a v specification repository https://github.com/cloudevents/spec. Core attributes poskytujú interoperable event envelope; uniqueness, authorization a business idempotency zostávajú domain contracts.

Apache Airflow event-driven scheduling cez Assets a `AssetWatcher` je popísané na https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/event-scheduling.html. Prefect events a automations sú na https://docs.prefect.io/v3/concepts/events a deployment triggers na https://docs.prefect.io/v3/how-to-guides/automations/creating-deployment-triggers. Tieto mechanisms spúšťajú runs, ale samy nedefinujú broker delivery a business side-effect semantics.

OpenTelemetry traces, metrics, logs a baggage sú current signals na https://opentelemetry.io/docs/concepts/signals/. Trace context a semantic conventions poskytujú correlation vocabulary na https://opentelemetry.io/docs/concepts/signals/traces/ a https://opentelemetry.io/docs/concepts/semantic-conventions/. Observability evidence musí stále uvádzať sampling, completeness a source health.

## Zhrnutie

Event-driven platforma je bezpečná až vtedy, keď producer identity, event envelope, broker semantics, consumer inbox, ordering, idempotency, replay a business reconciliation tvoria jeden testovaný contract. At-least-once delivery je normálny stav; presne jeden business effect vzniká z domain controls.

Ďalšia kapitola aplikuje rovnaké hranice na AI-assisted CI/CD, kde modelový návrh nesmie vlastniť merge, credential ani deployment authority.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: n8n oproti Temporal, Airflow a Prefect use cases](n8n-temporal-airflow-prefect-use-cases.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: AI-assisted CI/CD →](ai-assisted-ci-cd.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
