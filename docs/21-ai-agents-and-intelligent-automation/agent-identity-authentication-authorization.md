# Agent identity, authentication a authorization

Agent identity nie je meno modelu ani display label v orchestration UI. Produkčný agentický systém potrebuje presne rozlíšiť človeka alebo business principal, agent definition, workload process, konkrétny run, tool caller a downstream actor, pretože každá z týchto identít má inú authority, lifecycle a auditný význam.

Táto kapitola otvára incident `AGENT-SEC-04`. Remediation agent spracoval production alert pod zdieľaným service accountom `ops-automation`. Audit log preto nevedel rozlíšiť, či zmenu navrhol konkrétny používateľ, supervisor agent, code-execution worker alebo retry po obnovení runu. Agent navyše vymenil používateľský token za downstream token bez zachovania actor chainu a cloud API videlo iba široko oprávnenú machine identity. Authentication prešla, no authorization a accountability zlyhali.

Nosný lifecycle je:

```text
business request a human subject
→ agent definition a release generation
→ workload attestation a runtime identity
→ exact run, task a tool-call identity
→ delegation alebo impersonation semantics
→ audience/resource/scope reduction
→ policy evaluation nad subjectom, actorom a contextom
→ sender-constrained short-lived credential
→ downstream authorization a side effect
→ technical, business a audit read-back
→ revocation, expiry a second-operation isolation
```

## 1. Identity je tvrdenie o subjekte

Identity odpovedá na otázku „kto alebo čo je tento actor?“ a musí mať canonical identifier v konkrétnom trust domain-e. Display name `Checkout Agent` nie je canonical identity, pretože môže označovať viac deploymentov, tenantov alebo runtime instances.

Identita sama neurčuje oprávnenia. Overený workload môže byť autentifikovaný ako `spiffe://prod.example/agents/remediation`, ale stále nemusí mať authorization na restart production deploymentu alebo čítanie customer data.

## 2. Päť identít v jednom tool calle

Jeden tool call môže súčasne niesť viac identity vrstiev. Human subject iniciuje požiadavku, agent definition určuje schválené správanie, workload identity autentifikuje proces, run identity viaže operáciu na durable state a downstream actor claim vysvetľuje, kto koná v mene koho.

Ak sa tieto vrstvy zlejú do jedného service accountu, incident response nevie určiť pôvod autority. Least privilege sa tiež nedá presne aplikovať, pretože policy nepozná rozdiel medzi interaktívnym používateľom, scheduled automation a recovery workerom.

## 3. Canonical identity manifest

Agent release potrebuje identity manifest, ktorý je versioned spolu s tool catalogom a policy bindingom. Manifest neobsahuje iba meno, ale exact workload selector, trust domain, ownera, allowed environments a delegation modes.

```yaml
agent_identity:
  agent_id: agent://retail-eu/checkout-remediator
  release: checkout-remediator/13.4.2
  owner: sre-checkout
  workload_spiffe_id: spiffe://prod.example/agents/checkout-remediator
  allowed_environments:
    - staging
    - production
  delegation_modes:
    - on_behalf_of
  forbidden_modes:
    - unrestricted_impersonation
  policy_bundle: agent-authz/22
  tool_catalog_digest: sha256:8a1f...
```

Policy engine porovnáva loaded release a runtime identity s manifestom. Samotný signed image digest ešte nedokazuje, že workload dostal správnu identity alebo že request patrí povolenému tenantovi.

## 4. Workload identity

Workload identity označuje bežiaci compute endpoint, nie používateľa. SPIFFE štandardizuje SPIFFE ID, SVID a Workload API, cez ktoré workload získava krátkodobý kryptograficky overiteľný identity document bez hardcoded application secretu.

Workload API typicky identifikuje lokálneho caller-a out-of-band mechanizmom, napríklad vlastnosťami procesu a Unix socketu. To znamená, že bezpečnosť nezačína až pri certifikáte; začína pri node attestation, workload selectoroch, socket permissions a správnom priradení identity k procesu.

## 5. SVID a trust domain

SVID umožňuje workloadu prezentovať SPIFFE ID pomocou X.509, JWT alebo podporovaného workload identity tokenu. Verifier kontroluje podpis, trust bundle, časovú platnosť, audience a interpretáciu identity v danom trust domain-e.

Validný SVID nie je univerzálny pass. Federation medzi trust domains musí explicitne definovať, ktoré identity a paths sa akceptujú a na aké resources majú vplyv.

## 6. Runtime instance a run identity

