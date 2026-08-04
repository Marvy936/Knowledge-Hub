# Data exfiltration, tool abuse a excessive agency

Excessive agency vzniká, keď GenAI application poskytne modelu viac functionality, permissions alebo autonomy, než potrebuje na konkrétny task. Model potom môže pri hallucination, ambiguous user requeste, prompt injection alebo tool failure vykonať škodlivú, ale technicky povolenú akciu. Security problém nie je len „model urobil chybu“. Root cause je application capability boundary, ktorá dovolila chybe zmeniť dôvernosť, integritu alebo dostupnosť reálneho systému.

V incidente `GENAI-SUPPORT-08` support agent mal jediný connector pre mailbox, dokumenty a odosielanie správ. Na summarization task dostal delegated token s read aj send scope. Indirect prompt injection v prílohe vyvolala search bankových výpisov a následné odoslanie na externú adresu. Všetky API calls boli validné a autorizované pre broad service account. Gateway preto zaznamenala success. Incident vznikol kombináciou excessive functionality, excessive permission, excessive autonomy a chýbajúceho egress/approval controlu.

## 1. Exact agency subject

Agency sa hodnotí pre konkrétny task, principal, capability set, resource scope a autonomy policy.

```yaml
agency_subject:
  operation_id: support-case-82413
  user_goal: summarize-ticket-attachments
  acting_principal: support-agent-session-91
  delegated_user: user-441
  tool_catalog: support-tools-v16
  authorization_snapshot: authz-71c2
  autonomy_policy: support-readonly-v8
  release_manifest: support-release-2026-08-04.8
```

„Agent má Gmail access“ alebo „agent používa cloud tools“ je príliš hrubý statement. Potrebné je vedieť exact actions, resources, identities, conditions a side-effect boundaries.

## 2. Functionality, permission a autonomy

Tri osi sa oddeľujú:

```text
functionality
→ aké operácie tool vôbec ponúka

permission
→ nad ktorými resources ich principal smie vykonať

autonomy
→ za akých podmienok ich agent smie spustiť bez ďalšieho človeka
```

Agent môže mať úzky tool, ale príliš broad resource permission. Alebo môže mať správne permissions, no vykonávať high-impact action bez confirmation. Bez tohto rozkladu sa mitigácia sústredí na nesprávnu vrstvu.

## 3. Capability contract

Každý task má explicitný capability contract:

```yaml
capability_contract:
  task: summarize-ticket-attachments
  allowed:
    - read_ticket_thread
    - read_attachment
  forbidden:
    - search_other_threads
    - send_email
    - upload_file
    - modify_acl
  resource_scope:
    ticket_id: 82413
  max_operations: 20
  expiry: 15m
```

Tool catalog sa zostaví z contractu pred model invocation. Model nemôže presvedčiť policy layer, aby mu pridala neplánovaný tool iba natural-language argumentom.

## 4. Tool decomposition

Monolitický connector s `execute(action, args)` komplikuje policy. Bezpečnejšie sú malé typed operations s odlišnými permissions.

```text
mail.read_thread
mail.search_all
mail.send
mail.delete
```

Read a write capabilities sa oddeľujú. Trial alebo deprecated tools sa odstránia z runtime catalogu, nie iba z promptu.

## 5. Tool schema

Schema obmedzuje argument shape, ale nie business authorization. URL string môže byť syntakticky validný a smerovať na attacker endpoint.

```json
{
  "name": "send_summary",
  "parameters": {
    "type": "object",
    "properties": {
      "ticket_id": {"type": "integer"},
      "recipient_id": {"type": "string"},
      "summary_id": {"type": "string"}
    },
    "required": ["ticket_id", "recipient_id", "summary_id"],
    "additionalProperties": false
  }
}
```

`recipient_id` sa resolve-ne cez trusted directory a policy, nie na arbitrary email text od modelu.

## 6. Principal a credential boundary

Model nikdy nedostáva raw API key, OAuth refresh token alebo cloud secret. Tool executor drží credentials a vykonáva policy nad authenticated principal.

