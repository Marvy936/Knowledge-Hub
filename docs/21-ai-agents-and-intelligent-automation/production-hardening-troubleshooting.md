# Production hardening a troubleshooting

Production hardening n8n AI workflowu znamená zmenšiť capability surface, oddeliť deterministic controls od model behavior, pinovať všetky runtime generations a pripraviť recovery pre chyby modelu, toolu, memory, retrieval, approval, queue, database a provider side effectu. Green health endpoint alebo úspešná agent execution nepreukazuje bezpečný business outcome.

Táto kapitola uzatvára incident `AGENT-N8N-10`. Po postupných opravách agent, approval a RAG vrstvy bola funkcionalita správna v stagingu, ale production mala starší task-runner image, povolený generic HTTP tool, odlišný model fallback a chýbajúce negative tests. Pri model-provider degradácii sa workflow prepol na neotestovaný model, ktorý vytvoril iný tool argument shape; output parser opravil textovú odpoveď, no commit wrapper dostal default customer scope a operation skončila v quarantine.

Nosný hardening lifecycle je:

```text
business risk a threat model
→ composed release manifest
→ minimal nodes, tools, credentials a network reach
→ isolated code/task execution
→ policy, approval, idempotency a tenant controls
→ representative eval a adversarial tests
→ staged promotion a canary
→ process, execution a business telemetry
→ incident containment, reconciliation a rollback
→ second-operation a restore acceptance
```

## 1. Production boundary

Production environment zahŕňa n8n main, webhook processors, workers, task runners, PostgreSQL, Redis, binary/execution storage, model providers, vector stores, approval channels a business APIs. Hardening jedného containeru nepokrýva celý trust path.

Composed manifest viaže versions, images, workflow publications, model IDs, tool contracts, credentials, prompts, memory a index generations. Bez tejto väzby sa incident zredukuje na nepresné tvrdenie „n8n bolo aktuálne“.

## 2. Threat model

Threat model rozlišuje neúmyselnú model chybu, malicious user input, prompt injection z retrieved source, compromised credential, insider workflow edit, vulnerable community node, SSRF a provider inconsistency. Každá hrozba má odlišný prevention a detection control.

Agent nemá byť hodnotený iba podľa happy-path utility. Threat scenarios skúšajú, či vie získať cudzie data, obísť approval, spustiť všeobecný network call alebo opakovať side effect po timeout.

## 3. Minimal node surface

`NODES_EXCLUDE` blokuje vybrané nodes pre users a môže odstrániť Execute Command alebo Read/Write Files from Disk z dostupného surface. Production allow/deny policy vychádza z workflow requirements a user trust.

Blokovanie UI node nie je jediný control; existing workflows, community nodes a indirect sub-workflows sa inventarizujú. Security audit a source-control validation odhaľujú zakázané types pred publication.

## 4. Generic capability reduction

Generic HTTP, Code, Execute Command, filesystem a database-query capabilities majú vysoký blast radius. Uprednostňujú sa úzke wrapper workflows alebo app operations s fixným destination, method a credential.

Ak generic tool zostane, dostane network allowlist, schema bounds, response filtering a approval podľa risku. Modelom riadený URL alebo SQL text sa nepovažuje za bežný production parameter.

## 5. Task runner isolation

Code node executions sa v self-hosted deploymentoch hardenujú external task runners v oddelených containers. Distroless image, unprivileged `nobody` user, read-only root filesystem, obmedzené `/tmp` a AppArmor znižujú blast radius.

Isolation sa overí negatívnym testom čítania process environment, mountov, host filesystemu a neautorizovanej siete. Samotná konfigurácia sidecaru nie je proof, ak runner stále zdieľa secrets alebo privileged volume.

## 6. SSRF protection

HTTP-capable nodes a tools môžu byť zneužité na prístup k loopback, link-local, cloud metadata alebo interným admin endpoints. SSRF protection a network egress policy blokujú destinations mimo explicitne povoleného business scope.

DNS allowlist bez ochrany proti rebindingu alebo redirectom nestačí. Validation sa aplikuje na resolved address pri každom hop a internal services používajú authentication aj pri privátnej sieti.

## 7. Reverse proxy a public endpoints

Reverse proxy ukončuje TLS, nastavuje trusted forwarding headers a routuje editor, webhook a streaming endpoints podľa deployment modelu. Public exposure sa minimalizuje a management alebo metrics endpoints zostávajú interné.

Webhook URL, host, protocol a proxy trust musia zodpovedať effective external route. Nesprávna konfigurácia vytvára invalid callbacks, insecure cookies alebo spoofed client identity.

