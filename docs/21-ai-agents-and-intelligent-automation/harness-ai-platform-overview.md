# Harness AI platform overview

Harness AI platform treba chápať ako súbor oddelených AI-assisted a agentic surfaces nad spoločným Harness control plane, nie ako jeden model s univerzálnou autoritou. Bezpečný návrh zachováva RBAC, resource scope, policies, secrets, connectors, audit a runtime acceptance ako deterministic boundaries mimo modelu.

Blok 41–44 používa incident `AGENT-HARNESS-11`. AI-generated pipeline a connector prešli formálnou validáciou, ale nesprávny project scope, guidance-only AI Rule, nevyplnený secret, mutable Worker Agent a príliš široký MCP access vytvorili zelenú execution bez požadovaného resource outcome-u.

Nosný lifecycle tejto kapitoly je:

```text
business alebo delivery intent
→ exact account, org, project, resource a generation
→ capability surface: UI, IDE/MCP alebo pipeline agent
→ prompt context, rules, RBAC, policies a privacy route
→ proposal a deterministic validation
→ authorized apply a effective-state read-back
→ execution a business verification
→ containment, reconciliation a rollback
→ forbidden, recovery a second-operation acceptance
```

## 1. Harness AI nie je jedna funkcia

Harness AI je capability layer rozložená cez tri pracovné prostredia: Harness UI, vývojárske IDE alebo terminál a pipeline execution. DevOps Agent pomáha vytvárať a meniť platformové resources, IDE integrácie sprístupňujú Harness cez MCP a Worker Agents vykonávajú autonómne úlohy ako pipeline steps.

Tieto povrchy majú rozdielne authority boundaries. Konverzačný návrh v UI nie je pipeline execution, MCP call z IDE nie je schválená production zmena a Worker Agent output nie je automaticky business post-condition.

## 2. Exact platform subject

Incident sa neviaže na neurčité „Harness AI“, ale na composed subject: account, organization, project, module, resource identifier, pipeline commit alebo inline generation, agent definition version, model connector, MCP connector set, AI Rules snapshot, RBAC principal a runtime input generation.

Bez tohto subjectu sa nedá reprodukovať, prečo rovnaký prompt vytvoril odlišný resource alebo prečo agent v jednej pipeline mal inú capability než v druhej.

## 3. Account enablement a scope

Harness AI sa zapína na account úrovni a podľa konfigurácie môže byť scope alebo override správanie delegované nižšie. Enablement iba sprístupní capability; neudeľuje automaticky právo čítať, vytvárať alebo spúšťať všetky resources.

Acceptance preto overuje effective setting v správnom account scope a následne samostatne RBAC, module entitlement a connector access. Zelený toggle nie je authorization proof.

## 4. Tri capability areas

V UI sa AI používa na pipeline configuration, failure analysis a resource authoring. V IDE alebo termináli sa Harness operácie vykonávajú cez MCP klienta a server. V pipeline sa Worker Agent spúšťa ako containerized step s vlastným modelom, inputs, connectors a runtime identity.

Toto rozdelenie je dôležité pri incidente: UI conversation, MCP session a pipeline execution majú rozdielne correlation IDs, audit events, credentials a replay semantics.

## 5. Harness Platform authority

Harness Platform poskytuje spoločné user management, RBAC, secrets, connectors, audit a notifications pre moduly. AI vrstva tieto platformové controls používa, ale nenahrádza ich.

Model môže navrhnúť service, environment alebo connector, no authoritative resource vznikne až po úspešnom platform API write a read-backu z exact account/org/project scope.

## 6. Module entitlement

AI capability môže pracovať iba s modulmi, ku ktorým má účet a principal prístup. Prompt požadujúci CD stage v CI-only scope nesmie byť interpretovaný ako oprávnenie obísť module boundary.

Workflow pred mutation overí module availability a potrebné schemas. Failure sa vráti ako explicitný unsupported alebo unauthorized outcome, nie ako improvizovaný generic resource.

## 7. RBAC zostáva rozhodujúci

Harness používa additive RBAC model založený na role a resource-group assignments. AI návrh ani MCP tool nesmú rozšíriť effective permissions nad principal alebo scoped token.

Pre každú mutation sa eviduje actor, delegated agent identity, required permission, target resource group a authorization decision. Forbidden test používa rovnaký prompt s principalom bez edit permission a očakáva nulový write.

## 8. AI Rules verzus policy enforcement

