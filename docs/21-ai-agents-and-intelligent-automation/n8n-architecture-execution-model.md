# n8n architecture a execution model

n8n je workflow automation engine, ktorý načíta definíciu workflowu, prijme trigger event, vytvorí execution a postupne vyhodnotí uzly a ich spojenia. Nie je to iba vizuálny editor: produkčné správanie závisí od exact workflow version, publish/activation state, runtime configuration, database, queue, workers, task runners, credentials, binary storage a downstream systémov.

Táto kapitola otvára incident `AGENT-N8N-07`. Objednávkový webhook mal po nasadení novej mapovacej logiky vytvoriť jeden refund-review ticket, ale upstream provider dostal `504`, event zopakoval a n8n vytvorilo dve executions. Prvý worker používal staršiu runtime generation, druhý načítal novú workflow version; oba vykonali side effect, zatiaľ čo dashboard ukazoval iba jeden úspešný business záznam, pretože druhý zápis skončil v inom tenant konte.

Nosný lifecycle je:

```text
business workflow a owner
→ exact saved a published workflow version
→ trigger registration a runtime configuration generation
→ ingress alebo scheduler prijme event
→ execution identity a input snapshot
→ main/webhook process rozhodne execution path
→ worker alebo local executor načíta workflow, credentials a data
→ node-by-node state transitions a external side effects
→ execution record, logs, binary data a business read-back
→ retry, recovery a second-event acceptance
```

## 1. Workflow engine verzus agent

Deterministický n8n workflow má explicitný graph, nodes, connections a parameter mapping. Aj keď niektorý node volá LLM alebo AI Agent node, orchestration boundary zostáva workflowová: trigger, routing, credentials, retries, persistence a side effects riadi n8n execution model.

Agentická časť môže rozhodovať o ďalšom tool calle, ale nesmie sa zameniť za celý runtime. Incident môže vzniknúť v queue, expression mappingu alebo credential scope aj vtedy, keď model odpovedal správne.

## 2. Control plane a execution plane

Editor, workflow storage, user/project permissions, credential management a publish/activation operácie tvoria control-plane funkcie. Execution plane prijíma events, načítava published workflow, vyhodnocuje nodes a komunikuje s externými systémami.

Rozdelenie nie je absolútna procesná hranica v každom deployment mode, ale je dôležité pre reasoning. Control-plane status „workflow active“ nepreukazuje, že každý worker načítal rovnakú generation alebo že downstream side effect dosiahol intended outcome.

## 3. Exact execution subject

Troubleshooting nezačína názvom workflowu, ale exact subjectom. Ten obsahuje instance, environment, workflow ID, saved version, published/active version, execution ID, trigger identity, runtime image, configuration digest, worker identity, credential references a event identity.

Bez tejto identity sa porovnávajú nekompatibilné executions. Dve executions s rovnakým workflow name môžu používať inú published version, node package, timezone, encryption key alebo downstream credential generation.

## 4. Workflow definition

Workflow definition opisuje nodes, connections, parameters, settings, static data references a trigger configuration. Je to desired orchestration graph, nie dôkaz o tom, čo konkrétna execution skutočne načítala a vykonala.

Definition musí mať stable workflow ID a version alebo digest. Exportovaný JSON bez environment, credential stubs, runtime version a publish state nie je úplný release manifest.

## 5. Saved, published a active state

Uložená editovaná verzia môže byť odlišná od verzie používanej produkčnými triggers. Source-control alebo UI operácia môže preniesť saved content, zatiaľ čo produkčné spúšťanie vyžaduje osobitné publish alebo activation rozhodnutie podľa použitej n8n generation.

Operational read-back preto rozlišuje editor-visible draft, published version a effective trigger registration. „Vidím zmenu na canvase“ nie je dôkaz, že nová execution použila túto zmenu.

## 6. Main process

Main process typicky poskytuje editor/API funkcie, koordinuje workflow metadata a podľa deployment mode môže prijímať alebo vykonávať workflow work. V queue mode odovzdáva execution work do Redis-backed queue, aby ho spracovali workers.

Jeho dostupnosť a load ovplyvňujú control plane aj ingress paths. Horizontal scaling bez jasného ownershipu pre webhooks, encryption key, database migrations a queue settings môže vytvoriť split-brain-like behavior na aplikačnej vrstve.

## 7. Webhook processors

