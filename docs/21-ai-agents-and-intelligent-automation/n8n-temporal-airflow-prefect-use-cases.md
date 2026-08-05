# n8n oproti Temporal, Airflow a Prefect use cases

n8n, Temporal, Apache Airflow a Prefect všetky vykonávajú workflowy, ale nevlastnia rovnaký druh state-u ani failure model. Správny výber nevzniká z tabuľky funkcií; vzniká z presného business subjectu, trvania, event semantics, retry authority, operability a dôkazu, ktorý musí prežiť zlyhanie.

Incident `AGENT-AUTO-14` začal tým, že dlhý customer-onboarding proces používal jeden vizuálny execution record ako approval ledger, idempotency store aj recovery authority. Retention, event redelivery, AI-generated CI zmena a incomplete telemetry potom odhalili, že architektúra nemala jedného vlastníka durable process state-u.

Nosný lifecycle je:

```text
business capability a invariants
→ process subject a authoritative domain state
→ event, time, payload a side-effect model
→ candidate runtime semantics
→ failure, replay, retry a versioning tests
→ operability, security a cost evidence
→ selected responsibility split
→ production verification a exit strategy
```

## 1. Rozhodnutie začína procesom, nie produktom

Výber orchestration platformy začína business invariants, trvaním procesu, failure modelom, typom state-u, požadovanou latenciou, kompetenciou tímu a dôkazom, ktorý musí prežiť crash. Katalóg integrácií alebo atraktívne UI sú sekundárne, pretože rovnaký diagram môže skrývať odlišnú durability, retry a ownership semantics.

Architekt najprv pomenuje exact process subject, authoritative business system a side effects. Až potom porovná, či potrebuje integration workflow, durable application workflow, batch/data orchestration alebo Python-first operational flow.

## 2. n8n ako integration a business automation runtime

n8n je vhodný tam, kde proces skladá SaaS API, webhooky, databázové operácie, transformácie a human-facing notifikácie do relatívne zrozumiteľného workflowu. Jeho sila je rýchla integrácia, vizuálna kompozícia, credentials model, webhooks, sub-workflows a dostupná execution history.

n8n execution však nesmie byť automaticky vyhlásený za business ledger alebo univerzálnu durable saga authority. Pri dlhých procesoch treba osobitne riešiť retention, queue mode, shared storage, idempotency, versioning a to, čo sa stane pri retry s pôvodným alebo aktuálne uloženým workflowom.

## 3. Temporal ako durable application orchestration

Temporal je vhodný pre mission-critical procesy, ktoré musia pokračovať po crashoch, sieťových výpadkoch a dlhých čakaniach bez straty lokálneho workflow state-u. Workflow Execution používa event history a replay; failure-prone API, databázové alebo LLM operácie patria do Activities, ktoré majú samostatné timeout a retry semantics.

Táto vlastnosť je silná pre objednávky, platby, onboarding, provisioning a sagas, ale vyžaduje deterministic workflow code, worker lifecycle, namespace a task-queue governance, versioning a explicitnú idempotency externých side effectov. Temporal nezaručuje, že external API mutation je presne raz; poskytuje durable coordination, v ktorej sa outcome reconciliuje.

## 4. Airflow ako batch a data orchestration

Apache Airflow modeluje workflow ako Dag s tasks, dependencies, schedules a data intervals. Je prirodzený pre batch-oriented data pipelines, backfills, partitioned processing, ETL/ELT, model training a recurring analytical jobs, kde je dôležité vidieť jednotlivé task instances a opakovane spracovať časový interval.

Airflow 3 podporuje aj event-driven scheduling cez assets a watchers, no jeho základný mentálny model zostáva Dag run nad dátovým intervalom. User-facing transakčná saga s per-request low-latency state-om a komplikovanými command/reply interakciami zvyčajne potrebuje inú authority vrstvu.

## 5. Prefect ako Python-first flow orchestration

Prefect flows a deployments sú vhodné pre Python-heavy data a operational workflows, kde tím chce dynamický kód, task retries, schedules, event triggers, work pools a infra-aware execution bez pevnejšieho Dag authoring modelu. Deployment je server-side representation flowu, ktorá viaže schedule, event trigger a execution infrastructure.

Prefect môže pokryť experimentálne data workflows aj production automation, ale architekt stále musí definovať authoritative business state, event identity, deployment version, worker image a recovery semantics. Dynamickosť Pythonu neodstraňuje potrebu contractov a replay alebo migration testov.

