# Agent interoperability a protocol evolution

Agent interoperability znamená, že nezávislé agent systems dokážu objaviť capabilities, dohodnúť transport a content contract, vytvoriť alebo pokračovať v tasku, vymeniť artifacts a bezpečne interpretovať terminal či interrupted state. Neznamená, že zdieľajú rovnakú memory, tools, model, policy alebo interný reasoning.

Táto kapitola uzatvára `AGENT-OPS-03`. Lokálny operations supervisor delegoval provider diagnostics remote agentovi cez A2A-compatible endpoint. Agent Card bol cacheovaný pred upgradeom, remote skill zmenil output schema a task state semantics, no local adapter stále mapoval starý `completed` result na „provider healthy“. Súčasne MCP tool executor vykonal failover podľa nesprávne syntetizovaného artifactu. Wire communication prešla, ale semantic interoperability zlyhala.

Nosný lifecycle je:

```text
business delegation intent
→ remote agent identity a trust
→ Agent Card alebo capability manifest generation
→ protocol version a binding selection
→ security requirement a tenant context
→ exact message, context a task identity
→ typed task lifecycle a artifacts
→ interruption, auth alebo input-required handling
→ local policy a semantic validation
→ authoritative outcome read-back
→ compatibility, deprecation a migration evidence
```

## 1. Interoperabilita nie je iba konektivita

Dva systémy sú connected, ak si vymenia bytes. Sú syntakticky interoperabilné, ak rozumejú transportu a schema. Sú semanticky interoperabilné až vtedy, keď rovnako interpretujú identity, task states, artifacts, errors, authorization a business meaning.

Najnebezpečnejší failure je úspešná syntaktická komunikácia s odlišnou semantics. Taký incident často nevytvorí protocol error a môže skončiť false successom.

## 2. Agent-to-agent verzus agent-to-tool

MCP štandardizuje prístup hosta alebo agenta k tools, resources a prompts. A2A štandardizuje komunikáciu s nezávislým agentom, ktorý si ponecháva vlastnú internú memory, tools a orchestration.

Remote agent preto nie je iba „veľký tool“. Môže viesť multi-turn task, vyžiadať input alebo authentication, streamovať updates a produkovať viac artifacts. Local system musí udržať task lifecycle a delegation policy, nie iba function-call response.

## 3. Kedy použiť remote agent

Remote agent je vhodný, keď capability vlastní iný tím alebo vendor, potrebuje vlastný long-running state, izolované credentials, domain workflow alebo opaque proprietary implementation. Pri jednoduchej stateless operácii býva presný tool contract lacnejší a predvídateľnejší.

Interoperability protocol nemá byť výhovorka na zbytočné multi-agent rozdelenie. Každá remote boundary pridáva discovery, auth, latency, versioning, data disclosure a recovery cost.

## 4. Exact remote subject

Local run zaznamenáva remote provider, Agent Card digest, agent version, selected interface, protocol version, skill ID, security scheme a endpoint identity. Human-readable agent name nie je stable subject.

```yaml
remote_agent:
  provider: payments-platform
  agent_card_url: https://agents.payments.example.com/.well-known/agent-card.json
  agent_card_digest: sha256:7ac1...
  agent_version: 4.2.0
  skill_id: provider-diagnostics
  skill_contract: provider-diagnostics/v3
  interface:
    url: https://agents.payments.example.com/a2a/v1
    binding: HTTP+JSON
    protocol_version: "1.0"
  tenant: retail-eu
```

Ak Agent Card alebo skill contract zmení digest po approvale či počas tasku, local system musí uplatniť compatibility a trust policy.

## 5. Agent Card

Agent Card je self-describing manifest identity, interfaces, capabilities, skills, input/output modes a security requirements remote agenta. Pomáha discovery a routing, ale descriptions a examples zostávajú claims remote providera.

Local registry pridáva vlastný trust status, owner, allowed environments, review date, data classification a approved skill versions. Agent Card signature alebo TLS identity overuje pôvod, nie pravdivosť každého capability claimu.

## 6. Card discovery

Discovery môže používať well-known location, registry alebo explicitnú configuration. Dynamic URL dodaný modelom sa nesmie automaticky fetchovať a následne považovať za trusted agent.

Endpoint allowlist, DNS/TLS verification, SSRF protection a tenant policy sa aplikujú pred načítaním cardu. Redirect na iný origin môže zmeniť trust boundary a vyžaduje nové rozhodnutie.

## 7. Card caching

Agent Card cache potrebuje TTL, digest, ETag alebo generation a invalidation. Cache sa môže používať pre routing, ale high-impact task pred odoslaním overí current compatible interface a skill contract.

