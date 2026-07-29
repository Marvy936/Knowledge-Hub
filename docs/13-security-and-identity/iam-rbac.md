# IAM a RBAC

Identity and Access Management je lifecycle disciplína pre identities, accounts, credentials, authentication, federation, entitlements, privileged access, authorization, review, revocation a audit. Role-Based Access Control je jeden authorization model v tomto systéme. Role sama nevyrieši identity proofing, mover/leaver zmenu, session revocation, trusted attributes ani explainability effective accessu.

IAM musí fungovať ako reconciler medzi authoritative identity/ownership state-om a effective permissions naprieč identity providerom, applications, cloudom, Kubernetesom, databázami a CI/CD.

## 1. Dominantný lifecycle

```text
authoritative identity a resource-owner state
→ identity/entitlement desired generation
→ joiner, mover, leaver alebo workload event
→ account, group, role a attribute reconciliation
→ credential/federation/session generation
→ RBAC/ABAC/resource-policy evaluation
→ enforcement na resource boundary
→ effective-access graph a audit
→ access review, revoke a deprovision
→ second-sync, second-session a forbidden-path validation
```

Tento lifecycle oddeľuje:

```text
HR alebo service catalog obsahuje správny stav
≠ downstream groups a roles sú zhodné
≠ existujúce sessions používajú current entitlement state
≠ effective access nemá alternate path
≠ removal prežil ďalší reconciliation cycle
```

## 2. Exact IAM/RBAC subject

Pre connected Atlas incident používame:

```text
IAM subject: IAM-PAY-47
security subject: SEC-PAY-47
human identity: urn:atlas:human:7421
authoritative source: HR-7421 generation 118
old job function: Payments Operations
new job function: Finance Analytics
mover effective time: 2026-07-29 08:00 UTC
entitlement catalog: ENT-CAT-42
IdP reconciliation: IAM-SYNC-306
nested group path:
  finance-emea
  → legacy-shared-operations
  → prod-payment-operators
federated session: SESSION-771
Kubernetes binding: payments-prod-operators
ClusterRole generation: RBAC-PAY-63
namespace: payments-prod
```

Exact subject viaže business identity state, entitlement path, session a resource-side authorization generation.

## 3. IAM capability map

IAM platforma alebo operating model typicky pokrýva:

- authoritative identity source a identity proofing;
- account provisioning/deprovisioning;
- authenticator a credential lifecycle;
- authentication a session management;
- federation a principal mapping;
- group, role, attribute a entitlement governance;
- access request, approval a JIT activation;
- human aj workload identities;
- policy administration a enforcement integration;
- audit, access review a certification;
- revocation, recovery a break-glass.

Nie každý produkt implementuje celý lifecycle. Architecture musí určiť ownera a interface medzi HR, IdP, PAM, cloud IAM, Kubernetes, applications a audit platformou.

## 4. Authoritative source a desired state

Authoritative source určuje, odkiaľ pochádza pravda o konkrétnom identity alebo ownership attribute.

Príklady:

- HR — employment status, manager, department;
- contractor registry — sponsor a expiration;
- service catalog — workload owner, environment a criticality;
- customer identity store — customer account state;
- cloud inventory — account/resource ownership;
- Kubernetes API/GitOps source — ServiceAccount a binding desired state.

Jeden systém nemusí byť authoritative pre všetky attributes. Potrebná je attribute-level authority matrix:

| Attribute | Authoritative source | Consumer | Freshness/invalidácia |
|---|---|---|---|
| employment status | HR | IdP/PAM/apps | immediate disable event |
| team/job function | HR/org directory | entitlement engine | mover reconciliation |
| service owner | service catalog | workload IAM/review | deployment/review gate |
| production role eligibility | entitlement catalog + resource owner | PAM/IdP | approval + expiry |
| Kubernetes binding | Git/IaC | cluster API | controller reconciliation |

Add-only synchronization nie je desired-state reconciliation. Complete desired state musí vedieť pridávať aj odstraňovať stale assignments.