## 6. Porovnávacia os state authority

n8n typicky drží execution metadata a node data, Temporal durable workflow state rekonštruuje z event history, Airflow drží Dag/task run state a Prefect flow/task run state. Tieto state stores odpovedajú na otázku, čo orchestrator vykonal alebo čaká; nemusia byť authoritative recordom objednávky, platby, identity alebo compliance rozhodnutia.

Každý návrh preto uvádza domain system of record a pravidlo reconciliation. Orchestrator môže koordinovať, ale business entity sa overuje proti providerovi alebo doménovej databáze.

## 7. Porovnávacia os času a čakania

Krátke webhookové integrácie a manuálne schválenia môžu byť efektívne v n8n. Rok trvajúci subscription lifecycle alebo proces s tisíckami timerov je prirodzenejší pre durable execution runtime, zatiaľ čo denný data interval a backfill sú prirodzené pre Airflow a Python flow schedule pre Prefect.

Dĺžka sama nerozhoduje. Dôležité je, či waiting state musí prežiť upgrade, retention pruning, worker replacement a schema evolution a či sa dá bezpečne obnoviť z externého business recordu.

## 8. Porovnávacia os retry semantics

Retry musí mať jedného ownera. n8n node retry, Temporal Activity Retry Policy, Airflow task retry a Prefect task retry sú odlišné mechanizmy s odlišným checkpointom a visibility.

Ak HTTP klient, SDK, message consumer a orchestrator retryujú tú istú mutation nezávisle, vzniká retry multiplication. Platformový výber je prijateľný až keď je pre každý side effect určený stable operation key, retry owner, timeout, unknown-outcome path a provider read-back.

## 9. Porovnávacia os code a UI authority

Vizuálny workflow zrýchľuje integrácie a review business flowu, ale môže komplikovať large-scale code review, merge conflicts a automated refactoring. Code-first workflow zlepšuje použitie type systemu, tests a štandardných review nástrojov, no môže znížiť prístupnosť pre operations a domain expertov.

Rozhodnutie sa nerobí podľa osobného vkusu. Tím overí, či vie pinovať exact generation, reprodukovať render, vykonať policy checks, oddeliť secrets a overiť deployment z commit SHA až po live execution.

## 10. Human approval a manual work

n8n má prirodzené komunikačné a approval integrácie; Temporal môže držať durable wait cez Signals alebo Updates; Airflow a Prefect môžu koordinovať manuálne gates, ale často nie sú primárnym case-management systémom. Approval state musí byť viazaný na exact subject, approver identity, expiry a post-approval revalidation bez ohľadu na runtime.

Ak proces potrebuje rich case UI, comments, attachments a delegation, samostatný ticket alebo case-management system môže byť authority a orchestrator iba reaguje na jeho events. Workflow UI nesmie byť náhradou za chýbajúci business record.

## 11. Event-driven schopnosti

Všetky porovnávané platformy dokážu byť spustené eventom alebo API callom, ale event-driven capability neznamená rovnakú message semantics. Treba rozlíšiť ingestion trigger, durable event log, per-key ordering, consumer offset, replay, dead-letter handling a exactly-once business effect.

Platforma môže prijať webhook a vytvoriť run, no broker alebo event log môže zostať samostatnou authority. Event envelope a deduplication contract musia prežiť presun medzi platformami.

## 12. Data movement a payload boundaries

Orchestrator metadata store nie je data lake ani binary archive. Veľké payloads, model artifacts a document batches sa ukladajú do object storage alebo domain store a workflow prenáša immutable references, checksums a schema generation.

n8n binary mode, Airflow XCom, Prefect results a Temporal payloads majú limity a odlišnú retention. Selection test preto používa realistický payload, nie iba malé demo JSON.

## 13. Scale a concurrency

Scale sa hodnotí podľa počtu concurrent runs, task fan-out, event rate, payload size, polling load, worker startup latency a external rate limits. Replica count alebo queued-task throughput bez downstream constraints nie je business capacity.

Temporal task queues, Airflow executors/workers, Prefect work pools a n8n queue workers majú vlastné backpressure a failure domains. Capacity plan musí zahŕňať databázu, broker, object storage, API quotas a observability pipeline.

## 14. Versioning a replay