Viac replicas rovnakého agent release-u môže zdieľať workload identity, ale nesmie zdieľať run identity. Každý business operation, agent run, nested task a tool call potrebuje stable identifiers a parent-child lineage.

```yaml
identity_chain:
  operation_id: checkout-incident-2049
  run_id: run-2049-03
  agent_id: agent://retail-eu/checkout-remediator
  agent_release: checkout-remediator/13.4.2
  workload_id: spiffe://prod.example/agents/checkout-remediator
  workload_instance: pod/checkout-remediator-7f8d9
  tool_call_id: tc-77
  attempt_id: tc-77-attempt-2
```

Attempt ID sa mení pri retry, ale tool-call a operation identity zostávajú stabilné. Inak downstream audit nevie rozlíšiť nový business action od opakovania rovnakej operácie.

## 7. Authentication

Authentication overuje, že caller kontroluje credential priradený deklarovanej identity. Môže používať mTLS, signed JWT, workload identity federation, OAuth client authentication alebo sender-constrained access token.

Authentication výsledok musí obsahovať issuer, subject, audience, authentication method, key binding, issued/expiry time a trust-chain generation. Boolean `authenticated=true` je príliš slabý artifact na neskoršiu policy a incident analýzu.

## 8. Authorization

Authorization rozhoduje, či autentifikovaný subject alebo actor smie vykonať presnú action nad presným resource v aktuálnom contexte. Rozhodnutie zahŕňa tenant, environment, resource generation, risk, user delegation, tool contract, time, network zone a approval state.

Policy sa vyhodnocuje pri každom citlivom tool calle a znovu bezprostredne pred execution. Cached allow z predchádzajúceho turnu nemá automaticky platiť po handoffe, resume, token exchange alebo zmene resource generation.

## 9. Authentication nie je authorization

Agent môže úspešne autentifikovať svoj workload certificate a následne požadovať zakázanú action. Rovnako môže mať validný access token, ktorý je určený pre inú audience alebo obsahuje širší scope, než dovoľuje current business task.

Bezpečný runtime preto neodvodzuje `allow` iba z prítomnosti credentialu. Najprv overí token a sender, potom canonicalizuje resource a arguments a až následne vyhodnotí policy.

## 10. Human subject a workload actor

Pri on-behalf-of operácii je human alebo business principal subjectom a agent workload actorom. Audit aj downstream policy potrebujú zachovať obe identity, pretože „kto nesie business authority“ a „ktorý proces vykonal request“ nie sú rovnaké otázky.

```json
{
  "sub": "user:martin-vyhonsky",
  "act": {
    "sub": "spiffe://prod.example/agents/checkout-remediator"
  },
  "aud": "https://change-api.example.com",
  "scope": "change:propose",
  "tenant": "retail-eu",
  "operation_id": "checkout-incident-2049"
}
```

Actor chain nesmie byť iba log metadata pridaná po requeste. Musí byť integrity-protected a policy engine ju musí reálne používať.

## 11. Delegation verzus impersonation

Delegation znamená, že actor koná v mene subjectu a obe identity zostávajú rozlíšiteľné. Impersonation prezentuje actor-a ako subject alebo vytvára token, v ktorom downstream nemusí vidieť pôvodného vykonávateľa.

RFC 8693 podporuje token exchange vrátane delegation a impersonation semantics. Produkčný agentický systém má preferovať delegation s explicitným actor chainom; impersonation povoľuje iba tam, kde je nevyhnutná, úzko scoped a plne auditovaná.

## 12. OAuth token exchange

Token exchange môže vymeniť inbound subject token za downstream token s užšou audience, resource a scope. Exchange endpoint však nesmie kopírovať všetky upstream privileges do každého backendu.

```http
POST /oauth2/token
Content-Type: application/x-www-form-urlencoded

grant_type=urn:ietf:params:oauth:grant-type:token-exchange&
subject_token=eyJ...&
subject_token_type=urn:ietf:params:oauth:token-type:access_token&
requested_token_type=urn:ietf:params:oauth:token-type:access_token&
resource=https%3A%2F%2Fchange-api.example.com&
scope=change%3Apropose&
actor_token=eyJ...
```

Authorization server musí overiť, či actor smie konať za subject, či requested resource a scope zodpovedajú current operation a či výsledný token zachová required identity claims.

## 13. Audience, resource a scope

Audience určuje intended recipient tokenu, resource vyjadruje cieľovú službu alebo protected resource a scope obmedzuje povolené operácie. V praxi sa implementácie líšia, preto contract musí presne určiť, ktoré pole je authoritative a ako sa mapuje na downstream policy.