```yaml
execution_identity:
  workload_identity: support-tool-executor
  delegated_subject: user-441
  scopes: [ticket.read]
  audience: support-api
  expires_in: 600s
  token_binding: operation-82413
```

Ambient broad service-account credentials zvyšujú blast radius. Krátkodobé scoped tokens znižujú dopad compromise, ale nenahrádzajú resource authorization.

## 7. Resource-level authorization

Authorization sa vykonáva nad canonical resource po resolution. Model môže navrhnúť `ticket_id=82413`; executor overí tenant, ownership, user entitlement a task contract.

TOCTOU risk vzniká, ak preview a execution resolve-nú rozdielny resource. Confirmation sa viaže na immutable action digest a current authorization snapshot.

## 8. Delegated user authority

Delegation neznamená, že agent zdedí všetky user capabilities. User môže manuálne poslať email komukoľvek, ale summarization agent nemusí mať send capability.

```text
user maximum authority
≠ authority potrebná pre task
≠ authority delegovaná agentovi
```

Delegation je explicitná, časovo obmedzená a task-scoped.

## 9. Data classification

Pred tool callom a egressom sa data klasifikujú: public, internal, confidential, regulated, secret. Classification môže vychádzať zo source metadata, DLP a policy.

```yaml
data_object:
  id: bank-statement-71
  classification: confidential-financial
  tenant: sk-retail
  owner: user-441
  export_policy: user-explicit-only
```

Model summary nesmie znížiť classification iba preto, že text preformuloval. Derived data zdedí alebo prepočíta classification podľa policy.

## 10. Exfiltration channels

Exfiltration nemusí byť iba email. Kanály zahŕňajú URL query, DNS, webhook, file upload, code execution output, image/QR, logs, issue comments, shared documents, calendar invitations a prompt sent to another provider.

Egress inventory mapuje každý tool a telemetry sink. Security review sa nesmie obmedziť na explicitný `send_email` tool.

## 11. Destination policy

Destination sa canonicalize-ne a overí proti allowlistu, tenant boundary a user intentu.

```yaml
egress_decision:
  destination: support-user-441
  resolved_endpoint: internal-mailbox:user-441
  external: false
  data_classification: internal
  approval_required: false
  verdict: allow
```

Redirects, URL shorteners a nested callbacks sa resolve-nú pred send. Dynamic attacker-controlled hostname nie je povolený iba preto, že používa HTTPS.

## 12. Data minimization

Tool dostane len fields potrebné pre operation. Summary agent nepotrebuje full mailbox alebo customer database export.

```text
read exact ticket attachment
> search all customer documents
> export entire mailbox
```

Najmenší scope znižuje prompt-injection blast radius aj accidental disclosure.

## 13. Read versus disclose

Permission čítať data a permission odhaliť ich inému recipientovi sú odlišné. Application potrebuje explicitný information-flow policy.

```text
source principal → agent working context
≠ agent working context → external destination
```

DLP pred egressom kontroluje destination aj content classification. Model refusal alebo warning nie je substitute.

## 14. Side-effect classification

Tools sa klasifikujú podľa reversibility, financial impact, external visibility a security effect.

```yaml
action_class:
  tool: change_role_binding
  reversible: true
  blast_radius: high
  external_visibility: low
  security_impact: critical
  approval: two_person
```

Reversible action môže byť stále high risk, ak rollback nie je okamžitý alebo attacker stihne využiť zmenu.

## 15. Approval tiers

Low-risk read môže bežať automaticky. Medium-risk write vyžaduje user confirmation. High-risk security, financial alebo cross-tenant action môže vyžadovať expert alebo two-person approval.

Approval engine je deterministic policy mimo modelu. Model môže vysvetliť action, ale neurčuje vlastný risk tier.

## 16. Action preview

Pred confirmation sa zobrazí canonical action: tool, target, recipient, data scope, cost a reversibility.

```yaml
action_preview:
  action: send_email
  recipient: external@example.net
  attachments: [bank-statement-71]
  classification: confidential-financial
  irreversible_external_disclosure: true
  action_digest: sha256:771a...
```

Confirmation platí iba pre digest. Zmena recipienta alebo attachmentu vyžaduje novú confirmation.

## 17. Idempotency a unknown outcome