Pri škálovaných deploymentoch možno webhook ingress oddeliť od main procesu. Webhook processor prijme HTTP request, nájde registered trigger, vytvorí execution context a podľa konfigurácie odovzdá work ďalej.

Oddelenie znižuje tlak na editor/main proces, ale pridáva routing, base URL, load balancer a queue dependencies. HTTP `2xx` z edge vrstvy ešte nemusí znamenať, že workflow side effect bol commitnutý.

## 8. Workers

Worker načíta execution job, workflow definition a required runtime state a potom vykonáva nodes. Viac workers zvyšuje concurrency, ale iba ak majú kompatibilnú n8n version, rovnakú encryption key, dostupné custom nodes, network policy a shared storage assumptions.

Worker identity patrí do execution evidence. Ak jedna replika používa starší image alebo chýbajúci community node, intermittent failure sa môže javiť ako náhodný API problém.

## 9. Task runners

Task runners izolujú alebo presúvajú vykonávanie podporovaného user code z hlavného n8n procesu. Ich hardening, network access, available modules, timeouts a version compatibility sú samostatnou execution boundary.

Code node success preto nepreukazuje rovnaký isolation model vo všetkých environments. Runner môže mať inú filesystem alebo egress viditeľnosť než worker, ktorý orchestration koordinuje.

## 10. Database ako authoritative store

Produkčné workflow metadata, credentials metadata a execution records sa ukladajú do podporovanej database; pre škálované self-hosted prostredie je typickou voľbou PostgreSQL. Database je authority pre persistovaný control a execution state, ale nie pre externý business outcome.

Database backup bez encryption key, binary store a kompatibilnej runtime version nemusí byť obnoviteľný systém. Restore test musí overiť načítanie workflows, decrypt credentials, trigger registration a representative execution.

## 11. Redis a queue mode

V queue mode Redis prenáša execution jobs medzi producerom a workers. Redis nie je náhradou za workflow database ani business idempotency ledger; drží coordination a queue state podľa deployment konfigurácie.

Queue delivery môže viesť k opakovaniu worku po timeoutoch alebo worker failure. Externé mutation nodes preto potrebujú vlastnú idempotency a reconciliation hranicu.

## 12. Execution identity

Každá execution má identity, status, start/end timestamps, workflow reference a vstupné/výstupné data podľa retention policy. Execution ID koreluje technický run, nie automaticky upstream event alebo downstream business operation.

Event ID a business operation key musia byť zachované osobitne. Jeden event môže vytvoriť viac executions a jedna execution môže vykonať viac externých operations.

## 13. Execution status

Status ako running, waiting, success alebo failed opisuje stav n8n execution. `success` znamená, že graph skončil podľa runtime semantics bez neobslúženej chyby; neznamená, že externý systém prijal intended business state alebo že mapping použil správneho tenanta.

Waiting execution môže legitímne čakať na timer, webhook continuation alebo human input. Monitoring musí odlišovať očakávané waiting od stalled worku a retention cleanupu.

## 14. Manual a production execution

Manual execution slúži na interaktívne testovanie a môže používať test trigger, pinned data alebo editor state. Production execution vzniká z published/active trigger pathu a pracuje s reálnym eventom a production credentials.

Manual green test je dôležitý, ale nepreukazuje registration, reverse proxy, queue routing, worker generation ani provider retry behavior. Acceptance musí obsahovať production-like event cez intended ingress.

## 15. Node execution order

n8n vyhodnocuje graph podľa connections, branch availability a node semantics. Vizuálna poloha node na canvase neurčuje execution order; authority má graph a runtime scheduler.

Pri branches a merges treba rozumieť, ktoré input items sú dostupné a kedy. Chybný predpoklad o poradí môže viesť k stale data, duplicate callu alebo node, ktorý sa nespustí pre chýbajúcu vetvu.

## 16. Execution data

Execution data obsahujú node inputs, outputs, errors a metadata podľa save/retention nastavení. Sú cenné pre replay a debugging, ale môžu obsahovať citlivé payloads alebo byť zámerne neuložené.

Observability design musí vedieť, čo sa neuchováva. Neprítomný payload v UI nie je dôkaz, že node payload nespracoval; môže ísť o retention, redaction alebo failed persistence.

## 17. Binary data