Card refresh počas existujúceho tasku nemení automaticky task semantics. Task zostáva viazaný na remote generation, ktorá ho prijala, alebo sa explicitne migruje.

## 8. Protocol version

A2A interface deklaruje protocol version. Major/minor compatibility sa nepredpokladá bez conformance matrix a loaded binding evidence.

Client pinne supported range a zaznamená exact version použitú pre task. Fallback na staršiu verziu môže zmeniť task states, artifact fields, extensions alebo auth behavior a preto nie je invisible transport detail.

## 9. Protocol bindings

A2A môže byť exponované cez core bindings, napríklad JSON-RPC, gRPC alebo HTTP+JSON podľa interface manifestu. Binding mení serialization, streaming, error mapping a infrastructure path, ale nemá meniť business skill semantics.

Multi-binding server sa testuje na semantic parity. Ak HTTP adapter mapuje interrupted state na terminal error, zatiaľ čo gRPC ho zachová, interfaces nie sú kompatibilné napriek spoločnému backendu.

## 10. Security schemes

Agent Card publikuje security schemes a requirements. Local client vyberá scheme podľa policy, získava credential pre canonical remote resource a uchováva ho mimo model contextu.

Authentication local agenta neznamená delegation user authority. Remote request musí prenášať alebo mapovať end-user/tenant context podľa dohodnutého trust modelu a remote agent musí vykonať vlastnú authorization.

## 11. Identity propagation

Interoperabilita potrebuje rozlíšiť caller agent, end user, tenant, organization, business operation a technical client. Jeden bearer token bez auditovateľnej delegation chain môže vytvoriť confused deputy.

Remote agent nemá dôverovať user ID z message textu. Identity claims pochádzajú z authenticated transport alebo signed delegation artifactu a sú porovnané s task scope.

## 12. Skills

Skill je deklarovaná capability agenta s ID, description, tags, examples, modes a prípadnými security requirements. Local router používa skill ID a contract generation, nie iba embedding similarity nad description.

Skill selection je proposal. Policy môže zakázať skill pre production, citlivé data alebo mutation path aj keď remote agent tvrdí, že ho podporuje.

## 13. Message identity

Každá message má stable `message_id`, role, parts a prípadný task/context association. Retry alebo redelivery rovnakej message používa rovnakú identity.

Nový message ID znamená nový protocol event. Server môže inak vytvoriť duplicate task, opakovať input alebo zmeniť context history.

## 14. Context identity

Context ID zoskupuje súvisiace interactions, ale nie je automaticky business operation ID. Jeden context môže obsahovať viac tasks a jedna business operation môže byť rozdelená medzi viac remote contexts.

Local ledger preto uchováva mapping operation → delegation → remote context/task. Context ID nesmie byť reuse medzi tenantmi alebo nezávislými user journeys.

## 15. Task identity

Task je core remote unit of work s server-generated ID, context, status, artifacts a history. Local client po prvom response uloží task ID durable a pri reconnecte pokračuje cez get/subscribe/message continuation podľa protocolu.

Znovu odoslať initial message bez pôvodného task identity môže vytvoriť nový task. Preto network retry pred získaním task ID potrebuje client message deduplication alebo server-side operation correlation.

## 16. Task states

A2A 1.0 definuje submitted, working, completed, failed, canceled, input-required, rejected, auth-required a unspecified state. Local adapter nesmie zredukovať všetky non-completed states na generic error.

`input_required` a `auth_required` sú interrupted states, ktoré môžu pokračovať. `failed`, `canceled` a `rejected` sú terminal, ale každý má inú recovery a business meaning.

## 17. Terminal state nie je business proof

Remote `completed` znamená, že remote agent považuje task za dokončený podľa svojho contractu. Local supervisor ešte validuje required artifacts, schemas, provenance a local business invariant.

Remote diagnostics task môže byť completed aj keď nevedel overiť provider health a vrátil artifact `inconclusive`. Local synthesis ho nesmie mapovať na healthy.

## 18. Parts a media types

Messages a artifacts môžu niesť text, files alebo structured data. Local host povoľuje iba expected media types, size, URI schemes a data classifications.

File URL sa nesťahuje bez SSRF, malware, integrity a authorization controls. Structured data sa validuje proti local versioned schema, nie iba proti generic JSON parse.

## 19. Artifacts

Artifact je task output s identity, name, description, parts a metadata. Pri streaming updates môže rovnaký artifact ID dostávať append chunks a final marker.