Runtime upgrade alebo workflow change môže ovplyvniť rozpracované executions. Temporal replay vyžaduje deterministic compatibility a versioning, Airflow Dag code generation musí zostať dostupná pre task execution, Prefect deployment version a code storage musia byť dohľadateľné a n8n retry s current workflow môže zmeniť semantics pôvodného inputu.

Každá platforma preto potrebuje release manifest, compatibility policy a test rozpracovaného execution počas upgradu. Green fresh run nestačí.

## 15. Operability a evidence

Operátor potrebuje run identity, resolved workflow generation, inputs, attempts, waits, worker, logs, metrics, traces, outputs a business correlation. Produktové dashboardy sú views; authoritative evidence musí byť exportovateľné a viazané na retention.

Výber runtime-u zahŕňa on-call model, backup/restore, disaster recovery, audit export, SLO a troubleshooting. Platforma, ktorú tím nevie bezpečne prevádzkovať, nie je správna ani pri ideálnom feature fit-e.

## 16. Security a tenant isolation

Credentials, code execution, network access, worker identity a tenant scope sa posudzujú ako samostatné boundaries. Low-code connector s broad credential a Python task s broad cloud role môžu mať rovnaký blast radius.

Selection proof obsahuje negative tenant test, secret rotation, credential revocation, untrusted-input test a audit actor identity. UI role bez downstream authorization nestačí.

## 17. Cost model

Náklady zahŕňajú licenciu alebo cloud usage, workers, databázu, broker, storage, egress, observability, operations čas a migration cost. Lacný runtime môže byť drahý, ak vyžaduje ručné reconciliation alebo nevie reprodukovať incident.

AI-assisted workflows pridávajú model tokeny a evaluation cost. Cost budget sa viaže na business operation a alternatívny deterministic alebo human path.

## 18. Coexistence namiesto jedného víťaza

Veľká platforma často používa viac orchestrátorov: Airflow alebo Prefect pre data products, Temporal pre transaction sagas a n8n pre SaaS a human communication integrations. Shared event contracts a domain APIs zabránia, aby tieto runtimes priamo zapisovali do cudzích interných state stores.

Coexistence vyžaduje jasného end-to-end process ownera. Rozdelenie nesmie vytvoriť štyri retry owners a neviditeľné handoffs.

## 19. Decision record

Architecture decision record zachytí use case, invariants, considered options, evidence, rejected alternatives, risks, exit strategy a acceptance tests. Produktová marketingová veta nie je evidence.

Record viaže konkrétne verzie a deployment model. Revaliduje sa pri zmene event rate, compliance, runtime generation alebo business criticality.

## 20. Incident AGENT-AUTO-14

V incidente bol 30-dňový approval wait uložený iba v n8n execution history, hoci retention bola kratšia než business deadline. Po update workflowu operátor retryol execution s aktuálnou definíciou a zmenil idempotency key generation.

Rovnaký proces prijal redelivered event, spustil druhý build a AI CI remediation preskočila flaky test. Observability agent potom vyhodnotil absent error series ako recovery. Problém nebol v jednom produkte, ale v nesprávnom ownership modeli naprieč runtime, eventom, CI a evidence.

## 21. Competing hypotheses pri výbere

Zlyhanie môže byť spôsobené nesprávnym runtime-om, ale aj chybným domain contractom, broad credentials, missing idempotency, nevhodnou retention alebo neoperovateľným deploymentom. Migrácia platformy bez odstránenia týchto príčin iba presunie incident.

Proof-of-concept preto testuje failure hypotheses, nie iba happy-path authoring. Každý kandidát musí prejsť crash, duplicate event, long wait, version upgrade, provider timeout a business reconciliation.

## 22. Containment a recovery

Pri zistení nesprávneho runtime ownershipu sa najprv zastaví mutation alebo promotion, zachová execution evidence a domain operations sa reconciliujú. Rozpracované instances sa nemigrujú blind exportom.

Recovery môže použiť strangler pattern: nové operations idú cez nový orchestrator, staré zostanú pinned na pôvodnej generation a shared business ledger koordinuje status. Exit criteria zahŕňajú nulové duplicate side effects a reprodukovateľný rollback.

## 23. Positive acceptance

Test vytvorí rovnaký bounded use case vo vybranom runtime-e, simuluje worker crash, redelivery, long wait a upgrade a zachová stable operation identity. Po obnove sa technical state aj business outcome zhodujú.

Operátor vie z execution evidence určiť exact workflow generation a provider reference. Druhý use case s odlišným failure modelom overí, že selection rules nie sú šité na jeden demo scenár.