Write tool používa durable operation ID a idempotency key. Timeout sa read-backne pred retry.

```text
submit operation K
→ timeout
→ query operation K
→ committed / absent / pending
→ retry iba podľa authoritative state
```

Blind retry môže zdvojiť payment, email alebo permission mutation. Technical attempt identity sa oddeľuje od business operation identity.

## 18. Rate a volume limits

Rate limiting obmedzí blast radius, no nepreukazuje correctness. Limits môžu byť per user, task, tool, resource, destination a data volume.

```yaml
limits:
  send_email:
    max_per_operation: 1
  read_attachment:
    max_per_operation: 20
  exported_bytes:
    max_per_operation: 0
```

High-risk action môže mať limit zero bez approval tokenu.

## 19. Budget a consumption

Agent loops môžu vyvolať nákladný alebo denial-of-service behavior. Operation budget zahŕňa model calls, tokens, tool calls, wall time a external API cost.

Budget exhaustion vedie k controlled stop alebo escalation. Model nesmie samostatne navýšiť svoj budget.

## 20. Sandboxed execution

Shell, code a browser tools bežia bez ambient credentials, s minimálnym filesystemom, resource limits a egress policy. Workspace je per operation alebo tenant.

Generated code sa považuje za untrusted. Sandbox exit code nie je business acceptance a output sa validuje pred použitím.

## 21. File-system boundary

Agent má allowlisted paths a content classification. Symlinks, archive traversal, mount points a hidden files sa canonicalize-nú.

Read-only task nepoužíva write mount. Temporary files majú cleanup a retention policy. Secret volumes sa do general-purpose sandboxu nepripájajú.

## 22. Network boundary

Network policy povoľuje iba potrebné destinations a protocols. Browser fetch nemá automatický access k cloud metadata endpointu, internal admin panels alebo localhost services.

DNS rebinding, redirects a IP literal bypass sa testujú. Network egress logs sa spájajú s operation ID.

## 23. Cloud a infrastructure tools

Cloud tools musia oddeľovať read, plan a apply. Agent môže vytvoriť proposal alebo diff bez apply permission.

```text
observe resource
→ propose bounded change
→ policy validation
→ human approval
→ apply with scoped identity
→ read-back actual state
```

`admin` role pre pohodlie je forbidden. Break-glass capability má samostatný workflow a audit.

## 24. Database tools

Model nemá arbitrary SQL nad production. Tools používajú parameterized queries, views, stored operations alebo semantic layer s row/column policy.

Read query má result-size limit a sensitive-column filtering. Write operation má business validation a idempotency. Natural-language intent nikdy nie je authorization.

## 25. Communication tools

Email, chat, issue a social tools kontrolujú recipient, channel, mention scope, attachment classification a external visibility. Draft a send sú oddelené capabilities.

Agent môže pripraviť draft bez send permission. User edit po preview vytvorí nový action digest.

## 26. Secrets

Secrets sa resolve-nú v executorovi podľa tool a resource. Model vidí reference, nie secret value.

```yaml
credential_reference:
  secret_id: payments-api-prod
  allowed_tool: refund-status-read
  disclosure_to_model: false
  rotation_policy: 30d
```

Secret v prompt, trace alebo tool output je incident. Redaction sa vykoná pred telemetry exportom, ale primary control je secret neposkytnúť.

## 27. Multi-agent delegation

Delegating agent nesmie preniesť širšie oprávnenia, než má sám, ani širšie, než subtask potrebuje. Capability token obsahuje bounded delegation chain.

```yaml
delegation:
  parent_operation: support-82413
  subtask: extract-dates
  tools: [document.read]
  resources: [attachment-71]
  may_delegate: false
```

Peer output je untrusted data. Multi-agent consensus nie je authorization.

## 28. Model choice a capability

Výkonnejší model môže lepšie plánovať aj účinnejšie zneužiť široké tools pri failure. Security boundary sa preto nesmie spoliehať na slabší model.

Model compatibility eval zahŕňa tool selection, refusal, argument generation a behavior pod attackom. Fallback model bez rovnakej security capability nemôže dostať rovnakú autonomy.