## 5. Joiner, mover a leaver

### Joiner

```text
proofed/approved identity
→ account generation
→ baseline entitlements
→ authenticator enrollment
→ owner/manager
→ positive a forbidden onboarding tests
```

Baseline access má byť minimálny. Joiner nemá dediť template privileges bez task a environment scoping-u.

### Mover

```text
new job function
→ calculate new desired entitlements
→ remove incompatible old paths
→ SoD/conflict check
→ add approved new paths
→ revoke/refresh sessions
→ effective-access read-back
```

Mover je remove aj add transaction. Najprv pridávať a neskôr „niekedy“ čistiť staré roles vytvára privilege accumulation window.

### Leaver

```text
disable identity
→ revoke sessions/tokens/authenticators
→ remove direct/nested/delegated assignments
→ rotate shared/derived credentials
→ transfer ownership
→ preserve audit/data podľa policy
→ forbidden login a alternate-account test
```

Disable v jednom IdP nemusí odstrániť local application accounts, API keys, certificates, cloud roles alebo cached sessions.

## 6. Entitlement catalog

Entitlement je assignable role, group membership, permission set alebo capability. Catalog entry má obsahovať:

- stable ID a purpose;
- required business task;
- actions a resource scope;
- environment/data classification;
- owner a approver;
- eligibility rules;
- standing alebo JIT model;
- duration a review cadence;
- conflicting entitlements;
- indirect escalation analysis;
- positive/negative tests;
- deprecation a migration plan.

Role name bez permission inventory a ownera nie je governance contract.

## 7. RBAC model

Základný RBAC chain:

```text
principal
→ assignment alebo group membership
→ role
→ permission(action, resource, condition)
→ authorization decision
```

Role reprezentuje reusable job function alebo technical capability. Nemá byť pomenovaná podľa jedného človeka ani vytvorená pre každú náhodnú kombináciu attributes.

### Flat RBAC

Role nemajú inheritance. Effective access sa jednoduchšie vysvetľuje, ale permissions sa môžu opakovať.

### Hierarchical RBAC

Role dedia iné roles. Znižuje duplicitu, ale vytvára transitive privilege a komplikuje removal. Hierarchy musí byť acyclic, bounded a queryovateľná.

## 8. Role engineering

```text
business tasks
→ operation inventory
→ resource/data scopes
→ common a privileged capability clusters
→ SoD/conflict analysis
→ role a assignment design
→ positive/negative/escalation fixtures
→ usage a review
→ split, merge alebo retirement
```

Dobrý role contract má:

- purpose;
- permissions a scope;
- ownera;
- eligible principals;
- activation a duration;
- approval;
- incompatibilities;
- audit expectations;
- removal semantics.

Role count nie je maturity metric. Veľa roles môže znamenať role explosion; málo roles môže znamenať broad ambient authority.

## 9. Role explosion a composability

Role explosion vzniká pri modelovaní každej kombinácie:

```text
team × application × environment × Region × privilege level × tenant
```

Mitigácie:

- base capability roles plus resource-scoped assignments;
- JIT activation;
- trusted ABAC conditions;
- standardized entitlement catalog;
- group-based assignment s bounded nestingom;
- retirement duplicate roles;
- mediated application capabilities namiesto infra role per task.

ABAC nemá iba skryť role explosion do nekontrolovaných attributes.

## 10. RBAC a ABAC

RBAC je vhodný pre stabilné job functions a reusable capabilities. ABAC dopĺňa dynamický scope:

```text
role povoľuje settlement-requeue capability
+ principal.team = payments-operations
+ resource.environment = production
+ payment.tenant in principal.allowed_tenants
+ session.auth_age < 10 min
+ approval.state = approved
```

Attributes musia mať trusted source, schema, freshness a controlled write path. Ak principal môže zmeniť vlastný `team`, `clearance` alebo resource tag použitý na authorization, condition nie je účinný control.

## 11. Groups a nested effective access