Token pre metrics API sa nesmie akceptovať v deployment API. Scope `ops:write` je pre agentické tools príliš široký; vhodnejší je resource-specific capability ako `deployment:restart:propose` s ďalšou policy nad exact namespace a deployment UID.

## 14. Sender-constrained credentials

Bearer token môže použiť každý, kto ho získa. DPoP alebo mTLS sender-constrained token viaže credential na key pair, takže resource server požaduje dôkaz držby privátneho kľúča pri každom requeste.

Sender constraint znižuje riziko replayu uniknutého tokenu, ale nerieši kompromitovaný agent process, ktorý legitímny key používa. Preto sa kombinuje s short TTL, resource/scope reduction, sandboxom a per-action authorization.

## 15. Short-lived identity

Agent runtime nemá používať long-lived access keys vložené v image, environment variable alebo workspace. Workload attestation a federation majú vydávať krátkodobé credentials, ktoré sa automaticky obnovujú iba počas validného workload lifecycle.

Short TTL znižuje exposure window, no komplikuje durable pause/resume. Po obnovení runu sa starý credential nepoužíva; runtime znovu autentifikuje workload, obnoví delegation a revaliduje authorization nad current state.

## 16. Credential a decision lifetime

Credential expiry a authorization-decision TTL sú odlišné. Token môže byť platný desať minút, ale allow decision viazaný na resource generation môže byť stale po desiatich sekundách.

Execution preto kontroluje oba lifecycles. Validný token s neplatným approval digestom alebo zmeneným deployment UID nesmie autorizovať starú action.

## 17. Policy input

Policy input musí byť typed a zostavený z trusted runtime contextu, nie z modelového prose summary. Model môže navrhnúť action, ale nesmie určovať vlastný subject, tenant, role alebo approval state.

```json
{
  "subject": "user:martin-vyhonsky",
  "actor": "spiffe://prod.example/agents/checkout-remediator",
  "agent_release": "checkout-remediator/13.4.2",
  "operation_id": "checkout-incident-2049",
  "action": "deployment.restart.propose",
  "resource": {
    "cluster": "prod-eu-1",
    "namespace": "checkout",
    "kind": "Deployment",
    "name": "checkout-api",
    "uid": "9c83...",
    "generation": 84
  },
  "tool_contract": "kubernetes-remediation/v6",
  "approval_digest": "sha256:...",
  "risk": "high"
}
```

Policy decision vracia allow/deny, obligations, expiry a decision ID. Obligations môžu vyžadovať step-up authentication, second approver, read-only mode alebo narrower credential.

## 18. RBAC, ABAC a relationship policy

RBAC priraďuje permissions rolám a je vhodný pre stabilné job functions. Agentické operations však často potrebujú ABAC alebo relationship-aware podmienky nad tenantom, environmentom, resource ownerom, incident assignmentom a action riskom.

Role `SRE` sama nemá povoľovať všetky production zmeny. Policy môže vyžadovať, aby používateľ bol assigned responderom konkrétneho incidentu, agent release bol approved pre daný cluster a tool call zodpovedal current remediation proposal.

## 19. Step-up authentication

High-impact action môže vyžadovať čerstvejšiu alebo silnejšiu human authentication než read-only diagnostics. Step-up sa viaže na presný action digest a session, nie na všeobecné „používateľ sa dnes prihlásil“.

Ak sa po step-up zmení resource, arguments alebo policy generation, starý proof sa označí stale. Agent nemá meniť proposal tak, aby využil už získanú silnejšiu session bez nového review.

## 20. Service account sprawl

Zdieľaný service account pre desiatky agentov eliminuje attribution a vytvára privilege union. Každý agent alebo security-equivalent capability group potrebuje vlastnú workload identity a policy binding.

Identity cardinality sa nesmie riešiť návratom k jednému admin credentialu. Automatizované issuance, rotation a policy-as-code sú správnym spôsobom, ako zvládnuť veľký počet krátkodobých machine identities.

## 21. Identity registry

Registry eviduje agent ID, ownera, release, workload selector, trust domain, allowed tools, credential broker role, environments, data classification, expiry a revocation status. Discovery metadata od agenta alebo MCP/A2A endpointu nie sú authority pre identity enrollment.

Unknown alebo expired agent identity sa nesmie automaticky auto-register pri prvom úspešnom requeste. Enrollment je privileged control-plane operation s reviewom a dôkazom ownershipu.

## 22. Multi-agent identity propagation

