# Least privilege pre tools a credentials

Least privilege v agentickom systéme znamená, že model nevidí, nenavrhuje ani nevykonáva viac capabilities, než potrebuje pre aktuálnu business operation. Nejde iba o menší OAuth scope. Hranica zahŕňa tool discovery, argumenty, resource set, environment, credential lifetime, network reachability, writable data, side-effect class, approval obligations a počet povolených attempts.

Táto kapitola pokračuje v incidente `AGENT-SEC-04`. Agent mal v jednom catalogu metrics read, Kubernetes mutation, secret retrieval, email a arbitrary HTTP tools. Všetky používali rovnaký production service account a credential bol platný osem hodín. Keď retrieved issue zmenilo plán, model nemusel eskalovať privilege: požadovaná cesta už bola dostupná. Root cause preto nebol iba prompt injection, ale standing authority a capability union, ktoré umožnili nedôveryhodnému textu zmeniť inference na reálny side effect.

Nosný lifecycle je:

```text
exact task a risk classification
→ minimálny capability set
→ tool exposure filter a contract generation
→ canonical resource a environment bounds
→ policy evaluation a approval obligations
→ just-in-time credential request
→ narrow audience, scope a TTL
→ one call alebo bounded lease
→ immediate revocation alebo expiry
→ side-effect, descendant a business read-back
→ entitlement cleanup a second-operation isolation
```

## 1. Capability nie je iba function name

Tool `restart_service` môže skrývať veľmi odlišné authority podľa toho, či prijíma ľubovoľný cluster, namespace a service alebo iba pre-approved resource UID. Preto sa privilege meria kombináciou verbu, resource selectorov, argument constraints, environmentu a execution identity.

Dva tools s rovnakým názvom nemusia byť security-equivalent. Versioned contract musí presne určiť, čo tool dokáže, aké side effects vytvára a ktoré downstream credentials používa.

## 2. Tool exposure je prvý authorization layer

Najbezpečnejší zakázaný tool call je ten, ktorý model vôbec nemôže navrhnúť. Runtime preto filtruje catalog podľa authenticated subjectu, agent release, task type, environmentu, tenant scope, approval state a current phase workflowu.

Dynamic filtering nie je finálna authorization. Catalog môže byť stale alebo model môže použiť legitímny tool s nebezpečnými arguments, preto každý execution prejde samostatnou policy kontrolou.

## 3. Capability manifest

Agent release má deklarovaný maximálny capability envelope a každý run z neho odvodí menší active set. Manifest je reviewed artifact, nie text generovaný modelom.

```yaml
capability_manifest:
  agent_release: checkout-remediator/13.4.2
  maximum_tools:
    - name: metrics.query
      mode: read
    - name: kubernetes.get
      mode: read
    - name: deployment.restart.propose
      mode: propose
    - name: deployment.restart.execute
      mode: write
      requires:
        - human_approval
        - exact_resource_uid
        - active_incident_assignment
  forbidden_tools:
    - secret.read_raw
    - arbitrary_http.post
    - shell.host
```

Loaded tool catalog digest sa zapisuje do run state a approval envelope. Silent pridanie nového toolu počas resume je release change, nie bežné pokračovanie.

## 4. Read, propose a execute

Read-only evidence collection, návrh mutácie a samotná execution sú rozdielne capabilities. Agent môže analyzovať metrics a vytvoriť structured proposal bez toho, aby vlastnil credential schopný zmenu vykonať.

Oddelenie `propose` od `execute` znižuje blast radius prompt injectionu a model erroru. Executor môže byť deterministická služba s úzkym contractom, ktorá prijíma iba approved digest a stable operation identity.

## 5. Capability ladder

Tooling sa navrhuje ako ladder od najnižšieho privilege po najvyššie. Run začína read-only a získava ďalšiu capability iba po splnení explicitného gate-u.

```text
observe
→ query bounded evidence
→ propose action
→ simulate alebo dry-run
→ request approval
→ acquire JIT credential
→ execute exact action once
→ revoke credential
→ verify outcome
```

Model nesmie preskočiť z neúplného observation priamo na mutation tool len preto, že tool je v catalogu. Runtime phase machine vynucuje povolené transitions.

## 6. Resource scoping

Scope `kubernetes:write` je pre agentický workload zvyčajne príliš široký. Policy má viazať action na cluster, namespace, kind, name, UID, generation a povolený field alebo verb.