Groups zjednodušujú assignment, ale vytvárajú graph:

```text
principal
→ direct group
→ nested group
→ role eligibility
→ platform mapping
→ permission
```

Riziká:

- stale membership;
- circular alebo veľmi hlboké nesting;
- propagation delay;
- cross-domain group mapping;
- duplicate direct aj inherited assignment;
- nejasný owner;
- session claim zachovávajúci starý graph.

Audit a access review musia vysvetliť exact path, nie iba výsledný názov role.

## 12. Separation of duties

### Static SoD

Principal nesmie mať konfliktujúce entitlements súčasne, napríklad create vendor a approve payment.

### Dynamic SoD

Principal môže byť eligible pre obe capabilities, ale nesmie ich použiť v rovnakej transaction/session. Vyžaduje workflow context a enforcement.

Mover a access-request proces má conflict check vykonať pred aktiváciou. Post-hoc report po incidentnej action nie je preventive SoD.

## 13. Kubernetes RBAC semantics

Kubernetes RBAC používa štyri hlavné objects:

- `Role` — namespaced rules;
- `ClusterRole` — cluster-scoped alebo reusable rules;
- `RoleBinding` — bind Role/ClusterRole v jednom namespace;
- `ClusterRoleBinding` — cluster-wide assignment.

Rule obsahuje API groups, resources/subresources, verbs, optional `resourceNames` a non-resource URLs.

Kubernetes RBAC permissions sú additive. Neexistuje štandardné explicit deny pravidlo, ktoré by odobralo allow z iného bindingu. Preto treba identifikovať všetky bindings a authorization modes.

Sensitive verbs a capabilities:

- `bind` — bind role bez vlastnenia všetkých jej permissions podľa pravidiel API;
- `escalate` — create/update role s permissions nad vlastný current access;
- `impersonate` — konať ako iný user/group/ServiceAccount;
- create/patch RBAC objects;
- create workloads, exec/attach a select ServiceAccounts;
- read Secrets;
- certificate-signing requests;
- node proxy a admission/webhook configuration.

Namespace nie je automaticky silná tenant boundary. Workload creation a Secret/ServiceAccount relationships môžu umožniť lateral alebo privilege escalation.

## 14. Cloud a application policy planes

Cloud effective access môže kombinovať:

- identity policy;
- resource policy;
- role trust policy;
- organization guardrail;
- permissions boundary;
- session policy;
- condition keys;
- explicit deny.

Application môže kombinovať federated identity, local role, tenant ownership, relationship graph a data-plane authorization.

Názvy `Owner`, `Administrator` alebo `Operator` majú význam iba v konkrétnom policy plane. Directory admin nie je automaticky cloud resource owner; cloud role nie je automaticky application data access.

## 15. Workload IAM

Workload identity record má obsahovať:

```text
stable workload identity
owner a service catalog entry
environment a deployment binding
credential/issuer/audience
permissions a resource scope
rotation/expiration
runtime generation
usage a audit
```

Service principal bez ownera, deployment bindingu a recent expected use je candidate na quarantine. Workload offboarding zahŕňa role, tokens, certificates, secrets, resource policies a downstream database accounts.

## 16. Policy as code a reconciliation

IAM/RBAC sources majú byť:

- version-controlled;
- reviewed ownerom a security policy;
- schema/lint validované;
- analyzované na wildcard a escalation paths;
- testované na representative principal–action–resource–context fixtures;
- canary-nuté;
- deploymentované controlled pipeline-om;
- runtime read-backnuté;
- drift a stale assignment monitorované.

Test matrix:

```text
required allow
forbidden action deny
cross-tenant deny
expired/JIT-inactive deny
mover/leaver deny
indirect escalation deny
break-glass allow + alert + expiry
```

Policy apply success nie je effective-access verdict. Potrebný je resource-side authorization test.

## 17. Authorization explainability

Pre každý sensitive allow alebo deny má byť možné zostaviť:

```text
principal a session
→ direct/nested groups
→ role eligibility a activation
→ policy/binding generations
→ resource/attribute context
→ combining semantics
→ PDP decision
→ PEP enforcement
→ operation result
```

Explainability je potrebná pre incident response, access review, SoD, support aj policy migration. „RBAC denied“ alebo „user is admin“ nie je dostatočný dôkaz.

## 18. Worked incident: add-only mover sync ponechal production access

### Desired organizational state

```text
identity 7421
old team: Payments Operations
new team: Finance Analytics
old production eligibility: remove
new analytics access: add
mover time: 08:00 UTC
```

### Effective graph po sync-e

```text
urn:atlas:human:7421
→ finance-emea
→ legacy-shared-operations
→ prod-payment-operators
→ Kubernetes group oidc:prod-payment-operators
→ ClusterRoleBinding payments-prod-operators
→ ClusterRole payments-prod-operator
→ create pods / patch config / scale deployments
```

Identity sync odstránil iba direct `payments-oncall` group a pridal `finance-emea`. Starý nested path cez `legacy-shared-operations` zostal. Session `SESSION-771` bola vydaná po mover evente s týmto stale claimom.

### Competing hypotheses

1. HR source neobsahoval mover zmenu;
2. entitlement catalog zámerne povoľoval Finance Analytics production access;
3. direct Kubernetes binding bol vytvorený ručne;
4. nested group path prežil add-only sync;
5. old session iba cache-ovala predchádzajúci správny access;
6. ClusterRoleBinding používala iný group string;
7. admission alebo resource policy mala action odmietnuť;
8. break-glass eligibility bola omylom active.

### Discriminating evidence

```text
HR generation 118: team = Finance Analytics
entitlement catalog: production operator not eligible
IAM-SYNC-306 operations: add finance-emea, remove payments-oncall
nested-group removal operations: none
direct Kubernetes user binding: none
IdP token issue time: 11:51 UTC, after mover
IdP claim: prod-payment-operators
ClusterRoleBinding subject: exact same group
Kubernetes SubjectAccessReview:
  create pods = yes
  patch deployments/scale = yes
  get secrets = yes
PAM activation/approval: none
```

Root cause je identity/entitlement reconciliation, ktorá nepočítala complete desired graph. Broad role a chýbajúci admission constraint sú amplifiers. Nie je to Kubernetes cache bug ani authentication failure.

### Evidence-preserving containment

- suspend principal a revoke-nuť sessions/tokens;
- odstrániť stale nested group edge a affected binding eligibility;
- freeze manual IAM/RBAC edits počas reconstruction;
- zachovať HR generation, sync operations, group graph, token claims, RBAC objects a audit events;
- vyhodnotiť ďalších principals používajúcich rovnaký nested path;
- neodstrániť celý group graph bez impact analýzy;
- nepoužiť `cluster-admin` ako troubleshooting workaround.

### Authoritative recovery

1. zmeniť sync z add-only delta modelu na complete desired-state reconciliation;
2. definovať ownera každého nested group edge-u;
3. pri mover udalosti vykonať remove/incompatibility phase pred novou privileged activation;
4. revoke-nuť privileged sessions po entitlement removal-e;
5. splitnúť `payments-prod-operator` na mediated JIT task capabilities;
6. odstrániť human Secret a arbitrary workload access;
7. pridať policy fixtures pre direct, nested, stale-session a workload-escalation paths;
8. spustiť second-sync a second-login canary.

### Acceptance verdict

Recovery je prijatá, keď:

- HR, entitlement engine, IdP groups a Kubernetes effective access sú zhodné;
- identity `7421` nemá direct, nested, inherited ani session-cached production path;
- required Finance Analytics access funguje;
- production Pod create, Secret read, config patch a scale sú denied;
- approved JIT Payments operator dostane iba intended capability;
- `kubectl auth can-i`/SubjectAccessReview positive a negative fixtures prejdú;
- second reconciliation neznovu-vytvorí stale edge;
- new session aj previously active session sú bez removed privilege;
- affected peer identities z `legacy-shared-operations` boli vyhodnotené;
- audit vysvetlí source → entitlement → session → binding → action chain.