## 8. Authentication a user management

Instance owner, admin, project roles, SSO a MFA určujú, kto môže meniť workflows, credentials a source-control settings. Shared workflow môže umožniť editorovi používať credentials prítomné vo workflowe aj bez priameho credential sharingu.

Projects a roles sa preto navrhujú podľa capability, nie iba organizačnej štruktúry. Production authoring sa obmedzuje a protected instance alebo one-way promotion znižuje local drift.

## 9. Credentials a external secrets

Credentials sú šifrované spoločným encryption key a workers potrebujú správnu key generation. Provider secrets sa rotujú, scopeujú na exact tenant a environment a podľa možností načítavajú z external secret authority.

Rotation sa uzatvára effective provider identity read-backom. Nový secret v manageri nepreukazuje, že všetky workers ho načítali alebo že starý principal už nemá access.

## 10. Environment variables a `_FILE`

Sensitive environment values sa podľa capability načítajú zo secret-mounted files namiesto plaintext deployment manifestu. Orchestrator obmedzí read access a neexponuje secrets do debug outputu.

Env var precedence môže prepísať UI configuration, napríklad observability settings. Composed manifest preto eviduje effective values a restart/reload semantics.

## 11. Workflow promotion

Production používa source-control promotion, review, generated validation a explicitné publish/activation kroky. Saved workflow, Git commit a effective published runtime sú tri rozdielne states.

Promotion manifest obsahuje parent a child workflows, error workflows, tool contracts, credentials, variables, model, prompt, memory a index generations. Canary overí business-safe read path pred povolením mutation trafficu.

## 12. Model pinning a fallback

Primary aj fallback model sú explicitne pinované a prešli rovnakými tool-calling, refusal, structured-output, latency a safety tests. Provider alias typu `latest` sa nepoužíva pre uncontrolled mutation workflow.

Fallback strategy môže znížiť capability. Pri degradácii je bezpečnejšie prepnúť na read-only answer alebo human handoff než na lacnejší model, ktorý neprešiel tool contract acceptance.

## 13. Prompt a tool versioning

System message, tool descriptions, `$fromAI()` parameter instructions a output schema sú versioned release artifacts. Aj malá textová zmena môže zmeniť selection a arguments.

Semantic diff a evaluation porovnajú trajectories, nielen finálny text. Prompt hotfix bez workflow publication a composed manifestu vytvára neauditovaný runtime drift.

## 14. Tenant isolation

Tenant ID a authenticated subject sa vkladajú deterministicky a propagujú cez tools, memory, retrieval, execution metadata a audit. Model ich nesmie vytvoriť ani meniť.

Negative tests používajú kolidujúce IDs, semantic twin documents a shared provider credentials. Úspech znamená nulový cross-read aj cross-write, nie iba správnu odpoveď v bežnom teste.

## 15. Idempotency a side effects

Každý mutation tool používa stable business operation key, atomic ledger a provider-native idempotency alebo read-back. n8n execution retry nie je business deduplication.

Unknown outcome sa quarantinuje a reconciliuje. Automatický retry celej agent trajectory môže zopakovať už úspešný tool, preto mutation count a operation state sú deterministic.

## 16. Approval hardening

Sensitive tools sú za immutable approval envelope s reviewer authorization, digestom, expiry a freshness revalidation. Deny a timeout nesmú byť obídené alternate toolom.

Approval channel outage vytvorí pending alebo escalated state, nie fail-open. Outstanding tokens sa invalidujú pri deployment rollbacku, policy change alebo credential rebindingu podľa scope.

## 17. RAG hardening

Knowledge workflows používajú authoritative source manifest, tenant/ACL metadata, pinned embedding, blue-green index, effective-date filter, citations a abstention. Retrieved text sa považuje za untrusted data.

Mixed generations, missing metadata alebo stale watermark môžu zablokovať high-risk answer. Vector-store availability sama neotvára production traffic.

## 18. Memory hardening

Memory key je tenant-safe a viazaný na authenticated subject a conversation. Retention, trimming a poisoning controls bránia cross-session leakage a persistent prompt injection.

Memory sa nepoužíva ako approval, operation alebo customer authority. Recovery vie invalidovať jednu session alebo celú generation bez mazania unrelated tenant data.

## 19. Resource limits

Execution má wall-clock timeout, max agent iterations, model token budget, tool timeout, max payload, binary size a mutation count. Task runners a containers majú CPU, memory, process a filesystem limits.

Limit breach vytvorí explicitný outcome a zachová evidence. OOM kill alebo timeout po external commit sa klasifikuje ako unknown outcome, nie automaticky failed-before-side-effect.