Resource name samotný nestačí, pretože objekt môže byť zmazaný a znovu vytvorený s rovnakým menom. UID alebo equivalent immutable identity bráni použitiu starého approvalu či credentialu na novú resource generation.

## 7. Argument constraints

Schema validation kontroluje typ a formát, ale least privilege potrebuje semantic bounds. Restart count, replica delta, refund amount, recipient domain, SQL statement class alebo allowed path musia mať policy-defined limity.

```json
{
  "tool": "deployment.restart.execute",
  "constraints": {
    "cluster": ["prod-eu-1"],
    "namespace": ["checkout"],
    "resource_uid": ["9c83..."],
    "max_attempts": 1,
    "allowed_strategy": ["rolling"],
    "forbid_force": true
  }
}
```

Model nemá možnosť pridať `force=true`, zmeniť namespace alebo rozšíriť selector wildcardom.

## 8. Environment isolation

Staging a production nemajú zdieľať rovnaký credential, role ani tool endpoint bez ďalšej policy. Environment sa odvodzuje z trusted resource resolution a workload deployment, nie z textového argumentu.

Production capability sa môže objaviť až po environment-specific gate-e. Agent testujúci v stagingu nesmie získať production role iba zmenou stringu `environment` v tool calle.

## 9. Credential broker

Agent nemá čítať master secret ani dlhodobý cloud key. Credential broker autentifikuje workload, prijme typed capability request, vyhodnotí policy a vydá krátkodobý credential pre presnú audience, resource a action.

```text
agent workload identity
→ broker authentication
→ operation and approval validation
→ narrow role or dynamic secret issuance
→ execution
→ lease revocation and audit
```

Broker je security-critical component a nesmie dôverovať modelovému explanation. Používa canonical runtime context a signed approval artifacts.

## 10. Dynamic secrets

Vault database secrets engine a podobné systems generujú unique credentials podľa role a lease. Každý workload alebo session tak môže dostať samostatný účet s minimálnymi permissions a automatickou revocation po expiry.

Dynamic secret nie je automaticky least privilege. Ak role vytvára database owner credentials alebo TTL trvá hodiny, systém iba dynamicky vydáva nadmerné oprávnenie.

## 11. Just-in-time access

Zero standing privilege znamená, že high-impact credential neexistuje alebo nie je dostupný agentovi, kým current operation nesplní podmienky. Credential sa vytvorí tesne pred execution a zanikne po jednej action alebo krátkom lease.

JIT flow znižuje interval, počas ktorého prompt injection alebo compromised process môže credential zneužiť. Zároveň poskytuje prirodzený policy checkpoint po approvale a pred side effectom.

## 12. Short TTL a one-shot credential

TTL sa volí podľa očakávanej execution latency a možnosti revocation. Pre jednu API mutáciu môže byť vhodný token platný desiatky sekúnd; pre long-running job môže byť lepší bounded lease s heartbeatom a renewal policy.

One-shot capability sa po úspešnom použití označí consumed. Retry nepoužije nový širší credential, ale rovnakú operation identity a downstream idempotency contract.

## 13. Credential scope reduction

Broker odvodzuje result permissions ako prienik maximálneho agent entitlementu, human delegation, current tasku, approvalu a resource policy. Žiadna vrstva nesmie privilege rozšíriť.

```text
issued_permissions =
  agent_maximum
  ∩ human_delegation
  ∩ task_required
  ∩ approval_scope
  ∩ resource_policy
  ∩ environment_policy
```

Ak je prienik prázdny, request sa odmietne. Systém nemá fallback na shared admin credential.

## 14. Audience a endpoint pinning

Credential sa vydáva pre konkrétny resource server a tool endpoint. Arbitrary URL parameter nesmie presmerovať token na attacker-controlled host.

Endpoint resolution používa approved service registry, TLS identity a audience mapping. Redirecty, DNS changes a proxy routes sa posudzujú ako trust-boundary transition, nie ako transparentná sieťová vlastnosť.

## 15. Sender constraint

DPoP, mTLS alebo workload-bound credentials obmedzujú použitie tokenu na process, ktorý vlastní príslušný key. Ukradnutý bearer token je inak použiteľný mimo sandboxu alebo v inom agente.

Key material sa drží v memory, workload identity agentovi alebo hardware-backed store a nevkladá sa do LLM contextu. Tool function dostáva opaque credential handle, nie secret string.