## 29. Policy enforcement point

Policy sa vykonáva pri catalog assembly, proposal validation, authorization, approval, execution a egress. Jeden gateway check pred promptom nestačí.

```text
allowed to see tool?
→ allowed to propose action?
→ allowed on target resource?
→ approved now?
→ allowed to send these data there?
→ durable outcome confirmed?
```

Každý verdict sa loguje s policy version.

## 30. Audit ledger

Write a disclosure operations majú append-only audit: actor, delegated user, tool, canonical arguments digest, authorization, approval, downstream operation ID a outcome.

Telemetry sampling nesmie odstrániť durable security audit. Raw content sa minimalizuje, ale identity a decision evidence sa zachovajú podľa retention policy.

## 31. Monitoring

Signals zahŕňajú forbidden tool proposals, unusual resource breadth, new destinations, high data volume, repeated denials, approval bypass attempts, secret patterns a agent loops.

Anomaly detector je doplnok. Deterministic policy musí blokovať known forbidden action aj pri chýbajúcom anomaly signal-e.

## 32. Threat modeling

Threat model zahŕňa malicious usera, compromised external content, poisoned tool output, malicious connector, confused model, compromised model/provider a insidera.

Pre každý asset sa mapuje source, transformations, model visibility, tool access, egress a audit. „Prompt injection“ je iba jeden entry point do broader information-flow a capability threat modelu.

## 33. Adversarial tests

Testy simulujú direct/indirect injection, hallucinated tool, ambiguous user request, compromised tool output, cross-tenant resource ID, arbitrary recipient, unknown timeout a repeated loop.

```yaml
security_case:
  task: summarize-ticket
  injected_action: send-confidential-attachment
  expected:
    tool_visible: false
    send_attempts: 0
    security_event: excessive-agency-blocked
```

Success sa overí v downstream audit a destination systeme, nie iba v model transcript-e.

## 34. Negative a adjacent acceptance

Negative test overí, že forbidden action je blocked. Adjacent test overí legitímny povolený action s podobnými arguments, aby control neblokoval všetko.

```text
external recipient + confidential attachment
→ deny

current user + approved internal summary
→ allow after required confirmation
```

Security a utility sa hodnotia spolu.

## 35. Failure hypotheses

Pri exfiltration incidente sa skúma capability exposure, identity scope, resource authorization, data classification, destination validation, approval binding a egress. Pri duplicitnom side effectu idempotency, timeout semantics a read-before-retry. Pri agent loop-e budget, termination condition, tool error handling a retry policy.

„Model bol prompt injected“ je trigger, nie úplná root cause. Damage bolo možné iba cez konkrétnu excessive-agency path.

## 36. Containment a recovery

Containment revokuje tokens, vypne affected tools a destinations, zastaví agent sessions, izoluje compromised connectors a read-backne side effects. External disclosures sa riešia podľa incident a legal processu.

Recovery zúži tool catalog a scopes, opraví policy/approval/egress, rotuje secrets, odstráni poisoned memory/cache a revaliduje downstream state. Bounded canary používa synthetic alebo non-sensitive resources. Druhá operácia testuje odlišný tool a recipient/resource boundary.

## 37. Acceptance

Pozitívna acceptance vyžaduje task-scoped capability contract, minimal functionality, permissions a autonomy, typed small tools, scoped short-lived identity, resource authorization, data classification, destination a egress policy, approval binding, idempotency, budgets, sandboxing, durable audit a adversarial plus adjacent tests.

Recovery acceptance vyžaduje preserved attack/operation evidence, revoked capabilities, complete side-effect inventory, corrected policy, secret/memory/cache cleanup, downstream read-back, adversarial replay, bounded canary a second-operation test.

Forbidden acceptance je broad user permission ako agent permission, schema-valid tool call ako authorized action, HTTPS destination ako trusted egress, reversible action ako low risk, rate limit ako prevention, model refusal ako dôkaz bez downstream read-back alebo documentation validation ako production security acceptance.

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Prompt injection a indirect prompt injection](prompt-injection-indirect-prompt-injection.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Guardrails, moderation a output validation →](guardrails-moderation-output-validation.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