Supervisor, router a specialist nesmú prepisovať subject/actor chain vo free-form handoff texte. Delegation contract prenáša canonical identity refs a explicitne určuje, či child agent koná ako samostatný actor alebo ako bounded sub-actor parent operationu.

Nested agent nemá zdediť všetky parent credentials. Dostáva capability alebo token obmedzený na svoju task scope a time budget.

## 23. Cross-tenant isolation

Tenant sa odvodzuje z authenticated subjectu a trusted operation contextu. Model input, retrieved document alebo tool output nesmie zmeniť tenant claim.

Token exchange, cache, policy decisions, run state a audit logs musia obsahovať tenant boundary. Cross-tenant token alebo task ID sa fail-closed odmietne aj vtedy, keď downstream resource name vyzerá rovnako.

## 24. Revocation

Revocation môže zasiahnuť human session, workload identity, agent release, key, token, policy binding alebo approval. Systém potrebuje descendant graph, aby vedel zastaviť runs a credentials odvodené z kompromitovaného root subjectu.

Krátkodobé credentials znižujú potrebu okamžitého blacklistu, ale high-risk incident môže vyžadovať aktívne odobratie policy, workload registration alebo downstream role. Revocation status sa kontroluje pred mutation, nie iba pri začiatku runu.

## 25. Key rotation

Workload keys a trust bundles sa rotujú bez zmeny canonical identity. Runtime musí vedieť súbežne overovať current a prechodné trust generations a nesmie zameniť key change za nový agent principal.

Naopak, zmena agent ownera alebo trust domainu nie je iba key rotation. Vyžaduje nové enrollment a policy rozhodnutie, pretože mení authority boundary.

## 26. Identity cache

JWKS, trust bundles, token introspection a policy výsledky sa môžu cacheovať, ale každý cache entry potrebuje issuer, key ID, generation, fetched-at, expiry a invalidation policy. Unknown key nemá viesť k permanentnému deny bez controlled refreshu, no refresh endpoint nesmie byť dynamicky zvolený z untrusted tokenu.

Stale cache môže akceptovať odvolanú identity alebo odmietnuť novo rotovaný key. Incident diagnostika preto porovnáva loaded cache generation s authority source, nie iba HTTP status requestu.

## 27. Audit identity chain

Audit record zachytáva subject, actor chain, workload instance, agent release, run/task/tool-call IDs, token issuer/audience/scope, policy decision, approval, resource UID a downstream request ID. Secret alebo celý token sa do logu neukladá.

```yaml
audit_event:
  event: tool.authorization
  subject: user:martin-vyhonsky
  actors:
    - spiffe://prod.example/agents/checkout-remediator
    - spiffe://prod.example/workers/code-executor
  operation_id: checkout-incident-2049
  tool_call_id: tc-77
  action: deployment.restart.propose
  policy_decision_id: pd-9981
  outcome: denied
  reason: actor_not_allowed_for_environment
```

Audit musí umožniť spätne rekonštruovať chain bez toho, aby sa spoliehal na model transcript.

## 28. Incident `AGENT-SEC-04`

Remediation agent bol spustený používateľom assigned k incidentu, ale supervisor odovzdal specialistovi iba textové meno používateľa. Specialist použil shared `ops-automation` service account a token exchange vydal široký `ops:write` token bez actor claimu.

Retrieved issue potom presvedčil specialistu, aby zavolal credential tool a cloud API. Downstream log ukázal iba `ops-automation`; nebolo možné dokázať, ktorý agent release, run a human subject vytvorili mutation request.

Správny tok mal byť:

```text
authenticated human subject and incident assignment
→ attested supervisor workload identity
→ typed delegation with subject and actor chain
→ specialist-specific workload identity
→ narrow token exchange for one resource and action
→ policy over current operation, release and approval
→ sender-constrained short-lived credential
→ downstream audit with subject and actors
→ business and identity-chain read-back
```

Containment odobral shared accountu production write, zrušil outstanding tokens a zastavil runs bez complete actor chainu. Recovery zaviedla per-agent SPIFFE IDs, token exchange policy a mandatory audit fields.

## 29. Failure hypotheses

Identity incident sa diagnostikuje od root subjectu po downstream resource server. Najprv sa overí, kto inicioval operation, aký agent release a workload instance ju prevzali a aký credential bol reálne prezentovaný. Tým sa oddelí chyba enrollmentu od token issuance, propagation alebo policy evaluation.

Druhá vrstva porovná requested a issued audience, resource, scope a actor claims s tool contractom. Validný podpis nevylučuje wrong audience, privilege expansion alebo zamenenú delegation semantics. Napokon sa overí, či downstream authorization použila current policy a či audit zachoval celú identity chain.

