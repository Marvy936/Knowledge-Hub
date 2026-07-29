# Least privilege

Least privilege znamená, že human alebo workload principal dostane iba capabilities potrebné na presne definovanú úlohu, nad najmenším potrebným resource/data scope-om, za požadovaných podmienok a iba na potrebný čas. Nie je to jednorazové zmenšenie role. Je to lifecycle od business tasku cez privilege activation a effective-state verification až po revocation, access review a incident recovery.

Najmenší počet permission statements nie je cieľ. Cieľom je najmenší preukázateľne funkčný a bezpečný capability envelope.

## 1. Dominantný lifecycle

```text
business task a expected outcome
→ exact principal a trust boundary
→ required action/resource/data inventory
→ environment, tenant, time, delegation a assurance constraints
→ minimal entitlement a maximum-permission envelope
→ approval a privilege activation
→ session/token a loaded effective access
→ positive, negative a escalation tests
→ operation audit a usage evidence
→ expiration, revocation alebo removal
→ second-session a alternate-path validation
→ role/task redesign
```

Tento lifecycle oddeľuje:

```text
permission bola odstránená zo source policy
≠ active session ju už nemá
≠ alternate group/resource/workload path neexistuje
≠ principal nedokáže získať equivalent authority nepriamo
```

## 2. Exact privilege subject

Pre connected incident používame:

```text
privilege subject: PRIV-PAY-47
security subject: SEC-PAY-47
human principal: urn:atlas:human:7421
business task: requeue one failed settlement after reconciliation
intended resource scope: payment_id PAY-884219
intended environment: production/eu-central-1
intended duration: 30 min
required assurance: fresh phishing-resistant authentication
actual role: payments-prod-operator
policy generation: RBAC-PAY-63
actual activation: standing group membership
actual session: SESSION-771
workload escalation target: settlement-debug ServiceAccount
```

Bez tasku, principalu, scope-u, duration a effective generation nemožno rozhodnúť, či privilege je minimálny.

## 3. Dimensions privilege-u

Privilege má viac nezávislých dimensions:

- **action scope** — čo možno vykonať;
- **resource scope** — nad ktorými objects;
- **data scope** — ktoré fields, records alebo secrets;
- **environment scope** — dev, test, production;
- **tenant/account/namespace scope**;
- **network a device context**;
- **time scope** — validity, activation a session lifetime;
- **delegation scope** — komu možno authority preniesť;
- **session assurance** — authentication method a freshness;
- **operation count alebo budget** — koľko actions možno vykonať.

`read` nad všetkými production secrets môže mať väčší blast radius než `admin` nad jedným isolated test objectom. Permission name bez dimensions nevyjadruje risk.

## 4. Need-to-know, need-to-do a capability design

- **Need-to-know** obmedzuje disclosure informácií.
- **Need-to-do** obmedzuje actions potrebné na business task.
- **Capability design** poskytuje presnú operáciu bez broad ambient authority.

Pre task „requeue one reconciled settlement“ je intended capability:

```text
input: payment_id PAY-884219
precondition: final state = failed/reconciled
allowed action: create one idempotent requeue command
forbidden:
  read provider private key
  patch route configuration
  create arbitrary Pod
  scale worker fleet
  requeue another tenant/payment
  disable audit
```

Mediated operation je bezpečnejšia než shell alebo broad Kubernetes API access, pretože backend môže validovať business state, idempotency a forbidden outcomes.

## 5. Standing, eligible, JIT a just-enough privilege

### Standing privilege

Permission je stále active. Exposure window sa rovná lifetime accountu, group membershipu alebo credentialu.

### Eligible privilege

Principal smie požiadať o activation, ale permission ešte nie je active.

### Just-in-time privilege

Privilege sa aktivuje na bounded čas po splnení podmienok:

- fresh MFA alebo phishing-resistant step-up;
- justification a ticket/incident ID;
- approval správneho ownera;
- duration;
- device/network posture;
- automatic expiration;
- post-use review.

### Just-enough administration

Principal dostane konkrétnu operation, nie full admin plane. Príklady:

- restart jednej service bez root shellu;
- requeue jedného workflowu;
- rotate jeden secret bez čítania ostatných;
- deploy one signed artifact do jedného environmentu;
- run approved diagnostic bez arbitrary Pod creation.

JIT znižuje exposure time. JEA znižuje capability scope. Potrebné sú obe osi.

## 6. Task decomposition

Least privilege sa nezačína existujúcou role. Začína execution pathom úlohy:

```text
business request
→ required observation
→ precondition validation
→ exact mutation
→ convergence/result read-back
→ audit a closure
```

Príklad settlement requeue:

| Fáza | Required capability | Nepotrebná authority |
|---|---|---|
| Observe | read one payment reconciliation state | list all Secrets |
| Validate | verify tenant, failure class a duplicate guard | patch ConfigMaps |
| Execute | invoke one idempotent requeue operation | create arbitrary Pods |
| Verify | read final settlement/queue state | scale Deployments |
| Close | append reason, actor a result | delete audit events |

## 7. Human identities

Privileged human model má typicky používať:

- oddelený bežný a privileged context;
- phishing-resistant authentication;
- eligible/JIT access;
- minimal resource scope;
- managed endpoint alebo controlled admin environment podľa risku;
- no shared accounts;
- session timeout a revocation;
- activity audit;
- access reviews a mover/leaver removal.

Privileged identity sa nemá používať na email, browsing alebo bežnú engineering prácu. To zväčšuje attack surface sessionu s vysokou authority.

## 8. Workload identities

Workload identity potrebuje:

- platform-native, short-lived credential;
- stable workload ownera a purpose;
- explicitný audience a environment binding;
- samostatnú identity pre každý trust boundary;
- minimal action/resource scope;
- automatic rotation;
- no human credential reuse;
- complete issuance a usage audit.

Anti-patterny:

- jedna ServiceAccount pre celý namespace alebo cluster;
- static cloud key v image;
- database superuser pre application;
- CI identity s organization admin;
- shared debug identity s production Secret read.

## 9. Maximum-permission envelope

Guardrail, permissions boundary, organization policy alebo session restriction definuje maximum, ktoré principal môže získať.

Konceptuálne:

```text
effective allow
= granted identity/resource capabilities
∩ maximum boundary
∩ organization/environment guardrails
∩ session restrictions
− explicit denies podľa platformy
```

Boundary sama permission neudeľuje. Chráni pred tým, aby delegated administrator alebo compromised automation vytvorili role nad schválený envelope.

V Kubernetes štandardný RBAC explicit deny nemá. Maximum sa preto vytvára kombináciou:

- neudelenia broad RBAC permissions;
- obmedzenia, kto smie `bind`, `escalate` a `impersonate`;
- admission/policy controls nad workload spec-om;
- namespace/tenant architecture;
- oddelených ServiceAccounts a Secrets;
- node a runtime security boundaries.

## 10. Separation of duties

Citlivý workflow oddeľuje:

```text
requester
→ approver/resource owner
→ privilege activation system
→ bounded executor
→ independent audit/reviewer
```

Jedna identity nemá bez compensating controls zároveň:

- vytvoriť entitlement;
- schváliť vlastnú activation;
- vykonať high-impact action;
- zmeniť alebo odstrániť audit;
- potvrdiť vlastnú recovery.

Static SoD zakazuje conflictujúce assignments. Dynamic SoD zakazuje ich použitie v rovnakom workflowe alebo session.

## 11. Indirect privilege escalation

Effective privilege zahŕňa actions, ktoré umožnia získať inú authority.

Kubernetes príklady:

- create Pod s výberom privileged ServiceAccountu;
- mount Secret alebo hostPath cez workload;
- `exec` do Podu s vyššou identity;
- create/patch RoleBinding;
- `bind`, `escalate` alebo `impersonate`;
- create CSR a získať certificate;
- modify admission/webhook configuration;
- access node proxy alebo privileged runtime.

Permission `create pods` preto nie je automaticky low risk. Musí sa analyzovať spolu s povolenými ServiceAccounts, volumes, security contextom, host accessom a admission policy.

Cloud a CI/CD príklady:

- `iam:PassRole` alebo equivalent delegation;
- update function/task role;
- modify pipeline, ktorý má production credential;
- write artifact pod trusted name/tag;
- edit policy alebo approver group;
- read secret použiteľný na silnejšiu identity.

## 12. Configured, activated a effective privilege

```text
entitlement source
→ assignment eligibility
→ activation approval
→ session/token claims
→ platform mapping
→ loaded policy/binding
→ effective access graph
→ actual enforcement
```

Pri review alebo incident response zaznamenaj:

- source generation;
- direct, group, nested a inherited paths;
- role/binding revision;
- session issue/expiration/revocation;
- resource policy a alternate identity;
- workload delegation;
- cache a propagation state.

Role name nie je effective-access dôkaz.

## 13. Access review a removal