## 19. Access request, approval a PAM

Access request má obsahovať:

- requester a beneficiary;
- exact entitlement/resource;
- business task a reason;
- environment/tenant;
- duration;
- resource owner/approver;
- SoD a escalation check;
- required authentication assurance;
- audit/correlation ID.

PAM/PIM môže poskytovať eligibility, JIT activation, approval, MFA, session duration, credential checkout, recording a access review. Nenahrádza však zlý role design ani stale source attributes.

## 20. Troubleshooting IAM/RBAC deny

```text
exact principal/session?
→ desired eligibility?
→ direct/group/nested assignment?
→ role/binding a scope?
→ action/resource/subresource?
→ trusted attributes?
→ session freshness?
→ boundary/guardrail/explicit deny?
→ target resource policy?
→ PEP decision?
```

Kubernetes helper:

```bash
kubectl auth can-i get pods \
  --as=system:serviceaccount:payments-prod:worker \
  -n payments-prod
```

Výsledok API authorization testu nepreukazuje admission, runtime, data-plane ani external-service authorization.

## 21. Troubleshooting excessive access

```text
direct assignment
→ group a nested graph
→ role hierarchy
→ resource policy
→ wildcard/conditions
→ session/PAM eligibility
→ impersonation/delegation
→ policy modification capability
→ workload escalation
→ stale local account/credential
```

Po source oprave over active sessions, cached tokens, workload credentials a second reconciliation.

## 22. Anti-patterny

### IAM = login page

Chýba provisioning, authorization, review, revocation a audit.

### Mover = add new role

Old access sa hromadí a vytvára privilege creep.

### Role podľa človeka

Nevzniká reusable task contract ani owner.

### Nested groups bez explainability

Effective access nemožno spoľahlivo reviewovať ani revoke-nuť.

### `cluster-admin` ako fix

Maskuje exact missing permission a vytvára nový incident path.

### ABAC s user-writable attributes

Principal si sám mení authorization vstup.

### Source policy update bez runtime testu

Binding, token alebo alternate policy plane zostáva effective.

## 23. Kontrolné otázky

1. Čo tvorí exact IAM/RBAC subject?
2. Prečo je IAM širšie než RBAC?
3. Ako sa určuje authoritative source per attribute?
4. Prečo mover potrebuje removal aj session revocation?
5. Čo musí obsahovať entitlement catalog entry?
6. Ako sa líši flat a hierarchical RBAC?
7. Ako role explosion súvisí s ABAC a resource-scoped assignmentom?
8. Prečo trusted attribute potrebuje controlled write path?
9. Ako Kubernetes Role, ClusterRole a bindings vytvárajú effective access?
10. Prečo je Kubernetes RBAC additive a čo z toho vyplýva?
11. Ako vysvetlíš nested-group access path?
12. Čo musí overiť second-sync a second-session acceptance test?

## Glossary impact

Relevantné pojmy: IAM subject, attribute-authority matrix, entitlement desired generation, identity reconciliation, joiner generation, mover reconciliation, leaver closure, entitlement catalog, role-contract generation, nested-group access path, trusted-attribute contract, effective-access graph, authorization explainability, IAM drift, second-sync test, workload IAM subject a IAM/RBAC acceptance verdict.

## Primárne zdroje

- [NIST Role-Based Access Control](https://csrc.nist.gov/projects/role-based-access-control)
- [NIST least privilege glossary](https://csrc.nist.gov/glossary/term/least_privilege)
- [Kubernetes RBAC authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Kubernetes RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
- [Kubernetes authorization overview](https://kubernetes.io/docs/reference/access-authn-authz/authorization/)
- [Microsoft Entra RBAC](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/)
- [Azure ABAC overview](https://learn.microsoft.com/en-us/azure/role-based-access-control/conditions-overview)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Least privilege](least-privilege.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: Active Directory →](active-directory.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