- **Wrong workload binding** — node alebo process selectors vydali SVID inému workloadu; dôkazom sú attestation records a Workload API mapping.
- **Shared-principal collapse** — viac agentov používalo rovnaký service account, takže audit a revocation nevedeli izolovať actor-a.
- **Subject loss** — token exchange odstránil human alebo business subject a ponechal iba machine identity.
- **Actor spoofing** — actor claim pochádzal z modelového inputu alebo unsigned headeru namiesto trusted runtime contextu.
- **Audience confusion** — token určený pre jednu API bol akceptovaný iným resource serverom.
- **Scope expansion** — exchange alebo broker vydal širšie permissions než inbound token a current operation.
- **Stale policy decision** — cached allow prežil zmenu role, incident assignmentu alebo resource generation.
- **Key-cache drift** — verifier používal zastaraný JWKS alebo trust bundle a nesprávne prijal či odmietol identity.
- **Revocation gap** — root identity bola odobratá, ale descendant sessions, tokens alebo runs pokračovali.
- **False attribution** — log obsahoval display name bez canonical subject, actor chainu a runtime generation.

Každá hypotéza sa falsifikuje pomocou identity registry, attestation, token exchange records, cryptographic verification, policy decision logu a downstream audit trailu. Samotné tvrdenie agenta „konal som ako používateľ“ nie je identity evidence.

## 30. Containment

Pri identity incidente sa pozastavia mutation capabilities pre affected principal, agent release, trust domain alebo broker role. Runs bez complete subject/actor chainu prejdú do read-only reconciliation a nové token exchanges sa fail-closed odmietnu.

Containment zachová token metadata, attestation records a policy decisions, ale revokuje aktívne credentials podľa blast radiusu. Hromadná rotácia všetkých trust domains bez evidence môže zhoršiť dostupnosť a skryť first divergence.

## 31. Recovery

Recovery opraví workload registration, trust bundle, token exchange mapping, actor claim propagation, audience/scope policy alebo downstream authorization. Shared accounts sa rozdelia a outstanding descendants sa zneplatnia.

Po oprave sa replayuje rovnaký business scenario s current human assignmentom, agent release a exact resource. Recovery nie je hotová, kým downstream audit nezobrazí správny subject, actor chain a policy decision a business outcome nezodpovedá povolenej action.

## 32. Positive acceptance

Pozitívny test autentifikuje používateľa, attested workload a tool caller-a, vytvorí narrow delegated token a povolí jednu exact read-only alebo approval-bound action. Downstream log musí zachovať subject, actor, audience, scope, operation a resource identity.

Po expiry sa credential nepoužije. Resume vytvorí nový credential po novej policy evaluácii bez zmeny operation identity.

## 33. Forbidden acceptance

Zakázaný test podstrčí token pre inú audience, chýbajúci actor chain, nesprávny tenant, širší scope, expired SVID alebo stale policy decision. Resource server alebo policy layer musí request odmietnuť pred side effectom.

Ďalší test vloží `subject=user:admin` do tool arguments. Runtime musí tento field ignorovať alebo odmietnuť, pretože identity pochádza výhradne z trusted contextu.

## 34. Recovery acceptance

Recovery test rotuje workload key, revokuje human role počas pause, zmení agent release a obnoví run na inom workerovi. Systém musí overiť current trust, znovu vyhodnotiť authorization a nepoužiť stale token ani approval.

Audit musí ukázať, ktorá zmena spôsobila deny alebo nový approval requirement. Silent fallback na shared service account je zakázaný.

## 35. Second-operation acceptance

Nový incident alebo user request dostane nový operation ID, novú delegation chain a nový narrow credential. Nesmie zdediť subject, role, token, policy allow ani resource binding z predchádzajúcej operácie.

Tým sa overí, že identity lifecycle je operation-scoped a že úspech jedného runu nevytvára standing authority pre ďalší.

## 36. Zhrnutie

Agent identity je chain medzi human alebo business subjectom, agent definition, attested workloadom, runom, tool callerom a downstream actorom. Authentication overuje credential a sendera; authorization rozhoduje o presnej action nad presným resource v aktuálnom contexte.

Bezpečný systém používa canonical identities, krátkodobé a sender-constrained credentials, explicitnú delegation semantics, narrow token exchange, per-action policy, revocation graph a complete audit chain. Najdôležitejšia otázka nie je „má agent token?“, ale „ktorý subject a actor, pod ktorou release a policy generation, smú vykonať túto exact action práve teraz?“