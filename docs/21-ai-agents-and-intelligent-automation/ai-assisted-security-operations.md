# AI-assisted security operations

AI-assisted security operations neskracujú bezpečnostný proces tým, že modelu odovzdajú autoritu rozhodnúť, čo je útok a čo sa má zablokovať. Skracujú čas potrebný na zhromaždenie dôkazov, koreláciu signálov, formulovanie hypotéz a prípravu kontrolovaného zásahu. Bez presnej identity alertu, incidentu, používateľa, zariadenia, workloadu a časového okna môže agent vytvoriť presvedčivú, ale nepravdivú bezpečnostnú históriu.

## 1. Business outcome

Cieľom je znížiť mean time to acknowledge, investigate a contain bez zvýšenia false-positive containmentov, straty dôkazov alebo neoprávnených zásahov. Security operations musí súčasne chrániť dostupnosť služby, integritu vyšetrovania, dôvernosť dát a schopnosť preukázať, kto alebo čo vykonalo každú akciu.

Agent je úspešný až vtedy, keď zrýchli konkrétnu fázu incident lifecycle a nezhorší ostatné invariants. Rýchle uzavretie alertu nie je business outcome.

## 2. Exact governed subject

Každé spustenie musí niesť stabilný subject envelope. Ten zahŕňa provider alert ID, incident ID, tenant, workspace, subscription alebo account, resource identity, principal identity, prvý a posledný pozorovaný čas, detekčné pravidlo a jeho generáciu, telemetry snapshot alebo query bounds a correlation ID.

Display name, hostname alebo e-mailová adresa nie sú dostatočnou identitou. Rovnaký názov môže patriť viacerým objektom a môže sa počas incidentu zmeniť.

## 3. Generácie vstupov

Výstup závisí od alert generation, detection-rule version, threat-intelligence snapshotu, asset inventory snapshotu, identity graph generation, modelu, system promptu, tool schemas a retrieval indexu. Bez týchto identifikátorov sa nedá rozlíšiť, či odlišný záver vznikol novými dôkazmi alebo zmenou systému.

Re-run nad novšou telemetriou je nová analýza, nie pokračovanie pôvodného dôkazu.

## 4. Authority boundary

Model smie navrhovať klasifikáciu, competing hypotheses, potrebné queries a containment plan. Deterministic policy rozhoduje, ktoré datasources smie čítať, ktoré tool calls sú povolené, či je potrebný reviewer a aká identity vykoná zmenu.

Prompt typu „nikdy neblokuj produkciu“ nie je enforcement. Enforcement musí byť mimo modelu v policy, tool wrapperi a provider IAM.

## 5. Read-only ako predvolený režim

Prvý pass má používať read-only tools: načítanie alertu, audit logov, identity risku, endpoint telemetry, network flow, deployment change a asset ownership. Read-only režim neznamená nulové riziko; query môže odhaliť citlivé údaje alebo byť drahá, ale nevyvolá containment side effect.

Write tools sa pripájajú až po vytvorení evidence package a explicitnom decision gate.

## 6. Security data plane

SOC agent typicky číta SIEM, XDR, IAM, CSPM, vulnerability scanner, CMDB, ticketing, threat intelligence a deployment telemetry. Každý connector má vlastný freshness model, retention, authorization a failure semantics.

Chýbajúci výsledok môže znamenať „nič sa nestalo“, „nemáme oprávnenie“, „dáta ešte nedorazili“, „query bola orezaná“ alebo „zdroj je nedostupný“. Agent musí tieto stavy rozlišovať.

## 7. Alert nie je incident

Alert je tvrdenie konkrétnej detekcie. Incident je analytický alebo procesný objekt, ktorý môže združovať viac alertov, assets a hypotheses. Agent nesmie automaticky preniesť severity jedného alertu na celý incident ani uzavrieť incident len preto, že jeden alert bol potlačený.

Correlation logic musí byť versioned a auditovateľná.

## 8. Evidence before narrative

