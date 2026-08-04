# Human-in-the-loop a approval gates

Human-in-the-loop neznamená, že sa človek niekde objaví v procese. Produkčný approval gate je riadený state transition, ktorý zastaví vykonanie pred citlivou akciou, zobrazí reviewerovi presný subject, argumenty, dôkazy, risk a expected postcondition, zaznamená rozhodnutie a pri resume znovu overí, že schválená akcia je stále totožná a povolená. Neurčitá otázka „Mám pokračovať?“ neposkytuje informed consent ani bezpečnostnú hranicu.

V incidente `AGENT-OPS-02` supervisor zobrazil approval kartu „Reštartovať checkout služby na obnovenie prevádzky“. Karta neobsahovala konkrétne resources, deployment generations, namespaces, restart order ani action digest. Počas päťminútového čakania GitOps nasadil novú canary generation a on-call engineerovi sa zmenila incident role. Resume napriek tomu použil staré approval rozhodnutie a dvaja specialists vykonali dva restarty. Kliknutie bolo autentické, ale schválený subject nebol jednoznačný a runtime nevykonal freshness, authorization ani idempotency revalidation.

## 1. Approval gate ako state machine

Approval gate má explicitné stavy:

```text
proposed
→ policy-evaluated
→ awaiting-approval
→ approved | edited | rejected | expired | revoked
→ revalidated
→ executing
→ succeeded | failed | unknown-outcome
→ business-verified
```

Model nemá preskočiť z `proposed` priamo na `executing`. Každý transition má actor, timestamp, input generation a audit event.

## 2. Kedy approval potrebujeme

Approval sa viaže na risk a policy, nie na to, či tool „vyzerá nebezpečne“. Typické approval-required actions zahŕňajú finančné transakcie, produkčné mutácie, delete operácie, odosielanie externých správ, zmeny identity alebo prístupov, publikovanie obsahu, spustenie kódu s rozšírenými oprávneniami a spracovanie citlivých dát mimo schválenej trust zóny.

Read-only tool môže tiež potrebovať approval, ak sprístupňuje highly restricted dáta alebo prekračuje pôvodný účel operácie.

## 3. Approval policy

Policy engine rozhoduje, či action proposal môže pokračovať automaticky, potrebuje jedného reviewera, separation of duties, multi-party approval alebo sa nesmie vykonať vôbec.

```yaml
policy_id: production-remediation/v9
rules:
  - match:
      tool: kubernetes_rollout_restart
      environment: production
    decision: require-approval
    reviewer_role: incident-commander
    approval_ttl_seconds: 300
    require_separation_of_duties: true
  - match:
      tool: payment_refund
      amount_eur_gte: 500
    decision: require-two-approvals
  - match:
      tool: delete_customer_ledger
    decision: deny
```

Model môže poskytnúť risk explanation, ale finálne policy decision nemá byť iba modelová klasifikácia.

## 4. Exact approval subject

Approval sa viaže na immutable action envelope. Envelope musí obsahovať business operation, tool contract, canonical resources, arguments, identity, policy, preconditions, expected side effect a expiry.

```yaml
approval_request_id: apr-2044-03
operation_id: checkout-incident-2044
action_id: restart-checkout-canary
proposal_generation: 2
tool_contract: kubernetes-rollout-restart/v4
canonical_subjects:
  - cluster: eu-prod-1
    namespace: checkout
    kind: Deployment
    name: checkout-canary
    uid: 6f9f...
arguments:
  strategy: rolling
  max_unavailable: 1
preconditions:
  resource_version: "8839201"
  active_generation: 42
  error_budget_remaining: 0.73
expected_postconditions:
  - rollout_generation_increases_by: 1
  - ready_replicas_equals_desired: true
risk: high
policy_generation: production-remediation/v9
auth_context_digest: sha256:...
expires_at: 2026-08-04T14:23:00Z
action_digest: sha256:...
```

Reviewer schvaľuje `action_digest`, nie voľný prose summary.

## 5. Canonicalization pred approval

Resource names a arguments sa canonicalizujú pred vytvorením approval requestu. Alias `checkout` môže v rôznych clusters označovať iný objekt. Approval UI musí zobrazovať canonical ID, environment a owner.

Ak sa canonical subject nedá jednoznačne resolve-núť, request sa nevytvorí. Reviewer nemá suplovať resource resolution.

## 6. Proposal a execution separation