## 16. Opaque handles

Model nepotrebuje vidieť API key, password ani access token. Runtime môže priradiť toolu opaque handle, ktorý executor vymení za credential mimo model contextu.

```yaml
credential_binding:
  handle: credh-8841
  broker_role: k8s-checkout-restart
  audience: https://kubernetes.prod-eu-1.example
  resource_uid: 9c83...
  expires_at: 2026-08-04T16:31:20Z
  visible_to_model: false
```

Tool output nesmie credential vypísať ani pri chybe. Redaction sa aplikuje pred trace, model contextom a user-visible response.

## 17. Secret zero

Každý broker potrebuje bootstrap identity. Preferovaný model používa workload attestation alebo platform identity namiesto static bootstrap secretu uloženého v image či filesysteme.

Ak secret zero existuje, musí mať minimálnu capability iba na získanie krátkodobej identity, byť rotovaný a chránený mimo agent workspace. Kompromitácia bootstrapu nesmie priamo poskytovať production mutation authority.

## 18. Credential delivery

Credential sa doručuje najkratšou možnou cestou executorovi a neprechádza cez chat history, plan artifact, retriever ani general shared state. Environment variables môžu unikať do child procesov a crash dumps; files môžu zostať vo workspace po run-e.

Bezpečnejšie sú process-local handles, Unix socket agent, workload API alebo in-memory injection tesne pred requestom. Cleanup po execution musí byť overiteľný, nie iba best effort.

## 19. Tool-specific identity

Rôzne tools môžu používať rôzne downstream identities. Metrics reader nepotrebuje rovnakú role ako deployment executor a email sender nemá používať cloud infrastructure principal.

Oddelenie identity per capability zabraňuje confused deputy efektu, pri ktorom legitímny tool prenesie broad credential na iný účel. Audit tiež presne ukáže, ktorý executor a role vytvorili side effect.

## 20. Credential inheritance

Child agents a subprocesses nededia parent credentials automaticky. Delegation contract určí, ktoré opaque handles alebo capabilities sa smú preniesť a na aký time/resource scope.

Shell alebo code sandbox nemá dostať cloud token iba preto, že parent agent môže volať cloud tool. Privileged tool má zostať mimo sandboxu za narrow RPC boundary.

## 21. Tool namespaces

Veľký catalog sa delí na namespaces podľa domainu, risku a ownera. Qualification ako `metrics.read.query` alebo `kubernetes.write.restart` znižuje ambiguity a umožňuje policy nad celou classou.

Namespace nie je security control sám osebe. Runtime musí zabrániť aliasom, duplicate names a dynamic serverom, ktoré predstierajú trusted namespace.

## 22. MCP tool filtering

MCP host môže filtrovať tools podľa active agentu, run contextu a server identity. Filter má používať trusted metadata a policy, nie iba prefix name alebo server-supplied annotation.

Server descriptions, `readOnlyHint` a destructive annotations sú claims. Host ich používa pre UX a risk scoring, ale actual authorization a credential binding ostávajú local enforcement.

## 23. Approval-bound credential

High-impact credential sa vydá až po validnom approval decisione viazanom na action digest. Broker porovná approval subject, resource, arguments, tool contract, policy generation a TTL.

Zmena ktoréhokoľvek execution-relevant fieldu invaliduje binding. Approval „reštartovať checkout“ nemôže autorizovať credential pre ľubovoľný deployment alebo force delete.

## 24. Credential renewal

Long-running tasks môžu potrebovať renewal, no renewal je nové authorization rozhodnutie. Broker overí current workload identity, operation state, cancellation, policy a remaining budget.

Model nemá priamo volať renewal endpoint. Durable executor obnovuje lease iba počas povoleného state a po zastavení tasku credential aktívne revokuje.

## 25. Revocation a cleanup

Credential môže skončiť expiry, explicitnou revocation, consumed state, operation cancellation alebo policy change. Cleanup graph zahŕňa child tokens, database users, SSH certificates, temporary files, sessions a cached handles.

Úspešná business action neznamená úspešný cleanup. Acceptance musí potvrdiť, že credential už nie je použiteľný a descendant sessions boli ukončené.

## 26. Retry ownership

Iba jedna vrstva vlastní retry mutation requestu. Ak agent loop, SDK, gateway, broker a downstream client retryujú nezávisle, krátkodobý credential môže byť použitý viackrát a attempts prekročia risk budget.