Files a ďalšie binary payloads majú samostatný storage lifecycle. Filesystem mode viaže dostupnosť na konkrétny storage layout, zatiaľ čo external object storage pridáva credential, region, lifecycle a compatibility dependencies.

Database execution record môže existovať bez dostupného binary objectu. Recovery preto overuje metadata aj actual read z binary store a jeho retention policy.

## 18. Concurrency a backpressure

Concurrency určuje, koľko executions môže postupovať paralelne. Viac concurrency znižuje queue delay iba dovtedy, kým database, Redis, CPU, memory, provider rate limits a downstream services zvládajú zvýšený tlak.

Bez backpressure sa latency incident môže zmeniť na retry storm. Capacity control musí sledovať queue depth, oldest job age, running count, provider throttling a business deadline.

## 19. Queue mode scaling

Queue mode škáluje execution workers nezávisle od editor/main procesu. Scaling unit však nie je iba Pod alebo container; musí zahŕňať runtime image, custom nodes, encryption key, task-runner generation, network policy a storage access.

Mixed-version fleet môže vytvoriť behavior drift. Upgrade sa uzatvára až po loaded-version evidence zo všetkých execution paths a representative second evente.

## 20. Durability boundary

Persistovaný execution record pomáha diagnostike a retry, ale n8n nemôže atomicky commitnúť vlastný status spolu s ľubovoľným externým API. Crash po external commit a pred local persistence vytvára unknown outcome.

Durability workflowu preto nie je side-effect exactly-once guarantee. Bez downstream idempotency key a authoritative read-back môže retry zopakovať mutation.

## 21. Configuration generation

Runtime behavior ovplyvňujú environment variables, feature flags, timezone, endpoints, execution retention, queue, runners a security settings. Každý deployment má mať configuration generation alebo digest viazaný na image a rollout.

Environment variable prítomná v manifest file nie je loaded proof. Process-level read-back, startup logs alebo runtime diagnostics musia ukázať effective value bez zverejnenia secretu.

## 22. Shared incident `AGENT-N8N-07`

Workflow `order-refund-review` version `12.4` bol uložený a publikovaný v produkcii, ale jeden worker zostal na runtime image `2.6.3` a druhý prešiel na `2.6.4`. Reverse proxy timeoutol synchronnú webhook response po 30 sekundách, upstream event zopakoval a queue doručila dve jobs s rovnakým provider event ID.

Nová Code transformácia navyše neuchovala item linking a downstream expression vybrala credential context z prvého itemu. Jedna execution vytvorila ticket v správnom tenantovi, druhá v zdieľanom operations projekte; obe skončili `success`.

## 23. Competing failure hypotheses

Prvá hypotéza je duplicate webhook delivery po timeout response. Druhá je queue redelivery po worker failure, tretia mixed-version runtime behavior, štvrtá chybný item mapping a piata downstream API retry bez idempotency.

Hypotézy sa nerozhodnú podľa jedného success statusu. Potrebujú provider delivery log, ingress request ID, execution IDs, worker/image identity, queue attempts, node inputs, credential reference a downstream ledger.

## 24. Evidence preservation

Pred deaktiváciou alebo retry sa zachovajú upstream event ID a signature metadata, raw payload digest, ingress timestamp, execution IDs, workflow version, worker identity, queue attempt, node result digests a downstream object IDs. Sensitive payload sa uloží podľa access a retention policy, nie do verejného incident chatu.

Healthy comparator z rovnakého workflowu a obdobia je rovnako dôležitý. Umožní odlíšiť system-wide generation drift od jedného malformed eventu.

## 25. Containment

Containment prepne endpoint na rýchly acknowledgement alebo dočasný durable intake, zastaví nové mutation nodes a ponechá read-only enrichment. Provider retries sa nesmú slepo vypnúť, kým nie je jasné, ktoré events neboli prijaté.

Mixed-version workers sa vyberú z trafficu a queue sa nezmaže. Pending jobs sa klasifikujú podľa event identity a unknown outcome, aby cleanup neodstránil jedinú kópiu nevybaveného eventu.

## 26. Recovery

Recovery zjednotí runtime generation, opraví mapping a zavedie business idempotency key odvodený z provider eventu a operation class. Každý unknown outcome sa najprv prečíta z downstream authority a až potom sa rozhodne o retry alebo compensation.

Published workflow, trigger registration, credential generation a worker-loaded state sa overia samostatne. Queue sa uvoľňuje canary events s kontrolovaným tenant scope.