Client udržiava order, deduplication a integrity. Chýbajúci chunk alebo duplicate append nesmie vytvoriť ticho poškodený report, ktorý supervisor použije ako evidence.

## 20. Streaming

Streaming znižuje latency a prináša status/artifact updates, ale komplikuje reconnect, ordering a partial results. Client zaznamenáva last accepted event alebo artifact generation a po reconnecte používa supported subscription/resume path.

Stream end bez terminal eventu je unknown task state, nie failure ani completion. Client načíta task cez authoritative get endpoint.

## 21. Push notifications

Push notifications umožňujú updates pri disconnected clientovi. Callback URL, task token a authentication sú citlivé capability a musia byť scoped na konkrétny task.

Receiver validuje remote identity, task ID, token, replay protection a event ordering. Push payload je hint; pri high-impact transitione sa task state potvrdí cez authenticated read-back.

## 22. Return-immediately a asynchronous work

Client môže požiadať, aby send vrátil task okamžite namiesto čakania na terminal alebo interrupted state. To je vhodné pre dlhé jobs, ale local orchestration musí následne vlastniť polling, subscription, timeout a cancellation.

HTTP `202` alebo task `submitted` nepreukazuje, že remote worker začal. Schedule delay a queue saturation sú samostatné hypotheses.

## 23. Input required

Remote agent môže požiadať o doplňujúce input. Local system nesmie automaticky odpovedať z model-generated guessu, ak ide o user intent, secret alebo approval.

Input request sa preloží do typed local interruption s exact remote task identity. Odpoveď sa validuje, autorizuje a odošle ako nová message v tom istom task/context scope.

## 24. Auth required

`auth_required` znamená, že task potrebuje ďalší authentication alebo authorization step. Local client musí zobraziť alebo vykonať správny flow pre current user a canonical remote agent.

Credential sa neposiela ako text message. Po získaní nového tokenu sa overí, že task stále čaká, policy a user intent sú aktuálne a remote generation sa nezmenila nekompatibilne.

## 25. Cancellation

Cancel request je protocol operation. Remote task môže už dokončiť side effect pred spracovaním cancellation.

Local state používa `cancel_requested`, následne authoritative remote task read-back a potom business reconciliation. Terminal `canceled` stále nemusí znamenať rollback už vytvorených artifacts alebo externých effects.

## 26. Error mapping

Transport error, protocol error, task failed, task rejected a business-negative artifact sa nesmú spojiť do jedného `RemoteAgentError`. Každý typ má inú retry, escalation a user communication.

Adapter zachová original code, task state, message, remote version a correlation IDs. Retry policy sa rozhoduje až v local orchestration vrstve.

## 27. Stable delegation identity

Local delegation má vlastné ID a stable message key. Spája business operation s remote agent/taskom naprieč network retries a worker recovery.

```yaml
delegation_id: del-checkout-021-provider-diagnostics
operation_id: checkout-recovery-021
remote_agent_digest: sha256:7ac1...
skill_contract: provider-diagnostics/v3
client_message_id: msg-del-021-01
remote_task_id: task-99318
remote_context_id: ctx-4412
status: working
```

Ak response s task ID chýba, local system vyhľadáva podľa supported correlation alebo eskaluje. Nevytvára bezhlavo novú delegation.

## 28. Semantic output contract

Local client definuje required artifact schema nezávisle od prose description. Remote output obsahuje source refs, observed interval, confidence, unresolved hypotheses a result status.

```json
{
  "contract": "provider-diagnostics/v3",
  "provider": "provider-a",
  "status": "degraded",
  "observed_window": {
    "from": "2026-08-04T15:20:00Z",
    "to": "2026-08-04T15:35:00Z"
  },
  "evidence_refs": ["trace-set:psp-771", "metric-query:latency-992"],
  "confidence": 0.91,
  "unresolved": ["regional-routing-drift"]
}
```

Textový artifact možno zobraziť človeku, ale autonomous synthesis používa validated structured contract.

## 29. Contract versioning

Skill version a output contract version sa môžu vyvíjať oddelene. Backward-compatible addition je iná než zmena enum meaning, required evidence alebo terminal semantics.

Consumer-driven contract tests používajú recorded fixtures a live conformance environment. „JSON sa stále parsuje“ nie je dôkaz semantic compatibility.

## 30. Extensions

Extensions pridávajú optional protocol semantics. Agent Card označuje URI, required flag a params; client povoľuje iba známe extensions a exact versions.

Required extension, ktorému client nerozumie, vedie k fail-closed. Optional extension sa môže ignorovať iba vtedy, ak core task semantics zostanú kompletné bez nej.