Agent vytvára proposal; deterministic executor vykoná schválenú action. Proposal nemá side effect. Executor prijme iba action envelope s platným approval verdictom, policy generation a idempotency identity.

```python
def execute_approved_action(request: ApprovalRequest, decision: ApprovalDecision) -> Outcome:
    verify_signature(decision)
    verify_decision_matches_digest(decision, request.action_digest)
    verify_not_expired(request)
    revalidate_authorization(request)
    revalidate_policy(request)
    revalidate_preconditions(request)
    return execute_once(request.action_id, request.tool_contract, request.arguments)
```

Modelový text „approved“ nie je validný decision artifact.

## 7. Approve, edit, reject a escalate

Approval UI môže podporovať viac rozhodnutí:

- **Approve** — povoľuje presne zobrazený action digest.
- **Edit** — vytvorí novú proposal generation s novými arguments a digestom; pôvodný approval sa nepoužije.
- **Reject** — zastaví action a môže pridať bounded feedback pre replanning.
- **Escalate** — odovzdá rozhodnutie reviewerovi s vyššou authority alebo inej roli.

Edit nie je approval pôvodnej akcie. Po zmene resource, amount alebo parameter sa musí spustiť nová policy evaluation.

## 8. Reviewer identity

Reviewer sa autentifikuje strong identity mechanizmom primeraným risku. Decision artifact obsahuje canonical principal ID, authentication context, role, tenant, organization a session freshness.

Email adresa alebo display name nie sú dostatočná immutable identity. Pri citlivých akciách sa môže vyžadovať recent authentication alebo step-up MFA.

## 9. Reviewer authorization

To, že používateľ vidí approval kartu, neznamená, že smie rozhodnúť. Authorization sa overuje pri zobrazení aj pri odoslaní decisionu. Role alebo entitlement sa môžu počas čakania zmeniť.

```text
authenticate reviewer
→ resolve current roles and incident assignment
→ evaluate approval policy
→ accept signed decision
→ revalidate again before execution
```

Stará browser session nesmie prebiť aktuálne odvolané oprávnenie.

## 10. Separation of duties

Pri high-impact actions nemá rovnaký principal navrhnúť, schváliť aj vykonať akciu. Separation of duties môže vyžadovať odlišného reviewera, dvoch reviewerov alebo nezávislý security approval.

Agent identity sa nepovažuje za človeka, ktorý spĺňa druhú approval rolu. Viac agentov pod jedným service accountom tiež nepredstavuje nezávislosť.

## 11. Approval TTL

Approval má krátku platnosť podľa volatility subjectu. Deployment state sa môže meniť v sekundách až minútach; schválenie produkčnej mutácie nemá zostať platné hodiny.

TTL samo nestačí. Aj pred expiry môže resource version, policy, identity alebo incident state zmeniť význam akcie. Preto sa pri resume kontroluje freshness všetkých preconditions.

## 12. Resume a durable state

Agent run môže čakať na rozhodnutie dlhšie než život procesu. OpenAI Agents SDK a LangGraph dokumentujú pause/resume pattern, v ktorom sa run state serializuje a po decisione obnoví. Produkčný systém potrebuje durable persistence, exact thread/run identity a versioned state schema.

Resume nesmie znovu prehrať nodes pred interruptom, ak obsahujú ne-idempotent side effects. Side effects pred approval boundary musia byť read-only alebo idempotentné.

## 13. Revalidation po resume

Pred execution sa porovná current state so schváleným envelope:

```text
same action digest?
same canonical subject and UID?
same resource generation or allowed drift?
same policy generation or compatible policy?
reviewer still authorized?
credentials still valid?
preconditions still true?
no equivalent action already committed?
```

Pri zmene sa request označí `stale` a agent musí replanovať alebo vytvoriť nový approval request.

## 14. Approval drift

Approval drift nastáva, keď sa po schválení zmení subject alebo context. Príklady sú nový deployment, zmena refund amountu, odlišný recipient email, nový SQL query plan alebo zmena tool contractu.

Runtime nemá „približne“ aplikovať starý approval. Digest mismatch je fail-closed transition.

## 15. Argument digest

Digest sa počíta z canonical serialization všetkých execution-relevant fields. Nezahŕňa iba prose summary. Serialization musí byť deterministic a versioned.

```python
import hashlib
import json


def action_digest(envelope: dict) -> str:
    canonical = json.dumps(
        envelope,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()
```

Ak tool runtime doplní default parameter, musí byť zahrnutý pred approvalom alebo musí mať policy-approved invariant.