## 24. Forbidden acceptance

Platforma nesmie byť vybraná iba podľa počtu konektorov, benchmarku alebo AI-generated demo. Execution success nesmie nahradiť business read-back.

Retry na current definition nesmie potichu meniť rozpracovanú operation a migration nesmie zahodiť approvals, operation IDs alebo audit chain. Očakáva sa nulový unauthorized alebo duplicate side effect.

## 25. Recovery acceptance

Po nesprávnom výbere sa proces preklopí na bounded hybrid architecture bez straty authoritative business state-u. Staré executions sa dokončia alebo deterministicky reconciliujú.

Recovery drill obnoví databázu alebo control plane, znovu pripojí workers a overí waiting instances, timers a event offsets. Alternate test vykoná rollback jednej platformy bez poškodenia susedného orchestrátora.

## 26. Practical runtime-selection record

Runtime-selection record viaže rozhodnutie na konkrétnu capability a testovateľné invariants. Nejde o marketingové scorecard; každý kandidát má explicitný fit, gap a boundary voči domain authority.

Nasledujúci príklad zámerne vyberá hybridný model. Jedna platforma nemusí vlastniť transaction saga, SaaS komunikáciu aj batch enrichment, pokiaľ sú handoffs typed a majú jedného operation ownera.

```yaml
decision:
  id: ORCH-2026-014
  capability: customer-onboarding
  business_authority: crm-onboarding-ledger
  invariants:
    - no-duplicate-account
    - approval-bound-to-request-digest
    - resumable-for-45-days
    - provider-outcome-reconciled
  candidates:
    n8n:
      fit: saas-integration-and-human-notification
      gap: long-lived-state-requires-external-ledger
    temporal:
      fit: durable-transaction-saga
      gap: higher-code-and-operations-cost
    airflow:
      fit: nightly-batch-enrichment
      gap: not-request-saga-authority
    prefect:
      fit: python-data-enrichment-flow
      gap: business-state-remains-external
  selected:
    durable_process: temporal
    saas_notifications: n8n
    batch_enrichment: airflow
  acceptance:
    - worker-crash
    - duplicate-event
    - provider-timeout
    - workflow-upgrade
    - restore-and-reconcile
```

## 27. Primary sources

n8n execution history a retry behavior, vrátane možnosti retry s aktuálne uloženým workflowom, dokumentuje https://docs.n8n.io/workflows/executions/all-executions/. Queue mode, shared database, workers a broker boundary sú popísané v https://docs.n8n.io/hosting/scaling/queue-mode/. Tieto stránky podporujú integration a operational semantics, nie tvrdenie, že n8n execution je business ledger.

Temporal Workflow Execution ako durable, recoverable execution s event history a replay dokumentuje https://docs.temporal.io/workflow-execution. Retry Policies a hranicu medzi deterministic Workflow code a failure-prone Activities opisuje https://docs.temporal.io/encyclopedia/retry-policies. Temporal durability koordinuje process state; external side effects stále potrebujú idempotency a reconciliation.

Apache Airflow 3.3 sa oficiálne opisuje ako platforma pre batch-oriented workflows na https://airflow.apache.org/docs/apache-airflow/stable/. Dag, task dependency a data-interval model sú na https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html a event-driven scheduling cez assets a watchers na https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/event-scheduling.html.

Prefect flow a deployment model je na https://docs.prefect.io/v3/concepts/flows a https://docs.prefect.io/v3/concepts/deployments. Events a automations, ktoré môžu spúšťať deployments pri prítomnosti alebo absencii eventov, dokumentujú https://docs.prefect.io/v3/concepts/events a https://docs.prefect.io/v3/how-to-guides/automations/creating-deployment-triggers. Porovnanie v kapitole je architecture inference z týchto current primary semantics, nie univerzálny produktový ranking.

## Zhrnutie

n8n je silný integration runtime, Temporal durable application orchestrator, Airflow batch/data Dag platforma a Prefect Python-first flow orchestrator. Produkčný výber musí priradiť durable state, retry, event offset, approval a business outcome konkrétnemu authority ownerovi a preukázať ho failure injectionom.

Ďalšia kapitola rozoberie event-driven automation od event envelope cez broker semantics až po idempotent business effect.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Workflow engine oproti agent frameworku](workflow-engine-vs-agent-framework.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Event-driven automation →](event-driven-automation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