Retry používa rovnakú operation identity, idempotency key a capability bounds. Expired credential sa obnoví iba po unknown-outcome reconciliation, nie automaticky pred zistením, či prvý side effect commitol.

## 27. Break-glass

Emergency access je samostatný, explicitný a časovo obmedzený path s human accountability. Agent nemá automaticky aktivovať break-glass na základe vlastného urgency score alebo modelovej klasifikácie incidentu.

Break-glass credential má narrower resource set, silnejší audit, povinný post-review a okamžitú revocation po použití. Nemá sa ukladať ako fallback secret v tool configuration.

## 28. Cost a financial privilege

Privilege zahŕňa aj schopnosť vytvárať náklady. GPU jobs, cloud resources, paid APIs, messages a data egress potrebujú budgets a quantity limits rovnako ako security-sensitive writes.

Tool policy môže obmedziť maximum cost per call, operation a tenant. Model nesmie obísť limit rozdelením jednej veľkej action na stovky menších volaní.

## 29. Data privilege

Read-only tool môže mať vysoký risk, ak sprístupňuje secrets, PII alebo celý production dataset. Least privilege preto zahŕňa field-level projection, row/tenant filters, time window a aggregation.

Metrics tool môže vracať aggregate health bez raw customer identifiers. Retriever môže poskytovať redacted snippets namiesto celých dokumentov a secret store nemusí byť agent toolom vôbec.

## 30. Network privilege

Outbound network je capability. Sandbox alebo tool executor má explicitný allowlist destinations, protocols, DNS behavior a egress volume; default internet access vytvára exfiltration path.

HTTP fetch a HTTP post sa majú oddeľovať. Agent, ktorý potrebuje čítať vendor documentation, nemusí mať možnosť odoslať data na ľubovoľný origin.

## 31. Filesystem privilege

Workspace mounts sa delia na read-only inputs, writable scratch, explicit output a forbidden host paths. Home directory, SSH agent, cloud config, Docker socket a repository credentials sa nepripájajú defaultne.

Writable root filesystem nie je potrebný pre väčšinu generated-code tasks. Ephemeral scratch sa po run-e zničí a outputs prejdú validation pred exportom.

## 32. Observability bez secret leakage

Trace zachytáva credential handle, broker role, audience, scope, issued/expiry time, policy decision a consumption status, nie plaintext secret. Redaction musí fungovať aj pre tool errors, subprocess stderr a network captures.

Hash secretu nie je vždy bezpečný, ak má nízku entropiu alebo umožňuje correlation naprieč tenants. Lepšie je logovať broker-issued identifier a audit reference.

## 33. Incident `AGENT-SEC-04`

Agent dostal union capabilities pre diagnostics aj remediation. Shared credential mal read/write access ku Kubernetes, secret store a object storage a bol injectnutý do environmentu code sandboxu. Retrieved issue obsahovalo inštrukciu, aby agent „overil backup“ načítaním cloud key a odoslaním manifestu cez HTTP.

Model vybral existujúce tools a všetky authorization checks formálne prešli, pretože policy overovala iba service account role. Sandbox neunikol; zneužil presne tie resources, ktoré mu platforma poskytla.

Správna architektúra mala byť:

```text
read-only diagnostic catalog
→ untrusted retrieved content labels
→ bounded proposal without credentials
→ deterministic policy and human approval
→ one exact executor capability
→ JIT one-shot credential outside model and sandbox
→ destination-pinned request
→ credential revocation
→ side-effect and no-exfiltration read-back
```

Containment odstránil shared credential, vypol arbitrary HTTP post a secret tool a zastavil sandboxes s production mounts. Recovery zaviedla broker, per-tool roles, opaque handles a egress allowlist.

## 34. Failure hypotheses

Least-privilege incident sa analyzuje ako capability a credential chain, nie iba ako „agent mal priveľa práv“. Najprv sa porovná maximum manifest, active catalog a exact tool call, aby sa zistilo, či nebezpečná capability bola exposed omylom, získaná eskaláciou alebo zneužitá legitímnymi arguments.

Potom sa sleduje credential od broker requestu cez issuance, delivery, use, renewal a cleanup. Signed token môže mať wrong audience, príliš širokú role alebo príliš dlhý TTL; opaque handle môže byť správny, ale executor môže ignorovať resource constraints. Nakoniec sa overí descendant graph: primary write, events, network egress a remaining sessions.