## 16. Preview

Reviewer potrebuje preview efektu. Pri file change ide o diff, pri SQL o query a estimated affected rows, pri infra zmene o resource diff, pri refund o amount, recipient a ledger reference.

Preview má vzniknúť z toho istého canonical proposal, ktoré sa neskôr vykoná. Samostatne generovaný natural-language summary môže skryť kritický parameter.

## 17. Evidence pre decision

Approval karta obsahuje dôvod, supporting evidence, competing hypotheses, risk, rollback alebo compensating action a business invariant. Reviewer nemá dostať iba model confidence.

```text
symptom and impact
current authoritative state
proposed action and exact target
why this action follows from evidence
known alternatives
expected postcondition
rollback or compensation path
expiry and reviewer responsibility
```

Evidence refs majú byť dostupné reviewerovi v jeho authorization scope.

## 18. Inaccessible evidence

Ak reviewer nemôže otvoriť citation alebo source, approval nie je informed. Systém musí rozlišovať, či agent mal retrieval access a či reviewer má disclosure access.

Pri restricted evidence môže UI zobraziť redacted authoritative summary podpísané trusted service, ale nesmie predstierať, že reviewer videl raw source.

## 19. Approval batching

Batch approval znižuje friction, ale zvyšuje blast radius. Každá action v batchi potrebuje vlastný ID, digest, subject a outcome. Blanket approval „vykonaj všetky odporúčané opravy“ je neprijateľný pre heterogénne high-impact actions.

Policy môže povoliť batch iba pre homogénne, bounded a independently idempotent actions s maximálnym countom a aggregate risk limitom.

## 20. Multi-party approval

Pri dvoch approvaloch sa ukladá order, required roles, individual signatures a spoločný action digest. Druhý reviewer schvaľuje rovnakú generation ako prvý.

Ak edit vytvorí nový digest, všetky predchádzajúce approvals sa invalidujú. Nie je možné preniesť prvý podpis na zmenenú akciu.

## 21. Rejection feedback

Rejection môže obsahovať structured reason code a bounded feedback:

```json
{
  "decision": "reject",
  "reason_code": "INSUFFICIENT_EVIDENCE",
  "feedback": "Obtain current payment-provider status and checkout conversion before proposing mutation."
}
```

Agent smie replanovať, ale nesmie preformulovať rovnakú akciu a obísť rejection novým action ID. Similarity a subject checks spájajú návrhy s pôvodným decisionom.

## 22. Approval fatigue

Príliš veľa approval requestov vedie k mechanickému klikaníu. Systém má znižovať potrebu approvals architektonicky: používať read-only tools, narrow permissions, deterministic workflows, safe defaults a menšie blast radii.

Metriky zahŕňajú approval volume, rejection rate, median review time, edit rate, expired approvals, duplicate proposals a incidents after approval. Nízka rejection rate nemusí znamenať kvalitu; môže znamenať fatigue.

## 23. Auto-approval

Niektoré nízkorizikové actions možno automaticky schváliť policy engineom. Auto-approval je deterministic policy verdict, nie modelové sebahodnotenie.

```text
read-only + non-sensitive + bounded cost + trusted subject
→ auto-approve

production mutation or external communication
→ human review
```

Policy generation a reason code sa logujú aj pri auto-approval.

## 24. Pre-action a post-action review

Pre-action approval zabraňuje side effectu. Post-action review hodnotí výsledok alebo low-risk autonomous action po vykonaní. Post-action review nie je náhrada za pre-action gate pri nezvratnej mutácii.

Systém môže kombinovať oba: človek schváli rollout a po execution review-ne outcome a business metrics.

## 25. Unknown outcome

Timeout po execution requeste vytvára unknown outcome. Agent nesmie znova požiadať o approval pre „retry“ bez read-backu, pretože prvá akcia mohla byť commitnutá.

```text
execution timeout
→ mark action unknown_outcome
→ query target by action_id/idempotency_key
→ classify committed | not_committed | indeterminate
→ continue, compensate or escalate
```

Pôvodný approval nepovoľuje neobmedzený počet attempts.

## 26. Idempotency

Approval-bound action má stabilný action ID alebo idempotency key odvodený z business operation, nie z technical attemptu. Executor používa rovnakú identity pri bezpečnom retry.

Ak tool nepodporuje idempotency, policy môže vyžadovať manual execution alebo stronger reconciliation pred každým attemptom.

## 27. Approval a tool contract versioning