Harness AI Rules sú reusable instructions, ktoré dávajú AI kontext pred vytvorením, editáciou alebo review resource. Sú guidance vrstva: zlepšujú návrh, ale nie sú authoritative enforcement boundary.

OPA Policy as Code alebo iný deterministic gate musí nezávisle odmietnuť porušenie. Incident `AGENT-HARNESS-11` vzniká práve vtedy, keď tím považuje vetu v AI Rule za policy, hoci generated YAML ju môže obísť.

## 9. Prompt context a provenance

Model dostáva user prompt a relevantný Harness context, napríklad pipeline metadata alebo error logs. Každý context fragment má source, scope, freshness a sensitivity classification.

Untrusted repository text, PR title, execution log alebo error message sa nesmie zlúčiť so system instructions. Prompt-injection containment oddeľuje data channel od instruction channel a obmedzí tools, ktoré môže daný surface použiť.

## 10. Data privacy boundary

Harness dokumentuje, že Harness-managed AI features nepoužívajú customer content na training a používajú provider paths s nulovou retention pre popísané managed scenáre. Toto tvrdenie sa aplikuje na konkrétnu managed path, nie automaticky na BYO model connector alebo custom MCP server.

Composed manifest preto označí, či ide o Harness-managed chat, managed fallback, direct provider connector alebo custom service. Privacy acceptance sa viaže na exact route a zmluvný scope.

## 11. Model routing a fallback

DevOps Agent a Harness AI Chat používajú Harness-managed provider routing, zatiaľ čo Worker Agents môžu používať model connectors. Primary a fallback route môžu mať odlišný model, behavior a retention contract.

Fallback sa nesmie aktivovať iba podľa availability. Pred použitím musí prejsť rovnakou schema, tool-selection, refusal, latency, privacy a security acceptance ako primary generation.

## 12. Secrets boundary

Harness AI môže vytvoriť secret resource shell, ale secret value sa nemá posielať modelu a musí sa doplniť cez chránený secret workflow. Model-generated placeholder nesmie byť zamieňaný za funkčnú credential binding.

Acceptance overí, že resource existuje, value bola vložená mimo model path, connector používa správnu secret reference a provider read-back potvrdí exact identity bez expozície hodnoty.

## 13. Connector boundary

Connector je platformový resource, ktorý viaže endpoint, authentication a scope. AI môže navrhnúť alebo vytvoriť connector definition, no usable connector vyžaduje valid credentials, network reachability, permissions a connection test.

Incident môže vyzerať ako model error, hoci skutočná príčina je connector smerujúci do iného accountu alebo regiónu. Read-back preto zahŕňa endpoint fingerprint a provider identity.

## 14. Resource lifecycle

Bezpečný lifecycle je propose, review, deterministic validation, authorized apply, platform read-back a business verification. Save v UI alebo successful API response predstavuje iba medzistav.

Pri Git-backed resource sa navyše oddeľuje remote Git commit, Harness resolved YAML a effective execution generation. Každý transition má ownera a rollback path.

## 15. Audit trail

Audit trail zaznamenáva platformové mutations a identity, ale agent trajectory, model prompt a external provider side effect môžu byť v iných evidence stores. Jeden audit event preto nie je úplný príbeh.

Incident bundle koreluje conversation, accepted proposal, API mutation, resource generation, pipeline execution, Worker Agent logs, MCP calls a downstream outcome bez ukladania secretov alebo nadbytočných customer payloadov.

## 16. Observability

Platform metrics, execution logs, model telemetry a business SLIs sledujú odlišné vrstvy. AI response latency nevysvetľuje, či resource bol správne vytvorený; pipeline success rate nevysvetľuje, či nasadená služba spĺňa požadovaný outcome.

Dashboard používa bounded labels: account/project, capability surface, agent version, model generation, tool class a outcome category. High-cardinality prompt text sa nepoužíva ako metric label.

## 17. Availability nie je correctness

Harness UI môže byť dostupné a model môže odpovedať, hoci RBAC, connector alebo policy API zlyháva. Worker Agent môže skončiť úspešne, hoci output gate použije nesprávny default.

Readiness preto testuje minimálny bezpečný end-to-end path s read-only operation, exact scope a read-backom. Mutation readiness vyžaduje samostatný controlled canary.

## 18. Composed release manifest

Manifest viaže Harness release surface, pipeline definition, agent version, model connector, model name, MCP endpoints, rules, policies, inputs, secrets, permissions a expected schemas. Alias `latest` bez resolved digestu rozbíja reprodukovateľnosť.