- **Capability union** — jeden agent release kombinoval read, secret, mutation a exfiltration paths, ktoré nemali byť dostupné v rovnakom run-e.
- **Catalog filter bypass** — stale cache, alias alebo dynamic server znovu vystavili zakázaný tool.
- **Overbroad resource scope** — role povoľovala wildcard cluster, namespace, path alebo account namiesto exact subjectu.
- **Standing credential** — long-lived token existoval pred approvalom a zostal použiteľný po operácii.
- **Broker privilege expansion** — issued role bola širšia než prienik tasku, human delegation a agent maximum.
- **Credential leakage** — secret sa dostal do model contextu, environmentu, trace, erroru alebo output artifactu.
- **Inheritance leak** — child agent alebo sandbox zdedil parent credential bez explicitnej delegation.
- **Unbounded renewal** — task obnovoval lease po cancellation alebo mimo approved time window.
- **Egress gap** — execution bola resource-bounded, ale network tool umožnil odoslať získané data mimo trust domainu.
- **Cleanup gap** — primary token expiroval, no child session, database user alebo cached handle zostal aktívny.

Každá hypotéza sa testuje proti capability manifestu, loaded catalog digestu, policy inputu, broker a lease logom, process environment inventory, network flow a downstream auditom. Modelový transcript nepovie, ktoré credentials boli reálne dostupné procesu.

## 35. Containment

Pri privilege incidente sa skryjú affected mutation, secret a egress tools a broker prestane vydávať príslušné roles. Existujúce leases a child sessions sa revokujú podľa operation, agent release a workload identity.

Sandboxes sa presunú do no-network read-only režimu a pending operations do reconciliation. Evidence sa zachová bez plaintext secretov; hromadné mazanie auditov alebo workspace images by znemožnilo určiť exposure.

## 36. Recovery

Recovery rozdelí capability union, opraví manifest a catalog filtering, zúži role, audience, resources a TTL a presunie credentials mimo model/sandbox contextu. Broker dostane atomic issuance a revocation evidence.

Affected downstream systems sa skontrolujú na unexpected writes, sessions a data egress. Rotácia secretu sama nestačí, ak pretrváva overbroad policy alebo agent stále môže získať nový equivalent credential.

## 37. Positive acceptance

Pozitívny test začne bez production credentialu, vykoná read-only evidence collection, vytvorí proposal a po approvale získa one-shot credential pre exact resource. Executor vykoná jednu idempotent action a broker potvrdí consumed alebo revoked state.

Agent ani sandbox nesmú credential vidieť. Audit spája operation, approval, broker issuance, downstream request a business outcome.

## 38. Forbidden acceptance

Zakázaný test požiada o wildcard resource, širší scope, arbitrary endpoint, druhé použitie one-shot handle, renewal po cancellation alebo secret output do model contextu. Každá cesta musí fail-closed skončiť pred side effectom alebo exfiltration.

Ďalší test pridá nový MCP tool s trusted-looking názvom. Catalog policy ho nesmie vystaviť bez reviewed server identity a capability manifest update.

## 39. Recovery acceptance

Recovery test zabije executor po credential issuance, rotuje broker key, zmení policy a obnoví run na inom workerovi. Systém musí zistiť status pôvodnej action, revokovať stale lease a vydať nový credential iba po current authorization.

Cleanup test overí, že child sessions, database users, temporary files a egress routes už nie sú aktívne. Absencia ďalšieho API callu nie je dostatočný cleanup dôkaz.

## 40. Second-operation acceptance

Nová operation začína s minimálnym read-only catalogom a bez zdedených handles, leases alebo policy allow. Aj rovnaký používateľ a resource potrebujú nový operation context a podľa risku nový approval.

Tým sa overí, že JIT privilege je viazané na jednu operáciu a nestáva sa standing authority pre budúce agent runs.

## 41. Zhrnutie

Least privilege pre agentické tools je kombinácia minimálneho catalogu, narrow contracts, exact resources, argument bounds, environment isolation, JIT credentials, sender constraint, one-shot use, egress policy a úplného cleanupu. Menší OAuth scope bez kontroly tool exposure a descendants nestačí.

Najbezpečnejší agent nevlastní permanentnú production authority. Dokáže zbierať bounded evidence, navrhnúť action a po explicitných gates získať krátkodobú capability pre jeden presný side effect, ktorého technický, business aj cleanup outcome sa dá authoritative overiť.