Schválenie pre `tool/v3` sa nesmie automaticky použiť pre `tool/v4`, ak sa zmenili semantics, defaults alebo side effects. Tool contract generation je súčasť digestu.

Deployment novej tool generation invaliduje pending approvals, pokiaľ compatibility policy explicitne nepreukazuje identický execution behavior.

## 28. Approval a model replanning

Po approvale model nesmie meniť arguments počas execution. Replanning medzi approval a tool callom vytvára nový proposal.

Executor prijíma iba schválený envelope priamo, nie nový model output „vykonaj schválenú akciu s týmito aktualizovanými parametrami“.

## 29. Nested agents a approvals

Citlivý tool môže byť zavolaný top-level agentom, handoff specialistom alebo nested agent-as-tool runom. Approval interruption musí vystúpiť na operation ownera a uplatniť rovnakú policy.

OpenAI Agents SDK uvádza, že approval požiadavky z nested `Agent.as_tool()` execution sa zobrazia na outer run state. To je implementačný pattern, ale aplikácia stále musí uchovať exact nested run, tool a action identity.

## 30. Multi-agent duplicate approvals

Dvaja specialists môžu navrhnúť rovnakú akciu. Approval service deduplikuje proposals podľa canonical subject, tool semantics a business operation. Reviewer nemá dostať dve karty, ktoré vyzerajú odlišne iba wordingom.

Ak proposals konfliktujú, supervisor musí syntetizovať alebo eskalovať; nesmú sa schváliť nezávisle bez conflict analysis.

## 31. Audit trail

Audit obsahuje proposal, policy decision, reviewer identity, authentication context, displayed evidence digest, decision, timestamps, edits, expiry, revalidation, execution attempts, target request IDs, outcome a business read-back.

Raw sensitive content sa loguje iba podľa data policy. Hash bez bezpečne dostupného referenced artifactu nemusí stačiť na forenzný audit.

## 32. Non-repudiation a signatures

High-assurance systém môže podpisovať action envelope a approval decision. Signature chráni integritu medzi UI, approval service a executorom. Nezaručuje však, že reviewer správne pochopil risk alebo že source evidence bolo pravdivé.

Cryptographic integrity dopĺňa, nie nahrádza, usability, authorization a business validation.

## 33. Approval UI

UI musí zvýrazniť environment, resource, irreversible effect, external recipient, amount, data classification a diff. Critical fields nemajú byť ukryté v expandovateľnom prose bloku.

Pri mobile alebo chat approvale sa stále zobrazí exact subject a digest reference. Reakcia emoji bez strong identity a action binding nie je approval artifact.

## 34. Emergency bypass

Break-glass bypass má vlastnú policy, short TTL, explicitný reason, strong authentication, narrow scope a immediate audit alert. Agent si nemôže sám aktivovať emergency mode.

Bypass nezruší idempotency, subject canonicalization ani business read-back. Po incidente sa vykoná povinný review a credential/session revocation podľa policy.

## 35. Approval service availability

Ak approval service nie je dostupná, high-impact action failne closed alebo sa eskaluje na schválený manual runbook. Agent nesmie interpretovať timeout ako approval.

Low-risk read-only flow môže pokračovať, ale UI jasne označí, že mutation je blocked.

## 36. Privacy a retention

Approval records môžu obsahovať citlivé arguments a evidence. Retention sa riadi audit, privacy a legal policy. Reviewer comments sa nemajú automaticky používať ako long-term agent memory bez samostatného purpose a review.

Deletion request musí zohľadniť, že niektoré audit records majú zákonnú retention, zatiaľ čo derived model context alebo analytics copy možno odstrániť skôr.

## 37. Incident `AGENT-OPS-02`

Supervisor vytvoril approval summary bez canonical resources. Počas čakania GitOps zmenil deployment generation a druhý specialist vytvoril podobnú restart proposal. Approval service nevykonala deduplication a executor neoveril resource version ani reviewer entitlement.

Správny tok bol:

```text
one canonical action proposal
→ policy evaluation
→ immutable approval envelope and preview
→ authenticated and authorized decision
→ resume with state generation check
→ policy, identity and precondition revalidation
→ execute once with stable action ID
→ technical and business read-back
```

Pôvodný approval sa po generation change mal označiť `stale` a vyžiadať nový review.

## 38. Failure hypotheses

Pri incidente po ľudskom schválení nie je správny záver „človek to povolil“. Failure môže vzniknúť v proposal, UI, identity, policy, persistence, resume, execution alebo outcome verification.