Review musí odpovedať:

- Ktorý principal má akú effective capability?
- Cez ktorú direct, group, nested, delegated alebo resource path?
- Aký task ju odôvodňuje?
- Kto je owner entitlementu a resource-u?
- Kedy bola naposledy aktivovaná a použitá?
- Je duration a scope primeraný?
- Existuje conflicting duty alebo indirect escalation?
- Čo sa stane po removal-e s active sessions a derived credentials?

Review bez deterministic removal a revocation workflowu je iba report.

Usage data pomáha, ale nie je automatická autorita. Rare disaster-recovery capability môže byť legitímne nepoužitá. Musí mať periodic rehearsal a expiry/reapproval, nie slepé permanentné ponechanie ani automatic deletion bez recovery analysis.

## 14. Worked incident: task potreboval jedno requeue, role umožnila control-plane takeover

### Intended task

Operator mal po provider reconciliation vykonať:

```text
POST /operations/settlements/PAY-884219/requeue
reason = provider-timeout-reconciled
idempotency key = IR-884219-2
```

### Actual standing role

```yaml
role: payments-prod-operator
scope: payments-prod namespace
rules:
  - resources: [pods]
    verbs: [create, get, list, delete]
  - resources: [secrets]
    verbs: [get, list]
  - resources: [configmaps]
    verbs: [get, patch, update]
  - resources: [deployments, deployments/scale]
    verbs: [get, patch, update]
  - resources: [pods/exec]
    verbs: [create]
```

Pod admission navyše dovolil zvoliť `serviceAccountName: settlement-debug`, ktorá mala provider Secret read.

### Competing hypotheses

1. incident vyžadoval broad role pre legitimate diagnostics;
2. Secret read bolo potrebné pre requeue;
3. create Pod bolo neškodné, lebo role nemala direct `get secrets`;
4. ServiceAccount nemala vyššie permissions;
5. stale group bola jediný problém a role scope bol primeraný;
6. admission zabránila privileged workloadu;
7. broad role bola temporary a automaticky expirovala;
8. alternate mediated API neexistovalo.

### Discriminating evidence

```text
actual business task calls: one requeue endpoint
required Kubernetes actions: none
role standing duration: 214 days
last access review: role name only, no effective graph
create Pod permission: active
select settlement-debug ServiceAccount: allowed
Pod Secret mount/read: allowed
patch ConfigMap: allowed
patch deployments/scale: allowed
admission rule restricting ServiceAccount selection: absent
JIT activation/expiry: absent
```

Root cause least-privilege failureu je task-to-capability mismatch. Stale membership sprístupnila role nesprávnemu principalu; broad role zmenila identity defect na confidentiality, integrity a availability incident.

### Evidence-preserving containment

- disable standing role assignment a nové activations;
- revoke active sessions/tokens, nie iba upraviť source group;
- preserve exact role, bindings, admission generation a SubjectAccessReview results;
- block arbitrary Pod creation/ServiceAccount selection pre support path;
- zachovať legitimate settlement recovery cez controlled break-glass alebo mediated API;
- neudeliť `cluster-admin` incident responderom ako náhradu.

### Authoritative recovery

1. vytvoriť capability `settlement.requeue.one` v operations API;
2. viazať ju na payment ID, tenant, reconciled state a idempotency key;
3. sprístupniť ju iba ako eligible JIT privilege na 30 minút;
4. vyžadovať fresh phishing-resistant step-up a reason;
5. oddeliť read-only diagnostics od mutation capability;
6. odstrániť human `Secret` read, arbitrary Pod create, config patch a scale permissions;
7. obmedziť debug ServiceAccount a admission rules;
8. pridať negative escalation tests a second-session revocation test.

### Acceptance verdict

Recovery je prijatá, keď:

- approved operator requeue-ne iba `PAY-884219` po splnení preconditions;
- druhý payment a iný tenant sú odmietnuté;
- action po 30 minútach alebo bez step-up-e zlyhá;
- operator nevie create Pod, vybrať `settlement-debug`, exec, read Secret, patch route ani scale workers;
- denied attempts aj approved requeue sú auditované;
- removed entitlement nefunguje v existing ani new session;
- break-glass cesta funguje nezávisle, je bounded a alertovaná;
- second identity sync, rollout a policy reconciliation neobnovia broad privilege.

## 15. Platformové aplikácie

### Linux

- per-command `sudo` alebo mediated system action;
- capabilities namiesto root;
- file ACLs;
- systemd sandboxing;
- SELinux/AppArmor;
- read-only filesystems a namespace boundaries.