## 20. Concurrency a backpressure

Global a workflow concurrency chránia provider, PostgreSQL, Redis a memory/vector backends. Worker autoscaling rešpektuje database connection budget a downstream rate limits.

Queue depth bez ready worker a dependency saturation contextu je zlý scaling signal. Backpressure môže spomaliť alebo odmietnuť low-priority tasks namiesto destabilizácie celej platformy.

## 21. Execution retention

Execution history, binary objects, approval ledger, audit events a provider evidence majú koordinované retention policies. Debug convenience nesmie viesť k neobmedzenému ukladaniu prompts, tool arguments a personal data.

Pruning sa testuje spolu s incident a compliance requirements. Authoritative operation ledger nesmie zmiznúť len preto, že n8n execution bola odstránená.

## 22. Logging a redaction

Logs obsahujú workflow, execution, node, tenant-safe correlation, tool class a error category. Secrets, full prompts, memory content, retrieved documents a customer payload sa redigujú alebo ukladajú iba v explicitne chránenom store.

Debug level sa zapína časovo obmedzene a s ownerom. Log output nie je audit ledger a môže byť incomplete pri process crash alebo destination outage.

## 23. Metrics

Metrics sledujú process readiness, queue waiting/active/failed, worker saturation, database connections, Redis latency, model errors, tool latency, approval expiry, retrieval empty rate a business outcomes. Labels majú bounded cardinality.

Alerty používajú symptom plus dependency context. Vysoká agent success rate je zavádzajúca, ak business read-back zlyháva alebo tools vracajú partial results.

## 24. OpenTelemetry

Workflow a node spans môžu niesť execution identity, model/tool latency a trace context cez HTTP a sub-workflows podľa current capability. Queue deployment nastaví tracing na všetkých relevantných process roles.

Sampling nesmie odstrániť všetky errors alebo high-risk mutations. Sensitive prompts a tool results sa neexportujú automaticky; agent tracing input/output recording sa nastaví podľa privacy policy.

## 25. Security audit

Built-in `n8n audit` alebo audit API reportuje unused credentials, risky database expressions, filesystem nodes, risky/community/custom nodes, unprotected webhooks, missing settings a outdated instance. Report je discovery input pre remediation.

Passing audit nepreukazuje tenant isolation, provider scope alebo safe agent behavior. Organizácia pridáva vlastné controls pre prompts, tool schemas, model generations, approval a RAG metadata.

## 26. Pre-production tests

Test suite pokrýva deterministic unit contracts, workflow integration, model/tool evaluation, adversarial prompts, cross-tenant isolation, approval replay, duplicate events, provider timeout a RAG stale index. Test data nesmie používať production credentials.

Candidate sa spúšťa v isolated environment s exact release manifestom. Passing happy path bez forbidden a recovery tests neotvára mutation traffic.

## 27. Canary

Canary začína read-only alebo draft operations pre malý tenant alebo synthetic subject. Sleduje trajectories, tool selection, latency, abstention a business post-conditions.

Mutation canary používa reverzibilný alebo low-impact action s independent read-back. Percent traffic sa zvyšuje iba pri stable evidence, nie iba po uplynutí času.

## 28. Kill switch

Kill switch dokáže deaktivovať mutation tools, konkrétny workflow, model provider, tenant alebo celú agent capability bez odstránenia evidence. Control je rýchly, auditovaný a pravidelne testovaný.

Read-only fallback môže zostať dostupný, ak je bezpečný. Kill switch nesmie závisieť od toho istého poškodeného AI workflowu, ktorý má zastaviť.

## 29. Troubleshooting decomposition

Incident sa rozdelí na input/auth, workflow publication, model, prompt, tool selection, argument validation, credential, provider, memory, retrieval, approval, queue a persistence. Každá vrstva má authoritative read-back.

Tím nezačína náhodnou zmenou promptu. Najprv identifikuje exact generation a prvú boundary, kde observed state odbočil od expected state.

## 30. Symptom: agent nevolá tool

Možné príčiny zahŕňajú nejasnú description, model bez správnej tool-calling podpory, prompt konflikt, iteration limit, nedostupný sub-node alebo chýbajúci input. Execution trace ukáže, či tool bol advertised a či model navrhol call.

Recovery upraví contract alebo model až po reprodukcii. Násilné promptovanie „vždy volaj tool“ môže vytvoriť zbytočné calls pri otázkach, ktoré tool nepotrebujú.

## 31. Symptom: nesprávne tool parameters