## 31. Binding a extension governance

Protocol evolution potrebuje pravidlá, kto mení core schema, bindings a extensions, ako prebieha review, conformance a deprecation. Implementácia nemá sledovať iba SDK latest tag.

Architecture decision record uvádza pinned protocol, binding, extensions, support window a migration ownera. Upgrade je release s testami, nie dependency bot merge bez semantic review.

## 32. Deprecation

Deprecated feature zostáva počas definovaného obdobia použiteľná, ale nový development sa presúva na replacement. Consumer inventory ukazuje, ktoré agents, gateways a tasks stále používajú starú semantics.

Removal sa plánuje podľa loaded telemetry, nie iba source-code searchu. Dlhé remote tasks môžu prežiť rollout a potrebujú compatible worker/interface až do terminal state alebo migrácie.

## 33. Version negotiation

Negotiation vyberá spoločnú wire version, ale nemusí zaručiť compatible skill semantics. Po negotiation client stále porovná Agent Card, skill contract a required extensions.

Auto fallback je zakázaný pre high-risk delegation, ak staršia verzia nevie vyjadriť required identity, interrupted states alebo security control. Fail-fast je bezpečnejší než silent semantic downgrade.

## 34. Translation gateway

Gateway môže prekladať medzi protocol versions alebo bindings. Tým sa stáva semantic authority a musí mať explicitný mapping contract, loss report a own generation.

Gateway nesmie mapovať neznámy task state na completed, zahodiť artifact metadata alebo vymyslieť idempotency identity. Nezobraziteľná semantics vedie k explicitnému unsupported erroru.

## 35. Conformance testing

Conformance test overuje wire schema, required methods, state transitions, streaming, errors a security metadata. Nestačí na business correctness skillu, ale znižuje protocol ambiguity.

Každý supported agent/version pair prechádza protocol conformance a domain contract tests. Production canary následne overí actual auth, latency, task recovery a artifact semantics.

## 36. Compatibility matrix

Matrix uvádza local client generation, protocol versions, bindings, remote agent versions, skill contracts a extensions. Stav `supported` je opretý o konkrétny test run a date.

```yaml
compatibility:
  local_client: ops-supervisor/v8.4
  remote_agent: payments-diagnostics/4.2
  protocol: "1.0"
  binding: HTTP+JSON
  skill: provider-diagnostics/v3
  extensions:
    - uri: https://example.com/a2a/evidence/v1
      required: true
  conformance_run: a2a-conf-20260804-17
  domain_contract_run: diag-contract-881
```

Missing combination nie je automaticky compatible. Router ju nepoužije v production.

## 37. Rolling upgrade

Remote agent upgrade môže bežať vedľa starej generation. New tasks smerujú na canary, existing tasks zostávajú pinned na owner generation alebo sú migrované explicitným protocol flowom.

Load balancer nesmie posielať pokračovanie tasku workerovi, ktorý nepozná jeho state, pokiaľ backend state nie je skutočne shared a schema compatible. Task ID je routing/recovery subject.

## 38. Rollback

Rollback interface alebo agent code nevracia automaticky artifacts či side effects vytvorené novou generation. Najprv sa inventarizujú active tasks a ich contract versions.

Nové tasks možno presmerovať na known-good version, kým affected tasks sa dokončia, zrušia alebo reconciliujú. Rollback acceptance zahŕňa aj local adapter a registry cache.

## 39. Observability

Trace spája local operation/delegation, Agent Card digest, protocol/binding, message/context/task IDs, task transitions, artifact IDs/digests, auth subject, extension set, adapter generation a local synthesis decision.

Metrics sledujú route failures, negotiation downgrade, unsupported extension, duplicate task creation, interrupted-state latency, stream reconnect, schema rejection a false terminal success zistený local verificationom.

## 40. Multi-tenant isolation

Tenant context je enforced v transport/auth, task store, push callback, artifact storage a local mappingu. Remote agent nesmie reuse task/context ID naprieč tenantmi bez server-side isolation.

Local agent neodosiela artifacts z jedného tenant tasku do druhého contextu. Reference task IDs sa validujú rovnako ako primary task association.

## 41. Incident `AGENT-OPS-03`

Local registry cacheoval Agent Card pre payments diagnostics version `4.1` a skill `provider-diagnostics/v2`. Remote endpoint prešiel na version `4.2`, kde status `completed` mohol niesť artifact `inconclusive` a evidence sa presunulo do structured data partu.