### Kubernetes

- namespace-scoped Role, kde to task umožňuje;
- dedicated ServiceAccount per workload;
- minimal Secret access;
- projected short-lived tokens;
- restricted workload/admission policy;
- kontrola `bind`, `escalate`, `impersonate`, workload create a exec paths.

### Cloud

- roles a federation namiesto static keys;
- resource a condition scope;
- account/environment separation;
- permissions boundaries a organization guardrails;
- short sessions a JIT activation;
- explicit delegated-role controls.

### CI/CD

- oddelené build a deploy identities;
- OIDC/short-lived credentials;
- repository, ref, workflow a environment binding;
- no production credentials pre untrusted pull requests;
- signed artifact a protected deployment gate.

### AI agents

- tool allowlist;
- read-only default;
- parameter/resource constraints;
- approval pre mutating/high-impact action;
- action/time/cost budget;
- sandbox a kill switch;
- backend-enforced authorization.

Prompt instruction nie je security boundary.

## 16. Validation a troubleshooting

### Positive validation

Required task funguje na intended resource-e a outcome sa overí na business boundary.

### Negative validation

Forbidden action, resource, tenant, environment, expired session a alternate path zlyhajú.

### Escalation validation

Testuj, či povolená action umožní:

- zmeniť policy;
- vybrať silnejšiu workload identity;
- prečítať credential;
- impersonovať principal;
- spustiť arbitrary code pri trusted boundary;
- obísť PEP.

### Denied-access troubleshooting

```text
exact task a required tuple
→ principal/session?
→ direct/group/role assignment?
→ resource scope a conditions?
→ boundary/guardrail/session restriction?
→ policy propagation?
→ target resource policy?
→ PEP decision log?
```

Neopravuj deny pridaním admin role bez identifikácie exact missing capability.

### Excessive-access troubleshooting

```text
direct grant
→ nested/inherited group
→ role hierarchy
→ resource policy
→ wildcard/condition bypass
→ workload/delegation path
→ policy-modification capability
→ stale session/token
→ alternate endpoint
```

## 17. Anti-patterny

### Admin pre rýchlosť

Temporary broad role sa stane permanentným interface-om.

### Read-only = low risk

Secrets, PII, configs a audit evidence môžu mať kritický read impact.

### Role review podľa názvu

Ignoruje rules, nested paths, delegation a indirect escalation.

### JIT broad admin

Time scope sa zmenšil, action/resource blast radius zostal neprimeraný.

### Least privilege bez availability modelu

Identity-plane outage zablokuje incident response, pretože break-glass nebol testovaný.

### Odstránenie source assignmentu bez session revocation

Active token pokračuje do expirácie.

## 18. Kontrolné otázky

1. Čo tvorí exact privilege subject?
2. Aké dimensions má privilege?
3. Ako sa líši need-to-know, need-to-do a capability model?
4. Prečo JIT a just-enough riešia odlišné osi?
5. Ako sa task rozloží na required capabilities?
6. Prečo `create pods` môže byť privilege-escalation permission?
7. Čo je maximum-permission envelope?
8. Ako sa líši configured, activated a effective privilege?
9. Prečo usage data nie je automatická removal autorita?
10. Ako validovať positive, negative a escalation outcomes?
11. Prečo source removal nestačí bez session revocation?
12. Aký task-to-capability redesign uzavrel `PRIV-PAY-47`?

## Glossary impact

Relevantné pojmy: privilege subject, task-capability contract, privilege-dimension inventory, eligible privilege, activation generation, just-in-time privilege, just-enough capability, maximum-permission envelope, indirect privilege path, effective-privilege graph, privilege-removal closure, second-session revocation test, escalation acceptance test a least-privilege acceptance verdict.

## Primárne zdroje

- [NIST least privilege glossary](https://csrc.nist.gov/glossary/term/least_privilege)
- [NIST SP 800-53 Rev. 5 — Access Control](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)
- [Kubernetes RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)
- [Kubernetes RBAC authorization](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Microsoft Entra role best practices](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/best-practices)

<!-- KNOWLEDGE-NAVIGATION:START -->
---

**Navigácia**

[← Predchádzajúca: Authentication, authorization a auditing](authentication-authorization-auditing.md) · [↑ Obsah sekcie](README.md) · [Nasledujúca: IAM a RBAC →](iam-rbac.md)
<!-- KNOWLEDGE-NAVIGATION:END -->