Príčinou môže byť `$fromAI()` na authority field, ambiguous schema, sub-node first-item semantics, stale memory alebo fallback model. Porovná sa raw model proposal, normalized envelope a effective node parameters.

Containment zablokuje affected tool contract. Oprava presunie identity a security values do deterministic bindingu a pridá forbidden parameter tests.

## 32. Symptom: správny call, nesprávny účet

Najprv sa overí authenticated tenant, memory key, credential provider identity, metadata filter a child-workflow mapping. Validný provider response nevylučuje confused deputy, ak credential smeruje na iný account.

Affected operations sa reconciliujú podľa provider references. Prompt change bez opravy credential alebo tenant bindingu incident nevyrieši.

## 33. Symptom: approval stojí alebo sa zopakoval

Kontroluje sa waiting execution, channel delivery, callback authentication, expiry, atomic transition a queue retry. Duplicate message môže byť notification retry, nie nový business request.

Outstanding tokens sa neaktivujú manuálnym DB editom. Recovery používa ledger a vytvorí nový scoped request iba po invalidácii starého.

## 34. Symptom: RAG odpovedá starou policy

Overí sa source revision, ingestion watermark, index alias, embedding generation, effective-date filter, retrieval chunks a citations. Model môže správne sumarizovať nesprávny evidence set.

Containment prepne na known-good generation alebo abstention. Reindex bez delete/supersession kontroly môže starý dokument ponechať aktívny.

## 35. Symptom: workflow success, business failure

n8n execution môže skončiť success, aj keď tool absorboval error, odpoveď bola partial alebo provider operation zostala pending. Business SLI a post-condition read-back sú preto oddelené od execution statusu.

Recovery číta operation ledger a provider state. Celú execution nereplayuje, kým nie je známe, ktoré side effects už nastali.

## 36. Shared incident `AGENT-N8N-10`

Production fallback model vytvoril parameter `customerRef` namiesto očakávaného `customerId`. Output parser opravil finálny response object, ale generic wrapper použil default scope a poslal request do quarantine po authorization konflikte.

Main, workers aj model endpoint boli healthy a workflow skončil controlled errorom. Incident odhalil, že fallback contract nebol testovaný, generic tool zostal dostupný a alert neobsahoval model/tool generation ani authoritative customer binding.

## 37. Containment

Mutation tools sa deaktivujú kill switchom, fallback model sa odstráni z routing policy a affected workflow sa vráti na known-good composed release. Pending a unknown operations sa inventarizujú podľa stable operation keys.

Evidence sa uchová pred pruningom: workflow publication, model response/tool proposal po redakcii, normalized parameters, policy result, credential fingerprint a provider read-back. Platform môže ponechať read-only support odpovede, ak RAG a tenant controls sú validné.

## 38. Recovery

Recovery pridá fallback model contract suite, odstráni generic commit path, zavedie typed wrapper bez default tenant scope a rozšíri alert context. Candidate prejde adversarial, cross-tenant, stale-memory, approval a RAG tests.

Canary najprv vykoná read a draft flow a potom jednu bounded mutation s independent verification. Rollback sa testuje spolu s outstanding approvals a in-flight operations.

## 39. Acceptance

Pozitívny test preukáže exact composed generation, tenant-safe context, správny tool, bounded parameters, citations alebo approval a authoritative business outcome. Recovery test simuluje timeout po provider commit a obnoví rovnakú operation bez duplicate.

Forbidden test skúša SSRF, blocked node, cross-tenant memory/RAG, approval replay, model fallback schema drift a credential rebinding. Second-operation test zopakuje request aj deployment restart a musí zachovať jeden side effect, čitateľnú evidence chain a bezpečný terminal state.

## Kontrolné otázky

- Ktoré components a generations tvoria jeden composed n8n AI release?
- Ako obmedzujete generic nodes, network reach a task-runner blast radius?
- Čo sa stane pri model fallbacku, provider timeout a unknown outcome?
- Ktoré metrics dokazujú process health a ktoré business correctness?
- Ako kill switch, rollback a reconciliation fungujú pri in-flight approvals a side effects?

## Primárne zdroje

- [Block access to nodes](https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/block-specific-nodes/)
- [Hardening task runners](https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/harden-task-runners/)
- [SSRF protection](https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/enable-ssrf-protection/)
- [Security audit](https://docs.n8n.io/deploy/host-n8n/configure-n8n/security/run-security-audits/)
- [OpenTelemetry tracing](https://docs.n8n.io/deploy/host-n8n/keep-n8n-running/trace-executions-with-opentelemetry/)