Starý adapter čítal iba text part a mapoval každé completed na `healthy=true`. Supervisor preto povolil failover na provider, ktorý remote agent v skutočnosti označil za neoverený. Po stream disconnecte local worker navyše odoslal initial message znova a vytvoril druhý task.

Opravený chain bol:

```text
refresh and verify Agent Card
→ pin protocol, binding and skill contract
→ stable delegation and message identity
→ create one remote task
→ resume/get same task after disconnect
→ validate structured artifact status and evidence
→ preserve inconclusive result
→ local policy blocks remediation
→ current provider and checkout read-back
```

## 42. Failure hypotheses

Interoperability incident sa analyzuje od discovery po local business interpretation. Wire success je začiatok diagnostiky, nie koniec.

- **Stale Agent Card** — client routoval podľa starej skill/interface generation; porovná sa cached a served digest.
- **Version downgrade** — negotiation alebo gateway použili staršiu protocol semantics bez required controlu.
- **Binding skew** — HTTP, gRPC alebo JSON-RPC adapter mapoval state či errors rozdielne.
- **Duplicate initial message** — reconnect vytvoril nový task, pretože client message identity nebola stable.
- **Task association loss** — message použila nesprávny context/task pair a remote agent začal novú vetvu.
- **Interrupted-state collapse** — input-required alebo auth-required bolo mapované na failed/completed.
- **Artifact schema drift** — local adapter ignoroval nový field, enum meaning alebo media type.
- **Extension mismatch** — required extension bola ignorovaná alebo rozdielne versionovaná.
- **Identity propagation gap** — remote agent vykonal task pod nesprávnym user/tenant authority.
- **False semantic success** — remote completed artifact bol inconclusive alebo negative, ale local synthesis ho interpretoval ako úspech.

Každá hypotéza sa testuje cez served card, registry cache, wire/task trace, adapter mapping, artifact bytes/schema a local decision record. Prose summary remote agenta sa nepoužíva ako jediný dôkaz.

## 43. Containment

Pri interoperability incidente sa zakáže konkrétna remote agent/skill/version kombinácia. Router použije local read-only fallback alebo known-good agent generation.

Active tasks sa neodstránia. Zaznamenajú sa ich protocol, owner generation a last state; mutations závislé od ich outputs sa pozastavia do revalidation.

## 44. Recovery

Recovery opraví registry/card invalidation, version pinning, adapter mapping, task deduplication, auth delegation alebo artifact schema. Affected artifacts sa znovu interpretujú z raw immutable parts, nie z už skresleného summary.

Compatibility matrix sa aktualizuje iba po conformance, domain contract a failure-recovery tests. Stale approvals a synthesis decisions sa nevykonajú dodatočne.

## 45. Positive acceptance

Pozitívny test objaví trusted agent, vyberie podporovaný interface a skill, odošle stable message, prijme task, spracuje working a interrupted states, načíta structured artifact a potvrdí local business invariant.

Stream disconnect sa obnoví cez rovnaký task. Počet remote tasks pre jednu delegation zostane jeden.

## 46. Forbidden acceptance

Zakázaný test podstrčí unsigned alebo neapproved Agent Card, required unknown extension, incompatible skill schema, cross-tenant task ID alebo silent protocol downgrade. Client musí delegation odmietnuť.

Ďalší test vráti `completed` s artifactom `inconclusive`. Local policy nesmie z toho vytvoriť positive remediation evidence.

## 47. Recovery acceptance

Recovery test zmení remote generation počas tasku, preruší stream, rotuje token, pošle duplicate push notification a vráti artifacts po chunks. Local system musí zachovať task identity, deduplikovať events a zložiť validný final artifact alebo explicitne eskalovať.

## 48. Second-operation acceptance

Nová delegation po upgrade použije current Agent Card a contract, nový local delegation/message ID a nový remote task. Nesmie zdediť starý context, auth interruption ani artifact cache.

Tým sa overí, že migration opravila nové operations bez prepisu histórie predchádzajúceho tasku.

## 49. Zhrnutie

Agent interoperability je viacvrstvový contract: identity, discovery, version, binding, security, message/task lifecycle, artifacts a local semantic validation. Protocol umožňuje spoluprácu opaque agents, ale neprenáša automaticky dôveru ani business correctness.

Bezpečná evolúcia vyžaduje pinned revisions, compatibility matrix, conformance tests, explicitné deprecation a migration pravidlá a loaded-state telemetry. Najdôležitejšia otázka nie je „vedia sa agenti rozprávať?“, ale „vedia obe strany pre rovnakú task identity rovnako interpretovať state, artifacts, authority a outcome aj počas upgradeu, retry a recovery?“