## 27. Positive acceptance

Jeden validný production-like event vytvorí jednu execution chain a jeden intended downstream object. Evidence prepája event ID, execution ID, worker generation, workflow version, node results a business record.

Latency zostane pod provider timeoutom alebo endpoint včas potvrdí durable acceptance. Dashboard, execution record a downstream read-back sa zhodujú.

## 28. Forbidden acceptance

Release sa nepovažuje za úspešný iba preto, že manual run je zelený, workflow je active alebo execution má status `success`. Neprípustné sú mixed worker versions, untracked duplicate events, cross-tenant output a retry bez unknown-outcome read-backu.

Rovnako sa nesmie vymazať queue alebo execution history ako prvý recovery krok. Taký zásah znižuje tlak, ale ničí causal evidence a môže stratiť work.

## 29. Recovery acceptance

Recovery drill simuluje timeout po external commit a pred local persistence. Opakovaný event musí nájsť existujúci downstream operation cez idempotency key a skončiť bez druhého side effectu.

Drill zároveň odstaví jeden worker počas execution. Queue a runtime obnovia progress bez cross-tenant mappingu a bez straty audit correlation.

## 30. Second-event acceptance

Druhý event s iným tenantom a iným payload shape prejde cez rovnakú published version a fleet generation. Nesmie zdediť item, credential, binary object ani static data z prvého eventu.

Test dokazuje isolation aj absence residue. Jeden happy-path event by cache, static data alebo branch-specific defect nemusel odhaliť.

## 31. Praktický execution manifest

Execution manifest zhromažďuje identity, ktoré bežný n8n status nerozlišuje. Slúži ako incident a acceptance artifact, nie ako náhrada platformových records.

Manifest sa vytvára bez raw secrets a obsahuje digests alebo references. Každý field má authoritative source a freshness.

```yaml
execution_subject:
  instance: n8n-prod-eu
  environment: production
  workflow_id: wf_refund_review
  saved_version: 12.5-draft
  published_version: 12.4
  workflow_digest: sha256:91c2...
  execution_id: 884219
  trigger:
    type: webhook
    provider_event_id: evt_019af2
    request_id: req_7712
  runtime:
    n8n_version: 2.6.4
    image_digest: sha256:4f81...
    worker_id: worker-07
    config_digest: sha256:7a10...
  queue_attempt: 1
  credential_refs: [cred_ticketing_tenant_acme]
  business_operation_key: refund-review/evt_019af2
```

## 32. Prevádzkové metriky

Sledujú sa executions podľa statusu, queue depth, oldest waiting age, worker saturation, event-to-start delay, end-to-end latency, duplicate event rate, unknown outcomes, cross-version executions, binary read failures a cost na accepted business outcome. Metriky sa segmentujú podľa workflow, tenant, trigger a runtime generation.

Aggregate success rate môže skryť tenant-specific alebo branch-specific incident. Alert preto používa risk slices a business reconciliation, nie iba počet failed executions.

## 33. Primárne zdroje

- [n8n Docs — Architecture overview](https://docs.n8n.io/hosting/architecture/overview/)
- [n8n Docs — Configuring queue mode](https://docs.n8n.io/hosting/scaling/queue-mode/)
- [n8n Docs — Concurrency control](https://docs.n8n.io/hosting/scaling/concurrency-control/)
- [n8n Docs — Execution data](https://docs.n8n.io/hosting/scaling/execution-data/)
- [n8n Docs — All executions](https://docs.n8n.io/workflows/executions/all-executions/)
- [n8n Docs — Task runners](https://docs.n8n.io/hosting/configuration/task-runners/)
- [n8n Docs — External storage for binary data](https://docs.n8n.io/hosting/scaling/external-storage/)

## 34. Zhrnutie

n8n production outcome vzniká cez composed runtime: saved a published workflow, trigger registration, main alebo webhook process, queue, worker, task runner, database, binary storage, credentials a downstream system. Žiadna jednotlivá control-plane obrazovka nepreukazuje celý chain.

Spoľahlivý návrh viaže každý event na exact execution subject, oddeľuje workflow durability od external side-effect safety a uzatvára recovery authoritative business read-backom. Queue scaling je bezpečné až vtedy, keď všetky execution paths načítajú kompatibilnú generation a druhý event preukáže absence duplication a residue.