Najprv sa vytvorí evidence inventory: exact queries, result counts, časové hranice, zdroje, missing partitions, identity mappings a change events. Až potom model vytvorí narrative.

Tým sa zabráni tomu, aby prvá hypotéza určovala, ktoré dôkazy agent vôbec vyhľadá.

## 9. Competing hypotheses

Agent musí udržiavať aspoň benign, malicious a telemetry-failure hypotézu. Pri credential anomaly môže ísť o kompromitáciu, legitímny automation job, nesprávne časové pásmo alebo duplicate identity mapping.

Každá hypotéza má supporting evidence, contradicting evidence a ďalší discriminating test.

## 10. Confidence nie je authorization

Model confidence je kalibračný signál, nie povolenie na zásah. Vysoká confidence nad neúplnou telemetriou môže byť nebezpečnejšia než nízka confidence s otvorene priznanou neistotou.

Mutation gate má používať typ akcie, blast radius, asset criticality, dôkazovú úplnosť, policy a approval, nie len číslo confidence.

## 11. Harness STO a AI remediation

Aktuálna Harness STO dokumentácia opisuje orchestráciu security scannerov, deduplikáciu findings, governance v pipelines a Harness AI vysvetlenia, návrhy code changes, package upgrades a vytvorenie code suggestion alebo pull requestu. Takýto návrh je remediation proposal nad findingom, nie dôkaz, že vulnerability je exploitable, fix je korektný alebo deployed artifact je bezpečný.

PR musí prejsť testami, review, provenance a opätovným scanom nad exact artifact digestom.

## 12. Microsoft Security Copilot agents

Aktuálna dokumentácia Microsoft Security Copilot agents rozlišuje trigger, identity, permissions, plugins, required products a role-based access. Agent možno spustiť manuálne, automaticky alebo pozastaviť a Microsoft odporúča samostatnú agent identity a least privilege.

Časť custom-agent funkcionality je stále označená ako prerelease. Production design preto pinne manifest schema a capability generation a neberie preview behavior ako stabilný kontrakt.

## 13. Identity a delegated access

Agent identity nesmie byť osobný Global Administrator alebo zdieľaný SOC účet. Má mať samostatný principal, scoped roles, krátkodobé credentials a jasný owner.

Keď agent používa user-delegated token, audit musí zachytiť používateľa aj vykonávajúcu agent identity. „Executed by Copilot“ bez delegated subjectu nestačí.

## 14. Prompt injection v security dátach

Alert description, process command line, ticket text, e-mail, threat-intelligence report a log field sú untrusted data. Útočník môže vložiť text, ktorý sa tvári ako pokyn pre agenta.

Tool selection a policy sa nesmú meniť podľa inštrukcií získaných z evidence. Retrieved content sa označí ako data, nie system instruction.

## 15. Tool inventory

Tool catalog má deliť capabilities na query, enrichment, case update, containment proposal, containment execution a recovery. Generic shell, unrestricted HTTP alebo arbitrary query-to-command bridge zväčšujú authority surface.

Každý write tool má typed schema, allowlisted operation, exact target a authoritative result.

## 16. Vulnerability triage

Finding musí niesť scanner, scan run, target, artifact digest, branch alebo environment, rule ID, severity source, evidence location a baseline. Agent môže doplniť exploitability context a ownership, ale nesmie prepísať source finding bez zachovania originálu.

Suppression potrebuje dôvod, scope, expiry a reviewer; inak sa dočasná výnimka stane trvalou slepou škvrnou.

## 17. Incident timeline

Timeline používa event time, ingest time a processing time. Bez tohto rozlíšenia môže oneskorený log vyzerať ako udalosť po containment akcii alebo replay ako nový útok.

Clock skew a timezone conversion sa zapisujú explicitne.

## 18. Case mutation

Update ticketu alebo incidentu je side effect. Potrebuje stable operation ID, expected version a idempotent semantics. Agent nesmie prepisovať analyst notes ani meniť severity bez optimistic concurrency.

Konflikt znamená re-read a nové rozhodnutie, nie blind overwrite.