- **Ambiguous subject** — karta nezobrazila exact resource, recipient, amount alebo environment.
- **Digest mismatch** — vykonané arguments sa líšili od schváleného envelope.
- **Stale approval** — resource, policy, identity alebo evidence sa zmenili počas čakania.
- **Authorization drift** — reviewer už pri execution nemal required role.
- **Duplicate proposal** — viac agentov vytvorilo ekvivalentné approval requests.
- **Replay** — starý decision artifact sa použil na nový action attempt alebo operation.
- **Unknown outcome retry** — timeout viedol k opakovaniu už commitnutej akcie.
- **UI omission** — critical field alebo alternative bol skrytý.
- **Approval fatigue** — reviewer schvaľoval bez primeranej kontroly pre vysoký volume.
- **Audit gap** — chýbal displayed evidence digest alebo execution request ID.

Každá hypotéza sa testuje proti approval, identity, execution a business records.

## 39. Containment

Pri approval incidente sa zastavia pending actions pre affected policy alebo tool generation. Mutation agents prejdú do read-only mode, stale approvals sa revokujú a executor môže vyžadovať manual operation reconciliation.

Containment zachová decision artifacts a runtime traces. Mazanie approval records by zničilo forenznú väzbu.

## 40. Recovery

Recovery zahŕňa opravu envelope schema, UI, policy, reviewer authorization, deduplication, resume revalidation alebo executor idempotency. Pending requests sa nerecyklujú automaticky; vytvoria sa nové proposals iba po aktuálnom read-backu.

Ak bola akcia vykonaná dvakrát, recovery obsahuje compensating business action a overenie downstream state. Rollback agent code sám duplicate side effect neopraví.

## 41. Positive acceptance

Pozitívny test vytvorí exact proposal, zobrazí review evidence, pozastaví run, prijme authorized decision, revaliduje nezmenené preconditions a vykoná jednu akciu. Technical postcondition aj business outcome musia byť potvrdené read-backom.

## 42. Forbidden acceptance

Zakázaný test zmení arguments, resource generation, policy alebo reviewer role po approvale. Executor musí odmietnuť stale alebo mismatch decision. Ďalší test skúsi replay decisionu v inom tenantovi alebo operation a musí byť blokovaný.

## 43. Recovery acceptance

Recovery test simuluje approval-service restart, process loss, duplicate delivery decisionu a execution timeout. Run sa musí bezpečne obnoviť z durable state, decision sa aplikuje najviac raz a unknown outcome sa reconciliuje pred retry.

## 44. Second-operation acceptance

Druhá operácia s rovnakým toolom potrebuje nový action ID, subject digest a approval. Predchádzajúci decision sa nesmie preniesť ani pri rovnakom reviewerovi. Druhá operácia iného tenanta musí byť storage a authorization izolovaná.

## 45. Alternate-scenario acceptance

Alternate scenario používa low-risk read-only action, ktorú policy auto-approve-ne, a high-risk mutation, ktorá vyžaduje človeka. Tým sa overí, že approval policy nie je globálne „vždy“ ani „nikdy“, ale rešpektuje risk a subject.

## 46. Prevádzkový runbook

Runbook pre stuck approval obsahuje exact request ID, thread/run state, policy decision, reviewer identity status, expiry, current resource generation, duplicate proposals a execution attempts. Operátor najprv číta state a downstream outcome; nevytvára nový approval request naslepo.

```text
locate approval request
→ verify action digest and status
→ inspect current authorization and policy
→ compare current subject generation
→ inspect execution attempts
→ reconcile business outcome
→ expire, resume or recreate proposal
```

Runbook musí mať safe manual fallback a audit procedure.

## 47. Primárne zdroje a proof boundary

OpenAI Agents SDK Human-in-the-loop dokumentuje tool-level approval, interruptions, serializovaný `RunState` a resume pre top-level aj nested agent runs. LangGraph a LangChain dokumentácia opisuje interrupts, persistent checkpointing a rozhodnutia approve, edit alebo reject; zároveň upozorňuje, že side effects pred interruptom musia byť idempotentné.

Tieto framework mechanizmy poskytujú pause/resume primitives. Neimplementujú automaticky organization-specific identity, authorization, separation of duties, canonical business subject, approval digest, idempotency alebo business outcome validation. Repository validácia kapitoly nevykonáva reálnu approval session, role revocation, duplicate delivery, tool side effect ani recovery drill.