Pri incidente manifest umožní zistiť, či sa zmenil model, agent image, MCP capability list alebo policy, aj keď pipeline YAML ostal rovnaký.

## 19. Shared incident AGENT-HARNESS-11

Používateľ požiadal DevOps Agent o optimalizáciu release pipeline a vytvorenie chýbajúceho connectora. Návrh prešiel schema validation a používateľ ho prijal, ale project scope bol odvodený z predchádzajúcej konverzácie, AI Rule bola iba guidance a secret resource zostal bez hodnoty.

Následný Worker Agent používal mutable definition, široký hosted MCP connector a nejednoznačný output. Pipeline bola zelená, no intended environment nebol aktualizovaný. Incident sa preto klasifikuje ako composed authority a verification failure, nie ako jediná „halucinácia“.

## 20. Containment

Containment vypne mutation-capable AI surfaces alebo ich prepne na draft/read-only mode, zastaví affected pipeline triggers a zmrazí exact manifests. Outstanding approvals a tokens sa invalidujú podľa scope.

Tím neregeneruje pipeline opakovaným promptom. Najprv identifikuje uskutočnené writes, reconciliuje resources a zachová evidence pre root-cause analýzu.

## 21. Recovery

Recovery obnoví správny scope, connector binding, secret value, deterministic policy gate, pinned agent/model/MCP generations a explicitný output contract. Zmeny sa promujú cez review a canary.

Affected resources sa porovnajú s desired state a opravujú idempotentne. Unknown external outcomes sa najprv read-backnú, aby retry nevytvoril duplicate.

## 22. Positive acceptance

Positive test vytvorí alebo upraví low-risk resource v isolated project scope. Evidence obsahuje proposal diff, policy pass, authorized actor, platform read-back, expected audit event a downstream safe execution.

Test sa opakuje s druhým resource identifierom, aby sa vylúčilo cacheovanie alebo hard-coded success.

## 23. Forbidden acceptance

Principal bez edit permission, prompt s cudzím project ID, AI Rule conflict a unavailable secret musia skončiť bez write. Rovnako sa odmietne model-generated authority field alebo MCP endpoint mimo allowlistu.

Forbidden test kontroluje nulový počet resource mutations a nulové použitie privileged connectora, nie iba error text v UI.

## 24. Recovery acceptance

Recovery test obnoví resource a pipeline zo známého manifestu po úmyselnom drift evente. Overí Git/Harness state, connector identity, secret reference, policies, agent definitions a business read-back.

Restore je úspešný až po second-operation teste na inom resource a po potvrdení, že stará agent alebo MCP generation už nemôže vykonať write.

## 25. Prevádzkový ownership

Platform owner spravuje enablement, model routing a account controls; module owners vlastnia resource schemas a policies; security spravuje RBAC, secrets a connector trust; product owner definuje business acceptance.

AI tím nevlastní automaticky downstream resources. Runbook explicitne uvádza eskalácie pre provider, platform, pipeline, MCP a business-system incidents.

## 26. Čo platform overview nepreukazuje

Dokumentácia a configuration review nepreukazujú reálnu availability, privacy behavior providerov, správnosť generated resources ani safe autonomous execution. Tieto tvrdenia vyžadujú runtime evidence.

Kapitola preto zostáva conceptual a operational design, nie označenie `Verified` alebo `Stable` pre konkrétny Harness tenant.

## Primárne zdroje

- https://developer.harness.io/docs/platform/harness-ai/overview/
- https://developer.harness.io/docs/platform/harness-ai/core-capabilities/
- https://developer.harness.io/docs/platform/harness-ai/harness-ai-rules/
- https://developer.harness.io/docs/platform/get-started/overview/
- https://developer.harness.io/docs/platform/role-based-access-control/rbac-in-harness/
- https://developer.harness.io/docs/platform/governance/audit-trail/

## Zhrnutie

Kapitola ukazuje, že harness ai platform overview sa nesmie redukovať na dostupnosť AI funkcie alebo úspešný model response. Authoritative proof vzniká až spojením exact subjectu a generation, deterministic scope a identity, policy enforcementu, execution evidence, downstream read-backu, failure semantics a opakovateľného recovery testu.

## Navigácia

- Predchádzajúca kapitola: [Production hardening a troubleshooting](production-hardening-troubleshooting.md)
- Nasledujúca kapitola: [DevOps Agent pre pipeline a resource operations](devops-agent-pipeline-resource-operations.md)