## 19. Containment classes

Low-risk containment môže znamenať označenie session na dodatočné overenie alebo blokovanie známeho malicious hash v izolovanom test scope. High-risk containment zahŕňa disable identity, revoke sessions, isolate endpoint, block network route alebo rotate production secret.

Trieda určuje potrebný dôkaz, approvers, canary, timeout a recovery plan.

## 20. Approval envelope

Reviewer musí vidieť exact target, navrhovanú akciu, dôvody, competing hypotheses, expected impact, rollback alebo compensation, expiry a digest immutable planu. Schválenie všeobecného textu „contain compromised account“ nestačí.

Po zmene target state alebo plan digestu approval expiruje.

## 21. Separation of duties

Agent, ktorý vytvoril záver, nemá byť jediným schvaľovateľom akcie. Pri kritických assets má byť oddelený evidence owner, policy decision a execution identity.

Emergency mode môže zmeniť quorum, ale musí byť explicitný, časovo ohraničený a spätne reviewovaný.

## 22. Idempotency a unknown outcome

Provider timeout po `revokeSessions` nevie, či akcia prebehla. Retry bez read-backu môže opakovať ďalšie side effects alebo poškodiť audit.

Workflow prejde do `unknown_outcome`, načíta current state a až potom rozhodne o retry alebo reconciliation.

## 23. Containment read-back

HTTP 200 alebo tool success potvrdzuje prijatie requestu. Authoritative read-back musí overiť effective identity status, endpoint isolation, firewall policy generation alebo secret version.

Následne sa overí, či legitímne závislosti neboli odrezané.

## 24. Business impact

Security containment môže byť technicky správny a obchodne katastrofálny. Disable shared service principal môže zastaviť platby, onboarding alebo monitoring.

Preto incident state obsahuje security outcome aj service outcome a vlastníkov oboch.

## 25. Memory

Agent memory smie uchovávať schválené playbook preferences a neškodné investigation conventions. Nemá byť authoritative store incidentov, approvals, secrets ani long-lived reputácie používateľov.

Feedback „tento alert je vždy false positive“ musí byť scoped, reviewovaný a expirovateľný.

## 26. Data minimization

Model dostane len polia potrebné na konkrétnu úlohu. Full mailbox, entire identity directory alebo raw secrets nemajú byť default context.

Redaction sa vykoná pred modelom a audit zaznamená redaction policy generation.

## 27. Cost a denial of wallet

Útočník môže generovať množstvo alertov alebo extrémne dlhé evidence payloads. Rate limits, token budgets, duplicate detection a per-tenant quotas sú bezpečnostné kontroly.

Budget exhaustion nesmie viesť k silent auto-close.

## 28. Audit

Audit chain spája alert, incident, queries, tool results, model/prompt generation, proposals, policy decisions, approvals, execution, provider read-back a business verification. Citlivý chain môže používať hashed references a oddelené evidence storage.

Chat transcript sám osebe nie je kompletný audit.

## 29. Observability agentu

Merajú sa false-positive escalation, unsupported claims, missing-source rate, approval rejection, duplicate operation, unknown outcomes, containment rollback, business regressions a human correction. Samotná latency alebo počet uzavretých alertov vytvára zlú optimalizáciu.

Metrics sa segmentujú podľa action class a asset criticality.

## 30. Incident AGENT-OPS-15

Security agent spojí stale impossible-travel alert so servisným ticketom, ktorého text obsahuje neoverenú inštrukciu „disable the account immediately“. Identity graph mapuje alias na zdieľanú production service identity.

Agent vytvorí presvedčivý malicious narrative, hoci chýba endpoint telemetry a deployment calendar.

## 31. Failure propagation

Knowledge assistant v ďalšej kapitole vráti starý runbook bez aktuálnej výnimky pre shared identities. Ticket workflow odošle containment summary širokej distribučnej skupine a remediation agent vykoná disable.

Alert sa následne prestane generovať, pretože service identity už nepracuje. No-data je omylom označené ako recovery.

## 32. Containment

Incident sa prepne do read-only evidence collection. Write tools, auto-close a auto-disable sa vypnú; zablokujú sa memory writes a zachová sa exact telemetry snapshot.

Service owner a incident commander dostanú oddelené security a availability evidence.

## 33. Recovery

Identity sa obnoví len cez schválený recovery plan, rotáciu credentials, dependency validation a provider read-back. Ticket recipients dostanú correction notice a citlivý obsah sa odstráni, ak to platforma umožňuje.

Následne sa vykoná reconciliation všetkých zmeškaných business operácií.

## 34. Positive acceptance

Agent zhromaždí úplný evidence package, označí missing telemetry, predloží competing hypotheses a nepripojí high-risk mutation tool bez platného approval envelope. Containment vykoná least-privilege identity nad exact targetom a read-back potvrdí efekt.

Service SLO a business reconciliation ostanú zelené.

## 35. Forbidden acceptance

Alert closure, model confidence, tool HTTP success alebo zmiznutie signálu nesmú byť acceptance. Agent nesmie používať ticket text ako instruction, osobný admin účet ako execution identity ani memory ako suppression database.

High-risk akcia nesmie prejsť len preto, že incident severity je Critical.

## 36. Recovery acceptance

Po nesprávnom containment sa obnoví exact identity generation, overia sa dependencies, zreconciliujú zmeškané operácie a audit spojí pôvodný aj opravný zásah. Druhý test použije rovnaký display name pre dve identities a musí zablokovať nejednoznačný target.

## 37. Practical investigation contract

Investigation contract oddeľuje dôkazové queries od containment authority. Každý run uvádza, ktoré sources boli dostupné, ktoré chýbali a aká policy generation rozhodla o povolenej ďalšej akcii.

```yaml
security_investigation:
  subject:
    tenant: tenant-a
    incident_id: INC-2026-0815
    alert_ids: [ALERT-4412]
    resource_uid: entra://servicePrincipals/7f3a
  evidence:
    window: 2026-08-05T13:00:00Z/2026-08-05T14:00:00Z
    required_sources: [identity-audit, endpoint, deployment-calendar]
    missing_source_behavior: hold
  agent:
    mode: read-only
    model_generation: soc-model-2026-07
    prompt_digest: sha256:example
  mutation_gate:
    policy_bundle: soc-containment-v12
    target_must_be_unique: true
    approval_required_for: [disable-identity, isolate-endpoint]
  acceptance:
    require_provider_readback: true
    require_service_owner_check: true
```

Manifest je configuration intent, nie runtime evidence. Acceptance test musí simulovať missing endpoint telemetry, duplicate display name, provider timeout a service-owner rejection a preukázať, že systém ostane v hold alebo reconciliation stave.

## 38. Primary sources

Harness STO overview a feature inventory sú v aktuálnej Harness Developer Hub dokumentácii; Harness AI remediation page z júla 2026 opisuje vysvetlenia findings, code suggestions a pull requests. Microsoft Learn dokumentácia Security Copilot agents z marca až júna 2026 opisuje agent identity, permissions, triggers, plugins, run/pause controls a prerelease status custom-agent častí.

Google Cloud Architecture Center dokumentuje agentické security-operations workflowy a NIST AI RMF Generative AI Profile poskytuje širší risk-management rámec. Tieto zdroje opisujú capabilities a governance inputs; nepreukazujú bezpečnosť konkrétneho production workflowu.

## Zhrnutie

AI v SOC má byť evidence accelerator a bounded proposal system. Exact subject, immutable evidence, least privilege, competing hypotheses, approval, idempotent execution, provider read-back a business verification sú authority vrstvy, ktoré model nenahrádza.

Ďalšia kapitola rieši knowledge assistants a enterprise search, z ktorých security agent čerpá runbooky a organizačný kontext.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: AI-assisted observability a incident response](ai-assisted-observability-incident-response.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Knowledge assistants a enterprise search →](knowledge-assistants-enterprise-search.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
